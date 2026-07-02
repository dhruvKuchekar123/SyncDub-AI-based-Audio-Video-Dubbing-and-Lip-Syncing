# Chapter 13: Reliability, Releases & Failure Analysis

> **Part II — Engineering OS** · [← Chapter 12](12-security-compliance.md) · [Handbook index](README.md) · [Chapter 14 →](14-tech-debt.md)

SRE-lite: the smallest set of reliability practices that a team of two can actually sustain, chosen so that each one scales rather than needing replacement. The organizing insight for *our* product: *a batch pipeline fails differently than a website.* Users don't experience downtime; they experience **jobs that never finish, finish wrong, or finish silently**. Reliability engineering at SyncDub is therefore job-completion engineering first and uptime engineering second.

## 13.1 What reliability means here

Ranked reliability objectives (our SLO seeds, formalized when customers hold contracts — Chapter 23):

1. **No lost jobs.** Every accepted job terminally reaches `done` or `failed(stage, cause)` — never limbo. Today's `Popen` fire-and-forget violates this by design; the queue with heartbeats (Chapter 8 Stage 2) is the fix, and "worker died mid-job" is the first failure mode it must handle (retry or resume from the last stage artifact).
2. **No silent wrongness.** A job that completes with an empty transcript, silent audio, or a 3-second output for a 10-minute input is worse than a failure — it reaches a customer. The golden-test structural checks (Chapter 10 Layer 3) run as **post-conditions on every production job**, not just in CI; violations flip the job to `failed` rather than `done`. This is cheap and catches the class of bug that erodes trust fastest.
3. **Honest progress.** The progress a customer sees reflects job state truthfully, including "queued behind N jobs" and "failed at translation, will retry." The current UI's optimistic percentage is demo culture (Chapter 1); a truthful queue position retains customers better than a stuck 60%.
4. **API availability.** Last, deliberately: the API being briefly down delays *submissions*; the pipeline being wrong damages *outputs*. Effort follows harm.

## 13.2 Release standards

- **Releases are boring, small, and reversible.** Deploy from `main` via CI only (no laptop deploys — reproducibility is Chapter 11 §11.5's environment rule applied to people); every release must be revertible by redeploying the previous image, which forbids coupled irreversible migrations — schema changes ship additively first (expand), code moves over, cleanup follows (contract).
- **Model releases are releases.** Swapping a model, changing a prompt/parameter (even `beam_size`), or updating weights goes through the same gate as code: eval floors (Chapter 10 Layer 4) plus golden tests, with the model version recorded on every job it processes (the registry — Chapter 15 — makes this queryable). "It's just a model file" is how quality regressions ship unlogged.
- **Stage or shadow when the change is scary.** Before a swapped stage serves customers, run it in shadow — same inputs, outputs stored but not delivered, scores compared (Chapter 19 formalizes this). Our per-stage artifact design makes shadow runs nearly free to implement; use them instead of courage.
- **Release cadence is a habit, not an event.** Small releases, at least weekly, even pre-customers. Teams that release rarely get bad at releasing exactly when it starts mattering.

## 13.3 Monitoring standards

The minimum dashboard that answers "is the system healthy?" at a glance:

- **Jobs:** submitted / completed / failed per day, failure rate *by stage*, p50/p95 job duration, queue depth and oldest-job age (the early-warning metric — a growing oldest-age means workers are dying or drowning).
- **Quality canaries:** rolling rate of post-condition violations (§13.1.2) and, once Chapter 16 lands, rolling automatic quality score — a slow quality drift is an incident nobody pages for, which is why it gets a chart.
- **Cost:** CPDM weekly (Chapter 11) — cost regressions are reliability regressions of the business.
- **Alerts follow the pager rule:** alert only on conditions someone will act on *now* (no worker heartbeat, failure-rate spike, oldest-job age breach, disk/queue saturation). Everything else is a chart reviewed weekly. At two engineers, a noisy pager is self-DDoS; alert fatigue kills more reliability than missing metrics do.

## 13.4 Incidents and failure analysis

The founding brief asked "how failures are analyzed." The loop:

1. **During:** one person owns the incident (at current size, whoever noticed — announce it); mitigate first (usually: pause the queue, revert the release, re-run affected jobs), diagnose second. Customer-affecting incidents get a proactive message before customers notice — in the wedge market, "we caught a quality issue and are re-running your jobs free" *builds* trust rather than spending it.
2. **After (within 48h):** a blameless postmortem, one page, in `docs/postmortems/`: timeline, root cause, customer impact, and three mandatory questions — *Which test layer should have caught this?* (buys a test, Chapter 10 §10.5), *Which alert should have fired?* (buys an alert or explicitly declines one), *Which handbook chapter was wrong or silent?* (buys an edit — this is how the handbook stays true, per the index's living-document rule).
3. **Blameless means causes, not exemption from ownership.** The postmortem names systems and gaps, never villains; the follow-up items get owners and land in the 20% debt/interrupt capacity (Chapter 3 §3.5) rather than a someday-list.

## 13.5 On-call, sized honestly

Pre-customers: no pager; the morning triage of nightly runs (Chapter 10 §10.4) is the whole practice. First customers: business-hours responsiveness, founders carry it. Contracted SLAs: that is a *sales decision that buys infrastructure* — an SLA promise prices in the on-call rotation, the staging environment parity, and the redundancy it requires (Chapter 23 makes this pricing explicit). Never sign reliability the roster can't deliver.

## Key takeaways

- Batch reliability = job-completion reliability: no lost jobs, no silent wrongness (production post-conditions), honest progress, then API uptime — in that order.
- Releases: small, weekly, reversible, expand-then-contract migrations; model changes are releases with eval gates and recorded versions; shadow runs replace courage.
- Monitor jobs, quality canaries, and CPDM; page only on actionable conditions — alert fatigue is the real enemy at this size.
- Every incident buys a test, an alert (or its documented refusal), and a handbook edit; blameless names causes, not villains.
- SLAs are priced promises — sign nothing the current roster can't answer at 2 a.m.

## Questions founders should ask

1. Can a job be lost in limbo today, and would we know? (Until Chapter 8 Stage 2: yes, and no.)
2. What percentage of last month's completed jobs would have failed the production post-conditions, had they existed?
3. When did we last practice a revert — not discuss one, practice one?
4. Which postmortem follow-up items are past due, and did the 20% capacity actually absorb them?

## Future research topics

- Define the v1 post-condition set from the golden-test assertions (duration tolerance, non-silence, transcript sanity) and wire them into the current pipeline even pre-migration — cheap and immediately valuable.
- Pick the minimal observability stack (managed Grafana/Prometheus vs. a hosted product) with a CPDM-conscious eye; a one-page decision record.
- Draft the customer-facing incident-communication template now, in Marathi and English — writing it calmly precedes needing it urgently.
