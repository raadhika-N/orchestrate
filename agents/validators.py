from __future__ import annotations
from typing import Any
from backend.core.logging import get_logger
from agents.tools.submit_claim_review import (
    CLAIM_STATUS_VALUES,
    ISSUE_TYPE_VALUES,
    OBJECT_PART_VALUES,
    SAFE_FALLBACK_RESPONSE,
    SEVERITY_VALUES,
)

logger = get_logger(__name__)

ALLOWED_RISK_FLAGS = {
    "none",
    "blurry_image",
    "cropped_or_obstructed",
    "low_light_or_glare",
    "wrong_angle",
    "wrong_object",
    "wrong_object_part",
    "damage_not_visible",
    "claim_mismatch",
    "possible_manipulation",
    "non_original_image",
    "text_instruction_present",
    "user_history_risk",
    "manual_review_required",
}


def _fix_boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)


def _fix_enum(value: Any, allowed: list[str], field_name: str, fallback: str) -> str:
    if not value:
        logger.warning("Field %r is empty. Using fallback %r.", field_name, fallback)
        return fallback
    val = str(value).strip().lower()
    if val in allowed:
        return val
    logger.warning(
        "Field %r has invalid value %r. Using fallback %r.",
        field_name, value, fallback,
    )
    return fallback


def _fix_risk_flags(value: Any) -> str:
    if not value:
        return "none"
    raw = str(value).strip()
    if raw.lower() == "none":
        return "none"
    flags = [f.strip().lower() for f in raw.split(";") if f.strip()]
    seen: set[str] = set()
    valid = []
    for f in flags:
        if f in ALLOWED_RISK_FLAGS and f not in seen:
            valid.append(f)
            seen.add(f)
    invalid = [f for f in flags if f not in ALLOWED_RISK_FLAGS]
    if invalid:
        logger.warning("Removing invalid risk_flags: %s", invalid)
    return ";".join(valid) if valid else "none"


def validate_and_repair(response: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(response, dict):
        logger.error("Model response is not a dict. Returning safe fallback.")
        return {**SAFE_FALLBACK_RESPONSE}

    try:
        return {
            "evidence_standard_met": _fix_boolean(
                response.get("evidence_standard_met", False)
            ),
            "evidence_standard_met_reason": str(
                response.get("evidence_standard_met_reason", "No reason provided.")
            ).strip() or "No reason provided.",
            "risk_flags": _fix_risk_flags(response.get("risk_flags", "none")),
            "issue_type": _fix_enum(
                response.get("issue_type"), ISSUE_TYPE_VALUES, "issue_type", "unknown"
            ),
            "object_part": _fix_enum(
                response.get("object_part"), OBJECT_PART_VALUES, "object_part", "unknown"
            ),
            "claim_status": _fix_enum(
                response.get("claim_status"), CLAIM_STATUS_VALUES,
                "claim_status", "not_enough_information"
            ),
            "claim_status_justification": str(
                response.get("claim_status_justification", "No justification provided.")
            ).strip() or "No justification provided.",
            "supporting_image_ids": str(
                response.get("supporting_image_ids", "none")
            ).strip() or "none",
            "valid_image": _fix_boolean(response.get("valid_image", False)),
            "severity": _fix_enum(
                response.get("severity"), SEVERITY_VALUES, "severity", "unknown"
            ),
        }
    except Exception as exc:
        logger.error("validate_and_repair failed: %s. Returning safe fallback.", exc)
        return {**SAFE_FALLBACK_RESPONSE}