from app.risk_engine import score_transaction


def test_safe_transaction_has_low_risk():
    result = score_transaction(
        voice_spoof_probability=0.05,
        voice_verdict="HUMAN",
        amount=1200,
        known_device=True,
        known_beneficiary=True,
        transactions_last_10m=1,
    )

    assert result["risk_level"] == "LOW"
    assert result["risk_score"] < 30


def test_deepfake_high_value_new_context_is_critical():
    result = score_transaction(
        voice_spoof_probability=0.92,
        voice_verdict="AI",
        amount=45000,
        known_device=False,
        known_beneficiary=False,
        transactions_last_10m=6,
    )

    assert result["risk_level"] == "CRITICAL"
    assert result["risk_score"] >= 80


def test_genuine_voice_with_high_value_unknown_device_is_not_low_risk():
    result = score_transaction(
        voice_spoof_probability=0.05,
        voice_verdict="HUMAN",
        amount=80000,
        known_device=False,
        known_beneficiary=True,
        transactions_last_10m=1,
    )

    assert result["risk_level"] == "MEDIUM"
    assert result["risk_score"] >= 30
