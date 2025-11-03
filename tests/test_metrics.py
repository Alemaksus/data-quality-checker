"""
Integration tests for metrics endpoints.
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
    """Create sample data file for testing."""
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "email": ["alice@test.com", "bob@test.com", "charlie@test.com"],
        "age": [30, 25, 35]
    })
    file_path = tmp_path / "test_data.csv"
    df.to_csv(file_path, index=False)
    return file_path


class TestMetricsEndpoints:
    """Tests for metrics endpoints."""
    
    def test_usage_metrics_default(self, client, sample_data_file):
        """Test usage metrics with default parameters."""
        # Create some check sessions first
        generate_data_quality_report(sample_data_file, report_format="json")
        generate_data_quality_report(sample_data_file, report_format="json")
        
        response = client.get("/metrics/usage")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "period_days" in data
        assert "period_start" in data
        assert "period_end" in data
        assert "statistics" in data
        
        stats = data["statistics"]
        assert "total_checks" in stats
        assert "total_issues" in stats
        assert "average_issues_per_check" in stats
        assert "checks_by_day" in stats
        assert "checks_by_format" in stats
    
    def test_usage_metrics_custom_period(self, client, sample_data_file):
        """Test usage metrics with custom period."""
        generate_data_quality_report(sample_data_file, report_format="json")
        
        response = client.get("/metrics/usage?days=30")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["period_days"] == 30
    
    def test_metrics_summary(self, client, sample_data_file):
        """Test metrics summary endpoint."""
        # Create some check sessions first
        generate_data_quality_report(sample_data_file, report_format="json")
        
        response = client.get("/metrics/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_checks" in data
        assert "total_issues" in data
        assert "average_issues_per_check" in data
        assert "first_check" in data
        assert "last_check" in data
        assert "issues_by_severity" in data
        
        # Check data types
        assert isinstance(data["total_checks"], int)
        assert isinstance(data["total_issues"], int)
        assert isinstance(data["average_issues_per_check"], (int, float))

