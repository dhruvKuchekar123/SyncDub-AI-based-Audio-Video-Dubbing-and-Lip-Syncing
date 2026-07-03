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

# ---------------- CONFIGURATION ----------------
# All machine-specific values (ffmpeg location, cloning env, feature flags)
# live in config.py and are driven by environment variables.
import config
import jobs
from config import USE_VOICE_CLONING
from stages.languages import get_language, validate_pair

BASE_DIR = str(config.BASE_DIR)
TEMP_DIR = str(config.TEMP_DIR)
OUTPUT_DIR = str(config.OUTPUT_DIR)
UPLOAD_DIR = str(config.UPLOAD_DIR)

config.ensure_dirs()

# Set in __main__; stays None when the module is imported (tests, tooling),
# in which case progress updates only print.
PROGRESS: "jobs.ProgressWriter | None" = None


def update_progress(progress, status):
    if PROGRESS is not None:
        PROGRESS.update(progress, status)
    else:
        print(f"[PROGRESS] {progress}% - {status}", flush=True)

# ---------------- LOAD MODELS ----------------
whisper_model = None
mms_model = None
mms_tokenizer = None
translator = None

def get_xtts_model():
    """XTTS v2 is handled via the bridge script in voiceclone_env"""
    pass

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        import whisper
        # Check for corrupted download (~1.5GB expected for medium)
        cache_path = os.path.expanduser("~/.cache/whisper/medium.pt")
        if os.path.exists(cache_path) and os.path.getsize(cache_path) < 1000000:
            print(f"[WARN] Corrupted Whisper model detected ({os.path.getsize(cache_path)} bytes). Deleting...", flush=True)
            os.remove(cache_path)
            
        update_progress(25, "LOADING Whisper Medium (1.5GB) - PLEASE WAIT...")
        print("[INFO] Loading Whisper model (medium)...", flush=True)
        whisper_model = whisper.load_model("medium")
    return whisper_model

def get_translator(source_code, target_code):
    global translator
    key = (source_code, target_code)
    if translator is None or translator[0] != key:
        from deep_translator import GoogleTranslator
        print(f"[INFO] Loading Translator ({source_code} -> {target_code})...", flush=True)
        translator = (key, GoogleTranslator(source=source_code, target=target_code))
    return translator[1]



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
def transcribe_audio(audio_path, whisper_code):
    model = get_whisper_model()

    # beam_size=2 is a good balance of speed and accuracy;
    # beam_size=5 is much slower for minimal gain.
    result = model.transcribe(audio_path, beam_size=2, language=whisper_code, task="transcribe")

    detected = result.get("language")
    if detected and detected != whisper_code:
        # Warn only — the user picked the source language; no auto-override.
        print(f"[WARN] Whisper detected language '{detected}' but the job selected "
              f"'{whisper_code}'. Transcription used '{whisper_code}'.", flush=True)

    segments = result.get("segments", [])

    print(f"[INFO] Segments detected: {len(segments)}", flush=True)

    return segments


def extract_reference_sample(audio_path):
    """Extract a clean 10s clip from the middle of the audio for better cloning"""
    ref_path = os.path.join(TEMP_DIR, "reference_voice.wav")
    print(f"[INFO] Extracting clean voice reference sample...", flush=True)
    
    # We take 10 seconds starting from 5s to avoid potential intro music
    ffmpeg_exe = config.FFMPEG
    cmd = [
        ffmpeg_exe, "-y",
        "-i", audio_path,
        "-ss", "00:00:05",
        "-t", "00:00:10",
        "-ac", "1",
        "-ar", "24000", # XTTS v2 likes 24kHz
        ref_path
    ]
    subprocess.run(cmd, capture_output=True)
    
    # If file too short or failed, fallback to original
    if not os.path.exists(ref_path) or os.path.getsize(ref_path) < 1000:
        print("[WARN] Reference extraction too short, using full audio.", flush=True)
        return audio_path
        
    return ref_path


# ---------------- TRANSLATION (WITH RETRIES) ----------------
def translate_text(text, source_code, target_code):
    if not text.strip():
        return ""

    import re
    text = re.sub(r'\s+', ' ', text).strip()

    max_retries = 5 # Increased retries
    for attempt in range(max_retries):
        try:
            t = get_translator(source_code, target_code)
            result = t.translate(text)
            
            if result:
                if hasattr(result, "text"):
                    return result.text
                return str(result)
            
            print(f"[WARN] Translation attempt {attempt+1} returned empty", flush=True)
        except Exception as e:
            print(f"[WARN] Translation error on attempt {attempt+1}: {e}", flush=True)
            time.sleep(3) # Wait slightly longer before retry
            
    print("[ERROR] All translation attempts failed. Falling back to original text.", flush=True)
    return text


# ---------------- PITCH MATCHING & GENDER ----------------
def get_median_pitch(audio_path):
    import librosa
    import numpy as np
    try:
        # Load audio with 16k mono
        y, sr = librosa.load(audio_path, sr=16000)
        
        # pyin (Probabilistic YIN) is much more robust for F0 estimation
        fmin = librosa.note_to_hz('C2') # ~65Hz
        fmax = librosa.note_to_hz('C7') # ~2000Hz
        
        f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=fmin, fmax=fmax, sr=sr)
        
        # Filter only voiced frames with high confidence
        valid_f0 = f0[(voiced_probs > 0.6) & (~np.isnan(f0))]
        
        if len(valid_f0) == 0:
            return None
            
        return np.nanmedian(valid_f0)
    except Exception as e:
        print(f"[WARN] Pitch detection error: {e}", flush=True)
        return None

def detect_gender(audio_path):
    pitch = get_median_pitch(audio_path)
    if not pitch: 
        print("[WARN] Pitch not clearly detected. Defaulting to male.", flush=True)
        return "male"
    
    # Typical thresholds: Male (85-155Hz), Female (165-255Hz)
    # 160Hz is a safe pivot point
    print(f"[INFO] Analyzed Pitch: {pitch:.1f} Hz", flush=True)
    
    if pitch > 162:
        return "female"
    else:
        return "male"


# ---------------- NATURAL TTS (EDGE TTS WITH SSML) ----------------
def apply_ssml(text, voice, gender):
    """Wrap text in SSML for natural pauses and prosody"""
    # Clean text: remove extra spaces and ensure basic punctuation
    text = text.strip().replace("  ", " ")
    
    # Simple split by punctuation to add minor pauses
    import re
    sentences = re.split(r'([।\.!\?])', text)
    
    ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="mr-IN">'
    
    # Fine-tune rate and pitch based on gender for maximum naturalness
    rate = "+0%" # Natural pace
    pitch = "-1Hz" # Slightly deeper tone for better authority
    
    if gender == "female":
        pitch = "+0Hz" # Keep female voice clear
        rate = "+5%" # Slightly faster for female persona
        
    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i].strip()
        punc = sentences[i+1]
        if sentence:
            # Add prosody with natural breaks
            ssml += f'<prosody rate="{rate}" pitch="{pitch}">{sentence}{punc}</prosody>'
            ssml += '<break time="400ms"/>' # Natural pause between sentences
            
    # Handle trailing text if any
    if len(sentences) % 2 != 0:
        last = sentences[-1].strip()
        if last:
            ssml += f'<prosody rate="{rate}" pitch="{pitch}">{last}</prosody>'
            
    ssml += '</speak>'
    return ssml

def synthesize_speech(text, gender, target_lang):

    if not text.strip():
        raise RuntimeError("Translation produced empty text")

    print(f"[INFO] Generating {target_lang.display_name} speech (Edge TTS) - Voice: {gender}...", flush=True)

    voice = target_lang.edge_voices.get(gender) or target_lang.edge_voices["male"]

    audio_path = os.path.join(TEMP_DIR, "tts_stock.wav")

    import edge_tts
    import asyncio

    rate_val = "+2%" if gender == "female" else "-2%"
    pitch_val = "+0Hz"

    communicate = edge_tts.Communicate(text, voice, rate=rate_val, pitch=pitch_val)
    
    for attempt in range(3): # 3 retries for TTS
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(communicate.save(audio_path))
            
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                print(f"[DEBUG] TTS SUCCESS (Attempt {attempt+1})", flush=True)
                return audio_path
        except Exception as e:
            print(f"[WARN] TTS attempt {attempt+1} failed: {e}", flush=True)
            time.sleep(2)

    raise RuntimeError("TTS failed after multiple attempts")


def synthesize_cloned_speech(text, speaker_wav, out_path, target_lang):
    """Bridge call to voiceclone_env specifically for synthesis"""
    if not text.strip():
        raise RuntimeError("Empty text for cloned synthesis")

    if target_lang.xtts_code is None:
        raise RuntimeError(
            f"Voice cloning is not available for {target_lang.display_name}: "
            "XTTS v2 has no supported language code for it"
        )
    if target_lang.xtts_is_proxy:
        print(f"[WARN] XTTS has no native {target_lang.display_name}; synthesizing via "
              f"proxy language '{target_lang.xtts_code}'. Quality caveat applies.", flush=True)

    print(f"[INFO] Bridging to voiceclone_env for XTTS v2 Cloning...", flush=True)

    if not config.CLONE_PYTHON:
        raise RuntimeError(
            "Voice cloning requested but SYNCDUB_CLONE_PYTHON is not set "
            "(path to the XTTS environment's python; see .env.example)"
        )
    BRIDGE_SCRIPT = os.path.join(BASE_DIR, "clone_bridge.py")

    cmd = [
        config.CLONE_PYTHON, BRIDGE_SCRIPT,
        "--text", text,
        "--speaker_wav", speaker_wav,
        "--out_path", out_path,
        "--language", target_lang.xtts_code
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            print(f"[ERROR] Bridge Error: {result.stderr}", flush=True)
            raise RuntimeError(f"Voice cloning bridge failed: {result.stderr}")
        
        print("[INFO] Voice Cloning Bridge SUCCESS", flush=True)
        return out_path
    except Exception as e:
        print(f"[ERROR] Bridge execution failed: {e}", flush=True)
        raise e


# ---------------- AUDIO NORMALIZATION ----------------
def normalize_audio(audio_path):

    if not os.path.exists(audio_path):
        raise RuntimeError("TTS audio file not found")

    if os.path.getsize(audio_path) == 0:
        raise RuntimeError("TTS audio file is empty")

    out_path = os.path.join(TEMP_DIR, "marathi_16k.wav")

    ffmpeg_exe = config.FFMPEG
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

    print("[INFO] Audio ready:", out_path, flush=True)

    return out_path


def sync_audio_duration(audio_path, target_duration):
    """Adjusts audio tempo to match target duration precisely"""
    import librosa
    y, sr = librosa.load(audio_path, sr=None)
    current_duration = librosa.get_duration(y=y, sr=sr)
    
    if current_duration <= 0:
        return audio_path
        
    # Calculate tempo factor
    tempo = current_duration / target_duration
    # FFmpeg atempo range is 0.5 to 2.0
    tempo = max(0.5, min(2.0, tempo))
    
    synced_path = os.path.join(TEMP_DIR, "marathi_synced.wav")
    print(f"[INFO] Syncing audio duration: {current_duration:.2f}s -> {target_duration:.2f}s (Speed: {tempo:.2f}x)", flush=True)

    ffmpeg_exe = config.FFMPEG
    cmd = [
        ffmpeg_exe, "-y",
        "-i", audio_path,
        "-filter:a", f"atempo={tempo:.2f}",
        synced_path
    ]
    subprocess.run(cmd, capture_output=True)
    return synced_path


# ---------------- SEGMENT GROUPING ----------------
def group_segments(segments, gap_threshold=1.5):
    """Group ASR segments into context blocks for translation.

    Translating whole blocks instead of line fragments preserves Marathi
    grammar. A pause longer than gap_threshold seconds starts a new block.
    """
    grouped_text = []
    current_block = []

    last_end = 0
    for seg in segments:
        hi_text = seg["text"].strip()
        if not hi_text:
            continue

        if current_block and (seg["start"] - last_end) > gap_threshold:
            grouped_text.append(" ".join(current_block))
            current_block = [hi_text]
        else:
            current_block.append(hi_text)

        last_end = seg["end"]

    if current_block:
        grouped_text.append(" ".join(current_block))

    return grouped_text


# ---------------- MAIN PIPELINE ----------------
def process_video(video_path, job_id, source_lang="hi", target_lang="mr"):

    src, tgt = validate_pair(source_lang, target_lang)

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
    update_progress(25, f"Transcribing {src.display_name} speech")
    # Pre-normalize audio for better ASR
    asr_audio = normalize_audio(audio_path)
    segments = transcribe_audio(asr_audio, src.whisper_code)

    print("[INFO] Translating segments with grammatical context...")

    grouped_text = group_segments(segments)

    print(f"[INFO] Translation blocks created: {len(grouped_text)}", flush=True)

    if src.code == tgt.code:
        # Same-language job: re-voicing only, no translation stage.
        update_progress(50, "Skipping translation (same language)")
        translated_blocks = list(grouped_text)
    else:
        update_progress(50, f"Translating to {tgt.display_name} (Contextual)")
        translated_blocks = []
        for block in grouped_text:
            block_text = translate_text(block, src.translator_code, tgt.translator_code)
            try:
                print(f"[DEBUG] Translated block: {block_text[:50]}...", flush=True)
            except:
                pass
            translated_blocks.append(block_text)

    final_text = " ".join(translated_blocks)

    if not final_text.strip():
        raise RuntimeError("Translation returned empty text")

    # Extract speaker voice sample for cloning
    update_progress(65, "Extracting voice profile")
    reference_wav = extract_reference_sample(asr_audio)

    # Generate speech
    if USE_VOICE_CLONING:
        update_progress(70, "Synthesizing dubbed audio (Voice Cloning)")
        try:
            # We use the clean reference_wav instead of the full audio_path
            tts_audio = synthesize_cloned_speech(
                final_text, reference_wav, os.path.join(TEMP_DIR, "tts_cloned.wav"), tgt
            )
        except Exception as e:
            print(f"[WARN] Voice cloning failed: {e}. Falling back to Edge-TTS.", flush=True)
            # Detect speaker gender as fallback
            speaker_gender = detect_gender(audio_path)
            tts_audio = synthesize_speech(final_text, speaker_gender, tgt)
    else:
        update_progress(70, "Synthesizing dubbed audio (Natural)")
        speaker_gender = detect_gender(audio_path)
        tts_audio = synthesize_speech(final_text, speaker_gender, tgt)

    # NORMALIZE (KEEPING 1.0x SPEED AS REQUESTED)
    tts_audio = normalize_audio(tts_audio)
    
    # We disable sync_audio_duration as per user request for "normal speed"
    # orig_duration = librosa.get_duration(filename=audio_path)
    # tts_audio = sync_audio_duration(tts_audio, orig_duration)

    print(f"[DEBUG] Final normal-speed TTS path: {tts_audio}", flush=True)

    # FREE MEMORY BEFORE WAV2LIP
    unload_models()

    # Output video (per-job name; nothing is overwritten across jobs)
    output_video = str(jobs.job_paths(job_id).output_path)

    print("[INFO] Running Wav2Lip...", flush=True)
    update_progress(85, "Merging audio and video")
    print(f"[DEBUG] VIDEO: {video_path}", flush=True)
    print(f"[DEBUG] AUDIO: {tts_audio}", flush=True)
    print(f"[DEBUG] OUTPUT: {output_video}", flush=True)

    from lipdub.wav2lip_wrapper import run_wav2lip
    run_wav2lip(video_path, tts_audio, output_video, progress_callback=update_progress)

    if not os.path.exists(output_video):
        raise RuntimeError("Wav2Lip finished but output video not found")

    if PROGRESS is not None:
        PROGRESS.done(video_url=f"/outputs/{job_id}.mp4")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] SUCCESS -> {output_video}")

# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--video",
        type=str,
        required=True,
        help="Video filename inside uploads folder OR full path"
    )
    parser.add_argument(
        "--job-id",
        type=str,
        default=None,
        help="Job identifier (assigned by the server; generated for CLI runs)"
    )
    parser.add_argument("--source-lang", type=str, default="hi")
    parser.add_argument("--target-lang", type=str, default="mr")

    args = parser.parse_args()
    job_id = args.job_id or jobs.new_job_id()
    paths = jobs.job_paths(job_id)
    jobs.ensure_job_dirs(paths)

    PROGRESS = jobs.ProgressWriter(
        paths.progress_path, job_id,
        fields={"source_lang": args.source_lang, "target_lang": args.target_lang},
    )

    if not jobs.acquire_pipeline_lock(job_id):
        PROGRESS.fail("Another job is already running on this machine")
        sys.exit(1)
    try:
        process_video(args.video, job_id, args.source_lang, args.target_lang)
    except Exception as e:
        PROGRESS.fail(str(e))
        raise
    finally:
        jobs.release_pipeline_lock(job_id)