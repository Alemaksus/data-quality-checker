"""
Integration tests for webhook endpoints.
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.routes.webhooks import webhooks, WebhookEvent


pytestmark = pytest.mark.integration


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_webhooks():
    """Clean webhooks before and after each test."""
    webhooks.clear()
    yield
    webhooks.clear()


class TestWebhookEndpoints:
    """Tests for webhook endpoints."""
    
    def test_create_webhook(self, client):
        """Test creating a webhook."""
        webhook_data = {
            "webhook_id": "test_webhook",
            "url": "https://example.com/webhook",
            "events": ["check.completed"],
            "secret": "test_secret",
            "enabled": True
        }
        
        response = client.post("/webhooks", json=webhook_data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert "message" in result
        assert result["webhook_id"] == "test_webhook"
        assert "url" in result
        assert "events" in result
    
    def test_list_webhooks(self, client):
        """Test listing webhooks."""
        # Create a webhook first
        webhook_data = {
            "webhook_id": "test_webhook",
            "url": "https://example.com/webhook",
            "events": ["check.completed"],
            "enabled": True
        }
        client.post("/webhooks", json=webhook_data)
        
        response = client.get("/webhooks")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "webhooks" in data
        assert len(data["webhooks"]) >= 1
    
    def test_get_webhook(self, client):
        """Test getting a specific webhook."""
        # Create webhook first
        webhook_data = {
            "webhook_id": "test_webhook",
            "url": "https://example.com/webhook",
            "events": ["check.completed", "check.failed"],
            "enabled": True
        }
        client.post("/webhooks", json=webhook_data)
        
        response = client.get("/webhooks/test_webhook")
        
        assert response.status_code == 200
        data = response.json()
        
        assert str(data["url"]) == "https://example.com/webhook"
        assert len(data["events"]) == 2
    
    def test_get_nonexistent_webhook(self, client):
        """Test getting a nonexistent webhook."""
        response = client.get("/webhooks/nonexistent")
        
        assert response.status_code == 404
    
    def test_update_webhook(self, client):
        """Test updating a webhook."""
        # Create webhook first
        webhook_data = {
            "webhook_id": "test_webhook",
            "url": "https://example.com/webhook",
            "events": ["check.completed"],
            "enabled": True
        }
        client.post("/webhooks", json=webhook_data)
        
        # Update webhook
        updated_data = {
            "url": "https://example.com/webhook-new",
            "events": ["check.completed", "batch.completed"],
            "enabled": False
        }
        response = client.put("/webhooks/test_webhook", json=updated_data)
        
        assert response.status_code == 200
        
        # Verify update
        get_response = client.get("/webhooks/test_webhook")
        assert str(get_response.json()["url"]) == "https://example.com/webhook-new"
    
    def test_delete_webhook(self, client):
        """Test deleting a webhook."""
        # Create webhook first
        webhook_data = {
            "webhook_id": "test_webhook",
            "url": "https://example.com/webhook",
            "events": ["check.completed"],
            "enabled": True
        }
        client.post("/webhooks", json=webhook_data)
        
        # Delete webhook
        response = client.delete("/webhooks/test_webhook")
        
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get("/webhooks/test_webhook")
        assert get_response.status_code == 404
    
    @patch('src.api.routes.webhooks.httpx.AsyncClient')
    def test_test_webhook_endpoint(self, mock_async_client, client):
        """Test test webhook endpoint."""
        # Create webhook first
        webhook_data = {
            "webhook_id": "test_webhook",
            "url": "https://example.com/webhook",
            "events": ["check.completed"],
            "enabled": True
        }
        client.post("/webhooks", json=webhook_data)
        
        # Mock HTTP client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_async_client.return_value.__aenter__.return_value = mock_client
        
        # Test webhook
        response = client.post("/webhooks/test_webhook/test")
        
        assert response.status_code == 200
        assert "test webhook sent" in response.json()["message"].lower()

