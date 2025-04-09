from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.reservation import Reservation
from app.models.time_slot import TimeSlot
from app.models.user import User
from app.models.reservation_time_slot import ReservationTimeSlot