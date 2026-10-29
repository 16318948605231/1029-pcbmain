# Maintenance advice

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-043`
- 类型：`Function Implementation Specification`
- 版本：`1.3.0-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-DOM-054B`
- 领域：`Stencil`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

根据已提交的堵孔/污染/变形事实和趋势给出维护建议，建议不等于维护执行。

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

验证输入作用域、单位/坐标、版本、质量元数据和所需能力；对制造参考任务优先使用 Ready 的 ManufacturingGeometrySnapshot。

必须在执行前阻断：缺失必需输入、版本/hash 不匹配、作用域不一致、单位/坐标不一致、资格失效、能力不支持、输入质量低于该方法的最小条件。

## 4. 正常执行流程

1. 固定已提交事实/规则/维护上下文，按§28将单次现状、前后比较和历史趋势分支分别评价。
2. 检查数据充分性。
3. 生成建议及触发依据。
4. 输出建议等级与证据引用。
5. 原应用Owner接受提案；人工批准、实际维护事件、复检及质量处置分别记录，按§28执行，批准不等于设备动作。

## 5. 算法/规则设计

**实施分类：** `Stencil Quality Advice`

**Primary route：** `trend + rule-based evidence`

**Fallback route：** `No recommendation when evidence is insufficient`

**Fallback trigger：** Evidence sufficiency is evaluated per approved rule branch (§28); a trend rule cannot use missing history, while an independently qualified single-observation rule does not require unrelated history.

**Reject / Block conditions：** Missing prerequisites for the selected rule branch; incomparable observations; incomplete required maintenance context (§28).

**参数键（名称冻结，数值由批准 Profile / Recipe / Qualification 提供）：** `['TrendWindow', 'MinObservationCount', 'AdviceRuleSetId']`

**结果语义：** `Advice proposal + evidence`

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| 数据不足 | 注入/回放 数据不足 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 迟到数据 | 注入/回放 迟到数据 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 跨批次分母混用 | 注入/回放 跨批次分母混用 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |

## 7. 质量门与拒识策略

至少建立三层 Gate：

1. **InputQualityGate**：输入是否可处理；
2. **AlgorithmQualityGate**：算法结果是否足够可靠；
3. **BusinessApplicabilityGate**：方法是否适用于当前产品/特征/尺度/材料/工艺。

任何 Gate 失败都要保留原因、证据引用和状态。`Unknown/Invalid/NotApplicable` 不允许被强制转换成 `OK`。

## 8. 性能与资源

本功能不重算图像。按§28.5绑定目标/周期/事实/规则和查询字节负载，分别测042读取、045统计、规则解释、原提案保存及UI投影；具体接受值由批准PerformanceProfile给出。

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
| PerformanceProfile | `PF-FS-043` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
4. FS-043 本文
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
| Function | `FS-043` / `Maintenance advice` |
| Domain | `Stencil` |
| Guide | `DEV-DOM-054B` |
| Input | `Stencil CAD + 2D/3D evidence` |
| Output | `Stencil facts/advice` |
| Result semantic | `Domain InspectionFact / MeasurementSet / ReviewCandidate` |
| Canonical port | `IMaintenanceAdvice` |
| Project | `Asun.Domain.Stencil` |
| UI PageContract | `UI-PCS-017` |
| Primary Work Package | `WP-17` |
| Algorithm baseline | `trend + rule-based evidence` |
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
| Primary | `trend + rule-based evidence` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `No recommendation when evidence is insufficient` | Evidence sufficiency is evaluated per approved rule branch (§28); a trend rule cannot use missing history, while an independently qualified single-observation rule does not require unrelated history. |
| Reject / Block | `Missing prerequisites for the selected rule branch; incomparable observations; incomplete required maintenance context (§28).` | 保留证据与原因；不得生成权威 OK。 |

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
- `数据不足`
- `迟到数据`
- `跨批次分母混用`

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
  → Maintenance advice computation
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
| Port/interface | `IMaintenanceAdvice` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `MaintenanceAdvice.cs` | Pipeline/algorithm implementation |
| Validator | `MaintenanceAdviceValidator.cs` | Input/precondition/quality checks |
| Tests | `MaintenanceAdviceTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-043/` | fixed datasets, expected outputs, provenance |
| Benchmark | `MaintenanceAdviceBenchmark.cs` | P50/P95/P99/resource evidence |
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
| T43-01 | contract/schema validation | expected assertion + evidence + trace; no silent pass |
| T43-02 | normal + boundary + reject | expected assertion + evidence + trace; no silent pass |
| T43-03 | replay/golden dataset | expected assertion + evidence + trace; no silent pass |
| T43-04 | fault injection | expected assertion + evidence + trace; no silent pass |
| T43-05 | performance benchmark | expected assertion + evidence + trace; no silent pass |
| T43-06 | real domain consumer | expected assertion + evidence + trace; no silent pass |
| T43-07 | hard-negative/false-positive set | expected assertion + evidence + trace; no silent pass |

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
| Function | `FS-043` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-DOM-054B` | 指导文档是实施语义权威。 |
| Project | `Asun.Domain.Stencil` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `IMaintenanceAdvice` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-017` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `trend + rule-based evidence` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
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
| Function class | `Stencil Quality Advice` |
| Primary algorithm/route | `trend + rule-based evidence` |
| Fallback | `No recommendation when evidence is insufficient` |
| Fallback trigger | Evidence sufficiency is evaluated per approved rule branch (§28); a trend rule cannot use missing history, while an independently qualified single-observation rule does not require unrelated history. |
| Reject/Block | Missing prerequisites for the selected rule branch; incomparable observations; incomplete required maintenance context (§28). |
| Parameter authority | `['TrendWindow', 'MinObservationCount', 'AdviceRuleSetId']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | Advice proposal + evidence + input snapshot + algorithm/parameter version + quality-gate outcome |
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


<a id="stencil-maintenance-comparison"></a>
## 28. 清洗比较与维护建议的实施闭环

本节是 FS-043 的唯一实施细节；光学三态与几何定义仍来自 [PG-013](../../processes/PG-013_stencil.md)、[FS-042](FS-042_Blocked_aperture.md)，统计方法来自 [045/058A](<../../../shared-modules/guidance/06-domains/DEV-DOM-058A_QualityControl SPC与分母定义开发指导.md#spc-core>)。本功能消费已提交事实及其当前适用性，不重新分割图像、不自建统计引擎、不写设备动作。原 `IMaintenanceAdvice` 端口和登记的输入/输出名称保留；其中 `Stencil CAD + 2D/3D evidence` 表示可追溯的来源上下文，**不是允许本功能绕过已提交量测自行产生生产判定**。精确快照、规则适用性和提案字段继续由原 C-01～08 串行采纳。

### 28.1 冻结输入与逐规则前提

调用方必须绑定钢网实体/修订、开口稳定身份及制造父子关系、检查阶段、选定尝试与原事实/证据回执、清洗事件（若声称清洗前后）、张紧/装夹/面别、参考修订、单位/被测量、标定/方法/能力资格、查询截点/完整性、规则版本及当前使用权限。相同文件 hash、条码相同、时间相邻均不能补出物理身份或清洗事件。只做单次现状规则时不强制无关的历史和清洗前记录。

先将原 `AdviceRuleSetId` 中每条已批准规则分类为单次现状、前后比较或历史趋势；分类、优先级、冲突处置及适用阶段来自规则本身，不新增固定默认政策。`TrendWindow`、`MinObservationCount` 仍按原批准语义绑定，**历史趋势规则**需要它们；不能用缺历史关闭所有单次规则，也不能临时将趋势规则降级成单次阈值规则。

|规则分支|独立前提|满足后能返回的内容|不足时|
|---|---|---|---|
|单次现状|本次有效已提交事实、适用的单次规则、足够观察资格|带触发证据和规则的维护/复查候选；只见遮光时保留物理原因未确认|该规则不可评价；单次疑似不变成强制清洗|
|清洗前后|明确前后尝试/事件、同目标及可比被测量、两次观察支持和不确定性|具名差值/界、共同可见范围和是否满足该规则；不宣称清洗因果效果|展示两份原事实及不可比原因，禁止相减或出改善结论|
|历史趋势|冻结时间范围及顺序、独立观察/尝试政策、可比过程段、最小有效观察/跨度及统计方法资格|045 返回的统计投影和规则命中依据|历史/资格不足，不用零补缺测或用当前一个坏点伪造斜率|

“未命中规则”“规则不可评价”“提案已生成”“人工批准”“设备执行”“清洗后复检”“质量放行”必须分别投影原合同状态。前两者都不表示钢网合格。相互冲突的已命中规则保留全部依据及原冲突状态；未经批准的优先级不得凭分数最高静默选一个。

### 28.2 清洗前后配对与可比性

1. 固定所选前后事实及明确关系；多次清洗或多次复测由批准 AttemptPolicy 选择，不按查询返回顺序取最后一行。同一次图像重算只改变计算身份，不成为新的清洗周期或独立观察。
2. 核对实体、开口/父子关系、检查面、修订和参考意图；拆孔/合孔不能凭质心邻近强配。身份无可靠映射时仅并排查看。
3. 将张紧/装夹、光照/曝光/模态、标定、采样分辨率、遮光判据、几何坐标及方法变更逐项与批准可比条件比对。修订不完全相同但有已批准等价证明可以比较；修订相同也不能替代真实资格。禁止局部仿射/缩放消掉应检拉伸或形状变化。
4. 比较域 D 必须来自冻结的制造意图/合法清洁参考及被测量；不能由前后已知域的交集自动替换整孔分母。需要比较空间迁移时，由007和原关联Owner提供合格坐标/映射；配准不确定性进入原方法资格，不能让UI重采样后的像素决定量值。
5. 两次状态分别为 D 上互斥的已知通光 T、已知非通光 B、未知 U，三者覆盖 D。T仅是本文的数学记号，等于FS-042的O，不创建另一套字段或分类。这里只对**光学非通光占比**作确定性界；若缺少把非通光归因为残留/堵塞的资格，不将该界改名为“真实污染率”。传感/标定误差还须独立计入量测不确定度，集合未知界不是统计置信区间。

令 A=area(D)>0，时点 j 的下界 L_j=area(B_j)/A，上界 H_j=area(B_j∪U_j)/A；未知率单列。改善量定义为“前减后” Δ=q_before−q_after，故 **Δ∈[L_before−H_after, H_before−L_after]**，单位为比例或百分点。下界严格大于0才证明在该光学定义及未知模型下必然减少；包含0只能说无法证明严格减少；上界小于0才证明必然增加。是否足够维护验收仍由批准门限和不确定度处理决定，不把严格正值当通用工艺放行门。

同时提供共同已知域 K=(T_before∪B_before)∩(T_after∪B_after)：消失差区 B_before∩T_after、新增差区 T_before∩B_after、保留非通光 B_before∩B_after、两次通光 T_before∩T_after 四者分割 K。输出各自原几何/面积及 area(K)/A；这是证据解释，不是把 K 当整孔。K 外的未知不被淡出或算“已清净”。若空间映射不合格，可以保留各自整孔汇总，但不可画迁移差区或称逐点改善。

**可复算反例：** D=1 mm²；前 B=.20、T=.70、U=.10，后 B=.10、T=.50、U=.40。仅看已知域会从 .20/.90≈22.22% 降至 .10/.60≈16.67%，但整孔非通光界分别为[20%,30%]和[10%,50%]，Δ为[-30,+20]个百分点，不能宣称改善。另一例前[20%,30%]、后[5%,20%]只给[0,+25]个百分点，零端点仍不证明严格改善。例值仅供语义验算，不是默认生产阈值。

A=0、单位/域错配、数值非有限、集合重叠或未覆盖D均返回输入无效；缺后次结果不是后值0。前后不同目标集合仅可按已批准目标映射比较可比子集，且显式显示原全集/未配对项；不能用交集指标冒充全钢网改善。

### 28.3 趋势、统计与提案生成顺序

1. 042按已批准范围和权限提供有界固定读取及完整性，解析重复/更正/撤回和指定尝试政策。事实修订不可按到达时间覆盖，缺查询页不能当历史读完。
2. 工艺提供观察单位：同网同孔多个FOV不是多次清洗周期，数千孔也不是数千独立钢网。按同被测量/参考、张紧/装夹、方法和资格等构成批准的可比过程段；各段分开，UI筛选不改原分母。
3. 必检/有效/未知/缺测与未读取计数分开交给045；趋势的有效点数不代表总体完整。`MinObservationCount`按批准观察单位计数，并满足所选方法的时间跨度与独立性要求；无要求来源就不声称方法合格。不要对未知上下界擅取中点回归。
4. 045执行已批准统计方法，返回输入成员、方法/基线、量值、方法资格和缺口；FS-043只做规则解释。斜率、控制图报警、过程能力及维护寿命是不同结论；没有寿命模型/失效定义/右删失及独立验证时不输出“还可使用N次”。
5. 逐规则求命中、未命中或不可评价及证据；先按原作用域合并重复触发，再按已批准冲突政策返回建议集合。规则变更产生新的建议计算，不回写量测或已批准历史提案；同一坏孔不因页面刷新产生多条重复提案。
6. 生成只读预览，显示对象/来源/截至时间、规则、原因、支持/缺口、候选操作及适用条件。有权人员通过原 `CreateMaintenanceProposal` 应用意图提交；原Owner在接受边界复核当前资格/权限及引用，不能以页面按钮曾经可用代替服务端复核。

统计群体层的前后效果分析需要保留成对实体/周期及更高层聚类。固定SciPy的paired实现和测试表明同组索引共同重采样，但不能据此把孔/FOV当独立钢网；不直接引入SciPy运行时，也不以退化为零的bootstrap区间声称零风险。来源及限制见[REF-002](../../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#stencil-method-research)。HALCON优先用于上游观察与几何；维护规则/事件配对不属于图像算子功能，不新增私人视觉或统计库。

### 28.4 原操作回执、过时建议与人工动作

只读刷新、重算、新观察、提案提交重试各有不同意图。原提案提交应答丢失后保持同操作身份和内容，先向原Owner查询；查询暂缺/副本落后不证明未提交，不能换键再建一条。新输入或新规则产生关联后继建议，原Unknown仍需查询解决；重算不能把旧Unknown清零。

来源资格撤回、后续清洗/复测或维护上下文变化使提案当前适用性需重验，旧提案与原事实保留。最终接受栅栏、撤回竞态与跨服务读取由原C-04/06/08冻结；本地先查后写不能提供未获证明的原子保证，这仍是内部合同工作。只读历史应标“截至所选快照”，不得因保留可查看就继续给执行建议。

人工批准提案只产生相应批准记录，不能等同执行清洗/换网、设备安全准许或质量放行。真正维护事件由既有有权业务/设备Owner记录；清洗后采集是新物理尝试，复检结果再由原质量Owner按规则处置。拒绝提案不将原缺陷改为PASS，关闭页面不撤销已保存提案。当前范围不新增清洗机SDK或自动设备命令。

### 28.5 性能与可执行验收

无图像重算时，负载单位为钢网/开口/周期/事实/规则数与字节，不能仅沿旧表中的 `ROI/P95` 衡量。冻结每请求事实页、目标数、时间窗、规则数和预算；042有界读取、045分组统计及本功能规则解释分别计时。避免逐孔N+1查询；先固定有界输入闭包再批量查引用。排序/分组超预算应返回不完整原因，不能截掉最早/最差的历史后给出确定建议。缓存需包含实体/范围/原事实修订、被测量/域/规则/方法及当前资格；缓存命中不授予当前写权。取消停止尚未提交计算，真实资源按原038/042/045排空；已保存提案不可回滚。

|挑战|可判定结果|
|---|---|
|单次规则适用，趋势历史为0|单次规则独立评价；趋势不可评价；无强制清洗/合格结论|
|仅有一次“疑似堵孔”，没有批准单次规则|保留候选与缺规则，不生成“必须清洗”|
|前后已知比例22.22%→16.67%，未知域增加|显示整孔Δ=[-30,+20]百分点与未知，不显示改善徽标|
|Δ区间下端为0、全空D、缺后次输入|前者无法证明严格改善；后两者不可计算，不返回0改善|
|清洗前后目标顺序相反、孔ID不变|按原稳定键配对，与行顺序无关|
|同孔十个FOV/同图十次重算|不充十次独立周期；保留真实观察单位|
|不同张紧且无等价资格|原图可并看，趋势/差值受阻；不将其波动归因于磨损|
|一个已命中规则与一个不可评价规则|两者分别显示；不能把部分可评价写成整套规则完成|
|建议提交成功但回执丢失，再发生新清洗|原键查询解决旧回执；旧建议适用性单独重验，新清洗不抹旧记录|
|批准提案后没有维护事件，或维护后没有复检|分别显示尚未执行/尚未复检，不显示可生产或自动放行|
|查询缺页、资格撤销、权限变化、取消排空|保留各自真实状态；不靠无结果/按钮禁用证明没有副作用|

本节仍为DesignReview。公式/合成反例不代替真实光学输入、量测不确定度、清洁度政策、WPF或维护/质量业务合同验收。实现时先冻结原Owner的字段/接受协议，再按原端口接无UI规则计算、042/045/040链，最后接UI017投影，不让页面补做这些决定。
