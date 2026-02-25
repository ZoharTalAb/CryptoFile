import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

DATABASE_URL = os.getenv("DATABASE_URL")

# Allow SQLite fallback ONLY for tests
if not DATABASE_URL:
    if ENVIRONMENT == "test":
        DATABASE_URL = "sqlite:///./test.db"
    else:
        raise RuntimeError("DATABASE_URL must be set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass
