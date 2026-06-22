"""
Populate Postgres with fake Posts + Comments for manual RAG testing.

3 fake users post and answer each other across topics NOT in any seed file
(push_swap, minishell, webserv, philosophers, ft_printf) — so you can clearly
see what the RAG picks up after calling /admin/reload-from-db.

Seed content is already in RAG at startup. These posts appear only after sync,
making the before/after difference obvious both in the browser and in RAG.

Usage (stack must be up, run from python-services/rag/):
  uv run python dev_populate.py           # insert all fake posts
  uv run python dev_populate.py --clean   # delete bot posts first, re-insert

After running, trigger RAG sync (from project root):
  docker compose exec python-rag \\
    curl -s -X POST http://localhost:8090/admin/reload-from-db \\
    -H "X-Admin-Token: My!Favourite#RAG\\$Token&Is%Longer^Than*Your(Entire)Codebase~42overflow<3"

Then visit https://localhost:8443/posts to see the posts in the browser.
"""

import argparse
import asyncio
import os

import asyncpg

USERS = [
    {"id": "fake-user-happyface22",    "email": "happyface22@overflow.local",    "name": "HappyFace22"},
    {"id": "fake-user-revolution12",   "email": "revolution12@overflow.local",   "name": "Revolution12"},
    {"id": "fake-user-mysteryuser",    "email": "mysteryuser@overflow.local",    "name": "Mystery User"},
]

HF = USERS[0]["id"]   # HappyFace22
RV = USERS[1]["id"]   # Revolution12
MY = USERS[2]["id"]   # Mystery User

# Each post has an author, a title (project name), a question, and a list of
# comments — each comment has its own author so it looks like a real thread.
POSTS = [
    {
        "author": HF,
        "title": "push_swap",
        "content": "What is the cheapest way to sort exactly 5 elements in push_swap?",
        "comments": [
            {
                "author": RV,
                "content": (
                    "For 5 elements: push 3 to B with pb pb pb, sort the 2 remaining in A "
                    "with sa if needed, then insert each B element back into A at the cheapest "
                    "position using ra/rra + pa. The moulinette expects at most 12 operations."
                ),
            },
            {
                "author": MY,
                "content": (
                    "Also worth knowing: hardcode the 6 orderings for 3 elements as a lookup. "
                    "With 5 elements you push 2 to B, solve the 3-element case, then insert. "
                    "This is faster than a generic algorithm for small sizes."
                ),
            },
        ],
    },
    {
        "author": RV,
        "title": "push_swap",
        "content": "How does the chunk algorithm handle 100 elements and what chunk size is optimal?",
        "comments": [
            {
                "author": MY,
                "content": (
                    "Divide 100 values into chunks of ~20 by value range. Push each chunk to B — "
                    "if the element belongs to the current chunk, pb; otherwise ra. Inside B, "
                    "use rb/rrb to keep smaller values near the top. Then pull back to A cheapest-first. "
                    "Chunk size 20-25 keeps you under 700 operations for 100 elements."
                ),
            },
        ],
    },
    {
        "author": MY,
        "title": "minishell",
        "content": "Why should minishell NOT fork before running a builtin like cd or export?",
        "comments": [
            {
                "author": HF,
                "content": (
                    "Builtins modify the shell's own state — cd changes the working directory, "
                    "export sets an env variable. If you fork first, only the child is affected "
                    "and the parent shell never sees the change. Always execute builtins directly "
                    "in the parent process. Fork only for external commands."
                ),
            },
            {
                "author": RV,
                "content": (
                    "Good rule of thumb: if the command is in your builtin list (cd, echo, pwd, "
                    "export, unset, env, exit) — no fork. Everything else: fork + execve. "
                    "Check the builtin list before you ever call fork()."
                ),
            },
        ],
    },
    {
        "author": HF,
        "title": "minishell",
        "content": "How do I correctly update $? after a child process is killed by a signal?",
        "comments": [
            {
                "author": MY,
                "content": (
                    "Use WIFSIGNALED and WTERMSIG after waitpid. The exit status for a signal kill "
                    "is 128 + signal number (bash convention). So SIGINT (signal 2) → exit status 130. "
                    "WIFEXITED + WEXITSTATUS gives the normal exit code. "
                    "Store the result in your shell struct and update it before showing the next prompt."
                ),
            },
        ],
    },
    {
        "author": RV,
        "title": "webserv",
        "content": "When should I use Transfer-Encoding: chunked instead of Content-Length?",
        "comments": [
            {
                "author": HF,
                "content": (
                    "Use chunked when you don't know the total body size before you start sending — "
                    "mainly CGI output. Content-Length requires knowing the size upfront. "
                    "Chunked format: each chunk starts with its hex size on its own line, then the data, "
                    "then \\r\\n. A zero-length chunk signals end of body. HTTP/1.1 requires both."
                ),
            },
            {
                "author": MY,
                "content": (
                    "For static files always use Content-Length — you know the file size from stat(). "
                    "Only CGI responses genuinely need chunked. Simpler to buffer CGI output and "
                    "send Content-Length if the output is small enough to fit in memory."
                ),
            },
        ],
    },
    {
        "author": MY,
        "title": "webserv",
        "content": "How does poll() work and why is non-blocking I/O required for webserv?",
        "comments": [
            {
                "author": RV,
                "content": (
                    "poll() watches a set of fds and returns when any are ready to read or write — "
                    "so one thread handles many clients without blocking on any single one. "
                    "Set sockets non-blocking with fcntl(fd, F_SETFL, O_NONBLOCK). "
                    "Event loop: add all fds to poll set → call poll() → iterate ready fds → "
                    "read/write available data → update connection state. Never call read() on "
                    "a fd poll() didn't mark ready."
                ),
            },
        ],
    },
    {
        "author": HF,
        "title": "philosophers",
        "content": "What is the simplest way to prevent deadlock in the dining philosophers problem?",
        "comments": [
            {
                "author": MY,
                "content": (
                    "Resource ordering: philosopher i always picks up fork min(i, (i+1)%N) before "
                    "max(i, (i+1)%N). This breaks the circular wait — at least one philosopher "
                    "always gets both forks. Alternatively: odd philosophers pick right fork first, "
                    "even pick left. Both approaches work and are simple to implement."
                ),
            },
            {
                "author": RV,
                "content": (
                    "Another approach: allow at most N-1 philosophers to attempt eating simultaneously "
                    "using a semaphore initialised to N-1. The Nth philosopher always waits, ensuring "
                    "at least one can always proceed. Cleaner for large N but adds an extra sync primitive."
                ),
            },
        ],
    },
    {
        "author": RV,
        "title": "philosophers",
        "content": "How do I detect data races in my philosophers implementation with helgrind?",
        "comments": [
            {
                "author": HF,
                "content": (
                    "Run: valgrind --tool=helgrind ./philo 4 410 200 200. "
                    "Common races: last_meal timestamp and the death flag read by the monitor "
                    "thread while philosopher threads write. Fix: give each philosopher a mutex "
                    "for its own state. The monitor locks the same mutex before reading. "
                    "Never read a shared variable without its mutex held."
                ),
            },
        ],
    },
    {
        "author": MY,
        "title": "ft_printf",
        "content": "How do variadic arguments work in ft_printf — what is va_arg actually doing?",
        "comments": [
            {
                "author": HF,
                "content": (
                    "va_start initialises a va_list pointing to the first variadic argument on the stack. "
                    "va_arg(ap, type) reads the next argument as the given type and advances the internal "
                    "pointer. va_end cleans up. You must pass the correct type — va_arg(ap, int) for a "
                    "char* is undefined behaviour. Match the type to what the format specifier expects."
                ),
            },
            {
                "author": RV,
                "content": (
                    "Important: char and short are promoted to int when passed as variadic args "
                    "(default argument promotions). So %c uses va_arg(ap, int) and casts to char, "
                    "not va_arg(ap, char). Same for %hd — read as int, cast to short. "
                    "This trips up many ft_printf implementations."
                ),
            },
        ],
    },
    {
        "author": HF,
        "title": "ft_printf",
        "content": "How should %p handle a NULL pointer — what does the real printf output?",
        "comments": [
            {
                "author": MY,
                "content": (
                    "On Linux, printf(\"%p\", NULL) outputs '(nil)'. Check for NULL first and write "
                    "that string. For non-NULL pointers: cast to uintptr_t, format as lowercase hex "
                    "with '0x' prefix. Width and precision flags apply to the full string including "
                    "the prefix. The subject may not require (nil) but matching real printf behaviour "
                    "is good practice and impresses evaluators."
                ),
            },
        ],
    },
]


async def ensure_users(conn) -> None:
    for u in USERS:
        await conn.execute(
            """
            INSERT INTO "User" (id, email, name, "emailVerified", "createdAt", "updatedAt")
            VALUES ($1, $2, $3, false, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
            """,
            u["id"], u["email"], u["name"],
        )
    names = ", ".join(u["name"] for u in USERS)
    print(f"[users] ready: {names}")


async def ensure_subjects(conn) -> dict[str, int]:
    """For each unique title in POSTS: use existing Subject or create one.
    Returns {title: subject_id} map for use in insert_posts."""
    unique_titles = list(dict.fromkeys(entry["title"] for entry in POSTS))
    subject_map: dict[str, int] = {}

    for title in unique_titles:
        slug = title.lower().strip().replace(" ", "-")
        existing_id = await conn.fetchval(
            'SELECT id FROM "Subject" WHERE slug = $1', slug
        )
        if existing_id is not None:
            subject_map[title] = existing_id
            print(f"[subjects] using existing: {title!r} → id={existing_id}")
        else:
            new_id = await conn.fetchval(
                """
                INSERT INTO "Subject" (name, slug, created_at, updated_at)
                VALUES ($1, $2, NOW(), NOW())
                RETURNING id
                """,
                title, slug,
            )
            subject_map[title] = new_id
            print(f"[subjects] created: {title!r} → id={new_id}")

    return subject_map


async def clean_posts(conn) -> None:
    ids = [u["id"] for u in USERS]
    comment_count = await conn.fetchval(
        'SELECT COUNT(*) FROM "Comment" WHERE "userId" = ANY($1::text[])', ids
    )
    post_count = await conn.fetchval(
        'SELECT COUNT(*) FROM "Post" WHERE "userId" = ANY($1::text[])', ids
    )
    await conn.execute('DELETE FROM "Comment" WHERE "userId" = ANY($1::text[])', ids)
    await conn.execute('DELETE FROM "Post" WHERE "userId" = ANY($1::text[])', ids)
    print(f"[clean] deleted {post_count} posts and {comment_count} comments")


async def insert_posts(conn, subject_map: dict[str, int]) -> tuple[int, int]:
    inserted = 0
    skipped = 0

    for entry in POSTS:
        subject_id = subject_map[entry["title"]]
        existing = await conn.fetchval(
            'SELECT id FROM "Post" WHERE "userId" = $1 AND title = $2 AND content = $3',
            entry["author"], entry["title"], entry["content"],
        )
        if existing:
            skipped += 1
            continue

        post_id = await conn.fetchval(
            """
            INSERT INTO "Post" (title, content, "userId", "subjectId", created_at, updated_at)
            VALUES ($1, $2, $3, $4, NOW(), NOW()) RETURNING id
            """,
            entry["title"], entry["content"], entry["author"], subject_id,
        )

        for comment in entry["comments"]:
            await conn.execute(
                """
                INSERT INTO "Comment" (content, "postId", "userId", created_at, updated_at)
                VALUES ($1, $2, $3, NOW(), NOW())
                """,
                comment["content"], post_id, comment["author"],
            )

        author_name = next(u["name"] for u in USERS if u["id"] == entry["author"])
        print(f"[insert] Post #{post_id} by {author_name}: [{entry['title']}] {entry['content'][:55]}...")
        inserted += 1

    return inserted, skipped


async def main(clean: bool) -> None:
    db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/transcendance_db")
    print(f"[db] connecting to {db_url.split('@')[-1]}")
    conn = await asyncpg.connect(db_url)
    try:
        await ensure_users(conn)
        subject_map = await ensure_subjects(conn)
        if clean:
            await clean_posts(conn)
        inserted, skipped = await insert_posts(conn, subject_map)
        print(f"\n[done] inserted={inserted}  skipped={skipped}  total={len(POSTS)} posts")

        if inserted > 0:
            print("\nNext: call POST /admin/seed-postgres, then POST /admin/sync-chroma.")
    finally:
        await conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Insert fake dev posts for RAG testing")
    parser.add_argument("--clean", action="store_true", help="Delete all fake posts first, then re-insert")
    args = parser.parse_args()
    asyncio.run(main(clean=args.clean))
