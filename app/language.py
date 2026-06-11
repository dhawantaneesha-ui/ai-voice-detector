import whisper
from config import SUPPORTED_LANGUAGES, WHISPER_MODEL


# Load Whisper model once (efficient)
whisper_model = whisper.load_model(WHISPER_MODEL)


def detect_language(file_path: str) -> dict:
    """
    Detect spoken language from audio using Whisper.

    Returns:
    {
        "code": "en",
        "name": "English",
        "confidence": 0.87
    }
    """

    # Load and preprocess audio
    audio = whisper.load_audio(file_path)
    audio = whisper.pad_or_trim(audio)

    # Convert to Mel spectrogram
    mel = whisper.log_mel_spectrogram(audio).to(whisper_model.device)

    # Detect language probabilities
    _, probs = whisper_model.detect_language(mel)

    # Select most probable language
    lang_code = max(probs, key=probs.get)

    return {
        "code": lang_code,
        "name": SUPPORTED_LANGUAGES.get(lang_code, "Unsupported"),
        "confidence": round(probs[lang_code], 2)
    }
