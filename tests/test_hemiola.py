"""Regression tests for 3:2 (hemiola) tempo errors in both directions, e.g. 126 BPM read as 84 and vice versa."""

import numpy as np
import pytest
import soundfile as sf
from conftest import SAMPLE_RATE, generate_hihat, generate_kick, generate_snare

import audio_analyzer.main as main
from audio_analyzer.main import analyze_audio, resolve_hemiola

DURATION = 30.0
CONTROL_BPMS = [90, 100, 120, 128, 140]


def _render(events: list[tuple[float, np.ndarray, float]]) -> np.ndarray:
    audio = np.zeros(int(SAMPLE_RATE * DURATION), dtype=np.float32)
    for t, sound, gain in events:
        start = int(t * SAMPLE_RATE)
        if start < len(audio):
            end = min(start + len(sound), len(audio))
            audio[start:end] += gain * sound[: end - start]
    return audio / (np.abs(audio).max() + 1e-3)


def _kick_with_accents(bpm: float, kick_gain: float, accent_gain: float, accent_beats: float) -> np.ndarray:
    """Kick on every beat plus a quieter snare accent every `accent_beats` beats."""
    np.random.seed(0)
    kick, snare = generate_kick(), generate_snare()
    beat = 60 / bpm
    events = [(i * beat, kick, kick_gain) for i in range(int(DURATION / beat) + 1)]
    events += [(i * accent_beats * beat, snare, accent_gain) for i in range(int(DURATION / beat / accent_beats) + 1)]
    return _render(events)


def _slow_with_cross_rhythm(bpm: float) -> np.ndarray:
    """Kick on every beat at `bpm`, over hats and snare accents on a pulse 1.5x faster (reads as bpm*1.5)."""
    np.random.seed(0)
    kick, snare, hat = generate_kick(), generate_snare(), generate_hihat()
    beat = 60 / bpm
    pulse = beat / 1.5
    events = [(i * beat, kick, 0.8) for i in range(int(DURATION / beat) + 1)]
    for i in range(int(DURATION / pulse) + 1):
        events.append((i * pulse, hat, 0.5))
        if i % 3 == 0:
            events.append((i * pulse, snare, 0.6))
    return _render(events)


def _four_on_floor(bpm: float) -> np.ndarray:
    np.random.seed(0)
    kick, snare, hat = generate_kick(), generate_snare(), generate_hihat()
    beat = 60 / bpm
    events = []
    for i in range(int(DURATION / beat) + 1):
        events.append((i * beat, kick, 0.8))
        events.append((i * beat + beat / 2, hat, 0.3))
        if i % 4 in (1, 3):
            events.append((i * beat, snare, 0.5))
    return _render(events)


def _analyze(tmp_path, audio: np.ndarray) -> dict:
    path = tmp_path / "synthetic.wav"
    sf.write(path, audio, SAMPLE_RATE)
    return analyze_audio(path)


# --- fast track misread as 2/3 speed ------------------------------------------------------------


def test_kick_on_every_beat_not_read_as_two_thirds(tmp_path):
    """126 BPM kick with dotted-quarter (1.5 beat) accents used to be read as 84."""
    assert _analyze(tmp_path, _kick_with_accents(126, 0.8, 0.3, 1.5))["bpm"] == pytest.approx(126, abs=2)


def test_resolve_hemiola_flips_slow_reading_up():
    audio = _kick_with_accents(126, 0.8, 0.3, 1.5)
    result = resolve_hemiola(audio, SAMPLE_RATE, 84.0)
    assert result["bpm"] == 126.0
    assert result["bpm_alt"] == 84.0
    assert result["bpm_alt_reason"].startswith("flipped_")
    assert 0.2 <= result["bpm_alt_confidence"] <= 1.0


# --- slow track misread as 1.5x speed -----------------------------------------------------------


@pytest.mark.parametrize("true_bpm", [84, 90])
def test_resolve_hemiola_flips_fast_reading_down(true_bpm):
    audio = _slow_with_cross_rhythm(true_bpm)
    result = resolve_hemiola(audio, SAMPLE_RATE, true_bpm * 1.5)
    assert result["bpm"] == true_bpm
    assert result["bpm_alt"] == true_bpm * 1.5
    assert result["bpm_alt_reason"].startswith("flipped_")


def test_slow_track_with_cross_rhythm_not_read_as_one_and_a_half_times(tmp_path):
    assert _analyze(tmp_path, _slow_with_cross_rhythm(84))["bpm"] == pytest.approx(84, abs=2)


# --- controls that must not change --------------------------------------------------------------


@pytest.mark.parametrize("bpm", [84, 126])
def test_resolve_hemiola_keeps_correct_tempo(bpm):
    audio = _kick_with_accents(bpm, 0.8, 0.3, 1.5)
    result = resolve_hemiola(audio, SAMPLE_RATE, float(bpm))
    assert result["bpm"] == bpm
    assert result["bpm_alt_reason"].startswith("kept_")


@pytest.mark.parametrize("bpm", CONTROL_BPMS)
def test_controls_unchanged_by_resolver(bpm):
    result = resolve_hemiola(_four_on_floor(bpm), SAMPLE_RATE, float(bpm))
    assert result["bpm"] == bpm
    assert result["bpm_alt_reason"] is None or result["bpm_alt_reason"].startswith("kept_")


@pytest.mark.parametrize("bpm", CONTROL_BPMS)
def test_no_regression_four_on_floor(tmp_path, bpm):
    assert _analyze(tmp_path, _four_on_floor(bpm))["bpm"] == pytest.approx(bpm, abs=2)


def test_librosa_alone_cannot_flip():
    """librosa reading the 3:2 tempo is not evidence when the kick grid clearly favours the current one."""
    audio = _slow_with_cross_rhythm(90)
    result = resolve_hemiola(audio, SAMPLE_RATE, 90.0, librosa_bpm=135.0)
    assert result["bpm"] == 90.0
    assert result["bpm_alt"] == 135.0
    assert result["bpm_alt_reason"] == "kept_kick_grid"


# --- decision logic with fixed kick-grid scores --------------------------------------------------


def _with_scores(monkeypatch, scores: dict[float, float]):
    monkeypatch.setattr(main, "_kick_grid_score", lambda y, sr, bpm: scores[round(bpm)])


def test_librosa_agreement_relaxes_margin_for_near_tie(monkeypatch):
    _with_scores(monkeypatch, {84: 0.25, 126: 0.42})
    audio = np.zeros(1, dtype=np.float32)

    kept = resolve_hemiola(audio, SAMPLE_RATE, 84.0)
    assert kept["bpm"] == 84.0
    assert kept["bpm_alt"] == 126.0
    assert kept["bpm_alt_reason"] == "kept_insufficient_margin"

    flipped = resolve_hemiola(audio, SAMPLE_RATE, 84.0, librosa_bpm=126.5)
    assert flipped["bpm"] == 126.0
    assert flipped["bpm_alt"] == 84.0
    assert flipped["bpm_alt_reason"] == "flipped_kick_grid_librosa"


def test_librosa_disagreeing_with_alternative_gives_no_relaxation(monkeypatch):
    _with_scores(monkeypatch, {84: 0.25, 126: 0.42})
    result = resolve_hemiola(np.zeros(1, dtype=np.float32), SAMPLE_RATE, 84.0, librosa_bpm=84.0)
    assert result["bpm"] == 84.0


def test_weak_alternative_cannot_win_a_weak_base(monkeypatch):
    """Ratio gate: 0.55 vs 0.40 clears the margin/score floors but is not a clear win."""
    _with_scores(monkeypatch, {84: 0.40, 126: 0.55})
    assert resolve_hemiola(np.zeros(1, dtype=np.float32), SAMPLE_RATE, 84.0)["bpm"] == 84.0


def test_no_alternative_in_range_reports_null_fields():
    # Neither 7.5 nor 3.3 BPM is inside the 80-160 search range, so nothing is scored.
    result = resolve_hemiola(np.zeros(1, dtype=np.float32), SAMPLE_RATE, 5.0)
    assert result == {"bpm": 5.0, "bpm_alt": None, "bpm_alt_reason": None, "bpm_alt_confidence": None}


# --- JSON output ---------------------------------------------------------------------------------


def test_output_keeps_existing_fields_and_adds_alt_fields(tmp_path):
    result = _analyze(tmp_path, _four_on_floor(128))
    for key in ("bpm", "key", "key_raw", "energy", "has_vocals", "bpm_confidence", "key_confidence", "key_profiles"):
        assert key in result
    for key in ("bpm_alt", "bpm_alt_reason", "bpm_alt_confidence"):
        assert key in result
    assert (result["bpm_alt"] is None) == (result["bpm_alt_reason"] is None)
