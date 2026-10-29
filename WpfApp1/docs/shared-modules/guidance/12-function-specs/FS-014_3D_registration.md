# 3D registration

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-014`
- 类型：`Function Implementation Specification`
- 版本：`1.3.0-prep`
- 状态：`DesignReview`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-VIS-028`
- 领域：`Vision`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

双模型/多模型注册到声明坐标，输出最终变换、原生指标及其类型、支撑/双向覆盖、残差、图一致性与位姿可观测性。独立交付归属[PKG-060](../../packages/PKG-060_Registration3D.md)，031负责单表面特征，007只做已知变换。变换候选不自动成为标定或质量事实。

**不负责：** 生产机判、最终处置、真实设备安全功能。

## 2. 权威与契约

输入契约：`ObjectModel3D + rough transforms`；输出契约：`transforms/scores`。若字段尚未在现有 Schema 中冻结，必须登记到对应 ContractCandidate（通常 C-01/C-02/C-03/C-04/C-08），不能在功能目录中另建 JSON/数据库模型。

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

逐Surface绑定源/目标frame、单位/hash、有效性、定位域与独立check域、初值来源、允许自由度及预算。pair ICP需合适初值；global需已知近似关系与连通/锚点约束。非空点集不能证明存在合格法向/primitive/面。被测缺陷域不能被任意自由配准吸收。

必须在执行前阻断：缺失必需输入、版本/hash 不匹配、作用域不一致、单位/坐标不一致、资格失效、能力不支持、输入质量低于该方法的最小条件。

## 4. 正常执行流程

1. 冻结原始源/目标及用途、基准/初值/允许自由度，捕获独立检查支撑。
2. 031按声明采样/法向产生派生支撑；保持源映射和原有效分母。
3. pair的matching或ICP按实际适用条件执行；预变换T0后的增量Δ须组合为从原frame出发的Δ*T0。
4. 检查候选/歧义、双向覆盖、物理限幅、残差与可观测性；无对应/无pose、低残差但秩不足不能通过。
5. global先核连通、锚点、边来源，细化后再次检查全部必需节点与独立check域；不靠每节点有邻居推断连通。
6. 返回变换/实际指标/适用域及证据，不写生产事实。算法、变换方向、质量和反例的唯一细则见[IM-033 §7](../../../independent-modules/registration-3d/DEVELOPMENT-GUIDE.md#7-处理路线与质量门)；DEV-VIS-028仅保留应用导航。

## 5. 算法/规则设计

**实施分类：** `3D Registration`

**Primary route：** `register_object_model_3d_global/pair`

**Fallback route：** `Pairwise/known-transform route`

**Fallback trigger：** Use pairwise or known transform only when the registration graph and task semantics allow it; never use a fallback that hides a global residual failure.

**Reject / Block conditions：** Insufficient overlap, divergent solution, residual above gate, invalid initial transform.

**历史参数摘要（不等于native参数或完整字段冻结；精确映射按正式契约采纳）：** `['MinOverlap', 'MaxRegistrationResidual', 'InitialTransformSource', 'MaxIterations']`

**结果语义：** 候选最终Transform及类型化质量证据。pair Score与global邻居数量分开；不得将两者统一解释为概率或MaxRegistrationResidual。公共覆盖的分母/距离/单位需单独定义。

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| low overlap | 注入/回放 low overlap | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| bad initialization | 注入/回放 bad initialization | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| outlier model | 注入/回放 outlier model | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| disconnected graph | 注入/回放 disconnected graph | 显式质量状态；必要时 Reject/Review，不得静默 PASS |

## 7. 质量门与拒识策略

至少建立三层 Gate：

1. **InputQualityGate**：输入是否可处理；
2. **AlgorithmQualityGate**：算法结果是否足够可靠；
3. **BusinessApplicabilityGate**：方法是否适用于当前产品/特征/尺度/材料/工艺。

任何 Gate 失败都要保留原因、证据引用和状态。`Unknown/Invalid/NotApplicable` 不允许被强制转换成 `OK`。

## 8. 性能与资源

ROI-first；记录 P50/P95/P99、峰值内存、输入尺寸、候选数量和线程/并发条件；避免全图重复计算。

性能采集点必须至少覆盖：输入准备、核心计算、质量评估、序列化/提交（如有）、UI 投影（如有）。高峰资源与长尾单独报告，不以平均耗时掩盖 P99。

## 9. 并发、取消、重试与恢复

本FS是无生产副作用计算，下列提交恢复只适用于调用方既有结果Owner，不要求本包新增数据库/CommitOwner。pair/global官方支持取消超时/中断，但必须通过已确认公共适配传播；.NET CancellationToken不自动证明native已停。退出前工作资源不得释放。

- **Cancel**：取消尚未产生生产副作用的计算；已提交事实不可因 UI cancel 回滚。
- **Calculation Retry**：允许重新计算，生成新的 calculation identity。
- **Commit Retry**：必须复用原 CommitIdentity，并保持幂等。
- **Timeout**：形成明确超时事实/错误，不自动当作失败后的隐形重试。
- **Process Restart**：依赖 Snapshot/Receipt/Session 恢复；禁止读取 `latest` 猜状态。

## 10. 结果与证据

输出必须包含：输入引用、算法/规则版本、参数版本、坐标/单位、质量状态、执行时间、适用域、EvidenceRef；生产事实与 UI/报告投影分离。

## 11. UI / 操作员工作流

UI/工作区：3D transform overlay。交互遵循“状态→对象→结果→下一动作”；任何生产配置修改必须 Draft→Validate→Approve→Release；异常必须一键定位到证据。


关键操作顺序原则：系统自动带出可确定内容；操作员只处理异常、冲突和必要确认；批量动作先预览影响范围；高级参数渐进披露；每个阻断都有“原因+处理动作+证据”。

## 12. 测试设计

| 测试层 | 覆盖内容 | 必须留存 |
|---|---|---|
| Unit | 核心算法/规则、边界输入、单位/坐标、纯函数 | 输入快照、输出、expected/actual |
| Contract | Schema、状态、Owner、版本兼容 | validator report |
| Integration | 真实 consumer、Pipeline、Evidence | trace + receipt |
| Golden/Replay | 正常/边界/难例/拒识 | dataset hash + result diff |
| PerformanceProfile | `PF-FS-014` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
3. DEV-VIS-028
4. FS-014 本文
5. Contract/Schema refs registered for this capability
6. State/Owner/AuthorityScope rules
7. UI-PCS-002 (when UI is present)
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
| Function | `FS-014` / `3D registration` |
| Domain | `Vision` |
| Guide | `DEV-VIS-028` |
| Input | `ObjectModel3D + rough transforms` |
| Output | `transforms/scores` |
| Result semantic | `VisionCandidate/GeometryEvidence` |
| Canonical port | `IObjectModel3dRegistrar` |
| Project | `Asun.Vision.Halcon` |
| UI PageContract | `UI-PCS-002` |
| Primary Work Package | `WP-10` |
| Algorithm baseline | `register_object_model_3d_global/pair` |
| Performance gate | `N model scaling` |
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
| Primary | `register_object_model_3d_global/pair` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `Pairwise/known-transform route` | Use pairwise or known transform only when the registration graph and task semantics allow it; never use a fallback that hides a global residual failure. |
| Reject / Block | `Insufficient overlap, divergent solution, residual above gate, invalid initial transform.` | 保留证据与原因；不得生成权威 OK。 |

**本 FS 的 fallback 不是“另写一个算法看看”。任何替代路线都必须来自当前 Development Guide / Operator Decision Matrix / Qualification 已登记的候选集合。**

### 16.4 Parameter authority matrix

| Parameter class | Authority/source | Hard rule |
|---|---|---|
| Target/ROI | `from approved target set or runtime binding` | never guessed from image unless the FS explicitly allows auto-targeting |
| Coordinate/Unit | `from CoordinateGraph/Calibration/Manufacturing reference` | must be explicit; mismatch blocks |
| Algorithm parameters | `Recipe/Method configuration version` | no hidden constants in code |
| Thresholds | `approved library/recipe/qualification` | AI may propose only as draft unless qualification says otherwise |
| Fallback policy | `FunctionSpec decision table` | no automatic semantic downgrade |
| Performance budget | `N model scaling` | 由 PerformanceProfile 绑定；至少记录 P50/P95/P99、峰值内存、并发安全和取消延迟；未实测不得声称 Qualified |

## 17. Robustness challenge set

At minimum, the function must be challenged against:
- `low overlap`
- `bad initialization`
- `outlier model`
- `disconnected graph`

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
ObjectModel3D + rough transforms
  → input snapshot/reference
  → 3D registration computation
  → quality gate
  → VisionCandidate/GeometryEvidence
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
| Port/interface | `IObjectModel3dRegistrar` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `ObjectModel3dRegistrar.cs` | Pipeline/algorithm implementation |
| Validator | `ObjectModel3dRegistrarValidator.cs` | Input/precondition/quality checks |
| Tests | `ObjectModel3dRegistrarTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-014/` | fixed datasets, expected outputs, provenance |
| Benchmark | `ObjectModel3dRegistrarBenchmark.cs` | P50/P95/P99/resource evidence |
| UI | `src/Asun.UI.Workspaces/UI-PCS-002/` | projection only; no production fact write |


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
| T14-01 | contract/schema validation | expected assertion + evidence + trace; no silent pass |
| T14-02 | normal + boundary + reject | expected assertion + evidence + trace; no silent pass |
| T14-03 | replay/golden dataset | expected assertion + evidence + trace; no silent pass |
| T14-04 | fault injection | expected assertion + evidence + trace; no silent pass |
| T14-05 | performance benchmark | expected assertion + evidence + trace; no silent pass |
| T14-06 | parameter sweep | expected assertion + evidence + trace; no silent pass |
| T14-07 | operator-version verification | expected assertion + evidence + trace; no silent pass |

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
| Function | `FS-014` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-VIS-028` | 指导文档是实施语义权威。 |
| Project | `Asun.Vision.Halcon` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `IObjectModel3dRegistrar` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-002` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `register_object_model_3d_global/pair` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
| SideEffectPolicy | `none; 无副作用；本功能不得直接写入生产事实、设备状态、放行状态或外部控制副作用。` | 冻结策略；任何未批准副作用路径必须 Blocker。 |
| Performance focus | `N model scaling` | 未测量前不得声称满足性能。 |

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

- 输入契约：`ObjectModel3D + rough transforms`
- 输出契约：`transforms/scores`
- 质量语义：Unknown / Invalid / NotApplicable / NotQualified 不得被映射为 OK。
- 证据要求：结果必须能够回溯到输入快照、RuntimeManifest、算法/规则版本、关键参数、坐标/标定引用和执行时间。

### AI 完成后的强制回报

AI 必须输出：变更文件清单、对应 FS 条目、Contract/Schema 变更、测试、Benchmark、未关闭风险、未验证 API、禁止路径复核结果。未能证明的内容必须标记 `Unverified`，不得写成 `Completed`。

## 27. Function-specific deterministic freeze profile

| Item | Frozen implementation rule |
|---|---|
| Function class | `3D Registration` |
| Primary algorithm/route | `register_object_model_3d_global/pair` |
| Fallback | `Pairwise/known-transform route` |
| Fallback trigger | Use pairwise or known transform only when the registration graph and task semantics allow it; never use a fallback that hides a global residual failure. |
| Reject/Block | Insufficient overlap, divergent solution, residual above gate, invalid initial transform. |
| Parameter authority | `['MinOverlap', 'MaxRegistrationResidual', 'InitialTransformSource', 'MaxIterations']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | Transform + score/residual + input snapshot + algorithm/parameter version + quality-gate outcome |
| UI rule | PageContract may project and command; it must not create/modify the underlying fact directly. |
| Performance | `N model scaling`; target values come only from the applicable PerformanceProfile. |
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

当前状态为DesignReview。历史ImplementationSpecificationReady与§25/27冻结表只保留迁移来源；产品字段/Owner和方法Profile按原产品接收，不能据旧标签开始全包生产编码。模块精确算法、API与工程根以IM-033唯一指导为准；文档核对不代表native、真实Golden或计量资格。


### 27.3 ScopeDrift stop condition

`ScopeDrift` is required to remain `none`. A request to add a new object, field, state, Owner, algorithm route, page command, external API or file outside this FS is not an implementation detail; it is a change candidate and must stop the current task until approved and re-indexed.

<a id="registration-package-binding"></a>
## 28. 当前独立包及可判定专项接收

PKG-060采用`src/Modules/Registration3D/`候选根，由单Owner完整交付，SM-012责任不变；FS-014历史WP-10对照职责保留，WP-08涉及数据/计量输入，两者只协调依赖，不双写。§16/21/25中的旧项目和端口登记是兼容映射，正式采纳由Contract/集成Owner串行同步，不同时新建两套Registrar。

| 专项 | 接收断言 |
|---|---|
| T14-G1 变换方向 | 已知非交换初值与增量，最终从原source到target；全局锚点重新表达保持相对变换 |
| T14-G2 指标 | global Scores为邻居数；pair原值保留；空对应即使RMSE=0也不可评价 |
| T14-G3 可观测性 | 平面点面数据不能无独立约束声称6DOF；归一/尺度变化不改变物理适用性结论 |
| T14-G4 图 | 两个非孤立分量、单桥错边、必需节点失败，分别保留原因而非删点后成功 |
| T14-G5 缺陷保持 | 独立基准下整体偏高0.2mm仍可测，不能由自配准归零 |
| T14-G6 生命周期 | 原Surface与共享native别名不被&distance覆盖；两实例、超时/取消/迟到全部关联正确 |

误差预算/数值门槛来自用途Profile；算法限制按IM-033的HALCON26.05路线和适用条件评估，不替换为自行承诺的微米数值。这些是拟验收，不是已运行结果。
