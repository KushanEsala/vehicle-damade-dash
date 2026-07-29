from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from core.config import get_settings
from database.connection import get_db_session
from database.models.user import AppSession, User


COOKIE_NAME = "vehicle_erp_session"


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def db_dependency():
    with get_db_session() as session:
        yield session


DbSession = Depends(db_dependency)


def create_session(db: Session, user: User, response: Response) -> None:
    settings = get_settings()
    raw_token = secrets.token_urlsafe(48)
    now = utc_now()
    expiry = now + timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
    db.query(AppSession).filter(AppSession.user_id == user.id).delete()
    db.add(
        AppSession(
            token_hash=token_hash(raw_token),
            user_id=user.id,
            expires_at=expiry,
            last_activity_at=now,
        )
    )
    db.flush()
    response.set_cookie(
        key=COOKIE_NAME,
        value=raw_token,
        max_age=settings.SESSION_TIMEOUT_MINUTES * 60,
        httponly=True,
        secure=settings.APP_ENV.lower() == "production",
        samesite="lax",
        path="/",
    )


def clear_session(db: Session, response: Response, raw_token: str | None) -> None:
    if raw_token:
        db.query(AppSession).filter(AppSession.token_hash == token_hash(raw_token)).delete()
    response.delete_cookie(COOKIE_NAME, path="/")


def current_user(
    session_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
    db: Session = Depends(db_dependency),
) -> User:
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in required.")
    now = utc_now()
    app_session = (
        db.query(AppSession)
        .filter(AppSession.token_hash == token_hash(session_token))
        .first()
    )
    if not app_session or app_session.expires_at <= now:
        if app_session:
            db.delete(app_session)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired.")
    user = db.query(User).filter(User.id == app_session.user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account unavailable.")
    if user.role.code == "customer" and not user.customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer account is not linked.")
    settings = get_settings()
    app_session.last_activity_at = now
    app_session.expires_at = now + timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
    db.flush()
    return user


def require_roles(*roles: str):
    def dependency(user: User = Depends(current_user)) -> User:
        if user.role.code not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        return user

    return dependency
