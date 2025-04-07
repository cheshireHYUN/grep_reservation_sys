from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

# TimeSlot(시간) 테이블
class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    confirmed_headcount = Column(Integer, default=0, nullable=False)

    #TimeSlot:reservation = 1:N
    reservations = relationship("Reservation", back_populates="time_slot")