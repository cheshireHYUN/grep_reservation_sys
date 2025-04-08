from pydantic import BaseModel
from datetime import datetime

class TimeSlotSchema(BaseModel):
    start_time: datetime
    end_time: datetime
    available_headcount: int

    class Config:
        from_attributes = True