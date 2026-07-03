# Chapter 17: The Isochrony Problem

> **Part III — AI Research OS** · [← Chapter 16](16-evaluation-os.md) · [Handbook index](README.md) · [Chapter 18 →](18-multispeaker-emotion.md)

Isochrony — making translated speech occupy the same time as the original — is the difference between a dub and a voiceover, and it gets its own chapter because it is SyncDub's central research problem: unsolved in our pipeline, under-solved in most competitors', and decisive for perceived quality. A viewer forgives a slightly odd word choice; they do not forgive a speaker whose mouth stops while the voice continues, or Marathi audio drifting seconds behind the visual gestures it belongs to.

## 17.1 Why it's hard, and what our pipeline does today

Languages differ in information density: a Hindi sentence and its Marathi translation take different times to say, and the difference varies per sentence. Today's pipeline (`backend/pipeline.py`) transcribes with timestamps, translates in context blocks, synthesizes each block at the TTS engine's natural pace — and, since rungs 1–2 shipped (`backend/stages/assembly.py`), nudges each block toward its source duration with a capped atempo adjustment and places it at its original timestamp on a silent track exactly as long as the source video. Cumulative drift is eliminated by construction; the residue is per-segment error bounded by the rate cap, which the metric now reports per job. Wav2Lip previously hid the unconstrained version of this sin — it re-animates lips to *whatever* audio it receives — which is exactly why the problem was invisible in demos and corrosive at scale: the lips match the words, but the words no longer match the scene.

The honest statement, updated: **drift is fixed and per-segment error is measured per job (`jobs/{id}/metrics.json`: duration-error distribution, clamp count, overlap); what remains unmeasured is the axis-4 baseline across a benchmark set, and rate-cap clamps still leave residual error on dense segments — rung 3 territory.** (Chapter 16 §16.1 axis 4.)

## 17.2 The metric first

Per the house rule (measured beats impressive), the metric precedes the solutions:

- **Per-segment duration error**: `(dubbed_duration − source_duration) / source_duration`, as a distribution, not an average — one +80% segment ruins a lecture whose mean error is 3%.
- **Cumulative drift**: absolute offset between source and dub timelines over the video — the metric that catches "each segment is fine, the sum is not," which truncation-or-silence failures grow from.
- **Rate deviation**: how far any speed adjustment pushed speech from natural tempo (a +25%-sped-up segment scores perfectly on duration and sounds like an auctioneer; this metric keeps the fix honest).

All three are computable from artifacts the pipeline already produces (Whisper timestamps, synthesized audio lengths). This is days of work and should precede *any* solution investment.

## 17.3 The solution ladder

Ordered by cost; each rung ships value alone, and the metric decides how far up we climb:

1. **Segment-anchored placement (fix the drift) — shipped** (`backend/stages/assembly.py`). Stop concatenating; place each synthesized block at its source timestamp, absorbing small overruns into pause gaps between segments (overrun spill is logged per segment as `overlap_ms`). Eliminates cumulative drift entirely without touching synthesis quality — the ladder's best value-for-effort rung.
2. **Rate adjustment within tolerance — shipped** (`backend/stages/assembly.py`: ffmpeg atempo clamped to [0.85, 1.15], applied uniformly after synthesis for both engines; clamps and residual error land in the per-job metrics). ±10–12% is generally imperceptible; the rate-deviation metric enforces the cap. Cheap, safe inside the cap, ugly beyond it.
3. **Length-aware translation.** The interesting rung, and where Indic depth (Chapter 4) becomes real: generate translations under a syllable/duration budget. Mechanisms: prompt-or-constraint-based length control in the MT stage, or an LLM rephrasing pass ("same meaning, ~20% shorter Marathi") applied selectively to segments the metric flags. This is a *translation* fix for a *timing* problem — the insight most pipelines miss, and one our editor can also crowdsource ("shorten this segment" as a one-click correction feeding the flywheel).
4. **Duration-conditioned synthesis.** TTS that natively targets a duration (the research frontier). We adopt it when the model layer scouts it (Chapter 15 §15.5), not build it.
5. **Pause & prosody engineering.** Redistribute source-speech pauses (Hindi lecturers pause a lot — usable budget) and match emphasis timing. Mostly heuristics on data we already have; polish, not foundation.

The likely stable configuration for the wedge product: rungs 1+2 always on, rung 3 triggered by the metric on offending segments, rung 4 awaited, rung 5 opportunistic.

## 17.4 Interactions the metric must arbitrate

Isochrony trades against the other five axes explicitly: harder rate adjustment (worse voice naturalness), shorter translations (risk to adequacy), tighter timing (better lip-sync scores, since Wav2Lip stops covering gaps). This is the canonical example of why Chapter 16 insists on the score *vector* — an isochrony fix that silently costs adequacy must surface as that trade in the release gate, and the weighting question ("what does the *student* notice more?") is answerable by the customer-calibrated composite, not by engineers arguing.

## 17.5 Strategic note

Isochrony leadership is unusually moat-compatible: it is measurable (we can *prove* superiority on the public benchmark, Chapter 16 §16.5), it compounds through the flywheel (every editor re-timing is training signal for rung 3's selective rephrasing), and it is Indic-specific in its details (syllable-timing patterns, honorific length inflation) exactly where global players under-invest. If SyncDub becomes known for one measured thing, "dubs that keep time" is the right thing.

## Key takeaways

- Isochrony is the gap between dub and voiceover; today we don't control it, don't measure it, and let Wav2Lip disguise it.
- Three metrics (segment duration-error distribution, cumulative drift, rate deviation) are computable from existing artifacts — build them before any fix.
- The five-rung ladder: anchor placement, capped rate adjustment, length-aware translation (the Indic-depth rung), duration-conditioned synthesis (adopt, don't build), pause engineering. Rungs 1–2 are the immediate agenda.
- Every isochrony gain is a potential adequacy/naturalness trade; the eval vector arbitrates, weighted by what students actually notice.
- "Dubs that keep time" is the single best candidate for our provable, benchmarkable, flywheel-compounding technical identity.

## Questions founders should ask

1. What is our duration-error distribution on the benchmark set? (Until answered, this chapter is theory.)
2. Has rung 1 shipped? It requires no research, no new models, and fixes the worst failure class.
3. Are editors re-timing segments in practice, and is that signal being captured in the correction schema (Chapter 4's research topic) for rung 3?
4. Do competitor outputs drift? (Run their trials through *our* drift metric — cheap competitive intelligence and benchmark validation at once, per Chapter 2's research topics.)

## Future research topics

- Implement the three metrics and baseline the current pipeline — the prerequisite for everything above.
- Prototype rung 3 with an LLM rephrase pass on flagged segments; measure adequacy cost with the linguist panel.
- Study syllable-rate statistics for Hindi vs. Marathi on our corpus to set principled rate-adjustment caps, replacing the generic ±10–12% with Indic-specific numbers.
