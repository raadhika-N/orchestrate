from agents.validators import validate_and_repair, _fix_boolean, _fix_risk_flags
from agents.tools.submit_claim_review import SAFE_FALLBACK_RESPONSE


def _good_response():
    return {
        "evidence_standard_met": True,
        "evidence_standard_met_reason": "Clear image provided.",
        "risk_flags": "none",
        "issue_type": "dent",
        "object_part": "door",
        "claim_status": "supported",
        "claim_status_justification": "img_1 shows a dent.",
        "supporting_image_ids": "img_1",
        "valid_image": True,
        "severity": "medium",
    }


def test_valid_response_passes_through():
    result = validate_and_repair(_good_response())
    assert result["claim_status"] == "supported"
    assert result["issue_type"] == "dent"
    assert result["severity"] == "medium"
    assert result["evidence_standard_met"] is True


def test_string_true_is_fixed():
    resp = _good_response()
    resp["evidence_standard_met"] = "true"
    resp["valid_image"] = "True"
    result = validate_and_repair(resp)
    assert result["evidence_standard_met"] is True
    assert result["valid_image"] is True


def test_string_false_is_fixed():
    resp = _good_response()
    resp["evidence_standard_met"] = "false"
    resp["valid_image"] = "False"
    result = validate_and_repair(resp)
    assert result["evidence_standard_met"] is False
    assert result["valid_image"] is False


def test_invalid_claim_status_falls_back():
    resp = _good_response()
    resp["claim_status"] = "approved"
    result = validate_and_repair(resp)
    assert result["claim_status"] == "not_enough_information"


def test_invalid_issue_type_falls_back():
    resp = _good_response()
    resp["issue_type"] = "explosion"
    result = validate_and_repair(resp)
    assert result["issue_type"] == "unknown"


def test_invalid_severity_falls_back():
    resp = _good_response()
    resp["severity"] = "critical"
    result = validate_and_repair(resp)
    assert result["severity"] == "unknown"


def test_invalid_risk_flags_are_removed():
    resp = _good_response()
    resp["risk_flags"] = "blurry_image;made_up_flag;wrong_angle"
    result = validate_and_repair(resp)
    flags = result["risk_flags"].split(";")
    assert "made_up_flag" not in flags
    assert "blurry_image" in flags
    assert "wrong_angle" in flags


def test_non_dict_returns_safe_fallback():
    result = validate_and_repair("not a dict")
    assert result == {**SAFE_FALLBACK_RESPONSE}


def test_empty_dict_returns_safe_values():
    result = validate_and_repair({})
    assert result["claim_status"] == "not_enough_information"
    assert result["severity"] == "unknown"


def test_fix_boolean_handles_various_inputs():
    assert _fix_boolean(True) is True
    assert _fix_boolean(False) is False
    assert _fix_boolean("true") is True
    assert _fix_boolean("false") is False
    assert _fix_boolean("1") is True


def test_fix_risk_flags_handles_none():
    assert _fix_risk_flags("none") == "none"
    assert _fix_risk_flags("") == "none"
    assert _fix_risk_flags(None) == "none"


def test_fix_risk_flags_deduplicates():
    result = _fix_risk_flags("blurry_image;blurry_image;wrong_angle")
    flags = result.split(";")
    assert flags.count("blurry_image") == 1