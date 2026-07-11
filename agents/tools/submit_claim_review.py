from __future__ import annotations


CLAIM_STATUS_VALUES = ["supported", "contradicted", "not_enough_information"]

ISSUE_TYPE_VALUES = [
    "dent", "scratch", "crack", "glass_shatter", "broken_part",
    "missing_part", "torn_packaging", "crushed_packaging",
    "water_damage", "stain", "none", "unknown",
]

OBJECT_PART_VALUES = [
    "front_bumper", "rear_bumper", "door", "hood", "windshield",
    "side_mirror", "headlight", "taillight", "fender", "quarter_panel",
    "screen", "keyboard", "trackpad", "hinge", "lid", "corner", "port",
    "box", "package_corner", "package_side", "seal", "label", "contents", "item",
    "base", "body", "unknown",
]

SEVERITY_VALUES = ["none", "low", "medium", "high", "unknown"]


def get_response_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "evidence_standard_met": {
                "type": "boolean",
                "description": "True if the image set is sufficient to evaluate the claim.",
            },
            "evidence_standard_met_reason": {
                "type": "string",
                "description": "Short reason for the evidence standard decision.",
            },
            "risk_flags": {
                "type": "string",
                "description": (
                    "Semicolon-separated risk flags or the single string none. "
                    "Allowed values: blurry_image, cropped_or_obstructed, "
                    "low_light_or_glare, wrong_angle, wrong_object, "
                    "wrong_object_part, damage_not_visible, claim_mismatch, "
                    "possible_manipulation, non_original_image, "
                    "text_instruction_present, user_history_risk, "
                    "manual_review_required."
                ),
            },
            "issue_type": {
                "type": "string",
                "enum": ISSUE_TYPE_VALUES,
            },
            "object_part": {
                "type": "string",
                "enum": OBJECT_PART_VALUES,
            },
            "claim_status": {
                "type": "string",
                "enum": CLAIM_STATUS_VALUES,
            },
            "claim_status_justification": {
                "type": "string",
                "description": "Concise image-grounded explanation referencing image IDs.",
            },
            "supporting_image_ids": {
                "type": "string",
                "description": "Semicolon-separated image IDs or none.",
            },
            "valid_image": {
                "type": "boolean",
                "description": "False if any submitted image is completely unusable.",
            },
            "severity": {
                "type": "string",
                "enum": SEVERITY_VALUES,
            },
        },
        "required": [
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
        ],
    }


SAFE_FALLBACK_RESPONSE: dict = {
    "evidence_standard_met": False,
    "evidence_standard_met_reason": "Could not parse model response. Manual review required.",
    "risk_flags": "manual_review_required",
    "issue_type": "unknown",
    "object_part": "unknown",
    "claim_status": "not_enough_information",
    "claim_status_justification": "Automated review failed. Flagged for manual review.",
    "supporting_image_ids": "none",
    "valid_image": False,
    "severity": "unknown",
}