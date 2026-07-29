import numpy as np

from ml.damage_analyzer import DamageAnalyzer


def test_puncture_rejected_from_central_bumper_region():
    vehicle = np.array([100, 100, 900, 700], dtype=float)
    central_bumper = np.array([570, 510, 620, 560], dtype=float)
    assert not DamageAnalyzer._is_spatially_plausible("puncture", central_bumper, [vehicle])


def test_puncture_allowed_in_lower_outer_wheel_region():
    vehicle = np.array([100, 100, 900, 700], dtype=float)
    wheel_region = np.array([700, 480, 820, 650], dtype=float)
    assert DamageAnalyzer._is_spatially_plausible("puncture", wheel_region, [vehicle])


def test_other_damage_classes_are_not_position_filtered():
    vehicle = np.array([100, 100, 900, 700], dtype=float)
    center = np.array([450, 300, 550, 400], dtype=float)
    assert DamageAnalyzer._is_spatially_plausible("dent", center, [vehicle])
