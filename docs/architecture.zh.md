# 架构

[English version](architecture.md)

py2rs 不要求固定目录结构。它定义的是渐进式重写的控制面和审核纪律。

这是一套 meta-skill 架构。核心 skills 描述的是如何创造项目专属 rewrite skills；在项目还没有自己的事实、约束、manifest 和接受的 seam 之前，它们不是可以直接套用的成品工作流。

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

## 状态化工作区

工作区应该让多轮会话中的进展可持久化。这个结构借鉴了 [`teach`](../skills/foundations/teach/SKILL.md)：

- mission：为什么重写，什么不能丢。
- resources：source-of-truth docs、依赖源码和可信参考。
- notes：用户偏好、项目约束和临时观察。
- records：非显然迁移经验和决策。
- manifest：当前状态、owner、verification 和 rollback。
- reviews：支撑 promotion 决策的持久证据。

没有这些状态，loop 就会变成依赖记忆。py2rs 的假设是：记忆不够。

## 粒度配置

初始化仓库时应该询问用户迁移单元要切多细。

可用词汇：

- `coarse`：单元和审核更少，适合低风险 helper 或成本敏感任务。
- `balanced`：默认；单元能独立验证，但不把每个 helper 都拆成一轮审核。
- `fine`：适合 public payload、parser、数据结构、错误投影、持久化、model IO 和依赖兼容层。
- `ultra_fine`：例外情况；当 ABI、内存、数值/模型正确性或回滚精度比成本更重要时使用。

单元越细，审核轮次和 token 成本越高，但也会降低幻觉、死代码和行为漂移风险。

## 重写偏好

初始化仓库时使用独立的偏好画像，记录用户希望以多大力度复用 Rust 生态依赖，以及对相关框架是否已有偏好。它存放在 `NOTES.md`，不写入 manifest：

- `standard`：默认按能力权衡稳定 crate、adapter 和 fixture-backed 手写实现。
- `ecosystem_first`：尽量复用维护良好的 crate。
- `handwritten_first`：优先手写项目/领域行为，但允许通用基础设施。
- `domain_from_scratch`：从底层重写领域栈，但仍允许 `std`、异步运行时、序列化、诊断、tracing、transport 和构建工具。
- `custom`：按能力记录专属规则。

总体策略确认后，只询问项目实际检测到的框架类别，例如 async、错误/tracing、数值/ML、Web、UI 或持久化。skills 中的 crate 名只是示例，实际选择必须结合当前项目和当时的官方资料。

初始化只记录选择，不添加 crate，也不修改 lockfile。等 seam 或迁移单元确实需要该能力时，依赖对齐再应用画像。`require` 和 `avoid` 这类硬偏好不能被静默覆盖。

## 依赖对齐

依赖按能力对齐，不按包名一一对应。

合法路径：

- fixtures 证明 crate 直接覆盖行为。
- crate 负责稳定底层，compatibility adapter 补齐 Python 语义。
- 针对语义差异写窄 hand-written replacement。
- 当全手写比 crate + adapter 更小、更安全、更容易验证时，允许全手写。

Rust 依赖更少不是成功指标。在 `standard` 下，全量造轮子也不是默认偏好。选择必须符合已记录的重写画像，并在每个单元中记录如何应用偏好或为何调整。

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
