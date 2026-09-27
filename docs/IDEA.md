# Arc Treasury Guardian — idea doc

Date range: 2026-09-17 → 2026-09-18 (research), restructured 2026-09-18
after a fact-check pass against primary sources.
Status: Phase 1 shipped and running on testnet. Phases 2–4 are design,
not yet built.

This doc replaces earlier incremental versions. Everything below has been
checked against primary sources where one exists (official specs, EIP
text, regulation text, GitHub issues fetched directly) rather than
blended AI search summaries — see §10 for what changed in this pass and
why that distinction mattered in practice.

## 1. Thesis

Circle's Arc mainnet (launched 2026-09-16, EVM-compatible, USDC-native
gas) shipped alongside Circle Agent Stack — Agent Wallets, Circle CLI,
Nanopayments (x402 + Gateway batching), and an Agent Marketplace. Agents
can now pay each other autonomously at machine speed. Nobody has shipped
the governance layer for what happens after the money moves: whether
spend is sane, and whether a paid-for output was actually delivered
honestly. That's the target.

## 2. Market context

- Arc mainnet launched 2026-09-16 with BlackRock, DTCC, and Visa producing
  blocks.
- x402 had processed roughly **165M agent transactions across ~69K active
  agents by April 2026**, confirmed across independent sources — spread
  across the whole x402 ecosystem (Coinbase's Agent.market, Stripe's
  Machine Payments, Circle Wallets, Cloudflare's Agents SDK), not
  Circle-specific.
- Circle's Agent Marketplace lists on the order of 1,000+ services across
  six categories (SOCIAL_INTELLIGENCE, FINANCIAL_ANALYSIS,
  WEB_SEARCH_RESEARCH, PREDICTION_MARKETS, CREATIVE, INFRASTRUCTURE) —
  sourced from Circle's own blog, not independently re-verified; treat the
  exact count as approximate.
- Circle's own production checklist names the gap directly: *"Observability:
  build payment analytics dashboards, per-agent cost tracking, settlement
  monitoring, and balance depletion alerts so you catch issues before they
  become problems."* That's homework handed to developers, not a shipped
  feature.

### 2.1 Competitive landscape (checked 2026-09-20)

Every vertically-integrated agent-commerce platform checked so far has
independently built (or bought) its own trust/dispute layer, not left it
open:

- **Kite AI** — its own L1, identity/payments, "Agent SLAs" with slashing,
  a Proof-of-AI evidence log, and an arbitration layer that "checks the
  audit trail, applies the rules, and enforces the outcome on-chain"
  (with CI-MAC/Cayman arbitration as a legal fallback). Whitepaper-stage
  language for most of this, same maturity as our own Phase 3 — but the
  intent to own this layer is explicit, not a gap.
- **NEAR AI Agent Market** (launched Feb 2026) — escrow-held payments, an
  "agentic dispute system" where a dispute agent evaluates both sides,
  neutral arbitration, and SHA-256 evidence hashing for disputed
  deliverables. Live, not just roadmap language.
- **ASI Alliance / Agentverse** (Fetch.ai + SingularityNET + Ocean
  Protocol) — embedding DIDs, verifiable credentials, and Trust
  Registries into Agentverse (via a third-party vendor, cheqd, for the
  identity/credential piece), with tiered reputation scoring that
  already factors in dispute rates.

**Reading**: this isn't three unlucky coincidences — it's the default
move for any platform building the full stack (identity + payments +
marketplace). Trust/dispute resolution is table stakes they build
in-house, once they exist at that scale. The implication for
positioning: **don't pitch "the trust layer for platform X" to a
platform that already has one** — the open, defensible gap is
*portability*. Kite's reputation only works inside Kite; NEAR's only
inside NEAR's Agent Market; Agentverse's only inside Agentverse. An
agent that transacts across more than one starts over each time. An
open-standards (ERC-8004), chain-agnostic layer is structurally suited
to that gap in a way a vertically-integrated platform isn't — see §6.4.

**Checked and confirmed as the other profile — an aggregator/payment
rail with no trust layer of its own, i.e. genuinely complementary**:
BlockRun (Arc-native via `arc.blockrun.ai`, confirmed chain id 5042,
USDC gas — no reputation/escrow/dispute/arbitration found anywhere in
its docs) and Nevermined (payment-routing/metering layer, a real named
x402 Facilitator product, no dispute mechanism found — though Arc-
specific deployment isn't confirmed from public docs, and its ERC-8004
support claim, made on its own blog rather than its homepage, needs
direct verification before citing it). Payman was checked and
deprioritized — it targets banks/credit unions, a different vertical
from agent-to-agent commerce marketplaces, despite also having no
dispute layer of its own.

**Checked and dropped — wrong settlement rail entirely, not a
competitor**: Skyfire (verified 2026-09-20). Its KYA/KYAPay identity
stack settles through traditional card-network rails, not x402 — a live
launch partner on Visa's Trusted Agent Protocol (Oct 2025) and a live
purchase demo with Visa Intelligent Commerce (Dec 2025); Mastercard's
Agent Pay ties identity into the network token directly. No
dispute/escrow of its own either, so it isn't competing — there's just
no x402 transaction stream for an evidence ledger to observe. Notable
on its own terms: Visa and Mastercard are running a parallel, non-crypto
track on the same underlying problem (agent identity for payments) —
real validation that the problem is industry-wide, on a rail that
doesn't intersect with x402/ERC-8004 at all.

## 3. Idea evaluation → chosen direction

Five ideas were scored against real market need before picking a
direction:

| Idea | Need | Arc alone or integration? | Revenue model |
|---|---|---|---|
| Spend FinOps ("nanopayment janitor") | Agent spend is invisible at machine speed | Alone — built on data Circle CLI already emits | Flat SaaS fee or % of spend reduction |
| Escrow & SLA insurance | No arbiter when autonomous agents disagree on delivery | Integration | % fee held back per escrowed payment |
| Vertical micro-data APIs | Generic search is saturated; painful-to-parse public data isn't | Alone | Per-call nanopayment via marketplace listing |
| Creator royalty collection | No protection when content is reused by other agents | Integration | Rev-share on collected royalties |
| AML screening for small merchants | Enterprise compliance tooling is priced out of reach | Integration | Subscription + per-tx fee |

**Chosen: combine the first two** into "Treasury Ops for Agent Wallets" —
*we make sure your agents' money is being spent correctly, and that when
they pay someone, they actually get what they paid for.*

## 4. Standards landscape — what's already solved, what's genuinely open

This is the part that most needed a fact-check pass, because it's easy to
either duplicate something that already has a standard or build on a
standard that has known flaws. Verified against eips.ethereum.org,
docs.x402.org/GitHub, and the EIPs' own review threads directly.

**Already solved — build on these, don't rebuild:**

- **ERC-8004 "Trustless Agents"** (Draft, De Rossi/Crapis/Ellis/Reppel,
  2025-08-13) — `IdentityRegistry`, `ReputationRegistry`,
  `ValidationRegistry`. Real signatures (confirmed against the EIP text,
  which differ from Arc's own tutorial paraphrase — use these, not Arc's
  simplified version): `register(agentURI, MetadataEntry[])` for identity;
  `giveFeedback(agentId, int128 value, uint8 valueDecimals, tag1, tag2,
  endpoint, feedbackURI, feedbackHash)` for reputation — richer than a flat
  score, carries typed tags and a hash-linked evidence URI already.
- **ERC-8126 "AI Agent Verification"** (**Final status** — already
  standardized, not draft) — composable with 8004, posts attestations to
  its `ValidationRegistry`. Covers technical/security legitimacy: token,
  media, code, web-app, and wallet checks plus a risk score. Explicitly
  scoped away from behavior: *"does not guarantee the agent's future
  behavior or intentions."* This is exactly the boundary we need —
  8126 owns "is this agent technically legitimate," leaving "was this
  specific output actually good" untouched.
- **ERC-8183 "Agentic Commerce"** (Draft, Crapis/Lim/Weixiong/Zuhwa,
  2026-02-25) — Job contract: client escrows via `fund()`, provider
  submits a deliverable hash via `submit()`, and the evaluator settles.
  Correction to earlier research: the evaluator **does** have a
  `reject(jobId, reason)` function — Arc's own tutorial description of "no
  rejection function" was inaccurate. The real gap is narrower than first
  thought but still real: nothing in the standard independently checks
  whether the *evaluator's own judgment* was fair or correct. Accept or
  reject is still a single off-chain call with no verification behind it.

**Close but incomplete — a live, evolving cluster, worth tracking:**

- **ERC-8275** (renumbered from a proposed 8267), "Agent Service Discovery
  and Escrow Payments" — open PR, unmerged. Three-layer
  Registry/Escrow/Reputation design with passive, decaying reputation
  derived from escrow events. **A concrete anti-pattern was caught and
  fixed during its own review**: naive attestation-counting is
  Sybil-vulnerable — a small number of colluding attesters can fake
  diverse-looking feedback. The adopted fix, written into the spec as
  normative: **inverse-Simpson diversity weighting**, not a simple count.
  Direct design requirement for us: whatever reputation aggregation we
  build (on top of ERC-8004 feedback or our own bond registry) must weight
  for attester/reporter diversity from day one, not bolt it on later.
- Also named in this same author cluster, not yet reviewed in depth:
  ERC-8240 (trust infrastructure), ERC-8257 (Agent Tool Registry), ERC-8300
  (attestation-gated actions), and ERC-8263/8274/8281/8299 (dependencies of
  8275). Worth a second pass before Phase 3 implementation starts, since
  this cluster is moving.

**Genuinely open — this is the actual target:**

Across this entire ERC family, nobody standardizes *subjective output
quality* verification or *independent adjudication of the evaluator's own
judgment*. ERC-8126 explicitly disclaims behavior guarantees. ERC-8183's
evaluator can reject, but nothing checks whether that evaluator was
right. ERC-8275's reputation is passive and escrow-event-derived, not a
quality signal. This confirms — now checked broadly, not just against
8004/8183 in isolation — that the gap Phase 3 targets is real and
unclaimed.

**x402 protocol** (confirmed via direct fetch of docs.x402.org and the
GitHub issues themselves): stateless by design, payment settles instantly
and finally in one request-response cycle, no native escrow/dispute/refund
today. A non-custodial `"escrow"` scheme is proposed in
[x402-foundation/x402#2222](https://github.com/x402-foundation/x402/issues/2222)
(draft v0.1, reference implementation weeks out, unmerged). A dispute-
evidence gap is named directly in
[x402-foundation/x402#3500](https://github.com/x402-foundation/x402/issues/3500)
(opened 2026-09-16, zero assignees/PRs/comments as of last check) — draft
engagement comment at `docs/x402-issue-3500-comment.md`, not posted yet.

## 5. Roadmap

**Phase 1 — Spend Guardian (shipped, running on testnet).** Polls
`circle transaction list` / `circle wallet limit budget`, flags spend
spikes, first-seen high-value counterparties, and low budget. See
`scripts/poll_spend.py` and `docs/SETUP.md` for the live testnet wallet
and validated end-to-end run.

**Phase 2 — Evidence & instrumentation layer** (prerequisite to Phase 3:
its Tier 0 checks assume sellers *can* produce this evidence, and most
can't yet because nothing standard tells them how).

- Don't build a new observability SDK. Most agent stacks already emit
  OpenTelemetry GenAI-conformant traces (Langfuse, Traceloop, native OTel).
  Verified against the OTel spec directly: current maturity is
  "Development" (not yet stable), span names include `create_agent`,
  `invoke_agent`, `execute_tool`; `gen_ai.input.messages`/
  `gen_ai.output.messages` may be recorded as span *attributes* (JSON
  string) or as span *events* (structured) — both are valid per spec, not
  an either/or (an earlier pass here incorrectly framed events as the only
  correct option).
- Build a ledger backend that ingests existing OTel exporters and adds
  what's missing: version-attestation binding (which code/prompt version
  produced this operation), hash-chaining for tamper evidence, and a
  compliance-shaped retention profile (see EU AI Act note below).
- Ship a Claude Code Skill as the first, easiest adapter (wired to
  `PreToolUse`/`PostToolUse` hooks, zero code for the builder) — also how
  we dogfood on our own oracle/registry agent — then thin per-framework
  adapters (LangChain, CrewAI, OpenAI Agents SDK, Google ADK) using each
  framework's existing callback extension points.
- **Anchor, don't store, on Arc.** Batch off-chain log entries into a
  Merkle tree; commit only the 32-byte root plus a back-pointer to the
  prior root on Arc periodically. Confirmed cost pattern from recent
  research (Agent Flight Recorder, "A Black Box for Agentic Processes,"
  both arXiv 2026-09): roughly $2.30 per 100,000 events at 100-event
  epochs on an L2 — fractions of a cent per record. Anchoring on Arc
  specifically (not an unrelated chain — people are already anchoring
  agent-output proofs on NEAR) keeps a seller's bond, ERC-8004 identity,
  and audit-log anchor on one chain.
- **Regulatory driver, corrected**: the EU AI Act's Article 12
  (Record-Keeping) requires automatic event logging over a high-risk
  system's lifetime — confirmed against the primary text at
  artificialintelligenceact.eu/article/12/. Two things from the original
  research were wrong and are corrected here: there is **no specific
  retention-period figure in the primary text** (an earlier "6 months"
  claim doesn't hold up — drop it), and — materially — **Chapter III's
  high-risk obligations, Article 12 included, were deferred** by the
  "Digital Omnibus" regulation (in force 2026-07-27): Annex III systems to
  **2027-12-02**, Annex I systems to **2028-08-02**. Article 12 is *not yet
  in force* for high-risk systems as of this writing. The "regulatory
  deadline already passed" framing used earlier was wrong and is retracted
  — there's still a real, dated opportunity (a known future deadline with
  no finalized technical standard: prEN 18229-1 and ISO/IEC DIS 24970 are
  still drafts, not independently re-verified this pass), just not the
  urgency originally claimed.
- Open-core distribution: give the adapters away free, monetize the hosted
  ledger/compliance backend, contribute upstream to OTel's GenAI working
  group. The strongest adoption lever is tying instrumentation to Phase 3
  economics directly (see below), not the regulatory case alone.

**Phase 3 — Trust & verification layer**, built on the standards above
rather than a parallel proprietary system.

- Register agents (ours and verified sellers) in ERC-8004's
  `IdentityRegistry`; act as an ERC-8004 `validator` submitting
  `giveFeedback()` using the real, richer signature (typed tags,
  hash-linked evidence URI) — this is exactly the off-chain evidence
  Phase 2 produces.
- Reference ERC-8126 for technical/security legitimacy rather than
  re-checking it ourselves — it's Final, adopted, and out of scope for us
  to duplicate.
- Act as the **evaluator** on ERC-8183 jobs — correcting the earlier plan:
  the evaluator can already `reject()`, so the missing piece isn't "add a
  rejection path," it's "make the evaluator's own judgment independently
  verifiable," which is where the tiered verification mesh below applies.
- **Bake in the ERC-8275 lesson from day one**: any reputation aggregation
  we build must weight for attester/reporter diversity (inverse-Simpson or
  equivalent), not count attestations naively — this is a known,
  previously-exploited Sybil vector in the same design space, caught
  during that EIP's own review.
- **Split provenance from quality** (per RAILS, arXiv:2606.08790: *"Payment
  is not clearing. Authorization is not clearing. LLM-as-judge evaluation
  is not clearing."*):
  - Provenance (did they do the work) — TEE-attested inference where
    available (Nvidia Confidential Computing, AWS Nitro, Phala, Marlin,
    Atoma all shipping in some form as of 2026); optimistic bonded
    assertion as fallback.
  - Quality (was it good) — genuinely subjective for creative/research
    work, never fully automatable. UMA's own AI-judge experiment,
    confirmed directly against blog.uma.xyz: their bot runs **78%
    real-time accuracy** against **98.2% of human-reviewed assertions
    going undisputed** — worth being precise that these are two different
    metrics (undisputed rate vs. accuracy), not a strict apples-to-apples
    comparison, but the honest nuance actually strengthens the point: the
    bot hits 95% on clear yes/no cases and 99.3% on sports/pricing, and
    only 0.4% of *all* proposals face genuine factual disputes in the
    first place. A single LLM judge is not yet reliable enough to be the
    sole arbiter, especially on the harder, less-clear-cut cases that
    matter most for a dispute.
- Tiered verification mesh (evidence-graded, gated by an admissibility
  floor — cheap evidence clears a nanopayment, expensive evidence required
  before a large payout is protected):

  | Tier | Check | Cost | Applies to |
  |---|---|---|---|
  | 0 — Structural | Schema conformance, TEE attestation if present, Phase 2 longitudinal-record evidence if present | ~free | Every transaction |
  | 1 — Heuristic | Duplicate-output hash, citation-resolves check | cheap | Every transaction / high sample |
  | 2 — LLM judge (advisory only) | Rubric score vs. request, logged as one input | moderate | Sampled, flagged, or high value |
  | 3 — Committee | Advertised, opt-in juror pool; random draw from volunteers; longitudinal collusion/favoritism detection, not a static multi-model vote | expensive | Disputed or repeat-flagged sellers |

- A standing bond/insurance pool complements, rather than replaces,
  ERC-8183's per-job escrow: per-job escrow protects one buyer on one job;
  a standing pool catches a chronically-bad seller across many jobs and
  buyers, keyed off the same ERC-8004 identity/reputation the evaluator
  role already reads. Full design in `docs/phase3-design-decisions.md`,
  ADR-006 through ADR-014 — summarized here since the detail lives there,
  not duplicated:
  - **Committee formation and quality** (ADR-006–010): eligibility
    combines real tenure, genuine economic activity (not gameable topic
    counts), and an evergreen calibration exam scored with a proper
    scoring rule — so a brand-new agent isn't locked out of ever
    building trust. Eligibility is pool-relative and scales with the
    dispute's value, so credentials built cheaply during quiet periods
    don't automatically clear a high-stakes bar later. A juror with a
    direct relationship to either disputing party is excluded in
    real time; subtler favoritism is caught statistically over time.
  - **Collusion resistance** (ADR-008, ADR-011): jurors are advertised a
    dispute and volunteer, rather than being blind-drafted — solving a
    real opportunity-cost problem — but the committee is still a random
    draw *from* volunteers, and co-participation frequency plus
    above-baseline agreement (individually, and at a graph/cluster
    level) catches coordination that credentials alone can't.
  - **Volunteer shortfalls** (ADR-012): a four-tier escalation ladder
    (raise the fee, broaden eligibility, draw from a small standing
    reserve, or — only for low-value disputes — a smaller committee
    under a stricter threshold) — cheapest and least standard-lowering
    tried first, never skipped ahead.
  - **The money itself** (ADR-013–014): we hold no custody on either
    side — a buyer's job payment lives in the ERC-8183 job contract, and
    `BondPool` releases funds by code, not by our own decision. A
    buyer's hedge premium is never refunded and a payout never exceeds
    what that buyer actually paid, which makes a self-dealing
    buyer-seller collusion attempt a guaranteed loss even when executed
    perfectly. A seller must have real collateral already locked before
    a buyer can buy coverage on them at all — the direct fix for
    "what backs this if the seller's wallet is empty." Premiums and
    slash amounts are priced with a real actuarial-style formula
    (expected loss plus margin; penalty scaled by confidence in the
    verdict), reusing the same risk signals built for eligibility rather
    than inventing new inputs.
- Migrate bond custody onto x402's native `"escrow"` scheme once it
  stabilizes (§4), shrinking our own custody surface.

**Phase 4 — Distribution & defensibility.**

- **Automatic hiring is native to x402** — any standard x402 client can
  discover, inspect, pay, and receive a response from our listing with no
  human involved, provided we're schema-compliant.
- **Self-advertising, two surfaces**: Circle's Agent Marketplace is
  manual-review-only today (a Google Form; self-serve "coming," not
  shipped) — one human step, then automatic discovery/payment forever
  after. The x402 Bazaar discovery layer (facilitator-run, e.g. Coinbase's
  CDP) is genuinely automatic — add an `extensions.bazaar` block to the
  route's x402 config, no manifest file, no approval, though the
  facilitator does validate the schema before cataloging. Do both.
- **Onboarding requirements** — sellers: a schema-compliant x402 endpoint,
  the Bazaar extension block, registration + a bond sized to volume, and
  (optional, reduces required bond) a TEE attestation or Phase 2 adapter
  running. Buyers: an Agent Wallet holding USDC (already required to use
  Arc/x402 at all), a paid lookup call or standing subscription, and —
  to file a claim — the seller's signed receipt kept and forwarded at
  dispute time.
- **Defensibility** — the mechanism itself isn't hard to copy; the moat has
  to be earned, not built:
  1. Ship a working reference implementation against x402#3500 before
     anyone else touches it — zero assignees as of last check.
  2. Same play at the ERC layer: be an early, credible `validator` on
     ERC-8004 and `evaluator` on ERC-8183, riding standards Arc already
     drives adoption of rather than building distribution from scratch —
     confirmed via the broader ERC sweep in §4 that nobody has claimed the
     quality/adjudication gap yet.
  3. Reputation data compounds; a copycat starts at zero — same moat shape
     as a credit bureau, not a technical secret.
  4. Integration lock-in via `circle wallet limit set` blocklist feed —
     switching means re-plumbing a buyer's own wallet policy.
  5. Underwriting discipline on bond pricing improves with real
     dispute-rate data over time.
  6. Go deep in one marketplace category first rather than thin coverage
     across all six.

## 6. Business model: value, distribution, defensibility

### 6.1 Value add — why buyers and sellers actually pay

**Sellers**: a verified/bonded badge that wins buyers away from
unverified competitors, at near-zero marginal cost if they're already
OTel-instrumented (the Phase 2 bet). Running TEE-attested inference or
the Phase 2 evidence pipeline earns a *cheaper* bond — a direct financial
reward for adopting the free instrumentation layer, not just a compliance
nudge.

**Buyers**: an x402 payment today is final, with zero recourse if the
seller cheats. We sell the recourse two ways: a cheap pre-purchase
reputation check, and — the mechanism worked out in detail in
`docs/phase3-design-decisions.md` ADR-011–014 — an explicit, opt-in
per-transaction hedge premium a risk-aware buyer chooses to pay when
hiring a seller who hasn't yet earned enough trust to skip it. The
premium is priced like real insurance (expected loss plus a margin,
using the seller's own tenure/activity/dispute history), is never
refunded regardless of outcome, and pays out capped at exactly what the
buyer paid for that job — never more, which is also what keeps a
buyer-seller collusion attempt from ever being profitable (ADR-013 Part
B). Coverage only exists where the seller has already locked real
collateral (ADR-013 Part C) — there's no promise sold against an empty
wallet. Both sides are currently absorbing a cost (sellers can't prove
they're good; buyers can't tell who is) that a shared trust signal
removes more cheaply than either side solving it alone — the standard
argument for a credit bureau, not a novel one.

### 6.2 How agents actually choose — distribution for a machine buyer, not a human one

Human and agent purchasing behavior diverge enough that a human-facing
GTM playbook (brand, content marketing, SEO, sales relationships) mostly
doesn't apply. Checked directly rather than assumed: agent/skill
discovery already runs on **structured ranking signals** — install
count, GitHub stars, usage, registry metadata — and **semantic/vector
retrieval**, not brand. One source on the current MCP/Skills ecosystem
put the state of discovery bluntly: *"hundreds of new MCP servers pop up
on GitHub weekly... discovery is completely broken... choosing the right
one is its own job."* That's the actual environment being sold into.

Four implications:

1. **Compete on numbers a machine compares, not a story that persuades a
   human.** Price, latency, uptime, dispute rate — an agent's purchasing
   logic filters on these programmatically. A polished landing page does
   nothing a clean, complete x402 schema and a real reliability track
   record doesn't already do better.
2. **Get embedded as the default inside something already chosen, rather
   than competing to be chosen.** Once a human wires an agent to a
   framework/CLI/skill, the agent doesn't re-decide — it uses what it was
   given. The highest-leverage move isn't listing among thousands of
   marketplace competitors; it's getting referenced *inside* an
   already-popular skill (e.g., proposing that Circle's own
   `agent-wallet-policy` or `use-arc` skill recommend a check with us
   before a payment) — that changes what's already in an agent's context,
   which is the actual mechanism by which an LLM-driven agent "decides"
   to call something.
3. **Solve our own cold start the way we solve sellers' cold start.**
   Registries rank by installs/usage/stars — a new listing with zero
   traction is invisible by the same math that makes a zero-reputation
   seller unattractive. Dogfood hard and get real design-partner usage
   before broad listing; treat our own install count as a metric to seed
   deliberately, not a vanity number.
4. **Publish machine-first.** The primary artifacts are an x402 Bazaar
   manifest, an MCP server entry, a Circle Marketplace listing, an
   OpenAPI/x402 schema — structured data a discovery pipeline ingests.
   Docs and writing matter only insofar as they eventually feed a
   registry or a training corpus, not as the main channel.

### 6.3 GTM

Builds directly on §5's Phase 4 distribution mechanics (Marketplace form,
x402 Bazaar auto-catalog, standards engagement) plus §6.2's machine-first
tactics above:

- **Phase 2 (free layer)**: ride existing adoption, don't create new
  adoption. Publish open, contribute upstream to OTel's GenAI working
  group. The pitch to a builder is "add one line," not "adopt our SDK."
- **Phase 3 (paid layer)**: list on Circle's Marketplace and the x402
  Bazaar; ride Arc's own onboarding funnel by being an early, credible
  ERC-8004 validator / ERC-8183 evaluator — Arc's tutorials already point
  builders toward these standards, so the funnel already exists.
- **Credibility play**: ship the reference implementation against
  x402#3500 before anyone else touches it; engage the ERC-8004/8183/8275
  review threads directly.
- **Pilot first**: 2-3 real design partners before broad launch (§9).

### 6.4 Defensibility

Worth stating precisely, since it's a deliberate asymmetry: **there is no
defensibility in the telemetry layer, on purpose** — Phase 2 is free and
open by design (§5, ADR-006 in `docs/phase2-design-decisions.md`), the
same way OpenTelemetry itself is free. Verified concretely, not just
asserted, 2026-09-20: reviewed the actual code rather than reasoning
abstractly. `contracts/AnchorLog.sol` is plain Solidity with zero
Arc-specific dependencies; `ledger/merkle.py` and `ledger/store.py` are
pure stdlib Python with zero chain awareness. The only Arc-specific
surface is a `--chain` parameter to the Circle CLI in `ledger/anchor.py`
and `ledger/auth.py` (and the ERC-1271 logic in the latter is a general
EVM smart-wallet standard, not an Arc quirk). Circle's own Arc Studio
lists Base as one of nine chains it supports alongside Arc, with native
USDC on Base too — so this is a redeploy-and-reconfigure exercise, not a
rewrite. That's the commoditized-by-design layer proving itself
portable in practice, which is also the concrete answer to the
Kite/NEAR/ASI Alliance walled-garden problem in §2.1: they can't do
this — their trust layer is welded to their own chain; ours isn't,
because of a choice already made in ADR-002. Backlog: deploy AnchorLog
to Base once Phase 2 is fully proven on Arc, framed as a demonstration
of "no lock-in," not a defensive reaction to a competitor. The moat
lives entirely in Phase 3:

1. Shipping first against x402#3500, and operating credibly as an
   ERC-8004 validator / ERC-8183 evaluator before anyone else claims that
   role.
2. Reputation data compounding — a copycat starts at zero trust.
3. `circle wallet limit set` blocklist integration lock-in.
4. Bond-pricing/underwriting discipline improving with real dispute data.
5. Depth in one marketplace category before breadth across all six.
6. **The full trust mechanism (ADR-006 through ADR-014,
   `docs/phase3-design-decisions.md`)** — decided 2026-09-19 as the
   project's primary defensibility. Its code is necessarily auditable
   (Epic F1 requires anyone to independently verify no single party can
   trigger a discretionary payout), so the mechanism's design is
   copyable by any competitor who reads it. What isn't copyable: the
   accumulated calibration scores, tenure, collusion-clean voting
   history, and per-seller locked-collateral track record real
   participants build up going through it. A competitor launching the
   identical design starts at zero on exactly the data that makes the
   mechanism trustworthy — the more elaborate and well-used the
   mechanism, the higher the bar to catch up. This now spans committee
   formation and quality (ADR-006–012: eligibility, collusion detection,
   evergreen onboarding, volunteer-shortfall handling) and the money
   mechanics that make the whole thing sellable without becoming an
   unlicensed insurer (ADR-013–014: no custody on either side, payouts
   structurally incapable of profiting a self-dealing buyer-seller pair,
   seller collateral that must be locked before coverage can be sold
   against it, and actuarial-style premium/slash pricing reusing the
   same risk signals built for eligibility). This raises real execution
   risk in exchange (`docs/phase3-backlog.md` stages the build
   specifically to manage it — Epic G's collateral core now sits right
   after Epic A, since Epic C depends on it as much as Epic D does, a
   dependency an earlier pass through this design missed) — for a
   business whose product is "trust our judgment," shipping this wrong
   is a worse failure than shipping something simpler slowly.

None of #1-5 are the mechanism (bonds, schema checks, which are easy to
copy) — they're "being early and being right," the only moat available
when the layer underneath is intentionally commoditized. #6 is the
exception: here the mechanism is deliberately made elaborate and public,
and the moat is the track record accumulating inside it, not secrecy
about how it works.

### 6.5 Open-source vs. commercial — revisited for an agent-mediated market

Raised 2026-09-20: instead of running this purely as a closed commercial
product, release parts of it open source with instructions, to build
credibility before commercializing the rest. The classic human-software
spectrum (fully open → open-core → source-available/BSL → fully closed)
assumes two things that don't hold the same way when the adopter is an
agent rather than a human developer, so the model needs rethinking
rather than picking a point on that existing spectrum.

**Trust doesn't route through "read the source" here — it already
routes through verifiability.** A human trusts an open-source project
partly by reading it and partly through community/maintainer
reputation. An agent evaluating whether to trust a dispute-resolution
layer isn't reassured by GitHub stars; what satisfies a machine-checkable
trust requirement is exactly what this product already provides —
Merkle proofs, on-chain anchoring, a verified contract. Open-source and
cryptographic verifiability are different trust mechanisms, and this
project already leans on the stronger one. This is why §6.4 could
already conclude Phase 3 is "necessarily auditable" without that meaning
its internals need to be blogged about.

**But the *distribution* rationale for open source gets stronger, not
weaker, for agent adopters.** §6.2 already established that discovery
runs on install counts, MCP registries, and semantic retrieval, not
brand — PayCrow (docs/design-partner-outreach.md) is the live proof:
one GitHub star, no funding, no team, and still real distribution
because it shipped as an MCP server an agent (or an AI coding assistant
integrating on an agent's behalf) can find and wire in with zero human
sales cycle. For a product whose adopters increasingly do their own
integration work, open and spec-compliant *is* the distribution
channel, not a credibility nice-to-have.

**The moat implication matters more than either of those.** A human
enterprise is protected from switching by procurement friction and
organizational inertia. An agent — or whatever architects an agent's
integrations — can re-evaluate and re-route to an equally-capable
alternative with none of that friction, the moment this one is
marginally worse. Any moat resting on switching cost quietly stops
working in an agent-mediated market. What survives is only what
literally can't be forked along with the code: the accumulated
dispute-outcome and calibration track record (ADR-009), the network
effect of a reputation graph that's valuable only because *other*
marketplaces already recognize it, and whatever legal/compliance entity
stands behind custody-adjacent guarantees. A fork inherits none of that
no matter how faithfully it copies the design — which is the same
conclusion §6.4 already reached about Phase 3, extended one step
further: open-sourcing the mechanism doesn't cost the moat, because the
moat was never the mechanism.

**The split, reconciled with the standing disclosure boundary** (deck,
website, demo have all held to: no jury/committee mechanics, no
collusion-detection methods, no pricing formulas, no self-dealing fraud
vector, no insurer-classification reasoning, no competitor names).
Open-sourcing anything is a *stronger* disclosure act than any of that
external material — "release parts of it" has to be scoped against the
same boundary deliberately, not treated as a separate decision:

- **Open, and worth opening on purpose**: the evidence-ledger
  ingest/Merkle/anchoring mechanism, `contracts/AnchorLog.sol` itself
  (arguably already effectively public the moment it's deployed and
  verified on-chain — formalizing that costs nothing), ERC-8004/8183
  integration code, client SDKs for submitting evidence and reading
  trust records. This is Phase 2 — already designed to be free (§6.4's
  "no defensibility in the telemetry layer, on purpose"). Open-sourcing
  it isn't a new concession; it finishes a decision already made.
- **Stays closed, same reasoning as always**: committee-formation and
  voting mechanics, collusion-detection thresholds, payout-trigger and
  pricing formulas, self-dealing-defense logic — the standing
  non-disclosure list — plus the actual commercial surface: the hosted
  trust-registry service (the network-effect asset itself), the legal
  entity backing objective/discretionary payouts, and the calibration
  data.

**Decision**: open the plumbing, keep the judgment and the accumulated
record commercial — not as a safe midpoint on the human open-source
spectrum, but because that split is exactly where this project's real
moat already lives (track record and network effect, not secrecy) and
exactly where its real adoption channel already lives (agents
integrating open, spec-compliant infrastructure with no sales cycle).
It requires no reversal of anything decided earlier — it makes explicit
a line already implied by §6.4 and §6.2 for reasons that had nothing to
do with open source at the time.

## 7. Capital, operating cost, and revenue

All figures below are rough, labeled scenarios for planning discussion —
not a budget, not a forecast. Grounded against real comparables where
one exists (noted inline) rather than invented from scratch.

### 7.1 Capital to reach a working, audited MVP with a first design partner

Two build scenarios, since who's actually writing the code changes the
dominant cost line substantially:

| Item | Traditional team (2-4 eng, 6-9mo) | AI-assisted build (Claude Code, lean/solo) |
|---|---|---|
| Engineering | $250k–$450k | $50k–$150k (+ small Claude/API usage cost) |
| Legal/entity | $20k–$50k | $20k–$50k |
| Smart contract audit | $15k–$40k | $15k–$40k |
| Compliance review | $20k–$40k | $20k–$40k |
| Working capital buffer | $50k–$100k | $50k–$100k |
| **Total** | **~$350k–$650k** | **~$155k–$380k** |

The reduction is real and concentrated entirely in the engineering line —
research, planning, iteration, and bounded implementation work compress
the way this whole document's own production did. It does **not** touch
audit, legal, or compliance cost: a third party has to review code
regardless of how fast it was written (arguably *more* scrutiny is
warranted when more surface area ships faster), and a lawyer's fee for
entity/ToS/regulatory work is unrelated to development velocity. The
practical effect: as engineering cost shrinks toward a rounding error,
**the bottleneck shifts from "can we afford to build it" to "can we get
it trusted and compliant"** — a fitting result, since trust rather than
code is the actual scarce resource this business sells.

### 7.2 Effect of the objective/discretionary bond-trigger split (Phase 3 ADR-001)

Splitting automatic on-chain slashing (objective, Tier 0/1 evidence only)
from discretionary judgment (Tier 2/3, routed to a multi-party mechanism
rather than a single call from us) — see
`docs/phase3-design-decisions.md` ADR-001 — changes the AI-assisted
numbers above modestly, in exchange for avoiding a much larger tail risk:

| Item | AI-assisted, single-decider | AI-assisted, split |
|---|---|---|
| Engineering | $50k–$150k | $70k–$180k (two payout pathways instead of one) |
| Legal/entity | $20k–$50k | $25k–$60k (structuring a defensible discretionary-mutual framing is specialized work) |
| Contract audit | $15k–$40k | $20k–$50k (two mechanisms to audit) |
| Compliance review | $20k–$40k | $20k–$40k |
| Working capital | $50k–$100k | $40k–$90k (no insurer-style capital reserve) |
| **Total** | **~$155k–$380k** | **~$175k–$420k** |

Ongoing compliance drops from roughly $5k-15k/mo to $2k-8k/mo (not
running a licensed-insurer compliance program), and committee/vote
participant incentives can be funded from the bond pool itself — the same
way UMA pays disputers from the disputed bond, not from UMA's own
treasury — keeping this close to cost-neutral on an ongoing basis.

**The real number is the avoided tail risk.** Checked directly: a full
US multi-state money-transmitter license portfolio runs **$200k-$500k+
upfront (exceeding $1M over time), $225k+/year in ongoing maintenance,
plus surety bonds from $25k up to $7M depending on volume, over a
12-36 month timeline.** That's the exposure a fully-discretionary
"we decide, we pay out" design would risk being characterized as. The
~$20k-40k extra spent upfront on the split is small next to it.

### 7.3 Ongoing operating cost

| Item | Traditional team | AI-assisted, split design |
|---|---|---|
| Team | $40k–$70k/mo | $15k–$30k/mo |
| LLM API (Tier 2 judge calls) | scales with volume — low hundreds → low thousands $/mo early | same |
| TEE partner fees | usage-based, small initially | same |
| Gas/anchoring on Arc | trivial — confirmed ~$2.30 per 100K events batched | same |
| Compliance, ongoing | $5k–$15k/mo | $2k–$8k/mo |
| Hosting/infra | $1k–$3k/mo | same |
| **Total** | **~$50k–$90k/mo** | **~$22k–$48k/mo** |

### 7.4 Revenue and profit — scenario-based, not a forecast

Grounded against a real comparable rather than modeled from nothing: the
closest existing category, on-chain insurance/verification, has a mixed
track record worth respecting. **Nexus Mutual, the category leader, sits
around $150-200M TVL after years of operation; the category overall is
roughly 0.5% penetrated versus 5-10% for traditional insurance; and a
real competitor, Neptune Mutual, shut down in 2025 citing "insufficient
growth."** Our wedge is better-positioned than generic DeFi insurance —
riding a genuinely new, fast-growing volume base (x402's ~69K active
agents / ~$50M cumulative volume by April 2026) rather than competing for
existing locked TVL — but the model should stay conservative, gated on
real adoption data, not hockey-stick assumptions.

| Stage | Adoption assumption | Illustrative revenue |
|---|---|---|
| Year 1 — pilot | A handful of design partners, low hundreds of bonded sellers | ~$50k–$150k, likely sub-breakeven |
| Year 2 — early adoption | 1-2% of active x402 agents as bonded sellers/subscribing buyers, ~$50-150/mo blended revenue each | ~$500k–$2.5M ARR, near-breakeven to modestly profitable |
| Year 3+ — recognized default | 5-10% of a larger, growing ecosystem | ~$5M–$20M range, gross margin likely 70-85%+ once the fixed engineering/compliance base amortizes — marginal cost per verified transaction (an LLM call + gas) stays small |

The gating factor at every stage is real adoption data from the
design-partner phase (§9) — none of these numbers are safe to plan
against until that exists.

## 8. Putting it together — implementation, revenue, adoption, compliance, and running this as a sustainable business

Everything above is spread across this document and three companion
files (`docs/phase2-*.md`, `docs/phase3-*.md`). This section is the
single thread tying them into one story, not new content.

**Implementation path.** Phase 1 (spend monitoring) is shipped and
running on testnet today (§11). Phase 2 (`docs/phase2-architecture.md`,
`-design-decisions.md`, `-backlog.md`) builds the evidence layer every
later claim depends on — ingest existing OTel traces rather than a new
SDK, anchor Merkle roots on Arc rather than raw events. Phase 3
(`docs/phase3-*.md`, ADR-001 through ADR-014, Epics A–G) builds the
trust layer on top: identity and validation on ERC-8004, escrow and
evaluation on ERC-8183, and — the genuinely novel part — the committee,
collusion-detection, and BondPool mechanics that neither standard
provides. The dependency runs one direction only: Phase 3's Tier 0
evidence checks assume Phase 2 evidence exists, and no part of the
committee/bond mechanics (Epic D, and Epic G in full — including its
3.0-tagged collateral core, since locking and slashing real money is
exactly what ADR-013 covers regardless of which milestone a story is
tagged) should be built ahead of real legal review of ADR-013 (§9).
Being tagged Milestone 3.0 answers "what does this feature depend on
technically," not "is this safe to build without legal sign-off" — the
two questions are independent, and only the first one changed when Epic
G was resequenced. That review gate, not engineering effort,
is the actual bottleneck between design and a sellable product — stated
plainly in §7.1, and worth repeating here since it's the one dependency
that isn't ours to accelerate by writing more code.

**Revenue and why it's durable, not just plausible at launch.** The
product is the reputation lookup and the hedge premium (§6.1), priced
like real insurance — expected loss plus a margin (ADR-014) — which
means, unlike a flat subscription, revenue should scale automatically
with real risk rather than needing separate pricing work per segment.
Margin improves with scale because marginal cost per verified
transaction stays small (an LLM call plus gas, per §7.3) while the fixed
compliance/engineering base amortizes — the standard SaaS-adjacent
margin curve, not a novel claim. The harder question — will premiums
actually exceed payouts — is explicitly left open (§9) until real
dispute data exists, and every revenue figure in §7.4 is labeled
accordingly.

**Adoption and GTM, in one sentence each.** Sellers adopt because
instrumentation and tenure directly lower their bond/premium cost
(§6.1) — a financial reason, not a compliance ask. Buyers adopt because
a rational buyer's own risk-assessment logic chooses to hire the hedge
exactly when a transaction warrants it (§6.2) — this is self-selecting,
machine-driven distribution, not a sales motion. Discovery runs through
the same machine-first channels agents already use to find any paid
service (x402 Bazaar, Circle Marketplace, ERC-8004 validator listing,
§6.2–6.3) — there is no separate marketing channel to build.

**Compliance is a standing discipline, not a launch checklist item.**
Two distinct regimes apply, and both are addressed by design choices
already made rather than deferred: money-transmission/custody risk is
avoided structurally by holding no custody on either side (ADR-013 Part
A); insurance-classification risk is narrowed, not eliminated, by the
objective/discretionary split (ADR-001) and the seller-collateral
prerequisite (ADR-013 Part C) — but narrowed is the honest word, and
real legal counsel review of ADR-013 specifically, bundled into the
design-partner outreach itself (§9), is the one step that turns "we
believe this holds up" into "someone qualified confirmed it does" before
any real buyer premium is ever collected.

**Ecosystem fit — Arc first, not Arc only.** Every standard this design
builds on (ERC-8004, ERC-8126, ERC-8183, OpenTelemetry) is chain- and
vendor-neutral — Arc is the first target because Circle's Agent Stack
and USDC-native gas make it the earliest real deployment surface (§2),
not because the mechanism is Arc-specific. The same design ports to any
EVM-compatible agentic-commerce ecosystem that adopts the same ERCs,
which is itself a hedge against over-indexing on one chain's adoption
curve.

**Why this is sustainable, not just viable at launch.** The two hardest
problems in a trust business are usually opposite failure modes — too
fragile to survive being small, too easy to exploit once it's big — and
the design addresses both directly rather than trading one for the
other. Cold start is solved without waiting for scale: the evergreen
calibration track (ADR-009) and dogfooding (Phase 2) let real evidence
accumulate before real dispute volume exists. Getting bigger doesn't
make the mechanism easier to exploit — the opposite: collusion detection
(ADR-008) and the collateral prerequisite (ADR-013) both get *more*
effective with more real data and more locked capital in the system, and
the accumulated calibration/tenure/collusion-clean track record is
exactly the asset a copycat starts at zero on (§6.4). That combination —
survives being small, gets harder to attack as it grows — is what
"sustainable" means here, not a hope that adoption alone will carry it.

## 9. Open questions / next steps

- **ERC family, before writing any contract code**: review ERC-8240,
  8257, 8300, and the 8263/8274/8281/8299 cluster in depth — this space is
  actively moving and Phase 3 shouldn't be scoped against a stale snapshot.
- Confirm current review-thread state of ERC-8004 and ERC-8183 (open
  comments, pending changes) immediately before implementation, not from
  this doc's snapshot.
- Track prEN 18229-1 and ISO/IEC DIS 24970 toward finalization — neither
  was independently re-verified this pass; confirm they're real drafts
  before citing them as a certainty anywhere external-facing.
- Confirm whether Langfuse/Traceloop's OTel export is close enough to the
  raw GenAI semantic conventions to ingest directly, or needs a
  translation layer per tool.
- Confirm whether `circle transaction list` output includes enough
  counterparty/service metadata to attribute spend to a marketplace
  category, or needs a separate enrichment lookup.
- Insurance-pool economics need real modeling once dispute-rate data
  exists from Phase 3 — premiums must exceed expected payout.
- **Validate willingness to pay with 2-3 design partners before building
  the bond/insurance module — and bundle real legal counsel review of
  ADR-013 (`docs/phase3-design-decisions.md`) into that same outreach,
  not as a separate later step.** ADR-013 is the concrete implementation
  of ADR-001's structural principle — no custody on either side, capped
  unprofitable-by-design payouts, seller collateral locked before
  coverage is sold — and it's the piece a lawyer actually needs to see in
  full before any real buyer premium is collected, per §7.2's own
  standing instruction to get this review in parallel with building, not
  after. Design-partner conversations are also the natural venue to
  surface this to counsel concretely, rather than reviewing it in the
  abstract before real usage patterns exist to show them.

## 10. Corrections made in this pass (fact-check against primary sources)

Requested explicitly after this session's research accumulated some claims
from blended AI search summaries rather than primary sources — one of
which (an "Arc Studio commits execution proofs onchain" claim) turned out
to trace to a single uncited secondary article with no corroboration and
was retracted mid-session. This pass checked the rest:

| Claim | Outcome |
|---|---|
| EU AI Act Art. 12 "6 months retention" | **Removed** — primary text doesn't state a retention period |
| EU AI Act Art. 12 "deadline already passed" (2026-08-02) | **Corrected** — Digital Omnibus deferred Chapter III high-risk obligations to 2027-12-02 (Annex III) / 2028-08-02 (Annex I); not yet in force |
| OTel GenAI: content only valid in span events, not attributes | **Corrected** — both are valid per spec; not an either/or |
| UMA 78% vs 98.2% | **Verified exactly** against blog.uma.xyz, with added nuance (different metrics, not strictly comparable) folded in above |
| x402 statelessness, #2222, #3500 | **Verified** via direct fetch |
| ERC-8004 function signatures | **Corrected** to the real, richer signatures from the EIP text, not Arc's tutorial paraphrase |
| ERC-8183 "no rejection function" | **Corrected** — `reject(jobId, reason)` exists; the real gap is narrower (no check on the evaluator's own judgment) |
| ERC-8126 (Final), ERC-8275 (Sybil lesson) | **New findings**, not in earlier passes — added to §4 |
| x402 165M tx / 69K agents | **Verified**, multiple independent sources |
| Marketplace "1,055 listings" | Not re-verified this pass — sourced from Circle's own blog, treated as approximate |

## 11. Current live status

See `docs/SETUP.md` for the full operational log: Circle CLI install/login
state, the live testnet agent wallet
(`0x752942377f0e8a1e8ccb4273550ac7320c2a6755`, ARC-TESTNET, funded), and
the end-to-end validated run of `scripts/poll_spend.py`.
