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


def test_spoof_signal_without_risky_context_is_high_not_critical():
    result = score_transaction(
        voice_spoof_probability=0.99,
        voice_verdict="AI",
        amount=50000,
        known_device=True,
        known_beneficiary=True,
        transactions_last_10m=1,
    )

    assert result["risk_level"] == "HIGH"
    assert result["risk_score"] < 80


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


def test_unknown_device_is_exposed_as_risk_evidence():
    result = score_transaction(
        voice_spoof_probability=0.05,
        voice_verdict="HUMAN",
        amount=80000,
        known_device=False,
        known_beneficiary=True,
        transactions_last_10m=1,
    )

    assert {
        "code": "unknown_device",
        "points": 10,
    } in result["risk_factors"]


def test_critical_transaction_exposes_all_risk_evidence():
    result = score_transaction(
        voice_spoof_probability=0.92,
        voice_verdict="AI",
        amount=45000,
        known_device=False,
        known_beneficiary=False,
        transactions_last_10m=6,
    )

    codes = {
        factor["code"]
        for factor in result["risk_factors"]
    }

    assert "voice_spoof_probability" in codes
    assert "high_value_transaction" in codes
    assert "unknown_device" in codes
    assert "unknown_beneficiary" in codes
    assert "high_velocity" in codes


def test_uncertain_voice_adds_risk_evidence():
    result = score_transaction(
        voice_spoof_probability=0.57,
        voice_verdict="UNCERTAIN",
        amount=500,
        known_device=True,
        known_beneficiary=True,
        transactions_last_10m=1,
    )

    codes = {
        factor["code"]
        for factor in result["risk_factors"]
    }

    assert "voice_uncertain" in codes
