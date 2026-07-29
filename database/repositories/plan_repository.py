from __future__ import annotations

from sqlalchemy.orm import Session
from database.models.plan import InsurancePlan, VehiclePolicy


class PlanRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_active_plans(self) -> list[InsurancePlan]:
        return (
            self.session.query(InsurancePlan)
            .filter(InsurancePlan.is_active == True)
            .order_by(InsurancePlan.name)
            .all()
        )

    def get_plan_by_id(self, plan_id: int) -> InsurancePlan | None:
        return self.session.query(InsurancePlan).filter(InsurancePlan.id == plan_id).first()

    def save_plan(self, plan: InsurancePlan) -> InsurancePlan:
        self.session.add(plan)
        self.session.flush()
        return plan

    def save_policy(self, policy: VehiclePolicy) -> VehiclePolicy:
        self.session.add(policy)
        self.session.flush()
        return policy

    def get_active_policy_for_vehicle(self, vehicle_id: int) -> VehiclePolicy | None:
        return (
            self.session.query(VehiclePolicy)
            .filter(VehiclePolicy.vehicle_id == vehicle_id, VehiclePolicy.status == "active")
            .order_by(VehiclePolicy.end_date.desc())
            .first()
        )
