# Chapter 26: Open Source, Community & Investor Readiness

> **Part V — Business OS** · [← Chapter 25](25-gtm-competitive-strategy.md) · [Handbook index](README.md) · [Appendix A →](appendix-a-checklists.md)

Three decisions the founding brief asked for that share one property: they are cheap to decide now and expensive to reverse later. This chapter decides them — explicitly, with revisit-conditions, in the decision-record spirit of Chapter 3.

## 26.1 The open-source decision

**Decision: open-core, with the moat line as the boundary.** The moat map (Chapter 4) makes this almost mechanical — open what is already table stakes, keep what compounds:

- **Open (when ready):** stage interface definitions and adapters, the benchmark harness and its rights-cleared golden tier (Chapter 16 §16.5 — the benchmark *must* be open to be a referee), eval metric implementations (isochrony metrics included: we *want* the industry measuring on our axes — every published LSE or drift score anywhere reinforces our category framing), and eventually the pipeline glue that Chapter 4 already declared fake-moat.
- **Closed:** the correction schema's accumulated data and datasets (the moat itself), the triage/scoring calibrations learned from it, the editor, the routing/cost machinery, and everything trust-infrastructure (open-sourcing consent tooling invites forks that strip it).
- **Sequencing:** nothing opens before the sovereignty swaps complete — open-sourcing a pipeline whose components we can't legally ship commercially would be performative — and the first open artifact is the benchmark, because it does marketing, hiring, and moat work simultaneously.
- **Revisit-condition:** if a credible open-source Indic dubbing stack emerges from elsewhere, the calculus flips from "should we open?" to "can we afford not to lead it?" — that event reopens this record within the quarter.

Until then, the immediate housekeeping this decision unblocks: the repo gets its `LICENSE` (proprietary for now — Chapter 9 §9.1's missing file), and vendored third-party licenses stay scrupulously preserved.

## 26.2 Community strategy

Community for us is three concentric circles, funded in this order: **(1) The reviewer/linguist community** — the Marathi translators and educators who use or staff the editor; a small, real practitioner network (the founding linguist's orbit, Chapter 6) that feeds curation quality, managed-tier capacity, and the most credible word-of-mouth in the wedge. Unglamorous and first. **(2) The developer community** — activates with public API keys (Chapter 22 §22.4); until then, DX investment *is* the community strategy. **(3) The benchmark community** — researchers and rivals engaging with the published benchmark; success here looks like citations and submissions, and it is the only circle where competitor participation is the *goal*. What we do not do: Discord-server theater ahead of having anything for members to do, or "developer relations" hires before developers exist (Chapter 6 §6.2's non-hires, extended).

## 26.3 Investor readiness

The narrative, assembled from the handbook rather than invented for the deck — which is the point: **diligence-proof storytelling is just the truth, indexed.**

- **The story:** massive under-served market (Indian-language content access), a wedge with existence proof (education back-catalogs, Chapter 2), an economic engine with a compounding margin story (the flywheel widening gross margin as triage improves — Chapter 24 §24.4, the single most fundable sentence we own), and defensibility a VC can audit (the moat map, the benchmark, the data terms in actual contracts).
- **Milestones that map to raises:** the Chapter 25 phase gates *are* the funding gates — three-institutes-renewing de-risks seed; repeatable pilot motion + benchmark published + design partners live de-risks Series A. Raising against calendar instead of gates is how the expansion order (Chapter 2 §2.3) gets sold to the highest bidder.
- **The diligence file, maintained not assembled:** decision records, the model registry with licenses (the Chapter 1 §1.3 problems *visibly solved* — an acquirer's counsel will look exactly there), consent/data-rights contract terms, CPDM history, the debt register. A data room that is just our normal documentation is itself a signal most startups can't fake.
- **What we don't do for investors:** vanity metrics (registered users of a free demo tier), GMV theater via the managed tier (the 30% alarm, Chapter 21 §21.3, exists partly for this), or roadmap promises the eval suite hasn't blessed. The founding brief asked this handbook to resemble a world-class company's internals; the investor corollary is that we show internals instead of theater.

## 26.4 International expansion, held honestly

The brief asked for an international strategy; the honest version at our stage is a *trigger list, not a plan*: diaspora education demand appearing in lost-deal notes; an Indic pair's flywheel maturity making a structurally similar language family (the isochrony and honorific machinery generalizes) cheap to enter; or a design partner carrying us into a market we didn't choose. Until a trigger fires, international is a standing temptation to violate the expansion order — and this section exists mainly so that refusal has a citation.

## Key takeaways

- Open-core with the moat line as the boundary: benchmark and metrics open (referee status requires it), data/editor/calibrations closed, nothing before the swaps; the repo finally gets its LICENSE.
- Community funds practitioners first, developers when keys exist, benchmark-engagers as the endgame — no community theater.
- The investor narrative is the handbook indexed: flywheel-widens-margin is the fundable sentence, phase gates are the funding gates, and the data room is our ordinary documentation kept honest.
- International expansion is a trigger list; this section is the citation for saying "not yet."

## Questions founders should ask

1. Has the LICENSE file landed yet? (The cheapest item in the entire handbook to keep failing.)
2. If a lead investor asked for the data room next week, which artifact would be embarrassing — the registry, the CPDM history, or the contracts?
3. Is any raise being timed by calendar or burn rather than by phase gates, and is that a choice or a drift?
4. Which open-source revisit-condition or international trigger is closest to firing?

## Future research topics

- Draft the open-source license choice for the future benchmark release (data licensing differs from code licensing — CC variants vs. Apache; a decision record when release nears).
- Study how benchmark-led credibility played out for comparable companies (the referee strategy has precedents worth mining for timing mistakes).
- Maintain a quarterly one-page "state of the gates": phase-gate progress against Chapter 25, moat health against Chapter 4 — the standing input to both board conversations and this chapter's revisit-conditions.
