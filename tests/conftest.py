"""Shared test fixtures for audio-analyzer tests."""

import os
import tempfile

import numpy as np
import pytest
import soundfile as sf

SAMPLE_RATE = 44100

# Note frequencies (middle octave - A4 = 440Hz standard)
NOTES = {
    "C": 261.63,
    "C#": 277.18,
    "Db": 277.18,
    "D": 293.66,
    "D#": 311.13,
    "Eb": 311.13,
    "E": 329.63,
    "F": 349.23,
    "F#": 369.99,
    "Gb": 369.99,
    "G": 392.00,
    "G#": 415.30,
    "Ab": 415.30,
    "A": 440.00,
    "A#": 466.16,
    "Bb": 466.16,
    "B": 493.88,
}

# Complete Camelot Wheel mapping
# Camelot Key (e.g., "8B") -> (root_note, scale_type)
CAMELOT_TO_KEY = {
    # Major Keys (B)
    "1B": ("B", "major"),
    "2B": ("F#", "major"),
    "3B": ("Db", "major"),
    "4B": ("Ab", "major"),
    "5B": ("Eb", "major"),
    "6B": ("Bb", "major"),
    "7B": ("F", "major"),
    "8B": ("C", "major"),
    "9B": ("G", "major"),
    "10B": ("D", "major"),
    "11B": ("A", "major"),
    "12B": ("E", "major"),
    # Minor Keys (A)
    "1A": ("Ab", "minor"),
    "2A": ("Eb", "minor"),
    "3A": ("Bb", "minor"),
    "4A": ("F", "minor"),
    "5A": ("C", "minor"),
    "6A": ("G", "minor"),
    "7A": ("D", "minor"),
    "8A": ("A", "minor"),
    "9A": ("E", "minor"),
    "10A": ("B", "minor"),
    "11A": ("F#", "minor"),
    "12A": ("Db", "minor"),
}


def generate_tone(freq: float, duration: float, sr: int = SAMPLE_RATE, amp: float = 0.5) -> np.ndarray:
    """Generate a pure sine wave tone."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return amp * np.sin(2 * np.pi * freq * t).astype(np.float32)


def generate_chord(root_name: str, scale_type: str, duration: float, octave_shift: int = 0) -> np.ndarray:
    """Generate a chord with root, third, and fifth.

    Args:
        root_name: Root note name (e.g., "C", "F#")
        scale_type: "major" or "minor"
        duration: Duration in seconds
        octave_shift: Shift octave up (+) or down (-)
    """
    root_freq = NOTES[root_name] * (2**octave_shift)

    # Major third = 4 semitones, Minor third = 3 semitones
    if scale_type == "major":
        third_freq = root_freq * (2 ** (4 / 12))
    else:  # minor
        third_freq = root_freq * (2 ** (3 / 12))

    fifth_freq = root_freq * (2 ** (7 / 12))  # Perfect fifth = 7 semitones

    # Generate each note with slight amplitude variations for realism
    chord = (
        generate_tone(root_freq, duration, amp=0.35)
        + generate_tone(third_freq, duration, amp=0.30)
        + generate_tone(fifth_freq, duration, amp=0.30)
    )
    return chord


def generate_chord_progression(root_name: str, scale_type: str, duration: float) -> np.ndarray:
    """Generate a chord progression to make key detection more robust.

    Uses I-IV-V-I progression for major and i-iv-v-i for minor.
    """
    root_freq = NOTES[root_name]
    chord_duration = duration / 4

    progression = []

    for i, interval in enumerate([0, 5, 7, 0]):  # I, IV, V, I (in semitones from root)
        # Shift the chord root
        shifted_freq = root_freq * (2 ** (interval / 12))

        if scale_type == "major":
            third_freq = shifted_freq * (2 ** (4 / 12))
        else:
            third_freq = shifted_freq * (2 ** (3 / 12))
        fifth_freq = shifted_freq * (2 ** (7 / 12))

        chord = (
            generate_tone(shifted_freq, chord_duration, amp=0.35)
            + generate_tone(third_freq, chord_duration, amp=0.30)
            + generate_tone(fifth_freq, chord_duration, amp=0.30)
        )
        progression.append(chord)

    return np.concatenate(progression)


def generate_kick(duration: float = 0.15) -> np.ndarray:
    """Generate a synthetic kick drum sound."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Kick: low frequency with pitch envelope (starts high, drops low)
    freq_start = 150
    freq_end = 50
    freq = freq_start * np.exp(-t * 20) + freq_end
    phase = np.cumsum(2 * np.pi * freq / SAMPLE_RATE)
    kick = np.sin(phase) * np.exp(-t * 15)
    return kick.astype(np.float32)


def generate_snare(duration: float = 0.1) -> np.ndarray:
    """Generate a synthetic snare drum sound."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Snare: mix of tone and noise
    tone = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 30)
    noise = np.random.uniform(-1, 1, len(t)) * np.exp(-t * 20)
    snare = 0.5 * tone + 0.5 * noise
    return snare.astype(np.float32)


def generate_hihat(duration: float = 0.05) -> np.ndarray:
    """Generate a synthetic hi-hat sound."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # Hi-hat: filtered noise with fast decay
    noise = np.random.uniform(-1, 1, len(t)) * np.exp(-t * 50)
    return noise.astype(np.float32)


def generate_drum_pattern(bpm: float, duration: float, pattern: str = "four_on_floor") -> np.ndarray:
    """Generate a drum pattern at the specified BPM.

    Args:
        bpm: Beats per minute
        duration: Total duration in seconds
        pattern: "four_on_floor", "breakbeat", "halftime"
    """
    beat_duration = 60.0 / bpm

    total_samples = int(SAMPLE_RATE * duration)
    audio = np.zeros(total_samples, dtype=np.float32)

    kick = generate_kick()
    snare = generate_snare()
    hihat = generate_hihat()

    def place_sound(audio, sound, time_sec):
        """Place a sound at the given time in the audio array."""
        start = int(time_sec * SAMPLE_RATE)
        end = min(start + len(sound), len(audio))
        if start < len(audio):
            audio[start:end] += sound[: end - start]

    if pattern == "four_on_floor":
        # Standard 4/4: kick on every beat, snare on 2 and 4, hihat on 8ths
        current_time = 0.0
        beat = 0
        while current_time < duration:
            # Kick on every beat
            place_sound(audio, kick * 0.8, current_time)

            # Snare on beats 2 and 4
            if beat % 4 in [1, 3]:
                place_sound(audio, snare * 0.6, current_time)

            # Hi-hat on every 8th note
            place_sound(audio, hihat * 0.3, current_time)
            place_sound(audio, hihat * 0.2, current_time + beat_duration / 2)

            current_time += beat_duration
            beat += 1

    elif pattern == "breakbeat":
        # Syncopated pattern with off-beat kicks
        current_time = 0.0
        while current_time < duration:
            # Kick pattern: 1, and-of-2, 3
            place_sound(audio, kick * 0.8, current_time)
            place_sound(audio, kick * 0.6, current_time + beat_duration * 1.5)
            place_sound(audio, kick * 0.8, current_time + beat_duration * 2)

            # Snare on 2 and 4
            place_sound(audio, snare * 0.6, current_time + beat_duration)
            place_sound(audio, snare * 0.6, current_time + beat_duration * 3)

            current_time += beat_duration * 4

    elif pattern == "halftime":
        # Snare only on beat 3 (half-time feel)
        current_time = 0.0
        while current_time < duration:
            place_sound(audio, kick * 0.8, current_time)
            place_sound(audio, snare * 0.6, current_time + beat_duration * 2)
            current_time += beat_duration * 4

    return audio


def add_click_track(audio: np.ndarray, bpm: float) -> np.ndarray:
    """Add a click track to existing audio for BPM detection."""
    duration = len(audio) / SAMPLE_RATE
    bps = bpm / 60
    beat_interval = 1 / bps

    click_duration = 0.05
    click_freq = 1000
    click_t = np.linspace(0, click_duration, int(SAMPLE_RATE * click_duration), endpoint=False)
    click_wave = 0.8 * np.sin(2 * np.pi * click_freq * click_t) * np.exp(-10 * click_t)
    click_wave = click_wave.astype(np.float32)

    beats = np.arange(0, duration, beat_interval)
    for beat_time in beats:
        start_sample = int(beat_time * SAMPLE_RATE)
        end_sample = start_sample + len(click_wave)
        if end_sample < len(audio):
            audio[start_sample:end_sample] += click_wave
    return audio


@pytest.fixture
def generated_audio_file():
    """Factory fixture to generate audio file with chord + click track."""
    files_to_clean = []

    def _create(camelot: str, bpm: float, duration: float = 8.0) -> str:
        if camelot not in CAMELOT_TO_KEY:
            root, scale = "C", "major"
        else:
            root, scale = CAMELOT_TO_KEY[camelot]

        # Use chord progression for better key detection
        audio = generate_chord_progression(root, scale, duration)
        audio = add_click_track(audio, bpm)

        # Normalize
        audio = audio / (np.max(np.abs(audio)) + 0.001)

        fd, path = tempfile.mkstemp(suffix=f"_{camelot}_{bpm}bpm.wav")
        os.close(fd)

        sf.write(path, audio, SAMPLE_RATE)
        files_to_clean.append(path)
        return path

    yield _create

    for p in files_to_clean:
        if os.path.exists(p):
            os.remove(p)


@pytest.fixture
def generated_drum_file():
    """Factory fixture to generate drum pattern audio for BPM testing."""
    files_to_clean = []

    def _create(bpm: float, duration: float = 10.0, pattern: str = "four_on_floor") -> str:
        audio = generate_drum_pattern(bpm, duration, pattern)

        # Normalize
        audio = audio / (np.max(np.abs(audio)) + 0.001)

        fd, path = tempfile.mkstemp(suffix=f"_drums_{bpm}bpm_{pattern}.wav")
        os.close(fd)

        sf.write(path, audio, SAMPLE_RATE)
        files_to_clean.append(path)
        return path

    yield _create

    for p in files_to_clean:
        if os.path.exists(p):
            os.remove(p)


@pytest.fixture
def temp_audio_path():
    """Create a temporary file path for test audio."""
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)
