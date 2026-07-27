from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

import yaml


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = PROJECT_DIR / "data"
DEFAULT_OUTPUT_YAML = PROJECT_DIR / "prepared_dataset.yaml"


def extract_archives(data_dir: Path) -> None:
    archives = sorted(data_dir.glob("*.zip"))
    for archive in archives:
        destination = data_dir / archive.stem
        if destination.exists():
            print(f"Already extracted: {destination}")
            continue
        print(f"Extracting {archive.name} -> {destination}")
        destination.mkdir(parents=True)
        with zipfile.ZipFile(archive) as zip_file:
            zip_file.extractall(destination)


def find_dataset_yaml(data_dir: Path) -> Path:
    candidates = sorted(
        path
        for pattern in ("dataset.yaml", "data.yaml")
        for path in data_dir.rglob(pattern)
        if path.is_file()
    )
    if not candidates:
        raise FileNotFoundError(
            f"No dataset.yaml or data.yaml found under {data_dir}. "
            "Copy your YOLO dataset folder or ZIP into the data folder."
        )
    if len(candidates) > 1:
        print("Multiple dataset YAML files found; using:")
        for candidate in candidates:
            print(f"  {'*' if candidate == candidates[0] else '-'} {candidate}")
    return candidates[0]


def detect_split(dataset_root: Path, split: str) -> str | None:
    possibilities = (
        Path("images") / split,
        Path(split) / "images",
    )
    for relative_path in possibilities:
        if (dataset_root / relative_path).is_dir():
            return relative_path.as_posix()
    return None


def prepare(data_dir: Path, output_yaml: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    extract_archives(data_dir)
    source_yaml = find_dataset_yaml(data_dir)
    dataset_root = source_yaml.parent.resolve()

    with source_yaml.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    train = detect_split(dataset_root, "train") or config.get("train")
    val = detect_split(dataset_root, "val") or config.get("val")
    if not train or not val:
        raise ValueError(
            "Could not determine train/validation image folders. Expected "
            "images/train + images/val or train/images + val/images."
        )

    config["path"] = str(dataset_root)
    config["train"] = train
    config["val"] = val

    output_yaml.parent.mkdir(parents=True, exist_ok=True)
    with output_yaml.open("w", encoding="utf-8") as file:
        yaml.safe_dump(config, file, sort_keys=False, allow_unicode=True)

    print(f"Source YAML:   {source_yaml}")
    print(f"Dataset root:  {dataset_root}")
    print(f"Train images:  {train}")
    print(f"Val images:    {val}")
    print(f"Prepared YAML: {output_yaml}")
    return output_yaml


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a local YOLO dataset.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_YAML)
    args = parser.parse_args()
    prepare(args.data_dir.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()

