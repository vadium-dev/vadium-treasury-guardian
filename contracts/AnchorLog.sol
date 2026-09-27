// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @notice Minimal Merkle-root anchor log for the Phase 2 evidence ledger.
/// Stores only a root + back-pointer per epoch — never raw content. See
/// docs/phase2-architecture.md §3/§4 and ADR-003/ADR-004 in
/// docs/phase2-design-decisions.md for why: batching + anchoring keeps
/// on-chain cost to a Merkle root per epoch instead of one write per
/// operation, and content never has to leave the off-chain ledger.
contract AnchorLog {
    address public immutable owner;

    struct Anchor {
        bytes32 root;
        bytes32 prevRoot;
        uint256 timestamp;
    }

    Anchor[] public anchors;
    mapping(bytes32 => uint256) private rootIndexPlusOne; // 0 = not found

    event Anchored(uint256 indexed index, bytes32 indexed root, bytes32 prevRoot, uint256 timestamp);

    /// @param _owner passed explicitly rather than using msg.sender —
    /// Circle agent wallets are smart-contract accounts deployed via a
    /// factory/bundler, so msg.sender in the constructor is the factory,
    /// not the wallet that will actually call anchor() later.
    constructor(address _owner) {
        owner = _owner;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "AnchorLog: not owner");
        _;
    }

    function anchor(bytes32 root, bytes32 prevRoot) external onlyOwner returns (uint256 index) {
        index = anchors.length;
        anchors.push(Anchor(root, prevRoot, block.timestamp));
        rootIndexPlusOne[root] = index + 1;
        emit Anchored(index, root, prevRoot, block.timestamp);
    }

    function getAnchor(uint256 index) external view returns (bytes32 root, bytes32 prevRoot, uint256 timestamp) {
        Anchor memory a = anchors[index];
        return (a.root, a.prevRoot, a.timestamp);
    }

    function isAnchored(bytes32 root) external view returns (bool) {
        return rootIndexPlusOne[root] != 0;
    }

    function anchorCount() external view returns (uint256) {
        return anchors.length;
    }
}
