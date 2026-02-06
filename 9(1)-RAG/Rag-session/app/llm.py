"""Solar Pro3 LLM utility for RAG answer generation.

Uses Upstage Solar API (OpenAI-compatible) with solar-pro3 model.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = "https://api.upstage.ai/v1/solar"
MODEL = "solar-mini"

NO_RAG_PROMPT = "Answer the following question concisely.\n\nQuestion: {question}"

RAG_PROMPT = """\
Answer the question based ONLY on the provided context.
If the answer is not found in the context, reply exactly: "The provided context does not contain this information."
Do NOT use any outside knowledge.

Context:
{context}

Question: {question}"""


def _get_api_key() -> str:
    """Get the first available Upstage API key."""
    key = os.getenv("UPSTAGE_API_KEY1") or os.getenv("UPSTAGE_API_KEY", "")
    return key.strip()


def generate(question: str, context: str | None = None) -> str:
    """Generate an answer using Solar LLM.

    Args:
        question: The user question.
        context: Retrieved context for RAG. None for no-RAG generation.

    Returns:
        str: The model's answer text.

    Hints:
        - Use _get_api_key() and OpenAI(api_key=..., base_url=BASE_URL)
        - If context is provided, use RAG_PROMPT; otherwise use NO_RAG_PROMPT
        - Use client.chat.completions.create(model=MODEL, messages=[...])
        - Set temperature=0 for deterministic output, max_tokens=1024
    """
    # 1. API 키 확인 및 클라이언트 설정
    api_key = _get_api_key()
    if not api_key:
        return "Error: UPSTAGE_API_KEY not found."

    client = OpenAI(api_key=api_key, base_url=BASE_URL)

    # 2. 프롬프트 구성 (Context 유무에 따라 분기)
    if context:
        # RAG 모드: 검색된 문맥을 포함
        system_msg = "You are a helpful assistant that answers questions based on the provided context."
        user_msg = RAG_PROMPT.format(context=context, question=question)
    else:
        # No RAG 모드: LLM의 기본 지식 사용
        system_msg = "You are a helpful assistant."
        user_msg = NO_RAG_PROMPT.format(question=question)

    # 3. LLM 호출 (Chat Completion)
    try:
        response = client.chat.completions.create(
            model=MODEL,  # 위에서 정의한 "solar-mini" 사용
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0,      # 사실 기반 답변을 위해 0으로 설정 (Deterministic)
            max_tokens=1024,    # 충분한 답변 길이 확보
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating answer: {e}"
