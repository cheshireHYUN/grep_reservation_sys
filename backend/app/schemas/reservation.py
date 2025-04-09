from typing import Optional
from pydantic import Field, model_validator
from app.schemas.base import UTCBaseModel, KSTBaseModel
from datetime import datetime
from enum import Enum
from app.config.config import MAX_HEADCOUNT

# 예약 요청 객체
class ReservationCreateSchema(UTCBaseModel):
    start_time: datetime = Field(..., description="시작시간 (KST)",example="2025-04-12T17:00:00+09:00")
    end_time: datetime = Field(..., description="종료시간 (KST)",example="2025-04-12T18:00:00+09:00")
    head_count: int = Field(..., ge=1, le=MAX_HEADCOUNT, description="예약 인원 수")

    @model_validator(mode="after")
    def check_time_order(self):
        if self.end_time <= self.start_time:
            raise ValueError("종료시간은 시작시간보다 늦어야 합니다.")
        return self

# 예약 상태
class ReservationStatus(str, Enum):
    PENDING = "보류중"
    CONFIRMED = "확정됨"

# 예약 조회 or 예약 요청에 대한 응답 객체
class ReservationResponseSchema(KSTBaseModel):
    id: int = Field(..., description="예약 ID")
    name: str = Field(..., description="사용자 이름")
    head_count: int = Field(..., description="예약 인원 수")
    start_time: datetime = Field(..., description="시작시간 (KST)",example="2025-04-12T17:00:00+09:00")
    end_time: datetime = Field(..., description="종료시간 (KST)",example="2025-04-12T18:00:00+09:00")
    status: ReservationStatus = Field(..., description="예약 상태")
    created_at: datetime = Field(..., description="신청시간 (KST)",example="2025-04-08T12:00:00+09:00")

# 예약 수정
class ReservationUpdateSchema(UTCBaseModel):
    start_time: Optional[datetime] = Field(
        default=None,
        description="시작시간 (KST)",
        example="2025-04-12T17:00:00+09:00"
    )
    end_time: Optional[datetime] = Field(
        default=None,
        description="종료시간 (KST)",
        example="2025-04-12T18:00:00+09:00"
    )
    head_count: Optional[int] = Field(
        default=None, 
        ge=1, 
        le=MAX_HEADCOUNT,
        description="변경할 예약 인원 수"
    )

    @model_validator(mode="after")
    def check_time_order(self):
        if self.start_time is not None and self.end_time is not None:
            if self.end_time <= self.start_time:
                raise ValueError("종료시간은 시작시간보다 늦어야 합니다.")
        return self
