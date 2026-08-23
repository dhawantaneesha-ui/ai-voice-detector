import json
import time
from functools import lru_cache
from pathlib import Path

import librosa
import numpy as np
import torch

from app.config import MIN_AUDIO_DURATION
from third_party.aasist.AASIST import Model as AASISTModel


BASE_DIR = Path(__file__).resolve().parents[1]

AASIST_DIR = BASE_DIR / "third_party" / "aasist"
CONFIG_PATH = AASIST_DIR / "AASIST-L.conf"
WEIGHTS_PATH = AASIST_DIR / "AASIST-L.pth"

TARGET_SAMPLE_RATE = 16000
TARGET_NUM_SAMPLES = 64600

SPOOF_THRESHOLD = 0.80
BONAFIDE_THRESHOLD = 0.20


def pad_audio(
    audio: np.ndarray,
    max_len: int = TARGET_NUM_SAMPLES,
) -> np.ndarray:
    """
    Match the deterministic AASIST evaluation preprocessing.

    Long audio is truncated.
    Short audio is repeated until the required input length.
    """

    audio = np.asarray(audio, dtype=np.float32).reshape(-1)

    if audio.size == 0:
        raise ValueError("Audio contains no samples")

    if audio.size >= max_len:
        return audio[:max_len]

    repeats = (max_len // audio.size) + 1

    return np.tile(audio, repeats)[:max_len]


def verdict_from_spoof_probability(
    spoof_probability: float,
) -> str:
    """
    Conservative provisional thresholds.

    These thresholds will later be calibrated on development data
    and frozen before held-out evaluation.
    """

    if not 0.0 <= spoof_probability <= 1.0:
        raise ValueError("Spoof probability must be between 0 and 1")

    if spoof_probability >= SPOOF_THRESHOLD:
        return "AI"

    if spoof_probability <= BONAFIDE_THRESHOLD:
        return "HUMAN"

    return "UNCERTAIN"


@lru_cache(maxsize=1)
def load_aasist_model():
    """
    Load AASIST-L once per application process.
    """

    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    model = AASISTModel(config["model_config"])

    state_dict = torch.load(
        WEIGHTS_PATH,
        map_location="cpu",
        weights_only=True,
    )

    model.load_state_dict(state_dict)
    model.eval()

    return model


def predict_aasist(file_path: str) -> dict:
    """
    Run AASIST-L anti-spoof inference.

    Official model class 0 = spoof, class 1 = bonafide.
    """

    audio, _ = librosa.load(
        file_path,
        sr=TARGET_SAMPLE_RATE,
        mono=True,
    )

    if audio.size == 0:
        raise ValueError("Audio contains no samples")

    duration = len(audio) / TARGET_SAMPLE_RATE
    model_input = pad_audio(audio)

    tensor = torch.tensor(
        model_input,
        dtype=torch.float32,
    ).unsqueeze(0)

    model = load_aasist_model()

    started = time.perf_counter()

    with torch.inference_mode():
        _, logits = model(tensor)
        probabilities = torch.softmax(logits, dim=1)[0]

    latency_ms = (time.perf_counter() - started) * 1000

    spoof_probability = float(probabilities[0].item())
    bonafide_probability = float(probabilities[1].item())

    label = verdict_from_spoof_probability(
        spoof_probability,
    )

    quality_warnings = []

    # For financial authorization we do not trust a strong
    # classification from an extremely short utterance.
    if duration < MIN_AUDIO_DURATION:
        quality_warnings.append("audio_too_short")
        label = "UNCERTAIN"

    decision_strength = abs(
        spoof_probability - bonafide_probability
    ) * 100

    return {
        "label": label,
        "raw_score": round(spoof_probability, 6),
        "confidence": round(decision_strength, 2),
        "confidence_kind": "decision_margin_not_calibrated",
        "probability_breakdown": {
            "AI": round(spoof_probability, 6),
            "HUMAN": round(bonafide_probability, 6),
        },
        "model_name": "AASIST-L",
        "model_role": "primary_anti_spoof",
        "audio_duration": round(duration, 3),
        "sample_rate": TARGET_SAMPLE_RATE,
        "inference_latency_ms": round(latency_ms, 2),
        "quality_warnings": quality_warnings,
    }
