from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine
from app.db import models
from app.api.routes import auth
from app.exceptions import register_exception_handlers

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


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}