"""The segment schema — the pipeline's unit of work.

Schema outranks code (Founder OS Ch. 7 §7.5): fields are additive-only and
changes here get the most senior review of any change. speaker_id and emotion
are carried from v1 even though today's pipeline is single-speaker and the
emotion tag only reaches engines that accept style controls (Ch. 18 §18.1) —
adding them now is a cost of columns, not migrations.
"""
from dataclasses import asdict, dataclass


@dataclass
class Segment:
    idx: int
    start: float                     # seconds in the source video (block start)
    end: float                       # seconds in the source video (block end)
    source_text: str
    translated_text: str = ""
    speaker_id: str = "spk0"         # single-speaker wedge; diarization is future
    emotion: str = "neutral"         # recorded delivery tag, never inferred feelings (Ch. 18 §18.4)
    synth_path: "str | None" = None  # per-segment synthesized wav
    synth_duration: "float | None" = None  # seconds, at natural (1.0x) speed
    rate_applied: float = 1.0        # atempo factor actually applied

    @property
    def target_duration(self) -> float:
        return self.end - self.start

    def to_dict(self) -> dict:
        return asdict(self)
