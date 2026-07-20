---
name: "py2rs-env-bootstrap"
description: "[DRAFT] 跑通迁移 seam 的最小环境。根据项目选择 FFI、CLI、service、Tauri command、library 或 pipeline adapter，并证明参数、返回值、错误、日志和并发边界可用。"
---

# py2rs-env-bootstrap — Seam Bootstrap

本阶段只证明“旧/新实现能通过选定 seam 被稳定调用”。不要开始业务迁移。

## Pick The Seam

从 `py2rs-dep-align` 的记录读取 seam 类型、applied rewrite profile、crate
reconnaissance status、实际依赖和 preference deviations。偏好采集本身不能代替
这份单元级依赖记录。还要读取 execution policy、canonical shared dependency
registry，以及并行模式下 coordinator 分配的 Cargo build slot。Confirm the
unit's `behavior_verification` names an independently comparable legacy public
seam.

- `ffi`: Python 调 Rust extension。
- `cli`: legacy caller 调 Rust binary 或反向包装。
- `service`: HTTP/gRPC/API boundary。
- `tauri-command`: desktop command facade。
- `library`: Rust crate API 被旧入口调用。
- `pipeline`: data stage adapter with fixtures.

不要为不需要的 seam 建 demo。

## Demo Matrix

每种 seam 都必须证明：

- 参数传递：字符串、数字、列表/对象或项目核心 payload。
- 返回值：结构化结果能被旧调用方理解。
- 错误：新实现错误能映射为旧接口可处理的错误。
- 日志/trace：调用链能定位到 unit、operation 和 source error。
- 并发/重复调用：不会死锁、污染状态或破坏缓存。
- rollback：切回旧 owner 后同一调用仍可运行。

## Example Deliverables

Use project conventions. If none exist:

```text
bootstrap/
  README.md
  run_all.sh
  cases/
    hello_roundtrip.*
    error_mapping.*
    concurrent_calls.*
```

For Python FFI projects, the old `maturin + pyo3` demo is still valid. For Tauri or service projects, use command/API fixtures instead.

## Acceptance Output

Record results in the manifest or a Stage 0 file:

```yaml
env_bootstrap:
  status: done
  seam: tauri-command
  dependency_record: "rewrite-records/example-dependencies.yaml"
  applied_profile: standard
  crate_reconnaissance: complete
  behavior_verification:
    legacy_public_seam: "tauri command input/output/error boundary"
    required_observations:
      - command roundtrip
      - error projection
    comparison_policy:
      default: exact
      tolerances: []
    evidence: []
  canonical_dependencies:
    - "manifest/shared-dependencies.yaml#burn-missing-capability"
  cargo_build_evidence: "coordinator build record or serial command output"
  cases:
    roundtrip: PASS
    error_mapping: PASS
    trace_context: PASS
    repeated_calls: PASS
    rollback: PASS
  notes:
    - "New backend can be called behind existing command facade."
```

## Failure Handling

- Missing dependency: return to `py2rs-dep-align`.
- Crate reconnaissance is `blocked`, or required evidence is missing: do not
  bootstrap the Rust path. Return to reconnaissance/dependency alignment.
- Cargo manifest/lockfile does not match the applied dependency record: return
  to `py2rs-dep-align`; do not silently add a different framework here.
- A dependency resolves through `/tmp` or an agent-private copy: reject it and
  return to dependency alignment so the implementation is promoted into the
  canonical project root.
- In coordinated parallel mode, a worker has no coordinator build slot: do not
  start a competing Cargo build or create an isolated target directory silently.
- A hard framework preference conflicts with the seam: return to the user
  for a preference decision, then update `NOTES.md` and the dependency record.
- The legacy public seam is missing or cannot support independent old/new
  comparison: return to dependency alignment to move the seam, re-cut the unit,
  defer it, or keep its legacy owner. A compile check is not behavior evidence.
- Bad error mapping: fix the bridge/adapter before business migration.
- Deadlock/blocking behavior: define async boundary before business migration.
- Rollback cannot be shown: the seam is not ready.

## Exit Criteria

- The seam works without business rewrite code.
- Cargo manifests and lockfiles contain the dependencies selected for this seam,
  with no dependency added solely because it appeared in initialization notes.
- Shared dependencies resolve through registry-recorded project paths, not
  temporary or agent-private copies.
- Cargo build evidence follows the serial policy or the coordinator's build queue.
- The seam proves the declared behavior observations against the legacy path.
- Reconnaissance is `complete`, `policy_rejected`, `manual`, or explicitly
  `user_disabled`; the last case remains visible as residual risk.
- The demo uses the project's actual public interface shape where possible.
- The next migration unit can implement behind the seam without choosing new architecture.
