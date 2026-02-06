"""Ingest embeddings into Pinecone vector index.

Batch upsert: 100 vectors per call.
Metadata: text truncated to 1000 chars (40KB limit).
"""

import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from pinecone import Pinecone
from tqdm import tqdm

load_dotenv()

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

BATCH_SIZE = 100
TEXT_LIMIT = 1000  # metadata text truncation


def ingest(progress_callback=None):
    """Batch upsert embeddings into Pinecone vector index.

    Args:
        progress_callback: Optional callback(current, total) for progress updates.

    Returns:
        int: Number of vectors upserted.

    Hints:
        - Load embeddings from PROCESSED_DIR / "embeddings.npy"
        - Load IDs from PROCESSED_DIR / "embedding_ids.json"
        - Load texts from RAW_DIR / "corpus.jsonl" for metadata
        - Connect: Pinecone(api_key=...) → pc.Index(index_name)
        - Upsert format: {"id": ..., "values": [...], "metadata": {"text": ...}}
        - Batch size: BATCH_SIZE (100), truncate text to TEXT_LIMIT (1000) chars
    """
    # 1. 파일 경로 확인
    embeddings_path = PROCESSED_DIR / "embeddings.npy"
    ids_path = PROCESSED_DIR / "embedding_ids.json"
    corpus_path = RAW_DIR / "corpus.jsonl"

    if not embeddings_path.exists() or not ids_path.exists():
        print("Error: Embeddings file not found. Run Step 2 first.")
        return 0

    # 2. 데이터 로드
    print("Loading data...")
    embeddings = np.load(embeddings_path)
    
    with open(ids_path, "r", encoding="utf-8") as f:
        ids = json.load(f)
        
    # 텍스트 메타데이터 로드 (ID -> Text 매핑)
    id_to_text = {}
    if corpus_path.exists():
        with open(corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                doc = json.loads(line)
                id_to_text[doc["id"]] = doc["text"]

    # 3. Pinecone 연결
    api_key = os.getenv("PINECONE_API_KEY")
    # .env에 이름이 없으면 기본값 'ragsession' 사용
    index_name = os.getenv("PINECONE_INDEX_NAME", "ragsession")

    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in .env")

    pc = Pinecone(api_key=api_key)
    
    # 인덱스 존재 여부 확인
    existing_indexes = pc.list_indexes().names()
    if index_name not in existing_indexes:
        print(f"Error: Index '{index_name}' not found in Pinecone. Created indexes: {existing_indexes}")
        return 0
        
    index = pc.Index(index_name)

    # 4. 배치 업로드 실행
    total_vectors = len(ids)
    print(f"Upserting {total_vectors} vectors to index '{index_name}'...")

    for i in range(0, total_vectors, BATCH_SIZE):
        # 배치 슬라이싱
        batch_ids = ids[i : i + BATCH_SIZE]
        batch_vectors = embeddings[i : i + BATCH_SIZE]
        
        vectors_to_upsert = []
        for j, doc_id in enumerate(batch_ids):
            # Numpy array -> List 변환
            vector_values = batch_vectors[j].tolist()
            
            # 메타데이터 준비 (텍스트 길이 제한)
            original_text = id_to_text.get(doc_id, "")
            text_truncated = original_text[:TEXT_LIMIT]
            
            vectors_to_upsert.append({
                "id": doc_id,
                "values": vector_values,
                "metadata": {"text": text_truncated}
            })
        
        # 업로드 (Upsert)
        try:
            index.upsert(vectors=vectors_to_upsert)
        except Exception as e:
            print(f"Error upserting batch starting at {i}: {e}")
            # 에러 발생 시에도 계속 진행할지 여부는 선택 (여기선 로그만 찍고 진행)

        # 진행률 업데이트 (Streamlit용)
        current_count = min(i + BATCH_SIZE, total_vectors)
        if progress_callback:
            progress_callback(current_count, total_vectors)
        else:
            # 터미널 실행 시 로그
            if current_count % 1000 == 0:
                print(f"Progress: {current_count}/{total_vectors}")

    print("Pinecone ingestion complete.")
    return total_vectors


if __name__ == "__main__":
    ingest()
