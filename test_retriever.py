"""
test_retriever.py — Teste le retriever avec reranking.
Lance : docker exec -it protocare_backend python test_retriever.py
"""

import sys
sys.path.insert(0, "/app")

from app.rag.retriever import retrieve

question = "Quel est le traitement de la diarrhée chez l'enfant ?"

docs = retrieve(question, k=10, top_n=3)

print(f"\nQuestion : {question}")
print(f"Chunks après reranking : {len(docs)}")
print(f"{'='*50}")

for i, doc in enumerate(docs, 1):
    print(f"\n--- Chunk {i} ---")
    print(f"Protocole : {doc.metadata.get('protocol')}")
    print(f"Type      : {doc.metadata.get('type')}")
    print(f"Section   : {doc.metadata.get('section')}")
    print(f"Contenu   : {doc.page_content}")