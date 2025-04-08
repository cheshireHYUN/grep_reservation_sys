from fastapi import FastAPI
from app.api.v1.routers import router as api_router
from app.db.session import SessionLocal
from app.models.user import User

app = FastAPI(
    title="[grep] 시험일정 예약 시스템 API",
    description="시험일정 예약 시스템 API 명세입니다.",
    version="1.0.0")

app.include_router(api_router, prefix="/api/v1")
