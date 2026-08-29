# VoxGuard Demo Script

## 30-Second Pitch

VoxGuard is an AI Risk Manager for voice-authorized payments. It protects merchants from AI/deepfake voice fraud by combining an anti-spoofing voice signal with transaction risk context. The system does not blindly block a payment because a model says "AI"; it decides whether to allow, step up, review, or reject voice authorization based on the full risk picture.

## 5-Minute Demo Flow

1. Start on the VoxGuard payment authorization page.
2. Show the payment request for INR 50,000.
3. Explain that the user is asked to say: "I authorize this payment."
4. Record live microphone audio or use the WAV fallback.
5. Submit the verification.
6. Show that AASIST-L produces a voice authenticity signal.
7. Show the transaction context: amount, device, beneficiary, and velocity.
8. Show the final policy decision.

If Razorpay test keys are configured, point out that the payment request is backed by Razorpay Test Mode Orders API. If keys are not configured, explain that the app uses a mock fallback while preserving the same risk decision flow.

## Safe-Context Example

Known device, known beneficiary, and low velocity produce a safer transaction context. If the pretrained model flags the browser microphone as suspicious, VoxGuard can still allow a low-value trusted payment rather than pretending the model is perfect or silently blocking the payment.

Expected decision for suspicious voice signal plus low-value safe context:

```text
Payment Authorized
```

## Attack Example

For the attack scenario, use the same INR 50,000 payment amount but switch the context to new device, new beneficiary, and high transaction velocity. Suspicious voice plus risky payment context creates critical risk.

Expected decision:

```text
Voice Authorization Rejected
```

## What To Say To Judges

The important design choice is that VoxGuard treats voice as one risk signal. The model has strong benchmark performance on ASVspoof2019 LA but a higher false-positive rate on ASVspoof2021 LA and browser microphone audio. That is why the product uses step-up and review states instead of claiming perfect fraud detection.
