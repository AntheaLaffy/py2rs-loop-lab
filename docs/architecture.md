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

## Project Skill Scaffolding

Meta-skills retain architecture judgment because seams, domain ownership and
migration boundaries depend on project truth. Once those decisions stabilize,
repository initialization should generate project-specific operational skills.
Their documentation records steps and schemas; tested scripts own deterministic
registry collection, state transitions, fixture orchestration and report checks.

This reduces repeated prompt mechanics without pretending that code generation
can replace architectural reasoning. A role stays in `prompt` mode while its
workflow is evolving and moves to `scaffold` mode when its mechanics are stable.
Only one variant may be discoverable; archive the counterpart outside every
agent skill root and start a fresh session after switching. Do not scaffold
workflows whose inputs, outputs or failure modes are still speculative.

### Mode Lifecycle

Mode is selected per role; it is not one project-wide choice. A newly generated
role defaults to `prompt`. It may move to `scaffold` only after its inputs,
outputs, failure paths, completion criteria and recovery behavior are stable and
test or forward-test evidence exists.

Both variants of a role use the same skill name and record role, mode and a
real-file `validation_evidence` path in `.py2rs-skill-variant.json`. The active
variant lives under an agent discovery root. The inactive variant lives under
the project's `.py2rs/skill-archive` or another directory excluded from
discovery. Every Claude, Codex or other discovery root actually used for the
project participates in duplicate checks; changing a directory or skill name
cannot bypass the one-active-variant-per-role invariant.

A mode switch is a durable state transition. Dry-run first, then move the two
variants on one filesystem under a lock and journal. After files switch, the
journal remains `switched_pending_notes` until `NOTES.md` records the new mode,
active path and archived path and that update is explicitly acknowledged. Start
a fresh session only after the journal clears. Moving files cannot retract old
instructions already loaded into the current context, so the new session is a
correctness requirement rather than a convenience.

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

The same `NOTES.md` profile selects crate reconnaissance mode:

- `agent`: default; a fresh-context researcher produces bounded crates.io and Cargo dependency evidence
- `manual`: the user supplies candidate, feature and dependency-path evidence to save agent tokens
- `disabled`: skips evidence after warning that the user must understand or manually research the Rust ecosystem

Registry proxy configuration is a project usage preference. Store a non-secret URL or environment-variable reference in `NOTES.md`; do not commit machine-specific Cargo configuration or credentials.

Initialization records these choices but does not add crates or modify a lockfile. Dependency alignment applies the profile when a seam or migration unit needs the capability. Hard `require` and `avoid` preferences cannot be silently overridden.

## Dependency Alignment

Dependencies are aligned by capability, not by package name.

Enabled reconnaissance uses three evidence layers that do not replace each other:

- Registry search discovers the three most relevant candidates for a public capability and adds every user-named candidate; named candidates do not consume the Top 3.
- Context7 checks focused APIs, features and official examples. Bootstrap it when missing; fall back explicitly to docs.rs or crate source only when setup, service access or indexing fails.
- Cargo `info`, `metadata` and `tree` prove the resolved version, feature selection and dependency paths to the actual container, codec, runtime or other capability owner.

An umbrella crate cannot be rejected from its public API alone. `direct` means the target implementation can call the candidate's public API; `backend` means it should bypass the umbrella API and call a feature-selected lower dependency. Dependency alignment consumes the compact report and loads raw evidence only to challenge a conclusion.

Allowed paths:

- direct crate coverage when fixtures prove behavior
- crate-owned stable lower layer plus a compatibility adapter
- narrow hand-written replacement for semantic gaps
- full hand-written replacement when it is smaller, safer or easier to verify than crate reuse plus adapter

Fewer Rust dependencies is not a success metric. Under `standard`, full wheel rebuilding is not the default either. The selected path must follow the recorded rewrite profile, and each unit records how the preference was applied or why it was changed.

Disabled reconnaissance is recorded as `user_disabled`, not as completed search. It permits progress but leaves explicit residual ecosystem risk.

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
