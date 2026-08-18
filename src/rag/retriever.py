import os
import chromadb
from chromadb.utils import embedding_functions


def query_policies(query_text: str, n_results: int = 2):
    db_path = os.path.join("data", "chroma_db")

    if not os.path.exists(db_path):
        print(f"❌ Error: Vector database not found at '{db_path}'. Run ingest.py first!")
        return []

    # Initialize ChromaDB client and embedding function
    chroma_client = chromadb.PersistentClient(path=db_path)
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    # Access collection
    collection = chroma_client.get_collection(
        name="company_policies", embedding_function=embedding_fn
    )

    # Perform similarity search
    results = collection.query(query_embeddings=None, query_texts=[query_text], n_results=n_results)

    return results["documents"][0]


if __name__ == "__main__":
    test_query = "What is the SLA for a P1 critical incident?"
    print(f"🔍 Searching ChromaDB for: '{test_query}'...\n")

    matched_chunks = query_policies(test_query)
    for i, chunk in enumerate(matched_chunks, 1):
        print(f"--- Result {i} ---")
        print(chunk)
        print()