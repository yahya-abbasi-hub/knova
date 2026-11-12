from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.core.config import settings

# The "engine" manages the actual connection pool to PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# SessionLocal is a factory for creating new database sessions
# (a "session" is like a single conversation with the database —
# you open one, do some work, then close it)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is what all our future database models (tables) will inherit from
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes — gives each request its own database
    session, and guarantees it gets closed afterward even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()