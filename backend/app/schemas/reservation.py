from typing import Optional
from pydantic import Field
from app.schemas.base import UTCBaseModel, KSTBaseModel
from datetime import datetime
from enum import Enum

# 예약 요청 객체
class ReservationCreateSchema(UTCBaseModel):
    start_time: datetime = Field(..., description="시작 시간")
    end_time: datetime = Field(..., description="종료 시간")
    head_count: int = Field(gt=0, description="인원수")

# 예약 상태
class ReservationStatus(str, Enum):
    PENDING = "보류중"
    CONFIRMED = "확정됨"

# 예약 조회 or 예약 요청에 대한 응답 객체
class ReservationResponseSchema(KSTBaseModel):
    id: int
    name: str
    head_count: int
    start_time: datetime
    end_time: datetime
    status: ReservationStatus
    created_at: datetime

# 예약 수정
class ReservationUpdateSchema(UTCBaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    head_count: Optional[int] = None