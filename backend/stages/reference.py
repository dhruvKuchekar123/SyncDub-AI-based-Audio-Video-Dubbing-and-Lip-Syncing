"""Voice-reference selection for cloning (emotion rung 1, Ch. 18 §18.3).

Instead of a blind fixed cut, score candidate windows inside detected speech
blocks and concatenate the best few: windows with a high voiced-frame ratio
(clean speech, not music/silence) and high energy variation (prosodically
representative delivery) give XTTS a reference that carries how the speaker
actually talks. Output is mono 24 kHz — XTTS v2's native rate.

The reference sample is the most sensitive artifact we hold (Ch. 5/12): it is
written only into the job's temp dir and deleted with the job.
"""
import os

# Scoring weights: clean speech matters more than prosodic variation, variation
# breaks ties. Values are heuristic; revisit only with a speaker-similarity
# measurement in hand (Ch. 16: no benchmark, no opinion).
VOICED_WEIGHT = 1.0
VARIATION_WEIGHT = 0.5

MIN_WINDOW_S = 3.0
MAX_CANDIDATES = 12  # pyin is slow; cap the scored windows


def candidate_windows(segments, window_s: float) -> "list[tuple[float, float]]":
    """Pure: carve (start, end) windows out of speech blocks, longest blocks
    first so the cap spends its budget where the speech is."""
    windows = []
    for seg in sorted(segments, key=lambda s: s.end - s.start, reverse=True):
        t = seg.start
        while t + MIN_WINDOW_S <= seg.end and len(windows) < MAX_CANDIDATES:
            windows.append((t, min(t + window_s, seg.end)))
            t += window_s
    return windows[:MAX_CANDIDATES]


def _score_window(y, sr) -> float:
    import librosa
    import numpy as np

    f0, voiced_flag, voiced_probs = librosa.pyin(
        y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr
    )
    voiced_ratio = float(np.mean(voiced_probs > 0.6))

    rms = librosa.feature.rms(y=y)[0]
    mean = float(np.mean(rms))
    variation = float(np.std(rms) / mean) if mean > 0 else 0.0

    return VOICED_WEIGHT * voiced_ratio + VARIATION_WEIGHT * min(variation, 1.0)


def select_reference(audio_path, segments, out_path, n_windows=2, window_s=8.0):
    """Best-scoring speech windows concatenated to out_path (24 kHz mono).

    Returns out_path, or None when selection is not possible — the caller
    falls back to the fixed cut."""
    try:
        import librosa
        import numpy as np
        import soundfile as sf

        windows = candidate_windows(segments, window_s)
        if not windows:
            return None

        y, sr = librosa.load(audio_path, sr=24000, mono=True)
        scored = []
        for start, end in windows:
            clip = y[int(start * sr):int(end * sr)]
            if len(clip) < MIN_WINDOW_S * sr:
                continue
            scored.append((_score_window(clip, sr), start, end))

        if not scored:
            return None
        scored.sort(reverse=True)

        gap = np.zeros(int(0.2 * sr), dtype=y.dtype)
        pieces = []
        for _, start, end in sorted(scored[:n_windows], key=lambda x: x[1]):
            if pieces:
                pieces.append(gap)
            pieces.append(y[int(start * sr):int(end * sr)])

        reference = np.concatenate(pieces)
        if len(reference) < MIN_WINDOW_S * sr:
            return None

        sf.write(out_path, reference, sr)
        print(f"[INFO] Reference selected: {len(scored[:n_windows])} window(s), "
              f"{len(reference) / sr:.1f}s total", flush=True)
        return out_path
    except Exception as e:
        print(f"[WARN] Reference selection failed ({e}); falling back to fixed cut.",
              flush=True)
        return None
