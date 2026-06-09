from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from retriever import hybrid_search

router = APIRouter()


class AskRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(min_length=1)


class RetrieveResponse(BaseModel):
    contexts: list[dict]
    confidence: float


@router.post("/rag/retrieve", response_model=RetrieveResponse)
async def retrieve(body: AskRequest, request: Request) -> RetrieveResponse:
    """
    Retrieval only — no generation.
    Returns top-K context docs and the max RRF score as confidence.
    Used by the Go streaming Community endpoint.
    503 if BM25 index isn't ready. 502 if embedding service is unreachable.
    """
    bm25_index = request.app.state.bm25
    numpy_index = request.app.state.numpy_index
    id_to_text = request.app.state.id_to_text
    id_to_topic = request.app.state.id_to_topic
    centroids = request.app.state.centroids
    topic_intro_ids = getattr(request.app.state, "topic_intro_ids", {})

    if bm25_index is None:
        raise HTTPException(status_code=503, detail="RAG index not ready — try again shortly")

    try:
        contexts = await hybrid_search(
            body.question, bm25_index, numpy_index,
            id_to_text, id_to_topic, centroids,
            top_k=4,
            topic_intro_ids=topic_intro_ids,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    confidence = max((c["rrf_score"] for c in contexts), default=0.0)
    return RetrieveResponse(contexts=contexts, confidence=confidence)
