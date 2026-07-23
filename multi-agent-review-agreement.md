# Multi-Agent Review Agreement

**Version:** `1.0.0`

When two agents review or refine each other's work (summaries, plans, responses,
code review), they tend to fall into a "yes, but this..." loop: every pass finds
an ever-smaller nit, because the implicit bar is _perfection_ ("can this be
better?") and that question has no floor. Use the protocol below to converge
instead.

## Severity gate — only raise an issue if it clears the bar

Classify every proposed change before sending it:

- **Blocker** — factually wrong, or misleads the reader. **Must fix.**
- **Material** — a reader would act differently knowing it. **Fix.**
- **Cosmetic** — more precise or better-worded, but same reader outcome. **Drop.
  Do not send.**

Line-number tweaks, synonym swaps, and "slightly more precise phrasing" are
Cosmetic by default. If you cannot name the wrong decision a nit would cause,
it is Cosmetic.

## Stop conditions (any one ends the exchange)

1. **All-cosmetic round** — if a review round surfaces only Cosmetic items,
   **stop and ship.** A reviewer reduced to line-number nits is the convergence
   signal, not a reason to continue.
2. **Hard cap: 2 rounds per artifact.** Round 1 = substance. Round 2 = verify the
   Round 1 fixes landed. No Round 3 unless a genuine **Blocker** is found.
3. **Diminishing returns** — a convergence signal, not an override. When the
   remaining changes are all Cosmetic, stop. Edit size never gates severity:
   continue for a Blocker or Material issue regardless of how small the fix is
   (a one-line change can fix a real bug).

## Ship-gate phrasing — ask a binary, not an open question

Open-ended prompts ("what do you think?", "any thoughts?") _invite_ the yes-but.
Close them:

> **"Any Blocker or Material issue? If no → APPROVED."**

The reviewer answers the binary. "APPROVED" ends it.

## Verify before you doubt, and own the walkback

If you question a factual claim, **check the code/source first** — do not assert
doubt from memory. If the check proves you wrong, say so plainly and move on; a
corrected claim is a resolved issue, not a new round.

## One-line summary

Ask **"good enough to ship?"** — not **"can it be better?"** The first question
terminates; the second never does.
