import numpy as np

from ml.types import DamageDetection
from ml.vision_validator import (
    DirectVisionFinding,
    DirectVisionReview,
    GeminiVisionValidator,
    VisionDecision,
    VisionReview,
    apply_direct_vision_review,
    apply_vision_review,
    build_candidates,
)


def detection(name: str, *, passed: bool = True) -> DamageDetection:
    return DamageDetection(
        damage_class=name,
        confidence=0.81,
        box=np.array([10, 20, 80, 90], dtype=float),
        passed_vehicle_gate=passed,
    )


def test_high_certainty_visual_rejection_removes_false_positive():
    candidates = build_candidates([detection("puncture")], [])
    review = VisionReview(
        vehicle_context="full_vehicle",
        vehicle_certainty=0.99,
        decisions=(VisionDecision(
            candidate_id="accepted-0",
            decision="reject",
            corrected_damage=None,
            vehicle_part="front bumper",
            severity=None,
            certainty=0.95,
            refined_polygon=None,
            mask_certainty=0.0,
            description=None,
            reason="No tyre or wheel is present.",
        ),),
    )

    accepted, rejected, supplemental = apply_vision_review(
        candidates,
        review,
        allowed_damage_classes={"puncture", "dent"},
        initially_vehicle_confirmed=True,
        require_vehicle=True,
    )

    assert not accepted
    assert len(rejected) == 1
    assert rejected[0].vehicle_part == "front bumper"
    assert not supplemental


def test_visual_review_corrects_supported_class_and_prefills_review_fields():
    candidates = build_candidates([detection("tear")], [])
    review = VisionReview(
        vehicle_context="full_vehicle",
        vehicle_certainty=0.95,
        decisions=(VisionDecision(
            candidate_id="accepted-0",
            decision="correct",
            corrected_damage="scratch",
            vehicle_part="left front door",
            severity="minor",
            certainty=0.92,
            refined_polygon=None,
            mask_certainty=0.0,
            description="Surface abrasion on the left front door.",
            reason="The panel is abraded rather than torn.",
        ),),
    )

    accepted, rejected, _ = apply_vision_review(
        candidates,
        review,
        allowed_damage_classes={"tear", "scratch"},
        initially_vehicle_confirmed=True,
        require_vehicle=True,
    )

    assert not rejected
    assert accepted[0].damage_class == "scratch"
    assert accepted[0].vehicle_part == "left front door"
    assert accepted[0].severity == "minor"


def test_closeup_confirmation_can_recover_vehicle_gated_candidate():
    candidates = build_candidates([], [detection("dent", passed=False)])
    review = VisionReview(
        vehicle_context="vehicle_part_closeup",
        vehicle_certainty=0.91,
        decisions=(VisionDecision(
            candidate_id="rejected-0",
            decision="accept",
            corrected_damage=None,
            vehicle_part="rear quarter panel",
            severity="moderate",
            certainty=0.88,
            refined_polygon=None,
            mask_certainty=0.0,
            description="A visible inward deformation.",
            reason="The crop contains a damaged vehicle body panel.",
        ),),
    )

    accepted, rejected, supplemental = apply_vision_review(
        candidates,
        review,
        allowed_damage_classes={"dent"},
        initially_vehicle_confirmed=False,
        require_vehicle=True,
    )

    assert supplemental
    assert len(accepted) == 1
    assert not rejected


def test_high_confidence_refined_mask_replaces_display_polygon_and_preserves_model_mask():
    original_polygon = np.array(
        [[10, 20], [80, 20], [80, 90], [10, 90]],
        dtype=float,
    )
    refined_polygon = np.array(
        [[30, 40], [52, 38], [61, 55], [46, 67], [28, 59]],
        dtype=float,
    )
    damage = detection("dent")
    damage.polygon = original_polygon
    candidates = build_candidates([damage], [])
    review = VisionReview(
        vehicle_context="full_vehicle",
        vehicle_certainty=0.98,
        decisions=(VisionDecision(
            candidate_id="accepted-0",
            decision="accept",
            corrected_damage=None,
            vehicle_part="front bumper",
            severity="moderate",
            certainty=0.94,
            refined_polygon=refined_polygon,
            mask_certainty=0.91,
            description="Localized deformation on the front bumper.",
            reason="Visible deformation is confined to the marked area.",
        ),),
    )

    accepted, rejected, _ = apply_vision_review(
        candidates,
        review,
        allowed_damage_classes={"dent"},
        initially_vehicle_confirmed=True,
        require_vehicle=True,
    )

    assert not rejected
    assert accepted[0].mask_refined
    np.testing.assert_array_equal(accepted[0].polygon, refined_polygon)
    np.testing.assert_array_equal(accepted[0].model_polygon, original_polygon)


def test_refined_mask_outside_candidate_is_rejected_and_model_mask_remains_active():
    original_polygon = np.array(
        [[10, 20], [80, 20], [80, 90], [10, 90]],
        dtype=float,
    )
    outside_polygon = np.array(
        [[150, 160], [220, 160], [220, 230], [150, 230]],
        dtype=float,
    )
    damage = detection("scratch")
    damage.polygon = original_polygon
    candidates = build_candidates([damage], [])
    review = VisionReview(
        vehicle_context="full_vehicle",
        vehicle_certainty=0.98,
        decisions=(VisionDecision(
            candidate_id="accepted-0",
            decision="accept",
            corrected_damage=None,
            vehicle_part="left door",
            severity="minor",
            certainty=0.97,
            refined_polygon=outside_polygon,
            mask_certainty=0.96,
            description="Surface scratch.",
            reason="Visible scratch.",
        ),),
    )

    accepted, rejected, _ = apply_vision_review(
        candidates,
        review,
        allowed_damage_classes={"scratch"},
        initially_vehicle_confirmed=True,
        require_vehicle=True,
    )

    assert not rejected
    assert not accepted[0].mask_refined
    assert accepted[0].model_polygon is None
    np.testing.assert_array_equal(accepted[0].polygon, original_polygon)


def test_gemini_normalized_polygon_is_converted_to_full_image_pixels():
    raw = """
    {
      "vehicle_context": "vehicle_part_closeup",
      "vehicle_certainty": 0.96,
      "decisions": [{
        "candidate_id": "accepted-0",
        "decision": "accept",
        "corrected_damage": null,
        "vehicle_part": "windscreen",
        "severity": "severe",
        "certainty": 0.95,
        "refined_polygon_xy": [[100, 200], [500, 200], [500, 600], [100, 600]],
        "mask_certainty": 0.9,
        "description": "Cracked area on the windscreen.",
        "reason": "Visible radiating fractures."
      }]
    }
    """

    review = GeminiVisionValidator._parse_review(
        raw,
        {"accepted-0"},
        {"broken_glass"},
        width=1001,
        height=501,
    )

    polygon = review.decisions[0].refined_polygon
    assert polygon is not None
    np.testing.assert_allclose(
        polygon,
        np.array([[100, 100], [500, 100], [500, 300], [100, 300]], dtype=float),
    )


def test_confirmed_non_vehicle_rejects_findings_even_when_vehicle_gate_is_disabled():
    candidates = build_candidates([detection("dent")], [])
    review = VisionReview(
        vehicle_context="not_vehicle",
        vehicle_certainty=0.97,
        decisions=(VisionDecision(
            candidate_id="accepted-0",
            decision="accept",
            corrected_damage=None,
            vehicle_part=None,
            severity=None,
            certainty=0.85,
            refined_polygon=None,
            mask_certainty=0.0,
            description=None,
            reason="The image is a diagram rather than a vehicle.",
        ),),
    )

    accepted, rejected, supplemental = apply_vision_review(
        candidates,
        review,
        allowed_damage_classes={"dent"},
        initially_vehicle_confirmed=False,
        require_vehicle=False,
    )

    assert not accepted
    assert len(rejected) == 1
    assert not supplemental


def test_current_provider_payload_uses_interactions_and_valid_jpeg_mime_type():
    validator = GeminiVisionValidator(secret_reader=lambda: "not-used")
    payload = validator._build_payload("inspect", "encoded-image", ["dent"])

    assert validator.ENDPOINT.endswith("/v1beta/interactions")
    assert payload["model"] == "gemini-3.6-flash"
    assert payload["input"][1]["mime_type"] == "image/jpeg"
    assert payload["input"][1]["mime_type"] != "image/jpg"


def test_direct_schema_is_restricted_to_trained_system_classes():
    allowed = [
        "scratch",
        "dent",
        "tear",
        "missing_part",
        "broken_lamp",
        "puncture",
        "broken_glass",
    ]
    schema = GeminiVisionValidator._direct_response_schema(allowed)
    enum = (
        schema["properties"]["findings"]["items"]["properties"]
        ["damage_type"]["enum"]
    )

    assert enum == allowed
    assert "crack" not in enum
    assert "paint_damage" not in enum
    assert "other" not in enum
    assert "background" not in enum


def test_direct_review_parses_full_image_boxes_and_masks():
    raw = """
    {
      "vehicle_confirmed": true,
      "vehicle_type": "suv",
      "findings": [{
        "damage_type": "dent",
        "vehicle_part": "hood",
        "severity": "severe",
        "evidence_strength": "high",
        "description": "Impact deformation on the hood.",
        "box_2d": [200, 100, 600, 700],
        "mask": [[100, 200], [700, 200], [700, 600], [100, 600]]
      }, {
        "damage_type": "other",
        "vehicle_part": "road",
        "severity": "minor",
        "evidence_strength": "high",
        "description": "Unsupported class.",
        "box_2d": [0, 0, 100, 100],
        "mask": [[0, 0], [100, 0], [100, 100]]
      }],
      "review_required": false,
      "warnings": []
    }
    """
    review = GeminiVisionValidator._parse_direct_review(
        raw,
        {"dent", "broken_lamp"},
        width=1001,
        height=501,
    )

    assert review.vehicle_confirmed
    assert review.vehicle_type == "suv"
    assert len(review.findings) == 1
    finding = review.findings[0]
    assert finding.damage_class == "dent"
    np.testing.assert_allclose(finding.box, [100, 100, 700, 300])
    np.testing.assert_allclose(
        finding.polygon,
        [[100, 100], [700, 100], [700, 300], [100, 300]],
    )


def test_direct_review_recovers_provider_mask_when_xy_order_is_reversed():
    raw = """
    {
      "vehicle_confirmed": true,
      "vehicle_type": "pickup truck",
      "findings": [{
        "damage_type": "dent",
        "vehicle_part": "hood",
        "severity": "severe",
        "evidence_strength": "high",
        "description": "Impact deformation.",
        "box_2d": [281, 256, 414, 800],
        "mask": [[286, 281], [300, 483], [312, 608], [293, 769],
                 [324, 795], [356, 736], [389, 696], [411, 511],
                 [400, 350], [385, 258]]
      }],
      "review_required": false,
      "warnings": []
    }
    """
    review = GeminiVisionValidator._parse_direct_review(
        raw,
        {"dent"},
        width=1001,
        height=1001,
    )

    assert len(review.findings) == 1
    finding = review.findings[0]
    assert np.all(finding.polygon[:, 0] >= finding.box[0])
    assert np.all(finding.polygon[:, 0] <= finding.box[2])
    assert np.all(finding.polygon[:, 1] >= finding.box[1])
    assert np.all(finding.polygon[:, 1] <= finding.box[3])


def test_direct_review_splits_one_broad_yolo_region_into_multiple_findings():
    broad = detection("dent")
    broad.polygon = np.array([[10, 20], [80, 20], [80, 90], [10, 90]], dtype=float)
    candidates = build_candidates([broad], [])
    review = DirectVisionReview(
        vehicle_confirmed=True,
        vehicle_type="suv",
        findings=(
            DirectVisionFinding(
                damage_class="dent",
                vehicle_part="hood",
                severity="severe",
                evidence_strength="high",
                description="Buckling on the hood.",
                box=np.array([15, 22, 75, 50], dtype=float),
                polygon=np.array([[15, 22], [75, 22], [70, 50], [20, 48]], dtype=float),
            ),
            DirectVisionFinding(
                damage_class="dent",
                vehicle_part="front bumper",
                severity="severe",
                evidence_strength="high",
                description="Displaced front bumper.",
                box=np.array([12, 52, 78, 88], dtype=float),
                polygon=np.array([[12, 55], [78, 52], [75, 88], [16, 86]], dtype=float),
            ),
            DirectVisionFinding(
                damage_class="broken_lamp",
                vehicle_part="headlight",
                severity="severe",
                evidence_strength="high",
                description="Broken headlight assembly.",
                box=np.array([18, 38, 38, 58], dtype=float),
                polygon=np.array([[18, 38], [38, 40], [36, 58], [20, 56]], dtype=float),
            ),
        ),
        review_required=False,
        warnings=(),
    )

    accepted, rejected, supplemental = apply_direct_vision_review(
        candidates,
        review,
        allowed_damage_classes={
            "scratch",
            "dent",
            "tear",
            "missing_part",
            "broken_lamp",
            "puncture",
            "broken_glass",
        },
        initially_vehicle_confirmed=True,
    )

    assert len(accepted) == 3
    assert not rejected
    assert not supplemental
    assert {item.vehicle_part for item in accepted} == {
        "hood",
        "front bumper",
        "headlight",
    }
    assert sum(item.source == "hybrid" for item in accepted) == 1
    assert sum(item.source == "vision" for item in accepted) == 2
    assert all(item.mask_refined for item in accepted)


def test_direct_non_vehicle_review_rejects_every_local_candidate():
    candidates = build_candidates([detection("scratch")], [])
    review = DirectVisionReview(
        vehicle_confirmed=False,
        vehicle_type=None,
        findings=(),
        review_required=False,
        warnings=("No vehicle is visible.",),
    )

    accepted, rejected, supplemental = apply_direct_vision_review(
        candidates,
        review,
        allowed_damage_classes={"scratch"},
        initially_vehicle_confirmed=False,
    )

    assert not accepted
    assert len(rejected) == 1
    assert not supplemental


def test_uncertain_review_does_not_override_primary_detector():
    candidates = build_candidates([detection("dent")], [])
    review = VisionReview(
        vehicle_context="uncertain",
        vehicle_certainty=0.4,
        decisions=(VisionDecision(
            candidate_id="accepted-0",
            decision="reject",
            corrected_damage=None,
            vehicle_part=None,
            severity=None,
            certainty=0.4,
            refined_polygon=None,
            mask_certainty=0.0,
            description=None,
            reason=None,
        ),),
    )

    accepted, rejected, _ = apply_vision_review(
        candidates,
        review,
        allowed_damage_classes={"dent"},
        initially_vehicle_confirmed=True,
        require_vehicle=True,
    )

    assert len(accepted) == 1
    assert not rejected
