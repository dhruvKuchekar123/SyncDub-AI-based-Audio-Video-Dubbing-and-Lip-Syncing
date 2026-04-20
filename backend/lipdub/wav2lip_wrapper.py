import subprocess
from pathlib import Path
import os
import sys
import shutil
import re
import time
import json

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
    (WAV2LIP_REPO_PATH / "temp").mkdir(parents=True, exist_ok=True)


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

    url = "https://github.com/justinjohn0306/Wav2Lip/releases/download/models/wav2lip_gan.pth"

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
def run_wav2lip(face_video, audio_wav, outfile, progress_callback=None):

    ensure_folders()

    face_video = str(Path(face_video).resolve())
    audio_wav = str(Path(audio_wav).resolve())
    outfile = str(Path(outfile).resolve())

    ensure_wav2lip_repo()
    ensure_checkpoint()

    inference_script = WAV2LIP_REPO_PATH / "inference.py"

    results_dir = WAV2LIP_REPO_PATH / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Clean old results
    for f in results_dir.glob("*.mp4"):
        try: os.remove(f)
        except: pass

    cmd = [
        str(PYTHON_EXE),
        str(inference_script),
        "--checkpoint_path",
        str(CHECKPOINT_PATH),
        "--face",
        face_video,
        "--audio",
        audio_wav,
        "--wav2lip_batch_size", "8", # Reduced batch size for CPU stability
        "--face_det_batch_size", "8", # Increased for speed
        "--resize_factor", "1", # DISABLE resizing factor to maintain original quality (CRITICAL FOR BLUR)
        "--pads", "0", "10", "0", "0", # Padding for better mouth movement detection
        "--nosmooth" # Disable smoothing for sharper face outlines
    ]

    print("[INFO] Starting Wav2Lip inference with real-time logging...")

    # We use Popen to capture tqdm progress from stderr
    process = subprocess.Popen(
        cmd, 
        cwd=str(WAV2LIP_REPO_PATH),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # tqdm often goes to stderr, but we merge
        universal_newlines=True,
        bufsize=1
    )

    # Regex for tqdm: " 10%|█         | 8/87 [00:21<03:33,  2.70s/it]"
    tqdm_pattern = re.compile(r"(\d+)/(\d+)\s+\[")
    
    last_output_lines = []

    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            line = line.strip()
            print(line, flush=True)
            last_output_lines.append(line)
            if len(last_output_lines) > 20:
                last_output_lines.pop(0)

            match = tqdm_pattern.search(line)
            if match and progress_callback:
                try:
                    current = int(match.group(1))
                    total = int(match.group(2))
                    # Map 0-total to 85-99%
                    percentage = 85 + int((current / total) * 14)
                    progress_callback(percentage, f"Merging audio and video: {current}/{total} frames")
                except:
                    pass

    rc = process.poll()
    if rc != 0:
        error_msg = "\n".join(last_output_lines)
        print(f"[ERROR] Wav2Lip Failed with exit code {rc}. Last output:\n{error_msg}")
        raise RuntimeError(f"Wav2Lip failed (Exit {rc}). Check logs for details.")

    # ------------------------------------------------
    # Find generated video automatically (Robust Check)
    # ------------------------------------------------
    print("Searching for generated video in results and temp folders...")
    
    # Check Wav2Lip results folder AND temp folder
    possible_paths = [
        results_dir / "result_voice.mp4",
        results_dir / "result.mp4",
        WAV2LIP_REPO_PATH / "temp/result.avi",
        PROJECT_ROOT / "temp/result.avi"
    ]
    # Also glob for any .mp4 in results_dir
    possible_paths.extend(list(results_dir.glob("*.mp4")))

    generated_video = None
    for p in possible_paths:
        if p.exists() and p.stat().st_size > 0:
            generated_video = p
            print(f"[SUCCESS] Found output at: {p}")
            break

    if not generated_video:
        # Fallback: check if the process didn't create a file but didn't error
        print(f"[ERROR] Process finished but no output file found in: {possible_paths}")
        raise RuntimeError("Wav2Lip finished but output video was not found or is empty.")

    # Move to final location
    Path(outfile).parent.mkdir(parents=True, exist_ok=True)
    if generated_video.suffix == '.avi':
        # Convert avi to mp4 if needed, or just move and hope for the best
        # Actually, moving and renaming is usually fine for most players
        shutil.copy2(str(generated_video), outfile)
    else:
        shutil.move(str(generated_video), outfile)

    print("Wav2Lip done. Output saved to:", outfile)
    return outfile