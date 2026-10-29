# Cross-process correlation

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-065`
- 类型：`Function Implementation Specification`
- 版本：`1.4.0-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-DOM-058B`
- 领域：`Quality/AI`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

以 Board/Panel/attempt/time-window 等固定 join 规则分析 SPI/AOI/工艺等过程关系，不宣称因果。

**不负责：** 写入原始质量事实、生产安全状态或未经授权的处置。

## 2. 权威与契约

输入契约：`committed facts or approved inputs`；输出契约：`projection/candidate/draft`。若字段尚未在现有 Schema 中冻结，必须登记到对应 ContractCandidate（通常 C-01/C-02/C-03/C-04/C-08），不能在功能目录中另建 JSON/数据库模型。

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

固定分析单位、工序角色、原实体/尝试关系、两侧源快照/截至点与JoinPolicyId/TimeWindowPolicyId。来源必须能区分已提交事实、外部待采纳证据和调查候选；按实际操作核单位/坐标/方法，不给纯身份追踪强制附加制造几何或图像输入。

缺必需关系、版本/作用域冲突、时间不确定只阻受影响的配对/统计。已证部分与原证据可按批准部分分析政策返回，必须保留预计总体、实际范围和逐原因缺口；量种不相容可查看两侧原值但不生成差值。历史撤销来源可在有权时解释旧分析，不授当前使用资格。

## 4. 正常执行流程

1. 从037/原Owner取已证物理关系和工序尝试，固定问题/分析单位及选择政策。
2. 调042读取固定来源，沿048唯一核心形成关系、未决/缺失及候选完整性；不按最新PASS或最近时刻猜前驱。
3. 质量应用逐组核目标关系、量种/参考/单位/方法与总体，保留多对多和板内观测层级。
4. 只有具名统计方法和适用条件齐全才交045计算；否则返回原值、关系/可比性及准确计数，不虚构相关系数/置信度。
5. 固定分析输入/方法/源水位及输出；迟到或更正形成新投影，原保存Unknown查询原操作；页面和报告均消费同一快照。

## 5. 算法/规则设计

**实施分类：** `Quality Correlation`

**Primary route：** `identity/time/window join + statistics`

**Fallback route：** `Evidence-only partial correlation / not-computable state`

**Fallback trigger：** When identity/time joins are uncertain, preserve partial evidence but do not manufacture causal/quality linkage.

**Reject / Block conditions：** Ambiguous identity, time-domain uncertainty, insufficient sample, conflicting process lineage.

**参数键（名称冻结，数值由批准 Profile / Recipe / Qualification 提供）：** `['JoinPolicyId', 'TimeWindowPolicyId', 'MinimumSampleCount']`

**结果语义：** `Correlation result + confidence/coverage`

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| 身份错配 | 注入/回放 身份错配 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 时间偏移 | 注入/回放 时间偏移 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| selection bias | 注入/回放 selection bias | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 缺数据 | 注入/回放 缺数据 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |

## 7. 质量门与拒识策略

至少建立三层 Gate：

1. **InputQualityGate**：输入是否可处理；
2. **AlgorithmQualityGate**：算法结果是否足够可靠；
3. **BusinessApplicabilityGate**：方法是否适用于当前产品/特征/尺度/材料/工艺。

任何 Gate 失败都要保留原因、证据引用和状态。`Unknown/Invalid/NotApplicable` 不允许被强制转换成 `OK`。

## 8. 性能与资源

查询、聚合、统计和 AI 检索均必须限制时间窗口/分母/数据水位并提供分页/缓存策略；统计不可阻塞生产事实提交。

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

UI/工作区：quality/AI workspace。交互遵循“状态→对象→结果→下一动作”；任何生产配置修改必须 Draft→Validate→Approve→Release；异常必须一键定位到证据。


关键操作顺序原则：系统自动带出可确定内容；操作员只处理异常、冲突和必要确认；批量动作先预览影响范围；高级参数渐进披露；每个阻断都有“原因+处理动作+证据”。

## 12. 测试设计

| 测试层 | 覆盖内容 | 必须留存 |
|---|---|---|
| Unit | 核心算法/规则、边界输入、单位/坐标、纯函数 | 输入快照、输出、expected/actual |
| Contract | Schema、状态、Owner、版本兼容 | validator report |
| Integration | 真实 consumer、Pipeline、Evidence | trace + receipt |
| Golden/Replay | 正常/边界/难例/拒识 | dataset hash + result diff |
| PerformanceProfile | `PF-FS-065` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
3. DEV-DOM-058B
4. FS-065 本文
5. Contract/Schema refs registered for this capability
6. State/Owner/AuthorityScope rules
7. UI-PCS-021 (when UI is present)
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
| Function | `FS-065` / `Cross-process correlation` |
| Domain | `Quality/AI` |
| Guide | `DEV-DOM-058B` |
| Input | `committed facts or approved inputs` |
| Output | `projection/candidate/draft` |
| Result semantic | `projection/candidate/draft` |
| Canonical port | `ICrossProcessCorrelation` |
| Project | `Asun.Domain.Quality` |
| UI PageContract | `UI-PCS-021` |
| Primary Work Package | `WP-20` |
| Algorithm baseline | `identity/time/window join + statistics` |
| Performance gate | `batch latency` |
| Test baseline | `Golden + Contract + Integration + Fault + Performance` |

### 16.1 Preconditions

- input objects exist and are version/hash identifiable;
- scope and authority are compatible;
- coordinate/unit/calibration conditions are satisfied where relevant;
- method capability covers the actual feature/measurand/material/surface/mode;
- current use must satisfy its qualification policy; authorized historical analysis may retain withdrawn references with their time and status, without granting new use;
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
| Primary | `identity/time/window join + statistics` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `Evidence-only partial correlation / not-computable state` | When identity/time joins are uncertain, preserve partial evidence but do not manufacture causal/quality linkage. |
| Reject / Block | `Ambiguous identity, time-domain uncertainty, insufficient sample, conflicting process lineage.` | 保留证据与原因；不得生成权威 OK。 |

**本 FS 的 fallback 不是“另写一个算法看看”。任何替代路线都必须来自当前 Development Guide / Operator Decision Matrix / Qualification 已登记的候选集合。**

### 16.4 Parameter authority matrix

| Parameter class | Authority/source | Hard rule |
|---|---|---|
| Target/ROI | `from approved target set or runtime binding` | never guessed from image unless the FS explicitly allows auto-targeting |
| Coordinate/Unit | `from CoordinateGraph/Calibration/Manufacturing reference` | must be explicit; mismatch blocks |
| Algorithm parameters | `Recipe/Method configuration version` | no hidden constants in code |
| Thresholds | `approved library/recipe/qualification` | AI may propose only as draft unless qualification says otherwise |
| Fallback policy | `FunctionSpec decision table` | no automatic semantic downgrade |
| Performance budget | `batch latency` | 由 PerformanceProfile 绑定；至少记录 P50/P95/P99、峰值内存、并发安全和取消延迟；未实测不得声称 Qualified |

## 17. Robustness challenge set

At minimum, the function must be challenged against:
- `身份错配`
- `时间偏移`
- `selection bias`
- `缺数据`

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
committed facts or approved inputs
  → input snapshot/reference
  → Cross-process correlation computation
  → quality gate
  → projection/candidate/draft
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
| Port/interface | `ICrossProcessCorrelation` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `CrossProcessCorrelation.cs` | Pipeline/algorithm implementation |
| Validator | `CrossProcessCorrelationValidator.cs` | Input/precondition/quality checks |
| Tests | `CrossProcessCorrelationTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-065/` | fixed datasets, expected outputs, provenance |
| Benchmark | `CrossProcessCorrelationBenchmark.cs` | P50/P95/P99/resource evidence |
| UI | `src/Asun.UI.Workspaces/UI-PCS-021/` | projection only; no production fact write |


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
| T65-01 | contract/schema validation | expected assertion + evidence + trace; no silent pass |
| T65-02 | normal + boundary + reject | expected assertion + evidence + trace; no silent pass |
| T65-03 | replay/golden dataset | expected assertion + evidence + trace; no silent pass |
| T65-04 | fault injection | expected assertion + evidence + trace; no silent pass |
| T65-05 | performance benchmark | expected assertion + evidence + trace; no silent pass |

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
| Function | `FS-065` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-DOM-058B` | 指导文档是实施语义权威。 |
| Project | `Asun.Domain.Quality` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `ICrossProcessCorrelation` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-021` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `identity/time/window join + statistics` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
| SideEffectPolicy | `candidate/projection only unless explicitly authorized；候选/投影不得获得生产权威，除非 Contract/AuthorityScope 明确授权。` | 冻结策略；任何未批准副作用路径必须 Blocker。 |
| Performance focus | `batch latency` | 未测量前不得声称满足性能。 |

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

- 输入契约：`committed facts or approved inputs`
- 输出契约：`projection/candidate/draft`
- 质量语义：Unknown / Invalid / NotApplicable / NotQualified 不得被映射为 OK。
- 证据要求：结果必须能够回溯到输入快照、RuntimeManifest、算法/规则版本、关键参数、坐标/标定引用和执行时间。

### AI 完成后的强制回报

AI 必须输出：变更文件清单、对应 FS 条目、Contract/Schema 变更、测试、Benchmark、未关闭风险、未验证 API、禁止路径复核结果。未能证明的内容必须标记 `Unverified`，不得写成 `Completed`。

## 27. Function-specific deterministic freeze profile

| Item | Frozen implementation rule |
|---|---|
| Function class | `Quality Correlation` |
| Primary algorithm/route | `identity/time/window join + statistics` |
| Fallback | `Evidence-only partial correlation / not-computable state` |
| Fallback trigger | When identity/time joins are uncertain, preserve partial evidence but do not manufacture causal/quality linkage. |
| Reject/Block | Ambiguous identity, time-domain uncertainty, insufficient sample, conflicting process lineage. |
| Parameter authority | `['JoinPolicyId', 'TimeWindowPolicyId', 'MinimumSampleCount']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | Correlation result + confidence/coverage + input snapshot + algorithm/parameter version + quality-gate outcome |
| UI rule | PageContract may project and command; it must not create/modify the underlying fact directly. |
| Performance | `batch latency`; target values come only from the applicable PerformanceProfile. |
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

<a id="cross-process-consumer-binding"></a>
## 28. 关联核心与质量应用的接线

本FS的`ICrossProcessCorrelation / Asun.Domain.Quality / WP-20 / UI-PCS-021`和既有三个参数键保持。应用绑定不代表私有join引擎：公开身份/查询桥→[048唯一关联方法](../../packages/PKG-048_ProcessCorrelation.md)→[058B质量消费](../06-domains/DEV-DOM-058B_Cross-Process%20Correlation与Disposition闭环开发指导.md#quality-correlation-consumption)→045具名统计→原分析保存/提案→页面/报告。048核心、质量应用、协议适配和UI按明确文件独占，不在各机台复制算法或生产事实Store。

JoinPolicyId必须指向固定身份/工序/目标关系及基数政策；TimeWindowPolicyId规定原时间域、端点/不确定性及迟到方式，不能覆盖身份冲突；MinimumSampleCount仅是所选统计方法的门之一，按分析单位和真实独立层级解释。新字段需求沿原C采纳，不把其塞成未登记第四个通用参数或依靠客户端猜值。

输出中的confidence/coverage不是一个通用百分比：分别给关系依据/歧义/缺失、预计与已证/可比/统计使用总体，以及所选方法确实提供的数值区间/误差。方法尚无区间能力时明确不提供；低样本可以查看已证关系，不生成默认零相关或高置信。一个目标多缺陷、一个板多Pad和一次消息多单位均不直接扩大独立样本数。

必须执行058B §8反例：同载具换件、同板多印刷/返修、汇总100但仅2条NG明细、默认构造值/缺源ID、多对多目标、不同height参考、100/60/56及UI筛选、迟到更正、局部复检缺邻域、取消/Unknown。CFX消息只在047/原接收Owner采纳后成为稳定来源；当前未运行协议SDK、跨进程关联或WPF，不将文档绑定通过当作实现完成。

具名方法唯一绑定[IM-043 §7.1.3.7–8](../../../independent-modules/statistics/DEVELOPMENT-GUIDE.md#cross-process-statistics-method)，应用消费沿[058B §10](<../06-domains/DEV-DOM-058B_Cross-Process Correlation与Disposition闭环开发指导.md#quality-named-statistics-consumption>)。先固定分析单位和完整配对，再调用无权重Pearson/平均秩Spearman、post−pre描述或单标签表/一致率/κ；图表不重新计算。板内多行不自动增加df，Unknown不填0/正常类，常数相关未定义；后继来源或参数形成新计算身份，旧保存仍按原操作查询。

条件Pearson零相关t、配对均值t须分别绑定独立性/分布/抽样解释及045实际尾域。Pearson CI、Spearman p/CI、κ/一致率p/CI、加权/聚类/重复测量推断、置换/bootstrap、多重比较、一致性限/等效/非劣/因果尚未完成；未支持不由MinimumSampleCount通过升级为成功。算法公式接收与正式合同/后端数值资格、真实WPF和生产验收分别记录，不从本FS的statistics一词推定全部已实现。
