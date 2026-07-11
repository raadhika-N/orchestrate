"""
Phase 2 tests. All run fully offline — no Gemini API key needed.
Run with: pytest tests/test_vision_engine.py -v
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from agents.prompts.claim_context_template import build_claim_context
from agents.prompts.system_prompt import _load_system_prompt
from agents.tools.submit_claim_review import (
    CLAIM_STATUS_VALUES,
    ISSUE_TYPE_VALUES,
    OBJECT_PART_VALUES,
    SAFE_FALLBACK_RESPONSE,
    SEVERITY_VALUES,
    get_response_schema,
)
from agents.vision_engine import run_claim_review

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _make_settings():
    from backend.core.config import Settings
    return Settings(
        groq_api_key="test_key_not_real",
        model_name="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0.0,
        max_output_tokens=1024,
        image_max_dimension=256,
        image_jpeg_quality=70,
        max_images_per_request=5,
        max_retries=2,
        retry_delay_seconds=0.0,
    )


def _good_response() -> dict:
    return {
        "evidence_standard_met": True,
        "evidence_standard_met_reason": "One clear image provided.",
        "risk_flags": "none",
        "issue_type": "dent",
        "object_part": "door",
        "claim_status": "supported",
        "claim_status_justification": "img_1 clearly shows a dent on the door.",
        "supporting_image_ids": "img_1",
        "valid_image": True,
        "severity": "medium",
    }


def _base_history() -> dict:
    return {
        "user_id": "u_001",
        "past_claim_count": "3",
        "accept_claim": "2",
        "manual_review_claim": "1",
        "rejected_claim": "0",
        "last_90_days_claim_count": "1",
        "history_flags": "none",
        "history_summary": "Reliable claimant.",
    }


# ── Schema tests ──────────────────────────────────────────────────────────

def test_schema_has_all_required_fields():
    schema = get_response_schema()
    expected = {
        "evidence_standard_met", "evidence_standard_met_reason",
        "risk_flags", "issue_type", "object_part", "claim_status",
        "claim_status_justification", "supporting_image_ids",
        "valid_image", "severity",
    }
    assert set(schema["required"]) == expected


def test_claim_status_values_match_spec():
    assert set(CLAIM_STATUS_VALUES) == {
        "supported", "contradicted", "not_enough_information"
    }


def test_issue_type_contains_expected_values():
    for v in ["dent", "scratch", "crack", "water_damage", "none", "unknown"]:
        assert v in ISSUE_TYPE_VALUES


def test_severity_values_match_spec():
    assert set(SEVERITY_VALUES) == {"none", "low", "medium", "high", "unknown"}


def test_object_part_contains_all_three_object_types():
    assert "front_bumper" in OBJECT_PART_VALUES
    assert "screen" in OBJECT_PART_VALUES
    assert "box" in OBJECT_PART_VALUES


def test_safe_fallback_has_all_required_keys():
    schema = get_response_schema()
    for key in schema["required"]:
        assert key in SAFE_FALLBACK_RESPONSE


def test_safe_fallback_uses_cautious_values():
    assert SAFE_FALLBACK_RESPONSE["claim_status"] == "not_enough_information"
    assert SAFE_FALLBACK_RESPONSE["evidence_standard_met"] is False
    assert SAFE_FALLBACK_RESPONSE["valid_image"] is False
    assert "manual_review_required" in SAFE_FALLBACK_RESPONSE["risk_flags"]


# ── System prompt tests ───────────────────────────────────────────────────

def test_system_prompt_loads():
    prompt = _load_system_prompt()
    assert len(prompt) > 100


def test_system_prompt_contains_anti_injection_rule():
    prompt = _load_system_prompt()
    assert "text_instruction_present" in prompt


def test_system_prompt_lists_all_claim_status_values():
    prompt = _load_system_prompt()
    for v in CLAIM_STATUS_VALUES:
        assert v in prompt


def test_system_prompt_mentions_image_primacy():
    prompt = _load_system_prompt()
    assert "primary" in prompt.lower()


# ── Claim context template tests ──────────────────────────────────────────

def test_context_contains_claim_object():
    ctx = build_claim_context(
        claim_object="car",
        user_claim="Front bumper dented.",
        image_ids=["img_1"],
        user_history=_base_history(),
        evidence_requirements=[],
    )
    assert "car" in ctx


def test_context_contains_image_ids():
    ctx = build_claim_context(
        claim_object="laptop",
        user_claim="Screen cracked.",
        image_ids=["img_1", "img_2"],
        user_history=_base_history(),
        evidence_requirements=[],
    )
    assert "img_1" in ctx
    assert "img_2" in ctx


def test_context_contains_user_claim_text():
    ctx = build_claim_context(
        claim_object="package",
        user_claim="The box arrived completely crushed.",
        image_ids=["img_1"],
        user_history=_base_history(),
        evidence_requirements=[],
    )
    assert "crushed" in ctx


def test_context_contains_evidence_requirements_when_provided():
    reqs = [{
        "applies_to": "dent",
        "minimum_image_evidence": "One clear panel photo required."
    }]
    ctx = build_claim_context(
        claim_object="car",
        user_claim="Dent on hood.",
        image_ids=["img_1"],
        user_history=_base_history(),
        evidence_requirements=reqs,
    )
    assert "One clear panel photo" in ctx


def test_context_handles_empty_evidence_requirements():
    ctx = build_claim_context(
        claim_object="car",
        user_claim="Some damage.",
        image_ids=["img_1"],
        user_history=_base_history(),
        evidence_requirements=[],
    )
    assert "No specific evidence requirements" in ctx


def test_context_contains_history_flags():
    history = _base_history()
    history["history_flags"] = "frequent_claimant"
    ctx = build_claim_context(
        claim_object="car",
        user_claim="Scratch on door.",
        image_ids=["img_1"],
        user_history=history,
        evidence_requirements=[],
    )
    assert "frequent_claimant" in ctx


# ── Vision engine tests (mocked — no real API call) ───────────────────────

def test_returns_valid_response_on_success():
    with patch("agents.vision_engine._call_groq", return_value=_good_response()):
        result = run_claim_review(
            claim_context_text="Test context",
            image_paths=[FIXTURES_DIR / "images" / "case_001" / "img_1.jpg"],
            settings=_make_settings(),
        )
    assert result["claim_status"] == "supported"
    assert result["issue_type"] == "dent"
    assert result["severity"] == "medium"


def test_returns_safe_fallback_on_api_failure():
    with patch("agents.vision_engine._call_groq", side_effect=RuntimeError("API down")):
        result = run_claim_review(
            claim_context_text="Test context",
            image_paths=[FIXTURES_DIR / "images" / "case_001" / "img_1.jpg"],
            settings=_make_settings(),
        )
    assert result == {**SAFE_FALLBACK_RESPONSE}


def test_raises_on_missing_api_key():
    from backend.core.config import Settings
    no_key_settings = Settings(groq_api_key="")
    with pytest.raises(EnvironmentError, match="GROQ_API_KEY"):
        run_claim_review(
            claim_context_text="Test context",
            image_paths=[FIXTURES_DIR / "images" / "case_001" / "img_1.jpg"],
            settings=no_key_settings,
        )


def test_image_cap_is_enforced():
    from backend.core.config import Settings
    from agents.vision_engine import _build_contents
    cap_settings = Settings(
        groq_api_key="test_key",
        max_images_per_request=2,
        retry_delay_seconds=0.0,
    )
    images = [FIXTURES_DIR / "images" / "case_001" / "img_1.jpg"] * 4
    contents = _build_contents(
        claim_context_text="ctx",
        image_paths=images,
        settings=cap_settings,
    )
    # Groq format: [{"role": "user", "content": [text_part, img_part, img_part]}]
    # content[0] is the user message, content[0]["content"] is the parts list
    parts = contents[0]["content"]
    image_parts = [p for p in parts if p.get("type") == "image_url"]
    assert len(image_parts) == 2