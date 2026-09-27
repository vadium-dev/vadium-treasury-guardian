"""Local signing forwarder — reconciles two goals that are otherwise in
tension: Epic B1's "point your existing exporter at us, zero new code in
the agent" promise, and the auth fix in ledger/auth.py requiring every
submission to be signed. A stock OTel exporter (Claude Code's native
telemetry included) has no idea what a Circle wallet is and can't sign
anything.

The fix follows the standard sidecar/proxy pattern: the exporter's
config points at THIS process instead of the real ingest endpoint
directly. The forwarder receives plain, unsigned OTLP, signs it with a
configured wallet, and forwards it on. The agent's own code and export
config change not at all beyond the endpoint URL — a config value, not a
code change — which is what "zero new code" actually meant to promise.

For a seller who isn't us: they'd run this same forwarder locally (or a
packaged equivalent) in front of their own exporter's target, using
their own wallet address. It's the general answer, not a special case
for our own dogfooding.
"""

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ledger.auth import sign_for_submission

WALLET_ADDRESS = os.environ.get("ARC_FORWARDER_WALLET", "0x752942377f0e8a1e8ccb4273550ac7320c2a6755")
UPSTREAM = os.environ.get("ARC_INGEST_URL", "http://localhost:4318/v1/traces")


def make_handler():
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def do_POST(self):
            if self.path != "/v1/traces":
                self._respond(404, {"error": "not found"})
                return
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length)

            try:
                signature = sign_for_submission(raw_body, WALLET_ADDRESS)
            except RuntimeError as exc:
                self._respond(502, {"error": f"forwarder could not sign payload: {exc}"})
                return

            req = urllib.request.Request(
                UPSTREAM, data=raw_body, method="POST",
                headers={
                    "Content-Type": "application/json",
                    "X-Arc-Wallet": WALLET_ADDRESS,
                    "X-Arc-Signature": signature,
                },
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    body, status = resp.read(), resp.status
            except urllib.error.HTTPError as exc:
                body, status = exc.read(), exc.code

            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _respond(self, status: int, body: dict):
            data = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return Handler


def serve(port: int = 4319) -> None:
    server = ThreadingHTTPServer(("localhost", port), make_handler())
    print(f"signing forwarder listening on http://localhost:{port}/v1/traces "
          f"-> signs as {WALLET_ADDRESS} -> forwards to {UPSTREAM}")
    server.serve_forever()


if __name__ == "__main__":
    serve()
