# atesta.io redesign — plan (not yet executed)

Written 2026-09-20. Captures the plan discussed before any code changes,
so it survives to whenever the repo work actually happens. Source is
GitHub (per the user); the repo itself has not been opened in this
project — the plan below is content/IA only, no code.

## Why

atesta.io currently ships one product end to end: Supply Chain Risk
Intelligence (LkSG/CSDDD/EUDR/CBAM compliance for German industrials,
tagline "Trust, verified."), with a sample-report demo, a live JWT/EBSI
credential verification tool, a competitive comparison table, and a
lead-capture form all live at the root domain.

Atesta is now also the parent brand for Vadium (see
`phase3-design-decisions.md`, `docs/IDEA.md`), the agent-commerce trust
layer. Leaving the current homepage as-is would put a first-time visitor
into the supply-chain product when the near-term focus, and the thing
design partners/investors will be pointed at, is Vadium. The fix is
repositioning, not deletion: move the existing product to a sub-page,
keep it fully live, and let the homepage introduce Atesta as the parent
brand with Vadium in the lead position.

## Target site map

- **`/` — Atesta (parent brand).** Positions Atesta as the trust/
  verification company behind multiple products. Tagline "Trust,
  verified." stays — generic enough to cover both lines. Leads with
  Vadium; Supply Chain Risk Intelligence gets a smaller secondary
  section/card linking out.
- **`/vadium` — the Vadium product page.** Web counterpart to the
  design-partner deck: problem, solution, "by Atesta," design-partner
  CTA, reusing the existing lead-capture form component.
- **`/supply-chain` — today's homepage content, relocated as-is.**
  Sample-report demo, JWT/EBSI verification tool, comparison table, its
  own lead-capture form. Not rebuilt, just moved.
- **Nav / footer.** Two top-level products (Vadium, Supply Chain) or a
  simple switcher; Impressum and other legal pages stay global,
  unaffected by the split.

Decision already made: demote the supply-chain content to a sub-page and
keep it live there, rather than taking it fully offline.

## Migration mechanics — the part that's easy to get wrong on a live, indexed site

- **301 redirects** from every current root-level supply-chain URL to
  its new `/supply-chain/...` path — otherwise search ranking is lost
  and any already-shared link (the sample-report demo especially)
  breaks.
- **sitemap.xml / robots.txt** updated to the new paths.
- **Canonical URLs and OpenGraph tags** on the moved pages updated to
  point at their new location, not the old root.
- **Lead-capture form backend** — confirm the submission endpoint
  doesn't depend on URL path before shipping.

## Next step

~~Point Claude at the GitHub repo when ready.~~ Done — the real site repo
is `github.com/atesta-dev/atesta-site`, cloned locally at
`/Users/swathiselvaraju/code/atesta-site`. Confirmed 2026-09-30: it
deploys via **Cloudflare Workers Builds** — every push to `main` deploys
`atesta.io` live automatically (no manual `wrangler deploy`, no GitHub
Actions file in the repo; the build runs on Cloudflare's side). One real
gotcha: Cloudflare edge-caches the exact `/` path aggressively
(`cf-cache-status: HIT`), so a change can take a short while to show on
a plain fetch even though it's already live.

---

## Vadium site plan (2026-09-30) — full content map and narrative arc

This section supersedes the "starting proposal" note above with a
concrete plan, built from everything produced this session: the
explainer video, the three Claude Artifacts, and the existing ADRs/
positioning docs.

### Site map

| Location | What | Status |
|---|---|---|
| `atesta.io` (root) | Atesta parent brand, leads with Vadium | To build |
| `atesta.io/vadium` | **Main Vadium page** — the flagship | To build |
| `atesta.io/vadium/walkthrough` | Interactive scenario demo | Port from Artifact, needs a fix (below) |
| `atesta.io/vadium/proof` | "Three Real Disputes" — real testnet evidence | Port from Artifact, ready as-is |
| `atesta.io/vadium/mechanism` | Curated public subset of "Inside Vadium" | Needs a curation decision (below) |
| `atesta.io/vadium/playground` | Link/embed to the live interactive playground | Blocked — `vadium-playground` has no real hosting yet (see below) |
| `vadium-leaderboard.atesta.io` | **New** — live public ranking of registered agents by trust score | To build, separate subdomain (dynamic app, not a static page) |
| `atesta.io/supply-chain` | Today's homepage content, relocated as-is | Already planned above (redirects, sitemap, OG tags) |

`vadium-leaderboard.atesta.io` gets its own subdomain rather than a `/vadium`
sub-path because it's a live data app (needs a backend querying the
real ERC-8004 registry + Vadium's evidence ledger), not a static
marketing page — same reasoning as `app.atesta.io` being separate from
the static site.

### Content inventory — where everything already built goes

| Existing asset | Destination |
|---|---|
| `vadium_explainer_v4.mp4` (2:14 explainer video) | Hero of `/vadium` — now self-contained with intro/outro context cards, doesn't need extra scaffolding on the page to make sense |
| "Vadium Walkthrough" Artifact | `/vadium/walkthrough`, after the Atlas fix |
| "Three Real Disputes" Artifact | `/vadium/proof`, verbatim — already clean, correctly branded, no fixes needed |
| "Inside Vadium" Artifact | Curated subset → `/vadium/mechanism` (see below) |
| `docs/plain-english-primer.md` | Rewritten into the `/vadium` page's own "how it works" section copy (notary-stamp/court/insurance analogies) |
| `docs/IDEA.md` positioning ("Amazon of agentic services," non-discretionary design) | `/vadium` hero and value-prop copy |
| Vadium Design System (palette/type from the Artifacts: parchment `#f2ede1`/`#f7f3ea`, verdigris `#2f6b58`/`#4a8c76`/`#63c1a4`, bronze `#8a5a24`, Space Grotesk + Source Serif 4 + IBM Plex Mono) | Applied consistently across every new `/vadium/*` page — this is already a real, working design system, not something to invent from scratch |
| `vadium-lookup` (live x402-payable API, already deployed) | Linked from `/vadium` as a "try it live" / developer entry point |
| `vadium-playground` | Linked from `/vadium/playground` once it has real hosting |

### Two content decisions still needed before building

1. **The Atlas naming fix** (flagged earlier, still unresolved): both "Vadium
   Walkthrough" and "Inside Vadium" name the buyer-agent "Atlas" — the
   same name deliberately dropped from the video for causing confusion
   between named agent systems. Recommend renaming to just "the buyer
   agent" or reusing "Meridian's agent" in both before publishing, so
   the whole site tells one consistent story with the video.
2. **"Inside Vadium" is self-marked private** and documents real attack
   scenarios (self-dealing exploits, juror collusion mechanics, custody/
   regulatory cost specifics) not meant for external eyes. Recommend
   publishing only its "ecosystem" mode (the five roles — marketplace,
   seller, buyer, juror, Vadium — and what each can/cannot do) as
   `/vadium/mechanism`, and dropping the stress-test attack-scenario
   cards entirely from the public version. That mode alone is genuinely
   useful public content explaining *why* the system is trustworthy,
   without exposing the internal red-team playbook — especially since
   real legal review of ADR-001/ADR-013 is still outstanding (see
   CLAUDE.md).

### `vadium-playground` hosting — decided 2026-09-30

Choice was between the Hetzner VPS (same box as Paperclip) or Render
(same platform as `vadium-lookup`). **Recommendation: Render**, as a
"Static Site" service — purpose-built for exactly this (a Vite build
with no backend), gets git-push-to-deploy for free the same way
`vadium-lookup` already does, and keeps it isolated from Paperclip's
VPS so one going down doesn't take the other with it. Hetzner remains
the fallback if Render turns out not to fit once we're actually in it
(e.g. if the playground ends up needing a real backend later, not just
static Vite output).

Once deployed, gets its own subdomain: `vadium-playground.atesta.io`.

### `vadium-lookup` — bringing it into the site properly

Already live on Render with a real, working API. Two changes:

1. **Give it a subdomain**: `vadium-lookup.atesta.io`, via a CNAME to the
   existing Render service (Render supports custom domains natively —
   no migration, no rebuild, just DNS + one dashboard entry, same
   mechanism discussed for the VPS earlier).
2. **Weave it into the narrative, not just link it generically.**
   `vadium-lookup` *is* the real, callable version of the trust-record
   check dramatized in the Walkthrough's "Discover" step (Atlas checking
   Nomad Labs before paying) and referenced in Three Real Disputes. So:
   - **`/vadium/walkthrough` and `/vadium/proof`**: add a "this is a
     real, queryable endpoint" callout with an actual example call
     against `vadium-lookup.atesta.io`, right next to the illustrated/recorded
     version of the same check — ties the story directly to something
     the visitor can run themselves, right there.
   - **`/vadium/playground`**: present `vadium-lookup` and
     `vadium-playground` together as the developer toolkit — one for
     querying trust data, one for exercising the full on-chain flow —
     rather than as two disconnected links.

### Updated site map

| Location | What | Status |
|---|---|---|
| `atesta.io` (root) | Atesta parent brand, leads with Vadium | To build |
| `atesta.io/vadium` | Main Vadium page | To build |
| `atesta.io/vadium/walkthrough` | Interactive scenario demo | Port from Artifact + Atlas fix + lookup callout |
| `atesta.io/vadium/proof` | "Three Real Disputes" | Port as-is + lookup callout |
| `atesta.io/vadium/mechanism` | Curated "Inside Vadium" (ecosystem mode only) | Needs the curation pass |
| `atesta.io/vadium/playground` | Playground + Lookup, presented as one developer toolkit | Blocked until Render deploy lands |
| `vadium-playground.atesta.io` | The live interactive playground | To deploy (Render) |
| `vadium-lookup.atesta.io` | The live x402-payable lookup API | To alias (CNAME to existing Render service) |
| `vadium-leaderboard.atesta.io` | Live ranking of registered agents | To build |
| `atesta.io/supply-chain` | Current homepage, relocated | Already planned above |

### The narrative arc — how the whole property tells one story

The site is built as a funnel, each stage handing off to the next:

1. **Land on `/vadium`** — the video tells the concrete, human story
   (Meridian's problem, Vadium's resolution) in under 2.5 minutes.
   Establishes *why this matters* before any mechanism talk.
2. **"How it works" section, same page** — bridges from story to
   mechanism at a plain-English level (the primer's analogies).
3. **Click into Walkthrough** — same story, now interactive. The
   visitor picks the outcome themselves (job goes fine vs. job goes
   wrong) — turns passive watching into active engagement.
4. **Click into Proof** — real transaction hashes, real contract
   addresses, real testnet agent IDs. This is where "not illustrative"
   actually lands — the visitor can independently verify every number.
5. **Click into Mechanism** — for the technically curious: why no
   single party (Vadium included) can self-deal, without the internal
   attack-scenario detail.
6. **Leaderboard** — the "living proof": an always-updating page of
   real registered agents, reinforcing this is an operating system, not
   a static pitch.
7. **Playground** — for developers ready to actually build against it.
8. **Design-partner CTA** — convert interest into an actual
   conversation, reusing the existing lead-capture form pattern already
   on the current site.

Story → try it yourself → proof it's real → understand why it's
trustworthy → see it live and growing → build with it → talk to us.
