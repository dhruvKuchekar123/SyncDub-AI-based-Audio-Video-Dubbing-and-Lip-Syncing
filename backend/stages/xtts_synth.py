"""XTTS v2 cloning adapter, wrapping the clone_bridge subprocess.

The subprocess boundary is the sanctioned containment for XTTS's conflicting
dependencies (Founder OS Ch. 14 §14.1) — callers see only the Synthesizer
interface. XTTS v2 weights are CPML (non-commercial): demo/pilot only, see
docs/decisions/0001-xtts-v2-behind-synthesizer-interface.md.

A partial failure is a whole-job SynthesisError: the pipeline falls back to
stock voices for everything rather than mixing cloned and stock voices
mid-video. Voice consistency beats the wasted GPU time.
"""
import os
import subprocess

import config
from stages import assembly
from stages.languages import LanguageSpec
from stages.synthesizer import SynthesisError, SynthesisOptions, Synthesizer
from stages.types import Segment

BRIDGE_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "clone_bridge.py")


class XTTSCloneSynthesizer(Synthesizer):
    name = "xtts_clone"

    def synthesize(self, segments, language: LanguageSpec, out_dir, options: SynthesisOptions):
        if language.xtts_code is None:
            raise SynthesisError(
                f"Voice cloning is not available for {language.display_name}: "
                "XTTS v2 has no supported language code for it"
            )
        if not config.CLONE_PYTHON:
            raise SynthesisError(
                "Voice cloning requested but SYNCDUB_CLONE_PYTHON is not set "
                "(path to the XTTS environment's python; see .env.example)"
            )
        if not options.speaker_wav or not os.path.exists(options.speaker_wav):
            raise SynthesisError("Voice cloning requested without a reference sample")
        if language.xtts_is_proxy:
            print(
                f"[WARN] XTTS has no native {language.display_name}; synthesizing via "
                f"proxy language '{language.xtts_code}'. Quality caveat applies.",
                flush=True,
            )

        os.makedirs(out_dir, exist_ok=True)
        to_synth = [s for s in segments if s.translated_text.strip()]
        for seg in segments:
            if not seg.translated_text.strip():
                seg.synth_path = None
                seg.synth_duration = 0.0

        # One bridge process per segment reloads the model each time — known
        # cost, replaced by a batched manifest bridge in the next stage.
        for n, seg in enumerate(to_synth, 1):
            out_path = os.path.join(out_dir, f"seg_{seg.idx:04d}_clone.wav")
            print(f"[INFO] XTTS cloning segment {n}/{len(to_synth)}...", flush=True)
            cmd = [
                config.CLONE_PYTHON, BRIDGE_SCRIPT,
                "--text", seg.translated_text,
                "--speaker_wav", options.speaker_wav,
                "--out_path", out_path,
                "--language", language.xtts_code,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            if result.returncode != 0 or not os.path.exists(out_path):
                raise SynthesisError(
                    f"Cloning bridge failed on segment {seg.idx}: "
                    f"{(result.stderr or result.stdout or '').strip()[-400:]}"
                )
            seg.synth_path = out_path
            seg.synth_duration = assembly.measure_duration_s(out_path)
        return segments
