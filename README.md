# Audio Analyzer

[![CI](https://github.com/sohailbhamani/audio-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/sohailbhamani/audio-analyzer/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A GPL-licensed CLI tool for audio analysis using Essentia and Librosa. Detects BPM, musical key (Camelot notation), energy level, and vocal presence.

## Features

- **BPM Detection**: Dual-engine analysis using both Essentia and Librosa for accuracy
- **Key Detection**: Musical key in Camelot notation (DJ-friendly)
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
  "key_confidence": 0.72
}
```

## Development

```bash
# Run tests (Fast/Smoke suite)
# This is what runs in GitHub Actions CI
pytest -m "not slow"

# Run full test suite (Slow, includes synthetic audio generation)
# Run this locally before major releases
pytest -m "slow or not slow"

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
