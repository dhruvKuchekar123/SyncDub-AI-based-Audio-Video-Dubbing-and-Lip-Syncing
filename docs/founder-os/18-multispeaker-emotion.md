# Chapter 18: Multi-Speaker & Emotion

> **Part III — AI Research OS** · [← Chapter 17](17-isochrony.md) · [Handbook index](README.md) · [Chapter 19 →](19-experimentation.md)

Today's pipeline assumes one speaker per video: Librosa computes a single median pitch, picks one gender, one voice, and Wav2Lip re-animates whichever face it detects. That assumption fits the wedge (single-lecturer education content) and breaks on everything after it — interviews, panel lectures, dramas, corporate videos with multiple presenters. This chapter is the roadmap from one voice to many, and from words to feeling. It is deliberately *sequenced behind* the wedge: nothing here outranks Chapters 15–17 until customers bring multi-speaker content — but the schema decisions that make it cheap later are made now.

## 18.1 Schema now, features later

The expensive mistake would be baking "one speaker per job" into the data model the way the demo baked it into the code. The rule: **the segment schema (Chapter 7 §7.5) carries a `speaker_id` from v1**, defaulting to a single speaker. Cost today: one column. Alternative cost later: migrating every table, artifact, correction record, and eval score to a concept they were built without. Same logic as tenancy (Chapter 8): identity columns are cheap early and archaeology late.

## 18.2 The multi-speaker ladder

1. **Diarization** — who spoke when. A `Diarizer` stage interface (Chapter 15 §15.1's planned fifth interface) assigning `speaker_id` to segments; mature open models exist (pyannote and successors — license-gate them like everything else, Chapter 15 §15.5 step 2). Diarization errors are *catastrophic* downstream (a voice-swap mid-sentence is worse than any single-voice compromise), so the eval suite gets a diarization axis (DER — diarization error rate) before the feature ships, and low-confidence diarization routes to the editor rather than to production.
2. **Per-speaker voice assignment.** The current pitch-median gender detection generalizes: per-cluster profiling, per-speaker stock voice or clone (each clone requiring its own consent attestation — Chapter 5 §5.2 already speaks per-speaker precisely for this future). The editor shows the speaker map for confirmation; a human glance at "Speaker A / Speaker B, these voices" is cheap insurance against the catastrophic error class.
3. **Per-face lip sync.** The genuinely hard rung: matching *which face on screen* is speaking (active speaker detection) and re-animating only that face. Wav2Lip re-animates naively; multi-face content needs face tracking + speaker-face association. This rung stays research-flagged until a real customer segment demands it — dubbing a panel with correct per-face sync is film-industry territory, and film is not the wedge.

## 18.3 Emotion preservation

The founding brief listed "Emotion Preservation" as a bullet. The honest breakdown of what it actually is, easiest first:

1. **Prosodic carryover in cloning.** XTTS-class models already transfer some speaker affect from the reference sample; today we feed one 10-second reference (`extract_reference_sample`) chosen to avoid intro music, not to represent emotional range. Cheap upgrade: reference selection guided by the content (calm reference for calm lectures) — heuristic, measurable via MOS.
2. **Segment-level emotion tags.** Classify source segments (neutral/emphatic/questioning/excited — small taxonomy, education-content-appropriate) and pass tags to TTS engines that accept style controls. The tag also lands in the segment schema (one more column now, per §18.1) so editors can correct it — flywheel signal for whatever model eventually consumes it.
3. **Emphasis alignment.** The lecturer stresses *this word*; the dub should stress its translation. Requires word-level alignment across translation — genuinely hard, genuinely noticeable in education content ("यह **महत्वपूर्ण** है" losing its stress loses the pedagogy). Research-flagged; the flywheel's editor emphasis-corrections are the eventual training data.
4. **Full affective transfer** (the speaker's exact vocal emotional signature across languages) — frontier research; we adopt (Chapter 15 scouting), never build.

Emotion work is *wedge-relevant* in a way multi-speaker isn't: a monotone dub of an enthusiastic teacher is a worse product even with one speaker. Rungs 1–2 are therefore fair game for near-term quarters; the MOS naturalness axis (Chapter 16 §16.1.3) is their gate.

## 18.4 What this chapter refuses to do yet

No multi-speaker marketing promises before rung 2 ships with DER gates; no "emotion AI" claims ever (we preserve a speaker's delivery, we do not infer feelings — the distinction matters both scientifically and under Chapter 5's bright line); no film/entertainment vertical commitments while the wedge is unwon (Chapter 2 §2.3's expansion order stands).

## Key takeaways

- The single-speaker assumption is acceptable in code and fatal in schema: `speaker_id` (and an emotion tag) enter the segment schema now, at a cost of columns, not migrations.
- Multi-speaker ladder: diarization (DER-gated, editor-verified), per-speaker voices (per-speaker consent — the charter anticipated this), per-face lip sync (research-flagged, not wedge work).
- Emotion is four distinct problems: reference-selection carryover (cheap, now), segment style tags (schema now, models as available), emphasis alignment (hard, flywheel-fed), full affective transfer (adopt from the field).
- Diarization errors and voice mis-assignment are catastrophic-class failures: they route to human review, never silently to production.

## Questions founders should ask

1. Does the segment schema carry `speaker_id` and emotion tags yet — or are we re-baking the demo's assumption into the service?
2. What fraction of inbound customer content is actually multi-speaker? (Measure it in real uploads before funding the ladder.)
3. Is the cloning reference-sample selection still "seconds 5–15, hope for the best"? Rung 1 of emotion is an afternoon of work.
4. Are we marketing anything this chapter's gates haven't cleared?

## Future research topics

- License-gate and DER-benchmark the current diarization field (pyannote and successors) on Indic education audio — accent and code-switch robustness is unstudied territory.
- Prototype emotion-tagged TTS with whichever Chapter 15 TTS finalists accept style controls; MOS-test against untagged baseline.
- Investigate active-speaker-detection models' licenses now (cheap scouting) so rung 3's feasibility is known before a customer asks.
