# Practices

[中文版本](practices.zh.md)

This repository includes two concrete practice families built from the py2rs discipline.

## mvsep-rs

Project: [`AntheaLaffy/mvsep-rs`](https://github.com/AntheaLaffy/mvsep-rs)

Skills:

- `skills/practices/mvsep-rs-rewrite`
- `skills/practices/mvsep-rs-batch-writer`
- `skills/practices/mvsep-rs-review-gate`

mvsep-rs borrows py2rs discipline but not py2rs architecture.

Key shape:

- Tauri command -> backend facade seam.
- Existing command names and progress events are preserved.
- Writer and reviewer roles are separated.
- Behavior review is the first gate.
- No Python router and no forced `py/` / `rs/` layout.

This is an example of py2rs as migration discipline rather than fixed implementation template.

## Vocal2Midi / v2m

Project: [`AntheaLaffy/Vocal2Midi-for-linux`](https://github.com/AntheaLaffy/Vocal2Midi-for-linux)

Skills:

- `skills/practices/vocal2midi-rs-rewrite`
- `skills/practices/vocal2midi-rs-dep-bootstrap`
- `skills/practices/vocal2midi-rs-unit-writer`
- `skills/practices/vocal2midi-rs-review-gate`

Vocal2Midi is a Python dependency-heavy rewrite.

Key shape:

- Large third-party source corpus is used as local reference material.
- First-layer direct Python dependencies are useful for high-level wheel rebuilding.
- Second-layer or deeper dependencies require public-seam call-path evidence.
- Rust crates and hand-written replacements are complementary.
- Model manifests may be sharded, but one serial writer is the default; parallel work requires a coordinator for canonical dependencies, shared Cargo files and the build queue.
- When several models need missing Burn functionality, create one canonical project prerequisite instead of mutually invisible long-lived copies under `/tmp`.
- Normal legacy-facing units keep Python behavior parity. The deep inference chain may declare `rust_compatibility` at its entry and target already behavior-verified Rust tensor/codec/artifact contracts.
- Low-level native/compiler/runtime details are ignored unless they affect public behavior, memory/ABI, persistence, security or model/numeric correctness.

This is an example of py2rs applied to a glue-language project with heavy dependency alignment.
