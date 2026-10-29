# 报告模板与输出渲染独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`R-C1, R-C2, R-C3`

- 模块：`reporting`（报告模板与输出渲染）
- 独立模块 ID：`IM-044`
- 指导版本：`0.3.3-prep`（2026-10-12）；Module API Contract：`v0.2`，本文件内唯一当前版本
- 来源迁移映射：`PKG-046`；其历史说明不构成第二实施权威
- 状态：整体 `DesignReview/Prep`；R-C1/R-C2/R-C3：`ModuleCoreImplementationReady`（主控2026-10-10接收，仅规格准备）；R-A1/R-A2/R-U1：指导内容已接收，资格仍 `PreparationIncomplete / NotReady`
- 适用基线：C# / .NET 10；可选 WPF / DevExpress 25.2.3；报告数据必须来自调用方批准的只读投影
- 规划消费者：生产单件报告、质量/批次报告、客户输出；第二消费者必须使用同一 Core 契约
- 全批准范围文档准备结论：可决定的软件设计闭合，含R-C1/C2/C3、R-A1/A2、R-U1；本轮原会话自审与定向文档验证见§15.4。它没有宣布实现、编译、真实输出、性能资格或生产验收已经完成。
- 工程准入：`NewProjectRequired`；未找到契约完全匹配的既有 Reporting Core。实现切片开始时创建 `src/Modules/reporting/Asun.Modules.Reporting.Core/`，测试放在 `tests/Modules/reporting/Asun.Modules.Reporting.Core.Tests/`，namespace 为 `Asun.Modules.Reporting`；根Owner及两个Host明确在 `Asun.Modules.Reporting.Hosting`。
- 图片、原始 2D/3D 数据、点云、高度场和视频只接受 IM-066 文件对象/证据引用，不存入数据库字段；报告侧只流式读取获准附件，并受独立的字节、解码、页数和暂存预算约束。

## Core implementation binding

上述工程路径是本模块唯一 Core 写入位置；仅在实现切片获准启动时创建。WPF/DevExpress、格式适配器、模板包和 ArtifactStore 实现属于显式适配器，不进入 Core。

## 1. 职责、目的和边界

模块负责把调用方提供的不可变报告输入绑定到受控模板，生成预览或输出文件，并报告每个产物的生命周期、来源和完整性。模块可以做模板布局、分页、显示格式、图表排版、格式编码、暂存、发布适配和输出审计；不能产生新的生产事实。

模块不得：

- 读取或写入制程私有表、Grid 当前行、实时 `DbContext`、设备服务或任意 SQL/网络 URL；
- 计算良率、Cp/Cpk、分母、缺陷判定、质量放行、复判结论或工艺阈值；
- 修改检测事实、统计快照、证据、程序、配方、工单或设备状态；
- 把预览、生成、打印入队、客户签署或输出登记当作设备动作或质量放行；
- 把 `Unknown`、缺测、无权限、未完整读取或空字符串转换成 PASS、零、空结果或已完成；
- 维护第二套权限、报告事实库、统计 Schema、快照库、输出持久化主库或全局“当前报告”；
- 将 DevExpress 控件、WPF Dispatcher、页面 ViewModel 或窗口生命周期作为 Core 的启动条件。

调用方负责用途、目标/批次关联、数据查询与快照、权限决定、统计和工艺解释、最终质量决定、签章/打印政策、设备副作用以及产物持久化 Owner。模块只消费这些 Owner 的公开端口。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Reporting.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"不将 WPF Dispatcher 或页面 ViewModel 作为 Core 的启动条件"，Core 在无 WPF 宿主中完整运行。

**Blazor/Web**：报表是 Web 端 P2 优先需求。报表渲染在服务端执行，浏览器只展示渲染结果（HTML/PDF）；报表导出通过 HTTP 下载，不通过 SignalR。多机台对比报表经 `query` 模块数据，浏览器不直接访问数据库。

**AI 报表集成**：AI 推理的自动判定率/人工介入率/漏检误检统计进入质量报表；本模块从 `statistics`/`inspection-evidence` 读取这些聚合指标，不直接调用 `ai-inference`。

**HALCON 不适用**：本模块是纯报表渲染，不执行视觉算法；HALCON 备选 CI 不涉及本模块。

## 2. 分层、依赖和实现切片

依赖方向为宿主 → Core/可选 WPF → 显式适配端口；DevExpress Adapter → Core。Core 只引用 .NET BCL，不引用 WPF、DevExpress、AsunImage、产品 Shell、数据库或 SDK。调用方的事实/统计/权限/存储 Owner 不移交给 reporting；端口只映射其公开能力。`SnapshotId` 和范围声明是上游事实，不是 reporting 自证的完整性。

| 切片 | 完整责任与真实消费者 | 注入边界 |
|---|---|---|
| R-C1 | 类型、验证、规范编码、模板布局校验、能力协商；单件报告服务和批次质量工具共用 | 不做 IO；上游 DTO 映射另门 |
| R-C2 | 幂等接纳、有界调度、分页读取、流式完整性、三语固定、渲染及文件对象端口组合、资源账本、事件 | source/catalog/localization/auth/files/store/renderer/verifier/resource-meter/diagnostics；先以 Simulator 验证全部状态 |
| R-C3 | 多格式独立发布、原 ID 查询、Unknown 对账、部分成功、撤权、重启恢复、关闭及迟到排空 | 注入 Store 与文件租约；Simulator 可验证，真实持久化/权限 Owner 另门 |
| R-A1 | DevExpress 25.2.3 受控布局、PDF/版式 XLSX/DOCX/HTML/逐页 PNG、预览文件 | 本机程序集；完整内容不得依赖控件自动取源 |
| R-A2 | CSV/数据 XLSX 类型化输出及格式结构核验 | 固定行流；XLSX 消费本机 Spreadsheet 已冻结公共 API；真实格式/读回资格另门 |
| R-U1 | 可嵌入报告工作台、只读预览、产物/范围/错误联动、三语与键盘 | WPF、实例 presenter、已授权预览租约；不代替产品页面 |

报告不执行视觉算法。HALCON/AsunImage 不适用，不做算子比较。图像、视频、点云和高度场只使用硬盘文件对象的引用和受控流，不写数据库 BLOB、不扫描 AsunImage 内部、不重新量测。只接受上游已批准的可显示 PNG/JPEG 证据副本；3D/视频原件可作为引用列出，渲染模块不负责转换。

## 3. Module API Contract v0.2：公开形状与有效域

本节冻结模块自身契约；平台 C-02/C-04/C-05/C-07 只映射，不作为 Core 的编译依赖。本节代码块是**公开声明规格**，分块合并时使用 `namespace Asun.Modules.Reporting;` 及 `System`、`System.IO`、`System.Collections.Immutable`、`System.Threading`、`System.Threading.Tasks`。实现方法体尚未编写，不声称已编译。全部集合接纳时复制为不可变集合；禁止借用可变字典、业务对象、委托表达式、DbContext 或延迟 SQL。

### 3.1 身份、值、范围与统计

```csharp
public readonly record struct ReportIntentId(string Value);
public readonly record struct TemplateRevisionId(string Value);
public readonly record struct SnapshotId(string Value);
public readonly record struct ArtifactId(string Value);
public readonly record struct FileObjectId(string Value);
public readonly record struct UnitId(string Value);
public sealed record SourceRevision(string OwnerId, string Revision, string Sha256);
public enum ReportFormat { Pdf, LayoutXlsx, DataXlsx, Csv, Docx, Html, Png }
public enum RenderMode { Preview, Publish }
public enum DataViewMode { FixedSnapshot, ExplicitRealtimePreview }
public enum ReportFieldType { Text, Integer, Decimal, Boolean, UtcInstant, Duration,
    Enum, Identifier, EvidenceReference }
public enum ReportValueValidity { Valid, Unknown, Missing, NotApplicable, Invalid }
public abstract record ReportScalar
{
    public sealed record Text(string Value) : ReportScalar;
    public sealed record Integer(long Value) : ReportScalar;
    public sealed record Decimal(decimal Value) : ReportScalar;
    public sealed record Boolean(bool Value) : ReportScalar;
    public sealed record Timestamp(DateTimeOffset Value) : ReportScalar;
    public sealed record Duration(TimeSpan Value) : ReportScalar;
    public sealed record EnumValue(string ContractId, string Key) : ReportScalar;
    public sealed record Identifier(string Value) : ReportScalar;
    public sealed record Evidence(FileObjectId ObjectId) : ReportScalar;
}
public sealed record ReportField(string Name, ReportFieldType Type, UnitId? Unit,
    int? Scale, bool Required, SourceRevision Source);
public sealed record ReportValue(ReportFieldType Type, ReportScalar? SourceValue,
    string? DisplayValue, UnitId? Unit, ReportValueValidity Validity, string? ReasonKey);
public sealed record ReportRow(string StableKey, ImmutableDictionary<string, ReportValue> Values);
public sealed record RangeProof(string OwnerId, string ProofId, string ProofSha256,
    SnapshotId Snapshot, string ScopeId, SourceRevision Query, string SortContract,
    long ExpectedCount, string RowsSha256, bool Complete);
public sealed record EvidenceReference(string EvidenceId, FileObjectId ObjectId,
    string Sha256, long ByteLength, string MediaType, int? PixelWidth, int? PixelHeight,
    bool Required, SourceRevision Source);
public sealed record ReportPartInput(string PartId, SourceRevision DataContract,
    ImmutableArray<ReportField> Fields, RangeProof Range,
    ImmutableArray<EvidenceReference> Evidence);
public sealed record SummaryMetric(string Key, ReportValue Value, string MeaningKey);
public sealed record CountPartition(ImmutableArray<string> MemberKeys, string TotalKey,
    string RelationProofId); // 只校验上游显式声明的闭合关系
public sealed record ReportSummaryProjection(string SummaryId, string ScopeId,
    SnapshotId Snapshot, SourceRevision Method, string DenominatorPolicyRevision,
    string RelationProofId, bool Complete, ImmutableArray<SummaryMetric> Metrics,
    ImmutableArray<CountPartition> Partitions);
public enum ProjectionErrorSeverity { Information, Warning, Error }
public sealed record ReportErrorProjection(string ErrorId, string StageKey,
    string CategoryKey, string MessageKey, string? DetailSha256, string AffectedScopeId,
    ProjectionErrorSeverity Severity, bool Retryable, SourceRevision Source,
    DateTimeOffset OccurredUtc);
public sealed record ReportInputClosure(string PurposeId, string ConsumerId,
    SnapshotId DataSnapshot, DataViewMode ViewMode, SourceRevision Query,
    string ScopeId, string ScopePolicyRevision, ImmutableArray<ReportPartInput> Parts,
    ImmutableArray<ReportSummaryProjection> Summaries,
    ImmutableArray<ReportErrorProjection> Errors, TemplateRevisionId Template,
    string TemplateSha256, string LanguageTag, SourceRevision Localization,
    string TimeZoneId, string UnitProfileId, SourceRevision Renderer,
    DateTimeOffset AsOfUtc);
```

`PurposeId` 使用宿主登记的稳定键（如 `SingleInspection`、`BatchQuality`、`CustomerOutput`、`EngineeringReplay`），不是固定工艺枚举。`LanguageTag` 使用资源 Owner 支持的 BCP-47 标签，首版必含 zh-CN/zh-TW/en-US；增加语言不改 Core 枚举。时区由宿主传已解析的稳定标识及资源版本，未知时区拒绝，不退回本机时区。

统计分类属于统计 Owner。`Metrics` 可含通过、不通过、复判通过、Unknown、Incomplete、分子、分母、已算比例及资格；不强迫分类互斥。只有 Owner 提交 `Partitions`（成员key无重复且不含TotalKey，必须存在、皆Valid Integer）时，Core 才检查指定 Integer 值非负及求和等于指定 Total（checked Int64，溢出拒绝）；没有声明就不猜关系、不加总、不算比例、不发明分母。例：最终 Pass=4，ReviewPass=2 是 Pass 的子集，两者重叠合法；不能要求 Pass+Fail+ReviewPass=Total。关系证明由 source 端口确认来自固定的上游快照，单独 `Complete=true` 不能赋予事实真实性。

| 字段族 | 有效域、缺失与校验 |
|---|---|
| 所有身份/稳定键/版本/Owner/资源键 | 非空；1..128 UTF-8 字节；不得含 NUL、控制字符；Ordinal 比较，不 trim、不大小写归一；UnitId 为1..32 ASCII；文件建议名另见下表 |
| SHA-256 | 恰64个小写十六进制字符；指向实际规范字节或文件内容；未知 hash 不用全零代替 |
| 集合 | 非 default；可为空者为 Errors/Summaries/Evidence/Partitions；Parts 至少1；part、field、metric、row key 在对应范围唯一；无 null 元素 |
| 字段与值 | Type 必须等于字段声明和 scalar 变体；valid 的 SourceValue 必需，Unknown/Missing/NotApplicable/Invalid 必须无 SourceValue 且有 ReasonKey；空 Text 是合法原值，不等于 Unknown |
| 显示与单位 | DisplayValue 可缺，仅从批准的资源/格式规则生成；已有显示值原样输出并保留原值；Unit 与字段一致，Scale 为0..28且只用于Decimal显示；不换算、不重判 |
| 时间/时长/数值 | 时间 offset=0；Duration >=0；decimal 使用 .NET decimal 原值，Integer 为Int64；禁止 double NaN/Infinity；完整计数 >=0 |
| 范围 | 每part的Snapshot/Scope/Query与闭包一致，SortContract为上游稳定排序版本；RowsSha256含有序完整行集合；证明须经source核验，重复、缺页、改行全部拒绝 |
| Evidence | ObjectId不是路径/URL；ByteLength>=0；只读图片要正的尺寸；媒体类型精确比对；总解码像素及字节另受预算；原3D/视频不传字节到数据库 |
| 错误投影 | 稳定stage/category/message键、UTC时间、范围、来源；原检测ERROR/运行错误/人工意见不可合并为质量决定；只提供脱敏详情hash |

### 3.2 预算、模板与请求

```csharp
public sealed record ReportBudget(long MaxRows, int MaxColumns, int MaxPages,
    int MaxImages, long MaxInputBytes, long MaxDecodedImageBytes,
    long MaxWorkingBytes, long MaxTempBytes, long MaxOutputBytes,
    int PageBatchRows, int MaxBufferedPages, int MaxTextUtf8Bytes,
    TimeSpan QueueTimeout, TimeSpan RenderTimeout, TimeSpan PublishTimeout);
public sealed record ReportingOptions(string ProfileId, SourceRevision Profile,
    SourceRevision CoreRevision,
    ReportBudget Ceiling, int MaxActiveOperations, int MaxQueuedOperations,
    int MaxObservers, int EventCapacity, TimeSpan CloseObservationTimeout);
public sealed record RenderRequest(string ContractVersion, ReportIntentId IntentId,
    ReportInputClosure Input,
    ImmutableArray<ReportFormat> Formats, RenderMode Mode, ReportBudget Budget,
    string? SuggestedFileName, string RequesterId, string AuthorizationScopeId,
    string RequestContentSha256);
public enum LayoutNodeKind { Literal, Field, Metric, Evidence, ErrorList }
public sealed record LayoutNode(string NodeId, LayoutNodeKind Kind, string Key,
    string? PartId, bool Required, decimal WidthMm, decimal HeightMm);
public sealed record TemplateDefinition(TemplateRevisionId Id, SourceRevision Source,
    string SchemaVersion, ImmutableArray<string> PurposeIds,
    ImmutableArray<ReportFormat> Formats, decimal PageWidthMm, decimal PageHeightMm,
    decimal MarginMm, string FontResourceId, decimal FontSizePt,
    ImmutableArray<LayoutNode> Header, ImmutableArray<LayoutNode> Detail,
    ImmutableArray<LayoutNode> Footer, ImmutableArray<EvidenceReference> Resources);
public sealed record LocalizationData(SourceRevision Source, string LanguageTag,
    ImmutableDictionary<string,string> Texts, string DecimalSeparator,
    string DateTimePattern, string UnknownText, string MissingText,
    string NotApplicableText, string InvalidText, string EmptySetText);
public sealed record FormatCapability(ReportFormat Format, SourceRevision Adapter,
    bool SupportsPreview, bool SupportsPublish, bool UsesBoundedInput,
    bool ProducesPageSet, ImmutableArray<LayoutNodeKind> NodeKinds);
public sealed record ValidationIssue(string Code, string FieldPath, string MessageKey);
public sealed record ValidationResult(bool Valid, ImmutableArray<ValidationIssue> Issues,
    string? CalculatedRequestSha256);
```

Renderer/source/File/Verifier装配必须把缓冲、解码/native及lease纳入注入IReportingResourceMeter，Core另计其队列/行批次/事件预约；Read为实时只读采样，不是额外事实Owner。读取抛异常或计量不全时按Complete=false记录并停止新的预算扩大，不能声称UsesBoundedInput或性能PASS；Simulator全部托管计量可确定。所有阶段先预约checked预算后分配，实际追加不得超过预约，无法遵守的适配器Capability拒绝接纳。资源计数未知用nullable值+Complete=false，不以0伪无泄漏；DrainUnknown仍记录保守预约字节，不能抹除容量。MaxRows对每次完整同源重读校验，InputBytes按所有读取实际传输累计，OutputBytes包括Document/Metadata/PreviewDocument，Temp包含source暂存及PRNX；重复读取不是免费流量。预扫描时规范请求/模板/资源字节计入InputBytes，集合数量须受该预算和总节点<=4096、part<=256、summary<=256、error<=100000、每summary metric<=2048、资源<=100000的技术封顶约束，先计数后复制。超大请求形状直接拒绝，不能先规范编码分配无界字节。

预算必须显式提供，无隐含100k行/10min默认值。ReportingOptions 由宿主 Profile 冻结，任务预算只能收紧 Ceiling。所有字节/计数为正，MaxImages可0，MaxRows可0（合法空集），MaxColumns为1..2048，PageBatchRows为1..4096，MaxBufferedPages为1..64，MaxTextUtf8Bytes为1..1MiB；这些上界是模块防止整数/批次失控的技术限制，不是客户 SLA。MaxRows/MaxInputBytes/MaxTempBytes/MaxOutputBytes等为Int64且累加 checked；页数/列数/图数为Int32且 checked。MaxDecodedImageBytes按 width×height×4 及实际解码额外缓冲累计预约；MaxWorkingBytes包含source批次、解码、渲染器和事件缓存，只有计量完整的适配器才可声明UsesBoundedInput。期限均>0且<=24h，单调时钟；时间到不代表资源释放。队列/活动/订阅上限为1..1024，EventCapacity为16..65536。拒绝无Profile预算，不从模板放大资源。

模板 v0.2 是本模块 `TemplateDefinition` 的受限声明式布局，SchemaVersion=`report-layout-v2`。不接受任意 REPX/XML、自定义类型、脚本、对象数据源、SQL、URL、表达式/反射或函数。Catalog 先对原始定义hash及信任/用途/闭包负责，Core再校验节点：Literal.Key为资源键；Field.Key为Part字段；Metric.Key为summaryId/metricKey；Evidence.Key为已登记EvidenceId；ErrorList.Key固定为`errors`。不允许公式/分组计算或隐式子模板；子模板在资产发布阶段展开为有hash的扁平定义，运行时无外部递归加载。Header/Footer只允许Literal/Metric；Detail允许全部5类。按数组顺序排版；Header/Footer分别是ReportHeaderBand/ReportFooterBand的报告级节点，只在整份报告开头/结尾出现一次，不是PageHeader/PageFooter；跨part仍只一次。每part字段表按固定输入顺序、Metrics/Errors/Evidence说明在Footer前，Footer一次；不按字段字符串推断工艺。Detail中Evidence节点的PartId必需且Key属于该part证据，ErrorList只可单独说明段；Literal/Metric不得设置PartId，Field必需PartId；错误/汇总/证据一律另列追加页，顺序为Parts输入序、summary数组序、Errors数组序。重复NodeId/不存在键拒绝。图表只能消费上游已生成的受控图片证据及说明，本模块不新增统计计算。模板编辑/审批仍归资产Owner；任意REPX导入需独立转换/审查任务，不能作为正式运行fallback。

布局参数是显示几何，不是计量单位；纸张100..1000mm；MarginMm为0..50且双边小于纸张；节点Width/Height>0并不超可用区域；FontSizePt=6..36；字体必须是宿主Profile已加载的精确字体映射（FontResourceId），映射登记字体文件SourceRevision；模板Resources不允许运行时安装字体，缺字/缺字体拒绝，不静默换字体。版面字段宽按Detail的声明比例使用可用纸宽，长文本换行，不截断；单行跨页、表格字段列标题重复和证据附页由格式适配器按此规则资格验证；跨页重复的是字段列标题，不重复报告级Header/Footer。节点全部落在已声明字段/资源/用途内，未知Kind拒绝。原值、Unknown原因、范围、来源revision和错误不可被模板隐藏为“完整成功”；正式输出必须附Core生成的范围/完整性/版本清单，即使模板不含这些节点。

RenderRequest.ContractVersion恰`report-api-v0.2`，未知版本在Validate拒绝；Options.CoreRevision用于Claim/Metadata，不能为空或调用者临时编造。请求模式改用单一RenderMode，删除PreviewOnly/Publish双bool。Preview允许固定或明确实时输入；实时仍使用此次冻结的行版本，只在醒目标记中说明不具正式资格，禁止Publish。Formats非空、无重复、按enum值排序参与hash；v0.2 Preview请求恰包含Pdf（同时输出PDF/受控PRNX/Metadata）；其它format SupportsPreview=false，选择这些格式须Publish；Publish全部格式须具发布能力；文件建议名可null，否则1..128 UTF-8字节，禁止路径分隔符、冒号、控制字符、尾空格/点及Windows保留名，只是显示名，不作为存储路径。

### 3.3 结果、事件与核心入口

```csharp
public enum OperationPhase { PreAdmission, Accepted, Queued, Binding, Rendering, Encoding,
    Publishing, Reconciling, Draining, DrainUnknown, ResourcesReleased }
public enum OperationOutcome { Rejected, Completed, Partial, Cancelled, Failed,
    Unknown, NotRecoverable }
public enum ArtifactState { Planned, Staged, Verified, PublishPending, Published,
    PreviewReady, Failed, Cancelled, Unknown, NotRecoverable }
public enum ResourceState { Retained, DrainUnknown, Released }
public enum ReportLookupState { Found, NotFound, Unknown }
public sealed record RenderError(string Code, string Stage, string MessageKey,
    string? DetailSha256, bool RetrySameIntent);
public enum ArtifactRole { Document, Metadata, PreviewDocument }
public sealed record ArtifactResult(ArtifactId ArtifactId, OperationIdentity Identity,
    ReportFormat Format,
    ArtifactRole Role, int PageIndex, ArtifactState State, FileObjectId? ObjectId, long? ByteLength,
    string? ContentSha256, int? PageCount, int? RendererPageCount, long? RecordCount,
    string? PublishReceiptId, RenderError? Error);
public sealed record RenderResult(OperationIdentity Identity, OperationPhase Phase,
    OperationOutcome? Outcome, ResourceState Resources,
    ImmutableArray<ArtifactResult> Artifacts, string RequestSha256,
    DateTimeOffset StartedUtc, DateTimeOffset? FinishedUtc, RenderError? Error);
public sealed record ReportOperationLookupResult(OperationIdentity Identity,
    ReportLookupState LookupState, RenderResult? Result, RenderError? Error);
public sealed record ArtifactLookupResult(ArtifactId ArtifactId,
    ReportLookupState LookupState, ArtifactResult? Result, RenderError? Error);
public enum CancelDisposition { Requested, AlreadyRequested, AlreadyReleased,
    NotFound, Unknown }
public sealed record CancelReceipt(OperationIdentity Identity,
    CancelDisposition Disposition, OperationPhase? ObservedPhase);
public sealed record ResourceCounters(long ReservedBytes, long? MeasuredWorkingBytes,
    long? MeasuredNativeBytes, long? OpenLeaseCount, bool Complete);
public sealed record DrainResult(ResourceState State,
    ImmutableArray<OperationIdentity> RetainedIntents, ResourceCounters Counters,
    RenderError? Error);
public enum ReportEventKind { PhaseChanged, Progress, ArtifactChanged,
    PreviewReady, CancelRequested, DrainUnknown }
public sealed record ReportEvent(OperationIdentity Identity, long Sequence,
    ReportEventKind Kind, OperationPhase Phase, ArtifactId? ArtifactId,
    long Completed, long? Total, DateTimeOffset AtUtc, RenderError? Error);
public interface IReportEventObserver { void OnEvent(ReportEvent value); }
public interface IReportingCore : IAsyncDisposable
{
    ValidationResult Validate(RenderRequest request);
    ImmutableArray<FormatCapability> Capabilities { get; }
    Task<RenderResult> RenderAsync(RenderRequest request,
        CancellationToken cancellationToken = default);
    ValueTask<CancelReceipt> CancelAsync(OperationIdentity identity,
        CancellationToken cancellationToken = default);
    ValueTask<ReportOperationLookupResult> QueryOperationAsync(string consumerId,
        ReportIntentId intentId, string requesterId, string authorizationScopeId,
        CancellationToken cancellationToken = default);
    ValueTask<ArtifactLookupResult> GetArtifactAsync(string consumerId, ArtifactId artifactId,
        string requesterId, string authorizationScopeId,
        CancellationToken cancellationToken = default);
    IDisposable Subscribe(IReportEventObserver observer);
    Task<DrainResult> CloseAsync(TimeSpan observationTimeout,
        CancellationToken cancellationToken = default);
}
// 以下类为指定实现入口；方法行为按本节及§4–6，不是已存在代码。
// public sealed class ReportingCore : IReportingCore
//     public ReportingCore(ReportingDependencies dependencies, ReportingOptions options);
// public static class ReportingFactory
//     public static IReportingCore Create(ReportingDependencies dependencies, ReportingOptions options);
```

Core.Contracts的公开DTO/端口仍在Asun.Modules.Reporting；只有ReportingProcessOwner、SingleInspectionReportHost、BatchQualityReportHost实现类位于Asun.Modules.Reporting.Hosting，§14.4因此同时using两namespace，不存在同名影子DTO。构造/Create同步只验证参数、建立有界账本和immutable能力快照，不触发IO、渲染、线程文化或窗口；构造失败无接纳且不dispose宿主端口。`Validate`是无副作用纯函数，不能证明授权/快照/Store可用。任务完成/ResourcesReleased不再通过同一observer队列发额外回调（避免最终事件自身仍占排空资源的循环）；由原Task完成及Query最终快照通知，UI持有原Task续接并纳入view根Owner。最后一条回调最多Draining/DrainUnknown，关闭投递入口、已有回调全部退出后才发布最终本地快照。Core不提供阻塞Render包装；异步API不经UI线程，不把等待截止点误作原Task完成。构造注入的端口归宿主，Core不dispose；每次取得的租约/报告实例归操作并逐项归还。重复Dispose/Close共享一次内部关闭任务；DisposeAsync等待真实清理，可能因失控适配器不能及时完成，由§14的进程根Owner观察与保持，不能伪成功。

OperationPhase只描述在途/排空，不混用产物状态。Created原RenderAsync任务只有全部本次借用资源释放、事件队列完成投递或撤销且已进入的回调真实结束、最后快照可查询后才返回；返回Phase=ResourcesReleased、Resources=Released、Outcome非null。接纳前拒绝为PreAdmission/Rejected/Released且无artifact。重复请求若原执行在本实例内，返回同一个原Task；原执行在其它进程时只返回Store观察快照，Resources可Retained、Outcome可null，宿主必须Query原ID，不能当终态或另启render。外部发布已完成但本次cleanup未完，只能查询到Published产物和Draining/DrainUnknown操作，Outcome暂null。持久提交未知但本地资源已释放可返回Outcome=Unknown，这是发布不明，区别于资源未释放。Outcome聚合优先Unknown，其次部分成功Partial，其次全成功Completed；无成功项时按实际Cancelled/Failed/NotRecoverable。已发布部分不因取消改为Cancelled。

订阅是提示，不是事实Owner。Sequence每intent单调递增；状态/产物事件不合并，Progress可合并但序号保留跳号。每observer单独有界队列和串行后台投递；慢/抛异常observer脱离并诊断，不阻塞执行线程，不吞最终查询结果。Subscribe超限拒绝；UI按intent+view epoch+sequence过滤迟到；撤销订阅不取消操作。撤销observer丢弃未投递提示并禁止新调用；已经进入OnEvent的原回调Task仍强持并计入Core排空，回调不退出则DrainUnknown；不能脱离字典后假称线程已释放。宿主在OnEvent内自启的异步工作不属于该同步回调完成证明，必须由UI/根Owner另持至真实退出。

### 3.4 精确端口与租约

所有端口以`PortResult<T>`返回已知失败/Unknown，不能用null/空数组代替未知；Status=Ok时Value非null且Error=null，否则Value=null、Error必有稳定Code。端口抛异常在已调用之后按阶段转换；涉及接纳/发布的异常视作Unknown，不能宣称不存在或未发布。取消异常不证明回滚。拒绝默认枚举/非法实现结果。

```csharp
public enum PortStatus { Ok, NotFound, Denied, Conflict, Failed, Unknown }
public sealed record PortResult<T>(PortStatus Status, T? Value, RenderError? Error);
public sealed record AuthorizationRequest(string ConsumerId, string RequesterId,
    string ScopeId, ReportIntentId IntentId, ArtifactId? ArtifactId, string Action,
    string RequestSha256);
public sealed record AuthorizationReceipt(string DecisionId, SourceRevision Policy,
    DateTimeOffset ValidUntilUtc); // 仅栅栏凭证，Core不自制权限
public interface IAuthorizationGate
{
    ValueTask<PortResult<AuthorizationReceipt>> CheckAsync(AuthorizationRequest request,
        CancellationToken cancellationToken);
}
public interface IReportProjectionSource
{
    ValueTask<PortResult<IProjectionLease>> OpenAsync(ReportInputClosure input,
        CancellationToken cancellationToken);
}
public interface IProjectionLease : IAsyncDisposable
{
    string LeaseId { get; }
    ReportInputClosure Manifest { get; } // 精确版本与授权范围，不是实时对象
    ValueTask<PortResult<ReportPage>> ReadPageAsync(string partId, long pageIndex,
        int maxRows, CancellationToken cancellationToken);
}
public sealed record ReportPage(string PartId, long PageIndex, long FirstRowIndex,
    ImmutableArray<ReportRow> Rows, bool IsLast, string RowsSha256);
public interface ITemplateCatalog
{
    ValueTask<PortResult<ITemplateLease>> OpenAsync(TemplateRevisionId id,
        string expectedSha256, CancellationToken cancellationToken);
}
public interface ITemplateLease : IAsyncDisposable
{
    string LeaseId { get; }
    TemplateDefinition Definition { get; }
}
public interface ILocalizationSnapshot
{
    ValueTask<PortResult<ILocalizationLease>> OpenAsync(string languageTag,
        SourceRevision revision, CancellationToken cancellationToken);
}
public interface ILocalizationLease : IAsyncDisposable
{
    string LeaseId { get; }
    LocalizationData Data { get; }
}
public interface IReportFileObjects
{
    ValueTask<PortResult<IFileReadLease>> OpenReadAsync(FileObjectId id,
        string expectedSha256, AuthorizationReceipt authorization,
        CancellationToken cancellationToken);
}
public interface IFileReadLease : IAsyncDisposable
{
    FileObjectId ObjectId { get; }
    string Sha256 { get; }
    long Length { get; }
    Stream Content { get; } // 只读；不得向调用者泄漏任意本机路径
}
public sealed record OperationIdentity(string ConsumerId, ReportIntentId IntentId);
public sealed record ClaimRequest(OperationIdentity Identity, string RequestSha256,
    RenderRequest Request, SourceRevision CoreRevision);
public enum ClaimDisposition { Created, Existing, Conflict, Unknown }
public sealed record ClaimReceipt(ClaimDisposition Disposition, string? ExecutionToken,
    RenderResult? Existing, RenderError? Error);
public sealed record ArtifactKey(OperationIdentity Identity, ReportFormat Format,
    ArtifactRole Role, int PageIndex);
public sealed record Verification(long ByteLength, string Sha256, int PageCount,
    int? RendererPageCount, long RecordCount, string InputRowsSha256, SourceRevision Adapter);
public sealed record ArtifactPublication(ArtifactId ArtifactId, ArtifactRole Role,
    int PageIndex, Verification Verification);
public sealed record PublishRequest(OperationIdentity Identity, ReportFormat Format,
    string ExecutionToken, ImmutableArray<ArtifactPublication> Members,
    AuthorizationReceipt Authorization);
public interface IArtifactStore
{
    ValueTask<ReportOperationLookupResult> QueryAsync(OperationIdentity identity,
        CancellationToken cancellationToken);
    ValueTask<ClaimReceipt> ClaimAsync(ClaimRequest request, CancellationToken cancellationToken);
    ValueTask<PortResult<IArtifactWriteLease>> StageAsync(ArtifactKey key,
        string executionToken, long maxBytes, CancellationToken cancellationToken);
    ValueTask<PortResult<ImmutableArray<ArtifactResult>>> PublishAsync(PublishRequest request,
        CancellationToken cancellationToken);
    ValueTask<PortResult<RenderResult>> RecordAsync(OperationIdentity identity,
        string executionToken, long sequence, RenderResult snapshot,
        CancellationToken cancellationToken);
    ValueTask<ArtifactLookupResult> GetAsync(ArtifactId id, CancellationToken cancellationToken);
}
public interface IArtifactWriteLease : IAsyncDisposable
{
    ArtifactId ArtifactId { get; }
    FileObjectId ObjectId { get; }
    Stream Content { get; } // 有界可写、非公开
    ValueTask<PortResult<SealedArtifact>> SealAsync(CancellationToken cancellationToken);
}
public sealed record SealedArtifact(ArtifactId ArtifactId, FileObjectId ObjectId,
    long ByteLength, string Sha256);
public sealed record ReportMetadataHeader(string SchemaVersion, OperationIdentity Identity,
    string RequestSha256, ReportInputClosure Input, ReportBudget Budget,
    SourceRevision Core, ReportFormat Format, RenderMode Mode,
    ImmutableArray<ArtifactPublication> Members);

public interface IArtifactVerifier
{
    Task<PortResult<Verification>> VerifyAsync(SealedArtifact artifact,
        ArtifactKey key, RenderContext context, CancellationToken cancellationToken);
}
public interface IReportRows
{
    ValueTask<PortResult<ReportPage>> ReadAsync(string partId, long pageIndex,
        CancellationToken cancellationToken); // Core包裹source；每次只借一个批次
}
public sealed record RenderContext(RenderRequest Request, TemplateDefinition Template,
    LocalizationData Localization, IReportRows Rows, IReportFileObjects Files,
    AuthorizationReceipt Authorization);
public sealed record RenderedArtifact(ReportFormat Format, ArtifactRole Role, int PageIndex,
    Verification Verification);
public interface IRenderOutput
{
    ValueTask<PortResult<IArtifactWriteLease>> OpenAsync(ReportFormat format,
        ArtifactRole role, int pageIndex, CancellationToken cancellationToken);
}
public interface IRenderAdapter
{
    ImmutableArray<FormatCapability> Capabilities { get; }
    ValueTask<PortResult<IRenderSession>> CreateAsync(RenderContext context,
        CancellationToken cancellationToken);
}
public interface IRenderSession : IAsyncDisposable
{
    Task<PortResult<ImmutableArray<RenderedArtifact>>> EncodeAsync(ReportFormat format,
        IRenderOutput output, CancellationToken cancellationToken);
}
public sealed record ReportDiagnostic(string Code, OperationIdentity Identity,
    string Stage, string? DetailSha256, long? ResourceBytes);
public interface IDiagnosticsSink { bool TryWrite(ReportDiagnostic diagnostic); }
public interface IReportingResourceMeter
{
    ResourceCounters Read(OperationIdentity identity); // 无阻塞、已登记buffer/native/lease总量
}
public sealed record ReportingDependencies(IReportProjectionSource Source,
    ITemplateCatalog Templates, ILocalizationSnapshot Localization,
    IAuthorizationGate Authorization, IReportFileObjects Files,
    IArtifactStore Store, IRenderAdapter Renderer, IArtifactVerifier Verifier,
    IDiagnosticsSink Diagnostics, IReportingResourceMeter Resources,
    TimeProvider Time);
```

ArtifactRole是产物身份的一部分。Metadata为同intent/format的标准清单文件，PageIndex=0；Document单文件=0、PNG页=1..N；PreviewDocument在Pdf的Preview/Publish模式必需，PageIndex=0，内部PRNX仅由R-A1生成、绝不接受上传。ReportMetadataHeader.SchemaVersion固定`report-metadata-v2`；每format必须有Metadata产物，内含全部原范围/模板/语言/renderer版本、实际artifact清单、原值/显示/单位/Validity/Reason及缺口，按report-binary-v2对应类型编码，媒体类型application/vnd.asun.report-metadata-v2；正式单件/批次消费需支持该清单而不是丢失原值。CSV空集也有清单，不另建事实Owner。Metadata只记录文件对象hash/ID，不存图片字节；其规范完整结构如下，数据行以IReportRows同源重读并流式写入，不全量列表。Manifest先写ASCII `ASUN-META2`，然后ReportMetadataHeader按位置顺序编码，接着按Parts顺序写partId和Int64 ExpectedCount、逐行ReportRow，结尾写ASCII `END-META2`；完整性检查必须实际读到结尾且无尾字节。每format Header.Members只列Document/PreviewDocument的已封口ID/hash，不含Metadata自身，防循环hash。所有计划必需产物Verified后Store.Publish才可使该format组可见；多format不保证整组事务，保持Partial/Unknown。

租约归还包括关闭其流；借用方不另外关闭仍在使用的流。Renderer写完并await SealAsync，Core强持同一个lease及原Seal/Dispose任务；Seal只停止写入并返回实际文件长度/hash，不发布。Core Verifier从Files读同一已封口对象核结构并返回Verification，再await lease归还；double dispose必须幂等。Renderer不得持有租约超出session真实结束。Output.Open把新ArtifactId/lease先登记操作账本再交Renderer，异常/迟到也有Owner。Files端口通过Core的计量/授权decorator传入context，每次OpenRead都先过读取栅栏，成功先登记再交Renderer。Manifest.Length/Sha256与实际读取字节/hash不符则失败；必需附件不能用空白替代。所有query/read/续传由同一授权Owner定义线性化边界，Core只传原授权identity，不缓存“以前允许”。

Store负责持久幂等与执行token的fencing；`ClaimAsync` Created必须持久原请求闭包并仅给一个执行token，Existing返回历史/在途快照，Conflict拒绝，Unknown不得渲染。`RecordAsync`按token+sequence CAS，旧进程不能覆盖新状态。PublishRequest提交同一个format全部Document/Metadata及该格式必需PreviewDocument成员（Pdf的PRNX、PNG全部页及清单），Store须原子登记该format组可见性；成员有缺口不得公开，重试精确同一成员ID/hash；其它format可独立成功。发布只能读取已封口且Verified的文件对象；Stage/Publish在Store与文件对象实现中协调，不把文件字节放入数据库。Stage按ArtifactKey重试必须取得同一个ArtifactId，不新建重复正式产物；PageIndex=0用于单文件，PNG页为1..N。本地报告执行账本不是新的生产事实库。Store对外发布原子性、保持与跨进程恢复fencing必须由真实存储Owner映射资格确认，不能靠这个模块接口声称已实现。

## 4. 验证、身份与固定接纳顺序

### 4.1 唯一请求编码与幂等

幂等键只有`(ConsumerId, IntentId)`。RequestContentSha256是**比较内容**，不进入键；模板/格式改变仍是同意图冲突。删除旧`(IntentId, hash, template, formats)`组合键。相同内容查原回执优先于重新校验当前模板/当前快照有效期，否则历史产物会被模板删除误伤。

模块规范编码`report-binary-v2`：UTF-8严格编码（非法surrogate拒绝）无BOM、不归一Unicode；顶层先写ASCII `ASUN-RPT2`（9 bytes），后按record位置参数顺序逐字段；身份wrapper等价对应string；字符串写UInt32 little-endian字节长再UTF-8；nullable先写1 byte 0/1；bool为0/1；enum为Int32 little-endian，值按本节声明顺序从0起固定；int/long分别Int32/Int64 little-endian；decimal写不带locale的`ToString("G29", InvariantCulture)`字符串；时间写UTC ticks Int64、Duration写ticks Int64；数组写UInt32数量然后按顺序；字典写数量后按Ordinal key排序键/值；SourceRevision按OwnerId/Revision/Sha256；ReportScalar先写tag（Text=0,Integer=1,Decimal=2,Boolean=3,Timestamp=4,Duration=5,EnumValue=6,Identifier=7,Evidence=8）Int32再写变体参数；对象不写CLR类型名。request编码排除IntentId与RequestContentSha256，其余字段按RenderRequest顺序写，Formats预排序；不得排除预算、Requester/授权范围、模板、语言或任何投影元数据。SHA-256 lower hex后与request提供hash精确比较。规范编码公开入口（均为指定待实现的纯函数，无IO）：`ReportCanonicalCodec.ComputeRequestSha256(RenderRequest request)`（忽略自hash但先校验其余shape）、`ComputeTemplateSha256(TemplateDefinition definition)`、`ComputeLocalizationSha256(LocalizationData data)`；流式行入口为`ReportRowsHasher(long expectedCount)`、`void Append(ReportRow row)`、`string Finish()`，Append计数/稳定key，Finish仅当实际count等于expected且只调用一次；构造/Append/Finish的shape错误抛ArgumentException或InvalidOperationException，Core转ValidationIssue，不用异常文本当机器协议。模板/语言首次构造时Source.Sha256可置64个0再调用各自Compute并with替换为结果；该自摘要字段被唯一规则排除，不用private helper猜首个hash。元数据公开写入入口为`Task ReportCanonicalCodec.WriteMetadataAsync(ReportMetadataHeader header, IReportRows rows, Stream output, CancellationToken cancellationToken)`，按§3.4固定顺序流式写、核全部expectedCount/RowsSha256、禁止关闭借用output/rows；它是Core唯一规范序列化服务，正式Verifier独立解析，不能由重新调用写入codec自证。原请求RequestContentSha256可先为空交Compute但不能空交Validate/Render；计算hash不验证事实真实性。CoreRevision由Options.CoreRevision记录在Claim/Metadata，不改旧请求hash。TemplateDefinition摘要为ASCII `ASUN-TPL2`加按位置顺序编码的全部字段；LocalizationData摘要为ASCII `ASUN-LOC2`加全部字段。仅各自Source.Sha256在自摘要中省略（OwnerId/Revision仍写），否则形成自引用；外部文件资源hash保留。Catalog/Localization端口须提交对应规范摘要，不能以未定义JSON顺序冻结身份；源事实的SourceRevision/Snapshot摘要依原Owner规则，不在此重算。

RowsSha256采用`report-rows-v2`：ASCII `ASUN-ROWS2` + Int64 ExpectedCount + 按稳定顺序编码全部ReportRow（不写外层数组长度，因为计数已经固定）；page hash同法但count用该页实际行数。流式IncrementalHash，不为计算摘要全量ToList。StableKey使用SortContract承诺的严格Ordinal递增唯一键；上游复合排序需映射为该稳定键，Core不推断数据库顺序。字段字典名称Ordinal排序，原值/显示/Validity/原因全部进入hash。规范向量：string `00128`为`050000003030313238`，Int64 -1为`ffffffffffffffff`，decimal 0.32004先写7字节`0.32004`即`07000000302e3332303034`；enum新增不得改旧tag，破坏变化升schema。以上是模块自身编码，不改上游模型资产JCS或历史证据hash。

### 4.2 执行顺序

1. 无IO Validate身份、闭包形状/枚举、字符串、预算、模式和请求hash。非法请求无Claim，不产生文件。
2. 以ConsumerId/IntentId及请求范围核`query-operation`授权 → Store.Query。Found时比较原RequestSha256：异内容Conflict；相同则核原产物读取权限后返回/等待原任务，不打开当前模板；Unknown停止并返回查回提示。仅权威NotFound进入后续生成。查询授权Denied/Unknown不泄漏原产物存在性。
3. 核`preview`或`generate`授权，Store.Claim原身份；竞争只能一个Created。Existing仍按第2步；Conflict/Unknown不调用renderer。Claim成功后原任务进入Accepted，有界入队；队列满记录Rejected并无文件，不能悄悄换身份重试。
4. 打开模板/localization/source租约，精确比较request闭包；source确认RangeProof及统计关系。校验完整模板资源/格式/用途/字段/字体；确认固定总体。授权/输入变更为明确错误，不实时查询替换。
5. 按预算读源并核每页index、FirstRowIndex连续、StableKey、行类型、页hash、完整count/最终hash；单页<=PageBatchRows，空集只允许第0页零行IsLast=true；非末空页拒绝。对每个格式重新从同一个可重复读lease读取，有界reader串行，session不能并发读取同part。流式数据输出可写暂存同时累计hash，但全源验证未完成前不得Publish。需要全量数据的DX布局先写受预算暂存，再有界物化；超出MaxWorkingBytes拒绝。缓存页面不等于输入有界。
6. 由能力矩阵选择格式，session独占可变report；按enum排序逐格式执行。所有打开/输出租约先入账；编码返回后等原session调用结束、write lease封口；重新从文件对象流核字节/hash/页数/记录数/必需节点，与RenderedArtifact比较，不能信Renderer声明即发布。格式失败可继续其它独立格式，底层仍在执行时不启动下一格式。Verifier是独立结构读取器而不是Renderer自报布尔值；它须核每part行集合/最后hash、角色/所有页/Metadata结尾/原值类型及资源出处，失败/不支持验证即不发布；PageCount仅对PDF实际页/PNG单页及受控PRNX有文件分页意义；Verification非适用格式为0，ArtifactResult对应PageCount=null；DOCX/HTML/XLSX/CSV/Metadata一律不适用，不拿package/app.xml Pages或段落分页符当实际外部页数。RendererPageCount是本次CreateDocumentAsync后PrintingSystem.PageCount，仅对DX布局报告记录（Metadata/DataXlsx/CSV为null）；它与外部Word/浏览器/Excel打印页数不是同一值，缺生成分页证据即null。未知数值不填0伪已测。
7. Preview写入非公开短期preview文件对象；Encode的format支持预览时还输出PreviewDocument(PRNX)+Metadata，Verify全部后Core通过Store.RecordAsync记录PreviewReady成员，Store按该记录使preview对授权读可用，原子登记相同成员集合；不调用正式Publish。Publish在`publish`栅栏后按原ArtifactId/token提交，已封口/结构/完整性/范围全部通过才发布。发布异常/超时先查询原intent与artifact，Unknown不换ID。
8. 记录逻辑产物结果 → Draining →逐项真实归还→ResourcesReleased，原任务返回。最后RecordAsync为只写不可变回执的持久收尾：在所有渲染/IO/事件借用已真实释放后，记录拟定Released结果，且原Record Task由账本强持至实际返回；外部Store回执的Released仅是原执行者声明，跨进程观察不能单凭此声明当本进程清理证明，需原Owner/原Task确认。若该Record尚不返回，本地原Task/Query仍DrainUnknown，根Owner保留槽位。Store最终记录Unknown时本地仍保留快照与原token，对外Outcome=Unknown并按原ID查询，不声称持久完成。

## 5. 状态、恢复和错误

```text
Accepted -> Queued -> Binding -> Rendering -> Encoding -> Publishing/Reconciling
任一在途失败/取消/期限 -> Draining -> ResourcesReleased + Outcome
实际归还未确认 -> DrainUnknown（无Outcome/FinishedUtc，原任务仍被Owner持有）
迟到退出/归还 -> Draining -> ResourcesReleased（保留原错误，不覆盖为成功）
```

PreviewReady和产物Published是可查询逻辑结果，不表示资源释放。CancelAsync仅作用当前Core接纳且Consumer/Intent精确匹配的本地操作；调用资格是持有该Core实例的宿主授权Command/根Owner，不提供远程取消或按Intent猜其它consumer；Root关闭通过保存的业务CTS取消自己接纳的任务，查询外部操作不能获得取消权。取消不删除已发布/旧产物；阶段取消后停止新格式/新页，等待原调用返回。取消发生在Publish请求之后不能推断回滚；先对账，仍未知则Outcome=Unknown，即使调用者已取消。`CancelAsync`只记录请求并触发该操作令牌；token只取消这次等待，不等于撤销已写的取消请求。`CloseAsync`停止新接纳并对全部在途操作请求取消，以独立有限观察期限返回DrainResult；到期State=DrainUnknown及原intent清单，绝不dispose仍执行的对象。重复关闭观察同一次内部cleanup；构造后未执行也需可关闭，纯C1没有伪native排空。

恢复不默认重跑。进程重启先查询原身份；Published项只按当前权限读回；Unknown持续按原ID对账。只有Store权威确认未发布、源/模板/资源原版本仍保持、原执行者已排空并由Store发新fencing token时，才允许继续未完成格式。当前v0.2无公开“接管token”API：真实Owner恢复执行需其适配器在Claim协议中提供已确认恢复的Created回执；Core不会自行抢占。无法取回原输入为NotRecoverable；若还有Published项聚合Partial；未知项未查明始终Unknown优先。暂停、方法离栈、窗口关闭、等待取消均不是移交证据。

| 错误码 | 状态/保留与允许恢复 |
|---|---|
| RPT-REQ-INVALID / RPT-INVALID-MODE / RPT-VERSION-UNSUPPORTED | 接纳前Rejected；无文件；修请求/new intent；旧schema用旧codec，不重算历史身份 |
| RPT-AUTH-DENIED / RPT-AUTH-UNKNOWN | 不交付/不发布；历史产物保留；恢复栅栏后query原ID，Unknown不能沿缓存放行 |
| RPT-SNAPSHOT-NOT-FIXED / RPT-SNAPSHOT-INCOMPLETE | 停受影响格式，保留范围/缺失身份；新固定快照需新intent；零行完整集可成功 |
| RPT-TEMPLATE-NOT-FOUND / RPT-TEMPLATE-INCOMPATIBLE / RPT-TEMPLATE-UNTRUSTED | 关闭已取得租约；修/批准新模板新intent；不载任意REPX试运行 |
| RPT-FORMAT-UNSUPPORTED | 不启动该请求；不得静默删格式、降CSV或减少字段 |
| RPT-BUDGET-EXCEEDED | 停新读取/编码，真实排空；不截断为完整、不自动分卷；宿主批准更大Profile或显式分范围新intent |
| RPT-SOURCE-UNAVAILABLE / RPT-SOURCE-CHANGED | 不换实时源；只query原产物；失保持未完项NotRecoverable |
| RPT-CANCELLED / RPT-TIMEOUT | 原错误保留；实际排空前无取消/失败终态；Published保持，发布未知另对账 |
| RPT-PUBLISH-UNKNOWN / RPT-CLAIM-UNKNOWN / RPT-STORE-UNKNOWN | 原intent/artifact/token强持；只能按原ID查，禁止换键、覆盖或声称NotFound |
| RPT-OUTPUT-INCOMPLETE | 半文件不公开；校验失败格式Failed，已发布其它格式保留 |
| RPT-CONFLICT | 同Consumer/Intent不同content；返回冲突不取新数据；调用方决定新意图 |
| RPT-DRAIN-UNKNOWN | 不发ResourcesReleased；保留资源账本/原Task，根Owner继续观察迟到清理 |
| RPT-INTERNAL / RPT-OBSERVER-DETACHED | 原操作错误/诊断；observer错误只脱订阅，不把渲染改成功或阻塞资源归还 |

所有机器错误键稳定，界面文字本地化；异常堆栈及敏感输入只保留脱敏详情hash。Error.Stage精确为validate/lookup/claim/bind/read/render/encode/verify/publish/reconcile/drain/deliver；无原始SQL/模板脚本/路径/敏感值。Diagnostics.TryWrite=false只增加有界丢日志计数，不递归记录或覆盖主错误。

## 6. 线程、资源和关闭

Core内部使用有界队列、每intent独立状态锁/CAS、异步IO、TimeProvider单调期限；不能锁内await、同步Wait/Result、无界Task.Run或依靠UI Dispatcher。Adapter能力和资源预算在构造时复制冻结。CPU/同步DX工作在适配器有界worker上执行，不是假装同步IO变异步；是否需要STA以实际消费API为准，WPF实例始终在所属Dispatcher。

每操作有强持账本：原请求、claim token、原RenderTask、每个port原Task、租约、session、output stream、observer投递和清理Task。对任何可迟到的Open/Create/Encode/Publish/Dispose调用，**先在预算/账本登记Starting条目，之后才外调，再原子挂接返回的唯一原Task，后开始观察deadline**；取得迟到lease仍入同一账本并在无业务使用者后释放。业务调用返回之前不dispose上下文、输入或流；发布迟到必须更新原ArtifactId回执，不新建一次导出。根Owner回调ReleaseHostDependencies严格无资源逃逸、幂等且返回唯一原Task；外借deps不归Core。Close观察使用独立CTS，不复用已取消业务token；cleanup错误附加诊断，原业务错误和发布Unknown不丢失。

### 6.1 每次外调前登记 Starting

对Open/Create/Read/Claim/Encode/Seal/Verify/Publish/Record/Get/Dispose及同步诊断/计量入口，都先在操作锁内预约相应槽/字节并创建不可替换的Starting条目（CallId、OperationIdentity、端口实例、方法、参数/借用上下文、预计资源、开始时间、待挂接Task占位、状态）。尚未取得配额就不调用；注册失败无外部副作用。Starting条目计入活动/资源容量，关闭会观察它而非因Task还为null忽略。

出锁后且只调用一次端口方法，不在状态锁、Dispatcher或未登记Task.Run中执行。同步返回Task/ValueTask后立即在**同一条目**挂接原任务；ValueTask只AsTask一次，不能二次await消费。返回已完成任务也先挂接，之后才能分类结果和把lease加入同一条目；不因迅速完成绕过记账。同步throw也写回原条目的异常/阶段：无副作用的验证异常可确认Failed，Claim/Publish/Record等提交可能发生者保留Unknown并查原ID；没有返回Task不能虚构任务已取消/资源已释放。对以lease返回的端口，约定返回前失败必须由端口Owner释放尚未交付资源且不得启动逃逸后台任务；无法证明时计量Complete=false/条目Unknown，保持原端口实例和上下文并向Owner对账，不构造成功租约。

Core进程端口的同步前导必须只做有界参数校验和任务提交，快且不跨设备、不含同步数据库/网络/磁盘长IO、不阻塞等待。需要同步SDK/文件编码的适配器先有自己的有界worker槽，在Core已经登记的调用中快速返回唯一worker Task；同步前导可能失控者在装配时就隔离到该有界worker，Core不得直接调用并等它返回Task。worker预约/Starting同样先于启动函数，配额不足快速明确拒绝，不另启动无人持有任务。

观察期限可能在Task挂接前到达，或Close已停止新接纳；Starting条目/输入/端口仍由根Owner保持。原前导迟到返回Task、lease、封口或发布回执时归原CallId/Intent/Artifact，记录后执行已决定的取消/归还/对账，不重开格式或换ID。禁止新工作不等于删Starting；只有实际退出且交付/释放证明闭合才归还配额。TC14追加“端口同步throw、Task即时完成、前导/lease晚到”三个屏障断言，全部检查原CallId和Starting占位在外调前已可查询。

MaxActiveOperations、MaxQueuedOperations、MaxObservers含关闭未排空和Unknown持有项；到期不从容量计数抹除。一个活动session只处理一个格式；独立intent隔离语言、模板及流。共享的模板/资源仅immutable；不得设置线程全局Culture、DevExpress全局localizer或全局当前报告。归还顺序是停止新工作→原encode真实结束→session→文件read/write→source/template/localization→记录资源释放。释放失败保持该lease与同一个DisposeTask，不能并发再次dispose；只有接口明确幂等且原Task已失败完成才按Owner协议重试。

关闭预览仅归还视图读租约、取消订阅；取消报告用独立命令。PreviewReady的文件保留/到期由Store Owner策略管理，本次Render资源已释放不等于未来视图lease也已释放。所有入口caller identity/Scope/key/错误字段同§3.1有效域；AuthorizationRequest.Action只允许query-operation/lookup-artifact/preview/generate/publish/read，未知action拒绝，Core与宿主不增加权限政策。Lookup Found必须Result非null且identity匹配，NotFound须权威Error=null/Result=null，Unknown必须Error且Result=null；Claim Created的token非空，Existing的Result必需，未知返回不允许execution token。Origin Store错回consumer/token/sequence按StoreUnknown拒绝使用，不泄露别的范围。读取/下载/Range每次交付使用新授权；Core不把公开Locator给未授权调用方。进程结束移交只按§14确认协议，不把进程退出当文件发布或资源正常释放证据。

## 7. 格式适配与可复现输出

### 7.1 冻结的格式责任

| 格式 | 输入/布局与输出规定 | 资格门 |
|---|---|---|
| Pdf | 受限布局、固定分页，含范围/版本/原值/有效性清单；流式写硬盘暂存 | 实际页数、字体、Unicode、超长行、取消及封口结构核验 |
| LayoutXlsx | 同布局的呈现；合并/分组只是布局，不等于数据库；不承诺与PDF像素一致 | 公式/单元格类型/合并及字段无缺失核验 |
| DataXlsx | 每part独立sheet，固定字段顺序；类型化原值、显示/单位/validity/reason列，metadata sheet含范围/版本 | 1,048,576行含表头及16,384列格式上限，超出拒绝；真实Spreadsheet API绑定与读回 |
| Csv | 每request恰1part；UTF-8 BOM、逗号、CRLF、RFC4180 quoting；固定字段顺序，元数据/单位/validity/reason列逐行保留，空集保留表头及独立范围清单 | 多part拒绝；字符串formula防护及原值映射读回 |
| Docx | 受限布局；固定范围/清单，PageCount不适用；仅另列本次XtraReport生成的RendererPageCount，不声称Word实际页数 | ZIP/关系/文本/无宏外链，代表软件读回 |
| Html | 单文件UTF-8、自包含，所有文本HTML编码；无JS/外链/表单/自动请求，图片data URI来自已批准流 | CSP/结构/链接拒绝、打开无网络请求 |
| Png | 一页一FileObject、PageIndex=1..N；完整页集合及metadata manifest，由Store原intent清单原子登记可见 | 图像尺寸/DPI/页集合及遗漏页核验；不冒充可检索明细 |

格式能力是构造时明确登记，未装配返回Unsupported；全部计划能力保留适配切片，不以少支持几种格式宣称整模块完成。CSV文本在trim-leading-whitespace后首字符为`= + - @`或TAB/CR时，交付显示字段前置单引号防公式，同时伴随`<field>.raw_utf8_base64`列保存原字符串精确UTF-8；数值-1按Integer/Decimal写，不加单引号。XLSX以字符串单元格类型写文本，禁止公式setter；Identifier如00128始终文本。任何输出都保留Unknown/原因，不能空白/0/PASS替代。CSV/XLSX不得把所有字段转换为字符串破坏原类型；CSV原类型通过固定metadata/type列可重建，空集sidecar是同intent的metadata产物而不是另一事实Owner。Metadata产物身份/组可见性按§3.4；CSV不隐式省略该产物。

不自动分卷。宿主可显式生成多个已固定范围的独立intent，并用自身批次关系组合；reporting不会拆范围、改分母或猜批准卷数。大PDF采用`XtraReport.ExportToPdfAsync(Stream, PdfExportOptions, CancellationToken)`单任务路线，保留原Task等待真实结束；`PdfStreamingExporter`同步/多线程只是既有研究候选，v0.2不自动切换。DX数据先在受限暂存/物化预算内构建一次，超预算拒绝，不能以页面缓存宣称无限大输入有界。

### 7.2 DevExpress 25.2.3 具体构建路线

使用本机 `C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/` 程序集公开API。IRenderSession独占`XtraReport`，以`ReportHeaderBand`、`DetailBand`、`ReportFooterBand`和`XRTable.Rows`/`XRTableRow.Cells`构建。文字写`XRControl.Text`（Literal或已固定DisplayValue），`CanGrow=true`，声明宽高换算为报告单位，不把WidthF当像素；固定ReportUnit为HundredthsOfAnInch，mm×100/25.4；纸张/边距按同单位。不得使用内部用途的`XRTableCell.Weight`作为公共扩展契约；表格列宽在公开BoundsF/WidthF的适配构建与实际页中验证。证据`XRPictureBox.ImageSource`只从已授权流构造，不写ImageUrl、不载外部URI；已核公开构造为DXImage.FromStream(Stream)→new DevExpress.XtraPrinting.Drawing.ImageSource(dxImage, false)，ImageSource.Dispose负责图像释放；输入流/对象在report生成及encode真实结束前均强持，dispose ImageSource后再归还读流。

PDF/版式XLSX/DOCX/HTML/PNG分别使用已核XML的Stream+专属ExportOptions+CancellationToken异步重载。PNG在CreateDocumentAsync结束并取得实际页数后，逐页设置ImageExportOptions.PageRange为1-based页号Invariant字符串，调用ExportToImageAsync到各页独立stream，ProducingPageSet=true；不以一个stream覆盖最后一页。Preview另使用PrintingSystemBase.SaveDocument(Stream)保存本次受控PRNX；UI按§9.2.1复制经授权/hash核验的完整文件到实例自有临时路径，再由DocumentPreviewControl.OpenDocument(string)恢复，禁止外部PRNX。UI不另建PrintingSystem、不把它赋给object DocumentSource；PrintingSystemBase.LoadDocument(Stream)只作为已核公共入口资料，不是本版UI路线。预览使用同一次受控渲染文件/文档，不让控件按当前DataSource再生成。`LoadLayoutFromXml(Stream,bool)`虽存在，其官方安全注释明确不加载不可信来源；正式路线不调用它，`FromStream`也不是fallback。脚本默认禁用，本模块构建对象ScriptsSource保持空且不注册脚本；不按任务切换进程级ScriptPermissionManager。

DataXlsx冻结使用`DevExpress.Spreadsheet.Workbook`，WorksheetCollection.Add(string)按part输入序创建sheet，名称为`part0001`等固定编号避免业务key触发非法表名；`Worksheet.Cells[row,column].Value`通过已核CellValue隐式string/Int64/decimal/bool/DateTime/TimeSpan转换写值，不使用SetValueFromText自动识别、更不写Formula。长Integer/高精度Decimal超出Excel精确数字表示时不得静默舍入：始终写`raw_invariant`文本；source列仅在往返相等时写数值，否则写原文本，display仍为源DisplayValue。precision-preserved仅描述文本保留精度的技术行为，不是新增列、Validity枚举或生产状态；type在metadata保留，validity/reason沿源值。Datetime写ISO8601原UTC文本以免Excel日期系统改义。每字段扩展为source/display/unit/validity/reason/raw_invariant六列，Evidence/Enum用明确ID/key文本，null source对应未知保持无值+原因。仅用approved bcl scalar转换，不传任意object。Workbook.SaveDocument(Stream,DocumentFormat.Xlsx)后dispose Workbook；同一有界worker保留原同步任务直至完成，Stream晚到不提前释放；Verifier用Workbook.LoadDocument(Stream,DocumentFormat.Xlsx)读取自有输出并逐单元格校验type/精确原值/无Formula/外部关系。Spreadsheet格式自身总列数包含6×fields、固定metadata列，先检查16384列/1048576行及文本32767字符上限；超出拒绝，不截断。Metadata sheet与独立Metadata文件均来自同闭包，后者用于跨格式统一可复现。真实API用本机DevExpress.Docs.Spreadsheet.v25.2/Spreadsheet.Core直引，不下载包。

### 7.2.1 受限对象树、分页与固定导出选项

此节落实§3.2既有布局规则，不增加布局语言或改Template摘要。全部版式格式使用同一次已验证行物化及同一个XtraReport生成的文档；Renderer不得把DataSource交给业务对象或调用查询。内部ReportLayoutRow仅含固定RowOrdinal、StableKey、已解析单元格Text、Validity/Reason与节点身份，readonly数组复制且计入Working；不是公开DTO、延迟枚举、表达式或任意ObjectDataSource。

1. 校验所有Detail Field节点恰覆盖各part.Fields一次（不可重复Field/丢字段）；按part.Fields输入序建立列，宽度 `w[j]=可用纸宽×该字段节点WidthMm/该part所有字段节点WidthMm之和`。以decimal算累计边界，转换float后末列右界固定为可用纸宽，拒绝非有限/非正/整数溢出；不访问XRTableCell.Weight。NodeId在全模板唯一。Header/Footer各节点按数组序自上而下放XRLabel，宽高来自节点，起点x=0/y=前节点高度累计；同区总高度超可用纸高拒绝，不悄悄挤字号。Detail非Field节点的说明段按模板序放在其对应part/summary/errors附页，原值/范围/缺口的强制说明仍追加。
2. `ReportUnit=HundredthsOfAnInch`，`PaperKind=Custom`，`PageWidthF/HeightF=模板mm×100/25.4`；Margins整数边界用decimal Ceiling(mm×100/25.4)，有效内容宽高按实际整数Margins重算，拒绝不容纳节点。字体按§7.2.2已核family构造`DXFont(family,(float)FontSizePt,DXFontStyle.Regular,DXGraphicsUnit.Point)`，不给任务设进程字体库。每part创建一个DetailReportBand并按part输入序设Level=0..N-1、DataSource=该part内部readonly行数组、DataMember为空；不设SortFields/GroupFields/FilterString，保留source顺序。顶层空DetailBand HeightF=0，ReportHeader/ReportFooter仅全报告各一次。
3. 每part的GroupHeaderBand仅一行列标题，`RepeatEveryPage=true`；第一part `PageBreak=None`，其后part `BeforeBand`。DetailBand含一个XRTable/一行XRTableRow，Cells按字段序。每cell设公开WidthF/BoundsF、CanGrow=true、CanShrink=false、WordWrap=true、KeepTogether=false，DetailBand亦KeepTogether=false，不锁定整行到单页。DetailBand.BeforePrint从所属DetailReportBand.GetCurrentRow()取得内部ReportLayoutRow，逐cell只赋Text；未知/null row失败；回调同步有界、无IO/脚本/ExpressionBindings。字号不缩小，长文本按SDK路线跨页，TF01验证无截断/重复。空part仍出标题与EmptySetText，无伪数据行。
4. 每行第一列内保留固定行序/StableKey定位说明（`reporting.record`）；不用SDK隐藏Tag充当Verifier证据。错误、summary、证据及强制范围/完整性说明各用内部单记录DetailReportBand按既有顺序附页，不算总数。所有XRLabel `Multiline=true`、WordWrap/CanGrow=true/KeepTogether=false。所有控制的NavigateUrl、Scripts、ExpressionBindings为空。证据图用`XRPictureBox.Sizing=ZoomImage`，目标Node宽高内等比例居中，禁止crop/stretch或再次算法处理；原ObjectId/hash/尺寸与说明可见。必需附件失败阻断该格式；可选附件不可取时显示Missing及原身份，Metadata登记同一缺口。
5. 外调前按§6预约本次完整物化、全部图片解码、页/brick、字体及SDK托管/native资源的保守上界；没有已取得资格的上界与完整计量时，不开始客户输入的CreateDocument，只允许§11预先有限的诊断夹具且不得发布。已预约总量须不超Ceiling；生成中计量用于停止新工作，不以事后取消替代分配前预约。await原`CreateDocumentAsync` token Task；pageCount须1..MaxPages且计量完整，生成期越页/字节预算触发取消并等真实退出。物化/session原资源保持至所有格式编码/Verify退出（§6），同文档只生成一次，无Preview重取数据。

| 输出 | 固定25.2.3选项；不能依用户文本改SDK选项 |
|---|---|
| Pdf | `NeverEmbeddedFonts`为空、`ConvertImagesToJpeg=false`、`ShowPrintDialogOnOpen=false`、`ExportEditingFieldsToAcroForms=false`、`ExportBookmarks=false`、Attachments/密码/签名为空；所有字体须可嵌入且读回符合§7.2.2，否则失败 |
| LayoutXlsx | `ExportMode=SingleFilePageByPage`、`TextExportMode=Text`；每页独立sheet，仅版式文本，原型在Metadata保留；不启超链接/公式，不转DataXlsx |
| Docx | `ExportMode=SingleFilePageByPage`；报告级Header/Footer由band决定，不以Word实际分页反推结果 |
| Html | `ExportMode=SingleFilePageByPage`、`CharacterSet=UTF-8`、`EmbedImagesInHTML=true`、`AllowURLsWithJSContent=false`、`RemoveSecondarySymbols=false`、`UseHRefHyperlinks=true`；禁用控制NavigateUrl并禁止任何生成href，避免false时SDK脚本导航；封口前按§7.4审查HTML并加固定CSP `default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'`，禁止导航/脚本/event属性/外部字体/URL |
| Png | `Format=DXImageFormat.Png`、`ExportMode=SingleFilePageByPage`、`PageRange`为当前唯一1-based页号、`PageBorderWidth=0`、`Resolution=144`；每页独立流，DPI/尺寸进TF04读回 |

当前批准范围无参数推荐、自由REPX设计器、任意图表计算、打印/邮件/签章或外部打开能力；不能据“自动”字样追加这些功能。三语文本/字号/字体相同输入的分页以冻结SDK/字体实测Golden记录，不宣称跨SDK/Word像素或文件字节恒定。

### 7.2.2 字体映射、覆盖与长文本边界

字体绑定由R-A1自己验证：不可变`ReportingFontBinding(FontResourceId, SourceRevision FontFile, string AbsoluteFilePath, int FaceIndex, string FamilyName)`，读取部署文件并核hash；请求仍只有FontResourceId，路径不进Core/报告元数据/UI。绑定必须与宿主冻结Profile的FontResourceId及FontFile全部SourceRevision字段精确一致；AdapterRevision须绑定完整字体映射及字体文件SourceRevision，Input.Renderer/Verification.Adapter记录该不可变修订并精确比较；Profile留在宿主冻结配置和运行证据中，不给Core v0.2 Metadata新增Profile字段，不能只比family名字。读取期间保持只读文件租约且禁止写入/替换；实际SDK的已加载face/family与该文件的对应由同部署TF01资格证明，部署/font修订变化使原资格失效。资源Owner决定部署字体，Adapter验证实际bytes/face/family；不调用`DXFontRepository.Instance.AddFont/Clear/Dispose`，不改Windows字体设置，不默默fallback。FamilyName与实际SDK绑定须在TF01实际生成/读回确认。

无UI字体覆盖主路线是BCL有界读取OpenType `cmap`（[官方cmap规范](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap)，本轮定向实读），不依赖WPF窗口：校验sfnt/TTC头、FaceIndex、table偏移/长度checked不越文件；cmap优先(3,10) format12，其次platform0 format12，再(3,1) format4、platform0 format4；同优先映射不一致拒绝。Format12 groups必须start<=end且严格不重叠；字符c在组内glyph=startGlyphID+c-startCharCode，checked且glyph非0并小于maxp.numGlyphs才覆盖。Format4按有序endCode/startCode找段：idRangeOffset=0时glyph=(c+idDelta)&0xffff，否则从该idRangeOffset字本身地址+offset+2*(c-startCode)取UInt16 BE，值非0才加delta modulo65536；所有地址在subtable边界内，glyph非0且小于maxp.numGlyphs。Unicode按Rune解码，非法surrogate拒绝；U+0009/CR/LF为布局控制且不要求glyph，其它控制字符拒绝。此处仅字体字符覆盖技术，不做图像视觉算法；HALCON不适用。

生成前扫描本次实际显示文本、标题/单位/Validity/Reason、缺口及范围文字；缺码点返回受控诊断并`RPT-TEMPLATE-INCOMPATIBLE`，不看SDK方框替代成功。cmap不证明复杂脚本塑形、字体嵌入或实际页布局；三语由TF01/03验证，新增语言需同字体/脚本资格。WPF可用公开[GlyphTypeface.CharacterToGlyphMap](https://learn.microsoft.com/en-us/dotnet/api/system.windows.media.glyphtypeface.charactertoglyphmap?view=windowsdesktop-10.0)/[FontUri](https://learn.microsoft.com/en-us/dotnet/api/system.windows.media.glyphtypeface.fonturi?view=windowsdesktop-10.0)独立对照，但无UI流程不依赖WPF。

PDF检查字体嵌入与Unicode映射；Office/PRNX在同部署font binding下验证；PNG按144dpi实测三语截图/像素Golden。文字超`MaxTextUtf8Bytes`、Excel32767 UTF-16 code units、节点/页/输出预算均拒绝，不能省略、缩字或截断。CRLF/CR仅呈现层统一LF并换行，Metadata保留原字串；Verifier使用同一书面规则，不重算原数值/判定。

### 7.3 最小调用顺序

两无UI Host均以§14的进程根Owner取得槽位后，在该槽位原Task中调用ReportingFactory.Create(dependencies, options)；构造后调用Validate，再保存原`core.RenderAsync(request, businessToken)`到槽位，订阅提示按需。观察结束先query原intent，再CloseAsync独立cleanup deadline，DisposeAsync仍由槽位保持至完成。不能使用未定义的`reportingFactory.CreateScope()`、async using隐含无限等待或方法finally中释放仍在用的端口。完整根OwnerAPI与迟到处理见§14，不把此顺序当已编译示例。

### 7.4 Adapter公开装配、数据编码与独立核验

R-A1/R-A2不是“由将来实现者选择引擎”。两者由本模块`Asun.Modules.Reporting.DevExpress`的一个有界runtime提供同§3.4的IRenderAdapter/IArtifactVerifier；CSV使用BCL编码，DataXlsx用既定Workbook，其余用§7.2 XtraReport，不再引第三方报表/Office包。以下是新增Adapter装配声明规格，不修改Core v0.2或已接收codec/Host：

```csharp
// namespace Asun.Modules.Reporting.DevExpress;
public sealed record ReportingFontBinding(string FontResourceId,
    SourceRevision FontFile, string AbsoluteFilePath, int FaceIndex, string FamilyName);
public sealed record ReportingAdapterOptions(SourceRevision AdapterRevision,
    ReportBudget Ceiling, int MaxWorkers, string ControlledTempRoot,
    ImmutableArray<ReportingFontBinding> Fonts);
public interface IReportingAdapterRuntime : IAsyncDisposable
{
    IRenderAdapter Renderer { get; }
    IArtifactVerifier Verifier { get; }
    Task<DrainResult> CloseAsync(TimeSpan observationTimeout,
        CancellationToken cancellationToken = default);
}
// ReportingAdapterFactory.Create(ReportingAdapterOptions options,
//     IReportFileObjects files, IArtifactStore store, IReportingResourceMeter resources,
//     IDiagnosticsSink diagnostics, TimeProvider time) -> IReportingAdapterRuntime
```

Factory同步仅复制/shape检查、建立MaxWorkers有界槽和immutable能力（MaxWorkers为1..1024，Fonts按FontResourceId唯一，FaceIndex>=0，根路径绝对/由宿主提供）；无文件/字体IO、无SDK报告/线程文化。整个runtime在§14 Host根槽启动委托前由宿主依赖作用域强持，其Create不能在无根槽时启动后台任务；新session的worker原Task按§6先登记。字体读、暂存、DX同步/异步编码、独立Verifier均使用同runtime有限worker配额，不跨Dispatcher；工作未退出计配额，不为避免死锁开无界Task。Close停止新session/核验；原调用/session/文件归还后才runtime.Dispose完成；主机ReleaseHostDependencies委托按先Core后runtime关闭/Dispose顺序，业务错误与cleanup错误分离。borrowed Files/Store/Resources/Diagnostics/Time不由runtime释放。

worker执行槽按每次外调任务预约，执行至该任务及其派生SDK调用真实结束才归还；空闲session仍保留资源账本，但不持执行槽。Encode原Task结束后Verifier才能取得同一槽；session不得在持槽任务内等待另一排队任务。MaxWorkers=1也可按Encode→Verify→Close顺序完成，Close不抢占正在执行的槽或提前释放session。session内部锁防止同一可变report被并发调用，不把worker槽当session生命周期锁。

本版Adapter能力：Pdf支持Preview/Publish且必有PRNX，其它格式仅Publish；Png ProducesPageSet=true，其它false；NodeKinds五类均是既有受限节点投影，CSV/DataXlsx由Metadata保留非表格节点，不能声称布局像素一致。UsesBoundedInput只有TF05/BP-A1/A2证明物化、字体/图片/SDK文档、流/验证缓冲全部可预约计量后为true；未证明时false且只接受预先有限的诊断夹具，不获得生产容量资格。页数/缓存参数不允许掩盖无法界定的native峰值。

#### 7.4.1 固定CSV/DataXlsx列与原值规则

DataXlsx `part0001..partNNNN`：第0行表头，前两列`row_index`（从1起）、`stable_key`，后按part.Fields输入序各六列`<name>.source/display/unit/validity/reason/raw_invariant`，不得因当前UI隐藏列省略。type及字段Source/Scale在`metadata` sheet按part序/field序逐项列出，并由独立Metadata文件保留；不在value内新造业务状态。为避免Field.Name含点等导致拼接碰撞，写前构造全部表头做Ordinal唯一校验，冲突返回TemplateIncompatible。实际列数为2+6×fields，第0行计入Excel行限；空集仍有表头。`raw_invariant`始终是原Scalar可逆文本：Text/Identifier原字串、Integer十进制、Decimal G29、Boolean `true/false`、Timestamp UTC `O`、Duration `c`、EnumValue=`ContractId+LF+Key`（两个身份均不允许控制字符）、Evidence=ObjectId；非Valid为空。Timestamp source也为同UTC文本；Decimal/Integer只有按Excel double往返再转回原精确decimal/Int64相等才写numeric，否则source写原文本，type在metadata和raw保留，不作“精度丢失但成功”。Unit为空表示null，Reason/Display为空可为合法空字串，其null与empty精确区别以Metadata为权威；源Text空串同样不丢。每单元格禁止Formula/超链接setter，超32767 UTF-16 code units拒绝，不截断。

CSV恰1part，前四列`request_sha256/scope_id/row_index/stable_key`，每field按相同六列再加`<name>.type/raw_utf8_base64`；type为ReportFieldType稳定名字，raw_utf8_base64仅Text/Identifier为严格UTF-8的BCL Base64，其余空。所有cell按RFC4180：含逗号/双引号/CR/LF者包双引号，内部双引号写两次；每行CRLF，整文件仅开头UTF-8 BOM。先检测原字符串第一个非空白Rune是否`= + - @`，或原串以TAB/CR/LF开始，再对Text/Identifier的source/display/raw_invariant显示列前置单引号；raw_utf8_base64不加前缀。数字/Boolean/时间类型不执行文本formula判定；已以单引号开始的原Text仍由raw恢复。边界原字段类型、null/empty及上游原值精确比较通过Metadata，不以CSV空cell猜Missing。

Metadata sheet是固定Key/Value文本表：schema、identity、request、scope、snapshot、source/template/localization/renderer/Core版本、part/field/type/unit/scale、各part期望行数/hash、summary/Errors/证据身份及缺口按同闭包顺序；不嵌图片/JSON业务表。第0行严格为`key,value`，第1行`schema,report-sheet-v2`；其后从ReportMetadataHeader按§4位置字段顺序展开叶值，根路径为`header`，record段用本文件精确属性名、数组段用从0起Invariant十进制索引，以点连接。数组先写`<path>.count`，nullable先写`<path>.present`为0/1，仅present=1时展开值；字典按Ordinal key序写`<path>.<index>.key/value`，Scalar先写`<path>.tag`再展开已声明变体参数。普通叶value用同本节raw_invariant规则，enum为固定名字、SourceRevision逐属性展开；不把业务字段名嵌到路径。所有key唯一，全部cell为文本、无Formula；sheet行/文本上限先核，超出拒绝。sheet使用拟定Header的明确投影：Members固定为空数组，Verifier同样以独立Metadata Header清空Members后核对全部sheet键值；不把本Xlsx/Metadata自身hash写进sheet形成循环。独立Metadata文件才保存所有已封口Document/PRNX/PNG成员；宿主Profile由运行证据绑定，不增加Header未声明字段。严格编码规则已经在§3.4/4，实际字段不得从Spreadsheet当前值反推。报告本身不需要SQL/注册Schema；真实Stage/Claim/fencing/组可见性是宿主Store端口责任，不要求reporting再维护IM-066业务私表。

#### 7.4.2 完整元数据与核验的共同顺序

Verifier独立实例与Renderer可共用immutable契约、资源快照和预算，不能读Renderer“已通过”布尔值或重新调用WriteMetadata自证。先从Files用原授权开封口对象，流式核长度/SHA，核sealed/key/identity；所有解析深度/计数/解压/字体/图片缓冲计入Working/Temp/Input，早于分配预约。ZIP累计展开字节<=MaxTempBytes且每entry<=MaxWorkingBytes，XML禁止DTD/外部resolver，HTML无网络，PRNX只加载本模块封口对象；解析失败/预算超限不能发布。重复读取照§3.2计预算。

独立binary reader按§4的固定类型/tag/nullable/数组/字典顺序读`ASUN-META2`和Header，不接受未知schema/tag/非canonical decimal/非法UTF-8/乱序key/尾字节；逐part读Int64 count及完整行序，独立Append规则重建RowsSha256，与**源RangeProof**及同lease完整读取比较原值/显示/Unit/Validity/Reason，最后必须读到`END-META2`及EOF。字节字段仍按已批准codec，不另造Reader摘要/产品DTO。Header.Members须只含该format所有已核Document/PRNX/PNG，不含自身；Verifier通过注入Store.GetAsync(ArtifactId)逐项取原Staged/Verified/Published记录，核identity/format/role/pageIndex/ObjectId/封口hash/长度，再由Files开原ObjectId独立读回；Found但成员不同、NotFound或Unknown均不能通过。Store Stage/Seal必须让该精确记录在非公开内部读取可用，绝不把公开可见状态提前Published；Renderer清单只用于交叉比较，不代替Store原记录。

Encode按“封口所有Document/PRNX/PNG→用封口成员和拟定Verification写Metadata→封口Metadata→返回拟定RenderedArtifact”顺序结束；拟定值不代表独立验证。随后Core按§4.2先Verify所有Document/PRNX/PNG，再Verify Metadata并将其中拟定成员值与独立Verification逐项比较，全部一致后才整format组Publish/PreviewReady。不能在持一个worker的Encode里排队等待同runtime另一Verifier worker，造成MaxWorkers=1死锁。未完成元数据检查时只允许Staged/Verified内部状态。InputRowsSha256：1part为该part.RowsSha256，多part为`SHA256(ASCII ASUN-PARTROWS2 + 按Parts序UInt32 UTF8长度/PartId + Int64 ExpectedCount + UInt32 UTF8长度/RowsSha256)`，所有整数同§4使用little-endian；不把各part的count或hash相加。该聚合仅核验回执技术字段，不改变Request/Rows规范域或生产事实。

#### 7.4.3 各格式独立读取与拒绝条件

Metadata.Verify对每个成员在**同一Verifier worker**内再次执行下表的内部单对象核验，并将返回Verification逐字段与Header.Members比较；不递归调度另一个VerifyAsync、不缓存Renderer结果或建立隐含全局已验证字典。成本/流量计入原预算；资源不足返回BudgetExceeded，不能借“此前验证过”跳过当前封口对象。所有正式Verifier采用同一个固定解析规则，受测writer与reader分别实现，不以调用writer来比较hash代替reader。

| 格式 | 固定独立核验路径与判断 |
|---|---|
| Pdf | 本机`DevExpress.Pdf.PdfDocumentProcessor.LoadDocument(stream,false)`，保持read lease至processor.Dispose；Document.Pages.Count为实际页数，逐页GetPageText(1..N)，按§7.2.1行序/StableKey/源显示规则核完整有序文本，包括Unknown/原因/范围/附页，不只Contains某关键字。页内换行/重复列标题仅按固定规则移除，不能删任意空白造成串合；存在歧义时拒绝。字体嵌入/ToUnicode及无Action/Form/EmbeddedFiles由TF01对同版本输出资格确定，本次processor读回字符不等于嵌入已证明；无法从当前受控输出证明安全结构即失败，不调用未知PDF内部API |
| PRNX | 新的非UI`PrintingSystem`用LoadDocument(Stream)载入自有封口PRNX，核Pages.Count及Page.InnerBricks公开树、TextBrick文本、行序/StableKey/每必需节点；PanelBrick递归公开Bricks，其余容器沿InnerBricks，不能因基类Brick.Bricks默认空漏子项。遍历栈/计数有界，同对象visited避免双计，未知brick类型不可把必需文本忽略。PrintingSystem真实Dispose后read lease才归还。UI仍独立使用OpenDocument路径，不把此Verifier对象交DocumentSource |
| LayoutXlsx/DataXlsx | 独立Workbook.LoadDocument，布局格式核所有sheet呈现文本、行身份、无Formula；数据格式核固定sheet/列/原类型/raw及metadata键表，读回精确值与源重新比较。BCL ZipArchive先核package无外链/OLE/宏、无外部关系及所有entry边界；不信Workbook已加载就等于安全 |
| Docx | BCL ZipArchive+XmlReader独立核Content_Types、所有`.rels`拒绝TargetMode=External及oleObject/vbaProject/未知主动对象；只允许自有document/styles/fontTable/settings/media及本机SDK生成的已限定元数据/页眉页脚，未知part失败。按document.xml的w:t/w:tab/w:br及表格行顺序核可见文本/行身份/附件说明，media按关系定位证据并按§7.4.4核原图身份/尺寸及解码像素，不猜Word实际PageCount |
| Html | BCL流式tokenizer按字符状态Text/Tag/单双引号Attribute/Comment，严格UTF-8，最大token=MaxTextUtf8Bytes、栈深<=64、节点受Working限制；拒绝script/iframe/object/embed/form/base、on*属性、href及所有非data图片src、CSS url()/@import、未知实体/闭合歧义，禁止执行DOM或下载。实体仅amp/lt/gt/quot/apos及合法数字Rune；CSS由SDK生成的已限定布局属性，超出白名单失败。核完整Text流/行身份与Template/源，data图片Base64解码后按§7.4.4核原图身份/尺寸及解码像素。Renderer亦用此独立scanner审查生成文件后插入CSP，Verifier重新读封口文件核CSP，不以插入动作自证 |
| Csv | 独立BCL状态机解析BOM/双引号转义/CRLF/列数/末行EOF，核表头与期望行数/有序StableKey；严格Base64还原Text/Identifier，按原类型读取raw与Metadata，验证防公式前缀未修改原值；空集仍核范围。不能Split(',')或把检测formula当还原原值算法 |
| Png | 检查PNG签名、chunk长度/CRC、IHDR正尺寸/色彩、pHYs及完整IEND/无尾部，从DXImage读回实际尺寸，按页索引/144dpi/预算核N页；所有页与Metadata齐全才可组发布。图像栅格无法靠元数据证明文字/像素正确，TF04的同字体/SDK独立人工确认Golden用于取得该输出路线资格；本次只核结构/已资质路线/来源完整性，不伪造OCR或视觉测量来宣称每个字像素已证 |

PDF/PNG等呈现的实际字体/像素、PRNX恢复和超长行跨页是本模块真实资格用例，不是要客户提供内部解析算法。Verifier无法完成某项就`RPT-OUTPUT-INCOMPLETE`，不发布该format；已发布其它format保持。RecordCount固定为checked各part.ExpectedCount总和，不能把附页/标题计记录；Metadata精确保存每part，不让相同StableKey跨part互相替代。字体替换/排版变化不能只改hash使旧Golden继续PASS。

#### 7.4.4 解析的确定安全边界与反例

PDF的字形/嵌入/主动对象由Adapter独立BCL结构扫描补齐，不反射SDK内部：从最后有效`startxref`解析xref表或xref stream（W/Index字段及FlateDecode展开），追踪Prev并拒绝循环/越界；仅接受本次SDK单次输出、无增量修订的受控文件，出现Prev/XRefStm混合增量结构即拒绝，不猜同对象新旧定义。按xref定位间接对象，解析Name/Number/String/Array/Dictionary/Reference，stream以Length对应原字节切分而不是搜`endstream`。对象stream仅支持标准ObjStm+FlateDecode，N/First及对象偏移checked、全展开计Temp/Working；未知压缩/加密结构返回OutputIncomplete，不默默扫描原文件中的字符串。遍历Catalog/Pages/Resources的引用图，深度<=64，节点数/stream累计字节受Budget；解析Name先解`#hh`转义，拒绝越界长度和非法/缺失引用。引用图按(object number,generation)维护visited，每个对象只解析一次；共享字体或正常Page.Parent反向引用不算攻击。Pages树另沿Kids维护active-path，拒绝Kids祖先循环、重复叶页、Parent不匹配及Count与实际叶数不符；Parent只核身份不递归。安全检查覆盖所有可达对象，visited不能跳过首次字典检查。拒绝Root或任意页/annotation/names中的OpenAction、AA、JavaScript、Launch、URI、GoToR、SubmitForm、ImportData、RichMedia、EmbeddedFiles、AcroForm/字段和Filespec；即使键名压缩/转义也不能绕过。Document.OpenAction/Actions/AcroForm及Page.Actions/Annotations公开属性作为第二道交叉检查，不将对象非null本身当有害（空字典可存在）。

字体从每页有效Resources/Font解析FontDescriptor（Type0经DescendantFonts）；每个使用字体须有非空FontFile/FontFile2/FontFile3 stream、可解析对应ToUnicode CMap（bfchar/bfrange及codespace），实际字符非`.notdef`；匹配批准family/face或合法subset前缀。不以ASCII搜`FontFile`证明嵌入，不以Text extraction成功单独放行；实际字体subset/ToUnicode及像素仍须TF01资格。PdfDocumentProcessor负责PDF文本解析/页数，BCL扫描只补安全/字体结构，不能用自行光栅算法替代SDK。路线依据为PDF公开文件规范与本机25.2文档，非HALCON视觉路线。

图片完整性区分原文件摘要和导出媒体摘要：从Files独立读原ObjectId并核原Sha256，不能要求SDK重新编码的PNG/JPEG容器字节仍等于原hash。DOCX按image关系/出现顺序、HTML按img节点/出现顺序与同页证据身份说明逐项对应，缺项/歧义拒绝；两端用已核公开DXImage.FromStream读取，结果须为DXBitmap，保持原read lease至DXImage.Dispose。用公开DXBitmap.GetPixel(x,y)按y后x有界逐像素比较RGBA及Width/Height，透明像素四通道亦不忽略；逐图先预约两份解码及native预算，不物化额外全图数组。嵌入媒体保留原像素尺寸，缩放仅由布局几何呈现；有损重编码/降采样/色彩或alpha变化即OutputIncomplete，不用相似阈值放行。PDF/PRNX/PNG整页呈现的实际像素仍按TF01/04及受控来源绑定资格核验，不宣称每次逐字/逐图像素等价已证明。该比较是输出完整性，不引入图像检测算法或替代AsunImage。

HTML/CSS scanner白名单冻结为布局元素html/head/meta/title/style/body/div/span/p/br/table/thead/tbody/tfoot/tr/td/th/img；属性仅id/class/title/role/aria-label/colspan/rowspan/width/height/style及img的src/alt，meta属性仅charset/http-equiv/content/name，http-equiv只允许Content-Security-Policy且content必须等于本节固定CSP；name/content仅允许SDK生成无外部URL的文档元数据。CSS只允许字体族/字号/字重/颜色、背景颜色、宽高、margin/padding、border、display、position/top/left/right/bottom、text-align/vertical-align、white-space/line-height/overflow及table布局；值用数字/单位/颜色/批准字体/固定enum，拒绝url()/expression()/@import/backslash转义后主动内容。未知结构拒绝该format而非擅加执行权限；下次适配资格可通过只读实际输出扩展纯布局白名单，但须先改唯一指导。文档声明仅接受大小写不敏感的<!DOCTYPE html>，无外部标识/内部DTD；meta/br/img为void不入栈，其余元素必须按栈闭合，重复属性拒绝。所有比较支持HTML ASCII case-insensitive tag/attr，不在文本中查`script`误拒用户正常字符串。

新增规则并入现有TF用例，不另建过程测试工程：

| 现有用例 | 固定反例与期望 |
|---|---|
| TF01/03 | 单页A4宽210、左右10mm、两字段WidthMm=1/2，实际Margins按上取整到40报告单位，可用宽=`210×100/25.4−80`，列宽为该宽的1/3、2/3且末列恰到右界；Header/Footer各一次，跨页只重列标题。缺字体glyph/替换family/图形方框失败，不改源值 |
| TF01/05 | format4字符0x0041、delta=−64、rangeOffset=0→glyph1；rangeOffset分支原glyph0→不覆盖，即使delta非0；format12组[0x10000,0x10002]/startGlyph7→9；table越界/重叠组/未知format拒绝 |
| TF06 | 原Text `=1+1`→显示前置单引号且raw Base64 `PTErMQ==`；原TAB+`=1`→不因trim丢危险前缀；Integer −1仍number；`a,"b"`→CSV `"a,""b"""`，解析精确还原；原空Text与Unknown由Metadata区分 |
| TF07 | Integer9007199254740993及Decimal0.1234567890123456789012345678不能精确numeric往返→source/raw为原文本，metadata Type仍原类型；每field六列+前两列，超32767 UTF-16或含碰撞表头拒绝；无静默舍入 |
| TF01/02/03/04 | PDF的转义Name/ObjStm中JavaScript、缺FontFile/ToUnicode、Docx/Xlsx外部关系、HTML onload/CSS url/data非图片、PNG少页/CRC错均失败；未知数据不视为安全；PNG/字体实际像素Golden仍未运行 |
| TF08/TC09 | Metadata中ArtifactId合法但指向另一intent/role、Source同count而RowsSha不同、缺END/尾字节/多part摘要拼接次序错→不发布；先封口Metadata再独立Verify，不形成自身hash循环 |
| TF01/TC14 | PDF正常Parent反向引用/共享Font通过结构检查；Kids祖先循环、重复叶页、Parent错配/Count错误拒绝。MaxWorkers=1的Encode→成员Verify→Metadata Verify→session Close不死锁，原调用迟到仍计槽/资源；未取得完整生成资源上界的客户输入在SDK外调前拒绝 |

上述是确定的软件断言；客户工艺/字体部署选择、现场规模及性能阈值仍由各Owner/Profile提供。正式无UI测试不得拿PDF文本抽取或PNG元数据成功冒充实际版面/像素资格。

## 8. DZ-XVision 快照的可迁移事实与约束

以下事实来自只读快照 `docs/references/project-snapshots/DZ-XVision/20261004/`，不是本平台接口或生产能力证明。原工程中的 `SPC-YSmart30` 是 WinForms/DevExpress 查询与统计界面，`DZ-XVision` 是检测宿主；它们的数据库、全局计数、文件路径、消息框和控件状态不能直接迁入 Core。

### 8.1 现场报告和结果明细

快照中的单件结果对象可迁移的字段语义包括：程序名称、检测时间、条码、检测时长、总数/通过/错误计数、型号范围计数、检测结果、复判结果和图像拼版索引；逐功能结果还包含测试功能、功能名称、功能类别、测试值、标准、下限、上限和测试结果。来源：[SPC-YSmart30/SqlData.cs](../../references/project-snapshots/DZ-XVision/20261004/original/SPC-YSmart30/SPC-YSmart30/SqlData.cs) 的 `AllResult`、`DataResults`、`MeasureLineResult` 及相关结果类型。

迁移规则：

- 这些字段作为 `ReportPartInput` 的类型化投影和 `EvidenceReference`，由结果/计量/证据 Owner 提供；reporting 只绑定、分页和呈现。
- 原值、显示值、单位、有效性、上下限和判定来源分开保留。模板不能用显示值重新比较上下限，也不能由“错误”字符串推导新的质量决定。
- 图像拼版索引只能作为稳定证据引用的一部分；实际图像由证据 Owner 按 hash、保持期和授权提供，reporting 不拼图、不裁剪重测、不把文件路径当事实。
- 程序名称、条码、时间和型号是报告范围/身份字段，不是 reporting 自己的查询键；调用方必须同时提交 `ScopeId`、快照、字段版本和权限范围。

### 8.2 结果汇总和错误统计

快照中的汇总区分总数量、PASS、ERROR、复判后 PASS（原界面称误报/`RPASS`）和定位失败，并用饼图/标签显示直通率、不良率和误报率；运行宿主还保存当前产品与跨产品的累计 OK、NG、复判数量和 Yield。来源：[SPC-YSmart30.cs](../../references/project-snapshots/DZ-XVision/20261004/original/SPC-YSmart30/SPC-YSmart30/SPC-YSmart30.cs) 的查询与图表逻辑，以及 [DZ-XVision/DZXVision.cs](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/DZXVision.cs) 的运行计数逻辑。

这些是可迁移的“显示维度”，不是可迁移的计算实现：

1. 由统计/结果 Owner 提供 `ReportSummaryProjection`，显式给出总体、分子、分母政策修订、Unknown/Incomplete、复判语义、范围和完整性。reporting 不按页面平均百分比，不从总数减去其它列猜分母，也不把复判通过自动改成生产 PASS。
2. 分类和重叠关系完全由统计Owner冻结；复判通过可与最终通过重叠。reporting只校验§3.1显式Partitions，不发明互斥关系；未声明闭合关系不得从计数推导分母/总数。上游关系验证失败或来源修订不一致时返回RPT-SNAPSHOT-INCOMPLETE/RPT-SOURCE-CHANGED。
3. “定位失败”“采集失败”“保存失败”“MES 失败”“模板/导出失败”属于不同错误阶段。检测 ERROR 是结果事实，运行错误是诊断事实，人工复判是另一来源；reporting 只投影 `ReportErrorProjection`，不能把运行错误改写为 NG、PASS、放行或设备动作。
4. 汇总图表的颜色、标签和百分比只是显示策略。图表必须带范围、分母、来源修订和资格/缺口说明；资格不足时显示原因或不适用，不画出貌似有效的能力指标。

### 8.3 查询和跨文件合并的迁移边界

快照 SPC 界面支持条码、型号、起止时间、检测结果/复判结果筛选，遍历多个 SQLite 文件合并结果，并可按功能表查看明细。来源：[SPC-YSmart30.cs](../../references/project-snapshots/DZ-XVision/20261004/original/SPC-YSmart30/SPC-YSmart30/SPC-YSmart30.cs) 的查询逻辑。

接入 reporting 时必须改成：调用方先由 042/查询 Owner 生成参数化、带字段版本和稳定排序的固定查询快照，再把合并结果和完整读取证明交给 `ReportInputClosure`。禁止把原工程的字符串 SQL、动态表名、多个数据库逐个扫库、Grid 当前行或“没有再刷新”当作 reporting 的查询能力。条码、型号和时间边界的空值、时区、包含/不包含端点必须由查询 Contract 明确；起始时间晚于终止时间返回查询错误，不进入渲染。

### 8.4 导出需求的迁移边界

快照中的 SPC 导出通过保存对话框将当前结果 Grid 导出为 XLSX，并在导出后由 UI 启动文件。来源：[SPC-YSmart30.cs](../../references/project-snapshots/DZ-XVision/20261004/original/SPC-YSmart30/SPC-YSmart30/SPC-YSmart30.cs) 的导出处理。

平台迁移为显式 `ReportFormat.DataXlsx` 或 `ReportFormat.LayoutXlsx` 请求：

- “当前 Grid”必须替换为接纳时冻结的完整查询范围；当前选中行、当前页或可见列不能默认为完整导出。
- 文件名是受限显示建议，路径由 `IArtifactStore` 产生；Core 不弹保存对话框、不自动打开外部进程、不覆盖已发布文件。可选 UI 的“查看”仅选择本控件内已有受控PRNX；保存到宿主目标由宿主显式交付动作按ArtifactId/范围重新授权，不暴露原存储路径，不提供外部进程“打开”命令。
- 数据型 XLSX/CSV 保留字段类型和原值映射；版式 XLSX 明确合计、分组、分页和合并单元格的呈现限制。两者都要记录输入闭包 hash、范围、记录数、字节 hash、格式/适配器版本和发布回执。
- 导出失败、取消、磁盘不足或回执 Unknown 只改变对应产物状态；不能回写检测结果、计数、复判结果或设备状态。导出内容不等于客户签署、MES Applied 或质量放行。
- 快照的自动打开外部程序行为不迁入本模块；产品如需另行设计显式宿主动作，不在本批准范围提供ShellExecute/打印/邮件/签章入口。

### 8.5 错误日志和长期运行

快照中错误通过消息框、日志写入和运行列表显示，覆盖采集、图像拼接、定位、工具检测、结果保存、MES 进站/过站和线程停止超时等阶段。来源：[DZ-XVision/DZXVision.cs](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/DZXVision.cs) 的错误处理与 [DZ-XVision/PubParams.cs](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/PubParams.cs) 的运行计数/日志处理。

迁移时保留阶段、类别、影响范围、发生时间、可重试性和来源 hash；不要只保存本地化长文本。错误统计报告应能分别回答“检测结果错误多少”“运行错误多少”“保存/MES 错误多少”“哪些记录未闭合”，并说明统计范围和是否完整。日志写入失败、计数文件损坏、线程停止超时和数据库不可达必须返回诊断/Unknown，不得让上一轮累计计数继续冒充当前报告。

## 9. R-U1：可选 WPF/DevExpress 工作台实施规格

### 9.1 角色、实例和具体控件

操作者选择宿主已固定的范围与模板→预览核对→显式导出→查看各格式产物；质量角色核对总体/分母/来源；工程角色检查缺口/版本并恢复原ID。模块不执行刷新查询、批准模板、打印、签章、质量放行或自动打开外部进程。产品Shell持有权限和语言入口，独立控件不重复语言选择器。`ReportingWorkbenchControl`、`ReportingPresenter`位于`Asun.Modules.Reporting.Wpf`，不泄露产品ViewModel。

WPF实际装配沿§9.1.1工厂；工厂内部构造`ReportingPresenter(IReportingCore core, IReportDelivery delivery, ReportingViewContext context)`后以依赖属性`ReportingWorkbenchControl.Presenter`显式挂接；每control仅一个presenter。Presenter使用ICommand：Preview、Export、Cancel、QueryOriginal、SelectArtifact、ResetLayout；参数为明确identity/format，不由焦点/当前Grid推断。`SetViewContext(ReportingViewContext)`递增ViewEpoch、撤旧订阅并异步归还旧view lease，不dispose Core。`SetLanguage(LocalizationData)`只换chrome文本；在途报告资源快照不变。`DetachAsync`返回Task<DrainResult>、观察截止点与根Owner一致，卡住的Dispatcher不能伪detach完成。

```csharp
public sealed record ReportingViewContext(long ViewEpoch, string ConsumerId,
    string RequesterId, string AuthorizationScopeId, RenderRequest Draft,
    LocalizationData UiLanguage);
public sealed record ArtifactReadRequest(ArtifactId ArtifactId, string ConsumerId,
    string RequesterId, string AuthorizationScopeId, long Offset, long? Length);
public interface IReportDelivery
{
    ValueTask<PortResult<IFileReadLease>> OpenAsync(ArtifactReadRequest request,
        CancellationToken cancellationToken);
}
```

IReportDelivery在Core工程定义；实例由宿主用同一Store/Files/Auth装配。每次读取先以请求Consumer/Scope/ArtifactId核`lookup-artifact`栅栏，再Get原artifact并核返回Identity.ConsumerId一致，再授权`read`及范围，OpenRead核hash；Offset>=0、Length若非null必须>0且checked边界<=ByteLength，null表示Offset至EOF；返lease.Content为受限range流，其Length仍声明对象总长、不能越授权range读；Range交付仍走Owner栅栏，无法确认授权即拒绝。Pdf的Publish同样产生PreviewDocument(PRNX)，作为该format必需成员与Document/Metadata一起发布；其它格式从已有Pdf关联产物预览，若不存在需宿主显式创建新Pdf Preview intent，不根据当前Grid偷偷重跑。Preview只允许PreviewReady/Published的受控PRNX和已Verified Metadata；正式Published其它格式提供授权读取，不用随意路径。Delivery不创建新报告、不重查业务表。view lease归UI根Owner，Core关闭不强制关闭已借用流。Store保持到期与撤权只阻新读取，已打开流的截停以Owner协议明确，不能只靠按钮灰掉宣称撤权线性化。

### 9.1.1 公开WPF装配与权限投影

本工作台直接消费Core、Delivery及受控PRNX；**不直接引用IM-060 viewport**，不显示原HImage/Tile/3D模型，不把图像操作/ROI编辑塞入报告页。因此viewport Assembly v0.2的Presentation/Lifetime/Unbind不适用；现有Core Root/Close沿§6/14复用，PRNX视图生命周期沿§9.2.1，无第二套借用显示Owner。控件中的图片仅为已生成报告页的静态证据，页导航/缩放/搜索不能改原证据或生产事实。

以下是Wpf公开装配增补；原三参数ReportingPresenter构造仍只建纯命令/投影，不创建窗口/临时文件/后台任务。实际控件预览必须经同view根Owner的工厂；不提供自动静态根或默认临时目录：

```csharp
// namespace Asun.Modules.Reporting.Wpf;
public sealed record ReportingViewOptions(string ViewId, string ControlledTempRoot,
    ReportBudget Ceiling, TimeSpan ObservationTimeout);
public sealed record ReportingViewOwnerOptions(int MaxViews, long MaxRetainedBytes,
    TimeSpan CloseObservationTimeout, TimeSpan RecheckInterval);
public sealed record ReportingViewPermissions(string ConsumerId, string RequesterId,
    string AuthorizationScopeId, SourceRevision Policy,
    DateTimeOffset ValidUntilUtc, bool CanPreview, bool CanExport,
    bool CanRead, bool CanQuery);
public interface IReportingWorkbenchBinding : IAsyncDisposable
{
    ReportingWorkbenchControl Control { get; }
    ReportingPresenter Presenter { get; }
    string ViewId { get; }
    void SetPermissions(ReportingViewPermissions permissions);
    Task<DrainResult> DetachAsync(TimeSpan observationTimeout,
        CancellationToken cancellationToken = default);
}
// ReportingWpfOwner(ReportingViewOwnerOptions options,
//     IDiagnosticsSink diagnostics, TimeProvider time)
//     Query() -> ImmutableArray<ReportingViewOwnerSnapshot>
//     StopAndObserveAsync(TimeSpan timeout, CancellationToken token) -> Task<DrainResult>
// ReportingViewOwnerSnapshot(string ViewId, OperationIdentity Identity,
//     ResourceState Resources, long ReservedBytes, RenderError? Error)
// ReportingWorkbenchFactory.CreateBinding(ReportingWpfOwner owner,
//     IReportingCore core, IReportDelivery delivery, ReportingViewContext context,
//     ReportingViewOptions options) -> IReportingWorkbenchBinding
```

工厂必须在所属Dispatcher调用；Owner同步先预约ViewId唯一槽和`checked(Working+Temp+Output)`保守字节，再保存构造Starting、core/delivery/context/options；成功前不创建Control/Presenter，容量不足无预览任务。构造逐对象记入同槽后交Binding，失败仍由原槽清理已生成对象；构造只建控件树/事件/immutable配置，不读文件/开PRNX。MaxViews为1..1024，MaxRetainedBytes>0，观察/复查期限按§3.2时间有效域；view预算不超Core Ceiling，双控件各有独立binding/dispatcher affinity/消息桥。§9.2.1所有DispatcherOperation.Task、Delivery.ValueTask一次AsTask、copy/Open/Find/Close/lease.Dispose原Task在此槽先登记，迟到归原view/epoch而非新绑定。Control.Presenter属性仅接此工厂生成的所属Presenter，不允许同Presenter多Control。

SetViewContext先冻结旧epoch、关闭旧文档/租约，再启该view新context；旧项未排空则保留旧子槽及字节，若预览配额不足不启动新文档。原RenderTask/订阅通知在Presenter槽观察但Core是借用，不由Binding Dispose取消/释放；Cancel仍独立按原intent发命令。Detach/Dispose共用一次cleanup，Detach仅有限观察，Dispose等待原cleanup；Owner.Query按ViewId列原identity/资源状态，StopAndObserve只停止视图新接纳/Detach，不停止共享Core。有界根独立复查，Dispatcher阻塞及关闭后失败保留原任务/SDK model/路径，不能把Unloaded/GC当Released；应用根在所有binding真Released前持Owner，跨进程不转移WPF对象。

权限按钮初始全Unknown禁用，SetPermissions由宿主授权Owner提供immutable投影；有效期/Policy与context范围一致后仅决定CanExecute和提示。过期/撤权事件立即冻结新view请求与Export/Read，不以灰按钮完成撤权；实际Render/Publish/Delivery仍走原授权端口栅栏，拒绝/Unknown保留原intent查询。控件不从角色字符串、已有Published或历史允许推导权限。恢复权限时只查原ID并显式预览，不能自动生成或重发发布。TextBox/IME、ResetLayout、复制身份为本地无副作用命令，不授设备/质量放行权。

两WPF Host在Wpf.TestHost分别构造独立STA/Dispatcher的SingleInspection view与BatchQuality view，借§14双Host/同v0.2请求；各应用根先建自己的Owner再CreateBinding，明确ControlledTempRoot/预算/三语资源/权限投影。TU03–08检查双owner/同Core借用隔离、构造失败/容量拒绝、SetViewContext迟到、原Task/lease清理和全部原生命令入口；不是两个标签页共用一个静态Presenter作为第二消费者。真实DevExpress/字体/1920×1080/UIA验证仍为运行门。

### 9.2 固定1920×1080构图与联动

只用一个固定1920×1080验证viewport；不改显示分辨率。按实际DPI记录WPF DIP客户区并扣任务栏、标题、边框和宿主状态区，不用屏幕物理像素充当可用DIP。设计参考客户区1888×960 DIP（100%时），使用容器约束而非硬写屏幕尺寸：顶部56、范围条64、底部状态28，中部剩余；左模板/格式280（min240 max360）、右来源/缺口320（min280 max420）、中央预览占剩余且min720；底部产物面板180（min140 max240）从中部下方分配。实际客户区更小时先折叠右Inspector，中央优先；禁止隐藏状态/取消/Unknown提示。若DPI导致最小总宽不足，控件提供内部水平滚动且记录资格限制，不追加其它分辨率矩阵。

| 区域 | 25.2.3具体接入 | 信息及状态/联动 |
|---|---|---|
| 容器 | DockLayoutManager + LayoutGroup(Orientation)/LayoutPanel；常用面板AllowClose=false，AllowFloat=false；右Inspector可AllowHide=true | 工程角色可调整内部布局并由宿主保存自有布局配置，生产角色锁布局；ResetLayout只复位布局、不改报告 |
| 顶部 | 自有DevExpress Bars命令及实例BarItem.SuperTip（SuperTip.Items/Content） | 预览、导出、取消、查询原结果始终直达；限制/恢复解释不藏关键命令；权限Unknown禁新执行并显示原因 |
| 左侧 | GridControl.ItemsSource绑定不可变模板/能力投影，GridControl.View=TableView、AllowEditing=false；格式独立勾选 | 选模板显示版本/hash/用途；格式能力不符显示明确原因，禁止自动替代；高级预算只读展开 |
| 中央 | DocumentPreviewControl；OpenDocument(实例自有PRNX路径)；RequestDocumentCreation=false、AllowDocumentEditing=false、AllowCachePages=false、CommandBarStyle=None | 禁用内置导出/打印/保存/邮件/参数改动绕过Core；自有工具条页导航、缩放、搜索，均只作用文档视图；不重新生成当前数据 |
| 产物 | GridControl + 只读TableView，字段为格式/角色/状态/页或记录数/大小/原ID/时间/错误 | 选择产物以ArtifactId+epoch定位预览及右Inspector；Unknown行提供QueryOriginal，不显示成功勾；多格式Partial保留已发布项 |
| 右侧 | 只读来源/范围/统计关系/缺口/错误Inspector | 展示实际template/data/statistics/resource/adapter revision、原值/显示/单位/Validity；错误选择定位本报告node/page或缺口ID，不跳到其它产品页面 |
| 底部 | 自有状态条 | 阶段+已处理/总量、资源Retained/Released、原intent；总量未知用“不确定”，不可伪百分比；错误含影响和下一步 |

### 9.2.1 受控 PRNX 恢复与实例关闭的唯一接线

冻结路线为`DocumentPreviewControl.OpenDocument(string filePath)`，本机25.2.3官方XML明确“Opens the specified document in the current Document Preview Control”，继承的DocumentViewerControl同名入口明确从指定文件加载。每次预览使用新control/新加载账本，控件为Wpf内部实现；模块消费者只持ReportingWorkbenchControl，不取得SDK Document/PrintingSystem。仅载入本模块已Verified且身份/hash/完整Metadata匹配的PreviewDocument，不能用任意文件选择、REPX或未校验PRNX。内部步骤固定如下：

1. UI根Owner在Delivery.OpenAsync之前预约view槽、read lease、拷贝缓冲、临时文件及后续预览资源，登记Starting；源请求必须Offset=0/Length=null。取得lease后流式复制到宿主明确提供的受控临时根下、由本view生成的随机唯一`.prnx`文件；不采用SuggestedFileName/外部路径。文件CreateNew、写入期间不可读、长度及SHA-256与ArtifactResult逐项一致，完成并关写流才准交SDK。Temp记录全文件字节，Working记录拷贝缓冲及预览实际资源；超预算或计量不全停止新加载。关闭原read lease的唯一原Task实际完成后可归还该lease，但临时文件继续归view槽，不用DeleteOnClose抢先删除SDK仍可能读取的路径。复制失败/取消只回收已确认无人使用的本次文件。
2. 所属Dispatcher创建preview并先配置RequestDocumentCreation=false、AllowDocumentEditing=false、AllowCachePages=false、CommandBarStyle=None；ShowNavigationPane/ShowThumbnails/AutoShowDocumentMap/AutoShowParametersPanel全部false，UseAsyncDocumentCreation设DevExpress.Utils.DefaultBoolean.False。最后一项只控制报告创建，不据此断言PRNX加载没有异步工作。先装§9.3.1两个实例服务模板及命令拦截，再订阅DocumentChanged、DocumentLoaded、页码/缩放事件。DocumentChanged时立即强持实际Document并订阅其公开DocumentException，替换时先记录旧model到同槽，不能丢引用。DocumentSource保持未绑定，不调用CreateDocument/RequestDocumentCreation命令。
3. OpenDocument调用前预登记原DispatcherOperation、其Task占位、加载完成屏障及旧/new model引用，且只调用一次；Dispatcher.InvokeAsync返回的**同一个Task**纳入根Owner。DocumentLoaded只完成该control/ArtifactId/epoch的加载屏障；核Document.IsLoaded=true、IsCreating=false且PageCount等于已Verified PRNX页数后才能Ready。返回void、Dispatcher Task完成、IsLoaded或窗口可见单独均不等于ResourcesReleased。同步异常、DocumentException、实例消息桥错误都使本次加载Failed，进入关闭而不是重新载入。事件处理短且无IO；通知不猜领域错误，使用RPT-OUTPUT-INCOMPLETE/受控详情。若选择已换epoch，迟到文档只进入原槽关闭，不挂到新选择；同槽不同时调用Open/Find/Close。
4. Detach先冻结新命令/选择并递增epoch，保留生命周期事件以观察迟到，等本槽已登记的Open/Find/页操作及事件投递退出；加载尚无完成/失败信号时继续Retained，观察到期返回DrainUnknown。加载/创建确认退出后，在同Dispatcher预登记并执行CloseDocumentCommand（先CanExecute(null)，再Execute(null)），保留其原Dispatcher Task；不dispose SDK内部Document/PrintingSystem，不反射其内部资源。若CanExecute=false且Document仍非null，不伪关闭成功。
5. 关闭的可观察必要条件：原调用Task实际结束、加载屏障已完成或有确定失败、保存的model不再IsCreating、DocumentChanged观察到preview.Document=null、PageCount=0、全部实例回调退出。此后撤DocumentException/DocumentChanged/DocumentLoaded及键盘/鼠标/页码/缩放handler，两个服务解除Owner、控件脱离可视树/Presenter。临时文件以独占读写方式再次打开成功并关闭后，才删除该**确切自有文件**；无法独占、原Task未终结、Dispatcher卡住、关闭状态不符或资源账本未确认时，保持原control/model/路径/保守字节在原槽并独立复查，不启动替代清理Task。重复Detach共用该关闭Task；取消只取消观察，不遗弃清理。

上述公开状态和文件独占检查分别证明显示文档退出及文件不被占用，不能单独证明native缓存/线程全部释放。TU07–08须在目标SDK真实验证该固定关闭路线的资源归还，资源计量/资格不能确认时实现返回DrainUnknown并保留槽，不能自填Released。这里已冻结调用、状态、所有权和失败行为；真实编译、SDK关闭/资源测量与呈现资格属于实施验证，不留内部类型转换或清理策略待设计。

### 9.3 状态、键盘、三语和恢复

空态显示“请选择报告范围”；忙态冻结当前draft、保留取消/原ID查询；正常Ready显示实际快照/模板/语言；缺口状态显示未知/缺失来源，不作绿色成功；错误态保留draft/选择/滚动位置和原ID；无权限显示受影响能力；完成态逐产物显示状态，资源未归还时仍显示“正在释放资源”。刷新范围是宿主获得新快照后调用SetViewContext，新intent；已发布同intent不因刷新重写。连点以intent幂等，不创建多任务；Preview→Export是新关联intent且明确同闭包，不能把Preview产物登记为正式Published。

Tab顺序：模板→格式→预览→导出→取消→页导航→产物→Inspector→查询原结果；Enter只执行当前聚焦按钮，不将Grid选行自动导出；Esc只关非模态提示/编辑焦点，不取消后台；Ctrl+P预览、Ctrl+E导出、Ctrl+F文档搜索，焦点在文本输入/IME组合时不抢快捷键。取消必须显式按钮命令；窗口X仅Detach，由宿主决定是否Cancel。每控件有AutomationProperties.Name/HelpText/AutomationId，焦点可见；颜色同时有状态文字/图标，长ID可复制、文本不截断，详情可滚动。

| 资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| reporting.preview | 预览 | 預覽 | Preview |
| reporting.export | 导出 | 匯出 | Export |
| reporting.cancel | 取消 | 取消 | Cancel |
| reporting.queryOriginal | 查询原结果 | 查詢原結果 | Check original result |
| reporting.scope | 数据范围 | 資料範圍 | Data scope |
| reporting.releasePending | 正在释放资源 | 正在釋放資源 | Releasing resources |
| reporting.publishUnknown | 发布结果待确认 | 發佈結果待確認 | Publication unconfirmed |
| reporting.partial | 部分完成 | 部分完成 | Partially completed |
| reporting.authUnknown | 权限待确认 | 權限待確認 | Permission unconfirmed |

全部标题、列名、单位、命令、状态、错误/恢复/诊断从冻结资源键取得；RPT-*映射`reporting.error.<code>`及`reporting.recovery.<code>`。实例接线固定为§9.3.1；资源缺失阻止本次chrome批次采用并保留旧语言+缺词诊断，不显示key/空串作成功。后续R-U1只验证真实三语呈现、完整词条与自然术语审校，不再待设计全局/实例localizer路线。

R-U1验收须在真实WPF记录固定viewport客户区/DPI：三语长文本、Tab/快捷键/UIA、布局复位、慢/迟到预览、Unknown查询、关闭view不取消其它intent、双control隔离、切语言不改在途资源、权限撤销/恢复、半文件不可读、Dispatcher阻塞后迟到dispose。统一主题/字体/间距/图标由宿主design-system实例资源注入，不写模块私有机台主题。静态截图/HTML/Simulator不能代替真实控件交互及资源验证。

### 9.3.1 实例三语、导航/搜索与原生消息服务

报告文档使用request冻结的LocalizationData，不受SetLanguage影响；chrome使用该Presenter独有UiLanguage快照。每次SetLanguage先在内存解析本view全部资源/三语覆盖表，成功后在所属Dispatcher按language epoch一次更新chrome及本view PreviewMessageBridge.UiLanguage快照；桥自身保持同一实例以免失去原调用归属，在途回调用入口捕获的旧快照，后续消息取新快照；失效epoch不写入，不能改Application.Resources、Thread.CurrentCulture/CurrentUICulture、PrintingLocalizer.Active或GridControlLocalizer.Active。宿主控件实例主题与UI语言分别注入；A/B control不共享可变资源集合、服务或Presenter。

| 表面 | 固定25.2.3实例写入路径 |
|---|---|
| 自有命令/提示/状态/Inspector | BarItem.Content、BarItem.SuperTip中SuperTipItem.Content、自有TextBlock.Text、AutomationProperties.Name/HelpText及自有搜索输入标签；无原生Ribbon/toolbar |
| Dock标题 | BaseLayoutItem.Caption/TabCaption；更新本control对应item，不遍历其它窗口或宿主布局 |
| 每个Grid TableView | 新建该view独有GridRuntimeStringCollection，逐项RuntimeStringIdInfo(GridControlRuntimeStringId,string)，一次赋DataViewBase.RuntimeLocalizationStrings；至少NoRecords、NoRecordsFound、GridGroupPanelText，使用[localization §7.2](../localization/DEVELOPMENT-GUIDE.md#72-2523-实例接入)已冻结的支持边界；其余native菜单/过滤器本工作台不开放 |
| 文档页导航/缩放 | 自有三语按钮/数值输入；DocumentLoaded后使用preview.PageCount/CurrentPageNumber，校验1..PageCount才写CurrentPageNumber；监听CurrentPageNumberChanged回投影。自有缩放调用ZoomInCommand/ZoomOutCommand（CanExecute后Execute(null)）并监听ZoomChanged，显示ZoomFactor；无文档时全禁用 |
| 文档搜索 | 自有输入与前/后查找按钮，长度1..MaxTextUtf8Bytes，构造TextSearchParameter { Text, CurrentPage=preview.CurrentPageNumber, SearchDirection=Forward或Backward, IsCaseSensitive=false, WholeWord=false }，调用FindTextCommand；它搜索当前PRNX，不调用ShowFindTextCommand或原生搜索侧栏。调用也先入view账本，同槽串行；搜索不重新渲染/取数 |

工作台自己的PreviewKeyDown仅在其preview子树内拦截：Ctrl+P/E/F转本Presenter相应命令并Handled；其它组合仅允许当前文档导航键、Tab/Shift+Tab、复制选择Ctrl+C，阻断其余SDK快捷入口；搜索输入/IME仍遵循§9.3，宿主窗口关闭由宿主处理。preview的ContextMenuOpening直接Handled；所属实例CommandManager.PreviewExecuted再按页导航/缩放/文档复制白名单拦截路由命令。CommandBarStyle=None只是布局设置，不能单独作权限证明；不得把SDK Export/Save/Send/Print/PrintDirect/PageSetup/Open命令暴露到BarItem、UIA或产品调用方。权限判断及正式导出始终经Core/Delivery，模块不实现打印/签章。

原生搜索通知/加载错误通过公开MessageBoxServiceTemplate和DialogServiceTemplate注入，不能落回SDK默认弹窗。Wpf内部定义`ReportingPreviewServices : DevExpress.Mvvm.UI.ServiceBase, IMessageBoxService, IDialogService`；定义自己的Owner依赖属性，类型为本view专有`PreviewMessageBridge`（持Presenter、control epoch、UiLanguage只读快照、受限状态投递入口）。每个preview从模块固定编译XAML工厂取得两个**全新**DataTemplate，分别赋MessageBoxServiceTemplate/DialogServiceTemplate。模板各自Resources内有独立PreviewBridgeReference，服务Owner使用Source明确指向此reference的单向Binding；装配者在交SDK前把reference.Bridge置为本view bridge。reference实现INotifyPropertyChanged，关闭时置null并通知，服务Owner随之失效/清引用。ServiceBase的公开基类链为ServiceBaseGeneric/Behavior/AttachableObjectBase/Animatable，并非FrameworkElement，故不使用FrameworkElementFactory包装服务根；服务模板按固定编译XAML加载，不接受外部XAML。资源reference不存放在Application或共享主题字典；模板/服务实例相互独立，不猜SDK模板DataContext、不解析隐藏ViewModel、不用ServiceLocator/全局Active。服务不创建窗口/设备命令；任何迟到Show只安全返回并纳入原槽回调退出。

每个模板固定内容如下；这只是Wpf内部接线规格。PreviewBridgeReference.Bridge类型为PreviewMessageBridge?，初始null；只有该view装配/关闭者写入。所有者为空时服务返回同样安全拒绝，不等待绑定：

```xml
<DataTemplate xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
              xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
              xmlns:local="clr-namespace:Asun.Modules.Reporting.Wpf">
  <DataTemplate.Resources>
    <local:PreviewBridgeReference x:Key="OwnerRef" />
  </DataTemplate.Resources>
  <local:ReportingPreviewServices Owner="{Binding Bridge, Source={StaticResource OwnerRef}, Mode=OneWay}" />
</DataTemplate>
```

调用固定为`((PreviewBridgeReference)template.Resources["OwnerRef"]).Bridge = bridge`，再赋对应preview模板属性；Factory两次创建资源实例，不把已用模板给另一control。服务回调开始即捕获Owner/epoch及UiLanguage快照，结束计入原槽；关闭置null不删除仍在执行的回调。这里只使用模板显式Source，不依赖模板服务宿主的DataContext或自动服务查找。

精确接口按本机Mvvm公开XML冻结：

```csharp
// Wpf内部服务实现的方法形状；不是Core public API。
DevExpress.Mvvm.MessageResult Show(string messageBoxText, string caption,
    DevExpress.Mvvm.MessageButton button, DevExpress.Mvvm.MessageIcon icon,
    DevExpress.Mvvm.MessageResult defaultResult);
DevExpress.Mvvm.UICommand? ShowDialog(
    IEnumerable<DevExpress.Mvvm.UICommand> dialogCommands,
    string title, string documentType, object viewModel,
    object parameter, object parentViewModel);
```

Show只把已知预览通知映射到自有状态区：每次预登记FindText前，以只读PrintingLocalizer.GetString分别取得PrintingStringId.Search_EmptyResult和SearchFinished_NoMatchesFound的当前SDK文本，保存该调用局部映射，不改Active；回调仅在同control/epoch搜索上下文且messageBoxText逐字匹配时显示`reporting.search.noMatches`。其默认英文原文分别为“Your search did not match any text.”及“Finished searching throughout the document. No matches were found.”，不按包含词/翻译猜测。其它消息、SDK上下文不匹配或未知枚举一律显示`reporting.preview.operationFailed`，记录受限原文长度/hash/阶段供诊断（原生原文不是三语状态），加载阶段同时标记失败进入§9.2.1关闭；不改变报告事实或质量结果。Show返回固定安全值：OK→OK（仅通知确认）、OKCancel→Cancel、YesNo→No、YesNoCancel→Cancel、未知→None，不采用defaultResult、不隐式确认动作。ShowDialog不调用/执行传入UICommand、不打开内置参数/导出/打印窗口，投递operationFailed并返回null；这是禁止SDK附加操作的明确恢复路径，不把任意SDK对话内容翻译成业务许可。

新增固定资源：`reporting.search.noMatches`=`未找到文本 / 未找到文字 / No matching text`；`reporting.preview.operationFailed`=`预览操作未完成 / 預覽操作未完成 / Preview operation did not complete`。TU01–08须实测当前语言搜索无结果、未知SDK消息、双实例并发切换、所有快捷键/右键/UIA入口及事件回收；不能以服务模板赋值或截图代替成功接线/关闭资格。

### 9.4 视觉细节、三语资源与精确恢复

在§9.2构图内使用宿主design-system实例主题；基础8DIP间距、命令高32DIP、正文14DIP/身份等宽12DIP、标题18DIP、状态图标16DIP，主预览工具栏48DIP内保持页码/缩放/搜索同一行。只有Preview为强调按钮；Export依据授权与范围显式可见，Cancel/QueryOriginal在Unknown/忙态保持直达。Dock布局仅当前view可调整，ResetLayout恢复本view初始比例，不删除用户宿主配置。Grid默认无分组、无自动过滤/合计/导出；详细缺口/身份用右Inspector和可滚动详情，不能省略被选产物状态。完整identity支持复制，窄列ellipsis必须配实例SuperTip显示全值；不可让“文本不截断”成为撑开整个viewport的布局策略。

View状态以资源键为唯一文字；机器枚举只用于投影，不直接显示英文enum/key。颜色沿宿主主题语义，状态至少同时有图标+文字；布局选择/展开只用短120ms透明度过渡，Busy/Cancel/Unknown等关键反馈立即变化、遵循OS减少动画策略，不用动效延迟命令。恢复路径为保留范围/模板/选中Artifact/原ID→显示下表→只执行对应安全动作，不自动重试发布。

| 资源键/覆盖 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| reporting.title / reporting.record | 报告 / 记录 | 報告 / 記錄 | Report / Record |
| reporting.template / reporting.format | 模板 / 格式 | 範本 / 格式 | Template / Format |
| reporting.page / reporting.zoom / reporting.search | 页 / 缩放 / 搜索 | 頁 / 縮放 / 搜尋 | Page / Zoom / Search |
| reporting.previous / reporting.next / reporting.resetLayout | 上一个 / 下一个 / 重置布局 | 上一個 / 下一個 / 重設版面 | Previous / Next / Reset layout |
| reporting.source / reporting.identity / reporting.missing | 来源 / 身份 / 缺失 | 來源 / 識別 / 缺失 | Source / Identity / Missing |
| reporting.empty / reporting.busy | 无记录 / 正在生成报告 | 無記錄 / 正在產生報告 | No records / Generating report |
| reporting.state.Planned/Staged/Verified/PublishPending | 计划生成 / 暂存 / 已校验 / 正在发布 | 計畫產生 / 暫存 / 已驗證 / 正在發布 | Planned / Staged / Verified / Publishing |
| reporting.state.Published/PreviewReady/Failed/Cancelled | 已发布 / 预览就绪 / 失败 / 已取消 | 已發布 / 預覽就緒 / 失敗 / 已取消 | Published / Preview ready / Failed / Cancelled |
| reporting.state.Unknown/NotRecoverable | 结果待确认 / 无法恢复 | 結果待確認 / 無法復原 | Result unconfirmed / Cannot recover |
| reporting.resource.Retained/DrainUnknown/Released | 资源仍持有 / 资源释放待确认 / 资源已释放 | 資源仍持有 / 資源釋放待確認 / 資源已釋放 | Resources held / Release unconfirmed / Resources released |
| reporting.validity.Valid/Unknown/Missing/NotApplicable/Invalid | 有效 / 未知 / 缺失 / 不适用 / 无效 | 有效 / 未知 / 缺失 / 不適用 / 無效 | Valid / Unknown / Missing / Not applicable / Invalid |
| RPT-REQ-INVALID/INVALID-MODE/VERSION-UNSUPPORTED | 请求无效。检查参数和版本。 | 請求無效。檢查參數與版本。 | Invalid request. Check parameters and version. |
| RPT-AUTH-DENIED/AUTH-UNKNOWN | 无权限或权限待确认。联系管理员。 | 無權限或權限待確認。聯絡管理員。 | Permission denied or unconfirmed. Contact an administrator. |
| RPT-SNAPSHOT-NOT-FIXED/SNAPSHOT-INCOMPLETE/SOURCE-CHANGED | 数据范围已变更或不完整。重新固定范围。 | 資料範圍已變更或不完整。重新固定範圍。 | Data scope changed or is incomplete. Fix the scope again. |
| RPT-TEMPLATE-NOT-FOUND/INCOMPATIBLE/UNTRUSTED | 模板或字体不可用。选择已批准版本。 | 範本或字型無法使用。選擇已核准版本。 | Template or font unavailable. Select an approved revision. |
| RPT-FORMAT-UNSUPPORTED/BUDGET-EXCEEDED | 格式或资源预算不支持本范围。调整范围或配置。 | 格式或資源預算不支援此範圍。調整範圍或設定。 | Format or budget cannot support this scope. Adjust the scope or configuration. |
| RPT-SOURCE-UNAVAILABLE/OUTPUT-INCOMPLETE | 数据或文件不完整。查看缺失项。 | 資料或檔案不完整。查看缺失項目。 | Data or files are incomplete. Check missing items. |
| RPT-CANCELLED/TIMEOUT | 操作已取消或超时。等待资源释放并查原结果。 | 操作已取消或逾時。等待資源釋放並查詢原結果。 | Cancelled or timed out. Wait for resources and check the original result. |
| RPT-PUBLISH-UNKNOWN/CLAIM-UNKNOWN/STORE-UNKNOWN | 结果待确认。查询原结果，勿重复生成。 | 結果待確認。查詢原結果，勿重複產生。 | Result unconfirmed. Check the original result before generating again. |
| RPT-CONFLICT | 原请求内容不同。检查原意图。 | 原請求內容不同。檢查原意圖。 | Request content differs. Check the original intent. |
| RPT-DRAIN-UNKNOWN | 资源尚未释放。保留原操作并联系维护。 | 資源尚未釋放。保留原操作並聯絡維護。 | Resources are still held. Keep the original operation and contact support. |
| RPT-INTERNAL/OBSERVER-DETACHED | 操作或通知失败。查询原结果并保留诊断编号。 | 操作或通知失敗。查詢原結果並保留診斷編號。 | Operation or notification failed. Check the original result and keep the diagnostic ID. |

表中的slash分列仅减少正文重复；实现必须为每个完整`reporting.error.<Code>`和`reporting.recovery.<Code>`登记独立键，可复用同一静态字符串，不能运行时split/按异常文本翻译。参数（字段/节点/原ID/阶段）由单独详情区域实例资源标签呈现，不把SQL/路径/原始敏感值拼进错误。阶段使用以下逐枚举固定资源，不要求实现者翻译；Outcome Completed/Partial/Cancelled/Failed/Unknown/NotRecoverable/Rejected分别采用“完成/部分完成/已取消/失败/结果待确认/无法恢复/已拒绝”“完成/部分完成/已取消/失敗/結果待確認/無法復原/已拒絕”“Completed/Partially completed/Cancelled/Failed/Result unconfirmed/Cannot recover/Rejected”。资源释放阶段与Outcome分开，Unknown绝不绿色PASS。语言包完整性在SetLanguage前检查上述键及Template所用Literal/字段名/统计MeaningKey/ReasonKey；缺键保留上一完整chrome语言并显示缺词诊断，不能让请求报告的冻结语言被替换。

| reporting.phase枚举键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| PreAdmission / Accepted / Queued | 检查请求 / 已接纳 / 排队 | 檢查請求 / 已接納 / 排隊 | Checking request / Accepted / Queued |
| Binding / Rendering / Encoding | 绑定数据 / 生成报告 / 编码文件 | 綁定資料 / 產生報告 / 編碼檔案 | Binding data / Rendering report / Encoding files |
| Publishing / Reconciling | 发布文件 / 查询原结果 | 發布檔案 / 查詢原結果 | Publishing files / Checking original result |
| Draining / DrainUnknown / ResourcesReleased | 释放资源 / 资源未释放 / 资源已释放 | 釋放資源 / 資源未釋放 / 資源已釋放 | Releasing resources / Resources still held / Resources released |

## 10. 场景驱动复审：输入、顺序、结果和验收

报告元数据/统计投影与图像附件的持久化严格分离。`ReportInputClosure` 固定数据库投影快照、模板和文件对象引用清单；附件字节从 IM-066 受控文件存储取流，不通过 Npgsql/BLOB 列或一次性整图内存对象传递。每个附件均核授权、ObjectId、hash、尺寸/格式与保持租约；任一必需附件无法取回时，报告是 Partial/Failed，并列出缺失身份，不能用缩略空白占位冒充完整。大图只生成受预算约束的报告预览/缩略图，不得覆盖或替换原始证据。

本节是实现前的反例清单。每个场景都必须能在无 UI Core 中重放，并在两个不同消费者中证明同一闭包语义。`Input` 只能来自 `ReportInputClosure`、模板 manifest、语言快照、授权回执和宿主 `ReportBudget`；Core 不从场景名称推断工艺、质量或目标关联。`Output` 包括产物字节和结构检查结果，也包括未生成产物的明确状态。

### 10.1 正常、空集、部分成功和歧义输入

| 场景 | 输入与参数来源 | 处理顺序 | 输出、状态和错误 | 恢复动作与可判定验收 |
|---|---|---|---|---|
| 正常固定单件报告 | `SingleInspection`；042/调用方固定数据快照、证据引用；035/模板 Owner 提供模板 hash；003 提供语言快照；宿主提供格式/预算 | 校验请求→授权→模板闭包→字段/单位→完整性→绑定→分页→编码→结构检查→041/Store 发布 | 每种格式有独立 `Published` 产物、字节 hash、页/记录数、输入闭包 hash | 重新读取产物只能得到同一闭包；结构检查能定位实体、尝试、原值、显示值、单位、有效性和证据来源，且不产生质量放行结论 |
| 正常批次质量报告 | 045 提供已计算的总体、分母、首检/复测和资格；042 提供兼容固定查询关系；模板声明统计部分 | 先核统计与查询关系，再绑定图表/表格；不在模板表达式计算统计 | `Published` 或多格式 `Partial`；统计范围与明细范围分别显示 | 以同一快照核对分子、分母、Unknown、排除原因和范围；不能通过平均分页百分比得到另一数值 |
| 合法空集 | 固定快照完整证明 `ExpectedCount=0`，模板允许“无记录”部分；不是读取失败 | 校验完整性证明→绑定零行→渲染范围/时间/无记录说明→输出 | `Published`，记录数 0；不得生成 0%/100% 良率或把空集当未读取 | 结构检查同时看到范围和“无记录”；若缺完整性证明则改为 `RPT-SNAPSHOT-INCOMPLETE`，不能发布空报告 |
| 必需字段缺失或值为 Missing | 模板 manifest 标记必需字段；投影缺字段或 `ReportValueValidity.Missing` | 在绑定前区分“字段不存在”和“字段存在但值合法为空”；停止受影响产物 | `RPT-TEMPLATE-INCOMPATIBLE` 或 `RPT-OUTPUT-INCOMPLETE`；不填默认值 | 修订投影/模板后创建新意图；验收断言是错误指出字段名和来源修订，旧产物不变 |
| 多格式部分成功 | 同一闭包请求 PDF + DataXlsx；PDF 适配器完成，XLSX 编码或发布失败 | 各产物独立状态和回执；整组聚合最后计算 | PDF `Published`，XLSX `Failed`/`Unknown`，整组 `Partial` | 重启先查 XLSX 产物；确认未发布且同一闭包可恢复才重建，禁止删除 PDF 或宣称整组完成 |
| 字段/单位/范围歧义 | 相同字段名但 `UnitId`、scale、统计关系或 scope revision 不一致；来源 Owner 无明确迁移证明 | 在模板绑定前做精确版本/单位/关系比较；不做名称相似匹配或自动换算 | `RPT-TEMPLATE-INCOMPATIBLE`、`RPT-SOURCE-CHANGED` 或 `RPT-SNAPSHOT-NOT-FIXED` | 回到 Contract/Schema Owner 形成新修订；验收是拒绝原因可机器读取，不能以当前水位或显示单位继续 |

### 10.2 歧义、恶意和错误输入

| 场景 | 输入与参数来源 | 处理顺序 | 输出、状态和错误 | 恢复动作与验收 |
|---|---|---|---|---|
| 非法请求/文件名/枚举 | 用户或宿主提供空 ID、重复格式、控制字符、路径分隔符、未知枚举或超长字段 | 先做 UTF-8 字节长度、字符和枚举校验，再接触模板/Store | `Rejected` + `RPT-REQ-INVALID`；无文件、无查询、无副作用 | 修正并生成新请求；测试断言是拒绝前没有读取私表、创建输出目录或改变原意图 |
| 不可信模板 | 模板带脚本、反射、任意 ObjectDataSource、外链、未知子模板或资源越界 | 校验 manifest/hash/用途→受限TemplateDefinition解析/校验；REPX/脚本/任意类型入口直接拒绝 | `Rejected` + `RPT-TEMPLATE-UNTRUSTED` | 由模板 Owner 审查并发布新修订；验收证明模板不能访问 DB、网络、设备或进程 API |
| 权限拒绝或授权不可达 | `IAuthorizationGate` 返回 Denied/Unknown，或撤权与下载/Range 并发 | 接纳、发布前、每次交付关键边界均过同一栅栏；授权 Unknown 不沿缓存放行 | `RPT-AUTH-DENIED` 或 `RPT-AUTH-UNKNOWN`；已发布历史不删除 | 恢复授权后按原 ArtifactId 查询；新交付不能只因列表可见而成功 |
| 输入源改变/快照过期 | 投影 hash、快照代次、统计关系或证据保持与接纳时不同 | 绑定前和恢复时再次比较闭包；禁止静默重查实时数据 | `RPT-SOURCE-CHANGED` 或 `RPT-SOURCE-UNAVAILABLE` | 选择兼容快照并创建新意图；验收是旧意图仍可解释且不含新行 |
| 恶意文本和公式 | 字段值包含 `=1+1`、超长 Unicode、换行、HTML/路径样式内容 | 先按字段类型编码；CSV/XLSX 使用适配器的公式防护和长度上限 | 产物保留文本语义，不执行公式；超限 `RPT-BUDGET-EXCEEDED` | 结构化读取断言单元格类型和原值映射；不得全转字符串破坏数值/时间类型 |

### 10.3 超大、高并发、长期运行和资源上限

| 场景 | 输入与参数来源 | 处理顺序 | 输出、状态和错误 | 恢复动作与验收 |
|---|---|---|---|---|
| 超大明细/图片报告 | 行、列、图像和预计页数来自投影预估；预算来自宿主 Profile | 先预约输入/图片/页缓存/暂存/输出额度；小结果、固定暂存或明确拒绝 | 超限前拒绝 `RPT-BUDGET-EXCEEDED`，不自动分卷；不得隐式一次性物化 | 宿主显式缩小固定范围并创建关联新intent；分别测输入/文档内存，不改原范围或统计 |
| 高并发同模板多语言 | 多个不同 `IntentId`、语言和格式，共享不可变模板字节 | 每任务独占可变报告对象、事件、输出流；共享缓存只读；按并发额度排队 | 各任务独立状态和闭包 hash；队列超时 `RPT-TIMEOUT`，不串改语言/数据 | 并发压测检查交叉污染、队列深度和取消隔离；任一任务不得改变另一个任务的模板/文化 |
| 长时间运行/宿主重启 | 大报告跨分钟或重启；只允许 Store/适配器声明的检查点 | 记录阶段和产物清单→重启查原操作/每个产物→证明同一输入保持→按格式恢复 | 已发布项保持 `Published`；回执未知保持 `Unknown`；输入缺失的未完成项 `NotRecoverable` | 验收是重启后不新建实时查询、不覆盖已发布文件、整组清晰显示 `Partial`/未决项 |
| 磁盘/内存/句柄逼近上限 | 资源计数来自运行时计量器和宿主预算 | 在每个阶段检查并停止新工作；执行排空后释放租约；不按通配符删除用户目录 | `RPT-BUDGET-EXCEEDED` 或 `RPT-INTERNAL`；半文件不可见 | 注入磁盘满、缓存不足、句柄耗尽，验证资源归还和原产物可读性；不得默认成功 |
| 取消/超时/native 排空 | 调用方取消令牌、阶段 deadline、适配器可能仍持有 native 报告/图片对象 | `CancelRequested`→停止新页/格式→等待实际退出→关闭流/报告→归还租约；超时不强杀未确认对象 | `Draining` 期间不可宣称完成；退出后 `Cancelled`，发布结果不明则 `Unknown` | 用屏障证明 native 对象和流真实退出后才释放；重复取消幂等，另一任务不受影响 |

### 10.4 图像噪声、遮挡、退化和算法边界

本模块没有视觉算法、训练路线或模型恢复路线。视觉边界按 [DEV-VIS-020](<../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md>)；HALCON路线不适用：报告只消费证据 Owner 已批准的 `EvidenceReference`、显示尺寸、内容 hash 和质量/有效性字段，不调用 `ImageLibDotNet.cv2`、`HImage`、HALCON 算子或 AsunImage 内部。不得因为图像噪声、遮挡、模糊、曝光退化、缺图或压缩失败而在 reporting 内重采样、增强、补图、重测或改变判定。

| 场景 | 输入与参数来源 | 处理顺序 | 输出、状态和错误 | 恢复动作与验收 |
|---|---|---|---|---|
| 证据图像有噪声/遮挡/模糊 | 证据 Owner 提供原图引用、批准缩略图、质量状态和原因；不提供可计算图像则只提供缺口 | 校验引用/保持/hash→按模板显示原图或缺口说明；不运行增强算法 | 原检测有效性/Unknown 原因原样投影；证据缺失为 `RPT-OUTPUT-INCOMPLETE`，不是新视觉结果 | 回到证据/视觉模块补取或创建新检测意图；验收是报告显示质量状态和缺口，原值/判定不变 |
| 图像资源超尺寸或解码失败 | 资源 manifest、显示尺寸和图片预算来自证据 Owner/宿主 | 预约资源→解码计数→失败即停止该附件，不影响已完成其它格式 | 单附件缺失可为 `Partial`；必需附件失败为 `RPT-SOURCE-UNAVAILABLE` | 重新取得同一 hash 的资源或按模板声明缺口；不得用空白图冒充成功 |

任何需要去噪、遮挡修复、OCR、分割、配准、模型推理或训练的请求都拒绝为 reporting 能力，并转交相应视觉模块；报告可记录候选/影子/人工结果的来源和状态，但不把它们提升为生产事实或放行决定。

### 10.5 版本修订、升级和回退

| 场景 | 输入与参数来源 | 处理顺序 | 输出、状态和错误 | 恢复动作与验收 |
|---|---|---|---|---|
| 模板小修订且兼容 | 新模板 revision、manifest diff、明确迁移函数和兼容矩阵 | 先验证字段/单位/资源/版式差异，再创建关联新意图 | 新产物记录新模板 hash；旧产物只读不变 | 双版本并行生成并结构比对；只能证明显示变化，不可改变原事实 |
| 破坏性字段/单位/统计关系变化 | 字段删除/改义、单位变化、统计快照关系变化，无迁移证明 | 拒绝旧输入直接套新模板；不自动换算或填默认 | `RPT-TEMPLATE-INCOMPATIBLE` 或 `RPT-SOURCE-CHANGED` | 由原 Contract/统计 Owner 发布新修订和新闭包；验收旧意图仍可回读 |
| 适配器/模块升级失败 | 新 Core/adapter/资源包、兼容矩阵和发布包 hash | 停止新接纳→查询在途回执→保留已发布项→恢复旧版本并行读取 | 新任务 `Rejected/Failed/Unknown`；既有产物不改 hash | 回退后重放同一闭包；证明旧格式可读、新版本不会接管旧意图 |
| 需要回滚模板或资源 | 旧 manifest 仍可取且权限/保持有效 | 回滚引用，不删除已发布产物；未完成任务按原版本输入恢复或终结 | 已发布保持 `Published`；缺旧资源的任务 `NotRecoverable` | 验收不允许用当前资源冒充历史版本；输出中记录实际解析版本 |

本节所有“通过”仅是未来实现阶段的可判定验收断言；本轮没有执行渲染、性能、真实 HALCON、HIL 或生产验证。

### 10.6 既有核心反例

| 案例 | 必须结果 |
|---|---|
| 固定 10 条，2 通过、6 不通过、2 Unknown | 使用上游统计投影的计数/分母；不得平均页面百分比或删除 Unknown |
| 预览使用快照 r7，随后出现 r8 新记录 | PDF/XLSX 仍绑定 r7；刷新才创建新意图，不改 r7 产物 |
| 原值 `0.32004 mm`，显示 `0.320 mm`，原判定不通过 | 各格式显示值和原值来源；不按显示值重新判定 |
| 文本 `00128`、`=1+1`、数值 `-1`、Unknown 原因、真实空串 | 保留类型/前导零；文本不执行公式；Unknown 不当零；空串不当未知 |
| 同时间戳多行跨页且源排序更新 | 无固定完整读取证明则拒绝正式报告；不靠去重掩盖漏项 |
| 模板删必需字段、子模板 hash 变化、资源越界 | `RPT-TEMPLATE-INCOMPATIBLE/UNTRUSTED`；旧模板产物仍按当前权限可读 |
| PDF 已发布，XLSX 中断后重启 | PDF 保留；XLSX 查原产物，Unknown 继续回查，只有确认未发布且输入可恢复才重建 |
| 第 3 页渲染时取消/关闭预览 | 停止新工作并排空；半文件不公布；视图关闭不误停其它任务 |
| 发布回执丢失 | 状态 `Unknown`；按原 ArtifactId 查回，禁止实时重查、换键覆盖 |
| 资源超过页/字节/磁盘预算 | 返回 `RPT-BUDGET-EXCEEDED`，显式新范围另意图；不无限物化/排队 |

## 11. 测试、Simulator 与可判定断言

### 11.1 同一冻结合成夹具

合成夹具只用于软件定义，不证明客户工艺或现场资格。ConsumerId=`report-host-a`，Intent=`fixture-001`，Purpose=`SingleInspection`，ContractVersion=`report-api-v0.2`；UTC AsOf=`2026-10-10T00:00:00Z`，Language=zh-CN，TimeZoneId=`UTC`，UnitProfileId=`u1`；source/template/localization/renderer/profile/CoreRevision均用对应规范字节实际SHA-256，不填示例假hash。Query/Snapshot/Scope为`q1/s1/scope1`，Source Owner=`fixture-owner`、Revision=`1`。part=`p1`，SortContract=`ordinal-key-v1`，行key=`r0001`/`r0002`；字段serial Text无单位、measurement Decimal(mm,scale3)、decision Enum(`fixture-decision`)无单位。行1：Text `00128`、Decimal 0.32004/Display`0.320`、Enum`Fail`；行2：Text `=1+1`、measurement Unknown Reason`fixture.missing`、Enum`Unknown`。Range.ExpectedCount=2、完整RowsSha256按§4计算；source Simulator精确匹配原闭包才能Open。Summary可选：Total=2、Fail=1、Unknown=1且声明Partition；另加FinalPass=4/ReviewPass=2无Partition验证合法重叠，不算率。Host-B换Consumer/Intent、Purpose=BatchQuality，仍消费同shape，禁止产品DTO侵入Core。

软件测试Profile（不是客户性能承诺）给预算：Rows100、Columns16、Pages20、Images4、Input16MiB、Decoded16MiB、Working64MiB、Temp128MiB、Output32MiB、PageBatchRows1、BufferedPages1、Text4096bytes；queue/render/publish/close观察各2s，活动2、排队2、observer2、events16；root槽2、RetainedBytes512MiB、独立cleanup观察2s、recheck100ms。测试使用TimeProvider固定UTC+可推进单调时钟；外层每用例10s真实watchdog。所有hash由规范fixture字段重建，各集合顺序及optional null按§4；语言resources提供所有模板/状态/错误键，Bool/Enum显示由对应资源键供给。

缺DisplayValue的唯一格式规则：Text/Identifier原字串，Integer Invariant十进制；Decimal Scale=null时G29，指定Scale时decimal.Round(ToEven)后F<Scale>，只替换DecimalSeparator（只准`.`或`,`，不分组）；Timestamp转换宿主已解析TimeZone后按LocalizationData.DateTimePattern（首版只准`yyyy-MM-dd HH:mm:ss zzz`）显示，原UTC保留；Duration Invariant `c`；Bool使用`reporting.value.true/false`资源；Enum使用`reporting.enum.<contractId>.<key>`；Evidence显示EvidenceId；nonValid用对应状态词+ReasonKey翻译，不造数值。格式变化只影响显示，不修改SourceValue或decision。缺词/未知TimeZone/不允许pattern拒绝格式绑定，不依赖系统culture。

### 11.1.1 独立完整 Rows 字节/hash 向量

Expected常量由字段独立拼接，不由受测codec自生。ExpectedCount=1，StableKey=`r0001`，Values恰一个`serial`：Type=Text、SourceValue=Text(`00128`)、DisplayValue=`00128`、Unit=null、Validity=Valid、ReasonKey=null。

| 字段 | 固定HEX |
|---|---|
| domain ASUN-ROWS2 | 4153554e2d524f575332 |
| Int64 ExpectedCount=1 | 0100000000000000 |
| StableKey | 050000007230303031 |
| UInt32 字典count=1 | 01000000 |
| key serial | 0600000073657269616c |
| Type Text=0 | 00000000 |
| SourceValue存在+Text tag=0 | 0100000000 |
| SourceValue.Text | 050000003030313238 |
| DisplayValue存在+string | 01050000003030313238 |
| Unit不存在 | 00 |
| Validity Valid=0 | 00000000 |
| ReasonKey不存在 | 00 |

完整75 bytes HEX=`4153554e2d524f5753320100000000000000050000007230303031010000000600000073657269616c00000000010000000005000000303031323801050000003030313238000000000000`；独立SHA-256=`7de5a670cf9b977282440008f6893c346d51e12696fa297613178a84ea96e51c`。TC04分别以BCL SHA256核固定HEX和以受测RowsHasher核独立输入；另检request只换IntentId的hash不变、换Consumer/预算/授权/语言/数组顺序hash改变。

### 11.1.2 独立完整 Template 字节/hash 向量

此向量覆盖一个完整公开TemplateDefinition，不用ComputeTemplateSha256生成Expected。输入：Id=`golden-layout1`；Source=`(fixture-owner,template-golden1,64个0)`；SchemaVersion=`report-layout-v2`；PurposeIds=`[SingleInspection]`；Formats=`[Pdf]`；纸宽210m、纸高297m、边距10m、FontResourceId=`fixture-font`、字号10m；Header恰`(title,Literal,reporting.title,null,true,180m,8m)`；Detail恰`(serial,Field,serial,p1,true,60m,8m)`；Footer/Resources为空且不是default数组。Source.Sha256按§4.1唯一自摘要规则省略，除此之外无省略字段。它是编码shape向量，字体文件/语言/part须由独立消费夹具提供，不能据此声称真实渲染可用。

下表按字段用严格UTF-8/BCL little-endian独立拼接；decimal均是G29字符串。所有HEX连续拼接即完整bytes，无换行/分隔字节：

| 字段 | 实际输入 | 固定HEX |
|---|---|---|
| domain | `ASUN-TPL2` | `4153554e2d54504c32` |
| Id | `golden-layout1` | `0e000000676f6c64656e2d6c61796f757431` |
| Source.OwnerId / Revision | `fixture-owner / template-golden1` | `0d000000666978747572652d6f776e65721000000074656d706c6174652d676f6c64656e31` |
| SchemaVersion | `report-layout-v2` | `100000007265706f72742d6c61796f75742d7632` |
| PurposeIds | `[SingleInspection]` | `010000001000000053696e676c65496e7370656374696f6e` |
| Formats | `[Pdf=0]` | `0100000000000000` |
| PageWidthMm / PageHeightMm / MarginMm | `210 / 297 / 10` | `0300000032313003000000323937020000003130` |
| FontResourceId / FontSizePt | `fixture-font / 10` | `0c000000666978747572652d666f6e74020000003130` |
| Header | `[(title,Literal=0,reporting.title,null,true,180,8)]` | `01000000050000007469746c65000000000f0000007265706f7274696e672e7469746c650001030000003138300100000038` |
| Detail | `[(serial,Field=1,serial,p1,true,60,8)]` | `010000000600000073657269616c010000000600000073657269616c01020000007031010200000036300100000038` |
| Footer / Resources | `[] / []` | `0000000000000000` |

完整263 bytes HEX=`4153554e2d54504c320e000000676f6c64656e2d6c61796f7574310d000000666978747572652d6f776e65721000000074656d706c6174652d676f6c64656e31100000007265706f72742d6c61796f75742d7632010000001000000053696e676c65496e7370656374696f6e010000000000000003000000323130030000003239370200000031300c000000666978747572652d666f6e7402000000313001000000050000007469746c65000000000f0000007265706f7274696e672e7469746c650001030000003138300100000038010000000600000073657269616c010000000600000073657269616c010200000070310102000000363001000000380000000000000000`；独立SHA-256=`0f21b5d2fd3c18f183df7714b5de7ff5f712e951552cc6ac2635ebbeb47bed6a`。TC04及§14.4先核固定bytes长度/BCL hash，再以以上实际输入调用受测codec并比较固定hash；额外核只改Source.Sha256不变、改页宽必变。请求与语言夹具仍须按自己的编码规则验证；此向量不把它们的自算值变成独立Golden，也不代表真实格式Golden。

### 11.2 Core/Owner Simulator 精确控制点

测试工程提供实现全部端口的Simulator：immutable source按页返回，模板/语言严格hash，文件对象内存/隔离临时文件按ObjectId保存，Store用同一锁模拟Claim+token+sequence/组Publish原子性，Renderer只生成明确标记的测试字节，Verifier按合成格式验证；模拟字节不能标为真实PDF/XLSX。每个Open/Read/Claim/Encode/Seal/Verify/Publish/Record/Close/Dispose及observer入口有可控闩锁，先登记原Task再释放屏障；不使用随机sleep判断完成。每个租约统计取得/释放，原Task引用相等断言；错误可配置return/throw/timeout/迟到成功，查询Unknown与NotFound分开。所有资源计量Unknown时Complete=false。

| 用例 | 具体触发与必须断言 |
|---|---|
| TC01 | 上述正常2行、PageBatchRows1；两页连续、两类型及原值/显示差异保留；最后hash/count匹配后才能Verified/Publish |
| TC02 | 0行完整固定集→第0页空+IsLast；Published清单保留scope/0行，“无记录”且无0%/100%；source unavailable不得伪空 |
| TC03 | type mismatch、unknown enum/tag、required field missing、UTF8非法surrogate、long溢出、预算=0非法项→PreAdmission/Rejected且无Claim/Factory文件副作用 |
| TC04 | 随机字段字典插入顺序hash不变；数组/显示/语言/授权/预算改变hash变；§4标量向量精确；重复key/坏SHA拒绝 |
| TC05 | 开第二页屏障，修改source/sort/hash/首次index或丢/重复行；完整性失败，不公开文件，不靠去重掩盖；原源租约释放 |
| TC06 | 同Consumer/Intent并发提交相同内容→一个Created、一个原Task/历史观察；改template/hash仍同键Conflict；模板已删除时原回执查询不加载当前模板 |
| TC07 | 两intent/三语并发→可变session/流/文化隔离；另intent取消不影响其它；queue满/活动满不无限增任务；Retained仍计容量 |
| TC08 | scripts/URL/REPX/custom enum/template未知字段/越界几何→Untrusted/Incompatible，无反序列化/网络/SQL；合法TemplateDefinition可绑定 |
| TC09 | PDF测试格式已发布，第二格式失败→Partial并保留PDF；第二Publish已提交后回执丢失→Unknown优先，原ArtifactId查询，不换ID、不覆盖 |
| TC10 | generate/publish/read栅栏Denied/Unknown、撤权并发Range→无新交付；不存在/无权限/未知互不伪装；历史Published不删除 |
| TC11 | FinalPass4、ReviewPass2无Partition→接受不加总；声明闭合Fail1+Unknown1=Total2→接受；改Total3/重复MemberKey/负数→拒绝该统计关系，原事实不写 |
| TC12 | bind/read/render/encode/verify/publish阶段各取消/到期，底层屏障不释放→无ResourcesReleased/Outcome；解除屏障真实归还后才原Task完成 |
| TC13 | Publish迟到成功/异常；原回执查Found Published，清理仍卡住→phase DrainUnknown/Outcome null；清理真实结束保留Published，未知提交不判Cancelled |
| TC14 | Factory前占满root槽→Factory调用数0；Create成功Validate抛异常→AttachCore已保存，cleanup不丢；原factory/lease/Dispose晚到→同槽强持，独立cleanup期限不继承已取消business token |
| TC15 | 两Host方法/窗口观察离栈、原Task不结束→Retained及保守字节；根Stop返回DrainUnknown而不删槽；late产物查询同intent/ID；release依赖失败不覆盖原BusinessError |
| TC16 | 同进程移交接受/拒绝/回执丢失及CAS竞态→只有一个清理者，原Task相同；未确认不释放发送容量；跨进程liveSlot移交拒绝，重启只查持久Owner，不假移交 |

| 真实适配用例 | 断言 |
|---|---|
| TF01 | PDF结构/每part行数/完整元数据、字体、超长行跨页/页数/证据hash读回一致，无原值舍入改判 |
| TF02 | LayoutXlsx文本00128/=1+1不执行公式，文件结构与Metadata一致；无法保类型须reject或显式呈现限制，不能声称数据型XLSX |
| TF03 | Docx/Html无外部关系/脚本/网络，中文/繁中/英文和HTML危险文本编码，ZIP/DOM结构与清单对齐；Docx Artifact.PageCount=null/Verification.PageCount=0，只核RendererPageCount来自本次XtraReport，app.xml Pages不同不误判Word实际分页已验证 |
| TF04 | PNG PageRange逐页=1..N独立ID，hash/尺寸/DPI与页集合齐，少一页整format不得Published |
| TF05 | DX encode/图片/PRNX页面缓存真实取消/异常/长稳；所有stream/ImageSource/report/PrintingSystem实际归还；不按Task.Cancelled猜native结束 |
| TF06 | CSV串00128、=1+1、前置TAB/+/-/@、quote/newline按§7编码，raw_base64精确还原；数值-1仍number；空集Metadata保范围 |
| TF07 | DataXlsx高精度decimal/Int64/UTC/Duration/Enum/Unknown，scalar类型及raw_invariant读回精确；公式无设置；超Excel行列/文本上限直接拒绝不截断 |
| TF08 | 每format必需Metadata及文件对象组发布屏障、断电/回执丢失；半组不可读；已Published另一format不删除 |

| 真实WPF用例 | 断言 |
|---|---|
| TU01–02 | 固定1920 viewport/DPI实际客户区，三语及最长资源不遮取消/Unknown/页导航，Tab/UIA/焦点清楚 |
| TU03–04 | 双control/intent隔离、快速选择epoch过滤、迟到预览不盖新选择；Grid/Inspector/preview按同ArtifactId联动 |
| TU05–06 | §9.3.1实例Grid/Bar/Dock/三语消息服务真实接线；已知搜索无结果、未知SDK通知/对话安全拒绝；语言切换不改报告快照/另一view；Ctrl+P/E/F、IME/输入焦点/Enter/Esc不误执行；快捷键/右键/UIA不能绕Core导出/打印/邮件 |
| TU07–08 | §9.2.1完整PRNX恢复、同步异常/DocumentException、DocumentLoaded页数核对、加载/关闭迟到；关闭后Document=null、原调用/回调结束、确切自有文件可独占并删除，native/句柄/页面缓存资源实测归还后才Released；Dispatcher卡住保留原control/model/路径，不dispose内部SDK对象；导出Unknown在原ID恢复，撤权不由灰按钮冒充线性化 |

新增测试消费方为切片准入及上述两个Host接入；缺这些断言会放过原身份重复发布、漏数据/误PASS和提前释放。测试入口任何错误、未结束或必须断言跳过返回非零，不以用例数量当功能进度。

## 12. 性能预算和可观测性

本节冻结测量协议与测点，不设未经真实消费者采纳的性能达标值。每个不可变 BenchmarkProfile 必须记录唯一 ID/修订/hash、构建提交与 .NET/适配器/后端版本、OS 与 CPU/内存/存储/网络配置、带 hash 的输入集及规模分布、调用混合与并发/到达模型、队列与资源预算、时钟测点边界、故障注入点，以及 ColdSampleCount、WarmupIterationCount、MeasuredSampleCount 和各指标的验收目标/阈值来源。Profile 变更必须产生新修订，不得跨 Profile 合并数据。

冷测每个样本均从新进程/新模块实例开始，并清空模块自有缓存；OS 文件缓存、数据库缓存、外部服务和设备状态无法由模块清空时，必须记录其实际状态，使用隔离可重建夹具，不标称为冷。热测先按 Profile 固定次数执行预热，再按固定样本数测量；不使用自适应停止、只报最快值或丢弃慢样本。外部副作用操作使用可重建隔离夹具和唯一操作 ID。每个样本用单调时钟记录原始耗时；P50/P95/P99 的算法按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md) 计算，并同时报告样本数、单位和原始值。吞吐量使用 Profile 固定的观察窗口计算已完成且有效的操作数/时间，并单列拒绝、错误、重试和未完成项。

每轮同时记录 CPU、工作集/私有字节、托管分配与 GC、native/适配器缓冲、磁盘/网络 I/O、连接/句柄峰值，队列当前/峰值条数与字节、排队等待、积压变化、接受/拒绝/丢弃计数。排空时间从关闭新接纳开始，至在途操作、回调、IO/适配器资源全部实际归还结束；期限到达只记超时和未完成项，不得强杀后宣称排空。每项验收阈值必须引用消费者要求、正式 Contract/资源风险依据或已批准资格记录的稳定 ID；没有来源时写 TargetPending，只能报告测量结果，不得判定达标。协议/资源硬上限与性能目标分开，只有唯一权威中的必要性、数值和来源均已明确时才可作为硬上限，不从基准数据臆造上限。

### 本模块固定测点
将数据快照加载与报告生成分开；分别记录接纳/排队、首个预览页、全量布局与渲染、编码、暂存、发布、Range 读取和取消至排空。Profile 固定行/列/分组/图片/页面规模分布、数据快照模式与版本、模板/资源/语言 hash、渲染器和格式适配器版本、并发数、冷/热缓存以及缓存/暂存/输出介质。记录各阶段 P50/P95/P99、首字节/首屏、有效吞吐、CPU、托管/native 峰值、临时磁盘水位、队列与回压、输出字节、Partial/Unknown/失败数和资源归还。没有消费者批准的规模、目标和阈值来源时写 TargetPending，不得将模板默认预算称为 SLA。

### 12.1 可执行负载组与长稳断言

每Profile必须为下列组指定样本数/预热/冷测、finite deadline及具体阈值来源；没有性能目标仍执行诊断并NotEvaluated。下列规模是**诊断输入维度**，不是客户SLA：fixture生成时先核预算；不允许benchmark本身默认放大Ceiling。

| Profile组 | 负载/测点 | 资源及可判定失败 |
|---|---|---|
| BP-C1 | 0/2/100/100000行的规范hash流；1/16/256字段、最大允许字符串、模板节点1/64/4096 | hash正确性、分配峰值/throughput，whole-row ToList不存在；非法边界必须Reject；hash不能跨schema比较 |
| BP-C2 | PageBatchRows1/128/4096，buffer1/2；1/2/MaxActive并发；无图/4张/接近解码预算；三语混合 | 接纳/首批/完整读取/encoding/ResourcesReleased，队列条数+字节/源批次/native/temp/输出峰值不漏计；预算超限/Unknown另列 |
| BP-C3 | 单/2/全部启用formats；发布延迟/抛异常/断线/回执Unknown；真实Store重启仅资格组 | Claim/组发布/原ID回查/最终记录时延和Unknown驻留；不同ID重复发布、半组可见、查Unknown返回空均失败 |
| BP-H | 两Host滚动运行+root capacity边界；每N轮注入一次Open/Dispose迟到、observer阻塞、依赖release失败 | root retained槽/字节、Task与lease数、真实取消→排空；可结束负载后活动/队列/lease归基线，仍不明者保留容量且整组不得PASS |
| BP-A1/A2 | 明细/长文本/分组显示/图/页面规模+各format版本；实际文件结构hash与输入关联 | 输入物化与文档缓存分别计量；原值/必需节点遗漏、公式注入、乱码/缺页直接失败；内存目标由消费者机器Profile冻结 |
| BP-U1 | 原ID选择/多页PRNX/双控件/切语言/折叠Inspector/关闭/阻塞Dispatcher | 首屏/切页/输入响应、Dispatcher队列/texture/native/stream及detach真实排空；固定1920viewport，未测不叫流畅达标 |

长稳Profile冻结总运行时长、重启/故障周期、采样窗口及允许稳态增长阈值来源；不同Profile不合并趋势。每窗口记录active/queued/root Retained/cached bytes/句柄/Task数，正常已排空窗口必须回到该Profile预热后的已声明缓存基线；缓存有固定条/字节容量，不随任务历史无界增长。任何未知resource计量或未排空样本不能用“看起来稳定”判通过；统计与资源终态规则仍只引用GOV-010，不复制分位算法。

## 13. 版本、适配、发布和回退

版本至少分离：模块契约版本、模板 Schema/修订、数据/统计投影版本、渲染器版本、格式适配器版本、资源包版本和输出 Schema。产物记录全部实际解析版本/hash；版本未知或不在兼容矩阵内拒绝执行。只读兼容可在明确迁移函数和差异证明后使用；字段删除、改义、单位变化、统计关系变化和模板必需资源变化必须生成新报告意图，不静默迁移。

发布包包含 Core、适配器、兼容矩阵、模板/资源 manifest、许可证/来源记录、配置默认值、迁移/回退步骤和测试证据。灰度先接入离线/Replay，再接入两个消费者；旧版本继续读取旧产物。回退采用版本化并存和旧适配器恢复，不能删除已发布产物、改写其 hash 或把新实时数据接入旧意图。升级失败时停止新接纳，查询原回执，保留已发布项和未决/Unknown 项，按 Store 规则回收临时资源。

## 14. 两个无 UI Host 与有界进程根 Owner

### 14.1 真实复用计划与独立装配

Host-A=`SingleInspectionReportHost`，用于生产单件报告服务/离线证据工具：提供实体/尝试/原值/显示/单位/人工意见的不可变投影、证据文件引用及PDF；Host-B=`BatchQualityReportHost`，用于独立质量/客户输出工具：提供固定批次明细、上游已算统计/分母/资格及DataXlsx/CSV/PDF。两个Host是不同应用装配，不是同页别名；仅共用Reporting Core/公开端口，不能复用另一个产品的ViewModel或私表。无UI模拟宿主可验证调用与状态，正式第二消费者接入和真实文件读回仍须其Owner接收。

Host依赖对象由调用者显式提供，不在Factory内服务定位。Host构造`ReportingProcessOwner(ReportingOwnerOptions, TimeProvider, IDiagnosticsSink)`，该**非静态、进程长寿命实例**由应用根容器持有，必须先于ReportingFactory。两Host在同进程使用同一根Owner但不同ConsumerId；不同进程各有自己的根Owner，持久claim/token由Store串行约束。根Owner装配也是模块交付能力，源码在Core的Hosting命名空间；不依赖产品Shell。

```csharp
public sealed record ReportingOwnerOptions(int MaxSlots, long MaxRetainedBytes,
    TimeSpan ObservationTimeout, TimeSpan CleanupObservationTimeout,
    TimeSpan RecheckInterval);
public sealed record OwnerSlotId(string Value);
public enum OwnerSlotState { Reserved, Running, Cleaning, Retained, TransferPending,
    Released, Transferred }
public sealed record OwnerSlotSnapshot(OwnerSlotId Id, OperationIdentity Identity,
    OwnerSlotState State, bool OriginalTaskCompleted, bool CleanupCompleted,
    long RetainedBytes, RenderError? BusinessError, RenderError? CleanupError);
public sealed record OwnedReportingExecution(IReportingCore Core,
    Task<RenderResult> OriginalTask, Func<Task> ReleaseHostDependencies);
public sealed record OwnerObservation(OwnerSlotSnapshot Slot, RenderResult? Result,
    bool DeadlineExpired);
public sealed record OwnerTransferOffer(string TransferId, OwnerSlotId SlotId,
    OperationIdentity Identity, SourceRevision OwnerRevision);
public sealed record OwnerTransferReceipt(string TransferId, OwnerSlotId SlotId,
    OperationIdentity Identity, bool Accepted, string ReceiverOwnerId);
public interface IReportingOwnerSlot
{
    OwnerSlotId Id { get; }
    Task<OwnerObservation> StartAndObserveAsync(
        Func<IReportingOwnerScope, Task<OwnedReportingExecution>> createAndStart,
        CancellationToken observationCancellationToken);
    OwnerSlotSnapshot Snapshot { get; }
}
public interface IReportingOwnerScope
{
    void AttachCore(IReportingCore core); // Create返回后、Validate/Render之前
    void TrackOriginalTask(Task<RenderResult> task); // 保存同一个原Task，且只允许一次
}
public interface IReportingProcessOwner
{
    bool TryReserve(OperationIdentity identity, long retainedBytesUpperBound,
        Func<Task> releaseHostDependencies,
        out IReportingOwnerSlot? slot);
    ImmutableArray<OwnerSlotSnapshot> Query();
    Task<DrainResult> StopAndObserveAsync(TimeSpan timeout,
        CancellationToken observationCancellationToken);
    ValueTask<OwnerTransferReceipt> AcceptTransferAsync(OwnerTransferOffer offer,
        IReportingOwnerSlot liveSlot, CancellationToken cancellationToken);
}
```

唯一公开构造/方法形状：`ReportingProcessOwner(ReportingOwnerOptions options, TimeProvider time, IDiagnosticsSink diagnostics)`实现上述接口；`SingleInspectionReportHost(IReportingProcessOwner owner, ReportingDependencies dependencies, ReportingOptions options, Func<Task> releaseHostDependencies)`和BatchQualityReportHost同形；二者`Task<OwnerObservation> RunAsync(RenderRequest request, CancellationToken businessCancellationToken, CancellationToken observationCancellationToken)`，不自动Dispose外借dependencies。`releaseHostDependencies`只用于宿主此次独占的依赖作用域，借用端口传已完成空Task；不得释放另一Host共用的Store/Auth实例。OwnerOptions MaxSlots=1..1024、MaxRetainedBytes>0，3个时间>0且<=24h；无默认值，来源是宿主Profile。两Host的RetainedBytesUpperBound冻结为checked(Ceiling.MaxWorkingBytes + Ceiling.MaxTempBytes + Ceiling.MaxOutputBytes)；依赖暂存、模板/语言、借用上下文、回调和worker缓冲必须包含在MaxWorkingBytes中，不能另用未定义的private预算。输入流缓冲也计Working，磁盘暂存/输出分别计Temp/Output；因此这个和为保守上界，不是峰值实测。超出根预算不启动；Retained项算在槽数/字节内，不会为新任务腾空。

### 14.2 槽位先于 Factory 的最小顺序

以下为**接线语义步骤**，不是已编译应用代码；精确构造签名已在§3.3/本节给出。

1. Host纯校验ConsumerId/用途/预算和request形状，显式持其dependencies作用域；在根Owner `TryReserve(identity, byteUpperBound, releaseHostDependencies,out slot)`成功前不调用Factory、不启Task、不借流。失败返回宿主容量错误并无文件/Claim。
2. `StartAndObserveAsync`先在槽中登记createAndStart委托、原factory任务代理和需要强持的依赖作用域，再且只调用委托一次。委托内Create同步，立即scope.AttachCore(core)，再调用Validate；无效生成PreAdmission/Rejected结果；有效调用RenderAsync并立即scope.TrackOriginalTask保存**同一个原Task**。AttachCore/Track由槽同锁执行，无等待点；委托抛异常时根Owner仍能cleanup已登记core，不能只依赖OwnedReportingExecution成功返回。若Factory或同步Render调用抛异常，槽仍记录原错误并处理已经产生的core/任务，不用方法离栈释放dependencies。
3. root在委托开始前创建并保存原Task代理，委托成功迟到返回OwnedReportingExecution时立即强持Core/OriginalTask/ReleaseHostDependencies。观察token仅取消等待；business token传Core执行。deadline/观察取消返回OwnerObservation(DeadlineExpired=true)，槽Retained，不释放core/端口，也不重启原意图。Factory本身同步阻塞时用根Owner的有界worker隔离，其worker原Task强持；不在UI Dispatcher/无限Task.Run调用，不把worker观察到期等作Factory结束。
4. Core执行正常、错误、取消或发布Unknown返回后，root以**独立未取消的cleanup token**调用CloseAsync(CleanupObservationTimeout)，保存原Close Task；紧接保存同一个DisposeAsync.AsTask并观察。到期返回Retained，不并发dispose、不删除槽。Delegate/create/core/cleanup任何原Task的迟到结果都由同槽续接；迟到产物只Query原intent/artifact并保留原回执，不能当新请求。
5. Core/所有借用对象/observer真实排空后，再且只调用ReleaseHostDependencies并强持原release Task；失败附CleanupError，不覆盖BusinessError/Unknown回执。释放尚未确认时Retained，成功才Released、归还槽数和字节。失败已完成任务按其Owner幂等协议重试，禁止对尚运行的Dispose/Release发第二次调用。
6. `StopAndObserveAsync`停止根Owner新槽、通知全部core取消并以有限期限观察；未退出返回DrainUnknown及原身份。应用根容器继续强持根Owner并以有限RecheckInterval检查原Task/cleanup，不自动重跑业务。超过期限可明确告警/人工停机，不能返回成功或把未确认资源从计数抹除。

### 14.3 确认移交而非遗弃

常规关闭不需要移交，原根Owner一直保留。只有同进程更高寿命接收者显式接收同一个liveSlot、原Task、core、deps、lease、cleanup及原identity，先预约容量并`AcceptTransferAsync`持入账本，再返回Accepted=true且TransferId/SlotId/identity/ReceiverOwnerId完全匹配，发送方才可标Transferred、释放自己的重复容量计数；实际资源没有dispose或变更Owner协议。拒绝保持原Owner；发送前槽置TransferPending，暂停自己的新cleanup启动（已运行cleanup Task也一起移交，不重启）。双方以同进程共享liveSlot的原子cleanup-owner epoch CAS决定唯一清理者；接收CAS并强持成功后清理权归接收者，发送者即使回执丢失/未知/超时仍强持并计容量但不重启清理，只查询liveSlot确认TransferId/接收Owner。身份不符拒收；只有确认CAS未发生才恢复原清理权。接收不得再次Start，原Task不复制；应用根Owner持整个liveSlot直到资源实际释放。

此liveSlot协议**不适用于跨进程或电脑重启**；Task/SDK对象不能序列化。进程重启只能从Store原identity恢复公开回执，旧进程排空、持久fencing、文件对象恢复资格由StoreOwner证明。未证明的未完执行保持Unknown，不能拿进程退出当确认移交。无根Owner容量或明确接收者时不启动Factory；不能把静态字典、无人观察Task、窗口finally或GC当资源Owner。

### 14.4 完整最小合成 Program 与双 Host 夹具

以下是未来Core.Tests/Program.cs的完整基线夹具规格。待按本文实现Core/Factory/Codec/RowsHasher/Owner/两个Host后，可按§15原工程命令装配；本轮只写指导，未创建/编译该C#文件。全部私有夹具在此给出，不要求读者猜closure/options/private helper。Renderer产生明确SIM字节，Verifier只核合成协议，**不生成或声称真实PDF/PRNX/XLSX/CSV**。完整TC故障Simulator另按§11.2叠加，不把最小例当全套测试。

A：2行单件/Pdf含模拟PRNX；B：3行批次/DataXlsx+Csv及上游已算统计。wrapper/typed fields/范围/模板/语言/options/root均由以下代码构造；上游Revision是独立BCL来源标记摘要，行/模板/语言/请求通过已声明公开codec入口计算。root先于Host.Run/Factory。测试 runner 必须另有10s进程watchdog：未退出为失败，不把终止当排空。

```csharp
using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.Reporting;
using Asun.Modules.Reporting.Hosting;

internal static class Program
{
    private static async Task<int> Main()
    {
        const string hex = "4153554e2d524f5753320100000000000000050000007230303031" +
            "010000000600000073657269616c000000000100000000050000003030313238" +
            "01050000003030313238000000000000";
        const string expected = "7de5a670cf9b977282440008f6893c346d51e12696fa297613178a84ea96e51c";
        var root = new ReportingProcessOwner(new ReportingOwnerOptions(2, 512L << 20,
            TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(2), TimeSpan.FromMilliseconds(100)),
            TimeProvider.System, new NullDiagnostics());
        try
        {
            Check(Convert.FromHexString(hex).Length == 75 &&
                Hash(Convert.FromHexString(hex)) == expected, "independent-vector");
            var vector = new ReportRow("r0001", ImmutableDictionary<string, ReportValue>.Empty
                .Add("serial", new(ReportFieldType.Text, new ReportScalar.Text("00128"),
                    "00128", null, ReportValueValidity.Valid, null)));
            var h = new ReportRowsHasher(1); h.Append(vector);
            Check(h.Finish() == expected, "rows-codec-vector");
            const string templateHex = "4153554e2d54504c320e000000676f6c64656e2d6c61796f757431" +
                "0d000000666978747572652d6f776e65721000000074656d706c6174652d676f6c64656e31" +
                "100000007265706f72742d6c61796f75742d7632010000001000000053696e676c65496e7370656374696f6e" +
                "01000000000000000300000032313003000000323937020000003130" +
                "0c000000666978747572652d666f6e74020000003130" +
                "01000000050000007469746c65000000000f0000007265706f7274696e672e7469746c650001030000003138300100000038" +
                "010000000600000073657269616c010000000600000073657269616c01020000007031010200000036300100000038" +
                "0000000000000000";
            const string templateExpected = "0f21b5d2fd3c18f183df7714b5de7ff5f712e951552cc6ac2635ebbeb47bed6a";
            Check(Convert.FromHexString(templateHex).Length == 263 &&
                Hash(Convert.FromHexString(templateHex)) == templateExpected, "independent-template-vector");
            var templateVector = new TemplateDefinition(new TemplateRevisionId("golden-layout1"),
                new SourceRevision("fixture-owner", "template-golden1", new string('0', 64)),
                "report-layout-v2", ImmutableArray.Create("SingleInspection"),
                ImmutableArray.Create(ReportFormat.Pdf), 210m, 297m, 10m, "fixture-font", 10m,
                ImmutableArray.Create(new LayoutNode("title", LayoutNodeKind.Literal,
                    "reporting.title", null, true, 180m, 8m)),
                ImmutableArray.Create(new LayoutNode("serial", LayoutNodeKind.Field,
                    "serial", "p1", true, 60m, 8m)),
                ImmutableArray<LayoutNode>.Empty, ImmutableArray<EvidenceReference>.Empty);
            Check(ReportCanonicalCodec.ComputeTemplateSha256(templateVector) == templateExpected,
                "template-codec-vector");
            Check(ReportCanonicalCodec.ComputeTemplateSha256(templateVector with {
                Source = templateVector.Source with { Sha256 = new string('f', 64) } }) == templateExpected,
                "exclude-template-self-hash");
            Check(ReportCanonicalCodec.ComputeTemplateSha256(templateVector with {
                PageWidthMm = 211m }) != templateExpected, "include-template-page-width");
            var a = new Fixture(false); var b = new Fixture(true);
            var hostA = new SingleInspectionReportHost(root, a.Dependencies, a.Options,
                a.ReleaseDependenciesAsync);
            var hostB = new BatchQualityReportHost(root, b.Dependencies, b.Options,
                b.ReleaseDependenciesAsync);
            var first = await hostA.RunAsync(a.Request, CancellationToken.None, CancellationToken.None);
            var second = await hostB.RunAsync(b.Request, CancellationToken.None, CancellationToken.None);
            Check(ReportCanonicalCodec.ComputeRequestSha256(a.Request with {
                IntentId = new ReportIntentId("different-intent") }) == a.Request.RequestContentSha256,
                "exclude-intent");
            Check(ReportCanonicalCodec.ComputeRequestSha256(a.Request with {
                Input = a.Request.Input with { ConsumerId = "different-consumer" } }) !=
                a.Request.RequestContentSha256, "include-consumer");
            Check(ReportCanonicalCodec.ComputeRequestSha256(a.Request with {
                Budget = a.Request.Budget with { MaxRows = 99 } }) !=
                a.Request.RequestContentSha256, "include-budget");
            Check(first.Result?.Outcome == OperationOutcome.Completed && !first.DeadlineExpired,
                "host-a-result");
            Check(second.Result?.Outcome == OperationOutcome.Completed && !second.DeadlineExpired,
                "host-b-result");
            Check(first.Result!.Identity.ConsumerId != second.Result!.Identity.ConsumerId,
                "two-consumers");
            Check(first.Result.Artifacts.Any(x => x.Role == ArtifactRole.PreviewDocument),
                "pdf-preview-member");
            Check(second.Result.Artifacts.Select(x => x.Format).Distinct().Count() == 2,
                "batch-two-formats");
            var stopped = await root.StopAndObserveAsync(TimeSpan.FromSeconds(2), CancellationToken.None);
            Check(stopped.State == ResourceState.Released && stopped.RetainedIntents.IsEmpty,
                "root-released");
            Check(root.Query().All(x => x.State == OwnerSlotState.Released), "slots-released");
            foreach (var f in new[] { a, b })
            {
                Check(f.LiveLeases == 0 && f.DependenciesReleased, "leases-and-dependencies");
                foreach (var name in new[] { "auth", "source", "template", "language", "read-page",
                    "claim", "stage", "seal", "files", "renderer", "verify", "publish", "record" })
                    Check(f.Seen.Contains(name), "port-" + name);
                var id = new OperationIdentity(f.Request.Input.ConsumerId, f.Request.IntentId);
                var counters = f.Dependencies.Resources.Read(id);
                Check(counters.OpenLeaseCount == 0 && counters.MeasuredWorkingBytes is null &&
                    !counters.Complete, "resource-meter-unknown-not-zero");
                Check(f.Dependencies.Diagnostics.TryWrite(new("fixture-check", id, "drain", null, 0)),
                    "diagnostics-port");
                var original = await f.QueryAsync(id, CancellationToken.None);
                Check(original.LookupState == ReportLookupState.Found &&
                    original.Result?.Outcome == OperationOutcome.Completed, "original-query");
                foreach (var artifact in original.Result!.Artifacts) {
                    var found = await f.GetAsync(artifact.ArtifactId, CancellationToken.None);
                    Check(found.LookupState == ReportLookupState.Found &&
                        found.Result?.State == ArtifactState.Published, "original-artifact"); }
            }
            return 0;
        }
        catch (Exception e)
        {
            Console.Error.WriteLine(e.Message);
            var stopped = await root.StopAndObserveAsync(TimeSpan.FromSeconds(2), CancellationToken.None);
            Console.Error.WriteLine("cleanup=" + stopped.State);
            if (stopped.State != ResourceState.Released)
                await Task.Delay(Timeout.InfiniteTimeSpan); // root强持；外层watchdog判未结束/非零
            return 1;
        }
    }
    private static void Check(bool value, string id)
    { if (!value) throw new InvalidOperationException(id); }
    private static string Hash(byte[] bytes) =>
        Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    private static SourceRevision Revision(string id) =>
        new("fixture-owner", id, Hash(Encoding.UTF8.GetBytes("fixture-source:" + id)));
    private sealed class NullDiagnostics : IDiagnosticsSink
    { public bool TryWrite(ReportDiagnostic value) => true; }

    private sealed class Fixture : IReportProjectionSource, ITemplateCatalog,
        ILocalizationSnapshot, IAuthorizationGate, IReportFileObjects, IArtifactStore,
        IRenderAdapter, IArtifactVerifier, IDiagnosticsSink, IReportingResourceMeter
    {
        public readonly HashSet<string> Seen = new(StringComparer.Ordinal);
        public int LiveLeases;
        public bool DependenciesReleased;
        public RenderRequest Request { get; }
        public ReportingOptions Options { get; }
        public ReportingDependencies Dependencies { get; }
        private readonly ImmutableArray<ReportRow> rows;
        private readonly TemplateDefinition template;
        private readonly LocalizationData language;
        private readonly object gate = new();
        private readonly Dictionary<OperationIdentity, RenderResult> operations = new();
        private readonly Dictionary<OperationIdentity, string> tokens = new();
        private readonly Dictionary<OperationIdentity, long> sequences = new();
        private readonly Dictionary<ArtifactKey, ArtifactId> keys = new();
        private readonly Dictionary<ArtifactId, ArtifactResult> artifacts = new();
        private readonly Dictionary<FileObjectId, byte[]> objects = new();
        private readonly Dictionary<FileObjectId, Verification> simulatedVerification = new();
        private int next;
        public ImmutableArray<FormatCapability> Capabilities { get; }
        public Fixture(bool batch)
        {
            var revision = Revision("source-v1"); var renderer = Revision("sim-renderer-v1");
            var evidence = ImmutableArray<EvidenceReference>.Empty;
            var fields = ImmutableArray.Create(
                new ReportField("serial", ReportFieldType.Text, null, null, true, revision),
                new ReportField("measurement", ReportFieldType.Decimal, new UnitId("mm"), 3,
                    false, revision),
                new ReportField("decision", ReportFieldType.Enum, null, null, true, revision));
            rows = batch ? ImmutableArray.Create(
                Row("r0001", "B-0001", .40004m, "0.400", "Pass"),
                Row("r0002", "B-0002", .50004m, "0.500", "Pass"),
                Row("r0003", "B-0003", null, null, "Unknown"))
                : ImmutableArray.Create(Row("r0001", "00128", .32004m, "0.320", "Fail"),
                    Row("r0002", "=1+1", null, null, "Unknown"));
            var h = new ReportRowsHasher(rows.Length); foreach (var row in rows) h.Append(row);
            var snapshot = new SnapshotId(batch ? "batch-s1" : "single-s1");
            var scope = batch ? "batch-scope1" : "single-scope1";
            var query = Revision(batch ? "batch-q1" : "single-q1");
            var part = new ReportPartInput("p1", revision, fields,
                new RangeProof("fixture-owner", "range-proof1", Revision("range-proof1").Sha256,
                    snapshot, scope, query, "ordinal-key-v1", rows.Length, h.Finish(), true), evidence);
            var texts = ImmutableDictionary<string,string>.Empty
                .Add("reporting.title", batch ? "批次报告" : "单件报告")
                .Add("fixture.total", "总数").Add("fixture.pass", "通过")
                .Add("fixture.fail", "不通过").Add("fixture.unknown", "未知")
                .Add("fixture.missing", "未提供测量值")
                .Add("reporting.value.true", "是").Add("reporting.value.false", "否")
                .Add("reporting.enum.fixture-decision.Pass", "通过")
                .Add("reporting.enum.fixture-decision.Fail", "不通过")
                .Add("reporting.enum.fixture-decision.Unknown", "未知");
            language = new LocalizationData(Revision("language-v1") with { Sha256 = new string('0', 64) },
                "zh-CN", texts, ".", "yyyy-MM-dd HH:mm:ss zzz", "未知", "缺失", "不适用", "无效", "无记录");
            language = language with { Source = language.Source with {
                Sha256 = ReportCanonicalCodec.ComputeLocalizationSha256(language) } };
            template = new TemplateDefinition(new TemplateRevisionId("fixture-layout1"),
                Revision("template-v1") with { Sha256 = new string('0', 64) }, "report-layout-v2",
                ImmutableArray.Create("SingleInspection", "BatchQuality"),
                ImmutableArray.Create(ReportFormat.Pdf, ReportFormat.DataXlsx, ReportFormat.Csv),
                210m, 297m, 10m, "fixture-font", 10m,
                ImmutableArray.Create(new LayoutNode("title", LayoutNodeKind.Literal,
                    "reporting.title", null, true, 180m, 8m)),
                ImmutableArray.Create(
                    new LayoutNode("serial", LayoutNodeKind.Field, "serial", "p1", true, 60m, 8m),
                    new LayoutNode("measurement", LayoutNodeKind.Field, "measurement", "p1", false, 60m, 8m),
                    new LayoutNode("decision", LayoutNodeKind.Field, "decision", "p1", true, 60m, 8m)),
                ImmutableArray<LayoutNode>.Empty, evidence);
            template = template with { Source = template.Source with {
                Sha256 = ReportCanonicalCodec.ComputeTemplateSha256(template) } };
            var metrics = ImmutableArray.Create(Count("Total", rows.Length, "fixture.total"),
                Count(batch ? "Pass" : "Fail", batch ? 2 : 1, batch ? "fixture.pass" : "fixture.fail"),
                Count("Unknown", 1, "fixture.unknown"));
            var summary = new ReportSummaryProjection("summary1", scope, snapshot,
                Revision("statistics-v1"), "denominator-v1", "relation1", true, metrics,
                ImmutableArray.Create(new CountPartition(
                    ImmutableArray.Create(batch ? "Pass" : "Fail", "Unknown"), "Total", "relation1")));
            var input = new ReportInputClosure(batch ? "BatchQuality" : "SingleInspection",
                batch ? "report-host-b" : "report-host-a", snapshot, DataViewMode.FixedSnapshot,
                query, scope, "scope-policy1", ImmutableArray.Create(part), ImmutableArray.Create(summary),
                ImmutableArray<ReportErrorProjection>.Empty, template.Id, template.Source.Sha256,
                "zh-CN", language.Source, "UTC", "unit-profile1", renderer,
                new DateTimeOffset(2026, 10, 10, 0, 0, 0, TimeSpan.Zero));
            var budget = new ReportBudget(100, 16, 20, 0, 16L << 20, 16L << 20, 64L << 20,
                128L << 20, 32L << 20, 1, 1, 4096, TimeSpan.FromSeconds(2),
                TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(2));
            Options = new ReportingOptions("fixture-profile1", Revision("profile-v1"),
                Revision("core-v0.2"), budget, 2, 2, 2, 16, TimeSpan.FromSeconds(2));
            Request = new RenderRequest("report-api-v0.2", new ReportIntentId(batch ? "batch-001" : "single-001"),
                input, batch ? ImmutableArray.Create(ReportFormat.DataXlsx, ReportFormat.Csv)
                    : ImmutableArray.Create(ReportFormat.Pdf), RenderMode.Publish, budget,
                batch ? "batch-report" : "single-report", "fixture-user", scope, "");
            Request = Request with { RequestContentSha256 = ReportCanonicalCodec.ComputeRequestSha256(Request) };
            Capabilities = ImmutableArray.Create(ReportFormat.Pdf, ReportFormat.DataXlsx, ReportFormat.Csv)
                .Select(f => new FormatCapability(f, renderer, f == ReportFormat.Pdf, true, false,
                    false, Enum.GetValues<LayoutNodeKind>().ToImmutableArray())).ToImmutableArray();
            Dependencies = new ReportingDependencies(this, this, this, this, this,
                this, this, this, this, this, TimeProvider.System);
        }
        private static ReportRow Row(string key, string serial, decimal? measurement,
            string? display, string decision) => new(key, ImmutableDictionary<string,ReportValue>.Empty
            .Add("serial", new(ReportFieldType.Text, new ReportScalar.Text(serial), serial,
                null, ReportValueValidity.Valid, null))
            .Add("measurement", new(ReportFieldType.Decimal,
                measurement.HasValue ? new ReportScalar.Decimal(measurement.Value) : null,
                display, new UnitId("mm"), measurement.HasValue ? ReportValueValidity.Valid
                    : ReportValueValidity.Unknown, measurement.HasValue ? null : "fixture.missing"))
            .Add("decision", new(ReportFieldType.Enum,
                new ReportScalar.EnumValue("fixture-decision", decision), null,
                null, ReportValueValidity.Valid, null)));
        private static SummaryMetric Count(string key, long count, string meaning) =>
            new(key, new(ReportFieldType.Integer, new ReportScalar.Integer(count),
                null, null, ReportValueValidity.Valid, null), meaning);
        private void Mark(string name) { lock (gate) Seen.Add(name); }
        private static PortResult<T> Ok<T>(T value) => new(PortStatus.Ok, value, null);
        private static ValueTask<PortResult<T>> Ready<T>(T value) => ValueTask.FromResult(Ok(value));
        public ResourceCounters Read(OperationIdentity identity)
        { lock (gate) return new(64L << 20, null, 0,
            Volatile.Read(ref LiveLeases), false); }
        public bool TryWrite(ReportDiagnostic value) { Mark("diagnostics"); return true; }
        public Task ReleaseDependenciesAsync()
        { Check(LiveLeases == 0, "release-live-dependencies"); DependenciesReleased = true;
            return Task.CompletedTask; }
        public ValueTask<PortResult<AuthorizationReceipt>> CheckAsync(AuthorizationRequest request,
            CancellationToken token)
        { token.ThrowIfCancellationRequested(); Mark("auth");
            Check(request.ConsumerId == Request.Input.ConsumerId, "auth-consumer");
            Check(request.ScopeId == Request.AuthorizationScopeId, "auth-scope");
            return Ready(new AuthorizationReceipt("fixture-decision1", Revision("auth-v1"),
                DateTimeOffset.UtcNow.AddHours(1))); }
        public ValueTask<PortResult<IProjectionLease>> OpenAsync(ReportInputClosure input,
            CancellationToken token)
        { token.ThrowIfCancellationRequested(); Mark("source");
            Check(ReportCanonicalCodec.ComputeRequestSha256(Request with { Input = input }) ==
                Request.RequestContentSha256, "source-manifest");
            return Ready<IProjectionLease>(new Projection(this, input)); }
        public ValueTask<PortResult<ITemplateLease>> OpenAsync(TemplateRevisionId id,
            string hash, CancellationToken token)
        { token.ThrowIfCancellationRequested(); Mark("template");
            Check(id == template.Id && hash == template.Source.Sha256, "template-revision");
            return Ready<ITemplateLease>(new TemplateLease(this)); }
        public ValueTask<PortResult<ILocalizationLease>> OpenAsync(string tag,
            SourceRevision revision, CancellationToken token)
        { token.ThrowIfCancellationRequested(); Mark("language");
            Check(tag == language.LanguageTag && revision == language.Source, "language-revision");
            return Ready<ILocalizationLease>(new LanguageLease(this)); }
        public ValueTask<PortResult<IFileReadLease>> OpenReadAsync(FileObjectId id, string hash,
            AuthorizationReceipt auth, CancellationToken token)
        { token.ThrowIfCancellationRequested(); Mark("files"); lock (gate) {
            Check(objects.TryGetValue(id, out var bytes) && Hash(bytes!) == hash, "file-identity");
            return Ready<IFileReadLease>(new ReadLease(this, id, bytes!)); } }
        public ValueTask<ReportOperationLookupResult> QueryAsync(OperationIdentity id,
            CancellationToken token)
        { token.ThrowIfCancellationRequested(); Mark("query"); lock (gate)
            return ValueTask.FromResult(operations.TryGetValue(id, out var result)
                ? new ReportOperationLookupResult(id, ReportLookupState.Found, result, null)
                : new ReportOperationLookupResult(id, ReportLookupState.NotFound, null, null)); }
        public ValueTask<ClaimReceipt> ClaimAsync(ClaimRequest claim, CancellationToken token)
        { token.ThrowIfCancellationRequested(); Mark("claim"); lock (gate) {
            if (operations.TryGetValue(claim.Identity, out var prior))
                return ValueTask.FromResult(prior.RequestSha256 == claim.RequestSha256
                    ? new ClaimReceipt(ClaimDisposition.Existing, null, prior, null)
                    : new ClaimReceipt(ClaimDisposition.Conflict, null, null,
                        new RenderError("RPT-CONFLICT", "claim", "reporting.error.RPT-CONFLICT", null, false)));
            tokens.Add(claim.Identity, "fixture-token1"); sequences.Add(claim.Identity, -1);
            operations.Add(claim.Identity, new(claim.Identity, OperationPhase.Accepted, null,
                ResourceState.Retained, ImmutableArray<ArtifactResult>.Empty, claim.RequestSha256,
                DateTimeOffset.UtcNow, null, null));
            return ValueTask.FromResult(new ClaimReceipt(ClaimDisposition.Created,
                "fixture-token1", null, null)); } }
        public ValueTask<PortResult<IArtifactWriteLease>> StageAsync(ArtifactKey key,
            string executionToken, long maxBytes, CancellationToken token)
        { token.ThrowIfCancellationRequested(); Mark("stage"); lock (gate) {
            Check(tokens[key.Identity] == executionToken, "stage-token");
            Check(!keys.ContainsKey(key), "baseline-no-duplicate-stage");
            var id = new ArtifactId("sim-artifact-" + (++next));
            var obj = new FileObjectId("sim-object-" + next);
            keys.Add(key, id);
            artifacts.Add(id, new(id, key.Identity, key.Format, key.Role, key.PageIndex,
                ArtifactState.Staged, obj, ByteLength: null, ContentSha256: null,
                PageCount: null, RendererPageCount: null, RecordCount: null,
                PublishReceiptId: null, Error: null));
            return Ready<IArtifactWriteLease>(new WriteLease(this, id, obj, maxBytes)); } }
        public ValueTask<PortResult<ImmutableArray<ArtifactResult>>> PublishAsync(PublishRequest request,
            CancellationToken token)
        { token.ThrowIfCancellationRequested(); Mark("publish"); lock (gate) {
            Check(tokens[request.Identity] == request.ExecutionToken, "publish-token");
            Check(request.Members.Any(x => x.Role == ArtifactRole.Document) &&
                request.Members.Count(x => x.Role == ArtifactRole.Metadata) == 1 &&
                (request.Format != ReportFormat.Pdf ||
                    request.Members.Count(x => x.Role == ArtifactRole.PreviewDocument) == 1),
                "complete-format-group");
            foreach (var member in request.Members) {
                var a = artifacts[member.ArtifactId];
                Check(a.Identity == request.Identity && a.Format == request.Format &&
                    a.ContentSha256 == member.Verification.Sha256, "publish-member"); }
            var result = request.Members.Select(m => {
                var a = artifacts[m.ArtifactId] with { State = ArtifactState.Published,
                    PageCount = m.Verification.PageCount > 0 ? m.Verification.PageCount : null,
                    RendererPageCount = m.Verification.RendererPageCount,
                    RecordCount = m.Verification.RecordCount, PublishReceiptId = "fixture-publish1" };
                artifacts[a.ArtifactId] = a; return a;
            }).ToImmutableArray();
            return Ready(result); } }
        public ValueTask<PortResult<RenderResult>> RecordAsync(OperationIdentity id,
            string executionToken, long sequence, RenderResult result, CancellationToken token)
        { token.ThrowIfCancellationRequested(); Mark("record"); lock (gate) {
            Check(tokens[id] == executionToken && result.Identity == id, "record-identity");
            Check(sequence > sequences[id], "record-sequence"); sequences[id] = sequence;
            operations[id] = result;
            foreach (var a in result.Artifacts) artifacts[a.ArtifactId] = a;
            return Ready(result); } }
        public ValueTask<ArtifactLookupResult> GetAsync(ArtifactId id, CancellationToken token)
        { token.ThrowIfCancellationRequested(); Mark("get"); lock (gate)
            return ValueTask.FromResult(artifacts.TryGetValue(id, out var a)
                ? new ArtifactLookupResult(id, ReportLookupState.Found, a, null)
                : new ArtifactLookupResult(id, ReportLookupState.NotFound, null, null)); }
        public ValueTask<PortResult<IRenderSession>> CreateAsync(RenderContext context,
            CancellationToken token)
        { token.ThrowIfCancellationRequested(); Mark("renderer");
            return Ready<IRenderSession>(new Session(this, context)); }
        public async Task<PortResult<Verification>> VerifyAsync(SealedArtifact artifact,
            ArtifactKey key, RenderContext context, CancellationToken token)
        {
            Mark("verify");
            var opened = await context.Files.OpenReadAsync(artifact.ObjectId, artifact.Sha256,
                context.Authorization, token);
            Check(opened.Status == PortStatus.Ok, "verify-open");
            await using var lease = opened.Value!;
            using var copy = new MemoryStream();
            await lease.Content.CopyToAsync(copy, token);
            var bytes = copy.ToArray();
            Check(bytes.Length == artifact.ByteLength && Hash(bytes) == artifact.Sha256,
                "verify-independent-file-hash");
            if (key.Role == ArtifactRole.Metadata)
                Check(bytes.AsSpan().StartsWith("ASUN-META2"u8) &&
                    bytes.AsSpan().EndsWith("END-META2"u8), "sim-metadata-envelope");
            else Check(bytes.AsSpan().StartsWith("SIM-REPORT/"u8), "sim-document-envelope");
            lock (gate) return Ok(simulatedVerification[artifact.ObjectId]);
        }
        private abstract class Lease : IAsyncDisposable
        {
            protected readonly Fixture F;
            private int released;
            protected Lease(Fixture f) { F = f; Interlocked.Increment(ref f.LiveLeases); }
            public virtual ValueTask DisposeAsync()
            { if (Interlocked.Exchange(ref released, 1) == 0)
                Interlocked.Decrement(ref F.LiveLeases); return ValueTask.CompletedTask; }
        }
        private sealed class Projection : Lease, IProjectionLease
        {
            public Projection(Fixture f, ReportInputClosure input) : base(f) { Manifest = input; }
            public string LeaseId => "fixture-projection1";
            public ReportInputClosure Manifest { get; }
            public ValueTask<PortResult<ReportPage>> ReadPageAsync(string part, long page,
                int maxRows, CancellationToken token)
            { token.ThrowIfCancellationRequested(); F.Mark("read-page");
                Check(part == "p1" && page >= 0 && page < F.rows.Length && maxRows >= 1,
                    "page-domain");
                var row = F.rows[checked((int)page)]; var h = new ReportRowsHasher(1); h.Append(row);
                return Ready(new ReportPage(part, page, page, ImmutableArray.Create(row),
                    page == F.rows.Length - 1, h.Finish())); }
        }
        private sealed class TemplateLease(Fixture f) : Lease(f), ITemplateLease
        { public string LeaseId => "fixture-template1"; public TemplateDefinition Definition => F.template; }
        private sealed class LanguageLease(Fixture f) : Lease(f), ILocalizationLease
        { public string LeaseId => "fixture-language1"; public LocalizationData Data => F.language; }
        private sealed class ReadLease : Lease, IFileReadLease
        {
            public ReadLease(Fixture f, FileObjectId id, byte[] bytes) : base(f)
            { ObjectId = id; Sha256 = Hash(bytes); Length = bytes.Length;
                Content = new MemoryStream(bytes, writable: false); }
            public FileObjectId ObjectId { get; }
            public string Sha256 { get; }
            public long Length { get; }
            public Stream Content { get; }
            public override async ValueTask DisposeAsync()
            { Content.Dispose(); await base.DisposeAsync(); }
        }
        private sealed class WriteLease : Lease, IArtifactWriteLease
        {
            private readonly LimitStream stream;
            private SealedArtifact? sealedValue;
            public WriteLease(Fixture f, ArtifactId id, FileObjectId obj, long max) : base(f)
            { ArtifactId = id; ObjectId = obj; stream = new LimitStream(max); }
            public ArtifactId ArtifactId { get; }
            public FileObjectId ObjectId { get; }
            public Stream Content => stream;
            public ValueTask<PortResult<SealedArtifact>> SealAsync(CancellationToken token)
            { token.ThrowIfCancellationRequested(); F.Mark("seal"); lock (F.gate) {
                if (sealedValue is not null) return Ready(sealedValue);
                var bytes = stream.ToArray(); stream.Sealed = true;
                sealedValue = new(ArtifactId, ObjectId, bytes.LongLength, Hash(bytes));
                F.objects[ObjectId] = bytes;
                F.artifacts[ArtifactId] = F.artifacts[ArtifactId] with {
                    ByteLength = bytes.LongLength, ContentSha256 = sealedValue.Sha256 };
                return Ready(sealedValue); } }
            public override async ValueTask DisposeAsync()
            { stream.Dispose(); await base.DisposeAsync(); }
        }
        private sealed class LimitStream(long limit) : MemoryStream
        {
            public bool Sealed;
            private void Guard(long count)
            { Check(!Sealed && checked(Position + count) <= limit, "output-budget-or-sealed"); }
            public override void Write(byte[] bytes, int offset, int count)
            { Guard(count); base.Write(bytes, offset, count); }
            public override void Write(ReadOnlySpan<byte> bytes)
            { Guard(bytes.Length); base.Write(bytes); }
            public override void WriteByte(byte value) { Guard(1); base.WriteByte(value); }
            public override Task WriteAsync(byte[] bytes, int offset, int count, CancellationToken token)
            { token.ThrowIfCancellationRequested(); Write(bytes, offset, count); return Task.CompletedTask; }
            public override ValueTask WriteAsync(ReadOnlyMemory<byte> bytes, CancellationToken token = default)
            { token.ThrowIfCancellationRequested(); Write(bytes.Span); return ValueTask.CompletedTask; }
            public override void SetLength(long value)
            { Check(!Sealed && value >= 0 && value <= limit, "output-length"); base.SetLength(value); }
        }
        private sealed class Session(Fixture f, RenderContext context) : Lease(f), IRenderSession
        {
            public async Task<PortResult<ImmutableArray<RenderedArtifact>>> EncodeAsync(
                ReportFormat format, IRenderOutput output, CancellationToken token)
            {
                var all = ImmutableArray.CreateBuilder<RenderedArtifact>();
                var publications = ImmutableArray.CreateBuilder<ArtifactPublication>();
                long count = 0;
                for (long page = 0; ; ++page) {
                    var read = await context.Rows.ReadAsync("p1", page, token);
                    Check(read.Status == PortStatus.Ok, "encode-read");
                    count += read.Value!.Rows.Length;
                    if (read.Value.IsLast) break;
                }
                foreach (var role in format == ReportFormat.Pdf
                    ? new[] { ArtifactRole.Document, ArtifactRole.PreviewDocument, ArtifactRole.Metadata }
                    : new[] { ArtifactRole.Document, ArtifactRole.Metadata })
                {
                    var opened = await output.OpenAsync(format, role, 0, token);
                    Check(opened.Status == PortStatus.Ok, "encode-stage");
                    await using var destination = opened.Value!;
                    if (role == ArtifactRole.Metadata) {
                        var header = new ReportMetadataHeader("report-metadata-v2",
                            new OperationIdentity(context.Request.Input.ConsumerId, context.Request.IntentId),
                            context.Request.RequestContentSha256, context.Request.Input,
                            context.Request.Budget, F.Options.CoreRevision, format,
                            context.Request.Mode, publications.ToImmutable());
                        await ReportCanonicalCodec.WriteMetadataAsync(header, context.Rows,
                            destination.Content, token);
                    }
                    else {
                        var bytes = Encoding.UTF8.GetBytes("SIM-REPORT/" + format + "/" + role + "/" +
                            context.Request.Input.ConsumerId + "/" + context.Request.RequestContentSha256);
                        await destination.Content.WriteAsync(bytes, token);
                    }
                    var sealedResult = await destination.SealAsync(token);
                    Check(sealedResult.Status == PortStatus.Ok, "encode-seal");
                    var seal = sealedResult.Value!;
                    var verification = new Verification(seal.ByteLength, seal.Sha256,
                        format == ReportFormat.Pdf && role != ArtifactRole.Metadata ? 1 : 0,
                        format == ReportFormat.Pdf && role != ArtifactRole.Metadata ? 1 : null,
                        count, context.Request.Input.Parts[0].Range.RowsSha256,
                        context.Request.Input.Renderer);
                    lock (F.gate) F.simulatedVerification[seal.ObjectId] = verification;
                    all.Add(new(format, role, 0, verification));
                    if (role != ArtifactRole.Metadata)
                        publications.Add(new(seal.ArtifactId, role, 0, verification));
                }
                return Ok(all.ToImmutable());
            }
        }
    }
}
```

夹具私有Store为最小顺序路径；完整TC06需按§3.4实现同ArtifactKey重试/并发与token fence，不把基线例的快速拒绝用于幂等资格。模拟Verifier只证明文件hash/合成Envelope和Core端口编排，正式TF必须独立解析完整元数据及真实格式。此最小Fixture仅有确切lease数/native=0，未注册完整托管buffer计量，故MeasuredWorkingBytes=null/Complete=false、UsesBoundedInput=false；只能在这个预先有限的小输入物化预算内验证编排，不能扩大预算或宣称流式/性能PASS。完整TC资源Simulator另注册全部缓冲。fixture-font是模拟器映射，不能证明实际字体/分页/PRNX/WPF。Header/Footer沿§3.2报告级一次语义，不由格式工程师重新选。

## 15. 逐切片六门、落点与精确剩余门

### 15.1 工程与实现范围

本轮仅修改本文，不创建以下工程。后续获准实现时：

| 工程 | 目标/依赖/唯一namespace | 测试及验收消费方 |
|---|---|---|
| src/Modules/reporting/Asun.Modules.Reporting.Core/Asun.Modules.Reporting.Core.csproj | net10.0、Microsoft.NET.Sdk、BCL-only；Asun.Modules.Reporting，Asun.Modules.Reporting.Hosting仅根Owner/双Host | tests/Modules/reporting/Asun.Modules.Reporting.Core.Tests/Asun.Modules.Reporting.Core.Tests.csproj |
| src/Modules/reporting/Asun.Modules.Reporting.DevExpress/Asun.Modules.Reporting.DevExpress.csproj | net10.0-windows；Core及本机DX25.2.3直引；Asun.Modules.Reporting.DevExpress | tests/Modules/reporting/Asun.Modules.Reporting.DevExpress.Tests/Asun.Modules.Reporting.DevExpress.Tests.csproj |
| src/Modules/reporting/Asun.Modules.Reporting.Wpf/Asun.Modules.Reporting.Wpf.csproj | net10.0-windows、UseWPF=true；Core+显式DX Adapter；Asun.Modules.Reporting.Wpf | tests/Modules/reporting/Asun.Modules.Reporting.Wpf.TestHost/Asun.Modules.Reporting.Wpf.TestHost.csproj，STA Exe/UseWPF |

Core.Tests为net10.0/OutputType=Exe/BCL确定性断言，不引入待选测试框架；Simulator、两个Host及fault barriers放在此唯一测试工程而不是产品模拟数据库。实现命令：`dotnet build src/Modules/reporting/Asun.Modules.Reporting.Core/Asun.Modules.Reporting.Core.csproj -c Release`，`dotnet run --project tests/Modules/reporting/Asun.Modules.Reporting.Core.Tests/Asun.Modules.Reporting.Core.Tests.csproj -c Release`。Adapter.Tests为net10.0-windows Exe，实际文件读回断言；Wpf.TestHost显式启动STA/Dispatcher及有限独立watchdog，所有路径归还失败返回非零。不是用`dotnet test`无报错代替Exe执行。各工程未存在，命令是未来实施命令，不声称本轮执行。

允许路径仅对应获准切片工程与其唯一测试；公共契约只在Core；DX类型只在DevExpress/Wpf；禁止src其它模块/现有产品、shared DTO/Schema、私表、原参考项目、AsunImage、设备SDK、全局状态和共享文件。产品接线由正式Contract Owner和主控串行接收，不由本模块自行改。签章/打印/邮件/自动打开外部程序不是v0.2公开能力，禁止内置控件绕过边界。

### 15.2 六项规格接收与切片状态（2026-10-12）

主控已回读§3–7/9/11–15核心内容并接收0.3.2-prep窄修：完整Template的263字节字段独立重建与HEX/SHA一致；受控PRNX恢复、实际加载屏障、关闭/资源未知保留、实例三语与原生命令安全边界公开接线闭合。R-C1/R-C2/R-C3的DEV-GOV-010 §3.1六项规格已接收，标记ModuleCoreImplementationReady，仅涵盖Core、受控Simulator、有界进程根Owner和两个无UI Host的规格准备。R-A1/R-A2/R-U1指导内容已接收，无新增内部接线设计欠账；真实格式/字体/PRNX/WPF/资源、权限/文件持久资格及产品接入未关闭，仍PreparationIncomplete / NotReady，不标无UI CoreReady。整体保持DesignReview/Prep；本次只同步规格接收状态，不创建工程或启动代码开发，不宣称实现、测试或生产验收完成。

| 切片 | 1边界/消费者 | 2API/资源 | 3无UI宿主 | 4可判定测试 | 5Benchmark | 6落点/调用 | 当前状态 | 精确限制 |
|---|---|---|---|---|---|---|---|---|
| R-C1 | §1/2/14 | §3/4，codec/template/value验证 | §14两Host纯校验 | §10/11 TC01–04/11 | §12 BP-C1 | §15.1/7.3 | `ModuleCoreImplementationReady`（六项规格已接收） | 仅规格准备；不验证上游事实真实性 |
| R-C2 | §2单件/批次 | §3全部端口、§4顺序/§6Owner | §14根Owner+Simulator | TC05–10/12–14 | BP-C2/BP-H | §15.1/14 | `ModuleCoreImplementationReady`（六项规格已接收） | 受控Simulator仅用于软件验证，真实授权/文件/后端映射另门 |
| R-C3 | §2发布/恢复 | §3.4Store+§5/14 | 两Host多格式/Unknown | TC06/09/10/13–16 | BP-C3/BP-H | §15.1/14 | `ModuleCoreImplementationReady`（六项规格已接收） | 仅Core/Simulator规格准备；持久原子格式组/fencing/保持/撤权交付由StoreOwner资格确认 |
| R-A1 | §7全部版式输出 | §3render/verifier+§7.2 | 无UI真实DX Host | TF01–05/TC12–14 | BP-A1 | DevExpress工程 | 指导内容已接收；`PreparationIncomplete / NotReady` | ImageSource/PNG公开签名已绑定；列宽/纸张实际输出、资源/字体Golden未做；UI的PRNX恢复唯一见§9.2.1 |
| R-A2 | §7CSV/DataXlsx | §3roles/group+§7.1 | Host-B | TF06–08 | BP-A2 | 同Adapter工程 | 指导内容已接收；`PreparationIncomplete / NotReady` | 数据XLSX Spreadsheet writer/读回公开入口已绑定；精度/类型/CSV codec/Metadata形状已定，真实打开/类型核验未做 |
| R-U1 | §9所有任务/状态 | presenter/delivery/lease/epoch | Core无UI；UI单独TestHost | TU01–08 | BP-U1 | Wpf/Wpf.TestHost | 指导内容已接收；`PreparationIncomplete / NotReady` | §9.2.1 OpenDocument/关闭及§9.3.1实例服务/三语接线已冻结；真实编译、1920/DPI/键盘/UIA三语/呈现/关闭资源资格未做 |


### 15.3 后续门的责任与影响

| 门 | 原Owner/证据 | 只阻断 |
|---|---|---|
| 平台DTO及C-02/04/05/07映射 | 各事实/统计/语言/权限/输出Owner批准映射；不改模块v0.2 | 正式平台集成；不阻C1–C3 Simulator |
| Store/file/auth真实协议 | 原ID查回、组原子可见性、fencing、保持/撤权线性化、进程重启真实故障证据 | R-C3真实适配/生产交付及view读取；Core状态可先验证 |
| DevExpress真实运行资格 | 指导内容及内部公开接线已接收（§7/9/16）；消费编译、实际格式/字体/PRNX呈现与对象/流/资源归还仍待验证 | R-A1/R-A2/R-U1资格；不是内部设计欠账或依赖安装/授权/版本审查 |
| 格式结构/Golden/字体与三语 | 各format真实文件、代表数据/证据/长文本/未知值及语义读回；客户词条Owner审校 | 对应格式/用途与WPF资格 |
| 客户规模/时延/资源Profile | 消费者给固定输入/hash/规模、机器环境与阈值来源；无阈值结果NotEvaluated | 性能/生产验收；不编造SLA |
| 产品页面/最终操作授权 | 产品PageContract和调用方权限；签章/打印另任务 | 产品UI与外部副作用；不加入Core设备命令 |

本轮自审/结构校验仅证明文本一致性；主控已完成上述逐切片规格接收并据此同步状态。未执行代码构建、真实DevExpress/文件Store/格式Golden/性能/WPF或生产验收，规格接收不关闭这些资格门。

### 15.4 全批准范围文档准备结论（2026-10-12）

本轮沿当前架构 IM-044 的全部批准范围复审：模板声明与信任边界、输入/统计/证据投影、规范编码与独立完整性、幂等/权限/Store fencing、七类格式、图片硬盘引用、分页/字体/三语、DevExpress 25.2.3 受控对象树、PRNX 预览与关闭、两个无 UI Host/进程根Owner、WPF 工作台、CSV/DataXlsx原值、故障/取消/超时/恢复、双消费者、Golden/反例、BenchmarkProfile及发布回退均有唯一章节、公开端口、单位/有效域、Owner、顺序、错误和资源归还规则。没有发现需要后续开发者自行决定的内部算法、格式路线、控件接线、Root/lease或权限边界。

可决定的软件设计已经闭合：

- R-C1/C2/C3 的 `ModuleCoreImplementationReady` 只覆盖纯Core、受控Simulator、根Owner和两个无UI Host，继续受 DEV-GOV-010 §3.1 的六项条件约束。
- R-A1 已冻结 XtraReport 对象树、PDF/版式XLSX/DOCX/HTML/PNG 选项、页/列/跨页/证据图规则、字体cmap覆盖、独立Verifier及拒绝条件；R-A2 已冻结 CSV/RFC4180、防公式、类型化 DataXlsx、metadata sheet和读回核验；R-U1 已冻结 WPF 工厂、权限投影、实例三语、键盘/UIA安全边界、OpenDocument/关闭/迟到和双STA Host。三者仍为 `PreparationIncomplete / NotReady`，因为真实程序集消费编译、文件/字体/PRNX呈现、Office/PDF/HTML/PNG读回和WPF资源资格尚未执行。
- 无批准的视觉算法、HALCON/AsunImage 算子、训练/自动参数、数据库BLOB、查询刷新、打印/签章/邮件/外部程序启动或质量放行能力；这些边界保持不适用/宿主Owner责任。

剩余项均为资格或外部Owner门，而非本指导的软件设计欠账：

| 责任Owner | 仍需提供的证据 | 受影响范围 |
|---|---|---|
| DevExpress适配器实现Owner | .NET 10/25.2.3消费编译、真实DX对象/流/同步worker释放、取消到原Task结束 | R-A1/R-A2/R-U1运行资格 |
| 文件/字体/格式验证Owner | 受控字体文件及覆盖/嵌入、PDF/PRNX/Office/HTML/PNG真实读回Golden、长文本与三语样本 | 对应格式发布及WPF预览 |
| IM-066 storage-database / Store Owner | 文件对象、Claim/Publish原子组、fencing、保持租约、重启和撤权线性化 | R-C3真实持久化、交付和视图读取 |
| 平台事实/统计/授权/语言Owner | 正式 DTO/Schema 映射、消费者规模与阈值、策略/词条批准和PageContract | 平台集成、性能目标和产品权限 |
| 产品WPF集成Owner | 固定1920×1080真实TestHost、DPI/UIA/键盘/双STA/Dispatcher迟到与关闭 | R-U1产品接入 |

模块自身仍须在获准实现阶段执行 §15.1 的 Core/Adapter/Wpf 工程、TC01–16、TF01–08、TU01–08 和 BP-C1/C2/C3/H/A1/A2/U1；本轮未创建工程、未编译、未运行真实格式或WPF。合成向量与Simulator只能证明文档协议和无UI编排，不能替代上述证据。全范围结论为“文档设计闭合，真实实现/运行/生产资格未关闭”。

原会话增量自审已修正PDF正常Parent/共享Font与非法Kids循环的区分、MaxWorkers=1的逐调用执行槽、生成前完整资源预约、字体SourceRevision绑定、DataXlsx精度与Metadata自摘要边界、PRNX容器递归、图片原文件hash与导出像素的区分及三语资源/HTML闭合规则。定向文档验证通过：复用tools.validate_docs.targets检查本指导本地目标与fragment；核章节、TC/TF/TU覆盖、公开声明唯一性、C#示例括号和表格列；新增边距/列宽、cmap4/12、CSV转义/Base64、数字精度边界与多part摘要字节顺序断言通过。本机25.2.3官方XML已核新增导出/读回/页树及DXBitmap.GetPixel公开入口；旧Rows/Template完整向量和双Host Program保留，不重复重算或重新接收。上述是指导一致性和协议断言，不是C#消费编译、真实格式/字体/PRNX/WPF、性能或产品验收；本轮唯一写入仍是本文件。

## 16. 已读依据、版本和研究限制

- [独立模块架构](../INDEPENDENT-MODULE-ARCHITECTURE.md)、[DEV-GOV-010](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)：边界和逐切片准入唯一上位规则；本文是reporting实施唯一正文。
- [PKG-046](../../shared-modules/packages/PKG-046_Reporting.md#reporting-source-evidence)：历史来源/迁移映射，复用2026-09-28固定官方研究；不是第二当前指导。[DEV-PLT-018](../../shared-modules/guidance/02-platform/DEV-PLT-018_数据、报告、归档与数据主权开发指导.md)与[DEV-CONTRACT-002](../../13-contract-candidates/DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导.md)用于平台映射，不将候选DTO注入Core。
- DZ-XVision原件和SHA-256统一见[README](../../references/project-snapshots/DZ-XVision/20261004/README.md)/[manifest](../../references/project-snapshots/DZ-XVision/20261004/source-manifest.json)，§8只采纳字段/任务需求，不复用SQL、全局计数、客户阈值和判定。AsunControl快照没有所述reporting bin程序集，删除旧错误路径；当前API依据是本机安装目录公共XML，不是扫描其内部。

### 16.1 DevExpress 官方公共资料与本机25.2.3签名

2026-10-09联网请求docs.devexpress.com目标25.2页返回403；2026-10-10定向请求Microsoft/RFC资料DNS不可达，未冒充新资料已读，不无限重试。已有官方固定证据复用，新增签名以本机`C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/`的公共XML文档实读确认（只读取文档，不下载/安装/查产品授权）：

| 公共文档/入口 | 可用事实、选择和限制 |
|---|---|
| XtraReports.v25.2.xml；[ExportToPdfAsync](https://docs.devexpress.com/XtraReports/DevExpress.XtraReports.UI.XtraReport.ExportToPdfAsync%28System.IO.Stream-DevExpress.XtraPrinting.PdfExportOptions-System.Threading.CancellationToken%29?v=25.2) | Stream/Options/token异步重载真实存在；CreateDocumentAsync及Xlsx/Docx/Html/Image流重载已核。token支持不证明实际资源排空，§6/TC12–14保留原Task |
| 同文档LoadLayoutFromXml(Stream,bool)、ScriptsSource、ScriptPermissionManager/ExecutionMode.Deny | XML加载有“不加载不可信来源”安全注释；脚本不安全且默认禁用。选择受限TemplateDefinition对象构建，拒REPX/scripts；不声称扫描XML可形成沙箱 |
| [PdfStreamingExporter](https://docs.devexpress.com/XtraReports/DevExpress.XtraReports.UI.PdfStreamingExporter?v=25.2)、[CachedReportSource](https://docs.devexpress.com/CoreLibraries/DevExpress.XtraPrinting.Caching.CachedReportSource?v=25.2) | 复用已有固定研究；streaming同步/多线程与页面缓存不等于输入有界。v0.2只用固定异步导出路线，不给编码者任选fallback |
| ReportUnit、XRControl.BoundsF/Font/Text/CanGrow、XRTable.Rows/Row.Cells；Printing.v25.2.Core.xml | 单位随report；本版选HundredthsOfAnInch+mm换算。ImageExportOptions.PageRange是明确字符串；PrintingSystemBase.SaveDocument/LoadDocument(Stream)、PageCount、ImageSource(DXImage,bool)/Dispose已核 |
| Drawing.v25.2.xml、Docs.Spreadsheet/Spreadsheet.Core.v25.2.xml | DXImage.FromStream、Workbook.SaveDocument/LoadDocument(Stream,DocumentFormat)、CellValue string/Int64/decimal/bool/DateTime/TimeSpan隐式转换和Worksheet.Cells公开入口；只处理自有输出，不载任意外部Office文件 |
| Xpf.Printing/DocumentViewer.Core/Docking/Grid.Core/Grid/Core.v25.2.xml | DocumentPreviewControl.OpenDocument(string)、DocumentChanged/DocumentLoaded、Document/IsLoaded/IsCreating/DocumentException、CloseDocumentCommand、页码/缩放/FindTextCommand/TextSearchParameter及MessageBoxServiceTemplate/DialogServiceTemplate已核；自有chrome关闭原生面板。Dock/Grid/Bars使用实例公开入口，不把PrintingSystem当object DocumentSource |
| [OpenDocument(string)](https://docs.devexpress.com/WPF/DevExpress.Xpf.Printing.DocumentPreviewControl.OpenDocument%28System.String%29?v=25.2)、[MessageBoxServiceTemplate](https://docs.devexpress.com/WPF/DevExpress.Xpf.Printing.DocumentPreviewControl.MessageBoxServiceTemplate?v=25.2)；本机Xpf.Printing/DocumentViewer.Core与Mvvm/Core XML | OpenDocument为公开PRNX文件恢复路线；DocumentChanged/Loaded与CloseDocumentCommand为显式生命周期观察；Mvvm.IMessageBoxService.Show五参数返回MessageResult，IDialogService.ShowDialog六参数返回UICommand；Xpf.Core提供Mvvm.UI.ServiceBase，公开基类为Animatable行为，服务采用固定XAML模板及显式OwnerRef。SDK实例服务、原生搜索文本映射见§9.3.1，不用进程Active切语言 |
| [OpenType `cmap`规范](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap)、[GlyphTypeface.CharacterToGlyphMap](https://learn.microsoft.com/en-us/dotnet/api/system.windows.media.glyphtypeface.charactertoglyphmap?view=windowsdesktop-10.0)、[GlyphTypeface.FontUri](https://learn.microsoft.com/en-us/dotnet/api/system.windows.media.glyphtypeface.fonturi?view=windowsdesktop-10.0) | 本轮实读用于冻结无UI字体覆盖检查和WPF独立对照；不将字体解析或WPF作为Core依赖，不以公开文档代替字体文件/嵌入/分页Golden |
| [Adobe公开ISO 32000-1:2008原件](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf) | 只读内存提取原件相关物理页45–67（对象/xref/ObjStm）和292–296（FontDescriptor/FontFile），原件22,491,828 bytes/756页，SHA-256=`9de0ca9e8570d6209e8bd48a355be8eb6ec376acfc3fc3ae97cd8730351417ff`；作为§7.4.4 PDF结构/字体扫描依据，不引入Python运行依赖，不声称全文/实际PDF生成已验证 |

本机XML文本SHA-256（作为实际签名证据，不是用户依赖授权审查）：XtraReports=`ea2f1d145a5a534ebb7b330f8151de029ef21d370d5f0c57b29e06bbbc1028c5`；Xpf.Printing=`4fecd63879405c9e1659c42b9f4af4e6301d5e2f918425e82d5f991a478f385b`；Xpf.DocumentViewer.Core=`a5413b3ae752aca76b868bff77ea91d7a640a8a80595fa352f4f077a93008652`；Xpf.Docking=`b11b45dd7afc27b5e16b679a6a9e2e4291ecd13cb1f8e1b7c0fbe4e94a64477f`；Xpf.Grid.Core=`9ca164e53a54e5bc0eb6432a709e95c9295e60db3b0eac4fabf6dd32604b8eba`；Xpf.Core=`cf99d297b336a80f2361fa8bb79369434a6a10b9426efa670d636803433e8196`；Printing.Core=`51fe396b51c57e58b0624365bb2441149f7508f1a2d4f0d9df9d9eda6999409a`。Mvvm=`3690ca1fe9e644c4abb7957715d77243b022066146460f0abddd249ca5f768e0`。这些依据不能证明真实WPF/原生线程/取消/性能已通过。

### 16.2 固定GitHub源码、依赖和测试审查

[官方示例](https://github.com/DevExpress-Examples/reporting-wpf-mvvm-show-report-document-preview)固定commit=`4eadceb21b2df58cf9497288870ad046c72e4f14`，2026-10-09联网读ReportCatalogViewModel.cs、LICENSE和固定树成功，并复用本地已归档全文。实读[CatalogViewModel](../../references/open-source/devexpress_examples/reporting-wpf-mvvm-show-report-document-preview/4eadceb21b2df58cf9497288870ad046c72e4f14/CS/Models/ReportCatalogViewModel.cs)、[PreviewDialogViewModel](../../references/open-source/devexpress_examples/reporting-wpf-mvvm-show-report-document-preview/4eadceb21b2df58cf9497288870ad046c72e4f14/CS/Models/DocumentPreviewDialogViewModel.cs)、[MainWindow.xaml](../../references/open-source/devexpress_examples/reporting-wpf-mvvm-show-report-document-preview/4eadceb21b2df58cf9497288870ad046c72e4f14/CS/MainWindow.xaml)、csproj/packages.config、DbContext、LICENSE及vale workflow。借鉴目录选择/独立预览模型与DocumentSource显式绑定，排除同步DbContext.Load、任意FromStream、全局当前Report与控件内置导出权限替代；不复制整个工程。

本轮补查[官方PRNX用途示例固定README](https://github.com/DevExpress-Examples/out-of-maintenance-reporting-wpf-load-prnx-document/blob/3ea5b61a233d093a15fa1471883d51dba778ab4e/README.md)，commit=`3ea5b61a233d093a15fa1471883d51dba778ab4e`，已标out-of-maintenance并指向SupportCenter E4713；该固定树未提供产品源码/测试，不能当作25.2.3运行或关闭证明。当前选型依据是本机官方OpenDocument及服务公开文档，复用旧MVVM例的显式实例绑定思想，未复制过时PRNX适配代码。

实际依赖.NET Framework4.7.2、DevExpress24.2、EF6.4.4、SQLite1.0.115.0；仓库树未发现产品测试，vale只校README词条，不能当报告/取消/资源测试。LICENSE是示例免责声明和产品条款引用，不标为MIT；本轮只研究设计，不迁代码、不再询用户已确定的依赖授权。版本/固定原字节/hash统一见[REF-002报表研究](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#reporting-source-research)，本文已写可迁移结论和局限，不依赖研究脚本补规格。

.NET取消依据复用2026-10-09实读[Cancellation in Managed Threads](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads)，当时页面source commit=`8b2033ff9f3b355e8fca60a4b0ee5e6501ab4fc7`。只采用协作取消/调用者与监听者分离的事实；有限观察不是取消完成证明，真正原Task及资源退出按§6/14验证。RFC4180 quoting为冻结格式规则，本轮在线未成功读其原文，实际parser/readback资格留TF06，不把引用当网络实读。


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

## 附录 A：唯一契约导航与版本兼容

当前唯一Module API Contract是**v0.2，§3–7及§9/14补充公开接入**。旧v0.1泛化附录及历史产品候选DTO不再是可并行实现的API。兼容矩阵：v0.2模块只接纳report-binary-v2/report-rows-v2/report-layout-v2；未知schema拒绝；旧历史文件继续由原renderer/codec只读，不重算hash或换成当前模板。新增枚举tag/字段/角色、改字段语义、单位、hash规则、必需模板节点或端口资源责任必须升契约版本并显式迁移，不静默默认。

Core规格准备依据唯一为DEV-GOV-010 §3.1；主控已接收R-C1/R-C2/R-C3六项规格，当前为ModuleCoreImplementationReady，仅Core/受控Simulator/根Owner/两个无UI Host。R-A1/R-A2/R-U1指导内容已接收，真实资格仍PreparationIncomplete / NotReady，不能因Adapter无UI而标CoreReady。章节存在、模块索引 accepted、模板示例或结构PASS本身不授予准入；本次状态依据为主控明确接收。各切片剩余门见§15，平台事实Owner不被本契约覆盖。HALCON/AsunImage不适用，不复制“逐算子核验”门到报告模块。

本轮有限自审：第一轮按输入/模板/统计/产物身份复审，修正重叠分类、元数据自引用及格式组可见性；第二轮按两Host失败/取消/迟到/移交走查，补Factory前登记、唯一清理epoch、最终回调与持久收尾的排空边界。定向校验覆盖本文链接/锚点、声明唯一性/括号、章节/测试ID、规范标量字节及本机XML指纹；仅为指导一致性，不代替C#编译或真实运行。

0.3.1-prep定向退修：§6.1外调前Starting；§3.3/3.4/4.2/7.1/11的Docx PageCount不适用与RendererPageCount来源；§3.2报告级Header/Footer；§11.1.1独立75字节Rows/hash向量；§14.4完整双Host合成Program与全部私有端口/租约，明确未知内存计量及非真实格式边界。只做指导一致性与独立字节复算，未创建/执行C#、报告或WPF工程；该修订当时等待主控接收，当前接收状态以§15.2为准。

0.3.2-prep有限收口：§11.1.2/14.4增加独立完整263字节Template输入、字段拼接、HEX/长度/hash与受测codec断言；§7.2/9.2.1冻结受控PRNX→实例临时文件→OpenDocument恢复、原Dispatcher调用/事件/关闭与迟到保留；§9.3.1冻结实例Grid/Bars/Dock、自有导航搜索和明确Owner的三语消息/对话服务，§11/15/16同步验收及证据。实际编译、PRNX呈现/字体、SDK关闭资源、三语UIA及格式/性能资格仍未执行；本次主控接收后，逐切片状态已同步至页首与§15.2，API/算法/codec/Host正文保持不变。

0.3.3-prep全范围收口：按当前IM-044批准范围补齐§7.2.1受限对象树/分页/固定导出选项、§7.2.2无UI字体cmap覆盖与三语长文本边界、§7.4 Adapter工厂/CSV/DataXlsx列协议/独立格式Verifier、§9.1.1 WPF公开装配/权限/双STA根Owner及§9.4视觉细节/资源键/恢复文案；复核§15.4确认所有可决定软件设计闭合，剩余为真实程序集/格式/字体/Store/WPF/客户Profile/产品Owner资格门。未创建或执行C#、真实文件/字体/PRNX/WPF/性能工程。
