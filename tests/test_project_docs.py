from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (BASE_DIR / path).read_text(encoding="utf-8")


def test_readme_positions_voxguard_for_razorpay_risk_track():
    readme = read("README.md")

    assert "# VoxGuard" in readme
    assert "AI Risk Manager" in readme
    assert "Razorpay Buildathon Track 02" in readme
    assert "voice-authorized payment fraud" in readme
    assert "# AI Voice Authenticity Detector" not in readme


def test_readme_includes_honest_metrics_and_false_positive_cost():
    readme = read("README.md")

    assert "ASVspoof2019 LA" in readme
    assert "ASVspoof2021 LA" in readme
    assert "False-positive cost" in readme
    assert "not calibrated" in readme
    assert "290 / 1000" in readme


def test_readme_states_defense_only_scope():
    readme = read("README.md")

    assert "Defense-only" in readme
    assert "does not generate" in readme
    assert "deepfake" in readme


def test_readme_documents_razorpay_test_mode_with_mock_fallback():
    readme = read("README.md")

    assert "Razorpay Test Mode Orders API" in readme
    assert "RAZORPAY_KEY_ID" in readme
    assert "RAZORPAY_KEY_SECRET" in readme
    assert "mock fallback" in readme
    assert "amount in paise" in readme


def test_env_example_documents_secret_names_without_real_values():
    env_example = read(".env.example")
    gitignore = read(".gitignore")

    assert "RAZORPAY_KEY_ID=rzp_test_replace_with_key_id" in env_example
    assert "RAZORPAY_KEY_SECRET=replace_with_key_secret" in env_example
    assert "rzp_live_" not in env_example
    assert ".env" in gitignore


def test_supporting_docs_exist_for_submission():
    for path in [
        "docs/demo-script.md",
        "docs/architecture.md",
        "docs/evaluation.md",
    ]:
        content = read(path)
        assert "VoxGuard" in content
