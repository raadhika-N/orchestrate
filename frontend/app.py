"""
Main Streamlit entry point.

This is the landing page judges see first.
Shows system status and a quick summary.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import streamlit as st
from frontend.utils.api_client import get_health, get_claims
from frontend.utils.formatting import format_claim_status, format_severity

st.set_page_config(
    page_title="Evidence Review System",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Multi-Modal Evidence Review System")
st.markdown(
    "Automated damage claims adjudication using image evidence, "
    "claim text, and user history."
)

st.divider()

# System status
st.subheader("System Status")

health = get_health()

col1, col2, col3, col4 = st.columns(4)

with col1:
    if health.get("status") == "ok":
        st.success("🟢 API Online")
    else:
        st.error("🔴 API Offline")
        st.caption("Start with: uvicorn backend.main:app --reload")

with col2:
    if health.get("dataset_loaded"):
        st.success("🟢 Dataset Loaded")
    else:
        st.warning("🟡 Dataset Missing")

with col3:
    if health.get("output_exists"):
        st.success("🟢 Output Ready")
    else:
        st.warning("🟡 No Output Yet")

with col4:
    model = health.get("model", "unknown")
    st.info(f"🤖 {model}")

st.divider()

# Quick summary of claims
st.subheader("Claims Overview")

claims = get_claims()

if not claims:
    st.info(
        "No processed claims found. "
        "Run the pipeline first using the Run Pipeline page."
    )
else:
    total = len(claims)
    supported = sum(1 for c in claims if c.get("claim_status") == "supported")
    contradicted = sum(1 for c in claims if c.get("claim_status") == "contradicted")
    not_enough = sum(1 for c in claims if c.get("claim_status") == "not_enough_information")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Claims", total)
    with col2:
        st.metric("✅ Supported", supported)
    with col3:
        st.metric("❌ Contradicted", contradicted)
    with col4:
        st.metric("⚠️ Not Enough Info", not_enough)

    st.divider()

    # Claims table
    st.subheader("All Claims")

    for claim in claims:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            with col1:
                st.write(f"**{claim.get('user_id')}**")
            with col2:
                st.write(claim.get("claim_object", "").capitalize())
            with col3:
                st.write(format_claim_status(claim.get("claim_status", "")))
            with col4:
                st.write(format_severity(claim.get("severity", "")))

st.divider()
st.caption(
    "Navigate using the sidebar → "
    "Claim Viewer | Evaluation Dashboard | Run Pipeline"
)