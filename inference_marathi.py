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

    for i, seg in enumerate(segments):
        start, end, text = seg["start"], seg["end"], seg["text"].strip()
        if not text:
            continue

        print(f"[SEG {i}] {start:.2f}-{end:.2f}s: {text}")
        translated = translate_segment(translator, text)
        gender = detect_gender_from_text(text)

        tts_wav = f"tts_{i}.wav"
        synthesize_speech_google_ssml(translated, tts_wav, language_code="mr-IN", gender=gender)

        tts_mono = f"tts_{i}_16k.wav"
        ensure_mono_16k(tts_wav, tts_mono)

        target_dur = end - start
        tts_synced = f"tts_{i}_synced.wav"
        ffmpeg_tempo_sync(tts_mono, target_dur, tts_synced)

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
