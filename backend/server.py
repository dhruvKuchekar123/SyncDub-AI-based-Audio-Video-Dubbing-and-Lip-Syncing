from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import shutil
import subprocess
import os
import json

from fastapi.middleware.cors import CORSMiddleware

import config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = str(config.BASE_DIR)
UPLOAD_FOLDER = str(config.UPLOAD_DIR)
OUTPUT_FOLDER = str(config.OUTPUT_DIR)
PROGRESS_PATH = str(config.PROGRESS_PATH)
LOG_PATH = str(config.LOG_PATH)

config.ensure_dirs()

# serve output videos
app.mount("/outputs", StaticFiles(directory=OUTPUT_FOLDER), name="outputs")


# ------------------- UPLOAD VIDEO -------------------
@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):

    # basename() strips any client-supplied directory components (path traversal)
    safe_name = os.path.basename(file.filename or "upload.mp4")
    input_path = os.path.join(UPLOAD_FOLDER, safe_name)

    # save uploaded video
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    with open(PROGRESS_PATH, "w") as f:
        json.dump({"progress": 0, "status": "Initializing..."}, f)

    # run your AI pipeline
    import sys
    script_path = os.path.join(os.path.dirname(__file__), "inference_marathi.py")
    command = [
        sys.executable,
        script_path,
        "--video",
        os.path.abspath(input_path)
    ]

    with open(LOG_PATH, "a") as log_file:
        subprocess.Popen(command, stdout=log_file, stderr=log_file)

    return {"message": "Video processing started"}


@app.get("/progress")
def get_progress():
    if not os.path.exists(PROGRESS_PATH):
        return {"progress": 0, "status": "No task started"}
    try:
        with open(PROGRESS_PATH) as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, ValueError):
        # Handle cases where the file is currently being written to and is empty
        return {"progress": 0, "status": "Updating..."}


# ------------------- GET FINAL VIDEO -------------------
@app.get("/video")
def get_video():

    return {
        "video_url": "/outputs/final_dubbed.mp4"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)