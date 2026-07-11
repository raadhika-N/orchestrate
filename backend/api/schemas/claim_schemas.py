"""
Pydantic schemas for API request and response shapes.
These mirror the output.csv columns exactly so the API
can never return something the CSV writer wouldn't accept.
"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class ClaimResponse(BaseModel):
    user_id: str
    image_paths: str
    user_claim: str
    claim_object: str
    evidence_standard_met: Any
    evidence_standard_met_reason: str
    risk_flags: str
    issue_type: str
    object_part: str
    claim_status: str
    claim_status_justification: str
    supporting_image_ids: str
    valid_image: Any
    severity: str


class ClaimSummary(BaseModel):
    user_id: str
    claim_object: str
    claim_status: str
    severity: str
    risk_flags: str


class PipelineRunRequest(BaseModel):
    run_type: str = "sample"


class PipelineRunResponse(BaseModel):
    run_id: str
    status: str
    message: str


class PipelineStatusResponse(BaseModel):
    run_id: str
    status: str
    total_claims: int
    message: str


class EvaluationMetrics(BaseModel):
    total_claims: int
    claim_status_accuracy: float
    issue_type_accuracy: float
    object_part_accuracy: float
    severity_accuracy: float
    generated_at: str


class HealthResponse(BaseModel):
    status: str
    model: str
    dataset_loaded: bool
    output_exists: bool