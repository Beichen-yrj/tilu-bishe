"""HTTP 层公共依赖：数据库会话、JWT 会话校验，以及 reader/assessor/rectifier/admin 角色门槛。"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models import AuthSession, User
from ..services import auth_service, hazard_service


bearer = HTTPBearer(auto_error=False)


def get_current_session(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> tuple[User, AuthSession]:
    if credentials is None:
        raise auth_service.auth_error()
    return auth_service.load_session(db, credentials.credentials)


def get_current_user(current: tuple[User, AuthSession] = Depends(get_current_session)) -> User:
    return current[0]


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可执行该操作")
    return user


def require_reader(user: User = Depends(get_current_user)) -> User:
    if user.role not in hazard_service.READ_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前角色无风险数据查看权限")
    return user


def require_assessor(user: User = Depends(get_current_user)) -> User:
    if user.role not in hazard_service.WRITE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前角色无风险评估权限")
    return user


def require_rectifier(user: User = Depends(get_current_user)) -> User:
    if user.role not in hazard_service.RECTIFY_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前角色无整改操作权限")
    return user
