"""Upstage Solar embedding utility with disk caching and parallel API keys.

Models:
  - solar-embedding-1-large-passage  (document encoding)
  - solar-embedding-1-large-query    (query encoding)

Uses multiple API keys (UPSTAGE_API_KEY1..N) for parallel embedding.
Each key gets its own thread with independent RPM/TPM limits.
Saves progress incrementally so crashes don't lose work.
Cache: data/processed/embeddings.npy (float32) + embedding_ids.json
"""

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

load_dotenv()

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
EMBEDDINGS_PATH = PROCESSED_DIR / "embeddings.npy"
IDS_PATH = PROCESSED_DIR / "embedding_ids.json"

BATCH_SIZE = 100
RPM_LIMIT = 100
MIN_INTERVAL = 60.0 / RPM_LIMIT
DIM = 4096
BASE_URL = "https://api.upstage.ai/v1/solar"
MAX_CHARS = 12000  # ~3000 tokens, safely under 4000 token limit
MAX_RETRIES = 3


def _get_api_keys() -> list[str]:
    """Collect all UPSTAGE_API_KEY* from env."""
    keys = []
    for i in range(1, 100):
        key = os.getenv(f"UPSTAGE_API_KEY{i}")
        if key:
            keys.append(key.strip())
        else:
            break
    if not keys:
        single = os.getenv("UPSTAGE_API_KEY", "")
        if single:
            keys.append(single.strip())
    return keys


def _truncate(text: str) -> str:
    """Truncate text to stay within token limits."""
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS]
    return text


def _embed_batch_safe(client: OpenAI, batch: list[str]) -> list[list[float]]:
    """Embed a batch with retry and fallback to smaller sub-batches."""
    truncated = [_truncate(t) for t in batch]

    for attempt in range(MAX_RETRIES):
        try:
            response = client.embeddings.create(
                model="solar-embedding-1-large-passage",
                input=truncated,
            )
            sorted_data = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in sorted_data]
        except Exception as e:
            err_msg = str(e)
            if "maximum context length" in err_msg or "4000 tokens" in err_msg:
                # Split batch in half and process separately
                mid = len(truncated) // 2
                if mid == 0:
                    # Single text too long, truncate more aggressively
                    truncated = [t[:MAX_CHARS // 2] for t in truncated]
                    continue
                left = _embed_batch_safe(client, truncated[:mid])
                time.sleep(MIN_INTERVAL)
                right = _embed_batch_safe(client, truncated[mid:])
                return left + right
            elif attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                time.sleep(wait)
            else:
                raise


def embed_passages(texts: list[str], ids: list[str], progress_callback=None) -> np.ndarray:
    """Embed passages using parallel API keys.

    Args:
        texts: List of passage strings to embed.
        ids: List of document IDs (same length as texts).
        progress_callback: Optional callback(current, total) for progress updates.

    Returns:
        np.ndarray of shape (N, 4096), dtype float32.

    Hints:
        - Use _get_api_keys() to get API keys, OpenAI(api_key=..., base_url=BASE_URL) to create clients
        - Use _embed_batch_safe(client, batch) to embed a batch of texts
        - Process texts in chunks of BATCH_SIZE
        - Save results to EMBEDDINGS_PATH (.npy) and IDS_PATH (.json)
    """
    # 1. 출력 디렉토리 생성
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 2. API 키 로드 및 클라이언트 생성
    api_keys = _get_api_keys()
    if not api_keys:
        raise ValueError("No UPSTAGE_API_KEY found in .env")
    
    clients = [OpenAI(api_key=k, base_url=BASE_URL) for k in api_keys]
    num_workers = len(clients)
    print(f"Using {num_workers} API keys for embedding...")

    # 3. 배치 준비
    batches = [texts[i : i + BATCH_SIZE] for i in range(0, len(texts), BATCH_SIZE)]
    num_batches = len(batches)
    results = [None] * num_batches  # 순서 보장을 위한 리스트

    # 4. 병렬 처리 실행
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_idx = {}
        
        # 각 배치를 클라이언트들에게 라운드 로빈 방식으로 할당
        for i, batch in enumerate(batches):
            client = clients[i % num_workers]
            future = executor.submit(_embed_batch_safe, client, batch)
            future_to_idx[future] = i
        
        # 완료되는 순서대로 처리
        completed_count = 0
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                batch_embeddings = future.result()
                results[idx] = batch_embeddings
                
                completed_count += 1
                if progress_callback:
                    progress_callback(completed_count, num_batches)
                else:
                    # Streamlit이 아닐 경우 간단한 로그 출력
                    if completed_count % 5 == 0:
                        print(f"Progress: {completed_count}/{num_batches} batches")
                        
            except Exception as e:
                print(f"Error in batch {idx}: {e}")
                # 에러 발생 시 해당 배치는 0 벡터나 빈 리스트로 처리하지 않고 중단 (디버깅 용이성)
                raise e

    # 5. 결과 병합 및 저장
    # results는 list of list of float -> (N, 4096) numpy array로 변환
    all_embeddings = []
    for batch_res in results:
        all_embeddings.extend(batch_res)
    
    embeddings_array = np.array(all_embeddings, dtype=np.float32)

    np.save(EMBEDDINGS_PATH, embeddings_array)
    with open(IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(ids, f)

    print(f"Saved embeddings to {EMBEDDINGS_PATH} shape: {embeddings_array.shape}")
    return embeddings_array


def embed_query(query: str) -> list[float]:
    """Embed a single query using the query model.

    Args:
        query: The search query string.

    Returns:
        list[float] of length 4096 (embedding vector).

    Hints:
        - Use _get_api_keys() to get an API key
        - Model name: "solar-embedding-1-large-query"
        - Use _truncate() to handle long queries
    """
    api_keys = _get_api_keys()
    if not api_keys:
        raise ValueError("No UPSTAGE_API_KEY found")
    
    # 쿼리는 하나뿐이므로 첫 번째 키 사용
    client = OpenAI(api_key=api_keys[0], base_url=BASE_URL)
    
    response = client.embeddings.create(
        model="solar-embedding-1-large-query",  # 쿼리용 모델
        input=_truncate(query)
    )
    return response.data[0].embedding


def load_cached_embeddings() -> tuple[np.ndarray, list[str]] | None:
    """Load cached embeddings from disk. Returns (embeddings, ids) or None."""
    if EMBEDDINGS_PATH.exists() and IDS_PATH.exists():
        embeddings = np.load(EMBEDDINGS_PATH)
        ids = json.loads(IDS_PATH.read_text())
        return embeddings, ids
    return None


if __name__ == "__main__":
    from data.download import RAW_DIR

    corpus_path = RAW_DIR / "corpus.jsonl"
    if not corpus_path.exists():
        print("Run data/download.py first.")
        raise SystemExit(1)

    texts, ids = [], []
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            ids.append(doc["id"])
            texts.append(doc["text"])

    embed_passages(texts, ids)
