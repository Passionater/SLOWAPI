# chatbot.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from openai import OpenAI

import config
from kakao_API import get_kakao_api
from openAiRagChat import call_openai_api

router = APIRouter()

# --- 데이터 모델 정의 ---
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply_content: str
    reply_answer: str

class userInputParam(BaseModel):
    prompt: Optional[str] = ""
    temperature: Optional[float] = 0.7
    max_length: Optional[int] = 1000
    image: Optional[str] = None

class aiRespose(BaseModel):
    response: str
    action: str

class SearchResult(BaseModel):
    result: str

class SearchAPI(BaseModel):
    place_name: str
    phone: str
    road_address_name: str

# --- API 엔드포인트들 ---
@router.post("/chat", response_model=ChatResponse)
def handle_chat(chat_message: ChatMessage):
    user_message = chat_message.message
    print(f"Flutter 앱으로부터 받은 메시지: {user_message}")
    context, answer = call_openai_api(user_message)
    return {"reply_content": context, "reply_answer": answer}

@router.post("/chatBot", response_model=aiRespose)
def generate_plan(item: userInputParam):
    """고객서비스 및 앱 사용 관련 문의 처리용 엔드포인트"""
    user_question = item.prompt
    max_length = item.max_length
    
    try:
        print(f"고객서비스 문의: {user_question}")
        
        # 고객서비스 전용 프롬프트 구성
        customer_service_prompt = f"""
        너는 '법률 상담 AI 앱'의 친절하고 전문적인 고객서비스 담당자입니다.
        
        **역할:**
        - 앱 사용법 안내
        - 기능 설명 및 도움말 제공
        - 계정/로그인 관련 문의 처리
        - 서비스 이용 중 발생한 문제 해결
        - 요금/결제 관련 안내
        - 일반적인 앱 관련 질문 응답
        
        **응답 방식:**
        - 친근하고 정중한 말투 사용
        - 단계별로 명확하게 설명
        - 구체적인 해결 방법 제시
        - 필요시 관련 기능 위치 안내
        
        **우리 앱 주요 기능:**
        1. 🤖 AI 법률 상담: 보험, 교통사고, 손해사정 관련 전문 상담
        2. 📍 업체 검색: 손해사정 관련 업체 찾기 (카카오 지도 연동)
        3. 👤 계정 관리: 일반 회원가입, 카카오 로그인
        4. 📚 판례/법령 검색: AI 기반 법률 문서 검색
        
        **법률 상담이 아닌 경우 처리:**
        - 법률 상담 질문이면: "법률 상담은 메인 화면의 'AI 상담' 기능을 이용해주세요."
        - 앱 사용법/기술 문의면: 친절하게 상세 안내
        - 서비스 불만/제안이면: "소중한 의견 감사합니다. 개선에 참고하겠습니다."
        
        **고객 문의:** {user_question}
        
        위 문의에 대해 친절하고 도움이 되는 답변을 제공해주세요.
        """
        
        chat_client = OpenAI(api_key=config.OPENAI_API_KEY)
        response = chat_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": customer_service_prompt}],
            temperature=0.3,  # 일관된 고객서비스 응답을 위해 낮은 temperature
            max_tokens=max_length
        )
        result = response.choices[0].message.content
        
        # 응답 분류 (추후 분석용)
        action_type = "customer_service"
        if any(keyword in user_question.lower() for keyword in ["로그인", "회원가입", "계정"]):
            action_type = "account_help"
        elif any(keyword in user_question.lower() for keyword in ["사용법", "기능", "어떻게"]):
            action_type = "usage_guide"
        elif any(keyword in user_question.lower() for keyword in ["오류", "안됨", "문제"]):
            action_type = "technical_support"
        
        return aiRespose(response=result, action=action_type)
    except Exception as e:
        error_message = "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        return aiRespose(response=error_message, action=f"error: {str(e)}")

@router.get("/search", response_model=SearchResult)
def search_topic(query: str):
    # ... (기존 search 코드와 동일) ...
    print(f"Flutter 앱으로부터 받은 검색어: {query}")
    if "보험금" in query or "사고" in query:
        search_result = (
            '보험금 청구는 약관에 명시된 보험사고가 발생했을 때, 계약자가 보험사에 보상을 요청하는 정당한 권리입니다.\n\n'
            '정확한 산정을 위해 병원 서류, 사고 사실 확인서 등을 꼼꼼히 준비하는 것이 중요합니다.'
        )
    else:
        search_result = f"'{query}'에 대한 검색 결과를 찾을 수 없습니다. 다른 검색어로 시도해 보세요."
    return {"result": search_result}

@router.get("/searchAPI", response_model=List[SearchAPI])
def get_kakao_api123():
    results = get_kakao_api()
    return results[:3]