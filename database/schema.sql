CREATE TABLE IF NOT EXISTS claim_cache (
    cache_key     TEXT PRIMARY KEY,
    response_json TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS eval_runs (
    run_id        TEXT PRIMARY KEY,
    run_type      TEXT NOT NULL,
    started_at    TEXT NOT NULL,
    finished_at   TEXT,
    accuracy_json TEXT,
    total_claims  INTEGER DEFAULT 0,
    status        TEXT DEFAULT 'running'
);