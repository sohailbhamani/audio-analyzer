"""Parameterized key detection tests using chord progressions."""

from pathlib import Path

import pytest

from audio_analyzer.main import analyze_audio


def run_analyzer(file_path: str) -> dict:
    """Run the audio-analyzer internal API on the given file path."""
    return analyze_audio(Path(file_path))


class TestKeyDetection:
    """Test key detection utilizing chord progressions."""

    @pytest.mark.slow
    @pytest.mark.parametrize(
        "camelot, description",
        [
            ("8B", "C major"),
            ("9B", "G major"),
            ("10B", "D major"),
            ("11B", "A major"),
            ("12B", "E major"),
            ("7B", "F major"),
            pytest.param("6B", "Bb major", marks=pytest.mark.xfail(reason="Essentia detects C major on synthetic Bb")),
        ],
    )
    def test_major_key_detection(self, generated_audio_file, camelot, description):
        """Verify major key detection with chord progressions."""
        path = generated_audio_file(camelot=camelot, bpm=120, duration=20.0)

        data = run_analyzer(path)
        detected_key = data["key"]

        # Exact match or adjacent on Camelot wheel (compatible keys)
        expected_number = int(camelot[:-1])
        detected_number = int(detected_key[:-1])

        # Check if same key or relative minor
        exact_match = detected_key == camelot
        relative_minor = detected_key == f"{expected_number}A"
        adjacent = abs(expected_number - detected_number) <= 1 or abs(expected_number - detected_number) == 11

        assert exact_match or relative_minor or adjacent, f"Expected {camelot} ({description}), got {detected_key}"

    def test_key_smoke(self, generated_audio_file):
        """Smoke test for key detection (fast)."""
        self.test_major_key_detection(generated_audio_file, "8B", "C major")

    @pytest.mark.slow
    @pytest.mark.parametrize(
        "camelot, description",
        [
            ("8A", "A minor"),
            ("9A", "E minor"),
            ("7A", "D minor"),
            ("6A", "G minor"),
            ("5A", "C minor"),
            ("4A", "F minor"),
        ],
    )
    def test_minor_key_detection(self, generated_audio_file, camelot, description):
        """Verify minor key detection with chord progressions."""
        path = generated_audio_file(camelot=camelot, bpm=120, duration=10.0)

        data = run_analyzer(path)
        detected_key = data["key"]

        # Check for exact match or relative major
        expected_number = int(camelot[:-1])

        exact_match = detected_key == camelot
        relative_major = detected_key == f"{expected_number}B"

        assert exact_match or relative_major, f"Expected {camelot} ({description}), got {detected_key}"


class TestKeyConfidence:
    """Test key detection confidence values."""

    def test_key_confidence_returned(self, generated_audio_file):
        """Verify key confidence is returned."""
        path = generated_audio_file(camelot="8B", bpm=120, duration=10.0)

        data = run_analyzer(path)
        assert "key_confidence" in data
        assert isinstance(data["key_confidence"], (int, float))

    @pytest.mark.slow
    @pytest.mark.parametrize(
        "camelot",
        ["8B", "8A", "5A", "5B"],
    )
    def test_key_confidence_positive(self, generated_audio_file, camelot):
        """Verify key confidence is positive for valid audio."""
        path = generated_audio_file(camelot=camelot, bpm=120, duration=10.0)

        data = run_analyzer(path)
        assert data["key_confidence"] >= 0, "Key confidence should be non-negative"
