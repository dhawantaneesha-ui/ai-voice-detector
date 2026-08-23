import numpy as np

from app.anti_spoof import pad_audio, verdict_from_spoof_probability


def test_short_audio_is_repeated_to_aasist_input_length():
    audio = np.arange(1000, dtype=np.float32)

    result = pad_audio(audio)

    assert result.shape == (64600,)
    assert np.array_equal(result[:1000], audio)


def test_high_spoof_score_is_ai():
    assert verdict_from_spoof_probability(0.91) == "AI"


def test_low_spoof_score_is_human():
    assert verdict_from_spoof_probability(0.08) == "HUMAN"


def test_middle_spoof_score_is_uncertain():
    assert verdict_from_spoof_probability(0.55) == "UNCERTAIN"
