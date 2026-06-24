#FastAPI
#Creates the web application.
from fastapi import FastAPI, Request, Header, Depends

# to run: 1. pip install fastapi uvicorn but from python-rag dir!!
# 2. uvicorn 10_fastapi:app --reload // from python-rag, start the server, 10_fastapi is the file name, rmv .py
# 3. Open browser: http://127.0.0.1:8000/
# 4. http://127.0.0.1:8000/req
# 5. http://127.0.0.1:8000/profile
#FastAPI also generates documentation automatically:
# 6. http://127.0.0.1:8000/docs

app = FastAPI()

@app.get("/")
def home():
    return {"message": "hello"}

@app.get("/req")
async def req(request: Request):
    return {"url": str(request.url)}

@app.get("/head")
def head(api_key: str = Header()):
    return {"key": api_key}

def get_current_user():
    return {"name": "Petya"}

@app.get("/profile")
def profile(user=Depends(get_current_user)):
    return user

"""
app.include_router(rag_router)

  FastAPI is built on top of Starlette's routing system. The app object (a FastAPI instance) has one central routing table. include_router merges
  a separate APIRouter's routes into that table.

  Without APIRouter — all routes live in one file:
  app = FastAPI()

  @app.post("/rag/retrieve") ...
  @app.post("/admin/sync-chroma") ...
  @app.get("/healthz") ...

  With APIRouter — routes are defined in isolation, mounted at the end:
  # router.py
  router = APIRouter()

  @router.post("/rag/retrieve") ...   # no app needed here

  rom router import router as rag_router
  app.include_router(rag_router)      # merges all of router's routes into app

  APIRouter is a blueprint — it holds route definitions but has no HTTP server. include_router stamps them into the real app. You can also pass a
  prefix:
  app.include_router(rag_router, prefix="/api/v1")
  # /rag/retrieve becomes /api/v1/rag/retrieve


"""
