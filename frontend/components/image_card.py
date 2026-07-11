"""
Reusable image display component.
Shows an image with its ID and highlights
whether it is a supporting image or not.
"""
from pathlib import Path
import streamlit as st


def show_image(
    image_path: str,
    image_id: str,
    is_supporting: bool = False,
    dataset_dir: str = "dataset",
) -> None:
    """
    Displays one image with a label.
    Highlights supporting images with a green border effect.
    """
    full_path = Path(dataset_dir) / image_path

    if not full_path.exists():
        st.warning(f"Image not found: {image_path}")
        return

    label = f"🖼️ {image_id}"
    if is_supporting:
        label = f"✅ {image_id} (supporting)"

    st.image(str(full_path), caption=label, use_container_width=True)


def show_all_images(
    image_paths_field: str,
    supporting_image_ids: str,
    dataset_dir: str = "dataset",
) -> None:
    """
    Shows all images for a claim.
    Highlights the ones Groq identified as supporting evidence.
    """
    if not image_paths_field:
        st.info("No images submitted for this claim.")
        return

    paths = [p.strip() for p in image_paths_field.split(";") if p.strip()]

    supporting_ids = set()
    if supporting_image_ids and supporting_image_ids.lower() != "none":
        supporting_ids = {
            s.strip() for s in supporting_image_ids.split(";") if s.strip()
        }

    if len(paths) == 1:
        image_id = Path(paths[0]).stem
        show_image(
            paths[0],
            image_id,
            is_supporting=image_id in supporting_ids,
            dataset_dir=dataset_dir,
        )
    else:
        cols = st.columns(min(len(paths), 3))
        for i, path in enumerate(paths):
            image_id = Path(path).stem
            with cols[i % 3]:
                show_image(
                    path,
                    image_id,
                    is_supporting=image_id in supporting_ids,
                    dataset_dir=dataset_dir,
                )