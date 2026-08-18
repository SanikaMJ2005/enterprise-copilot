import os
import chromadb
from chromadb.utils import embedding_functions


def ingest_documents():
    data_dir = "data"
    policy_file = os.path.join(data_dir, "company_policy.md")
    db_path = os.path.join(data_dir, "chroma_db")

    if not os.path.exists(policy_file):
        print(f"❌ Error: File '{policy_file}' not found!")
        return

    print("📖 Reading company policy document...")
    with open(policy_file, "r", encoding="utf-8") as f:
        text_content = f.read()

    # Simple chunking by paragraph/sections
    chunks = [chunk.strip() for chunk in text_content.split("\n\n") if chunk.strip()]
    print(f"🧩 Split document into {len(chunks)} chunks.")

    # Initialize persistent ChromaDB client
    chroma_client = chromadb.PersistentClient(path=db_path)

    # Use default sentence transformer model for local embeddings
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    # Get or create collection
    collection = chroma_client.get_or_create_collection(
        name="company_policies", embedding_function=embedding_fn
    )

    # Generate IDs and metadata for each chunk
    ids = [f"doc_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": "company_policy.md", "chunk_index": i} for i in range(len(chunks))]

    print("⚡ Generating embeddings and storing in ChromaDB...")
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids,
    )

    print(f"✅ Successfully ingested {len(chunks)} chunks into ChromaDB at '{db_path}'!")


if __name__ == "__main__":
    ingest_documents()