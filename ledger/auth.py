"""Identity binding for ingest — closes the hole Milestone 2.0 shipped
with: the ingest endpoint originally accepted a POST from anyone,
claiming to be any agent, with nothing checking the claim.

Circle agent wallets are smart-contract accounts (confirmed when
deploying AnchorLog — msg.sender in a constructor is the deployer
factory, not the wallet). That rules out plain ecrecover-based signature
verification: there's no single keypair whose signature recovers to the
wallet's own address. Verified empirically instead of assumed (see
docs/SETUP.md): `circle wallet sign message` produces a standard EIP-191
personal-sign hash, and the wallet validates it via **ERC-1271**
(`isValidSignature(bytes32,bytes)`, returning the magic value
`0x1626ba7e`) — called on the wallet contract itself, on-chain, the same
`circle contract query` pattern already proven for AnchorLog. No local
ecrecover, no eth-account dependency needed — just keccak256 to compute
the hash being checked.
"""

import json
import os
import subprocess

from eth_utils import keccak

CHAIN = os.environ.get("ANCHORLOG_CHAIN", "ARC-TESTNET")
ERC1271_MAGIC_VALUE = "0x1626ba7e"
NAMESPACE = "arc-ledger-ingest:v1"


def signed_message(raw_body: bytes) -> str:
    """The exact string a submitter must sign — namespaced so a signature
    produced for this purpose can't be replayed as authorization for
    something else, and bound to the payload's own hash so a signature
    only authorizes that exact submission."""
    import hashlib
    return f"{NAMESPACE}:{hashlib.sha256(raw_body).hexdigest()}"


def _eip191_hash(message: str) -> str:
    msg_bytes = message.encode("utf-8")
    digest = keccak(b"\x19Ethereum Signed Message:\n" + str(len(msg_bytes)).encode() + msg_bytes)
    return "0x" + digest.hex()


def sign_for_submission(raw_body: bytes, wallet_address: str) -> str:
    """Client-side helper: what a forwarder/sender calls to produce the
    signature header for a given payload."""
    message = signed_message(raw_body)
    result = subprocess.run(
        [
            "circle", "wallet", "sign", "message", message,
            "--address", wallet_address, "--chain", CHAIN, "--output", "json",
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"signing failed: {result.stderr.strip()}")
    return json.loads(result.stdout)["data"]["signature"]


def verify_submission(raw_body: bytes, signature: str, claimed_wallet: str) -> bool:
    """Server-side check: does `signature` actually come from
    `claimed_wallet` for exactly this `raw_body`? Verified on-chain
    against the wallet's own ERC-1271 implementation — never trust a
    locally-recomputed answer for something a wallet contract can answer
    authoritatively itself.
    """
    message = signed_message(raw_body)
    hash_hex = _eip191_hash(message)
    result = subprocess.run(
        [
            "circle", "contract", "query", "isValidSignature(bytes32,bytes)",
            hash_hex, signature,
            "--contract", claimed_wallet, "--chain", CHAIN, "--output", "json",
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return False  # not a wallet, not deployed, or query failed — fail closed
    output_data = json.loads(result.stdout)["data"]["outputData"]
    return output_data.lower().startswith(ERC1271_MAGIC_VALUE.lower())
