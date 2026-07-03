"""Unit tests for the language registry."""
import pytest

from stages.languages import (
    LANGUAGES,
    UnsupportedLanguageError,
    get_language,
    registry_summary,
    validate_pair,
)

# XTTS v2's fixed supported set — a registry entry must never point outside it.
XTTS_V2_LANGUAGES = {
    "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru",
    "nl", "cs", "ar", "zh-cn", "hu", "ko", "ja", "hi",
}


def test_registry_ships_wedge_languages():
    assert {"hi", "mr", "en"} <= set(LANGUAGES)


def test_every_entry_is_internally_consistent():
    for code, spec in LANGUAGES.items():
        assert spec.code == code
        assert spec.edge_voices.get("male") and spec.edge_voices.get("female")
        if spec.xtts_code is not None:
            assert spec.xtts_code in XTTS_V2_LANGUAGES
        # proxy flag must be set exactly when the xtts code differs
        assert spec.xtts_is_proxy == (
            spec.xtts_code is not None and spec.xtts_code != spec.code
        )


def test_marathi_clones_via_hindi_proxy():
    mr = get_language("mr")
    assert mr.xtts_code == "hi"
    assert mr.xtts_is_proxy is True


def test_get_language_normalizes_case_and_whitespace():
    assert get_language(" HI ").code == "hi"


def test_get_language_rejects_unknown():
    with pytest.raises(UnsupportedLanguageError, match="ta"):
        get_language("ta")
    with pytest.raises(UnsupportedLanguageError):
        get_language("")


def test_validate_pair_allows_same_language():
    src, tgt = validate_pair("hi", "hi")
    assert src.code == tgt.code == "hi"


def test_validate_pair_rejects_bad_member():
    with pytest.raises(UnsupportedLanguageError):
        validate_pair("hi", "xx")


def test_registry_summary_shape():
    summary = registry_summary()
    by_code = {e["code"]: e for e in summary}
    assert by_code["mr"]["cloning_available"] is True
    assert by_code["mr"]["cloning_is_proxy"] is True
    assert by_code["hi"]["cloning_is_proxy"] is False
    assert all("display_name" in e for e in summary)
