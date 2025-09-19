# models.py
from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from database import Base # 2단계에서 만든 Base 클래스 가져오기

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    nickname = Column(String(50), nullable=False)
    provider = Column(String(20), nullable=False, server_default='local')
    social_id = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))