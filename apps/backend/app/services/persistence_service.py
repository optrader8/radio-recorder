"""
Persistence service for saving webhooks, analysis results, and event logs to database
"""
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.analysis import (
    WebhookModel,
    RecordingAnalysisModel,
    EventLogModel,
    PlaybackHistoryModel,
    AdFeedbackModel,
)

logger = logging.getLogger(__name__)


class PersistenceService:
    """Service for persisting data to database"""

    # ==================== Webhook Methods ====================

    async def save_webhook(
        self,
        session: AsyncSession,
        user_id: UUID,
        url: str,
        event_types: List[str],
        description: Optional[str] = None,
    ) -> Optional[UUID]:
        """Save webhook to database"""
        try:
            webhook = WebhookModel(
                user_id=user_id,
                url=url,
                event_types=event_types,
                description=description,
                is_active=True,
            )
            session.add(webhook)
            await session.commit()
            logger.info(f"Webhook saved: {webhook.id}")
            return webhook.id
        except Exception as e:
            logger.error(f"Failed to save webhook: {e}")
            await session.rollback()
            return None

    async def get_webhook(
        self,
        session: AsyncSession,
        webhook_id: UUID,
        user_id: UUID,
    ) -> Optional[WebhookModel]:
        """Get webhook by ID"""
        try:
            stmt = select(WebhookModel).where(
                (WebhookModel.id == webhook_id) & (WebhookModel.user_id == user_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get webhook: {e}")
            return None

    async def list_webhooks(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> List[WebhookModel]:
        """List all webhooks for user"""
        try:
            stmt = select(WebhookModel).where(
                WebhookModel.user_id == user_id
            ).order_by(desc(WebhookModel.created_at))
            result = await session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to list webhooks: {e}")
            return []

    async def update_webhook(
        self,
        session: AsyncSession,
        webhook_id: UUID,
        user_id: UUID,
        **kwargs
    ) -> Optional[WebhookModel]:
        """Update webhook"""
        try:
            webhook = await self.get_webhook(session, webhook_id, user_id)
            if not webhook:
                return None

            for key, value in kwargs.items():
                if hasattr(webhook, key) and value is not None:
                    setattr(webhook, key, value)

            webhook.updated_at = datetime.utcnow()
            await session.commit()
            logger.info(f"Webhook updated: {webhook_id}")
            return webhook
        except Exception as e:
            logger.error(f"Failed to update webhook: {e}")
            await session.rollback()
            return None

    async def delete_webhook(
        self,
        session: AsyncSession,
        webhook_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Delete webhook"""
        try:
            webhook = await self.get_webhook(session, webhook_id, user_id)
            if not webhook:
                return False

            await session.delete(webhook)
            await session.commit()
            logger.info(f"Webhook deleted: {webhook_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete webhook: {e}")
            await session.rollback()
            return False

    # ==================== Analysis Results Methods ====================

    async def save_analysis_result(
        self,
        session: AsyncSession,
        user_id: UUID,
        recording_id: UUID,
        file_path: str,
        analysis_data: Dict[str, Any],
    ) -> Optional[UUID]:
        """Save recording analysis result"""
        try:
            analysis = RecordingAnalysisModel(
                user_id=user_id,
                recording_id=recording_id,
                file_path=file_path,
                transcription_text=analysis_data.get("transcription_text"),
                transcription_language=analysis_data.get("transcription_language", "unknown"),
                transcription_confidence=analysis_data.get("transcription_confidence", 0.0),
                duration_seconds=analysis_data.get("duration_seconds"),
                num_speakers=analysis_data.get("num_speakers", 0),
                clarity_score=analysis_data.get("clarity_score", 0.0),
                noise_level_db=analysis_data.get("noise_level_db", 0.0),
                snr_db=analysis_data.get("snr_db", 0.0),
                overall_quality=analysis_data.get("overall_quality", 0.0),
                detected_emotions=analysis_data.get("detected_emotions"),
                speaker_segments=analysis_data.get("speaker_segments"),
                detected_ads=analysis_data.get("detected_ads"),
                processing_time_seconds=analysis_data.get("processing_time_seconds", 0.0),
                analysis_engine=analysis_data.get("analysis_engine", "combined"),
            )
            session.add(analysis)
            await session.commit()
            logger.info(f"Analysis result saved: {analysis.id}")
            return analysis.id
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            await session.rollback()
            return None

    async def get_analysis_result(
        self,
        session: AsyncSession,
        recording_id: UUID,
        user_id: UUID,
    ) -> Optional[RecordingAnalysisModel]:
        """Get analysis result for recording"""
        try:
            stmt = select(RecordingAnalysisModel).where(
                (RecordingAnalysisModel.recording_id == recording_id) &
                (RecordingAnalysisModel.user_id == user_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get analysis result: {e}")
            return None

    # ==================== Event Log Methods ====================

    async def log_event(
        self,
        session: AsyncSession,
        user_id: UUID,
        event_type: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Optional[UUID]:
        """Log event to database"""
        try:
            event_log = EventLogModel(
                user_id=user_id,
                event_type=event_type,
                resource_type=resource_type,
                resource_id=resource_id,
                data=data,
            )
            session.add(event_log)
            await session.commit()
            logger.debug(f"Event logged: {event_type}")
            return event_log.id
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
            await session.rollback()
            return None

    async def get_event_logs(
        self,
        session: AsyncSession,
        user_id: UUID,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[EventLogModel]:
        """Get event logs for user"""
        try:
            stmt = select(EventLogModel).where(
                EventLogModel.user_id == user_id
            )
            if event_type:
                stmt = stmt.where(EventLogModel.event_type == event_type)

            stmt = stmt.order_by(desc(EventLogModel.created_at)).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get event logs: {e}")
            return []

    # ==================== Playback History Methods ====================

    async def save_playback_history(
        self,
        session: AsyncSession,
        user_id: UUID,
        station_id: UUID,
        station_name: str,
        duration_seconds: Optional[float] = None,
        bitrate: Optional[int] = None,
        skip_ads: bool = False,
    ) -> Optional[UUID]:
        """Save playback history"""
        try:
            history = PlaybackHistoryModel(
                user_id=user_id,
                station_id=station_id,
                station_name=station_name,
                duration_seconds=duration_seconds,
                bitrate=bitrate,
                skip_ads=skip_ads,
                ended_at=datetime.utcnow(),
            )
            session.add(history)
            await session.commit()
            logger.info(f"Playback history saved: {history.id}")
            return history.id
        except Exception as e:
            logger.error(f"Failed to save playback history: {e}")
            await session.rollback()
            return None

    async def get_playback_history(
        self,
        session: AsyncSession,
        user_id: UUID,
        limit: int = 50,
    ) -> List[PlaybackHistoryModel]:
        """Get playback history for user"""
        try:
            stmt = select(PlaybackHistoryModel).where(
                PlaybackHistoryModel.user_id == user_id
            ).order_by(desc(PlaybackHistoryModel.created_at)).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get playback history: {e}")
            return []

    # ==================== Ad Feedback Methods ====================

    async def save_ad_feedback(
        self,
        session: AsyncSession,
        user_id: UUID,
        start_time: float,
        end_time: float,
        feedback_type: str,
        recording_id: Optional[UUID] = None,
        confidence_before: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> Optional[UUID]:
        """Save user feedback on ad detection"""
        try:
            feedback = AdFeedbackModel(
                user_id=user_id,
                recording_id=recording_id,
                start_time=start_time,
                end_time=end_time,
                feedback_type=feedback_type,
                confidence_before=confidence_before,
                notes=notes,
            )
            session.add(feedback)
            await session.commit()
            logger.info(f"Ad feedback saved: {feedback.id}")
            return feedback.id
        except Exception as e:
            logger.error(f"Failed to save ad feedback: {e}")
            await session.rollback()
            return None

    async def get_recent_ad_feedback(
        self,
        session: AsyncSession,
        user_id: UUID,
        days: int = 30,
        limit: int = 1000,
    ) -> List[AdFeedbackModel]:
        """Get recent ad feedback for training data"""
        try:
            since = datetime.utcnow() - timedelta(days=days)
            stmt = select(AdFeedbackModel).where(
                (AdFeedbackModel.user_id == user_id) &
                (AdFeedbackModel.created_at >= since)
            ).order_by(desc(AdFeedbackModel.created_at)).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get ad feedback: {e}")
            return []


# Global instance
persistence_service = PersistenceService()
