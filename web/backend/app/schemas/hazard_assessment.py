"""隐患排查评估 DTO：评估载荷与响应，以及整改操作载荷（阶段、操作类型、版本号、复核数据）。"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HazardAssessmentPayload(BaseModel):
    id: str = Field(min_length=3, max_length=40)
    task_name: str = Field(min_length=1, max_length=120)
    bureau: str = Field(default="", max_length=80)
    station: str = Field(min_length=1, max_length=80)
    area: str = Field(min_length=1, max_length=100)
    cargo: str = Field(min_length=1, max_length=100)
    un_number: str = Field(default="", max_length=30)
    inspector: str = Field(min_length=1, max_length=50)
    hazard_code: str = Field(min_length=1, max_length=20)
    stage: str = Field(min_length=1, max_length=20)
    dimension: str = Field(min_length=1, max_length=20)
    hazard_name: str = Field(min_length=1, max_length=160)
    basis: str = Field(min_length=1, max_length=4000)
    assessment_type: str = Field(pattern="^(静态|动态)$")
    data_name: str = Field(min_length=1, max_length=100)
    measured_value: str = Field(min_length=1, max_length=100)
    unit: str = Field(default="", max_length=30)
    standard_value: str = Field(default="", max_length=160)
    static_result: str = Field(default="", max_length=20)
    likelihood: int = Field(ge=1, le=5)
    severity: int = Field(ge=1, le=5)
    score: int = Field(ge=1, le=25)
    risk: str = Field(pattern="^(低|一般|较大|重大)$")
    has_hazard: bool
    finding: str = Field(default="", max_length=4000)
    action: str = Field(default="", max_length=4000)
    photo_name: str = Field(default="", max_length=180)
    photo_data: str = Field(default="", max_length=1_500_000)
    status: str = Field(default="已完成", max_length=20)
    created_at: str = Field(max_length=40)


class HazardAssessmentResponse(HazardAssessmentPayload):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    reviewer_name: str
    rectification_photo_name: str = ""
    rectification_photo_data: str = ""
    review_result: str = ""
    review_measured_value: str = ""
    review_standard_value: str = ""
    rectification_log: list[dict] = Field(default_factory=list)
    workflow_version: int = 0


class RectificationStatusPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["待整改", "整改中", "待复核", "复核中", "待项目经理确认", "已闭环"]
    operation: Literal["save_progress", "advance", "withdraw", "reject", "edit"]
    expected_version: int = Field(ge=0)
    note: str = Field(min_length=1, max_length=4000)
    rectification_photo_name: str = Field(default="", max_length=180)
    rectification_photo_data: str = Field(default="", max_length=1_500_000)
    review_result: Literal["", "合格", "不合格"] = ""
    review_measured_value: str = Field(default="", max_length=100)
    review_standard_value: str = Field(default="", max_length=160)
    edit_event_id: str = Field(default="", max_length=80)
