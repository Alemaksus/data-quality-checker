import pytest
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.db.database import SessionLocal

@pytest.fixture(scope="module")
def db():
    """
    Returns a database session for testing, and closes it after tests are done.
    """
    session = SessionLocal()
    yield session
    session.close()
