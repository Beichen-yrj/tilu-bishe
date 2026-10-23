"""AI 助手路由：把脱敏业务摘要与提问转发给模型服务，仅返回建议。"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ...models import User
from ...schemas import AiChatRequest, AiChatResponse
from ...services import ai_service
from ..deps import get_current_user


router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/chat", response_model=AiChatResponse)
async def chat(payload: AiChatRequest, user: User = Depends(get_current_user)) -> AiChatResponse:
    return await ai_service.chat(payload, user)
