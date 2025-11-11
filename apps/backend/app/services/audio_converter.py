"""
Audio format conversion service
Supports conversion between multiple audio formats using FFmpeg
"""
import logging
import subprocess
import os
from typing import Optional, List
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioFormat(str, Enum):
    """Supported audio formats"""
    MP3 = "mp3"
    AAC = "aac"
    OGG = "ogg"
    WAV = "wav"
    FLAC = "flac"
    M4A = "m4a"


class AudioCodec(str, Enum):
    """Audio codecs"""
    LIBMP3LAME = "libmp3lame"
    AAC = "aac"
    LIBVORBIS = "libvorbis"
    PCM_S16LE = "pcm_s16le"
    FLAC = "flac"


@dataclass
class AudioQuality:
    """Audio quality configuration"""
    bitrate: int  # kbps
    sample_rate: int  # Hz
    channels: int  # 1 (mono) or 2 (stereo)

    def __str__(self) -> str:
        return f"{self.bitrate}kbps_{self.sample_rate}hz_{self.channels}ch"


class AudioConverter:
    """Audio format converter using FFmpeg"""

    def __init__(self):
        self.ffmpeg_path = "ffmpeg"
        self.ffprobe_path = "ffprobe"
        self._verify_tools()

    def _verify_tools(self) -> None:
        """Verify FFmpeg and FFprobe are installed"""
        try:
            subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                timeout=5,
                check=True,
            )
            logger.info("FFmpeg found and verified")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("FFmpeg not found or not working properly")

    async def convert_file(
        self,
        input_file: str,
        output_file: str,
        target_format: AudioFormat,
        quality: Optional[AudioQuality] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Convert audio file to target format

        Args:
            input_file: Path to input audio file
            output_file: Path to output audio file
            target_format: Target audio format
            quality: Quality settings (bitrate, sample_rate, channels)
            metadata: Metadata to embed (title, artist, etc.)

        Returns:
            True if conversion successful, False otherwise
        """
        try:
            if not os.path.exists(input_file):
                logger.error(f"Input file not found: {input_file}")
                return False

            # Default quality settings
            if quality is None:
                quality = AudioQuality(bitrate=128, sample_rate=44100, channels=2)

            # Build FFmpeg command
            cmd = self._build_convert_command(
                input_file, output_file, target_format, quality, metadata
            )

            logger.info(f"Converting {input_file} to {target_format.value}")
            logger.debug(f"FFmpeg command: {' '.join(cmd)}")

            # Run conversion
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=3600,  # 1 hour timeout
                text=True,
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                return False

            if not os.path.exists(output_file):
                logger.error("Output file was not created")
                return False

            file_size = os.path.getsize(output_file)
            logger.info(f"Conversion successful: {output_file} ({file_size} bytes)")
            return True

        except subprocess.TimeoutExpired:
            logger.error("Conversion timeout")
            return False
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return False

    def _build_convert_command(
        self,
        input_file: str,
        output_file: str,
        target_format: AudioFormat,
        quality: AudioQuality,
        metadata: Optional[dict] = None,
    ) -> List[str]:
        """Build FFmpeg command for conversion"""
        cmd = [self.ffmpeg_path, "-i", input_file]

        # Audio codec selection
        codec_map = {
            AudioFormat.MP3: AudioCodec.LIBMP3LAME,
            AudioFormat.AAC: AudioCodec.AAC,
            AudioFormat.OGG: AudioCodec.LIBVORBIS,
            AudioFormat.WAV: AudioCodec.PCM_S16LE,
            AudioFormat.FLAC: AudioCodec.FLAC,
            AudioFormat.M4A: AudioCodec.AAC,
        }

        codec = codec_map.get(target_format, AudioCodec.LIBMP3LAME)
        cmd.extend(["-c:a", codec.value])

        # Audio quality
        if target_format != AudioFormat.FLAC:  # FLAC doesn't use bitrate the same way
            cmd.extend(["-b:a", f"{quality.bitrate}k"])

        cmd.extend(["-ar", str(quality.sample_rate)])
        cmd.extend(["-ac", str(quality.channels)])

        # Metadata
        if metadata:
            for key, value in metadata.items():
                cmd.extend(["-metadata", f"{key}={value}"])

        # Output options
        cmd.extend(["-y", output_file])  # -y for overwrite

        return cmd

    async def get_audio_info(self, file_path: str) -> Optional[dict]:
        """Get audio file information"""
        try:
            if not os.path.exists(file_path):
                return None

            cmd = [
                self.ffprobe_path,
                "-v", "error",
                "-select_streams", "a:0",
                "-show_entries", "stream=codec_type,duration,sample_rate,channels",
                "-of", "default=noprint_wrappers=1:nokey=1:noinout_type=1",
                file_path,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=10,
                text=True,
            )

            if result.returncode != 0:
                logger.error(f"FFprobe failed: {result.stderr}")
                return None

            lines = result.stdout.strip().split('\n')
            if len(lines) < 3:
                return None

            return {
                "duration": float(lines[0]),
                "sample_rate": int(lines[1]),
                "channels": int(lines[2]),
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
            }

        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return None

    async def batch_convert(
        self,
        input_dir: str,
        output_dir: str,
        target_format: AudioFormat,
        quality: Optional[AudioQuality] = None,
        pattern: str = "*.mp3",
    ) -> dict:
        """
        Batch convert audio files in a directory

        Args:
            input_dir: Input directory
            output_dir: Output directory
            target_format: Target format
            quality: Quality settings
            pattern: File pattern to match (e.g., "*.mp3")

        Returns:
            Conversion results dictionary
        """
        try:
            input_path = Path(input_dir)
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            files = list(input_path.glob(pattern))
            results = {
                "total": len(files),
                "successful": 0,
                "failed": 0,
                "files": [],
            }

            for input_file in files:
                output_file = output_path / f"{input_file.stem}.{target_format.value}"

                success = await self.convert_file(
                    str(input_file),
                    str(output_file),
                    target_format,
                    quality,
                )

                results["files"].append({
                    "input": str(input_file),
                    "output": str(output_file),
                    "success": success,
                })

                if success:
                    results["successful"] += 1
                else:
                    results["failed"] += 1

            logger.info(
                f"Batch conversion: {results['successful']}/{results['total']} successful"
            )
            return results

        except Exception as e:
            logger.error(f"Batch conversion error: {e}")
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "files": [],
                "error": str(e),
            }

    @staticmethod
    def get_format_extension(format: AudioFormat) -> str:
        """Get file extension for format"""
        extensions = {
            AudioFormat.MP3: "mp3",
            AudioFormat.AAC: "aac",
            AudioFormat.OGG: "ogg",
            AudioFormat.WAV: "wav",
            AudioFormat.FLAC: "flac",
            AudioFormat.M4A: "m4a",
        }
        return extensions.get(format, "mp3")

    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported formats"""
        return [f.value for f in AudioFormat]


# Global instance
audio_converter = AudioConverter()
