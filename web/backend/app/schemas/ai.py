from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AiAssessmentContext(BaseModel):
    id: str = Field(max_length=40)
    name: str = Field(max_length=120)
    cargo: str = Field(max_length=100)
    station: str = Field(max_length=80)
    risk: str = Field(max_length=20)
    score: int = Field(ge=1, le=25)
    finding_count: int = Field(ge=0, le=1000)


class AiChatContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    assessment_count: int = Field(ge=0, le=100000)
    open_issue_count: int = Field(ge=0, le=100000)
    major_issue_count: int = Field(ge=0, le=100000)
    latest_assessment: AiAssessmentContext | None = None


class AiChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=1000)
    context: AiChatContext

    @field_validator("question")
    @classmethod
    def clean_question(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("问题不能为空")
        return cleaned


class AiChatResponse(BaseModel):
    answer: str
    provider: str = "deepseek"
    model: str
