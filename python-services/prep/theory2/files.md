
  pyproject.toml — declares the project: name, Python version required,  and dependencies (fastapi, httpx, uvicorn). It's Python's equivalent of package.json or Go's go.mod. This is what uv reads to know what to
  install.
-------------------------
  .venv/ — the virtual environment: an isolated folder containing the
  actual installed packages for this project only. So httpx installed  here doesn't clash with other projects. You activate it and your
  import httpx works.
------------------------
  uv.lock — locks exact versions of every installed package (including
  transitive deps) so the build is reproducible. Like package-lock.json
  or go.sum. The Dockerfile uses this to guarantee the same versions in
  the container.
