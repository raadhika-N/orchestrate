from __future__ import annotations
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from backend.core.logging import configure_logging, get_logger

logger = get_logger(__name__)

EVALUATABLE_FIELDS = [
    "claim_status",
    "issue_type",
    "object_part",
    "severity",
    "evidence_standard_met",
    "valid_image",
]

SAMPLE_CLAIMS_PATH = Path("dataset/sample_claims.csv")
PREDICTED_OUTPUT_PATH = Path("output/sample_output.csv")
REPORT_PATH = Path("evaluation/evaluation_report.md")


def _safe_str(val) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip().lower()


def compute_field_accuracy(ground_truth, predictions, field):
    if field not in ground_truth.columns:
        return {"field": field, "available": False}
    if field not in predictions.columns:
        return {"field": field, "available": False}

    total = len(ground_truth)
    correct = 0
    mismatches = []

    for i in range(total):
        expected = _safe_str(ground_truth.iloc[i].get(field))
        predicted = _safe_str(predictions.iloc[i].get(field))
        if expected == predicted:
            correct += 1
        else:
            mismatches.append({
                "row": i,
                "user_id": _safe_str(ground_truth.iloc[i].get("user_id", "")),
                "expected": expected,
                "predicted": predicted,
            })

    accuracy = correct / total if total > 0 else 0.0
    return {
        "field": field,
        "available": True,
        "total": total,
        "correct": correct,
        "accuracy": accuracy,
        "mismatches": mismatches,
    }


def generate_report(results, total_claims):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    primary = next((r for r in results if r["field"] == "claim_status"), None)
    primary_accuracy = primary["accuracy"] if primary and primary.get("available") else 0.0

    lines = [
        "# Evaluation Report",
        "",
        f"Generated: {now}",
        f"Total claims evaluated: {total_claims}",
        "",
        "---",
        "",
        "## Overall Accuracy",
        "",
        f"**Primary metric (claim_status): {primary_accuracy:.1%}**",
        "",
        "| Field | Accuracy | Correct | Total |",
        "|---|---|---|---|",
    ]

    for r in results:
        if not r.get("available"):
            lines.append(f"| {r['field']} | N/A | — | — |")
        else:
            lines.append(
                f"| {r['field']} | {r['accuracy']:.1%} "
                f"| {r['correct']} | {r['total']} |"
            )

    lines += ["", "---", "", "## Mismatch Analysis", ""]

    for r in results:
        if not r.get("available") or not r.get("mismatches"):
            continue
        lines.append(f"### {r['field']} — {len(r['mismatches'])} mismatches")
        lines.append("")
        lines.append("| Row | User ID | Expected | Predicted |")
        lines.append("|---|---|---|---|")
        for m in r["mismatches"]:
            lines.append(
                f"| {m['row']} | {m['user_id']} "
                f"| {m['expected']} | {m['predicted']} |"
            )
        lines.append("")

    lines += [
        "---",
        "",
        "## Operational Analysis",
        "",
        f"- Model calls made: approximately {total_claims} (minus cache hits)",
        "- Caching: enabled — reruns cost zero additional API calls",
        "- Rate limiting: 1 second delay between calls",
        "- Safe fallback: failed calls return not_enough_information",
        "- Retry strategy: 3 attempts with exponential backoff",
        "",
        "## Cost Estimate",
        "",
        "- Groq Llama 4 Scout: free tier",
        f"- Estimated tokens: ~{total_claims * 2300:,}",
        "- Cost: $0.00 (free tier)",
        "",
    ]

    return "\n".join(lines)


def main() -> None:
    configure_logging("INFO")

    if not PREDICTED_OUTPUT_PATH.exists():
        logger.error("Run 'python scripts/run_sample.py' first.")
        sys.exit(1)

    ground_truth = pd.read_csv(SAMPLE_CLAIMS_PATH, dtype=str)
    predictions = pd.read_csv(PREDICTED_OUTPUT_PATH, dtype=str)

    total = min(len(ground_truth), len(predictions))
    ground_truth = ground_truth.iloc[:total]
    predictions = predictions.iloc[:total]

    results = []
    for field in EVALUATABLE_FIELDS:
        result = compute_field_accuracy(ground_truth, predictions, field)
        if result.get("available"):
            logger.info(
                "  %-25s accuracy=%.1f%% (%d/%d)",
                field, result["accuracy"] * 100,
                result["correct"], result["total"],
            )
        results.append(result)

    report = generate_report(results, total)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")

    logger.info("Report written to %s", REPORT_PATH)
    print("\n" + report)


if __name__ == "__main__":
    main()