from contextlib import asynccontextmanager
from fastapi import FastAPI

from admin_router import router as admin_router
from health_router import router as health_router
from indexer import load_and_index, qa_cache
from metrics import Metrics
from router import router as rag_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.metrics = Metrics()
    await load_and_index(app, label="startup", include_db=False)

    yield

    qa_cache["qa_pairs"] = []


app = FastAPI(lifespan=lifespan)
app.include_router(rag_router)
app.include_router(admin_router)
app.include_router(health_router)
