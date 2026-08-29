import json
import numpy as np


REPORT = "reports/aasist_2021_product_eval.json"


def evaluate_threshold(scores, labels, threshold):

    genuine_total = 0
    genuine_false_block = 0

    spoof_total = 0
    spoof_caught = 0

    for score, label in zip(scores, labels):

        prediction = 1 if score >= threshold else 0

        # label:
        # 0 = genuine
        # 1 = spoof

        if label == 0:
            genuine_total += 1

            if prediction == 1:
                genuine_false_block += 1

        else:
            spoof_total += 1

            if prediction == 1:
                spoof_caught += 1


    return {
        "threshold": threshold,

        "spoof_catch_rate": round(
            spoof_caught / spoof_total,
            3,
        ),

        "false_block_rate": round(
            genuine_false_block / genuine_total,
            3,
        ),

        "false_blocks_per_1000_users": round(
            (genuine_false_block / genuine_total) * 1000,
            1,
        ),
    }



with open(REPORT) as f:
    data = json.load(f)


scores = data["scores"]
labels = data["labels"]


print("\nThreshold sweep\n")


for threshold in np.arange(
    0.5,
    1.0,
    0.05,
):

    result = evaluate_threshold(
        scores,
        labels,
        round(float(threshold),2),
    )

    print(result)