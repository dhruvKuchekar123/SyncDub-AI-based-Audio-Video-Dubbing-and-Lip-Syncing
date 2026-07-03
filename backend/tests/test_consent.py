"""Consent gate truth table (Founder OS Ch. 5 §5.2: consent before capability)."""
import pytest

from jobs import cloning_allowed


@pytest.mark.parametrize(
    "requested, consent, env, xtts_code, expect_granted, reason_contains",
    [
        # not requested: default stock voices, no reason to report
        (False, False, True, "hi", False, None),
        (False, True, True, "hi", False, None),
        # requested without speaker consent: never granted
        (True, False, True, "hi", False, "consent"),
        # requested with consent but no clone environment
        (True, True, False, "hi", False, "SYNCDUB_CLONE_PYTHON"),
        # requested with consent but language has no XTTS path
        (True, True, True, None, False, "not available"),
        # everything in place
        (True, True, True, "hi", True, None),
    ],
)
def test_cloning_allowed_truth_table(requested, consent, env, xtts_code,
                                     expect_granted, reason_contains):
    granted, reason = cloning_allowed(
        requested=requested,
        speaker_consent=consent,
        clone_env_configured=env,
        xtts_code=xtts_code,
    )
    assert granted is expect_granted
    if reason_contains is None:
        assert reason is None
    else:
        assert reason_contains in reason


def test_consent_outranks_environment():
    """Missing consent must be the reported reason even when the environment
    is also missing — the trust failure, not the config failure, is the story."""
    _, reason = cloning_allowed(
        requested=True, speaker_consent=False,
        clone_env_configured=False, xtts_code=None,
    )
    assert "consent" in reason
