"""
test_rag.py — Tests unitaires du pipeline RAG
"""

import pytest
from unittest.mock import patch
from langchain.schema import Document


def test_chunk_markdown_returns_documents():
    """Vérifie que le chunker retourne bien une liste de Documents."""
    from app.rag.chunker import chunk_markdown

    text = """XXXXX Diarrhée
Validation : COTEPRO

# CE QU'IL FAUT SAVOIR

La diarrhée est une infection virale du tube digestif.
Elle se transmet par voie oro-fécale.
"""

    chunks = chunk_markdown(text, source="test.md")

    assert len(chunks) > 0
    assert all(hasattr(chunk, "page_content") for chunk in chunks)


def test_chunk_metadata_has_required_fields():
    from app.rag.chunker import chunk_markdown

    text = """XXXXX Diarrhée
# CE QU'IL FAUT FAIRE

Evaluer la déshydratation.
"""

    chunks = chunk_markdown(text, source="test.md")

    for chunk in chunks:
        assert "source" in chunk.metadata
        assert "type" in chunk.metadata
        assert "section" in chunk.metadata
        assert "protocol" in chunk.metadata


def test_table_kept_as_single_chunk():
    from app.rag.chunker import chunk_markdown

    text = """XXXXX Test
# Section

| Col1 | Col2 |
| --- | --- |
| Val1 | Val2 |
| Val3 | Val4 |
"""

    chunks = chunk_markdown(text, source="test.md")
    table_chunks = [c for c in chunks if c.metadata["type"] == "table"]

    assert len(table_chunks) == 1
    assert "| Col1 | Col2 |" in table_chunks[0].page_content


def test_protocol_separation():
    """Deux protocoles distincts doivent produire des chunks séparés."""
    from app.rag.chunker import chunk_markdown

    text = """XXXXX Diarrhée
# CE QU'IL FAUT SAVOIR
La diarrhée est virale.

XXXXX Toux
# CE QU'IL FAUT SAVOIR
La toux peut être grave.
"""

    chunks = chunk_markdown(text, source="test.md")
    protocols = {c.metadata["protocol"] for c in chunks}

    assert "Diarrhée" in protocols
    assert "Toux" in protocols


def test_no_mixed_protocols_in_chunk():
    from app.rag.chunker import chunk_markdown

    text = """XXXXX Diarrhée
# CE QU'IL FAUT SAVOIR
La diarrhée est virale.

XXXXX Toux
# CE QU'IL FAUT SAVOIR
La toux peut être grave.
"""

    chunks = chunk_markdown(text, source="test.md")

    for chunk in chunks:
        assert chunk.metadata["protocol"] in ["Diarrhée", "Toux", "Inconnu"]


def test_removes_page_numbers():
    """Les numéros de page doivent être supprimés."""
    from app.rag.cleaner import clean_markdown

    text = "Guide des Protocoles - 2025   42\n\nContenu médical."
    result = clean_markdown(text)

    assert "Contenu médical" in result


def test_normalizes_table_multiline():
    """Un tableau multi-lignes doit être normalisé sur une seule ligne."""
    from app.rag.cleaner import clean_markdown

    text = "| Cellule1\ncontinuation | Cellule2 |"
    result = clean_markdown(text)

    lines = [line for line in result.split("\n") if "|" in line]
    assert len(lines) == 1


def test_clean_markdown_file(tmp_path):
    """Vérifie que la fonction lit et réécrit correctement un fichier."""
    from app.rag.cleaner import clean_markdown_file

    input_file = tmp_path / "test.md"
    output_file = tmp_path / "test_clean.md"

    input_file.write_text(
        "Guide des Protocoles - 2025   5\n\nContenu.",
        encoding="utf-8"
    )

    clean_markdown_file(str(input_file), str(output_file))

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "Contenu." in content


@patch("app.rag.pipeline.retrieve")
@patch("app.rag.pipeline.chain")
def test_pipeline_returns_answer(mock_chain, mock_retrieve):
    """Le pipeline doit retourner une réponse structurée."""
    from app.rag.pipeline import run

    mock_retrieve.return_value = [
        Document(
            page_content="Les SRO sont le traitement de la diarrhée.",
            metadata={
                "protocol": "Diarrhée",
                "section": "# Traitement",
                "type": "text"
            }
        )
    ]

    mock_chain.invoke.return_value = "Administrer des SRO au patient."

    result = run("Quel est le traitement de la diarrhée ?")

    assert "answer" in result
    assert "sources" in result
    assert "chunks_used" in result
    assert result["chunks_used"] == 1


@patch("app.rag.pipeline.retrieve")
def test_pipeline_no_docs_returns_default_message(mock_retrieve):
    """Sans documents pertinents, un message par défaut doit être retourné."""
    from app.rag.pipeline import run

    mock_retrieve.return_value = []
    result = run("Question sans réponse")

    assert result["chunks_used"] == 0
    assert "Je ne trouve pas" in result["answer"]
    assert result["sources"] == []


@patch("app.rag.pipeline.retrieve")
@patch("app.rag.pipeline.chain")
def test_pipeline_sources_extracted_correctly(mock_chain, mock_retrieve):
    """Les sources doivent être correctement extraites des métadonnées."""
    from app.rag.pipeline import run

    mock_retrieve.return_value = [
        Document(
            page_content="Contenu 1",
            metadata={
                "protocol": "Diarrhée",
                "section": "# Traitement",
                "type": "text"
            }
        ),
        Document(
            page_content="Contenu 2",
            metadata={
                "protocol": "Diarrhée",
                "section": "# Symptômes",
                "type": "text"
            }
        ),
    ]

    mock_chain.invoke.return_value = "Réponse test."

    result = run("Question ?")

    assert len(result["sources"]) > 0
    assert any("Diarrhée" in source for source in result["sources"])