from __future__ import annotations
from typing import Any


def build_claim_context(
    *,
    claim_object: str,
    user_claim: str,
    image_ids: list[str],
    user_history: dict[str, Any],
    evidence_requirements: list[dict[str, Any]],
) -> str:
    history_block = _format_history(user_history)
    evidence_block = _format_evidence_requirements(evidence_requirements)
    image_id_list = ", ".join(image_ids) if image_ids else "none submitted"

    return f"""## Claim details

Object type: {claim_object}

User claim:
{user_claim.strip()}

## Images submitted

The images attached to this message are the evidence.
Their IDs are: {image_id_list}
When writing your justification use these exact IDs.

## Minimum evidence requirements

{evidence_block}

## Claimant history

{history_block}

## Your task

Inspect the images carefully against the user claim.
Apply the decision rules from your instructions.
Return a single JSON object with all required fields
using only the allowed values.
"""


def _format_history(user_history: dict[str, Any]) -> str:
    return (
        f"User ID: {user_history.get('user_id', 'unknown')}\n"
        f"Total past claims: {user_history.get('past_claim_count', '0')} "
        f"(accepted: {user_history.get('accept_claim', '0')}, "
        f"manual review: {user_history.get('manual_review_claim', '0')}, "
        f"rejected: {user_history.get('rejected_claim', '0')})\n"
        f"Claims in last 90 days: {user_history.get('last_90_days_claim_count', '0')}\n"
        f"History flags: {user_history.get('history_flags', 'none')}\n"
        f"Summary: {user_history.get('history_summary', 'No prior claim history on file.')}"
    )


def _format_evidence_requirements(requirements: list[dict[str, Any]]) -> str:
    if not requirements:
        return "No specific evidence requirements found for this object and issue combination."
    lines = []
    for req in requirements:
        applies_to = req.get("applies_to", "unknown")
        minimum = req.get("minimum_image_evidence", "Not specified.")
        lines.append(f"- [{applies_to}] {minimum}")
    return "\n".join(lines)