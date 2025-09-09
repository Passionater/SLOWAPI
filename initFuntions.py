import os
from time import time
from pymongo import MongoClient
from langchain_huggingface import HuggingFaceEmbeddings
import config

# 전역 변수 초기화
def init_settings():
    # 1. MongoDB 연결
    MONGO_URI = os.getenv("MONGO_URI")
    
    client = MongoClient(MONGO_URI)
    database = client["legal_db"]

    # 2. 임베딩 모델 (DB 저장할 때와 동일하게 맞춰야 함)
    embedding = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'}
    )

    # 3. OPENAI_API_KEY 설정
    api_key = os.getenv("OPENAI_API_KEY")
    
    # config 모듈의 전역 변수 설정
    config.set_globals(database, embedding, api_key)
