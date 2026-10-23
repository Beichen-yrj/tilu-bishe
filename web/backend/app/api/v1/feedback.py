"""意见反馈路由：提交反馈、按角色列出反馈、管理员回复。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models import User
from ...schemas import FeedbackCreate, FeedbackReply, FeedbackResponse
from ...services import feedback_service
from ..deps import get_current_user


router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    return feedback_service.create(db, user, payload)


@router.get("", response_model=list[FeedbackResponse])
def list_feedback(
    user: User = Depends(get_current_user), db: Session = Depends(get_db),
) -> list[FeedbackResponse]:
    return feedback_service.list_for_user(db, user)


@router.post("/{feedback_id}/reply", response_model=FeedbackResponse)
def reply_feedback(
    feedback_id: int,
    payload: FeedbackReply,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    return feedback_service.reply(db, user, feedback_id, payload)
