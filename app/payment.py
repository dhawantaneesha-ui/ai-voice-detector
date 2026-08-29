import base64
import json
import os
import time
import urllib.request
import uuid


RAZORPAY_ORDERS_URL = "https://api.razorpay.com/v1/orders"


def _amount_to_subunits(amount: float) -> int:
    return int(round(float(amount) * 100))


def create_razorpay_order(
    payload: dict,
    key_id: str,
    key_secret: str,
) -> dict:
    credentials = f"{key_id}:{key_secret}".encode("utf-8")
    auth_header = base64.b64encode(credentials).decode("ascii")

    request = urllib.request.Request(
        RAZORPAY_ORDERS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _mock_payment(
    amount: float,
    gateway_warning: str | None = None,
) -> dict:
    payment = {
        "payment_id": f"pay_{uuid.uuid4().hex[:12]}",
        "amount": amount,
        "currency": "INR",
        "status": "created",
        "provider": "VoxGuard Mock Razorpay",
        "mode": "mock",
    }

    if gateway_warning:
        payment["gateway_warning"] = gateway_warning

    return payment


def create_payment(
    amount: float,
    order_client=create_razorpay_order,
):
    """
    Create a Razorpay Test Mode order when credentials are configured.
    Fall back to a local mock so the hackathon demo remains runnable.
    """

    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")

    if not key_id or not key_secret:
        return _mock_payment(amount)

    receipt = f"voxguard_{uuid.uuid4().hex[:12]}"
    payload = {
        "amount": _amount_to_subunits(amount),
        "currency": "INR",
        "receipt": receipt,
        "notes": {
            "product": "VoxGuard",
            "risk_layer": "voice_authorization",
        },
    }

    try:
        order = order_client(
            payload,
            key_id,
            key_secret,
        )
    except Exception:
        return _mock_payment(
            amount,
            gateway_warning=(
                "Razorpay Test Mode unavailable; using mock fallback"
            ),
        )

    return {
        "payment_id": order["id"],
        "amount": amount,
        "amount_subunits": order.get("amount"),
        "currency": order.get("currency", "INR"),
        "receipt": receipt,
        "status": order.get("status", "created"),
        "provider": "Razorpay Test Mode",
        "mode": "razorpay_test",
        "created_at": order.get("created_at", int(time.time())),
    }


def process_payment_decision(decision: str):
    """
    Convert VoxGuard decision into payment state.
    """

    if decision == "ALLOW":
        return {
            "payment_status": "SUCCESS",
            "message": "Payment authorized",
        }

    if decision == "REVIEW":
        return {
            "payment_status": "ON_HOLD",
            "message": "Additional verification required",
        }

    if decision == "STEP_UP":
        return {
            "payment_status": "REQUIRES_VERIFICATION",
            "message": "Additional verification required",
        }

    return {
        "payment_status": "FAILED",
        "message": "Voice authorization rejected",
    }
