from fastapi import APIRouter, Depends, Query as QueryParam
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import List

from app.db.session import get_db
from app.db.models import Query
from app.api.deps import get_current_user
from app.db.models import User

router = APIRouter(prefix="/history", tags=["history"])



@router.get("/")
def get_history(
    skip: int = QueryParam(0, ge=0),
    limit: int = QueryParam(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Query)
        .filter(Query.user_id == current_user.id)
        .order_by(desc(Query.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for row in rows:
        result.append({
            "id": row.id,
            "query": row.query,
            "reponse": row.reponse,
            "sources": [s for s in (row.sources or "").split("|") if s.strip()],
            "chunks_used": row.chunks_used,
            "created_at": row.created_at,
        })

    return result



@router.delete("/{query_id}", status_code=204)
def delete_entry(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = (
        db.query(Query)
        .filter(Query.id == query_id, Query.user_id == current_user.id)
        .first()
    )

    if entry:
        db.delete(entry)
        db.commit()