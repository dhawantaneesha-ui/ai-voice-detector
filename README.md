---
title: VoxGuard AI Risk Manager
emoji: 🎙️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# VoxGuard: AI Risk Manager for Voice-Authorized Payment Fraud

VoxGuard is a **Razorpay Buildathon Track 02: AI Risk Manager** project for one concrete loss class: **voice-authorized payment fraud** caused by AI-generated or deepfake speech.

The product is not a generic "AI voice detector." It is a defense-only risk layer for high-value payment authorization. VoxGuard runs an anti-spoofing model, combines that voice authenticity signal with transaction context, and returns an explainable payment decision.

```text
Live voice authorization
  -> AASIST-L anti-spoof signal
  -> transaction risk context
  -> risk engine
  -> policy engine
  -> payment decision
```

## Track 02 Fit

Razorpay's AI Risk Manager track asks builders to stop merchant losses from fraud, returns, and chargebacks with a working detector, verifier, or responder, measured honestly on held-out data.

VoxGuard fits that bar by providing:

- A working verifier for voice-authorized payment fraud.
- Razorpay Test Mode Orders API support with mock fallback for demos without credentials.
- Measured precision, recall, F1, false-positive rate, and latency.
- Explicit false-positive cost handling through step-up verification.
- Defense-only scope: VoxGuard detects and gates suspicious payment authorization; it does not generate deepfake audio or enable attacks.

## What It Does

For each payment verification request, VoxGuard evaluates:

- Voice authenticity signal from AASIST-L.
- Transaction amount.
- Whether the device is known.
- Whether the beneficiary is known.
- Recent transaction velocity.

The policy engine can return:

- `ALLOW` -> Payment Authorized
- `STEP_UP` -> Additional Verification Required
- `REVIEW` -> Payment Under Review
- `DENY_VOICE_AUTH` -> Voice Authorization Rejected

Voice is one signal, not an unquestionable truth. A suspicious voice signal on a low-value, trusted-context transaction can still be allowed; the same signal on a high-value or risky-context transaction can trigger step-up, review, or voice authorization rejection.

## Model Semantics

Primary detector: **AASIST-L**.

Official class semantics:

- Class `0` = spoof
- Class `1` = bona fide
- Higher bona-fide score means more human-like according to the model

The displayed score is a model signal, **not calibrated** real-world fraud probability. Browser microphone recordings can trigger false positives because the pretrained model was not calibrated for every consumer mic/browser/audio-processing path.

## Evaluation

| Dataset | Samples | Precision | Recall | F1 | Accuracy | FPR | Latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ASVspoof2019 LA | 200 balanced | 1.000 | 0.910 | 0.953 | 0.955 | 0.000 | mean ~530 ms, p95 ~646 ms |
| ASVspoof2021 LA | 200 balanced | 0.770 | 0.970 | 0.858 | 0.840 | 0.290 | mean ~535-760 ms depending on execution path |

False-positive cost: on ASVspoof2021 LA, the observed FPR was `0.29`, equivalent to roughly **290 / 1000** genuine users being challenged if this signal were used alone. VoxGuard handles that by using `STEP_UP` or `REVIEW` instead of blindly blocking every suspicious voice signal.

See [docs/evaluation.md](docs/evaluation.md) for the full interpretation.

## Demo Flow

1. Open the payment authorization UI.
2. Review the payment request, usually INR 50,000 in the demo.
3. Say: "I authorize this payment."
4. VoxGuard records live audio or accepts a WAV fallback.
5. AASIST-L produces a voice authenticity signal.
6. The risk engine combines voice plus transaction context.
7. The policy engine returns the payment decision.

Demo scenarios use the same payment amount and only change transaction context:

| Scenario | Known Device | Known Beneficiary | Transactions Last 10m |
| --- | --- | --- | ---: |
| Safe Payment | Yes | Yes | 1 |
| Suspicious Payment | No | No | 6 |
| Deepfake Attack | No | No | 10 |

See [docs/demo-script.md](docs/demo-script.md) for the 5-minute pitch script.

## Razorpay Test Mode

VoxGuard can create a real Razorpay Test Mode order when credentials are configured:

```powershell
$env:RAZORPAY_KEY_ID="rzp_test_..."
$env:RAZORPAY_KEY_SECRET="..."
```

Use [.env.example](.env.example) as the local template if you prefer a file-based setup. Keep the real `.env` file private; `.gitignore` excludes it from commits.

When those variables are present, `/create-payment` calls Razorpay Orders API `POST /v1/orders` with the amount in paise. When they are absent, VoxGuard uses `VoxGuard Mock Razorpay` so the risk demo still works locally and during judging.

The risk decision is still made by VoxGuard. Razorpay provides the payment/order context; VoxGuard decides whether voice authorization should allow, step up, review, or reject.

## API

Backend runs on `http://127.0.0.1:8000`.

Endpoints:

- `GET /health`
- `POST /predict`
- `POST /assess-transaction`
- `POST /create-payment`
- `POST /verify-payment`
- `GET /supported-languages`

`POST /verify-payment` accepts:

- `file`: WAV voice authorization audio
- `payment_id`
- `amount`
- `known_device`
- `known_beneficiary`
- `transactions_last_10m`

It returns:

- `voice`: AASIST-L signal and metadata
- `risk`: score, level, and factors
- `decision`: policy action and reason codes
- `payment`: Razorpay Test Mode or mock payment status

## Local Run

Backend:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_backend.ps1
```

Frontend:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_frontend.ps1
```

Open:

```text
http://127.0.0.1:8092/
```

The backend also serves the frontend for deployment-style testing:

```text
http://127.0.0.1:8000/
```

## Tests

```powershell
py -3.11 -m pytest
node --check frontend\js\app.js
```

## Deployment

This repo includes `render.yaml` for Render deployment.

Render command:

```text
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Limitations

- AASIST-L output is not calibrated for every real-world microphone/browser environment.
- Browser microphone processing can produce false positives.
- The current payment layer supports Razorpay Test Mode order creation, with mock fallback for local demos without keys.
- This project is Defense-only: it does not generate, clone, or improve deepfake voices.

## Project Structure

```text
app/
  anti_spoof.py      AASIST-L inference and signal shaping
  assessment.py      Composes voice, risk, and policy
  risk_engine.py     Explainable transaction risk scoring
  policy_engine.py   Decision policy
  payment.py         Mock Razorpay-style payment state
frontend/
  index.html         Payment-first demo UI
  js/app.js          Recording, payment creation, verification rendering
scripts/
  evaluate_aasist.py
  evaluate_aasist_2021.py
tests/
  pytest coverage for model semantics, risk, policy, payment, docs, UI integrity
```
