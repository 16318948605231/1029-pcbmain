> 2026-09-27适用性：本页保留既有实现规划/注册信息。当前文档阶段以[平台设计基线](../00-baseline/PLATFORM-DESIGN-BASELINE.md)和SM/PG目录为准；本页历史状态、69项覆盖或波次不构成自动开工授权，逐切片核对Contract/Owner/验收。

# AI Code Task Traceability
- 文档 ID：`DEV-PLAN-007`
- 版本：`1.1.0`
- 状态：`DocMapped`

## 1. 任务卡必须字段

`TaskId / FunctionSpecId / GuideId / ContractIds / SchemaRefs / Owner / Inputs / Outputs / FilesToChange / Tests / Benchmark / UI / FailurePaths / Acceptance / ProhibitedPaths / Evidence / Risks`。

## 2. AI 执行协议

```text
READ → PLAN → VERIFY REFERENCES → IMPLEMENT → TEST → REVIEW → REPORT
```

AI 不得从自然语言需求直接跳到 IMPLEMENT。

## 3. Scope Drift 与回滚

- AI 任务开始前必须生成 `FilesToChange`。实际变更超过该集合即标记 `ScopeDrift`。
- ScopeDrift 未批准前不得合并。
- Contract/Schema/State/Owner 发生变化时，原任务必须暂停并重新进行 Change Impact Analysis。
- AI 不得通过改写测试预期、删除失败样本或放宽门槛来“修复”失败。

## 4. 允许自动化

- 生成样板代码；
- 生成 DTO/mapper/test fixtures；
- 生成纯函数算法骨架；
- 批量补充 UI AutomationId；
- 生成测试矩阵和 benchmark harness；
- 运行静态审计。

## 5. 必须人工/实机批准

- 生产阈值；
- 计量资格；
- 实机时序；
- 安全控制；
- 设备动作；
- 生产 MachineDecision authority；
- AI 从 Advice → Automatic 的升级。

## 6. 漂移检测

每次 AI PR 必须重新运行文档/契约/依赖/Owner/禁止路径审计；任何架构冲突先阻断 PR，不允许“先写了再讨论”。
