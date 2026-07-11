from agents.risk_rules import compute_history_risk_flags, merge_risk_flags


def _make_history(**kwargs):
    base = {
        "user_id": "u_001",
        "past_claim_count": "0",
        "accept_claim": "0",
        "manual_review_claim": "0",
        "rejected_claim": "0",
        "last_90_days_claim_count": "0",
        "history_flags": "none",
        "history_summary": "No history.",
    }
    base.update(kwargs)
    return base


def test_clean_user_has_no_flags():
    history = _make_history(
        past_claim_count="3",
        rejected_claim="0",
        last_90_days_claim_count="1",
    )
    assert compute_history_risk_flags(history) == []


def test_high_rejection_rate_flags_risk():
    history = _make_history(past_claim_count="10", rejected_claim="5")
    flags = compute_history_risk_flags(history)
    assert "user_history_risk" in flags


def test_frequent_recent_claimant_flags_risk():
    history = _make_history(last_90_days_claim_count="4")
    flags = compute_history_risk_flags(history)
    assert "user_history_risk" in flags


def test_explicit_history_flag_triggers_risk():
    history = _make_history(history_flags="frequent_claimant")
    flags = compute_history_risk_flags(history)
    assert "user_history_risk" in flags


def test_high_volume_with_rejections_adds_manual_review():
    history = _make_history(past_claim_count="15", rejected_claim="3")
    flags = compute_history_risk_flags(history)
    assert "manual_review_required" in flags


def test_merge_flags_combines_correctly():
    result = merge_risk_flags("blurry_image;wrong_angle", ["user_history_risk"])
    assert "blurry_image" in result
    assert "wrong_angle" in result
    assert "user_history_risk" in result


def test_merge_flags_deduplicates():
    result = merge_risk_flags("user_history_risk", ["user_history_risk"])
    assert result.count("user_history_risk") == 1


def test_merge_flags_with_none_base():
    result = merge_risk_flags("none", ["user_history_risk"])
    assert result == "user_history_risk"


def test_merge_flags_empty_history():
    result = merge_risk_flags("blurry_image", [])
    assert result == "blurry_image"


def test_merge_flags_both_empty():
    result = merge_risk_flags("none", [])
    assert result == "none"