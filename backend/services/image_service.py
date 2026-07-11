from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ResolvedImage:
    image_id: str
    relative_path: str
    absolute_path: Path
    exists: bool


def parse_image_paths(image_paths_field: str | None) -> list[str]:
    if not image_paths_field:
        return []
    return [p.strip() for p in image_paths_field.split(";") if p.strip()]


def get_image_id(relative_path: str) -> str:
    return Path(relative_path).stem


def resolve_images(dataset_dir: Path, image_paths_field: str | None) -> list[ResolvedImage]:
    resolved: list[ResolvedImage] = []
    for relative_path in parse_image_paths(image_paths_field):
        absolute_path = dataset_dir / relative_path
        exists = absolute_path.is_file()
        if not exists:
            logger.warning("Image path does not resolve to a file: %s", absolute_path)
        resolved.append(ResolvedImage(
            image_id=get_image_id(relative_path),
            relative_path=relative_path,
            absolute_path=absolute_path,
            exists=exists,
        ))
    return resolved


def validate_images(
    dataset_dir: Path,
    image_paths_field: str | None
) -> tuple[list[ResolvedImage], list[ResolvedImage]]:
    resolved = resolve_images(dataset_dir, image_paths_field)
    return [r for r in resolved if r.exists], [r for r in resolved if not r.exists]