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

## 项目 Skill 脚手架

Meta-skills 保留架构判断，因为 seam、领域 ownership 和迁移边界依赖项目事实。等这些决策稳定后，仓库初始化应该生成项目专属的 operational skills：文档只记录步骤和 schema，经过测试的脚本负责 registry 采集、状态迁移、fixture 编排和报告校验。

这样可以减少重复的 prompt 机械流程，但不会假装代码生成可以替代架构推理。流程仍在变化时，角色使用 `prompt` 模式；机械步骤稳定后再切换到 `scaffold` 模式。同一角色只能有一种形态可被发现，另一种必须归档到所有 agent skill roots 之外，切换后开启新会话。输入、输出或失败模式仍不稳定的流程不能提前脚手架化。

### 模式生命周期

模式按角色选择，不是整个项目只能统一选择一种。新生成的角色默认使用 `prompt`；只有输入、输出、失败路径、完成标准和恢复方式已经稳定，并且存在测试或 forward-test 证据时，才允许切换为 `scaffold`。

同一角色的两种形态必须使用相同的 skill name，并在 `.py2rs-skill-variant.json` 中记录 role、mode 和指向真实文件的 `validation_evidence`。激活形态位于 agent discovery root，非激活形态位于项目的 `.py2rs/skill-archive` 或其它明确不参与 discovery 的目录。所有实际使用的 Claude、Codex 或其它 discovery roots 都必须参与重复检查；只换一个目录名不能规避“每个角色只能激活一种形态”的约束。

模式切换是一项持久状态迁移：先 dry-run，再在同一文件系统内通过 lock 和 journal 移动两种形态。文件切换成功后 journal 保持 `switched_pending_notes`，直到 `NOTES.md` 写入新 mode、active path 和 archived path，并显式 acknowledgement。只有 journal 清除后才能开启新会话。当前会话已经加载的旧指令无法靠移动文件撤回，因此新会话是正确性要求，不只是使用建议。

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

同一份 `NOTES.md` 画像还会选择 crate 侦察模式：

- `agent`：默认；由 fresh-context researcher 产出有界的 crates.io 和 Cargo 依赖证据。
- `manual`：由用户提供候选、features 和 dependency paths，节省 agent token。
- `disabled`：提示用户需要熟悉或手动检索 Rust 生态后，跳过侦察证据。

Registry 代理也是项目使用偏好。只在 `NOTES.md` 中保存非敏感 URL 或环境变量引用，不提交机器专属 Cargo 配置或凭据。

初始化只记录选择，不添加 crate，也不修改 lockfile。等 seam 或迁移单元确实需要该能力时，依赖对齐再应用画像。`require` 和 `avoid` 这类硬偏好不能被静默覆盖。

## 依赖对齐

依赖按能力对齐，不按包名一一对应。

启用侦察时使用三层证据，三者不能互相替代：

- registry search 按公共能力发现最相关的 3 个候选，并额外加入所有用户点名候选；点名候选不占 Top 3 名额。
- Context7 定向核对候选的 API、features 和官方示例；工具缺失时先安装/配置，只有 setup、服务访问或索引失败时才明确回退到 docs.rs 或 crate source。
- Cargo `info`、`metadata` 和 `tree` 证明实际解析版本、feature selection 和 dependency paths，找到真正的 container、codec、runtime 或其它能力 owner。

不能只看 umbrella crate 的公开 API 就拒绝它。`direct` 表示目标实现可以调用候选的公开 API；`backend` 表示目标实现应该绕过 umbrella API，直接调用 feature-selected 下层依赖。依赖对齐默认只消费精简报告，只有质疑结论时才加载原始证据。

合法路径：

- fixtures 证明 crate 直接覆盖行为。
- crate 负责稳定底层，compatibility adapter 补齐 Python 语义。
- 针对语义差异写窄 hand-written replacement。
- 当全手写比 crate + adapter 更小、更安全、更容易验证时，允许全手写。

Rust 依赖更少不是成功指标。在 `standard` 下，全量造轮子也不是默认偏好。选择必须符合已记录的重写画像，并在每个单元中记录如何应用偏好或为何调整。

关闭侦察必须记录为 `user_disabled`，不能伪装成已完成搜索；迁移可以继续，但保留明确的 Rust 生态覆盖风险。

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
