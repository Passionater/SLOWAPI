# main.py

from fastapi import FastAPI
from dotenv import load_dotenv

import models
from database import engine
from chatbot import router as chatbot_router
from auth import router as auth_router

# .env 파일 로드 (가장 먼저 실행되도록)
load_dotenv()

app = FastAPI()

# DB 테이블 생성 (앱 실행 시 한번만)
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# 각 부서(라우터)를 메인 앱에 포함
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chatbot_router, prefix="/api", tags=["Chatbot & Search"])

# 서버 실행 (개발용)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)