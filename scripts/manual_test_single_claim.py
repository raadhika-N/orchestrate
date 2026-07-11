"""
Run one claim from sample_claims.csv through Gemini and print the result.

Usage:
    python scripts/manual_test_single_claim.py
    python scripts/manual_test_single_claim.py --row 2
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.config import get_settings
from backend.core.logging import configure_logging, get_logger
from backend.services.data_loader import (
    build_evidence_requirement_index,
    get_user_history,
    load_claims,
    load_evidence_requirements,
    load_user_history,
)
from backend.services.image_service import validate_images
from agents.prompts.claim_context_template import build_claim_context
from agents.vision_engine import run_claim_review

logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row", type=int, default=0)
    args = parser.parse_args()

    settings = get_settings()
    configure_logging(settings.log_level)

    sample_claims = load_claims(settings.sample_claims_path)
    user_history_index = load_user_history(settings.user_history_path)
    evidence_requirements = load_evidence_requirements(settings.evidence_requirements_path)
    evidence_index = build_evidence_requirement_index(evidence_requirements)

    if args.row >= len(sample_claims):
        logger.error("Row %d does not exist. File has %d rows.", args.row, len(sample_claims))
        sys.exit(1)

    claim = sample_claims[args.row]

    print("\n" + "=" * 60)
    print(f"CLAIM ROW {args.row}")
    print("=" * 60)
    print(f"  user_id      : {claim['user_id']}")
    print(f"  claim_object : {claim['claim_object']}")
    print(f"  user_claim   : {claim['user_claim']}")
    print(f"  image_paths  : {claim['image_paths']}")
    if "claim_status" in claim:
        print(f"  expected     : {claim['claim_status']}")
    print()

    valid_images, missing_images = validate_images(
        settings.dataset_dir, claim.get("image_paths")
    )

    if missing_images:
        logger.warning(
            "Missing images: %s", [r.relative_path for r in missing_images]
        )

    if not valid_images:
        logger.error("No valid images found. Cannot call the model.")
        sys.exit(1)

    image_ids = [r.image_id for r in valid_images]
    image_paths = [r.absolute_path for r in valid_images]

    user_history = get_user_history(user_history_index, claim["user_id"])

    claim_object = (claim.get("claim_object") or "").lower()
    all_reqs = [
        row for key, rows in evidence_index.items()
        if key[0] == claim_object
        for row in rows
    ]
    seen_ids: set[str] = set()
    unique_reqs = []
    for req in all_reqs:
        rid = req.get("requirement_id", "")
        if rid not in seen_ids:
            seen_ids.add(rid)
            unique_reqs.append(req)

    claim_context_text = build_claim_context(
        claim_object=claim_object,
        user_claim=claim.get("user_claim") or "",
        image_ids=image_ids,
        user_history=user_history,
        evidence_requirements=unique_reqs,
    )

    logger.info("Calling Gemini with %d image(s)...", len(image_paths))

    result = run_claim_review(
        claim_context_text=claim_context_text,
        image_paths=image_paths,
        settings=settings,
    )

    print("GEMINI OUTPUT:")
    print(json.dumps(result, indent=2))
    print()

    if "claim_status" in claim:
        expected = claim["claim_status"]
        actual = result.get("claim_status", "unknown")
        match = "MATCH" if expected == actual else "MISMATCH"
        print(f"claim_status: {match} (expected={expected}, got={actual})")

    print("=" * 60)


if __name__ == "__main__":
    main()