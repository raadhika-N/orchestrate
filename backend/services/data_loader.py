from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import pandas as pd
from backend.core.logging import get_logger

logger = get_logger(__name__)

REQUIRED_CLAIM_COLUMNS = ["user_id", "image_paths", "user_claim", "claim_object"]
REQUIRED_USER_HISTORY_COLUMNS = [
    "user_id", "past_claim_count", "accept_claim", "manual_review_claim",
    "rejected_claim", "last_90_days_claim_count", "history_flags", "history_summary",
]
REQUIRED_EVIDENCE_REQUIREMENT_COLUMNS = [
    "requirement_id", "claim_object", "applies_to", "minimum_image_evidence",
]
ALLOWED_CLAIM_OBJECTS = {"car", "laptop", "package"}

_NO_HISTORY_DEFAULT: dict[str, Any] = {
    "user_id": None,
    "past_claim_count": "0",
    "accept_claim": "0",
    "manual_review_claim": "0",
    "rejected_claim": "0",
    "last_90_days_claim_count": "0",
    "history_flags": "none",
    "history_summary": "No prior claim history on file.",
}


class DatasetValidationError(ValueError):
    pass


def _clean_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Expected input file not found: {path}")
    return pd.read_csv(path, dtype=str)


def _validate_columns(df: pd.DataFrame, required: list[str], source_name: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise DatasetValidationError(
            f"{source_name} is missing required column(s): {missing}. Found: {list(df.columns)}"
        )


def _df_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    records = df.to_dict(orient="records")
    return [{k: _clean_value(v) for k, v in row.items()} for row in records]


def load_claims(path: Path, *, validate_claim_object: bool = True) -> list[dict[str, Any]]:
    df = _read_csv(path)
    _validate_columns(df, REQUIRED_CLAIM_COLUMNS, source_name=path.name)
    records = _df_to_records(df)
    if validate_claim_object:
        for i, row in enumerate(records):
            obj = (row.get("claim_object") or "").lower()
            if obj not in ALLOWED_CLAIM_OBJECTS:
                logger.warning(
                    "%s row %d has unexpected claim_object=%r",
                    path.name, i, row.get("claim_object")
                )
    logger.info("Loaded %d claim rows from %s", len(records), path.name)
    return records


def load_user_history(path: Path) -> dict[str, dict[str, Any]]:
    df = _read_csv(path)
    _validate_columns(df, REQUIRED_USER_HISTORY_COLUMNS, source_name=path.name)
    records = _df_to_records(df)
    index: dict[str, dict[str, Any]] = {}
    for row in records:
        user_id = row.get("user_id")
        if not user_id:
            logger.warning("Skipping user_history row with missing user_id: %r", row)
            continue
        index[user_id] = row
    logger.info("Loaded history for %d users from %s", len(index), path.name)
    return index


def get_user_history(history_index: dict[str, dict[str, Any]], user_id: str) -> dict[str, Any]:
    record = history_index.get(user_id)
    if record is None:
        return {**_NO_HISTORY_DEFAULT, "user_id": user_id}
    return record


def load_evidence_requirements(path: Path) -> list[dict[str, Any]]:
    df = _read_csv(path)
    _validate_columns(df, REQUIRED_EVIDENCE_REQUIREMENT_COLUMNS, source_name=path.name)
    records = _df_to_records(df)
    logger.info("Loaded %d evidence requirement rows from %s", len(records), path.name)
    return records


def build_evidence_requirement_index(
    records: list[dict[str, Any]]
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    index: dict[tuple[str, str], list[dict[str, Any]]] = {}

    def _add(key: tuple[str, str], row: dict[str, Any]) -> None:
        index.setdefault(key, []).append(row)

    for row in records:
        claim_object = (row.get("claim_object") or "").strip().lower()
        applies_to = (row.get("applies_to") or "").strip().lower()
        if not claim_object or not applies_to:
            continue
        if claim_object == "all":
            for obj in ALLOWED_CLAIM_OBJECTS:
                _add((obj, applies_to), row)
            _add(("all", applies_to), row)
        else:
            _add((claim_object, applies_to), row)
    return index


def get_evidence_requirement(
    requirement_index: dict[tuple[str, str], list[dict[str, Any]]],
    claim_object: str,
    issue_family: str,
) -> list[dict[str, Any]]:
    key = ((claim_object or "").strip().lower(), (issue_family or "").strip().lower())
    return requirement_index.get(key, [])


@dataclass
class DatasetBundle:
    claims: list[dict[str, Any]] = field(default_factory=list)
    sample_claims: list[dict[str, Any]] = field(default_factory=list)
    user_history_index: dict[str, dict[str, Any]] = field(default_factory=dict)
    evidence_requirements: list[dict[str, Any]] = field(default_factory=list)
    evidence_requirements_index: dict[tuple[str, str], list[dict[str, Any]]] = field(default_factory=dict)


def load_dataset_bundle(
    *,
    claims_path: Path,
    sample_claims_path: Path,
    user_history_path: Path,
    evidence_requirements_path: Path,
) -> DatasetBundle:
    evidence_requirements = load_evidence_requirements(evidence_requirements_path)
    return DatasetBundle(
        claims=load_claims(claims_path),
        sample_claims=load_claims(sample_claims_path),
        user_history_index=load_user_history(user_history_path),
        evidence_requirements=evidence_requirements,
        evidence_requirements_index=build_evidence_requirement_index(evidence_requirements),
    )