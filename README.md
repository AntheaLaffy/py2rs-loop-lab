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
4. Initialize the rewrite workspace: mission, resources, notes, records, manifest, rewrite/framework preferences, dependency source policy and granularity profile.
5. Enter the loop: research crate capability paths, align dependencies, implement one unit, run R0, then add R1-R6 gates as needed.

The core output is not Rust code. The core output is a project-specific loop that can keep producing reviewed Rust code.

## Current Architecture

The architecture separates two decisions that are easy to conflate:

- **Dependency and rewrite policy**: initialization records rewrite depth, relevant framework preferences, crate reconnaissance mode and the project's own crates.io proxy in `NOTES.md`. When a capability is actually needed, Context7, registry search and the Cargo graph determine whether to reuse a crate, call a lower backend, add an adapter or hand-write the semantic difference.
- **Project skill execution mode**: each coordinator, dependency bootstrap, writer or review role independently selects `prompt` or `scaffold`. Use `prompt` while the workflow still needs creative iteration; switch to `scaffold` only after its inputs, outputs and failure paths are stable and validated, so scripts can own deterministic operations.

The two variants may replace each other as the project matures, but exactly one variant per role may remain under agent discovery roots. Archive the counterpart outside those roots, write the new state back to `NOTES.md`, then start a fresh session. This preserves freedom for architectural judgment without spending prompt tokens on mechanics that have already stabilized.

## Stateful Incremental Repository Architecture

py2rs does not rely on one long prompt to finish a migration. It turns the migration into a stateful, resumable, reviewable and rollbackable repository workflow. Each AI session should read the durable state instead of relying on chat memory.

- `mission`: records why the rewrite exists, what success means and which behaviors or constraints must not be lost
- `resources`: stores source-of-truth docs, existing tests, dependency source snapshots, protocol notes and trusted references so AI does not rewrite from memory
- `notes`: captures user preferences, including the rewrite-depth and framework profile, plus project constraints and temporary observations
- `records`: preserves non-obvious decisions, lessons, behavior differences, dependency tradeoffs and review conclusions for later sessions
- `manifest` / checklist: records each migration unit's state, owner, target owner, verification commands, rollback route and required review gates; this is the rewrite control plane
- crate reconnaissance: searches by capability, uses Context7 for focused API/feature docs, and follows Cargo dependencies before a high-level crate is rejected or behavior is hand-written
- dependency alignment: applies the recorded rewrite/framework preferences while mapping Python dependencies, Rust crates, compatibility adapters and hand-written replacements by capability coverage
- bootstrap: proves the chosen seam handles parameters, return values, errors, logs, tests and rollback before business logic is migrated
- review evidence: moves a unit from "reimplemented" toward "verified" or "promoted" only after R0 behavior parity and any required R1-R6 reviews

The point of this architecture is that the system stays runnable, testable and rollbackable at every migration state. Even if a new AI session takes over, it can continue from the repository's mission, records, manifest and reviews instead of guessing project state.

### Initialization Preferences And Dependency Timing

The initialization architecture separates user intent from migration state. A two-stage interview first records the overall rewrite strategy, then asks only about framework categories detected in the project. It also records whether crate reconnaissance is agent-run, manual or disabled, plus any crates.io proxy. These durable choices live in `NOTES.md`; migration ownership, verification and rollback remain in the manifest.

Initialization does not preinstall speculative crates. Agent reconnaissance runs in a fresh context and gives dependency alignment a compact evidence report; manual mode lets a Rust-ecosystem expert provide the same evidence. Reconnaissance can be disabled to save tokens, but py2rs then warns that the user must understand or manually research crates.io, docs.rs and feature/dependency paths. Only after alignment are required crates added and locked.

See [Architecture](docs/architecture.md#project-skill-scaffolding) for the mode lifecycle and [Usage](docs/usage.md#switch-project-skill-modes) for the operational sequence.

## What The Rust Output Should Look Like

After using these skills to migrate Python to Rust, the first-stage Rust code is not meant to be a line-by-line Python translation, and it is not meant to be maximally elegant or idiomatic Rust immediately. The first target is narrower and more important: a strictly behavior-compatible Rust version backed by broad, complete tests.

The migrated Rust code should prove:

- public behavior matches the original Python version
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
- [`py2rs-runtime`](skills/py2rs-runtime/SKILL.md): rewrite preferences, control plane, manifest, state model, shards and granularity.
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
