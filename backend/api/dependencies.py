"""
Shared dependencies injected into API routes.

The dataset bundle is loaded ONCE when the server starts
and reused for every request. This means no repeated CSV
reads per API call.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.services.data_loader import DatasetBundle, load_dataset_bundle

logger = get_logger(__name__)

# Global bundle loaded at startup
_bundle: DatasetBundle | None = None
_run_status: dict[str, Any] = {}


def get_bundle() -> DatasetBundle:
    global _bundle
    if _bundle is None:
        settings = get_settings()
        logger.info("Loading dataset bundle for API...")
        _bundle = load_dataset_bundle(
            claims_path=settings.claims_path,
            sample_claims_path=settings.sample_claims_path,
            user_history_path=settings.user_history_path,
            evidence_requirements_path=settings.evidence_requirements_path,
        )
        logger.info("Dataset bundle loaded.")
    return _bundle


def get_run_status() -> dict[str, Any]:
    return _run_status


def set_run_status(run_id: str, status: dict[str, Any]) -> None:
    _run_status[run_id] = status


def load_output_csv() -> list[dict[str, Any]]:
    """Reads the latest output.csv and returns rows as dicts."""
    output_path = Path("output/output.csv")
    if not output_path.exists():
        return []
    import pandas as pd
    df = pd.read_csv(output_path, dtype=str)
    return df.fillna("").to_dict(orient="records")


def load_sample_output_csv() -> list[dict[str, Any]]:
    """Reads the latest sample_output.csv and returns rows as dicts."""
    output_path = Path("output/sample_output.csv")
    if not output_path.exists():
        return []
    import pandas as pd
    df = pd.read_csv(output_path, dtype=str)
    return df.fillna("").to_dict(orient="records")