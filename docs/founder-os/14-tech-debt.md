# Chapter 14: Technical Debt & Refactoring Protocol

> **Part II — Engineering OS** · [← Chapter 13](13-reliability-releases.md) · [Handbook index](README.md) · [Chapter 15 →](15-model-layer.md)

Our house style ships ugly bridges on purpose (Chapter 3), which means we generate debt on purpose — so we need a sharper repayment discipline than teams that pretend not to borrow. The core idea of this chapter: **debt is repaid on triggers, not on calendars.** "Refactoring sprints" scheduled by guilt repay the wrong debts at the wrong time; trigger-based repayment repays exactly the debt that is about to hurt.

## 14.1 What counts as debt (and what doesn't)

Debt is a *known* gap between how the system is and how it needs to be, **with an owner-visible record**. The `clone_bridge.py` subprocess hop is debt done right: contained, documented, working. The hardcoded `D:/Miniconda3` ffmpeg path is debt done wrong: undocumented, wide (it breaks every non-founder machine), discovered rather than declared.

Not debt: code that is merely old, style you'd write differently today, or a library that has a trendier alternative. Rewriting working, contained, measured code is not repayment — it is *taking out a new loan to redecorate*, and the measured-evolution principle (Chapter 7 §7.4) blocks it.

## 14.2 The debt register

One file: `docs/debt.md`. Each entry, three lines: what the shortcut is, what it will break or block, and its **trigger** — the observable condition that makes repayment mandatory. Entries are added in the same PR that ships the shortcut ("ship the ugly bridge *with a debt entry*" — Chapter 3). No tickets rotting in a tracker; the register is short precisely because it is curated: if an entry has no plausible trigger, it isn't debt, delete it.

Seed entries, from the current codebase:

| Debt | Trigger that forces repayment |
|---|---|
| Direct model imports, no stage interfaces (`inference_marathi.py`) | First model swap attempt — which licensing has already scheduled (Ch. 15) |
| Global `progress.json`, no job identity | Second concurrent user — i.e., first real customer trial |
| `Popen` fire-and-forget, no queue | First lost-job incident, or first customer, whichever first |
| No auth, CORS `*`, filename-as-path | Any non-demo deployment reachable from the internet |
| Unpinned dependencies, two undocumented conda envs | First non-founder engineer's first day (Ch. 6 hire #1) |
| Frontend's 714-line `App.js` single component | First real frontend feature beyond the demo flow (the editor, Ch. 21) |
| No LICENSE file | First external code reader — investor diligence or open-source decision (Ch. 26) |

Note what the table reveals: most of our debt triggers fire on the same three events — *first customer, first hire, first model swap*. That is the honest definition of our current stage, and it is why Chapter 8's migration and Chapter 15's swaps are the roadmap rather than items on it.

## 14.3 Repayment rules

- **Trigger fires → repayment enters the current quarter**, funded from the 20% reserve (Chapter 3 §3.5). A fired trigger that gets re-snoozed must be re-snoozed *in writing* in the register, with the new trigger — silent snoozing is how registers become fiction.
- **Repay at the touch.** When feature work enters a debted area, the PR either repays the debt or consciously extends it (one line in the register). What it may not do is silently build a second storey on the known-bad foundation — that converts debt into architecture.
- **Repayment ships with the same gates as features:** tests for the new shape (Chapter 10), before/after measurement where performance is claimed (Chapter 7 §7.4), and a register deletion in the same PR. A refactor that can't say what it fixed isn't done.
- **Containment work counts as repayment.** Sometimes the right move isn't removing the ugliness but driving it deeper (Chapter 7 §7.3) — wrapping the bridge in an adapter, isolating the global into one module. Cheaper, and often all the trigger actually demands.

## 14.4 The debt conversation with product pressure

The recurring failure mode in every company: debt repayment loses the argument against features, quarter after quarter, until an incident wins the argument catastrophically. Our structural defenses: the trigger system makes repayment *non-discretionary* (it's not competing in the prioritization meeting — the trigger already decided), the 20% reserve means it has a budget without renegotiation, and the register's "what it will break" line converts engineer unease into founder-legible risk. The founder's half of the bargain: never spend the 20% reserve on features in a good month. Reserves spent in good months don't exist in bad ones.

## 14.5 The rewrite question

Someday someone will propose rewriting the pipeline/backend/frontend wholesale. The standard: rewrites are approved only when (a) the debt register shows a *cluster* of fired triggers in one area that incremental repayment demonstrably can't clear, (b) the rewrite has a staged, each-stage-ships-alone plan (the Chapter 8 shape — which is itself the approved rewrite of the backend, done right), and (c) a decision record names what is *kept* (Chapter 8 §8.4's discipline). Big-bang rewrites with a cutover day are rejected categorically; they are how working companies produce non-working software.

## Key takeaways

- We borrow deliberately, so we repay deliberately: every shortcut ships with a register entry and an observable trigger; calendars and guilt schedule nothing.
- The current register's triggers cluster on first customer, first hire, and first model swap — which is why Chapters 8 and 15 are the roadmap.
- Repay at the touch, fund from the protected 20% reserve, delete the entry in the repaying PR, and let containment count.
- Old-but-working code isn't debt; rewrites need fired-trigger clusters and staged plans, never cutover days.

## Questions founders should ask

1. Does `docs/debt.md` exist and match reality, or is this chapter still describing an intention?
2. Which triggers have already fired without repayment starting — and was the snooze written down?
3. Was the 20% reserve spent on features in any recent month? Who noticed?
4. Is any current PR quietly building on a register entry without extending or repaying it?

## Future research topics

- Create `docs/debt.md` from the §14.2 seed table — a fifteen-minute task that makes the whole protocol real.
- Add a PR-template checkbox ("touches a debted area? register updated?") once CI exists (Chapter 9).
- Revisit the register quarterly against the incident log (Chapter 13): incidents in un-registered areas mean our debt radar has a blind spot worth studying.
