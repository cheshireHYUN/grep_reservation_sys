from fastapi import APIRouter
from app.api.v1.endpoints import reservation

router = APIRouter()
router.include_router(reservation.router, prefix="/reservations", tags=["reservations"])
