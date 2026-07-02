# Chapter 16: The Evaluation OS

> **Part III — AI Research OS** · [← Chapter 15](15-model-layer.md) · [Handbook index](README.md) · [Chapter 17 →](17-isochrony.md)

You cannot swap, buy, price, or improve what you cannot measure. Every hard decision in this handbook — the sovereignty swaps, quantization trades, routing tiers, release gates, even competitive positioning — resolves into "run the eval suite and compare." This chapter builds that suite. It is also the strategic centerpiece: Chapter 4 named quality-metric ownership a moat; the company that defines how Indic dub quality is measured referees the category.

## 16.1 What a dub score must capture

A dubbed video can fail in six distinguishable ways, so the metric is a six-axis vector before it is a single number:

1. **Transcription fidelity** — did we hear the Hindi right? Metric: WER against reference transcripts. Fully automatic once references exist.
2. **Translation adequacy & fluency** — is the Marathi faithful and natural? Metrics: chrF/BLEU against reference translations for regression detection, plus periodic human adequacy ratings — automated MT metrics are weakest exactly where our moat is (idiom, code-switching, honorifics), so the linguist's panel (Chapter 6 hire #3) calibrates them rather than being replaced by them.
3. **Voice quality & similarity** — does it sound human, and (cloning path) like the speaker? Metrics: MOS panels for naturalness; speaker-embedding cosine similarity for cloning fidelity. Semi-automatic.
4. **Isochrony** — does speech fit the original timing? Metric: per-segment duration error distribution (Chapter 17 defines it precisely). Fully automatic, and currently *unmeasured while probably being our worst axis*.
5. **Lip sync** — do the lips match the audio? Metrics: LSE-C/LSE-D via SyncNet — the evaluation harness for this is already sitting unused in `backend/Wav2Lip_repo/evaluation/scores_LSE/` (Chapter 1 §1.5). Fully automatic.
6. **Delivery integrity** — structural sanity (duration, non-silence, A/V mux). Already specified as production post-conditions (Chapter 13 §13.1).

The **composite dub score** is a weighted roll-up for dashboards and marketing; *decisions* use the vector, because a composite hides exactly the trade-offs that matter (a TTS swap that gains naturalness but breaks isochrony must be visible as that trade).

## 16.2 Golden sets

Three tiers of curated test data, each answering a different question:

- **The smoke set** (~5 clips, the Chapter 10 fixtures): does the pipeline work? Runs everywhere, cheap.
- **The benchmark set** (30–50 clips, the real asset): stratified across our actual failure surface — male/female speakers, clean/noisy audio, slow lecture/fast conversation, pure Hindi/heavy code-switching, with reference transcripts and reference translations produced by the founding linguist. This is what model swaps and releases are judged on. Building it is *the* prerequisite for the entire Chapter 15 agenda and is measured in linguist-days, not engineer-months.
- **The frontier set** (grows from the flywheel): every correction cluster from real customer content (Chapter 20) becomes a test case. This tier is the moat mechanically realized — our benchmark converges on the failures that occur *in production Indic content*, which no competitor can replicate without our traffic.

Governance: golden sets are versioned and immutable per version (changing the test redefines every historical score — Chapter 10 §10.3's rule); reference answers get the same senior review as schema changes; scores always cite the set version.

## 16.3 Automatic quality scoring in production

The same axes, run on *every production job* (not just releases), at the automatic-only level: WER proxies (ASR confidence), duration-error stats, LSE scores, embedding similarity. Three consumers:

1. **Review triage** (the operational payoff): jobs above a confidence threshold ship with light review; below it, full editor pass. This is what makes human review scale sub-linearly with volume — the economics of Chapter 21 depend on this mechanism.
2. **Drift detection**: rolling score charts on the reliability dashboard (Chapter 13 §13.3) catch slow degradation no single job reveals.
3. **The flywheel's sensor**: score-vs-correction data (did editors fix what the scorer flagged?) continuously validates the scorer itself — the meta-loop that makes the metric trustworthy enough to sell against.

## 16.4 Benchmarking discipline

Rules that keep scores honest, several already broken once each in our own history:

- **Same set, same conditions, or it isn't a comparison.** The `beam_size=2` choice in `inference_marathi.py` was a real measured trade-off (good) recorded only as a code comment (bad). Benchmark results live in the registry (Chapter 15 §15.2) with dates and set versions.
- **No demo-driven evaluation.** A model that "looked great on the video we tried" has a score of undefined. The competition-demo instinct (Chapter 1) is our native bias; the suite is its antidote.
- **Cost rides along.** Every benchmark run records CPDM impact next to quality (Chapter 11 §11.3) — a quality-only leaderboard invites unaffordable winners.
- **Humans are calibrated, not assumed.** MOS/adequacy panels use fixed rubrics, multiple raters, and inter-rater checks; a panel that can't agree with itself can't judge a model.

## 16.5 The public benchmark (the moat move)

Once the benchmark set is mature and our scores are respectable: publish it — the set (rights-cleared tier), the metrics, the methodology, and a leaderboard scoring every tool in the market including us. Referees are hard to displace; challengers must either compete on our axes (where Indic depth favors us) or argue with the methodology (attention we welcome). Timing gate, stated coldly: publish only when we win or place credibly on our own benchmark — publishing a leaderboard we lose is competitor marketing at our expense. Chapter 25 owns the launch; this chapter owns the integrity that makes it defensible.

## Key takeaways

- Dub quality is a six-axis vector (ASR, translation, voice, isochrony, lip sync, integrity); composites are for dashboards, vectors are for decisions.
- Three golden tiers: smoke (works?), benchmark (30–50 stratified clips with linguist references — the prerequisite for all model swaps), frontier (correction-derived, the moat made mechanical).
- Automatic scoring runs on every production job, triaging review effort, catching drift, and validating itself against editor corrections.
- Benchmarks are versioned, cost-annotated, and demo-proof; human panels are calibrated instruments.
- The endgame is publishing the category's benchmark — after we can win it.

## Questions founders should ask

1. Does the benchmark set exist yet with linguist-made references? Every week it doesn't, every model decision is being made on vibes.
2. What are our own LSE-C/LSE-D numbers? (The tool ships in our repo; ignorance here is a choice.)
3. Is review triage actually driven by scores yet, and what is the false-confidence rate (shipped-with-light-review jobs that customers then flagged)?
4. Which axis is weakest this quarter, and does the roadmap reflect that or the loudest anecdote?

## Future research topics

- Stand up the LSE scoring harness from `Wav2Lip_repo/evaluation/` on current outputs — the fastest path to any real number on any axis.
- Evaluate reference-free MT quality estimators (COMET-QE class) for the production scorer, validated against the linguist's ratings.
- Design the composite-score weighting *with customers*: what educators rate as "bad dub" should set the weights, not internal intuition.
