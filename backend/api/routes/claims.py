from fastapi import APIRouter, HTTPException
from backend.api.dependencies import load_output_csv
from backend.api.schemas.claim_schemas import ClaimResponse, ClaimSummary

router = APIRouter()


@router.get("/claims", response_model=list[ClaimSummary])
def list_claims():
    """
    Returns a summary of all processed claims from output.csv.
    Used by the frontend to show the claims table.
    """
    rows = load_output_csv()
    if not rows:
        return []
    return [
        ClaimSummary(
            user_id=row.get("user_id", ""),
            claim_object=row.get("claim_object", ""),
            claim_status=row.get("claim_status", ""),
            severity=row.get("severity", ""),
            risk_flags=row.get("risk_flags", "none"),
        )
        for row in rows
    ]


@router.get("/claims/{user_id}", response_model=ClaimResponse)
def get_claim(user_id: str):
    """
    Returns the full decision for one specific claim by user_id.
    Used by the frontend claim viewer.
    """
    rows = load_output_csv()
    for row in rows:
        if row.get("user_id") == user_id:
            return ClaimResponse(**row)
    raise HTTPException(
        status_code=404,
        detail=f"Claim not found for user_id={user_id}"
    )