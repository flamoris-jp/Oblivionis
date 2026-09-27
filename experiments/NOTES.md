# Research notes and limits

This is an edited summary of the project-supplied early design logs,
`Oblivionis_music_LOG.md` and `Oblivionis_improv_LOG.md`. It records their research
framing without treating speculative anthropomorphic language as measured fact.
Consult [provenance](provenance.json) and [the plan](../docs/PHASE_A_PLAN.md).

## Early particles and waves

The supplied v0.0-v0.4 scripts progress from strength decay and distance changes
to oscillatory strength, pairwise interference and input-dependent thresholded
peaks. Their `Core`, `existence`, `retain` and `fade` names are historical probe
terms, not an agent identity or evidence of consciousness. Inactive particles
are removed by these historical scripts. That is not the future
active/fading/latent/evicted distinction, and there is no Profundumis store here.

## Music baseline

Twenty voices use a fixed integer-harmonic mapping for both timing and pitch.
The code exposes phase, activation `A`, persistence `S` and coupling `K`.
A 40-bar default session presents a straight pattern for 12 bars, a triplet
pattern for 12, then no input for 16. These domain choices belong to the probe.

The supplied log reports failed settings that made all voices remain active,
and settings that went silent almost immediately after input stopped. It also
records a trial of a non-audible core oscillator: remembering the triplet pattern
was more reliable in that trial, but timing offsets were worse. The supplied
baseline defaults therefore leave `core_gain=0`. The failed parameter trials
were not rerun during this import; not all original trial configurations exist
as machine-readable artifacts.

## Improvisation extension

The extension adds phase noise, grid-constrained slips, interruptions, delayed
self-feedback, fatigue and a homeostatic gain. The supplied notes report runaway
activity with stronger self-feedback, dispersal with fluctuation alone, and
collective silence with fatigue alone. These motivate measurements, not a claim
that the selected settings generalize to arbitrary stimuli.

Its session is 8 bars of straight input, 8 of triplets, then 32 without input.
`improv.py` explicitly lowers the homeostatic target during the final 6 bars.
Ending behavior is therefore conditioned by an external schedule; the notes'
poetic description of deciding to finish is not an autonomous-goal claim.

`random` is an output-level control derived from `improv`: it preserves notes,
voice identities and bar membership while randomizing time inside each bar.
It is not an independently running memoryless model. The coherence metric also
allows a per-bar grid offset; slips themselves are constrained to musical grids.
These scores do not demonstrate domain-neutral memory, musical quality or
semantic intelligence.

The supplied six-seed results are retained in full. The seed-2 demonstration was
explicitly selected for its visible structure, not randomly selected as an
unbiased example. Import validation reruns its `memory` and `improv` metrics,
compares the disabled extension with the old model, and checks the stored
six-seed summary against its rows. It does not rerun the full six-seed batch or
perform a listening evaluation.

## Boundary for the next experiments

A previously active voice becoming active again occurs within an existing
field. It is not evidence of serialization, removal to a latent store, semantic
association search, or Max-percentage initialization. Those are A2/A3 work.
Keep legacy sources as comparison baselines; introduce the domain-neutral
reference separately, with persistence, forgetting, snapshot continuation,
Max-relative initialization and recall-after-latency acceptance experiments.
