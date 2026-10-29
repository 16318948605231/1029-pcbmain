# OCR/marking

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-061`
- 类型：`Function Implementation Specification`
- 版本：`1.3.1-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-DOM-057B`
- 领域：`AOI`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

对丝印/激光字符等进行候选识别，低置信度必须进入人工复判。

**不负责：** 生产机判、最终处置、真实设备安全功能。

## 2. 权威与契约

输入语义：标记ROI、批准文本/变量规则、字符模型和图像质量。输出语义：识别文字/差异/置信或拒识；不自动纠正为预期值。以上明确本功能边界，不是新DTO/Schema；精确字段按GATE-001与对应既有ContractCandidate逐项采纳。

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

1. 应用固定元件/子槽位、面/尝试、独立位姿、必检集合与期待来源；期待读数不进入共享识别请求的纠正/几何费用。
2. 经024/007/020准备有来源和完整支持的单词ROI；独立紧裁直接识读，检测路线先完成[057B §10.1](<../06-domains/DEV-DOM-057B_AOI Component Pin Lead Polarity OCR开发指导.md#aoi-ocr-geometry-consumption>)规定的候选/关联，未决保留原目标。
3. 024按冻结模型/有序字符表与预处理执行并恢复输入→词→批次身份；方向处理属于具名输入方法，不能在结果后按期待串试到匹配为止。
4. 保留引擎原读、score原语义、输入/裁图/模型与坐标证据；模型mapping或业务规范化另存派生值及规则，不覆盖原读，不默认trim、大小写变换、NFC或O→0。
5. 应用按原固定槽位组合、期待来源和比较规则独立评价文字、字形/极性与必检完整性；低分/冲突按原复判策略处理，合法空读、未执行和无效支持分别表达。
6. 由原结果/证据Owner返回或提交各阶段结果；Unknown回查原操作，迟到结果不能覆盖新板。UI只投影，识出正确字符串不等于字形或质量通过。

## 5. 算法/规则设计

**实施分类：** `AOI OCR`

**Primary route：** `OCR candidate + confidence/review`

**Fallback route：** `Approved OCR candidate → Review on low confidence`

**Fallback trigger：** Fallback may use an alternate OCR mode/model only if the MarkingSpec authorizes it; unreadable required marks never become PASS.

**Reject / Block conditions：** Unreadable glyphs, conflicting strings, confidence below gate, charset mismatch.

**历史参数键候选（按§28绑定指定模型/score语义；正式字段与数值由原 Contract / Profile / Recipe / Qualification 采纳）：** `['OcrProfileId', 'MinConfidence', 'AllowedCharset', 'ReviewBand']`

**结果语义：** `OCR candidate + image evidence`

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| 低对比 | 注入/回放 低对比 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 污渍 | 注入/回放 污渍 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 字符断裂 | 注入/回放 字符断裂 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |
| 相似字符 | 注入/回放 相似字符 | 显式质量状态；必要时 Reject/Review，不得静默 PASS |

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

UI/工作区：AOI workbench。交互遵循“状态→对象→结果→下一动作”；任何生产配置修改必须 Draft→Validate→Approve→Release；异常必须一键定位到证据。


关键操作顺序原则：系统自动带出可确定内容；操作员只处理异常、冲突和必要确认；批量动作先预览影响范围；高级参数渐进披露；每个阻断都有“原因+处理动作+证据”。

## 12. 测试设计

| 测试层 | 覆盖内容 | 必须留存 |
|---|---|---|
| Unit | 核心算法/规则、边界输入、单位/坐标、纯函数 | 输入快照、输出、expected/actual |
| Contract | Schema、状态、Owner、版本兼容 | validator report |
| Integration | 真实 consumer、Pipeline、Evidence | trace + receipt |
| Golden/Replay | 正常/边界/难例/拒识 | dataset hash + result diff |
| PerformanceProfile | `PF-FS-061` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
3. DEV-DOM-057B
4. FS-061 本文
5. Contract/Schema refs registered for this capability
6. State/Owner/AuthorityScope rules
7. UI-PCS-020 (when UI is present)
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
| Function | `FS-061` / `OCR/marking` |
| Domain | `AOI` |
| Guide | `DEV-DOM-057B` |
| Input | `BOM/PnP/Library/Image` |
| Output | `AOI facts/review/rework` |
| Result semantic | `Domain InspectionFact / MeasurementSet / ReviewCandidate` |
| Canonical port | `IOCRMarking` |
| Project | `Asun.Domain.Aoi` |
| UI PageContract | `UI-PCS-020` |
| Primary Work Package | `WP-19` |
| Algorithm baseline | `OCR candidate + confidence/review` |
| Performance gate | `batch candidate + P95` |
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
| Primary | `OCR candidate + confidence/review` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `Approved OCR candidate → Review on low confidence` | Fallback may use an alternate OCR mode/model only if the MarkingSpec authorizes it; unreadable required marks never become PASS. |
| Reject / Block | `Unreadable glyphs, conflicting strings, confidence below gate, charset mismatch.` | 保留证据与原因；不得生成权威 OK。 |

**本 FS 的 fallback 不是“另写一个算法看看”。任何替代路线都必须来自当前 Development Guide / Operator Decision Matrix / Qualification 已登记的候选集合。**

### 16.4 Parameter authority matrix

| Parameter class | Authority/source | Hard rule |
|---|---|---|
| Target/ROI | `from approved target set or runtime binding` | never guessed from image unless the FS explicitly allows auto-targeting |
| Coordinate/Unit | `from CoordinateGraph/Calibration/Manufacturing reference` | must be explicit; mismatch blocks |
| Algorithm parameters | `Recipe/Method configuration version` | no hidden constants in code |
| Thresholds | `approved library/recipe/qualification` | AI may propose only as draft unless qualification says otherwise |
| Fallback policy | `FunctionSpec decision table` | no automatic semantic downgrade |
| Performance budget | `batch candidate + P95` | 由 PerformanceProfile 绑定；至少记录 P50/P95/P99、峰值内存、并发安全和取消延迟；未实测不得声称 Qualified |

## 17. Robustness challenge set

At minimum, the function must be challenged against:
- `低对比`
- `污渍`
- `字符断裂`
- `相似字符`

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
BOM/PnP/Library/Image
  → input snapshot/reference
  → OCR/marking computation
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
| Port/interface | `IOCRMarking` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `OCRMarking.cs` | Pipeline/algorithm implementation |
| Validator | `OCRMarkingValidator.cs` | Input/precondition/quality checks |
| Tests | `OCRMarkingTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-061/` | fixed datasets, expected outputs, provenance |
| Benchmark | `OCRMarkingBenchmark.cs` | P50/P95/P99/resource evidence |
| UI | `src/Asun.UI.Workspaces/UI-PCS-020/` | projection only; no production fact write |


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
| T61-01 | contract/schema validation | expected assertion + evidence + trace; no silent pass |
| T61-02 | normal + boundary + reject | expected assertion + evidence + trace; no silent pass |
| T61-03 | replay/golden dataset | expected assertion + evidence + trace; no silent pass |
| T61-04 | fault injection | expected assertion + evidence + trace; no silent pass |
| T61-05 | performance benchmark | expected assertion + evidence + trace; no silent pass |
| T61-06 | real domain consumer | expected assertion + evidence + trace; no silent pass |
| T61-07 | hard-negative/false-positive set | expected assertion + evidence + trace; no silent pass |

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
| Function | `FS-061` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-DOM-057B` | 指导文档是实施语义权威。 |
| Project | `Asun.Domain.Aoi` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `IOCRMarking` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-020` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `OCR candidate + confidence/review` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
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
- 输出契约：`AOI facts/review/rework`
- 质量语义：Unknown / Invalid / NotApplicable / NotQualified 不得被映射为 OK。
- 证据要求：结果必须能够回溯到输入快照、RuntimeManifest、算法/规则版本、关键参数、坐标/标定引用和执行时间。

### AI 完成后的强制回报

AI 必须输出：变更文件清单、对应 FS 条目、Contract/Schema 变更、测试、Benchmark、未关闭风险、未验证 API、禁止路径复核结果。未能证明的内容必须标记 `Unverified`，不得写成 `Completed`。

## 27. Function-specific deterministic freeze profile

| Item | Frozen implementation rule |
|---|---|
| Function class | `AOI OCR` |
| Primary algorithm/route | `OCR candidate + confidence/review` |
| Fallback | `Approved OCR candidate → Review on low confidence` |
| Fallback trigger | Fallback may use an alternate OCR mode/model only if the MarkingSpec authorizes it; unreadable required marks never become PASS. |
| Reject/Block | Unreadable glyphs, conflicting strings, confidence below gate, charset mismatch. |
| Parameter authority | `['OcrProfileId', 'MinConfidence', 'AllowedCharset', 'ReviewBand']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | OCR candidate + image evidence + input snapshot + algorithm/parameter version + quality-gate outcome |
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
5. **Replay:** the same input snapshot + RuntimeManifest + parameter/model versions reproduces the same semantic result or records an approved non-determinism reason.

### 27.2 AI stop condition

AI must stop before editing code when any value in this profile is unavailable from an authoritative source. The absence of a numeric threshold does **not** authorize the AI to invent one; it means the task must bind the applicable versioned PerformanceProfile / Recipe / Qualification asset first.

## 26. Implementation status

`ImplementationSpecificationReady` means the documentary implementation contract is complete within the current architecture scope. It does **not** assert that target hardware, real Golden data, HIL, calibration qualification, production thresholds, or external interoperability have been experimentally qualified.


### 27.3 ScopeDrift stop condition

`ScopeDrift` is required to remain `none`. A request to add a new object, field, state, Owner, algorithm route, page command, external API or file outside this FS is not an implementation detail; it is a change candidate and must stop the current task until approved and re-indexed.


## 28. 通用OCR与AOI应用组合的分工

本FS保留AOI元件标记、期待字段、领域规则和复判编排；§16历史项目/端口不是要求AOI重新实现OCR。识别算法与可选文字控件引用SM-011独立Text包；唯一专项见[DEV-VIS-021A](../../../shared-modules/guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md)。HALCON传统/Deep OCR优先，PaddleOCR为需实测的固定候选；新共享公共签名需原C契约采纳，不把IOCRMarking直接当跨制程视觉底层端口。

§5/§27的MinConfidence只在指定模型和score语义下有意义，禁止复用一个阈值比较Deep OCR字符softmax、传统分类置信与Paddle行均分；AllowedCharset不授权自动O→0或把字符删除。正式方法参数新增/变更按原契约修订。输入BOM/PnP不是每个纯OCR调用的必需参数，而是AOI应用组合上下文；原读/ROI/质量来自共享库，工单期待及评价由应用Owner处理。

AOI补充断言：相邻元件词框不能串目标；炉前模板不能默认适用炉后变色丝印；识出正确料号但字形损伤仍有独立候选；双后端不同读数不能挑期待匹配者；拒识不得当元件缺失；人工录入不覆盖原读。快速编程与公共控件按专项§8/9接入，恢复按§10；本轮未运行OCR或产品验收。

<a id="ocr-marking-method-binding"></a>
### 28.1 当前实施方法与退出断言

§16/21/25的旧端口/代码根/名称冻结描述仍按§28作为AOI应用的历史候选；不能据它们跳过当前C采纳或在AOI另造识别核心。正常步骤以上述§4为准；算法参数实际含义来自选定模型/方法，旧`MinConfidence`并非跨后端统一概率。

| AOI应用需要完成的部分 | 唯一实施位置和验收断言 |
|---|---|
| 返回、索引与原读 | [021A §15](../../../shared-modules/guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md#ocr-decoding-association-method)归024。A无字B有字、按长宽比重排与低分过滤后，B仍只绑定B；原ABB不得覆盖为期待AB8 |
| 几何、分块与应用关联 | [021A §16](../../../shared-modules/guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md#ocr-external-geometry-tiling-method)及057B §10.1。024整理候选，应用建图调062；两目标一词同费用或替代检查取消保持未决，三必检一完成仍为1/3 |
| 固定多行与领域比较 | [057B](<../06-domains/DEV-DOM-057B_AOI Component Pin Lead Polarity OCR开发指导.md#aoi-ocr-geometry-consumption>)保留槽位/分隔符及原词，缺一行不借邻件补位；正确MPN不消除极性/缺笔疑问，替代料仍为完整规则组 |
| 训练与离线评价 | [060](../../../shared-modules/guidance/07-ai/DEV-AI-060_AI运行治理开发指导.md#ai-training-export-method)和[063](../../../shared-modules/guidance/07-ai/DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md#ocr-text-evaluation-method)归053。FS不实现训练循环或CER核；合法空读与缺项分开，文字对齐不作字形定位证据 |
| 未来代码切片 | [014 §44](../../../09-development-plan/DEV-PLAN-014_全量研发工作包与并行依赖DAG.md#ocr-decoding-development-slices)、[§45](../../../09-development-plan/DEV-PLAN-014_全量研发工作包与并行依赖DAG.md#training-text-evaluation-development-slices)、[§46](../../../09-development-plan/DEV-PLAN-014_全量研发工作包与并行依赖DAG.md#ocr-geometry-tiling-development-slices)。共享024/062及合同各单Owner，两工艺应用文件可并行；无正式签名时不凭本表造DTO |

本节细化原T61-02/03/04/06等验收输入，不声称已经执行。所选后端Golden、模型/字典及支持资格、实际WPF和同条件工业对标继续独立验收；正文接通方法导航不把DocMapped升级为ImplementationReady。
