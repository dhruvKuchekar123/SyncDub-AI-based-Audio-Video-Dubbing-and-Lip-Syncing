"""XTTS v2 cloning adapter, wrapping the clone_bridge subprocess.

The subprocess boundary is the sanctioned containment for XTTS's conflicting
dependencies (Founder OS Ch. 14 §14.1) — callers see only the Synthesizer
interface. A whole job goes through one bridge invocation (JSON manifest, one
model load, N syntheses). XTTS v2 weights are CPML (non-commercial): demo and
pilot only, see docs/decisions/0001-xtts-v2-behind-synthesizer-interface.md.

A partial failure is a whole-job SynthesisError: the pipeline falls back to
stock voices for everything rather than mixing cloned and stock voices
mid-video. Voice consistency beats the wasted GPU time.
"""
import json
import os
import subprocess

import config
from stages import assembly
from stages.languages import LanguageSpec
from stages.synthesizer import SynthesisError, SynthesisOptions, Synthesizer

BRIDGE_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "clone_bridge.py"
)

# XTTS produces audible artifacts on very short inputs; text below this length
# is folded into a neighboring segment's synthesis instead.
MIN_CLONE_CHARS = 4


def build_manifest_entries(segments, out_dir: str) -> "list[dict]":
    """One manifest entry per synthesized clip, keyed by the anchor segment's
    idx. Too-short texts are folded into the previous entry (or prepended to
    the next when nothing precedes them); folded segments get no clip of
    their own and stay silent slots in assembly — their words are spoken as
    part of the anchor's clip, whose rate adjustment absorbs the extra length."""
    entries = []
    pending_short = None

    for seg in segments:
        text = seg.translated_text.strip()
        if not text:
            continue
        if len(text) < MIN_CLONE_CHARS:
            if entries:
                entries[-1]["text"] += " " + text
            else:
                pending_short = f"{pending_short} {text}" if pending_short else text
            print(f"[INFO] Segment {seg.idx} text too short for cloning; "
                  "folded into a neighbor.", flush=True)
            continue
        if pending_short:
            text = f"{pending_short} {text}"
            pending_short = None
        entries.append({
            "id": seg.idx,
            "text": text,
            "out_path": os.path.join(out_dir, f"seg_{seg.idx:04d}_clone.wav"),
        })

    if pending_short:
        if entries:
            entries[-1]["text"] += " " + pending_short
        else:
            first = next(s for s in segments if s.translated_text.strip())
            entries.append({
                "id": first.idx,
                "text": pending_short,
                "out_path": os.path.join(out_dir, f"seg_{first.idx:04d}_clone.wav"),
            })
    return entries


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
        entries = build_manifest_entries(segments, out_dir)
        if not entries:
            raise SynthesisError("No synthesizable text in any segment")

        manifest_path = os.path.join(out_dir, "xtts_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump({
                "language": language.xtts_code,
                "speaker_wav": options.speaker_wav,
                "segments": entries,
            }, f, ensure_ascii=False)

        print(f"[INFO] XTTS bridge: {len(entries)} segments, one model load...", flush=True)
        cmd = [config.CLONE_PYTHON, BRIDGE_SCRIPT, "--manifest", manifest_path]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            raise SynthesisError(
                "Cloning bridge failed: "
                f"{(result.stderr or result.stdout or '').strip()[-400:]}"
            )

        results_path = manifest_path + ".results.json"
        try:
            with open(results_path, encoding="utf-8") as f:
                seg_results = {r["id"]: r for r in json.load(f)["segments"]}
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            raise SynthesisError(f"Cloning bridge returned no readable results: {e}")

        failed = [r for r in seg_results.values() if not r["ok"]]
        if failed:
            raise SynthesisError(
                f"Cloning failed on {len(failed)} segment(s), e.g. "
                f"segment {failed[0]['id']}: {failed[0]['error']}"
            )

        by_id = {e["id"]: e for e in entries}
        for seg in segments:
            entry = by_id.get(seg.idx)
            if entry is None:
                # empty or folded-away segment: silent slot in assembly
                seg.synth_path = None
                seg.synth_duration = 0.0
                continue
            seg.synth_path = entry["out_path"]
            seg.synth_duration = assembly.measure_duration_s(entry["out_path"])
        return segments
