"""Hybrid retriever using Elasticsearch RRF (Reciprocal Rank Fusion).

Combines BM25 text search with dense vector kNN search.
Uses ES 8.14+ RRF support with rank_constant=60.
"""

import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from ingest.embedding import embed_query

load_dotenv()

INDEX_NAME = "wiki-hybrid"


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=30,
    )


def search(query: str, top_k: int = 10, candidate_size: int = 50) -> list[dict]:
    """RRF hybrid search combining BM25 + kNN.

    Args:
        query: Search query string.
        top_k: Number of results to return.
        candidate_size: Number of kNN candidates before RRF fusion.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "Hybrid (RRF)".

    Hints:
        - Use embed_query(query) to get the query embedding vector
        - Use get_es_client() and es.search() with "retriever" parameter
        - RRF retriever combines "standard" (BM25 match) + "knn" retrievers
        - kNN field: "embedding", rank_constant: 60
        - num_candidates = candidate_size * 2
    """
    client = get_es_client()
    
    # 1. 쿼리 임베딩
    query_vector = embed_query(query)

    # 2. Elasticsearch Retriever 구성 (RRF)
    # Hint: Use es.search() with "retriever" parameter
    retriever_config = {
        "rrf": {
            "retrievers": [
                # (1) Standard Retriever (BM25)
                {
                    "standard": {
                        "query": {
                            "match": {
                                "text": query
                            }
                        }
                    }
                },
                # (2) kNN Retriever (Vector)
                {
                    "knn": {
                        "field": "embedding",
                        "query_vector": query_vector,
                        "k": candidate_size,
                        "num_candidates": candidate_size * 2,
                    }
                }
            ],
            "rank_constant": 60,
            # window_size는 기본값 사용 (Top K 결과에 영향을 줌)
        }
    }

    # 3. 검색 실행
    response = client.search(
        index=INDEX_NAME,
        retriever=retriever_config,
        size=top_k,
        _source=["text"] # 결과에 텍스트 포함
    )

    # 4. 결과 파싱
    results = []
    for hit in response["hits"]["hits"]:
        results.append({
            "id": hit["_id"],
            "text": hit["_source"]["text"],
            "score": hit["_score"], # RRF 점수
            "method": "Hybrid(RRF)"
        })
        
    return results
