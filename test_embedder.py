

import sys

# Ensure the app directory is available inside the container
sys.path.insert(0, "/app")

from app.rag.embedder import index_markdown_file, get_vector_store


MARKDOWN_FILE = "data/documents/guide_de_protocoles_markdown_clean.md"


print("Starting indexing process...")
indexed_total = index_markdown_file(MARKDOWN_FILE)


# Step 2 — Verify stored documents
vector_store = get_vector_store()
stored_total = vector_store._collection.count()

print(f"Chunks indexed in this run : {indexed_total}")
print(f"Total chunks currently in ChromaDB : {stored_total}")


print("\nRunning similarity search test...")
results = vector_store.similarity_search("diarrhée traitement", k=2)

for idx, document in enumerate(results, start=1):
    print(f"\n--- Result {idx} ---")
    print(f"Type    : {document.metadata.get('type')}")
    print(f"Section : {document.metadata.get('section')}")
    print(f"Preview : {document.page_content[:200]}")