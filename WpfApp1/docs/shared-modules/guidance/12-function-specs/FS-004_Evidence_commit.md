# Evidence commit

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-004`
- 类型：`Function Implementation Specification`
- 版本：`1.2.0`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-PLT-012`
- 领域：`Platform`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

把事实、原始证据和结果提交构成可验证、幂等、可回读的 Evidence Graph 闭环。

**不负责：** 生产机判、最终处置、真实设备安全功能。

## 2. 权威与契约

输入契约：`Facts/Evidence blobs`；输出契约：`CommitReceipt`。若字段尚未在现有 Schema 中冻结，必须登记到对应 ContractCandidate（通常 C-01/C-02/C-03/C-04/C-08），不能在功能目录中另建 JSON/数据库模型。

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

检查事实版本、Evidence references、CAS 对象存在性、CommitIdentity。

提交前拒绝非法Schema、未授权写入、身份/版本/hash/引用冲突、最低提交证据不满足。合法的算法无效、NG、缺测和资格失效事实必须按失败结果证据政策记录，不能因为被保存的检测结果不合格就拒绝保存。

## 4. 正常执行流程

1. 生成 Evidence Manifest。
2. 先完成内容地址化对象和完整性校验。
3. 按 CommitIdentity 幂等提交；同键同载荷返回原 Receipt。
4. 结果、证据引用、Outbox意图、receipt和原操作结果在同一事务提交；之后按同提交身份回读，不在结果事务外补写回执/通知。
5. 区分 calculation retry 与 commit retry，禁止重复事实。

## 5. 算法/规则设计

**实施分类：** `Data Commit`

**Primary route：** `CAS + idempotent commit`

**Fallback route：** `Durable outbox retry with same CommitIdentity`

**Fallback trigger：** Retry the same CommitIdentity; a local durable outbox is only an evidence-preserving transport fallback and never creates a second fact.

**Reject / Block conditions：** Hash mismatch, manifest inconsistency, immutable store refusal, duplicate with conflicting content, exhausted durable retry.

**参数键（名称冻结，数值由批准 Profile / Recipe / Qualification 提供）：** `['CommitIdentity', 'EvidenceManifestHash', 'OutboxRetention', 'CommitRetryLimit']`

**结果语义：** `ResultCommitReceipt + immutable EvidenceManifest`

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| partial upload | 在格式/流尾结束前中断 | 操作未完成，无正常提交回执；按实际块续传或终结 |
| hash mismatch | 传输或持久内容与声明不符 | 拒绝该对象引用，保留原错误；不覆盖同hash已有对象 |
| duplicate commit | 同提交身份重复调用 | 同载荷返回原精确回执；不同载荷冲突 |
| network loss | commit请求后丢响应 | 查询同身份，未明则保持未知/引用，不能假报回滚 |
| outbox replay | 发送后ACK前重启 | 原业务身份重投，消费者去重；不制造第二结果事实 |

## 7. 存储准入与检测质量分开

此功能检查请求/Schema/授权、证据字节完整性、身份与逻辑关联、提交策略，不重新判定输入图像或产品是否合格。合法NG、Unknown、Invalid、未执行及标定失效是可存的领域事实；只有它们的表达/引用/最低证据不合法才拒绝提交。工艺完整性、最小持久化证据、Replay齐备度分别计算，不允许通过伪空图或改optional绕过。

“结果已保存”不等于“检测合格”，也不等于“允许出板”。Missing/Corrupt/Expired/Forbidden等读取状态不改历史事实。逐步协议与反例见DEV-PLT-012 §1–8，本页不另建第二质量门。

## 8. 性能与资源

记录关键阶段 P50/P95/P99、峰值内存、队列长度和失败重试次数。

性能采集点必须至少覆盖：输入准备、核心计算、质量评估、序列化/提交（如有）、UI 投影（如有）。高峰资源与长尾单独报告，不以平均耗时掩盖 P99。

## 9. 并发、取消、重试与恢复

- **Cancel**：停止尚未接纳/提交的工作按原scope归还；commit已经发出时取消不能证明回滚，查询原结果。
- **Calculation Retry**：本FS不重算检测；上游需要重算由原运行Owner创建关联计算尝试，不能由提交失败触发。
- **Commit Retry**：必须复用原 CommitIdentity，并保持幂等。
- **Timeout**：形成明确超时事实/错误，不自动当作失败后的隐形重试。
- **Process Restart**：依赖 Snapshot/Receipt/Session 恢复；禁止读取 `latest` 猜状态。

## 10. 结果与证据

输出必须包含：输入引用、算法/规则版本、参数版本、坐标/单位、质量状态、执行时间、适用域、EvidenceRef；生产事实与 UI/报告投影分离。

## 11. UI / 操作员工作流

UI/工作区：Evidence viewer。交互遵循“状态→对象→结果→下一动作”；本页只读历史事实，异常必须定位到原证据/缺项；不提供改配置或修改原机判入口。

Evidence Viewer 显示证据图谱、hash、对象类型、提交 Receipt 和回读结果；异常对象突出完整性失败。

关键操作顺序原则：系统自动带出可确定内容；操作员只处理异常、冲突和必要确认；批量动作先预览影响范围；高级参数渐进披露；每个阻断都有“原因+处理动作+证据”。

## 12. 测试设计

| 测试层 | 覆盖内容 | 必须留存 |
|---|---|---|
| Unit | 核心算法/规则、边界输入、单位/坐标、纯函数 | 输入快照、输出、expected/actual |
| Contract | Schema、状态、Owner、版本兼容 | validator report |
| Integration | 真实 consumer、Pipeline、Evidence | trace + receipt |
| Golden/Replay | 正常/边界/难例/拒识 | dataset hash + result diff |
| PerformanceProfile | `PF-FS-004` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
3. DEV-PLT-012
4. FS-004 本文
5. Contract/Schema refs registered for this capability
6. State/Owner/AuthorityScope rules
7. UI-PCS-013 (when UI is present)
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
| Function | `FS-004` / `Evidence commit` |
| Domain | `Platform` |
| Guide | `DEV-PLT-012` |
| Input | `Facts/Evidence blobs` |
| Output | `CommitReceipt` |
| Result semantic | `CommitReceipt` |
| Canonical port | `IEvidenceCommitService` |
| Project | `Asun.Platform.Core` |
| UI PageContract | `UI-PCS-013` |
| Primary Work Package | `WP-05` |
| Algorithm baseline | `CAS + idempotent commit` |
| Performance gate | `commit latency/IO` |
| Test baseline | `Golden + Contract + Integration + Fault + Performance` |

### 16.1 Preconditions

- input objects exist and are version/hash identifiable;
- scope and authority are compatible;
- evidence identity/unit/coordinate/calibration references correctly describe the recorded result, including explicit historical invalidity;
- method/capability failure, when part of a valid recorded result, remains explicit and is not converted to a storage rejection;
- historical revoked/withdrawn references remain attributable under read/retention policy; new production use is not authorized by storage;
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
| Primary | `CAS + idempotent commit` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `Durable outbox retry with same CommitIdentity` | Retry the same CommitIdentity; a local durable outbox is only an evidence-preserving transport fallback and never creates a second fact. |
| Reject / Block | `Hash mismatch, manifest inconsistency, immutable store refusal, duplicate with conflicting content, exhausted durable retry.` | 保留证据与原因；不得生成权威 OK。 |

**本 FS 的 fallback 不是“另写一个算法看看”。任何替代路线都必须来自当前 Development Guide / Operator Decision Matrix / Qualification 已登记的候选集合。**

### 16.4 Parameter authority matrix

| Parameter class | Authority/source | Hard rule |
|---|---|---|
| Target/ROI | `from approved target set or runtime binding` | never guessed from image unless the FS explicitly allows auto-targeting |
| Coordinate/Unit | `from CoordinateGraph/Calibration/Manufacturing reference` | must be explicit; mismatch blocks |
| Algorithm parameters | `Recipe/Method configuration version` | no hidden constants in code |
| Thresholds | `approved library/recipe/qualification` | AI may propose only as draft unless qualification says otherwise |
| Fallback policy | `FunctionSpec decision table` | no automatic semantic downgrade |
| Performance budget | `commit latency/IO` | 由 PerformanceProfile 绑定；至少记录 P50/P95/P99、峰值内存、并发安全和取消延迟；未实测不得声称 Qualified |

## 17. Robustness challenge set

At minimum, the function must be challenged against:
- `partial upload`
- `hash mismatch`
- `duplicate commit`
- `network loss`
- `outbox replay`

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
| `Ready` | request/schema/authority/reference and minimum commit evidence checks pass | execute persistence; recorded NG/Invalid stays unchanged |
| `Blocked` | required input/capability/authority missing | show reason; no production effect |
| `RecoverableError` | execution failed but restart/retry may be valid | retain evidence; follow retry policy |
| `Invalid/Rejected` | the submission or reference is malformed/conflicting, not merely a recorded algorithm Invalid | reject this write without rewriting production quality |
| `Completed` | output and evidence committed or returned to caller | immutable output semantics |

Only approved Application/Domain services may create production facts or machine-authoritative commands. UI and ViewModel are projections and command clients, not fact authorities.

## 19. Data/provenance and evidence mapping

```text
Facts/Evidence blobs
  → input snapshot/reference
  → Evidence commit computation
  → quality gate
  → CommitReceipt
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
| Port/interface | `IEvidenceCommitService` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `EvidenceCommitService.cs` | Pipeline/algorithm implementation |
| Validator | `EvidenceCommitServiceValidator.cs` | Submission/schema/reference/minimum evidence checks; preserve recorded quality |
| Tests | `EvidenceCommitServiceTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-004/` | fixed datasets, expected outputs, provenance |
| Benchmark | `EvidenceCommitServiceBenchmark.cs` | P50/P95/P99/resource evidence |
| UI | `src/Asun.UI.Workspaces/UI-PCS-013/` | projection only; no production fact write |


**Implementation order**
1. contract/port and validation;
2. pure core logic / algorithm adapter;
3. storage admission/error semantics, preserving recorded product quality;
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
| T04-01 | contract/schema validation | expected assertion + evidence + trace; no silent pass |
| T04-02 | normal + boundary + reject | expected assertion + evidence + trace; no silent pass |
| T04-03 | replay/golden dataset | expected assertion + evidence + trace; no silent pass |
| T04-04 | fault injection | expected assertion + evidence + trace; no silent pass |
| T04-05 | performance benchmark | expected assertion + evidence + trace; no silent pass |

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
| Function | `FS-004` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-PLT-012` | 指导文档是实施语义权威。 |
| Project | `Asun.Platform.Core` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `IEvidenceCommitService` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-013` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `CAS + idempotent commit` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
| SideEffectPolicy | `controlled production/integration side effect via approved Port；受控副作用只能通过批准 Port，并且必须满足 Authority/Permission/Commit 门禁。` | 冻结策略；任何未批准副作用路径必须 Blocker。 |
| Performance focus | `commit latency/IO` | 未测量前不得声称满足性能。 |

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

- 输入契约：`Facts/Evidence blobs`
- 输出契约：`CommitReceipt`
- 质量语义：Unknown / Invalid / NotApplicable / NotQualified 不得被映射为 OK。
- 证据要求：结果必须能够回溯到输入快照、RuntimeManifest、算法/规则版本、关键参数、坐标/标定引用和执行时间。

### AI 完成后的强制回报

AI 必须输出：变更文件清单、对应 FS 条目、Contract/Schema 变更、测试、Benchmark、未关闭风险、未验证 API、禁止路径复核结果。未能证明的内容必须标记 `Unverified`，不得写成 `Completed`。

## 27. Function-specific deterministic freeze profile

| Item | Frozen implementation rule |
|---|---|
| Function class | `Data Commit` |
| Primary algorithm/route | `CAS + idempotent commit` |
| Fallback | `Durable outbox retry with same CommitIdentity` |
| Fallback trigger | Retry the same CommitIdentity; a local durable outbox is only an evidence-preserving transport fallback and never creates a second fact. |
| Reject/Block | Hash mismatch, manifest inconsistency, immutable store refusal, duplicate with conflicting content, exhausted durable retry. |
| Parameter authority | `['CommitIdentity', 'EvidenceManifestHash', 'OutboxRetention', 'CommitRetryLimit']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | ResultCommitReceipt + immutable EvidenceManifest + input snapshot + algorithm/parameter version + quality-gate outcome |
| UI rule | PageContract may project and command; it must not create/modify the underlying fact directly. |
| Performance | `commit latency/IO`; target values come only from the applicable PerformanceProfile. |
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

<a id="evidence-specific-closure"></a>
## 28. 精确提交及恢复验收

实现唯一流程见[DEV-PLT-012](<../02-platform/DEV-PLT-012_Evidence Graph与Result Commit开发指导.md#evidence-commit-protocol>)，技术适配见[PKG-041](../../packages/PKG-041_Storage.md#storage-transactions-durability)。最小软件闭环必须覆盖合法失败结果保存、同blob多逻辑关联、重复帧不补缺FOV、对象先持久/保持后结果可见、回执/通知同事务、未知结果同ID查询，以及GC与读取/备份/新增引用的竞争。

Fallback中“durable outbox retry”只指可靠传递已有相同业务意图，不能把本地缓存/投递ACK冒充未发生的权威结果提交；离线权威/耐久位置仍按产品部署决定。取消/Dispose不证明commit被回滚，read-back不单独证明物理RPO=0。数据已提交、可重放、产品合格、质量放行、设备动作分别验收，原端口/Owner不变。
