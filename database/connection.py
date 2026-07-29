from __future__ import annotations

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session

from core.config import get_settings
from core.logging_config import logger
from database.base import Base

settings = get_settings()

try:
    engine = create_engine(
        settings.database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False,
    )
    with engine.connect() as conn:
        pass
    logger.info("Connected to MySQL database '%s' successfully.", settings.MYSQL_DATABASE)
except Exception as e:
    if settings.APP_ENV.lower() == "production":
        raise RuntimeError(
            f"Production database connection failed for {settings.MYSQL_DATABASE}. "
            "SQLite fallback is disabled in production."
        ) from e
    logger.warning(
        "Could not connect to MySQL at %s:%s/%s (%s). Falling back to local SQLite database 'vehicle_analyzis.db'.",
        settings.MYSQL_HOST, settings.MYSQL_PORT, settings.MYSQL_DATABASE, e,
    )
    sqlite_path = settings.project_root / "vehicle_analyzis.db"
    engine = create_engine(
        f"sqlite:///{sqlite_path}",
        connect_args={"check_same_thread": False},
        echo=False,
    )

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
            from database.models.plan import InsurancePlan
            from core.security import hash_password

            # Seed Roles
            if session.query(Role).count() == 0:
                roles = [
                    Role(code="admin", name="System Administrator", description="Full access to ERP configuration, staff, and audit records."),
                    Role(code="operator", name="Claims Operator", description="Registers customers, vehicles, runs analyses, and adds costs."),
                    Role(code="customer", name="Policyholder Customer", description="Views owned vehicles, damage summaries, and downloads reports."),
                ]
                session.add_all(roles)
                session.commit()

            # Seed Company
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

            # Seed Default Insurance Plan
            if session.query(InsurancePlan).count() == 0:
                plan = InsurancePlan(
                    plan_code="PLN-COMP-GOLD",
                    name="Comprehensive Gold Auto Shield",
                    description="Full comprehensive accident, natural disaster, and third-party liability coverage.",
                    coverage_limit=5000000.00,
                    deductible_amount=15000.00,
                    currency_code="LKR",
                    is_active=True,
                )
                session.add(plan)
                session.commit()

            # Seed Initial Admin
            admin_role = session.query(Role).filter(Role.code == "admin").first()
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
