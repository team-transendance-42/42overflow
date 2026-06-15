

sorted([3, 1, 2])  # [1, 2, 3]

scores = [0.2, 0.9, 0.5]
list(enumerate(scores))
# [(0, 0.2), (1, 0.9), (2, 0.5)]


"""
lambda creates a small anonymous function.
x is the input to the lambda function.
In this case, x will be one tuple from enumerate(scores).
x[0] is the index
x[1] is the score

[:n]
slice syntax
takes only the first n results

sorted():
if you give it plain values, it sorts by those values
if you give it tuples, it sorts by the first item in each tuple by default
"""
top_n = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:5]

pairs = [(0, 0.2), (1, 0.9), (2, 0.5)]
sorted(pairs, key=lambda x: x[1])
# [(0, 0.2), (2, 0.5), (1, 0.9)]

""" 
A tuple is a sequence type in Python, like a list, but it is immutable.

list: can change
tuple: cannot change
A tuple uses parentheses: t = (1, 2, 3)
You can also write it without parentheses in some cases:
t = 1, 2, 3  # this is also a tuple
Tuples use indexes just like lists:

t = (10, 20, 30)

print(t[0])  # 10
print(t[1])  # 20
print(t[2])  # 30
Use a tuple when the data should not change.
t = (1, 2, 3)
# t[0] = 10   # error
A single item tuple needs a comma: a = (5,)
a = (5) 
Here’s a tutorial on tuples in the same style.

What is a tuple?
A tuple is a sequence type in Python, like a list, but it is immutable.

list: can change
tuple: cannot change
Example:

That means:

3 is the first item
5 is the second item
Syntax
A tuple uses parentheses:

You can also write it without parentheses in some cases:

That is still a tuple.

Accessing items
Tuples use indexes just like lists:

t[0] means first item
t[1] means second item
Why tuple?
Use a tuple when the data should not change.

Example:

This says:

x = 100
y = 200
These values should stay fixed.

Immutable means what?
You cannot modify a tuple after creating it.

This fails because tuples are immutable.

One-item tuple
A single item tuple needs a comma:

Without the comma: a = (5)
That is just an integer, not a tuple.

point = (3, 5)
x, y = point
print(x)  # 3
print(y)  # 5
"""