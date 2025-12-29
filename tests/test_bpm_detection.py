"""Parameterized BPM detection tests using drum patterns."""

import json
import subprocess
import sys

import pytest


def run_analyzer(file_path: str) -> subprocess.CompletedProcess:
    """Run the audio-analyzer CLI on the given file path."""
    cmd = [sys.executable, "-m", "audio_analyzer.main", "analyze", str(file_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


class TestBPMDetectionWithDrums:
    """Test BPM detection accuracy using synthetic drum patterns."""

    @pytest.mark.parametrize(
        "bpm",
        [
            90,  # Slow hip-hop / downtempo
            100,  # Hip-hop / R&B
            110,  # Pop / indie
            120,  # House / pop standard
            128,  # House / EDM standard
            140,  # Dubstep / drum & bass slow
            150,  # Drum & bass
        ],
    )
    def test_bpm_detection_four_on_floor(self, generated_drum_file, bpm):
        """Verify BPM detection with standard 4/4 drum pattern."""
        path = generated_drum_file(bpm=bpm, duration=15.0, pattern="four_on_floor")

        result = run_analyzer(path)
        assert result.returncode == 0, f"Analyzer failed: {result.stderr}"

        data = json.loads(result.stdout)
        detected_bpm = data["bpm"]

        # Allow 2 BPM tolerance or half/double (octave error)
        bpm_match = abs(detected_bpm - bpm) <= 2
        octave_match = abs(detected_bpm - bpm * 2) <= 2 or abs(detected_bpm - bpm / 2) <= 2

        assert bpm_match or octave_match, f"Expected ~{bpm} BPM, got {detected_bpm}"

    @pytest.mark.parametrize(
        "bpm, pattern",
        [
            (120, "four_on_floor"),
            (120, "breakbeat"),
            (90, "halftime"),
            (140, "four_on_floor"),
        ],
    )
    def test_bpm_detection_various_patterns(self, generated_drum_file, bpm, pattern):
        """Verify BPM detection with various drum patterns."""
        path = generated_drum_file(bpm=bpm, duration=15.0, pattern=pattern)

        result = run_analyzer(path)
        assert result.returncode == 0, f"Analyzer failed: {result.stderr}"

        data = json.loads(result.stdout)
        detected_bpm = data["bpm"]

        # More lenient for complex patterns (breakbeat, halftime)
        tolerance = 5 if pattern in ["breakbeat", "halftime"] else 2
        bpm_match = abs(detected_bpm - bpm) <= tolerance
        octave_match = abs(detected_bpm - bpm * 2) <= tolerance or abs(detected_bpm - bpm / 2) <= tolerance

        assert bpm_match or octave_match, f"Expected ~{bpm} BPM ({pattern}), got {detected_bpm}"

    def test_bpm_confidence_reasonable(self, generated_drum_file):
        """Verify BPM confidence is returned and reasonable."""
        path = generated_drum_file(bpm=120, duration=15.0, pattern="four_on_floor")

        result = run_analyzer(path)
        assert result.returncode == 0

        data = json.loads(result.stdout)
        assert "bpm_confidence" in data
        assert 0 <= data["bpm_confidence"] <= 1.0


class TestBPMWithClickTrack:
    """Test BPM detection using chord + click track (original method)."""

    @pytest.mark.parametrize(
        "bpm",
        [100, 120, 128, 140],
    )
    def test_bpm_with_chord_and_click(self, generated_audio_file, bpm):
        """Verify BPM detection with chord + click track."""
        path = generated_audio_file(camelot="8B", bpm=bpm, duration=10.0)

        result = run_analyzer(path)
        assert result.returncode == 0, f"Analyzer failed: {result.stderr}"

        data = json.loads(result.stdout)
        detected_bpm = data["bpm"]

        # Allow tolerance
        bpm_match = abs(detected_bpm - bpm) <= 2
        octave_match = abs(detected_bpm - bpm * 2) <= 2 or abs(detected_bpm - bpm / 2) <= 2

        assert bpm_match or octave_match, f"Expected ~{bpm} BPM, got {detected_bpm}"
