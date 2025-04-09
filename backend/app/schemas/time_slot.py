from enum import Enum
from datetime import datetime
from typing import List

from pydantic import Field
from app.schemas.pagination import Pagination
from app.schemas.base import KSTBaseModel

# 예약 가능한 시간을 보여주는 객체
class TimeSlotResponseSchema(KSTBaseModel):
    id: int = Field(description="타임슬롯 ID")
    start_time: datetime = Field(description="타임슬롯 시작 시간 (KST)",example="2025-04-12T17:00:00+09:00")
    end_time: datetime = Field(description="타임슬롯 종료 시간 (KST)",example="2025-04-12T18:00:00+09:00")
    is_reservable: bool = Field(description="예약 가능 여부")
    available_headcount: int = Field(description="예약 가능한 잔여 인원 수")

    class Config:
        from_attributes = True

# 예약가능한 시간 리스트
class PaginationTimeSlotResponseSchema(KSTBaseModel):
    pagination : Pagination = Field(description="페이징 정보")
    time_slots : List[TimeSlotResponseSchema] = Field(description="예약 가능한 시간 리스트")