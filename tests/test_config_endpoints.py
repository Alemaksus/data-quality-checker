"""
Integration tests for configuration and validation rules endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.routes.config import validation_configs


pytestmark = pytest.mark.integration


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_configs():
    """Clean validation configs before and after each test."""
    validation_configs.clear()
    yield
    validation_configs.clear()


class TestValidationConfigEndpoints:
    """Tests for validation configuration endpoints."""
    
    def test_create_validation_config(self, client):
        """Test creating a validation configuration."""
        config_data = {
            "config_name": "test_config",
            "description": "Test validation configuration",
            "rules": [
                {
                    "rule_name": "no_missing_values",
                    "rule_type": "missing_threshold",
                    "enabled": True,
                    "parameters": {"threshold": 0}
                },
                {
                    "rule_name": "age_range",
                    "rule_type": "range_check",
                    "enabled": True,
                    "parameters": {"column": "age", "min": 0, "max": 120}
                }
            ]
        }
        
        response = client.post("/config/validation-rules", json=config_data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["message"] == "Validation configuration 'test_config' created successfully"
        assert result["config_name"] == "test_config"
        assert result["rules_count"] == 2
    
    def test_list_validation_configs(self, client):
        """Test listing validation configurations."""
        # Create a config first
        config_data = {
            "config_name": "test_config",
            "rules": [{
                "rule_name": "test_rule",
                "rule_type": "missing_threshold",
                "enabled": True,
                "parameters": {}
            }]
        }
        client.post("/config/validation-rules", json=config_data)
        
        response = client.get("/config/validation-rules")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "configs" in data
        assert len(data["configs"]) >= 1
        assert any(c["config_name"] == "test_config" for c in data["configs"])
    
    def test_get_validation_config(self, client):
        """Test getting a specific validation configuration."""
        # Create a config first
        config_data = {
            "config_name": "test_config",
            "description": "Test config",
            "rules": [{
                "rule_name": "test_rule",
                "rule_type": "missing_threshold",
                "enabled": True,
                "parameters": {"threshold": 10}
            }]
        }
        client.post("/config/validation-rules", json=config_data)
        
        response = client.get("/config/validation-rules/test_config")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["config_name"] == "test_config"
        assert data["description"] == "Test config"
        assert len(data["rules"]) == 1
    
    def test_get_nonexistent_config(self, client):
        """Test getting a nonexistent configuration."""
        response = client.get("/config/validation-rules/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_validation_config(self, client):
        """Test updating a validation configuration."""
        # Create config first
        config_data = {
            "config_name": "test_config",
            "rules": [{
                "rule_name": "old_rule",
                "rule_type": "missing_threshold",
                "enabled": True,
                "parameters": {}
            }]
        }
        client.post("/config/validation-rules", json=config_data)
        
        # Update config
        updated_config = {
            "config_name": "test_config",
            "description": "Updated config",
            "rules": [{
                "rule_name": "new_rule",
                "rule_type": "range_check",
                "enabled": True,
                "parameters": {"column": "age", "min": 0, "max": 100}
            }]
        }
        response = client.put("/config/validation-rules/test_config", json=updated_config)
        
        assert response.status_code == 200
        result = response.json()
        assert result["config_name"] == "test_config"
        
        # Verify update
        get_response = client.get("/config/validation-rules/test_config")
        assert get_response.json()["description"] == "Updated config"
    
    def test_delete_validation_config(self, client):
        """Test deleting a validation configuration."""
        # Create config first
        config_data = {
            "config_name": "test_config",
            "rules": [{
                "rule_name": "test_rule",
                "rule_type": "missing_threshold",
                "enabled": True,
                "parameters": {}
            }]
        }
        client.post("/config/validation-rules", json=config_data)
        
        # Delete config
        response = client.delete("/config/validation-rules/test_config")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify deletion
        get_response = client.get("/config/validation-rules/test_config")
        assert get_response.status_code == 404

