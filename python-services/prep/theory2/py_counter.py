from collections import Counter

def countering():
    # From a list (most common use)
    c = Counter(["dog", "cat", "dog", "dog", "cat"])
    # Result: Counter({'dog': 3, 'cat': 2})

    # From a string
    c = Counter("banana")
    # Result: Counter({'a': 3, 'n': 2, 'b': 1})

    # From a dict (manual initialization)
    c = Counter({"dog": 3, "cat": 2})

    # Empty counter
    c = Counter()
    # ----------
    c = Counter(["dog", "cat"])

    print(f"counter['dog']={c["dog"]}")   # 1
    print(f"counter['fish']={c["fish"]}")  # 0  ← no KeyError, unlike a regular dict
                    #      in Java: getOrDefault("fish", 0)
    # -------------

    # Incrementing
    c = Counter()

    c["dog"] += 1   # safe even though "dog" doesn't exist yet
    c["dog"] += 1
    c["cat"] += 1
    print(f"c={c}");
    # Result: Counter({'dog': 2, 'cat': 1})

# python3 python-services/rag/theory/counter.py
def main():
    print("bla")
    countering()

if __name__ == "__main__":
    main()