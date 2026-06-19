Tool	Purpose
venv	isolate project packages
uv	fast package/environment manager
uvicorn	runs FastAPI web server
pycache	cached compiled Python code

pyproject.toml is a Python project configuration file (modern standard): A file that tells tools like pip, uv, poetry, hatch:

“This is my project, and here is how to set it up.”

It defines how your project is:

built
installed
and which dependencies it uses

It uses TOML (a simple config language)

Example:

[project]
name = "my-app"
version = "0.1.0"
dependencies = [
    "fastapi",
    "uvicorn"
]