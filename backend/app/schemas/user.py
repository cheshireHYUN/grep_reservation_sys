from pydantic import BaseModel

# 유저 등록 요청 스키마
class UserCreate(BaseModel):
    email: str
    name: str
    
    class Config:
        from_attributes = True