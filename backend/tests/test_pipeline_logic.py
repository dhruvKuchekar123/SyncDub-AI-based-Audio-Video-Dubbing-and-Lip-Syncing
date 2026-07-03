"""Layer 1 unit tests (Founder OS Ch. 10): pure pipeline logic, no models."""
import pipeline as pl


# ---------------- group_segments ----------------

def seg(start, end, text):
    return {"start": start, "end": end, "text": text}


def texts(blocks):
    return [b.source_text for b in blocks]


def test_group_segments_merges_contiguous_speech():
    segments = [seg(0.0, 2.0, "नमस्ते"), seg(2.5, 4.0, "कैसे हैं आप")]
    blocks = pl.group_segments(segments)
    assert texts(blocks) == ["नमस्ते कैसे हैं आप"]
    assert blocks[0].start == 0.0
    assert blocks[0].end == 4.0
    assert blocks[0].target_duration == 4.0


def test_group_segments_splits_on_long_pause():
    segments = [seg(0.0, 2.0, "पहला वाक्य"), seg(4.0, 6.0, "दूसरा वाक्य")]
    blocks = pl.group_segments(segments)
    assert texts(blocks) == ["पहला वाक्य", "दूसरा वाक्य"]
    assert [(b.start, b.end) for b in blocks] == [(0.0, 2.0), (4.0, 6.0)]
    assert [b.idx for b in blocks] == [0, 1]


def test_group_segments_respects_custom_threshold():
    segments = [seg(0.0, 2.0, "a"), seg(3.0, 4.0, "b")]
    assert texts(pl.group_segments(segments, gap_threshold=0.5)) == ["a", "b"]
    assert texts(pl.group_segments(segments, gap_threshold=2.0)) == ["a b"]


def test_group_segments_skips_empty_text():
    segments = [seg(0.0, 1.0, "  "), seg(1.2, 2.0, "बोलिए"), seg(2.1, 3.0, "")]
    blocks = pl.group_segments(segments)
    assert texts(blocks) == ["बोलिए"]
    # block timing anchors on the first non-empty segment, not the empty one
    assert blocks[0].start == 1.2


def test_group_segments_empty_input():
    assert pl.group_segments([]) == []


def test_group_segments_defaults_schema_columns():
    blocks = pl.group_segments([seg(0.0, 1.0, "क्या हाल है?")])
    assert blocks[0].speaker_id == "spk0"
    assert blocks[0].emotion == "neutral"
    assert blocks[0].translated_text == ""


# ---------------- tag_emotions ----------------

def test_tag_emotions_from_punctuation():
    blocks = pl.group_segments([
        seg(0.0, 1.0, "क्या हाल है?"),
        seg(3.0, 4.0, "बहुत बढ़िया!"),
        seg(6.0, 7.0, "ठीक है।"),
    ])
    tagged = pl.tag_emotions(blocks)
    assert [b.emotion for b in tagged] == ["questioning", "emphatic", "neutral"]


# ---------------- emotion -> prosody mapping ----------------

def test_prosody_params_neutral_matches_legacy_gender_nudges():
    from stages.edge_tts_synth import prosody_params
    assert prosody_params("male", "neutral", map_emotion=True) == ("-2%", "+0Hz")
    assert prosody_params("female", "neutral", map_emotion=True) == ("+2%", "+0Hz")


def test_prosody_params_applies_documented_emotion_nudges():
    from stages.edge_tts_synth import prosody_params
    assert prosody_params("male", "questioning", map_emotion=True) == ("-2%", "+2Hz")
    assert prosody_params("male", "emphatic", map_emotion=True) == ("-5%", "+0Hz")


def test_prosody_params_ignores_emotion_when_mapping_off():
    from stages.edge_tts_synth import prosody_params
    assert prosody_params("male", "questioning", map_emotion=False) == ("-2%", "+0Hz")


# ---------------- translate_segments (same-language passthrough) ----------------

def test_translate_segments_same_language_passthrough():
    from stages.languages import get_language
    blocks = pl.group_segments([seg(0.0, 1.0, "नमस्ते")])
    out = pl.translate_segments(blocks, get_language("hi"), get_language("hi"))
    assert out[0].translated_text == "नमस्ते"


# ---------------- detect_gender ----------------

def test_detect_gender_female_above_threshold(monkeypatch):
    monkeypatch.setattr(pl, "get_median_pitch", lambda path: 200.0)
    assert pl.detect_gender("any.wav") == "female"


def test_detect_gender_male_below_threshold(monkeypatch):
    monkeypatch.setattr(pl, "get_median_pitch", lambda path: 120.0)
    assert pl.detect_gender("any.wav") == "male"


def test_detect_gender_defaults_to_male_when_undetected(monkeypatch):
    monkeypatch.setattr(pl, "get_median_pitch", lambda path: None)
    assert pl.detect_gender("any.wav") == "male"
