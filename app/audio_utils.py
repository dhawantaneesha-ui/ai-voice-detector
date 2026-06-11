"""
Audio processing utilities.
Converts raw audio into ML-friendly features.
(Language detection disabled for stability)
"""

import librosa
import numpy as np

from app.config import (
    N_MFCC,
    MIN_AUDIO_DURATION
)


def load_audio(file_path: str):
    """
    Load audio file safely.
    """
    y, sr = librosa.load(file_path, sr=None)

    duration = librosa.get_duration(y=y, sr=sr)
    if duration < MIN_AUDIO_DURATION:
        raise ValueError("Audio too short for reliable analysis")

    return y, sr


def extract_mfcc(file_path: str) -> np.ndarray:
    """
    Extract MFCC features from audio.
    """
    y, sr = load_audio(file_path)

    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=N_MFCC
    )

    # Fixed-length vector
    return np.mean(mfcc.T, axis=0)


def detect_language(file_path: str):
    """
    Language detection disabled.
    Returned as unknown for now.
    """
    return "unknown", "Unknown"
