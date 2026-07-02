"""Layer 1 unit tests (Founder OS Ch. 10): pure pipeline logic, no models."""
import inference_marathi as im


# ---------------- group_segments ----------------

def seg(start, end, text):
    return {"start": start, "end": end, "text": text}


def test_group_segments_merges_contiguous_speech():
    segments = [seg(0.0, 2.0, "नमस्ते"), seg(2.5, 4.0, "कैसे हैं आप")]
    assert im.group_segments(segments) == ["नमस्ते कैसे हैं आप"]


def test_group_segments_splits_on_long_pause():
    segments = [seg(0.0, 2.0, "पहला वाक्य"), seg(4.0, 6.0, "दूसरा वाक्य")]
    assert im.group_segments(segments) == ["पहला वाक्य", "दूसरा वाक्य"]


def test_group_segments_respects_custom_threshold():
    segments = [seg(0.0, 2.0, "a"), seg(3.0, 4.0, "b")]
    assert im.group_segments(segments, gap_threshold=0.5) == ["a", "b"]
    assert im.group_segments(segments, gap_threshold=2.0) == ["a b"]


def test_group_segments_skips_empty_text():
    segments = [seg(0.0, 1.0, "  "), seg(1.2, 2.0, "बोलिए"), seg(2.1, 3.0, "")]
    assert im.group_segments(segments) == ["बोलिए"]


def test_group_segments_empty_input():
    assert im.group_segments([]) == []


# ---------------- detect_gender ----------------

def test_detect_gender_female_above_threshold(monkeypatch):
    monkeypatch.setattr(im, "get_median_pitch", lambda path: 200.0)
    assert im.detect_gender("any.wav") == "female"


def test_detect_gender_male_below_threshold(monkeypatch):
    monkeypatch.setattr(im, "get_median_pitch", lambda path: 120.0)
    assert im.detect_gender("any.wav") == "male"


def test_detect_gender_defaults_to_male_when_undetected(monkeypatch):
    monkeypatch.setattr(im, "get_median_pitch", lambda path: None)
    assert im.detect_gender("any.wav") == "male"


# ---------------- apply_ssml ----------------

def test_apply_ssml_produces_wrapped_prosody():
    out = im.apply_ssml("यह पहला वाक्य है। यह दूसरा है।", "mr-IN-ManoharNeural", "male")
    assert out.startswith("<speak")
    assert out.endswith("</speak>")
    assert out.count("<prosody") == 2
    assert "<break" in out


def test_apply_ssml_female_uses_faster_rate():
    male = im.apply_ssml("वाक्य।", "v", "male")
    female = im.apply_ssml("वाक्य।", "v", "female")
    assert 'rate="+0%"' in male
    assert 'rate="+5%"' in female
