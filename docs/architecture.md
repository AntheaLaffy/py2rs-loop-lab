# Architecture

[中文版本](architecture.zh.md)

py2rs does not require one fixed directory layout. It defines a control plane and review discipline for incremental rewrites.

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

## Granularity Profile

The rewrite should ask the user how fine the units should be during initialization.

Available vocabulary:

- `coarse`: fewer units and fewer reviews; useful for low-risk helpers or cost-sensitive work.
- `balanced`: default; independently verifiable units without forcing every helper into its own review cycle.
- `fine`: useful for public payloads, parsers, data structures, error projection, persistence, model IO and dependency compatibility layers.
- `ultra_fine`: exceptional; useful when ABI, memory, numeric/model correctness or rollback precision matters more than cost.

Finer units cost more review rounds and tokens. They also reduce hallucination risk, dead-code risk and behavioral drift.

## Dependency Alignment

Dependencies are aligned by capability, not by package name.

Allowed paths:

- direct crate coverage when fixtures prove behavior
- crate-owned stable lower layer plus a compatibility adapter
- narrow hand-written replacement for semantic gaps
- full hand-written replacement when it is smaller, safer or easier to verify than crate reuse plus adapter

Fewer Rust dependencies is not a success metric. Full wheel rebuilding is not a default preference either. The selected path must be recorded as a tradeoff.

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
