# Design Partner Outreach

Status: drafted, **not sent**. Real companies, real public contact
channels — review the exact wording and pick the actual send channel
yourself before anything goes out. See `docs/plain-english-primer.md`
Part 4 for why this step matters and why legal review of ADR-013 rides
along with it, and `docs/IDEA.md` §8–9 for the underlying instruction.

## The shape of the story — read this before any candidate section

Every candidate pitch below leads with a project-specific hook, but they
all rest on the same underlying sequence, and it's worth stating once,
explicitly, rather than leaving a reader to infer it from a list of
dates: **each phase exists to remove one specific kind of risk before
spending effort on the next — cheapest and fastest first, hardest and
most consequential last.**

1. **Phase 1** (spend monitoring, live since 2026-09-17) answers a pure
   observability question — can we see what an agent is actually doing,
   against a real Circle Agent Wallet — before claiming anything about
   trust or disputes at all.
2. **Phase 2** (the evidence ledger, `AnchorLog` deployed on Arc testnet
   2026-09-18) answers the evidentiary question that observability alone
   doesn't: once we can see it, can we *prove* it later, to a skeptical
   third party, without anyone taking our word for it.
3. **The free Lookup MVP** answers the question that's cheapest to get
   wrong and most important to get right before building anything
   expensive — does anyone actually want a trust signal at all — tested
   against *real, existing* ERC-8004 data on Base rather than our own
   cold-started ledger, with zero financial mechanism and therefore zero
   legal exposure, specifically so this could be answered before any
   legally-sensitive work began.
4. **The Phase 3 testnet demo** answers the hardest engineering
   question — does the actual collateral, dispute, and insurance
   mechanism work correctly, under both automatic and judgment-call
   conditions — fully, with real transactions and real payout math,
   while deliberately holding the one variable that would make it
   legally consequential, real money, at exactly zero.
5. What's left is the one risk that can't be reduced by writing more
   code: whether this specific mechanism is compliant. That's not a gap
   in the plan — it's the plan working. Real legal review now reviews a
   fully-proven mechanism, not a hypothesis, which is the entire point
   of doing the other four in this order.

Every candidate section below assumes this framing rather than
restating it — lead with it explicitly if a conversation goes past the
first message.

## The base message

Subject: **Trust layer for Arc agent transactions — looking for 2-3 design partners**

> Hi [name] — following what you're building [with ERC-8183 / with
> BlockRun's marketplace / on x402] on Arc.
>
> We're building the piece we think is still missing from agent-to-agent
> commerce: a verification and dispute layer that sits on top of
> ERC-8004/ERC-8183, so a buyer agent has real recourse when a seller
> doesn't deliver, and a good seller can prove it. [Per-recipient line —
> see below.]
>
> We're looking for 2-3 real design partners before we finalize the
> build — teams with actual agent-to-agent transaction volume who'd be
> willing to try an early version, tell us honestly what's broken or
> overpriced, and help us calibrate this against real usage instead of
> our own assumptions. In exchange: early access, direct input into the
> design, and favorable terms once this is live.
>
> Would a short call make sense to see if there's a fit?
>
> [Your name]

## Be upfront about what's actually ready — for all three

**Say this plainly to every candidate, don't let the pitch imply more
than exists**: Phase 1 (spend monitoring against a real Circle Agent
Wallet) is live and working today. The trust/dispute layer described in
the message — the jury system, the bond economics — is a completed,
detailed design (14 ADRs) but **not yet built**. What a "yes" from a
design partner actually means right now is: help us validate the design
and pricing with real numbers, and be first in line once the build
reaches something usable — not "use our finished product today."
Overstating this to a technically sophisticated team (all three
candidates are) will be noticed immediately and costs more credibility
than it gains.

## Candidate 1 — Virtuals Protocol

**Why them**: co-authored ERC-8183 itself with the Ethereum Foundation's
dAI team — the exact escrow/evaluator standard this whole mechanism is
built on. Runs the largest agent launchpad (17,000+ agents) and has
publicly discussed managing $3M+ in agent transactions *without*
escrow — meaning they've already felt the specific pain point this
solves, not a hypothetical one.

**Channel**: Virtuals Partners Network application — virtuals.io/vpn.
This is a structured intake form, not an inbox — adapt the draft below
into whatever fields the form actually asks for (typically: what you're
building, what you need, stage) rather than pasting it verbatim.

**Draft message**:

> Hi [name] — we're building on ERC-8183, which your team co-authored
> with the Ethereum Foundation's dAI team. There's a real gap sitting
> right at the escrow/evaluator role the standard defines but leaves
> open: what happens when a buyer and seller disagree about whether
> delivered work meets spec.
>
> We're building Vadium (by Atesta) to fill exactly that role — a
> collateral and dispute-resolution layer where sellers post real
> collateral behind their promises, a tamper-evident evidence ledger
> records what actually happened, and disputes resolve with money that
> actually moves. Not a new protocol to adopt — the evaluator
> implementation ERC-8183 already made room for.
>
> Where we actually are, plainly: the evidence ledger and spend
> monitoring are live today, anchored on-chain and independently
> verifiable. The dispute-resolution and bond-economics layer — the part
> that would matter to your agents — is a complete, detailed design, not
> yet built. We're not asking you to integrate something finished; we're
> asking to be one of 2-3 design partners who help us calibrate it
> against real transaction volume before the build is locked in.
>
> You've talked publicly about managing $3M+ in agent transactions
> without escrow — that's the exact pain point this closes. Would a
> short call make sense to see if there's a real fit?
>
> [Your name]

**How to approach**:
- Lead with the ERC-8183 connection immediately, first sentence — that's
  the whole reason this isn't a cold pitch for them specifically.
- Expect sharp technical questions given they wrote the standard — have
  `docs/phase3-architecture.md` and `docs/phase3-design-decisions.md`
  ready to share if asked, don't try to explain the mechanism from
  memory in a fast-moving conversation.
- Expect the slowest response of the three — larger org, partnership
  intake likely goes through a queue. Send this one first, not last,
  specifically because of that lag.

## Candidate 2 — BlockRun

**Why them**: a live, currently-operating marketplace on Arc right
now — 78 frontier LLMs plus media/data services, billed per call via
x402, settled in USDC on a dedicated Arc endpoint (`arc.blockrun.ai`,
chain id 5042, USDC as gas — confirmed 2026-09-20). Checked their full
docs for a competing trust layer, the same way we checked Kite/NEAR/ASI
below: no reputation scoring, escrow, dispute resolution, arbitration,
refunds, or bonding anywhere. This is the cleanest complementary fit
found so far — real transaction volume today, and a genuinely open gap,
not one they've already filled.

One thing worth knowing before pitching: their transaction shape (LLM
calls, media generation) is mostly commodity and machine-verifiable —
did the API respond, was the output produced — not the richer
quality-fitness disputes this project's own scenarios use as examples.
Good for a first pilot (fewer ambiguous edge cases while the design
firms up), but a thinner dispute story than we'd eventually want to
showcase for a services marketplace.

**Channel**: verified 2026-09-21 — `blockrun.ai/contact` (their own
stated partnership path, linked from `/partners`) is primary. Also
listed in Circle's own Alliance Directory
(partners.circle.com/partner/blockrun, which itself describes them as
"Pay-as-you-go AI and x402 discovery on Base") — worth opening with the
shared-Circle-ecosystem context there. Backup channels: @BlockRunAI on
X, and a named team member, Emma Hsieh, findable on LinkedIn — often
more reliable than a generic form for a team this size. Real volume
split found while checking: 29M transactions in 7 months, 27M on Base
vs. 2M on Solana — confirms Base carries the large majority of their
actual activity, which is why the draft message below leans on the
Base-portability point rather than treating Arc as their primary rail.

**Draft message**:

> Hi [name] — we've been watching what you've built: pay-per-call access
> to 78 frontier LLMs plus media and data services, settled in USDC via
> x402, no API keys, no subscriptions. That's exactly the kind of real,
> live transaction volume we've been designing against.
>
> We're building Vadium (by Atesta): a collateral and dispute-resolution
> layer for agent-to-agent commerce, sitting on top of ERC-8004/ERC-8183
> rather than a proprietary system. We checked — nothing in your stack
> today handles what happens when an API call fails, times out, or
> returns something unusable after payment's already settled. That's the
> gap we're built to close.
>
> Concretely, rather than a general conversation: with your consent,
> we'd like to observe or instrument a slice of real transaction flow
> through arc.blockrun.ai, so we can calibrate this against actual
> failure/dispute patterns instead of our own assumptions. In exchange:
> early access, direct input into the design, and favorable terms once
> it's live.
>
> To be upfront about where we actually are: spend monitoring and the
> evidence ledger are live today, running against a real, funded agent
> wallet on Arc. The dispute-resolution and collateral mechanics are a
> complete design, not yet built — a "yes" from you means helping us get
> the design and pricing right with real data, not adopting a finished
> product today.
>
> One more thing worth knowing: we built this on open standards
> (ERC-8004/8183) specifically so it isn't locked to one chain — it
> already ports to Base with no rework, just redeployment, which matters
> if more of your real volume runs there than through the Arc-specific
> endpoint.
>
> Would a short call make sense?
>
> [Your name]

**How to approach**:
- Be concrete and operational, not abstract — propose something
  specific, like observing or instrumenting a slice of their real
  transaction flow (with their explicit consent), rather than a general
  discussion of the idea.
- Given real, live volume, this is the best candidate to actually
  produce usable data fastest — good first-priority send alongside
  Virtuals, not after it.

## Checked and moved to competitive-landscape tracking, not outreach

**Kite AI** was originally listed here as complementary ("SLA definition
is the upstream half, we do violation adjudication"). Rechecked
2026-09-20 against their own whitepaper: they already claim an
arbitration layer, reputation scoring, and slashing — the same
destination we're building toward, not an upstream half of it. Same
finding for **NEAR AI Agent Market** (live escrow + dispute-agent +
arbitration) and **ASI Alliance/Agentverse** (Trust Registries, tiered
reputation). Approaching any of these three as "we'd plug into what you
already do" would misread what they've actually built. See
`docs/IDEA.md` §2.1 for the full finding and what it implies for
positioning (portability across platforms, not owning one platform's
trust layer).

## Checked and dropped — wrong settlement rail, not a competing trust layer

**Skyfire** — verified 2026-09-20: not a chain/x402 mismatch to
"confirm later," a real disqualifier. Its KYA/KYAPay stack settles
through traditional card-network rails — live partnerships with Visa's
Trusted Agent Protocol (launch partner, live Oct 2025) and a live
purchase demo with Visa Intelligent Commerce (Dec 2025); Mastercard's
Agent Pay ties identity into the network token directly. USDC is listed
as one settlement option alongside Visa/Mastercard/Discover, but no
mention anywhere (multiple searches, direct doc fetch) of x402, Arc, or
blockchain settlement infrastructure. No dispute/escrow/arbitration
either, so it's not competing — but there's no x402 transaction stream
for an evidence ledger to observe in the first place. Not a candidate.

Useful context beyond Skyfire itself: Visa and Mastercard are running a
parallel, non-crypto track on the same underlying problem (agent
identity for payments) — real market validation, but a different rail
from x402/ERC-8004, not an adjacent opportunity or a competitor.

## Additional candidate — x402 confirmed, Arc-specific deployment not yet confirmed

**Nevermined** — payment-routing/metering layer (per-call, per-outcome,
subscription pricing). Has a real, named **x402 Facilitator** product
(not just a blog claim) — genuine x402 involvement confirmed via their
own docs. No dispute/escrow/arbitration/reputation mechanism found
anywhere. Open question: their docs describe chains generically
("blockchain," "on-chain," sandbox/production URLs) without naming Arc,
Base, or any specific network, and no public supported-networks list
was found. Worth a direct conversation to confirm Arc support before
treating this as equivalent to BlockRun's confirmed fit — don't cite
their own blog's ERC-8004 claim in outreach without verifying it
directly either, same reasoning.

## Candidate 3 — Base ecosystem team (via warm intro, not a marketplace pilot)

**Why them, and why now**: reviewed the actual code 2026-09-20 (see
`docs/IDEA.md` §6.4) — `AnchorLog.sol` and the Merkle/storage layer have
zero Arc-specific dependencies, and Circle's own tooling already treats
Base as a first-class supported chain alongside Arc, with native USDC.
Porting is a redeploy-and-reconfigure exercise, not a rewrite. Real x402
volume is concentrated on Base today (BlockRun's general product,
PayAI, Coinbase's own Agentic.market and CDP facilitator) — more than
currently exists on Arc. This is a different kind of contact than
Candidates 1-2: not a marketplace to pilot with, an ecosystem/BD
relationship that could open several marketplace introductions at once.

**Channel**: warm introduction via KnightIntelco's founder to a contact
at Base APAC — use it, don't cold-outreach this one instead.

**Draft message**:

> Hi [name] — [KnightIntelco founder] mentioned we should connect.
>
> We're building Vadium (by Atesta): a collateral and dispute-resolution
> layer for agent-to-agent commerce — sellers post real collateral, a
> tamper-evident evidence ledger records what happened, and disputes
> resolve with money that actually moves. It sits on top of
> ERC-8004/ERC-8183 rather than a proprietary system, running on Arc
> today.
>
> We built it on open standards deliberately, and it shows: we've
> confirmed our contracts and signature verification (ERC-1271, the same
> pattern Circle's own smart-contract wallets already use) port to Base
> with no rework, just redeployment. Given how much real x402 activity
> already runs on Base, it's a natural next chain for us.
>
> We'd like to understand the best way to plug into the Base
> agent-commerce ecosystem — whether that's ecosystem support, an
> introduction to marketplaces already running real x402 volume who
> might want a trust layer they don't have to build themselves, or just
> your take on where this is headed.
>
> Would a short call make sense?
>
> [Your name]

**How to approach**:
- Lead with the introduction, not the pitch — this is warm, don't open
  cold-outreach style.
- The ask here is different from Candidates 1-2: not "be our design
  partner," but "help us find design partners on Base, and tell us how
  Base thinks about this problem." Don't oversell readiness — same
  honesty rule as the base message: Phase 1/2 are live, Phase 3 is
  designed, not built.
- If it leads to specific marketplace introductions, run those through
  the same verification process as every other candidate here (check
  for an existing trust/dispute layer before pitching complementary) —
  a warm intro doesn't exempt a candidate from that check.

## Candidate 4 — Circle Developer Grants Program (direct to Circle/Arc, not a pilot pitch)

**Why this, and why now**: Arc's own vision post
(`arc.io/blog/the-unfinished-business-of-finance-machine-commerce-and-
global-money`, checked 2026-09-27 — see `docs/IDEA.md` §2) names, as
part of its own roadmap, **outcome marketplaces** ("payment released on
verified completion against an agreed standard") and **agentic
insurance** ("parametric payouts on verified loss events") — without
ever naming who verifies a contested completion or loss event, or how.
That gap is this project. Circle's own grants page
(`circle.com/grant`, checked 2026-09-27) lists **"agentic economic
activity" as its first priority use case**, and is explicit that
funding is milestone-based, $5,000–$100,000 in USDC, tied to
integrations and ecosystem impact — not a lump sum requiring instant
mainnet presence.

**Checked and ruled out, not just deprioritized**: Arc's separate
Microgrants program (DoraHacks, $500 × 20, deadline 2026-10-14)
explicitly requires Arc **mainnet** deployment and a **public** code
repository — both would mean abandoning the two things this project is
deliberately holding right now: no real value moves before ADR-001/013
legal review, and the source stays private until there's a reason not
to. $500 doesn't justify either tradeoff. Not pursuing this one.

**The angle**: don't pitch this as "please fund our roadmap" — pitch it
as "you named this gap yourselves; here's a working, verified answer,
and here's the specific milestone that turns it into something real."
The milestone structure is the actual lever: a milestone can legitimately
be "complete real legal review of the collateral/insurance mechanism,"
which is the one thing blocking this from being a live product, and
which Circle has direct interest in seeing resolved correctly rather
than left as a compliance question hanging over their own ecosystem's
agentic-insurance narrative.

**Channel**: `circle.com/grant` — a real, structured application
(business details, Circle/Arc integrations, product roadmap, proposed
milestones), not a cold email. Application content, not verbatim
copy — adapt to whatever fields the form actually asks for:

> **What you're building**: Vadium (by Atesta) — a collateral and
> dispute-resolution layer for agent-to-agent commerce on Arc, built on
> ERC-8004/ERC-8183 rather than a proprietary system. Where your own
> vision post calls for outcome marketplaces with payment released on
> "verified completion" and agentic insurance with "parametric payouts
> on verified loss events," we built the verification and arbitration
> mechanism that makes those claims adjudicable when the parties
> disagree — the part neither concept works without.
>
> **Circle/Arc integration**: identity and reputation on ERC-8004, job
> escrow on ERC-8183, collateral and dispute resolution (`BondPool`)
> settled in Arc-native USDC. A free reputation-lookup product is
> already live and self-registered as an ERC-8004 identity on Base
> mainnet (Arc-first positioning doesn't mean Arc-only — see
> `docs/IDEA.md` §6.4) — this grant is about the collateral/dispute
> layer behind it, not a green-field idea.
>
> **Traction so far — each step deliberately de-risks the next, cheapest
> first, hardest and most consequential last, everything below
> independently verifiable, not asserted**:
> - *Can we see what an agent is actually doing?* Phase 1 — spend
>   monitoring against a real Circle Agent Wallet, live since 2026-09-17.
> - *Can we prove it later, without anyone taking our word for it?*
>   Phase 2 — tamper-evident evidence ledger; `AnchorLog` deployed on Arc
>   testnet 2026-09-18: [`0xf3d5...6fa2`](https://explorer.testnet.arc.io/address/0xf3d5ecfb7b89dcc8b181191e5782edb5bb5f6fa2).
> - *Does anyone actually want a trust signal at all — cheaply, before
>   building anything expensive?* The free Lookup MVP —
>   [vadium-lookup.onrender.com](https://vadium-lookup.onrender.com),
>   tested against real, existing ERC-8004 data rather than a cold-started
>   ledger of our own, self-registered as agentId 95910 on Base mainnet
>   ([registration tx](https://basescan.org/tx/0xcc9bac8b7aadb20be687926e6f72f583e1b7fb641a45d9501a17df8bcafcadc8),
>   [agentURI set](https://basescan.org/tx/0x29403fd0fe8662e4b141f3f31eec889dfe5450559d5985ad8b4889bcf384085c)),
>   submitted to the Circle Agent Marketplace. Zero financial mechanism,
>   zero legal exposure, by design.
> - *Does the actual collateral/dispute/insurance mechanism work, under
>   both automatic and judgment-call conditions?* Phase 3 — fully built
>   and verified end-to-end on Arc testnet:
>   [`BondPool`](https://testnet.arcscan.app/address/0x73B2bE54639BE40FB549A6023798Fee3eF42D681),
>   [job escrow](https://testnet.arcscan.app/address/0xAC5C72D2F4E633c97314b755761CCB16E44DAFDF).
>   Three real disputes resolved — [objective-path slash](https://testnet.arcscan.app/tx/0x39441b642c484587e3c6b169fed9b91998f0cefc6cf36d042c86614cc9cc07b4),
>   [discretionary committee verdict](https://testnet.arcscan.app/tx/0x0440ecf3c8aa5860ecaebaf5058cf49973a54a0da354a55e146576b1f519b422),
>   [hedge-coverage payout](https://testnet.arcscan.app/tx/0xba8838e98243cef904a96c6c0e94f6630956d2acc33a5d27708351095d486f8c)
>   — all three payout rules independently confirmed on-chain, with the
>   one variable that would make this legally consequential, real money,
>   deliberately held at zero throughout.
> - *What's left is the one risk more code can't reduce*: whether this
>   specific mechanism is compliant. That's milestone 1 below — not a
>   gap we're glossing over, the reason we're applying now rather than
>   after paying for it alone.
>
> **Proposed milestones**: (1) complete real legal counsel review of the
> collateral/insurance-classification design — the concrete blocker
> between "designed and testnet-proven" and "live"; (2) mainnet
> deployment with real design-partner collateral once (1) clears; (3)
> [pricing/committee milestones once (1) and (2) are scoped].
>
> A short walkthrough of the live testnet mechanism (real transactions,
> real before/after balances) is available on request.

**How to approach**:
- Lead with their own language, not ours — the opening paragraph should
  make it obvious this is a direct response to something Circle already
  said publicly, not a generic pitch that happens to mention Arc.
- Milestone 1 (legal review) being fundable is the actual point of this
  channel — don't bury it as a caveat, it's the reason this is worth
  applying now rather than after the review is already done and paid
  for out of pocket.
- Same honesty discipline as every other candidate: traction claims
  above are real and dated; don't let "verified end-to-end on testnet"
  imply mainnet-ready if a reviewer skims fast.
- "Available on request" refers to the "Three Real Disputes" walkthrough
  artifact — currently private; share it (or a redeploy of it) directly
  with the reviewer rather than linking it in the application itself.

## Candidate 5 — Sam (Circle/Arc Developer Community) — a different channel, not a formal application

**Why, and why now**: Sam leads developer community at Circle & Arc
(@samconnerone) — not the grants team, but well-placed to (a) escalate
the Questbook bug directly and (b) be aware of what's being built, which
matters given events/spotlights are part of the role. Two real, concrete
things to raise, not a generic intro.

**Channel**: X DM to @samconnerone. Short, conversational register —
this is community outreach, not a grant application; don't reuse the
formal Candidate 4 language verbatim.

**Draft message**:

> Hi Sam — two things, one bug report and one heads-up.
>
> The Circle Grants Program portal (circle.questbook.app) is throwing
> real errors on load right now — repeated "Object Object error in scw
> deployment" plus a TypeError, not a fluke, reproducible. Figured it's
> worth flagging directly since it's blocking anyone trying to apply
> right now, myself included.
>
> Separately — we're building Vadium (by Atesta): the verification and
> dispute-resolution layer for agent-to-agent commerce that Arc's own
> post on machine commerce calls for (outcome marketplaces on "verified
> completion," agentic insurance on "verified loss events") without
> naming who does the verifying. We've proven the whole mechanism live
> on Arc testnet — three real disputes, real transactions, zero real
> money — happy to send a two-minute walkthrough if useful for what
> you're spotlighting.
>
> No ask beyond the bug report — just wanted it on your radar.

**How to approach**:
- Lead with the bug report — it's genuinely useful to them regardless of
  anything else, and it's why the DM isn't just a cold pitch.
- Keep the Vadium mention brief and low-pressure; this isn't the venue
  for the full pitch, that's what the walkthrough artifact is for if
  they respond with interest.
- If it goes anywhere, that's the moment to share the "Three Real
  Disputes" artifact directly (it's private — share the link, don't
  paste it into a public DM thread).

## OKX AI — corrected 2026-10-02, moved from outreach to competitive landscape

**Retraction**: this was briefly listed as "Candidate 6," a high-priority
outreach target, on the finding that OKX AI had no built-in dispute
mechanism of its own. **That finding was wrong**, caught by an
independent review and confirmed by re-checking OKX's own page directly
rather than relying on launch-day press coverage alone. The correction
matters enough to document in full, since the original outreach draft
below would have been factually wrong on first contact.

**What's actually confirmed, direct from okx.com/en-us/learn/okx-ai and
independent coverage**: OKX AI has its own native escrow (for negotiable
A2A tasks) and instant pay-per-call settlement (for standardized
A2MCP tasks); disputes are resolved by **a staked network of
evaluators** — not GenLayer, not a third party — who stake OKB, vote,
earn rewards for correct decisions, and lose stake for incorrect ones;
and reputation is portable across both transaction modes under one
"Agentic Wallet" identity. Separately and more importantly: **OKX's
identity layer is built on ERC-8004 itself** — the same standard this
project uses, not a proprietary system. GenLayer's listed
"dispute-resolution infrastructure" is a separate, additional product
sold on the marketplace — not, as previously stated here, the only
dispute mechanism OKX AI has.

**What this changes**: OKX AI gets the same treatment as Kite AI, NEAR's
Agent Market, and ASI Alliance above — a live, real, already-built
competitor on the evaluator/dispute-resolution role specifically, not an
outreach target for that role. Pitching "let us be your evaluator" to a
marketplace that already has a staked, live, OKB-backed one is the exact
mistake this doc's own methodology exists to catch.

**What doesn't change, and is worth keeping**: two things survive the
correction. First, OKX AI remains real, independently-sourced evidence
that agent-to-agent *service* commerce (not goods-purchasing) is
happening today, settled in stablecoins specifically because card rails
don't fit — that evidentiary point didn't depend on whether they had a
dispute mechanism. Second, and more interesting: because OKX AI's
identity layer uses **open, permissionless ERC-8004** rather than a
proprietary system like Kite/NEAR/ASI's, its agents' reputation data is
publicly readable by anyone — including Vadium's own lookup product —
without OKX's cooperation or permission, the same way any ERC-8004
reader can read any other reader's feedback by design. This is a
concrete, nameable test of the portability thesis already argued in
§2.1 of `docs/IDEA.md`: not "will OKX AI let us in," but "do agents who
sell on OKX AI also want a reputation record that travels to other
marketplaces, independent of OKX AI's own walled dispute system." That's
a real question worth testing directly with their actual sellers
(CertiK, CoinAnk, and others), not a reason to write off the lead
entirely — see the 30-day test in `docs/IDEA.md` §1.1.

**Do not send** the draft message that previously lived here. If
re-approaching OKX AI's sellers at all, the only honest pitch left is
the portability one, not a dispute-resolution pitch — see the updated
30-day test design in `docs/IDEA.md` §1.1 for how to validate that
cheaply before investing in an outreach draft.

## Sequencing and tracking

Send to Virtuals and BlockRun in the same window rather than waiting on
one before the other — response speed will differ a lot between a large
protocol (Virtuals) and a small live team (BlockRun). Treat Nevermined
as a second wave, after their Arc support is actually confirmed — don't
send to them on the strength of this doc alone. Skyfire is dropped, not
just deferred — see above. **OKX AI is moved to competitive landscape,
not an outreach send** — corrected 2026-10-02, see the full note above;
it has its own live, staked dispute-resolution mechanism, the same
situation as Kite/NEAR/ASI.

Track responses somewhere simple as they come in:

| Candidate | Channel used | Date sent | Response | Next step |
|---|---|---|---|---|
| Virtuals Protocol | virtuals.io/vpn | sent (pre-2026-09-26) | pending, no response as of 2026-10-02 | consider a tighter, more concrete ask — see note below |
| BlockRun | blockrun.ai/contact | sent (pre-2026-09-26) | pending, no response as of 2026-10-02 | same as above |
| OKX AI | — | not applicable | — | moved to competitive landscape (above), not an outreach send; its sellers are a 30-day test target instead, see `docs/IDEA.md` §1.1 |
| Nevermined | nevermined.ai | not sent | — | confirm Arc support directly with them before sending, per the note above |
| Base ecosystem (APAC) | warm intro via KnightIntelco | not yet — meeting with KnightIntelco scheduled for the week of 2026-09-28 | — | confirm intro happens at/after that meeting |
| Circle Developer Grants | circle.com/grant | not sent | — | ready to send now — traction section is accurate as of 2026-09-27 |
| Sam (Circle/Arc community) | X DM, @samconnerone | not sent | — | bug report + light-touch heads-up, ready now |

**Note on Virtuals/BlockRun silence (added 2026-10-02)**: over a week of
no response from either. Cold outreach to a larger protocol being slow
is expected (flagged in Candidate 1's own notes), but this long a
silence from *both* is worth treating as signal, not just normal lag.
Before sending more follow-ups on the same message, consider whether the
original ask ("want to be a design partner?") is too open-ended —
a concrete, zero-cost, time-boxed pilot offer (observe or instrument a
small slice of real transaction flow for 30 days, no commitment beyond
that) may get a faster answer than a general partnership conversation.

## Track B — outcome-billing audit leads (added 2026-10-02)

A different outreach motion from Candidates 1–5 above: those target
*marketplaces* as Track A design partners. This targets *buyers* of
outcome-billed AI customer-service agents, as real near-term leads for
Track B (see `docs/IDEA.md` §1.1). No engineering required to start —
this is cold outreach plus manual transcript review for the first few
pilots.

**Why these leads specifically**: real, documented, public complaints
already exist from people who've identified this exact pain themselves —
the best kind of lead, since there's no educating required. Confirmed
sources from this project's own research: a thread on Intercom's own
community forum titled around "Fin's flawed assumed-resolved pricing
design," and Reddit complaints about Zendesk billing abandoned chats as
resolved with "no dispute resolution process." HubSpot's outcome pricing
shipped too recently (April 2026) for public complaints to have surfaced
yet — not a dead end, just early; worth checking again in a few months,
or reaching out proactively to HubSpot Breeze customers before a public
complaint even exists.

**What to promise — be precise, don't overclaim**: a diagnostic audit
showing exactly how many billed "resolutions" fail even the vendor's own
stated definition, split into objective errors (agent never replied, no
real engagement — usually recoverable directly) versus defined-away
cases (silence-triggered, contractually-as-described — not a winnable
refund demand, but real leverage for the next renewal). For the
follow-up product, pitch *prevention*, not recovery: ongoing
shadow-testing of the vendor's live agent, not an after-the-fact audit —
see `docs/IDEA.md` §1.1 Track B for the mechanism (reuses ADR-009's
evergreen-calibration design).

**Draft message** (adapt per channel — a public forum reply should be
shorter and less formal than a cold email):

> Hi [name] — saw your post about [Fin's assumed-resolved billing /
> Zendesk counting abandoned chats as resolved]. We're looking into
> exactly this problem: AI customer-service vendors billing by outcome,
> judged by their own model, with no published appeal process.
>
> We'd like to run a free audit of your last 90 days of conversation
> transcripts — using your own export access, nothing from the vendor
> required — and show you exactly how many billed "resolutions" don't
> hold up, split into clear billing errors versus your vendor's own
> contractual definitions. No cost, no commitment.
>
> If that's useful, the next step we're building is live monitoring —
> catching this before you're billed, not after — but the audit alone
> should be useful on its own regardless.
>
> Worth a short conversation?
>
> [Your name]

**Channel guidance**:
- **Forum reply** (Intercom community, Reddit) — reply directly in-thread
  where the complaint was posted; shortest, most context-aware version
  of the message above, first line referencing their specific complaint
  verbatim.
- **Cold email/LinkedIn** — only if the poster's company is identifiable
  from their post/profile; use the fuller version above.
- Don't scrape or compile a list beyond what's already public and
  directly responsive to — reply to real complaints, don't build a
  database of who-complained-about-what beyond what's needed to send one
  relevant message each.

**How to approach**:
- Lead with their own complaint, not our pitch — the same discipline
  used for Virtuals' ERC-8183 connection and OKX AI's launch details.
- Free-audit-first, no strings — this is the cheapest possible way to
  find out whether real demand exists before building anything, per the
  30-day-experiment framing already discussed for Track A.
- Track responses the same way as the table above; add rows here once
  specific threads/people are identified and contacted.

## If someone says yes

Don't over-promise a scope that doesn't exist yet. The concrete next
step with a real "yes" is to define, specifically for that partner,
what a pilot actually looks like — what they'll actually get to touch
(today, realistically, that's Phase 1's spend-monitoring capability,
not the trust/dispute layer), what feedback loop you'll run, and what's
confidential about their transaction data versus what feeds back into
this project's own design docs. Scope that conversation before saying
yes to a broader commitment than what's actually buildable right now.
