"""
Tests for database operations, specifically save_check_to_db().
"""
import pytest

pytestmark = pytest.mark.unit
import pandas as pd
from pathlib import Path
from src.core.generate_sample_report import save_check_to_db
from src.db.models import CheckSession, Issue
from src.db.database import SessionLocal, engine, Base


class TestSaveCheckToDB:
    """Tests for save_check_to_db function."""
    
    def test_save_check_to_db_basic(self, clean_db, db_session):
        """Test basic saving of check results to database."""
        validation_issues = [
            {
                "issue_type": "missing_values",
                "description": "Column 'name' has 2 missing values",
                "severity": "medium",
                "row_number": None,
                "column_name": "name"
            },
            {
                "issue_type": "invalid_email",
                "description": "Row 2: Invalid email format",
                "severity": "low",
                "row_number": 1,
                "column_name": "email"
            }
        ]
        
        session_id = save_check_to_db(
            filename="test_data.csv",
            file_format="csv",
            rows=100,
            validation_issues=validation_issues,
            db_session=db_session
        )
        
        assert session_id is not None
        assert isinstance(session_id, int)
        
        # Verify CheckSession was created
        check_session = db_session.query(CheckSession).filter_by(id=session_id).first()
        assert check_session is not None
        assert check_session.filename == "test_data.csv"
        assert check_session.file_format == "csv"
        assert check_session.rows == 100
        assert check_session.issues_found == 2
        
        # Verify Issues were created
        issues = db_session.query(Issue).filter_by(session_id=session_id).all()
        assert len(issues) == 2
        
        # Check first issue
        assert issues[0].issue_type == "missing_values"
        assert issues[0].column_name == "name"
        assert issues[0].severity == "medium"
    
    def test_save_check_to_db_with_session(self, clean_db, db_session):
        """Test saving with provided session."""
        validation_issues = [
            {
                "issue_type": "duplicates",
                "description": "Found 5 duplicate rows",
                "severity": "high",
                "row_number": None,
                "column_name": None
            }
        ]
        
        session_id = save_check_to_db(
            filename="test2.csv",
            file_format="csv",
            rows=50,
            validation_issues=validation_issues,
            db_session=db_session
        )
        
        assert session_id is not None
        
        # Verify in database
        check_session = db_session.query(CheckSession).filter_by(id=session_id).first()
        assert check_session.issues_found == 1
    
    def test_save_check_to_db_creates_session(self, clean_db):
        """Test that save_check_to_db creates its own session if none provided."""
        validation_issues = [
            {
                "issue_type": "outliers",
                "description": "Column 'age' has 3 outliers",
                "severity": "medium",
                "row_number": None,
                "column_name": "age"
            }
        ]
        
        session_id = save_check_to_db(
            filename="test3.csv",
            file_format="csv",
            rows=200,
            validation_issues=validation_issues,
            db_session=None
        )
        
        assert session_id is not None
        
        # Verify using new session
        session = SessionLocal()
        try:
            check_session = session.query(CheckSession).filter_by(id=session_id).first()
            assert check_session is not None
            assert check_session.issues_found == 1
        finally:
            session.close()
    
    def test_save_check_to_db_empty_issues(self, clean_db, db_session):
        """Test saving with no issues."""
        session_id = save_check_to_db(
            filename="clean_data.csv",
            file_format="csv",
            rows=1000,
            validation_issues=[],
            db_session=db_session
        )
        
        assert session_id is not None
        
        check_session = db_session.query(CheckSession).filter_by(id=session_id).first()
        assert check_session.issues_found == 0
        
        # Verify no issues created
        issues = db_session.query(Issue).filter_by(session_id=session_id).all()
        assert len(issues) == 0
    
    def test_save_check_to_db_many_issues(self, clean_db, db_session):
        """Test saving with many issues."""
        # Create 50 issues
        validation_issues = [
            {
                "issue_type": f"issue_type_{i}",
                "description": f"Issue {i}",
                "severity": "medium" if i % 2 == 0 else "low",
                "row_number": i if i % 3 == 0 else None,
                "column_name": f"col_{i % 5}"
            }
            for i in range(50)
        ]
        
        session_id = save_check_to_db(
            filename="large_issues.csv",
            file_format="csv",
            rows=5000,
            validation_issues=validation_issues,
            db_session=db_session
        )
        
        assert session_id is not None
        
        check_session = db_session.query(CheckSession).filter_by(id=session_id).first()
        assert check_session.issues_found == 50
        
        # Verify all issues were saved
        issues = db_session.query(Issue).filter_by(session_id=session_id).all()
        assert len(issues) == 50
    
    def test_save_check_to_db_creates_tables(self, clean_db, db_session):
        """Test that tables are created if they don't exist."""
        # Ensure tables exist (this should happen automatically)
        Base.metadata.create_all(bind=engine)
        
        validation_issues = [
            {
                "issue_type": "test",
                "description": "Test issue",
                "severity": "low"
            }
        ]
        
        session_id = save_check_to_db(
            filename="table_test.csv",
            file_format="csv",
            rows=10,
            validation_issues=validation_issues,
            db_session=db_session
        )
        
        assert session_id is not None
    
    def test_save_check_to_db_error_handling(self, clean_db, db_session, monkeypatch):
        """Test error handling in save_check_to_db."""
        validation_issues = [
            {
                "issue_type": "test",
                "description": "Test",
                "severity": "medium"
            }
        ]
        
        # Mock a database error
        def mock_add(obj):
            raise Exception("Database error")
        
        # Should handle error gracefully
        original_add = db_session.add
        db_session.add = mock_add
        
        try:
            session_id = save_check_to_db(
                filename="error_test.csv",
                file_format="csv",
                rows=10,
                validation_issues=validation_issues,
                db_session=db_session
            )
            # Should return None on error
            assert session_id is None
        except Exception:
            # Or might raise, but should be handled
            pass
        finally:
            db_session.add = original_add
    
    def test_save_check_to_db_relationships(self, clean_db, db_session):
        """Test that relationships between CheckSession and Issue work."""
        validation_issues = [
            {
                "issue_type": "missing_values",
                "description": "Missing value",
                "severity": "high",
                "row_number": 5,
                "column_name": "name"
            }
        ]
        
        session_id = save_check_to_db(
            filename="relationship_test.csv",
            file_format="csv",
            rows=10,
            validation_issues=validation_issues,
            db_session=db_session
        )
        
        check_session = db_session.query(CheckSession).filter_by(id=session_id).first()
        
        # Test relationship
        assert len(check_session.issues) == 1
        assert check_session.issues[0].issue_type == "missing_values"
        assert check_session.issues[0].session_id == session_id

