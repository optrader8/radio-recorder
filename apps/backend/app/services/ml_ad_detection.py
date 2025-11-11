"""
ML-based Ad Detection Service
Uses machine learning to detect advertisements with higher accuracy
"""
import logging
import os
import pickle
from typing import Optional, List, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AdPrediction:
    """AD detection prediction"""
    start_time: float  # seconds
    end_time: float  # seconds
    probability: float  # 0.0 to 1.0
    confidence: float  # Overall confidence
    features: dict  # Feature values used for prediction


class MLAdDetectionService:
    """ML-based advertisement detection service"""

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.scaler = None
        self.model_path = model_path
        self.is_trained = False

        if model_path and os.path.exists(model_path):
            self._load_model(model_path)

    def _load_model(self, model_path: str) -> None:
        """Load pre-trained model"""
        try:
            with open(model_path, "rb") as f:
                model_data = pickle.load(f)
                self.model = model_data.get("model")
                self.scaler = model_data.get("scaler")
                self.is_trained = True
                logger.info(f"Loaded ML model from {model_path}")
        except Exception as e:
            logger.warning(f"Failed to load model: {e}")

    async def detect_ads(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        threshold: float = 0.6,
    ) -> List[AdPrediction]:
        """
        Detect advertisements using ML model

        Args:
            audio_data: Audio samples
            sample_rate: Sample rate in Hz
            threshold: Confidence threshold (0.0-1.0)

        Returns:
            List of detected ad segments
        """
        try:
            import librosa

            # Extract features
            features_list = []
            frame_length = 2048
            hop_length = 512

            for i in range(0, len(audio_data) - frame_length, hop_length):
                frame = audio_data[i : i + frame_length]
                features = self._extract_features(frame, sample_rate)
                features_list.append(features)

            if not features_list:
                return []

            # Convert to numpy array
            X = np.array(features_list)

            # Scale features if scaler available
            if self.scaler:
                X = self.scaler.transform(X)

            # Get predictions
            predictions = []
            if self.model and self.is_trained:
                probs = self.model.predict_proba(X)[:, 1]  # Probability of ad class
            else:
                # Fallback to simple heuristic
                probs = await self._heuristic_detection(X)

            # Group consecutive predictions
            ad_segments = self._group_predictions(
                probs,
                sample_rate,
                hop_length,
                threshold,
            )

            return ad_segments

        except Exception as e:
            logger.error(f"ML ad detection error: {e}")
            return []

    def _extract_features(self, audio_frame: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract features from audio frame"""
        try:
            import librosa

            features = []

            # Time domain features
            rms_energy = np.sqrt(np.mean(audio_frame**2))
            features.append(rms_energy)

            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio_frame))
            features.append(zero_crossing_rate)

            # Spectral features
            S = np.abs(librosa.stft(audio_frame))
            spectral_centroid = librosa.feature.spectral_centroid(S=S)[0]
            features.append(np.mean(spectral_centroid))

            spectral_bandwidth = librosa.feature.spectral_bandwidth(S=S)[0]
            features.append(np.mean(spectral_bandwidth))

            # MFCCs (Mel-frequency cepstral coefficients)
            mfccs = librosa.feature.mfcc(y=audio_frame, sr=sample_rate, n_mfcc=13)
            features.extend(np.mean(mfccs, axis=1))

            # Spectral rolloff
            rolloff = librosa.feature.spectral_rolloff(S=S)[0]
            features.append(np.mean(rolloff))

            return np.array(features)

        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return np.zeros(20)

    async def _heuristic_detection(self, features: np.ndarray) -> np.ndarray:
        """Fallback heuristic detection when model not available"""
        try:
            # Simple heuristic: ads often have different spectral characteristics
            # RMS energy (features[:, 0]) and spectral centroid (features[:, 2])
            rms_scores = (features[:, 0] - np.mean(features[:, 0])) / (np.std(features[:, 0]) + 1e-10)
            centroid_scores = (features[:, 2] - np.mean(features[:, 2])) / (np.std(features[:, 2]) + 1e-10)

            # Combine scores
            combined = np.abs(rms_scores) + np.abs(centroid_scores)
            probs = 1.0 / (1.0 + np.exp(-combined))  # Sigmoid normalization

            return probs

        except Exception as e:
            logger.error(f"Heuristic detection error: {e}")
            return np.zeros(len(features))

    def _group_predictions(
        self,
        predictions: np.ndarray,
        sample_rate: int,
        hop_length: int,
        threshold: float,
    ) -> List[AdPrediction]:
        """Group consecutive predictions into segments"""
        ad_segments = []

        in_ad = False
        ad_start_idx = 0
        ad_probs = []

        for idx, prob in enumerate(predictions):
            if prob >= threshold:
                if not in_ad:
                    ad_start_idx = idx
                    in_ad = True
                    ad_probs = []
                ad_probs.append(prob)
            else:
                if in_ad:
                    # End of ad segment
                    start_time = (ad_start_idx * hop_length) / sample_rate
                    end_time = (idx * hop_length) / sample_rate
                    avg_prob = np.mean(ad_probs)
                    confidence = min(1.0, avg_prob)

                    # Only keep segments of reasonable duration (0.5-60 seconds)
                    duration = end_time - start_time
                    if 0.5 < duration < 60:
                        ad_segments.append(
                            AdPrediction(
                                start_time=start_time,
                                end_time=end_time,
                                probability=avg_prob,
                                confidence=confidence,
                                features={"duration": duration},
                            )
                        )

                    in_ad = False

        # Handle case where audio ends during ad
        if in_ad:
            start_time = (ad_start_idx * hop_length) / sample_rate
            end_time = (len(predictions) * hop_length) / sample_rate
            avg_prob = np.mean(ad_probs)

            duration = end_time - start_time
            if 0.5 < duration < 60:
                ad_segments.append(
                    AdPrediction(
                        start_time=start_time,
                        end_time=end_time,
                        probability=avg_prob,
                        confidence=min(1.0, avg_prob),
                        features={"duration": duration},
                    )
                )

        return ad_segments

    def train_model(
        self,
        training_data: List[Tuple[np.ndarray, int]],
        output_path: str,
    ) -> bool:
        """
        Train ML model on labeled data

        Args:
            training_data: List of (audio_array, is_ad_flag) tuples
            output_path: Path to save model

        Returns:
            True if training successful
        """
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import StandardScaler

            if not training_data:
                logger.error("No training data provided")
                return False

            logger.info(f"Training ML model with {len(training_data)} samples")

            # Extract features from all training samples
            X_list = []
            y_list = []

            for audio_frame, is_ad in training_data:
                if len(audio_frame) >= 2048:
                    features = self._extract_features(audio_frame, 44100)
                    X_list.append(features)
                    y_list.append(is_ad)

            if not X_list:
                logger.error("Failed to extract features from training data")
                return False

            X = np.array(X_list)
            y = np.array(y_list)

            # Normalize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Train model
            model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
            model.fit(X_scaled, y)

            # Save model
            model_data = {"model": model, "scaler": scaler}
            with open(output_path, "wb") as f:
                pickle.dump(model_data, f)

            self.model = model
            self.scaler = scaler
            self.is_trained = True
            self.model_path = output_path

            logger.info(f"Model trained and saved to {output_path}")
            return True

        except ImportError:
            logger.error("scikit-learn not installed")
            return False
        except Exception as e:
            logger.error(f"Model training error: {e}")
            return False


# Global instance
ml_ad_detection = MLAdDetectionService()
