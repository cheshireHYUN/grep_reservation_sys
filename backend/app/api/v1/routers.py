from fastapi import APIRouter
from app.api.v1.endpoints import admin_reservation, reservation, user

router = APIRouter()
router.include_router(reservation.router, prefix="/reservations", tags=["reservations"])
router.include_router(admin_reservation.router, prefix="/admin/reservations", tags=["admin"])
router.include_router(user.router, prefix="/user", tags=["user"])

