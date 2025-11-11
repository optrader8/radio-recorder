"""
Webhook endpoints for event subscriptions
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import httpx
import asyncio

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.services.event_bus import event_bus, EventType, Event

logger = logging.getLogger(__name__)

router = APIRouter()


class WebhookCreate(BaseModel):
    """Request model for creating webhook"""
    url: HttpUrl
    event_types: List[str]  # List of event type values
    description: Optional[str] = None


class WebhookUpdate(BaseModel):
    """Request model for updating webhook"""
    url: Optional[HttpUrl] = None
    event_types: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class WebhookResponse(BaseModel):
    """Response model for webhook"""
    id: str
    url: str
    event_types: List[str]
    description: Optional[str]
    is_active: bool
    created_at: str


# In-memory webhook store (in production, use database)
webhooks: dict = {}


@router.post("/webhooks", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_in: WebhookCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> WebhookResponse:
    """
    Register a webhook for event notifications

    The webhook will receive POST requests with event data in JSON format:
    ```json
    {
      "type": "recording.started",
      "user_id": "...",
      "timestamp": "2024-01-15T10:30:00Z",
      "data": {...}
    }
    ```
    """
    try:
        from uuid import uuid4
        from datetime import datetime

        # Validate event types
        valid_types = {e.value for e in EventType}
        for event_type in webhook_in.event_types:
            if event_type not in valid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid event type: {event_type}"
                )

        webhook_id = str(uuid4())
        webhook = {
            "id": webhook_id,
            "user_id": str(current_user.id),
            "url": str(webhook_in.url),
            "event_types": webhook_in.event_types,
            "description": webhook_in.description,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "last_triggered": None,
            "success_count": 0,
            "error_count": 0,
        }

        webhooks[webhook_id] = webhook

        # Subscribe to events
        for event_type_str in webhook_in.event_types:
            try:
                event_type = EventType(event_type_str)
                await event_bus.subscribe(
                    event_type,
                    str(current_user.id),
                    lambda evt, url=str(webhook_in.url): asyncio.create_task(
                        _trigger_webhook(url, evt, webhook_id)
                    ),
                )
            except ValueError:
                pass

        logger.info(f"Webhook created: {webhook_id} for user {current_user.username}")

        return WebhookResponse(
            id=webhook_id,
            url=str(webhook_in.url),
            event_types=webhook_in.event_types,
            description=webhook_in.description,
            is_active=True,
            created_at=webhook["created_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to create webhook")


@router.get("/webhooks")
async def list_webhooks(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get all webhooks for current user"""
    try:
        user_webhooks = [
            w for w in webhooks.values()
            if w["user_id"] == str(current_user.id)
        ]

        return {
            "webhooks": [
                WebhookResponse(
                    id=w["id"],
                    url=w["url"],
                    event_types=w["event_types"],
                    description=w["description"],
                    is_active=w["is_active"],
                    created_at=w["created_at"],
                )
                for w in user_webhooks
            ],
            "total": len(user_webhooks),
        }
    except Exception as e:
        logger.error(f"Error listing webhooks: {e}")
        raise HTTPException(status_code=500, detail="Failed to list webhooks")


@router.get("/webhooks/{webhook_id}")
async def get_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get webhook details"""
    try:
        webhook = webhooks.get(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")

        if webhook["user_id"] != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

        return {
            "webhook": WebhookResponse(
                id=webhook["id"],
                url=webhook["url"],
                event_types=webhook["event_types"],
                description=webhook["description"],
                is_active=webhook["is_active"],
                created_at=webhook["created_at"],
            ),
            "statistics": {
                "success_count": webhook["success_count"],
                "error_count": webhook["error_count"],
                "last_triggered": webhook["last_triggered"],
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook")


@router.patch("/webhooks/{webhook_id}")
async def update_webhook(
    webhook_id: str,
    webhook_in: WebhookUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> WebhookResponse:
    """Update webhook"""
    try:
        webhook = webhooks.get(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")

        if webhook["user_id"] != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

        # Update fields
        if webhook_in.url:
            webhook["url"] = str(webhook_in.url)
        if webhook_in.event_types:
            webhook["event_types"] = webhook_in.event_types
        if webhook_in.description is not None:
            webhook["description"] = webhook_in.description
        if webhook_in.is_active is not None:
            webhook["is_active"] = webhook_in.is_active

        logger.info(f"Webhook updated: {webhook_id}")

        return WebhookResponse(
            id=webhook["id"],
            url=webhook["url"],
            event_types=webhook["event_types"],
            description=webhook["description"],
            is_active=webhook["is_active"],
            created_at=webhook["created_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to update webhook")


@router.delete("/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete webhook"""
    try:
        webhook = webhooks.get(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")

        if webhook["user_id"] != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

        del webhooks[webhook_id]
        logger.info(f"Webhook deleted: {webhook_id}")

        return {}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete webhook")


@router.post("/webhooks/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Test webhook by sending a sample event"""
    try:
        webhook = webhooks.get(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")

        if webhook["user_id"] != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

        # Create test event
        test_event = Event(
            type=EventType.SYSTEM_NOTIFICATION,
            user_id=str(current_user.id),
            timestamp=__import__('datetime').datetime.utcnow(),
            data={
                "test": True,
                "message": "Webhook test event"
            }
        )

        # Trigger webhook
        success = await _trigger_webhook(webhook["url"], test_event, webhook_id)

        return {
            "success": success,
            "message": "Test event sent" if success else "Failed to send test event"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to test webhook")


@router.get("/events/history")
async def get_event_history(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get recent event history for current user"""
    try:
        history = event_bus.get_event_history(str(current_user.id), limit)
        return {
            "events": [e.to_dict() for e in history],
            "total": len(history),
        }
    except Exception as e:
        logger.error(f"Error getting event history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get event history")


async def _trigger_webhook(url: str, event: Event, webhook_id: str) -> bool:
    """Trigger a webhook with an event"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json=event.to_dict(),
                headers={"Content-Type": "application/json"},
            )

            success = response.status_code in [200, 201, 202, 204]

            # Update webhook statistics
            if webhook_id in webhooks:
                webhooks[webhook_id]["last_triggered"] = __import__('datetime').datetime.utcnow().isoformat()
                if success:
                    webhooks[webhook_id]["success_count"] += 1
                else:
                    webhooks[webhook_id]["error_count"] += 1

            if success:
                logger.debug(f"Webhook triggered successfully: {webhook_id}")
            else:
                logger.warning(f"Webhook trigger failed ({response.status_code}): {webhook_id}")

            return success

    except asyncio.TimeoutError:
        logger.error(f"Webhook timeout: {webhook_id}")
        if webhook_id in webhooks:
            webhooks[webhook_id]["error_count"] += 1
        return False
    except Exception as e:
        logger.error(f"Error triggering webhook {webhook_id}: {e}")
        if webhook_id in webhooks:
            webhooks[webhook_id]["error_count"] += 1
        return False
