from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

# reservation:time_slot의 N:M관계를 연결하는 중간테이블
class ReservationTimeSlot(Base):
    __tablename__ = "reservation_time_slot"

    reservation_id = Column(Integer, ForeignKey("reservation.id"), primary_key=True)
    time_slot_id = Column(Integer, ForeignKey("time_slot.id"), primary_key=True)

    reservation = relationship("Reservation", back_populates="reservation_time_slots")
    time_slot = relationship("TimeSlot", back_populates="reservation_time_slots")
