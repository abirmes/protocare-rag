
import os
import mlflow
import mlflow.langchain
from datetime import datetime
from typing import Any, Dict, List, Optional

MLFLOW_TRACKING_URI  = os.getenv("MLFLOW_TRACKING_URI",  "http://mlflow:5000")
EXPERIMENT_NAME      = os.getenv("MLFLOW_EXPERIMENT_NAME", "protocare-rag")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)
mlflow.langchain.autolog()


RAG_CONFIG = {
    "chunk_size":        768,
    "chunk_overlap":     128,
    "chunk_strategy":    "hierarchical",
    "tokenizer":         "cl100k_base",
    "embedding_model":   "intfloat/multilingual-e5-base",
    "embedding_dim":     768,
    "normalization":     "L2",
    "similarity":        "cosine",
    "retriever_k":       10,
    "reranker_top_n":    3,
    "reranker_model":    "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
    "vector_store":      "ChromaDB",
}

LLM_CONFIG = {
    "model":          "mistral",
    "temperature":    0.0,
    "max_tokens":     2048,
    "top_p":          0.9,
    "top_k":          40,
    "quantization":   "Q4_K_M",
    "prompt":         "GENERATION_PROMPT + SELF_RAG_PROMPT",
}


def log_rag_config() -> None:
    with mlflow.start_run(run_name="rag-config"):
        mlflow.log_params({**RAG_CONFIG, **LLM_CONFIG})
        mlflow.set_tag("type",      "config")
        mlflow.set_tag("pipeline",  "Self-RAG")
        mlflow.set_tag("logged_at", datetime.utcnow().isoformat())


def log_query(
    question:    str,
    answer:      str,
    sources:     List[str],
    chunks_used: int,
    latency_s:   float,
    context:     Optional[str] = None,
) -> str:
    with mlflow.start_run(
        run_name=f"query-{datetime.utcnow().strftime('%H%M%S')}"
    ) as run:
        # Params LLM
        mlflow.log_params(LLM_CONFIG)

        # Métriques opérationnelles
        mlflow.log_metrics({
            "latency_seconds": round(latency_s, 3),
            "chunks_used":     float(chunks_used),
            "sources_count":   float(len(sources)),
            "answer_length":   float(len(answer)),
            "question_length": float(len(question)),
        })

        mlflow.log_text(question, "question.txt")
        mlflow.log_text(answer,   "answer.txt")
        if context:
            mlflow.log_text(context, "context.txt")
        if sources:
            mlflow.log_text("\n".join(sources), "sources.txt")

        mlflow.set_tag("type",      "query")
        mlflow.set_tag("model",     LLM_CONFIG["model"])
        mlflow.set_tag("timestamp", datetime.utcnow().isoformat())

        return run.info.run_id


def log_rag_metrics(
    run_id:           str,
    answer_relevance: float,
    faithfulness:     float,
    precision_at_k:   float,
    recall_at_k:      float,
) -> None:
    with mlflow.start_run(run_id=run_id):
        mlflow.log_metrics({
            "answer_relevance": round(answer_relevance, 4),
            "faithfulness":     round(faithfulness, 4),
            "precision_at_k":   round(precision_at_k, 4),
            "recall_at_k":      round(recall_at_k, 4),
        })
        mlflow.set_tag("deepeval", "true")


def evaluate_with_deepeval(
    question:     str,
    answer:       str,
    context_list: List[str],
    run_id:       Optional[str] = None,
) -> Dict[str, float]:
    try:
        from deepeval.metrics import (
            AnswerRelevancyMetric,
            FaithfulnessMetric,
            ContextualPrecisionMetric,
            ContextualRecallMetric,
        )
        from deepeval.test_case import LLMTestCase
        from deepeval.models import DeepEvalBaseLLM
        from langchain_ollama import OllamaLLM

        class OllamaDeepEval(DeepEvalBaseLLM):
            def __init__(self):
                self.model = OllamaLLM(
                    model="mistral",
                    base_url="http://ollama:11434",
                    temperature=0.0,
                )
            def load_model(self):
                return self.model
            def generate(self, prompt: str) -> str:
                return self.model.invoke(prompt)
            async def a_generate(self, prompt: str) -> str:
                return self.generate(prompt)
            def get_model_name(self) -> str:
                return "mistral"

        ollama_llm = OllamaDeepEval()

        test_case = LLMTestCase(
            input=question,
            actual_output=answer,
            retrieval_context=context_list,
            expected_output=answer,
        )

        metrics = [
            AnswerRelevancyMetric(threshold=0.5,    model=ollama_llm),
            FaithfulnessMetric(threshold=0.5,       model=ollama_llm),
            ContextualPrecisionMetric(threshold=0.5, model=ollama_llm),
            ContextualRecallMetric(threshold=0.5,   model=ollama_llm),
        ]

        for metric in metrics:
            metric.measure(test_case)

        mapped = {
            "answer_relevance": metrics[0].score or 0.0,
            "faithfulness":     metrics[1].score or 0.0,
            "precision_at_k":   metrics[2].score or 0.0,
            "recall_at_k":      metrics[3].score or 0.0,
        }

        if run_id:
            log_rag_metrics(run_id=run_id, **mapped)

        return mapped

    except Exception as e:
        print(f"[MLFlow] DeepEval error: {e}")
        return {"answer_relevance": 0.0, "faithfulness": 0.0,
                "precision_at_k": 0.0, "recall_at_k": 0.0}

    
    