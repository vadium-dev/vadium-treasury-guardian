"""Version resolution from incoming OTel GenAI span attributes.

See docs/phase2-architecture.md §8: OTel guarantees a model identifier on
every GenAI span, but not a code/prompt version — that's not part of the
standard. Two resolution paths follow from that:

- "strong": the source set a custom `arc.version_id` attribute (optionally
  with `arc.code_ref` / `arc.prompt_hash`) — real evidence of a pinned
  version.
- "weak": no such attribute. Fall back to (model_id, input_schema_shape) —
  the shape of the input, not its content, so this works even when a
  builder has opted out of recording content per OTel's own GenAI
  conventions.

Per ADR-009 (docs/phase2-design-decisions.md): version_id is always a
content-derived hash, never hand-assigned, so it can't drift.
"""

import hashlib
import json
import subprocess
import sqlite3
from datetime import datetime, timezone


def _hash(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update((p or "").encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def _input_schema_shape(input_messages) -> str:
    """Fingerprint the *shape* of the input, never its content."""
    if isinstance(input_messages, list):
        shape = [
            {"role": m.get("role"), "keys": sorted(m.keys())}
            for m in input_messages
            if isinstance(m, dict)
        ]
        return json.dumps(shape, sort_keys=True)
    return json.dumps({"type": type(input_messages).__name__})


def resolve_version(conn: sqlite3.Connection, attributes: dict, agent_identity: str | None = None) -> str:
    """Resolve (and create if new) the version_id for one incoming span.

    `attributes` is the flattened attribute dict from one OTLP span,
    already stripped of any content the source chose to redact.
    """
    model_id = attributes.get("gen_ai.request.model") or attributes.get(
        "gen_ai.response.model", "unknown-model"
    )

    # agent_identity is folded into the hash itself, not stored alongside
    # it as an afterthought — otherwise two different (verified) agents
    # producing the same model+shape combination would collide onto the
    # same version_id and silently inherit whichever one got there first.
    identity_component = agent_identity or "unverified"

    explicit_version = attributes.get("arc.version_id")
    if explicit_version:
        version_id = _hash("strong", identity_component, explicit_version)
        resolution = "strong"
        code_ref = attributes.get("arc.code_ref")
        prompt_hash = attributes.get("arc.prompt_hash")
    else:
        shape = _input_schema_shape(attributes.get("gen_ai.input.messages"))
        version_id = _hash("weak", identity_component, model_id, shape)
        resolution = "weak"
        code_ref = None
        prompt_hash = None

    existing = conn.execute(
        "SELECT 1 FROM agent_versions WHERE version_id = ?", (version_id,)
    ).fetchone()
    if existing:
        return version_id

    conn.execute(
        """INSERT INTO agent_versions
           (version_id, agent_identity, code_ref, prompt_hash, model_id, resolution, signature, created_at)
           VALUES (?, ?, ?, ?, ?, ?, NULL, ?)""",
        (
            version_id,
            agent_identity,
            code_ref,
            prompt_hash,
            model_id,
            resolution,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    return version_id


def sign_pending_versions(conn: sqlite3.Connection, wallet_address: str, chain: str) -> int:
    """Sign every unsigned version's manifest (ADR-005) — decoupled from
    the hot ingest path since it shells out to the Circle CLI.
    Returns the number signed.
    """
    rows = conn.execute(
        "SELECT version_id, code_ref, prompt_hash, model_id FROM agent_versions WHERE signature IS NULL"
    ).fetchall()
    signed = 0
    for version_id, code_ref, prompt_hash, model_id in rows:
        manifest = f"{version_id}|{code_ref}|{prompt_hash}|{model_id}"
        result = subprocess.run(
            [
                "circle", "wallet", "sign", "message", manifest,
                "--address", wallet_address, "--chain", chain, "--output", "json",
            ],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            continue
        signature = json.loads(result.stdout)["data"]["signature"]
        conn.execute(
            "UPDATE agent_versions SET signature = ? WHERE version_id = ?",
            (signature, version_id),
        )
        signed += 1
    conn.commit()
    return signed
