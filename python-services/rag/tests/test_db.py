"""
Unit tests for db.py helper functions — no DB connection needed.
Run: cd python-services/rag && uv run python -m pytest tests/test_db.py -v
"""
from db import _normalize_topic, _row_to_pair


def test_normalize_topic_lowercase():
    assert _normalize_topic("A-Maze-ing") == "a-maze-ing"


def test_normalize_topic_spaces():
    assert _normalize_topic("Agent Smith") == "agent-smith"


def test_normalize_topic_already_clean():
    assert _normalize_topic("minishell") == "minishell"


def test_normalize_topic_strips_whitespace():
    assert _normalize_topic("  push_swap  ") == "push_swap"


class _FakeRow(dict):
    """Minimal asyncpg Row stand-in — dict with attribute access."""
    def __getattr__(self, key):
        return self[key]


def test_row_to_pair_basic():
    row = _FakeRow(id=7, project_name="A-Maze-ing", question="What is A-Maze-ing?", answers="It is a maze generator.")
    pair = _row_to_pair(row)
    assert pair["id"] == "db-post-7"
    assert pair["question"] == "What is A-Maze-ing?"
    assert pair["answer"] == "It is a maze generator."
    assert pair["topic"] == "a-maze-ing"
    assert pair["tags"] == ["a-maze-ing"]
    assert pair["source"] == "db-post"


def test_row_to_pair_none_answers_becomes_empty_string():
    row = _FakeRow(id=1, project_name="minishell", question="Q?", answers=None)
    pair = _row_to_pair(row)
    assert pair["answer"] == ""


def test_row_to_pair_topic_used_as_tag():
    row = _FakeRow(id=2, project_name="Agent Smith", question="Q?", answers="A.")
    pair = _row_to_pair(row)
    assert pair["topic"] == "agent-smith"
    assert "agent-smith" in pair["tags"]
