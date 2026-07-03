"""Synthesizer stage interface.

The interface encodes the task — turn translated, timed segments into
per-segment audio — never a model's shape (Founder OS Ch. 7 §7.1, Ch. 15
§15.1). Swapping engines must never touch code outside the adapter, and a
swap is justified by evaluation scores, not vibes.
"""
import abc
from dataclasses import dataclass

from stages.languages import LanguageSpec
from stages.types import Segment


class SynthesisError(RuntimeError):
    """Whole-job synthesis failure. The pipeline treats it as loud fallback
    to the stock-voice synthesizer — never a mid-video voice change."""


@dataclass
class SynthesisOptions:
    gender: str = "male"                 # stock-voice selection
    speaker_wav: "str | None" = None     # cloning reference sample
    map_emotion: bool = False            # engines with style controls may map Segment.emotion


class Synthesizer(abc.ABC):
    name: str = "abstract"

    @abc.abstractmethod
    def synthesize(
        self,
        segments: "list[Segment]",
        language: LanguageSpec,
        out_dir: str,
        options: SynthesisOptions,
    ) -> "list[Segment]":
        """Synthesize each segment to a wav under out_dir.

        Fills synth_path and synth_duration on every segment and returns the
        list. Raises SynthesisError if the engine cannot produce a complete,
        single-voice result.
        """
