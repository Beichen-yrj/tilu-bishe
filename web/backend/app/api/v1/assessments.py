from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models import User
from ...schemas import AssessmentPayload, AssessmentResponse
from ...services import assessment_service
from ..deps import require_assessor


router = APIRouter(prefix="/api/assessments", tags=["assessments"])


@router.get("", response_model=list[AssessmentResponse])
def list_assessments(
    user: User = Depends(require_assessor), db: Session = Depends(get_db),
) -> list[AssessmentResponse]:
    return assessment_service.list_for_user(db, user)


@router.put("/{assessment_id}", response_model=AssessmentResponse)
def save_assessment(
    assessment_id: str,
    payload: AssessmentPayload,
    user: User = Depends(require_assessor),
    db: Session = Depends(get_db),
) -> AssessmentResponse:
    return assessment_service.save(db, user, assessment_id, payload)
