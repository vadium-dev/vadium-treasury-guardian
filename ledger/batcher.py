"""Epoch batcher — seals unsealed operations into a Merkle-anchored epoch.

Per ADR-008 (docs/phase2-design-decisions.md): seal at 100 operations or
15 minutes, whichever comes first. Idempotent and safe to run on a
schedule, same pattern as scripts/poll_spend.py — not a daemon.

On-chain anchoring (D1: circle wallet execute against AnchorLog) is
intentionally NOT wired in this pass — the contract doesn't exist yet.
seal_epoch() leaves anchor_tx_hash NULL; wiring the anchor call is the
next concrete step, not silently faked here.
"""

import hashlib
from datetime import datetime, timedelta, timezone

from ledger.anchor import write_anchor
from ledger.merkle import build_tree, root_of, proof_for
from ledger.store import connect

SEAL_COUNT_THRESHOLD = 100
SEAL_AGE_THRESHOLD = timedelta(minutes=15)


def _leaf_value(op_row) -> str:
    op_id, input_hash, output_hash, version_id, started_at = op_row
    return f"{op_id}|{input_hash}|{output_hash}|{version_id}|{started_at}"


def _epoch_id(prev_epoch_id, merkle_root, sealed_at) -> str:
    h = hashlib.sha256()
    for part in (prev_epoch_id or "", merkle_root, sealed_at):
        h.update(part.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def seal_epoch(db_path: str = "ledger.db", wallet_address: str | None = None) -> str | None:
    """Seals one epoch if either threshold is met. Returns the new
    epoch_id, or None if nothing needed sealing."""
    conn = connect(db_path)
    try:
        unsealed = conn.execute(
            """SELECT op_id, input_hash, output_hash, version_id, started_at
               FROM operations WHERE epoch_id IS NULL ORDER BY started_at ASC"""
        ).fetchall()
        if not unsealed:
            return None

        oldest_age = datetime.now(timezone.utc) - datetime.fromisoformat(unsealed[0][4])
        if len(unsealed) < SEAL_COUNT_THRESHOLD and oldest_age < SEAL_AGE_THRESHOLD:
            return None

        batch = unsealed[:SEAL_COUNT_THRESHOLD]
        leaves = [_leaf_value(row) for row in batch]
        levels = build_tree(leaves)
        merkle_root = root_of(levels)

        prev = conn.execute(
            "SELECT epoch_id FROM epochs ORDER BY sealed_at DESC LIMIT 1"
        ).fetchone()
        prev_epoch_id = prev[0] if prev else None

        sealed_at = datetime.now(timezone.utc).isoformat()
        epoch_id = _epoch_id(prev_epoch_id, merkle_root, sealed_at)

        conn.execute(
            """INSERT INTO epochs (epoch_id, prev_epoch_id, merkle_root, op_count, sealed_at)
               VALUES (?, ?, ?, ?, ?)""",
            (epoch_id, prev_epoch_id, merkle_root, len(batch), sealed_at),
        )
        for i, row in enumerate(batch):
            op_id = row[0]
            conn.execute(
                "UPDATE operations SET epoch_id = ? WHERE op_id = ?", (epoch_id, op_id)
            )
            conn.execute(
                "INSERT INTO epoch_members (epoch_id, op_id, leaf_index, leaf_hash) VALUES (?, ?, ?, ?)",
                (epoch_id, op_id, i, levels[0][i]),
            )
        conn.commit()

        if wallet_address:
            # Best-effort inline anchor. A failure here does NOT undo the
            # seal — sealing must not block on a flaky chain call. Left
            # NULL on failure for anchor_pending_epochs() (D2) to retry.
            try:
                tx_hash = write_anchor(merkle_root, prev_epoch_id and _prev_root(conn, prev_epoch_id), wallet_address)
                conn.execute(
                    "UPDATE epochs SET anchor_tx_hash = ?, anchored_at = ? WHERE epoch_id = ?",
                    (tx_hash, datetime.now(timezone.utc).isoformat(), epoch_id),
                )
                conn.commit()
            except RuntimeError as exc:
                print(f"warning: epoch {epoch_id} sealed but anchor write failed: {exc}")

        return epoch_id
    finally:
        conn.close()


def _prev_root(conn, prev_epoch_id: str) -> str | None:
    row = conn.execute(
        "SELECT merkle_root FROM epochs WHERE epoch_id = ?", (prev_epoch_id,)
    ).fetchone()
    return row[0] if row else None


def anchor_pending_epochs(db_path: str = "ledger.db", wallet_address: str = "") -> int:
    """D2: retry any sealed-but-unanchored epoch. Returns count anchored."""
    conn = connect(db_path)
    try:
        pending = conn.execute(
            "SELECT epoch_id, merkle_root, prev_epoch_id FROM epochs WHERE anchor_tx_hash IS NULL"
        ).fetchall()
        anchored = 0
        for epoch_id, merkle_root, prev_epoch_id in pending:
            prev_root = _prev_root(conn, prev_epoch_id) if prev_epoch_id else None
            try:
                tx_hash = write_anchor(merkle_root, prev_root, wallet_address)
            except RuntimeError as exc:
                print(f"warning: retry failed for epoch {epoch_id}: {exc}")
                continue
            conn.execute(
                "UPDATE epochs SET anchor_tx_hash = ?, anchored_at = ? WHERE epoch_id = ?",
                (tx_hash, datetime.now(timezone.utc).isoformat(), epoch_id),
            )
            conn.commit()
            anchored += 1
        return anchored
    finally:
        conn.close()


if __name__ == "__main__":
    result = seal_epoch()
    print(f"sealed epoch: {result}" if result else "nothing to seal")
