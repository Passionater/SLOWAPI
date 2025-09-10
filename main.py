from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from initFuntions import init_settings
from openai import OpenAI
from openAiRagChat import call_openai_api
from typing import Optional
import config


app = FastAPI()

# --- Flutter 챗봇으로부터 받을 데이터 형식을 정의 ---
class ChatMessage(BaseModel):
    message: str

# --- Flutter 챗봇에게 보낼 데이터 형식을 정의 ---
class ChatResponse(BaseModel):
    reply_content: str
    reply_answer: str

class userInputParam(BaseModel):
    prompt:  Optional[str] = "Generate a plan for a trip to Jeju Island"
    temperature: Optional[float] = 0.7
    max_length: Optional[int] = 50
    image : Optional[str] = None

class aiRespose(BaseModel):
    response: str
    action: str

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





#============================================호출할 function


if __name__ == "__main__":
    
    load_dotenv()  # .env 파일 로드
    init_settings()  # 전역 변수 초기화
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)