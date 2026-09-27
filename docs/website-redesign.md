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

Point Claude at the GitHub repo when ready. The work is then mechanical:
move the current homepage's routes/pages under `/supply-chain`, add the
redirects, build the new homepage and `/vadium` page, update nav and
sitemap. The product split above (parent brand + two product pages) is
the starting proposal, not a locked decision — open to changing it (e.g.
a product switcher instead of a homepage-with-a-secondary-card) once it
can actually be seen in the real site.
