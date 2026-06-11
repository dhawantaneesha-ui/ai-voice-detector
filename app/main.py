from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil, os, uuid

from app.config import SUPPORTED_LANGUAGES
from app.model import predict_voice
from app.audio_utils import detect_language

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Voice Authenticity Detection API",
    description="Detects AI-generated vs Human voice samples with language detection",
    version="1.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # hackathon-safe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------------------------------------------------
# Explainability helper
# -------------------------------------------------
def get_decision_reason(label: str, score: float):
    if label == "AI":
        return "Audio features strongly align with AI-generated speech patterns"
    elif label == "HUMAN":
        return "Audio features strongly align with natural human speech patterns"
    else:
        return "Prediction confidence lies in an uncertainty zone to avoid misclassification"


# -------------------------------------------------
# Health Check
# -------------------------------------------------
@app.get("/health")
async def health():
    return {
        "status": "running",
        "model_loaded": True,
        "supported_languages": list(SUPPORTED_LANGUAGES.keys())
    }


# -------------------------------------------------
# Prediction Endpoint
# -------------------------------------------------
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only WAV files are supported")

    temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{uuid.uuid4()}.wav")

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # AI vs Human prediction
        prediction = predict_voice(temp_path)

        # Language detection
        lang_code, lang_name = detect_language(temp_path)

        raw_score = prediction.get("raw_score", 0.5)

        probabilities = {
            "AI": round(raw_score, 2),
            "HUMAN": round(1 - raw_score, 2)
        }

        return {
            "status": "success",
            **prediction,
            "probabilities": probabilities,
            "decision_reason": get_decision_reason(
                prediction.get("label"),
                raw_score
            ),
            "language": lang_name,
            "language_code": lang_code
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# -------------------------------------------------
# Supported Languages
# -------------------------------------------------
@app.get("/supported-languages")
async def supported_languages():
    return {"supported_languages": SUPPORTED_LANGUAGES}
