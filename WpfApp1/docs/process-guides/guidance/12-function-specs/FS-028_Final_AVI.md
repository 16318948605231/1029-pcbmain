# Final AVI

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-028`
- 类型：`Function Implementation Specification`
- 版本：`1.3.1-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-DOM-050D`
- 领域：`PCB`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

按[PG-011](../../processes/PG-011_final-avi.md)调用已批准成品外观/尺寸/高度方法，返回逐功能候选、具名量值、覆盖/关联缺口与证据引用；提供无写入副作用的复判建议。双面精确汇合及翘曲定义以PG-011 §12/§14为唯一工艺正文，算法不自行变成整板结果、复判任务或放行Owner。

**不负责：** 写入生产事实/机判、ReviewClaim的创建/领取/续租/撤销、人工意见、质量放行、最终处置或真实设备安全功能。算法可返回ReviewCandidate语义的候选原因/证据，正式入队由原应用/044按已提交事实和权限策略处理。

## 2. 权威与契约

输入契约：`ManufacturingGeometry + image`；输出契约：`InspectionFact/MeasurementSet`。若字段尚未在现有 Schema 中冻结，必须登记到对应 ContractCandidate（通常 C-01/C-02/C-03/C-04/C-08），不能在功能目录中另建 JSON/数据库模型。

上述Input/Output是既有兼容登记概括，不是“仅一张图即可整板终检”。请求须绑定共同终检身份/分面尝试、必检库存及观察路线、原始输入/方法/资格、精确分面结果/提交引用；翘曲另需真实Surface、表面/支撑、采样/有效域、基准和方向。字段沿C-01/C-02/C-03/C-04/C-07/C-08采纳；`InspectionFact`在算法返回处只表示待原Owner校验/提交的typed产物，不授予本算法生产写入权。

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

验证输入作用域、单位/坐标、版本、质量元数据和所需能力；对制造参考任务优先使用 Ready 的 ManufacturingGeometrySnapshot。

必须在受影响义务计算前阻断：缺失必需输入、版本/hash不匹配、作用域不一致、单位/坐标不一致、资格失效、能力不支持、输入质量低于该方法的最小条件。共同物理身份/运行绑定不明时拒绝整个依赖请求；只有B面或高度输入缺失时，保留可独立验证的A面/2D候选及缺项，不伪造全板完成，也不删除已有合法证据。

## 4. 正常执行流程

1. 固定调用用途及PG-011的共同请求/评价修订，核物理板/单元、面/阶段、运行清单、必检库存、方法与资格。无正式配对关系时不从最新同条码拼面；原计算/提交Unknown先查询，不重跑掩盖。
2. 按目标和冻结观察路线核输入：同轴/侧光AND不能用两份同轴凑齐，单面空间覆盖不能补另一面或3D。逐义务保留缺采集、无效、未评价、规则结果与提交状态；批准不适用才按依据调整适用分母。
3. 调用现有工艺方法对分面区域提取候选/精检，保存原图/原几何、输入质量与排除原因；不得替代未提供的光板线路产品。候选语义和接受参数来自该方法/产品Profile，不用“终检统一阈值”覆盖不同材料或缺陷。
4. 按[PG-011 §12.6](../../processes/PG-011_final-avi.md#avi-defect-association)只对有物理依据的候选建立关联。传输重复按原身份/hash去重；近邻图连通不证明同缺陷；原候选不删除，跨面关联不减必检分母。
5. 请求含翘曲时按[PG-011 §14.1–14.4](../../processes/PG-011_final-avi.md#avi-warpage-measurands)复用027/029/030/018，固定表面、支撑、参考/方向及评价域，分别计算具名偏离/样本PV等获准量。LS/TLS去平面不自动成为最小区域平面度或弓曲率，缺高度不输出0。
6. 返回逐义务量值、候选及全部来源/质量/缺口。原039评价，原结果Owner经040提交；PG-011汇合应用仅消费冻结的精确分面事实闭包和当前接受资格，不让本算法调用数据库改写机判。
7. 需要复判时返回建议原因与原证据引用，原044/应用自行建立并受控领取任务。没有合格原证据时明确缺项；复判建议不是ReviewClaim，也不能把不可观测区域“转人工”后自动解除完整性阻断。

## 5. 算法/规则设计

**实施分类：** `PCB Inspection`

**Primary route：** `candidate detection + read-only review recommendation`

**Fallback route：** `Conservative unresolved-evidence route`

**Fallback trigger：** 歧义保留原候选/未知及复判建议；原应用决定是否提交给044，不取得Claim，不用人工入口解除缺测或证据缺口。

**Reject / Block conditions：** Input coverage gap, candidate ambiguity, evidence missing, model/recipe mismatch.

阻断按依赖范围解释：身份/方法错配或原证据不可校验时不计算其依赖量；候选关联歧义阻止“已确认同缺陷”结论，但仍返回原候选与未决建议；局部覆盖不足保留局部量并阻止完整域通过。Fallback只保留未决路径，不是清除这些阻断，也不把一个局部失败扩成丢弃整板合法结果。

**参数键（名称冻结，数值由批准 Profile / Recipe / Qualification 提供）：** `['FinalAVIMethodId', 'ReviewThreshold', 'CoverageFloor', 'EvidenceRequirementId']`

**结果语义：** 逐义务候选/具名`MeasurementSet`及证据、质量和未决；需要时返回只读`ReviewCandidate`建议。`ReviewClaim`仅属044的受控领取事务，不是算法产物。原兼容`InspectionFact`由原生产Owner提交后才成为相应用途的持久事实。

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| 低对比 | 注入/回放 低对比 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 纹理 | 注入/回放 纹理 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 异物/毛刺 | 注入/回放 异物/毛刺 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 批次变化 | 注入/回放 批次变化 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |

## 7. 质量门与拒识策略

至少建立三层 Gate：

1. **InputQualityGate**：输入是否可处理；
2. **AlgorithmQualityGate**：算法结果是否足够可靠；
3. **BusinessApplicabilityGate**：方法是否适用于当前产品/特征/尺度/材料/工艺。

任何 Gate 失败都要保留原因、证据引用和状态。`Unknown/Invalid/NotApplicable` 不允许被强制转换成 `OK`。

## 8. 性能与资源

先限制目标/ROI，再执行高成本精测；记录板级、目标级与最慢1%长尾；3D/大图按tile流转，LOD只作显示，量测始终使用批准的完整评价支持及原始精度。不得为加速缩掉翘曲极值域或丢必检项；生产节拍使用批准PerformanceProfile。

性能采集点必须至少覆盖：输入准备、核心计算、质量评估、序列化/提交（如有）、UI 投影（如有）。高峰资源与长尾单独报告，不以平均耗时掩盖 P99。

## 9. 并发、取消、重试与恢复

- **Cancel**：取消尚未产生生产副作用的计算；已提交事实不可因 UI cancel 回滚。
- **Calculation Retry**：先查询原执行，仍运行则等待，明确可恢复则续接；相同输入确实无法续接且原执行已终结时，由038创建关联原意图的新计算执行。输入/方法改变或真实重采分别按原Owner生成新关联，不用新计算掩盖提交Unknown。
- **Commit Retry**：必须复用原 CommitIdentity，并保持幂等。
- **Timeout**：形成明确超时事实/错误，不自动当作失败后的隐形重试。
- **Process Restart**：依赖 Snapshot/Receipt/Session 恢复；禁止读取 `latest` 猜状态。

## 10. 结果与证据

输出必须包含：输入引用、算法/规则版本、参数版本、坐标/单位、质量状态、执行时间、适用域、EvidenceRef；生产事实与 UI/报告投影分离。

## 11. UI / 操作员工作流

UI/工作区：PCB inspection workspace。交互遵循“状态→对象→结果→下一动作”；任何生产配置修改必须 Draft→Validate→Approve→Release；异常必须一键定位到证据。


关键操作顺序原则：系统自动带出可确定内容；操作员只处理异常、冲突和必要确认；批量动作先预览影响范围；高级参数渐进披露；每个阻断都有“原因+处理动作+证据”。

## 12. 测试设计

| 测试层 | 覆盖内容 | 必须留存 |
|---|---|---|
| Unit | 核心算法/规则、边界输入、单位/坐标、纯函数 | 输入快照、输出、expected/actual |
| Contract | Schema、状态、Owner、版本兼容 | validator report |
| Integration | 真实 consumer、Pipeline、Evidence | trace + receipt |
| Golden/Replay | 正常/边界/难例/拒识 | dataset hash + result diff |
| PerformanceProfile | `PF-FS-028` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
3. DEV-DOM-050D
4. FS-028 本文
5. Contract/Schema refs registered for this capability
6. State/Owner/AuthorityScope rules
7. UI-PCS-015 (when UI is present)
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
| Function | `FS-028` / `Final AVI` |
| Domain | `PCB` |
| Guide | `DEV-DOM-050D` |
| Input | `ManufacturingGeometry + image` |
| Output | `InspectionFact/MeasurementSet` |
| Result semantic | `Domain InspectionFact / MeasurementSet / ReviewCandidate` |
| Canonical port | `IFinalAvi` |
| Project | `Asun.Domain.Pcb` |
| UI PageContract | `UI-PCS-015` |
| Primary Work Package | `WP-15` |
| Algorithm baseline | `candidate detection + read-only review recommendation` |
| Performance gate | `ROI-first P95` |
| Test baseline | `Golden + Contract + Integration + Fault + Performance` |

### 16.1 Preconditions

- input objects exist and are version/hash identifiable;
- scope and authority are compatible;
- coordinate/unit/calibration conditions are satisfied where relevant;
- method capability covers the actual feature/measurand/material/surface/mode;
- withdrawn artifacts cannot supply current qualified contributions; their identifiers and original evidence remain available for historical provenance and correction;
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
| Primary | `candidate detection + read-only review recommendation` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `Conservative unresolved-evidence route` | 歧义保留原候选/未知及复判建议；原应用决定是否提交给044，不取得Claim，不用人工入口解除缺测或证据缺口。 |
| Reject / Block | `Input coverage gap, candidate ambiguity, evidence missing, model/recipe mismatch.` | 保留证据与原因；不得生成权威 OK。 |

**本 FS 的 fallback 不是“另写一个算法看看”。任何替代路线都必须来自当前 Development Guide / Operator Decision Matrix / Qualification 已登记的候选集合。**

### 16.4 Parameter authority matrix

| Parameter class | Authority/source | Hard rule |
|---|---|---|
| Target/ROI | `from approved target set or runtime binding` | never guessed from image unless the FS explicitly allows auto-targeting |
| Coordinate/Unit | `from CoordinateGraph/Calibration/Manufacturing reference` | must be explicit; mismatch blocks |
| Algorithm parameters | `Recipe/Method configuration version` | no hidden constants in code |
| Thresholds | `approved library/recipe/qualification` | AI may propose only as draft unless qualification says otherwise |
| Fallback policy | `FunctionSpec decision table` | no automatic semantic downgrade |
| Performance budget | `ROI-first P95` | 由 PerformanceProfile 绑定；至少记录 P50/P95/P99、峰值内存、并发安全和取消延迟；未实测不得声称 Qualified |

## 17. Robustness challenge set

At minimum, the function must be challenged against:
- `低对比`
- `纹理`
- `异物/毛刺`
- `批次变化`

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

下表是原执行状态在本调用边界的投影，不新建FS私有状态机。Ready按本次调用实际计算义务核验；Completed可以携带明确的局部无效/缺项，不能被宿主当整板通过。取消/超时不证明native已停止，原执行Owner确认停止/排空前不得释放仍在用的资源。

| State | Entry condition | Allowed behavior |
|---|---|---|
| `Ready` | all required inputs and capability/qualification gates pass | execute |
| `Blocked` | required input/capability/authority missing | show reason; no production effect |
| `RecoverableError` | execution failed but restart/retry may be valid | retain evidence; follow retry policy |
| `Invalid/Rejected` | result cannot be trusted or is out-of-domain | no quality pass |
| `Completed` | 当前算法输出及证据引用已按约定返回调用者 | 不可变输出；不代表生产事实已提交、双面已完整或人工复判已完成 |

Only approved Application/Domain services may create production facts or machine-authoritative commands. UI and ViewModel are projections and command clients, not fact authorities.

## 19. Data/provenance and evidence mapping

```text
ManufacturingGeometry + image
  → input snapshot/reference
  → Final AVI computation
  → quality gate
  → Domain InspectionFact / MeasurementSet / ReviewCandidate
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
| Port/interface | `IFinalAvi` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `FinalAvi.cs` | Pipeline/algorithm implementation |
| Validator | `FinalAviValidator.cs` | Input/precondition/quality checks |
| Tests | `FinalAviTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-028/` | fixed datasets, expected outputs, provenance |
| Benchmark | `FinalAviBenchmark.cs` | P50/P95/P99/resource evidence |
| UI | `src/Asun.UI.Workspaces/UI-PCS-015/` | projection only; no production fact write |


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
| T28-01 | contract/schema validation | expected assertion + evidence + trace; no silent pass |
| T28-02 | normal + boundary + reject | expected assertion + evidence + trace; no silent pass |
| T28-03 | replay/golden dataset | expected assertion + evidence + trace; no silent pass |
| T28-04 | fault injection | expected assertion + evidence + trace; no silent pass |
| T28-05 | performance benchmark | expected assertion + evidence + trace; no silent pass |
| T28-06 | real domain consumer | expected assertion + evidence + trace; no silent pass |
| T28-07 | hard-negative/false-positive set | expected assertion + evidence + trace; no silent pass |

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
| Function | `FS-028` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-DOM-050D` | 指导文档是实施语义权威。 |
| Project | `Asun.Domain.Pcb` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `IFinalAvi` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-015` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `candidate detection + read-only review recommendation` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
| SideEffectPolicy | `算法返回候选/量值/证据与复判建议；生产机判、提交、Claim及人工意见均由原Owner执行，无隐含写入权。` | 冻结策略；任何未批准副作用路径必须 Blocker。 |
| Performance focus | `ROI-first P95` | 未测量前不得声称满足性能。 |

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

- 输入契约：`ManufacturingGeometry + image`
- 输出契约：`InspectionFact/MeasurementSet`
- 质量语义：Unknown / Invalid / NotApplicable / NotQualified 不得被映射为 OK。
- 证据要求：结果必须能够回溯到输入快照、RuntimeManifest、算法/规则版本、关键参数、坐标/标定引用和执行时间。

### AI 完成后的强制回报

AI 必须输出：变更文件清单、对应 FS 条目、Contract/Schema 变更、测试、Benchmark、未关闭风险、未验证 API、禁止路径复核结果。未能证明的内容必须标记 `Unverified`，不得写成 `Completed`。

## 26. Implementation status

当前状态为`DocMapped`准备，未取得`ImplementationSpecificationReady`。后者要求当前范围的指导与正式合同完整，不等于目标硬件、真实Golden、HIL、标定、生产阈值或现场互操作已获实验资格。

## 27. Function-specific deterministic freeze profile

| Item | Frozen implementation rule |
|---|---|
| Function class | `PCB Inspection` |
| Primary algorithm/route | `candidate detection + read-only review recommendation` |
| Fallback | `Conservative unresolved-evidence route` |
| Fallback trigger | 歧义保留原候选/未知及复判建议；原应用决定是否提交给044，不取得Claim，不用人工入口解除缺测或证据缺口。 |
| Reject/Block | Input coverage gap, candidate ambiguity, evidence missing, model/recipe mismatch. |
| Parameter authority | `['FinalAVIMethodId', 'ReviewThreshold', 'CoverageFloor', 'EvidenceRequirementId']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | 逐义务候选 / MeasurementSet / 只读ReviewCandidate建议 + 精确输入引用 + 方法版本 + 质量/缺口；不创建ReviewClaim或直接持久化机判 |
| UI rule | PageContract may project and command; it must not create/modify the underlying fact directly. |
| Performance | `ROI-first P95`; target values come only from the applicable PerformanceProfile. |
| External API | 具体调用先查目标版本官方文档与公共签名；不验证AsunImage/DevExpress依赖、兼容性或授权，项目自身行为按功能验收。 |
| Unknown | Any unverified field/API/parameter/owner/state is `Blocker` or `Unverified`; never guessed. |
| ScopeDrift | `none`; any work outside the current FS/File Scope requires a change proposal before implementation. |

### 27.1 Required test cases

1. **Nominal:** representative Golden input produces the expected typed output and provenance.
2. **Boundary:** each acceptance/reject threshold boundary is exercised.
3. **Adversarial:** the rejection/fallback trigger in this profile is deliberately injected.
4. **Recovery:** restart/cancel/timeout/duplicate behavior follows the stated state and identity rules.
5. **Replay:** the same input snapshot + RuntimeManifest + parameter/model versions reproduces the same semantic result or records an approved non-determinism reason.

### 27.2 AI stop condition

AI must stop before editing code when any value in this profile is unavailable from an authoritative source. The absence of a numeric threshold does **not** authorize the AI to invent one; it means the task must bind the applicable versioned PerformanceProfile / Recipe / Qualification asset first.

### 27.3 ScopeDrift stop condition

`ScopeDrift` is required to remain `none`. A request to add a new object, field, state, Owner, algorithm route, page command, external API or file outside this FS is not an implementation detail; it is a change candidate and must stop the affected slice until approved and re-indexed.

### 27.4 终检专项可判定接入验收

本表是未来实现/集成的验收输入，未运行平台测试。数值与反例唯一正文为[PG-011 §14.4](../../processes/PG-011_final-avi.md#avi-numeric-challenges)，不要复制为第二套工艺阈值。测试调用层必须在正式合同采纳后绑定。

| 刺激/调用层 | 必须断言 | 不得出现 |
|---|---|---|
| 分面计算：同板A有效、B过曝，6项中仅5项有效 | 输出保留A/B有效候选、B无效原因及原义务；失败证据已提交时分别显示5/6有效与6/6提交 | Completed被解释为全检通过；缺测从分母删除 |
| 原应用汇合：e2固定b2后收到b1或重复b2 | 只按精确输入关系接受；同内容重复只贡献一次，异内容同修订冲突；e1原件可追溯 | latest/最优分面拼板；重复消息多计覆盖 |
| 原应用汇合：缺B/b1的e1/c1已冻结，之后原b1到达 | 动态收集可更新，原评价输入不变；新捕获形成关联后继评价/计算，没有新物理采集 | 原e1/c1内填入新输入；把到达事件当真实重拍 |
| 原执行集成：聚合截止，B来源仍在native执行 | 按原政策结束等待并固定不完整快照；038继续观察实际执行/排空，来源封口另行确认 | 用聚合终态释放仍在用的来源租约，或伪造B完成/封口 |
| 原Owner集成：原提交Unknown且出现后继重测 | 查询原提交身份，保留后继关联；撤销生效/接受栅栏未冻结则该验收保持未通过 | 用新提交或后继结果抹掉未知；声称本算法实现跨服务原子性 |
| 纯计算：同轴重复两次、缺低角度AND输入 | 原观察可查，所依赖功能缺输入；只有批准的完整替代路线才可满足 | 凭帧数/空间面积100%认定功能完整 |
| 关联计算：0/0.4/0.8mm挑战、跨面同XY | 近邻不作传递确认；保留原候选/未决，面别义务独立 | 连通分量直接确定物理身份；簇数减少提升覆盖 |
| 公共量测调用：斜参考平面与同变换 | 法向距与指定轴距分别具名；同时变换点/平面/方向后对应量保持 | 设备Z冒充法向高；取abs隐藏板面方向 |
| 公共量测调用：TLS/鞍形/缺角/共线支撑 | 解析结果符合PG；TLS-PV不称最小区域；全域缺口保持未知，共线不输出间隙0 | 逐tile贴平、滤掉极值或显示LOD改变测量 |
| 算法边界：返回复判建议、取消或重放 | 无Claim创建/领取/写入调用；原038管理租约至实际结束，原044独立处理意见 | 复判建议写机判、页面动作放行、超时提前释放native资源 |

原Contract接收项集中为：精确分面引用/封口/撤销接受边界、观察义务与路线、具名量值及支撑/域引用、只读复判建议与Owner映射。项目/端口/Schema登记不得被本表自行改名或扩字段；UI-PCS-015只消费已采纳投影，最终真实UI和性能验收独立执行。

## 当前工序专项细化

本FS与[对应PG唯一专项](../../processes/PG-011_final-avi.md#avi-coverage-pairing)共同实施。精确分面汇合、迟到/撤销及接受边界在[§12.4](../../processes/PG-011_final-avi.md#avi-exact-side-join)，库存和分母在[§12.5](../../processes/PG-011_final-avi.md#avi-obligation-inventory)，跨视角关联在[§12.6](../../processes/PG-011_final-avi.md#avi-defect-association)，翘曲公式、支撑与失败链在[§14.1–14.5](../../processes/PG-011_final-avi.md#avi-warpage-measurands)。历史Input/Output概括不能省略所需参考、适用性与来源；正式契约仍由原Owner采纳。本轮为DesignReview细化，FS继续DocMapped准备，未执行产品算法或现场验收。
