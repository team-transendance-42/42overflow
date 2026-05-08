import math  # sqrt, log | math ops
import re  # sub | regex
from collections import Counter  # Counter | counting
from pathlib import Path  # Path | file paths

def load_documents(directory: str) -> dict[str, str]:
    docs = {}  # 1. Empty dictionary(map: key-val) to hold results
    for path in Path(directory).glob("*.md"):  # glob is genexpr
        docs[path.name] = path.read_text(encoding="utf-8")  # 2a-c. Read and store file content
    return docs  # 3. Return the dictionary

# chunk size 150, overlap 30: 1-150, 121-270, 241-390, etc. (overlap 30 means next chunk starts 30 words before previous chunk ends)
def chunk_text(text: str, chunk_size: int = 150, overlap: int = 30) -> list[str]:
    words = text.split() # split str into arr on whitespace
    chunks: list[str] = [] # []string{} in Go — empty result array
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(words):
            break
        start += chunk_size - overlap
    return chunks


# python3 python-services/rag/theory/rag_cpy.py
def main():
    docs_dir = str(Path(__file__).parent) # get current file's parent dir as string
    docs = load_documents(docs_dir)
    print(f"Found {len(docs)} files")
    for filename, content in docs.items(): # items() buildin method returns list of (key, value) tuples(str, str)
        # print(f"{filename}: {len(content)} chars")
        chunks = chunk_text(content, 5, 2) # chunk size 5 words, overlap 2 words
        print("Chunks:")
        print(f"{filename}: {len(chunks)} chunks")
        for i, chunk in enumerate(chunks[:3]): # print first 3 chunks
            print(f"  Chunk {i+1}: {chunk}\n")
if __name__ == "__main__":
    main()
    