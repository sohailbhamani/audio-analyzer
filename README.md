# audio-analyzer

Audio analysis CLI for BPM, key, energy, and vocals detection. Wraps [Essentia](https://essentia.upf.edu/).

## Features

- **BPM Detection** — Accurate tempo analysis
- **Key Detection** — Musical key identification
- **Energy Analysis** — Track intensity measurement
- **Vocals Detection** — Identify instrumental vs vocal tracks

## Installation

```bash
pip install audio-analyzer
```

## Usage

```bash
# Analyze a single file
audio-analyzer analyze track.mp3

# Output as JSON
audio-analyzer analyze track.mp3 --format json
```

## Requirements

- Python 3.9+
- Essentia

## License

GPL-3.0 — See [LICENSE](LICENSE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
