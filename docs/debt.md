# Technical Debt Register

Rules: every deliberate shortcut ships with an entry here (same PR). Each entry: what the shortcut is, what it will break or block, and the observable **trigger** that makes repayment mandatory. Trigger fires → repayment enters the current quarter, funded from the 20% reserve. Re-snoozing a fired trigger happens in writing, in this file. Full protocol: [docs/founder-os/14-tech-debt.md](founder-os/14-tech-debt.md).

| # | Debt | What it breaks / blocks | Trigger for repayment | Status |
|---|---|---|---|---|
| 1 | Direct model imports, no stage interfaces (`backend/inference_marathi.py` calls Whisper/GoogleTranslator/XTTS by name) | Every model swap touches pipeline code; sovereignty swaps (Ch. 15) blocked | First model swap attempt — already scheduled by licensing (translation first) | Open |
| 2 | Global `progress.json`, no job identity | Two concurrent users corrupt each other's progress; no audit trail | Second concurrent user — i.e. first real customer trial | Open |
| 3 | `subprocess.Popen` fire-and-forget in `/upload-video/`, no queue | Lost jobs are undetectable; no retries; no failure states | First lost-job incident or first customer, whichever first | Open |
| 4 | No auth, CORS `*` | Anyone reaching the server can submit jobs and fetch outputs | Any non-demo deployment reachable from the internet | Open |
| 5 | Output always overwrites `outputs/final_dubbed.mp4` | Every job destroys the previous job's result | Same as #2 (first concurrent use) | Open |
| 6 | Unpinned dependencies; XTTS lives in a second, undocumented conda env | Fresh clones behave differently; onboarding is folklore | First non-founder engineer's first day (hire #1) | **Repaid** — `requirements.txt`/`requirements-dev.txt` pinned, clone env pinned in `requirements-clone.txt` with setup instructions. Pins are a compatible baseline, not a founder-machine freeze; first full run on the pinned set confirms or adjusts them |
| 7 | Frontend is one 714-line `App.js` component | No architecture to carry the editor (Ch. 21) | First real frontend feature beyond the demo flow | Open |
| 8 | Hardcoded Windows ffmpeg path + import-time `os.environ` writes | Pipeline runs on exactly one machine | First non-founder run of the pipeline | **Repaid** (Stage 0: `backend/config.py`) |
| 9 | No LICENSE file | Legal posture undefined for any external reader | First external code reader | **Repaid** (proprietary `LICENSE`, interim per Ch. 26) |
| 10 | Uploaded filename used directly as disk path (`server.py`) | Path traversal + collision risk | Any non-demo deployment | Partially repaid — filename sanitized (Stage 0); job-ID paths arrive with #2 |
| 11 | Root-level scratch scripts (`test.py`, `TP.py`, `test_tts.py`, `filelist.txt`, stray `python` file) | Noise; no real test suite exists where tests should be | First CI setup (Ch. 9/10) | Open — first real unit tests added in Stage 0; scratch cleanup pending |
