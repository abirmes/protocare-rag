

import sys
from app.rag.pdf_load import save_pdf_as_markdown

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python ingest.py <chemin_du_pdf>")
        print("Exemple : python ingest.py data/documents/protocole.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    save_pdf_as_markdown(pdf_path)