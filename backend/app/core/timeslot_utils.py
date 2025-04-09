from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.time_slot import TimeSlot

# 약 한달 후 까지 타임슬롯을 계산한 뒤, 부족한 슬롯이 있다면 생성
def generate_timeslots(db: Session, days_ahead: int = 30):
    now = datetime.now()
    start = now + timedelta(days=3)
    end = now + timedelta(days=days_ahead)

    curr = datetime(start.year, start.month, start.day, 0, 0, 0)
    while curr < end:
        end_time = curr + timedelta(hours=1)
        exists = db.query(TimeSlot).filter_by(start_time=curr, end_time=end_time).first()
        if not exists:
            slot = TimeSlot(start_time=curr, end_time=end_time)
            db.add(slot)
        curr = end_time

    db.commit()
