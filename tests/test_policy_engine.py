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

def test_detected_ai_voice_requires_step_up_on_medium_risk():
    result = decide_action(
        risk_level="MEDIUM",
        voice_verdict="AI",
    )

    assert result["action"] == "STEP_UP"
    assert "voice_spoof_suspected" in result["reason_codes"]


def test_detected_ai_voice_with_only_low_value_trusted_context_is_allowed():
    result = decide_action(
        risk_level="MEDIUM",
        voice_verdict="AI",
        risk_factors=[
            {
                "code": "voice_spoof_probability",
                "points": 45,
            }
        ],
    )

    assert result["action"] == "ALLOW"
    assert "trusted_low_value_context" in result["reason_codes"]
    


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
