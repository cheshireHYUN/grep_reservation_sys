# 시험일정 예약 시스템 API
시험 일정 예약을 위한 FastAPI 기반 RESTful API입니다.

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

(CF) postman / 자세한 API 문서
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

</br></br>

## 테스트 방법
(1) 제일 먼저, 로그인 API를 실행합니다.
- 현재 임시로그인 형태입니다.
- User가 사용하는 API들은 헤더의 Authorization 액세스토큰을 파싱하여 로그인중인 유저를 판단합니다. 따라서 로그인 API를 가장 먼저 실행후 응답으로 오는 액세스토큰값을 활용하여 나머지 API를 테스트 할 수 있습니다.

(2) 어드민 API는 토큰이 필요하지 않습니다. 따라서 (1)을 진행한 뒤엔 어드민과 고객 API를 자유롭게 테스트 할 수 있습니다.

</br>

(CF)
- 마이그레이션시 일정기간의 time_slot이 자동생성됩니다.
- 예약이 정각단위로만 가능하다는 전제하에 구성했습니다.
- 요구사항을 구체화하여, 확정된 예약의 경우 고객/어드민 모두 수정이 불가하지만 어드민의 삭제는 가능하다는 전제 하에 구현했습니다.


</br></br>

## 사용기술
- Language : Python 3.13.2
- Framework : fastAPI 0.115.12(latest)
- Database : PostgreSQL 1.4-1
- ETC : unicorn, SQLAlchemy, alembic, python-dotenv

</br></br>

## 데이터베이스 설계
![Image](https://github.com/user-attachments/assets/6229808f-1bc0-439b-b23f-b831100fb169)

</br></br>

## 고민했던점
- 각 시간대별 예약을 위해서 하루를 한시간단위로 쪼개 저장하는 TimeSlot을 만들어 Reservation을 처리.
- 확장성을 위해 백엔드, DB에서 모든 날짜를 UTC로 변환하여 사용.
- 여러 어드민이 동시에 같은 TimeSlot에 접근할 경우를 상정하여 낙관적 락을 적용.
- 목록 조회 API는 페이징 처리.
- soft delete를 활용
- 로그인은 JWT를 통해 임시로그인 구현(권한처리X, 로그인객체가 필요한 로직인 고객API에 대하여 Access-token을 기준으로 백엔드 로직 구현).

</br></br>

## 디렉토리 구조
```
BACKEND/
│
├── app/                             # 애플리케이션 메인 디렉토리
│   ├── api/                         # API 엔드포인트 관련 모듈
│   │   └── v1/                      
│   │       ├── endpoints/          # API endpoint 라우터
│   │       │   ├── admin_reservation.py
│   │       │   ├── reservation.py
│   │       │   └── user.py
│   │       └── routers.py          # 라우터 설정
│   │
│   ├── config/                      # 환경설정 관련 모듈(MAX_COUNT 등)
│   │   └── config.py
│   │
│   ├── core/                        # CRUD외 필요한 로직 (JWT 등)
│   │
│   ├── crud/                        # CRUD 로직(비즈니스 레이어)
│   │   ├── admin_reservation.py
│   │   └── reservation.py
│   │
│   ├── db/                          # DB 연결 및 세션 관리
│
│   ├── exception/                   # 예외 처리 모듈
│
│   ├── models/                      # SQLAlchemy 모델 정의
│
│   ├── schemas/                     # Pydantic 스키마 정의
│
│   └── main.py                      # 앱 실행 진입점
│
├── venv/                            # 가상환경 디렉토리
│
├── .env                             # 환경 변수 파일(로컬환경에서 각자 추가 필요)
├── .gitignore                       
├── alembic.ini                      # Alembic 설정 파일 (마이그레이션)
└── requirements.txt                 # 프로젝트 의존성 목록
```




