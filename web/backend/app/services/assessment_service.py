from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Assessment, User
from ..schemas import AssessmentPayload, AssessmentResponse


FIELDS = (
    "name", "station", "area", "cargo", "un_number", "detector", "temperature", "pressure",
    "concentration", "static_checks", "likelihood", "severity", "risk", "score", "status", "findings", "measures",
)


def to_response(item: Assessment) -> AssessmentResponse:
    return AssessmentResponse(
        id=item.id,
        name=item.name,
        station=item.station,
        area=item.area,
        cargo=item.cargo,
        un_number=item.un_number,
        detector=item.detector,
        temperature=item.temperature,
        pressure=item.pressure,
        concentration=item.concentration,
        static_checks=item.static_checks,
        likelihood=item.likelihood,
        severity=item.severity,
        risk=item.risk,
        score=item.score,
        status=item.status,
        findings=item.findings,
        measures=item.measures,
        created_at=item.created_label,
    )


def list_for_user(db: Session, user: User) -> list[AssessmentResponse]:
    items = db.scalars(
        select(Assessment).where(Assessment.user_id == user.id).order_by(Assessment.updated_at.desc())
    ).all()
    return [to_response(item) for item in items]


def save(db: Session, user: User, assessment_id: str, payload: AssessmentPayload) -> AssessmentResponse:
    item = db.get(Assessment, assessment_id)
    if item is None:
        item = Assessment(id=assessment_id, user_id=user.id)
        db.add(item)
    elif item.user_id != user.id:
        # Do not reveal whether another user's record exists.
        item = Assessment(id=f"{assessment_id}-{user.id}", user_id=user.id)
        db.add(item)
    for field in FIELDS:
        setattr(item, field, getattr(payload, field))
    item.created_label = payload.created_at
    db.commit()
    db.refresh(item)
    return to_response(item)
