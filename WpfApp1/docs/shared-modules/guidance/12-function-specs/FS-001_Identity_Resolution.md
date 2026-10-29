# Identity Resolution

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-001`
- 类型：`Function Implementation Specification`
- 版本：`1.2.2-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-PLT-010`
- 领域：`Platform`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

把来自读码器、Hermes、MES 和人工观察的多个观察合并为可审计的身份解析结果；未决身份必须保留证据，但不能作为正常生产绑定。

**不负责：** 生产机判、最终处置、真实设备安全功能。

## 2. 权威与契约

输入契约：`CodeReader/Hermes/MES/Human Observation`；输出契约：`IdentityResolutionReceipt/BoardIdentity`。若字段尚未在现有 Schema 中冻结，必须登记到对应 ContractCandidate（通常 C-01/C-02/C-03/C-04/C-08），不能在功能目录中另建 JSON/数据库模型。

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

规范化来源、时间域、观察值、来源可信等级、产品/工单作用域；校验观察是否属于当前 BoardRun/生产作用域。

必须在执行前阻断：缺失必需输入、版本/hash 不匹配、作用域不一致、单位/坐标不一致、资格失效、能力不支持、输入质量低于该方法的最小条件。

## 4. 正常执行流程

1. 固定本次实体/工单/入口作用域、IdentityPolicy和必需来源；按[037 §6.1](../../packages/PKG-037_Identity.md#identity-implementation)接收Observation集合。按原事件身份和内容摘要处理重投，同事件异内容冲突；不按字符串相同合并不同物理观察。必需来源未闭合时不将暂时唯一解释转accepted。
2. 保留原观察及其内容层和来源；仅按批准IdentityPolicy派生规范化值，再执行精确匹配、优先级和冲突矩阵。读码byte、引擎串、HRI/GS1字段与期待值分开；字节不可得不以字符串回编码补造，未知字段/分隔不按期待猜补。
3. 产生`IdentityResolutionReceipt`的原结论与依据，说明accepted/rejected/unresolved/conflict。accepted表示本次冻结来源集合有唯一合规解释；解码成功、语法有效或质量高各自不足以授予accepted。
4. 只有Orchestrator身份Owner才把解析结果绑定为`BoardIdentity`。按037 §7.2–7.3复核当前权限、作用域、关系和CAS，沿原幂等身份提交；回执Unknown查询原操作，不更换板号或重扫制造第二次绑定。
5. 持精确身份绑定回执进入原Recipe/Runtime admission；未决走retained/hold/recovery并保留观察。程序拒绝不抹身份依据；重采、计算重试、工序/检测尝试由各原Owner按既定政策区分，不由解析器自动重建。

## 5. 算法/规则设计

**实施分类：** `Workflow`

**Primary route：** `policy + conflict resolution`

**Fallback route：** `Manual Resolution / approved observation source`

**Fallback trigger：** Primary produces Resolved only when one policy-consistent identity wins; conflicting trusted sources or scope mismatch blocks.

**Reject / Block conditions：** Unresolved, conflicting, stale, wrong-scope, duplicate-but-incompatible identities.

**参数键（历史候选名称；正式名称及值由原 Contract / Profile / Recipe / Qualification 采纳）：** `['IdentityPolicyVersion', 'ObservationFreshnessWindow', 'SourceTrustClass', 'ScopeId']`

**结果语义：** `IdentityResolutionReceipt + BoardIdentity provenance`

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| duplicate identity in incompatible scopes | 注入/回放 duplicate identity in incompatible scopes | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| conflicting trusted observations | 注入/回放 conflicting trusted observations | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| unresolved identity | 注入/回放 unresolved identity | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| stale observation | 注入/回放 stale observation | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| scope mismatch | 注入/回放 scope mismatch | 显式质量状态；必要时 Reject/Review，不得静默 PASS |

## 7. 质量门与拒识策略

至少建立三层 Gate：

1. **InputQualityGate**：输入是否可处理；
2. **AlgorithmQualityGate**：算法结果是否足够可靠；
3. **BusinessApplicabilityGate**：方法是否适用于当前产品/特征/尺度/材料/工艺。

任何 Gate 失败都要保留原因、证据引用和状态。`Unknown/Invalid/NotApplicable` 不允许被强制转换成 `OK`。

## 8. 性能与资源

记录关键阶段 P50/P95/P99、峰值内存、队列长度和失败重试次数。

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

UI/工作区：Identity/Admission workspace。交互遵循“状态→对象→结果→下一动作”；任何生产配置修改必须 Draft→Validate→Approve→Release；异常必须一键定位到证据。

主页面左侧身份来源时间线；中心显示当前解析候选；右侧显示冲突来源、Policy 版本和阻断原因；未决身份提供“保留证据/重试解析”而非“忽略”。

关键操作顺序原则：系统自动带出可确定内容；操作员只处理异常、冲突和必要确认；批量动作先预览影响范围；高级参数渐进披露；每个阻断都有“原因+处理动作+证据”。

## 12. 测试设计

| 测试层 | 覆盖内容 | 必须留存 |
|---|---|---|
| Unit | 核心算法/规则、边界输入、单位/坐标、纯函数 | 输入快照、输出、expected/actual |
| Contract | Schema、状态、Owner、版本兼容 | validator report |
| Integration | 真实 consumer、Pipeline、Evidence | trace + receipt |
| Golden/Replay | 正常/边界/难例/拒识 | dataset hash + result diff |
| PerformanceProfile | `PF-FS-001` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
3. DEV-PLT-010
4. FS-001 本文
5. Contract/Schema refs registered for this capability
6. State/Owner/AuthorityScope rules
7. UI-PCS-001 (when UI is present)
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
| Function | `FS-001` / `Identity Resolution` |
| Domain | `Platform` |
| Guide | `DEV-PLT-010` |
| Input | `CodeReader/Hermes/MES/Human Observation` |
| Output | `IdentityResolutionReceipt/BoardIdentity` |
| Result semantic | `IdentityResolutionReceipt/BoardIdentity` |
| Canonical port | `IIdentityResolver` |
| Project | `Asun.Platform.Core` |
| UI PageContract | `UI-PCS-001` |
| Primary Work Package | `WP-03` |
| Algorithm baseline | `policy + conflict resolution` |
| Performance gate | `PF-FS-001; no busy polling` |
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
| Primary | `policy + conflict resolution` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `Manual Resolution / approved observation source` | Primary produces Resolved only when one policy-consistent identity wins; conflicting trusted sources or scope mismatch blocks. |
| Reject / Block | `Unresolved, conflicting, stale, wrong-scope, duplicate-but-incompatible identities.` | 保留证据与原因；不得生成权威 OK。 |

**本 FS 的 fallback 不是“另写一个算法看看”。任何替代路线都必须来自当前 Development Guide / Operator Decision Matrix / Qualification 已登记的候选集合。**

### 16.4 Parameter authority matrix

| Parameter class | Authority/source | Hard rule |
|---|---|---|
| Target/ROI | `from approved target set or runtime binding` | never guessed from image unless the FS explicitly allows auto-targeting |
| Coordinate/Unit | `from CoordinateGraph/Calibration/Manufacturing reference` | must be explicit; mismatch blocks |
| Algorithm parameters | `Recipe/Method configuration version` | no hidden constants in code |
| Thresholds | `approved library/recipe/qualification` | AI may propose only as draft unless qualification says otherwise |
| Fallback policy | `FunctionSpec decision table` | no automatic semantic downgrade |
| Performance budget | `PF-FS-001; no busy polling` | 由 PerformanceProfile 绑定；至少记录 P50/P95/P99、峰值内存、并发安全和取消延迟；未实测不得声称 Qualified |

## 17. Robustness challenge set

At minimum, the function must be challenged against:
- `duplicate identity in incompatible scopes`
- `conflicting trusted observations`
- `unresolved identity`
- `stale observation`
- `scope mismatch`

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
CodeReader/Hermes/MES/Human Observation
  → input snapshot/reference
  → Identity Resolution computation
  → quality gate
  → IdentityResolutionReceipt/BoardIdentity
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
| Port/interface | `IIdentityResolver` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `IdentityResolver.cs` | Pipeline/algorithm implementation |
| Validator | `IdentityResolverValidator.cs` | Input/precondition/quality checks |
| Tests | `IdentityResolverTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-001/` | fixed datasets, expected outputs, provenance |
| Benchmark | `IdentityResolverBenchmark.cs` | P50/P95/P99/resource evidence |
| UI | `src/Asun.UI.Workspaces/UI-PCS-001/` | projection only; no production fact write |


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
| T01-01 | contract/schema validation | expected assertion + evidence + trace; no silent pass |
| T01-02 | normal + boundary + reject | expected assertion + evidence + trace; no silent pass |
| T01-03 | replay/golden dataset | expected assertion + evidence + trace; no silent pass |
| T01-04 | fault injection | expected assertion + evidence + trace; no silent pass |
| T01-05 | performance benchmark | expected assertion + evidence + trace; no silent pass |

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
| Function | `FS-001` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-PLT-010` | 指导文档是实施语义权威。 |
| Project | `Asun.Platform.Core` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `IIdentityResolver` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-001` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `policy + conflict resolution` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
| SideEffectPolicy | `none; 无副作用；本功能不得直接写入生产事实、设备状态、放行状态或外部控制副作用。` | 冻结策略；任何未批准副作用路径必须 Blocker。 |
| Performance focus | `PF-FS-001; no busy polling` | 未测量前不得声称满足性能。 |

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

- 输入契约：`CodeReader/Hermes/MES/Human Observation`
- 输出契约：`IdentityResolutionReceipt/BoardIdentity`
- 质量语义：Unknown / Invalid / NotApplicable / NotQualified 不得被映射为 OK。
- 证据要求：结果必须能够回溯到输入快照、RuntimeManifest、算法/规则版本、关键参数、坐标/标定引用和执行时间。

### AI 完成后的强制回报

AI 必须输出：变更文件清单、对应 FS 条目、Contract/Schema 变更、测试、Benchmark、未关闭风险、未验证 API、禁止路径复核结果。未能证明的内容必须标记 `Unverified`，不得写成 `Completed`。

## 27. Function-specific deterministic freeze profile

| Item | Frozen implementation rule |
|---|---|
| Function class | `Workflow` |
| Primary algorithm/route | `policy + conflict resolution` |
| Fallback | `Manual Resolution / approved observation source` |
| Fallback trigger | Primary produces Resolved only when one policy-consistent identity wins; conflicting trusted sources or scope mismatch blocks. |
| Reject/Block | Unresolved, conflicting, stale, wrong-scope, duplicate-but-incompatible identities. |
| Parameter authority | `['IdentityPolicyVersion', 'ObservationFreshnessWindow', 'SourceTrustClass', 'ScopeId']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | IdentityResolutionReceipt + BoardIdentity provenance + input snapshot + algorithm/parameter version + quality-gate outcome |
| UI rule | PageContract may project and command; it must not create/modify the underlying fact directly. |
| Performance | `PF-FS-001; no busy polling`; target values come only from the applicable PerformanceProfile. |
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

<a id="identity-code-reading-method-binding"></a>
## 28. 受控观察与读码来源的方法绑定

本页§4的具体解析、关系及幂等/CAS方法唯一维护于[037 §6–7](../../packages/PKG-037_Identity.md#identity-implementation)，读码内容交接见[037 §8](../../packages/PKG-037_Identity.md#code-observation-identity-consumption)，原返回与质量见[021B §7](../03-vision/DEV-VIS-021B_条码解码与印制质量独立能力开发指导.md#code-reading-evidence-method)。037消费宿主观察合同，不增加023/视觉库强依赖，不复制解码器或GS1核心；原身份Owner、运行清单Owner和质量处置保持分开。

按原T01-01～05补入可判定断言：两个位置同0012保留两个观察；相同事件ID异内容拒绝覆盖；原byte含NUL但引擎串截断仍保留各层；超时/上限/必需来源尚未完成不能因成功列表唯一而绑定；语法正确但工单/父子关系冲突保持未决或冲突；解析后换件/撤权/旧CAS不能沿用旧结论写入；原绑定Unknown查同操作而非重扫生成新绑定。缺raw只限制依赖该层的用途，缺GS1正式方法只限制该解析，不冻结可用的普通文本显示与其它已批准来源链。

原IIdentityResolver、代码根、注册表和测试ID保持历史绑定，具体字段/错误/公共签名仍沿原C候选采纳。本次只修正文档步骤歧义和方法导航，没有执行实际身份绑定、读码、GS1、WPF或性能验证；不将源格式、候选政策或文档检查升级为生产批准。

<a id="identity-gs1-method-binding"></a>
### 28.1 GS1内容方法及身份门禁

§4第2步的GS1受控解释绑定[037 §9](../../packages/PKG-037_Identity.md#gs1-content-parsing-method)：入口/词典/方法冻结→独占context→失败清派生结果→复制分层输出/来源→应用字段核对→原037完整解析→Orchestrator当前条件/CAS绑定。真实来源层、语法解释、业务一致性、生产绑定分开；不新增原端口、Schema、包或直接依赖。该章已有研究方法，正式格式/Profile、词典构建和native/.NET接入仍未冻结，不把本次导航当生产准入。

原T01断言补：普通非GS1字符串调用返回true不得accepted；合法AI10长值不能按期待拆补21；同AI同值在元素串与DL的规则不同；日期日00不造DateTime；失败后的旧context输出不能冒本次结果；词典缺失/结构错误不得静默换版本；跨实物不能凑req；逐AI原字节区间未知只能整观察引用。语法成功后撤权/换件/旧CAS/Unknown仍按§4与037原写权处理。有限研究例不代实际引擎、身份事务或WPF验收。
