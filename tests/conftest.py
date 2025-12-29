import pytest
import numpy as np
import soundfile as sf
import tempfile
import os

SAMPLE_RATE = 44100

# Note frequencies (middle octave)
NOTES = {
    "C": 261.63,
    "C#": 277.18,
    "D": 293.66,
    "D#": 311.13,
    "E": 329.63,
    "F": 349.23,
    "F#": 369.99,
    "G": 392.00,
    "G#": 415.30,
    "A": 440.00,
    "A#": 466.16,
    "B": 493.88,
}

CAMELOT_TO_KEY = {
    "8B": ("C", "major"),
    "5A": ("C", "minor"),
    "3B": ("F#", "major"),
    "2B": ("F#", "major"),  # 3B is F# Major? Check circle.
    # Camelot Wheel:
    # 8B = C Major
    # 3B = F# Major (Bottom of wheel) - wait.
    # 1B=B, 2B=F#, 3B=Db(C#).
    # Let's check standards.
    # 1B (B), 2B (F#), 3B (Db/C#), 4B (Ab/G#), 5B (Eb/D#), 6B (Bb/A#), 7B (F), 8B (C), 9B (G), 10B (D), 11B (A), 12B (E)
    "8B": ("C", "major"),
    "2B": ("F#", "major"),
    "5A": ("C", "minor"),
}


def generate_tone(freq, duration, amp=0.5):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    return amp * np.sin(2 * np.pi * freq * t)


def generate_chord(root_name, scale_type, duration):
    root_freq = NOTES[root_name]
    if scale_type == "major":
        third_freq = root_freq * (2 ** (4 / 12))
    else:  # minor
        third_freq = root_freq * (2 ** (3 / 12))
    fifth_freq = root_freq * (2 ** (7 / 12))

    chord = (
        generate_tone(root_freq, duration, 0.3)
        + generate_tone(third_freq, duration, 0.3)
        + generate_tone(fifth_freq, duration, 0.3)
    )
    return chord


def add_click_track(audio, bpm):
    duration = len(audio) / SAMPLE_RATE
    bps = bpm / 60
    beat_interval = 1 / bps

    click_duration = 0.05
    click_freq = 1000
    click_t = np.linspace(
        0, click_duration, int(SAMPLE_RATE * click_duration), endpoint=False
    )
    click_wave = 0.8 * np.sin(2 * np.pi * click_freq * click_t) * np.exp(-10 * click_t)

    beats = np.arange(0, duration, beat_interval)
    for beat_time in beats:
        start_sample = int(beat_time * SAMPLE_RATE)
        end_sample = start_sample + len(click_wave)
        if end_sample < len(audio):
            audio[start_sample:end_sample] += click_wave
    return audio


@pytest.fixture
def generated_audio_file():
    """Factory fixture to generate audio file with specific params."""
    files_to_clean = []

    def _create(camelot, bpm, duration=5.0):
        if camelot not in CAMELOT_TO_KEY:
            # Default fallback or error
            root, scale = "C", "major"
        else:
            root, scale = CAMELOT_TO_KEY[camelot]

        audio = generate_chord(root, scale, duration)
        audio = add_click_track(audio, bpm)

        # Maximize volume
        audio = audio / np.max(np.abs(audio))

        fd, path = tempfile.mkstemp(suffix=f"_{camelot}_{bpm}bpm.wav")
        os.close(fd)

        sf.write(path, audio, SAMPLE_RATE)
        files_to_clean.append(path)
        return path

    yield _create

    for p in files_to_clean:
        if os.path.exists(p):
            os.remove(p)
