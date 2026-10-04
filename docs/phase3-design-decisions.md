# Phase 3 Design Decisions

Fourteen ADRs, in the order they were decided, not necessarily the order
that matters for reading. If you're new to this file, read them in this
grouping instead of top to bottom:

- **The core payout principle**: ADR-001 (objective vs. discretionary
  split — no single party can trigger a discretionary payout alone) and
  ADR-002 (build on ERC-8004/8183, not a parallel proprietary system).
- **Who's trusted to arbitrate, and why**: ADR-004 (diversity-weighted
  reputation), ADR-006/007/010 (eligibility — tenure, genuine activity,
  topic relevance, pool-relative and value-scaled thresholds, direct-
  relationship recusal), ADR-009 (the evergreen calibration track that
  solves cold start).
- **Keeping arbitration honest as it scales**: ADR-008 (collusion
  detection — pairwise, single-juror, and graph-cluster level), ADR-005
  (why a Bittensor subnet was evaluated and rejected for this).
- **How a committee actually gets assembled**: ADR-011 (advertised,
  opt-in, random-draw-from-volunteers) and ADR-012 (the four-tier
  escalation ladder for when too few volunteer).
- **The money itself — read this pair before anything else if you're
  reviewing this for legal or financial soundness**: ADR-013 (no custody
  on either side; payouts structurally incapable of rewarding a
  self-dealing buyer-seller pair; a seller must have collateral already
  locked before coverage can be sold against them) and ADR-014 (the
  actual premium/slash pricing formulas).
- **ADR-003** (committee incentives paid from the disputed bond, not our
  treasury) threads through several of the above rather than standing
  alone.

ADR-001 was written early, before Phase 3's architecture or backlog
existed, because it's load-bearing enough (affects capital planning
directly, per `docs/IDEA.md` §7.2) that losing it while waiting for
Phase 2 to ship first would have cost more than capturing it out of
sequence. Everything after it followed once Phase 2 (Milestone 2.0)
was real and Phase 3's design work actually started. Same lightweight
ADR format as `docs/phase2-design-decisions.md`.

## ADR-001: Split objective (code-triggered) payouts from discretionary (judgment-triggered) ones — don't let one mechanism do both

**Decision**: bonds/pools stay fully on-chain, in a smart contract — that
was never in question. What's decided here is *who or what is allowed to
trigger a payout*, split into two structurally separate paths:

- **Objective path** — Tier 0/1 evidence only (schema mismatch, failed TEE
  attestation, duplicate-output hash). Fully code-verifiable, no human or
  model judgment involved. This path can trigger automatic on-chain
  slashing.
- **Discretionary path** — Tier 2/3 evidence (LLM judge score, committee
  vote). Never triggers a payout directly. Routes to a separate,
  multi-party adjudication mechanism — not a single call from us.

**Why**: checked against real precedent rather than reasoned from first
principles. Nexus Mutual, the category leader, deliberately did not go
pure-smart-contract — they wrapped a UK company-limited-by-guarantee
around a *"discretionary mutual"* structure specifically because
*"insurance is already a highly regulated space"* and pure code doesn't
change how regulators characterize the underlying activity. Their own
structuring choice is the useful part: a discretionary mutual is
*"not... a contract of insurance"* precisely because members provide
discretionary cover to *each other*, not because a company promises to
pay. That's a legal characterization lever, independent of custody
technology, and it's directly borrowable.

Putting bond money in a smart contract instead of a bank account reduces
cost and friction (no surety company, no escrow bank) — genuinely worth
doing, already the plan. It does **not** by itself change whether the
*activity* looks like insurance underwriting or money transmission to a
regulator. What does change that: minimizing how much of the payout
decision is *our* discretion, by keeping automatic slashing limited to
objectively verifiable conditions, and pushing genuine judgment calls
into a decentralized-ish mechanism (a committee/vote, à la UMA's DVM or
Nexus's NXM-holder vote) rather than a single company (us) deciding.

**Cost implication** (worked through in full in `docs/IDEA.md`'s
business-model section): modestly higher upfront engineering and audit
cost (two payout pathways instead of one), lighter ongoing compliance
burden, and — the dominant term — avoidance of the tail risk of being
classified as a money transmitter or insurer. A full 49-state MTL
portfolio runs $200k-$500k+ upfront, $225k+/year in ongoing maintenance,
and surety bonds up to $7M depending on volume, over 12-36 months. That
risk, not the smart-contract-vs-bank-account question, is what this
decision is actually about.

**Revisit if**: real legal counsel review (still needed — this ADR is a
design lever, not a legal opinion) finds the objective/discretionary
split doesn't hold up the way Nexus Mutual's did, or transaction volume
grows to a point where a lighter-weight structure is no longer
defensible. Also worth revisiting once there's a track record — Nexus
Mutual itself is now (2026) moving to sunset its legal entity and lift
KYC requirements, suggesting this kind of wrapper is often stage-
appropriate scaffolding rather than a permanent requirement.

## ADR-002: Build on ERC-8004/8183 rather than a parallel proprietary system

**Decision**: identity, feedback, and escrow use ERC-8004's registries
and (where we're named) ERC-8183's evaluator role, instead of a custom
identity/reputation/escrow system.

**Why**: confirmed directly against the EIP text (fetched
2026-09-19, not recalled from an earlier pass — see
`docs/phase3-architecture.md`'s header note) that ERC-8183 states
outright: *"a malicious evaluator can complete or reject arbitrarily"*
and *"no dispute resolution or arbitration; reject/expire is final."*
That is exactly the gap this phase fills — the standard names its own
missing piece, which means becoming a credible, accountable evaluator is
additive to an existing standard's adoption path, not a competing
system asking sellers to trust something new. Same reasoning as ADR-006
in `docs/phase2-design-decisions.md`: build on what's already there and
already has a funnel (Arc's own tutorials point developers at these
ERCs), rather than duplicating it.

**Revisit if**: either EIP's review process surfaces a design change
that breaks this plan's assumptions (both are Draft status, still
moving) — re-check immediately before implementation, not from this
document's snapshot, per the standing instruction in `docs/IDEA.md` §9.

## ADR-003: Committee incentives come from the disputed bond, not our treasury

**Decision**: participants in the Tier 2/3 discretionary-dispute
committee are compensated from the bond under dispute (a small fee
carved out of the resolved amount), not paid a salary or fee from our
own operating budget.

**Why**: this is what keeps the committee mechanism close to
cost-neutral on an ongoing basis (quantified in `docs/IDEA.md` §7.2) and,
more importantly, it's the same incentive design UMA's own Optimistic
Oracle DVM uses — token holders who vote correctly on a dispute are paid
from the dispute's own bond, not by UMA the company. Precedent matters
here specifically because it's the same "who's actually deciding, and
who's paying them to decide fairly" question ADR-001 is built around:
paying committee members from our own treasury would make us look more,
not less, like the single interested party making the call.

**Revisit if**: bond sizes turn out too small in practice to fund a
committee incentive that attracts honest, engaged participants — would
require either a minimum bond floor or a different incentive source,
not a change to who decides.

## ADR-004: Reputation aggregation is diversity-weighted from the first line of code, not added later

**Decision**: any score derived from ERC-8004 `giveFeedback()` history or
our own dispute record uses an attester-diversity weighting scheme
(inverse-Simpson or equivalent) from the very first implementation —
never a naive count of attestations.

**Why**: this is a previously-exploited, publicly-documented failure
mode in the exact same design space, not a hypothetical concern. ERC-8275
(a companion, unmerged ERC in this same author cluster — see
`docs/IDEA.md` §4) had this Sybil vulnerability caught during its own
review: a small number of colluding attester-operators can fake
diverse-looking feedback under naive counting. The fix was written into
that spec as a normative requirement, not an optional hardening step.
Building our own aggregation without this from day one would mean
knowingly shipping a vulnerability someone else already found and fixed
in public.

**Revisit if**: real usage data suggests inverse-Simpson specifically is
either too punishing (legitimate small sellers with few attesters get
under-weighted) or insufficient (a more sophisticated Sybil pattern
emerges) — the principle (never naive-count) is fixed; the exact formula
is not.

## ADR-005: Evaluated and rejected running a Bittensor subnet for Tier 2/3; consider consuming an existing subnet as one input instead

**Decision**: do not build or register a Bittensor subnet as the Tier 2/3
discretionary-dispute mechanism. Keep the multi-party committee design
(ADR-001, ADR-003, ADR-004) as the actual binding decision-maker. Treat
an existing Bittensor subnet, if used at all, as one more external
evidence *input* to that committee — the same "buy, don't build" posture
already adopted for TEE providers — not as a replacement mechanism.

**What was actually evaluated, not assumed**: Bittensor's Yuma Consensus
is not "validators vote, top miner gets paid" — each validator submits a
continuous ranking over all miners on a repeated task, combined into a
stake-weighted median with outlier clipping; both miners and validators
earn ongoing token emissions from protocol-level inflation. It's built
for continuous multi-miner competition on a repeated task, not one-off
binary adjudication of a single dispute.

**Why rejected as the primary mechanism**:

1. **A documented exploit in exactly the dimension we care about.**
   Weight-copying — a validator copying/predicting the aggregate instead
   of doing real independent evaluation — is a known strategy that is
   *more profitable* than honest validation under the stake-weighted
   median dynamics. The system's own mitigation (clipping) only bounds
   collusion up to 50% stake, the same order of guarantee as ordinary
   BFT, not something stronger than our own committee design. Building
   the "malicious arbiter" fix on a mechanism with a known
   honesty-losing exploit at its core would be adopting a flaw we
   already know about, the same category of mistake ADR-004 explicitly
   avoids by not naively counting attestations.
2. **Capital infeasible at this stage.** Subnet registration has run
   $100Ks to over $1.6M historically, on a decaying-but-volatile
   bonding curve, with a hard cap on active slots and **competitive
   eviction of the lowest-performing subnet** whenever a new one
   registers — meaning even after paying to get in, continued
   participation depends on token-price performance, not verification
   quality. This dwarfs the entire Phase 3 capital estimate
   (`docs/IDEA.md` §7, ~$175k-420k for the whole build).
3. **Wrong shape for the actual audience.** Bittensor's participants are
   TAO speculators/miners/validators — a different population from the
   Arc/Circle/x402 buyers and sellers already being targeted. Adopting
   it would ask them to trust a second chain's separate token economics
   for their dispute outcome, directly against Phase 2 ADR-004's "one
   coherent trust stack, one chain" principle.

**What a closer look at actual subnets found** (2026-09-19): **Targon**
(Bittensor SN4) is a GPU compute/inference marketplace with hardware TEE
attestation — it verifies compute *provenance* (a claimed model ran
honestly on claimed hardware), the same job already assigned to
Phala/Marlin/Atoma in `docs/IDEA.md` §5, not subjective output quality.
It's a competing option for that one Tier 0 slot, not an addition to
Tier 2/3. A separate subnet (associated with Subnet 41 "Almanac" and a
project called DegenPredict) resolves prediction-market outcomes by AI
consensus — but that's scoped to exactly the one Arc marketplace
category (`PREDICTION_MARKETS`) `docs/IDEA.md` §5 already concluded we
shouldn't build an oracle for ourselves, since the market's own
real-world resolution already is ground truth. It also carries a
concrete, independent reason for caution: it is reportedly tied up in
an ownership lawsuit. Neither subnet, nor any found in this pass, covers
subjective quality verification for the other four Arc categories
(SOCIAL_INTELLIGENCE, FINANCIAL_ANALYSIS, WEB_SEARCH_RESEARCH,
CREATIVE) — confirming that gap remains genuinely open and is still the
right target for our own committee + Tier 2 LLM-judge design, not
something a Bittensor subscription would substitute for.

**Cost of consuming Targon, if pursued as a Tier 0 alternative later**:
not fully pinned down in this pass — flagging that honestly rather than
estimating a number without a source. Confirmed only that pricing is a
TAO-denominated auction (miners bid hourly rates per GPU/node type),
with stablecoin support described as planned, not universally live. Get
a real quote from Targon's current docs/dashboard directly before
budgeting against it, the same discipline already applied to every other
load-bearing number in this project.

**Revisit if**: Bittensor's incentive-mechanism design changes materially
(a documented fix for weight-copying beyond clipping), or a Phase 3.2
TEE-provider evaluation (already planned in `docs/phase3-backlog.md`)
finds Targon genuinely more cost-effective than Phala/Marlin/Atoma for
provenance evidence specifically — that would be a Tier 0 sourcing
decision, not a reversal of this ADR's core conclusion about Tier 2/3.

## ADR-006: Committee eligibility and vote weight use longitudinal track
record from the Phase 2 ledger, not just identity diversity

**Decision**: being a distinct identity (ADR-004's Sybil defense) is
necessary but not sufficient to sit on the Tier 2/3 committee or to have
a full-weight vote. Two additional, independently-checkable signals are
required, both sourced from data already produced by Milestone 2.0's
evidence ledger (`docs/phase2-architecture.md`), not a new data source:

1. **Tenure/eligibility gate (binary — do they get a seat at all).** A
   candidate juror must have real, anchored history predating the
   dispute by a minimum age — e.g. its `agent_versions`/`operations`
   history in the Phase 2 ledger must span at least N days and include
   activity anchored in at least M distinct epochs (`epochs` table).
   Registering an identity moments before a vote and immediately
   participating is excluded by construction, not by policy — the
   ledger simply has no history to check yet, so the gate fails.
2. **Credibility/breadth weight (continuous — how much their vote
   counts).** Once eligible, a juror's vote weight scales with (a) how
   varied their own real operational history is — distinct
   `operation_type`/`model_id` values in their Phase 2 record, as a
   proxy for "this is a genuinely active, general-purpose agent, not a
   narrow bot built to farm one cheap repeated task for tenure"
   **[flawed as originally stated — see the correction in ADR-010: this
   literally penalizes a genuine deep specialist, exactly the juror
   you'd most want on a topic they specialize in]** — and
   (b), once any dispute history exists, how often their past committee
   votes aligned with the eventual majority-weighted outcome, tracked
   *per dispute category* rather than as one global number, so a juror
   who's only ever been right about `FINANCIAL_ANALYSIS` disputes isn't
   given the same weight on a `CREATIVE` one.

**Why**: this closes exactly the gap named when this idea was raised —
*"what if 5 independent jurors are secretly the same person with 5 fake
accounts"* — with a second, orthogonal defense on top of ADR-004's
diversity weighting. Diversity weighting alone only detects that voters
are *distinct*; it says nothing about whether a distinct identity was
spun up five minutes ago specifically to vote, or has ever demonstrated
real, varied judgment before. A well-funded attacker can manufacture
distinct-looking identities relatively cheaply; manufacturing *aged,
diversely-active, historically-accurate* identities is far more
expensive, because it requires actually doing the thing being verified —
real agent work, sustained over real time — rather than just
registering a new address. This is the same principle ERC-8275's own
review already established for reputation feedback (ADR-004) — extended
here to a different population (committee jurors, not sellers) and a
different dataset (the juror's own Phase 2 track record, not ERC-8004
feedback about them).

**Honest limitation, stated rather than glossed over**: the
credibility-by-past-voting-accuracy signal has a cold-start problem —
on day one of the committee mechanism, zero disputes have ever been
resolved, so there is no voting history for anyone. Tenure and
topic-breadth (from Milestone 2.0's already-real data) can be checked
from day one; accuracy-across-topics can only phase in as real dispute
volume accumulates. Don't pretend otherwise in how this is described to
early design partners — the credibility weight starts thin and gets more
meaningful with usage, the same honest trajectory Phase 2's own
`weak`/`strong` version-resolution distinction already models for a
different signal.

**Open implementation question, not yet resolved**: Phase 2's ledger
schema tracks `operation_type` and `model_id` diversity directly, but
has no notion of Arc Marketplace *category* (FINANCIAL_ANALYSIS,
CREATIVE, etc.) — that mapping would need to come from cross-referencing
a seller's/juror's Marketplace listing metadata, not from the ledger
alone. Needs a design pass before `docs/phase3-backlog.md`'s Epic D
(discretionary disputes) can turn this into real acceptance criteria.

**Revisit if**: real committee usage shows tenure/breadth thresholds are
either too easy to satisfy cheaply (e.g. an attacker running a genuinely
diverse-looking but still centrally-controlled fleet of agents over
time) or too strict (locking out legitimate new-but-active agents
indefinitely) — the principle (track record must be real and checkable,
not asserted) is fixed; the exact thresholds are not.

## ADR-007: Committee eligibility is pool-relative with an absolute
floor, and the bar scales with dispute value

**Decision**: instead of a single hard-coded absolute threshold for
ADR-006's tenure/breadth gate, use a **percentile rank relative to the
current eligible pool**, subject to two additional constraints: (a) a
minimum absolute floor underneath the percentile (so a thin, uniformly
young pool can't trivially satisfy "top 50%"), and (b) a bar that
**scales up with the dollar value of the dispute being judged** — larger
disputes require a smaller pool of higher-percentile, longer-tenured
jurors; small disputes can draw from a larger, lower-bar pool.

**Why**: a fixed absolute threshold requires guessing a number with no
data to guess from — the exact problem ADR-006 already admitted it
couldn't solve cleanly. Pool-relative scoring self-calibrates as the
ecosystem grows instead. But relative scoring alone has its own failure
mode: in a small pool, "top 50th percentile" is a weak bar if an
attacker controls a meaningful share of that pool — hence the absolute
floor. The value-scaling piece answers a distinct, sharper risk raised in
discussion: a sophisticated attacker doesn't need to wait for real money
before acting — the *rational* attacker builds "aged, diverse-looking"
sleeper identities cheaply during the low-scrutiny cold-start period,
specifically so they look legitimate by the time real stakes appear
(the same pattern seen in real reputation fraud — e.g. fake reviewer
accounts cultivated for months before being used). Scaling the
eligibility bar with dispute value means a sleeper identity's cheaply-
built credentials from the cold-start period don't automatically clear
the *high-stakes* bar later — that bar is recomputed against the pool's
distribution *at the time of the high-stakes dispute*, when a real,
non-gamed population will have grown around them, diluting any
early-mover advantage rather than letting it compound.

**Revisit if**: real usage shows the value-scaling curve is either too
aggressive (locking honest, established jurors out of high-value
disputes unnecessarily) or too permissive (a well-resourced attacker
still clears even the high-stakes bar) — the mechanism (scale the bar
with stakes, not with system age alone) is the fixed principle; the
exact curve is a tuning question for real data, not a decision made here.

## ADR-008: Longitudinal collusion detection — the primary
sleeper-attacker defense, extended beyond pairwise agreement

**Framing correction, stated plainly rather than left implicit**: an
earlier conversation about this ADR drifted toward treating a proposed
covert-honeypot mechanism as *the* fix for sleeper attackers, with this
ADR's original two signals implied to be insufficient on their own. That
overstated the honeypot's role and understated this ADR's. The correct
framing: **the mechanisms below, using only real dispute history, are
the primary sleeper-attacker defense** — they work given enough real
volume and time, for the same reason a colluding pair's votes must
sometimes diverge from honest, independent judgment to be worth
colluding at all. Honeypots (added at the end of this ADR) are a
secondary accelerant that supplies a *known* ground truth instead of
relying on the rest of the committee's honest majority as a *proxy* for
one — useful, especially while real volume is thin, but not the
mechanism the defense depends on.

**Decision**: track five behavioral signals, not two, all measured
against what an honest, independent population would statistically
produce — never raw counts, never a hand-picked absolute bar:

1. **Co-participation frequency** — how often two wallets end up
   selected onto the same committee together, relative to the rate fair
   random selection from the eligible pool would predict.
2. **Agreement correlation** — how often they vote the same way *when*
   selected together, measured as agreement **above** what's expected
   given each juror's own individual accuracy rate (not raw agreement),
   and weighted more heavily when it holds across topically *different*
   disputes (using ADR-006's topic-diversity data) rather than one
   narrow repeated category.
3. **Divergence-from-majority (new, single-juror level)** — does this
   *one* juror's vote diverge from the eventual committee majority more
   often than their own general accuracy predicts, and does that
   divergence disproportionately benefit the same counterparty? This
   needs no suspected partner identified in advance and no pairwise
   search — it flags a single wallet directly, using the honest
   majority's aggregate outcome as a working proxy for truth, the same
   principle Yuma Consensus and UMA's DVM both rely on for a different
   purpose (reward, not detection).
4. **Voting-graph clustering (new, population-level)** — build a
   correlation graph over the whole eligible juror population, edges
   weighted by signals 1-2, and look for anomalously dense *clusters*,
   not just anomalous pairs. A ring of 4-5 identities can spread
   coordination thin enough that no single pair crosses a pairwise
   threshold while the group still functions as one coordinated actor —
   the same reason real fraud-ring detection (financial fraud,
   peer-review rings, esports match-fixing) uses graph/community
   detection rather than pairwise checks alone.
5. **Economic-activity-graph clustering (new, closes a real loophole in
   ADR-010B)** — apply the same clustering technique to the *economic*
   counterparty graph behind ADR-010B's genuine-activity signal, not
   just the voting graph. ADR-010B's fix (weight real transaction value
   and distinct counterparties instead of topic variety) is itself
   gameable: a puppet fleet can wash-trade with *each other* to
   manufacture fake-but-real-looking economic legitimacy without ever
   touching a genuine external customer. Checking whether a candidate's
   claimed "distinct counterparties" trace back to other addresses
   already in a suspected voting cluster closes this without requiring a
   new data source — it's the same Phase 2/x402 payment history ADR-010B
   already reads.

Response remains graduated, on the same two levers as originally
designed: reduced future joint-selection probability, and reduced vote
weight — now informed by all five signals, and by cluster membership
(signal 4/5) rather than only pairwise flags. Neither is a hard,
one-time exclusion.

**Why the original two signals were already sufficient in principle, and
why the extensions still matter**: a colluding pair's objective is to
extract value, which means their coordinated vote must sometimes differ
from what independent honest judgment would produce — that divergence is
detectable given enough real disputes, with no honeypot required. The
extensions matter because the *cost* of detection matters: divergence-
from-majority (signal 3) is far cheaper to compute than an exhaustive
pairwise search and doesn't require having already guessed who the
colluding partner is; graph clustering (signals 4-5) catches a ring that
deliberately spreads thin specifically to dodge pairwise thresholds — a
real evasion a sufficiently patient attacker would eventually try once
pairwise detection alone became known to exist.

Frequency (signal 1) matters as a first-class input, not just a
component of agreement, because a colluding pair's actual goal is to
*maximize joint opportunities* to swing outcomes — the same logic real
cartel/bid-rigging detection uses: investigators look at both whether
bidders coordinate when competing *and* whether they show up in the same
auctions unusually often. Overrepresentation is itself evidence,
independent of what happens once a pair is together.

The "above baseline, not raw" qualifier on agreement (signal 2) is
load-bearing, not a nuance: two genuinely honest, skilled jurors will
naturally agree with each other often, simply because they're both good
at the job and clear-cut cases have an obvious right answer. A naive
raw-agreement metric would punish competence as if it were collusion.
Only agreement exceeding what each juror's own accuracy predicts is real
evidence of coordination — and the same "above baseline, not raw"
discipline applies to signal 3's majority-divergence check.

**Secondary accelerant: covert honeypot injection.** Periodically and
*unpredictably* — never on a fixed schedule, which a patient attacker
would learn to detect and behave honestly around — inject a fully
synthetic dispute, with synthetic disputing parties and a synthetic
bond so no real party or real funds are involved, formatted
indistinguishably from a real one, into the live committee-selection
stream. Because its correct answer is known in advance, any deviation
from it is direct evidence, not a statistical inference relying on the
honest majority as a proxy. This is standard practice in crowdsourcing
and content-moderation quality assurance (hidden "gold-standard" tasks
mixed into real work), applied here to sleeper-attacker detection
specifically. It is a genuine strengthening, especially valuable while
real dispute volume is still thin and signals 1-5 haven't accumulated
enough history to be reliable on their own — but it supplements the five
signals above; it does not replace them, and this ADR's core defense
does not depend on it existing.

**Constraint, not optional polish**: any adjustment to *selection
probability* — from any of the five signals, or from honeypot results —
must be a fully deterministic, publicly auditable function of on-chain
data, never an opaque internal decision. Quietly reducing a wallet's
odds of being drawn based on our own internal scoring would recreate
exactly the single-party-discretion problem ADR-001 exists to prevent,
just relocated into the selection mechanism instead of the payout
mechanism. Anyone must be able to recompute "why was this pair's or
cluster's future joint-selection odds reduced" from public inputs alone.

**Honest limitations**:
- Small-sample false positives are a real risk across all five signals,
  arguably more than anywhere else in this design. A minimum number of
  joint appearances (or, for signal 3, a minimum number of votes cast)
  must be required before treating a result as meaningful — otherwise
  genuinely honest, unrelated jurors could be unfairly and durably
  penalized from noise alone.
- Honeypots carry their own tension: too rare and the signal is weak,
  too frequent and real committee capacity is burned and the odds of a
  sophisticated attacker reverse-engineering which disputes are fake
  rise. Never confirming which resolved disputes were honeypots, even
  after the fact, is part of the defense, not a nice-to-have.
- None of this — five signals plus honeypots together — is airtight
  against a maximally patient, maximally sophisticated adversary. It
  raises the cost of the attack substantially; it does not make the
  attack impossible. That's the realistic goal, stated plainly rather
  than oversold.

**Related, distinct signal, now actually designed rather than deferred**:
juror-to-specific-disputant correlation (a juror who suspiciously favors
one particular seller or buyer) is evidence of a different problem —
favoritism or bribery, not juror-juror collusion. This was originally
left as a one-line "needs its own tracking" note here; it's now fully
designed in ADR-010, prompted by the correct observation that it may be
a more direct and common corruption vector than juror-juror collusion
itself.

**Revisit if**: real dispute volume shows the false-positive rate at any
chosen minimum-sample threshold is unacceptably high, honeypot injection
frequency turns out detectable via some tell not yet identified, or a
coordination pattern emerges that none of the five signals nor honeypots
catch — the underlying principle (compare observed behavior to an
honest-population null model, generalizing to new patterns as they're
found, never a hand-picked absolute bar) is meant to extend to whatever
is discovered next, not be re-invented from scratch each time.

**Implementation note, not yet its own ADR** (2026-09-20): however a juror/
arbiter agent reaches its conclusion, the vote it submits to us needs to
arrive as a strictly typed, schema-valid value (a fixed outcome enum, a
bounded liability score) — never free text we have to parse. Routing the
agent's already-formed conclusion through a constrained-output layer
before submission (TypeSafe AI's "Jev" is one candidate) is a boundary
type-check, not a second opinion — no independent judgment is exposed to
other jurors, so this doesn't reopen the weight-copying failure mode
ADR-005 rejected Bittensor over. Revisit once such a layer has a real
track record; until then, noted option, not a dependency.

## ADR-009: Evergreen calibration track for arbiter onboarding, scored
with a proper scoring rule — not a one-time bootstrap window

**Decision**: build an always-available "Calibration Track" — synthetic
disputes with known correct answers (and, once real disputes exist,
optionally replayed resolved real disputes used as calibration
material), graded in increasing ambiguity. Any candidate, joining at any
time, can work through it and receive a score, computed with an
established proper scoring rule (Brier score or an ELO-style rating),
not raw percent-correct. A strong calibration score can fast-track
eligibility for *low-stakes* real disputes (composing with ADR-007's
value-scaled floor); it does not substitute for the real accumulated
tenure and track record ADR-006/007 require for *high-stakes* eligibility.

**Why, and a correction to the originating idea**: the proposal that
prompted this was framed as "similar to Bitcoin's proof of work" — worth
being precise that the actual mechanism here is not proof-of-work
(computational cost as sybil resistance). It's closer to **graded
calibration tasks against known ground truth**, which has real, mature
prior art directly on point: forecasting platforms like **Metaculus** and
the **Good Judgment Project** build calibrated forecaster reputations
exactly this way — new forecasters are scored against *resolved*
historical questions before their opinions carry weight on live ones.
Crowdsourcing platforms use the same idea via "gold-standard" tasks with
known answers mixed into real work. This is useful beyond terminology:
it means a well-studied, already-proven methodology exists to borrow
from, rather than a mechanism to invent from scratch. The Brier-score
recommendation follows directly from that prior art — it properly
penalizes overconfidence (a juror always certain and occasionally wrong
scores worse than one appropriately uncertain on hard cases), which
matters more for an arbiter than raw accuracy alone.

The genuinely valuable part of the original Bitcoin-inspired instinct
survives the correction and is worth stating plainly: **bootstrap trust
cheaply, before real stakes exist, so a track record already exists by
the time it matters.** This directly resolves ADR-006's stated cold-start
limitation — the accuracy-by-voting-history signal there could only
phase in as real dispute volume accumulated; a Calibration Track produces
a meaningful score for any candidate immediately, using synthetic data we
control, without waiting for real disputes at all.

**Where this must deliberately diverge from Bitcoin, not imitate it**:
Bitcoin's actual dynamic is that the cheap early period is gone forever,
permanently advantaging early miners over every later entrant. That
dynamic would be actively harmful here — Arc's agent population is
expected to keep growing (`docs/IDEA.md` §2), and we need the arbiter
pool to keep admitting new, high-quality jurors indefinitely, not
entrench whoever joined first. So the Calibration Track must be
**evergreen** — the same graded exam, available on the same terms, to
every candidate regardless of when they join. Joining later in calendar
time should cost nothing but not having taken the exam yet.

**Open funding question, not resolved here**: ADR-003 funds committee
incentives from the disputed bond itself — that model doesn't apply to
calibration tasks, since there is no real disputed bond behind a
synthetic exercise. A small, separate incentive (real but low-value,
echoing the "cheap-early-coin" instinct without importing its permanent-
advantage flaw) needs its own funding source — a modest treasury
allocation, or a non-monetary credential-only reward whose only value is
unlocking future real-dispute eligibility. Not decided here; flagged as
a real open question before this ADR is buildable.

**A strategic observation worth keeping, not designing further yet**:
this professionalizes the arbiter role into a genuinely distinct class of
agent — one whose product is judgment itself, not task completion,
separate from the seller and buyer agents everything else in this
project has scored. That points naturally toward a future "Verified
Arbiter" role or Marketplace category, the agent-economy equivalent of a
referee, auditor, or notary being a distinct profession rather than
something any agent does incidentally. Not a decision to act on now —
noted here so it isn't lost, consistent with how this document already
treats forward-looking observations elsewhere (e.g. ADR-002's standards-
adoption reasoning).

**Field validation, 2026-10-04**: this exact pattern — score a candidate
against graded, verifiable cases before real stakes exist, so a track
record already exists by the time it matters — was independently
re-derived and actually built for a different subject.
[`vadium-attest`](../../vadium-attest) applies it to ChatGPT-ecosystem
*sellers' tools* rather than arbiters, for an equivalent cold-start
problem found in production: `vadium-lookup`'s self-reported
`report_outcome` mechanism turned out to have no natural incentive for a
ChatGPT integrator to ever use, so there's no organic way to accumulate a
track record for those sellers either (see `vadium-lookup/docs/chatgpt-
apps-warm-start.md` for the full problem statement). vadium-attest's
staged task battery (`vadium-attest/docs/methodology.md`) is this ADR's
Calibration Track concept, concretely implemented and already structured
to run against real test accounts — graded, independently-verified tasks
with a checkable correct outcome, the same shape as a calibration
exercise with a known answer key, just verified against live system state
instead of a pre-written answer. Worth reading before implementing this
ADR for real: the "never trust the write call's own response, verify
independently" rule and the consistency (Pass^k) metric there are
directly reusable design decisions, not just an analogy — see
[`docs/vadium-project-map.md`](vadium-project-map.md) in this repo for
how all three repos relate.

**Sequencing decision, covering ADR-006 through ADR-009 at the time,
now the full ADR-006 through ADR-014 arc**: resolved 2026-09-19 — build
the full mechanism, not the simplified version, as the project's primary
market defensibility. The reasoning: this mechanism's code is necessarily
auditable (Epic F1 requires it to be independently checkable that no
single party can trigger a discretionary payout), which means the code
itself is copyable by any competitor who reads it. What isn't copyable is
the accumulated calibration history, tenure, and collusion-clean track
record of real arbiters who have already been through the mechanism in
our system — a copycat launching the same design starts at zero on
exactly the data that makes the mechanism trustworthy. The more elaborate
the mechanism, the higher the bar to replicate that accumulated trust
quickly, which is the actual defensibility, not secrecy. Everything added
since this decision (ADR-010's relationship/breadth fixes, ADR-011's
advertise-and-volunteer model, ADR-012's escalation ladder, ADR-013's
custody/unprofitability/collateral corrections, ADR-014's pricing
formulas) is downstream of this same call, not a reopening of it.

This decision raises the execution-risk stakes, not lowers them —
worth stating plainly rather than only celebrating the upside: this is a
genuinely elaborate system to get right the first time, and for a
business whose entire product is "trust our judgment," a bug in an
elaborate mechanism is a worse failure than being simple and slow. The
build sequence in `docs/phase3-backlog.md` Epic D (D.1 raw signals → D.2
eligibility/selection → D.3 collusion detection → D.4 hardening/legal
validation) is staged specifically to manage that risk — each stage
produces something independently useful and testable before the next
stage builds on it, rather than attempting all four ADRs as one
monolithic build.

**Revisit if**: real usage shows the calibration track's synthetic
disputes don't predict real-dispute performance well (a risk with any
proxy-task calibration system) — would mean redesigning the task
curriculum, not abandoning the evergreen-onboarding principle itself.

## ADR-010: Arbiter-disputant relationship checks, and a fix to
ADR-006's breadth signal penalizing genuine specialists

Two corrections found on review of ADR-006/007/008, the same way the
Milestone 2.0 tamper test found two real bugs by testing rather than
just reading the design — worth fixing at the design stage before either
reaches code, not after.

### Part A: arbiter-disputant correlation was deferred in ADR-008, not designed — fixed here

**Decision**: two separate mechanisms, not one, because they operate on
different timescales and different kinds of evidence:

1. **Hard recusal at selection time (real-time, no history required).**
   Before a candidate is drawn onto a dispute's committee, check whether
   they have any direct prior transactional relationship with either
   disputing party — a payment, a service purchase, a shared
   counterparty — visible in Phase 2 ledger or on-chain payment history.
   Any hit disqualifies that candidate from *that specific dispute's*
   committee. This needs zero accumulated pattern data; it's a direct
   factual check, computable the first time the mechanism ever runs.
2. **Longitudinal favoritism tracking (statistical, needs real history,
   same shape as ADR-008's juror-juror correlation).** Even with no
   direct relationship on record, track whether a specific juror's
   ruling pattern shows above-baseline correlation with ruling in favor
   of a specific seller or buyer across many disputes over time — the
   same "compare to an honest-population null model" principle ADR-008
   already established, applied to a juror-vs-counterparty pair instead
   of a juror-vs-juror pair. This catches subtler bias or off-chain
   collusion that a direct-relationship check can't see, and — like
   ADR-008's own signal — needs a minimum sample size before being
   treated as meaningful, for the same false-positive reasons already
   stated there.

**Why this needed two mechanisms, not one**: the question that surfaced
this — "is the co-occurrence of an arbiter *with the disputing parties*
accounted for, not just arbiter-arbiter co-occurrence?" — is arguably a
more direct and common corruption vector than juror-juror collusion:
real-world judicial systems treat "does the judge have any prior
relationship with a party" as a basic, mandatory recusal check, done
immediately and factually, not inferred statistically after years of
rulings. Building only the longitudinal version (as the original ADR-008
draft implicitly assumed by deferring this to "needs its own tracking")
would have meant the most basic, cheapest-to-implement integrity check —
a real-time conflict-of-interest screen — was missing entirely at
launch, with only a slow, data-hungry statistical detector standing in
for something that should have been a same-day factual lookup.

**Revisit if**: the recusal check's definition of "prior relationship"
proves too narrow (misses indirect relationships worth excluding) or too
broad (excludes so many candidates in a small pool that eligible
committees can't be formed) — the two-mechanism split itself is not in
question; only where the recusal boundary is drawn.

### Part B: fixing ADR-006's breadth signal, which penalized genuine depth

**The flaw, stated plainly**: ADR-006 used topic/operation-type variety
as a *positive* weight — more distinct topics, higher credibility. This
was designed as an anti-farming signal (a narrow bot repeating one cheap
task to pad tenure looks suspicious), but it has a real, damaging side
effect: a genuine specialist — an agent with years of deep, substantial
history doing nothing but sophisticated financial analysis, say — scores
*lower* on breadth than a shallow generalist, despite being exactly the
juror you'd most want judging a `FINANCIAL_ANALYSIS` dispute. The signal
conflated two different things that need to be separated.

**Decision**: split the single breadth metric into two independent axes:

1. **Genuine-activity check (anti-farming, replaces topic-variety as
   this signal's basis)** — measured by real economic substance: total
   real transaction value and count of distinct real counterparties from
   *paid* x402/Marketplace activity, not by how many different
   `operation_type` values appear in the ledger. This is harder to fake
   for the same reason ADR-006's own core argument already established:
   manufacturing real economic value and real distinct paying
   counterparties costs real money and real time, unlike issuing free or
   trivial repeated API calls to rack up an operation count cheaply.
2. **Topic-relevance for the specific dispute at hand (evaluated
   per-selection, not as a blanket eligibility requirement)** — a
   candidate qualifies on this axis by showing *either* broad general
   coverage *or* deep, substantial history in the dispute's own specific
   category. Both paths count positively. A specialist is never
   penalized for lacking breadth outside their specialty; they're
   evaluated on depth *within* the topic they're actually being
   considered for.

**Why this fix is correct and not just a patch**: it removes the
contradiction that was already latent in ADR-006 itself — point (b) of
the original design already tracked accuracy *per dispute category*,
explicitly because topic-specific expertise was expected and valued. The
breadth signal in point (a) was quietly working against that same goal.
Separating "is this a real, non-farmed agent" (economic substance) from
"is this agent qualified for *this* topic" (breadth-or-depth, evaluated
per dispute) resolves the contradiction rather than papering over it.

**Revisit if**: real usage shows economic-value/counterparty-count is
itself gameable more cheaply than expected (e.g. wash-trading-style
fake-but-real-looking transactions between colluding wallets) — would
require a further refinement to what counts as "genuine" economic
activity, not a reversion to topic-variety as the anti-farming proxy.

## ADR-011: Advertised, opt-in candidacy with a random draw from
volunteers — not a forced blind draw; and two simplifications this forces

Prompted by a direct challenge to the committee-selection and
opportunity-cost assumptions made in ADR-006 through ADR-010. Both
challenges turned out correct and improved the design — one by showing
an earlier proposal was unnecessary, one by fixing a real gap in how
selection worked.

### Part A: committee assembly is advertise-and-volunteer, then random draw from volunteers — not a blind forced draw

**Decision**: a dispute's candidate pool is computed exactly as before
(ADR-006/007/010B eligibility, ADR-010A recusal) — nothing about who
*qualifies* changes. What changes is how a committee is actually
assembled from that pool:

1. The dispute is advertised only to the already-eligible,
   already-non-conflicted pool for that specific dispute (not broadcast
   universally) — closer to a job posting than a summons.
2. Interested, eligible candidates volunteer within a window.
3. The committee is filled by a **random draw from the volunteers**, not
   simply the first N to respond, and not everyone who volunteers.

**Why**: the original design (D2b, unchanged until now) assumed agents
would be drawn and would serve regardless of whether it was worth their
time — a real, unaddressed opportunity-cost problem, since serving on a
dispute committee competes directly with a busy specialist's normal paid
work. Forcing participation, or trying to hand-tune a fee schedule that
guarantees participation is always worthwhile, are both worse than
letting the market clear it: an agent volunteers exactly when the
advertised fee is worth its time, and doesn't when it isn't. This also
resolves cleanly with a fact already established but underused until
now: **only contested disputes ever reach this mechanism at all** — the
overwhelming majority of transactions settle via Tier 0/1 or are never
disputed, so real arbitration demand on any given specialist's time is
inherently sporadic, not a standing competing obligation.

**The randomness draw-from-volunteers step is not optional decoration —
it's what keeps ADR-008's anti-collusion machinery intact.** If every
volunteer simply served, a colluding pair could guarantee joint
appearances just by both choosing to respond to the same disputes —
turning opt-in into a stronger collusion channel than blind random
selection ever was. Drawing randomly *from* the volunteer pool keeps the
same auditable-randomness property D2b already required, while still
letting the fee/opportunity-cost problem resolve itself at the
volunteering step.

**A consequence worth stating directly, not treated as a side effect**:
opting in together repeatedly is now the primary way a colluding pair
would try to inflate their joint appearances — which means ADR-008's
co-participation-frequency signal (signal 1) becomes *more* load-bearing
under this design than it was under a blind draw, not less. No new
detector is needed; the existing one simply does more of the actual work
now.

**Honest new risk, not present under a blind draw**: a thin volunteer
pool. A niche or low-fee dispute might not attract enough eligible
specialists to bother responding, producing a small or weak committee
where a blind draw could always have pulled from the full eligible pool
regardless of interest. Needs either a fee floor calibrated to guarantee
real interest, or a fallback (broaden the advertisement, or raise the
fee) when volunteer count falls short of the needed committee size —
not resolved here, flagged as a real open design question.

**Revisit if**: real usage shows volunteer counts are consistently too
thin even with reasonable fees (would mean the fallback mechanism needs
to be a first-class part of the design, not a rare edge case), or the
co-participation-frequency signal's false-positive rate rises now that
legitimate high-demand specialists volunteering often looks superficially
similar to a colluding pair volunteering together often — the two need
to be distinguishable, which the "above baseline given each juror's own
overall accuracy" qualifier already established in ADR-008 should
handle, but this needs real data to confirm, not just an assumption
carried over from the blind-draw design.

### Part B: symmetric favoritism tracking replaces a proposed
competitor-conflict mechanism that turned out redundant

**Decision**: do not build a separate market-competitor
conflict-of-interest detector, as an earlier discussion of this design
proposed. Instead, make one small but important clarification to
ADR-008 signal 3 and ADR-010A Part A(2): favoritism tracking must be
**symmetric** — flagging both undue *favor* toward a counterparty and
undue *disfavor* against one, not favor alone as originally described.

**Why this is a retraction, not an addition**: a specialist agent ruling
harshly against a market competitor out of ordinary competitive
self-interest, rather than honest judgment, produces exactly the same
statistical signature as bribery-driven favoritism — a correlated
deviation between a specific juror and a specific counterparty, just in
the opposite direction. Building a dedicated "competitor conflict"
detector would have duplicated machinery that already exists once it's
described correctly. This is a real instance of the discipline this
project has tried to hold itself to elsewhere (e.g. not building a
parallel identity system when ERC-8004 already covers it, ADR-002) —
recognizing that a proposed new mechanism is redundant is as valuable a
design outcome as building a genuinely new one, and cheaper.

The underlying claim this correction rests on — that a fair, healthy
population of jurors and a working longitudinal detector will surface
and correct this kind of bias without a dedicated, purpose-built
mechanism — is accepted as correct specifically *because* the detector
already exists and already generalizes to this case; it would not have
been correct as a general argument for skipping detection of bias
altogether.

**Revisit if**: real dispute data shows disfavor-driven bias has a
different statistical signature than favor-driven bias in practice (e.g.
requiring a different minimum-sample threshold) — would mean tuning the
existing detector's parameters per-direction, not building a second one.

### Part C: calibration and honeypot participation is treasury-funded, not bond-funded — resolving ADR-009's open question

**Decision**: the funding source ADR-009 left open is resolved —
calibration-exercise and covert-honeypot participation rewards are paid
from a small team/treasury allocation, not from any disputed bond.

**Why**: ADR-003's bond-funded incentive model only works when a real
disputed bond exists to fund it from; synthetic calibration and honeypot
tasks have no real bond behind them by construction. A separate,
modest, real allocation is the only funding source that was ever
actually available for this — confirmed directly rather than left as a
placeholder.

**Revisit if**: calibration/honeypot volume grows large enough that the
treasury allocation becomes a meaningful ongoing cost line — would be a
budgeting question for `docs/IDEA.md` §7, not a reason to change the
funding source itself.

## ADR-012: A four-tier escalation ladder when volunteers fall short — not one fallback, in a fixed order, cheapest and least-compromising first

Resolves the open question ADR-011 Part A explicitly left unanswered:
what happens when the advertise-and-volunteer step doesn't produce
enough volunteers to fill a committee.

**Decision**: escalate through four tiers, in order, only advancing to
the next when the current one fails — never skip ahead, and never
silently seat an undersized or under-qualified committee without going
through the ladder:

1. **Extend the response window and raise the advertised fee**, then
   re-advertise to the *same* already-eligible, already-non-conflicted
   pool. This is the cheapest fix and the right first response
   specifically when the shortfall is a *pricing* problem — real
   eligible specialists exist but didn't find the original fee worth
   their time. The fee increase is carved from the disputed bond, capped
   at a defined ceiling relative to the bond's total value, so an
   escalating fee can never eat a meaningful share of the buyer's
   eventual restitution regardless of how thin volunteering is.
2. **Broaden eligibility one step down** (relax ADR-007's percentile
   rank or absolute floor by a defined increment) and re-advertise with
   a longer window. This is the right response when the shortfall is a
   *population* problem instead — a genuinely niche category with too
   few real specialists to summon at any fee. Broadening has a hard
   floor beneath which it will not go, regardless of how many times this
   tier fires for a given dispute — the worst case is a somewhat lower
   bar, never no bar.
3. **Draw from a small standing reserve** of agents who have explicitly
   pre-committed to being available on short notice, compensated by a
   modest treasury-funded retainer (not bond-funded, since a retainer is
   owed whether or not it's ever actually called on) rather than the
   per-dispute fee. This is a last-resort safety net, not a return to a
   "hired arbiter" model as the default — it exists specifically to stay
   rare, preserving the advertise-and-volunteer model (ADR-011) as the
   norm.
4. **Seat a smaller committee under a stricter approval threshold**
   (e.g. unanimous instead of a majority), restricted to disputes below
   a defined value ceiling. This is the least good option and is treated
   as such — a smaller committee is measurably easier to collude on, and
   a stricter threshold only partially compensates. Capping it to
   low-value disputes bounds the downside by the same logic ADR-007
   already established in reverse: a thin, weaker committee is an
   acceptable risk only when the harm ceiling is capped by the dispute's
   own low value.

**Why an ordered ladder, not a single fallback**: the two most likely
real causes of a shortfall — pricing and population scarcity — call for
different fixes, and trying the cheap, non-compromising fix (tier 1)
before any fix that weakens eligibility or committee strength (tiers
2-4) means the design never gives up rigor it didn't have to. This
mirrors the same "objective before discretionary" ordering discipline
ADR-001 already established for payout mechanisms, applied here to
committee-formation instead.

**A gaming vector worth naming explicitly, consistent with how every
other mechanism in this document has been checked for one**: could a
party deliberately structure a dispute to look unattractive, forcing
escalation to a weaker tier specifically to get a favorable outcome from
a lower-bar or smaller committee? The fee-escalation cap (tier 1) limits
how much of this benefits anyone financially, and the population-floor
(tier 2) limits how far eligibility can be pushed down regardless of
cause. The stronger mitigation: **track how often escalation fires for
disputes involving a specific seller or category**, using the same
"compare observed frequency to an honest-population baseline" principle
already applied throughout ADR-008 — a seller whose disputes
suspiciously and repeatedly trigger escalation is itself an anomaly
worth surfacing, not just a coincidence to shrug off. This is the third
recurring instance of the same design principle in this document (after
ADR-008's collusion detection and ADR-010's activity-graph checks):
build the mechanism, then check whether *usage of the mechanism itself*
produces an exploitable or informative pattern.

**Not specified here, deliberately**: exact fee-increment size, window
extension duration, eligibility-broadening step size, reserve pool
minimum size, and the low-value ceiling for tier 4. Every other
threshold in this design (ADR-006 through ADR-011) has been left to real
usage data rather than guessed in advance, and this ADR follows the same
discipline rather than being the exception.

**Revisit if**: real usage shows tier 1 (fee escalation) rarely resolves
a shortfall on its own, suggesting most real shortfalls are population-
driven rather than pricing-driven — would argue for reordering tiers 1
and 2, or running them in parallel rather than strictly sequentially, not
for abandoning the ladder structure itself.

## ADR-013: BondPool custody, unprofitability, and the seller-collateral
prerequisite — three corrections that make the mechanism actually work

Written after a sequence of direct challenges exposed that earlier
descriptions of `BondPool` were describing outcomes ("the seller's bond
gets slashed") without having actually designed the mechanism that makes
those outcomes possible. All three parts below are corrections, not
extensions — none of this changes the payout governance already
established in ADR-001/003/008; it fixes how money actually gets in,
stays safe, and comes out.

### Part A: we hold no custody, on either side

**Decision**: the job payment is never held by us — it's held by the
ERC-8183 job escrow contract itself, and we are the **evaluator** (a
role that renders a verdict, per Epic E) telling that contract who gets
the funds it already holds. Separately, `BondPool` is a smart contract
we deploy and whose release logic we design, but fund movement out of it
is governed entirely by code (ADR-001's objective/discretionary split),
never a direct call from us.

**Why this matters beyond precision**: if we personally, custodially
held buyer and seller funds the way a bank or payment processor does,
that's a *third* regulatory regime (escrow-agent and money-transmitter
licensing) stacked on top of the insurance-classification question
already discussed — and we already have real cost figures for how
expensive that regime is (the state-by-state money-transmitter licensing
research in `docs/IDEA.md` §7.2). Holding no custody anywhere in this
design isn't a nice-to-have; it's what keeps that third regime from
applying at all.

### Part B: the payout design must make self-dealing fraud unprofitable, not just hard to detect

**Decision**: three rules, all enforced structurally, not by policy:

1. A dispute payout to a buyer can never exceed what that buyer actually
   paid for that specific job.
2. A premium paid to purchase hedge coverage is never refunded,
   regardless of the dispute's outcome — the same as real insurance:
   you don't get your premium back for not filing a claim, and you don't
   get it back for filing and winning one either.
3. Any seller-bond slash beyond simple restitution of the buyer's own
   payment routes to the **shared pool**, never to the specific
   disputing buyer.

**Why**: this directly defeats the self-dealing arbitrage attack
identified earlier (one attacker controlling both the buyer and seller
side of a transaction, delivering deliberately bad work, then disputing
it to extract a payout). Run the numbers with all three rules in place:
the attacker's own escrowed payment returns to them (a wash — it was
always their own money), their premium is gone permanently, and their
slashed collateral goes to the pool, not back to them. The result is a
**guaranteed net loss**, even when the attack is executed perfectly and
never detected. This is a defense that doesn't depend on catching
anyone — it makes the exploit irrational by construction, which is a
strictly more robust class of defense than detection alone (detection —
tenure gating, dispute-rate baseline comparison, graph clustering,
AML-style edge correlation — remains valuable as a second layer, per the
earlier discussion, but this is the primary defense).

### Part C: a seller must already have collateral locked before a buyer can buy coverage on them — this is the fix for "what if the seller's wallet is empty"

**Decision**: buyers can only purchase hedge coverage on a seller who
already has a minimum bond locked in `BondPool`. No locked collateral,
no hedge product available for that seller — full stop. A seller
reaches eligibility one of two ways:

1. **An explicit upfront deposit** — immediate eligibility, real
   capital committed.
2. **Gradual accumulation** — a small percentage of the seller's own
   job payments locks automatically over time (the job-funding-levy
   mechanism raised earlier), no upfront cost, but no eligibility until
   a minimum threshold is crossed.

**Why this was a real, not cosmetic, gap**: "slash the seller's bond"
is meaningless unless the seller already has money sitting in a
contract, locked, before anything goes wrong — this is the identical
principle behind Ethereum's own validator slashing (you cannot slash a
validator who never staked) and DeFi over-collateralized lending (you
cannot liquidate collateral that was never posted). A brand-new seller
with zero job history has zero locked collateral, and is therefore
correctly **not** hedge-eligible yet — this is a feature, not a bug,
and it's the same principle as ADR-006's tenure gate, just applied to
capital instead of reputation.

**Direct consequence**: a slash can never exceed what's actually locked
— capped at the seller's current balance, full stop. Which means **the
maximum job size a buyer can safely hedge with a given seller should be
bounded by that seller's currently locked collateral**, reusing
ADR-007's value-scaling principle in a new context: a seller with $150
locked shouldn't be sellable as hedge-eligible for a $10,000 job, since
even a full slash couldn't back a meaningful restitution.

**Revisit if**: real usage shows the minimum-collateral threshold is set
too high (locking out sellers who'd otherwise participate) or too low
(providing coverage that isn't credible) — a tuning question for real
data, the same discipline held throughout this document.

## ADR-014: Premium and slash pricing formulas — reusing existing risk
signals, not inventing new infrastructure

**Correction, stated directly**: the dollar figures used in the worked
examples discussing scenario spectra earlier were illustrative color for
exposition, not a designed formula — there was no actual sizing logic
behind them, which a direct question correctly exposed. This ADR is
the actual designed formula.

**Decision — premium**: priced using the standard actuarial shape,
**expected loss plus a margin**, where expected loss = probability of a
valid claim × the job's value (severity). Both halves reuse signals
already computed elsewhere in this design, not new inputs:
- *Probability* comes from the seller's existing risk profile — ADR-006
  tenure, ADR-010B genuine-activity, and prior dispute/slash history. A
  long-tenured, never-disputed seller prices lower than a new or
  previously-slashed one.
- *Severity* is simply the job's own declared value.

This directly resolves the open item already flagged in `docs/IDEA.md`
§7.4 ("premiums must exceed expected payout, once dispute-rate data
exists") — same question, now given an actual shape rather than left as
a placeholder.

**Decision — slash amount**: `slash = job value × base penalty rate ×
confidence multiplier`, capped at the seller's currently locked
collateral (ADR-013 Part C). The confidence multiplier is the corrected
piece: it should NOT be set by which tier caught the violation (tier
reflects how truth was established, not how severe the violation was).
Instead:
- Tier 0/1 objective evidence → full confidence multiplier — code-
  verified, no ambiguity.
- Tier 2/3 discretionary → derived from the **actual committee vote
  margin** (a 5-0 unanimous verdict earns a fuller multiplier than a
  narrow 3-2 one). This isn't new infrastructure — ADR-009 already
  assumes jurors produce confidence-style, not purely binary, outputs;
  this is a new use of a signal that already exists as a byproduct of
  the mesh.

**Decision — repeat offenders**: the base penalty rate should escalate
for a seller with prior slash history, reusing the same dispute-history
data already tracked, rather than a flat rate applied identically to a
first-time and a repeat violation — the same principle real insurers use
raising premiums or denying renewal after repeat claims.

**Revisit if**: real dispute data shows the actuarial formula's
probability inputs don't actually predict claim rates well, or the
confidence-multiplier mapping from vote margin needs recalibration —
exactly the kind of tuning question every other numeric threshold in
this document has been deliberately left open for, not guessed at here.

## ADR-015: Organizations as a collateral-holding layer above individual
agents — explicit, mutual-consent delegation, never inferred from payment

Prompted by the ratee/payee gap raised publicly on ERC-8004 issue #99
(`docs/erc8004-issue-99-followup.md`): a payTo/treasury address sitting
between many worker-agents and one payment address is routinely not the
agent that did the work. Extending that into our own design: a single
agent may act for more than one organization, and collateral settlement
has to resolve unambiguously to whichever one it was actually acting for
on a given job — never inferred, never left ambiguous.

**Decision**:

1. **Organization is a first-class identity, not a payment address.**
   It can post its own locked collateral in BondPool — the same
   mechanism ADR-013 Part C already established for an individual
   seller — and covers the agents delegated under it instead of (or
   alongside) their own individually-posted collateral.
2. **Membership requires mutual signed consent, never unilateral in
   either direction.** An organization becomes accountable for an
   agent's work, and an agent becomes covered by an organization's
   collateral, only when *both* sides sign a delegation record: the
   org's controlling key signs "I authorize agent Y," the agent signs
   "I consent to act under organization X's collateral, for [scope]."
   An org can't borrow a reputable agent's credibility by claiming them
   without consent; an agent can't claim a deep-pocketed org's
   collateral backs it without that org's actual sign-off.
3. **Delegation is scoped, not blanket** — a time window, optionally
   category/amount limits, the same policy-controlled pattern Circle's
   own Agent Wallets already use for spending rules, applied here to
   accountability instead of spend. A standing delegation, not a
   per-job signature — practical at real transaction volume, the same
   tradeoff every session/policy model elsewhere in this stack makes.
4. **Every job carries an explicit, checkable organization
   attribution, fixed at hiring — never a later, separate claim.** The
   buyer hires the organization (or an agent-under-that-organization
   listing) directly; the job's own creation names the organization,
   which only succeeds if a real, currently-valid, in-scope delegation
   already exists — checked the same way an agent's own signature
   already is (ERC-1271). An agent belonging to several organizations
   never gets to declare which one after the fact.
5. **Collateral settlement resolves strictly to the named, verified
   organization — never split, never guessed.** An unverified or
   out-of-scope claim is rejected outright; the job falls back to
   whatever the agent has posted under its own individual identity, if
   any — exactly as if no organization were involved. No fallback
   silently splits or guesses liability across an agent's several
   organizations.
6. **This has to be checkable before a buyer pays, not only at dispute
   time.** The same Discover-step lookup that already checks a seller's
   collateral and dispute history needs to be able to check "is this
   agent currently, validly delegated by the organization it claims" —
   otherwise a buyer could rely on coverage that turns out, at dispute
   time, to have never actually existed.

**Why**: the same standing principle that governs every other identity
claim in this design — ADR-013 Part A already established that fund
release is governed by code, never a direct call from any single
party — applies equally here: *who is accountable* for a job must be a
checkable fact, never an inference from payment routing or a bare
assertion. The mutual-consent requirement mirrors the same
anti-unilateral-claim logic ADR-011's advertise-and-volunteer model
already uses for jurors (nobody is bound without their own explicit
action) — extended here to organizational accountability instead of
committee selection.

**Corrected after direct challenge**: the first pass of this ADR
treated per-job organization attribution as something the *agent*
declares and we verify after the fact — and named a gaming vector
around an agent picking whichever attribution suited it. That framing
was solving a harder problem than the one that actually exists.
Simpler and correct: **a buyer hires the organization, not an agent
that separately self-reports one** — the org (or a specific
agent-under-that-org listing) is the counterparty named at the moment a
job is created, with the delegation already in place before hiring is
even possible. There's no separate attribution claim for anyone to
fake, because the org was who got hired. Liability follows hiring
directly: whichever agent the org internally assigns to do the work,
the org bears the reputation credit and the collateral cost of the
outcome — the same way a client's relationship is with a consulting
firm, not individually with whichever staff member the firm assigns.

**The narrower question this leaves — org misattributing which of its
own agents did the work, for internal reputation-padding purposes —
is already closed by infrastructure that exists.** The evidence ledger
already requires a real ERC-1271 signature from the specific identity
producing a submission (`ledger/auth.py`); that signature is
authoritative for who actually did the work regardless of what an org
claims. An org can't inflate one internal agent's record by
misattributing another's work to it — the signer is the signer.

**Reputation stays as two separate, non-overlapping scores, not a
hybrid** — deliberately simpler than a per-org-segmented agent score,
which would reintroduce a cold-start problem (ADR-006) for every new
agent/org pairing without adding anything the org-liability model
needs:

1. **Agent-level reputation** — unchanged, exactly ADR-004/006 as
   already designed: one portable, global score per agent, built from
   everything it's done, independent of organization.
2. **Organization-level reputation** — new: an aggregate over every job
   completed under that organization's collateral, computed by reusing
   the same diversity-weighted aggregation machinery already built for
   agent reputation (ADR-004), not new math. This is what a buyer
   hiring an organization for a complex, multi-agent task actually
   needs to see — the org's own track record for staffing the right
   agents and standing behind the outcome, not a blend of its members'
   individual scores.

**This also makes organization-hiring a first-class capability, not
just a collateral-plumbing detail**: a buyer can hire an individual
agent directly, or hire an organization for a task the organization
internally decomposes across its own member agents — the organization
is responsible for assigning capable agents and bears the reputation
and collateral consequences either way, the same division of labor
real consulting/staffing firms already operate under.

**Open question, not resolved here**: whether Organization should be
its own ERC-8004 `agentId` (reusing IdentityRegistry, consistent with
ADR-002's "build on what's already there" principle — an organization
genuinely does have identity, reputation, and now collateral, all
things ERC-8004 already models) or a new, parallel registry. Leaning
toward reusing IdentityRegistry; needs a real design pass before this
extends Epic G, not decided by default here.

**Revisit if**: real usage shows scoped delegation (time/amount/category
limits) is either too rigid (constant re-issuing for normal ongoing
work) or too loose (limits wide enough the scope check does no real
work) — the principle (explicit, mutual, checkable, frozen at job
start) is fixed; the exact scope shape is a tuning question for real
data, the same discipline as every other threshold in this document.

## ADR-016: Identity anchors accountability, not payment destination — generalizing the individual-agent case of the ratee/payee gap

**Decision**: reputation and collateral attribution key exclusively off
an agent's (or Organization's, per ADR-015) registered ERC-8004
identity — `agentId`/`agentWallet`, fixed once at registration. The
wallet address that actually receives payment for any given job
(`payTo`) is a separate, mutable, per-job routing detail and has no
bearing on reputation or collateral attribution, ever. Discover-step
lookups, collateral locking, feedback aggregation, and dispute
resolution all read `agentId` (or organization identity); none of them
read, store, or depend on a payment destination.

**Why**: ADR-015 already established this at the organization level —
"a payTo/treasury address sitting between many worker-agents and one
payment address is routinely not the agent that did the work." The same
gap exists one level down, at a single, non-organizational agent's own
registration: a buyer looks up and a dispute attaches to `agentWallet`,
not to wherever a specific job's payment happened to land. Payment
routing legitimately varies for entirely benign reasons — a different
hirer, an escrow intermediary, a wallet chosen purely for custody
convenience — and tying attribution to it would mean reputation and
collateral silently break on ordinary operational changes, while also
leaving open a laundering vector: an operator could let one identity
carry the reputation and collateral exposure while directing all actual
proceeds to an entirely separate, unaccountable wallet. Keying
attribution to the immutable registered identity instead closes both
problems the same way.

**Confirms, in our own infrastructure, exactly the gap raised publicly**
on ERC-8004 issue #99 (`docs/erc8004-issue-99-followup.md`) and observed
concretely during our own MVP self-registration
(`docs/erc8004-mvp-verification.md`'s "Known ratee/payee split" note):
the wallet used to register the lookup service
(`0xFC414bE58228fe5dBe961B74225548D29b8abeFA`, CDP-managed, the only one
this process can sign for) is deliberately different from the wallet
used as `X402_PAY_TO_ADDRESS` (user-held). That split is safe under this
ADR precisely because nothing here — nor should it — ever attributes
reputation or collateral based on `payTo`.

**Revisit if**: a future mechanism (e.g. an escrow or automated payout
path) needs to verify a specific payment actually originated from, or
was authorized by, the registered identity's controller — that's a
narrower, legitimate fraud/spoofing check on the payment leg itself, and
would be a separate verification, not a reason to fold payment
destination into the reputation/collateral attribution model.
