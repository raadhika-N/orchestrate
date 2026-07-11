from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.api.schemas.claim_schemas import EvaluationMetrics
from backend.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/evaluation/metrics", response_model=EvaluationMetrics)
def get_evaluation_metrics():
    """
    Returns the latest accuracy metrics from the evaluation report.
    Judges use this to see how well the system is performing.
    """
    sample_output = Path("output/sample_output.csv")
    sample_claims = Path("dataset/sample_claims.csv")

    if not sample_output.exists():
        raise HTTPException(
            status_code=404,
            detail="No evaluation data found. Run 'python scripts/run_sample.py' first."
        )

    import pandas as pd
    from datetime import datetime

    predictions = pd.read_csv(sample_output, dtype=str).fillna("")
    ground_truth = pd.read_csv(sample_claims, dtype=str).fillna("")

    total = min(len(predictions), len(ground_truth))
    gt = ground_truth.iloc[:total]
    pred = predictions.iloc[:total]

    def accuracy(field: str) -> float:
        if field not in gt.columns or field not in pred.columns:
            return 0.0
        matches = sum(
            str(gt.iloc[i].get(field, "")).strip().lower() ==
            str(pred.iloc[i].get(field, "")).strip().lower()
            for i in range(total)
        )
        return matches / total if total > 0 else 0.0

    return EvaluationMetrics(
        total_claims=total,
        claim_status_accuracy=accuracy("claim_status"),
        issue_type_accuracy=accuracy("issue_type"),
        object_part_accuracy=accuracy("object_part"),
        severity_accuracy=accuracy("severity"),
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )