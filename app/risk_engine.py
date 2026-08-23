def score_transaction(
    voice_spoof_probability: float,
    voice_verdict: str,
    amount: float,
    known_device: bool,
    known_beneficiary: bool,
    transactions_last_10m: int,
):
    """
    Calculate transaction risk on a 0-100 scale.

    Voice authenticity carries the highest weight.
    Transaction-context signals increase risk further.
    """

    score = 0

    # Voice risk: maximum 60 points
    score += round(voice_spoof_probability * 60)

    # High transaction amount
    if amount >= 50000:
     score += 20
    elif amount >= 25000:
     score += 15
    elif amount >= 10000:
     score += 8

    # Unknown device
    if not known_device:
        score += 10

    # New / unknown beneficiary
    if not known_beneficiary:
        score += 10

    # Unusually high transaction velocity
    if transactions_last_10m >= 5:
        score += 10
    elif transactions_last_10m >= 3:
        score += 5

    score = min(score, 100)

    if score >= 80:
        risk_level = "CRITICAL"
    elif score >= 60:
        risk_level = "HIGH"
    elif score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": score,
        "risk_level": risk_level,
    }