import os
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.audio_utils import extract_mfcc
from app.config import MODEL_PATH

DATASET_DIR = BASE_DIR / "dataset"
HUMAN_DIR = DATASET_DIR / "human"
AI_DIR = DATASET_DIR / "ai"


def load_examples(folder: Path, label: int):
    examples = []
    skipped = []

    for audio_file in sorted(folder.glob("*.wav")):
        try:
            examples.append((extract_mfcc(str(audio_file)), label, audio_file.name))
        except Exception as exc:
            skipped.append((audio_file.name, str(exc)))

    return examples, skipped


def main():
    if not HUMAN_DIR.exists() or not AI_DIR.exists():
        raise SystemExit(
            "Missing dataset folders. Expected dataset/human and dataset/ai."
        )

    human_examples, human_skipped = load_examples(HUMAN_DIR, 0)
    ai_examples, ai_skipped = load_examples(AI_DIR, 1)
    examples = human_examples + ai_examples

    if len(human_examples) < 5 or len(ai_examples) < 5:
        raise SystemExit(
            "Not enough training data.\n"
            f"Found {len(human_examples)} human WAV files and {len(ai_examples)} AI WAV files.\n"
            "Add at least 5 WAV files in each folder, preferably 20+ each."
        )

    X = np.array([features for features, _, _ in examples])
    y = np.array([label for _, label, _ in examples])

    stratify = y if len(set(y)) == 2 and min(np.bincount(y)) >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=stratify,
    )

    model = RandomForestClassifier(
        n_estimators=250,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=["HUMAN", "AI"]))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Model trained and saved to {MODEL_PATH}")

    skipped = human_skipped + ai_skipped
    if skipped:
        print("\nSkipped files:")
        for filename, reason in skipped:
            print(f"- {filename}: {reason}")


if __name__ == "__main__":
    main()
