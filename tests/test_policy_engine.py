from app.policy_engine import decide_action


def test_low_risk_human_voice_is_allowed():
    result = decide_action(
        risk_level="LOW",
        voice_verdict="HUMAN",
    )

    assert result["action"] == "ALLOW"


def test_uncertain_voice_requires_step_up():
    result = decide_action(
        risk_level="LOW",
        voice_verdict="UNCERTAIN",
    )

    assert result["action"] == "STEP_UP"


def test_medium_risk_requires_step_up():
    result = decide_action(
        risk_level="MEDIUM",
        voice_verdict="HUMAN",
    )

    assert result["action"] == "STEP_UP"


def test_high_risk_requires_review():
    result = decide_action(
        risk_level="HIGH",
        voice_verdict="HUMAN",
    )

    assert result["action"] == "REVIEW"


def test_detected_ai_voice_denies_voice_authorization():
    result = decide_action(
        risk_level="MEDIUM",
        voice_verdict="AI",
    )

    assert result["action"] == "DENY_VOICE_AUTH"
    assert "voice_spoof_detected" in result["reason_codes"]


def test_critical_risk_overrides_uncertain_voice():
    result = decide_action(
        risk_level="CRITICAL",
        voice_verdict="UNCERTAIN",
    )

    assert result["action"] == "DENY_VOICE_AUTH"
    assert "critical_transaction_risk" in result["reason_codes"]
    
    
def test_high_risk_overrides_uncertain_voice():
    result = decide_action(
        risk_level="HIGH",
        voice_verdict="UNCERTAIN",
    )

    assert result["action"] == "REVIEW"
    assert "high_transaction_risk" in result["reason_codes"]
