from sqlalchemy.orm import Session
from sqlalchemy import and_, delete, select
from app.models import Reservation, TimeSlot
from app.config.config import MAX_HEADCOUNT
from app.models.reservation_time_slot import ReservationTimeSlot
from app.models.user import User
from app.schemas.time_slot import TimeSlotSchema
from app.schemas.reservation import ReservationCreateSchema, ReservationResponseSchema, ReservationStatus, ReservationUpdateSchema
from fastapi import HTTPException
from datetime import date
from app.core.reservation_utils import create_reservation_response, remove_reservation_from_slots, update_reservation_fields, validate_and_get_time_slots, apply_reservation_to_slots

# 예약 가능한 시간을 조회
def get_available_times(db: Session):
    time_slots = db.query(TimeSlot).filter(
        (MAX_HEADCOUNT - TimeSlot.confirmed_headcount) > 0
    ).all()

    available_times = []
    for time_slot in time_slots:
        available_times.append(TimeSlotSchema(
            start_time = time_slot.start_time,
            end_time = time_slot.end_time,
            available_headcount = MAX_HEADCOUNT - time_slot.confirmed_headcount
        ))
    
    return available_times


# 예약 신청
def create_reservation(db: Session, req: ReservationCreateSchema, user:User):

    time_slots = validate_and_get_time_slots(db, req.start_time, req.end_time, req.head_count)

    reservation = Reservation(
        start_time=req.start_time,
        end_time=req.end_time,
        head_count=req.head_count,
        user_id=user.id
    )
    db.add(reservation)
    db.flush()  # ID 필요

    apply_reservation_to_slots(db, reservation.id, time_slots, req.head_count)
    db.commit()

    return create_reservation_response(reservation, user)


# 예약 목록 조회
def get_reservations_by_user(db: Session, user: User):
    result = db.execute(
        select(Reservation)
        .where(Reservation.user_id == user.id)
        .order_by(Reservation.start_time)
    ).scalars().all()

    reservations = []
    for reservation in result:
        reservations.append(create_reservation_response(reservation, user))
    
    return reservations

# 예약 수정
def update_reservation(
    db: Session,
    reservation_id: int,
    user: User,
    req: ReservationUpdateSchema):

    reservation = db.execute(
        select(Reservation).where(
            and_(
                Reservation.id == reservation_id,
                Reservation.user_id == user.id
            )
        )
    ).scalar_one_or_none()

    if reservation is None:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다.")

    if reservation.is_confirmed:
        raise HTTPException(status_code=400, detail="확정된 예약은 수정할 수 없습니다.")
    
    # 수정할 필드를 반영
    update_reservation_fields(reservation, req)

    # 기존 타임슬롯의 인원수, 관계 삭제
    remove_reservation_from_slots(db,reservation)

    # 새로운 타임슬롯 등록 및 카운트 증가
    new_slots = validate_and_get_time_slots(db, reservation.start_time, reservation.end_time, reservation.head_count)
    apply_reservation_to_slots(db, reservation_id, new_slots, reservation.head_count)

    db.commit()

    return create_reservation_response(reservation, user)