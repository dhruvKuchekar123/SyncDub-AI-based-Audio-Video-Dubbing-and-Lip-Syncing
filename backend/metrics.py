"""Per-job measurements (Founder OS Ch. 16: numbers over adjectives).

Written into jobs/{id}/metrics.json so every quality claim about a run has a
recorded basis: per-segment duration error and clamp counts for isochrony
(axis 4), and — when cloning ran — speaker-embedding similarity (axis 3).
Metric computation must never fail a job; everything here is best-effort.
"""
import json


def build_job_metrics(
    *,
    job_id: str,
    total_duration_s: float,
    segments: list,
    placements: list,
    synthesizer_used: str,
    fallback_reason: "str | None" = None,
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
        "speaker_similarity": None,  # filled by the cloning stage when it runs
        "per_segment": per_segment,
    }


def write_job_metrics(metrics_path, payload: dict) -> None:
    try:
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"[INFO] Metrics written: {metrics_path}", flush=True)
    except Exception as e:
        print(f"[WARN] Failed to write metrics: {e}", flush=True)
