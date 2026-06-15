pip install flake8

Check a file
flake8 main.py

check an entire project:
flake8 .

===================
Ignore specific rules
Command line:
flake8 --ignore=E501 .

Or create .flake8:

[flake8]
ignore = E501
max-line-length = 88
Example workflow
pip install flake8
cd my_project
flake8 .
=======================
A context manager 
=======================
is an object that automatically performs setup and cleanup.

The most common example is opening a file.

Without a context manager
# main.py

file = open("data.txt", "r")
content = file.read()
file.close()

Problem:

If an exception occurs before close(), the file stays open.
With a context manager
# main.py

with open("data.txt", "r") as file:
    content = file.read()

When the with block ends:

file is automatically closed
even if an exception occurs
---
with open("data.txt", "r") as file:
    print(file.read())
    raise Exception("Boom!")

Even though an exception is raised, Python still closes the file before propagating the exception.
----
Database connections

Instead of:

# main.py

conn = create_connection()
# use conn
conn.close()

Use:

# main.py

with create_connection() as conn:
    # use conn

The connection is automatically closed afterward.
---
Creating your own context manager
# main.py

class MyResource:
    def __enter__(self):
        print("Opening")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Closing")

Usage:

# main.py

with MyResource() as resource:
    print("Working")

Output:

Opening
Working
Closing

Python calls:

__enter__() when entering the with block.
__exit__() when leaving it, even if an exception happens
----
When working with:

files
sockets
database connections
locks
network resources

they want code like:

with open(...)
with socket(...)
with lock:

because cleanup is guaranteed. This prevents resource leaks and makes crashes less likely to leave files or connections open.
---
Type hints

Type hints tell Python (and programmers) what type is expected.

# main.py

def greet(name: str) -> None:
    print(f"Hello {name}")
name: str → parameter must be a string
-> None → function returns nothing
---
Type hints for variables
# main.py

name: str = "Petya"
age: int = 51
price: float = 9.99
----
For more complex types:

# main.py

from typing import List

numbers: List[int] = [1, 2, 3]

Modern Python (3.9+) usually uses:

# main.py

numbers: list[int] = [1, 2, 3]

Dictionary:

# main.py

ages: dict[str, int] = {
    "John": 30,
    "Mary": 25
}

Optional value:

# main.py

def find_user(id: int) -> str | None:
    ...

Meaning: returns either a string or None.
---
What is static type checking?

Normally Python checks types while running.

# main.py

def add(a: int, b: int) -> int:
    return a + b

add("hello", "world")

Python runs this and produces:

helloworld

No complaint!

Static type checking analyzes the code before running it and warns:

Argument 1 has incompatible type "str"; expected "int"
---
MYPY
---
mypy is the most popular static type checker for Python.

Install:
pip install mypy

Run:
mypy main.py
error: Argument 1 to "add" has incompatible type "str"; expected "int"
error: Argument 2 to "add" has incompatible type "str"; expected "int"
---------------------
docstrings
---------------------

A docstring is a string written inside a function or class that explains what it does.

It is placed right after the definition.

Python reads it as documentation.

def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b

	view it:
	print(add.__doc__)
----------
Why PEP 257?

PEP 257 is the official Python rule for writing docstrings.

It defines:

where docstrings go
how they should be formatted
what information they should contain
Google style (most common in schools)
def add(a: int, b: int) -> int:
    """
    Add two integers.

    Args:
        a (int): First number.
        b (int): Second number.

    Returns:
        int: Sum of a and b.
    """
    return a + b
---

NumPy style (also accepted in many projects)
def add(a: int, b: int) -> int:
    """
    Add two integers.

    Parameters
    ----------
    a : int
        First number
    b : int
        Second number

    Returns
    -------
    int
        Sum of a and b
    """
    return a + b
---
for classes:
class Car:
    """
    Represents a car object.

    Attributes:
        brand (str): The car brand.
        year (int): Manufacturing year.
    """

    def __init__(self, brand: str, year: int):
        self.brand = brand
        self.year = year
------------------------------------------
PYTHON CODE STYLE
------------------------------------------
type hints (mypy-safe)
docstrings (PEP 257 / Google style)
flake8-friendly structure
context for functions + classes
------------------------------------------
for docker services:
install pip, uv, pipx or any other package manager
debug: Run the main script in debug mode using Python’s built-in debugger (e.g.,pdb).
• clean: Remove temporary files or caches (e.g., __pycache__, .mypy_cache) to
keep the project environment clean.
----
• lint: Execute the commands flake8 . and mypy . --warn-return-any
--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs
--check-untyped-defs
============================
Create test programs to verify project functionality (not submitted or graded). Use
frameworks like pytest or unittest for unit tests, covering edge cases.
• Include a .gitignore file to exclude Python artifacts.
• It is recommended to use virtual environments (e.g., venv or conda) for dependency
isolation during development.