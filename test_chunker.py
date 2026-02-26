
import sys
sys.path.insert(0, "/app")

from app.rag.chunker import chunk_markdown_file

MARKDOWN_FILE = "data/documents/guide_de_protocoles_markdown.md"

chunks = chunk_markdown_file(MARKDOWN_FILE)

print(f"\n{'='*50}")
print(f"Total chunks : {len(chunks)}")
print(f"{'='*50}")

for i, chunk in enumerate(chunks[:3]):
    print(f"\n--- Chunk {i+1} ---")
    print(f"Type    : {chunk.metadata['type']}")
    print(f"Section : {chunk.metadata['section']}")
    print(f"Taille  : {len(chunk.page_content)} caractères")
    print(f"Contenu :\n{chunk.page_content[:300]}")
    print()