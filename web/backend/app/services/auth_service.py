from __future__ import annotations

from datetime import datetime, timezone

import jwt
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..core.database import SessionLocal
from ..core.security import create_access_token, decode_access_token, hash_password, verify_password
from ..models import AuthSession, User
from ..schemas import (
    ChangePasswordRequest,
    LoginRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


def auth_error(detail: str = "登录状态无效或已过期") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def ensure_default_admin() -> None:
    """确保演示环境存在管理员账号：不存在则创建，存在但角色不是 admin 则提升为 admin。"""
    settings = get_settings()
    username = settings.admin_username.strip()
    if not username:
        return
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == username))
        if user is None:
            db.add(User(
                username=username,
                display_name="系统管理员",
                password_hash=hash_password(settings.admin_password),
                role="admin",
            ))
            db.commit()
            return
        if user.role != "admin":
            user.role = "admin"
            db.commit()


def resolve_role(user: User) -> str:
    """历史数据里 operator 与 ordinary 等价。"""
    return "ordinary" if user.role == "operator" else user.role


def load_session(db: Session, token: str) -> tuple[User, AuthSession]:
    """校验 JWT 与数据库会话，返回 (用户, 会话)；任何异常统一 401。"""
    try:
        payload = decode_access_token(token)
        user_id = int(str(payload["sub"]))
        token_id = str(payload["jti"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise auth_error() from None

    session = db.scalar(select(AuthSession).where(AuthSession.token_id == token_id))
    user = db.get(User, user_id)
    now = datetime.now(timezone.utc)
    if session is None or user is None or not user.is_active or session.revoked_at is not None:
        raise auth_error()
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        raise auth_error()
    return user, session


def register(db: Session, payload: RegisterRequest) -> User:
    existing = db.scalar(select(User).where(User.username == payload.username))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该账号已注册")
    user = User(
        username=payload.username,
        display_name=(payload.display_name or payload.username).strip(),
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该账号已注册") from None
    db.refresh(user)
    return user


def login(db: Session, payload: LoginRequest) -> TokenResponse:
    user = db.scalar(select(User).where(User.username == payload.username.strip()))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise auth_error("账号或密码不正确")
    expected_role = resolve_role(user)
    if payload.role and payload.role != expected_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="所选角色与账号权限不一致")
    token, token_id, expires_at = create_access_token(user.id)
    db.add(AuthSession(token_id=token_id, user_id=user.id, expires_at=expires_at))
    db.commit()
    return TokenResponse(
        access_token=token,
        expires_in=get_settings().access_token_minutes * 60,
        user=UserResponse.model_validate(user),
    )


def update_profile(db: Session, user: User, payload: ProfileUpdateRequest) -> User:
    user.avatar_data = payload.avatar_data or None
    db.commit()
    db.refresh(user)
    return user


def logout(db: Session, session: AuthSession) -> None:
    session.revoked_at = datetime.now(timezone.utc)
    db.commit()


def change_password(db: Session, user: User, session: AuthSession, payload: ChangePasswordRequest) -> None:
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码不正确")
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码不能与当前密码相同")
    user.password_hash = hash_password(payload.new_password)
    now = datetime.now(timezone.utc)
    db.execute(
        update(AuthSession)
        .where(AuthSession.user_id == user.id, AuthSession.id != session.id, AuthSession.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    db.commit()
