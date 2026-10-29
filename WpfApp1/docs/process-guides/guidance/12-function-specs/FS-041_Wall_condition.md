# Wall condition

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-041`
- 类型：`Function Implementation Specification`
- 版本：`1.3.1-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-DOM-054A`
- 领域：`Stencil`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

分析 aperture wall profile/残差等可观察指标。

**不负责：** 生产机判、最终处置、真实设备安全功能。

## 2. 权威与契约

输入契约：`Stencil CAD + 2D/3D evidence`；输出契约：`Stencil facts/advice`。若字段尚未在现有 Schema 中冻结，必须登记到对应 ContractCandidate（通常 C-01/C-02/C-03/C-04/C-08），不能在功能目录中另建 JSON/数据库模型。

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

核对实际壁面/截面来源、同孔/面别/坐标、原索引、法向/高度方向、遮挡与有效支持；冻结壁段、深度范围、截面站位和覆盖分母。顶面点云、上下口二维投影、CAD理想壁或自动补洞mesh均不能替代实际孔壁证据。

必须在执行前阻断：缺失必需输入、版本/hash 不匹配、作用域不一致、单位/坐标不一致、资格失效、能力不支持、输入质量低于该方法的最小条件。

## 4. 正常执行流程

1. 冻结必检壁段×深度范围及实际观察能力，保留未见域。
2. 公共027/031从真实壁点形成有源索引的截面支撑，029/030按§28定义基准和方向。
3. 仅在单值、完整且已资格化的壁段计算局部倾斜/锥度与残差；折返、多段、缺测或端点外推不强拟合单线。
4. 同时保存原壁点、模型/剔点、可见缺口/污染候选及固定域覆盖；大真实偏差与算法失效分开。
5. 返回壁面几何/观察质量及证据，交原规则/复判链；不以端点吻合或低内点残差证明全壁光洁。

## 5. 算法/规则设计

**实施分类：** `Stencil 3D`

**Primary route：** `3D profile + residual`

**Fallback route：** `Approved wall profile method`

**Fallback trigger：** Fallback only between qualified profile sampling methods for the same wall-condition definition.

**Reject / Block conditions：** Required wall support or fit qualification invalid, profile pairing ambiguous, surface occluded/invalid; valid geometric deviations remain evidence.

**参数键（名称冻结，数值由批准 Profile / Recipe / Qualification 提供）：** `['WallConditionMethodId', 'MinProfileCoverage', 'MaxResidual']`

**结果语义：** `Wall condition + residual`

`MaxResidual`须由原方法明确是模型适用门还是工艺接受值；不能用同一个未定义阈值把真实壁面缺陷删成输入异常。标准粗糙度、原壁形貌偏差和模型内点残差按§28分开。

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| 壁面反射 | 注入/回放 壁面反射 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 局部缺失 | 注入/回放 局部缺失 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 3D 噪声 | 注入/回放 3D 噪声 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |

## 7. 质量门与拒识策略

至少建立三层 Gate：

1. **InputQualityGate**：输入是否可处理；
2. **AlgorithmQualityGate**：算法结果是否足够可靠；
3. **BusinessApplicabilityGate**：方法是否适用于当前产品/特征/尺度/材料/工艺。

任何 Gate 失败都要保留原因、证据引用和状态。`Unknown/Invalid/NotApplicable` 不允许被强制转换成 `OK`。

## 8. 性能与资源

先限制目标/ROI，再执行高成本精测；记录板级、目标级与最慢 1% 长尾；3D/大图使用 tile/LOD/有效域；生产节拍使用批准 PerformanceProfile。

性能采集点必须至少覆盖：输入准备、核心计算、质量评估、序列化/提交（如有）、UI 投影（如有）。高峰资源与长尾单独报告，不以平均耗时掩盖 P99。

## 9. 并发、取消、重试与恢复

- **Cancel**：取消尚未产生生产副作用的计算；已提交事实不可因 UI cancel 回滚。
- **Calculation Retry**：允许重新计算，生成新的 calculation identity。
- **Commit Retry**：必须复用原 CommitIdentity，并保持幂等。
- **Timeout**：形成明确超时事实/错误，不自动当作失败后的隐形重试。
- **Process Restart**：依赖 Snapshot/Receipt/Session 恢复；禁止读取 `latest` 猜状态。

## 10. 结果与证据

输出必须包含：输入引用、算法/规则版本、参数版本、坐标/单位、质量状态、执行时间、适用域、EvidenceRef；生产事实与 UI/报告投影分离。

## 11. UI / 操作员工作流

UI/工作区：Stencil workspace。交互遵循“状态→对象→结果→下一动作”；任何生产配置修改必须 Draft→Validate→Approve→Release；异常必须一键定位到证据。


关键操作顺序原则：系统自动带出可确定内容；操作员只处理异常、冲突和必要确认；批量动作先预览影响范围；高级参数渐进披露；每个阻断都有“原因+处理动作+证据”。

## 12. 测试设计

| 测试层 | 覆盖内容 | 必须留存 |
|---|---|---|
| Unit | 核心算法/规则、边界输入、单位/坐标、纯函数 | 输入快照、输出、expected/actual |
| Contract | Schema、状态、Owner、版本兼容 | validator report |
| Integration | 真实 consumer、Pipeline、Evidence | trace + receipt |
| Golden/Replay | 正常/边界/难例/拒识 | dataset hash + result diff |
| PerformanceProfile | `PF-FS-041` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
3. DEV-DOM-054A
4. FS-041 本文
5. Contract/Schema refs registered for this capability
6. State/Owner/AuthorityScope rules
7. UI-PCS-017 (when UI is present)
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
| Function | `FS-041` / `Wall condition` |
| Domain | `Stencil` |
| Guide | `DEV-DOM-054A` |
| Input | `Stencil CAD + 2D/3D evidence` |
| Output | `Stencil facts/advice` |
| Result semantic | `Domain InspectionFact / MeasurementSet / ReviewCandidate` |
| Canonical port | `IWallCondition` |
| Project | `Asun.Domain.Stencil` |
| UI PageContract | `UI-PCS-017` |
| Primary Work Package | `WP-17` |
| Algorithm baseline | `3D profile + residual` |
| Performance gate | `ROI/P95` |
| Test baseline | `Golden + Contract + Integration + Fault + Performance` |

### 16.1 Preconditions

- input objects exist and are version/hash identifiable;
- scope and authority are compatible;
- coordinate/unit/calibration conditions are satisfied where relevant;
- method capability covers the actual feature/measurand/material/surface/mode;
- no withdrawn artifact is referenced;
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
| Primary | `3D profile + residual` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `Approved wall profile method` | Fallback only between qualified profile sampling methods for the same wall-condition definition. |
| Reject / Block | `Required wall support or fit qualification invalid, profile pairing ambiguous, surface occluded/invalid; valid geometric deviations remain evidence.` | 保留证据与原因；不得生成权威 OK。 |

**本 FS 的 fallback 不是“另写一个算法看看”。任何替代路线都必须来自当前 Development Guide / Operator Decision Matrix / Qualification 已登记的候选集合。**

### 16.4 Parameter authority matrix

| Parameter class | Authority/source | Hard rule |
|---|---|---|
| Target/ROI | `from approved target set or runtime binding` | never guessed from image unless the FS explicitly allows auto-targeting |
| Coordinate/Unit | `from CoordinateGraph/Calibration/Manufacturing reference` | must be explicit; mismatch blocks |
| Algorithm parameters | `Recipe/Method configuration version` | no hidden constants in code |
| Thresholds | `approved library/recipe/qualification` | AI may propose only as draft unless qualification says otherwise |
| Fallback policy | `FunctionSpec decision table` | no automatic semantic downgrade |
| Performance budget | `ROI/P95` | 由 PerformanceProfile 绑定；至少记录 P50/P95/P99、峰值内存、并发安全和取消延迟；未实测不得声称 Qualified |

## 17. Robustness challenge set

At minimum, the function must be challenged against:
- `壁面反射`
- `局部缺失`
- `3D 噪声`

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
Stencil CAD + 2D/3D evidence
  → input snapshot/reference
  → Wall condition computation
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
| Port/interface | `IWallCondition` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `WallCondition.cs` | Pipeline/algorithm implementation |
| Validator | `WallConditionValidator.cs` | Input/precondition/quality checks |
| Tests | `WallConditionTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-041/` | fixed datasets, expected outputs, provenance |
| Benchmark | `WallConditionBenchmark.cs` | P50/P95/P99/resource evidence |
| UI | `src/Asun.UI.Workspaces/UI-PCS-017/` | projection only; no production fact write |


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
| T41-01 | contract/schema validation | expected assertion + evidence + trace; no silent pass |
| T41-02 | normal + boundary + reject | expected assertion + evidence + trace; no silent pass |
| T41-03 | replay/golden dataset | expected assertion + evidence + trace; no silent pass |
| T41-04 | fault injection | expected assertion + evidence + trace; no silent pass |
| T41-05 | performance benchmark | expected assertion + evidence + trace; no silent pass |
| T41-06 | real domain consumer | expected assertion + evidence + trace; no silent pass |
| T41-07 | hard-negative/false-positive set | expected assertion + evidence + trace; no silent pass |

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
| Function | `FS-041` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-DOM-054A` | 指导文档是实施语义权威。 |
| Project | `Asun.Domain.Stencil` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `IWallCondition` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-017` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `3D profile + residual` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
| SideEffectPolicy | `none; 无副作用；本功能不得直接写入生产事实、设备状态、放行状态或外部控制副作用。` | 冻结策略；任何未批准副作用路径必须 Blocker。 |
| Performance focus | `ROI/P95` | 未测量前不得声称满足性能。 |

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

- 输入契约：`Stencil CAD + 2D/3D evidence`
- 输出契约：`Stencil facts/advice`
- 质量语义：Unknown / Invalid / NotApplicable / NotQualified 不得被映射为 OK。
- 证据要求：结果必须能够回溯到输入快照、RuntimeManifest、算法/规则版本、关键参数、坐标/标定引用和执行时间。

### AI 完成后的强制回报

AI 必须输出：变更文件清单、对应 FS 条目、Contract/Schema 变更、测试、Benchmark、未关闭风险、未验证 API、禁止路径复核结果。未能证明的内容必须标记 `Unverified`，不得写成 `Completed`。

## 27. Function-specific deterministic freeze profile

| Item | Frozen implementation rule |
|---|---|
| Function class | `Stencil 3D` |
| Primary algorithm/route | `3D profile + residual` |
| Fallback | `Approved wall profile method` |
| Fallback trigger | Fallback only between qualified profile sampling methods for the same wall-condition definition. |
| Reject/Block | Required wall support or fit qualification invalid, profile pairing ambiguous, surface occluded/invalid; valid geometric deviations remain evidence. |
| Parameter authority | `['WallConditionMethodId', 'MinProfileCoverage', 'MaxResidual']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | Wall condition + residual + input snapshot + algorithm/parameter version + quality-gate outcome |
| UI rule | PageContract may project and command; it must not create/modify the underlying fact directly. |
| Performance | `ROI/P95`; target values come only from the applicable PerformanceProfile. |
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

<a id="stencil-wall-method"></a>
## 28. 实际孔壁、截面与锥度的专项方法

本节保持原`IWallCondition`/`Asun.Domain.Stencil`和Owner；新增语义待原C-03/04/07采纳。使用[027原表面/索引](../../../shared-modules/packages/PKG-027_SurfaceData.md#surface-data-provenance)、031/029特征和[030量测](../../../shared-modules/packages/PKG-030_Metrology.md)，不在钢网域复制3D拟合、剖面或最近距离Core。

### 28.1 固定被测壁域与实际观察

输入必须指向本孔实际可见壁面点或合格实测截面；斜视表面/多视图重建亦需各自标定、原支持和重建资格，不能因生成了点云就认为见到了内壁。直接观察不到的深部、镜面失返、遮挡和重建洞保持未知；用CAD封口/表面三角化跨洞只可显示派生模型，不增加覆盖。

先按设计/批准参考建立必检壁段和深度范围。圆孔可用固定基准轴的周角s及高度h；异形孔用参考边弧长s、明确朝向和局部截面编号，圆角/尖角另分段。h=0/上界来自具备资格的上下表面或独立基准，不从当前点云min/max当作实际孔深。坐标/基准不明只阻断依赖的量测，不删除已观察原壁点。

每条截面定义包含高度方向a和批准横向u的平面、有限取样带、投影/插值方法及误差预算。只把带内合格原壁点投影形成剖面；带过宽混入不同周角/曲面会伪造平滑壁，带太窄缺点则无值。一个截面可能有两侧、多层或折返壁，必须保持分支身份，不能按最近点串成单条线。原索引/多视融合的贡献映射由027保存。

### 28.2 首批量值及方向

**局部壁倾斜。** 在一段已确认单值、近直线且深度支撑充分的真实壁剖面上，以h为固定轴、u为该壁向外方向，优先调用公共HALCON直线/3D特征拟合，模型写为`u(h)=b+k·h`；报告该深度区间的有符号倾斜`α=atan(k)`。这只是单壁相对高度轴的倾斜；圆孔中须圆度/轴/角向资格成立才可称局部锥度，完整周向未见不能称整孔锥角。对称直锥的几何全夹角`2|α|`是另派生量，向上/向下扩口方向仍单独保留，不把它与有符号α写入同一Angle。

圆孔真实径向剖面`r(h)=r0+k·h`时k>0表示向上变宽；若方法以相反面为上，必须显式变换方向和来源，不能静默取绝对值。两侧矩形/槽壁分别拟合自身的有符号方向；只有已证共轴/对称时才可由宽差的一半描述单壁变化。阶梯、倒角、鼓肚、挂渣或折返壁不能用贯穿全部深度的一条线自动解释，须分段并保留断点/原偏差。

**端点尺寸不是壁面事实。** 下口h=0的半径.100mm、上口h=.120mm的半径.112mm且同轴，只确定两端尺寸；只有实际壁点支持直锥模型时才得到α≈+5.7106°。若保持h向上而上/下半径互换，α应为−5.7106°，不能因取绝对值丢失扩口方向。相同端点之间可以有−.020mm内凹/挂渣，故上下口尺寸与二维投影不能证明壁直、全壁锥度或光洁。端点可作独立开口量，不能用它们填补FS-041缺测。

**残差和形貌。** 保留原有效点到已冻结模型的有符号/无符号残差定义、点数、剔点、有效深度/角向覆盖，区分内点RMS与全部原壁支持残差。拟合后必须对最终模型重算残差和支持资格；不能直接继承拟合前候选的内点列表或日志RMS。真实壁面超差是可评价的异常，不必因残差大一律变算法错误；模型不适用时仍交原形貌候选和明确无值原因。

本阶段可提供具名的剖面残差分布/峰谷/平均绝对偏差；**不得把这些值命名Ra、Rz、Sa或标准粗糙度**，除非相应滤波、截止波长/评价长度、仪器传递特性、采样/不确定度和标准版次均已冻结并具资格。高通强度/反光纹理与3D粗糙度也不互换。

### 28.3 覆盖与数值资格

冻结参考壁域`S_req`及非重叠(s,h)单元或明确必需截面站位。每单元只有真实支持满足原方法的点距、深度跨度、横向带宽/最大缺口、视角及误差条件才记合格；一个点不自动代表整单元。参数域覆盖按预先固定权重计算，重复视图、同点重建或渲染网格不能重复计数。圆周接缝0/2π同一位置去重；仅见一侧不能报360°。

参数域覆盖率应明确叫“参考壁域观察覆盖”；若报告真实壁面积覆盖，须另有合格表面面积映射/Jacobian，不能将ds·dh直接当有斜率/曲率的真实面积。覆盖不足使依赖全壁的结论未知，但完整子段的局部量可保留。点数很多、拟合RMS低和凸包覆盖都不能填补大洞/缺侧；未取得的深度区仍留分母。

HALCON原件确认`fit_primitives_object_model_3d`需先提供对应单一primitive的点，候选为平面/圆柱/球；不能把未分层混点或锥壁直接说成其已支持的锥模型。`distance_object_model_3d`可对primitive/三角形/点等计算距离、会向输入模型写距离属性，且非零MaxDistance把超距值截成上限。适配须用独占派生对象及明确目标类型；截断值只能作为距离下界诊断，不能作为真实最大偏差或方向厚度。有限壁域的物理解释仍由本FS及030负责。

### 28.4 反例、恢复和性能

| 输入/故障 | 应有结果 |
|---|---|
| 实测直线r=.100+.1h、h∈[0,.120]mm | 下/上半径.100/.112；局部α≈5.7106°，需保留角向覆盖才能讨论整孔 |
| 上述相同端点，但中段向内偏.020mm | 端点不变，原中段残差保留；不得由两端宣布直锥/光洁 |
| 12个固定壁域单元仅9个有足够支持 | 参考域覆盖75%；重复拍这9格不变成100% |
| 只有上表面和上下口轮廓 | 开口量可有值，FS-041保持未观测；不可创建理想壁补全 |
| 最近距离真实.08mm但native上限.05 | 返回.05只是达到截断界，不能报告实测最大.05或以此通过.06接受值 |
| 壁面高残差是真实挂渣、鲁棒拟合将其剔除 | 保留原异常；内点模型可用不代表全部壁面合格 |

执行预算含原壁点、法向/源索引、截面邻域索引、派生属性和模型/原点残差，不为每测站复制整云。先按批准空间域限制，再用公共有界查询；LOD只用于显示。取消在native退出后释放派生对象/租约，旧视角或深度修订回调不得更新当前结果。壁面数据缺失可恢复为受控补采/人工复核的宿主候选，不在本FS发硬件动作。钢网与PG-003微孔复用表面/剖面Core，各自冻结壁材/层/观察方向与工艺接受；不能把微孔可见口径当钢网壁资格。
