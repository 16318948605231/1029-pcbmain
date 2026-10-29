# CAD/PnP target generation

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-056`
- 类型：`Function Implementation Specification`
- 版本：`1.3.0`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-DOM-057A`
- 领域：`AOI`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

从制造几何、BOM/PnP、PackageLibrary 生成 AOI Draft targets。

**不负责：** 生产机判、最终处置、真实设备安全功能。

## 2. 权威与契约

输入语义：CAD/PnP/BOM适用资料、坐标/单位/面别和封装映射。输出语义：位号/元件目标、来源和歧义；不凭几何猜缺失料号。以上明确本功能边界，不是新DTO/Schema；精确字段按GATE-001与对应既有ContractCandidate逐项采纳。

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

先区分整个输入集合不可处理与某目标/方法未决：伪造hash、无法确认来源范围或非法结构阻断受影响处理；缺BOM、库缺项、局部位置/可见性不足可输出明确不完整的工程候选。无法确定单位/坐标的对象不能实例化；缺总全集不得以已生成数作为覆盖分母。完整性/资格门在试检及发布各按用途复核，未决不是产品NG。

## 4. 正常执行流程

1. 固定资料、导出过滤、装配变体与坐标约定，对账BOM/PnP/CAM。
2. 建立稳定拼板/面/位号实例和独立必检义务；缺行不自动DNP。
3. 通过034按身份/硬约束/精确版本匹配，歧义保留未决。
4. 通过007/020和工艺规则生成component/lead/pad及ROI/方法候选，保留针序与来源依赖。
5. 对比B/L/R的值、覆盖意图和耦合组，生成有界typed补丁/覆盖缺口；由035保存，不直接Release。
6. 按057A的P0–P7完成试检与审批交接，FS-056自身保持纯生成；完整流程见[057A](<../06-domains/DEV-DOM-057A_AOI CAD PnP与Target自动生成开发指导.md#aoi-target-synthesis>)。

## 5. 算法/规则设计

**实施分类：** `AOI Target Synthesis`

**Primary route：** `reference binding + target synthesis`

**Fallback route：** `Explicit source hierarchy from SourceSetManifest`

**Fallback trigger：** Fallback to another source only when it is declared Present/Valid and the mapping policy allows it; never silently substitute.

**Reject / Block conditions：** Ambiguous mapping, missing source, incompatible board revision, target outside coverage. 限受影响的目标/方法与生产发布；不把部分工程候选整体吞掉。

**参数键（名称冻结，数值由批准 Profile / Recipe / Qualification 提供）：** `['SourceSetManifestId', 'MappingPolicyId', 'TargetSynthesisPolicyId']`

**结果语义：** `Draft TargetSet + unresolved items`

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| 缺 BOM | 有PnP及图像、无批准料号来源 | 仅已知位置/外观候选；身份/必检全集未决，不凭value补MPN |
| 库缺项 | 同封装存在但无对应料号/方法 | 保留原实例与检测义务；仅可建议几何复用，不删除目标 |
| 坐标系冲突 | bottom已翻X、再统一反号；奇异逆变换 | 约定冲突/不可逆明确拒绝相关映射，不沿用旧变换 |
| 料号替换歧义 | 同value/封装但不同MPN、两个合法外观变体 | 身份/混料政策未决；必要子项不能跨变体拼PASS |

## 7. 质量门与拒识策略

本FS的三类检查面向工程候选及生成完整性，不生成产品质量判定：

1. **InputQualityGate**：来源结构/单位/范围能否处理，逐依赖范围给理由。
2. **AlgorithmQualityGate**：稳定身份、映射/库选择和几何生成是否确定且无歧义；完整性与置信分开。
3. **BusinessApplicabilityGate**：方法/模板适用性、装配意图及必检覆盖是否闭合；隐藏焊接不可凭外观模板填满覆盖。

任何 Gate 失败都要保留原因、证据引用和状态。`Unknown/Invalid/NotApplicable` 不允许被强制转换成 `OK`。

## 8. 性能与资源

先元数据对账/身份索引/模板复用，再按需生成局部几何和有界外观候选。试检调用原执行/Replay链且单独计时；本FS不逐元件重复解码全图。测来源行数、拼板实例/候选/ROI数、展开深度和内存；top-k截断不能证明唯一，预算使用批准PerformanceProfile。

性能采集点必须至少覆盖：输入准备、核心计算、质量评估、序列化/提交（如有）、UI 投影（如有）。高峰资源与长尾单独报告，不以平均耗时掩盖 P99。

## 9. 并发、取消、重试与恢复

- **Cancel**：终止本次候选生成的后续调度，保留完成/未完成范围；原执行Owner排空native。若应用已发出035草稿保存，则按原回执恢复，不以UI cancel声明撤销。
- **Calculation Retry**：允许重新计算，生成新的 calculation identity。
- **Commit Retry**：纯生成无生产提交；应用035草稿变更前固化原请求身份/摘要，超时查询原回执，同请求重发不新建草稿。
- **Timeout**：返回生成超时与完成范围；等待结束不代表native已停止，资源按原执行Owner排空。不得无限重试或静默换算法。
- **Process Restart**：依赖 Snapshot/Receipt/Session 恢复；禁止读取 `latest` 猜状态。

## 10. 结果与证据

输出包含声明来源/范围、实际采用的输入引用、生成策略/库版本、局部覆盖基线、完成/未决/覆盖缺口、耗时与可用证据。坐标/单位和图像EvidenceRef按实际用途携带；缺坐标的身份候选仍可存在但不可伪装成已定位目标。本FS的候选完整性不是产品质量状态。

## 11. UI / 操作员工作流

UI012负责共用快速编程，UI020负责AOI针序/极性/焊点细节；两者使用同一生成/库/草稿Owner。已生成、已保存、试检完成、发布分别显示；运行模式不修改当前板程序。


关键操作顺序原则：系统自动带出可确定内容；操作员只处理异常、冲突和必要确认；批量动作先预览影响范围；高级参数渐进披露；每个阻断都有“原因+处理动作+证据”。

## 12. 测试设计

| 测试层 | 覆盖内容 | 必须留存 |
|---|---|---|
| Unit | 核心算法/规则、边界输入、单位/坐标、纯函数 | 输入快照、输出、expected/actual |
| Contract | Schema、状态、Owner、版本兼容 | validator report |
| Integration | 真实 consumer、Pipeline、Evidence | trace + receipt |
| Golden/Replay | 正常/边界/难例/拒识 | dataset hash + result diff |
| PerformanceProfile | `PF-FS-056` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
3. DEV-DOM-057A
4. FS-056 本文
5. Contract/Schema refs registered for this capability
6. State/Owner/AuthorityScope rules
7. UI-PCS-012 (when UI is present)
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
| Function | `FS-056` / `CAD/PnP target generation` |
| Domain | `AOI` |
| Guide | `DEV-DOM-057A` |
| Input | `BOM/PnP/Library/Image` |
| Output | `Draft TargetSet + unresolved items` |
| Result semantic | `Draft candidates / provenance / coverage gaps` |
| Canonical port | `ICADPnPTargetGeneration` |
| Project | `Asun.Domain.Aoi` |
| UI PageContract | `UI-PCS-012` |
| Primary Work Package | `WP-19` |
| Algorithm baseline | `reference binding + target synthesis` |
| Performance gate | `batch candidate + P95` |
| Test baseline | `Golden + Contract + Integration + Fault + Performance` |

### 16.1 Preconditions

- declared available inputs are version/hash identifiable; absent optional/partial sources remain explicit and are not silently substituted;
- scope and authority are compatible;
- coordinate/unit/calibration conditions hold for each instantiated target; unresolved identity-only candidates cannot be treated as located targets;
- method applicability is evaluated against actual obligations; unsupported/hidden features remain coverage gaps, not removed requirements;
- historical retired references may be read under current permission; new selection/publication follows the approved retirement policy;
- each available input has provenance; missing inputs remain explicit and cannot be used to claim complete production coverage.

### 16.2 Postconditions

- output semantics are typed and versioned;
- quality state is explicit;
- provenance is retained;
- no unauthorized production side effect was performed;
- failed quality gates cannot be represented as authoritative OK.

### 16.3 Algorithm decision matrix

| Route | Candidate | Selection / trigger |
|---|---|---|
| Primary | `reference binding + target synthesis` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `Explicit source hierarchy from SourceSetManifest` | Fallback to another source only when it is declared Present/Valid and the mapping policy allows it; never silently substitute. |
| Reject / Block | `Ambiguous mapping, missing source, incompatible board revision, target outside coverage.` | 对受影响目标/方法保留未决与原因；完整性不足阻发布，已知域仍可生成工程候选。 |

**本 FS 的 fallback 不是“另写一个算法看看”。任何替代路线都必须来自当前 Development Guide / Operator Decision Matrix / Qualification 已登记的候选集合。**

### 16.4 Parameter authority matrix

| Parameter class | Authority/source | Hard rule |
|---|---|---|
| Target/ROI | `from fixed manufacturing/assembly intent and typed generation policy` | image-only candidates retain their role; no invented complete target universe |
| Coordinate/Unit | `from CoordinateGraph/Calibration/Manufacturing reference` | must be explicit; mismatch blocks |
| Algorithm parameters | `Recipe/Method configuration version` | no hidden constants in code |
| Thresholds | `approved library/recipe/qualification` | quality tolerances are not inferred from images or tuned to maximize trial pass rate |
| Fallback policy | `FunctionSpec decision table` | no automatic semantic downgrade |
| Performance budget | `batch candidate + P95` | 由 PerformanceProfile 绑定；至少记录 P50/P95/P99、峰值内存、并发安全和取消延迟；未实测不得声称 Qualified |

## 17. Robustness challenge set

At minimum, the function must be challenged against:
- `缺 BOM`
- `库缺项`
- `坐标系冲突`
- `料号替换歧义`

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
| `Ready` | the declared full/partial engineering scope is processable | generate candidates and explicit missing items; not production Ready |
| `Blocked` | the requested scope cannot proceed due to required input/capability/authority | locate the affected scope; keep independent permitted engineering work available |
| `RecoverableError` | execution failed but restart/retry may be valid | retain evidence; follow retry policy |
| `Invalid/Rejected` | result cannot be trusted or is out-of-domain | no quality pass |
| `Completed` | candidate set and missing/coverage report returned | generation ended; neither saved nor qualified by implication |

Only approved Application/Domain services may create production facts or machine-authoritative commands. UI and ViewModel are projections and command clients, not fact authorities.

## 19. Data/provenance and evidence mapping

```text
BOM/PnP/Library/Image
  → input snapshot/reference
  → CAD/PnP target generation computation
  → quality gate
  → Draft candidates / provenance / coverage gaps
  → EvidenceRef / Replay reference
  → downstream consumer
```

**Trace requirements**
- Trace correlation, generation identity and the original draft-apply request identity have different purposes. The latter must survive retries; it is not merely a log label and is not a BoardRun/production FactId.
- Every candidate binds source set, assembly intent/scope, library closure, generation policy, coordinate/calibration where used, local overlay/baseline and completion/missing lists. Trial inspection separately records its actual execution manifest and samples.
- Replay must reconstruct the same semantic result or emit a documented non-determinism reason; “different because code changed” is not an acceptable replay explanation without version comparison.


## 20. Performance engineering contract

The implementation must benchmark:

| Dimension | Requirement |
|---|---|
| Latency | report P50/P95/P99; do not report only average |
| Throughput | benchmark source reconciliation and candidate generation separately from trial inspection and human/approval waiting |
| Memory | peak and steady-state; include large image/3D buffers |
| Queue | bounded queue length and defined backpressure |
| Parallelism | define safe concurrency and non-thread-safe resources |
| Cancellation | report request-to-stop separately from actual native drain and resource return |
| Recovery | restart/resume cost and duplicate-side-effect prevention |
| UI | interaction remains responsive; heavy compute stays off UI thread |

No performance number is considered “qualified” until measured on the target runtime/hardware or an explicitly approved equivalent profile.

## 21. Code artifacts and exact task slices

| Artifact | Canonical location | Responsibility |
|---|---|---|
| Port/interface | `ICADPnPTargetGeneration` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `CADPnPTargetGeneration.cs` | Pipeline/algorithm implementation |
| Validator | `CADPnPTargetGenerationValidator.cs` | Input/precondition/quality checks |
| Tests | `CADPnPTargetGenerationTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-056/` | fixed datasets, expected outputs, provenance |
| Benchmark | `CADPnPTargetGenerationBenchmark.cs` | P50/P95/P99/resource evidence |
| UI | `src/Asun.UI.Workspaces/UI-PCS-012/` | projection only; no production fact write |


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
| T56-01 | 同名/同value不同MPN，Panel-A/R1与Panel-B/R1，重复位号冲突；不误合并且有来源行 | fixed input + exact expected disposition/provenance + recovery trace; planned, not executed |
| T56-02 | PnP过滤DNP/通孔但BOM仍含项；缺行不推不装，全集未知不报100% | fixed input + exact expected disposition/provenance + recovery trace; planned, not executed |
| T56-03 | 固定来源/库/覆盖重跑，行排序改变不改身份；旧修订人工锁和覆盖来源保留 | fixed input + exact expected disposition/provenance + recovery trace; planned, not executed |
| T56-04 | 生成取消、CAS冲突、保存回执丢失/重启；旧候选不覆写，原请求恢复 | fixed input + exact expected disposition/provenance + recovery trace; planned, not executed |
| T56-05 | 大拼板/大候选库/变体集及冷暖缓存；P95/P99、峰值字节和截断完整性报告 | fixed input + exact expected disposition/provenance + recovery trace; planned, not executed |
| T56-06 | AOI纯生成→034→035新草稿→试检→覆盖/审批；FS自身不写事实或激活 | fixed input + exact expected disposition/provenance + recovery trace; planned, not executed |
| T56-07 | Pin1反向、底面双镜像、BGA空球位、同pin多pad、隐藏焊接；拒绝错误映射/虚假覆盖 | fixed input + exact expected disposition/provenance + recovery trace; planned, not executed |

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
| Function | `FS-056` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-DOM-057A` | 指导文档是实施语义权威。 |
| Project | `Asun.Domain.Aoi` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `ICADPnPTargetGeneration` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-012` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `reference binding + target synthesis` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
| SideEffectPolicy | `none; 无副作用；本功能不得直接写入生产事实、设备状态、放行状态或外部控制副作用。` | 冻结策略；任何未批准副作用路径必须 Blocker。 |
| Performance focus | `batch candidate + P95` | 未测量前不得声称满足性能。 |

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

- 输入契约：`BOM/PnP/Library/Image`
- 输出契约：`Draft TargetSet + unresolved items`
- 质量语义：Unknown / Invalid / NotApplicable / NotQualified 不得被映射为 OK。
- 证据要求：候选回溯来源/装配意图、库闭包、生成策略、局部覆盖/草稿基线、坐标及范围；试检另绑实际运行清单，不虚构生产BoardRun。

### AI 完成后的强制回报

AI 必须输出：变更文件清单、对应 FS 条目、Contract/Schema 变更、测试、Benchmark、未关闭风险、未验证 API、禁止路径复核结果。未能证明的内容必须标记 `Unverified`，不得写成 `Completed`。

## 27. Function-specific deterministic freeze profile

| Item | Frozen implementation rule |
|---|---|
| Function class | `AOI Target Synthesis` |
| Primary algorithm/route | `reference binding + target synthesis` |
| Fallback | `Explicit source hierarchy from SourceSetManifest` |
| Fallback trigger | Fallback to another source only when it is declared Present/Valid and the mapping policy allows it; never silently substitute. |
| Reject/Block | Ambiguous mapping, missing source, incompatible board revision, target outside coverage; affected scope remains explicit, partial engineering candidates do not imply publishable completeness. |
| Parameter authority | `['SourceSetManifestId', 'MappingPolicyId', 'TargetSynthesisPolicyId']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | Draft TargetSet + unresolved items + input snapshot + algorithm/parameter version + quality-gate outcome |
| UI rule | PageContract may project and command; it must not create/modify the underlying fact directly. |
| Performance | `batch candidate + P95`; target values come only from the applicable PerformanceProfile. |
| External API | 具体调用先查目标版本官方文档与公共签名；不验证AsunImage/DevExpress依赖、兼容性或授权，项目自身行为按功能验收。 |
| Unknown | Any unverified field/API/parameter/owner/state is `Blocker` or `Unverified`; never guessed. |
| ScopeDrift | `none` | Any work outside the current FS/File Scope requires a change proposal before implementation. |

### 27.1 Required test cases

1. **Nominal:** representative Golden input produces the expected typed output and provenance.
2. **Boundary:** each acceptance/reject threshold boundary is exercised.
3. **Adversarial:** the rejection/fallback trigger in this profile is deliberately injected.
4. **Recovery:** restart/cancel/timeout/duplicate behavior follows the stated state and identity rules.
5. **Replay:** the same source/assembly scope + exact library closure + policy + overlay/baseline reproduces candidate semantics; trial execution has its own evidence closure.

### 27.2 AI stop condition

AI must stop before editing code when any value in this profile is unavailable from an authoritative source. The absence of a numeric threshold does **not** authorize the AI to invent one; it means the task must bind the applicable versioned PerformanceProfile / Recipe / Qualification asset first.

## 26. Implementation status

当前仍为DocMapped，按057A细化了生成语义和拟验收；原ImplementationSpecificationReady标签不作为本轮准入。原Project/Port/Page绑定保留兼容映射，精确合同与实际代码根仍由GATE-001采纳。软件、真实WPF、工业样本和性能没有因本次文档修改自动通过。


### 27.3 ScopeDrift stop condition

`ScopeDrift` is required to remain `none`. A request to add a new object, field, state, Owner, algorithm route, page command, external API or file outside this FS is not an implementation detail; it is a change candidate and must stop the current task until approved and re-indexed.
