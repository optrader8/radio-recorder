"""
Audio Ad Detection Service

Detects advertisements in audio streams using signal processing techniques.
Methods:
1. Silence Detection - Identifies gaps/silence periods
2. Frequency Analysis - Analyzes audio frequency characteristics
3. Volume Envelope Analysis - Detects sudden volume changes
"""
import logging
import numpy as np
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class AdDetectionMethod(str, Enum):
    """Ad detection method enumeration"""
    SILENCE = "silence"
    FREQUENCY = "frequency"
    VOLUME = "volume"
    COMBINED = "combined"


@dataclass
class AdSegment:
    """Represents a detected ad segment"""
    start_time: float  # in seconds
    end_time: float  # in seconds
    confidence: float  # 0.0 to 1.0
    method: AdDetectionMethod
    details: Dict[str, Any]

    @property
    def duration(self) -> float:
        """Get duration of ad segment"""
        return self.end_time - self.start_time


class AdDetectionService:
    """Service for detecting advertisements in audio streams"""

    def __init__(
        self,
        silence_threshold_db: float = -40.0,
        silence_duration_min_seconds: float = 2.0,
        silence_duration_max_seconds: float = 20.0,
        volume_change_threshold_db: float = 10.0,
        confidence_threshold: float = 0.6,
    ):
        """
        Initialize ad detection service

        Args:
            silence_threshold_db: Volume threshold for silence detection (dB)
            silence_duration_min_seconds: Minimum silence duration to be considered (seconds)
            silence_duration_max_seconds: Maximum silence duration to be considered as ad (seconds)
            volume_change_threshold_db: Minimum volume change to detect ad boundary (dB)
            confidence_threshold: Minimum confidence score to report ad (0.0-1.0)
        """
        self.silence_threshold_db = silence_threshold_db
        self.silence_duration_min_seconds = silence_duration_min_seconds
        self.silence_duration_max_seconds = silence_duration_max_seconds
        self.volume_change_threshold_db = volume_change_threshold_db
        self.confidence_threshold = confidence_threshold

    def detect_silence_segments(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        frame_length: int = 2048,
        hop_length: int = 512,
    ) -> List[Tuple[float, float]]:
        """
        Detect silence segments in audio

        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate in Hz
            frame_length: Frame length for STFT
            hop_length: Hop length for STFT

        Returns:
            List of (start_time, end_time) tuples for silent segments
        """
        try:
            # Calculate RMS energy per frame
            energy = self._calculate_rms_energy(audio_data, frame_length, hop_length)

            # Convert energy to dB
            energy_db = 20 * np.log10(np.maximum(energy, 1e-10))

            # Find silent frames
            silent_frames = energy_db < self.silence_threshold_db

            # Convert frame indices to time
            frame_times = (np.arange(len(silent_frames)) * hop_length) / sample_rate

            # Group consecutive silent frames
            silence_segments = []
            in_silence = False
            silence_start = 0.0

            for i, is_silent in enumerate(silent_frames):
                if is_silent and not in_silence:
                    silence_start = frame_times[i]
                    in_silence = True
                elif not is_silent and in_silence:
                    silence_end = frame_times[i]
                    silence_duration = silence_end - silence_start

                    # Only keep silence segments within expected ad duration
                    if (
                        self.silence_duration_min_seconds
                        <= silence_duration
                        <= self.silence_duration_max_seconds
                    ):
                        silence_segments.append((silence_start, silence_end))

                    in_silence = False

            return silence_segments

        except Exception as e:
            logger.error(f"Error detecting silence segments: {e}")
            return []

    def detect_volume_changes(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        frame_length: int = 2048,
        hop_length: int = 512,
    ) -> List[Tuple[float, float]]:
        """
        Detect volume change boundaries (potential ad boundaries)

        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate in Hz
            frame_length: Frame length for STFT
            hop_length: Hop length for STFT

        Returns:
            List of (start_time, end_time) tuples for volume change regions
        """
        try:
            # Calculate RMS energy per frame
            energy = self._calculate_rms_energy(audio_data, frame_length, hop_length)

            # Convert energy to dB
            energy_db = 20 * np.log10(np.maximum(energy, 1e-10))

            # Calculate delta (change) in energy
            delta_energy = np.abs(np.diff(energy_db))

            # Find frames with significant volume changes
            high_change_frames = delta_energy > self.volume_change_threshold_db

            # Convert frame indices to time
            frame_times = (np.arange(len(high_change_frames)) * hop_length) / sample_rate

            # Group consecutive high change frames
            change_segments = []
            in_change = False
            change_start = 0.0

            for i, is_change in enumerate(high_change_frames):
                if is_change and not in_change:
                    change_start = frame_times[i]
                    in_change = True
                elif not is_change and in_change:
                    change_end = frame_times[i]
                    change_duration = change_end - change_start

                    # Only keep segments with reasonable duration
                    if 0.5 < change_duration < 30:
                        change_segments.append((change_start, change_end))

                    in_change = False

            return change_segments

        except Exception as e:
            logger.error(f"Error detecting volume changes: {e}")
            return []

    def detect_frequency_anomalies(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        frame_length: int = 2048,
        hop_length: int = 512,
        n_mels: int = 128,
    ) -> List[Tuple[float, float, Dict[str, Any]]]:
        """
        Detect frequency anomalies (ads often have different frequency characteristics)

        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate in Hz
            frame_length: Frame length for STFT
            hop_length: Hop length for STFT
            n_mels: Number of mel frequency bins

        Returns:
            List of (start_time, end_time, details) tuples for anomalies
        """
        try:
            import librosa

            # Compute mel-spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio_data,
                sr=sample_rate,
                n_fft=frame_length,
                hop_length=hop_length,
                n_mels=n_mels,
            )

            # Convert to dB
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

            # Calculate spectral centroid per frame
            spectral_centroid = librosa.feature.spectral_centroid(
                S=mel_spec, sr=sample_rate
            )[0]

            # Calculate spectral flatness per frame
            spectral_flatness = librosa.feature.spectral_flatness(S=mel_spec)[0]

            # Normalize metrics
            spectral_centroid_norm = (spectral_centroid - np.mean(spectral_centroid)) / (
                np.std(spectral_centroid) + 1e-10
            )
            spectral_flatness_norm = (
                spectral_flatness - np.mean(spectral_flatness)
            ) / (np.std(spectral_flatness) + 1e-10)

            # Detect anomalies (values beyond 1 std dev)
            anomaly_score = np.abs(spectral_centroid_norm) + np.abs(spectral_flatness_norm)
            anomaly_threshold = np.mean(anomaly_score) + np.std(anomaly_score)

            anomaly_frames = anomaly_score > anomaly_threshold

            # Convert frame indices to time
            frame_times = (np.arange(len(anomaly_frames)) * hop_length) / sample_rate

            # Group consecutive anomalies
            anomaly_segments = []
            in_anomaly = False
            anomaly_start = 0.0

            for i, is_anomaly in enumerate(anomaly_frames):
                if is_anomaly and not in_anomaly:
                    anomaly_start = frame_times[i]
                    in_anomaly = True
                elif not is_anomaly and in_anomaly:
                    anomaly_end = frame_times[i]
                    duration = anomaly_end - anomaly_start

                    if 1.0 < duration < 60:  # Reasonable ad duration
                        details = {
                            "spectral_centroid_mean": float(
                                np.mean(spectral_centroid[int(anomaly_start * sample_rate / hop_length) : int(anomaly_end * sample_rate / hop_length)])
                            ),
                            "spectral_flatness_mean": float(
                                np.mean(spectral_flatness[int(anomaly_start * sample_rate / hop_length) : int(anomaly_end * sample_rate / hop_length)])
                            ),
                        }
                        anomaly_segments.append((anomaly_start, anomaly_end, details))

                    in_anomaly = False

            return anomaly_segments

        except ImportError:
            logger.warning("librosa not available, skipping frequency analysis")
            return []
        except Exception as e:
            logger.error(f"Error detecting frequency anomalies: {e}")
            return []

    async def detect_ads(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        method: AdDetectionMethod = AdDetectionMethod.COMBINED,
    ) -> List[AdSegment]:
        """
        Detect advertisements in audio

        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate in Hz
            method: Detection method to use

        Returns:
            List of detected ad segments
        """
        try:
            ads = []

            if method in [AdDetectionMethod.SILENCE, AdDetectionMethod.COMBINED]:
                # Detect silence-based ads
                silence_segments = self.detect_silence_segments(audio_data, sample_rate)
                for start, end in silence_segments:
                    ads.append(
                        AdSegment(
                            start_time=start,
                            end_time=end,
                            confidence=0.8,
                            method=AdDetectionMethod.SILENCE,
                            details={"type": "silence"},
                        )
                    )

            if method in [AdDetectionMethod.VOLUME, AdDetectionMethod.COMBINED]:
                # Detect volume change-based ads
                change_segments = self.detect_volume_changes(audio_data, sample_rate)
                for start, end in change_segments:
                    ads.append(
                        AdSegment(
                            start_time=start,
                            end_time=end,
                            confidence=0.6,
                            method=AdDetectionMethod.VOLUME,
                            details={"type": "volume_change"},
                        )
                    )

            if method in [AdDetectionMethod.FREQUENCY, AdDetectionMethod.COMBINED]:
                # Detect frequency-based ads
                freq_anomalies = self.detect_frequency_anomalies(audio_data, sample_rate)
                for start, end, details in freq_anomalies:
                    ads.append(
                        AdSegment(
                            start_time=start,
                            end_time=end,
                            confidence=0.7,
                            method=AdDetectionMethod.FREQUENCY,
                            details=details,
                        )
                    )

            # Filter by confidence threshold
            ads = [ad for ad in ads if ad.confidence >= self.confidence_threshold]

            # Sort by start time
            ads.sort(key=lambda x: x.start_time)

            # Merge overlapping segments
            merged_ads = self._merge_overlapping_segments(ads)

            logger.info(f"Detected {len(merged_ads)} ad segments using {method.value} method")

            return merged_ads

        except Exception as e:
            logger.error(f"Error detecting ads: {e}")
            return []

    def _calculate_rms_energy(
        self,
        audio_data: np.ndarray,
        frame_length: int = 2048,
        hop_length: int = 512,
    ) -> np.ndarray:
        """Calculate RMS energy per frame"""
        energy = []
        for i in range(0, len(audio_data) - frame_length, hop_length):
            frame = audio_data[i : i + frame_length]
            rms = np.sqrt(np.mean(frame**2))
            energy.append(rms)
        return np.array(energy)

    @staticmethod
    def _merge_overlapping_segments(segments: List[AdSegment], overlap_threshold: float = 0.3) -> List[AdSegment]:
        """Merge overlapping ad segments"""
        if not segments:
            return []

        merged = [segments[0]]

        for current in segments[1:]:
            last = merged[-1]

            # Check if segments overlap
            if current.start_time < last.end_time:
                # Merge by extending the end time
                merged[-1] = AdSegment(
                    start_time=last.start_time,
                    end_time=max(last.end_time, current.end_time),
                    confidence=max(last.confidence, current.confidence),
                    method=last.method,
                    details={**last.details, **current.details},
                )
            else:
                merged.append(current)

        return merged


# Global instance
ad_detection_service = AdDetectionService()
