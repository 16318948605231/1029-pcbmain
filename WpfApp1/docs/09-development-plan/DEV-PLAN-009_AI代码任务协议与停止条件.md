> 2026-09-27适用性：本页保留既有实现规划/注册信息。当前文档阶段以[平台设计基线](../00-baseline/PLATFORM-DESIGN-BASELINE.md)和SM/PG目录为准；本页历史状态、69项覆盖或波次不构成自动开工授权，逐切片核对Contract/Owner/验收。

# AI 代码任务协议与停止条件
- 文档 ID：`DEV-PLAN-009`
- 版本：`1.1.0-prep`
- 状态：`Normative`

## 1. 固定循环

`READ → PLAN → VERIFY → FREEZE → IMPLEMENT → TEST → REVIEW → AUDIT`

## 2. READ

必须读取：Architecture、Guide、FS、Contract/Schema、State/Owner、PageContract（若有）、依赖 FS、Golden/Replay、当前实际仓库相关代码。

## 3. VERIFY

必须验证：文件是否真实存在、类型/接口是否真实存在、API/算子是否属于目标版本、引用版本/hash 是否匹配、Task Scope 是否完整。

## 4. FREEZE

实施前必须形成 Task Card：FunctionSpecId、FilesToChange、Contracts、Inputs、Outputs、State、FailurePaths、Tests、Benchmark、Acceptance、ProhibitedPaths、OpenGates。

## 5. STOP

以下任一情况停止**依赖该事实的受影响切片**，定位问题和消费者；独立研究/设计继续：

- 资料缺失；
- 两个权威资产冲突；
- 需要新增未登记 Contract/State/Owner；
- API 无法从实际环境确认；
- 参数/阈值/单位/坐标未冻结；
- 需要修改 Task Scope 之外的文件；
- 测试目标不能由文档推出；
- 需要把 Unknown/Invalid/NotQualified 转成 OK。

停止后在原任务/指导登记准确影响，提交可评审的补充设计或变更；允许继续不依赖该缺口的工作。不得用“合理默认值”、复制DTO或放宽验收继续受影响生产实现。AsunImage/DevExpress按用户决定不安排安装/兼容性/授权准入；API资料读取是正确使用该接口的具体工作。

## 6. REVIEW

实现完成后必须给出：代码 diff → FS 条目映射 → Test evidence → Benchmark → 未验证项 → ScopeDrift 检查 → 文档/Manifest 更新。

## 7. 禁止把“修复编译/测试”当作需求变更授权

- 编译失败只能导致代码实现层修正；不得因此改变 Contract、Schema、状态、Owner、阈值或验收标准。
- 测试失败必须先判断“实现错误 / 标准错误 / 测试错误 / 环境缺失”四类原因；在权威未变更前，默认标准不变。
- 第三方 API 与当前环境不一致时，必须登记 `Unverified` 或 `Blocker`，不得用相似 API 名称替代。
- AI 完成任务必须提交 `ScopeDrift = none` 的证明；若不为 none，任务不得进入完成状态。
