# Phase 2 Design Decisions

Lightweight ADR log — one entry per real decision point, why it went that
way, and what would make us revisit it. Numbered in the order decided, not
by importance.

## ADR-001: Ingest existing OTel traces, don't build a new SDK

**Decision**: the ledger accepts OpenTelemetry GenAI-conformant spans
(from Langfuse, Traceloop, native OTel, or our own Skill hook) rather than
shipping a proprietary tracing SDK.

**Why**: most agent stacks already emit these traces. A builder with any
OTel-based setup should be able to repoint one exporter, not learn a new
library. Confirmed against the OTel spec directly (`docs/IDEA.md` §5) that
the span/attribute shape we need (`invoke_agent`, `execute_tool`,
`gen_ai.input.messages`) already exists and is stable enough to build on
even at "Development" maturity.

**Revisit if**: OTel's GenAI conventions change incompatibly before
reaching stable status, or a large enough share of target builders turn
out not to use OTel at all (would push us toward the framework-adapter
path being primary instead of a fallback).

## ADR-002: SQLite for the ledger store, not Postgres

**Decision**: the off-chain ledger uses SQLite, same as `scripts/poll_spend.py`.

**Why**: Phase 2's first milestone is dogfooding on our own agent — single
writer, low volume, no concurrent-access requirement yet. Introducing a
second database technology into a project that already has one working
pattern is unjustified until there's a concrete multi-writer or
concurrent-load requirement (Milestone 2.1's external ingest, if it
materializes at real scale, is the actual trigger to revisit — not a
guess in advance).

**Revisit if**: Milestone 2.1 ships and shows concurrent-write contention,
or retention requirements (a real compliance target, once EU AI Act
Article 12 is actually in force) demand replication/backup guarantees
SQLite doesn't give for free.

## ADR-003: Batch-and-anchor, never store the raw log on-chain

**Decision**: only a periodic Merkle root reaches Arc. The full record —
content, hashes, version bindings — stays in the off-chain ledger store.

**Why**: on-chain storage cost and public visibility both rule out storing
raw events per-transaction. Confirmed cost figure (`docs/IDEA.md` §5):
roughly $2.30 per 100,000 events at 100-event epochs on an L2 when
batched, versus prohibitive cost per individual on-chain write. This is
the same batching principle Gateway already uses for nanopayments —
not a novel idea, a proven pattern applied to a second problem.

**Revisit if**: a future L2/L1 fee model makes per-event anchoring
genuinely cheap (unlikely to change the privacy argument, which stands
independent of cost).

## ADR-004: Anchor on Arc specifically, not a separate chain

**Decision**: the `AnchorLog` contract deploys on Arc, not on a
general-purpose chain chosen for cost alone.

**Why**: a seller's ERC-8004 identity, bond, reputation, and audit-log
anchor should all reference the same chain and the same address. Other
teams are already anchoring similar agent-output proofs on unrelated
chains (NEAR, per research in `docs/IDEA.md` §5) — fragmenting our own
stack the same way would give up the coherence advantage of already being
on Arc for everything else.

**Revisit if**: Arc's gas/throughput characteristics change materially
relative to alternatives, or ERC-8004/8183 activity concentrates
elsewhere.

## ADR-005: Reuse the agent's Circle Agent Wallet key for attestation signing

**Decision**: version-attestation manifests are signed with
`circle wallet sign`, using the same key Phase 1's wallet already holds —
no separate PKI or identity system introduced.

**Why**: every agent in this project already has a wallet key by
necessity (it's how it pays/gets paid). Reusing it for signing avoids a
second key-management surface, and it ties the attestation directly to
the same address that will register in ERC-8004's `IdentityRegistry` in
Phase 3 — one identity, not two.

**Revisit if**: ERC-8004 registration ends up requiring a distinct signing
key by convention (not confirmed either way yet — flagged as an open
question in `docs/IDEA.md` §6).

## ADR-006: Build a generic OTLP receiver first; write custom adapter code only for genuine gaps

**Superseded**: an earlier version of this decision was "ship a Claude
Code Skill wired to `PreToolUse`/`PostToolUse` hooks as the first
adapter." That was wrong on its own terms, not just suboptimal — it
special-cased one runtime as the entry point instead of building the
standard interface first, the exact inversion ADR-001 already argued
against. Checked directly rather than assumed: Claude Code already emits
OTLP natively (`CLAUDE_CODE_ENABLE_TELEMETRY=1` +
`OTEL_EXPORTER_OTLP_ENDPOINT`, zero code), so a custom hook-based Skill
would have duplicated an interface that already exists, in a
non-standard, Claude-Code-only shape.

**Decision**: Milestone 2.0 builds one generic OTLP-over-HTTP ingest
endpoint. No source-specific adapter code ships by default. Coverage
comes from what already emits OTLP-compliant traces:

- Claude Code — native export, two environment variables, no code.
- Anything using OpenAI, Anthropic, Gemini, Bedrock, LangChain,
  LlamaIndex, CrewAI, or 15+ other providers/frameworks — via
  Traceloop/OpenLLMetry's existing one-line auto-instrumentation
  (Apache 2.0, already maintained by someone else).
- Anything else already on Langfuse or a native OTel SDK.

Dogfooding on our own agent means picking whichever of these already
fits its runtime and pointing it at our endpoint — not writing bespoke
integration code for it.

**Why this is the >90%-adoption argument, not just a simplification**:
this is the actual mechanism by which OpenTelemetry itself became a
default rather than one tracing library among many — it didn't ask every
library to bespoke-integrate; auto-instrumentation got written once per
popular library by the ecosystem, and every downstream consumer inherited
it for free. Building a proprietary Skill first would have meant asking
adopters to learn *our* integration instead of using the one they may
already have. Custom gap-fill code (Milestone 2.2) is reserved for a
runtime with no existing OTel path at all, and even then should be
contributed upstream to the relevant open project rather than kept as our
own plugin — same reasoning as building on ERC-8004/8183 instead of a
parallel proprietary registry (`docs/IDEA.md` §4).

**Revisit if**: an audit (§8 of the architecture doc) finds a
high-value agent stack with genuinely no OTel path — that's the trigger
to write gap-fill code, not a general framework-adapter roadmap decided
in advance.

## ADR-007: Content is redactable per field, and a record is still valid without it

**Decision**: `operations.content_ref` is nullable. A builder can emit a
fully valid, verifiable record (hashes, version binding, epoch membership,
Merkle proof) while withholding the actual prompt/response content
entirely.

**Why**: this is the direct fix for the privacy objection raised earlier
in the project (`docs/IDEA.md` §4-5) — a builder shouldn't have to trust
us with sensitive content just to get a tamper-evident record of *that
something happened*. Provenance (did an operation of this shape occur, at
this version, with this input/output hash) doesn't require content
disclosure; only a later dispute would need it, and only from the builder
who chooses to submit it.

**Revisit if**: Phase 3's quality-tier checks (Tier 2/3) turn out to need
content by default rather than only on dispute — would mean loosening this
default, not the schema.

## ADR-008: Batch by count OR time, whichever comes first

**Decision**: an epoch seals at 100 operations or 15 minutes, whichever
happens first.

**Why**: bounds both the cost-per-anchor (count ceiling) and the
tamper-exposure window described in the architecture doc's threat-model
note (time ceiling) — a low-traffic agent shouldn't wait hours for its
first anchor just because it hasn't hit 100 operations yet.

**Revisit if**: real dogfooding traffic shows either threshold is
obviously wrong in either direction — these are starting guesses, not
derived from data yet, and should be tuned once Milestone 2.0 has run for
a while.

## ADR-009: `version_id` is a hash of code + prompt + model, not a manually assigned label

**Decision**: `version_id = hash(code_ref, prompt_hash, model_id)`,
computed automatically, never hand-assigned.

**Why**: a manually maintained version label drifts from reality (someone
forgets to bump it). A content-derived hash can't drift — the same code,
prompt, and model always resolve to the same id, and any change to any of
the three produces a new one automatically, which is exactly the property
an audit trail needs.

**Revisit if**: a need emerges for human-readable version names alongside
the hash (likely, eventually, for usability) — add a label as metadata
pointing at the hash, don't replace the hash as primary key.
