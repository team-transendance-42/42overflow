Python is a scripting and application language with a very different feel from C, C++, Java, JS, and Go.

It is dynamically typed by default.
It ships with a large standard library and a huge ecosystem.
It is common for automation, web backends, tooling, data work, and AI.
The usual workflow today is: create a project, isolate dependencies, lock them, run code.
====
Astral uv is not Python itself. It is a fast tool for managing Python projects, dependencies, virtual environments, and Python versions. Think of it as a modern replacement for a mix of pip, venv, pipx, and often pyenv.
===
Lists, dicts, sets, and tuples are the main built-ins
Everything is an object
You usually do not declare types everywhere, but type hints are common
Error handling uses try and except
==========
Python function is closer to a Go function or Java method, but lighter.
Python list is like a dynamic array.
Python dict is like a hash map.
Python module is like a source file / package unit.
Python package is a directory of modules.
===
No semicolons.
No braces.
Much less boilerplate.
Faster to write, easier to read, but easier to create messy code if you do not use tooling.
===
uv handles the boring parts of Python work:

Installing and pinning dependencies
Creating isolated environments
Running scripts in a project
Managing Python versions
Producing reproducible builds with a lock file
===
The usual modern setup is:

pyproject.toml for project metadata and dependencies
uv.lock for exact dependency versions
.venv for the local environment
The workflow you should learn first

Install Python through uv if needed.
Create a project.
Add dependencies.
Run code inside the project environment.
Lock dependencies for reproducibility.
Use formatting and linting tools.
===
Typical flow:

uv init myapp
cd myapp
uv add requests
uv run python main.py
====
If you want a script-style project, you can still use uv, but pyproject.toml is the standard starting point now.
===
A virtual environment is an isolated Python install for one project.

Why it exists:

Different projects need different package versions
Installing everything globally causes conflicts
It keeps your system Python clean

uv add requests
uv run python main.py
===
A file is usually a module
===
A folder becomes a package when it is structured correctly
====
Modern Python usually uses pyproject.toml.

That file defines:

project name
dependencies
scripts / entry points
build system config

That file defines:

project name
dependencies
scripts / entry points
build system config
===
dependencies are declared once
uv resolves them
uv.lock records exact versions

