# Dev environment setup log

Records what's already been done so a future session doesn't have to
re-derive it or repeat setup steps. Not a memory substitute — this is
current, checkable project state; verify with the commands shown before
trusting it, since sessions/wallets can expire or be recreated.

## Circle CLI

- Installed globally: `npm install -g @circle-fin/cli` → started at `1.1.2`,
  updated to **`1.1.3`** on 2026-09-18 (`circle update --yes`) after
  `circle wallet sign`/`execute` returned `VERSION_BLOCKED`: *"Circle CLI
  1.1.2 is no longer supported for wallet operations."* Wallet-operation
  commands can apparently be version-gated server-side independent of when
  you last installed — don't assume a working install stays working;
  re-run `circle update --yes` if a wallet command suddenly 1.1.2s.
- Terms of Use / Privacy Policy accepted (`circle terms accept`) — required
  once per machine/install before login works. Check with `circle terms show`.
- Logged in as `vasuren@gmail.com`, **both** mainnet and testnet sessions
  (they're separate — see `circle wallet login --help`). Verify current
  status with `circle wallet status`; re-auth with
  `circle wallet login vasuren@gmail.com [--testnet] --init` then
  `circle wallet login --request <id> --otp <code>` if a session has expired.

## Live testnet agent wallet

- Address: `0x752942377f0e8a1e8ccb4273550ac7320c2a6755`
- Chain: `ARC-TESTNET`
- Funded via faucet on 2026-09-17: 20 USDC (both the native-gas and ERC-20
  representations show 20 — Arc exposes USDC as the same asset both ways).
- Re-check anytime with:
  ```bash
  circle wallet balance --address 0x752942377f0e8a1e8ccb4273550ac7320c2a6755 --chain ARC-TESTNET
  ```
- This is the wallet `scripts/poll_spend.py` has been validated against —
  use it as the default target for local testing rather than creating a
  new one, unless you specifically need a second wallet to test
  counterparty/multi-wallet scenarios.

## Known CLI behavior discovered while integrating (not obvious from --help)

- All `circle ... --output json` responses wrap the payload as
  `{"data": {...}}` on success (or `{"error": {...}}` on failure, which
  arrives on stderr with a non-zero exit code). `poll_spend.py`'s
  `run_circle()` unwraps this.
- `circle transaction list` fields differ from what you'd guess from the
  docs prose: `transactionType` is `"INBOUND"`/`"OUTBOUND"` (uppercase),
  `amounts` is a list of strings (not a single `amount` field), and there's
  no explicit token field on a plain transfer — assume USDC on Arc unless
  proven otherwise for a given tx.
- **`circle wallet limit budget` (spending-policy budgets) is mainnet-only.**
  It 403s ("Policy access forbidden") on testnet wallets. `poll_spend.py`
  catches this and skips budget ingestion/alerts rather than failing —
  meaning the "budget low" alert rule is currently untestable on testnet.
  To validate that rule, either test against a mainnet wallet with a policy
  set (`circle wallet limit set`), or stub `ingest_budget`'s return value in
  a test.

## First successful end-to-end run

```
$ .venv/bin/python scripts/poll_spend.py --address 0x752942377f0e8a1e8ccb4273550ac7320c2a6755 --chain ARC-TESTNET --db spend.db
note: spending-policy budgets are mainnet-only; skipping on this wallet
No alerts for 0x752942377f0e8a1e8ccb4273550ac7320c2a6755.
```

Ingested the faucet-funded inbound transaction correctly (verified by
querying `spend.db` directly). No alerts fired, as expected with a single
inbound transaction and no spend history to compare against.

## Phase 2 smoke test (2026-09-18): `circle wallet sign` and `circle wallet execute`

Both commands Phase 2's design depends on (ADR-005's attestation signing,
D1's anchor write) were exercised for real against the live testnet
wallet, confirming the assumptions in `docs/phase2-architecture.md` and
`docs/phase2-backlog.md` hold:

- `circle wallet sign message "<text>" --address <addr> --chain ARC-TESTNET --output json`
  → `{"data": {"signature": "0x99b4c9ab...81b"}}`. Plain signature string,
  no envelope surprises.
- `circle wallet execute "approve(address,uint256)" 0x000...dEaD 0 --contract 0x3600000000000000000000000000000000000000 --address <addr> --chain ARC-TESTNET --output json --estimate`
  confirmed gas estimation works before committing.
- The real (harmless — `approve` of 0 to a burn address, no funds moved)
  committed call succeeded: `state: "COMPLETE"`, a real `txHash`,
  `operation: "CONTRACT_EXECUTION"`, confirmed within ~3 seconds
  (`createDate` → `firstConfirmDate`).

This is the exact mechanism Phase 2's `AnchorLog` writer and version-
attestation signer will use — both now confirmed to work end-to-end
against a real wallet, not just assumed from docs.

## Phase 2 Milestone 2.0 build (2026-09-18)

Built and smoke-tested `ledger/` — schema, generic OTLP/HTTP+JSON ingest
endpoint, version resolver, Merkle batcher, `AnchorLog` deployment/wiring
(D1), and `verify()`. All against synthetic GenAI-conformant spans (real
dogfooding on Claude Code's native OTLP export is still pending — see
below).

### AnchorLog deployed on ARC-TESTNET

- Contract: `0xf3d5ecfb7b89dcc8b181191e5782edb5bb5f6fa2`
- Owner (only address allowed to call `anchor()`): `0x752942377f0e8a1e8ccb4273550ac7320c2a6755`
- Deployment tx: `0x154bb223622595938fb774235dcc999e3685371c88cedb0468546806e9a709f9`
- Source: `contracts/AnchorLog.sol`. Compiled with
  `npx -y solc --bin --abi --optimize -o build/ contracts/AnchorLog.sol`
  (uses `solcjs` via npx — no permanent Solidity toolchain added to the
  project; `build/` is regenerable, not committed).
- Explorer (Blockscout): https://explorer.testnet.arc.io/address/0xf3d5ecfb7b89dcc8b181191e5782edb5bb5f6fa2
  (`testnet.arcscan.app` 301-redirects here — same explorer, friendlier
  domain).
- Note from the CLI on deploy: agent wallets are smart-contract accounts,
  so `msg.sender` inside a constructor is the deployer factory, not the
  wallet — `AnchorLog`'s constructor takes the intended owner as an
  explicit argument for exactly this reason, confirmed correct by
  querying `owner()` post-deploy.

### Two real bugs found by testing, both fixed

**Bug 1 — trusting our own database.** First `verify()` compared a
recomputed root against the *locally stored* `epochs.merkle_root` —
which lives in the same SQLite file an attacker tampering with
`operations` could also tamper with. Fixed by having `verify()` check
`AnchorLog.isAnchored()` on-chain instead of trusting the local table
(`ledger/anchor.py`).

**Bug 2 — one tampered leaf poisoned its whole epoch.** Even after fixing
(1), tampering with *one* operation still made *every* operation in that
epoch report invalid. Cause: the Merkle tree was rebuilt from live
`operations` data on every check, so one changed leaf changes the
recomputed root for the whole batch — correctly detecting *something*
was wrong, but unable to isolate *which* leaf, and unable to still vouch
for the untouched ones. Fixed by freezing each leaf's hash into a new
`epoch_members.leaf_hash` column at sealing time, and having `verify()`
rebuild from those frozen hashes rather than live data — confirmed by
retesting: tampering with one operation now correctly fails only that
operation, siblings stay valid.

**Confirmed working after both fixes:**
- Ingest accepts a valid span, resolves a `weak`-mode version correctly.
- A span missing the required model attribute is rejected with a
  specific reason, not silently dropped.
- `seal_epoch()` builds the tree, seals the epoch, and writes the real
  anchor transaction to `AnchorLog` on ARC-TESTNET.
- `verify(op_id)` returns true for real, untampered, chain-anchored
  operations, and correctly isolates a tampered one from its siblings.

D2 (retry logic for a failed anchor write) is implemented
(`anchor_pending_epochs` in `ledger/batcher.py`) but not yet exercised
against a real failure.

## Identity binding on ingest (2026-09-18)

Milestone 2.0 originally accepted a POST from anyone, claiming to be any
agent — `agent_versions.agent_identity` existed in the schema but sat
NULL, unused. Fixed:

- **`circle wallet sign` does not produce a plain-ecrecoverable signature**
  — confirmed empirically, not assumed: recovering an address from a
  known-good signature via `eth-account`'s standard EIP-191 path returned
  the wrong address. Root cause: Circle agent wallets are smart-contract
  accounts (the same fact the `contract deploy` command warns about for
  `msg.sender`). Verification instead uses **ERC-1271** —
  `isValidSignature(bytes32,bytes)` called on the wallet contract itself,
  confirmed by querying it directly: it returned the magic value
  `0x1626ba7e` for the real signature from the earlier `circle wallet
  sign` smoke test. `ledger/auth.py` implements verification this way —
  on-chain, via `circle contract query`, the same pattern already proven
  for `AnchorLog`, not a local crypto library.
- Added `eth-utils` as the project's first third-party dependency (see
  `requirements.txt`) — only for `keccak256`, to compute the EIP-191 hash
  being checked. `eth-account` was tried first, found unnecessary once
  the ERC-1271 approach was confirmed, and removed again.
- A second, subtler bug caught before it shipped: `version_id` was
  originally hashed from model+shape only, not identity — two different
  (verified) agents producing the same model+shape combination would
  have collided onto the same `version_id` and silently inherited
  whichever one got there first. Fixed by folding `agent_identity` into
  the hash itself (`ledger/resolver.py`).
- **The tension this created, and how it was resolved**: requiring every
  submission to be signed conflicts with Epic B1's "point your existing
  exporter at us, zero new code" promise, since a stock OTel exporter has
  no concept of Circle wallets. Resolved with a local signing forwarder
  (`ledger/forwarder.py`) — a stock exporter points at the forwarder
  instead of the real endpoint (a config value, not a code change), the
  forwarder signs on its behalf, and forwards on. Confirmed working:
  an unsigned request straight to `ledger/ingest.py` gets `401`; the same
  request through the forwarder succeeds and correctly records the
  signing wallet as `agent_identity`; a forged wallet claim with a bogus
  signature gets `401`.

## Real Claude Code dogfood attempt (2026-09-18) — inconclusive, and why

Pointed a fresh, non-interactive `claude -p` invocation's native OTLP
export at the forwarder
(`CLAUDE_CODE_ENABLE_TELEMETRY=1`, `OTEL_EXPORTER_OTLP_ENDPOINT`, etc.).
**Nothing arrived** — confirmed with a raw, unauthenticated listener on
the target port (bypassing our own forwarder/ingest code entirely) that
saw zero HTTP requests of any kind during the run. This isolates the gap
to Claude Code's own export behavior, not a bug in `ledger/`.

Checked against Claude Code's own documentation rather than guessed
further: *"the first metric export happens after one minute... if you're
using headless mode with the `-p` flag and running short-lived sessions,
this could explain why no data is being received if the process exits
before the export interval completes."* Overriding
`OTEL_METRIC_EXPORT_INTERVAL` and `OTEL_BSP_SCHEDULE_DELAY` to 1 second
didn't produce a different result in this pass — either those env vars
don't cover the code path a quick `-p` call exits through, or Claude
Code's telemetry is metrics/logs-oriented (cost, token usage, session
counts) rather than emitting rich GenAI-semconv trace spans on the
`/v1/traces` signal our ingest listens on at all. Not resolved this pass.

**Next honest options**, not yet tried: an interactive session held open
past the export interval; the `console` exporter to confirm spans are
generated locally at all before worrying about delivery; or dogfooding
via Traceloop-wrapped direct Anthropic API calls instead, which controls
its own flush behavior more predictably than Claude Code's telemetry
timing.

## Traceloop/Anthropic instrumentation — source-verified, not yet live-tested (2026-09-18)

No `ANTHROPIC_API_KEY` (or any provider key) is available in this
environment, so a real live call hasn't been made. Before asking to spend
API credits on a test, installed `opentelemetry-instrumentation-anthropic`
+ `traceloop-sdk` (heavier than we'd want to keep permanently — see note
below) and read its actual source rather than guess at its behavior:

- `GEN_AI_REQUEST_MODEL = "gen_ai.request.model"`,
  `GEN_AI_RESPONSE_MODEL = "gen_ai.response.model"` — exact match to what
  `ledger/ingest.py` requires for acceptance.
- `use_attributes=True` is the **default** (the span-*events* path is
  opt-in only, and its own deprecation warning confirms attributes are
  "the current OTel GenAI spec"). It serializes
  `gen_ai.input.messages`/`gen_ai.output.messages` via `json.dumps(...)`
  as a string attribute — exactly the shape `flatten_attributes()` in
  `ledger/ingest.py` already handles. Our Milestone 2.0 scoping decision
  (handle attribute-based content now, span-events as a fast-follow)
  covers this library's real default behavior, confirmed from source, not
  assumed.
- One real but minor divergence: span names are `anthropic.chat` /
  `anthropic.completion`, not the generic `chat`/`invoke_agent` names
  from the OTel semconv spec. Doesn't break acceptance (`record_span`
  doesn't gate on span name), but means `GENAI_SPAN_NAMES` in
  `ledger/ingest.py` won't match real-world span names from this library
  — `operation_type` ends up storing the literal name instead, which is
  harmless but worth knowing.

**Dependency note**: `traceloop-sdk` pulls in instrumentation for dozens
of providers — much heavier than the single-purpose `eth-utils`
dependency added earlier. Installed for source inspection; not added to
`requirements.txt` since we don't need the whole package to just verify
shape. If a live test happens, a real integration would more likely
depend on `opentelemetry-instrumentation-anthropic` alone.

## Not yet done

- No outbound/spend transactions exist on this wallet yet, so the spike and
  new-counterparty alert rules are unverified against real data — only
  checked to not crash on empty history. Send a couple of test transfers
  out of this wallet to a second address to exercise those paths.
- `spend.db` is local test output, not committed to any VCS (no git repo
  exists in this project yet).
