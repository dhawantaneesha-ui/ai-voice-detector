# VoxGuard Evaluation

VoxGuard reports anti-spoofing performance honestly because the Buildathon Track 02 bar asks for measured precision, recall, and false-positive cost.

## AASIST-L Benchmarks

| Dataset | Samples | Precision | Recall | F1 | Accuracy | FPR | Latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ASVspoof2019 LA | 200 balanced | 1.000 | 0.910 | 0.953 | 0.955 | 0.000 | mean ~530 ms, p95 ~646 ms |
| ASVspoof2021 LA | 200 balanced | 0.770 | 0.970 | 0.858 | 0.840 | 0.290 | mean ~535-760 ms depending on execution path |

## False-Positive Cost

The ASVspoof2021 LA run produced an observed false-positive rate of `0.29`. At product scale, that means roughly **290 / 1000** genuine users could be challenged if the anti-spoof model were used as a standalone blocker.

VoxGuard avoids that unsafe product behavior by routing suspicious or uncertain voice signals through the transaction risk engine and policy engine.

## Browser Microphone Behavior

Real browser microphone recordings may be affected by device hardware, echo cancellation, noise suppression, browser capture settings, and resampling. In local testing, a genuine voice saying "I authorize this payment" was sometimes assigned a very high spoof signal by AASIST-L.

This is not hidden in the demo. The UI labels the value as a model signal and not calibrated probability. Low-value known-context payments with suspicious voice signals can be allowed, while higher-value or riskier transactions are stepped up, reviewed, or rejected.

## Reproducibility

Evaluation scripts:

```text
scripts/evaluate_aasist.py
scripts/evaluate_aasist_2021.py
scripts/threshold_sweep.py
```

Stored reports:

```text
reports/aasist_eval_200.json
reports/aasist_2021_eval_200.json
reports/aasist_2021_product_eval.json
```

## Limitations

- Metrics from ASVspoof datasets do not guarantee identical performance on browser microphone recordings.
- Model scores are not calibrated fraud probabilities.
- The current system demonstrates a risk workflow, not production-ready payment orchestration.
