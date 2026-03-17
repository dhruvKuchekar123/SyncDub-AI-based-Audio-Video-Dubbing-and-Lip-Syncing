import argparse
import subprocess
import numpy as np
import os
import time
import textwrap
import json
import os

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.environ["IMAGEIO_FFMPEG_EXE"] = r"D:/Miniconda3/envs/lipdub_env/Library/bin/ffmpeg.exe"
os.environ["COQUI_TOS_AGREED"] = "1"

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

def update_progress(progress, status):
    print(f"[PROGRESS] {progress}% - {status}", flush=True)
    try:
        with open(os.path.join(BASE_DIR, "progress.json"), "w") as f:
            json.dump({"progress": progress, "status": status}, f)
    except Exception as e:
        print(f"[WARN] Failed to write progress: {e}", flush=True)

# ---------------- LOAD MODELS ----------------
whisper_model = None
mms_model = None
mms_tokenizer = None
translator = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        import whisper
        update_progress(25, "Loading Whisper model...")
        print("[INFO] Loading Whisper model (small)...", flush=True)
        whisper_model = whisper.load_model("small")
    return whisper_model

def get_translator():
    global translator
    if translator is None:
        from deep_translator import GoogleTranslator
        print("[INFO] Loading Translator...", flush=True)
        translator = GoogleTranslator(source='hi', target='mr')
    return translator



def unload_models():
    """Clear memory before heavy video processing"""
    print("[INFO] Unloading models to free memory...", flush=True)
    global whisper_model, translator
    whisper_model = None
    translator = None
    import gc
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except:
        pass

# ---------------- AUDIO EXTRACTION ----------------
def extract_audio(video_path):

    print("[INFO] Extracting audio...")
    from moviepy.editor import VideoFileClip
    audio_path = os.path.join(TEMP_DIR, "audio.wav")

    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, codec="pcm_s16le", logger=None)

    if not os.path.exists(audio_path):
        raise RuntimeError("Audio extraction failed")

    return audio_path


# ---------------- SPEECH RECOGNITION ----------------
def transcribe_audio(audio_path):

    model = get_whisper_model()
    update_progress(30, "Transcribing Hindi speech")
    print("[INFO] Running Whisper (Hindi)...", flush=True)
    # Enforce Hindi to avoid detection errors and improve accuracy
    # beam_size=5 is a good balance for CPU
    result = model.transcribe(audio_path, beam_size=5, language="hi", task="transcribe")

    segments = result.get("segments", [])

    print(f"[INFO] Segments detected: {len(segments)}", flush=True)

    return segments


# ---------------- TRANSLATION ----------------
def translate_text(text):

    if not text.strip():
        return ""

    # Clean text: remove multiple spaces and newlines
    import re
    text = re.sub(r'\s+', ' ', text).strip()

    try:
        t = get_translator()
        # Translate sentence by sentence or small blocks using deep-translator
        result = t.translate(text)
        if not result:
             print("[WARN] Translation result was empty", flush=True)
             return text # Fallback to original
        
        # Ensure it returns a string if deep-translator wrapped it in an object
        if hasattr(result, "text"):
            return result.text
        return str(result)
    except Exception as e:
        print(f"[WARN] Translation error: {e}", flush=True)
        return text # Fallback


# ---------------- PITCH MATCHING & GENDER ----------------
def get_median_pitch(audio_path):
    import librosa
    import numpy as np
    try:
        y, sr = librosa.load(audio_path, sr=16000)
        pitches, mags = librosa.piptrack(y=y, sr=sr)
        pitches = pitches[mags > np.percentile(mags, 80)]
        pitches = pitches[pitches > 60] 
        if len(pitches) == 0: return None
        return np.median(pitches)
    except Exception as e:
        print(f"[WARN] Pitch detection error: {e}")
        return None

def detect_gender(audio_path):
    pitch = get_median_pitch(audio_path)
    if not pitch: 
        print("[WARN] Pitch not found. Defaulting to male.")
        return "male"
    print(f"[DEBUG] Detected pitch: {pitch:.1f}Hz")
    return "female" if pitch > 180 else "male"

# ---------------- GENDER DETECTION ----------------
def detect_gender(audio_path):
    pitch = get_median_pitch(audio_path)
    if not pitch: return "male"
    return "female" if pitch > 180 else "male"


# ---------------- NATURAL TTS (EDGE TTS) ----------------
def synthesize_speech(text, gender="male"):

    if not text.strip():
        raise RuntimeError("Translation produced empty text")

    print(f"[INFO] Generating natural Marathi speech (Edge TTS) - Voice: {gender}...", flush=True)
    
    # Select Voice Model based on Gender
    voice = "mr-IN-AarohiNeural" if gender == "female" else "mr-IN-ManoharNeural"
    
    audio_path = os.path.join(TEMP_DIR, "marathi.wav")
    
    import edge_tts
    import asyncio
    
    # Generate TTS
    communicate = edge_tts.Communicate(text, voice)
    
    # We use a blocking async run to generate the file inline
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(communicate.save(audio_path))

    print("[DEBUG] TTS audio size:", os.path.getsize(audio_path))

    if os.path.getsize(audio_path) == 0:
        raise RuntimeError("TTS produced empty audio")

    return audio_path


# ---------------- AUDIO NORMALIZATION ----------------
def normalize_audio(audio_path):

    if not os.path.exists(audio_path):
        raise RuntimeError("TTS audio file not found")

    if os.path.getsize(audio_path) == 0:
        raise RuntimeError("TTS audio file is empty")

    out_path = os.path.join(TEMP_DIR, "marathi_16k.wav")

    ffmpeg_exe = os.environ.get("IMAGEIO_FFMPEG_EXE", "ffmpeg")
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", audio_path,
        "-ac", "1",
        "-ar", "16000",
        out_path
    ]

    result = subprocess.run(cmd, capture_output=True)

    if result.returncode != 0:
        print(result.stderr.decode())
        raise RuntimeError("FFmpeg conversion failed")

    if not os.path.exists(out_path):
        raise RuntimeError("Normalized audio not created")

    print("[DEBUG] Normalized audio size:", os.path.getsize(out_path))

    return out_path


# ---------------- MAIN PIPELINE ----------------
def process_video(video_path):

    if not os.path.isabs(video_path):
        video_path = os.path.join(UPLOAD_DIR, video_path)

    video_path = os.path.abspath(video_path)

    if not os.path.exists(video_path):
        raise FileNotFoundError(video_path)

    print("[START] Processing:", video_path)
    update_progress(10, "Extracting audio track")

    # Extract audio
    audio_path = extract_audio(video_path)

    # Speech recognition
    update_progress(25, "Transcribing Hindi speech")
    segments = transcribe_audio(audio_path)

    print("[INFO] Translating segments...")
    update_progress(50, "Translating to Marathi")

    print("[INFO] Translating segments sentence by sentence for better context...")
    translated_segments = []
    
    for seg in segments:
        hi_text = seg["text"].strip()
        if hi_text:
            mr_text = translate_text(hi_text)
            try:
                print(f"[DEBUG] Translated segment: {mr_text[:50]}...", flush=True)
            except:
                pass
            translated_segments.append(mr_text)
            
    final_text = " ".join(translated_segments)

    if not final_text.strip():
        raise RuntimeError("Translation returned empty text")

    # Detect speaker gender
    update_progress(65, "Detecting speaker gender")
    speaker_gender = detect_gender(audio_path)
    print(f"[INFO] Speaker identified as: {speaker_gender}", flush=True)

    # Generate speech with Edge-TTS
    update_progress(70, "Synthesizing dubbed audio (Natural)")
    tts_audio = synthesize_speech(final_text, gender=speaker_gender)

    print(f"[DEBUG] TTS path: {tts_audio}", flush=True)

    # Normalize audio
    tts_audio = normalize_audio(tts_audio)

    print("[INFO] Audio ready:", tts_audio, flush=True)

    # FREE MEMORY BEFORE WAV2LIP
    unload_models()

    # Output video
    output_video = os.path.join(
        OUTPUT_DIR,
        f"dubbed_{int(time.time())}.mp4"
    )

    print("[INFO] Running Wav2Lip...", flush=True)
    update_progress(85, "Merging audio and video")
    print(f"[DEBUG] VIDEO: {video_path}", flush=True)
    print(f"[DEBUG] AUDIO: {tts_audio}", flush=True)
    print(f"[DEBUG] OUTPUT: {output_video}", flush=True)

    from lipdub.wav2lip_wrapper import run_wav2lip
    run_wav2lip(video_path, tts_audio, output_video)

    if not os.path.exists(output_video):
        raise RuntimeError("Wav2Lip finished but output video not found")

    # Rename to final_dubbed.mp4 so the frontend can find it
    final_dest = os.path.join(OUTPUT_DIR, "final_dubbed.mp4")
    os.replace(output_video, final_dest)
    output_video = final_dest

    update_progress(100, "Processing Complete")
    print("\nSUCCESS ->", output_video)

# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--video",
        type=str,
        required=True,
        help="Video filename inside uploads folder OR full path"
    )

    args = parser.parse_args()

    process_video(args.video)