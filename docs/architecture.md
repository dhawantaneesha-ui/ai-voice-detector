# VoxGuard Architecture

VoxGuard is a payment-risk pipeline built around voice authorization.

## Flow

```text
Browser microphone or WAV upload
  -> FastAPI /verify-payment
  -> AASIST-L anti-spoof model
  -> voice authenticity signal
  -> transaction risk engine
  -> policy engine
  -> Razorpay Test Mode order or mock payment state
```

## Components

`app/anti_spoof.py`

Loads AASIST-L, resamples audio to 16 kHz mono, pads or truncates to 64,600 samples, and returns the model signal. Class `0` is spoof and class `1` is bona fide.

`app/risk_engine.py`

Converts voice and transaction context into an explainable risk score from 0 to 100. Risk factors include suspicious voice signal, uncertain voice signal, high-value payment, new device, new beneficiary, and high velocity.

`app/policy_engine.py`

Maps risk level and voice verdict into one bounded action: allow, step-up, review, or reject voice authorization.

`app/payment.py`

Creates a Razorpay Test Mode order when `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are configured. Without credentials, it falls back to a local mock so the demo remains runnable.

`frontend/`

Provides the payment-first demo experience: create payment, record voice authorization, run verification, and show the final decision with readable risk evidence.

## Design Principle

Voice authenticity is not treated as ground truth. A suspicious voice signal by itself can still allow a low-value trusted-context payment, while suspicious voice plus high-value or risky transaction context can trigger step-up, review, or voice authorization rejection.
