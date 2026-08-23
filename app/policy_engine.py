VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_VOICE_VERDICTS = {"HUMAN", "AI", "UNCERTAIN"}


def decide_action(risk_level: str, voice_verdict: str):
    """
    Convert voice + transaction risk into a bounded financial action.

    Policy precedence:
    1. Confirmed spoof
    2. Critical transaction risk
    3. High transaction risk
    4. Uncertain voice
    5. Medium transaction risk
    6. Low-risk human voice
    """

    risk_level = risk_level.upper()
    voice_verdict = voice_verdict.upper()

    if risk_level not in VALID_RISK_LEVELS:
        raise ValueError(f"Unsupported risk level: {risk_level}")

    if voice_verdict not in VALID_VOICE_VERDICTS:
        raise ValueError(f"Unsupported voice verdict: {voice_verdict}")

    # 1. Confirmed synthetic / spoofed voice
    if voice_verdict == "AI":
        reason_codes = ["voice_spoof_detected"]

        if risk_level == "CRITICAL":
            reason_codes.append("critical_transaction_risk")
        elif risk_level == "HIGH":
            reason_codes.append("high_transaction_risk")

        return {
            "action": "DENY_VOICE_AUTH",
            "reason_codes": reason_codes,
        }

    # 2. Critical financial context overrides voice result
    if risk_level == "CRITICAL":
        return {
            "action": "DENY_VOICE_AUTH",
            "reason_codes": ["critical_transaction_risk"],
        }

    # 3. High financial risk requires review
    if risk_level == "HIGH":
        return {
            "action": "REVIEW",
            "reason_codes": ["high_transaction_risk"],
        }

    # 4. Ambiguous voice requires stronger authentication
    if voice_verdict == "UNCERTAIN":
        return {
            "action": "STEP_UP",
            "reason_codes": ["voice_auth_uncertain"],
        }

    # 5. Medium transaction risk
    if risk_level == "MEDIUM":
        return {
            "action": "STEP_UP",
            "reason_codes": ["medium_transaction_risk"],
        }

    # 6. Low risk + human voice
    return {
        "action": "ALLOW",
        "reason_codes": ["risk_within_policy"],
    }
