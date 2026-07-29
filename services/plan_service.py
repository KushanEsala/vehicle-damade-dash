from __future__ import annotations

from decimal import Decimal
from sqlalchemy.orm import Session
from core.exceptions import AuthorizationError, DuplicateResourceError, ResourceNotFoundError, ValidationError
from database.models.user import Role, User
from database.repositories.plan_repository import PlanRepository
from database.repositories.audit_repository import AuditRepository
from database.models.plan import InsurancePlan, VehiclePolicy


class PlanService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.plan_repo = PlanRepository(session)
        self.audit_repo = AuditRepository(session)

    def create_plan(
        self,
        plan_code: str,
        name: str,
        description: str,
        deductible_amount: Decimal | float | int,
        admin_user_id: int,
        coverage_limit: Decimal | float | int | None = None,
        currency_code: str = "LKR",
        is_active: bool = True,
    ) -> InsurancePlan:
        admin = (
            self.session.query(User)
            .join(User.role)
            .filter(User.id == admin_user_id, Role.code == "admin", User.is_active.is_(True))
            .first()
        )
        if not admin:
            raise AuthorizationError("Only an active administrator can create insurance plans.")
        plan_code = plan_code.strip().upper()
        if not plan_code or not name.strip() or not description.strip():
            raise ValidationError("Plan code, name, and description are required.")

        plan = InsurancePlan(
            plan_code=plan_code,
            name=name.strip(),
            description=description.strip(),
            coverage_limit=Decimal(str(coverage_limit)) if coverage_limit else None,
            deductible_amount=Decimal(str(deductible_amount)),
            currency_code=currency_code,
            is_active=is_active,
            created_by=admin_user_id,
        )
        self.plan_repo.save_plan(plan)

        self.audit_repo.log_event(
            action="create_insurance_plan",
            entity_type="insurance_plan",
            user_id=admin_user_id,
            entity_id=plan.id,
            new_values={"plan_code": plan_code, "name": name},
        )

        return plan

    def list_active_plans(self) -> list[InsurancePlan]:
        return self.plan_repo.list_active_plans()

    def list_all_plans(self) -> list[InsurancePlan]:
        return self.session.query(InsurancePlan).order_by(InsurancePlan.name).all()

    def update_plan(
        self,
        plan_id: int,
        *,
        plan_code: str,
        name: str,
        description: str,
        deductible_amount: Decimal | float | int,
        coverage_limit: Decimal | float | int | None,
        currency_code: str,
        is_active: bool,
        admin_user_id: int,
    ) -> InsurancePlan:
        plan = self.plan_repo.get_plan_by_id(plan_id)
        if not plan:
            raise ResourceNotFoundError(f"Insurance plan #{plan_id} not found.")
        normalized_code = plan_code.strip().upper()
        duplicate = (
            self.session.query(InsurancePlan)
            .filter(InsurancePlan.plan_code == normalized_code, InsurancePlan.id != plan_id)
            .first()
        )
        if duplicate:
            raise DuplicateResourceError(f"Plan code '{normalized_code}' already exists.")
        if not normalized_code or not name.strip() or not description.strip():
            raise ValidationError("Plan code, name, and description are required.")
        old_values = {"plan_code": plan.plan_code, "name": plan.name, "is_active": plan.is_active}
        plan.plan_code = normalized_code
        plan.name = name.strip()
        plan.description = description.strip()
        plan.deductible_amount = Decimal(str(deductible_amount))
        plan.coverage_limit = Decimal(str(coverage_limit)) if coverage_limit is not None else None
        plan.currency_code = currency_code.strip().upper()
        plan.is_active = is_active
        self.plan_repo.save_plan(plan)
        self.audit_repo.log_event(
            action="update_insurance_plan",
            entity_type="insurance_plan",
            user_id=admin_user_id,
            entity_id=plan.id,
            old_values=old_values,
            new_values={"plan_code": plan.plan_code, "name": plan.name, "is_active": plan.is_active},
        )
        return plan

    def delete_plan(self, plan_id: int, admin_user_id: int) -> None:
        plan = self.plan_repo.get_plan_by_id(plan_id)
        if not plan:
            raise ResourceNotFoundError(f"Insurance plan #{plan_id} not found.")
        if self.session.query(VehiclePolicy).filter(VehiclePolicy.plan_id == plan_id).count():
            raise ValidationError("This plan is assigned to vehicle policies. Deactivate it instead of deleting it.")
        self.audit_repo.log_event(
            action="delete_insurance_plan",
            entity_type="insurance_plan",
            user_id=admin_user_id,
            entity_id=plan.id,
            old_values={"plan_code": plan.plan_code, "name": plan.name},
        )
        self.session.delete(plan)
        self.session.flush()
