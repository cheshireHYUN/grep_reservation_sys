from app.schemas.reservation import ReservationResponseSchema, ReservationStatus, ReservationUpdateSchema
from app.models import Reservation
from app.models.user import User
from app.models.time_slot import TimeSlot
from app.models.reservation_time_slot import ReservationTimeSlot
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import delete, select, and_
from fastapi import HTTPException
from app.config.config import MAX_HEADCOUNT

# Reservation -> ReservationResponseSchema응답으로 바꿔주는 유틸
def create_reservation_response(reservation: Reservation, user: User) -> ReservationResponseSchema:
    return ReservationResponseSchema(
        id=reservation.id,
        name=user.name,
        head_count=reservation.head_count,
        start_time=reservation.start_time,
        end_time=reservation.end_time,
        status=ReservationStatus.CONFIRMED if reservation.is_confirmed else ReservationStatus.PENDING,
        created_at=reservation.created_at
    )

# 부분 업데이트를 위한 처리 유틸
def update_reservation_fields(reservation: Reservation, update_data: ReservationUpdateSchema):
    if update_data.start_time is not None:
        reservation.start_time = update_data.start_time
    if update_data.end_time is not None:
        reservation.end_time = update_data.end_time
    if update_data.head_count is not None:
        reservation.head_count = update_data.head_count

# 타임슬롯 유효성을 검사하는 유틸
def validate_and_get_time_slots(
    db: Session,
    start_time,
    end_time,
    head_count: int) -> list[TimeSlot]:

    if (start_time.date() - date.today()).days < 3:
        raise HTTPException(status_code=400, detail="예약은 최소 3일전까지만 신청 및 수정이 가능합니다.")

    time_slots = db.execute(
        select(TimeSlot).where(
            and_(
                TimeSlot.start_time >= start_time,
                TimeSlot.end_time <= end_time,
            )
        )
    ).scalars().all()

    expected_count = int((end_time - start_time).total_seconds() // 3600)
    if not time_slots or len(time_slots) < expected_count:
        raise HTTPException(status_code=404, detail="신청 불가능한 시간이 포함되어 있습니다.")

    # 인원 초과 확인
    for slot in time_slots:
        available = MAX_HEADCOUNT - slot.confirmed_headcount
        if available < head_count:
            raise HTTPException(status_code=400, detail=f"{slot.start_time} ~ {slot.end_time} 는 {available}명 이하까지만 신청 가능합니다.")

    return time_slots


# 타임슬롯에 예약인원을 반영하고 관계를 저장하는 유틸
def apply_reservation_to_slots(
    db: Session,
    reservation_id: int,
    time_slots: list[TimeSlot],
    head_count: int):

    for slot in time_slots:
        slot.confirmed_headcount += head_count
        db.add(ReservationTimeSlot(
            reservation_id=reservation_id,
            time_slot_id=slot.id
        ))

# 기존 예약의 타임슬롯을 초기화하고, 인원수도 차감하는 유틸
def remove_reservation_from_slots(
    db: Session,
    reservation: Reservation):

    old_slots = db.execute(
        select(TimeSlot).join(ReservationTimeSlot)
        .where(ReservationTimeSlot.reservation_id == reservation.id)
    ).scalars().all()

    for slot in old_slots:
        slot.confirmed_headcount -= reservation.head_count

    db.execute(
        delete(ReservationTimeSlot).where(ReservationTimeSlot.reservation_id == reservation.id)
    )