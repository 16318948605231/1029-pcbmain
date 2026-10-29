# Review/rework

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。

> 本轮实施要求统一遵循[DEV-GOV-010十二项标准](<../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md>)：HALCON适用能力优先经AsunImage/已有控件；复用功能独立模块；精美DevExpress视觉和交互分别验收。工艺组合/增量按[唯一功能覆盖导航](<../../../09-development-plan/DEV-PLAN-000_开发指导文档地图.md#功能覆盖与实施深度>)读取对应PG实施卡及SM接入节；仅有本文模板和历史端口绑定不足以获得ImplementationReady。

- 文档 ID：`FS-063`
- 类型：`Function Implementation Specification`
- 版本：`1.2.0`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 对应开发指导：`DEV-DOM-057D`
- 领域：`AOI`

> 本文是**代码实施层**标准。它补充平台/领域 Development Guide，目标是让人工开发和 AI 开发在实现该能力时有明确的输入、输出、流程、失败路径、性能、UI、测试和验收边界。
> 
> 精确持久化/传输字段仍必须绑定批准的 Contract/Schema；本文不得创建第二套事实模型。尚不存在的 Contract 以 `ContractCandidate` 标识并进入对应 C-01~C-08 工作包。

## 1. 功能目标与边界

以 evidence-first 工作流进行复判、返修、复验和处置，不修改原始事实。

**不负责：** 生产机判、最终处置、真实设备安全功能。

## 2. 权威与契约

输入语义：已提交机器结果/证据、任务租约/版本、人工权限与返修信息。输出语义：独立人工意见、返修与新尝试关联；不覆盖机器测量/机判或默认放行。以上明确本功能边界，不是新DTO/Schema；精确字段按GATE-001与对应既有ContractCandidate逐项采纳。

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

分别核对读取、草稿、新提交和返修动作的前置条件：读取核当前访问权限与原事实身份；草稿核Case/Item、允许意见及可见证据；新提交再核准确Claim代、期望修订、策略、理由及前序；返修/实体复检走各自领域端口。

缺图、原结果Invalid、旧程序撤回或Claim过期不能一律禁止查看历史。页面应显示实际缺项；哪些意见因证据不足不可提交由固定工艺策略判定。制造几何、坐标/标定只在相应补标或引用量测需要时核对，不为普通文字意见虚构制造参考前置。

## 4. 正常执行流程

1. 按当前用途/权限加载已提交原事实、Case/Item及证据；是否显示原机判、AI或既有人判由盲审策略决定。
2. 领取准确写入范围后录入独立草稿，引用真实证据和允许理由；不因选择意见自动提交。
3. 显式提交按PKG-044的已采纳事务形态追加人工记录，Unknown先查原操作，未发送项不自动续发。
4. 返修实际动作与新实体复检分别接原Owner回执，校验身份/面/尝试/覆盖，不把Replay当实体复检。
5. 人工必审闭合只成为最终处置输入；原处置Owner另核当前条件，意见成功不等于出板。

## 5. 算法/规则设计

**实施分类：** `Review/Rework`

**Primary route：** `evidence-first UI + state machine`

**Fallback route：** `Manual review / approved rework workflow`

**Fallback trigger：** There is no automatic quality fallback. If evidence is insufficient, Review remains unresolved. Rework changes are commands with their own receipt/authorization.

**Reject / Block conditions：** For new writes: unauthorized reviewer, expired claim, required evidence missing or disposition conflict. Historical committed receipts remain queryable under current access authorization.

**既有候选参数键（原合同采纳后固定，数值由批准策略/Profile提供）：** `['ReviewClaimPolicyId', 'ClaimLease', 'DispositionPolicyId']`

**结果语义：** `ReviewDecision + rework/disposition evidence`

本节是该 FS 的功能特定算法/规则入口。不得使用其它 FS 的算法默认、阈值、对象模型或 fallback 替代本功能定义。

## 6. 鲁棒性与异常设计

| 变化/故障源 | 必测处理 | 结果要求 |
|---|---|---|
| 证据缺失 | 当前Item原图缺失，另一Item图迟到 | 显示实际缺图，旧图不替补；保留已提交意见，受影响新意见按策略阻断 |
| 重复复判 | 同键同请求、同键异请求、旧代迟到分别注入 | 前者恢复原回执；异请求冲突；旧代不能追加；合法独立轮次不被错误去重 |
| 返修循环 | 实际返修完成，但新实体复检缺邻域或再次NG | 保留每轮动作/结果，不能选最好一次或旧图Replay关闭问题 |
| 权限不足 | 提交前撤权、提交成功后撤权、旧图晚到分别注入 | 新写按正式授权生效协议处理；历史读核当前访问权；无权内容不重新显示 |

## 7. 新提交准入与历史回执恢复

本功能不是视觉算法重算。新意见核真实已提交来源、当前Claim/代/期望修订、工艺允许意见/理由/证据、前序及权限；返修命令另核实际动作与当前实体条件。无效/缺图项保持未解决，不默认OK。已经提交的合法NG、人工意见或失败返修记录不因当前Claim过期或原算法质量不合格而消失，历史查询仍核当前访问权限。

完整协议唯一在[PKG-044](../../../shared-modules/packages/PKG-044_Review.md#review-transaction-flow)，工艺链在[DEV-DOM-057D](<../06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md#aoi-review-closure>)；不套Input/AlgorithmQualityGate三层模板替代复判权限与事务。

## 8. 性能与资源

分别测队列分页、领取/续租、证据加载、逐项提交/回执查询与关闭释放；3D/大图按需加载且预算有界。等待时间、客户端往返和服务端持久提交分开，Profile按并发站/网络/数据规模冻结。

性能采集点覆盖：资格过滤/分页、Claim事务、证据IO/解码、草稿校验、提交持久化/回执查询及UI投影。高峰资源与长尾单独报告，不以平均耗时掩盖 P99。

## 9. 并发、取消、重试与恢复

- **Cancel**：取消尚未产生生产副作用的计算；已提交事实不可因 UI cancel 回滚。
- **Draft / command recovery**：人工意见不通过计算重试自动再生成；已发送请求查询/恢复原身份，未发送草稿刷新上下文后由人提交。
- **Commit Retry**：先查询已发送原操作；正式协议允许重投时复用其幂等身份和同一请求，不生成新的人工意见。
- **Timeout**：显示客户端等待超时/提交未知，不伪造服务端拒绝或已失败事实；继续查询原回执。
- **Process Restart**：先查已发送原操作/回执；当前Case/Claim从权威端刷新，旧秘密/代不盲复活；不能将当前投影代替原历史回执。

## 10. 结果与证据

输出绑定原Fact/Case/Item、人工意见/理由/主体/前序、策略、操作及持久回执；返修实际动作和新复检引用独立。坐标/单位仅用于所引用量测或补标几何，不给领取/提交伪造算法版本或零量值。

## 11. UI / 操作员工作流

UI/工作区：AOI workbench。交互遵循“状态→对象→结果→下一动作”；任何生产配置修改必须 Draft→Validate→Approve→Release；异常必须一键定位到证据。

Review workspace 默认“证据优先”：原图/适用3D与本任务允许的信息联动。机判/AI/相似案例/他人意见/操作历史仅在当前盲审与访问政策允许时交付；禁止为了默认排版预取被隐藏内容。返修/复验导航不改变原机判。

关键操作顺序原则：系统自动带出可确定内容；操作员只处理异常、冲突和必要确认；批量动作先预览影响范围；高级参数渐进披露；每个阻断都有“原因+处理动作+证据”。

## 12. 测试设计

| 测试层 | 覆盖内容 | 必须留存 |
|---|---|---|
| Unit | 意见资格、必审集合、前序/重复语义及工艺关联 | 固定上下文、草稿/预期拒绝、expected/actual |
| Contract | Schema、状态、Owner、版本兼容 | validator report |
| Integration | 真实 consumer、Pipeline、Evidence | trace + receipt |
| Golden/Replay | 正常/边界/难例/拒识 | dataset hash + result diff |
| PerformanceProfile | `PF-FS-063` | All numeric targets must come from the approved profile; missing profile values are Unverified/Blocker. |
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
3. DEV-DOM-057D
4. FS-063 本文
5. Contract/Schema refs registered for this capability
6. State/Owner/AuthorityScope rules
7. UI-PCS-005 (when UI is present)
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
| Function | `FS-063` / `Review/rework` |
| Domain | `AOI` |
| Guide | `DEV-DOM-057D` |
| Input | `committed result/evidence + Case/Item/policy + actor/claim context` |
| Output | `appended review record/receipt + rework/reinspection links` |
| Result semantic | `immutable machine fact reference + independent human/rework records` |
| Canonical port | `IReviewRework` |
| Project | `Asun.Domain.Aoi` |
| UI PageContract | `UI-PCS-005` |
| Primary Work Package | `WP-19` |
| Algorithm baseline | `evidence-first UI + state machine` |
| Performance gate | `batch candidate + P95` |
| Test baseline | `Golden + Contract + Integration + Fault + Performance` |

### 16.1 Preconditions

- input objects exist and are version/hash identifiable;
- scope and authority are compatible;
- coordinate/unit/calibration conditions are satisfied where relevant;
- the selected review action is allowed for this product/item/purpose under the frozen policy;
- current authorization and policy govern new writes; historical reads preserve original withdrawn/replaced references where access policy allows;
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
| Primary | `evidence-first UI + state machine` | 仅在本 FS 的适用域、输入质量门和参数来源满足时执行。 |
| Fallback | `Manual review / approved rework workflow` | There is no automatic quality fallback. If evidence is insufficient, Review remains unresolved. Rework changes are commands with their own receipt/authorization. |
| Reject / Block | `For new writes: unauthorized reviewer, expired claim, required evidence missing or disposition conflict. Historical committed receipts remain queryable under current access authorization.` | 保留证据与原因；不得生成权威 OK。 |

**本 FS 的 fallback 不是“另写一个算法看看”。任何替代路线都必须来自当前 Development Guide / Operator Decision Matrix / Qualification 已登记的候选集合。**

### 16.4 Parameter authority matrix

| Parameter class | Authority/source | Hard rule |
|---|---|---|
| Target/ROI | `from approved target set or runtime binding` | never guessed from image unless the FS explicitly allows auto-targeting |
| Coordinate/Unit | `from CoordinateGraph/Calibration/Manufacturing reference` | must be explicit; mismatch blocks |
| Review policy | `approved review/action policy snapshot` | allowed outcomes, reasons, scope and concurrency semantics are explicit |
| Claim/completeness/late rules | `approved review policy` | client clock, visible-row count or AI suggestion cannot substitute |
| Fallback policy | `FunctionSpec decision table` | no automatic semantic downgrade |
| Performance budget | `batch candidate + P95` | 由 PerformanceProfile 绑定；至少记录 P50/P95/P99、峰值内存、并发安全和取消延迟；未实测不得声称 Qualified |

## 17. Robustness challenge set

At minimum, the function must be challenged against:
- `证据缺失`
- `重复复判`
- `返修循环`
- `权限不足`

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

## 18. 操作展示状态与副作用边界

| State | Entry condition | Allowed behavior |
|---|---|---|
| `Ready` | 当前任务上下文允许准备该操作 | 仍在服务端提交点复核；页面Ready不是写入权 |
| `Blocked` | 该操作缺证据/前序/权限等条件 | 定位原因；不阻断其它允许的历史阅读 |
| `RecoverableError` | 读取失败或提交结论未知 | 读取可按原范围恢复；未知提交查原回执，不盲重判 |
| `Invalid/Rejected` | 原Owner明确拒绝本次请求 | 保留原意见/证据，不把请求被拒变成产品NG或PASS |
| `Completed` | 本次明确范围的操作已有确定回执 | 单项成功不等于整板必审闭合、处置或实体离站 |

本表是操作/UI分类，不新增Case、Claim、返修或设备状态机；合法NG和缺项事实保持其原始质量状态。

Only approved Application/Domain services may create production facts or machine-authoritative commands. UI and ViewModel are projections and command clients, not fact authorities.

## 19. Data/provenance and evidence mapping

```text
Committed production result + exact evidence
  → Case / Item / policy + valid Claim for new writes
  → human draft + explicit submit
  → appended ReviewDecision / original receipt
  → approved actual rework + new physical inspection result
  → product disposition input (no direct motion)
```

**Trace requirements**
- 请求幂等身份、追踪关联、Claim代、Case修订和板次身份按原合同分别绑定；不得把正式请求操作身份降为仅日志字段，也不互相替代。
- Every review record binds original production result/item, policy, actor, predecessor and receipt; machine algorithm/measurement provenance remains in the immutable referenced evidence.
- Replay可读取已提交人工历史，或在隔离模拟中核协议；不能重新计算出一个人类决定。真实意见/返修/设备写入必须为0，版本比较另留工程报告。


## 20. Performance engineering contract

The implementation must benchmark:

| Dimension | Requirement |
|---|---|
| Latency | report P50/P95/P99; do not report only average |
| Throughput | 分别测服务每秒请求/并发站与人的每板审阅时间；后者包含证据/难例，不用空操作替代 |
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
| Port/interface | `IReviewRework` | Stable application/domain-facing contract; no vendor type leakage |
| Implementation | `ReviewRework.cs` | AOI工艺适配与原端口组合；复用PKG-044，不复制Claim/Store |
| Validator | `ReviewReworkValidator.cs` | Input/precondition/quality checks |
| Tests | `ReviewReworkTests.cs` | unit/contract/integration/fault tests |
| Golden/Replay | `tests/Golden/FS-063/` | fixed datasets, expected outputs, provenance |
| Benchmark | `ReviewReworkBenchmark.cs` | P50/P95/P99/resource evidence |
| UI | `src/Asun.UI.Workspaces/UI-PCS-005/` | projection only; no production fact write |


**Implementation order**
1. contract/port and validation;
2. frozen PKG-044 application-port integration and AOI review/rework mapping;
3. authorization/claim/receipt recovery and required-set/coverage semantics;
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
| T63-01 | 来源/Claim代/CAS/操作身份合同 | 同键同请求回原回执，异请求冲突，旧代不能新增意见 |
| T63-02 | 人工草稿→显式提交→原回执 | 原NG/量测不变；未发送项与必审全集缺项保持可见 |
| T63-03 | 固定历史读取与隔离协议回放 | 已提交意见可追溯，真实新意见/返修/设备命令增量0 |
| T63-04 | 丢响应/过期/断网/停止与旧worker并发 | 成功不重做；未知先查询；废止前排空或同事务fence；不强清屏障 |
| T63-05 | 队列、证据、Claim、提交与关闭 | 分并发站/冷热/负载测P95/P99，人的审阅耗时与服务延迟分别报告 |
| T63-06 | 机旁与独立站同核心，接AOI及第二工艺 | 不引用机台私表；同坐标独立原因互不消除；局部复检缺邻域不闭合 |
| T63-07 | 缺图/盲审/原PASS补标/已离站更正 | 无权内容不泄漏，补标有原来源和独立人工身份，零自动设备动作 |

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
| Function | `FS-063` | 本任务只实现该 FS；不得顺手扩展其它 FS。 |
| Guide | `DEV-DOM-057D` | 指导文档是实施语义权威。 |
| Project | `Asun.Domain.Aoi` | 首选代码项目；跨项目修改必须有依赖记录。 |
| Port | `IReviewRework` | 公共入口名称固定；改变名称必须先改 Contract/Registry。 |
| PageContract | `UI-PCS-005` | UI 只做投影/Command client；不得成为事实权威。 |
| Algorithm baseline | `evidence-first UI + state machine` | 只能在明确的条件下切换到 Fallback；不得凭个人偏好替换。 |
| SideEffectPolicy | `controlled production/integration side effect via approved Port；受控副作用只能通过批准 Port，并且必须满足 Authority/Permission/Commit 门禁。` | 冻结策略；任何未批准副作用路径必须 Blocker。 |
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

- 输入契约：`committed result/evidence + Case/Item/policy + actor/claim context`
- 输出契约：`appended review record/receipt + rework/reinspection links`
- 质量语义：Unknown / Invalid / NotApplicable / NotQualified 不得被映射为 OK。
- 证据要求：人工记录回溯原结果/Item/证据、主体/策略/前序与提交回执；机器算法/量测谱系沿原事实引用读取，不给人判伪造算法、标定或零量值。

### AI 完成后的强制回报

AI 必须输出：变更文件清单、对应 FS 条目、Contract/Schema 变更、测试、Benchmark、未关闭风险、未验证 API、禁止路径复核结果。未能证明的内容必须标记 `Unverified`，不得写成 `Completed`。

## 27. Function-specific deterministic freeze profile

| Item | Frozen implementation rule |
|---|---|
| Function class | `Review/Rework` |
| Primary algorithm/route | `evidence-first UI + state machine` |
| Fallback | `Manual review / approved rework workflow` |
| Fallback trigger | There is no automatic quality fallback. If evidence is insufficient, Review remains unresolved. Rework changes are commands with their own receipt/authorization. |
| Reject/Block | For new writes: unauthorized reviewer, expired claim, required evidence missing or disposition conflict. Historical committed receipts remain queryable under current access authorization. |
| Parameter authority | `['ReviewClaimPolicyId', 'ClaimLease', 'DispositionPolicyId']` come from versioned Contract/Recipe/MethodPolicy/Qualification; no code constants |
| Result/evidence | ReviewDecision + exact original result/item + policy/actor/predecessor + receipt + rework/reinspection references |
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
5. **Replay:** 同一历史回执可受权读回；隔离模拟固定故障顺序验证恢复，不新增真实人工记录、返修动作或设备命令。

### 27.2 AI stop condition

AI must stop before editing code when any value in this profile is unavailable from an authoritative source. The absence of a numeric threshold does **not** authorize the AI to invent one; it means the task must bind the applicable versioned PerformanceProfile / Recipe / Qualification asset first.

## 26. Implementation status

`ImplementationSpecificationReady` means the documentary implementation contract is complete within the current architecture scope. It does **not** assert that target hardware, real Golden data, HIL, calibration qualification, production thresholds, or external interoperability have been experimentally qualified.


### 27.3 ScopeDrift stop condition

`ScopeDrift` is required to remain `none`. A request to add a new object, field, state, Owner, algorithm route, page command, external API or file outside this FS is not an implementation detail; it is a change candidate and must stop the current task until approved and re-indexed.


## 复判事务及局部复检的专项接收

以[PKG-044 §8](../../../shared-modules/packages/PKG-044_Review.md#review-submission-recovery)验收旧代迟到、续租丢响应、部分提交/未知/未发送与终结屏障；以[DEV-DOM-057D §3](<../06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md#rework-reinspection>)验收实际返修/新尝试/局部覆盖和质量处置分离。通用模板中的Ready/Completed只是页面/操作分类，不成为第二套Case状态机。重放人工记录是读取历史或模拟协议，不自动再造人判。

## 多轮复核与仲裁的实施接收

除单审事务外，按[044 §11](../../../shared-modules/packages/PKG-044_Review.md#review-rounds-arbitration)和[AOI工艺差异](<../06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md#aoi-arbitration-semantics>)接收：同人更正不增票、必审分母不随缺席缩小、同Outcome不同原因仍可分歧、盲审披露不可撤回、仲裁冻结集合变化拒绝旧提交、Unknown恢复原回执。现有同Case排他Claim不擅自扩为多个并行Claim；原契约多轮字段/权限未冻结前不以新增私有DTO绕过。人工仲裁不产生GroundTruth、偏差批准或设备动作。
