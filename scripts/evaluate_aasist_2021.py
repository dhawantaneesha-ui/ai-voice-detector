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


DATASET_NAME = "SpeechAntiSpoofingBenchmarks/ASVspoof2021_LA"
TARGET_SR = 16000
THRESHOLD = 0.50


def decode_audio(record):
    audio, sr = sf.read(
        io.BytesIO(record["bytes"]),
        dtype="float32",
    )

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    if sr != TARGET_SR:
        audio = librosa.resample(
            audio,
            orig_sr=sr,
            target_sr=TARGET_SR,
        )

    return audio


def predict(model, audio):

    x = pad_audio(audio)

    tensor = torch.tensor(
        x,
        dtype=torch.float32,
    ).unsqueeze(0)

    start = time.perf_counter()

    with torch.inference_mode():
        _, logits = model(tensor)
        probs = torch.softmax(logits, dim=1)[0]

    latency = (
        time.perf_counter() - start
    ) * 1000

    return (
        float(probs[0]),
        latency,
    )


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--per-class",
        type=int,
        default=100,
    )

    args = parser.parse_args()

    print(
        "Loading ASVspoof2021 LA evaluation partition..."
    )

    dataset = load_dataset(
        DATASET_NAME,
        split="test",
        streaming=True,
    )

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
        0:0,
        1:0,
    }


    for row in dataset:

        label = int(row["label"])

        if counts[label] >= args.per_class:
            continue


        audio = decode_audio(
            row["audio"]
        )


        score, latency = predict(
            model,
            audio,
        )


        pred = int(
            score >= THRESHOLD
        )


        y_true.append(label)
        y_pred.append(pred)
        scores.append(score)
        latencies.append(latency)

        counts[label]+=1


        if len(y_true)%25==0:
            print(
                f"Evaluated {len(y_true)} "
                f"bonafide={counts[0]} "
                f"spoof={counts[1]}"
            )


        if (
            counts[0]>=args.per_class
            and counts[1]>=args.per_class
        ):
            break



    tn,fp,fn,tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0,1],
    ).ravel()


    # Product triage

    AI_THRESHOLD = 0.80
    HUMAN_THRESHOLD = 0.20


    genuine = {
        "allowed":0,
        "uncertain":0,
        "false_voice_denials":0,
    }

    spoof = {
        "strongly_caught":0,
        "uncertain":0,
        "dangerously_allowed":0,
    }


    for label,score in zip(
        y_true,
        scores,
    ):

        if score>=AI_THRESHOLD:
            verdict="AI"

        elif score<=HUMAN_THRESHOLD:
            verdict="HUMAN"

        else:
            verdict="UNCERTAIN"



        if label==0:

            if verdict=="HUMAN":
                genuine["allowed"]+=1

            elif verdict=="UNCERTAIN":
                genuine["uncertain"]+=1

            else:
                genuine["false_voice_denials"]+=1


        else:

            if verdict=="AI":
                spoof["strongly_caught"]+=1

            elif verdict=="UNCERTAIN":
                spoof["uncertain"]+=1

            else:
                spoof["dangerously_allowed"]+=1



    result={

        "dataset":DATASET_NAME,

        "samples":len(y_true),
        "scores": scores,
        "labels": y_true,

        "precision":precision_score(
            y_true,
            y_pred,
            zero_division=0,
        ),

        "recall":recall_score(
            y_true,
            y_pred,
            zero_division=0,
        ),

        "f1":f1_score(
            y_true,
            y_pred,
            zero_division=0,
        ),

        "accuracy":accuracy_score(
            y_true,
            y_pred,
        ),


        "confusion_matrix":{
            "tn":int(tn),
            "fp":int(fp),
            "fn":int(fn),
            "tp":int(tp),
        },


        "product_voice_triage":{

            "genuine":genuine,

            "spoof":spoof,

            "thresholds":{
                "human":HUMAN_THRESHOLD,
                "ai":AI_THRESHOLD,
            }
        },


        "latency":{
            "mean_ms":np.mean(latencies),
            "p95_ms":np.percentile(
                latencies,
                95,
            )
        }

    }


    Path("reports").mkdir(
        exist_ok=True
    )


    Path(
        "reports/aasist_2021_product_eval.json"
    ).write_text(
        json.dumps(
            result,
            indent=2,
        )
    )


    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__=="__main__":
    main()