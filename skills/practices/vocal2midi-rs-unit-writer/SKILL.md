---
name: vocal2midi-rs-unit-writer
description: Implement exactly one confirmed Vocal2Midi Rust migration unit as the writer role. Use when dependency discovery has accepted the boundary, canonical dependencies, and legacy public behavior seam, and the user asks to add fixtures, port behavior, or prepare one unit for review. Do not use for review-only or shared dependency coordination requests.
---

# Vocal2Midi Rust Unit Writer

Implement one migration unit while preserving Python behavior and preparing the
work for independent review.

## Required Context

Read these before editing:

- `rewrite-in-rust/README.md`
- `rewrite-in-rust/manifest.yaml`
- `rewrite-in-rust/resources.md`
- `rewrite-in-rust/notes.md`
- `rewrite-in-rust/reference/glossary.md`
- relevant `rewrite-in-rust/dependencies/<unit-id>.yaml` if present
- relevant `rewrite-in-rust/bootstrap/<unit-id>.md` if present
- canonical shared dependency registry and execution policy if present
- the unit's `behavior_verification` and legacy seam evidence
- source refs named by the selected unit
- existing tests around the touched behavior

Completion criterion: the writer knows the public/application boundary,
behavior verification seam, fixture strategy, rollback route, and required reviews
before editing.

## Boundary Gate

The manifest inventory is provisional. Before editing, confirm one of these is
true:

- `rewrite-in-rust/dependencies/<unit-id>.yaml` confirms the current boundary
- the dependency record selects a Rust crate plus a semantic-delta adapter, names
  the crate-owned lower layer, and lists Python-specific gaps covered by
  fixtures
- the dependency record justifies a full hand-written replacement with a
  tradeoff, reference sources, and fixtures
- any second-layer or deeper dependency source used by the unit has public-seam
  call path evidence; lockfile transitivity alone is not enough
- the unit is pure stdlib/local behavior with no meaningful third-party/native
  dependency expansion
- the coordinator explicitly records why dependency bootstrap is unnecessary

If the unit touches unclear Python dependencies, native/FFI behavior, broad
package APIs, or missing fixtures, stop and route to
`vocal2midi-rs-dep-bootstrap`.

Completion criterion: the writer is not blindly implementing a temporary module
list entry.

## Writer Workflow

1. Select or confirm exactly one unit from `manifest.yaml`.
2. Confirm the boundary gate above.
3. If the unit is `planned`, mark it `active` only when implementation actually
   starts.
4. Shrink the work to one independently verifiable contract.
5. Add Python/Rust behavior-parity fixtures at the declared legacy public seam
   before routing changes.
6. Check and reuse canonical shared dependencies before adding local code. Reuse
   selected Rust crates where dependency/bootstrap proved a lower-layer
   capability match, and implement only the Python semantic gaps named in
   the dependency record. If the record chose full hand-written replacement,
   keep it inside the recorded capability and tradeoff.
7. Implement in `rewrite-in-rust/rust/` unless the manifest explicitly permits a
   production bridge.
8. Preserve Python/legacy public behavior at the declared seam, including
   observable tensor, codec, artifact and model-loading behavior when relevant.
9. Run the narrowest useful Rust test, then the behavior-parity checks named by
   the unit.
10. If Rust implementation exists but independent review is incomplete, mark the
   unit `reimplemented`, not `verified`.
11. Add a rewrite record when the work changes a boundary or reveals a reusable
   lesson.
12. Final response must request the required review roles.

Completion criterion: one unit is implemented or the blocker is concrete.

## Source Boundary

- Do not wire Rust into GUI, Web, CLI, or inference runtime paths unless the unit
  is explicitly in promotion planning.
- Do not add PyO3, CLI/subprocess, HTTP, or runtime router architecture as a
  shortcut.
- Do not hand-write lower-level dependency machinery when the accepted boundary
  already selected a Rust crate that covers it. Keep custom code focused on the
  Python semantic delta and fixture-bound projections.
- Do not chase low-level native/compiler/runtime details unless the dependency
  record shows they affect public outputs, memory/ABI contracts, persistence,
  security, or model/numeric correctness.
- Do not migrate model inference, ONNX Runtime ownership, Qwen ASR, PyQt, or
  Flask as part of a small library unit.
- Do not broaden a unit to nearby modules because they are convenient.
- Do not replace a failed parity check with a Rust-only oracle. Route the unit
  back for seam selection, re-cutting, deferral, or retained legacy ownership.
- Do not treat model-loading, codec, artifact or tensor handoff failures that
  cross the selected seam as irrelevant framework internals.
- Do not preserve an initial unit boundary after discovery shows it should be
  re-cut.
- Do not create a reusable dependency under `/tmp` or an agent-private path.
- Do not modify shared Cargo manifests/lockfiles or bypass the coordinator build
  queue in coordinated parallel mode; route the need back to dependency/bootstrap.

## State Rules

- `planned`: described but not started.
- `active`: writer has started implementation work.
- `reimplemented`: Rust path and fixtures exist; independent review incomplete.
- `verified`: required review reports passed; writer must not set this for its
  own work.
- `promoted`: Rust is runtime owner; requires explicit promotion work.
- `blocked`: cannot proceed without a concrete missing decision or dependency.

Completion criterion: manifest status is factual, never aspirational.

## Checks

Prefer focused commands:

```bash
cargo test --manifest-path rewrite-in-rust/rust/Cargo.toml <unit-filter>
```

Run broader checks when the touched behavior can affect callers:

```bash
cargo test --manifest-path rewrite-in-rust/rust/Cargo.toml
uv run pytest tests/test_web_api.py
```

If tests cannot run, state exactly why.

## Completion Response

List changed files, tests run, manifest state, residual risks, and required
review roles. Do not claim review success for your own patch.
