import numpy as np
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.exceptions import NonVehicleImageError, StorageError
from ml.types import InferenceResult, VehicleDetection
from services.analysis_service import AnalysisService
from services.storage_service import StorageService


def result(*, rejected: bool, vehicle_confirmed: bool) -> InferenceResult:
    vehicles = (
        [VehicleDetection("car", 0.9, np.array([0, 0, 100, 100], dtype=float))]
        if vehicle_confirmed
        else []
    )
    return InferenceResult(
        annotated_image=np.zeros((120, 160, 3), dtype=np.uint8),
        vehicles=vehicles,
        image_rejected_as_non_vehicle=rejected,
    )


def test_non_vehicle_result_stops_analysis_with_user_message():
    with pytest.raises(NonVehicleImageError, match="Please attach a vehicle image"):
        AnalysisService._require_vehicle_image(
            result(rejected=True, vehicle_confirmed=False),
        )


def test_unconfirmed_image_stops_even_without_explicit_negative_review():
    with pytest.raises(NonVehicleImageError, match="Please attach a vehicle image"):
        AnalysisService._require_vehicle_image(
            result(rejected=False, vehicle_confirmed=False),
        )


def test_confirmed_vehicle_result_can_continue():
    AnalysisService._require_vehicle_image(
        result(rejected=False, vehicle_confirmed=True),
    )


def test_failed_upload_cleanup_only_deletes_file_inside_storage():
    with TemporaryDirectory(prefix="storage-cleanup-", dir=Path.cwd()) as temporary:
        root = Path(temporary)
        storage = StorageService()
        storage.root = root
        target = root / "vehicles" / "1" / "damage" / "rejected.jpg"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"temporary")

        storage.delete_file("vehicles/1/damage/rejected.jpg")

        assert not target.exists()
        with pytest.raises(StorageError):
            storage.delete_file("../outside.jpg")
