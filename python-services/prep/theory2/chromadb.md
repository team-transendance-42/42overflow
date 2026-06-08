ChromaDB is a vector database that stores and manages your embeddings (vectors). Here’s how it’s typically set up and used in your context:

How do we connect to ChromaDB?
The connection and setup are usually handled in your store.py file (with functions like ensure_collection, upsert, get_existing_hashes).
When you call ensure_collection(), it makes sure the ChromaDB collection (like a table) exists.
upsert() sends your vectors and metadata to ChromaDB.
get_existing_hashes() fetches info about what’s already stored.
----------------

How is ChromaDB set up?
In development, ChromaDB often runs as a Docker container.
It stores data in a volume (a folder on your disk or managed by Docker), so your vectors are persistent even if the container restarts.
The database can be local (on your machine) or remote (on a server).
What does it store?
It keeps your vectors (embeddings), document IDs, and metadata (like topic, difficulty, hash).
You can search, update, or delete vectors as needed.
Summary
ChromaDB acts as a persistent “vector store.”
Your code connects to it using Python client libraries (handled in store.py).
It stores all your question/answer vectors and related info, usually in a Docker volume for persistence.
--------------------

