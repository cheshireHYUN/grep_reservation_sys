from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
import app.crud.admin_reservation as admin_service
from app.schemas.admin_reservation import PagingReservationResponseSchema
from app.schemas.api_response import APIResponse, success_response
from app.schemas.reservation import ReservationUpdateSchema

router = APIRouter()

@router.get("", response_model=APIResponse[PagingReservationResponseSchema], summary="전체 예약 리스트 조회", description="전체 예약 리스트를 생성순서대로 조회합니다.")
def get_all_reservations_for_admin(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)):
    return success_response(admin_service.get_all_reservations_for_admin(db,page,page_size))

@router.post("/{reservation_id}/confirmation", response_model=APIResponse[None], summary="예약 확정", description="예약을 확정합니다.")
def confirm_reservation(reservation_id: int, db: Session = Depends(get_db)):
    admin_service.confirm_reservation_by_admin(db, reservation_id)
    return success_response(message="예약이 확정 되었습니다.")

@router.patch("/{reservation_id}", summary="예약 수정", response_model=APIResponse[ReservationUpdateSchema], description="인원수나 날짜를 입력해 예약을 수정합니다. 확정된 예약은 수정이 불가능합니다.")
def update_reservation(reservation_id: int, request: ReservationUpdateSchema, db: Session = Depends(get_db)):
    return success_response(admin_service.update_reservation_by_admin(db, reservation_id, request))

@router.delete("/{reservation_id}/confirmation", response_model=APIResponse[None], summary="예약 확정 취소", description="예약확정을 취소합니다.")
def cancel_confirm_reservation(reservation_id: int, db: Session = Depends(get_db)):
    admin_service.cancel_confirm_reservation_by_admin(db, reservation_id)
    return success_response(message="예약 확정이 취소되었습니다.")

@router.delete("/{reservation_id}", response_model=APIResponse[None], summary="예약 삭제 (soft delete)", description="확정여부와 관계없이 예약을 삭제합니다.")
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    admin_service.delete_reservation_by_admin(db, reservation_id)
    return success_response(message="예약이 삭제 되었습니다.")
