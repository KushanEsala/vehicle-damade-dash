from __future__ import annotations

from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from core.config import get_settings
from core.exceptions import AuthenticationError, AccountLockedError, ValidationError, ResourceNotFoundError
from core.security import verify_password, hash_password, validate_password_strength, generate_temporary_password
from database.repositories.user_repository import UserRepository
from database.repositories.audit_repository import AuditRepository
from database.models.user import User


class AuthenticationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.audit_repo = AuditRepository(session)
        self.settings = get_settings()

    def authenticate(self, identifier: str, password: str, ip_address: str | None = None) -> User:
        user = self.user_repo.get_by_username_or_email(identifier)
        if not user or not user.is_active:
            self.audit_repo.log_event(
                action="login_failed",
                entity_type="user",
                ip_address=ip_address,
                success=False,
                failure_reason="Invalid credentials or inactive user.",
            )
            raise AuthenticationError("Invalid username/email or password.")

        # Check lockout
        now = datetime.now(timezone.utc)
        if user.locked_until and user.locked_until > now:
            remaining = int((user.locked_until - now).total_seconds() / 60.0) + 1
            self.audit_repo.log_event(
                action="login_blocked_locked",
                entity_type="user",
                user_id=user.id,
                ip_address=ip_address,
                success=False,
                failure_reason=f"Account locked for {remaining} more minutes.",
            )
            raise AccountLockedError(f"Account is temporarily locked. Try again in {remaining} minutes.")

        # Verify password
        if not verify_password(user.password_hash, password):
            user.failed_login_count += 1
            if user.failed_login_count >= self.settings.MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=self.settings.LOCKOUT_DURATION_MINUTES)
                failure_msg = f"Account locked due to {user.failed_login_count} failed login attempts."
            else:
                failure_msg = "Invalid password."

            self.user_repo.save(user)
            self.audit_repo.log_event(
                action="login_failed",
                entity_type="user",
                user_id=user.id,
                ip_address=ip_address,
                success=False,
                failure_reason=failure_msg,
            )
            raise AuthenticationError("Invalid username/email or password.")

        # Login successful
        user.failed_login_count = 0
        user.locked_until = None
        user.last_login_at = now
        self.user_repo.save(user)

        self.audit_repo.log_event(
            action="login_success",
            entity_type="user",
            user_id=user.id,
            ip_address=ip_address,
            success=True,
        )

        return user

    def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User not found.")

        if not verify_password(user.password_hash, current_password):
            raise ValidationError("Current password is incorrect.")

        if current_password == new_password:
            raise ValidationError("New password must differ from current password.")

        validate_password_strength(new_password)

        user.password_hash = hash_password(new_password)
        user.must_change_password = False
        user.password_changed_at = datetime.now(timezone.utc)
        self.user_repo.save(user)

        self.audit_repo.log_event(
            action="password_change",
            entity_type="user",
            user_id=user.id,
            success=True,
        )

    def reset_password(self, admin_id: int, target_user_id: int) -> str:
        user = self.user_repo.get_by_id(target_user_id)
        if not user:
            raise ResourceNotFoundError("Target user not found.")

        temp_password = generate_temporary_password()
        user.password_hash = hash_password(temp_password)
        user.must_change_password = True
        user.failed_login_count = 0
        user.locked_until = None
        self.user_repo.save(user)

        self.audit_repo.log_event(
            action="admin_password_reset",
            entity_type="user",
            user_id=admin_id,
            entity_id=target_user_id,
            success=True,
        )

        return temp_password
