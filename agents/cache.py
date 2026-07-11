from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any
from backend.core.logging import get_logger
from database.connection import get_connection

logger = get_logger(__name__)


def _compute_cache_key(
    *,
    claim_context_text: str,
    image_paths: list[Path],
    model_name: str,
) -> str:
    hasher = hashlib.sha256()
    hasher.update(model_name.encode("utf-8"))
    hasher.update(claim_context_text.encode("utf-8"))
    for path in sorted(image_paths):
        try:
            hasher.update(path.read_bytes())
        except Exception as exc:
            logger.warning("Could not read image for cache key: %s (%s)", path, exc)
            hasher.update(str(path).encode("utf-8"))
    return hasher.hexdigest()


def get_cached_response(
    *,
    claim_context_text: str,
    image_paths: list[Path],
    model_name: str,
    db_path: Path | None = None,
) -> dict[str, Any] | None:
    key = _compute_cache_key(
        claim_context_text=claim_context_text,
        image_paths=image_paths,
        model_name=model_name,
    )
    try:
        kwargs = {"db_path": db_path} if db_path else {}
        conn = get_connection(**kwargs)
        row = conn.execute(
            "SELECT response_json FROM claim_cache WHERE cache_key = ?", (key,)
        ).fetchone()
        conn.close()
        if row:
            logger.debug("Cache HIT for key %s", key[:12])
            return json.loads(row["response_json"])
        logger.debug("Cache MISS for key %s", key[:12])
        return None
    except Exception as exc:
        logger.warning("Cache lookup failed: %s", exc)
        return None


def set_cached_response(
    *,
    claim_context_text: str,
    image_paths: list[Path],
    model_name: str,
    response: dict[str, Any],
    db_path: Path | None = None,
) -> None:
    key = _compute_cache_key(
        claim_context_text=claim_context_text,
        image_paths=image_paths,
        model_name=model_name,
    )
    try:
        kwargs = {"db_path": db_path} if db_path else {}
        conn = get_connection(**kwargs)
        conn.execute(
            "INSERT OR REPLACE INTO claim_cache (cache_key, response_json) VALUES (?, ?)",
            (key, json.dumps(response)),
        )
        conn.commit()
        conn.close()
        logger.debug("Cache SET for key %s", key[:12])
    except Exception as exc:
        logger.warning("Cache write failed: %s", exc)