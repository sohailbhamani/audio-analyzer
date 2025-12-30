"""Error handling tests for audio-analyzer CLI."""

import json
import os
import subprocess
import sys

import numpy as np
import pytest
import soundfile as sf


def run_analyzer(file_path: str) -> subprocess.CompletedProcess:
    """Run the audio-analyzer CLI on the given file path."""
    cmd = [sys.executable, "-m", "audio_analyzer.main", "analyze", str(file_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


class TestInvalidInputs:
    """Test error handling for invalid inputs."""

    def test_nonexistent_file(self):
        """Verify graceful handling of nonexistent file."""
        result = run_analyzer("/nonexistent/path/to/audio.wav")
        assert result.returncode != 0, "Should fail for nonexistent file"

    def test_empty_file(self, temp_audio_path):
        """Verify graceful handling of empty file."""
        # Create an empty file
        with open(temp_audio_path, "w"):
            pass

        result = run_analyzer(temp_audio_path)
        assert result.returncode != 0, "Should fail for empty file"

    def test_corrupted_audio_file(self, temp_audio_path):
        """Verify graceful handling of corrupted audio file."""
        # Write random bytes that aren't valid audio
        with open(temp_audio_path, "wb") as f:
            f.write(os.urandom(1024))

        result = run_analyzer(temp_audio_path)
        assert result.returncode != 0, "Should fail for corrupted file"

    def test_text_file_as_audio(self, temp_audio_path):
        """Verify graceful handling of text file."""
        with open(temp_audio_path, "w") as f:
            f.write("This is not audio data, just plain text.\n" * 100)

        result = run_analyzer(temp_audio_path)
        assert result.returncode != 0, "Should fail for text file"


@pytest.mark.slow
class TestEdgeCases:
    """Test edge cases in audio analysis."""

    def test_very_short_audio(self, temp_audio_path):
        """Verify handling of very short audio (< 1 second)."""
        # Generate 0.5 seconds of audio
        sr = 44100
        duration = 0.5
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sr * duration)))
        audio = audio.astype(np.float32)
        sf.write(temp_audio_path, audio, sr)

        result = run_analyzer(temp_audio_path)
        # Should either succeed with limited accuracy or fail gracefully
        # Either is acceptable for very short audio
        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert "bpm" in data
            assert "key" in data

    def test_silent_audio(self, temp_audio_path):
        """Verify handling of silent audio."""
        sr = 44100
        duration = 5.0
        audio = np.zeros(int(sr * duration), dtype=np.float32)
        sf.write(temp_audio_path, audio, sr)

        result = run_analyzer(temp_audio_path)
        # Should handle gracefully - may return default values or fail
        # We just check it doesn't crash
        assert result.returncode in [0, 1]

    def test_very_loud_audio(self, temp_audio_path):
        """Verify handling of clipped/loud audio."""
        sr = 44100
        duration = 5.0
        t = np.linspace(0, duration, int(sr * duration))
        # Clipped sine wave (values outside -1 to 1)
        audio = np.sin(2 * np.pi * 440 * t) * 2.0  # Intentionally loud
        audio = np.clip(audio, -1.0, 1.0).astype(np.float32)
        sf.write(temp_audio_path, audio, sr)

        result = run_analyzer(temp_audio_path)
        assert result.returncode == 0, "Should handle loud audio"
        data = json.loads(result.stdout)
        assert "bpm" in data
        assert "key" in data

    def test_mono_audio(self, temp_audio_path):
        """Verify handling of mono audio."""
        sr = 44100
        duration = 5.0
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sr * duration)))
        audio = audio.astype(np.float32)
        sf.write(temp_audio_path, audio, sr)  # Default is mono

        result = run_analyzer(temp_audio_path)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "bpm" in data

    def test_stereo_audio(self, temp_audio_path):
        """Verify handling of stereo audio."""
        sr = 44100
        duration = 5.0
        t = np.linspace(0, duration, int(sr * duration))
        left = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        right = np.sin(2 * np.pi * 550 * t).astype(np.float32)
        stereo = np.column_stack([left, right])
        sf.write(temp_audio_path, stereo, sr)

        result = run_analyzer(temp_audio_path)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "bpm" in data


@pytest.mark.slow
class TestOutputFormat:
    """Test JSON output format and required fields."""

    def test_output_is_valid_json(self, generated_audio_file):
        """Verify output is valid JSON."""
        path = generated_audio_file(camelot="8B", bpm=120)

        result = run_analyzer(path)
        assert result.returncode == 0

        # Should not raise
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    def test_all_required_fields_present(self, generated_audio_file):
        """Verify all required fields are in output."""
        path = generated_audio_file(camelot="8B", bpm=120)

        result = run_analyzer(path)
        assert result.returncode == 0

        data = json.loads(result.stdout)
        required_fields = ["bpm", "key", "energy", "has_vocals", "bpm_confidence", "key_confidence"]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_field_types(self, generated_audio_file):
        """Verify field types are correct."""
        path = generated_audio_file(camelot="8B", bpm=120)

        result = run_analyzer(path)
        assert result.returncode == 0

        data = json.loads(result.stdout)

        assert isinstance(data["bpm"], (int, float))
        assert isinstance(data["key"], str)
        assert isinstance(data["energy"], int)
        assert isinstance(data["has_vocals"], bool)
        assert isinstance(data["bpm_confidence"], (int, float))
        assert isinstance(data["key_confidence"], (int, float))
