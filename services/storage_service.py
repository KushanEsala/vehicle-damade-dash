from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from PIL import Image

from core.config import get_settings
from core.constants import ALLOWED_IMAGE_MIME_TYPES, ALLOWED_IMAGE_EXTENSIONS, MAX_UPLOAD_SIZE_BYTES
from core.exceptions import ValidationError, StorageError


class StorageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.root = self.settings.storage_path
        self.root.mkdir(parents=True, exist_ok=True)

    def validate_image(self, file_bytes: bytes, filename: str) -> str:
        if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
            raise ValidationError(f"File size exceeds maximum allowed ({MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB).")

        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError(f"File extension '{ext}' is not supported. Allowed: {sorted(ALLOWED_IMAGE_EXTENSIONS)}")

        try:
            from io import BytesIO
            img = Image.open(BytesIO(file_bytes))
            img.verify()
            mime = Image.MIME.get(img.format, "image/jpeg")
            if mime not in ALLOWED_IMAGE_MIME_TYPES:
                raise ValidationError(f"MIME type '{mime}' is not supported.")
            return mime
        except Exception as e:
            raise ValidationError(f"Invalid image file: {e}")

    def save_vehicle_image(
        self,
        vehicle_id: int,
        file_bytes: bytes,
        original_filename: str,
        category: str = "profile",
    ) -> tuple[str, str, int, int, int]:
        """
        Saves image under storage/vehicles/{vehicle_id}/{category}/UUID.ext.
        Returns (relative_path, sha256_hash, width, height, file_size).
        """
        mime = self.validate_image(file_bytes, original_filename)
        ext = Path(original_filename).suffix.lower()
        if not ext:
            ext = ".jpg"

        file_uuid = uuid.uuid4().hex
        rel_dir = Path("vehicles") / str(vehicle_id) / category
        abs_dir = self.root / rel_dir
        abs_dir.mkdir(parents=True, exist_ok=True)

        rel_path = rel_dir / f"{file_uuid}{ext}"
        abs_path = self.root / rel_path

        try:
            abs_path.write_bytes(file_bytes)
        except Exception as e:
            raise StorageError(f"Failed to write file to disk: {e}")

        sha256 = hashlib.sha256(file_bytes).hexdigest()
        from io import BytesIO
        img = Image.open(BytesIO(file_bytes))
        width, height = img.size

        return str(rel_path).replace("\\", "/"), sha256, width, height, len(file_bytes)

    def save_annotated_image(self, analysis_num: str, image_rgb: np.ndarray) -> str:
        """Saves annotated image array to PNG under storage/analyses/."""
        from io import BytesIO
        import numpy as np

        file_uuid = uuid.uuid4().hex
        rel_dir = Path("analyses") / analysis_num
        abs_dir = self.root / rel_dir
        abs_dir.mkdir(parents=True, exist_ok=True)

        rel_path = rel_dir / f"annotated_{file_uuid}.png"
        abs_path = self.root / rel_path

        try:
            img = Image.fromarray(image_rgb)
            img.save(abs_path, format="PNG")
        except Exception as e:
            raise StorageError(f"Failed to save annotated image: {e}")

        return str(rel_path).replace("\\", "/")

    def get_absolute_path(self, relative_path: str) -> Path:
        return self.root / Path(relative_path)

    def delete_file(self, relative_path: str) -> None:
        """Delete one explicitly identified storage file after a failed transaction."""
        root = self.root.resolve()
        target = (root / Path(relative_path)).resolve()
        if target == root or root not in target.parents:
            raise StorageError("Refusing to delete a file outside application storage.")
        if target.is_file():
            try:
                target.unlink()
            except Exception as exc:
                raise StorageError(f"Failed to remove incomplete upload: {exc}") from exc
