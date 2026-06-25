from contextlib import asynccontextmanager
from fastapi import FastAPI

from indexer import load_and_index
from metrics import Metrics
from router_rag import router as rag_router
from router_admin import router as admin_router
from router_health import router as health_router


# turns async generator(generator returns values one at a time, pausing between each) into a context manager; FastAPI calls the body before `yield` on startup, and after `yield` on shutdown
@asynccontextmanager
async def lifespan(app: FastAPI): # https://fastapi.tiangolo.com/tutorial/first-steps/
    """Startup: build indexes into app.state. Shutdown: clear qa_pairs from app.state."""
    app.state.metrics = Metrics()
    await load_and_index(app, label="startup", include_db=False)

    yield  # FastAPI serves requests while suspended here
    # Stays here until server stops(Ctrl+C or signal)

    app.state.qa_pairs = []


app = FastAPI(lifespan=lifespan)
app.include_router(rag_router)
app.include_router(admin_router)
app.include_router(health_router)
