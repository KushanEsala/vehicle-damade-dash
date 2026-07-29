from __future__ import annotations

from sqlalchemy.orm import Session
from database.models.user import Role, User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_role_by_code(self, code: str) -> Role | None:
        return self.session.query(Role).filter(Role.code == code).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_username_or_email(self, identifier: str) -> User | None:
        ident = identifier.strip().lower()
        return (
            self.session.query(User)
            .filter((User.username == ident) | (User.email == ident))
            .first()
        )

    def list_users(self) -> list[User]:
        return self.session.query(User).order_by(User.created_at.desc()).all()

    def save(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user
