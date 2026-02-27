"""
pipeline.py — Pipeline RAG avec couche Self-Verification (Self-RAG léger).

Flux :
1. Retrieval + Reranking
2. Construction du contexte
3. Génération initiale (draft)
4. Auto-évaluation et correction
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
from app.core.config import settings
from app.rag.retriever import retrieve


llm = OllamaLLM(
    model=settings.LLM_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    temperature=settings.LLM_TEMPERATURE,
)

parser = StrOutputParser()


GENERATION_PROMPT = ChatPromptTemplate.from_template("""
Tu es ProtoCare, assistant médical pour professionnels de santé.

RÈGLES STRICTES :
- Réponds uniquement à partir des protocoles fournis.
- Si l'information n'est pas présente, répond :
  "Je ne trouve pas cette information dans les protocoles disponibles."
- N'invente aucune information médicale.
- Cite toujours le protocole utilisé.
- En cas d'urgence vitale, rappelle d'appeler le SAMU.

PROTOCOLES :
{context}

QUESTION :
{question}

RÉPONSE :
""")


SELF_RAG_PROMPT = ChatPromptTemplate.from_template("""
Tu es un vérificateur médical strict.

CONTEXTE :
{context}

QUESTION :
{question}

RÉPONSE PROPOSÉE :
{draft}

Analyse :

1. La réponse est-elle totalement basée sur le contexte ?
2. Contient-elle une information absente des protocoles ?
3. Les sources sont-elles cohérentes ?

Si tout est correct :
→ Réécris la réponse proprement.

Si une information n'est PAS présente dans le contexte :
→ Répond uniquement :
"Je ne trouve pas cette information dans les protocoles disponibles."
""")


generation_chain = GENERATION_PROMPT | llm | parser
self_rag_chain = SELF_RAG_PROMPT | llm | parser


def _build_context(docs) -> str:
    parts = []

    for i, doc in enumerate(docs, 1):
        protocol = doc.metadata.get("protocol", "Inconnu")
        section = doc.metadata.get("section", "")

        parts.append(
            f"[Source {i} — Protocole : {protocol} | {section}]\n"
            f"{doc.page_content}"
        )

    return "\n\n---\n\n".join(parts)


def run(question: str) -> Dict[str, Any]:
 

    docs = retrieve(question)

    if not docs:
        return {
            "answer": "Je ne trouve pas cette information dans les protocoles disponibles.",
            "sources": [],
            "chunks_used": 0,
        }

    context = _build_context(docs)

    draft_answer = generation_chain.invoke({
        "context": context,
        "question": question,
    })

    final_answer = self_rag_chain.invoke({
        "context": context,
        "question": question,
        "draft": draft_answer,
    })

    sources = list({
        f"Protocole : {doc.metadata.get('protocol', 'Inconnu')} — "
        f"{doc.metadata.get('section', '')}"
        for doc in docs
    })

    return {
        "answer": final_answer,
        "sources": sources,
        "chunks_used": len(docs),
    }