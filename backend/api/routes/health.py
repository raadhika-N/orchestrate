from pathlib import Path
from fastapi import APIRouter
from backend.api.schemas.claim_schemas import HealthResponse
from backend.core.config import get_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    Returns server health status.
    Judges use this to confirm the server is running.
    """
    settings = get_settings()
    return HealthResponse(
        status="ok",
        model=settings.model_name,
        dataset_loaded=settings.sample_claims_path.exists(),
        output_exists=Path("output/output.csv").exists(),
    )