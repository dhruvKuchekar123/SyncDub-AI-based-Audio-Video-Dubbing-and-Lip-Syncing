# Chapter 6: From One Founder to 500 Engineers

> **Part I — Founder OS** · [← Chapter 5](05-responsible-synthetic-media.md) · [Handbook index](README.md) · [Chapter 7 →](07-architecture-principles.md)

The founding brief imagined a handbook for 500 engineers. The only org that matters right now is one founder deciding who hires #1 through #5 are. This chapter serves Monday morning first and the 500-engineer company second — with the scaling principles stated so the early decisions don't have to be unwound later.

## 6.1 The founder's actual job, by stage

- **Now (team of one):** the founder is the bottleneck on everything; the job is choosing which bottleneck to *be*. Per the moat map, the founder's irreplaceable work is customer discovery in the wedge market and the quality bar — everything else (pipeline hardening, UI) is delegable to the first hires. The trap at this stage is engineering comfort: rebuilding the backend feels like progress and postpones the phone calls that decide whether the company should exist.
- **1→5:** the founder still reviews everything; the handbook is enforced by proximity.
- **5→25:** the handbook replaces proximity. Decision records (Chapter 3 §3.4) and review checklists (Appendix A) stop being founder tools and become the management system.
- **25→500:** the founder's job is protecting the decision stack and the charter against scale's default drift (speed over quality, growth over trust). Everything else has an owner who isn't the founder.

## 6.2 The first five hires

Sequenced against the moats and the roadmap, not against org-chart convention:

1. **#1 — Pipeline/ML engineer.** Owns the licensing-forced model swaps (Chapter 15) and the evaluation OS (Chapter 16). The single highest-leverage hire: they unblock both legality and measurability. Profile: has shipped ML systems to production, allergic to unmeasured claims, comfortable in the ugly-bridge house style.
2. **#2 — Product/full-stack engineer.** Owns demo-to-service (Chapter 8) and then the editor (Chapter 21) with its correction-data capture. Profile: has built multi-tenant SaaS before; treats data schemas as product decisions.
3. **#3 — Founding editor/linguist (part-time is fine).** A working Marathi translator/dubbing professional. Not an engineer — the person who makes our quality metrics mean something and our golden sets honest. Cheap, rare thinking: every dubbing-tech company discovers too late that linguists should have been in the room from the start.
4. **#4 — Infra/SRE-minded engineer.** Owns GPU cost (Chapter 11), reliability (Chapter 13), security hardening (Chapter 12). Until this hire, #1 and #2 share the pager.
5. **#5 — Growth/customer engineer.** Sits with wedge customers (coaching institutes), owns onboarding and the feedback loop into the roadmap. Half sales-engineer, half support; the founder's successor on customer discovery so the founder can raise/expand.

Non-hires at this stage, stated to resist pressure: no designers-as-employees (contract it), no "Head of AI" (hire #1 *is* AI), no salespeople before the product can be sold without the founder in the room (Chapter 25), no managers of any kind.

## 6.3 Hiring philosophy

- **Hire for the eval, not the vibe.** Every candidate does a paid work-sample shaped like the real job: #1 candidates benchmark two ASR models on a Hindi test set and write up the trade-off; #2 candidates design the job-queue migration for `backend/server.py`. Their write-up is a decision record; judge it like one. Interviews measure interviewing; work samples measure work.
- **Values screen = the challenge test.** During the work sample, we assert something wrong. Candidates who push back with reasons pass the culture bar (Chapter 3's challenge duty); candidates who fold — however brilliant — fail it. At five people, one agreeable genius quietly breaks the decision stack.
- **Indic context is a real qualification.** A Marathi-speaking engineer hears our failure modes; treat language skill as the hiring signal it is, not a nice-to-have.
- **Pay honestly at the bottom of the market's top.** We won't outbid big tech; we offer real equity, real ownership of a chapter of this handbook, and a mission with a face (the student in Chapter 3's values). Candidates who need the highest number should take it elsewhere without hard feelings.
- **Fire fast on trust, slow on skill.** A charter violation or a faked result ends employment immediately. A skill gap gets a written expectation, real help, and one honest quarter.

## 6.4 How the org scales without becoming an org chart

Principles that hold from 5 to 500:

- **Owners, not committees.** Every system, metric, and chapter of this handbook has exactly one named owner. Shared ownership is unowned.
- **The handbook is the manager until managers exist.** First management layer arrives around 12–15 people, and managers are working engineers/editors first.
- **Teams form around moats, not technologies.** Future teams are "evaluation," "editor/flywheel," "trust," "cost" — not "frontend team" and "backend team." Technology-shaped teams optimize their layer; moat-shaped teams optimize the company.
- **Every engineer touches customer content monthly.** Watching a real dubbed lecture with real corrections is the antidote to building for the demo again.

## Key takeaways

- The founder's scarce work is customer discovery and the quality bar; the engineering itch is the trap.
- Five hires, in order: ML/eval engineer, product/SaaS engineer, founding linguist, infra/SRE, growth/customer engineer — sequenced by moat, with the linguist as the unconventional early call.
- Hire by paid work samples judged as decision records; screen values by testing the challenge duty; treat Marathi/Indic fluency as a technical qualification.
- Scale by named owners and moat-shaped teams; the handbook replaces proximity before managers replace the handbook.

## Questions founders should ask

1. This month, how many hours went to customer discovery versus code? Is that ratio a decision or a drift?
2. If hire #1 started Monday, is there a written work-sample brief and a golden-set seed for them — or would their first week be spent watching you work?
3. Who is the named owner of each shipped system today? (Every "me, I guess" is a pending hire or a pending handoff.)
4. Which handbook chapter would you trust the least in a new hire's hands, and what does that say about the chapter?

## Future research topics

- Draft the two work-sample briefs (#1 and #2) now — they're useful even before hiring, as scoping documents for the actual work.
- Compensation benchmarks for ML engineers in Indian startup market vs. equity expectations; decide the equity budget for hires #1–5 as one decision record, not five negotiations.
- Talk to founders of Indic-language ML companies (AI4Bharat orbit, Sarvam-adjacent) about where linguist-in-the-loop hiring worked or failed.
