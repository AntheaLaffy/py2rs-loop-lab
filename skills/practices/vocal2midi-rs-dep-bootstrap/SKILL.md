---
name: vocal2midi-rs-dep-bootstrap
description: Expand first-layer Python dependency sources, justify targeted transitive source expansion, and align capability coverage, Rust crate reuse, compatibility adapters, hand-written replacements, fixtures, and seam/bootstrap records for Vocal2Midi. Use before implementation when imports, native/FFI sources, dependency mismatch, fixture strategy, low-level boundary, or manifest re-cut decisions affect a migration unit.
---

# Vocal2Midi Rust Dependency And Bootstrap

Prepare or re-cut migration units so implementation can start without guessing
about dependencies, fixtures, or seam shape.

## Required Context

Read these first:

- `rewrite-in-rust/README.md`
- `rewrite-in-rust/manifest.yaml`
- `rewrite-in-rust/resources.md`
- `rewrite-in-rust/notes.md`
- `rewrite-in-rust/reference/glossary.md`
- `pyproject.toml`
- `uv.lock`
- `requirements.txt`, `requirements-linux.txt`, `requirements-web.txt`
- `third_party/README.md`
- `third_party/sources/manifest.json`
- `third_party/sources/MISSING_SOURCES.md`
- `third_party/native_sources/manifest.json`
- `third_party/source_audit.json`
- Source refs and verification notes for the selected unit

Completion criterion: every dependency claim is grounded in a file or marked as
an assumption.

## Dependency Expansion Pass

Vocal2Midi intentionally keeps a large local third-party source corpus. Treat
first-layer direct Python dependency source snapshots as the normal high-level
reference material for dependency alignment and wheel rebuilding. They are
reference sources, not automatic rewrite targets.

Start from the selected Python source refs, then search first-layer direct
dependency sources before going deeper. Second-layer or deeper transitive
dependency source expansion is allowed only when there is public-seam call path
evidence that the selected behavior depends on a specific transitive
implementation.

Inspect:

- project imports and local helper calls
- Python package requirements and lockfile entries
- `third_party/sources/<package-version>/` for Python source distributions
- `third_party/upstream_sources/<package-version>/` for packages without sdists
- `third_party/native_sources/<library-version>/` for native/FFI source trees
- `third_party/cargo_vendor/<source-path>/` for Rust-backed Python package crates
- existing tests, fixtures, and public caller expectations

For second-layer or deeper source, record the exact call path from the
Vocal2Midi public behavior boundary to the transitive symbol, function, class,
schema, native wrapper, data table, ABI contract, persistence format, model
payload, cache key, or error projection. A lockfile dependency edge alone is not
evidence.

Stop when the unit can name its behavior, dependencies, fixtures, rollback, and
kept-legacy capabilities. Do not expand just to map the whole Python ecosystem.

Completion criterion: the unit boundary is confirmed or a re-cut is proposed.

## Capability Coverage

Decide by capability, not by Python package name.

- Pure validation, parsing, formatting, alignment, and deterministic algorithms
  can be hand-written in Rust against fixtures.
- A Rust crate does not need to be a perfect drop-in to be useful. When a crate
  covers a stable lower layer, such as tokenization, parsing events, IO,
  Unicode tables, numeric primitives, or data structures, prefer reusing that
  layer and writing a small compatibility adapter for the Python-specific
  behavior it does not cover.
- If Python source for the legacy behavior is available in project files,
  `third_party/`, or another recorded source snapshot, use it to implement only
  the observed semantic delta between the Rust crate and Python behavior. Do not
  reject a crate merely because its high-level API disagrees with the Python
  package.
- Heavy model inference, ONNX Runtime, Qwen ASR, PyQt, and Flask remain
  legacy-owned unless the manifest changes.
- Local vendored Python, Rust, and native sources may be used as references.
- Use `third_party/source_audit.json` and the source manifests to justify the
  exact reference source path used for a compatibility adapter or hand-written
  replacement.
- A direct crate replacement is optional. Fewer Rust dependencies is not a
  success metric. Prefer maintained crates for stable lower-layer behavior when
  fixtures prove the fit, then hand-write the Python compatibility delta.
- Full hand-written replacement is valid when it is smaller, safer, or easier to
  verify and roll back than crate reuse plus adapter. Record the tradeoff:
  semantic mismatch, licensing/security/build/runtime/portability/maintenance
  risk, excessive integration cost, or a capability so narrow that a crate adds
  more surface than it removes.
- If a planned unit is too broad after expansion, split it. If several units
  share the same required Rust data model or fixture harness, merge or extract a
  prerequisite unit.
- Do not install or add bridge dependencies that the selected seam does not need.

Completion criterion: kept-legacy capabilities and Rust-covered capabilities are
both named.

## Native And Low-Level Boundary

Vocal2Midi uses Python as a glue layer over native and model ecosystems. Do not
turn low-level compiler/runtime/native-library details into migration work just
because they are visible in dependency source.

In scope when they affect the selected public behavior:

- parser state, tokenizer output, tensor shape/dtype policy, model runner
  payloads, serialization schema, cache keys, business DTOs, user-visible error
  projection, and Unicode normalization output

Ignore by default:

- NaN bit payloads, compiler macros, native struct padding, allocator behavior,
  SIMD branches, internal Unicode table layout, BLAS/CUDA kernel choice, and
  other implementation details that do not reach the public seam

Investigate low-level differences only when they can affect public outputs,
errors, serialization, persistence, memory/ABI contracts, security, or
model/numeric correctness.

## Seam Default

The default seam is an independent Rust library plus fixtures under
`rewrite-in-rust/rust/`. Do not introduce PyO3, CLI/subprocess, HTTP, or a Python
runtime router during bootstrap unless the unit needs runtime promotion planning.

If a non-default seam is needed, record:

- seam kind
- public payload shape
- error mapping
- trace/log context
- repeated-call behavior
- rollback path

Completion criterion: the next writer can implement without choosing a new
architecture.

## Output

Write or update:

- `rewrite-in-rust/dependencies/<unit-id>.yaml`
- `rewrite-in-rust/bootstrap/<unit-id>.md` when a seam or fixture harness is
  proven
- `rewrite-in-rust/records/NNNN-*.md` when the decision changes a boundary or
  teaches a reusable lesson
- `rewrite-in-rust/manifest.yaml` when dependency discovery confirms, splits,
  merges, replaces, or defers provisional units

Use this dependency record shape:

```yaml
unit: unit_id
status: planned | active | done | blocked
capabilities:
  capability_name:
    legacy: "Python source or dependency"
    rust: "crate or narrow implementation"
    reason: "why this covers behavior"
seam:
  kind: library | ffi | cli | service | pipeline
  default_owner: legacy
  bridge_dependencies: []
fixtures:
  required:
    - "fixture or golden output needed before writer starts"
crate_reuse:
  candidates:
    - crate: "crate-name"
      covered_capabilities:
        - "what the crate can own safely"
      gaps:
        - "Python behavior not covered by crate"
      adapter_plan: "how the unit will patch the gaps using legacy source/fixtures"
      decision: use | reject | defer
dependency_strategy:
  stance: "reuse stable crate-owned lower layers; hand-write compatibility gaps or full replacement when tradeoff says so"
  not_goal: "minimize dependency count"
  full_handwritten_allowed_when:
    - "crate semantic mismatch is larger than the selected capability"
    - "licensing, security, build, runtime, portability, or maintenance risk is unacceptable"
    - "a narrow fixture-backed implementation is smaller and easier to roll back"
source_expansion:
  first_layer_reference:
    status: indexed | missing | partial
    source_manifest: "third_party/sources/manifest.json"
  targeted_deep_expansion:
    used: true | false
    proof:
      - "public seam -> first-layer dependency -> transitive symbol/function/schema"
    rejected:
      - "lockfile transitivity without public-seam evidence"
low_level_boundary:
  ignored:
    - "native/compiler/runtime detail that does not affect public seam"
  investigated:
    - "public behavior, memory/ABI, persistence, security, or model/numeric correctness risk"
inventory_impact:
  decision: confirmed | split | merged | renamed | deferred | replaced
  reason: "why the manifest unit boundary did or did not change"
hand_written_replacements:
  - capability: "behavior implemented directly in Rust instead of by crate"
    reference_sources:
      - "third_party/sources/package-version or native/upstream/cargo source path"
    reason: "why this is better than crate reuse plus an adapter"
legacy_kept:
  - capability: "capability retained in Python"
    reason: "why not moving now"
verification:
  - "copyable command"
```

Completion criterion: output records are specific enough for
`vocal2midi-rs-unit-writer`, or the manifest has been re-cut before writer work.

## Checks

Run non-mutating checks where useful:

```bash
cargo test --manifest-path rewrite-in-rust/rust/Cargo.toml
uv run python scripts/audit_vendored_sources.py
```

If a required command fails because the environment is missing or blocked, report
the exact blocker and do not pretend dependency alignment is complete.

Also check:

- first-layer direct dependency references are indexed or the missing source is
  recorded in `third_party/sources/MISSING_SOURCES.md`
- any second-layer or deeper source expansion has call-path evidence
- low-level native/compiler/runtime differences are ignored unless they affect
  the selected public seam or memory/ABI, persistence, security, or model/numeric
  correctness
