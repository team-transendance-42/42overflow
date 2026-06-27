# RAG Sync Guide

At startup the RAG loads only seed data (JSON files). DB content is added on demand.

---

## Option 1 — Real user posts only

Use this after real users have posted questions and comments in the browser.

From the project root:

```bash
bash reload_rag.sh
```

The response shows how many posts were picked up, e.g.:

```json
{"status":"ok","total_docs":107,"db_docs":10,"seed_docs":97,...}
```

**Requirement:** a post must have at least one comment to be included — a question with no answer has nothing useful for the LLM.

---

## Option 2 — Fake data + real posts

`dev_populate.py` inserts 10 fake posts across push_swap / minishell / webserv / philosophers / ft_printf written by three fake users (HappyFace22, Revolution12, Mystery User). These topics are not in the seed files, so the before/after difference is obvious.

From the project root:

```bash
cd python-services/rag && uv run python dev_populate.py && cd ../..
bash reload_rag.sh
```

To wipe the fake posts and re-insert fresh:

```bash
cd python-services/rag && uv run python dev_populate.py --clean && cd ../..
bash reload_rag.sh
```

---

## Notes

- `reload_rag.sh` is at the project root and calls `POST /admin/sync-chroma` inside the container.
- The reload rebuilds BM25, NumpyIndex, and ChromaDB without restarting the container.
- Future improvement: automate the reload on a schedule (e.g. twice a day).
