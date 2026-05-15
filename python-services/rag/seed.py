import json
from pathlib import Path

_SEED_DIR = Path(__file__).parent / "seed"


def load_seed() -> list[dict]:
    if not _SEED_DIR.is_dir():
        raise RuntimeError(f"Seed directory not found: {_SEED_DIR}")

    pairs: list[dict] = []
    for path in sorted(_SEED_DIR.glob("*.json")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise RuntimeError(f"Could not read seed file {path.name}: {exc}") from exc
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Invalid JSON in {path.name} at line {exc.lineno}: {exc.msg}"
            ) from exc
        if not isinstance(data, list):
            raise RuntimeError(f"{path.name} must contain a JSON array")
        pairs.extend(data)

    if not pairs:
        raise RuntimeError(f"No Q&A pairs found in {_SEED_DIR} — add *.json topic files")
    return pairs


# python3 python-services/rag/seed.py
if __name__ == "__main__":
    pairs = load_seed()
    by_topic: dict[str, int] = {}
    for p in pairs:
        by_topic[p.get("topic", "?")] = by_topic.get(p.get("topic", "?"), 0) + 1
    print(f"{len(pairs)} Q&A pairs across {len(by_topic)} topics:")
    for topic, count in sorted(by_topic.items()):
        print(f"  {topic}: {count}")
