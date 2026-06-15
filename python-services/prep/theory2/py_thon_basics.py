"""
Python Basics — run this file with: python3 python_basics.py
Each section is a function you can call. Uncomment the calls at the bottom to try them.
"""

# ── 1. Variables & types ──────────────────────────────────────────────────────

def variables_demo():
    name = "Alice"
    age = 25
    height = 1.75
    is_student = True

    print(name, age, height, is_student)
    print(type(name), type(age), type(height), type(is_student))

    # type conversion
    x = "42"
    print(int(x) + 1)       # 43
    print(float(x) * 2)     # 84.0
    print(str(100) + "px")  # "100px"

    # f-strings
    print(f"My name is {name} and next year I'll be {age + 1}.")


# ── 2. Strings ────────────────────────────────────────────────────────────────

def strings_demo():
    s = "Hello, World!"
    print(len(s))               # 13
    print(s.upper())            # HELLO, WORLD!
    print(s.lower())            # hello, world!
    print(s[0])                 # H  (index starts at 0)
    print(s[-1])                # !  (negative index from end)
    print(s[0:5])               # Hello
    print(s.replace("World", "Python"))  # Hello, Python!
    print(s.split(", "))        # ['Hello', 'World!']
    print("  spaces  ".strip()) # "spaces"
    print("ha" * 3)             # hahaha


# ── 3. Lists ──────────────────────────────────────────────────────────────────

def lists_demo():
    fruits = ["apple", "banana", "cherry"]

    print(fruits[0])      # apple
    print(fruits[-1])     # cherry
    print(len(fruits))    # 3

    fruits.append("mango")
    fruits.remove("banana")
    fruits[0] = "orange"
    print(fruits)         # ['orange', 'cherry', 'mango']

    # sorting
    nums = [3, 1, 4, 1, 5, 9]
    print(sorted(nums))   # [1, 1, 3, 4, 5, 9]  — new list
    nums.sort()           # modifies in place
    print(nums)

    # list comprehension — build lists in one line
    squares = [x ** 2 for x in range(6)]
    print(squares)        # [0, 1, 4, 9, 16, 25]

    evens = [x for x in range(20) if x % 2 == 0]
    print(evens)


# ── 4. Dictionaries ───────────────────────────────────────────────────────────

def dicts_demo():
    person = {"name": "Alice", "age": 25, "city": "Paris"}

    print(person["name"])          # Alice
    print(person.get("missing", "default"))  # default (safe access)

    person["email"] = "alice@example.com"
    del person["city"]
    print(person)

    # loop over items
    for key, value in person.items():
        print(f"  {key}: {value}")

    # dict comprehension
    squares = {x: x**2 for x in range(5)}
    print(squares)  # {0:0, 1:1, 2:4, 3:9, 4:16}


# ── 5. Conditionals ───────────────────────────────────────────────────────────

def conditionals_demo():
    score = 78

    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    else:
        grade = "F"

    print(f"Score {score} → Grade {grade}")

    # one-liner (ternary)
    label = "pass" if score >= 70 else "fail"
    print(label)

    # logical operators
    age, has_id = 20, True
    print("entry ok" if age >= 18 and has_id else "denied")


# ── 6. Loops ──────────────────────────────────────────────────────────────────

def loops_demo():
    # for + range
    for i in range(5):
        print(i, end=" ")   # 0 1 2 3 4
    print()

    # for with enumerate — get index and value
    animals = ["cat", "dog", "bird"]
    for i, animal in enumerate(animals):
        print(f"  [{i}] {animal}")

    # while
    count = 0
    while count < 3:
        print(f"  count = {count}")
        count += 1

    # break and continue
    for n in range(10):
        if n == 6:
            break
        if n % 2 == 0:
            continue
        print(n, end=" ")   # 1 3 5
    print()


# ── 7. Functions ──────────────────────────────────────────────────────────────

def functions_demo():
    def greet(name, greeting="Hello"):
        return f"{greeting}, {name}!"

    print(greet("Bob"))             # Hello, Bob!
    print(greet("Bob", "Hey"))      # Hey, Bob!

    # multiple return values
    def stats(nums):
        return min(nums), max(nums), sum(nums) / len(nums)

    lo, hi, avg = stats([4, 7, 2, 9, 1])
    print(f"min={lo}, max={hi}, avg={avg}")

    # *args — variable number of positional arguments
    def total(*args):
        return sum(args)

    print(total(1, 2, 3, 4))   # 10

    # **kwargs — variable keyword arguments
    def describe(**kwargs):
        for k, v in kwargs.items():
            print(f"  {k} = {v}")

    describe(color="blue", size=10, shape="circle")

    # lambda — anonymous one-liner function
    square = lambda x: x ** 2
    print(square(7))   # 49

    double = lambda x: x * 2
    print(list(map(double, [1, 2, 3])))   # [2, 4, 6]


# ── 8. Error handling ─────────────────────────────────────────────────────────

def errors_demo():
    def safe_divide(a, b):
        try:
            result = a / b
        except ZeroDivisionError:
            return "Cannot divide by zero"
        except TypeError as e:
            return f"Type error: {e}"
        else:
            return result          # runs only if no exception
        finally:
            print("  safe_divide called")  # always runs

    print(safe_divide(10, 2))    # 5.0
    print(safe_divide(10, 0))    # Cannot divide by zero
    print(safe_divide(10, "x"))  # Type error


# ── 9. Classes ────────────────────────────────────────────────────────────────

def classes_demo():
    class Animal:
        species_count = 0   # class variable (shared by all instances)

        def __init__(self, name, sound):
            self.name = name       # instance variable
            self.sound = sound
            Animal.species_count += 1

        def speak(self):
            return f"{self.name} says {self.sound}!"

        def __repr__(self):
            return f"Animal({self.name!r})"

    class Dog(Animal):
        def __init__(self, name):
            super().__init__(name, "Woof")

        def fetch(self, item):
            return f"{self.name} fetches the {item}!"

    cat = Animal("Cat", "Meow")
    dog = Dog("Rex")

    print(cat.speak())     # Cat says Meow!
    print(dog.speak())     # Rex says Woof!
    print(dog.fetch("ball"))
    print(f"Total animals: {Animal.species_count}")
    print(repr(dog))


# ── 10. File I/O ──────────────────────────────────────────────────────────────

def file_demo():
    import os

    path = "/tmp/demo_notes.txt"

    # write
    with open(path, "w") as f:
        f.writelines([f"Line {i}\n" for i in range(1, 4)])

    # read all
    with open(path, "r") as f:
        print(f.read())

    # read line by line
    with open(path, "r") as f:
        for line in f:
            print(line.strip())

    os.remove(path)


# ── 11. Useful standard library ───────────────────────────────────────────────

def stdlib_demo():
    import math
    import random
    from collections import Counter, defaultdict
    from itertools import combinations

    print(math.sqrt(2))       # 1.4142...
    print(math.pi)
    print(math.floor(3.7))    # 3
    print(math.ceil(3.2))     # 4

    random.seed(42)
    print(random.randint(1, 10))
    print(random.choice(["red", "green", "blue"]))
    lst = [1, 2, 3, 4, 5]
    random.shuffle(lst)
    print(lst)

    words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
    print(Counter(words))   # Counter({'apple': 3, 'banana': 2, 'cherry': 1})

    d = defaultdict(list)
    d["key"].append(1)      # no KeyError even though 'key' didn't exist
    print(d)

    print(list(combinations([1, 2, 3], 2)))  # [(1,2),(1,3),(2,3)]


# ─────────────────────────────────────────────────────────────────────────────
# Run sections — uncomment what you want to try
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sections = [
        ("1. Variables & types",   variables_demo),
        ("2. Strings",             strings_demo),
        ("3. Lists",               lists_demo),
        ("4. Dictionaries",        dicts_demo),
        ("5. Conditionals",        conditionals_demo),
        ("6. Loops",               loops_demo),
        ("7. Functions",           functions_demo),
        ("8. Error handling",      errors_demo),
        ("9. Classes",             classes_demo),
        ("10. File I/O",           file_demo),
        ("11. Standard library",   stdlib_demo),
    ]

    for title, fn in sections:
        print(f"\n{'─'*50}")
        print(f"  {title}")
        print('─'*50)
        fn()
