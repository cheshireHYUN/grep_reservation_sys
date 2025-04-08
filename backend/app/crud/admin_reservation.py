from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, delete, select
from app.models import Reservation, TimeSlot
from app.config.config import MAX_HEADCOUNT
from app.models.reservation_time_slot import ReservationTimeSlot
from app.models.user import User
from app.schemas.reservation import ReservationStatus
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

# 예약 확정
def confirm_reservation_by_admin(db: Session, reservation_id: int):
    reservation = db.execute(
        select(Reservation)
        .options(
            joinedload(Reservation.reservation_time_slots).joinedload(ReservationTimeSlot.time_slot)
        )
        .where(
            Reservation.id == reservation_id,
            Reservation.deleted_at.is_(None)
        )
    ).unique().scalar_one_or_none()

    if not reservation:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다.")

    if reservation.is_confirmed:
        raise HTTPException(status_code=400, detail="이미 확정된 예약입니다.")

    # 인원 초과 여부 확인
    for rts in reservation.reservation_time_slots:
        timeslot = rts.time_slot
        if timeslot.confirmed_headcount + reservation.head_count > 50000:
            raise HTTPException(
                status_code=400,
                detail=f"[{timeslot.id}] {timeslot.start_time}~{timeslot.end_time} 시간대의 예약 인원이 50,000명을 초과합니다."
            )
        
    for rts in reservation.reservation_time_slots:
        rts.time_slot.confirmed_headcount += reservation.head_count
    reservation.is_confirmed = True

    db.commit()
    db.refresh(reservation)