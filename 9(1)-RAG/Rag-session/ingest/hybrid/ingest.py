"""Ingest corpus into Elasticsearch Hybrid index (wiki-hybrid).

Index mapping: text field + dense_vector(4096, cosine).
Bulk chunk_size=100 (heavier with 4096-dim vectors).
"""

import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tqdm import tqdm

load_dotenv()

INDEX_NAME = "wiki-hybrid"
RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

INDEX_MAPPINGS = {
    "properties": {
        "text": {"type": "text", "analyzer": "standard"},
        "embedding": {
            "type": "dense_vector",
            "dims": 4096,
            "index": True,
            "similarity": "cosine",
        },
    }
}


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=120,
    )


def _generate_actions(corpus_path: Path, embeddings: np.ndarray, ids: list[str]):
    id_to_idx = {doc_id: idx for idx, doc_id in enumerate(ids)}

    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            doc_id = doc["id"]
            idx = id_to_idx.get(doc_id)
            if idx is None:
                continue
            yield {
                "_index": INDEX_NAME,
                "_id": doc_id,
                "_source": {
                    "text": doc["text"],
                    "embedding": embeddings[idx].tolist(),
                },
            }


def ingest(progress_callback=None):
    """Create hybrid index (text + dense_vector) and bulk-ingest corpus.

    Args:
        progress_callback: Optional callback(count) called after completion.

    Returns:
        int: Number of documents indexed.

    Hints:
        - Load embeddings from PROCESSED_DIR / "embeddings.npy"
        - Load IDs from PROCESSED_DIR / "embedding_ids.json"
        - Use get_es_client(), delete/create index with INDEX_MAPPINGS
        - Use _generate_actions(corpus_path, embeddings, ids) for bulk data
        - Use elasticsearch.helpers.bulk() with chunk_size=100
        - Call es.indices.refresh() after bulk ingest
    """
    client = get_es_client()
    
    # 1. 데이터 파일 경로 설정
    corpus_path = RAW_DIR / "corpus.jsonl"
    embeddings_path = PROCESSED_DIR / "embeddings.npy"
    ids_path = PROCESSED_DIR / "embedding_ids.json"

    # 파일 존재 확인
    if not embeddings_path.exists() or not ids_path.exists():
        print("Error: Embeddings or IDs file not found. Run Step 2 first.")
        return 0

    print("Loading embeddings and IDs...")
    embeddings = np.load(embeddings_path)
    with open(ids_path, "r", encoding="utf-8") as f:
        ids = json.load(f)

    # 2. 인덱스 재생성 (기존 인덱스 삭제 후 생성)
    if client.indices.exists(index=INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)
    
    client.indices.create(index=INDEX_NAME, mappings=INDEX_MAPPINGS)
    print(f"Index '{INDEX_NAME}' created.")

    # 3. Bulk 적재 실행
    print(f"Ingesting {len(ids)} documents into {INDEX_NAME}...")
    
    # _generate_actions 제너레이터를 사용하여 bulk 함수 호출
    success_count, _ = bulk(
        client,
        _generate_actions(corpus_path, embeddings, ids),
        chunk_size=100,  # 벡터 데이터가 크므로 청크 사이즈 조절
        stats_only=True,
        request_timeout=120
    )

    # 4. 리프레시 (검색 반영)
    client.indices.refresh(index=INDEX_NAME)
    print(f"Ingestion complete: {success_count} docs.")
    
    return success_count


if __name__ == "__main__":
    ingest()
