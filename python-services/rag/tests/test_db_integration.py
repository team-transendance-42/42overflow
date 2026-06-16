"""
DB integration end-to-end test.

What it proves:
  1. QAPair rows inserted into Postgres are picked up by python-rag on startup.
  2. /rag/retrieve returns those DB-sourced docs as context.
  3. Doc IDs from DB have the "db-" prefix (set in db.py) — distinguishable from seeds.

How to run (stack must be up, python-rag restarted after DB rows inserted):
  python tests/test_db_integration.py --seed         # inserts rows into DB
  python tests/test_db_integration.py --test         # queries RAG and checks results
  python tests/test_db_integration.py --seed --test  # both

Requirements:
  pip install asyncpg httpx

Edge cases:
  - If python-rag was NOT restarted after seeding, DB pairs are not indexed yet.
    The test will fail with "no db- prefixed context" — restart and retry.
  - If DATABASE_URL is not set in python-rag env, load_db_pairs() returns [] silently.
    Verify: docker compose logs python-rag | grep '[db]'
  - Questions must be specific enough that BM25/dense search retrieves the DB doc
    and not a seed doc. Generic questions may match existing seed content instead.
"""

import argparse
import asyncio
import sys

import asyncpg
import httpx

# --- config -------------------------------------------------------------------
DB_URL = "postgresql://postgres:postgres@localhost:5433/transcendance_db"
RAG_URL = "http://localhost:8090"

# QA pairs NOT in any seed file. Topics: push_swap, minishell, webserv.
DB_TEST_PAIRS = [
    {
        "question": "What sorting algorithm does push_swap use for large stacks and why is it optimal for that range?",
        "answer": (
            "push_swap uses a chunk-based approach for large stacks (100 or 500 elements). "
            "The stack is divided into value-range chunks; elements in the current chunk are "
            "pushed to stack B in roughly sorted order using ra/rb rotations to find the cheapest "
            "target position. Chunk size is tuned experimentally — chunks of 30-40 elements "
            "minimise total move count. For 100 elements the moulinette requires under 700 "
            "operations; for 500 elements under 5500. Pure insertion sort is O(n^2) and fails "
            "these limits above ~20 elements. The chunk approach achieves O(n log n) equivalent "
            "move counts."
        ),
        "topic": "push_swap",
        "source": "db-test",
        "tags": ["sorting", "chunk-sort", "optimization", "large-stack", "moulinette"],
    },
    {
        "question": "In push_swap with exactly 3 elements, what is the maximum number of operations needed and what are the cases?",
        "answer": (
            "Sorting 3 elements [a, b, c] where a<b<c requires at most 2 operations. "
            "The 6 orderings: [a,b,c] already sorted — 0 ops. [b,a,c] — sa, 1 op. "
            "[a,c,b] — rra, 1 op. [c,a,b] — ra, 1 op. [b,c,a] — ra then ra, 2 ops. "
            "[c,b,a] — sa then rra, 2 ops. Worst case is always 2 operations. "
            "The moulinette tests 3-element sort with this exact limit."
        ),
        "topic": "push_swap",
        "source": "db-test",
        "tags": ["3-elements", "small-stack", "cases", "optimal", "moulinette"],
    },
    {
        "question": "How does minishell handle heredoc and why must it fork before reading heredoc input?",
        "answer": (
            "A heredoc (<< DELIMITER) reads lines from stdin until a line matching DELIMITER "
            "appears, then makes that content the command stdin. Minishell must fork before "
            "reading heredoc input for two reasons: (1) the parent shell must not block on "
            "readline — Ctrl+C during heredoc input should kill only the reader, not the shell; "
            "(2) SIGINT during heredoc reading should cancel only the heredoc. Correct "
            "implementation: fork a child that reads lines into a pipe write-end, parent "
            "waitpid; if child is killed by SIGINT (WIFSIGNALED && WTERMSIG==SIGINT), abandon "
            "the heredoc and print a newline, matching bash behavior."
        ),
        "topic": "minishell",
        "source": "db-test",
        "tags": ["heredoc", "fork", "SIGINT", "pipe", "signal-handling"],
    },
    {
        "question": "What is CGI in webserv and how does the server pass environment variables to the CGI process?",
        "answer": (
            "CGI (Common Gateway Interface) lets a web server execute an external program and "
            "use its stdout as the HTTP response. In webserv, when a request matches a CGI "
            "location (*.py, *.php), the server: (1) forks a child; (2) sets env vars via "
            "execve envp — REQUEST_METHOD, QUERY_STRING, CONTENT_TYPE, CONTENT_LENGTH, "
            "PATH_INFO, SCRIPT_FILENAME; (3) pipes the request body to child stdin; (4) reads "
            "child stdout as the response. The server must enforce a timeout — kill child after "
            "N seconds and return 504 Gateway Timeout. Close all listening sockets in the child "
            "before execve."
        ),
        "topic": "webserv",
        "source": "db-test",
        "tags": ["CGI", "fork", "execve", "environment-variables", "timeout", "504"],
    },
]

TEST_QUERIES = [
    {
        "question": "What sorting algorithm does push_swap use for large stacks and why is it optimal?",
        "expected_topic": "push_swap",
        "expected_keyword": "chunk",
    },
    {
        "question": "How many operations does push_swap need for 3 elements?",
        "expected_topic": "push_swap",
        "expected_keyword": "moulinette",
    },
    {
        "question": "Why does minishell fork before reading heredoc input?",
        "expected_topic": "minishell",
        "expected_keyword": "heredoc",
    },
    {
        "question": "How does webserv pass environment variables to a CGI process?",
        "expected_topic": "webserv",
        "expected_keyword": "CGI",
    },
]


# --- seed ---------------------------------------------------------------------

async def seed_db():
    print(f"[seed] connecting to {DB_URL}")
    conn = await asyncpg.connect(DB_URL)

    exists = await conn.fetchval(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name='QAPair')"
    )
    if not exists:
        print("[seed] ERROR: QAPair table does not exist.")
        print("       Run: docker compose up app  (it runs prisma db push on start)")
        await conn.close()
        return False

    inserted = 0
    skipped = 0
    for pair in DB_TEST_PAIRS:
        existing = await conn.fetchval(
            'SELECT id FROM "QAPair" WHERE question = $1', pair["question"]
        )
        if existing:
            print(f"[seed] skip (exists): {pair['question'][:60]}...")
            skipped += 1
            continue

        await conn.execute(
            'INSERT INTO "QAPair" (question, answer, topic, tags, source, "createdAt", "updatedAt") '
            "VALUES ($1, $2, $3, $4, $5, NOW(), NOW())",
            pair["question"],
            pair["answer"],
            pair["topic"],
            pair["tags"],
            pair.get("source"),
        )
        print(f"[seed] inserted: {pair['question'][:60]}...")
        inserted += 1

    await conn.close()
    print(f"\n[seed] done — {inserted} inserted, {skipped} already existed")
    print("\nNext step: restart python-rag to pick up the new rows:")
    print("  docker compose restart python-rag")
    print("  docker compose logs python-rag -f   # wait for 'ChromaDB sync complete'")
    return True


# --- test ---------------------------------------------------------------------

def test_rag(verbose: bool = False):
    passed = 0
    failed = 0

    with httpx.Client(base_url=RAG_URL, timeout=30) as client:
        health = client.get("/healthz").json()
        seed_only_count = 123  # known seed count without DB
        print(f"[test] python-rag reports {health['qa_count']} total docs")
        if health["qa_count"] <= seed_only_count:
            print(f"[test] WARNING: qa_count <= {seed_only_count} (seed-only).")
            print("       DB pairs may not be loaded. Check:")
            print("       docker compose logs python-rag | grep '[db]'")
        print()

        for q in TEST_QUERIES:
            print(f"[test] Q: {q['question'][:70]}...")
            resp = client.post("/rag/retrieve", json={"question": q["question"]})

            if resp.status_code != 200:
                print(f"       FAIL — HTTP {resp.status_code}: {resp.text[:200]}")
                failed += 1
                continue

            data = resp.json()
            contexts = data["contexts"]
            confidence = data["confidence"]
            best_sim = data["best_similarity"]

            if verbose:
                print(f"       confidence={confidence:.4f}  best_similarity={best_sim:.4f}")
                for i, ctx in enumerate(contexts):
                    print(f"       [{i}] id={ctx['id']}  topic={ctx['topic']}  rrf={ctx['rrf_score']:.6f}")

            if not contexts:
                print("       FAIL — no contexts returned (off-topic gate triggered)")
                failed += 1
                continue

            db_contexts = [c for c in contexts if c["id"].startswith("db-")]
            if not db_contexts:
                ids = [c["id"] for c in contexts]
                print(f"       FAIL — no DB-sourced context. ids={ids}")
                print("              python-rag may not have been restarted after seeding.")
                failed += 1
                continue

            top_db = db_contexts[0]
            keyword = q["expected_keyword"]
            keyword_found = any(keyword.lower() in c["text"].lower() for c in db_contexts)
            if not keyword_found:
                print(f"       FAIL — keyword '{keyword}' not found in DB context text")
                failed += 1
                continue

            topic_ok = top_db["topic"] == q["expected_topic"]
            topic_note = "" if topic_ok else f" (expected topic '{q['expected_topic']}', got '{top_db['topic']}')"
            print(f"       PASS — DB doc retrieved (id={top_db['id']}, topic={top_db['topic']}){topic_note}")
            passed += 1

    print(f"\nResults: {passed} passed, {failed} failed out of {len(TEST_QUERIES)} queries")
    return failed == 0


# --- main ---------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", action="store_true", help="Insert test rows into DB")
    parser.add_argument("--test", action="store_true", help="Query RAG and verify DB docs returned")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all context IDs and scores")
    args = parser.parse_args()

    if not args.seed and not args.test:
        parser.print_help()
        sys.exit(0)

    if args.seed:
        ok = asyncio.run(seed_db())
        if not ok:
            sys.exit(1)

    if args.test:
        ok = test_rag(verbose=args.verbose)
        sys.exit(0 if ok else 1)
