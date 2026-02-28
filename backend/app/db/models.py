from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String(100), unique=True, nullable=False)
    email           = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role            = Column(Enum("medecin", "admin", name="user_role"), default="medecin", nullable=False)
    created_at      = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    queries         = relationship("Query", back_populates="user", cascade="all, delete-orphan")


class Query(Base):

    __tablename__ = "query"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    query       = Column(Text, nullable=False)       
    reponse     = Column(Text, nullable=False)       
    sources     = Column(Text, default="")           
    chunks_used = Column(Integer, default=0)         
    created_at  = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="queries")