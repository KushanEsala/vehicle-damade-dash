from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.logging_config import logger
from core.security import hash_password
from database.connection import get_db_session
from database.models.user import Role, User


def create_initial_admin(username: str = "admin", email: str = "admin@apexinsurance.lk", password: str = "Admin@123456") -> None:
    with get_db_session() as session:
        admin_role = session.query(Role).filter(Role.code == "admin").first()
        if not admin_role:
            logger.error("Admin role not found. Run bootstrap_database.py first.")
            return

        existing = session.query(User).filter(User.username == username).first()
        if existing:
            logger.info(f"Admin user '{username}' already exists.")
            return

        hashed = hash_password(password)
        admin = User(
            role_id=admin_role.id,
            username=username,
            email=email,
            password_hash=hashed,
            must_change_password=False,
            is_active=True,
        )
        session.add(admin)
        session.commit()
        logger.info(f"Successfully created admin user: {username}")


if __name__ == "__main__":
    create_initial_admin()
