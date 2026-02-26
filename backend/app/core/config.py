from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    LLAMA_PARSE_API_KEY: str = ""
    CHUNK_SIZE: int = 768       
    CHUNK_OVERLAP: int = 128 
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-base"    
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    RETRIEVER_K: int = 5
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()