import subprocess, os
from pathlib import Path

def run(cmd, verbose=True):
    if verbose:
        print('RUN:', ' '.join(cmd))
    subprocess.check_call(cmd)

def extract_audio(video_path, out_wav, sr=16000):
    out_wav = str(out_wav)
    run(['ffmpeg', '-y', '-i', video_path, '-vn', '-ac', '1', '-ar', str(sr), out_wav])

def mux_audio(video_input, audio_input, out_file):
    run(['ffmpeg', '-y', '-i', video_input, '-i', audio_input,
         '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0', '-shortest', out_file])

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)
