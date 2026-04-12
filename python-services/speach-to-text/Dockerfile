FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Whisper and audio processing
RUN apt-get update && apt-get install -y ffmpeg git curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Install uv as the package/runtime manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY . .

CMD ["uv", "run", "python", "main.py"]