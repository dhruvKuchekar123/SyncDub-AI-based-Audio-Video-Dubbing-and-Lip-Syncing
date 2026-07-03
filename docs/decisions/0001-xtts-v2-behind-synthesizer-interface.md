# 0001 — Keep XTTS v2 as the cloning engine, behind the Synthesizer interface

- **Status:** accepted (2026-07-03)
- **Owners:** founder
- **Related:** Founder OS Ch. 5 (consent), Ch. 7 §7.1 (sovereignty), Ch. 15 §15.3 (licensing table), Ch. 17 (isochrony), docs/debt.md #1

## Context

Voice cloning is the product's differentiator, and XTTS v2 is the only cloning
engine already integrated (via the `clone_bridge.py` subprocess containment).
Two problems forced a decision:

1. **It never actually ran.** The bridge was invoked with `--language mr`,
   which XTTS v2 does not support, so every job silently fell back to stock
   Edge-TTS voices.
2. **The XTTS v2 weights are CPML (Coqui Public Model License) —
   non-commercial.** Whatever we build on it cannot legally take revenue.

## Options considered

1. **Keep XTTS v2, fixed, behind a new `Synthesizer` interface** (chosen).
   Zero licence cost today; the pipeline becomes engine-agnostic, so the
   commercial swap is an adapter + registry entry, not a rewrite.
   Price: the cloning path stays demo/pilot-only until the swap.
2. **Add a commercial cloning API (e.g. ElevenLabs) now.** Commercially
   shippable immediately; per-character cost, an external data-processor for
   voice prints (Ch. 12 residency/consent implications), and no benchmark set
   yet to justify the choice (Ch. 16 §16.2: no benchmark, no opinion).
3. **Swap to a permissively licensed open model.** Cleanest licence; the
   Marathi-capable permissive field was not surveyed and quality is unproven —
   this is the Ch. 15 §15.5 scouting pipeline, not a decision to make blind.

## Decision

Keep XTTS v2 as the only cloning engine, with:

- the `Synthesizer` interface (`backend/stages/synthesizer.py`) so engine
  swaps never touch pipeline code (repays docs/debt.md #1 for the TTS stage);
- Marathi synthesized via the **Hindi proxy code** (shared Devanagari script,
  close phonology; `xtts_is_proxy` flag logged per run) because XTTS v2 has no
  native Marathi;
- **whole-job fallback** to stock voices on any cloning failure — never a
  mid-video voice change; wasted GPU time on partial success is accepted;
- cloning **opt-in per job with recorded speaker consent** (Ch. 5 §5.2);
  default path remains stock neural voices;
- non-commercial status stated wherever the engine is named
  (requirements-clone.txt, adapter docstring, this record).

## Revisit condition

Any of:

- **first paying customer in sight** (the Ch. 15 swap order already schedules
  TTS/cloning replacement before the first rupee of revenue);
- Coqui/successor changes the CPML terms or a licensed XTTS offering appears;
- the Marathi-via-Hindi proxy scores below usable on speaker-similarity or
  MOS once the benchmark set (Ch. 16 §16.2) exists.

Revisiting means running the Ch. 15 §15.5 replacement pipeline (scout →
license gate → adapter → benchmark → shadow → promote), for which the
Synthesizer interface built here is the prerequisite.
