import re
import sys
import time
import threading
from typing import Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM

from app.core.config import settings
from app.rag.retriever import retrieve
from app.api.routes.metrics import record_request, record_deepeval_scores

MLFLOW_ENABLED = False
try:
    sys.path.insert(0, "/app")
    from rag_ops.rag_tracking import log_query, evaluate_with_deepeval
    MLFLOW_ENABLED = True
    print("[MLFlow] tracking activé ✓")
except Exception as e:
    print(f"[MLFlow] désactivé: {e}")

llm = OllamaLLM(
    model=settings.LLM_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    temperature=settings.LLM_TEMPERATURE,
    num_predict=settings.LLM_MAX_TOKENS,
    top_p=settings.LLM_TOP_P,
    top_k=settings.LLM_TOP_K,
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
Ton rôle : corriger ou valider la réponse ci-dessous.

RÈGLES ABSOLUES :
- Réponds UNIQUEMENT avec la réponse médicale finale, sans aucun commentaire.
- N'écris jamais de phrase comme "La réponse est correcte", "Voici la réponse", "Réécris", etc.
- N'inclus jamais d'analyse, de meta-commentaire, ni d'évaluation dans ta réponse.
- Si la réponse proposée est correcte et basée sur le contexte, reproduis-la telle quelle.
- Si une information est absente du contexte, remplace par : "Je ne trouve pas cette information dans les protocoles disponibles."

CONTEXTE :
{context}

QUESTION :
{question}

RÉPONSE PROPOSÉE :
{draft}

RÉPONSE FINALE (texte médical uniquement, sans commentaire) :
""")

generation_chain = GENERATION_PROMPT | llm | parser
self_rag_chain   = SELF_RAG_PROMPT   | llm | parser


def _clean_answer(text: str) -> str:
    patterns = [
        r"La réponse est.*?\n",
        r"Réécris la réponse.*?\n",
        r"Voici la réponse.*?\n",
        r"La réponse proposée.*?\n",
        r"Cette réponse.*?\n",
    ]
    for p in patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _build_context(docs) -> str:
    parts = []
    for i, doc in enumerate(docs, 1):
        protocol = doc.metadata.get("protocol", "Inconnu")
        section  = doc.metadata.get("section", "")
        parts.append(
            f"[Source {i} — Protocole : {protocol} | {section}]\n"
            f"{doc.page_content}"
        )
    return "\n\n---\n\n".join(parts)


def _background_eval(question, answer, context_list, run_id):
    try:
        scores = evaluate_with_deepeval(
            question     = question,
            answer       = answer,
            context_list = context_list,
            run_id       = run_id,
        )
        record_deepeval_scores(scores)  
    except Exception as e:
        print(f"[MLFlow] background eval error: {e}")


def run(question: str) -> Dict[str, Any]:
    start = time.time()

    docs = retrieve(question)
    if not docs:
        record_request(latency=0.0, status="error", chunks=0)
        return {
            "answer":      "Je ne trouve pas cette information dans les protocoles disponibles.",
            "sources":     [],
            "chunks_used": 0,
        }

    context = _build_context(docs)

    draft_answer = generation_chain.invoke({
        "context":  context,
        "question": question,
    })

    final_answer = self_rag_chain.invoke({
        "context":  context,
        "question": question,
        "draft":    draft_answer,
    })

    final_answer = _clean_answer(final_answer)
    latency      = round(time.time() - start, 3)  

    record_request(latency=latency, status="success", chunks=len(docs))

    sources = list({
        f"Protocole : {doc.metadata.get('protocol', 'Inconnu')} — "
        f"{doc.metadata.get('section', '')}"
        for doc in docs
    })

    if MLFLOW_ENABLED:
        try:
            run_id = log_query(
                question    = question,
                answer      = final_answer,
                sources     = sources,
                chunks_used = len(docs),
                latency_s   = latency,
                context     = context,
            )
            context_list = [doc.page_content for doc in docs]
            threading.Thread(
                target=_background_eval,
                kwargs={
                    "question":     question,
                    "answer":       final_answer,
                    "context_list": context_list,
                    "run_id":       run_id,
                },
                daemon=True
            ).start()
        except Exception as e:
            print(f"[MLFlow] tracking error (non-bloquant): {e}")

    return {
        "answer":      final_answer,
        "sources":     sources,
        "chunks_used": len(docs),
        "latency":     latency,
    }