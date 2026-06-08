
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero!")
    return a / b

def main():
    try:
        result = divide(10, 0)
    except ValueError as e:
        print("Error:", e)
=======
Python uses exceptions for error handling, similar to Java and C++ (but unlike C, which uses return codes).
When an error occurs, Python “raises” (throws) an exception.
If not handled, the program stops and prints a traceback.
You can “catch” (handle) exceptions using try/except blocks.
=======
try:
    # code that might raise an error
    risky_operation()
except SomeException as e:
    # handle the error
    print("Error:", e)

=======
catch all exceptions (not recommended):
try:
    do_something()
except Exception as e:
    print("Something went wrong:", e)
=======
Use raise to throw an exception.
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero!")
    return a / b
======
class MyError(Exception):
    pass

raise MyError("Something custom went wrong!")
======
C: Uses return codes (e.g., -1, NULL). No built-in exceptions.
Java/C++: Uses try/catch, throw, finally. Python is similar but uses except instead of catch.
Python: No checked exceptions (unlike Java). All exceptions are unchecked.
======
try:
    with open("file.txt") as f:
        data = f.read()
except FileNotFoundError:
    print("File not found!")
=======

