# 架构

[English version](architecture.md)

py2rs 不要求固定目录结构。它定义的是渐进式重写的控制面和审核纪律。

## 控制面

控制面记录：

- 迁移单元。
- 当前 owner 和目标 owner。
- 公共接口策略。
- 验证命令或 fixtures。
- 回滚路径。
- 必需审核角色。
- 当前状态。

控制面可以是 YAML manifest、Tauri backend facade、HTTP adapter、CLI dispatcher、feature flag registry 或 pipeline stage registry。只有当 Python 仍然是统一编排进程时，Python router 才合适。

## 粒度配置

初始化仓库时应该询问用户迁移单元要切多细。

可用词汇：

- `coarse`：单元和审核更少，适合低风险 helper 或成本敏感任务。
- `balanced`：默认；单元能独立验证，但不把每个 helper 都拆成一轮审核。
- `fine`：适合 public payload、parser、数据结构、错误投影、持久化、model IO 和依赖兼容层。
- `ultra_fine`：例外情况；当 ABI、内存、数值/模型正确性或回滚精度比成本更重要时使用。

单元越细，审核轮次和 token 成本越高，但也会降低幻觉、死代码和行为漂移风险。

## 依赖对齐

依赖按能力对齐，不按包名一一对应。

合法路径：

- fixtures 证明 crate 直接覆盖行为。
- crate 负责稳定底层，compatibility adapter 补齐 Python 语义。
- 针对语义差异写窄 hand-written replacement。
- 当全手写比 crate + adapter 更小、更安全、更容易验证时，允许全手写。

Rust 依赖更少不是成功指标。全量造轮子也不是默认偏好。选择哪条路径必须记录为 tradeoff。

## 源码展开

初始化仓库时，可以把第一层直接 Python 依赖展开或 snapshot 成本地 reference corpus。

第二层或更深依赖必须有 public-seam call-path evidence。lockfile 的传递依赖关系本身不够。py2rs 重写的是项目，不是整个 Python 或 native 生态。

## Manifest Shards

大型重写可以在边界稳定时使用 root manifest + shard manifests，让多个 Codex session 并行。

Shard 必须说明：

- 拥有和排除的单元。
- public seam。
- cross-shard contracts。
- shared prerequisites。
- verification commands。
- rollback routes。

Sharding 是为了真正的独立推进，不是为了掩盖不清楚的架构。
