# database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# 1. 접속 정보 (본인 환경에 맞게 수정)
DB_USER = "root"
DB_PASSWORD = "1234" # 🚨 여기에 실제 비밀번호를 입력하세요!
DB_HOST = "127.0.0.1"
DB_NAME = "myapp_db"
DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{3306}/{DB_NAME}"

# 2. 비동기 엔진 및 세션 생성
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. 모델 클래스의 기반이 될 Base 클래스
Base = declarative_base()

# 4. API에서 DB 세션을 사용하기 위한 함수 (의존성 주입용)
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db