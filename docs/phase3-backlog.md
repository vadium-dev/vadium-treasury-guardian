# Phase 3 Backlog — Trust & Verification Layer

User stories grouped by epic, staged across three milestones, mirroring
how Phase 2's backlog is organized. **Resequenced 2026-09-20**: an
end-to-end pass found that Epic G (seller collateral) was written and
tagged as if it only gated Epic D, when in fact Epic C's automatic
slashing is equally dependent on it — `slashObjective()` has nothing to
draw from without G1's locked-collateral ledger existing first, and
without G7's anti-fraud payout rule, Milestone 3.0's "automatic"
slashing would ship with the same self-dealing vulnerability ADR-013 was
written to close. Epic G's core (G1–G4, G7) is now split out to
Milestone 3.0 and the epic is physically relocated to sit right after
Epic A — see Epic G's own header for the resulting shape.

- **3.0** — registration (Epic A), the seller-collateral core that makes
  slashing mean something (Epic G's 3.0-tagged stories), reputation
  lookup (Epic B), and the *objective* dispute path (Epic C, Tier 0/1,
  automatic slashing with the anti-fraud payout rule already in force).
  No committee, no discretionary payouts, no buyer-purchased premium
  product yet — the lowest-liability slice that's still a real,
  fraud-resistant product, not a stub that happens to demo well.
- **3.1** — the committee mechanism and Tier 2/3 discretionary disputes
  (Epic D), the buyer-purchased hedge premium and actuarial pricing
  (Epic G's remaining stories), acting as ERC-8183 evaluator (Epic
  E2, which genuinely needs Epic D to exist first — E1 does not, see
  Epic E), and organizations as a collateral-holding layer above
  individual agents (Epic H, ADR-015 — gated on Epic G's collateral
  core, since an organization posts collateral the identical way a
  seller does). Gated on ADR-003's incentive design and real legal
  counsel review of ADR-001, ADR-013, **and now ADR-015** (`docs/IDEA.md`
  §7.2, §8, and §9) — organizational liability for a member agent's
  conduct is its own real legal question, not a footnote to ADR-013's.
  ADR-013 is where ADR-001's structural principle becomes a concrete
  contract design; it's the one a lawyer needs to see in full, not
  ADR-001 in isolation.
- **3.2** — TEE attestation integration (buy, don't build — evaluate a
  real provider), bond-discount economics tuned from real dispute data,
  and the rare-path refinements (repeat-offender penalty escalation, the
  reserve-arbiter and reduced-committee escalation tiers, the covert
  honeypot accelerant) that all explicitly need real usage history to be
  worth building at all.

Priorities: P0 = required for the milestone to be meaningful, P1 = fast
follow, P2 = can slip.

## Epic A — Seller registration & identity

**A1. As a seller, I want to register my agent's identity on ERC-8004
once, so my reputation and bond are tied to a standard identity other
tools can also read, not a proprietary one only we recognize.** *(3.0, P0)*
- Calling the registration service for a wallet with no existing
  `agentId` results in a real `IdentityRegistry.register()` call and a
  returned `agentId`.
- Calling it again for the same wallet does not re-register — idempotent,
  same principle as Phase 2's `poll_spend.py` and epoch sealing.

**A2. As a seller with existing Phase 2 evidence (an anchored operation
history), I want that reflected in a lower bond quote, so adopting the
free instrumentation layer has a direct financial payoff, not just a
compliance argument.** *(3.0, P0)*
- A registration request for an identity with ≥1 anchored Phase 2 epoch
  returns a quote below the standard baseline.
- A registration request for an identity with a valid TEE attestation on
  file returns a quote below even the Phase-2-only discount — attestation
  is stronger evidence than telemetry alone (per the mesh's Tier 0
  design).

**A3. As a seller, I want to deposit my bond directly into `BondPool`
myself, so custody never passes through us even momentarily.** *(3.0, P0)*
- The bond deposit is a direct on-chain call from the seller's own
  wallet to `BondPool` — no step where we hold funds, even transiently.

## Epic G — Seller collateral (core here, 3.0; hedge pricing, 3.1)

Positioned right after Epic A, not after Epic F, because both Epic C
*and* Epic D depend on it — not Epic D alone, as earlier drafts of this
backlog implied. `slashObjective()` (Epic C) and `recordCommitteeVerdict()`
(Epic D) are both no-ops without a locked-collateral ledger to draw
from, and both need the same anti-fraud payout rule regardless of which
tier established the verdict. The stories below are split by which
milestone actually needs them, not grouped as one undifferentiated unit:

**G1. As `BondPool`, I want a per-seller locked-collateral balance, so a
slash instruction always has a real, checkable amount to draw from
instead of an undefined one.** *(3.0, P0, ADR-013 Part C — required for
Epic C's slashing to be real, not just Epic D's)*
- A seller with no locked balance and a seller with a locked balance are
  distinguishable in a single query — no implicit zero.

**G2. As a seller, I want to lock a minimum bond either as an explicit
deposit or gradually via a percentage of my own job payments, so I have
two real paths to eligibility instead of one forced upfront cost.**
*(3.0, P0, ADR-013 Part C)*
- An explicit deposit crosses the eligibility threshold immediately.
- Accumulated levy contributions cross it only once the running total
  reaches the same threshold — no separate, lower bar for the slow path.

**G3. As the objective/discretionary dispute path, I want to reject
slashing a seller with no locked collateral, with a clear reason, so
"the seller's wallet is empty" can never silently produce an unfunded
payout at either tier.** *(3.0, P0, ADR-013 Part C — the direct fix for
the gap that originally prompted this epic; applies to Epic C from day
one, not only once Epic D exists)*
- A dispute resolving against a sub-threshold seller returns an explicit
  ineligibility reason for payout, not a silently-attempted transfer
  from nothing.

**G4. As `BondPool`, I want any payout to a disputing buyer capped at
exactly what that buyer paid for the disputed job, with any slash
beyond that restitution routed to the shared pool rather than to the
buyer, so self-dealing between a colluding buyer and seller cannot
extract more than they put in — at either tier.** *(3.0, P0, ADR-013
Part B — this is the core anti-fraud rule and belongs in Milestone 3.0:
Epic C's automatic slashing is exploitable by the exact same
buyer=seller collusion attack ADR-013 was written against, and it needs
this protection from its first release, not starting at 3.1)*
- A dispute payout to the buyer never exceeds what that buyer paid for
  the disputed job, verified by an adversarial test using a buyer=seller
  self-dealing scenario against Epic C's objective path specifically,
  not only against Epic D's committee path.
- Excess slash beyond that restitution is verified to land in the
  shared pool, never in the disputing buyer's wallet.

**G5. As a buyer, I want to purchase an explicit hedge premium on a
specific transaction, with the maximum hedgeable job value capped by
the seller's currently locked collateral, so I can buy protection the
seller's own collateral could actually back.** *(3.1, P0, ADR-013 Part
C — this is the buyer-purchased premium *product*, genuinely a 3.1
feature since Milestone 3.0's Epic C provides automatic seller-funded
protection without requiring a separate buyer purchase at all)*
- A hedge-purchase request whose job value would require a slash
  exceeding the seller's locked balance is rejected or capped, not
  silently accepted at face value.

**G6. As the pricing engine, I want to price the hedge premium as
expected loss plus a margin, using the seller's existing
tenure/genuine-activity/dispute-history signals for probability and job
value for severity, so premiums aren't guessed at per transaction.**
*(3.1, P1, ADR-014)*
- Two sellers with identical job value but different risk histories
  receive different premium quotes — verified by comparing quotes for a
  long-tenured, undisputed seller against a newer or previously-slashed
  one.
- The premium paid is never refunded under any resolution outcome —
  verified across both an upheld and a rejected dispute. (This
  acceptance criterion only applies once G5's premium product exists;
  Milestone 3.0's Epic C has no premium to refund or withhold in the
  first place.)

**G7. As `BondPool`, I want a slash amount computed as job value × base
rate × a confidence multiplier, so the penalty reflects actual certainty
rather than which tier caught the violation.** *(3.1, P1, ADR-014 — a
flat, un-weighted rate is an acceptable Milestone 3.0 placeholder for
G4's core payout-capping rule; this story is the confidence-weighted
refinement)*
- Tier 0/1 violations use a fixed full-confidence multiplier.
- Tier 2/3 violations derive their multiplier from the real committee
  vote margin — verified by comparing the computed slash for a
  unanimous verdict against a narrow-majority verdict on an otherwise
  identical case.

**G8. As the pricing engine, I want a seller's base penalty rate to
escalate after a prior slash, so a repeat offender faces a stricter
penalty than a first-time one.** *(3.2, P2, ADR-014 — genuinely needs at
least one real prior violation on record to be meaningful, so it can't
usefully ship before real dispute history exists)*
- A seller with one prior slash on record receives a higher computed
  slash rate on a second violation than an otherwise-identical seller
  with no prior history.

## Epic B — Reputation lookup (the paid product surface)

**B1. As a buyer agent, I want to pay a small nanopayment and get a
seller's reputation score before I pay them, so I can avoid an
unverified counterparty.** *(3.0, P0)*
- `GET /reputation/{agent_identity}` is x402-payable and returns a score
  plus links to underlying evidence (ERC-8004 feedback entries, bond
  status, dispute history).
- A lookup for an identity with zero history returns an explicit
  "no reputation data" result, not an error or a fabricated neutral score.

**B2. As a buyer agent, I want the score to be resistant to a seller
buying fake positive feedback from colluding accounts, so the number I'm
paying for is actually meaningful.** *(3.0, P0, see ADR-004)*
- The aggregation function weights by distinct attester identity
  (inverse-Simpson or equivalent), not a raw count — verified by a test
  that N pieces of feedback from 1 colluding identity score materially
  lower than N pieces from N distinct identities.

**B3. As us, I want to list this endpoint on the Agent Marketplace and
the x402 Bazaar, so buyer agents can discover it the way they discover
any other paid service.** *(3.0, P1, mechanics per `docs/IDEA.md` §5/§6)*
- A Marketplace submission is filed.
- The endpoint's route carries a valid `extensions.bazaar` block and is
  confirmed cataloged by the facilitator (not just submitted — per the
  caveat in `docs/IDEA.md` §5 that facilitator validation can silently
  fail).

## Epic C — Objective dispute path (Tier 0/1, automatic)

Depends on Epic G's 3.0-tagged stories (G1–G4), not just Epic A — a
dependency the earlier draft of this backlog never stated. `slashObjective()`
(C3) has nothing to draw from without G1's locked-collateral ledger, and
without G4's payout cap, C4's "automatic payout" is exploitable by the
same buyer=seller self-dealing attack ADR-013 was written against. Build
Epic G before this epic, not after it.

**C1. As a buyer, I want to file a dispute against a specific
transaction, so a bad transaction has recourse where none existed under
plain x402.** *(3.0, P0)*
- `file_dispute(seller_identity, buyer_wallet, tx_reference,
  evidence_ref=None)` creates a `disputes` row in `pending` state.
- `evidence_ref` is optional — filing a dispute doesn't require
  disclosing content, consistent with Phase 2 ADR-007's redaction
  principle carried into this phase.

**C2. As the verification mesh, I want to check Tier 0/1 evidence
automatically on a filed dispute, so an objectively-provable failure
(schema mismatch, failed TEE attestation, duplicate-output hash) doesn't
need human or committee involvement.** *(3.0, P0)*
- A dispute whose `tx_reference` maps to a Phase 2 operation with a
  schema violation or duplicate-hash match resolves to `upheld, tier 0/1`
  without reaching Epic D.
- A dispute with no Tier 0/1 signal is marked for escalation, not
  silently closed.

**C3. As `BondPool`, I want `slashObjective()` callable only with
Tier 0/1 evidence attached, against a seller with a locked balance per
G1, so the automatic path can never be used to justify a discretionary
judgment call or slash a balance that was never designed to exist.**
*(3.0, P0, see ADR-001 and G1)*
- `slashObjective()`'s on-chain logic checks the evidence type tag, not
  just that *some* evidence hash was provided — a Tier 2/3 verdict cannot
  be submitted through this function even if someone tries.
- Calling it against a seller with no locked collateral fails per G3, not
  silently succeeds against nothing.

**C4. As a buyer with an upheld objective dispute, I want automatic
payout from the seller's bond, capped at G4's restitution rule, so
recourse doesn't require waiting on a committee for the clear-cut cases —
and so this automatic path can't be exploited by the same self-dealing
attack a discretionary payout could be.** *(3.0, P0, see G4)*
- An `upheld, tier 0/1` dispute results in a bond transfer to the buyer
  wallet without any additional off-chain approval step.
- The transfer never exceeds what the buyer paid for the disputed job,
  and any additional slash lands in the shared pool, not the buyer's
  wallet — verified by the same adversarial buyer=seller test G4
  requires, run against this objective path specifically.

## Epic D — Discretionary dispute path (Tier 2/3, committee) — Milestone 3.1

**Sequencing decision (2026-09-19): build the full mechanism** —
ADR-006 through ADR-014 in `docs/phase3-design-decisions.md`
(tenure/breadth gate, pool-relative and value-scaled eligibility,
longitudinal collusion detection, evergreen calibration-track onboarding,
relationship-conflict and breadth-vs-depth fixes, advertise-and-volunteer
selection, the volunteer-shortfall escalation ladder, and the BondPool
custody/unprofitability/collateral-prerequisite/pricing corrections),
not a simplified version — as the project's primary market
defensibility: the mechanism's code is necessarily auditable (Epic F1)
and therefore copyable, but the accumulated calibration/tenure/
collusion-clean track record it produces is not. Epic G's 3.0-tagged
core (G1–G4) already exists by the time this epic starts, built right
after Epic A — what this epic additionally depends on is Epic G's
3.1-tagged remainder (G5–G7): the buyer-purchased premium product and
its actuarial pricing, without which this epic's discretionary payouts
have no real buyer-paid coverage to sell, only the seller-funded
automatic protection Epic C already provides.

That's four ADRs with real dependencies between them, not four
independent features — the sub-epics below (D.1 → D.4) sequence the
build in the order those dependencies actually require, not the order
the ADRs were written in. D.1's two tracks can build in parallel; D.2
depends on both finishing; D.3 depends on D.2 running long enough to
accumulate real selection/voting history; D.4 closes the whole epic.

### D.1 — Raw signal infrastructure (two parallel tracks, no shared dependency)

**D1a. As the eligibility system, I want tenure, genuine-activity, and
topic-relevance computed directly from the Phase 2 ledger for any
wallet, so eligibility has a real, checkable signal from day one — and
so a genuine specialist isn't penalized for lacking breadth outside
their specialty.** *(3.1, P0, ADR-006 as corrected by ADR-010 Part B)*
- Given a wallet with anchored Phase 2 operations, a query returns its
  real age (days since first anchored epoch), a genuine-activity measure
  (real transaction value and distinct paying counterparties from paid
  x402/Marketplace activity — not raw operation-type variety), and a
  topic-relevance score for any given dispute category (satisfied by
  either broad coverage or deep, substantial history in that specific
  category).
- A wallet with no anchored history returns an explicit "ineligible, no
  history" result, not a zero score treated as eligible-but-weak.

**D1b. As a new candidate arbiter, I want to take an evergreen
calibration exam at any time and receive a scored result, so I don't
need months of real dispute history to start building trust.**
*(3.1, P0, ADR-009)*
- A candidate can request and complete calibration tasks of increasing
  ambiguity at any time after this ships — not only during some initial
  launch window.
- A completed calibration run produces a Brier-score-based (or
  ELO-style) result, not raw percent-correct.
- The same exam and scoring function are used for a candidate joining on
  day one and a candidate joining a year later — verified by a test that
  compares the two paths produce identically-computed scores for
  identical performance.

**D1c. As `BondPool`, I want the objective/discretionary structural
split deployed and estimated before any real bond money touches it, so
the core legal claim of ADR-001 exists in code before it's relied
on.** *(3.1, P0, ADR-001, same estimate-before-commit discipline as
`AnchorLog`'s deployment in Phase 2)*
- `slashObjective()` and `recordCommitteeVerdict()` exist as separate
  entry points on a deployed (testnet first) contract.
- Deployment follows the same estimate-then-commit sequence already
  proven for `AnchorLog` — `--estimate` succeeds before a real deploy is
  attempted.

### D.2 — Eligibility, selection, and voting (depends on all of D.1)

**D2a. As the eligibility system, I want to combine D1a's tenure,
genuine-activity, and topic-relevance signals with D1b's calibration
score into one pool-relative eligibility rank, floored by an absolute
minimum and scaled by the dispute's value, so neither signal alone
determines who's trusted with which size of dispute.** *(3.1, P0,
ADR-007, using the corrected breadth split from ADR-010 Part B — not
the original ADR-006 topic-variety metric)*
- A candidate's percentile rank is computed against the *current*
  eligible pool at query time, not a fixed historical snapshot.
- A candidate below the absolute floor is ineligible regardless of
  percentile rank, even in a thin pool.
- A candidate with deep, substantial real history in only the dispute's
  own category scores at least as well on topic-relevance as a shallow
  generalist with the same overall activity level — verified by a test
  comparing a synthetic "specialist" profile against a synthetic
  "generalist" profile of equal genuine-activity level.
- A higher-value dispute produces a stricter eligibility bar than a
  lower-value one, verified by comparing the computed threshold across
  two disputes of different declared value.

**D2b. As the selection mechanism, I want to advertise a dispute to its
already-eligible, non-conflicted candidate pool, let interested
candidates volunteer, and then draw the committee at random from
volunteers only — not force a blind draw across the whole eligible pool
regardless of interest.** *(3.1, P0, ADR-011 Part A — supersedes the
original blind-draw design; sets up D.3's baseline)*
- The advertisement reaches only candidates who already pass D2a's
  eligibility and D2b's (this story's) recusal check for this specific
  dispute — not a universal broadcast.
- The final committee is a random draw from the set of volunteers within
  the response window, not "first N to respond" and not "every
  volunteer serves."
- The selection function's inputs and randomness source are public and
  independently recomputable — the same "detected via public inputs,
  not asserted" standard `docs/phase2-architecture.md` already holds
  Merkle verification to.
- If volunteer count falls short of the needed committee size, escalation
  proceeds through D2g-D2j below, in order — never silently seating an
  undersized or under-qualified committee, and never skipping a tier.

**D2g. As the selection mechanism, I want to extend the response window
and raise the advertised fee before trying anything else, so a pricing-
driven shortfall is fixed cheaply without weakening eligibility or
committee strength.** *(3.1, P1, ADR-012 tier 1)*
- The fee increase is carved from the disputed bond, capped at a defined
  ceiling relative to the bond's total value — verified by a test
  confirming the fee can never exceed that ceiling regardless of how
  many escalation rounds fire.
- Re-advertisement targets the same eligible, non-conflicted pool as the
  original attempt, not a broadened one.

**D2h. As the selection mechanism, I want to broaden eligibility by one
defined step only after D2g has failed to fill the committee, so a
genuine population shortfall (not a pricing one) still gets a committee,
without lowering standards further than necessary.** *(3.1, P1, ADR-012
tier 2)*
- Eligibility broadening has a hard floor — verified by a test that
  repeated failed attempts on the same dispute never push the bar below
  that floor.
- This tier only fires after D2g has been tried and failed, not in
  parallel with it or instead of it.

**D2i. As the selection mechanism, I want a small pool of pre-committed
reserve arbiters available as a last resort when D2g and D2h both fail,
so a committee can still be formed without reverting to a standing
"hired arbiter" model as the default.** *(3.2, P2, ADR-012 tier 3 —
deliberately low priority, since it should be rare)*
- Reserve arbiters are compensated by a treasury-funded retainer, not
  the per-dispute bond-funded fee (D2e) — distinct funding source,
  verified by checking the payment doesn't draw from `BondPool`.
- This tier only fires after both D2g and D2h have been attempted.

**D2j. As the selection mechanism, I want to seat a reduced-size
committee under a stricter approval threshold, restricted to disputes
below a defined value ceiling, as the true last resort when D2g-D2i all
fail.** *(3.2, P2, ADR-012 tier 4 — the least good option, scoped tightly
on purpose)*
- This path is unavailable for any dispute above the defined value
  ceiling — verified by a test confirming a high-value dispute cannot
  reach this tier even if D2g-D2i all fail for it.
- The approval threshold for a reduced committee is stricter than the
  standard threshold (e.g. unanimous vs. majority) — verified by
  comparing the two threshold values directly.

**D2k. As the eligibility system, I want to track how often escalation
(D2g-D2j) fires for disputes involving a specific seller or category,
relative to the rest of the marketplace, so a seller whose disputes
suspiciously and repeatedly trigger escalation is itself surfaced as an
anomaly.** *(3.2, P2, ADR-012's own anti-gaming check — the same
"compare to a baseline" principle as ADR-008/D3a, applied to usage of
the escalation ladder itself)*
- A seller's escalation-trigger rate is compared against the
  marketplace-wide baseline rate, not treated as inherently suspicious
  in isolation.

**D2b'. As the selection mechanism, I want to exclude any candidate with
a direct prior transactional relationship to either disputing party
before they're ever drawn, so an obvious conflict of interest is caught
immediately rather than relying only on a slow, data-hungry statistical
signal to catch it eventually.** *(3.1, P0, ADR-010 Part A — a basic
integrity check, not an optional refinement; this is checkable from day
one, with zero accumulated history required, unlike D3d below)*
- A candidate with any recorded payment/service relationship (either
  direction) to either disputing party, found in Phase 2 ledger or
  on-chain payment history, is excluded from that dispute's draw.
- This check runs before D2a's eligibility scoring, not after — an
  excluded candidate never enters the ranked pool for this dispute.

**D2c. As a committee member, I want to vote on an escalated dispute
independently, so my vote isn't influenced by seeing other members'
votes first.** *(3.1, P0)*
- Votes are recorded without a member being able to read other members'
  votes before submitting their own (commit-then-reveal, or equivalent —
  exact mechanism is one of the open risks in the architecture doc).

**D2d. As the verification mesh, I want to run a Tier 2 LLM judge on an
escalated dispute and log its score as one input, never the verdict
itself, so no single model's judgment can trigger a payout alone.**
*(3.1, P0, see ADR-001 and the UMA accuracy data in `docs/IDEA.md` §5)*
- A Tier 2 evaluation writes a score + rationale to the dispute record.
- No code path allows a Tier 2 score alone to call `BondPool` — this must
  be enforced structurally (Epic F1 below), not just by not writing that
  code path today.

**D2e. As a committee member, I want to be compensated from the disputed
bond for participating, so the incentive to vote honestly doesn't depend
on us paying a salary.** *(3.1, P0, see ADR-003)*
- A resolved dispute's payout calculation carves out a defined fee
  distributed among voting committee members before the remainder goes
  to the buyer/seller outcome.
- A separate, smaller incentive path exists for D1b's calibration
  exercises and D3g's honeypot participation, funded from a team/
  treasury allocation, not from any disputed bond — resolved per ADR-011
  Part C, no longer an open question.

**D2f. As `BondPool`, I want `recordCommitteeVerdict()` to only release
funds once a defined multi-party threshold is met, so no single
party — including us — can trigger a discretionary payout alone.**
*(3.1, P0, the core structural claim of ADR-001)*
- Calling this function with votes from fewer than the threshold number
  of distinct committee members does not move funds.
- This is checked with an adversarial test: a single actor controlling
  one identity (even an identity we operate) cannot satisfy the
  threshold alone.

### D.3 — Longitudinal collusion detection (depends on D.2 running long enough to accumulate real selection/voting history)

**D3a. As the eligibility system, I want to track how often each pair of
committee wallets is selected together, relative to what fair random
selection would predict, so overrepresentation is visible even before
any vote is examined.** *(3.1, P1 — genuinely needs D.2's real selection
history to exist first, not buildable as a day-one feature; ADR-008)*
- A pair's observed co-selection rate is compared against the
  expected rate implied by D2b's selection algorithm and pool size.
- No adjustment applies until a minimum number of joint appearances has
  been observed — enforced explicitly, not left as an implicit
  assumption, per ADR-008's own stated false-positive risk.

**D3b. As the eligibility system, I want to measure how often a pair
agrees beyond what their individual accuracy would predict, weighted
more when it holds across different dispute topics, so genuine
competence isn't mistaken for collusion.** *(3.1, P1, ADR-008)*
- The computed "excess agreement" for two independently-accurate honest
  jurors is verified (via simulation or historical replay) to sit near
  zero, not falsely flagged.
- Excess agreement observed across ≥2 distinct topic categories scores
  higher than the same raw agreement rate confined to one category.

**D3c. As the selection mechanism, I want a flagged pair's future
joint-selection probability and combined vote weight both reduced
gradually, through a function anyone can recompute from public data, so
the adjustment itself can never become a new form of single-party
discretion.** *(3.1, P0 — this is the constraint ADR-008 states is
non-negotiable, not an optional refinement)*
- The adjustment applied to any flagged pair is reproducible by a third
  party from public selection/voting history alone.
- No manual override path exists that bypasses this computed adjustment.

**D3d. As the eligibility system, I want to track whether a specific
juror's rulings correlate, above baseline, with favoring a specific
seller or buyer across many disputes over time, so subtler bias or
off-chain collusion is caught even when D2b' finds no direct
relationship on record.** *(3.1, P1, ADR-010 Part A — the statistical
complement to D2b's real-time recusal check; genuinely needs real
dispute history to accumulate first, same dependency shape as D3a/D3b)*
- A juror's rate of ruling in favor of a specific counterparty is
  compared against that juror's own overall base rate, the same
  above-baseline principle as D3b, not raw favor-rate alone.
- No adjustment applies until a minimum number of disputes involving
  that juror-counterparty pairing has been observed, for the same
  false-positive reasons already governing D3a/D3b.

**D3e. As the eligibility system, I want to flag a single juror whose
votes diverge from the eventual committee majority more than their own
accuracy predicts, in a direction that consistently benefits one
counterparty, so a colluding actor is detectable without first having to
guess which other wallet they're colluding with.** *(3.1, P1, ADR-008
signal 3 — this is the primary sleeper-attacker defense, not the
honeypot mechanism in D3g, and is cheaper to compute than D3a/D3b's
pairwise search since it operates per-juror)*
- A juror's divergence-from-majority rate is compared against their own
  overall accuracy, the same above-baseline discipline as D3b/D3d.
- This check runs independent of D3a-D3d — it does not require a
  suspected partner to already be identified.

**D3f. As the eligibility system, I want to detect anomalously dense
clusters in the juror correlation graph, and in the economic-
counterparty graph behind D1a's genuine-activity signal, so a ring that
deliberately spreads coordination across 3+ identities to dodge pairwise
thresholds is still caught.** *(3.1, P2 — the most complex signal in
this epic, correctly sequenced last within D.3; ADR-008 signals 4-5)*
- A correlation graph over the eligible pool, weighted by D3a/D3b, is
  checked for clusters denser than the rest of the graph, using an
  established community-detection method, not an ad hoc threshold.
- The same clustering check runs against the economic-counterparty graph
  underlying D1a's genuine-activity signal — verified by a test showing
  a synthetic wash-trading ring (candidates transacting mostly with each
  other, not real external counterparties) is flagged even though no
  single pair's transaction volume alone looks suspicious.

**D3g. As the eligibility system, I want an unpredictable, covert
synthetic dispute occasionally injected into the real selection stream,
with a known correct answer, so collusion can be checked against direct
ground truth rather than only the honest-majority proxy D3e relies
on.** *(3.2, P2 — a secondary accelerant per ADR-008, not required for
D.3's core defense to function, and deliberately sequenced after the
signals that don't need it)*
- The synthetic dispute uses entirely synthetic disputing parties and a
  synthetic bond — no real party or real funds are ever involved.
- Injection timing is drawn from an unpredictable distribution, not a
  fixed interval — verified by confirming no fixed period or count
  pattern exists in the injection schedule.
- Resolution of a synthetic dispute is never disclosed as synthetic,
  including after the fact — checked as an explicit constraint on
  whatever surfaces dispute outcomes to participants.

### D.4 — Hardening and independent validation (closes the epic)

**D4a. As an auditor, I want to verify from `BondPool`'s code alone —
not from our word — that no single-party call can ever trigger a
discretionary payout, so ADR-001's central claim is checkable end to
end, including everything D.1-D.3 added on top of it.** *(3.1, P0,
Epic F1's own acceptance criterion, now covering the full mechanism)*
- Independently reviewed by real legal/security counsel, per
  `docs/IDEA.md` §7.2 — not just internally tested.

**D4b. As the project, I want ADR-007's value-scaling curve and
ADR-008's minimum-sample thresholds tuned against real pilot data before
wide rollout, so the mechanism's parameters reflect actual usage, not
launch-day guesses.** *(3.1/3.2 boundary, P1)*
- At least one real design-partner pilot's dispute/selection history is
  used to re-derive these thresholds, replacing the placeholder values
  used to ship D.1-D.3.

## Epic E — Acting as ERC-8004 validator / ERC-8183 evaluator

Documented here as one epic, but its two stories don't share a
milestone or a build-order position, worth being explicit about rather
than letting the shared header imply otherwise: **E1 is tagged 3.0 and
genuinely has no dependency beyond Epic A** — it could be built
immediately after registration, in parallel with Epic G/B/C, not
"whenever we get to Epic E" as its position in this document might
suggest. **E2 is tagged 3.1 and genuinely does depend on Epic D** — a
real evaluator decision needs the same tiered/committee backing a
direct dispute would. Kept as one epic here because both concern the
same pair of external roles, not because they share a build sequence.

**E1. As an ERC-8004 validator, I want to respond to
`validationRequest()` calls using our own verification-mesh output as
the basis, so our credibility in the standard builds through real,
checkable responses.** *(3.0, P1)*
- A `validationRequest()` addressed to our validator address produces a
  `validationResponse()` within a defined SLA, backed by an actual
  mesh evaluation, not a rubber stamp.

**E2. As the named evaluator on an ERC-8183 Job, I want to call
`complete()`/`reject()` based on verification-mesh output, so the
standard's own admitted gap (an evaluator's arbitrary discretion) is
answered with something checkable instead of nothing.** *(3.1, P1 —
gated on Epic D existing, since a real evaluator decision needs the
same tiered/committee backing a direct dispute would)*
- A Job where we're named `evaluator` resolves via the same
  Tier 0-3 pipeline as Epic C/D, not a separate, less accountable path
  just because the trigger was an ERC-8183 call instead of our own
  dispute endpoint.

## Epic F — Structural safeguards (cross-cutting, but tracked explicitly)

**F1. As an auditor, I want to verify from the contract code alone —
not from our word — that no single-party call can ever trigger a
discretionary payout, so ADR-001's central claim is checkable, not just
asserted.** *(3.1, P0)*
- `BondPool`'s source has exactly two payout-triggering entry points,
  and only one (`slashObjective`) requires no multi-party proof; the
  other (`recordCommitteeVerdict`'s associated release) is structurally
  incapable of executing under a single caller's signature.
- This is the one acceptance criterion in this entire backlog that
  should be independently verified by real legal/security counsel, not
  just by us — flagged again here deliberately, matching
  `docs/IDEA.md` §7.2's instruction to get that review in parallel with
  building, not after.

## Epic H — Organizations: a collateral-holding layer above individual agents (ADR-015)

Gated on Epic G's collateral core existing (an organization posts
collateral the identical way a seller does) and Epic A's identity
pattern. Legal review of ADR-015 rides alongside ADR-001/013's — see
the 3.1 milestone note above.

**H1. As an organization, I want to register with my own identity and
post my own locked collateral, so I can be hired for work my member
agents perform, the same way an individual seller is today.** *(3.1, P0)*
- Reuses `sellers`' exact bond-posting mechanism (ADR-013 Part C) against
  a new `organizations` row — same deposit/levy-accumulation paths, same
  "zero bond means not hedge-eligible" rule, no new collateral logic
  invented.

**H2. As an organization and an agent, we want to jointly sign a
delegation record before the agent is covered by the organization's
collateral, so neither of us can claim the relationship unilaterally.**
*(3.1, P0)*
- A `org_memberships` row is only valid with both the org's and the
  agent's signature present (ADR-015 Decision #2) — a row with only one
  signature is not a membership, full stop.
- The delegation carries a scope: a time window, and optionally a
  category or max-job-value ceiling (ADR-015 Decision #3) — not a
  blanket, permanent grant.

**H3. As a buyer, I want to hire an organization directly — not an
individual agent that separately claims to represent one — so the
liable party is fixed at the moment I hire, not asserted afterward.**
*(3.1, P0)*
- Job creation against an organization succeeds only if a real,
  currently-valid, in-scope `org_memberships` row exists for whichever
  agent the org assigns; otherwise it's rejected outright, never
  silently falls back to guessing (ADR-015 Decision #4/#5).
- The resulting job's `org_identity` is set once, at creation, and never
  edited afterward — same "freeze at job start" discipline Phase 2's
  evidence ledger already applies to leaf hashes.

**H4. As a buyer, I want to check whether an agent is currently, validly
delegated by the organization it's listed under *before* I pay, so I'm
never relying on coverage that turns out not to have existed.** *(3.1,
P0)*
- Extends the existing reputation-lookup surface (Epic B) with an
  org-delegation check, not a separate endpoint — one lookup, not two.

**H5. As a buyer evaluating an organization for a complex task, I want
to see the organization's own aggregate track record — not a blend of
its individual members' scores — so I can judge its ability to staff
and stand behind outcomes as a whole.** *(3.1, P1)*
- Computed by reusing ADR-004's existing diversity-weighted aggregation
  code path over every dispute/job carrying that `org_identity`, not a
  new aggregation method (ADR-015's "two separate scores" decision).
- An agent's own individual reputation (ADR-004/006) is unaffected and
  unsegmented by which organization, if any, it was acting under for a
  given job — one portable score per agent, same as before this epic.

**H6. As an organization, I want to revoke a member agent's delegation,
so I can stop being liable for an agent I no longer want to stand
behind.** *(3.1, P2)*
- Revocation stops new jobs from being created against that delegation;
  it does not retroactively change `org_identity` on jobs already
  created under it (same freeze-at-creation rule H3 already
  establishes) — a revoked agent's *past* work is still the org's
  recorded liability, only future hiring is cut off.

## Explicitly out of scope for Phase 3

- Multi-chain support — everything here assumes Arc, per Phase 2 ADR-004's
  same reasoning (one coherent trust stack, one chain).
- Building our own TEE infrastructure — Milestone 3.2 evaluates an
  existing provider (Phala/Marlin/Atoma); we do not run enclave hardware.
- A general-purpose insurance product beyond agent-to-agent transaction
  disputes — scope creep past what ADR-001's structuring even attempts to
  justify.
- Real-time/synchronous dispute resolution — Tier 2/3 disputes involve a
  committee vote; nothing here promises sub-second resolution the way
  Epic C's objective path can.
