---
name: "py2rs-dep-align"
description: "[DRAFT] 消费 crate reconnaissance 或用户手动生态证据，按 NOTES.md 中的偏好对齐 Python/Rust 或 legacy/Rust 依赖。覆盖 canonical shared dependencies、crate/backend/adapter/手写能力组合、manifest 重切、seam、验证和桥接；用于避免串行或并行 writer 创建冲突依赖副本。"
---

# py2rs-dep-align — 依赖与能力对齐

Stage 0 的目标是证明迁移有可行的能力覆盖和集成路径。先对齐项目需要的能力，再决定用哪些依赖。

## Inputs

先读取：

- 项目依赖清单：`requirements.txt`、`pyproject.toml`、`Cargo.toml`、lockfile、package manifests。
- 项目事实：mission、architecture、manifest、resources、records。
- `NOTES.md` 中的 `rewrite_preferences`；缺失时使用 `standard` 并记录这是默认假设。
- `crate_reconnaissance.mode` 及对应的 agent report、manual evidence 或
  disabled acknowledgement。
- 目标迁移单元的公共接口和验证方式。
- 已有第三方源码快照、vendored sources、native sources、source audit 或等价记录。
- manifest 中的 `execution_policy`、shared dependency registry，以及当前
  unit/shard 的依赖关系和允许修改的路径。
- unit 的 `behavior_verification`、legacy public seam 和 evidence。

## Apply Rewrite Preferences

Rewrite preferences constrain the candidate search; they do not replace public
behavior evidence, project architecture, or dependency source analysis.

- `standard`: use the capability ladder below. Prefer maintained crates or
  crate plus adapter, while allowing a full hand-written path when recorded
  evidence shows it is smaller, safer, or easier to roll back.
- `ecosystem_first`: maximize maintained crate coverage and limit hand-written
  code to project semantics and observed semantic gaps.
- `handwritten_first`: start from a fixture-backed hand-written domain path;
  reuse general infrastructure and use a domain crate only when the dependency
  record explains why hand-writing would violate the user's actual goal.
- `domain_from_scratch`: reject crates that own the selected domain algorithms,
  domain data structures, or Python-visible domain semantics. General
  infrastructure remains allowed unless separately constrained.
- `custom`: apply the capability-specific rules recorded in `NOTES.md`.

For each relevant framework preference, honor `prefer` when project evidence
does not favor another path. Never silently violate `require` or `avoid`. If a
hard preference conflicts with public behavior, licensing, security, build,
portability, or an existing accepted architecture, stop and get a user decision
before changing the preference.

Do not treat example crate names in py2rs documentation as a current catalog.
Inspect existing project choices and verify maintained candidates against
current official sources before selecting a new framework.

## Crate Reconnaissance Gate

Apply the mode recorded in `NOTES.md` before comparing implementation paths:

- `agent`: require a fresh-context `py2rs-crate-recon` report with status
  `complete` or `policy_rejected`. A `blocked` or missing report blocks this
  dependency alignment stage.
- `manual`: require user-supplied evidence naming searched capabilities,
  candidates, relevant features/dependency paths, and rejection or fit reasons.
  Record status `manual`; missing evidence blocks the stage.
- `disabled`: verify the stored acknowledgement that the user understands the
  Rust ecosystem or will search it independently. Continue with status
  `user_disabled`, but do not claim that no maintained crate/backend exists or
  that ecosystem coverage is complete.

`disabled` skips the independent comparative reconnaissance stage. It does not
waive minimum official-source due diligence for a dependency the unit actually
selects, but that narrow check cannot be presented as complete ecosystem search.
Keep the acknowledgement only in `NOTES.md`; unit records reference that source
and retain residual risk instead of copying the preference text.

In `agent` mode, require focused candidate documentation evidence. Context7 is
the default provider and should be bootstrapped when missing; docs.rs or
downloaded crate source is an acceptable fallback only when the report records
why Context7 setup, service access, or indexing could not serve the candidate.

When enabled, search by public capability, inspect the three most relevant
candidates, and always inspect user-named candidates. For umbrella/high-level
crates, follow only capability-relevant features and dependencies until the
actual owner is found. Top-level API mismatch alone is not a rejection reason.

Read the reconnaissance summary first. Load raw registry/Cargo evidence only
when challenging a candidate decision; this keeps implementation context from
overwriting the independent research judgment.

## Capability Coverage

按能力对齐，不按库名对齐。

- Python 大库可以由多个 Rust crate 组合覆盖。
- Rust crate 不需要是 Python 包的高层 drop-in 才有价值。只要它能稳定覆盖
  tokenizer、parser、event stream、IO、Unicode table、numeric primitive、
  data structure 等较低层能力，就可以复用该层，再用小 adapter 补齐 Python
  包的 public behavior。
- 不追求依赖一一对应。`standard` 的优先级是：
  1. fixture 证明直接 crate 覆盖；
  2. crate 覆盖稳定下层能力，Python 源码解释语义差异，Rust adapter 补齐；
  3. 仅对语义差异或 crate 不能安全负责的窄能力手写 Rust。
- 在 rewrite preferences 允许 crate reuse 时，引入依赖和造轮子不是互斥选项。
  依赖审查优化的是“最小、可验证、可回滚的
  能力组合”，不是依赖数量最少。成熟 crate 能安全负责的底层能力应优先复用，
  手写代码负责 Python 行为投影、语义 delta、错误投影、构造器差异、格式化差异
  或其它被 fixtures 锁住的小范围行为。
- 在 `standard` 或 `ecosystem_first` 下，审查时同时反对两个极端：为了包名一致
  而强行找 drop-in replacement；以及因为 crate 不能完美匹配 Python 包就退回
  几乎全手写。不要把这条规则用于推翻用户选择的 hand-written profile。
- 必要时全量造轮子也是可行方案。判断标准不是“有没有依赖”，而是哪条路径
  更小、更可验证、更可维护、更容易回滚。可接受理由包括：crate 语义偏差过大、
  crate 不稳定或维护不足、许可/安全/构建/运行时/跨平台约束不可接受、集成成本
  高于收益，或 selected capability 很窄导致引入 crate 的 surface 大于收益。
  在 `standard` 或 `ecosystem_first` 下，这种决定必须写成 tradeoff，并绑定参考
  源码与 fixtures；hand-written profiles 仍然必须绑定 fixtures 和参考源码，但
  不需要重新论证用户已经确认的总体重写方向。
- Python 侧依赖很大时，不要因为 Rust 侧 crate 覆盖了“大量无关内容”而拒绝
  它；只要 selected unit 只暴露一小片能力，并且 adapter/fixtures 把行为锁住，
  这种覆盖是可接受的。
- 若直接 crate 替换比选定单元更宽、更不稳定或更难验证，允许手写一个窄 Rust
  replacement。手写必须绑定参考源码和 fixtures，不能凭记忆重造行为；在
  `standard` 下它不是默认优先级。无论 profile 如何，通用基础设施与领域能力
  都必须分开判断。
- Python `re` 若使用 lookaround/backtracking 特性，Rust 侧考虑 `fancy-regex`。
- pandas/numpy 类能力可能由 `polars`、`arrow`、`ndarray` 或保留 Python owner 覆盖。
- GUI/web/front-end 构建链不是 py2rs 迁移对象，除非该项目的迁移单元明确包含它。
- 专有 SDK、闭源 binding 或 Rust 侧无法覆盖的能力保留 legacy owner，并通过 seam 集成。

## Canonical Shared Dependencies

Before adding a crate, fork, adapter, generated source tree, fixture harness, or
hand-written implementation, search the project-controlled shared dependency
registry and canonical source roots. Reuse an existing capability that satisfies
the selected behavior and project constraints instead of creating an agent-local
alternative.

When an upstream crate is incomplete, a hand-written gap can be the correct
solution. If two or more units may need it, create or re-cut one shared
prerequisite unit with a canonical project path, API, owner, consumers, source
references, fixtures, and build evidence. For example, a missing Burn capability
must not be independently implemented under two model shards.

`/tmp` and agent-private directories are disposable discovery locations only.
They cannot appear in a dependency record as the implementation path consumed
by another unit. Promote useful code into the canonical project root, record it
in the registry, and verify it there before reuse.

Under `coordinated_parallel`, only the coordinator may change shared
`Cargo.toml`, `Cargo.lock`, workspace members, patch configuration, vendored
sources, or registry entries. A worker writes a dependency-change request and
waits; it does not create a private dependency copy to bypass coordination.

## Deep Framework Boundary

Dependency analysis may reveal that Python and Rust deep-learning frameworks
interpret tensors or model artifacts differently in ways that reach codecs,
loading, schemas, or inference handoff. Do not propose rewriting the entire
framework just to preserve its internals.

If the selected seam cannot support exact parity without pulling those internals
into scope, move the seam outward to an observable application boundary or
re-cut the migration unit. Record tensor, codec, artifact, model-loading and
error behavior when it crosses that seam. If no independently comparable legacy
seam exists, keep the capability legacy-owned or defer the unit. A failed parity
test is not a reason to replace the legacy oracle with a Rust-only contract.

## Dependency Source Expansion

依赖展开分两层：初始化基线和单元内深挖。

### Initialization Baseline

在初始化重写仓库时，如果存储、许可和项目政策允许，展开或 snapshot Python
项目的第一层直接依赖源码到 project-controlled reference location。第一层直接
依赖来自 `requirements`、lockfiles、`pyproject`、package manifests 或项目
明确 import/运行时加载的包。

目的：

- 给依赖对齐和造轮子提供高级语言层面的参考源码。
- 避免每个迁移单元重复联网查源码。
- 支撑后续判断：crate 复用、adapter、窄手写、全手写或保留 legacy owner。

大体量源码快照可以接受，但它必须是有索引、有版本、有来源、有 license 的
reference corpus，不是把 Python 生态递归迁入项目。

### Targeted Deep Expansion

从目标迁移单元的 Python source refs 出发，默认只在第一层直接依赖内搜索和展开。
第二层、第三层或更深的 transitive dependency 只有在能证明 selected public
behavior 直接依赖其特定实现时才展开。

允许深层展开的证据包括：

- 调用链从项目 public seam 到第一层依赖，再进入 transitive dependency 的特定
  symbol、function、class、schema、native wrapper 或 data table。
- 第一层依赖只是薄包装，实际 public behavior 由第二层依赖定义。
- 行为 fixture、错误投影、序列化格式、模型输入输出、缓存键、ABI/memory
  contract 或持久化格式会因该 transitive implementation 改变。
- 第一层源码无法解释 observed behavior，必须读取下层实现才能写 adapter 或
  replacement。

不允许的理由：

- 第一层依赖在 lockfile 中依赖了某包。
- 为了画完整依赖图。
- 为了审查 Python 生态或 native 生态的全部实现。
- 因为底层编译器、C/Rust/Fortran/native library 内部实现存在差异，但该差异
  没有穿透到 selected public seam。

检查顺序：

- project imports and local helper calls
- requirements, lockfiles and package manifests
- first-layer direct dependency source snapshots
- project-controlled third-party source snapshots
- vendored Python/Rust/native source trees
- targeted transitive source only when the call path evidence above exists
- upstream source archives downloaded for this rewrite, when license and project
  policy allow it
- existing tests, fixtures and caller expectations

若需要下载或保存第三方源码，记录 package、version、dependency depth、origin
URL、hash、license、用途和触发它的 public behavior/call path。源码快照是语义
参考，不等于要把整个依赖迁入 Rust。

停止条件：当前单元已经能说明 public behavior、legacy dependencies、Rust-covered
capabilities、fixtures、rollback 和 kept-legacy capabilities。不要为了画完整依赖图
而展开整个 Python 生态。

## Native And Low-Level Boundaries

Python 项目经常是胶水层。越往第二层、第三层依赖下探，越容易进入 C、C++、
Fortran、Rust、CUDA、系统库或编译器运行时的实现细节。py2rs 重构的是项目的
Python 语义和 accepted public seam，不是递归重构 Python 生态或 native 生态。

区分两类差异：

- High-level/domain-visible structures: parser state、tokenizer output、tensor
  shape/dtype policy、model runner payload、serialization schema、cache key、
  business DTO、error projection、Unicode normalization output 等。如果它们影响
  selected public behavior，可以展开依赖、写 adapter 或造轮子。
- Low-level implementation details: NaN bit payload、compiler macro、native
  struct padding、allocator behavior、SIMD path、internal Unicode table layout、
  BLAS/CUDA kernel choice 等。默认不作为依赖对齐或 R0 行为审查目标，除非它们
  会造成 public seam 不一致、内存/ABI 契约风险、持久化不兼容、安全问题或
  模型/数值正确性问题。

不要为了复刻低层实现细节而手写底层轮子。只有当低层差异确实穿透到项目契约，
并且 crate/community/runtime 不能合理承担时，才把它提升为迁移单元或 hand-written
replacement。

## Re-Cut Signals

依赖对齐可以改变 manifest，而不只是填依赖表。出现这些信号时先提议重切：

- 一个 planned unit 混合了多个独立 capability，导致 fixtures 难以命名。
- 直接 crate replacement 覆盖范围远大于用户要迁移的一小片行为。
- Python dependency source 揭示 public API、constructor、formatting、resolver、
  error projection 或 cache semantics 可以单独验证。
- 多个 units 需要同一个 Rust DTO、parser state、fixture harness 或 adapter。
- rollback route 在当前边界下不清楚。
- Rust crate 和 Python package 的差异只影响薄 semantic-delta adapter，适合拆出独立 unit。

输出必须说明是 confirmed、split、merged、renamed、deferred 还是 replaced。

## Seam Dependencies

根据项目 seam 选择依赖：

- Python extension: `pyo3`, `maturin`.
- CLI/subprocess: argument parser, JSON/stdin protocol, exit-code contract.
- HTTP/service: `reqwest`, server framework, schema fixtures.
- Tauri/backend facade: Tauri APIs, async runtime, command payload types.
- Data pipeline: parser, serializer, fixture and golden-output tooling.
- Rust library extraction: crate layout, error type, serialization and test harness.

Do not install bridge dependencies that the chosen seam does not need.

## Dependency Locking

- Repository initialization records preferences only; it must not add speculative
  crates or change a lockfile.
- When a seam or selected migration unit enters Stage 0, identify, add and lock
  the dependencies required for its behavior parity.
- In serial mode, update canonical manifests once and let later shards reuse the
  recorded dependency and build evidence.
- In coordinated parallel mode, route shared manifest/lockfile changes through
  the coordinator and its serialized Cargo build queue.
- During implementation and R0, avoid dependency churn. Missing essentials mean Stage 0 was incomplete.
- During R1-R6, new dependencies are allowed only for the review objective and must preserve R0 behavior.
- Prefer Rust Edition 2024 for new Rust crates unless the project constrains toolchain/FFI.

## Output

Write or update a dependency record. Use the project location if one exists; otherwise:

```yaml
unit: example_unit
status: planned
capabilities:
  regex:
    legacy: python-re
    rust: fancy-regex
    reason: "lookaround used in source patterns"

seam:
  kind: cli | ffi | service | tauri-command | library | pipeline
  bridge_dependencies:
    - name: serde_json
      reason: "stable subprocess protocol"

preference_application:
  source: "NOTES.md#py2rs-rewrite-preferences"
  profile: standard
  framework_preferences:
    async_runtime:
      selection: tokio
      strength: prefer
      decision: use
  deviations: []

crate_reconnaissance:
  mode: agent # agent | manual | disabled
  status: complete # complete | policy_rejected | manual | user_disabled | blocked
  report: "rewrite-records/dependencies/example-unit-crate-recon.yaml"
  residual_risk: null

canonical_dependency:
  registry: manifest/shared-dependencies.yaml
  reuse:
    - id: burn-missing-capability
      path: rust/crates/burn-missing-capability
  requested_changes: []
  temporary_sources: disposable_only

behavior_verification:
  legacy_public_seam: "CLI/API/command/model/application boundary"
  required_observations: []
  comparison_policy:
    default: exact
    tolerances: []
  evidence: []

rust:
  edition: "2024"
  crates:
    - name: thiserror
      reason: "structured public errors"

dependency_strategy:
  stance: "reuse stable crate-owned lower layers; hand-write only observed semantic gaps"
  not_goal: "minimize dependency count"
  full_handwritten_allowed_when:
    - "crate semantic mismatch is larger than the selected capability"
    - "licensing, security, build, runtime, portability, or maintenance risk is unacceptable"
    - "a narrow fixture-backed implementation is smaller and easier to roll back"
  rejected_extremes:
    - "force one-to-one Python package parity"
    - "rewrite mature lower-layer behavior by hand without a recorded tradeoff"

source_expansion:
  initialization_baseline:
    depth: "first-layer direct Python dependencies"
    purpose: "local reference corpus for dependency alignment and wheel rebuilding"
  targeted_deep_expansion:
    allowed_depth: "second-layer or deeper only with call-path evidence"
    proof_required:
      - "public seam behavior reaches the transitive implementation"
      - "fixture, error projection, schema, ABI, persistence, cache, or model behavior depends on it"
    not_allowed_for:
      - "recursive ecosystem inventory"
      - "lockfile dependency existence alone"

low_level_boundary:
  ignore_by_default:
    - "compiler/runtime/internal native representation differences"
    - "native dependency implementation details that do not reach the public seam"
  investigate_when:
    - "public seam behavior differs"
    - "memory, ABI, persistence, security, or model/numeric correctness is at risk"

crate_reuse:
  candidates:
    - crate: fancy-regex
      covered_capabilities:
        - "regex matching with lookaround"
      gaps:
        - "legacy wrapper error text"
      adapter_plan: "normalize errors in the selected unit only"
      decision: use

inventory_impact:
  decision: confirmed # confirmed | split | merged | renamed | deferred | replaced
  reason: "unit boundary is narrow enough for independent R0 fixtures"

hand_written_replacements:
  - capability: "legacy wrapper error text"
    reference_sources:
      - "third_party/sources/example-1.2.3"
    reason: "crate owns matching; wrapper owns the legacy behavior projection"

legacy_kept:
  - capability: proprietary_sdk
    owner: legacy
    integration: subprocess

verification:
  - "copyable test or fixture command"
```

## Checks

- Toolchains are available (`python`, `cargo`, project build tools).
- Crate reconnaissance matches the mode in `NOTES.md`; missing/blocked agent
  reports and incomplete manual evidence stop the stage.
- `user_disabled` references the acknowledgement stored in `NOTES.md` and
  records residual ecosystem risk instead of pretending that search evidence exists.
- The dependency record names the rewrite preference source and applied profile.
- Every preference deviation has a reason; no `require` or `avoid` rule is
  violated without a new user decision.
- The chosen seam dependencies are present.
- Behavior fixture/test dependencies are present.
- The dependency record explains any legacy-owned capability.
- The dependency record names reference sources for adapter or hand-written behavior.
- The shared dependency registry was checked before adding or hand-writing a
  capability.
- Shared hand-written or patched capabilities have one canonical project path,
  owner, consumer list and verification record.
- No reusable dependency path points to `/tmp` or an agent-private directory.
- Under coordinated parallel execution, only the coordinator changed shared
  Cargo manifests, lockfiles, workspace members, patch configuration or the
  canonical registry.
- `behavior_verification` names an independently comparable legacy public seam
  before writer work; a failed parity review does not authorize a Rust-only oracle.
- First-layer direct dependency snapshots are indexed when the project performs
  repository initialization.
- Second-layer or deeper dependency expansion has public-seam call-path evidence;
  lockfile transitivity alone is not enough.
- Low-level native/compiler/runtime differences are ignored unless they affect
  public behavior, memory/ABI contracts, persistence, security, or model/numeric
  correctness.
- The dependency record does not treat fewer Rust dependencies as a success
  metric.
- Under `standard` or `ecosystem_first`, enabled/manual reconnaissance challenges
  unnecessary full hand-written rewrites when a crate can safely own a stable
  lower layer.
- Under a hand-written profile, domain crate reuse is rejected or explicitly
  reconciled with the recorded user preference.
- Full hand-written replacements under `standard` or `ecosystem_first` include a
  tradeoff explaining why crate reuse plus adapter is worse for this unit.
- The manifest is re-cut before writer work if the current unit is too broad.
- The next skill can bootstrap the seam without guessing.
