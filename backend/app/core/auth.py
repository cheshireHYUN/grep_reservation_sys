from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
import jwt
from app.config.config import SECRET_KEY

ALGORITHM = "HS256"

def get_current_user(
    db: Session = Depends(get_db),
    authorization: str = Header(None)
) -> User:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    token = authorization.replace("Bearer ", "")
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(decoded)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalid")

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

def create_access_token(user_id: int):
    to_encode = {"sub": str(user_id)} 
    to_encode.update({"exp": datetime.now() + timedelta(days=365)}) #임의로그인이므로 1년으로 지정
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt