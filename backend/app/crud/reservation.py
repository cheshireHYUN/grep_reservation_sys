from sqlalchemy.orm import Session
from app.models.timeslot import TimeSlot
from app.config.config import MAX_HEADCOUNT
from app.schemas.reservation import TimeSlotSchema

def get_available_times(db: Session):
    time_slots = db.query(TimeSlot).filter(
        (MAX_HEADCOUNT - TimeSlot.confirmed_headcount) > 0
    ).all()

    available_times = []
    for time_slot in time_slots:
        available_times.append(TimeSlotSchema(
            start_time = time_slot.start_time,
            end_time = time_slot.end_time,
            available_headcount = MAX_HEADCOUNT - time_slot.confirmed_headcount
        ))
    
    return available_times
