> 2026-09-27适用性：本页保留既有实现规划/注册信息。当前文档阶段以[平台设计基线](../00-baseline/PLATFORM-DESIGN-BASELINE.md)和SM/PG目录为准；本页历史状态、69项覆盖或波次不构成自动开工授权，逐切片核对Contract/Owner/验收。

# 69项功能实现蓝图
- 文档 ID：`DEV-PLAN-005`
- 版本：`1.0.0-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：当前开发准备包中 69 个功能/能力切片的实施级蓝图
- 直接依赖：`DEV-PLAN-003`, `DEV-GOV-004`, `DEV-GOV-007`, `DEV-GOV-008`, `DEV-VIS-021`, `DEV-PLT-014`
- 主要输出：功能级输入/输出、执行顺序、异常、性能、UI、测试和 AI 实施边界

> 本文是代码任务拆分与 AI 实施的中间层，不替代各领域 Development Guide、现有权威 Schema 或状态/Owner 规范。任何字段、状态、API、HALCON operator 必须以实际仓库/目标版本资料为准；下文不给出未经证实的具体数值阈值。

## 0. 统一实现骨架

```text
Load Contract/Schema
→ Resolve Authority + Scope
→ Validate Input
→ Normalize / Prepare ROI
→ Execute algorithm / business rule
→ Quality Gate
→ Candidate / Measurement / Fact / Proposal
→ Commit only at approved owner
→ Evidence + Receipt
→ UI projection
→ Replay / Test / Benchmark
```

每个功能至少实现：正常路径、拒识路径、取消/超时、恢复、可回放输入、性能计时点、证据引用和 UI 下一步提示（涉及 UI 时）。

## 1. Platform / Identity Resolution

- FunctionSpec：`FS-001`
- PerformanceProfile：`PF-FS-001`

- 关联指导：`DEV-PLT-010`
- 输入：`CodeReader/Hermes/MES/Human Observation`
- 输出：`IdentityResolutionReceipt/BoardIdentity`
- 算法/逻辑基线：`policy + conflict resolution`
- 鲁棒性重点：`duplicate/conflict/unresolved retained`
- 性能重点：`PF-FS-001; profile-bound benchmark`
- UI 工作区：`Identity/Admission workspace`
- 测试基线：`replay + conflict + restart`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `policy + conflict resolution` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 2. Platform / Effective Runtime Manifest

- FunctionSpec：`FS-002`
- PerformanceProfile：`PF-FS-002`

- 关联指导：`DEV-PLT-010`
- 输入：`Product/Program/Recipe/Machine/Calibration/Library`
- 输出：`immutable closure`
- 算法/逻辑基线：`graph closure + hash`
- 鲁棒性重点：`missing/incompatible/withdrawn`
- 性能重点：`PF-FS-002; profile-bound benchmark`
- UI 工作区：`Manifest inspector`
- 测试基线：`dependency closure`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `graph closure + hash` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 3. Platform / Pipeline execution

- FunctionSpec：`FS-003`
- PerformanceProfile：`PF-FS-003`

- 关联指导：`DEV-PLT-011`
- 输入：`Frame/Targets/RuntimeManifest`
- 输出：`Facts/Decision proposals`
- 算法/逻辑基线：`DAG orchestrator`
- 鲁棒性重点：`cancel/timeout/retry`
- 性能重点：`PF-FS-003; profile-bound benchmark`
- UI 工作区：`Execution inspector`
- 测试基线：`fault injection`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `DAG orchestrator` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 4. Platform / Evidence commit

- FunctionSpec：`FS-004`
- PerformanceProfile：`PF-FS-004`

- 关联指导：`DEV-PLT-012`
- 输入：`Facts/Evidence blobs`
- 输出：`CommitReceipt`
- 算法/逻辑基线：`CAS + idempotent commit`
- 鲁棒性重点：`duplicate/partial/network loss`
- 性能重点：`PF-FS-004; profile-bound benchmark`
- UI 工作区：`Evidence viewer`
- 测试基线：`replay/readback`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `CAS + idempotent commit` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 5. Platform / Cross-module event

- FunctionSpec：`FS-005`
- PerformanceProfile：`PF-FS-005`

- 关联指导：`DEV-PLT-013`
- 输入：`Envelope + payload`
- 输出：`ack/receipt`
- 算法/逻辑基线：`at-least-once + idempotency`
- 鲁棒性重点：`duplicate/out-of-order/resume`
- 性能重点：`PF-FS-005; profile-bound benchmark`
- UI 工作区：`integration monitor`
- 测试基线：`interop simulator`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `at-least-once + idempotency` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 6. Platform / Board flow

- FunctionSpec：`FS-006`
- PerformanceProfile：`PF-FS-006`

- 关联指导：`DEV-PLT-014`
- 输入：`Lane/BoardPosition/Handoff`
- 输出：`HandoffSession`
- 算法/逻辑基线：`state/lease model`
- 鲁棒性重点：`stuck board/restart`
- 性能重点：`PF-FS-006; profile-bound benchmark`
- UI 工作区：`line overview`
- 测试基线：`simulated jam`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `state/lease model` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 7. Vision / Shape localization

- FunctionSpec：`FS-007`
- PerformanceProfile：`PF-FS-007`

- 关联指导：`DEV-VIS-021`
- 输入：`Image + model`
- 输出：`pose/score`
- 算法/逻辑基线：`find_shape_model`
- 鲁棒性重点：`occlusion/noise/scale`
- 性能重点：`PF-FS-007; profile-bound benchmark`
- UI 工作区：`Alignment workspace`
- 测试基线：`Golden pose set`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `find_shape_model` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 8. Vision / Subpixel edge extraction

- FunctionSpec：`FS-008`
- PerformanceProfile：`PF-FS-008`

- 关联指导：`DEV-VIS-025`
- 输入：`ROI image`
- 输出：`XLD contours`
- 算法/逻辑基线：`edges_sub_pix`
- 鲁棒性重点：`noise/reflective edge`
- 性能重点：`PF-FS-008; profile-bound benchmark`
- UI 工作区：`Measurement workspace`
- 测试基线：`edge repeatability`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `edges_sub_pix` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 9. Vision / Ellipse/circle fit

- FunctionSpec：`FS-009`
- PerformanceProfile：`PF-FS-009`

- 关联指导：`DEV-VIS-025`
- 输入：`XLD contour`
- 输出：`center/radius/residual`
- 算法/逻辑基线：`fit_ellipse_contour_xld or alternative fit`
- 鲁棒性重点：`partial arc/outlier`
- 性能重点：`PF-FS-009; profile-bound benchmark`
- UI 工作区：`measurement overlay`
- 测试基线：`residual cases`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `fit_ellipse_contour_xld or alternative fit` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 10. Vision / Local segmentation

- FunctionSpec：`FS-010`
- PerformanceProfile：`PF-FS-010`

- 关联指导：`DEV-VIS-026`
- 输入：`image/background`
- 输出：`region`
- 算法/逻辑基线：`dyn_threshold / local candidate`
- 鲁棒性重点：`illumination drift`
- 性能重点：`PF-FS-010; profile-bound benchmark`
- UI 工作区：`segmentation overlay`
- 测试基线：`recall/false alarm`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `dyn_threshold / local candidate` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 11. Vision / 2D candidate scoring

- FunctionSpec：`FS-011`
- PerformanceProfile：`PF-FS-011`

- 关联指导：`DEV-VIS-026`
- 输入：`regions/features`
- 输出：`candidate score`
- 算法/逻辑基线：`rule + feature score`
- 鲁棒性重点：`ambiguous/non-observable`
- 性能重点：`PF-FS-011; profile-bound benchmark`
- UI 工作区：`candidate list`
- 测试基线：`hard negative set`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `rule + feature score` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 12. Vision / 3D HeightField build

- FunctionSpec：`FS-012`
- PerformanceProfile：`PF-FS-012`

- 关联指导：`DEV-VIS-027`
- 输入：`sensor frames`
- 输出：`HeightField/ValidMask`
- 算法/逻辑基线：`sensor-specific reconstruction + xyz_to_object_model_3d as needed`
- 鲁棒性重点：`invalid depth/saturation`
- 性能重点：`PF-FS-012; profile-bound benchmark`
- UI 工作区：`3D viewport`
- 测试基线：`height accuracy/coverage`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `sensor-specific reconstruction + xyz_to_object_model_3d as needed` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 13. Vision / Stereo surface reconstruction

- FunctionSpec：`FS-013`
- PerformanceProfile：`PF-FS-013`

- 关联指导：`DEV-VIS-027`
- 输入：`calibrated multi-view`
- 输出：`ObjectModel3D`
- 算法/逻辑基线：`reconstruct_surface_stereo`
- 鲁棒性重点：`calibration/occlusion`
- 性能重点：`PF-FS-013; profile-bound benchmark`
- UI 工作区：`3D workspace`
- 测试基线：`height/coverage benchmark`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `reconstruct_surface_stereo` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 14. Vision / 3D registration

- FunctionSpec：`FS-014`
- PerformanceProfile：`PF-FS-014`

- 关联指导：`DEV-VIS-028`
- 输入：`ObjectModel3D + rough transforms`
- 输出：`transforms/scores`
- 算法/逻辑基线：`register_object_model_3d_global/pair`
- 鲁棒性重点：`low overlap/outliers`
- 性能重点：`PF-FS-014; profile-bound benchmark`
- UI 工作区：`3D transform overlay`
- 测试基线：`residual benchmark`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `register_object_model_3d_global/pair` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 15. Vision / Multi-FOV stitch

- FunctionSpec：`FS-015`
- PerformanceProfile：`PF-FS-015`

- 关联指导：`DEV-VIS-029`
- 输入：`FOV frames + transforms`
- 输出：`global image/map`
- 算法/逻辑基线：`position graph + image/geometry fusion`
- 鲁棒性重点：`drift/outlier overlap`
- 性能重点：`PF-FS-015; profile-bound benchmark`
- UI 工作区：`stitch workspace`
- 测试基线：`seam/residual test`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `position graph + image/geometry fusion` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 16. Metrology / Calibration

- FunctionSpec：`FS-016`
- PerformanceProfile：`PF-FS-016`

- 关联指导：`DEV-MET-030`
- 输入：`calibration targets/device`
- 输出：`CalibrationProfile/Artifact`
- 算法/逻辑基线：`target solve + validation`
- 鲁棒性重点：`temperature/field distortion`
- 性能重点：`PF-FS-016; profile-bound benchmark`
- UI 工作区：`calibration workspace`
- 测试基线：`reference certificate`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `target solve + validation` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 17. Metrology / Feature measurement

- FunctionSpec：`FS-017`
- PerformanceProfile：`PF-FS-017`

- 关联指导：`DEV-MET-031`
- 输入：`feature geometry`
- 输出：`FeatureMeasurement`
- 算法/逻辑基线：`edge/fit/distance/relationship`
- 鲁棒性重点：`outlier/rejectability`
- 性能重点：`PF-FS-017; profile-bound benchmark`
- UI 工作区：`metrology workspace`
- 测试基线：`golden dimensions`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `edge/fit/distance/relationship` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 18. Metrology / Uncertainty budget

- FunctionSpec：`FS-018`
- PerformanceProfile：`PF-FS-018`

- 关联指导：`DEV-MET-033`
- 输入：`measurement components`
- 输出：`uncertainty/qualification`
- 算法/逻辑基线：`component budget + statistical tests`
- 鲁棒性重点：`drift/repeatability`
- 性能重点：`PF-FS-018; profile-bound benchmark`
- UI 工作区：`qualification workspace`
- 测试基线：`MSA/GR&R`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `component budget + statistical tests` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 19. Metrology / Coverage calculation

- FunctionSpec：`FS-019`
- PerformanceProfile：`PF-FS-019`

- 关联指导：`DEV-MET-034`
- 输入：`TargetSet/Policy`
- 输出：`CoverageResult`
- 算法/逻辑基线：`feature + intra-feature + sampling`
- 鲁棒性重点：`unknown/missing coverage`
- 性能重点：`PF-FS-019; profile-bound benchmark`
- UI 工作区：`coverage heatmap`
- 测试基线：`coverage gaps`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `feature + intra-feature + sampling` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 20. PCB / Pattern width/space

- FunctionSpec：`FS-020`
- PerformanceProfile：`PF-FS-020`

- 关联指导：`DEV-DOM-050A`
- 输入：`ManufacturingGeometry + image`
- 输出：`InspectionFact/MeasurementSet`
- 算法/逻辑基线：`design ROI + edge measurement`
- 鲁棒性重点：`design/illumination variation`
- 性能重点：`PF-FS-020; profile-bound benchmark`
- UI 工作区：`PCB inspection workspace`
- 测试基线：`golden + hard negatives`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `design ROI + edge measurement` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 21. PCB / Pad geometry

- FunctionSpec：`FS-021`
- PerformanceProfile：`PF-FS-021`

- 关联指导：`DEV-DOM-050A`
- 输入：`ManufacturingGeometry + image`
- 输出：`InspectionFact/MeasurementSet`
- 算法/逻辑基线：`contour/fit + reference`
- 鲁棒性重点：`design/illumination variation`
- 性能重点：`PF-FS-021; profile-bound benchmark`
- UI 工作区：`PCB inspection workspace`
- 测试基线：`golden + hard negatives`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `contour/fit + reference` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 22. PCB / Surface defect candidate

- FunctionSpec：`FS-022`
- PerformanceProfile：`PF-FS-022`

- 关联指导：`DEV-DOM-050A`
- 输入：`ManufacturingGeometry + image`
- 输出：`InspectionFact/MeasurementSet`
- 算法/逻辑基线：`local segmentation + feature scoring`
- 鲁棒性重点：`design/illumination variation`
- 性能重点：`PF-FS-022; profile-bound benchmark`
- UI 工作区：`PCB inspection workspace`
- 测试基线：`golden + hard negatives`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `local segmentation + feature scoring` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 23. PCB / Drill diameter

- FunctionSpec：`FS-023`
- PerformanceProfile：`PF-FS-023`

- 关联指导：`DEV-DOM-050B`
- 输入：`ManufacturingGeometry + image`
- 输出：`InspectionFact/MeasurementSet`
- 算法/逻辑基线：`edge/ellipse/circle fit`
- 鲁棒性重点：`design/illumination variation`
- 性能重点：`PF-FS-023; profile-bound benchmark`
- UI 工作区：`PCB inspection workspace`
- 测试基线：`golden + hard negatives`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `edge/ellipse/circle fit` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 24. PCB / Drill position

- FunctionSpec：`FS-024`
- PerformanceProfile：`PF-FS-024`

- 关联指导：`DEV-DOM-050B`
- 输入：`ManufacturingGeometry + image`
- 输出：`InspectionFact/MeasurementSet`
- 算法/逻辑基线：`registration + coordinate transform`
- 鲁棒性重点：`design/illumination variation`
- 性能重点：`PF-FS-024; profile-bound benchmark`
- UI 工作区：`PCB inspection workspace`
- 测试基线：`golden + hard negatives`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `registration + coordinate transform` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 25. PCB / Laser via opening

- FunctionSpec：`FS-025`
- PerformanceProfile：`PF-FS-025`

- 关联指导：`DEV-DOM-050C`
- 输入：`ManufacturingGeometry + image`
- 输出：`InspectionFact/MeasurementSet`
- 算法/逻辑基线：`local contour fit`
- 鲁棒性重点：`design/illumination variation`
- 性能重点：`PF-FS-025; profile-bound benchmark`
- UI 工作区：`PCB inspection workspace`
- 测试基线：`golden + hard negatives`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `local contour fit` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 26. PCB / Layer registration

- FunctionSpec：`FS-026`
- PerformanceProfile：`PF-FS-026`

- 关联指导：`DEV-DOM-050D`
- 输入：`ManufacturingGeometry + image`
- 输出：`InspectionFact/MeasurementSet`
- 算法/逻辑基线：`multi-reference transform + residual`
- 鲁棒性重点：`design/illumination variation`
- 性能重点：`PF-FS-026; profile-bound benchmark`
- UI 工作区：`PCB inspection workspace`
- 测试基线：`golden + hard negatives`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `multi-reference transform + residual` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 27. PCB / Solder mask defect

- FunctionSpec：`FS-027`
- PerformanceProfile：`PF-FS-027`

- 关联指导：`DEV-DOM-050D`
- 输入：`ManufacturingGeometry + image`
- 输出：`InspectionFact/MeasurementSet`
- 算法/逻辑基线：`surface segmentation + template/reference`
- 鲁棒性重点：`design/illumination variation`
- 性能重点：`PF-FS-027; profile-bound benchmark`
- UI 工作区：`PCB inspection workspace`
- 测试基线：`golden + hard negatives`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `surface segmentation + template/reference` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 28. PCB / Final AVI

- FunctionSpec：`FS-028`
- PerformanceProfile：`PF-FS-028`

- 关联指导：`DEV-DOM-050D`
- 输入：`ManufacturingGeometry + image`
- 输出：`InspectionFact/MeasurementSet`
- 算法/逻辑基线：`candidate detection + read-only review recommendation`
- 鲁棒性重点：`design/illumination variation`
- 性能重点：`PF-FS-028; profile-bound benchmark`
- UI 工作区：`PCB inspection workspace`
- 测试基线：`golden + hard negatives`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `candidate detection + read-only review recommendation` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 29. HDI / Layer stack validation

- FunctionSpec：`FS-029`
- PerformanceProfile：`PF-FS-029`

- 关联指导：`DEV-DOM-051A`
- 输入：`LayerStack/BuildUp/Via reference`
- 输出：`HDI facts/measurements`
- 算法/逻辑基线：`reference graph + version/hash`
- 鲁棒性重点：`layer mismatch/nonobservable`
- 性能重点：`PF-FS-029; profile-bound benchmark`
- UI 工作区：`HDI workspace`
- 测试基线：`reference + golden`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `reference graph + version/hash` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 30. HDI / Build-up layer target

- FunctionSpec：`FS-030`
- PerformanceProfile：`PF-FS-030`

- 关联指导：`DEV-DOM-051A`
- 输入：`LayerStack/BuildUp/Via reference`
- 输出：`HDI facts/measurements`
- 算法/逻辑基线：`layer revision + geometry`
- 鲁棒性重点：`layer mismatch/nonobservable`
- 性能重点：`PF-FS-030; profile-bound benchmark`
- UI 工作区：`HDI workspace`
- 测试基线：`reference + golden`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `layer revision + geometry` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 31. HDI / Laser via metrology

- FunctionSpec：`FS-031`
- PerformanceProfile：`PF-FS-031`

- 关联指导：`DEV-DOM-051B`
- 输入：`LayerStack/BuildUp/Via reference`
- 输出：`HDI facts/measurements`
- 算法/逻辑基线：`local contour + fit`
- 鲁棒性重点：`layer mismatch/nonobservable`
- 性能重点：`PF-FS-031; profile-bound benchmark`
- UI 工作区：`HDI workspace`
- 测试基线：`reference + golden`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `local contour + fit` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 32. HDI / Fine line/space

- FunctionSpec：`FS-032`
- PerformanceProfile：`PF-FS-032`

- 关联指导：`DEV-DOM-051B`
- 输入：`LayerStack/BuildUp/Via reference`
- 输出：`HDI facts/measurements`
- 算法/逻辑基线：`subpixel edge + design reference`
- 鲁棒性重点：`layer mismatch/nonobservable`
- 性能重点：`PF-FS-032; profile-bound benchmark`
- UI 工作区：`HDI workspace`
- 测试基线：`reference + golden`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `subpixel edge + design reference` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 33. HDI / HDI metrology

- FunctionSpec：`FS-033`
- PerformanceProfile：`PF-FS-033`

- 关联指导：`DEV-DOM-051B`
- 输入：`LayerStack/BuildUp/Via reference`
- 输出：`HDI facts/measurements`
- 算法/逻辑基线：`relationship measurement + uncertainty`
- 鲁棒性重点：`layer mismatch/nonobservable`
- 性能重点：`PF-FS-033; profile-bound benchmark`
- UI 工作区：`HDI workspace`
- 测试基线：`reference + golden`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `relationship measurement + uncertainty` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 34. FPC / R2R coordinate

- FunctionSpec：`FS-034`
- PerformanceProfile：`PF-FS-034`

- 关联指导：`DEV-DOM-052A`
- 输入：`Web/geometry/image`
- 输出：`FPC facts`
- 算法/逻辑基线：`WebCoordinateReference + fitted correction`
- 鲁棒性重点：`nonrigid variation`
- 性能重点：`PF-FS-034; profile-bound benchmark`
- UI 工作区：`R2R workspace`
- 测试基线：`roll/web sweep`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `WebCoordinateReference + fitted correction` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 35. FPC / NonRigid local transform

- FunctionSpec：`FS-035`
- PerformanceProfile：`PF-FS-035`

- 关联指导：`DEV-DOM-052A`
- 输入：`Web/geometry/image`
- 输出：`FPC facts`
- 算法/逻辑基线：`local deformation model + residual`
- 鲁棒性重点：`nonrigid variation`
- 性能重点：`PF-FS-035; profile-bound benchmark`
- UI 工作区：`R2R workspace`
- 测试基线：`roll/web sweep`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `local deformation model + residual` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 36. FPC / Coverlay inspection

- FunctionSpec：`FS-036`
- PerformanceProfile：`PF-FS-036`

- 关联指导：`DEV-DOM-052B`
- 输入：`Web/geometry/image`
- 输出：`FPC facts`
- 算法/逻辑基线：`design ROI + segmentation`
- 鲁棒性重点：`nonrigid variation`
- 性能重点：`PF-FS-036; profile-bound benchmark`
- UI 工作区：`R2R workspace`
- 测试基线：`roll/web sweep`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `design ROI + segmentation` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 37. FPC / Stiffener inspection

- FunctionSpec：`FS-037`
- PerformanceProfile：`PF-FS-037`

- 关联指导：`DEV-DOM-052B`
- 输入：`Web/geometry/image`
- 输出：`FPC facts`
- 算法/逻辑基线：`geometry + surface candidate`
- 鲁棒性重点：`nonrigid variation`
- 性能重点：`PF-FS-037; profile-bound benchmark`
- UI 工作区：`R2R workspace`
- 测试基线：`roll/web sweep`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `geometry + surface candidate` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 38. FPC / Bend region

- FunctionSpec：`FS-038`
- PerformanceProfile：`PF-FS-038`

- 关联指导：`DEV-DOM-052B`
- 输入：`Web/geometry/image`
- 输出：`FPC facts`
- 算法/逻辑基线：`local frame + admissibility`
- 鲁棒性重点：`nonrigid variation`
- 性能重点：`PF-FS-038; profile-bound benchmark`
- UI 工作区：`R2R workspace`
- 测试基线：`roll/web sweep`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `local frame + admissibility` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 39. Stencil / Aperture geometry

- FunctionSpec：`FS-039`
- PerformanceProfile：`PF-FS-039`

- 关联指导：`DEV-DOM-054A`
- 输入：`Stencil CAD + 2D/3D evidence`
- 输出：`Stencil facts/advice`
- 算法/逻辑基线：`2D contour + 3D surface`
- 鲁棒性重点：`surface variation`
- 性能重点：`PF-FS-039; profile-bound benchmark`
- UI 工作区：`Stencil workspace`
- 测试基线：`golden stencil`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `2D contour + 3D surface` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 40. Stencil / Stencil thickness

- FunctionSpec：`FS-040`
- PerformanceProfile：`PF-FS-040`

- 关联指导：`DEV-DOM-054A`
- 输入：`Stencil CAD + 2D/3D evidence`
- 输出：`Stencil facts/advice`
- 算法/逻辑基线：`3D metrology + calibration`
- 鲁棒性重点：`surface variation`
- 性能重点：`PF-FS-040; profile-bound benchmark`
- UI 工作区：`Stencil workspace`
- 测试基线：`golden stencil`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `3D metrology + calibration` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 41. Stencil / Wall condition

- FunctionSpec：`FS-041`
- PerformanceProfile：`PF-FS-041`

- 关联指导：`DEV-DOM-054A`
- 输入：`Stencil CAD + 2D/3D evidence`
- 输出：`Stencil facts/advice`
- 算法/逻辑基线：`3D profile + residual`
- 鲁棒性重点：`surface variation`
- 性能重点：`PF-FS-041; profile-bound benchmark`
- UI 工作区：`Stencil workspace`
- 测试基线：`golden stencil`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `3D profile + residual` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 42. Stencil / Blocked aperture

- FunctionSpec：`FS-042`
- PerformanceProfile：`PF-FS-042`

- 关联指导：`DEV-DOM-054B`
- 输入：`Stencil CAD + 2D/3D evidence`
- 输出：`Stencil facts/advice`
- 算法/逻辑基线：`height/surface/region candidate`
- 鲁棒性重点：`surface variation`
- 性能重点：`PF-FS-042; profile-bound benchmark`
- UI 工作区：`Stencil workspace`
- 测试基线：`golden stencil`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `height/surface/region candidate` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 43. Stencil / Maintenance advice

- FunctionSpec：`FS-043`
- PerformanceProfile：`PF-FS-043`

- 关联指导：`DEV-DOM-054B`
- 输入：`Stencil CAD + 2D/3D evidence`
- 输出：`Stencil facts/advice`
- 算法/逻辑基线：`trend + rule-based evidence`
- 鲁棒性重点：`surface variation`
- 性能重点：`PF-FS-043; profile-bound benchmark`
- UI 工作区：`Stencil workspace`
- 测试基线：`golden stencil`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `trend + rule-based evidence` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 44. SPI / 3D acquisition quality

- FunctionSpec：`FS-044`
- PerformanceProfile：`PF-FS-044`

- 关联指导：`DEV-DOM-055A`
- 输入：`3D/PAD/stencil/process evidence`
- 输出：`MeasurementSet/Decision/SPC/feedback`
- 算法/逻辑基线：`sensor validity + ValidMask`
- 鲁棒性重点：`gloss/occlusion/invalid depth/edge shadow`
- 性能重点：`PF-FS-044; profile-bound benchmark`
- UI 工作区：`SPI programming/production`
- 测试基线：`hard cases + printer simulator`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `sensor validity + ValidMask` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 45. SPI / Reference plane

- FunctionSpec：`FS-045`
- PerformanceProfile：`PF-FS-045`

- 关联指导：`DEV-DOM-055B`
- 输入：`3D/PAD/stencil/process evidence`
- 输出：`MeasurementSet/Decision/SPC/feedback`
- 算法/逻辑基线：`local plane fit + residual`
- 鲁棒性重点：`gloss/occlusion/invalid depth/edge shadow`
- 性能重点：`PF-FS-045; profile-bound benchmark`
- UI 工作区：`SPI programming/production`
- 测试基线：`hard cases + printer simulator`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `local plane fit + residual` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 46. SPI / Pad target generation

- FunctionSpec：`FS-046`
- PerformanceProfile：`PF-FS-046`

- 关联指导：`DEV-DOM-055B`
- 输入：`3D/PAD/stencil/process evidence`
- 输出：`MeasurementSet/Decision/SPC/feedback`
- 算法/逻辑基线：`ManufacturingGeometry/PAD + local frame`
- 鲁棒性重点：`gloss/occlusion/invalid depth/edge shadow`
- 性能重点：`PF-FS-046; profile-bound benchmark`
- UI 工作区：`SPI programming/production`
- 测试基线：`hard cases + printer simulator`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `ManufacturingGeometry/PAD + local frame` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 47. SPI / Paste segmentation

- FunctionSpec：`FS-047`
- PerformanceProfile：`PF-FS-047`

- 关联指导：`DEV-DOM-055C`
- 输入：`3D/PAD/stencil/process evidence`
- 输出：`MeasurementSet/Decision/SPC/feedback`
- 算法/逻辑基线：`local/global segmentation candidates`
- 鲁棒性重点：`gloss/occlusion/invalid depth/edge shadow`
- 性能重点：`PF-FS-047; profile-bound benchmark`
- UI 工作区：`SPI programming/production`
- 测试基线：`hard cases + printer simulator`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `local/global segmentation candidates` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 48. SPI / Paste volume

- FunctionSpec：`FS-048`
- PerformanceProfile：`PF-FS-048`

- 关联指导：`DEV-DOM-055C`
- 输入：`3D/PAD/stencil/process evidence`
- 输出：`MeasurementSet/Decision/SPC/feedback`
- 算法/逻辑基线：`integral over valid surface`
- 鲁棒性重点：`gloss/occlusion/invalid depth/edge shadow`
- 性能重点：`PF-FS-048; profile-bound benchmark`
- UI 工作区：`SPI programming/production`
- 测试基线：`hard cases + printer simulator`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `integral over valid surface` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 49. SPI / Paste area

- FunctionSpec：`FS-049`
- PerformanceProfile：`PF-FS-049`

- 关联指导：`DEV-DOM-055C`
- 输入：`3D/PAD/stencil/process evidence`
- 输出：`MeasurementSet/Decision/SPC/feedback`
- 算法/逻辑基线：`projected region measurement`
- 鲁棒性重点：`gloss/occlusion/invalid depth/edge shadow`
- 性能重点：`PF-FS-049; profile-bound benchmark`
- UI 工作区：`SPI programming/production`
- 测试基线：`hard cases + printer simulator`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `projected region measurement` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 50. SPI / Paste height

- FunctionSpec：`FS-050`
- PerformanceProfile：`PF-FS-050`

- 关联指导：`DEV-DOM-055C`
- 输入：`3D/PAD/stencil/process evidence`
- 输出：`MeasurementSet/Decision/SPC/feedback`
- 算法/逻辑基线：`max/percentile/robust height metrics`
- 鲁棒性重点：`gloss/occlusion/invalid depth/edge shadow`
- 性能重点：`PF-FS-050; profile-bound benchmark`
- UI 工作区：`SPI programming/production`
- 测试基线：`hard cases + printer simulator`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `max/percentile/robust height metrics` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 51. SPI / Paste offset

- FunctionSpec：`FS-051`
- PerformanceProfile：`PF-FS-051`

- 关联指导：`DEV-DOM-055C`
- 输入：`3D/PAD/stencil/process evidence`
- 输出：`MeasurementSet/Decision/SPC/feedback`
- 算法/逻辑基线：`centroid/reference relation`
- 鲁棒性重点：`gloss/occlusion/invalid depth/edge shadow`
- 性能重点：`PF-FS-051; profile-bound benchmark`
- UI 工作区：`SPI programming/production`
- 测试基线：`hard cases + printer simulator`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `centroid/reference relation` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 52. SPI / Paste shape

- FunctionSpec：`FS-052`
- PerformanceProfile：`PF-FS-052`

- 关联指导：`DEV-DOM-055C`
- 输入：`3D/PAD/stencil/process evidence`
- 输出：`MeasurementSet/Decision/SPC/feedback`
- 算法/逻辑基线：`contour descriptors`
- 鲁棒性重点：`gloss/occlusion/invalid depth/edge shadow`
- 性能重点：`PF-FS-052; profile-bound benchmark`
- UI 工作区：`SPI programming/production`
- 测试基线：`hard cases + printer simulator`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `contour descriptors` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 53. SPI / SPI rule evaluation

- FunctionSpec：`FS-053`
- PerformanceProfile：`PF-FS-053`

- 关联指导：`DEV-DOM-055D`
- 输入：`3D/PAD/stencil/process evidence`
- 输出：`MeasurementSet/Decision/SPC/feedback`
- 算法/逻辑基线：`measurement thresholds + quality gating`
- 鲁棒性重点：`gloss/occlusion/invalid depth/edge shadow`
- 性能重点：`PF-FS-053; profile-bound benchmark`
- UI 工作区：`SPI programming/production`
- 测试基线：`hard cases + printer simulator`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `measurement thresholds + quality gating` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 54. SPI / SPC

- FunctionSpec：`FS-054`
- PerformanceProfile：`PF-FS-054`

- 关联指导：`DEV-DOM-055D`
- 输入：`3D/PAD/stencil/process evidence`
- 输出：`MeasurementSet/Decision/SPC/feedback`
- 算法/逻辑基线：`subgroup + denominator + watermark`
- 鲁棒性重点：`gloss/occlusion/invalid depth/edge shadow`
- 性能重点：`PF-FS-054; profile-bound benchmark`
- UI 工作区：`SPI programming/production`
- 测试基线：`hard cases + printer simulator`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `subgroup + denominator + watermark` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 55. SPI / Printer feedback

- FunctionSpec：`FS-055`
- PerformanceProfile：`PF-FS-055`

- 关联指导：`DEV-DOM-055D`
- 输入：`3D/PAD/stencil/process evidence`
- 输出：`MeasurementSet/Decision/SPC/feedback`
- 算法/逻辑基线：`proposal → command → applied → effect`
- 鲁棒性重点：`gloss/occlusion/invalid depth/edge shadow`
- 性能重点：`PF-FS-055; profile-bound benchmark`
- UI 工作区：`SPI programming/production`
- 测试基线：`hard cases + printer simulator`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `proposal → command → applied → effect` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 56. AOI / CAD/PnP target generation

- FunctionSpec：`FS-056`
- PerformanceProfile：`PF-FS-056`

- 关联指导：`DEV-DOM-057A`
- 输入：`BOM/PnP/Library/Image`
- 输出：`AOI facts/review/rework`
- 算法/逻辑基线：`reference binding + target synthesis`
- 鲁棒性重点：`component variation/occlusion/lighting`
- 性能重点：`PF-FS-056; profile-bound benchmark`
- UI 工作区：`AOI workbench`
- 测试基线：`package/defect golden set`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `reference binding + target synthesis` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 57. AOI / Component presence

- FunctionSpec：`FS-057`
- PerformanceProfile：`PF-FS-057`

- 关联指导：`DEV-DOM-057B`
- 输入：`BOM/PnP/Library/Image`
- 输出：`AOI facts/review/rework`
- 算法/逻辑基线：`ROI + region/candidate score`
- 鲁棒性重点：`component variation/occlusion/lighting`
- 性能重点：`PF-FS-057; profile-bound benchmark`
- UI 工作区：`AOI workbench`
- 测试基线：`package/defect golden set`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `ROI + region/candidate score` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 58. AOI / Component identity

- FunctionSpec：`FS-058`
- PerformanceProfile：`PF-FS-058`

- 关联指导：`DEV-DOM-057B`
- 输入：`BOM/PnP/Library/Image`
- 输出：`AOI facts/review/rework`
- 算法/逻辑基线：`PackageLibrary + visual features`
- 鲁棒性重点：`component variation/occlusion/lighting`
- 性能重点：`PF-FS-058; profile-bound benchmark`
- UI 工作区：`AOI workbench`
- 测试基线：`package/defect golden set`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `PackageLibrary + visual features` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 59. AOI / Polarity/orientation

- FunctionSpec：`FS-059`
- PerformanceProfile：`PF-FS-059`

- 关联指导：`DEV-DOM-057B`
- 输入：`BOM/PnP/Library/Image`
- 输出：`AOI facts/review/rework`
- 算法/逻辑基线：`mark/feature alignment`
- 鲁棒性重点：`component variation/occlusion/lighting`
- 性能重点：`PF-FS-059; profile-bound benchmark`
- UI 工作区：`AOI workbench`
- 测试基线：`package/defect golden set`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `mark/feature alignment` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 60. AOI / Pin/lead inspection

- FunctionSpec：`FS-060`
- PerformanceProfile：`PF-FS-060`

- 关联指导：`DEV-DOM-057B`
- 输入：`BOM/PnP/Library/Image`
- 输出：`AOI facts/review/rework`
- 算法/逻辑基线：`edge/region + geometry`
- 鲁棒性重点：`component variation/occlusion/lighting`
- 性能重点：`PF-FS-060; profile-bound benchmark`
- UI 工作区：`AOI workbench`
- 测试基线：`package/defect golden set`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `edge/region + geometry` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 61. AOI / OCR/marking

- FunctionSpec：`FS-061`
- PerformanceProfile：`PF-FS-061`

- 关联指导：`DEV-DOM-057B`
- 输入：`BOM/PnP/Library/Image`
- 输出：`AOI facts/review/rework`
- 算法/逻辑基线：`OCR candidate + confidence/review`
- 鲁棒性重点：`component variation/occlusion/lighting`
- 性能重点：`PF-FS-061; profile-bound benchmark`
- UI 工作区：`AOI workbench`
- 测试基线：`package/defect golden set`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `OCR candidate + confidence/review` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 62. AOI / Solder joint post-reflow

- FunctionSpec：`FS-062`
- PerformanceProfile：`PF-FS-062`

- 关联指导：`DEV-DOM-057C`
- 输入：`BOM/PnP/Library/Image`
- 输出：`AOI facts/review/rework`
- 算法/逻辑基线：`geometry/surface candidate + review`
- 鲁棒性重点：`component variation/occlusion/lighting`
- 性能重点：`PF-FS-062; profile-bound benchmark`
- UI 工作区：`AOI workbench`
- 测试基线：`package/defect golden set`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `geometry/surface candidate + review` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 63. AOI / Review/rework

- FunctionSpec：`FS-063`
- PerformanceProfile：`PF-FS-063`

- 关联指导：`DEV-DOM-057D`
- 输入：`BOM/PnP/Library/Image`
- 输出：`AOI facts/review/rework`
- 算法/逻辑基线：`evidence-first UI + state machine`
- 鲁棒性重点：`component variation/occlusion/lighting`
- 性能重点：`PF-FS-063; profile-bound benchmark`
- UI 工作区：`AOI workbench`
- 测试基线：`package/defect golden set`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `evidence-first UI + state machine` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 64. Quality/AI / SPC chart

- FunctionSpec：`FS-064`
- PerformanceProfile：`PF-FS-064`

- 关联指导：`DEV-DOM-058A`
- 输入：`committed facts or approved inputs`
- 输出：`projection/candidate/draft`
- 算法/逻辑基线：`MetricDefinition + subgroup rules`
- 鲁棒性重点：`missing/late data, bias, reject option`
- 性能重点：`PF-FS-064; profile-bound benchmark`
- UI 工作区：`quality/AI workspace`
- 测试基线：`statistical + replay`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `MetricDefinition + subgroup rules` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 65. Quality/AI / Cross-process correlation

- FunctionSpec：`FS-065`
- PerformanceProfile：`PF-FS-065`

- 关联指导：`DEV-DOM-058B`
- 输入：`committed facts or approved inputs`
- 输出：`projection/candidate/draft`
- 算法/逻辑基线：`identity/time/window join + statistics`
- 鲁棒性重点：`missing/late data, bias, reject option`
- 性能重点：`PF-FS-065; profile-bound benchmark`
- UI 工作区：`quality/AI workspace`
- 测试基线：`statistical + replay`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `identity/time/window join + statistics` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 66. Quality/AI / Disposition projection

- FunctionSpec：`FS-066`
- PerformanceProfile：`PF-FS-066`

- 关联指导：`DEV-AI-063`
- 输入：`committed facts or approved inputs`
- 输出：`projection/candidate/draft`
- 算法/逻辑基线：`committed facts + quality plan`
- 鲁棒性重点：`missing/late data, bias, reject option`
- 性能重点：`PF-FS-066; profile-bound benchmark`
- UI 工作区：`quality/AI workspace`
- 测试基线：`statistical + replay`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `committed facts + quality plan` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 67. Quality/AI / AI assisted review

- FunctionSpec：`FS-067`
- PerformanceProfile：`PF-FS-067`

- 关联指导：`DEV-AI-061`
- 输入：`committed facts or approved inputs`
- 输出：`projection/candidate/draft`
- 算法/逻辑基线：`embedding/retrieval/ranking with evidence`
- 鲁棒性重点：`missing/late data, bias, reject option`
- 性能重点：`PF-FS-067; profile-bound benchmark`
- UI 工作区：`quality/AI workspace`
- 测试基线：`statistical + replay`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `embedding/retrieval/ranking with evidence` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 68. Quality/AI / Program synthesis

- FunctionSpec：`FS-068`
- PerformanceProfile：`PF-FS-068`

- 关联指导：`DEV-AI-062`
- 输入：`committed facts or approved inputs`
- 输出：`projection/candidate/draft`
- 算法/逻辑基线：`geometry + library + rules → draft`
- 鲁棒性重点：`missing/late data, bias, reject option`
- 性能重点：`PF-FS-068; profile-bound benchmark`
- UI 工作区：`quality/AI workspace`
- 测试基线：`statistical + replay`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `geometry + library + rules → draft` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。

## 69. Quality/AI / AI validation
- PerformanceProfile：`PF-FS-069`

- FunctionSpec：`FS-069`


- 关联指导：`DEV-AI-063`
- 输入：`committed facts or approved inputs`
- 输出：`projection/candidate/draft`
- 算法/逻辑基线：`held-out dataset + confidence intervals`
- 鲁棒性重点：`missing/late data, bias, reject option`
- 性能重点：`PF-FS-069; profile-bound benchmark`
- UI 工作区：`quality/AI workspace`
- 测试基线：`statistical + replay`
- 当前文档准备状态：`SPEC_READY`

### 实施步骤

1. **契约解析**：读取该功能关联 Development Guide、Contract/Schema、AuthorityScope、State/Owner；禁止自行创建平行对象。
2. **输入前置检查**：验证身份、版本、有效域、坐标/单位、质量元数据和必要能力；缺失输入必须进入显式 `Blocked/RecoverableError/Reject` 路径。
3. **主处理**：按上述 `held-out dataset + confidence intervals` 执行，所有耗时关键点打点；视觉类功能先限制 ROI/目标集，再进入高成本阶段。
4. **质量门**：至少检查结果完整性、数值域、残差/score/有效率或业务规则一致性；无法可靠判断时输出拒识，而不是伪造成功。
5. **产物分类**：明确这是 Candidate、Measurement、Fact、Proposal 还是 Projection；只有规定 Producer/CommitOwner 才可形成生产事实或机判。
6. **证据闭环**：输出必须带 algorithm/version/parameter provenance；生产事实要能关联 Evidence Graph / ResultCommitReceipt。
7. **UI 投影**：UI 显示状态、结果、质量理由和下一动作，不直接持有 HALCON/AsunImage 原生对象；高频操作优先支持批量、快捷键和上下文命令。
8. **回放与基准**：固定输入 snapshot，执行 Replay；记录 P50/P95/P99、峰值内存、错误率和结果差异。

### 鲁棒性测试矩阵

| 变化源 | 必测项 | 通过条件 |
|---|---|---|
| 输入质量 | 缺失/损坏/污染/局部遮挡 | 显式质量状态，不静默成功 |
| 参数扰动 | 合理范围边界、非法值 | 校验器阻断或进入受控 fallback |
| 产品变化 | 不同尺寸/批次/域内变体 | 结果稳定或可解释拒识 |
| 运行变化 | 重启/取消/超时/重复消息 | 可恢复且不重复提交事实 |
| 资源变化 | 高并发/内存压力 | 不发生静默数据丢失；按策略背压 |

### AI 实施边界

- AI 可以帮助代码生成、参数候选、难例分析或候选目标生成，但必须遵循该功能的 Contract/AuthorityScope。
- 任何 AI proposal 必须记录依据、输入快照、模型版本和影响范围。
- AI 不得绕过 Validator、Test、Approval 或 Release。

### 禁止实现

- 不复制既有 Schema、State、Owner 或事实存储。
- 不以 UI 状态代替领域事实。
- 不用单样本通过率、人工主观观察或未验证 operator/API 作为“最优方案”结论。
- 不把设备 ACK、网络 ACK 或 UI 完成事件直接等同于业务 Applied/Committed。

### 完成定义

- Contract/Schema test 通过；
- 正常 + 边界 + 拒识 + 恢复路径通过；
- Replay 可重现或差异有明确解释；
- Benchmark 有原始数据；
- UI（若适用）通过八态、AutomationId、键盘/DPI/本地化验证；
- 相关文档、Manifest、状态成熟度同步更新。
