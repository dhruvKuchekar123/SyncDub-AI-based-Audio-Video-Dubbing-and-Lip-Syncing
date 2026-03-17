import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence

r = sr.Recognizer()
sound = AudioSegment.from_file("temp_audio.wav", format="wav")

chunks = split_on_silence(sound, min_silence_len=500, silence_thresh=sound.dBFS-14, keep_silence=400)

print(f"Chunks: {len(chunks)}")
for i, chunk in enumerate(chunks):
    filename = f"chunk{i}.wav"
    chunk.export(filename, format="wav")
    with sr.AudioFile(filename) as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data, language="hi-IN")
            print(f"Chunk {i}: {text}")
        except Exception as e:
            print(f"Chunk {i} failed: {e}")
