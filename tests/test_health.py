"""
Integration tests for health check endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app


pytestmark = pytest.mark.integration


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "Data Quality Checker API"
        assert "version" in data
    
    def test_detailed_health_check(self, client):
        """Test detailed health check endpoint."""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data
        assert "service" in data
        
        if data["status"] == "healthy":
            assert "system" in data
            assert "components" in data
            
            # Check system metrics
            if "system" in data:
                assert "cpu_percent" in data["system"]
                assert "memory" in data["system"]
                assert "disk" in data["system"]
            
            # Check components
            if "components" in data:
                assert "database" in data["components"]
                assert "reports_directory" in data["components"]

