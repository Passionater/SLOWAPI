# schemas.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    provider: str

    class Config:
        from_attributes = True # SQLAlchemy 모델을 Pydantic 모델로 변환
        
        
        
# schemas.py (파일 하단에 추가)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# schemas.py (파일 하단에 추가)

# KakaoAuthCode 대신 아래 클래스를 사용해야 합니다.
class KakaoToken(BaseModel):
    access_token: str