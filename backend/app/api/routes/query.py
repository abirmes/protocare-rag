from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.rag.pipeline import run
from app.db.session import get_db
from app.db.models import Query
from app.api.deps import get_current_user
from app.db.models import User

router = APIRouter(prefix="/query", tags=["query"])


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer:      str
    sources:     List[str]
    chunks_used: int


@router.post("/ask", response_model=AnswerResponse)
def ask(
    payload: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question vide")

    result = run(payload.question)
 
    sources_str = "|".join(result.get("sources", []))

    entry = Query(
        user_id     = current_user.id,
        query       = payload.question,
        reponse     = result["answer"],
        sources     = sources_str,
        chunks_used = result.get("chunks_used", 0),
    )
    db.add(entry)
    db.commit()

    return AnswerResponse(
        answer      = result["answer"],
        sources     = result.get("sources", []),
        chunks_used = result.get("chunks_used", 0),
    )


@router.get("/health")
def health():
    return {"status": "ok"}