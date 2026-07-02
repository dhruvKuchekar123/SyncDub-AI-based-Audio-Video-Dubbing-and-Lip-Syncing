# Test Fixtures

Rights-cleared clips for the golden pipeline tests (Layer 3) and eval seeds.
See [docs/founder-os/10-testing-quality.md](../../../docs/founder-os/10-testing-quality.md) §10.3.

## Rules

- **Rights-cleared only.** Record these ourselves; never drop customer or
  downloaded content here. Every file needs a line in the table below naming
  who recorded it and their consent.
- **Small.** 10–20 seconds each, ≤ 720p. These run in CI and live in git history forever.
- **Immutable once referenced.** Changing a fixture silently redefines every
  downstream score — replacing one is a schema-level review event (Ch. 10 §10.3).

## Wanted (the v1 set — recording these is an afternoon of founder work)

| File | Contents | Recorded by / consent | Status |
|---|---|---|---|
| `male_clean.mp4` | One male speaker, clear Hindi, quiet room, 15s | — | ☐ to record |
| `female_clean.mp4` | One female speaker, clear Hindi, quiet room, 15s | — | ☐ to record |
| `noisy.mp4` | Hindi speech with background noise (fan/street), 15s | — | ☐ to record |
| `code_switched.mp4` | Hindi with heavy English mixing ("आज हम discuss करेंगे…"), 15s | — | ☐ to record |
