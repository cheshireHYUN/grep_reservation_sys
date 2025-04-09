from sqlalchemy.orm import Session, joinedload
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy import and_, delete, select
from app.crud.reservation import create_reservation_response
from app.models import Reservation, TimeSlot
from app.config.config import MAX_HEADCOUNT
from app.config.config import MAX_HEADCOUNT
from app.models.reservation_time_slot import ReservationTimeSlot
from app.models.user import User
from app.schemas.reservation import ReservationStatus, ReservationUpdateSchema
from app.schemas.admin_reservation import ReservationResponseSchema
from fastapi import HTTPException
from datetime import date, datetime

# 전체예약목록 조회
def get_all_reservations_for_admin(db: Session):
    results = db.execute(
        select(Reservation, User)
        .join(User, Reservation.user_id == User.id)
        .where(Reservation.deleted_at.is_(None))
        .order_by(Reservation.created_at)
    ).all()

    return [
        ReservationResponseSchema(
            id=reservation.id,
            user_id=reservation.user_id,
            user_email=user.email,
            user_name=user.name,
            head_count=reservation.head_count,
            status=ReservationStatus.CONFIRMED if reservation.is_confirmed else ReservationStatus.PENDING,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
            created_at=reservation.created_at,
        )
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
        if timeslot.confirmed_headcount + reservation.head_count > MAX_HEADCOUNT:
            raise HTTPException(
                status_code=400,
                detail=f"[{timeslot.id}] {timeslot.start_time}~{timeslot.end_time} 시간대의 예약 인원이 50,000명을 초과합니다."
            )
        
    try:
        for rts in reservation.reservation_time_slots:
            rts.time_slot.confirmed_headcount += reservation.head_count

        reservation.is_confirmed = True

    except StaleDataError:
        # 여러 관리자 동시 수정시 에러
        db.rollback()
        raise HTTPException(status_code=409, detail="다른 관리자에 의해 예약이 먼저 확정되었습니다. 다시 시도해주세요.")
        


# 예약 수정
def update_reservation_by_admin(
    db: Session,
    reservation_id: int,
    req: ReservationUpdateSchema):

    reservation = db.execute(
        select(Reservation).where(
            and_(
                Reservation.id == reservation_id,
                Reservation.deleted_at == None
            )
        )
    ).scalar_one_or_none()

    if reservation is None:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다.")
    
    if reservation.is_confirmed:
        raise HTTPException(status_code=404, detail="확정된 예약은 수정할 수 없습니다. 먼저 확정을 취소한 후 다시 시도해주세요.")
    
    # 기존 데이터 삭제
    remove_reservation_from_slots(db,reservation)

    # 수정할 필드를 반영
    update_reservation_fields(reservation, req)

    # 새로운 타임슬롯 등록
    new_slots = validate_and_get_time_slots(db, reservation.start_time, reservation.end_time, reservation.head_count)
    apply_reservation_to_slots(db, reservation, new_slots)

    return create_reservation_response(reservation, reservation.user)


# 예약 삭제
def delete_reservation_by_admin(db: Session, reservation_id: int):
    reservation = db.execute(
        select(Reservation)
        .options(
            joinedload(Reservation.reservation_time_slots).joinedload(ReservationTimeSlot.time_slot)
        )
        .where(Reservation.id == reservation_id, Reservation.deleted_at.is_(None))
    ).unique().scalar_one_or_none() 

    if not reservation:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다.")

    if reservation.is_confirmed:
        for rts in reservation.reservation_time_slots:
            rts.time_slot.confirmed_headcount -= reservation.head_count

    reservation.deleted_at = datetime.now()


# 확정 취소
def cancel_confirm_reservation_by_admin(db: Session, reservation_id: int):
    reservation = db.execute(
        select(Reservation)
        .options(
            joinedload(Reservation.reservation_time_slots)
            .joinedload(ReservationTimeSlot.time_slot)
        )
        .where(
            Reservation.id == reservation_id,
            Reservation.deleted_at.is_(None)
        )
    ).unique().scalar_one_or_none()

    if reservation is None:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다.")

    if not reservation.is_confirmed:
        raise HTTPException(status_code=400, detail="이미 확정이 취소된 예약입니다.")

    for rts in reservation.reservation_time_slots:
        rts.time_slot.confirmed_headcount -= reservation.head_count
        if rts.time_slot.confirmed_headcount < 0:
            rts.time_slot.confirmed_headcount = 0 #오류방지

    reservation.is_confirmed = False

    return create_reservation_response(reservation, reservation.user)



# == Admin Util ==
def update_reservation_fields(reservation: Reservation, update_data: ReservationUpdateSchema):
    if update_data.start_time is not None:
        reservation.start_time = update_data.start_time
    if update_data.end_time is not None:
        reservation.end_time = update_data.end_time
    if update_data.head_count is not None:
        reservation.head_count = update_data.head_count

# 기존 타임슬롯매핑 삭제
def remove_reservation_from_slots(
    db: Session,
    reservation: Reservation):

    db.execute(
        delete(ReservationTimeSlot).where(ReservationTimeSlot.reservation_id == reservation.id)
    )

# 새로운 타임슬롯 유효성을 검사하고 리턴
def validate_and_get_time_slots(
    db: Session,
    start_time,
    end_time,
    head_count: int) -> list[TimeSlot]:

    # 어드민은 3일 제한 없을것이라 판단함.
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

    for slot in time_slots:
        available = MAX_HEADCOUNT - slot.confirmed_headcount
        if available < head_count:
            raise HTTPException(status_code=400, detail=f"{slot.start_time} ~ {slot.end_time} 는 {available}명 이하까지만 신청 가능합니다.")

    return time_slots

# 예약과 타임슬롯 연관관계를 새로 저장하는 유틸
def apply_reservation_to_slots(
    db: Session,
    reservation: Reservation,
    time_slots: list[TimeSlot]):

    for slot in time_slots:
        db.add(ReservationTimeSlot(
            reservation_id=reservation.id,
            time_slot_id=slot.id
        ))

