# Chapter 21: Product Philosophy & the Human-in-the-Loop Editor

> **Part IV — Product OS** · [← Chapter 20](20-data-strategy.md) · [Handbook index](README.md) · [Chapter 22 →](22-api-first-dx.md)

Product philosophy in one sentence: **automation is a slider, not a switch — and the slider's handle is the editor.** The industry's failed promise is one-click perfect dubbing; the industry's expensive reality is agency work with AI garnish. SyncDub's product lives deliberately between: the pipeline does everything, a human confirms or corrects what the confidence scores flag, and every correction makes tomorrow's pipeline need less correcting (Chapter 20). This chapter defines the product principles and the editor that embodies them.

## 21.1 Product principles

- **Ship the review, not just the render.** The deliverable is a dub *someone stands behind*. For the wedge customer, "our pipeline plus your review" beats "our pipeline, fingers crossed" — an institute putting its brand on a lecture needs the second sentence to be false. The review step is a feature we charge for, not an apology.
- **Confidence is a UI element.** The automatic scores (Chapter 16 §16.3) surface *in the product*: segments the scorer trusts render green and collapsed; flagged segments open for attention. The customer's reviewer spends minutes, not hours, per lecture — that ratio is the product's economics and its pitch in one number.
- **The student is the user; the reviewer is the customer's face of us** (Chapter 3's value, applied). Editor UX quality is not internal tooling polish — it *is* the enterprise product surface. But output quality decisions always resolve toward the student's phone, not the reviewer's monitor.
- **No feature before its measurement.** A product surface ships with the metric that will judge it (editor: corrections per lecture and review-minutes per dubbed-minute; delivery: watch-through where hosts share it). The gauntlet (Chapter 3 §3.3) already enforces this at acceptance time; this restates it at design time.
- **Speed of feedback beats speed of pipeline.** A dub returned in an hour with instant, pleasant review beats a dub in ten minutes with clunky correction. Chapter 11 monetized our latency tolerance; this principle spends some of it on review quality.

## 21.2 The editor, defined by its data

Per Chapter 20, the editor is the correction pipeline's front end — its design brief is the event schema. V1 surfaces, in priority order:

1. **The segment table.** Source transcript, translation, timing bar, confidence color, per segment. Click to edit text (transcript or translation), drag to re-time, one keystroke to flag-and-regenerate. Every action emits a typed correction event; none of this is freetext.
2. **Side-by-side preview.** Original and dub, synchronized at the selected segment (per-segment artifacts make seeking free). The reviewer never scrubs blind.
3. **The speaker/voice card.** Detected gender→voice mapping (today's Librosa pitch call, made visible and overridable — the silent auto-decision becomes an inspectable one). Cloning consent state displays here (Chapter 5 §5.2); the multi-speaker map slots in later (Chapter 18 §18.2.2).
4. **Batch actions.** Approve-all-green, regenerate-all-flagged, export. Reviewers of 40-lecture courses live in batch; a per-segment-only editor punishes exactly our best customers.

Deliberately absent from v1: waveform surgery, video editing, font/subtitle styling suites — those are adjacent products, and the moat is in corrections, not in becoming a worse Premiere.

## 21.3 The workflow tiers

The slider's stops, productized:

- **Auto** (API tier, Chapter 22): pipeline output as-is, confidence report attached. For integrators with their own review or risk tolerance.
- **Assisted** (the wedge default): pipeline + customer's reviewer in our editor. The confidence triage does the compression; the customer supplies the judgment. This tier feeds the flywheel fastest and prices best (Chapter 24).
- **Managed** (bounded, per Chapter 2 §2.4): pipeline + *our* editor bench (the founding linguist's network) for customers who want turnkey. Tolerated as a data-and-learning channel with an explicit ceiling — the moment managed review dominates revenue, we have become an agency and the strategy has failed; the written trigger for that alarm is managed-revenue > 30% two quarters running.

## 21.4 Frontend honesty

The current React app (`frontend/src/App.js`, 714 lines, one component) is the demo's upload-progress-download flow and has no architecture to carry the editor. The debt register already prices this (Chapter 14 §14.2: trigger = "first real frontend feature beyond the demo flow"). The editor is that trigger. Plan accordingly: the editor is a new frontend built on the job/segment API (Chapter 8–9), not a renovation of `App.js`; the demo flow becomes one small page of it.

## 21.5 Feedback loops beyond the editor

The founding brief asked for a "customer feedback loop"; ours is mostly *structural* rather than survey-based: correction events are feedback with coordinates (Chapter 20 §20.3 ranks the roadmap by them), reviewer-abandoned segments (opened, stared at, regenerated, abandoned) mark where the editor itself fails, and the quarterly customer conversation (Chapter 6's founder job) asks one question above all: *"What did you publish anyway despite disliking it?"* — the gap between corrected and tolerated is where the next quality axis hides.

## Key takeaways

- Automation is a slider; the editor is the handle, the moat's front end, and the enterprise product surface — designed from the correction-event schema outward.
- Confidence triage is the core UX: green-and-collapsed vs. flagged-and-open is what turns review from hours to minutes, and that ratio is the pitch.
- Three tiers — auto, assisted (the wedge default), managed (bounded at 30% with a written alarm) — keep us a software company that touches content, not an agency with software.
- The editor is a new frontend on the jobs API; `App.js` is the demo it replaces, not the foundation it extends.
- Feedback is structural: corrections, abandonment patterns, and the published-anyway question outrank surveys.

## Questions founders should ask

1. What is review-minutes-per-dubbed-minute this month, and which Chapter 16 axis improvement would cut it most?
2. Are green segments actually trustworthy — what's the rate of customer-reported errors in segments the triage collapsed?
3. Is managed-tier revenue creeping toward the 30% alarm, and is anyone watching?
4. What did our pilot customers publish anyway despite disliking it?

## Future research topics

- Paper-prototype the segment table with a real Marathi reviewer (the founding linguist's network) before building — an afternoon that prevents a quarter of wrong UI.
- Define the v1 confidence-threshold policy (what collapses, what opens) from early scorer-vs-correction calibration data (Chapter 16 §16.3's meta-loop).
- Study reviewer keyboard workflows in subtitling tools (Aegisub-class) — decades of correction-UX conventions exist; import, don't reinvent.
