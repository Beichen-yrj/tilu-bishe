"""意见反馈业务：创建、可见范围查询与管理员回复。"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Feedback, User
from ..schemas import FeedbackCreate, FeedbackReply, FeedbackResponse


def to_response(feedback: Feedback, submitter: User | None) -> FeedbackResponse:
    return FeedbackResponse(
        id=feedback.id,
        category=feedback.category,
        title=feedback.title,
        content=feedback.content,
        status=feedback.status,
        reply=feedback.reply,
        replied_by=feedback.replied_by,
        created_at=feedback.created_at.strftime("%Y-%m-%d %H:%M"),
        replied_at=feedback.replied_at.strftime("%Y-%m-%d %H:%M") if feedback.replied_at else None,
        submitter=(submitter.display_name if submitter else "未知用户"),
        username=(submitter.username if submitter else "-"),
    )


def create(db: Session, user: User, payload: FeedbackCreate) -> FeedbackResponse:
    feedback = Feedback(
        user_id=user.id,
        category=payload.category.strip(),
        title=payload.title.strip(),
        content=payload.content.strip(),
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return to_response(feedback, user)


def list_for_user(db: Session, user: User) -> list[FeedbackResponse]:
    is_admin = user.role == "admin"
    statement = select(Feedback).order_by(Feedback.created_at.desc())
    if not is_admin:
        statement = statement.where(Feedback.user_id == user.id)
    records = list(db.scalars(statement))
    submitters: dict[int, User] = {}
    ids = {record.user_id for record in records}
    if ids:
        for submitter in db.scalars(select(User).where(User.id.in_(ids))):
            submitters[submitter.id] = submitter
    return [to_response(record, submitters.get(record.user_id)) for record in records]


def reply(db: Session, admin: User, feedback_id: int, payload: FeedbackReply) -> FeedbackResponse:
    if admin.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可执行该操作")
    feedback = db.get(Feedback, feedback_id)
    if feedback is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="反馈记录不存在")
    feedback.reply = payload.reply.strip()
    feedback.status = "已回复"
    feedback.replied_by = f"{admin.display_name}（管理员）"
    feedback.replied_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(feedback)
    submitter = db.get(User, feedback.user_id)
    return to_response(feedback, submitter)
