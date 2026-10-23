"""通用评估实体：Assessment，保存检测数据、风险等级与结论。"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base
from .base import utc_now


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    station: Mapped[str] = mapped_column(String(80), nullable=False)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    cargo: Mapped[str] = mapped_column(String(100), nullable=False)
    un_number: Mapped[str] = mapped_column(String(30), default="", nullable=False)
    detector: Mapped[str] = mapped_column(String(120), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    pressure: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    concentration: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    static_checks: Mapped[list[bool]] = mapped_column(JSON, nullable=False)
    likelihood: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    severity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    risk: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    findings: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    measures: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_label: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
