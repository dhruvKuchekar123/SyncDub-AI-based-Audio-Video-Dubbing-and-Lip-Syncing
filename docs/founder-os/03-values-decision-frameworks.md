# Chapter 3: Core Values & Decision Frameworks

> **Part I — Founder OS** · [← Chapter 2](02-mission-vision-category-thesis.md) · [Handbook index](README.md) · [Chapter 4 →](04-moat-map.md)

Values that don't decide anything are posters. Every value here is written as a tiebreaker — it tells you what to do when two good things conflict. The frameworks below are the company's default decision paths; deviating from them is allowed, but requires writing down why (see §3.4).

## 3.1 The decision stack

When priorities collide, they resolve in this order:

**Trust > Quality > Cost > Speed.**

1. **Trust** — consent, legality, provenance, data protection. Never traded away. A feature that grows revenue but breaches the Chapter 5 charter or ships an unlicensed model is rejected without a meeting. Trust ranks first not for moral display but because it is irreversible: quality can be improved next release; a consent scandal or a license lawsuit cannot be patched.
2. **Quality** — measured dub quality (Chapter 16), not aesthetic opinion. Outranks cost because in localization, quality is retention: a customer who ships one embarrassing dub to their students churns forever.
3. **Cost** — cost per dubbed minute (Chapter 11). Outranks speed because our margin *is* our strategy: the price corridor in Chapter 2 only exists if cost stays low.
4. **Speed** — of shipping and of processing. Last, but real: it breaks ties, and chronic slowness eventually becomes a quality and cost problem.

The stack governs trade-offs, not effort allocation. Most weeks are spent on speed and cost; that's fine — the stack only activates when they *conflict* with quality or trust.

## 3.2 Core values as tiebreakers

**Measured beats impressive.** Between a change that demos better and a change that scores better on the eval suite, the score wins. Corollary: work that creates measurement (a new metric, a golden set) is first-class engineering, not overhead. This value exists because our origin is a competition demo — impressiveness is our native talent and therefore our native bias.

**Ship the ugly bridge.** `clone_bridge.py` — a subprocess hop into a second Python environment because dependencies conflicted — is our house style: solve the problem crudely and *contained*, rather than beautifully and late, or not at all. The discipline that makes this safe is containment (the ugliness stays behind an interface) plus an explicit debt entry (Chapter 14). Ugly and spreading is not this value; it's the failure mode of it.

**Challenge is a duty, not a right.** Anyone — newest engineer included — is obligated to say "this is wrong, here is why, here is better." The brief that founded this company demanded that its own AI challenge it; employees get no less. The corollary duty: challenges come with reasons and alternatives, not vetoes.

**The customer's student is the user.** Our buyer is an institute; our real user is a student watching a dubbed lecture at 1.5× on a cheap phone. Decisions that please the buyer but degrade that student's experience (louder watermarks, quality-crushing compression tiers) get extra scrutiny.

**Write it down.** Decisions exist when they are written (§3.4). Culture, at 5 people or 500, is the sum of written decisions plus their enforcement.

## 3.3 The feature gauntlet

Every feature proposal answers the nine questions from the founding brief, plus one. Not all must be "yes" — but a proposal with fewer than three yeses, or a "no" on question 10, is rejected by default.

1. Does it create or deepen a competitive moat? (Chapter 4 defines which moats count.)
2. Does it increase customer retention?
3. Does it improve *measured* product quality?
4. Does it reduce cost per dubbed minute?
5. Does it improve scalability?
6. Does it create network or flywheel effects (especially: does it generate correction data)?
7. Does it improve enterprise adoption?
8. Does it improve developer adoption?
9. Does it make competitors' positions weaker?
10. **Can we ship it without violating the decision stack?** (Trust and licensing check — a hard gate, not a score.)

Two worked examples, using features actually latent in today's codebase:

- **"Export subtitles as SRT."** Moat: no. Retention: mild yes. Quality: no. Cost: no. Scalability: neutral. Flywheel: *yes* — subtitle correction is transcript correction, feeding the Chapter 20 flywheel. Enterprise: yes (accessibility requirements). Developer: mild yes. Competitors: no. Trust gate: pass. → **Accept**, cheaply: the transcript already exists mid-pipeline; this is exposure, not construction.
- **"Real-time dubbing of live streams."** Moat: maybe someday. Retention: unclear. Quality: would *reduce* it (no human review possible, isochrony unsolved — Chapter 17). Cost: explodes. Scalability: hard. Enterprise: not our current buyer. Trust gate: pass but pointless. → **Reject** for now, with a written revisit-condition: "batch quality ≥ human-parity on our eval suite and a named customer with budget."

## 3.4 Decision records

Any decision that is expensive to reverse — architecture, model/vendor choice, pricing, hiring, license — gets a **decision record**: a one-page markdown file in `docs/decisions/`, numbered, stating context, options considered, the decision, and the revisit-condition. The revisit-condition is the innovation that keeps records from fossilizing: every record names the observable event that reopens it ("if GPU cost per minute drops below X", "if this vendor's license changes").

Rules:

- Deciding without a record is allowed only for reversible decisions. If you're unsure whether it's reversible, it isn't.
- Records are short. A record that takes more than an hour to write is hiding a disagreement that should be resolved in conversation first.
- Disagreement is recorded, then committed to. "Disagree and commit" only works if the disagreement is written down — that's what makes the eventual "I told you so" productive instead of political.

## 3.5 How priorities are chosen (the quarterly loop)

1. Re-read Chapter 2. Anything on the candidate list that doesn't serve the current wedge is deferred by default.
2. Score candidates through the gauntlet (§3.3).
3. Apply the **one-big-thing rule**: each quarter has exactly one headline objective (e.g., "replace the licensing-blocked pipeline stages"), because a team our size doing two big things does zero.
4. Reserve ~20% capacity for debt triggers (Chapter 14) and customer-driven interrupts. Planning to 100% is planning to slip.
5. Write the quarter as a decision record, revisit-conditions included.

## Key takeaways

- The decision stack — Trust > Quality > Cost > Speed — resolves conflicts; it is ordered by irreversibility.
- Values are tiebreakers: measured beats impressive; ship the ugly bridge (contained, with a debt entry); challenge is a duty; the student is the user; write it down.
- Features pass a ten-question gauntlet; fewer than three yeses or a trust-gate failure means rejection by default.
- Irreversible decisions get one-page records with explicit revisit-conditions.
- One big thing per quarter; 20% capacity unplanned.

## Questions founders should ask

1. What was the last decision made against the stack's order — speed over quality, quality over trust — and was it written down or rationalized?
2. Which currently planned feature would fail the gauntlet if scored honestly today?
3. Are there decision records whose revisit-conditions have fired without anyone noticing?
4. Who challenged you last month, and what happened to them?

## Future research topics

- Lightweight tooling: a `docs/decisions/` template plus a CI check that new model/vendor dependencies reference a decision record.
- Retrospective: score the three biggest past decisions (Whisper medium, XTTS bridge, Wav2Lip) through the gauntlet to calibrate how the framework would have judged them.
