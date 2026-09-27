# Experimental work

Read the root AGENTS.md, this directory's README.md and NOTES.md, and
`docs/PHASE_A_PLAN.md` / `docs/MAX_RECALL.md` before modifying experiments.

Experiments are first-class repository contents. Preserve useful failures and
controls, not only successful demonstrations. Keep historical suites separate
from the domain-neutral reference model. Do not turn a source-integrity test
failure into permission to silently overwrite a baseline or its expected data.
Add a new experimental version or make a documented, reviewed baseline fix;
record original/current hashes, parameters, seeds and limitations.

Do not claim that returning voices implement Profundumis, or that changing a
Max ratio guarantees a proportionate final response. Max ratios specify the
initial recalled activation; integration into the present is a separate rule.

Run `python -m unittest discover -s experiments/tests -v` after changes.
Long batches and rendering are explicit experiment runs, not necessary on every
PR. Generated output belongs in `outputs/` until deliberately reviewed.
