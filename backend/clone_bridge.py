"""XTTS v2 synthesis bridge — runs in the separate voiceclone environment.

Invoked by stages/xtts_synth.py as `SYNCDUB_CLONE_PYTHON clone_bridge.py
--manifest <path>`. The manifest carries a whole job's segments so the model
loads once per job, not once per segment:

    {"language": "hi", "speaker_wav": "...", "segments":
        [{"id": 0, "text": "...", "out_path": "..."}, ...]}

Per-segment outcomes go to <manifest>.results.json ({"segments": [{"id", "ok",
"error"}]}); the caller decides what a partial failure means (whole-job
fallback). A non-zero exit code means only manifest/model-load failure.

XTTS v2 weights are CPML (non-commercial) — see
docs/decisions/0001-xtts-v2-behind-synthesizer-interface.md.
"""
import argparse
import json
import os
import sys

# Ensure UTF-8 for Devanagari
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=str, required=True)
    args = parser.parse_args()

    try:
        with open(args.manifest, encoding="utf-8") as f:
            manifest = json.load(f)
        language = manifest["language"]
        speaker_wav = manifest["speaker_wav"]
        segments = manifest["segments"]
    except Exception as e:
        print(f"[BRIDGE ERROR] Bad manifest: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        from TTS.api import TTS
        # Agreement for Coqui TTS
        os.environ["COQUI_TOS_AGREED"] = "1"

        print(f"[BRIDGE] Loading XTTS v2 in Python {sys.version.split()[0]}...")
        model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

        import torch
        if torch.cuda.is_available():
            model.to("cuda")
    except Exception as e:
        print(f"[BRIDGE ERROR] Model load failed: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    for n, seg in enumerate(segments, 1):
        ok, error = False, None
        for attempt in (1, 2):  # one retry per segment
            try:
                print(f"[BRIDGE] Segment {n}/{len(segments)} (attempt {attempt}): "
                      f"{seg['text'][:30]}...")
                model.tts_to_file(
                    text=seg["text"],
                    speaker_wav=speaker_wav,
                    language=language,
                    file_path=seg["out_path"],
                )
                if os.path.exists(seg["out_path"]) and os.path.getsize(seg["out_path"]) > 0:
                    ok = True
                    break
                error = "empty output file"
            except Exception as e:
                error = str(e)
        results.append({"id": seg["id"], "ok": ok, "error": None if ok else error})

    results_path = args.manifest + ".results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({"segments": results}, f, ensure_ascii=False)

    failed = sum(1 for r in results if not r["ok"])
    print(f"[BRIDGE] Done: {len(results) - failed}/{len(results)} segments OK")


if __name__ == "__main__":
    main()
