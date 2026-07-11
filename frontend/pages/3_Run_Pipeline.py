"""
Page 3 - Run Pipeline

Lets judges trigger a new pipeline run from the UI
and watch live progress without touching the terminal.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))





import time
import streamlit as st
from frontend.utils.api_client import (
    trigger_pipeline,
    get_pipeline_status,
)

st.set_page_config(
    page_title="Run Pipeline",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Run Pipeline")
st.markdown(
    "Trigger a new pipeline run. "
    "The system will process all claims using Groq AI and update the output."
)

st.divider()

# Run type selector
st.subheader("Select Run Type")

run_type = st.radio(
    "What do you want to process?",
    options=["sample", "test"],
    format_func=lambda x: (
        "📋 Sample Claims (sample_claims.csv) — use for accuracy testing"
        if x == "sample"
        else "📁 Test Claims (claims.csv) — use for final submission"
    ),
)

st.divider()

col1, col2 = st.columns([1, 3])

with col1:
    run_button = st.button(
        "🚀 Start Pipeline",
        type="primary",
        use_container_width=True,
    )

with col2:
    st.info(
        "ℹ️ Each claim takes about 2-5 seconds. "
        "Cached claims are instant. "
        "The page will show live progress."
    )

if run_button:
    st.divider()
    st.subheader("Pipeline Progress")

    # Trigger the run
    result = trigger_pipeline(run_type=run_type)

    if result.get("status") == "error":
        st.error(f"Failed to start pipeline: {result.get('message')}")
        st.stop()

    run_id = result.get("run_id")
    st.success(f"Pipeline started! Run ID: `{run_id}`")

    # Progress bar and status
    progress_bar = st.progress(0)
    status_text = st.empty()
    claim_count = st.empty()

    # Poll for status
    max_polls = 300
    for poll in range(max_polls):
        time.sleep(2)

        status = get_pipeline_status(run_id)

        current_status = status.get("status", "unknown")
        total = status.get("total_claims", 0)
        message = status.get("message", "")

        status_text.write(f"**Status:** {current_status.upper()}")
        claim_count.write(f"**Claims processed:** {total}")

        # Update progress bar
        if current_status == "completed":
            progress_bar.progress(1.0)
            st.success(f"✅ {message}")
            st.balloons()
            break
        elif current_status == "failed":
            progress_bar.progress(0)
            st.error(f"❌ {message}")
            break
        elif current_status == "running":
            # Animate progress bar
            progress = min((poll + 1) / max_polls * 2, 0.95)
            progress_bar.progress(progress)
        else:
            time.sleep(1)

    else:
        st.warning("Pipeline is taking longer than expected. Check the terminal for progress.")

st.divider()

st.subheader("Manual Commands")
st.markdown("You can also run these directly in the terminal:")

st.code("python scripts/run_sample.py", language="bash")
st.code("python scripts/run_test.py", language="bash")
st.code("python evaluation/evaluate.py", language="bash")