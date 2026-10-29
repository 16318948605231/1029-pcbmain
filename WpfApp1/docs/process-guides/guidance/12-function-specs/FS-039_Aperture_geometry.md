# Aperture geometry

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-039`
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

检查钢网 aperture 开口的几何与名义设计关系。

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

验证钢网/版次/面别/张网状态、原设计开口及父子来源、坐标/单位、基准、成像角色/量测平面、有效支持与所需能力；制造参考使用已批准适用的ManufacturingGeometrySnapshot。光学透射投影与指定金属表面开口必须分别定义，不把一个Ready标签当作两者可比的证明。

必须在执行前阻断：缺失必需输入、版本/hash 不匹配、作用域不一致、单位/坐标不一致、资格失效、能力不支持、输入质量低于该方法的最小条件。

## 4. 正常执行流程

1. 冻结设计子开口全集、观测角色、独立全局位姿与搜索域。
2. 通过025/021提取并去重真实观察，先形成带原始支持/残差的方法几何。
3. PG构造固定费用与物理排他图，062求一对一映射及替代证明；几何改变重建受影响图，不以关联后的重拟合反证旧映射。
4. 030按§28计算指定轴向尺寸、真实观察面积和模型量；原轮廓缺口/未知单列。厚度/壁面分别交FS-040/041，其缺口不取消合格2D量。
5. 返回关联/几何/支持与证据，交原评价及提交Owner；本FS不直接发布生产事实。

## 5. 算法/规则设计

**实施分类：** `Stencil Metrology`

**Primary route：** `2D contour + 3D surface`

此历史路线名表示按被测量装配适用模态；2D投影几何不强制要求3D，3D厚度/壁面也不能被2D替代。具体执行语义唯一见§28，不改变原`IApertureGeometry`、项目或Owner。

**Fallback route：** `2D contour for 2D classes; 3D surface route when thickness/wall is required`

**Fallback trigger：** 2D fallback is forbidden when the requested measurement requires 3D evidence.

**Reject / Block conditions：** Missing aperture binding, contour ambiguity, invalid 3D surface when 3D required.

**参数键（名称冻结，数值由批准 Profile / Recipe / Qualification 提供）：** `['ApertureGeometryClass', 'RequiredModality', 'MaxContourResidual']`

**结果语义：** `Aperture geometry + modality evidence`

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| 细小开口 | 注入/回放 细小开口 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 污染 | 注入/回放 污染 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 反光 | 注入/回放 反光 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 变形 | 注入/回放 变形 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |

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
| PerformanceProfile | `PF-FS-039` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
4. FS-039 本文
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
| Function | `FS-039` / `Aperture geometry` |
| Domain | `Stencil` |
| Guide | `DEV-DOM-054A` |
| Input | `Stencil CAD + 2D/3D evidence` |
| Output | `Stencil facts/advice` |
| Result semantic | `Domain InspectionFact / MeasurementSet / ReviewCandidate` |
| Canonical port | `IApertureGeometry` |
| Project | `Asun.Domain.Stencil` |
| UI PageContract | `UI-PCS-017` |
| Primary Work Package | `WP-17` |
| Algorithm baseline | `2D contour + 3D surface` |
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
| Primary | `2D contour + 3D surface` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `2D contour for 2D classes; 3D surface route when thickness/wall is required` | 2D fallback is forbidden when the requested measurement requires 3D evidence. |
| Reject / Block | `Missing aperture binding, contour ambiguity, invalid 3D surface when 3D required.` | 保留证据与原因；不得生成权威 OK。 |

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
- `细小开口`
- `污染`
- `反光`
- `变形`

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
  → Aperture geometry computation
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
| Port/interface | `IApertureGeometry` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `ApertureGeometry.cs` | Pipeline/algorithm implementation |
| Validator | `ApertureGeometryValidator.cs` | Input/precondition/quality checks |
| Tests | `ApertureGeometryTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-039/` | fixed datasets, expected outputs, provenance |
| Benchmark | `ApertureGeometryBenchmark.cs` | P50/P95/P99/resource evidence |
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
| T39-01 | contract/schema validation | expected assertion + evidence + trace; no silent pass |
| T39-02 | normal + boundary + reject | expected assertion + evidence + trace; no silent pass |
| T39-03 | replay/golden dataset | expected assertion + evidence + trace; no silent pass |
| T39-04 | fault injection | expected assertion + evidence + trace; no silent pass |
| T39-05 | performance benchmark | expected assertion + evidence + trace; no silent pass |
| T39-06 | real domain consumer | expected assertion + evidence + trace; no silent pass |
| T39-07 | hard-negative/false-positive set | expected assertion + evidence + trace; no silent pass |

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
| Function | `FS-039` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-DOM-054A` | 指导文档是实施语义权威。 |
| Project | `Asun.Domain.Stencil` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `IApertureGeometry` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-017` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `2D contour + 3D surface` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
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
| Primary algorithm/route | `2D contour + 3D surface` |
| Fallback | `2D contour for 2D classes; 3D surface route when thickness/wall is required` |
| Fallback trigger | 2D fallback is forbidden when the requested measurement requires 3D evidence. |
| Reject/Block | Missing aperture binding, contour ambiguity, invalid 3D surface when 3D required. |
| Parameter authority | `['ApertureGeometryClass', 'RequiredModality', 'MaxContourResidual']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | Aperture geometry + modality evidence + input snapshot + algorithm/parameter version + quality-gate outcome |
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

<a id="stencil-aperture-method"></a>
## 28. 开口观察、关联与几何的专项实施语义

本节为待原C-02/03/04/07采纳的详细语义，保留原端口/项目/Owner及DocMapped准备状态。算法Core分别复用[021](../../../shared-modules/packages/PKG-021_Features2D.md)、[025](../../../shared-modules/packages/PKG-025_Segmentation.md)、[030](../../../shared-modules/packages/PKG-030_Metrology.md)、[062](../../../shared-modules/packages/PKG-062_Assignment.md#assignment-implementation)，PG-013只负责钢网物理来源、建图和解释，不新建钢网拟合/分配核心。

### 28.1 先说明量到的是什么

透射图O描述具备成像资格时的**可透光射线投影**。对于不透明钢网、合格近法向平行光/远心成像和无散射模型，射线须穿过沿深度全部孔腔，因此投影受最窄部、斜壁、残留和视角共同限制；一般透射轮廓不等于上表面或下表面的金属边界。锥孔上口宽.30mm、下口宽.20mm，即使同轴无污染，透射宽仍可为.20mm。不得报告“上口实测.20”或据差额认定上口堵塞。

方法资产须声明透射投影、指定表面金属边界或指定剖面几何之一，并绑定成像角色、基准平面、允许材料/厚度/壁型、光学与标定适用域。2D切割资料若只描述某表面，不能直接成为不同投影角色的真值；需批准的可比性或投影参考。非远心成像的深度放大率不由显示比例修正。没有相应资格时，只返回观察投影/差异候选，不改名实体上口、下口或侧壁。

### 28.2 无循环的候选—几何—关联链

1. **设计全集。** 制造来源先展开稳定父→子开口关系，每个实际设计开口叶子是一个目标。一个PCB焊盘对应四个钢网子开口时，父焊盘用于导航，四个子ID各有几何/公差；不能同时把父项和子项计入四孔覆盖分母。来源重叠/重复子ID或关系不明先拒绝，不能按连通域数反造设计。
2. **独立定位。** 由批准Mark/夹具基准固定坐标变换，保留支撑/残差。待检开口不得用于自由缩放/局部变形把真实孔位误差拟合掉；全局位姿不明时回原022定位问题，不能将未知位姿的联合优化伪装成062固定费用分配。
3. **完整观察。** 在批准搜索域及halo上调用025/021，保留原透射域、原轮廓、坏支持、原图索引和实际分辨率。跨tile先完成来源合并与物理去重；拼图插值不增加独立证据。多个FOV、不同方法或一个开口的多段亮碎片不能直接成为多个可独占“实体开口”。碎片可能由堵塞造成：无法证明物理组合时只作观察片段，F01对应保持未决，F02仍可按独立设计定位的D求三态，不反过来强造F01映射。
4. **先形成几何。** 对每一可识别物理观察，执行预先批准的有限孔型/方法候选，保存原轮廓与每个方法的几何、资格、残差和被剔点。圆拟合、矩形边/圆角或异形原轮廓是不同描述，不能先凭尚未确定的目标身份选一个模型，再以该模型结果证明身份。需要目标类别选择方法时，按冻结的目标类→方法政策生成边证据；右顶点仍是同一物理观察，不为每个方法复制右顶点。
5. **建图。** 左为设计子开口，右为合格物理观察；每个合法边绑定确切方法几何与源版本。关联搜索门与尺寸/位置接受公差分开；窄到只容PASS的门会把超差孔隐藏成缺孔。首批费用可采用冻结全局基准上的归一化中心距离平方；轴向形状项仅在方法可比且有明确权重/尺度时纳入。费用有限非负，δ来源明确，不能按画面排序或“最佳分差”取代全局消歧。失败几何保留原观察诊断，不默默从搜索完整性证据删去。
6. **062求解/绑定。** 同一完整图按最大匹配数、最小费用及近等价证明执行。任何替代带内映射使整个相关分量未决；截断或消歧未完成不给唯一对应。配对后评价必须引用建图时那份几何；若新拟合改变中心/方法/费用，重建受影响图及证明，旧对应只作历史。
7. **缺/多开解释。** 未配对设计保留必检义务；无透射可能为未加工、全堵或失效观察，不能仅凭K不足下“缺加工孔”结论。未配对观察仅在完整额外开口搜索、独立定位、观察资格和去重已完成时形成多开候选。062的图结论不授予物理类别。

### 28.3 明确尺寸，保留缺陷边

真实观察区域面积、边界模型面积和设计面积分别命名。前者由有效原区域/闭合原轮廓按同一物理映射求；有未知边界时不能补线封孔后声称真实面积。像素计数×像素面积和亚像素闭合轮廓积分是两个采样模型，方法/误差须固定，不能混用分子分母。简单多边形积分/Region面积经030及AsunImage既有公共能力；复杂自交/多环/方向/孔洞须原几何资格，不自行猜测封闭规则。

对于设计已冻结单位轴u/v，投影跨度为`max(p·u)−min(p·u)`及v同式；它是具名Feret跨度，**不是**局部最窄槽宽。槽宽另在批准站位上取相对两真实边交点，交点多值/缺侧/穿未知时该站无值，有限站位最小不冒称连续全域最小。圆形模型报告2r、中心和原边径向残差；等效圆径`2sqrt(A/π)`是面积派生，不能替代矩形长宽。模型拟合把毛刺降权/删点只为估计模型，原毛刺必须进入独立缺陷候选；MaxContourResidual必须区分拟合适用门与工艺轮廓偏差接受值，不能共用未定义阈值消除真实缺陷。

中心定义明确为面积质心、模型中心或其它方法，三者不混合；方向按形状对称性解释。圆无可辨方向，正方形轴向有90°等价，长矩形长轴有180°等价；近对称的方向不稳定时输出无值/等价类，不能以数值噪声“旋转90°”判错。比较前保持设计全局frame；另做局部形状对齐时保留原全局Δx/Δy和变换，局部一致不抵消位置偏差。

矩形方法先分出各条实际直边及圆角段，再由021分别拟合；原边有足够跨度且相对边/邻边符合该模型适用门，才生成矩形模型量。不能将四边/圆角一次送直线拟合；拟合返回线段端点只是原首末点向拟合线投影，不自动是矩形真实角点。直线延长求交得到的圆角“尖角”只属于模型，不加入原轮廓。相对边不平行时，按冻结站位分别求宽，不能以无名“平均线距”掩盖楔形；是否能接受形状偏差交产品规则。

### 28.4 有限反例与恢复

| 输入/故障 | 必须输出 |
|---|---|
| .2×.4mm完整矩形 | 面积.08mm²；指定轴宽长.2/.4；等效圆径约.31915mm仅作派生，不能替代长宽 |
| 同面积异形L域与矩形 | 面积相同不代表形状一致；原轮廓差异保留 |
| 费用边a→x=0、a→y=4、b→x=3 | 复用062得两配对a→y/b→x；不能最近邻贪心只配一个 |
| 父焊盘含4子开口，仅3子有可用结果 | 子目标覆盖3/4；父节点不增加分子/分母；第4子保持未知/待解释 |
| 圆孔原边有毛刺，但拟合圆残差门因剔点通过 | 模型直径可有效，原毛刺证据仍在；不能判“原边完整正常” |
| 坐标/几何方法修订晚到或跨FOV候选未齐 | 旧图不能绑定新几何，未齐分量不报唯一/缺孔；保留原输入和计算引用 |

图像、轮廓点、方法数、候选/边数、062完整消歧、原/派生证据均计入同一预算；不只测单孔拟合。纯计算取消等native及062排空再归还租约，重算有新CalculationIdentity；保存Unknown沿原CommitIdentity查询。页面只呈现原/模型/设计、关联见证及各量值资格。共享双消费者验证由PG-002钻孔与PG-013分别提供领域输入调用同一021/030/062，既有PG-003消费者保留；不复制其孔型/层语义到钢网。


<a id="stencil-aperture-edge-binding"></a>
### 28.5 边证据入口与物理拟合的专项绑定

§4及§28.2–28.3使用[025 §7唯一方法](../../../shared-modules/guidance/03-vision/DEV-VIS-025_2D边缘、轮廓与几何特征开发指导.md#edges2d-association-method)，沿原IApertureGeometry、代码根、T39-01～T39-07及合同候选，不新设钢网提边接口或状态。这里的完整观察指已批准搜索/来源/支撑具有相应完成证据，不能由某个native返回非空或达到num_instances推定。

将固定角色的原连续边/卡尺slot作为输入，保留断点和多个候选；透射可见边不冒清洁表面外边。纯pair仅有实际完整边对，空pair不确定单边位置/极性或物理缺失原因；需要单边时按冻结方法登记独立证据入口。若全profile含无效贡献则先拒绝该slot，不用reduce_domain或补0解除污染。Metrology无测区—找边点映射，不能构造虚假slot列表或按任意实例顺序认目标。

用于建图和尺寸的物理几何顺序为：原实际支撑点→007合格映射→目标空间primitive/连续性/分布资格→021拟合与全原点残差→冻结候选几何→PG固定图/062→030按具名定义量测。像素诊断可另存，但不能把像素端点/圆心变换后冒此物理链。多方法共享同一物理观察，换几何须重建受影响图；正式绑定时以原T39-01/02覆盖合同与失败语义，T39-03/06覆盖此链的Golden及真实消费者，不以本段另建平行FS或代码项目。

在原Golden追加可判定挑战：完整profile下无边/仅正/仅负均可能没有pair，应保留无法区分；只有已登记并真实完成的单边调用才提供其独立证据。非等距圆、缺角矩形、污染双边、乱序多实例、实例上限及缺端部各验证上游资格/完整性，不能仅比较最终尺寸。F02固定D三态仍是独立消费，F01失败不使其可用输入失效；本段不改变FS040/041/043职责或维护/设备命令。
