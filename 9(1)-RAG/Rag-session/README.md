# RAG Retrieval Playground

YBIGTA coursework comparing BM25, vector and hybrid retrieval on the `rag-datasets/rag-mini-wikipedia` dataset. This exercise uses the course's `quant-jason/Rag-session` material; it is not an independently authored production system.

## What to inspect

- [Streamlit interface](app/streamlit_app.py): data preparation, side-by-side retrieval and answer comparisons.
- [Dataset download](data/download.py): corpus and question-answer data from Hugging Face.
- [Ingestion](ingest/): embedding, Elasticsearch, Pinecone and hybrid indexing.
- [Retrievers](retrievers/): the three retrieval paths.
- [Answer generation](app/llm.py): language-model integration.

## Preview

![Coursework RAG demonstration](RAG%20test1.png)

## Local entry point

From this `Rag-session` directory, create a Python environment and run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app/streamlit_app.py
```

Copy `.env.example` to your local `.env` and configure the services used by the selected path. Elasticsearch/Pinecone and embedding/generation credentials are required for the corresponding features. In the interface, prepare the dataset, embeddings and indexes before running retrieval comparisons. Dataset downloading can also be started with `python -m data.download`.

This documentation was checked against the source entry points. A clean installation, external service connectivity and an end-to-end run have not been verified in this review. The screenshot records a coursework demonstration, not a current service availability guarantee.
