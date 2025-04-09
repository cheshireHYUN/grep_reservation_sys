from enum import Enum
from datetime import datetime
from app.schemas.base import KSTBaseModel

# 예약가능한 시간을 보여주는 객체
class TimeSlotResponseSchema(KSTBaseModel):
    id : int
    start_time: datetime
    end_time: datetime
    is_reservable : bool
    available_headcount: int

    class Config:
        from_attributes = True

