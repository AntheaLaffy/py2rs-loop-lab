# 用法

[English version](usage.md)

这个仓库不是复制到任意代码库就能直接运行的成品工具。正确用法是让 AI 研究它、借鉴架构，再为具体项目创造项目专属 rewrite skills。

## 安装或参考 Skills

把这个仓库作为设计项目专属 skills 的参考。直接复制 skills 可以用于学习或启动，但真正的重写应该先编码自己的项目事实，再进入 loop。

建议从这些开始：

- `skills/py2rs`
- `skills/py2rs-runtime`
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
4. 询问用户 granularity profile。
5. 创建或复用 manifest/control plane。
6. 在存储、license 和项目政策允许时，snapshot 第一层直接 Python 依赖源码。
7. 在实现前定义回滚路径。

初始化时应该保留 [`teach`](../skills/foundations/teach/SKILL.md) 式渐进模型：mission first、resources before memory、records 记录非显然经验、notes 保存偏好、小单元配合反馈循环。

## 推进一个单元

1. 从 manifest 选择一个迁移单元。
2. 如果单元触及第三方行为、native code、宽泛 package API、fixtures 或不清楚的 rollback，先做依赖对齐。
3. 添加或识别 behavior fixtures。
4. 在接受的 seam 后实现。
5. 把单元标为 `reimplemented`，不是 `verified`。
6. 运行 R0 行为审核。
7. 运行 manifest 要求的其它 review roles。
8. 只有在 review evidence 存在后才能 promotion。

## 先构建项目专属 Skills

当项目模式稳定后，py2rs 通常应该发展出项目专属 skills。

好的项目 skill 会编码：

- 接受的架构 seam。
- source-of-truth docs。
- manifest 位置和状态模型。
- 依赖展开策略。
- writer workflow。
- review roles。
- promotion rules。
- 不可违反的项目约束。

本仓库的实践 skills 展示了两个不同结果：Tauri backend facade 重写，以及依赖复杂的 Python 项目重写。
