---
name: "py2rs"
description: "Python-to-Rust 渐进式重写总 skill。用于规划、实施或审查系统级重写：读取项目事实与架构 seam，校准迁移粒度、重写力度和依赖偏好，通过可选的独立 crate 侦察、能力对齐、manifest、回滚路径和质量门逐步替换旧实现。"
---

# py2rs — 渐进式重写与现代化纪律

py2rs 不是翻译器，也不是强制的目录模板。它是一套重写纪律：在持续可运行、可验证、可回滚的前提下，把旧实现逐步替换为 Rust 或 Rust-backed 实现。

## Core Idea

先判断项目该如何迁移，再决定是否使用 Python/Rust router、FFI、CLI、subprocess、HTTP adapter、Tauri command facade 或已有后端 seam。

`mvsep-rs` 是一个重要范例：它借鉴了 `teach` 的状态化工作区，也借鉴了 py2rs 的迁移纪律，但没有采用 py2rs 的 `py/`、`rs/`、`runtime/router.py` 架构。它使用自己的 Tauri command -> backend facade seam。这是正确用法。

## Project Truth First

每次启动 py2rs 工作前，先找到项目事实，不从 py2rs 模板出发。

1. 读取项目的 mission、architecture、resources、notes、glossary、manifest、rewrite records 或等价文件。
2. 找出当前稳定公共接口：CLI 参数、HTTP API、Tauri command、事件名、DB schema、file format、FFI surface 或用户可见 workflow。
3. 找出接受的架构 seam：现有 facade、adapter、service boundary、command boundary、library boundary 或 process boundary。
4. 找出 rollback route：切回旧实现、改 manifest owner、切 adapter、恢复 legacy store 或关闭 feature flag。
5. 记录 borrowed-ideas boundary：借鉴什么理念，不借鉴什么架构。

若项目没有这些文件，先创建最小项目画像，而不是直接生成 Rust 代码。

## Granularity Calibration

初始化重写仓库或重切 manifest 前，必须和用户校准迁移单元粒度。`minimum
independently verifiable rewrite unit` 不是“想象中最小的一行代码”，而是用户在
质量、成本、速度和审核深度之间接受的最小可验证单元。

向用户说明这个 tradeoff：

- 更小的单元：更多轮 writer/reviewer、更多 token 和协调成本；换来更少 AI
  幻觉、更细的行为/依赖把握、更少死代码、更小回滚面和更高代码质量。
- 更大的单元：更少审核轮次、更低 token 成本、更快看到大块迁移成果；代价是
  更宽的行为面、更高遗漏概率、更难定位差异、更容易产生无用抽象或死代码。

校准至少覆盖：

- capability/domain：哪些领域要切得细，哪些可以粗一些。
- review budget：每个单元默认需要哪些 review roles，是否所有单元都跑完整 R0-R6。
- token/time budget：用户更重视速度、成本还是质量。
- parallelism：是否希望多个 Codex 并行，是否需要 manifest shards。
- risk tolerance：哪些公共接口、数据结构、模型/数值路径、持久化或 ABI 边界必须细切。

记录结果，例如：

```yaml
granularity_profile:
  default_unit_size: balanced # coarse | balanced | fine | ultra_fine
  review_budget: behavior_first # behavior_first | full_gate | risk_based
  token_budget_policy: "Prefer fine units for parser/model payloads; coarse units for leaf formatting helpers."
  parallelism: shard_when_boundaries_are_stable
  high_precision_domains:
    - public_payloads
    - model_io_shapes
    - persistence_formats
  coarse_allowed_domains:
    - internal_formatting_helpers
```

If the user does not choose, default to `balanced`: small enough for independent
fixtures and rollback, but not so small that every helper creates a separate
review cycle. Revisit the profile after dependency expansion, after the first
failed R0 review, or when review cost dominates implementation cost.

## Rewrite Preference Calibration

初始化重写仓库时，还要询问或读取项目的 rewrite preferences。它与 granularity
不同：granularity 决定迁移单元和审核要切多细；rewrite preferences 决定项目
倾向复用 Rust 生态、手写兼容层，还是从底层重写领域能力，以及各能力类别的
框架偏好。

由 `py2rs-runtime` 负责两阶段采集并写入 `NOTES.md`。用户不知道或不想定制时，
使用当前 capability-first 的 `standard` 策略。初始化只记录偏好，不预先修改
`Cargo.toml` 或 lockfile；进入相关迁移单元后，`py2rs-dep-align` 才应用偏好并
锁定实际依赖。

## What py2rs Borrows From Other Skills

从 `teach` 借鉴：

- mission-grounded work
- resources before memory
- durable notes and glossary
- records for non-obvious lessons
- minimum scoped progression

py2rs 自己提供：

- behavior before architecture
- reversible migration state
- manifest-driven progress
- writer/reviewer separation
- independent quality gates
- R0 behavior parity before optimization

项目自己提供：

- accepted architecture
- stable public interfaces
- migration unit boundaries
- storage and ownership rules
- verification commands
- promotion policy

## Migration Unit

迁移单元不是固定的“脚本”。迁移单元是：

```text
minimum independently verifiable rewrite unit
```

常见形态：

- 纯 Python 项目：一个 script、module、CLI subcommand 或 service function。
- Web/backend 项目：一个 endpoint group、repository、worker、job type 或 service adapter。
- Desktop/Tauri 项目：一个 command batch、event contract、backend capability 或 persistence domain。
- Data/ML 项目：一个 pipeline stage、parser、transformer、model runner wrapper 或 cache layer。

选择标准：单元必须能独立测试、独立审查、独立回滚。

The unit size must follow the recorded granularity profile. Do not split
everything to the smallest imaginable fragment by default, and do not merge
separate public behaviors just to reduce review count.

迁移单元清单是临时的工作假设，不是必须维护的资产。依赖展开后如果发现
一个单元覆盖了多个可独立验证的能力，先重切单元，再写实现。反过来，如果
多个单元共享同一个必要的 Rust 数据模型、fixture harness 或 adapter，可以
提取前置单元或合并边界。渐进式重写的核心是最小可验证分割，而不是维护最初
列出来的模块列表。

## Architecture Selection

py2rs 默认不强加 runtime architecture。先根据项目形态选 seam。

| Project Shape | Preferred Seam |
|---|---|
| Python process remains orchestrator | `runtime/router.py` + bridge can be appropriate |
| CLI replacement | command wrapper or binary compatibility surface |
| Service/backend | HTTP/API/service facade or repository adapter |
| Tauri/desktop | command facade or backend trait seam |
| Batch/data pipeline | pipeline stage adapter and golden fixtures |
| Library extraction | stable public library API with old caller adapter |

Only use `py/`, `rs/`, and `runtime/router.py` when they fit the project. If the project already has a stronger seam, keep it.

## Standard Flow

1. Ground in project truth: read source-of-truth docs, current manifest, records, architecture and existing tests.
2. Calibrate or read the user's rewrite preferences and granularity profile.
3. Define the migration unit and public interface policy.
4. Define current owner, target owner, rollback route and required reviews.
5. Satisfy the recorded crate reconnaissance mode before dependency alignment.
6. Align and lock the selected unit's dependencies when its capability coverage requires them.
7. Add or identify behavior tests before implementation when practical.
8. Implement behind the chosen seam.
9. Mark new implementation as `reimplemented`, not `verified`.
10. Run R0 behavior review first.
11. Run additional review gates as separate roles.
12. Promote only after required reviews pass and rollback remains clear.
13. Record reusable lessons in rewrite records.

## Manifest Model

Use a manifest shape that fits the project. The minimum fields are:

```yaml
units:
  - id: example_unit
    status: planned # planned | active | reimplemented | verified | promoted | optimized | blocked
    unit_size: balanced # coarse | balanced | fine | ultra_fine
    current_owner: legacy
    target_owner: rust
    public_interface_policy: "Preserve existing CLI/API/command/event/payload behavior."
    dependency_recon:
      mode: agent # agent | manual | disabled
      status: pending
      report: null
    required_reviews:
      - behavior_reviewer
      - error_tracing_reviewer
    verification:
      - "project-specific test command"
    rollback: "How to route back to the legacy path."
```

For pure Python script migrations, the older module form is still valid:

```yaml
modules:
  user_service:
    owner: py
    status: planned
    path_py: py/user_service.py
    path_rs: rs/user_service.rs
    signature: manifest/signatures/user_service.json
```

Manifest state must be factual. Do not mark a unit `verified` without behavior evidence and required independent reports.

### Manifest Sharding And Parallel Work

For large rewrites, one long manifest can become an artificial serial bottleneck.
When the user wants parallel Codex sessions and the project has clear ownership
boundaries, split the control plane into a root index plus scoped manifests.

Use sharding only when each shard can name:

- owned units and excluded units
- public seam and cross-shard contracts
- shared prerequisites
- verification commands
- rollback route
- required review roles

Example root index:

```yaml
manifest_shards:
  - id: model_inference
    path: manifests/model-inference.yaml
    boundary: "model loading, inference wrapper, runtime cache"
    dependencies: []
  - id: backend_io
    path: manifests/backend-io.yaml
    boundary: "file IO, parsing, export adapters"
    dependencies:
      - shared_types
  - id: shared_types
    path: manifests/shared-types.yaml
    boundary: "canonical DTOs, errors, fixtures"
    dependencies: []
```

Rules:

- Do not split by file count alone; split by stable contracts.
- Extract shared types, fixture harnesses and adapters before parallelizing units
  that depend on them.
- A worker owns one shard at a time and does not change another shard's manifest
  except through an explicit cross-shard record.
- Promotion still requires R0 behavior evidence for the unit, even if another
  shard has already advanced.
- Keep a root index so global rollback and dependency order remain visible.

## Review Roles

Use separate reviewer roles. A writer never reviews their own code.

- `behavior_reviewer`: public behavior, payloads, compatibility and old/new parity.
- `error_tracing_reviewer`: structured errors, logs, context and redaction.
- `async_ergonomics_reviewer`: blocking behavior, cancellation, polling, recovery and concurrency ergonomics.
- `data_algorithm_reviewer`: schema, data structures, complexity, migrations and benchmarks.
- `rust_style_reviewer`: Rust module shape, ownership, clippy, warnings and maintainability.
- `frontend_ux_reviewer` or `product_ergonomics_reviewer`: user workflow, accessibility, CLI/help/log ergonomics and text overflow where relevant.

Behavior review is always first. Other roles depend on the migration unit.

## Dependency Policy

Dependencies are aligned by capability coverage, not one-to-one package names.

- Read the rewrite preferences in `NOTES.md` before comparing Rust candidates.
  Treat them as a search constraint, not as a substitute for project facts or
  behavior fixtures.
- Read `crate_reconnaissance.mode` before dependency alignment. `agent` requires
  a fresh-context `py2rs-crate-recon` report; `manual` requires user-supplied
  candidate and dependency-path evidence; `disabled` requires a stored warning
  acknowledgement and remains visible as `user_disabled`.
- A high-level crate cannot be rejected before its relevant features and
  dependency paths are checked, unless reconnaissance is explicitly disabled.
- Stage 0 should identify the bridge/seam and dependencies required for behavior parity.
- Python dependency packages may be much broader than the selected migration
  unit. It is valid for Rust crates to cover a large lower layer while a small
  compatibility adapter or hand-written Rust fills only the observed Python
  semantic gaps.
- Do not require perfect package parity. Under `standard`, prefer this ladder:
  1. direct crate coverage when fixtures prove behavior;
  2. partial crate reuse plus a fixture-bound compatibility adapter when the
     Python source explains the semantic delta;
  3. narrow hand-written Rust for semantic gaps or capabilities the crate
     cannot safely own.
- This `standard` ladder is not a preference for fewer dependencies or full wheel
  rewriting. Introducing Rust dependencies and writing small compatibility code
  are complementary. Under `standard` or `ecosystem_first`, a dependency review
  should challenge unnecessary hand-written reimplementation when a maintained
  crate can safely own a stable lower layer behind fixtures.
- Under `standard`, full hand-written replacement is still valid when it is the
  smaller or safer verified path. Common reasons include unacceptable semantic
  mismatch, unstable or unmaintained crates, licensing/security/build/runtime
  constraints,
  portability problems, excessive integration cost, or a selected capability so
  narrow that a crate would add more surface than it removes. Record this as a
  tradeoff, not as a default preference.
- Under `handwritten_first` or `domain_from_scratch`, follow the recorded domain
  boundary instead of reapplying the standard ladder. Hand-written behavior must
  still be grounded in reference sources and fixtures.
- When dependency behavior matters, expand or snapshot the relevant Python,
  native or Rust-backed dependency source into a project-controlled reference
  location, with version, origin and license recorded. Use it to understand
  semantics; do not expand the whole ecosystem just to make an inventory.
- At repository initialization, snapshot first-layer direct Python dependency
  sources when storage, license and project policy allow it. This can be large;
  it exists as a local reference corpus for dependency alignment and wheel
  rebuilding, not as a recursive rewrite target.
- Expand second-layer or deeper transitive dependencies only with public-seam
  call-path evidence. Lockfile transitivity alone is not enough; py2rs rewrites
  the Python project, not the entire Python/native ecosystem below it.
- Dependency alignment may recommend re-cutting a migration unit before
  implementation when the planned unit is too broad, mixes unrelated
  capabilities, or hides a better seam.
- During implementation and R0, avoid unplanned dependency churn. Missing essentials mean Stage 0 was incomplete.
- During later quality reviews, new dependencies are allowed when they serve a review objective and R0 behavior still passes.
- Repository initialization records framework choices but does not add speculative
  dependencies. Add and lock a crate only when a seam or selected migration unit
  needs its capability.
- Rust Edition 2024 is preferred for new Rust crates unless the project toolchain or FFI choice prevents it.

## Non-Negotiables

- Behavior parity precedes Rust elegance.
- Public interfaces stay stable unless the migration unit explicitly changes protocol.
- Runtime/control-plane/adapters do not contain business logic.
- Every unit has a rollback route.
- Review reports are durable handoff artifacts, not chat summaries.
- Do not import another skill's architecture without recording why it fits this project.

## Sub-Skill Routing

- `py2rs-crate-recon`: search crates.io and trace feature/dependency paths in a
  fresh context before dependency alignment.
- `py2rs-dep-align`: consume reconnaissance evidence and decide capability coverage and seam dependencies.
- `py2rs-env-bootstrap`: prove the chosen seam works before business migration.
- `py2rs-runtime`: capture rewrite preferences, define manifest/control-plane and optional routing adapters.
- `py2rs-review-r0-behavior`: independent behavior parity gate.
- `py2rs-review-r1-rust-style`: Rust structure and maintainability.
- `py2rs-review-r2-error-tracing`: error semantics, tracing and diagnosability.
- `py2rs-review-r3-io-concurrency`: async, blocking IO, cancellation and concurrency.
- `py2rs-review-r4-algo-complexity`: algorithmic changes only with analysis and benchmarks.
- `py2rs-review-r5-architecture`: data structures, ownership and API boundaries.
- `py2rs-review-r6-ergonomics`: product, CLI, UX and operational ergonomics; report-only by default.

## Success Metric

The success metric is not “Rust code exists.” It is:

```text
At every migration state, the system remains runnable, testable and rollbackable.
```
