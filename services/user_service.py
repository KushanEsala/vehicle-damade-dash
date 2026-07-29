from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from core.exceptions import DuplicateResourceError, ResourceNotFoundError, ValidationError
from core.security import hash_password, generate_temporary_password
from database.repositories.user_repository import UserRepository
from database.repositories.audit_repository import AuditRepository
from database.models.user import AppSession, User


class UserService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.audit_repo = AuditRepository(session)

    def create_staff_user(
        self,
        username: str,
        email: str,
        role_code: str,
        admin_user_id: int,
    ) -> tuple[User, str]:
        username = username.strip().lower()
        email = email.strip().lower()

        if not username or not email:
            raise ValidationError("Username and email are required.")

        role = self.user_repo.get_role_by_code(role_code)
        if not role:
            raise ValidationError(f"Role '{role_code}' does not exist.")

        existing = self.user_repo.get_by_username_or_email(username)
        if existing:
            raise DuplicateResourceError(f"User '{username}' or email '{email}' already exists.")

        temp_password = generate_temporary_password()
        user = User(
            role_id=role.id,
            username=username,
            email=email,
            password_hash=hash_password(temp_password),
            must_change_password=True,
            is_active=True,
            created_by=admin_user_id,
        )
        self.user_repo.save(user)

        self.audit_repo.log_event(
            action="create_staff_user",
            entity_type="user",
            user_id=admin_user_id,
            entity_id=user.id,
            new_values={"username": username, "role": role_code},
        )

        return user, temp_password

    def set_user_active_status(self, user_id: int, is_active: bool, admin_user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError(f"User #{user_id} not found.")

        user.is_active = is_active
        self.user_repo.save(user)

        self.audit_repo.log_event(
            action="update_user_status",
            entity_type="user",
            user_id=admin_user_id,
            entity_id=user_id,
            new_values={"is_active": is_active},
        )

        return user

    def list_all_users(self) -> list[User]:
        return self.user_repo.list_users()

    def update_active_status(self, user_id: int, is_active: bool, admin_user_id: int) -> User:
        if user_id == admin_user_id:
            raise ValidationError("You cannot deactivate your own administrator account.")
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError(f"User #{user_id} not found.")
        old_status = user.is_active
        user.is_active = is_active
        self.user_repo.save(user)
        if not is_active:
            self.session.query(AppSession).filter(AppSession.user_id == user.id).delete()
        self.audit_repo.log_event(
            action="activate_user" if is_active else "deactivate_user",
            entity_type="user",
            user_id=admin_user_id,
            entity_id=user.id,
            old_values={"is_active": old_status},
            new_values={"is_active": is_active},
        )
        return user

    def delete_user(self, user_id: int, admin_user_id: int) -> None:
        if user_id == admin_user_id:
            raise ValidationError("You cannot delete your own administrator account.")
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError(f"User #{user_id} not found.")
        self.session.query(AppSession).filter(AppSession.user_id == user.id).delete()
        username = user.username
        try:
            self.session.delete(user)
            self.session.flush()
        except IntegrityError as exc:
            raise ValidationError(
                "This user has linked history and cannot be deleted. Deactivate the account instead."
            ) from exc
        self.audit_repo.log_event(
            action="delete_user",
            entity_type="user",
            user_id=admin_user_id,
            entity_id=user_id,
            old_values={"username": username},
        )
