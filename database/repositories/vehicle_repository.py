from __future__ import annotations

from sqlalchemy.orm import Session
from database.models.vehicle import Vehicle, VehicleImage


class VehicleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, vehicle_id: int) -> Vehicle | None:
        return self.session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    def get_by_registration(self, reg_num: str) -> Vehicle | None:
        reg = reg_num.strip().upper()
        return self.session.query(Vehicle).filter(Vehicle.registration_number == reg).first()

    def list_by_customer(self, customer_id: int) -> list[Vehicle]:
        return (
            self.session.query(Vehicle)
            .filter(Vehicle.customer_id == customer_id)
            .order_by(Vehicle.created_at.desc())
            .all()
        )

    def list_all(self) -> list[Vehicle]:
        return self.session.query(Vehicle).order_by(Vehicle.created_at.desc()).all()

    def save(self, vehicle: Vehicle) -> Vehicle:
        self.session.add(vehicle)
        self.session.flush()
        return vehicle

    def save_image(self, image: VehicleImage) -> VehicleImage:
        self.session.add(image)
        self.session.flush()
        return image
