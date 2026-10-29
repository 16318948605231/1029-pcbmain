# Uncertainty budget

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-018`
- 类型：`Function Implementation Specification`
- 版本：`1.3.0-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-MET-033`
- 领域：`Metrology`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

把量测不确定度来源结构化并生成资格输入，而不是用单一重复性数字代替完整预算。

**不负责：** 生产机判、最终处置、真实设备安全功能。

## 2. 权威与契约

输入契约：`measurement components`；输出契约：`uncertainty/qualification`。若字段尚未在现有 Schema 中冻结，必须登记到对应 ContractCandidate（通常 C-01/C-02/C-03/C-04/C-08），不能在功能目录中另建 JSON/数据库模型。

1. **Architecture is the boundary authority**: do not invent a second domain model, state machine, Owner, Event schema, fact store, or production decision path.
2. **Contract/Schema is the data authority**: development guides define semantics and implementation constraints; exact persisted/transport fields are bound through the approved Contract/Schema.
3. **State/Owner is the authority**: UI, ViewModel, report, AI, cache, or adapter must not become a second writer.
4. **Every failure is explicit**: `Blocked`, `RecoverableError`, `Rejected`, `NotQualified`, `Invalid` or equivalent documented state; never convert uncertainty to success.
5. **Replay before HIL**: design every deterministic computation so its inputs, configuration, algorithm version, and evidence can be replayed.
6. **Performance is a design input**: define measurement points, queue behavior, memory lifecycle, backpressure, cancellation, and resource limits before optimization work.
7. **AI is bounded**: AI may generate candidates, proposals, explanations, ranking and code, but cannot gain implicit production authority.
8. **External implementation research is evidence, not authority**: GitHub/third-party code can inform a design but cannot overwrite this platform's Contract, licensing, security, or qualification rules.
9. **AsunImage API usage**: use the public AsunImage API and applicable official operator documentation; do not guess operator names or parameters. AsunImage and DevExpress dependency/compatibility/license verification is not required by the user; project behavior tests remain applicable.
10. **Production qualification is separate**: document completeness does not equal metrology qualification, HIL acceptance or production acceptance.

## 3. 输入前置检查

先按[033 §6](<../04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md#metrology-qualification-method>)绑定被测量/单位/支持、单次或平均、原参考证书和相关组、实验格、物理件/观察/采集层级、方法和四个既有参数键。纯不确定度预算只要求其声明分量的必要输入；偏差、线性、交叉/嵌套GR&R分别核自己的条件，不能把全部实验强加给每次请求。

缺少必要输入、版本/hash或单位/作用域冲突时停止受影响分析。缺格/重复观测身份不能填均值或凑次数，相关未知不能设0；允许保留具名局部描述与缺口，但不得标总预算或完整GR&R。资格重评可读取失效历史证书作证据，不能据旧资格授新用途；是否有有效参考、模型和数据决定该分析能否继续。

## 4. 正常执行流程

1. 冻结请求、输入/计划及必要的物理层级；列出分量、相关性、已有贡献和未取得项，保留全部失败/排除记录。
2. 按[033 §7–9](<../04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md#bias-linearity-stability>)选择预先声明的偏差、线性、稳定性或GR&R路线。045提供数值，055解释实验，不因结果不理想改模型、池化交互或更换分母。
3. 按[033 §10](<../04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md#uncertainty-components>)转换具名标准不确定度，校验协方差及敏感度、线性化范围和贡献去重，输出可计算值与缺口。
4. 仅当相应覆盖方法与条件齐全才输出U或指定区间；条件t区间、覆盖区间、标准不确定度、GR&R点估计各自标明。原负分量及采用的边界点估计并列；首批未定义的方差分量区间保持未验证。
5. 返回报告与证据引用给055/宿主；其持久化、计量审定、资格发布/撤销和039的公差/guard band消费各守原Owner。本FS无持久化、签发或生产副作用。

## 5. 算法/规则设计

**实施分类：** `Metrology/Qualification`

**Primary route：** `component budget + statistical tests`

**Fallback route：** `Recompute with approved statistical estimator`

**Fallback trigger：** No silent estimator swap; the estimator is part of the frozen qualification context.

**Reject / Block conditions：** Missing uncertainty component, incompatible covariance assumption, insufficient repeatability data.

**参数键（名称冻结，数值由批准 Profile / Recipe / Qualification 提供）：** `['UncertaintyModelId', 'ConfidenceLevel', 'VarianceComponentPolicy', 'GRRPolicy']`

**结果语义：** `Uncertainty budget + confidence bounds`

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

具体方法、假设、数值反例及来源唯一见033 §6–14。上表“confidence bounds”只表示可请求的结果族，不承诺每条路线都有有效区间；缺方法只交点估计/限制。共同参考误差不随重复数缩小；研究跨度系数、公差宽度和覆盖因子不能相互替代。改变估计量形成新方法/计算身份，不把原失败请求悄悄改成成功。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| insufficient data | 两点拟合、相同参照值、缺格或同一观测复制补格 | 不把零stderr当零不确定度，不形成完整平衡GR&R；保留原格缺口 |
| correlation unknown | 四次重采共用参考；协方差未知或非法 | 共同项不除重复数，未知预算不完整，非法矩阵不能用负分量截断修补 |
| drift | 设备与时间共线、锡膏变化、清洗重印/不同Pad混作同件 | 拒绝不可识别的因素结论；同帧Replay只支持算法层，交错顺序也不证明消除非线性变化 |
| domain extrapolation | 高度标准用于材料分割、量程外拟合或撤销资格沿用 | 保留适用域及原证书/报告，停止该用途资格，不重写历史事实 |
| estimator boundary | 负交互分量、零总方差或缺公差宽度 | 原估计与预声明边界策略并列；不能事后池化，不可评价的比例/区间不填0 |

## 7. 质量门与拒识策略

至少建立三层 Gate：

1. **InputQualityGate**：输入是否可处理；
2. **AlgorithmQualityGate**：算法结果是否足够可靠；
3. **BusinessApplicabilityGate**：方法是否适用于当前产品/特征/尺度/材料/工艺。

任何 Gate 失败都要保留原因、证据引用和状态。`Unknown/Invalid/NotApplicable` 不允许被强制转换成 `OK`。

## 8. 性能与资源

逐量值记录 P50/P95/P99；把拟合/坐标转换/统计分析拆开计时；避免 Display/Report 再计算。

性能采集点必须至少覆盖：输入准备、核心计算、质量评估、序列化/提交（如有）、UI 投影（如有）。高峰资源与长尾单独报告，不以平均耗时掩盖 P99。

## 9. 并发、取消、重试与恢复

- **Cancel**：取消尚未产生生产副作用的计算；已提交事实不可因 UI cancel 回滚。
- **Calculation Retry**：允许重新计算，生成新的 calculation identity。
- **Commit Retry**：必须复用原 CommitIdentity，并保持幂等。
- **Timeout**：形成明确超时事实/错误，不自动当作失败后的隐形重试。
- **Process Restart**：依赖 Snapshot/Receipt/Session 恢复；禁止读取 `latest` 猜状态。

## 10. 结果与证据

输出必须包含：输入引用、算法/规则版本、参数版本、坐标/单位、质量状态、执行时间、适用域、EvidenceRef；生产事实与 UI/报告投影分离。

本FS输出还按实际路线保留实验格/失败分母、参考相关组、SS/df/原及边界估计、残差、预算缺项和每项未验证原因。原参考证书、分析报告和计量资格决定不互相替代；提交、撤销发布时刻/适用起点、影响范围和旧事实保持见[033 §11](<../04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md#qualification-lifecycle>)，由宿主与原Owner执行，不因本文通用Commit Retry条目授本FS写权。

## 11. UI / 操作员工作流

UI/工作区：qualification workspace。交互遵循“状态→对象→结果→下一动作”；任何生产配置修改必须 Draft→Validate→Approve→Release；异常必须一键定位到证据。


关键操作顺序原则：系统自动带出可确定内容；操作员只处理异常、冲突和必要确认；批量动作先预览影响范围；高级参数渐进披露；每个阻断都有“原因+处理动作+证据”。

## 12. 测试设计

必须接入[033 §12–13](<../04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md#qualification-consumers>)的具名向量及正常/拒绝条件，分别验证SPI与PCB孔槽/钢网消费者。原表为测试类型索引，不能以模板T18通过代替交叉/嵌套、单位平方缩放、参考共同项、退化及时间混杂断言。

| 测试层 | 覆盖内容 | 必须留存 |
|---|---|---|
| Unit | 核心算法/规则、边界输入、单位/坐标、纯函数 | 输入快照、输出、expected/actual |
| Contract | Schema、状态、Owner、版本兼容 | validator report |
| Integration | 真实 consumer、Pipeline、Evidence | trace + receipt |
| Golden/Replay | 正常/边界/难例/拒识 | dataset hash + result diff |
| PerformanceProfile | `PF-FS-018` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
| Performance | P50/P95/P99、内存、并发 | raw benchmark |
| Fault injection | 断网、重启、取消、超时、重复消息 | recovery evidence |
| UIA | AutomationId、键盘、DPI、三语、八态 | screen + UIA report |

## 13. 验收标准

通过条件必须全部满足：

- Contract/Schema 校验通过；
- 正常、边界、拒识、恢复路径通过；
- Replay 可重现，或差异有经批准的非确定性解释；
- PerformanceProfile 绑定真实数据；
- 证据可回读；
- UI（涉及 UI 时）完成八态/UIA/键盘/DPI/本地化；
- 领域结果仅由批准 Owner 写入；
- 无未解释的高严重度残余问题；
- Manifest/版本/开发指导引用已同步。

## 14. AI 实施指令

## AI implementation task block

**Required read order**
```text
1. ARCH-PCBA-VISION-001 v0.5.3
2. GATE-001 — 当前仓库权威资产解析门禁
3. DEV-MET-033
4. FS-018 本文
5. Contract/Schema refs registered for this capability
6. State/Owner/AuthorityScope rules
7. UI-PCS-006 (when UI is present)
8. Golden/Replay + Benchmark requirements
9. actual repository API and target HALCON/DevExpress versions
```

**AI must produce before editing code**
1. dependency map and impacted files;
2. proposed interface/port changes;
3. algorithm route and fallback triggers;
4. state/error table;
5. test cases and benchmark harness plan;
6. UI command/query list (if applicable);
7. explicit list of unknowns/blockers.

**AI is forbidden to infer** missing schema fields, HALCON operators, DevExpress APIs, production thresholds, metrology tolerances, safety behavior, or authority from memory. Missing evidence is a blocking item.

**受影响切片准入：** 本功能依赖的契约、Owner、输入、参数或验收条件未冻结时，不实现依赖该缺口的生产逻辑；继续已授权且不依赖缺口的指导/切片。不得把其它功能的未决项扩大成全平台停工；也不得用脚手架绕过本切片准入。


## 15. 外部实现研究要求

Before implementation, record:
- official vendor/reference material;
- GitHub/open-source candidates;
- architecture/algorithm ideas borrowed;
- license and redistribution constraints;
- security/dependency risks;
- reasons not to copy production logic blindly.

External projects are evidence and inspiration only. They do not change Asun authority, schemas, quality gates, or qualification rules.

## 16. Canonical implementation contract

| Item | Binding |
|---|---|
| Function | `FS-018` / `Uncertainty budget` |
| Domain | `Metrology` |
| Guide | `DEV-MET-033` |
| Input | `measurement components` |
| Output | `uncertainty/qualification` |
| Result semantic | `FeatureMeasurement/MeasurementSet` |
| Canonical port | `IUncertaintyBudgetEvaluator` |
| Project | `Asun.Metrology.Core` |
| UI PageContract | `UI-PCS-006` |
| Primary Work Package | `WP-08` |
| Algorithm baseline | `component budget + statistical tests` |
| Performance gate | `analysis batch time` |
| Test baseline | `Golden + Contract + Integration + Fault + Performance` |

### 16.1 Preconditions

- input objects exist and are version/hash identifiable;
- scope and authority are compatible;
- coordinate/unit/calibration conditions are satisfied where relevant;
- method capability covers the actual feature/measurand/material/surface/mode;
- no withdrawn artifact is used to grant current qualification; historical reassessment may reference a withdrawn certificate with its original status and impact scope, as specified in section 3;
- required evidence fields are available.

### 16.2 Postconditions

- output semantics are typed and versioned;
- quality state is explicit;
- provenance is retained;
- no unauthorized production side effect was performed;
- failed quality gates cannot be represented as authoritative OK.

### 16.3 Algorithm decision matrix

| Route | Candidate | Selection / trigger |
|---|---|---|
| Primary | `component budget + statistical tests` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `Recompute with approved statistical estimator` | No silent estimator swap; the estimator is part of the frozen qualification context. |
| Reject / Block | `Missing uncertainty component, incompatible covariance assumption, insufficient repeatability data.` | 保留证据与原因；不得生成权威 OK。 |

**本 FS 的 fallback 不是“另写一个算法看看”。任何替代路线都必须来自当前 Development Guide / Operator Decision Matrix / Qualification 已登记的候选集合。**

### 16.4 Parameter authority matrix

| Parameter class | Authority/source | Hard rule |
|---|---|---|
| Target/ROI | `from approved target set or runtime binding` | never guessed from image unless the FS explicitly allows auto-targeting |
| Coordinate/Unit | `from CoordinateGraph/Calibration/Manufacturing reference` | must be explicit; mismatch blocks |
| Algorithm parameters | `Recipe/Method configuration version` | no hidden constants in code |
| Thresholds | `approved library/recipe/qualification` | AI may propose only as draft unless qualification says otherwise |
| Fallback policy | `FunctionSpec decision table` | no automatic semantic downgrade |
| Performance budget | `analysis batch time` | 由 PerformanceProfile 绑定；至少记录 P50/P95/P99、峰值内存、并发安全和取消延迟；未实测不得声称 Qualified |

## 17. Robustness challenge set

At minimum, the function must be challenged against:
- `insufficient data`
- `correlation unknown`
- `drift`
- `domain extrapolation`

Additional universal challenge classes:
- illumination/exposure drift where imaging applies;
- geometry/position/scale variation;
- partial observability and occlusion;
- missing/duplicate/late data;
- wrong version/hash/coordinate/identity;
- process restart and recovery;
- high-load queue pressure;
- operator cancellation at each stage boundary.

For each failure class, define whether the result is `Blocked`, `RecoverableError`, `Rejected`, `Unknown`, `NotApplicable`, or a domain-specific explicit state. No implicit “best effort OK”.

## 18. State machine and side-effect policy

| State | Entry condition | Allowed behavior |
|---|---|---|
| `Ready` | all required inputs and capability/qualification gates pass | execute |
| `Blocked` | required input/capability/authority missing | show reason; no production effect |
| `RecoverableError` | execution failed but restart/retry may be valid | retain evidence; follow retry policy |
| `Invalid/Rejected` | result cannot be trusted or is out-of-domain | no quality pass |
| `Completed` | output and evidence committed or returned to caller | immutable output semantics |

Only approved Application/Domain services may create production facts or machine-authoritative commands. UI and ViewModel are projections and command clients, not fact authorities.

## 19. Data/provenance and evidence mapping

```text
measurement components
  → input snapshot/reference
  → Uncertainty budget computation
  → quality gate
  → FeatureMeasurement/MeasurementSet
  → EvidenceRef / Replay reference
  → downstream consumer
```

**Trace requirements**
- `operationId` is trace identity only; it is not FactId, CommitIdentity, or BoardIdentity.
- Every result must be attributable to: input snapshot, RuntimeManifest, algorithm version, parameter version, coordinate/calibration reference, quality gate outcome and execution timestamps.
- Replay must reconstruct the same semantic result or emit a documented non-determinism reason; “different because code changed” is not an acceptable replay explanation without version comparison.


## 20. Performance engineering contract

The implementation must benchmark:

| Dimension | Requirement |
|---|---|
| Latency | report P50/P95/P99; do not report only average |
| Throughput | prove required boards/targets per time window on target hardware |
| Memory | peak and steady-state; include large image/3D buffers |
| Queue | bounded queue length and defined backpressure |
| Parallelism | define safe concurrency and non-thread-safe resources |
| Cancellation | bounded cancellation latency at stage boundaries |
| Recovery | restart/resume cost and duplicate-side-effect prevention |
| UI | interaction remains responsive; heavy compute stays off UI thread |

No performance number is considered “qualified” until measured on the target runtime/hardware or an explicitly approved equivalent profile.

## 21. Code artifacts and exact task slices

| Artifact | Canonical location | Responsibility |
|---|---|---|
| Port/interface | `IUncertaintyBudgetEvaluator` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `UncertaintyBudgetEvaluator.cs` | Pipeline/algorithm implementation |
| Validator | `UncertaintyBudgetEvaluatorValidator.cs` | Input/precondition/quality checks |
| Tests | `UncertaintyBudgetEvaluatorTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-018/` | fixed datasets, expected outputs, provenance |
| Benchmark | `UncertaintyBudgetEvaluatorBenchmark.cs` | P50/P95/P99/resource evidence |
| UI | `src/Asun.UI.Workspaces/UI-PCS-006/` | projection only; no production fact write |


**Implementation order**
1. contract/port and validation;
2. pure core logic / algorithm adapter;
3. quality gates and error semantics;
4. evidence/provenance;
5. application integration;
6. UI projection;
7. golden/replay tests;
8. performance/fault tests;
9. documentation/manifest update.

Each slice must compile and test independently where technically possible. A slice that crosses a missing ContractCandidate is blocked until the candidate is contracted.

## 22. Test matrix

| Test ID | Test objective | Evidence |
|---|---|---|
| T18-01 | contract/schema validation | expected assertion + evidence + trace; no silent pass |
| T18-02 | normal + boundary + reject | expected assertion + evidence + trace; no silent pass |
| T18-03 | replay/golden dataset | expected assertion + evidence + trace; no silent pass |
| T18-04 | fault injection | expected assertion + evidence + trace; no silent pass |
| T18-05 | performance benchmark | expected assertion + evidence + trace; no silent pass |
| T18-06 | reference standard | expected assertion + evidence + trace; no silent pass |
| T18-07 | repeatability/reproducibility | expected assertion + evidence + trace; no silent pass |
| T18-08 | uncertainty contribution | expected assertion + evidence + trace; no silent pass |

## 23. Acceptance checklist

- [ ] Contract/Schema reference is unique and versioned.
- [ ] Producer/StateOwner/CommitOwner/ActivationOwner is unique.
- [ ] Inputs and outputs are version/hash traceable.
- [ ] Primary/Fallback/Reject routes are explicit.
- [ ] Every fallback has a trigger and cannot lower the semantic quality gate silently.
- [ ] Unknown/Invalid/NotApplicable cannot become OK by UI or report transformation.
- [ ] Golden/replay vector exists.
- [ ] P50/P95/P99 and resource benchmark exists.
- [ ] Failure/restart/cancel/timeout paths tested.
- [ ] UI PageContract exists where a page is involved.
- [ ] UI cannot write production facts directly.
- [ ] External implementation research and license review recorded.
- [ ] No unknown API was invented.
- [ ] No new universal object or duplicate store was introduced.

## 24. Forbidden implementation patterns

- hard-coded undocumented thresholds;
- direct vendor SDK types in Domain/Application contracts;
- hidden retry loops or unbounded queues;
- `latest` production binding;
- UI-driven production authority;
- silent geometry/coordinate/unit conversion;
- auto-fallback that hides loss of observability;
- AI-generated code merged without the corresponding tests/benchmark/audit updates;
- copying open-source implementation without license and security review.


## 25. Implementation Freeze Card

本节是 AI/人工编码前的**冻结卡**。除明确列出的待门禁项外，禁止自行选择实现。

| 项目 | 冻结值 | 规则 |
|---|---|---|
| Function | `FS-018` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-MET-033` | 指导文档是实施语义权威。 |
| Project | `Asun.Metrology.Core` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `IUncertaintyBudgetEvaluator` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-006` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `component budget + statistical tests` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
| SideEffectPolicy | `none; 无副作用；本功能不得直接写入生产事实、设备状态、放行状态或外部控制副作用。` | 冻结策略；任何未批准副作用路径必须 Blocker。 |
| Performance focus | `analysis batch time` | 未测量前不得声称满足性能。 |

### 编码前强制停止条件

遇到以下任一情况，AI/开发人员必须**停止写代码并登记 Blocker**，不得用经验补齐：

1. Contract/Schema 字段、枚举、Owner、AuthorityScope 未找到；
2. HALCON/DevExpress/AsunImage API 无法从目标实际版本资料确认；
3. 单位、坐标系、容差、阈值、采样规则或分母未冻结；
4. Primary/Fallback/Reject 选择条件不明确；
5. 需要新增 Producer/Store/State/Universal Object；
6. 需要修改不在 `Code artifacts and exact task slices` 中的代码；
7. 现有代码与本标准冲突且未完成变更影响分析；
8. 需要真实硬件行为但尚无已批准的 Port/Mock/HIL 约定。

### 本 FS 的输入输出冻结

- 输入契约：`measurement components`
- 输出契约：`uncertainty/qualification`
- 质量语义：Unknown / Invalid / NotApplicable / NotQualified 不得被映射为 OK。
- 证据要求：结果必须能够回溯到输入快照、RuntimeManifest、算法/规则版本、关键参数、坐标/标定引用和执行时间。

### AI 完成后的强制回报

AI 必须输出：变更文件清单、对应 FS 条目、Contract/Schema 变更、测试、Benchmark、未关闭风险、未验证 API、禁止路径复核结果。未能证明的内容必须标记 `Unverified`，不得写成 `Completed`。

## 27. Function-specific deterministic freeze profile

| Item | Frozen implementation rule |
|---|---|
| Function class | `Metrology/Qualification` |
| Primary algorithm/route | `component budget + statistical tests` |
| Fallback | `Recompute with approved statistical estimator` |
| Fallback trigger | No silent estimator swap; the estimator is part of the frozen qualification context. |
| Reject/Block | Missing uncertainty component, incompatible covariance assumption, insufficient repeatability data. |
| Parameter authority | `['UncertaintyModelId', 'ConfidenceLevel', 'VarianceComponentPolicy', 'GRRPolicy']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | Uncertainty budget + confidence bounds + input snapshot + algorithm/parameter version + quality-gate outcome |
| UI rule | PageContract may project and command; it must not create/modify the underlying fact directly. |
| Performance | `analysis batch time`; target values come only from the applicable PerformanceProfile. |
| External API | 具体调用先查目标版本官方文档与公共签名；不验证AsunImage/DevExpress依赖、兼容性或授权，项目自身行为按功能验收。 |
| Unknown | Any unverified field/API/parameter/owner/state is `Blocker` or `Unverified`; never guessed. |
| ScopeDrift | `none` | Any work outside the current FS/File Scope requires a change proposal before implementation. |

### 27.1 Required test cases

1. **Nominal:** representative Golden input produces the expected typed output and provenance.
2. **Boundary:** each acceptance/reject threshold boundary is exercised.
3. **Adversarial:** the rejection/fallback trigger in this profile is deliberately injected.
4. **Recovery:** restart/cancel/timeout/duplicate behavior follows the stated state and identity rules.
5. **Replay:** the same input snapshot + RuntimeManifest + parameter/model versions reproduces the same semantic result or records an approved non-determinism reason.

### 27.2 AI stop condition

AI must stop before editing code when any value in this profile is unavailable from an authoritative source. The absence of a numeric threshold does **not** authorize the AI to invent one; it means the task must bind the applicable versioned PerformanceProfile / Recipe / Qualification asset first.

## 26. Implementation status

`ImplementationSpecificationReady` means the documentary implementation contract is complete within the current architecture scope. It does **not** assert that target hardware, real Golden data, HIL, calibration qualification, production thresholds, or external interoperability have been experimentally qualified.


### 27.3 ScopeDrift stop condition

`ScopeDrift` is required to remain `none`. A request to add a new object, field, state, Owner, algorithm route, page command, external API or file outside this FS is not an implementation detail; it is a change candidate and must stop the current task until approved and re-indexed.
