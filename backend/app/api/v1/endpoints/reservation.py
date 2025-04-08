from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.reservation import ReservationCreateSchema, ReservationResponseSchema, ReservationUpdateSchema
from app.schemas.time_slot import TimeSlotSchema
from app.crud.reservation import create_reservation, get_available_times, get_reservations_by_user, update_reservation

router = APIRouter()

@router.get("/available-times", response_model=List[TimeSlotSchema], summary="예약 가능한 시간 조회")
def get_available_times_api(db: Session = Depends(get_db)):
    available_times = get_available_times(db)

    if not available_times:
        raise HTTPException(status_code=404, detail="예약가능한 시간이 존재하지 않음")
    
    return available_times

@router.post("", response_model=ReservationResponseSchema, summary="예약 신청")
def create_reservation(req: ReservationCreateSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    reservation = create_reservation(db, req, user)
    return reservation

@router.get("", response_model=List[ReservationResponseSchema], summary="예약한 목록 조회")
def get_reservations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    reservations = get_reservations_by_user(db, user)
    return reservations

@router.patch("/{reservation_id}", response_model=ReservationResponseSchema, summary="예약 수정")
def update_reservation(
    reservation_id: int,
    req: ReservationUpdateSchema,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)):
    
    updated_reservation = update_reservation(db, reservation_id, user, req)

    return updated_reservation

