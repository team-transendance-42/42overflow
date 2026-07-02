from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field # data validation, parsing, and serialization
# BaseModel checks that incoming data has the correct types and structure and automatically converts values when possible.
# Field: add metadata, validation rules, defaults, descriptions, aliases, etc.
# ConfigDict: configure model behavior
#class User(BaseModel):
#    model_config = ConfigDict(
#        extra="forbid"
#    ) ; User(name="John", city="Amsterdam") raises err


from retriever import hybrid_search
from router_admin import require_admin

router = APIRouter()


class AskRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)  # ConfigDict: pydantic config for the model; str_strip_whitespace=True auto-strips leading/trailing spaces from all str fields; Pydantic looks for model_config internally when the class is created.
    question: str = Field(min_length=1)  # Field: adds validation metadata; min_length=1 rejects empty strings before the handler runs


class RetrieveResponse(BaseModel):
    contexts: list[dict] # [{"id": "post_42", "text": "Q: ...\nA: ...", "rrf_score": 0.031, "topic": "git"},{...}, {...}]
    confidence: float
    best_similarity: float
    has_embeddings: bool


 # @router.post: registers this function as a POST handler;
#  response_model is a FastAPI param: validate and serialize the return value against that schema
# Request from FastAPI(build on top of Starlette)
# When a client sends an HTTP request, the ASGI server (Uvicorn) receives raw bytes and builds an ASGI scope — a plain Python dict:
#  scope = {
#      "type": "http",
#      "method": "POST",
#      "path": "/rag/retrieve",
#      "headers": [...],
#      "query_string": b"limit=10",
#      ...
#  } Starlette wraps that scope in a Request object, not to work with raw dicts.
#  It's a lazy wrapper — it doesn't read the body until the await request.body()
@router.post("/rag/retrieve", response_model=RetrieveResponse)
async def retrieve(body: AskRequest, request: Request, _: None = Depends(require_admin)) -> RetrieveResponse:
    """
    Retrieval only — no generation.
    Returns top-K context docs and the max RRF score as confidence.
    Used by the Go streaming Community endpoint.
    503 if BM25 index isn't ready. 502 if hybrid_search raises unexpectedly.
    Embedding failures are caught inside hybrid_search and degrade to BM25-only (has_embeddings=False).
    """
    bm25_index = request.app.state.bm25
    numpy_index = request.app.state.numpy_index
    id_to_text = request.app.state.id_to_text
    id_to_topic = request.app.state.id_to_topic
    centroids = request.app.state.centroids
    topic_intro_ids = getattr(request.app.state, "topic_intro_ids", {})
    metrics = request.app.state.metrics

    metrics.retrieve_total += 1

    if bm25_index is None:
        metrics.retrieve_errors += 1
        raise HTTPException(status_code=503, detail="RAG index not ready — try again shortly")

    try:
        contexts, best_similarity, has_embeddings = await hybrid_search(
            body.question, bm25_index, numpy_index,
            id_to_text, id_to_topic, centroids,
            top_k=4,
            topic_intro_ids=topic_intro_ids,
        )
    except Exception as exc:
        metrics.retrieve_errors += 1
        raise HTTPException(status_code=502, detail=str(exc))

    if not has_embeddings:
        metrics.bm25_only_fallbacks += 1

    confidence = max((c["rrf_score"] for c in contexts), default=0.0)
    return RetrieveResponse(
        contexts=contexts,
        confidence=confidence,
        best_similarity=best_similarity,
        has_embeddings=has_embeddings,
    )
