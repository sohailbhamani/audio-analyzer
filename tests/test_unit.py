"""Unit tests for audio_analyzer internal functions."""

import pytest

from audio_analyzer.main import pitch_to_camelot


class TestPitchToCamelot:
    """Test the pitch_to_camelot function with all valid inputs."""

    # Complete mapping of (pitch_class, mode) -> expected camelot
    @pytest.mark.parametrize(
        "pitch_class, mode, expected",
        [
            # Minor Keys (A) - mode=0
            (8, 0, "1A"),  # G#m / Abm
            (3, 0, "2A"),  # D#m / Ebm
            (10, 0, "3A"),  # A#m / Bbm
            (5, 0, "4A"),  # Fm
            (0, 0, "5A"),  # Cm
            (7, 0, "6A"),  # Gm
            (2, 0, "7A"),  # Dm
            (9, 0, "8A"),  # Am
            (4, 0, "9A"),  # Em
            (11, 0, "10A"),  # Bm
            (6, 0, "11A"),  # F#m
            (1, 0, "12A"),  # C#m / Dbm
            # Major Keys (B) - mode=1
            (11, 1, "1B"),  # B
            (6, 1, "2B"),  # F#
            (1, 1, "3B"),  # C# / Db
            (8, 1, "4B"),  # G# / Ab
            (3, 1, "5B"),  # D# / Eb
            (10, 1, "6B"),  # A# / Bb
            (5, 1, "7B"),  # F
            (0, 1, "8B"),  # C
            (7, 1, "9B"),  # G
            (2, 1, "10B"),  # D
            (9, 1, "11B"),  # A
            (4, 1, "12B"),  # E
        ],
    )
    def test_all_valid_camelot_mappings(self, pitch_class, mode, expected):
        """Verify all 24 valid Camelot mappings."""
        result = pitch_to_camelot(pitch_class, mode)
        assert result == expected, f"Expected {expected} for pitch={pitch_class}, mode={mode}"

    @pytest.mark.parametrize(
        "pitch_class, mode",
        [
            (-1, 0),  # Invalid pitch (negative)
            (12, 0),  # Invalid pitch (too high)
            (0, 2),  # Invalid mode
            (0, -1),  # Invalid mode (negative)
            (100, 1),  # Way out of range
        ],
    )
    def test_invalid_inputs_return_none(self, pitch_class, mode):
        """Verify invalid inputs return None."""
        result = pitch_to_camelot(pitch_class, mode)
        assert result is None, f"Expected None for pitch={pitch_class}, mode={mode}"

    def test_camelot_wheel_relationships(self):
        """Verify Camelot wheel relationships (relative major/minor)."""
        # Each minor key (A) is the relative minor of the major key with same number
        # e.g., 8A (Am) is relative minor of 8B (C major)

        # Am (pitch=9, mode=0) -> 8A
        assert pitch_to_camelot(9, 0) == "8A"
        # C major (pitch=0, mode=1) -> 8B
        assert pitch_to_camelot(0, 1) == "8B"

        # Em (pitch=4, mode=0) -> 9A
        assert pitch_to_camelot(4, 0) == "9A"
        # G major (pitch=7, mode=1) -> 9B
        assert pitch_to_camelot(7, 1) == "9B"


class TestCamelotMappingConsistency:
    """Verify Camelot mapping consistency and coverage."""

    def test_all_24_keys_covered(self):
        """Ensure all 24 Camelot keys are mapped exactly once."""
        results = []
        for pitch in range(12):
            for mode in range(2):
                result = pitch_to_camelot(pitch, mode)
                if result is not None:
                    results.append(result)

        assert len(results) == 24, f"Expected 24 mappings, got {len(results)}"
        assert len(set(results)) == 24, "Duplicate Camelot keys found"

    def test_all_camelot_values_valid_format(self):
        """Verify all returned values match Camelot format (1-12 + A/B)."""
        import re

        pattern = r"^(1[0-2]|[1-9])[AB]$"

        for pitch in range(12):
            for mode in range(2):
                result = pitch_to_camelot(pitch, mode)
                if result is not None:
                    assert re.match(pattern, result), f"Invalid format: {result}"
