from app.model import apply_threshold


def test_moderate_probability_is_uncertain():
    label, confidence = apply_threshold(
        ai_prob=0.63,
        human_prob=0.37,
    )

    assert label == "UNCERTAIN"


def test_strong_ai_probability_is_ai():
    label, confidence = apply_threshold(
        ai_prob=0.95,
        human_prob=0.05,
    )

    assert label == "AI"


def test_strong_human_probability_is_human():
    label, confidence = apply_threshold(
        ai_prob=0.05,
        human_prob=0.95,
    )

    assert label == "HUMAN"
    