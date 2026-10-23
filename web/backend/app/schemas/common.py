"""通用响应模型：健康检查与消息响应。"""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: str


class MessageResponse(BaseModel):
    message: str
