# AGENTS.md

This repository contains **Oblivionis**, an experimental non-LLM dynamic state and memory model developed within the FLAMORIS ecosystem.

Read [README.md](README.md) and [docs/MODEL.md](docs/MODEL.md) before making substantial changes.

Do not implement behavior from chat context alone. Preserve the distinction between reviewed repository design, current experiments, and future ideas.

## Repository identity

Oblivionis is intended to be callable by an AI runtime in a model-like position, but it is not an LLM and should not be forced into token-prediction or chat-oriented abstractions.

### This repository owns

Planned ownership:

- the evolving Active Field;
- oscillator/state dynamics;
- resonance and coupling;
- fluctuation and bounded stochastic variation;
- fatigue / habituation and homeostatic dynamics;
- forgetting transitions;
- model-state snapshots;
- Profundumis latent storage semantics;
- association- and resonance-driven recall;
- model-level observe/stimulate/advance/snapshot/forget/recall contracts.

### This repository does not own

Do not absorb authority from neighboring systems:

- agent identity, conversation, goals, and personality belong to agent-layer systems;
- workflow scheduling and orchestration belong to AI Runtime;
- media generation remains owned by its relevant model/service;
- external asset lifecycle belongs to the system that owns those assets;
- semantic meaning must not be collapsed into a raw external-data pointer.

## Core architecture rules

### 1. Oblivionis is not a music model

Music experiments are probes used to make dynamics observable.

Do not make rhythm, MIDI, pitch, DAW concepts, or music-specific state part of the core model unless a reviewed design explicitly generalizes them.

### 2. History must matter

Do not replace stateful dynamics with uncorrelated randomness.

Fluctuation may perturb behavior, but the defining question is whether prior experience changes the state from which later behavior emerges.

### 3. Forgetting is not synonymous with deletion

Keep these concepts distinguishable:

- active state;
- fading state;
- latent state in Profundumis;
- eviction;
- irreversible extinction.

A future implementation may simplify them, but only through an explicit reviewed decision.

### 4. Recall is not necessarily exact restore

Recall may reintroduce only part of a prior state and may combine with the current Active Field.

Preserve room for both semantic-association recall and non-semantic resonance recall.

### 5. Pointer and meaning are separate

A memory entry may reference external data through a stable pointer or identifier.

Do not assume that the pointer itself owns:

- semantic tags;
- relationships;
- interpretation;
- external asset lifetime.

The same external datum may accumulate different associations over time.

### 6. Profundumis is an intentional project term

**Profundumis** names Oblivionis's latent deep store / drawer.

It is intentionally a project coinage, not a claim of standard Latin usage. Do not silently rename it to Profundum or Profundis.

### 7. Keep runtime influence bounded

Oblivionis may produce state signals, recalled traces, biases, or model outputs that a runtime can use.

It must not silently bypass AI Runtime authorization, workflow, resource, or effect boundaries.

## Experiment discipline

Experiments should make behavior observable and falsifiable.

Where practical:

- preserve random seeds;
- record parameters;
- distinguish input from model-generated behavior;
- compare against useful baselines such as replay and random behavior;
- record failures as well as successful runs;
- keep generated large media artifacts out of source control unless they are intentionally reviewed assets.

Do not promote an experimental parameter or domain-specific mechanism into the stable model contract solely because one demo produced interesting behavior.

## Implementation language

No production implementation language is frozen yet.

Do not add a root build scaffold merely by copying another FLAMORIS repository.

Choose the implementation boundary only after the model contract and runtime integration requirements make the trade-offs concrete. Experiment-specific Python is acceptable without making Python the permanent production language.

## AI Runtime boundary

Conceptually, AI Runtime may:

- stimulate Oblivionis with bounded input;
- advance or sample model state;
- request observation;
- request snapshot / forgetting / recall operations;
- receive bounded state-derived outputs.

AI Runtime remains responsible for scheduling, workflow semantics, capability permissions, resource policy, and downstream actions.

## Before implementing a substantial change

- read README.md and docs/MODEL.md;
- inspect current experiments and tests;
- identify whether the change belongs to the core model or only to an experimental probe;
- identify the state authority and persistence boundary;
- check whether the change couples pointers to semantic meaning;
- state how the behavior can be measured or tested;
- keep current implementation and planned behavior clearly separated.

## Security and privacy

- Never commit secrets, credentials, tokens, private keys, private topology, or sensitive user data.
- Treat external input and referenced content as untrusted.
- Keep serialized state bounded and validate it before loading.
- Do not add arbitrary shell, ambient filesystem/network access, or embedded credentials as model shortcuts.
- A recalled association does not grant authority to act on the referenced resource.

## Licensing

Unless stated otherwise, code in this repository is licensed under Apache License 2.0.

Do not add third-party code, models, model weights, datasets, media, fonts, or generated assets unless their licenses are compatible and clearly documented.
