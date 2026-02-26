

from typing import List
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.core.config import settings
from app.rag.chunker import chunk_markdown_file


embeddings = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)


def get_vector_store() -> Chroma:
    return Chroma(
        collection_name="protocare_medical",
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR,
    )


def _apply_passage_prefix(chunks: List[Document]) -> List[Document]:
    
    for chunk in chunks:
        if not chunk.page_content.startswith("passage: "):
            chunk.page_content = "passage: " + chunk.page_content
    return chunks


def index_chunks(chunks: List[Document]) -> int:
    if not chunks:
        print("No chunks to index.")
        return 0

    chunks = _apply_passage_prefix(chunks)

    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    print(f"{len(chunks)} chunks successfully indexed in ChromaDB.")
    return len(chunks)


def index_markdown_file(file_path: str) -> int:
  
    print(f"Chunking file: {file_path}")
    chunks = chunk_markdown_file(file_path)

    print(f"Indexing {len(chunks)} chunks...")
    return index_chunks(chunks)


def search(query: str, k: int = None) -> List[Document]:
    
    k = k or settings.RETRIEVER_K
    query_with_prefix = "query: " + query

    vector_store = get_vector_store()
    return vector_store.similarity_search(query_with_prefix, k=k)