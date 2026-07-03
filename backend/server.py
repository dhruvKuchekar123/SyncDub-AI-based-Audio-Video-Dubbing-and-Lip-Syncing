from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
import shutil
import subprocess
import os
import sys

from fastapi.middleware.cors import CORSMiddleware

import config
import jobs

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


PIPELINE_SCRIPT = os.path.join(os.path.dirname(__file__), "inference_marathi.py")


@app.post("/jobs")
async def create_job(file: UploadFile = File(...)):
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

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    progress = jobs.ProgressWriter(paths.progress_path, job_id)
    progress.update(0, "Initializing...")

    command = [
        sys.executable,
        PIPELINE_SCRIPT,
        "--video", os.path.abspath(input_path),
        "--job-id", job_id,
    ]
    with open(paths.log_path, "a") as log_file:
        subprocess.Popen(command, stdout=log_file, stderr=log_file)

    return {"job_id": job_id, "message": "Video processing started"}


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
