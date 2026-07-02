# Chapter 12: Security & Compliance Standards

> **Part II — Engineering OS** · [← Chapter 11](11-infra-gpu-cost.md) · [Handbook index](README.md) · [Chapter 13 →](13-reliability-releases.md)

Customer video is sensitive by nature — a professor's face, a company's unreleased course, a government program's content — and our product additionally handles *voice prints*, which are biometric-adjacent personal data. Security here is not a compliance checkbox; it is the engineering half of the trust moat (Chapters 4–5). This chapter is sequenced like everything else in Part II: the embarrassing basics now, the enterprise posture when enterprise pulls.

## 12.1 Where we start (the honest list)

Today's surface, from Chapter 1 §1.2: no authentication, CORS `allow_origins=["*"]`, uploaded filename used directly as a disk path (path traversal), outputs served statically to anyone, secrets and config as scattered environment writes, no HTTPS story, no dependency auditing. None of this is surprising for a demo; all of it ends with the Chapter 8 migration, whose stages carry the fixes: job UUIDs kill filename-as-path (Stage 1), API keys and locked CORS arrive at Stage 3, signed expiring URLs replace static serving at Stage 4.

## 12.2 Baseline standards (apply from the first customer)

- **Tenancy isolation is a query discipline.** Every data access is scoped by `account_id` at the query layer — not filtered in application code after fetching. One shared helper builds scoped queries; direct table access outside it is a review-blocking offense. This single rule prevents the classic multi-tenant leak class.
- **Secrets management:** no secrets in git, in images, or in code (CI check); one secrets store (the platform's native one is fine); rotation is possible without a deploy.
- **Transport and at-rest:** HTTPS only, HSTS on; object storage buckets private-by-default with signed URLs (Stage 4); database encrypted at rest (a checkbox on any managed Postgres — check it).
- **Input handling:** uploads validated by content type and size cap before processing; media processed by ffmpeg/MoviePy is a real parsing attack surface, so workers run as unprivileged users in containers with no outbound network access except what the stage needs — the `clone_bridge.py` isolation habit, generalized into a security boundary.
- **Dependency hygiene:** pinned versions (Chapter 9 §9.5) plus an automated vulnerability scan (pip-audit / npm audit in CI). ML dependency trees are enormous; scanning is not optional at our dependency count.
- **Least privilege for humans too:** production access is named, logged, and minimal. At two engineers this feels silly; it is precisely the habit that cannot be retrofitted at twenty.

## 12.3 Data protection (DPDP/GDPR posture)

India's DPDP Act is our home regime; GDPR is the template enterprise buyers ask about. Our posture, engineered rather than promised:

- **Data inventory by design:** the job schema (Chapter 7 §7.5) *is* the inventory — every artifact traces to an account, a purpose (the job), and a timestamp. What most companies reconstruct in panic before an audit, we get from the architecture.
- **Deletion that actually deletes:** "delete my data" resolves to a deletable per-job storage prefix (Stage 4) plus row deletion, including intermediate artifacts and — critically — **voice reference samples** (`reference_voice.wav` today), which are the most sensitive artifact we hold. Deletion is tested in staging like any feature. The audit ledger's *hashes* (Chapter 5 §5.4) survive deletion by design: proving what we made requires no retained media.
- **Retention by contract, not by default-forever:** every artifact class has a stated retention period; the lifecycle policy (Chapter 11 §11.4) enforces it, so compliance and cost control are one mechanism.
- **Consent records are data too:** attestations (Chapter 5 §5.2) are retained as long as the legal exposure they answer, independent of media deletion.
- **Data residency:** wedge customers (Indian education/government) will increasingly require in-India processing and storage. Choose regions accordingly *now* (jointly with the Chapter 11 GPU sourcing decision) — residency is nearly free as a starting constraint and brutal as a migration.

## 12.4 Security decision-making

How security decisions are made (per the founding brief's demand):

- Security sits inside the **trust layer** of the decision stack (Chapter 3) — above quality, cost, and speed. Concretely: a launch blocked on a tenancy-isolation bug stays blocked, whatever the demo calendar says.
- **Threat-model the deltas.** Big-bang security reviews rot; instead, any PR touching auth, tenancy scoping, upload handling, URL signing, or the consent/audit schema carries a "what could this leak or forge?" paragraph in the description, and gets the trust-priority review of Chapter 9 §9.3.
- **Assume breach in design:** signed URLs expire; keys rotate; workers are sandboxed; blast radius per stolen credential is enumerable. We are a small target today; automated scanning doesn't care about company size.
- **Disclosure readiness:** a `security.txt` and a monitored contact address cost an hour and signal seriousness; when a researcher finds the inevitable bug, we want the report, not the tweet.

## 12.5 What we defer, explicitly

SOC 2 / ISO 27001 certification waits for a named deal that requires it (Chapter 23 sequences this) — but every §12.2–12.3 habit is chosen to *be* the evidence those audits want, so certification becomes paperwork over practice, not a rebuild. Pen tests wait for a public API surface. A bug-bounty program waits for the security team that can triage it.

## Key takeaways

- Security is the engineering half of the trust moat; its fixes ride the Chapter 8 migration stages rather than forming a separate project.
- Tenancy isolation by query discipline, sandboxed media workers, pinned-and-scanned dependencies, secrets out of git — the baseline from customer one.
- DPDP/GDPR posture is architectural: the job schema is the data inventory, deletion is a tested feature (voice samples especially), retention equals lifecycle policy, residency is chosen now.
- Security decisions live in the trust layer of the decision stack; threat-modeling happens on deltas, in PRs, not in annual ceremonies.
- Certifications are deferred but pre-paid: today's habits are tomorrow's audit evidence.

## Questions founders should ask

1. Can any query in the codebase reach another account's rows today? Who checked?
2. Does deletion actually remove voice reference samples and intermediates, and when was that last tested?
3. Which stage of the Chapter 8 migration is the current security posture waiting on, and is anything customer-facing shipping ahead of it?
4. If a security researcher emailed us tonight, does the address exist and does anyone read it?

## Future research topics

- DPDP Act implementation rules: track the actual notification schedule and consent-manager requirements; assign the same owner as Chapter 5's regulatory watch.
- Evaluate container sandboxing depth for media workers (gVisor/firecracker vs. plain containers) once there is a public upload surface.
- Draft the data-processing agreement (DPA) template early — enterprise deals (Chapter 23) will ask, and legal drafting has a long lead time.
