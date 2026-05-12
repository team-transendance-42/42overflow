import json
from pathlib import Path

_SEED_FILE = Path(__file__).parent / "seed.json"


def load_seed() -> list[dict]:
    return json.loads(_SEED_FILE.read_text(encoding="utf-8"))

# python3 python-services/rag/seed.py
if __name__ == "__main__":
    pairs = load_seed()
    print(f"{len(pairs)} Q&A pairs in seed.json")
    print(f"**Q** {pairs[0]['question']}\n**A** {pairs[0]['answer']}")
