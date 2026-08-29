from app.payment import create_payment, process_payment_decision


def test_payment_creation():
    result = create_payment(50000)

    assert result["amount"] == 50000
    assert result["currency"] == "INR"
    assert result["status"] == "created"
    assert result["provider"] == "VoxGuard Mock Razorpay"


def test_payment_creation_uses_razorpay_order_client_when_credentials_exist(monkeypatch):
    calls = []

    def fake_order_client(payload, key_id, key_secret):
        calls.append({
            "payload": payload,
            "key_id": key_id,
            "key_secret": key_secret,
        })

        return {
            "id": "order_test123",
            "amount": 5000000,
            "currency": "INR",
            "status": "created",
        }

    monkeypatch.setenv("RAZORPAY_KEY_ID", "rzp_test_key")
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", "secret")

    result = create_payment(
        50000,
        order_client=fake_order_client,
    )

    assert calls == [
        {
            "payload": {
                "amount": 5000000,
                "currency": "INR",
                "receipt": result["receipt"],
                "notes": {
                    "product": "VoxGuard",
                    "risk_layer": "voice_authorization",
                },
            },
            "key_id": "rzp_test_key",
            "key_secret": "secret",
        }
    ]
    assert result["payment_id"] == "order_test123"
    assert result["provider"] == "Razorpay Test Mode"
    assert result["amount"] == 50000


def test_payment_creation_falls_back_to_mock_without_credentials(monkeypatch):
    def failing_order_client(payload, key_id, key_secret):
        raise AssertionError("order client should not be called")

    monkeypatch.delenv("RAZORPAY_KEY_ID", raising=False)
    monkeypatch.delenv("RAZORPAY_KEY_SECRET", raising=False)

    result = create_payment(
        750,
        order_client=failing_order_client,
    )

    assert result["payment_id"].startswith("pay_")
    assert result["provider"] == "VoxGuard Mock Razorpay"


def test_payment_creation_falls_back_to_mock_when_razorpay_rejects_credentials(monkeypatch):
    def failing_order_client(payload, key_id, key_secret):
        raise RuntimeError("Razorpay order creation failed: HTTP 401")

    monkeypatch.setenv("RAZORPAY_KEY_ID", "rzp_test_bad")
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", "bad_secret")

    result = create_payment(
        5000,
        order_client=failing_order_client,
    )

    assert result["payment_id"].startswith("pay_")
    assert result["provider"] == "VoxGuard Mock Razorpay"
    assert result["mode"] == "mock"
    assert result["gateway_warning"] == "Razorpay Test Mode unavailable; using mock fallback"


def test_review_payment_is_held():
    result = process_payment_decision("REVIEW")

    assert result["payment_status"] == "ON_HOLD"


def test_step_up_payment_requires_verification():
    result = process_payment_decision("STEP_UP")

    assert result["payment_status"] == "REQUIRES_VERIFICATION"


def test_denied_payment_fails():
    result = process_payment_decision(
        "DENY_VOICE_AUTH"
    )

    assert result["payment_status"] == "FAILED"
