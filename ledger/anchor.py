"""D1: write epoch roots to AnchorLog on Arc, and read them back for verify().

Deployed contract (ARC-TESTNET, see docs/SETUP.md): 0xf3d5ecfb7b89dcc8b181191e5782edb5bb5f6fa2
Owner (the only address allowed to call anchor()): 0x752942377f0e8a1e8ccb4273550ac7320c2a6755
"""

import json
import os
import subprocess

CONTRACT_ADDRESS = os.environ.get("ANCHORLOG_CONTRACT", "0xf3d5ecfb7b89dcc8b181191e5782edb5bb5f6fa2")
CHAIN = os.environ.get("ANCHORLOG_CHAIN", "ARC-TESTNET")


def _zero_bytes32() -> str:
    return "0x" + "0" * 64


def _fmt(root: str) -> str:
    """merkle.py's hashes come back as bare 64-char hex, no 0x prefix —
    normalize here rather than trust every call site to remember."""
    return root if root.startswith("0x") else "0x" + root


def write_anchor(root: str, prev_root: str | None, wallet_address: str) -> str:
    """Calls anchor(root, prevRoot). Returns the transaction hash.
    Raises RuntimeError on failure — the caller (batcher) decides whether
    to retry (D2) rather than this function silently swallowing it.
    """
    result = subprocess.run(
        [
            "circle", "wallet", "execute", "anchor(bytes32,bytes32)",
            _fmt(root), _fmt(prev_root) if prev_root else _zero_bytes32(),
            "--contract", CONTRACT_ADDRESS,
            "--address", wallet_address,
            "--chain", CHAIN,
            "--output", "json",
        ],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"anchor write failed: {result.stderr.strip()}")
    data = json.loads(result.stdout)["data"]
    if data.get("state") != "COMPLETE":
        raise RuntimeError(f"anchor write did not complete: {data}")
    return data["txHash"]


def is_anchored(root: str) -> bool:
    """Reads isAnchored(root) directly from chain — this is the check
    that makes verify() trust Arc instead of our own database.
    """
    result = subprocess.run(
        [
            "circle", "contract", "query", "isAnchored(bytes32)", _fmt(root),
            "--contract", CONTRACT_ADDRESS,
            "--chain", CHAIN,
            "--output", "json",
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"isAnchored query failed: {result.stderr.strip()}")
    output_data = json.loads(result.stdout)["data"]["outputData"]
    return int(output_data, 16) == 1
