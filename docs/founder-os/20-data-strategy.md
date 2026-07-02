# Chapter 20: Data Strategy & the Correction Flywheel

> **Part III — AI Research OS** · [← Chapter 19](19-experimentation.md) · [Handbook index](README.md) · [Chapter 21 →](21-product-philosophy-editor.md)

Chapter 4 named the correction-data flywheel the company's primary moat. This chapter is its engineering: what data we capture, under what rights, in what shape, and how it converts into quality. The one-line thesis: **SyncDub's most valuable production line is not the dubbing pipeline — it is the correction pipeline that runs whenever a human touches a dub.**

## 20.1 What a correction is

Every editor action on a job is an event: `(job, segment, stage, before, after, action_type, editor, timestamp, rationale?)`. Action types map to pipeline stages — transcript fix (ASR failure), translation fix (MT failure), re-timing (isochrony failure), voice/gender override (profiling failure), emphasis/style change (emotion failure), rejection-and-regenerate (compound failure). The mapping is the point: **each correction is a labeled example of a specific stage failing on a specific input**, which is exactly the supervision signal that eval sets, triage models, and fine-tunes are made of. Freetext "fixed some stuff" editing captures none of this; hence the standing rule (Chapter 4 §4.2) that the editor's structured capture is non-negotiable from v1 — the editor UI (Chapter 21) is downstream of this schema, never the other way around.

## 20.2 Rights: the flywheel runs on consent

The moat cannot be built on quietly repurposed customer content — that is both a Chapter 5 violation and a time bomb under any acquisition diligence. The rights architecture:

- **Corrections-as-data is a contract term, not a discovered behavior.** Customer agreements state plainly: correction events (the deltas, the text) may be used to improve the service; the underlying *media* may not, absent a separate opt-in. Text deltas are the flywheel's fuel anyway — this default gets us most of the value at a consent level customers readily accept.
- **Media opt-in is bought, not assumed.** Voice/video used for training or as frontier-tier eval clips (Chapter 16 §16.2) requires explicit per-customer opt-in, typically exchanged for discount — the education wedge is unusually amenable ("help us make Marathi dubbing better for everyone" is a mission their institutions share).
- **Aggregates are ours; provenance is tracked anyway.** Statistical aggregates (error rates by content type, syllable-rate statistics) carry no customer content and flow freely into research. But every dataset row retains its source-consent lineage, because "which rows may we still use?" must survive any single customer's departure or deletion request (Chapter 12 §12.3 — deletion propagates to derived datasets whose consent died with the account).

## 20.3 From corrections to quality (closing the loop)

Captured corrections convert through four consumers, cheapest first:

1. **The frontier eval tier** (immediate): correction clusters become test cases (Chapter 16 §16.2). A dozen institutes' worth of corrections gives us the only benchmark in existence made of *real Indic production failures*. This consumer requires no ML at all — just the schema and curation time.
2. **Triage calibration** (early): corrections are ground truth for the automatic scorer — segments editors fixed that the scorer passed are the scorer's false negatives (Chapter 16 §16.3's meta-loop). This directly moves review economics, the margin lever of Chapter 21.
3. **Failure-ranked research** (ongoing): the correction stream ranks Chapters 17–18's backlog by observed frequency — isochrony re-timings vs. code-switch mistranscriptions vs. honorific errors — replacing anecdote-driven prioritization (Chapter 19 §19.4's ranking input).
4. **Fine-tuning** (later, gated): when volume suffices, correction pairs fine-tune stage models — translation first (before/after text pairs are the cleanest signal and MT fine-tuning is the most mature path). Gated on: enough data, a Chapter 16 suite able to prove the fine-tune helps, and Chapter 2 §2.4's boundary (narrow fine-tuning, never frontier research).

## 20.4 Dataset governance

Boring on purpose, because dataset chaos is irreversible in a way code chaos isn't:

- **Datasets are versioned, immutable artifacts** with manifests: source jobs, consent lineage, date range, curation rules. "The training data" with no version is as meaningless as "the code" with no commit.
- **One catalog** (a directory of manifests beside the model registry) lists every dataset, its consent basis, and its consumers. When DPDP deletion or a churned customer's rights revocation arrives, the catalog answers "what must be rebuilt?" in minutes.
- **External data enters through the license gate.** Public corpora (AI4Bharat's Indic corpora and similar) are treated exactly like models in Chapter 15 §15.5: license read, decision record, then use. "It was on Hugging Face" is not a rights basis, and dataset licensing hygiene is the difference between our corpus being an asset or a liability at diligence time.
- **The linguist owns curation quality** (Chapter 6 hire #3): inter-editor consistency, rationale sampling, taxonomy evolution. A flywheel spinning on noisy labels amplifies noise.

## 20.5 The cold-start honesty

Today the flywheel has zero rotations: no editor, no customers, no corrections. The strategy is not blocked by this — it is *sequenced* by it: the schema ships before the editor (this chapter), the editor ships with the first customer (Chapter 21), contracts carry the data terms from customer one (§20.2 — retrofitting them is somewhere between awkward and impossible), and the frontier tier starts mattering around the tenth institute. The only cold-start *mistake* available is building v1 without the event schema and the contract language — everything else compounds on its own schedule.

## Key takeaways

- The correction event — job, segment, stage, before/after, type — is the company's most valuable data structure; the editor exists to produce it.
- Rights by design: correction deltas usable by default contract, media only by paid opt-in, every dataset row carrying consent lineage that survives deletion requests.
- Four consumers close the loop: frontier eval cases (no ML needed), scorer calibration (moves review margins), failure-ranked research priorities, and eventually translation-first fine-tuning.
- Datasets are versioned, manifested, cataloged, license-gated, and linguist-curated — dataset chaos, unlike code chaos, cannot be refactored away.
- Cold start is fine; shipping the editor without the schema or signing customers without the data terms are the only unforced errors.

## Questions founders should ask

1. Is the correction-event schema designed and reviewed yet (it was Chapter 4's research topic — has it happened)?
2. Do the draft customer agreements actually contain the corrections-as-data and media-opt-in language?
3. Once live: what fraction of correction events carry a usable `action_type` vs. falling into a generic bucket? (That ratio measures whether the editor UI is serving the schema.)
4. Can we answer "which datasets contain content from customer X?" in one query today — or would deletion be archaeology?

## Future research topics

- Draft the correction-event schema jointly with the Chapter 7/8 segment schema (explicitly the same design exercise, per Chapter 7's research topics).
- Have the data-use contract clauses drafted alongside Chapter 12's DPA template — one legal engagement, both documents.
- Survey AI4Bharat and related Indic corpora licenses now, so external-data options are known before fine-tuning is on any roadmap.
