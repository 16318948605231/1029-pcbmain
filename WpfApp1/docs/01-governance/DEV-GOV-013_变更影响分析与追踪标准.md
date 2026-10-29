# 变更影响分析与追踪标准
- 文档 ID：`DEV-GOV-013`
- 版本：`1.1.0`
- 状态：`Normative`

## 1. 任何变更都必须回答

```text
Change
→ Why
→ Affected Contract / Schema
→ Affected State / Owner
→ Affected FunctionSpecs
→ Affected PageContracts
→ Affected Tests / Golden / Benchmark
→ Affected Qualification
→ Migration / Compatibility
→ Release / Manifest
```

## 2. AI/人工禁止的“顺手修改”

不能因为编译失败、测试失败、UI 绑定不便、性能不足或第三方 API 不熟悉而顺手修改无关 Contract、领域边界、生产状态、数据库结构或 UI 交互语义。

## 3. 文件范围冻结

每个任务先明确 `FilesToChange` 范围，可放在现有任务描述或指导中，不强制新建文件。范围内必要消费者同步属于同一变更；超出批准范围先澄清，不能以顺手修复扩大任务。

## 4. 兼容策略

Schema/Contract 变更必须明确 Major/Minor/Patch 影响、消费者兼容范围、旧版本读取策略和回滚方式。禁止通过隐式字段、字符串或“向下兼容”口号绕过契约审查。

## 5. 按风险选择工具

普通定位、已知调用链的局部修改、文档和测试维护使用 rg、源码/项目引用、语义工具及定向验证。跨模块公共契约、广泛重构，或权限/持久化/设备副作用且调用关系不清时，按需用可用 GitNexus 索引辅助影响核对。

不复制 AOI 索引名或工作树路径。索引失败/UNKNOWN/不完整不等于无风险；改用消费者、引用与回归核对，只暂停仍未收敛的受影响部分。不重复证明已知坏索引，不按每次编辑、提交或恢复自动建图，不更改全局技能。商业交付依赖该工具前仍处理其许可证要求。
