"""
Audio Transcription Service
Integrates with OpenAI Whisper API for speech-to-text conversion
Also supports local Whisper model (if installed)
"""
import logging
import os
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class TranscriptionEngine(str, Enum):
    """Transcription engine options"""
    OPENAI_WHISPER = "openai_whisper"
    LOCAL_WHISPER = "local_whisper"


@dataclass
class TranscriptionResult:
    """Transcription result"""
    text: str
    language: str
    duration_seconds: float
    confidence: float
    segments: list  # List of {start, end, text}
    engine: TranscriptionEngine
    processing_time_seconds: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "text": self.text,
            "language": self.language,
            "duration_seconds": self.duration_seconds,
            "confidence": self.confidence,
            "segments": self.segments,
            "engine": self.engine.value,
            "processing_time_seconds": self.processing_time_seconds,
        }


class TranscriptionService:
    """Service for audio transcription"""

    def __init__(self, api_key: Optional[str] = None, engine: TranscriptionEngine = TranscriptionEngine.LOCAL_WHISPER):
        self.api_key = api_key
        self.engine = engine
        self.openai_client = None

        if api_key and engine == TranscriptionEngine.OPENAI_WHISPER:
            try:
                import openai
                openai.api_key = api_key
                self.openai_client = openai
                logger.info("OpenAI Whisper initialized")
            except ImportError:
                logger.warning("OpenAI package not found")

    async def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None,
        engine: Optional[TranscriptionEngine] = None,
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe an audio file

        Args:
            file_path: Path to audio file
            language: Optional language code (e.g., 'en', 'ko')
            engine: Transcription engine to use

        Returns:
            TranscriptionResult or None if failed
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None

            engine = engine or self.engine

            start_time = datetime.utcnow()

            if engine == TranscriptionEngine.OPENAI_WHISPER:
                result = await self._transcribe_openai(file_path, language)
            else:
                result = await self._transcribe_local(file_path, language)

            if result:
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                result.processing_time_seconds = elapsed
                logger.info(f"Transcription completed: {file_path}")
                return result
            else:
                logger.error(f"Transcription failed: {file_path}")
                return None

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

    async def _transcribe_openai(
        self,
        file_path: str,
        language: Optional[str] = None,
    ) -> Optional[TranscriptionResult]:
        """Transcribe using OpenAI Whisper API"""
        try:
            if not self.openai_client or not self.api_key:
                logger.error("OpenAI Whisper not configured")
                return None

            # Read audio file
            with open(file_path, "rb") as f:
                audio_data = f.read()

            # Call Whisper API
            transcript = await asyncio.to_thread(
                lambda: self.openai_client.Audio.transcribe(
                    model="whisper-1",
                    file=open(file_path, "rb"),
                    language=language,
                    response_format="verbose_json",
                )
            )

            # Extract results
            text = transcript.get("text", "")
            detected_language = transcript.get("language", language or "unknown")
            segments = transcript.get("segments", [])

            # Convert segments
            formatted_segments = [
                {
                    "start": seg.get("start", 0),
                    "end": seg.get("end", 0),
                    "text": seg.get("text", ""),
                }
                for seg in segments
            ]

            return TranscriptionResult(
                text=text,
                language=detected_language,
                duration_seconds=transcript.get("duration", 0),
                confidence=0.95,  # OpenAI doesn't provide confidence scores
                segments=formatted_segments,
                engine=TranscriptionEngine.OPENAI_WHISPER,
                processing_time_seconds=0,
            )

        except Exception as e:
            logger.error(f"OpenAI transcription error: {e}")
            return None

    async def _transcribe_local(
        self,
        file_path: str,
        language: Optional[str] = None,
    ) -> Optional[TranscriptionResult]:
        """Transcribe using local Whisper model"""
        try:
            import whisper

            # Load model (small model by default)
            model = await asyncio.to_thread(lambda: whisper.load_model("base"))

            # Transcribe
            result = await asyncio.to_thread(
                lambda: model.transcribe(
                    file_path,
                    language=language,
                    verbose=False,
                )
            )

            # Extract results
            text = result.get("text", "")
            detected_language = result.get("language", language or "unknown")
            segments = result.get("segments", [])

            # Convert segments
            formatted_segments = [
                {
                    "start": seg.get("start", 0),
                    "end": seg.get("end", 0),
                    "text": seg.get("text", ""),
                }
                for seg in segments
            ]

            return TranscriptionResult(
                text=text,
                language=detected_language,
                duration_seconds=result.get("duration", 0),
                confidence=0.90,  # Estimate
                segments=formatted_segments,
                engine=TranscriptionEngine.LOCAL_WHISPER,
                processing_time_seconds=0,
            )

        except ImportError:
            logger.error("Whisper not installed. Install with: pip install openai-whisper")
            return None
        except Exception as e:
            logger.error(f"Local transcription error: {e}")
            return None

    def supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        return {
            "en": "English",
            "ko": "Korean",
            "ja": "Japanese",
            "zh": "Chinese",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "ru": "Russian",
            "pt": "Portuguese",
            "it": "Italian",
            "nl": "Dutch",
            "tr": "Turkish",
            "pl": "Polish",
            "ar": "Arabic",
            "hi": "Hindi",
        }


# Global instance
transcription_service = TranscriptionService()
