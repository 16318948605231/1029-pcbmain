# Query 独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`Q-C1, Q-C2, Q-C3, Q-C4`

- 模块：`IM-045 query`（受控查询与流式导出）
- 来源：`PKG-042`；候选交付包：`Query.Core`、`Query.Adapters`、可选 `Query.Wpf`
- 状态：`DesignReview/Prep`
- 版本：`0.4.0-prep`
- 日期：2026-10-12
- 本轮修订：完整批准范围文档收口；冻结数据库注册装配、聚合/附件编码扩展、持久CAS与回查、格式字节规则及WPF草稿/动态列接点；不启动产品实现
- 规划消费者：复判检索、SPC 数据准备、生产追溯与数据工具
- 技术基线：C# / .NET 10；宿主可为 WPF、服务或命令行；数据库和导出库均通过适配器注入
- 图像和原始 2D/3D/点云数据通过 IM-066 文件对象引用读取；数据库字段只存元数据和引用

本文是独立模块的唯一实施指导。它描述可脱离 PCB/PCBA 检测平台复用的查询能力，附录 B 冻结模块 Core v0.2 基础 DTO/端口，附录 C 冻结完整范围的可选扩展和软件装配；选定 IM-066 注册读写和本机 DevExpress XLSX 接点，不批准产品数据库字段、权限或平台事实 Schema。`IM-045` 独占 `PKG-042` 的通用数据集、条件树、排序、分页、快照、聚合和导出职责；`IM-015 inspection-evidence` 只提供已发布事实、Manifest、回执和按身份的证据读取，不能被本模块当作通用查询实现。正式 Contract/Schema、State/Owner 和数据主权协议由其原 Owner 采纳后绑定；本页 §11 是按附录 B 的调用片段；生产字段、数据库映射和宿主事实必须另外由原 Owner 绑定。状态保持 `DesignReview/Prep`，不表示已实现、已运行、已完成性能测试或取得生产资格。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/query/Asun.Modules.Query.Core/Asun.Modules.Query.Core.csproj`；namespace：`Asun.Modules.Query`。预定唯一Core测试/无UI Host工程：`tests/Modules/query/Asun.Modules.Query.Core.Tests/Asun.Modules.Query.Core.Tests.csproj`（net10.0 BCL Exe，见§12.4）。上述项目尚未创建。
- 允许变更范围：仅上述 Core 和测试工程目录；在明确获准的实现切片中，必要的新文件也只能放入这两个目录。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- Core切片状态：Q-C1/Q-C2/Q-C3/Q-C4均为 `ModuleCoreImplementationReady`（2026-10-10主控按DEV-GOV-010 §3.1六项规格接收）。仅限本页Core范围；尚未创建/构建/运行产品代码。真实DB、硬盘恢复、WPF与产品集成仍为 `PreparationIncomplete / NotReady`，U1指导内容已主控接收；真实WPF/后端/产品资格未关闭，未标UI为ModuleCoreImplementationReady。权威代码仓库/分支仍须在另行授权的实现任务开工前绑定。

## 1. 目标与边界

### 1.1 负责的能力

Query 接受受信主体、用途和一个已登记的数据集投影，完成以下工作：

1. 读取数据集、字段、算子、比较器和导出格式目录的只读版本。
2. 校验并规范化强类型条件、时间区间、单位、排序、分组、聚合和预算。
3. 在适配器提供的保证下建立固定快照，或明确标记为实时浏览。
4. 以稳定全序执行 keyset 分页，签发绑定查询语义和授权上下文的游标。
5. 返回精确、估计或未计算的计数，并保留其来源和一致性语义。
6. 保存、加载和逐版本迁移查询意图；不保存授权、连接、快照或游标。
7. 在有界队列上读取、编码、写入和发布流式导出；只有完整清单和发布回执成立后才报告完成。
8. 发出可观测的阶段、进度和诊断事件；最终结果以返回值或持久回执为唯一权威。

### 1.2 明确不负责

Query 不拥有以下事实或权力：

- PCB、PCBA、SPI、AOI、点胶、涂覆或任何制程判定、阈值、目标关联、缺项政策。
- 复判领取/提交、SPC 分母/规格限/控制限、生产放行、返修闭环或 MES 业务动作。
- 数据库表名、连接字符串、`DbConnection`、任意 `IQueryable`、任意 SQL、脚本或私有主键。
- 图像解析、质量评估、HALCON 算法和 AsunImage 内部访问。视觉证据由 040/041 或宿主提供的公开端口读取。
- 设备、相机、运动、灯光、PLC、SDK 句柄和硬件副作用。
- 以 Grid 当前行、客户端缓存或多次实时翻页拼接正式总体或全量导出。
- 用“无数据”掩盖无权、超时、快照失效、撤权、取消或未知提交。

调用方拥有流程顺序、目标/工单关联、工艺解释、质量放行和设备副作用。Query 返回的是受控投影和完整性事实，不是质量结论。

### 1.3 独立性验收

断开原产品 Shell、ViewModel、私表和隐藏窗口后，`Query.Core` 必须能由最小宿主构造、校验、执行、取消和释放。两个实例必须能使用不同主体、语言、授权修订、数据集和取消令牌并行运行而不共享可变“当前查询”。至少两个不同行业视觉消费者接入时，核心无需修改；复判、SPC 和追溯只应通过公开投影和用途配置表达差异。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Query.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1.3 已明确"断开原产品 Shell、ViewModel 后 Core 必须能由最小宿主构造运行"。

**Blazor/Web**：查询是 Web 端 P1 优先需求（SPC 看板、结果查询、证据浏览）。服务端执行查询；大文件通过 HTTP Range 分片下载；查询结果分页，单次最多 100 条；§1 已明确"不暴露万能 SQL 或任意表名"——Web 端只通过模块公开投影查询。

**AI 数据分析**：`ai-dataset-governance` §7.4.2（L2）的分析依赖本模块查询生产批次数据（工程师修正记录）；本模块按查询契约提供数据，不直接参与 L2 分析逻辑。

**HALCON 不适用**：本模块是纯数据查询，不执行视觉算法；HALCON 备选 CI 不涉及本模块。

## 2. 依赖、端口与所有权

### 2.1 依赖方向

```text
消费者/宿主
   -> Query.Core（契约、校验、游标、状态、导出编排）
      -> AuthorizationPort、CatalogPort、ProjectionPort、SnapshotPort
      -> CursorPort、OperationStore、AuditPort、ExportTargetPort、EvidenceRetentionPort
      -> DiagnosticsPort、FormatAdapter
   -> QueryIntentService -> SaveQueryPort、IntentMigrationPort（共用校验/授权/操作存储）
```

`Query.Core` 不反向引用宿主页面、领域包、数据库驱动或 AsunImage。适配器是唯一可以持有原生数据库连接、reader、事务、文件句柄或外部 SDK 对象的边界；原生句柄不得出现在公开请求、响应或 UI 绑定对象中。

### 2.2 端口职责

| 端口 | 输入 | 输出/责任 | 禁止 |
|---|---|---|---|
| `IAuthorizationPort` | 主体、动作、对象、用途、权限修订 | 当前允许范围、字段可见性、盲审策略、撤权/租约守卫 | 用角色名推断行权限；在缓存中延长授权 |
| `ICatalogPort` | 数据集/字段/算子 ID 与修订 | 不可变目录、类型、单位、null/排序/成本/能力 | 接受显示名、表名、未登记算子 |
| `IProjectionPort` | 已验证投影、规范条件、排序、受信目标/当前授权 | 有序行、扫描/EOF、来源修订；Core计数/聚合 | 返回私有表或未经权限过滤的数据 |
| `ISnapshotPort` | 数据集、模式、预算 | 快照/实时上下文、源代、TTL、可恢复信息 | 用最大 ID/时间戳冒充封闭水位 |
| `ISaveQueryPort` / `IIntentMigrationPort` | 版本化意图、所有者、共享范围/明确迁移映射 | 幂等保存、读取回执/纯确定迁移及差异 | 保存 token、授权、连接或当前结果 |
| `ICursorPort` | 完整绑定和锚 | 同步认证编码/验签 | 裸 hash 或未认证解析 |
| `IOperationStore` | 原 ID、作用域、请求 hash、Sequence | 原子预约、CAS、原操作回查 | 未完成记录按缓存 TTL 淘汰 |
| `IQueryAuditPort` | 受控结果摘要/身份集合 | 幂等审计回执 | 审计失败仍交付 |
| `IExportTargetPort` | 受控目标和原操作绑定 | 硬盘 staging、检查点、发布/原回执 | 覆盖用户文件或删除其它操作文件 |
| `IEvidenceRetentionPort` | 已批准证据引用闭包、保持期限 | 保持屏障、释放回执 | 逐行 pin 后声称全闭包已保持 |
| `IFormatAdapter` | typed 行、格式 Profile、取消令牌 | 有界编码块、完成清单 | 把 `ToString()` 或 UI Grid 作为原值来源 |
| `IDiagnosticsPort` | 脱敏阶段事件、计量 | 结构化指标/日志/trace | 记录秘密、游标明文、敏感字段值 |

所有端口实例由宿主显式注入。模块不得使用 Service Locator、静态连接池、自动发现、环境变量中的生产连接或隐式线程。

## 3. 输入与输出语义（Core 类型唯一见附录 B）

本节规定 Core 有效域；附录 B 是唯一 v0.2 基础类型/签名定义，两者共同构成 v0.2；可选新增能力唯一见附录 C。产品字段、目录实例及跨模块序列化映射继续由原 Owner 采纳，不阻断不依赖它们的 Core。所有字符串均按 UTF-8 字节数限制，ID 不受语言切换影响。

### 3.1 请求上下文

| 字段 | 类型/单位 | 必填 | 默认/范围 | 规则 |
|---|---|---:|---|---|
| `ProtocolVersion` | `int` | 是 | 当前支持 `1` | 未支持版本拒绝，不降级 |
| `RequestId` | `Guid` | 是 | 无默认 | 宿主生成并保持重试关联 |
| `Snapshot.ExecutionId` | `string` UUID D | 首次无 Snapshot | Core 分配 | 续页及导出绑定原值 |
| `Identity.SubjectId` | 稳定主体 ID | 是 | 无默认 | 与实例受信身份匹配，不能由 UI 用户名拼装 |
| `Identity.Purpose` | 登记稳定用途代码 | 是 | 无默认 | 工程夹具为 ReviewSearch/TraceExport；业务目录由 Owner 绑定 |
| `Identity.TenantId/ScopeId/SessionId` | 不透明稳定 ID | 是 | 无默认 | 与实例一致；非 SQL、表名或隐式全局当前用户 |
| 宿主 `Culture` | `zh-CN`/`zh-TW`/`en-US` 等 | 非 Core 字段 | 宿主资源 | 只影响显示，不影响值、hash、排序 |
| `CancellationToken` | 方法参数，非 DTO 字段 | 调用时传入 | 不持久化 | 取消是请求，不等于资源已排空 |
| `Budget.DeadlineUtc` | UTC instant，100 ns | 是 | 无生产默认 | 必须晚于入场时间且不超过 Profile 上限；同操作重试不延长 |

### 3.2 查询意图

| 字段 | 类型/单位 | 默认/范围 | 校验 |
|---|---|---|---|
| `DatasetId/Revision` | 稳定 ID/修订 | 无默认；各 ≤128 UTF-8 字节 | 目录必须存在且摘要匹配 |
| `ProjectionFields` | 有序字段 ID 列表 | 必填；1..256 个 | 每字段可投影且有类型/单位/脱敏定义 |
| `Condition` | 版本化 typed AST | 默认不提供；节点 1..1024、深度 1..32 | 仅登记 `And`/`Or` 和叶子；空组、脚本、子查询、任意 Not 拒绝 |
| 时间范围 | 两个 UtcTicks 叶子组成 And(Ge start,Lt end) | 可选；跨度受 Profile 限制 | 本地时间由宿主按显式 offset/规则解析，不另设重复 TimeRange 字段 |
| `OrderBy` | 1..8 字段 + 唯一键 | 省略时采用目录完整默认序；无默认序拒绝 | 每列方向、null 位置、比较器、稳定键固定并进入 hash |
| `GroupBy` | 登记维度列表 | 默认空；≤8 个 | 仅登记桶/维度；隐式 join 拒绝 |
| `Aggregates` | 登记聚合列表（含AggregatePolicy） | 默认空；≤16 个 | Average默认固定avg-decimal-to-even-v1，也可明确ExactFraction；Policy、精确分子/分母、投影scale/ToEven规则进入hash；无值不是0 |
| `PageSize` | 行数 | `100`；1..1000 | 不能用续页修改旧值 |
| `Consistency` | `Fixed`/`Realtime` | `Realtime` 仅浏览 | SPC/正式全量导出必须 `Fixed` 或封存工件 |
| `CountMode` | `Exact`/`Estimate`/`None` | `None` | v0.2 Estimate返回NotComputed（无估算适配）；超时不返回0 |
| `Budget.Profile` | VersionRef | 宿主批准值 | 缺失/超限拒绝，不自行放宽 |

条件叶子使用字段声明的 CLR/协议类型：`string`、稳定枚举代码、`bool`、有限十进制/整数、UTC `Instant`、带时区规则的本地时间输入。`NaN`、`Infinity`、`Eq(null)`、空 `IN`、集合内 null、单位不明或精度不可表示的值拒绝。文本不自动 trim、改大小写或 NFC/NFKC；这些规则进入字段比较器版本。

长度、深度、集合和字节上限是防资源耗尽的模块默认上限；消费者 Profile 可更严格但不得放宽核心安全上限。模块不得把 SQL 翻译失败退回无界客户端全量读取。附录 C.2 的 CorePredicateV1 是事先登记、按固定排序逐块读取并受原累计预算限制的主执行策略，不是翻译失败后的 fallback；未登记策略或预算不足整体拒绝。

条件缺席只表示不筛选；已提供的条件不得因来源缺失而被忽略。字段目录须区分原事实明确未知、历史未记录、来源暂不可用和非法值，不能统一变为空串、0 或 PASS。字段不支持筛选时返回 `QRY_FIELD_UNSUPPORTED`；已登记来源运行中不可用时按 `QRY_DATA_QUALITY_DEGRADED` 保留缺口，不能将缺口当成满足“未知值”条件。历史归属、名称、单位和解释版本来自当时的权威记录，不按当前机台配置或最新字典补齐；检测时间、提交时间与摄入时间分别登记来源和精度，不以显示时区或毫秒截断改变查询边界。

### 3.3 查询响应

响应包含 `ExecutionId`、协议/目录/数据集修订、查询语义 hash、权限修订、快照/实时标识、字段描述、行粒度、当前页 typed 行、`HasNext/HasPrevious`、游标、计数语义、状态、诊断引用和资源结束状态。`Count` 结构必须携带：

- `Kind`: `Exact`、`Estimate`、`NotComputed`、`Unavailable`；
- `Value`（仅 exact/estimate 有值）、来源/观察点、快照身份和误差/下界说明；
- 对 SPC 用途的总体成员数、有效测量数、Unknown/缺测覆盖来源（这些定义由 045/领域 Owner 提供）。

`PASS`、`FAIL`、`Unknown` 是调用方事实状态的投影，Query 不重分类、不补 0、不删除 Unknown。

### 3.4 游标

游标必须是认证保护的 opaque token 或不可猜的服务端句柄，至少绑定：协议、查询 hash、主体/租户/用途、当前权限和字段可见性修订、数据集/源代、快照/封闭边界、完整排序、typed 锚值、页大小、方向、预算修订、签发/到期和保护版本（认证token的密钥版本，或C.2.1服务端句柄的实例代）。锚保存实际完整值（包括 null、精度和稳定键），不能用 UI 截断值。

验签/完整性、到期、授权、请求语义、目录/源代、方向、页大小、锚类型必须按顺序核验；任一不符返回 `QRY_CURSOR_INVALID`/`QRY_QUERY_CHANGED`，不回退第一页。裸 Base64、普通 hash、URL 明文锚和可推测递增 ID 都不合格。

### 3.5 导出请求与清单

导出请求独立声明 `Scope`（全量匹配、批准成员集合或当前页）、`FormatProfileId/Revision`、用途、字段、单位/时区、证据闭包策略、目标临时空间和总字节预算。`CompleteManifest` 绑定查询 hash、快照/来源修订、实际行数/字节、Unknown/排除说明、文件角色/长度/hash、格式/保护 Profile 和发布回执。清单不循环包含自身 hash。

正式全量导出不能来自 Grid 当前行或多次实时请求；不能在快照失效后悄悄换新快照继续写旧文件。

清单必须明确实际包含的事实类型、投影字段、附件角色、来源版本和省略项。仅导出结构化事实或证据引用，不等于导出了原件字节或完整追溯链；只读到提交状态，不得宣称包含质量最终处置。`Published` 只证明本次声明范围完整发布，不扩大范围，也不赋予质量或生产验收资格。

## 4. 规范化与执行流程

每次执行按以下顺序运行；第 1–6 步拒绝不建立长快照，取得资源后的失败按 §7/§8 真实排空：

1. 限制请求字节、节点、深度、值长和集合长度，解析协议版本。
2. 读取并锁定目录修订，核字段类型、单位、null、比较器、支持能力和成本。
3. 解析时间：瞬时点按 UTC；本地墙钟必须带时区规则；范围统一 `[start,end)`。
4. 规范化条件、排序、分组、聚合和字段选择；计算类型标签完整的语义 hash。
5. 调用授权端口，获得动作、字段、行范围、盲审策略和当前权限修订。
6. 校验 BudgetProfile、Consistency 能力、快照寿命、并发和临时空间。
7. 由 Snapshot/Projection 适配器建立固定快照或实时上下文；返回源身份/代次和可恢复能力。
8. 执行 keyset 首页：在已授权匹配集合中以完整序取 `PageSize+1`；额外行只用于 `HasNext`，游标锚定最后交付行。
9. 计数/聚合若请求，必须使用相同语义、权限和快照；封存 as-of 可用新逻辑读 scope 读取同一不可变 cut，不能在新连接上读取当前数据补 count。
10. 每页交付前再次通过授权守卫；将响应和通知绑定 `ExecutionId + RequestRevision`。
11. 结束、取消、超时或失败时排空 reader/worker/编码器，释放本次资源并返回可判定终态。

实时浏览必须在原Intent和结果Snapshot明确 `Consistency=Realtime`、观察点和“翻页期间可能变化”语义；实时页不能被 SPC/报告当固定总体使用。

### 4.1 同步与异步入口

核心唯一公开入口以附录 B 的 `IQueryService` 为准：

| 入口 | 适用 | 行为与限制 |
|---|---|---|
| `Validate` | 查询意图的同步结构预检 | 只用构造时注入的不可变目录校验类型、有效域、预算形状和协议；不做数据库/实时授权/并发预约，不证明执行许可。导出范围/格式/目标的专门预检由 `ExportAsync` 执行 |
| `QueryAsync` | 单页查询及无 UI、服务、WPF、复判/SPC/追溯正常路径 | 执行一页并传递 `CancellationToken`；翻页将前一页游标放回 `QueryRequest`，再次调用同一入口；不得偷偷同步全量缓冲 |
| `ExportAsync` | 所有正式、流式、有证据或可恢复导出 | 有界 reader→encoder→writer 管线；取消/撤权/发布未知必须返回对应状态；完成以清单/回执为准 |
| `QueryOperationAsync` | 导出或异步操作状态、发布回执和恢复状态查询 | 通过 `operationId` 查询原操作；`NotFound` 不证明副作用未发生，不得据此创建第二个操作 |
| `ReleaseExecutionAsync` | 不再浏览某个固定快照 | 关闭该执行的新续页、取消其在途请求并等待实际排空后释放快照；重复调用同身份幂等 |
| `CloseAsync` / `DisposeAsync` | 宿主关闭 | `CloseAsync` 允许取消等待并返回未排空状态；`DisposeAsync` 复用同一关闭任务，等待实际资源与回调归还；排空未知不报关闭成功。没有独立公开排空 API |

保存、读取和迁移查询意图通过附录 B 的 `IQueryIntentService` 无 UI 调用，不把保存状态或 CAS 塞入纯查询入口。

`Validate` 不得通过 `.Result`、`.Wait()` 或阻塞异步 I/O 实现；`QueryAsync`/`ExportAsync` 在实时授权、目录当前性和预算入场后重新校验，不信任预检回执。所有异步入口使用相同规范化/错误/授权/资源语义，不切换成同步全量缓冲。

### 4.2 条件语义、参数化和规范 hash

主路线是白名单 typed AST → Core 校验/规范化 → 已登记执行策略。IM-066 主适配采用 C.2 的固定 statement + keyset 候选读取 + CorePredicateV1；可证明的必要范围条件才作为固定参数下推，不生成任意动态 SQL。其它适配可登记语义等价的参数化计划；禁止接受调用方 LINQ 表达式、SQL 片段、表名、排序文本或脚本。SQL 标识符只能由 Catalog 中批准的映射生成，值全部作为驱动参数；字段/方向/运算符不能靠值参数代替白名单。StartsWith/Contains 将用户输入视为字面值，后端 LIKE 的 %/_/escape 必须转义，不能把 UI 输入变成通配表达式；含通配符的单独业务能力须先登记算子，本版不接任意模式。

| 操作/状态 | 固定规则 | 反例与输出 |
|---|---|---|
| Eq/NotEq/Lt/Le/Gt/Ge | Known 同 Kind/单位值产生 True/False；非 Known 比较产生 Indeterminate，最终只有 True 命中 | NotEq(PASS) 不会自动把未知当 NG；要查未知使用 IsUnknown 或明确 Or |
| In/NotIn | Known 值成员关系；非 Known 为 Indeterminate；集合内 null/异型值或空集合拒绝 | [PASS, null] 拒绝；未知不等于不在 PASS 集合 |
| IsNull/IsNotNull | IsNull 只匹配 Null；IsNotNull 只匹配 Known | Unknown/缺失/不可用不混入已知非空总体 |
| IsUnknown | 仅匹配来源明确记录的 Unknown，不能匹配 Missing/Unavailable/Invalid | 缺来源返回缺口，不伪造历史 Unknown |
| StartsWith/Contains | 仅 Text、目录已登记、固定 Ordinal/OrdinalIgnoreCase，无自动 trim/NFC | 条码 `001%_` 是字面值；大范围 Contains 需成本/扫描准入 |
| And/Or | 节点至少一个孩子；每叶产生三值 True/False/Indeterminate：不可计算产生 Indeterminate，And 的 False 优先、Or 的 True 优先，最终只有 True 命中 | 明确 IsNull/IsUnknown 给 True/False；仅数据源退化不可据此推断所有记录为 False。正式固定总体遇必需来源缺口返回退化错误 |
| 参数变化 | 任何字段、比较规则、排序、单位、group/aggregate/范围变化产生新 semanticHash/执行 | 拒绝用旧 cursor 改 PageSize；UI 草稿变化不能覆盖旧完整包 |
| 多候选身份 | 同码/同名/同 hash 都不推断同实体；稳定身份歧义返回数据质量错误 | 精确明细 0=不存在，>1=歧义，不能挑 first/latest |

时间输入在宿主解析为 UTC Scalar，歧义 DST 必须明确 offset 与规则版本，否则 QRY_TIME_INVALID；UtcTicks 范围为 DateTimeOffset 可表示域。不静默降精度：源只能秒/毫秒精度时，目录说明该精度与边界可表达域；不能声称保留原 100 ns。

规范 hash 固定 SHA-256 域 `Asun.Query.Intent/v2`。canonical 采用 UTF-8 byte length 前缀（无 BOM）、Kind/节点标签、整数 little-endian 定长和严格原文本；不可用逗号拼接或 ToString(current culture)。规范化顺序：按原规模检查 → 锁目录 → 检类型/单位/算子 → Decimal 归一数值 → 同逻辑节点展平 → And/Or 子节点按 canonical 字节序排序且相同字节去重 → IN 同型值排序去重 → 补完整默认排序和末稳定键 → 编码数据集/目录/比较器版本、字段有序表、条件、排序/null rank、组/聚合、Fixed/Realtime、countMode、页大小 → hash。不能重排投影字段或混合 And/Or，不做需要领域知识的逻辑化简。RequestId、权限 token、cursor、deadline、显示语言不进入意图 hash；请求/操作 hash 另绑定身份、预算修订/原期限、范围/格式/目标和快照身份，不能把纯语义 hash 当授权证明。

### 4.3 聚合与固定成员

CountRows统计已授权且命中固定成员的源行；CountKnown只计指定字段Known。Sum/Average仅Int64/UInt64/Decimal；按decimal的96位整数系数与scale构建有界BigInteger精确累加（源decimal scale≤28、数值文本≤64B、累计行数≤MaxScanRows），无中间decimal加法/除法隐式舍入。AggregateSpec.Policy进入规范化和hash：非Average必须None；Average的Default规范为固定avg-decimal-to-even-v1，宿主也可明确AverageDecimalToEvenV1或ExactFraction。两种Average都先约分为ExactFraction(正Denominator)；真实聚合值始终保留精确Numerator/Denominator字符串。avg-decimal-to-even-v1再生成最多28位小数的DecimalProjection：分子符号单独处理、以绝对值整数商和余数计算，scale=28开始执行round-to-nearest-even，正负tie都取偶数绝对系数再恢复符号；若96位decimal系数溢出则逐级降低scale并重新ToEven，直到可表示或scale=0仍溢出并返回QRY_AGGREGATE_OVERFLOW。去除显示尾零后的实际scale写入结果；Projection.IsExact由最终投影带符号整数系数C与实际scale严格验证：C×Denominator == Numerator×10^scale时为true，否则为false；不能仅凭分母质因子判定。Projection.Canonical遵守Decimal的无指数、无前导零、无-0规则，Scale等于去尾零后的实际小数位。7/3正常返回ExactFraction(7/3)+DecimalProjection(2.3333333333333333333333333333, scale=28, IsExact=false, PolicyId=avg-decimal-to-even-v1)，不再令聚合失败。ExactFraction政策只返回精确分数，宿主必须按该值显示/导出，不能自行舍入；普通首发Host使用Default/avg-decimal-to-even-v1。Sum在完成精确累加后才转换decimal并核范围/精度；Average直接用BigInteger总和除以有效项数约分，不先调用Sum的decimal转换，避免大总和使合法均值失败。QRY_AGGREGATE_PRECISION仅用于策略缺失/未知、源精度超过Core契约或无法构造精确分子分母，不能用于7/3等正常非有限decimal均值。Min/Max仅目录声明可排序类型。空集合CountRows/CountKnown=0，Sum/Average/Min/Max=Null且ValidCount=0，不能补零测量。Unknown/Missing等以MissingCount和原因摘要保留，不重分类事实。

GroupBy不为空时，QueryIntent.Sort只允许完整GroupBy维度的全序（缺省为每维Asc/Last），不附源id末键；空GroupBy但有Aggregates为唯一全局组，Sort必须空且无游标。Rows分页的源稳定键规则不适用聚合输出，ProjectionRead源读序使用Dataset.DefaultSort完整稳定键，Cursor的group锚只由Core核，不传成源行锚。AggregateSpec.OutputId唯一、1..128B；CountRows.FieldId=null，其余必须填登记字段。Min/Max保留原Kind，Sum输出Decimal，Average输出ExactFraction及按Policy选择的DecimalProjection，Count输出Int64；ValidCount/MissingCount都是已授权源成员计数，Unknown/Null归MissingCount并有摘要原因，隐藏成员不参与。UI和导出必须同时说明PolicyId、实际scale和IsExact，不能把DecimalProjection当原始计量值。

GroupBy桶、首检/复测成员选择和机会数由源 Owner 的注册投影完成；Core 不从时间戳挑最新人判。Group 的整个 typed 元组构成稳定组键（含状态/null rank），拒绝不可排序分组维度；聚合排序不能以尚未完成的 top-N 截断总体。MaxGroups/扫描/临时空间任一超限返回 QRY_BUDGET_EXCEEDED，无局部聚合伪装完整。v0.2 计数/聚合统一由 Core 在同快照的完整受权行流上计算，不开放后端聚合快路径；避免仅凭 scope hash 对隐藏行聚合。该选择不缩减功能；后续若引入优化端口，须升契约修订并冻结可信成员证明及等价测试。


### 4.4 Canonical 二进制规则与独立 Golden

Core公开纯codec唯一签名：`public static ImmutableArray<byte> QueryCanonical.EncodeIntent(VersionRef catalogVersion, QueryIntent normalizedIntent)`。仅编码合法规范意图；未知枚举/非规范输入/原规模超限按§7.3抛QueryPortException，不做I/O；QueryService.Validate先校验/规范再调用。此签名用于独立字节Golden测试，不让测试反射私有状态。

唯一编码版本 query-canonical-v2；所有字符串采用严格 UTF-8，无BOM、无Unicode归一化；Str=U32LE字节数+原字节，空串长度0。I32/I64采用little-endian有符号定长；计数字段Array.Count采用U32LE；布尔/枚举采用单字节（false=0/true=1，枚举按 B.1 从0逐项递增，不按名称或当前语言）。Optional=存在字节0或1，1后接完整值。Array=U32数量+逐项；VersionRef/SourceRef按声明字段顺序Str；Scalar=Kind字节+Str(Canonical)。Dictionary按键的UTF-8字节序排序后编码键值数组。时间统一UtcTicks/I64，TimeSpan.Ticks/I64；Guid编码小写D格式Str，避免.NET Guid.ToByteArray混合字节序。不存在“默认省略”字段。

Condition 为 Optional；存在时节点标签 Leaf=0/And=1/Or=2；Leaf 后为Str(FieldId)、Operator字节、Values数组；Logic后为孩子数组（子节点本身不重复Optional）。先按§4.2规范，再编码。Cell为Str(FieldId)、State字节、Optional Scalar、Optional Str(ReasonKey)。SortTerm为Str(FieldId)、Direction字节、NullOrder字节。AggregateSpec为Str(OutputId)、Kind字节、Optional Str(FieldId)、Policy字节；Default先规范成AverageDecimalToEvenV1（非Average的Default拒绝）。语义字节严格顺序为：
Str("Asun.Query.Intent/v2") → Catalog.Version → Intent.Dataset → Fields数组 → Condition Optional → AllRangeConfirmed bool → 补齐的Sort数组 → GroupBy数组 → Aggregates数组 → Consistency字节 → CountMode字节 → PageSize I32。
目录Version.Sha256固定所有字段类型、单位、比较器、默认排序、Profile和格式版本；同Version却内容不同拒绝QRY_REVISION_MISMATCH。规范catalog摘要使用同record字段声明顺序规则，排除自身Version.Sha256，domain="Asun.Query.Catalog/v2"。其中目录顺序保留，不能把显示顺序排序后再误称同一目录。

请求hash域 Asun.Query.Request/v2，按 QueryRequest 声明顺序编码，但 Intent 替为 Str(semanticHash)，Cursor 替为 Optional已验签Binding（不依赖随机nonce），Snapshot按原请求存在性编码；预算全字段和身份全字段均包含。导出hash域 Asun.Query.Export/v2，按ExportRequest声明顺序，Query替为请求hash，其余完整包含。保存hash域 Asun.Query.Save/v2，按SaveIntentRequest顺序，Intent替semanticHash；迁移域 Asun.Query.Migrate/v2按声明顺序。操作重试使用完全相同原RequestId/OperationId与DTO；续页是新RequestId，新请求hash但沿用semanticHash和Snapshot。意图hash不证明授权。

游标canonical域 Asun.Query.Cursor/v2，payload=CursorBinding按声明顺序（Request以规范QueryRequest编码、其Cursor固定null，避免递归），含完整预算/原期限、身份与Snapshot；ICursorPort适配的opaque外壳先验认证，再解析payload，有效载荷上限16KiB。游标不含当前语言。同权限策略或源代变化均拒绝旧token；策略身份由Root执行记录与当前CheckAsync比对，不只信token内自报。

结果/审计摘要域 Asun.Query.Result/v2，编码有序QueryRow/Count/AggregateRows（含AggregateSpec.Policy、ExactFraction和DecimalProjection全部字段）及semanticHash、Snapshot身份；排除Operation时间/事件序列/回执，以免不可重复。ExportManifest 摘要域 Asun.Query.Manifest/v2，按字段声明顺序，排除ReceiptId；ContentSha256是实际主要数据对象字节摘要，Objects逐一记录实际文件hash/长度，ContentBytes是Objects内容文件长度之和，不含清单本体；总磁盘预算另累计清单实际字节，避免循环。通用record编码按声明顺序、可空属性带Optional，其余按上面原语；不使用JSON属性默认顺序或反射运行顺序推断协议。

最小完整意图Golden：Catalog=("c","1",64个ASCII "0")，Dataset=("d","1",64个ASCII "1")，Fields=["id"]，Condition=null，AllRangeConfirmed=true，Sort=[("id",Asc,First)]，GroupBy=[]，Aggregates=[]，Consistency=Fixed，CountMode=None，PageSize=1。此为codec fixture，Catalog具有同名已授权稳定键，不是生产目录。期望218字节，SHA-256：
`d470ea8d75cddecb68d3dd2d5ff99bd288f9c76a067bef9e1f09ffecf28fc0b9`。

```text
140000004173756e2e51756572792e496e74656e742f76320100000063010000003140000000303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030300100000064010000003140000000313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131310100000002000000696400010100000002000000696400000000000000000000000001000000
```

测试expected按上述字段独立拼接：BinaryPrimitives写固定长度，Encoding.UTF8严格写Str，固定枚举字节与固定空数组字节；既断言固定hex，也断言独立SHA256.HashData与固定摘要。不得调用被测normalize/codec/serialize来生成expected；调整codec不能顺便“更新Golden”。另外设组合Leaf/And/IN/Decimal/非ASCII/排序混方向Golden（每个独立手工字段拼接）及1025节点/超长/cycle失败断言。此处实际运行的是独立字段拼接与SHA-256计算，尚未执行产品codec测试。

## 5. 分页、快照与聚合规则

### 5.1 稳定全序

每个排序列先比较显式 null rank，再按 ASC/DESC 比较值，最后比较非空唯一键。NULLS FIRST/LAST、文本 collation、数值精度、时间精度和键必须与后端排序一致。混合方向或含 null 时不能直接套普通元组 `>`；适配器无法等价翻译时拒绝。

下一页谓词是词典序：前置列相等，某一列按完整排序语义大于锚；上一页反向所有列后取 n+1，再反转返回顺序。空页不制造锚。重试相同页可替换当前页，不声称网络恰好一次。

授权范围依赖逐记录权威归属时，查询入场授权或固定 scope hash 不能替代逐记录检查。优先由投影适配器下推授权过滤；不能下推时，在同一快照和稳定排序下有界分批读取、核归属、筛选，再形成可见页。其它租户或范围的记录不得占用可见页、暴露身份或参与 `Count`/`HasNext`；缺失归属不能获得授权，损坏来源不能猜补。扫描预算耗尽且尚未证明可见集合结束时返回 `QRY_BUDGET_EXCEEDED`，不返回截断成功页或 `HasNext=false`；下一次执行不得以未披露记录构造对外游标。

### 5.2 固定总体

可接受的固定路线必须是已选定并验证的下列之一：同一只读 MVCC 事务、受控导出/导入快照、Owner 提供的不可变 as-of 修订投影、或已封存且核验闭包的查询工件。最大 ID、最大时间、当前数据库时间和简单 LSN 不足以封闭成员集合。跨源只有 Owner 提供共同一致切面或已封口组合投影时才可称固定。

快照固定数据视图，不固定当前权限；每页、每块、证据读取和完整发布仍须当前授权守卫。TTL、空闲上限、断连、源代切换和撤权使旧 token 失效，禁止重连后继续旧总体。

组合投影必须固定参与本次查询的每个来源修订、索引版本和派生质量投影版本，并由 Owner 证明同一切面的关联关系；仅固定主数据水位而每页读取最新人工结果不构成固定总体。关联来源的版本向量与原快照共同绑定游标、计数和导出；新提交、迟到数据或人工修订进入下一次刷新。原版本不可读取时返回 `QRY_SNAPSHOT_EXPIRED` 或 `QRY_DATASET_REVISION_MISMATCH`，不换成最新版本续页。可重建索引仍是原事实的派生投影，不产生第二套结果真值；仅有高水位数值且不能证明封闭性时继续按本节拒绝固定模式。

### 5.3 计数、分组和总体

区分页行数、快照匹配行数、总体成员数和有效测量数。分组/聚合先按 Owner 规则选择成员/首检复测，再施加允许的测量条件；不能先筛 `PASS` 或非 null 再选首检。空 `sum/avg/min/max` 返回“无值”和有效项数。展开缺陷、多个相机或多个站点不增加板级分母，去重依据原 Owner 稳定身份/修订。


### 5.4 可比较域、固定总体完整性与授权围栏

比较器固定：Text/EnumCode按目录Ordinal/OrdinalIgnoreCase；Boolean false<true；Int64/UInt64/Decimal/UtcTicks按精确数值；Guid按小写D格式Ordinal。Known与Null/Unknown的状态rank在NullOrder.First为Null<Unknown<Known，在Last为Known<Unknown<Null；Direction仅反转Known值的比较，不隐式反转已声明null rank。Backward执行反转整个每列比较（包括rank），取n+1后反转返回。稳定键必须Known非空；Missing/Unavailable/Invalid排序值不进入rank，固定查询返回QRY_DATA_QUALITY_DEGRADED。Unknown只表示原事实未知，Null独立；Group整个tuple使用相同比较器/rank，组间全序由全部GroupBy列形成（默认Asc/Last）。任何未知自定义comparer拒绝QRY_BACKEND_UNSUPPORTED。

每次完整扫描维护源身份/稳定键的有界seen集合（不是仅hash比较而丢失身份）；每添加项先按保守512B+字符串UTF-8×2计入MaxTemporaryBytes，超过预算立即失败，不能为查重复无限内存。严格排序不单独证明不同时间的同ID唯一；适配器真实契约与Core seen检查共同防冲突。隐藏行身份不写响应/日志/游标。固定正式查询的筛选/排序/成员/聚合必需来源出现Missing/Unavailable/Invalid，无论Or是否可能短路，整体QRY_DATA_QUALITY_DEGRADED，不返回完整页/count/aggregate/export。普通可选证据引用缺失可保留行状态，但IncludeEvidenceBytes完整导出必须失败。已知Null/Unknown不构成来源故障。字段缺失不能当Null，时间/稳定键缺失不能隐式跳行。

QueryTarget.Row用于单行过滤，Members必须空；页/块交付Row=null且Members为精确有序成员（最大1000，单行编码块最大1）；空页/总数/聚合发布可Members为空，但contentHash及Policy绑定全范围。AuthPolicy修订必须覆盖主体/字段/行归属/共享范围的所有权限变化，任何变化使原Snapshot.AuthorizationPolicy过期。逐行Check只授予该行候选可见性；同Policy下审计成功、原reader归还后，Core对精确不可变payload进行最后Check/CommitDelivery。CommitDelivery必须在受信授权Owner锁中核相同Policy和未撤权，并登记本operation对应contentHash的一次交付准入；true是授权交付线性化点，晚于该点的撤权不能召回该次已批准payload，仍阻止下一页/块/下载。不把两个普通角色查询假装原子围栏。最终发布同样核Policy未变；权限改后不能刷新Guard继续旧总体。

QueryAudit.DeliveredMembers按每页/块分段有界写入，幂等键=(operationId,resultHash)；最终包/聚合记录成员链摘要与实际rows/bytes，不能一次ImmutableArray缓存百万成员。结果hash流式更新，查count/aggregate时隐藏行不进摘要。总聚合字典与seen集合同时占MaxTemporaryBytes；组完成后仅返回PageSize+1组，缓存其余组须Root限额/TTL或每续页同快照重新完整扫描，不能未经批准写产品数据库。v0.2选择后者，重扫仍受原执行累计MaxScanRows/总deadline；不重置累计预算。任何输入会让全扫描无法在预算内完成时拒绝，不用TopN部分组冒充全量。


## 6. 保存查询与版本兼容

保存内容是版本化查询意图、CatalogVersion、Name、所有者/共享范围及可选PreferredExport；字段/排序/分组/typed时间条件在Intent中。UI显示偏好/相对日期模板属于Host独立配置，Core不将模板当固定历史区间；执行前Host解析为绝对UTC叶子并重新校验。它不保存授权、token、快照、连接、私钥或原生对象。

加载顺序是：授权 → 解析原版本 → 登记迁移器 → 产生确定差异 → 重新执行完整校验。字段删除、枚举拆分、量纲/精度/null语义或默认时区变化不能静默删除条件、选择同名字段或取“最接近”字段；迁移失败的条目保留为不可执行并指出修复动作。未知更高版本拒绝。相对日期模板每次新执行重新解析；历史重现必须使用历史固定区间和可恢复切面。

兼容策略：同一主版本只允许向后兼容的附加字段和资源键；改变排序、null、单位、时间、授权或导出安全语义必须升主版本并提供迁移/回退。查询 hash 变化即新执行，旧游标和旧结果不再接收。

## 7. 状态、事件和错误语义

### 7.1 状态机

操作状态、发布状态和关闭状态唯一枚举见附录B；旧描述中的PublishUnknown仅指PublishState.Unknown观察，不是额外OperationState。正常路径为 `Accepted → Running → Draining → Completed`；取消/异常为 `Accepted/Running → Cancelling/Draining → Cancelled/TimedOut/Failed/Revoked/Expired`。只有本次 reader/writer/worker/回调实际归还才进入终态；`Drained`、`ResourcesReleased` 是事件，不是重复状态。排空超时走 `Draining → DrainUnknown → Draining`，仍非终态，无数据交付，不释放仍被使用的资源。未接纳的结构/授权拒绝为 `Rejected`，不能混作执行失败。

导出在 `Running` 内经过编码/发布阶段，`PublishState=Published/Unknown/NotPublished` 独立于操作状态；回执未知且实际排空后进入 `AwaitingReceipt`，只按原 operation 回查。原发布确定后 `Completed` 或 `Failed`；未知不伪造最终失败。已确认发布后发生撤权或响应取消，保留原发布事实，不回滚文件，查询/下载仍经当前权限。`Completed` 不等于质量 PASS。正常页的 `ResourcesReleased` 指本页reader/worker/缓冲资源，终态通知派发自身由实例Root保留至callback返回；返回的 `Snapshot` 是另行持有、按 TTL/释放入口管理的资源，不声称全实例已排空。

| 状态 | 含义 | 允许动作 |
|---|---|---|
| `Validating` | 尚未分配长资源 | 修正请求、取消 |
| `Running` | 可读取/计数/分页 | 续页、取消、授权守卫 |
| `Completed` | 本次页资源已经释放，快照可能仍持有 | 同快照续页或 `ReleaseExecutionAsync`；不再次释放 reader |
| `Cancelling/Draining` | 已停止继续交付，等待实际资源终结 | 查询排空状态；不复用连接 |
| `TimedOut` | deadline/预算超限 | 缩小范围或新执行 |
| `Revoked` | 当前授权/范围/盲审策略不再允许 | 新授权后新执行 |
| `Expired` | 快照、token、工件或迁移修订失效 | 重新查询/恢复检查点 |
| `AwaitingReceipt` | 发布可能成功、回执未知且本次资源已归还 | `QueryOperationAsync` 查询原操作，不重发新包 |
| `DrainUnknown` | 操作尚未确认资源归还 | 继续后台排空/隔离和回查，不提供成功、取消或关闭终态 |

### 7.2 事件顺序

事件必须带 `ExecutionId`、`RequestRevision`、UTC 时间、阶段和单调序列；进度可合并，终态/结果不可丢弃。正常顺序：

`Accepted → Authorized → SnapshotOpened? → Started → Progress* → PageReady? → Draining → Drained → ResourcesReleased → Terminal`。`QueryEvent` 携带操作/执行/请求代次与单调序列；结果唯一以返回/回查为准。纯预检不发操作事件，入场拒绝仅发 `Rejected`；一旦取得资源就走真实排空。计数性质随 `QueryResult.Count` 返回，不以事件订阅存在为前提。

取消/超时/撤权首先记录原因并停止交付，再 `Draining → Drained → ResourcesReleased → Terminal`；不能确认时发 `DrainUnknown` 并保持非终态。导出直接枚举固定集合，不依赖先生成浏览页；事件为 `Started → EncodingStarted → Progress* → ManifestVerified → PublishRequested → PublishObserved → Draining → Drained → ResourcesReleased → AwaitingReceipt/Terminal`。发布未知回查随后可发唯一 `Terminal`。订阅者异常进入脱敏诊断，不改变操作结果；迟到响应和回调均由宿主按 RequestRevision 丢弃。

### 7.3 错误码

错误码稳定、可本地化，参数只引用安全的字段位置、限制和修复动作，不带 SQL 或敏感值。

| 错误码 | 语义 | 调用方动作 |
|---|---|---|
| `QRY_PROTOCOL_UNSUPPORTED` | 协议/契约版本不支持 | 升级适配器或选择受支持版本 |
| `QRY_DATASET_UNKNOWN` / `QRY_REVISION_MISMATCH` / `QRY_DATASET_REVISION_MISMATCH` | 目录不存在、摘要/投影/源修订不符 | 刷新目录，不能回落相似表或跳过历史分段 |
| `QRY_FIELD_UNSUPPORTED` / `QRY_OPERATOR_UNSUPPORTED` | 字段能力、算子、比较器未登记 | 修改条件或等待 Owner 扩展 |
| `QRY_INVALID_CONDITION` | 类型、null、范围、深度或精度非法 | 定位字段/节点并修正 |
| `QRY_TIME_INVALID` | 无效 DST、缺时区或反向区间 | 提供明确时区/offset/范围 |
| `QRY_AUTH_DENIED` / `QRY_AUTH_UNAVAILABLE` | 无权或当前授权不可判明 | 不显示“无数据”；等待授权或换合法用途 |
| `QRY_BUDGET_EXCEEDED` | 行、字节、成本、时间、空间或并发超限 | 缩小范围/字段/并发 |
| `QRY_CONCURRENCY_LIMIT` | 该主体、用途、租户或模块实例达到并发准入上限 | 等待有界队列或减少并发；不能绕过配额 |
| `QRY_CURSOR_INVALID` / `QRY_QUERY_CHANGED` | token 过期、篡改、语义/权限/源代变化 | 开始新执行 |
| `QRY_SNAPSHOT_UNAVAILABLE` / `QRY_SNAPSHOT_EXPIRED` | 无法建立或继续固定总体 | 重新查询；不得换快照续写 |
| `QRY_BACKEND_UNSUPPORTED` | 适配器不能证明语义等价 | 选支持路线或拒绝 |
| `QRY_CANCELLED` / `QRY_TIMEOUT` / `QRY_DRAIN_FAILED` | 已取消、deadline 到达或排空未确认 | 前两者仅在排空完成后为终态；未确认时为 `DrainUnknown`，不复用资源、不发布成功 |
| `QRY_DATA_QUALITY_DEGRADED` | 公开投影存在类型、编码、身份或覆盖缺口 | 保留原状态/原因；由事实 Owner 修复或重新投影 |
| `QRY_EVIDENCE_UNAVAILABLE` | 受权引用的证据暂不可读或保持闭包不完整 | 不补缩略图；按 040/041 恢复或拒绝完整导出 |
| `QRY_EXPORT_FORMAT_REJECTED` | 格式/公式保护/消费 Profile 不满足 | 选择批准格式，不删除危险值 |
| `QRY_EXPORT_INCOMPLETE` / `QRY_PUBLISH_UNKNOWN` | 文件未完整或发布回执未知 | 隔离残件；按原操作查回执 |
| `QRY_MIGRATION_REQUIRED` / `QRY_MIGRATION_FAILED` | 保存查询不能直接执行/迁移失败 | 展示差异并人工修正 |
| `QRY_AGGREGATE_PRECISION` | 聚合策略缺失/未知、源精度超出Core契约或无法构造精确分子/分母 | 选择批准的AverageDecimalToEvenV1/ExactFraction策略或修复源精度；7/3等正常均值不得报此错 |
| `QRY_AGGREGATE_OVERFLOW` | 精确累计或DecimalToEvenV1降至scale=0仍超96位decimal系数/范围 | 缩小范围或选择仅保留ExactFraction的批准策略；不饱和、不改double |
| `QRY_AUDIT_UNAVAILABLE` | 审计未确认 | 保留原操作，停止交付，不伪装无数据 |
| `QRY_OPERATION_CONFLICT` / `QRY_OPERATION_NOT_FOUND` | 同ID异请求或确证可见作用域内无记录 | 冲突不得覆盖；NotFound不证明外部副作用未发生 |
| `QRY_SERVICE_CLOSING` | Root已关闭接纳闸 | 等待原实例排空，回查仍用原ID；不绕过未知资源 |
| `QRY_INPUT_TOO_LARGE` | 复制/hash前原输入或目录超协议限额 | 缩小条件、集合或字段，不扩大核心上限 |

未知错误不得映射为“空结果”或成功；是否可重试由错误的 `RetryAdvice` 和原操作幂等语义共同决定。

## 8. 取消、超时、线程与资源排空

### 8.1 预算

每次执行至少有：排队/连接等待、单语句和总 deadline、快照 TTL/空闲寿命、并发数、服务端临时空间、返回行/列/字节、单字段/单行字节、分组基数、编码/压缩缓冲、导出磁盘余量和慢接收者等待。`QueryBudget` 和 `QueryHostOptions` 的时间/并发/扫描/总字节均由调用方显式给出并经目录 Profile 约束；缺失、0、负值或无穷拒绝。旧例中的 5 s/30 s/2 min/60 s/4 并发/16 块/64 MiB 只作为工程夹具候选，不是生产默认或性能目标。已规定的节点/深度/页大小及单行 4 MiB、单字段 1 MiB 是 v0.2 协议防耗尽上限，Profile 可收紧；上线值仍按真实负载验证。

### 8.2 取消和排空

取消令牌传至适配器、reader、编码器和文件写入。收到取消后停止入队和新块交付，已合法交付的数据不回收；等待 reader/worker/encoder 实际终止，再释放连接、事务、缓冲和证据保持。取消协议失败、连接损坏或排空超时报告 `QRY_DRAIN_FAILED` 与非终态 `DrainUnknown`，受影响连接隔离，禁止回池。隔离不等于已终止；操作回查持续可用，收到实际归还证明后才转最终失败/取消。宿主关闭调用 `CloseAsync` 停止接纳、取消在途并观察排空；只有真实排空才 `Closed`。取消关闭等待不取消后台排空，不清除未知记录；最终通过 `DisposeAsync` 等待同一关闭完成。

同一连接/事务上的命令串行；count、分页和导出不能共用忙 reader。需要并行时由 SnapshotPort 提供独立会话并满足同一快照保证。核心不阻塞 UI 线程，不依赖 SynchronizationContext；事件回调不得在数据库/采集线程同步执行长逻辑。


### 8.3 有界根 Owner、迟到返回和独立清理

QueryService/QueryIntentService 各持有一个实例根 Owner；构造时完成不可变目录验证及容量预约。先在 MaxConcurrentOperations + MaxQueuedOperations 的有界槽登记操作 ID、受信身份、原请求、原 CancellationTokenSource、原 Task/ValueTask 的唯一 AsTask、取得中的 lease 槽、失败原因、期限、回调代次，再调用任何端口 factory。没有槽直接 QRY_CONCURRENCY_LIMIT；不能先 OpenAsync 后登记，也不能把等待队列作为无限 Task 列表。每操作最多一个取得中 factory、一个 reader、一个 snapshot 引用、一个 evidence lease、一个 writer、一个 encoder 枚举器；原 Task 与来源 DTO 在所有路径保留到取得/实际终结和清理证明齐全。计数第二 reader 串行打开；快照有 MaxSnapshots 独立槽。OperationStore 保留记录与这些运行资源槽分开，不以 WriteAsync 成功作为资源释放。

所有 ValueTask 仅消费一次，Root 跟踪的 Task 不因用户等待被取消而丢弃。Task.WhenAny/WaitAsync 只限制观察窗口：原任务未结束时返回 DrainUnknown，保留 Owner 与原任务；迟到返回 lease 由原操作 Owner 收取并排空，不能交新 RequestRevision。Factory 超时且实际可能取得资源不调用第二次 factory，不 Dispose 尚在使用的源/借用 block。MoveNextAsync、EncodeAsync、WriteAsync、PublishAsync 和 callback 的在途 Task 同样登记；退订、窗口 Unload、方法返回、异常捕获或断开连接均不是释放证明。

在业务 token 已取消后用独立清理 CTS，每轮 Deadline=clock.UtcNow+Budget.DrainObservation；该 token 限制观察，不销毁原任务。先关交付闸/请求取消，等待在途 MoveNext/Write/Publish 和 encoder 真实退出，后按 writer→evidence→reader→snapshot 引用的逆序 Dispose。DisposeAsync Task 本身也是 Root 资源：未返回就保留原 Task，后续仅观察同任务，不能并发第二次 Dispose。连接隔离仅阻止复用，不是假排空。每轮清理有限；后台以同一登记任务继续观察，服务 Closing/DrainUnknown 期间不允许新操作绕过容量。已持久 AwaitingReceipt 不再占已归还IO槽，但保留原记录与不可变快照/工件恢复引用，确认writer/lease无在途使用后可归还物理lease；持久记录由OperationStore接收确认后可由新Host回查，不能淘汰。快照Owner保证原修订可重新Open，物理读资源已归还不等于删除as-of原件。未知资源未归还仍占Root槽，不能用持久Write替代释放。

第一个业务错误（取消/超时/撤权/磁盘满/发布未知）保持为 PrimaryCause；清理错误只记脱敏诊断和 QRY_DRAIN_FAILED 的观察状态，不覆盖原错误。实际排空后回查恢复 PrimaryCause 对应终态。Published 已确认则保存发布事实与 ReceiptId；晚到取消不改成 NotPublished。Root 只有在原任务、所有 lease、快照引用和已开始 callback 全部归还后才 Closed。DisposeAsync 必须等待此事实，无法完成时保持未完成，不伪造关闭。Host 若不能无限等，应保留本实例和 Owner 继续回查；本版无跨进程运行资源移交 API。仅持久 operation/checkpoint 可由新实例恢复，目标/存储端口须先独占确认旧 writer 已死且其所有权被新实例接收，确认前拒绝恢复；不能把“发送移交消息”当接收证明。

输入硬限在复制/规范 hash 前逐项检查：请求原字符 UTF-8 合计≤8 MiB，目录≤256数据集/每集256字段/每集32预算/64格式且总≤4 MiB；节点≤1024、深≤32、单叶IN≤256、字段≤256、sort≤8、group≤8、aggregate≤16、ID≤128 B、token≤16 KiB、单值≤1 MiB、单行≤4 MiB。UTF-8 采用严格编码，非法 surrogate 拒绝；GetByteCount 不分配字节数组，checked 计量。深度优先使用32层有界栈及活动路径引用集检查循环（共享子树按每出现次数计预算），超过预算立即停止，不遍历全树后再拒绝。只支持密封节点，规范树的最大分配由已检查上限推导。HostOptions 所有容量正数，QueueBlocks≤1024、QueueBytes≤64 MiB、操作并发≤64、排队≤256、snapshot≤256、记录≤4096；工程值并非客户性能阈值。每块在入队前预约字节，归还后减计；超 QueueBytes 的单块拒绝，不靠数量上限假装内存有界。

Observer 队列容量=MaxConcurrentOperations×16，Progress 每操作最多保留最新一条；关键事件背压至空位，不能丢弃。observer 返回才算 callback 归还；不返回时同样 DrainUnknown，后续接纳关闭。Terminal只能在此前callback已返回且本操作IO/worker资源真实归还后入队；该Terminal派发自身仍属实例Root，实例Closed须它返回后才成立。事件通知不能成为唯一终态存储。Observer 禁止同步/异步等待本操作终态或 Close，否则死锁由Host负责修复；用户观察等待超时不会解除它的资源所有权。

## 9. 流式导出与安全

导出先固定查询语义和授权，再建立临时目标、证据保持屏障和有界队列。队列同时限制数量和字节；reader 按固定序读取 typed 行，适配器编码成块并持久化。CSV/XLSX 的字段精度、编码/BOM、分隔符、换行、null/空串、时区和消费程序版本必须写入 FormatProfile。聚合Average导出同时写ExactNumerator/ExactDenominator、ProjectionCanonical、ProjectionScale、ProjectionPolicyId和ProjectionIsExact；DecimalProjection是显示/消费投影，不能覆盖或替代精确分子/分母。ExactFraction政策不得由格式适配器自行ToEven；只有请求中已冻结的AverageDecimalToEvenV1才可写其明确scale投影。

CSV 引号只解决分隔，不等于防公式。未经批准的 CSV 保护策略遇到首字符 `=`、`+`、`-`、`@`、TAB、CR、LF、全角变体或前导空白风险时拒绝并建议字符串单元格 XLSX；不得 Strip 原值。XLSX 必须将不可信文本写成真实字符串，不创建公式、超链接或外部关系；长整数、前导零条码和不可精确数值按无损文本写出，原 typed 值保留在同权限映射中。

只有枚举到固定集合末尾、所有字段/证据齐全、行数/字节/hash 核对、清单完成且发布权限仍有效时才 `Published`。网络中断的可打开片段是未完成工件。恢复只能从已持久完整块、同一快照/封存投影、固定末键、编码版本、累计摘要继续；半行 CSV 或未关闭 ZIP/XLSX 不得任意 append。重试不重置原预算和过期时间。

文件导出由适配器在宿主批准的目标范围内独占创建本操作 staging，并以不覆盖方式发布；不能覆盖既有导出或用户文件。路径与归档条目必须经过目标适配器的规范化/允许范围检查，拒绝路径穿越、符号链接或重解析点逃逸，不能只检查字符串前缀。失败或取消后先确认 writer 已排空，仅按批准策略处理本操作确实拥有的未发布临时文件；不能扫描删除其它操作目录。发布回执未知时保留恢复所需身份与工件，先通过 `QueryOperationAsync` 查原回执；已发布文件的到期删除归独立生命周期 Owner，不由查询取消或宿主关闭触发。


### 9.1 硬盘发布、取消与恢复的确定输出

工程主格式TypedJsonLines使用UTF-8无BOM、LF，字节/metadata/聚合扩展见C.4；普通行每行一个完整QueryRow：identity含namespace/id/revision/sha256；cells含fieldId/state/value(kind,canonical)/reasonKey；sortKey、evidence明确引用。数字Scalar仍写无损canonical字符串，Null/Unknown不可合并；格式版本与字节规则入ExportProfile.Version摘要。一次EncodedBlock最多一个完整行（协议单行≤4MiB）；终块CompleteRows=0且FinalBlock=true。结构化metadata不是原件附件；IncludeEvidenceBytes=true时闭包先受权保持，实际原件流也计入原Budget，不用预览缩略图代替。

FixtureDiskTargets与真实磁盘适配主路线为批准TargetId对应目录下本OperationId独占staging bundle（data.jsonl、manifest与必要附件），FileMode.CreateNew；目标与staging必须同卷。Write写成功只是内存/OS观察；Checkpoint提交前Flush(true)，持久记录核prefix后可恢复。清单及C.5确定publication.json先落盘并核摘要，Publish将整个bundle以不覆盖rename到正式目录，回执随bundle同时发布；未证明真实文件系统/原子rename及崩溃恢复资格时不得称生产可恢复。manifest文件不写ReceiptId（仅publication记录及已确认公开响应含此值），ContentBytes不含manifest本体而Budget.MaxTemporaryBytes/MaxBytes包含它。已有目标若身份/hash一致，只回原回执；异绑定报QRY_OPERATION_CONFLICT，不覆盖。

Cancel发生在Publish前：关闭新交付、等待原writer/encoder、保留或按本op策略处理已确认归还staging，输出Cancelled/TimedOut/Revoked且NotPublished；busy时只DrainUnknown。Publish正在进行时cancel/断连，不能猜未发布，状态Publish=Unknown且无可下载Manifest；真实IO归还后AwaitingReceipt。QueryReceiptAsync只读检查同op正式bundle/manifest摘要/publication记录，核当前Recover授权：确证一致Published则恢复ReceiptId和原Manifest；确证未rename且staging身份完整才NotPublished。没有记录/观察权限不证明未发布，保留Unknown或对应授权错误；无界“重试发布”禁止。

QueryOperationAsync首先读取原Owner/hash/快照/checkpoint；已归还而AwaitingReceipt才调用QueryReceiptAsync，正在DrainUnknown时仅观察原Task和排空状态，不起第二writer。证明NotPublished且源可恢复、原deadline/累计预算尚有余额、格式支持完整记录检查点时，才可同OperationId/原requestHash重入ExportAsync继续；重复进入并发由OperationStore CAS运行所有权锁合并，不起第二pipeline。检查点不支持的CSV/XLSX只在NotPublished且原budget允许重建时原ID重建staging；本版TypedJsonLines行级恢复是必验主路径。源过期/原deadline已过输出Expired/TimedOut（实际资源归还后），不换新源或新期限续写旧工件；新查询/导出是新ID，旧未发布内容仍标Incomplete。

SnapshotOpen(Request.Snapshot非空)必须核原不可变版本、AuthorizationPolicy和当前权限，返回可恢复同ExecutionId的lease或QRY_SNAPSHOT_EXPIRED。新实例仅在端口确认原Root不存在活跃资源、持久操作恢复锁被本实例接收后继续；OperationStore.ReserveAsync在原记录非终态、请求同hash时读取原状态，恢复主权另由WriteAsync(expectedSequence)把原record状态从AwaitingReceipt转换Running，CAS只允许一个接收者。receipt未知时不允许此转换；必须先NotPublished确认。新Session回查原结果合法，但恢复执行须Host经过受信Session续接并保持原DTO/hash，不能自行改Identity绕过条件；新Session未获续接则只允许读取状态/Manifest，真正新执行生成新ID。

公共OperationObservation仅在当前获权且原结果摘要一致时交付原Manifest/Page/Intent；恢复读取也先审计、CommitDelivery围栏。QRY_OPERATION_NOT_FOUND只表达该可见记录确实不存在，不证明文件没写，调用方不能根据它“再导出一次”。业务错误与清理错误保持两条事实，QRY_EXPORT_INCOMPLETE不用来覆盖已确认Published。

## 10. 可选 UI 契约

`Query.Wpf` 是可选投影，不是核心依赖。控件仅调用 Core 的同一校验/执行入口，接收宿主注入的语言资源、主题、权限摘要和命令回调，不创建自己的查询事实、数据库连接或语言切换入口。

最小任务流：选择已授权数据集/时间字段 → 编辑条件和范围 → 显示校验错误及成本提示 → 执行 → 显示查询身份、固定/实时、计数性质和覆盖 → keyset 翻页/证据跳转 → 按明确范围、用途和格式导出 → 仅在完整回执后提供下载。复判领取/提交、SPC 指标、追溯业务动作由宿主页面处理。

UI 必须区分“无数据”“无权”“执行中”“取消中”“已取消”“快照过期”“导出未完成”和“发布未知”，不沿用旧查询成功徽标。筛选变化生成新请求代次，旧响应不回填。关键范围、完整性和 Unknown 提示不能只放在 tooltip；高级成本、快照和格式说明可渐进展示。zh-CN/zh-TW/en-US 资源由宿主切换，字段 ID、hash、排序和数值不随语言变化。具体控件和绑定见 §10.1～10.3；真实 UIA/DPI/键盘按 UI 指导验收。

### 10.1 角色、控件组合及布局

可选 `Query.Wpf.QueryWorkspaceControl` 只负责查询/导出工作区；浏览者可查询/查看证据，导出者另需 Export 权限，目录维护/质量放行留宿主。输入仍为 B.1 意图；控件不引用产品 ViewModel/表，也不自动创建服务。宿主借用注入 IQueryService、可选 IQueryIntentService、不可变 QueryCatalog、资源提供器、主题与证据导航回调；Unload 取消本控件等待并释放其 Execution，不 Dispose 宿主借用服务。再次加载建立新 RequestRevision，不复活旧 cursor。

只按固定 1920×1080 窗口验证，先扣实际任务栏/边框/标题栏，控件使用剩余工作区，不假定客户区也有1080 px。查询不是影像页，不套影像占比；证据预览借宿主已有控件，Query 不解码。主布局用 DockLayoutManager + LayoutGroup/LayoutPanel：顶部命令区约56 DIP，底部状态/页导航约40 DIP；左条件区28%、中央结果52%、右身份/证据摘要20%，左右最小宽度280/240 DIP，中央最小560 DIP。可折叠右区，条件区不能因美观隐藏；窄剩余宽度时右区切为可唤回面板，中心保留固定身份/状态列与横向滚动，不缩字体。Dock 布局只保存面板位置/宽度；按用户/模块布局版本隔离，不能恢复旧查询权限、结果或隐藏关键命令。

| 区域 | 已核对25.2.3的控件/接点 | 交互和边界 |
|---|---|---|
| 条件树 | GridControl.View=TreeListView；KeyFieldName/ParentFieldName 指向本地草稿 NodeId/ParentNodeId | 分组And/Or、字段、算子、值按目录联动；字段改变立即重新校验并清除不兼容的旧值，显示需补填，不静默转换单位。拖动只改变合法树位置，阻止祖先放入子节点 |
| 结果页 | GridControl.ItemsSource + TableView；DataViewBase.AllowSorting=false、AllowColumnFiltering=false | 仅绑定当前已交付页；目录排序按钮发新 QueryRequest，禁止 Grid 对一页排序/筛选后伪装全总体。关闭本地分组/全量summary；计数和聚合由Core结果显示 |
| 高级参数 | PropertyGridControl.SelectedObject 绑定仅含可编辑预算/字段选择的本地草稿 | 参数分组为范围/返回字段/预算，生产Profile硬上限只读；编辑不直接改运行请求，不展示 secret、snapshot handle 或私路径 |
| 身份/证据区 | LayoutPanel 内目录生成的只读字段和角色列表 | 选中行只显示其固定 SourceRef/修订/可用性；证据打开发精确回调。新选择代次取消旧导航，异步返回前再核身份/权限，不回填其它行 |
| 提示/反馈 | SuperTip + SuperTipItem；普通状态横条 | tooltip只放限额、当前范围与修复说明；无权/快照过期/发布未知常显，不能只藏tip。非必要动效≤150ms，只用于面板展开/状态反馈，不使运行完成看起来提前 |
| 保存/导出 | 常显查询、取消、上一页/下一页、导出；次级保存/高级设置 | 导出先显示范围/实际附件/格式/预算，再调用ExportAsync；未知发布保留原OperationId与“查回执”，不出现“重新导出成功” |

这里明确不用任意 FilterEditor.Criteria 自动翻译、ServerMode/InfiniteAsyncSource 的 offset 模拟、内置 Grid 导出和图表自动统计，它们会绕过本页 typed/hash/授权/完整范围。条件树与 PropertyGrid 同草稿通过一条显式 AST mapper 转为 B.1；图表不是本模块新增能力，统计图归第二消费者。数据库异步等待不在 Dispatcher 上，UI只接收不可变当前页；事件进度节流合并，terminal及错误立即呈现，绝不按每行 ObservableCollection 更新。单页最多1000行，列默认显示目录优先级最高的8列，其余由字段选择，核心最多256列仍按预算拒绝/按需显示；不在页面加载时请求所有证据字节。

### 10.2 最小控件接入合同与键盘/语言

WPF 公开类 `QueryWorkspaceControl : System.Windows.Controls.UserControl`，实例方法：
`QueryBindingAttachment Attach(IQueryService query, IQueryIntentService? intents, QueryCatalog catalog, QueryViewOptions options, IQueryViewHost host, IQueryViewTaskReceiver receiver)`；
`void SetCulture(string cultureName)`；
`ValueTask DetachAsync(CancellationToken waitCancellationToken)`。
同控件只允许一个活动Attachment；重复Attach须原BindingRoot关闭回执已确认Closed，不能仅凭Detach返回覆盖借用服务。QueryViewOptions 为 `record QueryViewOptions(QueryIdentity Identity, QueryBudget Budget, bool AllowSave, bool AllowExport)`（bool是显示能力上限，不授权限）。
WPF内定义 `IQueryViewHost`：
`string ResolveText(string resourceKey, string cultureName)`、
`ValueTask OpenEvidenceAsync(SourceRef row, SourceRef evidence, long selectionRevision, CancellationToken ct)`、
`void ReportError(QueryError error)`。
宿主自己的导航/权限/主题来源通过该接口组合，不暴露业务页面类型；SetCulture 在 UI Dispatcher 调用，替换资源而不重建服务/改变 hash。缺资源回退zh-CN并诊断缺键，不能显示 raw exception。

Tab顺序：数据集/时间 → 条件树 → 查询/取消 → 结果 → 页导航 → 证据/导出。Ctrl+Enter执行合法草稿；Esc只取消当前动作而不清条件；Alt+Left/Right仅在合法游标存在时翻页；Enter在行中打开身份详情，证据打开另有明确按钮；Ctrl+C复制已授权显示值，不复制cursor/secret。字段/值错误提供节点定位和键盘焦点；取消中禁新查询至原请求排空或明确隔离，页显示旧范围但标“已过期”，不保留旧成功徽标。

| 资源意图 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| 查询/取消/导出 | 查询 / 取消 / 导出 | 查詢 / 取消 / 匯出 | Query / Cancel / Export |
| 范围变化 | 条件已变，请重新查询 | 條件已變，請重新查詢 | Filters changed. Run the query again. |
| 快照失效 | 查询已过期，请重新查询 | 查詢已到期，請重新查詢 | Query expired. Run it again. |
| 当前无权 | 无权查看，请联系管理员 | 無權查看，請聯絡管理員 | Access denied. Contact an administrator. |
| 发布未知 | 操作回执未确认，请查回执 | 操作回執未確認，請查回執 | Operation receipt unknown. Check its status. |
| 排空未知 | 操作尚未结束，请等待资源归还 | 操作尚未結束，請等待資源歸還 | Operation is still active. Wait for resources to return. |

WPF验收必须在唯一1920×1080基线下实际验证上述布局、最长英语字段、运行时三语切换、键盘/UIA、页筛选不误导全总体、旧页/证据迟到、导出回执未知及慢源关闭。字体/对比度/图标/主题沿DEV-UI-040，主题由宿主提供。没有真实运行和截图/自动化证据，本页只冻结规格，不称UI完成。


### 10.3 Binding、Session、命令与恢复

QueryWorkspaceControl.DataContext只能是模块的QueryWorkspaceViewModel，由Attach创建；产品ViewModel作为Host回调消费者。Binding.Session是control-local Guid+AttachGeneration，绑定受信Identity.SessionId；服务身份必须完全一致。Detach后旧Session不能再修改新VM。命令提交前冻结QueryRequest，执行请求代次单调递增；回填检查 AttachGeneration/RequestRevision/OperationId/Snapshot身份四项，证据导航再检查SelectionRevision及原SourceRef。后台查询由Core service Root持有；WPF的OpenEvidence、Dispatcher continuation、命令和Detach任务由控件自己的有界BindingRoot持有，页面只是投影；IsLoading=false仅代表当前等待结束，不能表示原资源归还。

WPF公开的绑定接收边界如下，宿主不得从Unloaded、Dispatcher队列为空或Detach返回推断任务已结束：

```csharp
public enum QueryBindingTaskKind { OpenEvidence, Command, Dispatcher, Detach, CloseCoordinator }
public enum QueryBindingRootState { Attached, Detaching, Detached, DrainUnknown, Closed }
public sealed record QueryBindingTaskContext(long RequestRevision,
    long SelectionRevision, string? OperationId, SourceRef? Row, SourceRef? Evidence);
public sealed record QueryBindingTaskNotice(Guid SessionId, long Generation,
    long TaskId, QueryBindingTaskKind Kind, QueryBindingTaskContext Context,
    Task OriginalTask);
public sealed record QueryBindingTaskReceipt(Guid SessionId, long Generation,
    long TaskId, bool Accepted, string? ReasonKey);
public sealed record QueryBindingDrainReceipt(Guid SessionId, long Generation,
    QueryBindingRootState State, int ActiveTasks, long LastTaskId,
    ImmutableArray<long> UnknownTaskIds);
public interface IQueryViewTaskReceiver {
    QueryBindingTaskReceipt Receive(QueryBindingTaskNotice notice);
}
public interface IQueryBindingRoot : IAsyncDisposable {
    Guid SessionId { get; }
    long Generation { get; }
    int MaxInFlightTasks { get; }
    int MaxControlTasks { get; }
    QueryBindingRootState State { get; }
    IQueryBindingTaskLease Reserve(QueryBindingTaskKind kind,
        QueryBindingTaskContext context);
    ValueTask<QueryBindingDrainReceipt> ObserveDrainAsync(
        CancellationToken observationCancellationToken);
}
public interface IQueryBindingTaskLease {
    long TaskId { get; }
    bool TryStart();
    QueryBindingTaskReceipt Bind(Task originalTask);
    void Reject(string reasonKey);
}
public sealed record QueryBindingAttachment(IQueryBindingRoot Root,
    IQueryViewTaskReceiver Receiver);
```

Attach唯一公开签名见§10.2，本节只定义生命周期，不另给变体。构造控件时建立WPF独占BindingRoot：MaxInFlightTasks=8业务槽（OpenEvidence子限额2）；另有MaxControlTasks=2独立控制槽，其中1个Detach信号工作、1个关闭协调工作。业务槽满也不能阻塞取消/Detach/关闭；同Attachment重复Detach/关闭复用已登记的原控制Task，不增加槽、递归或新Root。Root登记与Receiver账本都按相同边界有界，通知墓碑按TaskId保留至本Attachment关闭；Root持有原请求上下文、来源引用、owner/取消源及原Task，Core服务只管理自身查询资源，不替它接收UI任务。

任务阶段固定为Reserved → Started → Bound → Returned；仅Reserved可取消预约。Reserve在Root锁内记录Kind/QueryBindingTaskContext/owner及容量，超限抛QueryPortException(QRY_CONCURRENCY_LIMIT)，不启动源动作。TryStart在同锁原子核业务接纳闸：业务闸已Closing时返回false并维持未启动事实，此时才能Reject撤销Reserved；成功则阶段Started，Root必须强持原上下文并跟踪取得Task的同步调用，即使紧随其后Detach也不能删除该槽。外部异步工厂只能在TryStart=true后调用；工厂同步抛异常时Bind(Task.FromException(error))形成可收敛的原工作记录，不把异常当没有启动。Detach/协调专用控制槽在关闭阶段仍允许TryStart。

Bind仅消费原ValueTask.AsTask一次，绑定同Started槽；Root遇Closing、Detached或Receiver拒收时仍必须接受并强持原Task，不能退还运行容量或使其失去Owner。对同Task重复Bind返回原receipt；绑定另一Task拒绝且仍保留原任务，新任务由启动者原owner保留并诊断契约违反。Receiver.Receive在Root已登记后同步返回接收确认；Accepted仅表示宿主账本已收取原TaskNotice，不代表完成。Receiver拒收/抛出或迟到确认不能移除Started/Bound工作，只记录交接未确认、请求本Session取消并由原Root继续保留，直到原Task和来源/迟到回调真实收敛。Reject仅撤销确证尚未TryStart成功的Reserved槽；对Started/Bound调用Reject只记停止交付原因，不删记录、不释放仍在使用的owner/来源/Task。

OpenEvidence先Reserve(QueryBindingTaskKind.OpenEvidence, context)，context含RequestRevision/SelectionRevision/精确Row与Evidence，再TryStart并调用IQueryViewHost.OpenEvidenceAsync；Dispatcher continuation亦先登记且持有原DispatcherOperation.Task，不能以排队/Abort请求当返回。宿主接收任务通知后纳入自己的有界导航账本；失败接收时原WPF Root保留责任，不能宣称已经移交。双方仅以原Task终结及来源/回调归还证明释放；已解绑代次的迟到结果不回填VM，仍按原TaskId/Context收敛。同步/异步异常与清理观察错误分开，不覆盖业务QRY原因。

DetachAsync只在独立控制槽关闭本Session交付/登记闸、请求取消并进行有限信号/观察；其原Task不等待包含自身的Root全体排空，也不在UI Dispatcher上等待自己排队的continuation。Root保存它并在Detach Task自身返回后再核所有业务/控制槽是否归还；外部Host才能调用ObserveDrainAsync观察全Root。ObserveDrainAsync每次有独立有限token，不将该等待Task登记进它等待的账本；观察取消返回DrainUnknown与当前UnknownTaskIds，保留原Root/原Task。Detached仅表示UI解绑，Closed才要求所有已Started/Bound业务和控制工作、Dispatcher continuation及借用来源实际归还，Root自身的观察/Dispose协调通知不等待自身形成环。DisposeAsync复用唯一关闭Task，外部Host保留它到完成，不给Core同步codec添加Dispose或虚构原生资源。

| Binding属性（只在Wpf命名空间） | 类型/来源 | 控件绑定 |
|---|---|---|
| CatalogDatasets/SelectedDataset | ImmutableArray<DatasetDescriptor>/DatasetDescriptor?；Attach.catalog | 数据集选择，改变后清旧游标并校验字段兼容性 |
| DraftNodes | ObservableCollection<ConditionDraftNode>，仅UI线程、本地编辑；可编辑class形状唯一见C.6，不另造record或CompareOp属性名 | 条件树ItemsSource；NodeId只作UI树身份，不进Core AST/hash |
| FieldChoices/OperatorChoices/ValidationErrors | ImmutableArray<FieldDescriptor>/CompareOp/QueryError | 随字段联动；错误常显并可定位焦点 |
| BudgetDraft/SelectedFields | 模块本地可编辑属性集合、ImmutableArray<string> | PropertyGrid.SelectedObject仅BudgetDraft，不直接绑定运行Budget/服务 |
| RawRows/RawAggregateRows/DisplayRows/Count | ImmutableArray<QueryRow>/ImmutableArray<AggregateRow>/ImmutableArray<QueryDisplayRow>/CountResult；仅完成结果 | Grid.ItemsSource=DisplayRows（C.6），RawRows/RawAggregateRows保留typed原值；各Cell.State对应显示“未知/无值/缺失”，AggregateValue显示Exact分子/分母；若Policy为AverageDecimalToEvenV1再显示DecimalProjection实际scale/PolicyId/IsExact，ExactFraction政策显示精确分数；不ToString补0或把投影当原值 |
| CurrentOperation/Snapshot/NextCursor/PreviousCursor | B.1类型，VM私有setter，token不显示 | 身份横条/页导航资格；控件不能修改token/源代 |
| SelectedRow/SelectionRevision | QueryRow?/long，本次合法页的行 | 行选择联动右面板；一次只取批准证据角色，取消旧导航 |
| UiState/IsLoading/IsDraftDirty/StatusText/ErrorText | QueryUiState/bool/bool/string/string | QueryUiState为Editing,Loading,Ready,Cancelling,Expired,AwaitingReceipt,DrainUnknown,Detached；由当前Operation映射，错误保留原operation与修复命令 |
| QueryCommand/CancelCommand/PreviousCommand/NextCommand/ExportCommand/ReceiptCommand/SaveCommand/LoadCommand/MigrateCommand/OpenEvidenceCommand | Wpf内ICommand实现，异步任务按Session登记且不可并行重入 | CanExecute规则见下；单一exception边界映射QRY错误，不async void吞错 |

Query：Editing/Ready/Expired且Validate合法、无未排空原动作时可执行；变更草稿不覆盖已交付结果，横条标条件已变。Cancel：只对Loading有效，一次发取消，随即Cancelling并保留操作ID。Previous/Next：Ready、非Dirty且合法对应cursor；不在本页做local sort。Export：Ready、Fixed、非Dirty、AllowExport显示上限和Core实时授权均成立；对话框确认Scope/字段/附件/format/target及聚合PolicyId/scale/IsExact，普通行当前页从原Rows.Identity生成成员；聚合组不是SourceRef，聚合导出仅开放AllMatching/ExplicitMembers，CurrentPage明确拒绝，不伪造组身份。Receipt：AwaitingReceipt或DrainUnknown只查询原ID，不能转为重新导出；回查Completed后读原Manifest并显示原ReceiptId。Save/Load/Migrate：AllowSave且intents非空时常显，不向用户假装有未注入功能；绑定同Identity，迁移差异需显式确认。OpenEvidence：SelectedRow确属当前页，host回调返回前再核四项代次和当前授权；迟到结果资源交回原Owner，不注入当前选中行。

Detach的UI信号工作与Core ReleaseExecutionAsync原Task分别登记在WPF BindingRoot与service Root；导出未完成时不提前释放快照。观察到期保留Detached/DrainUnknown投影及原任务，Host继续持有两个Root直到各自归还确认，借用端口不由控件销毁；重新Attach须原BindingRoot已Closed，不能绕过未知资源或service容量。

两个独立WPF Host均在后续query模块Wpf.Tests批准范围中：A=DevExpress工作台LayoutPanel嵌入QueryWorkspaceControl（复判检索用途，宿主证据预览）；B=独立Window嵌入同控件（追溯硬盘导出用途，外部结果阅读器）。每个Host都必须按固定顺序执行：构造自己的Core service、QueryWorkspaceControl、HostTaskReceiver和生命周期账本；调用 Attach 得到 QueryBindingAttachment；保存 attachment.Root 与 Generation；SetCulture；运行命令；关闭时Host调用control.DetachAsync；该方法内部先预约Detach专用控制槽、TryStart后启动信号原Task并Bind，Host仅在自己的关闭账本保留返回ValueTask.AsTask的原Task，不对同工作再次Reserve/Bind；Detach信号Task返回后，Host外部用独立有限token调用ObserveDrainAsync（不入被观察账本），并保留Root.DisposeAsync唯一原Task；只有回执State=Closed且ActiveTasks=0才确认控件根已接收归还。返回Detached/DrainUnknown或窗口Unloaded只表示UI解绑，Host继续持有 attachment、Receiver账本和所有原Task，迟到通知按TaskId收敛；最终由Root回执确认后才释放控件/Host持有的服务。两者无产品私表/隐藏窗依赖。控件实例/Session/语言资源互相隔离，不给Core增业务判断。真实25.2.3程序集编译、Binding错误零、键盘/UIA、固定1920×1080扣除边框后的三语截图与两个Host交互回放仍是后续实际门，本轮未运行。

## 11. 两个可构造的无 UI Host

以下两个Host方法放在唯一 Core.Tests Exe 的 ConsumerHosts.cs；不是产品Shell，不创建另一个TestHost工程。方法参数都是B.2公开端口与测试所有权账本，DTO不依赖产品Schema。静态fixture helper由本节定义，无隐藏对象工厂。所有测试源租约/目标和服务均先由测试根账本预约后创建。Host不吞未知结果；返回前保留原operation/snapshot与仍活跃服务的槽，关闭的有限等待不当成释放。Root在suite结束继续观察未归还任务直到外层有限截止；截止仍未知，整个Exe非零。

```csharp
// Core.Tests私有值；所有端口由§12.3明确的夹具实例实现。
internal sealed record HostPorts(ICatalogPort Catalog, IAuthorizationPort Authorization,
    ISnapshotPort Snapshots, IProjectionPort Projection, ICursorPort Cursors,
    IOperationStore Operations, IQueryAuditPort Audit, IExportTargetPort Targets,
    ImmutableArray<IFormatAdapter> Formats, IEvidenceRetentionPort? Evidence,
    IDiagnosticsPort Diagnostics, TimeProvider Clock);
// 不传递native句柄。slot先登记，调用方Root一直持有到Receipt.ReleaseConfirmed。
internal interface ITestOwnerSlot {
    void Attach(IAsyncDisposable service);
    void Retain(Task originalTask);
    void CleanupFault(Exception error);
    ValueTask<CloseResult> CloseBoundedAsync(IQueryService service, CancellationToken waitCt);
}
internal static class ConsumerHosts {
    internal static QueryHostOptions Options() => new(2, 2, 4, 4, 4*1024*1024,
        32, TimeSpan.FromMinutes(5));
    internal static QueryBudget Budget(QueryCatalog c, TimeProvider clock) =>
        new(c.Datasets[0].BudgetProfiles[0].Version,
            clock.GetUtcNow().AddMinutes(2), TimeSpan.FromSeconds(2),
            TimeSpan.FromSeconds(10), TimeSpan.FromSeconds(90),
            TimeSpan.FromSeconds(30), TimeSpan.FromSeconds(2),
            2000, 1000, 16*1024*1024, 100, 32*1024*1024);
    internal static QueryService Service(QueryIdentity id, HostPorts p) =>
        new(id, Options(), p.Catalog, p.Authorization, p.Snapshots,
            p.Projection, p.Cursors, p.Operations, p.Audit, p.Targets,
            p.Formats, p.Evidence, p.Diagnostics, p.Clock, null);

    // Host A：复判只读检索，固定页及反向页，不进行领取/质量决定。
    internal static async Task<QueryResult> ReviewAsync(HostPorts p,
        ITestOwnerSlot slot, CancellationToken userCt, CancellationToken recoveryCt) {
        var id = new QueryIdentity("reviewer","T1","review","session-A","ReviewSearch",1);
        var intent = new QueryIntent(p.Catalog.Snapshot.Datasets[0].Version,
            ImmutableArray.Create("id","time","value","state","barcode"),
            null, true,
            ImmutableArray.Create(new SortTerm("time",Direction.Asc,NullOrder.Last),
                new SortTerm("id",Direction.Asc,NullOrder.First)),
            ImmutableArray<string>.Empty, ImmutableArray<AggregateSpec>.Empty,
            Consistency.Fixed, CountMode.Exact, 2);
        var request = new QueryRequest(1, Guid.Parse("00000000-0000-0000-0000-000000000101"),
            id, intent, Budget(p.Catalog.Snapshot,p.Clock), null, null);
        var service = Service(id,p); slot.Attach(service);
        try {
            if (!service.Validate(request).IsValid)
                throw new InvalidOperationException("Fixture validation failed");
            Task<QueryResult> firstTask=service.QueryAsync(request,userCt).AsTask();
            slot.Retain(firstTask);
            var first=await firstTask;
            if (first.Operation.State!=OperationState.Completed) return first;
            QueryResult result=first;
            if(first.HasNext==true && first.NextCursor is not null) {
                var nextRequest=request with {
                    RequestId=Guid.Parse("00000000-0000-0000-0000-000000000102"),
                    Snapshot=first.Snapshot, Cursor=first.NextCursor
                };
                Task<QueryResult> nextTask=service.QueryAsync(nextRequest,userCt).AsTask();
                slot.Retain(nextTask); result=await nextTask;
            }
            if(result.Operation.State==OperationState.Completed && first.Snapshot is not null) {
                Task<ExecutionRelease> releaseTask=service.ReleaseExecutionAsync(
                    first.Snapshot.ExecutionId,recoveryCt).AsTask();
                slot.Retain(releaseTask); await releaseTask;
            }
            return result;
        } finally {
            // 已取消userCt不用作排空；slot保留未完成Dispose的原Task，不重复Dispose。
            try { await slot.CloseBoundedAsync(service,recoveryCt); }
            catch(Exception cleanup) { slot.CleanupFault(cleanup); }
        }
    }

    // Host B：追溯硬盘导出；不同主体/用途/Session，复用Core无分叉。
    internal static async Task<ExportResult> TraceAsync(HostPorts p,
        ITestOwnerSlot slot, CancellationToken userCt, CancellationToken recoveryCt) {
        var id = new QueryIdentity("trace","T2","trace","session-B","TraceExport",1);
        var intent = new QueryIntent(p.Catalog.Snapshot.Datasets[0].Version,
            ImmutableArray.Create("id","time","value","state","barcode"),
            null, true,
            ImmutableArray.Create(new SortTerm("time",Direction.Asc,NullOrder.Last),
                new SortTerm("id",Direction.Asc,NullOrder.First)),
            ImmutableArray<string>.Empty, ImmutableArray<AggregateSpec>.Empty,
            Consistency.Fixed, CountMode.None, 2);
        var query=new QueryRequest(1,Guid.Parse("00000000-0000-0000-0000-000000000201"),
            id,intent,Budget(p.Catalog.Snapshot,p.Clock),null,null);
        var service=Service(id,p); slot.Attach(service);
        try {
            Task<QueryResult> openTask=service.QueryAsync(query,userCt).AsTask();
            slot.Retain(openTask); var page=await openTask;
            if(page.Operation.State!=OperationState.Completed || page.Snapshot is null)
                return new ExportResult(page.Operation,null);
            var format=p.Catalog.Snapshot.Formats.Single(
                f=>f.Format==ExportFormat.TypedJsonLines);
            var export=new ExportRequest(1,Guid.Parse("00000000-0000-0000-0000-000000000202"),
                "00000000-0000-0000-0000-000000000203",
                query with {Snapshot=page.Snapshot,Cursor=null},ExportScope.AllMatching,null,
                ImmutableArray<SourceRef>.Empty,format,"fixture-disk-B");
            Task<ExportResult> exportTask=service.ExportAsync(export,userCt).AsTask();
            slot.Retain(exportTask); var result=await exportTask;
            if(result.Operation.State==OperationState.AwaitingReceipt ||
               result.Operation.State==OperationState.DrainUnknown) {
                Task<OperationObservation> statusTask=service.QueryOperationAsync(
                    export.OperationId,recoveryCt).AsTask();
                slot.Retain(statusTask); var observation=await statusTask;
                if(observation.Status.State==OperationState.Completed)
                    result=new ExportResult(observation.Status,observation.Manifest);
            }
            if(result.Operation.State==OperationState.Completed ||
               result.Operation.State==OperationState.Cancelled ||
               result.Operation.State==OperationState.TimedOut ||
               result.Operation.State==OperationState.Failed ||
               result.Operation.State==OperationState.Revoked ||
               result.Operation.State==OperationState.Expired) {
                Task<ExecutionRelease> releaseTask=service.ReleaseExecutionAsync(
                    page.Snapshot.ExecutionId,recoveryCt).AsTask();
                slot.Retain(releaseTask); await releaseTask;
            }
            // 未知时不Release仍关联的快照。Close也不能提前归还它。
            return result;
        } finally {
            try { await slot.CloseBoundedAsync(service,recoveryCt); }
            catch(Exception cleanup) { slot.CleanupFault(cleanup); }
        }
    }
}
```

Options/Budget是工程夹具值，只在本节Profile限额内使用。真实调用者可生成新Guid，但重试同操作须保留原DTO/id；上述固定UUID仅在每case新建隔离Store时用。两个Host运行时同时持有不同HostPorts身份过滤，若共享存储则Store按Identity范围检查；语言是Host输出资源设置（A zh-CN、B en-US），Core不改Hash。

Save/Load/Migrate的完整无UI链同样只用公开DTO：以同受信Identity及Options构造B.3 QueryIntentService；SaveIntentRequest(op,id,catalog.Version,"检索",null,0,intent,null,Empty,budget)经SaveAsync，确认Saved/Completed后，用LoadIntentRequest(newGuid,id,saved.Identity,budget)调用LoadAsync；迁移以MigrateIntentRequest(newOp,id,saved.Identity,targetCatalog,true,budget)调用MigrateAsync，检查Differences和新Saved.Identity；任一步Unknown仅QueryOperationAsync原op，不能另生成键。更新将Saved.Identity及其Revision的Int64解析值同时传回SaveIntentRequest，不按Name覆盖。服务亦由测试slot先登记；关闭保留原Task，迁移器纯同步有限映射不访问数据库。

## 12. 测试与验收矩阵

文档阶段只核契约、顺序和可判定反例，不填写 PASS、性能成绩或生产资格。实现后至少建立以下测试层：

| 层级 | 用例 | 必须断言 |
|---|---|---|
| Core 单测 | 类型、单位、null、空组、IN、DST、规范 hash、保存迁移 | 非法输入定位明确；同语义 hash 稳定；迁移不删条件 |
| 排序/分页 | null first/last、混合 ASC/DESC、重复时间、反向页、空页 | 页间无漏重；锚为最后交付行；反向结果顺序正确 |
| 快照适配 | 同快照增删改、低 ID 晚提交、源代切换、TTL、断连 | 固定模式不变；实时模式明确变化；旧 token 拒绝 |
| 历史投影迁移 | 旧产品/板标识、条码、时间、检测/复判代码、功能明细、异常代码和证据引用映射；当前归属/字典变化、历史字段缺失和来源不可用 | 只通过注册投影；稳定 RunId/修订缺失时拒绝固定总体；历史归属不随当前配置改变；明确未知与来源不可用不合并；不忽略已提供条件或复制旧表/路径 |
| 历史分段 | 跨日/月/季度/设备分段、重叠修订、缺口、单段不可读 | 覆盖区间和源代可见；重叠按修订去重；缺口不显示为无数据 |
| 板/时间/结果筛选 | 精确板 ID、板组关系、UTC 半开区间、结果代码/组合分类、前导零条码 | 条件参数化且有目录版本；结果组合不写死；分页锚和 hash 包含完整条件 |
| 异常追溯 | Run → Finding → 位置/来源点 → EvidenceRef → TraceEvent，证据缺失/修订冲突 | 不读旧路径、不替换当前证据；缺证据与无异常可区分；040/041 保持边界清晰 |
| 授权 | 行/字段/用途/盲审、撤权在页/块/发布前后、授权服务不可达；混合租户且可见记录稀疏、逐记录归属缺失或损坏 | 不泄漏 count/hasNext；隐藏行不占可见页、不进入对外游标；扫描耗尽返回 `QRY_BUDGET_EXCEEDED` 而非假报结束；后续交付停止；不改历史已交付事实 |
| 聚合 | 首检/复测、Unknown/null、板级去重、空聚合、Average ExactFraction/DecimalProjection、ToEven边界、溢出 | 先选成员再过滤；分子/分母和实际scale/PolicyId/IsExact一致；普通7/3成功；无值不补 0 |
| 取消/资源 | reader 取消、慢消费者、回调异常、关闭、排空超时 | 不回池忙连接；状态终态明确；资源恰好由 Owner 释放 |
| 导出 | CSV 公式风险、XLSX 字符串/前导零、超大字段、磁盘满、崩溃检查点；仅事实/仅引用导出、目标已存在、路径逃逸、并发 staging 与发布未知 | 原值映射可还原；未完成工件不可下载；清单范围与实际内容相符且 hash 正确；既有文件与其它操作 staging 不被覆盖/删除；未知发布先查询原回执 |
| 恢复/发布 | commit 应答丢失、重复恢复、包 Range、权限变化 | 原操作回执唯一；恢复不换快照；下载仍检查当前权限 |
| 双消费者 | 复判检索与追溯导出使用不同 Profile/语言/取消 | 核心无修改、实例不串扰、结果语义一致 |
| UI（如采用） | 1920x1080、三语、键盘/UIA、旧响应、错误恢复 | 不遮挡关键状态；UI 与无 UI 校验一致；不藏关键警告 |
| 真实资格 | 选定数据库/驱动/格式消费者和真实负载 | 仅在执行 HIL/集成、性能和消费端测试后记录资格；Mock 不代替 |

契约测试通过 `IQueryService`/`IQueryIntentService` 和本页精确 DTO 驱动，按固定成员、字段与状态断言，不使用私有 Core 内部方法。`Validate` 对请求/协议问题的错误映射以 §7.3 为准；已接纳执行中的后端、取消和发布错误则断言对应终态、排空及原操作查询语义，不把它们伪装成预检拒绝。

合成序列必须包括：固定 S 中同刻 A/B/C、null E/F；快照后更新/删除；A 预取未提交而 B 先提交；撤权发生在预读之后；导出写半行后断电；六个风险 CSV 文本；无效/重复 DST。每个用例同时记录身份/修订、状态、资源释放和可观测事件。

### 12.1 两种审核视角的固定反例夹具

**视角A：外部算法/数据消费者。** 合成目录 `engineering.results/v1`（非生产数据）声明 `id UInt64` 唯一键、`time UtcTicks`、`value Decimal`、`state EnumCode`、`barcode Text/Ordinal`，按 time Asc NullLast + id Asc。不可变来源S包含 A=(id1,t10,value1.0,PASS), B=(id2,t10,value2.00,Unknown state), C=(id3,t11,Null value,FAIL), D=(id4,Null time,value4,Null state)；不同租户Z=(id5,t10,value9,PASS)。Identity只获A-D，PageSize=2。首次页[A,B]、第二页[C,D]，上一页精确回[A,B]；NextCursor锚为B而非C预读，HasNext=false只能源证明末尾。Predicate state Eq PASS只A；state NotEq PASS只C；IsUnknown只B；另设 DUnavailable（state.State=Unavailable）故障分支：Unavailable不是Unknown，必需来源缺口固定查询整体失败，不沿用正常[A,B]/[C,D]期望。值>1只B,D；无条件源集合Sum=7、CountKnown=3、CountRows=4，Average默认Policy=AverageDecimalToEvenV1，返回ExactFraction(7/3)和DecimalProjection=2.3333333333333333333333333333（Scale=28、IsExact=false、PolicyId=avg-decimal-to-even-v1）；普通宿主成功显示/导出该投影，同时保留7/3真实值。ExactFraction策略同一输入只返回7/3，不生成隐式显示舍入；独立Sum请求仍成功返回7。边界向量还必须断言：-1/8显示-0.125、IsExact=true；1/2去尾零后的实际Scale=1；1/6显示0.1666666666666666666666666667、IsExact=false；正负中点用具体向量覆盖：两个源值之和为±3×10^-28、有效项数2时均值±1.5×10^-28在scale=28取偶数系数±2×10^-28；和为±1×10^-28、有效项数2时tie取偶数0且不产生-0；96位边界固定M=79228162514264337593543950335：Average(M,M-1)的精确值为(2M-1)/2，投影从scale=28逐级降至0后ToEven取M-1=79228162514264337593543950334，IsExact=false；Average(M,1)精确(M+1)/2=39614081257132168796771975168，投影scale=0、IsExact=true。Sum(M,1)=M+1仍报QRY_AGGREGATE_OVERFLOW，但独立Average(M,1)必须Completed，不能先用Sum的decimal范围检查拒绝；只有投影scale=0仍越界才报该错。空集合sum Null/count0；单位错、未登记字段、Eq(null)、空IN、NaN文本、AST深33和页1001拒绝。barcode中001/%/_/空格保持字面，恶意SQL样文本仅进入参数。无图像弱信号/遮挡对Query不适用；用Missing/Unavailable/Invalid投影夹具验证退化，不做视觉插值或补PASS。重复stable id（不同hash）失败，不去重；改排序/页大小/字段/hash/Policy后原cursor拒绝。规范相等的And节点重排、1.0与1.00产生相同意图hash；字段顺序/单位/比较器版本改变产生不同hash。

**视角B：并发集成/运维消费者。** 两实例H1/H2同Store、不同Subject/Tenant/语言/取消；H1只见A-D、H2只见Z，不能共享CurrentQuery/页面缓存。源S2在分页间增加低ID晚提交、修改B人判或删除C，原S仍上述顺序和值；刷新绑定S2。先插999个不可见行再可见两行，MaxScanRows=1000时不能假报末页；未找到n+1且源未EOF，返回QRY_BUDGET_EXCEEDED并无局部页。并发相同导出OperationId同hash仅一个staging/回执，异hash=冲突；两个不同ID不可覆盖同目标。页预读后撤权、审计返回后撤权、写末块后发布前撤权分别不交付；发布确认后撤权保留已发布事实且下载拒绝。调用方取消/语句超时/断连后源仍活跃时仅DrainUnknown，busy reader/借用block不得Dispose或回池；延迟归还后才Terminal。慢observer/异常observer、不订阅、队列满都不丢终态；关闭等待取消返回Closing，随后Dispose等待同任务。发布响应丢失先AwaitingReceipt，用新Host+原Store回查同ID；NotFound不可解释为文件未写。升级/回退不同主版本拒绝cursor，不重写已发布包；迁移必须保留旧意图且报告差异。

每个夹具调用真实Core入口、注入可控端口和barrier，断言成员顺序/值/版本/hash、错误键、唯一Terminal、Owner归还计数及峰值，不用只有拒绝的授权stub证明成功链。逻辑小夹具与大负载分开，所有都是软件验证计划，未执行。纯结构Validate不伪造Draining；已接纳异步操作才有排空。应用质量物理阈值不来自本夹具。

### 12.2 切片测试与性能执行计划

Q-C1：AST/标量/parser/canonical/三值逻辑/参数计划；Q-C2：排序/反向/授权/稀疏扫描/count/group/snapshot registry；Q-C3：有界queue/文件格式/同ID恢复/磁盘失败/PublishUnknown；Q-C4：保存CAS/变更迁移/共享授权/关闭。Adapter.Tests 另测真实DB读计划参数/精度/null/collation/一致切面/索引/驱动取消；Wpf.Tests测§10；两个无UI Host在Core.Tests同Exe拥有不同Consumer Profile，不创建第二镜像工程。不跑无关模块全测；本次文档任务未执行这些工程。

工程BenchmarkProfile输入序列冻结为1,000/100,000/1,000,000行，4/32/256字段，Known/Null/Unknown三种比例、1/10%可见稀疏授权、单字段128 B与接近1 MiB、group基数1/1000/超过预算；工程并发1/4/16，慢源/慢writer/撤权/关闭故障点可重现。样本hash、随机seed、.NET/Core/端口版本、OS/硬件、所有预算/预热/样本计划记录；这些是诊断工作负载，不是客户上限。按消费者签署profile决定实际规模/并发/样本数和阈值，未提供为NotEvaluated。性能输出按§13与DEV-GOV-010记录完整排空E2E及失败/删失，硬断言源扫描/内存queue/快照/句柄不越显式上限、无隐藏数据/伪完整页/重复发布；没有真实性能结果不能称大数据长期运行通过。


### 12.3 私有端口夹具、工厂与故障位置

全部位于唯一 Core.Tests Exe，不写到 Core，不为每个场景新建测试工程。FixtureWorld 构造不可变Catalog与下表端口；它的 CreatePorts(subjectScope, diskTarget) 在已预约 ITestOwnerSlot 后调用。Clock为本测试PrivateTimeProvider，初始2026-10-10T00:00:00Z，Advance仅推进逻辑deadline/TTL，外层case/suite截止由真实 Stopwatch/系统时钟执行。barrier使用TaskCompletionSource(RunContinuationsAsynchronously)，每个Gate记录Entered/Released/Returned，测试控制明确的调用阶段，不能靠延时猜竞态。

| 测试私有实现 | 真实调用/故障点 | 必须收集/断言 |
|---|---|---|
| FixtureCatalog : ICatalogPort | Snapshot完整工程目录；IsCurrentAsync在Root预约后，故障改版本/抛出 | dataset含id非空唯一、time/value/state可Null、barcode Ordinal、全部字段登记Operators；Catalog/数据Revision由独立canonical摘要产生；Profile覆盖§11值，formats仅TypedJsonLines |
| FixtureAuthorization : IAuthorizationPort | CheckAsync分别在操作入场、每行、每页/块、发布/原回执/保存前；CommitDeliveryAsync为revocation lock下比较guard及完整Target | reviewer/T1只A-D、trace/T2只Z；逐记录归属损坏拒绝；页预读后/审计后/末块后撤权Gate；策略版本变化使cursor QRY_QUERY_CHANGED |
| FixtureSnapshot : ISnapshotPort | OpenAsync前/返回前两个Gate，Reference绑定固定S/S2；DisposeAsync前/返回后Gate | factory迟到的lease仍由原槽收取，计数LiveSnapshots不得提前0；OpenAsync传原Snapshot时仅恢复相同不可变修订/核hash，不换S2 |
| FixtureProjection : IProjectionPort | OpenAsync登记后Gate；reader.ReadAsync逐次MoveNext前/完成后Gate；DisposeAsync独立Gate | 正常投影按完整排序提供匹配源行，可配置不下推授权以稀疏扫描；ScannedRows原始扫描/EOF准确，固定S更新无效；bad type/重复id/Unavailable失败；取消后尚忙不能提前Dispose |
| TestCursor : ICursorPort | Protect使用HMACSHA256+固定测试32B密钥，Unprotect先认证再解码；keyId=test-only | 测试token上限/篡改/过期/方向/不同身份/Source与budget；constant-time比较使用CryptographicOperations.FixedTimeEquals；不用于生产 |
| FixtureOperations : IOperationStore | ReserveAsync同Owner范围原子锁；ReadAsync必须传caller；WriteAsync Sequence CAS；每处前后Gate | 同ID唯一预约、异hash冲突、回执丢失、TTL仅淘汰已结束页，未完成导出/保存保留；Store本身有max records/bytes而非无限ConcurrentDictionary |
| FixtureAudit : IQueryAuditPort | CommitAsync在每页/发布交付闸之前，唯一operation+resultHash幂等 | false/异常/迟到、与撤权竞态；empty页也审计，成员集合无隐藏Z |
| FixtureDiskTargets : IExportTargetPort | CreateAsync前登记、返回前Gate；lease.WriteAsync末块前/后；CheckpointAsync落盘前/后；PublishAsync rename前/回执后；QueryReceiptAsync原ID | 本case批准临时根下本op独占staging；实际FileStream硬盘写，完整记录Flush(true)；磁盘满用确定失败写端口和真实空间资格分开；发布成功丢回执不二次rename；路径重解析/目标已存在失败；不删非本case文件 |
| FixtureJsonLines : IFormatAdapter | EncodeAsync逐行/最后FinalBlock；Encode借用缓冲在下次MoveNext覆盖，强制检验先Write再复用 | 完整行块/末键、字节预算、null/空串/Decimal文本；慢writer Gate触发队列双上限；半行不形成Checkpoint；faulted编码器必须归还 |
| FixtureEvidence : IEvidenceRetentionPort | AcquireAsync全闭包前/后、ReadAsync每块、DisposeAsync Gate | IncludeEvidenceBytes=false正常Host不调用；true必须先全闭包保持，撤权停止读取；缺对象不可发布完整包；迟到返回保留原Owner |
| FixtureSaved : ISaveQueryPort | ReadAsync原身份/hash；WriteAsync原op/requestHash幂等+ExpectedRevision CAS；QueryReceiptAsync | 同Name不覆盖，未知保存回执先查原ID，更新保留旧版本；权威身份只由port分配且修订单调 |
| FixtureMigration : IIntentMigrationPort | Migrate纯有限版本表，v1→v2显式字段映射；无映射/删字段/单位改动输出Difference/Error | 拒绝未确认语义变化，old intent不变；Migrate写入通过与Save同原operation receipt，不调第二套私表 |
| FixtureDiagnostics、Observer | Record立即返回、只记脱敏Event；observer Enter/Return Gate及异常 | callback异常不覆盖业务错误，未返回callback根Owner仍活跃；没有observer也能完成 |
| TestOwnerRoot、ITestOwnerSlot | Reserve(operation/case)在Factory/Service前；Attach登记service；Retain原Task；CloseBoundedAsync调用CloseAsync后只启动一次DisposeAsync并Retain | Root容量=8 slots，每slot最多64原Task引用（含已归还墓碑计数），超限case失败；关闭用独立2s观察token，超时返回Closing并保留原Task/服务；ReleaseConfirmed只在原Dispose返回且所有端口Live=0才成立 |

FixtureCatalog预算矩形有明确值：duration 2min、queue2s、statement10s、snapshot90s/idle30s、drain2s、scan2000、rows1000、bytes16MiB、groups100、temp32MiB；只在本合成case使用，范围不得跨消费者冒充客户Profile。字典/行来源输入由CaseDataBuilder先按字段独立构造，fixture helper不能调用产品codec产生expected。A-D/Z是五个SourceRef Namespace="fixture"、id=A/B/C/D/Z、revision="1"、hash分别SHA256独立行原始字节；time为UTC ticks基点+10/11（不是日期格式字符串）。端口source copy及Field Cell均按公开DTO构造；reader排序锚完整包括state/null和值，页返回的SortKey与cell原值一致。Source.State Missing/Unavailable/Invalid是故障分支，正常数据只Known/Null/Unknown。

TestOwnerRoot接收移交时先原子Reserve空槽并记录原Task/service/source/lease/checkpoint引用，再返回接收确认；发送方收到确认前持续保留，确认后也保留墓碑。slot满、ack失败或root关闭禁止移交，仍由原slot负责。跨进程无运行Task移交，仅通过端口独占确认和持久快照/checkpoint恢复，不能用新slot把忙句柄“重置”。Core不依赖这些测试私有类型；真实Host实现同样遵守§8.3。

### 12.4 单一 BCL Exe、执行命令与非零规则

Core为net10.0 DLL；测试只有顶部唯一 Core.Tests 工程，TargetFramework=net10.0、OutputType=Exe、Nullable=enable、ImplicitUsings=enable，仅ProjectReference指向Core，不依赖xUnit/NUnit/WPF/数据库或NuGet下载。Program.Main支持 --suite core|benchmark、--case all|C1-canonical|C1-invalid|C2-page|C2-sparse|C2-revoke|C2-aggregate|C2-late-owner|C3-disk|C3-unknown|C3-resume|C4-save|C4-migrate|close，以及 --case-timeout-ms、--suite-timeout-ms；未支持参数返回2。每case新FixtureWorld/隔离本case目标，两个Host各调用一次且并行互相取消断言；suite选all串行case共享的文件接收，不能同时写同target。

```powershell
dotnet build tests/Modules/query/Asun.Modules.Query.Core.Tests/Asun.Modules.Query.Core.Tests.csproj -c Release
dotnet run --project tests/Modules/query/Asun.Modules.Query.Core.Tests/Asun.Modules.Query.Core.Tests.csproj -c Release --no-build -- --suite core --case all --case-timeout-ms 10000 --suite-timeout-ms 120000
dotnet run --project tests/Modules/query/Asun.Modules.Query.Core.Tests/Asun.Modules.Query.Core.Tests.csproj -c Release --no-build -- --suite benchmark --case all --case-timeout-ms 60000 --suite-timeout-ms 600000
```

上述为将来已授权实现后的真实命令，本轮未创建工程/未执行build/run。Main在进入case前登记根Owner，真实Stopwatch到10s发测试停止请求并开放本case所有可释放Gate，另给2s清理观察；未归还计为failed+DrainUnknown，并保留original tasks至suite外层截止，不进入下一case继续累积活跃资源。根Owner有8槽、未归还任务有限，不“无限等待保证最终完成”。suite截止返回非零，记录未完成case/原operation/资源种类，不把未完成样本从总数删掉。

Exe返回0仅所有要求case、确定错误/成员/Golden断言、所有释放计数和Root空闲均成立；断言或未排空返回1，参数/缺Profile返回2；磁盘权限不可用标NotEvaluated并非零，不能skip通过。外部CI/Host watchdog的实际进程截止必须比suite+清理至少多5s；WaitForExit(false)即失败，保留输出和本case恢复文件。若CI终止合成测试子进程，只记forced-stop失败，不能作为正常排空证据，也不得终止生产Host或改显示设置。不得对PowerShell job Wait超时声称child已释放。

benchmark工程诊断默认cold=5新进程样本、warmup=5、measured=50、每组固定规模/并发/输入hash；生产目标仍TargetPending。测点用Stopwatch.GetTimestamp：T0 Root预约前、TA请求Accepted（接纳记录原子写入时）、T1入场授权完成、T2快照完成、T3首合法交付页/块、T4末交付、T5本操作ResourcesReleased（原在途IO/worker/lease实际归还并登记事件时）、T6callback归还/实例Closed。DEV-GOV-010规范E2E唯一为T5-TA（Accepted→ResourcesReleased），以完整排空样本报告P50/P95/P99与n；取消起点另计至T5，DrainUnknown不得当完整样本。T3-TA首屏、T4-TA交付分别报告；T0预约前与T6实例Closed仅作附加Host开销/总体关闭测量，可附报T3-T0和T6-T0，不能替代规范E2E。原始失败/超时/删失项同时输出；峰值记录Root slots/tasks、扫描/返回、组/缓冲/临时盘、managed bytes与GC、IO和句柄。只在同输入/Profile比较“源授权下推”与“Core稀疏过滤”，结果成员必须先等价，再比较P50/P95/P99，不凭最快样本更改语义或安全限额。Benchmark数据保存在已有CI日志/消费者证据位置，不新增无消费者报告。

## 13. 性能与可观测性

本节冻结测量协议与测点，不设未经真实消费者采纳的性能达标值。每个不可变 BenchmarkProfile 必须记录唯一 ID/修订/hash、构建提交与 .NET/适配器/后端版本、OS 与 CPU/内存/存储/网络配置、带 hash 的输入集及规模分布、调用混合与并发/到达模型、队列与资源预算、时钟测点边界、故障注入点，以及 ColdSampleCount、WarmupIterationCount、MeasuredSampleCount 和各指标的验收目标/阈值来源。Profile 变更必须产生新修订，不得跨 Profile 合并数据。

冷测每个样本均从新进程/新模块实例开始，并清空模块自有缓存；OS 文件缓存、数据库缓存、外部服务和设备状态无法由模块清空时，必须记录其实际状态，使用隔离可重建夹具，不标称为冷。热测先按 Profile 固定次数执行预热，再按固定样本数测量；不使用自适应停止、只报最快值或丢弃慢样本。外部副作用操作使用可重建隔离夹具和唯一操作 ID。每个样本用单调时钟记录原始耗时；P50/P95/P99 的算法按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md) 计算，并同时报告样本数、单位和原始值。吞吐量使用 Profile 固定的观察窗口计算已完成且有效的操作数/时间，并单列拒绝、错误、重试和未完成项。

每轮同时记录 CPU、工作集/私有字节、托管分配与 GC、native/适配器缓冲、磁盘/网络 I/O、连接/句柄峰值，队列当前/峰值条数与字节、排队等待、积压变化、接受/拒绝/丢弃计数。排空时间从关闭新接纳开始，至在途操作、回调、IO/适配器资源全部实际归还结束；期限到达只记超时和未完成项，不得强杀后宣称排空。每项验收阈值必须引用消费者要求、正式 Contract/资源风险依据或已批准资格记录的稳定 ID；没有来源时写 TargetPending，只能报告测量结果，不得判定达标。协议/资源硬上限与性能目标分开，只有唯一权威中的必要性、数值和来源均已明确时才可作为硬上限，不从基准数据臆造上限。

### 本模块固定测点
分别记录授权/计划预检、连接/排队等待、快照建立、首行/首屏、后续分页、精确计数、聚合、导出首字节和完成、取消至连接/Reader/文件流真实归还。Profile 固定行粒度/行宽/null 与重复值分布、组基数、字段和证据体积、数据集/索引/目录修订、数据库与驱动版本、网络/存储、权限过滤、并发读写和冷/热缓存。记录实际与估计行量、端到端与分段耗时、吞吐、服务端/客户端内存和临时磁盘、连接/Reader 数、队列水位、慢接收者、取消/撤权生效及 drain 尾部；目标数据规模和 SLA 来源未批准时 TargetPending。

## 14. 适配器、版本、发布与回退

适配器必须声明能力矩阵：支持的数据集/目录修订、字段类型/单位、null 和比较器、固定模式、快照 TTL、count/aggregate、keyset、SequentialAccess（如适用）、取消/排空、导出格式和恢复能力。声明不能证明能力；每项需有适配器契约测试。本页选定C.2/C.3的IM-066注册读写、C.4的BCL TypedJsonLines/Strict CSV与本机DevExpress25.2.3流式XLSX、C.5同卷目标和C.6可选WPF。Npgsql由IM-066现有PostgreSQL适配持有，不重复引用到Core；EF Core KeysetPagination/CsvHelper仅复用研究/测试思想，不引新包或复制源码。具体装配、有限statement/codec、格式和恢复以附录C为准，不拿上游默认行为当平台保证。

发布单元包括 `Query.Core`、选定适配器、格式适配器及资源/版本清单。程序集主版本变化覆盖公共语义、错误码和状态机；次版本可增加向后兼容目录能力；补丁不得改变排序、授权、单位或导出安全语义。部署前保留上一份可启动包、配置/目录修订和迁移器；回退先停止新执行、排空旧 worker、核旧游标/快照不可跨版本续用，再切回兼容包。已发布事实、导出包和用户文件不得删除或改写。迁移或回退失败时保持旧条目不可执行/发布未知，不能自动降权或换字段。

## 15. 两个消费者接入断言

### 15.1 复判检索

复判宿主只传已授权候选投影、时间范围、用途和检索条件；Query 返回受权页、固定/实时语义、证据稳定引用和计数性质。Query 不领取任务、不提交复判意见、不以队列 `SKIP LOCKED` 结果充当总体。证据打开由 040/041，复判流程由 044。

### 15.2 SPC/追溯与数据工具

SPC 宿主传已批准 population/subgroup/首检复测选择和修订；Query 返回固定成员、原测量/状态、Unknown/覆盖来源和完整性信息。它不决定分母、规格限、控制限、Cpk 或良率。追溯/数据工具传注册字段、用途、格式和预算；导出必须从固定集合/封存工件建立，不从 Grid 重建总体，不写原事实，不合并私表。两个消费者必须使用同一 Core 校验、游标、取消和错误语义。

## 16. DZ-XVision 历史查询需求的可迁移抽象

### 16.1 来源与可迁移结论

只读来源为 DZ-XVision `20261004` 快照（来源说明明确其为现场流程参考，不是直接迁移基线）：

- `DZ-XVision/Runtime/ProductResultStore.cs`（SHA-256 `e662201c41a4fe2a3cd4e2fca280a2cb24eea5a51d68190b90b45a3f240cf88a`）按产品运行保存产品/程序上下文、`FixtureRunId`、产品键/编号、条码、检测/复判相关状态、检测时间、工具错误码、来源点位和图像文件。
- `SPC-YSmart30/SPC-YSmart30/SPC-YSmart30.cs`（SHA-256 `cb1d72b810913e0ea3e367735d3d0671e74ef5ae2a85223a7dec0b1bf1f31d30`）和 `SqlData.cs`（SHA-256 `6e0a8a165f904a11b19b2ed3a6282eb18a1368b3b62e1d22277576a1aabc849a`）展示了按条码、产品/程序、起止时间、结果组合、功能类别和操作日志查询，并从总结果行钻取功能明细和图像。
- `SPC-YSmart30/SPC-YSmart30/C_SqLite.cs`（SHA-256 `7d54aca86b4c3270f500d55389f41da60dfe66872c033b3ce803b70fc2fcbdcc`）展示了历史分段/备份读取的需求，但其文件路径和 SQLite 表结构不构成本模块契约。

可迁移的是操作意图和信息链：**按板/板组定位 → 按时间限定 → 按结果状态筛选 → 稳定分页 → 选择一条运行 → 查看功能/异常明细 → 通过受权证据引用查看图像或文件**。不能迁移的是旧数据库表名、中文列名、`DataTable`、文件夹路径、季度文件枚举、拼接 SQL、MES 登录/上传协议、旧页面权限和“条码+时间+拼板号”作为唯一键的假设。

### 16.2 历史查询的规范化公开投影

原 Owner 注册一个或多个公开投影，Query 只看投影，不看旧表。建议的最小字段组如下；正式字段 ID、类型和 Owner 仍需合同采纳：

这里的“板/板组”只是调用方登记的可追溯对象粒度，不能把 Query 固定成 PCB 领域；其他视觉项目可将同一位置绑定为工件、载具、样品或批次对象，字段身份和行粒度仍由其 Owner 定义。

| 投影组 | 必须表达的语义 | 查询/追溯用途 | 边界 |
|---|---|---|---|
| `RunIdentity` | 不透明 `RunId`/修订、`BoardId`、可选 `PanelId`/`SubBoardId`、产品/程序稳定 ID、源分段/源代 | 按板、板组、程序检索；详情关联 | 条码是可选业务字段，不自动等于唯一键；不得把 UI 行号或路径当身份 |
| `ObservedTime` | 检测瞬时点 UTC、可选本地显示规则、提交/摄入时间及精度 | 起止时间 `[start,end)`、历史归档分段选择 | 不能用本机时区、日期字符串或四舍五入秒值作为边界 |
| `ResultState` | 原始检测状态、复判/人工状态、最终来源状态、Unknown/Invalid 原因 | 结果筛选、SPC 成员准备、追溯 | Query 不解释 PASS/ERROR/RPASS 等代码；代码集/组合分类由领域 Owner 登记 |
| `RunMetrics` | 时长、目标/点位计数、有效/失败/Unknown 覆盖信息 | 结果列表摘要、统计候选 | 只投影原事实；Query 不计算质量指标或补缺失计数 |
| `Finding` | 功能/工具稳定 ID、预期值/观测值（若 Owner 允许）、结果代码、错误代码、位置/来源点引用、修订 | 异常追溯、按功能筛选 | 不把工具名称、点位文本或严重度当跨项目标准；缺陷判定留原 Owner |
| `EvidenceRef` | 不透明证据 ID、角色、内容 hash/修订、保持状态 | 从运行/异常明细跳转证据 | 不返回旧文件路径，不持有图像句柄；040/041 负责保持和读取 |
| `TraceEvent` | 与运行/异常关联的事件 ID、阶段、时间、来源修订、原因代码 | 追溯采集、保存、发布或恢复异常 | 不含登录令牌、MES 权限或设备命令；审计权限由 004/原 Owner 决定 |

同一 `RunId` 可有多个 `Finding` 和 `EvidenceRef`；Query 不能把展开行直接当板级总体。若来源只有条码/时间/拼板号，适配器必须声明“无法证明稳定身份”，固定分页、去重、历史重现和正式导出应拒绝或降级为实时非正式浏览，返回 `QRY_DATASET_REVISION_MISMATCH`/`QRY_SNAPSHOT_UNAVAILABLE`，不能悄悄拼接。

### 16.3 按板、时间和结果的条件语义

1. **按板/板组**：使用注册的 `BoardId` 或 `PanelId` 精确匹配；条码允许精确匹配、前缀或包含仅在字段目录分别登记时启用，保留前导零、大小写和空格规则。板组展开关系由 Owner 投影，Query 不从字符串拆分拼板号，也不把多个子板结果自动折算成一个板的 PASS/FAIL。
2. **按时间**：用户本地输入必须带区域 ID/规则修订并解析为 UTC `[start,end)`；查询响应EffectiveIntent保留UTC叶子，Operation.ObservedUtc记录观察时点。跨天/跨归档分段由 Projection/Snapshot适配内部的分段解析按事件时间与源代选择，不能依赖宿主机器的固定磁盘路径、程序启动目录或当前机器日期。
3. **按结果**：条件引用稳定结果代码或经 Owner 登记的组合分类。旧快照中的“检测 PASS + 复判 PASS”“检测 ERROR + 复判 ERROR”“检测 ERROR + 复判 PASS”只能作为迁移示例映射为组合谓词，不能在 Core 写死，也不能以筛选后的页面行重新命名总体或计算放行率。
4. **按功能/异常**：功能 ID、错误代码、位置引用和 `Finding` 修订必须来自目录；结果缺失、异常未关联或证据不可用保留 Unknown/Unavailable，不能被 `NotIn` 或空值语义误删。跨功能查询使用已登记组合投影，不允许 UI 临时 join。

### 16.4 历史分段合并与分页

历史存储可以按日、月、季度、设备或归档工件分段，但 分段解析/归并是IProjectionPort/ISnapshotPort适配实现的内部职责（不是新增公开IArchiveResolver），输出带来源身份/覆盖区间的注册投影。执行顺序为：

1. 用绝对 UTC 区间和字段能力向 resolver 请求候选分段；核覆盖是否闭合、是否存在重叠和缺口。
2. 对每个分段建立同一固定模式或明确实时模式；每行携带 `SourceId/SourceRevision` 和稳定 `RunId`。
3. 以完整排序键（例如检测时间、稳定 RunId、修订）做受控归并；重叠分段按 Owner 的修订/墓碑规则去重，不按枚举顺序或条码去重。
4. 仅在所有必需分段达到固定/封存保证时返回 `CompleteCoverage`；缺失或失效分段返回覆盖区间、`QRY_SNAPSHOT_UNAVAILABLE` 或 `QRY_DATASET_REVISION_MISMATCH`，不得显示“查询无结果”。
5. 游标绑定分段向量、源代、完整排序和锚值。UI 可以显示页码或“上一页/下一页”，Core 不实现无界 offset；跨分段的下一页仍使用同一 keyset 词典序。

本版不开放PartialCoverage成功响应；必需历史分段缺口整体拒绝并保留安全缺口原因键。已经合法交付的旧页保留历史事实，但后续停止，不声称完整历史。将来明确支持部分覆盖须先增加精确Coverage DTO/模式与验收，不能由adapter私下补字段。分段读取失败应保留已交付页和缺口事实，后续页停止或新建执行，不能默默跳过故障分段。

### 16.5 异常追溯链

异常追溯不是 Query 读取图像本身，而是返回可验证的关联链：

```
RunIdentity
  -> ResultState / Finding
  -> PositionRef / SourcePointRef
  -> EvidenceRef（040/041 保持与读取）
  -> TraceEvent（采集、保存、发布或恢复事件）
```

宿主从列表行进入明细任务流；Query Core 通过冻结的 `QueryAsync` 对应请求读取已注册的明细投影，并再次核当前授权和执行修订。需要图像、行图、点位原图或报告附件时只交给 040/041 的不透明 `EvidenceRef`。证据读取失败返回 `QRY_EVIDENCE_UNAVAILABLE`，保留异常代码、来源修订和失败原因，不以另一张图或当前最新图替换历史证据。明细查询不另增公开 API。

追溯结果至少区分：运行不存在、运行存在但无异常、异常存在但无证据、证据存在但当前不可读、来源修订冲突、历史覆盖不完整。Query 不领取复判任务、不提交人工结论、不改变原始结果、不发送 MES/设备命令。人工复判、质量放行和异常关闭由调用方/044 等 Owner 持有。

### 16.6 对旧实现的反例保护

以下旧行为只作为迁移验收反例：

- 旧代码用“总成条码 + 时间 + 图片拼版号”查明细；新适配器必须以稳定 `RunId`/修订和证据引用查询，条码/时间只能是条件。
- 旧代码把多个历史数据库文件读入 `DataTable` 后合并；新适配器必须返回分段覆盖和固定/实时保证，不能在客户端无限合并。
- 旧代码使用字符串拼接结果条件；新 Core 只接受 typed 结果代码/组合分类并参数化值，字段/算子由目录白名单映射。
- 旧代码从定位结果表删除/排除板后再统计定位失败；新 Query 只返回原 Owner 的覆盖状态和 `Finding`，不修改总体成员、不补分母。
- 旧代码点击 Grid 行后按文件路径读图；新 UI 只提交不可变行身份和 `EvidenceRef`，防止语言切换、刷新或归档迁移改变历史指向。

可判定接纳条件：同一固定快照内，板条件、UTC 时间条件和已登记结果组合返回相同 RunId 顺序；跨历史分段的覆盖/缺口可见；从一行追溯到 Finding 和 EvidenceRef 不依赖旧路径；异常证据缺失不会变成无异常；第二消费者可以替换结果代码集和用途而不修改 Core。

## 17. 第二轮场景驱动架构复审

查询层与数据落盘职责严格分开：Query 只通过已授权投影端口读取数据库拥有的结构化事实，通过证据/文件对象端口取得对象引用或有界流式内容；不得把图像、点云、高度场或视频搬进查询 DTO、临时数据库字段或大内存行结果。导出包含图像时按对象引用建立文件闭包，流式读取并单独应用预算/保持租约；结构化查询和文件对象丢失分别给出行事实状态与附件可用状态。第二消费者验收还应验证 Query 不持有数据库连接跨 UI 浏览期，慢查看器不会占满生产连接池，导出可取消且完成发布后才关闭来源 lease。

本节是实现前的反例门。每个场景都必须能从公开输入走到明确终态；“有行返回”“文件能打开”或“异常被捕获”都不是完成条件。参数只来自请求、已登记目录、授权上下文、快照能力或消费者 BudgetProfile；不能从数据库当前值、UI 默认值、操作者本机区域或私表推断。

| 场景 | 输入与参数来源 | 强制处理顺序 | 输出、状态与错误 | 恢复动作 | 可判定验收 |
|---|---|---|---|---|---|
| 正常固定查询 | 合法 Dataset/Revision、typed 条件、字段目录、授权上下文、`Consistency=Fixed`；页大小/期限来自 BudgetProfile | 限制请求 → 锁目录 → 规范化/hash → 授权 → 建立同一快照 → keyset 取 n+1 → 页守卫 → 返回 | typed 行、快照身份、hash、游标、计数性质；`Completed` | 用返回游标续页；不改页大小/排序 | 同一快照重复取页顺序与身份一致；资源释放事件出现一次 |
| 空输入/空集 | 空结果范围或已批准的全范围意图；禁止用空条件绕过目录/预算 | 先判断全范围意图是否被目录允许，再授权/预算；不建立无限快照 | 允许返回空页与 `Exact=0`；不伪造锚；`Completed` | 缩小/修正范围或结束执行 | `HasNext=false`，count=0 仅在同快照 exact 成立时出现；无扫描越权 |
| 部分成功 | 页面成功但可选count超时并已确认其reader归还，或某行证据引用缺失；字段/用途仍获授权 | 页读取与可选count隔离；计数reader未归还时整操作DrainUnknown不提前交付页；逐行保留原状态；证据缺失不得换缩略图 | 页面可 `Completed`，count=`NotComputed`/`Unavailable`；行带证据不可用状态；不得整体变空 | 宿主可稍后同快照重算 count，或重新查询；证据按 040/041 恢复 | 不把未完成 count 显示为 0；不发布缺证据的“完整包”；页身份不重复 |
| 歧义/错误输入 | 未知字段/算子、空逻辑组、`Eq(null)`、空 IN、反向区间、重复 DST、非有限数、未知协议版本、需迁移的已保存查询 | 字节/深度/集合上限 → 解析协议版本 → 字段/单位/null/时区校验 → 仅对已保存查询解析迁移版本；失败前不分配长资源 | 非法条件=`QRY_INVALID_CONDITION`；无效时间=`QRY_TIME_INVALID`；未登记字段/算子=`QRY_FIELD_UNSUPPORTED`/`QRY_OPERATOR_UNSUPPORTED`；不支持协议版本=`QRY_PROTOCOL_UNSUPPORTED`；已保存查询需迁移/迁移失败=`QRY_MIGRATION_REQUIRED`/`QRY_MIGRATION_FAILED`；状态为预检拒绝，不映射为通用执行 `Failed` | 指向安全的字段/节点与修复动作；原请求代次结束 | 没有查询、快照、count、文件或权限泄漏副作用；错误可本地化且不返回私表信息 |
| 超大/高并发 | 大字段/宽行、深页、超多组、并发超过 Profile、慢接收者 | 预检成本/并发/磁盘 → 排队有界 → 有界 reader/encoder 队列；不先宽扫再截断 | `QRY_BUDGET_EXCEEDED` 或 `QRY_CONCURRENCY_LIMIT`；`Failed`/`TimedOut`；不返回截断成功 | 缩小字段/范围、降低并发、重新执行；不提高模块硬上限 | 内存/队列/临时盘不超过 Profile；拒绝发生在长快照/大扫描前；无饥饿或无界排队 |
| 数据退化（噪声/遮挡/缺失） | 数据源返回损坏编码、类型不符、缺失字段、重复身份、证据对象不可读；Query 不接收图像算法输入 | 适配器校验行粒度/类型/修订 → 逐行核原状态 → 必需来源Missing/Unavailable/Invalid固定查询停止；合法Null/Unknown保留；禁止插值/猜值 | `QRY_DATA_QUALITY_DEGRADED` 或 `QRY_EVIDENCE_UNAVAILABLE`；原值/Unknown/缺失原因保留；固定总体不自动补齐 | 由原事实/证据 Owner 修复或重建投影；Query 可按同一快照重读，不能改事实 | 损坏行不变成 PASS/0；重复身份被拒绝或按已注册组合投影源规则去重而非Core猜测；统计消费者可区分缺测与未生产 |
| 取消/超时/原生排空 | 用户 token、宿主关闭、deadline、驱动 cancel 失败或 reader 仍忙 | 记录取消原因 → 停止新交付/入队 → 传播至 reader/encoder/writer → 等待实际结束 → 隔离未排空资源 | `Cancelling→Draining→Cancelled/TimedOut` 仅在真实归还后成立；未确认为非终态 `DrainUnknown` + `QRY_DRAIN_FAILED`，不报告资源已释放 | 继续排空或隔离连接；恢复必须新执行/原操作回执，不复用忙句柄 | 不回池忙连接；`ResourcesReleased` 只在适配器确认后出现；迟到页被旧代次丢弃 |
| 资源上限/磁盘满 | 单行/字段/字节、临时盘、快照 TTL、压缩缓冲或 evidence 保持超 Profile | 预检可测上限 → 运行中累计计量 → 达限先停新交付并隔离尾块 | `QRY_BUDGET_EXCEEDED` 或 `QRY_EXPORT_INCOMPLETE`；临时工件不可下载 | 缩小范围/字段、扩容后新执行；已持久完整块按检查点政策处理 | 未发布文件不出现在正式索引；没有静默截断、删除危险值或重置预算 |
| 保存/持久化/修订 | 已保存查询意图、旧目录修订、权限变化、相对日期模板、历史执行重现请求 | 当前授权 → 解析原版本 → 登记迁移器 → 报告差异 → 重新校验；历史重现核固定切面 | 可执行新修订或 `QRY_MIGRATION_FAILED`；旧 token/快照不继承 | 用户确认语义差异或修复字段；不可迁移条目保留但不可执行 | 删除字段/单位/null 变化不会静默删条件；模板与历史绝对区间不混用 |
| 升级/回退 | 新 Core/适配器/目录修订与正在运行的旧执行、导出、游标并存 | 停止新旧混写 → 排空旧 worker → 记录版本/源代 → 切换兼容包；旧执行按协议终止 | 旧 token/快照不跨不兼容主版本；发布未知仍可按原操作查询；状态可为 `Expired`/`Failed` | 保留上一可启动包、迁移器和清单；回退后新建执行，不篡改旧事实/文件 | 双版本不同时写同一事实；回退后资源归还、审计完整，已发布包 hash 不变 |
| 无 UI 调用 | 最小宿主注入 `IQueryService`；无 WPF Dispatcher | Root预约/注入 → Validate → QueryAsync/ExportAsync → QueryOperationAsync原ID → 终态后ReleaseExecutionAsync → CloseAsync有限观察/DisposeAsync原Task保留 | 与 UI 完全相同的行、hash、状态、错误和资源语义 | 由宿主依据 `RetryAdvice` 决定新执行；不得依赖控件初始化 | 移除 WPF/DevExpress 后仍可构建和运行；无订阅者也能完成 |
| 可选 UI | WPF 宿主传语言/主题/权限摘要；筛选改动产生新 RequestRevision | UI 草稿 → 调用 Core 校验 → 提交不可变请求 → 显示状态/覆盖/错误；UI 不读私表 | 显示无数据、无权、取消中、过期、未完成、发布未知等，不显示质量放行 | 重试、缩小范围、重新查询/导出；旧响应不能回填 | 1920x1080、三语、键盘/UIA 下文字不重叠；UI 与无 UI 校验一致 |
| 第二消费者 | 与第一消费者不同用途、字段、语言、并发/取消 Profile；仍走同一 Core | 仅替换用途/投影/适配器配置；核心校验、游标和授权路径不分叉 | 复判返回检索页；SPC/追溯返回固定成员/导出清单；无制程判定权 | 消费者处理自身流程/放行/设备动作；Query 只返回公开结果 | 两消费者无需修改核心；差异只在批准的 Contract/Profile，资源和缓存不串扰 |
| 长期运行/慢源 | 小块持续流、源迟到、快照将到期、连接重置、服务重启 | 心跳/进度 → TTL 与预算检查 → 可恢复点持久化 → 到期前停止或按协议恢复 | 可恢复导出返回检查点；不可恢复查询 `QRY_SNAPSHOT_EXPIRED`；不无限续租 | 同一封存/as-of 工件核 hash 后恢复；否则新执行 | 内存有界；重启不重复已确认块；总预算/授权期限不因重试重置 |

### 17.1 关键反例的逐步断言

1. **低 ID 晚提交**：A 分配 ID=101 未提交，B=102 提交。任何只以 `ID<=102` 或最大时间作为固定总体的适配器必须在准入阶段返回 `QRY_SNAPSHOT_UNAVAILABLE`；真快照中不得在后页突然出现 A。验收是固定页序与源代不变，而不是数量恰好相等。
2. **预读后撤权**：页守卫前预读的下一页不得交付；当前页已合法交付的字节不声称可召回。撤权事件后状态先进入 `Draining`，实际归还后才 `Revoked`，旧游标拒绝，UI 不以“无数据”替代。
3. **部分导出尾块**：只持久化完整块及摘要；半行、未关闭压缩容器和未核 hash 的尾块隔离。没有同一快照/封存能力时不得接续，必须新建导出。
4. **计数不是事实**：页面已成功而精确 count 超时，响应必须保留页并标 `NotComputed`；禁止把 count 失败变为 exact=0，也禁止用新快照补 count 后继续宣称同一总体。
5. **数据退化不是视觉判定**：Query 不对噪声、遮挡、模糊或缺失图像做清理、插值、OCR、缺陷判断。它只能传播原 Owner 的 `Unknown/Invalid/EvidenceUnavailable` 和修订；需要图像恢复时由视觉/证据模块另行处理。
6. **关联投影更新**：查询固定主数据修订与人工结果投影修订后，人工结果发生变化。原游标、计数和导出仍读取原切面；刷新建立新切面。原人工投影已不可用时拒绝原游标，不按最新值补齐。验收同时核字段值、版本向量和查询范围，不能仅核行数相同。

### 17.2 不支持能力与适配门

- 不支持任意 SQL、客户端表达式树、任意 join、全文脚本、动态正则、无限 offset、无边界导出、无授权的 count/hasNext、跨源未协调的“同一时刻”以及以当前表重建历史快照。
- 不支持用 Query 训练/推理模型，也没有备用视觉算法路线；本模块的备用路线只有另一个已登记的投影/快照/格式适配器，语义不能降低。需要模型训练、图像去噪、遮挡恢复或视觉算法时，必须转交对应视觉/AI 模块并由其定义 HALCON/AsunImage 路线、训练数据、回退和恢复条件。
- Core 的规范化、值比较、授权交付围栏、快照分支、排空及错误键由本页冻结；正式数据集/稳定键、受信授权适配、真实后端、证据闭包、消费程序和生产预算由宿主/领域 Owner 按本页端口绑定。它们只阻断实际适配/集成切片，不阻断独立 Core 和内存夹具。

## 18. HALCON、AsunImage 与研究依据

本模块是数据访问、权限、排序和编码能力；HALCON 算子不适用于查询、事务隔离、分页、授权或导出编码，因此本功能记录为“不适用”。第二轮复审核对了项目入口指定的 `halcon算子手册/operators/index.html`（标题标示 HALCON Operator Reference `26.05.0.0`）及代表性 `query_data_code_2d_params.html` 页面；该算子查询的是视觉数据码模型参数，不能为 Query 的数据目录、权限或导出提供实现路线。`ImageLibDotNet` 仅作为其它视觉模块的公共适配边界，本模块不调用其视觉句柄，也不把 `HObject`/`HTuple` 放入 Query 契约。涉及图像/证据读取时，只能通过 040/041 公开端口；不扫描、修改或猜测 AsunImage 内部 API。若未来增加图像元数据筛选，由原视觉 Owner 生成公开元数据并注册投影字段/算子，不能在 Query 中加入视觉算法。

PKG-042 的定向研究依据包括 PostgreSQL 18 事务/快照/排序/快照同步、.NET 10 `TimeZoneInfo` DST 语义、Npgsql 参数/SequentialAccess 与取消测试、MR.EntityFrameworkCore.KeysetPagination（锁定 commit `84fd37923e35db4a23244e40189fd42efb60caf6`）以及 CsvHelper（锁定 commit `7dbb3fe710466ec2f573f81e19c7130ec1c7a365`）和 OWASP CSV Injection。它们只支持设计取舍，不替代本模块选定后端、真实消费程序、WPF、性能、恢复或生产验收。[`AsunControl` 只读快照](../../references/project-snapshots/AsunControl/20261004/original) 检查未发现受控查询/流式导出实现；Vision_DataCode 的引擎/UI 分离形态不能作为 Query API、数据事实或导出安全证据。

2026-10-06 只读核对 `H:\docs\40-development\60-data\数据服务与证据追溯开发指导.md`（`DEV-DAT-001`，标示版本 2.8；SHA-256 `ce03205a54dad3821159fedf84d31e70ab6235446725a890cfa5f93994c7a8c6`），与[全量来源清单](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)一致。本会话此前完成冻结 API 一致性及 DZ-XVision 有限来源审查，本次仅补查询增量：来源 §11/§11.2/§11.9 的稀疏授权分页、历史字段来源区分和关联投影固定版本落入 §3.2/§4/§5；§2/§11 的导出实际范围及独占临时文件/不覆盖发布落入 §3.5/§9；反例沿用 §12/§17 验收矩阵。现有 typed 条件、UTC 半开区间、keyset、撤权、计数、流式预算、Unknown 和原操作恢复已覆盖，未重复扩写。

该来源中的 AOI 提交、容量预约、人工复判写入、FinalDisposition、RouteAuthorization、Outbox、Retention/GC、远程部署和像素解码不属于 query 实施范围；不迁入其私有 DTO/API、协议域、特定数据库/签名算法、固定数量/字节限额、任务记录或测试通过声明。来源的最大 JournalSequence/高水位仅是其存储实现线索，不能替代 §5.2 的真实快照/封闭性证明；生成段落的通用命令/CAS/replay 模板也不覆盖本页冻结 API 或纯读取语义。本次未采用视觉方法，HALCON 路线不适用，未读取 AsunImage 内部。2026-10-06增量未新增API；本轮v0.2闭合Core类型/端口但不新增产品事实Owner，真实映射/发布适配按§19逐切片接收。


### 18.1 本轮沿用的实际来源与设计落点

以下源码/测试在暂停前已按固定commit阅读，本轮直接沿用；未重复下载/全审。产品实现依赖仍是BCL Core+注入适配，不自动引入这些第三方库。来源license记录仅作可追溯元数据，不对AsunImage/DevExpress重新做准入核验。

| 官方/固定来源 | 实读位置、版本/依赖/许可 | 采纳及局限 |
|---|---|---|
| [PostgreSQL 18 isolation](https://www.postgresql.org/docs/18/transaction-iso.html)、[ORDER BY](https://www.postgresql.org/docs/18/queries-order.html) | 18版官方事务隔离与每列方向/null规则；资料，不复制代码 | §5/§B.2：Repeatable Read提供有限事务视图，Read Committed不可固定多页；长期路线as-of/封存，词典序分列比较，不拿事务教程证明跨源资格 |
| [.NET Channels](https://learn.microsoft.com/en-us/dotnet/core/extensions/channels) | 官方bounded channel/FullMode；框架API不另加包 | §8/§B.2：Wait背压，不Drop；Channel容量仍需独立字节计量，API本身不证明native排空 |
| [Keyset固定源码](https://github.com/mrahhal/MR.EntityFrameworkCore.KeysetPagination/tree/84fd37923e35db4a23244e40189fd42efb60caf6) | KeysetFilterPredicateStrategy.cs混方向词典序、KeysetPaginationTest.cs Forward/Backward/空反向与offset对照；Directory.Build.props net10.0/EF Core10.0.0；LICENSE.txt MIT。commit是版本权威，不把未核标签当版本 | §5.1/§12：借排序与反向测试思想；不引EF Core依赖到Core，不用该测试证明null/授权/固定源/恢复 |
| [CsvHelper固定源码](https://github.com/JoshClose/CsvHelper/tree/7dbb3fe710466ec2f573f81e19c7130ec1c7a365) | CsvWriter.cs Trim/Injection修改原值、DisposeAsync flush；tests/Async/WritingTests.cs WriteRecordsTestCanceled异常包装取消；csproj net8/7/6/netstandard多目标及兼容依赖；LICENSE MS-PL OR Apache-2.0 | §9：未经Profile批准拒绝风险CSV、不Strip，适配器处理取消包装并追实际Task；flush返回不自动等价完整发布。InjectionTests.cs原尝试路径404，未声称阅读其测试 |
| [Npgsql 10.0.3固定资料](https://github.com/npgsql/npgsql/tree/d3768398c17877b3a916c3c4d87e8e11698991fc) | 沿用REF-002已固定公共参数/SequentialAccess/取消源码与测试；本轮未重复全审 | 真实Adapter按参数化/顺序读取/取消验证；数据库连接、snapshot和性能资格不能由上游测试替代 |
| [.NET 10 FileStream.Flush](https://learn.microsoft.com/en-us/dotnet/api/system.io.filestream.flush?view=net-10.0)、[Directory.Move](https://learn.microsoft.com/en-us/dotnet/api/system.io.directory.move?view=net-10.0) | 已读Flush(Boolean)落OS缓冲与Move跨卷/目标存在约束 | C.3/C.5先flush、同卷不覆盖rename；不据API推断介质断电耐久或服务端commit结论 |
| [.NET 10 Utf8JsonWriter](https://learn.microsoft.com/en-us/dotnet/api/system.text.json.utf8jsonwriter?view=net-10.0)、[RandomNumberGenerator.Fill](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.randomnumbergenerator.fill?view=net-10.0)、[Convert.ToBase64String](https://learn.microsoft.com/en-us/dotnet/api/system.convert.tobase64string?view=net-10.0) | 已读官方.NET10显式JSON写入和BCL随机字节/Base64签名；不落新参考副本 | C.2.1/C.4使用有限句柄及固定JSON协议；API不证明授权/资源与耐久资格 |
| [PostgreSQL 18 partitioning](https://www.postgresql.org/docs/18/ddl-partitioning.html) | 已读18版官方分区/pruning说明 | C.2固定封存段/必要UTC参数；须真实EXPLAIN与等价验证，不以官方教程声称客户性能达标 |
| 本机DevExpress流式XLSX/动态Binding官方XML | Components/Bin/NetCore/DevExpress.Printing.v25.2.Core.xml与DevExpress.Xpf.Grid.v25.2.Core.xml；XlExport.CreateExporter、IXlExporter.CreateDocument(Stream)、CreateSheet/Row/Cell、XlVariantValue.TextValue、ColumnBase.Binding及AutoGenerateColumnsMode.None实际签名/枚举已读 | C.4/C.6复用安装25.2.3接点，不用BeginExport/FromObject，不猜FieldId反射路径；真实.NET10编译/容器/DPI/WPF仍未执行 |
| 本机DevExpress25.2.3官方XML | C:/Program Files/DevExpress 25.2/Components/Offline Packages/下25.2.3/lib/net8.0-windows；DockLayoutManager/LayoutGroup/LayoutPanel、GridControl.View/DataControlBase.ItemsSource、TableView、TreeListView.KeyFieldName/ParentFieldName、DataViewBase.AllowSorting/AllowColumnFiltering、PropertyGridControl.SelectedObject、SuperTip/SuperTipItem实际签名已读 | §10使用已确认接点，在线API页403且无dxdocs/匹配WPF skill，未把403当API不存在。Flyout/FilterEditor未确认，本版不用。net8.0-windows是安装包资料路径，不改变平台net10.0-windows或25.2.3；真实WPF运行尚未执行 |

## 19. 实施前置、开放项与自审门

本轮完整批准范围内部设计按附录B/C闭合：条件/分页/聚合、保存/迁移、数据库与持久CAS装配、游标、普通/聚合/附件三格式导出、硬盘恢复、可选WPF任务/草稿/动态列和三语资源均有唯一实施接点、失败/恢复与验收断言。内部软件路线不再作为“后续Owner决定”开放项；内容审核和修复在本永久原会话完成，不等待总控代做模块内容复核。

真实外门如下，未采纳项仅阻断其消费者/运行切片：

| 外门事实/验收 | 原权威及具体输入 | 阻断范围 |
|---|---|---|
| 生产字段/粒度/成员/稳定键与历史来源 | 复判/SPC/追溯事实Owner采纳Dataset/FieldDescriptor、sealed Cut/source vector、SortVariant/固定StatementCatalog及真实代表输入 | 该投影注册/真实查询，不阻断通用Core和适配codec实现 |
| 当前授权/撤权/审计 | 授权与审计Owner提供Policy修订、受信context/逐行归属、CommitDelivery线性化及原审计回执 | 生产数据交付，不把角色名或缓存视为授权 |
| 真实封存保留与附件闭包 | 事实/证据Owner确认源保持屏障、精确ObjectRef→SourceRef/Role/长度/ContentSha256与retention资格 | 固定生产读取/带原件导出；无附件普通能力独立验证 |
| 保存迁移的领域语义映射 | 原字段/单位/枚举Owner批准有限版本映射和SemanticChanges差异 | 该生产迁移，不阻断通用Save/Load/CAS/差异机制 |
| 客户负载/消费/目标 | Host/客户提供ConsumerId/版本、批准Target根/ACL/同卷介质、BudgetProfile、规模/TTL/保留与SLA来源 | 对应容量/性能/文件系统与消费资格，缺值仍TargetPending |
| 真实运行与交付基线 | 授权实现任务绑定代码仓库/分支，再按§12/§13/C.7执行.NET10、IM-066/真实PG、磁盘故障恢复、1920×1080 WPF三语/UIA与双消费者验收 | 实施/运行/生产资格；本次文档不造构建或测试成绩 |

本轮未创建产品工程或测试工程，不修改其它模块/共享文件；上述外门不能由query编造，但也不再要求他人补做query内部软件设计。

包 Owner 自审必须逐项回答：

- 是否能在无 UI、无产品 Shell、无数据库私表和无全局状态下执行？
- 是否所有输入都有类型、单位、范围、默认、版本、空值和错误语义？
- 是否每页/块/完整发布都通过当前授权守卫，且撤权竞态有可证明边界？
- 是否固定总体使用真正快照/封存能力，而非 max ID、Grid 行或实时拼接？
- 是否取消、超时、断连、未知回执和资源未排空均有终态与恢复动作？
- 是否导出原值、公式风险、null/空串、精度、时区和完整清单可核验？
- 是否复判与 SPC/追溯两个消费者无需修改核心即可接入？
- 是否明确哪些验证尚未运行，未把合成、Mock、上游测试或截图称为生产通过？

2026-10-10主控已回读接收Q-C1～Q-C4六项规格，四切片同步 `ModuleCoreImplementationReady`（仅规格）。模块阶段仍为 `DesignReview/Prep`；U1指导内容已主控接收（2026-10-10），真实WPF/后端/产品资格未关闭，真实DB/硬盘恢复/WPF/产品门继续 `PreparationIncomplete / NotReady`。未执行代码构建、测试或性能测量，不提升ImplementationSpecificationReady、Implemented、ProductionValidated或客户交付资格。

2026-10-12原会话完成本轮完整批准范围的两条消费路径自审与修复：明确Core共享保存授权扩展、IM-066完整技术信封摘要与query输入摘要的分工、有界私有恢复日志及Unknown不重发、候选全字段读取后Core最终投影、聚合源排序、单一bundle发布事实、独立检查点文件序号及原预算恢复、三格式字节规则与WPF三语接点。复用现有validate_docs.targets并对唯一指导执行定向检查，本地链接、标题唯一性、代码围栏、Markdown表列数、公开类型声明重复、错误码声明、UTF-8/CRLF和既有四切片仅规格状态均通过。文档范围收口完成；新增附录C范围不追溯为旧六门接收，真实外门按本节保留。本次未创建工程，未执行C#编译、正式测试、DB/磁盘故障恢复或WPF运行验证，不启动实现。
## 附录 B：Module API Contract v0.2（唯一 Core 类型与接点）

v0.2取代原v0.1的仅名称接口；本节是模块技术决定，未创建程序集、未执行编译。产品 Contract/Schema 映射不得改变这里的错误与资源语义。所有下列类型归 `Asun.Modules.Query`，使用 .NET 10 的 `System.Collections.Immutable`/`TimeProvider`，Core 不引用 WPF、ORM、数据库驱动、DevExpress 或 AsunImage。代码形状不省略被引用的模块类型；标量编码和组合有效域由正文及下表约束。

### B.1 不可变请求、返回和状态

```csharp
using System.Collections.Immutable;
namespace Asun.Modules.Query;

public enum ValueKind { Text, EnumCode, Boolean, Int64, UInt64, Decimal, UtcTicks, Guid }
public enum ValueState { Known, Null, Unknown, Missing, Unavailable, Invalid }
public enum LogicKind { And, Or }
public enum CompareOp {
    Eq, NotEq, Lt, Le, Gt, Ge, In, NotIn,
    StartsWith, Contains, IsNull, IsNotNull, IsUnknown
}
public enum Direction { Asc, Desc }
public enum NullOrder { First, Last }
public enum Consistency { Fixed, Realtime }
public enum CountMode { None, Exact, Estimate }
public enum CountKind { Exact, Estimate, NotComputed, Unavailable }
public enum AggregateKind { CountRows, CountKnown, Sum, Average, Min, Max }
public enum AggregatePolicy { None, Default, ExactFraction, AverageDecimalToEvenV1 }
public enum OperationState {
    Rejected, Accepted, Running, Cancelling, Draining, DrainUnknown,
    AwaitingReceipt, Completed, Cancelled, TimedOut, Failed, Revoked, Expired
}
public enum PublishState { NotPublished, Published, Unknown }
public enum ServiceState { Open, Closing, Closed }
public enum RetryAdvice { None, CorrectInput, NewQuery, QueryOriginal, WaitDrain }
public enum EventKind {
    Rejected, Accepted, Authorized, SnapshotOpened, Started, Progress,
    PageReady, EncodingStarted, ManifestVerified, PublishRequested,
    PublishObserved, Draining, DrainUnknown, Drained, ResourcesReleased,
    AwaitingReceipt, Terminal
}
public enum ExportScope { AllMatching, ExplicitMembers, CurrentPage }
public enum ExportFormat { TypedJsonLines, Csv, Xlsx }
public enum IntentOutcome { Saved, Loaded, Migrated, Rejected, Conflict, Unknown }
public enum StringComparisonRule { Ordinal, OrdinalIgnoreCase }

public sealed record VersionRef(string Id, string Revision, string Sha256);
public sealed record SourceRef(string Namespace, string Id, string Revision, string Sha256);
public sealed record QueryIdentity(string SubjectId, string TenantId, string ScopeId,
    string SessionId, string Purpose, long RequestRevision);
public sealed record Scalar(ValueKind Kind, string Canonical);
public sealed record Cell(string FieldId, ValueState State, Scalar? Value, string? ReasonKey);
public sealed record QueryRow(SourceRef Identity, ImmutableArray<Cell> Cells,
    ImmutableArray<Cell> SortKey, ImmutableArray<SourceRef> Evidence);
public abstract record ConditionNode;
public sealed record LogicNode(LogicKind Logic, ImmutableArray<ConditionNode> Children)
    : ConditionNode;
public sealed record LeafNode(string FieldId, CompareOp Operator,
    ImmutableArray<Scalar> Values) : ConditionNode;
public sealed record SortTerm(string FieldId, Direction Direction, NullOrder NullOrder);
public sealed record AggregateSpec(string OutputId, AggregateKind Kind, string? FieldId,
    AggregatePolicy Policy = AggregatePolicy.Default);
public sealed record QueryIntent(VersionRef Dataset, ImmutableArray<string> Fields,
    ConditionNode? Condition, bool AllRangeConfirmed, ImmutableArray<SortTerm> Sort,
    ImmutableArray<string> GroupBy, ImmutableArray<AggregateSpec> Aggregates,
    Consistency Consistency, CountMode CountMode, int PageSize);
public sealed record QueryBudget(VersionRef Profile, DateTimeOffset DeadlineUtc,
    TimeSpan QueueWait, TimeSpan StatementTimeout, TimeSpan SnapshotTtl,
    TimeSpan SnapshotIdle, TimeSpan DrainObservation, long MaxScanRows,
    long MaxRows, long MaxBytes, int MaxGroups, long MaxTemporaryBytes);
public sealed record SnapshotRef(string ExecutionId, string Handle, string SemanticHash,
    ImmutableArray<VersionRef> Sources, VersionRef AuthorizationPolicy, DateTimeOffset ExpiresUtc);
public sealed record QueryRequest(int ProtocolVersion, Guid RequestId,
    QueryIdentity Identity, QueryIntent Intent, QueryBudget Budget,
    SnapshotRef? Snapshot, string? Cursor);
public sealed record QueryError(string Code, string? FieldPath, RetryAdvice Retry,
    ImmutableDictionary<string, string> SafeArguments);
public sealed record QueryValidation(bool IsValid, string? SemanticHash,
    ImmutableArray<QueryError> Errors);
public sealed record CountResult(CountKind Kind, long? Value,
    string? SnapshotHash, decimal? RelativeError, string? ReasonKey);
public sealed record ExactFraction(string Numerator, string Denominator);
public sealed record DecimalProjection(string Canonical, int Scale, bool IsExact,
    string PolicyId);
public sealed record AggregateValue(string OutputId, ValueState State, Scalar? Value,
    ExactFraction? Exact, DecimalProjection? Projection,
    long ValidCount, long MissingCount, string? ReasonKey);
public sealed record AggregateRow(ImmutableArray<Cell> Group,
    ImmutableArray<AggregateValue> Values);
public sealed record OperationStatus(string OperationId, string? ExecutionId,
    OperationState State, PublishState Publish, bool ResourcesReleased,
    long Sequence, QueryError? Error, DateTimeOffset ObservedUtc, string? ReceiptId);
public sealed record OperationObservation(OperationStatus Status, ExportManifest? Manifest,
    QueryResult? Page, IntentResult? Intent);
public sealed record QueryResult(OperationStatus Operation, SnapshotRef? Snapshot,
    string? SemanticHash, QueryIntent? EffectiveIntent,
    ImmutableArray<FieldDescriptor> FieldDescriptors, ImmutableArray<QueryRow> Rows,
    string? NextCursor, string? PreviousCursor, bool? HasNext, bool? HasPrevious,
    CountResult Count, ImmutableArray<AggregateRow> AggregateRows);
public sealed record ExportProfile(VersionRef Version, ExportFormat Format,
    string Encoding, string NullMarker, string EmptyMarker, string TimeZoneId,
    string ConsumerId, bool RejectFormulaRisk, bool IncludeEvidenceBytes);
public sealed record ExportRequest(int ProtocolVersion, Guid RequestId,
    string OperationId, QueryRequest Query, ExportScope Scope, string? PageOperationId,
    ImmutableArray<SourceRef> Members, ExportProfile Format, string TargetId);
public sealed record ExportObject(SourceRef Identity, string Role, long LengthBytes,
    string Sha256, bool ContainsBytes);
public sealed record ExportManifest(string SemanticHash, SnapshotRef Snapshot,
    ImmutableArray<string> Fields, ImmutableArray<ExportObject> Objects,
    long Rows, long ContentBytes, string ContentSha256, VersionRef Format,
    ImmutableArray<string> Omissions, string? ReceiptId);
public sealed record ExportResult(OperationStatus Operation, ExportManifest? Manifest);
public sealed record QueryEvent(string OperationId, string? ExecutionId,
    long RequestRevision, long Sequence, DateTimeOffset Utc,
    EventKind Kind, long Rows, long Bytes, QueryError? Error);
public sealed record ExecutionRelease(string ExecutionId, bool Released,
    OperationStatus Status);
public sealed record CloseResult(ServiceState State, int ActiveOperations,
    int ActiveSnapshots, bool ResourcesReleased, ImmutableArray<string> UnknownOperations);

public interface IQueryService : IAsyncDisposable {
    QueryValidation Validate(QueryRequest request);
    ValueTask<QueryResult> QueryAsync(QueryRequest request, CancellationToken cancellationToken);
    ValueTask<ExportResult> ExportAsync(ExportRequest request, CancellationToken cancellationToken);
    ValueTask<OperationObservation> QueryOperationAsync(string operationId, CancellationToken cancellationToken);
    ValueTask<ExecutionRelease> ReleaseExecutionAsync(string executionId, CancellationToken cancellationToken);
    ValueTask<CloseResult> CloseAsync(CancellationToken waitCancellationToken);
}
```

- 默认 `ImmutableArray`（IsDefault）、null 集合/元素、未定义枚举、空 ID、格式非法 SHA-256 均拒绝，不能当空集合；合法空集合仅允许在明确可选位置。所有公开值仅含密封 record、string 和 ImmutableArray/ImmutableDictionary；只接受 B.1 的两种密封 AST 子类，拒绝未知子类。先在原输入上有界校验，后构造模块自有规范树/目录，不能先递归复制/hash 再检查限额。string 和标量不重复复制；数组不得通过 ImmutableCollectionsMarshal 的可变后门交给模块。传输层在构造 DTO 前限制原始输入字节；Core 不承担调用方已分配的无限字符串。
- `VersionRef` 三字段必需；ID/Revision 各 1..128 UTF-8 字节，Sha256 为 64 位小写 hex。`SourceRef` 命名空间/稳定 ID/修订/hash 全部必需，标识相同但修订/hash 冲突不是同一对象；不能按相同内容 hash 合并不同身份。`Identity` 各 ID 和 Purpose 必填，RequestRevision 为非负单调代次；构造的 trustedIdentity 由受信 Host 提供；每请求 Subject/Tenant/Scope/Session/Purpose 必须逐字段 Ordinal 相等，仅 RequestRevision 可变。回查/释放/关闭使用同实例身份；不靠 AsyncLocal、线程身份或全局当前用户。目录/授权适配仍验证此身份。
- `Scalar.Canonical`：Text/EnumCode 是原字符串；Boolean 只为 `true/false`；Int64/UInt64 是无前导零的十进制（0 唯一，禁止 -0），Decimal输入为≤64B、非指数的十进制形式（1.0/1.00允许Normalize成1）；先按数字系数/scale验证能精确表示.NET decimal，再去尾零。不能用TryParse隐式舍入过长小数，UtcTicks 为 UTC .NET ticks（100 ns）的非负十进制，Guid 为小写 D 格式。禁止 double、当前 Culture 格式和不受限 object；单位由字段目录固定。Cell Known 必须有匹配 Scalar、ReasonKey=null；其它状态 Value=null，Unknown/Missing/Unavailable/Invalid 必须有稳定原因键。Null 单独表示事实 null，不能承载 DBNull。
- `QueryIntent` 字段上限见 §3，GroupBy/Aggregates 为空表示不请求；null Condition 仅在 AllRangeConfirmed=true 且目录 AllowAllRange=true 时允许。一个 Leaf 的 IsNull/IsNotNull/IsUnknown 必须零 Values，In/NotIn 为 1..256 个同类型值，其它运算恰好一值；重复 IN 值规范化去重但仍先按原字节/元素预算预检。
- `QueryBudget` 所有上限为正且有限，SnapshotIdle≤SnapshotTtl，QueueWait/StatementTimeout受Profile上限；每个实际等待采用min(配置时长,原deadline剩余)，不改变预算/hash。清理观察采用独立DrainObservation，不再受已过业务deadline影响；MaxScanRows≥MaxRows，MaxGroups≥1。截止时间不能放进 CancellationToken，也不因重试续期。超过入场 deadline 为 `QRY_TIMEOUT` 拒绝，不调用源端口。Culture 只由宿主资源/显示层控制，不是查询意图或 hash 输入。
- Cursor=null 是首页，空字符串为无效；续页必须带 Snapshot 且精确匹配 ExecutionId/handle/semanticHash/source vector；Fixed 的 Snapshot 至少一来源，不能由调用方生成有效句柄。Realtime也返回可复查的不可变源观察上下文；若后端无法在释放reader后恢复观察点，则该分支HasNext/HasPrevious=null，不签发续页游标。支持实时keyset的适配必须保持有限源上下文lease至TTL/Release，明确页间可能变化；不可用于固定导出。上一页/下一页方向封在游标内，调用方不能改锚。
- QueryResult 的 Rows 按 Fields 顺序返回唯一字段 Cell，Count 只在 Exact/Estimate 有 Value；HasNext/HasPrevious=null 表示未证明，不能显示“最后一页”。成功普通页的 Operation=Completed、ResourcesReleased=true；失败/拒绝/DrainUnknown 不返回行或游标。聚合页只填 AggregateRows，Rows为空，稳定键为规范化Group全元组，禁止用组ordinal续页。AggregateValue.State=Known时，Sum/Min/Max使用Value；Average使用Exact（分子/分母）并按Policy选择可选Projection，Projection的Canonical/Scale/IsExact/PolicyId必须原样返回；State=Null时这些值均为空。Count表示匹配源行数，不能用它代替组数。
- ExportRequest.OperationId 是调用方在副作用前生成的 UUID D 字符串，服务在同权限作用域注册并由 OperationStore 持久锁定请求 hash；同 ID 同 hash 读原状态/回执，同 ID 异 hash `QRY_OPERATION_CONFLICT`。当前页/成员导出的 Members 非空、唯一且全部绑定原 Snapshot；AllMatching 的 Members 必须空且PageOperationId=null。CurrentPage须PageOperationId为原已完成页操作，Core读OperationStore核Identity/semanticHash/snapshot与完整已交付Members精确相等；不能把调用方自报集合当原页。ExplicitMembers须PageOperationId=null，Core在同快照核每成员精确修订/hash、当前授权及原predicate；任一缺失/冲突整体拒绝，不静默少导出。目标仅 TargetId，由宿主批准的适配器解析，Core 不接受任意本地路径/SQL。
- PublishAsync 接收的待发布 Manifest.ReceiptId=null；canonical 清单排除 ReceiptId 和自身 hash，签发回执绑定清单摘要，避免循环。公开 ExportResult.Manifest 只在已确认 Published 且原回执核验时填 ReceiptId；Unknown 可在 OperationStore 保留待发布清单，不能作为可下载完成结果。导出大小含清单/编码/附件，所有累加 checked；估计/缺口/不完整不能隐式升为全量包。TypedJsonLines 为 Core 工程与机器消费主格式，CSV/XLSX 是经 Profile 批准的格式适配；不静默互换。
- `QueryOperationAsync` 包括查询、导出和保存操作；ReleaseExecutionAsync通过其ExecutionRelease返回状态，内部释放操作ID同样可回查；必须核当前主体/租户/用途，跨主体或权限不可用都不能降为 NotFound。QueryAsync 操作 ID 是 RequestId 小写 D，不能与导出/保存已有 ID 碰撞；查询同 RequestId 同请求只在原状态保留期内复用，同 ID 异 hash 拒绝。服务已 Closing 时拒绝新读写、仍允许本实例回查与关闭等待；Closed后必须借新实例+同持久Store回查导出/保存。OperationObservation.Status是唯一状态，已核回执时附原Manifest/Page/Intent；Unknown时不附完成载荷。恢复实例可用当前新Session，但须同Subject/Tenant/Scope/Purpose且经Recover动作授权；Session不能变更原operation hash，回查不重新提交旧请求。跨Subject明确拒绝，不以NotFound掩盖。
- 结构错误用返回的 QueryError，端口异常边界用 §7.3 稳定键，不透传 SQL/路径/secret；OperationCanceledException 不能直接跳出已取得资源的生命周期。CloseAsync 的 token 仅取消等待，返回 Closing/未排空（不抛“已关闭”）；DisposeAsync 无 token，等待同一关闭任务，不能同步阻塞或强杀。多次关闭/释放复用同任务。终态不可逆，唯一 Terminal 每操作一次；AwaitingReceipt/DrainUnknown 均非终态。

### B.2 目录、依赖端口及构造

下列端口为本模块公开接入点；§2 表是责任解释，不再允许另造同义接口。端口必须提供 typed 回执或抛出 `QueryPortException`；错误码、实际副作用状态和资源仍须 Core 接收。借用的端口不由 Core Dispose；每次返回的 reader、快照或工件 lease 由 Core 独占，实际归还后才能发 ResourcesReleased。

```csharp
public sealed record FieldDescriptor(string Id, ValueKind Kind, string Unit,
    bool Nullable, bool Filterable, bool Sortable, bool Projectable,
    bool Groupable, int MaxUtf8Bytes, StringComparisonRule TextComparison,
    ImmutableArray<CompareOp> Operators);
public sealed record BudgetDescriptor(VersionRef Version, TimeSpan MaxDuration,
    TimeSpan MaxQueueWait, TimeSpan MaxStatementTimeout, TimeSpan MaxSnapshotTtl,
    TimeSpan MaxSnapshotIdle, TimeSpan MaxDrainObservation,
    long MaxScanRows, long MaxRows, long MaxBytes, int MaxGroups, long MaxTemporaryBytes);
public sealed record DatasetDescriptor(VersionRef Version, string RowGrain,
    string StableKeyField, bool AllowAllRange, ImmutableArray<FieldDescriptor> Fields,
    ImmutableArray<SortTerm> DefaultSort, ImmutableArray<BudgetDescriptor> BudgetProfiles);
public sealed record QueryCatalog(VersionRef Version,
    ImmutableArray<DatasetDescriptor> Datasets, ImmutableArray<ExportProfile> Formats);
public sealed record QueryHostOptions(int MaxConcurrentOperations, int MaxQueuedOperations,
    int MaxSnapshots, int QueueBlocks, long QueueBytes,
    int MaxOperationRecords, TimeSpan OperationRecordTtl);
public sealed record QueryTarget(QueryIdentity Identity, string Action,
    VersionRef? Dataset, string? SemanticHash, SourceRef? Row,
    ImmutableArray<string> Fields, ImmutableArray<SourceRef> Members);
public sealed record AuthorizationDecision(bool Allowed, VersionRef Policy,
    DateTimeOffset ExpiresUtc, string GuardId, QueryError? Error);
public interface IAuthorizationPort {
    ValueTask<AuthorizationDecision> CheckAsync(QueryTarget target, CancellationToken ct);
    ValueTask<bool> CommitDeliveryAsync(string guardId, QueryTarget target,
        string contentHash, CancellationToken ct);
}
public interface ICatalogPort {
    QueryCatalog Snapshot { get; }
    ValueTask<bool> IsCurrentAsync(VersionRef catalog, CancellationToken ct);
}
public sealed record SnapshotOpen(QueryRequest Request, string SemanticHash,
    AuthorizationDecision Authorization);
public interface ISnapshotLease : IAsyncDisposable {
    SnapshotRef Reference { get; }
}
public interface ISnapshotPort {
    ValueTask<ISnapshotLease> OpenAsync(SnapshotOpen request, CancellationToken ct);
}
public sealed record ProjectionRead(QueryIntent Intent, SnapshotRef Snapshot,
    QueryTarget Target, AuthorizationDecision Authorization,
    ImmutableArray<Cell> Anchor, bool Backward, long ScanLimit,
    DateTimeOffset DeadlineUtc);
public interface IProjectionReader : IAsyncDisposable {
    IAsyncEnumerable<QueryRow> ReadAsync(CancellationToken ct);
    long ScannedRows { get; }
    bool EndOfSource { get; }
}
public interface IProjectionPort {
    ValueTask<IProjectionReader> OpenAsync(ProjectionRead request, CancellationToken ct);
}
public sealed record CursorBinding(QueryRequest Request, SnapshotRef Snapshot,
    ImmutableArray<Cell> Anchor, bool Backward, DateTimeOffset ExpiresUtc);
public sealed record CursorDecoded(CursorBinding? Binding, QueryError? Error);
public interface ICursorPort {
    string Protect(CursorBinding binding);
    CursorDecoded Unprotect(string token);
}
public sealed record EvidenceClosure(ImmutableArray<SourceRef> Members,
    SnapshotRef Snapshot, DateTimeOffset ExpiresUtc);
public interface IEvidenceLease : IAsyncDisposable {
    EvidenceClosure Closure { get; }
    IAsyncEnumerable<ReadOnlyMemory<byte>> ReadAsync(SourceRef evidence, CancellationToken ct);
}
public interface IEvidenceRetentionPort {
    ValueTask<IEvidenceLease> AcquireAsync(EvidenceClosure closure, CancellationToken ct);
}
public sealed record EncodedBlock(ReadOnlyMemory<byte> Bytes, long CompleteRows,
    ImmutableArray<Cell> LastKey, bool FinalBlock);
public interface IFormatAdapter {
    ExportFormat Format { get; }
    IAsyncEnumerable<EncodedBlock> EncodeAsync(
        IAsyncEnumerable<QueryRow> rows, ExportProfile profile, CancellationToken ct);
}
public sealed record ExportBinding(ExportRequest Request, string RequestHash,
    SnapshotRef Snapshot);
public sealed record PublishReceipt(PublishState State, string? ReceiptId,
    string? ManifestSha256, QueryError? Error);
public sealed record ExportCheckpoint(string OperationId, string RequestHash,
    SnapshotRef Snapshot, VersionRef Format, ImmutableArray<Cell> LastKey,
    long Rows, long Bytes, long ScannedRows, string PrefixSha256,
    ImmutableArray<ExportObject> CompletedObjects, DateTimeOffset OriginalDeadlineUtc);
public interface IExportLease : IAsyncDisposable {
    ExportCheckpoint? Checkpoint { get; }
    ValueTask WriteAsync(ReadOnlyMemory<byte> block, CancellationToken ct);
    ValueTask CheckpointAsync(ExportCheckpoint checkpoint, CancellationToken ct);
    ValueTask<PublishReceipt> PublishAsync(ExportManifest manifest, CancellationToken ct);
}
public interface IExportTargetPort {
    ValueTask<IExportLease> CreateAsync(ExportBinding binding, CancellationToken ct);
    ValueTask<PublishReceipt> QueryReceiptAsync(string operationId, QueryIdentity caller, CancellationToken ct);
}
public sealed record OperationRecord(string OperationId, string RequestHash,
    QueryIdentity Owner, OperationStatus Status, SnapshotRef? Snapshot,
    ExportCheckpoint? Checkpoint, ExportManifest? Manifest,
    QueryResult? Page, IntentResult? Intent);
public sealed record OperationReservation(bool Created, OperationRecord Record);
public interface IOperationStore {
    ValueTask<OperationReservation> ReserveAsync(OperationRecord initial, CancellationToken ct);
    ValueTask<OperationRecord?> ReadAsync(string operationId, QueryIdentity caller, CancellationToken ct);
    ValueTask WriteAsync(OperationRecord record, long expectedSequence, CancellationToken ct);
}
public sealed record QueryAudit(QueryTarget Target, string OperationId,
    ImmutableArray<SourceRef> DeliveredMembers, string ResultHash,
    long Rows, long Bytes, DateTimeOffset Utc);
public interface IQueryAuditPort {
    ValueTask<bool> CommitAsync(QueryAudit audit, CancellationToken ct);
}
public interface IDiagnosticsPort {
    void Record(QueryEvent value);
}
public sealed class QueryPortException : Exception {
    public QueryError Error { get; }
    public QueryPortException(QueryError error) : base(error.Code) => Error = error;
}
```

- `QueryService` 的唯一公开构造签名：
  `QueryService(QueryIdentity trustedIdentity, QueryHostOptions options, ICatalogPort catalog, IAuthorizationPort authorization, ISnapshotPort snapshots, IProjectionPort projection, ICursorPort cursors, IOperationStore operations, IQueryAuditPort audit, IExportTargetPort exportTargets, ImmutableArray<IFormatAdapter> formats, IEvidenceRetentionPort? evidence, IDiagnosticsPort diagnostics, TimeProvider clock, Action<QueryEvent>? observer)`。implements IQueryService；参数均非空，evidence/observer 可空；空 evidence 只阻断 IncludeEvidenceBytes，不使普通页失败。每种 Format 仅一个适配器，未知/重复格式拒绝构造。所有依赖显式借用，Host 先 Dispose service，最后按反序 Dispose 自己拥有的端口。
- Dataset 稳定键在 Fields 内，非 null 且行身份唯一；唯一性在适配器契约测试证明，出现重复时失败，禁止静默去重。允许的 StringComparison 为 .NET Ordinal 或 OrdinalIgnoreCase，不能拿任意 SQL collation 冒充；后端不能证明对代表字符/大小写相同排序时拒绝该字段排序。字段 Unit 无量纲写 `1`，禁止猜单位或把显示文字作为 ID。
- 同操作当前授权的 CheckAsync 与 CommitDeliveryAsync 分工：GuardId 只由受信端口产生，绑定主体/动作/精确行字段/语义/期限；CommitDelivery 是撤权与实际“进入响应/发布队列”的线性化点。若撤权先赢，返回 false 且不交付；已交付字节不声称召回。逐行过滤只决定可见性，页发布还核完整有序成员集合 ResultHash；导出每块及最终发布同样检查。端口实现缺这个原子边界不能假装两次普通角色查询等价。查询/导出/保存/读取意图/恢复回执使用独立 Action，完整生产保存还使用C.3 CheckSaveAsync以授权全部共享scope，证据读取许可不自动授予全局查询。
- Audit.CommitAsync 绑定完整有序身份/修订/hash 与结果摘要（空页也有记录），不能只记首尾 ID；审计成功后还检查当前授权。false、异常、未知回执不交付数据，错误 `QRY_AUDIT_UNAVAILABLE`；它是业务读审计端口，不能要求用户同时获得日志查询权。Core 不定义审计数据库或跨库事务。
- ICursorPort 的 Protect/Unprotect 是同步、无IO的保护/解析入口。生产主路线按C.2.1使用不可猜服务端句柄及有界绑定registry；其它明确登记的认证token适配须用宿主批准key ring、Constant-time MAC/AEAD先验认证后解析。token/payload各≤16KiB UTF-8，canonical域仍 `Asun.Query.Cursor/v2`；不能用普通hash代替认证或把句柄当执行许可。工程测试密钥只能用于明确的夹具。
- SourceReader 在一个消费者中枚举，ScannedRows 从实际读取候选源行累计且不可倒退（IM-066主路线详C.2，不等于物理执行器访问统计）；不可见记录也消耗扫描预算。EndOfSource 只在真正源 EOF 为 true，取消/异常/限额不是 EOF。reader 不持有 UI 跨浏览期。Snapshot lease 可跨页，计入 MaxSnapshots，绝不持有忙 reader；实时上下文无续页能力时页结束释放，有续页能力时与Fixed同样按有限TTL/Release释放。真实长浏览主路线为不可变 as-of/封存投影；只读 Repeatable Read 事务仅在适配 Profile 允许有限 TTL/连接占用时启用；Read Committed 或最大 ID 一律不可冒充 Fixed。
- ProjectionRead 携带实例受信 Target 和当前 Authorization；Anchor 是 Core 验签后的完整排序锚，不把 opaque token 交后端猜。Projection 可下推批准条件/授权，但 Core 仍逐行检查。精确 count/aggregate 在首页 reader 归还后另开同快照、无锚的全范围 reader；Core 在 MaxScanRows/MaxGroups/MaxTemporaryBytes 内流式计算，超限失败，禁止全表 ToList。Estimate 本版不推估，返回 NotComputed + QRY_BACKEND_UNSUPPORTED，页仍可完成；不冒充 exact。
- IOperationStore 原子 Reserve 绑定 ID/hash/Owner，Write 使用单调 Sequence CAS；同键异 hash 不覆盖。查询页记录受 MaxOperationRecords/TTL 严格限制，超限拒绝新请求，不无界保留页；可恢复导出/保存记录由真实持久 Store 保留且不可按缓存 TTL 当成不存在。模拟 Store 只能证明工程语义。请求和终态需持久化时不得先发布成功再写状态。NotFound 仅在确证当前可见且记录不存在时给 `QRY_OPERATION_NOT_FOUND`，不证明外部文件没有发布。
- Encode 的 EncodedBlock.Bytes /证据 Read 产生的 ReadOnlyMemory 仅在下一次 MoveNextAsync 前有效；Core await WriteAsync 成功后才释放/复用该块，不让队列保留借用内存。reader→encoder→writer 有界 Channel 选择 Wait，绝不 DropOldest/DropWrite；条数与字节双计量，单块超过 QueueBytes 立即拒绝。队列/写入只用同 deadline 和取消令牌，不在每块重置 TTL。
- 行式格式的 EncodedBlock 必须只包含完整可恢复记录；C.4 的 XLSX 封闭容器传输块是明确例外，不具行级恢复能力。行式格式的CompleteRows 是本块行数、LastKey 是最后完整行完整排序键，FinalBlock 标记编码器完整结束；收尾块可0行/空LastKey。Core checked累计行/字节，最终源EOF与FinalBlock必须同时成立。未关闭XLSX不支持行级检查点。所有排序字段必须可获授权（包括稳定键），否则拒绝排序，不能借SortKey泄漏未授权值。PublishAsync 在原 operation staging 上执行不覆盖发布并持久化回执；取消/断连后不猜 NotPublished。CreateAsync 对同 ID/同 requestHash 原子恢复或新建原 staging，返回 lease.Checkpoint；checkpoint 绑定完整行末键、格式/源切面、原期限、扫描/行/字节累计和已完成对象。不同 hash 直接冲突。只在完整行/块 Flush(true) 和摘要核验后提交 checkpoint；读取时重算硬盘 prefix hash，不能从普通 SHA-256 摘要恢复内部算法状态。续传先流式重读 prefix 重建 hash，计入原 IO/时间预算；扫描/磁盘累计不重置。恢复不原地 append 半行或未闭合容器；不支持 checkpoint 的格式在发布未发生确认后以原 ID 重建 staging，不产生第二份已发布文件。软件实现按C.3～C.5冻结；宿主只绑定受信目标、事实引用和真实保持资格，不再由普通程序员另选算法。
- observer 为可空 Action，实例内每操作顺序串行、跨操作可交错；回调在专用有界派发队列执行，不在 DB/native 线程，不捕获 SynchronizationContext。进度可按 operation 合并，ResourcesReleased/Terminal 不丢；回调异常只诊断。关闭等待已开始回调返回，故回调不可等待本实例 Close/Dispose；宿主以 async continuation 关闭。队列慢时停止新接纳而非无界积累。IDiagnosticsPort 必须非阻塞，不提供日志读取权限。

### B.3 保存、加载及迁移查询意图（仍属模块完整范围）

```csharp
public sealed record SavedIntent(SourceRef Identity, VersionRef CatalogVersion, QueryIntent Intent,
    ExportProfile? PreferredExport, string Name, string OwnerId,
    ImmutableArray<string> SharedScopes);
public sealed record SaveIntentRequest(string OperationId, QueryIdentity Identity, VersionRef CatalogVersion,
    string Name, SourceRef? Saved, long ExpectedRevision, QueryIntent Intent,
    ExportProfile? PreferredExport,
    ImmutableArray<string> SharedScopes, QueryBudget Budget);
public sealed record LoadIntentRequest(Guid RequestId, QueryIdentity Identity, SourceRef Saved,
    QueryBudget Budget);
public sealed record MigrateIntentRequest(string OperationId, QueryIdentity Identity,
    SourceRef Saved, VersionRef TargetCatalog, bool AcceptSemanticChanges,
    QueryBudget Budget);
public sealed record IntentDifference(string FieldPath, string ChangeKey);
public sealed record IntentResult(IntentOutcome Outcome, SavedIntent? Saved,
    ImmutableArray<IntentDifference> Differences, OperationStatus Operation);
public sealed record IntentWriteReceipt(IntentOutcome Outcome, SavedIntent? Saved, QueryError? Error);
public interface ISaveQueryPort {
    ValueTask<SavedIntent?> ReadAsync(SourceRef saved, CancellationToken ct);
    ValueTask<IntentWriteReceipt> WriteAsync(SaveIntentRequest request, string requestHash, CancellationToken ct);
    ValueTask<IntentWriteReceipt> QueryReceiptAsync(string operationId, QueryIdentity caller, CancellationToken ct);
}
public sealed record IntentMigration(QueryIntent? Intent, ExportProfile? PreferredExport,
    ImmutableArray<IntentDifference> Differences, QueryError? Error);
public interface IIntentMigrationPort {
    IntentMigration Migrate(SavedIntent original, VersionRef targetCatalog);
}
public interface IQueryIntentService : IAsyncDisposable {
    ValueTask<IntentResult> SaveAsync(SaveIntentRequest request, CancellationToken ct);
    ValueTask<IntentResult> LoadAsync(LoadIntentRequest request, CancellationToken ct);
    ValueTask<IntentResult> MigrateAsync(MigrateIntentRequest request, CancellationToken ct);
    ValueTask<OperationObservation> QueryOperationAsync(string operationId, CancellationToken ct);
    ValueTask<CloseResult> CloseAsync(CancellationToken waitCancellationToken);
}
```

`QueryIntentService(QueryIdentity trustedIdentity, QueryHostOptions options, ICatalogPort catalog, IAuthorizationPort authorization, ISaveQueryPort saved, IIntentMigrationPort migrations, IOperationStore operations, IQueryAuditPort audit, IDiagnosticsPort diagnostics, TimeProvider clock, Action<QueryEvent>? observer)` 为唯一构造。共享校验/canonical 与 QueryService 相同；不建立快照或 reader。Save 的 Name 为资源无关显示名（1..128 UTF-8），不能是存储路径；ExpectedRevision=0 且 Saved=null 新建；更新须 Saved 非空且 ExpectedRevision>0 与原数字修订 CAS，Saved.Identity.Revision 为正十进制。Saved 身份由 ISaveQueryPort 分配，不接受任意覆盖其它 Owner 条目。共享范围须由当前授权批准；保存不附带执行权限。Load 核当前读取权限和原身份/hash，再返回原意图及迁移差异；不自动执行。Migrate 无注册迁移器为 QRY_MIGRATION_REQUIRED，失败为 QRY_MIGRATION_FAILED；只允许显式字段 ID/单位/枚举/时间规则映射，禁止删条件或 nearest 字段替代。AcceptSemanticChanges=false 且有差异仅返回差异与 Rejected，不能写新版本；true 仍校验当前目录及权限，原意图保留，保存为新修订。同键恢复必须读原 OperationStore，Unknown 不重发新键。


- SaveIntentRequest.CatalogVersion必须为构造目录当前Version；SavedIntent保留当时版本与PreferredExport（不能含Target路径/secret），读旧版本仅解析原内容，不自动用当前目录解释。Load仅返回原Saved，若需要迁移则Outcome=Loaded且Differences指示QRY_MIGRATION_REQUIRED；没有当前执行许可不能自动Query。Migrate依据原CatalogVersion/Intent.Dataset至TargetCatalog的有限映射，产生完整新Intent，任何删除字段/条件/格式变化必须报告差异且保留旧内容。PreferredExport是可选偏好，加载也须当前Profile重新批准。
- 在SavedRead/Recover/Release的入场对象授权阶段，QueryTarget.Dataset/SemanticHash可空，Row须精确原Saved/操作对象引用且Action固定；读取后再以实际Dataset/hash做内容授权。查询/导出阶段两字段必填，不允许通配对象。Name/SharedScopes空白不隐式全局共享。
- ISaveQueryPort.WriteAsync收到同OperationId/原requestHash只回原IntentWriteReceipt；Unknown必须附QRY_PUBLISH_UNKNOWN、Saved=null，Core实际IO归还后状态AwaitingReceipt。QueryReceiptAsync已确认保存才填Saved；恢复不再次写新修订。MigrateAsync在同原operationId下构造目标SaveIntentRequest并复用该幂等端口，ExpectedRevision精确来自原Saved数值修订，requestHash仍使用原迁移domain；端口不得自行按Save domain重算。
- IntentOutcome只为本次语义分类，Operation.State负责资源/在途状态。Saved/Loaded/Migrated只有Operation.Completed才可交付完整Saved；Conflict=Rejected+QRY_OPERATION_CONFLICT，不覆盖条目；Unknown同AwaitingReceipt/DrainUnknown处理。Save完成不等于执行权或共享质量放行。

### B.4 独立落点、分片与六项接收

所有路径是预定工程，本文不创建代码。基础命名空间 `Asun.Modules.Query`；适配器 `Asun.Modules.Query.Adapters`；控件 `Asun.Modules.Query.Wpf`，测试/Host 使用同名后缀。Core 工程与测试见顶部 binding；后续工程只能位于 `src/Modules/query/Asun.Modules.Query.Adapters/`、`src/Modules/query/Asun.Modules.Query.Wpf/`、`tests/Modules/query/Asun.Modules.Query.Adapter.Tests/`、`tests/Modules/query/Asun.Modules.Query.Wpf.Tests/`、`tests/Modules/query/Asun.Modules.Query.Core.Tests/`（两个无UI Host同Exe）。各 .csproj 同目录同名；禁止扩写 Shell/其它模块/共享 Contract/tools。本次允许写入仍仅唯一指导。

| 能力切片 | 完整内容与依赖 | 六门准备结论及后续门 |
|---|---|---|
| Q-C1 值/条件/规范化 | B.1/B.2类型、§3/§4.2～4.4运算/比较/字节/hash、结构Validate | `ModuleCoreImplementationReady`（仅规格）；六项已由主控2026-10-10回读接收；218字节空Aggregate Golden独立字段复算一致。代码尚未创建/运行 |
| Q-C2 查询/授权/快照/聚合 | 全部IQueryService、页/反向/计数/聚合、snapshot registry、授权/审计/回调/关闭 | `ModuleCoreImplementationReady`（仅规格）；六项已由主控2026-10-10回读接收。真实授权线性化、数据库语义/索引/驱动排空保留适配门 |
| Q-C3 导出/恢复 | ExportAsync、OperationStore、TypedJsonLines、完整清单、Checkpoint/Publish/回查 | `ModuleCoreImplementationReady`（仅规格）；六项已由主控2026-10-10回读接收。持久Store、真实文件崩溃/恢复、消费Profile/附件保持保留实际门 |
| Q-C4 保存/迁移 | B.3全部入口/授权/CAS/差异/未知回执与关闭 | `ModuleCoreImplementationReady`（仅规格）；六项已由主控2026-10-10回读接收。真实存储/生产迁移目录保留后续门，不带入平台私表 |
| Q-A/W 适配与可选控件（U1） | §10、真实存储/格式/保持/宿主授权 | U1指导内容已主控接收（2026-10-10）；真实WPF/后端/产品资格未关闭，不标UI为ModuleCoreImplementationReady；运行资格仍 `PreparationIncomplete / NotReady`。真实.NET10/WPF/25.2.3编译、1920×1080三语/UIA、双Host与性能门未关闭 |

接收范围仅Q-C1～Q-C4的DEV-GOV-010 §3.1六项实施规格；本轮没有产品代码、编译/正式测试、真实DB/硬盘恢复/DevExpress运行或性能成绩。Core规格接收不等于代码实施/集成或运行资格，也不自动启动开发。客户数据量/时延/磁盘保留/容许TTL等目标缺失时为TargetPending/NotEvaluated，只阻断相应消费者性能与生产资格。



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

## 附录 C：完整范围的软件装配与可选能力 v1

本节是 query 自身的实施决定，供 Adapters/Wpf 与具备扩展能力的 Core 编排消费；不创建第二份活动契约。B.1～B.3 的 v0.2 基础签名、既有 Q-C1～Q-C4 规格接收不变；下列新增能力不追溯声称已被旧六门接收或运行通过。完整范围的内部设计按本节闭合，真实映射/运行门见§19。所有本模块类型未特别注明时使用 `Asun.Modules.Query`；IM-066 同名 VersionRef/OperationRecord 等必须用 namespace alias，不能按结构相似直接强转。

### C.1 聚合编码与证据对象的明确接点

```csharp
public abstract record QueryExportRecord;
public sealed record RowExportRecord(QueryRow Row) : QueryExportRecord;
public sealed record AggregateExportRecord(AggregateRow Row) : QueryExportRecord;
public sealed record ExportEncodingContext(QueryIntent Intent,
    ImmutableArray<FieldDescriptor> Fields, ExportProfile Profile,
    SnapshotRef Snapshot, string SemanticHash, QueryBudget Budget,
    int MaxBufferBytes, long MaxSpoolBytes);
public interface IQueryFormatAdapterV1 : IFormatAdapter {
    IAsyncEnumerable<EncodedBlock> EncodeAsync(ExportEncodingContext context,
        IAsyncEnumerable<QueryExportRecord> records, CancellationToken ct);
}
public sealed record EvidenceObjectDescriptor(SourceRef Identity, string Role,
    long LengthBytes, string ContentSha256);
public interface IEvidenceObjectLease : IEvidenceLease {
    ImmutableArray<EvidenceObjectDescriptor> Objects { get; }
}
public interface IEvidenceObjectRetentionPort : IEvidenceRetentionPort { }
public interface IExportObjectLease : IExportLease {
    ValueTask<ExportObject> WriteObjectAsync(EvidenceObjectDescriptor descriptor,
        IAsyncEnumerable<ReadOnlyMemory<byte>> blocks, CancellationToken ct);
}
public interface IExportObjectTargetPort : IExportTargetPort { }
```

这些是可选能力接口，不另造 QueryService 入口或同义请求。普通 v0.2 Core 夹具可继续用旧 EncodeAsync(rows,profile,ct)；完整格式 Profile 必须选择 IQueryFormatAdapterV1，生产聚合严禁 cast 为 QueryRow 或丢弃 Exact/Projection。构造时逐 Format 核唯一实例；格式扩展、附件保持和对象目标的能力检查在建立源/writer前完成。声明扩展而返回基础 lease 时，原Root收取并排空该 lease，返回 QRY_BACKEND_UNSUPPORTED，不换factory重试。旧基础格式不支持的完整Profile返回 QRY_EXPORT_FORMAT_REJECTED，不能静默降格式。

Intent.Aggregates 非空或 GroupBy 非空时只接受 AggregateExportRecord，否则只接受 RowExportRecord；混用、字段数/顺序/Kind 不符拒绝。聚合先按§4.3/§5.4完成受权源全扫描，再按完整组序编码；LastKey为完整Group元组，空Group全局聚合无锚。Manifest.Rows计输出源行或输出组数，metadata不计行；metadata同时保留实际受权匹配源行数，不能把组数称源成员数。源扫描、预扫描、重扫、编码、恢复验证累计同一原Budget，聚合/附件组合不能重置额度。输出行/组数受MaxRows，组字典/源seen/闭包/队列/编码同时占MaxTemporaryBytes，预算超限整体失败。

聚合 CurrentPage 在factory前明确 QRY_EXPORT_FORMAT_REJECTED：v0.2 Members是SourceRef，不能代表组页。AllMatching导出完整匹配组；ExplicitMembers先在原快照逐一核精确源身份、原predicate和当前权限，再聚合该批准源集合。UI将“当前页”置不可选并常显原因；不改变普通行当前页合同，也不把Group键伪装源身份。

IncludeEvidenceBytes 的步骤固定：保持原as-of source lease → 全匹配源扫描/逐行授权并收集Evidence引用 → 确证EOF和成员完整性 → AcquireAsync完整闭包 → 核IEvidenceObjectLease.Objects恰与闭包一一对应 → 同快照重扫生成数据/聚合 → 逐对象授权/审计/交付围栏并写入 → 完整核验/发布。预扫描reader先归还，snapshot和取得中的保持任务仍由原Root强持；不能逐行pin后宣称屏障。聚合附件来自实际参与源行，不能从组键推证据。事实Owner的封存保留保证须覆盖取得证据保持的间隙；中途不可读整体QRY_EVIDENCE_UNAVAILABLE，不换最新版本。

闭包按完整SourceRef去重；同Namespace/Id异Revision/Sha256保留独立身份，同完整身份却Role/长度/内容摘要冲突拒绝。Role是注册稳定代码，不是路径。每次完整导出最多16384个附件且描述总canonical≤16MiB（新增防耗尽协议上限，Profile可收紧，非客户容量目标），仍先按实际保守内存占用预约MaxTemporaryBytes；超过时QRY_BUDGET_EXCEEDED。Objects属性不可变、不进行IO。Identity.Sha256是对象身份摘要，不能推断等于ContentSha256；内容摘要由证据Owner提供并逐字节复核，零字节附件仍须核SHA-256空流摘要。

WriteObjectAsync在原writer内创建附件，不返回子句柄；Core登记唯一在途Task，串行写附件，所有借用block保持到消费完成。写入前核剩余总字节/临时盘；分块≤64KiB，checked累计长度与增量SHA-256，EOF必须长度/hash双符，否则QRY_EVIDENCE_UNAVAILABLE且禁止发布。返回 ExportObject.ContainsBytes=true、精确身份/role/实际长度/hash；每个对象完整flush并核验后才能进入CompletedObjects检查点。路径由目标内部用完整身份canonical摘要生成 `objects/<64hex>.bin`，禁止用ID/Role作目录；不同身份即使内容相同也不跨身份合并。恢复已完成附件时读回长度/hash/身份侧记，未知/半对象不能按“文件存在”跳过。

### C.2 IM-066 as-of 主读适配与长期历史

本小节全部新增配置、Header与源/上下文端口归 `Asun.Modules.Query.Adapters`，只在适配层使用；C.1能力接口仍归Core namespace。

生产主读适配 `Asun.Modules.Query.Adapters.QueryStorageAdapter` 同时实现 ISnapshotPort/IProjectionPort/IAsyncDisposable；Host借用注入 IM-066 IStorageDatabase，不直连Npgsql、不创建新池、不把 DbConnection/SQL/IM-066资源句柄传入Core。依据是[IM-066公开注册读及PostgreSQL接点](../storage-database/DEVELOPMENT-GUIDE.md) §2/§6/§17。IM-066逻辑Read逐次建立只读scope，不能保持跨页Repeatable Read；本适配只声明封存as-of Fixed，不宣称Realtime或RR；Realtime请求在取得源前QRY_BACKEND_UNSUPPORTED，其它适配可按B.2正式登记实时能力。§5中有限RR仍是其他有真实事务能力适配的可选路线。

Host装配采用以下显式参数，归Adapters命名空间：

```csharp
using Storage = Asun.Platform.StorageDatabase.Contracts;
public sealed record QueryStorageReadOptions(int ChunkRows, int MaxChunkBytes,
    int MaxSnapshotHeaders, int MaxConcurrentReaders, int MaxSortVariants, int MaxSegments,
    TimeSpan ResolutionBudget);
public sealed record QueryStorageSortBinding(VersionRef Dataset,
    ImmutableArray<SortTerm> Sort, VersionRef Variant, string OwnerKey, string? UtcFieldId,
    Storage.VersionRef ReadBinding,
    Storage.VersionRef InputSchema, Storage.VersionRef ResultSchema,
    Storage.StorageBindingDescriptor Descriptor, string StrategyId);
public sealed record QueryStorageRegistration(QueryCatalog Catalog,
    Storage.StorageInputLimits InputLimits, ImmutableArray<QueryStorageSortBinding> Reads);
```

唯一构造 `QueryStorageAdapter(Storage.IStorageDatabase runtime, QueryStorageRegistration registration, QueryStorageReadOptions options, IQuerySealedSourcePort sources, IQueryStorageContextFactory contexts, TimeProvider clock)`。sources/contexts是下述显式事实/授权映射边界，借用不Dispose；runtime由Host最后关闭。Options正且有限；ChunkRows≤1000、MaxChunkBytes≤Int32.MaxValue，headers≤Core MaxSnapshots、MaxConcurrentReaders≤64，sort/segments数量受启动目录字节限额，ResolutionBudget受当前授权余量及原deadline限制。启动拒重复/空/default/同Id修订异hash、Catalog不符和未经登记Strategy；本版StrategyId仅 `CorePredicateV1`。一个Dataset仅有限明确Sort组合，完整包含稳定键；聚合源选择Dataset.DefaultSort；Source Acquire根据原Intent是否聚合选择此SourceSort及variant，Header边界按SourceSort，原Intent.Sort/group游标仍为组序，不将group锚交源读取。Descriptor/InputLimits来自创建Runtime的同一已冻结配置；启动核ReadBinding/Schema/Owner/Purpose/Kind exact，读取不算mutation技术hash。未登记任意字段组合返回QRY_BACKEND_UNSUPPORTED，不穷举8字段的所有方向，也不拼SQL。

```csharp
public sealed record QuerySealedSegment(string Id, VersionRef Version,
    long Rows, long Bytes, ImmutableArray<Cell> FirstKey,
    ImmutableArray<Cell> LastKey);
public sealed record QuerySealedHeader(VersionRef Dataset, VersionRef Catalog,
    VersionRef SortVariant, string CutId, ImmutableArray<VersionRef> Sources,
    ImmutableArray<QuerySealedSegment> Segments, DateTimeOffset RetainedUntilUtc);
public interface IQuerySealedSourceLease : IAsyncDisposable {
    QuerySealedHeader Header { get; }
}
public interface IQuerySealedSourcePort {
    ValueTask<IQuerySealedSourceLease> AcquireAsync(QueryRequest request,
        AuthorizationDecision authorization, CancellationToken ct);
}
public interface IQueryStorageContextFactory {
    Storage.CallContext Create(QueryIdentity identity,
        AuthorizationDecision authorization, TimeSpan executionBudget,
        TimeSpan waitBudget);
}
```

Source Acquire返回已发布、不可变、全来源封闭的Header及其真实保留lease；不是Owner未来选择算法。初次由事实Owner登记封存Cut；恢复必须读取Request.Snapshot的同Cut/同来源版本，不准新建切面。Owner负责封存事实与保留屏障，query负责header/type/hash/coverage校验、租约registry和读取编排。Header.SortVariant须精确等于登记读取variant，Sources还须包含该封存排序/索引修订；不能用另一排序的边界证明当前Sort。Header的Segments必须按**完整Sort全序**互斥连续且覆盖声明Cut，Rows/Bytes checked总和、空段边界为空；跨历史物理文件的重叠/修订选择在Owner封存投影时完成，不能在Core静默去重。各Sort variant须有对应覆盖证明，不用时间分段顺序冒充任意Sort全序；不能证明时拒绝该Sort。选择这一主路线免去无限扇入reader/任意归并算法。长期历史逐段串行keyset读，缺任一必需段QRY_DATASET_REVISION_MISMATCH；不返回“其余可读段”的成功全集。

SnapshotOpen先预约header/源取得槽，再Acquire，核dataset/catalog/source向量、全覆盖、RetainedUntil≥所需TTL且不超原授权到期；用不可猜实例Handle映射完整header、原Budget、Scope、源lease和引用计数。ProjectionRead必须找到同实例活动entry或经合法同Cut恢复，核其Target/Policy/Intent绑定及原deadline；不从Handle解析路径。每reader先预约entry引用，串行调用runtime.OpenSessionAsync(SessionRequest(context, registeredOwnerKey, PoolPurpose.Query))并保存原Task，再ReadAsync(RegisteredReadRequest(context, binding, payload))；read返回后真实Dispose session才能取下一块。Header/源lease保持至所有reader/原IO归还，不以reader等待超时删entry。取消/释放按§8强持原session/read/Dispose任务；Dispose adapter排空自己的header/reader，不Dispose借用Runtime。

输入payload/结果的唯一typed形状如下（Adapters），不留给codec另选字段：

```csharp
public sealed record QueryProjectionChunkPayload(Storage.VersionRef Schema,
    Storage.StorageScope StorageScope, Storage.StoreRef Store, string QueryScopeId,
    string CutId, string SegmentId, VersionRef SegmentVersion,
    VersionRef SortVariantVersion, bool AnchorPresent, ImmutableArray<Cell> Anchor,
    bool Backward, bool UtcRangePresent, string? UtcFieldId,
    long StartUtcTicks, long EndUtcTicks, int MaxRows, int MaxResultBytes)
    : Storage.IOwnerStoragePayload;
public sealed record QueryProjectionChunkResult(string CutId, string SegmentId,
    VersionRef SegmentVersion, VersionRef SortVariantVersion,
    ImmutableArray<QueryRow> Rows, bool EndOfSegment);
```

各binding输入/结果domain分别为 `Asun.Query.ProjectionChunk/<variant.Id>/input/v1` 与 `/result/v1`，按上述声明序；Storage类型的编码同C.3。AnchorPresent=false要求Anchor=[]；UtcRangePresent=false要求UtcFieldId=null且两个ticks=0；true时UtcFieldId须为该statement唯一登记的Known UTC列，range为合法半开[start,end)。注册variant最多下推一列UTC（不能随请求选择任意列）；未登记的其它时间字段仍由Core判定。Schema和IM-066版本用其原类型，query语义字段按§4.4编码；参数值只能来自核验后的trusted context/entry/anchor，不能从原UI文本拼入。每块MaxRows=min(ChunkRows,剩余ScanLimit)，MaxResultBytes=min(MaxChunkBytes,当前临时预约额度,IM-066输入/结果上限)，不足一行立即预算错误。Chunk bytes和解码DTO同时占原Budget；先核length再分配。reader.ScannedRows为本注册statement实际返回给Core判定的候选源行，**包含隐藏/不匹配行**；这是逻辑源扫描计量，不能声称等于PG物理heap/index访问量。固定SQL内部访问/必要范围以外的扫描成本由StatementTimeout、注册计划/索引预算及真实EXPLAIN资格约束，不用返回行LIMIT声称物理扫描有界；Core跨预扫/分页/聚合累计，候选超限不当过滤成功。

结果schema固定为 `QueryProjectionChunkV1`，型别/顺序见上；Rows使用B.1 QueryRow完整canonical。注册statement固定返回Dataset全部Fields目录序，adapter reader保留这些候选值供Core条件/分组/聚合判定，不因用户只投影id就漏掉条件字段。Core在完整性/predicate/逐行授权后，才按Intent.Fields构造最终QueryResult.Rows.Cells；未选择字段不能泄露到响应、encoding或日志。所有条件/排序/分组/聚合输入字段须入场具备相应读/过滤权，不用秘密字段筛选可见结果。OwnerReadResult.Schema须精确、Fault为空；ResultCodec先检bytes/类型/数量，再query核完整来源/字段状态/SortKey及严格全序。reader不提前过滤候选，所以Core可对所有扫描行做必需来源完整性/重复身份检查，再执行§4.2三值predicate和逐行授权。零行且非EndOfSegment是协议错误；非空块锚必须严格推进，不能相同锚无限循环。短块不能自行证明EOF，只有注册结果EndOfSegment且所有必需段完成才EndOfSource=true。到ScanLimit但EOF未证实仍预算失败。

PostgreSQL注册包按每个variant提供固定StatementCatalog/参数列类型/ResultCodec；query codec实现 Asun.Platform.StorageDatabase.PostgreSql.IPostgreSqlBindingCodec 的GetParameters/EncodeResult，零IO、不生成SQL。固定只读statement明确tenant/scope/cut/segment、完整字典序keyset、方向/null rank和LIMIT；结果不含驱动对象。Binding Kind=Read、Purpose=Query、AffectedRows=0、MaxCommands=1；具体VersionRef hash由注册包内容计算，不能伪造占位hash。UtcTicks使用BigInt以保留100ns，不能让PG UtcTimestamp微秒精度悄悄截断；UInt64使用已登记numeric全域。文本排序必须与Core一致：Ordinal可由Owner物化UTF-16 code-unit big-endian bytea序键且登记相等证明；OrdinalIgnoreCase不得拿lower()/locale collation猜等价，注册包无法证明全部允许域则拒绝该variant。Guid按小写D文本Ordinal；null/unknown rank按§5.4，不只用PG默认NULLS。

CorePredicateV1不做任意AST→SQL转换：只下推受信tenant/scope、精确Cut/段/keyset以及可证明为整个predicate必要条件的Known UTC半开范围；只取空Condition以外的单个UTC叶或顶层And的该UTC字段叶交集，Or内范围不能提取，不能把IsUnknown误变非空SQL过滤。其余条件全部由Core在有界候选流上判定，包含字面StartsWith/Contains，因此不依赖LIKE/collation的近似语义。Condition为空仍必须AllowAllRange/AllRangeConfirmed；有合法Condition但无可下推UTC范围时，按已登记CorePredicateV1与扫描成本预算准入，不另要求伪装无条件确认。预算不足整体失败。真实EXPLAIN/分区pruning/索引和完整成员等价验证是运行门，PG18分区教程不能证明实际负载达标。

### C.2.1 有界服务端游标外壳

生产游标选择 `Asun.Modules.Query.Adapters.QueryHandleCursorAdapter : ICursorPort`，不引入密钥环或另造Core协议。唯一配置/构造如下：

```csharp
public sealed record QueryHandleCursorOptions(int MaxEntries, long MaxBytes,
    TimeSpan MaxTtl, int MaxInsertAttempts);
// QueryHandleCursorAdapter(QueryHandleCursorOptions options, TimeProvider clock)
```

Options全部正且有限，MaxEntries≤8192、MaxInsertAttempts≤8；MaxBytes包括绑定canonical、DTO保守占用、字符串/字典entry及实例代，不只计token长度。MaxTtl不得超过Host批准的snapshot寿命；本适配没有磁盘/网络IO，不拥有注入clock。初始化用 `RandomNumberGenerator.Fill(Span<byte>)` 生成16随机字节实例代，Protect每次生成32随机字节句柄；各自按Convert.ToBase64String后去尾padding、`+→-`、`/→_`，token为 `qch1.<22字符实例代>.<43字符句柄>`，恰71个ASCII字符。Unprotect先核固定长度/前缀/字符域及严格decode后重新encode相同，无padding/其它等价字形；异实例统一QRY_CURSOR_INVALID，不解析用户payload。

Protect输入先按B.1校验和§4.4编码完整CursorBinding（Request.Cursor固定null），canonical≤16KiB；签发时记录IssuedUtc与ExpiresUtc，期限≤min(原deadline、snapshot.ExpiresUtc、IssuedUtc+MaxTtl)，禁止无效/已过期绑定。服务端保存模块自有immutable绑定，不能引用调用方可变后门；锁内预约bytes/entry，再原子TryAdd新句柄，碰撞只有限重新生成且不覆盖已有entry。容量满时可移除确证到期entry；不得驱逐未到期entry以腾空间，有限尝试仍无空间抛QRY_BUDGET_EXCEEDED，无新token。Unprotect仅锁内查本实例entry、核到期并返回完整绑定或CursorDecoded(null,QRY_CURSOR_INVALID)，不触发源取得/恢复。

此句柄只防伪造绑定，不是执行授权。Core仍比较当前identity/完整intent与semanticHash/预算/源向量/Policy/锚/期限并逐行授权；原Snapshot释放后旧句柄即使未到期也不能续页。实例重启旧token失效，普通浏览开始新执行；持久导出/保存恢复按OperationRecord/Checkpoint同原ID完成，不靠游标伪装跨进程续页。到期/容量清理仅释放本适配immutable内存，不释放Core源lease或改操作状态。

### C.3 query 自有元数据持久CAS与保存事务

持久 `QueryStorageMetadataAdapter` 实现IOperationStore/ISaveQueryPort/IAsyncDisposable，只存本模块查询/导出恢复与保存意图，不写生产事实。唯一构造为 `(Storage.IStorageDatabase runtime, QueryIdentity trustedIdentity, QueryMetadataRegistration registration, IAuthorizationPort authorization, IQueryStorageContextFactory contexts, TimeProvider clock)`；registration的精确形状见下文，适配实例固定trustedIdentity；ReadAsync(SourceRef)不借隐藏当前用户。完整生产保存须authorization实现IQuerySaveAuthorizationPortV1，构造时缺能力拒绝；基础Core无共享夹具不追溯为生产授权资格。每次输入caller/新请求identity须匹配当前trustedIdentity的Subject/Tenant/Scope/Session/Purpose（RequestRevision是请求代次）；持久原Owner回查仅比较Subject/Tenant/Scope/Purpose，原Session保留不改，执行续接须§9.1受信授权。Saved.OwnerId可为已获共享许可的原Owner，不要求等于读者。OperationRead/IntentReceipt用Recover、IntentRead用SavedRead、IntentWrite用Save、OperationReserve/Write用OperationWrite动作取得当前AuthorizationDecision，再contexts.Create生成受信CallContext；Core交付前授权/审计仍再次执行。权限映射由contexts生成，禁止从QueryIdentity.ScopeId拆机台路径。写用已注册Production逻辑session，读取/原回执用Query；不借读池写ledger，也不另建数据库连接。所有session、ExecuteTransaction/QueryOperation/GetTaskStatus/Dispose任务先进入适配有界Owner，仍遵守§8迟到返回。元数据CallContext执行/等待时长取min(Capacity.CallBudget/WaitBudget、授权余量、可用原请求Budget余量)；只有无业务Budget参数的只读回查/恢复观察用有限Capacity预算，不借此重置业务deadline。OperationReserve的原业务Budget由Core入场核验，适配方法本身无该参数，不猜从Page/Checkpoint恢复，按Capacity预算执行。

Recover/OperationWrite的操作对象引用采用Namespace=`asun.query.operation`、Id=原operation UUID D、Revision=`1`；身份Sha256=domain `Asun.Query.OperationIdentity/v1` 后原SubjectId/TenantId/ScopeId/Purpose/OperationId声明序canonical摘要，排除Session/RequestRevision和状态内容。这是确定对象身份，不等于OperationRecord内容hash；授权必须按完整对象及当前主体核验。SavedRead直接用输入精确SourceRef。新建Save没有原Saved时Row为空，不伪造已有对象；更新使用原Saved。Save/Migrate由Core和适配明确调用CheckSaveAsync(originalSaveRequest,originalRequestHash,ct)，传递完整CatalogVersion/原Saved/ExpectedRevision/新Intent/SharedScopes而不让授权Owner从字段列表猜共享范围；返回guard绑定该规范requestHash及所有共享scope/读写权限。原CommitDeliveryAsync仍核相同Save QueryTarget和完整Proposed内容摘要（含SharedScopes），签发permit后才启动原保存事务；写后结果交付再核当前授权，回查不自动重新共享。新建OwnerId/更新原OwnerId保护由C.3事务共同核验。

本小节新增registration/payload/result/journal类型归Adapters；IQuerySaveAuthorizationPortV1归Core namespace `Asun.Modules.Query`，Core不引用Adapters。公开配置形状：

```csharp
public sealed record QueryMetadataCapacityProfile(VersionRef Version,
    int MaxRecordBytes, int MaxSavedBytes, int MaxRecords, int MaxSavedRevisions,
    int MaxConcurrentCalls, TimeSpan CallBudget, TimeSpan WaitBudget);
public sealed record QueryMetadataBinding(string Id, Storage.VersionRef Binding,
    Storage.VersionRef InputSchema, Storage.VersionRef ResultSchema,
    Storage.StorageBindingDescriptor Descriptor);
public sealed record QueryMetadataJournalOptions(VersionRef Policy, string AbsoluteRoot,
    long MaxBytes, int MaxEntries, int MaxEntryBytes);
public sealed record QueryMetadataRegistration(string OwnerKey,
    Storage.StorageScope Scope, Storage.StoreRef Store,
    Storage.StorageInputLimits InputLimits, QueryMetadataCapacityProfile Capacity,
    QueryMetadataJournalOptions Journal,
    ImmutableArray<QueryMetadataBinding> Bindings);
// 单独放Asun.Modules.Query.Core；其余本节配置/载荷放Adapters。
public interface IQuerySaveAuthorizationPortV1 : IAuthorizationPort {
    ValueTask<AuthorizationDecision> CheckSaveAsync(SaveIntentRequest request,
        string requestHash, CancellationToken ct);
}
```

Bindings恰含下文六种固定Id，Kind/Purpose/Schema/codec exact；startup拒缺失/重复、Descriptor.Version与Binding及Input/ResultSchema不符、context与Scope/Store不一致和无效容量/时间；InputLimits/Descriptor须与Host用于创建IM-066的同一已冻结配置一致，不能重查动态目录。MaxConcurrentCalls≤64且在每个原IO启动前预约槽。逻辑scope容量行（PK=tenant/query_scope/storage_scope/store/generation，reservedRecordBytes/records/savedRevisions及policy version）在注册事务行锁内核额度/预留，不从无锁COUNT推容量；query_scope使用原ScopeId独立列，storage_scope包含完整IM-066五字段，不把二者强转。OperationReserve预约该op一个MaxRecordBytes envelope，后续record原地CAS不消费第二个slot。固定命令及逐项行数如下，所有mutation条件共享锁定的原键/请求hash/owner/容量/版本前置谓词，partial结果在commit前使整个事务回滚：

| Binding | 固定StatementCatalog顺序 | Owner AffectedRows / MaxCommands | codec必验分支 |
|---|---|---|---|
| OperationReserveV1 | Read锁容量/原键 → Mutation容量预留 → Mutation初始record → Read结果 | Min=0/Max=2，4命令 | 新建mutation向量(1,1)、Created=true；同键同hash重放(0,0)、Created=false/原record；其它向量/异hash拒绝并回滚 |
| OperationWriteV1 | Mutation CAS record → Read结果 | Min=0/Max=1，2命令 | 变更(1)/Applied=true；相同newSequence且recordHash相同的重放(0)/Applied=false；其它0行冲突，不覆盖 |
| IntentWriteV1 | Read锁容量/原receipt/head → Mutation容量 → Mutation CAS head → Mutation revision → Mutation receipt → Read结果 | Min=0/Max=4，6命令 | 新建/更新向量(1,1,1,1)；原receipt重放(0,0,0,0)；全0无原receipt是CAS/权限/容量错误，按证据分开，不当重放；任意混合/异receipt冲突回滚 |
| OperationReadV1 / IntentReadV1 / IntentReceiptV1 | 各一条Read | AffectedRows=0，1命令 | 当前获权且确证原键无行才返回NotFound；坏schema/hash/重复行不是NotFound；在完整scope按operation_id读取原Owner后，异主体/用途返回AuthDenied而非通过WHERE主体过滤成NotFound |

变更Binding为Kind=Transaction/Purpose=Production，读取为Kind=Read/Purpose=Query；query元数据固定ReadCommitted，串行化由scope容量行锁与显式CAS/唯一约束保障。MaxRetries=0，由原技术identity回查处理未知，不能自动换ID重试。所有语句显式tenant/query_scope/完整storage_scope/StoreGeneration，并执行登记的tenant RLS；codec结果在IM-066提交前校验，不跨Owner写技术ledger。

物理Schema为query私有 `query_meta`（不进入Core或其它模块契约），表结构由query注册包冻结；下表scope缩写代表query_scope加完整storage_scope，不能省略任一维度：

| 表/主键 | 必需列/约束 | 权威 |
|---|---|---|
| operation；PK=(tenant,scope,store,generation,operation_id) | request_hash、owner完整canonical、sequence bigint≥0、record bytea、record_hash、recoverable bool、terminal bool、expires_utc_ticks；原hash/owner不可变 | 原OperationRecord唯一CAS状态；页TTL只在确证terminal且不可恢复时可回收 |
| intent_head；PK=(tenant,scope,store,generation,intent_id) | current_revision bigint>0 | 保存意图修订的CAS；不授执行权限 |
| intent_revision；PK=head+revision | saved canonical、saved_hash、creator_subject、shared_scopes canonical | immutable SavedIntent原版本；不改历史 |
| intent_receipt；PK=(tenant,scope,store,generation,operation_id) | request_hash、outcome、saved_id/revision/hash、receipt_id | 原保存/迁移回执，与head/revision同事务 |

容量Profile冻结MaxRecordBytes/MaxSavedBytes/MaxRecords/MaxSavedRevisions，正且checked；与IM-066输入/结果上限一并冻结，入场预约该record最大envelope再启动源副作用；合法DTO并不保证任意Profile容纳全部极值。页/聚合/检查点边界有界编码核记录容量，超envelope在对外交付前QRY_BUDGET_EXCEEDED，不先ToArray后拒绝。MaxOperationRecords限制活动与保留页记录，不把长期可恢复导出/保存按TTL删除；持久容量满拒绝新操作QRY_BUDGET_EXCEEDED，已预约操作的更新空间不被其他操作侵占。生产保留/归档期限由Host政策采纳，query不自动删用户意图或未知操作。数据库迁移在IM-066正式migration接点执行；普通运行binding没有DDL。

有限bindings冻结为 `OperationReserveV1`、`OperationWriteV1`、`OperationReadV1`、`IntentWriteV1`、`IntentReadV1`、`IntentReceiptV1`。payload实现IM-066 IOwnerStoragePayload；下列Shape是对应binding唯一型别，codec不接受匿名object：

```csharp
public sealed record QueryMetadataScope(Storage.StorageScope StorageScope,
    Storage.StoreRef Store, string QueryScopeId);
public sealed record QueryOperationReservePayload(Storage.VersionRef Schema,
    QueryMetadataScope Scope, OperationRecord Initial, string RecordHash)
    : Storage.IOwnerStoragePayload;
public sealed record QueryOperationWritePayload(Storage.VersionRef Schema,
    QueryMetadataScope Scope, long ExpectedSequence, OperationRecord Record,
    string RecordHash) : Storage.IOwnerStoragePayload;
public sealed record QueryOperationReadPayload(Storage.VersionRef Schema,
    QueryMetadataScope Scope, string OperationId, QueryIdentity Caller)
    : Storage.IOwnerStoragePayload;
public sealed record QueryIntentWritePayload(Storage.VersionRef Schema,
    QueryMetadataScope Scope, SaveIntentRequest Request, string RequestHash,
    SavedIntent Proposed) : Storage.IOwnerStoragePayload;
public sealed record QueryIntentReadPayload(Storage.VersionRef Schema,
    QueryMetadataScope Scope, SourceRef Saved, QueryIdentity Caller)
    : Storage.IOwnerStoragePayload;
public sealed record QueryIntentReceiptPayload(Storage.VersionRef Schema,
    QueryMetadataScope Scope, string OperationId, QueryIdentity Caller)
    : Storage.IOwnerStoragePayload;
public sealed record QueryOperationReserveResult(bool Created, OperationRecord Record);
public sealed record QueryOperationWriteResult(bool Applied, OperationRecord Record);
public sealed record QueryOperationReadResult(bool Found, OperationRecord? Record);
public sealed record QueryIntentReadResult(bool Found, SavedIntent? Saved);
public sealed record QueryIntentWriteResult(IntentWriteReceipt Receipt);
public sealed record QueryIntentReceiptResult(bool Found, string? RequestHash,
    IntentWriteReceipt? Receipt);
```

输入/结果domain分别为 `Asun.Query.Metadata/<binding>/input/v1` 与 `/result/v1`，按上述声明顺序与§4.4原语编码；Storage.VersionRef固定Id/Revision I32/Hash.Hex，StorageScope五字符串、StoreRef StoreId/Generation I64/Profile，不拿query.VersionRef编码代替。除Shape本身外所有嵌套query record使用其完整声明序，不在这里替换成semanticHash。OperationRecord内容摘要domain=`Asun.Query.OperationRecord/v1`、全字段声明顺序；RecordHash是编码后SHA-256，不进入被摘要Record。结果Found=false仅Record/Saved/Receipt等可空载荷为空，Found=true对应必需载荷非空；Receipt Found=true时RequestHash必填且核原OperationRecord，结果schema为registration对应ResultSchema。失败抛QueryPortException或IM-066 Fault，不能编码为正常空结果。

Reserve初始Sequence=0且hash/owner/operation一致，不存在才插入；存在则精确核请求hash/原主体租户scope用途并返回原record。Write严格ExpectedSequence→ExpectedSequence+1，目标record.Status.Sequence必须相同；原hash/owner/OperationId不变且状态变化符合§7。CAS 0行后只相同新sequence和RecordHash可确认为重放；旧sequence/其它record不直接成功，相同旧sequence仅保留原技术identity调查，不能last-write-wins。

每个变更子调用的IM-066 OperationIdentity不可换：OwnerKey=query登记值；OperationId/IdempotencyKey采用 `qry/<original UUID D>/<binding>/<ExpectedSequence或0>`，PayloadHash必须调用 `Asun.Platform.StorageDatabase.Runtime.StorageRequestHasher.Compute(registeredRequest, binding.Descriptor, canonicalInput, registration.InputLimits)`，不是SHA-256(canonicalInput)。先用合法占位Sha256构造请求，Compute忽略Identity.PayloadHash，再with填实际完整技术信封摘要；References固定空ImmutableArray<Storage.ObjectRef>，query SourceRef不是IM-066对象保持声明。同identity异输入由IM-066拒绝。Save/Migrate IntentWrite末值0且RequestHash取原业务domain，不能另按Save重算。受信StorageScope/StoreGeneration来自context；读取不构造新mutation身份。ExecuteTransactionAsync返回StorageTaskStatus，只从State=Completed且Result.Commit.State=Committed、ResultSchema/ResultBytes精确核验的结果交付；ResourcesReleased以前不能释放原session/额度。保留TaskHandle后以GetTaskStatusAsync(TaskQuery(context,originalHandle))观察归还，以QueryOperationAsync(OperationQuery(context,originalIdentity))只读核原耐久receipt；两个接口职责不能混用。

Unknown时适配Owner保留原Task/handle/identity/payload/ExpectedSequence，真实原IO归还后仍查原技术identity并与原业务record/intent receipt交叉核验。确认前禁止对同操作发新sequence的Write；本机cache/读到旧sequence都不证明未commit。IOperationStore.WriteAsync没有typed返回，确认Applied或相同record重放才正常完成，否则抛QRY_PUBLISH_UNKNOWN并由Core保持AwaitingReceipt/DrainUnknown。新实例恢复使用下述私有恢复日志的**原完整技术identity及输入**（不能从业务requestHash猜PayloadHash），技术ledger及业务回查一致后才进入下一CAS；已确认RolledBack/Rejected作为原失败事实处理，不能以重放旧技术identity企图重新commit；用户合法新执行必须新ID。未知/过保证期/NotFound不自行重发，不绕过IM-066保留策略。


跨进程恢复输入只由query私有有界journal保存，schema如下；它是原调用材料，不是commit或业务状态的第二权威：

```csharp
public sealed record QueryMetadataJournalRecord(VersionRef Policy,
    Storage.OperationIdentity Identity, Storage.StoreRef Store,
    string BindingId, Storage.StorageBindingDescriptor Descriptor,
    long ExpectedSequence, string InputSha256, ImmutableArray<byte> CanonicalInput);
```

Journal.AbsoluteRoot由Host批准为稳定本机同卷根，ACL禁止不受信改写且无未批准reparse/symlink；不推导为SQL/产品路径。MaxBytes/MaxEntries/MaxEntryBytes正有限，entries≤4096；entry上限至少覆盖本registration有界输入且受IM-066限制。Adapters启动先取得该完整scope/store/owner journal命名空间的固定FileShare.None独占锁（不随单调用完成释放），同scope主写适配本版只一个活动实例；并发服务/两个Host借用这一Owner，跨主机多写不是本版主路线。其它只读消费者借用已注入的读端口，不夺取未死writer恢复责任。实际root介质/ACL/重启可达性属于Host资格，软件格式与恢复算法在此冻结。

原技术identity计算后、ExecuteTransaction之前，序列化JournalRecord，domain=`Asun.Query.MetadataJournal/v1`，完整声明序/§4.4原语；Storage.OperationIdentity按IM-066声明序，InputSha256严格等于CanonicalInput SHA-256；Identity.PayloadHash另按IM-066完整技术信封Compute复核，Store/Descriptor必须为原注册值，不混用两个摘要。canonical byte数组=U32LE长度+原bytes，不按Str编码。文件名取完整技术identity的canonical SHA-256，临时CreateNew→Flush(true)→同卷不覆盖rename为 `<64hex>.pending`；同名已存在核完整identity/原bytes/hash，相同复用，异输入冲突。先预约整个entry及临时文件双份空间，≤MaxBytes/MaxEntries；已满拒绝新mutation但保留原Unknown回查，不驱逐活动条目。未确证journal完成就不发DB事务；落盘未知保留原Task/文件并停止新发起，不把部分文件当成功日志。

适配startup有限枚举本命名空间最多MaxEntries条完整pending（超限停止新mutation），先核文件长度/协议/内容hash/scope/绑定版本，再以每条原identity QueryOperationAsync恢复；日志原Store/Descriptor/schema/版本必须仍受支持，不能重新Normalize为另一个输入。Committed只恢复原结果，RolledBack/Rejected恢复原失败；ledger NotFound、业务旧sequence或客户端进程已死均不证明未发起/服务端回滚，本适配不自动重发未知事务。原DB权威未能给出最终事实时保持Unknown与原日志，通知查原操作；不擅查pg_stat_activity或改技术ledger来编造确认。Unknown/in-progress保留journal并阻断该operation后续sequence，允许无关已获配额只读。冲突/损坏保留工件并报OperationConflict/ExportIncomplete，不跳过后继续写。已确认技术终态、原资源实际归还且业务结果核验一致后可移除本Owner这条可再取得的恢复输入；不清空root、业务记录、用户配置或未知条目。Dispose排空自己的锁/IO后关闭；pending在重启仍保留。

IntentWrite首先按固定事务锁scope容量/原receipt/head。原receipt存在且RequestHash相同返回原Saved；异hash冲突。新建intent_id=原operation UUID D、ExpectedRevision=0；更新核精确Saved.Identity及expectedRevision、原Owner/共享授权，不接受任意覆盖。Proposed由适配在执行事务前以原request和expectedRevision构造（更新修订+1，checked）；SQL仍在锁/CAS内验证其前置原revision，不能以预读替代CAS。head/revision/receipt与容量四mutation同commit，无receipt时才全变更；逐项验向量见上表。

Saved.Identity.Namespace固定 `asun.query.intent`、Id为intent_id、Revision为正十进制。内容摘要domain=`Asun.Query.SavedIntent/v1`，顺序为Identity.Namespace/Id/Revision、CatalogVersion、Intent、PreferredExport、Name、OwnerId、SharedScopes，排除Identity.Sha256及所有回执字段；SharedScopes按Ordinal排序去重后保存，完整新Saved.Identity.Sha256为上述摘要。新建OwnerId=受信SubjectId；更新OwnerId保留原值，共享写须明确授权，不夺取所有权。receipt_id=`qry-intent/<operation UUID D>`；IntentWriteReceipt本身无ReceiptId，Core将该确定ID写原OperationStatus.ReceiptId，不能另造公开返回类型。codec先核完整Saved schema/hash再交付；回滚无新修订，Unknown不填Saved，原IntentReceiptV1/技术receipt联合核验后恢复。旧修订永远原字节；迁移用B.3显式映射及新revision，不改历史。

### C.4 格式、metadata和清单的确定输出

完整Profile `QueryTypedJsonLinesV1` 使用C.1 context：第一条记录为metadata，其后才为row/aggregate。UTF-8无BOM、LF、无缩进/多余空白，属性按以下固定顺序；名称用小写camelCase、enum写B.1成员名称，数字Scalar.canonical始终JSON字符串。JSON字符串按Unicode标量扫描，未配对surrogate拒绝；quote/backslash分别写 `\"`/`\\`，BS/FF/LF/CR/TAB用短escape，其余U+0000..001F写小写hex `\u00xx`，其余合法标量直接严格UTF-8（不trim/normalization/HTML escape）。用Utf8JsonWriter显式写属性；字符串辅助生成上述合法字面量后以校验开启的WriteRawValue写入，不能依赖默认反射/encoder顺序。decimal/大整数不经double。

- metadata顺序：recordKind=`metadata`、formatVersion（完整VersionRef）、semanticHash、snapshot（完整SnapshotRef）、intent（EffectiveIntent全部字段）、fields（FieldDescriptor全部字段，按下文唯一构造顺序）、budgetProfile、scope、sourceRows、outputKind=`row|aggregate`。context不含scope/sourceRows，所以编排将这一记录作为目标WriteAsync的首块生成，**不交给格式适配器猜**；format只编码typed records，context为schema/预算依据。metadata写后暂不checkpoint，首完整数据记录检查点包含metadata prefix；空数据EOF后也须flush并完成清单。XLSX/CSV metadata放 `metadata.json`，通过C.1对象目标写，同样受预算/核验。Budget只公开Profile版本与声明上限，不导出身份token/本机路径/guard secret。
- row顺序：recordKind=`row`、identity、cells、sortKey、evidence。SourceRef依声明namespace/id/revision/sha256；Cell依fieldId/state/value/reasonKey；Scalar依kind/canonical；nullable值写null，数组严格保留声明序，不省略Null/Unknown原因。身份不是字节附件摘要。
- aggregate顺序：recordKind=`aggregate`、group、values；AggregateValue依outputId/state/value/exact/projection/validCount/missingCount/reasonKey；Exact依numerator/denominator，Projection依canonical/scale/isExact/policyId。空组写[]，源计数不替组数；格式不自行创建Projection。
- manifest.json顺序依B.1 ExportManifest字段声明的camelCase，ReceiptId整个属性省略；VersionRef依id/revision/sha256，SnapshotRef依executionId/handle/semanticHash/sources/authorizationPolicy/expiresUtc。handle只允许不授权限的不透明query引用，不是数据库/证据句柄或秘密。时间按UTC `yyyy-MM-ddTHH:mm:ss.fffffffZ`；非Scalar整数字段按不带引号十进制、boolean小写。实际清单文件byte hash与§4.4 canonical语义摘要分别核验，回执绑定后者，不将两种hash混称同值。

context.Fields普通行按EffectiveIntent.Fields顺序；聚合按GroupBy顺序，再按Aggregates声明顺序添加非空FieldId并去重（已在GroupBy者不重复），CountRows无输入字段；每个Id精确取当前目录FieldDescriptor，不按显示标题或字典遍历排序。metadata与context采用同一Fields。metadata中scope来自原ExportRequest，sourceRows为完整匹配源计数；普通不带附件的流式行导出在EOF前未知总数，因此metadata.sourceRows写null，并以manifest.Rows精确记录源行数；聚合和附件预扫描已有完整计数则写精确值。不得为了填header强制普通行预先全扫描；未知不会冒充0。Intent/FieldDescriptor完整嵌套字段按B.1/B.2声明顺序、上述基本类型规则显式编码，Condition用nodeKind=`logic|leaf`后各record声明字段；QueryCatalog自身摘要/canonical仍按§4.4，JSON不替代hash协议。Q-C3旧普通行夹具无metadata只测基础入口，完整Profile的header/附件/格式是新增范围，不能冒称旧Golden覆盖。

CSV Profile首发固定 `QueryCsvStrictV1`：UTF-8无BOM、逗号、CRLF、每个字段都双引号包围、内部quote加倍，不trim；表头为稳定FieldId/OutputId派生键，不用本地化显示名。为每个Cell写 `f<index>.state/kind/value/reasonKey` 四列，源身份四列在前，SortKey及Evidence按上述紧凑JSON各占一列；聚合按GroupBy顺序写 `g<index>.state/kind/value/reasonKey`，再按Aggregates声明序写 `a<index>.outputId/state/kind/value/exact.numerator/exact.denominator/projection.canonical/projection.scale/projection.isExact/projection.policyId/validCount/missingCount/reasonKey`。普通行源身份列固定 `identity.namespace/id/revision/sha256`，然后按Fields的f列、`sortKey`、`evidence`；聚合没有伪identity/sortKey/evidence列。每个不存在子对象的全部子列写NullMarker，Present的空字符串写EmptyMarker；count/scale用十进制，boolean用true/false，元数据按此顺序列出稳定列键→实际FieldId/OutputId，不靠标题反推。nullable值用Profile.NullMarker，Known空文本用EmptyMarker；两个marker非空/不同，Known值与任一marker相等直接QRY_EXPORT_FORMAT_REJECTED，不能无提示碰撞。字段列表/单位/时区/列映射放metadata.json，UtcTicks原值保留canonical；另附显示时间不替原值。首字符/去除前导Unicode空白后的首字符为= + - @ TAB CR LF或其全角变体时Strict拒绝，含引号/逗号仍正确quote；包括负数canonical也可拒CSV并给TypedJsonLines/XLSX选择，不能暗加apostrophe/Strip。只要消费Profile要求不同分隔/保护规则就新增明确版本，不套CsvHelper默认转换。

XLSX首发固定 `QueryXlsxTextV1`，与CSV相同稳定列映射，所有数据值按**字符串单元格**写（包括长整数/decimal/UTC/状态/Exact），不写公式/URL/外部关系。使用安装25.2.3的 `DevExpress.Export.Xl.XlExport.CreateExporter(XlDocumentFormat.Xlsx)` → `IXlExporter.CreateDocument(Stream)` → `IXlDocument.CreateSheet()` → `IXlSheet.CreateRow()` → `IXlRow.CreateCell()`；`IXlCell.Value`赋予新XlVariantValue的TextValue，不用FromObject失败变empty。cell/row/sheet/document按逆序Dispose，临时Stream最后flush关闭；公式parser不注入。单sheet最多1048576行（含表头）/16384列，单文本32767 UTF-16 units；本Profile不自动拆sheet或截断，N+1在写前拒绝并建议TypedJsonLines。每个业务值按schema可还原，不以Excel numeric/date精度替原值。

XLSX先在本操作受控scratch的CreateNew临时文件中流式形成完整容器，预算写入包装Stream强制累计/大小/deadline检查；不用整Workbook常驻内存，不用内存ZIP再ToArray。库自身缓冲必须在资格测试测峰值并受context.MaxBufferBytes约束，无法证明则该Profile NotReady，不声称流式API自动保证内存。MaxSpoolBytes是Core预留的本次临时盘额度，scratch与目标staging同时存在时按两份实际空间核预算；每条记录/库写入前核ct，同步库调用期间Root仍强持原encoder/scratch，不用WaitAsync后关闭它。容器闭合后才按≤64KiB传输块回送；中间块CompleteRows=0/LastKey=[]/FinalBlock=false，最后块CompleteRows=完整输出数/LastKey=[]/FinalBlock=true（末块可空）。这是封闭容器transport，不是可恢复记录；任何行级CheckpointAsync均拒绝XLSX，Publish必须证明源EOF、容器关闭和全部bytes核验。原ID恢复只在NotPublished/旧writer已死且原预算足够时重建，不append半ZIP。

行式TypedJsonLines/CSV每块最多一个完整数据record≤4MiB，LastKey完整，终块0行/空锚/FinalBlock=true；CSV header/metadata不计CompleteRows。Core预约MaxBufferBytes和MaxSpoolBytes前计现有seen/group/closure/queue/目标占用，二者正有限且总预约不超过原MaxTemporaryBytes；QueueBlocks/QueueBytes不因格式变更扩大。MaxBytes累计实际编码/附件/metadata/清单及恢复验证IO（重读也累计），MaxTemporaryBytes限制同时实际内存/临时盘保守和；清单ContentBytes仅实际对象长度之和，不能把IO重复计入文件长度。metadata与manifest各≤16MiB严格UTF-8，先有界逐字段核量再编码，不在超限后才ToArray；它们是输出协议限额，输入仍受8MiB请求/4MiB目录限制。所有binding/checkpoint/publication控制文件也累计字节/临时空间，不排除小文件；读回验证同样计原IO预算。

主要数据对象role=`query.data`，Identity.Namespace=`asun.query.export`、Id=`<operation UUID D>/data`、Revision=Format.Version.Revision、Sha256=实际数据字节摘要；Format为对应版本。metadata sidecar的Id末段metadata、role=`query.metadata`，附件保留原Identity/Role，但Role不得冒充query.data/query.metadata保留角色，同完整身份与自生成对象碰撞直接拒绝。Objects顺序data→metadata（如有）→附件完整identity canonical顺序；均ContainsBytes=true。manifest不是自身Objects成员，故不循环hash；Omissions只列Profile明确不包含的可选角色；IncludeEvidenceBytes=false时仍保留逐行Evidence引用，其对应ExportObject如列出须ContainsBytes=false/长度与内容hash来自Owner，不能伪造0长度/hash。完整Profile本版不在Objects列无实际描述的外部引用，Omissions用已登记角色代码表示未附原件，详情仍在data.evidence。任一请求必需角色缺失不能通过Omissions掩盖。空导出仍有有效数据header/格式空容器、精确Rows=0及实际对象hash；已确认回执后公开Manifest才附ReceiptId。

### C.5 同卷目标、真实排空与恢复装配

生产目标 `Asun.Modules.Query.Adapters.QueryDiskExportTargets` 实现IExportObjectTargetPort/IAsyncDisposable，其lease实现IExportObjectLease。公开配置及唯一构造如下，Host显式绑定受信identity/授权和目标政策，不造第二receipt数据库：

```csharp
public sealed record QueryDiskTargetRegistration(string TargetId, string AbsoluteRoot,
    VersionRef Policy, long MaxTemporaryBytes, long MaxExportBytes,
    TimeSpan RecoveryCallBudget, int MaxConcurrentLeases);
public sealed record QueryDiskTargetOptions(
    ImmutableArray<QueryDiskTargetRegistration> Targets,
    int MaxControlFileBytes, int MaxCheckpointFiles);
public sealed record QueryDiskBindingRecord(string OperationId, string RequestHash,
    QueryIdentity Owner, string TargetId, VersionRef TargetPolicy,
    VersionRef Dataset, string SemanticHash, SnapshotRef Snapshot,
    VersionRef Format, QueryBudget Budget);
public sealed record QueryDiskPublicationRecord(string OperationId, string RequestHash,
    string ReceiptId, string ManifestSemanticSha256, string ManifestFileSha256);
public sealed record QueryDiskCheckpointRecord(long Sequence,
    ExportCheckpoint Checkpoint, string CheckpointSha256);
// QueryDiskExportTargets(QueryIdentity trustedIdentity, QueryDiskTargetOptions options,
//     IAuthorizationPort authorization, TimeProvider clock)
```

容量/时长全为正且有限，MaxConcurrentLeases≤64、MaxControlFileBytes≤16MiB、2≤MaxCheckpointFiles≤4096；同TargetId重复/空/default/非绝对根拒绝；同一operation ID不得在不同Target根重复登记，恢复只在有限登记根中找原ID（多根同时存在则冲突），不扫描任意目录。实际operation额度=min(目标政策额度,原Budget剩余)，跨operation同时scratch/staging/控制文件计目标全局MaxTemporaryBytes，开始IO前原子预约。RecoveryCallBudget只限制只读状态验证，不能延长旧pipeline。Target根/ACL/volume由Host批准，TargetId只精确查登记表，不能从调用方任意路径生成。创建前核同卷volume identity、canonical根/最终parent链无未批准reparse/symlink；运行期间目标树ACL禁止不受信修改。无法保证这个信任模型拒绝目标，不能用一次字符串prefix承担TOCTOU，也不自行创建网络/跨卷生产目标。

每operation只有一个writer，锁固定在 `<root>/.query-locks/<operation UUID D>.lock`，FileShare.None且不随bundle rename；CAS运行主权先由Core取得，目标另核同原binding/独占锁，锁Task/handle在factory前预约槽。新实例恢复必须取得原锁并确认旧进程资源已死，锁忙不等于可接管。staging固定 `<root>/.query-staging/<operation UUID D>`、最终 `<root>/<operation UUID D>`，Root/固定子目录由Host授权本适配创建；ID只允许小写UUID D。binding.json按QueryDiskBindingRecord声明序/C.4 JSON原语写入，含实际原Owner但无cursor/guard/token/本机路径。主数据/附件CreateNew；只有证明原NotPublished/旧writer死亡和原checkpoint时才能重建本op半尾，不清理未知目录。

checkpoint流程固定：完整数据/完成对象Flush(true) → 以CreateNew写 `checkpoint.<sequence>.json.tmp` 并Flush(true) → 同卷不覆盖rename为 `checkpoint.<sequence>.json`。sequence是该staging lease的本地持久文件序号，从1开始checked递增（恢复从最大合法值+1），不是Core的OperationStatus.Sequence，B.2 Checkpoint参数不含它。文件内容按QueryDiskCheckpointRecord声明序/C.4 JSON写，CheckpointSha256=domain `Asun.Query.ExportCheckpoint/v1` 后完整ExportCheckpoint声明序canonical摘要，不包含wrapper/自身hash；文件名序号与wrapper必须相同，不覆盖已有同sequence。回读最多MaxCheckpointFiles，选择最大通过绑定/原budget/canonical/hash核验的sequence，重读数据prefix和CompletedObjects并重建hash，累计原预算；发现非法最新checkpoint不退回旧版本伪成功。首次创建按原Budget.MaxRows及MaxCheckpointFiles计算rowInterval=max(1,ceil(MaxRows/(MaxCheckpointFiles-1)))，使用有检查的整数商/余数而非浮点；每至少rowInterval个新完整输出记录落一次checkpoint，EOF再落最后一次（相同完整状态已落则不重复）。零行终块不覆盖最后完整LastKey，空数据只落Rows=0/LastKey=[]的EOF checkpoint。源码扫描数/累计IO/对象完成同原checkpoint记录；恢复保持相同interval与额度。容量仍满则停止新写并报预算错误，不无界增长或删恢复证据。TypedJsonLines数据prefix包括metadata，CSV/XLSX生产首版均不提供行checkpoint；取消/恢复只在确证NotPublished后按原ID/原预算重建。

PublishAsync先核全部对象、metadata与manifest；manifest.json无ReceiptId，其文件SHA与§4.4语义SHA分别验证。确定ReceiptId=`qry-export/<operation UUID D>`，预写publication.json（上述完整record）并Flush(true)，它不是manifest.Objects成员且不含自身hash。binding/manifest/publication全部flush，关闭本lease数据/控制文件后，将**整个bundle目录**不覆盖rename到正式目录；publication随同目录成为一次发布事实，不在rename后再写外部回执。Core在rename前持久PublishRequested/待发布Manifest，并完成审计/交付围栏；目标按ExportBinding原identity/dataset/semanticHash/字段及Request.Members构建Export最终授权Check/CommitDelivery（contentHash=清单语义SHA），并核Policy精确等于原Snapshot.AuthorizationPolicy后rename，不能刷新Policy或用旧GuardId跨取消/撤权恢复。若围栏先被撤权击败则不rename；rename已开始的取消保留Unknown至原IO返回，禁止删除已可能发布bundle。

QueryReceiptAsync仅只读核验原正式bundle的binding/publication/manifest及全部对象长度/hash，在固定数量/字节/RecoveryCallBudget内完成；预算不足/观察取消返回Unknown或对应错误，不宣称NotPublished。caller须匹配当前trustedIdentity；原Owner按Subject/Tenant/Scope/Purpose核验，允许已授权新Session回查。读取前以C.3精确操作对象做Recover核验，内容读出后再核dataset/hash当前权限；Core对交付另做审计/CommitDelivery。不rename、不补建文件、不写所谓“修复回执”。完全一致才Published并回确定ReceiptId/语义SHA，Core再CAS登记原OperationRecord；Core CAS未知不改变已确认文件发布事实，仍按原CAS技术ID回查。确证正式bundle不存在、旧writer已死且原staging身份完整才NotPublished；无记录/无观察权限不证明未发布。异binding报QRY_OPERATION_CONFLICT，缺件/损坏报QRY_EXPORT_INCOMPLETE并保留工件，不发布第二目录。已发布不再Create writer，CreateAsync与PublishAsync重复同ID只核原回执，异hash不覆盖。

最终范围授权沿用§5.4：CurrentPage/ExplicitMembers使用原Request.Members，AllMatching及聚合最终发布允许Members为空，**仅表示带semanticHash/完整Snapshot/Policy/清单摘要的固定全范围交付**；不是通配授权，也不新增不存在的成员传递端口。逐源行/每块的当前授权与完整有序审计由Core在扫描/写入时完成，最终整体发布以清单摘要及源向量闭合。目标不重复取得全源，也不另存无界成员账本。QueryReceiptAsync恢复只返回原Receipt/Manifest摘要；Core新交付Manifest时审计该精确清单与原scope，DeliveredMembers为空（这次不重发源行）。原行/块审计保留可追溯关系；后续实际下载仍须宿主按相同scope/来源/字段核当前完整内容授权，不拿查回执许可自动授予下载权。

文件系统断电耐久/rename资格必须真实故障测试，Flush(true)/Directory.Move教程不证明设备耐久。Core Root唯一拥有源/证据资源；目标Publish关闭自己的文件不关闭仍在用的源/证据lease，锁保持到该lease实际Dispose。原Flush/rename/验证Task不因取消观察而Dispose。Host顺序：关闭UI接纳并收取BindingRoot → Close/Dispose QueryService与IntentService → 排空Adapters自有Owner → Dispose Host拥有的持久端口/IM-066 Runtime。已发布bundle保留清理由独立策略执行，不从取消/Unload触发。

### C.6 WPF草稿、显示列、状态和三语资源

本节补§10已接收的U1软件接点，不新增产品页或viewport装配。证据只通过IQueryViewHost.OpenEvidenceAsync；宿主负责040/041/viewport的真实预览与权限，不在query重复解码/缓存像素。模块本身不直接消费viewport bridge，不能把该bridge的运行验收列为query Core门。

Wpf本地ConditionDraftNode冻结为可编辑class（INotifyPropertyChanged）：Guid NodeId、Guid? ParentNodeId、LogicKind? Logic、string? FieldId、CompareOp? Operator、ImmutableArray<Scalar> Values。Logic非null只允许逻辑节点且FieldId/Operator空、Values空；Logic空为叶且FieldId/Operator必填；Values的合法个数/Kind按§4.2。每次编辑先校验节点唯一/恰一个根/parent存在/无环/深度≤32/总节点≤1024（与Core同有效域，不另缩窄已保存条件），再按树生成B.1 LogicNode/LeafNode；子序以当前可见编辑序交Core规范化，NodeId不进hash。空DraftNodes=Condition null；多个根不能偷偷And。字段改变清旧Operator/Values后提示重新选择；IsNull/IsNotNull/IsUnknown切换清Values；一个叶的空Values不自动删节点，定位错误。时间草稿另含字符串文本、offset、timeZoneId/规则版本，宿主解析成UTC Scalar后才进入Values，DST歧义常显修复。

BudgetDraft冻结为只含B.1 QueryBudget可编辑值的local class：Profile只读；MaxScanRows/MaxRows/MaxBytes/MaxGroups/MaxTemporaryBytes及QueueWait/StatementTimeout/SnapshotTtl/SnapshotIdle/DrainObservation为有单位属性，全部按BudgetDescriptor联动上限；DeadlineUtc不让PropertyGrid编辑，点击执行时由Host批准duration与clock生成**一次**原deadline，同执行续页保留原值；导出可按§3.5/ExportRequest.Query建立其独立获批预算，但一经ExportAsync入场其恢复/重建均保留该导出原deadline/累计额度，不能在每次恢复刷新。Mapper深拷贝字段/条件/预算→QueryRequest，再Validate；变更Dataset/时间/条件/字段/Sort/Group/Aggregate立即IsDraftDirty=true、清cursor/禁翻页导出，旧已交付页保留但常显“条件已变”。执行权限仍Core实时核验，草稿不改运行DTO。

```csharp
// 仅Asun.Modules.Query.Wpf，原typed数据仍为权威。
public sealed record QueryDisplayCell(string Text, string StateText, string? ReasonText);
public sealed record QueryDisplayRow(SourceRef? Identity,
    ImmutableArray<QueryDisplayCell> DisplayCells,
    QueryRow? RawRow, AggregateRow? RawAggregate);
```

VM的RawRows/RawAggregateRows保留当前合法结果；DisplayRows由单次纯mapper按当前QueryResult.FieldDescriptors/Rows.Cells顺序生成（聚合按GroupBy后Aggregates序），不重新按目录或标题排序，一行仅有RawRow或RawAggregate，组行Identity=null且不出现证据按钮。三语切换只重建Text/StateText/ReasonText，不调用Query/改变原值/排序/身份；数字/时间显示遵目录单位与当前culture，UTC/Exact原值可从显式“复制原值”操作获得，不把格式化投影写回Raw。当前撤权通知关闭交付、取消导航并清除控件内可见敏感Rows/DisplayRows/详情缓存；已合法外部交付不冒称召回。Detach旧代次无法填入新DisplayRows，任务仍按§10.3收敛。

GridControl.AutoGenerateColumns=`AutoGenerateColumnsMode.None`；逐个当前选择字段建立GridColumn，ColumnBase.Binding=只读Binding(`DisplayCells[<可信零基index>].Text`)，FieldName使用模块生成`c<index>`，Header取目录已授权资源；绝不把FieldId/用户输入拼成Binding.Path或反射产品对象。保存的列布局按FieldId精确映射，缺/撤权字段丢弃该显示布局项并提示，不修改查询条件。Grid在有限LayoutPanel高度内，不包外层无限ScrollViewer；当前页≤1000，默认8列，不提前生成1000×256个WPF元素，不一次加载证据。TableView禁本地Sort/Filter/Group/Summary，用明确查询命令改变全范围意图；真实1920×1080/DPI/键盘/UIA测布局/虚拟化峰值，不能凭静态XAML称通过。

稳定resourceKey逐文本使用，不在VM硬写中英文；下面冻结关键状态/恢复文案，§10原表只是显示意图，不另成第二份键表。命令键包括 Query.Command.Query/Cancel/Export/Previous/Next/Save/Load/Migrate/OpenEvidence/CheckReceipt/CopyRaw；label键采用 `Query.Label.<语义>`，每个实际label/tip/error均有zh-CN/zh-TW/en-US资源。各QRY_*错误的Code/Recovery分别为 `Query.Error.<code>` 与 `Query.Recovery.<code>`，SafeArguments只带脱敏定位/限额，用资源模板替换，不显示raw exception或生产路径。缺键回退zh-CN并记diagnostic，不能静默空白。下面资源与所有命令/错误键在Wpf.Tests通过三语枚举覆盖，不为文档制造尚不存在的资源工程。

| 稳定资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Query.Command.Query | 查询 | 查詢 | Query |
| Query.Command.Cancel | 取消 | 取消 | Cancel |
| Query.Command.Export | 导出 | 匯出 | Export |
| Query.Command.Previous | 上一页 | 上一頁 | Previous page |
| Query.Command.Next | 下一页 | 下一頁 | Next page |
| Query.Command.Save | 保存查询 | 儲存查詢 | Save query |
| Query.Command.Load | 加载查询 | 載入查詢 | Load query |
| Query.Command.Migrate | 迁移查询 | 移轉查詢 | Migrate query |
| Query.Command.OpenEvidence | 查看原件 | 檢視原件 | Open evidence |
| Query.Command.CheckReceipt | 查回执 | 查回執 | Check receipt |
| Query.Command.CopyRaw | 复制原值 | 複製原值 | Copy raw value |
| Query.State.Empty | 无数据 | 無資料 | No data |
| Query.State.Loading | 正在查询 | 正在查詢 | Querying |
| Query.State.Cancelling | 正在取消 | 正在取消 | Cancelling |
| Query.State.Cancelled | 已取消 | 已取消 | Cancelled |
| Query.State.Dirty | 条件已变，请重新查询 | 條件已變，請重新查詢 | Filters changed. Run the query again. |
| Query.State.Expired | 查询已过期，请重新查询 | 查詢已到期，請重新查詢 | Query expired. Run it again. |
| Query.State.AccessDenied | 无权查看，请联系管理员 | 無權查看，請聯絡管理員 | Access denied. Contact an administrator. |
| Query.State.ExportIncomplete | 导出未完成 | 匯出未完成 | Export incomplete |
| Query.State.AwaitingReceipt | 操作回执未确认，请查回执 | 操作回執未確認，請查回執 | Operation receipt unknown. Check its status. |
| Query.State.DrainUnknown | 操作尚未结束，请等待资源归还 | 操作尚未結束，請等待資源歸還 | Operation is still active. Wait for resources to return. |
| Query.Value.Null | 无值 | 無值 | No value |
| Query.Value.Unknown | 未知 | 未知 | Unknown |
| Query.Value.Missing | 缺失 | 缺失 | Missing |
| Query.Value.Unavailable | 暂不可用 | 暫時無法使用 | Unavailable |
| Query.Value.Invalid | 数据无效 | 資料無效 | Invalid data |
| Query.Export.GroupPageUnsupported | 分组结果请选择全量或明确源成员 | 分組結果請選擇全量或明確來源成員 | Choose all matches or explicit source members for grouped results. |

### C.7 本范围定向验收断言

复用§12/§17现有Golden/反例，新增范围的实现断言归唯一Adapter.Tests/Wpf.Tests；本次只冻结输入/输出与失败条件，未写测试工程/运行成绩。

| 实现消费方 | 输入/动作 | 精确验收 |
|---|---|---|
| QueryStorageAdapter | 同Cut跨两页期间新提交/旧修订变化；低ID迟到；缺历史段；Or中时间条件 | 原Cut成员不变；缺段整体RevisionMismatch；Or时间不能被错误下推；不生成任意SQL；候选ScanLimit N+1失败，不报完整页/计数 |
| projection codec | UInt64.MaxValue、100ns UTC边界、Null/Unknown混方向、代表UTF-16/大小写、零行非EOF/重复锚 | 全域无损且与Core全序逐值一致；不能证明比较器的variant拒绝；坏schema/锚停进/错误EOF整体退化或后端拒绝，无无限轮询 |
| QueryHandleCursorAdapter | 非canonical Base64url/异实例/到期/entry满/同句柄碰撞/已释放Snapshot | 固定71字符；先拒无效句柄；不驱逐活动绑定、不IO；容量错误不签发token；有效句柄仍经Core当前授权/源核验 |
| metadata adapter | 同ID同hash重复Reserve；CAS旧sequence；技术commit断连；日志完成后进程死亡；保存head写入后事务失败；共享scope变更 | 完整技术hash用IM-066 Compute，非payload裸hash；旧CAS不得覆盖；journal保留原identity/输入，Unknown或NotFound不重发；四mutation同commit或全回滚；CheckSave看完整共享列表，换实例读原结果 |
| 格式/对象目标 | 7/3精确值+投影；Known空串/Null/Unknown；quote/反斜杠/控制/Unicode；=1、前导空白、长整数；附件身份hash≠内容hash | 聚合原值/策略全保留；JSON字节/顺序固定；CSV风险拒绝不改值；XLSX真实string无公式；附件长度/hash核验且不按身份hash猜内容 |
| 容器/恢复 | XLSX最后Dispose前取消、末块未到、scratch超限、重复发布/rename后回执断连、半附件 | 未闭容器不得Published/行checkpoint；原Task实际归还才释放；超限整体失败；同原ID回查完整bundle仅一次Published；半对象不列CompletedObjects |
| 可选WPF | 1920×1080当前1000行/8列、FieldId含`.`/`[]`、三语长度、组当前页、撤权/旧证据迟到 | 索引Binding不把FieldId当路径；页面状态与scope清楚；组当前页禁选且解释；撤权清可见缓存；旧回调不回填且原Root仍持任务；真实UIA/键盘/峰值另验 |

本次内容自审按两条消费路径执行：普通程序员的类型→算法→失败/恢复→验收，以及宿主的注入→注册→源保持→执行→回查→关闭。内部设计不再列“后续Owner决定”；只保留§19事实/权限采纳、真实输入/目标和运行资格。未执行事项不以文档完整、上游资料或模拟端口替代。
