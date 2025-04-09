from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.v1.routers import router as api_router
from app.db.session import SessionLocal
from app.models.user import User
from app.exception.api_exception import APIException
from fastapi import status

app = FastAPI(
    title="[grep] 시험일정 예약 시스템 API",
    description="시험일정 예약 시스템 API 명세입니다.",
    version="1.0.0")

app.include_router(api_router, prefix="/api/v1")

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "httpStatus": exc.status_code,
            "data": None,
            "message": exc.message
        }
    )