# Chapter 7: Architecture Principles

> **Part II — Engineering OS** · [← Chapter 6](06-org-and-hiring.md) · [Handbook index](README.md) · [Chapter 8 →](08-demo-to-service.md)

These principles govern every architecture decision at SyncDub. They are few, they are ranked, and each one earns its place by referencing a real scar or a real moat — not by being a best practice somewhere else.

## 7.1 Principle 1: Model sovereignty

**The core pipeline must never depend on a component we cannot legally use, and every model must be replaceable behind a stable interface.**

This is the Wav2Lip lesson (Chapter 1 §1.3) made permanent: our lip-sync stage is owned by a competitor, our voice cloning is non-commercial-only with no counterparty to license from, and our translation rides an unofficial scraper. Sovereignty has two halves:

- **Legal sovereignty:** every model, weight file, and API in the serving path has a license or contract that permits commercial use, recorded in a decision record (Chapter 3 §3.4) with its revisit-condition ("if this license changes...", "if this vendor is acquired by a competitor..."). A CI check should eventually refuse builds that introduce dependencies without a license record.
- **Technical sovereignty:** each pipeline stage (ASR, MT, TTS, lip sync, and later diarization) is consumed through a stage interface — `Transcriber`, `Translator`, `Synthesizer`, `LipSyncer` — that names *what the stage does*, not which model does it. Today `inference_marathi.py` calls Whisper, GoogleTranslator, and the XTTS bridge directly by name; the refactor to interfaces is priced into the demo-to-service migration (Chapter 8). The bar: swapping a stage's model must never touch code outside that stage's adapter, and must always be justified by evaluation scores (Chapter 16), never by vibes.

The founding brief said "never lock the company to today's AI models." This principle is how that sentence becomes enforceable.

## 7.2 Principle 2: The pipeline is jobs, not calls

Dubbing is minutes-long, GPU-hungry, multi-stage work. Architecturally it is a **job system** — durable jobs with IDs, states, retries, and per-stage artifacts — never a request/response call, and never `subprocess.Popen` fire-and-forget (today's reality in `backend/server.py`). Consequences:

- Every stage writes its artifact (audio, transcript, translation, synthesized audio, rendered video) to durable storage keyed by job ID. Stages become resumable and independently retryable; a Wav2Lip crash doesn't re-run Whisper.
- Job state is the single source of truth the frontend polls and the audit trail (Chapter 5 §5.4) reads — one schema serving product, trust, and the flywheel at once.
- Progress reporting is a property of the job record, not a global `progress.json` file.

Chapter 8 is the migration plan; this principle is why it isn't optional.

## 7.3 Principle 3: Contain the ugly

The house style (Chapter 3): crude solutions are welcome when they are *contained* — behind an interface, in their own process or environment, with a debt entry. `clone_bridge.py` is the canonical example: dependency hell resolved by a subprocess boundary instead of a three-week environment unification. The rule that keeps this healthy:

**Ugliness may be deep, never wide.** A hack inside one stage adapter is fine. A hack that forces callers to know about it (a magic filename, a shared global file, an env var like today's hardcoded `IMAGEIO_FFMPEG_EXE` path) has escaped containment and must be driven back in at the next touch.

## 7.4 Principle 4: Measured evolution

No architecture change ships on aesthetics. Every significant change carries: the metric it should move (cost per dubbed minute, p95 job latency, eval-suite quality score), the measurement before, and the measurement after. This is the engineering face of "measured beats impressive" (Chapter 3) — and it cuts both ways: it blocks resume-driven rewrites *and* it justifies genuinely needed ones with numbers instead of arguments.

Corollary — **boring by default**: Postgres before exotic stores, one queue before an event mesh, a monolith with clean stage interfaces before microservices. The founding brief asked for "Microservice Standards"; our standard is that microservices are an *outcome* of measured scaling pressure on a specific stage (GPU stages will likely split first — Chapter 11), never a starting shape. A five-person company running twelve services is doing distributed-systems cosplay.

## 7.5 Principle 5: The data schema is the architecture

Chapters 4 and 5 both land on the same artifact: the job/segment/correction schema. Per-segment records — source text, timing, translation, edits, quality scores — are simultaneously the moat's raw material, the audit trail, and the pipeline's working state. Design consequence: **schema changes get the most senior review of any change in the company**, and stage adapters may be rewritten freely while the schema evolves only additively. Code is replaceable; the accumulated data is the company.

## 7.6 Anti-principles

Things we explicitly do not value architecturally: horizontal scale before there is load; multi-cloud abstraction before there is one cloud bill worth optimizing; plugin systems before there are two real consumers; configurability before there are two real configurations; real-time paths before batch quality is won (Chapter 3's worked rejection). Each of these is a form of pretending to be the 500-engineer company instead of becoming it.

## Key takeaways

- Model sovereignty — legal and technical — is principle #1, born from the fact that today zero pipeline components are commercially usable.
- The pipeline is a durable job system with per-stage artifacts; request/response and fire-and-forget are architectural bugs.
- Ugly is fine when deep and contained; ugly that callers can see has escaped and must be recaptured.
- Architecture changes ship with before/after measurements; boring technology is the default; microservices are an outcome, not a plan.
- The job/segment/correction schema outranks all code — it is moat, audit trail, and state in one, and it evolves additively under senior review.

## Questions founders should ask

1. Which pipeline stages are still consumed as direct imports rather than through a stage interface, and what does each swap cost today versus after Chapter 8?
2. Does every model in the serving path have a license decision record yet?
3. What was the last architecture change shipped without a before/after metric — and did it actually help?
4. Where has ugliness gone wide (visible to callers) rather than deep this quarter?

## Future research topics

- Define the v1 stage-interface signatures (`Transcriber`, `Translator`, `Synthesizer`, `LipSyncer`) against the current call sites in `inference_marathi.py` — the cheapest possible start on sovereignty.
- Draft the v1 job/segment schema jointly with the correction-schema work from Chapter 4's research topics; they must be one design exercise, not two.
- Evaluate queue options at our scale (a Postgres-backed queue is likely sufficient for years) with a one-page decision record.
