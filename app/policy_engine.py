VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_VOICE_VERDICTS = {"HUMAN", "AI", "UNCERTAIN"}


def decide_action(risk_level: str, voice_verdict: str):
    """
    Convert model + transaction risk into a bounded financial action.

    DENY_VOICE_AUTH never means "block the user's money forever".
    It means voice authorization is not trusted and a safer
    authentication path must be used.
    """

    risk_level = risk_level.upper()
    voice_verdict = voice_verdict.upper()

    if risk_level not in VALID_RISK_LEVELS:
        raise ValueError(f"Unsupported risk level: {risk_level}")

    if voice_verdict not in VALID_VOICE_VERDICTS:
        raise ValueError(f"Unsupported voice verdict: {voice_verdict}")

    reason_codes = []

    # Strong spoof evidence must never authorize money using voice.
    if voice_verdict == "AI":
        reason_codes.append("voice_spoof_detected")

        if risk_level == "CRITICAL":
            reason_codes.append("critical_transaction_risk")

        return {
            "action": "DENY_VOICE_AUTH",
            "reason_codes": reason_codes,
        }

    # Ambiguous biometric evidence gets safer authentication.
    if voice_verdict == "UNCERTAIN":
        return {
            "action": "STEP_UP",
            "reason_codes": ["voice_auth_uncertain"],
        }

    # HUMAN voice does not bypass transaction-risk controls.
    if risk_level == "CRITICAL":
        return {
            "action": "DENY_VOICE_AUTH",
            "reason_codes": ["critical_transaction_risk"],
        }

    if risk_level == "HIGH":
        return {
            "action": "REVIEW",
            "reason_codes": ["high_transaction_risk"],
        }

    if risk_level == "MEDIUM":
        return {
            "action": "STEP_UP",
            "reason_codes": ["medium_transaction_risk"],
        }

    return {
        "action": "ALLOW",
        "reason_codes": ["risk_within_policy"],
    }
