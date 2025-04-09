# 시험일정 예약 시스템 API
시험 일정 예약을 위한 FastAPI 기반 RESTful API입니다.
- DB/ 디렉토리 : 데이터베이스 관련 파일
- BACKEND/ 디렉토리 : FastAPI 개발물

</br></br>

## ⚙️ 환경 설정 (로컬 개발)

### 1. 가상환경 생성(권장)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수(.env) 추가
```bash
DATABASE_URL=postgresql://postgres:{password}@localhost:5432/exam_reservation  # 로컬 DB URL
```

### 4. 실행 방법
(1) 데이터베이스 마이그레이션
```bash
alembic upgrade head
```

(2) 서버 실행
```bash
uvicorn app.main:app --reload
```
(4) 로그인 API 실행

- 응답데이터의 access-token값을 Authorization 헤더에 Bearer+토큰값 형태로 저장하여 user관련 API 테스트.

(CF) postman / 자세한 API 문서
- Postman: 
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


</br></br>

## 사용기술
- Language : Python 3.13.2
- Framework : fastAPI 0.115.12(latest)
- Database : PostgreSQL 1.4-1
- ETC : unicorn, SQLAlchemy, alembic, python-dotenv

</br></br>

## 고민했던점
- 각 시간대별 예약을 위해서 하루를 한시간단위로 쪼개 저장하는 TimeSlot을 만들어 Reservation을 처리함
- 확장성을 위해 날짜는 백엔드, DB에서 UTC로 사용함
- 여러 어드민이 동시에 같은 TimeSlot에 접근할 경우를 상정하여 낙관적 락을 적용함
- 로그인은 JWT를 통해 임시로그인만 구현함(권한처리X, 로그인객체가 필요한 로직인 고객API에 대하여 Access-token을 기준으로 백엔드 로직을 처리함)






