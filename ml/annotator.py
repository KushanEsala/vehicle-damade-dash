from __future__ import annotations

import cv2
import numpy as np

from core.constants import CLASS_COLORS
from ml.types import VehicleDetection, DamageDetection


def _polygon_mask(image_shape: tuple[int, ...], polygon: np.ndarray | None) -> np.ndarray:
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    if polygon is None or len(polygon) < 3:
        return mask
    points = np.asarray(polygon, dtype=np.int32).reshape((-1, 1, 2))
    cv2.fillPoly(mask, [points], 255)
    return mask


def _remove_small_components(mask: np.ndarray, minimum_area: int) -> np.ndarray:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    cleaned = np.zeros_like(mask)
    for label in range(1, count):
        if stats[label, cv2.CC_STAT_AREA] >= minimum_area:
            cleaned[labels == label] = 255
    return cleaned


def _refine_broken_glass_mask(image_rgb: np.ndarray, region_mask: np.ndarray) -> np.ndarray:
    """Create a thin, display-only crack mask inside the model's glass region."""
    if cv2.countNonZero(region_mask) == 0:
        return region_mask

    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(8, 8)).apply(gray)
    smooth = cv2.GaussianBlur(gray, (9, 9), 0)
    local_detail = cv2.absdiff(gray, smooth)
    edges = cv2.Canny(gray, 45, 135)

    # Ignore the model polygon boundary itself; it represents the glass panel,
    # not a crack.
    region_area = cv2.countNonZero(region_mask)
    erosion_radius = max(3, round(np.sqrt(region_area) * 0.008))
    erosion_radius = erosion_radius + 1 if erosion_radius % 2 == 0 else erosion_radius
    interior = cv2.erode(
        region_mask,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (erosion_radius, erosion_radius)),
    )
    if cv2.countNonZero(interior) == 0:
        interior = region_mask

    detail_values = local_detail[interior > 0]
    if detail_values.size == 0:
        return np.zeros_like(region_mask)
    detail_threshold = max(12, int(np.percentile(detail_values, 82)))
    detailed = np.where(local_detail >= detail_threshold, 255, 0).astype(np.uint8)
    cracks = cv2.bitwise_or(edges, detailed)
    cracks = cv2.bitwise_and(cracks, interior)
    cracks = cv2.morphologyEx(
        cracks,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
        iterations=1,
    )
    cracks = cv2.dilate(
        cracks,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
        iterations=1,
    )
    minimum_component = max(8, round(region_area * 0.00015))
    return _remove_small_components(cracks, minimum_component)


def _display_mask(image_rgb: np.ndarray, damage: DamageDetection) -> np.ndarray:
    model_mask = _polygon_mask(image_rgb.shape, damage.polygon)
    class_name = damage.damage_class.lower().strip().replace(" ", "_").replace("-", "_")
    # Even a correct glass-region polygon is too broad for display: the actual
    # damage is the crack network within that region. Gemini still narrows the
    # region first when available; this pass extracts the visible fracture
    # pixels without tinting the entire pane.
    if class_name == "broken_glass":
        return _refine_broken_glass_mask(image_rgb, model_mask)
    return model_mask


def _blend_mask(canvas: np.ndarray, mask: np.ndarray, bgr: tuple[int, int, int], alpha: float) -> None:
    if cv2.countNonZero(mask) == 0 or alpha <= 0:
        return
    overlay = canvas.copy()
    overlay[mask > 0] = bgr
    blended = cv2.addWeighted(overlay, alpha, canvas, 1.0 - alpha, 0)
    canvas[mask > 0] = blended[mask > 0]


def _finding_label(damage: DamageDetection) -> str:
    damage_text = damage.damage_class.replace("_", " ").strip()
    part = (damage.vehicle_part or "").replace("_", " ").strip()
    if not part:
        description = damage_text
    elif damage.damage_class in {"broken_lamp", "broken_glass"}:
        description = f"broken {part}"
    elif damage.damage_class == "missing_part":
        description = f"missing {part}"
    else:
        description = f"{part} {damage_text}"
    return f"{description.title()} {damage.confidence:.0%}"


def annotate_image(
    image_rgb: np.ndarray,
    vehicles: list[VehicleDetection],
    damages: list[DamageDetection],
) -> np.ndarray:
    """
    Renders vehicle bounding boxes, damage bounding boxes, segmentation masks, and labels
    identically to the baseline model_tester.py.
    """
    canvas = cv2.cvtColor(image_rgb.copy(), cv2.COLOR_RGB2BGR)
    display_masks: list[np.ndarray] = []
    for d in damages:
        color = CLASS_COLORS.get(d.damage_class, (255, 255, 255))
        bgr = (color[2], color[1], color[0])
        mask = _display_mask(image_rgb, d)
        display_masks.append(mask)
        mask_area = cv2.countNonZero(mask)
        image_area = max(mask.shape[0] * mask.shape[1], 1)
        class_name = d.damage_class.lower().strip().replace(" ", "_").replace("-", "_")
        if class_name == "broken_glass":
            _blend_mask(canvas, mask, bgr, 0.42)
        elif mask_area / image_area <= 0.22:
            _blend_mask(canvas, mask, bgr, 0.20)

    # A direct full-image review already confirmed the vehicle context. Keep
    # issued report images focused on the damage parts and avoid displaying an
    # unrelated COCO vehicle-class label such as "bus" on a damaged pickup.
    if not any(d.source in {"hybrid", "vision"} for d in damages):
        for v in vehicles:
            x1, y1, x2, y2 = map(int, v.box)
            cv2.rectangle(canvas, (x1, y1), (x2, y2), (155, 222, 80), 2)
            label = f"{v.vehicle_class} {v.confidence:.0%}"
            cv2.putText(
                canvas,
                label,
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                (155, 222, 80),
                2,
            )

    for index, d in enumerate(damages):
        x1, y1, x2, y2 = map(int, d.box)
        color = CLASS_COLORS.get(d.damage_class, (255, 255, 255))
        bgr = (color[2], color[1], color[0])
        polygon = d.polygon
        mask = display_masks[index]
        class_name = d.damage_class.lower().strip().replace(" ", "_").replace("-", "_")
        if class_name == "broken_glass" and cv2.countNonZero(mask):
            contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(canvas, contours, -1, bgr, 1)
        elif polygon is not None and len(polygon) >= 3:
            points = np.asarray(polygon, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(canvas, [points], True, bgr, 2)
        else:
            cv2.rectangle(canvas, (x1, y1), (x2, y2), bgr, 2)
        label = _finding_label(d)
        text_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.58, 2)
        top = max(0, y1 - text_size[1] - 12)
        cv2.rectangle(canvas, (x1, top), (x1 + text_size[0] + 10, y1), bgr, -1)
        cv2.putText(
            canvas,
            label,
            (x1 + 5, y1 - 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            (10, 14, 18),
            2,
        )

    return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
