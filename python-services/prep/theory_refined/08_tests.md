 1. Seed test data
  cd python-services/rag
  uv run python tests/test_db_integration.py --seed

  # 2. Restart python-rag
  cd /sgoinfre/pekatsar/42overflow
  docker compose restart python-rag

  # 3. Watch logs until you see "ChromaDB sync complete"
  docker compose logs python-rag -f

  # 4. Run integration test
  cd python-services/rag
  uv run python tests/test_db_integration.py --test --verbose
