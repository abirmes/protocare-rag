

from typing import List
from langchain.schema import Document
from sentence_transformers import CrossEncoder
from app.rag.embedder import search
from app.core.config import settings


# Chargement du reranker multilingue
reranker = CrossEncoder(
    "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
    max_length=512,
)


def retrieve(query: str, k: int = 10, top_n: int = 3) -> List[Document]:
   

    docs = search(query, k=k)

    if not docs:
        return []

    for doc in docs:
        if doc.page_content.startswith("passage: "):
            doc.page_content = doc.page_content.replace("passage: ", "", 1)

    pairs = [[query, doc.page_content] for doc in docs]

    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(scores, docs),
        key=lambda x: x[0],
        reverse=True
    )

    top_docs = [doc for score, doc in ranked[:top_n]]

    return top_docs