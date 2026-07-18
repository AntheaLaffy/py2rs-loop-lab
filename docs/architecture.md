# Architecture

[中文版本](architecture.zh.md)

py2rs does not require one fixed directory layout. It defines a control plane and review discipline for incremental rewrites.

This is a meta-skill architecture. The core skills describe how to create project-specific rewrite skills; they are not a finished workflow that should be applied before a project has its own facts, constraints, manifest and accepted seam.

## Control Plane

The control plane records:

- migration units
- current owner and target owner
- public interface policy
- verification commands or fixtures
- rollback route
- required review roles
- current state

The control plane can be a YAML manifest, Tauri backend facade, HTTP adapter, CLI dispatcher, feature flag registry or pipeline stage registry. A Python router is only appropriate when Python remains the orchestrating process.

## Stateful Workspace

The workspace should make progress durable across sessions. The structure is inspired by [`teach`](../skills/foundations/teach/SKILL.md):

- mission: why this rewrite exists and what must not be lost
- resources: source-of-truth docs, dependency sources and trusted references
- notes: user preferences, project constraints and temporary observations
- records: non-obvious migration lessons and decisions
- manifest: current state, owners, verification and rollback
- reviews: durable evidence for promotion decisions

Without this state, a loop becomes memory-driven. py2rs assumes memory is not enough.

## Granularity Profile

The rewrite should ask the user how fine the units should be during initialization.

Available vocabulary:

- `coarse`: fewer units and fewer reviews; useful for low-risk helpers or cost-sensitive work.
- `balanced`: default; independently verifiable units without forcing every helper into its own review cycle.
- `fine`: useful for public payloads, parsers, data structures, error projection, persistence, model IO and dependency compatibility layers.
- `ultra_fine`: exceptional; useful when ABI, memory, numeric/model correctness or rollback precision matters more than cost.

Finer units cost more review rounds and tokens. They also reduce hallucination risk, dead-code risk and behavioral drift.

## Rewrite Preferences

Repository initialization uses a separate preference profile to record how strongly the user wants to reuse Rust ecosystem dependencies and which relevant frameworks they prefer. It lives in `NOTES.md`, not in the manifest:

- `standard`: default capability-first tradeoff between maintained crates, adapters and fixture-backed hand-written code
- `ecosystem_first`: maximize maintained crate reuse
- `handwritten_first`: prefer hand-written project/domain behavior while allowing general infrastructure
- `domain_from_scratch`: rebuild the domain stack bottom-up while still allowing `std`, async runtimes, serialization, diagnostics, tracing, transport and build tooling
- `custom`: capability-specific rules

After the overall strategy, ask only about framework categories detected in the project, such as async, errors/tracing, numeric/ML, Web, UI or persistence. Candidate names in the skills are examples; actual choices must respect the current project and current official sources.

Initialization records these choices but does not add crates or modify a lockfile. Dependency alignment applies the profile when a seam or migration unit needs the capability. Hard `require` and `avoid` preferences cannot be silently overridden.

## Dependency Alignment

Dependencies are aligned by capability, not by package name.

Allowed paths:

- direct crate coverage when fixtures prove behavior
- crate-owned stable lower layer plus a compatibility adapter
- narrow hand-written replacement for semantic gaps
- full hand-written replacement when it is smaller, safer or easier to verify than crate reuse plus adapter

Fewer Rust dependencies is not a success metric. Under `standard`, full wheel rebuilding is not the default either. The selected path must follow the recorded rewrite profile, and each unit records how the preference was applied or why it was changed.

## Source Expansion

At repository initialization, first-layer direct Python dependencies may be expanded or snapshotted as a local reference corpus.

Second-layer or deeper dependencies require public-seam call-path evidence. Lockfile transitivity alone is not enough. py2rs rewrites the project, not the entire Python or native ecosystem.

## Manifest Shards

Large rewrites may use a root manifest plus shard manifests when boundaries are stable enough for parallel Codex sessions.

Shards must name:

- owned and excluded units
- public seam
- cross-shard contracts
- shared prerequisites
- verification commands
- rollback routes

Sharding is for real independent progress, not for hiding an unclear architecture.
