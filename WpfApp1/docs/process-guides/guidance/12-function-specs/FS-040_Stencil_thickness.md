# Stencil thickness

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-040`
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

对钢网厚度执行独立计量，不能由开口图像推断。

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

核对同一钢网/版次/张网状态、上下表面身份、共同坐标与翻面变换、真实双面或合格直接测厚能力；冻结厚度方向、测站/面积域、阶梯区及独立基准。单面高度、另一张网的下表面或不同张紧状态的配对不能进入厚度计算。

必须在执行前阻断：缺失必需输入、版本/hash 不匹配、作用域不一致、单位/坐标不一致、资格失效、能力不支持、输入质量低于该方法的最小条件。

## 4. 正常执行流程

1. 固定上下表面/直接测厚来源与量测定义，核两面坐标及实体状态。
2. 027保留真实有效支持/原索引；029只在各自批准表面域估计参考，不混拟合上下层或台阶。
3. 030按§28沿冻结方向在同一测线上配对实际有限表面，计算局部厚度；无对应或多交点返回无值。
4. 分别保存上下原始值、方向、交点、方法、覆盖、差值及不确定度；显示舍入不参加判定。
5. 交原规则与提交Owner；台阶高差、单面翘曲和厚度分别评价，缺面不填理想面。

## 5. 算法/规则设计

**实施分类：** `Stencil Metrology`

**Primary route：** `3D metrology + calibration`

**Fallback route：** `Re-acquire/revalidate calibration`

**Fallback trigger：** Never substitute stale calibration. If current 3D calibration is invalid, block thickness.

**Reject / Block conditions：** Reference-surface invalid, calibration expired, valid-point fraction too low.

**参数键（名称冻结，数值由批准 Profile / Recipe / Qualification 提供）：** `['CalibrationId', 'MinValidFraction', 'MaxThicknessResidual']`

**结果语义：** `Thickness measurement + qualification`

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| 表面翘曲 | 注入/回放 表面翘曲 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 参考面错误 | 注入/回放 参考面错误 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 校准漂移 | 注入/回放 校准漂移 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |

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
| PerformanceProfile | `PF-FS-040` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
4. FS-040 本文
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
| Function | `FS-040` / `Stencil thickness` |
| Domain | `Stencil` |
| Guide | `DEV-DOM-054A` |
| Input | `Stencil CAD + 2D/3D evidence` |
| Output | `Stencil facts/advice` |
| Result semantic | `Domain InspectionFact / MeasurementSet / ReviewCandidate` |
| Canonical port | `IStencilThickness` |
| Project | `Asun.Domain.Stencil` |
| UI PageContract | `UI-PCS-017` |
| Primary Work Package | `WP-17` |
| Algorithm baseline | `3D metrology + calibration` |
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
| Primary | `3D metrology + calibration` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `Re-acquire/revalidate calibration` | Never substitute stale calibration. If current 3D calibration is invalid, block thickness. |
| Reject / Block | `Reference-surface invalid, calibration expired, valid-point fraction too low.` | 保留证据与原因；不得生成权威 OK。 |

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
- `表面翘曲`
- `参考面错误`
- `校准漂移`

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
  → Stencil thickness computation
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
| Port/interface | `IStencilThickness` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `StencilThickness.cs` | Pipeline/algorithm implementation |
| Validator | `StencilThicknessValidator.cs` | Input/precondition/quality checks |
| Tests | `StencilThicknessTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-040/` | fixed datasets, expected outputs, provenance |
| Benchmark | `StencilThicknessBenchmark.cs` | P50/P95/P99/resource evidence |
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
| T40-01 | contract/schema validation | expected assertion + evidence + trace; no silent pass |
| T40-02 | normal + boundary + reject | expected assertion + evidence + trace; no silent pass |
| T40-03 | replay/golden dataset | expected assertion + evidence + trace; no silent pass |
| T40-04 | fault injection | expected assertion + evidence + trace; no silent pass |
| T40-05 | performance benchmark | expected assertion + evidence + trace; no silent pass |
| T40-06 | real domain consumer | expected assertion + evidence + trace; no silent pass |
| T40-07 | hard-negative/false-positive set | expected assertion + evidence + trace; no silent pass |

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
| Function | `FS-040` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-DOM-054A` | 指导文档是实施语义权威。 |
| Project | `Asun.Domain.Stencil` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `IStencilThickness` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-017` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `3D metrology + calibration` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
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
| Function class | `Stencil Metrology` |
| Primary algorithm/route | `3D metrology + calibration` |
| Fallback | `Re-acquire/revalidate calibration` |
| Fallback trigger | Never substitute stale calibration. If current 3D calibration is invalid, block thickness. |
| Reject/Block | Reference-surface invalid, calibration expired, valid-point fraction too low. |
| Parameter authority | `['CalibrationId', 'MinValidFraction', 'MaxThicknessResidual']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | Thickness measurement + qualification + input snapshot + algorithm/parameter version + quality-gate outcome |
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

<a id="stencil-thickness-method"></a>
## 28. 双表面、方向与阶梯钢网厚度

本节细化原`IStencilThickness`/`Asun.Domain.Stencil`，不改变Owner。精确字段仍待C-03/04/07采纳；[027表面](../../../shared-modules/packages/PKG-027_SurfaceData.md#surface-data-provenance)、[029基准](../../../shared-modules/packages/PKG-029_ReferenceSurface.md#reference-surface-qualification)及[030量测](../../../shared-modules/packages/PKG-030_Metrology.md)是唯一公共Core。

### 28.1 配对前置与来源

支持两类有名方法：①同实体相容状态、共同坐标内实际上下表面的方向配对；②已有合格真实测厚装置提供的量值/测站/量程/资格与原证据。②不是用CAD名义厚度、单面高度或材料库填数，也不由本FS实现厂商SDK。选哪类方法由能力/配方冻结，不能在运行中隐式混合。

双面即使先后拍摄，也须证实测量期间张网、装夹、温度/变形和翻面配准在方法适用条件内；不要求假造同时拍摄，但状态不相容就拒绝相关配对。公共007/060/标定提供独立变换和资格，禁止为使上下点云“最吻合”而自由ICP重合两表面，这会消除真实厚度。上下同一数组下标不等于同一物理测站；每个交点保留Surface/返回层/原索引及映射来源。

输入拒绝：两层来源混淆、单位/面别错、标定与该观察不匹配或在相应用途中失效、法向未定义、只见上面、下表面被夹具代替、网孔内没有材料而仍要求板厚、表面层顺序不明。不能仅因后来存在新标定版本而把历史原标定一律判无效；历史回放绑定原快照，新的生产用途另核当前资格。批准ROI/排除必须在运行前固定，不能为躲污染/台阶删域；原始缺点与计划不适用分开。

### 28.2 首批可计算定义

P1先选取每阶梯区的固定测站q或面积网格D_t，并冻结单位方向a（从下向上）及参考frame。每条测线`r(t)=q+t·a`要求在上、下**有限已观察表面**上各有一个适用交点p_u、p_l，厚度为`t_a=t_u−t_l`。方向a必须单位化，t的单位与坐标相同；负厚度、交点次序不明、多返回无唯一层、近切向和支持越界分别无效，不取abs、0或任意最近点。

首批各阶梯区可使用已合格局部平面patch：`n_i·p+d_i=0`、`||n_i||=1`，交线参数`t_i=−(n_i·q+d_i)/(n_i·a)`。只有分母满足方法数值门且交点位于各自有效patch支持内才可用；不能仅因无限平面有交点就跨大洞/跨区外推。上/下平面非平行时厚度随q变化，不存在可替代全区的单个面面距离。曲面/网格路线需冻结多交点、有限拓扑、插值与误差后再扩展；显示mesh不生成真实下表面。

参考面沿029先核二维展开、内外点、原点残差与适用域。上/下各自拟合，再做方向交点；不能把两层或相邻台阶合成一个“更稳定”平面。少数坏点的鲁棒排除仍保留原证据；成像失效与真实突起/划伤分别处理，拟合不能剥除被测缺陷而仍声称全区厚度符合。

**三个量不得混用。** 沿全局Z的层差、沿局部法向的厚度、最近表面距离均可能不同；HALCON最近距离及其截断结果不是自动厚度。对上下`z=0.1x`和`z=0.1x+0.12`，Z厚度.12mm，法向厚度`.12/sqrt(1.01)`≈.119404mm。若上样点x=0、下样点x=1，直接减z仅得.02mm，说明相邻像素/最近采样点不能代替同测线配对。

### 28.3 台阶、覆盖与不确定度

阶梯区由制造/批准参考定义，分别保留其上下表面范围和过渡边。每区厚度、上表面台阶高差、下表面台阶高差及过渡宽度是不同被测量；一侧台阶不能直接成为厚度增量。区A上/下=.12/0mm、区B=.17/.05mm，两区厚度同为.12mm，而上/下台阶都为.05mm。区域相交或边缘混合像素先按冻结边界策略标未知，不临时扩大不检区。两区模型可比较台阶，但无有效支持时不得外推到同一点编造台阶值。

计数模式按冻结必需测站数报告有效配对/总数；面积模式按固定D_t及各格两面支持的共同有效面积报告，重复/高密点不增加覆盖。未配对、污染、取消、缺tile都留在原分母。仅采样点或有限patch的最小值叫“有效测站/有效域最小”，不得声称整网连续最小；点数很多不证明覆盖空白区。

每个t同时保留上下位置误差、方向/配准/标定以及拟合/插值贡献；上下面误差可能相关，不能机械独立平方和。不确定度方法由原030/Qualification负责；内点RMS不是厚度不确定度。若有经资格化的确定误差界ε_u、ε_l，固定方向层差可保守传播为ε_u+ε_l，方向与配准误差另计；没有依据不编造上下限用于PASS。

### 28.4 可复算反例与恢复/预算

| 输入/故障 | 应有结果 |
|---|---|
| 上/下z=.12/0mm且完整相容 | 沿Z厚度.12mm；删除下表面后厚度无值，2D结果保持其独立资格 |
| .1坡面的两个平行层，Z间距.12 | Z和法向分别为.12和约.119404mm；不能混填同一个Thickness |
| 上下平面不平行，上z=.12+.02x、下z=0 | x=0/1测站厚度.12/.14mm；全区不能只输出一个无限平面距离 |
| 上表面台阶+.05，下表面也+.05 | 厚度差0；仅上表面抬升不足以证明加厚 |
| 10个必需测站只有8个双面合格 | 覆盖80%；2个未知保留；有效均值不代表全网均值或100%完成 |
| 一面新修订/翻面变换迟到、提交Unknown | 新计算不得混入旧配对；旧提交查原身份，不重新采集掩盖未知 |

预算含两面原点、过滤/索引映射、参考拟合、交点查询及证据，按区复用只读参考且逐目标核外推资格。取消不释放尚在native使用的两面租约；重算不覆盖前次厚度。页面必须显示厚度方向、上下来源/交点、台阶和覆盖，缺面提示定位到具体表面；不得用灰色0表示未测。钢网厚度与PG-021膜层厚度只复用027/029/030配对能力，两工艺各有材料/界面/方向资格，不共享一套薄层事实或默认值。
