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


# ── OLD per-post tests (kept for comparison) ──────────────────────────────────
# class _FakeRow(dict):
#     """Minimal asyncpg Row stand-in — dict with attribute access."""
#     def __getattr__(self, key):
#         return self[key]
#
#
# def test_row_to_pair_basic():
#     row = _FakeRow(id=7, project_name="A-Maze-ing", question="What is A-Maze-ing?", answers="It is a maze generator.")
#     pair = _row_to_pair(row)
#     assert pair["id"] == "db-post-7"
#     assert pair["question"] == "What is A-Maze-ing?"
#     assert pair["answer"] == "It is a maze generator."
#     assert pair["topic"] == "a-maze-ing"
#     assert pair["tags"] == ["a-maze-ing"]
#     assert pair["source"] == "db-post"
#
#
# def test_row_to_pair_none_answers_becomes_empty_string():
#     row = _FakeRow(id=1, project_name="minishell", question="Q?", answers=None)
#     pair = _row_to_pair(row)
#     assert pair["answer"] == ""
#
#
# def test_row_to_pair_topic_used_as_tag():
#     row = _FakeRow(id=2, project_name="Agent Smith", question="Q?", answers="A.")
#     pair = _row_to_pair(row)
#     assert pair["topic"] == "agent-smith"
#     assert "agent-smith" in pair["tags"]
#
#
# def test_row_to_pair_topic_from_subject_slug():
#     row = _FakeRow(id=10, project_name="push_swap", question="Q?", answers="A.")
#     pair = _row_to_pair(row)
#     assert pair["topic"] == "push_swap"
#     assert pair["tags"] == ["push_swap"]
#
#
# def test_row_to_pair_question_is_full_text():
#     row = _FakeRow(
#         id=11,
#         project_name="minishell",
#         question="Why no fork for builtins?\n\nBecause builtins modify shell state.",
#         answers="Fork only for externals.",
#     )
#     pair = _row_to_pair(row)
#     assert "Why no fork" in pair["question"]
#     assert "shell state" in pair["question"]
# ── END OLD tests ─────────────────────────────────────────────────────────────


# ── NEW per-comment tests ─────────────────────────────────────────────────────
class _FakeRow(dict):
    """Minimal asyncpg Row stand-in — dict with attribute access."""
    def __getattr__(self, key):
        return self[key]


def test_row_to_pair_uses_comment_id_in_doc_id():
    row = _FakeRow(comment_id=42, project_name="A-Maze-ing",
                   question="What is A-Maze-ing?", answer="It is a maze generator.")
    pair = _row_to_pair(row)
    assert pair["id"] == "db-comment-42"


def test_row_to_pair_source_is_db_comment():
    row = _FakeRow(comment_id=1, project_name="minishell", question="Q?", answer="A.")
    pair = _row_to_pair(row)
    assert pair["source"] == "db-comment"


def test_row_to_pair_answer_field():
    row = _FakeRow(comment_id=5, project_name="webserv",
                   question="Why non-blocking?", answer="So one thread handles many clients.")
    pair = _row_to_pair(row)
    assert pair["answer"] == "So one thread handles many clients."


def test_row_to_pair_topic_normalised():
    row = _FakeRow(comment_id=3, project_name="Agent Smith", question="Q?", answer="A.")
    pair = _row_to_pair(row)
    assert pair["topic"] == "agent-smith"
    assert pair["tags"] == ["agent-smith"]


def test_row_to_pair_question_preserved():
    row = _FakeRow(
        comment_id=11,
        project_name="minishell",
        question="Why no fork for builtins?\n\nBecause builtins modify shell state.",
        answer="Fork only for externals.",
    )
    pair = _row_to_pair(row)
    assert "Why no fork" in pair["question"]
    assert "shell state" in pair["question"]


def test_row_to_pair_empty_answer_becomes_empty_string():
    """Comment content should never be NULL (DB constraint), but guard anyway."""
    row = _FakeRow(comment_id=9, project_name="push_swap", question="Q?", answer=None)
    pair = _row_to_pair(row)
    assert pair["answer"] == ""
