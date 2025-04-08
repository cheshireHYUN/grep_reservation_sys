from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth import get_current_user
import app.crud.admin_reservation as admin_service
from app.schemas.admin_reservation import AllReservationResponseSchema

router = APIRouter()

@router.get("", response_model=List[AllReservationResponseSchema], summary="전체 예약 리스트 조회")
def get_all_reservations_for_admin(db: Session = Depends(get_db)):
    return admin_service.get_all_reservations_for_admin(db)

@router.patch("/{reservation_id}/confirm", summary="예약 확정")
def confirm_reservation(reservation_id: int, db: Session = Depends(get_db)):
    admin_service.confirm_reservation_by_admin(db, reservation_id)
    return {"msg": "예약이 확정되었습니다."}
