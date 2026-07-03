"""Per-job measurements (Founder OS Ch. 16: numbers over adjectives).

Written into jobs/{id}/metrics.json so every quality claim about a run has a
recorded basis: per-segment duration error and clamp counts for isochrony
(axis 4), and — when cloning ran — speaker-embedding similarity (axis 3).
Metric computation must never fail a job; everything here is best-effort.
"""
import json


def compute_speaker_similarity(reference_wav: str, dubbed_wav: str) -> "float | None":
    """Cosine similarity between speaker embeddings of the cloning reference
    and the dubbed track (resemblyzer d-vectors, L2-normalized so the dot
    product is the cosine). The number that backs any 'sounds like the
    speaker' claim (Ch. 16 axis 3). Best-effort: None on any failure."""
    try:
        import numpy as np
        from resemblyzer import VoiceEncoder, preprocess_wav

        encoder = VoiceEncoder()
        ref_embed = encoder.embed_utterance(preprocess_wav(reference_wav))
        dub_embed = encoder.embed_utterance(preprocess_wav(dubbed_wav))
        return round(float(np.dot(ref_embed, dub_embed)), 4)
    except Exception as e:
        print(f"[WARN] Speaker-similarity metric unavailable: {e}", flush=True)
        return None


def build_job_metrics(
    *,
    job_id: str,
    total_duration_s: float,
    segments: list,
    placements: list,
    synthesizer_used: str,
    fallback_reason: "str | None" = None,
    speaker_similarity: "float | None" = None,
) -> dict:
    per_segment = []
    by_idx = {p.idx: p for p in placements}
    for seg in segments:
        p = by_idx.get(seg.idx)
        if p is None:
            continue
        target = round(seg.target_duration, 3)
        residual = round(p.expected_duration_s - target, 3)
        per_segment.append({
            "idx": seg.idx,
            "start": seg.start,
            "end": seg.end,
            "emotion": seg.emotion,
            "speaker_id": seg.speaker_id,
            "target_s": target,
            "synth_s": round(seg.synth_duration or 0.0, 3),
            "rate": p.rate,
            "clamped": p.clamped,
            "residual_error_s": residual,
            "overlap_ms": p.overlap_ms,
        })

    abs_errors = [abs(s["residual_error_s"]) for s in per_segment]
    return {
        "job_id": job_id,
        "total_duration_s": round(total_duration_s, 3),
        "synthesizer_used": synthesizer_used,
        "fallback_reason": fallback_reason,
        "isochrony": {
            "segments": len(per_segment),
            "clamp_count": sum(1 for s in per_segment if s["clamped"]),
            "mean_abs_error_s": round(sum(abs_errors) / len(abs_errors), 3) if abs_errors else 0.0,
            "max_abs_error_s": round(max(abs_errors), 3) if abs_errors else 0.0,
            "total_overlap_ms": sum(s["overlap_ms"] for s in per_segment),
        },
        "speaker_similarity": speaker_similarity,  # None unless cloning ran
        "per_segment": per_segment,
    }


def write_job_metrics(metrics_path, payload: dict) -> None:
    try:
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"[INFO] Metrics written: {metrics_path}", flush=True)
    except Exception as e:
        print(f"[WARN] Failed to write metrics: {e}", flush=True)
