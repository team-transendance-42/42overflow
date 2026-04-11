mac os, linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
---
| sh passes the downloaded script directly to the shell for execution
=============================
step 2:
making that directory available on your shell PATH.(the shell only finds commands in directories listed in PATH)
It installed the binaries into /home/pekatsar/.local/bin.
It added two commands there: uv and uvx.
---
Do this for the current shell session:
source $HOME/.local/bin/env
---
To make it permanent:

If you use zsh, add this line to ~/.zshrc:
source $HOME/.local/bin/env
If you use bash, add the same line to ~/.bashrc.
Reload your shell:
source ~/.zshrc
or
source ~/.bashrc
Then verify with:
uv --version
==================================

Astral's uv — The Real Win
If you go Python, uv is the game-changer:

10-100x faster than pip (C-based, concurrent downloads)
Lock files + reproducibility — Like Go's go.sum; no more "works on my machine"
Single executable — No Python version manager needed; ships with Python
Minimal overhead — 15MB vs venv baggage

Best for your case: Use uv with a pyproject.toml + uv.lock for reproducible deployments across containers.
==============================
uv manages project dependencies and environments, with support for lockfiles, workspaces, and more, similar to rye or poetry: