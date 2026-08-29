import numpy as np
import torch

import app.anti_spoof as anti_spoof
from app.anti_spoof import pad_audio, predict_aasist, verdict_from_spoof_probability


def test_short_audio_is_repeated_to_aasist_input_length():
    audio = np.arange(1000, dtype=np.float32)

    result = pad_audio(audio)

    assert result.shape == (64600,)
    assert np.array_equal(result[:1000], audio)


def test_only_very_high_spoof_score_is_ai():
    assert verdict_from_spoof_probability(0.96) == "AI"


def test_only_very_low_spoof_score_is_human():
    assert verdict_from_spoof_probability(0.04) == "HUMAN"

def test_middle_spoof_score_is_uncertain():
    assert verdict_from_spoof_probability(0.55) == "UNCERTAIN"


def test_predict_aasist_returns_official_class_breakdown(monkeypatch, tmp_path):
    class FakeModel:
        def __call__(self, tensor):
            return None, torch.tensor([[4.0, 1.0]], dtype=torch.float32)

    audio = np.ones(anti_spoof.TARGET_SAMPLE_RATE * 4, dtype=np.float32)

    monkeypatch.setattr(
        anti_spoof.librosa,
        "load",
        lambda file_path, sr, mono: (audio, sr),
    )
    monkeypatch.setattr(
        anti_spoof,
        "load_aasist_model",
        lambda: FakeModel(),
    )

    result = predict_aasist(str(tmp_path / "sample.wav"))

    assert result["label"] == "AI"
    assert result["raw_score"] == result["probability_breakdown"]["AI"]
    assert result["probability_breakdown"]["AI"] > result["probability_breakdown"]["HUMAN"]
    assert result["confidence_kind"] == "model_margin_not_calibrated"
