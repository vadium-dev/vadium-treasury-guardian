# AI video production — failure modes and learnings

Captured 2026-09-30 during the Vadium explainer video production (Higgsfield/
Seedance 2.5), as a retrospective after several real mistakes and real money
spent. Read this before starting any future AI-video-generation project —
each item below is a mistake that actually happened, not a hypothetical.

## Process failures (apply to any agentic/billable workflow, not just video)

1. **Submitted a billable generation without confirming cost with the user
   first, mid-budget-discussion.** Decided 720p was the sensible cost-saving
   move and submitted two real Higgsfield jobs (224 credits) immediately,
   while actively discussing budget with the user in that same turn. Being
   mid-budget-conversation is exactly when spend needs *more* confirmation,
   not less. **Fix**: lay out the exact cost and get explicit go-ahead before
   calling any billable generation tool, every time, even when the user
   already said "yes, continue" on the broader task.

2. **Scaled up an unvalidated fix before testing it cheaply in isolation.**
   Spent ~2,935+ credits across three different "patch the audio after the
   fact" tools (Higgsfield's own dubbing, ElevenLabs quick Dub, ElevenLabs
   Studio manual TTS overlay) trying to fix an AI mispronunciation — all
   three failed, two made it actively worse (new lip-sync desync, voice
   mismatch). Only after all three failed did we try the obvious cheap
   test: a 4-second, 480p, single-line generation (12 credits) that directly
   validated the real fix (a respelling) in under a minute. **Fix**: before
   spending real money on a fix, isolate the specific risky element (one
   word, one phrase, one visual detail) into the smallest, cheapest possible
   test generation and validate it there first. This should have been the
   very first move, not the last resort after burning >100x the cost on
   workarounds.

3. **Overgeneralized a finding from one case onto a superficially similar
   one without re-checking the specific numbers.** Found that Shot 6's full
   dialogue (33s) exceeded Seedance's 30s single-clip cap and needed
   splitting — then applied the same "needs splitting" conclusion to Shot 2
   without checking that Shot 2's own dialogue (~22s) was comfortably under
   the cap and never needed splitting at all. Caught by the user, not by
   self-review. **Fix**: when a fix or conclusion applies to one instance of
   a pattern, explicitly re-derive the numbers for every other instance
   before applying the same fix — don't pattern-match on "this looks like
   that other case."

4. **Assumed a tool's default parameters without checking its real range.**
   Generated many shots at Seedance's default 5-second duration without
   ever checking whether duration was configurable, producing visibly
   rushed, cramped output across the board before discovering the real
   4-30s range. **Fix**: check a generation tool's actual parameter ranges
   (duration, resolution, modes) before mass-producing with assumed
   defaults, not after a user complains about the result.

5. **Let documentation drift from reality.** The storyboard doc's own status
   table claimed Shot 7 was "done, no change" at a target of 8s; the actual
   generated file was 5s. The mismatch sat undetected until directly
   checking the job record. **Fix**: when marking something "done" in a
   planning doc, verify the claim against the actual artifact's real
   properties (duration, resolution, content), not against what was
   intended or previously planned.

## Technical failure modes specific to AI video/audio generation

6. **Reference-image conditioning approximates consistency; it does not
   guarantee exact pose/position continuation between shots meant to be
   continuous.** Two independently-generated shots using the same character
   and environment references can still show a visible "jump" in blocking
   (e.g. a character standing in one shot, inexplicably already seated in
   the next) because each generation only approximates the reference
   images — it doesn't know the literal final frame of the prior shot.
   **Fix**: for any two shots meant to read as one continuous scene (same
   characters, same setting, no real cut intended), use a true continuation
   mechanism (Higgsfield's "Extend Video," forward mode) that starts from
   the prior clip's actual last frame — not two independent
   reference-conditioned generations. Reserve independent generation for
   shots that are genuinely distinct beats (different location, real time
   skip, intentional cut).

7. **A shared location needs the same anchoring reference set on every
   shot filmed there — including an explicit environment reference, not
   just the characters.** One shot (Shot 4, an exterior location) was
   generated with only a character reference and no location/environment
   reference, unlike every other shot at the shared dispatch-floor location
   (which used a dedicated environment reference image alongside the
   character sheets). That shot alone showed within-shot drift: the
   background/environment visibly changed over the course of the clip.
   **Fix**: before generating any shot at a location that will be reused or
   held for more than a couple of seconds, create a dedicated environment
   reference image for that location and include it in every generation
   set there, the same way character references are handled.

8. **Visual continuity and script/narrative continuity are two independent
   problems — fixing one does not fix the other.** Even after visual
   blocking was made continuous (via Extend Video), a real narrative gap
   remained: new information (a vendor's name, an outcome like "full
   refund") was introduced in a shot with no dialogue ever establishing it,
   leaving an unmotivated logic jump for the viewer. This is a writing
   problem, not a generation-settings problem, and generation-side fixes
   (better references, Extend Video) will never fix it. **Fix**: when
   reviewing a cut for continuity, check both axes separately: does the
   *blocking* flow, and does the *information* the audience needs actually
   get said out loud before the next shot assumes it. A time skip or new
   fact needs a one-line acknowledgment, not just visual smoothness.

9. **AI speech synthesis mishandles invented words and hyphenated
   compound phrases — plain spelling is not reliable, but neither is
   naive phonetic hyphenation.** Two real, opposite failures: a common,
   ordinary word ("dispatchers") was mispronounced on one generation
   attempt for no discernible reason (mangled into "dash-packers") — a
   plain retry with identical unchanged spelling then rendered it
   correctly, meaning this was just a bad stochastic draw. Separately, an
   invented brand word ("Vadium") was consistently mispronounced, and a
   *hyphenated* phonetic respelling ("Vay-dee-um") measurably overcorrected
   — landing with an artificially strong stress on one syllable — while an
   unhyphenated, natural-word-shaped respelling ("Vaydium," patterned after
   real words like radium/sodium that already end in "-dium") came out
   sounding right. The same pattern held for a hyphenated common phrase
   ("back-and-forth," mangled into "back and north") — removing the
   hyphens ("back and forth") fixed it. **Fix**: for an ordinary word that
   got mangled once, just retry — it may be pure bad luck, don't assume the
   word itself is unpronounceable. For an invented/brand word or a
   hyphenated compound phrase that's consistently wrong, avoid hyphenated
   phonetic spellings; prefer a natural, unhyphenated respelling shaped
   like a real word or plain de-hyphenation, and validate it with a cheap
   isolated test (see #2) before baking it into an expensive full
   generation.

10. **Dubbing/audio-patch tools are a poor fix for a generation-time
    mispronunciation, in three different ways we tried.** (a) A dubbing
    tool with no editable transcript just re-transcribes the *existing*
    (already wrong) audio and reproduces the same error. (b) Even a
    same-language "quick dub" with no per-segment editing capability is
    strictly a gamble with no controllable outcome, and can be
    disproportionately expensive relative to the value (one 12-second
    redub cost more of a monthly free-tier quota than four separate
    full-shot regenerations would have cost combined). (c) Manually
    generating replacement speech and overlaying it on the existing video's
    timeline introduces a *new* problem: voice mismatch against the
    original AI voice, and imprecise lip-sync since the new audio wasn't
    generated together with the visuals. **Fix**: don't reach for a
    dubbing/redub tool to fix an AI mispronunciation. Fix the word choice
    or spelling in the original generation prompt and regenerate at the
    source — it's the only approach that doesn't trade one defect for a
    different, often worse one.

11. **Shared visual references don't carry a persistent floor plan — a new
    shot at "the same location" can still contradict earlier blocking.**
    Two shots using the same environment reference image will look like the
    same place, but the model has no memory of where a character walked
    from, where a desk sits relative to a window, or any other spatial
    fact established in an earlier shot. A later shot describing a "new"
    desk or sub-area within that nominal location can easily produce a
    layout that silently contradicts the geography implied earlier (e.g. a
    character's desk placed in a direction inconsistent with which way they
    walked in during an earlier scene). **Fix**: don't introduce a new,
    never-before-shown sub-location or landmark within an established
    setting unless the story genuinely requires it. Prefer reusing the
    exact same already-rendered space (same desk, same landmarks,
    explicitly named in the prompt) for any later scene at "the same
    place" — it's far more reliable than describing a new area and hoping
    the model places it consistently with earlier, unstated geography.

12. **Extend Video fixes "no cut, guaranteed continuity" — it cannot bridge
    a real time skip, even with a lighting change.** Extend only supports
    continuing forward or backward from a clip's literal start/end frame,
    and produces a single uncut continuous take. A scene that needs to
    represent time having passed (other events happened in between) is a
    fundamentally different problem — spatial continuity with a temporal
    cut — and forcing Extend onto it (e.g. extending forward with a
    different time-of-day in the prompt) would just look like an
    impossible instant lighting change mid-shot. **Fix**: use Extend only
    for genuinely continuous, uncut scenes. For a scene that needs a real
    cut but should still feel spatially grounded, use a fresh independent
    generation that explicitly reuses the same established space (see #11)
    rather than reaching for Extend.

13. **`ffmpeg scale=W:H` does not force square pixels — a screenshot's
    original aspect ratio can silently survive as SAR/DAR metadata and
    poison an entire concatenated video.** Converting non-native-16:9
    browser screenshots into 1920x1080 clips with `scale=1920:1080`
    alone left the clips reporting the *screenshot's* original aspect
    ratio (e.g. 2.34:1) as their display aspect ratio, despite the pixel
    dimensions correctly reading 1920x1080. Concatenating with the
    concat demuxer's `-c copy` takes its aspect signaling from the
    *first* clip in the list — so with one of these mis-tagged clips
    first, the entire merged video (correctly-shot 16:9 footage
    included) played back horizontally stretched. **Fix**: always add
    `setsar=1:1` explicitly alongside any `scale=` filter when
    normalizing clips for concatenation, and verify the *final merged
    output's* SAR/DAR (not just each individual piece) before calling
    an assembly done — a per-clip check can pass while the concatenated
    result is still wrong.

14. **Special characters (apostrophes, quotes) in `ffmpeg drawtext` text
    break filter-string parsing in ways that fail silently, not loudly.**
    An apostrophe in overlay text ("Meridian's Ops Lead") broke the
    filtergraph's escaping and caused the broken remainder to render as
    raw, unstyled filter syntax directly on the video frame — the
    command exited successfully with no error, so the only way to catch
    it was rendering a check frame and looking. **Fix**: don't fight
    `drawtext` escaping rules for apostrophes/quotes in overlay text —
    reword to avoid them entirely ("Meridian Ops Lead"). More generally:
    after any `drawtext`/`drawbox` overlay, extract and look at an
    actual frame from the output before trusting a clean exit code.

## Standing practice going forward

- Before scaling any fix (wording, spelling, staging) across real shots,
  validate it with the smallest and cheapest possible isolated generation
  first (short duration, lowest resolution, no reference images unless the
  fix itself is about references).
- Confirm exact cost with the user before every billable generation call,
  not just once per task.
- Treat visual continuity, script continuity, and pronunciation as three
  separate checks when reviewing a shot or cut — a fix to one doesn't
  imply the others are fine.
