# Blocked aperture

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-042`
- 类型：`Function Implementation Specification`
- 版本：`1.3.1-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-DOM-054B`
- 领域：`Stencil`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

检测堵孔/残留污染候选并保留证据。

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

验证同钢网/子开口/版次/阶段、独立定位、期望通光D及批准排除、成像/分类方法资格与有效支撑。D必须在采集/分割前冻结，逻辑D内未采或未处理区域保留未知。制造开口、合格清洁参考与PCB焊盘不同用途，不以焊盘直接替代缩口/分割后的钢网开口。

必须在执行前阻断：缺失必需输入、版本/hash 不匹配、作用域不一致、单位/坐标不一致、资格失效、能力不支持、输入质量低于该方法的最小条件。

## 4. 正常执行流程

1. 按独立设计/参考和定位绑定预期通光D，不要求先从脏孔透光碎片强配出完整孔轮廓。
2. 公共025在实际支撑上分割；按批准方法将其响应解释为O透光、B已证光学遮光或U未知，未处理域一并进入U。
3. 按§28固定分母计算遮光下/上界与分类覆盖；有效域比例只作诊断。原候选与形态处理分别保留。
4. 对有相应证据者独立形成污染/残留候选；光学阻断与材料类别分开，2D路线不强制要求高度图。
5. 交原规则/复判链；Unknown与阈值可判定性分列，维护建议及清洗动作不属于本算法写权。

## 5. 算法/规则设计

**实施分类：** `Stencil Defect Candidate`

**Primary route：** `height/surface/region candidate`

**Fallback route：** `2D/height/surface candidate according to defect class`

**Fallback trigger：** Ambiguity routes to Review; no automatic clean result.

**Reject / Block conditions：** Missing aperture reference or classification support, invalid required modality, unresolved score meaning; low defect score alone is not invalid input.

**参数键（名称冻结，数值由批准 Profile / Recipe / Qualification 提供）：** `['BlockedApertureMethodId', 'MinBlockedScore', 'ReviewScoreBand']`

**结果语义：** `Candidate + evidence`

旧`MinBlockedScore`/`ReviewScoreBand`仅在已明确评分对象和语义的候选方法中使用，不作为物理面积阈值或必需的二值像素分类门。低缺陷分数、低分类置信和缺证据不同；高度mask失效只限制实际需要高度的路线。

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| 残留薄层 | 注入/回放 残留薄层 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 噪声 | 注入/回放 噪声 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 不完全堵塞 | 注入/回放 不完全堵塞 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |

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
| PerformanceProfile | `PF-FS-042` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
3. DEV-DOM-054B
4. FS-042 本文
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
| Function | `FS-042` / `Blocked aperture` |
| Domain | `Stencil` |
| Guide | `DEV-DOM-054B` |
| Input | `Stencil CAD + 2D/3D evidence` |
| Output | `Stencil facts/advice` |
| Result semantic | `Domain InspectionFact / MeasurementSet / ReviewCandidate` |
| Canonical port | `IBlockedAperture` |
| Project | `Asun.Domain.Stencil` |
| UI PageContract | `UI-PCS-017` |
| Primary Work Package | `WP-17` |
| Algorithm baseline | `height/surface/region candidate` |
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
| Primary | `height/surface/region candidate` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `2D/height/surface candidate according to defect class` | Ambiguity routes to Review; no automatic clean result. |
| Reject / Block | `Missing aperture reference or classification support, invalid required modality, unresolved score meaning; low defect score alone is not invalid input.` | 保留证据与原因；不得生成权威 OK。 |

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
- `残留薄层`
- `噪声`
- `不完全堵塞`

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
  → Blocked aperture computation
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
| Port/interface | `IBlockedAperture` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `BlockedAperture.cs` | Pipeline/algorithm implementation |
| Validator | `BlockedApertureValidator.cs` | Input/precondition/quality checks |
| Tests | `BlockedApertureTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-042/` | fixed datasets, expected outputs, provenance |
| Benchmark | `BlockedApertureBenchmark.cs` | P50/P95/P99/resource evidence |
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
| T42-01 | contract/schema validation | expected assertion + evidence + trace; no silent pass |
| T42-02 | normal + boundary + reject | expected assertion + evidence + trace; no silent pass |
| T42-03 | replay/golden dataset | expected assertion + evidence + trace; no silent pass |
| T42-04 | fault injection | expected assertion + evidence + trace; no silent pass |
| T42-05 | performance benchmark | expected assertion + evidence + trace; no silent pass |
| T42-06 | real domain consumer | expected assertion + evidence + trace; no silent pass |
| T42-07 | hard-negative/false-positive set | expected assertion + evidence + trace; no silent pass |

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
| Function | `FS-042` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-DOM-054B` | 指导文档是实施语义权威。 |
| Project | `Asun.Domain.Stencil` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `IBlockedAperture` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-017` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `height/surface/region candidate` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
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
| Function class | `Stencil Defect Candidate` |
| Primary algorithm/route | `height/surface/region candidate` |
| Fallback | `2D/height/surface candidate according to defect class` |
| Fallback trigger | Ambiguity routes to Review; no automatic clean result. |
| Reject/Block | Missing aperture reference or classification support, invalid required modality, unresolved score meaning; low defect score alone is not invalid input. |
| Parameter authority | `['BlockedApertureMethodId', 'MinBlockedScore', 'ReviewScoreBand']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | Candidate + evidence + input snapshot + algorithm/parameter version + quality-gate outcome |
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

<a id="stencil-blockage-bounds"></a>
## 28. 固定期望域的透光、遮光、未知与阻断界

本节保留原`IBlockedAperture`、项目和Owner；D/O/B/U及区间是待原C-02/03/04/07采纳的语义，不创建新DTO、Store或枚举。[025三态/支撑/组件](../../../shared-modules/guidance/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md#segmentation-support-components)为唯一分割Core；面积/量纲交030，候选/区间交039，证据交040。

### 28.1 物理解释及固定分母

D是每一设计子开口的**本方法期望通光域**，来自已批准、同角色可比的制造/清洁参考和独立全局定位。它与FS-039所区分的上/下口、实际透射投影必须角色一致。批准边界保护带或非孔结构排除有独立来源并在观察前冻结；当前暗斑、疑似污染或缺图不得用于缩D。映射不确定的边界带可以成为U，不能运行中从D删除。

在同一父图/物理面积定义下，O为已确认通光、B为有资格的光学遮光、`U=D−(O∪B)`，O∩B=∅，O/B均属于D。工作域W用于halo/计算，若W只处理D的一部分，剩余D也属于U；不能只在W内做补集。原无效、未采、未处理、分类灰区/多解释、饱和、照明漂移和夹具遮挡分别保留原因。可分类域`V=O∪B`，不把“有像素”当“分类有效”。

透光/遮光分类须先证明光源工作、曝光/位深/通道、参考与当前几何、允许反射/散射条件及所需支持；高亮饱和不必然是正常透光，暗像素不必然是物体。优先固定阈值/合格参考比较，HALCON局部阈值可用于响应候选但其高通非响应不能自动成为B。形态close只能产生派生辅助域，不能填U、改变原O/B或用闭合后的“孔通了”覆盖原遮光。

B证明该方法下射线未通，不自动证明锡膏/油污/异物。未加工孔、设计缩口/锥度不匹配、真实孔位偏差和残留可能产生相同差区；类别缺证据时报告“光学阻断候选/原因未定”。材料类别需独立反射/3D/复核资格，AI分割只在获批用途内给候选及拒识，不能提升为已证材料或自动调整D。清洗前后比较不是材料成分证明。

### 28.2 可判定的面积区间

令A(D)>0，面积来自同一合格映射，定义：

- 固定分母遮光下界`β_lo=A(B)/A(D)`，上界`β_hi=[A(B)+A(U)]/A(D)`；未知可全通或全遮，但不能写成已测值。
- 分类覆盖`c=A(O∪B)/A(D)`，未知比例`u=A(U)/A(D)`。
- 仅供诊断的已分类域遮光比`β_observed=A(B)/A(O∪B)`；分母为0时无值，不填0%。

若批准规则为“遮光比例≤τ”，可以给出该**单项数学阈值**的结论：β_hi≤τ则在此不确定区间下满足；β_lo>τ则确定超限；其余不能判定。等号不能互换。039仍独立执行必检完整性/资格/其它缺陷规则；区间满足某阈值不消除U、更不自动放行整网。规则若要求完整观察，仍受该要求约束。零D属于请求无效/明确不适用的前置问题，全未知D产生[0,1]及覆盖0，不是零堵塞。

这些界是在既定O/B证据可信和面积定义下的保守集合界，不是统计置信区间，也不自动包含标定、边界定位和材料分类误差。需要计量接受时由030/Qualification补相应不确定度；不能把显示小数或任意epsilon当资格。Region数组执行集合运算时需按精确子开口逐项关联；HALCON intersection会合并其第二数组，不能把两个等长数组直接当逐项配对而使相邻孔互串。

空区域策略也必须保持目标映射：官方说明结果数量可能少于第一输入数组，不能按输出下标重建孔ID。公共适配按显式目标清单逐项执行/收回，或使用已验证的保空映射；不得临时改全局系统参数影响并行任务。一次成功执行得到的合法空交集、目标未处理、取消以及调用失败分别返回；只有第一种可按本方法解释为空区域，后三种仍保留相应未知/缺口，不能因少一项就左移下一孔结果。

### 28.3 前后变化与保持原事实

只有钢网/子孔/修订、参考D、面别/张紧、方法/光学与坐标可比时才生成变化。两次各有独立观察/尝试/结果，保持完整D及各自O/B/U。共同已分类域`E=(O_pre∪B_pre)∩(O_post∪B_post)`可比较具体通/遮变化，并报告A(E)/A(D)；E不足时只说该可比域的变化，不能推整孔洁净。不同钢网、换版或无法对齐D不得相减。

如需要整个固定D的**界限变化**，可由两次区间派生`改善量∈[β_lo_pre−β_hi_post, β_hi_pre−β_lo_post]`，正值表示遮光减少。区间跨0即不能证明整孔改善；它与E内精确变化是两种投影，不能混成一个百分比。即使改善下界>0，也只证明遮光减少而非清洗动作发生或清洗后合格；维护/清洗事实与权限沿原FS-043，不在此创建执行链。

### 28.4 反例、恢复与性能

| 固定输入 | 必须返回 |
|---|---|
| D=.080mm²，O=.056、B=.016、U=.008 | 遮光界[20%,30%]、分类覆盖90%、诊断已分类域比22.222…%；三个数不能替换 |
| 上例τ=.30/.20/.19，规则≤τ | 分别：该单项区间满足/不能判定/确定超限；完整性仍独立 |
| D100像素，只处理10像素且全通 | O10/B0/U90，界[0%,90%]；不能因处理域全通就报整孔0% |
| 全暗但光源故障 | 全U而非全B；全暗且通光/遮光方法资格充分才可输出B=D，材料原因仍可能不明 |
| 前界[.2,.3]、后界[.1,.2] | 改善界[0,.2]，不能证明严格改善；前后相同D且全分类时才可退化为精确差值 |
| 一父4子、只测其中3子或当前图裁掉脏孔 | 保留第4子/被裁域义务及未知；不能靠重计分母达到全检 |

性能负载固定目标数/D总面积、halo、跨tile组件、候选密度、原/派生mask及证据；先共享025分类再按目标裁取，不能每个重叠ROI重算全图或向UI复制所有Region。区域/候选预算超限保留U和未完成证据，不抽前N项当全部。取消不归还尚在native使用的租约，结果按输入/方法/计算代隔离；新预览不删除旧事实，原提交Unknown先查原ID。钢网与PG-006/021共用025的F/B/U机制，各产品独立解释透射、阻焊或涂层，不能在公共输出塞“堵孔”字段。
