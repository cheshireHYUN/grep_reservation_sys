from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.reservation import ReservationCreateSchema, ReservationResponseSchema
from app.schemas.time_slot import TimeSlotSchema
from app.crud.reservation import create_reservation, get_available_times

router = APIRouter()

@router.get("/available-times", response_model=List[TimeSlotSchema], summary="예약 가능한 시간 조회")
def get_available_times_api(db: Session = Depends(get_db)):
    available_times = get_available_times(db)

    if not available_times:
        raise HTTPException(status_code=404, detail="No available times found")
    
    return available_times

@router.post("/", response_model=ReservationResponseSchema, summary="예약 신청")
def make_reservation(req: ReservationCreateSchema, db: Session = Depends(get_db)):
    reservation = create_reservation(db, req)
    return reservation