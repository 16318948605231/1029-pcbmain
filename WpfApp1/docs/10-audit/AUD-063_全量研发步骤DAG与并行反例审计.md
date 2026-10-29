# 全量研发步骤 DAG 与并行反例审计
- 文档 ID：`AUD-063`
- 版本：`1.0.0`
- 状态：`PASS_WITH_EXTERNAL_GATES`
- 审计基线：`ARCH-PCBA-VISION-001 v0.5.3` + `Asun Vision Development Standard v2.1.5`
- 范围：除硬件具体 SDK 外的全量开发准备文档、开发步骤、FunctionSpec、PageContract、工具、权威绑定和语义链路

## 1. 审计目标

从团队同时运行多个 AI/开发者的最坏场景检查：共享 Schema、Owner、Manifest、Acceptance、PageContract、Term Registry 是否可能产生竞争修改。

## 2. 必须串行化

Schema Major、AuthoritySource、Owner/State、Event Catalog、Manifest Schema、AcceptanceProfile、PageContract Catalog、Term Registry、Module Registry 等单点权威只能有一个写入线程；其他任务可以围绕已冻结版本并行。

## 3. 可并行边界

不同 FunctionSpec、不同领域内部模块、不同测试/Benchmark、不同 UI PageContract 可并行，但跨域共享 Contract 变更必须先暂停受影响任务并重新计算 DAG。

## 4. 反例

- 两个 Agent 同时修改同一 Schema；
- SPI Agent 为方便添加第二个 Owner Registry；
- UI Agent 为绕过状态门禁直接写 Fact；
- Quality Agent 自己重算判定；
- 性能 Agent 通过降低 Coverage 偷换性能；
- 领域 Agent 为“未来复用”提前上提不稳定工艺逻辑；
- 一个 Agent 的成功实现改变另一个 Agent 的 Acceptance。

## 5. 处理

所有冲突均以权威版本、Task Traceability 和 ScopeFreeze 为准；冲突任务进入 `BLOCKED_SHARED_AUTHORITY_CHANGE`，完成影响分析后再恢复。
