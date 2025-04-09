"""Add test data to time_slot

Revision ID: 963fd8085c2c
Revises: 0170b535a75c
Create Date: 2025-04-09 23:00:38.393426

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '963fd8085c2c'
down_revision: Union[str, None] = '0170b535a75c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # 기존 테이블 및 컬럼 생성 코드 (자동 생성된 경우 생략)
    
    # 테스트 데이터 삽입
    op.execute("""
    WITH dates AS (
        SELECT generate_series(
            '2025-04-10'::date,
            '2025-04-20'::date,
            INTERVAL '1 day'
        ) AS date
    ),
    hours AS (
        SELECT generate_series(9, 17) AS hour
    )
    INSERT INTO time_slot (start_time, end_time, confirmed_headcount)
    SELECT 
        make_timestamp(
            EXTRACT(YEAR FROM d.date)::int,
            EXTRACT(MONTH FROM d.date)::int,
            EXTRACT(DAY FROM d.date)::int,
            h.hour,
            0,
            0
        ) AS start_time,
        make_timestamp(
            EXTRACT(YEAR FROM d.date)::int,
            EXTRACT(MONTH FROM d.date)::int,
            EXTRACT(DAY FROM d.date)::int,
            h.hour + 1,
            0,
            0
        ) AS end_time,
        0 AS confirmed_headcount
    FROM dates d
    CROSS JOIN hours h;
    """)

def downgrade():
    # 데이터를 삭제하려면 적절한 SQL을 사용
    op.execute("DELETE FROM time_slot WHERE start_time >= '2025-04-10' AND start_time <= '2025-04-20';")