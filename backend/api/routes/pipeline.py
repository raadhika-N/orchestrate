import uuid
import threading
import time
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks
from backend.api.schemas.claim_schemas import (
    PipelineRunRequest,
    PipelineRunResponse,
    PipelineStatusResponse,
)
from backend.api.dependencies import get_bundle, get_run_status, set_run_status
from backend.core.config import get_settings
from backend.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


def _run_pipeline_background(run_id: str, run_type: str) -> None:
    """
    Runs the pipeline in a background thread so the API
    doesn't block while processing claims.
    """
    import csv

    set_run_status(run_id, {
        "status": "running",
        "total_claims": 0,
        "message": "Pipeline started...",
    })

    try:
        from backend.services.pipeline_runner import process_claim

        settings = get_settings()
        bundle = get_bundle()

        claims = bundle.sample_claims if run_type == "sample" else bundle.claims
        output_file = "output/sample_output.csv" if run_type == "sample" else "output/output.csv"

        OUTPUT_COLUMNS = [
            "user_id", "image_paths", "user_claim", "claim_object",
            "evidence_standard_met", "evidence_standard_met_reason",
            "risk_flags", "issue_type", "object_part", "claim_status",
            "claim_status_justification", "supporting_image_ids",
            "valid_image", "severity",
        ]

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        results = []

        for i, claim in enumerate(claims):
            result = process_claim(claim, bundle, settings)
            results.append(result)
            set_run_status(run_id, {
                "status": "running",
                "total_claims": i + 1,
                "message": f"Processed {i + 1}/{len(claims)} claims...",
            })
            if i < len(claims) - 1:
                time.sleep(1.0)

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=OUTPUT_COLUMNS, extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(results)

        set_run_status(run_id, {
            "status": "completed",
            "total_claims": len(results),
            "message": f"Done! {len(results)} claims written to {output_file}",
        })
        logger.info("Pipeline run %s completed.", run_id)

    except Exception as exc:
        logger.error("Pipeline run %s failed: %s", run_id, exc)
        set_run_status(run_id, {
            "status": "failed",
            "total_claims": 0,
            "message": f"Pipeline failed: {str(exc)}",
        })


@router.post("/pipeline/run", response_model=PipelineRunResponse)
def trigger_pipeline(
    request: PipelineRunRequest,
    background_tasks: BackgroundTasks,
):
    """
    Triggers a pipeline run in the background.
    Returns immediately with a run_id you can use to check status.
    run_type: 'sample' processes sample_claims.csv
    run_type: 'test' processes claims.csv
    """
    run_id = str(uuid.uuid4())[:8]
    background_tasks.add_task(
        _run_pipeline_background, run_id, request.run_type
    )
    return PipelineRunResponse(
        run_id=run_id,
        status="started",
        message=f"Pipeline started for run_type={request.run_type}",
    )


@router.get("/pipeline/run/{run_id}", response_model=PipelineStatusResponse)
def get_pipeline_status(run_id: str):
    """
    Returns the current status of a pipeline run.
    Poll this every few seconds to track progress.
    """
    status = get_run_status().get(run_id)
    if not status:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"Run ID {run_id} not found."
        )
    return PipelineStatusResponse(
        run_id=run_id,
        status=status["status"],
        total_claims=status["total_claims"],
        message=status["message"],
    )