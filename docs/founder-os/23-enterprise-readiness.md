# Chapter 23: Enterprise Readiness

> **Part IV — Product OS** · [← Chapter 22](22-api-first-dx.md) · [Handbook index](README.md) · [Chapter 24 →](24-pricing-unit-economics.md)

"Enterprise" in our market means education boards, university systems, large coaching chains, media houses, and government skilling programs. They buy differently: procurement processes, security questionnaires, contracts with SLAs, invoices instead of cards, and — in our category specifically — *someone whose job depends on the dub not embarrassing the institution*. This chapter defines what enterprise-ready means for SyncDub and, more importantly, **when each piece gets built: on a named deal's demand, not on speculation.** Premature enterprise-building is how startups drown the wedge product in checkbox features; late enterprise-building loses one deal, teaches the lesson, and the second deal closes.

## 23.1 What our enterprise buyers actually require

Ranked by how often it decides the deal, per the realities of Indian institutional procurement:

1. **Accountability for output quality.** The assisted tier's review workflow (Chapter 21 §21.3) with named reviewer sign-off *is* the enterprise feature — an audit trail showing a human approved each published lecture. We get this almost free from the correction schema; sell it as governance, because that is what it is.
2. **Trust documentation.** Consent chain, provenance ledger, misuse policy, deletion story (Chapters 5, 12) — packaged as a plain-language trust dossier a procurement officer can forward. The engineering exists by design; the *packaging* is a marketing-week task that closes deals disproportionate to its cost. Government content programs in particular will make synthetic-media governance a tender requirement before most vendors can spell C2PA; being early here is the Chapter 4 trust moat converting into revenue.
3. **Data residency and confidentiality.** In-India processing (the Chapter 11/12 joint region decision), a signable DPA (Chapter 12's research topic), and honest answers about model training on their content (Chapter 20 §20.2's contract terms — our default *is* the answer they want).
4. **Commercial plumbing.** GST invoices, purchase orders, NEFT payment, multi-year quotes, and rate-contract formats for government. Zero engineering, real close-rate impact; a founder-afternoon with an accountant, not a roadmap item.
5. **SSO and role separation.** Reviewer vs. admin roles arrive with the editor's tiers naturally; SSO (Google Workspace covers Indian education overwhelmingly) waits for the first deal that names it — it is a Stage 3 auth extension, priced into that deal.
6. **SLAs.** Per Chapter 13 §13.5: an SLA is a priced promise. Our battery: job-completion time targets (not uptime theater — buyers care when the semester's lectures land), support response tiers, and a re-run-free remedy for quality incidents. Signed only at volumes where the roster answers 2 a.m. (or the price funds the roster that does).
7. **Certifications.** SOC 2/ISO 27001 on a named deal's written requirement only — with Chapter 12's habits as pre-paid evidence, certification is months of paperwork, not years of rebuild. In Indian education procurement it is asked about more often than actually required; the trust dossier usually satisfies.

## 23.2 The enterprise feature gate

Standing rule extending the gauntlet (Chapter 3 §3.3): **an enterprise feature is built when a named account with a plausible close names it as blocking, and its cost is priced into that deal.** Speculative enterprise work fails gauntlet question 10 by default. The one standing exception is anything in the trust dossier — that is moat work (Chapter 4) that happens regardless of deals.

Corollary — the **enterprise readiness ledger**: a one-page list of known future asks (SSO, SOC 2, on-prem, VPC peering) each marked "awaiting named deal," with rough cost. When a prospect names one, the conversation is a lookup, not a scramble, and the deal prices it knowingly.

## 23.3 On-prem and air-gapped, answered in advance

The wedge's government edge will eventually ask for on-premise deployment — the `Project_Specifications.md` future-scope already intuited this ("offline translation... full air-gapped security"). The prepared answer: the sovereignty swaps (Chapter 15) move us toward self-hostable open models *anyway*; the job-system architecture (Chapter 8) containerizes *anyway*; therefore a single-tenant "SyncDub appliance" is a packaging problem, not a rewrite — but an expensive packaging problem (support, upgrades, GPU procurement on their side), so it is quoted at a price that reflects a forked operational burden, and only for deals that justify a dedicated engineer-quarter. Until then: in-India cloud with residency guarantees answers 90% of the underlying concern at 10% of the cost.

## 23.4 Support standards

Support is tiered like everything else: self-serve docs and status page (all tiers, Chapter 22 §22.2); named-contact email with response targets (assisted tier); a shared channel and quarterly review call (enterprise). Two disciplines keep it sane: **support tickets are correction data too** — quality complaints route into the same triage that ranks the research backlog (Chapter 20 §20.3) — and **the founder reads every ticket until hire #5 exists** (Chapter 6), because at this stage support *is* customer discovery wearing a different hat.

## Key takeaways

- Our enterprise buyers purchase accountability, trust documentation, residency, and commercial plumbing before they purchase features — and most of that we get by packaging what Chapters 5, 12, 20, 21 already build.
- The gate: enterprise features are built on named deals and priced into them; the trust dossier is the standing exception because it is moat work.
- Keep an enterprise-asks ledger so prospects' requirements meet prepared answers with known costs.
- On-prem is a foreseen packaging problem made cheaper by decisions already taken (open models, containerized jobs) — quoted expensively, built reluctantly, never before a deal that funds it.
- SLAs are priced promises; support is customer discovery; every quality ticket feeds the flywheel.

## Questions founders should ask

1. Does the trust dossier exist as a forwardable document yet? It is the highest-leverage sales asset this chapter names.
2. What is on the enterprise-asks ledger right now, and did anything get built this quarter without a named deal attached?
3. Can we issue a GST invoice against a purchase order today without improvisation?
4. Which prospective deal is closest to naming SSO, SOC 2, or on-prem — and is the priced answer ready?

## Future research topics

- Draft the trust dossier from Chapters 5 and 12's commitments (a writing task, not an engineering one) and test it on a friendly procurement officer.
- Research Maharashtra government empanelment/tender norms for content-services vendors — the wedge's government edge has formal entry rules worth knowing early.
- Estimate the true cost of a single on-prem deployment (support hours, upgrade path, their-GPU sizing) so the §23.3 quote is grounded before it is ever needed.
