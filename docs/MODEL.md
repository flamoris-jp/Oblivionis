# Oblivionis Model Concept

This document records the initial conceptual boundary for Oblivionis.

It intentionally describes **what the model is trying to represent**, not a frozen implementation API.

## 1. Model class

Oblivionis is a **dynamic state model**.

It is model-like in the sense that a runtime can stimulate it, evolve it, observe it, and use its outputs. It is not defined by autoregressive token prediction, prompt completion, or media generation.

A useful contrast is:

~~~text
LLM
input + model parameters + inference state
    → predicted token/content

Oblivionis
input + history-shaped dynamic state + time
    → changed state / resonance / recall / bounded influence signal
~~~

The second form is the important one: **history is part of the computation**.

## 2. Active Field

The **Active Field** is the currently evolving model state.

The exact representation is not frozen. Candidate state may include:

- oscillator phase;
- amplitude / activation;
- frequency or equivalent response dynamics;
- coupling;
- resonance parameters;
- fatigue / habituation;
- homeostatic terms;
- decay;
- local stability;
- fluctuation state;
- externally stimulated features;
- model-specific hidden state required to continue evolution.

The Active Field should be inspectable through bounded summaries even if its complete internal state is larger.

## 3. Time and fluctuation

Oblivionis is not intended to be a pure request/response lookup.

State advances over time.

Fluctuation may alter trajectories, but randomness must not erase the distinction between:

- a state reached because of prior experience; and
- an unrelated random state.

Deterministic seeds should be supported in experiments and tests wherever practical.

## 4. Forgetting

Forgetting is modeled as a transition.

Initial conceptual stages:

~~~text
active
  ↓
fading
  ↓
latent / Profundumis
  ↓
evicted or extinct
~~~

These names do not require four physical storage systems. They describe different semantics that should not be accidentally collapsed.

### Forgetting is not deletion

When a state falls out of active participation, Oblivionis may retain a snapshot or trace that can later participate in recall.

Deletion/eviction is a separate operation.

## 5. Profundumis

**Profundumis** is the latent deep store for states that have fallen out of the Active Field but remain recallable.

A future entry format may contain:

~~~text
ProfundumisEntry
  id
  state_snapshot
  created_at
  latent_since
  decay / retention metadata
  resonance_signature
  external_pointers[]
  recall_metadata
~~~

This is illustrative, not a frozen schema.

### Snapshot boundary

A snapshot should capture enough state to reproduce or meaningfully reintroduce the relevant oscillatory condition.

The model should distinguish:

- exact restoration, if supported;
- partial state reactivation;
- extracted resonance signatures;
- lossy/compressed traces.

Not every forgotten state needs to preserve full fidelity forever.

## 6. Pointer / meaning separation

Oblivionis should not make raw data identity and semantic meaning the same object.

Conceptually:

~~~text
Profundumis entry
   │
   ├── pointer ──────────► external datum
   │
   └── association hooks
              │
              ▼
       semantic relationships
~~~

A pointer answers **which external thing?**

Associations answer **what does this currently mean or evoke?**

These relationships may change independently.

This also prevents Oblivionis from becoming the lifecycle authority for every image, document, audio file, or other referenced asset.

## 7. Recall

Recall is a mode of changing the present using latent state.

Initial recall families:

### Explicit recall

A caller directly identifies a latent entry or group of entries.

### Associative recall

Current semantic/contextual input activates related entries.

### Resonance recall

The current dynamic state resembles or resonates with a latent state's signature strongly enough that it becomes a recall candidate even without an explicit semantic relationship.

This third mode is particularly important: Oblivionis should be able to represent **state-dependent recall that is difficult to explain as a database query**.

## 8. Recall is reconstruction

A recalled state does not have to overwrite the Active Field.

Conceptually:

~~~text
current Active Field
        +
recalled state fragment
        +
current fluctuation
        ↓
new Active Field
~~~

Possible policies may include:

- exact restore;
- weighted blend;
- local reactivation;
- resonance-only influence;
- temporary recall;
- persistent reintegration.

The policy should be explicit and testable.

## 9. Runtime integration

FLAMORIS AI Runtime is expected to orchestrate Oblivionis as a model/capability.

Conceptual operations may eventually include:

~~~text
stimulate(input)
advance(delta_time)
observe(scope)
snapshot(scope)
forget(target, policy)
recall(cue, policy)
list_recall_candidates(cue)
~~~

These are conceptual verbs, not committed API names.

Runtime integration must define bounded influence. For example, downstream generation might receive a normalized state vector, selected recalled references, or a bounded bias object. Oblivionis should not directly perform arbitrary external actions simply because a state became active.

## 10. Why music experiments matter without defining the model

Music exposes several useful properties:

- synchronization can be heard;
- timing drift can be measured;
- persistence after input stops is obvious;
- replay versus transformation is distinguishable;
- fatigue and role changes are audible;
- incoherent randomness is easy to compare against structured variation.

The experiments therefore act as an oscilloscope with speakers.

The core model must remain domain-neutral.

## 11. Initial invariants

Until deliberately revised, preserve these invariants:

1. Oblivionis is not an LLM.
2. Oblivionis is not an agent.
3. Oblivionis is not a music model.
4. Past state must be able to change future evolution.
5. Randomness alone does not count as memory.
6. Forgetting and deletion are distinct.
7. Profundumis stores latent state or traces, not merely semantic records.
8. Pointer identity and semantic meaning remain separable.
9. Recall may be partial and reconstructive.
10. AI Runtime remains the execution/orchestration authority.

## 12. Open design questions

The next design pass should answer:

- What is the smallest domain-neutral state representation that preserves the observed behavior?
- What exactly is captured in a full state snapshot?
- Which state can be compressed into a resonance signature?
- How are latent traces scored for associative recall versus resonance recall?
- How does a recalled trace blend into the present without producing unstable self-excitation?
- What is the retention/eviction model for Profundumis?
- Which semantics live inside Oblivionis and which belong to an adjacent association system?
- What bounded output should AI Runtime receive from Oblivionis?
- What deterministic acceptance experiments prove persistence, forgetting, recall, and non-random transformation?
