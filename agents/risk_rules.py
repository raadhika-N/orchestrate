from __future__ import annotations
from typing import Any
from backend.core.logging import get_logger

logger = get_logger(__name__)

REJECTED_CLAIM_RATE_THRESHOLD = 0.30
LAST_90_DAYS_COUNT_THRESHOLD = 3
TOTAL_CLAIM_COUNT_THRESHOLD = 10


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value or 0)
    except (ValueError, TypeError):
        return default


def compute_history_risk_flags(user_history: dict[str, Any]) -> list[str]:
    flags: list[str] = []

    past_claims = _safe_int(user_history.get("past_claim_count"))
    rejected = _safe_int(user_history.get("rejected_claim"))
    last_90 = _safe_int(user_history.get("last_90_days_claim_count"))
    history_flags = str(user_history.get("history_flags") or "").lower()

    if past_claims > 0:
        rejection_rate = rejected / past_claims
        if rejection_rate >= REJECTED_CLAIM_RATE_THRESHOLD:
            flags.append("user_history_risk")

    if last_90 >= LAST_90_DAYS_COUNT_THRESHOLD:
        if "user_history_risk" not in flags:
            flags.append("user_history_risk")

    if history_flags and history_flags != "none":
        if "user_history_risk" not in flags:
            flags.append("user_history_risk")

    if past_claims >= TOTAL_CLAIM_COUNT_THRESHOLD and rejected > 0:
        if "manual_review_required" not in flags:
            flags.append("manual_review_required")

    return flags


def merge_risk_flags(model_flags: str, history_flags: list[str]) -> str:
    existing: list[str] = []
    if model_flags and model_flags.lower() != "none":
        existing = [f.strip() for f in model_flags.split(";") if f.strip()]

    combined = existing.copy()
    for flag in history_flags:
        if flag not in combined:
            combined.append(flag)

    return ";".join(combined) if combined else "none"