from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from initFuntions import init_settings
from openai import OpenAI
from openAiRagChat import call_openai_api
from typing import Optional
import config
from kakao_API import get_kakao_api
from typing import List


app = FastAPI()

# --- Flutter 챗봇으로부터 받을 데이터 형식을 정의 ---
class ChatMessage(BaseModel):
    message: str

# --- Flutter 챗봇에게 보낼 데이터 형식을 정의 ---
class ChatResponse(BaseModel):
    reply_content: str
    reply_answer: str

class userInputParam(BaseModel):
    prompt:  Optional[str] = ""
    temperature: Optional[float] = 0.7
    max_length: Optional[int] = 50
    image : Optional[str] = None

class aiRespose(BaseModel):
    response: str
    action: str

# --- ❗️새로운 검색 관련 모델 추가 ---
class SearchResult(BaseModel):
    result: str
    
class SearchAPI(BaseModel):
    place_name: str
    phone: str
    road_address_name: str    
    
    
# # POST /chat : 챗봇 메시지를 받아 답변을 반환
# @app.post("/chat", response_model=ChatResponse)
# def handle_chat(chat_message: ChatMessage):
#     user_message = chat_message.message
    
#     print(f"Flutter 앱으로부터 받은 메시지: {user_message}")
    
#     # (나중에는 여기에 실제 AI 모델 로직이 들어갑니다)
#     # 지금은 간단히 받은 메시지를 되돌려주는 응답을 생성합니다.
#     bot_reply = f"'{user_message}'라고 질문하셨네요. 지금은 학습 중이라 간단한 답변만 가능해요."
    
#     return {"reply": bot_reply}


# POST /chat : 챗봇 메시지를 받아 답변을 반환
@app.post("/chat", response_model=ChatResponse)
def handle_chat(chat_message: ChatMessage):
    user_message = chat_message.message
    
    print(f"Flutter 앱으로부터 받은 메시지: {user_message}")
    
    # (나중에는 여기에 실제 AI 모델 로직이 들어갑니다)
    # 지금은 간단히 받은 메시지를 되돌려주는 응답을 생성합니다.
    context , answer = call_openai_api(user_message)
    
    return {"reply_content": context,"reply_answer": answer}
    

@app.post("/chatBot", response_model=aiRespose)
def generate_plan(item: userInputParam):
    prompt = item.prompt
    max_length = item.max_length

    try:
        print(f''"Flutter 앱으로부터 받은 메시지: {prompt}"'')
        chat_client = OpenAI(api_key=config.OPENAI_API_KEY)

        response = chat_client.chat.completions.create(
            model="gpt-4o-mini",  # 필요시 gpt-4로 변경
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=max_length
        )
        result = response.choices[0].message.content
        return aiRespose(response=result, action="")
    except Exception as e:
        return aiRespose(response="Error occurred", action=str(e))


# --- ❗️새로운 검색 API 엔드포인트 추가 ---
@app.get("/search", response_model=SearchResult)
def search_topic(query: str):
    print(f"Flutter 앱으로부터 받은 검색어: {query}")
    
    # 지금은 Flutter와의 연결 테스트를 위해 간단한 로직을 사용합니다.
    # 나중에는 이 부분을 call_openai_api 처럼 실제 검색 로직으로 바꿀 수 있습니다.
    if "보험금" in query or "사고" in query:
        search_result = (
            '보험금 청구는 약관에 명시된 보험사고가 발생했을 때, 계약자가 보험사에 보상을 요청하는 정당한 권리입니다.\n\n'
            '정확한 산정을 위해 병원 서류, 사고 사실 확인서 등을 꼼꼼히 준비하는 것이 중요합니다.'
        )
    else:
        search_result = f"'{query}'에 대한 검색 결과를 찾을 수 없습니다. 다른 검색어로 시도해 보세요."
        
    return {"result": search_result}

from typing import List

@app.get("/searchAPI", response_model=List[SearchAPI])
def get_kakao_api123():
    results = get_kakao_api()
    return results[:3]


#============================================호출할 function


if __name__ == "__main__":
    
    load_dotenv()  # .env 파일 로드
    init_settings()  # 전역 변수 초기화
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)