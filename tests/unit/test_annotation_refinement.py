import cv2
import numpy as np

from ml.annotator import _display_mask, annotate_image
from ml.types import DamageDetection, VehicleDetection


def broken_glass_fixture() -> tuple[np.ndarray, DamageDetection]:
    image = np.full((240, 320, 3), 65, dtype=np.uint8)
    polygon = np.array([[30, 30], [290, 30], [290, 210], [30, 210]], dtype=float)
    center = (160, 120)
    for endpoint in [(55, 45), (265, 45), (285, 120), (255, 195), (70, 200), (35, 125)]:
        cv2.line(image, center, endpoint, (225, 225, 225), 2)
    damage = DamageDetection(
        damage_class="broken_glass",
        confidence=0.91,
        box=np.array([30, 30, 290, 210], dtype=float),
        polygon=polygon,
    )
    return image, damage


def test_broken_glass_display_mask_marks_cracks_not_whole_glass_panel():
    image, damage = broken_glass_fixture()
    refined = _display_mask(image, damage)
    polygon_area = (290 - 30) * (210 - 30)
    refined_area = cv2.countNonZero(refined)

    assert refined_area > 100
    assert refined_area < polygon_area * 0.35
    assert refined[120, 160] == 255
    assert refined[80, 160] == 0


def test_gemini_refined_glass_region_still_marks_cracks_instead_of_full_pane():
    image, damage = broken_glass_fixture()
    damage.mask_refined = True
    refined = _display_mask(image, damage)
    polygon_area = (290 - 30) * (210 - 30)

    assert 100 < cv2.countNonZero(refined) < polygon_area * 0.35
    assert refined[120, 160] == 255
    assert refined[80, 160] == 0


def test_segmentation_overlay_does_not_draw_full_damage_rectangle():
    image, damage = broken_glass_fixture()
    annotated = annotate_image(image, [], [damage])

    # The former implementation drew a cyan rectangle on this exact corner.
    # The refined display keeps undamaged panel pixels close to the source.
    difference = np.abs(annotated[210, 290].astype(int) - image[210, 290].astype(int))
    assert int(difference.max()) < 20


def test_refined_report_overlay_hides_generic_vehicle_detector_box():
    image = np.full((120, 160, 3), 70, dtype=np.uint8)
    vehicle = VehicleDetection(
        vehicle_class="bus",
        confidence=0.48,
        box=np.array([5, 5, 150, 110], dtype=float),
    )
    damage = DamageDetection(
        damage_class="dent",
        confidence=0.90,
        box=np.array([50, 50, 90, 85], dtype=float),
        source="hybrid",
        polygon=np.array([[50, 50], [90, 50], [88, 85], [52, 83]], dtype=float),
        mask_refined=True,
        vehicle_part="hood",
    )

    annotated = annotate_image(image, [vehicle], [damage])

    np.testing.assert_array_equal(annotated[5, 5], image[5, 5])
