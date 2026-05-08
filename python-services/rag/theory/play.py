def play1():
    name = "Bla"
    age = 28
    is_student = False

    print(name, age, is_student)
    print(type(name), type(age), type(is_student))
    print(f"My name is {name} and next year I'll be {age + 1}.")

def type_conver():
    x = "42"
    print(int(x) + 1)       # 43
    # print(int("abc"))       # ValueError: invalid literal for int() with base 10: 'abc'
    print(float(x) * 2)     # 84.0
    print(str(100) + "px")  # "100px"

def play_str():
    s = "tra la, la, la!"
    print("===== str =========")
    print(len(s))               # 13
    print(s.upper())            # HELLO, WORLD!
    print(s.lower())            # hello, world!
    print(s[0])                 # H  (index starts at 0)
    print(s[-1])                # !  (negative index from end)
    print(s[0:5])               # Hello
    print(s.replace("World", "Python"))  # Hello, Python!
    print(s.split(","))        # ['Hello', 'World!']
    print("  spaces  ".strip()) # "spaces"
    print("ha" * 3)             # hahaha
    print("===== end str =========")

def play_list():
    # fruits = ["apple", "banana", "cherry"]

    # print(fruits[0])      # apple
    # print(fruits[-1])     # cherry
    # print(len(fruits))    # 3

    # fruits.append("mango")
    # fruits.remove("banana")
    # fruits[0] = "orange"
    # print(fruits)         # ['orange', 'cherry', 'mango']

    # # sorting
    # nums = [3, 1, 4, 1, 5, 9]
    # print(sorted(nums))   # [1, 1, 3, 4, 5, 9]  — new list
    # nums.sort()           # modifies in place
    # print(nums)

    # list comprehension — build lists in one line
    squares = [x ** 2 for x in range(6)] # from 0 to 5
    print(squares)

    evens = [x for x in range(20) if x % 2 == 0]
    print(evens)

def play_dict():
    person = {
        "name": "Alice",
        "age": 30,
        "is_student": True
    }

    print(person["name"])  # Alice
    print(person.get("age"))  # 30
    print(person.get("height", "unknown"))  # unknown

    person["age"] = 31
    person["city"] = "New York"
    print(person)

def play_loops():
    for i in range(5):
        # print(i) # on new line
        print(i, end=" ")  # on same line
    print()  # newline

    # for with enumerate — get index and value
    animals = ["cat", "dog", "bird"]
    for i, animal in enumerate(animals):
        print(f"[{i}]: {animal}")

def play_funcs():
    # multiple return values
    def stats(nums):
        return min(nums), max(nums), sum(nums) / len(nums)
    lo, hi, avg = stats([1, 2, 3, 4, 5])
    print(f"min={lo}, max={hi}, avg={avg}")

     # *args — variable number of positional arguments
    def total(*args):
        return sum(args)
    print(total(1,2,3,4))  # 10

    # **kwargs — variable keyword arguments
    def describe(**kwargs):
        for key, value in kwargs.items():
            print(f"{key}: {value}")
    describe(name="Alice", age=30, city="NY")

    # lambda — anonymous one-liner function
    cubic = lambda x: x ** 3
    print(f"cubic(5): {cubic(5)}")  # 125
    print(f"map(cubic, [1, 2, 3]): {list(map(cubic, [1, 2, 3]))}")  # [1, 8, 27]

def play_err():
    def safe_divide(a, b):
        try:
            result = a / b
        except ZeroDivisionError:
            return "Cannot divide by zero!"
        except TypeError as e:
            return f"TypeError: {e}"
        else:
            return result
        finally:
            print("safe_divide was called.")
    
    print(safe_divide(10, 2))  # 5.0
    print(safe_divide(10, 0))  # Cannot divide by zero!
    print(safe_divide(10, "a"))  # TypeError: unsupported operand

def classes_bla():
    class Animal:
        species_count = 0; # class var, shared by all instances

        def __init__(self, name, sound):
            self.name = name; # instance var, unique to each instance
            self.sound = sound;
            Animal.species_count += 1

        def speak(self):
            return f"{self.name} says {self.sound}"

    cat = Animal("Cat", "meow")
    print(cat.speak())  # Cat says meow

#  python3 python-services/rag/theory/play.py
def main():
    # type_conver()
    # play_str()
    # play_list()
    # play_dict()
    # play_loops()
    # play_funcs()
    # play_err()
    classes_bla()

# Python entry point
if __name__ == "__main__":
    main()
    play1()
