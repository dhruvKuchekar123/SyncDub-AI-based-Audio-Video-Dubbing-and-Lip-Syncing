import argparse
import os
import sys

# Ensure UTF-8 for Devanagari
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, required=True)
    parser.add_argument("--speaker_wav", type=str, required=True)
    parser.add_argument("--out_path", type=str, required=True)
    parser.add_argument("--language", type=str, default="mr")
    args = parser.parse_args()

    try:
        from TTS.api import TTS
        # Agreement for Coqui TTS
        os.environ["COQUI_TOS_AGREED"] = "1"
        
        print(f"[BRIDGE] Loading XTTS v2 in Python {sys.version.split()[0]}...")
        model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        
        import torch
        if torch.cuda.is_available():
            model.to("cuda")
            
        print(f"[BRIDGE] Synthesizing: {args.text[:30]}...")
        model.tts_to_file(
            text=args.text,
            speaker_wav=args.speaker_wav,
            language=args.language,
            file_path=args.out_path
        )
        print("[BRIDGE] SUCCESS")
    except Exception as e:
        print(f"[BRIDGE ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
