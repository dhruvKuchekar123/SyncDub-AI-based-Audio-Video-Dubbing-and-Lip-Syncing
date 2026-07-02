# Chapter 1: The State of SyncDub Today

> **Part 0 — Ground Truth** · [Handbook index](README.md) · Next: [Chapter 2 →](02-mission-vision-category-thesis.md)

Every handbook that skips the honest audit becomes fiction. This chapter records exactly what SyncDub is on the day this handbook was written: what works, what is demo-grade, and which parts of the foundation cannot legally carry a company. Every later chapter builds on this baseline. When the system changes, change this chapter in the same pull request.

## 1.1 What SyncDub is right now

SyncDub is a working end-to-end pipeline that takes a Hindi video and produces a Marathi-dubbed, lip-synced video. That sentence is worth more than most pitch decks, because the pipeline actually runs:

1. **Upload** — a React frontend (`frontend/src/App.js`) posts a video to a FastAPI backend (`backend/server.py`).
2. **Audio extraction** — MoviePy pulls the audio track (`extract_audio` in `backend/inference_marathi.py`).
3. **Transcription** — OpenAI Whisper (medium, ~1.5 GB), forced to Hindi with `beam_size=2` as a deliberate speed/accuracy trade-off.
4. **Translation** — `deep-translator`'s GoogleTranslator wrapper, Hindi→Marathi, with segments grouped into context blocks rather than translated line-by-line.
5. **Speaker profiling** — Librosa pitch analysis; median frequency above ~160 Hz selects a female voice, otherwise male.
6. **Speech synthesis** — two paths: Edge-TTS neural voices (`mr-IN-AarohiNeural` / `mr-IN-ManoharNeural`), or XTTS v2 voice cloning via `backend/clone_bridge.py`, a subprocess bridge into a separate Python environment (`USE_VOICE_CLONING = True` in `inference_marathi.py`).
7. **Lip sync** — Wav2Lip, vendored wholesale in `backend/Wav2Lip_repo/`.
8. **Render** — MoviePy merges and writes `outputs/final_dubbed.mp4`.

Progress is reported through a single `progress.json` file written atomically (write-to-temp then `os.replace`) and polled by the frontend.

### What is genuinely good in this code

Do not let the audit below obscure this: the codebase shows correct production instincts.

- **Context-block translation.** Grouping ASR segments before translating preserves Marathi grammar. Most first attempts translate line-by-line and produce garbage. Ours doesn't.
- **Lazy model loading and explicit unloading.** `get_whisper_model()` / `unload_models()` in `inference_marathi.py` manage memory deliberately, including `torch.cuda.empty_cache()`. This is someone who has hit OOM in practice.
- **Corruption defense.** The Whisper loader checks for a truncated model download and deletes it rather than crashing cryptically.
- **Atomic progress writes.** The temp-file-then-rename pattern prevents the frontend from reading half-written JSON.
- **Environment isolation via bridge.** `clone_bridge.py` runs XTTS v2 in a separate Python env through a subprocess because its dependencies conflict with the main env. It is ugly and it works, which is the right order to solve problems in.

These instincts are the seed of our engineering culture. Chapter 7 turns them into principles.

## 1.2 What is demo-grade

The backend is a competition demo, not a service. This is not a criticism — it won the job it was hired for (see `SyncDub_Competition_Guide.md`) — but nobody should mistake it for a product backend.

| Reality in the code | Consequence |
|---|---|
| One global `progress.json`, no job IDs | Two concurrent users corrupt each other's progress. The system is single-tenant by construction. |
| `subprocess.Popen` fire-and-forget in `/upload-video/` | No retries, no failure states, no way to know a job died except reading `pipeline.log`. |
| No authentication, CORS `allow_origins=["*"]` | Anyone who can reach the server can submit jobs and fetch outputs. |
| Output always `outputs/final_dubbed.mp4` | Every job overwrites the previous user's video. |
| Hardcoded `D:/Miniconda3/...ffmpeg.exe` path | The pipeline runs on exactly one Windows machine. |
| Uploaded filename used directly as the save path | Path traversal risk and collision risk in one line. |
| `test.py`, `test_tts.py`, `test_upload.py` | Scratch scripts, not a test suite. There is no CI and nothing for CI to run. |
| No `LICENSE` file in the repo | Our own legal posture is undefined, before we even discuss dependencies. |

Chapter 8 defines the migration path from this to a real service. Chapter 14 defines when each item above *must* be paid down (trigger-based, not calendar-based).

## 1.3 The licensing reality — read this section twice

**Not one component of the current AI pipeline can legally or reliably power a commercial product.** This is the single most important fact in this handbook.

- **Wav2Lip** (`backend/Wav2Lip_repo/README.md`, verbatim): *"This repository can only be used for personal/research/non-commercial purposes."* Worse: its authors commercialized the technology as **Sync Labs** — our core lip-sync dependency is owned by a direct competitor, who profits from our category and controls our license.
- **XTTS v2 / Coqui** (used via `clone_bridge.py`): released under the Coqui Public Model License, **non-commercial**. Coqui the company has shut down, so there is no counterparty to buy a commercial license from.
- **deep-translator → Google Translate**: an unofficial wrapper around the free web endpoint. It violates Google's terms at commercial scale and can be rate-limited or blocked without notice.
- **Edge-TTS**: a reverse-engineered Microsoft endpoint, not a contracted API. It can break or be blocked any day, and offers no SLA, no invoice, and no legal standing.

For a competition prototype this is normal and fine. For a company it is company-ending — an acquirer's diligence or an enterprise customer's security review would surface it in an afternoon. The consequence is one of our deepest architecture principles (Chapter 7): **model sovereignty** — the core pipeline must never depend on a component we cannot legally use, and must treat every model as replaceable behind a stable interface. The near-term replacement candidates (commercially usable ASR, IndicTrans2 for translation, permissively licensed TTS and lip-sync models) are catalogued in Chapter 15.

## 1.4 What does not exist yet

An inventory, so nobody discovers these gaps mid-commitment. Grouped by the part of the handbook that addresses them:

- **Trust & legal** (Ch. 5, 12): consent capture, watermarking, content provenance, misuse policy, terms of service, data-protection posture (DPDP/GDPR), our own repo license.
- **Engineering platform** (Ch. 8, 10, 11, 13): auth, multi-tenancy, job queue, object storage, containerization, CI/CD, tests, observability beyond one append-only log file, staging, incident process.
- **AI research** (Ch. 15–20): golden evaluation sets, automatic dub-quality scoring, isochrony control, diarization/multi-speaker, emotion preservation, model registry, benchmark harness, A/B infrastructure.
- **Product** (Ch. 21–24): human-in-the-loop editor, API keys and metering, billing, pricing, SLAs, onboarding, accessibility, brand.
- **Business** (Ch. 25–26): named target customer, named competitors, GTM plan, unit economics, hiring plan, open-source decision, fundraising narrative.

The point of this list is sequencing, not shame. A company that builds all of this before finding a paying customer dies of thoroughness; one that finds customers without ever building it dies of success. The decision frameworks in Chapter 3 and the trigger rules in Chapter 14 exist to walk that line.

## 1.5 The honest performance baseline

From the competition guide and observed behavior: a 1-minute video takes roughly **3–5 minutes on CPU**; GPU brings it near **1.5× real time**. Whisper medium alone is a 1.5 GB download and the dominant memory consumer; Wav2Lip inference is the dominant GPU consumer. Nobody has yet measured **cost per dubbed minute** — the number that Chapter 11 establishes as the governing metric of the entire infrastructure, and Chapter 24 as the floor under every price we quote.

Quality has never been measured either. We have judge-impressions ("the sync is frame-perfect") but no word-error rate on our own test set, no translation adequacy score, no lip-sync error metric (LSE-C/LSE-D — Wav2Lip's own evaluation harness sits unused in `backend/Wav2Lip_repo/evaluation/`), and no human MOS panel. Chapter 16 exists because of this paragraph.

## Key takeaways

- A real end-to-end Hindi→Marathi dubbing pipeline exists and works. That is rare and valuable.
- The code already carries good engineering instincts; the handbook's job is to systematize them, not import a foreign culture.
- The backend is single-tenant demo infrastructure and must not be marketed as more.
- **Every AI component in the pipeline is legally unusable for commerce.** Model sovereignty is therefore an architecture principle, not a preference.
- Nothing — cost, speed, or quality — is currently measured. Measurement precedes improvement, pricing, and model swaps alike.

## Questions founders should ask

1. If a customer offered to pay tomorrow, which of the licensing items in §1.3 blocks taking their money, and what is the fastest legal path around each?
2. What is our actual cost per dubbed minute today, on CPU and on a rented GPU? (If unknown, that measurement is this week's work.)
3. Which single demo-grade item in §1.2 would embarrass us first with real users — and is it the same one we planned to fix first?
4. When this chapter is six months old, what in it will have silently become false?

## Future research topics

- Benchmark the unused Wav2Lip evaluation harness (`evaluation/scores_LSE/`) on our own outputs to get a first LSE-C/LSE-D baseline before any model swap.
- Measure Whisper medium vs. small vs. large-v3 WER on a held-out Hindi education-video set; the current "medium" choice was never validated.
- Profile the pipeline stage-by-stage to find the true cost driver (hypothesis: Wav2Lip inference, but hypotheses are not measurements).
