"""
Runs the full pipeline on claims.csv and writes the final output.csv.

This is the actual hackathon submission script.
Run this AFTER running run_sample.py + evaluate.py to confirm accuracy.

Usage:
    python scripts/run_test.py
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.config import get_settings
from backend.core.logging import configure_logging, get_logger
from backend.services.data_loader import load_dataset_bundle
from backend.services.pipeline_runner import process_claim

logger = get_logger(__name__)

OUTPUT_COLUMNS = [
    "user_id",
    "image_paths",
    "user_claim",
    "claim_object",
    "evidence_standard_met",
    "evidence_standard_met_reason",
    "risk_flags",
    "issue_type",
    "object_part",
    "claim_status",
    "claim_status_justification",
    "supporting_image_ids",
    "valid_image",
    "severity",
]


def validate_output_row(row: dict, row_num: int) -> list[str]:
    """
    Checks one output row for issues before writing to CSV.
    Returns list of warning strings. Empty list means row is clean.
    """
    warnings = []

    # Check all required columns exist
    for col in OUTPUT_COLUMNS:
        if col not in row:
            warnings.append(f"Row {row_num}: missing column '{col}'")

    # Check enum values
    valid_claim_status = {"supported", "contradicted", "not_enough_information"}
    if str(row.get("claim_status", "")).lower() not in valid_claim_status:
        warnings.append(
            f"Row {row_num}: invalid claim_status='{row.get('claim_status')}'"
        )

    valid_severity = {"none", "low", "medium", "high", "unknown"}
    if str(row.get("severity", "")).lower() not in valid_severity:
        warnings.append(
            f"Row {row_num}: invalid severity='{row.get('severity')}'"
        )

    # Check supporting_image_ids only references real image IDs
    image_paths = str(row.get("image_paths", ""))
    supporting = str(row.get("supporting_image_ids", "none"))
    if supporting.lower() != "none":
        real_ids = {
            Path(p.strip()).stem
            for p in image_paths.split(";")
            if p.strip()
        }
        claimed_ids = {s.strip() for s in supporting.split(";") if s.strip()}
        invalid_ids = claimed_ids - real_ids
        if invalid_ids:
            warnings.append(
                f"Row {row_num}: supporting_image_ids references "
                f"unknown IDs: {invalid_ids}"
            )

    return warnings


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    logger.info("=" * 50)
    logger.info("PHASE 4 — Generating output.csv")
    logger.info("=" * 50)

    # Load all dataset files
    logger.info("Loading dataset...")
    bundle = load_dataset_bundle(
        claims_path=settings.claims_path,
        sample_claims_path=settings.sample_claims_path,
        user_history_path=settings.user_history_path,
        evidence_requirements_path=settings.evidence_requirements_path,
    )

    claims = bundle.claims
    logger.info("Found %d claims to process.", len(claims))

    output_path = Path("output/output.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results = []
    all_warnings = []
    start_total = time.time()

    for i, claim in enumerate(claims):
        logger.info(
            "Processing claim %d/%d (user=%s, object=%s)...",
            i + 1, len(claims),
            claim.get("user_id"),
            claim.get("claim_object"),
        )

        claim_start = time.time()
        result = process_claim(claim, bundle, settings)
        claim_elapsed = time.time() - claim_start

        # Validate the output row
        row_warnings = validate_output_row(result, i)
        if row_warnings:
            for w in row_warnings:
                logger.warning(w)
            all_warnings.extend(row_warnings)

        logger.info(
            "  Done in %.1fs — status=%s severity=%s flags=%s",
            claim_elapsed,
            result.get("claim_status"),
            result.get("severity"),
            result.get("risk_flags"),
        )

        results.append(result)

        # Respect rate limits — 1 second between calls
        if i < len(claims) - 1:
            time.sleep(1.0)

    total_elapsed = time.time() - start_total

    # Write output.csv
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=OUTPUT_COLUMNS, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(results)

    # Summary
    logger.info("=" * 50)
    logger.info("DONE")
    logger.info("  Claims processed : %d", len(results))
    logger.info("  Total time       : %.1f seconds", total_elapsed)
    logger.info("  Avg per claim    : %.1f seconds", total_elapsed / len(results) if results else 0)
    logger.info("  Output written   : %s", output_path)
    logger.info("  Warnings         : %d", len(all_warnings))
    logger.info("=" * 50)

    if all_warnings:
        logger.warning("Warnings found — review before submitting:")
        for w in all_warnings:
            logger.warning("  %s", w)
    else:
        logger.info("All rows validated — output.csv is clean!")

    logger.info("Submission checklist:")
    logger.info("  [x] output.csv generated")
    logger.info("  [ ] Run: python evaluation/evaluate.py")
    logger.info("  [ ] Check evaluation/evaluation_report.md")
    logger.info("  [ ] Zip code/ folder for submission")


if __name__ == "__main__":
    main()