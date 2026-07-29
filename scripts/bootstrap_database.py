from __future__ import annotations

import sys
from pathlib import Path

# Append project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.logging_config import logger
from core.security import hash_password
from database.connection import init_db, get_db_session
from database.models.user import Role, User
from database.models.company import CompanyInformation
from database.models.plan import InsurancePlan


def bootstrap() -> None:
    logger.info("Initializing database schema...")
    init_db()

    with get_db_session() as session:
        # Seed Roles
        roles_data = [
            ("admin", "System Administrator", "Full access to ERP configuration, staff, and audit records."),
            ("operator", "Claims Operator", "Registers customers, vehicles, runs analyses, and adds costs."),
            ("customer", "Policyholder Customer", "Views owned vehicles, damage summaries, and downloads reports."),
        ]
        for code, name, desc in roles_data:
            existing = session.query(Role).filter(Role.code == code).first()
            if not existing:
                role = Role(code=code, name=name, description=desc)
                session.add(role)
                logger.info(f"Seeded role: {code}")

        # Seed Company Information
        company = session.query(CompanyInformation).first()
        if not company:
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
            logger.info("Seeded company information placeholder.")

        # Seed Default Insurance Plan
        plan = session.query(InsurancePlan).filter(InsurancePlan.plan_code == "PLN-COMP-GOLD").first()
        if not plan:
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
            logger.info("Seeded default insurance plan.")

        session.commit()
    logger.info("BOOTSTRAP COMPLETED SUCCESSFULLY.")


if __name__ == "__main__":
    bootstrap()
