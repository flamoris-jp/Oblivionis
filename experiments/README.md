# Oblivionis experiments

Experiments are first-class contents of this repository. Keep useful attempts,
failures, parameters, small measurements and reproducible scripts here as the
model evolves. Do not move them out merely because other FLAMORIS product
repositories separate disposable experiments.

These are **historical research probes**, not a production music model, stable
core API, Profundumis implementation, or proof of semantic understanding.

## Layout and provenance

| Directory | Source / purpose |
|---|---|
| `early/` | Five particle, wave, interference and peak-search prototypes from `oblivionis.zip`. |
| `music_baseline/` | Five scripts from `oblivionis_music.zip`. |
| `music_improv/` | Seven scripts from `oblivionis_music 2.zip`; keep this distinct from the baseline. |
| `results/imported/` | Four supplied JSON results, reformatted only; all rows and values retained. |
| `tests/` | Bounded import/regression checks, not future core acceptance tests. |
| `outputs/` | Ignored regenerated files; never overwrite reviewed reference results. |

[provenance.json](provenance.json) records archive names, original members and
original/imported SHA-256 values. Executable prototype logic is preserved.
Two non-executable normalizations are explicitly recorded: a final newline in
`early/v00.py` and expanded wording of one baseline parameter comment.

[NOTES.md](NOTES.md) is a public summary of research observations and limitations,
not a verbatim upload of private conversations. The standalone v0.5 memory-field
source mentioned by the historical notes was not present in these archives;
we have not reconstructed or claimed to import it.

## Reproduce the regression checks

From the repository root, use a Python 3.13 virtual environment of your choice:

```bash
python -m pip install -r experiments/requirements-test.txt
python -m unittest discover -s experiments/tests -v
```

The test dependency versions are the observed verification environment, not a
permanent production toolchain decision. Six tests check all 17 source files,
old/new equality on every one of 4,000 steps, seed-2 metrics for `memory` and
`improv`, invariants of the randomized control, consistency of the imported
six-seed summary, and a bounded extended-model smoke run.

A summary consistency check **does not rerun all six seeds**. Floating metrics
use `1e-12` absolute/relative tolerance; old/new state comparison is exact within
the same process. Different numerical environments may require separate review,
not silently regenerated expected results. See [import_verification.json](results/import_verification.json).

## Run historical scripts without polluting the source tree

```bash
python experiments/run.py early v00.py
python experiments/run.py music_baseline seeds.py
python experiments/run.py music_improv improv.py
```

The wrapper uses an allowlisted script, the current Python interpreter and an
ignored `experiments/outputs/<suite>/` working directory. Runs in the same suite
overwrite their generated output names; preserve a reviewed result explicitly
under a new record before rerunning. No shell invocation is used.

For optional visualization and synthesis dependencies:

```bash
python -m pip install -r experiments/requirements-visual.txt
python experiments/run.py early oblivionis_v01_visual.py
python experiments/run.py early oblivionis_v02_wave_visual.py
python experiments/run.py early oblivionis_v04_peak_search.py
python experiments/run.py music_baseline session.py
python experiments/run.py music_baseline plot_session.py
python experiments/run.py music_improv render_improv.py
```

`plot_session.py` needs the `notes.json`, `trace.npz` and metrics produced by
`session.py` in the same suite output directory. `oblivionis_v03_interference.py`
defines a model but has no standalone demo entry point. The plot scripts expect
a locally installed Japanese font; missing glyphs do not establish a numerical
failure. Font files are not bundled. Visual dependencies are optional and are
not pinned by the numerical regression environment.

Historical scripts are not hardened libraries. Some execute on import, and
`session.py` uses default global BPM/dt in scheduling even when custom parameters
are passed. Keep baseline reproduction at default BPM/dt; a generalized runner
requires a separately reviewed change. Early visualizers may not handle all
empty-particle plotting cases. Rendering/MIDI/audio validation is not part of
the current numerical test suite.

## What belongs in Git

Commit research code, seeds, parameters, small JSON/CSV summaries, reviewed
small figures, and notes including negative results. Record source commit,
environment, command, selection policy and limitations for new experiments.
Keep substantial WAV/MP3/GIF/video, raw large arrays, model weights, private
conversation logs, credentials and host-specific deployment information out of
normal source commits. A deliberately reviewed small demonstration asset may
be added later with its provenance and license. These imports contain code and
numeric records only; large supplied media are not committed.

Keep current results separate from [future Max/recall requirements](../docs/MAX_RECALL.md).
All imported code is project-supplied Oblivionis research code under the root
Apache-2.0 code license. External dependencies retain their own licenses; no
third-party recordings, weights, datasets or fonts are included.
