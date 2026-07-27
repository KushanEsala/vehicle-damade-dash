from __future__ import annotations

import hashlib
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DAMAGE_MODEL = (
    PROJECT_DIR
    / "Runscomplete"
    / "runs"
    / "vehicle_damage_seg-2"
    / "weights"
    / "best.pt"
)
VEHICLE_MODEL = PROJECT_DIR / "yolov8n.pt"

EXPECTED_HASHES = {
    DAMAGE_MODEL: "c9d86e67a4c14f65047f33c17b4c4357613a0a15b52f919d76ff1c8542c0d541",
    VEHICLE_MODEL: "f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36",
}
EXPECTED_DAMAGE_CLASSES = {
    "scratch",
    "dent",
    "tear",
    "missing_part",
    "broken_lamp",
    "puncture",
    "broken_glass",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def main() -> None:
    print(f"Python: {sys.version.split()[0]}")

    for path, expected_hash in EXPECTED_HASHES.items():
        if not path.is_file():
            fail(f"Missing model: {path}")
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            fail(
                f"Checksum mismatch for {path.name}.\n"
                f"Expected: {expected_hash}\n"
                f"Actual:   {actual_hash}"
            )
        print(f"Model verified: {path.name}")

    try:
        import numpy as np
        import streamlit
        import torch
        import ultralytics
        from ultralytics import YOLO
    except Exception as error:
        fail(f"Package import failed: {error}")

    print(f"PyTorch: {torch.__version__}")
    print(f"Ultralytics: {ultralytics.__version__}")
    print(f"Streamlit: {streamlit.__version__}")
    device: int | str = 0 if torch.cuda.is_available() else "cpu"
    runtime = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    print(f"Runtime: {runtime}")

    try:
        damage_model = YOLO(str(DAMAGE_MODEL))
        vehicle_model = YOLO(str(VEHICLE_MODEL))
    except Exception as error:
        fail(f"Model loading failed: {error}")

    actual_classes = set(damage_model.names.values())
    if actual_classes != EXPECTED_DAMAGE_CLASSES:
        fail(
            "Damage classes do not match the expected model.\n"
            f"Expected: {sorted(EXPECTED_DAMAGE_CLASSES)}\n"
            f"Actual:   {sorted(actual_classes)}"
        )

    test_image = np.zeros((320, 320, 3), dtype=np.uint8)
    try:
        damage_model.predict(test_image, imgsz=320, device=device, verbose=False)
        vehicle_model.predict(test_image, imgsz=320, device=device, verbose=False)
    except Exception as error:
        fail(f"Inference smoke test failed: {error}")

    print(f"Damage classes: {', '.join(sorted(actual_classes))}")
    print("Inference smoke test: passed")
    print("SETUP VERIFIED")


if __name__ == "__main__":
    main()

