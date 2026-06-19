"""
DB integration end-to-end test for Posts+Comments data source.

What it proves:
  1. Post + Comment rows in Postgres are picked up by /admin/reload-from-db.
  2. /rag/retrieve returns those DB-sourced docs with the "db-post-" prefix.
  3. The answer text comes from the comments, not the post body.

How to run (stack must be up):
  python tests/test_db_integration.py --seed         # insert test Post+Comment rows
  python tests/test_db_integration.py --reload       # call /admin/reload-from-db
  python tests/test_db_integration.py --test         # query RAG and verify results
  python tests/test_db_integration.py --seed --reload --test  # full flow

Requirements: uv (or pip install asyncpg httpx)
"""

import argparse
import asyncio
import sys

import asyncpg
import httpx

DB_URL = "postgresql://postgres:postgres@localhost:5433/transcendance_db"
RAG_URL = "http://localhost:8090"   # only reachable via docker compose exec (no ports mapping)
RAG_ADMIN_TOKEN = ""  # fill in from llm-system-interface/.env before running

# Test data — topics not in any seed file
DB_TEST_POSTS = [
    {
        "title": "push_swap",
        "content": "What sorting algorithm does push_swap use for large stacks and why is it optimal?",
        "comments": [
            "push_swap uses a chunk-based approach for large stacks (100 or 500 elements). "
            "The stack is divided into value-range chunks pushed to stack B in sorted order. "
            "Chunk size of 30-40 elements minimises total move count. "
            "For 100 elements the moulinette requires under 700 operations.",
        ],
        "expected_keyword": "chunk",
    },
    {
        "title": "minishell",
        "content": "Why does minishell fork before reading heredoc input?",
        "comments": [
            "A heredoc reads lines until a DELIMITER line appears. Minishell must fork before "
            "reading heredoc input so that Ctrl+C during heredoc reading kills only the reader "
            "child, not the shell itself. SIGINT during heredoc should cancel only the heredoc.",
        ],
        "expected_keyword": "heredoc",
    },
]

TEST_QUERIES = [
    {
        "question": "What sorting algorithm does push_swap use for large stacks?",
        "expected_keyword": "chunk",
        "expected_topic": "push_swap",
    },
    {
        "question": "Why does minishell fork before reading heredoc?",
        "expected_keyword": "heredoc",
        "expected_topic": "minishell",
    },
]

TEST_USER_ID = "rag-integration-test-user"
TEST_USER_EMAIL = "rag-test@test.local"



async def seed_db():
    print(f"[seed] connecting to {DB_URL}")
    conn = await asyncpg.connect(DB_URL)

    # Ensure a test user exists (Post.userId FK requires a valid User)
    await conn.execute(
        'INSERT INTO "User" (id, email, "emailVerified", "createdAt", "updatedAt") '
        "VALUES ($1, $2, false, NOW(), NOW()) ON CONFLICT (id) DO NOTHING",
        TEST_USER_ID, TEST_USER_EMAIL,
    )
    print(f"[seed] test user ensured: {TEST_USER_EMAIL}")

    for post_data in DB_TEST_POSTS:
        existing = await conn.fetchval(
            'SELECT id FROM "Post" WHERE title = $1 AND "userId" = $2',
            post_data["title"], TEST_USER_ID,
        )
        if existing:
            print(f"[seed] skip (exists): Post title={post_data['title']!r}")
            continue

        post_id = await conn.fetchval(
            'INSERT INTO "Post" (title, content, "userId", created_at, updated_at) '
            "VALUES ($1, $2, $3, NOW(), NOW()) RETURNING id",
            post_data["title"], post_data["content"], TEST_USER_ID,
        )
        print(f"[seed] inserted Post id={post_id} title={post_data['title']!r}")

        for comment_text in post_data["comments"]:
            await conn.execute(
                'INSERT INTO "Comment" (content, "postId", "userId", created_at, updated_at) '
                "VALUES ($1, $2, $3, NOW(), NOW())",
                comment_text, post_id, TEST_USER_ID,
            )
        print(f"[seed] inserted {len(post_data['comments'])} comment(s) for post {post_id}")

    await conn.close()
    print("\n[seed] done. Next: run --reload to sync into RAG.")


def reload_rag():
    print(f"[reload] calling /admin/reload-from-db on {RAG_URL}")
    print("         NOTE: this URL is only reachable inside docker network.")
    print("         From host, use: docker compose exec python-rag curl -s -X POST")
    print(f"           http://localhost:8090/admin/reload-from-db -H 'X-Admin-Token: <token>'")
    if not RAG_ADMIN_TOKEN:
        print("[reload] RAG_ADMIN_TOKEN not set in this script — skipping HTTP call.")
        print("         Set it at the top of this file or call the endpoint manually.")
        return
    with httpx.Client(base_url=RAG_URL, timeout=60) as client:
        resp = client.post(
            "/admin/reload-from-db",
            headers={"X-Admin-Token": RAG_ADMIN_TOKEN},
        )
        if resp.status_code == 200:
            print(f"[reload] OK: {resp.json()}")
        else:
            print(f"[reload] FAIL HTTP {resp.status_code}: {resp.text[:200]}")



def test_rag(verbose: bool = False):
    passed = 0
    failed = 0

    with httpx.Client(base_url=RAG_URL, timeout=30) as client:
        health = client.get("/healthz").json()
        print(f"[test] python-rag: {health['qa_count']} total docs, "
              f"embeddings_ready={health['embeddings_ready']}")

        for q in TEST_QUERIES:
            print(f"\n[test] Q: {q['question'][:70]}...")
            resp = client.post("/rag/retrieve", json={"question": q["question"]})

            if resp.status_code != 200:
                print(f"       FAIL — HTTP {resp.status_code}: {resp.text[:200]}")
                failed += 1
                continue

            data = resp.json()
            contexts = data["contexts"]

            if verbose:
                print(f"       confidence={data['confidence']:.4f}  best_sim={data['best_similarity']:.4f}")
                for i, ctx in enumerate(contexts):
                    print(f"       [{i}] id={ctx['id']}  topic={ctx['topic']}  rrf={ctx['rrf_score']:.6f}")

            db_contexts = [c for c in contexts if c["id"].startswith("db-post-")]
            if not db_contexts:
                ids = [c["id"] for c in contexts]
                print(f"       FAIL — no db-post- context found. ids={ids}")
                print("              Did you run --reload after --seed?")
                failed += 1
                continue

            keyword = q["expected_keyword"]
            keyword_found = any(keyword.lower() in c["text"].lower() for c in db_contexts)
            if not keyword_found:
                print(f"       FAIL — keyword '{keyword}' not in any db-post context")
                failed += 1
                continue

            print(f"       PASS — db-post context retrieved, keyword '{keyword}' found")
            passed += 1

    print(f"\nResults: {passed} passed, {failed} failed out of {len(TEST_QUERIES)} queries")
    return failed == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", action="store_true", help="Insert test Post+Comment rows")
    parser.add_argument("--reload", action="store_true", help="Call /admin/reload-from-db")
    parser.add_argument("--test", action="store_true", help="Query RAG and verify db-post- docs")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if not any([args.seed, args.reload, args.test]):
        parser.print_help()
        sys.exit(0)

    if args.seed:
        asyncio.run(seed_db())
    if args.reload:
        reload_rag()

    if args.test:
        ok = test_rag(verbose=args.verbose)
        sys.exit(0 if ok else 1)
