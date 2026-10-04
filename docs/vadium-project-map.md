# The Vadium project: how the three repos fit together

This is the single place this relationship is explained. `CLAUDE.md` in
each of the three repos below points here with a short paragraph instead
of repeating this content — if you're updating how the repos relate,
update only this file.

**Read this fully before assuming any one repo is "the whole project."**
It isn't — Vadium (a sub-brand of Atesta) is built across three repos on
purpose, because the three pieces have genuinely different lifecycles,
not because the work fragmented accidentally.

## The three repos

| Repo | Absolute path | What it is | Status |
|---|---|---|---|
| **arc** (Arc Treasury Guardian) | `/Users/swathiselvaraju/code/arc` | The architectural home base — the full four-phase roadmap (spend monitoring → evidence ledger → trust/verification/dispute-arbitration → beyond), designed in depth via `docs/phase3-design-decisions.md`'s 16+ ADRs | Phase 1 shipped (`scripts/poll_spend.py`); Phase 2 designed; Phase 3 designed but **gated on real legal review** (ADR-001, ADR-013) before it's safe to build |
| **vadium-lookup** | `/Users/swathiselvaraju/code/vadium-lookup` | A live, shipped MVP: free ERC-8004 trust-record lookup (raw + Sybil-adjusted) as an MCP/HTTP service, listed in the ChatGPT Apps directory | Live at `vadium-lookup.atesta.io`; submitted to OpenAI's Apps directory |
| **vadium-attest** | `/Users/swathiselvaraju/code/vadium-attest` | A research program: state-verified capability/fulfillment testing for third-party MCP tools, to generate trust signal for ChatGPT-ecosystem sellers without relying on self-reporting | Methodology frozen, harness built, 4 apps speced; no live test-account run yet |

## How they actually relate — not three unrelated efforts

**arc holds the long-term vision; the other two are a real-world
validation loop running in parallel with it, not instead of it.**

Phase 3 (arc) is the ambitious version: on-chain identity, a committee
dispute mechanism, bond economics — correctly slow, because real money and
arbitration are at stake and it's waiting on legal review it hasn't had
yet. Rather than wait for that full machinery, `vadium-lookup` shipped the
simplest real slice of Phase 3's "reputation lookup" idea now: ERC-8004's
*existing* on-chain reputation, cleaned up (Sybil-adjusted) and
distributed through ChatGPT's app ecosystem instead of Circle's narrower
Agent Marketplace — a different chain (Base, not Arc) and a different
distribution channel than arc's master plan, deliberately, to get real
usage data sooner.

That wedge did what a real pilot should: it hit a wall in contact with
reality. ChatGPT users evaluate ChatGPT apps (Notion, Linear, etc.), not
crypto agents — "a good MVP, useless for chatgpt users" was the pilot
working, not failing. Worse, the fix couldn't be "ask integrators to
self-report outcomes" (`vadium-lookup`'s `report_outcome` tool) — there's
no natural incentive for anyone to bother, and ChatGPT never auto-records
anything. See `vadium-lookup/docs/chatgpt-apps-warm-start.md` for the full
problem statement.

**vadium-attest exists to generate that missing signal directly, by
testing tools rather than waiting for anyone to report on them** — and
critically, this isn't a new idea invented to patch the gap. It's
**arc's own ADR-009** (`docs/phase3-design-decisions.md`) — the evergreen
calibration track, originally designed to let a new *arbiter* build trust
before real dispute volume exists — independently re-derived and actually
built for a different subject (sellers' tools, not arbiters). That the
same pattern transferred cleanly is real evidence ADR-009's underlying
idea is general, discovered through shipping something rather than more
design work. See ADR-009's "Field validation" note for the technical
detail.

## Reading order if you're starting fresh in one of these repos

- **Landed in `arc`?** Read this file, then `docs/IDEA.md`, then whichever
  phase's docs are relevant to what you're doing. If you're touching
  Phase 3, read `docs/phase3-design-decisions.md` in full before
  changing anything — don't assume the CLAUDE.md summary is complete.
- **Landed in `vadium-lookup`?** Read its own `CLAUDE.md` first (repo
  mechanics), then this file for context on why `docs/chatgpt-apps-
  warm-start.md` points at a different repo instead of solving its own
  problem in place.
- **Landed in `vadium-attest`?** Read its own `README.md` and
  `docs/methodology.md` first, then this file for why it's a separate
  repo and how it connects back to `arc`'s ADR-009.

## Cross-repo file access

These are siblings under the same parent directory, not isolated
projects. A Claude Code session working in any one of these repos should
read files in the other two by absolute path whenever cross-referencing
is useful (a doc pointing at `vadium-attest/docs/methodology.md` from
inside `arc`, say) — don't treat the current repo as a sandbox boundary.
The paths in the table above are stable; use them directly rather than
re-deriving them.

## Keeping this map from going stale

Update this file, not each repo's `CLAUDE.md`, when: a repo's status
changes meaningfully (e.g. vadium-attest's first live run completes), a
new repo joins the project, or the relationship between repos changes.
Each `CLAUDE.md`'s pointer paragraph is deliberately short and about as
stable as the repo's own name and path — it shouldn't need editing when
this file's content changes underneath it.
