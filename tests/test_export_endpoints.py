"""
Integration tests for export endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import pandas as pd
import tempfile
from src.api.main import app
from src.core.generate_sample_report import generate_data_quality_report


pytestmark = pytest.mark.integration


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_data_file(tmp_path):
    """Create sample data file."""
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "email": ["alice@test.com", "bob@test.com", "charlie@test.com"]
    })
    file_path = tmp_path / "test_data.csv"
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def create_check_session(sample_data_file):
    """Create a check session and return session_id."""
    result = generate_data_quality_report(sample_data_file, report_format="json")
    return result.get("session_id")


class TestExportEndpoints:
    """Tests for export endpoints."""
    
    def test_export_session_json(self, client, create_check_session):
        """Test exporting session data as JSON."""
        session_id = create_check_session
        if not session_id:
            pytest.skip("No session created")
        
        response = client.get(f"/export/session/{session_id}?format=json")
        
        assert response.status_code == 200
        assert "application/octet-stream" in response.headers.get("content-type", "")
        assert f"session_{session_id}_issues.json" in response.headers.get("content-disposition", "")
    
    def test_export_session_csv(self, client, create_check_session):
        """Test exporting session data as CSV."""
        session_id = create_check_session
        if not session_id:
            pytest.skip("No session created")
        
        response = client.get(f"/export/session/{session_id}?format=csv")
        
        assert response.status_code == 200
        assert f"session_{session_id}_issues.csv" in response.headers.get("content-disposition", "").lower()
    
    def test_export_session_xml(self, client, create_check_session):
        """Test exporting session data as XML."""
        session_id = create_check_session
        if not session_id:
            pytest.skip("No session created")
        
        response = client.get(f"/export/session/{session_id}?format=xml")
        
        assert response.status_code == 200
        assert f"session_{session_id}_issues.xml" in response.headers.get("content-disposition", "").lower()
    
    def test_export_session_nonexistent(self, client):
        """Test exporting nonexistent session."""
        response = client.get("/export/session/99999?format=json")
        
        # Should return 404 for nonexistent session
        assert response.status_code == 404
    
    def test_export_history_json(self, client, sample_data_file):
        """Test exporting history as JSON."""
        # Create some sessions first
        generate_data_quality_report(sample_data_file, report_format="json")
        
        response = client.get("/export/history?format=json")
        
        assert response.status_code == 200
        assert "check_history.json" in response.headers.get("content-disposition", "")
    
    def test_export_history_csv(self, client, sample_data_file):
        """Test exporting history as CSV."""
        generate_data_quality_report(sample_data_file, report_format="json")
        
        response = client.get("/export/history?format=csv")
        
        assert response.status_code == 200
        assert "check_history.csv" in response.headers.get("content-disposition", "").lower()
    
    def test_export_history_with_limit(self, client, sample_data_file):
        """Test exporting history with limit."""
        generate_data_quality_report(sample_data_file, report_format="json")
        
        response = client.get("/export/history?format=json&limit=10")
        
        assert response.status_code == 200

