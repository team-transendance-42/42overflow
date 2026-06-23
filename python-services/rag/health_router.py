from fastapi import APIRouter, Request

from bm25_index import BM25Index
from indexer import qa_cache
from numpy_index import NumpyIndex

router = APIRouter()


# docker compose exec python-rag curl http://localhost:8000/healthz
@router.get("/healthz")
def healthz(request: Request):
    numpy_idx: NumpyIndex = request.app.state.numpy_index
    bm25_idx: BM25Index = request.app.state.bm25
    return {
        "status": "ok",
        "qa_count": len(qa_cache["qa_pairs"]),
        "embeddings_ready": numpy_idx._matrix is not None,
        "bm25_ready": bm25_idx._bm25 is not None,
    }
