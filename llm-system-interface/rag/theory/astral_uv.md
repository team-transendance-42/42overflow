mac os, linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
==================================

Astral's uv — The Real Win
If you go Python, uv is the game-changer:

10-100x faster than pip (C-based, concurrent downloads)
Lock files + reproducibility — Like Go's go.sum; no more "works on my machine"
Single executable — No Python version manager needed; ships with Python
Minimal overhead — 15MB vs venv baggage

Best for your case: Use uv with a pyproject.toml + uv.lock for reproducible deployments across containers.