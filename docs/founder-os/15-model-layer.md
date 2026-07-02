# Chapter 15: The Model Layer

> **Part III — AI Research OS** · [← Chapter 14](14-tech-debt.md) · [Handbook index](README.md) · [Chapter 16 →](16-evaluation-os.md)

The founding brief demanded: "Never lock the company to today's AI models. Design for the next generation of AI." This chapter is the mechanism. The model layer has four parts — stage interfaces, a registry, a routing policy, and a replacement pipeline — and one immediate mission: replacing every legally-blocked component identified in Chapter 1 §1.3.

## 15.1 Stage interfaces (recap and contract)

From Chapter 7 §7.1: `Transcriber`, `Translator`, `Synthesizer`, `LipSyncer` (later `Diarizer`, Chapter 18). Each contract specifies inputs/outputs in *domain terms* (audio + language → timed segments; segments + target language → translated segments; text + voice spec → audio; video + audio → video), typed failures, and the metadata every implementation must return: model identifier, version, processing cost hints. The contract-test suites (Chapter 10 Layer 2) enforce mechanically that implementations are interchangeable.

The subtle design rule: **interfaces encode the *task*, not the current model's shape.** Whisper returns rich segment objects; a future streaming ASR might not. The interface owns the segment schema (Chapter 7 §7.5); adapters translate whatever their model emits into it. When a next-generation model collapses two stages into one (e.g., direct speech-to-speech translation), it implements *both* interfaces behind a combined adapter — the pipeline shape survives even when models merge stages.

## 15.2 The model registry

Every model usable in production has a registry entry (a directory of YAML files under `models/registry/` is entirely sufficient — the registry is a discipline, not a product):

- identity: name, version, weights hash or API version
- **license status and the decision record link** (the sovereignty gate — Chapter 7 §7.1; no entry, no deploy)
- eval scores on the current golden suites, with dates (Chapter 16)
- cost profile: per-minute compute on reference hardware (feeds CPDM, Chapter 11)
- operational notes: memory footprint, environment/bridge requirements, known failure modes

Every job records which registry entries processed it (Chapter 13 §13.2's model-releases-are-releases rule). This is what makes questions like "which customers received outputs from the buggy TTS version?" answerable in one query instead of one archaeology.

## 15.3 The sovereignty swaps (the immediate agenda)

Current stage-by-stage replacement agenda, each item a decision-record-to-be with candidates to benchmark, not conclusions:

| Stage | Today (status) | Candidates to evaluate |
|---|---|---|
| ASR | Whisper medium (MIT — **legal, keep**) | faster-whisper (cost), large-v3 (quality), IndicWhisper-style Indic fine-tunes |
| Translation | deep-translator scraping Google (**ToS-blocked**) | IndicTrans2 (AI4Bharat, open, Indic-specialized — the obvious first benchmark), NLLB, licensed cloud MT as fallback tier |
| TTS/cloning | Edge-TTS (unlicensed endpoint) + XTTS v2 (**non-commercial**) | Licensed commercial APIs; permissive open models with Marathi support (a moving field — survey at benchmark time, not in this document) |
| Lip sync | Wav2Lip (**non-commercial, competitor-owned**) | MuseTalk and successors (verify licenses individually), commercial lip-sync APIs, licensed-Wav2Lip negotiation as a priced option |

Two honest notes. First, ASR is already legal — the licensing crisis is really a translation/TTS/lip-sync crisis, which usefully narrows the work. Second, the lip-sync column is the hardest: the field's strongest models trend non-commercial, so the realistic v1 outcome may be a *commercial API* at honest CPDM cost (Chapter 11's "fake zero" made real) while open alternatives mature. The registry's cost field exists precisely so that trade can be made with numbers.

Swap order follows exposure: translation first (ToS-blocked *and* the best open replacement exists), TTS second, lip sync third (hardest, and non-commercial use remains legal while revenue is zero — but it must be swapped before the first rupee).

## 15.4 Routing policy

Once the registry holds more than one live implementation per stage, routing chooses per job. Routing inputs: customer tier (Chapter 24's quality/cost tiers), content properties (duration, noise, language pair), and cost state. The v1 policy is a lookup table in code — explicitly not an ML system; a routing decision must be explainable to a customer in one sentence ("your tier uses X"). Learned routing is a someday-entry gated on the eval suite being able to *judge* it.

## 15.5 The replacement pipeline (how models enter and exit)

The permanent process, so next-generation adoption is routine rather than heroic:

1. **Scout** — candidate spotted (paper, release, license change). Anyone can nominate; a registry stub records it.
2. **License gate** — before any engineering: license read, decision record drafted. Kills most candidates cheaply.
3. **Adapter + contract tests** — implement the stage interface; pass Layer 2. Typically days, thanks to the interface work.
4. **Benchmark** — run the Chapter 16 suites; record scores and cost in the registry. No benchmark, no opinion: advocacy without scores is noise (Chapter 3's "measured beats impressive").
5. **Shadow** — run beside production on real jobs (Chapter 13 §13.2); compare automatic scores and spot-check with the founding linguist (Chapter 6 hire #3).
6. **Promote / archive** — routing table updated by decision record; the loser stays in the registry with its scores, because today's loser is next year's re-benchmark shortcut.

Exit follows the same path in reverse: a model leaves routing before it leaves the registry, and never leaves the registry's history — job records point at it forever (audit, Chapter 5 §5.4).

## Key takeaways

- Four mechanisms — task-shaped interfaces, a YAML registry with license/eval/cost per model, explainable routing, and a six-step replacement pipeline — turn "never lock to today's models" from a wish into a process.
- Interfaces encode tasks, not current model shapes; merged next-gen models implement multiple interfaces behind one adapter.
- The immediate agenda: translation swap first (IndicTrans2 benchmark), TTS second, lip sync third — all before the first rupee of revenue.
- Every job records its models; every model records its license, scores, and cost. No registry entry, no deploy; no benchmark, no opinion.

## Questions founders should ask

1. Which stage would take the longest to swap today, and is that the same answer as last quarter (i.e., are the interfaces actually landing)?
2. Has the IndicTrans2 benchmark run yet? It is the single cheapest de-risking action on the legal agenda.
3. What would we do if the chosen lip-sync vendor doubled prices — does the registry hold a scored, ready alternate?
4. Are job records actually carrying model versions, or is that still aspirational?

## Future research topics

- Run the translation bake-off (deep-translator vs. IndicTrans2 vs. one licensed API) on the golden set — this both fixes the worst legal exposure and forces the Chapter 16 metrics into existence.
- Survey the current Marathi-capable TTS field with licenses in a single scouting doc (step 1–2 of the pipeline, batched).
- Watch for speech-to-speech translation models maturing — they merge three of our stages, and §15.1's combined-adapter rule is the plan for that day; a small prototype ahead of need would validate it.
