# Third-party notices

## Beat This! (code and model weights)

audio-analyzer uses the Beat This! beat tracker for BPM, beat and downbeat detection:

- Code: the `beat-this` Python package, https://github.com/CPJKU/beat_this
- Model weights: the "small0" checkpoint, bundled unmodified as
  `src/audio_analyzer/models/beat_this-small0.ckpt`
  (SHA-256 `6074be2c4d490c5f6101fcc374a1ec72ae93456e23bb6019783b849f5dc7d47b`).
  It is never downloaded at runtime.

Paper: F. Foscarin, J. Schlüter and G. Widmer, "Beat This! Accurate Beat Tracking Without
DBN Postprocessing", ISMIR 2024.

The upstream project states that both the code and the published model weights are
released under the MIT license:

```
MIT License

Copyright (c) 2024 Institute of Computational Perception, JKU Linz, Austria

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Training-data caveat (from the upstream README):** "Note that some of the training
files are fully copyrighted or under limited Creative Commons licenses, and it is up to
the user to assess whether this may impact their use case."

The optional madmom DBN post-processing of Beat This! is not used: madmom's model files
are licensed for non-commercial use only.
