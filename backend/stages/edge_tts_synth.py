"""Edge-TTS adapter: stock neural voices, and the fallback for every job.

Edge-TTS is an unlicensed endpoint (Founder OS Ch. 15 §15.3) — demo-grade,
never presented as commercially shippable. It stays the default voice path
because cloning is opt-in with consent (Ch. 5 §5.2).
"""
import asyncio
import os
import time

from stages import assembly
from stages.languages import LanguageSpec
from stages.synthesizer import SynthesisError, SynthesisOptions, Synthesizer
from stages.types import Segment

# Emotion rung 2 (Ch. 18 §18.3): tiny, documented prosody nudges for engines
# with style controls. These re-express the speaker's own recorded delivery
# tag — they never infer feelings.
EMOTION_NUDGES = {
    "questioning": {"pitch_hz": +2, "rate_pct": 0},
    "emphatic": {"pitch_hz": 0, "rate_pct": -3},
}


def prosody_params(gender: str, emotion: str, map_emotion: bool) -> "tuple[str, str]":
    """(rate, pitch) strings for edge_tts.Communicate."""
    rate_pct = 2 if gender == "female" else -2
    pitch_hz = 0
    if map_emotion:
        nudge = EMOTION_NUDGES.get(emotion)
        if nudge:
            rate_pct += nudge["rate_pct"]
            pitch_hz += nudge["pitch_hz"]
    return f"{rate_pct:+d}%", f"{pitch_hz:+d}Hz"


class EdgeTTSSynthesizer(Synthesizer):
    name = "edge_tts"

    def __init__(self, retries: int = 3, retry_wait_s: float = 2.0):
        self.retries = retries
        self.retry_wait_s = retry_wait_s

    def _synth_one(self, text: str, voice: str, rate: str, pitch: str, out_path: str) -> None:
        import edge_tts

        last_error = None
        for attempt in range(self.retries):
            try:
                # a Communicate stream is single-use: build it per attempt
                communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(communicate.save(out_path))
                finally:
                    loop.close()
                if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                    return
                last_error = RuntimeError("Edge-TTS produced an empty file")
            except Exception as e:
                last_error = e
                print(f"[WARN] Edge-TTS attempt {attempt + 1} failed: {e}", flush=True)
            time.sleep(self.retry_wait_s)
        raise SynthesisError(f"Edge-TTS failed after {self.retries} attempts: {last_error}")

    def synthesize(self, segments, language: LanguageSpec, out_dir, options: SynthesisOptions):
        voice = language.edge_voices.get(options.gender) or language.edge_voices["male"]
        os.makedirs(out_dir, exist_ok=True)

        for seg in segments:
            if not seg.translated_text.strip():
                seg.synth_path = None
                seg.synth_duration = 0.0
                continue
            rate, pitch = prosody_params(options.gender, seg.emotion, options.map_emotion)
            out_path = os.path.join(out_dir, f"seg_{seg.idx:04d}_edge.wav")
            self._synth_one(seg.translated_text, voice, rate, pitch, out_path)
            seg.synth_path = out_path
            seg.synth_duration = assembly.measure_duration_s(out_path)
        return segments
