# auth.py

import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from dotenv import load_dotenv

import models, schemas
from database import get_db

# .env 파일에서 환경 변수 로드
load_dotenv()

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 헬퍼 함수 ---
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).filter(models.User.email == email, models.User.provider == 'local'))
    return result.scalars().first()

async def get_or_create_kakao_user(db: AsyncSession, user_info: dict):
    # ... (이전 답변의 get_or_create_kakao_user 함수 내용 그대로 붙여넣기) ...
    kakao_id = user_info.get("id")
    nickname = user_info.get("properties", {}).get("nickname")
    email = user_info.get("kakao_account", {}).get("email")
    if not kakao_id or not nickname:
        raise HTTPException(status_code=400, detail="Kakao user info is invalid")
    result = await db.execute(select(models.User).filter(models.User.social_id == str(kakao_id), models.User.provider == 'kakao'))
    db_user = result.scalars().first()
    if not db_user:
        db_user = models.User(email=email, nickname=nickname, provider='kakao', social_id=str(kakao_id))
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    return db_user

# --- API 엔드포인트들 ---
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # ... (기존 register 코드와 동일) ...
    hashed_password = pwd_context.hash(user_create.password)
    db_user = models.User(email=user_create.email, password=hashed_password, nickname=user_create.nickname, provider='local')
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=schemas.UserResponse)
async def login_for_access_token(user_login: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    # ... (기존 login 코드와 동일) ...
    user = await get_user_by_email(db, email=user_login.email)
    if not user or not pwd_context.verify(user_login.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    return user

# ⭐️ 새로운 카카오 로그인 엔드포인트 (액세스 토큰 사용)
@router.post("/kakao", response_model=schemas.UserResponse)
async def kakao_login(token: schemas.KakaoToken, db: AsyncSession = Depends(get_db)):
    KAKAO_USERINFO_URL = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {token.access_token}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(KAKAO_USERINFO_URL, headers=headers)
            response.raise_for_status()
            user_info = response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=400, detail=f"Invalid Kakao token: {e}")

    # get_or_create_kakao_user 헬퍼 함수를 호출하는 방식으로 변경 (코드 재사용)
    user = await get_or_create_kakao_user(db, user_info)
    return user