VALID_RISK_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL"
}

VALID_VOICE_VERDICTS = {
    "HUMAN",
    "AI",
    "UNCERTAIN"
}


def decide_action(
    risk_level: str,
    voice_verdict: str,
    risk_factors=None,
):
    """
    Convert voice authenticity risk + transaction risk
    into a bounded payment security action.
    """

    risk_level = risk_level.upper()
    voice_verdict = voice_verdict.upper()


    if risk_level not in VALID_RISK_LEVELS:
        raise ValueError(
            f"Unsupported risk level: {risk_level}"
        )

    if voice_verdict not in VALID_VOICE_VERDICTS:
        raise ValueError(
            f"Unsupported voice verdict: {voice_verdict}"
        )

    risk_factor_codes = {
        factor.get("code")
        for factor in (risk_factors or [])
    }


    # Strongest case:
    # AI voice + critical transaction
    if (
        voice_verdict == "AI"
        and risk_level == "CRITICAL"
    ):
        return {
            "action": "DENY_VOICE_AUTH",
            "reason_codes": [
                "voice_spoof_detected",
                "critical_transaction_risk",
            ],
        }


    # AI voice but not enough transaction risk
    # ask for stronger verification
    if voice_verdict == "AI":
        if (
            risk_level == "MEDIUM"
            and risk_factor_codes == {"voice_spoof_probability"}
        ):
            return {
                "action": "ALLOW",
                "reason_codes": [
                    "voice_signal_not_standalone_blocker",
                    "trusted_low_value_context",
                ],
            }

        return {
            "action": "STEP_UP",
            "reason_codes": [
                "voice_spoof_suspected",
                "additional_authentication_required",
            ],
        }


    # High transaction risk
    if risk_level == "HIGH":

        return {
            "action": "REVIEW",
            "reason_codes": [
                "high_transaction_risk",
            ],
        }


    # Critical financial risk
    if risk_level == "CRITICAL":

        return {
            "action": "DENY_VOICE_AUTH",
            "reason_codes": [
                "critical_transaction_risk",
            ],
        }


    # Uncertain voice
    if voice_verdict == "UNCERTAIN":

        return {
            "action": "STEP_UP",
            "reason_codes": [
                "voice_auth_uncertain",
            ],
        }


    # Medium risk
    if risk_level == "MEDIUM":

        return {
            "action": "STEP_UP",
            "reason_codes": [
                "medium_transaction_risk",
            ],
        }


    return {
        "action": "ALLOW",
        "reason_codes": [
            "risk_within_policy",
        ],
    }
