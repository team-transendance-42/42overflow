 APIRouter + app.state

  APIRouter keeps route definitions out of main.py. main.py's job is
  startup orchestration — loading data, building indexes. Route handling
   is a separate concern.

  app.state is FastAPI's built-in way to share data with routers without
   circular imports. The pattern:
  - main.py builds the BM25 index and id_to_text lookup at startup,
  writes them to app.state
  - router.py reads them back via request.app.state at request time

  This avoids the circular import you'd get if router.py imported
  qa_cache from main.py while main.py imports the router from router.py.

  Pydantic models for request/response give you automatic input
  validation (empty question → 422 before your code runs) and a
  documented contract between the API and its callers.