---
title: AI Voice Detector
emoji: 🎙️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# AI Voice Authenticity Detector

Detect whether a WAV voice sample is AI-generated, human, or uncertain.

The project has:

- FastAPI backend on `http://127.0.0.1:8000`
- Static frontend on `http://127.0.0.1:8092`
- MFCC feature extraction with a saved scikit-learn model

## Run From VS Code

Open this folder in VS Code:

```powershell
C:\Users\ASUS\OneDrive\Desktop\Buildathon\ai-voice-auth-detector
```

Then use two terminals.

Backend:

```powershell
.\run_backend.ps1
```

Frontend:

```powershell
.\run_frontend.ps1
```

If PowerShell blocks scripts, run them like this:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_backend.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_frontend.ps1
```

Open the app:

```text
http://127.0.0.1:8092/
```

Check the backend:

```text
http://127.0.0.1:8000/health
```

For deployment-style local testing, the backend also serves the frontend:

```text
http://127.0.0.1:8000/
```

## VS Code Tasks

You can also use:

1. Press `Ctrl + Shift + P`
2. Search `Tasks: Run Task`
3. Run `Run backend`
4. Open another task and run `Run frontend`

To stop old local servers:

```powershell
.\stop_servers.ps1
```

## API

Prediction endpoint:

```text
POST http://127.0.0.1:8000/predict
```

Upload a `.wav` file using the form field name `file`.

## Deploy

This repo includes `render.yaml` for Render deployment.

1. Push the latest code to GitHub.
2. Open Render and create a new Blueprint from this GitHub repo.
3. Render will run:

```text
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

After deployment, use the Render service URL as the live demo link.

## Notes

- Use Python 3.11.
- The old `venv/` folder may be stale, so the scripts use `py -3.11`.
- Frontend uses port `8092` to avoid browser cache issues from older local runs.
