from fastapi import APIRouter, Request

from bm25_index import BM25Index
from numpy_index import NumpyIndex

router = APIRouter()


# docker compose exec python-rag curl http://localhost:8000/healthz
@router.get("/healthz")  # @router.get: registers a synchronous GET handler; FastAPI runs it in a thread pool so it won't block the event loop
def healthz(request: Request):
    """Return index readiness flags — used by docker-compose healthcheck and the Go service."""
    numpy_idx: NumpyIndex = request.app.state.numpy_index
    bm25_idx: BM25Index = request.app.state.bm25
    return {
        "status": "ok",
        "qa_count": len(getattr(request.app.state, "qa_pairs", [])),
        "embeddings_ready": numpy_idx._matrix is not None,
        "bm25_ready": bm25_idx._bm25 is not None,
    }
