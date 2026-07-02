# The SyncDub Founder Operating System

**The internal handbook of SyncDub — how we think, engineer, research, build product, and win.**

This is the document every SyncDub employee reads before writing their first line of code. It is not documentation of what exists; it is the operating system that decides what gets built, how, and why. It is written for a team of one today and a company of five hundred later — the principles hold at both sizes, and each chapter says explicitly what applies now versus at scale.

Every chapter is grounded in the real SyncDub codebase and its real gaps, not in generic startup advice. When a chapter cites `backend/server.py` or the Wav2Lip license, go look — the handbook earns trust by never pretending the current system is more than it is.

## How to read this handbook

- **New engineer?** Read Part 0, then Part II, then Chapter 16 (Evaluation OS). Everything else as needed.
- **Making a product decision?** Chapter 3 (Decision Frameworks) is the gate; Part IV is the context.
- **Evaluating a new model or vendor?** Chapters 7, 15, and 16, in that order.
- **Founder, quarterly?** Re-read Chapters 2, 4, and 24, and answer every "Questions founders should ask" section honestly.

## Table of Contents

### Part 0 — Ground Truth
- [Chapter 1: The State of SyncDub Today](01-state-of-syncdub.md)

### Part I — Founder OS: How the Company Thinks
- [Chapter 2: Mission, Vision & the Category Thesis](02-mission-vision-category-thesis.md)
- [Chapter 3: Core Values & Decision Frameworks](03-values-decision-frameworks.md)
- [Chapter 4: The Moat Map](04-moat-map.md)
- [Chapter 5: The Responsible Synthetic Media Charter](05-responsible-synthetic-media.md)
- [Chapter 6: From One Founder to 500 Engineers](06-org-and-hiring.md)

### Part II — Engineering OS: How Engineers Think
- [Chapter 7: Architecture Principles](07-architecture-principles.md)
- [Chapter 8: From Demo to Service](08-demo-to-service.md)
- [Chapter 9: Code, Repository & API Standards](09-code-repo-api-standards.md)
- [Chapter 10: Testing & Quality Engineering](10-testing-quality.md)
- [Chapter 11: Infrastructure, GPU & Cost Standards](11-infra-gpu-cost.md)
- [Chapter 12: Security & Compliance Standards](12-security-compliance.md)
- [Chapter 13: Reliability, Releases & Failure Analysis](13-reliability-releases.md)
- [Chapter 14: Technical Debt & Refactoring Protocol](14-tech-debt.md)

### Part III — AI Research OS: How AI Systems Think
- [Chapter 15: The Model Layer](15-model-layer.md)
- [Chapter 16: The Evaluation OS](16-evaluation-os.md)
- [Chapter 17: The Isochrony Problem](17-isochrony.md)
- [Chapter 18: Multi-Speaker & Emotion](18-multispeaker-emotion.md)
- [Chapter 19: Experimentation & A/B Framework](19-experimentation.md)
- [Chapter 20: Data Strategy & the Correction Flywheel](20-data-strategy.md)

### Part IV — Product OS: How Product Decisions Are Made
- [Chapter 21: Product Philosophy & the Human-in-the-Loop Editor](21-product-philosophy-editor.md)
- [Chapter 22: API-First & Developer Experience](22-api-first-dx.md)
- [Chapter 23: Enterprise Readiness](23-enterprise-readiness.md)
- [Chapter 24: Pricing, Packaging & Unit Economics](24-pricing-unit-economics.md)

### Part V — Business OS: How the Company Wins
- [Chapter 25: Go-To-Market & Competitive Strategy](25-gtm-competitive-strategy.md)
- [Chapter 26: Open Source, Community & Investor Readiness](26-open-source-community-investors.md)

### Appendices
- [Appendix A: Review Checklists](appendix-a-checklists.md)
- [Appendix B: Claude Behavior Protocol](appendix-b-claude-protocol.md) (also installed as [`CLAUDE.md`](../../CLAUDE.md) at repo root)
- [Appendix C: Glossary](appendix-c-glossary.md)

---

*This handbook is a living document. Chapters change by pull request, like code. If reality and the handbook disagree, fix one of them — never let them quietly diverge.*
