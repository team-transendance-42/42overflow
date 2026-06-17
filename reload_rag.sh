#!/bin/bash
# Sync RAG with the database. Run from the project root.
#
# Option 1 — real user posts only:
#   bash reload_rag.sh
#
# Option 2 — fake data (push_swap/minishell/webserv/philosophers/ft_printf)
#             posted by HappyFace22, Revolution12, Mystery User, then real posts:
#   cd python-services/rag && uv run python dev_populate.py && cd ../..
#   bash reload_rag.sh
#
# Add --clean to dev_populate.py to wipe fake posts and re-insert fresh:
#   cd python-services/rag && uv run python dev_populate.py --clean && cd ../..
#   bash reload_rag.sh
#
# Note: a post must have at least one comment to be picked up by the RAG.
# The response shows total_docs, db_docs, seed_docs, and topics indexed.

docker compose exec python-rag curl -s -X POST \
  http://localhost:8090/admin/reload-from-db \
  -H 'X-Admin-Token: My!Favourite-RAG-Token-Is-Longer-Than-Your-Entire-Codebase~42overflow'
