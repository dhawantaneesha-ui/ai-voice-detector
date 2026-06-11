"""
Central configuration file.
Keeps all constants in one place.
"""

import os

# ================= PATH CONFIG =================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "models", "voice_model.joblib")

# ================= AUDIO FEATURE CONFIG =================

# Number of MFCC features (must match training)
N_MFCC = 40

# Audio duration control (seconds)
MIN_AUDIO_DURATION = 3.0
MAX_DURATION = 5.0

SAMPLE_RATE = 16000

# ================= MODEL CONFIG =================

# Whisper model size (if used later)
WHISPER_MODEL = "tiny"

# ================= LANGUAGE CONFIG =================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "fr": "French"
}
