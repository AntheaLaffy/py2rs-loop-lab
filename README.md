# py2rs-loop-lab

> Architecture skills for creating project-specific rewrite skills.

[中文 README](README.zh.md)

`py2rs-loop-lab` is a loop-engineering repository for controlled Python-to-Rust and legacy-to-Rust rewrites.

It is not a drop-in skill pack. Use AI to read this repository as an architecture reference, then ask it to create concrete skills for your actual project. The real loop starts only after the project has its own facts, constraints, manifest, records, dependency policy and review gates.

If you want open-ended creative exploration, this is the wrong tool. This project is for bounded engineering work: migration state, behavior evidence, dependency alignment, review reports and rollback.

## How To Use It

1. Start with a real project repository.
2. Ask AI to study this repository's ideas and architecture.
3. Have AI design project-specific skills for that repository: coordinator, dependency/bootstrap, writer and review gates.
4. Initialize the rewrite workspace: mission, resources, notes, records, manifest, rewrite/framework preferences, behavior verification policy, dependency source policy, granularity, review cadence, manifest partitioning and execution policy.
5. Enter the loop: research crate capability paths, align dependencies, write one configured review batch, then run R0 and the required R1-R6 gates over it.

The core output is not Rust code. The core output is a project-specific loop that can keep producing reviewed Rust code.

## Current Architecture

The architecture separates five decisions that are easy to conflate:

- **Dependency and rewrite policy**: initialization records rewrite depth, relevant framework preferences, crate reconnaissance mode and the project's own crates.io proxy in `NOTES.md`. When a capability is actually needed, Context7, registry search and the Cargo graph determine whether to reuse a crate, call a lower backend, add an adapter or hand-write the semantic difference.
- **Verification target**: every unit uses a named legacy public seam as its behavior oracle. R0 proves observable Python/Rust parity; exact comparison is the default, with only explicitly recorded public-contract tolerances for model or numeric outputs. If a deep framework boundary cannot expose an independently comparable seam, re-cut the unit or keep its legacy owner.
- **Review budget and cadence**: `review_budget` selects the roles each unit needs; `review_policy.cadence` chooses per-unit review, one aggregate review every N units, or review after the current scope is fully written. The default is a three-unit batch. Promotion always flushes first; risk boundaries do so by default, but the user may choose to follow the overall cadence.
- **Manifest partitioning and execution mode**: a large manifest may be split into shards to reduce per-session context and expose dependency/rollback boundaries, but sharding does not mean parallel writing. One serial writer is the default. `coordinated_parallel` requires explicit user acceptance of extra token/build/integration cost plus a coordinator for shared dependencies and the Cargo build queue.
- **Project skill execution mode**: each coordinator, dependency bootstrap, writer or review role independently selects `prompt` or `scaffold`. Use `prompt` while the workflow still needs creative iteration; switch to `scaffold` only after its inputs, outputs and failure paths are stable and validated, so scripts can own deterministic operations.

The two variants may replace each other as the project matures, but exactly one variant per role may remain under agent discovery roots. Archive the counterpart outside those roots, write the new state back to `NOTES.md`, then start a fresh session. This preserves freedom for architectural judgment without spending prompt tokens on mechanics that have already stabilized.

## Why There Seem To Be Many Steps

These mechanisms do not require every migration unit to run every possible
flow. They trade a small amount of up-front control work for less repeated
search, context reconstruction and rework. The goal is to save tokens and time
and increase rewrite throughput while preserving user control, project fit and
strong behavioral consistency.

| Mechanism | What it saves or protects in this project |
|---|---|
| Manifest, records and reviews | A new session reads owners, rollback routes, prior decisions and evidence instead of rescanning the project or relying on chat memory. |
| Separate granularity and review cadence | Code stays in small testable, rollbackable units while a writer completes several units continuously and three share one review context by default. Fewer role switches increase rewrite throughput; a small project can use `end_of_scope` and review after all writing finishes. |
| `review_budget` and per-unit verdicts | Low-risk units do not need the full R0-R6 set. Batch reports reuse context while still allowing passing units to advance independently, preserving strong consistency. |
| Explicit behavior seam | Every unit names the legacy public seam and observable cases before implementation. Tensor, codec, artifact, model-loading and handoff checks remain in R0 when they cross that seam; framework internals stay out of scope only when they do not affect it. |
| Sharded but serial by default | A large inventory can be partitioned by stable capability and traversed in dependency order while one writer reuses loaded project and dependency context. This usually consumes fewer tokens and gives steadier throughput than several Codex windows. |
| Canonical shared dependencies | Concurrent Cargo builds contend for locks and target artifacts, while shared dependencies may also change `Cargo.toml`/`Cargo.lock`. If Burn lacks a required capability, one hand-written canonical prerequisite is created in the project and reused; agents may not build mutually invisible copies under `/tmp`. |
| Rewrite preferences and relevant-only framework questions | Initialization records crate-reuse depth and asks only about framework categories the project needs. Later units do not repeat the interview or preinstall speculative dependencies. |
| Fresh-context crate reconnaissance with compact reports | Registry search, Context7 checks and Cargo dependency paths stay in an isolated context; dependency alignment normally reads only the summary, reducing both prompt load and rework from a poor dependency choice. Users can select manual or disabled mode to control that cost. |
| `prompt` / `scaffold` modes | Architectural work stays flexible; stable registry queries, state transitions, batch flushing and report validation move into scripts, increasing the speed of repeated migration operations. This repository's `switch_skill_mode.py` uses validation, a lock and a journal so later sessions do not replay those mechanics in prompts. |
| Project truth, accepted seam and rollback | py2rs does not force one router or directory layout. A Tauri project may keep its command -> backend facade, while a Python-orchestrated project may use a Python router, and the manifest retains a route back to the legacy owner. |

Parallel work remains an exception. A coordinator exclusively owns the root
manifest, shared dependency registry, shared Cargo files and serialized build
queue; workers edit only assigned shard paths. Without that layer, agents tend
to reread the same code, duplicate missing capabilities, and wait on or repeat
compilation, making the rewrite slower and more token-intensive than serial work.

The objective is not "more process is more rigorous." It is to spend tokens
where judgment is needed, encode stable mechanics once, let writers progress
continuously for higher rewrite throughput, let the user control review
frequency, and preserve consistency with canonical dependencies, R0, per-unit
evidence and promotion rules. The user controls the seam and any explicit
comparison tolerance before implementation.

## Stateful Incremental Repository Architecture

py2rs does not rely on one long prompt to finish a migration. It turns the migration into a stateful, resumable, reviewable and rollbackable repository workflow. Each AI session should read the durable state instead of relying on chat memory.

- `mission`: records why the rewrite exists, what success means and which behaviors or constraints must not be lost
- `resources`: stores source-of-truth docs, existing tests, dependency source snapshots, protocol notes and trusted references so AI does not rewrite from memory
- `notes`: captures user preferences, including the rewrite-depth and framework profile, plus project constraints and temporary observations
- `records`: preserves non-obvious decisions, lessons, behavior differences, dependency tradeoffs and review conclusions for later sessions
- `manifest` / checklist: records each migration unit's state, owner, target owner, behavior verification seam and commands, rollback route, required review gates, cadence, partitioning and execution policy; this is the rewrite control plane
- shared dependency registry: records the one project path, owner, consumers and build evidence for shared crates, forks, adapters, generated sources or hand-written capabilities
- crate reconnaissance: searches by capability, uses Context7 for focused API/feature docs, and follows Cargo dependencies before a high-level crate is rejected or behavior is hand-written
- dependency alignment: applies the recorded rewrite/framework preferences while mapping Python dependencies, Rust crates, semantic-delta adapters and hand-written replacements by capability coverage
- bootstrap: proves the chosen seam handles parameters, return values, errors, logs, tests and rollback before business logic is migrated
- review evidence: lets a batch share each role's context while requiring per-unit verdicts; a unit advances only after its R0 behavior and required R1-R6 reviews

The point of this architecture is that the system stays runnable, testable and rollbackable at every migration state. Even if a new AI session takes over, it can continue from the repository's mission, records, manifest and reviews instead of guessing project state.

### Initialization Preferences And Dependency Timing

The initialization architecture separates user intent from migration state. A two-stage interview records strategy and relevant frameworks, crate reconnaissance/network choices, review cadence, partitioning and execution mode. Execution defaults to serial. Each unit records its legacy public behavior seam and comparison policy before implementation. Durable dependency preferences live in `NOTES.md`; verification/review/execution policy, ownership and rollback remain in the manifest.

Initialization does not preinstall speculative crates. Agent reconnaissance runs in a fresh context and gives dependency alignment a compact evidence report; manual mode lets a Rust-ecosystem expert provide the same evidence. Reconnaissance can be disabled to save tokens, but py2rs then warns that the user must understand or manually research crates.io, docs.rs and feature/dependency paths. Only after alignment are required crates added and locked.

See [Architecture](docs/architecture.md#project-skill-scaffolding) for the mode lifecycle and [Usage](docs/usage.md#switch-project-skill-modes) for the operational sequence.

## What The Rust Output Should Look Like

After using these skills to migrate Python to Rust, the first-stage code is not a line-by-line translation or an immediate style exercise. Every unit targets strict behavior parity at its declared legacy public seam, backed by complete tests. Deep framework internals remain outside scope only when they do not change that observable behavior.

The migrated Rust code should prove:

- every unit matches original Python public behavior at its declared seam
- model/artifact loading, tensor, codec and handoff cases are included whenever they cross that seam
- edge cases, error paths, fixtures and regressions are covered by tests
- each migration unit has review evidence instead of relying on code that merely looks correct

After the py-to-rs behavior migration is complete, give AI a separate goal:

```text
Adopt Rust community standards and build complete documentation.
```

If you still have capacity after that, ask AI to optimize the code toward Rust community style and structure. That phase should happen only after behavior tests are stable, and every style pass should rerun behavior review and the full test suite.

If you only want to install the skills into Codex or Claude first, see [`docs/installation.md`](docs/installation.md). It covers both discovery directories, Context7 setup, an "ask AI to install" prompt and macOS/Linux and Windows manual commands.

## Core Skills

- [`py2rs`](skills/py2rs/SKILL.md): overall rewrite discipline and routing.
- [`py2rs-runtime`](skills/py2rs-runtime/SKILL.md): rewrite preferences, control plane, manifest, state model, shards, granularity and review cadence.
- [`py2rs-crate-recon`](skills/py2rs-crate-recon/SKILL.md): fresh-context capability search, Context7 documentation checks and Cargo feature/dependency evidence.
- [`py2rs-dep-align`](skills/py2rs-dep-align/SKILL.md): dependency source expansion and capability alignment.
- [`py2rs-env-bootstrap`](skills/py2rs-env-bootstrap/SKILL.md): seam proof before business migration.

## Review Gates

- [`R0 behavior`](skills/py2rs-review-r0-behavior/SKILL.md): public behavior parity.
- [`R1 Rust style`](skills/py2rs-review-r1-rust-style/SKILL.md): Rust structure and maintainability.
- [`R2 error tracing`](skills/py2rs-review-r2-error-tracing/SKILL.md): errors, logs, context and redaction.
- [`R3 IO concurrency`](skills/py2rs-review-r3-io-concurrency/SKILL.md): blocking IO, async boundaries and runtime ergonomics.
- [`R4 algorithm complexity`](skills/py2rs-review-r4-algo-complexity/SKILL.md): algorithmic claims and benchmark evidence.
- [`R5 architecture`](skills/py2rs-review-r5-architecture/SKILL.md): ownership, APIs, storage and data boundaries.
- [`R6 ergonomics`](skills/py2rs-review-r6-ergonomics/SKILL.md): CLI, UX, recovery and operations.

See [`docs/review-gates.md`](docs/review-gates.md).

## Where The Ideas Come From

py2rs combines:

- **teach-style progression**: mission-grounded work, resources before memory, durable records, notes, small units and feedback loops.
- **rewrite discipline**: behavior before architecture, reversible state, manifest-driven progress and independent review gates.
- **project-specific adaptation**: each real project keeps its accepted seam instead of adopting a fixed py2rs directory layout.

The source skill is included at [`skills/foundations/teach`](skills/foundations/teach/SKILL.md). It comes from Matt Pocock's [`mattpocock/skills`](https://github.com/mattpocock/skills) repository; see [`THIRD_PARTY.md`](THIRD_PARTY.md).

## Practice Skills

- [`mvsep-rs`](skills/practices/mvsep-rs-rewrite/SKILL.md): Tauri backend facade rewrite for [`AntheaLaffy/mvsep-rs`](https://github.com/AntheaLaffy/mvsep-rs).
- [`Vocal2Midi / v2m`](skills/practices/vocal2midi-rs-rewrite/SKILL.md): dependency-heavy Python rewrite for [`AntheaLaffy/Vocal2Midi-for-linux`](https://github.com/AntheaLaffy/Vocal2Midi-for-linux).

These are examples of project-specific skills created from the same architecture. They are not universal templates.

## Docs

English:

- [`docs/installation.md`](docs/installation.md)
- [`docs/philosophy.md`](docs/philosophy.md)
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/review-gates.md`](docs/review-gates.md)
- [`docs/usage.md`](docs/usage.md)
- [`docs/practices.md`](docs/practices.md)

Chinese:

- [`docs/philosophy.zh.md`](docs/philosophy.zh.md)
- [`docs/architecture.zh.md`](docs/architecture.zh.md)
- [`docs/review-gates.zh.md`](docs/review-gates.zh.md)
- [`docs/usage.zh.md`](docs/usage.zh.md)
- [`docs/practices.zh.md`](docs/practices.zh.md)

## License

MIT. See [`LICENSE`](LICENSE).
