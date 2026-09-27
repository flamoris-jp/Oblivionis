# Max-relative recall initialization

Status: design requirement and proposed Phase A mechanics, not an implemented API.
Decision recorded: 2026-09-27.

## Why retain Max?

Max is retained so that, when entering a remembering/recall mode, the recalled
trace can start from a chosen percentage of its own peak activation. It is not
only an interesting historical maximum or a backup of the state before forgetting.

```text
experience -> capture Max reference -> fade -> Profundumis
                                             |
                                      recall at ratio r
                                             |
                         initial recalled activation = r * peak activation
                                             |
                              reintegrate into the present
```

For example, 25%, 50%, or 100% selects a different initial activation of the same
remembered pattern. These are examples, not defaults. The denominator is that
trace's retained peak, not the current nearly forgotten value, a global maximum,
or the maximum representable value of the model.

## Proposed representation

Keep three objects distinct:

- A **checkpoint** continues an interrupted computation, including clock, RNG,
  pending feedback, topology, and every evolving variable needed for continuation.
- A **Max reference** retains a coherent state from one observed peak instant,
  with its scope, node IDs, interval, metric/version, measured value and time.
- A **recall seed** is constructed from that reference with explicit activation
  scaling, before the current field's dynamics and integration policy act on it.

The purpose is a maintainer requirement. The exact peak metric, scope, interval,
and reintegration rule remain design proposals to be tested in A2/A3. Do not
invent an impossible snapshot by taking unrelated per-variable maxima from
different times. Start with caller-delimited experience intervals and fixed node
scopes; specify tie-breaking and zero/missing-peak behavior. Use a documented
activation norm or other reviewed measure to select the peak, not a music-only
loudness metric. Do not silently update Max due solely to repeated recall.

## What a percentage scales

For a non-negative peak activation vector `a_peak`, a candidate rule is:

```text
a_seed = r * a_peak, with 0 <= r <= 1
```

Only the specified activation/amplitude components are scaled. Phase, frequency,
node IDs, semantic associations, clock, RNG and coupling matrices are not all
multiplied by `r`. A norm used to *select* the peak is not automatically the
quantity being scaled: 50% amplitude is not 50% squared energy.

The stored reference remains immutable. Zero means no recall influence, not
clearing the current field. Invalid or non-finite ratios are rejected before
mutation. A missing or incompatible reference returns an explicit outcome;
never silently substitute the fading state. Ratios above 100% are outside the
initial proposal and require an explicit bounded amplification policy later.

## Initialization is not the final response

Keep `recall_ratio` separate from a potential `blend_weight` into the current
field. A 100% seed does not mean replacing the present, rewinding its clock, or
achieving the same later trajectory. After initialization, current context,
phase, coupling, fatigue and fluctuation still matter.

Define node mapping, circular-phase handling, stale-schema rejection, and
reintegration bounds before implementation. Candidate lookup does not mutate
state. Apply explicit limits/cooldowns to repeated recall so it cannot repeatedly
increase its own reference without a newly defined experience interval.

## Required A2/A3 experiments

Test 0%, 25%, 50% and 100% against a known retained peak **before reintegration**.
The initial activation must match the chosen ratio within a stated tolerance.
Then independently test reintegration into distinct current fields. Also test
missing/zero peaks, invalid ratios, incompatible topology, persistence/reload,
repeated recall, and a decay period that does not silently change the stored Max.

Max's reference value, initial seed value and post-integration observation should
be distinguishable in the experimental record. Do not require a monotone final
response merely because the initialization ratio is monotone.

See [Phase A plan](PHASE_A_PLAN.md) and [model concept](MODEL.md).
