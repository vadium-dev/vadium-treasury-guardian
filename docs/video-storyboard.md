# Vadium explainer video — storyboard (v2: human scenes, not screens)

## Production log (started 2026-09-29)

Actual generation method differs from the "Soul ID" line above: Soul ID
training got stuck in Higgsfield's queue for 15+ minutes (likely platform
congestion, not our setup — it did eventually clear), so shots are being
produced with **image-reference conditioning** instead — a per-character
photorealistic reference sheet (front/3/4/left/right/full-body), generated
once via Seedream 5.0 lite and attached as a "Reference" to each Seedance
2.5 video generation. Validated on Shot 3 before committing to the rest:
identity held up well (same face, hair, beard) with no Soul ID involved.
Trained Soul ID characters (Priya, Dae, Marcus) did finish separately and
are available if a shot needs revisiting with tighter consistency.

**Continuity bug caught and fixed after Shots 1–2's first pass**: character
references alone don't hold the *environment* consistent — Shot 1 and
Shot 2 rendered visibly different dispatch floors (different desk
layout, different windows) despite matching faces, because nothing
constrained the set. Fixed the same way as character identity: generated
one canonical environment reference image (empty dispatch floor, wide
establishing shot, Seedream 5.0 lite) and now attach it as a *third*
reference alongside the two character sheets for every dispatch-floor
shot (1, 2, 5, 6). Shots 1 and 2 were regenerated against it.

**Shot count is 9, not 8 (corrected 2026-09-30)** — only Shot 6 splits
into two (6a/6b), once the natural-pacing pass (below) showed its full
dialogue couldn't fit one take. Shot 2 was briefly split into 2a/2b too,
on a first pass, but that was a mistake — see the feedback log below —
and has been merged back into a single Shot 2. See "Shot durations"
section for the per-shot reasoning.

**Production method for 6a→6b: Higgsfield's "Extend Video" (under Edit
Video), not two independently generated clips.** The split isn't a real
scene cut — same desk, same two people, no camera or angle change was
ever intended, it exists purely because one 30s-capped generation call
can't hold the full 33s of dialogue. Generating 6a and 6b as two separate
clips risks a visible seam — posture, lighting, or framing drifting
slightly between two independent generations that then have to be
matched up in an editor. Extending the first clip forward instead
continues the actual same shot, so there's nothing to match up. Reserved
for exactly this one case — every other shot (1, 2, 3, 4, 5, 7, 8)
already fits one natural take or is a genuinely distinct beat (different
location or moment), and extending those would just be complexity
nobody asked for. One thing to verify once unblocked, not yet confirmed:
whether an extended clip's *combined* length is still capped at 30s
total, or whether the cap applies per-generation-call — matters for 6a
(26s) + 6b (8s) = 34s combined, which would exceed a 30s combined cap if
one exists.

| Shot | Status | Target duration | Notes |
|---|---|---|---|
| 1 — Cold open | **done (v4)** | 12s | Adds "Nomad Labs" naming to bridge into Shot 2 — job `16a67ad9`. Pronunciation of "Nomad Labs" unresolved (see note above) |
| 2 — Hiring decision | **done (v3, via Extend)** | 22s | Extend from Shot 1 v4, Vaydium fix applied — job `0375f9e9` |
| 3 — Out on the road | **done, no change** | 5s | Marcus solo, reference-conditioned — already natural, no dialogue |
| 4 — Something's wrong | **done (v2)** | 10s | Regenerated with a new house-exterior environment reference to fix within-shot drift — job `72f1294d` |
| 5 — Filing it | **done (v2)** | 17s | Job `45e27f45` — Vaydium fix applied, pronunciation in full-shot context unconfirmed |
| 6a — The resolution, pt 1 | **done (v3, "same-desk")** | 28s | Job `00c8788a` — reuses Dae's desk (spatial-continuity fix), Vaydium fix + full-refund bridge line applied |
| 6b — The resolution, pt 2 | **done (v2, Extend from 6a v3)** | +8s | Job `602dcdae` — "back and forth" de-hyphenation fix applied |
| 7 — End of day | **done, no change (deprioritized)** | 5s actual (8s was the derived target) | Kept as-is by explicit decision — the pacing mismatch was accepted, not fixed |
| 8 — Closing card | **done, no change (deprioritized)** | 5s actual (9s was the derived target) | Kept as-is by explicit decision — the pacing mismatch was accepted, not fixed |

**Three rounds of user feedback after the first full pass (2026-09-30):**
1. **Pacing** — shots with dialogue felt cramped and hurried at Seedance
   2.5's default 5s duration. Confirmed the model actually supports
   4s-30s (found via the "Duration" control, a free-form stepper hidden
   below the prompt box, not a fixed preset) — every prior shot was
   generated at the default without ever checking this. Followed up with
   a full word-count/pace pass per shot (see "Shot durations" above)
   rather than just picking a bigger round number.
2. **Overcorrected the pacing fix onto Shot 2** — the first pass of that
   word-count pass found that Shot 6's full dialogue (~33s) exceeds the
   30s cap and needs splitting, then wrongly generalized the same
   conclusion onto Shot 2, whose full dialogue is only ~22s — well under
   the cap. Split it into 2a/2b anyway, for no real reason. Caught
   directly by the user ("in cases where we can do it in one shot, why
   break it? ... 2a and 2b together is 22s why not generate as one
   shot?") — correct catch, merged back into a single Shot 2. Only Shot
   6 actually needs the 30s-cap split; that's the one case, not a
   pattern.
3. **Atlas/Vadium brand confusion** — the original dialogue named two
   AI systems (Atlas: found the vendor; Vadium: checks the dispute) with
   no way for a first-time viewer to tell if they're related. Fixed by
   dropping "Atlas" entirely: Shot 1's sourcing act is now unnamed/generic
   ("our sourcing agent"), and **Vadium's first mention moved up to Shot
   2** ("Vadium checked them...") — the "checked" line is accurate to
   what Vadium actually does, unlike Shot 1's "found us someone" (an
   active-matchmaking claim Vadium should never be shown making, per the
   Amazon-of-agents positioning: Vadium surfaces data, it doesn't pick
   winners).

**Unblocked (2026-09-30)**: the CAPTCHA/bot-detection challenge is gone —
confirmed cleared on a fresh check of the Higgsfield tab, no verification
prompt showing. Also switched production from browser automation to
Higgsfield's native MCP tools (available this session, weren't earlier),
which is both more reliable and lets outputs be organized properly.

**Organizing final takes separately from the old first-pass clips**: all
prior generations (Shot 1 v1/v2 at the old 5s default, the original
Shot 2a/2b split, etc.) live unfiled in Higgsfield's general history —
there's no rename/move API for existing generations, so rather than try
to relabel them in place, every new final-pass generation from here on
is filed into a dedicated Higgsfield project, **"Vadium Explainer —
Final"** (project `82b3ea6a-6453-4327-a3f9-e30ef69c59df`). Anything not
in that project is an old/superseded pass — check there first, not the
unfiled history, to avoid confusion.

**Shot 1 v3: done.** Generated via Seedance 2.5, `omni_reference` mode,
three image references (Priya element, Dae element, the canonical
dispatch-floor environment reference), 12s, 1080p, audio on — job
`d56211b2-3a56-4672-9a5a-f031c180ce8b`, filed in the Final project.

**Real continuity bug caught: Shot 1 → Shot 2 position jump (2026-09-30).**
Generated Shot 2 independently (omni_reference, same 3 references as
Shot 1) and the user caught a jump: Priya's blocking didn't match between
shots. Verified with Higgsfield's video-analysis tool — Shot 1 actually
ends with Priya *standing* beside Dae's desk, in a close profile
two-shot; the independent Shot 2 generation opened with her already
*perched on the desk edge*, no transition. Reference-image conditioning
only approximates a consistent scene — it doesn't guarantee the exact
end pose of the prior shot carries forward. **Fix: generate Shot 2 as an
Extend Video continuation of Shot 1's actual job**, not an independent
generation — this starts from Shot 1's literal last frame, so there's no
pose to jump from/to. Confirmed via cost preflight that Seedance accepts
a 22s extension on a 12s source (34s combined) without erroring, at the
same 12 credits/sec rate as any other generation — no extra cost for the
more robust method. Shot 2 v2 generated this way — job `159376bc`,
continuity re-verified via video analysis before calling it done.
**Same logic likely applies to 6a → 6b** (already planned as an Extend)
and is the reason Extend was reserved for genuinely continuous scenes in
the first place — this bug is exactly the failure mode Extend avoids.

**All 9 shots generated and downloaded (2026-09-30)** — local copies in
`video-shots/` (gitignored, not committed): shot1_v3, shot2_v2_extend,
shot3, shot4_upscaled, shot5, shot6a, shot6b, shot7. Shot 8 intentionally
left at its original 5s take (deprioritized).

**Pronunciation bug found: Seedance mispronounces uncommon/invented
words.** Shot 1 rendered "dispatchers" as "dash-packers" (confirmed via
Higgsfield's video-analysis transcript). Separately, the user caught
Shot 5's audio mispronouncing "Vadium" itself — the actual brand name,
a higher-priority fix given the video's job is to make that name stick.
Shot 6a has the same "Vadium checked..." line and likely the same risk,
not yet confirmed by ear.

**Full redo pass complete (2026-09-30) — all 9 shots now generated.**
Final state, all filed in the "Vadium Explainer — Final" project:
- Shot 1 v4 (`16a67ad9`): adds "...found us Nomad Labs" to Priya's line,
  bridging into Shot 2.
- Shot 2 v3 (`0375f9e9`): redone as Extend from Shot 1 v4 (not v3, the
  prior Shot 1), carries the Vaydium respelling on its own "Vadium
  checked them" line proactively.
- Shot 3: unchanged.
- Shot 4 v2 (`72f1294d`): regenerated with a new house-exterior
  environment reference (previously had none) — fixes the within-shot
  drift.
- Shot 5 v2 (`45e27f45`): Vaydium respelling fix.
- Shot 6a v3 (`00c8788a`, "same-desk" version): regenerated to reuse
  Dae's established desk instead of introducing a new, ungrounded
  "Priya's desk" — see the spatial-continuity note below. Carries the
  Vaydium fix and a new bridge line ("Vaydium already came back — full
  refund?...") connecting it back to Shot 5's promise to flag things.
- Shot 6b v2 (`602dcdae`): Extend from Shot 6a v3, with "back-and-forth"
  de-hyphenated to "back and forth" (validated fix).
- Shot 7, 8: deprioritized by explicit decision, left at original takes.

**New spatial-continuity finding (2026-09-30):** shared reference images
give consistent *look*, not a persistent floor plan. Shot 6a originally
introduced "Priya's desk" — a location never established anywhere else —
which the user correctly flagged as ungrounded relative to the geography
implied by Priya's entrance in Shot 1. Fixed by reusing Dae's desk (the
one space already rendered consistently across Shots 1/2/5) instead of
inventing a new sub-location. Full writeup in
`docs/ai-video-production-learnings.md` (#11, #12) — also covers why
Extend Video can't be used to bridge a real time-skip (it only continues
a single uncut take; forcing a lighting change into an extension look
like an impossible instant jump, not a clean cut).

**New pronunciation finding, unresolved (2026-09-30):** even validated
respellings don't hold reliably in full-shot context. In the actual
shots, "Nomad Labs" (plain English, no hyphen) came out as "Nobad Labs,"
and "Vaydium" (the respelling that tested clean in isolation) came out
as "Vaydum" — both proper nouns losing/swapping a syllable toward a more
common-sounding neighbor. This held even though an earlier isolated test
of "Vaydium" in a short neutral-delivery sentence sounded correct — the
difference may be delivery style (Shot 6a is directed as a slow,
deliberate "thesis statement," unlike the neutral test line) or simply
that proper nouns are inherently higher-risk regardless of spelling.
**Not yet fixed** — budget ran out (13.8 credits remaining) before this
could be diagnosed further. Next step, once resourced: rerun the cheap
isolated-test method (see learnings doc) but matching the *actual*
delivery direction of the shot in question, not a neutral line.

**Tested and rejected: Higgsfield's `dubbing` tool (English → English) as
a cheap re-synthesis pass.** Tried on Shot 1 (the shortest affected clip,
36 credits vs. 144 for a full regen) as an experiment before committing
to redubbing the Vadium lines. Result, confirmed by ear (2026-09-30):
**failed on both counts** — "dispatchers" still came out as
"dash-packers" (dubbing transcribes the *actual spoken audio* first, so
it faithfully reproduced the existing error instead of fixing it, exactly
the risk flagged before trying it), and it introduced a new, worse
artifact: Dae's mouth moves during Priya's line — cross-character
lip-sync desync that wasn't there before. Test file deleted, **dubbing
is not a viable fix for pronunciation issues on this project** — don't
retry it. The only remaining path for Shot 5's "Vadium" mispronunciation
(and Shot 6a's, if it has the same problem) is a full regeneration with
an adjusted prompt (e.g. a phonetic respelling like "Vay-dee-um" in the
spoken dialogue text, on-screen spelling unaffected) — untested, and
still no guarantee against Seedance's speech synthesis being stochastic.

**Remaining work**: generate 2, 4, 5, 6a, 6b, 8 at their derived natural
durations (see table above) — 1 is now done, 3 and 7 are already right
and don't need redoing; then pull all 9 clips, edit into one
sequence (standard NLE — CapCut/Premiere, not a generation step), lay
the separately-sourced instrumental track underneath per the
storyboard's own music production note, and confirm whether Shot 8's
voiceover actually rendered as audio or only as on-screen text. Expect
a ~1:57 total runtime, not the ~40s an all-5s cut would have produced —
that's a real, deliberate increase worth flagging as a decision, not
just letting it happen.


## Structure v3 — intro hook + inline label + outro payoff (2026-09-30)

Real gap found after watching the full stitched cut: the video never
establishes the premise for a viewer with zero context — what an
"agentic" vendor even is, who Nomad Labs is, or what Vadium actually
does beyond "checks things and issues refunds." A pure outro explainer
was considered and rejected in favor of a combination structure, because
a pure recap at the end still leaves the viewer confused *during* the
7-shot story, and a pure intro would spoil the "aha" of Vadium's name
being introduced organically in Shot 2's dialogue. Locked-in structure:

**Intro (before Shot 1, ~9-10s, plain text cards, no Vadium mention yet
— sets up a question, doesn't answer it):**
> Card A — "AI agents now hire other AI agents to get real work done."
>
> Card B — "How do you know they'll deliver? And what happens when they
> don't?"
>
> *(cut straight to Shot 1 — no further setup)*

**Inline (Shot 2, lower-third overlay the moment Dae says "Nomad Labs" —
zero added runtime):**
> "NOMAD LABS — an autonomous logistics network"

**Outro (after Shot 7, replacing the old single-card Shot 8 — now a
payoff tied to the specific story just watched, not a generic recap):**
> Card 1 — "Vadium checked Nomad Labs before Meridian ever hired them."
>
> Card 2 — "When the delivery didn't match what was promised, the
> refund happened automatically."
>
> Card 3 (unchanged, the original Shot 8) — "See exactly what happened,
> on-chain." → Vadium logomark → "VADIUM, BY ATESTA"

**Design refinement (2026-09-30): dropped the persistent Vd/VADIUM
logomark from every intro/outro card.** Reserved it for the existing
closing card only. Reasoning: the consistent parchment/verdigris color
and type system already reads as "one coherent piece" without repeating
the literal logo four times, and holding the actual brand mark back
until the one closing moment makes that reveal land harder rather than
feeling already-seen. Brand consistency came from the shared visual
language, not from repeating the mark itself.

**Revised and reassembled (2026-09-30): `video-shots/vadium_explainer_v4.mp4`
(2:14), current final.** Three fixes on top of the first assembly (plus
the logomark removal above):

1. **Real aspect-ratio bug found and fixed.** The v2 assembly
   (`vadium_explainer_v2_with_context.mp4`) had the entire video
   playing back horizontally stretched. Root cause: the new title cards
   were built from browser screenshots that weren't natively 16:9, and
   `scale=1920:1080` alone doesn't force square pixels — ffmpeg carried
   the screenshot's original aspect ratio through as SAR/DAR metadata
   despite the pixel dimensions reading 1920x1080. Since concat with
   `-c copy` takes its aspect signaling from the first clip, and the
   first intro card was one of the affected files, that wrong ratio
   applied to the *entire* merged file — original correctly-shot 16:9
   footage included. Fixed by adding `setsar=1:1` explicitly to every
   card's scale filter and verifying `SAR 1:1 DAR 16:9` on the final
   output before calling it done, not just on individual pieces.
2. **Shot 5 → 6a transition** — the hard cut read as jarring (Priya
   "suddenly" in a new position after having just walked out). A text
   transition card was added between them rather than another video
   generation: "Later that day — all forty routes complete." — worded
   to ground the time-skip in the delivery operation completing (a full
   day's worth of routes), not in "waiting for Vadium," which would
   have misrepresented what's actually happening off-screen.
3. **Character intro labels** — Priya, Dae (both in Shot 1) and Marcus
   (Shot 3) now get a lower-third the first time they appear, in the
   same visual language as the Nomad Labs label (dark bar, verdigris
   accent stripe, bold name + role): "PRIYA — Meridian Ops Lead," "DAE —
   Dispatcher," "MARCUS — Delivery Driver." Built with the same
   `drawtext`/`drawbox` ffmpeg approach as Nomad Labs, not a screenshot,
   so this didn't carry the aspect-ratio risk. One real escaping bug hit
   here too: an apostrophe in "Meridian's Ops Lead" broke ffmpeg's
   drawtext filter parsing and leaked raw filter syntax onto the frame
   as literal text — fixed by removing the apostrophe ("Meridian Ops
   Lead") rather than fighting filter-string escaping. Worth remembering
   for any future drawtext work: avoid apostrophes/quotes in overlay
   text entirely rather than trying to escape them.

`vadium_explainer_v2_with_context.mp4` (aspect-ratio bug) and
`vadium_explainer_v3.mp4` (superseded by the logomark removal above) are
kept for reference but should not be used — `v4` is current.

**Built and assembled (2026-09-30)**: `video-shots/vadium_explainer_v2_with_context.mp4`
(2:11 total). Card visuals built as HTML/CSS (parchment `#f2ede1`
background, verdigris-green `#4a8c76` accent, small persistent "Vd" +
"VADIUM" brandmark on every intro/outro card so the brand is present
throughout, not just at the very end) — served locally, captured via
browser screenshot, converted to video with a 0.6s fade-in/fade-out each
via ffmpeg (obtained through `imageio-ffmpeg`, a standard PyPI package —
no Homebrew needed). The Nomad Labs lower-third is rendered directly
onto Shot 2 with ffmpeg's `drawtext`/`drawbox` (transparent-PNG
compositing wasn't viable from a JPEG screenshot, so this was done as a
direct overlay instead) — shown roughly t=2.3-7.3s into Shot 2, a
manual estimate of when "Nomad Labs" is spoken, not derived from exact
word timestamps. Shot 1's start and Shot 7's end also get matching fades
to/from black so the new cards feel stitched in, not bolted on. A rough
straight-concatenation preview (`vadium_explainer_full_preview.mp4`, no
new cards, no music) also still exists from before this pass for
comparison. Final music-under-dialogue mixing is still a separate,
un-done step per the Music production note below.

**Production note**: all new cards are pure on-screen text/graphics, no
spoken narration — this sidesteps the still-unresolved "Vaydum"/"Nobad
Labs" AI mispronunciation problem entirely for the most brand-critical
explanatory content, and needs no further Higgsfield video generation
(budget was down to 13.8 credits at the time this was decided). Built
as static-background title cards matching Shot 8's existing look (warm
parchment `#f2ede1`, verdigris-green accents, mono type) via HTML +
browser screenshot + ffmpeg, not new AI video generations.

**What changed from v1**: v1 was UI-screen recordings with on-screen text
carrying the plot. This version tells the same story through people
talking to each other — dispatchers, a driver, an ops lead — the way the
actual consequences of a bad delivery route play out in the real world.
Every on-chain/technical detail (the trust record's exact numbers, the
ledger entries, the dispute mechanics) is deliberately left out of the
video and pushed to the "Vadium Walkthrough" artifact and the live
playground instead — the video's job is to make someone *care*, not to
demo a dashboard.

**Tool**: [Higgsfield](https://higgsfield.ai) (Soul ID for character
consistency across shots — now doing real work, three recurring humans
instead of one operator), Veo 3 as the underlying model for dialogue
shots. See the note on music below — do not rely on per-shot generated
music for continuity.

**Scenario**: Meridian Logistics, same numbers as the original walkthrough
($180 job, 40 vehicles, 3 misrouted, **full $180 refund**) — kept as a
full refund deliberately, because the original agreement's own terms make
it a clean, automatic **objective**-path case, not a judgment call: the
deal was "all 40 routes correct," no partial-credit clause, so 3 wrong
routes means the pre-agreed spec simply wasn't met. No committee, no
discretion, no proportionality argument to defend — Vadium checks the
delivered outcome against the agreed terms and it either matches or it
doesn't. This keeps the story airtight against the obvious follow-up
question ("why not partial refund?") by removing the judgment call
entirely, not by explaining it away. The reasoning is spoken by Priya in
shot 6, not displayed as a number.

**Cast** (three recurring humans — register each as a Higgsfield Soul ID
the first time they appear):
- **Priya** — Meridian's ops lead. Calm, direct, the person who actually
  decided to hire Nomad Labs.
- **Dae** — a dispatcher on Priya's team, more skeptical, asks the
  questions a viewer would ask.
- **Marcus** — a delivery driver, on the road, the one who hits the
  actual wrong turn.

---

## Shot durations — derived from content, not a uniform 5s/9s (2026-09-30)

Per-shot length was originally a round-number guess (7-9s), then defaulted
to Seedance 2.5's 5s preset without anyone checking whether that was even
adjustable (it is — 4s-30s via a "Duration" stepper hidden below the
prompt box). Redone properly: word count × natural conversational pace
(2.3-2.6 words/sec, slower for weightier lines) + inter-turn pauses +
reaction beats (a laugh needs real time to land) + blocking beats (a
walk-in, a knock, a settle) that the visual description calls for but
dialogue-timing alone would skip. Real finding, corrected 2026-09-30
after a direct catch (see production log): **only Shot 6's full dialogue
fails to fit one natural-paced take** — its 47-word thesis line plus the
surrounding two lines needs ~33s, and Seedance caps a single clip at 30s
regardless, so it genuinely has to split. Shot 2 was *wrongly* split in
the first pass — its full four-line exchange only needs ~22s, comfortably
under the 30s cap — that was an overgeneralization from Shot 6's real
constraint, not a real constraint of its own. Shot 2 is one continuous
take; only Shot 6 splits, at a natural mid-scene beat.

| Shot | Duration | Reasoning |
|---|---|---|
| 1 | 12s | Walk-in beat + two unhurried lines (11 + 12 words) |
| 2 | 22s | Settle + Dae's question (13w) + Priya's full reassurance (22w) + the half-laugh beat (needs real time) + button line — one continuous exchange, well under the 30s cap |
| 3 | 5s | No dialogue — a breath; already right, no change |
| 4 | 10s | Wordless business (confusion, knock, head-shake) earns its own screen time before the one line |
| 5 | 17s | Two substantial lines (15w + 21w), not a quick exchange — more content than it looked |
| 6a | 26s | Dae's question + Priya's full 47-word explanation, held as one uninterrupted take — this is the video's thesis line, it earns the weight |
| 6b | 8s | The follow-up tag: Dae's question + Priya's close |
| 7 | 8s | No dialogue, but the "ordinary end of day" mood wants room to sit |
| 8 | 9s | Text read time + a 12-word VO shouldn't race each other |

**Total runway: ~117s (~1:57)**, unchanged from the split-shot total —
merging 2a+2b back into one continuous Shot 2 doesn't shorten the video,
it just removes an unnecessary cut. Still up from the rushed ~40s an
all-5s cut
would have produced. That's a real, material runtime increase worth
being explicit about — this is now a proper narrative-driven brand
piece, not a 40-second stitched-together clip reel.

---

## Shot 1 — Cold open (12s)

**Visual**: Pre-dawn Meridian Logistics dispatch floor. Priya, coffee in
hand, walks past a wall of departure-board-style monitors (glanced, not
read) to Dae's desk. Real warmth — this is a workplace, not a control
room.

**Dialogue**:
> **Dae**: "Forty trucks, same-day, and we're two dispatchers short today."
> **Priya**: "That's what our sourcing agent's for. It already found us someone."

**Music**: none yet — just room tone. Let the first line of dialogue land
in silence; music enters in shot 2.

**Higgsfield/Veo prompt**:
> Realistic handheld documentary-style shot, pre-dawn logistics dispatch
> floor, warm practical lighting mixed with cool morning light through
> high windows. A woman in her 40s (Priya) walks with a coffee cup past a
> row of monitors toward a dispatcher's desk where a man in his late 20s
> (Dae) is seated. Natural, unforced blocking — a real workplace morning,
> not a control room. Dialogue: Dae: "Forty trucks, same-day, and we're
> two dispatchers short today." Priya: "That's what our sourcing agent's
> for. It already found us someone." Ambient room tone only — quiet HVAC
> hum, distant phone ring, no music.

---

## Shot 2 — The hiring decision, in conversation (22s)

**Visual**: Priya sits on the edge of Dae's desk. Dae is visibly a little
uneasy — not about the technology, about the *unknown vendor*. Priya
reassures him; he softens into a genuine half-laugh by the end. One
continuous scene, no cut — same two people, same desk, the whole
exchange in one take.

**Dialogue**:
> **Dae**: "We've never used this Nomad Labs outfit before. What if they're bad?"
> **Priya**: "Vadium checked them. They've got real money on the line if they mess it up — not just a rating someone could fake."
> **Dae**: (half a laugh) "Money on the line. Like a deposit?"
> **Priya**: "Basically, yeah."

**Music**: a warm, minimal underscore begins under Priya's line — soft
nylon-string guitar or felt piano, unhurried, ~80 BPM, no percussion.
Stays low under dialogue throughout the video; never louder than the
voices.

**Higgsfield/Veo prompt**:
> Medium two-shot, same dispatch floor, natural morning light. Priya
> perches on the edge of Dae's desk, relaxed posture. Dae leans back,
> mildly skeptical but not alarmed. Dialogue: Dae: "We've never used this
> Nomad Labs outfit before. What if they're bad?" Priya: "Vadium checked
> them. They've got real money on the line if they mess it up — not just
> a rating someone could fake." Dae reacts with a genuine half-laugh:
> "Money on the line. Like a deposit?" Priya, easy and confident:
> "Basically, yeah." Warm, minimal instrumental underscore begins quietly
> under Priya's first line — soft nylon guitar, unhurried, no percussion.
> Naturalistic performances throughout, let the laugh actually land, do
> not rush any of it — give the dialogue room to breathe at an unhurried
> pace across the full exchange.

---

## Shot 3 — Out on the road (5s)

**Visual**: Cut to daylight. Marcus, driving a delivery van, radio/CB
chatter in the background, checking a route on a mounted phone holder —
brief, not a UI close-up, just a glimpse of a normal workday.

**Dialogue**: none — or a single line of Marcus humming along to the
radio. This shot is a breath, establishing the human stakes (real people
driving real routes) before something goes wrong.

**Music**: underscore continues, unchanged.

**Higgsfield/Veo prompt**:
> Realistic driver's-seat and through-windshield shot, delivery van,
> midday, ordinary suburban streets. Marcus, a driver in his 30s, glances
> at a phone mounted on the dash, relaxed, humming quietly along to a
> barely-audible radio. No dialogue. Naturalistic daylight, handheld
> camera feel. Warm minimal instrumental underscore continues quietly
> under ambient van and traffic sound.

---

## Shot 4 — Something's wrong (10s)

**Visual**: Marcus pulls up to a house, looks at the address, looks at
his phone, confused. Knocks — a resident answers, clearly not expecting
a delivery. A brief, awkward, human beat.

**Dialogue**:
> **Marcus** (into phone, calling dispatch): "Dae — this address doesn't
> match what's on the package. Third one today."

**Music**: underscore drops out almost entirely here — just a single
sustained low note, tension without melodrama.

**Higgsfield/Veo prompt**:
> Realistic exterior shot, suburban house, daytime. Marcus stands at the
> door holding a package, looking between it and his phone, visibly
> confused. A resident opens the door, glances at the package, shakes
> their head slightly — clearly the wrong delivery. Marcus steps back,
> calls dispatch. Dialogue, Marcus: "Dae — this address doesn't match
> what's on the package. Third one today." Naturalistic performances,
> mild awkwardness, nothing exaggerated. Music underscore drops to a
> single sustained low note, minimal tension, no dramatic sting.

---

## Shot 5 — Back at dispatch: filing it (17s)

**Visual**: Dae, phone to ear, catches Priya's eye across the floor.
Priya walks over. No screens shown — just two people deciding what to
do.

**Dialogue**:
> **Dae**: "Three bad routes out of the forty. Marcus is out there
> sorting it by hand."
> **Priya**: "Then we flag it. It's cut and dry — the deal was all forty
> correct, and it wasn't. Vadium checks that automatically."

**Music**: underscore returns, slightly more present than shot 2 but
still restrained.

**Higgsfield/Veo prompt**:
> Medium shot, dispatch floor, Dae still on the phone, catches Priya's
> eye and waves her over. Priya crosses to him, listens, reacts calmly —
> mildly frustrated, not alarmed. Dialogue: Dae: "Three bad routes out of
> the forty. Marcus is out there sorting it by hand." Priya: "Then we
> flag it. It's cut and dry — the deal was all forty correct, and it
> wasn't. Vadium checks that automatically." Naturalistic, low-key
> performances. Warm minimal underscore returns, slightly more present
> than earlier, still quiet under dialogue.

---

## Shot 6a — The resolution, explained by a person (26s)

**Visual**: Later — Priya at her desk, Dae nearby. This is the shot that
answers "why the full $180," in dialogue, not a number on a screen — and
the answer is deliberately simple: it's not generosity, it's the deal's
own terms. This is the video's thesis line — held as one uninterrupted
take on purpose, it earns the weight rather than being rushed or cut up.

**Dialogue**:
> **Dae**: "Full refund? Only three of forty were actually wrong."
> **Priya**: "Doesn't matter how many. The deal was all forty routes,
> correct, full stop — that's what we agreed to pay for. Three wrong
> means the job wasn't delivered as promised, and Vadium checked that
> against exactly what we signed off on. Automatic. Nobody had to argue
> about it."

**Music**: underscore begins to resolve — a warm chord change starting
partway through Priya's line, still no percussion, understated
satisfaction building rather than triumph.

**Higgsfield/Veo prompt**:
> Medium shot, Priya at her desk, Dae standing nearby, natural
> late-afternoon light. Calm, unhurried conversation — give this the
> full weight of a thesis statement, deliberate pace, no rushing. Dae:
> "Full refund? Only three of forty were actually wrong." Priya:
> "Doesn't matter how many. The deal was all forty routes, correct, full
> stop — that's what we agreed to pay for. Three wrong means the job
> wasn't delivered as promised, and Vadium checked that against exactly
> what we signed off on. Automatic. Nobody had to argue about it."
> Naturalistic performance, quiet confidence, no triumphant tone. Music
> underscore begins resolving to a warm chord change partway through,
> still minimal, no percussion.

---

## Shot 6b — The resolution, the tag (8s)

**Visual**: Same scene, continuous beat — Dae's genuine follow-up
question, Priya's calm close.

**Dialogue**:
> **Dae**: "So no back-and-forth with Nomad Labs at all?"
> **Priya**: "None needed. The terms were clear going in."

**Music**: underscore's warm chord change resolves fully here.

**Higgsfield/Veo prompt**:
> Medium shot, same desk, same characters and positions as the previous
> shot. Dae: "So no back-and-forth with Nomad Labs at all?" Priya, calm
> and unhurried: "None needed. The terms were clear going in."
> Naturalistic performances, quiet confidence, no triumphant tone. Music
> underscore resolves fully to a warm chord change, still minimal, no
> percussion.

---

## Shot 7 — End of day (8s)

**Visual**: Wide shot, dispatch floor winding down, Marcus's van pulling
back into the yard at dusk, Priya watching from the window. Ordinary.
Nothing dramatic — the point is that this was a normal Tuesday, not a
crisis.

**Dialogue**: none.

**Music**: underscore continues, beginning to soften toward the close.

**Higgsfield/Veo prompt**:
> Wide shot, dispatch floor at dusk, warm interior light against a
> darkening sky outside the windows. Marcus's van visible pulling into
> the yard below. Priya stands at the window, quiet, satisfied, unhurried
> — an ordinary end to an ordinary day. No dialogue. Warm minimal
> instrumental underscore continues, softening in volume and density
> toward the end of the shot.

---

## Shot 8 — Closing card (9s)

**Visual**: Cut to the Vadium logomark on warm parchment, same
restrained treatment as v1. One line of text only — resist the urge to
re-explain the mechanism here, that's what the walkthrough is for.

**On-screen text**: *"See exactly what happened, on-chain."* — then the
Vadium logomark, then "VADIUM, BY ATESTA."

**Voiceover** (the only VO in the whole piece — everything before this
was dialogue, not narration): *"Every step you just watched — verified,
on-chain, and yours to check."*

**Music**: underscore resolves fully and fades to silence under the VO.

**Higgsfield/Veo prompt**:
> Clean static composition, warm parchment background (#f2ede1), text
> fades in: "See exactly what happened, on-chain." Hold, then cross-fade
> to the Vadium logomark (rounded square frame, verdigris-green stroke,
> "Vd" centered, "VADIUM" in small mono type beneath), then "VADIUM, BY
> ATESTA" in mono type below it. No camera movement, confident negative
> space. Voiceover, calm, warm: "Every step you just watched — verified,
> on-chain, and yours to check." Instrumental underscore resolves fully
> and fades to silence under the voiceover.

---

## Music — one important production note

**Do not rely on each Higgsfield/Veo clip to independently generate
matching background music.** Per-shot generated music will not stay
consistent in key, tempo, or instrumentation across nine separate
generations, and it will sound stitched-together. The right approach:

1. Generate each shot with **dialogue and ambient/diegetic sound only**
   (room tone, traffic, footsteps) — the prompts above already specify
   this.
2. Source **one continuous instrumental track** separately — either a
   licensed stock cue (search "minimal warm acoustic underscore,
   unhurried, no percussion until a late resolve") or generate one via a
   dedicated music tool (e.g., Suno, Udio) using the direction above:
   nylon guitar or felt piano, ~80 BPM, sparse, resolving warmly at shot
   6, softening to silence by shot 8.
3. Lay that one track under the whole edited sequence at a level that
   never competes with dialogue — this is a standard editing step
   (CapCut/Premiere), not something to solve at generation time.

## The on-chain/technical handoff

This video deliberately shows none of: the trust-record numbers, the
evidence ledger, the dispute-review UI, the exact collateral figures. All
of that lives in two places, both already built:

- **"Vadium Walkthrough"** artifact — the clickable version of the same
  kind of objective, automatic case this video tells.
- **The Arc testnet playground** — where a viewer can register an
  identity, lock collateral, and watch both this objective case *and*
  the discretionary committee path (a genuine judgment call, for the
  disputes that aren't as clean-cut as this one) resolve on-chain, for
  real.

The closing card's line ("see exactly what happened, on-chain") is the
intended bridge to either — worth linking directly to whichever one the
video is published alongside.
