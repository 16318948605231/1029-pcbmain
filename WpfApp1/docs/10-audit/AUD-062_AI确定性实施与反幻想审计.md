# AI确定性实施与反幻想审计
- 文档 ID：`AUD-062`
- 版本：`1.0.0`
- 状态：`PASS_WITH_EXTERNAL_GATES`
- 审计基线：`ARCH-PCBA-VISION-001 v0.5.3` + `Asun Vision Development Standard v2.1.5`
- 范围：除硬件具体 SDK 外的全量开发准备文档、开发步骤、FunctionSpec、PageContract、工具、权威绑定和语义链路

## 1. 新 Agent 威胁模型

假设 Agent 从零开始，没有本次会话记忆，只允许读取：Architecture、GATE-001、Guide、FS、Contract/Schema、State/Owner、PageContract、Test/Benchmark。审查它是否仍可能自行补齐未知事实。

## 2. 必须可回答

每个 FS 必须能回答：做什么、不要做什么、输入是什么、输出是什么、Port 在哪里、项目在哪里、Primary/Fallback/Reject 是什么、参数来自哪里、什么状态阻断、什么证据提交、怎么取消、怎么重试、怎么恢复、怎么测试、怎么 Benchmark、什么 UI 页面、什么是 ScopeDrift。

## 3. 强制停止条件

缺字段/枚举/单位/坐标系/阈值/Owner/State/AuthorityScope/API/算法选择条件/硬件时序/Acceptance 时，必须 `Blocker` 或 `Unverified`；不得使用模型记忆、GitHub 示例或编译报错推断项目事实。

## 4. 编码前输出

Agent 必须先给出影响文件、依赖图、接口变化、算法路由、状态/错误表、测试/Benchmark 方案和未知项；未得到批准不得直接扩大 Scope。

## 5. 编译错误与测试失败

编译失败只说明实现与当前契约/环境不一致，不等于有权改 Contract。测试失败只触发缺陷修复或变更流程，不等于降低 Acceptance。
