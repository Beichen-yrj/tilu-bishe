from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models import User
from ...schemas import HazardAssessmentPayload, HazardAssessmentResponse, RectificationStatusPayload
from ...services import hazard_service
from ..deps import require_assessor, require_reader, require_rectifier


router = APIRouter(prefix="/api/hazard-assessments", tags=["hazard-assessments"])


@router.get("", response_model=list[HazardAssessmentResponse])
def list_hazard_assessments(
    user: User = Depends(require_reader), db: Session = Depends(get_db),
) -> list[HazardAssessmentResponse]:
    return hazard_service.list_all(db)


@router.put("/{assessment_id}", response_model=HazardAssessmentResponse)
def save_hazard_assessment(
    assessment_id: str,
    payload: HazardAssessmentPayload,
    user: User = Depends(require_assessor),
    db: Session = Depends(get_db),
) -> HazardAssessmentResponse:
    return hazard_service.save(db, user, assessment_id, payload)


@router.delete("/{assessment_id}", response_model=dict[str, bool])
def delete_hazard_assessment(
    assessment_id: str,
    user: User = Depends(require_assessor),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    return hazard_service.delete(db, user, assessment_id)


@router.patch("/{assessment_id}/rectification", response_model=HazardAssessmentResponse)
def update_rectification(
    assessment_id: str,
    payload: RectificationStatusPayload,
    user: User = Depends(require_rectifier),
    db: Session = Depends(get_db),
) -> HazardAssessmentResponse:
    return hazard_service.update_rectification(db, user, assessment_id, payload)
