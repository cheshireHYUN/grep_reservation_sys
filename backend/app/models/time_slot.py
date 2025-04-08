from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.reservation_time_slot import reservation_time_slot_table

# TimeSlot(시간) 테이블
class TimeSlot(Base):
    __tablename__ = "time_slot"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    confirmed_headcount = Column(Integer, default=0, nullable=False)

    reservations = relationship(
        "Reservation",
        secondary=reservation_time_slot_table,
        back_populates="time_slots"
    )