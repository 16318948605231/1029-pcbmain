> 2026-09-27适用性：本页保留既有实现规划/注册信息。当前文档阶段以[平台设计基线](../00-baseline/PLATFORM-DESIGN-BASELINE.md)和SM/PG目录为准；本页历史状态、69项覆盖或波次不构成自动开工授权，逐切片核对Contract/Owner/验收。

# 开放门禁与禁止推断登记册
- 文档 ID：`DEV-PLAN-010`
- 版本：`1.0.0`
- 状态：`Normative`

## 1. 文档层已冻结的内容

Architecture boundary、领域边界、事实/候选/判定分离、Evidence Graph、Runtime Manifest、Identity、Retry semantics、UI 状态模型、模块复用原则、AI 生命周期原则、HALCON/DevExpress 实施规则、69 个功能规格和 21 个 PageContract 均属于本开发标准的文档约束。

## 2. 外部门禁

以下项目只能由实际工程证据关闭，不得由 AI 或文档推断：

- 硬件 SDK/设备时序；
- HALCON 精确 patch 与目标机 API；
- DevExpress 实际安装版本/API；
- 相机/镜头/光源/3D/运动/PLC 的真实参数；
- Golden Dataset 与真实缺陷覆盖；
- Calibration / GR&R / MSA；
- HIL/FAT/SAT；
- CFX/Hermes/MES 实际互操作；
- Production Acceptance。

## 3. 门禁关闭规则

每项门禁必须有 Owner、输入证据、执行环境、结果、日期、版本/hash、结论和回归影响。没有证据就保持 `Gated`。


## 4. AI停止条件 / Blocker / Scope / Test / 验收

- **Stop / 停止**：任何未关闭的外部门禁或软件语义不确定项均不得越过当前依赖边界。
- **Blocker**：缺失权威 Contract、字段、枚举、Owner、State、AuthorityScope、API 或验收口径均登记为 Blocker/Unverified。
- **Scope**：工作范围由 FunctionSpec/TaskCard 冻结；任何新增行为先判定 ScopeDrift。
- **Test**：每项关闭必须绑定 Unit/Contract/Integration/Replay/Performance 等适用 Test。
- **验收**：AcceptanceProfile、Qualification 和真实环境证据必须来自获批权威；实现失败不得降低验收标准。
