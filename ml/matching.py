from __future__ import annotations

import numpy as np


def intersection_ratio(damage_box: np.ndarray, vehicle_box: np.ndarray) -> float:
    """
    Calculates the ratio of the intersection area between damage_box and vehicle_box
    relative to the damage_box area.
    """
    dx1, dy1, dx2, dy2 = damage_box
    vx1, vy1, vx2, vy2 = vehicle_box
    ix1, iy1 = max(dx1, vx1), max(dy1, vy1)
    ix2, iy2 = min(dx2, vx2), min(dy2, vy2)
    intersection = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    damage_area = max(1.0, (dx2 - dx1) * (dy2 - dy1))
    return float(intersection / damage_area)


def damage_matches_vehicle(
    damage_box: np.ndarray,
    vehicle_boxes: list[np.ndarray],
    min_overlap: float = 0.20,
) -> tuple[bool, float]:
    """
    Returns (matched, max_overlap_ratio).
    A damage box matches if its center is inside a vehicle box or if overlap >= min_overlap (20%).
    """
    if not vehicle_boxes:
        return False, 0.0

    x1, y1, x2, y2 = damage_box
    center_x, center_y = (x1 + x2) / 2.0, (y1 + y2) / 2.0
    max_ratio = 0.0

    for vehicle_box in vehicle_boxes:
        vx1, vy1, vx2, vy2 = vehicle_box
        ratio = intersection_ratio(damage_box, vehicle_box)
        if ratio > max_ratio:
            max_ratio = ratio

        center_inside = vx1 <= center_x <= vx2 and vy1 <= center_y <= vy2
        if center_inside or ratio >= min_overlap:
            return True, max(max_ratio, ratio)

    return False, max_ratio
