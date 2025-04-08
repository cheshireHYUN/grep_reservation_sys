from sqlalchemy.orm import Session
from sqlalchemy import and_, delete, select
from app.models import Reservation, TimeSlot
from app.config.config import MAX_HEADCOUNT
from app.models.reservation_time_slot import ReservationTimeSlot
from app.models.user import User
from app.schemas.time_slot import TimeSlotSchema
from app.schemas.reservation import ReservationCreateSchema, ReservationResponseSchema, ReservationStatus, ReservationUpdateSchema
from fastapi import HTTPException
from datetime import date, datetime

# 전체예약목록 조회
def get_all_reservations_for_admin(db: Session):
    results = db.execute(
        select(Reservation, User)
        .join(User, Reservation.user_id == User.id)
        .where(Reservation.deleted_at.is_(None))
        .order_by(Reservation.start_time)
    ).all()

    return [
        {
            "id": reservation.id,
            "user_id": reservation.user_id,
            "user_email": user.email,
            "user_name": user.name,
            "head_count": reservation.head_count,
            "status": ReservationStatus.CONFIRMED if reservation.is_confirmed else ReservationStatus.PENDING,
            "start_time": reservation.start_time,
            "end_time": reservation.end_time,
            "created_at": reservation.created_at,
        }
        for reservation, user in results 
    ]