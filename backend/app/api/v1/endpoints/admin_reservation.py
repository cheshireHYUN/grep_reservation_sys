from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth import get_current_user
import app.crud.admin_reservation as admin_service
from app.schemas.admin_reservation import AllReservationResponseSchema
from app.schemas.reservation import ReservationUpdateSchema

router = APIRouter()

@router.get("", response_model=List[AllReservationResponseSchema], summary="전체 예약 리스트 조회")
def get_all_reservations_for_admin(db: Session = Depends(get_db)):
    return admin_service.get_all_reservations_for_admin(db)

@router.post("/{reservation_id}/confirmation", summary="예약 확정")
def confirm_reservation(reservation_id: int, db: Session = Depends(get_db)):
    admin_service.confirm_reservation_by_admin(db, reservation_id)
    return {"msg": "예약이 확정되었습니다."}

@router.patch("/{reservation_id}", summary="예약 수정")
def update_reservation(reservation_id: int, request: ReservationUpdateSchema, db: Session = Depends(get_db)):
    return admin_service.update_reservation_by_admin(db, reservation_id, request)

@router.delete("/{reservation_id}/confirmation", summary="예약 확정 취소")
def cancel_confirm_reservation(reservation_id: int, db: Session = Depends(get_db)):
    return admin_service.cancel_confirm_reservation_by_admin(db, reservation_id)