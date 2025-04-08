from sqlalchemy import Column, Integer, ForeignKey, Table
from app.db.base import Base

# reservation:time_slot의 N:M관계를 연결하는 중간테이블
reservation_time_slot_table = Table(
    "reservation_time_slot",
    Base.metadata,
    Column("reservation_id", ForeignKey("reservation.id"), primary_key=True),
    Column("time_slot_id", ForeignKey("time_slot.id"), primary_key=True),
)
