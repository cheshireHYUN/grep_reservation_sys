from sqlalchemy.orm import Session
from sqlalchemy import and_, delete, func, select
from app.exception.api_exception import APIException
from app.models import Reservation, TimeSlot
from app.config.config import MAX_HEADCOUNT
from app.models.reservation_time_slot import ReservationTimeSlot
from app.models.user import User
from app.schemas.reservation import PagingReservationResponseSchema
from app.schemas.time_slot import PaginationTimeSlotResponseSchema, TimeSlotResponseSchema
from app.schemas.reservation import ReservationCreateSchema, ReservationResponseSchema, ReservationStatus, ReservationUpdateSchema
from datetime import date, datetime, timedelta

# 예약 가능한 시간을 조회
def get_available_times(db: Session, page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size
    three_days_later = datetime.now().date() + timedelta(days=3)

    time_slots = db.execute(
        select(TimeSlot)
        .where(TimeSlot.start_time >= three_days_later)
        .order_by(TimeSlot.start_time)
        .limit(page_size)
        .offset(offset)
    ).scalars().all()

    total_count = db.execute(
        select(func.count(TimeSlot.id))
        .where(Reservation.deleted_at.is_(None))
    ).scalar()

    pagination = {
        "page": page,
        "page_size": page_size,
        "total_items": total_count,
        "total_pages": (total_count + page_size - 1) // page_size  # 총 페이지 수 계산
    }

    available_times = [
        TimeSlotResponseSchema(
            id = time_slot.id, 
            start_time = time_slot.start_time,
            end_time = time_slot.end_time,
            is_reservable= MAX_HEADCOUNT > time_slot.confirmed_headcount,
            available_headcount = MAX_HEADCOUNT - time_slot.confirmed_headcount,
        )
        for time_slot in time_slots
    ]

    return PaginationTimeSlotResponseSchema(
        pagination = pagination,
        time_slots = available_times
    )


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
    db.flush()

    apply_reservation_to_slots(db, reservation.id, time_slots)

    return create_reservation_response(reservation, user)


# 예약 목록 조회
def get_reservations_by_user(db: Session, user: User, page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size

    result = db.execute(
        select(Reservation)
        .where(
            and_(
                Reservation.user_id == user.id,
                Reservation.deleted_at == None
            )
        )
        .order_by(Reservation.created_at)
        .offset(offset)
        .limit(page_size)
    ).scalars().all()

    total_count = db.execute(
        select(func.count(Reservation.id))
        .where(
            and_(
                Reservation.user_id == user.id,
                Reservation.deleted_at == None
            )
        )
    ).scalar()

    pagination = {
        "page": page,
        "page_size": page_size,
        "total_items": total_count,
        "total_pages": (total_count + page_size - 1) // page_size  # 총 페이지 수 계산
    }


    reservations = []
    for reservation in result:
        reservations.append(create_reservation_response(reservation, user))
    
    return PagingReservationResponseSchema(
        reservations = reservations,
        pagination = pagination )


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
                Reservation.user_id == user.id,
                Reservation.deleted_at == None
            )
        )
    ).scalar_one_or_none()

    if reservation is None:
        raise APIException(status_code=404, message="예약을 찾을 수 없습니다.")

    if reservation.is_confirmed:
        raise APIException(status_code=400, message="확정된 예약은 수정할 수 없습니다.")
    
    # 기존 타임슬롯 관계 삭제
    remove_reservation_from_slots(db,reservation)
    
    # 수정할 필드를 반영
    update_reservation_fields(reservation, req)

    # 새로운 타임슬롯 검사 및 생성
    new_slots = validate_and_get_time_slots(db, reservation.start_time, reservation.end_time, reservation.head_count)
    apply_reservation_to_slots(db, reservation_id, new_slots)

    return create_reservation_response(reservation, user)


# 예약 삭제
def delete_reservation(
    db: Session,
    reservation_id: int,
    user: User):
    reservation = db.execute(
        select(Reservation).where(
            and_(
                Reservation.id == reservation_id,
                Reservation.user_id == user.id,
                Reservation.deleted_at == None
            )
        )
    ).scalar_one_or_none()

    if reservation is None:
        raise APIException(status_code=404, message="예약을 찾을 수 없습니다.")

    if reservation.is_confirmed:
        raise APIException(status_code=400, message="확정된 예약은 삭제할 수 없습니다.")

    # 기존 예약 타임슬롯 관계 삭제
    remove_reservation_from_slots(db, reservation)

    # soft delete
    reservation.deleted_at = datetime.now()


# == User Util ==

# 부분 업데이트를 위한 처리 유틸
def update_reservation_fields(reservation: Reservation, update_data: ReservationUpdateSchema):
    if update_data.start_time is not None:
        reservation.start_time = update_data.start_time
    if update_data.end_time is not None:
        reservation.end_time = update_data.end_time
    if update_data.head_count is not None:
        reservation.head_count = update_data.head_count

# 타임슬롯 유효성을 검사하고 리턴
def validate_and_get_time_slots(
    db: Session,
    start_time,
    end_time,
    head_count: int) -> list[TimeSlot]:

    if (start_time.date() - date.today()).days < 3:
        raise APIException(status_code=400, message="예약은 최소 3일전까지만 신청 및 수정이 가능합니다.")

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
        raise APIException(status_code=404, message="신청 불가능한 시간이 포함되어 있습니다.")

    # 인원 초과 확인
    for slot in time_slots:
        available = MAX_HEADCOUNT - slot.confirmed_headcount
        if available < head_count:
            raise APIException(status_code=400, message=f"{slot.start_time} ~ {slot.end_time} 는 {available}명 이하까지만 신청 가능합니다.")

    return time_slots


# 타임슬롯과 예약의 연관관계를 새로 저장하는 유틸
def apply_reservation_to_slots(
    db: Session,
    reservation_id: int,
    time_slots: list[TimeSlot]):

    for slot in time_slots:
        db.add(ReservationTimeSlot(
            reservation_id=reservation_id,
            time_slot_id=slot.id
        ))

# 기존 예약의 타임슬롯을 삭제하는 유틸
def remove_reservation_from_slots(
    db: Session,
    reservation: Reservation):

    db.execute(
        delete(ReservationTimeSlot).where(ReservationTimeSlot.reservation_id == reservation.id)
    )

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

