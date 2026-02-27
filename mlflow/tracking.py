

import mlflow
from typing import List, Dict
from app.rag.pipeline import run
from app.rag.retriever import retrieve
from app.core.config import settings

# Exemple de dataset de test
TEST_QUERIES = [
    {"question": "Traitement de la diarrhée aiguë ?", "expected_chunks": ["diarrhée"]},
    {"question": "Que faire en cas d'hypertension sévère ?", "expected_chunks": ["hypertension"]},
]

def precision_at_k(retrieved: List[str], expected: List[str]) -> float:
    retrieved_set = set(retrieved)
    expected_set = set(expected)
    if not retrieved_set or not expected_set:
        return 0.0
    return len(retrieved_set & expected_set) / len(retrieved_set)

def recall_at_k(retrieved: List[str], expected: List[str]) -> float:
    retrieved_set = set(retrieved)
    expected_set = set(expected)
    if not expected_set:
        return 0.0
    return len(retrieved_set & expected_set) / len(expected_set)

def evaluate_pipeline():
    # Démarrage d'une run MLflow
    with mlflow.start_run(run_name="RAG_Evaluation"):

        # Log des hyperparamètres du pipeline
        mlflow.log_param("chunk_size", settings.CHUNK_SIZE)
        mlflow.log_param("chunk_overlap", settings.CHUNK_OVERLAP)
        mlflow.log_param("embedding_model", settings.EMBEDDING_MODEL)
        mlflow.log_param("retriever_k", settings.RETRIEVER_K)
        mlflow.log_param("reranker_model", "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")
        mlflow.log_param("llm_model", settings.LLM_MODEL)
        mlflow.log_param("llm_temperature", settings.LLM_TEMPERATURE)

        all_precisions = []
        all_recalls = []

        for q in TEST_QUERIES:
            # Exécution du pipeline RAG complet
            result = run(q["question"])

            # Log des réponses et contexte
            mlflow.log_text(q["question"], f"questions/{q['question'][:20]}.txt")
            mlflow.log_text(result["answer"], f"answers/{q['question'][:20]}.txt")
            mlflow.log_text("\n".join(result["sources"]), f"sources/{q['question'][:20]}.txt")
            mlflow.log_metric("chunks_used", result["chunks_used"])

            # Extraction des chunks récupérés pour métriques
            retrieved_chunks = [s.split(" — ")[0] for s in result["sources"]]

            p = precision_at_k(retrieved_chunks, q["expected_chunks"])
            r = recall_at_k(retrieved_chunks, q["expected_chunks"])
            f1 = (2 * p * r / (p + r)) if (p + r) > 0 else 0.0

            mlflow.log_metric("precision", p)
            mlflow.log_metric("recall", r)
            mlflow.log_metric("f1", f1)

            all_precisions.append(p)
            all_recalls.append(r)

        mlflow.log_metric("mean_precision", sum(all_precisions)/len(all_precisions))
        mlflow.log_metric("mean_recall", sum(all_recalls)/len(all_recalls))
        mean_f1 = (2 * sum(all_precisions)/len(all_precisions) * sum(all_recalls)/len(all_recalls)) / (
            sum(all_precisions)/len(all_precisions) + sum(all_recalls)/len(all_recalls)
        ) if (sum(all_precisions)/len(all_precisions) + sum(all_recalls)/len(all_recalls)) > 0 else 0.0
        mlflow.log_metric("mean_f1", mean_f1)

        print("✓ Evaluation MLflow terminée")
        print(f"Mean Precision: {sum(all_precisions)/len(all_precisions):.3f}")
        print(f"Mean Recall   : {sum(all_recalls)/len(all_recalls):.3f}")
        print(f"Mean F1       : {mean_f1:.3f}")

if __name__ == "__main__":
    evaluate_pipeline()