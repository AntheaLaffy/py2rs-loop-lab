---
name: "py2rs-runtime"
description: "[DRAFT] 初始化 py2rs 重写偏好并建立迁移控制面：维护 manifest/shards、迁移粒度、behavior-parity 或 Rust-compatibility oracle、审核批次、默认串行执行、协调式并行、canonical shared dependencies、Cargo build 调度、状态机、回滚和审计。"
---

# py2rs-runtime — 迁移控制面与可选路由层

本 skill 不再把 `runtime/router.py` 当成所有项目的强制架构。它负责建立迁移控制面：哪些单元存在、当前归谁、公共接口是什么、如何验证、如何回滚、如何审计状态变化。

## Start Here

1. 读取项目事实：mission、architecture、resources、notes、manifest、records、tests 或等价文件。
2. 确认项目已有 seam。如果已有稳定 facade/adapter/command/API boundary，优先沿用。
3. 初始化仓库时，询问或读取用户的 rewrite preferences，并把偏好写入 `NOTES.md`。
4. 项目事实、seam 和偏好稳定后，为固定操作创建项目专属 script-backed skills。
5. 初始化仓库或重切 manifest 前，询问或读取 granularity、verification oracle、review cadence、manifest partitioning 和 execution policy；默认串行。
6. 只有在 Python 进程仍是统一入口时，才创建 Python runtime router。
7. 若项目已有控制面，扩展它；不要另起一个与项目冲突的 py2rs manifest。

## Runtime Means Control Plane

py2rs runtime 可以表现为：

- Python `runtime/router.py`
- Rust trait/facade
- CLI dispatcher
- HTTP/service adapter
- Tauri command facade
- feature flag or config router
- batch pipeline stage registry

共同职责只有三件：

1. 读取迁移状态。
2. 把请求路由到 current owner 或 target owner。
3. 记录验证、回滚和审计信息。

控制面不写业务逻辑。

## Manifest Shape

优先采用项目现有 manifest。没有时使用最小通用形态：

```yaml
version: 1
project:
  mission_doc: docs/mission.md
  architecture_doc: docs/architecture/rewrite.md
  resources_doc: RESOURCES.md
  records_dir: rewrite-records/

granularity_profile:
  default_unit_size: balanced # coarse | balanced | fine | ultra_fine
  review_budget: behavior_first # behavior_first | full_gate | risk_based
  token_budget_policy: "User-approved tradeoff between review cost and quality."
  manifest_partitioning: shard_when_stable # single_manifest | shard_when_stable | sharded
  high_precision_domains: []
  coarse_allowed_domains: []

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

review_policy:
  cadence:
    mode: batch # per_unit | batch | end_of_scope
    units_per_review: 3 # 1 for per_unit; null for end_of_scope
    scope: manifest # manifest | shard | named:<scope-id>
    source: default # user | default
  risk_override: flush_batch # flush_batch | follow_cadence
  flush_triggers:
    - batch_full
    - scope_complete
    - before_promotion

status_values:
  - planned
  - active
  - reimplemented
  - verified
  - promoted
  - optimized
  - blocked

units:
  - id: example
    status: planned
    unit_size: balanced
    current_owner: legacy
    target_owner: rust
    public_interface_policy: "Preserve existing public behavior."
    verification_policy:
      mode: behavior_parity # behavior_parity | rust_compatibility
      oracle:
        kind: legacy_public_seam # legacy_public_seam | verified_rust_contract
        evidence: []
      rationale: "Legacy public behavior remains the oracle."
      required_contracts: []
      excluded_legacy_internals: []
    dependency_recon:
      mode: agent # agent | manual | disabled
      status: pending # not_required | pending | complete | policy_rejected | manual | user_disabled | blocked
      report: null
    required_reviews:
      - behavior_reviewer
    writer_verification:
      status: pending # pending | passed | failed
      evidence: null
    review_batch: null
    verification:
      - "test command or behavior fixture"
    rollback: "Route back to legacy owner."

review_batches:
  - id: review-0001
    scope: manifest
    status: open # open | in_review | complete
    unit_ids: []
    required_reviews: []
    reports: []
    unit_verdicts: {}
```

For simple Python module migration, a `modules:` map with `path_py`, `path_rs` and `signature` is acceptable.

## Granularity Profile

The manifest should record how finely the user wants the rewrite cut. Ask during
repository initialization, because unit size determines review count, token
cost, potential shard boundaries, hallucination risk, dead-code risk and
rollback precision.

Use these levels as vocabulary, not as rigid categories:

- `coarse`: fewer units and reviews; good for low-risk internal helpers or when
  speed/cost dominates.
- `balanced`: default; each unit has independent fixtures and rollback without
  forcing every helper into its own review.
- `fine`: more reviews and token cost; useful for public payloads, parsers,
  data structures, error projection, persistence, model IO and dependency
  compatibility layers.
- `ultra_fine`: exceptional; use for high-risk contracts where hallucination,
  dead code, ABI/memory, numeric/model correctness or rollback precision matters
  more than cost.

Granularity may vary by domain. Do not impose one size across the whole project.
For example, parser state and model payloads may be `fine`, while leaf formatting
helpers remain `coarse` or `balanced`.

Record:

- default unit size
- domains requiring fine-grained cuts
- domains allowed to stay coarse
- default review roles per size
- review cadence: every unit, every N units, or the end of the current scope
- token/time/cost policy
- manifest partitioning independently from execution concurrency
- execution mode, defaulting to one serial writer

If the user has not chosen, start with `balanced` and explicitly mark it as an
assumption. Revisit the profile when R0 failures cluster, when review overhead
exceeds implementation work, or when dependency expansion reveals better unit
boundaries.

## Execution Policy

Manifest sharding and writer concurrency are separate decisions. Large projects
may use shards for ownership, dependency order, review scope and resumability
while a single writer processes them serially. Serial execution is the default
because multiple agents repeat context, compete for Cargo builds, and can create
incompatible private dependency implementations.

When sharding, parallel execution, shared Rust code, or shared Cargo state is
relevant, read [execution-policy.md](references/execution-policy.md) completely.
Use `coordinated_parallel` only after its admission gate passes. It requires one
coordinator to own the shared dependency registry, root manifests/lockfiles and
serialized Cargo build queue. `/tmp` remains disposable research only.

## Review Cadence

Ask how many completed migration units should share one independent review
cycle. Record this separately from `review_budget`: budget selects review roles;
cadence schedules them. Also ask whether high-precision boundaries should flush
the current batch or follow that cadence.

- `per_unit`: set `units_per_review: 1`.
- `batch`: require a positive `units_per_review`; default to `3` when the user
  does not choose.
- `end_of_scope`: set `units_per_review: null` and name the manifest, shard, or
  small-project scope whose completion closes the batch.

Treat the review batch only as a scheduling and evidence container. Keep each
unit's owner, verification, rollback and promotion state independent.

After each writer pass, run the unit's declared verification. Only passing
writer-verified units may enter an open review batch. They remain
`reimplemented`; the control plane must keep the legacy path as default until
the required independent evidence exists.

Close and review the batch when its size is reached, its scope is complete, or a
promotion is requested. Default `risk_override: flush_batch` also closes it at
a recorded high-precision boundary; `follow_cadence` lets the user's selected
schedule take precedence. If writer verification fails, stop accumulating units
and fix the failure; do not spend a review cycle on a knowingly broken batch.

Run R0 once over the closed batch, checking every unit and their integration.
Then run the union of additional roles required by the included units. A batch
report is valid only when it names the batch and records an explicit verdict for
each unit. `not_required` is valid only when the unit's manifest does not require
that report's role. Update unit state individually, so one failure does not
erase valid evidence for unrelated passing units.

## Verification Policy

Record one R0 oracle per unit before implementation. Default to
`behavior_parity` against the legacy public seam. Use `rust_compatibility` only
when exact legacy parity would require reproducing out-of-scope framework
internals and the application instead needs compatibility with already verified
canonical Rust contracts.

Compatibility mode must reference verified upstream Rust evidence and name the
application contracts that still cannot break: tensor shape/dtype/layout,
codec/artifact formats, model loading, schemas, handoff and error projection as
relevant. Record excluded legacy internals explicitly. Never switch modes merely
because parity tests failed, and never use an unverified or circular Rust oracle.

## Rewrite Preferences

Repository initialization must capture how strongly the user wants to reuse
Rust ecosystem dependencies, which domain capabilities should be hand-written,
and whether the user already prefers a framework for relevant capability
categories. This preference profile is durable user context, not migration
state: keep its single source of truth in `NOTES.md`, while the granularity
profile remains in the manifest/control plane.

When initializing a repository or when the user asks to revise these choices,
read [rewrite-preferences.md](references/rewrite-preferences.md) completely and
follow its two-stage interview and schema. Detect the project's capability
categories first and ask only about relevant choices. If the user does not know
or does not want to customize, record the `standard` default instead of forcing
more questions.

Do not add crates or change a lockfile while capturing preferences. The profile
is complete when every detected, architecture-significant category has either
an explicit selection or `auto`, crate reconnaissance is `agent`, `manual`, or
`disabled`, any registry proxy is recorded safely, and the fenced YAML block in
`NOTES.md` is internally consistent.

Default crate reconnaissance to `agent`. Before accepting `disabled`, warn that
py2rs will no longer prove whether a maintained crate or transitive backend
exists, and that the user should understand the Rust ecosystem or perform their
own crates.io/docs.rs and feature/dependency search. Record the acknowledgement
so later sessions do not confuse an intentional skip with completed research.

## Project Skill Scaffolding

After project facts, accepted seam, preferences, and state locations are known,
read [project-skill-scaffolding.md](references/project-skill-scaffolding.md)
completely. Use it to turn stable operational loops into project-specific
script-backed skills while leaving architecture choices in reasoning skills.
Select `prompt` or `scaffold` independently for each project role. Keep exactly
one variant under agent skill discovery roots; archive its counterpart outside
those roots and start a fresh session after every mode switch.

## Manifest Partitioning And Execution

大型重写不一定只能有一个长 manifest。只要项目能划出稳定 ownership 和依赖
边界，就可以建立 root manifest/index，再为每个范围维护独立 shard manifest。
这主要是控制面分割，不表示应该启动多个 Codex；默认仍按依赖顺序串行执行。

Root index example:

```yaml
version: 1
manifest_shards:
  - id: shared_types
    path: manifests/shared-types.yaml
    boundary: "canonical DTOs, error contracts, fixtures"
    dependencies: []
    owner_policy: "Only this shard changes shared public structs."
  - id: model_inference
    path: manifests/model-inference.yaml
    boundary: "model loading, inference wrapper, runtime cache"
    dependencies:
      - shared_types
    owner_policy: "Does not change GUI or export formats."
  - id: backend_io
    path: manifests/backend-io.yaml
    boundary: "parsing, file IO, export adapters"
    dependencies:
      - shared_types
    owner_policy: "Does not change model runtime behavior."
```

Shard manifest example:

```yaml
shard:
  id: backend_io
  boundary: "parsing, file IO, export adapters"
  owned_paths:
    - legacy/io/
    - rust/src/io/
  excluded_paths:
    - legacy/model/
  cross_shard_contracts:
    - "shared_types::AudioFrame is read-only from this shard"

units:
  - id: parse_wav_header
    status: planned
    unit_size: fine
    current_owner: legacy
    target_owner: rust
    public_interface_policy: "Preserve parser output and error projection."
    verification_policy:
      mode: behavior_parity
      oracle:
        kind: legacy_public_seam
        evidence: []
    required_reviews:
      - behavior_reviewer
    verification:
      - "cargo test -p rewrite_io parse_wav_header"
    rollback: "Route parser adapter back to legacy owner."
```

Use shards when they increase independent progress. Do not shard when boundaries
are still speculative, when shared data structures are unstable, or when every
unit modifies the same public contract.

Rules:

- Split by ownership boundary and public contract, not by line count.
- Keep shared DTOs, errors, fixtures, adapters, forked crates and hand-written
  dependency gaps in canonical prerequisite shards when multiple units need them.
- Under serial execution, keep one writer unit active and traverse shards in
  dependency order.
- Under coordinated parallel execution, one coordinator assigns shards and owns
  root manifests, shared Cargo files, the canonical dependency registry and the
  build queue. Workers never create private reusable dependencies.
- Cross-shard edits require an explicit record and dependency update in the root
  index.
- Promotion is per unit, but global release readiness is evaluated from the root
  index.
- Root rollback must remain understandable regardless of execution mode.
- Sharding must respect the granularity profile and improve control-plane
  clarity; do not create shards merely to justify parallel agents.

## State Rules

- `planned`: described but not started.
- `active`: implementation work has started.
- `reimplemented`: new path exists but independent review is incomplete.
- `verified`: the selected R0 evidence and required reviews passed.
- `promoted`: target owner is the default runtime path.
- `optimized`: post-promotion quality work is complete.
- `blocked`: cannot proceed without an explicit decision or external dependency.

Rules:

- Advance state only when reality changed.
- Do not skip the selected behavior-parity or Rust-compatibility R0 gate.
- Do not let a writer mark their own work verified.
- Keep batched units `reimplemented` and on the legacy default route until their
  per-unit verdicts and required reports pass.
- Never carry an open batch past its configured flush trigger.
- Keep rollback notes before promotion.
- Record non-obvious lessons in rewrite records.

## Optional Python Router

Use this only when Python remains the orchestrating process.

```python
def call(unit: str, function: str, *args, **kwargs):
    entry = manifest.get(unit)
    if entry.owner == "py":
        return call_python(entry, function, *args, **kwargs)
    if entry.owner == "rs":
        return call_rust_bridge(entry, function, *args, **kwargs)
    raise RuntimeError(f"unknown owner for {unit}")
```

The router must not know business semantics. It only adapts calls, errors, trace ids and return values.

## Optional Bridge

Choose the bridge that matches the project:

- `pyo3`/`maturin` for in-process Python extension calls.
- subprocess or CLI for coarse-grained batch/command replacement.
- HTTP/gRPC for service boundaries.
- Tauri commands for desktop backend replacement.
- direct Rust library API for extracted crates.

The bridge must preserve public behavior and error semantics until a migration unit explicitly changes them.

## Required Deliverables

- A manifest/control-plane file or confirmed reuse of the project manifest.
- A rewrite preference profile in `NOTES.md`, using `standard` defaults where
  the user declined customization.
- A crate reconnaissance mode and any crates.io proxy preference in `NOTES.md`.
- Project-specific skills for stable operational loops, or an explicit record
  that the project is not stable enough to scaffold them yet.
- A recorded granularity profile, or an explicit assumption that `balanced` is
  being used until the user decides.
- A recorded review cadence, or an explicit default of a three-unit batch.
- A recorded manifest partitioning choice and execution policy; serial is the
  default even for large sharded rewrites.
- A canonical shared dependency registry when multiple units consume common
  crates, forks, generated sources or hand-written capabilities.
- A documented public interface policy for each unit.
- A declared verification policy and non-circular oracle for each unit.
- A rollback route for each unit.
- Review roles and batch membership required before promotion.
- A history/audit trail for state changes.

## Acceptance

- A request can be routed through the chosen seam to old and new implementations.
- A rollback can be performed by changing the control-plane state or adapter selection.
- Invalid state jumps are rejected or clearly documented.
- The manifest names verification commands or fixtures.
- The runtime/control plane has no business logic.
- Unit sizes, review requirements and review timing match the recorded
  granularity profile and review policy.
- Open review batches contain only writer-verified `reimplemented` units and
  cannot be promoted before per-unit verdicts exist.
- Every unit has exactly one selected R0 gate; Rust-compatibility units reference
  already verified canonical Rust evidence and explicit application contracts.
- Rewrite preferences live in `NOTES.md`; repository initialization has not
  introduced speculative Cargo dependencies.
- Every dependency-sensitive unit distinguishes completed, manual, disabled,
  and blocked crate reconnaissance instead of treating missing evidence as a pass.
- Sharded manifests do not activate parallel writers by themselves.
- Parallel mode has an assigned coordinator, canonical shared dependency paths,
  exclusive shared-file ownership and serialized Cargo build scheduling.
- No durable dependency, build input or handoff artifact points to `/tmp` or an
  agent-private copy.
- For sharded manifests, shard boundaries, dependencies and cross-shard contracts
  are explicit enough for serial traversal or coordinator-assigned workers.
