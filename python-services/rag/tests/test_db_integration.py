"""
DB integration end-to-end test.

What it proves:
  1. QAPair rows inserted into Postgres are picked up by python-rag on startup.
  2. The /rag/retrieve endpoint returns those DB-sourced docs as context.
  3. Doc IDs from DB have the "db-" prefix (set in db.py) — distinguishable from seeds.

How to run (stack must be up, python-rag restarted after DB rows inserted):
  python tests/test_db_integration.py --seed        # inserts rows into DB
  python tests/test_db_integration.py --test        # queries RAG and checks results
  python tests/test_db_integration.py --seed --test # do both

Requirements:
  pip install asyncpg httpx

Theory:
  db.py runs at startup inside lifespan(). It calls load_db_pairs() which fetches all
  QAPair rows and merges them with seed data (DB wins on duplicate questions).
  After --seed, you MUST restart python-rag so the new rows are embedded and indexed.
  The --test flag queries /rag/retrieve and checks that returned context IDs start with
  "db-", proving the answer came from DB, not any seed file.

Edge cases:
  - If python-rag was NOT restarted after seeding, the DB pairs won't be indexed yet.
    The test will fail with "no db- prefixed context" — this is correct behavior, not a bug.
  - If DATABASE_URL is not set in python-rag's env, load_db_pairs() returns [] silently.
    Check: docker compose logs python-rag | grep '\[db\]'
  - Questions must be specific enough that BM25/dense search retrieves the DB doc,
    not a seed doc. Generic questions (e.g. "what is a mutex") might retrieve codexion
    seed docs instead.
"""

import argparse
import asyncio
import sys

import asyncpg
import httpx

# --- config -------------------------------------------------------------------
DB_URL = "postgresql://postgres:postgres@localhost:5433/transcendance_db"
RAG_URL = "http://localhost:8090"

# QA pairs that do NOT appear in any seed file.
# Topics: push_swap, minishell, webserv — none are in the 8 seed files.
# Answers are deliberately unique enough that only these DB rows match the questions.
DB_TEST_PAIRS = [
    {
        "question": "What sorting algorithm does push_swap use for large stacks and why is it optimal for that range?",
        "answer": (
            "push_swap uses a chunk-based radix sort variant for large stacks (>20 elements). "
            "The stack is divided into chunks by value range; elements of the current chunk are "
            "pushed to stack B in roughly sorted order using ra/rb rotations to find the cheapest "
            "position. The chunk size is tuned experimentally — chunks of ~30-40 elements minimize "
            "the total move count. For exactly 100 elements the target is under 700 operations; for "
            "500 elements under 5500. Pure insertion sort is O(n^2) operations and fails these limits "
            "above ~20 elements. Radix/chunk sort achieves O(n log n) equivalent move counts."
        ),
        "topic": "push_swap",
        "difficulty": "hard",
        "source": "db-test",
        "tags": ["sorting", "chunk-sort", "radix", "optimization", "stack"],
    },
    {
        "question": "How does minishell handle heredoc and why must it fork before reading heredoc input?",
        "answer": (
            "A heredoc (<< DELIMITER) reads lines from stdin until a line matching DELIMITER appears, "
            "then makes that content available as the command's stdin. Minishell must fork before "
            "reading heredoc input because: (1) the parent shell must not block on readline — the user "
            "can Ctrl+C during heredoc input and only the heredoc reader should die, not the shell "
            "itself; (2) signals (SIGINT) sent during heredoc reading should cancel only the current "
            "heredoc, not terminate the shell process. The correct implementation: fork a child that "
            "reads heredoc lines into a pipe, parent waits; if child is killed by SIGINT (waitpid "
            "returns WIFSIGNALED && WTERMSIG==SIGINT), the heredoc is abandoned and a newline is "
            "printed, matching bash behavior."
        ),
        "topic": "minishell",
        "difficulty": "hard",
        "source": "db-test",
        "tags": ["heredoc", "fork", "SIGINT", "pipe", "signal-handling"],
    },
    {
        "question": "What is CGI in webserv and how does the server pass environment variables to the CGI process?",
        "answer": (
            "CGI (Common Gateway Interface) is a protocol for a web server to execute an external "
            "program and use its stdout as the HTTP response body. In webserv, when a request matches "
            "a CGI-enabled location (e.g. *.py, *.php), the server: (1) forks a child process; "
            "(2) sets environment variables via execve's envp argument — including REQUEST_METHOD, "
            "QUERY_STRING, CONTENT_TYPE, CONTENT_LENGTH, PATH_INFO, SCRIPT_FILENAME; (3) pipes the "
            "request body to the child's stdin; (4) reads the child's stdout as the response body. "
            "The server must handle the case where the CGI script times out (kill child after N "
            "seconds, return 504 Gateway Timeout). The child must NOT inherit the server's listening "
            "socket — close it in the child before execve to avoid port conflicts if the child forks "
            "further."
        ),
        "topic": "webserv",
        "difficulty": "hard",
        "source": "db-test",
        "tags": ["CGI", "fork", "execve", "environment-variables", "HTTP"],
    },
    {
        "question": "In push_swap with exactly 3 elements, what is the maximum number of operations needed and what are the cases?",
        "answer": (
            "Sorting 3 elements requires at most 2 operations. There are 6 possible orderings of "
            "[a, b, c] where a<b<c is sorted. Already sorted [a,b,c]: 0 ops. [b,a,c]: sa → 1 op. "
            "[a,c,b]: rra → 1 op (or sa then ra: 2 ops — but rra is cheaper). [c,a,b]: ra → 1 op. "
            "[b,c,a]: rra → wait, [b,c,a] needs: sa gives [c,b,a], rra gives [a,c,b] — wrong. "
            "Correct: [b,c,a] → ra → [c,a,b] → ra → [a,b,c]: 2 ops. Or sa → [c,b,a] → rra → "
            "[a,c,b] → sa → [a,b,c]: 3 ops — worse. Best: [b,c,a] needs 2 ops (ra; ra). "
            "[c,b,a]: sa → [b,c,a] → ra → [c,a,b] — wrong. Correct: [c,b,a] → sa → [b,c,a] then "
            "rra → [a,b,c]... wait [b,c,a] rra = [a,b,c]: yes, 2 ops (sa; rra). So worst case is "
            "2 operations. The moulinette tests 3-element sort with this exact limit."
        ),
        "topic": "push_swap",
        "difficulty": "medium",
        "source": "db-test",
        "tags": ["3-elements", "operations", "cases", "optimal", "moulinette"],
    },
]

# For each DB pair, the exact question string used to test retrieval.
# These must semantically match the question above well enough to pass the cosine gate.
TEST_QUERIES = [
    {
        "question": "What sorting algorithm does push_swap use for large stacks and why is it optimal for that range?",
        "expected_topic": "push_swap",
        "expected_keyword": "chunk",
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
    {
        "question": "How many operations does push_swap need to sort exactly 3 elements?",
        "expected_topic": "push_swap",
        "expected_keyword": "3",
    },
]


# --- seed ---------------------------------------------------------------------

async def seed_db():
    print(f"[seed] connecting to {DB_URL}")
    conn = await asyncpg.connect(DB_URL)

    # Check table exists
    exists = await conn.fetchval(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name='QAPair')"
    )
    if not exists:
        print("[seed] ERROR: QAPair table does not exist.")
        print("       Run: DATABASE_URL=... npx prisma db push")
        print("       or restart the app container (it runs prisma db push on start).")
        await conn.close()
        return False

    inserted = 0
    skipped = 0
    for pair in DB_TEST_PAIRS:
        existing = await conn.fetchval(
            'SELECT id FROM "QAPair" WHERE question = $1', pair["question"]
        )
        if existing:
            print(f"[seed] skip (already exists): {pair['question'][:60]}...")
            skipped += 1
            continue

        await conn.execute(
            'INSERT INTO "QAPair" (question, answer, topic, difficulty, source, tags) '
            "VALUES ($1, $2, $3, $4, $5, $6)",
            pair["question"],
            pair["answer"],
            pair["topic"],
            pair.get("difficulty"),
            pair.get("source"),
            pair.get("tags", []),
        )
        print(f"[seed] inserted: {pair['question'][:60]}...")
        inserted += 1

    await conn.close()
    print(f"[seed] done — {inserted} inserted, {skipped} already existed")
    print()
    print("IMPORTANT: restart python-rag to pick up the new rows:")
    print("  docker compose restart python-rag")
    print("  docker compose logs python-rag -f   # wait for 'ChromaDB sync complete'")
    return True


# --- test ---------------------------------------------------------------------

def test_rag(verbose: bool = False):
    passed = 0
    failed = 0

    with httpx.Client(base_url=RAG_URL, timeout=30) as client:
        # Sanity check: healthz shows expected doc count
        health = client.get("/healthz").json()
        print(f"[test] python-rag reports {health['qa_count']} total docs")
        if health["qa_count"] <= 123:
            print("[test] WARNING: qa_count is <= 123 (seed-only count).")
            print("       DB pairs may not have been loaded. Check:")
            print("       docker compose logs python-rag | grep '\\[db\\]'")

        print()

        for q in TEST_QUERIES:
            print(f"[test] question: {q['question'][:70]}...")
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

            # Check 1: must return at least one context
            if not contexts:
                print(f"       FAIL — no contexts returned (off-topic gate triggered?)")
                failed += 1
                continue

            # Check 2: at least one context must have a "db-" prefixed ID
            db_contexts = [c for c in contexts if c["id"].startswith("db-")]
            if not db_contexts:
                print(f"       FAIL — no DB-sourced context (all ids: {[c['id'] for c in contexts]})")
                print(f"              python-rag may not have been restarted after seeding.")
                failed += 1
                continue

            # Check 3: top DB context should match expected topic
            top_db = db_contexts[0]
            if top_db["topic"] != q["expected_topic"]:
                print(f"       WARN  — expected topic '{q['expected_topic']}', got '{top_db['topic']}'")

            # Check 4: expected keyword in context text
            keyword = q["expected_keyword"]
            matched_text = any(keyword.lower() in c["text"].lower() for c in db_contexts)
            if not matched_text:
                print(f"       FAIL — keyword '{keyword}' not found in any DB context text")
                failed += 1
                continue

            print(f"       PASS  — DB doc retrieved (id={top_db['id']}, topic={top_db['topic']})")
            passed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed out of {len(TEST_QUERIES)} queries")
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
