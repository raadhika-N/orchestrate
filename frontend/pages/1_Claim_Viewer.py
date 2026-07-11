"""
Page 1 - Claim Viewer

Shows one claim at a time.
Image on the left, AI decision on the right.
This is the main demo page judges will look at.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))




import streamlit as st
from frontend.utils.api_client import get_claims, get_claim
from frontend.components.image_card import show_all_images
from frontend.components.claim_table import show_claim_decision

st.set_page_config(
    page_title="Claim Viewer",
    page_icon="🖼️",
    layout="wide",
)

st.title("🖼️ Claim Viewer")
st.markdown("Select a claim to see the image evidence and AI decision side by side.")

# Load all claims for the selector
claims = get_claims()

if not claims:
    st.warning(
        "No processed claims found. "
        "Go to **Run Pipeline** page and run the pipeline first."
    )
    st.stop()

# Dropdown to pick a claim
user_ids = [c.get("user_id", "") for c in claims]
selected_user_id = st.selectbox(
    "Select a claim:",
    options=user_ids,
    format_func=lambda uid: f"{uid} — {next((c.get('claim_object','') for c in claims if c.get('user_id') == uid), '')}",
)

if not selected_user_id:
    st.stop()

# Load the full claim detail
claim = get_claim(selected_user_id)

if not claim:
    st.error(f"Could not load claim for {selected_user_id}")
    st.stop()

st.divider()

# Side by side layout
left, right = st.columns([1, 1])

with left:
    st.subheader("📸 Submitted Images")
    show_all_images(
        image_paths_field=claim.get("image_paths", ""),
        supporting_image_ids=claim.get("supporting_image_ids", "none"),
        dataset_dir="dataset",
    )

    st.markdown("**Image Paths:**")
    st.code(claim.get("image_paths", "none"))

with right:
    st.subheader("🤖 AI Decision")
    show_claim_decision(claim)