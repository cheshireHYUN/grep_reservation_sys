from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import reservation_time_slot
from app.models.time_slot import TimeSlot
from app.models.reservation import Reservation
from app.config.config import MAX_HEADCOUNT
from app.schemas.time_slot import TimeSlotSchema
from app.schemas.reservation import ReservationCreateSchema
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone

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
def create_reservation(db: Session, req: ReservationCreateSchema):
    # 시험 시작 최소 3일 전인지 검사
    if (req.start_time - datetime.now(timezone.utc)) < timedelta(days=3):
        raise HTTPException(status_code=400, detail="예약은 최소 3일전 까지만 가능합니다.")

    time_slots = db.query(TimeSlot).filter(
        and_(
            TimeSlot.start_time >= req.start_time,
            TimeSlot.end_time <= req.end_time,
        )
    ).all()

    # 타임슬롯 존재 여부 및 개수 확인 (예: 3시간 신청했는데 3개 미만일 경우 오류)
    expected_slot_count = int((req.end_time - req.start_time).total_seconds() // 3600)
    if not time_slots or len(time_slots) < expected_slot_count:
        raise HTTPException(status_code=404, detail="신청 불가능한 시간이 포함되어 있습니다.")

    # 요청이 신청시각에 가능한 신청인원인지 검사
    for time_slot in time_slots:
        avaliable_head_count = MAX_HEADCOUNT - time_slot.confirmed_headcount
        if (avaliable_head_count < req.head_count):
            raise HTTPException(status_code=400, detail=f"{time_slot.start_time} ~ {time_slot.end_time} 는 {avaliable_head_count}명 이하까지만 신청 가능합니다.")

    # 예약정보 생성 및 TimeSlot에 신청인원 업데이트
    reservation = Reservation(
        company_name=req.company_name,
        start_time=req.start_time,
        end_time=req.end_time,
        head_count=req.head_count
    )
    db.add(reservation)
    db.flush()

    for time_slot in time_slots:
        time_slot.confirmed_headcount += req.head_count #변경감지?
        db.add(reservation_time_slot(
            reservation_id=reservation.id,
            time_slot_id=time_slot.id
        ))

    db.commit()
    db.refresh(reservation)
    return reservation