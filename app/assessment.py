from app.policy_engine import decide_action
from app.risk_engine import score_transaction


def build_assessment(
    voice_result: dict,
    amount: float,
    known_device: bool,
    known_beneficiary: bool,
    transactions_last_10m: int,
):
    """
    Compose voice authenticity, transaction risk and bounded policy
    into one auditable VoxGuard decision.
    """

    voice_verdict = str(voice_result["label"]).upper()
    spoof_probability = float(voice_result["raw_score"])

    risk = score_transaction(
        voice_spoof_probability=spoof_probability,
        voice_verdict=voice_verdict,
        amount=amount,
        known_device=known_device,
        known_beneficiary=known_beneficiary,
        transactions_last_10m=transactions_last_10m,
    )

    decision = decide_action(
        risk_level=risk["risk_level"],
        voice_verdict=voice_verdict,
    )

    return {
        "voice": {
            "verdict": voice_verdict,
            "spoof_probability": spoof_probability,
            "confidence": voice_result.get("confidence"),
            "model_name": voice_result.get("model_name"),
        },
        "transaction": {
            "amount": amount,
            "known_device": known_device,
            "known_beneficiary": known_beneficiary,
            "transactions_last_10m": transactions_last_10m,
        },
        "risk": risk,
        "decision": decision,
    }
