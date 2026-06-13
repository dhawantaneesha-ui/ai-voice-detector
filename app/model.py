"""
Handles ML model loading and prediction.
Phase 1: structured, confidence-calibrated, explainable output
"""

import numpy as np
from joblib import load
import librosa

from app.config import MODEL_PATH, SAMPLE_RATE
from app.audio_utils import extract_mfcc, detect_language

# --------------------------------------------------
# Constants
# --------------------------------------------------
MODEL_NAME = "ML Classifier + MFCC"

# --------------------------------------------------
# Load model ONCE
# --------------------------------------------------
model = load(MODEL_PATH)

# --------------------------------------------------
# Confidence Threshold Logic
# --------------------------------------------------

def apply_threshold(ai_prob: float, human_prob: float):
    """
    Label decision + calibrated confidence
    """
    margin = abs(ai_prob - human_prob)

    if ai_prob >= 0.85:
        label = "AI"
    elif ai_prob <= 0.40:
        label = "HUMAN"
    else:
        label = "UNCERTAIN"

    # Calibrated confidence (never 100%)
    confidence = min(round(margin * 100, 2), 95)

    return label, confidence

# --------------------------------------------------
# Explainability Logic
# --------------------------------------------------
def explain_decision(raw_score: float, mfcc_features: np.ndarray):
    """
    Explain model decision using confidence zones + signal behavior
    """
    variance = float(np.var(mfcc_features))

    explanation = {
        "confidence_zone": "",
        "signal_stability": "",
        "reasoning": []
    }

    # Confidence reasoning
    if raw_score >= 0.75:
        explanation["confidence_zone"] = "high-confidence"
        explanation["reasoning"].append(
            "Classifier shows strong confidence for AI-generated voice"
        )
    elif raw_score <= 0.45:
        explanation["confidence_zone"] = "high-confidence"
        explanation["reasoning"].append(
            "Classifier shows strong confidence for human voice"
        )
    else:
        explanation["confidence_zone"] = "uncertain-zone"
        explanation["reasoning"].append(
            "Prediction lies in calibrated uncertainty region"
        )

    # Signal behavior
    if variance < 5:
        explanation["signal_stability"] = "stable"
        explanation["reasoning"].append(
            "Low MFCC variance indicates consistent spectral patterns"
        )
    else:
        explanation["signal_stability"] = "unstable"
        explanation["reasoning"].append(
            "High MFCC variance indicates natural speech variability"
        )

    return explanation


# --------------------------------------------------
# Main Prediction Function
# --------------------------------------------------
def predict_voice(file_path: str):
    """
    Predict AI vs Human with explainability + visualization
    """

    # ---- Feature Extraction ----
    mfcc_features = extract_mfcc(file_path)
    features = mfcc_features.reshape(1, -1)

    # ---- Model Prediction ----
    proba = model.predict_proba(features)[0]

    human_prob = float(proba[0])
    ai_prob = float(proba[1])

    raw_score = ai_prob

    label, confidence = apply_threshold(ai_prob, human_prob)

    # ---- Explainability ----
    explanation = explain_decision(raw_score, mfcc_features)

    # ---- Confidence Visualization ----
    max_prob = max(human_prob, ai_prob)

    if max_prob >= 0.75:
        verdict_strength = "strong"
    elif max_prob >= 0.55:
        verdict_strength = "moderate"
    else:
        verdict_strength = "weak"

    confidence_visualization = {
        "type": "confidence-levels",
        "human_level": int(human_prob * 100),
        "ai_level": int(ai_prob * 100),
        "verdict_strength": verdict_strength
    }

    # ---- Audio Metadata ----
    audio, sr = librosa.load(file_path, sr=SAMPLE_RATE)
    duration = len(audio) / sr

    # ---- Language Detection ----
    lang_code, lang_name = detect_language(file_path)

    return {
        "label": label,
        "confidence": round(confidence, 2),
        "raw_score": round(raw_score, 2),
        "probability_breakdown": {
            "AI": round(ai_prob, 2),
            "HUMAN": round(human_prob, 2)
        },
        "model_name": MODEL_NAME,
        "audio_duration": round(duration, 2),
        "sample_rate": SAMPLE_RATE,
        "language": lang_name,
        "language_code": lang_code,
        "explainability": explanation,
        "confidence_visualization": confidence_visualization
    }
