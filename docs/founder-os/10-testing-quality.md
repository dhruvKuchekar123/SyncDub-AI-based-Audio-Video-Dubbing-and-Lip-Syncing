# Chapter 10: Testing & Quality Engineering

> **Part II — Engineering OS** · [← Chapter 9](09-code-repo-api-standards.md) · [Handbook index](README.md) · [Chapter 11 →](11-infra-gpu-cost.md)

Testing an ML pipeline is different from testing a CRUD app: the most important outputs are probabilistic, the heaviest components take minutes and gigabytes, and "correct" is a score, not a boolean. This chapter defines what "tested" means at SyncDub, layer by layer, so that "the tests pass" is a meaningful sentence. Today it is not: `test.py`, `test_tts.py`, and `test_upload.py` are scratch scripts with no assertions, no runner, and no CI.

## 10.1 The four layers

**Layer 1 — Unit tests (deterministic logic).** Fast, no models, no network. Prime targets already in the codebase: segment grouping into context blocks (a pure-logic function with real linguistic consequences), pitch-threshold gender classification given synthetic pitch arrays, progress-state transitions, path/naming logic (the Stage-1 job-ID work), translation retry/backoff behavior with a mocked translator. Run on every PR; measured in seconds.

**Layer 2 — Contract tests (stage adapters).** Each stage interface (`Transcriber`, `Translator`, `Synthesizer`, `LipSyncer` — Chapter 7 §7.1) gets a contract suite that any implementation must pass: given a 5-second fixture, returns segments with monotonic timestamps; given Devanagari input, output is valid UTF-8 Marathi text; given text and a reference voice, produces a playable WAV of plausible duration; errors raise typed exceptions with stage context (Chapter 9 §9.2). Contract tests are what make model swapping (the sovereignty principle) safe *mechanically*, before evaluation makes it safe *qualitatively*. Run on every PR against fake/stub implementations; against real models nightly.

**Layer 3 — Golden pipeline tests (end-to-end, small).** Three to five short fixture videos (10–20 seconds: one male speaker, one female, one noisy audio, one code-switched Hindi-English) run through the entire real pipeline on a schedule and before any release. Assertions are structural and tolerant, not byte-exact: pipeline completes, every stage artifact exists, output video duration within tolerance of input, audio track non-silent, transcript non-empty and Devanagari. These catch the "someone broke stage wiring" class of failure that unit tests can't see and eval suites are too slow for. Byte-exact comparison of media outputs is a known false-negative factory — never assert on encoded bytes.

**Layer 4 — Evaluation suites (quality as a number).** WER on our Hindi test set, translation adequacy, isochrony error, LSE-C/LSE-D for lip sync, and eventually automatic dub-quality score — Chapter 16 owns the definitions. The testing chapter's rule about them: **eval scores are release gates, not dashboards.** A model or prompt change that drops the suite score below its floor does not ship, exactly as a failing unit test does not merge. This is the mechanical link between the testing culture and the quality moat.

## 10.2 What we deliberately do not test

Honesty about the budget: no UI pixel tests (the frontend gets Layer-1 logic tests and one smoke test that the app renders and can poll a mocked job); no load testing before there is load (Chapter 8's ceiling analysis stands in); no fuzzing beyond input-validation basics until the attack surface is public (Chapter 12 revisits); no coverage-percentage targets, ever — coverage is a flashlight, not a KPI, and chasing it produces assertion-free tests like the ones we're replacing.

## 10.3 Fixtures and test data

- A `fixtures/` directory of small, *rights-cleared* clips — we cannot test a consent-first product on videos we don't have rights to (Chapter 5 eats its own cooking). Record them ourselves; a founder reading two sentences of Hindi in four acoustic conditions is an afternoon's work and a permanent asset.
- Fixtures are versioned and immutable; changing a fixture is a schema-level review event (it silently redefines every downstream score).
- Real customer content never becomes test data without the explicit consent path from Chapter 20; "it was handy" is a trust violation, not a shortcut.

## 10.4 CI reality

Minimal viable CI (rides Chapter 8 Stage 0): every PR runs format + lint + Layer 1 + Layer 2 (stubbed) in minutes, CPU-only. Nightly runs Layer 2 (real models) + Layer 3 on a GPU runner when one exists, CPU meanwhile — slow nightly beats absent. Release runs everything plus the Layer 4 floors. A red nightly is triaged the next morning, not silenced: a flaky golden test is a real bug in either the pipeline or the test, and both are worth a morning.

## 10.5 The cultural rule

**A bug found by a customer that a Layer 1–3 test could have caught costs a test, not a blame.** Every incident postmortem (Chapter 13) asks "which layer should have caught this?" and the fix PR includes that test. This is how the suite grows to fit *our* failure modes instead of a textbook's.

## Key takeaways

- Four layers: unit (logic, every PR), contract (stage interfaces, what makes model swaps mechanically safe), golden pipeline (small end-to-end fixtures, structural assertions), evaluation (quality scores as release gates).
- Media outputs are asserted structurally, never byte-exactly; eval floors block releases exactly like failing tests.
- Fixtures are small, rights-cleared, versioned, and immutable; customer content is never casually test data.
- No coverage targets, no load tests before load, no pixel tests — the budget goes where our failures actually are.
- Every escaped bug buys the test that would have caught it.

## Questions founders should ask

1. Can a new engineer run Layers 1–2 locally in under five minutes? If not, testing is still folklore.
2. When did the golden pipeline last go red, and was it triaged or silenced?
3. Which release gate has been waived recently, by whom, and is that written down?
4. Do our fixtures cover the failure modes customers actually hit (noise, code-switching, multiple speakers), or the ones that were easy to record?

## Future research topics

- Record the v1 fixture set (four clips, rights-cleared) — an afternoon that unblocks Layers 2–3.
- Investigate deterministic-mode options for Whisper/TTS inference (seeds, temperature) to tighten golden-test tolerances.
- Evaluate lightweight GPU CI options (a single spot instance on a nightly cron beats a hosted-runner bill) alongside Chapter 11's cost work.
