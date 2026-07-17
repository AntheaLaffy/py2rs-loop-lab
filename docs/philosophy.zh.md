# 思想

[English version](philosophy.md)

py2rs 是一种用于受控重写的 loop engineering 纪律。

它不是为了最大化创意。它的目标是在 AI agent 执行重复迁移工作时保留工程控制。如果任务需要自由发散、产品品味或开放式探索，这个仓库不是合适工具。如果任务需要有边界的重写、行为一致性、审核门禁和回滚能力，它才合适。

这个仓库里的 skills 是架构和思想 skills。它们主要是用来创造其它 skills 的 skills。一个项目不应该一开始就盲目运行它们，而应该先理解项目、编写项目专属 skills、初始化重写工作区，然后再进入 loop。

## 来自 teach 的渐进思想

py2rs 的渐进模型很大一部分来自 [`teach`](../skills/foundations/teach/SKILL.md) skill；该 skill 原始来源是 Matt Pocock 的 [`mattpocock/skills`](https://github.com/mattpocock/skills) 仓库。

在 `teach` 里，学习不是一次回答，而是一个状态化工作区：

- `MISSION.md` 让学习理由始终可见。
- `RESOURCES.md` 让 agent 先依赖资源，而不是依赖记忆。
- records 捕捉未来还会用到的非显然经验。
- notes 保存用户偏好和工作上下文。
- 每个 lesson 都小而自洽，并且绑定 mission。
- 进步来自反馈循环，而不是一次性输出。

py2rs 把这些思想映射到重写工程里：

- mission 变成重写理由和约束。
- resources 变成 source-of-truth docs、依赖源码和高置信参考。
- learning records 变成 rewrite records 和 review reports。
- lessons 变成 migration units。
- retrieval/feedback 变成 behavior fixtures、R0 checks 和 reviewer gates。
- 状态化学习变成 manifest 驱动的重写工作区。

所以 py2rs 不是“让 AI 直接重写”。它是一种让 loop 在多轮会话中仍然保持上下文和约束的方法。

## 人定义约束

人负责定义 loop 的边界：

- 为什么要重写。
- 哪个架构 seam 被接受。
- 哪些公共行为不能变。
- 迁移单元切多细。
- 审核预算和 token 预算。
- 依赖源码展开策略。
- 复用 crate、写 adapter 或造轮子的取舍。
- 哪些项目规则应该沉淀成专属 skills。

AI 在这些约束里工作。

## AI 在 Loop 里执行

AI 仍然可以做大量工作：

- 读取项目事实。
- 提议或重切 manifest 单元。
- 一次实现一个迁移单元。
- 添加 fixtures 和 tests。
- 产出审核报告。
- 维护迁移状态。
- 记录可复用经验。

重点是让快速 loop 仍然产出可理解、可审核、可回滚的代码。

## 为什么用 Skills

Skills 是人类意图和 AI 执行之间的可复用边界。好的 skill 会记录：

- 什么时候使用。
- 先读哪些上下文。
- 哪个架构被接受。
- 哪些决策不在范围内。
- 如何产生证据。
- 什么算完成。

py2rs 是通用纪律。项目专属 skills 是这套纪律落地的地方。
