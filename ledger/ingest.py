"""Generic OTLP ingest endpoint — Phase 2 Milestone 2.0.

Accepts OTLP/HTTP with JSON encoding (OTEL_EXPORTER_OTLP_PROTOCOL=http/json)
at POST /v1/traces, the standard OTLP HTTP path. This is the one interface
external builders and our own dogfooding both use — see ADR-006
(docs/phase2-design-decisions.md): no source-specific adapter code, one
generic receiver.

Scoping note, not an oversight: this pass handles OTLP/HTTP+JSON only, not
protobuf. Most OTel SDKs default to protobuf over HTTP — sources need
OTEL_EXPORTER_OTLP_PROTOCOL=http/json set explicitly. Protobuf support is
a real fast-follow (needs the opentelemetry-proto message definitions,
which is a legitimate dependency to add when a real source requires it,
not something worth hand-rolling against the wire format). Documented
here rather than silently claimed as "any exporter."

Also scoped down for this pass: GenAI message content recorded as a span
*attribute* (a JSON-encoded string) is handled. Content recorded as a span
*event* (the other spec-valid form per docs/phase2-architecture.md §5) is
not yet — same fast-follow note applies.
"""

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ledger.auth import verify_submission
from ledger.resolver import resolve_version
from ledger.store import connect

CONTENT_DIR = Path("ledger_content")

GENAI_SPAN_NAMES = {"invoke_agent", "create_agent", "chat", "execute_tool"}


def _hash_json(value) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _otlp_value(v: dict):
    """Unwrap one OTLP JSON AnyValue into a plain Python value."""
    if "stringValue" in v:
        return v["stringValue"]
    if "intValue" in v:
        return int(v["intValue"])
    if "doubleValue" in v:
        return v["doubleValue"]
    if "boolValue" in v:
        return v["boolValue"]
    if "arrayValue" in v:
        return [_otlp_value(x) for x in v["arrayValue"].get("values", [])]
    if "kvlistValue" in v:
        return {kv["key"]: _otlp_value(kv["value"]) for kv in v["kvlistValue"].get("values", [])}
    return None


def flatten_attributes(attr_list: list) -> dict:
    flat = {}
    for a in attr_list or []:
        flat[a["key"]] = _otlp_value(a.get("value", {}))
    # gen_ai.input.messages / gen_ai.output.messages are commonly recorded
    # as a JSON-encoded string attribute — decode it if so.
    for key in ("gen_ai.input.messages", "gen_ai.output.messages"):
        if isinstance(flat.get(key), str):
            try:
                flat[key] = json.loads(flat[key])
            except (json.JSONDecodeError, TypeError):
                pass  # leave as raw string; not our job to reject on this alone
    return flat


def record_span(conn: sqlite3.Connection, span: dict, agent_identity: str) -> tuple[bool, str]:
    attrs = flatten_attributes(span.get("attributes", []))

    if not (attrs.get("gen_ai.request.model") or attrs.get("gen_ai.response.model")):
        return False, "missing required attribute: gen_ai.request.model or gen_ai.response.model"

    op_id = span.get("spanId")
    trace_id = span.get("traceId")
    if not op_id or not trace_id:
        return False, "missing required field: spanId or traceId"

    version_id = resolve_version(conn, attrs, agent_identity)

    operation_type = span.get("name") if span.get("name") in GENAI_SPAN_NAMES else span.get("name", "unknown")

    input_messages = attrs.get("gen_ai.input.messages")
    output_messages = attrs.get("gen_ai.output.messages")
    input_hash = _hash_json(input_messages) if input_messages is not None else _hash_json(
        {k: v for k, v in attrs.items() if k not in ("gen_ai.input.messages", "gen_ai.output.messages")}
    )
    output_hash = _hash_json(output_messages) if output_messages is not None else None

    content_ref = None
    if input_messages is not None or output_messages is not None:
        CONTENT_DIR.mkdir(exist_ok=True)
        content_ref = str(CONTENT_DIR / f"{op_id}.json")
        Path(content_ref).write_text(
            json.dumps({"input": input_messages, "output": output_messages}, indent=2)
        )

    status_code = (span.get("status") or {}).get("code", "STATUS_CODE_UNSET")
    status = {"STATUS_CODE_OK": "ok", "STATUS_CODE_ERROR": "error"}.get(status_code, "unset")

    started_at = _nano_to_iso(span.get("startTimeUnixNano"))
    ended_at = _nano_to_iso(span.get("endTimeUnixNano")) if span.get("endTimeUnixNano") else None

    token_usage = json.dumps({
        k: v for k, v in attrs.items() if k.startswith("gen_ai.usage.")
    })

    conn.execute(
        """INSERT OR IGNORE INTO operations
           (op_id, trace_id, version_id, operation_type, input_hash, output_hash,
            content_ref, token_usage, status, started_at, ended_at, epoch_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)""",
        (op_id, trace_id, version_id, operation_type, input_hash, output_hash,
         content_ref, token_usage, status, started_at, ended_at),
    )
    conn.commit()
    return True, op_id


def _nano_to_iso(nanos) -> str:
    if not nanos:
        return datetime.now(timezone.utc).isoformat()
    return datetime.fromtimestamp(int(nanos) / 1e9, tz=timezone.utc).isoformat()


def make_handler(db_path: str):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass  # quiet by default; rely on response bodies for diagnostics

        def do_GET(self):
            if self.path == "/health":
                self._respond(200, {"status": "ok"})
            else:
                self._respond(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/v1/traces":
                self._respond(404, {"error": "not found"})
                return
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length)

            claimed_wallet = self.headers.get("X-Arc-Wallet")
            signature = self.headers.get("X-Arc-Signature")
            if not claimed_wallet or not signature:
                self._respond(401, {"error": "missing X-Arc-Wallet / X-Arc-Signature headers"})
                return
            if not verify_submission(raw_body, signature, claimed_wallet):
                self._respond(401, {"error": "signature verification failed for claimed wallet"})
                return

            try:
                payload = json.loads(raw_body)
            except json.JSONDecodeError:
                self._respond(400, {"error": "invalid JSON body"})
                return

            conn = connect(db_path)
            accepted, rejected = [], []
            for rs in payload.get("resourceSpans", []):
                for ss in rs.get("scopeSpans", []):
                    for span in ss.get("spans", []):
                        ok, detail = record_span(conn, span, claimed_wallet)
                        (accepted if ok else rejected).append(detail)
            conn.close()

            status = 200 if accepted or not rejected else 400
            self._respond(status, {"accepted": accepted, "rejected": rejected, "verified_wallet": claimed_wallet})

        def _respond(self, status: int, body: dict):
            data = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return Handler


def serve(db_path: str = "ledger.db", port: int = 4318) -> None:
    """4318 is OTLP's conventional HTTP port."""
    server = ThreadingHTTPServer(("localhost", port), make_handler(db_path))
    print(f"ledger ingest listening on http://localhost:{port}/v1/traces (db={db_path})")
    server.serve_forever()


if __name__ == "__main__":
    serve()
