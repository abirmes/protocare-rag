# CliniQ – Assistant Décisionnel Clinique

**CliniQ** est un assistant intelligent basé sur une architecture **RAG (Retrieval-Augmented Generation)** optimisée[cite: 2]. Il fournit aux professionnels de santé un accès instantané et contextualisé aux protocoles médicaux et à la documentation clinique[cite: 2].

---

## 📋 Présentation du Projet
Développé par **ProtoCare**, CliniQ vise à standardiser la prise en charge des patients et à assister les médecins dans leurs décisions cliniques, particulièrement en situation d'urgence[cite: 4, 5]. La solution automatise l'accès aux protocoles pour garantir des diagnostics rapides et éclairés[cite: 5].



## 🛠️ Architecture du Système RAG

### 1. Prétraitement et Chunking [cite: 9]
* **Importation** : Support des manuels techniques et documents PDF de référence[cite: 11].
* **Segmentation** : Utilisation d'une méthode de chunking préservant le maximum de contexte[cite: 12].
* **Métadonnées** : Chaque chunk est enrichi de métadonnées utiles pour la récupération[cite: 13].

### 2. Indexation et Persistance [cite: 14]
* **Embeddings** : Utilisation de modèles Hugging Face ou Ollama[cite: 17].
* **Vector Store** : Stockage et persistance dans des bases adaptées comme ChromaDB, FAISS ou Qdrant[cite: 15, 18].

### 3. Retrieval (Récupération) [cite: 19]
* **Retriever** : Configuration pour extraire les chunks pertinents selon la requête[cite: 20].
* **Optimisation** : Intégration de techniques de *Query expansion* et de *Reranking*[cite: 21].

### 4. Génération [cite: 22]
* **Modèle LLM** : Utilisation de **Mistral** pour la génération de réponses.
* **Prompt Engineering** : Utilisation d'un prompt centralisé et précis pour garantir la fiabilité médicale[cite: 23, 25].

---

## 💻 Stack Technique

### Back-end [cite: 29]
* **Framework** : FastAPI (Asynchrone)[cite: 30].
* **Validation** : Pydantic[cite: 32].
* **ORM & DB** : SQLAlchemy avec PostgreSQL[cite: 33, 38].
* **Pipeline AI** : LangChain[cite: 35].
* **Sécurité** : Authentification via JWT[cite: 36].

### Front-end [cite: 45]
* **Interface** : Interface intuitive développée avec Streamlit ou React pour une interaction rapide[cite: 46].

### DevOps & Conteneurisation [cite: 41, 59]
* **Docker** : Utilisation de Docker et Docker Compose[cite: 41].
* **CI/CD** : Pipeline automatisé pour l'exécution des tests (code + RAG) et la publication sur Docker Hub[cite: 61, 62, 63].

---

## 📈 LLMOps & Monitoring

### Suivi avec MLflow [cite: 48]
Nous logguons l'ensemble des paramètres pour assurer la traçabilité :
* **Configuration RAG** : Taille des chunks, overlap, modèle d'embedding, algorithme de similarité (cosine, L2)[cite: 51, 52, 53].
* **Hyperparamètres LLM** : Template de prompt, température, max tokens[cite: 55].
* **Métriques Qualité** : Évaluation via **DeepEval** (Answer relevance, Faithfulness, Precision@k, Recall@k)[cite: 57].

### Surveillance (Prometheus & Grafana) 
* **Métriques Infrastructure** : Consommation CPU et RAM[cite: 66].
* **Métriques Métier** : Latence du RAG, qualité des réponses, taux d'erreurs et volume de requêtes[cite: 67].
* **Alerting** : Seuils configurés pour prévenir toute dégradation de la qualité clinique[cite: 68].

---

## 🗄️ Modèle de Données
Le système s'appuie sur deux tables principales[cite: 26]:
* **`users`** : id, username, email, hashed_password, role[cite: 27].
* **`Query`** : id, query, reponse, created_at[cite: 28].