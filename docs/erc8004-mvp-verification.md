# MVP lookup — verification log

2026-09-26. What was confirmed empirically, not assumed, before shipping
defaults into `mvp/erc8004_client.py`.

## Contract addresses (Base Mainnet)

- IdentityRegistry: `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`
- ReputationRegistry: `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63`

Source: the README of https://github.com/erc-8004/erc-8004-contracts.
Both addresses carry the `0x8004` vanity prefix matching the EIP number —
a strong corroborating signal these are the deliberate, real deployment,
not something else.

## Verified live, against real Base mainnet state

1. **Public RPC works with no signup**: `https://mainnet.base.org`
   connects and returns a real, current block number.
2. **The ReputationRegistry address has real deployed bytecode** (130
   bytes — consistent with a thin proxy in front of the real logic,
   which is fine; calls still route through correctly).
3. **Our ABI is correct, not just plausible**: calling `getSummary`
   with an empty `clientAddresses` array produced a *clean, decoded*
   revert — `"clientAddresses required"` — the exact constraint the
   EIP-8004 spec text describes. A wrong function signature or bad ABI
   encoding would have failed to decode at all, not returned an
   on-topic Solidity require() message.
4. **A real, non-reverting round trip works**: calling `getSummary`
   with a real address in the client filter (agentId 1,
   `0x000000000000000000000000000000000000dEaD`) returned `{count: 0,
   value: 0}` cleanly — no feedback for that pairing, which is the
   expected, honest answer for an arbitrary test address, not an error.
5. **The full HTTP endpoint works end-to-end**: `GET
   /lookup/1?reviewers=0x...dEaD` through the actual FastAPI app
   returned the correctly-shaped combined response (own-ledger +
   ERC-8004 raw + Sybil-adjustment sections), each honestly labeled
   when data isn't available rather than silently blank.

## Reviewer discovery — resolved 2026-09-26

Turned out not to need event-log scanning at all: pulled the real,
complete ABI from the reference repo itself
(`github.com/erc-8004/erc-8004-contracts/blob/master/abis/ReputationRegistry.json`,
saved as `mvp/reputation_registry_abi.json`) rather than hand-typing
signatures from the EIP text. It exposes `getClients(agentId) → address[]`
— a direct on-chain enumeration of every reviewer for an agent.
`discover_reviewers()` now calls this for real; no manual `?reviewers=`
param needed for the common case.

Found in the process, and fixed: calling `getSummary`/`readAllFeedback`
with a genuinely empty reviewer list reverts (`"clientAddresses
required"`) rather than returning zero — `mvp/lookup.py` now short-circuits
before that call when discovery legitimately finds no reviewers, instead
of letting it surface as an exception.

## Tested against real, live data

Scanned agentIds 1–150 via `getClients()`; the first three (1, 2, 3) all
have real reviewers (23, 9, 11 respectively) — Base clearly has real
feedback volume, consistent with the empirical paper's finding that Base
carries the large majority of it.

Full pipeline run against **agentId 1** (auto-discovered, no manual
input): **23 real reviewers, 42 feedback entries, raw mean 82.3**. The
Sybil-adjusted number correctly declined to compute and said exactly
why (`BASESCAN_API_KEY not configured`) rather than showing a fake or
silently-wrong adjusted figure.

## The first real raw-vs-Sybil-adjusted comparison — 2026-09-27

`BASESCAN_API_KEY` obtained and set. Re-ran the full lookup against
agentId 1, no other changes:

| | Raw | Sybil-adjusted |
|---|---|---|
| Score | 82.3 | **66.6** |
| Reviewer count | 23 reviewers / 42 feedback entries | **13.6 effective independent reviewers** |

A ~16-point gap between the number every other lookup tool
(phion.systems, Quicknode's explorer) would show as-is, and what it
represents once funding-cluster overlap is priced in — with roughly
40% of the apparent reviewer count collapsing into shared clusters.
This is the differentiator working on real, live Base mainnet data, not
a simulated example.

## Extended to agentIds 2 and 3 — 2026-09-27, same real key

| Agent | Raw score | Adjusted score | Raw reviewers | Effective independent |
|---|---|---|---|---|
| 1 | 82.3 | 66.6 (−16) | 23 | 13.6 |
| 2 | 64.0 | 77.8 (+14) | 9 | 5.6 |
| 3 | 65.3 | 71.7 (+6) | 11 | 5.6 |

Important finding this adds, not visible from agent 1 alone: **the
adjustment moves in both directions.** Agent 1's raw score was inflated
by a concentrated cluster of good reviews; agents 2 and 3's raw scores
look artificially *low*, consistent with a cluster of connected
low-scoring reviews dragging the average down. This is a stronger claim
than "catches fake positive reviews" — it corrects for over-concentrated
influence either way, including protecting an agent from coordinated
brigading, not just from self-inflation.

**Honest caveat, not glossed over**: for agent 3, the largest cluster
(11) equals its total unique reviewer count, which most likely means
one address left many separate feedback entries over time (a real
repeat customer), not necessarily many Sybil wallets funded by one
source. The current clustering treats both cases the same — defensible
(both really are one independent voice carrying outsized weight) but
not proof of fraud specifically, the same "correlation, not proof of
coordination" caveat the source paper made about its own methodology.

## Deployed to Render — 2026-09-27

Live at **https://vadium-lookup.onrender.com**, created via Render's API
(not the dashboard) using a dedicated `vadium-dev` GitHub identity
(separate SSH key + host alias — kept isolated from the primary
account). Deployable package lives in its own repo
(`vadium-dev/vadium-lookup`), deliberately containing only `mvp/` — none
of this project's strategy docs, ADRs, or competitive research, on
purpose.

**Real bug found and fixed before wider rollout**: the rate limiter was
keyed `"global"` — one shared bucket for every caller, meaning a single
aggressive caller could exhaust the whole quota for everyone else,
including whichever new discovery channel we most wanted signal from.
Fixed to key per-caller IP (`X-Forwarded-For`-aware for Render's proxy).
Verified with a clean 35-request burst: 30 succeed, 429 from the 31st
call on. Also added an optional `via` query param (e.g. `?via=mcp`) so
discoverability is measurable per distribution channel instead of
guessed at — logged to stdout (durable in Render's own log history) and
tallied at `/stats` (in-memory, convenience view only).

**Known gap, not yet resolved**: creating the service via Render's API
with a raw `repo` URL doesn't appear to wire up the GitHub webhook the
dashboard's OAuth connection flow would — a push to `main` didn't
trigger `autoDeploy` on its own; had to trigger the redeploy manually
via the API. Works fine as a manual step for now; worth connecting the
GitHub App properly in Render's dashboard if this repo sees frequent
pushes going forward.

## Known ratee/payee split — by design, per ADR-016 — 2026-09-27

Self-registration (below) uses a CDP-managed wallet
(`0xFC414bE58228fe5dBe961B74225548D29b8abeFA`) as `agentWallet`, because
that's the only wallet whose keys this process can actually sign with.
`X402_PAY_TO_ADDRESS` for the paid route is a separate, user-held wallet
(`0x6D9BfB01D003A680b1809E96C0D4003be2ec87d0`), chosen deliberately so
payment funds land somewhere the user holds the seed for directly, not
somewhere requiring CDP API credentials to withdraw from.

This is the same ratee/payee gap raised in the `erc8004-issue-99`
follow-up comment, at the individual-agent level rather than the
organization level ADR-015 already covered. Formalized as
**ADR-016** (`docs/phase3-design-decisions.md`): reputation and
collateral attribution key off the registered identity (`agentWallet`),
never off `payTo` — which is expected to rotate, and does here. This
identity isn't wired into Phase 3's collateral/dispute logic yet, so
there's nothing live depending on the distinction today, but the split
itself is the correct, intended shape going forward, not a shortcut
taken because the stakes happen to be low.

## Self-registered on-chain — 2026-09-27

Vadium Lookup registered itself as an ERC-8004 identity for real, on Base
mainnet, from the CDP-managed wallet (see the ratee/payee note above for
why that wallet, not the user's own).

1. **`register()`** (bare, no args) — tx
   `0xcc9bac8b7aadb20be687926e6f72f583e1b7fb641a45d9501a17df8bcafcadc8`,
   block 51858284, 106,883 gas. Decoded the `Registered` event from the
   receipt directly rather than guessing: **agentId = 95910**, owner =
   `0xFC414bE58228fe5dBe961B74225548D29b8abeFA`.
2. Set `ERC8004_AGENT_ID=95910`, redeployed — confirmed
   `/.well-known/agent-registration.json` now serves a `registrations`
   entry pointing at this exact agentId and registry address.
3. **`setAgentURI(95910, ".../agent-registration.json")`** — tx
   `0x29403fd0fe8662e4b141f3f31eec889dfe5450559d5985ad8b4889bcf384085c`,
   block 51858373, 123,899 gas.
4. **Verified, not assumed**: `tokenURI(95910)` on-chain returns exactly
   the registered URL (needed a few seconds of RPC propagation — first
   read came back empty, three retries later it was correct — a real,
   observed lag, not a guess papered over). `ownerOf(95910)` and
   `getAgentWallet(95910)` both independently resolve to the CDP wallet,
   confirming the identity is internally consistent.

Total real cost for both transactions: on the order of 0.000001–0.000002
ETH combined — Base mainnet gas at the time of writing was roughly
0.005 gwei base fee, making this registration cost a small fraction of a
cent, not a meaningful expense even repeated many times over.

Registration file used the real ERC8004SPEC.md `registration-v1` schema
(fetched fresh, not recalled) — `services` lists only what's actually
live (`web`); deliberately omits an `MCP` entry since our MCP server
runs over stdio, not a network URL the spec's format expects, and
omits `A2A`/`OASF`/`ENS`/`DID` entries and `crypto-economic`/
`tee-attestation` trust claims we don't implement. `supportedTrust` is
just `["reputation"]` — the one claim that's real.

## Circle Agent Marketplace — submitted 2026-09-27

Verified the real submission mechanism first rather than trusting a
possibly-stale note: `docs/IDEA.md` described a manual-review Google
Form, current `developers.circle.com/agent-stack/agent-marketplace/
get-listed` confirms that's still accurate ("Listings are reviewed and
approved manually today. A self-serve, automated submission flow is
coming.") and gave the same form URL independently. Cross-checked the
form itself before entering anything — footer confirms "This form was
created inside of Circle Internet Financial Inc."

Submitted: service name Vadium Lookup, website
`https://vadium-lookup.onrender.com`, category Infrastructure (closest
fit — no dedicated trust/reputation option), 2 endpoints, pricing model
described (free + $0.001 USDC x402 tier), docs URL pointing at the live
FastAPI `/docs`. Mentioned the ERC-8004 self-registration (agentId
95910) and the discoverability-measurement framing in the free-text
field. Response confirmed recorded by Circle's own form.

This is now the fifth measurable discovery channel alongside direct,
MCP, x402 Bazaar, and ERC-8004 registry — and, per the earlier channel
comparison, the one with the closest audience-market fit, since
Circle/Arc-native agents are the same population already capable of
paying via x402.

## Still open

- No caching yet — `mvp/diversity.py`'s in-process `_funder_cache` only
  persists for the life of one running process; fine for testing, worth
  revisiting before real traffic volume.
- Not yet distinguishing "one address, many feedback entries" from
  "many addresses, one funder" in the cluster output — both currently
  collapse into the same cluster-size number. Worth surfacing separately
  if this goes further, so "5 fake wallets" and "1 repeat customer"
  don't read identically to someone using the tool.
