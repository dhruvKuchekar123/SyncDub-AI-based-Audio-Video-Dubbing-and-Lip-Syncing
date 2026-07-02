# Appendix A: Review Checklists

> **Appendices** · [← Chapter 26](26-open-source-community-investors.md) · [Handbook index](README.md) · [Appendix B →](appendix-b-claude-protocol.md)

The handbook's decision rules, consolidated into the three checklists that get used at the moments decisions actually happen. Each item cites its chapter — a checklist answer that surprises you is a chapter to reread. These lists are deliberately short: a checklist longer than a screen gets skipped under exactly the deadline pressure it exists for.

## A.1 Architecture Review Checklist

Run before merging any change to system structure, schemas, stages, or dependencies.

- [ ] **License gate:** every new model/dependency has a commercial-use-compatible license and a decision record. (Ch. 7 §7.1, Ch. 9 §9.5, Ch. 15 §15.2)
- [ ] **Interface discipline:** model/stage specifics stay behind stage interfaces; no caller learns a model's name. (Ch. 7 §7.1, Ch. 15 §15.1)
- [ ] **Job-system shape:** long work is durable jobs with IDs, states, per-stage artifacts — no fire-and-forget, no global files. (Ch. 7 §7.2, Ch. 8)
- [ ] **Schema conservatism:** segment/job/correction schema changes are additive, senior-reviewed, and carry `speaker_id`/tag foresight. (Ch. 7 §7.5, Ch. 18 §18.1)
- [ ] **Containment:** any shortcut is deep, not wide — invisible to callers, registered in `docs/debt.md` with a trigger. (Ch. 7 §7.3, Ch. 14)
- [ ] **Measurement attached:** performance/cost claims come with before/after numbers; CPDM impact estimated for pipeline changes. (Ch. 7 §7.4, Ch. 11)
- [ ] **Boring by default:** no new infrastructure category (service, store, queue) without a fired need; microservices only as measured outcome. (Ch. 7 §7.4)
- [ ] **Tenancy & trust surfaces:** account-scoped queries only; auth/upload/URL-signing changes carry a threat-model paragraph. (Ch. 12 §12.2, §12.4)
- [ ] **Reversibility:** the change deploys behind expand-then-contract migrations and can be reverted by redeploy. (Ch. 13 §13.2)

## A.2 Product Review Checklist

Run before committing to any feature, tier, or customer promise.

- [ ] **Gauntlet passed:** ≥3 honest yeses on the ten questions; trust gate (question 10) is a hard pass. (Ch. 3 §3.3)
- [ ] **Wedge alignment:** serves Hindi→Marathi education excellence now, or has a written revisit-condition. (Ch. 2 §2.3, Ch. 3 §3.5)
- [ ] **Bright line intact:** transforms consented content only; no fabrication pathway; consent UX not weakened. (Ch. 5 §5.1–5.2)
- [ ] **Flywheel check:** does it generate structured correction data — and if it touches editing, does it emit typed events, not freetext? (Ch. 4 §4.2, Ch. 20 §20.1)
- [ ] **Student test:** improves or preserves the end-viewer's experience on a cheap phone, not just the buyer's checklist. (Ch. 3 §3.2, Ch. 21 §21.1)
- [ ] **Measurement shipped with it:** the metric that will judge the feature exists at launch. (Ch. 21 §21.1)
- [ ] **Priced honestly:** unit-economics impact estimated; discounts purchase something named; enterprise asks tied to named deals. (Ch. 24, Ch. 23 §23.2)
- [ ] **Latency tolerance preserved:** no casual real-time or turnaround promises that forfeit the batch-cost weapon. (Ch. 11 §11.2, Ch. 3 §3.3)
- [ ] **API-shaped:** the capability exists (or is planned) as a documented `/v1` surface, not a frontend privilege. (Ch. 22 §22.1)

## A.3 Engineering Review Checklist

Run on every non-trivial PR; the reviewer's working list.

- [ ] **Tier identified:** is this interface-tier code (full rigor: types, contracts, tests) or adapter-interior (pragmatic)? Argue the tier, not the taste. (Ch. 9 §9.2)
- [ ] **Tests at the right layer:** logic → unit; stage behavior → contract; wiring → golden; quality claims → eval floors. Escaped-bug fixes include the test that would have caught them. (Ch. 10)
- [ ] **Errors carry context:** failures set job/stage state; no new silent `except: pass` without a justifying comment. (Ch. 9 §9.2, Ch. 13 §13.1)
- [ ] **Config centralized, secrets absent:** no import-time env mutations, nothing sensitive in git. (Ch. 9 §9.2, Ch. 12 §12.2)
- [ ] **Dependencies pinned & licensed:** new entries justified in the PR, license read. (Ch. 9 §9.5)
- [ ] **Model changes are releases:** eval floors run, version recorded on jobs, registry updated, shadow considered. (Ch. 13 §13.2, Ch. 15)
- [ ] **Debt honesty:** touching a registered-debt area either repays or extends the entry in this PR. (Ch. 14 §14.3)
- [ ] **Post-conditions & observability:** new pipeline behavior is visible in job metrics and covered by structural post-conditions where applicable. (Ch. 13 §13.1, §13.3)
- [ ] **Docs & handbook truth:** if this PR falsifies a handbook statement, the same PR fixes the handbook. (Index rule; Ch. 13 §13.4)

## A.4 The meta-checklist (quarterly, founder)

- [ ] Re-read Chapters 2, 4, 24; answer every "Questions founders should ask" in writing, honestly. (Index)
- [ ] Debt register vs. reality; fired triggers funded from the reserve. (Ch. 14)
- [ ] CPDM:price by tier; managed-revenue vs. the 30% alarm. (Ch. 24, Ch. 21 §21.3)
- [ ] Competitive snapshot re-verified; anyone else accumulating Indic correction data? (Ch. 25 §25.5)
- [ ] Phase-gate and revisit-condition sweep: what fired unnoticed? (Ch. 3 §3.4, Ch. 26)
