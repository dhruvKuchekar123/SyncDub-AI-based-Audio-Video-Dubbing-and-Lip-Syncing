"""Job identity, per-job paths, progress reporting, and the single-run lock.

Repays debt #2/#5 (global progress.json, overwritten final_dubbed.mp4) and the
failure-reporting half of #3. The queue itself stays debt: one pipeline run at
a time, enforced by a pid-checked lock file, and a second submission is
refused rather than queued (GPU + RAM cannot hold two runs anyway).
"""
import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

import config

LOCK_PATH = config.BASE_DIR / ".pipeline.lock"


def new_job_id() -> str:
    return uuid.uuid4().hex[:12]


@dataclass(frozen=True)
class JobPaths:
    """Every on-disk location a job may touch, derived only from its id.

    temp_dir holds intermediates including the voice reference sample — it is
    deleted when the job ends (Founder OS Ch. 5/12: reference audio is the
    most sensitive artifact we hold). job_dir holds the persisted audit
    artifacts (consent, metrics, log) and survives temp cleanup.
    """
    job_id: str
    temp_dir: Path
    output_path: Path
    progress_path: Path
    job_dir: Path

    @property
    def log_path(self) -> Path:
        return self.job_dir / "pipeline.log"

    @property
    def consent_path(self) -> Path:
        return self.job_dir / "consent.json"

    @property
    def metrics_path(self) -> Path:
        return self.job_dir / "metrics.json"


def job_paths(job_id: str) -> JobPaths:
    return JobPaths(
        job_id=job_id,
        temp_dir=config.TEMP_DIR / job_id,
        output_path=config.OUTPUT_DIR / f"{job_id}.mp4",
        progress_path=config.PROGRESS_DIR / f"{job_id}.json",
        job_dir=config.JOBS_DIR / job_id,
    )


def ensure_job_dirs(paths: JobPaths) -> None:
    config.ensure_dirs()
    paths.temp_dir.mkdir(parents=True, exist_ok=True)
    paths.job_dir.mkdir(parents=True, exist_ok=True)


class ProgressWriter:
    """Atomic per-job progress file; the only channel the frontend polls.

    States: running -> done | error. `fail()` replaces the silent-hang
    failure mode where a crashed pipeline left the bar frozen forever.
    """

    def __init__(self, progress_path: Path, job_id: str, fields: dict | None = None):
        self.path = Path(progress_path)
        self.job_id = job_id
        self.fields = dict(fields or {})
        self._progress = 0
        self._status = ""

    def _write(self, state: str, error: str | None = None) -> None:
        payload = {
            "job_id": self.job_id,
            "progress": self._progress,
            "status": self._status,
            "state": state,
            "error": error,
            **self.fields,
        }
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
            os.replace(tmp, self.path)
        except Exception as e:  # progress reporting must never kill the job
            print(f"[WARN] Failed to write progress: {e}", flush=True)

    def update(self, progress: int, status: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [PROGRESS] {progress}% - {status}", flush=True)
        self._progress = progress
        self._status = status
        self._write("running")

    def set_fields(self, **fields) -> None:
        """Merge job facts (synthesizer_used, fallback_reason, ...) and rewrite."""
        self.fields.update(fields)
        self._write("running")

    def fail(self, message: str) -> None:
        print(f"[ERROR] Job {self.job_id} failed: {message}", flush=True)
        self._status = "Failed"
        self._write("error", error=message)

    def done(self, **fields) -> None:
        self.fields.update(fields)
        self._progress = 100
        self._status = "Processing Complete"
        self._write("done")


def read_progress(progress_path: Path) -> dict | None:
    """None if the job is unknown; a placeholder dict during a mid-write race."""
    if not os.path.exists(progress_path):
        return None
    try:
        with open(progress_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {"progress": 0, "status": "Updating...", "state": "running"}


# ---------------- single-run lock ----------------

def _pid_alive(pid: int) -> bool:
    if os.name == "nt":
        # os.kill(pid, 0) on Windows TERMINATES the target process — never use
        # it as a liveness probe there.
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION, False, pid
        )
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def read_lock() -> dict | None:
    try:
        with open(LOCK_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return None


def lock_holder() -> str | None:
    """job_id of a live lock holder, or None if the lock is free/stale."""
    holder = read_lock()
    if holder and _pid_alive(int(holder.get("pid", -1))):
        return holder.get("job_id", "unknown")
    return None


def acquire_pipeline_lock(job_id: str) -> bool:
    """Take the single-run lock; steals a lock whose owner pid is dead."""
    payload = json.dumps({"pid": os.getpid(), "job_id": job_id})
    for _ in range(2):
        try:
            fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as f:
                f.write(payload)
            return True
        except FileExistsError:
            if lock_holder() is not None:
                return False
            # stale lock: owner died without cleanup — remove and retry once
            try:
                os.remove(LOCK_PATH)
            except FileNotFoundError:
                pass
    return False


def release_pipeline_lock(job_id: str) -> None:
    holder = read_lock()
    if holder and holder.get("job_id") == job_id:
        try:
            os.remove(LOCK_PATH)
        except FileNotFoundError:
            pass
