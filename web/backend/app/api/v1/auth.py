from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models import AuthSession, User
from ...schemas import (
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    ProfileUpdateRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from ...services import auth_service
from ..deps import get_current_session, get_current_user


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    return auth_service.register(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.login(db, payload)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("/profile", response_model=UserResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    return auth_service.update_profile(db, user, payload)


@router.post("/logout", response_model=MessageResponse)
def logout(
    current: tuple[User, AuthSession] = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> MessageResponse:
    auth_service.logout(db, current[1])
    return MessageResponse(message="已退出登录")


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    current: tuple[User, AuthSession] = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> MessageResponse:
    user, session = current
    auth_service.change_password(db, user, session, payload)
    return MessageResponse(message="密码已修改，其他登录会话已失效")
