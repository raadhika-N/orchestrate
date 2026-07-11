"""
Display labels, colors and formatting helpers.
Converts raw enum values into human readable display text.
"""

CLAIM_STATUS_COLORS = {
    "supported": "🟢",
    "contradicted": "🔴",
    "not_enough_information": "🟡",
}

CLAIM_STATUS_LABELS = {
    "supported": "✅ Supported",
    "contradicted": "❌ Contradicted",
    "not_enough_information": "⚠️ Not Enough Information",
}

SEVERITY_COLORS = {
    "none": "⚪",
    "low": "🟢",
    "medium": "🟡",
    "high": "🔴",
    "unknown": "⚫",
}

SEVERITY_LABELS = {
    "none": "None",
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "unknown": "Unknown",
}

CLAIM_OBJECT_EMOJIS = {
    "car": "🚗",
    "laptop": "💻",
    "package": "📦",
}


def format_claim_status(status: str) -> str:
    s = (status or "").lower()
    label = CLAIM_STATUS_LABELS.get(s, status)
    return label


def format_severity(severity: str) -> str:
    s = (severity or "").lower()
    icon = SEVERITY_COLORS.get(s, "⚫")
    label = SEVERITY_LABELS.get(s, severity)
    return f"{icon} {label}"


def format_claim_object(obj: str) -> str:
    o = (obj or "").lower()
    emoji = CLAIM_OBJECT_EMOJIS.get(o, "📋")
    return f"{emoji} {obj.capitalize()}"


def format_risk_flags(flags: str) -> str:
    if not flags or flags.lower() == "none":
        return "✅ None"
    flag_list = [f.strip() for f in flags.split(";") if f.strip()]
    return " | ".join(f"⚠️ {f}" for f in flag_list)


def format_boolean(value) -> str:
    if str(value).lower() in ("true", "1", "yes"):
        return "✅ Yes"
    return "❌ No"


def status_to_color(status: str) -> str:
    colors = {
        "supported": "green",
        "contradicted": "red",
        "not_enough_information": "orange",
    }
    return colors.get((status or "").lower(), "gray")