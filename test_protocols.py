import sys
sys.path.insert(0, "/app")

from app.rag.chunker import _split_into_protocols, _get_protocol_name

text = open("data/documents/guide_de_protocoles_markdown_clean.md").read()
protocols = _split_into_protocols(text)

print(f"Nombre de protocoles détectés : {len(protocols)}")
for i, p in enumerate(protocols):
    name = _get_protocol_name(p)
    print(f"  Protocole {i+1} : {name}")