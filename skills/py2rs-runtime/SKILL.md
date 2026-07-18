---
name: "py2rs-runtime"
description: "[DRAFT] 初始化 py2rs 重写偏好并建立迁移控制面：在 NOTES.md 记录依赖重写力度、框架偏好、crate 侦察模式和 registry 代理，维护 manifest 或 manifest shards、迁移粒度、状态机、路由/adapter、回滚和审计。"
---

# py2rs-runtime — 迁移控制面与可选路由层

本 skill 不再把 `runtime/router.py` 当成所有项目的强制架构。它负责建立迁移控制面：哪些单元存在、当前归谁、公共接口是什么、如何验证、如何回滚、如何审计状态变化。

## Start Here

1. 读取项目事实：mission、architecture、resources、notes、manifest、records、tests 或等价文件。
2. 确认项目已有 seam。如果已有稳定 facade/adapter/command/API boundary，优先沿用。
3. 初始化仓库时，询问或读取用户的 rewrite preferences，并把偏好写入 `NOTES.md`。
4. 项目事实、seam 和偏好稳定后，为固定操作创建项目专属 script-backed skills。
5. 初始化仓库或重切 manifest 前，询问或读取用户的 granularity profile。
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
  parallelism: single_manifest # single_manifest | shard_when_stable | shard_now
  high_precision_domains: []
  coarse_allowed_domains: []

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
    dependency_recon:
      mode: agent # agent | manual | disabled
      status: pending # not_required | pending | complete | policy_rejected | manual | user_disabled | blocked
      report: null
    required_reviews:
      - behavior_reviewer
    verification:
      - "test command or behavior fixture"
    rollback: "Route back to legacy owner."
```

For simple Python module migration, a `modules:` map with `path_py`, `path_rs` and `signature` is acceptable.

## Granularity Profile

The manifest should record how finely the user wants the rewrite cut. Ask during
repository initialization, because unit size determines review count, token
cost, parallelism, hallucination risk, dead-code risk and rollback precision.

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
- token/time/cost policy
- sharding preference for parallel Codex sessions

If the user has not chosen, start with `balanced` and explicitly mark it as an
assumption. Revisit the profile when R0 failures cluster, when review overhead
exceeds implementation work, or when dependency expansion reveals better unit
boundaries.

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

## Manifest Shards

大型重写不一定只能有一个长 manifest。若用户希望开多个 Codex 并行工作，且项目
能划出稳定边界，可以建立 root manifest/index，再为每个范围维护独立 shard
manifest。

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
- Keep shared DTOs, errors, fixtures and adapters in their own prerequisite
  shard when multiple teams need them.
- One worker owns one shard at a time.
- Cross-shard edits require an explicit record and dependency update in the root
  index.
- Promotion is per unit, but global release readiness is evaluated from the root
  index.
- Root rollback must remain understandable even when shard work proceeds in
  parallel.
- Sharding must respect the granularity profile: do not create many shards just
  to parallelize if the user chose a coarse or low-token rewrite, and do not
  force one serial manifest when the user chose fine-grained high-quality work
  with stable independent domains.

## State Rules

- `planned`: described but not started.
- `active`: implementation work has started.
- `reimplemented`: new path exists but independent review is incomplete.
- `verified`: behavior evidence and required reviews passed.
- `promoted`: target owner is the default runtime path.
- `optimized`: post-promotion quality work is complete.
- `blocked`: cannot proceed without an explicit decision or external dependency.

Rules:

- Advance state only when reality changed.
- Do not skip behavior review.
- Do not let a writer mark their own work verified.
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
- For large parallel rewrites, either a root manifest with shard manifests or an
  explicit decision not to shard.
- A documented public interface policy for each unit.
- A rollback route for each unit.
- Review roles required before promotion.
- A history/audit trail for state changes.

## Acceptance

- A request can be routed through the chosen seam to old and new implementations.
- A rollback can be performed by changing the control-plane state or adapter selection.
- Invalid state jumps are rejected or clearly documented.
- The manifest names verification commands or fixtures.
- The runtime/control plane has no business logic.
- Unit sizes and review requirements match the recorded granularity profile.
- Rewrite preferences live in `NOTES.md`; repository initialization has not
  introduced speculative Cargo dependencies.
- Every dependency-sensitive unit distinguishes completed, manual, disabled,
  and blocked crate reconnaissance instead of treating missing evidence as a pass.
- For sharded manifests, shard boundaries, dependencies and cross-shard contracts
  are explicit enough for separate Codex sessions to work without editing the
  same control-plane scope.
