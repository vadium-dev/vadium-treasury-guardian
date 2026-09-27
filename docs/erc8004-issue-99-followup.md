# Follow-up comment for erc-8004/erc-8004-contracts#99

Status: DRAFT — not posted. Review before submitting.

---

Both good catches, and the second one is a real sharpening, not just a
critique — worth restating back to make sure I've got it right.

**On tag vs. weight**: agreed, and I think this fully resolves Q2. The
grounding tag should say *how* a record was verified — cheap, objective,
something a settlement contract can check without walking anything —
and stop there. Weighting (diversity, funding-graph clustering,
whatever else) only makes sense for an off-chain consumer that can
afford it, and baking a weight into the tag conflates two things with
completely different cost budgets: a contract deciding inside a
transaction, and something like our own lookup that can afford a few
dozen sub-queries per read. Tag = verification method, weight =
consumer policy. That's a cleaner answer than what I proposed.

**On ratee vs. payee**: also a real gap, and worth being honest in
public about where it does and doesn't bite us. Our own evidence
attribution never infers identity from payment flow in the first place
— it requires a signature from the specific identity claiming credit,
checked independently of where any money moved — so this doesn't touch
that layer. It *is* a live open question for anything that ties
collateral or coverage to "the agent behind this payout" specifically,
which is exactly the shape you're both flagging: a treasury or
marketplace payTo sitting between many worker-agents and one payment
address needs the ratee to be its own explicit field, not inferred.
Good to have that named plainly before anyone's schema bakes in the
assumption.

Appreciate the fixture offer too — more directly useful for validating
the payment-proof half of this than the weighting side, so I'll leave
it there for now rather than adding noise, but noted for later if this
moves toward a reference implementation.

---

## Notes before posting

- Keeps the same tone as the first comment — collaborative, not
  defensive about the ratee/payee gap in our own design.
- Doesn't over-disclose: names the *principle* our identity layer
  follows (signature-based, not payment-flow-based) without describing
  BondPool/collateral mechanics in any detail — consistent with the
  standing rule for anything public-facing.
- Not posted automatically — same as before, a public, attributable
  action on your own GitHub identity. Post with:
  `gh issue comment 99 --repo erc-8004/erc-8004-contracts --body-file docs/erc8004-issue-99-followup.md`
  (strip this "Notes before posting" section first).
