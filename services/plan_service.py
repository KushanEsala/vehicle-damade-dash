from __future__ import annotations

from decimal import Decimal
from sqlalchemy.orm import Session
from core.exceptions import ResourceNotFoundError, ValidationError
from database.repositories.plan_repository import PlanRepository
from database.repositories.audit_repository import AuditRepository
from database.models.plan import InsurancePlan


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
    ) -> InsurancePlan:
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
            is_active=True,
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
