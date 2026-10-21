import functools
import json
import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TypedDict, cast

import click
import numpy as np

# Configure logging to stderr so stdout is clean for JSON
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(message)s")
logger = logging.getLogger("audio-analyzer")


class KeyResult(TypedDict):
    """Structure for key extraction results."""

    key: str  # Camelot notation (e.g., "8B")
    key_raw: str  # Raw key (e.g., "C major")
    confidence: float
    profile: str | None


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


# Every common spelling of each pitch class. Essentia reports flats (Ab, Bb, Eb, ...).
NOTE_TO_PITCH = {
    "C": 0, "B#": 0,
    "C#": 1, "Db": 1,
    "D": 2,
    "D#": 3, "Eb": 3,
    "E": 4, "Fb": 4,
    "F": 5, "E#": 5,
    "F#": 6, "Gb": 6,
    "G": 7,
    "G#": 8, "Ab": 8,
    "A": 9,
    "A#": 10, "Bb": 10,
    "B": 11, "Cb": 11,
}  # fmt: skip


def key_to_camelot(key_name: str, scale: str) -> str:
    """Convert a key name (sharp or flat spelling) and scale ("major"/"minor") to Camelot.

    Raises ValueError for an unknown key name or scale instead of defaulting.
    """
    if key_name not in NOTE_TO_PITCH:
        raise ValueError(f"Unknown key name: {key_name!r}")
    if scale not in ("major", "minor"):
        raise ValueError(f"Unknown scale: {scale!r}")
    camelot = pitch_to_camelot(NOTE_TO_PITCH[key_name], 1 if scale == "major" else 0)
    if camelot is None:  # every pitch class 0-11 is mapped for both modes
        raise ValueError(f"No Camelot code for {key_name} {scale}")
    return camelot


MIN_BPM = 60.0
MAX_BPM = 200.0
# Tempo relatives of the detected tempo that are scored as candidates.
TEMPO_RELATIVES = (1.0, 2.0, 0.5, 1.5, 1 / 1.5)
MAX_TEMPO_CANDIDATES = 4

# Beat This! "small" checkpoint (MIT), bundled with the package so it is never downloaded.
BEAT_THIS_CHECKPOINT = Path(__file__).parent / "models" / "beat_this-small0.ckpt"
# Inter-beat intervals within this fraction of the median interval count as inliers.
BEAT_INLIER_TOLERANCE = 0.2
# Least-squares refinement passes of the beat period.
BEAT_PERIOD_REFINEMENTS = 3


def tempo_from_beats(beats: Sequence[float] | np.ndarray) -> tuple[float, float]:
    """Derive the tempo from beat times. Returns (bpm, confidence); (0.0, 0.0) for < 3 beats.

    A plain median of the inter-beat intervals is biased by the tracker's 20 ms frame grid
    (up to 4% at drum & bass tempos), so the period is estimated robustly instead: the mean
    of the inlier intervals (within BEAT_INLIER_TOLERANCE of the median), refined by a
    least-squares fit of beat time against beat index. The confidence is the share of
    intervals that are inliers, i.e. how regular the beat grid is.
    """
    b = np.asarray(beats, dtype=float)
    if len(b) < 3:
        return 0.0, 0.0
    intervals = np.diff(b)
    median = float(np.median(intervals))
    if median <= 0:
        return 0.0, 0.0
    inliers = np.abs(intervals - median) < BEAT_INLIER_TOLERANCE * median
    period = float(intervals[inliers].mean()) if inliers.any() else median
    for _ in range(BEAT_PERIOD_REFINEMENTS):
        index = np.round((b - b[0]) / period)
        period = float(np.polyfit(index, b, 1)[0])
    return 60.0 / period, float(inliers.mean())


@functools.cache
def _beat_tracker():
    """Load the bundled Beat This! small model once per process (CPU, no DBN post-processing)."""
    from beat_this.inference import Audio2Beats

    # beat_this treats a missing path as a checkpoint name and downloads it; never let it.
    if not BEAT_THIS_CHECKPOINT.is_file():
        raise FileNotFoundError(f"Bundled beat model missing: {BEAT_THIS_CHECKPOINT}")
    return Audio2Beats(checkpoint_path=str(BEAT_THIS_CHECKPOINT), device="cpu", dbn=False)


def detect_beats(y: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (beat_times, downbeat_times) in seconds for a mono signal."""
    beats, downbeats = _beat_tracker()(y, sr)
    return np.asarray(beats, dtype=float), np.asarray(downbeats, dtype=float)


def _beat_grid_score(env: np.ndarray, tempo: float, fps: float) -> tuple[float, float]:
    """Score how well a regular beat grid at ~`tempo` BPM explains an onset envelope.

    Searches phase and a +-3% tempo neighbourhood for the grid that captures the most
    onset strength. Returns (score, refined_tempo). The score is precision (mean strength
    on the grid) x coverage (share of total strength on the grid), so both a sparse grid
    that misses onsets and a dense grid that lands on silence are penalised.
    """
    n = len(env)
    total = float(env.sum())
    ref = float(np.percentile(env, 99)) if n else 0.0
    if n < 4 or total <= 0 or ref <= 0:
        return 0.0, tempo
    # Tolerate one frame of jitter around each grid point.
    padded = np.maximum(np.maximum(env, np.r_[env[1:], 0.0]), np.r_[0.0, env[:-1]])

    best_score, best_tempo = 0.0, tempo
    for candidate in tempo * np.linspace(0.97, 1.03, 25):
        period = fps * 60.0 / candidate
        for offset in np.arange(0.0, period, 0.5):
            hits = padded[np.round(np.arange(offset, n - 1, period)).astype(int)]
            score = min(float(hits.mean()) / ref, 1.0) * min(float(hits.sum()) / total, 1.0)
            if score > best_score:
                best_score, best_tempo = score, float(candidate)
    return best_score, best_tempo


def tempo_candidates(y: np.ndarray, sr: int, detected_bpm: float) -> list[dict[str, float]]:
    """Score the detected tempo and its x2, /2, x1.5 and /1.5 relatives within 60-200 BPM.

    Returns up to MAX_TEMPO_CANDIDATES {"bpm", "score"} entries, best score first.
    """
    import librosa

    if detected_bpm <= 0:
        return []
    hop_length = 512
    # Squared so strong hits (kick/snare) outweigh weak ones (hats) in the score.
    env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length) ** 2
    fps = sr / hop_length

    scored = []
    for ratio in TEMPO_RELATIVES:
        tempo = detected_bpm * ratio
        if MIN_BPM <= tempo <= MAX_BPM:
            score, refined = _beat_grid_score(env, tempo, fps)
            scored.append({"bpm": round(refined, 1), "score": round(score, 3)})
    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored[:MAX_TEMPO_CANDIDATES]


@click.group()
def cli():
    """Audio Analyzer CLI - Detect BPM, Key, Energy, and Vocals."""
    pass


@cli.command()
@click.argument("audio_path", type=click.Path(exists=True, path_type=Path))
def analyze(audio_path: Path):
    """Analyze audio file and output JSON results."""
    try:
        result = analyze_audio(audio_path)
        click.echo(json.dumps(result))
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)


def analyze_audio(audio_path: Path) -> dict:
    """Analyze audio file and return results dict."""
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
    # Beat This! tracks beats and downbeats; the tempo comes from the beat period.
    beats, downbeats = detect_beats(y, sr)
    detected_bpm, bpm_confidence = tempo_from_beats(beats)
    final_bpm = float(round(detected_bpm))
    bpm_candidates = tempo_candidates(y, sr, detected_bpm)

    # 2. Key Detection - Multi-profile Voting ------------------------------
    from collections import Counter

    profiles = ["edma", "bgate", "temperley"]
    key_results: list[KeyResult] = []

    if hasattr(es, "KeyExtractor"):
        # Standard Essentia builds might only support default or require specific config
        # We try multiple profileTypes. If profileType is not supported in the
        # installed python bindings (depends on version), we might need fallback.
        # However, standard KeyExtractor(profileType=...) is common.

        for profile in profiles:
            try:
                extractor = es.KeyExtractor(profileType=profile)
                key_name, scale, strength = extractor(y)

                camelot = key_to_camelot(key_name, scale)
                key_raw = f"{key_name} {scale}"

                key_results.append(
                    {
                        "profile": profile,
                        "key": camelot,
                        "key_raw": key_raw,
                        "confidence": float(strength),
                    }
                )
            except Exception as e:
                logger.warning(f"Key profile {profile} failed: {e}")

    # If no results (e.g. all failed), use default
    if not key_results:
        try:
            extractor = es.KeyExtractor()
            key_name, scale, strength = extractor(y)
            camelot = key_to_camelot(key_name, scale)
            key_raw = f"{key_name} {scale}"
            key_results.append(
                {
                    "key": camelot,
                    "key_raw": key_raw,
                    "confidence": float(strength),
                    "profile": None,
                }
            )
        except Exception as e:
            logger.warning(f"Key detection failed: {e}")
            key_results.append(
                {
                    "key": "8A",
                    "key_raw": "A minor",
                    "confidence": 0.0,
                    "profile": None,
                }
            )

    # Voting Logic
    # 1. Count occurrences
    counts = Counter(r["key"] for r in key_results)
    most_common = counts.most_common()  # [(key, count), ...]

    final_key = "8A"
    final_key_raw = "A minor"
    key_confidence = 0.0

    if most_common:
        # Cast for mypy since most_common can return Generic types
        top_key = cast(str, most_common[0][0])
        count = cast(int, most_common[0][1])

        # Case A: Majority (2 or 3 agree)
        if count >= 2:
            final_key = top_key
            # Avg confidence of matching results
            matches = [r for r in key_results if r["key"] == top_key]
            key_confidence = sum(float(r["confidence"]) for r in matches) / len(matches)
            # Use raw key from first matching profile
            final_key_raw = cast(str, matches[0]["key_raw"])

        # Case B: All differ (1, 1, 1) -> Take highest confidence
        else:
            best_result = max(key_results, key=lambda x: float(x["confidence"]))
            final_key = cast(str, best_result["key"])
            final_key_raw = cast(str, best_result["key_raw"])
            key_confidence = float(best_result["confidence"])

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

        vocal_ratios: list[float] = []

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
        "bpm_candidates": bpm_candidates,
        "key": final_key,
        "key_raw": final_key_raw,
        "energy": final_energy,
        "has_vocals": bool(has_vocals),
        "bpm_confidence": float(bpm_confidence),
        "key_confidence": float(key_confidence),
        "key_profiles": key_results,
        "beats": [round(float(t), 3) for t in beats],
        "downbeats": [round(float(t), 3) for t in downbeats],
    }
    return result


if __name__ == "__main__":
    cli()
# Trigger CI
