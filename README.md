# Audio Analyzer

[![CI](https://github.com/sohailbhamani/audio-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/sohailbhamani/audio-analyzer/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A GPL-licensed CLI tool for audio analysis using Essentia and Librosa. Detects BPM, musical key (Camelot notation), energy level, and vocal presence.

## Features

- **BPM Detection**: Dual-engine analysis using both Essentia and Librosa for accuracy
- **Key Detection**: Multi-profile key analysis with voting consensus
  - Uses three Essentia profiles: `edma`, `bgate`, and `temperley`
  - Voting logic: if 2+ profiles agree, use consensus; otherwise use highest confidence
  - Results in Camelot notation (DJ-friendly)
- **Energy Analysis**: Percentile-based energy level (0-100)
- **Vocal Detection**: Spectral analysis to detect vocal presence

## Installation

```bash
# Clone the repository
git clone https://github.com/sohailbhamani/audio-analyzer.git
cd audio-analyzer

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev]"
```

## Usage

```bash
# Analyze an audio file
audio-analyzer analyze path/to/song.mp3
```

### Output

```json
{
  "bpm": 128.0,
  "key": "8A",
  "energy": 75,
  "has_vocals": true,
  "bpm_confidence": 0.85,
  "bpm_alt": 85.0,
  "bpm_alt_reason": "kept_kick_grid",
  "bpm_alt_confidence": 0.58,
  "key_confidence": 0.72
}
```

`bpm_alt` is the 3:2 alternative tempo that was rejected (the original estimate if the tempo was flipped),
`bpm_alt_reason` says why (`flipped_kick_grid`, `flipped_kick_grid_librosa`, `kept_kick_grid`,
`kept_insufficient_margin`), and `bpm_alt_confidence` is how far the chosen tempo beats it on the kick-band grid
(0–1). All three are `null` when no alternative falls in the 80–160 BPM range.

## Development

```bash
# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy src/
```

## Dependencies

- [Essentia](https://essentia.upf.edu/) - Audio analysis library
- [Librosa](https://librosa.org/) - Music and audio analysis
- [Click](https://click.palletsprojects.com/) - CLI framework

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
