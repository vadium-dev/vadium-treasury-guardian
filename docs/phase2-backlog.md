# Phase 2 Backlog — Evidence & Instrumentation Layer

User stories grouped by epic, each tagged with the milestone it belongs to
and a priority (P0 = required for that milestone to be meaningful, P1 =
fast follow, P2 = can slip). Acceptance criteria are the definition of
done, not a spec of implementation.

Milestones, corrected from an earlier draft that staged a Claude-Code-only
path before a "real" generic one (backwards — see ADR-006):
- **2.0** — the generic OTLP ingest endpoint exists and is proven against
  our own agent, via whichever existing export path already fits its
  runtime. No source-specific adapter code.
- **2.1** — hardened for external builders, plus copy-paste config docs
  for the top ingestion paths (Claude Code, Traceloop, raw OTel SDK).
- **2.2** — gap-fill only: custom instrumentation for a confirmed-absent
  OTel path, contributed upstream rather than kept proprietary.

## Epic A — Version resolution & attestation

**A1. As the ledger, I need a stable identifier for the exact
code+prompt+model combination that produced an operation, so a dispute
can be traced to precisely one version.** *(2.0, P0)*
- Given the same code_ref, prompt_hash, and model_id, `version_id` is
  identical across calls.
- Given any one of the three changes, `version_id` changes.
- A new `version_id` triggers creation of an `agent_versions` row, not a
  duplicate.

**A2. As the ledger, I need each new version's manifest signed with the
agent's own wallet key, so the attestation is verifiable without a
separate identity system.** *(2.0, P0)*
- `circle wallet sign` is called over `(code_ref, prompt_hash, model_id)`
  exactly once per new `version_id`.
- The signature is stored and independently verifiable against the
  agent's known wallet address.

**A3. As a future ERC-8004 registrant, I want `agent_identity` to be
nullable until registration happens, so Phase 2 doesn't block on Phase 3
being built.** *(2.0, P0)*
- `agent_versions.agent_identity` accepts NULL.
- A later backfill can populate it once ERC-8004 registration exists,
  without altering existing rows' `version_id`.

## Epic B — Universal operation recording (framework-agnostic by construction)

Reframed from an earlier draft that made this Claude-Code-specific — that
was a mistake, not a starting point to build on. The interface is OTLP
itself, not any one source's plugin. See ADR-006.

**B1. As any agent builder whose stack already emits OTel-compliant
traces — natively (Claude Code), via Traceloop/OpenLLMetry
(OpenAI/Anthropic/Gemini/Bedrock/LangChain/LlamaIndex/CrewAI/20+ others),
via Langfuse, or via a raw OTel SDK — I want to point one exporter or set
one environment variable at your endpoint and start getting evidence
recorded, with zero new code written for your system specifically.**
*(2.0, P0)*
- A valid OTLP POST from any of the four source types above produces
  exactly one `operations` row, in the same shape regardless of source.
- `operation_type` matches OTel GenAI semconv values (`invoke_agent`,
  `execute_tool`, `chat`) as emitted by the source — the ingest endpoint
  does not require a source-specific parser branch per source type.
- A span missing required GenAI attributes is rejected with a clear
  error, not silently dropped or guessed at.

**B2. As the builder of our own oracle agent, I want it instrumented via
whichever existing OTel export path already fits its runtime — not a
bespoke integration we wrote for ourselves — so dogfooding proves the
generic path works, not a special case of it.** *(2.0, P0)*
- The oracle/registry agent's chosen runtime's existing exporter (Claude
  Code native telemetry, or Traceloop if it calls a provider Traceloop
  covers) is configured to point at our endpoint from its first commit.
- No source-specific code exists in this project for that agent's
  instrumentation — only endpoint configuration.

**B3. As a builder, I want copy-paste setup instructions for the top
ingestion paths, so "flipping this on" is a documentation lookup, not an
integration project.** *(2.1, P0)*
- Published snippets exist for at minimum: Claude Code (the two env
  vars), Traceloop one-line init pointed at our OTLP endpoint, and a raw
  OTel SDK exporter config. Each is copy-paste complete, not partial.

**B4. As a privacy-conscious builder, I want to redact specific fields
from what gets recorded, so I can get a valid record without disclosing
sensitive content.** *(2.0, P1)*
- An incoming span with content fields stripped (or a source configured
  not to record content, which OTel's own GenAI conventions already
  support as an opt-out) produces a row with `content_ref = NULL` and
  valid `input_hash`/`output_hash` computed from whatever is present.
- The resulting operation still passes Merkle inclusion verification (A2,
  D-epic below) identically to a non-redacted one.

**B5. As the ledger, I want a failed or partial operation recorded too,
not silently dropped, so the audit trail doesn't have gaps that look like
tampering.** *(2.0, P1)*
- A span representing an errored or timed-out operation still produces a
  row, with `status` reflecting the failure and `ended_at` possibly NULL.

**B6. As the ledger, I want a direct-call fallback for a source that
genuinely cannot emit OTLP, so coverage isn't strictly all-or-nothing —
without presenting this as the recommended path.** *(2.2, P2)*
- `record_operation(...)` exists and produces an identical row shape to
  the OTLP path.
- Documentation lists this only after the OTLP paths, explicitly as a
  fallback.

## Epic C — Epoch batching

**C1. As the batcher, I want to seal an epoch at 100 unsealed operations
or 15 minutes, whichever comes first, so cost and tamper-exposure window
are both bounded.** *(2.0, P0, see ADR-008)*
- A cron run with ≥100 unsealed operations seals exactly one epoch of 100.
- A cron run with <100 unsealed operations but the oldest one >15 minutes
  old seals an epoch of whatever is pending.
- A cron run with nothing unsealed does nothing (idempotent, matches
  `poll_spend.py`'s existing re-run-safe pattern).

**C2. As the batcher, I want each epoch to reference the previous epoch's
root, so the chain of epochs is itself tamper-evident, not just each
epoch internally.** *(2.0, P0)*
- `epochs.prev_epoch_id` is set correctly on every epoch after the first.
- Recomputing the chain from `epochs` alone detects a missing or
  reordered epoch.

**C3. As a developer, I want `epoch_members` to let me reconstruct a
Merkle proof for any operation in a sealed epoch, so verification doesn't
require re-deriving the whole tree from scratch each time.** *(2.0, P0)*
- Given an `op_id`, the stored `leaf_index` plus sibling hashes
  reconstructs a valid proof against `epochs.merkle_root`.

## Epic D — Arc anchoring

**D1. As the batcher, I want a sealed epoch's root committed to a minimal
Arc contract, so the epoch is independently verifiable without trusting
our database.** *(2.0, P0)*
- A deployed `AnchorLog` contract accepts `anchor(bytes32 root, bytes32
  prevRoot)` and emits an event with both values plus a timestamp.
- After a successful `circle wallet execute` call, the epoch's
  `anchor_tx_hash` and `anchored_at` are populated.

**D2. As the batcher, I want a failed anchor write to retry rather than
silently leave an epoch unanchored, so gaps don't accumulate
unnoticed.** *(2.0, P1)*
- A cron run finds any epoch with `anchor_tx_hash IS NULL` older than one
  retry interval and re-attempts the anchor call before sealing new
  epochs.

**D3. As anyone, I want to read an anchored root directly from Arc without
needing write access or an API key, so verification doesn't depend on us
staying operational.** *(2.0, P1)*
- `AnchorLog`'s root-by-epoch lookup is a public view function, callable
  by any RPC client.

## Epic E — Verification

**E1. As a Phase 3 validator, I want to call `verify(op_id)` and get a
boolean, so Tier 0 evidence checks don't need custom logic per
integration.** *(2.0, P0)*
- `verify(op_id)` fetches the operation, its epoch's Merkle proof, and the
  onchain root, recomputes, and returns true only on an exact match.
- A tampered operation row (any field altered post-sealing) returns false.

**E2. As an external auditor, I want to verify an operation without
running our code, so the guarantee doesn't depend on trusting our
implementation.** *(2.1, P1)*
- The verification algorithm (Merkle proof recomputation against a
  publicly-read onchain root) is documented plainly enough
  (`docs/phase2-architecture.md` §5c) that a third party could reimplement
  it independently.

## Epic F — Opening the endpoint to external builders (Milestone 2.1)

The endpoint itself is built and proven in 2.0 (Epic B) — this epic is
what changes when traffic stops being just our own agent's.

**F1. As an external builder, I want my traces kept separate from every
other builder's, so multi-tenant use doesn't leak or cross-attribute
data.** *(2.1, P0)*
- Incoming spans are scoped to the submitting agent's identity (wallet
  address or, once registered, ERC-8004 `agentId`) and no query path
  returns another agent's operations without explicit authorization.

**F2. As the endpoint operator, I want basic rate limiting and malformed-
payload handling before opening this beyond our own traffic, so one
misbehaving external source can't degrade the ledger for everyone.**
*(2.1, P0)*
- A source exceeding a defined rate is throttled with a standard
  retry-after response, not silently dropped or allowed to overwhelm the
  batcher.

**F3. As an external builder, I want to see which of my sellers already
have Phase 2 evidence versus none at all, so I know who qualifies for the
Phase 3 bond discount.** *(2.1, P1, depends on Phase 3 existing)*
- A lookup by `agent_identity` returns a count of anchored operations and
  the most recent `epoch_id`, or an explicit "no evidence" result.

## Epic G — Gap-fill instrumentation (Milestone 2.2, exception not default)

Reframed: Traceloop/OpenLLMetry already auto-instruments LangChain,
LlamaIndex, CrewAI, and 15+ others. Building our own parallel adapters for
frameworks an existing open-source project already covers would duplicate
effort and fragment the ecosystem in exactly the way OTel's own
consolidation (unifying OpenTracing and OpenCensus rather than adding a
third competing standard) avoided. This epic exists only for genuine gaps.

**G1. As the project, I want an actual audit of which real, high-value
agent stacks have no existing OTel export path at all, before writing any
gap-fill code, so effort goes where it's actually needed rather than
where it's assumed to be needed.** *(2.2, P1)*
- A documented list exists of specific frameworks/SDKs checked and
  confirmed to have no OTel path (native or via Traceloop/Langfuse), with
  the date checked — this list is expected to shrink over time as
  upstream coverage grows, and should be re-checked before acting on it.

**G2. As a builder on a stack confirmed to have no existing OTel path
(per G1), I want a thin instrumentation contributed upstream to the
relevant open project, so the fix benefits the whole ecosystem, not just
our own ledger.** *(2.2, P2)*
- A pull request (or equivalent contribution) exists against the
  upstream project (e.g. OpenLLMetry) implementing the missing coverage,
  emitting GenAI-conformant spans identical in shape to any other source.
- We consume our own contribution the same way we'd consume anyone else's
  — no special-cased ingest logic for it.

## Explicitly out of scope for Phase 2

- Any Phase 3 concern: bonding, reputation scoring, dispute adjudication.
  Phase 2 produces evidence; it doesn't judge it.
- Real-time/streaming verification — `verify()` is a pull, not a push;
  nothing here promises sub-second detection of tampering.
- Multi-tenant ingest at scale — Milestone 2.1's endpoint is designed for
  correctness first; load characteristics are an explicit open risk in
  the architecture doc, not solved here.
