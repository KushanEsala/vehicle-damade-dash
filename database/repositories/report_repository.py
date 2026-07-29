from __future__ import annotations

from sqlalchemy.orm import Session
from database.models.report import Report


class ReportRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, report_id: int) -> Report | None:
        return self.session.query(Report).filter(Report.id == report_id).first()

    def get_by_number(self, report_num: str) -> Report | None:
        return self.session.query(Report).filter(Report.report_number == report_num).first()

    def get_by_analysis_id(self, analysis_id: int) -> Report | None:
        return (
            self.session.query(Report)
            .filter(Report.analysis_id == analysis_id, Report.is_current == True)
            .first()
        )

    def list_all(self) -> list[Report]:
        return self.session.query(Report).order_by(Report.generated_at.desc()).all()

    def save(self, report: Report) -> Report:
        self.session.add(report)
        self.session.flush()
        return report
