import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load test environment BEFORE importing anything from backend,
# so backend.core.config picks up .env.test values instead of .env
from dotenv import load_dotenv
load_dotenv(".env.test", override=True)

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database.session import Base, engine, SessionLocal


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Creates all tables fresh at the start of the test session, and drops
    them at the end. autouse=True means this runs automatically for every
    test session, without needing to be explicitly requested.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Gives each test its own database session, rolled back after the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client():
    """A test client that can make requests to our FastAPI app without
    actually running a live uvicorn server."""
    return TestClient(app)