# 전역 변수들을 관리하는 설정 파일
db = None
embedding_model = None
OPENAI_API_KEY = None
KAKAO_API_KEY = None

def set_globals(database, embedding, api_key, kakao_api_key):
    """전역 변수들을 설정하는 함수"""
    global db, embedding_model, OPENAI_API_KEY , KAKAO_API_KEY
    db = database
    embedding_model = embedding
    OPENAI_API_KEY = api_key
    KAKAO_API_KEY = kakao_api_key