"""
Recording analysis endpoints for transcription, voice analysis, and statistics
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.services.persistence_service import persistence_service
from app.services.transcription_service import transcription_service
from app.services.voice_analysis_service import voice_analysis_service
from app.services.ml_ad_detection import ml_ad_detection

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/analysis/recording/{recording_id}")
async def get_recording_analysis(
    recording_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get analysis results for a recording"""
    try:
        try:
            rec_id = UUID(recording_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid recording ID")

        analysis = await persistence_service.get_analysis_result(db, rec_id, current_user.id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return {
            "analysis": {
                "id": str(analysis.id),
                "recording_id": str(analysis.recording_id),
                "transcription": {
                    "text": analysis.transcription_text,
                    "language": analysis.transcription_language,
                    "confidence": analysis.transcription_confidence,
                },
                "voice_quality": {
                    "clarity_score": analysis.clarity_score,
                    "noise_level_db": analysis.noise_level_db,
                    "snr_db": analysis.snr_db,
                    "overall_quality": analysis.overall_quality,
                },
                "speakers": {
                    "num_speakers": analysis.num_speakers,
                    "segments": analysis.speaker_segments or [],
                },
                "emotions": analysis.detected_emotions or {},
                "detected_ads": analysis.detected_ads or [],
                "processing_time_seconds": analysis.processing_time_seconds,
                "created_at": analysis.created_at.isoformat(),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analysis")


@router.post("/analysis/recording/{recording_id}/transcribe")
async def transcribe_recording(
    recording_id: str,
    file_path: str,
    language: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Transcribe a recording"""
    try:
        try:
            rec_id = UUID(recording_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid recording ID")

        # Transcribe
        result = await transcription_service.transcribe_file(file_path, language)
        if not result:
            raise HTTPException(status_code=500, detail="Transcription failed")

        # Save analysis
        analysis_data = {
            "transcription_text": result.text,
            "transcription_language": result.language,
            "transcription_confidence": result.confidence,
            "processing_time_seconds": result.processing_time_seconds,
            "analysis_engine": result.engine.value,
        }

        await persistence_service.save_analysis_result(
            db, current_user.id, rec_id, file_path, analysis_data
        )

        return {
            "success": True,
            "transcription": {
                "text": result.text,
                "language": result.language,
                "confidence": result.confidence,
                "segments": result.segments,
                "processing_time": result.processing_time_seconds,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transcribing: {e}")
        raise HTTPException(status_code=500, detail="Transcription error")


@router.post("/analysis/recording/{recording_id}/voice-analysis")
async def analyze_recording_voice(
    recording_id: str,
    file_path: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Analyze voice characteristics"""
    try:
        try:
            rec_id = UUID(recording_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid recording ID")

        # Analyze voice
        result = await voice_analysis_service.analyze_voice(file_path)
        if not result:
            raise HTTPException(status_code=500, detail="Voice analysis failed")

        # Save analysis
        analysis_data = {
            "duration_seconds": result.duration_seconds,
            "num_speakers": result.num_speakers,
            "clarity_score": result.voice_quality.clarity_score,
            "noise_level_db": result.voice_quality.noise_level,
            "snr_db": result.voice_quality.signal_to_noise_ratio,
            "overall_quality": result.voice_quality.overall_quality,
            "detected_emotions": result.emotions,
            "speaker_segments": [s.to_dict() for s in result.speaker_segments],
            "processing_time_seconds": result.processing_time_seconds,
        }

        await persistence_service.save_analysis_result(
            db, current_user.id, rec_id, file_path, analysis_data
        )

        return {
            "success": True,
            "voice_analysis": result.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing voice: {e}")
        raise HTTPException(status_code=500, detail="Voice analysis error")


@router.get("/analysis/playback-history")
async def get_playback_history(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get playback history for user"""
    try:
        history = await persistence_service.get_playback_history(db, current_user.id, limit)
        return {
            "history": [
                {
                    "id": str(h.id),
                    "station_id": str(h.station_id),
                    "station_name": h.station_name,
                    "duration_seconds": h.duration_seconds,
                    "bitrate": h.bitrate,
                    "skip_ads": h.skip_ads,
                    "started_at": h.started_at.isoformat(),
                    "ended_at": h.ended_at.isoformat() if h.ended_at else None,
                    "created_at": h.created_at.isoformat(),
                }
                for h in history
            ],
            "total": len(history),
        }
    except Exception as e:
        logger.error(f"Error getting playback history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get playback history")


@router.post("/analysis/ad-feedback")
async def submit_ad_feedback(
    recording_id: Optional[str] = None,
    start_time: float = 0.0,
    end_time: float = 0.0,
    feedback_type: str = "correct_ad",
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Submit feedback on ad detection accuracy"""
    try:
        try:
            rec_id = UUID(recording_id) if recording_id else None
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid recording ID")

        feedback_id = await persistence_service.save_ad_feedback(
            db,
            current_user.id,
            start_time,
            end_time,
            feedback_type,
            rec_id,
            None,
            notes,
        )

        if not feedback_id:
            raise HTTPException(status_code=500, detail="Failed to save feedback")

        return {
            "success": True,
            "feedback_id": str(feedback_id),
            "message": "Feedback saved. Thank you for helping improve ad detection!",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving ad feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to save feedback")
