from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os
import shutil
import uuid

from app.assessment import build_assessment
from app.audio_utils import detect_language
from app.config import SUPPORTED_LANGUAGES
from app.model import predict_voice


app = FastAPI(
    title="VoxGuard Voice Risk API",
    description="Deepfake-aware risk assessment for voice-authorized transactions",
    version="2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_decision_reason(label: str, score: float):
    if label == "AI":
        return "Audio features strongly align with AI-generated speech patterns"

    if label == "HUMAN":
        return "Audio features strongly align with natural human speech patterns"

    return "Prediction confidence lies in an uncertainty zone to avoid unsafe misclassification"


@app.get("/health")
async def health():
    return {
        "status": "running",
        "model_loaded": True,
        "supported_languages": list(SUPPORTED_LANGUAGES.keys()),
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".wav"):
        raise HTTPException(
            status_code=400,
            detail="Only WAV files are supported",
        )

    temp_path = os.path.join(
        UPLOAD_FOLDER,
        f"temp_{uuid.uuid4()}.wav",
    )

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        prediction = predict_voice(temp_path)

        lang_code, lang_name = detect_language(temp_path)

        raw_score = prediction.get("raw_score", 0.5)

        probabilities = {
            "AI": round(raw_score, 2),
            "HUMAN": round(1 - raw_score, 2),
        }

        return {
            "status": "success",
            **prediction,
            "probabilities": probabilities,
            "decision_reason": get_decision_reason(
                prediction.get("label"),
                raw_score,
            ),
            "language": lang_name,
            "language_code": lang_code,
        }

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Voice analysis unavailable; use standard authentication",
        )

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/assess-transaction")
async def assess_transaction(
    file: UploadFile = File(...),
    amount: float = Form(...),
    known_device: bool = Form(...),
    known_beneficiary: bool = Form(...),
    transactions_last_10m: int = Form(...),
):
    if not file.filename or not file.filename.lower().endswith(".wav"):
        raise HTTPException(
            status_code=400,
            detail="Only WAV files are supported",
        )

    if amount < 0:
        raise HTTPException(
            status_code=400,
            detail="Transaction amount cannot be negative",
        )

    if transactions_last_10m < 0:
        raise HTTPException(
            status_code=400,
            detail="Transaction velocity cannot be negative",
        )

    temp_path = os.path.join(
        UPLOAD_FOLDER,
        f"assessment_{uuid.uuid4()}.wav",
    )

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        voice_result = predict_voice(temp_path)

        assessment = build_assessment(
            voice_result=voice_result,
            amount=amount,
            known_device=known_device,
            known_beneficiary=known_beneficiary,
            transactions_last_10m=transactions_last_10m,
        )

        return {
            "status": "success",
            **assessment,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Voice-risk assessment unavailable; use standard authentication",
        )

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/supported-languages")
async def supported_languages():
    return {
        "supported_languages": SUPPORTED_LANGUAGES,
    }


# Keep static frontend mount LAST so API routes match first.
FRONTEND_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "frontend",
)

if os.path.isdir(FRONTEND_FOLDER):
    app.mount(
        "/",
        StaticFiles(directory=FRONTEND_FOLDER, html=True),
        name="frontend",
    )
