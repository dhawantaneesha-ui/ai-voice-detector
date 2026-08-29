def score_transaction(
    voice_spoof_probability: float,
    voice_verdict: str,
    amount: float,
    known_device: bool,
    known_beneficiary: bool,
    transactions_last_10m: int,
):
    """
    Produce an explainable financial-risk score from 0 to 100.
    Every material contribution is returned as auditable evidence.
    """

    score = 0
    risk_factors = []

    # -----------------------------
    # Voice risk
    # -----------------------------
    if voice_verdict == "AI":
        voice_points = 45
        score += voice_points

        risk_factors.append({
            "code": "voice_spoof_probability",
            "points": voice_points,
        })

    elif voice_verdict == "UNCERTAIN":
        score += 20

        risk_factors.append({
            "code": "voice_uncertain",
            "points": 20,
        })

    # -----------------------------
    # Transaction amount
    # -----------------------------
    amount_points = 0

    if amount >= 50000:
        amount_points = 20
    elif amount >= 25000:
        amount_points = 15
    elif amount >= 10000:
        amount_points = 8

    if amount_points:
        score += amount_points

        risk_factors.append({
            "code": "high_value_transaction",
            "points": amount_points,
        })

    # -----------------------------
    # Device novelty
    # -----------------------------
    if not known_device:
        score += 10

        risk_factors.append({
            "code": "unknown_device",
            "points": 10,
        })

    # -----------------------------
    # Beneficiary novelty
    # -----------------------------
    if not known_beneficiary:
        score += 10

        risk_factors.append({
            "code": "unknown_beneficiary",
            "points": 10,
        })

    # -----------------------------
    # Transaction velocity
    # -----------------------------
    velocity_points = 0

    if transactions_last_10m >= 5:
        velocity_points = 10

    elif transactions_last_10m >= 3:
        velocity_points = 5

    if velocity_points:
        score += velocity_points

        risk_factors.append({
            "code": "high_velocity",
            "points": velocity_points,
        })

    score = min(score, 100)

    # -----------------------------
    # Risk level
    # -----------------------------
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
        "risk_factors": risk_factors,
    }
