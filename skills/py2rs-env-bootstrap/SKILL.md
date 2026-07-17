---
name: "py2rs-env-bootstrap"
description: "[DRAFT] 跑通迁移 seam 的最小环境。根据项目选择 FFI、CLI、service、Tauri command、library 或 pipeline adapter，并证明参数、返回值、错误、日志和并发边界可用。"
---

# py2rs-env-bootstrap — Seam Bootstrap

本阶段只证明“旧/新实现能通过选定 seam 被稳定调用”。不要开始业务迁移。

## Pick The Seam

从 `py2rs-dep-align` 的记录读取 seam 类型：

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
- Bad error mapping: fix the bridge/adapter before business migration.
- Deadlock/blocking behavior: define async boundary before business migration.
- Rollback cannot be shown: the seam is not ready.

## Exit Criteria

- The seam works without business rewrite code.
- The demo uses the project's actual public interface shape where possible.
- The next migration unit can implement behind the seam without choosing new architecture.
