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
4. Initialize the rewrite workspace: mission, resources, notes, records, manifest, dependency source policy and granularity profile.
5. Enter the loop: align dependencies, implement one unit, run R0, then add R1-R6 gates as needed.

The core output is not Rust code. The core output is a project-specific loop that can keep producing reviewed Rust code.

## Core Skills

- [`py2rs`](skills/py2rs/SKILL.md): overall rewrite discipline and routing.
- [`py2rs-runtime`](skills/py2rs-runtime/SKILL.md): control plane, manifest, state model, shards and granularity.
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

The source skill is included at [`skills/foundations/teach`](skills/foundations/teach/SKILL.md).

## Practice Skills

- [`mvsep-rs`](skills/practices/mvsep-rs-rewrite/SKILL.md): Tauri backend facade rewrite.
- [`Vocal2Midi / v2m`](skills/practices/vocal2midi-rs-rewrite/SKILL.md): dependency-heavy Python rewrite.

These are examples of project-specific skills created from the same architecture. They are not universal templates.

## Docs

English:

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
