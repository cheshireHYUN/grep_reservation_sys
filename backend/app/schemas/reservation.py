from pydantic import Field
from app.schemas.base import UTCBaseModel
from datetime import datetime

# 예약 요청 객체
class ReservationCreateSchema(UTCBaseModel):
    company_name: str= Field(..., description="회사명")
    start_time: datetime = Field(..., description="시작 시간")
    end_time: datetime = Field(..., description="종료 시간")
    head_count: int = Field(gt=0, description="인원수")

# 예약 요청에 대한 응답 객체
class ReservationResponseSchema(UTCBaseModel):
    id: int
    company_name: str
    start_time: datetime
    end_time: datetime
    head_count: int
    is_confirmed: bool

    class Config:
        from_attributes = True
