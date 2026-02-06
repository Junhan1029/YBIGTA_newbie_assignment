"""Ingest corpus into Elasticsearch BM25 index (wiki-bm25).

Index mapping: text field only (no vectors).
Bulk chunk_size=500 (lightweight without vectors).
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tqdm import tqdm

load_dotenv()

INDEX_NAME = "wiki-bm25"
RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"

INDEX_MAPPINGS = {
    "properties": {
        "text": {"type": "text", "analyzer": "standard"},
    }
}


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=60,
    )


def _generate_actions(corpus_path: Path):
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            yield {
                "_index": INDEX_NAME,
                "_id": doc["id"],
                "_source": {
                    "text": doc["text"],
                },
            }


def ingest(progress_callback=None):
    """Create BM25 index and bulk-ingest corpus into Elasticsearch.

    Args:
        progress_callback: Optional callback(count) called after completion.

    Returns:
        int: Number of documents indexed.

    Hints:
        - Use get_es_client() to get ES client
        - Delete existing index if it exists, then create with INDEX_MAPPINGS
        - Corpus is at RAW_DIR / "corpus.jsonl"
        - Use _generate_actions(corpus_path) for bulk data
        - Use elasticsearch.helpers.bulk() with chunk_size=500
        - Call es.indices.refresh() after bulk ingest
    """
    client = get_es_client()
    corpus_path = RAW_DIR / "corpus.jsonl"

    # 1. 기존 인덱스 삭제 및 새로 생성
    if client.indices.exists(index=INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)
    
    client.indices.create(index=INDEX_NAME, mappings=INDEX_MAPPINGS)
    print(f"Index '{INDEX_NAME}' created.")

    if not corpus_path.exists():
        print(f"Error: {corpus_path} not found.")
        return 0

    # 2. 데이터 적재 (Bulk)
    # 총 라인 수 계산 (progress bar용)
    total_docs = sum(1 for _ in open(corpus_path, encoding="utf-8"))
    
    # bulk 함수 실행
    success_count, _ = bulk(
        client,
        _generate_actions(corpus_path),
        chunk_size=500,
        stats_only=True
    )

    # 3. 리프레시 (검색 가능하게 만듦)
    client.indices.refresh(index=INDEX_NAME)
    print(f"Ingested {success_count} documents into {INDEX_NAME}.")

    return success_count


if __name__ == "__main__":
    ingest()
