"""Regression tests for 3:2 (hemiola) tempo errors, e.g. 126 BPM read as 84."""

import numpy as np
import pytest
import soundfile as sf
from conftest import SAMPLE_RATE, generate_hihat, generate_kick, generate_snare

from audio_analyzer.main import analyze_audio, resolve_hemiola

DURATION = 30.0


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


def _detect(tmp_path, audio: np.ndarray) -> float:
    path = tmp_path / "synthetic.wav"
    sf.write(path, audio, SAMPLE_RATE)
    return analyze_audio(path)["bpm"]


def test_kick_on_every_beat_not_read_as_two_thirds(tmp_path):
    """126 BPM kick with dotted-quarter (1.5 beat) accents used to be read as 84."""
    assert _detect(tmp_path, _kick_with_accents(126, 0.8, 0.3, 1.5)) == pytest.approx(126, abs=2)


def test_resolve_hemiola_flips_when_kick_grid_favours_alternative():
    audio = _kick_with_accents(126, 0.8, 0.3, 1.5).astype(np.float32)
    assert resolve_hemiola(audio, SAMPLE_RATE, 84.0) == 126.0


@pytest.mark.parametrize("bpm", [84, 126])
def test_resolve_hemiola_keeps_correct_tempo(bpm):
    audio = _kick_with_accents(bpm, 0.8, 0.3, 1.5).astype(np.float32)
    assert resolve_hemiola(audio, SAMPLE_RATE, float(bpm)) == bpm


@pytest.mark.parametrize("bpm", [84, 120, 126, 128])
def test_no_regression_four_on_floor(tmp_path, bpm):
    assert _detect(tmp_path, _four_on_floor(bpm)) == pytest.approx(bpm, abs=2)
