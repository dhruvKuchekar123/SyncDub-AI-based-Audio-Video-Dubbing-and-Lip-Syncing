"""Unit tests for the XTTS manifest adapter (bridge subprocess mocked)."""
import json
import os

import pytest

import config
import stages.xtts_synth as xs
from stages.languages import get_language
from stages.synthesizer import SynthesisError, SynthesisOptions
from stages.types import Segment
from stages.xtts_synth import XTTSCloneSynthesizer, build_manifest_entries


def make_seg(idx, text, start=None, end=None):
    start = float(idx * 5) if start is None else start
    end = start + 4.0 if end is None else end
    return Segment(idx=idx, start=start, end=end, source_text="src",
                   translated_text=text)


# ---------------- build_manifest_entries ----------------

def test_entries_one_per_segment(tmp_path):
    segs = [make_seg(0, "पहला ब्लॉक यहाँ"), make_seg(1, "दूसरा ब्लॉक यहाँ")]
    entries = build_manifest_entries(segs, str(tmp_path))
    assert [e["id"] for e in entries] == [0, 1]
    assert entries[0]["out_path"].endswith("seg_0000_clone.wav")


def test_short_text_folds_into_previous(tmp_path):
    segs = [make_seg(0, "पहला ब्लॉक यहाँ"), make_seg(1, "हाँ"), make_seg(2, "तीसरा ब्लॉक")]
    entries = build_manifest_entries(segs, str(tmp_path))
    assert [e["id"] for e in entries] == [0, 2]
    assert entries[0]["text"] == "पहला ब्लॉक यहाँ हाँ"


def test_leading_short_text_prepends_to_next(tmp_path):
    segs = [make_seg(0, "जी"), make_seg(1, "अगला पूरा ब्लॉक")]
    entries = build_manifest_entries(segs, str(tmp_path))
    assert [e["id"] for e in entries] == [1]
    assert entries[0]["text"] == "जी अगला पूरा ब्लॉक"


def test_all_short_texts_still_produce_one_entry(tmp_path):
    segs = [make_seg(0, "जी"), make_seg(1, "हाँ")]
    entries = build_manifest_entries(segs, str(tmp_path))
    assert len(entries) == 1
    assert entries[0]["text"] == "जी हाँ"


def test_empty_texts_skipped(tmp_path):
    segs = [make_seg(0, "  "), make_seg(1, "असली पाठ यहाँ")]
    entries = build_manifest_entries(segs, str(tmp_path))
    assert [e["id"] for e in entries] == [1]


# ---------------- XTTSCloneSynthesizer ----------------

@pytest.fixture
def clone_env(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CLONE_PYTHON", "/fake/clone/python")
    ref = tmp_path / "reference_voice.wav"
    ref.write_bytes(b"fake-audio")
    monkeypatch.setattr(xs.assembly, "measure_duration_s", lambda p: 2.5)
    return tmp_path, str(ref)


def fake_bridge(returncode=0, results=None, create_outputs=True):
    """A subprocess.run stand-in that behaves like clone_bridge.py."""
    class R:
        pass

    def run(cmd, **kw):
        manifest_path = cmd[cmd.index("--manifest") + 1]
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        if returncode == 0:
            seg_results = results or [
                {"id": e["id"], "ok": True, "error": None} for e in manifest["segments"]
            ]
            ok_ids = {r["id"] for r in seg_results if r["ok"]}
            if create_outputs:
                for e in manifest["segments"]:
                    if e["id"] in ok_ids:
                        with open(e["out_path"], "wb") as f:
                            f.write(b"wav")
            with open(manifest_path + ".results.json", "w", encoding="utf-8") as f:
                json.dump({"segments": seg_results}, f)
        r = R()
        r.returncode = returncode
        r.stderr = "boom" if returncode else ""
        r.stdout = ""
        return r

    return run


def test_successful_batch_fills_segments(clone_env, monkeypatch):
    tmp_path, ref = clone_env
    monkeypatch.setattr(xs.subprocess, "run", fake_bridge())

    segs = [make_seg(0, "पहला ब्लॉक यहाँ"), make_seg(1, ""), make_seg(2, "तीसरा ब्लॉक")]
    out = XTTSCloneSynthesizer().synthesize(
        segs, get_language("mr"), str(tmp_path), SynthesisOptions(speaker_wav=ref)
    )
    assert out[0].synth_path.endswith("seg_0000_clone.wav")
    assert out[0].synth_duration == 2.5
    assert out[1].synth_path is None  # empty text -> silent slot
    assert out[2].synth_duration == 2.5

    manifest = json.loads((tmp_path / "xtts_manifest.json").read_text(encoding="utf-8"))
    assert manifest["language"] == "hi"  # Marathi rides the Hindi proxy
    assert manifest["speaker_wav"] == ref


def test_bridge_nonzero_exit_raises(clone_env, monkeypatch):
    tmp_path, ref = clone_env
    monkeypatch.setattr(xs.subprocess, "run", fake_bridge(returncode=1))
    with pytest.raises(SynthesisError, match="boom"):
        XTTSCloneSynthesizer().synthesize(
            [make_seg(0, "पूरा ब्लॉक")], get_language("mr"), str(tmp_path),
            SynthesisOptions(speaker_wav=ref),
        )


def test_partial_segment_failure_raises_whole_job(clone_env, monkeypatch):
    tmp_path, ref = clone_env
    results = [
        {"id": 0, "ok": True, "error": None},
        {"id": 1, "ok": False, "error": "CUDA OOM"},
    ]
    monkeypatch.setattr(xs.subprocess, "run", fake_bridge(results=results))
    with pytest.raises(SynthesisError, match="CUDA OOM"):
        XTTSCloneSynthesizer().synthesize(
            [make_seg(0, "पहला ब्लॉक यहाँ"), make_seg(1, "दूसरा ब्लॉक यहाँ")],
            get_language("mr"), str(tmp_path), SynthesisOptions(speaker_wav=ref),
        )


def test_missing_clone_env_raises(clone_env, monkeypatch):
    tmp_path, ref = clone_env
    monkeypatch.setattr(config, "CLONE_PYTHON", None)
    with pytest.raises(SynthesisError, match="SYNCDUB_CLONE_PYTHON"):
        XTTSCloneSynthesizer().synthesize(
            [make_seg(0, "पूरा ब्लॉक")], get_language("mr"), str(tmp_path),
            SynthesisOptions(speaker_wav=ref),
        )


def test_missing_reference_raises(clone_env):
    tmp_path, _ = clone_env
    with pytest.raises(SynthesisError, match="reference"):
        XTTSCloneSynthesizer().synthesize(
            [make_seg(0, "पूरा ब्लॉक")], get_language("mr"), str(tmp_path),
            SynthesisOptions(speaker_wav=None),
        )


# ---------------- reference window selection (pure part) ----------------

def test_candidate_windows_prefers_long_blocks():
    from stages.reference import candidate_windows
    segs = [
        make_seg(0, "छोटा", start=0.0, end=2.0),      # too short for a window
        make_seg(1, "लंबा ब्लॉक", start=10.0, end=30.0),
    ]
    windows = candidate_windows(segs, window_s=8.0)
    assert windows[0] == (10.0, 18.0)   # longest block first
    assert all(end - start >= 3.0 for start, end in windows)
    assert (0.0, 2.0) not in windows


def test_candidate_windows_caps_count():
    from stages.reference import MAX_CANDIDATES, candidate_windows
    segs = [make_seg(0, "x", start=0.0, end=500.0)]
    windows = candidate_windows(segs, window_s=8.0)
    assert len(windows) == MAX_CANDIDATES
