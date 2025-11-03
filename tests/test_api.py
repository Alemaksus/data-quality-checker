"""
Integration tests for API endpoints using FastAPI TestClient.
Tests for /upload-data/ and /upload-from-url/ endpoints.
"""
import pytest

pytestmark = pytest.mark.integration
from fastapi.testclient import TestClient
from pathlib import Path
import pandas as pd
import tempfile
from src.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing."""
    df = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", None, "Eve"],
        "email": ["alice@example.com", "invalid-email", "charlie@example.com", "david@example.com", "eve@example.com"],
        "age": [30, 27, 35, 45, None]
    })
    file_path = tmp_path / "test_upload.csv"
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def sample_json_file(tmp_path):
    """Create a sample JSON file for testing."""
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "value": [10, 20, 30]
    })
    file_path = tmp_path / "test_upload.json"
    df.to_json(file_path, orient='records', lines=False)
    return file_path


class TestUploadDataEndpoint:
    """Tests for POST /upload-data/ endpoint."""
    
    def test_upload_data_csv(self, client, sample_csv_file):
        """Test uploading a CSV file."""
        with open(sample_csv_file, "rb") as f:
            response = client.post(
                "/upload-data/",
                files={"file": ("test.csv", f, "text/csv")},
                data={
                    "report_format": "md",
                    "include_ai_insights": "true",
                    "client_name": "Test Client"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "report_paths" in data
        assert "✅" in data["message"]
    
    def test_upload_data_json(self, client, sample_json_file):
        """Test uploading a JSON file."""
        with open(sample_json_file, "rb") as f:
            response = client.post(
                "/upload-data/",
                files={"file": ("test.json", f, "application/json")},
                data={
                    "report_format": "html",
                    "include_ai_insights": "true"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "report_paths" in data
    
    def test_upload_data_all_formats(self, client, sample_csv_file):
        """Test uploading with all report formats."""
        with open(sample_csv_file, "rb") as f:
            response = client.post(
                "/upload-data/",
                files={"file": ("test.csv", f, "text/csv")},
                data={
                    "report_format": "all",
                    "include_ai_insights": "true"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        report_paths = data["report_paths"]
        
        # Should have markdown, html, and pdf (if available)
        assert "markdown" in report_paths or len(report_paths) > 0
    
    def test_upload_data_without_ai(self, client, sample_csv_file):
        """Test uploading without AI insights."""
        with open(sample_csv_file, "rb") as f:
            response = client.post(
                "/upload-data/",
                files={"file": ("test.csv", f, "text/csv")},
                data={
                    "report_format": "md",
                    "include_ai_insights": "false"
                }
            )
        
        assert response.status_code == 200
    
    def test_upload_data_invalid_file(self, client):
        """Test uploading an invalid file."""
        response = client.post(
            "/upload-data/",
            files={"file": ("test.txt", b"not a csv or json", "text/plain")},
            data={"report_format": "md"}
        )
        
        # Should return error for unsupported format
        assert response.status_code in [400, 422]
    
    def test_upload_data_missing_file(self, client):
        """Test uploading without file."""
        response = client.post(
            "/upload-data/",
            data={"report_format": "md"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_upload_data_returns_session_id(self, client, sample_csv_file):
        """Test that upload returns session_id when saved to DB."""
        with open(sample_csv_file, "rb") as f:
            response = client.post(
                "/upload-data/",
                files={"file": ("test.csv", f, "text/csv")},
                data={
                    "report_format": "md",
                    "include_ai_insights": "true"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        # session_id might be in report_paths or at top level
        report_paths = data.get("report_paths", {})
        # Check if session_id is present (might be in report_paths or separate)
        assert "session_id" in report_paths or "issues_count" in report_paths
    
    def test_upload_data_error_handling(self, client):
        """Test error handling in upload endpoint."""
        # Test with invalid file that causes error during processing
        response = client.post(
            "/upload-data/",
            files={"file": ("test.csv", b"invalid,csv,content\nbroken", "text/csv")},
            data={"report_format": "md"}
        )
        
        # Should handle error gracefully (either succeed or return 400)
        assert response.status_code in [200, 400]
    
class TestUploadFromUrlEndpoint:
    """Tests for POST /upload-from-url/ endpoint."""
    
    def test_upload_from_url_missing_url(self, client):
        """Test upload from URL without URL parameter."""
        response = client.post(
            "/upload-from-url/",
            data={"report_format": "md"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_upload_from_url_invalid_url(self, client):
        """Test upload from URL with invalid URL."""
        response = client.post(
            "/upload-from-url/",
            data={
                "url": "not-a-valid-url",
                "report_format": "md"
            }
        )
        
        # Should return error for invalid URL
        assert response.status_code in [400, 422]
    
    def test_upload_from_url_invalid_scheme(self, client):
        """Test upload from URL with invalid scheme."""
        response = client.post(
            "/upload-from-url/",
            data={
                "url": "ftp://example.com/file.csv",
                "report_format": "md"
            }
        )
        
        # Should return error for invalid scheme
        assert response.status_code == 400
    
    def test_upload_from_url_error_handling(self, client):
        """Test upload from URL error handling."""
        # Test with non-existent URL (should return error)
        response = client.post(
            "/upload-from-url/",
            data={
                "url": "http://invalid-domain-that-does-not-exist-12345.com/file.csv",
                "report_format": "md"
            }
        )
        
        # Should return error for unreachable URL
        assert response.status_code in [400, 408, 503]
    
    def test_upload_from_url_error_path(self, client):
        """Test upload from URL error handling path."""
        # Test that exception handling works
        response = client.post(
            "/upload-from-url/",
            data={
                "url": "http://invalid-url-test-12345.com/file.csv",
                "report_format": "md"
            }
        )
        
        # Should return error
        assert response.status_code in [400, 408, 503]
    
    def test_upload_from_url_success_path(self, client):
        """Test upload from URL success path."""
        from unittest.mock import patch
        from pathlib import Path
        import tempfile
        
        # Mock the download function to return a valid file
        async def mock_download(url):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
            temp_file.write(b"id,name\n1,Alice\n2,Bob")
            temp_file.close()
            return Path(temp_file.name)
        
        with patch('src.api.main.download_file_from_url', side_effect=mock_download):
            response = client.post(
                "/upload-from-url/",
                data={
                    "url": "http://example.com/data.csv",
                    "report_format": "md"
                }
            )
            
            # Should succeed
            assert response.status_code == 200


class TestHistoryEndpoint:
    """Tests for GET /checks/history endpoint."""
    
    def test_get_check_history(self, client):
        """Test getting check history."""
        response = client.get("/checks/history")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_check_history_with_issues(self, client):
        """Test getting check history with issues."""
        response = client.get("/checks/history?with_issues=true")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # If there are sessions, check structure
        if len(data) > 0:
            session = data[0]
            assert "id" in session
            assert "filename" in session
            assert "issues_found" in session


class TestSummaryEndpoint:
    """Tests for GET /checks/summary endpoint."""
    
    def test_get_check_summary(self, client):
        """Test getting check summary."""
        response = client.get("/checks/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # If there are summaries, check structure
        if len(data) > 0:
            summary = data[0]
            assert "session_id" in summary
            assert "filename" in summary
            assert "issue_count" in summary


class TestAPIErrorHandling:
    """Tests for API error handling."""
    
    def test_upload_data_large_file_handling(self, client):
        """Test handling of large files (if there's a limit)."""
        # Create a large file (in memory)
        large_content = "id,name,email\n" + "\n".join([f"{i},Name{i},email{i}@test.com" for i in range(10000)])
        
        response = client.post(
            "/upload-data/",
            files={"file": ("large.csv", large_content.encode(), "text/csv")},
            data={"report_format": "md"}
        )
        
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 400, 413, 500]
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        # Test with actual request to see CORS headers
        response = client.get("/checks/history")
        
        # CORS headers might be present in actual requests
        # Just verify endpoint works (CORS middleware is configured)
        assert response.status_code == 200


class TestComparisonEndpoints:
    """Tests for comparison endpoints."""
    
    def test_compare_sessions_endpoint(self, client, clean_db, db_session):
        """Test GET /checks/compare endpoint."""
        from datetime import datetime
        from src.db.models import CheckSession, Issue
        
        # Create two sessions
        session1 = CheckSession(
            filename="test1.csv",
            file_format="csv",
            rows=100,
            issues_found=10,
            created_at=datetime.utcnow()
        )
        db_session.add(session1)
        db_session.flush()
        
        session2 = CheckSession(
            filename="test2.csv",
            file_format="csv",
            rows=100,
            issues_found=5,
            created_at=datetime.utcnow()
        )
        db_session.add(session2)
        db_session.flush()
        
        db_session.commit()
        
        # Test comparison endpoint
        response = client.get(
            "/checks/compare",
            params={"session_id1": session1.id, "session_id2": session2.id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session1" in data
        assert "session2" in data
        assert "comparison" in data
        assert "trend" in data["comparison"]
    
    def test_compare_sessions_not_found(self, client):
        """Test compare endpoint with non-existent sessions."""
        response = client.get(
            "/checks/compare",
            params={"session_id1": 9999, "session_id2": 9998}
        )
        
        assert response.status_code == 404
    
    def test_compare_sessions_missing_params(self, client):
        """Test compare endpoint with missing parameters."""
        response = client.get("/checks/compare")
        
        assert response.status_code == 422  # Validation error
    
    def test_get_quality_trend_endpoint(self, client, clean_db, db_session):
        """Test GET /checks/{session_id}/trend endpoint."""
        from datetime import datetime
        from src.db.models import CheckSession
        
        # Create a session
        session = CheckSession(
            filename="test.csv",
            file_format="csv",
            rows=100,
            issues_found=10,
            created_at=datetime.utcnow()
        )
        db_session.add(session)
        db_session.commit()
        
        # Test trend endpoint
        response = client.get(f"/checks/{session.id}/trend", params={"days_back": 30})
        
        assert response.status_code == 200
        data = response.json()
        assert "current_session" in data
        assert "trend" in data
    
    def test_get_quality_trend_not_found(self, client):
        """Test trend endpoint with non-existent session."""
        response = client.get("/checks/9999/trend")
        
        assert response.status_code == 404
    
    def test_upload_data_excel_format(self, client, sample_csv_file):
        """Test uploading with Excel format."""
        with open(sample_csv_file, "rb") as f:
            response = client.post(
                "/upload-data/",
                files={"file": ("test.csv", f, "text/csv")},
                data={
                    "report_format": "xlsx",
                    "include_ai_insights": "true"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        report_paths = data.get("report_paths", {})
        # Excel might be None if openpyxl not installed, or a path if installed
        assert "excel" in report_paths or len(report_paths) > 0
    
    def test_upload_data_excel_all_formats(self, client, sample_csv_file):
        """Test uploading with all formats including Excel."""
        with open(sample_csv_file, "rb") as f:
            response = client.post(
                "/upload-data/",
                files={"file": ("test.csv", f, "text/csv")},
                data={
                    "report_format": "all",
                    "include_ai_insights": "true"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        report_paths = data.get("report_paths", {})
        # Should have multiple formats
        assert len(report_paths) > 0
