import os
from time import time
from pymongo import MongoClient
from langchain_huggingface import HuggingFaceEmbeddings
from openai import OpenAI
from dotenv import load_dotenv
import time
import re

# 전역 변수 초기화
def init_settings():
    global client, db, embedding_model, OPENAI_API_KEY
    # 1. MongoDB 연결
    MONGO_URI = os.getenv("MONGO_URI")
    
    client = MongoClient(MONGO_URI)
    db = client["legal_db"]

    # 2. 임베딩 모델 (DB 저장할 때와 동일하게 맞춰야 함)
    embedding_model = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'}
    )

    # 3. OPENAI_API_KEY 설정
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# 4. 공통 검색 함수
def search_collection(collection, index_name, embedding, top_k=3):
    pipeline = [
        {
            "$vectorSearch": {
                "index": index_name,
                "queryVector": embedding,
                "path": "embedding",
                "numCandidates": 100,
                "limit": top_k
            }
        },
        {
            "$project": {
                "_id": 0,
                "doc_type": collection.name,
                "case_no": 1,
                "case_name": 1,
                "law_id": 1,
                "law_name": 1,
                "holding": 1,
                "text": 1,
                "material_type": 1,
                "edition": 1,
                "org_author": 1,
                "filename": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    return list(collection.aggregate(pipeline))

def get_sentences(text, max_sentences=2):
    # 문장 단위 분리
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return " ".join(sentences[:max_sentences])

def clean_practice_text(text, max_sentences=3):
    import re
    # 1) 불필요한 공백 정리
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 2) 약관 구분자를 문장 끝으로 인식 (제 조, 제 관 등)
    text = re.sub(r'(제\s*조)', r'\1.', text)
    text = re.sub(r'(제\s*관)', r'\1.', text)
    
    # 3) 문장 단위로 분리
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # 4) 앞부분 몇 개만 가져오기
    summary = " ".join(sentences[:max_sentences])
    
    return summary


def make_Context(results_cases, results_laws, results_practices):
    # ========== CASE ==========
    context = "=== 📂 CASE ===\n"
    for r in results_cases[:3]:   # 상위 3개만 출력
        if r.get("holding"):
            case_name = r.get("case_name", "사건명 없음")
            case_no = r.get("case_no") or "검색요망"
            holding = get_sentences(r['holding'])
            context += f"- {case_name} (판레번호:{case_no}): {holding}\n"

    # ========== LAW ==========
    context += "\n=== 📂 LAW ===\n"
    if results_laws and results_laws[0].get("text"):
        r = results_laws[0]
        law_name = r.get("law_name", "법령명 없음")
        promulgation_no = r.get("promulgation_no") or "검색요망"
        law_text = get_sentences(r['text'])
        context += f"- {law_name} (공포번호:{promulgation_no}): {law_text}\n"
    else:
        context += "해당 질문에 적용할 법령 자료가 검색되지 않았습니다. (추가 검토 필요)"


    # ========== PRACTICE ==========
    context += "\n=== 📂 PRACTICE ===\n"
    for r in results_practices[:3]:  # 상위 3개만 출력
        if r.get("text"):
            material = r.get("material_type")
            if not material or material == "미상":
                material = "약관"
            org_author = r.get("org_author") or "실무자료"
            filename = r.get("filename") or "실무자료"
            practice_text = clean_practice_text(r['text'], max_sentences=3)
            context += f"- {material}\n  · 작성자: {org_author}\n  · 파일: {filename}\n  · 내용: {practice_text}\n"


    print("=== 검색된 컨텍스트 ===")
    print(context)
    print("=====================")

    return context


def call_openai_api(user_prompt):
    #prompt를 임베딩으로 변환
    embedding = embedding_model.embed_query(user_prompt)

    results_cases = search_collection(db.cases, "cases_vector_index", embedding, top_k=10)
    results_laws = search_collection(db.laws, "laws_vector_index", embedding, top_k=3)
    results_practices = search_collection(db.practices, "practices_vector_index", embedding, top_k=5)

    context = make_Context(results_cases, results_laws, results_practices)

    client = OpenAI(api_key=OPENAI_API_KEY)

    # 9. 프롬프트 생성
    prompt = f"""
    너는 손해사정사인 동시에 오랫동안 일 해왔고, 완벽히 업무를 숙지하고 있는 보험 관련 법률 어시스턴트다.
    아래 참고 자료를 분석하여, 질문과 직접 관련된 핵심 답변만 제시하라.
    - 질문이 처한 상황을 다시 한번 인지하고 답변에 반영한다.
    - 답변은 반드시 참고 자료에서 근거를 찾아야 한다.
    - 참고 자료와 무관한 내용은 '전문가에게 요청하기'라고 말한다.
    - 답변은 10줄 이내 확실하고, 간결하게 요약문으로 작성한다.
    - 검색된 컨텍스트에서 적절한 case와 practice를 연계해서 질문에 알 맞는 내용도 분석해서 요약하고.
    - 질문이 처한 상황을 다시 한번 인지하고 답변에 반영한다.
    - 좀 더 전문적이고 섬세하게 구체적으로 답변한다.

    📚 참고 자료:
    {context}

    ❓ 질문: {user_prompt}
    """
    print("🚀 chat completions 시작...")
    completions_start = time.time()
    # 10. LLM 호출
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300
    )

    completions_time = time.time() - completions_start
    print(f"\n🎯 chat completions 실행 시간: {completions_time:.2f}초")
    print("=" * 80)

    answer = response.choices[0].message.content.strip()
    if not answer:
        answer = "자료에 없음"

    print("\n=== AI 답변 ===")
    print(answer)

    return context ,answer


if __name__ == "__main__":

    print("🚀 프로그램 시작...")
    total_start = time.time()
    # 환경 변수 로드 및 설정 초기화
    load_dotenv()
    init_settings()

    # 테스트 질문
    user_question = "교통사고로 인한 손해배상 청구 소송에서, 상대방이 보험사인 경우와 개인인 경우에 어떤 차이가 있나요?"
    context, answer = call_openai_api(user_question)

    total_program_time = time.time() - total_start
    print(f"\n🎯 전체 프로그램 실행 시간: {total_program_time:.2f}초")
    print("=" * 80)

    print(f"출력된 context: {context}")
    print(f"출력된 answer: {answer}")
