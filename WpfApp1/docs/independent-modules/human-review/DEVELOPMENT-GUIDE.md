# 人工复判独立能力开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2`

- 文档 ID：`IM-HR-044`
- 模块键：`human-review`
- 版本：`0.3.2-prep`（2026-10-12；完整范围设计收口，Module API Contract仍为v0.3）
- 状态：`DesignReview/Prep`
- 技术基线：C# / .NET 10；Core 无 UI；可选 WPF + DevExpress 25.2.3
- 视觉基线：HALCON 26.05 / `ImageLibDotNet`；本模块不执行视觉算法
- 来源映射：[PKG-044 Review](../../shared-modules/packages/PKG-044_Review.md)、[SM-022](../../shared-modules/modules/SM-022_review.md)
- AOI 组合边界：[DEV-DOM-057D](<../../process-guides/guidance/06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md>)
- 跨工艺组合边界：[PG-023](<../../process-guides/processes/PG-023_review-rework.md>)
- 实施标准：[DEV-GOV-005](../../01-governance/DEV-GOV-005_模块独立性与复用标准.md)、[DEV-GOV-006](../../01-governance/DEV-GOV-006_外部实现与GitHub研究标准.md)、[DEV-GOV-010](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)

本文件是人工复判能力在独立目录中的唯一实施指导。它是对现有 `PKG-044`/`SM-022` 的独立架构审查和可实施化细化，不修改共享架构、`模块索引`、`PROJECT_ENTRY`、`PROJECT_PROGRESS`、`PKG-044`、参考项目或客户代码。主会话已将该能力接收为当前独立模块候选中的 `IM-067`；`accepted` 只表示指导完成架构接收，不表示平台 Contract、代码实现、产品集成或生产验收完成。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/human-review/Asun.Modules.HumanReview.Core/Asun.Modules.HumanReview.Core.csproj`；namespace：`Asun.Modules.HumanReview`。预定测试工程：`tests/Modules/human-review/Asun.Modules.HumanReview.Core.Tests/Asun.Modules.HumanReview.Core.Tests.csproj`。上述项目尚未创建。
- 允许变更范围：仅上述 Core 和测试工程目录；在明确获准的实现切片中，必要的新文件也只能放入这两个目录。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 当前切片状态：`C1/C2 = ModuleCoreImplementationReady`（本永久原会话已完成六项核心规格接收）；`U1/I1/P1 = PreparationIncomplete`。该状态仅允许纯 Core/Simulator/安全端口按已接收契约进入代码任务，不表示工程已创建、代码已运行、产品集成或资格通过。

2026-10-11 修订冻结本模块 `Module API Contract v0.3`（§9），替代旧 v0.2 接口形状；是已接收C1/C2的模块技术基线，不批准平台产品 Schema 或客户策略。本轮只完善本指导，不创建项目或改变登记状态；各切片六项定位和剩余门见附录 A。

## 1. 审查结论与边界裁决

### 1.1 为什么需要拆出稳定 Core

机旁复判和独立 `ReviewStation` 已是两个真实消费者。两者都需要相同的领取/续租/归还、幂等提交、未知回执恢复、意见链和证据可见性栅栏；仅把这些逻辑留在 AOI 应用会导致第二个消费者复制状态机、租约和恢复规则。这个稳定、可测试、无制程判定的事务能力可以独立发布。

### 1.2 Core 管理的稳定事务语义

Core 管理下列技术/人工事务规则；持久事实由宿主注入的 Review Owner/Repository 持有，Core 实例没有第二事实库：

1. 不透明的 `ReviewWorkItemRef`、Item 修订和本轮问题快照引用；不解释板件、位号、焊点、锡膏或其它制程语义。
2. 队列读取的受控投影端口、领取/续租/归还租约、执行代和 fencing 规则。
3. 人工观察意见的追加链、同一主体的有因更正、独立轮次/分配引用、仲裁输入和提交回执。
4. 授权观察点、证据可见性/盲审裁剪结果的引用、幂等身份、未知结果和可恢复状态。
5. 可重建的状态事件、诊断关联和资源排空状态。

Core 不拥有最终“通过/不通过”的质量事实；`Outcome` 只是在批准策略允许范围内由人工提交的候选意见，最终是否闭合由宿主和产品 Owner 判断。

### 1.3 必须留在调用应用/宿主的责任

以下责任不能下沉为通用 Core：

- 从检测结果选择哪些 Item 入队、建立板/工单/面/尝试关系、解释缺陷类型和严重度；
- 决定允许的人工结论、理由枚举、必审分母、超时/升级/替补策略和是否必须仲裁；
- 质量放行、客户协议、返修动作目录、返修工具/材料、再检计划、实体位置和任何设备/PLC/运动命令；
- 把人工意见聚合为制程决定、报告结论、AI 真值、统计分母或训练标签；
- 站点路由、停板/隔离/出站、页面导航和产品工作流编排；
- 业务数据库表、私有文件路径、产品 ViewModel、全局状态和领域状态机。

`ReworkCompleted`、`ReinspectionPassed`、`DispositionApproved` 和 `BoardReleased` 是不同事实，均由宿主或其批准 Owner 写入。Core 只能保存宿主提供的稳定引用和关联意图，不能把其中任何一个转换成另一个。

### 1.4 独立性与依赖原则

Core 只依赖稳定的授权、身份、证据、查询、存储/事务、时钟和诊断端口；依赖方向为宿主 → Core → 端口适配器。Core 不直接引用其它独立模块实现 DLL，不直接访问数据库或硬盘，也不持有 HALCON/AsunImage 句柄。依赖的能力契约由宿主注入；未采纳的产品 Schema 不得偷偷变成 Core DTO。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.HumanReview.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1.4 已明确"Core 只依赖授权、身份、证据、查询、存储/事务、时钟和诊断端口"。

**Blazor/Web**：复判工作台的 Web 版本支持远程复判。服务端执行所有判定逻辑，浏览器只渲染缺陷证据图和意见表单；图像通过 HTTP Range 分片加载；人工意见提交经授权 gRPC 接口，每次提交绑定 principal 令牌和操作 ID。

**AI 三态仲裁集成**：本模块是三态仲裁（`ai-inference` §1A）中 `NeedsHuman` 终态的直接消费者——AI 仲裁产出 `NeedsHuman` 时，由宿主路由到本模块的复判队列。本模块只接收任务和收集人工意见，不重新执行 AI 推理；人工结论回流到 `ai-dataset-governance` 的训练队列。

**HALCON 不适用**：复判是人工审核事务，不执行视觉算法；HALCON 备选 CI 不涉及本模块。

## 2. 角色、消费者与调用链

### 2.1 角色

| 角色 | 责任 | Core 可见范围 |
|---|---|---|
| 复判宿主（机旁/ReviewStation） | 编排筛选、读取、草稿、提交和下一项；展示 Core 投影 | 仅宿主收到的策略裁剪；无默认全量读取 |
| Review Owner | 建立/修订 WorkItem、定义本轮用途和允许范围 | Core 只校验引用、修订和策略快照 |
| 授权 Owner | 签发读/写/仲裁权限及撤权代次 | Core 只消费可验证的授权观察点 |
| 证据 Owner | 提供不可变原图/派生/量测引用和读取租约 | Core 不生成、不补齐、不改变证据 |
| 人工审核员 | 在允许范围内观察并提交意见 | 只能写自己的有效租约和分配范围 |
| 仲裁 Owner | 处理批准策略指定的分歧 | 只能提交冻结依赖下的仲裁记录 |
| 质量/返修/设备 Owner | 聚合、返修、复检、放行和设备动作 | Core 无权写入这些事实 |

### 2.2 两个消费者的真实调用链

```text
检测/质量宿主
  -> ReviewQueueAdapter（宿主筛选后的不透明任务投影）
  -> HumanReviewCore
        -> AuthorizationPort（包含独立认证）
       -> EvidencePort（IM-015 语义端口）
        -> ReviewRepository（宿主适配 IM-066 技术端口）
       -> Clock / Diagnostics / PolicySnapshotPort
  -> 宿主聚合与最终处置 Owner

机旁 HMI 或独立 ReviewStation
  -> 同一 Core API + 同一策略/权限端口
  -> 可选 HumanReview.Wpf 控件（只投影和发出命令意图）
```

机旁和独立站必须使用同一发布包和语义；差异只来自宿主策略、权限、证据适配和页面组合。独立站不启动相机、运动或整机 Shell，不打开共享数据库文件，也不传服务器本地路径。

## 3. 输入、输出、参数与策略 Owner

### 3.1 输入契约

| 输入 | 必需约束 | 来源/Owner | Core 行为 |
|---|---|---|---|
| `ReviewWorkItemRef` | 非空、稳定、带 `Scope` 与 `Revision`；不透明字符串 | Review Owner | 仅用于定位与 CAS，不解析制程字段 |
| `ReviewQuestionRef` | 本轮问题、独立原因和用途的不可变引用 | Review Owner/Contract | 缺失或修订不匹配则拒绝提交 |
| `EvidenceSetRef` | 允许读取的 Manifest/对象引用集合 | 证据 Owner | 只经 EvidencePort 读取；缺项显式返回 |
| `AssignmentRef` | 主体、角色、独立性/利益冲突过滤结果、分配代 | 授权/Review Owner | 领取与提交时再次核验 |
| `PolicySnapshotRef` | 允许 Outcome、理由、批量/多轮/盲审策略的摘要和版本 | 产品/质量 Owner | 只消费已冻结快照，不自行补默认 |
| `LeaseRef` | Core 按权威时钟提出、Repository 原子接受的 claim 代和期限；主体/用途绑定原操作 | Review Repository/租约权威 | 新写必须带当前代；提案不构成已领取，旧代被 fencing |
| `ReviewOpinionDraft` | 候选结论、理由、证据引用、可观察性和备注 | 审核员 | 仅为内存草稿，未提交不产生事实 |
| `IdempotencyKey` | 调用方作用域内唯一；载荷摘要绑定 | 调用方 | 相同载荷恢复原回执，冲突返回错误 |
| `OperationBudget` | 总期限、取消令牌、队列/读取/提交子预算 | 宿主 Profile | 缺失或越界拒绝，不使用无限默认值 |

核心不接受板码、AOI 枚举、SPI 缺陷字段、绝对路径、SQL、设备句柄或自由 JSON 作为业务入口。产品字段通过宿主映射为不透明引用和已批准策略快照。

### 3.2 输出契约

| 输出 | 语义 | Owner |
|---|---|---|
| `ReviewQueuePage` | 权限裁剪后的稳定排序投影、游标/水位和资格原因 | Query/宿主投影 Owner |
| `ClaimResult` | `OperationStatus` 与当前获准交付时唯一的短时 `ReviewLeaseCredential`；拒绝/冲突/未知结果不携带秘密 | Core |
| `RenewResult` | `OperationStatus` 与当前获准交付时的新代 `ReviewLeaseCredential`；不把历史回执误当成当前秘密交付资格 | Core |
| `EvidenceReadReceipt` | 允许对象、可见性范围、Manifest 修订、完整性/缺失/拒绝 | Evidence Owner + Core 事务 |
| `OpinionReceipt` | 追加意见、回执 ID、状态、前序、证据/策略摘要和审计引用 | Core/Review Owner |
| `ArbitrationReceipt` | 冻结依赖、仲裁记录、回执和未解决项 | 仲裁 Owner；不等于放行 |
| `ReviewProjection` | 未完成、争议、待仲裁、已提交等投影，带水位和修订 | 宿主投影层 |
| `OperationStatus` | 原操作 Unknown/Pending/Resolved，以及证明中的 Committed/Rejected/Conflict；本地排空另用 DrainReceipt | Repository 事实，Core 投影 |

计算成功、人工意见、质量不合格、未观察、取消和提交未知必须分开表达，不能返回一个 `bool`。UI/报表只能投影这些结果，不得成为第二写入权威。

### 3.3 参数和策略归属

Core 固定类型、单位、版本、CAS、幂等、租约和错误语义；宿主 Profile 提供并记录队列页大小、租约 TTL、续租提前量、超时、最大并发、预取窗口、排空期限、批量形态和性能目标。产品/质量 Owner 冻结角色资格、Outcome/理由、分母、盲审对象、仲裁权限、替补、保留和升级政策。缺少策略时 Core 返回 `PolicyRequired`，不得默认 PASS、默认全量证据或默认多数票。

Claim/Renew 的秘密交付是 Core API 的一等结果：`ClaimResult`/`RenewResult` 只有在 `Delivery=Granted` 时才带 `ReviewLeaseCredential`，其包含不可复制的安全句柄和不透明 `LeaseRef`；拒绝、冲突、未知或仅历史状态查询不得带句柄。credential 不可序列化、不可记录、不可从 `ToString()` 取得秘密。宿主只可将同一 credential 传给 Renew、Submit、Correct、Arbitrate、Release 等 Core 写操作，并在替换或关闭时释放；只读看图不要求 Claim，授权由读取用途端口验证。取消等待不表示远端传输已排空，底层缓冲必须等适配器确认序列化/RPC 真正结束后才可清零或复用。

## 4. 权限、证据集与盲审

### 4.1 权限栅栏

每一次队列读取、Claim、续租、证据读取、意见提交、纠正和仲裁都携带授权观察点、主体、用途、范围和撤权代。页面刚刚检查过权限不能替代服务端提交时的再次核验。无权读取与“没有意见/没有证据”不同，Core 必须返回 `PermissionDenied` 或被批准的受限投影，不返回伪造的空集合。

原图只读、Claim、补标、量测/规则明细和导出是不同用途，分别核权。仅图片可见不授予读取整个结果 Artifact 或其量测正文；基础读取与明细读取在入口、异步返回及最终发布边界各核当前授权。策略未说明的用途不得由已有看图权限推导。

### 4.2 证据边界

Core 只接受不可变 `EvidenceSetRef` 和 EvidencePort 返回的受控字节/元数据租约。原图、派生图、3D/量测证据和工程报告保留来源、Manifest 修订、对象 hash、用途和完整性；缺图、失效租约、损坏或不可观察必须显式显示。不能从缩略图、相邻时间、文件名或 AI 分数补齐原证据，不能把 2D 证据推断成不可见 3D 事实。

实际读取范围为当前获权可见投影、原 WorkItem/Question 映射、原已提交 Manifest/receipt 和当前 retention 的交集。元数据、尺寸和坐标变换同样受可见性限制；普通合法图片阅读不要求可信尺寸，未知尺寸只阻止依赖尺寸的补标/量测操作。历史解释必须绑定实际已持久事实的精确引用、修订、内容 hash 和回执；调用方自造未持久对象或 `latest` 不构成历史来源。

事实投影与图片投影分别失效：事实缺失、损坏、解码失败或对象映射不唯一时，仅该事实不可用，仍获权的合法图片可继续查看；共同授权撤回时两者同时清除。发布和清除均须匹配捕获的 binding/selection generation，迟到失败不得清掉新项。事实由原 Owner/decoder 提供，Core 不另解码或重算；显示保留原值、单位、有效性、Known/Unknown/NotApplicable 和来源，不把遗留零值当已知值，不把算法候选或宿主业务状态提升为机判/最终处置层。

### 4.3 盲审

盲审策略必须逐项说明隐藏对象：原机判、AI 候选、其他意见、人员身份、历史轮次、参考图/期望文字和计数。服务端裁剪队列、Item、错误、计数、缩略图、预取、导出和订阅，不把隐藏列只当 UI 样式。实际披露范围和时间写入审计；已看见答案的人员不能靠刷新恢复“未见过”状态。盲审不证明线下交流不存在，产品需保留独立性限制。

裁剪同时覆盖 UIA/automation 属性、tooltip、截图、诊断及投影 hash；受限真实结果以无值和受限原因表达，不填 `PASS` 或机判 `Unknown` 枚举冒充原结论。投影 hash 只覆盖实际获准交付内容，不能夹带隐藏结论。迟到结果、更正或新轮次只产生各自引用，不改写原机器、人工或设备历史。

### 4.4 完整性与计数维度

必审集合、获权可见 Item、未处理 Item，以及图像引用、实际已读、缺失、损坏、受限数量分别投影；每项保留来源/水位及已知或受限状态。一 Item 多图/多 FOV 不重复计 Item，引用数量不等于已读数量，分页空页或过滤后空列表不等于完成。盲审受限总数不编码为零，也不通过差值泄露；部分图片或全部图片已到达均不能替代上游必检完整事实。Core 消费 Owner 提供的完整性，不从列表行数重建分母或判定放行。

## 5. 队列、领取、租约与幂等

### 5.1 队列

宿主先按产品规则从已提交检测事实选择 WorkItem，再调用 Core 的受控查询端口。Core 负责稳定排序、水位、游标、资格裁剪和投影一致性，不创建制程缺陷或从板级 NG 推导 Item。已加载列表不授予写权；页面排序、预取和总数不改变 Claim 结果。高优先级持续满负荷时只能记录普通队列等待，不声称同时保证严格优先和最大等待。

首次页固定 QueueSnapshot（查询 hash、唯一排序、可见性 scope、源水位和保留期限）；排序键由队列 Owner 提供，Core 仅按 ordinal 稳定 Item 身份补最终 tie-break。后页使用同一 snapshot 的 keyset cursor，不用 offset 或每页 `latest`。源不能维持 snapshot、权限/策略改变或游标到期，返回 `SnapshotExpired/DependencyConflict`，显式从新首屏开始；不拼接新旧总数。空页可带有效 next cursor；只有 `EndOfSnapshot=true` 表示获权快照枚举结束，仍不代表必审完成。不在 Core 引入通用条件树或数据集注册。

### 5.2 Claim/续租/归还顺序

```text
Authenticate caller + validate request structure and exact-operation query scope
  -> Resolve original operation/idempotency key and compare frozen request identity
  -> If found: return its durable outcome; separately revalidate whether a live secret may be delivered
  -> If absent: validate current capability/policy/revision/lease and assignment
  -> Grant one fenced lease generation
  -> Persist receipt before returning success
  -> Renew or Release with exact generation
```

同一 WorkItem 的当前写范围最多一个，除非产品先在正式 Contract 中定义互斥分配范围和原子闭合；不能用多个普通 Claim 假造并行盲审。续租必须核主体、用途、设备/会话绑定（如策略要求）、修订和服务端期限；旧客户端迟到的归还不能释放新代租约。关闭不自动归还；无未决操作时由人或批准宿主流程显式 Release，确认前仍以服务端期限和 fencing 为准。lease 到期不自动生成新 Owner，也不产生意见。

WorkItem 的语义 `Revision` 与可变事务 `StateVersion` 分开。Claim/Renew/Release/意见/仲裁每次真正持久新写只使 StateVersion 增一，Lease generation 仅 Claim/Renew 改变；证据、Question、Policy 的语义引用保持原值。成功回执返回完整 AfterState，下一次写显式使用该版本；重放不增版本。状态版本溢出或代次耗尽拒绝新写并通知 Owner，不绕回零。新证据/新问题另由 Review Owner 提供新 revision，不让 Core 自动重绑定草稿。

### 5.3 幂等与未知回执

Claim、Renew、Submit、Correct、Arbitrate、Release 各有操作身份。服务端先认证调用方并验证可查询该精确操作，再按原 idempotency key/OperationId 查询持久操作并比较冻结的请求身份；已存在的原操作必须在检查当前可变 WorkItem revision、当前 Claim 或重新执行 CAS 前解析。相同身份和相同版本化规范载荷返回原业务回执；同身份不同载荷返回 `IdempotencyConflict`。只在无原操作记录的新写分支检查当前策略、授权、修订与 lease。请求已发送但响应丢失时先按原身份查询；查询无权限、无记录或网络失败不能证明未提交，也不能换键重做。Claim/Renew 的历史成功回执与当前秘密交付资格分开：即便原操作已成功，当前租约到期、撤销或 rotation 替换后也不得发回 token。租约过期只拒绝新的写入，不抹除已持久的合法回执。

恢复结果必须区分本次查询的错误/无权/损坏/不可用与原操作的持久结果。只有精确绑定的权威终态证明才能宣称原操作 `Rejected`；查不到为 `Unknown`，权威确认尚未结束为 `Pending`。请求关联身份可保留，但未获证明时不得伪造服务端 operation、receipt、实体修订或终态字段。业务持久结果、安全审计状态和当前秘密交付状态分别表达；提交后的审计或交付失败不回滚原事实、不改成 `Rejected`。审计恢复只继续原审计，不再次 CAS/rotation，普通日志不能替代安全审计。

### 5.4 Claim capability secret 与响应丢失恢复

Claim token 是短时、只交给获准领取人的 capability secret，不是可查询的领域字段。首次 Claim/Renew 成功后，服务端必须同时留下可恢复的原操作事实和安全秘密交付材料；只存不可逆 verifier、却承诺响应丢失后返回同一有效 lease，属于不完整协议。持久化实现由注入的 Review Repository/Key Protection ports 提供，不限定 SQLite、表结构或某个产品数据库；claim 状态、幂等记录、回执、token verifier、加密交付 envelope 和所需 outbox 事实必须处于同一原子事务边界。

- 使用 CSPRNG 产生固定长度 32-byte token 与独立 salt。Core/UI 只通过 `ReviewClaimSecretHandle` 这样的可撤销安全句柄接触秘密；禁止用 `string`、Base64 或普通日志型 record 表示明文。句柄 `ToString()` 必须脱敏，释放时清零其拥有的缓冲区；映射到传输缓冲后，必须等真实序列化/RPC 工作排空再清零，取消等待本身不证明缓冲可复用。
- Repository 只保存带 key/algorithm/schema 版本的 verifier 和短期 AEAD 加密 envelope，不保存明文 token。verifier 使用独立密钥计算 HMAC-SHA-256；比较使用常量时间 API。恢复 envelope 使用 AES-256-GCM 或经安全 Owner 明确批准的等价 AEAD；AAD 必须绑定 WorkItem/Claim、rotation generation、主体、策略要求的设备/会话、expiry、原 IdempotencyKey、命令种类及算法/schema 版本。加密密钥不可写入业务记录，按 key ID/epoch 经密钥保护端口解析；未知、撤销、过期或不可用密钥时失败关闭。
- 幂等处理先认证调用方并按原操作身份解析持久记录，再区分查询原事实和交付秘密。恢复查询不授予读取/写入权限；交付原秘密前必须重新核验当前授权、完整原 origin/session 绑定、主体、适用设备、active rotation、WorkItem 修订和 lease 期限。相同操作键且相同版本化 canonical request bytes 返回原 operation/receipt；只有 lease 仍有效且交付条件仍满足时才可解封并返回同一 token。相同键但请求摘要、目标、主体或设备绑定不同，返回 `IdempotencyConflict`。过期、被替换、撤销或跨越不可恢复 epoch 时保留原成功事实和回执，但秘密交付返回 `LeaseUnavailable`；不得把历史成功显示为当前仍持有 Claim，也不得再次 CAS/旋转以重造同值 token。
- canonical request/verifier/AAD bytes 必须版本化、域分离，并在本模块正式 Contract 中固定字段次序、编码、整数端序、字符串规范化、空值表示和 hash 算法；禁止分隔符拼接、平台默认编码或静默规范化。JCS 只在其各自批准的 JSON 资产摘要合同中使用，不自动替代 Claim 秘密协议。每个版本提供固定 golden bytes/hash 以及逐字段篡改测试；算法或字段改变必须升级 schema/version。
- Renew 产生一个新 rotation generation 并使旧 token 不再授权新写入；同一 Renew 操作键重放只能恢复同一新 lease，不得二次旋转。客户端只有收到并验证新 lease 后才原子替换内存安全句柄并释放旧句柄；Renew 响应未知时只用原操作键查询/恢复，不得换键再续租。安全审计、异常、事件、Outbox、遥测、截图、诊断包、序列化和普通缓存均结构性排除 token、verifier 输入/派生值、salt、nonce 与密文；单独的受控安全审计保留安全结果，不把秘密写入一般日志。

只读来源：[PCBA-AOI ReviewClaim 安全与幂等恢复指导](../../references/project-snapshots/PCBA-AOI/20261006/review-claim-recovery/original/docs/40-development/50-ai-review/ReviewClaim安全与幂等恢复协议开发指导.md) §1–4、§7；精确来源与 SHA-256 见[本次来源快照](../../references/project-snapshots/PCBA-AOI/20261006/review-claim-recovery/README.md)。仅吸收通用 token 交付、幂等恢复和失败关闭约束；不移植 AOI 私有 Case/SQLite/Outbox 实现或其当前应用字段。

### 5.5 宿主在途 gate 与跨进程恢复记录

机旁和独立站的按钮、热键及 headless 调用共用同一 WorkItem 写操作在途 gate；服务端仍执行 CAS/fencing。首次发送可跨进程恢复的写请求前，宿主持久保存非秘密恢复身份：原操作种类、目标/修订、主体 scope、服务权威/端点绑定、幂等键和版本化载荷摘要，以及已知原 OperationId。保存失败则零发送；不保存 token、凭据、签名、完整载荷、草稿或证据内容。

未知期间保留原记录并阻止该项新的 Claim/Renew/Release/Submit/Correct/Arbitrate；取消、关闭、切换主体/端点或重连不自动释放、续租、重发或执行余项。冷重开先在当前获权范围查询原操作；只有精确原终态证明允许完成原记录，完成记录写入失败仍保留恢复身份。容量满时拒绝新 reservation，保留查询/恢复，不裁剪去重事实腾位。

恢复记录由宿主 Integration 的既有持久化端口承担，不是意见事实 Store，也不授予读写权限。纯 Core 首片和 Simulator 可用内存端口验证 gate/身份语义，不因此依赖产品数据库或宣称耐久恢复；真实跨进程验收另核宿主记录保存、完成失败与冷重开。

## 6. 意见、更正、多轮与仲裁

### 6.1 草稿与逐项提交

草稿可在 UI 或无 UI 宿主内编辑，包含证据引用、可观察性、候选 Outcome 和理由。提交前 Core 校验 WorkItem/Question/Assignment/Lease/Policy/Evidence 的修订和权限；服务端生成持久意见和回执。若批准策略允许批量提交，每个 Item 必须有明确目标集合、独立回执和完整性屏障；不能因页面一次点击就声称整板原子成功。未知项不得批量 PASS。

状态观察纯到期与撤权分开。仅当独立保留检查仍证明完整主体/会话、WorkItem/Question 修订、证据/策略和服务权威/端点绑定相同时，可只读保留未发送内存草稿；此证明不返回读取、编辑或提交许可，不复活旧观察。未提供保留能力或无法区分失效原因时拒绝跨到期保留；已观察的来源异常、撤权、身份/端点变化锁存失效，A→B→A 不复活旧 generation。保留检查不能宣称已发现尚未被客户端观察到的服务端撤权。显式刷新取得新状态后核精确绑定和自己的原意见头，由人核对并再次提交；图片仍须独立当前授权有效，合格时无需为刷新状态重复读取大图。已发送 `Unknown` 优先恢复原操作，不从新状态形成新请求。

### 6.2 更正

更正是带原因的追加前序链，引用精确的有效意见头、原证据/策略修订和当前授权；绝不按客户端时间戳最后写胜出。同一主体更正不增加独立票数。已用于质量、报表或 AI 候选的数据由其 Owner 做影响分析，Core 不静默删除旧意见。

自己的前序不得从可见有效结果、时间排序或缓存猜测。Repository 定向只读返回当前认证主体的逐项意见头观察，状态区分 `None/Present/Unavailable`：`None` 仅表示同一权威读取事务证明该主体在该 Item 无已持久意见，`Present` 带精确原意见/receipt，缺项、损坏或不可证明均为不可用，不回退到较早记录。观察绑定主体、Item/修订、水位及策略/可见范围，不披露他人意见；盲审隐藏自己的旧答案时按批准策略拒绝或限定该能力。发送前重读并比较，提交事务再核精确前序/CAS；变化时保留仍获准的草稿、要求刷新并由人再次提交，不自动替换前序或重发。

### 6.3 多轮和独立性

每轮先固定问题、证据闭包、用途、允许结论、可见范围、分配主体和分母，再领取。当前 Core 采用同一 Item 的排他 Claim 串行提交；若需同一 Item 并行意见，必须先采纳表达独立分配范围、前序和共同闭合版本的 Contract，不复制生产 Item 或暗造第二业务对象。替补是新分配并关联原分配，不把两人同时计入有效票。

### 6.4 仲裁

仲裁输入必须冻结有效意见头、分配、证据、策略和可见性；仲裁者可按政策采纳、给出有依据的新意见、保留无法判断或请求补证据。仲裁回执只关闭其明确问题/轮次，不授予返修、放行或设备权。父意见在等待时更正、证据更换、权限撤回或 Claim 过期时，旧预览提交必须返回 `DependencyConflict`；成功回执丢失只恢复原仲裁，不新增另一条。

`ReadArbitrationContextAsync` 由受权 Owner 返回本轮完整依赖摘要、允许可见的意见和未解决项，依赖摘要包含不可见父项但不向客户端披露其内容。不能只取当前页面可见两条意见当全部父集。提交精确比较全部有效父头/分配/水位及策略 hash；零父集、重复父引用、跨问题/轮次或缺必要分配拒绝。人数、独立性和结论规则来自批准 Round/Policy，Core 不默认多数票。串行分配结束可进入待仲裁；部分已提交意见不自动形成仲裁结果。

## 7. 状态、事件与错误

### 7.1 事务状态

```text
Available -> Claiming -> Claimed -> Renewing -> Claimed
Claimed -> Drafting -> Submitting -> Committed
Submitting -> Rejected | Conflict | Unknown
Claimed -> Releasing -> Released
Claimed/Unknown -> Recovering -> Committed | Rejected | Conflict | Unknown | Pending | StillDraining
Disputed -> ArbitrationPending -> Arbitrated | NeedsEvidence | Unresolved
```

`Committed` 只表示人工记录/仲裁事实已持久；不表示质量放行、返修完成或实体离站。`Unknown` 表示客户端尚未得知权威结果，必须保留原操作身份和草稿屏障。取消请求不自动变成 `Cancelled`，直到在途 IO/原生读取真实排空。

上图是操作路径摘要，不把恢复查询失败转换成原操作终态；恢复可继续 `Unknown/Pending`，或由权威证明到达 `Committed/Rejected/Conflict`。审计待恢复和 lease 交付阻断是独立维度，不覆盖原业务状态。

### 7.2 事件顺序

事件携带本次 `RequestId`，以及存在时的持久 `OperationId/ReceiptRef`；未创建业务操作的读取、预拒绝或 Unknown 不伪造持久身份。另带获准的 WorkItem/Question 修订、Lease generation、Policy hash、Evidence scope 和实例 epoch。下列是各操作适用事件的偏序，非每次调用都发送全链：

```text
Accepted -> Authorized -> SnapshotFrozen -> LeaseGranted
 -> EvidenceOpened -> DraftValidated -> CommitPersisting
 -> Committed | Rejected | Conflict | Unknown
 -> ReceiptAvailable -> ProjectionRebuilt
```

进度事件可合并；正式回执必须由Repository保留并可查询，事件订阅不保证回执通知必达。订阅者异常不得改变事实；退订/关闭后迟到事件按 epoch 丢弃或转诊断。

实例事件是有界可丢进度投影，不承诺可靠事务总线；持久事实仍以 Repository 回执读取为准。序号只在单实例内递增，重启带新 InstanceId/epoch；溢出投递一次 `ProjectionResyncRequired` 并通过原水位显式重读，不阻塞提交线程或丢弃持久事实。事件不含秘密/备注全文/隐藏字段，订阅回调不得在持锁区、UI Dispatcher 或事务内执行。

### 7.3 错误分类

| 错误 | 含义 | 恢复 |
|---|---|---|
| `InvalidRequest` | 缺字段、版本/范围/格式非法 | 修正同一草稿，不重放副作用 |
| `PermissionDenied` | 当前用途/主体无权 | 重新取得批准授权，不扩权重试 |
| `LeaseConflict` / `LeaseExpired` | 当前代不再有效 | 读取当前投影并按策略重新领取 |
| `PolicyRequired` / `PolicyMismatch` | 策略缺失或已改变 | 重新冻结批准策略 |
| `EvidenceUnavailable` / `EvidenceCorrupt` | 证据缺失、撤回或完整性失败 | 转待证据/升级，不默认正常 |
| `DependencyConflict` | 前序、分配、Item/证据修订变化 | 丢弃旧提交资格，形成新轮次/草稿 |
| `IdempotencyConflict` | 同操作身份载荷不同 | 查询原回执，使用新身份前先人工确认 |
| `Unknown` | 请求结果未知 | 按原操作身份查询/恢复 |
| `TimedOut` / `StillDraining` | 预算或关闭排空未完成 | 停止接纳，等待或重启恢复；不伪称失败/成功 |

## 8. 取消、超时、关闭与排空

Core 在进入 `Stopping` 后拒绝新 Claim/Submit，保留恢复查询；已在途的证据读取、事务提交和回执查询继续到明确终态或 `StillDraining`。`CancellationToken` 只表达请求取消，不保证远端事务回滚、文件删除或租约立即失效。关闭顺序固定为：停止接收 → 标记 epoch → 取消可取消读取 → 等待持久提交/原生读取真实结束 → 查询 Unknown → 释放 Evidence lease/缓存 → 退订事件 → 返回 `Drained` 或 `StillDraining`。未排空不得复用连接、缓冲、租约秘密或 UI 实例。

实例 `Created→Running→Stopping→Stopped→Disposed`，Stopping 内可有 `StillDraining`。Stop 不恢复业务写入，也不因 Unknown 永远等远端终态：真实本地 IO 排空、恢复身份可保留后允许 Stopped；业务 Unknown 与排空未知分别报告。重复 Stop 共用原 stop ticket，`QueryDrainAsync` 只能查询/等待同 ticket 的本地排空，不启动新的业务恢复或重新分配资源；取消查询仅取消等待。Stopped 只允许 drain/能力读取，原业务恢复由新实例用原身份查询。DisposeAsync 永不同步等待 Dispatcher；资源未真实结束时抛带 stop ticket 的 `ReviewDrainIncompleteException`、保持隔离供显式查询/重试 Dispose，不宣称已释放。无后台轮询/隐式续租；宿主借用端口只在成功 Dispose 后释放。

超时分为队列等待、证据首字节、整次读取、提交和关闭排空，均以单调时钟计量并保留 UTC 审计时间。超时不自动 PASS、不删除草稿、不解除停板、不撤销已发生返修。

每次独立读取在开始边界固定本次观察和最早单调期限，捕获观察本身也计入预算/排空；嵌套索引、元数据、明细读取共享同一次 capture。不得跨 `await` 改用可变 `latest`，不得用后来的同身份观察救活旧读、旧状态或旧前序。最后可能阻塞的来源读取及租约释放后，发布前仍核取消、身份/端点、修订、撤权和期限。

## 9. 持久化 Adapter Port 与文件边界

### 9.1 Core 公共入口（Module API Contract v0.3）

```csharp
public interface IHumanReviewCore : IAsyncDisposable
{
    ReviewCapabilities Capabilities { get; }
    IDisposable Subscribe(IReviewObserver observer);
    ValueTask<ReviewResult<ReviewQueuePage>> QueryQueueAsync(
        ReviewQueueRequest request, CancellationToken cancellationToken);
    ValueTask<ReviewResult<ReviewState>> ReadStateAsync(
        ReviewStateRequest request, CancellationToken cancellationToken);
    ValueTask<ReviewResult<OwnOpinionHeads>> ReadOwnOpinionHeadsAsync(
        OwnOpinionHeadsRequest request, CancellationToken cancellationToken);
    ValueTask<ReviewResult<ArbitrationContext>> ReadArbitrationContextAsync(
        ArbitrationContextRequest request, CancellationToken cancellationToken);
    ValueTask<ReviewResult<ClaimResult>> ClaimAsync(
        ClaimRequest request, CancellationToken cancellationToken);
    ValueTask<ReviewResult<RenewResult>> RenewAsync(
        RenewRequest request, CancellationToken cancellationToken);
    ValueTask<ReviewResult<ReleaseReceipt>> ReleaseAsync(
        ReleaseRequest request, CancellationToken cancellationToken);
    ValueTask<ReviewResult<EvidenceReadReceipt>> ReadEvidenceAsync(
        EvidenceReadRequest request, CancellationToken cancellationToken);
    ValueTask<ReviewResult<OpinionReceipt>> SubmitOpinionAsync(
        OpinionSubmitRequest request, CancellationToken cancellationToken);
    ValueTask<ReviewResult<OpinionReceipt>> CorrectOpinionAsync(
        OpinionCorrectionRequest request, CancellationToken cancellationToken);
    ValueTask<ReviewResult<ArbitrationReceipt>> SubmitArbitrationAsync(
        ArbitrationRequest request, CancellationToken cancellationToken);
    ValueTask<ReviewResult<OperationStatus>> QueryOperationAsync(
        OperationQuery request, CancellationToken cancellationToken);
    ValueTask<ReviewResult<ClaimResult>> RecoverLeaseAsync(
        LeaseRecoveryRequest request, CancellationToken cancellationToken);
    ValueTask<DrainReceipt> StopAsync(
        StopRequest request, CancellationToken cancellationToken);
    ValueTask<DrainReceipt> QueryDrainAsync(
        DrainQuery request, CancellationToken cancellationToken);
}

// Contract shape; secret bytes are deliberately inaccessible to callers.
public sealed class ReviewLeaseCredential : IDisposable
{
    public LeaseRef Reference { get; }
    public bool IsDisposed { get; }
    public void Dispose();
}

public sealed class ReviewClaimSecretHandle : IDisposable
{
    public bool IsDisposed { get; }
    public void Dispose();
    public override string ToString() => "[REDACTED]";
}
```

此代码块是正式方法签名与句柄成员声明，不是独立可编译文件（省略句柄私有实现体）；所有关联公开类型的唯一字段与有效域见 §9.3–9.5。Core namespace 为 `Asun.Modules.HumanReview`，WPF namespace 为 `Asun.Modules.HumanReview.Wpf`。不另建 Contracts DLL 或平台 C-01～C-08 的替代 Schema。`ReviewLeaseCredential` 只能由 Core 创建，不能由宿主构造、复制或反序列化；写请求引用其当前实例，读取请求只带当前授权 context，不单独接受 token 字符串。`QueryOperationAsync` 永不交付秘密；`RecoverLeaseAsync` 单独核当前取密条件，最多续原审计、解原 envelope，不生成新业务操作。凭据传输与秘密缓冲由注入适配器完成，实际序列化/RPC 排空后才清零或复用。

Adapter Port 的唯一完整清单与构造关系见 §9.5。事件通过 Subscribe/IReviewObserver 订阅，不另注入第二个事件总线；身份认证属于 IAuthorizationPort。

宿主 Integration 提供 §9.5 的非秘密恢复记录端口及可选内存草稿保留检查；WPF/headless 共用宿主命令入口，不各建 journal。安全审计由注入的独立能力保存结果并支持原身份续办，诊断端口不能充当它。本次冻结进程内 Core 与端口契约及§9.7 Adapter软件配方；产品远端 wire/部署与实际数据库/证据/密钥提供者由对应Host提供，已定Adapter逻辑按该节实施，不能直接移入来源私表/RPC。

### 9.2 数据库与硬盘文件边界

`IReviewRepository`就是显式注入的复判事务事实端口，覆盖当前Item/自己的意见头/仲裁依赖/精确原回执，最终持久Owner仍是宿主；不是从某个AOI私表取得隐含事实。上游检测原值仅为可选只读投影，由§10.3另注入获权事实投影端口，不作为Core新写事实或可自行聚合的放行结论。

Core 不打开数据库连接、不拼 SQL、不读产品私表。`IReviewRepository` 的生产实现通过 `IM-066 storage-database` 的受控事务/迁移端口保存元数据、不可变意见链和回执；每个事实仍由 Review Owner 写入，IM-066 只提供技术持久化。`IM-045 query` 负责通用过滤、分页、导出；Core 只做复判队列和单项/回执定向读取。

原图、3D、缩略图、导出包和其它大对象不存入 Review 数据库字段，不由 Core 接受绝对路径。它们由 `IM-015 inspection-evidence` 或宿主提供受控 `ObjectId/ManifestRef`，硬盘/NAS 根、临时文件、封口、hash、保留和回收由存储/证据 Owner 管理。Core 只持有对象引用和读取租约；关闭、取消或权限撤回时释放租约，不删除原始证据。数据库提交与文件封口不是跨介质原子事务，Unknown 通过原 `OperationId` 查询，不换对象或操作身份。

### 9.3 唯一值类型、参数和返回字段

下表为规范字段定义，写法 `名称:类型` 对应同名只读 C# 属性，`?` 是可空，集合一律 `ImmutableArray<T>` 并在边界深拷贝；没有表列字段即不得作为隐含状态。不是自由 JSON/产品业务对象。类型使用 record/value object；所有 constructor/factory 统一执行下列验证，default struct 不是合法实例。

| 类型 | 固定字段与有效域 |
|---|---|
| `ReviewRef` | `Scope:string, Id:string, Revision:long, Sha256:string`；标识非空、ordinal 比较、严格 UTF-8，无 NUL/控制字符/非法 surrogate，不 trim/大小写转换/Unicode 归一化；Revision>0，Sha256 为64位小写十六进制。长度由显式 Profile.MaxIdentifierUtf8Bytes/MaxRequestBytes 限制 |
| 专用引用 | `ReviewWorkItemRef/ReviewQuestionRef/EvidenceSetRef/AssignmentRef/PolicySnapshotRef/RoundRef/OpinionRef/ReceiptRef/ManifestRef/ObjectRef` 是独立强类型，均与ReviewRef有相同四个公开字段Scope/Id/Revision/Sha256，不再嵌ReviewRef属性，不能相互隐式转换；内容身份只有相应 Owner 可建立 |
| `LeaseRef` | `Id:Guid, WorkItem:ReviewWorkItemRef, Generation:long, ExpiresUtc:DateTimeOffset, AuthorityEpoch:Guid`；非空 Guid、Generation>0、UTC offset=0；expiry 是服务端事实，本机时钟不重新签发期限 |
| 身份 | `RequestId/OperationId/InstanceId/StopTicket` 各为非空 Guid 强类型；`IdempotencyKey` 为满足标识规则的不透明 string；OperationId 由调用者预分配，只有 OriginalOperationProof 才证明权威已接受该持久身份；不另生成不同服务端 OperationId |
| `ReviewOrigin` | `SubjectScope:string, SubjectId:string, DeviceId:string?, SessionId:string, AuthorityId:string, EndpointGeneration:long`；字符串按标识规则，Generation>0；可选设备缺席只能用于策略明确无设备绑定场景 |
| `ReviewReadContext` | `RequestId, Origin:ReviewOrigin, AuthorizationObservation:ReviewRef, Purpose:ReviewPurpose, Budget:OperationBudget`；认证端口必须独立验证 Origin，调用方字段不创建身份或批准 |
| `ReviewBinding` | `WorkItem, Question, Evidence, Assignment, Policy, Round` 六种专用引用；全部 scope 匹配、归属由 Owner 明确映射；不按相同字符串猜对象关系 |
| `ReviewState` | `Binding:ReviewBinding, StateVersion:long, Watermark:long, ActiveLease:LeaseRef?, ReadProjectionHash:string, UnresolvedQuestions:ImmutableArray<ReviewQuestionRef>`；版本>0，水位≥0；仅获权投影，不含秘密或隐藏意见 |
| `ReviewWriteIdentity` | `OperationId, IdempotencyKey, Kind:ReviewWriteKind, OriginalOrigin:ReviewOrigin, Binding:ReviewBinding, ExpectedStateVersion:long, PayloadSha256:string`；Kind=Claim/Renew/Release/Submit/Correct/Arbitrate；载荷 hash 由 §9.4 唯一 codec 核算，不信调用者宣称 |
| `OperationBudget` | `Total, QueueWait, EvidenceRead, Commit, Drain:TimeSpan`；均>0、有限、≤Profile相应上限，子预算≤Total；Total 从接纳计时，阶段排队也计入，不累加延长。UTC 只审计；本地单调戳不跨机/重启复用 |
| `ReviewProfile` | `ProfileRef:ReviewRef, MaxIdentifierUtf8Bytes, MaxRequestBytes, MaxPageItems, MaxHeadsItems, MaxParents, MaxEvidenceObjects, MaxReadBytes, MaxConcurrentCalls, MaxEventBuffer, MaxPendingOperations:long` 全部正且可用内存分配范围内；`MaxLeaseTtl, MaxTotal, MaxQueueWait, MaxEvidenceRead, MaxCommit, MaxDrain:TimeSpan` 全部正有限；`BenchmarkPlan:ReviewRef?`。无无限/隐含默认，不强加来源容量 |
| `ReviewPurpose` | QueueRead/StateRead/EvidenceRead/OwnHeadsRead/ArbitrationRead/OperationRead/LeaseRecover/Claim/Renew/Release/OpinionSubmit/OpinionCorrect/ArbitrationSubmit/FactRead；FactRead仅用于可选事实投影端口，不新增Core方法；未知值拒绝。导出/补标不创建此模块写方法，交由宿主专用授权端口 |
| `ReviewObservability` | Observed/Partial/Unobservable；未查看不能选 Observed；这些是人工声明，不由 hash、看图次数或 AI 分数证明；各允许 Outcome 对应观测/证据要求由 Policy 明确 |
| `ReviewOpinionDraft` | `Binding, OutcomeId:string, ReasonIds:ImmutableArray<string>, Observability, EvidenceRefs:ImmutableArray<ObjectRef>, Note:string?`；Outcome/Reason 逐个属于批准 Policy、理由不重复，字节受 MaxRequestBytes 限制；备注允许正常换行但禁止非法 UTF-8/NUL，不进普通日志；未发送草稿不产生事实 |
| `ReviewError` | `Code:ReviewErrorCode, FieldPath:string?, DiagnosticId:Guid`；只给批准脱敏字段路径/关联号，不带异常原文/载荷/秘密；错误显示经宿主资源映射 |
| `ReviewResult<T>` | `RequestId, Call:ReviewCallState, Value:T?, Error:ReviewError?, Drain:CallDrainReceipt`。Call=Ready/NotSent/Unconfirmed/Fault；Ready 必有 Value，其可包含持久拒绝/冲突；NotSent 必无 Value 且说明零副作用发送；Unconfirmed 用于可能已发送但未证明结果，Value空且原恢复身份不变；Fault 表示读取/查询失败，不改变原业务状态 |
| `CallDrainReceipt` | `State:Released/StillDraining, PendingCallId:RequestId?`；StillDraining 必有 PendingCallId，实例继续拥有在途资源。已交给调用者的 Evidence lease/credential 另列在资源账本，不冒充所有资源 Released |
| `OriginalOperationProof` | `Identity:ReviewWriteIdentity, Outcome:ReviewOperationOutcome, Receipt:ReceiptRef, AfterState:ReviewState?, RecordedUtc:DateTimeOffset, Opinion:OpinionRef?, Predecessor:OpinionRef?, Arbitration:ReviewRef?, DependenciesHash:string?, Unresolved:ImmutableArray<ReviewQuestionRef>`；精确身份匹配，由 Repository 返回；Committed 必有 AfterState 及对应 Kind 的业务引用，拒绝/冲突无新实体；RecordedUtc 是终态记录时间，不把拒绝称提交成功。精确查询据此重建原意见/仲裁回执，不返回隐含 Draft/他人意见 |
| `OperationStatus` | `Original:ReviewWriteIdentity, Resolution:Unknown/Pending/Resolved, Proof:OriginalOperationProof?, Audit:NotRequired/Pending/Confirmed/Unavailable, AuditRef:ReviewRef?, Delivery:NotRequested/Granted/LeaseUnavailable/AuditPending`；Resolved 才有 Proof；Audit=Confirmed 必有 AuditRef，其余为空。查询只回 Delivery=NotRequested，原成功不因此授予当前 Claim；Audit 的 NotRequired 仅由显式批准 Policy 给出 |
| `ClaimResult/RenewResult` | 各为 `Operation:OperationStatus, Lease:ReviewLeaseCredential?`；仅 Proof.Outcome=Committed、Audit 已确认/明确不要求且 Delivery=Granted 时有 lease；lease 引用等于 AfterState.ActiveLease；其余无秘密。Unknown/Pending 可返回 OperationStatus 而无 lease |
| `ReleaseReceipt` | `Operation:OperationStatus`；成功回执 AfterState.ActiveLease为空，过期/旧代按原操作身份和 CAS 处理，不释放新代 |
| `OpinionReceipt` | `Operation:OperationStatus, Opinion:OpinionRef?, Predecessor:OpinionRef?`；仅 Committed 有 Opinion；Predecessor 与原请求一致。同主体链追加，不把意见 Outcome 提升为质量事实 |
| `ArbitrationReceipt` | `Operation:OperationStatus, Arbitration:ReviewRef?, DependenciesHash:string, Unresolved:ImmutableArray<ReviewQuestionRef>`；仅 Committed 有 Arbitration；hash 与原依赖上下文精确一致 |
| `ReviewCapabilities` | `ContractVersion:string, SupportedPurposes:ImmutableArray<ReviewPurpose>, SecretRecovery:bool, DurableOperations:bool, QueueSnapshots:bool`；版本固定0.3，能力是实际端口组合事实，不是权限或现场资格。内存 Simulator 必须 DurableOperations=false |
| `ReviewEvent` | `InstanceId, Epoch:long, Sequence:long, RequestId?, OperationId?, Receipt?, Kind, Binding:ReviewBinding?, StateVersion:long?, Error:ReviewError?`；Kind 仅 §7 所列进度/事实引用及 ProjectionResyncRequired/Stopping/ResourcesReleased，按可见性裁剪；Epoch/Sequence>0 |

`ReviewErrorCode` 闭合集合为 §7.3 的错误加 `SnapshotExpired/CapacityExceeded/PortUnavailable/ProtocolMismatch/SourceChanged/CancelledBeforeSend/Disposed/Stopping/LeaseUnavailable/SecurityAuditRequired`；Unknown 是业务恢复维度，StillDraining 是资源维度，不用它们掩盖错误。版本不支持用 ProtocolMismatch，参数大/数量越界用 InvalidRequest，运行容量满用 CapacityExceeded；资源已排空的未决写仍为 Unconfirmed，不能自动改成失败。端口抛 OperationCanceledException 也必须由发送边界区分 NotSent/Unconfirmed，不能把所有异常映射 NotSent。

### 9.4 每个操作的精确输入、分支与规范字节

业务请求必有 `Context:ReviewReadContext`，方法与 Purpose 严格一一对应（SubmitOpinion→OpinionSubmit、CorrectOpinion→OpinionCorrect、SubmitArbitration→ArbitrationSubmit，其余按同义用途）；StopRequest/DrainQuery 只有表列生命周期字段。写请求还必有 `Identity:ReviewWriteIdentity`，Context 当前认证与 OriginalOrigin 的查询/写入资格由授权端口判断；恢复查询可使用获准的新会话，但不能修改 OriginalOrigin。非 Claim 新写必有 Core-issued credential，其 Reference 与 State.ActiveLease 相符并参与原载荷摘要；重放解析不先因 credential 已释放阻断获权查询。

| 请求类型 | Context/Identity 以外的完整字段；处理与输出 |
|---|---|
| `ReviewQueueRequest` | `Queue:ReviewRef, QueryRef:ReviewRef, PageSize:int, Cursor:string?`；PageSize=1..MaxPageItems，QueryRef 由队列 Owner 表达获准查询/排序，Cursor 首次空。`ReviewQueuePage(Snapshot:ReviewRef, Watermark:long, Rows:ImmutableArray<ReviewQueueRow>, NextCursor:string?, EndOfSnapshot:bool)`；行=`ReviewQueueRow(State:ReviewState, DisplayId:string, EligibilityReasonId:string?)`，不返回机判/AI分数排序旁路；Rows≤请求大小，End时Next为空 |
| `ReviewStateRequest` | `WorkItem:ReviewWorkItemRef, Policy:PolicySnapshotRef`；空/非法拒绝，不授 Claim；返回当前获权 State，旧 revision 返回冲突，不选最新语义 revision |
| `OwnOpinionHeadsRequest` | `State:ReviewState, Items:ImmutableArray<ReviewWorkItemRef>`；1..MaxHeadsItems、唯一、同获权 scope/轮次，主体只能 Context 中认证主体。`OwnOpinionHeads(State:ReviewState, HeadsHash:string, Entries:ImmutableArray<OwnOpinionHead>)`，原顺序完整；`OwnOpinionHead(Item:ReviewWorkItemRef, State:ReviewOwnHeadState, Opinion:OpinionRef?, Receipt:ReceiptRef?)`，只有 Present 同时有两引用 |
| `ArbitrationContextRequest` | `State:ReviewState`；返回 `ArbitrationContext(State, DependenciesHash:string, ParentRefs:ImmutableArray<OpinionRef>, Unresolved:ImmutableArray<ReviewQuestionRef>, VisibleOpinions:ImmutableArray<OpinionView>)`；`OpinionView(Ref:OpinionRef, OutcomeId:string?, ReasonIds:ImmutableArray<string>, Observability:ReviewObservability?)`；父引用也按可见性披露，完整隐藏依赖只在 Owner 摘要中；无仲裁权限不披露 |
| `ClaimRequest` | `State:ReviewState, RequestedTtl:TimeSpan`；>0且≤Policy许可TTL与Profile.MaxLeaseTtl；State 与 Identity.Binding/版本相同，先解原操作后在新写分支核分配和排他；无 Lease 字段 |
| `RenewRequest` | `State:ReviewState, Lease:ReviewLeaseCredential, RequestedTtl:TimeSpan`；新代 expiry=服务端接纳UTC+获准TTL，并以服务端连续epoch/单调期限约束；不加到旧expiry，不越产品deadline。原操作重放不再延长 |
| `ReleaseRequest` | `State:ReviewState, Lease:ReviewLeaseCredential`；只释放精确原代。成功仅归还复判租约，不代表板件/设备释放 |
| `EvidenceReadRequest` | `Binding:ReviewBinding, Objects:ImmutableArray<ObjectRef>, MaxBytes:long`；1..MaxEvidenceObjects、无重复、≤Profile.MaxReadBytes，范围属于§4.2交集；无 Claim。返回 `EvidenceReadReceipt(Binding, Manifest:ManifestRef, Objects:ImmutableArray<EvidenceObjectRead>, SnapshotHash:string, Lease:IReviewEvidenceLease?)`；`EvidenceObjectRead(Object, Availability:Available/Missing/Corrupt/Restricted, VerifiedBytes:long?, Observed:bool)`，Restricted 无字节计数；Observed仅记录本次读取完成，不代替人工Observed；字节只从lease有界流取，结果不携绝对路径 |
| `OpinionSubmitRequest` | `State, Lease, Draft:ReviewOpinionDraft, OwnHead:OwnOpinionHead, EvidenceSnapshotHash:string`；首意见只接受权威 None，同主体已有 Present 必须 Correct；不可用拒绝。Policy允许 Unobservable 时可以提交对应获准 Outcome，不能填 PASS |
| `OpinionCorrectionRequest` | `State, Lease, Draft, OwnHead, EvidenceSnapshotHash, CorrectionReasonId:string`；OwnHead=Present且原主体匹配，原因属于Policy许可更正原因，事务再核前序；不能用他人头或较旧头，保持独立票数 |
| `ArbitrationRequest` | `State, Lease, ContextSnapshot:ArbitrationContext, OutcomeId:string, ReasonIds:ImmutableArray<string>, Observability:ReviewObservability, EvidenceSnapshotHash:string`；完整依赖摘要/父集由Owner再核，理由/可观察性/必需证据与获准仲裁OutcomeRule相符，不能接受只读预览自行拼集 |
| `OperationQuery` | `Original:ReviewWriteIdentity`；精确获权查询原操作，不带写 credential，不提交/预留任何业务事实；返回 OperationStatus，源无记录Unknown、源真实在途Pending、查询异常Fault |
| `LeaseRecoveryRequest` | `Original:ReviewWriteIdentity`；Kind只Claim/Renew，Context Purpose=LeaseRecover；当前同原完整绑定仍具取密资格才返回ClaimResult；不允许从意见回执或租约Id猜原key恢复 |
| `StopRequest/DrainQuery` | Stop=`RequestId, Budget:OperationBudget`；Query=`RequestId, Ticket:StopTicket, Budget:OperationBudget`；不需要业务授权。`DrainReceipt(Ticket, State:Drained/StillDraining, PendingCalls:ImmutableArray<RequestId>, UnresolvedWrites:ImmutableArray<ReviewWriteIdentity>, BorrowedResources:long)`；Drained表示无本地在途IO，归还调用者lease后BorrowedResources须为0才允许Dispose完成 |

写操作流程固定：深拷贝/结构验证→认证及原操作查询资格→原Identity/canonical摘要解析→命中返回原证明并独立处理审计/取密→无原记录读取State/Policy/原头/依赖→Core校验→取得当前授权提交guard→Repository事务重新解原操作和精确CAS→原子追加/租约变化/回执/outbox及版本增一→安全审计→当前取密/投影发布→真实归还短借用。两线程读同“无原记录”时由事务中唯一幂等键和CAS确定唯一接受者；外部guard在commit线性化点必须仍有效。不得持数据库事务等网络看图或人工输入。

每次语义更正新操作，恢复重放原操作；同IdempotencyKey异bytes为冲突而不是“最后一次覆盖”。空Reason只在Policy明确允许时合法；多Outcome候选不能自动选最高分。可选参考缺失不阻普通Actual看图；必需证据缺失/不可观察只限制Policy指定的提交，保留待证据或无法判断路径，不修改必审分母。

规范字节 `HumanReviewCanonical/v1` 为该模块新协议，不改历史AOI字节或旧回执：严格UTF-8、不Unicode归一化；字段为固定顺序、网络字节序的大端整数，字符串=`u32字节数+bytes`，可空=`u8(0/1)`后内容，数组=`u32数量`后原顺序，Guid使用RFC4122网络字节序，引用顺序Scope/Id/Revision/Sha256。UTC编码为自Unix epoch的Int64 100ns ticks，TimeSpan编码Int64 ticks（100ns）；拒绝超范围/非UTC/小数丢失。Id/理由/对象无重复，不排序改变原选择。

- canonical request 的顺序：域字符串、schema u32=1、Kind u8（Claim=1/Renew=2/Release=3/Submit=4/Correct=5/Arbitrate=6）、OperationId、IdempotencyKey、OriginalOrigin六字段、Binding六引用、ExpectedStateVersion、方法表列出的业务字段。State完整编码Binding/StateVersion/Watermark/ActiveLease可空/ReadProjectionHash/UnresolvedQuestions数组；LeaseRef按§9.3字段顺序，credential只编码其LeaseRef，绝不编码token。Draft按§9.3字段顺序；OwnHead按Item/State/Opinion/Receipt；Arbitration context按State/DependenciesHash/获准ParentRefs/Unresolved/VisibleOpinions字段序。字符串hash仍为64-byte小写hex字符串而非32-byte原始摘要，布尔u8=0/1。Binding/State/Draft重复字段仍逐项编码且必须相等，不能去重或省略。PayloadSha256自身、当前授权观察、RequestId、transport metadata和操作等待Budget不参与，避免循环hash/刷新查询误改原身份；RequestedTtl和全部草稿/理由/证据必须参与。
- verifier域=`HumanReviewVerifier/v1`，输入域、schema=1、LeaseRef、OriginalOrigin、16-byte随机salt、32-byte token；HMAC-SHA256密钥与envelope密钥分离；比较先验证长度再FixedTimeEquals。
- envelope AAD域=`HumanReviewEnvelope/v1`，顺序域、schema=1、原ReviewWriteIdentity（包括PayloadSha256）、LeaseRef、KeyId:string、KeyEpoch:Guid；AES256GCM key=32bytes、nonce=12bytes、tag=16bytes，nonce由密钥保护Owner保证同key不重复。envelope包含算法ID/KeyId/KeyEpoch/schema/nonce/ciphertext/tag/salt/verifier，仅Repository/安全Adapter可读，普通事件/诊断完全不交付。

字段枚举按 §9.6 固定值编码；schema/域/字段变化升级版本。codec解析执行长度/数量/总字节上限，拒绝尾随字节/未知值/非规范可空；Golden见 §13.5，不仅做序列化→自身反序列化测试。历史协议由独立旧codec只读解析，不重算其身份；新旧不得混用同一key域。

### 9.5 端口、工厂、回调与最小宿主

`HumanReviewFactory.Create(ReviewPorts ports, ReviewProfile profile):IHumanReviewCore` 是唯一构造入口，同步仅校验端口/能力/Profile，不连接设备/数据库或开窗口；创建后Running。`ReviewPorts` 的必需字段是下表Queue/Repository/Authorization/Policy/Evidence/LeaseSecurity/SecurityAudit/Clock/Diagnostics；EventBuffer容量来自Profile。均由宿主借用注入，Core不Dispose它们；缺任一必需端口创建失败且零调用，Capabilities也是必需不可变字段。Simulator显式提供全部内存端口；实际不支持可选用途时Capabilities不声明该用途，调用返回PortUnavailable，不能返回假成功。

| 公开端口 | 唯一方法/类型与职责 |
|---|---|
| `IReviewQueuePort` | `QueryAsync(ReviewQueueRequest, CancellationToken):ValueTask<ReviewResult<ReviewQueuePage>>`；固定快照排序/cursor，由获权投影Owner产生；不从Core查询产品私表 |
| `IReviewRepository` | `FindAsync(OperationQuery, ct):ValueTask<OperationStatus>`；`ReadStateAsync(ReviewStateRequest, ct):ValueTask<ReviewState>`；`ReadOwnHeadsAsync(OwnOpinionHeadsRequest, ct):ValueTask<OwnOpinionHeads>`；`ReadArbitrationAsync(ArbitrationContextRequest, ct):ValueTask<ArbitrationContext>`；`CommitAsync(ReviewMutation, IReviewCommitGuard, ct):ValueTask<ReviewCommitResult>`。ct均CancellationToken，异常按发送/提交边界归类；事务必须实现本节CAS/原操作优先原子性 |
| `ReviewMutation/ReviewCommitResult` | mutation=`Identity:ReviewWriteIdentity, Command:ReviewCommand, ProposedLease:LeaseRef?, PreparedSecret:PreparedLeaseSecret?`，Claim/Renew才有后两项；Command见§9.6，不带UI或数据库类型。result=`Status:OperationStatus`，业务引用均来自Proof，避免第二份不一致字段；状态变化/回执/secret envelope/outbox同事务。Repository重核所有引用、前序、依赖及证据hash，不重选Outcome或策略 |
| `IAuthorizationPort` | `ObserveAsync(ReviewReadContext, ReviewBinding?, ct):ValueTask<IReviewAuthorizationLease>`；`AcquireCommitGuardAsync(IReviewAuthorizationLease, ReviewWriteIdentity, ct):ValueTask<IReviewCommitGuard>`；lease/guard均IAsyncDisposable，分别提供`Observation:ReviewRef, Origin:ReviewOrigin, Purpose:ReviewPurpose, RemainingLifetime:TimeSpan, Revoked:CancellationToken, ValidateCurrent():void`。RemainingLifetime在取得时固定为正有限值，Core从捕获开始单调扣减并与预算取最早期限，不得续命；ValidateCurrent实时核撤权/主体/绑定/来源，不能只检查客户端ref。guard另提供`ValidateAtCommit():void`，授权Owner保证该短guard与撤权有可审计线性化顺序；无法保证则拒绝Adapter，不用签名未过期替代。首次/跨await/末次均核，读取租约不等于Claim |
| `IReviewPolicyPort` | `ReadAsync(PolicySnapshotRef, ct):ValueTask<ReviewPolicy>`；字段=`Ref:PolicySnapshotRef, AllowedOutcomes:ImmutableArray<OutcomeRule>, CorrectionReasonIds:ImmutableArray<string>, AllowedArbitrationOutcomes:ImmutableArray<OutcomeRule>, MaxLeaseTtl:TimeSpan, DeadlineUtc:DateTimeOffset?, RequireSecurityAudit:bool, OwnHeadsVisibility:ReviewOwnHeadsVisibility, Round:RoundSnapshot`。`OutcomeRule(Id:string, AllowedReasons:ImmutableArray<string>, ReasonRequired:bool, AllowedObservability:ImmutableArray<ReviewObservability>, RequiredObjects:ImmutableArray<ObjectRef>)`；RoundSnapshot=`Ref:RoundRef, Assignments:ImmutableArray<AssignmentRef>, RequiredAssignments:ImmutableArray<AssignmentRef>, DependenciesHash:string`；必审子集/唯一性/版本由Owner验证，无默认阈值 |
| `IEvidencePort` | `OpenAsync(EvidenceReadRequest, ct):ValueTask<EvidenceReadReceipt>`；`ValidateSnapshotAsync(ReviewBinding, string snapshotHash, ct):ValueTask<bool>`，false即冲突不再读latest补齐。`IReviewEvidenceLease:IAsyncDisposable` 提供 `ReadAsync(ObjectRef, long offset, Memory<byte> destination, ct):ValueTask<int>`、`Revoked:CancellationToken`；offset字节≥0/请求对象内范围，返回0仅真EOF，短读循环仍计总预算；失败清未发布字节且真实排空。宿主Viewer解码，不在Core构建图像 |
| `IReviewLeaseSecurityPort` | `PrepareAsync(ReviewWriteIdentity, LeaseRef, ct):ValueTask<PreparedLeaseSecret>`；`ValidateAsync(ReviewLeaseCredential, ReviewWriteIdentity, IReviewAuthorizationLease, ct):ValueTask<bool>`；`DeliverAsync(OperationStatus, IReviewAuthorizationLease, ct):ValueTask<LeaseDeliveryResult>`，result=`Delivery:ReviewDeliveryState, Credential:ReviewLeaseCredential?`；仅Granted有凭据。服务内实现由下述公开安全工厂提供，不要求外部代码伪造opaque句柄。Prepare生成临时token及持久材料；Validate核当前verifier/lease/主体，不只比较Id；Deliver核当前租约/epoch/审计/key并解原材料，不生成新秘密。Core整合返回Delivery，不能要求适配器修改不可变入参。后台借用计数，调用者Dispose撤销新借用，最后一次借用结束才清零 |
| `IReviewSecurityAuditPort` | `ReadAsync(OriginalOperationProof, ct):ValueTask<SecurityAuditResult>`只读原审计；`ConfirmAsync(OriginalOperationProof, ct):ValueTask<SecurityAuditResult>`仅续原审计；result=`State:ReviewAuditState, AuditRef:ReviewRef?`，端口只返回Pending/Confirmed/Unavailable，Confirmed必有引用；同原receipt幂等，不包含token或明文草稿。不改变Proof.Outcome；只有Policy显式不要求才不调用 |
| 时钟/诊断/观察者 | `IReviewClock`提供`UtcNow:DateTimeOffset, Epoch:Guid, GetTimestamp():long, GetElapsed(long start,long end):TimeSpan`；单实例频率由实现固定、epoch变使旧capture失效。`IDiagnosticsPort.Report(ReviewDiagnostic)`；diagnostic=`DiagnosticId, RequestId, Stage:string, Code, Elapsed:TimeSpan, ResourceCount:long`仅脱敏。`IReviewObserver.OnNext(ReviewEvent):void`；Subscribe返回幂等退订句柄，异常被隔离并报告，不执行业务写 |
| `IReviewRecoveryJournal`（宿主Integration） | `ReadPendingAsync(ReviewOrigin, ct):ValueTask<ImmutableArray<ReviewWriteIdentity>>`；`SavePendingAsync(ReviewWriteIdentity, ct):ValueTask<JournalResult>`；`CompleteAsync(ReviewWriteIdentity, OriginalOperationProof, ct):ValueTask<JournalResult>`；JournalResult=Saved/AlreadySame/Conflict/Unavailable/CapacityExceeded。保存按精确identity CAS，完成只接受原终态；未知/网络错不得Complete；保存失败零发送 |
| `IReviewDraftRetentionPort`（可选宿主能力） | `CanRetain(ReviewBinding, ReviewOrigin, long selectionGeneration):bool`，同步只检查原来源/绑定，false保持失败锁存，不发RPC/取得新观察或返回授权；未注入默认false；只管未发送内存草稿，不持久化 |

所有端口异步返回前报告真实短借用已结束；若无法确认，保持活动call并在Core排空账本查询，不丢后台Task。Repository/证据/安全Adapter须支持自己的实际终止/排空；不接受仅用WaitAsync超时伪装实际完成的实现。跨进程Adapter必须在自己的发送边界持久标记MayHaveSent，Core能区分提交前零发送和结果未知；这是Adapter契约，不从exception类型猜测。

Claim提案在新写分支按权威Clock.UtcNow/epoch创建新Guid、Generation=该Item历史最大代+1（首次1），Renew同Lease.Id、Generation+1；期限是当前UTC+TTL且不越Policy.DeadlineUtc。Repository在事务线性化点核同一权威epoch、未过最早单调期限、无新租约/版本变化才接受，不能按客户端UTC信任提案。epoch变化使活动租约不可恢复，但保留历史证明；两个消费者的服务权威时钟一致，独立本地计时器只限观察预算。

`HumanReviewLeaseSecurityFactory.Create(IReviewKeyProtectionPort keys,IReviewLeaseMaterialStore store,IReviewClock authorityClock):IReviewLeaseSecurityPort` 是公开默认安全实现构造入口，同步零IO；只实现本协议，不内建远端RPC。`IReviewKeyProtectionPort.AcquireAsync(ReviewKeyPurpose purpose,string? keyId,Guid? epoch,CancellationToken):ValueTask<IReviewKeyLease>`；purpose=Verifier/Envelope，空标识取得当前获准key，指定标识只能解析原key。key lease提供`KeyId:string, Epoch:Guid, Revoked:CancellationToken, CopyKey(Span<byte>):void, CreateUniqueNonce(Span<byte>):void, ValidateCurrent():void`及IAsyncDisposable，CopyKey仅32bytes、nonce仅12bytes；受控安全实现短借用复制并finally清零，禁止普通消费者取得key。Verifier与Envelope不得同key。

`LeaseSecretMaterial` 为仅持久边界使用的不可变类型：`Schema:uint, AlgorithmId:string, VerifierKeyId:string, VerifierKeyEpoch:Guid, EnvelopeKeyId:string, EnvelopeKeyEpoch:Guid, Salt:ImmutableArray<byte>, Verifier:ImmutableArray<byte>, Nonce:ImmutableArray<byte>, Ciphertext:ImmutableArray<byte>, Tag:ImmutableArray<byte>, Lease:LeaseRef, Identity:ReviewWriteIdentity`；版本1、AlgorithmId=`HR-HMACSHA256-AES256GCM/v1`，各长度见§9.4，数组深拷贝、ToString脱敏，不进入常规序列化/事件。`PreparedLeaseSecret` 只能由安全工厂实现创建，公开只读`Material:LeaseSecretMaterial`供Repository同事务保存，IAsyncDisposable清零临时明文；持久加密数组保留受控存储中，不冒充明文销毁。AAD的KeyId/KeyEpoch专指Envelope key；verifier key版本由Material保存，未知版/任何篡改一律失败关闭。

`IReviewLeaseMaterialStore.ReadAsync(ReviewWriteIdentity,CancellationToken):ValueTask<LeaseMaterialSnapshot?>`，snapshot字段=`Status:OperationStatus, CurrentState:ReviewState, Material:LeaseSecretMaterial?`，读取同一权威事务，缺原记录为空而非伪造Rejected；Store由宿主实现，与Repository共享同一事实库。安全实现解封后重核授权、CurrentState.ActiveLease/完整Binding/epoch/key，再读取同原材料核没有撤换才交付；Core末次发布再核。非Claim/Renew当前新写以凭据内部原身份读材料，核新Identity.Binding==CurrentState.Binding且凭据代仍有效。外部Adapter无需构造credential，远端请求须在服务进程组合此安全工厂，经单独批准wire接入；本v0.3不公开token导出入口。

`ReviewPorts(Queue:IReviewQueuePort,Repository:IReviewRepository,Authorization:IAuthorizationPort,Policy:IReviewPolicyPort,Evidence:IEvidencePort,LeaseSecurity:IReviewLeaseSecurityPort,SecurityAudit:IReviewSecurityAuditPort,Clock:IReviewClock,Diagnostics:IDiagnosticsPort,Capabilities:ReviewCapabilities)` 使用公开全参构造。Capabilities由组合Owner按实际端口支持声明，内存持久能力必须false，组合提供者对此负责；Factory只读该不可变声明校验ContractVersion/用途，不探测外部连接，Core.Capabilities返回同声明。Factory将本地IO/借用资源计数纳入实例账本；不调用诊断以外的外部端口。Profile/引用/请求均采用表列顺序公开全参构造；有默认值的属性只允许显式可空值或空ImmutableArray，不存在隐式默认Profile。

### 9.6 契约闭包与编解码入口

所有§9表中以`State:名称/…`或`Kind`表示的属性使用下表命名枚举，各值从1按表顺序连续编号；只有bool使用0/1。未声明整数枚举拒绝，禁止借用产品枚举。`ReviewWriteKind`编号已在§9.4明确。

| 类型 | 唯一值序 |
|---|---|
| ReviewCallState | Ready, NotSent, Unconfirmed, Fault |
| ReviewCallDrainState / ReviewDrainState | Released, StillDraining / Drained, StillDraining |
| ReviewOperationResolution / ReviewOperationOutcome | Unknown, Pending, Resolved / Committed, Rejected, Conflict |
| ReviewAuditState / ReviewDeliveryState | NotRequired, Pending, Confirmed, Unavailable / NotRequested, Granted, LeaseUnavailable, AuditPending |
| ReviewOwnHeadState / ReviewOwnHeadsVisibility | None, Present, Unavailable / Allowed, Denied |
| ReviewEvidenceAvailability / ReviewObservability | Available, Missing, Corrupt, Restricted / Observed, Partial, Unobservable |
| ReviewKeyPurpose / JournalResult | Verifier, Envelope / Saved, AlreadySame, Conflict, Unavailable, CapacityExceeded |
| ReviewPurpose | QueueRead, StateRead, EvidenceRead, OwnHeadsRead, ArbitrationRead, OperationRead, LeaseRecover, Claim, Renew, Release, OpinionSubmit, OpinionCorrect, ArbitrationSubmit, FactRead |
| ReviewEventKind | Accepted, Authorized, SnapshotFrozen, LeaseGranted, EvidenceOpened, DraftValidated, CommitPersisting, Committed, Rejected, Conflict, Unknown, ReceiptAvailable, ProjectionRebuilt, ProjectionResyncRequired, Stopping, ResourcesReleased |
| ReviewErrorCode | InvalidRequest, PermissionDenied, LeaseConflict, LeaseExpired, PolicyRequired, PolicyMismatch, EvidenceUnavailable, EvidenceCorrupt, DependencyConflict, IdempotencyConflict, Unknown, TimedOut, StillDraining, SnapshotExpired, CapacityExceeded, PortUnavailable, ProtocolMismatch, SourceChanged, CancelledBeforeSend, Disposed, Stopping, LeaseUnavailable, SecurityAuditRequired |

`ReviewCommand` 为无秘密封闭union，公开派生record：`ClaimCommand(State,RequestedTtl)`、`RenewCommand(State,Lease:LeaseRef,RequestedTtl)`、`ReleaseCommand(State,Lease:LeaseRef)`、`SubmitCommand(State,Lease:LeaseRef,Draft,OwnHead,EvidenceSnapshotHash)`、`CorrectCommand(State,Lease:LeaseRef,Draft,OwnHead,EvidenceSnapshotHash,CorrectionReasonId)`、`ArbitrateCommand(State,Lease:LeaseRef,ContextSnapshot,OutcomeId,ReasonIds,Observability,EvidenceSnapshotHash)`；类型与§9.4相同，属性/构造顺序严格按此。请求转Command由Core比对credential.Reference；Command不授予写入，Repository仅接受Core的有效commit guard。

`HumanReviewCanonical.EncodeRequest(ReviewWriteIdentity identity,ReviewCommand command):ImmutableArray<byte>`；`CreateIdentity(OperationId,IdempotencyKey,ReviewOrigin,ReviewCommand):ReviewWriteIdentity` 自动从Command.State取得Binding/ExpectedStateVersion和Kind并计算SHA256；`VerifyIdentity(ReviewWriteIdentity,ReviewCommand):bool`，结构无效抛ArgumentException，字节/hash不符返回false。EncodeRequest不编码PayloadSha256；不能用CreateIdentity悄悄更新旧操作。`ReviewRef`及各专用引用提供公开全参构造`(string scope,string id,long revision,string sha256)`；强身份构造`(Guid value)`，IdempotencyKey构造`(string value)`，属性分别为Value，不嵌另一层隐含wire对象。`ReviewDrainIncompleteException.Ticket:StopTicket`公开，异常不含原始秘密。所有构造错误在发送前抛ArgumentException，正常端口失败返回ReviewResult，实例被Dispose时仍给可判定Disposed/NotSent而非业务终态。

Ready+OperationStatus.Unknown/Pending表示本次查询获得权威“无记录/仍在处理”，无Proof；Unconfirmed无Value表示本次请求传输结果不明。查询Unknown不授权换key。终态拒绝/冲突的Receipt只证明拒绝记录，AfterState为空；未进入Repository的结构/授权预拒绝为NotSent，无伪造回执。Audit只有Committed且Policy要求时续办，失败不得擦除已提交Proof。

ConfirmAsync自身耐久幂等保存AuditRef；FindAsync/材料Store同权威组合读取其审计状态（由Repository Adapter组合审计Owner的ReadAsync端口，禁止Core私自维护第二表）。审计服务不可用可返回Pending/Unavailable和原Proof，不伪造Confirmed。安全ValidateAsync按credential内部原Claim/Renew来源定位material，与新Identity的主体/Binding/current lease核对，不按新的Submit.OperationId查Claim材料；内部短借用始终由安全实现/Core登记。新写Identity.OriginalOrigin必须匹配当前认证主体/设备/session/权威，恢复查询可在明确授权下改变当前Context但不更改OriginalOrigin；冷新session查历史不默认取得旧session的secret。

非Claim新写分支在AcquireCommitGuard前必须调用LeaseSecurity.ValidateAsync；false返回LeaseUnavailable/NotSent，不能仅靠引用相等写入。Deliver解封后重新计算原verifier并固定时间比较，同时核Material.Identity/Lease与原Proof一致，任一失败不交付。恢复取密返回历史Proof.AfterState，不宣称它仍是最新可写版本；新写前必须显式ReadState取得当前StateVersion/完整Binding及OwnHead，不能使用历史Claim的版本绕过CAS。

幂等唯一键为AuthorityId/SubjectScope/SubjectId/IdempotencyKey（Kind也参与载荷，不能借改Kind复用key）；OperationId同authority也唯一。Repository同时比较key和OperationId，任一已有不同identity均IdempotencyConflict，查原结果先核精确查询资格。所有端口Task原本持续到真实工作完成；若Core用有限等待返回，不把其后Task取消/忽略，登记并观察其异常/迟到结果，Drain.PendingCalls来自仍活动原Task。没有额外猜测的PortUnavailable异常可证明零发送。

读取/查询已发送后的取消、超时或异常返回Fault（相应CancelledBeforeSend仅零发送时可用），Value为空、Error说明本次读取失效，Drain按原Task真实状态；不能产生业务Unknown操作。仅写请求可能发送后用Unconfirmed，且原Identity由Session/journal继续保留。Ready的资源账本Released仅指该调用临时借用，交付lease/presenter副本另计，不表示用户图像资源已归还。

IEvidencePort.OpenAsync必须在MaxBytes累积上限内校验获准对象/Manifest并形成受控暂存，Available才有VerifiedBytes和可读lease；缺失/受限不创建假空字节，全部非Available时Lease为空。Observed只表示对象完整读取校验完成，尚未呈现也不证明人工已看；所需总字节超限拒绝而非截断为完整。返回lease由接收调用者拥有并DisposeAsync；Core持有账本归还标记至Dispose实际完成，Open失败产生的未转移资源由Core/Adapter归还。ReadAsync每次跨await和发布核撤权、预算、scope；权限撤回锁存禁止继续读，已有Viewer像素由宿主同步遮盖。

最小Host为Core.Tests中同测试程序集内的内存组合，使用可控IReviewClock、单锁原子Repository、故障注入Queue/授权/证据/Policy/安全审计、受控假对象字节；两个实例共享Repository模拟两个消费者，各自身份/本地观察计时捕获/缓存/事件/journal独立；服务权威Clock按§10.1共享。不给这些夹具生产证书/耐久能力。生产端口以公开语义接入；不把宿主ViewModel或其它模块实现DLL引回Core。

### 9.7 Adapter 的确定实现配方与持久边界

本节关闭I1范围内可由软件设计决定的欠账；实现落在§16宿主Adapter工程，采用§9.5公开端口，不另发产品Schema或第二Review API。Core自身仍只引用BCL。适配器使用注入的实际服务对象，不按名称查全局容器；每个异步Task持续到实际驱动调用结束，Core/Host有限等待可先返回但Root继续持有原Task。跨进程连接/认证/数据拓扑由部署Owner提供，不据此省略以下确定逻辑。

| Adapter | 构造依赖、确定处理与失败 |
|---|---|
| Repository/MaterialStore | 同一Review事务Owner持有的IM-066 `IStorageDatabase`、注册binding/codec版本、当前授权fence和权威Clock；借用而不Dispose Runtime。按下面单事务步骤实现ReadState/OwnHeads/Arbitration/Find/Commit及材料读取；现行状态与历史Proof分区，绝不从UI缓存查“已提交” |
| Authorization | 宿主可信身份/会话验证服务、当前authority状态、用途策略和实际CommitOwner；Origin六字段逐个匹配认证结果，Observation与Binding精确关联。读核当前授权/最早期限；提交按[authorization §8.2](../authorization/DEVELOPMENT-GUIDE.md#82-实际-commitowner首版提交与撤权协议)与撤权共用权威线性化点。前后两次RPC均通过仍不够；不能协调该事务的生产绑定拒写，不向Core返回假guard |
| Policy/Queue | 宿主批准不可变Policy目录及Review事实读取服务。Policy按Ref全字段取冻结版本，AllowedOutcomes/理由/可观察性/必需对象逐个校验，无推荐默认。Queue按获权queryRef生成同scope快照及keyset cursor；分页失效按§5.1重启。使用IM-045通用查询时仅适配其公开API；不下载全表在本地过滤或把隐藏分数作排序 |
| Evidence | IM-015获准`IInspectionEvidenceReader`/已提交Manifest/对象关系目录、用途授权、受控内容读取lease；按[证据唯一指导](../inspection-evidence/DEVELOPMENT-GUIDE.md)的IInspectionEvidenceReader.ReadAsync→IEvidenceReadLease.CheckDeliveryAsync/ReadChunkAsync→DisposeAsync/ObserveResources链映射。固定原receipt和object digest，完整读取/校验后返回§9.6受控暂存；MaxBytes为所有对象累计，含短读/暂存预算；hash不符Corrupt，撤回/缺失Missing，无权Restricted，不回填latest。原Owner输出的坐标/尺寸/单位只作为获权元数据，不从相邻图或文件名推断；生产缓存/文件根由Owner持有 |
| KeyProtection/Security | 提供者按§9.5返回原keyId/epoch的32byte独立Verifier/Envelope key及唯一12byte nonce；当前key用于新Prepare，旧key仅在原仍有效且未撤销期限内解封，未知/撤销epoch拒交付。调用者不用CopyKey，默认安全工厂短借用/清零；固定算法/长度/域无自动弱算法降级。nonce唯一性跨所有共享key实例/进程/重启保障，不能只用Host内计数证明生产唯一性 |
| Audit/Journal | 独立安全审计Owner保存原Proof/AuditRef，Confirm幂等；Repository原事务保存PendingAudit意图，查询读审计Owner当前状态。Journal按Origin权威域/主体索引非秘密Identity，Save/Complete CAS、未决不驱逐、失败零业务发送；重启只查原操作。二者不能互替，不把文本日志当任一耐久事实 |
| Clock/Diagnostics | Clock由服务事务权威签发统一epoch；本地TimeProvider单调捕获只计预算。重启epoch改变需拒旧租约而保留Proof。诊断只记录§9.5白名单阶段/Code/计数，不记录payload、note、密文、salt或token；来源失败返回脱敏DiagnosticId，不执行自动恢复业务 |

**Repository逻辑存储模型。** ReviewOwner登记以下唯一技术集合，不读取产品私表；Head.MaxLeaseGeneration初态为0，有ActiveLease时必须≥其Generation，释放后不回退：`Head[(AuthorityId,WorkItem.Scope,Id,Revision)] = ReviewState + maxLeaseGeneration`；`Operation[(AuthorityId,OperationId)] = 原Identity/ReviewCommand/OriginalOperationProof及PendingAudit意图`；唯一索引`(AuthorityId,SubjectScope,SubjectId,IdempotencyKey)`关联同Operation；`LeaseMaterial[(AuthorityId,Lease.Id,Generation)] = LeaseSecretMaterial`；`Opinion[(AuthorityId,OpinionRef)] = 原Draft/主体/Assignment/Predecessor/Receipt/RecordedUtc`；`Arbitration[(AuthorityId,ArbitrationRef)] = 原仲裁命令/完整权威依赖摘要/Receipt`；`Journal[(AuthorityId,SubjectScope,SubjectId,OperationId)] = Identity/完成Proof?`。Scope参与每项查找与授权，不按裸Id合并。同一Item更正链与头、lease材料、原回执/outbox及水位在同事务变化；元数据与证据文件封口不跨介质伪造原子。

物理存储采用IM-066注册Owner bindings而非透传SQL。注册OwnerKey=`human-review/<AuthorityId>`，schema/codec=`HumanReviewOwnerStorage/1`，事务binding=`review.commit@1`（Serializable、MaxRetries=0、单Item命令、空batch=false）；read bindings=`review.state/own-heads/arbitration/operation/lease-material@1`（RepeatableRead、只读），journal bindings=`review.journal-save/complete/pending@1`，audit与其Owner独立绑定。注册前提供完整输入/结果codec和有限字节/命令/affected-row上限，技术权限分别read/write/query/audit，不能一张业务“审核员”角色代替存储技术权。宿主依实际IM-066公开`StorageBindingDescriptor/StorageBindingCatalog`填技术配置和statement catalog，由ReviewOwner拥有迁移；没有正确注册/codec即ProtocolMismatch/零提交，不自动建表或用Execute任意SQL。注册输入/结果codec分别核下面固定PortInput与对应§9返回值，数据库持久记录使用下面OwnerStorage codec；Context的CT/Budget/当前认证观察不持久化或授予业务权；物理statement只实现下面的固定读取/CAS/追加，不重解释业务Outcome；DB连接/表命名是部署选择，算法和Owner不是待决项。

**注册输入闭包。** 每个binding用exact CLR强类型，不接自由object；`HumanReviewPortInput/1`头为域字符串、schema u32=1、binding kind u8（按下面1..9），Body按列序和§9.4原语编码。1 commit=`Identity,Command,ProposedLease:LeaseRef?,Material:LeaseSecretMaterial?`（取PreparedSecret.Material的独立不可变副本）；2 state=`WorkItem,Policy`；3 own-heads=`Origin,State,Items`；4 arbitration=`Origin,State`；5 operation=`Original`；6 lease-material=`Original`；7 journal-save=`Identity`；8 journal-complete=`Identity,Proof`；9 journal-pending=`Origin`。具体类型全部取§9，不复制Context/guard/credential/等待预算；读取投影另依本次可信Origin核权，不能让payload中的Origin替代认证。commit的Lease/Material可空组合与Kind/Command/Identity逐字段一致，Claim/Renew必须有，其它必须无；材料和AuthorityEpoch/当前guard由服务端权威核验。结果分别用§9.5的ReviewCommitResult、ReviewState、OwnOpinionHeads、ArbitrationContext、OperationStatus、LeaseMaterialSnapshot?、JournalResult、JournalResult、Identity数组，域`HumanReviewPortResult/1`/schema1/kind同输入，按原字段顺序编码且有界；Evidence流/安全句柄不进入DB结果。技术StorageRequestHasher按IM-066原公开公式计算另一层hash，不替换HumanReview原Identity；参数解码完成后再执行固定事务，不能仅信任上游技术hash。

注册限额由确定公式生成：所有input/output编码≤Profile.MaxRequestBytes，超过拒绝不截断；commit MaxCommands=16、MinAffectedRows=0/MaxAffectedRows=6（唯一索引不计额外行，重放只读可为0）、MaxRetries=0/RetryDelay=TimeSpan.FromTicks(1)（符合IM-066正有限配置，次数0故不执行延迟）、ServerLockTimeout/ServerStatementTimeout均≤本次Commit剩余预算；journal save/complete单行CAS、MaxCommands=4/MaxAffectedRows=1，pending读取最多Profile.MaxPendingOperations；其它read MaxCommands=4/MaxAffectedRows=0、返回集合受MaxHeadsItems/MaxParents/MaxPageItems限制。批量请求不得扩大这些binding范围。连接/PoolPurpose由IM-066注册配置显式填、整体Root/DB限额同时取小值；真实provider不支持该隔离/timeout/CAS时拒该生产绑定，不换较弱隔离。MinAffectedRows=0不是成功证明，Head应变化分支必须恰1，Opinion/Arbitration/Operation/Audit意图按本次新写种类分别核1，否则事务失败而非签Proof。

新写单事务顺序唯一为：①锁精确Head及两个唯一幂等索引，先解析原Operation；已有同内容立即返回原Proof，无新状态/随机材料；异内容记明确冲突但不覆盖原记录。②核当前授权fence、epoch、期限、StateVersion和完整Binding，再核active lease代/排他、Policy及证据snapshot、OwnHead/全部仲裁父头。③Claim/Renew存Prepared材料并更新代，Release仅置本代inactive，Submit/Correct/Arbitrate追加原不可变命令和Owner新引用；StateVersion+1/Watermark+1，水位在同authority内单调、溢出拒写。④同事务保存Proof/Receipt和PendingAudit意图/lease材料/索引，提交后才ConfirmAudit与可交付投影。冲突/拒绝的原终态记录不递增Item版本，预认证/结构拒绝无持久操作。DB serialization/唯一索引竞争终止后先Find精确原Identity；没有权威证明仍Unknown，不自动换key/重试新写。普通读不阻塞人工输入；提交事务不等待证据解码、远端授权RPC或安全审计。

引用由ReviewOwner在事务接受后生成（Guid字符串ordinal、revision1），Receipt/Opinion/Arbitration分别强类型；RecordedUtc为权威接受UTC。为避免Receipt↔Opinion及自引用hash循环，生成引用的Sha256只覆盖不可变身份描述：域字符串`HumanReviewReference/v1`、schema u32=1、Kind u8（Receipt1/Opinion2/Arbitration3）、Scope/Id字符串、Revision Int64、完整原ReviewWriteIdentity（含PayloadSha256）、RecordedUtc，按§9.4原语编码；描述同事务保留，实体存储记录另有完整记录hash，不能拿身份描述hash证明实体未损坏。OwnHeads定向读取主体精确最新链头；链损坏不回退，None只在同事务证明没有记录时返回。仲裁摘要由Owner对完整有效父头/分配/策略/证据规范字节计算，不从可见ParentRefs推完整集。读取裁剪字段不能改变内部原命令/原Proof；不具备披露原Proof字段资格时返回PermissionDenied，不能返回截断后仍冒认原Proof的hash。

**存储codec闭包。** `HumanReviewOwnerStorage/1`使用§9.4相同原语（所有声明枚举u8、Int64大端、Guid网络序、UTC100ns、严格UTF8/可空/数组），header=`domain字符串 + schema u32=1 + recordKind u8`，recordKind按Head/Operation/LeaseMaterial/Opinion/Arbitration/Journal/PendingAudit顺序1..7。Body按本段集合值中字段顺序，关联类型字段按§9.3–9.6声明顺序，Command先Kind再其§9.6业务字段；Identity按§9.3列序编码，其末字段包含PayloadSha256（不是把整个Identity挪至record末尾）。Operation.Proof可空表示权威Pending，不等Committed；Journal完成Proof可空。Prepared对象/Task/guard/credential/CT永不序列化，LeaseMaterial只有加密材料；固定salt/verifier/nonce/tag用固定16/32/12/16 raw bytes，Ciphertext=`u32长度+bytes`（本协议token密文必须32bytes），没有UTF8/Base64替代。验证尾随字节/长度/重复索引/版本/跨scope/引用hash/状态组合，坏记录EvidenceCorrupt或ProtocolMismatch，不签终态。严格canonical request仍是原HumanReviewCanonical/v1，存储header不参与其载荷hash，HR-G01不变化。

上述Body的唯一具体字段如下，按列序公开不可变record或Adapter内部同列强类型实现；不将“集合值”实现为自由JSON：Head=`State:ReviewState,MaxLeaseGeneration:long`；Operation=`Identity:ReviewWriteIdentity,Command:ReviewCommand,Proof:OriginalOperationProof?,PendingAudit:ReviewPendingAuditIntent?`；LeaseMaterial=§9.5 LeaseSecretMaterial字段全序；Opinion=`Draft:ReviewOpinionDraft,Origin:ReviewOrigin,Assignment:AssignmentRef,Predecessor:OpinionRef?,Receipt:ReceiptRef,RecordedUtc:DateTimeOffset`；Arbitration=`Command:ArbitrateCommand,FullParentHeads:ImmutableArray<OpinionRef>,FullAssignments:ImmutableArray<AssignmentRef>,DependenciesHash:string,Receipt:ReceiptRef,RecordedUtc:DateTimeOffset`；Journal=`Identity:ReviewWriteIdentity,CompletedProof:OriginalOperationProof?`；`ReviewPendingAuditIntent`=`Identity:ReviewWriteIdentity,Proof:OriginalOperationProof,Policy:PolicySnapshotRef`（仅Committed且RequireSecurityAudit=true才有）。完整record hash为SHA256(header+Body)，保存于受控外列，不参与自身Body；读取先检hash、再解析各字段/关系。版本/容量和完整性拒绝都在进入持久事实前完成，Proof和LeaseMaterial索引只接受已核同原Identity。

codec/表版本升级由ReviewOwner按§15 expand/验证/切换执行，旧版本不理解新状态时只读拒写。与IM-066 technical OperationId分开保存关联；技术提交成功必须核同原mutation/hash和受影响行数，技术超时查询原技术操作再恢复Review原Operation，不能凭存储Task结束宣称意见提交。Opinion历史和幂等事实按Policy/RetentionOwner获准保留，达到部署容量只拒新写并允许原查询，不能清除未知记录腾位。内存和真实DB适配执行同规则，耐久/撤权线性化/断电资格必须实测。

远端站的网络客户端属于宿主应用边界：v0.3的Core/安全句柄协议是进程内，station不自行序列化credential/token、不能直接打开服务器私有数据库文件。远端调用通过宿主获准的服务端Review命令门把原Identity/无秘密ReviewCommand/当前认证Context送给同一权威，服务端执行此完整算法并保存原操作；认证传输租约、连接和endpoint generation由Host transport持有。若需要跨进程交付可携带秘密的claim句柄，必须在产品transport契约冻结此密钥交付协议后接入，不能把本地opaque句柄当现有wire格式。此为明确模块不适用边界；当前模块不创建HTTP/消息总线协议，不接管产品跨站登录或终端路由，但其幂等/查询/有限IO/失败关闭不因远端省略。

## 10. 无 UI API 与可选 WPF UI

### 10.1 无 UI 最小调用

无UI与WPF统一使用以下公开宿主装配入口；这些是Core内的技术生命周期/恢复工具，不持有产品最终事实。`ReviewHostRoot(int maxSessions)` 在进程入口、任何Factory之前构造，maxSessions>0且有限；公开 `Open(ReviewPorts,ReviewProfile,IReviewRecoveryJournal):ReviewHostSession` 同步预留槽→校验→创建Core+命令facade，失败回收槽且零IO；满返回抛`ReviewHostCapacityException`。Root由进程服务字段强持，不能仅用方法局部变量或Window字段代替；不拥有借用ports的释放权。

`ReviewHostSession`提供`Core:IHumanReviewCore`（facade）、`SessionId:Guid`、`CloseAsync(StopRequest,CancellationToken):ValueTask<DrainReceipt>`、`QueryCloseAsync(DrainQuery,CancellationToken):ValueTask<DrainReceipt>`、`DisposeAsync():ValueTask`。facade完整实现§9.1，只增加同Item互斥gate、SavePending/Complete和原Task保管，不另判断业务；每次写在调用Core前冻结Identity并SavePending，Saved/AlreadySame才发送，保存Conflict/Unavailable/CapacityExceeded返回NotSent。已知未决同Item只允许原查询/取密；查询精确终态自动Complete，完成失败保留阻断。读取不持写gate，Core仍核权限。Journal也计Total及在途/排空，保存等待超时仍强持原Task；即使迟到Saved也不继续发送，记录留给精确查询，不声称原业务失败。

facade产生的CallDrainReceipt包括journal在途，Close的PendingCalls/UnresolvedWrites/BorrowedResources合并Core与facade账本；Facade的StopAsync/QueryDrainAsync分别代理CloseAsync/QueryCloseAsync，ticket由Session一次产生并映射唯一Core stop ticket。Root每槽强持Session、原调用Task、深拷贝请求/原Identity、借用授权/证据/凭据、发布generation、原业务错误和cleanup错误；返回Unconfirmed或StillDraining不丢Task。句柄Dispose和lease.DisposeAsync应显式在独立cleanup阶段调用，不能先等Core账本为零造成死锁。

`ReviewHostRoot.ReadPendingSessions():ImmutableArray<Guid>`；`TryRelease(Guid sessionId):bool` 仅Session Dispose成功且本地所有IO/调用者lease归还后才移除槽；`Adopt(ReviewHostSession session):bool` 只能显式接受同进程来自另一Root的未释放Session，目标先预留槽、强持全部原对象，再原Root确认移除，任一步失败原Root继续持有。跨进程不能搬Task/句柄，只能用已保存原Identity冷恢复。无隐式后台轮询/自动续租；进程服务按显式人工/调度请求QueryClose，保持Root到释放确认。进程终止不伪造ResourcesReleased，已保存journal由下一进程恢复。

#### 10.1.1 Core.Tests 合成装配（完整有限值）

本节builder只存在测试程序集，同一源文件可链接到Integration.Tests，不引用Core.Tests Exe。以下是完整合成输入，非客户默认、非生产凭证；不改变已接收C1/C2方法/codec及HR-G01。`FixtureAuthority.Create():AuthorityFixture`同步创建单锁Repository、同库MaterialStore、Clock和只读Seed；`CreateHost(AuthorityFixture,char subject,Guid sessionId,AuthorizationMode,bool allowOwnHeads,ReviewLanguage):HostFixture`只接受A/B/C（C为获准并发测试主体），先创建进程服务字段持有的Root再Open，失败按§10.1归还，不能在方法返回时丢Root。

```csharp
// Exact synthetic Profile, constructed independently for each host; declarations, not run.
var profile = new ReviewProfile(
    ProfileRef: new ReviewRef("s", "profile-test", 1, new string('5', 64)),
    MaxIdentifierUtf8Bytes: 256, MaxRequestBytes: 65536,
    MaxPageItems: 2, MaxHeadsItems: 2, MaxParents: 4,
    MaxEvidenceObjects: 4, MaxReadBytes: 1048576, MaxConcurrentCalls: 8,
    MaxEventBuffer: 32, MaxPendingOperations: 8,
    MaxLeaseTtl: TimeSpan.FromSeconds(10), MaxTotal: TimeSpan.FromSeconds(2),
    MaxQueueWait: TimeSpan.FromSeconds(1), MaxEvidenceRead: TimeSpan.FromSeconds(1),
    MaxCommit: TimeSpan.FromSeconds(1), MaxDrain: TimeSpan.FromSeconds(1),
    BenchmarkPlan: new ReviewRef("s", "bench-test", 1, new string('6', 64)));
var requestBudget = new OperationBudget(TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(1),
    TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1));
// Cleanup is a NEW object/token, not a child of request cancellation.
var cleanupBudget = new OperationBudget(TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1),
    TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1));
```

`Seed.Ref<T>(string id,char hashDigit)`仅fixture辅助：返回T的公开四参构造`("s",id,1,new string(hashDigit,64))`，不是产品API或缺省hash算法；Seed登记这些精确不可变metadata身份和归属，不能凭数字相等认关系。对象hash另按实际字节校验。全部输入如下：

| Seed输入 | 确定值/映射 |
|---|---|
| WorkItem/Question | ItemA=`ReviewWorkItemRef(s,item-A,1,a×64)`、ItemB=`(s,item-B,1,b×64)`；QuestionA=`ReviewQuestionRef(s,question-A,1,c×64)`、QuestionB=`(s,question-B,1,d×64)`；Question归其同名Item |
| 其它绑定 | EvidenceA/B=`EvidenceSetRef(s,evidence-A/B,1,e/f×64)`；Assignment=`AssignmentRef(s,assignment-1,1,7×64)`；Policy=`PolicySnapshotRef(s,policy-1,1,1×64)`；Round=`RoundRef(s,round-1,1,2×64)`；Assignment登记subject-A及subject-C的排他资格，不给B写权；Round的Assignments/RequiredAssignments均=[Assignment] |
| State/证据 | 每Item初始StateVersion7/Watermark0/ActiveLease=null，ReadProjectionHash=8×64，UnresolvedQuestions=[其Question]。ManifestA/B=`ManifestRef(s,manifest-A/B,1,9/a×64)`；E1=`ObjectRef(s,E1,1,be45cb2605bf36bebde684841a28f0fd43c69850a3dce5fedba69928ee3a8991)`实际字节00..0f；E2=`ObjectRef(s,E2,1,b×64)`Restricted，E3=`(s,E3,1,c×64)`Corrupt；两Evidence集合登记同E1/E2/E3及各自Manifest，不声称E2/E3已验证 |
| Policy | `OutcomeRule("O1",[],false,[Observed],[E1])`、`OutcomeRule("O2",["R2"],true,[Partial],[])`、`OutcomeRule("U",[],false,[Unobservable],[])`；AllowedOutcomes三者原序，CorrectionReasonIds=[C1]，AllowedArbitrationOutcomes=[上述O2和U的完整OutcomeRule]；MaxLeaseTtl10s、DeadlineUtc=null、RequireSecurityAudit=true、OwnHeadsVisibility=Allowed；Round.DependenciesHash=3×64。HR10另显式seed父集及其摘要，不从空初态猜仲裁 |
| Queue/排序 | Queue=`ReviewRef(s,queue-1,1,d×64)`、Query=`(s,query-1,1,e×64)`、Snapshot=`(s,snapshot-1,1,f×64)`；初始两行A/B、DisplayId=item-A/B、EligibilityReasonId=null；排序按Id ordinal，快照保持30s单调期限；PageSize2，首cursor=null，第二页按keyset。HR02有100000行和空页脚本，输出仍最多2行 |
| Clock | authority-test，EndpointGeneration1；ControlledReviewClock UTC=2026-10-11T00:00:00Z、Epoch=11111111-1111-1111-1111-111111111111，timestamp0、frequency1000000Hz；`Advance(TimeSpan)`推进单调戳/到期计时及UTC，`SetUtc(DateTimeOffset)`只改UTC，`ChangeEpoch(Guid)`锁存旧租约失效；各Host独立capture，服务权威Clock唯一共享 |
| Origin/观察 | `new ReviewOrigin("s","subject-A/B/C",null,sessionId.ToString("D"),"authority-test",1)`；sessionId=A为aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa、B为bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb、C为cccccccc-cccc-cccc-cccc-cccccccccccc；AuthorizationObservation=`ReviewRef(s,auth-A/B/C,1,a/b/c×64)`；可信fixture认证仅接受登记的完整Origin，不接受调用方改Subject |
| 请求/操作标识 | 每Host独立计数n从1；Request/Operation Guid用RFC4122字节`u32槽(A1/B2/C3)||u32域(Request1/Operation2)||u64 n`，生成后按§9.6公开构造；key=`hr-A/B/C-n`。ContextFactory(purpose)创建新RequestId、原Origin/观察、purpose、requestBudget；身份使用CreateIdentity，不手填payload hash |
| 授权/权限 | FullReview允许所有本Core用途及显式FactRead白名单；ImageOnly只允许QueueRead/StateRead/EvidenceRead与本人原操作查询，禁FactRead/OwnHeads/LeaseRecover/全部写；无业务操作的OperationRead为Unknown。lease/guard.RemainingLifetime=2s，单锁当前撤权状态与Repository提交共用同事务线性化点；`Revoke()`/`SeedCurrentOrigin(...)`受控且不复活旧capture |
| key/nonce | 每Host独立KeyProtection实例，Verifier keyId=verifier-test-1/epoch22222222-2222-2222-2222-222222222222/32bytes00..1f；Envelope keyId=envelope-test-1/epoch33333333-3333-3333-3333-333333333333/32bytes20..3f。nonce=`u32槽(A1/B2/C3)||u64本Host计数`，从0开始，12bytes大端，故A首值000000010000000000000000、B首值000000020000000000000000；原Host冷恢复继续计数，不从0重开，同key/nonce重复或溢出失败关闭。固定key仅合成；默认安全工厂token/salt仍用BCL CSPRNG，不引入可预测生产随机源；HR-G03单独纯算法向量用固定token00..1f/salt40..4f/nonce000000010000000000000000，不拿向量token当实际Claim |

每Host固定装配顺序（以下名称均是同源fixture内构造器/方法的精确定义，不是额外公开产品依赖）：

1. `root=new ReviewHostRoot(2)`由fixture进程服务集合强持；`profile=上述全参值`、Origin/ContextFactory/计数器按Seed产生。
2. `authorization=new MemoryAuthorizationPort(authority.Repository,authority.Clock,origin,mode,allowOwnHeads)`；Repository提供其内部短事务锁而非公开SQL句柄，Observe/guard与撤权使用同锁。`policy=new MemoryPolicyPort(Seed.Policy)`、`queue=new MemoryQueuePort(repository,Seed.Queue,Seed.Query,clock,authorization,30s)`、`evidence=new MemoryEvidencePort(Seed.Objects,Seed.ManifestMap,authorization,profile)`均各Host独立；E1有界3-byte短读、完整EOF16，故障前零隐含调用。
3. `keys=new FixedTestKeyProtectionPort(上述key副本,hostSlot,nonceCounter)`；`leaseSecurity=HumanReviewLeaseSecurityFactory.Create(keys,authority.MaterialStore,authority.Clock)`。`audit=new MemorySecurityAuditPort(repository,origin,clock)`把原Receipt的Pending/Confirmed关联存Repository同事实表的Audit区；各Host对象独立，恢复时可读取别实例已为同获权原receipt保存的审计状态，不能从自身空缓存当未审计。`ConfirmAsync`按原receipt幂等产生`ReviewRef(s,audit-<OperationId>,1,4×64)`；合成且非耐久。
4. `diagnostics=new MemoryDiagnosticsPort(32)`、`journal=new MemoryRecoveryJournal(origin,8,65536)`、`events=new HostObserver(32)`各自独立；满拒新记录，未决不驱逐。`capabilities=new ReviewCapabilities("0.3", 所有Core用途及FactRead, true,false,true)`各Host同技术能力声明，权限只由authorization判断，不因ImageOnly把端口能力说成不存在。这样B写调用稳定返回PermissionDenied/NotSent、无持久Proof、Commit=0。
5. `ports=new ReviewPorts(queue,repository,authorization,policy,evidence,leaseSecurity,audit,clock,diagnostics,capabilities)`→`session=root.Open(ports,profile,journal)`→`subscription=session.Core.Subscribe(events)`。`HostFixture`强持`Origin/ContextFactory/Profile/RequestBudget/CleanupBudget/Root/Session/Ports/Keys/Journal/Events/Subscription`，退订先于Session实际释放；语言仅本Host记录zh-CN或en-US，不更改Core/线程全局culture。

`CreateHost(authority,'A',Guid.Parse("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),FullReview,true,zhCN)`；B同形式为ImageOnly/false/enUS；并发Claim专用C为FullReview/true/enUS，不能给B暗扩权。冷恢复A'先保留原journal内容和nonce计数，仅重新取得当前授权Origin；原session秘密交付条件不满足则LeaseUnavailable，查询历史仍合法。复用journal是原Host数据恢复而非A/B共用可变journal。

两Host只共享权威Repository、同库MaterialStore、Clock；其它实例/Root/订阅/语言/授权/缓存/lease均独立，Seed只按值复制。所有fixture异步入口有`Block(阶段)`/`Release(阶段)`确定性闩锁，阶段枚举Observe/SavePending/OpenEvidence/BeforeCommit/AfterCommit/ConfirmAudit/Deliver/Return；`ObserveCounts()`读每阶段调用数及活动Task/lease/guard/root槽，峰值受Profile限制。业务与cleanup错误分开；测试suite释放所有闩锁后归还实际资源，不能靠停止线程判通过。固定nonce脚本只保证该测试key的唯一性；生产密钥/nonce持久计数由批准KeyProtection提供者实现§9.5协议，不用本builder替代。

清理预算是与业务Total独立的新有限OperationBudget（由同Profile上限校验），cleanup token不链接已取消的业务token。Close有限等待到期返回StillDraining；Dispose对未完成抛§8异常并保持原Root槽，不能在finally覆盖原业务错误或提前Dispose借用端口。Caller交付lease的迟到结果由原Root登记，若已不允许发布，直接排空并归还；绝不更新另一请求的选择。Root槽只能随真实归还释放，入口满拒绝新session但既有恢复仍可调用。

```text
process-owned ReviewHostRoot.Open(ReviewPorts, ReviewProfile, journal) -> session.Core facade
ReadPendingAsync(original origin) -> QueryOperationAsync(original Identity)
  unresolved: keep identity; stop new writes for that Item
QueryQueueAsync(queue request) -> Ready + page; empty: show Empty, never index Rows[0]
ReadStateAsync(selected exact WorkItem/Policy) -> current State
ReadEvidenceAsync(State.Binding, authorized ObjectRefs, MaxBytes) -> receipt + owned lease
  bind to current generation; inspect only authorized evidence; no Claim required
ClaimAsync(State, new frozen Identity, requested TTL) through gate + SavePending
  require Ready + Committed proof + Delivery=Granted + non-null credential
  complete journal with exact proof; use returned AfterState, not pre-Claim StateVersion
ReadOwnOpinionHeadsAsync(AfterState, current Item) -> None/Present/Unavailable
human confirms draft; freeze same Binding/evidence/heads
SubmitOpinionAsync(None) or CorrectOpinionAsync(Present), with current Lease/AfterState
  each new write freezes new Identity/hash; SavePending before send
  Unconfirmed: QueryOperationAsync(original Identity), no replacement key
  Ready terminal: verify original proof and complete journal; render receipt's AfterState
ReleaseAsync only if no pending write and explicitly requested with current AfterState
dispose returned evidence lease/credential; StopAsync -> QueryDrainAsync(same ticket)
  local StillDraining: keep ports alive; business Unknown: keep original journal identity
DisposeAsync only after actual drain; host then releases its injected ports
```

此为调用顺序伪代码，所有方法和字段由 §9 唯一 Contract 定义，不保留旧派生示意 API。无 UI Host 不依赖 Dispatcher/Shell/数据库自动发现或先打开窗口。内存恢复只验证语义，跨进程恢复另验真实journal。观察None才首提交、Present才更正、Unavailable停提交；发布前仍核授权/绑定。释放本地 credential 不发送 Release、不撤销服务端意见。

两个从空入口构造的Host按下表实现于Integration.Tests（可复用Core.Tests内存夹具源码，但不依赖产品Shell）。每个Host都有独立进程服务Root、Profile、context工厂、journal、凭据/证据lease局部Owner；共享的仅是测试权威Repository/材料Store/权威Clock。没有隐藏窗口或UI初始化。

| 步骤 | Host A：无UI单项提交 | Host B：无UI恢复/冲突消费者 |
|---|---|---|
| 构造 | new ReviewHostRoot(2)；按§10.1.1 `FixtureAuthority.Create()`/`CreateHost(A)`取得完整Profile/ports/journal/context；LeaseSecurity用公开工厂；root.Open取得session | 同authority调用`CreateHost(B)`取得其已Open的独立Root/session（不得再Open一次），SubjectId=subject-B、SessionId=上述B的Guid D字符串，注入独立授权/事件/journal；不读取A的原头/草稿 |
| 查询 | Context用new RequestId(Guid)、当前Origin/AuthorizationObservation、相应用途及有限Budget；new ReviewQueueRequest(context,queue,query,2,null)；Ready后遍历获权Rows，空页仅检查NextCursor | QueryQueue取得同Item；ImageOnly B 只调用ReadState/ReadEvidence验证当前状态和可见图片，任何Claim/Submit/Correct/Arbitrate调用均由Authorization以PermissionDenied/NotSent拒绝（技术Capabilities不等于权限）；需要并发Claim冲突时另用获准FullReview主体和独立测试Context，不得让B越权 |
| 看图 | new EvidenceReadRequest(context,state.Binding,objects,maxBytes)，Ready且有lease才ReadAsync逐对象、短读循环至VerifiedBytes；末次核撤权后展示/处理人工声明；归还lease | 只读权限仍可看图；结果明细不可见时零读取；撤权立即停止发布并DisposeAsync，A不受影响 |
| 首提交 | new ClaimCommand(state,ttl)→HumanReviewCanonical.CreateIdentity(new OperationId(Guid),new IdempotencyKey(key),origin,command)；new ClaimRequest(context,identity,state,ttl)；facade先持久保存。取得Granted credential/AfterState后new OwnOpinionHeadsRequest；None才new SubmitCommand→新identity→new OpinionSubmitRequest | B更换新分配需由Owner显式提供，不能自动绕冲突。A提交回执丢失时，使用其获准恢复的原Identity（不是B冒认A主体），new OperationQuery(context,original)查询；无取密资格不RecoverLease |
| 结果 | Ready Proof=Committed读取Opinion/AfterState；Unconfirmed保留identity，由用户显式new OperationQuery查询；Pending/Unknown保持gate。更正先Present→new CorrectCommand/新identity，不复用旧提交key | 模拟A关闭后新获准A会话，new OperationQuery精确恢复，Proof里的Opinion/Predecessor足以还原回执；调用LeaseRecoveryRequest只用于原Claim/Renew且当前完整origin取密资格满足 |
| 收尾 | 无未决且显式批准归还才Release；finally先归还本地证据/credential，再用独立cleanup Budget执行session.CloseAsync；Drained且BorrowedResources=0→session.DisposeAsync→root.TryRelease=true，之后才由port Owner释放专属ports | StillDraining保留同Root/session/ticket；显式QueryClose同ticket，业务Unknown留journal但本地可完成Dispose。第二消费者ports共享时由组合Owner等全部session释放后释放，单Host不得提前释放 |

以上构造/调用类型按§9.3–9.6表列顺序，未列类型不能成为实现必需条件。Host入口先记录业务结果，再执行cleanup，最后统一决定退出码：仅指定断言全部完成且TryRelease成功为0；错误、未完成、超时或仍有根槽非零。外层进程截止不能把非零/被杀进程判成功；强制进程结束前由测试闩锁放开IO完成可验证回收。

### 10.2 可选 WPF 控件

可选 `HumanReview.Wpf` 只提供任务列表、证据导航、意见草稿、状态和键盘命令投影，调用同一 `IHumanReviewCore`；不创建自己的状态机、Store、权限判断或提交 API。宿主注入语言、主题、权限投影、PolicySnapshot 和命令路由；控件不放置语言切换器。UI 必须支持三语、UIA、键盘快速下一项、缺证据/Unknown/冲突/盲审状态和关闭排空，并在 1920×1080 固定验证视口下检查长文本、DPI、焦点、无重叠和错误恢复。最终产品页面、AOI 缺陷表单和返修/放行按钮由宿主 PageContract 负责。

### 10.3 本模块 WPF 控件契约与紧凑工作台

本节是可嵌入控件自身 PageContract，产品顶层页面仍归宿主，不改共享 PageContract。公开 `HumanReviewControl:UserControl,IAsyncDisposable`有公开无参构造（零IO）：`Attach(ReviewUiServices):void` 仅一次；`SetLanguage(CultureInfo):void`；`DetachAsync(OperationBudget,CancellationToken):ValueTask<DrainReceipt>`；Dispose遵循§8。`ReviewUiServices`全参字段为 `Core:IHumanReviewCore, ContextFactory:Func<ReviewPurpose,ReviewReadContext>, EvidencePresenter:IReviewEvidencePresenter, Text:IReviewTextResources, ThemeResources:ResourceDictionary, Profile:ReviewProfile, Retention:IReviewDraftRetentionPort?, Facts:IReviewFactProjectionPort?`（固定八参数；Profile须与session创建Profile相同，Facts可空但不可省略）。Core由宿主注入§10.1 session.Core facade；每个控件独占一个Core会话，多个控件共享Repository而不共享当前选项/草稿。控件借用Core/Presenter/资源服务，不Dispose宿主端口；Detach先禁新操作/遮盖→Presenter.Clear真实结束→归还调用者lease/credential→Core.Stop，不先等待仍持有的lease账本为零；超期保留原Task/控件于Root的宿主扩展Owner，之后同ticket查询。成功排空后宿主Dispose控件、session和端口。

`IReviewTextResources.Get(string key,CultureInfo culture):string` 为完整资源服务，SetLanguage只更新当前控件/已开菜单提示，不改线程/应用全局语言、输入备注、身份、草稿或key。未知语言显式fallback en-US并诊断一次，缺key显示同用途安全通用文字并诊断，不显示资源键。`IReviewEvidencePresenter.View:FrameworkElement`只能挂在其STA；`ShowAsync(EvidenceReadReceipt,long generation,CancellationToken):ValueTask`、`ClearAsync(long generation,CancellationToken):ValueTask`只借用获权lease，由宿主公开Viewer组合实现，`Hide(long generation):void`在所属Dispatcher同步遮盖像素/移出UIA后立即返回，不等解码。Presenter拥有解码/纹理副本，Clear实际排空后才能归还证据lease。老generation Clear/Hide不得影响新画面；撤权先Hide/禁命令，后异步清屏/排空。

可选 `IReviewFactProjectionPort`及其值类型声明在Core namespace（纯BCL、无UI），通过`ReviewUiServices`末尾全参字段`Facts:IReviewFactProjectionPort?`显式注入；null隐藏事实详情，不改变合法看图。公开方法`ReadAsync(ReviewFactRequest,CancellationToken):ValueTask<ReviewFactProjection>`；request=`Context:ReviewReadContext, Binding:ReviewBinding, SourceReceipt:ReceiptRef, MaxItems:int, MaxUtf8Bytes:long`，Context.Purpose=FactRead；授权Owner独立核该事实用途，不能从图片权限推导；MaxItems/Bytes均正且受调用Profile.MaxHeadsItems/MaxRequestBytes限制（复用技术投影边界，不混业务分母）。projection=`Binding, SourceReceipt, ProjectionHash:string, Rows:ImmutableArray<ReviewFactRow>`；row=`Source:ReviewRef, LayerId:string, FieldId:string, ValueState:ReviewFactValueState, DisplayValue:string?, UnitId:string?`，枚举按列出顺序从1编码Known/Unknown/NotApplicable/Restricted/Unavailable；仅Known有原值，其余无值，Restricted不披露隐藏Source/FieldId则整行不交付。字段与LayerId由Owner白名单定义，不让Core补建Machine/Final层，单位值原样保存、资源服务只翻译标签。

该端口在入口/跨await/末次发布独立核权、来源完整性/精确已持久receipt/完整Binding，失败清事实但不清仍获权图片；不能用来源latest或产品对象反射替代。STA Owner强持原读取Task/generation，超期不发布且记入其Close/QueryClose的PendingCalls；迟到归还仅原调用，不污染新项。结果为有界不可变文本投影、无SDK/路径/句柄，端口返回必须无未登记后台IO；这是显示端口，不传入Submit进行质量解释。无UIHost需要事实详情时也显式注入并以进程服务Owner强持同原Task，Core事务链不依赖此可选端口。

| 操作链/区域 | 固定布局、控件与交互 |
|---|---|
| 入口与身份 | 顶部一行当前DisplayId、问题、主体可见名、连接/盲审/租约状态；第二行常用命令。标题是“人工复判”，不显示夸大完成或质量放行结论。选择列表只读，不因选中自动Claim |
| 总体工作区 | `DockLayoutManager + LayoutGroup/LayoutPanel`，中央承载宿主EvidencePresenter，左右任务/意见面板可AutoHide，固定状态栏不允许隐藏/浮动。1920×1080物理验证viewport下，从实际控件客户区扣OS任务栏/外框/标题再量矩形；默认任务/图像/意见列约15%/70%/15%，图像交互矩形≥控件客户区60%，专注模式两侧折叠后≥85%。比例是本模块设计验收目标，不是引用AOI旧比例或视觉精度 |
| 列表 | `GridControl + TableView`显式列：显示身份、问题、读取/已提交/未处理状态、当前可用动作；`AllowEditing=false, ShowGroupPanel=false, AllowPerPixelScrolling=true`，行虚拟化，有界page/当前页刷新；不启用本地全库筛选/下载。查询条件变化显式新snapshot；稳定Id联动图像/问题/意见，不以row handle认事实 |
| 多图/多原因 | 仅有真实层次时使用`GridControl + TreeListView`显示Item→已获权证据引用；不从多图推多个Item。同选择generation联动图框、参考/Actual、原值和历史；同对象变换经授权验证才同步定位/缩放，缺变换禁联动，不能凭屏幕位置制造坐标 |
| 意见栏 | 顶部本项进度/可观察性，`ComboBoxEdit`只显示Policy允许Outcome与理由，`MemoEdit`备注，逐项校验紧邻字段；更正显示原可见意见/更正原因，仲裁按批准依赖显示分歧。多项提交是宿主逐项编排和独立回执，不提供“全部PASS”按钮。记录草稿与提交按钮分开 |
| 精确信息 | 用户展开后显示原值/单位/有效性/来源修订/缺证据原因；只读`PropertyGridControl`仅绑定获权白名单DTO、禁止自动枚举原产品对象/句柄/secret；默认折叠。技术参数编辑归宿主parameter-editor，不让操作员改租约/必审/盲审/理由字典 |
| 常驻命令 | 查看上一项/下一项、领取、提交、刷新状态、专注/退出专注及当前安全恢复动作直接可达。Renew/Release只在当前资格满足时显式展示；无隐式续租。次要查看选项放`PopupMenu`，临时原因说明用`DevExpress.Xpf.Editors.Flyout.FlyoutControl`，重要阻断仍常驻状态栏 |
| 提示/底部 | `ToolBarControl/StatusBarControl`（Bars namespace）组合，状态栏分别显示连接、当前lease、操作结果、审计/交付、读取/排空；不合并成绿灯。命令使用`BarButtonItem.SuperTip`，普通控件使用`SuperTipControl`包装；提示含作用/不可用原因/恢复/快捷键，不含凭据或盲审内容 |

视觉：借用宿主冻结主题/token，字体14DIP正文/12DIP次要/18DIP当前对象、8DIP节奏间距、32DIP常用图标按钮、≥36DIP关键按钮；图标+短文字+形状区分状态，NG色不作为未知/未审唯一标识。正常界面少边框、无装饰图表/无阴影盖像素；白名单详情和当前操作用细分隔/轻强调，不用全屏闪烁。Flyout展开/关闭动效120ms、切项不做像素渐变（防旧图混合）；减少动效偏好下动效为0。字号/动效是控件设计值，须实际WPF验证，不是客户节拍目标。

长度适应只在固定验证viewport内改变控件布局：物理宽度转DIP后先将工程详情AutoHide，再折叠左列表，保留图像/当前对象/结果/安全动作；核心提交/Unknown恢复不可放入overflow。命令内容测量后自适应宽度，英语不强行固定汉字宽度；DisplayId可中间省略但获权完整值可复制，错误和未处理原因换行；无横向截断关键数字/单位。用户布局由宿主按语言/角色/Contract版本保存，只保存面板/列配置，不保存数据/权限；恢复后再次检查图像比例/命令可见，布局坏数据只重置该控件默认布局，不删用户原文件。

### 10.4 键盘、状态、错误与 UIA 验收

Tab顺序：任务列表→图像导航→可观察性→Outcome→理由→备注→提交→恢复/关闭。Alt+Left/Right在非文本/IME/Popup焦点时换项，F6切图像/意见栏，F5只显式刷新状态，Ctrl+Enter只在合法编辑区域且IME非组合/无popup/无在途时发一次提交；Enter/数字键不会直接提交。Esc关闭临时Flyout或取消未发送编辑，不撤销已提交事实。自动切下一项默认关闭；提交后保留回执供人核对，下一项是单独选择，不自动Claim。

| 页面态 | 可见内容和唯一安全动作 |
|---|---|
| Empty | “暂无任务”；刷新队列；不生成空Item/意见 |
| Busy | 显示本次读取/提交阶段及可取消等待；同gate禁止连按，选择变化取消读取并等待排空后换generation |
| Ready/Drafting | “未提交”；只有精确当前上下文/lease/证据/前序有效才允许编辑/提交，显示尚未处理项 |
| Stale | “状态已过期”；符合独立保留条件的内存草稿只读；动作“刷新状态”，刷新后人再次提交 |
| Blocked/PermissionDenied | “证据不可用”或“无权查看”；列本项缺失原因/受限状态；禁止相关操作，允许仍合法图片查看或退出 |
| RecoverableError/Unknown | “结果未确认”；只提供“查询原操作”，显示审计/交付阻断独立文字，不显示“未保存”诱导新key重发 |
| Conflict | “内容已改变”；原草稿保留仅限仍获权绑定，显式刷新/查看差异；不得自动替换前序或理由 |
| Completed | “意见已提交”；显示原receipt/更正来源和有权未解决项；不显示“已放行” |
| Closing/StillDraining | “正在结束操作”；禁新写，保留恢复记录；确认真实排空前窗体不能销毁Presenter/端口，超预算给显式重试结束入口 |

资源键的三语示例：`Submit=提交意见/提交意見/Submit opinion`，`RefreshState=刷新状态/重新整理狀態/Refresh status`，`Unconfirmed=结果未确认/結果未確認/Result unconfirmed`，`Recover=查询原操作/查詢原操作/Check original operation`，`Committed=意见已提交/意見已提交/Opinion submitted`，`NotObservable=无法判断/無法判斷/Cannot assess`。产品Outcome文字由其批准资源提供，不能用这些UI词汇创建质量Outcome。

AutomationId为`HumanReview.Queue/Viewport/Outcome/Reason/Submit/RefreshState/Recover/Status`及基于获权稳定Id的行标识；UIA Name/HelpText/LiveRegion只来自同一裁剪投影。Flyout动态内容按25.2官方方法设置`AutomationProperties.LiveSetting`，布局就绪后对已存在peer发LiveRegionChanged；切项/清屏从UIA树移除旧Image，不创建全局peer或保留旧隐藏结果。提示不会替代可聚焦错误文本。

真实WPF验收仅1920×1080验证viewport（按该尺寸核DPI/系统边界，不改显示设置、不扩分辨率矩阵）：三语热切已有菜单/SuperTip/Flyout/错误；100/125/150%DPI在同物理viewport内检查长度/焦点/比例；键盘/IME/连按只发送一次，Unknown后Ctrl+Enter不得发送，撤权清图与UIA树一致，A→B→A迟到失败不清新项，缩放/展开不重复整结果读取，关闭超期仍可查询drain。记录切项/首图/UI Dispatcher滞后、工作集/native/纹理峰值和关闭尾部；不得用HTML原型、截图或VM测试代替上述实际行为。图表/产量看板不属于人工事务控件，确有宿主统计需求时调用其公开统计投影，不能从盲审队列自算。

### 10.5 两个 STA Host 的公开接线与关闭

本节编号保留10章流程：Wpf.Tests中的HostA/HostB各创建独立STA线程（Thread.SetApartmentState(STA)，仅Windows），各自Dispatcher、Window、控件、Presenter.View、ResourceDictionary及session；Core事务只用线程安全端口，不要求Dispatcher。测试进程入口先构造长期`ReviewHostRoot(2)`，两个root槽预留完成才允许开窗，借用ports由组合Owner持有。每个窗口用`new HumanReviewControl()`→`new ReviewUiServices(session.Core, contextFactory, presenter, text, theme, profile, Retention: null, Facts: null)`→Attach→SetLanguage→设置Window.Content；不得把同一FrameworkElement/ResourceDictionary跨STA挂载。

HostA按任务Grid→证据→Claim→草稿→提交链调用同facade；HostB为ImageOnly独立ReviewStation容器，只验证同Item的只读状态、图片和撤权，并断言写用途被拒绝；同Item Claim冲突由另一个显式获准FullReview测试Context验证，Unknown仅按当前获准的精确操作查询范围恢复。A热切zh-CN/zh-TW不改B的en-US、草稿、epoch或焦点；B清屏不释放A的纹理/lease。同一后台权威Repository可共享，任何Window/VM均不进入Core。

WPF借用对象不能直接塞Core字段：公开宿主装配工具`ReviewStaOwner(Dispatcher dispatcher,HumanReviewControl control,IReviewEvidencePresenter presenter,ReviewHostSession session)`（Wpf namespace）由进程服务字典按session.SessionId强持；`CloseAsync(OperationBudget,CancellationToken):ValueTask<DrainReceipt>` 在所属Dispatcher执行Detach并保管原Task；`QueryCloseAsync(DrainQuery,CancellationToken):ValueTask<DrainReceipt>` 有限查询原清理，实际完成前不注销原Dispatcher。`ReviewStaOwner.IsReleased:bool`仅控件与session实际Dispose成功且TryRelease成功后为true，组合Owner据此删除字典/停Dispatcher。控件关闭按钮仅发命令意图，Window.Closing先Cancel=true，禁写/遮盖后await Close；StillDraining可隐藏Window但不能销毁Presenter/关Dispatcher。观察超时留下原STA Owner，后续显式查询同ticket；跨STA禁止同步Invoke/Wait/Result。

Clear/Detach原Task迟到时归还原generation的资源，不发布旧图/恢复命令；cleanup使用独立有限预算与token。窗体正常关闭、创建失败、Attach异常、Viewer异常和资源满都走同Root/STA Owner账本，主业务错误与清理错误分别保留。测试固定1920×1080 viewport、不改显示设置；实现后实际验证两STA窗口关闭、热切三语、IME/UIA和迟到回收，不以文档/VM通过代替真实WPF。

### 10.6 viewport WPF Assembly v0.2 的实际消费与呈现边界

本段属于10章控件装配，使用[viewport §10.6–10.9](../viewport/DEVELOPMENT-GUIDE.md#106-公开bindingunbind与presenter借用)已冻结的Core API0.1/WPF Assembly v0.2（当前上游0.3.5-prep，0.3.4-prep装配契约保持）。不重写其Root/Close/Renderer/HALCON算法，也不让HumanReview.Core引用WPF。标准影像Presenter是本模块Wpf Adapter；其View就是本STA实际`Asun.UI.Viewports.Wpf.ViewportControl`，无窗口的Core无需创建它。其它宿主Viewer也只能实现同§10.3 Presenter接口，不能降低呈现/权限/归还契约。

公开 `ReviewViewportPresenterFactory.Create(ReviewViewportPresenterOptions options):IReviewViewportPresenter` 同步零IO。`IReviewViewportPresenter:IReviewEvidencePresenter,IAsyncDisposable`是本Wpf包的有类型生命周期出口；不改Core或ReviewUiServices八参数。`ReviewViewportPresenterOptions`全参字段：`Control:ViewportControl, Root:IViewportProcessRoot, Session:IViewportSession, Binding:IViewportUiBinding, Sources:IReviewViewportSourcePort, Profile:ReviewViewportProfile`，类型在Wpf namespace、精确借用，不Dispose源服务/借用session。构造只核公开Binding.Session与Session实例相同、非空同Dispatcher及Host保存的原装配关系；私有root/control关联由viewport实际Bind/Commit核验，不能靠文字id相等或不存在的公开属性猜同Owner。`ReviewViewportProfile(MaxSceneBytes:long,MaxSourceBindings:int,OperationTimeout:TimeSpan,CleanupTimeout:TimeSpan)`全部正有限、≤该viewport注册Profile；合成值=(67108864,2,2s,2s)，这是显示资源预算，不能把Core的1MiB证据/请求预算当64MiB viewport可用资源。

标准装配只有一条：进程服务持本窗口自己的viewport Root→同STA new ViewportControl→`ViewportRendererFactory.Create(control,root,rendererOptions)`检查Succeeded/Value→用同返回`Backend`构造ViewportOptions、`Presentation=control.Presentation`→`root.CreateFactory().Create(options)`→Catalog.Get(当前culture)检查完整成功→`control.BindAsync(session,root,new ViewportUiBindingOptions(bindingId,false,resources,2s,Lifetime:renderer.Value.Lifetime,ExecutionBudget:new(67108864,32,32)),ct)`保存原Task及成功binding→new ReviewViewportPresenterOptions→本Presenter工厂→注入ReviewUiServices。所有新资源启动之前已有§10.5 STA Owner及viewport根，Bind失败也沿同原根清理。Lifetime与Backend必须来自同renderer.Owner，不能把返回record当Lifetime。OwnSession=false表示Unbind不关闭借用会话；app的该Session Owner在Unbind/源归还后关闭自己的session/root，HumanReview不能顺手关别人会话。

软件双STA显示夹具Options固定ReadOnly、Navigation|Presentation、OfflineRasterOnly/BudgetOnly、MaxDisplayBytes64MiB、MaxInFlightTiles2、Drain/Operation2s、Limits=(4,32,4096,16,32,64,4096,8,128)，Roi/Surface/Probe/ResourceAdmission/IntentSink=null、UpdateThrottle=null；RendererOptions=(OfflineRasterOnly,0,67108864,2,2s)，RootOptions=(review-A/B,2,256,128,268435456,2s,2)。实际canvas/DPI取控件客户区，不从1920外框猜尺寸。生产EvidenceReview固定HalconRequired/Required，并显式注入实际ResourceAdmission及其有界native/raster额度；缺物理容量/授权拒绝，不套离线夹具权。3D Evidence由原surface Owner/viewport公开ISurfacePort与SurfaceSourceDescriptor供给，显式申请Surface3D，不自行将2D构成3D；Probe/SurfacePick只有各自获权端口才申请，不因FullReview或Claim自动启用；RoiEditing永不申请。相关投影/相机/坐标算法唯一归viewport/surface-data/coordinate-geometry，不在人工事务重写。

`IReviewViewportSourcePort.PrepareAsync(ReviewViewportSourceRequest,CancellationToken):ValueTask<IReviewViewportSceneLease>`：request字段=`Receipt:EvidenceReadReceipt, SelectionGeneration:long, CanvasDip:DipSize, DpiScaleX:double,DpiScaleY:double, Language:string, Profile:ReviewViewportProfile`；generation>0、canvas/DPI有限正。lease提供`Context:ViewportContext, Binding:ReviewBinding, SelectionGeneration:long, RetainedBytes:long`及IAsyncDisposable；它拥有本次解码/发布借用，宿主通过此显式源Adapter构造，无自由object payload或隐藏读取latest。Context使用原受控object/manifest映射、当前授权（EvidenceRead映Read，FactRead专门映Probe而非Claim映Probe）、只读Primary/可选Reference、准确revision和像素/物理空间；pixel坐标遵守viewport CenterInteger（列x/行y）、物理单位保持原Owner，未知尺寸允许独立合法看图但禁止需要可靠尺寸的联动。两图缺获准变换只独立Fit，不凭屏幕位置同步。

本节类型别名明确为`VP=Asun.UI.Viewports`、`VW=Asun.UI.Viewports.Wpf`、`VI=Asun.UI.Viewports.ImageFrame`、`IF=Asun.Modules.ImageFrame.Resources`；IFrameService/FrameDescriptor分别为IF.IFrameService/IF.FrameDescriptor，其余Viewport类型归VP，Control/binding/renderer归VW，源工厂归VI。SourcePort同时提供只读`Frames:IFramePort, Coordinates:ICoordinatePort, Authorization:Asun.UI.Viewports.IAuthorizationPort, Surfaces:ISurfacePort?, Probes:IProbePort?`供上述ViewportOptions显式构造；这些实例在Create/整个session内稳定，不能每Show替换。2D默认公开构造`ReviewViewportPublishedSourceFactory.Create(IFrameService frameService,IReviewPublishedEvidencePort published,IViewportProcessRoot root,Asun.UI.Viewports.IAuthorizationPort authorization,ReviewViewportProfile profile):IReviewViewportSourcePort`；Create内部一次调用ViewportImageFrameSourceFactory.Create(frameService,root,new("review-display",profile.MaxSourceBindings,Math.Min(1048576L,profile.MaxSceneBytes)))并核成功，frameService须由原Owner显式注册review-display consumer额度，不隐式注册。元数据限额在Host注册Profile及原root预算中显式预留，并与scene像素等实际保留量累计受MaxSceneBytes限制；超过拒绝，不证明任意尺寸证据均可显示。返回Frames/Coordinates就是同sourcePorts，Surface/Probe为空；若生产要跨frame物理联动/3D/原值Probe，由宿主显式实现同SourcePort并借用各自批准公开端口，不把像素identity伪作物理校准。

`IReviewPublishedEvidencePort.PublishAsync(ReviewViewportSourceRequest,CancellationToken):ValueTask<IReviewPublishedEvidenceLease>`是宿主已批准decoder/image-frame发布管线的注入边界（不能引用业务VM）；lease公开`ReviewBinding Binding, ManifestRef Manifest, ImmutableArray<ReviewViewportPublishedImage> Images, AuthorizationSnapshot Authorization`及IAsyncDisposable；image记录=`Object:ObjectRef, Frame:FrameDescriptor, Descriptor:ImageSourceDescriptor, PixelSpace:string, Role:SourceRole`（这些image-frame/viewport类型只出现在Wpf Adapter）。发布Owner从此次Receipt受控有界流解码，按image-frame已冻结Import/PublishCopy公共链得到Completed+OperationResourcesReleased的Frame；不得凭空返回未发布Frame、猜编码或窃取别generation。合成显示使用独立256-byte 16×16 Gray8对象，字节为按行序0..255、stride16、UInt8×1 Interleaved/完整有效域；真实SHA256=`40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880`（§10.1的E1是16byte事务读取fixture，不拿它当256byte图）；byte/Manifest/Profile输入由显式显示fixture提供。Prepare先核当前仍注册源数量/保留bytes+新scene是否≤Profile；不足时由Presenter显式Clear旧scene并等待Remove/归还后再Prepare，期间显示正在处理，不偷偷扩大限额或提前Retire。Prepare按Images原顺序Register，每项Frame/Descriptor完整一致、plane=[0]、PixelSpace=原Frame.CoordinateReference；SourceRole/当前授权裁剪和Reference存在性由Owner明示。输入来源超限/无decoder/当前撤权拒绝，不生成空正常图。scene lease保存发布lease/各bindingId，先合法空/替换解除viewport引用并Remove确认，再Dispose发布lease由其原Owner Retire；尚有源Read/Return时Dispose不得伪装完成。

源Adapter按已验证Receipt字节→已批准解码器→image-frame已发布FrameDescriptor→[ViewportImageFrameSourceFactory公开Register](../viewport/DEVELOPMENT-GUIDE.md#1522-image-frame--iframeportiframelease与原值读取)映射2D源；借用服务/consumerId/FrameKey/CoordinateReference/plane0/有效域精确相符。编码未知或缺decoder返回EvidenceUnavailable，不调用自猜HALCON文件API；有HALCON源时按image-frame当前公共适配，无AsunImage内部扫描。Frame来源/尺寸及字节来自同次受控完整校验，Range/thumbnail不能冒充原完整证据。灰度合成16×16 Gray8采用明确手动LUT(0,255,display-range/uint8/1)，不宣称自动测了min/max；真实自动对比度/LOD沿viewport已采纳统计/显示建议，只有显示参数，不自动改Outcome、理由、必审或期限。无统计保持原显示或提示，不执行未批准扫描。

首次Show保存原Prepare Task/scene lease后，仅一次`Session.AttachAsync(scene.Context,ct)`；后续切项用`UpdateAsync(new ViewportUpdate(当前ContextRevision,完整replacement),ct)`，新ContextRevision单调增加，不重Attach/换Backend/重复Bind。同binding实际backend Submit产生原PresentationRequest/SourceCall；Options.Presentation直接转发`control.Presentation.CommitAsync(request,sourceCall,ct)`，不创建新call或伪造presentationId/VisibleConfirmed。Lifetime.Acquire接收`ViewportPresenterSubmission(Request,Presentation,SourceCall)`并保存原Acquire/Confirm/lease；同binding.GetPresentations记录原Commit/Acquire/Confirm/Revoke/Return Task与Identity，由viewport根持有。HumanReview STA Owner强持同原Task引用和selection generation，有限Show等待结束不删除它们，也不另Return Presenter lease。没有实际VisibleConfirmed不显示“已读取且已呈现”，更不能把它证明人工Observed。

ShowAsync的ValueTask仅在实际当前generation呈现已确认后正常完成；其余由公开`ReviewPresentationException(Error:ReviewError,SelectionGeneration:long)`给出EvidenceUnavailable/TimedOut/PermissionDenied/SourceChanged等脱敏原因，operation业务状态不受影响。原Task/清理轴由STA Owner保存；ClearAsync的正常完成必须代表原呈现和source借用真实退出，有限等待到期抛同异常TimedOut并保原cleanup Task继续可查，不吞掉异常当Clear成功。Constructors/Create只校验可公开验证的Binding.Session==Session、同Dispatcher/保存的组合关系，viewport root仍在每个实际源call/Bind/Commit核自身签发关联，Host不调用不存在的Session.Root属性或通过伪造id确认Owner。首context.ContextRevision=0；后每次Show/Clear new revision=此前实际revision+1，溢出拒接纳并清理，失效session（失败Attach/Stopped）由原Owner新建，不假复活。

Hide在所属Dispatcher立即遮盖/禁止输入并移出本控件UIA；后台仍有viewport借用时不返源资源。Clear切项走viewport合法空`UpdateAsync`（Sources/Layers空、同session/version、显式新ContextRevision）等待旧Presentation原Revoke→原Owner Return/QueryReturn、原frame/surface借用确认归还，再Dispose scene lease；Review证据lease仍由§10.3原调用者在Clear成功后归还一次，Presenter借用不替Owner重复Dispose；清理权限不要求仍有Read，不复活普通读门。最终关闭先沿§10.3同一次Detach的Clear→证据/credential归还→Core.Stop，再由ReviewStaOwner在关闭链调用IReviewViewportPresenter.DisposeAsync；该方法幂等保存同原binding.UnbindAsync(cleanupTimeout,独立cleanupToken) Task，不再次Clear或重复Return。有限Dispose等待到期抛ReviewPresentationException(TimedOut,原generation)，原Task/异常与迟到结果仍由STA Owner记录，显式QueryClose/再次Dispose只观察同清理；失败/超期保原Unbind Task/trace/root直到晚到Return，CallbacksQuiesced/ReferencesDetached/Returned齐全才Drained。Unbind仅撤本binding，OwnSession=false不关闭Session；Close余下借用session/root由app Owner显式执行；只有ReviewStaOwner.IsReleased且该viewport Owner也确认释放，组合Host才可停原Dispatcher，不能把Core排空当viewport整体排空。Show失败中晚到Value的scene/lease也按原generation归还，不覆盖新画面、不提前Retire其FrameKey；来源发布Owner在viewport.Remove成功/所有Read归还后才Retire。

Language切换先取ViewportUiResourceCatalog完整当前culture资源，失败保旧完整语言并显示复判资源错误；成功同binding.SetResourcesAsync，不重新读取图/Claim/提交。新UI资源schema/Assembly版本在Wpf发布元数据明确，不能以Core0.3代表viewport0.1/Assembly0.2。HostA/B使用各自Control/renderer/source/root/Binding，不共享FrameworkElement或lease；Root/Close仍按既有§10.1/10.5。

新增必要断言HR-V01：同Control/binding原Presentation/SourceCall/Task关联一致，Lifetime=null/跨Root/source/授权/旧generation零Acquire；HR-V02：原Acquire/Confirm/Unbind闩锁下取消/撤权/换项，先Hide再原Revoke，晚到lease仍只归还一次，OwnSession=false不关借用session，旧源Retire前必须Returned；HR-V03：FrameKey/revision/CoordinateReference/灰度LUT/3D Evidence映射准确，缺原尺寸/坐标变换禁联动，三语Catalog切换不读图，实际VisibleConfirmed不足不冒称呈现。纳入Wpf.Tests/Integration.Tests规划，未执行真实viewport/WPF/HALCON测试。

### 10.7 全部文字资源、自动参数与使用场景收口

`HumanReviewTextCatalog.Create():IReviewTextResources`为Wpf公开同步默认完整三语入口，无IO/隐藏全局语言。`RequiredKeys:ImmutableArray<string>`是下面键加`Error.<每个ReviewErrorCode名称>`的唯一集合、ordinal排序；内置资源属于Wpf包，每个key/value有界（key≤128 UTF8bytes，value≤1024 UTF8bytes，完整三语快照≤1MiB），不从enum.ToString给操作员直接显示。宿主Text可扩展Policy Outcome/Reason白名单资源，不强制安装另一个Localization控件；语言由宿主SetLanguage/Catalog传入。

| HumanReview.键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Title | 人工复判 | 人工複判 | Human review |
| Previous / Next | 上一项 / 下一项 | 上一項 / 下一項 | Previous / Next |
| Claim / Renew / Release | 领取 / 续租 / 归还 | 領取 / 續租 / 歸還 | Claim / Renew / Release |
| Submit / Correct / Arbitrate | 提交意见 / 更正意见 / 提交仲裁 | 提交意見 / 更正意見 / 提交仲裁 | Submit opinion / Correct opinion / Submit arbitration |
| RefreshState / RefreshQueue / Recover | 刷新状态 / 刷新任务 / 查询原操作 | 重新整理狀態 / 重新整理工作 / 查詢原操作 | Refresh status / Refresh tasks / Check original operation |
| Focus / ExitFocus / Details | 专注看图 / 退出专注 / 详情 | 專注看圖 / 離開專注 / 詳細資料 | Focus on image / Exit focus / Details |
| Outcome / Reasons / CorrectionReason / Note | 意见 / 理由 / 更正原因 / 备注 | 意見 / 理由 / 更正原因 / 備註 | Opinion / Reasons / Correction reason / Note |
| Observed / Partial / Unobservable | 已观察 / 部分可见 / 无法判断 | 已觀察 / 部分可見 / 無法判斷 | Observed / Partly visible / Cannot assess |
| Empty / Unsubmitted / Committed | 暂无任务 / 未提交 / 意见已提交 | 目前無工作 / 未提交 / 意見已提交 | No tasks / Not submitted / Opinion submitted |
| Busy / Stale / Unconfirmed | 正在处理 / 状态已过期 / 结果未确认 | 正在處理 / 狀態已過期 / 結果未確認 | Working / Status expired / Result unconfirmed |
| Conflict / MissingEvidence / Restricted | 内容已改变 / 证据缺失 / 无权查看 | 內容已變更 / 證據缺少 / 無權檢視 | Content changed / Evidence missing / Access denied |
| AuditPending / LeaseUnavailable / Closing | 审计待确认 / 租约不可用 / 正在结束操作 | 稽核待確認 / 租約無法使用 / 正在結束操作 | Audit pending / Lease unavailable / Finishing operations |
| Image / Reference / Status / Close | 图像 / 参考图 / 状态 / 关闭 | 影像 / 參考影像 / 狀態 / 關閉 | Image / Reference image / Status / Close |
| Tip.Claim | 只领取当前项，不改变检测结果 | 僅領取目前項目，不變更檢測結果 | Claim this item; inspection results stay unchanged |
| Tip.Submit | 提交当前意见；最终处置由宿主决定 | 提交目前意見；最終處置由主程式決定 | Submit this opinion; the host decides final disposition |
| Tip.Recover | 查询原操作；结果未确认时不要重新提交 | 查詢原操作；結果未確認時不要重新提交 | Check the original operation before submitting again |
| Tip.Release | 归还当前租约；不代表质量放行 | 歸還目前租約；不代表品質放行 | Release this lease; quality release remains separate |
| Tip.Close | 等待原任务退出并归还资源 | 等候原工作結束並歸還資源 | Wait for original tasks and return resources |
| ResourceError | 文字资源不可用，请检查配置 | 文字資源無法使用，請檢查設定 | Text resources unavailable; check configuration |

上表斜杠行逐个展开为独立key/value，不保留斜杠拼接字串。每个Error key按§7/9错误分类映上述状态+恢复文字：PermissionDenied→Restricted/联系权限管理员；LeaseConflict/LeaseExpired/DependencyConflict/SourceChanged→Conflict/RefreshState；SnapshotExpired→Stale/RefreshQueue；Unknown→Unconfirmed/Recover；TimedOut/StillDraining→Closing/等待原任务；EvidenceUnavailable/EvidenceCorrupt→MissingEvidence/检查原证据；SecurityAuditRequired→AuditPending/Recover；LeaseUnavailable→LeaseUnavailable/RefreshState；InvalidRequest/IdempotencyConflict/PolicyRequired/PolicyMismatch/ProtocolMismatch/CapacityExceeded/PortUnavailable/CancelledBeforeSend/Disposed/Stopping→安全通用“操作未完成，请检查诊断 / 操作未完成，請檢查診斷 / Operation incomplete; check diagnostics”并按对应Code显示安全动作（修字段/原查询/重新冻结策略/停止新写/退出），不自动重试。所有错误HelpText/SuperTip使用同已裁剪文字和DiagnosticId，不带exception/note/隐藏父集；不会把原业务Unknown改写成“未保存”。Policy的Outcome/Reason key由宿主带PolicyRef/hash的文本映射显式提供，缺该映射禁相应选择并提示ResourceError，不用不透明Id猜质量结论。

本模块不拥有视觉算法、缺陷阈值或自动工艺参数：TTL/并发/预取/预算来自显式ReviewProfile，缺值拒绝，无自动推荐TTL、续租或多数票；GUI不调这些技术上限。影像Fit/1:1/平移缩放/只读Probe/多图联动和可选显示LUT/LOD唯一消费viewport已有算法，显示建议不得改变原字节或人工意见。真值/坐标/单位/标定由原Evidence/Frame/Surface/Coordinate Owner提供，不用Claim或图片读取次数证明人工Observed。用途受限时仅只读ImageOnly，原机判/AI/他人意见/事实Detail无权即不读，FullReview也不隐含质量放行或编辑ROI权。

使用场景覆盖单项只读、单项领取/续租/归还、首意见/有因更正、串行独立分配、多轮争议仲裁、复判站响应丢失/冷恢复、证据缺失/遮挡/退化、空/大规模稳定队列、并发站冲突、撤权/epoch/策略更换和窗口有限关闭；每项沿§5–10/12/13同契约。当前模块不提供整板批量原子提交、并行同Item盲审、产品放行、返修/复检、设备路由或新视觉算法；宿主需要批量时只对显式Item逐个同API执行、分别保存身份/回执/未知，不把一次按钮当全体成功。

补充断言HR-U14：三语RequiredKeys集合相同、23个Error码均可取、Policy文字缺失禁选择；Unknown无新key重发、ImageOnly零明细/零写、IME连按只有一次、主题/语言/布局改变不影响Binding；完整资源切换失败保旧语言。两STA分别切语言/清图/关闭，另一方图像和资源计数不变；1920×1080真实WPF/长英文/SuperTip/UIA仍须运行验证。

## 11. 并发、一致性与资源所有权

每个 Core 实例、请求和租约有独立 operation/epoch；不得共享可变静态缓存或“当前 Item”。同一 WorkItem 的 Claim、Renew、Submit、Correct、Release 在 Repository 事务内按 WorkItem revision + lease generation + policy/evidence snapshot CAS 核验。两个 WorkItem 可并行；同一 Item 的并行写入必须被 fencing 或被正式并行分配 Contract 拒绝。

证据读取、提交和事件通知可由宿主分别调度，但提交前必须等待所有依赖读取真实结束并再次核对期限、权限和修订。预取缓存键至少包括 ObjectId、Manifest revision、用途、可见范围、策略 hash 和主体 scope；权限撤回时不从缓存回填。订阅者慢或抛异常不阻塞提交线程，事件缓冲有界并可从持久水位重建。

热点优化仅可按精确已核原字节和版本复用深层不可变的同步编解码/规范化材料，隔离外部可变数组并限制容量；不缓存验签成功、授权、撤销、健康或证书仍存在的判断。跨异步边界与末次发布检查保持；用相同输入比较调用次数、耗时和资源，不通过延长期限或削弱检查制造性能改善。

资源所有权在端口中声明：Core 借用并最终归还 Evidence lease、数据库 session、缓冲和订阅；宿主拥有输入草稿，直到 Core 返回接收/拒绝；适配器拥有数据库/文件/SDK 句柄。取消、异常、重复 Dispose 和实例并行均须回到账本基线。任何未知所有权的资源不得释放或复用。

## 12. 故障恢复矩阵

| 场景 | 必须保留 | 恢复动作 | 禁止 |
|---|---|---|---|
| 两站同时 Claim | 失败方的冲突和当前投影 | 读取当前 lease/策略后重排 | 后台抢租或本地强行可提交 |
| Renew 回执丢失 | 原 OperationId、旧代和草稿 | 查询原操作；确认后继续/重新领取 | 换键反复续租 |
| Submit 响应丢失 | 草稿、幂等键、证据/策略快照 | 查询原操作；未知期间禁止重复新意见 | 返回失败或新建意见 |
| 原操作查询失败/无权/损坏 | 原恢复身份及查询错误 | 当前获权后继续精确查询 | 冒充原业务 Rejected 或清记录 |
| 持久成功后审计/交付失败 | 原成功事实、审计和交付状态 | 只续原审计/核当前交付资格 | 再次 CAS/rotation 或伪造回滚 |
| 状态观察纯到期 | 经独立检查仍同绑定的未发送内存草稿 | 显式刷新状态/原意见头，由人再提交 | 续旧观察或把保留证明当权限 |
| 租约过期后迟到提交 | 已提交历史回执 | 旧代拒绝，重新固定新上下文 | 接受旧代覆盖新 Owner |
| 权限撤回/主体切换 | 审计和已合法回执 | 停止交付、清理无权投影，按授权重新读 | 从缓存/导出泄露 |
| 证据缺失/Hash 不符 | 原 Manifest、缺项和诊断 | 转待证据/升级/新证据轮次 | 以缩略图或“看起来正常”替代 |
| 仲裁父意见更正 | 原意见链和新修订 | 旧依赖冲突，新建批准处理 | 覆盖父意见或沿用旧预览 |
| 进程崩溃/断线 | 持久回执、未知操作和草稿（按宿主策略） | 重启后按 OperationId/lease 查询，旧代 fencing | 清空内存即当未提交 |
| 关闭仍有 IO | 资源账本和 StillDraining | 等待真实排空后释放；下次启动恢复 | 超时后复用连接/缓冲 |
| 返修/复检事件迟到 | 原意见及宿主关联引用 | 由返修/复检 Owner 分析影响 | Core 自动改判或发设备命令 |

## 13. 独立测试矩阵、反例与验收断言

### 13.1 Core/Simulator 测试

必须在无 UI、无产品数据库、无硬件的最小宿主覆盖：

- 正常：单 Item Claim→证据读取→逐项意见提交→回执查询→Release；两消费者使用同一输入语义；
- 空/边界：空队列、缺证据、零/超限页大小、到期边界、无可见字段、重复订阅和重复 Dispose；
- 并发：两站同 Claim、Renew 与 Submit 交错、同人三窗口、两 Item 并行、同 IdempotencyKey 不同载荷；
- 回执：Commit/Arbitrate 成功但响应丢失、查询权限不足、服务重启后恢复、旧代迟到；
- Claim/Renew：提交前后响应丢失、同键同请求返回同 operation/receipt/lease、同键异载荷冲突、过期/撤权/key rotation 不交付秘密、密文/AAD/verifier 篡改失败关闭、旧 token 不可继续写、传输取消时实际 drain 前不清零/复用缓冲；
- 盲审：原机判/AI/他人意见在队列、缩略图、错误、tooltip、导出和事件中均不泄露；揭示后刷新不能恢复未见状态；
- 多轮：固定分母、缺席不缩分母、同坐标不同原因不合并、父意见更正使仲裁提交冲突、仲裁不关闭其它 Item；
- 取消/关闭：证据读取中、提交中、Unknown、超时、订阅者抛异常、关闭 StillDraining 和下一次恢复；
- 反例保护：意见“误报”不改机器原值，返修完成不等于复检通过，复检通过不等于放行，AI 建议不等于人工确认。

本次来源增量的定向断言：

- 原操作查询无权、损坏、不可用、无记录及权威 Pending 分别保留原恢复身份；不伪造终态字段；持久成功后审计失败只续原审计，CAS/rotation 次数不增加；
- 同主体 None/Present/Unavailable、缺项/坏链、不同主体隔离、盲审限制、读取后前序/水位变化；不可用不当无前序，变化不自动更换或发送；
- 仅图片权限时零读取结果明细，未知尺寸可合法看图但禁补标；事实损坏仅清事实，共同撤权清两者，迟到清除不影响新 generation；
- UIA/投影 hash/错误/导出均不泄盲审内容；受限结果无值，Raw/Rule 原值/单位/未知不变，不生成不存在的 Machine/Final 层；
- 必审、可见、未处理和图像各维度不混；多 FOV/多图不重复 Item，空页不完成，受限不编码为零，旧项迟到不回填；
- 真实固定 capture 到期不能被后续观察或 UTC 回拨续命；仅同绑定未发送内存草稿可只读保留，撤权/传输撤销/ABA/最后来源检查失败不保留。显式刷新后须人工再提交，Unknown 不重发。

### 13.2 两个消费者接入验收

消费者 A 为机旁复判宿主，消费者 B 为独立 ReviewStation。二者分别注入不同的权限、PolicySnapshot、证据适配和语言/主题，均不引用对方 VM、私表或全局状态。必须证明：

1. 删除任一宿主仍可构建/运行 Core；第二消费者无需修改 Core；
2. 相同 WorkItem/策略输入得到相同租约、意见、错误和回执语义；差异有明确权限/证据/策略原因；
3. A 的取消、关闭、缓存和语言切换不影响 B；一个消费者的撤权不扩大另一个消费者的读取范围；
4. 两宿主均能重建 Unknown、处理 Claim 冲突、保留草稿和完成真实排空；
5. WPF 仅作为投影，Core 无 UI 调用路径与 UI 路径的校验/结果一致。

宿主恢复集成还须断言：按钮/热键/headless 同 gate 仅一次发送，恢复身份保存失败零发送，终态记录完成失败仍可按原身份冷恢复，容量满拒绝新写但可查询；重开/换端点不自动 Release/Renew/提交余项。内存 Simulator 不作为此项耐久通过证据。草稿恢复、投影失效和 UIA 均由两个宿主的实际消费者验证，不从 Core 单测外推 WPF 或两机通过。

### 13.3 不适用 HALCON/AsunImage 的说明

人工复判 Core 不做图像分割、匹配、OCR、量测或 3D 重建，因此没有 HALCON 算子选择或 AsunImage 算法适用性。影像展示/解码由 `IM-015`、`viewport` 或宿主通过其公共端口完成；若宿主需要视觉重算，必须另走对应视觉模块和 HALCON 26.05 适配，不得把算子句柄或算法结果塞进本 Core。

### 13.4 两个有限自审视角及合成验收输入

以下均为合成事务样例，不是客户工艺/视觉真值。固定scope=`s`，ItemA/ItemB语义revision=1，六绑定引用由内存Owner提供正确归属，StateVersion=7、Watermark=0、无活动lease；主体A/B，Policy仅允许不透明Outcome `O1/O2/U`（U表示本夹具无法判断），O1要求Observed和对象E1，O2允许Partial且要求理由R2，U允许Unobservable且无必需对象，更正原因C1。权威UTC=2026-10-11T00:00:00Z，lease TTL=10s、请求Total=2s、Drain=1s；这是夹具有限预算，不成为客户默认。每条用可控Clock/闩锁执行，不靠随机sleep。

| 用例ID / 视角 | 具体输入或故障注入 | 可判定断言 |
|---|---|---|
| HR01 实现者正常链 | A合法看E1→Claim A→OwnHead=None→O1提交→显式Release | 看图零Claim；Claim StateVersion8/generation1，Submit版本9且唯一Opinion，Release版本10/ActiveLease空；最终质量字段零写入；资源账本归零 |
| HR02 空/大规模消费者 | 第1页Rows=[]且NextCursor非空，第2页两行，最后End=true；总100000Item、PageSize2 | 不索引空行、不声称完成；只枚举同snapshot；最多MaxPageItems页内数据、无全库下载；权限变更拒旧cursor |
| HR03 弱证据/遮挡/退化 | E1缺失、E2合成受限、E3字节损坏；人工Partial或Unobservable | Missing/Restricted/Corrupt不同；不把短读当完整，O1拒绝；Policy允许时U可提交；参考缺失不阻仍获权Actual看图。Core不评估图像质量或调用HALCON |
| HR04 多候选/参数变化 | 人工同时选择O1/O2；Policy hash变、更换证据revision或Question | 单Outcome字段不接受两候选、不自动选分数；旧Binding/草稿提交冲突，新轮次需Owner建立；StateVersion更新不改变语义revision |
| HR05 重复/并发 | 两个获准FullReview主体（非ImageOnly HostB）同版本Claim；A同key重放，再同key改TTL；Renew与Submit闩锁交错 | 唯一领取；重放同原Operation/Receipt不增版本、不新随机secret；异bytes IdempotencyConflict；旧generation不能写/释放新代；两个Item可独立并行 |
| HR06 已审核项更正 | A头Present P1，B无权读A头；A更正前P1被追加P2；坏链/不可用 | B零披露；Unavailable不当None；A旧前序冲突，新头只经显式刷新/人工确认；C1追加不增独立票数，不改原事实 |
| HR07 Unknown/断线 | Submit持久版本9后丢响应；Query无记录/无权/异常/权威Pending/终态依次独立注入 | 原identity/key一直不变、提交计数1；无记录Unknown不准重发，无权Fault不变原业务；精确Proof恢复同Opinion；Journal.Complete失败仍可冷恢复 |
| HR08 取消/迟到/close | Commit闩锁未放开，业务2s到期；Close独立1s到期，再放开闩锁 | Unconfirmed+StillDraining；Root槽/原Task/ports存活；未发前取消NotSent；迟到成功仅写原journal/回执，不更新新项；实际归还后同ticket Drained/TryRelease |
| HR09 撤权/时钟/审计 | 读后撤权、UTC回拨、key epoch变化、Commit后审计不可用 | 发布前拒交付/Hide；单调期限不复活；原成功Proof保留、AuditUnavailable无secret；恢复审计不再次CAS，旧key不交付 |
| HR10 仲裁依赖 | 可见P1+隐藏P2摘要D，等待时隐藏P2更正 | 不用可见父集代完整集；D失效旧仲裁DependencyConflict；零父/重复/跨轮拒绝；成功丢响应恢复同Arbitration，无放行 |
| HR11 外部消费者构造 | 完全空Host按§10.1依次构造；缺port、非法Profile、Root满、Journal迟到Saved | 无隐藏窗口/全局变量；Factory前根槽，失败零业务IO；满拒新session保恢复；迟到Saved不发送；所有关联类型由§9可构造 |
| HR12 回退/第二消费者 | A Contract0.3成功，B只懂0.2，随后A关闭/切语言 | B ProtocolMismatch零新写，不覆新事实；A关闭只归A资源，B语言/投影不变；同输入授权相同的两个新Host结果语义一致 |
| HR13 双STA | 两窗口分别A/B，A撤权/IME Ctrl+Enter/Close超期，B继续 | A同步遮盖/UIA移除、连按至多一次，A Dispatcher保活直到归还；B正常，三语热切不跨STA；实际WPF运行后才判定 |
| HR-S01 存储 Head codec | `Head`按`HumanReviewOwnerStorage/1`、recordKind=1、HR-G01六引用/State/MaxLeaseGeneration=0编码；独立损坏/尾随字节 | 固定长度647 bytes，SHA256=`56d4366f41aa5c3b045ea6bde5eb91d4f0adfd92332909281b92c3691cf273eb`；尾随、长度、版本或hash错误为EvidenceCorrupt/ProtocolMismatch，不签终态 |
| HR-S02 存储 CAS/原操作 | 两提交同Head/IdempotencyKey交错；一个持久成功后响应丢失，另一个见唯一索引冲突；Journal Complete重复/乱序 | 只有一个StateVersion/Opinion增量；竞争终止后按原Identity查询，未能证明权威结果保持Unknown；Complete同Proof幂等，异Proof Conflict，不换key |
| HR-S03 审计与跨 Host nonce | Commit后ConfirmAudit不可用；A/B同Envelope key实例并发Prepare，A冷恢复继续计数 | Proof保留且Audit=Pending/Unavailable不交付秘密；同key nonce跨Host/重启不重复，冲突/溢出拒绝关闭；固定fixture nonce不冒充生产唯一性 |

实现者自审沿§5→6→9逐输入至结果走通：无原记录新写、重复解析、证据/授权变化、更正/仲裁和Unknown均有不同分支，发现历史成功缺业务引用已补入Proof。外部消费者自审沿§9工厂→§10两个Host走通：opaque credential不要求消费者构造，安全材料可持久，Host预算/根槽/迟到归还可公开查询；发现旧端口同义、Mutation自由Payload、Dispose等待借用lease死锁已修。此为两次有限文档自审结果，不是代码执行通过。

### 13.5 Canonical Golden 的完整固定输入与独立核算

HR-G01固定Claim载荷用于codec验证，引用均刻意取同字节，仅测试规范编码，不作为获准业务归属。六种引用各字段scope=`s`、id=`i`、revision=1、sha256=`0`重复64次；OperationId=`00112233-4455-6677-8899-aabbccddeeff`，key=`k`；Origin=`(s,u,null,n,a,1)`；State=(Binding,7,0,null,`0`×64,空UnresolvedQuestions)，RequestedTtl=1s。Identity.Kind=Claim、ExpectedStateVersion=7；PayloadSha256不参与自身编码。

完整字节用可展开的无歧义拼接表达（不是省略号）：`R=hex(00000001730000000169000000000000000100000040) || ASCII("0"×64)`（86bytes）；`B=R||R||R||R||R||R`（516bytes）；`O=hex(0000000173000000017500000000016e00000001610000000000000001)`（29bytes）；`S=B || hex(000000000000000700000000000000000000000040) || ASCII("0"×64) || hex(00000000)`（605bytes，包含ActiveLease null的一字节）。

`Request = hex(00000017) || UTF8("HumanReviewCanonical/v1") || hex(000000010100112233445566778899aabbccddeeff000000016b) || O || B || hex(0000000000000007) || S || hex(0000000000989680)`；总1219bytes，SHA256=`9297ca6edecf617b57d5d63a377c168055f0cad471455ba774377aec0159a30c`。2026-10-11内存Python分别按字段pack及上列固定hex块重建，长度/hash一致；未运行未来C#codec。原语向量：字符串“复判”=`00000006e5a48de588a4`；Int64(-1)=`ffffffffffffffff`；Guid字节如上RFC4122；可空null=`00`、空数组=`00000000`；空字符串不等null。尾随字节/过长/非法UTF8/未知Kind均拒绝。

HR-G02逐字段改Origin.SessionId、Binding任一revision、ExpectedStateVersion、State水位、ActiveLease、Draft任一字段、OwnHead/前序、仲裁隐藏依赖hash、TTL，断言对应载荷hash变化；RequestId/当前授权/Budget变化不改原载荷。提交/更正/仲裁先按§9.4固定字段独立构造期望bytes，再核C#codec，不能只自身往返。HR-G03固定测试key/token/salt/nonce仅夹具使用，AEAD/verifier按§9.4独立BCL重算，逐位改AAD/cipher/tag/verifier失败关闭；token/key不能出现在诊断/事件/普通序列化。以上是必需未来执行断言，未造平台加密通过记录。

## 14. BenchmarkProfile 与可观测性

客户目标数值尚未冻结，测量方法已冻结、目标值待消费者 Profile 采纳。`ReviewBenchmarkProfile`是测试输入（非产品DTO），公开全参字段=`Ref:ReviewRef, ModuleVersion:string, Profile:ReviewProfile, InputManifest:ReviewRef, PolicyRefs:ImmutableArray<PolicySnapshotRef>, ScenarioIds:ImmutableArray<string>, ConcurrentHosts:int, ColdSamples:int, WarmupSamples:int, WarmSamples:int, MinimumValidSamples:int, RunDeadline:TimeSpan, MaxManagedBytes:long, MaxNativeBytes:long, MaxWorkingSetBytes:long, MaxConnections:int, MaxEvidenceLeases:int, MaxSecretBorrows:int, MaxRootSlots:int, Targets:ImmutableArray<ReviewBenchmarkTarget>`；样本/并发/资源上限为正（预热可0），有限deadline，所有max不超过组合Profile。`ReviewBenchmarkTarget(MetricId:string,Limit:double,Unit:string,Source:ReviewRef)`来自已采纳消费者Profile，不能为空Source或以示例数字冒充客户目标；Targets空则NotEvaluated。

InputManifest绑定固定输入字节/hash、队列规模/过滤复杂度、Item/证据数、原图与3D对象大小、网络往返注入、数据库/文件介质、权限/盲审裁剪比例、Unknown/失败脚本和持续时长。冷样本每次创建新独立Root/session和空缓存，热样本同一有效实例、先执行WarmupSamples但不纳入测量；所有预热结果/排空也记录，不忽略预热失败。随机脚本需固定种子、实际序列和hash，不能不同消费者使用不同负载后比较。

测点包括：队列首屏/翻页 P50/P95/P99、Claim/Renew 往返、首幅证据与完整 Manifest 就绪、逐项提交及回执查询、仲裁提交、Projection 重建、关闭排空尾部、峰值托管/native 内存、缓存/连接/证据租约数量、Unknown 年龄、队列等待和事件重建延迟。统计使用单调计时器、分位数方法和明确分母，报告冷/热与错误分布，不能用平均值替代长尾。

统计方法唯一按DEV-GOV-010 §3.1，不在本指导复制分位算法。端到端从接纳（含Journal、排队、授权、回执、呈现）到实际ResourcesReleased；另计取消到真实排空、Close尾部，调用返回时长不能代替端到端。逐样本保留状态、失败、未读、超时、删失、Unknown、资源终态和有效n；无本地排空证明不可判性能通过，业务Unknown的已排空样本单列。资源账本计Root槽、活动Task、授权guard、连接、证据lease、secret borrow、缓冲/native/纹理及事件峰值；不能靠清空引用掩盖仍活动Task。

失败阈值由两个消费者和部署Owner采纳；缺目标为`NotEvaluated`，不是通过。有目标时任一超限/必需样本不足/未排空为Fail；任一资源/排空预算超限停止接纳或降级只读/待恢复，不能降低盲审、必审或幂等要求。无硬件Benchmark可量事务/内存，不外推真实DB、网络、WPF首图和现场节拍。

## 15. 版本、迁移与发布回退

发布单元为 `HumanReview.Core`（必需）和 `HumanReview.Wpf`（可选），Adapter 由宿主/部署单元提供。接口版本遵循加字段向后兼容、删除/改语义升 Major；策略、证据 Manifest、错误键和状态语义均带版本/hash。未知版本、未知 Outcome 或未知可见性策略必须拒绝写入并保留原回执。

Core=`net10.0`、Microsoft.NET.Sdk，无UseWPF/Windows/DevExpress/AsunImage/产品项目引用，只用BCL；公开Contract、默认安全实现、HostRoot/facade在同一DLL。Wpf=`net10.0-windows`、UseWPF=true，引用Core及本机固定DevExpress25.2.3所需Core/Docking/Grid/Grid.Core/Editors/PropertyGrid程序集，HintPath由仓库既有依赖配置提供，不下载NuGet或假造Bars.dll。Wpf标准Presenter另引用`Asun.UI.Viewports`（Core API0.1）、`Asun.UI.Viewports.Wpf`（Assembly v0.2）、`Asun.UI.Viewports.ImageFrame`以及image-frame的Core/Resources公开包；依赖由宿主组合注入，不带进HumanReview.Core。不默认引用3D实现，获准3D源由宿主SourcePort提供。源码包/发布元数据记录本模块版本、Contract0.3、codec1、目标框架、公开依赖、迁移支持及源证据；不自动复制用户程序集，不审查授权。

v0.2→v0.3是破坏性准备期契约替换，旧secret/AAD/canonical域不得当作新版本；能力协商不支持0.3则ProtocolMismatch并禁止写，不把未知DTO字段当可忽略。产品持久Owner负责expand/回填/切换/rollback，Core不得创建私表或替迁移Owner执行数据删除。任何回退版本不能解释新事实/盲审/仲裁依赖时只读并拒绝写；旧客户端仍可按获准旧只读codec查原历史，不重新hash旧事实。功能切片不是按按钮分DLL。

持久化迁移采用 `expand -> 双读/兼容回填 -> 校验 -> 切换 -> contract`。旧客户端未能理解的新状态/盲审范围/仲裁依赖不得继续写入；回退只回到仍能解释全部已提交事实的版本，不删除意见链、证据引用或审计。迁移演练需覆盖中断、Unknown、旧租约 fencing、事件水位和证据 Manifest 不变。

## 16. 代码、测试落点与变更范围

以下是实现切片的唯一工程落点规划，目录尚未创建，不代表已有代码：

| 内容 | 规划落点 | 允许内容 |
|---|---|---|
| Core 与公开 Contract | `src/Modules/human-review/Asun.Modules.HumanReview.Core/` | 无 UI 的值类型、Core、状态/错误、端口和 Simulator；不放产品字段 |
| 可选 WPF 控件 | `src/Modules/human-review/Asun.Modules.HumanReview.Wpf/` | namespace `Asun.Modules.HumanReview.Wpf`；任务/证据/草稿投影、键盘/UIA、§10.6 Presenter/Source Adapter与§10.7 TextCatalog；不放质量处置 |
| Core 单元/契约测试 | `tests/Modules/human-review/Asun.Modules.HumanReview.Core.Tests/` | 正常、边界、失败、幂等、并发、盲审、取消、排空和资源账本 |
| 两消费者接入测试 | `tests/Modules/human-review/Asun.Modules.HumanReview.Integration.Tests/` | 机旁模拟宿主与独立 ReviewStation 最小宿主；各自端口和 Profile |
| WPF 双 STA 验证 | `tests/Modules/human-review/Asun.Modules.HumanReview.Wpf.Tests/` | 固定viewport的真实控件/Dispatcher、三语/IME/UIA/关闭与纹理账本 |
| 真实持久化/证据适配 | 对应宿主或 Adapter 工程 | 只实现本指导端口，依赖 IM-015/IM-066 的已批准公开接口 |

上述目录中csproj均与目录同名；Wpf源码工程同表同名。Core.Tests/Integration.Tests采用DEV-GOV-010 §3.1既有约定：net10.0、OutputType=Exe、仅BCL及本Core引用、确定性断言/可控时钟/闩锁，无待选NUnit/xUnit包。Wpf.Tests为net10.0-windows/UseWPF、Exe、引用Wpf/Core及宿主测试Viewer，不含产品Shell。全部HR01–12及HR-G01–03由Core/Integration入口分配；HR-S01–03由Integration入口执行（内存语义与实际DB耐久分别标记），HR13/HR-U14/HR-V01–03由Wpf入口执行，源接线反例亦纳入Integration；未完成/跳过/外层超时非零，禁止dotnet test空运行冒充通过。

后续获准实施时的独立命令（本轮未执行，工程尚未创建）：

```powershell
dotnet build src/Modules/human-review/Asun.Modules.HumanReview.Core/Asun.Modules.HumanReview.Core.csproj -c Release
dotnet run --project tests/Modules/human-review/Asun.Modules.HumanReview.Core.Tests/Asun.Modules.HumanReview.Core.Tests.csproj -c Release
dotnet run --project tests/Modules/human-review/Asun.Modules.HumanReview.Integration.Tests/Asun.Modules.HumanReview.Integration.Tests.csproj -c Release
dotnet build src/Modules/human-review/Asun.Modules.HumanReview.Wpf/Asun.Modules.HumanReview.Wpf.csproj -c Release
dotnet run --project tests/Modules/human-review/Asun.Modules.HumanReview.Wpf.Tests/Asun.Modules.HumanReview.Wpf.Tests.csproj -c Release
```

禁止仅build Core后对未build的测试使用--no-build。测试进程外层截止由已采纳测试Profile提供，进程提前被终止记未完成；内部cleanupdeadline按§10不能抹业务失败。新增测试仅跟随真实实现，本轮不创建测试/脚本/报告。

本会话只修改 `docs/independent-modules/human-review/DEVELOPMENT-GUIDE.md`。实现时允许变更上述新模块工程及其测试；禁止修改 `PKG-044`、`SM-022`、共享架构/入口/登记、参考项目、客户项目、AsunImage 内部、产品私表、产品 Shell/ViewModel 和厂商 SDK。正式 Contract/Schema/State/Owner 变更必须由其唯一 Owner 另行接收，不能在 Core 工程临时开字段。

## 17. 独立发布与逐操作接入

接入顺序固定为：

1. 宿主构造授权、身份、证据、策略、持久化、时钟和诊断端口；
2. 读取能力/版本并校验 Profile、PolicySnapshot 和请求范围；当前获权后先按原绑定恢复未决操作，未核清的 Item 禁止新写；
3. Query 队列投影，选择宿主已批准的 Item；
4. 经宿主在途 gate/恢复记录发送 Claim，并取得唯一 fenced Lease；后续各写调用沿用相同入口；
5. 按可见性读取证据，等待依赖读取排空并冻结草稿；
6. Submit/Correct/Arbitrate，处理明确回执或按原 OperationId 恢复 Unknown；
7. 无未决写且当前资格满足时显式 Release；未决项只保留恢复身份，不自动 Release。取消订阅、归还证据/数据库资源并等待真实排空；
8. 将意见回执交给质量/返修/处置 Owner，宿主自行决定后续事实和设备动作。

Core 的最小示例必须覆盖正常、拒绝、冲突、取消、Unknown、关闭和释放；没有正式数据库、WPF、硬件或客户样本时，只能运行 Simulator/契约测试，不能写“生产通过”。

## 18. 未决政策与实施门

以下事实必须由产品/质量/Contract Owner 决定，本文不猜：

- 角色、技能、利益冲突、替补和人员独立性规则；
- 每种产品允许的 Outcome/理由/批量范围、必审分母、截止期限和升级动作；
- 是否需要盲审、盲审隐藏对象、揭示后的后续资格；
- 多轮并行是否批准、仲裁资格/可见性/允许结论和再审条件；
- Claim 恢复 envelope 的目标密钥保护服务及 key custody/rotation 操作；离线可读/可提交边界、草稿持久策略；
- 证据保留、撤回、跨站网络、数据库拓扑和客户性能 Profile；
- AOI/SPI/PCB 领域的缺陷表单、返修动作、局部复检覆盖和最终放行 Owner。

这些未决项阻断对应产品集成、正式 Contract、WPF 页面和生产验收；不阻断无产品事实写入的 Core、Simulator、Adapter Port、错误/取消/排空和契约测试。实现者发现新歧义必须先修订本指导或上层 Contract，再编码。

## 19. 自审、状态与验收边界

本审查确认：两个消费者和独立目录满足拆出稳定事务 Core 的理由；Core 不拥有制程解释、质量放行、返修/复检、设备副作用或产品数据库；所有操作有权限、证据、租约、幂等、Unknown、取消、排空和资源边界；无 UI API 与可选 WPF 共享同一校验；第二消费者、反例和 BenchmarkProfile 已给出；HALCON/AsunImage 对本模块算法不适用。

本文件为 `DesignReview/Prep`，其完整当前架构范围的可决定软件设计结论见§19.3。文档审查不等于 C# 编译、真实数据库/文件系统、WPF/DevExpress、HALCON/AsunImage、两进程长稳、Golden/Replay、HIL、计量、客户验收或现场质量资格。产品Contract/两个消费者真实接入/生产Profile和外部证据按受影响范围验收，不据设计闭合提升实际运行状态。

2026-10-11本轮定向检查范围仅此指导：本地链接存在、章节标题唯一/顺序、代码围栏闭合、15个Core异步入口的请求/返回定位、旧API删除、HR用例/Golden覆盖及HR-G01两种独立字节重建。结果均通过文档检查；未执行未来工程build/run、真实数据库、WPF、加密实现、性能/HIL/现场验收。两种有限内容自审与已关闭缺陷见§13.4，六项送接收定位见附录A；不跑全仓验证、不新建证据文件。

### 19.1 2026-10-06 候选来源定向审查

以下为 `H:\docs\40-development\50-ai-review` 三份只读原件的模块相关审查；以现有[全量来源清单](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)定位，不修改原件/清单或另建报告。原件 SHA-256 已核对；本表只记录本模块取舍，不宣称全部原件、源码或测试已审查通过。

| 原件与 SHA-256 | 实读并用于本次取舍的范围 | 采纳落点与排除 |
|---|---|---|
| `ReviewClaim安全与幂等恢复协议开发指导.md`；`c5fcfbf3b284fae0c65519324ff9219e0c35e9a3ea8bd25effdec3b591dd547a` | §1–7、§8.1–8.2；生成区定向核原操作/失败状态，不作为新合同 | §5.3/5.5、§7、§12–13：查询与原结果、审计/交付分态、单项在途及原恢复身份；§5.4 既有 secret 约束保留。排除 AOI Case/SQLite、具体密钥部署、wire/域字节、固定容量及来源通过记录 |
| `复判站与返修闭环开发指导.md`；`ebed3013db8f6299acbed164c9631889c2bead53f405189c94e950d2ec3bfe75` | 开篇 FACTS-LIFECYCLE-02/LOCAL-FACTS-01；§1.3/1.4、§1.8–1.11、§1.15–1.20、§1.23–1.26.1；§3.2/4.1、§7.1/8.1、H11；末尾 Office 固定观察/同步重复校验/UIA；生成区定向核反例 | §4、§6、§8–9、§11–13：分层权限、事实/图片失效、更正前序、到期草稿、固定观察和完整性。排除入队/缺陷/返修/复检/放行、客户端私表和产品 API、部署、固定数值/图像比例；生成 Case 状态与正文冲突不迁入，排他 Claim 不放宽 |
| `机判_AI_人判融合开发指导.md`；`70869c962de65c0ca76083cdd9faf2b214b48222e37848cf1a03aa20ec439bfb` | §0–11，重点 §1/3/6/8/10；末尾多来源说明仅核边界，生成区不作为 Core 合同 | §4/13：真实层分离、精确持久历史、盲审无值/UIA/hash 裁剪。排除融合图、N-of-M、MachineDecision/FinalDisposition 写入与激活、设备路由、板级多来源协议及来源性能/验收结论 |

这些来源是内部指导候选及历史实现定位，不是已验证的平台代码。原始竞品页码/营销、来源夹具或通过数量不转成平台证据；本模块只吸收上述稳定事务与投影约束，其余仍归产品或对应事实 Owner。此次不改变 `PreparationIncomplete`、逐切片准入或未决产品政策。

### 19.2 官方资料与固定源码/测试研究落点

复用暂停前已实读的官方资料及实际源码/测试，本轮不重复下载来源，不把引用访问或上游测试当本模块运行证据。DevExpress官方页面选择v25.2，与本机XML的v25.2成员交叉核对；页面显示25.2后续补丁包不改变平台固定25.2.3、不下载替换库。没有可用dxdocs/匹配WPF skill时采用官方网页及本机XML；不审查用户库许可证。

| 已实际查阅来源 | 可迁移内容及正文落点 | 限制 |
|---|---|---|
| [DockLayoutManager 25.2](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)、[TableView 25.2](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TableView?v=25.2) | §10.3 Docking分区、保存恢复和显式TableView/按像素滚动；本机Docking/Grid XML核AllowClose/AllowFloat/AllowDock/AllowEditing/ShowGroupPanel等 | 只能证明API用法，不能证明本控件布局/UI性能已运行 |
| [FlyoutControl 25.2](https://docs.devexpress.com/WPF/DevExpress.Xpf.Editors.Flyout.FlyoutControl?v=25.2)、[SuperTip 25.2](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip?v=25.2)、[BarManager 25.2](https://docs.devexpress.com/WPF/DevExpress.Xpf.Bars.BarManager?v=25.2) | §10.3–10.4正确Flyout CLR namespace、SuperTipControl包装普通控件提示、UIA LiveSetting/已存在peer通知；按官方推荐简单ToolBarControl/StatusBarControl组合 | BarManager是legacy；Bars属Core程序集，不能猜独立Bars.dll。PropertyGrid XML只读说明存在歧义，使用白名单只读投影并要求实际编辑禁用断言，不据歧义宣称可编辑 |
| [.NET取消](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads)、[TimeProvider net10](https://learn.microsoft.com/en-us/dotnet/api/system.timeprovider?view=net-10.0) | §8/10合作取消不等IO结束，单调计时与UTC审计分开；测试用可控时钟/闩锁 | 不证明远端事务回滚，不新增测试包依赖 |
| [AesGcm net10](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.aesgcm?view=net-10.0)、[FixedTimeEquals net10](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.cryptographicoperations.fixedtimeequals?view=net-10.0) | §9.4–9.5固定16-byte tag构造、Dispose、密钥清零、先定长验证再固定时间比较 | 比较长度不同会提前返回；BCL文档不是本协议安全验收 |
| DistributedLock tag2.8.3，[RedisDistributedLock.cs](https://github.com/madelson/DistributedLock/blob/8007a8686909be235dc339564adca4a0673843bb/src/DistributedLock.Redis/RedisDistributedLock.cs)、[RedisDistributedLockHandle.cs](https://github.com/madelson/DistributedLock/blob/8007a8686909be235dc339564adca4a0673843bb/src/DistributedLock.Redis/RedisDistributedLockHandle.cs)、[LeaseMonitor.cs](https://github.com/madelson/DistributedLock/blob/8007a8686909be235dc339564adca4a0673843bb/src/DistributedLock.Core/Internal/LeaseMonitor.cs)、[RedLockHandle.cs](https://github.com/madelson/DistributedLock/blob/8007a8686909be235dc339564adca4a0673843bb/src/DistributedLock.Redis/RedLock/RedLockHandle.cs) | 实读unique lockId、Volatile失效token、Interlocked幂等DisposeAsync、先结束monitor再release；Unknown/Held不重启租约寿命，Renewed才延长。§5/8/11/13采纳生命周期和失效反例 | 不采纳Redis锁/自动续租/GC释放替代复判事务、持久幂等和fencing；不复制代码、不新增Redis依赖 |
| 同commit [DistributedLockCoreTestCases.cs](https://github.com/madelson/DistributedLock/blob/8007a8686909be235dc339564adca4a0673843bb/src/DistributedLock.Tests/AbstractTestCases/DistributedLockCoreTestCases.cs)、[RedisDistributedLockTest.cs](https://github.com/madelson/DistributedLock/blob/8007a8686909be235dc339564adca4a0673843bb/src/DistributedLock.Tests/Tests/Redis/RedisDistributedLockTest.cs)、[ConnectionStringStrategyTestCases.cs](https://github.com/madelson/DistributedLock/blob/8007a8686909be235dc339564adca4a0673843bb/src/DistributedLock.Tests/AbstractTestCases/Data/ConnectionStringStrategyTestCases.cs) | 实读TestHandleLostTriggersCorrectly、AlreadyCanceled、CanSafelyDisposeWhileMonitoring、TurkishTurkey ordinal、AccessingHandleLostTokenWhileKeepaliveActiveDoesNotBlock；§13失效/并发释放/ordinal断言 | 仅阅读，未运行上游测试，不把锁释放语义直接等同Opinion事务 |

固定commit=`8007a8686909be235dc339564adca4a0673843bb`；内存codeload zip SHA256=`f0d9c420279629038ffd9e15959c01bdede5bda3dbdc6a1f9808a678a3a9310d`；[MIT License.txt](https://github.com/madelson/DistributedLock/blob/8007a8686909be235dc339564adca4a0673843bb/License.txt) SHA256=`6a4eb088f7da45022de3da8105a477d36fdb69c57088b609176a5196ee75bf89`。实读Redis项目自身version1.1.1、目标net462/netstandard2.0/netstandard2.1、Core项目引用、StackExchange.Redis2.7.33；上游测试net8/net472、NUnit3.14/Moq4.20.70。平台只采用设计/测试思想，目标net10.0/BCL无上述依赖，版本/许可元数据供来源追溯，不构成新增依赖审查门。

### 19.3 2026-10-12 完整批准范围的可决定软件设计结论

本永久唯一会话已对当前批准的 IM-067 范围完成一次有限自审：C1/C2 的 Core、Simulator、无 UI HostRoot/facade、安全端口和默认安全实现，I1 的 Adapter/存储 codec/证据/授权/审计/journal/远端宿主边界，以及 U1 的 WPF 双 STA、viewport 同 binding Presenter、三语资源、源发布和关闭排空规则，均已有唯一输入、输出、版本、Owner、状态、预算、资源所有权、错误、取消、Unknown、恢复、第二消费者和测试断言。当前没有仍可由本模块软件设计决定、却被留给实现者猜测的字段、调用顺序、存储记录或清理语义。

| 范围 | 设计闭合结论 | 仍由外部/后续门决定的事实 |
|---|---|---|
| C1 Core/Simulator/无 UI | 完整 v0.3 API、canonical、状态/CAS、幂等/Unknown、Root/STA-independent lifecycle、两个消费者和 HR01–12 已定；可按准入切片实现 | 真实 C# 工程、编译、契约测试、端口接入与生产宿主运行 |
| C2 安全端口/默认安全实现 | token/salt/verifier/envelope/nonce、AEAD/AAD、fencing、材料恢复、秘密交付与不记录规则已定；HR-G03、HR-S03 覆盖 | 生产 key custody/rotation、跨进程秘密 wire、真实安全服务和耐久断电证据 |
| I1 Adapter/存储/证据/授权/审计 | 注入依赖、固定 binding/codec 输入结果、OwnerStorage 记录、事务顺序、affected-row/timeout 限额、原操作恢复、审计与证据 lease 链已定；不是把 Adapter 设计交给外部门 | IM-066 实际数据库/文件 provider、IM-015 manifest/decoder、授权与审计服务、跨站部署 endpoint，以及耐久/撤权线性化实测 |
| U1 WPF/viewport | 八参数 ReviewUiServices、同 binding Presentation/Lifetime/SourceCall、一次 Clear→Return→Stop→Unbind 链、三语/UIA/1920×1080 和 HR-U14/HR-V01–03 已定 | 真实 WPF/DevExpress 25.2.3、viewport/image-frame 装配、UIA/DPI/纹理和双 STA 运行验证 |
| P1 产品政策/质量事实 | 已明确不进入本模块默认值和写入权；宿主只能按显式 Policy/授权调用 | Outcome/理由/必审分母/盲审/仲裁/保留期限、最终放行、返修复检和设备动作由产品/质量 Owner 冻结并验收 |

本结论覆盖架构当前批准的全部 C1/C2/I1/U1 软件设计范围；`ModuleCoreImplementationReady` 只适用于表中 C1/C2 的纯 Core/Simulator/安全夹具，不提升 I1、U1 或 P1 的实现、运行或生产资格。未编译/运行的项目、真实数据库/网络/WPF、性能、Golden/Replay、HIL、计量和客户现场验收仍明确记录为后续门，不能反向称为设计欠账。总控只接收本结论和状态，不承担第二次内容审核；若后续上游公开契约变更，暂停受影响切片并在本唯一指导修订。

定向文档验证（本轮仅本文件）：链接目标存在；标题唯一且顺序有效；Markdown 围栏闭合；15 个 Core 异步入口在请求/返回表中闭包；旧接口名未残留；HR01–13、HR-G01–03、HR-S01–03、HR-U14、HR-V01–03 已有规划定位；三语资源覆盖 23 个 `ReviewErrorCode`；fixture 的 Profile、Origin.SessionId、跨 Host nonce 前缀和技术 Capabilities/权限分离已核对。HR-G01 的 1219-byte canonical Golden 未改变；新增 Head codec 向量见 HR-S01。未执行 build/run、实际数据库/WPF、加密、性能或现场验证。


### 图标可访问性验收

遵循 [DEV-UI-047 §2.3](../../shared-modules/guidance/05-ui/DEV-UI-047_视觉设计系统规格.md#23-图标可访问性补齐全库空缺)：

| 项 | 验收要求 |
|---|---|
| 可访问名称 | 每个图标按钮/树节点/状态标记有非空可访问名称(`Name`/`HelpText`/SuperTip)，不能只有图形 |
| 装饰图标 | 纯装饰图标标记为装饰并从可访问树剔除 |
| 悬停提示 | 图标操作使用 DevExpress SuperTip(标题/作用/限制/快捷键/恢复步骤)，随语言切换 |
| 危险动作 | 图标 + 文字 + 颜色三重表达，不依赖单一图形 |
| 状态标记 | 状态色块同时有文字标签或图形形状差异 |
| 对比度 | 图标本身满足 §1.3 图形 3:1 门槛 |
| 高对比模式 | 不因系统高对比模式失效 |

**判据**：屏幕阅读器朗读时，每个可操作图标都有可理解的名称；任何"只有图标、看不出是什么"的位置是缺陷。

## 附录 A：Module API Contract v0.3 与六项逐切片准备定位

唯一规范是§9当前版本字段/方法、§10宿主/控件契约及§15兼容规则；本附录只是接收定位，不创建优先于正文的第二套API。本永久原会话已接收 C1/C2 的六项核心规格为 `ModuleCoreImplementationReady`；U1 仅接收具体 Profile、八参数服务和双 STA 装配指导，真实 WPF/UIA、DB/持久化、性能及生产 key custody 仍为 `PreparationIncomplete/NotReady`。I1/P1 仍为 `PreparationIncomplete`；文档历史accepted与本轮自审不能扩大任何切片的准入范围。

| DEV-GOV-010六项 | 当前可定位规格 | 准备结论 |
|---|---|---|
| ①边界/第二消费者 | §1–2、§9.2、§10.1/10.5 | Core仅事务规则、宿主持有最终事实；机旁/独立站真实消费计划明确，C1/C2规格已接收 |
| ②唯一API/参数/结果/事件/生命周期/版本 | §3–9.6、§10.1/10.3/10.5、§11/15 | v0.3公开工厂/强类型/端口/codec/Owner/预算/错误闭包，C1/C2规格已接收 |
| ③空无UI Host | §9.5/9.6、§10.1双Host和根Owner | BCL内存组合可实施，无窗口/SDK/产品DB；仅规格，未build/run |
| ④测试/反例/回退 | §12–13.5、§16 | HR01–13、HR-G01–03及异步故障可判定；Golden字节独立核算，C#及真实端口/WPF未运行 |
| ⑤Benchmark | §14、§3.3/9.3 Profile | 输入hash/样本/deadline/资源/端到端至Released齐全，统计引用唯一GOV；目标待Profile采纳、NotEvaluated |
| ⑥工程/范围/调用/后续门 | 顶部binding、§10、§15–18 | Core/Wpf及各测试唯一落点/命令明确；本轮仅guide写入 |

| 切片 | 本轮内部决定准备 | 精确后续门/Owner |
|---|---|---|
| C1 Core/Simulator/无UI HostRoot/facade | 六项核心规格已由本永久原会话接收，覆盖完整事务而非只缩首片 | `ModuleCoreImplementationReady`；工程创建和HR01–12运行仍须真实代码任务，不能外推产品集成 |
| C2 默认安全实现/安全端口 | 六项核心规格已由本永久原会话接收；密钥借用/材料/工厂/AEAD/恢复/fencing已定 | `ModuleCoreImplementationReady` 仅限纯Core/Simulator安全夹具；生产key custody/rotation提供者及真实安全Adapter仍未就绪 |
| I1 真实Integration/DB/证据/wire/journal | 端口/原操作查询/gate/持久恢复及有限收尾已定 | 宿主Owner提供实际权威DB、证据Manifest映射、密钥服务及获准wire；耐久/撤权线性化/跨机验收未做，不把内存当耐久 |
| U1 可选WPF控件/双STA Host | 具体Profile、八参数ReviewUiServices、双STA Root/Presenter装配已接收为指导范围 | 仅指导范围接收；真实25.2.3 WPF行为、UIA/DPI/纹理、1920×1080运行资格仍 `PreparationIncomplete/NotReady` |
| P1 产品政策/客户资格 | 不进入Core默认值 | 产品/质量Owner决定Outcome、角色、必审/盲审/仲裁/保留；消费者采纳真实性能Profile，现场/放行Owner另验 |

当前完整范围的有限自审/验证由本永久原会话负责，总控只接收状态和协调依赖，不再作为内容复读门；发现具体字段/调用矛盾，只暂停受影响切片并在此唯一指导修订。未build/run、正式平台Contract、真实WPF/DB/网络、性能/HIL/现场不得标通过。后续实现仍以明确授权切片派发，不自动进入产品代码或扩大模块范围。
