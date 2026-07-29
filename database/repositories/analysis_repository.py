from __future__ import annotations

from sqlalchemy.orm import Session
from database.models.analysis import ModelVersion, Analysis, AnalysisVehicleDetection, AnalysisDamage, AnalysisRevision


class AnalysisRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, analysis_id: int) -> Analysis | None:
        return self.session.query(Analysis).filter(Analysis.id == analysis_id).first()

    def get_by_number(self, analysis_num: str) -> Analysis | None:
        return self.session.query(Analysis).filter(Analysis.analysis_number == analysis_num).first()

    def list_by_vehicle(self, vehicle_id: int) -> list[Analysis]:
        return (
            self.session.query(Analysis)
            .filter(Analysis.vehicle_id == vehicle_id)
            .order_by(Analysis.created_at.desc())
            .all()
        )

    def list_all(self) -> list[Analysis]:
        return self.session.query(Analysis).order_by(Analysis.created_at.desc()).all()

    def save_analysis(self, analysis: Analysis) -> Analysis:
        self.session.add(analysis)
        self.session.flush()
        return analysis

    def get_or_create_model_version(
        self,
        model_key: str,
        display_name: str,
        model_type: str,
        file_path: str,
        sha256: str,
        classes: list[str],
        framework: str,
        framework_version: str,
    ) -> ModelVersion:
        mv = self.session.query(ModelVersion).filter(ModelVersion.model_key == model_key).first()
        if not mv:
            mv = ModelVersion(
                model_key=model_key,
                display_name=display_name,
                model_type=model_type,
                file_path=file_path,
                sha256=sha256,
                classes_json=classes,
                framework=framework,
                framework_version=framework_version,
                is_active=True,
            )
            self.session.add(mv)
            self.session.flush()
        return mv
