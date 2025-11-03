"""
Integration tests for batch processing endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import pandas as pd
import tempfile
from src.api.main import app


pytestmark = pytest.mark.integration


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create sample CSV file."""
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "email": ["alice@test.com", "bob@test.com", "charlie@test.com"]
    })
    file_path = tmp_path / "test.csv"
    df.to_csv(file_path, index=False)
    return file_path


class TestBatchProcessing:
    """Tests for batch processing endpoints."""
    
    def test_batch_upload_single_file(self, client, sample_csv_file):
        """Test batch upload with single file."""
        # For List[UploadFile], send files as list of tuples with same field name
        with open(sample_csv_file, "rb") as f:
            content = f.read()
        
        # FastAPI expects multiple files with same field name
        files = [("files", ("test1.csv", content, "text/csv"))]
        data = {"report_format": "md"}  # Use valid format
        response = client.post("/upload-batch/", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert "message" in result
        assert "results" in result
        assert result["total_files"] == 1
        assert result["successful"] >= 0
        assert result["failed"] >= 0
    
    def test_batch_upload_multiple_files(self, client, sample_csv_file, tmp_path):
        """Test batch upload with multiple files."""
        # Create second file
        df2 = pd.DataFrame({
            "id": [4, 5],
            "value": [10, 20]
        })
        file2 = tmp_path / "test2.csv"
        df2.to_csv(file2, index=False)
        
        files = []
        with open(sample_csv_file, "rb") as f1:
            files.append(("files", ("test1.csv", f1.read(), "text/csv")))
        with open(file2, "rb") as f2:
            files.append(("files", ("test2.csv", f2.read(), "text/csv")))
        
        data = {"report_format": "md"}
        response = client.post("/upload-batch/", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["total_files"] == 2
        assert len(result["results"]) == 2
    
    def test_batch_upload_too_many_files(self, client, sample_csv_file):
        """Test batch upload with too many files."""
        files = []
        with open(sample_csv_file, "rb") as f:
            content = f.read()
        for i in range(11):  # Max is 10
            files.append(("files", (f"test{i}.csv", content, "text/csv")))
        
        data = {"report_format": "md"}
        response = client.post("/upload-batch/", files=files, data=data)
        
        assert response.status_code == 400
        assert "Maximum 10 files" in response.json()["detail"]
    
    def test_batch_upload_with_errors(self, client, tmp_path):
        """Test batch upload with some files that fail."""
        # Create one valid and one invalid file
        valid_file = tmp_path / "valid.csv"
        df = pd.DataFrame({"id": [1, 2]})
        df.to_csv(valid_file, index=False)
        
        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_text("not a csv")
        
        files = []
        with open(valid_file, "rb") as f1:
            files.append(("files", ("valid.csv", f1.read(), "text/csv")))
        with open(invalid_file, "rb") as f2:
            files.append(("files", ("invalid.txt", f2.read(), "text/plain")))
        
        data = {"report_format": "md"}
        response = client.post("/upload-batch/", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["total_files"] == 2
        assert result["successful"] >= 0
        assert result["failed"] >= 0
        assert result["successful"] + result["failed"] == 2

