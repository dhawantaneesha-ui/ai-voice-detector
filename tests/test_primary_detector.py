from app.anti_spoof import predict_aasist
import app.main as main


def test_voxguard_api_uses_aasist_as_primary_detector():
    assert main.predict_voice is predict_aasist
