from app.model import predict_voice

audio_path = "dataset/sample_audio/sample.wav"  # change if needed

result = predict_voice(audio_path, language="hi")
print(result)
