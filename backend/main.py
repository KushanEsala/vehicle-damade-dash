from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Cookie, Depends, FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session, joinedload

from backend.auth import (
    COOKIE_NAME,
    clear_session,
    create_session,
    current_user,
    db_dependency,
    require_roles,
)
from backend.schemas import (
    ChangePasswordRequest,
    CompanyUpdate,
    CustomerCreate,
    DamageUpdate,
    FinalizeRequest,
    LoginRequest,
    OverrideRequest,
    ReanalyzeRequest,
    PlanCreate,
    PlanUpdate,
    StaffUserCreate,
    UserStatusUpdate,
    VehicleCreate,
)
from core.exceptions import ERPBaseException, NonVehicleImageError
from database.connection import engine, ensure_database_ready
from database.models.analysis import Analysis, AnalysisDamage
from database.models.company import CompanyInformation
from database.models.customer import Customer
from database.models.plan import InsurancePlan
from database.models.report import Report
from database.models.user import User
from database.models.vehicle import Vehicle
from services.analysis_service import AnalysisService
from services.authentication_service import AuthenticationService
from services.customer_service import CustomerService
from services.dashboard_service import DashboardService
from services.plan_service import PlanService
from services.report_service import ReportService
from services.vehicle_service import VehicleService
from services.user_service import UserService


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_database_ready()
    yield


app = FastAPI(
    title="Vehicle Insurance ERP API",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ERPBaseException)
async def erp_error_handler(_, exc: ERPBaseException):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=400, content={"detail": str(exc)})


def user_payload(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.code,
        "customer_id": user.customer_id,
        "must_change_password": user.must_change_password,
    }


def vehicle_payload(vehicle: Vehicle) -> dict[str, Any]:
    return {
        "id": vehicle.id,
        "customer_id": vehicle.customer_id,
        "vehicle_code": vehicle.vehicle_code,
        "registration_number": vehicle.registration_number,
        "make": vehicle.make,
        "model": vehicle.model,
        "manufactured_year": vehicle.manufactured_year,
        "colour": vehicle.colour,
        "vehicle_type": vehicle.vehicle_type,
        "status": vehicle.status,
        "image_url": f"/api/vehicles/{vehicle.id}/image" if vehicle.images else None,
    }


def analysis_payload(analysis: Analysis, customer_view: bool = False) -> dict[str, Any]:
    damages = []
    for damage in analysis.damages:
        if not damage.passed_vehicle_gate or damage.review_status not in {"accepted", "corrected"}:
            continue
        item = {
            "id": damage.id,
            "damage_class": damage.final_damage_class,
            "vehicle_part": damage.vehicle_part,
            "severity": damage.severity,
            "confidence": float(damage.confidence) if damage.confidence is not None else None,
            "description": damage.description,
            "estimated_cost": float(damage.estimated_cost),
            "review_status": damage.review_status,
        }
        if not customer_view:
            item["internal_note"] = damage.internal_note
        damages.append(item)
    return {
        "id": analysis.id,
        "analysis_number": analysis.analysis_number,
        "vehicle_id": analysis.vehicle_id,
        "registration_number": analysis.vehicle.registration_number if analysis.vehicle else None,
        "vehicle_name": f"{analysis.vehicle.make} {analysis.vehicle.model}" if analysis.vehicle else None,
        "status": analysis.status,
        "vehicle_confirmed": analysis.vehicle_confirmed,
        "damage_confidence": float(analysis.damage_confidence),
        "vehicle_confidence": float(analysis.vehicle_confidence),
        "require_vehicle_confirmation": analysis.require_vehicle_confirmation,
        "accepted_damage_count": analysis.accepted_damage_count,
        "currency_code": analysis.currency_code,
        "subtotal_cost": float(analysis.subtotal_cost),
        "tax_amount": float(analysis.tax_amount),
        "total_estimated_cost": float(analysis.total_estimated_cost),
        "analyzed_at": analysis.analyzed_at,
        "finalized_at": analysis.finalized_at,
        "annotated_image_url": f"/api/analyses/{analysis.id}/annotated-image" if analysis.annotated_image_path else None,
        "damages": damages,
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "database": engine.url.get_backend_name()}


@app.post("/api/auth/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(db_dependency)):
    user = AuthenticationService(db).authenticate(payload.identifier.strip(), payload.password)
    if user.role.code == "customer" and not user.customer_id:
        raise HTTPException(status_code=403, detail="Customer account is not linked.")
    create_session(db, user, response)
    return {"user": user_payload(user)}


@app.post("/api/auth/logout", status_code=204)
def logout(
    response: Response,
    session_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
    db: Session = Depends(db_dependency),
):
    clear_session(db, response, session_token)
    response.status_code = 204
    return response


@app.get("/api/auth/session")
def session(user: User = Depends(current_user)):
    return {"user": user_payload(user)}


@app.post("/api/auth/change-password", status_code=204)
def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(current_user),
    db: Session = Depends(db_dependency),
):
    AuthenticationService(db).change_password(user.id, payload.current_password, payload.new_password)
    return Response(status_code=204)


@app.get("/api/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(db_dependency)):
    service = DashboardService(db)
    if user.role.code == "admin":
        return {"role": "admin", **service.get_admin_metrics()}
    if user.role.code == "customer":
        return {"role": "customer", **service.get_customer_portal_metrics(user.customer_id)}
    return {
        "role": "operator",
        "total_customers": db.query(Customer).count(),
        "total_vehicles": db.query(Vehicle).count(),
        "total_analyses": db.query(Analysis).count(),
        "open_analyses": db.query(Analysis).filter(Analysis.status != "finalized").count(),
    }


@app.get("/api/customers")
def list_customers(
    _: User = Depends(require_roles("admin", "operator")),
    db: Session = Depends(db_dependency),
):
    return [
        {
            "id": customer.id,
            "customer_code": customer.customer_code,
            "full_name": customer.full_name,
            "phone_primary": customer.phone_primary,
            "email": customer.email,
            "city": customer.city,
            "status": customer.status,
            "portal_account": bool(customer.user_account),
        }
        for customer in CustomerService(db).list_customers()
    ]


@app.post("/api/customers", status_code=201)
def create_customer(
    payload: CustomerCreate,
    user: User = Depends(require_roles("admin", "operator")),
    db: Session = Depends(db_dependency),
):
    customer, password = CustomerService(db).create_customer(
        full_name=payload.full_name,
        phone_primary=payload.phone_primary,
        email=str(payload.email),
        address_line_1=payload.address_line_1,
        city=payload.city,
        operator_user_id=user.id,
        nic_or_passport=payload.nic_or_passport,
        phone_secondary=payload.phone_secondary,
        address_line_2=payload.address_line_2,
        postal_code=payload.postal_code,
        notes=payload.notes,
        create_user_account=payload.create_portal_account,
    )
    account = customer.user_account
    return {
        "id": customer.id,
        "customer_code": customer.customer_code,
        "username": account.username if account else None,
        "temporary_password": password,
    }


@app.get("/api/vehicles")
def list_vehicles(user: User = Depends(current_user), db: Session = Depends(db_dependency)):
    service = VehicleService(db)
    vehicles = (
        service.list_vehicles_by_customer(user.customer_id)
        if user.role.code == "customer"
        else service.list_all_vehicles()
    )
    return [vehicle_payload(vehicle) for vehicle in vehicles]


@app.post("/api/vehicles", status_code=201)
def create_vehicle(
    payload: VehicleCreate,
    user: User = Depends(require_roles("admin", "operator")),
    db: Session = Depends(db_dependency),
):
    vehicle = VehicleService(db).register_vehicle(
        **payload.model_dump(),
        operator_user_id=user.id,
    )
    return vehicle_payload(vehicle)


def owned_vehicle(db: Session, user: User, vehicle_id: int) -> Vehicle:
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle or (user.role.code == "customer" and vehicle.customer_id != user.customer_id):
        raise HTTPException(status_code=404, detail="Vehicle not found.")
    return vehicle


@app.get("/api/vehicles/{vehicle_id}/image")
def vehicle_image(
    vehicle_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(db_dependency),
):
    vehicle = owned_vehicle(db, user, vehicle_id)
    image = next((item for item in vehicle.images if item.is_primary), None) or (vehicle.images[0] if vehicle.images else None)
    if not image:
        raise HTTPException(status_code=404, detail="Vehicle image not found.")
    path = VehicleService(db).storage.get_absolute_path(image.storage_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Vehicle image not found.")
    return FileResponse(path, media_type=image.mime_type)


@app.post("/api/analyses", status_code=201)
async def create_analysis(
    vehicle_id: int = Form(...),
    damage_confidence: float = Form(0.30),
    vehicle_confidence: float = Form(0.25),
    require_vehicle: bool = Form(True),
    image: UploadFile = File(...),
    user: User = Depends(require_roles("admin", "operator")),
    db: Session = Depends(db_dependency),
):
    content = await image.read()
    vehicle = owned_vehicle(db, user, vehicle_id)
    vehicle_service = VehicleService(db)
    vehicle_image = vehicle_service.upload_vehicle_image(
        vehicle_id=vehicle.id,
        file_bytes=content,
        filename=image.filename or "inspection.jpg",
        operator_user_id=user.id,
        category="damage",
    )
    uploaded_storage_path = vehicle_image.storage_path
    try:
        analysis = AnalysisService(db).run_new_analysis(
            vehicle_id=vehicle.id,
            source_image_id=vehicle_image.id,
            operator_user_id=user.id,
            image_bytes=content,
            damage_confidence=damage_confidence,
            vehicle_confidence=vehicle_confidence,
            require_vehicle_confirmation=require_vehicle,
        )
    except NonVehicleImageError as exc:
        # A valid upload that is not a vehicle is an expected assessment
        # outcome, not a malformed HTTP request. Roll back the pending image
        # record, remove its file, and return a normal response the UI can show
        # without producing a browser-level 400 error.
        db.rollback()
        vehicle_service.storage.delete_file(uploaded_storage_path)
        return JSONResponse(
            status_code=200,
            content={"accepted": False, "message": str(exc)},
        )
    except Exception:
        # The database transaction is rolled back by the request dependency.
        # Remove the newly written file as well so rejected non-vehicle uploads
        # do not remain in vehicle storage.
        vehicle_service.storage.delete_file(uploaded_storage_path)
        raise
    return analysis_payload(analysis)


@app.get("/api/analyses")
def list_analyses(user: User = Depends(current_user), db: Session = Depends(db_dependency)):
    query = db.query(Analysis).options(joinedload(Analysis.vehicle), joinedload(Analysis.damages))
    if user.role.code == "customer":
        query = query.join(Analysis.vehicle).filter(
            Vehicle.customer_id == user.customer_id,
            Analysis.status == "finalized",
        )
    return [analysis_payload(item, user.role.code == "customer") for item in query.order_by(Analysis.created_at.desc()).all()]


def owned_analysis(db: Session, user: User, analysis_id: int) -> Analysis:
    analysis = (
        db.query(Analysis)
        .options(joinedload(Analysis.vehicle), joinedload(Analysis.damages))
        .filter(Analysis.id == analysis_id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    if user.role.code == "customer" and (
        analysis.vehicle.customer_id != user.customer_id or analysis.status != "finalized"
    ):
        raise HTTPException(status_code=404, detail="Assessment not found.")
    return analysis


@app.get("/api/analyses/{analysis_id}")
def get_analysis(
    analysis_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(db_dependency),
):
    return analysis_payload(owned_analysis(db, user, analysis_id), user.role.code == "customer")


@app.get("/api/analyses/{analysis_id}/annotated-image")
def annotated_image(
    analysis_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(db_dependency),
):
    analysis = owned_analysis(db, user, analysis_id)
    if not analysis.annotated_image_path:
        raise HTTPException(status_code=404, detail="Annotated image not found.")
    path = AnalysisService(db).storage.get_absolute_path(analysis.annotated_image_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Annotated image not found.")
    return FileResponse(path, media_type="image/png")


@app.patch("/api/analyses/{analysis_id}/damages/{damage_id}")
def update_damage(
    analysis_id: int,
    damage_id: int,
    payload: DamageUpdate,
    user: User = Depends(require_roles("admin", "operator")),
    db: Session = Depends(db_dependency),
):
    analysis = owned_analysis(db, user, analysis_id)
    damage = db.query(AnalysisDamage).filter(AnalysisDamage.id == damage_id, AnalysisDamage.analysis_id == analysis.id).first()
    if not damage:
        raise HTTPException(status_code=404, detail="Damage item not found.")
    updated = AnalysisService(db).update_damage_item(
        damage_id=damage.id,
        operator_user_id=user.id,
        final_class=payload.final_class,
        severity=payload.severity,
        estimated_cost=payload.estimated_cost,
        vehicle_part=payload.vehicle_part,
        description=payload.description,
        internal_note=payload.internal_note,
    )
    return {"id": updated.id, "updated": True}


@app.delete("/api/analyses/{analysis_id}/damages/{damage_id}", status_code=204)
def delete_damage(
    analysis_id: int,
    damage_id: int,
    user: User = Depends(require_roles("admin", "operator")),
    db: Session = Depends(db_dependency),
):
    owned_analysis(db, user, analysis_id)
    AnalysisService(db).delete_damage_item(analysis_id, damage_id, user.id)
    return Response(status_code=204)


@app.post("/api/analyses/{analysis_id}/vehicle-override")
def override_vehicle(
    analysis_id: int,
    payload: OverrideRequest,
    user: User = Depends(require_roles("admin", "operator")),
    db: Session = Depends(db_dependency),
):
    analysis = AnalysisService(db).override_vehicle_confirmation(analysis_id, user.id, payload.reason)
    return analysis_payload(analysis)


@app.post("/api/analyses/{analysis_id}/reanalyze", status_code=201)
def reanalyze_assessment(
    analysis_id: int,
    payload: ReanalyzeRequest,
    user: User = Depends(require_roles("admin", "operator")),
    db: Session = Depends(db_dependency),
):
    owned_analysis(db, user, analysis_id)
    replacement = AnalysisService(db).reanalyze(
        analysis_id,
        user.id,
        damage_confidence=payload.damage_confidence,
        vehicle_confidence=payload.vehicle_confidence,
        require_vehicle=payload.require_vehicle,
        reason=payload.reason,
    )
    return analysis_payload(replacement)


@app.post("/api/analyses/{analysis_id}/finalize")
def finalize_analysis(
    analysis_id: int,
    payload: FinalizeRequest,
    user: User = Depends(require_roles("admin", "operator")),
    db: Session = Depends(db_dependency),
):
    service = AnalysisService(db)
    analysis = service.finalize_analysis(analysis_id, user.id, payload.notes)
    report = ReportService(db).generate_pdf_report(analysis.id, user.id)
    return {"analysis": analysis_payload(analysis), "report_id": report.id}


@app.get("/api/reports")
def list_reports(user: User = Depends(current_user), db: Session = Depends(db_dependency)):
    service = ReportService(db)
    reports = service.list_for_customer(user.customer_id) if user.role.code == "customer" else service.list_all()
    return {
        "scope": "company" if user.role.code == "admin" else ("assigned_operations" if user.role.code == "operator" else "customer"),
        "reports": [{
            "id": report.id,
            "report_number": report.report_number,
            "analysis_number": report.analysis.analysis_number,
            "registration_number": report.analysis.vehicle.registration_number,
            "generated_at": report.generated_at,
            "total_estimated_cost": float(report.analysis.total_estimated_cost),
            "currency_code": report.analysis.currency_code,
            "customer_name": report.analysis.vehicle.customer.full_name if user.role.code != "customer" else None,
        }
        for report in reports if report.is_current],
    }


@app.get("/api/reports/{report_id}")
def report_detail(
    report_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(db_dependency),
):
    service = ReportService(db)
    report = service.get_authorized_report(report_id, role_code=user.role.code, customer_id=user.customer_id)
    snapshot = report.snapshot_json
    return {
        "id": report.id,
        "report_number": report.report_number,
        "analysis_number": report.analysis.analysis_number,
        "generated_at": report.generated_at,
        "role_scope": user.role.code,
        "customer": snapshot.get("customer", {}),
        "vehicle": snapshot.get("vehicle", {}),
        "damages": snapshot.get("damages", []),
        "totals": snapshot.get("totals", {}),
        "currency_code": snapshot.get("currency_code", "LKR"),
        "annotated_image_url": (
            f"/api/analyses/{report.analysis_id}/annotated-image"
            if report.analysis.annotated_image_path else None
        ),
        "pdf_view_url": f"/api/reports/{report.id}/pdf",
        "pdf_download_url": f"/api/reports/{report.id}/download",
    }


@app.get("/api/reports/{report_id}/pdf")
def report_pdf(
    report_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(db_dependency),
):
    service = ReportService(db)
    report = service.get_authorized_report(report_id, role_code=user.role.code, customer_id=user.customer_id)
    report = service.ensure_current_pdf_layout(report)
    path = service.storage.get_absolute_path(report.pdf_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Report file not found.")
    return FileResponse(
        path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{report.report_number}.pdf"'},
    )


@app.get("/api/reports/{report_id}/download")
def download_report_pdf(
    report_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(db_dependency),
):
    service = ReportService(db)
    report = service.get_authorized_report(report_id, role_code=user.role.code, customer_id=user.customer_id)
    report = service.ensure_current_pdf_layout(report)
    path = service.storage.get_absolute_path(report.pdf_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Report file not found.")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"{report.report_number}.pdf",
    )


@app.get("/api/plans")
def list_plans(
    _: User = Depends(require_roles("admin", "operator")),
    db: Session = Depends(db_dependency),
):
    return [
        {
            "id": plan.id,
            "plan_code": plan.plan_code,
            "name": plan.name,
            "description": plan.description,
            "deductible_amount": float(plan.deductible_amount),
            "coverage_limit": float(plan.coverage_limit) if plan.coverage_limit else None,
            "currency_code": plan.currency_code,
            "is_active": plan.is_active,
        }
        for plan in PlanService(db).list_all_plans()
    ]


@app.post("/api/plans", status_code=201)
def create_plan(
    payload: PlanCreate,
    user: User = Depends(require_roles("admin")),
    db: Session = Depends(db_dependency),
):
    plan = PlanService(db).create_plan(**payload.model_dump(), admin_user_id=user.id)
    return {"id": plan.id, "plan_code": plan.plan_code, "name": plan.name}


@app.patch("/api/plans/{plan_id}")
def update_plan(
    plan_id: int,
    payload: PlanUpdate,
    user: User = Depends(require_roles("admin")),
    db: Session = Depends(db_dependency),
):
    plan = PlanService(db).update_plan(plan_id, **payload.model_dump(), admin_user_id=user.id)
    return {
        "id": plan.id,
        "plan_code": plan.plan_code,
        "name": plan.name,
        "description": plan.description,
        "deductible_amount": float(plan.deductible_amount),
        "coverage_limit": float(plan.coverage_limit) if plan.coverage_limit is not None else None,
        "currency_code": plan.currency_code,
        "is_active": plan.is_active,
    }


@app.delete("/api/plans/{plan_id}", status_code=204)
def delete_plan(
    plan_id: int,
    user: User = Depends(require_roles("admin")),
    db: Session = Depends(db_dependency),
):
    PlanService(db).delete_plan(plan_id, user.id)
    return Response(status_code=204)


@app.get("/api/company")
def company(_: User = Depends(current_user), db: Session = Depends(db_dependency)):
    item = db.query(CompanyInformation).first()
    if not item:
        raise HTTPException(status_code=404, detail="Company information unavailable.")
    return {
        "company_name": item.company_name,
        "registration_number": item.registration_number,
        "address_line_1": item.address_line_1,
        "address_line_2": item.address_line_2,
        "city": item.city,
        "address": ", ".join(filter(None, [item.address_line_1, item.address_line_2, item.city])),
        "phone": item.phone,
        "email": item.email,
        "website": item.website,
        "currency_code": item.currency_code,
        "tax_label": item.tax_label,
        "tax_rate": float(item.tax_rate),
        "report_footer": item.report_footer,
    }


@app.patch("/api/company")
def update_company(
    payload: CompanyUpdate,
    admin: User = Depends(require_roles("admin")),
    db: Session = Depends(db_dependency),
):
    item = db.query(CompanyInformation).first()
    if not item:
        item = CompanyInformation()
        db.add(item)
    for field, value in payload.model_dump().items():
        setattr(item, field, value)
    item.currency_code = item.currency_code.upper()
    item.updated_by = admin.id
    db.flush()
    return {
        "company_name": item.company_name,
        "registration_number": item.registration_number,
        "address_line_1": item.address_line_1,
        "address_line_2": item.address_line_2,
        "city": item.city,
        "phone": item.phone,
        "email": item.email,
        "website": item.website,
        "currency_code": item.currency_code,
        "tax_label": item.tax_label,
        "tax_rate": float(item.tax_rate),
        "report_footer": item.report_footer,
    }


@app.get("/api/users")
def list_users(_: User = Depends(require_roles("admin")), db: Session = Depends(db_dependency)):
    return [
        {
            "id": item.id,
            "username": item.username,
            "email": item.email,
            "role": item.role.code,
            "is_active": item.is_active,
            "customer_id": item.customer_id,
        }
        for item in UserService(db).list_all_users()
    ]


@app.post("/api/users", status_code=201)
def create_staff_user(
    payload: StaffUserCreate,
    admin: User = Depends(require_roles("admin")),
    db: Session = Depends(db_dependency),
):
    if payload.role_code not in {"admin", "operator"}:
        raise HTTPException(status_code=422, detail="Staff role must be admin or operator.")
    item, temporary_password = UserService(db).create_staff_user(
        username=payload.username,
        email=str(payload.email),
        role_code=payload.role_code,
        admin_user_id=admin.id,
    )
    return {"id": item.id, "username": item.username, "temporary_password": temporary_password}


@app.patch("/api/users/{user_id}/status")
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    admin: User = Depends(require_roles("admin")),
    db: Session = Depends(db_dependency),
):
    item = UserService(db).update_active_status(user_id, payload.is_active, admin.id)
    return {"id": item.id, "username": item.username, "is_active": item.is_active}


@app.delete("/api/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    admin: User = Depends(require_roles("admin")),
    db: Session = Depends(db_dependency),
):
    UserService(db).delete_user(user_id, admin.id)
    return Response(status_code=204)
