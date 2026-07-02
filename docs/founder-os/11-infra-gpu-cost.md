# Chapter 11: Infrastructure, GPU & Cost Standards

> **Part II — Engineering OS** · [← Chapter 10](10-testing-quality.md) · [Handbook index](README.md) · [Chapter 12 →](12-security-compliance.md)

The founding brief asked for "GPU Standards." The correct standard is one level up: **cost per dubbed minute (CPDM) is the governing metric of all infrastructure**, and every GPU, instance, and storage decision is a move in the CPDM game. This ordering matters because our strategy (Chapter 2 §2.3) depends on a price corridor — human dubbing far above us, our costs far below our price — and infrastructure is where that corridor is either defended or squandered.

## 11.1 CPDM: definition and discipline

**CPDM = total marginal cost to produce one minute of reviewed, delivered, dubbed video.** It decomposes into: compute (per stage), storage and egress, third-party API fees (today ₹0 because we're using unlicensed free endpoints — a fake zero that Chapter 15's swaps will make real and honest), and the human review minutes it triggers (Chapter 21 — yes, editor time is in CPDM; excluding it is how "AI-first" companies discover they run an agency).

Disciplines:

- **Measured, not modeled.** Stage 5 of the migration (Chapter 8) emits per-stage duration and resource use per job; CPDM is computed from real jobs weekly. Today nobody knows this number (Chapter 1 §1.5) — the first measurement is this chapter's most urgent action.
- **Decomposed by stage.** The hypothesis is that Wav2Lip inference dominates GPU time and Whisper dominates memory, but hypotheses are not measurements. The stage breakdown decides where optimization effort goes; optimizing an already-cheap stage is theater.
- **Tracked against price.** Chapter 24 sets price per dubbed minute; the CPDM:price ratio is reviewed monthly. Margin erosion arrives quietly, one convenient instance-type upgrade at a time.

## 11.2 GPU standards

- **Rent, never buy, until utilization proves otherwise.** Owned hardware is justified only when measured sustained utilization would repay it inside ~18 months — a spreadsheet check in a decision record, not an instinct. Early-stage GPU ownership is how startups convert runway into depreciating paperweights.
- **Right-size per stage, not per pipeline.** ASR, TTS, and lip sync have different GPU appetites; running the whole pipeline on the GPU the *hungriest* stage needs means paying peak price for every stage. The job system's per-stage structure (Chapter 7 §7.2) lets stages run on different instance classes once volume justifies the split — this, not microservice fashion, is the measured reason GPU stages split first.
- **Batch is our friend.** Nothing in the wedge product is latency-critical (a lecture dub returning in an hour is fine — Chapter 3 rejected real-time). That unlocks the cheap end of every market: spot/preemptible instances with checkpoint-resume (per-stage artifacts make resumption natural), off-peak scheduling, and aggressive batching of Wav2Lip inference. Our latency tolerance is a *cost weapon*; guard it against product creep that would casually promise "results in minutes."
- **Utilization is the KPI, not the fleet.** One dashboard number: GPU-hours paid vs. GPU-hours doing work. Below ~60%, fix scheduling before adding capacity.

## 11.3 Model-serving standards

- Weights load once per worker lifetime, not per job — today's per-run loading of Whisper (1.5 GB) is rational for a demo script and ruinous for a service; the worker model (Chapter 8 Stage 2) amortizes it.
- The lazy-load/explicit-unload discipline from `inference_marathi.py` survives as the *within-worker* memory policy for stages that can't co-reside.
- Quantization/compression (e.g., faster-whisper, int8) are evaluated like any model change: through the Chapter 16 suite with CPDM attached. A 40% cost cut for one eval-point drop is usually a great trade — but it goes through the gate, not around it.

## 11.4 Storage and bandwidth standards

Video is heavy, and Indian egress fees are real money at scale:

- Artifacts stored per job with a **lifecycle policy from day one**: source and output retained per customer contract; intermediate artifacts (extracted WAVs, frame caches) deleted on job completion + a debugging grace window. Storing everything forever is a silent CPDM tax and a Chapter 12 liability at once.
- Egress discipline: signed, expiring URLs; no free unlimited re-downloads in the product's default tier; output bitrate/resolution defaults chosen for the actual viewing context (a student's phone) rather than videophile pride — with the Chapter 3 caveat that quality-crushing compression fails the "student is the user" test. Measured, again: pick the lowest bitrate that doesn't move review scores.

## 11.5 Environment standards

Three environments, no more: **local** (docker compose, CPU paths, stub adapters — the Chapter 8 Stage 0 deliverable), **staging** (real models, small GPU, golden tests and nightly evals live here), **production**. Infrastructure is code (even if it's a well-commented Terraform file and a bootstrap script); the console is for looking, not changing. Anything clicked into existence is one outage away from being unreproducible.

## Key takeaways

- Cost per dubbed minute — including honest license fees and human review time — governs all infrastructure; measure it weekly from real jobs, decomposed by stage.
- Rent GPUs, right-size per stage, exploit our batch latency tolerance as a cost weapon (spot instances, off-peak, batching); watch utilization, not fleet size.
- Load weights per worker, not per job; quantization goes through the eval gate with CPDM attached.
- Storage has a lifecycle from day one; egress is designed, not discovered.
- Three environments, all reproducible from code.

## Questions founders should ask

1. What is CPDM this week, which stage dominates it, and how has it moved month-over-month?
2. What fraction of CPDM is currently a "fake zero" (unlicensed free endpoints) and what does it become after the sovereignty swaps?
3. Has any product promise crept toward latency guarantees that would forfeit the batch-cost weapon?
4. If our biggest customer 10×'d volume next month, which line item breaks first — GPU capacity, storage, or review hours?

## Future research topics

- First real CPDM measurement: instrument the current pipeline (even pre-migration) with per-stage timing and run ten representative jobs on a rented GPU vs. CPU.
- Benchmark faster-whisper/int8 Whisper against the current medium model on the Chapter 16 golden set with cost attached.
- Price out Indian-region GPU availability (major clouds vs. Indian providers like E2E/AceCloud) — data-residency pressure from Chapter 12 may constrain this choice, so do it once, jointly.
