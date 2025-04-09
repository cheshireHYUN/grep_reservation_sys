from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import create_access_token
from app.db.session import SessionLocal, get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post("", response_model=UserResponse, summary="임시 회원가입", description="액세스토큰을 반환한다.")
def register_user(req: UserCreate, db: Session = Depends(get_db)):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        db.close()
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(email=req.email, name=req.name)
    db.add(user)
    db.commit()
    db.refresh(user)

    # 액세스 토큰 생성
    return UserResponse(access_token=create_access_token(user.id))

