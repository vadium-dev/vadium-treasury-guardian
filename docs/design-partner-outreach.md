# Design Partner Outreach

Status: drafted, **not sent**. Real companies, real public contact
channels — review the exact wording and pick the actual send channel
yourself before anything goes out. See `docs/plain-english-primer.md`
Part 4 for why this step matters and why legal review of ADR-013 rides
along with it, and `docs/IDEA.md` §8–9 for the underlying instruction.

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

## Sequencing and tracking

Send to Virtuals and BlockRun in the same window rather than waiting on
one before the other — response speed will differ a lot between a large
protocol (Virtuals) and a small live team (BlockRun). Treat Nevermined
as a second wave, after their Arc support is actually confirmed — don't
send to them on the strength of this doc alone. Skyfire is dropped, not
just deferred — see above.

Track responses somewhere simple as they come in:

| Candidate | Channel used | Date sent | Response | Next step |
|---|---|---|---|---|
| Virtuals Protocol | virtuals.io/vpn | sent (pre-2026-09-26) | pending | watch for response — expect slowest of the three per note above |
| BlockRun | blockrun.ai/contact | sent (pre-2026-09-26) | pending | watch for response |
| Nevermined | nevermined.ai | not sent | — | confirm Arc support directly with them before sending, per the note above |
| Base ecosystem (APAC) | warm intro via KnightIntelco | not yet — meeting with KnightIntelco scheduled for the week of 2026-09-28 | — | confirm intro happens at/after that meeting |

## If someone says yes

Don't over-promise a scope that doesn't exist yet. The concrete next
step with a real "yes" is to define, specifically for that partner,
what a pilot actually looks like — what they'll actually get to touch
(today, realistically, that's Phase 1's spend-monitoring capability,
not the trust/dispute layer), what feedback loop you'll run, and what's
confidential about their transaction data versus what feeds back into
this project's own design docs. Scope that conversation before saying
yes to a broader commitment than what's actually buildable right now.
