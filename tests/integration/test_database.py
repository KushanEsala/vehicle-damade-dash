import uuid
import pytest
from database.connection import get_db_session
from services.customer_service import CustomerService
from services.vehicle_service import VehicleService
from services.authentication_service import AuthenticationService


def test_customer_and_vehicle_flow():
    unique_reg = f"TST-{uuid.uuid4().hex[:6].upper()}"
    unique_email = f"customer_{uuid.uuid4().hex[:6]}@example.com"
    with get_db_session() as session:
        auth = AuthenticationService(session)
        admin = auth.user_repo.get_by_username_or_email("admin")
        assert admin is not None

        c_service = CustomerService(session)
        customer, _ = c_service.create_customer(
            full_name="Test Customer",
            phone_primary="+94 77 000 0000",
            email=unique_email,
            address_line_1="123 Test Street",
            city="Colombo",
            operator_user_id=admin.id,
        )
        assert customer.customer_code.startswith("CUS-")

        v_service = VehicleService(session)
        vehicle = v_service.register_vehicle(
            customer_id=customer.id,
            registration_number=unique_reg,
            make="Honda",
            model="Civic",
            colour="Black",
            operator_user_id=admin.id,
        )
        assert vehicle.vehicle_code.startswith("VEH-")
        assert vehicle.registration_number == unique_reg
