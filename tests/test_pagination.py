"""
Integration tests for pagination functionality.
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


class TestPagination:
    """Tests for pagination functionality."""
    
    def test_pagination_default(self, client, sample_data_file):
        """Test pagination with default parameters."""
        # Create multiple sessions
        for i in range(15):
            generate_data_quality_report(sample_data_file, report_format="json")
        
        response = client.get("/checks/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "pagination" in data
        
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 10
        assert pagination["total_items"] >= 15
        assert pagination["total_pages"] >= 2
        assert isinstance(pagination["has_next"], bool)
        assert isinstance(pagination["has_previous"], bool)
    
    def test_pagination_custom_page_size(self, client, sample_data_file):
        """Test pagination with custom page size."""
        # Create multiple sessions
        for i in range(20):
            generate_data_quality_report(sample_data_file, report_format="json")
        
        response = client.get("/checks/history?page=1&page_size=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) <= 5
        assert data["pagination"]["page_size"] == 5
        assert data["pagination"]["total_items"] >= 20
    
    def test_pagination_multiple_pages(self, client, sample_data_file):
        """Test pagination across multiple pages."""
        # Create multiple sessions
        for i in range(25):
            generate_data_quality_report(sample_data_file, report_format="json")
        
        # Get first page
        page1_response = client.get("/checks/history?page=1&page_size=10")
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        
        assert page1_data["pagination"]["page"] == 1
        assert page1_data["pagination"]["has_next"] is True
        assert page1_data["pagination"]["has_previous"] is False
        
        # Get second page
        page2_response = client.get("/checks/history?page=2&page_size=10")
        assert page2_response.status_code == 200
        page2_data = page2_response.json()
        
        assert page2_data["pagination"]["page"] == 2
        assert page2_data["pagination"]["has_next"] is True
        assert page2_data["pagination"]["has_previous"] is True
        
        # Get last page
        last_page = page2_data["pagination"]["total_pages"]
        last_page_response = client.get(f"/checks/history?page={last_page}&page_size=10")
        assert last_page_response.status_code == 200
        last_page_data = last_page_response.json()
        
        assert last_page_data["pagination"]["page"] == last_page
        assert last_page_data["pagination"]["has_next"] is False
        assert last_page_data["pagination"]["has_previous"] is True
    
    def test_pagination_with_issues(self, client, sample_data_file):
        """Test pagination with issues included."""
        # Create some sessions
        for i in range(5):
            generate_data_quality_report(sample_data_file, report_format="json")
        
        response = client.get("/checks/history?page=1&page_size=10&with_issues=true")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert len(data["items"]) > 0
    
    def test_pagination_empty_result(self, client, clean_db):
        """Test pagination with no results."""
        # clean_db fixture ensures empty database
        response = client.get("/checks/history?page=1&page_size=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["pagination"]["total_items"] == 0
        assert data["pagination"]["total_pages"] == 0
        assert data["pagination"]["has_next"] is False
        assert data["pagination"]["has_previous"] is False
    
    def test_pagination_invalid_page(self, client):
        """Test pagination with invalid page number."""
        response = client.get("/checks/history?page=0&page_size=10")
        
        # Should return 422 validation error or default to page 1
        assert response.status_code in [200, 422]
    
    def test_pagination_max_page_size(self, client, sample_data_file):
        """Test pagination with maximum page size."""
        # Create some sessions
        for i in range(50):
            generate_data_quality_report(sample_data_file, report_format="json")
        
        response = client.get("/checks/history?page=1&page_size=100")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) <= 100
        assert data["pagination"]["page_size"] <= 100
    
    def test_pagination_exceeds_max_page_size(self, client):
        """Test pagination with page size exceeding maximum."""
        response = client.get("/checks/history?page=1&page_size=200")
        
        # Should return 422 validation error
        assert response.status_code == 422

