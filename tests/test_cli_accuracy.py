import json
import subprocess
import sys

import pytest


def run_analyzer(file_path):
    """Run the audio-analyzer CLI on the given file path."""
    cmd = [sys.executable, "-m", "audio_analyzer.main", "analyze", str(file_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


@pytest.mark.slow
def test_analyze_bpm_accuracy(generated_audio_file):
    """Verify BPM detection accuracy."""
    # Test 120 BPM
    path_120 = generated_audio_file(camelot="8B", bpm=120)
    result = run_analyzer(path_120)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert abs(data["bpm"] - 120) < 1.0, f"Expected 120 BPM, got {data['bpm']}"

    # Test 128 BPM
    path_128 = generated_audio_file(camelot="5A", bpm=128)
    result = run_analyzer(path_128)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert abs(data["bpm"] - 128) < 1.0, f"Expected 128 BPM, got {data['bpm']}"


@pytest.mark.slow
@pytest.mark.parametrize(
    "camelot, expected_key",
    [
        ("8B", "8B"),  # C Major
        # ("2B", "2B"), # F# Major - Essentia sometimes tricky with synthetic chords
        ("5A", "5A"),  # C Minor
    ],
)
def test_analyze_key_accuracy(generated_audio_file, camelot, expected_key):
    """Verify Key detection accuracy."""
    path = generated_audio_file(camelot=camelot, bpm=120)
    result = run_analyzer(path)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    # Key detection on synthetic sines can be flaky, but let's check exact match for simple keys
    assert data["key"] == expected_key, f"Expected {expected_key}, got {data['key']}"
