from enum import Enum

# 예약 상태
class ReservationStatus(str, Enum):
    PENDING = "보류중"
    CONFIRMED = "확정됨"