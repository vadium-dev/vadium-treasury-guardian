# Draft comment for erc-8004/erc-8004-contracts#99

Target: https://github.com/erc-8004/erc-8004-contracts/issues/99
Status: DRAFT — not posted. Review before submitting.

---

The payment-proof grounding here is a real improvement and solves the
cheapest version of this problem — right now a Sybil reviewer costs
nothing to create, and tying `response`/`responseURI` to a signed x402
settlement fixes that for a single fabricated identity.

One gap worth naming explicitly, because it's exactly the pattern the
2606.26028 paper used to flag reviewers, not a hypothetical: payment-proof
raises the cost of *one* fake reviewer, but doesn't address a funded
*cluster* of them. An attacker with one x402-capable wallet can fund N
downstream wallets, have each one pay-and-review, and every single
review now carries a valid, verifiable payment proof — satisfying the
grounding requirement while still being one entity. That's the
first-funder pattern the paper traced to flag 90.6% of reviewers on
Base; requiring payment doesn't by itself break that graph, since the
attacker is genuinely willing to pay for coverage across the cluster.

Proposal, complementary to payment-proof rather than an alternative to
it: weight aggregation by reviewer independence, not just by count or
by payment validity. Concretely — build the same kind of funding-graph
(or broader activity-graph) clustering the paper used for detection,
and use it to *discount* a cluster's combined weight toward something
closer to one independent voice, rather than N. A group of 50
reviewers who all trace to the same first-funder should contribute
roughly what one reviewer does, not 50x that. Inverse-Simpson (or an
equivalent diversity index) is a reasonable off-the-shelf choice — it
naturally punishes concentrated clusters harder than raw discounting
does, without needing a hard cutoff or an allow/deny list.

This composes with what's already proposed here, I think, in the same
spirit noted above ("without a registry change") — the weighting can
live entirely on the consumer side, reading existing `giveFeedback`
history plus ordinary on-chain funding data, no new registry field
required. It could also reasonably sit in `best-practices/Reputation.md`
as a recommended consumption pattern rather than a protocol change,
if that's a cleaner fit than touching the contracts repo.

We've been building exactly this (diversity-weighted feedback
aggregation, plus a longitudinal-tenure gate for anything that reads
reputation for higher-stakes decisions) into a trust/dispute layer for
agent-to-agent commerce — happy to share the approach in more detail or
put together a reference scorer against real registry data if that's
useful before this gets formalized either way.

Q1/Q2 above, from my read: this feels like it wants to be both — a
standardized grounding tag so consumers know *how* a signal was
verified (Q2), plus independence-weighting as the thing that actually
determines how much any given tag is worth once it's there (a level
past Q1's "gate," since a gate alone still lets a funded cluster
through).

---

## Notes before posting

- Numbers cited (73.5% / 59.2% / 90.6%, and the funding-graph
  methodology) are verified directly against the paper
  (arxiv.org/html/2606.26028), not a secondary summary — safe to quote
  as-is. The paper's own caveat is included implicitly by describing
  this as a "pattern," not proof of coordination; keep it that way if
  editing further, don't state it as certain.
- Deliberately doesn't name Vadium/Atesta by name or link out — one
  line acknowledging "a trust/dispute layer for agent-to-agent
  commerce" without a pitch, consistent with how the x402#3500 draft
  handled this. Add a link only if you want to be identifiable; fine
  either way, just a deliberate choice either direction.
- Tone is collaborative and additive on purpose — this project depends
  on ERC-8004 succeeding (ADR-002), so this reads as "here's a gap your
  own data shows, here's a fix that composes with what you've already
  proposed," never "your standard is broken."
- Not posted automatically — public, attributable action on your own
  GitHub identity. Post with:
  `gh issue comment 99 --repo erc-8004/erc-8004-contracts --body-file docs/erc8004-issue-99-comment.md`
  (strip this "Notes before posting" section first).
