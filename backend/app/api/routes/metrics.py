from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter()

rag_requests_total = Counter(
    "rag_requests_total",
    "Nombre total de requêtes RAG",
    ["status"],
)

rag_request_duration = Histogram(
    "rag_request_duration_seconds",
    "Latence des requêtes RAG en secondes",
    buckets=[5, 10, 20, 30, 45, 60, 90, 120, 180],
)

rag_chunks_used = Gauge(
    "rag_chunks_used",
    "Nombre de chunks utilisés pour la dernière réponse",
)

rag_answer_relevance = Gauge(
    "rag_answer_relevance_avg",
    "Score moyen Answer Relevance",
)
rag_faithfulness = Gauge(
    "rag_faithfulness_avg",
    "Score moyen Faithfulness",
)
rag_precision_at_k = Gauge(
    "rag_precision_at_k_avg",
    "Score moyen Precision@k",
)
rag_recall_at_k = Gauge(
    "rag_recall_at_k_avg",
    "Score moyen Recall@k",
)

_scores = {
    "answer_relevance": [],
    "faithfulness": [],
    "precision_at_k": [],
    "recall_at_k": [],
}

MAX_SCORES = 100


def record_request(latency: float, status: str, chunks: int):
    rag_requests_total.labels(status=status).inc()
    rag_request_duration.observe(latency)
    rag_chunks_used.set(chunks)


def record_deepeval_scores(scores: dict):
    for key, gauge in [
        ("answer_relevance", rag_answer_relevance),
        ("faithfulness", rag_faithfulness),
        ("precision_at_k", rag_precision_at_k),
        ("recall_at_k", rag_recall_at_k),
    ]:
        if key in scores and scores[key] > 0:
            _scores[key].append(scores[key])
            if len(_scores[key]) > MAX_SCORES:
                _scores[key].pop(0)
            avg = sum(_scores[key]) / len(_scores[key])
            gauge.set(round(avg, 4))


@router.get("/metrics", include_in_schema=False)
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )