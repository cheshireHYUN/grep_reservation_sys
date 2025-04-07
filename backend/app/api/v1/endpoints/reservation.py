from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.reservation import TimeSlotSchema
from app.crud.reservation import get_available_times

router = APIRouter()

@router.get("/available-times", response_model=List[TimeSlotSchema])
def get_available_times_api(db: Session = Depends(get_db)):
    available_times = get_available_times(db)

    if not available_times:
        raise HTTPException(status_code=404, detail="No available times found")
    
    return available_times