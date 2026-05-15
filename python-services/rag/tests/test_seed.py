"""
Run: uv run python -m tests.test_seed
-m for module
"""

import json
import pytest
from collections import Counter
from unittest.mock import patch

# VALID_TOPICS = {"c", "python", "networking", "maze", "drone", "agentsmith", "rag"} # todo if we want to?
REQUIRED_FIELDS = {"question", "answer", "topic", "tags"}


def test_seed():
    from seed import load_seed

    pairs = load_seed()

    assert len(pairs) >= 1, f"Expected at least 1 pair, got {len(pairs)}"

    for i, pair in enumerate(pairs):
        missing = REQUIRED_FIELDS - pair.keys()
        assert not missing, f"Pair {i} missing fields: {missing}"
        assert pair["question"].strip(), f"Pair {i} empty question"
        assert pair["answer"].strip(), f"Pair {i} empty answer"
        # assert pair["topic"] in VALID_TOPICS, f"Pair {i} invalid topic: {pair['topic']}"
        assert isinstance(pair["tags"], list) and pair["tags"], f"Pair {i} tags must be non-empty list"

    dist = Counter(p["topic"] for p in pairs)
    print(f"✓ seed: {len(pairs)} pairs loaded, all fields valid")
    print(f"  topic distribution: {dict(sorted(dist.items()))}")


def test_merge():
    from main import _merge

    seed = [
        {"question": "What is X?", "answer": "seed answer", "topic": "c",
         "difficulty": "beginner", "tags": ["x"]},
    ]
    db = [
        {"question": "What is X?", "answer": "db answer", "topic": "c",
         "difficulty": "beginner", "tags": ["x"]},          # same question → DB wins
        {"question": "What is Y?", "answer": "db only", "topic": "python",
         "difficulty": "intermediate", "tags": ["y"]},      # new from DB
    ]
    result = _merge(seed, db)

    assert len(result) == 2, f"Expected 2, got {len(result)}"
    by_q = {r["question"]: r for r in result}
    assert by_q["What is X?"]["answer"] == "db answer", "DB should overwrite seed"
    assert "What is Y?" in by_q, "DB-only pair should be included"
    print("✓ merge: DB overwrites seed on duplicate question, additives included")


def test_load_seed_missing_dir():
    with patch("seed._SEED_DIR") as mock_dir:
        mock_dir.is_dir.return_value = False
        with pytest.raises(RuntimeError, match="Seed directory not found"):
            from seed import load_seed
            load_seed()


def test_load_seed_bad_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not valid json {")
    with patch("seed._SEED_DIR") as mock_dir:
        mock_dir.is_dir.return_value = True
        mock_dir.glob.return_value = [bad_file]
        with pytest.raises(RuntimeError, match="Invalid JSON"):
            from seed import load_seed
            load_seed()


if __name__ == "__main__":
    test_seed()
    test_merge()
    print("\nAll tests passed.")
