import json
from pathlib import Path

_SEED_FILE = Path(__file__).parent / "seed.json"


def load_seed() -> list[dict]:
    try:
        text = _SEED_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise RuntimeError(f"Seed file not found: {_SEED_FILE}") from None
    except OSError as exc:
        raise RuntimeError(f"Could not read seed file {_SEED_FILE}: {exc}") from exc

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Seed file contains invalid JSON at line {exc.lineno}: {exc.msg}"
        ) from exc

# python3 python-services/rag/seed.py
if __name__ == "__main__":
    pairs = load_seed()
    print(f"{len(pairs)} Q&A pairs in seed.json")
    print(f"**Q** {pairs[0]['question']}\n**A** {pairs[0]['answer']}")
