from __future__ import annotations

import cv2
import numpy as np

from core.constants import CLASS_COLORS
from ml.types import VehicleDetection, DamageDetection


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
    mask_layer = canvas.copy()

    for d in damages:
        color = CLASS_COLORS.get(d.damage_class, (255, 255, 255))
        bgr = (color[2], color[1], color[0])
        polygon = d.polygon
        if polygon is not None and len(polygon) >= 3:
            points = np.asarray(polygon, dtype=np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(mask_layer, [points], bgr)

    canvas = cv2.addWeighted(mask_layer, 0.34, canvas, 0.66, 0)

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

    for d in damages:
        x1, y1, x2, y2 = map(int, d.box)
        color = CLASS_COLORS.get(d.damage_class, (255, 255, 255))
        bgr = (color[2], color[1], color[0])
        polygon = d.polygon
        if polygon is not None and len(polygon) >= 3:
            points = np.asarray(polygon, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(canvas, [points], True, bgr, 2)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), bgr, 2)
        label = f"{d.damage_class.replace('_', ' ')} {d.confidence:.0%}"
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
