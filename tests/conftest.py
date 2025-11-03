"""
Pytest configuration and shared fixtures for all tests.
"""
import pytest
import sys
import os
from pathlib import Path
import pandas as pd
import tempfile
import shutil

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import SessionLocal, engine, Base
from src.db.models import CheckSession, Issue


@pytest.fixture(scope="module")
def db_session():
    """
    Returns a database session for testing, and closes it after tests are done.
    """
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def clean_db(db_session):
    """
    Clean database before each test.
    """
    # Delete all issues first (due to foreign key constraint)
    db_session.query(Issue).delete()
    db_session.query(CheckSession).delete()
    db_session.commit()
    yield
    # Cleanup after test
    db_session.query(Issue).delete()
    db_session.query(CheckSession).delete()
    db_session.commit()


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame with various data quality issues."""
    data = {
        "id": [1, 2, 3, 4, 5, 6, 7, 8],
        "name": ["Alice", "Bob", "Charlie", None, "Eve", "Alice", "Bob", None],
        "email": [
            "alice@example.com",
            "invalid-email",
            "charlie@example.com",
            "david@example.com",
            "eve@example.com",
            "alice@example.com",  # duplicate
            "bob@test.com",
            None
        ],
        "age": [30, 27, "not_a_number", 45, None, 30, 27, 35],
        "phone": ["1234567890", "invalid", "9876543210", None, "555-1234", "1234567890", "9999999999", ""],
        "salary": [50000, 60000, 70000, 80000, 90000, 50000, 150000, 55000],
        "date": ["2023-01-01", "2023-02-01", "invalid-date", "2023-04-01", None, "2023-01-01", "2023-06-01", "2023-07-01"]
    }
    return pd.DataFrame(data)


@pytest.fixture
def clean_dataframe():
    """Clean DataFrame without issues for comparison."""
    data = {
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "email": ["alice@example.com", "bob@example.com", "charlie@example.com", "david@example.com", "eve@example.com"],
        "age": [30, 27, 35, 45, 28],
        "salary": [50000, 60000, 70000, 80000, 55000]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_csv_file(tmp_path, sample_dataframe):
    """Create a temporary CSV file with sample data."""
    file_path = tmp_path / "test_data.csv"
    sample_dataframe.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def sample_json_file(tmp_path, sample_dataframe):
    """Create a temporary JSON file with sample data."""
    file_path = tmp_path / "test_data.json"
    sample_dataframe.to_json(file_path, orient='records', lines=False)
    return file_path


@pytest.fixture
def temp_reports_dir(tmp_path):
    """Create a temporary directory for reports."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(exist_ok=True)
    return reports_dir


@pytest.fixture
def temp_uploads_dir(tmp_path):
    """Create a temporary directory for uploads."""
    uploads_dir = tmp_path / "tmp_uploads"
    uploads_dir.mkdir(exist_ok=True)
    return uploads_dir


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch, tmp_path):
    """Setup test environment variables and paths."""
    # Override reports directory
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Set environment variables if needed
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
    
    # Cleanup after test
    yield
    # Additional cleanup if needed

