# Phase 3 testnet build — spec

Status: **spec written, build starting.** Companion to
`docs/phase3-architecture.md`, `-design-decisions.md`, and `-backlog.md`
— this doc doesn't redesign anything, it scopes a concrete, testnet-only
build of a real slice of the existing design, using free faucet
currency, so the mechanism is demonstrable (to design partners and to
legal counsel) before any real money is involved anywhere.

## Why testnet-only, and where the real gate still sits

Building and demoing this mechanism doesn't require legal sign-off.
**Operating it with real value does.** Nothing here changes that:

- No real premium is ever collected from a real buyer.
- No real collateral is ever locked by a real, non-test counterparty.
- No real payout ever settles real value.

Everything below uses Arc testnet and faucet USDC (`faucet.circle.com`),
which has zero economic value — so the insurance-classification and
money-transmission questions ADR-001/ADR-013 raise simply don't attach
to *any* of this, including the hedge-premium mechanism (ADR-014),
regardless of which ADR a given piece implements. That's a change from
this doc's own earlier draft scoping, which excluded the hedge-premium
piece as if it were inherently higher-risk — it isn't, on testnet; the
risk was always about real value changing hands, not about which
contract the code lives in. See `docs/erc8004-mvp-verification.md` and
the session history around 2026-09-27 for the full reasoning.

The one thing this build does **not** shortcut: real legal counsel
review of ADR-001/ADR-013 (`docs/phase3-design-decisions.md`) is still
required before any of this touches real money, exactly as
`docs/IDEA.md` §8–9 and `CLAUDE.md` already state. This build makes that
review *easier* — a lawyer can watch a real dispute resolve end-to-end
instead of reasoning about fourteen ADRs in the abstract — it doesn't
replace it.

## Verified facts (not assumed)

| Fact | Value | Verified how |
|---|---|---|
| Arc testnet chain ID | `5042002` | `eth_chainId` against the RPC directly |
| Arc testnet RPC | `https://rpc.testnet.arc.io` | `docs.arc.io/arc/references/rpc-endpoints`, cross-checked with a live `eth_blockNumber` call |
| Arc testnet explorer | `https://explorer.testnet.arc.io` (`testnet.arcscan.app` redirects here) | Already used for `AnchorLog`, `docs/SETUP.md` |
| Gas token | **USDC**, natively — "Arc denominates all transaction fees in USDC, the native gas token" | `docs.arc.io/arc/references/gas-and-fees`, quoted directly |
| ERC-8004 IdentityRegistry (Arc testnet) | `0x8004A818BFB912233c491871b3d84c89A494BD9e` | Real deployed bytecode confirmed via `eth_getCode` |
| ERC-8004 ReputationRegistry (Arc testnet) | `0x8004B663056A597Dffe9eCcC1965A193B7388713` | Real deployed bytecode confirmed via `eth_getCode` |
| ERC-8183 (job escrow) | No shared deployment — reference implementation (`erc-8183/base-contracts`) each integrator deploys their own instance of, UUPS-upgradeable, ships `MockUSDC.sol` for exactly this kind of testing | `erc-8183/base-contracts` README, fetched fresh |
| Faucet | `faucet.circle.com` — real testnet USDC, no cost | Referenced in Arc's own testnet docs |

**Consequence**: we do *not* build or deploy ERC-8004 identity/reputation
— reuse the real Arc testnet deployment, same integration pattern as
`mvp/erc8004_client.py` already proven against Base mainnet, just
pointed at the addresses above. We *do* deploy our own ERC-8183 instance
(expected, standard practice for this EIP) and our own `BondPool` (no
standard exists for it — always ours to build).

## Actors and wallets

Reusing the CDP-managed-wallet pattern already proven for the MVP's
on-chain registration (`cdp.evm.create_account()`, sign via
`account.sign_transaction()`, broadcast via `w3.eth.send_raw_transaction()`
— CDP's own `send_transaction` only relays to a fixed list of named
networks that doesn't include Arc, but signing is chain-agnostic, so
this path works against any EVM RPC).

| Role | Notes |
|---|---|
| Deployer | Deploys `ERC8183` and `BondPool`; funded with faucet USDC for gas |
| Seller agent | Registers on ERC-8004 (Arc testnet), locks collateral in `BondPool` |
| Buyer agent | Registers on ERC-8004, funds a job, optionally buys hedge coverage |
| Committee members (2–3, fixed for this demo) | Vote on the one discretionary-path dispute; not the full eligibility/selection system |

All new accounts, all funded from the same faucet — no reuse of the
Base-mainnet MVP wallets, since this is a different chain and a
different purpose.

## Contracts

- **`ERC8183.sol`** — deployed as-is from `erc-8183/base-contracts`
  (UUPS proxy, OpenZeppelin-based), configured to allow testnet USDC as
  the payment token. Not modified — using the real reference
  implementation is the point.
- **`BondPool.sol`** (new, ours) — implements Epic G in full (G1–G8) and
  the objective-path hooks Epic C needs:
  - Per-seller locked balance (G1), minimum-bond eligibility (G2)
  - `slashObjective()` — Tier 0/1-triggered, automatic, no human call
    (G3, C2, C3)
  - Payout capped at the disputing buyer's own payment; any slash beyond
    restitution routes to the shared pool, never back to the disputer
    (G4, ADR-013 Part B, C4)
  - Hedge premium: purchase (G5), pricing formula (G6), slash-amount
    computation (G7), seller base penalty rate (G8) — ADR-014's formulas,
    implemented directly, no simplification
  - `recordCommitteeVerdict()` — discretionary-path release, callable
    only by the fixed demo committee, same payout-capping rules as the
    objective path (D2f)

## Progress log

**2026-09-27 — environment + local validation, before any testnet deployment.**

- Foundry installed, `contracts-testnet/` project initialized.
- Real `erc-8183/base-contracts` reference implementation installed as a
  dependency (`forge install`), not copied/reimplemented — confirmed it
  compiles standalone first.
- `src/BondPool.sol` written implementing G1–G8, the objective-path hook
  automation, and the minimal discretionary committee — compiles clean
  against the real `IERC8183Hook` interface and OpenZeppelin.
- **8/8 local tests pass** (`test/BondPool.t.sol`), run against a real
  `ERC8183` instance deployed behind a real `ERC1967Proxy` (not a mock of
  ERC8183) on Foundry's local EVM:
  - Objective path: buyer restitution correctly capped at their own
    payment (ADR-013 Part B rule 1); excess slash correctly lands in
    the shared pool, never back to the disputer (rule 3); a second
    reject() attempt on the same job correctly reverts (no double-slash).
  - Discretionary path: a single juror's vote is insufficient
    (quorum = 2 enforced on-chain); a 2-0 upheld vote produces the same
    slash math as the objective path; a 2-0 not-upheld vote leaves the
    seller's collateral untouched.
  - Hedge premium: coverage requires the seller to already be
    hedge-eligible and caps coverage at their locked collateral (ADR-013
    Part C); the premium is retained in the shared pool even when the
    covered job succeeds (ADR-013 Part B rule 2); on a covered failure,
    buyer restitution is capped at the *coverage amount*, not the raw
    job budget.
- **One real bug found and fixed, worth recording**: `vm.prank()` (and
  separately `vm.expectRevert()`) in Foundry only applies to the very
  next external call — evaluating `bondPool.REASON_OBJECTIVE_FAIL()` as
  an argument expression counts as that next call, silently consuming
  the prank/expectRevert before the intended `reject()` call ran. Not a
  contract bug; a real test-authoring pitfall, fixed by fetching the
  constant into a local variable first.

**2026-09-27 — live on Arc testnet, all three scenarios, real (if
worthless) money end to end.**

Deployed for real, verified via `eth_getCode` and read calls, not
assumed from transaction receipts alone:

| Contract | Arc testnet address |
|---|---|
| `ERC8183` implementation | `0x087c06de1b058329FB3b265FBBF556eA2752cf25` |
| `ERC8183` (proxy — this is the live instance) | `0xAC5C72D2F4E633c97314b755761CCB16E44DAFDF` |
| `BondPool` | `0x73B2bE54639BE40FB549A6023798Fee3eF42D681` |

Configured: `USDC` (`0x3600...0000`, Arc's native-USDC ERC-20 interface —
6 decimals, distinct from the 18-decimal native balance used for gas;
verified both independently) allowed as payment token; `BondPool`
whitelisted as an `ERC8183` hook. Seller and buyer registered for real on
Arc testnet's `IdentityRegistry` — agentId `896867` (seller) and `896868`
(buyer), ownership verified via `ownerOf()`.

Funding: each of 6 CDP-managed demo wallets (deployer, buyer, seller,
3 committee members) requested independently from `faucet.circle.com`
(20 USDC each, real testnet funds, zero economic value) — the rate limit
is per-address, so requesting per-actor gave more usable float than one
request plus internal redistribution.

**All three scenarios run live, on-chain, matching the local test suite
exactly:**

1. **Objective path** (job 1, budget 5 USDC, seller collateral 15 USDC):
   evaluator's `reject()` with `REASON_OBJECTIVE_FAIL` automatically
   slashed 10 USDC from the seller (2x penalty rule, capped at
   available); buyer's total gain was exactly 10 USDC (5 USDC native
   `ERC8183` escrow refund + 5 USDC `BondPool` restitution, capped at
   what they paid — rule 1); the other 5 USDC landed in the shared pool
   (rule 3). Seller: 15 → 5 USDC locked.
2. **Discretionary path** (job 2, budget 2 USDC): a single committee
   vote was **verifiably insufficient** — calling
   `executeDiscretionaryVerdict` with only 1 of 2 required votes
   reverted for real, on-chain, proving no single call (not even the
   deployer's) can trigger this payout alone. A second vote met quorum;
   the resulting slash math matched the objective path exactly. Seller:
   5 → 1 USDC locked; pool: 5 → 7 USDC.
   - One real correction made mid-run: after job 2, seller's locked
     collateral (1 USDC) fell below `MIN_BOND` (10 USDC) —
     `purchaseCoverage` correctly reverted with `SellerNotEligible` on
     the first attempt at job 3, a genuine on-chain enforcement of
     ADR-013 Part C, not a bug. Buyer transferred 8 USDC to seller (a
     funding top-up, not part of the mechanism itself) so seller could
     lock enough to clear eligibility again.
3. **Hedge coverage** (job 3, budget deliberately small — 1 USDC —
   against 6 USDC of purchased coverage, 1 USDC premium): premium landed
   in the shared pool immediately and irreversibly on purchase. On
   rejection, buyer's restitution was governed by the **6 USDC coverage
   ceiling, not the 1 USDC job budget** — the core hedge-product claim,
   proven live: buyer's total gain was 7 USDC (1 USDC escrow refund + 6
   USDC coverage payout), seller's remaining 11 USDC collateral was
   fully consumed (11 slashed, 6 to buyer, 5 to pool), final shared pool
   13 USDC.

Every number above was read back from live contract state after the
fact, not inferred from an expected formula — the same discipline as
the rest of this project's verification logs.

## Build sequence

Each step has a concrete, checkable acceptance criterion — matching the
existing backlog's per-story format, not "it compiles."

1. **Environment**: Foundry project under `contracts-testnet/`
   (separate from the single-file, no-toolchain `contracts/AnchorLog.sol`
   convention, since `ERC8183` genuinely needs dependency management —
   OpenZeppelin, a proxy pattern — that `solcjs` alone doesn't handle).
   *Acceptance*: `forge build` succeeds against both contracts.
2. **Fund the deployer**: real faucet USDC into the CDP-managed deployer
   wallet on Arc testnet.
   *Acceptance*: non-zero USDC balance confirmed via `eth_call` on the
   USDC contract, not assumed from the faucet's own success message.
3. **Deploy `ERC8183`**, configure testnet USDC as an allowed payment
   token.
   *Acceptance*: `eth_getCode` at the deployed address is non-empty;
   a read call (e.g. the allowed-token check) returns the expected value.
4. **Deploy `BondPool`**, wired to the same testnet USDC and to the
   deployed `ERC8183` instance's job-completion signal.
   *Acceptance*: same code-presence + read-call check as step 3.
5. **Register seller + buyer** on ERC-8004 (Arc testnet IdentityRegistry),
   reusing the exact `register()`/`setAgentURI()` pattern already proven
   on Base mainnet.
   *Acceptance*: `ownerOf(agentId)` and `getAgentWallet(agentId)` resolve
   correctly for both, on Arc testnet.
6. **Seller locks collateral** in `BondPool`.
   *Acceptance*: `BondPool`'s per-seller balance reflects the real
   on-chain deposit, read back, not inferred from the transaction receipt
   alone.
7. **Objective-path run**: create a job via `ERC8183`, fund it, submit a
   Tier 0/1-failing deliverable, file a dispute, confirm automatic
   slashing.
   *Acceptance*: buyer's on-chain USDC balance increases by exactly the
   restitution amount (not more — checks G4/ADR-013 Part B directly);
   seller's locked balance decreases by the slash amount; the remainder
   (if any) lands in the shared pool, verified by its balance, not
   assumed.
8. **Hedge-premium run**: buyer purchases coverage on the same seller
   before hiring them for a second job, premium is collected and
   confirmed non-refundable regardless of outcome (ADR-013 Part B rule
   2), a Tier 0/1 failure triggers payout up to the coverage amount.
   *Acceptance*: premium payment confirmed on-chain and provably
   retained by the pool even when the covered job succeeds (run once
   with a successful job specifically to prove the premium isn't
   refunded) as well as once when it fails (to prove payout triggers).
9. **Discretionary-path run**: a second, Tier 2/3 dispute (a judgment
   call, not a schema failure), routed to the fixed 2–3-member demo
   committee, a vote recorded, `recordCommitteeVerdict()` releases funds
   per the vote — never a direct call from the deployer.
   *Acceptance*: the release only succeeds when a real quorum of
   committee votes exists on-chain; a direct attempt to call the release
   function from the deployer address, bypassing the committee, is
   confirmed to revert.

## Explicitly out of scope (sequencing reasons, not legal ones)

- **D1a–D4 in full** (tenure/eligibility gating, advertise-and-volunteer
  selection, escalation ladder, collusion detection D3a–g) — these are
  designed to find patterns across real historical dispute volume; a
  testnet demo with a handful of manufactured disputes can't exercise
  them meaningfully either way. Build when real dispute volume exists,
  per ADR-009's own reasoning for evergreen calibration.
- **Epic H** (Organizations, ADR-015) — a layer on top of a proven core
  mechanism, not required to prove the core mechanism itself.
- Any deployment to Arc **mainnet**, or any use of real USDC, by
  anyone, for any reason, before ADR-001/ADR-013 legal review completes.

## Open items to resolve during the build, not before

- Exact `ERC8183` payment-token-allowlist admin call signature — confirm
  against the real contract source once cloned, not the README summary.
- Whether `BondPool` reads job-completion state from `ERC8183` via a
  hook (`IERC8183Hook`) or a separate oracle-style call — the reference
  implementation's hook system looks like the right fit; confirm once
  `ERC8183.sol` is actually in hand.
