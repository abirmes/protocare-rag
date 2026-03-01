from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db import models
from app.api.routes import auth, query, history
from app.exceptions import register_exception_handlers
from app.api.routes import auth, query, history, metrics

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ProtoCare RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(query.router)
app.include_router(history.router)
app.include_router(metrics.router)



@app.on_event("startup")
async def startup_event():
    try:
        import sys
        sys.path.insert(0, "/app")
        from rag_ops.rag_tracking import log_rag_config
        log_rag_config()
        print("[MLFlow] Config RAG loggée ")
    except Exception as e:
        print(f"[MLFlow] startup log ignoré: {e}")


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}