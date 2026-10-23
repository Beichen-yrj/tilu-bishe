from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base
from .base import utc_now


class HazardAssessment(Base):
    __tablename__ = "hazard_assessments"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    task_name: Mapped[str] = mapped_column(String(120), nullable=False)
    bureau: Mapped[str] = mapped_column(String(80), default="", nullable=False)
    station: Mapped[str] = mapped_column(String(80), nullable=False)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    cargo: Mapped[str] = mapped_column(String(100), nullable=False)
    un_number: Mapped[str] = mapped_column(String(30), default="", nullable=False)
    inspector: Mapped[str] = mapped_column(String(50), nullable=False)
    hazard_code: Mapped[str] = mapped_column(String(20), nullable=False)
    stage: Mapped[str] = mapped_column(String(20), nullable=False)
    dimension: Mapped[str] = mapped_column(String(20), nullable=False)
    hazard_name: Mapped[str] = mapped_column(String(160), nullable=False)
    basis: Mapped[str] = mapped_column(Text, nullable=False)
    assessment_type: Mapped[str] = mapped_column(String(20), nullable=False)
    data_name: Mapped[str] = mapped_column(String(100), nullable=False)
    measured_value: Mapped[str] = mapped_column(String(100), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), default="", nullable=False)
    standard_value: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    static_result: Mapped[str] = mapped_column(String(20), default="", nullable=False)
    likelihood: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    severity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    risk: Mapped[str] = mapped_column(String(20), nullable=False)
    has_hazard: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    finding: Mapped[str] = mapped_column(Text, default="", nullable=False)
    action: Mapped[str] = mapped_column(Text, default="", nullable=False)
    photo_name: Mapped[str] = mapped_column(String(180), default="", nullable=False)
    photo_data: Mapped[str] = mapped_column(Text().with_variant(LONGTEXT(), "mysql"), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="已完成", nullable=False)
    rectification_photo_name: Mapped[str] = mapped_column(String(180), default="", nullable=False)
    rectification_photo_data: Mapped[str] = mapped_column(Text().with_variant(LONGTEXT(), "mysql"), default="", nullable=False)
    review_result: Mapped[str] = mapped_column(String(20), default="", nullable=False)
    review_measured_value: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    review_standard_value: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    rectification_log: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    workflow_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_label: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
