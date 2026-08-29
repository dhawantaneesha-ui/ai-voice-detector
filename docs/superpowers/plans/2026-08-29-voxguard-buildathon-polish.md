# VoxGuard Buildathon Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing detector into a Razorpay Buildathon Track 02 AI Risk Manager submission.

**Architecture:** Keep AASIST-L as the primary anti-spoof model, but present its output as an uncalibrated voice authenticity signal. The payment decision remains a composition of voice signal, transaction context, risk scoring, and policy action.

**Tech Stack:** Python 3.11, FastAPI, PyTorch, librosa, vanilla HTML/CSS/JavaScript, pytest.

**Spec:** User-provided Razorpay Track 02 brief and VoxGuard project requirements in the conversation.

## Global Constraints

- Do not fake HUMAN/AI predictions.
- Do not claim calibrated probabilities.
- Demo scenario buttons only change transaction context.
- Preserve honest benchmark metrics and false-positive costs.
- Keep the product defense-only.
- Use tests before behavior changes where practical.

---

### Task 1: Submission Documentation

**Files:**
- Modify: `README.md`
- Create: `docs/demo-script.md`
- Create: `docs/architecture.md`
- Create: `docs/evaluation.md`
- Test: `tests/test_project_docs.py`

**Interfaces:**
- Consumes: Existing benchmark reports in `reports/`
- Produces: Buildathon-ready docs that explain problem, architecture, metrics, limitations, and demo flow

- [ ] Write failing tests asserting README contains Track 02 positioning, honest metrics, false-positive cost, defense-only framing, and no generic "AI Voice Detector" H1.
- [ ] Run `py -3.11 -m pytest tests/test_project_docs.py` and confirm failures.
- [ ] Update README and docs with concrete VoxGuard submission narrative.
- [ ] Rerun docs tests and confirm pass.

### Task 2: Payment-First UI Narrative

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/js/app.js`
- Test: `tests/test_frontend_integrity.py`

**Interfaces:**
- Consumes: `/create-payment` and `/verify-payment` responses
- Produces: A frontend where the first screen is voice authorization for a payment request, with AASIST displayed as a signal and final decision displayed as the primary result

- [ ] Add failing frontend integrity tests for payment-first copy, limitation note, and readable scenario descriptions.
- [ ] Run `py -3.11 -m pytest tests/test_frontend_integrity.py` and confirm failures.
- [ ] Update UI copy and result explanation without changing backend model outputs.
- [ ] Run `node --check frontend/js/app.js` and frontend tests.

### Task 3: Final Verification

**Files:**
- Verify all touched files

**Interfaces:**
- Consumes: Complete repo state
- Produces: Running local demo and passing test suite

- [ ] Run `py -3.11 -m pytest`.
- [ ] Run `node --check frontend/js/app.js`.
- [ ] Check backend health at `http://127.0.0.1:8000/health`.
- [ ] Restart local servers if frontend cache version changes.
