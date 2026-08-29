from html.parser import HTMLParser
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class IdCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == "id":
                self.ids.append(value)


def test_frontend_has_unique_dom_ids():
    parser = IdCollector()
    parser.feed((BASE_DIR / "frontend" / "index.html").read_text(encoding="utf-8"))

    duplicate_ids = {
        element_id
        for element_id in parser.ids
        if parser.ids.count(element_id) > 1
    }

    assert duplicate_ids == set()


def test_frontend_script_does_not_have_trailing_syntax_junk():
    source = (BASE_DIR / "frontend" / "js" / "app.js").read_text(encoding="utf-8")

    assert source.rstrip().endswith("}")


def test_frontend_describes_model_outputs_as_signals_not_probabilities():
    html = (BASE_DIR / "frontend" / "index.html").read_text(encoding="utf-8")
    script = (BASE_DIR / "frontend" / "js" / "app.js").read_text(encoding="utf-8")

    assert "AI probability" not in html
    assert "Human probability" not in html
    assert "Spoof signal" in html
    assert "Bona fide signal" in html
    assert "Model margin" in script


def test_default_transaction_context_is_known_and_low_velocity():
    script = (BASE_DIR / "frontend" / "js" / "app.js").read_text(encoding="utf-8")

    default_context = script.split("const demoScenarios", maxsplit=1)[0]

    assert "known_device: true" in default_context
    assert "known_beneficiary: true" in default_context
    assert "transactions_last_10m: 1" in default_context


def test_frontend_maps_policy_actions_to_customer_facing_labels():
    script = (BASE_DIR / "frontend" / "js" / "app.js").read_text(encoding="utf-8")

    assert "Payment Authorized" in script
    assert "Additional Verification Required" in script
    assert "Payment Under Review" in script
    assert "Voice Authorization Rejected" in script
    assert "decision.action || \"UNKNOWN\"" not in script


def test_frontend_maps_risk_factors_to_readable_labels():
    script = (BASE_DIR / "frontend" / "js" / "app.js").read_text(encoding="utf-8")

    assert "AASIST spoof signal" in script
    assert "High-value payment" in script
    assert "New device" in script
    assert "New beneficiary" in script
    assert "High recent payment velocity" in script
    assert "factor.code}: +" not in script


def test_frontend_is_payment_first_not_upload_first():
    html = (BASE_DIR / "frontend" / "index.html").read_text(encoding="utf-8")

    assert "Payment Request" in html
    assert "Voice Authorization" in html
    assert "Use WAV file instead" in html
    assert "Voice Authorization" in html.split("Use WAV file instead", maxsplit=1)[0]
    assert "Audio Sample" not in html


def test_frontend_includes_honest_model_limitation_copy():
    html = (BASE_DIR / "frontend" / "index.html").read_text(encoding="utf-8")

    assert "model signal, not a calibrated probability" in html
    assert "Browser microphone audio may require step-up verification" in html


def test_demo_buttons_describe_transaction_context_not_fake_outputs():
    html = (BASE_DIR / "frontend" / "index.html").read_text(encoding="utf-8")

    assert "Known device, known beneficiary" in html
    assert "New device, new beneficiary" in html
    assert "No scenario changes the voice model output" in html


def test_frontend_exposes_amount_control_and_payment_provider():
    html = (BASE_DIR / "frontend" / "index.html").read_text(encoding="utf-8")
    script = (BASE_DIR / "frontend" / "js" / "app.js").read_text(encoding="utf-8")

    assert 'id="amountInput"' in html
    assert "paymentProvider" in html
    assert "payment.provider" in script
    assert "currentPaymentProvider" in script
    assert "updatePaymentPreview" in script


def test_frontend_primary_result_is_policy_decision():
    script = (BASE_DIR / "frontend" / "js" / "app.js").read_text(encoding="utf-8")

    assert "setText(\n    labelEl,\n    policyAction\n  );" in script
    assert "setText(\n    labelEl,\n    voiceSignal\n  );" not in script


def test_frontend_can_display_gateway_fallback_warning():
    html = (BASE_DIR / "frontend" / "index.html").read_text(encoding="utf-8")
    script = (BASE_DIR / "frontend" / "js" / "app.js").read_text(encoding="utf-8")

    assert 'id="paymentWarning"' in html
    assert "currentPaymentWarning" in script
    assert "gateway_warning" in script
