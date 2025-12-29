import json
import logging
import sys
from pathlib import Path

import click
import numpy as np

# Configure logging to stderr so stdout is clean for JSON
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(message)s")
logger = logging.getLogger("audio-analyzer")


def pitch_to_camelot(pitch_class: int, mode: int) -> str | None:
    """Convert pitch class (0-11) and mode (0=minor, 1=major) to Camelot notation."""
    # Pitch class 0=C, 1=C#, etc.
    # Mode 0=Minor, 1=Major

    # Camelot Wheel:
    # 8A=Am (pitch 9, mode 0) | 8B=C (pitch 0, mode 1)
    # 9A=Em (pitch 4, mode 0) | 9B=G (pitch 7, mode 1)
    # ...

    # Map (pitch, mode) -> Camelot
    # mode: 0 = Minor (A), 1 = Major (B)
    camelot_map = {
        # Minor Keys (A)
        (8, 0): "1A",  # G#m
        (3, 0): "2A",  # D#m
        (10, 0): "3A",  # A#m
        (5, 0): "4A",  # Fm
        (0, 0): "5A",  # Cm
        (7, 0): "6A",  # Gm
        (2, 0): "7A",  # Dm
        (9, 0): "8A",  # Am
        (4, 0): "9A",  # Em
        (11, 0): "10A",  # Bm
        (6, 0): "11A",  # F#m
        (1, 0): "12A",  # C#m
        # Major Keys (B)
        (11, 1): "1B",  # B
        (6, 1): "2B",  # F#
        (1, 1): "3B",  # C#
        (8, 1): "4B",  # G#
        (3, 1): "5B",  # D#
        (10, 1): "6B",  # A#
        (5, 1): "7B",  # F
        (0, 1): "8B",  # C
        (7, 1): "9B",  # G
        (2, 1): "10B",  # D
        (9, 1): "11B",  # A
        (4, 1): "12B",  # E
    }
    return camelot_map.get((pitch_class, mode))


@click.group()
def cli():
    """Audio Analyzer CLI - Detect BPM, Key, Energy, and Vocals."""
    pass


@cli.command()
@click.argument("audio_path", type=click.Path(exists=True, path_type=Path))
def analyze(audio_path: Path):
    """Analyze audio file and output JSON results."""
    try:
        # Suppress warnings
        import warnings

        import essentia.standard as es
        import librosa
        from scipy.fft import rfft, rfftfreq

        warnings.filterwarnings("ignore")

        # Load audio using librosa
        # Use 44.1kHz mono for consistent analysis
        sr = 44100
        y, _ = librosa.load(str(audio_path), sr=sr, mono=True)

        # Optimizations: Ensure float32 for Essentia
        y = y.astype(np.float32)

        # 1. BPM Detection ----------------------------------------------------
        # Librosa BPM (multi-segment for stability)
        segment_length = min(30 * sr, len(y) // 3)
        librosa_tempos = []

        for i in range(3):
            start = i * segment_length
            end = start + segment_length
            if end <= len(y):
                segment = y[start:end]
                # librosa's type hints can be tricky, cast return to float
                tempo = librosa.beat.beat_track(y=segment, sr=sr)[0]
                bpm = float(tempo)

                # Fix octave errors (normalize to 80-160 - typical DJ tempo range)
                while bpm < 80:
                    bpm = bpm * 2
                while bpm > 160:
                    bpm = bpm / 2
                librosa_tempos.append(bpm)

        librosa_bpm = round(np.median(librosa_tempos)) if librosa_tempos else 120

        # Essentia BPM (RhythmExtractor2013 - best for electronic)
        rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
        essentia_bpm, _, beats_confidence, _, _ = rhythm_extractor(y)
        essentia_bpm = float(essentia_bpm)

        # Apply octave correction to Essentia
        while essentia_bpm < 80:
            essentia_bpm = essentia_bpm * 2
        while essentia_bpm > 160:
            essentia_bpm = essentia_bpm / 2
        essentia_bpm = round(essentia_bpm)

        # Prefer Essentia
        final_bpm = float(essentia_bpm)
        bpm_confidence = min(1.0, float(beats_confidence) / 10.0)

        # 2. Key Detection ----------------------------------------------------
        key_extractor = es.KeyExtractor()
        key_name, scale, key_strength = key_extractor(y)

        key_map = {
            "C": 0,
            "C#": 1,
            "D": 2,
            "D#": 3,
            "E": 4,
            "F": 5,
            "F#": 6,
            "G": 7,
            "G#": 8,
            "A": 9,
            "A#": 10,
            "B": 11,
        }
        pitch = key_map.get(key_name, 0)
        mode = 1 if scale == "major" else 0
        final_key = pitch_to_camelot(pitch, mode) or "8A"
        key_confidence = float(key_strength)

        # 3. Energy Detection -------------------------------------------------
        try:
            energy_extractor = es.Energy()
            energy_values = []
            frame_size = 2048
            hop_size = 1024

            for i in range(0, len(y) - frame_size, hop_size):
                frame = y[i : i + frame_size]
                energy_values.append(energy_extractor(frame))

            if energy_values:
                # Percentile-based normalization
                p95 = np.percentile(energy_values, 95)
                p999 = np.percentile(energy_values, 99.9)
                raw_energy = min(1.0, p95 / (p999 + 0.001))
                final_energy = int(raw_energy * 100)
            else:
                final_energy = 50
        except Exception:
            final_energy = 50

        # 4. Vocals Detection -------------------------------------------------
        try:
            frame_size = 4096
            hop_size = 2048
            freqs = rfftfreq(frame_size, 1 / sr)

            vocal_low = 200
            vocal_high = 4000
            vocal_mask = (freqs >= vocal_low) & (freqs <= vocal_high)
            low_mask = freqs < vocal_low

            vocal_ratios = []

            for i in range(0, len(y) - frame_size, hop_size):
                frame = y[i : i + frame_size]
                spectrum = np.abs(rfft(frame))

                vocal_energy = np.sum(spectrum[vocal_mask] ** 2)
                total_energy = np.sum(spectrum**2)
                low_energy = np.sum(spectrum[low_mask] ** 2)

                if total_energy > 0:
                    non_bass_energy = total_energy - low_energy
                    if non_bass_energy > 0:
                        vocal_ratio = vocal_energy / non_bass_energy
                        if len(vocal_ratios) < 100:
                            vocal_ratios.append(vocal_ratio)

            if vocal_ratios:
                avg_vocal_ratio = sum(vocal_ratios) / len(vocal_ratios)
                has_vocals = avg_vocal_ratio > 0.70
            else:
                has_vocals = False

        except Exception:
            has_vocals = False

        # Output JSON
        result = {
            "bpm": final_bpm,
            "key": final_key,
            "energy": final_energy,
            "has_vocals": bool(has_vocals),
            "bpm_confidence": float(bpm_confidence),
            "key_confidence": float(key_confidence),
        }
        click.echo(json.dumps(result))

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        # Return generic error structure if possible, but simplest is exit code
        # However, protocol says non-zero exit code on failure
        sys.exit(1)


if __name__ == "__main__":
    cli()
