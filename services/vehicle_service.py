from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from core.exceptions import DuplicateResourceError, ResourceNotFoundError, ValidationError
from database.repositories.vehicle_repository import VehicleRepository
from database.repositories.customer_repository import CustomerRepository
from database.repositories.plan_repository import PlanRepository
from database.repositories.audit_repository import AuditRepository
from database.models.vehicle import Vehicle, VehicleImage
from database.models.plan import VehiclePolicy
from services.storage_service import StorageService


class VehicleService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.vehicle_repo = VehicleRepository(session)
        self.customer_repo = CustomerRepository(session)
        self.plan_repo = PlanRepository(session)
        self.audit_repo = AuditRepository(session)
        self.storage = StorageService()

    def generate_vehicle_code(self) -> str:
        year = datetime.now(timezone.utc).year
        count = len(self.vehicle_repo.list_all()) + 1
        return f"VEH-{year}-{count:06d}"

    def register_vehicle(
        self,
        customer_id: int,
        registration_number: str,
        make: str,
        model: str,
        colour: str,
        operator_user_id: int,
        chassis_number: str | None = None,
        engine_number: str | None = None,
        manufactured_year: int | None = None,
        vehicle_type: str = "Car",
        fuel_type: str | None = None,
        odometer_km: int | None = None,
        plan_id: int | None = None,
        policy_number: str | None = None,
    ) -> Vehicle:
        reg = registration_number.strip().upper()
        if not reg or not make.strip() or not model.strip() or not colour.strip():
            raise ValidationError("Registration number, make, model, and colour are required.")

        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise ResourceNotFoundError(f"Customer #{customer_id} not found.")

        existing = self.vehicle_repo.get_by_registration(reg)
        if existing:
            raise DuplicateResourceError(f"Vehicle with registration '{reg}' already exists.")

        code = self.generate_vehicle_code()
        vehicle = Vehicle(
            customer_id=customer_id,
            vehicle_code=code,
            registration_number=reg,
            chassis_number=chassis_number.strip().upper() if chassis_number else None,
            engine_number=engine_number.strip() if engine_number else None,
            make=make.strip(),
            model=model.strip(),
            manufactured_year=manufactured_year,
            colour=colour.strip(),
            vehicle_type=vehicle_type,
            fuel_type=fuel_type,
            odometer_km=odometer_km,
            status="active",
            created_by=operator_user_id,
        )
        self.vehicle_repo.save(vehicle)

        # Policy creation if plan_id is provided
        if plan_id:
            plan = self.plan_repo.get_plan_by_id(plan_id)
            if plan:
                p_num = policy_number.strip() if policy_number else f"POL-{reg}"
                today = datetime.now(timezone.utc).date()
                policy = VehiclePolicy(
                    vehicle_id=vehicle.id,
                    plan_id=plan.id,
                    policy_number=p_num,
                    start_date=today,
                    end_date=today.replace(year=today.year + 1),
                    premium_amount=plan.deductible_amount,
                    status="active",
                    created_by=operator_user_id,
                )
                self.plan_repo.save_policy(policy)

        self.audit_repo.log_event(
            action="register_vehicle",
            entity_type="vehicle",
            user_id=operator_user_id,
            entity_id=vehicle.id,
            new_values={"registration": reg, "make": make, "model": model},
        )

        return vehicle

    def upload_vehicle_image(
        self,
        vehicle_id: int,
        file_bytes: bytes,
        filename: str,
        operator_user_id: int,
        category: str = "profile",
        is_primary: bool = False,
    ) -> VehicleImage:
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise ResourceNotFoundError(f"Vehicle #{vehicle_id} not found.")

        rel_path, sha256, width, height, file_size = self.storage.save_vehicle_image(
            vehicle_id=vehicle_id,
            file_bytes=file_bytes,
            original_filename=filename,
            category=category,
        )

        img = VehicleImage(
            vehicle_id=vehicle_id,
            image_category=category,
            original_filename=filename,
            storage_path=rel_path,
            mime_type="image/jpeg",
            file_size_bytes=file_size,
            width_px=width,
            height_px=height,
            sha256=sha256,
            is_primary=is_primary,
            uploaded_by=operator_user_id,
        )
        self.vehicle_repo.save_image(img)

        if is_primary or vehicle.primary_image_id is None:
            vehicle.primary_image_id = img.id
            self.vehicle_repo.save(vehicle)

        self.audit_repo.log_event(
            action="upload_vehicle_image",
            entity_type="vehicle_image",
            user_id=operator_user_id,
            entity_id=img.id,
            new_values={"filename": filename, "path": rel_path},
        )

        return img

    def get_vehicle_by_id(self, vehicle_id: int) -> Vehicle:
        v = self.vehicle_repo.get_by_id(vehicle_id)
        if not v:
            raise ResourceNotFoundError(f"Vehicle #{vehicle_id} not found.")
        return v

    def list_vehicles_by_customer(self, customer_id: int) -> list[Vehicle]:
        return self.vehicle_repo.list_by_customer(customer_id)

    def list_all_vehicles(self) -> list[Vehicle]:
        return self.vehicle_repo.list_all()
