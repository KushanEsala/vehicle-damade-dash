from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Generator
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session

from core.config import get_settings
from core.logging_config import logger
from database.base import Base

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)

# Verify MySQL connection on startup — no SQLite fallback.
with engine.connect() as _conn:
    pass
logger.info("Connected to MySQL database '%s' successfully.", settings.MYSQL_DATABASE)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def init_db() -> None:
    """Creates all database tables defined in ORM models."""
    # Import the model package before create_all so every table, including API
    # sessions, is registered with SQLAlchemy metadata.
    import database.models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def ensure_incremental_schema() -> None:
    """Apply small additive changes for existing local/MySQL installations."""
    inspector = inspect(engine)
    if "analysis_damages" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("analysis_damages")}
    if "model_polygon_json" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE analysis_damages ADD COLUMN model_polygon_json JSON NULL")
            )
    if "mask_refined" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE analysis_damages "
                    "ADD COLUMN mask_refined BOOLEAN NOT NULL DEFAULT FALSE"
                )
            )


def ensure_database_ready() -> None:
    """Ensures database tables are created and bootstrapped with initial seed data."""
    init_db()
    ensure_incremental_schema()
    with SessionLocal() as session:
        try:
            from database.models.user import Role, User
            from database.models.company import CompanyInformation
            from database.models.plan import InsurancePlan, VehiclePolicy
            from database.models.customer import Customer
            from database.models.vehicle import Vehicle
            from core.security import hash_password

            # ----- Seed Roles -----
            if session.query(Role).count() == 0:
                roles = [
                    Role(code="admin", name="System Administrator", description="Full access to ERP configuration, staff, and audit records."),
                    Role(code="operator", name="Claims Operator", description="Registers customers, vehicles, runs analyses, and adds costs."),
                    Role(code="customer", name="Policyholder Customer", description="Views owned vehicles, damage summaries, and downloads reports."),
                ]
                session.add_all(roles)
                session.commit()

            admin_role = session.query(Role).filter(Role.code == "admin").first()
            operator_role = session.query(Role).filter(Role.code == "operator").first()
            customer_role = session.query(Role).filter(Role.code == "customer").first()

            # ----- Seed Company -----
            if session.query(CompanyInformation).count() == 0:
                company = CompanyInformation(
                    company_name="Apex Vehicle Assurance Services",
                    registration_number="PV-10029384",
                    address_line_1="100 Commercial Drive",
                    address_line_2="Level 4, Apex Tower",
                    city="Colombo",
                    phone="+94 11 234 5678",
                    email="claims@apexinsurance.lk",
                    website="https://apexinsurance.lk",
                    currency_code="LKR",
                    tax_label="VAT",
                    tax_rate=0.1500,
                    report_footer="Official Vehicle Damage Assessment Report produced by Apex Insurance ERP. Advisory only.",
                )
                session.add(company)
                session.commit()

            # ----- Seed Insurance Plans -----
            if session.query(InsurancePlan).count() == 0:
                plans = [
                    InsurancePlan(
                        plan_code="PLN-COMP-GOLD",
                        name="Comprehensive Gold Auto Shield",
                        description="Full comprehensive accident, natural disaster, and third-party liability coverage.",
                        coverage_limit=Decimal("5000000.00"),
                        deductible_amount=Decimal("15000.00"),
                        currency_code="LKR",
                        is_active=True,
                    ),
                    InsurancePlan(
                        plan_code="PLN-COMP-SILVER",
                        name="Comprehensive Silver Shield",
                        description="Standard comprehensive coverage for accident and theft with moderate deductible.",
                        coverage_limit=Decimal("3000000.00"),
                        deductible_amount=Decimal("25000.00"),
                        currency_code="LKR",
                        is_active=True,
                    ),
                    InsurancePlan(
                        plan_code="PLN-THIRD-PARTY",
                        name="Third-Party Only",
                        description="Mandatory third-party bodily injury and property damage liability coverage.",
                        coverage_limit=Decimal("1000000.00"),
                        deductible_amount=Decimal("5000.00"),
                        currency_code="LKR",
                        is_active=True,
                    ),
                    InsurancePlan(
                        plan_code="PLN-COMP-PLAT",
                        name="Platinum Premium Cover",
                        description="Premium all-risk coverage including roadside assistance, zero depreciation, and rental car benefit.",
                        coverage_limit=Decimal("10000000.00"),
                        deductible_amount=Decimal("10000.00"),
                        currency_code="LKR",
                        is_active=True,
                    ),
                ]
                session.add_all(plans)
                session.commit()

            # ----- Seed Admin User -----
            if admin_role and session.query(User).filter(User.username == "admin").count() == 0:
                admin_user = User(
                    role_id=admin_role.id,
                    username="admin",
                    email="admin@apexinsurance.lk",
                    password_hash=hash_password("Admin@123456"),
                    must_change_password=False,
                    is_active=True,
                )
                session.add(admin_user)
                session.commit()

            # ----- Seed Operator User -----
            if operator_role and session.query(User).filter(User.username == "operatorm").count() == 0:
                operator_user = User(
                    role_id=operator_role.id,
                    username="operatorm",
                    email="operatorm@gmail.com",
                    password_hash=hash_password("Operator@123456"),
                    must_change_password=False,
                    is_active=True,
                )
                session.add(operator_user)
                session.commit()

            # ----- Seed Mock Customers -----
            if session.query(Customer).count() == 0:
                admin_user = session.query(User).filter(User.username == "admin").first()
                created_by_id = admin_user.id if admin_user else None

                customers_data = [
                    dict(
                        customer_code="CUS-00001",
                        full_name="Kamal Perera",
                        nic_or_passport="199023456789",
                        phone_primary="+94 77 123 4567",
                        email="kamal.perera@gmail.com",
                        address_line_1="45 Temple Road",
                        address_line_2="Dehiwala",
                        city="Colombo",
                        postal_code="10350",
                        notes="Long-standing policyholder since 2020.",
                        status="active",
                    ),
                    dict(
                        customer_code="CUS-00002",
                        full_name="Nimal Fernando",
                        nic_or_passport="198534567890",
                        phone_primary="+94 71 234 5678",
                        email="nimal.fernando@yahoo.com",
                        address_line_1="78 Lake Drive",
                        city="Kandy",
                        postal_code="20000",
                        status="active",
                    ),
                    dict(
                        customer_code="CUS-00003",
                        full_name="Sachini De Silva",
                        nic_or_passport="199245678901",
                        phone_primary="+94 76 345 6789",
                        email="sachini.desilva@outlook.com",
                        address_line_1="12 Galle Face Terrace",
                        address_line_2="Apt 3B",
                        city="Colombo",
                        postal_code="10200",
                        notes="VIP customer — Platinum plan.",
                        status="active",
                    ),
                    dict(
                        customer_code="CUS-00004",
                        full_name="Madara Senevi",
                        nic_or_passport="200056789012",
                        phone_primary="+94 70 456 7890",
                        email="ma22gs@gmail.com",
                        address_line_1="56 High Level Road",
                        city="Nugegoda",
                        postal_code="10250",
                        status="active",
                    ),
                    dict(
                        customer_code="CUS-00005",
                        full_name="Ruwan Jayasinghe",
                        nic_or_passport="198867890123",
                        phone_primary="+94 72 567 8901",
                        email="ruwan.jayasinghe@gmail.com",
                        address_line_1="33 Marine Drive",
                        city="Galle",
                        postal_code="80000",
                        status="active",
                    ),
                ]

                customer_objects = []
                for cdata in customers_data:
                    customer = Customer(created_by=created_by_id, **cdata)
                    session.add(customer)
                    customer_objects.append(customer)
                session.commit()

                # ----- Seed Customer User Accounts -----
                if customer_role:
                    customer_users = [
                        ("cus_1", "kamal.perera@gmail.com", customer_objects[0].id),
                        ("cus_2", "nimal.fernando@yahoo.com", customer_objects[1].id),
                        ("cus_3", "sachini.desilva@outlook.com", customer_objects[2].id),
                        ("cus_4", "ma22gs@gmail.com", customer_objects[3].id),
                        ("cus_5", "ruwan.jayasinghe@gmail.com", customer_objects[4].id),
                    ]
                    for username, email, cid in customer_users:
                        if session.query(User).filter(User.username == username).count() == 0:
                            session.add(User(
                                role_id=customer_role.id,
                                customer_id=cid,
                                username=username,
                                email=email,
                                password_hash=hash_password("Customer@123456"),
                                must_change_password=False,
                                is_active=True,
                            ))
                    session.commit()

                # ----- Seed Mock Vehicles -----
                vehicles_data = [
                    dict(customer_id=customer_objects[0].id, vehicle_code="VEH-00001",
                         registration_number="WP-CAB-1234", make="Toyota", model="Corolla",
                         manufactured_year=2020, colour="White", vehicle_type="Car",
                         fuel_type="Petrol", odometer_km=45000),
                    dict(customer_id=customer_objects[0].id, vehicle_code="VEH-00002",
                         registration_number="WP-KD-5678", make="Honda", model="Civic",
                         manufactured_year=2019, colour="Silver", vehicle_type="Car",
                         fuel_type="Petrol", odometer_km=62000),
                    dict(customer_id=customer_objects[1].id, vehicle_code="VEH-00003",
                         registration_number="CP-ABG-9012", make="Suzuki", model="Swift",
                         manufactured_year=2021, colour="Red", vehicle_type="Car",
                         fuel_type="Petrol", odometer_km=28000),
                    dict(customer_id=customer_objects[2].id, vehicle_code="VEH-00004",
                         registration_number="WP-LT-3456", make="BMW", model="X5",
                         manufactured_year=2022, colour="Black", vehicle_type="SUV",
                         fuel_type="Diesel", odometer_km=18000),
                    dict(customer_id=customer_objects[2].id, vehicle_code="VEH-00005",
                         registration_number="WP-MN-7890", make="Mercedes-Benz", model="C200",
                         manufactured_year=2021, colour="Grey", vehicle_type="Car",
                         fuel_type="Petrol", odometer_km=35000),
                    dict(customer_id=customer_objects[3].id, vehicle_code="VEH-00006",
                         registration_number="WP-QR-2345", make="Nissan", model="X-Trail",
                         manufactured_year=2020, colour="Blue", vehicle_type="SUV",
                         fuel_type="Diesel", odometer_km=52000),
                    dict(customer_id=customer_objects[3].id, vehicle_code="VEH-00007",
                         registration_number="SP-CD-6789", make="Toyota", model="Hilux",
                         manufactured_year=2023, colour="Silver", vehicle_type="Pickup",
                         fuel_type="Diesel", odometer_km=12000),
                    dict(customer_id=customer_objects[4].id, vehicle_code="VEH-00008",
                         registration_number="SG-EF-0123", make="Hyundai", model="Tucson",
                         manufactured_year=2022, colour="White", vehicle_type="SUV",
                         fuel_type="Petrol", odometer_km=22000),
                ]

                vehicle_objects = []
                for vdata in vehicles_data:
                    vehicle = Vehicle(created_by=created_by_id, **vdata)
                    session.add(vehicle)
                    vehicle_objects.append(vehicle)
                session.commit()

                # ----- Seed Vehicle Policies -----
                plans = session.query(InsurancePlan).all()
                if plans and vehicle_objects:
                    policies_data = [
                        dict(vehicle_id=vehicle_objects[0].id, plan_id=plans[0].id,
                             policy_number="POL-2024-00001", start_date=date(2024, 1, 15),
                             end_date=date(2025, 1, 14), premium_amount=Decimal("85000.00"), status="active"),
                        dict(vehicle_id=vehicle_objects[1].id, plan_id=plans[1].id,
                             policy_number="POL-2024-00002", start_date=date(2024, 3, 1),
                             end_date=date(2025, 2, 28), premium_amount=Decimal("62000.00"), status="active"),
                        dict(vehicle_id=vehicle_objects[2].id, plan_id=plans[2].id,
                             policy_number="POL-2024-00003", start_date=date(2024, 6, 1),
                             end_date=date(2025, 5, 31), premium_amount=Decimal("28000.00"), status="active"),
                        dict(vehicle_id=vehicle_objects[3].id, plan_id=plans[3].id,
                             policy_number="POL-2024-00004", start_date=date(2024, 2, 1),
                             end_date=date(2025, 1, 31), premium_amount=Decimal("180000.00"), status="active"),
                        dict(vehicle_id=vehicle_objects[4].id, plan_id=plans[0].id,
                             policy_number="POL-2024-00005", start_date=date(2024, 4, 15),
                             end_date=date(2025, 4, 14), premium_amount=Decimal("95000.00"), status="active"),
                        dict(vehicle_id=vehicle_objects[5].id, plan_id=plans[1].id,
                             policy_number="POL-2024-00006", start_date=date(2024, 7, 1),
                             end_date=date(2025, 6, 30), premium_amount=Decimal("70000.00"), status="active"),
                        dict(vehicle_id=vehicle_objects[6].id, plan_id=plans[0].id,
                             policy_number="POL-2024-00007", start_date=date(2024, 9, 1),
                             end_date=date(2025, 8, 31), premium_amount=Decimal("90000.00"), status="active"),
                        dict(vehicle_id=vehicle_objects[7].id, plan_id=plans[1].id,
                             policy_number="POL-2024-00008", start_date=date(2024, 5, 1),
                             end_date=date(2025, 4, 30), premium_amount=Decimal("68000.00"), status="active"),
                    ]
                    for pdata in policies_data:
                        session.add(VehiclePolicy(created_by=created_by_id, **pdata))
                    session.commit()
                    logger.info("Mock seed data inserted: 5 customers, 8 vehicles, %d policies, %d plans.", len(policies_data), len(plans))

        except Exception as e:
            logger.error(f"Error during auto DB bootstrap: {e}")
            session.rollback()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
