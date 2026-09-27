"""Minimal binary Merkle tree — shared by the batcher (build) and verify (prove)."""

import hashlib


def _h(*parts: bytes) -> str:
    hasher = hashlib.sha256()
    for p in parts:
        hasher.update(p)
    return hasher.hexdigest()


def _leaf_hash(value: str) -> str:
    return _h(b"\x00", value.encode("utf-8"))  # leaf prefix, avoids leaf/node hash collision


def _node_hash(left: str, right: str) -> str:
    return _h(b"\x01", bytes.fromhex(left), bytes.fromhex(right))


def leaf_hash(value: str) -> str:
    """Public wrapper — callers that need to freeze a leaf hash at
    sealing time (see ledger/batcher.py) use this directly."""
    return _leaf_hash(value)


def build_tree(leaf_values: list[str]) -> list[list[str]]:
    """Returns levels[0] = leaf hashes, ..., levels[-1] = [root].
    Odd nodes at any level are promoted by duplicating the last one.
    """
    if not leaf_values:
        raise ValueError("cannot build a Merkle tree over zero leaves")
    levels = [[_leaf_hash(v) for v in leaf_values]]
    while len(levels[-1]) > 1:
        level = levels[-1]
        if len(level) % 2 == 1:
            level = level + [level[-1]]
        levels.append([_node_hash(level[i], level[i + 1]) for i in range(0, len(level), 2)])
    return levels


def build_tree_from_hashes(leaf_hashes: list[str]) -> list[list[str]]:
    """Same as build_tree(), but the inputs are already leaf hashes —
    used at verify time to rebuild from FROZEN hashes captured at sealing
    time, not re-derived from (possibly since-tampered) live data. This
    is what isolates a tamper to the one leaf that changed, instead of
    invalidating the whole epoch — see the docstring in ledger/verify.py.
    """
    if not leaf_hashes:
        raise ValueError("cannot build a Merkle tree over zero leaves")
    levels = [list(leaf_hashes)]
    while len(levels[-1]) > 1:
        level = levels[-1]
        if len(level) % 2 == 1:
            level = level + [level[-1]]
        levels.append([_node_hash(level[i], level[i + 1]) for i in range(0, len(level), 2)])
    return levels


def root_of(levels: list[list[str]]) -> str:
    return levels[-1][0]


def proof_for(levels: list[list[str]], leaf_index: int) -> list[tuple[str, str]]:
    """Returns [(sibling_hash, 'L'|'R'), ...] from leaf to root."""
    proof = []
    idx = leaf_index
    for level in levels[:-1]:
        level_padded = level if len(level) % 2 == 0 else level + [level[-1]]
        sibling_idx = idx ^ 1
        side = "R" if sibling_idx > idx else "L"
        proof.append((level_padded[sibling_idx], side))
        idx //= 2
    return proof


def verify_proof(leaf_value: str, proof: list[tuple[str, str]], root: str) -> bool:
    return verify_proof_from_hash(_leaf_hash(leaf_value), proof, root)


def verify_proof_from_hash(leaf_hash_value: str, proof: list[tuple[str, str]], root: str) -> bool:
    current = leaf_hash_value
    for sibling, side in proof:
        current = _node_hash(current, sibling) if side == "R" else _node_hash(sibling, current)
    return current == root
