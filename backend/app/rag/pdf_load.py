"""
pdf_load.py — Charge un PDF avec LlamaParse et sauvegarde en Markdown.
"""

from pathlib import Path
from llama_parse import LlamaParse
from app.core.config import settings
from app.rag.cleaner import clean_markdown

OUTPUT_PATH = "data/documents/guide_de_protocoles_markdown.md"


def load_pdf_to_markdown(pdf_path: str) -> str:
    """Charge un PDF avec LlamaParse et retourne le contenu en Markdown."""
    parser = LlamaParse(
        api_key=settings.LLAMA_CLOUD_API_KEY,
        result_type="markdown",
        verbose=True,
    )
    documents = parser.load_data(pdf_path)
    full_text = "\n\n".join([doc.text for doc in documents])
    return full_text


def save_pdf_as_markdown(pdf_path: str) -> str:
    """
    Charge un PDF, nettoie le markdown et sauvegarde dans :
    data/documents/guide_de_protocoles_markdown.md
    """
    print(f"Chargement du PDF : {pdf_path}")
    content = load_pdf_to_markdown(pdf_path)

    # Nettoyage du markdown
    print("Nettoyage du markdown...")
    content = clean_markdown(content)

    output = Path(OUTPUT_PATH)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")

    print(f"✓ Markdown sauvegardé : {OUTPUT_PATH}")
    print(f"✓ Taille : {len(content)} caractères")
    return content