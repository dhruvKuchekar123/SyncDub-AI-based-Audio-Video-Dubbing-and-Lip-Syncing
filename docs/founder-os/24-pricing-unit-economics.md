# Chapter 24: Pricing, Packaging & Unit Economics

> **Part IV — Product OS** · [← Chapter 23](23-enterprise-readiness.md) · [Handbook index](README.md) · [Chapter 25 →](25-gtm-competitive-strategy.md)

Pricing is a product decision — it tells the market what we are — and a strategy decision — the corridor between human-dubbing costs and our CPDM *is* the business (Chapter 2 §2.3). This chapter sets the pricing philosophy, the packaging that expresses the tiers, and the unit-economics discipline that keeps the corridor real. Numbers here are placeholders with reasoning attached; the reasoning is the standard, the numbers get replaced by measurement.

## 24.1 The corridor

Three reference points define our room:

- **Ceiling — human dubbing.** Professional Indic dubbing runs at studio rates that price most education content out entirely (which is why the content sits untranslated — the market's existence proof). Whatever the current quote per finished minute is in Mumbai studios, that is the ceiling's order of magnitude: *thousands of rupees per minute*.
- **Floor — our CPDM** (Chapter 11), *honestly loaded*: compute, storage, licensed model fees post-swap (the fake zero made real, §11.1), review minutes, support. Unmeasured today; the first measurement is scheduled work, and until it exists every price is a guess wearing confidence.
- **Reference — global competitors' INR-translated pricing** (Rask/HeyGen-class subscriptions). Relevant mostly as the anchor *international-minded* customers arrive holding; our wedge buyers compare against the ceiling and against ₹0-and-stay-undubbed, not against Silicon Valley SaaS tiers.

The pricing thesis: **price per dubbed minute, an order of magnitude below human dubbing, at a healthy multiple above loaded CPDM** — concretely, target a CPDM:price ratio of 1:4 or better, reviewed monthly (Chapter 11 §11.1), because model fees, GPU markets, and review ratios will all move under us.

## 24.2 The unit, defended

The billing unit is the **dubbed output minute** (matching the API meter, Chapter 22 §22.3). Rejected alternatives, recorded so they stay rejected: per-video (punishes short content, invites 3-hour "videos"), per-seat (our value scales with content volume, not humans logged in — seat pricing invites one-login institutes), flat unlimited (an invitation to be someone's free GPU farm), credits-with-expiry (short-term revenue, long-term resentment; wedge institutions budget annually and hate breakage). Per-minute is explainable in one sentence, maps to cost, and survives procurement scrutiny.

## 24.3 Packaging: the tiers price the slider

Packaging mirrors the workflow tiers (Chapter 21 §21.3), so the price list *teaches the product*:

- **Auto (API)**: lowest per-minute rate; confidence report included; no review. For integrators (Chapter 22 §22.4's sequencing gates when this is even available).
- **Assisted** (the wedge default): mid rate; editor seats included free (the editor feeds the flywheel — charging for it would tax our own moat); volume-tiered per-minute discounts, because the 400-lecture institute is exactly whom we want and volume improves both flywheel and margin.
- **Managed**: highest rate, quoted per project; priced to *discourage* all but strategic cases (the 30% agency alarm, Chapter 21 §21.3).
- **Enterprise wrapper** on any tier: residency, SLA, SSO, invoicing — priced as the Chapter 23 ledger dictates, on named asks.

**Cloning as premium**: voice cloning carries a per-minute premium over stock neural voices — it costs more (heavier synthesis, consent workflow) and is worth more (the teacher's-own-voice value, Chapter 2 §2.3.4). The premium also usefully throttles cloning to customers serious enough to complete consent properly.

**The free tier is a demo, not a tier**: a few minutes of watermarked-output trial (visible watermark — the honest kind, Chapter 5 §5.3), enough to prove quality on *their* content, structurally incapable of being a production freeloader. In a GPU-cost business, generous free tiers are venture-subsidized marketing we cannot and should not copy.

## 24.4 Unit-economics discipline

- **The weekly number is CPDM:price by tier.** Margin erosion is quiet and specific: one enterprise deal's review-heavy content, one model swap's fee structure, one customer's pathological audio. Per-tier (eventually per-account) unit tracking finds it while it's a conversation, not a crisis.
- **Review minutes are the swing variable.** At target, assisted-tier review cost falls as triage improves (Chapter 16 §16.3.1) — this is the *margin expansion story*: the flywheel doesn't just improve quality, it widens gross margin every quarter the scorer gets better. That sentence is also the investor narrative's economic core (Chapter 26).
- **Discounts buy something.** Volume discounts buy flywheel data; design-partner discounts buy case studies and DX feedback (Chapter 22 §22.4); media-opt-in discounts buy training rights (Chapter 20 §20.2). A discount that buys nothing is just margin donated to negotiation theater — every non-list price names what it purchased, in the deal record.
- **Price changes are experiments with records** (Chapter 19's discipline applied): hypothesis, cohort, decision rule, result. Grandfather existing customers by default — wedge institutions run on annual budgets and trust; repricing them mid-year spends the moat to make a quarter.

## 24.5 The honest sequence

Today, with unlicensed models and no consent flow, **we cannot charge anyone anything** (Chapter 1 §1.3) — pricing work is therefore: (1) measure CPDM on the current pipeline now (it bounds every plan), (2) complete the sovereignty swaps that make revenue legal, (3) pilot-price the first three institutes individually against measured CPDM with the 1:4 target, (4) publish the price list only after three pilots confirm the review-minutes assumption — the number most likely to surprise us.

## Key takeaways

- The corridor — human-dubbing ceiling, loaded-CPDM floor — is the business; target CPDM:price of 1:4+, reviewed monthly.
- Bill per dubbed output minute; the rejected alternatives stay rejected for recorded reasons. Packaging mirrors the automation slider; cloning is premium; the free tier is a watermarked demo.
- Review minutes are the swing variable, and triage improvement is the margin-expansion story — the flywheel compounds economically, not just qualitatively.
- Every discount purchases something named; every price change is a recorded experiment; pilots precede price lists.
- Nothing is chargeable until the swaps land — which makes CPDM measurement and the Chapter 15 agenda the *revenue* roadmap, not just the legal one.

## Questions founders should ask

1. What is loaded CPDM this week, by tier, and is any tier's ratio drifting below 1:4?
2. What did each active discount purchase, and did we collect it (the case study, the data rights, the feedback)?
3. What are actual review-minutes-per-dubbed-minute in the pilots vs. the pricing assumption?
4. Is anything being sold today that Chapter 1 §1.3 says cannot legally be sold?

## Future research topics

- Get three real quotes for human Marathi dubbing of a one-hour lecture (the ceiling deserves data, not folklore).
- Model the assisted-tier P&L at 10 / 100 / 1,000 dubbed hours per month using measured CPDM — the spreadsheet that answers "when does this fund itself?"
- Survey wedge buyers' budget cycles and procurement thresholds (the price *format* — annual contract vs. per-minute metered — may matter more than the price level in education).
