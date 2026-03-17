from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import shutil
import subprocess
import os
import json

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# serve output videos
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


# ------------------- UPLOAD VIDEO -------------------
@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # save uploaded video
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    with open("progress.json", "w") as f:
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

    with open("pipeline.log", "a") as log_file:
        subprocess.Popen(command, stdout=log_file, stderr=log_file)

    return {"message": "Video processing started"}


# ------------------- CHECK PROGRESS -------------------
@app.get("/progress")
def get_progress():

    with open("progress.json") as f:
        data = json.load(f)

    return data


# ------------------- GET FINAL VIDEO -------------------
@app.get("/video")
def get_video():

    return {
        "video_url": "/outputs/final_dubbed.mp4"
    }