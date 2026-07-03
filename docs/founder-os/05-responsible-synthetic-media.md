# Chapter 5: The Responsible Synthetic Media Charter

> **Part I — Founder OS** · [← Chapter 4](04-moat-map.md) · [Handbook index](README.md) · [Chapter 6 →](06-org-and-hiring.md)

SyncDub clones voices and re-animates faces. That is deepfake-adjacent technology, and pretending otherwise is how companies in this category end up as cautionary headlines. This charter is the trust layer of the decision stack (Chapter 3): it is never traded away, and every employee is empowered to block a release that violates it. It is also — deliberately — a sales weapon: Chapter 4 established trust infrastructure as a moat, and Chapter 23 shows it winning procurement. Ethics and strategy point the same direction here; that alignment is why this charter will actually be followed.

## 5.1 The bright line

**SyncDub transforms consented content for its rightful owner. It does not put words in anyone's mouth.**

Everything we build re-expresses what a speaker *actually said*, in another language, with their consent. The moment a tool of ours can make a person appear to say something they never said, we have left our product category and entered another one — one we have chosen not to be in (Chapter 2, §2.4).

Concrete consequences of the bright line:

- No "type text, get the speaker saying it" feature, ever, regardless of revenue attached. The TTS stage is only ever fed by the translation of the speaker's own transcript. (Editor corrections to translations are bounded rephrasings of the source — audited, attributed, and logged, per §5.4.)
- No dubbing of content the uploader does not have rights to. "It's for education" is not a rights claim.
- No voice cloning without speaker-level consent (§5.2) — the uploader owning the *video* does not imply the speaker consented to *voice cloning*.

## 5.2 Consent, in layers

Consent is a chain, and layers 1–2 are now implemented: `POST /jobs` refuses uploads without an uploader rights attestation (HTTP 400), refuses cloning requests without speaker consent, and persists a timestamped consent record (verbatim attestation texts, language pair, input hash) in `jobs/{id}/consent.json`, which outlives the media (§12.3). The charter's three layers, phased in as the product matures (Chapter 8 sequences the implementation):

1. **Uploader attestation (v1, cheap, immediate — implemented):** at upload, the customer attests they hold the rights to the content and the authority to localize it. Recorded, timestamped; tying it to an *account* arrives with accounts themselves (Ch. 8 Stage 3). This is a legal instrument, not a UX hurdle — one checkbox with real words.
2. **Speaker consent for voice cloning (v1 for cloning path — implemented):** cloning is opt-in per job, with a recorded attestation that identified speakers consented to voice replication, enforced in both the server and the pipeline (`jobs.cloning_allowed`). Default path remains stock neural voices.
3. **Verified consent (enterprise):** for institutional deals, speaker consent collected verifiably — signed release or an in-product spoken-consent flow ("I authorize SyncDub to replicate my voice for localization of my content", in the speaker's own cloned-reference voice sample). This is the procurement-gate version.

## 5.3 Provenance and watermarking

Every SyncDub output must be *identifiable as synthetic* by machines, and *attributable* by us:

- **Audible/visible disclosure** where the customer's jurisdiction or platform requires it; controllable by the customer otherwise — but the metadata layer below is never customer-controllable.
- **Content credentials (C2PA)**: sign outputs with provenance metadata — produced by SyncDub, from which source asset, for which account — as soon as engineering capacity allows (this is a known, standardized integration, not research).
- **Forensic watermarking** (inaudible/invisible): the aspiration is real but the technology is an arms race; we adopt the best available standard rather than inventing one, and we never *claim* robustness we don't have.
- **Internal attribution ledger (v1, immediate):** even before C2PA, we keep hashes of every input and output tied to the producing account and job. When a video surfaces and someone asks "did SyncDub make this?", we must be able to answer. Today we cannot — outputs aren't even uniquely named (`final_dubbed.mp4`, Chapter 1 §1.2).

## 5.4 Auditability

Every job retains, for a defined period: who submitted it, the consent attestations, the input hash, the transcript, the translation (with any editor modifications attributed to the editing account), and the output hash. This audit trail is what turns the bright line from a promise into a checkable fact — and it doubles as the data layer the flywheel needs anyway (Chapter 20). Trust and moat, one schema.

## 5.5 Misuse policy and enforcement

- **Refusal categories:** impersonation of public figures without documented authority; political campaign material (categorically, in v1 — the review capacity to do it safely doesn't exist); content the uploader cannot claim rights to; sexual content involving real persons.
- **Detection posture:** we are realistic — a determined bad actor with a consented-looking upload can fool us. The policy is therefore built on attestation + attribution + takedown: fraud is the *uploader's* documented lie, we can prove what we made, and we can act fast when notified.
- **Takedown:** a public reporting channel; verified reports get the output's distribution support revoked, the account reviewed, and law enforcement cooperation where warranted. Response-time targets live in the support standards (Chapter 23).
- **Enforcement inward:** any employee can halt a feature or a deal on charter grounds by writing down the objection (Chapter 3's challenge duty). The objection is resolved by the founder in writing. A charter that can be waived verbally under quarterly pressure is not a charter.

## 5.6 Regulatory posture

We build *ahead* of Indian regulation, not behind it: India's DPDP Act (personal data — and a voice print is personal data), IT Rules on synthetic media disclosure as they evolve, and the EU AI Act's transparency obligations as the likely global template. The stance in one line: **compliance is a product feature we ship early, because our buyers' lawyers will eventually require it and our competitors will retrofit it in panic.** Chapter 12 carries the engineering specifics (retention, deletion, data residency).

## Key takeaways

- The bright line: consented transformation of real content, never fabrication. No text-to-speaker feature, ever.
- Consent is layered — uploader attestation now, speaker consent for cloning now, verified consent for enterprise — layers 1–2 are live in the upload flow; layer 3 remains.
- Every output must be attributable (hash ledger now, C2PA soon); every job auditable end-to-end.
- Misuse policy = attestation + attribution + fast takedown, enforced by anyone in the company, in writing.
- Trust is simultaneously an ethical floor and a competitive moat; that alignment is what makes it durable.

## Questions founders should ask

1. Could we, today, prove whether a given viral video was produced by our pipeline? (Today: no. When does that become yes?)
2. Which charter commitment would be most tempting to waive for our first large deal, and is the enforcement path (§5.5) strong enough to survive that day?
3. ~~Is the cloning path (`USE_VOICE_CLONING`) still on-by-default without consent capture? Why?~~ Resolved: cloning is opt-in per job behind recorded speaker consent (`jobs.cloning_allowed`); `SYNCDUB_VOICE_CLONING` now only gates *availability* of the clone environment, never activation.
4. Whose voice-consent gets violated *first* in our wedge market — the professor whose old lectures the institute uploads? What does our attestation actually say about that case?

## Future research topics

- C2PA integration effort estimate for our MoviePy/ffmpeg render stage.
- Survey audio watermarking robustness (re-encoding, platform transcoding) to calibrate what we can honestly claim.
- Track DPDP rules and IT-Rules amendments on synthetic media; assign an owner who reads the actual notifications, not the news coverage.
