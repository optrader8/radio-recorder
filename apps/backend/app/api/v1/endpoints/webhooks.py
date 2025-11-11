"""
Webhook endpoints for event subscriptions with database persistence
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import httpx
import asyncio
from datetime import datetime

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.services.event_bus import event_bus, EventType, Event
from app.services.persistence_service import persistence_service

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
    success_count: int = 0
    error_count: int = 0
    last_triggered_at: Optional[str] = None


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
        # Validate event types
        valid_types = {e.value for e in EventType}
        for event_type in webhook_in.event_types:
            if event_type not in valid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid event type: {event_type}"
                )

        # Save to database
        webhook_id = await persistence_service.save_webhook(
            db,
            current_user.id,
            str(webhook_in.url),
            webhook_in.event_types,
            webhook_in.description,
        )

        if not webhook_id:
            raise HTTPException(status_code=500, detail="Failed to create webhook")

        # Subscribe to events
        for event_type_str in webhook_in.event_types:
            try:
                event_type = EventType(event_type_str)
                await event_bus.subscribe(
                    event_type,
                    str(current_user.id),
                    lambda evt, url=str(webhook_in.url), wid=webhook_id: asyncio.create_task(
                        _trigger_webhook(url, evt, wid, db)
                    ),
                )
            except ValueError:
                pass

        logger.info(f"Webhook created: {webhook_id} for user {current_user.username}")

        return WebhookResponse(
            id=str(webhook_id),
            url=str(webhook_in.url),
            event_types=webhook_in.event_types,
            description=webhook_in.description,
            is_active=True,
            created_at=datetime.utcnow().isoformat(),
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
        webhooks = await persistence_service.list_webhooks(db, current_user.id)

        return {
            "webhooks": [
                WebhookResponse(
                    id=str(w.id),
                    url=w.url,
                    event_types=w.event_types,
                    description=w.description,
                    is_active=w.is_active,
                    created_at=w.created_at.isoformat(),
                    success_count=w.success_count,
                    error_count=w.error_count,
                    last_triggered_at=w.last_triggered_at.isoformat() if w.last_triggered_at else None,
                )
                for w in webhooks
            ],
            "total": len(webhooks),
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
        try:
            wid = UUID(webhook_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid webhook ID")

        webhook = await persistence_service.get_webhook(db, wid, current_user.id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")

        return {
            "webhook": WebhookResponse(
                id=str(webhook.id),
                url=webhook.url,
                event_types=webhook.event_types,
                description=webhook.description,
                is_active=webhook.is_active,
                created_at=webhook.created_at.isoformat(),
                success_count=webhook.success_count,
                error_count=webhook.error_count,
                last_triggered_at=webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None,
            ),
            "statistics": {
                "success_count": webhook.success_count,
                "error_count": webhook.error_count,
                "last_triggered": webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None,
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
        try:
            wid = UUID(webhook_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid webhook ID")

        webhook = await persistence_service.update_webhook(
            db,
            wid,
            current_user.id,
            url=str(webhook_in.url) if webhook_in.url else None,
            event_types=webhook_in.event_types,
            description=webhook_in.description,
            is_active=webhook_in.is_active,
        )

        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")

        logger.info(f"Webhook updated: {wid}")

        return WebhookResponse(
            id=str(webhook.id),
            url=webhook.url,
            event_types=webhook.event_types,
            description=webhook.description,
            is_active=webhook.is_active,
            created_at=webhook.created_at.isoformat(),
            success_count=webhook.success_count,
            error_count=webhook.error_count,
            last_triggered_at=webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None,
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
        try:
            wid = UUID(webhook_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid webhook ID")

        success = await persistence_service.delete_webhook(db, wid, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Webhook not found")

        logger.info(f"Webhook deleted: {wid}")
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
        try:
            wid = UUID(webhook_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid webhook ID")

        webhook = await persistence_service.get_webhook(db, wid, current_user.id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")

        # Create test event
        test_event = Event(
            type=EventType.SYSTEM_NOTIFICATION,
            user_id=str(current_user.id),
            timestamp=datetime.utcnow(),
            data={
                "test": True,
                "message": "Webhook test event"
            }
        )

        # Trigger webhook
        success = await _trigger_webhook(webhook.url, test_event, wid, db)

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
        events = await persistence_service.get_event_logs(db, current_user.id, limit=limit)
        return {
            "events": [
                {
                    "id": str(e.id),
                    "event_type": e.event_type,
                    "resource_type": e.resource_type,
                    "resource_id": str(e.resource_id) if e.resource_id else None,
                    "data": e.data,
                    "created_at": e.created_at.isoformat(),
                }
                for e in events
            ],
            "total": len(events),
        }
    except Exception as e:
        logger.error(f"Error getting event history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get event history")


async def _trigger_webhook(url: str, event: Event, webhook_id: UUID, db: AsyncSession) -> bool:
    """Trigger a webhook with an event"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json=event.to_dict(),
                headers={"Content-Type": "application/json"},
            )

            success = response.status_code in [200, 201, 202, 204]

            # Update webhook statistics in database
            if success:
                await persistence_service.update_webhook(
                    db,
                    webhook_id,
                    event.user_id,
                    success_count=db.query.count() + 1,
                    last_triggered_at=datetime.utcnow(),
                )
            else:
                await persistence_service.update_webhook(
                    db,
                    webhook_id,
                    event.user_id,
                    error_count=db.query.count() + 1,
                    last_triggered_at=datetime.utcnow(),
                )

            if success:
                logger.debug(f"Webhook triggered successfully: {webhook_id}")
            else:
                logger.warning(f"Webhook trigger failed ({response.status_code}): {webhook_id}")

            return success

    except asyncio.TimeoutError:
        logger.error(f"Webhook timeout: {webhook_id}")
        return False
    except Exception as e:
        logger.error(f"Error triggering webhook {webhook_id}: {e}")
        return False
