# Simple TTS wrapper. Default uses gTTS for quick testing. Replace with AI4Bharat or Google Cloud for production.
from gtts import gTTS
from pydub import AudioSegment
import os
from pathlib import Path

class TTS:
    def __init__(self, engine='gtts', config=None):
        self.engine = engine
        self.config = config or {}

    def synthesize_gtts(self, text, lang, out_mp3):
        t = gTTS(text=text, lang=lang)
        t.save(out_mp3)
        # convert to WAV 16k mono using pydub to keep consistent format
        wav_out = str(Path(out_mp3).with_suffix('.wav'))
        audio = AudioSegment.from_file(out_mp3)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_out, format='wav')
        return wav_out

    def synthesize(self, text, lang, out_base):
        if self.engine == 'gtts':
            out_mp3 = out_base + '.mp3'
            return self.synthesize_gtts(text, lang, out_mp3)
        else:
            raise NotImplementedError('Only gtts engine implemented in this starter. Replace with AI4Bharat or cloud TTS in production.')
