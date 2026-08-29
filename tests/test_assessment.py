from app.assessment import build_assessment


def test_deepfake_transaction_returns_complete_denial_decision():
    voice_result = {
        "label": "AI",
        "raw_score": 0.92,
        "confidence": 84.0,
        "model_name": "test-model",
    }

    result = build_assessment(
        voice_result=voice_result,
        amount=45000,
        known_device=False,
        known_beneficiary=False,
        transactions_last_10m=6,
    )

    assert result["voice"]["verdict"] == "AI"
    assert result["risk"]["risk_level"] == "CRITICAL"
    assert result["decision"]["action"] == "DENY_VOICE_AUTH"
    assert "voice_spoof_detected" in result["decision"]["reason_codes"]
    assert len(result["risk"]["risk_factors"]) >= 4


def test_uncertain_voice_never_silently_allows_payment():
    voice_result = {
        "label": "UNCERTAIN",
        "raw_score": 0.63,
        "confidence": 26.0,
        "model_name": "test-model",
    }

    result = build_assessment(
        voice_result=voice_result,
        amount=1000,
        known_device=True,
        known_beneficiary=True,
        transactions_last_10m=1,
    )

    assert result["decision"]["action"] == "STEP_UP"


def test_spoof_signal_with_known_context_steps_up_not_denies():
    voice_result = {
        "label": "AI",
        "raw_score": 0.99,
        "confidence": 99.0,
        "confidence_kind": "model_margin_not_calibrated",
        "model_name": "test-model",
    }

    result = build_assessment(
        voice_result=voice_result,
        amount=50000,
        known_device=True,
        known_beneficiary=True,
        transactions_last_10m=1,
    )

    assert result["risk"]["risk_level"] == "HIGH"
    assert result["decision"]["action"] == "STEP_UP"
    assert result["voice"]["confidence_kind"] == "model_margin_not_calibrated"


def test_low_value_known_context_can_allow_despite_spoof_signal():
    voice_result = {
        "label": "AI",
        "raw_score": 0.99,
        "confidence": 99.0,
        "confidence_kind": "model_margin_not_calibrated",
        "model_name": "test-model",
    }

    result = build_assessment(
        voice_result=voice_result,
        amount=5000,
        known_device=True,
        known_beneficiary=True,
        transactions_last_10m=1,
    )

    assert result["risk"]["risk_level"] == "MEDIUM"
    assert result["risk"]["risk_score"] == 45
    assert result["decision"]["action"] == "ALLOW"
    assert "trusted_low_value_context" in result["decision"]["reason_codes"]
