from __future__ import annotations

from decimal import Decimal
from typing import Any
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models.customer import Customer
from database.models.vehicle import Vehicle
from database.models.analysis import Analysis, AnalysisDamage
from database.models.report import Report


class DashboardService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_admin_metrics(self) -> dict[str, Any]:
        total_customers = self.session.query(func.count(Customer.id)).scalar() or 0
        total_vehicles = self.session.query(func.count(Vehicle.id)).scalar() or 0
        total_analyses = self.session.query(func.count(Analysis.id)).scalar() or 0
        finalized_analyses = (
            self.session.query(func.count(Analysis.id)).filter(Analysis.status == "finalized").scalar() or 0
        )
        total_estimated_cost = (
            self.session.query(func.sum(Analysis.total_estimated_cost)).filter(Analysis.status == "finalized").scalar()
            or Decimal("0.00")
        )
        damage_class_counts = (
            self.session.query(AnalysisDamage.final_damage_class, func.count(AnalysisDamage.id))
            .group_by(AnalysisDamage.final_damage_class)
            .all()
        )

        return {
            "total_customers": total_customers,
            "total_vehicles": total_vehicles,
            "total_analyses": total_analyses,
            "finalized_analyses": finalized_analyses,
            "total_estimated_cost": float(total_estimated_cost),
            "damage_class_counts": {cls_name: cnt for cls_name, cnt in damage_class_counts},
        }

    def get_customer_portal_metrics(self, customer_id: int) -> dict[str, Any]:
        vehicles = self.session.query(Vehicle).filter(Vehicle.customer_id == customer_id).all()
        v_ids = [v.id for v in vehicles]

        if not v_ids:
            return {
                "vehicle_count": 0,
                "reports_count": 0,
                "total_estimated_cost": 0.0,
                "vehicles": [],
            }

        reports_count = (
            self.session.query(func.count(Report.id))
            .join(Analysis, Report.analysis_id == Analysis.id)
            .filter(Analysis.vehicle_id.in_(v_ids), Report.is_current == True)
            .scalar()
            or 0
        )

        total_cost = (
            self.session.query(func.sum(Analysis.total_estimated_cost))
            .filter(Analysis.vehicle_id.in_(v_ids), Analysis.status == "finalized")
            .scalar()
            or Decimal("0.00")
        )

        return {
            "vehicle_count": len(vehicles),
            "reports_count": reports_count,
            "total_estimated_cost": float(total_cost),
        }
