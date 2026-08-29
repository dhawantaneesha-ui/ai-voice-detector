from app.model import predict_voice


if __name__ == "__main__":
    audio_path = "dataset/sample_audio/sample.wav"
    result = predict_voice(audio_path)
    print(result)
