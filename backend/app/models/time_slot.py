from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

# TimeSlot(시간) 테이블
class TimeSlot(Base):
    __tablename__ = "time_slot"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)
    confirmed_headcount = Column(Integer, default=0, nullable=False)
    version = Column(Integer, nullable=False, default=0)

    reservation_time_slots = relationship(
        "ReservationTimeSlot",
        back_populates="time_slot"
    )

    __mapper_args__ = {
        "version_id_col": version
    }