# 架构

[English version](architecture.md)

py2rs 不要求固定目录结构。它定义的是渐进式重写的控制面和审核纪律。

这是一套 meta-skill 架构。核心 skills 描述的是如何创造项目专属 rewrite skills；在项目还没有自己的事实、约束、manifest 和接受的 seam 之前，它们不是可以直接套用的成品工作流。

## 控制面

控制面记录：

- 迁移单元。
- 当前 owner 和目标 owner。
- 公共接口策略。
- behavior verification seam、比较策略与 fixture evidence。
- 验证命令或 fixtures。
- 回滚路径。
- 必需审核角色。
- 审核频率、当前 review batch 和逐单元 verdict。
- manifest partitioning、execution policy、canonical shared dependencies 和 Cargo build policy。
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

Meta-skills 保留架构判断，因为 seam、领域 ownership 和迁移边界依赖项目事实。等这些决策稳定后，仓库初始化应该生成项目专属的 operational skills：文档只记录步骤和 schema，经过测试的脚本负责 registry 采集、状态迁移、review batch 收批、fixture 编排和逐单元报告校验。

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
- `fine`：适合 public payload、parser、数据结构、错误投影、持久化、model IO 和依赖 semantic-delta adapter。
- `ultra_fine`：例外情况；当 ABI、内存、数值/模型正确性或回滚精度比成本更重要时使用。

单元越细，审核轮次和 token 成本越高，但也会降低幻觉、死代码和行为漂移风险。

## 审核频率

迁移单元粒度决定“每块代码有多大”，审核频率决定“写完多少块后启动一次独立审核”。初始化仓库时让用户选择：

- `per_unit`：每个单元写完就审，适合高风险公共契约。
- `batch`：每 N 个单元做一次总审核；用户未选择时默认 N 为 3。
- `end_of_scope`：当前 manifest、shard 或命名 scope 全部写完后再总审，适合小项目。

Review batch 只是审核调度和证据容器，不合并迁移单元各自的 ownership、verification、rollback 或 promotion 状态。

每个 writer 环节仍要运行该单元自己的 verification。通过后，单元保持 `reimplemented` 并进入 open review batch；在独立审核完成前，legacy owner 继续作为默认路径，单元不能 promotion。

达到 N、scope 写完或准备 promotion 时立即收批。默认 `risk_override: flush_batch` 也会在 high-precision domain 边界收批；用户可选 `follow_cadence`，让这些单元遵循总体节奏。审核周期先对整批运行一次 R0，并覆盖单元间集成行为，再按整批所需 review roles 的并集运行其它门禁。每个角色可以为整批写一份报告，但必须逐单元给出 verdict；只有 manifest 没要求该角色的单元才能标成 `not_required`，避免一个失败无差别阻塞其它单元。

## 行为验证

每个单元在实现前记录一个可独立比较的 legacy public seam、该 seam 暴露的输入/输出/错误/副作用、比较策略和 fixture evidence。R0 behavior 在这个 seam 上证明严格的 Python/Rust 行为一致；默认精确比较，模型或数值容差必须来自已有公共契约或实现前明确批准。

例如 Python/Rust 深度学习框架对 tensor shape、dtype、layout 或 artifact 的解释不同，这些差异会穿透到 codec、模型配置和权重加载；只要穿透选定的 application seam，就纳入行为矩阵。如果 framework 内部让当前单元无法独立验证，就把 seam 外移、重切单元或保留 legacy owner。编译结果和 Rust-to-Rust 证据不能替代旧/新行为证据，parity 失败也不能触发 oracle 替换。

这是一次 control-plane breaking change。旧双 oracle schema 中的 legacy-parity 条目可以机械迁移到 `behavior_verification`；只依赖 Rust contracts 的条目不能映射，必须拒绝后重新选择可比较 seam、重切或延后单元，或保留 legacy owner，不提供旧 schema shim。

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
- crate 负责稳定底层，semantic-delta adapter 补齐 Python 语义。
- 针对语义差异写窄 hand-written replacement。
- 当全手写比 crate + adapter 更小、更安全、更容易验证时，允许全手写。

Rust 依赖更少不是成功指标。在 `standard` 下，全量造轮子也不是默认偏好。选择必须符合已记录的重写画像，并在每个单元中记录如何应用偏好或为何调整。

多个单元共享 crate、fork、adapter、生成源码或手写能力时，必须先查 canonical shared dependency registry。像 Burn 缺失能力这样的公共 gap 应先成为项目内 prerequisite unit/shard，只有一个 owner、路径和 build evidence；`/tmp` 与 agent 私有目录只能用于一次性研究。

关闭侦察必须记录为 `user_disabled`，不能伪装成已完成搜索；迁移可以继续，但保留明确的 Rust 生态覆盖风险。

## 源码展开

初始化仓库时，可以把第一层直接 Python 依赖展开或 snapshot 成本地 reference corpus。

第二层或更深依赖必须有 public-seam call-path evidence。lockfile 的传递依赖关系本身不够。py2rs 重写的是项目，不是整个 Python 或 native 生态。

## 清单分片与执行模式

大型重写可以在边界稳定时使用 root manifest + shard manifests。分片用于减少单次上下文、明确 ownership、依赖顺序、review scope 和 rollback；它不表示应该并行。

Shard 必须说明：

- 拥有和排除的单元。
- public seam。
- cross-shard contracts。
- shared prerequisites。
- canonical dependency paths。
- verification commands。
- rollback routes。

默认 `execution_policy.mode: serial`，一个 writer 按 shard dependency order 推进。这通常比多个 Codex 窗口更省 token，也避免 Cargo lock/target contention、重复编译和共享依赖漂移。

只有用户明确接受成本，且 coordinator 已独占 root manifest、shared dependency registry、共享 `Cargo.toml`/`Cargo.lock` 和 serialized build queue 时，才能使用 `coordinated_parallel`。worker 只能改 assigned paths；需要共享依赖变更时提交请求并等待，不能在 `/tmp` 另造一份继续。

Open review batch 默认只能属于一个 manifest 或 shard。跨 shard 的 release readiness 由 root index 汇总。
