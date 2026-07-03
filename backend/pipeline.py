"""SyncDub dubbing pipeline: source video in, dubbed lip-synced video out.

Stage flow (Founder OS Ch. 7): extract audio -> Whisper ASR -> block grouping
(segment schema, stages/types.py) -> per-block translation -> per-segment
synthesis behind the Synthesizer interface -> isochronous track assembly
(stages/assembly.py) -> Wav2Lip -> outputs/{job_id}.mp4.

Runs as a subprocess of server.py (one job at a time, jobs.py lock). All
intermediates live in temp/{job_id}/ and are deleted when the job ends —
including the voice reference sample, the most sensitive artifact we hold
(Ch. 5/Ch. 12).
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import config
import jobs
import metrics
from stages import assembly
from stages.edge_tts_synth import EdgeTTSSynthesizer
from stages.languages import validate_pair
from stages.synthesizer import SynthesisError, SynthesisOptions
from stages.types import Segment
from stages.xtts_synth import XTTSCloneSynthesizer

config.ensure_dirs()

# Set in __main__; stays None when the module is imported (tests, tooling),
# in which case progress updates only print.
PROGRESS: "jobs.ProgressWriter | None" = None


def update_progress(progress, status):
    if PROGRESS is not None:
        PROGRESS.update(progress, status)
    else:
        print(f"[PROGRESS] {progress}% - {status}", flush=True)


def set_progress_fields(**fields):
    if PROGRESS is not None:
        PROGRESS.set_fields(**fields)


# ---------------- MODELS ----------------
whisper_model = None
translator = None  # (src, tgt) keyed tuple; see get_translator


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
    """Clear memory before the heavy Wav2Lip step. XTTS lives in its own
    subprocess and never occupies this interpreter's memory."""
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
    except Exception:
        pass


# ---------------- AUDIO EXTRACTION ----------------
def extract_audio(video_path, temp_dir):
    print("[INFO] Extracting audio...")
    from moviepy.editor import VideoFileClip
    audio_path = os.path.join(temp_dir, "source_audio.wav")

    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, codec="pcm_s16le", logger=None)
    clip.close()

    if not os.path.exists(audio_path):
        raise RuntimeError("Audio extraction failed")

    return audio_path


def normalize_audio(audio_path, out_path):
    """Mono 16 kHz wav — what Whisper and Wav2Lip both want."""
    if not os.path.exists(audio_path):
        raise RuntimeError(f"Audio file not found: {audio_path}")
    if os.path.getsize(audio_path) == 0:
        raise RuntimeError(f"Audio file is empty: {audio_path}")

    cmd = [config.FFMPEG, "-y", "-i", audio_path, "-ac", "1", "-ar", "16000", out_path]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(result.stderr.decode(errors="replace"))
        raise RuntimeError("FFmpeg conversion failed")
    if not os.path.exists(out_path):
        raise RuntimeError("Normalized audio not created")

    print("[INFO] Audio ready:", out_path, flush=True)
    return out_path


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


# ---------------- SEGMENT GROUPING ----------------
def group_segments(asr_segments, gap_threshold=1.5):
    """Group ASR segments into timed context blocks (Segment schema).

    Translating whole blocks instead of line fragments preserves target-language
    grammar. A pause longer than gap_threshold seconds starts a new block; the
    pause boundaries are exactly where dubbed audio must re-anchor (Ch. 17).
    """
    blocks = []
    current_texts = []
    block_start = 0.0
    last_end = 0.0

    def close_block():
        if current_texts:
            blocks.append(Segment(
                idx=len(blocks),
                start=block_start,
                end=last_end,
                source_text=" ".join(current_texts),
            ))

    for seg in asr_segments:
        text = seg["text"].strip()
        if not text:
            continue

        if current_texts and (seg["start"] - last_end) > gap_threshold:
            close_block()
            current_texts = [text]
            block_start = seg["start"]
        else:
            if not current_texts:
                block_start = seg["start"]
            current_texts.append(text)

        last_end = seg["end"]

    close_block()
    return blocks


# ---------------- EMOTION TAGGING ----------------
def tag_emotions(segments):
    """Punctuation-only delivery tags (emotion rung 2, Ch. 18 §18.3).

    Records how the speaker delivered a block — never infers feelings
    (Ch. 18 §18.4). Tags flow to synthesizers that accept style controls;
    engines without them simply record the tag in the job metrics.
    """
    for seg in segments:
        text = seg.source_text.rstrip()
        if text.endswith("?") or text.endswith("?!"):
            seg.emotion = "questioning"
        elif text.endswith("!"):
            seg.emotion = "emphatic"
    return segments


# ---------------- TRANSLATION (WITH RETRIES) ----------------
def translate_text(text, source_code, target_code):
    if not text.strip():
        return ""

    import re
    text = re.sub(r'\s+', ' ', text).strip()

    max_retries = 5
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
            time.sleep(3)

    print("[ERROR] All translation attempts failed. Falling back to original text.", flush=True)
    return text


def translate_segments(segments, src, tgt):
    """Fill translated_text per block; same-language jobs pass text through."""
    if src.code == tgt.code:
        for seg in segments:
            seg.translated_text = seg.source_text
        return segments

    for seg in segments:
        seg.translated_text = translate_text(
            seg.source_text, src.translator_code, tgt.translator_code
        )
        try:
            print(f"[DEBUG] Translated block {seg.idx}: {seg.translated_text[:50]}...", flush=True)
        except Exception:
            pass
    return segments


# ---------------- PITCH MATCHING & GENDER ----------------
def get_median_pitch(audio_path):
    import librosa
    import numpy as np
    try:
        # Load audio with 16k mono
        y, sr = librosa.load(audio_path, sr=16000)

        # pyin (Probabilistic YIN) is much more robust for F0 estimation
        fmin = librosa.note_to_hz('C2')  # ~65Hz
        fmax = librosa.note_to_hz('C7')  # ~2000Hz

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
    # 162Hz is a safe pivot point
    print(f"[INFO] Analyzed Pitch: {pitch:.1f} Hz", flush=True)
    return "female" if pitch > 162 else "male"


# ---------------- VOICE REFERENCE ----------------
def extract_reference_sample(audio_path, temp_dir, segments=None):
    """Reference clip for cloning, mono 24 kHz (XTTS v2's native rate).

    Preference order: prosody-scored window selection (stages/reference.py,
    emotion rung 1) -> fixed 10 s cut at 5 s (skips intro music) -> full audio.
    Lives only inside temp/{job_id}/ — deleted with the job (Ch. 12 §12.3)."""
    ref_path = os.path.join(temp_dir, "reference_voice.wav")

    if segments:
        from stages.reference import select_reference
        selected = select_reference(audio_path, segments, ref_path)
        if selected:
            return selected

    print("[INFO] Extracting fixed voice reference sample...", flush=True)
    cmd = [
        config.FFMPEG, "-y",
        "-i", audio_path,
        "-ss", "00:00:05",
        "-t", "00:00:10",
        "-ac", "1",
        "-ar", "24000",
        ref_path,
    ]
    subprocess.run(cmd, capture_output=True)

    if not os.path.exists(ref_path) or os.path.getsize(ref_path) < 1000:
        print("[WARN] Reference extraction too short, using full audio.", flush=True)
        return audio_path

    return ref_path


# ---------------- SYNTHESIS ----------------
def synthesize_segments(segments, tgt, temp_dir, *, enable_cloning, reference_wav, gender):
    """Run the chosen Synthesizer; a cloning failure is a loud, whole-job
    fallback to stock voices — never a mid-video voice change."""
    synth_dir = os.path.join(temp_dir, "synth")
    fallback_reason = None

    if enable_cloning:
        update_progress(70, "Synthesizing dubbed audio (Voice Cloning)")
        try:
            options = SynthesisOptions(speaker_wav=reference_wav)
            segments = XTTSCloneSynthesizer().synthesize(segments, tgt, synth_dir, options)
            return segments, "xtts_clone", None
        except SynthesisError as e:
            fallback_reason = str(e)
            print(f"[WARN] Voice cloning failed: {e}. Falling back to Edge-TTS.", flush=True)

    update_progress(70, "Synthesizing dubbed audio (Natural)")
    # map_emotion: Edge-TTS accepts style controls, so recorded delivery tags
    # become small prosody nudges (Ch. 18 rung 2). XTTS has none — the tag is
    # recorded in metrics only.
    options = SynthesisOptions(gender=gender, map_emotion=True)
    segments = EdgeTTSSynthesizer().synthesize(segments, tgt, synth_dir, options)
    return segments, "edge_tts", fallback_reason


# ---------------- MAIN PIPELINE ----------------
def process_video(video_path, job_id, source_lang="hi", target_lang="mr", enable_cloning=False):
    src, tgt = validate_pair(source_lang, target_lang)
    paths = jobs.job_paths(job_id)
    jobs.ensure_job_dirs(paths)
    temp_dir = str(paths.temp_dir)

    if not os.path.isabs(video_path):
        video_path = os.path.join(str(config.UPLOAD_DIR), video_path)
    video_path = os.path.abspath(video_path)
    if not os.path.exists(video_path):
        raise FileNotFoundError(video_path)

    print("[START] Processing:", video_path)
    update_progress(10, "Extracting audio track")
    audio_path = extract_audio(video_path, temp_dir)
    total_duration_s = assembly.measure_duration_s(audio_path)

    update_progress(25, f"Transcribing {src.display_name} speech")
    asr_audio = normalize_audio(audio_path, os.path.join(temp_dir, "asr_16k.wav"))
    asr_segments = transcribe_audio(asr_audio, src.whisper_code)

    segments = group_segments(asr_segments)
    segments = tag_emotions(segments)
    print(f"[INFO] Translation blocks created: {len(segments)}", flush=True)
    if not segments:
        raise RuntimeError("No speech detected in the source video")

    if src.code == tgt.code:
        update_progress(50, "Skipping translation (same language)")
    else:
        update_progress(50, f"Translating to {tgt.display_name} (Contextual)")
    segments = translate_segments(segments, src, tgt)

    if not any(seg.translated_text.strip() for seg in segments):
        raise RuntimeError("Translation returned empty text")

    update_progress(65, "Extracting voice profile")
    # The reference sample is sensitive personal data — only extract it when
    # a consented cloning run will actually use it (Ch. 5 §5.2).
    reference_wav = (
        extract_reference_sample(asr_audio, temp_dir, segments)
        if enable_cloning else None
    )
    gender = detect_gender(audio_path)

    segments, synthesizer_used, fallback_reason = synthesize_segments(
        segments, tgt, temp_dir,
        enable_cloning=enable_cloning, reference_wav=reference_wav, gender=gender,
    )
    set_progress_fields(synthesizer_used=synthesizer_used, fallback_reason=fallback_reason)

    update_progress(80, "Assembling isochronous audio track")
    placements = assembly.plan_placement(segments, total_duration_s)
    for seg, placement in zip(segments, placements):
        if seg.synth_path and placement.rate != 1.0:
            rated_path = os.path.join(temp_dir, "synth", f"seg_{seg.idx:04d}_rated.wav")
            seg.synth_path = assembly.apply_rate(seg.synth_path, placement.rate, rated_path)
            seg.rate_applied = placement.rate
        if placement.clamped:
            print(f"[WARN] Segment {seg.idx}: ideal rate outside "
                  f"[{assembly.RATE_MIN}, {assembly.RATE_MAX}], clamped to {placement.rate} "
                  f"(overlap {placement.overlap_ms} ms)", flush=True)

    dub_track = assembly.assemble_track(
        segments, placements, total_duration_s, os.path.join(temp_dir, "dub_track.wav")
    )

    speaker_similarity = None
    if synthesizer_used == "xtts_clone" and reference_wav:
        update_progress(82, "Measuring speaker similarity")
        speaker_similarity = metrics.compute_speaker_similarity(reference_wav, dub_track)
        if speaker_similarity is not None:
            print(f"[INFO] Speaker similarity (reference vs dub): {speaker_similarity}",
                  flush=True)
            set_progress_fields(speaker_similarity=speaker_similarity)

    metrics.write_job_metrics(paths.metrics_path, metrics.build_job_metrics(
        job_id=job_id,
        total_duration_s=total_duration_s,
        segments=segments,
        placements=placements,
        synthesizer_used=synthesizer_used,
        fallback_reason=fallback_reason,
        speaker_similarity=speaker_similarity,
    ))

    # FREE MEMORY BEFORE WAV2LIP
    unload_models()

    output_video = str(paths.output_path)
    print("[INFO] Running Wav2Lip...", flush=True)
    update_progress(85, "Merging audio and video")
    print(f"[DEBUG] VIDEO: {video_path}", flush=True)
    print(f"[DEBUG] AUDIO: {dub_track}", flush=True)
    print(f"[DEBUG] OUTPUT: {output_video}", flush=True)

    from lipdub.wav2lip_wrapper import run_wav2lip
    run_wav2lip(video_path, dub_track, output_video, progress_callback=update_progress)

    if not os.path.exists(output_video):
        raise RuntimeError("Wav2Lip finished but output video not found")

    if PROGRESS is not None:
        PROGRESS.done(video_url=f"/outputs/{job_id}.mp4")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] SUCCESS -> {output_video}")


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=str, required=True,
                        help="Video filename inside uploads folder OR full path")
    parser.add_argument("--job-id", type=str, default=None,
                        help="Job identifier (assigned by the server; generated for CLI runs)")
    parser.add_argument("--source-lang", type=str, default="hi")
    parser.add_argument("--target-lang", type=str, default="mr")
    parser.add_argument("--clone", action="store_true",
                        help="Clone the speaker's voice (requires the consent flags "
                             "recorded by the server; CLI runs assert consent themselves)")

    args = parser.parse_args()
    job_id = args.job_id or jobs.new_job_id()
    paths = jobs.job_paths(job_id)
    jobs.ensure_job_dirs(paths)

    # Preserve fields the server already recorded (consent facts, languages).
    existing = jobs.read_progress(paths.progress_path) or {}
    seed_fields = {
        k: v for k, v in existing.items()
        if k not in ("job_id", "progress", "status", "state", "error")
    }
    seed_fields.setdefault("source_lang", args.source_lang)
    seed_fields.setdefault("target_lang", args.target_lang)
    seed_fields.setdefault("cloning_requested", bool(args.clone))

    # Consent before capability (Ch. 5 §5.2), enforced here too so a CLI run
    # cannot clone without a recorded speaker consent, whatever flags it passes.
    enable_cloning = bool(args.clone)
    if enable_cloning:
        consent = jobs.read_consent_record(paths)
        if not consent or not consent.get("speaker_cloning_consent"):
            enable_cloning = False
            seed_fields["cloning_granted"] = False
            seed_fields["fallback_reason"] = (
                "speaker consent for voice cloning was not recorded"
            )
            print("[WARN] --clone requested without a recorded speaker consent "
                  f"(jobs/{job_id}/consent.json). Using stock voices.", flush=True)

    PROGRESS = jobs.ProgressWriter(paths.progress_path, job_id, fields=seed_fields)

    if not jobs.acquire_pipeline_lock(job_id):
        PROGRESS.fail("Another job is already running on this machine")
        sys.exit(1)
    try:
        process_video(args.video, job_id, args.source_lang, args.target_lang,
                      enable_cloning=enable_cloning)
    except Exception as e:
        PROGRESS.fail(str(e))
        raise
    finally:
        jobs.release_pipeline_lock(job_id)
        # temp/{job_id}/ holds the voice reference sample — never outlives the job
        shutil.rmtree(paths.temp_dir, ignore_errors=True)
