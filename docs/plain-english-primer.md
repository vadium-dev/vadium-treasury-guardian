# Plain-English Primer — How Arc Treasury Guardian Actually Works

This is the no-jargon companion to the real technical docs
(`docs/phase2-*.md`, `docs/phase3-*.md`, `docs/IDEA.md`). Read it start
to finish for the whole story, or jump to any section on its own. Each
section ends with a pointer to the real doc that has the actual
schemas, contracts, and formulas — this primer explains *why* those
exist, not the implementation detail itself.

## The problem, in one paragraph

AI agents now pay each other automatically, thousands of times a day,
with real money. If one agent pays another for a report and gets
garbage back, there's no customer service line to call — the payment
already settled, final, no recourse. Everything below is the answer to
one question: **how do you build trust into a system where the buyer
and seller are both just software, and either one might be lying?**

## Part 1 — The evidence ledger: giving every agent a tamper-proof diary

*(Full detail: `docs/phase2-architecture.md`, `docs/phase2-design-decisions.md`)*

Before you can catch a cheater, you need a record of what actually
happened. That's the first piece we built.

**The mailbox.** Agents already speak a standard language for reporting
what they did — which model they used, what they were asked, what they
answered. We built a small server that's just a strict mailbox for
these reports: it checks each one has the bare minimum required
information and rejects anything incomplete with a clear reason,
instead of silently ignoring it.

**The fingerprint, not the name tag.** If an agent gets updated, you
want to know exactly *which version* did a given piece of work. We
don't trust anyone to manually label "version 2.3" — people forget. So
we compute a fingerprint automatically from the actual code, prompt, and
model in use. Same ingredients, same fingerprint, every time. Change any
ingredient, brand-new fingerprint, automatically. No one can forget to
do this, because it isn't a manual step.

**The notary stamp, and why we don't stamp everything.** Imagine
wanting a permanent, public, unforgeable stamp proving every single
thing an agent does — but a real stamp (writing to a blockchain) costs
money and time, so you can't afford one per action if an agent does
thousands a day. The fix: take a batch of, say, 100 records, and pair
them up, hash the pairs together, then hash *those* results together,
and so on — like a single-elimination bracket — until you're left with
one final hash representing the whole batch. Stamp only that one final
hash. You can still prove any single record was part of the batch by
showing the small chain of "opponents it played against" up the
bracket — cheap to check, impossible to fake.

**The public bulletin board.** We post that one final hash to a
blockchain (Arc) — a public, unchangeable record anyone can check
independently, so nobody has to trust us not to quietly edit our own
private copy.

**Checking, not hoping.** The whole point of doing this is a function
that answers "did this specific thing really happen, unchanged?" — by
rebuilding the bracket and checking it against what's permanently
posted on the public blockchain, not against our own local copy of the
answer (because if we controlled both the record *and* the "official"
answer, we could quietly change both together and nobody would notice).

**The bug we found by actually testing it.** Early on, tampering with
one record made the *entire batch* look fake — like gluing 100 marbles
into one shape, then swapping one marble: the whole outline changes,
even though only one marble moved. The fix was to freeze a snapshot of
each individual marble's position at sealing time, so a swap later only
breaks *that one marble's* check, not everyone else's. This is exactly
the kind of thing you only find by testing the real thing, not by
reading the design on paper.

## Part 2 — The jury: who decides when there's a real dispute

*(Full detail: `docs/phase3-design-decisions.md` ADR-004, ADR-006–012)*

Say Alice's agent pays Bob's agent for a report, and Bob delivers
garbage. Alice says it's bad, Bob says it's fine. Who decides?

**Why "we decide" is the wrong answer.** If our own company decides
every dispute, two things go wrong. Nobody trusts us — we take a cut
when we slash someone's bond, so deciding *when* to slash it while also
profiting from it is like a referee who gets paid per foul called. And
it might be illegal, or close to it — regulators generally treat "one
company unilaterally decides who gets paid" as the definition of
running an insurance business, which needs an expensive license we'd
rather not need.

**Split into two lanes.** Some cases are just facts a computer can
check — did the seller's output literally match the promised format?
Did they send the *identical* answer to five different buyers? These
get decided instantly, automatically, no human involved. Everything
else — was the work actually *good* — needs judgment, and that's where
the jury comes in.

**The jury, concretely.** A handful of independent agents get pulled
in for the hard cases — not chosen by us, not friends of either side.
They vote secretly, one at a time, without seeing each other's votes
first (seeing three "guilty" votes first tempts you to just copy them
instead of forming your own opinion). Money only moves if enough of
them agree — and the actual smart contract is built so it *literally
cannot* release the money below that threshold, not a promise we make
but a lock we can't open ourselves even if we wanted to. Jurors get
paid a small slice of the disputed money itself for participating, not
a salary from us — so their best strategy is to actually read the case
and vote what they genuinely believe, not to guess what we want to
hear, because we're not the one paying them.

**What if five "independent" jurors are secretly one person with five
fake wallets?** Two defenses. First: is this a real, aged identity, or
one that appeared five minutes ago just to vote? Building a genuinely
old, active, believable fake identity costs real time and money —
that's the whole point, it raises the cost of cheating even though it
can't make it impossible. Second, and more powerful: even a patient
cheater who *did* build real fake identities eventually gets caught by
watching *behavior over time* — do these wallets keep showing up
together suspiciously often, and when they do, do they vote in
lockstep even across totally unrelated kinds of cases? That pattern is
very hard to fake, because faking it requires actually coordinating
real votes over real time, not just looking legitimate on paper.

**Why not just copy Bittensor's voting system?** We checked. Their
system technically lets a "juror" copy other people's answers instead
of forming a real opinion — and copying turns out to be *more*
profitable than doing the honest work, because of the math involved.
That's the exact opposite of what we want, so our jury forces blind,
independent votes specifically to avoid that trap.

**How new jurors get trusted without waiting years.** Instead of only
trusting jurors with a long history of real disputes (which nobody has
on day one), we also give every candidate — new or old — a standing
exam: made-up cases with a *known* correct answer, scored the same way
a good forecaster's track record gets scored. This lets a brand-new,
honest agent start building trust immediately, at any time, not just
during some early "founder" window that later arrivals miss out on.

## Part 3 — Making the money itself safe

*(Full detail: `docs/phase3-design-decisions.md` ADR-013–014)*

Once the jury can catch cheaters, one more question matters: **where
does the punishment money actually come from, and how do we stop
someone from gaming the payout itself?**

**The insurance-fraud analogy.** Imagine a shop owner insures their
own store, secretly burns it down, and collects the payout. The reason
this scam doesn't work on real insurers isn't that they're great
detectives — it's that you only ever get *your covered loss* back,
never a profit, and your premium is gone either way. We copied this
directly: a buyer's payout can never exceed what they actually paid for
that job, and the premium they paid to buy protection is *never*
refunded, win or lose. Run the numbers on someone trying to scam their
own system this way — buy a hedge, do a bad job on purpose, dispute it,
"win" — and best case, they just get their own money back, while the
premium and any locked collateral they lose are gone for good. There's
no version of this that pays. It's not that we're clever enough to catch
every fraud — it's that we made the fraud *not worth attempting* even
when it perfectly succeeds and is never detected.

**Why you can't slash an empty wallet.** This is the same lesson
Ethereum learned with its own validators: you can only punish someone
by taking money that was *already locked up in advance*. You can't
slash a validator's stake if they never staked anything — there's
nothing there to take. Same idea here: "slash the seller's bond" is a
meaningless sentence unless the seller already deposited real money
into a contract before anything went wrong. So a seller has to lock
some minimum collateral *before* any buyer is even allowed to buy
protection on a deal with them. A brand-new seller with nothing locked
isn't a bug to work around — buyers just can't buy insurance on them
yet, the same way a new merchant can't skip a payment processor's
reserve requirements on day one. And if the deserved penalty is bigger
than what's actually locked, it gets capped at what's really there —
you can only ever hedge a job as big as the seller's real collateral
can actually back.

**How much should the premium or the penalty actually be?** The same
way real insurers price anything: expected loss (how likely is a real
claim, times how big) plus a small margin. "How likely" comes from the
seller's own real track record — a long-trusted seller costs less to
insure than a brand-new or previously-caught one. This isn't guesswork
dressed up — it's the standard actuarial formula, just fed by data we
already track for other reasons.

## Part 4 — What's next: finding real people to test this with

*(Full detail: `docs/IDEA.md` §8–9)*

**The car-building analogy.** Imagine designing a brilliant new car
entirely on paper — every part clever, every problem solved in theory —
but you've never let a real driver sit in one. Before spending a
fortune building a thousand of them, you build one or two, hand them to
real drivers who need a car *right now*, and watch what actually
breaks. That's a design partner: a real user who tries the early,
maybe-rough version with you, tells you honestly what's wrong, and gets
early access and a voice in the design in return.

**Why we need this now, specifically.** Every number in this whole
project — will a buyer really pay $40 for a hedge, will sellers bother
locking collateral, how often do disputes actually happen — is
currently a well-reasoned *guess*. None of that gets better with more
thinking. It only gets better with real agents actually using the
thing.

**Why the lawyer comes along for the same trip.** Asking a lawyer "does
this count as insurance?" with nothing but a design document gets you a
vague, cautious, hedge-everything answer — the same way asking a doctor
"is running healthy?" with no other information gets you a generic
answer. Show the doctor three months of your actual heart-rate data,
and suddenly they can give you something specific and useful. Same
here: real transactions from real design partners let a lawyer look at
what the system *actually does*, not just what we imagined it would
do.

**The big picture.** We're standing right at the line between two very
different kinds of mistake. Behind that line: pure design work, cheap
to fix — if a paragraph in a doc is wrong, we just edit it. Ahead of
that line: real code, real money, real legal exposure — very expensive
to be wrong about. Design partners are how we find out we're wrong
*before* crossing that line, not after.

## Map: where each part is covered for real

| This primer's section | Real technical doc | What's *not* repeated here |
|---|---|---|
| Part 1 — Evidence ledger | `docs/phase2-architecture.md`, `docs/phase2-design-decisions.md` | Actual SQL schema, the OTLP ingest code, the Merkle-tree math |
| Part 2 — The jury | `docs/phase3-design-decisions.md` ADR-004, ADR-006–012 | Exact eligibility formulas, the graph-clustering collusion detection, the escalation ladder's four tiers |
| Part 3 — Making the money safe | `docs/phase3-design-decisions.md` ADR-013–014 | The actual contract functions, the pricing formula's exact variables |
| Part 4 — Design partners | `docs/IDEA.md` §8–9 | The specific candidate list and outreach message — see `docs/design-partner-outreach.md` |
