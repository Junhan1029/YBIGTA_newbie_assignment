"""Vector retriever using Pinecone (cosine similarity)."""

import os

from dotenv import load_dotenv
from pinecone import Pinecone

from ingest.embedding import embed_query

load_dotenv()


def search(query: str, top_k: int = 10) -> list[dict]:
    """Vector cosine similarity search.

    Args:
        query: Search query string.
        top_k: Number of results to return.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "Vector".

    Hints:
        - Use embed_query(query) to get the query embedding vector
        - Connect: Pinecone(api_key=...) → pc.Index(index_name)
        - Use index.query(vector=..., top_k=..., include_metadata=True)
        - Text is in match["metadata"]["text"]
    """
    # 1. Pinecone 연결 설정
    api_key = os.getenv("PINECONE_API_KEY")
    # .env에 설정된 이름이 없으면 'ragsession' 기본값 사용
    index_name = os.getenv("PINECONE_INDEX_NAME", "ragsession")
    
    if not api_key:
        raise ValueError("PINECONE_API_KEY가 설정되지 않았습니다.")

    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)

    # 2. 쿼리 임베딩 (질문을 벡터로 변환)
    # 이미 구현해둔 embed_query 함수를 재사용합니다.
    try:
        query_vector = embed_query(query)
    except Exception as e:
        print(f"Error embedding query: {e}")
        return []

    # 3. Pinecone 검색 실행
    # include_metadata=True로 설정해야 저장해둔 텍스트를 같이 가져올 수 있습니다.
    response = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    # 4. 결과 파싱 (UI에서 요구하는 형식으로 변환)
    results = []
    for match in response["matches"]:
        # 메타데이터에서 원본 텍스트 추출 (없을 경우 빈 문자열)
        text_content = match["metadata"].get("text", "") if match.get("metadata") else ""
        
        results.append({
            "id": match["id"],
            "text": text_content,
            "score": match["score"],
            "method": "Vector"  # 출처 표기
        })
        
    return results
