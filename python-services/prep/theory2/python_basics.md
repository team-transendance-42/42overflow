# Python Basics — Beginner Tutorial

## What is Python?
Python is a high-level, interpreted programming language. "High-level" means it reads like English. "Interpreted" means code runs line by line without a separate compile step.

```bash
python3 --version   # check version
python3             # open interactive shell (REPL)
```

---

## Variables and Data Types

A variable is a named box that holds a value. Python figures out the type automatically (dynamic typing).

```python
name = "Alice"        # str  — text, always in quotes
age = 25              # int  — whole number
height = 1.75         # float — decimal number
is_student = True     # bool — True or False

print(name, age)      # Alice 25
print(type(age))      # <class 'int'>
```

### Type conversion
```python
x = "42"
y = int(x)     # "42" → 42
z = float(x)   # "42" → 42.0
s = str(100)   # 100  → "100"
```

---

## Strings

```python
greeting = "Hello, World!"

print(len(greeting))          # 13  — number of characters
print(greeting.upper())       # HELLO, WORLD!
print(greeting.lower())       # hello, world!
print(greeting[0])            # H  — indexing starts at 0
print(greeting[0:5])          # Hello  — slicing [start:end]
print(greeting.replace("World", "Python"))  # Hello, Python!

# f-strings — easiest way to embed variables in text
name = "Bob"
print(f"My name is {name} and I am {2026 - 2000} years old.")
```

---

## Numbers and Math

```python
a, b = 10, 3

print(a + b)   # 13  addition
print(a - b)   # 7   subtraction
print(a * b)   # 30  multiplication
print(a / b)   # 3.333...  division (always float)
print(a // b)  # 3   integer division (floor)
print(a % b)   # 1   modulo (remainder)
print(a ** b)  # 1000  power (10³)
```

---

## Lists

A list is an ordered, mutable collection of items (can hold mixed types).

```python
fruits = ["apple", "banana", "cherry"]

print(fruits[0])       # apple  — first element
print(fruits[-1])      # cherry — last element
print(len(fruits))     # 3

fruits.append("mango")    # add to end
fruits.remove("banana")   # remove by value
fruits[0] = "orange"      # change element

# loop through a list
for fruit in fruits:
    print(fruit)

# list slicing
print(fruits[1:3])    # elements at index 1 and 2
```

---

## Dictionaries

A dictionary stores key-value pairs (like a real dictionary: word → definition).

```python
person = {
    "name": "Alice",
    "age": 25,
    "city": "Paris"
}

print(person["name"])         # Alice
print(person.get("age"))      # 25

person["email"] = "alice@example.com"   # add new key
person["age"] = 26                       # update value
del person["city"]                       # delete key

# loop through dictionary
for key, value in person.items():
    print(f"{key}: {value}")
```

---

## Conditionals (if / elif / else)

```python
score = 75

if score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
else:
    print("F")
```

### Comparison operators
```python
==   # equal
!=   # not equal
>    # greater than
<    # less than
>=   # greater or equal
<=   # less or equal
```

### Logical operators
```python
and   # both conditions must be True
or    # at least one must be True
not   # reverses the condition

if age >= 18 and has_id:
    print("Access granted")
```

---

## Loops

### for loop — iterate a known number of times
```python
for i in range(5):        # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):    # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):  # 0, 2, 4, 6, 8 (step=2)
    print(i)
```

### while loop — repeat while condition is True
```python
count = 0
while count < 5:
    print(count)
    count += 1     # count = count + 1
```

### break and continue
```python
for i in range(10):
    if i == 5:
        break       # exit the loop entirely
    if i % 2 == 0:
        continue    # skip this iteration
    print(i)        # prints 1, 3
```

---

## Functions

A function is a reusable block of code. Define once, call many times.

```python
def greet(name):
    return f"Hello, {name}!"

message = greet("Alice")
print(message)    # Hello, Alice!
```

### Default parameters
```python
def power(base, exponent=2):   # exponent defaults to 2
    return base ** exponent

print(power(3))      # 9  (3²)
print(power(3, 3))   # 27 (3³)
```

### Multiple return values
```python
def min_max(numbers):
    return min(numbers), max(numbers)

lo, hi = min_max([4, 1, 9, 2])
print(lo, hi)   # 1 9
```

---

## Error Handling

```python
try:
    x = int(input("Enter a number: "))
    result = 10 / x
    print(result)
except ValueError:
    print("That's not a number!")
except ZeroDivisionError:
    print("Cannot divide by zero!")
finally:
    print("Done.")   # runs no matter what
```

---

## File I/O

```python
# write a file
with open("notes.txt", "w") as f:
    f.write("Hello, file!\n")

# read a file
with open("notes.txt", "r") as f:
    content = f.read()
    print(content)

# read line by line
with open("notes.txt", "r") as f:
    for line in f:
        print(line.strip())
```

`with` automatically closes the file when the block ends.

---

## List Comprehensions

A concise way to build lists.

```python
# standard loop
squares = []
for x in range(5):
    squares.append(x ** 2)

# same thing as a comprehension
squares = [x ** 2 for x in range(5)]   # [0, 1, 4, 9, 16]

# with condition
evens = [x for x in range(10) if x % 2 == 0]  # [0, 2, 4, 6, 8]
```

---

## Modules and Imports

Modules are files of reusable code. Python ships with many built-in ones.

```python
import math
print(math.sqrt(16))    # 4.0
print(math.pi)          # 3.14159...

import random
print(random.randint(1, 10))   # random int between 1 and 10
print(random.choice(["a", "b", "c"]))

from datetime import datetime
now = datetime.now()
print(now.year, now.month, now.day)
```

---

## Classes (Object-Oriented Programming)

A class is a blueprint. An object is an instance of that blueprint.

```python
class Dog:
    def __init__(self, name, breed):   # constructor
        self.name = name               # instance attributes
        self.breed = breed

    def bark(self):
        return f"{self.name} says Woof!"

    def info(self):
        return f"{self.name} is a {self.breed}"

my_dog = Dog("Rex", "Labrador")
print(my_dog.bark())    # Rex says Woof!
print(my_dog.info())    # Rex is a Labrador
```

### Inheritance — a child class extends a parent
```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

class Cat(Animal):
    def speak(self):                  # override parent method
        return f"{self.name} says Meow!"

cat = Cat("Whiskers")
print(cat.speak())   # Whiskers says Meow!
```

---

## Common Built-in Functions

```python
len([1, 2, 3])          # 3
sum([1, 2, 3])          # 6
max([1, 2, 3])          # 3
min([1, 2, 3])          # 1
sorted([3, 1, 2])       # [1, 2, 3]
reversed([1, 2, 3])     # iterator → list(reversed(...))
enumerate(["a","b"])    # (0,'a'), (1,'b')
zip([1,2], ["a","b"])   # (1,'a'), (2,'b')
map(str, [1, 2, 3])     # ['1', '2', '3']
filter(lambda x: x>1, [0,1,2,3])  # [2, 3]
```

---

## Key Concepts Summary

| Concept | What it is |
|---|---|
| Variable | Named storage for a value |
| Function | Reusable block of code that takes input and returns output |
| List | Ordered, mutable sequence |
| Dict | Key-value pairs |
| Loop | Repeat code |
| Condition | Branch code based on True/False |
| Class | Blueprint for objects |
| Module | File of reusable code |
| Exception | Runtime error that can be caught |
