"""Central configuration for the SyncDub backend.

Every machine-specific value is read from an environment variable here, with
a portable default. No other module may hardcode machine paths or write
os.environ at import time (Founder OS Ch. 9 §9.2). See .env.example at the
repo root for the full list of variables.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TEMP_DIR = BASE_DIR / "temp"          # per-job subdirs, deleted when the job ends
OUTPUT_DIR = BASE_DIR / "outputs"     # {job_id}.mp4
UPLOAD_DIR = BASE_DIR / "uploads"     # {job_id}_{original_name}
PROGRESS_DIR = BASE_DIR / "progress"  # {job_id}.json
JOBS_DIR = BASE_DIR / "jobs"          # {job_id}/ audit artifacts (consent, metrics, log)


def _env_bool(name: str, default: bool) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


# ffmpeg binary. Default assumes it is on PATH (apt/brew/conda install);
# override with SYNCDUB_FFMPEG for a non-PATH location.
FFMPEG = os.environ.get("SYNCDUB_FFMPEG", "ffmpeg")

# moviepy/imageio can only discover ffmpeg through this variable, so it is
# the one sanctioned import-time environment write in the codebase.
os.environ.setdefault("IMAGEIO_FFMPEG_EXE", FFMPEG)

# Python interpreter of the separate XTTS voice-cloning environment invoked
# via clone_bridge.py (its dependencies conflict with the main env). Unset
# means cloning is unavailable and the pipeline uses stock Edge-TTS voices.
CLONE_PYTHON = os.environ.get("SYNCDUB_CLONE_PYTHON")

# Voice cloning defaults to on only when a cloning environment is configured.
USE_VOICE_CLONING = _env_bool("SYNCDUB_VOICE_CLONING", default=bool(CLONE_PYTHON))


def ensure_dirs() -> None:
    for d in (TEMP_DIR, OUTPUT_DIR, UPLOAD_DIR, PROGRESS_DIR, JOBS_DIR):
        d.mkdir(parents=True, exist_ok=True)
