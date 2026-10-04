# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Arc Treasury Guardian — an early-stage tool for monitoring spend and
enforcing trust on top of Circle's Agent Stack (Agent Wallets, Circle CLI,
Agent Nanopayments/x402, Agent Marketplace) on the Arc mainnet. The full
business rationale, market research, and phased architecture live in
`docs/IDEA.md` — read that first for context before making product
decisions.

MVP scope right now is spend analytics/alerting only (no escrow/verification
module yet — that's phase 2, see `docs/IDEA.md`).

## Part of the Vadium project — two sibling repos exist

This repo is one of three. **Read `docs/vadium-project-map.md` before
assuming this repo is the whole picture** — it explains how arc's Phase 3
design relates to two shipped/in-progress sibling projects, so changes
here don't silently duplicate or contradict work already done there.

- `/Users/swathiselvaraju/code/vadium-lookup` — live ERC-8004 trust-lookup
  MVP, listed in the ChatGPT Apps directory.
- `/Users/swathiselvaraju/code/vadium-attest` — capability/fulfillment
  testing research program for ChatGPT-ecosystem tools.

These are siblings, not isolated projects — read files there by absolute
path whenever cross-referencing helps, same as any file in this repo.

## Environment

- Python 3.14, managed with `uv` (`.venv` already created via `uv venv`).
  Use `uv add <package>` / `uv pip install` rather than raw pip so the venv
  stays in sync.
- No third-party Python dependencies yet — `scripts/poll_spend.py` uses only
  the standard library (`subprocess`, `sqlite3`, `json`).
- The **Circle CLI** (`@circle-fin/cli`, Node.js v20.18.2+) is an external
  dependency, not part of this repo. Install with
  `npm install -g @circle-fin/cli`, then authenticate with
  `circle wallet login <email>` before running anything here — the scripts
  shell out to `circle` and expect an authenticated session.

## Running the spend monitor

```bash
.venv/bin/python scripts/poll_spend.py --address <agent-wallet-address> --chain ARC --db spend.db
```

This polls `circle transaction list` and `circle wallet limit budget`,
stores results in a local SQLite file, evaluates alert rules, and prints a
digest. Safe to re-run repeatedly (transaction inserts are idempotent on
`tx_id`); intended to be run on a schedule (cron/launchd) rather than kept
running as a daemon.

A live testnet wallet already exists for local testing — see
`docs/SETUP.md` for the address, login state, and CLI quirks discovered
while integrating (response envelope shape, field names, and the fact that
spending-policy budgets are mainnet-only). Check that doc before
re-deriving any of this from scratch.

## Planning docs

`docs/IDEA.md` is the source of truth for the overall four-phase roadmap
(Phase 1 is this spend monitor; Phases 2-4 are designed, not built yet).
Phase 2 (the evidence/instrumentation layer that Phase 3's verification
work depends on) has its own planning set — read these before writing any
Phase 2 code:
- `docs/phase2-architecture.md` — components, data model, key flows
- `docs/phase2-design-decisions.md` — numbered ADRs with rationale; check
  before re-litigating a decision already made (e.g. "why SQLite," "why
  batch instead of storing on-chain")
- `docs/phase2-backlog.md` — user stories with acceptance criteria,
  staged as milestones 2.0 (local dogfood) → 2.1 (external ingest) → 2.2
  (framework adapters)

Phase 3 (trust & verification — identity, disputes, committee
arbitration, bond economics) has the same three-doc set, gated on
Phase 2's ledger for its Tier 0 evidence. This is a large, actively-grown
design (14 ADRs as of this writing) — read the design-decisions doc
fully before touching any of it, don't assume the summary below is
complete:
- `docs/phase3-architecture.md` — components, data model, key flows;
  fetch the current ERC-8004/8183 text fresh before implementing anything
  here, don't trust this doc's snapshot (both are Draft status and the
  cluster moves — see the doc's own header note)
- `docs/phase3-design-decisions.md` — ADR-001 through ADR-014. Roughly:
  ADR-001 splits bond payouts into an objective (automatic) path and a
  discretionary (committee-only) one, so no single party — us included —
  can ever trigger a discretionary payout alone; ADR-002 builds on
  ERC-8004/8183 rather than a parallel identity/escrow system; ADR-006
  through ADR-010 design who's eligible to arbitrate and why; ADR-008
  covers collusion detection at increasing sophistication (pairwise,
  single-juror, and graph-cluster level); ADR-009 is the evergreen
  calibration track that lets a new arbiter build trust without waiting
  for real dispute volume; ADR-011/012 cover how a committee actually
  gets assembled (advertised, opt-in, random-draw-from-volunteers) and
  what happens when too few volunteer; **ADR-013 is the one to read most
  carefully** — it fixes three real gaps found by direct challenge (we
  hold no custody on either side; payouts are structurally incapable of
  rewarding a self-dealing buyer-seller pair; a seller must have
  collateral already locked before a buyer can buy coverage on them,
  the fix for "what backs this if the seller's wallet is empty"); ADR-014
  gives the actual premium/slash pricing formulas.
- `docs/phase3-backlog.md` — resequenced 2026-09-20 after an end-to-end
  pass found Epic G was written as if it only gated Epic D, when Epic
  C's automatic slashing depends on it equally. Epic G now sits right
  after Epic A, split by milestone: **G1–G4 (locked collateral, the
  anti-fraud payout cap) are Milestone 3.0** — required for Epic C's
  slashing to be real, not a stub — **G5–G7 (the buyer-purchased premium
  product, actuarial pricing) are Milestone 3.1**, needed for Epic D's
  discretionary payouts to have real buyer-paid coverage behind them.
  Milestones: 3.0 (registration, seller collateral core, reputation
  lookup, objective disputes) → 3.1 (committee mechanism/Epic D, hedge
  premium pricing) → 3.2 (TEE provider integration, repeat-offender and
  rare-escalation refinements).

Real legal counsel review of ADR-001 **and, specifically, ADR-013's
concrete implementation** is still outstanding as of this writing —
`docs/IDEA.md` §8-9 calls for it bundled directly into design-partner
outreach, not as a separate later step. Treat both as design hypotheses,
not settled law, until that review happens — this is the single
highest-leverage open item in Phase 3, more consequential than any
remaining engineering work.

## Plain-English companion and outreach

- `docs/plain-english-primer.md` — a no-jargon narrative walkthrough of
  the evidence ledger, the jury/dispute mechanism, and the bond
  economics, with real-world analogies (Merkle batching as a notary
  stamp, the jury as a court, bond slashing as PoS staking/insurance
  fraud). Point a non-technical reader here before the ADRs.
- `docs/design-partner-outreach.md` — drafted (not sent) outreach to
  three real Arc-ecosystem candidates (Virtuals Protocol, Kite AI,
  BlockRun) with per-candidate approach notes. Review before sending —
  these are real companies and real public contact channels.

## Branding and web presence

The product is **Vadium**, a sub-brand of **Atesta** (the parent
company/domain). Naming rationale, palette, type system, and logo assets
live in the published Vadium Design System artifact — see the pitch deck
and `docs/phase3-design-decisions.md`'s implementation notes for context
if that link is lost. `docs/website-redesign.md` has the (not yet
executed) plan for restructuring atesta.io: move the existing Supply
Chain Risk Intelligence product to `/supply-chain`, make the homepage
the Atesta parent-brand page leading with Vadium. Source is on GitHub,
not this repo — read that doc before touching the site so the redirect/
sitemap requirements aren't rediscovered from scratch.

Syntax-check after edits with:

```bash
.venv/bin/python -m py_compile scripts/poll_spend.py
```

There is no test suite yet.

## Architecture

`scripts/poll_spend.py` is a single-file pipeline with four stages, run in
sequence each invocation:

1. **`run_circle()`** — thin subprocess wrapper that always passes
   `--output json` to the Circle CLI and parses the result. All Circle CLI
   interaction goes through this one function.
2. **`ingest_transactions()` / `ingest_budget()`** — write CLI output into
   two SQLite tables (`transactions`, `budget_snapshots`). These are pure
   append/upsert steps with no business logic.
3. **`compute_alerts()`** — the actual analytics: compares today's outbound
   spend against a 7-day rolling average, flags first-seen high-value
   counterparties, and flags low remaining daily budget. Alert thresholds
   (`SPIKE_MULTIPLIER`, `NEW_COUNTERPARTY_ALERT_AMOUNT`,
   `BUDGET_LOW_FRACTION`) are module-level constants — tune these in place
   rather than adding a config system until there's a real reason to.
4. **`print_digest()`** — reads back from the `alerts` table for display.

When extending alert logic, add new rules inside `compute_alerts()` writing
to the existing `alerts` table rather than introducing new alert-storage
mechanisms — the table's `(alert_type, severity, detail)` shape is meant to
cover new rule types without a schema change.

The phase-2 escrow/verification module described in `docs/IDEA.md` does not
exist in code yet; when it's built, keep it as a separate module rather than
folding it into `poll_spend.py`, since it has a different trigger model
(per-payment, synchronous) than the polling/batch model here.
