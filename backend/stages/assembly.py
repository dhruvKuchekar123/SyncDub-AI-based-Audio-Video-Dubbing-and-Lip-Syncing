"""Isochrony rungs 1–2 (Founder OS Ch. 17 §17.3): segment-anchored placement
plus capped rate adjustment.

Each translated segment is synthesized at natural speed, nudged toward its
original duration with ffmpeg atempo (capped so voices stay natural), and
overlaid at its original start time on a silent track exactly as long as the
source video. Drift is eliminated by construction; per-segment error is
bounded by the cap and logged, never hidden.

plan_placement is pure math so the timing logic stays unit-testable without
audio files.
"""
import os
import subprocess
from dataclasses import dataclass

import config
from stages.types import Segment

# Tighter than ffmpeg's atempo [0.5, 2.0] on purpose: beyond ~15% the voice
# audibly degrades, and rung 3 (length-aware translation) is the real fix for
# larger mismatches (Ch. 17 §17.4).
RATE_MIN = 0.85
RATE_MAX = 1.15

# atempo within 2% of unity is inaudible and not worth a re-encode.
RATE_SKIP_EPSILON = 0.02


@dataclass(frozen=True)
class Placement:
    idx: int
    offset_ms: int        # where the segment lands on the output track
    rate: float           # atempo factor (clamped)
    clamped: bool         # True when the ideal rate fell outside the cap
    expected_duration_s: float  # synth duration after rate adjustment
    overlap_ms: int       # spill into the next segment (or past track end)


def plan_placement(segments: "list[Segment]", total_duration_s: float) -> "list[Placement]":
    """Pure: compute per-segment atempo rates and placements.

    Segments must carry synth_duration (natural-speed length in seconds).
    """
    placements = []
    for i, seg in enumerate(segments):
        synth = seg.synth_duration or 0.0
        target = seg.target_duration

        if synth <= 0 or target <= 0:
            ideal = 1.0
        else:
            ideal = synth / target

        rate = max(RATE_MIN, min(RATE_MAX, ideal))
        clamped = rate != ideal
        expected = synth / rate if rate > 0 else synth

        offset_ms = int(round(seg.start * 1000))
        end_ms = offset_ms + int(round(expected * 1000))
        if i + 1 < len(segments):
            boundary_ms = int(round(segments[i + 1].start * 1000))
        else:
            boundary_ms = int(round(total_duration_s * 1000))
        overlap_ms = max(0, end_ms - boundary_ms)

        placements.append(Placement(
            idx=seg.idx,
            offset_ms=offset_ms,
            rate=round(rate, 4),
            clamped=clamped,
            expected_duration_s=round(expected, 3),
            overlap_ms=overlap_ms,
        ))
    return placements


def apply_rate(in_wav: str, rate: float, out_wav: str) -> str:
    """ffmpeg atempo; returns the path to use (input unchanged when skipped)."""
    if abs(rate - 1.0) < RATE_SKIP_EPSILON:
        return in_wav

    cmd = [
        config.FFMPEG, "-y",
        "-i", in_wav,
        "-filter:a", f"atempo={rate:.4f}",
        out_wav,
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0 or not os.path.exists(out_wav):
        raise RuntimeError(
            f"atempo failed for {in_wav}: {result.stderr.decode(errors='replace')[-400:]}"
        )
    return out_wav


def measure_duration_s(audio_path: str) -> float:
    from pydub import AudioSegment
    return len(AudioSegment.from_file(audio_path)) / 1000.0


def assemble_track(
    segments: "list[Segment]",
    placements: "list[Placement]",
    total_duration_s: float,
    out_path: str,
) -> str:
    """Overlay rate-adjusted segment audio onto silence of the source's exact
    length; export 16 kHz mono wav (what Wav2Lip consumes)."""
    from pydub import AudioSegment

    track = AudioSegment.silent(
        duration=int(round(total_duration_s * 1000)), frame_rate=16000
    )
    by_idx = {p.idx: p for p in placements}

    for seg in segments:
        if not seg.synth_path:
            continue
        placement = by_idx[seg.idx]
        clip = AudioSegment.from_file(seg.synth_path)
        # overlay truncates at track end — the residue past the source's
        # duration is already counted in the last placement's overlap_ms
        track = track.overlay(clip, position=placement.offset_ms)

    track = track.set_frame_rate(16000).set_channels(1)
    track.export(out_path, format="wav")
    return out_path
