# Disposition projection

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-066`
- 类型：`Function Implementation Specification`
- 版本：`1.2.0`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-AI-063`
- 领域：`Quality/AI`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

从已提交结果、人工意见及原处置记录投影当前可见状态、来源和缺口。质量计划用于解释所需证据；本功能不重算机判、不独立批准质量处置。

**不负责：** 产生或修改生产质量事实、人工意见、正式处置、设备授权和安全状态。

## 2. 权威与契约

输入语义：精确已提交事实/回执、质量计划/选择策略、权威处置记录及受权查询水位；输出为只读处置/缺口投影，不是待自动提交的质量决定。精确字段进入既有ContractCandidate，不在本目录新建Schema或数据库模型。原DEV-AI-063绑定只保留数据/真值关系；实际复判/处置交接按[DEV-DOM-057D §4](<../../../process-guides/guidance/06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md#4-人工意见质量处置与物理动作>)，不能把人工意见自动当GroundTruth或最终放行。

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

核当前主体/用途/对象访问范围，固定板/面/工序/尝试及查询时点、原事实修订、质量计划和选择策略。原NG、缺证据、待复判、旧程序撤回都是可能需要展示的内容，不能因不满足算法质量门而从页面消失。

拒绝错对象、同身份异hash及不允许的读取；对尚未取得/不可访问的内容只显示政策允许的缺口或不可判定提示，不能将权限过滤后的空集合解释为没有质量问题。单位/坐标只随引用量测/几何解释，不要求每个处置投影具备制造几何或有效相机标定。

## 4. 正常执行流程

1. 解析授权查询范围并固定所需快照/水位。已发生处置的历史输入与本次查询到的后续意见分别读取。
2. 按唯一事实/意见Owner的有效前序和选择规则关联记录；不能按到达时间取最后一条，不从当前筛选列表推定必审全集。
3. 沿质量计划解析所需证据，只生成存在、缺失、不可判定及来源解释；正式路线评估/处置仍读取原Owner结果。若允许what-if评价，标为候选用途并隔离，不充当已签发处置。
4. 分别显示原机判、人工必审闭合、处置已提交、动作接收、实际离站；没有回执的阶段保持未知。当前质量更正可以晚于历史离站，不倒写原路由。
5. UI原子替换一个已完成构建的投影；点击复判/处置只导航原应用入口，重新核当前条件。本投影不签发授权，不重放设备命令。

多个来源的修订号属于不同版本域，不能取一个`max`就宣称全部已追平。若Owner提供共同一致切点，按其协议读取；否则记录各来源水位和关联缺口，以未同步投影展示，不伪装成同一全局快照。Watch/事件只是刷新提示，不能替代权威查询或消除读后更新窗口。

## 5. 算法/规则设计

**实施分类：** `Quality Projection`

**Primary route：** `committed facts + quality plan`

**Fallback route：** `No fallback to recomputed facts`

**Fallback trigger：** When required committed facts are stale/missing, project a gated/incomplete state and expose the gap.

**Reject / Block conditions：** Wrong identity/hash or unauthorized read rejects the request. Missing/stale facts or conflicting plan produce an explicit incomplete projection; an uncommitted candidate cannot substitute for a fact.

**既有候选参数键（原合同采纳后固定）：** `['QualityPlanRevisionId', 'FactWatermarkId', 'StalenessPolicyId']`；不同来源的水位不能因名称单数而合成一个序号。

**结果语义：** `Disposition projection + gap evidence`

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| 迟到 | 原板已离站，后续更正到达；旧页面请求再晚到 | 历史处置/路由保持，新增意见可追溯；旧选择结果丢弃，不发反向运动 |
| 证据缺口 | 必需3项只读到2项，或不同来源水位尚不相容 | 缺项/未同步可见，不按可见2项全通过推定整体合格 |
| 权限限制 | 当前用户只能读取部分项，缓存来自更高权限主体 | 缓存不得越权复用；受限内容与计数按策略裁剪，不谎报零缺陷 |

## 7. 投影完整性与可见范围

只读投影核来源身份、读取权限、版本/前序关联及水位一致性。原NG/Invalid可以正常展示；投影构建成功不表示产品合格。缺失、不可访问、尚未同步与原Owner明确不适用分别保留，不能因空列表或所有可见行通过而显示整板通过。

原正式处置已存在时显示其原输入及回执；新意见尚未被处置Owner采纳时显示“后续记录待处理”，不由本功能擅自替换。历史资格撤回的后果按原政策展示，不抹除当时确已发生的事实。

## 8. 性能与资源

查询、聚合、统计和 AI 检索均必须限制时间窗口/分母/数据水位并提供分页/缓存策略；统计不可阻塞生产事实提交。

性能采集点必须至少覆盖：输入准备、核心计算、质量评估、序列化/提交（如有）、UI 投影（如有）。高峰资源与长尾单独报告，不以平均耗时掩盖 P99。

## 9. 并发、取消、重试与恢复

- **Cancel**：取消尚未产生生产副作用的计算；已提交事实不可因 UI cancel 回滚。
- **Projection refresh**：按请求选择代重新查询/构建只读投影；不是新的检测尝试或质量决定。
- **Commit**：本功能无生产事实/处置提交；可再生缓存不能成为权威Store。其它动作仅导航其原应用端口及恢复协议。
- **Timeout**：保留有权显示的旧投影并标水位/陈旧，或显示读取失败；不把读超时转成产品NG或自动隔离命令。
- **Process Restart**：重新取得授权范围与明确查询基准；旧缓存先按权限/版本核验，迟到旧请求不能覆盖新选择。历史固定查询与当前刷新明确区分。

## 10. 结果与证据

输出绑定读取范围、各来源精确引用/修订/水位、质量计划/选择策略、投影版本/用途、缺口及原处置/动作回执。引用量测时保留原单位/资格；不为纯状态显示伪造算法、标定或量值。盲审/跨客户受限信息不能由计数、原因、导出或缓存泄露。

## 11. UI / 操作员工作流

UI/工作区：quality/AI workspace。交互遵循“状态→对象→结果→下一动作”；任何生产配置修改必须 Draft→Validate→Approve→Release；异常必须一键定位到证据。


关键操作顺序原则：系统自动带出可确定内容；操作员只处理异常、冲突和必要确认；批量动作先预览影响范围；高级参数渐进披露；每个阻断都有“原因+处理动作+证据”。

## 12. 测试设计

| 测试层 | 覆盖内容 | 必须留存 |
|---|---|---|
| Unit | 身份/前序关联、必需集合、来源水位与纯投影解释 | 固定输入、预期缺口/来源、expected/actual |
| Contract | Schema、状态、Owner、版本兼容 | validator report |
| Integration | 真实 consumer、Pipeline、Evidence | trace + receipt |
| Golden/Replay | 正常/边界/难例/拒识 | dataset hash + result diff |
| PerformanceProfile | `PF-FS-066` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
3. DEV-AI-063
4. FS-066 本文
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
| Function | `FS-066` / `Disposition projection` |
| Domain | `Quality/AI` |
| Guide | `DEV-AI-063` |
| Input | `committed facts/receipts + plan/selection policy + source watermarks + read scope` |
| Output | `read-only disposition/gap projection` |
| Result semantic | `source-bound projection; no decision or route authority` |
| Canonical port | `IDispositionProjection` |
| Project | `Asun.Domain.Quality` |
| UI PageContract | `UI-PCS-021` |
| Primary Work Package | `WP-20` |
| Algorithm baseline | `committed facts + quality plan` |
| Performance gate | `batch latency` |
| Test baseline | `Golden + Contract + Integration + Fault + Performance` |

### 16.1 Preconditions

- the requested object scope and query policy are identifiable; source references are validated when present and missing sources remain explicit;
- scope and authority are compatible;
- coordinate/unit/calibration conditions are satisfied where relevant;
- source selection and plan are explicit; no current UI filter substitutes for the required set;
- historical withdrawn/replaced references remain readable where current access policy permits;
- missing/inaccessible evidence is projected as an explicit gap, not removed from the population.

### 16.2 Postconditions

- output semantics are typed and versioned;
- quality state is explicit;
- provenance is retained;
- no unauthorized production side effect was performed;
- failed quality gates cannot be represented as authoritative OK.

### 16.3 Algorithm decision matrix

| Route | Candidate | Selection / trigger |
|---|---|---|
| Primary | `committed facts + quality plan` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `No fallback to recomputed facts` | When required committed facts are stale/missing, project a gated/incomplete state and expose the gap. |
| Reject / Block | `Wrong identity/hash or unauthorized read rejects the request. Missing/stale facts or conflicting plan produce an explicit incomplete projection; an uncommitted candidate cannot substitute for a fact.` | 保留证据与原因；不得生成权威 OK。 |

**本 FS 的 fallback 不是“另写一个算法看看”。任何替代路线都必须来自当前 Development Guide / Operator Decision Matrix / Qualification 已登记的候选集合。**

### 16.4 Parameter authority matrix

| Parameter class | Authority/source | Hard rule |
|---|---|---|
| Object/required set | `source identity + frozen plan/selection policy` | no barcode-only join or visible-row denominator |
| Source watermarks | `each authoritative source or its approved common cut` | no max across unrelated revisions; no Watch-based authority |
| Display interpretation | `original committed assessment/disposition + projection policy` | no second quality decision |
| Access/staleness | `current read authorization + approved staleness policy` | caches and exports preserve scope; no automatic device response |
| Fallback policy | `FunctionSpec decision table` | no automatic semantic downgrade |
| Performance budget | `batch latency` | 由 PerformanceProfile 绑定；至少记录 P50/P95/P99、峰值内存、并发安全和取消延迟；未实测不得声称 Qualified |

## 17. Robustness challenge set

At minimum, the function must be challenged against:
- `迟到`
- `证据缺口`
- `权限限制`

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

## 18. 投影展示状态与副作用边界

| State | Entry condition | Allowed behavior |
|---|---|---|
| `Ready` | 当前范围可查询/查看 | NG、待复判、缺证据均可展示，不代表已放行 |
| `Blocked` | 无法解释部分来源/计划 | 给出受影响范围；保留其它有权内容及缺口 |
| `RecoverableError` | 查询失败 | 按原范围恢复或标旧投影陈旧，不发设备命令 |
| `Invalid/Rejected` | 查询请求错对象/无权/同身份异hash | 明确拒绝原因；不能伪造产品质量状态 |
| `Completed` | 本次只读投影构建完成 | 来源和水位可见；不等于检测、复判或出板完成 |

这些是页面/查询分类，不新增生产状态机。正式处置、人工意见与设备回执各从原Owner投影。

Only approved Application/Domain services may create production facts or machine-authoritative commands. UI and ViewModel are projections and command clients, not fact authorities.

## 19. Data/provenance and evidence mapping

```text
committed result/review/disposition/action receipts
  → authorized source selection + per-source watermarks
  → identity/predecessor/required-set association
  → read-only projection with gaps and original sources
  → UI/report; navigation to original command owner
```

**Trace requirements**
- `operationId` is trace identity only; it is not FactId, CommitIdentity, or BoardIdentity.
- 投影可回溯各来源修订/水位、原计划/选择策略、读取范围与构建版本；机器RuntimeManifest/算法/标定按原证据关联，不复制新生产谱系。
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
| Port/interface | `IDispositionProjection` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `DispositionProjection.cs` | 受权读取、来源关联、缺口解释及不可变投影构建 |
| Validator | `DispositionProjectionValidator.cs` | Input/precondition/quality checks |
| Tests | `DispositionProjectionTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-066/` | fixed datasets, expected outputs, provenance |
| Benchmark | `DispositionProjectionBenchmark.cs` | P50/P95/P99/resource evidence |
| UI | `src/Asun.UI.Workspaces/UI-PCS-021/` | projection only; no production fact write |


**Implementation order**
1. contract/port and validation;
2. authorized queries, source association and immutable projection construction;
3. missing/stale/inaccessible source semantics and historical disposition separation;
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
| T66-01 | 原身份/修订/水位/读权限合同 | 错板面、同身份异hash拒绝；缺记录形成缺口，不造事实 |
| T66-02 | 原NG＋人工意见＋历史处置＋新更正 | 五阶段来源分别可查，新意见不覆盖离站回执 |
| T66-03 | 固定来源重建投影 | 同快照/策略/可见范围同语义；当前权限变化不泄漏原缓存 |
| T66-04 | 乱序、断线、不同来源水位、筛选缺项 | 旧选择不回填；不取跨来源max；不把已读集合当必需全集 |
| T66-05 | 大母体查询/构建/刷新/导出 | 固定负载及分页水位，P95/P99与缓存上限按PF-FS-066，生产命令增量0 |

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
| Function | `FS-066` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-AI-063` | 指导文档是实施语义权威。 |
| Project | `Asun.Domain.Quality` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `IDispositionProjection` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-021` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `committed facts + quality plan` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
| SideEffectPolicy | `quality fact/decision projection or approved evaluation；质量投影不得成为第二事实权威；评价只能在批准的策略范围内执行。` | 冻结策略；任何未批准副作用路径必须 Blocker。 |
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

- 输入契约：`committed facts/receipts + plan/selection policy + source watermarks + read scope`
- 输出契约：`read-only disposition/gap projection`
- 质量语义：Unknown / Invalid / NotApplicable / NotQualified 不得被映射为 OK。
- 证据要求：保留原事实/意见/处置/动作回执、各来源水位、选择策略及缺口，不要求纯投影具备虚构算法或标定。

### AI 完成后的强制回报

AI 必须输出：变更文件清单、对应 FS 条目、Contract/Schema 变更、测试、Benchmark、未关闭风险、未验证 API、禁止路径复核结果。未能证明的内容必须标记 `Unverified`，不得写成 `Completed`。

## 27. Function-specific deterministic freeze profile

| Item | Frozen implementation rule |
|---|---|
| Function class | `Quality Projection` |
| Primary algorithm/route | `committed facts + quality plan` |
| Fallback | `No fallback to recomputed facts` |
| Fallback trigger | When required committed facts are stale/missing, project a gated/incomplete state and expose the gap. |
| Reject/Block | Wrong identity/hash or unauthorized read rejects the request. Missing/stale facts or conflicting plan produce an explicit incomplete projection; an uncommitted candidate cannot substitute for a fact. |
| Parameter authority | 既有候选键`['QualityPlanRevisionId', 'FactWatermarkId', 'StalenessPolicyId']`沿原合同采纳；实际值来自质量计划、各来源水位和读取/陈旧策略，不从算法配方猜 |
| Result/evidence | Read-only disposition/gap projection + exact source revisions/watermarks + plan/selection policy + read scope |
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
5. **Replay:** 固定各来源快照/策略及模拟读取范围，核投影关联/缺口；当前访问限制变化必须显式处理。无生产事实、处置或设备命令增量。

### 27.2 AI stop condition

AI must stop before editing code when any value in this profile is unavailable from an authoritative source. The absence of a numeric threshold does **not** authorize the AI to invent one; it means the task must bind the applicable versioned PerformanceProfile / Recipe / Qualification asset first.

## 26. Implementation status

`ImplementationSpecificationReady` means the documentary implementation contract is complete within the current architecture scope. It does **not** assert that target hardware, real Golden data, HIL, calibration qualification, production thresholds, or external interoperability have been experimentally qualified.


### 27.3 ScopeDrift stop condition

`ScopeDrift` is required to remain `none`. A request to add a new object, field, state, Owner, algorithm route, page command, external API or file outside this FS is not an implementation detail; it is a change candidate and must stop the current task until approved and re-indexed.

## 人工意见与实体处置的专项边界

本功能投影原Owner的FinalDisposition及已发生动作，不根据“最新人工PASS”自行重建放行。源Claim过期不使此前合法意见消失，新意见仍需044有效Claim/CAS；任务完成、返修实际完成、新实体复检和设备离站分开。已出板质量更正只追加记录，不覆盖历史处置或自动发反向运动；原处置需变更时由正式Owner按当前身份/位置/策略处理。

原/新量测组合须符合返修后覆盖计划；局部PASS不能直接拼旧结果宣布整板PASS。详见[DEV-DOM-057D](<../../../process-guides/guidance/06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md#aoi-review-closure>)及[端到端恢复链](../../../process-guides/END-TO-END-FLOWS.md#review-rework-recovery)。本节不新增状态/处置Owner。

## 仲裁投影的接收约束

仲裁来源按[044 §11](../../packages/PKG-044_Review.md#review-rounds-arbitration)读取确切原意见头、问题/轮次及仲裁回执，显示“本人已审/轮次未完/待仲裁/该问题已解决”的获准语义。投影不得根据赞成数自行运行另一套仲裁规则，也不把旧已提交仲裁改成未发生。新证据/更正造成待处理时保留原历史及当前缺口；服务端盲审裁剪覆盖所有计数/导出，空可见列表不是全板通过。
