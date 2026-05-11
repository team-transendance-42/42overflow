import math
from collections import Counter

# What problem are we solving?
# We have a list of docs. Some words appear in every doc (like "the", "is") — those are boring, not useful for search. Some words appear in only 1 doc (like "quantum") — those are special, very useful.
# We want to give each word a score:

# boring word (appears everywhere) → low score
# special word (appears rarely) → high score
# for term, freq in df.items()
# df looks like this after counting:
# pythondf = {
#     "dog":  3,   # appeared in 3 docs
#     "cat":  1,   # appeared in 1 doc
#     "eats": 2    # appeared in 2 docs
# }
# df.items() gives us each pair one by one:
# → ("dog",  3)
# → ("cat",  1)
# → ("eats", 2)
# Each time: term = the word, freq = how many docs had it.

# pythonvectorizer["dir_size"] / (1 + freq)
# dir_size = total number of docs = let's say 3.
# For each word:
# "dog"  → 3 / (1 + 3) = 3/4 = 0.75   # common,  small number
# "cat"  → 3 / (1 + 1) = 3/2 = 1.5    # rare,    bigger number
# "eats" → 3 / (1 + 2) = 3/3 = 1.0    # medium
# The +1 in (1 + freq) is just a safety net — prevents dividing by zero if freq = 0.
# Rare words → bigger number. Common words → smaller number.
# math.log(...)
# We wrap it in log to compress the numbers. Without log, a word appearing in 1 out of 1000 docs would get a score 1000x bigger than a common word — way too extreme.
# log(0.75) = -0.28   # common word
# log(1.0)  =  0.0    # medium word
# log(1.5)  =  0.40   # rare word
# The +1 at the end just shifts everything up so no word gets a negative or zero score:
# "dog"  → -0.28 + 1 = 0.72   # common → low but still positive
# "cat"  →  0.40 + 1 = 1.40   # rare   → higher score
# "eats" →  0.0  + 1 = 1.0    # medium
# term: math.log(vectorizer["dir_size"] / (1 + freq)) + 1
# term: means — store this score under the word's name as the key:
# python{
#     "dog":  0.72,   # ← boring, low score
#     "cat":  1.40,   # ← special, high score
#     "eats": 1.0     # ← medium
# }


#dictionary comprehension is:
# { key: value for variable in collection }
# for cpp:
# you have a list of numbers
# numbers = [1, 2, 3, 4, 5]

# # you want: {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}  (number: its square)

# # normal loop 
# result = {}
# for n in numbers:
#     result[n] = n * n

# print(result)  # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
# result = {n: n * n for n in numbers}
#         ↑  ↑↑↑↑↑  ↑↑↑↑↑↑↑↑↑↑↑↑↑
#        key: value  the loop

def tokenize(text):
    return text.lower().split()

def create_vectorizer():
    return { "idf": {}, "dir_size": 0 }

def fit(vectorizer, dir):
    vectorizer["dir_size"] = len(dir)
    df = Counter() # doc frequency in dir

    for doc in dir:
        for token in set(tokenize(doc)):
            df[token] += 1

    vectorizer["idf"] = {
        term: math.log(vectorizer["dir_size"] / (1 + freq)) + 1
        for term, freq in df.items() # items(.entry() in js, term is key, freq is val)
    }

# python3 python-services/rag/theory/dict_comprehension.py
def main():
    v = create_vectorizer()
    fit(v, ["dog bites man",
            "cat eats food",
            "dog eats everything"])
    # print(v["dir_size"])
    # print(v["idf"])
    # dict comprehension:
    words = ["tralala", "cat", "elephant"]
    # len(bla) is the val, bla is the key
    result = {bla: len(bla) for bla in words}
    print(result)

    prices = {"apple": 1.0, "banana": 0.5, "cherry": 2.0}
    doubled = {key: val * 2 for key, val in prices.items()}
    print(doubled)
    # {"apple": 2.0, "banana": 1.0, "cherry": 4.0}

    expensive = {key: val for key, val in prices.items() if val > 0.6}
    print(expensive)

if __name__ == "__main__":
    main()
