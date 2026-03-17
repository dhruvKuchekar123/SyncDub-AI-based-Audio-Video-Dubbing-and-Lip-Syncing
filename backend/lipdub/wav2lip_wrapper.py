import subprocess
from pathlib import Path
import os
import sys
import shutil

# Python executable of current environment
PYTHON_EXE = Path(sys.executable)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WAV2LIP_REPO_PATH = PROJECT_ROOT / "Wav2Lip_repo"
CHECKPOINT_DIR = WAV2LIP_REPO_PATH / "checkpoints"
CHECKPOINT_PATH = CHECKPOINT_DIR / "wav2lip_gan.pth"

TEMP_DIR = PROJECT_ROOT / "temp"
OUTPUT_DIR = PROJECT_ROOT / "outputs"


# ----------------------------------------------------
# Ensure required folders exist
# ----------------------------------------------------
def ensure_folders():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------
# Ensure Wav2Lip repo exists
# ----------------------------------------------------
def ensure_wav2lip_repo():

    if (WAV2LIP_REPO_PATH / "inference.py").exists():
        print("Wav2Lip repo already exists")
        return

    print("Cloning Wav2Lip repository...")

    subprocess.check_call([
        "git",
        "clone",
        "https://github.com/Rudrabha/Wav2Lip.git",
        str(WAV2LIP_REPO_PATH)
    ])


# ----------------------------------------------------
# Ensure checkpoint exists
# ----------------------------------------------------
def ensure_checkpoint():

    if CHECKPOINT_PATH.exists():
        print("Checkpoint already exists")
        return

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    url = "https://github.com/justinjohn0306/Wav2Lip/releases/download/models/wav2lip.pth"

    print("Downloading Wav2Lip checkpoint (~436MB)...")

    import requests

    response = requests.get(url, stream=True)

    if response.status_code != 200:
        raise RuntimeError("Checkpoint download failed")

    with open(CHECKPOINT_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print("Checkpoint downloaded:", CHECKPOINT_PATH)


# ----------------------------------------------------
# Run Wav2Lip
# ----------------------------------------------------
def run_wav2lip(face_video, audio_wav, outfile):

    ensure_folders()

    face_video = str(Path(face_video).resolve())
    audio_wav = str(Path(audio_wav).resolve())
    outfile = str(Path(outfile).resolve())

    print("\n--- Wav2Lip INPUT DEBUG ---")
    print("Face video:", face_video)
    print("Audio file:", audio_wav)
    print("Output file:", outfile)
    print("---------------------------\n")

    ensure_wav2lip_repo()
    ensure_checkpoint()

    inference_script = WAV2LIP_REPO_PATH / "inference.py"

    results_dir = WAV2LIP_REPO_PATH / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(PYTHON_EXE),
        str(inference_script),
        "--checkpoint_path",
        str(CHECKPOINT_PATH),
        "--face",
        face_video,
        "--audio",
        audio_wav,
        "--wav2lip_batch_size", "16",
        "--face_det_batch_size", "4",
        "--resize_factor", "2"
    ]

    print("Running Wav2Lip inference...")

    # Important: run inside Wav2Lip repo
    subprocess.check_call(cmd, cwd=str(WAV2LIP_REPO_PATH))

    # ------------------------------------------------
    # Find generated video automatically
    # ------------------------------------------------

    print("Searching for generated video...")

    video_files = list(results_dir.glob("*.mp4"))

    if len(video_files) == 0:
        raise RuntimeError("Wav2Lip finished but output video not found")

    generated_video = video_files[0]

    print("Generated video found:", generated_video)

    # ------------------------------------------------
    # Move to outputs folder
    # ------------------------------------------------

    Path(outfile).parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(generated_video), outfile)

    print("Wav2Lip done. Output saved to:", outfile)

    return outfile