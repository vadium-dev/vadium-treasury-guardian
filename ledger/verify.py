"""verify(op_id) — Epic E1, now checking the chain (D1) with tamper
isolation (fixed after Milestone 2.0's own smoke test found a real gap).

Two bugs were found and fixed building this, in order:

1. Comparing a recomputed root against the *locally stored*
   epochs.merkle_root proved nothing — an attacker able to tamper with
   `operations` could tamper with `epochs.merkle_root` too, since both
   live in the same database. Fixed by checking the chain instead
   (ledger/anchor.py's is_anchored()) — the one thing not under our own
   control.

2. Even after fixing (1), tampering with ONE operation still invalidated
   verification for every operation in its epoch. Cause: the tree was
   rebuilt from live `operations` data every time, so one changed leaf
   changes the recomputed root for the WHOLE batch — correctly proving
   "something in this epoch doesn't match what was anchored," but unable
   to say *which* leaf, and unable to still vouch for the untouched ones.
   Fixed by freezing each leaf's hash in epoch_members.leaf_hash at
   sealing time (ledger/batcher.py) and rebuilding the tree from those
   frozen hashes, not from live data. Now: (a) a specific operation's
   current data is checked against its own frozen hash — tampering with
   it is caught precisely; (b) the tree used for the chain check is built
   from frozen hashes, so one tampered operation doesn't corrupt the
   proof for its siblings.
"""

from ledger.anchor import is_anchored
from ledger.merkle import build_tree_from_hashes, leaf_hash, proof_for, verify_proof_from_hash
from ledger.store import connect


def verify(op_id: str, db_path: str = "ledger.db") -> bool:
    conn = connect(db_path)
    try:
        op = conn.execute(
            "SELECT op_id, input_hash, output_hash, version_id, started_at, epoch_id FROM operations WHERE op_id = ?",
            (op_id,),
        ).fetchone()
        if not op or not op[5]:
            return False  # unknown operation, or not yet sealed into an epoch

        epoch_id = op[5]
        current_leaf_value = f"{op[0]}|{op[1]}|{op[2]}|{op[3]}|{op[4]}"

        member = conn.execute(
            "SELECT leaf_index, leaf_hash FROM epoch_members WHERE epoch_id = ? AND op_id = ?",
            (epoch_id, op_id),
        ).fetchone()
        if not member:
            return False
        leaf_index, frozen_hash = member

        # Bug #2's fix, part A: does this operation's CURRENT data still
        # match what was frozen at sealing time? If not, it — specifically
        # it, not its epoch siblings — was tampered with after the fact.
        if leaf_hash(current_leaf_value) != frozen_hash:
            return False

        # Rebuild the tree from FROZEN hashes of every member — not from
        # live operation data — so a tampered sibling can't corrupt this
        # operation's own proof.
        members = conn.execute(
            "SELECT leaf_hash FROM epoch_members WHERE epoch_id = ? ORDER BY leaf_index ASC",
            (epoch_id,),
        ).fetchall()
        frozen_leaves = [m[0] for m in members]
        levels = build_tree_from_hashes(frozen_leaves)
        recomputed_root = levels[-1][0]

        # Bug #1's fix: trust the chain, not our own epochs table, for
        # whether this root was really anchored.
        if not is_anchored(recomputed_root):
            return False

        proof = proof_for(levels, leaf_index)
        return verify_proof_from_hash(frozen_hash, proof, recomputed_root)
    finally:
        conn.close()
