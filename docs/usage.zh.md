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
5. 询问用户 granularity profile。
6. 创建或复用 manifest/control plane。
7. 在存储、license 和项目政策允许时，snapshot 第一层直接 Python 依赖源码。
8. 在实现前定义回滚路径。

采集偏好时不添加 crate，也不修改 lockfile。侦察可以选择 `agent`、`manual` 或 `disabled`；关闭可以节省 token，但用户需要熟悉或手动检索 Rust 生态。满足侦察策略并完成依赖对齐后，才真正加入和锁定依赖。

`agent` 模式需要可用的 Context7。缺失时按 [`安装教程`](installation.zh.md#配置-context7) 先安装/配置；工具缺失不能作为“没有合适 crate”的证据。`disabled` 只跳过独立、比较式生态侦察，不免除对最终选中依赖的最小官方资料核验，也不能声明生态覆盖完整。

初始化时应该保留 [`teach`](../skills/foundations/teach/SKILL.md) 式渐进模型：mission first、resources before memory、records 记录非显然经验、notes 保存偏好、小单元配合反馈循环。

当 seam 和状态模型稳定后，把固定的项目流程脚手架化为 script-backed skills。架构判断继续留在 reasoning skills；重复的 registry 查询、状态迁移、fixture 编排和报告校验放进经过测试的代码，让后续会话只消费 schema，不再用 prompt 重建机械流程。每个角色独立选择 `prompt` 或 `scaffold`，只把选中形态留在 skill discovery roots，另一形态归档到目录之外；模式切换后开启新会话。

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

## 推进一个单元

1. 从 manifest 选择一个迁移单元。
2. 满足 `NOTES.md` 中的 crate 侦察模式：fresh agent 报告、manual 证据或已确认风险的 disabled 状态。
3. 在依赖对齐中应用侦察报告/状态和重写偏好。
4. 添加或识别 behavior fixtures。
5. 在接受的 seam 后实现。
6. 把单元标为 `reimplemented`，不是 `verified`。
7. 运行 R0 行为审核。
8. 运行 manifest 要求的其它 review roles。
9. 只有在 review evidence 存在后才能 promotion。

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
- writer workflow。
- review roles。
- promotion rules。
- 不可违反的项目约束。

本仓库的实践 skills 展示了两个不同结果：Tauri backend facade 重写，以及依赖复杂的 Python 项目重写。
