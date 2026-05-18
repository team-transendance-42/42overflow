FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv as the package/runtime manager.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

COPY . ./

# Pre-download the default embedding model so the container never needs network at startup.
# Default: BAAI/bge-small-en-v1.5 (384-dim, ~100 MB RAM) — for memory-constrained machines.
# School computers: set EMBED_MODEL=nomic-ai/nomic-embed-text-v1.5 at runtime (downloads on first start).
# Changing EMBED_MODEL also requires wiping the ChromaDB volume (dimension mismatch otherwise).
RUN uv run python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')"

EXPOSE 8090

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]