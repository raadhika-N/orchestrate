from __future__ import annotations
from pathlib import Path
from typing import Any
from backend.core.config import Settings, get_settings
from backend.core.logging import get_logger
from backend.services.data_loader import DatasetBundle, get_user_history
from backend.services.image_service import validate_images
from agents.prompts.claim_context_template import build_claim_context
from agents.vision_engine import run_claim_review
from agents.validators import validate_and_repair
from agents.risk_rules import compute_history_risk_flags, merge_risk_flags
from agents.cache import get_cached_response, set_cached_response
from agents.tools.submit_claim_review import SAFE_FALLBACK_RESPONSE

logger = get_logger(__name__)


def process_claim(
    claim: dict[str, Any],
    bundle: DatasetBundle,
    settings: Settings | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    if settings is None:
        settings = get_settings()

    user_id = claim.get("user_id", "unknown")
    claim_object = (claim.get("claim_object") or "").lower()
    image_paths_field = claim.get("image_paths")
    user_claim = claim.get("user_claim") or ""

    logger.info("Processing claim for user=%s object=%s", user_id, claim_object)

    # Step 1: Resolve images
    valid_images, missing_images = validate_images(settings.dataset_dir, image_paths_field)

    if missing_images:
        logger.warning("Missing images for user=%s: %s", user_id,
            [r.relative_path for r in missing_images])

    if not valid_images:
        logger.error("No valid images for user=%s. Returning fallback.", user_id)
        return _build_output_row(
            claim=claim,
            model_result={**SAFE_FALLBACK_RESPONSE},
            extra_risk_flags=["damage_not_visible"],
        )

    image_ids = [r.image_id for r in valid_images]
    image_paths = [r.absolute_path for r in valid_images]

    # Step 2: User history
    user_history = get_user_history(bundle.user_history_index, user_id)

    # Step 3: Evidence requirements
    all_reqs = [
        row for key, rows in bundle.evidence_requirements_index.items()
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

    # Step 4: Build context
    claim_context_text = build_claim_context(
        claim_object=claim_object,
        user_claim=user_claim,
        image_ids=image_ids,
        user_history=user_history,
        evidence_requirements=unique_reqs,
    )

    # Step 5: Check cache
    cache_kwargs = {"db_path": db_path} if db_path else {}
    cached = get_cached_response(
        claim_context_text=claim_context_text,
        image_paths=image_paths,
        model_name=settings.model_name,
        **cache_kwargs,
    )

    if cached:
        logger.info("Cache HIT for user=%s — skipping API call.", user_id)
        raw_result = cached
    else:
        # Step 6: Call Groq
        raw_result = run_claim_review(
            claim_context_text=claim_context_text,
            image_paths=image_paths,
            settings=settings,
        )
        # Step 7: Cache it
        set_cached_response(
            claim_context_text=claim_context_text,
            image_paths=image_paths,
            model_name=settings.model_name,
            response=raw_result,
            **cache_kwargs,
        )

    # Step 8: Validate and repair
    validated = validate_and_repair(raw_result)

    # Step 9: History risk rules
    history_flags = compute_history_risk_flags(user_history)
    if history_flags:
        validated["risk_flags"] = merge_risk_flags(
            validated["risk_flags"], history_flags
        )

    # Step 10: Build output row
    return _build_output_row(claim=claim, model_result=validated)


def _build_output_row(
    claim: dict[str, Any],
    model_result: dict[str, Any],
    extra_risk_flags: list[str] | None = None,
) -> dict[str, Any]:
    risk_flags = model_result.get("risk_flags", "none")
    if extra_risk_flags:
        risk_flags = merge_risk_flags(risk_flags, extra_risk_flags)

    return {
        "user_id": claim.get("user_id", ""),
        "image_paths": claim.get("image_paths", ""),
        "user_claim": claim.get("user_claim", ""),
        "claim_object": claim.get("claim_object", ""),
        "evidence_standard_met": model_result.get("evidence_standard_met", False),
        "evidence_standard_met_reason": model_result.get("evidence_standard_met_reason", ""),
        "risk_flags": risk_flags,
        "issue_type": model_result.get("issue_type", "unknown"),
        "object_part": model_result.get("object_part", "unknown"),
        "claim_status": model_result.get("claim_status", "not_enough_information"),
        "claim_status_justification": model_result.get("claim_status_justification", ""),
        "supporting_image_ids": model_result.get("supporting_image_ids", "none"),
        "valid_image": model_result.get("valid_image", False),
        "severity": model_result.get("severity", "unknown"),
    }