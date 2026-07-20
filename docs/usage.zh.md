# 用法

[English version](usage.md)

这个仓库不是复制到任意代码库就能直接运行的成品工具。正确用法是让 AI 研究它、借鉴架构，再为具体项目创造项目专属 rewrite skills。

## 安装或参考 Skills

把这个仓库作为设计项目专属 skills 的参考。直接复制 skills 可以用于学习或启动，但真正的重写应该先编码自己的项目事实，再进入 loop。

如果你想先安装到 Codex 或 Claude，直接看 [`安装教程`](installation.zh.md)。推荐把教程里的提示词交给 AI 安装；Codex 默认使用 `$CODEX_HOME/skills`（未设置时为 `~/.codex/skills`），Claude Code 使用 `~/.claude/skills`。

建议从这些开始：

- `skills/py2rs`
- `skills/py2rs-runtime`
- `skills/py2rs-crate-recon`
- `skills/py2rs-dep-align`
- `skills/py2rs-env-bootstrap`
- `skills/py2rs-review-r0-behavior`

再根据风险加入 R1-R6 审核 skills。

## 必须遵守的顺序

1. 先建立具体项目仓库并读取项目事实。
2. 让 AI 提取对这个项目有用的 py2rs 思想。
3. 判断哪些思想适合这个项目，哪些不适合。
4. 根据这些决策创建项目专属 skills。
5. 初始化重写工作区。
6. 只有 manifest/control plane 和 review policy 存在后，才开始 loop。

## 初始化重写工作区

1. 读取项目事实：mission、architecture、resources、manifest、records 和 tests。
2. 识别接受的 seam：CLI、service facade、Tauri command facade、Python module、library API、pipeline stage 或其它项目专属边界。
3. 为 coordination、dependency bootstrap、writer work 和 review gates 编写或改造项目专属 skills。
4. 询问总体重写策略、相关框架类别、crate 侦察模式和 crates.io 代理，并写入 `NOTES.md`；默认使用 `standard` 和 agent 侦察。
5. 询问 granularity，并为每个单元识别一个可独立比较的 legacy public seam；默认精确比较，模型或数值容差必须在 writer 前来自公共契约或明确记录。
6. 询问每几个已实现单元总审：`per_unit`、每 N 个一批，或 `end_of_scope`；未选择时默认每 3 个一批。
7. 创建或复用 manifest/control plane，分别记录 manifest partitioning 与 execution policy。大项目可以分片，但执行默认 serial。
8. 多个单元共享依赖能力时创建 canonical shared dependency registry；`/tmp` 不得作为长期路径。
9. 在存储、license 和项目政策允许时，snapshot 第一层直接 Python 依赖源码。
10. 在实现前定义回滚路径。

采集偏好时不添加 crate，也不修改 lockfile。侦察可以选择 `agent`、`manual` 或 `disabled`；关闭可以节省 token，但用户需要熟悉或手动检索 Rust 生态。满足侦察策略并完成依赖对齐后，才真正加入和锁定依赖。

`agent` 模式需要可用的 Context7。缺失时按 [`安装教程`](installation.zh.md#配置-context7) 先安装/配置；工具缺失不能作为“没有合适 crate”的证据。`disabled` 只跳过独立、比较式生态侦察，不免除对最终选中依赖的最小官方资料核验，也不能声明生态覆盖完整。

初始化时应该保留 [`teach`](../skills/foundations/teach/SKILL.md) 式渐进模型：mission first、resources before memory、records 记录非显然经验、notes 保存偏好、小单元配合反馈循环。

当 seam 和状态模型稳定后，把固定的项目流程脚手架化为 script-backed skills。架构判断继续留在 reasoning skills；重复的 registry 查询、状态迁移、review batch 收批、fixture 编排和逐单元报告校验放进经过测试的代码，让后续会话只消费 schema，不再用 prompt 重建机械流程。每个角色独立选择 `prompt` 或 `scaffold`，只把选中形态留在 skill discovery roots，另一形态归档到目录之外；模式切换后开启新会话。

## 切换项目 Skill 模式

新角色默认从 `prompt` 开始。切换前，两种形态必须拥有相同 skill name、正确的 `.py2rs-skill-variant.json`，且 `validation_evidence` 指向各自目录内真实存在的验证文件。下面以 Claude 项目目录为例；Codex 用户把 `PY2RS_RUNTIME` 和 active/discovery paths 换成对应的 `.codex` 目录。

先从项目根目录 dry-run，并列出项目实际使用的全部 discovery roots：

```bash
PY2RS_RUNTIME="${PY2RS_RUNTIME:-$HOME/.claude/skills/py2rs-runtime}"
switcher="$PY2RS_RUNTIME/scripts/switch_skill_mode.py"

python "$switcher" \
  --role dependency-bootstrap \
  --current-mode prompt \
  --target-mode scaffold \
  --active .claude/skills/project-dependency-bootstrap \
  --archive-root .py2rs/skill-archive \
  --discovery-root .claude/skills \
  --discovery-root .codex/skills
```

确认输出为 `ready` 后，用相同参数增加 `--apply`。脚本会移动两种形态并留下 `switched_pending_notes` journal。立即把输出中的 `notes_update` 写入 `NOTES.md`，然后确认持久状态：

```bash
python "$switcher" \
  --role dependency-bootstrap \
  --archive-root .py2rs/skill-archive \
  --ack-notes
```

只有输出 `notes_acknowledged` 后才开启新会话。如果出现 `manual_recovery_required`，保留 journal，按其中记录的 paths 和 phase 恢复；不要用新副本覆盖 active path。完整不变量见 [`架构`](architecture.zh.md#模式生命周期)。

## 推进一个写入/审核批次

1. 从 manifest 选择一个迁移单元。
2. 满足 `NOTES.md` 中的 crate 侦察模式：fresh agent 报告、manual 证据或已确认风险的 disabled 状态。
3. 在依赖对齐中应用侦察报告/状态和重写偏好，并先检查 canonical shared dependencies。
4. 确认 `behavior_verification` 已记录 legacy public seam 和比较策略。
5. 为该 seam 添加 Python/Rust behavior fixtures。
6. 在接受的 seam 后实现。
7. 运行 writer verification；通过后标为 `reimplemented` 并加入 open review batch。
8. 若尚未达到 review cadence 且没有早期收批条件，继续选择下一个单元。
9. 达到 N、scope 完成或准备 promotion 时收批；高风险边界按 `risk_override` 决定。
10. 对每个单元先运行 R0 behavior，再运行其它 roles；每份报告逐单元给 verdict。
11. 只有单元自己的全部 review evidence 存在后才能 promotion。

## 清单分片与执行

清单分片是大项目的控制面工具，不是并行开关。推荐按 stable contracts 分 shard，再由一个 writer 按 dependency order 串行推进。这样能复用上下文和 Cargo artifacts，避免多个 agent 重复读项目、竞争编译或产生不一致的手写依赖。

只有明确选择 `coordinated_parallel` 时才启动多个 writer。coordinator 独占 root manifest、shared dependency registry、共享 Cargo files 和 build queue；worker 只改 assigned shard，需要共享依赖变更时提交请求并等待。

## 先构建项目专属 Skills

当项目模式稳定后，py2rs 通常应该发展出项目专属 skills。

好的项目 skill 会编码：

- 接受的架构 seam。
- source-of-truth docs。
- manifest 位置和状态模型。
- 重写力度和框架偏好画像。
- crate 侦察和 registry 代理策略。
- 每个角色的 `prompt`/`scaffold` 选择和 discovery 目录外归档位置。
- 依赖展开策略。
- behavior verification seam、比较策略和 fixture evidence。
- manifest partitioning、默认串行 execution policy、canonical dependency registry 和 Cargo build policy。
- writer workflow。
- review roles、review cadence 和 batch flush rules。
- promotion rules。
- 不可违反的项目约束。

本仓库的实践 skills 展示了两个不同结果：Tauri backend facade 重写，以及依赖复杂的 Python 项目重写。
