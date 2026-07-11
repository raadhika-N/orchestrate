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
    "user_id", "image_paths", "user_claim", "claim_object",
    "evidence_standard_met", "evidence_standard_met_reason",
    "risk_flags", "issue_type", "object_part", "claim_status",
    "claim_status_justification", "supporting_image_ids",
    "valid_image", "severity",
]


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    logger.info("Loading dataset...")
    bundle = load_dataset_bundle(
        claims_path=settings.claims_path,
        sample_claims_path=settings.sample_claims_path,
        user_history_path=settings.user_history_path,
        evidence_requirements_path=settings.evidence_requirements_path,
    )

    claims = bundle.sample_claims
    logger.info("Processing %d sample claims...", len(claims))

    output_path = Path("output/sample_output.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results = []
    for i, claim in enumerate(claims):
        logger.info(
            "Processing claim %d/%d (user=%s)...",
            i + 1, len(claims), claim.get("user_id")
        )
        start = time.time()
        result = process_claim(claim, bundle, settings)
        elapsed = time.time() - start
        logger.info(
            "Claim %d done in %.1fs — status=%s",
            i + 1, elapsed, result.get("claim_status")
        )
        results.append(result)
        if i < len(claims) - 1:
            time.sleep(1.0)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    logger.info("Done! Written to %s", output_path)
    logger.info("Next: python evaluation/evaluate.py")


if __name__ == "__main__":
    main()