# Execution Policy

Read this reference during repository initialization when manifest sharding,
multiple AI sessions, shared Rust dependencies, hand-written crate gaps, or
Cargo build contention are relevant.

## Contents

- [Separate Partitioning From Execution](#separate-partitioning-from-execution)
- [Control-Plane Schema](#control-plane-schema)
- [Canonical Shared Dependencies](#canonical-shared-dependencies)
- [Parallel Admission Gate](#parallel-admission-gate)
- [Coordinator Authority](#coordinator-authority)
- [Cargo Build Coordination](#cargo-build-coordination)
- [Temporary Sources](#temporary-sources)
- [Exit Criteria](#exit-criteria)

## Separate Partitioning From Execution

Manifest sharding organizes a large rewrite. It does not authorize concurrent
writers. Shards remain useful under serial execution because they expose stable
ownership, prerequisite order, verification, rollback, and review scope without
forcing one session to load the whole inventory.

Default to `serial`, including for sharded manifests. Parallel writers consume
extra agent context, repeat project discovery, contend for Cargo locks and build
artifacts, and increase integration work. Use `coordinated_parallel` only after
the user explicitly accepts that cost and the admission gate below passes.

## Control-Plane Schema

```yaml
granularity_profile:
  manifest_partitioning: shard_when_stable # single_manifest | shard_when_stable | sharded

execution_policy:
  mode: serial # serial | coordinated_parallel
  source: default # user | default
  coordinator_required_for_parallel: true
  shared_dependency_registry: manifest/shared-dependencies.yaml
  cargo_build_policy: serialized
  temporary_dependency_policy: disposable_only
  coordinator:
    status: not_required # not_required | assigned
    owner: null
```

For serial execution, process shards in dependency order and keep only one
writer unit active. For coordinated parallel execution, add durable worker
assignments with shard ids, allowed paths, excluded shared files, and expiry or
completion state.

## Canonical Shared Dependencies

Create one project-controlled registry when two or more units may share a crate,
fork, adapter, generated source tree, fixture harness, or hand-written lower
layer. Check it before researching or implementing a dependency.

```yaml
version: 1
shared_dependencies:
  - id: burn-missing-capability
    kind: handwritten_crate # crate | fork | adapter | handwritten_crate | generated
    capability: "Burn capability not covered by the selected upstream version"
    canonical_path: rust/crates/burn-missing-capability
    owner_shard: shared_dependencies
    consumers:
      - model_a
      - model_b
    status: verified # planned | active | reimplemented | verified
    manifests:
      - rust/Cargo.toml
      - rust/Cargo.lock
    build_evidence:
      - "cargo test -p burn-missing-capability"
```

When an ecosystem crate is incomplete and a shared capability must be written
by hand, make it a prerequisite unit or shard before downstream writers start.
Do not let multiple workers independently fill the same gap. Every consumer
uses the canonical project path and recorded API.

## Parallel Admission Gate

Permit `coordinated_parallel` only when all are true:

- the user explicitly selects it after being warned about extra token, compile,
  and integration cost;
- shard ownership and cross-shard contracts are stable;
- shared prerequisites and canonical dependency paths are already recorded;
- a coordinator is assigned and is the sole authority for shared files;
- Cargo builds can be queued instead of competing for one target directory;
- the expected wall-clock gain exceeds agent, duplicated build, and merge cost.

Otherwise keep `serial`. More Codex windows are not evidence of greater rewrite
throughput.

## Coordinator Authority

In coordinated parallel mode, only the coordinator may:

- assign or close worker shards;
- edit the root manifest, cross-shard dependency graph, shared dependency
  registry, workspace membership, shared `Cargo.toml`, `Cargo.lock`, or patch
  configuration;
- accept a new vendored, forked, generated, or hand-written dependency path;
- schedule Cargo build/test slots and record reusable build evidence;
- resolve overlapping changes and tell workers when canonical shared code has
  changed.

Workers may edit only their assigned paths. A worker that needs a shared
dependency change writes a request and stops dependent implementation until the
coordinator applies or rejects it. It must not create a competing dependency
copy to continue locally.

## Cargo Build Coordination

Cargo processes can wait on package-cache, lockfile, or target-directory locks,
while separate target directories duplicate compilation and disk use. Default
to one coordinator-serialized build queue for commands that compile or mutate
shared workspace state.

An isolated `CARGO_TARGET_DIR` is an explicit exception, not the default. Record
its duplicated cost and require a final integration build against the canonical
workspace and target policy before accepting evidence.

## Temporary Sources

`/tmp` and agent-private directories are disposable research locations only.
They cannot be named as a canonical dependency, manifest path, build input, or
handoff artifact. Before another unit consumes useful work, move it into the
project-controlled canonical root, record its origin/license when applicable,
add it to the shared dependency registry, and verify it there.

## Exit Criteria

- Manifest partitioning and execution mode are recorded separately.
- Serial is the default and sharded serial execution has a dependency order.
- Parallel mode has one assigned coordinator and no worker-owned shared files.
- Shared hand-written capabilities have one canonical project path and owner.
- Cargo compilation is serialized or an isolated-target exception is recorded
  with a final canonical integration build.
- No durable dependency or evidence points to `/tmp` or an agent-private copy.
