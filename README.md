# py2rs-loop-lab

> A loop engineering skill lab for controlled Python-to-Rust and legacy-to-Rust rewrites.

[中文 README](README.zh.md)

`py2rs-loop-lab` is a collection of Codex/Claude skills for turning Python-to-Rust or legacy-to-Rust rewrites into a runnable, reviewable and rollbackable engineering loop.

This project is not an anti-loop-engineering manifesto. It is a loop engineering project. Its position is narrower: use it when you want constrained engineering progress, behavior gates, dependency alignment, review reports and durable migration state. Do not use it when your primary goal is open-ended creative exploration, because this workflow intentionally reduces creative freedom in exchange for quality control.

## Positioning

py2rs assumes that AI can do a lot of migration work: read code, write code, produce fixtures, run checks, write review reports and maintain migration state.

The human still owns the important constraints:

- why the project is being rewritten
- which public behaviors cannot change
- which architecture seam is accepted
- how small migration units should be
- where dependency reuse, adapters or hand-written replacements are appropriate
- which project-specific practices should become reusable skills

In short: py2rs is loop engineering with explicit human constraints.

## Repository Contents

Core py2rs skills:

- [`skills/py2rs`](skills/py2rs/SKILL.md): the overall rewrite discipline and routing skill.
- [`skills/py2rs-runtime`](skills/py2rs-runtime/SKILL.md): manifest, control plane, state model, manifest shards and granularity profile.
- [`skills/py2rs-dep-align`](skills/py2rs-dep-align/SKILL.md): capability-based dependency alignment, source expansion and crate/adapter/hand-written tradeoffs.
- [`skills/py2rs-env-bootstrap`](skills/py2rs-env-bootstrap/SKILL.md): seam bootstrap before business migration.

Review gate skills:

- [`R0 behavior`](skills/py2rs-review-r0-behavior/SKILL.md): public behavior parity before any promotion.
- [`R1 Rust style`](skills/py2rs-review-r1-rust-style/SKILL.md): Rust module shape, ownership, visibility, warnings and maintainability.
- [`R2 error tracing`](skills/py2rs-review-r2-error-tracing/SKILL.md): structured errors, logs, context and redaction.
- [`R3 IO concurrency`](skills/py2rs-review-r3-io-concurrency/SKILL.md): blocking IO, async boundaries, cancellation, retries and runtime ergonomics.
- [`R4 algorithm complexity`](skills/py2rs-review-r4-algo-complexity/SKILL.md): algorithmic changes, complexity claims and benchmark evidence.
- [`R5 architecture`](skills/py2rs-review-r5-architecture/SKILL.md): data ownership, API boundaries, canonical storage and module depth.
- [`R6 ergonomics`](skills/py2rs-review-r6-ergonomics/SKILL.md): product, CLI, UX and operational ergonomics.

Practice skills:

- [`mvsep-rs`](skills/practices/mvsep-rs-rewrite/SKILL.md): a Tauri backend facade rewrite practice.
- [`Vocal2Midi / v2m`](skills/practices/vocal2midi-rs-rewrite/SKILL.md): a dependency-heavy Python rewrite practice.

## Documentation

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

## Core Ideas

1. **Project truth first**: read the project before applying a template.
2. **Granularity calibration**: agree with the user on unit size, review cost and quality targets before cutting the manifest.
3. **Capability coverage, not package parity**: dependencies are aligned by behavior and capability, not by one-to-one package names.
4. **Bounded source expansion**: first-layer direct Python dependencies can be local reference material; deeper dependencies require public-seam call-path evidence.
5. **Writer/reviewer separation**: the agent that writes the unit does not review it.
6. **R0 before elegance**: behavior parity comes before Rust style or optimization.
7. **Project-specific skills**: py2rs is a discipline, not a mandatory architecture.

## Quick Start

1. Read [`skills/py2rs/SKILL.md`](skills/py2rs/SKILL.md).
2. Set up or reuse a manifest/control plane with [`skills/py2rs-runtime/SKILL.md`](skills/py2rs-runtime/SKILL.md).
3. Calibrate the migration unit granularity with the user.
4. Run dependency alignment with [`skills/py2rs-dep-align/SKILL.md`](skills/py2rs-dep-align/SKILL.md).
5. Implement one confirmed unit with a writer role.
6. Run [`R0 behavior review`](skills/py2rs-review-r0-behavior/SKILL.md).
7. Add R1-R6 gates based on risk and promotion requirements.

## License

MIT. See [`LICENSE`](LICENSE).
