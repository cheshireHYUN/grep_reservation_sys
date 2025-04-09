from typing import Optional
from pydantic import Field
from app.schemas.base import KSTBaseModel
from datetime import datetime
from app.schemas.reservation import ReservationStatus

# 전체 예약목록 조회
class ReservationResponseSchema(KSTBaseModel):
    id: int
    user_id: int
    user_email: str
    user_name: str
    head_count: int
    status: ReservationStatus
    start_time: datetime
    end_time: datetime
    created_at : datetime
