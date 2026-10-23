"""意见反馈 DTO：创建、回复、响应结构。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    category: str = Field(min_length=2, max_length=40)
    title: str = Field(min_length=2, max_length=120)
    content: str = Field(min_length=5, max_length=2000)


class FeedbackReply(BaseModel):
    reply: str = Field(min_length=2, max_length=2000)


class FeedbackResponse(BaseModel):
    id: int
    category: str
    title: str
    content: str
    status: str
    reply: str | None = None
    replied_by: str | None = None
    created_at: str
    replied_at: str | None = None
    submitter: str
    username: str
