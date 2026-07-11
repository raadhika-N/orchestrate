from pathlib import Path
import pytest
from agents.cache import get_cached_response, set_cached_response


@pytest.fixture
def tmp_db(tmp_path):
    return tmp_path / "test_cache.db"


def test_cache_miss_returns_none(tmp_db):
    result = get_cached_response(
        claim_context_text="test",
        image_paths=[],
        model_name="model",
        db_path=tmp_db,
    )
    assert result is None


def test_cache_hit_returns_response(tmp_db):
    response = {"claim_status": "supported"}
    set_cached_response(
        claim_context_text="test",
        image_paths=[],
        model_name="model",
        response=response,
        db_path=tmp_db,
    )
    result = get_cached_response(
        claim_context_text="test",
        image_paths=[],
        model_name="model",
        db_path=tmp_db,
    )
    assert result == response


def test_different_text_gives_cache_miss(tmp_db):
    set_cached_response(
        claim_context_text="claim A",
        image_paths=[],
        model_name="model",
        response={"claim_status": "supported"},
        db_path=tmp_db,
    )
    result = get_cached_response(
        claim_context_text="claim B",
        image_paths=[],
        model_name="model",
        db_path=tmp_db,
    )
    assert result is None


def test_different_model_gives_cache_miss(tmp_db):
    set_cached_response(
        claim_context_text="same",
        image_paths=[],
        model_name="model-A",
        response={"claim_status": "supported"},
        db_path=tmp_db,
    )
    result = get_cached_response(
        claim_context_text="same",
        image_paths=[],
        model_name="model-B",
        db_path=tmp_db,
    )
    assert result is None


def test_overwrite_updates_cache(tmp_db):
    set_cached_response(
        claim_context_text="test",
        image_paths=[],
        model_name="model",
        response={"claim_status": "supported"},
        db_path=tmp_db,
    )
    set_cached_response(
        claim_context_text="test",
        image_paths=[],
        model_name="model",
        response={"claim_status": "contradicted"},
        db_path=tmp_db,
    )
    result = get_cached_response(
        claim_context_text="test",
        image_paths=[],
        model_name="model",
        db_path=tmp_db,
    )
    assert result["claim_status"] == "contradicted"