# Architecture

py2rs 不强制目录结构。它是一套迁移控制面和审核纪律。

## Control Plane

控制面回答这些问题：

- 有哪些迁移单元。
- 当前 owner 是 legacy 还是 Rust。
- public interface policy 是什么。
- verification command 是什么。
- rollback route 是什么。
- promotion 前需要哪些 review roles。

控制面可以是 YAML manifest、Tauri backend facade、HTTP service adapter、CLI dispatcher、feature flag registry 或 pipeline stage registry。只有当 Python 进程仍然是统一入口时，`runtime/router.py` 才是合适选择。

## Granularity Profile

初始化仓库时要记录单元粒度偏好：

- `coarse`: 更快、更少审核，适合低风险 helper。
- `balanced`: 默认选择，单元可独立验证和回滚，但不把每个 helper 都拆出来。
- `fine`: 适合 public payload、parser、数据结构、错误投影、持久化、model IO 和依赖兼容层。
- `ultra_fine`: 只给高风险契约使用，例如 ABI、内存、数值、模型正确性或极小回滚面。

更细的单元会增加审核轮次和 token 成本，但通常减少 AI 幻觉、死代码和行为遗漏。

## Dependency Alignment

依赖对齐按 capability，不按 package name。

合法路径包括：

- crate 直接覆盖行为，fixture 证明。
- crate 负责稳定底层，adapter 补 Python 语义差异。
- 窄手写 replacement，只负责 crate 不能安全承担的行为。
- 全手写 replacement，当它比 crate + adapter 更小、更安全、更容易验证和回滚。

依赖少不是成功指标。全量造轮子也不是默认偏好。每个选择都要有 reference source、fixture 和 tradeoff 记录。

## Source Expansion

初始化时可以 snapshot 第一层直接 Python 依赖源码，作为本地 reference corpus。

第二层或更深依赖必须有 public-seam call-path evidence，不能因为 lockfile 里存在就递归展开。py2rs 重构的是项目，不是整个 Python/native 生态。

## Review Gates

R0 behavior review 永远优先。后续 review 根据风险选择：

- Rust style
- error tracing
- IO/concurrency
- algorithm/complexity
- architecture/data ownership
- product/ergonomics

Reviewer 可以写 report，但不能改生产代码。
