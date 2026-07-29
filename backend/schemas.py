from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=255)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class CustomerCreate(BaseModel):
    full_name: str
    phone_primary: str
    email: EmailStr
    address_line_1: str
    city: str
    nic_or_passport: str | None = None
    phone_secondary: str | None = None
    address_line_2: str | None = None
    postal_code: str | None = None
    notes: str | None = None
    create_portal_account: bool = True


class VehicleCreate(BaseModel):
    customer_id: int
    registration_number: str
    make: str
    model: str
    colour: str
    chassis_number: str | None = None
    engine_number: str | None = None
    manufactured_year: int | None = None
    vehicle_type: str = "Car"
    fuel_type: str | None = None
    odometer_km: int | None = None
    plan_id: int | None = None
    policy_number: str | None = None


class DamageUpdate(BaseModel):
    final_class: str
    severity: str
    estimated_cost: float = Field(ge=0)
    vehicle_part: str | None = None
    description: str | None = None
    internal_note: str | None = None


class FinalizeRequest(BaseModel):
    notes: str | None = None


class OverrideRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


class ReanalyzeRequest(BaseModel):
    damage_confidence: float = Field(ge=0.05, le=0.95)
    vehicle_confidence: float = Field(ge=0.05, le=0.95)
    require_vehicle: bool = True
    reason: str = Field(default="Confidence thresholds adjusted before finalization.", min_length=5, max_length=500)


class PlanCreate(BaseModel):
    plan_code: str
    name: str
    description: str
    deductible_amount: float = Field(ge=0)
    coverage_limit: float | None = Field(default=None, ge=0)
    currency_code: str = "LKR"
    is_active: bool = True


class PlanUpdate(PlanCreate):
    is_active: bool = True


class StaffUserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    role_code: str


class UserStatusUpdate(BaseModel):
    is_active: bool


class CompanyUpdate(BaseModel):
    company_name: str = Field(min_length=2, max_length=200)
    registration_number: str = Field(min_length=1, max_length=100)
    address_line_1: str = Field(min_length=1, max_length=255)
    address_line_2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=3, max_length=40)
    email: EmailStr
    website: str | None = Field(default=None, max_length=255)
    currency_code: str = Field(min_length=3, max_length=3)
    tax_label: str = Field(min_length=1, max_length=30)
    tax_rate: float = Field(ge=0, le=1)
    report_footer: str | None = Field(default=None, max_length=2000)
