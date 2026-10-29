# Coverage calculation

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-019`
- 类型：`Function Implementation Specification`
- 版本：`1.2.0`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-MET-034`
- 领域：`Metrology`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

明确区分 feature coverage、intra-feature sampling、board/panel/batch sampling，并产生实际 CoverageResult。

**不负责：** 生产机判、最终处置、真实设备安全功能。

## 2. 权威与契约

输入契约：`TargetSet/Policy`；输出契约：`CoverageResult`。若字段尚未在现有 Schema 中冻结，必须登记到对应 ContractCandidate（通常 C-01/C-02/C-03/C-04/C-08），不能在功能目录中另建 JSON/数据库模型。

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

TargetSet + MeasurementSamplingPolicy + actual execution observations。

缺实际观测、低质量、未测和无资格是覆盖计算需要准确报告的输入事实，不应一概拒绝计算。请求结构/身份损坏、作用域或几何约定无法解释时阻断受影响计算；保留其它已知范围。缺完整需求库存则全集未知，不生成100%覆盖。

## 4. 正常执行流程

1. 固定需求库存、适用/排除与采样Policy及来源水位。
2. 按实体/面/尝试/义务/观察角色对账，重复去重、冲突/未匹配分列。
3. 分开计划、采集、有效、算法评价、规则评价和证据提交，合法NG也可完整。
4. 对相容域求精确支持/缺口，检查不可拆分及完整多步骤，不将面积分数相加冒充覆盖。
5. 固定分母报告逐项缺口/N/A依据与暂定/完成范围；撤销贡献重新计算，原结果不原位改。
6. 详细公式/采样/空域/增量见[DEV-MET-034](../04-metrology/DEV-MET-034_Coverage与Sampling开发指导.md#coverage-sampling-implementation)，本FS不重复Schema。

## 5. 算法/规则设计

**实施分类：** `Coverage/Planning`

**Primary route：** `feature + intra-feature + sampling`

**Fallback route：** `No semantic fallback; recompute from frozen CoveragePolicy`

**Fallback trigger：** Missing/unknown coverage is an explicit coverage gap, not a product defect or a reason to pass or widen criteria.

**Reject / Block conditions：** Malformed scope/policy blocks calculation; missing observations or unknown applicability remain explicit coverage gaps; stale inputs cannot authorize current release.

**参数键（名称冻结，数值由批准 Profile / Recipe / Qualification 提供）：** `['CoveragePolicyId', 'FeatureCoverageFloor', 'IntraFeatureCoverageFloor', 'SamplingPolicyId']`

**结果语义：** `CoverageResult + coverage gap reasons`

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| unknown target | 固定库存并注入该异常 | 未知义务/全集边界单列，不能按收到对象补造分母 |
| missing actual evidence | 固定库存并注入该异常 | 对应义务保留未采/无有效域/未提交原因，不拒绝缺口报告本身 |
| partial execution | 固定库存并注入该异常 | 8项仅7项评价且已有NG，报告7/8与NG并存，后续不填完成 |
| late data | 固定库存并注入该异常 | 旧attempt不进入新尝试；已提交结果追加纠正，不原位覆盖或重放设备 |

## 7. 质量门与拒识策略

至少建立三层 Gate：

1. **InputQualityGate**：原库存/作用域可否解释，坏观测保留理由并排除其覆盖贡献；
2. **AlgorithmQualityGate**：集合/测度/组合观察及来源关联正确，空域、量化不确定不伪装完整；
3. **BusinessApplicabilityGate**：按批准功能/采样义务解释适用、缺测和排除，不自行决定质量放行。

任何 Gate 失败都要保留原因、证据引用和状态。`Unknown/Invalid/NotApplicable` 不允许被强制转换成 `OK`。

## 8. 性能与资源

分别计身份对账、空间粗筛、精确并/交/差、组合义务、撤销重算和投影。记录需求/观测数、Region复杂度及关系K、冷/热P50/P95/P99、峰值与排空；UI的LOD不降低计算精度。

性能采集点必须至少覆盖：输入准备、核心计算、质量评估、序列化/提交（如有）、UI 投影（如有）。高峰资源与长尾单独报告，不以平均耗时掩盖 P99。

## 9. 并发、取消、重试与恢复

- **Cancel**：取消尚未产生生产副作用的计算；已提交事实不可因 UI cancel 回滚。
- **Calculation Retry**：允许重新计算，生成新的 calculation identity。
- **Commit Retry**：必须复用原 CommitIdentity，并保持幂等。
- **Timeout**：形成明确超时事实/错误，不自动当作失败后的隐形重试。
- **Process Restart**：依赖 Snapshot/Receipt/Session 恢复；禁止读取 `latest` 猜状态。

## 10. 结果与证据

输出必须包含：输入引用、算法/规则版本、参数版本、坐标/单位、质量状态、执行时间、适用域、EvidenceRef；生产事实与 UI/报告投影分离。

CoverageResult绑定适用规则/策略版本，不提前嵌入尚未产生的规则结果或自己的提交回执。提交前计算和提交后六阶段关联沿[DEV-MET-034 §2](../04-metrology/DEV-MET-034_Coverage与Sampling开发指导.md#2-六个阶段质量和完成度分开)执行，防止Coverage等待自身提交而形成闭环死锁；正式字段回原C-04采纳。

## 11. UI / 操作员工作流

UI/工作区：coverage heatmap。交互遵循“状态→对象→结果→下一动作”；任何生产配置修改必须 Draft→Validate→Approve→Release；异常必须一键定位到证据。


关键操作顺序原则：系统自动带出可确定内容；操作员只处理异常、冲突和必要确认；批量动作先预览影响范围；高级参数渐进披露；每个阻断都有“原因+处理动作+证据”。

## 12. 测试设计

| 测试层 | 覆盖内容 | 必须留存 |
|---|---|---|
| Unit | 核心算法/规则、边界输入、单位/坐标、纯函数 | 输入快照、输出、expected/actual |
| Contract | Schema、状态、Owner、版本兼容 | validator report |
| Integration | 真实 consumer、Pipeline、Evidence | trace + receipt |
| Golden/Replay | 正常/边界/难例/拒识 | dataset hash + result diff |
| PerformanceProfile | `PF-FS-019` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
3. DEV-MET-034
4. FS-019 本文
5. Contract/Schema refs registered for this capability
6. State/Owner/AuthorityScope rules
7. UI-PCS-006 (when UI is present)
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
| Function | `FS-019` / `Coverage calculation` |
| Domain | `Metrology` |
| Guide | `DEV-MET-034` |
| Input | `TargetSet/Policy` |
| Output | `CoverageResult` |
| Result semantic | `CoverageResult + stage support/gaps/provenance` |
| Canonical port | `ICoverageCalculator` |
| Project | `Asun.Metrology.Core` |
| UI PageContract | `UI-PCS-006` |
| Primary Work Package | `WP-08` |
| Algorithm baseline | `feature + intra-feature + sampling` |
| Performance gate | `coverage compute` |
| Test baseline | `Golden + Contract + Integration + Fault + Performance` |

### 16.1 Preconditions

- the declared inventory/policy and available observations are version/hash identifiable; missing observations remain reportable gaps;
- scope and authority are compatible;
- coordinate/unit/calibration conditions are satisfied where relevant;
- actual capability/validity is evidence for each obligation, not assumed universally true before coverage reporting;
- retired/invalidated source contributions are identified and excluded from current support while historical evidence remains readable under permission;
- provenance and source completion/watermarks distinguish unavailable, missing, invalid and actual empty support.

### 16.2 Postconditions

- output semantics are typed and versioned;
- quality state is explicit;
- provenance is retained;
- no unauthorized production side effect was performed;
- failed quality gates cannot be represented as authoritative OK.

### 16.3 Algorithm decision matrix

| Route | Candidate | Selection / trigger |
|---|---|---|
| Primary | `feature + intra-feature + sampling` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `No semantic fallback; recompute from frozen CoveragePolicy` | Missing/unknown coverage is an explicit coverage gap, not a product defect or a reason to pass or widen criteria. |
| Reject / Block | `Malformed scope/policy blocks calculation; missing observations or unknown applicability remain explicit coverage gaps; stale inputs cannot authorize current release.` | 保留证据与原因；不得生成权威 OK。 |

**本 FS 的 fallback 不是“另写一个算法看看”。任何替代路线都必须来自当前 Development Guide / Operator Decision Matrix / Qualification 已登记的候选集合。**

### 16.4 Parameter authority matrix

| Parameter class | Authority/source | Hard rule |
|---|---|---|
| Target/ROI | `from approved target set or runtime binding` | never guessed from image unless the FS explicitly allows auto-targeting |
| Coordinate/Unit | `from CoordinateGraph/Calibration/Manufacturing reference` | must be explicit; mismatch blocks |
| Algorithm parameters | `Recipe/Method configuration version` | no hidden constants in code |
| Thresholds | `approved coverage/sampling policy` | percentage floors cannot waive critical subdomains, required observation roles or frozen denominators |
| Fallback policy | `FunctionSpec decision table` | no automatic semantic downgrade |
| Performance budget | `coverage compute` | 由 PerformanceProfile 绑定；至少记录 P50/P95/P99、峰值内存、并发安全和取消延迟；未实测不得声称 Qualified |

## 17. Robustness challenge set

At minimum, the function must be challenged against:
- `unknown target`
- `missing actual evidence`
- `partial execution`
- `late data`

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
| `Ready` | requested inventory/scope can be interpreted | calculate complete or incomplete coverage explicitly |
| `Blocked` | request scope/policy cannot be interpreted or computation is unauthorized | report affected computation; missing actual observations remain reportable gaps |
| `RecoverableError` | execution failed but restart/retry may be valid | retain evidence; follow retry policy |
| `Invalid/Rejected` | result cannot be trusted or is out-of-domain | no quality pass |
| `Completed` | coverage computation returned a valid typed report | report may contain gaps/NG; not product PASS or device release |

Only approved Application/Domain services may create production facts or machine-authoritative commands. UI and ViewModel are projections and command clients, not fact authorities.

## 19. Data/provenance and evidence mapping

```text
TargetSet/Policy
  → input snapshot/reference
  → Coverage calculation computation
  → quality gate
  → CoverageResult + stage support/gaps/provenance
  → EvidenceRef / Replay reference
  → downstream consumer
```

**Trace requirements**
- Correlation, coverage calculation identity and original result commit identity are separate. A persistence request must retain its original recoverable identity/receipt; it cannot be treated as merely a log tag.
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
| Port/interface | `ICoverageCalculator` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `CoverageCalculator.cs` | Pipeline/algorithm implementation |
| Validator | `CoverageCalculatorValidator.cs` | Input/precondition/quality checks |
| Tests | `CoverageCalculatorTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-019/` | fixed datasets, expected outputs, provenance |
| Benchmark | `CoverageCalculatorBenchmark.cs` | P50/P95/P99/resource evidence |
| UI | `src/Asun.UI.Workspaces/UI-PCS-006/` | projection only; no production fact write |


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
| T19-01 | 同名不同板面/PanelUnit/角色及同key异内容；身份隔离与冲突可查 | 固定输入/逐项预期及出处；拟验收，未执行 |
| T19-02 | 空集合/空Region/点线义务/小缝；分母零无100%，量化未确认不称全覆盖 | 固定输入/逐项预期及出处；拟验收，未执行 |
| T19-03 | 两个FOV各半且不可拆；多方向缺一步；重叠面积不相加填满 | 固定输入/逐项预期及出处；拟验收，未执行 |
| T19-04 | 撤销一帧后重叠区仍由另一帧支持；旧attempt/迟到/取消不串范围 | 固定输入/逐项预期及出处；拟验收，未执行 |
| T19-05 | 需求/观测/Region复杂度/关系K逐级负载，精度固定、字节有界和真实排空 | 固定输入/逐项预期及出处；拟验收，未执行 |
| T19-06 | AOI义务及钢网/涂覆区域两个消费者，无产品VM或私表依赖 | 固定输入/逐项预期及出处；拟验收，未执行 |
| T19-07 | 重复帧/排序/回放不增分母；同样本重拍不变新增抽样；补抽保留失败 | 固定输入/逐项预期及出处；拟验收，未执行 |
| T19-08 | margin不重复扣、需求外包/支持内包、非均匀映射与物理测度、99%漏关键区 | 固定输入/逐项预期及出处；拟验收，未执行 |

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
| Function | `FS-019` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-MET-034` | 指导文档是实施语义权威。 |
| Project | `Asun.Metrology.Core` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `ICoverageCalculator` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-006` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `feature + intra-feature + sampling` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
| SideEffectPolicy | `none; 无副作用；本功能不得直接写入生产事实、设备状态、放行状态或外部控制副作用。` | 冻结策略；任何未批准副作用路径必须 Blocker。 |
| Performance focus | `coverage compute` | 未测量前不得声称满足性能。 |

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

- 输入契约：`TargetSet/Policy`
- 输出契约：`CoverageResult`
- 质量语义：Unknown / Invalid / NotApplicable / NotQualified 不得被映射为 OK。
- 证据要求：结果必须能够回溯到输入快照、RuntimeManifest、算法/规则版本、关键参数、坐标/标定引用和执行时间。

### AI 完成后的强制回报

AI 必须输出：变更文件清单、对应 FS 条目、Contract/Schema 变更、测试、Benchmark、未关闭风险、未验证 API、禁止路径复核结果。未能证明的内容必须标记 `Unverified`，不得写成 `Completed`。

## 27. Function-specific deterministic freeze profile

| Item | Frozen implementation rule |
|---|---|
| Function class | `Coverage/Planning` |
| Primary algorithm/route | `feature + intra-feature + sampling` |
| Fallback | `No semantic fallback; recompute from frozen CoveragePolicy` |
| Fallback trigger | Missing/unknown coverage is an explicit coverage gap, not a product defect or a reason to pass or widen criteria. |
| Reject/Block | Malformed scope/policy blocks calculation; missing observations or unknown applicability remain explicit coverage gaps; stale inputs cannot authorize current release. |
| Parameter authority | `['CoveragePolicyId', 'FeatureCoverageFloor', 'IntraFeatureCoverageFloor', 'SamplingPolicyId']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | CoverageResult + coverage gap reasons + input snapshot + algorithm/parameter version + quality-gate outcome |
| UI rule | PageContract may project and command; it must not create/modify the underlying fact directly. |
| Performance | `coverage compute`; target values come only from the applicable PerformanceProfile. |
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

当前仍为DocMapped；已补覆盖计算/采样与具体拟验收，原Project/Port/Page兼容绑定不代表精确合同已批准。没有因文档核验获得算法、WPF、现场或工业性能资格。


### 27.3 ScopeDrift stop condition

`ScopeDrift` is required to remain `none`. A request to add a new object, field, state, Owner, algorithm route, page command, external API or file outside this FS is not an implementation detail; it is a change candidate and must stop the current task until approved and re-indexed.
