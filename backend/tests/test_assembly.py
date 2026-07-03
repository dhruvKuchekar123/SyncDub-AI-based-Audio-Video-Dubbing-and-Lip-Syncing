"""Unit tests for the isochrony placement math (pure — no audio files)."""
from stages.assembly import RATE_MAX, RATE_MIN, plan_placement
from stages.types import Segment


def make_seg(idx, start, end, synth):
    return Segment(
        idx=idx, start=start, end=end,
        source_text="s", translated_text="t",
        synth_path=f"/tmp/seg_{idx}.wav", synth_duration=synth,
    )


def test_exact_fit_needs_no_rate_change():
    segs = [make_seg(0, 0.0, 4.0, synth=4.0)]
    [p] = plan_placement(segs, total_duration_s=10.0)
    assert p.rate == 1.0
    assert p.clamped is False
    assert p.offset_ms == 0
    assert p.overlap_ms == 0


def test_longer_synth_speeds_up_within_cap():
    # 4.4s of speech into a 4.0s slot -> rate 1.1 (within cap)
    segs = [make_seg(0, 0.0, 4.0, synth=4.4)]
    [p] = plan_placement(segs, total_duration_s=10.0)
    assert p.rate == 1.1
    assert p.clamped is False
    assert abs(p.expected_duration_s - 4.0) < 0.01


def test_much_longer_synth_clamps_high_and_reports_overlap():
    # 8s of speech into a 4s slot -> ideal 2.0, clamped to RATE_MAX
    segs = [
        make_seg(0, 0.0, 4.0, synth=8.0),
        make_seg(1, 5.0, 8.0, synth=3.0),
    ]
    p0, p1 = plan_placement(segs, total_duration_s=10.0)
    assert p0.rate == RATE_MAX
    assert p0.clamped is True
    # 8 / 1.15 = 6.956s from t=0 spills 1.956s past the next block at t=5
    assert p0.overlap_ms == 1957 or p0.overlap_ms == 1956
    assert p1.overlap_ms == 0


def test_much_shorter_synth_clamps_low():
    # 2s of speech into a 4s slot -> ideal 0.5, clamped to RATE_MIN
    segs = [make_seg(0, 0.0, 4.0, synth=2.0)]
    [p] = plan_placement(segs, total_duration_s=10.0)
    assert p.rate == RATE_MIN
    assert p.clamped is True
    assert p.overlap_ms == 0  # shorter than the slot never overlaps


def test_last_segment_overlap_measured_against_track_end():
    segs = [make_seg(0, 8.0, 9.0, synth=1.15 * 3.0)]  # even at max rate: 3s from t=8
    [p] = plan_placement(segs, total_duration_s=10.0)
    assert p.rate == RATE_MAX
    assert p.overlap_ms == 1000  # 8 + 3 = 11s on a 10s track


def test_offsets_anchor_to_original_block_starts():
    segs = [
        make_seg(0, 0.5, 2.0, synth=1.5),
        make_seg(1, 6.25, 8.0, synth=1.75),
    ]
    p0, p1 = plan_placement(segs, total_duration_s=10.0)
    assert p0.offset_ms == 500
    assert p1.offset_ms == 6250


def test_zero_or_missing_synth_duration_is_neutral():
    seg = make_seg(0, 0.0, 4.0, synth=None)
    seg.synth_duration = None
    [p] = plan_placement([seg], total_duration_s=10.0)
    assert p.rate == 1.0
    assert p.clamped is False


def test_empty_input():
    assert plan_placement([], total_duration_s=10.0) == []
