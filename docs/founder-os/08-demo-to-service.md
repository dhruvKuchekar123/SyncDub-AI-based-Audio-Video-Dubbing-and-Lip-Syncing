# Chapter 8: From Demo to Service

> **Part II — Engineering OS** · [← Chapter 7](07-architecture-principles.md) · [Handbook index](README.md) · [Chapter 9 →](09-code-repo-api-standards.md)

This is the next engineering epic, written as a concrete migration plan from the code that exists (`backend/server.py`, `backend/inference_marathi.py`) to a service that can take money. It is deliberately staged so that each stage ships value alone — the migration can pause at any stage without leaving the system worse than it started.

## 8.1 Where we are (recap of the gap)

One FastAPI process; upload spawns `inference_marathi.py` via `subprocess.Popen` fire-and-forget; a single global `progress.json`; output always `outputs/final_dubbed.mp4`; no auth; CORS `*`; uploaded filename used as the disk path; Windows-hardcoded ffmpeg location. Single-tenant by construction (Chapter 1 §1.2).

## 8.2 Target shape (v1 service, not v10 platform)

A deliberately boring target, per Chapter 7's principles:

- **One API service** (FastAPI stays) + **one worker process** consuming a **Postgres-backed job queue** + **object storage** for artifacts. No Kubernetes, no Redis, no microservices. Postgres does jobs, users, segments, and audit in one place.
- **Job model:** `job(id, account_id, state, created_at, ...)`, states `queued → running(stage) → review → done | failed(stage, error)`; per-stage artifact rows pointing into object storage; per-segment rows carrying transcript/translation/timing (the Chapter 7 §7.5 schema).
- **Stage interfaces:** `Transcriber / Translator / Synthesizer / LipSyncer` adapters wrapping today's exact implementations — the sovereignty refactor (Chapter 7 §7.1) done as part of the move, not as a separate rewrite.
- **Auth:** account-scoped API keys (hashed at rest). Enough for first customers and the API product's foundation (Chapter 22); OAuth/SSO waits for enterprise pull (Chapter 23).
- **Consent capture:** the uploader attestation and cloning opt-in from Chapter 5 §5.2 enter the upload flow *here*, in v1 — retrofitting consent after customers exist is far harder.

## 8.3 The staged migration

Each stage is independently shippable and reversible:

1. **Stage 0 — Portability (days).** Kill the hardcoded `D:/Miniconda3/...` ffmpeg path and `COQUI_TOS_AGREED` scattering; configuration via environment/settings file; a `Dockerfile` that runs the pipeline end-to-end on CPU. Exit test: a teammate (or CI) runs the pipeline on Linux from a fresh clone.
2. **Stage 1 — Job identity (days).** Every upload gets a UUID; inputs stored as `uploads/{job_id}/source.mp4` (killing the filename-as-path traversal risk); outputs as `outputs/{job_id}/dubbed.mp4`; `progress.json` becomes `progress/{job_id}.json`. Frontend passes the job ID. Two users stop corrupting each other *before* any queue exists.
3. **Stage 2 — The queue (week).** Jobs table in Postgres; API enqueues; a worker loop claims jobs (`SELECT ... FOR UPDATE SKIP LOCKED`), runs the pipeline in-process, heartbeats, and writes state. `Popen` dies here. Retry-per-stage arrives with per-stage artifact records. Concurrency = number of workers, controlled and observable.
4. **Stage 3 — Accounts, keys, consent (week).** Accounts table, API keys, per-account job listing; the attestation checkbox and cloning opt-in recorded on the job row; CORS locked to the real frontend origin. The audit ledger (input/output hashes, Chapter 5 §5.3) is two columns on tables that now exist.
5. **Stage 4 — Object storage & artifacts (week).** Local disk paths replaced by S3-compatible storage keyed by job; signed URLs replace the static `/outputs` mount; retention policy becomes a deletable prefix per job (the Chapter 12 deletion story starts working).
6. **Stage 5 — Observability (ongoing).** Structured logs with `job_id`/`stage` fields replacing the single `pipeline.log`; per-stage duration and cost metrics emitted — feeding the cost-per-dubbed-minute measurement Chapter 11 governs by.

Sequencing rationale: identity before queue (Stage 1's UUID work is what Stage 2's schema keys on), queue before accounts (accounts without job isolation are cosmetic), storage after accounts (signed URLs need identity). The consent items ride Stage 3 because that's when the schema they attach to exists.

## 8.4 What we keep

Migration plans fail by rewriting what works. Explicitly preserved: the pipeline logic itself (`inference_marathi.py`'s stage functions move behind adapters largely intact), the lazy load/unload memory discipline, the atomic-write pattern (now applied to DB transactions instead of JSON files), the `clone_bridge.py` subprocess isolation (now invoked by the worker), and the React frontend (its polling model maps directly onto job-state polling).

## 8.5 What "done" means

The migration is complete when: two customers can run jobs concurrently without interference; a killed worker resumes or retries its job without operator archaeology; every output traces to an account, an attestation, and input/output hashes; and a new engineer can run the whole system locally with `docker compose up`. That last clause is also the hiring work-sample environment (Chapter 6 §6.3).

## Common mistakes this plan is designed against

- **The platform rewrite.** Kubernetes + microservices + Redis + a message bus for a system with zero concurrent users. Our ceiling-check: Postgres-backed queues comfortably serve thousands of jobs/day; we will be thrilled to have that problem.
- **The parallel system.** Building v2 beside v1 and cutting over "when ready." Every stage above modifies the live system and ships alone.
- **Auth last.** Deferring accounts until "after launch" means retrofitting tenancy onto data with no tenant column. Stage 3 is early on purpose.
- **Skipping Stage 0.** Every subsequent stage is untestable by anyone but the founder's Windows machine until portability lands.

## Key takeaways

- Target: API + Postgres queue + worker + object storage. Boring, sufficient for years, and each piece earns later replacements with measurements (Chapter 7 §7.4).
- Six stages, each shippable alone: portability → job identity → queue → accounts/consent → object storage → observability.
- Consent capture and the audit ledger enter at Stage 3 — trust infrastructure rides the migration rather than following it.
- The pipeline's working logic, memory discipline, and bridge isolation are kept, not rewritten.

## Questions founders should ask

1. Which stage is live today, and does anything in flight violate "each stage ships alone"?
2. Has anyone other than the founder run the full pipeline end-to-end yet? (Stage 0's exit test is the hiring unblock.)
3. Are consent attestations actually recorded on jobs, or did Stage 3 ship as auth-only under time pressure?
4. What did Stage 5's first cost-per-minute numbers reveal, and did they surprise us?

## Future research topics

- Postgres queue implementation choice (hand-rolled `SKIP LOCKED` loop vs. a small library) — one-page decision record.
- Signed-URL expiry and download UX for large video files on Indian mobile networks.
- Whether Whisper/Wav2Lip model weights live in the image, a volume, or a model cache service at Stage 0 — affects both cold-start time and the Chapter 15 registry design.
