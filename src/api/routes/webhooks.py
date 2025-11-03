"""
Webhook endpoints for notifications.
"""
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict
import httpx
import asyncio
from datetime import datetime
from enum import Enum

router = APIRouter()


class WebhookEvent(str, Enum):
    """Webhook event types."""
    CHECK_COMPLETED = "check.completed"
    CHECK_FAILED = "check.failed"
    BATCH_COMPLETED = "batch.completed"


class WebhookConfig(BaseModel):
    """Webhook configuration."""
    url: HttpUrl = Field(..., description="Webhook URL to send notifications to")
    events: List[WebhookEvent] = Field(..., description="List of events to subscribe to")
    secret: Optional[str] = Field(None, description="Optional secret for webhook signature")
    enabled: bool = Field(True, description="Whether the webhook is enabled")


# In-memory storage for webhooks (use database in production)
webhooks: Dict[str, WebhookConfig] = {}


async def send_webhook(webhook_id: str, event: WebhookEvent, data: Dict):
    """
    Send webhook notification.
    
    Args:
        webhook_id: ID of the webhook configuration
        event: Event type
        data: Event data payload
    """
    if webhook_id not in webhooks:
        return
    
    webhook = webhooks[webhook_id]
    
    if not webhook.enabled:
        return
    
    if event not in webhook.events:
        return
    
    try:
        payload = {
            "event": event.value,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Data-Quality-Checker-API/1.0.0"
        }
        
        # Add signature if secret is configured
        if webhook.secret:
            import hmac
            import hashlib
            import json
            payload_str = json.dumps(payload, sort_keys=True)
            signature = hmac.new(
                webhook.secret.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = f"sha256={signature}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                str(webhook.url),
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
    except Exception as e:
        # Log error but don't fail the request
        print(f"Webhook delivery failed for {webhook_id}: {e}")


@router.post("/webhooks", tags=["Webhooks"])
async def create_webhook(
    webhook_data: Dict = Body(..., description="Webhook data with webhook_id and webhook config")
) -> Dict:
    """
    Create a new webhook configuration.
    
    Example:
    {
        "webhook_id": "my_webhook",
        "url": "https://example.com/webhook",
        "events": ["check.completed", "check.failed"],
        "secret": "my_secret_key",
        "enabled": true
    }
    """
    webhook_id = webhook_data.get("webhook_id")
    if not webhook_id:
        raise HTTPException(status_code=400, detail="webhook_id is required")
    
    webhook_config = WebhookConfig(**{k: v for k, v in webhook_data.items() if k != "webhook_id"})
    webhooks[webhook_id] = webhook_config
    
    return {
        "message": f"Webhook '{webhook_id}' created successfully",
        "webhook_id": webhook_id,
        "url": str(webhook_config.url),
        "events": [e.value if isinstance(e, WebhookEvent) else e for e in webhook_config.events]
    }


@router.get("/webhooks", tags=["Webhooks"])
async def list_webhooks() -> Dict:
    """
    List all configured webhooks.
    """
    return {
        "webhooks": [
            {
                "webhook_id": webhook_id,
                "url": str(config.url),
                "events": [e.value for e in config.events],
                "enabled": config.enabled
            }
            for webhook_id, config in webhooks.items()
        ]
    }


@router.get("/webhooks/{webhook_id}", tags=["Webhooks"])
async def get_webhook(webhook_id: str) -> WebhookConfig:
    """
    Get a specific webhook configuration.
    """
    if webhook_id not in webhooks:
        raise HTTPException(status_code=404, detail=f"Webhook '{webhook_id}' not found")
    
    return webhooks[webhook_id]


@router.put("/webhooks/{webhook_id}", tags=["Webhooks"])
async def update_webhook(webhook_id: str, webhook_data: Dict = Body(...)) -> Dict:
    """
    Update an existing webhook configuration.
    """
    if webhook_id not in webhooks:
        raise HTTPException(status_code=404, detail=f"Webhook '{webhook_id}' not found")
    
    webhook_config = WebhookConfig(**webhook_data)
    webhooks[webhook_id] = webhook_config
    
    return {
        "message": f"Webhook '{webhook_id}' updated successfully"
    }


@router.delete("/webhooks/{webhook_id}", tags=["Webhooks"])
async def delete_webhook(webhook_id: str) -> Dict:
    """
    Delete a webhook configuration.
    """
    if webhook_id not in webhooks:
        raise HTTPException(status_code=404, detail=f"Webhook '{webhook_id}' not found")
    
    del webhooks[webhook_id]
    
    return {
        "message": f"Webhook '{webhook_id}' deleted successfully"
    }


@router.post("/webhooks/{webhook_id}/test", tags=["Webhooks"])
async def test_webhook(webhook_id: str) -> Dict:
    """
    Send a test webhook notification.
    """
    if webhook_id not in webhooks:
        raise HTTPException(status_code=404, detail=f"Webhook '{webhook_id}' not found")
    
    test_data = {
        "message": "This is a test webhook",
        "test": True
    }
    
    await send_webhook(webhook_id, WebhookEvent.CHECK_COMPLETED, test_data)
    
    return {
        "message": f"Test webhook sent to '{webhook_id}'"
    }

