from pathlib import Path
from backend.services.image_service import (
    get_image_id,
    parse_image_paths,
    resolve_images,
    validate_images,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_image_paths_splits_on_semicolon():
    raw = "images/case_001/img_1.jpg; images/case_001/img_2.jpg "
    assert parse_image_paths(raw) == [
        "images/case_001/img_1.jpg",
        "images/case_001/img_2.jpg",
    ]


def test_parse_image_paths_handles_empty_input():
    assert parse_image_paths(None) == []
    assert parse_image_paths("") == []


def test_get_image_id_strips_dir_and_extension():
    assert get_image_id("images/case_001/img_1.jpg") == "img_1"


def test_resolve_images_marks_existing_files():
    resolved = resolve_images(
        FIXTURES_DIR, "images/case_001/img_1.jpg;images/case_001/img_2.jpg"
    )
    assert len(resolved) == 2
    assert all(r.exists for r in resolved)
    assert [r.image_id for r in resolved] == ["img_1", "img_2"]


def test_resolve_images_does_not_raise_on_missing_file():
    resolved = resolve_images(
        FIXTURES_DIR, "images/case_003/img_1.jpg;images/case_003/img_missing.jpg"
    )
    assert resolved[0].exists is True
    assert resolved[1].exists is False


def test_validate_images_splits_valid_and_missing():
    valid, missing = validate_images(
        FIXTURES_DIR, "images/case_003/img_1.jpg;images/case_003/img_missing.jpg"
    )
    assert len(valid) == 1
    assert len(missing) == 1
    assert missing[0].image_id == "img_missing"