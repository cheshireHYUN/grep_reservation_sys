from app.schemas.reservation import ReservationResponseSchema, ReservationStatus
from app.models import Reservation
from app.models.user import User

def create_reservation_response(reservation: Reservation, user: User) -> ReservationResponseSchema:
    return ReservationResponseSchema(
        id=reservation.id,
        name=user.name,
        head_count=reservation.head_count,
        start_time=reservation.start_time,
        end_time=reservation.end_time,
        status=ReservationStatus.CONFIRMED if reservation.is_confirmed else ReservationStatus.PENDING,
        created_at=reservation.created_at
    )