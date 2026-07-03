from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
import hashlib
import subprocess
import os
import sys
from datetime import datetime, timezone

from fastapi.middleware.cors import CORSMiddleware

import config
import jobs
from stages.languages import UnsupportedLanguageError, registry_summary, validate_pair

app = FastAPI()

# CORS * is known debt #4 — demo-only until any internet-reachable deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config.ensure_dirs()

# serve output videos
app.mount("/outputs", StaticFiles(directory=str(config.OUTPUT_DIR)), name="outputs")


PIPELINE_SCRIPT = os.path.join(os.path.dirname(__file__), "pipeline.py")


@app.get("/languages")
def get_languages():
    return {"languages": registry_summary()}


@app.post("/jobs")
async def create_job(
    file: UploadFile = File(...),
    source_lang: str = Form("hi"),
    target_lang: str = Form("mr"),
    enable_cloning: bool = Form(False),
    uploader_attestation: bool = Form(False),
    speaker_cloning_consent: bool = Form(False),
):
    try:
        _, tgt = validate_pair(source_lang, target_lang)
    except UnsupportedLanguageError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Consent gates before any processing (Ch. 5 §5.2): no attestation, no job;
    # no per-speaker consent, no cloning. The default path is stock voices.
    if not uploader_attestation:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "uploader_attestation is required",
                "attestation_text": jobs.UPLOADER_ATTESTATION_TEXT,
            },
        )
    if enable_cloning and not speaker_cloning_consent:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "voice cloning requires speaker_cloning_consent",
                "consent_text": jobs.SPEAKER_CONSENT_TEXT,
            },
        )

    busy = jobs.lock_holder()
    if busy is not None:
        raise HTTPException(
            status_code=409,
            detail=f"A job is already running ({busy}). Try again when it finishes.",
        )

    job_id = jobs.new_job_id()
    paths = jobs.job_paths(job_id)
    jobs.ensure_job_dirs(paths)

    # basename() strips any client-supplied directory components (path
    # traversal); the job-id prefix removes cross-job filename collisions.
    safe_name = os.path.basename(file.filename or "upload.mp4")
    input_path = os.path.join(str(config.UPLOAD_DIR), f"{job_id}_{safe_name}")

    sha256 = hashlib.sha256()
    with open(input_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            sha256.update(chunk)
            buffer.write(chunk)

    granted, deny_reason = jobs.cloning_allowed(
        requested=enable_cloning,
        speaker_consent=speaker_cloning_consent,
        clone_env_configured=bool(config.CLONE_PYTHON),
        xtts_code=tgt.xtts_code,
    )

    consent_record = {
        "job_id": job_id,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "uploader_attestation": True,
        "uploader_attestation_text": jobs.UPLOADER_ATTESTATION_TEXT,
        "voice_cloning_requested": enable_cloning,
        "speaker_cloning_consent": speaker_cloning_consent,
        "speaker_consent_text": jobs.SPEAKER_CONSENT_TEXT if speaker_cloning_consent else None,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "input_filename": safe_name,
        "input_sha256": sha256.hexdigest(),
    }
    jobs.write_consent_record(paths, consent_record)

    progress = jobs.ProgressWriter(
        paths.progress_path, job_id,
        fields={
            "source_lang": source_lang,
            "target_lang": target_lang,
            "cloning_requested": enable_cloning,
            "cloning_granted": granted,
            "fallback_reason": deny_reason,
        },
    )
    progress.update(0, "Initializing...")

    command = [
        sys.executable,
        PIPELINE_SCRIPT,
        "--video", os.path.abspath(input_path),
        "--job-id", job_id,
        "--source-lang", source_lang,
        "--target-lang", target_lang,
    ]
    if granted:
        command.append("--clone")
    with open(paths.log_path, "a") as log_file:
        subprocess.Popen(command, stdout=log_file, stderr=log_file)

    return {
        "job_id": job_id,
        "message": "Video processing started",
        "cloning": {"requested": enable_cloning, "granted": granted, "reason": deny_reason},
    }


@app.get("/progress/{job_id}")
def get_progress(job_id: str):
    data = jobs.read_progress(jobs.job_paths(job_id).progress_path)
    if data is None:
        raise HTTPException(status_code=404, detail="Unknown job")
    return data


@app.get("/video/{job_id}")
def get_video(job_id: str):
    paths = jobs.job_paths(job_id)
    data = jobs.read_progress(paths.progress_path)
    if data is None:
        raise HTTPException(status_code=404, detail="Unknown job")
    if data.get("state") != "done" or not os.path.exists(paths.output_path):
        raise HTTPException(status_code=404, detail="Job not finished")
    return {"video_url": f"/outputs/{job_id}.mp4"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
