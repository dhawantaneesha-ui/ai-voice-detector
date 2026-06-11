import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from app.audio_utils import extract_mfcc

# -----------------------------
# Get PROJECT ROOT directory
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data paths
HUMAN_DIR = os.path.join(BASE_DIR, "data", "human")
AI_DIR = os.path.join(BASE_DIR, "data", "ai")

X = []  # features 
y = []  # labels

# -----------------------------
# Load HUMAN voice samples
# -----------------------------
for file in os.listdir(HUMAN_DIR):
    if file.endswith(".wav"):
        file_path = os.path.join(HUMAN_DIR, file)
        mfcc = extract_mfcc(file_path)
        X.append(mfcc)
        y.append(0)  # 0 = Human

# -----------------------------
# Load AI voice samples
# -----------------------------
for file in os.listdir(AI_DIR):
    if file.endswith(".wav"):
        file_path = os.path.join(AI_DIR, file)
        mfcc = extract_mfcc(file_path)
        X.append(mfcc)
        y.append(1)  # 1 = AI

# -----------------------------
# Train Model
# -----------------------------
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

# -----------------------------
# Save Model
# -----------------------------
MODEL_PATH = os.path.join(BASE_DIR, "models", "voice_detector.pkl")
joblib.dump(model, MODEL_PATH)

print("✅ Model trained and saved successfully!")
