from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.rag.pipeline import run

router = APIRouter(
    prefix="/query",
    tags=["query"]
)

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]
    chunks_used: int


@router.post("/ask", response_model=AnswerResponse)
def ask(payload: QuestionRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question vide")

    result = run(payload.question)
    return result


@router.get("/health")
def health():
    return {"status": "ok"}