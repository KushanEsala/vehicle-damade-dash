from __future__ import annotations

import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.exceptions import ConfigurationError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = Field(default="development")
    APP_NAME: str = Field(default="Vehicle Damage Insurance ERP")
    APP_BASE_URL: str = Field(default="http://localhost:8501")
    SESSION_TIMEOUT_MINUTES: int = Field(default=30)
    MAX_FAILED_LOGIN_ATTEMPTS: int = Field(default=5)
    LOCKOUT_DURATION_MINUTES: int = Field(default=15)

    MYSQL_HOST: str = Field(default="127.0.0.1")
    MYSQL_PORT: int = Field(default=3306)
    MYSQL_DATABASE: str = Field(default="Vehicle_Analyzis")
    MYSQL_USER: str = Field(default="vehicle_erp_app")
    MYSQL_PASSWORD: str = Field(default="vehicle_erp_secret")

    STORAGE_ROOT: str = Field(default="storage")
    DAMAGE_MODEL_PATH: str = Field(default="Runscomplete/runs/vehicle_damage_seg-2/weights/best.pt")
    VEHICLE_MODEL_PATH: str = Field(default="yolov8n.pt")

    DEFAULT_DAMAGE_CONFIDENCE: float = Field(default=0.30)
    DEFAULT_VEHICLE_CONFIDENCE: float = Field(default=0.25)
    DEFAULT_REQUIRE_VEHICLE: bool = Field(default=True)
    DEFAULT_CURRENCY: str = Field(default="LKR")

    LOG_LEVEL: str = Field(default="INFO")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
        )

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def storage_path(self) -> Path:
        p = Path(self.STORAGE_ROOT)
        if not p.is_absolute():
            p = self.project_root / p
        return p

    @property
    def damage_model_abs_path(self) -> Path:
        p = Path(self.DAMAGE_MODEL_PATH)
        if not p.is_absolute():
            p = self.project_root / p
        return p

    @property
    def vehicle_model_abs_path(self) -> Path:
        p = Path(self.VEHICLE_MODEL_PATH)
        if not p.is_absolute():
            p = self.project_root / p
        return p

    def validate_paths(self) -> None:
        """Validates that storage directory and model files exist or can be created."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        if not self.damage_model_abs_path.is_file():
            raise ConfigurationError(f"Damage model file not found at: {self.damage_model_abs_path}")
        if not self.vehicle_model_abs_path.is_file():
            raise ConfigurationError(f"Vehicle model file not found at: {self.vehicle_model_abs_path}")


_settings_instance: Settings | None = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
