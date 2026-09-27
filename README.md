# Oblivionis

**Oblivionis** is an experimental dynamic state and memory model for AI runtimes.

It is not an LLM, a generative-media model, or an agent. Instead, it maintains a continuously evolving internal field shaped by oscillation, resonance, fluctuation, fatigue, forgetting, association, and recall.

> The same input does not have to meet the same internal state twice.

## Project

**Name:** Oblivionis

**Description:** Dynamic state and memory model for AI runtimes based on oscillation, forgetting, association, and recall.

**Status:** experimental

## 🧭 Repository identity / このRepositoryは何者？

### What it is / 何者か

Oblivionis is a **non-LLM AI model** centered on dynamical state rather than token prediction.

Architecturally, it is intended to sit beside callable models such as Vem: something that an AI runtime can invoke as a model capability. Its role, however, is different. Oblivionis does not primarily generate content. It evolves state over time and returns signals, recalled traces, and state changes that can influence later runtime execution.

Early prototypes use coupled oscillatory systems to explore how experience can persist as state, fade through forgetting, reappear through resonance, and influence later behavior.

Music has been used as an experimental probe because synchronization, drift, persistence, fatigue, and spontaneous reorganization are easy to hear and measure. **Oblivionis is not a music model.**

### What it owns / 主な責任範囲

Oblivionis is intended to own:

- the evolving **Active Field**;
- oscillation, resonance, coupling, fatigue, fluctuation, and homeostatic dynamics;
- state traces produced by experience;
- forgetting as a state transition rather than immediate deletion;
- full or partial model-state snapshots suitable for later reactivation;
- associative and resonance-based recall;
- **Profundumis**, the latent deep store for states that have faded from the Active Field;
- model-level contracts for stimulating, advancing, observing, snapshotting, forgetting, and recalling state.

### What it does not own / 持たない責任

Oblivionis does not own:

- language reasoning or token generation;
- image, audio, video, or music generation as a domain;
- agent identity, goals, personality, or conversation history;
- workflow scheduling or capability execution;
- the lifecycle or storage authority of external assets referenced by memory entries;
- a universal semantic database.

External data should be referenced through stable pointers or identifiers. The pointer to data and the meaning associated with that data are intentionally separate concerns.

### Current status / 現在の状態

**Experimental / research-stage.**

Prototype experiments have already explored:

- coupled oscillatory memory;
- phase locking and resonance;
- selective strengthening from input;
- gradual forgetting after input stops;
- fluctuation and interruption;
- habituation / fatigue;
- homeostatic activity;
- re-emergence of previously active patterns;
- behavior between literal replay and random variation.

The production model contract, serialization format, runtime API, and implementation language are **not frozen yet**.

### Where it fits / FLAMORISのどこに属する？

Oblivionis is designed to be callable from **FLAMORIS AI Runtime** while remaining independently understandable as a model.

Conceptually:

~~~text
AI Agent / Application
        │
        ▼
FLAMORIS AI Runtime
        │
        ├── LLM / Vision / Speech / Generation / Vem / ...
        │
        └── Oblivionis
              │
              ├── Active Field
              ├── Fluctuation
              ├── Association / Recall
              └── Profundumis
~~~

AI Runtime remains responsible for workflow execution, scheduling, capability boundaries, and orchestration. Oblivionis contributes evolving model state that other runtime steps may observe or use as bounded input.

See [Model concept](docs/MODEL.md) for the initial conceptual contract.

## 🌘 Core idea

A conventional memory system often treats memory as stored records.

Oblivionis explores another possibility:

~~~text
experience
   ↓
state changes
   ↓
resonance / coupling / fatigue / fluctuation
   ↓
Active Field
   ↓
fade / forget
   ↓
Profundumis
   ↓
association or resonance
   ↓
partial recall
   ↓
Active Field changes again
~~~

Forgetting is therefore not necessarily deletion.

A state may leave the Active Field while remaining available as a latent trace. Recall also does not have to mean exact restoration: a recalled state may be mixed with the current field and current fluctuation, allowing the past to influence the present without replacing it.

## Profundumis

**Profundumis** is the project name for Oblivionis's deep drawer-like latent store.

The name is intentionally a FLAMORIS coinage rather than standard Latin.

A Profundumis entry may eventually contain:

- an oscillatory/model-state snapshot;
- temporal metadata;
- decay and retention metadata;
- stable pointers to external data;
- recall hooks or resonance signatures.

The semantic relationships around an entry should remain separable from the raw pointer to the referenced data.

## Design principles

- **State before story.** Expose measurable state rather than inventing semantic explanations for the model.
- **History changes the present.** Randomness alone is not memory.
- **Forgetting is behavior.** Decay, latent storage, eviction, and extinction are different concepts.
- **Recall is reconstruction.** Exact replay is only one possible mode.
- **Pointers and meaning are separate.** External data identity and semantic association must not be conflated.
- **Bounded influence.** Runtime integrations define how much Oblivionis may affect downstream execution.
- **Experiments remain measurable.** Preserve seeds, parameters, and results where practical.
- **Do not confuse a probe with the model.** Music or other domains may be used to observe the dynamics without defining the model's purpose.

## Repository roadmap

Before freezing a production implementation, define and review:

1. the minimal mathematical state model;
2. Active Field state and update rules;
3. snapshot and restoration boundaries;
4. Profundumis entry format and retention semantics;
5. semantic-association and resonance recall modes;
6. separation between data pointers and semantic relationships;
7. deterministic seeding and reproducibility;
8. AI Runtime integration contracts;
9. bounded observability and serialization;
10. acceptance experiments that distinguish memory, noise, persistence, forgetting, and recall.

## Repository principles

- Keep Oblivionis usable as an independent model, even while it is developed inside the FLAMORIS ecosystem.
- Do not turn this repository into an agent, workflow engine, conventional vector database, or media generator.
- Keep public documentation portable and free of private hostnames, credentials, topology, or machine-specific paths.
- Do not commit secrets, private data, or unlicensed model/data assets.
- Prefer explicit experiments and measurable behavior over anthropomorphic claims.
- Treat current repository code, tests, documentation, and reviewed design decisions as the source of truth.
- AI-assisted development is welcome; submitted changes still require human review and responsibility.

## FLAMORIS

Oblivionis is developed within the FLAMORIS ecosystem, but intentionally keeps its own repository name and model identity.

FLAMORIS is open-source software for creative work and AI-native production.

Use it however you like.

Commercial use is welcome and does not require permission. If you'd like, we'd be happy to hear what you used FLAMORIS for. This is completely optional.

FLAMORIS software is provided as-is. We do not provide individual support or guaranteed assistance.

If you run into trouble, let your AI assistant read the repository, documentation, Issues, tests, logs, and source code and help you solve it.

If FLAMORIS helps you or you find it interesting, your support helps fund development and keeps the project growing. 🌱

<sub>Mostly GPU bills.</sub>

---

## FLAMORISについて

FLAMORISは、クリエイティブ制作とAIネイティブな制作環境のためのオープンソースソフトウェアです。

勝手に使ってください。改造しても、組み込んでも、面白いものや変なものを作ってもOKです。

商用作品や製品で使う場合も許可は不要です。もしよければ「こんなのに使ったよ」と教えてもらえるとうれしいです。もちろん強制ではありません。

FLAMORISのソフトウェアは現状のまま提供されます。個別サポートや動作保証はありません。

困ったときは、README、ドキュメント、Issue、テスト、ログ、ソースコードをあなたのAIに読ませて、自己サポートしてもらってください。

もしお役に立てたり、面白いと思っていただけたなら、開発費用をご支援いただけるとうれしいです。FLAMORISは元気になって育ちます。🌱

<sub>主にGPU代とか。</sub>

## License

Code in this repository is licensed under the [Apache License 2.0](LICENSE), unless otherwise noted.

AI models, model weights, datasets, media, and other non-code assets may use separate licenses. State their applicable licenses alongside those assets.
