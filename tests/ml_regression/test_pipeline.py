from __future__ import annotations

import numpy as np
import pytest

from ml.pipeline import get_pipeline
from ml.types import InferenceRequest


def test_pipeline_smoke_test():
    pipeline = get_pipeline()
    test_image = np.zeros((320, 320, 3), dtype=np.uint8)
    req = InferenceRequest(image=test_image, damage_confidence=0.30, vehicle_confidence=0.25, require_vehicle=True)
    res = pipeline.run(req)

    assert res.annotated_image is not None
    assert res.annotated_image.shape == (320, 320, 3)
    assert isinstance(res.vehicles, list)
    assert isinstance(res.accepted_damages, list)
    assert isinstance(res.rejected_damages, list)
    assert len(res.damage_model_hash) == 64
    assert len(res.vehicle_model_hash) == 64
