-- Phase 2 evidence ledger schema. See docs/phase2-architecture.md §4.

CREATE TABLE IF NOT EXISTS agent_versions (
    version_id      TEXT PRIMARY KEY,   -- hash(code_ref, prompt_hash, model_id)
    agent_identity  TEXT,               -- ERC-8004 agentId once registered, else NULL
    code_ref        TEXT,
    prompt_hash     TEXT,
    model_id        TEXT NOT NULL,
    resolution      TEXT NOT NULL,      -- 'strong' (explicit arc.version_id attr) or 'weak' (model-only fallback)
    signature       TEXT,               -- circle wallet sign() over the above, hex
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS operations (
    op_id           TEXT PRIMARY KEY,   -- otel span_id
    trace_id        TEXT NOT NULL,
    version_id      TEXT NOT NULL REFERENCES agent_versions(version_id),
    operation_type  TEXT NOT NULL,      -- invoke_agent | chat | execute_tool, per OTel GenAI semconv
    input_hash      TEXT NOT NULL,
    output_hash     TEXT,
    content_ref     TEXT,               -- pointer to off-chain content blob, NULL if redacted/excluded
    token_usage     TEXT,               -- JSON, per gen_ai.usage.* attributes
    status          TEXT NOT NULL,      -- ok | error | unset, per span status
    started_at      TEXT NOT NULL,
    ended_at        TEXT,
    epoch_id        TEXT REFERENCES epochs(epoch_id)
);

CREATE TABLE IF NOT EXISTS epochs (
    epoch_id        TEXT PRIMARY KEY,
    prev_epoch_id   TEXT REFERENCES epochs(epoch_id),
    merkle_root     TEXT NOT NULL,
    op_count        INTEGER NOT NULL,
    sealed_at       TEXT NOT NULL,
    anchor_tx_hash  TEXT,               -- NULL until D1 (AnchorLog) is deployed and wired
    anchored_at     TEXT
);

CREATE TABLE IF NOT EXISTS epoch_members (
    epoch_id        TEXT NOT NULL REFERENCES epochs(epoch_id),
    op_id           TEXT NOT NULL REFERENCES operations(op_id),
    leaf_index      INTEGER NOT NULL,
    leaf_hash       TEXT NOT NULL,       -- frozen at sealing time — see ledger/verify.py
    PRIMARY KEY (epoch_id, op_id)
);
