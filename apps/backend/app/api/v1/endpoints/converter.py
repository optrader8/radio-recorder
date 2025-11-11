"""
Audio format conversion endpoints
"""
import logging
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
import asyncio

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.services.audio_converter import audio_converter, AudioFormat, AudioQuality
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/converter/formats")
async def get_supported_formats(
    current_user: User = Depends(get_current_active_user),
):
    """Get list of supported audio formats"""
    return {
        "formats": audio_converter.get_supported_formats(),
        "details": {
            "mp3": {"description": "MPEG Layer III Audio", "extension": "mp3"},
            "aac": {"description": "Advanced Audio Coding", "extension": "aac"},
            "ogg": {"description": "Ogg Vorbis", "extension": "ogg"},
            "wav": {"description": "Waveform Audio File Format", "extension": "wav"},
            "flac": {"description": "Free Lossless Audio Codec", "extension": "flac"},
            "m4a": {"description": "MPEG-4 Audio", "extension": "m4a"},
        },
    }


@router.post("/converter/convert")
async def convert_audio(
    file: UploadFile = File(...),
    target_format: str = Form(...),
    bitrate: int = Form(128),
    sample_rate: int = Form(44100),
    channels: int = Form(2),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Convert audio file to target format

    Parameters:
    - file: Audio file to convert
    - target_format: Target format (mp3, aac, ogg, wav, flac, m4a)
    - bitrate: Audio bitrate in kbps (64-320)
    - sample_rate: Sample rate in Hz (8000, 16000, 44100, 48000)
    - channels: Number of channels (1=mono, 2=stereo)
    """
    temp_file = None
    output_file = None

    try:
        # Validate format
        try:
            fmt = AudioFormat(target_format)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {target_format}"
            )

        # Validate quality parameters
        if not (64 <= bitrate <= 320):
            raise HTTPException(status_code=400, detail="Bitrate must be 64-320 kbps")

        if sample_rate not in [8000, 16000, 44100, 48000]:
            raise HTTPException(status_code=400, detail="Invalid sample rate")

        if channels not in [1, 2]:
            raise HTTPException(status_code=400, detail="Channels must be 1 or 2")

        # Save uploaded file temporarily
        temp_dir = os.path.join(settings.STORAGE_PATH, "temp")
        os.makedirs(temp_dir, exist_ok=True)

        temp_file = os.path.join(temp_dir, f"{uuid4()}_{file.filename}")

        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"Uploaded file: {temp_file} ({len(content)} bytes)")

        # Create output file path
        base_name = os.path.splitext(os.path.basename(file.filename))[0]
        output_file = os.path.join(
            settings.STORAGE_PATH,
            f"{base_name}_converted_{uuid4()}.{target_format}"
        )

        # Create quality settings
        quality = AudioQuality(
            bitrate=bitrate,
            sample_rate=sample_rate,
            channels=channels
        )

        # Convert file
        success = await audio_converter.convert_file(
            temp_file,
            output_file,
            fmt,
            quality,
            metadata={
                "title": base_name,
                "artist": current_user.username,
            }
        )

        if not success:
            raise HTTPException(status_code=500, detail="Conversion failed")

        # Get file info
        file_size = os.path.getsize(output_file)
        audio_info = await audio_converter.get_audio_info(output_file)

        logger.info(f"Conversion successful: {output_file}")

        return {
            "success": True,
            "file": {
                "path": output_file,
                "name": os.path.basename(output_file),
                "format": target_format,
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
            },
            "audio_info": audio_info,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")

    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")


@router.post("/converter/batch-convert")
async def batch_convert_audio(
    input_pattern: str = Form("*.mp3"),
    target_format: str = Form(...),
    bitrate: int = Form(128),
    sample_rate: int = Form(44100),
    channels: int = Form(2),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Batch convert audio files in storage directory

    Parameters:
    - input_pattern: File pattern to match (e.g., "*.mp3", "*.wav")
    - target_format: Target format
    - bitrate: Audio bitrate in kbps
    - sample_rate: Sample rate in Hz
    - channels: Number of channels
    """
    try:
        # Validate format
        try:
            fmt = AudioFormat(target_format)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {target_format}"
            )

        # Validate quality parameters
        if not (64 <= bitrate <= 320):
            raise HTTPException(status_code=400, detail="Bitrate must be 64-320 kbps")

        quality = AudioQuality(
            bitrate=bitrate,
            sample_rate=sample_rate,
            channels=channels
        )

        # Create output directory
        output_dir = os.path.join(
            settings.STORAGE_PATH,
            f"converted_{uuid4()}"
        )

        # Run batch conversion
        results = await audio_converter.batch_convert(
            settings.STORAGE_PATH,
            output_dir,
            fmt,
            quality,
            input_pattern
        )

        logger.info(f"Batch conversion results: {results}")

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch conversion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/converter/audio-info/{filename}")
async def get_audio_info(
    filename: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get audio file information"""
    try:
        file_path = os.path.join(settings.STORAGE_PATH, filename)

        # Security: prevent path traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(settings.STORAGE_PATH)):
            raise HTTPException(status_code=403, detail="Access denied")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        info = await audio_converter.get_audio_info(file_path)

        if not info:
            raise HTTPException(status_code=400, detail="Could not read audio file info")

        return {
            "file": filename,
            "audio_info": info,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audio info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get audio info")
