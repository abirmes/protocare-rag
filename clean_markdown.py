"""
clean_markdown.py — Nettoie le markdown existant sans re-parser le PDF.
Lance : docker exec -it protocare_backend python clean_markdown.py
"""

import sys
sys.path.insert(0, "/app")

from app.rag.cleaner import clean_markdown_file

clean_markdown_file(
    input_path="data/documents/guide_de_protocoles_markdown.md",
    output_path="data/documents/guide_de_protocoles_markdown_clean.md"
)