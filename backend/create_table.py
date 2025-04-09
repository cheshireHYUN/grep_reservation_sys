from sqlalchemy import create_engine, insert
from app.db.base import Base
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import datetime as dt

from app.models.time_slot import TimeSlot

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# 모든 테이블 생성
Base.metadata.create_all(engine)
print(f"모든 테이블이 {DATABASE_URL}에 성공적으로 생성되었습니다.")

# 테스트 데이터 생성
def create_test_data():
    # 날짜 범위 생성 (2025-04-10부터 2025-04-20까지)
    start_date = dt.date(2025, 4, 10)
    end_date = dt.date(2025, 4, 20)
    
    # 데이터 저장할 리스트
    time_slots = []
    
    # 날짜별로 순회
    current_date = start_date
    while current_date <= end_date:
        # 시간별로 순회 (9시부터 17시까지)
        for hour in range(9, 18):
            # 시작 시간과 종료 시간 생성
            start_time = datetime.combine(current_date, dt.time(hour, 0))
            end_time = datetime.combine(current_date, dt.time(hour + 1, 0))
            
            # 데이터 객체 생성
            time_slot = {
                "start_time": start_time,
                "end_time": end_time,
                "confirmed_headcount": 0
            }
            
            time_slots.append(time_slot)
        
        # 다음 날짜로 이동
        current_date += timedelta(days=1)
    
    # insert() 생성
    insert_stmt = insert(TimeSlot).values(time_slots)
    
    # 데이터베이스에 insert 실행
    with engine.connect() as conn:
        conn.execute(insert_stmt)
        conn.commit()

create_test_data()
print("테스트 데이터가 성공적으로 생성되었습니다.")