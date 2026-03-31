"""Database initialization and connection management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://nepse_user:nepse_password@localhost:5432/nepse_intelligence"
)

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Disable pooling for better Docker compatibility
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with schema."""
    Base.metadata.create_all(bind=engine)
