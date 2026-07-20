---
name: "py2rs-review-r3-io-concurrency"
description: "[DRAFT] 第 3 轮 IO、并发与运行时人体工学审查。对一个迁移单元或已收批的 review batch 检查阻塞 IO、async 边界、取消、重试、并发限制和运行时嵌套；默认审查不改生产代码。"
---

# R3 IO And Concurrency Review

R3 关注系统是否会因为 IO、运行时边界或无界并发而卡住、死锁或难以恢复。

## Preconditions

- The R0 behavior report exists.
- R2 error/tracing review is complete or explicitly deferred.
- Every in-scope unit's runtime context is known: CLI, service, Tauri, Python bridge, batch worker or library.

## Review Focus

- Blocking IO in async command/service paths.
- Nested runtime creation such as Tokio inside an existing Tokio runtime.
- Cancellation behavior for long-running work.
- Retry and backoff for recoverable network/external failures.
- Progress/event/log behavior for long operations.
- Concurrency limits: semaphore, queue, bounded worker pool or documented serial behavior.
- Trace/context propagation across spawned tasks.

## Workflow

1. Confirm the unit or closed review batch, included unit ids and runtime environments.
2. Inspect IO paths: filesystem, network, DB, process, bridge and event channels.
3. Run narrow non-mutating checks or tests when practical.
4. Look for user-visible hangs, unbounded waits and stuck partial state.
5. Save a report with promotion decision.

## Code Changes

Default review-gate mode does not edit production code. If explicitly asked to remediate:

- Keep public behavior stable.
- Preserve cancellation/progress contracts.
- Avoid broad algorithm or storage redesigns.
- Require the R0 behavior gate to be rerun after changes.
- Do not write the final pass report for your own patch.

## Report

Use project convention or:

```text
reviews/YYYY-MM-DD-<unit-or-batch-id>-async-ergonomics.md
```

Include:

- Scope reviewed
- Included unit ids and per-unit verdicts (`not_required` only when the manifest
  does not require R3 for that unit)
- Runtime/IO interfaces inspected
- Findings ordered by severity
- Checks or benchmarks run
- Residual risk
- Promotion decision

## Non-Negotiables

- No blocking HTTP/file transfer inside async command paths unless isolated and justified.
- No unbounded concurrency.
- No swallowed cancellation.
- Do not change algorithms for speed here unless the change is strictly required by the IO model and R0 still passes.
