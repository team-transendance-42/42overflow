"""
End-to-end flow (not a unit test):
  1. Load all pairs from seed.json
  2. Print the last entry
  3. Embed it via Ollama
  4. Store it in ChromaDB
  5. Retrieve it back and print its vector

Run: docker exec -it 42overflow-python-rag-1 bash // enter container
     uv run python -m tests.flow_seed_embed_store
Requires: Ollama + ChromaDB running (docker compose up -d)
"""
import asyncio

from embedder import embed_texts, format_doc, make_doc_hash
from seed import load_seed
from store import ensure_collection, retrieve, upsert


async def run() -> None:
    # 1. load all pairs
    pairs = load_seed()
    print(f"[seed] loaded {len(pairs)} pairs from seed.json")

    # 2. last entry
    last = pairs[-1]
    print("\n[last entry]")
    print(f"  topic:      {last.get('topic', '')}")
    print(f"  difficulty: {last.get('difficulty', '')}")  # we dont have this field
    print(f"  Q: {last['question']}")
    print(f"  A: {last['answer'][:120]}{'...' if len(last['answer']) > 120 else ''}")

    # 3. embed
    text = format_doc(last["question"], last["answer"])
    doc_id = make_doc_hash(last["question"], last["answer"])

    print("\n[embed] sending to Ollama...")
    embeddings = await embed_texts([text])
    vec = embeddings[0]
    print(f"  embedding dim: {len(vec)}")
    print(f"  first 5 values: {[round(v, 6) for v in vec[:5]]}")

    # 4. store
    ensure_collection()
    upsert(
        ids=[doc_id],
        documents=[text],
        embeddings=embeddings,
        metadatas=[{
            "topic": last.get("topic", ""),
            "difficulty": last.get("difficulty", ""),
            "doc_hash": doc_id,
        }],
    )
    print(f"\n[store] upserted 1 doc  id={doc_id[:16]}...")

    # 5. retrieve and print vectors
    result = retrieve([doc_id])
    stored_vec = result["embeddings"][0]
    print(f"\n[retrieve] got {len(result['ids'])} record(s)")
    print(f"  doc preview: {result['documents'][0][:80]}...")
    print(f"  metadata:    {result['metadatas'][0]}")
    print(f"  vector dim:  {len(stored_vec)}")
    print(f"  vector:      [{stored_vec[0]:.6f}, {stored_vec[1]:.6f}, {stored_vec[2]:.6f}"
          f", ... , {stored_vec[-1]:.6f}]")


if __name__ == "__main__":
    asyncio.run(run())
