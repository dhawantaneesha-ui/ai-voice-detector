import argparse
import io
import json
import time
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import torch
from datasets import Audio, load_dataset
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from app.anti_spoof import load_aasist_model, pad_audio


DATASET_NAME = "SpeechAntiSpoofingBenchmarks/ASVspoof2019_LA"
THRESHOLD = 0.50
TARGET_SAMPLE_RATE = 16000


def decode_audio(audio_record):
    """
    Decode embedded FLAC bytes ourselves.

    This intentionally avoids Hugging Face Audio decoding,
    so torchcodec is not required.
    """
    audio_bytes = audio_record.get("bytes")

    if audio_bytes is None:
        raise RuntimeError(
            "Dataset row did not contain embedded audio bytes."
        )

    audio, sample_rate = sf.read(
        io.BytesIO(audio_bytes),
        dtype="float32",
    )

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    if sample_rate != TARGET_SAMPLE_RATE:
        audio = librosa.resample(
            audio,
            orig_sr=sample_rate,
            target_sr=TARGET_SAMPLE_RATE,
        )

    return np.asarray(audio, dtype=np.float32)


def predict_audio(model, audio):
    model_input = pad_audio(audio)

    tensor = torch.tensor(
        model_input,
        dtype=torch.float32,
    ).unsqueeze(0)

    started = time.perf_counter()

    with torch.inference_mode():
        _, logits = model(tensor)
        probabilities = torch.softmax(logits, dim=1)[0]

    latency_ms = (
        time.perf_counter() - started
    ) * 1000

    # Official AASIST output:
    # index 0 = spoof
    # index 1 = bonafide
    spoof_probability = float(
        probabilities[0].item()
    )

    return spoof_probability, latency_ms


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--per-class",
        type=int,
        default=100,
    )

    args = parser.parse_args()

    print(
        "Loading ASVspoof2019 LA official "
        "evaluation partition..."
    )

    dataset = load_dataset(
        DATASET_NAME,
        split="test",
        streaming=True,
    )

    # IMPORTANT:
    # Never let datasets decode audio itself.
    # That would require torchcodec.
    dataset = dataset.cast_column(
        "audio",
        Audio(decode=False),
    )

    model = load_aasist_model()

    y_true = []
    y_pred = []
    scores = []
    latencies = []

    counts = {
        0: 0,  # bonafide
        1: 0,  # spoof
    }

    scanned = 0

    for row in dataset:
        scanned += 1

        label = int(row["label"])

        if counts[label] >= args.per_class:
            continue

        audio = decode_audio(row["audio"])

        spoof_probability, latency_ms = (
            predict_audio(
                model,
                audio,
            )
        )

        prediction = int(
            spoof_probability >= THRESHOLD
        )

        y_true.append(label)
        y_pred.append(prediction)
        scores.append(spoof_probability)
        latencies.append(latency_ms)

        counts[label] += 1

        total = len(y_true)

        if total % 25 == 0:
            print(
                f"Evaluated {total} | "
                f"bonafide={counts[0]} "
                f"spoof={counts[1]} | "
                f"rows_scanned={scanned}"
            )

        if (
            counts[0] >= args.per_class
            and counts[1] >= args.per_class
        ):
            break

    if min(counts.values()) < args.per_class:
        raise RuntimeError(
            "Could not collect requested balanced "
            f"sample. Counts={counts}"
        )

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    ).ravel()

    false_positive_rate = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0.0
    )

    results = {
        "dataset": DATASET_NAME,
        "partition": "official_evaluation",
        "evaluation_type": (
            "balanced_sequential_held_out_sample"
        ),
        "threshold": THRESHOLD,
        "samples": len(y_true),
        "bonafide_samples": counts[0],
        "spoof_samples": counts[1],
        "rows_scanned": scanned,

        "precision": round(
            precision_score(
                y_true,
                y_pred,
                zero_division=0,
            ),
            6,
        ),

        "recall": round(
            recall_score(
                y_true,
                y_pred,
                zero_division=0,
            ),
            6,
        ),

        "f1": round(
            f1_score(
                y_true,
                y_pred,
                zero_division=0,
            ),
            6,
        ),

        "accuracy": round(
            accuracy_score(
                y_true,
                y_pred,
            ),
            6,
        ),

        "false_positive_rate": round(
            false_positive_rate,
            6,
        ),

        "false_challenges_per_1000_genuine": (
            round(
                false_positive_rate * 1000,
                2,
            )
        ),

        "confusion_matrix": {
            "true_bonafide_pred_bonafide": int(tn),
            "true_bonafide_pred_spoof": int(fp),
            "true_spoof_pred_bonafide": int(fn),
            "true_spoof_pred_spoof": int(tp),
        },

        "latency_ms": {
            "mean": round(
                float(np.mean(latencies)),
                2,
            ),
            "p95": round(
                float(
                    np.percentile(
                        latencies,
                        95,
                    )
                ),
                2,
            ),
        },

        "score_summary": {
            "mean": round(
                float(np.mean(scores)),
                6,
            ),
            "min": round(
                float(np.min(scores)),
                6,
            ),
            "max": round(
                float(np.max(scores)),
                6,
            ),
        },
    }

    Path("reports").mkdir(
        exist_ok=True,
    )

    output_path = Path(
        f"reports/aasist_eval_{len(y_true)}.json"
    )

    output_path.write_text(
        json.dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(
        json.dumps(
            results,
            indent=2,
        )
    )
    print()
    print(
        f"Saved: {output_path}"
    )


if __name__ == "__main__":
    main()
