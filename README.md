# Oblivionis

**Oblivionis** is an experimental non-LLM dynamic state and memory model exploring **AI behavior that changes with experience**.

Its intended path is: experience changes an oscillatory field; that field produces firing responses; an AI runtime uses those responses to introduce **history-shaped fluctuation into its execution and behavior**. This is more than returning stored memories or starting work when an event occurs.

Oblivionis is not an LLM, a generative-media model, or an agent. Oscillation, resonance, fatigue, forgetting, association, and recall shape the internal state from which those responses emerge. Firing and runtime modulation are design goals, not implemented integration claims.

> The same input does not have to meet the same internal state twice.

## Project

**Name:** Oblivionis

**Description:** Experimental non-LLM model for history-shaped firing, runtime modulation, forgetting, and associative recall.

**Status:** experimental

## 🧭 Repository identity / このRepositoryは何者？

### What it is / 何者か

Oblivionis is a **non-LLM AI model** centered on dynamical state rather than token prediction.

Architecturally, it is intended to sit beside callable models such as Vem: something that an AI runtime can invoke as a model capability. Its role, however, is different. Oblivionis does not primarily generate content. It evolves a history-shaped state and is intended to provide firing responses and state-derived signals that the runtime can use to modulate subsequent behavior.

The goal is not merely to add independent random noise or ask an LLM to act differently. Prior experience should change the state from which a response arises, and that response should influence the runtime through an explicit integration boundary.

Early prototypes use coupled oscillatory systems to explore how experience can persist as state, fade through forgetting, reappear through resonance, and influence later behavior.

Music has been used as an experimental probe because synchronization, drift, persistence, fatigue, and spontaneous reorganization are easy to hear and measure. **Oblivionis is not a music model.**

### What it owns / 主な責任範囲

Oblivionis is intended to own:

- the evolving **Active Field**;
- oscillation, resonance, coupling, fatigue, fluctuation, and homeostatic dynamics;
- state traces produced by experience;
- model-level firing responses and state-derived signals for runtime modulation;
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
- workflow scheduling, capability execution, or the runtime's decision to apply a modulation signal;
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

The repository now retains 17 historical Python probe files, supplied compact results, research notes, and six bounded regression tests under [experiments](experiments/README.md). These do not yet implement the domain-neutral core, checkpoint serialization, Max-relative recall initialization, Profundumis, sensor/trigger integration, or firing-derived AI Runtime modulation.

The production model contract, serialization format, runtime API, and implementation language are **not frozen yet**. See the [Phase A plan](docs/PHASE_A_PLAN.md) for A1 experiment preservation, A2 core/state persistence, and A3 latent recall.

### Where it fits / FLAMORISのどこに属する？

Oblivionis is designed to be callable from **FLAMORIS AI Runtime** while remaining independently understandable as a model. Its response signals are intended to feed back into runtime execution through a defined boundary.

Conceptually, not an implemented connection:

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
              ├── Active Field / firing responses
              ├── Fluctuation
              ├── Association / Recall
              └── Profundumis

Oblivionis firing responses
        ↓
runtime-defined modulation mapping
        ↓
history-shaped fluctuation in runtime behavior
~~~

AI Runtime remains responsible for execution, scheduling, capability boundaries, and orchestration. Oblivionis owns its model state and responses; Runtime owns where, when, and how a response may influence execution.

See [Model concept](docs/MODEL.md) for the conceptual contract.

## 🌘 Firing, modulation, and triggers

The central goal is **experience → evolving state → firing → runtime fluctuation → changed behavior**.

Here, **firing** names a model-level response arising from the current field. It is a conceptual term, not a claim of biological brain simulation or a commitment to a particular spiking-neural-network implementation.

Keep two uses distinct:

- **Modulation:** a response contributes bounded fluctuation to runtime behavior, including within an already-running execution where the runtime explicitly supports it. It does not require starting a new Workflow.
- **Trigger:** a response meets a registered condition for requesting new runtime work. Firing does not automatically mean a Workflow starts.

Camera/microphone adapters may supply stimuli, while recalled traces may change the current field from within. Neither every input nor every recollection must fire. Sensor and trigger design is tracked in [#3](https://github.com/flamoris-jp/Oblivionis/issues/3); Profundumis association/recall is tracked separately in [#4](https://github.com/flamoris-jp/Oblivionis/issues/4).

The signal format, modulation mapping, supported execution points, and influence limits still need design and experiments. Do not equate modulation with arbitrary parameter changes, independent random noise, or a permission to execute actions.

**日本語:** Oblivionisは、経験によって変わる振動状態から発火し、その発火をもとにAI Runtimeへ揺らぎを与えて、AIの振る舞いを変えることを目指す非LLMモデル。処理開始のトリガと、実行中の振る舞いへの作用は別の役割として扱う。これらの連携はまだ構想段階であり、音楽実験は本体を観測するための実験装置である。

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

A state may leave the Active Field while remaining available as a latent trace. Recall also does not have to mean exact restoration: a recalled state may be mixed with the current field and current fluctuation, allowing the past to influence the present without replacing it. That changed present may then affect firing and runtime modulation; recall need not cause an immediate trigger.

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

### Max as the reference for remembering

Retaining **Max** is intended to let a remembering mode initialize a trace at a chosen percentage of its own stored peak, rather than a percentage of its nearly forgotten current value. For example, an initial recalled activation could be `recall_ratio * peak_activation`.

Recording Max during experience is distinct from using it: **Max-state search and percentage reactivation apply after a trace has been stored in Profundumis, during association/recall.** Ordinary activity, firing, and trigger thresholds must not use retained Max as a continuous amplification or restoration rule.

This initial intensity is separate from how the recalled pattern blends into the present. Do not multiply an entire checkpoint, rewind time, or treat 100% as exact restoration. The mechanism is planned, not yet implemented; see [Max-relative recall](docs/MAX_RECALL.md) for the requirement, proposed boundaries, and acceptance experiments.

## Experiments / 実験もここで育てる

Experiments are first-class repository contents. Keep code, seeds, parameters, small results and useful failures here as Oblivionis evolves. Historical music probes stay distinct from the domain-neutral reference model. Large regenerated media and private raw logs are not committed by default.

このリポジトリでは、実験コード・結果・失敗の記録も継続して管理する。音楽実験は本体とは分けて残し、将来の変更を比較する基準にする。

For numerical regressions, use a Python 3.13 virtual environment and run from the repository root:

```bash
python -m pip install -r experiments/requirements-test.txt
python -m unittest discover -s experiments/tests -v
```

See [experiment instructions](experiments/README.md), [research notes](experiments/NOTES.md), [source provenance](experiments/provenance.json), and [import validation](experiments/results/import_verification.json). The numerical checks do not validate media rendering or prove future memory/recall capabilities.

## Design principles

- **State before story.** Expose measurable state rather than inventing semantic explanations for the model.
- **History changes the present.** Randomness alone is not memory.
- **Firing is a source of modulation.** Do not reduce the model to a memory lookup or Workflow-start detector.
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
8. firing-response and AI Runtime modulation contracts, distinct from Workflow-start triggers;
9. bounded observability and serialization;
10. acceptance experiments that distinguish memory, noise, persistence, forgetting, recall, and history-dependent behavioral change.

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
