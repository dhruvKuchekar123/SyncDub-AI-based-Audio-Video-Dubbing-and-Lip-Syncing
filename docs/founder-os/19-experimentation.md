# Chapter 19: Experimentation & A/B Framework

> **Part III — AI Research OS** · [← Chapter 18](18-multispeaker-emotion.md) · [Handbook index](README.md) · [Chapter 20 →](20-data-strategy.md)

Chapters 15–18 generate a constant stream of candidates: new models, isochrony rungs, emotion tags, parameter changes. This chapter is the process wrapper that decides which candidates win — and it begins with an honest correction to the founding brief, which asked for "Automatic A/B Testing" in the web-startup sense. **Traffic-split A/B testing is mostly the wrong tool for us**: our outcomes are quality scores computable offline, our traffic is small, and shipping a worse dub to half of a customer's students to learn something we could have learned on the benchmark set is both bad science and bad ethics. Our framework is therefore offline-first, shadow-second, live-split last and rarely.

## 19.1 The experiment hierarchy

Cheapest decisive method wins; escalate only when the cheaper level can't decide:

1. **Offline evaluation** (decides ~80% of questions). Run candidate vs. incumbent on the benchmark set (Chapter 16 §16.2); compare score vectors and CPDM. Model swaps, parameter changes (`beam_size`, rate caps), quantization trades — all decidable here, in hours, harming no one.
2. **Shadow runs** (decides most of the rest). Candidate processes real production inputs alongside the incumbent; outputs stored, scored, spot-checked by the linguist — never delivered (Chapter 13 §13.2). Catches what golden sets miss by construction: the distribution shift between our curated 50 clips and whatever customers actually upload. Per-stage artifacts make shadows nearly free; the standing rule is that **any promotion (Chapter 15 §15.5 step 5) shadows for a meaningful sample first**.
3. **Human preference tests.** When automatic scores disagree with each other or the stakes are perceptual (voice naturalness, emotion tags), run calibrated preference panels (Chapter 16 §16.4's rubric discipline) on shadow outputs.
4. **Live experiments** (rare, opt-in). Only when the question is genuinely about *user behavior* rather than output quality — e.g., does the editor's re-timing suggestion UI get used? Live splits on *dub quality* require the affected customer's informed opt-in ("beta voice program"), because students are not experimental subjects the institute didn't consent for. This is the Chapter 5 posture applied to experimentation.

## 19.2 The experiment record

Every experiment, one lightweight record (a sibling of the decision record, in `docs/experiments/`): hypothesis with a falsifiable claim ("IndicTrans2 ≥ current translation adequacy at ≤ cost, on benchmark v3"), method level (1–4), the pre-registered decision rule ("promote if adequacy within 1 point and isochrony improves"), result, and decision. Pre-registering the rule is the part that matters: deciding *after* seeing results which metric counts is how motivated reasoning ships regressions with a straight face. Failed experiments file the same record — the registry's archived scores (Chapter 15 §15.5 step 6) and the experiment log together are why the same dead end doesn't get explored twice a year apart.

## 19.3 Velocity: the real constraint

A framework this clean can still be slow, and slow experimentation quietly becomes no experimentation. Standards that protect velocity:

- **One command.** `run-eval <candidate-adapter> <benchmark-version>` produces the full score vector and CPDM delta. If benchmarking requires manual steps, benchmarks won't happen under deadline — automation of evaluation *is* research infrastructure (the founding brief's "how experimentation happens" answered concretely).
- **The 20% reserve covers experiments too** (Chapter 3 §3.5): candidate evaluation is maintenance of the model layer, not a luxury.
- **Timeboxes over milestones for research-flagged work.** Isochrony rung 3 or emotion prototypes get "two weeks, then a record with a recommendation" — research that can't report in two weeks reports *that*, and the founder decides on renewal. This keeps frontier work from becoming an unbounded tax on a five-person company.
- **Anyone can nominate; the suite adjudicates.** The intern's model nomination and the founder's get the same `run-eval` treatment (Chapter 3's challenge duty, mechanized).

## 19.4 How experimentation stays innovative

The founding brief asked how the company remains innovative. Not by innovation theater (hackathons, "10% time" that dies at the first deadline) but structurally: the flywheel keeps surfacing *real* failures ranked by frequency (Chapter 20), the frontier golden tier turns them into reproducible challenges (Chapter 16 §16.2), the scouting pipeline keeps the candidate stream full (Chapter 15 §15.5), and this chapter keeps the cost of testing a candidate near zero. Innovation at SyncDub is a *pipeline property* — low friction from "what if" to scored answer — not a calendar event. When the friction rises, that is the innovation incident worth a postmortem.

## Key takeaways

- Offline-first: the benchmark set decides most questions in hours; shadow runs catch distribution shift; calibrated panels settle perceptual calls; live splits are rare and opt-in — students are not unconsented test subjects.
- Every experiment pre-registers its decision rule; failed experiments file records too, so dead ends stay dead.
- Velocity is the guarded resource: one-command evaluation, timeboxed research, reserve-funded candidate testing, open nomination.
- Innovation is the low-friction path from hypothesis to scored answer, fed by real production failures — not an event on a calendar.

## Questions founders should ask

1. How long does it take today to get a full score vector for a new model candidate? (If the answer involves a person's afternoon, `run-eval` is overdue.)
2. What was the last experiment whose pre-registered rule said "don't promote" — and was it obeyed?
3. Are shadow runs actually preceding promotions, or has deadline pressure made courage the method again?
4. What's the current hypothesis backlog, and does its ranking reflect correction-frequency data or the most recent customer call?

## Future research topics

- Build `run-eval` as part of the first sovereignty swap (Chapter 15's translation bake-off is its natural first user).
- Define the shadow-sample-size heuristic per stage (how many real jobs before promotion is confident) using early score-variance data.
- Design the "beta program" consent language with Chapter 5's owner so live experiments have a lawful, honest home before anyone wants one urgently.
