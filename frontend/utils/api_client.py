"""
Thin wrapper around the backend API.
All API calls go through here so pages never
contain raw HTTP code.
"""
from __future__ import annotations
import requests

BASE_URL = "http://localhost:8000"


def get_health() -> dict:
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        return r.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_claims() -> list[dict]:
    try:
        r = requests.get(f"{BASE_URL}/claims", timeout=10)
        if r.status_code == 200:
            return r.json()
        return []
    except Exception:
        return []


def get_claim(user_id: str) -> dict | None:
    try:
        r = requests.get(f"{BASE_URL}/claims/{user_id}", timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None


def get_evaluation_metrics() -> dict | None:
    try:
        r = requests.get(f"{BASE_URL}/evaluation/metrics", timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None


def trigger_pipeline(run_type: str = "sample") -> dict:
    try:
        r = requests.post(
            f"{BASE_URL}/pipeline/run",
            json={"run_type": run_type},
            timeout=10,
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_pipeline_status(run_id: str) -> dict:
    try:
        r = requests.get(f"{BASE_URL}/pipeline/run/{run_id}", timeout=10)
        if r.status_code == 200:
            return r.json()
        return {"status": "error", "message": "Run not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}