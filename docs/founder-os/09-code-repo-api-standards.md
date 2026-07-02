# Chapter 9: Code, Repository & API Standards

> **Part II — Engineering OS** · [← Chapter 8](08-demo-to-service.md) · [Handbook index](README.md) · [Chapter 10 →](10-testing-quality.md)

Standards for a five-person company, strict exactly where violations compound (interfaces, schemas, dependencies, public APIs) and deliberately loose where they don't (formatting taste, internal style debates). Every rule here is enforceable by a machine or a checklist — standards that rely on remembering are wishes.

## 9.1 Repository standards

- **One repo.** The monorepo (backend, frontend, docs, this handbook) stays until a measured reason splits it. Vendored third-party code lives under a `third_party/` path with its license file preserved — `backend/Wav2Lip_repo/` is grandfathered until Chapter 15's swap retires it, but no new vendoring without a license decision record (Chapter 7 §7.1).
- **A `LICENSE` file at root** — currently missing (Chapter 1 §1.2). Until the open-source decision (Chapter 26) is made, the repo is explicitly proprietary; an empty license field is not a neutral default, it is ambiguity.
- **Hygiene enforced by CI, not comments:** formatter (black/ruff for Python, prettier for JS) and linter run on every PR; a failing check blocks merge. No style debates in review — the formatter is the arbiter, chosen once in a decision record.
- **No artifacts in git:** model weights, videos, `progress.json`, logs are gitignored. Weights are fetched by the Stage-0 setup (Chapter 8), never committed.
- **Scratch code has a home:** `scratch/` is gitignored; the root-level `test.py`, `TP.py`, `filelist.txt` era ends. If an experiment is worth sharing, it becomes a documented script under `tools/`; if not, it stays out of history.

## 9.2 Code standards

- **The interface line is the quality line.** Inside a stage adapter, pragmatic code is fine (Chapter 7 §7.3). At interfaces — stage adapters, API handlers, schema definitions — full rigor: type hints, docstrings stating contract and failure modes, and tests (Chapter 10). This two-tier standard is written down precisely so reviews argue about *which tier code is in*, not about taste.
- **Errors are data.** Pipeline failures must set job state with stage and cause — today's pattern of `except: pass` (see the CUDA cleanup in `unload_models()`) and log-and-continue is acceptable only where the failure is genuinely ignorable, and that judgment goes in a comment. A silent failure in ASR shows up as a mystery in lip-sync; error context is how a two-person team debugs a five-stage pipeline.
- **Configuration is explicit.** One settings module, env-var driven, no `os.environ` writes scattered at import time (today: `IMAGEIO_FFMPEG_EXE` and `COQUI_TOS_AGREED` set as side effects at the top of `inference_marathi.py`).
- **Comments state constraints, not narration.** The good existing example: the note that `beam_size=5` was tried and wasn't worth it — that's a measurement preserved. The standard: comments record *why* and *what was ruled out*, never what the next line does.

## 9.3 Code review standards

- **Every change is a PR; every PR has one reviewer.** At current team size the reviewer may be "future you after a night's sleep" for solo work — the discipline of writing the description ("what, why, how verified") is most of the value.
- **Review priorities, in order:** correctness of schema/interface changes → security and trust implications (Chapter 5, 12) → measurement claims ("makes it faster" needs a number) → containment (did ugliness leak wide?) → everything else. A reviewer's approval means "I understand this and would maintain it," not "I skimmed it."
- **Schema changes get the most senior review in the company** (Chapter 7 §7.5) and must be additive unless a decision record says otherwise.
- **Review SLA: one business day.** Blocked authors may escalate; stale reviews are the founder's problem to unblock, because review latency silently sets the company's shipping speed.

## 9.4 API standards

The API is a future product (Chapter 22); these standards start applying with Stage 2–3 of the migration (Chapter 8):

- **Versioned from the first public consumer:** `/v1/` prefix; breaking changes require a new version and a deprecation window, never an in-place change. Internal-only endpoints may break freely until a customer holds a key.
- **Resource-shaped, job-centric:** `POST /v1/jobs` (create dubbing job), `GET /v1/jobs/{id}` (state + artifact URLs), `GET /v1/jobs/{id}/segments` (transcript/translation for the editor). Verbs live in state transitions, not URL names.
- **Errors follow one envelope:** machine-readable code, human message, `job_id`/`stage` context where applicable. The frontend's current guess-from-shape parsing ends with this.
- **Idempotency for anything billable:** job creation accepts an idempotency key, because customers on Indian mobile networks *will* retry uploads, and double-charging a dub is a trust incident, not a bug.
- **Nothing undocumented is public.** An endpoint is public when it appears in the API reference with an example — not when it happens to be reachable.

## 9.5 Dependency standards

- New runtime dependencies require: a license check (the Chapter 1 lesson — a `requirements.txt` line is a legal decision), a maintenance sanity check (is it alive?), and a one-line justification in the PR.
- Pin everything: `requirements.txt` moves to pinned versions with a lock/constraints file; today's unpinned installs mean two clones of the repo can behave differently — which, combined with the Whisper/XTTS environment split, is how "works on my machine" becomes the whole engineering culture.
- The `clone_bridge.py` second environment is documented as what it is: a pinned, containerized sidecar after Stage 0, not folklore about "the other conda env."

## Key takeaways

- Strict where violations compound (interfaces, schemas, deps, public API), loose where they don't; machines enforce, not memory.
- The repo gets a LICENSE, CI-enforced formatting, no committed artifacts, and an end to root-level scratch scripts.
- Two-tier code standard: pragmatic inside adapters, rigorous at interfaces; errors carry stage context; configuration is centralized.
- Reviews prioritize schema > trust > measurement claims > containment; schema changes get the most senior eyes.
- The API is versioned, job-centric, idempotent where money moves, and public only when documented.

## Questions founders should ask

1. Is CI actually blocking merges yet, or are these standards still enforced by memory?
2. What was the last dependency added, and did anyone read its license before merging?
3. Which interface currently has the worst gap between its importance and its documentation?
4. Is review latency measured in hours or in "when someone remembers"?

## Future research topics

- Set up the minimal CI (format, lint, and Chapter 10's tests) as part of Stage 0 — it is the cheapest cultural investment available.
- Evaluate a license-scanning step (e.g., pip-licenses in CI) to mechanize the §9.5 check.
- Define the `/v1/jobs` OpenAPI spec early — it doubles as the design document for Chapter 8's Stage 2–3.
