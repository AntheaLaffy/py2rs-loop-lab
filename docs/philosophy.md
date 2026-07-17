# Philosophy

py2rs 是一种 human-constrained loop engineering 方法。

它承认 AI 在迁移工程中很强：可以读代码、写代码、补测试、写审核报告、维持 manifest 状态。但它也承认一个现实：如果规划、书写、审核、演进方向全交给 AI，人就只剩下“开 loop”和“看结果”的角色。

py2rs 试图把人的创意和判断力放回系统里。

## What The Human Owns

- 项目为什么要迁移。
- 哪些公共行为不能变。
- 哪些 seam 被接受，哪些架构不该引入。
- 单元切分粒度：速度、token 成本、审核成本和质量之间的取舍。
- 依赖策略：复用 crate、写 adapter、局部造轮子或全量造轮子的权衡。
- 哪些实践经验应该固化成项目专属 skill。

## What The AI Owns

- 在既定约束下推进一个迁移单元。
- 收集行为证据。
- 写 fixture、实现和 review report。
- 维护 manifest 状态。
- 在依赖展开后提出重切、合并、延期或替换单元。

## The Difference From Generic Vibecoding

Generic vibecoding 往往把 loop 看成“让 AI 自己规划、自己写、自己审、自己继续”。py2rs 把 loop 拆开：

- writer 不审自己的代码。
- behavior review 是第一门。
- manifest 状态必须对应事实。
- 依赖展开有边界。
- 低层 native/runtime 差异默认不追，除非穿透到 public seam。
- 项目专属约束可以写成 skills，让 AI 下次继续服从这些约束。

The point is not to slow AI down. The point is to give it rails sharp enough that speed still produces engineering-quality code.
