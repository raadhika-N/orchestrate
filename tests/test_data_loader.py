from pathlib import Path
import pytest
from backend.services.data_loader import (
    DatasetValidationError,
    build_evidence_requirement_index,
    get_evidence_requirement,
    get_user_history,
    load_claims,
    load_evidence_requirements,
    load_user_history,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_load_claims_returns_all_rows_with_required_columns():
    records = load_claims(FIXTURES_DIR / "sample_claims.csv")
    assert len(records) == 4
    for row in records:
        assert {"user_id", "image_paths", "user_claim", "claim_object"} <= row.keys()


def test_load_claims_raises_on_missing_required_column(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("user_id,user_claim,claim_object\nu_001,hello,car\n")
    with pytest.raises(DatasetValidationError, match="image_paths"):
        load_claims(bad)


def test_load_claims_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        load_claims(FIXTURES_DIR / "does_not_exist.csv")


def test_load_claims_warns_on_unexpected_claim_object():
    records = load_claims(FIXTURES_DIR / "sample_claims.csv")
    assert any(r["claim_object"] == "drone" for r in records)


def test_load_user_history_indexes_by_user_id():
    index = load_user_history(FIXTURES_DIR / "user_history.csv")
    assert set(index.keys()) == {"u_001", "u_002", "u_003"}
    assert index["u_002"]["rejected_claim"] == "2"


def test_get_user_history_returns_safe_default_for_unknown_user():
    index = load_user_history(FIXTURES_DIR / "user_history.csv")
    result = get_user_history(index, "u_999")
    assert result["user_id"] == "u_999"
    assert result["past_claim_count"] == "0"
    assert result["history_flags"] == "none"


def test_get_user_history_returns_real_record_for_known_user():
    index = load_user_history(FIXTURES_DIR / "user_history.csv")
    result = get_user_history(index, "u_001")
    assert result["history_summary"].startswith("Generally reliable")


def test_evidence_requirement_lookup_object_specific():
    records = load_evidence_requirements(FIXTURES_DIR / "evidence_requirements.csv")
    index = build_evidence_requirement_index(records)
    matches = get_evidence_requirement(index, "car", "dent")
    assert len(matches) == 1
    assert matches[0]["requirement_id"] == "req_001"


def test_evidence_requirement_lookup_all_rule():
    records = load_evidence_requirements(FIXTURES_DIR / "evidence_requirements.csv")
    index = build_evidence_requirement_index(records)
    for obj in ("car", "laptop", "package"):
        matches = get_evidence_requirement(index, obj, "water_damage")
        assert len(matches) == 1
        assert matches[0]["requirement_id"] == "req_005"


def test_evidence_requirement_returns_empty_list_when_no_rule():
    records = load_evidence_requirements(FIXTURES_DIR / "evidence_requirements.csv")
    index = build_evidence_requirement_index(records)
    assert get_evidence_requirement(index, "laptop", "missing_part") == []