from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class TimeSlotSchema(BaseModel):
    id : int
    start_time: datetime
    end_time: datetime
    is_reservable : bool
    available_headcount: int

    class Config:
        from_attributes = True

