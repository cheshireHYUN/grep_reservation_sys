from typing import Optional
from pydantic import Field
from typing import List
from app.schemas.pagination import Pagination
from app.schemas.base import KSTBaseModel
from datetime import datetime
from app.schemas.reservation import ReservationStatus

# 예약정보
class ReservationResponseSchema(KSTBaseModel):
    id: int = Field(description="예약ID")
    user_id: int
    user_email: str
    user_name: str
    head_count: int = Field(description="신청 인원수")
    status: ReservationStatus = Field(description="확정상태")
    start_time: datetime = Field(description="시작 시간")
    end_time: datetime = Field(description="종료 시간")
    created_at : datetime = Field(description="신청 시간")


# 전체 예약목록
class PagingReservationResponseSchema(KSTBaseModel):
    pagination : Pagination = Field(description="페이징 정보")
    reservations : List[ReservationResponseSchema]= Field(description="전체 예약 목록")
    

