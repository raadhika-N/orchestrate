"""
Renders a single claim decision in a human readable format.
Used in the claim viewer page.
"""
import streamlit as st
from frontend.utils.formatting import (
    format_claim_status,
    format_severity,
    format_claim_object,
    format_risk_flags,
    format_boolean,
    status_to_color,
)


def show_claim_decision(claim: dict) -> None:
    """
    Shows the full decision for one claim in a
    clean, readable layout with color coding.
    """
    status = claim.get("claim_status", "unknown")
    color = status_to_color(status)

    # Big status badge at the top
    st.markdown(
        f"""
        <div style="
            background-color: {'#d4edda' if color == 'green' else '#f8d7da' if color == 'red' else '#fff3cd'};
            border-left: 6px solid {'#28a745' if color == 'green' else '#dc3545' if color == 'red' else '#ffc107'};
            padding: 16px;
            border-radius: 4px;
            margin-bottom: 16px;
        ">
            <h3 style="margin:0; color: {'#155724' if color == 'green' else '#721c24' if color == 'red' else '#856404'}">
                {format_claim_status(status)}
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Justification
    st.markdown("**Justification:**")
    st.info(claim.get("claim_status_justification", "No justification provided."))

    # Key fields in two columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Object Type:**")
        st.write(format_claim_object(claim.get("claim_object", "")))

        st.markdown("**Issue Type:**")
        st.write(claim.get("issue_type", "unknown"))

        st.markdown("**Object Part:**")
        st.write(claim.get("object_part", "unknown"))

        st.markdown("**Severity:**")
        st.write(format_severity(claim.get("severity", "unknown")))

    with col2:
        st.markdown("**Evidence Standard Met:**")
        st.write(format_boolean(claim.get("evidence_standard_met", False)))

        st.markdown("**Valid Image:**")
        st.write(format_boolean(claim.get("valid_image", False)))

        st.markdown("**Supporting Images:**")
        st.write(claim.get("supporting_image_ids", "none"))

        st.markdown("**Risk Flags:**")
        st.write(format_risk_flags(claim.get("risk_flags", "none")))

    # Evidence standard reason
    if claim.get("evidence_standard_met_reason"):
        st.markdown("**Evidence Standard Reason:**")
        st.write(claim.get("evidence_standard_met_reason"))

    # User claim transcript
    with st.expander("📜 Original User Claim"):
        st.write(claim.get("user_claim", "No claim text available."))