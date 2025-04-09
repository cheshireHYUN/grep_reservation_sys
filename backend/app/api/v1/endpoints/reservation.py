from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth import get_current_user
from app.exception.api_exception import APIException
from app.models.user import User
from app.schemas.reservation import PagingReservationResponseSchema
from app.schemas.reservation import ReservationCreateSchema, ReservationResponseSchema, ReservationUpdateSchema
from app.schemas.time_slot import PaginationTimeSlotResponseSchema, TimeSlotResponseSchema
import app.crud.reservation as reservation_service
from app.schemas.api_response import APIResponse, success_response

router = APIRouter()

@router.get("/available-times", response_model=APIResponse[PaginationTimeSlotResponseSchema], summary="예약 가능한 시간 조회", description="3일 이후의 예약가능 시간을 조회합니다.")
def get_available_times_api(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)):
    data = reservation_service.get_available_times(db, page, page_size)
    
    return success_response(data)

@router.post("", response_model=APIResponse[ReservationResponseSchema], summary="예약 신청", description="날짜범위를 입력하여 예약을 신청합니다.")
def create_reservation(req: ReservationCreateSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    reservation = reservation_service.create_reservation(db, req, user)
    return success_response(reservation)

@router.get("", response_model=APIResponse[PagingReservationResponseSchema], summary="예약한 목록 조회", description="로그인한 유저의 예약목록을 신청순으로 조회합니다.")
def get_reservations(
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)):
    reservations = reservation_service.get_reservations_by_user(db, user, page, page_size)
    return success_response(reservations)

@router.patch("/{reservation_id}", response_model=APIResponse[ReservationResponseSchema], summary="예약 수정", description="인원수 또는 날짜를 입력해 예약을 수정합니다.")
def update_reservation(
    reservation_id: int,
    req: ReservationUpdateSchema,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)):
    
    updated_reservation = reservation_service.update_reservation(db, reservation_id, user, req)

    return success_response(updated_reservation)

@router.delete("/{reservation_id}", response_model=APIResponse[None], summary="예약 삭제", description="예약을 삭제합니다.")
def delete_reservation_api(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)):

    reservation_service.delete_reservation(db, reservation_id, user)
    return success_response(message="예약이 삭제 되었습니다.")
