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
    max_length: Optional[int] = 50
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
@router.post("/message", response_model=ChatResponse)
def handle_chat(chat_message: ChatMessage):
    user_message = chat_message.message
    print(f"Flutter 앱으로부터 받은 메시지: {user_message}")
    context, answer = call_openai_api(user_message)
    return {"reply_content": context, "reply_answer": answer}

@router.post("/bot", response_model=aiRespose)
def generate_plan(item: userInputParam):
    # ... (기존 chatBot 코드와 동일) ...
    prompt = item.prompt
    max_length = item.max_length
    try:
        print(f"Flutter 앱으로부터 받은 메시지: {prompt}")
        chat_client = OpenAI(api_key=config.OPENAI_API_KEY)
        response = chat_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=max_length
        )
        result = response.choices[0].message.content
        return aiRespose(response=result, action="")
    except Exception as e:
        return aiRespose(response="Error occurred", action=str(e))

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