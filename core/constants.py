from __future__ import annotations

from enum import Enum


class RoleCode(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    CUSTOMER = "customer"


class AnalysisStatus(str, Enum):
    DRAFT = "draft"
    ANALYZED = "analyzed"
    UNDER_REVIEW = "under_review"
    FINALIZED = "finalized"
    SUPERSEDED = "superseded"


class ReviewStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CORRECTED = "corrected"


class SeverityLevel(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class CustomerStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class VehicleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SOLD = "sold"


class PolicyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


DAMAGE_CLASSES = [
    "scratch",
    "dent",
    "tear",
    "missing_part",
    "broken_lamp",
    "puncture",
    "broken_glass",
]

VEHICLE_CLASS_IDS = {2, 3, 5, 7}  # COCO IDs for car, motorcycle, bus, truck

CLASS_COLORS = {
    "scratch": (255, 188, 66),
    "dent": (70, 190, 255),
    "tear": (255, 99, 132),
    "missing_part": (176, 116, 255),
    "broken_lamp": (255, 224, 92),
    "puncture": (76, 220, 155),
    "broken_glass": (70, 225, 235),
}

EXPECTED_DAMAGE_MODEL_HASH = "c9d86e67a4c14f65047f33c17b4c4357613a0a15b52f919d76ff1c8542c0d541"
EXPECTED_VEHICLE_MODEL_HASH = "f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36"

ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

MAX_UPLOAD_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
