from collections import Counter
import math
import re

# return list of str: split text into tokens(words) by white space, rmv any not alphanumeric char(replace with " ") or 1 char 
def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if len(t) > 1]

class TFIDFVectorizer:
    def __init__(self) -> None:
        self.idf = {}
        self.corpus_size = 0 

    # sets corpus_size and idf
    def fit(self, corpus):
        self.corpus_size = len(corpus)
        df = Counter()

        for doc in corpus: # dir
            for token in set(tokenize(doc)):  # unordered
                df[token] += 1

        self.idf = {
            term: math.log(self.corpus_size / (1 + freq)) + 1
            for term, freq in df.items()
        }

# python3 python-services/rag/theory/self.py
# dict(map) order is guaranteed, set not
def main():
    vectorizer = TFIDFVectorizer()
    vectorizer.fit(["dog bites man", "cat eats food"])
    # now self.corpus_size = 2
    # now self.idf = {"dog": ..., "bites": ..., ...}

    print(vectorizer.corpus_size)  # 2
    print(vectorizer.idf)          # {"dog": 0.71, ...}

if __name__ == "__main__":
    main()