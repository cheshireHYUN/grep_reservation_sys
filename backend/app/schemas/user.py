from pydantic import BaseModel, Field

# 유저 등록 요청 스키마
class UserCreate(BaseModel):
    email: str = Field(description="이메일(중복불가)")
    name: str = Field(description="기업명")
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    access_token: str = Field(description="임시 액세스토큰(JWT)")