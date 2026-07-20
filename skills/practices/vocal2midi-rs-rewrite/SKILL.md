---
name: vocal2midi-rs-rewrite
description: Coordinate the Vocal2Midi Python-to-Rust rewrite. Use when the user asks to continue, plan, route, re-cut, shard, implement, audit, promote, choose serial or coordinated-parallel execution, or select the next migration unit; when shared Burn gaps, dependency source expansion, capability coverage, or workflow may change the manifest inventory.
---

# Vocal2Midi Rust Rewrite

Drive the project-specific rewrite loop for Vocal2Midi. Treat
`rewrite-in-rust/` as the durable control plane.

## Start Here

1. Confirm the current workspace is the Vocal2Midi repository.
2. Read these before making decisions:
   - `rewrite-in-rust/README.md`
   - `rewrite-in-rust/manifest.yaml`
   - `rewrite-in-rust/resources.md`
   - `rewrite-in-rust/notes.md`
   - `rewrite-in-rust/reference/glossary.md`
   - `rewrite-in-rust/records/`
   - `docs/architecture.md`
   - `docs/contributing.md`
3. Read source files and tests named by the selected unit.
4. If the task is dependency or seam setup, use `vocal2midi-rs-dep-bootstrap`.
5. If the task is implementation, use `vocal2midi-rs-unit-writer`.
6. If the task is review-only, use `vocal2midi-rs-review-gate`.

Completion criterion: the selected path is grounded in manifest state and source
truth, not memory.

## Discovery First

Vocal2Midi is a cross-language dependency rewrite, not a mostly-Rust backend
rewrite like mvsep-rs. Treat `manifest.yaml` units as a provisional inventory.

Before choosing implementation work, check whether dependency expansion could
change the unit boundary:

- imports cross heavy Python package, native, FFI, model runtime, or vendored
  source boundaries
- the unit depends on first-layer direct Python dependency behavior that should
  be read from `third_party/` before implementation
- second-layer or deeper dependency behavior appears relevant, but no
  public-seam call path evidence has been recorded yet
- the planned unit mixes several separately verifiable capabilities
- a direct crate replacement looks broader than a narrow Rust implementation
- a Rust crate covers useful lower-level behavior but differs from Python at the
  public API, resolver, constructor, formatting, or error-projection layer
- a low-level native/compiler/runtime difference is being treated as behavior
  without proof that it reaches public outputs, memory/ABI contracts,
  persistence, security, or model/numeric correctness
- fixtures or shared Rust data structures are missing
- rollback is unclear after dependency expansion

If any signal is present, route to `vocal2midi-rs-dep-bootstrap` before writer
work. Re-cut planned units when that creates a smaller or more verifiable path.
Do not treat dependency alignment as a binary choice between perfect crate
parity and fully hand-written Rust. Dependency reuse and wheel rebuilding are
complementary. The preferred decision paths are:

1. direct crate coverage when fixtures prove it;
2. partial crate reuse plus a fixture-bound semantic-delta adapter when Python
   source explains the semantic gaps;
3. narrow hand-written Rust for semantic gaps or capabilities the crate cannot
   safely own;
4. full hand-written replacement when it is the smaller or safer verified path,
   with a recorded tradeoff explaining why crate reuse plus adapter is worse.

Completion criterion: continuing with the current unit boundary is justified, or
the plan is routed to dependency/bootstrap discovery.

## Unit Selection

- If the user names a unit, work on that unit.
- Otherwise select the first manifest unit that is not `verified`, `promoted`,
  or `optimized`.
- A selected unit may still be split, merged, renamed, deferred, or replaced
  after dependency discovery.
- Manifest sharding does not imply parallel writers. Keep one unit active and
  process model shards serially by default; this avoids repeated model context,
  Cargo contention and conflicting dependency implementations.
- Use coordinated parallel work only after explicit user opt-in, stable disjoint
  shard paths, canonical shared prerequisites, an assigned coordinator, and a
  serialized Cargo build queue. Otherwise remain serial.
- Do not skip the R0 behavior gate.
- Do not promote a unit without its R0 behavior evidence, required reviews, and a
  rollback route.

Completion criterion: the next unit and route are explicit.

## Behavior Verification Target

Every unit uses Python/legacy behavior at a named public or application seam as
its oracle. Record the observable inputs, outputs, errors, state changes and
handoffs before writer work. Comparison is exact unless an existing public
contract or explicit pre-implementation user decision records a model or numeric
tolerance.

For deep inference work, choose a seam that exposes model/config/weight loading,
codec roundtrips, tensor shape/dtype/layout handoff, errors and application
workflow without requiring framework internals to become migration targets. If
the current unit cannot support independent Python/Rust comparison, move the
seam outward, re-cut the unit, or keep the capability legacy-owned. Compilation
or canonical Rust-to-Rust contracts cannot replace this behavior evidence.

## Source Boundary

Borrow from py2rs:

- behavior-first migration
- reversible state
- manifest-driven progress
- writer/reviewer separation
- one R0 behavior-parity gate before promotion

Borrow from teach:

- mission-grounded work
- resources before memory
- durable notes, references, and records
- minimum scoped progression

Do not borrow a fixed py2rs architecture. No PyO3, runtime router, CLI bridge,
or subprocess bridge is introduced unless the unit's record explains why it
fits Vocal2Midi.

## Rewrite Loop

1. Ground in state: read manifest, resources, records, selected sources, and
   existing tests.
2. Run the discovery check and re-cut provisional units when needed.
3. Define the unit's public boundary, current owner, target owner,
   `behavior_verification`, verification command, and rollback route.
4. Check the canonical shared dependency registry, then ensure
   dependency/bootstrap records exist before implementation when the unit needs
   new crates, fixtures, hand-written Burn gaps, or bridge/seam decisions.
5. Add Python/Rust behavior-parity fixtures at the declared seam before changing
   production paths.
6. Implement behind the accepted boundary through `vocal2midi-rs-unit-writer`.
7. Mark implemented-but-unreviewed work as `reimplemented`, not `verified`.
8. Run or request the R0 behavior role through `vocal2midi-rs-review-gate`, then
   the other required review roles.
9. Promote only after reviews pass and rollback remains clear.
10. Record reusable lessons in `rewrite-in-rust/records/`.

Completion criterion: manifest state reflects reality and the next action is
obvious.

## Non-Negotiables

- Python/legacy public behavior is the oracle for every unit. A unit without an
  independently comparable seam remains legacy-owned or is re-cut before writer work.
- GUI, Flask/Web handlers, and model inference remain legacy-owned unless a unit
  explicitly changes that boundary.
- Runtime/control-plane code must not contain business logic.
- A writer must not review its own work.
- A reviewer must not patch production code.
- Dependency alignment is by capability coverage, not package-name matching;
  partial crate coverage plus a Python-source-guided adapter is valid when it is
  smaller and more verifiable than fully hand-writing the lower layer.
- Fewer Rust dependencies is not a success metric. Challenge unnecessary
  hand-written rewrites when a maintained crate can safely own a stable lower
  layer, and also allow full hand-written replacement when the dependency
  tradeoff is recorded and fixture-backed.
- First-layer direct Python dependency sources are the normal local reference
  corpus. Second-layer or deeper source expansion requires public-seam call path
  evidence; lockfile transitivity alone is not enough.
- Do not turn low-level native/compiler/runtime details into rewrite work unless
  they affect public behavior, memory/ABI contracts, persistence, security, or
  model/numeric correctness.
- The initial module list is temporary; do not preserve it when dependency
  expansion proves a better boundary.
- Shared Burn gaps, adapters, generated sources and fixture harnesses have one
  canonical project path and prerequisite owner. Never reimplement them under a
  second model shard.
- `/tmp` and agent-private dependency copies are disposable research only and
  cannot be consumed by another unit.
- Only a coordinator may modify shared Cargo manifests/lockfiles or schedule
  competing builds in coordinated parallel mode.
- Use uv Python 3.12.x for Python checks; do not use the system `python`.

## Completion Response

Name the selected unit, route taken, manifest state changes, files changed, checks
run, and remaining review roles.
