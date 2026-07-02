# Chapter 22: API-First & Developer Experience

> **Part IV — Product OS** · [← Chapter 21](21-product-philosophy-editor.md) · [Handbook index](README.md) · [Chapter 23 →](23-enterprise-readiness.md)

"API-first" earns its place in this handbook for a structural reason, not a fashionable one: our biggest future customers are *platforms* — ed-tech companies, LMS vendors, media asset systems — who want dubbing inside their product, not ours. The web app and the editor are one consumer of the API; they must never be a privileged one. This chapter defines what that means concretely and when the API becomes a sold product.

## 22.1 API-first, operationally

- **One API.** The frontend, the editor, the CLI, and paying integrators call the same `/v1` (Chapter 9 §9.4). The moment an internal surface uses a private endpoint "just for now," the API's completeness stops being tested by our own product — the cheapest QA we will ever have. (Today's violation, for the record: the frontend's reliance on the static `/outputs/final_dubbed.mp4` mount; it dies at migration Stage 4.)
- **The job is the product's noun** everywhere: create job → poll/webhook state → fetch artifacts → submit corrections. That last item matters: **the corrections endpoint is part of the public API**, so integrators' review UIs feed the flywheel exactly like our editor does (Chapter 20's schema, exposed). An API-tier customer who builds their own reviewer is still spinning our moat.
- **Webhooks over polling** as soon as Stage 3 auth exists: dubbing jobs run minutes-to-hours; forcing integrators to poll is hostile. Signed webhook delivery for `job.completed` / `job.failed` / `job.review_ready`, with polling retained as the fallback.
- **Consent is API-visible.** The attestation and cloning opt-in (Chapter 5 §5.2) are required request fields, not web-form-only ceremonies — integrators inherit our trust posture in their own flows, which is precisely what an education platform's lawyers want to see.

## 22.2 Developer experience standards

DX is a compounding adoption channel (gauntlet question 8) and it is cheap to do well at our size:

- **Docs are the product's front door**: a quickstart that gets a developer from key to dubbed sample clip in under fifteen minutes, an honest reference generated from the OpenAPI spec, and a documented sample video so first calls need no content hunt.
- **Errors teach.** The Chapter 9 error envelope, plus prose: `"consent_attestation missing — see docs/consent"` beats `400 Bad Request` by exactly one saved support ticket per occurrence.
- **One official SDK, Python first** (our audience: ed-tech backends and ML-adjacent integrators), generated plus hand-polished. JavaScript second. Nothing else until asked twice by paying customers.
- **A sandbox that costs us nothing and them nothing**: test keys process only the documented sample clips (pre-computed results served as if fresh) — full API mechanics, zero GPU spend, zero consent ambiguity.
- **Status page and changelog from the first external key.** API trust is mostly communication hygiene: what changed, what broke, what's deprecated, with the Chapter 9 versioning promise visibly kept.

## 22.3 Rate limits, quotas, and metering

Every key carries per-tier quotas (jobs/day, minutes/month) enforced at the API layer — this is the billing meter (Chapter 24) and the abuse throttle (Chapter 5 §5.5's volume-anomaly signal) in one mechanism. Metering is by *dubbed output minute*, matching pricing, so a customer's invoice is explainable from their own API logs. Design rule: **429s must be honest and predictable** — documented limits, remaining-quota headers, no silent throttling; surprise rate limiting burns integrator trust faster than low limits do.

## 22.4 When the API becomes a product

Sequencing, because API-as-product costs support and stability promises that must be bought consciously:

1. **Now → first customers:** the API exists (it's how our own frontend works) but is sold only as part of assisted-tier deals. No public keys.
2. **After the sovereignty swaps + Stage 4** (legal outputs, real storage): design-partner keys — three to five integrators, hand-held, half-price, in exchange for DX feedback and case studies. Their friction list is the DX roadmap.
3. **Public self-serve keys** only when: the benchmark is publishable (Chapter 16 §16.5 — API customers *will* benchmark us unsupervised, so we go public when unsupervised evaluation flatters us), the sandbox exists, and support load per key is known from the design partners.

## 22.5 What API-first does not mean

Not building for imaginary integrators ahead of the wedge (the web product serves the wedge; the API's first consumer is us); not feature-parity paralysis (the editor may ship UI affordances before their API equivalents — but the *data* they produce is always API-shaped); not marketplace/plugin dreams (Chapter 2's platform ambitions activate after Indic leadership, not before; the founding brief's "Marketplace Strategy" is parked exactly there).

## Key takeaways

- API-first means our own products are ordinary API consumers — the frontend using the same `/v1` as integrators is the cheapest completeness test available.
- The corrections endpoint is public: integrators' reviewers feed the flywheel too.
- DX investment order: fifteen-minute quickstart, teaching errors, Python SDK, zero-cost sandbox, status/changelog hygiene.
- Metering equals pricing equals quota — one mechanism, explainable invoices, honest 429s.
- Sequencing: internal API now, design partners after the swaps make outputs legal, self-serve only when the public benchmark and sandbox make unsupervised evaluation safe.

## Questions founders should ask

1. Can our own frontend run entirely on documented `/v1` endpoints today? Every gap is a lie the API tells integrators.
2. How long does key-to-dubbed-sample actually take a fresh developer? (Time it with the next hire's onboarding.)
3. Are the design partners' friction lists actually driving the DX backlog, or are we polishing what's fun?
4. Would an unsupervised integrator's benchmark of us today produce a case study or a churn note?

## Future research topics

- Write the OpenAPI spec early (already a Chapter 9 research topic) — it is simultaneously the Stage 2–3 design doc, the docs source, and the SDK generator input.
- Prototype the webhook signature scheme alongside Stage 3 auth so it isn't retrofitted onto shipped integrations.
- Identify the three ideal design partners from the wedge's adjacent platforms (Marathi ed-tech, LMS vendors serving Maharashtra institutions) — a Chapter 25 conversation with a Chapter 22 deliverable.
