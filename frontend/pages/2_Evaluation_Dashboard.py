"""
Page 2 - Evaluation Dashboard

Shows accuracy metrics as charts.
This is what judges look at to assess system quality.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))





import streamlit as st
from frontend.utils.api_client import get_evaluation_metrics

st.set_page_config(
    page_title="Evaluation Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Evaluation Dashboard")
st.markdown(
    "Accuracy metrics comparing AI predictions against "
    "ground truth labels from sample_claims.csv."
)

metrics = get_evaluation_metrics()

if not metrics:
    st.warning(
        "No evaluation data found. "
        "Run the pipeline on sample claims first, then run:\n"
        "`python evaluation/evaluate.py`"
    )
    st.stop()

st.divider()

# Top metrics
st.subheader("Overall Performance")

col1, col2, col3, col4 = st.columns(4)

claim_acc = metrics.get("claim_status_accuracy", 0)
issue_acc = metrics.get("issue_type_accuracy", 0)
part_acc = metrics.get("object_part_accuracy", 0)
sev_acc = metrics.get("severity_accuracy", 0)

with col1:
    st.metric(
        "Claim Status",
        f"{claim_acc:.1%}",
        help="Primary metric — was supported/contradicted/not_enough_information correct?",
    )
with col2:
    st.metric(
        "Issue Type",
        f"{issue_acc:.1%}",
        help="Was dent/scratch/crack etc correct?",
    )
with col3:
    st.metric(
        "Object Part",
        f"{part_acc:.1%}",
        help="Was door/bumper/screen etc correct?",
    )
with col4:
    st.metric(
        "Severity",
        f"{sev_acc:.1%}",
        help="Was none/low/medium/high correct?",
    )

st.divider()

# Bar chart
st.subheader("Accuracy by Field")

try:
    import pandas as pd

    chart_data = pd.DataFrame({
        "Field": [
            "Claim Status",
            "Issue Type",
            "Object Part",
            "Severity",
        ],
        "Accuracy": [
            claim_acc * 100,
            issue_acc * 100,
            part_acc * 100,
            sev_acc * 100,
        ],
    })

    st.bar_chart(
        chart_data.set_index("Field"),
        y="Accuracy",
        color="#4CAF50",
    )
except Exception:
    st.info("Install pandas to see the chart.")

st.divider()

# Details
st.subheader("Run Details")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Claims Evaluated", metrics.get("total_claims", 0))
with col2:
    st.write(f"**Generated at:** {metrics.get('generated_at', 'unknown')}")

st.divider()

# How to improve
st.subheader("How to Improve Accuracy")
st.markdown("""
- **Claim Status below 70%?** Tune the system prompt in `agents/prompts/system_prompt.md`
- **Issue Type below 60%?** Add more specific damage type descriptions to the prompt
- **Severity below 50%?** Add explicit severity scale definitions to the prompt
- After any prompt change, run `python scripts/run_sample.py` then re-check this dashboard
""")