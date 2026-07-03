"""Language registry: everything the pipeline needs to know per language.

Adding a language is a registry entry, not a code change. Fields encode the
task (which ASR code, which translation code, which stock voices, whether
cloning is possible), never model internals — per Founder OS Ch. 7 §7.1.

xtts_code is the language code handed to XTTS v2 for the cloning path.
XTTS v2 supports only: en es fr de it pt pl tr ru nl cs ar zh-cn hu ko ja hi.
A language outside that list either borrows a phonologically close supported
code (xtts_is_proxy=True — Marathi rides on Hindi: shared Devanagari script,
close phonology, quality caveat logged per run) or sets xtts_code=None,
which makes cloning unavailable for that language and forces stock voices.
"""
from dataclasses import dataclass, field


class UnsupportedLanguageError(ValueError):
    pass


@dataclass(frozen=True)
class LanguageSpec:
    code: str
    display_name: str
    whisper_code: str
    translator_code: str
    edge_voices: dict = field(default_factory=dict)  # {"male": ..., "female": ...}
    xtts_code: "str | None" = None
    xtts_is_proxy: bool = False


LANGUAGES = {
    "hi": LanguageSpec(
        code="hi",
        display_name="Hindi",
        whisper_code="hi",
        translator_code="hi",
        edge_voices={"male": "hi-IN-MadhurNeural", "female": "hi-IN-SwaraNeural"},
        xtts_code="hi",
    ),
    "mr": LanguageSpec(
        code="mr",
        display_name="Marathi",
        whisper_code="mr",
        translator_code="mr",
        edge_voices={"male": "mr-IN-ManoharNeural", "female": "mr-IN-AarohiNeural"},
        xtts_code="hi",  # XTTS v2 has no Marathi; Hindi proxy (see module docstring)
        xtts_is_proxy=True,
    ),
    "en": LanguageSpec(
        code="en",
        display_name="English",
        whisper_code="en",
        translator_code="en",
        edge_voices={"male": "en-IN-PrabhatNeural", "female": "en-IN-NeerjaNeural"},
        xtts_code="en",
    ),
}


def get_language(code: str) -> LanguageSpec:
    spec = LANGUAGES.get((code or "").strip().lower())
    if spec is None:
        supported = ", ".join(sorted(LANGUAGES))
        raise UnsupportedLanguageError(
            f"Unsupported language '{code}' (supported: {supported})"
        )
    return spec


def validate_pair(source: str, target: str) -> "tuple[LanguageSpec, LanguageSpec]":
    """Source==target is allowed: the translation stage is skipped, the job
    becomes re-voicing (and lip-sync re-timing) in the same language."""
    return get_language(source), get_language(target)


def registry_summary() -> list:
    """Shape served by GET /languages for frontend dropdowns."""
    return [
        {
            "code": spec.code,
            "display_name": spec.display_name,
            "cloning_available": spec.xtts_code is not None,
            "cloning_is_proxy": spec.xtts_is_proxy,
        }
        for spec in LANGUAGES.values()
    ]
