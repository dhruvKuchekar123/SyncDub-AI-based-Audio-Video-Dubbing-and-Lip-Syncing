import argparse
import os
import subprocess
import librosa
import soundfile as sf
from moviepy.editor import VideoFileClip
from transformers import pipeline
from google.cloud import texttospeech
from lipdub.wav2lip_wrapper import run_wav2lip
import whisper

# ---------------- CONFIGURATION ----------------
USE_VOICE_CLONING = True  # SET TO False TO REVERT TO DEFAULT VOICES


# ------------------- AUDIO EXTRACTION -------------------
def extract_audio(video_path, audio_path="temp_audio.wav"):
    print("[INFO] Extracting audio from video...")
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, codec='pcm_s16le')
    return audio_path


# ------------------- SPEECH TO TEXT -------------------
def transcribe_audio_segments(audio_path, model_size="large"):
    print("[INFO] Loading Whisper model (word timestamps enabled)...")
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, word_timestamps=True)
    detected_lang = result.get("language", "unknown")
    segments = result.get("segments", [])
    print(f"[DEBUG] Detected language: {detected_lang}")
    print(f"[INFO] {len(segments)} segments detected.")
    return segments, detected_lang


def extract_reference_sample(audio_path):
    """Extract a clean 10s clip for better cloning"""
    # Assuming audio_path is accessible
    ref_path = "reference_voice.wav"
    print(f"[INFO] Extracting clean voice reference sample...")
    
    # Take 10 seconds starting from 5s
    cmd = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-ss", "00:00:05",
        "-t", "00:00:10",
        "-ac", "1",
        "-ar", "24000",
        ref_path
    ]
    import subprocess
    subprocess.run(cmd, capture_output=True)
    
    if not os.path.exists(ref_path) or os.path.getsize(ref_path) < 1000:
        return audio_path
        
    return ref_path


# ------------------- TRANSLATION -------------------
def create_translator():
    print("[INFO] Loading NLLB translation model for Hindi → Marathi...")
    translator_hi_mr = pipeline("translation", model="facebook/nllb-200-distilled-600M")
    return translator_hi_mr


def translate_segment(translator, text):
    if not text.strip():
        return ""
    result = translator(text, src_lang="hin_Deva", tgt_lang="mar_Deva", max_length=512)
    return result[0]["translation_text"]


# ------------------- GENDER DETECTION -------------------
def detect_gender_from_text(text):
    text_lower = text.lower()
    male_words = ["main", "mera", "beta", "bhai", "uncle", "sir"]
    female_words = ["meri", "beti", "behen", "madam", "aunty"]
    male_count = sum(w in text_lower for w in male_words)
    female_count = sum(w in text_lower for w in female_words)
    return "male" if male_count >= female_count else "female"


# ---------------- VOICE CLONING (XTTS v2) ----------------
xtts_model = None

def get_xtts_model():
    """XTTS v2 is handled via the bridge script in voiceclone_env"""
    pass

def synthesize_cloned_speech(text, speaker_wav, out_path):
    """Bridge call to voiceclone_env specifically for synthesis"""
    import subprocess
    import os
    
    CLONE_PYTHON = r"D:\Miniconda3\envs\voiceclone_env\python.exe"
    # Bridge is in backend/ folder
    BRIDGE_SCRIPT = os.path.join(os.getcwd(), "backend", "clone_bridge.py")

    cmd = [
        CLONE_PYTHON, BRIDGE_SCRIPT,
        "--text", text,
        "--speaker_wav", speaker_wav,
        "--out_path", out_path,
        "--language", "mr"
    ]

    try:
        print(f"[INFO] Bridging synthesis to voiceclone_env...")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            print(f"[ERROR] Bridge Error: {result.stderr}")
            raise RuntimeError(f"Cloning bridge failed: {result.stderr}")
        
        return out_path
    except Exception as e:
        print(f"[ERROR] Bridge execution failed: {e}")
        raise e


# ------------------- TEXT TO SPEECH (GOOGLE CLOUD) -------------------
def synthesize_speech_google_ssml(text, out_path="dubbed_audio.wav", language_code="mr-IN", gender="male"):
    if not text:
        print("[ERROR] Empty text for TTS.")
        return None

    client = texttospeech.TextToSpeechClient()

    # SSML with natural prosody
    ssml_text = f"""
    <speak>
        <prosody rate="1.15" pitch="-1st">
            {text}
        </prosody>
    </speak>
    """

    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
    voice_name = "mr-IN-Wavenet-A" if gender == "male" else "mr-IN-Wavenet-B"

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.SsmlVoiceGender.MALE if gender == "male" else texttospeech.SsmlVoiceGender.FEMALE,
        name=voice_name
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(out_path, "wb") as f:
        f.write(response.audio_content)

    return out_path


# ------------------- AUDIO PROCESSING HELPERS -------------------
def ensure_mono_16k(input_wav, out_wav):
    cmd = ["ffmpeg", "-y", "-i", input_wav, "-ac", "1", "-ar", "16000", out_wav]
    subprocess.run(cmd, check=True)
    return out_wav


def ffmpeg_tempo_sync(input_wav, target_dur, out_wav):
    """Adjusts tempo using FFmpeg atempo filter (natural pitch)"""
    y, sr = librosa.load(input_wav, sr=None)
    current_dur = librosa.get_duration(y=y, sr=sr)
    if current_dur == 0:
        return input_wav
    tempo = current_dur / target_dur
    tempo = max(0.5, min(2.0, tempo))  # FFmpeg valid atempo range
    subprocess.run(
        ["ffmpeg", "-y", "-i", input_wav, "-filter:a", f"atempo={tempo:.2f}", out_wav],
        check=True
    )
    return out_wav


# ------------------- MAIN PROCESS -------------------
def process_video_segmented(video_path, src_lang="hi", tgt_lang="mr"):
    audio_path = extract_audio(video_path, "temp_audio.wav")
    segments, detected_lang = transcribe_audio_segments(audio_path)
    translator = create_translator()
    out_segments = []

    # Extract speaker voice sample for cloning
    reference_wav = extract_reference_sample(audio_path)

    for i, seg in enumerate(segments):
        start, end, text = seg["start"], seg["end"], seg["text"].strip()
        if not text:
            continue

        print(f"[SEG {i}] {start:.2f}-{end:.2f}s: {text}")
        translated = translate_segment(translator, text)
        gender = detect_gender_from_text(text)

        tts_wav = f"tts_{i}.wav"
        if USE_VOICE_CLONING:
            try:
                # Use the clean reference_wav for all segments
                synthesize_cloned_speech(translated, reference_wav, tts_wav)
            except Exception as e:
                print(f"[WARN] Cloning failed for seg {i}: {e}. Falling back to Google TTS.")
                synthesize_speech_google_ssml(translated, tts_wav, language_code="mr-IN", gender=gender)
        else:
            synthesize_speech_google_ssml(translated, tts_wav, language_code="mr-IN", gender=gender)

        tts_mono = f"tts_{i}_16k.wav"
        ensure_mono_16k(tts_wav, tts_mono)

        # NORMAL SPEED: We skip tempo sync to keep voice natural
        tts_synced = tts_mono
        # ffmpeg_tempo_sync(tts_mono, target_dur, tts_synced)

        seg_vid = f"seg_{i}.mp4"
        subprocess.run(["ffmpeg", "-y", "-i", video_path, "-ss", str(start), "-to", str(end), "-c", "copy", seg_vid])

        out_seg = f"seg_{i}_dubbed.mp4"
        run_wav2lip(seg_vid, tts_synced, out_seg)
        out_segments.append(out_seg)

    with open("filelist.txt", "w", encoding="utf-8") as f:
        for p in out_segments:
            f.write(f"file '{os.path.abspath(p)}'\n")

    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "filelist.txt",
                    "-c", "copy", "final_dubbed.mp4"], check=True)

    print("[✅ SUCCESS] final_dubbed.mp4 created successfully.")


# ------------------- ENTRY POINT -------------------
def main(video_path, src_lang="hi", tgt_lang="mr"):
    process_video_segmented(video_path, src_lang, tgt_lang)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=str, required=True, help="Input video file")
    parser.add_argument("--src_lang", type=str, default="hi", help="Source language (default: Hindi)")
    parser.add_argument("--tgt_lang", type=str, default="mr", help="Target language (default: Marathi)")
    args = parser.parse_args()

    main(args.video, src_lang=args.src_lang, tgt_lang=args.tgt_lang)
