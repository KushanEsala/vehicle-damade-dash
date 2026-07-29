from __future__ import annotations

import base64
import json
from dataclasses import dataclass, replace
from io import BytesIO
from typing import Callable, Iterable, Literal

import httpx
import numpy as np
from PIL import Image

from core.logging_config import logger
from core.secret_store import get_vision_api_key
from ml.types import DamageDetection, VehicleDetection


DecisionName = Literal["accept", "correct", "reject"]
VehicleContext = Literal["full_vehicle", "vehicle_part_closeup", "not_vehicle", "uncertain"]
EvidenceStrength = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class VisionDecision:
    candidate_id: str
    decision: DecisionName
    corrected_damage: str | None
    vehicle_part: str | None
    severity: str | None
    certainty: float
    refined_polygon: np.ndarray | None
    mask_certainty: float
    description: str | None
    reason: str | None


@dataclass(frozen=True)
class VisionReview:
    vehicle_context: VehicleContext
    vehicle_certainty: float
    decisions: tuple[VisionDecision, ...]


@dataclass(frozen=True)
class DirectVisionFinding:
    damage_class: str
    vehicle_part: str
    severity: str
    evidence_strength: EvidenceStrength
    description: str
    box: np.ndarray
    polygon: np.ndarray


@dataclass(frozen=True)
class DirectVisionReview:
    vehicle_confirmed: bool
    vehicle_type: str | None
    findings: tuple[DirectVisionFinding, ...]
    review_required: bool
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    detection: DamageDetection
    initially_accepted: bool


def _clamp(value: object, low: float = 0.0, high: float = 1.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return low
    return min(max(number, low), high)


def _clean_text(value: object, maximum: int) -> str | None:
    if not isinstance(value, str):
        return None
    text = " ".join(value.strip().split())
    return text[:maximum] or None


def build_candidates(
    accepted: Iterable[DamageDetection],
    rejected: Iterable[DamageDetection],
) -> list[Candidate]:
    rows = [
        Candidate(f"accepted-{index}", detection, True)
        for index, detection in enumerate(accepted)
    ]
    rows.extend(
        Candidate(f"rejected-{index}", detection, False)
        for index, detection in enumerate(rejected)
    )
    return rows


def _polygon_area(polygon: np.ndarray) -> float:
    points = np.asarray(polygon, dtype=float)
    if points.ndim != 2 or points.shape[0] < 3 or points.shape[1] != 2:
        return 0.0
    x = points[:, 0]
    y = points[:, 1]
    return float(abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))) * 0.5)


def _usable_refined_polygon(
    polygon: np.ndarray | None,
    candidate_box: np.ndarray,
) -> bool:
    """Reject malformed or implausible second-stage masks."""
    if polygon is None:
        return False
    points = np.asarray(polygon, dtype=float)
    if (
        points.ndim != 2
        or points.shape[0] < 3
        or points.shape[0] > 160
        or points.shape[1] != 2
        or not np.isfinite(points).all()
    ):
        return False

    x1, y1, x2, y2 = [float(value) for value in candidate_box]
    box_width = max(x2 - x1, 1.0)
    box_height = max(y2 - y1, 1.0)
    box_area = box_width * box_height
    margin_x = max(6.0, box_width * 0.08)
    margin_y = max(6.0, box_height * 0.08)
    if (
        np.any(points[:, 0] < x1 - margin_x)
        or np.any(points[:, 0] > x2 + margin_x)
        or np.any(points[:, 1] < y1 - margin_y)
        or np.any(points[:, 1] > y2 + margin_y)
    ):
        return False

    area = _polygon_area(points)
    if area < max(9.0, box_area * 0.0005):
        return False
    # A tight polygon can nearly fill a detector box, but allowing it to be
    # larger would reintroduce whole-panel masks and background spill.
    if area > box_area * 1.02:
        return False

    centroid = points.mean(axis=0)
    return bool(x1 <= centroid[0] <= x2 and y1 <= centroid[1] <= y2)


def _box_overlap_over_smaller(first: np.ndarray, second: np.ndarray) -> float:
    ax1, ay1, ax2, ay2 = [float(value) for value in first]
    bx1, by1, bx2, by2 = [float(value) for value in second]
    intersection = max(0.0, min(ax2, bx2) - max(ax1, bx1)) * max(
        0.0,
        min(ay2, by2) - max(ay1, by1),
    )
    first_area = max((ax2 - ax1) * (ay2 - ay1), 1.0)
    second_area = max((bx2 - bx1) * (by2 - by1), 1.0)
    return float(intersection / min(first_area, second_area))


def _polygon_box_fit_score(polygon: np.ndarray, box: np.ndarray) -> float:
    x1, y1, x2, y2 = [float(value) for value in box]
    points = np.asarray(polygon, dtype=float)
    inside = (
        (points[:, 0] >= x1)
        & (points[:, 0] <= x2)
        & (points[:, 1] >= y1)
        & (points[:, 1] <= y2)
    )
    return float(np.mean(inside))


def apply_direct_vision_review(
    candidates: list[Candidate],
    review: DirectVisionReview,
    *,
    allowed_damage_classes: set[str],
    initially_vehicle_confirmed: bool,
) -> tuple[list[DamageDetection], list[DamageDetection], bool]:
    """Fuse full-image Gemini masks with YOLO candidates and preserve both sources."""
    supplemental_vehicle = review.vehicle_confirmed and not initially_vehicle_confirmed
    if not review.vehicle_confirmed:
        rejected = [
            replace(
                candidate.detection,
                passed_vehicle_gate=False,
                validation_note="The full-image review did not confirm a vehicle or vehicle part.",
            )
            for candidate in candidates
        ]
        return [], rejected, False

    accepted: list[DamageDetection] = []
    used_candidate_ids: set[str] = set()
    supported_findings = [
        finding
        for finding in review.findings
        if finding.damage_class in allowed_damage_classes
        and finding.evidence_strength in {"medium", "high"}
        and _usable_refined_polygon(finding.polygon, finding.box)
    ]

    for finding in supported_findings:
        ranked_matches = sorted(
            (
                (_box_overlap_over_smaller(finding.box, candidate.detection.box), candidate)
                for candidate in candidates
                if candidate.candidate_id not in used_candidate_ids
            ),
            key=lambda row: row[0],
            reverse=True,
        )
        score, matched = ranked_matches[0] if ranked_matches else (0.0, None)
        if matched is not None and score < 0.15:
            matched = None

        # A medium-evidence Gemini-only region is not enough to create a new
        # insurance finding. High evidence can recover a region YOLO missed.
        if matched is None and finding.evidence_strength != "high":
            continue

        if matched is not None:
            used_candidate_ids.add(matched.candidate_id)
            original = matched.detection
            confidence = original.confidence
            original_class = original.original_damage_class or original.damage_class
            original_polygon = (
                original.model_polygon
                if original.model_polygon is not None
                else original.polygon
            )
            overlap_ratio = max(original.overlap_ratio, score)
            source = "hybrid"
        else:
            confidence = 0.90
            original_class = finding.damage_class
            original_polygon = None
            overlap_ratio = 0.0
            source = "vision"

        accepted.append(DamageDetection(
            damage_class=finding.damage_class,
            confidence=confidence,
            box=np.asarray(finding.box, dtype=float),
            source=source,
            original_damage_class=original_class,
            polygon=np.asarray(finding.polygon, dtype=float),
            model_polygon=(
                np.asarray(original_polygon, dtype=float)
                if original_polygon is not None
                else None
            ),
            mask_refined=True,
            passed_vehicle_gate=True,
            overlap_ratio=overlap_ratio,
            vehicle_part=finding.vehicle_part,
            severity=finding.severity,
            description=finding.description,
            validation_note=(
                f"Full-image visual review: {finding.evidence_strength} evidence."
            ),
        ))

    rejected = [
        replace(
            candidate.detection,
            passed_vehicle_gate=False,
            validation_note="The local finding was not supported by the full-image visual review.",
        )
        for candidate in candidates
        if candidate.candidate_id not in used_candidate_ids
    ]
    return accepted, rejected, supplemental_vehicle


def apply_vision_review(
    candidates: list[Candidate],
    review: VisionReview,
    *,
    allowed_damage_classes: set[str],
    initially_vehicle_confirmed: bool,
    require_vehicle: bool,
) -> tuple[list[DamageDetection], list[DamageDetection], bool]:
    """Conservatively merge a visual second opinion with detector output."""
    decisions = {item.candidate_id: item for item in review.decisions}
    supplemental_vehicle = (
        not initially_vehicle_confirmed
        and review.vehicle_context in {"full_vehicle", "vehicle_part_closeup"}
        and review.vehicle_certainty >= 0.80
    )
    confirmed_not_vehicle = (
        review.vehicle_context == "not_vehicle"
        and review.vehicle_certainty >= 0.80
    )
    accepted: list[DamageDetection] = []
    rejected: list[DamageDetection] = []

    for candidate in candidates:
        detection = candidate.detection
        decision = decisions.get(candidate.candidate_id)
        final_accept = candidate.initially_accepted

        if decision and decision.certainty >= 0.72:
            if decision.decision == "reject":
                final_accept = False
            elif candidate.initially_accepted:
                final_accept = True
            elif (
                not initially_vehicle_confirmed
                and supplemental_vehicle
                and decision.decision in {"accept", "correct"}
            ):
                # Only recover detections that were withheld because a tightly
                # cropped vehicle part could not pass the general vehicle model.
                final_accept = True

        # Disabling the general vehicle-overlap gate supports tightly cropped
        # vehicle parts; it must never turn off explicit negative-image safety.
        if confirmed_not_vehicle:
            final_accept = False
        elif require_vehicle and not (initially_vehicle_confirmed or supplemental_vehicle):
            final_accept = False

        corrected_class = None
        if decision and decision.decision == "correct":
            proposed = (decision.corrected_damage or "").lower().strip()
            if proposed in allowed_damage_classes:
                corrected_class = proposed

        if decision and decision.certainty >= 0.60:
            detection = replace(
                detection,
                original_damage_class=detection.original_damage_class or detection.damage_class,
                damage_class=corrected_class or detection.damage_class,
                passed_vehicle_gate=final_accept,
                vehicle_part=decision.vehicle_part,
                severity=decision.severity,
                description=decision.description,
                validation_note=decision.reason,
            )
        else:
            detection = replace(detection, passed_vehicle_gate=final_accept)

        if (
            final_accept
            and decision
            and decision.decision in {"accept", "correct"}
            and decision.certainty >= 0.72
            and decision.mask_certainty >= 0.72
            and _usable_refined_polygon(decision.refined_polygon, detection.box)
        ):
            detection = replace(
                detection,
                model_polygon=(
                    detection.model_polygon
                    if detection.model_polygon is not None
                    else detection.polygon
                ),
                polygon=np.asarray(decision.refined_polygon, dtype=float),
                mask_refined=True,
            )

        (accepted if final_accept else rejected).append(detection)

    return accepted, rejected, supplemental_vehicle


class GeminiVisionValidator:
    """Server-only visual validation. No credential or provider call reaches the browser."""

    MODEL = "gemini-3.6-flash"
    ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"

    def __init__(
        self,
        secret_reader: Callable[[], str | None] = get_vision_api_key,
        timeout_seconds: float = 35.0,
    ) -> None:
        self._secret_reader = secret_reader
        self._timeout = timeout_seconds

    def inspect(
        self,
        image_rgb: np.ndarray,
        allowed_damage_classes: set[str],
    ) -> DirectVisionReview | None:
        """Discover and segment all supported damage regions in one image."""
        key = self._secret_reader()
        if not key or not allowed_damage_classes:
            return None

        allowed = sorted(allowed_damage_classes)
        payload = self._build_interaction_payload(
            self._build_direct_prompt(allowed),
            self._prepare_image(image_rgb),
            self._direct_response_schema(allowed),
        )
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(
                    self.ENDPOINT,
                    headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
                raw = self._extract_output_text(response.json())
            return self._parse_direct_review(
                raw,
                allowed_damage_classes,
                width=image_rgb.shape[1],
                height=image_rgb.shape[0],
            )
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Full-image visual inspection failed with HTTP %s; using local findings.",
                exc.response.status_code,
            )
            return None
        except Exception as exc:
            logger.warning(
                "Full-image visual inspection was unavailable (%s); using local findings.",
                type(exc).__name__,
            )
            return None

    def review(
        self,
        image_rgb: np.ndarray,
        vehicles: list[VehicleDetection],
        candidates: list[Candidate],
        allowed_damage_classes: set[str],
    ) -> VisionReview | None:
        key = self._secret_reader()
        if not key or not candidates:
            return None

        image_data = self._prepare_image(image_rgb)
        prompt = self._build_prompt(image_rgb.shape, vehicles, candidates, allowed_damage_classes)
        payload = self._build_payload(
            prompt,
            image_data,
            sorted(allowed_damage_classes),
        )

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(
                    self.ENDPOINT,
                    headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
                body = response.json()
            raw = self._extract_output_text(body)
            return self._parse_review(
                raw,
                {item.candidate_id for item in candidates},
                allowed_damage_classes,
                width=image_rgb.shape[1],
                height=image_rgb.shape[0],
            )
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Optional visual refinement request failed with HTTP %s; using the local model mask.",
                exc.response.status_code,
            )
            return None
        except Exception as exc:
            # The primary detector remains usable when the optional second
            # opinion is unavailable, rate-limited, or malformed.
            logger.warning(
                "Optional visual refinement was unavailable (%s); using the local model mask.",
                type(exc).__name__,
            )
            return None

    def _build_payload(
        self,
        prompt: str,
        image_data: str,
        allowed_damage_classes: list[str],
    ) -> dict:
        # The source upload may use a .jpg filename, but _prepare_image always
        # re-encodes its pixels as JPEG. The API MIME name is image/jpeg;
        # image/jpg is not a valid media type.
        return self._build_interaction_payload(
            prompt,
            image_data,
            self._response_schema(allowed_damage_classes),
        )

    def _build_interaction_payload(
        self,
        prompt: str,
        image_data: str,
        response_schema: dict,
    ) -> dict:
        return {
            "model": self.MODEL,
            "input": [
                {"type": "text", "text": prompt},
                {
                    "type": "image",
                    "mime_type": "image/jpeg",
                    "data": image_data,
                },
            ],
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": response_schema,
            },
            "generation_config": {"thinking_level": "minimal"},
        }

    @staticmethod
    def _extract_output_text(body: object) -> str:
        if not isinstance(body, dict) or body.get("status") != "completed":
            raise ValueError("Visual refinement interaction did not complete.")
        for step in reversed(body.get("steps", [])):
            if not isinstance(step, dict) or step.get("type") != "model_output":
                continue
            for content in step.get("content", []):
                if isinstance(content, dict) and content.get("type") == "text":
                    text = content.get("text")
                    if isinstance(text, str) and text.strip():
                        return text
        raise ValueError("Visual refinement response did not contain text output.")

    @staticmethod
    def _prepare_image(image_rgb: np.ndarray) -> str:
        image = Image.fromarray(image_rgb.astype(np.uint8), mode="RGB")
        image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        output = BytesIO()
        image.save(output, format="JPEG", quality=88, optimize=True)
        return base64.b64encode(output.getvalue()).decode("ascii")

    @staticmethod
    def _normalized_box(box: np.ndarray, width: int, height: int) -> list[int]:
        x1, y1, x2, y2 = [float(value) for value in box]
        return [
            round(max(0, min(1000, y1 / max(height, 1) * 1000))),
            round(max(0, min(1000, x1 / max(width, 1) * 1000))),
            round(max(0, min(1000, y2 / max(height, 1) * 1000))),
            round(max(0, min(1000, x2 / max(width, 1) * 1000))),
        ]

    @staticmethod
    def _normalized_polygon(
        polygon: np.ndarray | None,
        width: int,
        height: int,
        maximum_points: int = 32,
    ) -> list[list[int]]:
        if polygon is None:
            return []
        points = np.asarray(polygon, dtype=float)
        if points.ndim != 2 or points.shape[0] < 3 or points.shape[1] != 2:
            return []
        if points.shape[0] > maximum_points:
            indexes = np.linspace(0, points.shape[0] - 1, maximum_points, dtype=int)
            points = points[indexes]
        return [
            [
                round(max(0, min(1000, x / max(width, 1) * 1000))),
                round(max(0, min(1000, y / max(height, 1) * 1000))),
            ]
            for x, y in points
        ]

    def _build_prompt(
        self,
        image_shape: tuple[int, ...],
        vehicles: list[VehicleDetection],
        candidates: list[Candidate],
        allowed_damage_classes: set[str],
    ) -> str:
        height, width = image_shape[:2]
        candidate_rows = [{
            "candidate_id": item.candidate_id,
            "detector_class": item.detection.damage_class,
            "detector_confidence": round(item.detection.confidence, 4),
            "box_2d": self._normalized_box(item.detection.box, width, height),
            "detector_mask_outline_xy": self._normalized_polygon(
                item.detection.polygon,
                width,
                height,
            ),
        } for item in candidates]
        vehicle_rows = [{
            "class": item.vehicle_class,
            "confidence": round(item.confidence, 4),
            "box_2d": self._normalized_box(item.box, width, height),
        } for item in vehicles]
        return (
            "Act as a conservative vehicle-damage visual reviewer. Inspect the actual image and "
            "review only the supplied candidate regions. Coordinates use [ymin,xmin,ymax,xmax] "
            "on a 0-1000 scale. Determine whether the image contains a full vehicle, a close-up "
            "of a vehicle part, something that is not a vehicle, or is uncertain. For every "
            "candidate return exactly one decision. Reject reflections, shadows, dirt, normal "
            "panel seams, intact parts, people, background objects and uncertain marks. A "
            "puncture is valid only when the region contains a tyre/wheel. Never call bumper, "
            "grille, lamp or body-panel damage a puncture. Correct a class only to one of the "
            f"allowed classes: {sorted(allowed_damage_classes)}. Use severity minor, moderate, "
            "or severe. Use a short factual description without repair prices or insurance "
            "decisions. For every accepted or corrected candidate, return refined_polygon_xy "
            "as an ordered polygon of [x,y] points on a 0-1000 scale relative to the FULL "
            "IMAGE. Trace only the pixels that visibly belong to the actual damage. Do not "
            "copy the detector outline when it includes intact material. Never mask a whole "
            "door, bumper, bonnet, windscreen, lamp, tyre, wheel, glass pane, or body panel "
            "unless the visible damage genuinely occupies that whole part. For scratches, "
            "tears and glass cracks, follow the narrow damaged path closely. For dents, trace "
            "only the visibly deformed surface. For a broken or missing part, trace the broken "
            "or missing area, not the intact surrounding part. Keep the polygon inside the "
            "candidate box. Use at least 3 points and at most 80 points. For reject decisions, "
            "return an empty polygon and mask_certainty 0. mask_certainty must describe how "
            "certain you are that the polygon itself is spatially accurate, independently "
            "from the damage classification certainty. Do not infer customer identity, "
            "registration, policy or cost. For any optional text field that does not apply, "
            "return an empty string. "
            f"General vehicle detections: {json.dumps(vehicle_rows, separators=(',', ':'))}. "
            f"Damage candidates: {json.dumps(candidate_rows, separators=(',', ':'))}."
        )

    @staticmethod
    def _build_direct_prompt(allowed_damage_classes: list[str]) -> str:
        return (
            "Inspect this image for externally visible motor-vehicle damage. This is "
            "decision support and not a final insurance decision. Confirm a vehicle when "
            "either a full vehicle or a clearly recognizable vehicle body part is visible. "
            "Only report damage that is visibly supported and can be localized. The only "
            f"allowed damage types are: {allowed_damage_classes}. Never invent, rename, or "
            "return a damage type outside this list. Do not return background as a finding. "
            "A puncture is valid only when a tyre is visible and the damage lies on that "
            "tyre; never label a bumper, grille, lamp, or body panel as puncture. A broken "
            "lamp requires visible damage to a lamp lens or housing. broken_glass requires "
            "visible cracked, shattered, or missing vehicle glass. missing_part requires a "
            "clearly absent vehicle component. Avoid duplicate findings for the same "
            "physical region. Return bounding boxes as [ymin,xmin,ymax,xmax] normalized "
            "from 0 to 1000. Return each polygon mask as [x,y] points normalized from 0 to "
            "1000 relative to the full image. Trace the visible damaged region tightly. "
            "Do not mask an entire vehicle, hood, bumper, door, panel, lamp, tyre, or glass "
            "surface when only a smaller area is damaged. Use an empty findings array when "
            "no supported vehicle damage is visible. Set vehicle_confirmed false for "
            "diagrams, model graphs, buildings, people, furniture, and other non-vehicle "
            "images."
        )

    @staticmethod
    def _direct_response_schema(allowed_damage_classes: list[str]) -> dict:
        return {
            "type": "object",
            "properties": {
                "vehicle_confirmed": {"type": "boolean"},
                "vehicle_type": {"type": "string"},
                "findings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "damage_type": {
                                "type": "string",
                                "enum": allowed_damage_classes,
                            },
                            "vehicle_part": {"type": "string"},
                            "severity": {
                                "type": "string",
                                "enum": ["minor", "moderate", "severe"],
                            },
                            "evidence_strength": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                            },
                            "description": {"type": "string"},
                            "box_2d": {
                                "type": "array",
                                "items": {"type": "integer"},
                            },
                            "mask": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                },
                            },
                        },
                        "required": [
                            "damage_type",
                            "vehicle_part",
                            "severity",
                            "evidence_strength",
                            "description",
                            "box_2d",
                            "mask",
                        ],
                    },
                },
                "review_required": {"type": "boolean"},
                "warnings": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": [
                "vehicle_confirmed",
                "vehicle_type",
                "findings",
                "review_required",
                "warnings",
            ],
        }

    @staticmethod
    def _response_schema(allowed_damage_classes: list[str]) -> dict:
        return {
            "type": "object",
            "properties": {
                "vehicle_context": {
                    "type": "string",
                    "enum": ["full_vehicle", "vehicle_part_closeup", "not_vehicle", "uncertain"],
                },
                "vehicle_certainty": {"type": "number", "minimum": 0, "maximum": 1},
                "decisions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "candidate_id": {"type": "string"},
                            "decision": {
                                "type": "string",
                                "enum": ["accept", "correct", "reject"],
                            },
                            "corrected_damage": {
                                "type": "string",
                                "enum": [*allowed_damage_classes, ""],
                            },
                            "vehicle_part": {"type": "string"},
                            "severity": {
                                "type": "string",
                                "enum": ["minor", "moderate", "severe", ""],
                            },
                            "certainty": {"type": "number", "minimum": 0, "maximum": 1},
                            "refined_polygon_xy": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 1000,
                                    },
                                },
                            },
                            "mask_certainty": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "description": {"type": "string"},
                            "reason": {"type": "string"},
                        },
                        "required": [
                            "candidate_id",
                            "decision",
                            "corrected_damage",
                            "vehicle_part",
                            "severity",
                            "certainty",
                            "refined_polygon_xy",
                            "mask_certainty",
                            "description",
                            "reason",
                        ],
                    },
                },
            },
            "required": ["vehicle_context", "vehicle_certainty", "decisions"],
        }

    @staticmethod
    def _parse_review(
        raw: str,
        candidate_ids: set[str],
        allowed_damage_classes: set[str],
        *,
        width: int,
        height: int,
    ) -> VisionReview:
        text = raw.strip()
        if text.startswith("```"):
            text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(text)
        context = data.get("vehicle_context")
        if context not in {"full_vehicle", "vehicle_part_closeup", "not_vehicle", "uncertain"}:
            context = "uncertain"
        decisions: list[VisionDecision] = []
        seen: set[str] = set()
        for item in data.get("decisions", []):
            candidate_id = str(item.get("candidate_id", ""))
            decision = item.get("decision")
            if candidate_id not in candidate_ids or candidate_id in seen:
                continue
            if decision not in {"accept", "correct", "reject"}:
                continue
            corrected = _clean_text(item.get("corrected_damage"), 80)
            if corrected:
                corrected = corrected.lower()
            if corrected not in allowed_damage_classes:
                corrected = None
            severity = _clean_text(item.get("severity"), 20)
            if severity not in {"minor", "moderate", "severe"}:
                severity = None
            refined_polygon = GeminiVisionValidator._parse_polygon(
                item.get("refined_polygon_xy"),
                width=width,
                height=height,
            )
            if decision == "reject":
                refined_polygon = None
            decisions.append(VisionDecision(
                candidate_id=candidate_id,
                decision=decision,
                corrected_damage=corrected,
                vehicle_part=_clean_text(item.get("vehicle_part"), 100),
                severity=severity,
                certainty=_clamp(item.get("certainty")),
                refined_polygon=refined_polygon,
                mask_certainty=(
                    0.0
                    if decision == "reject"
                    else _clamp(item.get("mask_certainty"))
                ),
                description=_clean_text(item.get("description"), 500),
                reason=_clean_text(item.get("reason"), 500),
            ))
            seen.add(candidate_id)
        return VisionReview(
            vehicle_context=context,
            vehicle_certainty=_clamp(data.get("vehicle_certainty")),
            decisions=tuple(decisions),
        )

    @staticmethod
    def _parse_polygon(
        value: object,
        *,
        width: int,
        height: int,
    ) -> np.ndarray | None:
        if not isinstance(value, list) or not 3 <= len(value) <= 160:
            return None
        points: list[list[float]] = []
        for point in value:
            if not isinstance(point, list) or len(point) != 2:
                return None
            try:
                normalized_x = float(point[0])
                normalized_y = float(point[1])
            except (TypeError, ValueError):
                return None
            if not np.isfinite(normalized_x) or not np.isfinite(normalized_y):
                return None
            if not (0 <= normalized_x <= 1000 and 0 <= normalized_y <= 1000):
                return None
            points.append([
                normalized_x / 1000.0 * max(width - 1, 0),
                normalized_y / 1000.0 * max(height - 1, 0),
            ])
        polygon = np.asarray(points, dtype=float)
        return polygon if _polygon_area(polygon) > 0 else None

    @staticmethod
    def _parse_box_2d(
        value: object,
        *,
        width: int,
        height: int,
    ) -> np.ndarray | None:
        if not isinstance(value, list) or len(value) != 4:
            return None
        try:
            ymin, xmin, ymax, xmax = [float(item) for item in value]
        except (TypeError, ValueError):
            return None
        if (
            not np.isfinite([ymin, xmin, ymax, xmax]).all()
            or not all(0 <= item <= 1000 for item in [ymin, xmin, ymax, xmax])
            or ymax <= ymin
            or xmax <= xmin
        ):
            return None
        return np.asarray([
            xmin / 1000.0 * max(width - 1, 0),
            ymin / 1000.0 * max(height - 1, 0),
            xmax / 1000.0 * max(width - 1, 0),
            ymax / 1000.0 * max(height - 1, 0),
        ], dtype=float)

    @staticmethod
    def _parse_direct_review(
        raw: str,
        allowed_damage_classes: set[str],
        *,
        width: int,
        height: int,
    ) -> DirectVisionReview:
        text = raw.strip()
        if text.startswith("```"):
            text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(text)
        vehicle_confirmed = bool(data.get("vehicle_confirmed"))
        findings: list[DirectVisionFinding] = []
        if vehicle_confirmed:
            for item in data.get("findings", []):
                if not isinstance(item, dict):
                    continue
                damage_class = str(item.get("damage_type", "")).lower().strip()
                severity = str(item.get("severity", "")).lower().strip()
                evidence = str(item.get("evidence_strength", "")).lower().strip()
                if damage_class not in allowed_damage_classes:
                    continue
                if severity not in {"minor", "moderate", "severe"}:
                    continue
                if evidence not in {"low", "medium", "high"}:
                    continue
                box = GeminiVisionValidator._parse_box_2d(
                    item.get("box_2d"),
                    width=width,
                    height=height,
                )
                if box is None:
                    continue
                polygon = GeminiVisionValidator._parse_direct_mask(
                    item.get("mask"),
                    box=box,
                    width=width,
                    height=height,
                )
                if polygon is None:
                    continue
                findings.append(DirectVisionFinding(
                    damage_class=damage_class,
                    vehicle_part=_clean_text(item.get("vehicle_part"), 100) or "vehicle body",
                    severity=severity,
                    evidence_strength=evidence,
                    description=_clean_text(item.get("description"), 500)
                    or f"Visible {damage_class.replace('_', ' ')}.",
                    box=box,
                    polygon=np.asarray(polygon, dtype=float),
                ))

        warnings = tuple(
            text
            for item in data.get("warnings", [])
            if (text := _clean_text(item, 300))
        )
        return DirectVisionReview(
            vehicle_confirmed=vehicle_confirmed,
            vehicle_type=_clean_text(data.get("vehicle_type"), 80),
            findings=tuple(findings),
            review_required=bool(data.get("review_required")),
            warnings=warnings,
        )

    @staticmethod
    def _parse_direct_mask(
        value: object,
        *,
        box: np.ndarray,
        width: int,
        height: int,
    ) -> np.ndarray | None:
        """Accept documented [x,y] masks and safely recover occasional [y,x] output."""
        xy = GeminiVisionValidator._parse_polygon(value, width=width, height=height)
        swapped_value = None
        if isinstance(value, list):
            swapped_value = [
                [point[1], point[0]]
                for point in value
                if isinstance(point, list) and len(point) == 2
            ]
            if len(swapped_value) != len(value):
                swapped_value = None
        yx = GeminiVisionValidator._parse_polygon(
            swapped_value,
            width=width,
            height=height,
        )
        candidates = [
            polygon
            for polygon in (xy, yx)
            if _usable_refined_polygon(polygon, box)
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda polygon: _polygon_box_fit_score(polygon, box))
