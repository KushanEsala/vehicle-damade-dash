from __future__ import annotations

import argparse
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Train vehicle-damage YOLO segmentation.")
    parser.add_argument(
        "--confirm-train",
        action="store_true",
        help="Required safety flag. Training will not start without it.",
    )
    parser.add_argument("--data", type=Path, default=PROJECT_DIR / "prepared_dataset.yaml")
    parser.add_argument("--model", default="yolov8n-seg.pt")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--device", default=None, help="Examples: 0, cpu. Default: auto-detect.")
    args = parser.parse_args()

    if not args.confirm_train:
        print("Training NOT started.")
        print("When ready, run: python train.py --confirm-train")
        return

    data_path = args.data.resolve()
    if not data_path.is_file():
        raise FileNotFoundError(
            f"Missing {data_path}. Run `python prepare_dataset.py` first."
        )

    import torch
    from ultralytics import YOLO

    device = args.device
    if device is None:
        device = 0 if torch.cuda.is_available() else "cpu"

    if torch.cuda.is_available() and str(device) != "cpu":
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("Using CPU. Training may be slow.")

    output_dir = PROJECT_DIR / "runs" / "vehicle_damage_seg"
    print(f"Live training files will be written to: {output_dir}")
    print("To watch charts, run watch_training.ps1 in another PowerShell window.")

    model = YOLO(args.model)
    model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=str(PROJECT_DIR / "runs"),
        name="vehicle_damage_seg",
        device=device,
        workers=args.workers,
        val=True,
        plots=True,
        save=True,
    )


if __name__ == "__main__":
    main()
