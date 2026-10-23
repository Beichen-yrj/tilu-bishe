from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AssessmentPayload(BaseModel):
    id: str = Field(min_length=3, max_length=40)
    name: str = Field(min_length=1, max_length=120)
    station: str = Field(min_length=1, max_length=80)
    area: str = Field(min_length=1, max_length=100)
    cargo: str = Field(min_length=1, max_length=100)
    un_number: str = Field(default="", max_length=30)
    detector: str = Field(min_length=1, max_length=120)
    temperature: float
    pressure: float
    concentration: float
    static_checks: list[bool]
    likelihood: int = Field(ge=1, le=5)
    severity: int = Field(ge=1, le=5)
    risk: str = Field(max_length=20)
    score: int = Field(ge=1, le=25)
    status: str = Field(max_length=20)
    findings: list[str]
    measures: list[str]
    created_at: str = Field(max_length=40)


class AssessmentResponse(AssessmentPayload):
    model_config = ConfigDict(from_attributes=True)
