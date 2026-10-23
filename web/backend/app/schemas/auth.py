"""认证相关 DTO：注册/登录/改密/资料更新请求与用户、令牌响应，含账号与角色校验。"""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


USERNAME_PATTERN = re.compile(r"^[\w\u4e00-\u9fff.-]+$", re.UNICODE)
PUBLIC_ROLES = {"safety_manager", "project_manager", "ordinary"}


class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, min_length=2, max_length=50)
    role: str = Field(default="ordinary", max_length=30)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        cleaned = value.strip()
        if not USERNAME_PATTERN.fullmatch(cleaned):
            raise ValueError("账号只能包含中文、字母、数字、点、短横线和下划线")
        return cleaned

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in PUBLIC_ROLES:
            raise ValueError("请选择安全管理员、项目经理或普通人员")
        return value


class LoginRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=1, max_length=128)
    role: str | None = Field(default=None, max_length=30)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class ProfileUpdateRequest(BaseModel):
    avatar_data: str = Field(default="", max_length=700_000)

    @field_validator("avatar_data")
    @classmethod
    def validate_avatar(cls, value: str) -> str:
        if value and not re.match(r"^data:image/(jpeg|png|webp);base64,", value):
            raise ValueError("头像仅支持 JPG、PNG 或 WebP 图片")
        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    avatar_data: str | None = None
    role: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
