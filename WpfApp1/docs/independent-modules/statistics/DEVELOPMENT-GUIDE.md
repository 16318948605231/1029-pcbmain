# IM-043 统计与过程监测独立模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`S1, S2, S3, S4, S6, S7`

- 文档 ID：`IM-043`；来源：`PKG-045`；模块键：`statistics`
- 中文名称：统计与过程监测
- 版本：`0.3.0-prep`；规格准备状态：S1–S4 `ModuleCoreImplementationReady`（主控接收通过，仅规格准备）；S5 不纳入本版Core（宿主产品接入另行界定）；S6 `ModuleCoreImplementationReady`（2026-10-11 主控接收，仅规格准备）；S7 常方差比 Deming 点估计 `ModuleCoreImplementationReady`（2026-10-11 主控接收，仅规格准备）
- 编写日期：2026-10-04
- 本轮修订：2026-10-12；核心契约修订 `0.3.0-prep`，补齐已批准范围的 Core 装配身份、Boost Adapter 生命周期和完整 SPC 无 UI 双宿主；S6/S7 六项文档规格保持主控接收；保留既有 S1–S4 接收状态及 §12 的纯托管 Exe 测试执行约定；按附录 A 迁移，不原地解释旧请求。
- 工程准入：`NewProjectRequired`；未发现契约完全匹配的 Statistics Core。实现切片开始时创建 `src/Modules/statistics/Asun.Modules.Statistics.Core/`，测试放在 `tests/Modules/statistics/Asun.Modules.Statistics.Core.Tests/`，namespace 为 `Asun.Modules.Statistics`。
- 规划消费者：SPC 工作台、质量分析工具、工程数据工具
- 当前结论：本页是独立模块的金标准设计；当前批准范围的软件设计已闭合，S1–S4/S6/S7 均为 `ModuleCoreImplementationReady`（仅规格准备）；尚未声明已实现、已编译、已通过 Golden/Replay、现场资格或生产验收。
- 输入只能是有界结构化观察及其文件对象引用；图像、点云、高度场和视频字节留在 IM-066 硬盘文件存储。Statistics 不读取大文件进数据库，也不将像素/点云临时物化成无界观察数组；需视觉特征时由已批准算法模块输出带来源/单位/版本的结构化值。
- 模块级设计评审态：`DesignReview`（方案可评审）。§15.1「全模块批准范围的软件设计结论」给出本模块当前批准范围的设计结论，§16「自审清单」记录本版本自审；该状态只表示方案可供评审，不表示已实现、已集成、已测性能、已过 WPF/HIL 或已获生产资格。

## Core implementation binding

- 上述工程路径是本模块唯一 Core 写入位置；仅在实现切片获准启动时创建。输入/回执/存储适配器和 UI 投影不进入 Core。
- S7 ConstantRatioDeming 点估计六项文档规格于2026-10-11由主控接收为 `ModuleCoreImplementationReady`（仅规格准备），S1–S4/S6 接收保持。S5 不纳入本版 Core，不列内部待补任务。实施任务授权、真实构建/后端身份、Golden 运行及数值/消费者资格仍各按其门禁关闭；本轮只完善唯一指导，不创建工程或修改代码。
- 端口与不可变值类型随 Core DLL 发布，外部适配器实现由宿主引用；Core 仅依赖 .NET 10 BCL，不引用 WPF、DevExpress、AsunImage、平台 Shell/私表或 DI 服务定位器。唯一实现工程为 `src/Modules/statistics/Asun.Modules.Statistics.Core/Asun.Modules.Statistics.Core.csproj`，唯一测试工程为 `tests/Modules/statistics/Asun.Modules.Statistics.Core.Tests/Asun.Modules.Statistics.Core.Tests.csproj`，最小 console Host 放在 `tests/Modules/statistics/Asun.Modules.Statistics.TestHost/Asun.Modules.Statistics.TestHost.csproj`；三者 namespace 根均为 `Asun.Modules.Statistics`，测试/Host 可分别用 `.Tests`/`.TestHost` 后缀。
- 本轮只写本指导。将来实现允许上述三个工程、本模块文档目录，以及 §7.1.3.6 指定的模块内分布适配工程；禁止其它模块、共享 Schema、产品装配、原参考项目、AsunImage 内部及 `tools/`。跨项目引用/共享合同采纳由主会话串行处理。独立发布 Core DLL、可选分布适配 DLL、XML API 文档、版本/兼容矩阵及对应测试输入；Host 不是生产依赖，无 UI DLL 或隐藏窗口。

本模块为无 UI 的有限统计计算与过程监测能力。它接收调用方已经定义并冻结的观察单位、范围、数据和统计方法，返回带完整性、适用性和来源关系的统计快照或实时投影。调用方拥有业务流程、目标关联、工艺解释、质量放行、复判、权限策略和设备副作用。

## 1. 职责、边界和准入

### 1.1 模块负责

- 按已批准的 `MetricDefinition` 和 `MethodRevision` 处理描述性统计、分组累计、过程能力、有限控制图和过程监测信号。
- 验证固定输入的范围、单位、观察单位、去重关系、分母、子组、完整读取证明和方法适用性。
- 保留合法的 `Unknown`、缺测、未测、排除、无效和不适用原因；分别报告输入完整性与统计适用性。
- 产生不可变的统计快照或明确标为实时的统计投影，记录输入引用、方法/参数版本、范围、分母和执行诊断。
- 以有界读取、有限缓存、可取消计算和可观测事件支持离线重算、持续监测及回放。

### 1.2 模块禁止

- 不引用 PCB、PCBA、SPI、AOI、点胶、涂覆或其它制程判定，不拥有板、Pad、孔、元件或缺陷的业务含义。
- 不决定首检/复测选择、目标关联、工艺阈值、必检全集、质量放行、人工复判或设备命令；这些由原事实/质量/应用 Owner 提供。
- 不把 `NG`、`Unknown`、未测或方法不适用自动剔除，不把缺测填成 0，不把水位当作总体封口。
- 不创建第二套快照、查询、范围、指标、告警、权限或事实 Store；不读取 `latest` 猜测生产状态。
- 不持有页面 ViewModel、数据库连接、HALCON/AsunImage 原生句柄、SDK 句柄或宿主全局可变状态。
- 不因 UI 筛选、缩放、抽稀或语言切换重算或修改原统计范围。
- 不提供自动调参、设备反馈、工艺补偿、质量放行或外部提交副作用。

### 1.3 独立接入准入

宿主必须能在无 WPF、无隐藏窗口、无数据库上下文的最小进程中调用核心。纯 Core 使用本页 §3、§7.1.3 及附录 A 的同一套模块值契约；C-01、C-04、C-07 的产品字段、序列化及 Owner 未采纳只阻断产品映射/持久化切片，不阻断不写产品事实的 Core。正式平台接入另外绑定唯一 Contract/Schema Owner、State/Owner/Authority、版本化方法、输入快照及回执关系。S1–S4 六项规格已由主会话逐项接收，状态为 ModuleCoreImplementationReady；S6 六项文档规格于2026-10-11由主控接收，同为 ModuleCoreImplementationReady（仅规格准备）；S7 常方差比Deming点估计六项文档规格于2026-10-11由主控接收为ModuleCoreImplementationReady（仅规格准备）；S5 明确不纳入本版Core；HALCON替代路线未采用，不定义适配端口、工程或内部待实现任务，产品接线为宿主另行授权的外部责任。规格接收不替代实施任务授权或实现/运行验收，本轮不创建工程。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Statistics.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1.3 已明确"最小宿主无 WPF/数据库上下文即可运行 Core"。

**Blazor/Web**：SPC 看板是 Web 端 P1 优先需求（Cpk、控制图、趋势线实时推送）。统计计算在服务端执行；SPC 图表数据通过 SignalR 实时推送；浏览器不重新计算 Cpk/均值/标准差；统计历史通过 gRPC/REST 查询，单次最多 1000 数据点。

**AI 漂移监控集成**：`ai-dataset-governance` §7.4.3（L3）的 PSI/KS 检验漂移监控依赖本模块的统计基础设施；漂移观察结果写入 `DriftObservation`，本模块提供统计能力，不执行 AI 训练。

**HALCON 不适用**：本模块是纯统计分析，不执行视觉算法；HALCON 备选 CI 不涉及本模块。

## 2. 依赖和数据流

```text
事实/评价 Owner ──→ 固定或实时输入适配器 ──→ IM-043 Core
             MetricDefinition + MethodRevision + 预算/取消
                                      │
                          StatisticsSnapshot / LiveProjection
                                      │
                    SPC、质量分析、工程数据工具、报告/UI投影
```

直接语义依赖为：

- `PKG-042 Query`：提供固定输入引用、成员/范围、排序、分块和完整读取回执；实时读取必须明确标注实时语义。
- `PKG-039 Evaluation`：提供源评价、有效性和规则修订引用；模块不重判原事实。
- `DEV-DOM-058A`：提供 SPC 公式与常数参考；模块值契约、执行步骤和数值实现以本指导为唯一实施正文。
- `PKG-046 Reporting` / UI-PCS-008：只消费统计结果并核对范围/来源关系。

持久回执由宿主的原 Snapshot/Commit Owner 保持；Statistics Core 不自建事实 Store，也不在 `ComputeAsync` 内调用保存。组合根可注入只读 `IStatisticsOperationReceiptSource` 查询原计算状态；它不是统计保存端口。宿主在收到已排空结果后，用自身原保存操作提交；保存 Unknown 沿该保存 OperationId 查询，不把已完成计算重新标为运行或重算来掩盖提交。未注入回执端口时只支持当前实例执行查询，跨进程结果为 Unknown，不能由 NotFound 推断原 worker 已停止。

本模块不是视觉算法模块：弱信号、遮挡、ROI、像素/点云候选及自动视觉参数均不适用；只消费上游已给出的数值与状态，不据其数值大小推导有效性。当前 Core 固定采用 §7 的托管数值路线；t/F 分布任务仅通过 §7.1.3.6 已冻结的可选 Boost Beta 端口执行，未配置时明确拒绝，不切换后端。已比较未采用的路线仅在 §15 保留研究依据，不构成实施能力或待办。

## 3. 模块公共值契约与平台映射边界

以下声明冻结模块 Core `0.3` 的公开形状，统一置于 `Asun.Modules.Statistics`；使用 `System.Collections.Immutable.ImmutableArray<T>`，不以 `IReadOnlyList` 包装可变列表冒充不可变输入。产品 JSON/数据库 DTO 由原 Contract Owner 映射，不复制本节为第二平台 Schema。字符串身份/修订必须非空；`ContentHash` 必须对应提供者声明的原内容，不按显示舍入值或本地随机序列猜 hash。请求被接纳前完成快照化，之后宿主修改原集合不得影响运行。

### 3.1 输入类型

```csharp
public sealed record StatisticsRequest(
    string OperationId,
    string MetricDefinitionId,
    string MetricDefinitionRevision,
    string MethodRevision,
    MetricDefinition Definition,
    ImmutableArray<StatisticalMethod> Methods,
    StatisticsScope Scope,
    InputReference Input,
    SubgroupPolicy Subgroup,
    CompletenessPolicy Completeness,
    NumericPolicy Numeric,
    ExecutionBudget Budget);

public sealed record StatisticsScope(
    string ObservationUnitKind,
    string MeasurandId,
    string Unit,                 // SI 或经批准的业务单位；不可为空
    TimeRange? TimeRangeUtc,     // [start,end)，UTC；成员范围与时间域二选一或由政策明确组合
    string? MemberSetReference,
    string ScopeRevision,
    string? SpecificationRevision,
    string? BaselineRevision,
    string SourcePolicyRevision);

public sealed record InputReference(
    string SnapshotId,
    string SnapshotRevision,
    InputMode Mode,              // FixedSnapshot 或 LiveView
    string QueryReceiptId,
    string SourceBoundary,
    string ContentHash,
    string? WatermarkId,
    bool ReadComplete,
    bool CanReplay);

public sealed record NumericPolicy(
    NumericKind Kind,             // Binary64；计数单独用 checked Int64
    int? SignificantDigits,
    double AbsoluteTolerance,
    double RelativeTolerance,
    OverflowPolicy Overflow);

public sealed record ExecutionBudget(
    int MaxRows,
    int MaxGroups,
    int MaxRowsPerGroup,
    int MaxChartPoints,
    int ReadBatchSize,
    TimeSpan WallClockLimit,
    TimeSpan CancellationResponseLimit,
    long MaxWorkingSetBytes,
    long MaxBufferedBytes,
    int MaxPendingBatches,
    int MaxSignals,
    int MaxNotifications,
    TimeSpan DrainObservationLimit);

public sealed record StatisticsObservation(
    string ObservationId, string SourceRevision, string ContentHash,
    string PhysicalUnitId, DateTimeOffset ObservedAtUtc, long SourceSequence,
    string SegmentKey, string StratumKey, string GroupKey,
    bool BreakBefore, ObservationState State, string? ReasonCode,
    string Unit, double? Value, UnitClassification Classification,
    long? EventCount, long? OpportunityCount, double? Exposure,
    string? EvidenceReference, string MemberReference);

public sealed record StatisticsInput(
    InputReference Reference,
    ImmutableArray<StatisticsObservation> Observations,
    InputClosure Closure,
    string ContentHash);

public enum InputMode { FixedSnapshot, LiveView }
public enum NumericKind { Binary64 }
public enum OverflowPolicy { Reject }
public enum ObservationState { Valid, Unknown, Missing, Unmeasured, Invalid, NotApplicable, Excluded }
public enum UnitClassification { NotProvided, Satisfied, NotSatisfied, Unknown }
public enum ObservationKind { Continuous, ClassifiedUnit, CountExposure }
public enum CompletenessPolicy { RequireAll, ApprovedObservedSubset }
public enum QualificationState { Approved, Exploratory, Unknown, Rejected }
public enum BaselinePhase { EstimateCandidate, FrozenMonitoring }
public enum EstimatorKind { Moments, UnitRate, EventRate, Capability, XbarR, XbarS, IMR, P, NP, C, U }
public enum WithinEstimator { None, RangeD2, SbarC4, MovingRangeD2 }
public enum RuleKind { BeyondLimits, EightSameSide, TwoOfThreeBeyondTwoSigma, FourOfFiveBeyondOneSigma }
public sealed record TimeRange(DateTimeOffset StartUtc, DateTimeOffset EndUtc);
public sealed record DefinitionReference(string Id, string Revision, string ContentHash);
public sealed record InputGap(
    string MemberReference, ObservationState State, string ReasonCode,
    string? SegmentKey, string? StratumKey, string? GroupKey,
    DateTimeOffset? ObservedAtUtc, long? SourceSequence);
public sealed record InputClosure(
    long? ExpectedMembers, string? ExpectedMemberSetHash,
    bool ReadComplete, bool PopulationClosed,
    string? ClosureReceiptReference, ImmutableArray<InputGap> Gaps);
public sealed record MetricDefinition(
    DefinitionReference Identity, ObservationKind Kind,
    string ObservationUnitKind, string MeasurandId, string Unit, string ExposureUnit,
    DefinitionReference SourcePolicy, DefinitionReference SelectionPolicy,
    DefinitionReference? ObservedSubsetApproval,
    DefinitionReference AggregationPolicy);
public sealed record SubgroupPolicy(
    DefinitionReference Identity, int? FixedSize,
    TimeSpan MaximumSpan, TimeSpan MaximumAdjacentGap,
    DefinitionReference Qualification);
public sealed record StatisticalMethod(
    string MetricId, DefinitionReference Identity, EstimatorKind Estimator,
    long MinimumSamples, long MinimumCompleteGroups, QualificationState Qualification,
    DefinitionReference QualificationEvidence, WithinEstimator Within,
    SpecificationLimits? Specification, FrozenBaseline? Baseline,
    BaselinePhase Phase, ImmutableArray<ControlRule> Rules);
public sealed record SpecificationLimits(
    DefinitionReference Identity, double? Lower, double? Upper, string Unit);
public sealed record FrozenBaseline(
    DefinitionReference Identity, EstimatorKind Chart,
    string SegmentKey, string StratumKey, string MeasurandId, string Unit,
    double Center, double? WithinSigma, double? RangeOrDeviationCenter,
    long? FixedOpportunityCount, double? FixedExposure,
    DefinitionReference Method, DefinitionReference Constants,
    DefinitionReference ApprovedScope);
public sealed record ControlRule(DefinitionReference Identity, RuleKind Kind);

public enum OperationState
{
    Accepted,
    Running,
    Draining,   // 已接收 operation 的资源仍在排空；不得视为终态
    Completed,
    Cancelled,
    TimedOut,
    Failed,
    Rejected,
    Unknown
}

public enum OperationOutcome
{
    None, Completed, Cancelled, TimedOut, Failed, Unknown
}

public enum DrainState
{
    NotStarted,
    Draining,
    Drained,   // 已确认所有租约、在途调用、缓冲、任务和原生资源均已释放
    TimedOut,  // 达到排空截止，仍有资源或调用未确认；非终态观察状态
    Unknown    // 无法判断是否仍有资源或调用在途；非终态观察状态
}

public interface IStatisticsInputSource
{
    IAsyncEnumerable<IReadOnlyList<StatisticsObservation>> ReadBatchesAsync(
        StatisticsRequest request, CancellationToken cancellationToken);
    ValueTask<InputReference> GetReferenceAsync(CancellationToken cancellationToken);
    ValueTask<InputClosure> GetClosureAsync(CancellationToken cancellationToken);
}

public interface IStatisticsMonitor : IAsyncDisposable
{
    string MonitorId { get; }
    IAsyncEnumerable<StatisticsNotification> Notifications { get; }
    Task<StatisticsOperationStatus> Completion { get; }
    ValueTask<StatisticsOperationStatus> GetStatusAsync(CancellationToken cancellationToken);
    ValueTask StopAsync(StopMode mode, CancellationToken cancellationToken);
    ValueTask<StatisticsDrainResult> DrainAsync(
        DateTimeOffset deadlineUtc, CancellationToken cancellationToken);
}

public enum StopMode { Drain, Cancel }
public enum WindowMode { Tumbling, SlidingRebuild }
public sealed record StatisticsMonitorRequest(
    string MonitorId, StatisticsRequest Template, WindowMode Mode,
    DateTimeOffset OriginUtc, TimeSpan Width, TimeSpan Step,
    int MaxConcurrentWindows, int MaxRetainedWindows);
public sealed record StatisticsWindowInput(
    long WindowSequence, StatisticsRequest Request, IStatisticsInputSource Source);
public interface IStatisticsWindowSource
{
    IAsyncEnumerable<StatisticsWindowInput> ReadWindowsAsync(
        StatisticsMonitorRequest request, CancellationToken cancellationToken);
}

public sealed record StatisticsOperationStatus(
    string OperationId, OperationState State, OperationOutcome PendingOutcome,
    bool IsTerminal, bool InputComplete,
    string? ErrorCode, int InFlightBatches,
    DrainState DrainState, bool CanReuseResources);

public sealed record StatisticsDrainObservation(
    string OperationId, string DrainAttemptId, DrainState State,
    int? RemainingOperations, int? OutstandingResourceCount,
    DateTimeOffset ObservedAtUtc, bool IsTerminal, bool CanReuseResources);

public sealed record StatisticsDrainResult(
    DrainState State, int? RemainingOperations, int? OutstandingResourceCount,
    DateTimeOffset ObservedAtUtc, string DrainAttemptId,
    bool IsTerminal, bool CanReuseResources);
```

### 3.2 参数单位、范围和默认值

| 参数 | 单位/类型 | 允许范围 | 设计默认值 | 约束 |
|---|---|---|---|---|
| `ReadBatchSize` | 条，`int` | 1–65,536 | 4,096 | 仅为分块资源默认值，不是抽样或分母策略；超限拒绝。 |
| `MaxRows` | 条，`int` | 1–2,000,000,000 | 由宿主 Profile 提供 | 未提供批准 Profile 时为 `Unspecified`，不能以默认值宣称全量。 |
| `MaxGroups` | 组，`int` | 1–10,000,000 | 由宿主 Profile 提供 | 超限返回预算错误，不截断后宣称完整。 |
| `MaxRowsPerGroup` | 条/组，`int` | 1–10,000,000 | 由宿主 Profile 提供 | 影响子组完整性；不能自动拆组。 |
| `MaxChartPoints` | 点，`int` | 1–10,000,000 | 100,000（资源建议，实际请求由Profile显式给出） | 本版限制最终原始图点总数；超限明确失败。宿主显示抽稀另行处理，不能删信号后冒充完整结果。 |
| `WallClockLimit` | `TimeSpan` | >0 且 ≤宿主任务截止 | 必须显式提供 | 到期将已接收 operation 转为 `Draining`、`PendingOutcome=TimedOut`；不隐式重试或提前发终态。 |
| `CancellationResponseLimit` | `TimeSpan` | >0 | 必须显式提供 | 只约束停止响应，不表示底层已结束。 |
| `MaxWorkingSetBytes` | 字节，`long` | >0 | 由 PerformanceProfile 提供 | 仅控制本任务预算，不可挤占其它宿主。 |
| `MaxBufferedBytes` / `MaxPendingBatches` | 字节 / 批 | >0；批数≥1 | 必须显式提供 | 约束自有复制、组/去重、结果及排序状态；入队前预留，满则等待或拒绝，不丢数据。 |
| `MaxSignals` / `MaxNotifications` | 条 | ≥1 | 必须显式提供 | 信号/结果超限明确失败；通知进度可合并，完整终态仍可查询。 |
| `DrainObservationLimit` | `TimeSpan` | >0 | 必须显式提供 | 单次排空观察期限，不是强制终止或释放许可。 |
| `AbsoluteTolerance` | 同输入单位 | ≥0 且有限 | 0（精确整数/声明无需容差时） | 不可用 epsilon 修复非法 M2、分母或单位。 |
| `RelativeTolerance` | 无量纲 | 0–1 | 0 | 需由方法/资格政策批准；不改变比较方向或分母。 |
| `SignificantDigits` | 位，`int?` | 1–17（Binary64） | `null` | 仅显示/序列化；未舍入值用于比较和计算。.NET `decimal` 不冒充 IEEE Decimal128；其它数值域须新方法/API 修订。 |
| `Unit` | 单位标识 | 非空、已注册且与被测量相容 | 无默认 | 不猜测 mm、µm 或比例换算；换单位形成新请求/修订。 |
| `TimeRangeUtc` | UTC 半开区间 | `start < end` | 无默认 | 不允许本地时区隐式转换；无时间域时须有固定成员引用。 |

`MinimumSampleRule`、控制限常数、首检/复测选择、缺口允许子集、规格端点和显著性/置信政策没有通用安全默认值，必须由版本化 `MetricDefinition`、`SubgroupPolicy`、`BaselineRevision` 或资格 Owner 提供。不存在时受影响指标返回 `NotComputable`/`Blocked`，不得补常数。

### 3.2.1 输入字段联合校验及方法绑定

- `Continuous` 的 Valid 行只允许有限 `Value`；事件/机会/暴露字段为空，`Classification` 不参与数值有效性。合法超规格数仍是 Valid；Unknown/Missing/Unmeasured 等行的计算值必须为空并给原因，原数值证据仅通过引用保留。质量状态不由浮点 NaN 承担。
- `ClassifiedUnit` 的已知行使用 `Satisfied`/`NotSatisfied`、无连续值/事件/暴露字段，每个已选定 `PhysicalUnitId` 贡献一个单位；Unknown 分类不算合格。完整成员范围中的 Unknown/Missing 仍保留在范围计数；p/np 仅消费已批准且完整分类的子组，不能把缺项当成功。
- `CountExposure` 使用非负 Int64 `EventCount`，并且在方法所需域提供正 `OpportunityCount` 或有限正 `Exposure`。二者同给时须有明确且可核转换政策，不能相加为分母。p/np 使用整数机会数且 `EventCount≤OpportunityCount`；c/u 的事件可多于暴露量，u 不裁到 1。ClassifiedUnit 与 CountExposure 不在同一请求混用。
- `InputReference.ReadComplete` 是读取端提供的初始承诺；最终 `InputClosure.ReadComplete` 是完成读取后的回执。`PopulationClosed` 是总体封口的另一个证据，不能由 IEnumerable 正常结束、达到水位或两项布尔相等推定。ExpectedMembers 未知用 null，非负且包括预期但没读到的成员；每个 InputGap 保留原因，不能只以 N−n 猜身份。统计分母、读到的行数和预计物理单位数分别输出。
- Closure.Gaps只描述未形成观察行的预计成员；已有Unknown/Missing行的同一成员不再添加一个Gap增加计数。ReadRows为实际读取行数（含传输重复），各状态Rows为去重后的已读取行数，满足ReadRows=各状态Rows之和+DuplicateRows；未读取缺口仍在Closure.Gaps，不伪造已读行。Gap的位置/组未知时，受影响层的IMR/连续规则/子组完整性不能证明，返回GROUP_INVALID/NotComputable；定位已知时在其正确位置形成断点，不能把所有缺口只追加在末尾。
- 去重键为原来源边界＋ObservationId＋SourceRevision：同键同hash且全部字段一致才重发仅一次，同键异hash或同hash异字段均IDENTITY_CONFLICT，不取最后一条。尝试/原事实更正选择由上游SelectionPolicy完成；Core再核PhysicalUnitId/组成员关系。两个真实重复测量有不同观察身份，不因值/hash相同删除，也不能用它们扩充板/件级分母。
- Template 的 Definition.Identity、三个原 ID/revision 字段及 Scope 中单位/观察单位/SourcePolicy 必须相互一致；Methods 的 MetricId 唯一，每种方法绑定自己的定义修订，顶层 MethodRevision 是整个有序方法集合的修订。可按同一冻结输入执行多个有限方法，分别返回结果；不存在“选一个最显著/最好看的方法”的分支。
- `MinimumSamples≥1`，但样本方差/IMR 等另按公式要求≥2或有合法相邻对。Subgroup 的 MaximumSpan/MaximumAdjacentGap 都必须正且来自政策，FixedSize 为空仅适用于个体/已定义暴露组；Xbar-R 固定 n=2–10，Xbar-S 固定 n=2–25，表与精度按 058A，不因数据量超界静默换估计量。组键、段键、层键不能为空（无分层用显式常量键）；观察按 `ObservedAtUtc, SourceSequence, ObservationId` 排序，同时间戳/序号无法证明真实先后时趋势/IMR不可评价。
- Specification 的端点按有限值/同单位核验，双侧必须 Upper>Lower；单侧输出对应 Cpu/Cpl 或 Ppu/Ppl，不补另一端。FrozenBaseline 的 Chart/Method/Constants/ApprovedScope 必须与请求匹配；Center 及所需 sigma/变异中心有限，需正变异的方法禁止零宽基线。图种要求的 FixedOpportunityCount/FixedExposure 缺失时 np/c 不适用。
- `Qualification=Exploratory/Unknown/Rejected` 不签发稳定/能力解释；描述性计数/矩仍可独立计算。Method.Identity、QualificationEvidence、规格、子组、Baseline 和 Rules 的确切修订必须留在结果中，只有 Owner 提供的 Approved 资格可启用对应方法。不以一次未命中或正态检验未拒绝替代资格。
- RequireAll 不计算缺口总体的依赖指标；ApprovedObservedSubset 必须有 Definition.ObservedSubsetApproval，保留预计/实际/排除/Unknown 计数并命名为观测子集。这不授权通用插补。InputMode=LiveView 即使数值可计算也输出实时投影，不能生成 Complete 固定快照。
- UnitRate 的完整单位占比为已确认Satisfied或NotSatisfied计数/经批准适用单位数A，A含Unknown/未测而不含获批NotApplicable/Excluded；其 Value 不是“在已知结果中合格率”。只有显式ObservedSubsetApproval才可报告已知分类子集比例，ScopeEvidence.ComputedSubsetReference/DenominatorEvidence必须标出该子集。p/np必须另满足完整分类子组和独立性，不能把P/A直接喂入图种。EventRate先checked累加事件，再按批准的整数机会或连续暴露总量相除，未知暴露禁止完整率。
- `OpportunityCount` 和计数相加使用checked Int64，转Binary64前检查≤2^53的精确整数域；大于该域的率/图点本版明确NUMERIC_OVERFLOW/NotComputable并保留原Int64计数，不能静默近似。所有负载上限、成员数和int索引缩窄同样先核验。
- Scope 的 SpecificationRevision/BaselineRevision 为空表示没有这些依赖；非空必须等于相关Method的确切修订。一个请求若要比较不同规格/基线，须按Scope分成各自请求，不能用一条全局修订代表多个物理条件。FrozenBaseline的SegmentKey/StratumKey/MeasurandId/Unit与本次受检层匹配，不能把一个层的基线套给其它层；资格引用同时核子组与源定义的适用范围。Core只核声明关系，不以hash代替外部批准。
- MinimumCompleteGroups≥1且由方法Profile提供；它约束完整合理子组数，MinimumSamples约束有效个体/分类数，二者不互代。Constants 固定表身份：R路线`nist-r-3dp-qcc-d2-v1`、S路线`nist-c4-recurrence-v1`、I-MR/p/np/c/u路线`spc-3sigma-v1`，修订`1`，内容/hash必须与058A已发布表/公式的冻结包对应；未知常数身份拒绝VERSION_INCOMPATIBLE，不从UI传入任意倍数。本版规则只有058A四种Kind，窗口8/3/5与严格比较为方法语义，不是客户默认启用。
- 全部 UTC 端点 Offset=0，Start<End；最大时窗/组跨度不与默认班次绑定。涉及单位转换必须由上游版本化转换形成新输入，Core 不从 Unit 字符串猜倍数。非有限 Value、Exposure、参数、sigma、计算中间量与结果分别定位错误。
- ImmutableArray不得IsDefault，空集合用Empty；请求的未定义枚举/null必需引用/重复MetricId/非法参数在接纳前拒绝。流式行的非法计数、空MemberReference/身份超预算在读到时定位并失败/阻断受影响指标，不能伪称源已全量提前验证。Result/Notification的数组同样非default，PointIds与ComparedValues长度相等，PointId仅在自身图组件/段/层内稳定，信号窗口引用必须都在该实际评价范围；未知数量/nullValue不以0替代。MessageKey/Code为机器键，Arguments为不参与判定的格式化参数。

未形成方法与输入的适用关系时不得开始公式：Moments/Capability/XbarR/XbarS/IMR只接Continuous；UnitRate只接ClassifiedUnit；EventRate/C/U只接CountExposure；P/NP接ClassifiedUnit完整分组，或带完整MemberReference的CountExposure整数单位汇总。汇总行须提供原成员引用/机会量及去重资格，输入行数不作为n；无原成员证明仅可作描述性事件率，不产生p/np完整子组。State=Valid且Classification=Unknown的单位行非法，应明确State=Unknown；Continuous的Classification仅来源信息，不影响Valid超规格值。

### 3.3 输出类型

```csharp
public sealed record StatisticsResult(
    string OperationId,
    string StatisticsSnapshotId,
    ResultState State,
    InputReference Input,
    ScopeEvidence Scope,
    ImmutableArray<MetricResult> Metrics,
    CompletenessEvidence Completeness,
    ImmutableArray<Diagnostic> Diagnostics,
    Provenance Provenance,
    ImmutableArray<BaselineCandidate> CandidateBaselines);

public sealed record MetricResult(
    string MetricId,
    string Component,
    string SegmentKey, string StratumKey,
    MetricApplicability Applicability,
    string Unit,
    double? Value,
    DenominatorEvidence Denominator,
    ImmutableArray<SubgroupEvidence> Subgroups,
    ControlSignalEvidence? Signals,
    ImmutableArray<ObservationReference> Evidence,
    ImmutableArray<ControlChartPoint> ChartPoints);

public enum ResultState { Complete, Partial, LiveProjection, Blocked, Invalid, Cancelled, TimedOut, Failed, Unknown }
public enum MetricApplicability { Computed, NotComputable, NotApplicable, InsufficientData, InvalidInput, Blocked, Overflow, Unknown }
public sealed record ObservationReference(
    string ObservationId, string SourceRevision, string ContentHash,
    string? EvidenceReference);
public sealed record ScopeEvidence(
    StatisticsScope Scope, DefinitionReference Definition,
    string InputMemberHash, string ComputedSubsetReference);
public sealed record CompletenessEvidence(
    InputClosure Closure, long ReadRows, long ValidRows, long UnknownRows,
    long MissingRows, long UnmeasuredRows, long InvalidRows,
    long NotApplicableRows, long ExcludedRows, long DuplicateRows);
public sealed record DenominatorEvidence(
    string ObservationUnitKind, string Unit,
    long? Expected, long KnownUnits, long UnknownUnits,
    long? NumeratorCount, long? OpportunityCount, double? Exposure,
    DefinitionReference Policy, string MemberReference);
public sealed record SubgroupEvidence(
    DefinitionReference Policy, string GroupKey, long Count,
    bool Complete, bool Qualified, string MemberReference);
public sealed record ControlChartPoint(
    string PointId, string GroupKey, string ChartComponent,
    DateTimeOffset ObservedAtUtc, double? Value,
    double? Center, double? Lower, double? Upper,
    long? OpportunityCount, double? Exposure, bool BreakBefore,
    MetricApplicability Applicability, string MemberReference);
public sealed record ControlSignal(
    DefinitionReference Rule, DefinitionReference Baseline,
    string Direction, double Threshold,
    ImmutableArray<string> PointIds, ImmutableArray<double> ComparedValues);
public sealed record ControlSignalEvidence(ImmutableArray<ControlSignal> Hits);
public sealed record BaselineCandidate(
    DefinitionReference Identity, string SegmentKey, string StratumKey,
    EstimatorKind Chart, double Center, double? WithinSigma,
    double? RangeOrDeviationCenter, long? FixedOpportunityCount,
    double? FixedExposure, DefinitionReference Constants,
    DefinitionReference Method, InputReference Input,
    DefinitionReference Subgroup, QualificationState Qualification);
public sealed record Diagnostic(
    string Code, string MessageKey, string? MetricId,
    string? ObservationId, ImmutableArray<string> Arguments);
public sealed record Provenance(
    string CoreApiVersion, string ImplementationVersion, string Backend,
    InputReference Input, DefinitionReference Definition,
    ImmutableArray<DefinitionReference> Methods,
    ImmutableArray<DefinitionReference> Baselines,
    ImmutableArray<DefinitionReference> Specifications,
    ImmutableArray<DefinitionReference> Rules,
    DefinitionReference Subgroup, NumericPolicy Numeric,
    string OrderPolicy, string MergePolicy,
    ImmutableArray<DefinitionReference> QualificationReferences);
```

`Value=null` 与数值 0 有不同语义。每个指标必须独立表达 `Computed`、`NotComputable`、`NotApplicable`、`InsufficientData`、`InvalidInput`、`Blocked`、`Overflow` 或 `Unknown`；某指标不适用不能清空同一输入中其它可计算指标。同步 StatisticsResult 在局部资源释放后直接返回，异步结果仅在 StatisticsRun.Completion 后作为最终结果交付；排空前通知只是暂存结果，不是 operation 终态。统计结果不是质量事实、机判、放行或设备命令。

每个 Method 输出一个或多个带固定 Component 的 MetricResult：Moments 为 `count/mean/m2/sample-variance/sample-deviation/population-variance/min/max`，UnitRate 为 `satisfied-rate/not-satisfied-rate`，EventRate 为 `event-rate`，能力为 `cp/cpu/cpl/cpk/pp/ppu/ppl/ppk/ca-signed/ca-abs`；缺失或不适用组件仍带 Applicability，不填零。图表组件为 `individuals/mr/xbar/r/s/p/np/c/u`，ChartPoint 保存未舍入数值与逐点限值；显示端不得重新拟合。MetricId＋Component＋SegmentKey＋StratumKey 在结果中唯一，段/层分开输出，禁止先平均各层能力指数。Evidence 只保存有界必要锚点/失败引用，完整成员沿固定输入和 MemberReference 重取；不得为百万行均值复制百万条引用。所有结果/图点/信号/诊断均扣减 MaxBufferedBytes；超过 MaxChartPoints/MaxSignals 时明确预算失败，不丢信号后返回 Complete。统计对象身份由请求 OperationId 与输入/方法修订的确定性关系形成，Core 不声明其已持久提交。

count 的 Value 只用于可精确表示范围内的数值投影，原 Int64 计数在 Denominator/Completeness/Subgroup 证据；不能先将巨大计数窄化double再求率。mean/deviation/min/max 与输入单位相同，M2/variance 为 `(<输入单位>)^2` 的机器单位表达，UI可本地化显示；能力/Ca/UnitRate 为 `1`，event-rate/u 为 `count/(<ExposureUnit>)`，p为`1`，np/c为`count`，R/S/MR和Xbar/I与原单位相同。单位定义/hash仍沿 Definition，不以用户显示标签计算转换。

Phase I 的 BaselineCandidate.Qualification 永远为 Exploratory，即使原采样资格Approved也不代表新限值获批；候选只返回计算已得到的每层中心/变异、来源与方法，不能用于后续FrozenMonitoring，除非宿主基线Owner用原审批事实创建带批准范围的FrozenBaseline。ControlSignal中候选信号绑定该Candidate.Identity，Provenance.Baselines区分其候选性质；Phase II绑定输入FrozenBaseline.Identity。数值不适用时不创建一个零值候选。Result.State=Complete只表示请求所声明固定范围完整读取/计算，不表示ProductionClosed、方法全部可计算或质量合格；Partial含范围未完整或已批准子集限制，LiveProjection独立标识实时输入。Cancelled/TimedOut/Failed保留实际已计算子集，全部指标均不得被消费者标作全范围完整值。

## 4. 同步/异步入口和事件顺序

### 4.1 入口语义

- **同步纯计算**：`Compute(StatisticsInput, StatisticsRequest, CancellationToken)` 只接收已经冻结、内存可遍历的输入闭包；不打开数据库、不拥有外部租约。按当前线程执行，局部托管缓冲在返回前释放；不伪造跨进程 operation 登记、异步通知或 native 排空。成功/部分/非法输入返回相应 StatisticsResult；取消、截止或计算失败返回对应状态和诊断，不把算法错误包装为产品 NG。
- **异步有界执行**：`ComputeAsync(IStatisticsInputSource, StatisticsRequest, CancellationToken)` 通过适配器分块读取，支持进度、取消、超时和排空。读取端口、核心计算和输出交接均有独立预算。
- **持续监测**：`StartMonitorAsync(IStatisticsWindowSource, StatisticsMonitorRequest, CancellationToken)` 创建独立监测实例；窗口、累加器和方法不得与其它实例共享可变状态。宿主显式调用 `StopAsync(StopMode.Drain|StopMode.Cancel, token)`，关闭页面只解除订阅。Drain 停止接纳新窗口并完成已接纳窗口；Cancel 同时请求在途窗口取消。两者均先记录停止意图，再查询 GetStatusAsync/DrainAsync；Completion 只在全部窗口/数据枚举器已释放后完成。数据源不遵守取消时继续 Draining/Unknown，不返池。

### 4.2 事件顺序

以下仅适用于异步 operation/monitor，不套用到无外部资源的同步调用。事件 Kind 的有限键由附录 A 冻结，产品事件映射另由 Contract Owner 采纳。请求可处于 Accepted/Running；只有产生待定结束结果或请求停止时才进入 Draining，不能用 `DrainState!=Drained` 推导正在运行的任务已经在排空。

1. `Accepted`：请求、方法/参数修订、范围、用途和预算已校验。
2. `InputBound`：输入快照/实时视图、来源边界、查询回执和水位已绑定。
3. `ReadingStarted` → 零或多次 `ChunkRead`：每块报告条数、组数、累计字节和读回执，不发布部分最终分母。
4. `InputCompletenessEvaluated`：固定输入完整/不完整、缺口、封口证据分别表达。
5. `GroupingCompleted`：去重、分层、子组、断点和排除原因完成。
6. `MetricsComputed`：每个指标分别报告适用性、值、诊断和信号。
7. `SnapshotSealed`：统计修订、输入关系、范围、方法和完整性闭合；仅固定且满足政策的结果可标 `Complete`。若请求已被 `Accepted`，此时只确定 `PendingOutcome` 并进入 `Draining`，不能直接写 `Completed`。
8. `OutputReturned`：将暂存结果或输出引用交给内部交接链；它不是 operation 完成，也不改变 `OperationState=Draining`。`StatisticsRun.Completion` 不得在排空前完成。
9. `DrainObserved`：报告本次排空观察的 `DrainState`、排空代次、剩余操作/资源摘要和观察时间。`TimedOut`/`Unknown` 只产生此类观察；已接收 operation 保持 `OperationState=Draining`，不得提前发 `Completed`/`Cancelled`/`TimedOut`/`Failed`/`Unknown` 终态。
10. `DrainCompleted`：且仅在 `DrainState == Drained`、所有租约/在途调用/缓冲/任务/原生资源均已确认释放时产生；事件中的 `IsTerminal=true`、`CanReuseResources=true`，随后 operation 才能按 `PendingOutcome` 写入唯一终态。同一 `OperationId` 与 `DrainAttemptId` 只允许产生一次。

事件必须单调带 OperationId 和序号；排空观察还带 DrainAttemptId。Kind 为 DrainObserved/DrainCompleted 时 Drain 不为空，其它事件为 null。DrainCompleted 的 Drain.State=Drained、IsTerminal=true、CanReuseResources=true 描述的是资源排空终结；业务 Status 仍在 Draining，随后写唯一终态再完成 Completion。TimedOut/Unknown 观察的两布尔为 false，未知数量用 null。DrainAttemptId 仅标识观察代次，最终资源完成按 OperationId 去重，不能每次重查发一个新完成。OutputReturned/停止通知不证明资源已释放。通知不是业务事实队列；无订阅/慢订阅时运行不等待消费者读完通知，§6.1 定义有界通知降载，终态可从 Completion/QueryOperationAsync 取得。

## 5. 状态、错误码和恢复

### 5.1 状态

OperationState 描述异步已接纳操作的生命周期，ResultState 描述输入/统计结果，两者不同。Accepted/Running 的 PendingOutcome=None、DrainState=NotStarted、IsTerminal=false、CanReuseResources=false；结束意图后才 Draining（PendingOutcome 非 None）→确认 Drained/DrainCompleted→Completed/Cancelled/TimedOut/Failed/Unknown。接纳前非法请求返回 ResultState=Invalid/Blocked，异步入口抛 StatisticsRequestRejectedException（Code 为本页稳定错误键），不分配后台 run，不发 Accepted。接纳后的每指标 InvalidInput 不把 operation 改成 Rejected；可成功完成一份包含不可计算指标的结果。单纯构造 OperationId 不算接纳。

| 状态 | 含义 | 允许行为 |
|---|---|---|
| `Ready` | 请求已绑定且前置能力满足 | 可开始执行 |
| `Running` | 正在读取/分组/计算 | 仅消费本任务资源 |
| `Draining` | 已接收 operation 正在停止接纳并等待所有在途工作、租约和资源归还；`PendingOutcome` 保存预期结果 | 只能观察、隔离和重查；`IsTerminal=false`，不得发布任何 operation 终态 |
| `Completed` | 结果与证据闭合且 `DrainState=Drained` | 唯一终态；结果不可变，资源可复用 |
| `Blocked` | 缺权限、范围、字段、方法或批准政策，尚未接收为 operation | 返回原因，不产生生产副作用 |
| `Cancelled` | 取消结果已确定且此前已确认 `DrainState=Drained` | 唯一终态；不得再有在途资源 |
| `TimedOut` | 截止结果已确定且此前已确认 `DrainState=Drained` | 唯一终态；不得把排空截止本身当作完成 |
| `Failed` | 失败结果已确定且此前已确认 `DrainState=Drained` | 唯一终态或按原规则建立新 operation；不得复用未知资源 |
| `Unknown` | 结果/提交未知，但只有在资源已确认释放后才可作为 operation 终态 | 否则保持 `Draining`，查询原 operation 和排空观察 |
| `Rejected`/`Invalid` | 在 operation 接收前拒绝输入或版本 | 可直接返回，不产生已接收 operation 的终态事件 |

### 5.2 错误码语义

错误码是稳定语义类别，正式数值/序列化由 Contract Owner 冻结：

| 代码 | 触发 | 调用方动作 |
|---|---|---|
| `STAT.INPUT_INCOMPLETE` | 固定范围尚未完整读取 | 补齐同一快照或返回部分结果；不改分母。 |
| `STAT.SCOPE_MISMATCH` | 输入、范围、单位、代次或来源不相容 | 重新绑定经批准的输入；不得转换掩盖。 |
| `STAT.DENOMINATOR_UNKNOWN` | 分母/机会量未定义或为零 | 保留缺口，等待 Owner；不返回 0%/100%。 |
| `STAT.GROUP_INVALID` | 子组不完整、跨断点或不满足方法 | 只阻断受影响指标；保留样本和原因。 |
| `STAT.METHOD_UNSUPPORTED` | 方法/后端不覆盖输入域 | 返回不支持；不得静默换估计量。 |
| `STAT.NONFINITE_VALUE` | NaN、Infinity 或非法 M2/计数 | 拒绝受影响指标并定位观察。 |
| `STAT.NUMERIC_OVERFLOW` | checked 计数、矩或预算溢出 | 停止相关计算，不能截断后宣称完整。 |
| `STAT.BUDGET_EXCEEDED` | 行、组、字节、时间或输出预算超限 | 返回预算诊断；宿主决定新请求。 |
| `STAT.CANCELLED` | 取消已接收；operation 进入 `Draining`，尚未形成终态 | 返回取消观察；确认 `Drained` 后才发布 `DrainCompleted` 并写入 `Cancelled` 终态，资源未确认前不得返池/复用。 |
| `STAT.TIMEOUT` | 到达截止；operation 进入 `Draining`，实际完成或资源释放未知 | 查询原操作和排空观察；确认 `Drained` 后才写入 `TimedOut` 终态，不得并发盲重算、返池或把超时当 `DrainCompleted`。 |
| `STAT.RECEIPT_UNKNOWN` | 持久交接回执未知 | 沿原 `OperationId` 查询；不生成新成功。 |
| `STAT.VERSION_INCOMPATIBLE` | 方法、输入或序列化版本不兼容 | 选择明确兼容适配器或阻断。 |
| `STAT.IDENTITY_CONFLICT` | 同 observation/operation 身份对应不同内容或修订 | 保留原内容和冲突诊断，不覆盖、不并发重放。 |
| `STAT.ORDER_INVALID` | 顺序倒退、跨段组或真实邻接证据不足 | 停止受影响时间/子组方法，原输入不重排为伪顺序。 |
| `STAT.SOURCE_STALE` | 固定输入/租约/修订在读取中失效 | 保留已读范围与原因，不能重连后换 latest 续算。 |
| `STAT.PORT_FAILURE` | 数据源/窗口/回执端口抛出异常 | 异步先排空，保留原操作；诊断含稳定键，不向操作员裸传堆栈。 |
| `STAT.OBSERVER_FAILURE` | 可选进度回调抛异常 | 解绑该回调并保留诊断；不改变统计值或抢先释放运行资源。 |

错误不得把源产品 `NG` 映射为模块错误；源事实、统计适用性、执行状态和持久回执保持正交。

## 6. 取消、超时、资源、线程和排空

- 每次执行拥有独立输入闭包、累加器、当前子组、规则窗口、诊断和输出缓冲；只读方法常量可共享，不共享可变窗口。
- 核心不保证调用线程；同步入口在当前线程计算，异步入口使用宿主提供的调度器/线程池，不捕获 UI `SynchronizationContext`。UI 投影必须在宿主 UI 线程更新，重计算不得占用该线程。
- `DrainState` 是资源生命周期的独立维度，与 `OperationState`、统计结果状态和持久回执正交：`NotStarted` 表示尚未开始排空；`Draining` 表示正在等待在途工作和释放资源；`Drained` 只表示已确认全部释放；`TimedOut` 表示达到排空截止但仍有未确认资源；`Unknown` 表示无法判断是否仍有资源或调用在途。
- `TimedOut` 和 `Unknown` 都是非终态排空观察状态。它们必须进入隔离跟踪和重查队列，由明确的排空 Owner 继续观察；已接收 operation 在重查确认全部释放前必须保持 `OperationState=Draining`、`IsTerminal=false`，禁止发送任何 operation 终态、`DrainCompleted`、归还或复用可能仍在使用的资源。
- 取消请求只停止接收新分块和新工作，并将已接收 operation 转为 `Draining`，记录 `PendingOutcome=Cancelled`；取消响应返回不等于 operation 终态或排空完成。取消后等待已启动的读取/计算/输出退出并释放资源；若确认 `Drained`，才发送一次 `DrainCompleted`，随后写入 `Cancelled` 终态。若达到截止仍未确认，则只发送 `DrainObserved(TimedOut)` 或 `DrainObserved(Unknown)`，保持 `Draining` 并继续重查。
- 超时只表示请求截止，不表示底层已停止。纯计算无持久登记时，宿主必须确认旧 worker 已停止后才能同一操作恢复；有原操作/回执时先查询原状态。到达排空截止不允许强杀后宣称排空完成。
- 任何已接收的执行失败都先记录 `PendingOutcome=Failed` 并进入 `Draining`；只有确认 `Drained` 后才允许写入 `Failed` 终态。失败、取消、超时和未知回执不改变统计业务判定，只改变执行生命周期和恢复动作。
- 读取批、去重/分组批、公式批、输出块和持久交接前都必须检查取消；停止接收后仍须等待在途调用、回调、IO、适配器和原生调用返回，再逐项释放。
- §7.1.3.6 的可选 Boost Beta 原生调用由其适配器拥有；取消或失败须等待真实调用返回再归还输入缓冲与槽位，不以等待任务取消推断调用已退出。
- 每次排空观察和事件 DTO 都携带 `DrainAttemptId`、`DrainState`、`ObservedAtUtc`、可确认的剩余操作/资源摘要、`IsTerminal` 和 `CanReuseResources`；`TimedOut`/`Unknown` 的数量可为 `null`，两个布尔值必须为 `false`。只有 `Drained` 才能为 `true`。
- 重查确认全部资源释放后，将 `DrainState` 推进到 `Drained` 并发送唯一 `DrainCompleted`；随后按 `PendingOutcome` 写入唯一 operation 终态并让 `Completion` 完成。若始终无法确认，保持 `OperationState=Draining`、`DrainState=Unknown`、保留诊断和隔离记录，不伪造完成事件。
- 下游慢时暂停有界生产或返回 `STAT.BUDGET_EXCEEDED`；不建立无限 Task、无限事件队列或无上限图点缓存。

### 6.1 有界执行、幂等与回调隔离

- 固定一次计算最多一个源枚举器和一条归约流水线；同一 operation 有状态归约单写。交错的段/层各维护自身当前组、前一点/规则窗口，状态总数与未闭合组共同计入MaxGroups/MaxBufferedBytes；不使用另一层前一点。ReadBatchSize 只改变传输分块，数值归约按实际成员稳定顺序逐个更新；不因分块大小/线程完成先后改变合并树。当前 0.3 不并行乱序合并一个指标，各 operation 可独立并行，宿主在调用前限制同时接纳数。
- 批次所有权：源拥有 ReadBatchesAsync 返回的只读批直到下一次 MoveNextAsync；Core 必须在推进源前校验条数并复制必要字段至自有有界缓冲，不能保留源池数组。源枚举器由 Core 在成功/失败/取消路径 DisposeAsync；source 对象由调用方拥有并在排空后处置。回执源和定义均只读借用。释放有异常或结果未知时保持 Draining，不伪造计数0。
- GetReferenceAsync返回请求绑定的不可变引用（含初始ReadComplete承诺），不以该对象表示本轮读取进度；变化的读取完成状态在GetClosureAsync。固定模式下Input与Provenance仍保留该引用，最终完整性以Closure/实际成员核验为准，不能单看Input.ReadComplete一个bool。回调投递也不借用原源批；宿主若用`Progress<T>`自动向UI队列Post，必须在其外提供有界/可解绑观察者，不能以Report立刻返回声称UI队列已有限。
- 读取前取Reference与初始Closure的预计成员/已知缺口，结束后再次取Reference/Closure。最终Closure发现新增未知位置缺口时，已累计描述值可保留，不能封闭跨缺口MR/规则；有CanReplay时用同一固定输入/最终缺口重新评价，没有可重读保证则该方法NotComputable，已暂算信号不交付为有效。最终Gaps在计算结束后才得知的源不得靠不读回执声称完整。源抛异常且释放仍可确认时返回Failed/Partial诊断；释放抛异常又无释放证明时继续Draining/Unknown，两种失败分开。
- 如读/算解耦使用 .NET `Channel.CreateBounded`，数据通道固定 `BoundedChannelFullMode.Wait`、SingleWriter/SingleReader=true、AllowSynchronousContinuations=false；条数/字节都先预留，写取消不等于已读批释放。数据/图点/信号不能采用 DropOldest/DropWrite；不解耦时顺序 await 即提供背压。排队耗时计入 WallClockLimit，deadline 用单调时间，UTC只供关联。
- Notifications 是可合并的观察通道，单消费者，不作为完整审计/信号传送。Kind 仅允许 §4 列出的十个键及 `WindowCompleted`；每项 Status/Progress/Drain/Result 字段按 Kind 验证。进度相同 Phase 保留最后值；慢/无消费者时最多 MaxNotifications，先合并进度、再丢旧非终态观察，并递增 DroppedNotifications，不阻止资源完成。最终状态写入查询登记和 Completion 后结束通知流；资源终态不能靠收到某条通知来推断。全部统计信号在最终 Result，绝不随通知降载删除。
- `IProgress` 是可选观察者，单序列、不并发回调，抛异常记录 `STAT.OBSERVER_FAILURE` 后解绑该观察者，计算/排空继续。禁止在计算锁内调用宿主代码；回调不得重入改变 Core 状态。宿主提供的 Progress 应只做有界投递，阻塞的同步回调没有可强杀保证，测试注入阻塞时仍记录在途并等其退出；不得把额外 Task 超时当回调已结束。
- 同一 engine 内 OperationId 原子登记：同 ID 且输入引用/方法/参数闭包完全相同返回原 run/已封存结果；同 ID 异闭包拒绝 IDENTITY_CONFLICT。取消一个等待 Completion/查询的 token 只取消等待，不取消原 run；原执行仅响应接纳时 token 或显式 run.CancelAsync。同步 Compute 无永久登记，同输入仍须语义一致。
- 闭包相等按全部字段逐项结构比较：字符串Ordinal、double原位模式、nullable有无、ImmutableArray元素顺序与递归值，不使用数组引用相等、当前文化/显示舍入或仅一个客户hash。运行登记与生成结果无全局静态字典。读取MemberSequenceHash用于证明实际顺序：按观察声明顺序写字段，字符串UTF8字节长度前缀Int32 little-endian（null另写0存在标记，非null写1及长度），bool/枚举为受检字节/Int32，Int64/UTC ticks/double原位模式little-endian，nullable先0/1再值；使用增量SHA-256。它是本次读取的派生序列证据，不冒充源ContentHash或客户签名；每遍核相同序列hash，源Reference/Closure另外核对。超长字段先扣预算，不为hash暂存全文件。
- run.DisposeAsync 是“发 Cancel 请求并等待真实完成”的便利入口；不得拿 Dispose 已调用当排空证明。engine.DrainAsync 停止接纳所有新任务并逐项等待，Cancel 单个 run 不停止其它 run；engine.DisposeAsync 在任务/回调未归还时不提前返回。查询 tombstone/完整结果受实例 MaxOperations/MaxRetainedResults 约束，容量满接纳前拒绝；调用方显式 ForgetOperationAsync 只能移除已终态且排空的记录，未终态不可遗忘。未持久化记录被遗忘后查询 NotFound，并明确仅指当前实例。
- MaxRetainedResults的一个结果槽位在接纳时预留，完成时不再因槽位不足丢结果；重放共享原槽位。CancelAsync/StopAsync 的token只取消本次请求投递前的等待，成功投递后停止意图不能撤回；重复停止幂等，Drain可升级Cancel但不能反向。StopMode.Drain取消新窗口枚举的等待不算监测业务取消，完成已接纳窗后PendingOutcome=Completed；源异常或已接纳窗失败保留诊断并最终Failed。主动Cancel最终Cancelled。排空/timeout/失败竞态按首次锁定结束意图为准，后续资源诊断追加不改已封存结果。


### 6.2 装配与派生身份补充（2026-10-12，沿用已接收语义）

本节只闭合既有 Core 装配/对象身份的实施细节，不改变 S1–S4/S6/S7 的公式、有效域、字段和旧 Golden。Core 0.3 默认单条顺序 await 读取/归约，不创建读算分离 Channel 或独立 IStatisticsScheduler；§6.1 的 Channel 规则只在后续明确采用该优化时适用。本版异步已接纳任务使用 BCL Task.Run 启动各自流水线，内部 await 不捕获 SynchronizationContext，所有并发由实例 EngineLimits、请求字节预算及宿主接纳限额约束，不修改 ThreadPool 全局设置。同步在调用线程完成。§6“宿主提供的调度器/线程池”不表示未定义的注入端口；本版不存在隐藏调度器服务定位。

SPC 固定输入源按 §3.2.1 的时间/序号/身份顺序交付，Core 检查去重后的顺序，不全量缓存重排流、也不以字符串兜底证明真实邻接。§7 的“单位转换”指核验上游已经完成的具名转换与新输入，不在 Core 变换量值；§7.1 的“固定树合并”对本版为固定成员顺序的左折叠，分块不改变运算顺序，不启用并行合并。Moments/分母、组、限值和规则继续按 §7.1.1/058A；排序/单位显示不能改变其实际顺序或身份。

**本地字段编码。** 模块 CLR 输入/输出不是平台 JSON/数据库 Schema。Core 的派生内容身份使用下述白名单 codec，命名为 stats-core-field-v1：String 为严格 UTF8、不做Unicode正规化，Int32 little-endian字节长度后写字节；null String先byte0，非null先byte1再String；Int32/枚举、Int64、binary64原位模式均little-endian；bool为byte0/1；任意nullable值/引用先byte0/1；TimeSpan写Int64 ticks，DateTimeOffset受检Offset=0后写UTC ticks；数组写受检Int32 Count，再原序逐元素。Record按本指导公开声明字段顺序递归一次写全（继承的TaskId/Coverage/Diagnostics已在具体声明中出现，只写一次）；不写CLR类型名、属性名或文化格式。唯一多态位置 NumericalTask/Result先写本指导明确支持的具体tag String再写具体字段，不反射枚举插件/任意record。Guid/decimal/JSON/原生对象不在本codec。定义引用含Id/Revision/ContentHash全三项；来源引用含全部字段；nullable、空串、空数组、±0原位模式不得合并。默认数组/未知枚举/超预算在写入前拒绝。定义正文的 ContentHash 属原定义 Owner；Core 不凭引用重建外部正文或重新给源资料签名。

SHA-256域使用ASCII域名+一次byte0在流开头，生产增量编码/hash并计字节/暂存预算；不先拼接完整巨型byte[]。新增本地派生域：
- SPC-REQUEST-IDENTITY-V1：完整 StatisticsRequest 按 §3 声明顺序写全，用于 Core 内部可复算身份；实际幂等仍按 §6.1 完整结构比较，hash不能取代相等检查。输入闭包/观察数组另核，不把此 hash写回源 Input.ContentHash。
- NUMERICAL-REQUEST-IDENTITY-V1：仅 S4 的完整 NumericalRequest 按 §7.1.3 声明顺序递归写全，Task多态tag在每项前；S6/S7继续用其已经冻结的 REQUEST域，不插入本域或改变旧字节。Core 必须按明确family分派。
- SPC-SNAPSHOT-IDENTITY-V1 / NUMERICAL-SNAPSHOT-IDENTITY-V1：ApiVersion(String)、实际ImplementationVersion(String)、SPC后端String/数值Backends数组（完整BackendIdentity）、OperationId(String)、完整请求hash(String)、最终InputClosure、实际MemberSequenceHash(String)、最终ResultState(Int32)；生成StatisticsSnapshotId="statistics:"+小写hex SHA-256。只有输入和资源闭合后生成最终身份；OutputReturned暂存投影不冒终态快照。结果含缺口/失败仍记录其实际最终Closure/范围；无最终Closure时只沿请求/最后已核Closure保留Failed或Unknown，不编封口。
- SPC-SUBSET-IDENTITY-V1：SourceBoundary(String)、完整InputReference、MetricId/Component/SegmentKey/StratumKey各String、成员串（每成员byte1+完整ObservationReference+原MemberReference，按源实际顺序）后写byte0+Count(Int64)；完整GroupKey作为最后一个nullable String写入，非组子集为null。这是派生子集证据，ComputedSubsetReference="statistics-subset:"+hex；不是第二查询Store。这个新增域支持单遍增量hash，Count在结尾，不为前缀数量缓存成员。Core只保留哈希与层/组/范围，宿主用原固定输入/层/组重取成员再核hash，不从hash反推成员、不复制百万引用。
- SPC-POINT-IDENTITY-V1：MetricId/Component/SegmentKey/StratumKey/GroupKey各String、ObservedAtUtc ticks、MemberReference(String)，PointId="statistics-point:"+hex；相同组件同原成员点跨显示筛选/语言/分块稳定，层/组不混用。个体点原MemberReference直接沿源；子组点采用上述subset域（Component固定图组件，另含实际GroupKey作为最后一个String），同组重开按原GROUP_INVALID拒绝。
- SPC-BASELINE-CANDIDATE-V1：BaselineCandidate除自身Identity之外的全字段，含原Input/Method/Subgroup/Constants和Qualification=Exploratory。Identity.Id="statistics-baseline-candidate:"+hex、Revision="1"、ContentHash=该hash；仍须外部Baseline Owner批准后另造FrozenBaseline，不原地改Candidate身份。
- S4-NUMERICAL-MEMBER-SEQUENCE-V1：任务Count(Int32)，按请求Task顺序写tag/TaskId和实际参与成员Count(Int64)，再源原序写每个完整NumericalMember；Pair写该Member及两侧引用/State，Kappa明细同理；Design用Members原序，GroupMoments/Contrast用Rows的Member原序；无行的Covariance/Distribution/κ汇总写0并写完整任务hash（域S4-NUMERICAL-TASK-IDENTITY-V1+tag+完整具体Task声明字段，不重复TaskId）。该数值序列证据不代替完整Task身份/覆盖；S6组顺序/S7精确PairSequenceHash及外层既有语义保持，不把两个hash强制相等。

本补充身份域没有替代外部源hash/QLNI/QLMS/产品快照，旧包生成的旧结果不重算ID。实际新包SemVer/BuildHash和codec能力在实施发布时绑定；不据仍为0.3声明与旧未核包二进制兼容。消费者需要签名/存储/导出时由原Owner把本地完整值映射到自己的Schema，不让Core增加通用序列化或事实提交端口。


## 7. 统计方法边界

SPC 公式唯一见 DEV-DOM-058A；扩展数值公式/步骤以本页 §7.1.3 为唯一实施正文。SPC 接入顺序如下：

1. 固定 `MetricDefinition`、观察单位、范围、单位、尝试政策、规格、子组/缺口、基线和方法修订。
2. 验证输入快照/回执关系和完整读取；水位只能说明读取进度，不能证明封口。
3. 依既定顺序执行身份去重、分层、单位转换和子组；同单位不代表同被测量，混批/混规格拒绝混合。
4. 先输出有效/预期/缺口/排除/Unknown 计数，再计算各指标。
5. 过程能力区分 within/overall；缺少合法 sigma、规格端点、样本或资格时不可计算。均值超规格时允许负 Cpk/Ppk；sigma=0 不返回无穷或任意大数。
6. 控制图基线与本次受检点分开。缺口清空连续规则窗口；显示抽稀不得删除已计算的信号。
7. 迟到/更正/重复输入形成新快照或新计算意图；不回写旧统计，不把重测改善首检分母。

比例或率只在观察单位、计数/暴露量、单位、来源边界和方法政策均相容时合并：先合并原始分子与分母，再做一次除法，不能平均各层百分比。例如 `1/1` 与 `0/99` 的合并结果是 `1/100=1%`，不是 `50%`。任一层的分母或机会量未知时不得生成合并率；不相容层继续分层并保留各自证据。该规则与 [`DEV-DOM-058A`](../../shared-modules/guidance/06-domains/DEV-DOM-058A_QualityControl%20SPC与分母定义开发指导.md) 的分母定义一致，具体公式仍以该指导为准。

合理子组必须消费预先批准的观察顺序、时间/采样窗口、组键和组宽定义。不得按 PASS/NG、报警命中、复判结果或已观测数值事后重组以稳定图形；同一物理目标的重复测量表示重复性，不自动视为独立过程波动。子组资格、断点和缺口由其 Owner 提供，缺失或不满足时只阻断受影响的 within/控制图方法，不改写原始观察。

对 Phase II 控制图，中心参数、限值方法和规则版本绑定冻结的 baseline 修订；p/u 中心按批准 baseline 的合并计数/暴露量确定，或绑定方法允许的已批准目标及来源。每点限值使用冻结中心和该点实际批准的正分母/暴露量计算，这不属于在线重估中心。np/c 仅在可比且恒定的单位数/暴露量下适用，不得因 n 或暴露量变化静默切换方法。在线极端值、后续点或告警命中不能改写当前 baseline；精确公式和常数仍集中在 [`DEV-DOM-058A §6`](../../shared-modules/guidance/06-domains/DEV-DOM-058A_QualityControl%20SPC与分母定义开发指导.md#spc-control-charts) 和 [§7](../../shared-modules/guidance/06-domains/DEV-DOM-058A_QualityControl%20SPC与分母定义开发指导.md#spc-baseline-alarms)。

每个信号保留规则修订、方向和阈值、参与观察的 ID/窗口、baseline 修订及比较值；无信号不证明过程稳定或具备能力。告警确认、关闭、抑制和调查动作仍由外部 Owner 负责，Statistics 只返回可追溯的 `ControlSignalEvidence`。

当前不覆盖：复杂置信区间、非正态能力、稳健能力、加权/多层/时间块聚类、重复测量推断、多重比较、等效/非劣、一致性限、因果推断和自动模型选择。请求这些能力必须返回 `STAT.METHOD_UNSUPPORTED` 或由独立方法修订扩展，不可用近似静默替代。唯一新增的组级推断是 §7.1.3.9 的等概率独立组 percentile bootstrap；它不改变 SPC、计量或产品资格语义。`DEV-TST-003 §§4–10` 对照后，以下通用方法门槛作为本模块的可复用边界：统计单位/分母、缺失与 Unknown、聚类/过度离散、置信区间和跨来源分层必须满足下节定义；AOI 的缺陷召回、误报负担、人工复判或放行指标仍不属于本模块。

### 7.1 固定算法路线和恢复条件

| 路线 | 适用输入/触发条件 | 处理顺序 | 输出/拒绝 | 恢复条件 |
|---|---|---|---|---|
| 主路线：确定性流式累计 | 已通过身份/单位/有限性检查的固定或有序实时数值；方法要求均值、M2、计数、子组或控制图 | 固定排序键→去重/分层→按批准顺序 Welford 累计→固定树合并→子组/基线→指标与规则→封闭快照 | 返回充分统计、成员证明、数值诊断和方法适用性；同一输入、顺序、合并树须语义一致 | 固定快照仍可读、方法/数值策略/范围未变且旧 worker 已明确停止时，从同一快照重算；本版本不假设可安全减样本。 |
| 不支持路线：鲁棒/训练/自动选模 | 噪声、离群、遮挡、退化、混合分布或需要训练/自动选模的请求 | 不执行中值替换、winsorize、自动剔除、稳健 sigma、聚类、模型训练或自动选择 | `STAT.METHOD_UNSUPPORTED` 或受影响指标 `NotComputable`，保留原始观察及原因；不能以“清洗后更稳定”生成生产值 | 只有新批准的 `MethodRevision`、输入资格、训练/评价证据和回放基线全部存在时，才作为新能力接入；本模块当前无训练入口。 |

固定路线的确定性要求不等于逐位跨平台相同；跨运行时比较使用批准的绝对/相对容差。SPC 后端为 `managed-binary64-welford-v1`，矩阵后端为 §7.1.3.3 的 `managed-mathnet-isolated-v1`，条件 t/F 通过 §7.1.3.6 的 `boost-beta-tail-v1` 执行；本版无备用路线或自动后端切换。

### 7.1.1 可直接实施的有限方法集合

Core 0.3 的 SPC 主后端固定 `managed-binary64-welford-v1`，计数 checked Int64。Moments、UnitRate、EventRate、Capability、Xbar-R/S、I-MR、p/np/c/u 全部保留在模块范围，按 058A §2–7 唯一公式执行，不以首片缩小替代模块设计。数值累计先校有限性→按稳定成员序更新 n/mean/M2/min/max→各段/层独立计算→图点→有限规则。没有方法 ID 就拒绝，不根据直方图自动选图。

Phase 仅约束图种；Moments/比例/率/Capability 使用本次声明固定范围，不能把基线 sigma 偷换为当期 within/overall。图种 Phase=EstimateCandidate 对同一可重读固定输入两遍：CanReplay=true 或同步内存输入才允许；第一遍建描述/子组累计及候选中心/变异，第二遍重新ReadBatchesAsync前后核同Reference、最终Closure的成员/缺口/封口证据及MemberSequenceHash，ReadComplete的初始false到读取结束true不当成版本变化。两次枚举不重叠、旧枚举器先释放；不可重读源返回METHOD_UNSUPPORTED，不缓存无界全量。全部为工程候选，不能自行构造Approved基线。Phase=FrozenMonitoring从请求FrozenBaseline取中心/变异/常数，单遍产生点；p/u用实际n/o，np/c校恒定条件。每条规则按058A §7的适用图种/严格比较/窗口处理，等于界限不触发BeyondLimits，等于中心线打断EightSameSide；R/S/MR和计数图不默认套正态区规则。变异图先于均值图解释，sigma=0或无合法邻接对保持不适用而非零宽稳定。候选重算不获质量批准。

组完整性不从读取批边界推断：各段/层携带未闭合当前组至下一批，组成员、FixedSize、MaximumSpan 与段/层核验完成后才产生一点；同层已闭合GroupKey又出现不同成员返回GROUP_INVALID，不重开并重复算一点。跨层可交错，各自顺序仍需稳定；末尾不完整组保留缺口，不缩 n。I-MR 缺测/Unknown/Invalid/排除/未批准时间间隔清邻接，断点首点的 MR=null；样例 `[1, Missing, 4]` 有两个可描述值但无 MR，不得到3。一次请求的有界去重集合计入字节预算，不能以 Bloom filter 误判真实成员已见；超过规模拒绝，外部排序/磁盘 spill 必须由后续公开适配端口设计后才能采用。

Ca、单侧能力和负 Cpk 按 058A §5；无规格不阻断 Moments。非法矩/计数不得 abs/加 epsilon/clip 修补。最低样本、适用性与容差均使用已绑定方法，弱散布/近常量先按实际有限值计算，零 sigma 明确无能力值；不因“噪声大/结果不好”清洗或拟合。

### 7.1.2 时间窗口、持续运行及迟到

监测不消费设备 event 或 durable Inbox；`IStatisticsWindowSource` 是宿主提供的已冻结窗口输入序列，Core 只校验并调度同一 ComputeAsync。模板规定 OriginUtc/Width/Step：Tumbling 必须 Step=Width；SlidingRebuild 为 0<Step≤Width，每窗独立 `[Origin+k·Step, Origin+k·Step+Width)`，整数 k 与日期加法检查溢出。相邻 Tumbling 边界点只属后一窗，Sliding 允许同一观察在不同明确窗口各一次，不能把各窗相加为总体。窗口不是 UI 可见时间范围。

WindowSequence 单调，WindowInput.Request.Scope.TimeRangeUtc 必须匹配该窗，且数据模式固定 FixedSnapshot；在线源未能给固定引用时只能发独立 LiveProjection 请求，不伪称正式封窗。迟到/更正由宿主创建同窗新 SnapshotRevision、新 OperationId，完整重算后并列修订；没有减样本/反向 Welford/自动 checkpoint 恢复。旧窗口结果不可修改；旧 worker 在途时相同窗新修订按 MaxConcurrentWindows 排队，不能交换源引用。Definition/Methods/规格/基线参数改变须停止旧 monitor，完成排空后以新 MonitorId/Template 启动，不在旧窗口中混修订。

MaxConcurrentWindows/MaxRetainedWindows≥1，必须显式提供并受 EngineLimits 和 MaxBufferedBytes 共同限制；每窗有独立预算/操作状态/结果。完成后通知 WindowCompleted 携带已排空 Result；慢显示仅通知降载，宿主按窗口 OperationId 查询终态。保留窗口满时停止接纳并报告预算原因，不无限积累历史；宿主持久保存/消费后可 ForgetOperationAsync 已完成窗口。源断连/枚举异常标 PORT_FAILURE 或 SOURCE_STALE，停止新窗、在途排空，保留已完成修订；重连从宿主已证明的窗口序列开始，新 monitor 不猜 latest 或跳过未完成窗。源枚举器关闭与任务关闭分别等待，不由页面关闭触发。

### 7.1.3 数值能力的唯一实施规格（S4/S6/S7 数值部分）

<a id="qualification-numerical-operations"></a>
#### 7.1.3.1 权威、消费者与公开请求

本节接收原 PKG-045 §§7.5–7.7/§8 的数值实施责任：分组矩、声明对比/平方和、仿射和一般设计、QR/SVD、条件 t/F、协方差传播、Pearson/Spearman、配对差及无权重 Cohen κ 均保留，数值实现只按本页。DEV-MET-033 保留实验格、交叉/嵌套 GR&R 模型组合、自由度解释、负方差分量政策、物理独立性、资格和客户判据；PKG-055 组装资格报告。Statistics 不自行从实验数据选模型、删交互、截负分量或签发 MSA。具名配对来源由跨工序关联 Owner 冻结，Core 不执行目标匹配或仲裁。PKG-045 现为 IM-043 应用映射，数值消费者直接引用本指导；本轮不改共享文件。

真实复用计划为：①033/055 的 SPI 计量与 PCB 孔槽/钢网资格消费者；②工程数据工具的有限设计/协方差计算；③SPI→AOI 连续量关联、原机判→指定复判轮分类配对。它们只传本节不可变值，不带制程实体/VM/数据库表。描述计算与推断资格分开；合法但不支持的高级请求仍返回明确结果，不删能力范围。矩阵运算和统计事务均非视觉算法，采用本节固定托管数值路线及明确的 Beta 端口。

所有以下类型属于 Asun.Modules.Statistics。数组默认值 default 不是空数组；接纳前拒绝。请求仅处理有界冻结内存，固定输入必须为 FixedSnapshot，实际行身份/Closure 与 Input 核对；本版本不提供无界数值源/任意动态设计生成。字段单位为机器单位标识，单位变换先由量值 Owner 冻结，不能按显示标签转换。工程上界 N≤1,000,000，设计列/协方差维数≤128，类别数≤256，任务数≤64；同时受调用预算较小值限制。这些是内存/算法边界，非工业最小样本或质量门限。

~~~csharp
public sealed record NumericalRequest(
    string OperationId, InputReference Input, InputClosure Closure,
    DefinitionReference Method, DefinitionReference SelectionPolicy,
    DefinitionReference? ObservedSubsetApproval,
    CompletenessPolicy Completeness, NumericalPolicy Policy,
    NumericalBudget Budget, ImmutableArray<NumericalTask> Tasks);

public sealed record NumericalPolicy(
    DefinitionReference Identity, double RankAbsolute, double RankRelative,
    double DecompositionTolerance, double PsdTolerance,
    double CorrelationRoundoffTolerance, double TQuantileAbsolute,
    double TQuantileRelative, double FQuantileRelative,
    double TailRelative);

public sealed record NumericalBudget(
    int MaxRows, int MaxGroups, int MaxColumns, int MaxCategories,
    int MaxTasks, int MaxDetailRows, int MaxDiagnostics,
    int MaxIntegerBits, long MaxBufferedBytes, long MaxWorkingSetBytes,
    TimeSpan WallClockLimit, TimeSpan DrainObservationLimit,
    int MaxNotifications);

public abstract record NumericalTask(string TaskId);
public sealed record NumericalMember(
    string RowId, ObservationReference Source, ObservationState State,
    string? ReasonCode);
public sealed record NumericRow(
    NumericalMember Member, string GroupKey, double? Value);
public sealed record GroupMomentsTask(
    string TaskId, string Unit, ImmutableArray<NumericRow> Rows)
    : NumericalTask(TaskId);
public sealed record ContrastTerm(string GroupKey, double Coefficient);
public sealed record DeclaredContrast(
    string Id, ImmutableArray<ContrastTerm> Terms, double SumSquareDivisor);
public sealed record ContrastTask(
    string TaskId, string Unit, ImmutableArray<NumericRow> Rows,
    ImmutableArray<DeclaredContrast> Contrasts) : NumericalTask(TaskId);

public enum DesignColumnRole { Intercept, Continuous, Indicator }
public sealed record DesignColumn(string Id, string Unit, DesignColumnRole Role);
public sealed record DesignTask(
    string TaskId, DefinitionReference Model, string ResponseUnit,
    ImmutableArray<NumericalMember> Members, ImmutableArray<DesignColumn> Columns,
    ImmutableArray<double> RowMajorDesign, ImmutableArray<double> Response,
    bool RequireResidualVariance, bool ReturnDetails) : NumericalTask(TaskId);
public sealed record AffineTask(
    string TaskId, string XUnit, string YUnit, double CenterX,
    ImmutableArray<PairRow> Rows, bool ReturnDetails) : NumericalTask(TaskId);
public sealed record CovarianceTask(
    string TaskId, DefinitionReference BudgetModel, string OutputUnit,
    ImmutableArray<string> ComponentIds, ImmutableArray<string> InputUnits,
    ImmutableArray<double> RowMajorCovariance,
    ImmutableArray<double> Sensitivities) : NumericalTask(TaskId);

public enum DistributionKind { StandardT, F }
public enum DistributionOperation { Tail, Quantile }
public enum TailSide { Lower, Upper }
public sealed record DistributionTask(
    string TaskId, DistributionKind Distribution, DistributionOperation Operation,
    TailSide Side, double Degrees1, double? Degrees2, double Argument)
    : NumericalTask(TaskId);

public enum PairStatistic { Pearson, Spearman, Difference }
public enum InferenceKind { None, PearsonZeroT, PairedMeanT }
public enum Alternative { TwoSided, Less, Greater }
public sealed record PairRow(
    NumericalMember Member, ObservationReference? LeftReference,
    ObservationReference? RightReference, ObservationState LeftState,
    ObservationState RightState, double? Left, double? Right, string? ClusterKey);
public sealed record ConditionalInference(
    InferenceKind Kind, DefinitionReference AssumptionEvidence,
    Alternative Alternative, double NullMean, double Alpha);
public sealed record PairTask(
    string TaskId, PairStatistic Statistic, string LeftRole, string RightRole,
    string LeftUnit, string RightUnit, DefinitionReference PairingPolicy,
    ImmutableArray<PairRow> Rows, ConditionalInference? Inference,
    bool ReturnDetails) : NumericalTask(TaskId);

public sealed record CategoryPair(
    NumericalMember Member, ObservationReference? LeftReference,
    ObservationReference? RightReference, ObservationState LeftState,
    ObservationState RightState, string? LeftLabel, string? RightLabel);
public sealed record CategoryTable(
    ImmutableArray<long> RowMajorCounts, DefinitionReference CertifiedPairTable,
    long ExpectedPairs, long MissingPairs);
public sealed record KappaTask(
    string TaskId, string LeftRole, string RightRole,
    DefinitionReference CategoryPolicy, ImmutableArray<string> Labels,
    ImmutableArray<CategoryPair> Pairs, CategoryTable? Table)
    : NumericalTask(TaskId);
~~~

结构校验先于接纳：TaskId 非空且请求内唯一；行 ID 非空且任务内唯一（同物理成员跨不同任务允许），相同身份异内容拒绝 IDENTITY_CONFLICT，同内容重复也拒绝重复而不充样本；来源引用/hash/修订必须齐。模型、选择、配对/类别政策非空。所有数值有限，只有分布明确端点允许 Infinity；Valid 行须有值，其它 State 不可假装有效。两侧缺失状态各自保留，先形成已批准完整配对子集，再计算/排名；禁止分别删除 X/Y、按位置 zip、把 Unknown 补0/负类。RequireAll 遇缺口阻断受影响任务；ApprovedObservedSubset 必有批准引用，保留预计数/缺口和 Partial，不能称全总体。设计矩阵不做删行/插补：Members 全有效、N 行闭包完整，否则受影响设计任务 NotComputable；宿主若批准新子集须构造新输入。

NumericalPolicy 固定 engineering-binary64-v1：RankAbsolute=1e-14、RankRelative=1e-12，DecompositionTolerance=1e-10，PsdTolerance=1e-12，CorrelationRoundoffTolerance=8·2^-52，TQuantileAbsolute=TQuantileRelative=5e-12，FQuantileRelative=1e-10，TailRelative=1e-9。前四项作用于已归一化无量纲矩阵；相关容差仅处理有证明的舍入越界；分布误差门是目标支持域资格的技术阈值，不是客户物理公差。Identity 的内容 hash 在实现时按 §6.1 确定性字段编码生成，不在示例编造。调用方须显式传这些精确值，改值/域须新方法版本及回归接收，不运行时任意放宽。Budget 所有整数/字节/时限>0，MaxIntegerBits≥128 且≤4096，其它项不超过工程上界；MaxDetailRows 可为0并拒绝请求明细。接纳先核形状乘法/内存预留；未知枚举值及派生类型拒绝，不反射发现插件。

#### 7.1.3.2 公开结果与执行入口

~~~csharp
public enum NumericalValueState {
    Computed, MathematicalEndpoint, Undefined, InsufficientData,
    UnsupportedDomain, InvalidInput, RangeLoss, NumericUncertain,
    EvaluationFailed, BudgetExceeded, Cancelled
}
public sealed record NumericalValue(
    NumericalValueState State, double? Value, string Unit, string? Code);
public sealed record NumericalCoverage(
    long Expected, long Included, long Unknown, long Missing,
    long Unmeasured, long Invalid, long NotApplicable, long Excluded);
public sealed record NumericalProvenance(
    string CoreApiVersion, string ImplementationVersion, InputReference Input,
    InputClosure Closure, DefinitionReference Method,
    DefinitionReference SelectionPolicy, DefinitionReference? SubsetApproval,
    DefinitionReference NumericPolicy, string MemberSequenceHash,
    ImmutableArray<BackendIdentity> Backends);
public sealed record NumericalResult(
    string OperationId, string StatisticsSnapshotId, ResultState State,
    ImmutableArray<NumericalTaskResult> Tasks,
    ImmutableArray<Diagnostic> Diagnostics, NumericalProvenance Provenance);
public abstract record NumericalTaskResult(
    string TaskId, NumericalCoverage Coverage, ImmutableArray<Diagnostic> Diagnostics);
public sealed record NumericalMoments(
    string GroupKey, long Count, NumericalValue Mean, NumericalValue M2,
    NumericalValue SampleVariance, NumericalValue Minimum, NumericalValue Maximum);
public sealed record GroupMomentsResult(
    string TaskId, NumericalCoverage Coverage, ImmutableArray<Diagnostic> Diagnostics,
    ImmutableArray<NumericalMoments> Groups) : NumericalTaskResult(TaskId, Coverage, Diagnostics);
public sealed record ContrastValue(string Id, NumericalValue Estimate, NumericalValue SumSquare);
public sealed record ContrastResult(
    string TaskId, NumericalCoverage Coverage, ImmutableArray<Diagnostic> Diagnostics,
    ImmutableArray<NumericalMoments> Groups, NumericalValue WithinSumSquare,
    ImmutableArray<ContrastValue> Contrasts) : NumericalTaskResult(TaskId, Coverage, Diagnostics);
public sealed record RowDetail(string RowId, NumericalValue Value);
public sealed record LinearCoefficient(string ColumnId, NumericalValue Value);
public sealed record DesignDiagnostics(
    int Rows, int Columns, int Rank, double RankThreshold,
    ImmutableArray<double> SingularValues, ImmutableArray<double> ColumnCenters,
    ImmutableArray<double> ColumnScales, double ResponseCenter, double ResponseScale,
    double ReconstructionError, double OrthogonalityError, double? ConditionNumber);
public sealed record DesignResult(
    string TaskId, NumericalCoverage Coverage, ImmutableArray<Diagnostic> Diagnostics,
    ImmutableArray<LinearCoefficient> Coefficients, long ResidualDegrees,
    NumericalValue ResidualSumSquare, NumericalValue ResidualVariance,
    DesignDiagnostics? Design, ImmutableArray<RowDetail> Residuals,
    ImmutableArray<NumericalValue> RowMajorCoefficientCovariance)
    : NumericalTaskResult(TaskId, Coverage, Diagnostics);
public enum PsdState { PositiveDefinite, Semidefinite, Invalid, Uncertain }
public sealed record CovarianceContribution(string LeftId, string RightId, NumericalValue Value);
public sealed record CovarianceResult(
    string TaskId, NumericalCoverage Coverage, ImmutableArray<Diagnostic> Diagnostics,
    PsdState Psd, ImmutableArray<double> Scales, ImmutableArray<double> Eigenvalues,
    double? ReconstructionError, double? OrthogonalityError,
    NumericalValue Variance, NumericalValue StandardUncertainty,
    ImmutableArray<CovarianceContribution> Contributions)
    : NumericalTaskResult(TaskId, Coverage, Diagnostics);
public sealed record DistributionResult(
    string TaskId, NumericalCoverage Coverage, ImmutableArray<Diagnostic> Diagnostics,
    DistributionKind Distribution, DistributionOperation Operation, TailSide Side,
    double Argument, double Degrees1, double? Degrees2, NumericalValue Output,
    double? SmallTail, long? Iterations, bool HasPerRequestConvergenceCertificate)
    : NumericalTaskResult(TaskId, Coverage, Diagnostics);
public sealed record InferenceResult(
    InferenceKind Kind, Alternative Alternative, double Alpha, long Degrees,
    NumericalValue Statistic, NumericalValue Probability,
    NumericalValue LowerMeanBound, NumericalValue UpperMeanBound,
    DefinitionReference AssumptionEvidence);
public sealed record PairResult(
    string TaskId, NumericalCoverage Coverage, ImmutableArray<Diagnostic> Diagnostics,
    PairStatistic Statistic, NumericalValue Estimate, NumericalMoments? Differences,
    int LeftTieGroups, int RightTieGroups, int LeftMaxTie, int RightMaxTie,
    InferenceResult? Inference, ImmutableArray<RowDetail> Details)
    : NumericalTaskResult(TaskId, Coverage, Diagnostics);
public sealed record KappaResult(
    string TaskId, NumericalCoverage Coverage, ImmutableArray<Diagnostic> Diagnostics,
    ImmutableArray<string> Labels, ImmutableArray<long> RowMajorCounts,
    ImmutableArray<long> RowTotals, ImmutableArray<long> ColumnTotals,
    long Total, long Agreeing, NumericalValue Agreement, NumericalValue Kappa)
    : NumericalTaskResult(TaskId, Coverage, Diagnostics);

public interface INumericalStatistics {
    NumericalCapabilities NumericalCapabilities { get; }
    NumericalResult ComputeNumerical(NumericalRequest request, CancellationToken cancellationToken);
    ValueTask<NumericalRun> ComputeNumericalAsync(
        NumericalRequest request, CancellationToken cancellationToken,
        IProgress<StatisticsProgress>? progress = null);
    ValueTask<NumericalOperationLookup> QueryNumericalOperationAsync(
        string operationId, CancellationToken cancellationToken);
}
public abstract class NumericalRun : IAsyncDisposable {
    public abstract string OperationId { get; }
    public abstract Task<NumericalResult> Completion { get; }
    public abstract IAsyncEnumerable<NumericalNotification> Notifications { get; }
    public abstract ValueTask CancelAsync(CancellationToken cancellationToken);
    public abstract ValueTask DisposeAsync();
}
public sealed record NumericalNotification(
    string OperationId, long Sequence, string Kind,
    StatisticsOperationStatus? Status, StatisticsProgress? Progress,
    StatisticsDrainObservation? Drain, NumericalResult? Result, long DroppedNotifications);
public sealed record NumericalOperationLookup(
    string OperationId, OperationLookupState LookupState,
    StatisticsOperationStatus? Status, NumericalResult? Result);
public interface INumericalOperationReceiptSource {
    ValueTask<NumericalOperationLookup> QueryAsync(string operationId, CancellationToken cancellationToken);
}
public sealed record NumericalCapabilities(
    string ApiVersion, ImmutableArray<string> TaskKinds,
    DefinitionReference Policy, DefinitionReference SupportDomain,
    ImmutableArray<BackendIdentity> Backends);
~~~

StatisticsEngine 同时实现 IStatisticsEngine/INumericalStatistics，沿用同一实例 OperationId 登记、容量、DrainAsync/ForgetOperationAsync/DisposeAsync。数值与 SPC 用同 ID 混投拒绝 IDENTITY_CONFLICT；同闭包重入复用原 run。单任务语义不可算仍返回具名结果/诊断，不吞其它任务；请求结构无效在 Accepted 前抛 StatisticsRequestRejectedException。结果 Complete 只代表全部声明输入已处理，Undefined/UnsupportedDomain 不等于成功数值；子集 Partial；执行取消/超时/失败按 §6 状态链，已算项仅为实际子集。没有虚构 Unknown 行/默认结果补齐。数值通知复用 §6.1 有界降载/不依赖消费者规则，Kind 不加私有完成状态。状态查询 InputComplete 来自闭包/实际覆盖；终态 Result 非空、其余 null。

新增错误键 STAT.NUMERIC_DOMAIN（合法但超支持域）、STAT.RANK_DEFICIENT、STAT.PSD_INVALID、STAT.NUMERIC_UNCERTAIN、STAT.RANGE_LOSS、STAT.EVALUATION_FAILED、STAT.DEGENERATE、STAT.ASSUMPTION_MISSING；Diagnostic.MessageKey 使用同键且可有定位 TaskId 的 MetricId。第三方异常内部记录类型/阶段/后端身份，公开不用第三方类型。NumericUncertain 不裁负方差/谱/相关使成功；资源不足 BudgetExceeded；RangeLoss 区分中间信息丢失与已证输出溢出。Value 非 Computed/MathematicalEndpoint 为 null；只有数学端点允许 Infinity，Undefined 不显示0。整数计数留 Int64，所有 double 投影均注明舍入；不生成生产判定。

共同数值顺序为：预算/闭包验证→固定完整成员→尺度和结构验证→逐任务计算→有限性/残差/适用性门→覆盖/来源→资源排空→最终结果。同步数值入口仅允许全 managed 任务，任何请求到 native 分布/条件推断均返回 METHOD_UNSUPPORTED（不在 UI 线程阻塞 native）；其局部资源直接释放后返回。异步接纳后执行在非 UI 工作线程，token 只在校验/批次/排序分段/内核前后检查；进入不可中断端口后等待真实返回，不能 WaitAsync 超时后归还缓冲/槽位。后端对象由宿主拥有，须在 engine 排空后处置；调用期间数据为 Core 自有有界副本，端口不得保留或修改请求集合。无持久保存、无自动重试/换库。晚到结果只归原任务；查询/等待取消不取消计算。


<a id="qualification-numerical-backend"></a>
#### 7.1.3.3 分组、MSA 数值、设计矩阵和隔离后端

分组先按源声明顺序逐行校身份/State/单位，组键 Ordinal，同组固定成员顺序，不以线程完成顺序归约。尺度用正二次幂避免中间平方/差溢出，按 §7.1.1 稳定中心矩累计并反变换：n=0 的 mean/min/max 未定义、n=1 有 mean/M2=0 而样本方差不足；M2 的单位是 Unit²。每组 n/mean/M2/min/max 与覆盖分别返回。默认不返回全成员副本，沿原固定输入/MemberSequenceHash 重取。小离散差/极端量化须保留数值诊断，不自动去离群或加 epsilon。

ContrastTask 先形成上述组矩；每个 Contrast 的 Terms 组键唯一且必须全部存在并有有效样本。Coefficient 有限、总和按输入 binary64 的精确二进制有理值求和必须为0；SumSquareDivisor 有限>0、无量纲，由033冻结模型及组内计数推导并供本模块核引用，不由 Core 猜平衡设计。固定任一参与组均值为锚点 a，L=Σ c_g(mean_g−a)，SS=L²/divisor；使用二次幂尺度和补偿归约，禁止原尺度 Σx²−(Σx)²/n。WithinSumSquare=Σ组 M2，Estimates 单位 Unit，SS/Within 为 Unit²。缺格、同 ID 重复、组计数不满足冻结设计由033先拒绝；Core 仍拒绝不存在/空组，不填组均值。自由度、交互/主效应平方和组合、负分量截取由033唯一负责，库不把一组 contrast 自动称完整 ANOVA。

设计输入为显式 N×p row-major，长度 checked(N·p)，Response/Members 长度N，Columns 长度p、列ID唯一。Intercept 最多一列且全1；Indicator 只能0/1；Continuous 任意有限数。N≥p>0；RequireResidualVariance=true 需 N>p，否则回归系数/残差可描述、方差 InsufficientData。无截距不中心化；有截距仅中心化 Continuous 并对响应中心化，保留中心/尺度及零点系数反变换。截距和 Indicator 不随意重新编码；模型由消费者传，Core 不选择因素/交互。各非零列和响应按正二次幂缩放，非零信息因缩放下溢/相减消失时 RangeLoss；全零列判秩亏，全零响应允许确定系数但不能凭零残差证明模型资格。

固定顺序：有界复制/缩放→Thin Householder QR→检查 Q/R 有限与重构/正交→仅对 p×p R 求 SVD 谱→秩/病态门→满秩才回代→反变换→按原输入重新计算有界残差/SSE→残差方差和系数协方差。阈值 τ=max(RankAbsolute, RankRelative·σmax)，σ>τ 才计秩；等于阈值或临界邻域 [τ/2,2τ] 内有谱则 NumericUncertain，不由布尔 IsFullRank 决定。只有 rank=p、谱不在临界邻域、ConditionNumber=σmax/σmin≤1/RankRelative、相对 Frobenius 重构及正交误差≤DecompositionTolerance 才求系数。阈值/尺度/谱都入 DesignDiagnostics，秩亏结果保留诊断而系数 Undefined；SVD只诊断，不求伪逆。QR 约 O(Np²)/O(Np+p²)，R-SVD O(p³)/O(p²)；禁止 Full N×N Q，禁止高矩阵 N×p 的 full-U SVD。

残差 r_i=y_i−预测_i，SSE=Σr_i²，df=N−rank；仅稳定满秩且df>0才 s²=SSE/df。原尺度系数、残差、方差无法表示分别 RangeLoss，不用 max-double/∞补值；对需要残差方差的请求，反变换残差不可靠时系数可保留但方差 NumericUncertain。系数协方差 s²·R^-1·R^-T 用三角回代形成并沿同一尺度/中心变换到原参数坐标，禁止构造 XᵀX 求逆。它只是同方差独立误差模型的条件数值，不替消费者验证该假设。无 df 或要求未满足时各协方差元素带状态；单位为对应两系数单位乘积。矩阵列单位 Ui、响应Uy时系数单位 Uy/Ui；截距 Uy。残差 Uy、SSE/方差 Uy²。RowDetail.Value 在 DesignResult 仅为残差，行 ID 不移位；ReturnDetails=false 不分配全量残差输出。参数本身、SSE/协方差所需内部缓冲仍计预算。

AffineTask 是同量/角色已冻结的简单仿射专用入口：CenterX 有限且为 XUnit，模型 y=α0+β(x−CenterX)，完整配对后先共同缩放、两遍固定锚点中心化，计算 Sxx/Sxy，再 β=Sxy/Sxx、α0=meanY−β(meanX−CenterX)。采用与设计相同的有限性/原尺度残差/df/误差门，并用 [1,x−CenterX] 的同一 Thin QR/R-SVD 路线交叉诊断；系数ID固定 center-intercept/slope。同x导致 Sxx=0，返回 Undefined；n<2 InsufficientData；n=2可返回点拟合而df=0、残差方差/协方差不足，不把0 stderr当资格。CenterX 不由 UI 平移改变。差值在原尺度溢出先按尺度安全形成，不以未经批准 SimpleRegression.Fit 替换。

~~~csharp
public enum NumericalBackendValidation { Unverified, Validated }
public sealed record BackendIdentity(
    string Id, string Version, string SourceCommit, string BuildHash,
    string FloatingPointProfile, bool Interruptible,
    NumericalBackendValidation Validation);
public sealed record KernelMatrix(
    int Rows, int Columns, ImmutableArray<double> RowMajorValues);
public sealed record QrKernelResult(KernelMatrix Q, KernelMatrix R);
public sealed record SymmetricEigenKernelResult(
    ImmutableArray<double> Eigenvalues, KernelMatrix Eigenvectors);
public interface IStatisticsMatrixKernel {
    BackendIdentity Identity { get; }
    QrKernelResult ThinQr(KernelMatrix normalizedDesign);
    ImmutableArray<double> SingularValues(KernelMatrix squareR);
    ImmutableArray<double> SolveThinQr(
        QrKernelResult factor, ImmutableArray<double> normalizedResponse);
    SymmetricEigenKernelResult SymmetricEigen(KernelMatrix normalizedCovariance);
}
public sealed record NumericalBackendPorts(
    IStatisticsMatrixKernel Matrix, IStatisticsBetaKernel? Beta);
~~~

默认矩阵后端固定 managed-mathnet-isolated-v1：在唯一 Core 工程 Numerics/ 内按 DEV-GOV-006 移植已固定 Math.NET 5.0.0 commit 的 ManagedLinearAlgebraProvider.Double 中 ThinQRFactor/QRSolveFactored、SingularValueDecomposition、对称 EigenDecomp 及其必要纯数值 helpers；保留 MIT 版权/许可与原 source/hash、改造记录，禁止复制整个工程或用 .work 作运行依赖。移植后的命名空间内部化，不公开 Math.NET Matrix/Vector/Provider/Complex；保留算法顺序/局部迭代拒绝机制，所有 Control/LinearAlgebraControl/CommonParallel/调度取值改为明确的本次串行局部循环，不能读写宿主全局。这是一项明确的源码适配实施任务，非已经存在的内核。其算子语义/重构/退化必须按本节与固定上游测试验证；不得省略为“实现者选一个库”。

原库真实公共入口 ThinQRFactor(double[],int,int,double[],double[])、QRSolveFactored(...,QRMethod.Thin)、SingularValueDecomposition(bool,double[],int,int,double[],double[],double[])、EigenDecomp(bool,int,double[],double[],Complex[],double[]) 是接线依据；原数组为 column-major，模块公开 row-major，内部只做一次有界转置，不将布局错位交给客户。原 SVD 即使 computeVectors=false 仍要求 p×p U/VT，预算按真实分配；只对R调用。原 ThinQR helper读取全局 Control 并使用 CommonParallel，直接 new provider 并不隔离，故本路线不直接引用原全局库。原 SVD/EVD 局部1000迭代不是整次 deadline，也不当逐请求收敛证书。替代内核只能以显式新 BackendIdentity/方法版本接收，不能 UseBest、探测 GPU 或无声正常方程/伪逆回退。端口调用是同步不可中断阶段；大小/预算先检查，结束前保留输入和槽位。

#### 7.1.3.4 协方差校验与传播

ComponentIds/InputUnits/sensitivities 长度p一致、ID唯一，矩阵p²、1≤p≤128，所有值有限，未知相关不能填0。Sensitivity_i 单位 OutputUnit/InputUnit_i；Σij 为 InputUnit_i·InputUnit_j。不允许 UI 编辑后直接使用；BudgetModel 是消费者冻结的不确定度模型引用。先查对角≥0和对称：本版要求数值完全相等（+0/−0可同值），不自动 (Σ+Σᵀ)/2。零对角行列必须全零，否则 PSD Invalid；不删除零分量隐藏错误。

正对角取 D_i=√Σii；零行取 D_i=1（记录零分量身份，单位归一尺度为该分量单位），通过安全比值形成 C=D^-1ΣD^-1，w=Dc。尺度过小导致比值/权重丢信息 RangeLoss。先结构验证再调用 SymmetricEigen，取得实谱/列特征向量，核相对 Frobenius CV−VΛ 和 VᵀV−I ≤DecompositionTolerance；λmin<−PsdTolerance·max(1,|λmax|) 为 Invalid，负但在该门内为 Uncertain，不裁为0。非负谱且残差通过才能 PositiveDefinite/Semidefinite；零邻域的数值谱不能单独证明精确 PSD：只在结构可证（全零或 n≤2 的精确二进制有理主子式）时承认 Semidefinite，其它临界矩阵 Uncertain。不以可逆、Cholesky、逐对相关范围或行列式单项替代全 PSD。

通过门后以稳定尺度/补偿计算 v=wᵀCw，另用原 c_iΣijc_j 形成贡献：i=i 单项、i<j 返回2c_iΣijc_j，不重复双算。Variance 单位 OutputUnit²，StandardUncertainty=√v 单位 OutputUnit。两路线在冻结误差门内相符；v为负或舍入无法证明非负则 NumericUncertain，不取 abs。本版在精确结构可证零方差时返回0，否则接近0且误差符号不能判定时返回 Uncertain。结果保留D/谱/残差/贡献，不做负谱投影；非线性适用性/覆盖因子仍由033/055负责。EVD及完整诊断 O(p³)/O(p²)，二次型才 O(p²)。

<a id="qualification-tail-distribution-method"></a>
#### 7.1.3.5 t/F 尾与分位：参数域、公式和错误门

工程方法固定 boost-beta-tail-v1，标准t无位置/尺度参数；F的 Degrees1/2始终分子/分母，不排序。数学域 df有限>0，t的 Degrees2=null，F必须有 Degrees2。本版本冻结实现支持域 df各自∈[1,10^6]（允许实数），非端点量化请求的原概率 p∈[10^-12,1−10^-12]；原 p位模式保留，计算小尾r=p或1−p并查 r∈[10^-12,.5]，上界舍入不以十进制意图解释。Tail 输入标准t任意有限z、F有限z≥0，只在算法所得严格小尾∈[10^-12,.5]内提供 Computed；其它合法尾返回 UnsupportedDomain 并保留原参数。不扩大成任意 double 合法域，不改正态、不改df。域与§7.1.3.1容差是本轮工程设计冻结，尚无产品后端/整域精度证据；实现必须执行§7.1.3.8资格套件后才能在发布 Capabilities 声明实际支持，失败先修实现或显式修方法，不把研究点通过宣传为整个矩形通过。

数学端点单独处理：Quantile p=0/1，t Lower为−∞/+∞，Upper反向；F Lower为0/+∞，Upper反向。Tail t的±∞给0/1，z=0两尾.5；F z=0为Lower0/Upper1、+∞反向。这些 Output.State=MathematicalEndpoint，不提供有限宽资格区间；t z=0 的.5 是可精确算的有限特殊值 Computed。NaN、df非法、F负值 InvalidInput；输出溢出/内部损失不标数学端点。

分位先保留原侧/原p；当p>.5，r=1−p并切换尾侧（F通过交换Beta参数，不能用F的简单正负号）；小尾小侧固定：
- t：x=ibeta_inv(df/2,.5,2r,&y,policy)，|z|=√(df·y/x)，原小侧Upper取正、Lower取负；r=.5时z=0直接返回。y使用函数直接互补，不算1−x。
- F Lower：x=ibeta_inv(df1/2,df2/2,r,&y,policy)；F Upper：y=ibeta_inv(df2/2,df1/2,r,&x,policy)。z=(df2/df1)·x/y，不能调用会先1−q丢尾的 ibetac_inv 入口。
- 乘除/开方用 binary64 尾数及整数指数（ILogB/ScaleB 等）组合，不先 df·y、x²或df1·z产生溢出；保留互补变量和原位模式。内部x或y丢失且无法区分输出真溢出时 RangeLoss，不猜原因。

尾值用尾数/指数形成t的u=z²、d=df，F的u=df1·z、d=df2，先比较后算s=min(u,d)/max(u,d)≤1，再小变量 s/(1+s)、大变量1/(1+s)，不能先恢复u。t的x=df/(df+z²)、y=z²/(df+z²)：小侧 x≤.5用ibeta(df/2,.5,x)/2，否则ibetac(.5,df/2,y)/2，z正小侧Upper、z负小侧Lower。F的x=u/(u+d)、y=d/(u+d)：Upper y≤.5用ibeta(df2/2,df1/2,y)，否则ibetac(df1/2,df2/2,x)；Lower x≤.5用ibeta(df1/2,df2/2,x)，否则ibetac(df2/2,df1/2,y)。大尾只在直接小尾可表示并满足域后用1−小尾，结果保留SmallTail，禁止从舍入为1的大尾倒推0。

有限观测的尾真实严格(0,1)：内核返回0/非有限、s下溢或最终乘除窄化丢尾 RangeLoss；尾尚可表示但低于冻结最小r是 UnsupportedDomain。内部失败 EvaluationFailed，回代未满足相对尾门 NumericUncertain。分位用同尾向回代作必需但非充分门：相对尾差≤TailRelative；不伪造单次分位真实误差证明。独立高精度oracle验证t误差≤TQuantileAbsolute+TQuantileRelative·|q_ref|，F相对误差≤FQuantileRelative，尾相对≤TailRelative。没有每次证书，Iterations=null、HasPerRequestConvergenceCertificate=false；这不影响已通过声明资格的数值值。数学端点/超域/失败不参加回代“成功”计数。

<a id="qualification-tail-runtime-evidence"></a>
#### 7.1.3.6 Boost 适配端口、构建及不可中断限制

~~~csharp
public enum BetaOperation { Lower, Complement, InverseLower }
public sealed record BetaKernelRequest(BetaOperation Operation, double A, double B, double Argument);
public sealed record BetaKernelResult(
    NumericalValueState State, double? Value, double? Complement,
    string? Code, long? Iterations);
public interface IStatisticsBetaKernel {
    BackendIdentity Identity { get; }
    ValueTask<BetaKernelResult> EvaluateAsync(
        BetaKernelRequest request, CancellationToken cancellationToken);
}
~~~

可选模块内适配唯一工程为 src/Modules/statistics/Asun.Modules.Statistics.Distribution.Boost/Asun.Modules.Statistics.Distribution.Boost.csproj，namespace Asun.Modules.Statistics.Distribution.Boost，只引用 Core。公开工厂 BoostBetaKernel.Create(string absoluteLibraryPath, string expectedSha256) 返回 IStatisticsBetaKernel；加载前核绝对路径/hash/方法ABI，不能环境 PATH搜索/安装替换/探测另库。native 唯一工程在其 native/Asun.Statistics.BoostBeta.vcxproj，发布 Windows x64 ABI1 DLL；不是另一个独立模块/会话。适配测试仍在本模块 Core.Tests 的 Adapter 子目录，Host 额外引用该适配工程；不创建无消费者的第二测试工程。本轮不创建工程。

固定 Boost.Math1.88.0 commit 529f3a759d83aa9437613666ea6293c9336d4069，BSL-1.0；复用完整实际包含闭包/source hash，保留版权/许可；.work只是研究原件，不作 include路径。native Windows x64/MSVC2026 C++17、/O2 /fp:strict /MD，double53位、round-to-nearest、FTZ/DAZ关闭、禁fast-math，Boost promote_double/float=false、standalone、domain/pole/overflow/evaluation/underflow全部throw_on_error，max_root_iterations=200、max_series_iterations=1,000,000。编译器具体版本、CPU/浮点设置、源码闭包和DLL hash随实际发布 BackendIdentity固定，不在文档造hash。环境不匹配返回 VERSION_INCOMPATIBLE，不核用户商业许可。

自定义ABI是明确待实施合同：extern "C" 导出 int32_t __cdecl im043_beta_v1(int32_t op,double a,double b,double p,double* value,double* complement) noexcept；op=0 ibeta、1 ibetac、2 ibeta_inv(...,&complement,policy)。返回0成功、1域/参数、2范围损失、3求值、4未知内部失败；非0时两个输出不消费，均预置quiet_NaN，成功 Lower/Complement也不要求互补输出（NaN），InverseLower需返回直接 x/y。返回int32及double不跨C++对象/异常/内存所有权；native只借本次指针且返回前结束调用，捕获所有异常，C#适配映射上述状态，不把C++异常穿过ABI。适配不启动私有进程/回调或保存数据。同步导出在非UI工作线程调用，EvaluateAsync token只在进内核前检查，之后不可提早返回；不使用 cancellation Task替代真实结束。大尾/df/尺度转换留 Core，不在两层复制一套t/F实现。

官方 ibeta_inv 支持直接输出互补变量，但固定源码部分连分式与Temme Newton不消费整次共享计数；嵌套调用预算不共享。上述policy局部上限不保证整次有限迭代/硬期限。WallClockLimit只触发停止意图，真实在途保持 Draining，资源/并发槽不能返池；要求硬实时上限的部署不在本方法能力声明。原研究F2,2 Upper1e-20直接补分位丢失而交换小尾约1e20；t2 nextDown(.5)的x可舍入1而y=2^-106；t1 Upper1e-200有可表示分位但Beta变量下溢、F1,1相同尾是真输出超范围；F2,4 z=2^600的最终尾可下溢。这些在工程域外仍作为拒绝/分类回归，不扩大支持域或填p=0。原14/15点研究不是矩形域资格；不得沿用它为本次产品声明。

<a id="cross-process-statistics-method"></a>
#### 7.1.3.7 配对连续量、差值与分类一致性

PairTask 的 LeftRole/RightRole、PairingPolicy 和两侧单位须冻结。Pearson/Spearman 两侧可为不同量/单位；Difference 必须同量同单位，方向固定 right−left（消费 post−pre 时 RightRole=post），不能根据页面左右排列改方向。每个 PairRow 一个原分析单位：独立推断要求观察单位间独立，不能有未经建模 ClusterKey；同板多个点不自动成为独立单位。字段 ClusterKey 非空时仍可描述但本条件推断不支持；无ClusterKey不等于证明独立，必需 AssumptionEvidence。任何权重只能1，本API不接受任意 sample weight，不暗中按板平均。变更观察单位、缺失政策、方向/α/方法必须新输入/OperationId，不能从已完成结果挑最大相关。

Pearson n≥2：先对每侧按正二次幂安全缩放，固定锚点两遍求均值/中心残差，再各自除 max|residual|，用稳定范数归一为单位向量，按原行顺序补偿点积得r。禁止原 Sxx·Syy 或 deltaX·deltaY 在原尺度溢出；原值非有限是输入错误，尺度信息丢失是 RangeLoss。任一侧全常数 Undefined而非0；近常数按中心化误差上界8·2^-52·max|scaled value|给诊断，不能自动换 Spearman或删除。结果点值单位1。理论 |r|≤1；越界仅在误差≤CorrelationRoundoffTolerance且有额外独立的精确二进制 Gram 共线证明时修到±1并记 RoundedBoundary，否则 NumericUncertain。精确证明只用于≤64行、扣MaxIntegerBits预算，不能为了裁切启动无界整数。原点r在范围内可返回；非共线却舍入±1时记 PrecisionSaturated，推断不可用，不把p写0。n=2非恒定的±1点值是样本性质，非强证据。r=0不证明独立；Y=2X+10给r=1也不证明量测相等。

Spearman 先批准完整配对子集，然后分别按真实 binary64数值排序（±0同值，NaN已拒绝），同值组1-based位置p…q赋平均秩(p+q)/2，按 RowId 还原原配对，再调用同一 Pearson点值。稳定身份只兜底同值顺序，不给并列不同秩；显示舍入/非传递近似相等不参与并列。工程N上界保证整数/半整数秩精确；输出两侧并列组数/最大并列数（只计大小≥2的组）。任何一侧全同秩 Undefined。禁止无并列公式1−6Σd²/[n(n²−1)]用于有并列。排序采用有界稳定归并、每归并块取消检查，O(N log N)/O(N)；不外排到未批准存储。Details仅在请求时返回左右平均秩，RowDetail.RowId 用 Left/Right 前缀与原RowId的无歧义长度编码，不能按排序行号关联。

Difference 逐完整配对共同安全尺度形成d=right−left，再按固定顺序稳定累计 n/mean/M2/sample variance/min/max，每个差对应同一 RowId/两侧引用。n=1有描述差但样本方差不足，n=0描述未定义；有限原值差超范围 RangeLoss，不裁最大值。结果Estimate=mean difference，Differences 使用 NumericalMoments，GroupKey固定 paired-difference；Details只在ReturnDetails时提供差值。配对方差绝不能换成两侧边际方差之和，n/coverage不由两边独立删除得到。非Difference的Differences=null，未请求Details为空；未请求Inference为null，表示没有推断而非成功空区间。

条件推断仅两项，不默认随点值返回：
- PearsonZeroT：Statistic必须Pearson，n>2、独立同分布二元正态/零相关原假设证据、NullMean=0、0≤|r|<1并通过非饱和门。t=r√[(n−2)/((1−r)(1+r))]，df=n−2；Less取Lower(t)，Greater取Upper(t)，TwoSided取2·Upper(|t|)。不先1−CDF。Alpha有限0<α<1，作为预声明判断水平记录，不自动质量判定。Pearson均值上下界返回UnsupportedDomain（相关区间未支持），不冒充缺失/零宽CI。
- PairedMeanT：Statistic必须Difference，独立同分布正态差值/缺失机制证据，n≥2、sD>0，NullMean同差值单位，SE=sD/√n、df=n−1、t=(meanD−NullMean)/SE，尾方向同上。TwoSided均值界 meanD±q·SE，q为Upper(α/2)；Greater下界meanD−q(Upperα)·SE、上界数学+∞；Less上界meanD+q(Upperα)·SE、下界−∞。α/2及df须落本节分布域；常数差保留描述，推断 Undefined，不返回∞t、p=0/1或零宽资格区间。置信区间针对总体均值变化，非单件预测/一致性限/等效性。

推断本身的任务结果与描述分开，任意尾/分位超域/失败保留描述、仅推断给对应状态。p超域不换检验；两侧p计算中小尾与最终范围都核验，n3 r=√3/2的双侧p=1/3作为解析断言。临界/零方差、独立性证据缺失、聚类/加权、截断等返回明确诊断。Spearman p/CI、Pearson CI、κ/一致率p或CI、加权κ、多重比较、置换、BCa/basic/studentized bootstrap、非等概率/多层/重复测量 bootstrap、Bland–Altman一致性限、等效/非劣与因果均明确不支持；§7.1.3.9 的 `group-percentile-bootstrap-v1` 是独立的组级计数区间切片，不扩展这些推断。本页支持的是这些具名点值、两项条件推断和 S6 组级区间，扩展须新方法契约。推断字段在已请求而条件不满足时仍返回 InferenceResult 的具名错误状态，不以null吞掉请求。

KappaTask 是固定名义单标签全集、角色和CategoryPolicy。Labels唯一、Ordinal、K≥2；类别缺陷码数字/字典序不作距离。明细模式 Pairs非空或合法空，Table=null；汇总模式 Pairs空、Table非空，必须 CertifiedPairTable证明同单位同状态的完整配对交叉表，不以两个边际拼表。Valid的两侧标签均须在全集，未知标签报冲突而不采用sklearn labels悄悄删行。Unknown/未审/不可见/撤销保留预计覆盖，不能当正常类；真正“拒识决策类别”须类别政策具名、与数据缺失分开。

按Left为行/Right为列累计K²非负checked Int64；总n、d和边际也checked，总量溢出 NUMERIC_OVERFLOW，不扩大无限类别表。汇总 ExpectedPairs/MissingPairs非负、ExpectedPairs=n+MissingPairs，以源证明保留缺口；Coverage其他缺失类为0并说明无法细分，不能假装行身份齐全。明细覆盖按实际 State分类，不丢预计记录。p_o=d/n；核心内部 BCL BigInteger在MaxIntegerBits内精确计算 A=n·d−Σr_i c_i、B=n²−Σr_i c_i，然后 κ=A/B 最后转binary64（该Int64域只需≤128bit）；不先1−p_e相消，不把 BigInteger作为公开DTO。n=0两者Undefined；B=0时Agreement=1、κ Undefined；κ<0合法，不裁0。表/边际/原整数返回，Agreement/κ单位1，rounded投影不取代原计数。K²表/精确整数字节/诊断也扣预算，O(N+K²)；不提供伪计数/加权/默认“好坏”阈值，不据κ认定谁正确或质量放行。

#### 7.1.3.8 数值验证、最小 Host、预算和迁移接收

以下为实现时必须消费的向量，不宣称本轮已运行产品。测试统一本模块 Core.Tests，复用033与已有研究的输入/来源，不重新造平行权威；独立oracle与生产算法不得共享同一特殊函数作为expected。

| 范围/向量 | 可判定断言 |
|---|---|
| 空组/单行/大偏置小差、重复身份/缺格/Unknown/混单位 | mean/方差各自状态，重复不充n；平方单位/覆盖正确，无插补；平衡MSA是否成立由033而非Core决定 |
| 033交叉2×2×2，y=100+4p+2o+po+e（各±1） | 本模块组矩/声明contrast组合后SS_P/O/PO/E=128/32/8/8；033核df=1/1/1/4、原分量2/3/6/30及GRR11/Total41，不能在Core复制资格判断 |
| 033嵌套/负交互/缺格；µm→mm | 组矩/SS与033唯一向量相符，负分量政策留033；mean/σ÷1000、M2/SS÷10^6，不能方差线性缩放 |
| x=0/1/2各两次，y=(0,2)/(1,3)/(4,6)，CenterX=1 | α0=8/3、β=2，SSE=22/3、df4，残差方差11/6；中心截距/斜率协方差0，方差分别11/36、11/24；消费者PE6/LOF4/3加和核SSE |
| N=p、同x、零列/重复列、近共线临界谱、设备和时间完全混杂/ABBA | 两点点拟合与df0分开；秩亏/临界谱不伪逆；可识别性不由缩放创造，返回门和原尺度残差均核 |
| Thin QR/R-SVD/EVD与内核注入NaN/错尺寸/非正交/不收敛 | 尺寸/预算接纳前核；分解失败不提供系数/合法PSD；对R而非高X求SVD；实际内存与N/p复杂度一致 |
| Σ=[[4,4],[4,4]]、[[4,8],[8,4]]、3维diag1/offdiag−.9 | 第一组精确PSD秩1，c=[1,1]/[1,−1]方差16/0；第二组特征12/−4非法；第三组负谱−.8不能因逐对相关合法而接受 |
| 非对称/零对角非零行、近0负谱、混量纲/共同参考 | 不自动对称化/裁谱；共同参考不除√n，033四次σ2µm及共同u3µm均值方差10µm²，尺度反变换不变 |
| t1/t2/F1,1/F2,2解析，F2,4在z1 | 固定binary64输入独立高精度参考；F2,4 Lower=5/9，不假中位1；t1 .9999分位约3183、F1,1 .99约4052，不沿原Math.NET夹根范围截值 |
| df=1/1.5/2/3/5/10/30/100/1000/10^6，两侧概率1e−12/1e−9/1e−6/.01/.25/.5及邻接double | 按原位模式oracle核§7.1.3.5误差；F交叉df对、近中位、域边界内外、单调/对称/倒数关系；回代不是独立oracle |
| t2 Upper=nextDown(.5)、F2,2 Upper1e−20、t1/F1,1 Upper1e−200、F2,4 z=2^600 | 前者直接互补保留；后三者按冻结域/范围分类，禁止p0、∞端点或静默扩域；底层不足不伪报迭代0/Converged |
| X=[−1,0,1],Y=X²；Y=2X+10；全常数；n2 | r0不意味着独立、r1不意味着相等；常数Undefined，n2点±1无本条件推断 |
| [1,1,nextafter(1,2)]对[0,0,3]；非共线[1,2,3]对[1,2,3+2^-40] | 前者数学r1，越界裁切需证明；后者binary64可饱和1，不输出p0 |
| X=[1,2,3,4],Y=[1,2,2,3]，删缺行前后排名 | 平均秩[1,2.5,2.5,4]，Spearman=√.9≈.9486832980505138而非.95；完整配对后排名，独立删行反例不得沿用全体秩 |
| pre=[10,20],post=[11,23]，正态差假设、μ0=0 | d=[1,3]、mean2、sample variance2、SE1、df1、t2；两侧边际方差之和122不能替代2；双侧p=2atan(.5)/π≈.2951672353008665；合成50%CI[1,3]，95%q≈12.7062047361747 |
| κ表[[20,20],[10,50]]、[[99,1],[0,0]]、[[5,0],[0,0]]、[[0,5],[5,0]] | κ依次8/23、0、Undefined、−1；对应一致率与覆盖单列，不伪计数/裁负 |
| κ表[[10^18−1,1],[0,0]]；expected3仅known2 | 精确κ0，即使po/pe都舍入1；已知子集一致率1、覆盖2/3，不补第三项正常 |
| 同闭包重入/异闭包/数值与SPC撞ID，两宿主/取消等待/不读通知 | 单登记/原结果、冲突拒绝、实例隔离；不读通知仍完成，等待取消不取消计算 |
| 内核阻塞/忽略取消/晚到、Drain deadline/Dispose、关闭/回退 | 进入内核后取消保持Draining非终态/槽位；晚返只归原任务，确认释放后唯一DrainCompleted/终态；旧结果/hash只读，版本不兼容拒绝 |

独立分布参考使用至少100位十进制精度的直接数值积分/根求解或解析闭式，输入由binary64精确有理值构造；再以200位复算稳定参考。除表内格点，资格套件固定种子0x1043、对df和小尾作log均匀抽样各10,000点（t与F分别），含F交换参数、域四角、nextUp/nextDown边界与输出残差；保留原输入位模式/expected/actual/误差/失败分类，复用已有测试夹具输出，不以随机样本证明连续域数学全覆盖。独立资格未执行前发布Backends不得声称Validated；无证据BuildHash不能虚构，文档状态仍Prep。MSA物理独立/客户水平是外部门，技术支持域/DTO已给出，不能把后端实现验证转成“API以后补”。

最小Host调用顺序（示意已定义接口，不是已实现示例）：构造 NumericalRequest 的固定输入/Closure/Policy/预算与上述合成任务→new StatisticsEngine(limits, numericalBackends: explicitPorts)→ComputeNumericalAsync→可选通知消费→Completion→逐Task/Value.State核证→宿主另保存→Dispose run/engine→处置宿主拥有端口。Core-only Host可用默认隔离managed矩阵后端并同步验证分组/contrast/设计/协方差/配对描述/κ；独立工程Host无Shell/数据库/DevExpress也能运行。条件t/F Host显式注入可选Boost端口；未注入Beta仅对应分布/推断 UnsupportedDomain，描述仍可算，不自动安装替代。生产消费者SPI与孔槽/钢网、连续配对与复判分类分别验证边界/覆盖/恢复，不以空调用证明复用。

专属BenchmarkProfile在§13口径下冻结N=0/1/2/10^4/10^6、组1/10^3、p=1/2/16/64/128、K=2/16/256、任务1/64、明细关/上界、缺失/并列0/高比例、满秩/临界/秩亏、协方差PD/PSD/非法、df/尾域、并发1/2/宿主上限、内核正常/阻塞/失败。矩阵自有输入、Q/R/work/R-SVD/U/VT/谱/残差、双秩排序缓冲、K²表/BigInteger、诊断/通知均计 MaxBufferedBytes；先核checked尺寸、按核实内核实际分配预留，不能仅8Np估全部。分别测验证/缩放/QR/R-SVD/回代/残差/EVD/Beta/成对/封装与真实排空，报告P50/P95/P99/分配GC/峰值/拒绝/失败/取消到排空；阈值按实际消费者Profile采纳，未给则NotEvaluated。内核无硬中断不承诺固定取消时延；高阶工作不占UI线程，预算不足不返回前N的全体系数。

迁移锚点固定：qualification-numerical-operations→本节§7.1.3.1–3，qualification-numerical-backend→§7.1.3.3–4，qualification-tail-distribution-method→§7.1.3.5–6，qualification-tail-runtime-evidence→§7.1.3.6，cross-process-statistics-method→§7.1.3.7–8。主会话已将PKG-045收为IM-043应用映射，033/055/配对消费者数值实现链接直接指向本指导；033的实验/资格公式保留，058A仅提供SPC公式常数参考。平台序列化/产品事实映射仍由其Owner采纳；发现实际契约冲突时暂停受影响接入切片，不另造权威。

<a id="group-interval-bootstrap"></a>
#### 7.1.3.9 组级比例与配对区间（切片 S6，ModuleCoreImplementationReady，仅规格准备）

本切片回应真实治理消费者对独立物理组比例、负担和同义务配对比较的窄缺口。它只提供通用组级计数推断，不定义缺陷、板、字符、像素、放行或客户门槛语义。S6 定向修订日期为 `2026-10-11`，文档版本仍为 `0.3.0-prep`；本节六项文档规格已于2026-10-11由主控内容接收，状态为 `ModuleCoreImplementationReady`（仅规格准备）；S1–S4 的 `ModuleCoreImplementationReady` 状态不回退。S6 规格接收后仍须单独完成实现、独立算法资格验证和消费者接线，不能把区间输出当作现场资格或签署证据。

DEV-GOV-010 §3.1 六项定位为：①本节首发方法/适用边界中的职责、治理与配对消费者；②本节公开 DTO、入口/状态/错误、唯一字段编码、PCG/整数/分位算法与来源；③本节两个纯 BCL Host 的完整请求→engine→结果断言；④本节完整字段 Golden、小型 Golden/错误/取消/关闭与恢复 Owner 断言，复用 §6/§12.1；⑤本节 BenchmarkProfile 与 §13 的负载、资源、P50/P95/P99 测点和 TargetPending；⑥本节两 Host 的最小调用顺序及本文开头 Core implementation binding 的唯一 Core/Core.Tests/TestHost 工程与允许/禁止路径。主控本轮已接收六项文档规格，并独立按字段重建17项长度/SHA-256、生产PCG16输出、G=3拒绝向量及两个精确分位区间，全部吻合；该结论仅为规格内容与字段算术一致，不代表实际C#后端可运行或算法/性能/产品资格通过。

**首发方法与适用边界。** 唯一首发方法为 `group-percentile-bootstrap-v1`：输入是已冻结、可复核的独立组；每次重采样以等概率有放回抽取整组，按原始整数分子/分母求 pooled ratio，再以固定 percentile 分位插值形成双侧或单侧区间。配对任务在同一重复中使用完全相同的组索引，对左右 pooled ratio 做 `left−right`；不能分别抽样再相减。失败、覆盖、缺失和 Unknown 计数随组保存并参与覆盖诊断；不因困难组、失败组、零分母重复或区间较宽而删除组/重复。

不支持加权组、分层不同抽样概率、时间/block bootstrap、多层 cluster、重复观测模型、有限总体修正、BCa/basic/studentized/permutation、同时区间、多重比较、缺失插补、比值的 delta 近似和任何自动方法选择。各组必须代表同一声明层级的可交换独立单位；物理组内的板/器件/字符/像素不得被当作独立 bootstrap 单位。若独立性、层级、义务全集或配对关系没有冻结证据，返回 `STAT.METHOD_UNSUPPORTED`/`NotComputable`，保留点计数和缺口诊断。

**公开 DTO（`Asun.Modules.Statistics`）。** 下列类型加入现有 `NumericalTask`/`NumericalTaskResult` 闭包；不另建项目、模块或统计库：

~~~csharp
public enum GroupIntervalTail { TwoSided, Lower, Upper }
public enum GroupIntervalRepeatState { Valid, ZeroDenominator, InvalidInput, Overflow, BudgetExceeded, Cancelled }

public sealed record FailureCoverageCrossCounts(
    long FailureAndCovered, long FailureAndNotCovered,
    long NonFailureAndCovered, long NonFailureAndNotCovered,
    long Unknown);

public sealed record GroupCoverageEvidence(
    long Obligations, long Covered, long NotCovered, long Failed,
    long Missing, long Unknown,
    FailureCoverageCrossCounts CrossCounts);

public sealed record GroupIntervalObservation(
    string GroupId, string EndpointName,
    long Numerator, long Denominator,
    string NumeratorUnit, string DenominatorUnit,
    GroupCoverageEvidence Coverage,
    ObservationReference Source);

public sealed record GroupRatioTask(
    string TaskId, string EndpointName, string RatioUnit,
    GroupIntervalPolicy Policy, GroupIntervalBudget Budget,
    ImmutableArray<GroupIntervalObservation> Groups)
    : NumericalTask(TaskId);

public sealed record GroupPair(
    string GroupId, GroupIntervalObservation Left,
    GroupIntervalObservation Right, string PairingKey);

public sealed record GroupPairedRatioTask(
    string TaskId, string EndpointName, string LeftRole, string RightRole,
    string DifferenceUnit, GroupIntervalPolicy Policy,
    GroupIntervalBudget Budget,
    ImmutableArray<GroupPair> Groups)
    : NumericalTask(TaskId);

public sealed record GroupIntervalPolicy(
    DefinitionReference Identity, string MethodRevision,
    GroupIntervalTail Tail, int ConfidencePpm, int Resamples,
    uint Seed, int MinIndependentGroups, string PrngRevision,
    string QuantileRevision);

public sealed record GroupIntervalBudget(
    int MaxGroups, int MaxResamples, int MaxIntegerBits,
    long MaxPrngOutputs, long MaxBufferedBytes, TimeSpan WallClockLimit,
    TimeSpan CancellationResponseLimit, TimeSpan DrainObservationLimit);

public sealed record GroupIntervalDiagnostics(
    int IndependentGroups, int ExecutedRepeats, int UnexecutedRepeats,
    int ValidRepeats, int InvalidRepeats, int CancelledRepeats,
    int ZeroDenominatorRepeats, int OverflowRepeats,
    bool DegenerateDistribution, long FailedGroups, long MissingGroups,
    long UnknownGroups, ImmutableArray<Diagnostic> Diagnostics);

public enum GroupIntervalBoundState { Computed, Undefined, InfiniteValue }
public sealed record GroupIntervalBound(
    GroupIntervalBoundState State, double? Value, string? Code);
public sealed record GroupIntervalProvenance(
    string MethodRevision, string PrngRevision, string QuantileRevision,
    uint Seed, string GroupOrderHash, string PrngOutputByteHash,
    long PrngOutputCount, long PrngRejectionCount);

public sealed record GroupIntervalEstimate(
    string EndpointName, NumericalValue Point,
    GroupIntervalBound Lower, GroupIntervalBound Upper,
    System.Numerics.BigInteger RawTotalNumerator,
    System.Numerics.BigInteger RawTotalDenominator,
    System.Numerics.BigInteger TotalNumerator,
    System.Numerics.BigInteger TotalDenominator,
    System.Numerics.BigInteger? RawLeftTotalNumerator,
    System.Numerics.BigInteger? RawLeftTotalDenominator,
    System.Numerics.BigInteger? LeftTotalNumerator,
    System.Numerics.BigInteger? LeftTotalDenominator,
    System.Numerics.BigInteger? RawRightTotalNumerator,
    System.Numerics.BigInteger? RawRightTotalDenominator,
    System.Numerics.BigInteger? RightTotalNumerator,
    System.Numerics.BigInteger? RightTotalDenominator,
    GroupIntervalDiagnostics Diagnostics);

public sealed record GroupIntervalResult(
    string TaskId, NumericalCoverage Coverage,
    ImmutableArray<Diagnostic> Diagnostics,
    string MethodRevision, GroupIntervalPolicy Policy,
    GroupIntervalProvenance Provenance,
    ImmutableArray<GroupIntervalEstimate> Estimates)
    : NumericalTaskResult(TaskId, Coverage, Diagnostics);
~~~

`NumericalRequest.Tasks` 接受 `GroupRatioTask` 或 `GroupPairedRatioTask`；每个 task 的 `Policy` 和 `Budget` 都是必填字段，禁止从 ambient/static config、DI 服务定位器或共享 catalog 补取。结果在同一 `NumericalResult.Tasks` 中返回 `GroupIntervalResult`。无需新增入口接口：同步调用沿 `INumericalStatistics.ComputeNumerical`，异步调用沿 `ComputeNumericalAsync`/`NumericalRun`，查询、通知、取消、排空、幂等和 `OperationId` 规则沿 §7.1.3.2 与 §6。外层 `NumericalPolicy` 继续提供 binary64、rank、分解和容差等公共数值策略；S6 task 的 `GroupIntervalPolicy` 才提供 Tail、ConfidencePpm、Resamples、Seed、PRNG 和 Quantile 修订；`GroupIntervalBudget` 与外层 `NumericalBudget` 对每项上限取较小值。请求的 task `MethodRevision`、`Policy.Identity`、`PrngRevision`、`QuantileRevision`、task `Budget`、输入快照 hash、组排序 hash 和 seed 均进入 operation identity/hash 及公开诊断；方法版本变化必须产生新 OperationId。缺任一字段、超限或 task/outer policy、budget 不一致，必须在接纳前拒绝；实现者不得猜测置信度、seed、Tail 或重复次数。

**结构、单位和覆盖预检。** `GroupId`、`EndpointName`、角色、单位、修订、来源引用和 `PairingKey` 非空；任务内 GroupId 唯一，pair 的 PairingKey 唯一，EndpointName/单位为任务所有组共同值（不要求各组不同），左右角色不同；输入组先按 `GroupId` ordinal 排序，不能按文件/到达顺序决定随机流。每个分子、分母、覆盖、失败、缺失、Unknown 和交叉计数为非负 checked `Int64`；交叉计数满足完整守恒：`Failed = FailureAndCovered + FailureAndNotCovered`；`Covered = FailureAndCovered + NonFailureAndCovered`；`NotCovered = FailureAndNotCovered + NonFailureAndNotCovered`；`Unknown = CrossCounts.Unknown`；`Obligations = Covered + NotCovered + Missing + Unknown`。这里 `Missing` 表示预期义务中没有读到或没有覆盖分类的组级义务，`Unknown` 表示已观察但覆盖状态未知的义务；两者不能互换。所有字段在 checked `Int64` 下非负，按组求和时保留失败、缺失和 Unknown 困难组，不删除以凑样本；不满足守恒时拒绝并定位组/字段。Ratio 要求每组 `Denominator > 0`、左右单位及方法修订一致；零分母组仍作为输入证据保留，但任务返回 `Undefined`/`NotComputable` 及 `STAT.DENOMINATOR_UNKNOWN`，不跳过该组继续 bootstrap。配对要求左右组 ID、义务层级、配对策略、单位兼容且集合完全相同；缺一侧或同组多行返回 `STAT.PAIR_INCOMPLETE`。

点估计先用 `System.Numerics.BigInteger` checked 累加所有组的原始分子和分母。Ratio task 的 `RawTotalNumerator`/`RawTotalDenominator` 保留 pooled 原始整数总数，`TotalNumerator`/`TotalDenominator` 是其约分后精确分子/分母，左右八个字段为 `null`；因此 `2/200` 必须同时保留原始 `2`、`200` 与约分后的 `1`、`100`。配对 task 的 `RawLeftTotal*`/`RawRightTotal*` 保留左右 pooled 原始整数总数，`LeftTotal*` 与 `RightTotal*` 是左右 pooled ratio 各自约分后的精确分数；`RawTotalNumerator = RawLeftTotalNumerator*RawRightTotalDenominator − RawRightTotalNumerator*RawLeftTotalDenominator`、`RawTotalDenominator = RawLeftTotalDenominator*RawRightTotalDenominator` 保留交叉相减前的 checked 原始差分子/分母，`TotalNumerator/TotalDenominator` 再是该差值约分后的精确结果。Ratio task 的四个 `RawLeft/RawRight` 字段与配对 task 的左右字段分别按 schema 全部为 null/非空，不能从 Binary64 `Point` 反推计数。输出 `NumericalValue.Value` 是该精确结果的 Binary64 投影，原始精确分数仍可复核；无法在 `MaxIntegerBits` 内表示或投影非有限时返回 `RangeLoss`，不截断、不转 double 后再相加。Ratio 单位是冻结的 `RatioUnit`；配对差值单位是冻结的 `DifferenceUnit`，不得从显示文字猜转换。

**固定 PRNG 和重采样算法。** `PrngRevision=pcg32-xsh-rr-v1`，不使用 `System.Random`、平台默认 RNG 或第三方库。实现按固定 PCG C 基准（commit `bc39cd76ac3d541e618606bcc6e1e5ba5e5e6aa3`）的 `pcg32_srandom_r`/`pcg32_random_r`/`pcg32_boundedrand_r` 语义重写为 BCL：`initstate=(ulong)Seed`，`initseq=54`，`inc=(initseq<<1)|1`；先 `state=0`、输出一次、`state += initstate`、再输出一次完成初始化。初始化加法、状态乘法和输出移位按 C# `unchecked` 的 `ulong`/`uint` 模 2^64/2^32 语义执行，状态/output/threshold 和 byte 截取按明确的 `unchecked` 规则执行，以下为状态/output 公式：

~~~csharp
unchecked
{
    ulong oldState = state;
    state = oldState * 6364136223846793005UL + increment;
    uint xorshifted = (uint)(((oldState >> 18) ^ oldState) >> 27);
    int rotation = (int)(oldState >> 59);
    uint output = (xorshifted >> rotation)
        | (xorshifted << ((-rotation) & 31));
}
~~~

**draw 预算与固定拒绝向量。** `GroupIntervalBudget.MaxPrngOutputs` 是任务必填的正 Int64 上限，统计初始化之后的每一次 PCG output（接受和拒绝都计入），不从平均拒绝概率推导。接纳前要求 `checked((long)G * Policy.Resamples) <= MaxPrngOutputs`，且上限不超过 `long.MaxValue/4`，以保证累计字节数可 checked 表示。每次 draw 前检查 token、墙钟期限及 output count；当 count 已等于上限时不再调用 PCG，返回 `STAT.BUDGET_EXCEEDED`，两端 Undefined，保留已完成重复和 hash。初始化的两次输出不计入上限或输出 hash；初始化只发生一次，不能重置流绕过预算。预算中断的当前重复计入 Executed/Invalid（RepeatState=BudgetExceeded），尚未开始的重复仅计 Unexecuted，不补跑、不重试。预算改变须新 OperationId。外层 MaxBufferedBytes、MaxIntegerBits、WallClockLimit、DrainObservationLimit 与 task 对应项取较小值；外层没有 MaxPrngOutputs 项，不能凭其它项猜它。

`increment=109UL`，`uint bound=checked((uint)G)`，`uint threshold=unchecked(0u-bound)%bound`。严格按 repetition=0..B−1、position=0..G−1 进行 bounded draw；每个位置可能消耗多次 output，只产生一个 accepted index：

~~~csharp
// 算法形状，非新增公共接口；state 已按 Seed/54 初始化。
Span<byte> bytes = stackalloc byte[4]; // 每次 bounded draw 一份，不在循环累积 stackalloc
while (true)
{
    cancellationToken.ThrowIfCancellationRequested();
    // 同时检查 WallClockLimit；count==MaxPrngOutputs 时终止该 task。
    if (outputCount == budget.MaxPrngOutputs) return BudgetExceeded;
    uint r = NextPcg32(ref state, 109UL); // 上方 unchecked 固定公式
    outputCount = checked(outputCount + 1);
    System.Buffers.Binary.BinaryPrimitives.WriteUInt32LittleEndian(bytes, r);
    outputHash.AppendData(bytes);
    if (r < threshold)
    {
        rejectionCount = checked(rejectionCount + 1);
        continue;
    }
    return r % bound;
}
~~~

`NextPcg32` 仅使用上方固定公式；生产不注入或替换 RNG。byte 截取与 threshold 减法使用 unchecked，预算/计数均 checked。Golden `S6-BOUNDED-G3-REJECTION-001` 使用真实 PCG transition 的**内部测试起点** `state=0UL, increment=109UL, bound=3u`（不运行 seed 初始化，不作为生产 Seed/Policy 路径），threshold=1。连续三个实际 output 为 `00000000,00000000,47c28b93`：拒绝前两个，接受第三个，index=2、outputCount=3、rejectionCount=2；前两个 output 必须仍进入 hash。上限=2 时，第三次调用前返回 BudgetExceeded、count=2、rejectionCount=2、无 accepted index；重置测试状态后上限=3 才接受，不在生产 operation 续跑。这样拒绝测试确定发生，不依赖约 2^-32 的罕见事件。生产 seed=(42,54) 的既有 16-output 向量继续独立验证初始化；内部起点不冒充生产种子。

**唯一字段编码（s6-field-encoding-v1）。** 每个域只在流开头写一次 ASCII 域名及一个实际 `0x00` 终止字节（文中的 `\0` 不是反斜杠和数字两个字符）；之后按以下顺序直接拼接字段，嵌套值不再写域。String 为无 BOM 的严格 UTF-8，前置 little-endian Int32 **字节**长度；拒绝孤立 UTF-16 代理项，保留原 Unicode，不作 normalization/trim/大小写折叠。仅 nullable String 使用 byte presence=0（无内容）或1（随后长度/字节），其它 String 非 null。bool 为 byte 0/1；enum 为 Int32：InputMode FixedSnapshot=0/LiveView=1，Completeness RequireAll=0/ApprovedObservedSubset=1，Tail TwoSided=0/Lower=1/Upper=2。Int32/Int64/UInt32、TimeSpan.Ticks、double 原始 UInt64 位模式均 little-endian。数组先写 Int32 Count，default 数组拒绝；nullable Int64/reference 先写 byte presence。hash 为64个小写hex字符的 String；最终 SHA-256 为小写hex。排序使用 `StringComparer.Ordinal` 的 UTF-16 code-unit 序，**不是 UTF-8 字节序**；先排序再编码。GroupId 唯一，Tasks 保留数组顺序。

以下定义完整嵌套字段；生成某对象的自身 hash 时才排除那个 hash，引用时包含完整 hash：

- `Coverage`：Obligations、Covered、NotCovered、Failed、Missing、Unknown，再写 CrossCounts 的 FailureAndCovered、FailureAndNotCovered、NonFailureAndCovered、NonFailureAndNotCovered、Unknown（11个 Int64）。
- `SourceBody`：Source.ObservationId、Source.SourceRevision、Source.EvidenceReference（nullable），GroupId、EndpointName、Numerator、Denominator、NumeratorUnit、DenominatorUnit、Coverage。Source.ContentHash 使用域 `S6-SOURCE-V1\0` + 此 body，不含自身 hash；左右不同内容必须不同来源 ID/hash。
- `Observation`：GroupId、EndpointName、Numerator、Denominator、NumeratorUnit、DenominatorUnit、Coverage，再写 Source.ObservationId、Source.SourceRevision、Source.ContentHash、Source.EvidenceReference（nullable）。
- `DefinitionReference`：Id、Revision、ContentHash。`DefinitionBody`：Id、Revision、下方完整定义正文 String；域 `S6-DEFINITION-V1\0`，不能只 hash Id/Revision。
- `NumericPolicyBody`：Identity.Id、Identity.Revision，再写 RankAbsolute、RankRelative、DecompositionTolerance、PsdTolerance、CorrelationRoundoffTolerance、TQuantileAbsolute、TQuantileRelative、FQuantileRelative、TailRelative 的9个 double；域 `S6-NUMERIC-POLICY-V1\0`。生成 Identity.ContentHash 不含自身 hash；作为请求字段时 body 后加 Identity.ContentHash。
- `GroupPolicyBody`：Identity.Id、Identity.Revision、MethodRevision、Tail、ConfidencePpm、Resamples、Seed、MinIndependentGroups、PrngRevision、QuantileRevision；域 `S6-GROUP-POLICY-V1\0`。作为 task 字段时 body 后加 Identity.ContentHash；任意参数变化都改变 policy hash。
- `GroupBudget`：MaxGroups、MaxResamples、MaxIntegerBits、MaxPrngOutputs、MaxBufferedBytes、WallClockLimit.Ticks、CancellationResponseLimit.Ticks、DrainObservationLimit.Ticks。`NumericalBudget` 按 §7.1.3.1 声明顺序全字段写（含 MaxNotifications）。
- `Closure`：ExpectedMembers（nullable Int64）、ExpectedMemberSetHash（nullable String）、ReadComplete、PopulationClosed、ClosureReceiptReference（nullable String）、Gaps（Count 后按 InputGap 声明顺序；State enum 沿 §3，nullable/time/sequence 用 presence；DateTimeOffset 只写 UTC ticks）。
- `Task`：类型 String（GroupRatioTask/GroupPairedRatioTask）、TaskId、EndpointName；ratio 再写 RatioUnit，paired 再写 LeftRole、RightRole、DifferenceUnit；随后完整 GroupPolicy、GroupBudget、Count、排序后的 Observation 或 pair（GroupId、PairingKey、Left Observation、Right Observation）。
- `InputMetadata`：SnapshotId、SnapshotRevision、Mode、QueryReceiptId、SourceBoundary、WatermarkId（nullable）、ReadComplete、CanReplay，不含正在生成的 ContentHash。
- `SnapshotBody`：InputMetadata、Closure、Method、SelectionPolicy、ObservedSubsetApproval（nullable DefinitionReference）、Completeness、完整 NumericPolicy、完整 NumericalBudget、Tasks。Input.ContentHash=SHA-256(`S6-INPUT-V1\0` + SnapshotBody)，ratio/paired 的完整内容各有独立输入 hash。完整请求 Golden/幂等摘要=SHA-256(`S6-REQUEST-V1\0` + OperationId + SnapshotBody + Input.ContentHash)；OperationId 不进入快照 hash，避免自引用。
- `MemberSet`：Count、排序后的 GroupId；ExpectedMemberSetHash 使用域 `S6-MEMBER-SET-V1\0`，配对按独立组而非两侧行计 Count。

`GroupOrderHash`：ratio 的 `S6-GROUP-ORDER-V1\0` **一次**、Count、排序后的完整 Observation；paired 的 `S6-PAIRED-GROUP-ORDER-V1\0` **一次**、LeftRole、RightRole、DifferenceUnit、Count、排序后的 GroupId、PairingKey、Left Observation、Right Observation。不得每组重写域、重复写角色或省略 Source.EvidenceReference。Coverage 顺序严格如上。组 hash 与另外覆盖请求 policy/budget 的 Input.ContentHash 不可互换；所有域使用同一编码原语。流式增量 SHA-256 只保留当前字段有界 scratch，字段长度/数组长度先 checked 预算拒绝。

MaxIntegerBits 取 task/outer 较小值且各在 [128,4096]；位数为 abs(value).GetBitLength()（零=0，符号不计）。输入计数、每步原始 pooled 累加、交叉乘积/差、GCD前后分数、每次重复和分位整数索引乘积都显式检查位数，不先约分掩盖超限；BigInteger 的 checked 语法**不会**执行位上限。差值可负，计数非负。一次预留 B 个 double，原地排序；当前 index draw 后立即同时归约左右，不保留 G×B 索引表。BigInteger scratch、排序栈、输入副本、UTF-8缓冲、增量 hash、诊断/通知/结果按峰值同时存活量计入任务/outer buffer及外层工作集，接纳前拒绝不足预算。取消后保留已完成值/状态，尚未开始重复不构造值；B数组预留保持至结束后释放，不声称取消时从未分配。

**重复与区间。** `ConfidencePpm` 为 1..999999；`Resamples≥2`、`MinIndependentGroups≥2`，且均不超过任务/外层预算。每次重复累加被抽组的精确整数分子/分母；任一零分母、整数溢出、非法组或取消都保留为对应 `GroupIntervalRepeatState` 并递增计数，不能删除无效重复后用剩余样本“修复”。本版要求所有重复 `Valid` 才能返回区间；否则 `Lower`/`Upper` 为 `Undefined`，点估计和无效重复诊断仍返回。有效重复值按 Binary64 投影排序，`QuantileRevision=linear-hf7-v1` 固定为 `h=(B−1)q`、`i=floor(h)`、`g=h−i`、`Q(q)=(1−g)x[i]+g*x[i+1]`，端点 q=0/1 取首/尾；q 的分子由 `ConfidencePpm` 和 `B` 的整数有理式计算，不以十进制 parse 或平台四舍五入决定索引。令 `C=ConfidencePpm/1_000_000`、`α=1−C`：`TwoSided` 使用 `Lower=Q(α/2)`、`Upper=Q(1−α/2)`；`Lower` 使用 `Lower=Q(α)`、`Upper=InfiniteValue(+∞)`；`Upper` 使用 `Lower=InfiniteValue(−∞)`、`Upper=Q(C)`。`GroupIntervalBound.State=Computed` 时 `Value` 必须是有限 double；`Undefined` 时 `Value=null`；`InfiniteValue` 时 `Value` 必须严格为 `double.NegativeInfinity` 或 `double.PositiveInfinity`，并带固定 Code。退化时双侧为 `[x,x]`、Lower 为 `[x,+∞]`、Upper 为 `[-∞,x]`，仍附 `STAT.DEGENERATE`；不返回 NaN，也不把退化区间当物理零风险或资格通过。

`InfiniteValue` 的 `Code` 固定为 `STAT.NEGATIVE_INFINITY_BOUND` 或 `STAT.POSITIVE_INFINITY_BOUND`，分别对应 `double.NegativeInfinity` 与 `double.PositiveInfinity`；其它状态不得复用这两个 Code。

取消时已开始但未完成的重复记为 `Cancelled`，其后的重复记为 `Unexecuted`；必须保持 `ExecutedRepeats + UnexecutedRepeats = Resamples`，不能把尚未执行重复全算 `Invalid`。本版要求所有 `Resamples` 均 `Valid` 才能返回区间；否则 `Lower`/`Upper` 为 `Undefined`，点估计和无效/取消重复诊断仍返回。

**确定性顺序和输出语义。** 先做预算/结构/单位/配对/整数预检，再固定排序、点估计、PRNG 重采样、有效性计数、区间排序和投影，最后按既有 drain 链交付。`IndependentGroups` 是实际完整组数；`ExecutedRepeats`、`UnexecutedRepeats`、`ValidRepeats`、`InvalidRepeats`、`CancelledRepeats`、零分母/溢出重复、失败/缺失/Unknown 组计数全部输出并满足上述守恒。任一必需组无效、覆盖不闭合或组数不足时不返回看似完整的区间；`Coverage` 与 `Diagnostics` 仍保留可定位的部分证据。点估计可计算而区间不可计算时，`Point=Computed`、边界为 `Undefined`，不能把边界 null 改成点估计或 0。

**Capabilities、Provenance 和诊断落点。** S6 的 TaskKinds（`GroupRatioTask`/`GroupPairedRatioTask`）及托管后端身份 `managed-group-percentile-bootstrap-v1` 的声明规格已接收；实际发布的 `NumericalCapabilities` 仍须在实现和相应运行资格完成后才声明可运行能力/Validated，不能凭本轮规格接收把后端标为可运行，其它模块亦不得据此宣称运行能力。每个 `GroupIntervalResult.Provenance` 是稳定公开落点，必须给出 `MethodRevision`、`PrngRevision`、`QuantileRevision`、`Seed`、`GroupOrderHash`、`PrngOutputByteHash`、`PrngOutputCount` 和 `PrngRejectionCount`；`PrngOutputCount = accepted draws + rejected draws`，不含初始化两次 output。`GroupIntervalDiagnostics` 公开独立组数、`ExecutedRepeats`、`UnexecutedRepeats`、有效/无效/取消/零分母/溢出重复、失败/缺失/Unknown 组数和诊断码，并满足 `ExecutedRepeats = ValidRepeats + InvalidRepeats + CancelledRepeats`、`ExecutedRepeats + UnexecutedRepeats = Policy.Resamples`；取消中断的当前重复计入 `CancelledRepeats`，尚未开始的重复只计 `UnexecutedRepeats`，绝不把后者批量算作 Invalid。诊断参数必须重复这些 hash/拒绝信息或明确引用该 Provenance，不能只写入隐藏日志。外层 `NumericalProvenance` 仍记录输入、闭包、选择和公共数值策略，S6 的随机流细节以 `GroupIntervalResult.Provenance` 为准。

**两个纯 BCL Host 及断言。** 不新增 csproj；唯一测试工程 `tests/Modules/statistics/Asun.Modules.Statistics.TestHost/` 须在切片获授权时创建，以两个明确模式调用同一 `StatisticsEngine`。下面是 DTO→request→engine 的最小完整接线形状（伪码中的 hash 是夹具固定值，不是运行时默认值）：

两 Host 共享下方本地夹具编码函数（位于既有 TestHost/Core.Tests，非新增公开 API/工程）；它们逐字段实现上述唯一规则。这里 hash 均由实际完整字段生成，不硬写虚构来源值。方法/选择定义的正文是代码内精确 ASCII 常量，numeric/group policy 的 Identity 绑定实际全部参数；来源包括两侧自身计数与 Coverage。Host 的 Gaps 固定为空，其编码函数对非空 Gaps 明确拒绝，仅生产实现按上方完整规则支持 Gaps。示例是待实施的调用规格，未编译/执行 C#。

~~~csharp
using System.Collections.Immutable;
using System.Security.Cryptography;
using System.Text;
using Asun.Modules.Statistics;

static void S(BinaryWriter w, string v)
{
    var bytes = new UTF8Encoding(false, true).GetBytes(v);
    w.Write(bytes.Length); w.Write(bytes);
}
static void NS(BinaryWriter w, string? v)
{
    w.Write((byte)(v is null ? 0 : 1)); if (v is not null) S(w, v);
}
static string H(string domain, Action<BinaryWriter> body)
{
    // 小型 Golden/Host 有界内存编码；生产增量 SHA-256。
    using var ms = new MemoryStream();
    using var w = new BinaryWriter(ms, Encoding.UTF8, true);
    w.Write(Encoding.ASCII.GetBytes(domain)); w.Write((byte)0);
    body(w); w.Flush();
    return Convert.ToHexString(SHA256.HashData(ms.ToArray())).ToLowerInvariant();
}
static void Ref(BinaryWriter w, DefinitionReference d)
{
    S(w, d.Id); S(w, d.Revision); S(w, d.ContentHash);
}
static DefinitionReference Definition(string id, string revision, string text)
    => new(id, revision, H("S6-DEFINITION-V1", w =>
       { S(w, id); S(w, revision); S(w, text); }));
static void Cov(BinaryWriter w, GroupCoverageEvidence c)
{
    w.Write(c.Obligations); w.Write(c.Covered); w.Write(c.NotCovered);
    w.Write(c.Failed); w.Write(c.Missing); w.Write(c.Unknown);
    w.Write(c.CrossCounts.FailureAndCovered);
    w.Write(c.CrossCounts.FailureAndNotCovered);
    w.Write(c.CrossCounts.NonFailureAndCovered);
    w.Write(c.CrossCounts.NonFailureAndNotCovered);
    w.Write(c.CrossCounts.Unknown);
}
static void ObservationBody(BinaryWriter w, GroupIntervalObservation o)
{
    S(w, o.GroupId); S(w, o.EndpointName); w.Write(o.Numerator);
    w.Write(o.Denominator); S(w, o.NumeratorUnit); S(w, o.DenominatorUnit);
    Cov(w, o.Coverage);
}
static void Obs(BinaryWriter w, GroupIntervalObservation o)
{
    ObservationBody(w, o); S(w, o.Source.ObservationId);
    S(w, o.Source.SourceRevision); S(w, o.Source.ContentHash);
    NS(w, o.Source.EvidenceReference);
}
static GroupIntervalObservation MakeObservation(
    string group, string sourceId, long numerator, long denominator,
    GroupCoverageEvidence coverage)
{
    var source = new ObservationReference(sourceId, "src-r1", "", null);
    var o = new GroupIntervalObservation(group, "governance-rate",
        numerator, denominator, "event", "opportunity", coverage, source);
    string hash = H("S6-SOURCE-V1", w =>
    {
        S(w, source.ObservationId); S(w, source.SourceRevision);
        NS(w, source.EvidenceReference); ObservationBody(w, o);
    });
    return o with { Source = source with { ContentHash = hash } };
}
static void NPBody(BinaryWriter w, NumericalPolicy p)
{
    S(w, p.Identity.Id); S(w, p.Identity.Revision);
    w.Write(p.RankAbsolute); w.Write(p.RankRelative);
    w.Write(p.DecompositionTolerance); w.Write(p.PsdTolerance);
    w.Write(p.CorrelationRoundoffTolerance); w.Write(p.TQuantileAbsolute);
    w.Write(p.TQuantileRelative); w.Write(p.FQuantileRelative);
    w.Write(p.TailRelative);
}
static void GPBody(BinaryWriter w, GroupIntervalPolicy p)
{
    S(w, p.Identity.Id); S(w, p.Identity.Revision); S(w, p.MethodRevision);
    w.Write((int)p.Tail); w.Write(p.ConfidencePpm); w.Write(p.Resamples);
    w.Write(p.Seed); w.Write(p.MinIndependentGroups);
    S(w, p.PrngRevision); S(w, p.QuantileRevision);
}
static void GB(BinaryWriter w, GroupIntervalBudget b)
{
    w.Write(b.MaxGroups); w.Write(b.MaxResamples); w.Write(b.MaxIntegerBits);
    w.Write(b.MaxPrngOutputs); w.Write(b.MaxBufferedBytes);
    w.Write(b.WallClockLimit.Ticks); w.Write(b.CancellationResponseLimit.Ticks);
    w.Write(b.DrainObservationLimit.Ticks);
}
static void NB(BinaryWriter w, NumericalBudget b)
{
    w.Write(b.MaxRows); w.Write(b.MaxGroups); w.Write(b.MaxColumns);
    w.Write(b.MaxCategories); w.Write(b.MaxTasks); w.Write(b.MaxDetailRows);
    w.Write(b.MaxDiagnostics); w.Write(b.MaxIntegerBits);
    w.Write(b.MaxBufferedBytes); w.Write(b.MaxWorkingSetBytes);
    w.Write(b.WallClockLimit.Ticks); w.Write(b.DrainObservationLimit.Ticks);
    w.Write(b.MaxNotifications);
}
static void Closure(BinaryWriter w, InputClosure c)
{
    w.Write((byte)(c.ExpectedMembers.HasValue ? 1 : 0));
    if (c.ExpectedMembers.HasValue) w.Write(c.ExpectedMembers.Value);
    NS(w, c.ExpectedMemberSetHash); w.Write(c.ReadComplete);
    w.Write(c.PopulationClosed); NS(w, c.ClosureReceiptReference);
    if (!c.Gaps.IsEmpty) throw new InvalidOperationException("Host requires empty Gaps");
    w.Write(c.Gaps.Length);
}
static void SortedRatio(BinaryWriter w, ImmutableArray<GroupIntervalObservation> g)
{
    var a = g.OrderBy(o => o.GroupId, StringComparer.Ordinal).ToArray();
    w.Write(a.Length); foreach (var o in a) Obs(w, o);
}
static void SortedPairs(BinaryWriter w, ImmutableArray<GroupPair> g)
{
    var a = g.OrderBy(o => o.GroupId, StringComparer.Ordinal).ToArray();
    w.Write(a.Length);
    foreach (var p in a)
    { S(w, p.GroupId); S(w, p.PairingKey); Obs(w, p.Left); Obs(w, p.Right); }
}
static void TaskBody(BinaryWriter w, NumericalTask task)
{
    switch (task)
    {
        case GroupRatioTask t:
            S(w, "GroupRatioTask"); S(w, t.TaskId); S(w, t.EndpointName);
            S(w, t.RatioUnit); GPBody(w, t.Policy); S(w, t.Policy.Identity.ContentHash);
            GB(w, t.Budget); SortedRatio(w, t.Groups); break;
        case GroupPairedRatioTask t:
            S(w, "GroupPairedRatioTask"); S(w, t.TaskId); S(w, t.EndpointName);
            S(w, t.LeftRole); S(w, t.RightRole); S(w, t.DifferenceUnit);
            GPBody(w, t.Policy); S(w, t.Policy.Identity.ContentHash);
            GB(w, t.Budget); SortedPairs(w, t.Groups); break;
        default: throw new InvalidOperationException("Unsupported fixture task");
    }
}
static void SnapshotBody(BinaryWriter w, NumericalRequest r)
{
    var i = r.Input;
    S(w, i.SnapshotId); S(w, i.SnapshotRevision); w.Write((int)i.Mode);
    S(w, i.QueryReceiptId); S(w, i.SourceBoundary); NS(w, i.WatermarkId);
    w.Write(i.ReadComplete); w.Write(i.CanReplay); Closure(w, r.Closure);
    Ref(w, r.Method); Ref(w, r.SelectionPolicy);
    w.Write((byte)(r.ObservedSubsetApproval is null ? 0 : 1));
    if (r.ObservedSubsetApproval is not null) Ref(w, r.ObservedSubsetApproval);
    w.Write((int)r.Completeness); NPBody(w, r.Policy);
    S(w, r.Policy.Identity.ContentHash); NB(w, r.Budget);
    w.Write(r.Tasks.Length); foreach (var t in r.Tasks) TaskBody(w, t);
}
static NumericalRequest Seal(NumericalRequest r)
    => r with { Input = r.Input with
       { ContentHash = H("S6-INPUT-V1", w => SnapshotBody(w, r)) } };
static string RequestHash(NumericalRequest r)
    => H("S6-REQUEST-V1", w =>
       { S(w, r.OperationId); SnapshotBody(w, r); S(w, r.Input.ContentHash); });
static string OrderHash(NumericalTask task) => task switch
{
    GroupRatioTask t => H("S6-GROUP-ORDER-V1", w => SortedRatio(w, t.Groups)),
    GroupPairedRatioTask t => H("S6-PAIRED-GROUP-ORDER-V1", w =>
    { S(w, t.LeftRole); S(w, t.RightRole); S(w, t.DifferenceUnit);
      SortedPairs(w, t.Groups); }),
    _ => throw new InvalidOperationException("Unsupported fixture task")
};

const string methodText =
    "independent-exchangeable-groups;equal-probability-with-replacement;" +
    "pooled-raw-integers;paired-shared-indices;left-minus-right;" +
    "pcg32-xsh-rr-v1;initseq=54;linear-hf7-v1;all-resamples-valid;" +
    "one-sided-infinite-bound;no-imputation;coverage-preserved;limits-before-draw";
const string selectionText =
    "synthetic-fixture;independent-exchangeable-group;GroupId-ordinal;" +
    "same-obligation-set-per-pair;complete-pairs;no-exclusion;no-imputation";
var method = Definition("group-percentile-bootstrap-v1", "1", methodText);
var selection = Definition("s6-independent-groups-v1", "1", selectionText);
var numeric0 = new NumericalPolicy(
    new DefinitionReference("engineering-binary64-v1", "1", ""),
    1e-14, 1e-12, 1e-10, 1e-12, 8 * Math.Pow(2, -52),
    5e-12, 5e-12, 1e-10, 1e-9);
var outerPolicy = numeric0 with { Identity = numeric0.Identity with
    { ContentHash = H("S6-NUMERIC-POLICY-V1", w => NPBody(w, numeric0)) } };
var policy0 = new GroupIntervalPolicy(
    new DefinitionReference("s6-group-policy", "1", ""),
    "group-percentile-bootstrap-v1", GroupIntervalTail.TwoSided,
    750000, 8, 42u, 2, "pcg32-xsh-rr-v1", "linear-hf7-v1");
var groupPolicy = policy0 with { Identity = policy0.Identity with
    { ContentHash = H("S6-GROUP-POLICY-V1", w => GPBody(w, policy0)) } };
var outerBudget = new NumericalBudget(
    2, 2, 1, 1, 1, 0, 64, 256, 1_048_576, 4_194_304,
    TimeSpan.FromSeconds(5), TimeSpan.FromSeconds(2), 64);
var groupBudget = new GroupIntervalBudget(
    2, 8, 256, MaxPrngOutputs: 64, MaxBufferedBytes: 1_048_576,
    WallClockLimit: TimeSpan.FromSeconds(5),
    CancellationResponseLimit: TimeSpan.FromSeconds(1),
    DrainObservationLimit: TimeSpan.FromSeconds(2));
var closure = new InputClosure(2, H("S6-MEMBER-SET-V1", w =>
    { w.Write(2); S(w, "G-A"); S(w, "G-B"); }),
    true, true, "closure-s6", ImmutableArray<InputGap>.Empty);
var leftCoverageA = new GroupCoverageEvidence(
    1, 1, 0, 0, 0, 0, new FailureCoverageCrossCounts(0, 0, 1, 0, 0));
var leftCoverageB = new GroupCoverageEvidence(
    99, 99, 0, 0, 0, 0, new FailureCoverageCrossCounts(0, 0, 99, 0, 0));
var left = ImmutableArray.Create(
    MakeObservation("G-A", "L-A", 1, 1, leftCoverageA),
    MakeObservation("G-B", "L-B", 0, 99, leftCoverageB));
var ratioTask = new GroupRatioTask("S6-RATIO-HOST-GOLDEN-001",
    "governance-rate", "ratio", groupPolicy, groupBudget, left);
var ratioRequest = Seal(new NumericalRequest("op-s6-ratio-001",
    new InputReference("snap-s6-ratio", "r1", InputMode.FixedSnapshot,
        "receipt-s6-ratio", "governance-groups", "", null, true, true),
    closure, method, selection, null, CompletenessPolicy.RequireAll,
    outerPolicy, outerBudget, ImmutableArray.Create<NumericalTask>(ratioTask)));
await using var ratioEngine = new StatisticsEngine(new EngineLimits(4, 4));
var ratioResult = ratioEngine.ComputeNumerical(ratioRequest, CancellationToken.None);
var ratioOutput = (GroupIntervalResult)ratioResult.Tasks[0];
var ratioEstimate = ratioOutput.Estimates[0];
if (ratioResult.State != ResultState.Complete ||
    ratioEstimate.Point.State != NumericalValueState.Computed ||
    ratioEstimate.Lower.State != GroupIntervalBoundState.Computed ||
    ratioEstimate.Upper.State != GroupIntervalBoundState.Computed ||
    ratioEstimate.RawTotalNumerator != 1 || ratioEstimate.RawTotalDenominator != 100 ||
    ratioEstimate.TotalNumerator != 1 || ratioEstimate.TotalDenominator != 100 ||
    ratioEstimate.Point.Value != 0.01d || ratioEstimate.Lower.Value != 0d ||
    Math.Abs(ratioEstimate.Upper.Value!.Value - 0.13375d) > 1e-15 ||
    ratioOutput.Provenance.GroupOrderHash != OrderHash(ratioTask) ||
    ratioOutput.Provenance.PrngOutputCount != 16 ||
    ratioOutput.Provenance.PrngRejectionCount != 0)
    throw new InvalidOperationException("S6-RATIO-HOST-GOLDEN-001");

// 配对右侧各有完整自身覆盖与来源；不复用左侧的 Source。
var rightCoverageA = new GroupCoverageEvidence(
    1, 1, 0, 0, 0, 0, new FailureCoverageCrossCounts(0, 0, 1, 0, 0));
var rightCoverageB = new GroupCoverageEvidence(
    99, 99, 0, 0, 0, 0, new FailureCoverageCrossCounts(0, 0, 99, 0, 0));
var right = ImmutableArray.Create(
    MakeObservation("G-A", "R-A", 0, 1, rightCoverageA),
    MakeObservation("G-B", "R-B", 1, 99, rightCoverageB));
var pairs = ImmutableArray.Create(
    new GroupPair("G-A", left[0], right[0], "pair-G-A-v1"),
    new GroupPair("G-B", left[1], right[1], "pair-G-B-v1"));
var pairedTask = new GroupPairedRatioTask("S6-PAIRED-HOST-GOLDEN-001",
    "governance-rate", "left", "right", "ratio-difference",
    groupPolicy, groupBudget, pairs);
var pairedRequest = Seal(new NumericalRequest("op-s6-paired-001",
    new InputReference("snap-s6-paired", "r1", InputMode.FixedSnapshot,
        "receipt-s6-paired", "governance-groups", "", null, true, true),
    closure, method, selection, null, CompletenessPolicy.RequireAll,
    outerPolicy, outerBudget, ImmutableArray.Create<NumericalTask>(pairedTask)));
await using var pairedEngine = new StatisticsEngine(new EngineLimits(4, 4));
var pairedResult = pairedEngine.ComputeNumerical(pairedRequest, CancellationToken.None);
var pairedOutput = (GroupIntervalResult)pairedResult.Tasks[0];
var pairedEstimate = pairedOutput.Estimates[0];
if (pairedResult.State != ResultState.Complete ||
    pairedEstimate.Point.State != NumericalValueState.Computed ||
    pairedEstimate.Lower.State != GroupIntervalBoundState.Computed ||
    pairedEstimate.Upper.State != GroupIntervalBoundState.Computed ||
    pairedEstimate.RawLeftTotalNumerator != 1 ||
    pairedEstimate.RawLeftTotalDenominator != 100 ||
    pairedEstimate.RawRightTotalNumerator != 1 ||
    pairedEstimate.RawRightTotalDenominator != 100 ||
    pairedEstimate.RawTotalNumerator != 0 || pairedEstimate.RawTotalDenominator != 10000 ||
    pairedEstimate.TotalNumerator != 0 || pairedEstimate.TotalDenominator != 1 ||
    pairedEstimate.Point.Value != 0d ||
    Math.Abs(pairedEstimate.Lower.Value!.Value + 1d / 99d) > 1e-15 ||
    Math.Abs(pairedEstimate.Upper.Value!.Value - 0.125d) > 1e-15 ||
    pairedOutput.Provenance.GroupOrderHash != OrderHash(pairedTask) ||
    pairedOutput.Provenance.PrngOutputCount != 16 ||
    pairedOutput.Provenance.PrngRejectionCount != 0)
    throw new InvalidOperationException("S6-PAIRED-HOST-GOLDEN-001");
if (ratioRequest.Input.ContentHash !=
    "c6c59c1f6df0a1be3e4c64553311027a47a9361db00ad807bc7b3ce3924b8290" ||
    RequestHash(ratioRequest) !=
    "57ea74eb757fc713907c66bd01203f1502616c0d5b00f75769626ed9e1b30502" ||
    pairedRequest.Input.ContentHash !=
    "b67555033a62d2632a72e5625beee9afbe1968578b5076afb6b16eac422c90f3" ||
    RequestHash(pairedRequest) !=
    "6f8b9588f1a8a11550b3d2fbc64120f0182b7d8c3ea46f7558b73629406a038c")
    throw new InvalidOperationException("S6-FULL-REQUEST-GOLDEN-001");
~~~

两个 Host 在调用前已经 Seal 完成，不把临时空 hash 带入 engine。S6 的一次 task 只有一个 EndpointName，结果 Estimates 正常为一个；task 与其所有观察 EndpointName 必须一致。这里 numerator 的 event 单位是一般计数，不把它等同于 Coverage.Failed；覆盖交叉表描述义务执行失败，保留独立统计语义。两来源可同组同义务而内容不同。其它 BCL namespaces（System、System.IO、System.Linq、System.Threading 等）由固定 Microsoft.NET.Sdk ImplicitUsings 提供。

**完整字段 Golden（本节 2026-10-11 修订）。** 以下长度包含一次域头与所有字段；PRNG 两行是纯输出字节，无域头。值由上述完整夹具逐字段重建，是文档编码核对，未执行 C# Host。原部分字段 hash 已替换，不混用旧引用。

| 对象 | bytes | SHA-256 |
|---|---:|---|
| method | 322 | `107e8a65e2bae817a7d2d362a713db01dc276f51c81f18319c0036529b38bbef` |
| selection | 189 | `54ea32701510afa799515fef28bacb844936b9685d18a7ae5be1f945b97b2c80` |
| numericPolicy | 125 | `8d21d209379633eb385bcac2d80f339405561abe4e07ce6927c96c240b160bf8` |
| groupPolicy | 132 | `9fe8efa003c509e21ef08f11df7e3c218d8f4dc83c875316e198969f691a729a` |
| memberSet | 35 | `088921f65c33bc27dfb4ec9c91aebbcefd9140e0506a78e7483582dcd84ca130` |
| L-A | 185 | `1bea46369b2cfce134047382e29965a039f86e15f58c67cb1644ba10a55ea4e6` |
| L-B | 185 | `12b5997377123c13bfc0f2442c424977f22dae1f77ab2977acbf3559c7ac9ab9` |
| R-A | 185 | `6447d77100d30f241687674f4c0438f4a7e35b62ad1725940a8092d4e470d755` |
| R-B | 185 | `bbba1f736060d196a9f91ffb9ea9aa24ac8861309529ae59a00cd5a2257cf12e` |
| ratioOrder | 502 | `55fe8a9ec157a41015838343bdd6d93ab247bc3461901e728891ce3081fffdde` |
| pairedOrder | 1070 | `5f0f981b430d3fa5cb113ec14ec8624971ec4be98c01ad11966dd2c0d0843611` |
| ratioInput | 1429 | `c6c59c1f6df0a1be3e4c64553311027a47a9361db00ad807bc7b3ce3924b8290` |
| ratioRequest | 1518 | `57ea74eb757fc713907c66bd01203f1502616c0d5b00f75769626ed9e1b30502` |
| pairedInput | 1990 | `b67555033a62d2632a72e5625beee9afbe1968578b5076afb6b16eac422c90f3` |
| pairedRequest | 2080 | `6f8b9588f1a8a11550b3d2fbc64120f0182b7d8c3ea46f7558b73629406a038c` |
| g3Outputs | 12 | `443998650ccef99f67ffc3128735e6385383d8014a524f360e7a712ef4d01a43` |
| g3Budget2 | 8 | `af5570f5a1810b7af78caf4bc70a660f0df51e42baf91d4de5b2328de0e83dfc` |

Host 须断言上述 method/selection/policy/member/source/order/input/request 长度与 hash，并逐项扰动一个字段（包括右侧计数、Source.EvidenceReference、置信度、seed、MaxPrngOutputs）核对相关 hash 改变；不以只重放预写 hex 代替按字段构造。g3Outputs 的完整12-byte hex 为 `0000000000000000938bc247`；g3Budget2 为 `0000000000000000`，两个拒绝输出都在 hash 内。ratio/paired 的 PRNG 内容仍是既有 64-byte Golden，与各自输入/order hash 区分。

1. 治理比例 Host：组 A=`1/1`、组 B=`0/99`，覆盖交叉计数均完整，`ConfidencePpm=750000`、`Resamples=8`、`Seed=42`、`MinIndependentGroups=2`。固定 PCG 输出前 16 个值为 `a15c02b7 7b47f409 ba1d3330 83d2f293 bfa4784b cbed606e bfc6a3ad 812fff6d e61f305a f9384b90 32db86fe 1dc035f9 ed786826 3822441d 2ba113d7 1c5b818b`，索引为 `1,1,0,1,1,0,1,1,0,0,0,1,0,1,1,1`。这 64 个 little-endian 输出字节的 `PrngOutputByteHash` 为 `7a40659e59745b6adacf411f7830b57137b8758f0bda4c6afd0ca709cc0945c8`。点估计精确为 `1/100`；排序后的重复值为 `[0,0,0,1/100,1/100,1/100,1/100,1]`；线性 q=.125/.875 区间为 `[0,0.13375]`（Binary64 投影）。
2. 通用配对 Host：左侧仍为 A/B，右侧组 A=`0/1`、组 B=`1/99`，同一 `GroupId`/义务/索引，差值定义 `left−right`。点估计为 `0`；八个重复差值排序为 `[-1/99,-1/99,-1/99,0,0,0,0,1]`；q=.125/.875 区间为 `[-1/99,0.125]`，输出 Coverage、共同失败/覆盖诊断和共享 PRNG hash。两 Host 均使用 `Microsoft.NET.Sdk`、`net10.0`、`OutputType=Exe`、BCL，仅作为现有 TestHost/Core.Tests 的调用模式；不创建第二测试工程或产品页面。

**S6 小型 Golden、错误和关闭断言。** 必须把上述两 Host 向量以及以下情况绑定稳定用例 ID：空组/组数低于2→`STAT.INDEPENDENT_GROUPS_INSUFFICIENT`；零分母→保留组、`STAT.DENOMINATOR_UNKNOWN`、无区间；一侧配对缺组/义务不等→`STAT.PAIR_INCOMPLETE`；任一交叉计数不守恒→接纳前拒绝；所有重复相同→`[x,x]`+`STAT.DEGENERATE`；任一重复无效→区间 Undefined、无效重复数准确；seed/组排序/批预算变更→新方法或新操作身份；取消/截止→保留 `Draining`，不返还仍在归约的缓冲；确认资源归还后唯一 DrainCompleted→唯一终态→Completion→通知流关闭，沿 §6 的既定顺序。每个断言输出用例 ID、expected/actual；失败、未完成、必需跳过和超时均返回非零，沿 §12.1 的唯一 Exe 命令执行。

S6 的 Closure.ExpectedMembers、NumericalCoverage.Expected/Included 和 NumericalBudget.MaxRows 都以独立组计，配对的左右观察不作为两倍独立样本；完整夹具两组对应2，完整性计数与每组义务覆盖/失败诊断分开。`FailedGroups`/`MissingGroups`/`UnknownGroups` 是存在相应计数>0的组数，配对按任一侧存在计一次，不把左右数相加当独立组数。`InvalidRepeats` 包含 ZeroDenominator、InvalidInput、Overflow、BudgetExceeded；对应原因互斥计一次，零分母/溢出是其子计数。取消重复单独计 Cancelled，执行/未执行守恒不变。尚未开始重采样就发现零分母/组数不足时 Executed=0、Unexecuted=B，点计数仍保留，不造B个非法重复。

恢复/Owner 断言沿原 §6/§7.1.3.2：接纳前结构、hash、预算拒绝不产生 run；接纳后算法错误返回明确任务诊断，资源确认释放后才产生 Failed 终态。同步 S6 是纯 managed 栈内调用，返回前释放局部 scratch，调用 token 已取消时不得开始重采样。异步 Host 在调用前把 engine、完整封闭 request 和接纳 ValueTask 放入进程根的有界 Owner 槽；接纳后强持原 NumericalRun/Completion，调用 `CancelAsync` 只是取消意图，观察超时不释放 run/engine/请求引用、不启动相同计算副本。墙钟到期按 TimedOut 意图走 drain；观察取消/截止只结束该次等待，根 Owner 用独立有限等待继续查询原 OperationId/原 Completion，未确认仍在槽内隔离。退出/异常也不以方法离栈证明排空；根最终确认 Completion 与 DisposeAsync 实际完成后释放槽，清理异常单独诊断不覆盖原业务错误。迟到完成仅归原 run，确认资源已归还后形成原终态，不进入新请求。S6 没有 native/设备/隐藏窗口资源；Core 拥有 PRNG、hash、数组和工作任务，宿主拥有 engine/run 和输入引用的保留期。

必要用例补入既有 Core.Tests：`S6-BOUNDED-G3-REJECTION-001` 与 draw预算=2/3边界；`S6-RAW-REDUCED-001`（原始2/200、约分1/100）；完整 hash 的逐字段扰动；`S6-CANCEL-DRAIN-001` 用确定性闩锁在首个重复内/两个已完成重复之间/排序中分别取消，断言已执行与未执行守恒；超时/晚完成/释放失败只使用可控制BCL测试闩锁，不用概率或 sleep 碰运气。测试闩锁为内部测试能力，不开放替换生产随机流。失败、取消、预算用例均验证原 run 只发一次 drain/终态且无未释放 scratch。真正运行和 P50/P95/P99/排空时限验证仍待实现；本轮未执行 C#、没有运行通过结论。

**BenchmarkProfile 绑定。** §13 的模块固定测点新增 `G`（独立组数）、`B`（重采样次数）、最大组整数位数、无效重复率、排序/归约/分位耗时、当前/峰值 buffer、P50/P95/P99 和完整排空时间；至少覆盖 G=2/10^2/10^4、B=2/10^3/10^4、零分母/失败覆盖/退化/取消/预算拒绝。结果按 nearest-rank 只用于性能报告，不能把 interval percentile 与性能分位混用。没有真实消费者 Profile 时写 `TargetPending`/`NotEvaluated`；本节不编造性能阈值，也不把合成 Host 或 SciPy 对照当作生产证据。

<a id="constant-ratio-deming"></a>
#### 7.1.3.10 常方差比 Deming 点估计（S7，ModuleCoreImplementationReady，仅规格准备）

**范围、版本与六项定位。** 本切片于2026-10-11为真实消费者 qualification §6.4/A.3.1 的 ConstantRatioDeming 补专用数值入口，第二消费者为无UI工程比对 console；只算无权重、独立配对、两侧误差不相关、方差恒定且误差比已知的点估计。消费者 Owner 证明这些假设并冻结配对/误差比来源；Core 不估计误差比、证明假设、发布修正、写原读数或授予质量资格。不支持 CI/标准误、bootstrap、加权/异方差/重复测量/相关误差 Deming、Passing–Bablok 或通用 ODR。纯数值不是视觉事务，不适用 HALCON 路线，不接 AsunImage。S1–S4/S6 接收与 S6 全部17 Golden/PCG/编码原文保持；S7 六项文档规格于2026-10-11由主控接收为 ModuleCoreImplementationReady（仅规格准备），未实施。

新增封闭 task tag 为 String `ConstantRatioDemingTask`，task schema `deming-s7-task-v1`，方法 `constant-ratio-deming-exact-center-v1`，后端身份规划 `managed-deming-exact-center-v1`；它们是 Core API 0.3 的独立扩展能力，不重解释 PairTask/AffineTask/任何旧 tag，也不改变旧 family 的输入/Golden。S7 请求只包含 S7 tasks；首发禁止与旧 family 混投同一 NumericalRequest，接纳前 METHOD_UNSUPPORTED，消费者拆成具名操作。实现包添加能力的 SemVer/BuildHash 在实际发布时记录，旧包未知 tag 明确拒绝，不据同为0.3猜支持。NumericalCapabilities 仅在本切片接收、实际实现及运行资格完成后声明可运行，不据文档出现 tag 冒充后端存在。

DEV-GOV-010 §3.1 六项位置：①本段范围/两个消费者；②下方完整 DTO/单位/有效域/算法/错误/执行根；③下方两个 BCL Host；④逐字段编码/完整 Golden/解析与异常断言；⑤下方 BenchmarkProfile 及 §13 的资源/目标口径；⑥复用本文开头唯一 Core/Core.Tests/TestHost 工程、§12.1 的唯一构建/Exe执行约定与下面调用顺序。只允许本指导写入；不新增工程/源码/报告/脚本/依赖。

**主控接收与证据（2026-10-11）。** 主控已回读本节DTO、支持域、单位变换、精确中心矩/稳定白化根、RNE投影、双Host、原Task根、D7-001–022、Benchmark及六项位置，接收为ModuleCoreImplementationReady（仅规格准备）。主控按字段独立构造定义/Policy/MemberSet/12来源/两Pairs/Task/Input/Request共25项，长度/hash一致；normal/swap完整请求为2011/1979 bytes。另构造normal Expected的145 bytes完整hex/hash一致，共26项独立复核，不与本模块此前27项重建口径混算。主控Fraction/100位Decimal复算含噪λ=1、4、0.25、极端偏置矩与中心；D7-011围绕7/3的实际归一化d=+2^-52/0/−2^-52亦独立复算一致。上述是文档字段与数学复核，未执行产品后端；Core实现、真实BuildHash/后端、Golden运行、Benchmark及客户物理资格仍另门。CI、加权/异方差/相关误差与通用ODR不扩范围；本入口λ仍为Y误差方差/X误差方差，外部mcr对照才取倒比，不用OLS替代。

**定向依据与采纳。** 本轮实际读取 [SciPy 1.16.2 官方 ODR 文档](https://docs.scipy.org/doc/scipy-1.16.2/reference/odr.html)：两侧有测量误差时 OLS 固定解释变量的前提不成立，wd/we 为误差方差倒数。它引用 Boggs/Rogers 1990 和 NIST ODRPACK；采用双侧误差模型与明确方差权重含义，不接 Python/NumPy/Fortran 或迭代 ODR，不能把非线性一般 ODR 的运行资格移给本闭式点估计。NIST [ODRPACK User's Reference Guide 2.01 / NISTIR 4834](https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir4834.pdf) 本次 HTTP403；Dataplot旧 Deming 链接重定向至ITL首页，未读到公式正文，不声称 NIST 公式/测试已核实，不再无界重试。

mcr 固定为 CRAN 1.3.3.1、commit `3d72540bf23a60eb7980ffb58da0f173f749a61c`，GPL≥3，R≥3.0、parallel/robslopes，Imports stats/graphics/grDevices/methods，NeedsCompilation=yes。本轮实际读取：
- [src/calcRegression.c](https://github.com/cran/mcr/blob/3d72540bf23a60eb7980ffb58da0f173f749a61c/src/calcRegression.c) calc_Deming 的 mean/u/q/p、闭式斜率与原零点截距；SHA-256 `e7dc269ee60f7ca4662759a697f20f4bd6fddb919bed962c3726cea2023d8a53`。
- [R/mcDeming.r](https://github.com/cran/mcr/blob/3d72540bf23a60eb7980ffb58da0f173f749a61c/R/mcDeming.r) 的非空/同长/非NA/正 error.ratio 验证、mode=0 native调用与许可文字；SHA-256 `e92fa1aa0b8d52d1e2caa40c79e6ba8f578e8a458b789b43948f32005a680ab9`。
- [inst/unitTests/runit.mcDeming.R](https://github.com/cran/mcr/blob/3d72540bf23a60eb7980ffb58da0f173f749a61c/inst/unitTests/runit.mcDeming.R) 的空比值、0、NA、字符串异常断言及 creatinine 的 b0=-0.05891341、b1=1.054539、xw=1.221111（ratio=1、tolerance=10e-7）；SHA-256 `c2b29d0330006c6ef56b708ac4aad48a8e476ce1a06c3e038a35b87cfa39f3e6`。其测试先 complete.cases，不能移植为本模块静默删行；它不提供本任务极端尺度/取消/完整性证据，未执行上游测试。
- [DESCRIPTION](https://github.com/cran/mcr/blob/3d72540bf23a60eb7980ffb58da0f173f749a61c/DESCRIPTION) SHA-256 `99dba8c58321dce618c9dffd7bd630c99022574624b885d1b386b9e27fc648e0`，版本/依赖/许可核对；[mc.deming.Rd](https://github.com/cran/mcr/blob/3d72540bf23a60eb7980ffb58da0f173f749a61c/man/mc.deming.Rd) 说明 X=reference、Y=test、比值为 reference/test。

源码实际公式使用 mcr ratio=`Var(error_X)/Var(error_Y)`，不是本切片的 Y/X；对照必须传 `1/ErrorVarianceRatio`。采用其闭式数学与真实测试的输入/正常断言思想；不复制GPL代码、R/native依赖、standard-error或weighted分支，也不接原公式的普通累加/平方开根/相消路径。BCL 独立实现精确 dyadic 中心累计、两次幂归一化和稳定根，针对本支持域另验；mcr 只作正常域外部 oracle，不能作为极端域生产证明。没有下载/修改参考原件，不阻断授权开发做许可确认。

**公开 DTO 与唯一入口（namespace Asun.Modules.Statistics）。**

~~~csharp
public sealed record DemingObservation(
    NumericalMember Member, string Unit, double? Value);
public sealed record DemingPairRow(
    string PairId, DemingObservation Left, DemingObservation Right,
    string? ClusterKey);
public sealed record ConstantRatioDemingTask(
    string TaskId, string XRole, string YRole, string XUnit, string YUnit,
    double CenterX, double ErrorVarianceRatio,
    DefinitionReference Method, DefinitionReference PairingPolicy,
    DefinitionReference ErrorVarianceEvidence,
    ImmutableArray<DemingPairRow> Rows, bool ReturnDetails)
    : NumericalTask(TaskId);

public enum DemingLineKind {
    NotEvaluated = 0, Finite = 1, Horizontal = 2, Vertical = 3,
    Unidentified = 4
}
// 精确量的可复核尺度投影，不把原尺度 overflow 当矩不存在。
public sealed record DemingScaledValue(
    NumericalValueState State, double? Mantissa, int? Exponent2,
    string Unit, string? Code);
public sealed record DemingCenteredMoments(
    long Count, double? AnchorX, double? AnchorY,
    NumericalValue MeanX, NumericalValue MeanY,
    DemingScaledValue MeanOffsetX, DemingScaledValue MeanOffsetY,
    DemingScaledValue Sxx, DemingScaledValue Syy, DemingScaledValue Sxy);
public sealed record DemingDiagnostics(
    string MethodRevision, int? ScaleExponentX, int? ScaleExponentY,
    double? NormalizedErrorVarianceRatio, double? Correlation,
    double? RelativeEigenGap, string? RootBranch,
    int PeakIntegerBits, long PairsVisited, string PairSequenceHash,
    BackendIdentity Backend);
public sealed record DemingPointDetail(
    string PairId, NumericalValue CenteredX, NumericalValue CenteredY,
    NumericalValue PredictedY, NumericalValue VerticalResidual);
public sealed record ConstantRatioDemingResult(
    string TaskId, NumericalCoverage Coverage,
    ImmutableArray<Diagnostic> Diagnostics,
    NumericalCoverage LeftCoverage, NumericalCoverage RightCoverage,
    DefinitionReference Method, DefinitionReference PairingPolicy,
    DefinitionReference ErrorVarianceEvidence,
    double ErrorVarianceRatio, double CenterX, DemingLineKind LineKind,
    DemingCenteredMoments Moments, NumericalValue Slope,
    NumericalValue CenterIntercept, DemingDiagnostics Computation,
    ImmutableArray<DemingPointDetail> Details)
    : NumericalTaskResult(TaskId, Coverage, Diagnostics);
~~~

沿 `NumericalRequest`（显式 NumericalPolicy/NumericalBudget/Input/Closure/Method/SelectionPolicy/Completeness）→`ComputeNumerical` 或 `ComputeNumericalAsync`→同一 NumericalResult.Tasks 中的 ConstantRatioDemingResult；不用 Pearson 提取极端尺度中心矩，也不造第二引擎/运行根。外层 Method 必须等于该单方法请求每个 task.Method，NumericPolicy 固定 §7.1.3.1 的 engineering-binary64-v1 参数；ErrorVarianceEvidence/PairingPolicy 由消费者显式给内容引用。没有默认ratio=1/CenterX=0。ReturnDetails=false 时 Details 空；true 时预检 Included≤MaxDetailRows，不足接纳前拒绝，不截断明细。Budget 参数继续外层固定有效域，MaxIntegerBits 最小128最高4096，WallClockLimit/DrainObservationLimit等来自请求；禁止 ambient/provider 参数或后台自动选择方法。

**单位、比值方向、预检与完整性。** x=Left/XRole，y=Right/YRole；关系是 `y = CenterIntercept + Slope*(x-CenterX)`，CenterX/X/MeanX/MeanOffsetX 是 XUnit，Y/CenterIntercept/残差是 YUnit，Slope=YUnit/XUnit，Sxx=XUnit²、Syy=YUnit²、Sxy=XUnit·YUnit。每侧 Unit 必须逐行等于 task 冻结单位，角色不同，PairId/每侧 Member.RowId/每侧 Source.ObservationId 唯一且非空，来源revision/hash齐全；同 ID 重复即使同内容也拒绝，不增 n。完整来源/实际配对由消费者外连接决定，不按行位置 zip。两侧状态/ReasonCode 逐一保留；Valid 有有限 Value，非Valid 的 Value=null，不拿 NaN 编状态。ClusterKey 非null表示有未建模的相关组，首发拒绝推断为 METHOD_UNSUPPORTED，保留覆盖，不能把多个行当独立 n。

`λ=ErrorVarianceRatio=Var(error_y)/Var(error_x)`，是**方差**比，不是标准差比；数值单位 YUnit²/XUnit²。即便同一物理量不同单位，λ也须按传入数值单位冻结。正线性单位换算 x'=a*x+c、y'=b*y+d（a,b>0）必须由外部量值Owner先实施：λ'=(b/a)²λ、CenterX'=a*CenterX+c、Slope'=(b/a)Slope、CenterIntercept'=b*CenterIntercept+d；源/输入/方法引用形成新修订。负尺度/非线性换算不在首发范围，Core 不按显示文字换算。调换X/Y需新任务/来源/角色、λ'=1/λ，并显式另定 CenterX；可识别非零有限斜率互为倒数，不是同数据改标签。

Closure/Expected/Included 按 PairId 计，LeftCoverage/RightCoverage 分别按侧State，task.Coverage 用每pair双侧最严重状态唯一归类，优先 Invalid→Missing→Unmeasured→Unknown→Excluded→NotApplicable→Valid；未提供pair由原Closure.Gaps逐项证明，每个缺失PairId只登记一个Gap，Expected与实际行/缺口守恒，不在两侧重复加总。RequireAll 有任一缺对/非Valid/Gap 时 Moments.Count=0，均值/矩/系数为 Undefined/STAT.INPUT_INCOMPLETE，不拿有效子集冒全总体；ApprovedObservedSubset 必须显式批准、固定所选完整有效对子、保留全覆盖/Partial及源引用，不能各侧分别删行。n=0均值/矩 Undefined；n=1可给均值/零中心矩、系数 InsufficientData，n≥2只是数值最小，不是客户有效样本量。未提供方法、误差比证据、未知枚举/类型/default数组/数值非法在Accepted前拒绝。合法不支持的数值域返回 UnsupportedDomain/STAT.NUMERIC_DOMAIN，不静默换OLS；数值任务 Complete 只表示输入已处理，不代表可识别或资格通过。

**冻结支持域与稳定处理（唯一算法）。** 支持 n≤1,000,000并受 MaxRows；每个非零X/Y/CenterX 的 |value|∈[2^-400,2^400]（零允许），λ∈[2^-256,2^256]且有限>0。域外不声称double全域。先按PairId StringComparer.Ordinal 固定序；统计及取消顺序不随线程调度变。初始复制/排序/来源/closure核对→按完整有效pair抽取→精确中心累计→支持门→白化2×2主方向稳定根→反尺度系数/中心截距→有界逐对明细→诊断/排空。所有内存/计数/位数预算先验；只用BCL，不需矩阵/Beta/native后端。

1. 将每个 binary64 精确解码为有符号BigInteger significand×2^exponent（normal含隐含bit，subnormal按2^-1074），不把decimal字符串作为数学原值。每侧以第一个完整pair的X/Y为Anchor；每个 `dXi=Xi-AnchorX`、`dYi=Yi-AnchorY` 在精确 dyadic 上相减。先按最小二进制指数对齐，再在每步加法/乘法后显式核 abs(BigInteger).GetBitLength()≤MaxIntegerBits（零0，符号不计；checked BigInteger不会自限）；超限RangeLoss。需要的整数 scratch/对齐位也入预算，不能先舍入残差。
2. 有两遍固定序：第一遍精确 ΣdX/ΣdY 及最大abs差；第二遍精确 ΣdX²/ΣdY²/ΣdXdY。均值为 Anchor+Σd/n。中心量 `Sxx=(n*ΣdX²-(ΣdX)²)/n`、`Syy=(n*ΣdY²-(ΣdY)²)/n`、`Sxy=(n*ΣdXdY-ΣdXΣdY)/n`，这些等式只在锚点差的**精确整数/有理数**上执行，禁止原尺度浮点 Σx²−(Σx)²/n。n/mean/moments取完整同一pair子集；不组合Pearson四舍五入结果。每侧非零锚点差的 exponent spread≤128（max ILogB(abs d)−min），超过域返回UnsupportedDomain而不是抹掉小差。
3. 输出 MeanX/MeanY 是精确均值最近偶数binary64投影；MeanOffsetX/Y 独立保留精确 SumD/n 的尺度投影，不能用 `MeanX-AnchorX` 恢复它。每个非零尺度量按 `value=m*2^e`，1≤|m|<2、e为int、m最近偶数投影（若舍入为2则m/2、e+1）；零m=0/e=0。不在这里强转原尺度中心矩：巨大Sxx仍有有限mantissa+exponent，原尺度downstream强转overflow必须报RangeLoss；资格消费者应使用本ScaledValue，不能以普通double恢复极端矩。ValueState Computed只表示该尺度表示可靠，Undefined等无mantissa/exponent。
4. 若Sxx=Syy=0，LineKind=Unidentified；Sxy=0时先精确比较 `D=Syy−λ*Sxx`：D>0为Vertical，D<0为Horizontal，D=0为Unidentified（白化散布各向同性）；两系数均Undefined/STAT.DEMING_UNIDENTIFIABLE，不默认水平0或斜率∞。这与qualification当前Sxy=0斜率Unavailable一致；水平/垂直分类是数学方向诊断，不当可用拟合系数。常量X且Y变动属于Vertical，常量Y且X变动属于Horizontal；不得除零或根据符号0挑根。
5. 非零Sxy时，令 ex=ILogB(max|dX|)、ey=ILogB(max|dY|)，`U=Sxx/2^(2ex)`、`V=Syy/2^(2ey)`、`W=Sxy/2^(ex+ey)` 从精确有理量一次最近偶数投影；`λn=λ*2^(2ex−2ey)` 保留指数并核 [2^-128,2^128]，再投影。U/V应正且有限；W不得非零被投影为0，否则RangeLoss。PSD关系 `Sxx*Syy−Sxy²>=0` 先精确核，负则EvaluationFailed；`ρ=W/(sqrt(U)*sqrt(V))`，合法有限且 |ρ|≤1+CorrelationRoundoffTolerance，仅此浮点容差内越界可归±1；0<|ρ|<2^-40或不确定白化间隙走NumericUncertain，不能给不稳斜率。
6. 令 `a=λn*U, b=V, c=sqrt(λn)*W`，共同除 `max(a,b,|c|)` 后形成有限2×2矩阵，`d=b−a`（不在原大尺度相减）、`h=hypot(d,2c)`。hypot固定：p=max(|d|,|2c|)，p=0则0，否则 `p*sqrt((d/p)²+(2c/p)²)`；中间位在此归一化域。相对eigen gap=`h/(a+b)`；≤2^-40→NumericUncertain/STAT.NUMERIC_UNCERTAIN（恰等也拒绝），不把几乎圆形散布指定方向。d≥0稳定根 `t=(d+h)/(2c)`；d<0用等价无相消根 `t=2c/(h−d)`。它是主方向的白化斜率，sign(t)=sign(W)；`βn=sqrt(λn)*t`、`β=βn*2^(ey−ex)`。RootBranch固定为 `direct-positive-d`/`rationalized-negative-d`；禁止一直用 d+h 在负d处相消、禁止选另一个负/倒数根或OLS近似。对归一化beta核二次方程 `W*βn²+(λn U−V)*βn−λn W=0` 的缩放相对残差≤1e-10（各项先共同尺度再算），超出EvaluationFailed；这是算法残差门，不是客户公差或全域精度证明。
7. β反尺度到binary64非有限、非零变0→Slope RangeLoss，不返回∞或0；中心截距依赖Slope不得假Computed。CenterX 与meanX的精确位移若 `|CenterX−meanX|/2^ex >2^40`，Slope可保留，CenterIntercept UnsupportedDomain（避免无限量程外外推）。否则中心截距用精确meanY/meanX有理量及**已返回β的精确binary64值**计算 `aCenter=meanY−β*(meanX−CenterX)` 后一次最近偶数投影，取消相消影响，不声称消除β误差。中心截距的点值不是原零点截距，Core不额外返回不稳原零点值；源量化已经把不同实值变成相同binary64时只识别常量/退化，不能从double推测丢失的物理方差。
8. ReturnDetails时每对的CenteredX=Xi−CenterX、CenteredY=Yi−精确meanY、PredictedY=aCenter+β*(Xi−CenterX)、VerticalResidual=Yi−PredictedY 用精确有理/已发布β与aCenter一次投影；这是**垂直**描述残差，不是Deming正交距离、量测误差或校正。系数Undefined/Unsupported时PredictedY/Residual继承不可算状态，仍保留PairId以及能算的中心量；明细某值投影RangeLoss单项保留，不清空其它结果。极端投影、预算或取消不得返回前N条冒完整。
9. 同步返回前局部资源已释放，异步进入原 §6/§7.1.3.2 根：token/墙钟在每pair解码/位对齐、中心累计、归约、root前后与detail检查，纯managed无native不可中断段。停止意图→Draining，真实释放→唯一DrainCompleted→唯一终态→Completion→通知关闭。异步owner启动前保留engine/request与接纳Task的Owner槽位，返回ValueTask立即且仅一次AsTask保存，等待前强持该Task，接纳后强持NumericalRun/Completion；等待超时不Dispose/返池/换OperationId并发重试，独立有限cleanup/原查询保持原根。Mean/moment部分结果只允许以明确Cancelled/TimedOut诊断交付，不将未处理pair当0；PairsVisited与全覆盖分开，物理输入完整不等于计算完成。

新增键 `STAT.DEMING_UNIDENTIFIABLE`、`STAT.DEMING_RATIO_INVALID`（结构ratio≤0/非有限，接纳前）、`STAT.DEMING_PAIR_INVALID`；其余复用 STAT.NUMERIC_DOMAIN/RANGE_LOSS/NUMERIC_UNCERTAIN/EVALUATION_FAILED/BUDGET_EXCEEDED/CANCELLED/TIMEOUT/INPUT_INCOMPLETE/IDENTITY_CONFLICT。Diagnostic.MetricId=TaskId，参数给PairId/侧/阶段、n/位数/尺度/ratio/gap/root/原因，外部不泄露内部异常类型或BigInteger实现对象。结果 Computation 与外层 NumericalProvenance 保留后端/方法/hash；缺 BuildHash 不编造，Backend.Validation=Unverified至真实资格通过。模块无UI/无隐藏窗口，消息键仍由宿主三语资源呈现。

S7 BackendIdentity.Id=managed-deming-exact-center-v1、Version=1、FloatingPointProfile=exact-dyadic-binary64-rne-no-fma-v1、Interruptible=true；二元运算按正文标量顺序执行，不使用隐式/显式FMA或并行归约改变结果。SourceCommit/BuildHash来自实际Core源码/发布构建，不能写mcr commit或示例假值。Validation在完整实际数值资格前为Unverified，运行Golden核真实身份不等于自行Validated。


**逐字段身份与完整小 Golden。** 编码原语只复用 S6 s6-field-encoding-v1 的 String/nullable/Int32/Int64/double/bool/数组/域头，不修改它或任一旧域。S7 新域与版本 `S7-DEMING-TASK-V1\0`、`S7-DEMING-SOURCE-V1\0`、`S7-DEMING-DEFINITION-V1\0`、`S7-DEMING-POLICY-V1\0`、`S7-DEMING-INPUT-V1\0`、`S7-DEMING-REQUEST-V1\0`、`S7-DEMING-PAIR-SEQUENCE-V1\0`；域一次在流开头，nullable Value是byte presence+double位，State为 §3 ObservationState Int32（Valid=0/Unknown=1/Missing=2/Unmeasured=3/Invalid=4/NotApplicable=5/Excluded=6）。不得更改S6 tag/域、在其SnapshotBody闭包插入S7或沿旧schema混投；Core使用明确family+revision分派本独立编码。

- SourceBody字段顺序：PairId、role（x/y）、Member.RowId、Source.ObservationId、Source.SourceRevision、Source.EvidenceReference(nullable)、Member.State、Member.ReasonCode(nullable)、Unit、Value(nullable)。Source.ContentHash=新SOURCE域+该body，不含自身；同一来源id不同内容拒绝。Observation写Member.RowId、Source全4字段（ObservationId、SourceRevision、ContentHash、EvidenceReference）、State、ReasonCode、Unit、Value。Pair写PairId、Left Observation、Right Observation、ClusterKey(nullable)。按PairId Ordinal排序，严格UTF8/UTF16规则沿S6；其中不可把cluster缺失写成空串。
- Definition hash：新DEFINITION域 + Id/Revision/完整ASCII正文String；Policy hash：新POLICY域 + Identity.Id/Revision + NumericPolicy的9个double（同原顺序），不含自身hash，引用时Body后加完整hash。不只hash名称或revision。
- Task字段顺序：schema String=`deming-s7-task-v1`，tag String=`ConstantRatioDemingTask`，TaskId、XRole、YRole、XUnit、YUnit、CenterX、ErrorVarianceRatio、Method/PairingPolicy/ErrorVarianceEvidence各完整DefinitionReference，Rows(count+完整排序Pair)、ReturnDetails。Task hash包含全部字段；PairSequenceHash是新PAIR-SEQUENCE域+Rows，不替代完整task hash。
- InputBody：InputReference的SnapshotId、SnapshotRevision、Mode、QueryReceiptId、SourceBoundary、WatermarkId(nullable)、ReadComplete、CanReplay（排除自身ContentHash），Closure（全字段，见S6原语）、Method、SelectionPolicy、ObservedSubsetApproval(nullable)、Completeness、完整NumericPolicy（Id/Rev+9double+hash）、完整NumericalBudget、Tasks(count+上述完整Task)。Input.ContentHash是新INPUT域+InputBody；来源与方法/预算绑定，不与产品原始snapshot hash冒同一用途，宿主保留原来源引用另建确定派生snapshot。
- Request Golden：新REQUEST域+OperationId+InputBody+Input.ContentHash，避免自引用；新operation/λ/单位/CenterX/来源/选择/预算变化都进入身份。MemberSequenceHash沿Core原计算序列语义，Computation.PairSequenceHash公开提供本slice精确配对序列身份，不把它强行等于qualification QLMS。
- Expected point Golden另用 `S7-DEMING-EXPECTED-V1\0` + n(Int64)、CenterX、λ、MeanX、MeanY、Sxx/Syy/Sxy各mantissa(double)+exponent(Int32)、LineKind(Int32)、Slope State(Int32沿NumericalValueState)/Value(nullable)/Unit/Code(nullable)、CenterIntercept同结构。该Golden是可判定数值投影，不是完整运行NumericalResult序列化，不缺method/source绑定，因为完整Task/Input/Request单独闭合；运行后端BuildHash/快照ID由实际实现另验。



**精确投影、状态和预算细则。** n<2在方向步骤4之前返回：n=0不选Anchor，均值/offset/矩Undefined，两系数InsufficientData；n=1可给Anchor/均值及零offset/矩，两系数InsufficientData；两者LineKind=NotEvaluated、RootBranch/ScaleExponent/NormalizedRatio/Correlation/Gap=null，不拿单点零矩进入Unidentified分支。下述归一化/根仅对n≥2执行。ρ的舍入边界处理只影响诊断，不改U/V/W或拟合根，不提供推断资格。

上述“一次最近偶数”按有符号 p/q·2^k（q>0）实现，不用 (double)p/(double)q。先规范dyadic尾零与有理分母符号；对abs(p)、q的bit length作候选比指数，用有界移位后的整数比较修正 floor(log2(abs(p)/q))，得到e=k+该指数。尺度投影将有理量归一到[1,2)，用BigInteger.DivRem在2^52网格上得整数Q/余数R；2R>除数或2R=除数且Q为奇数则Q+1，符号最后恢复，Q=2^53时指数进位。所有对齐/2R/DivRem暂存仍核位和字节预算，不能以投影阶段为例外。普通binary64投影normal按同一53位规则；subnormal用2^-1074网格并按同一tie-even舍入，跨最小normal时正常进位；非零变0/指数超1023是RangeLoss。零固定+0；本域输入不含subnormal，但复用投影核仍须验端点，不能将其测试冒充扩大输入域。原均值/中心截距/明细、尺度矩与offset分别投影；精确值可靠而普通投影RangeLoss时可保留尺度诊断，不能保留不存在的普通Value。

二次方程残差门具体为：将 T1=W·βn²、T2=(λn U−V)·βn、T3=−λn W 用frexp/ScaleB式保留指数生成，取最大项指数共同缩放后，abs(T1+T2+T3)/(abs(T1)+abs(T2)+abs(T3))≤1e-10；分母0或项非零丢成0→RangeLoss，非有限→EvaluationFailed。ρ容差外越界/不可信为NumericUncertain，不用PsdTolerance裁 exact Gram；精确负PSD只可能实现/输入错误，EvaluationFailed。β值门通过不能替代独立系数oracle。

未执行/完整性阻断/取消未完成累计时 Moments.Count=0，Anchor/ScaleExponent/NormalizedRatio/Correlation/Gap/RootBranch等尚未形成字段为null；均值/尺度矩/系数用对应Undefined、Cancelled、BudgetExceeded等状态及Code，不用0填值。Count=0表示没有完成可用矩，实际完整有效pair数仍在Coverage；n=0正常空输入与未计算由Code/终态分辨。完整中心累计后发生支持域/根/截距门失败，可保留真实Count/矩/Anchor/已得诊断；LineKind=NotEvaluated直至成功方向或精确Sxy=0分类，NumericUncertain不猜Finite。PairsVisited为第二遍中心矩累计中已完整处理的pair数，范围[0,Included]，其它遍/明细访问不重复计；PeakIntegerBits包含全部中间整数。若预算不足以预留快照/索引/必需结果/诊断则接纳前BUDGET_EXCEEDED，接纳后字节/墙钟中断走原终态链；整数位数超限按本slice RangeLoss保留原因，和S6既有语义一致。未开始的task只返回具名未执行诊断，不补造均值/行；取消明细阶段的部分Details清空并给Cancelled，已完成矩可保留但不得称明细完整。

S7 的政策内容哈希使用新family域，参数仍精确采用engineering-binary64-v1；不同family编码所产生的引用不能跨family仅凭Id/Revision复用或判同，操作身份始终包含family/schema及完整hash。这不是重新标记旧政策/后端。机器单位字符串组合冻结为XUnit+"²"、YUnit+"²"、XUnit+"·"+YUnit、YUnit+"/"+XUnit；同单位斜率仍写mm/mm，不自动改1；消息展示由宿主本地化，机器身份不随语言改变。


**两个完整无 UI Host。** 以下代码加入既有 TestHost 的 S7 模式，不新增工程或产品入口。沿用 §7.1.3.9 的本地原语 S/NS/H/Ref/NPBody/NB/Closure 原文；只共享这些基础编码函数，不调用 S6 的 Definition/TaskBody/SnapshotBody/Seal。各模式在自己的进程执行以下完整夹具构造；这些函数不是公开 Core API。三个 ASCII 正文、全部状态/来源/单位/政策/预算/Closure 都在代码中给全，Source 和 Input 的空 hash 仅为构造中间态，Seal 后才能送入引擎。夹具误差比证据是明确合成协议，不能用作客户物理证据。S7 MemberSet 另用新域 S7-DEMING-MEMBER-SET-V1\0 + Count(Int32) + 排序 PairId(String)；不复用 S6 组身份。

S7模式显式引用 System、System.IO、System.Linq、System.Threading、System.Threading.Tasks、System.Collections.Immutable、System.Security.Cryptography、System.Text 和 Asun.Modules.Statistics；下方代码及复用原语置于同一 .NET10 console 编译单元，不依赖未声明的隐式using。

~~~csharp
static void D7Value(BinaryWriter w, double? v)
{
    w.Write((byte)(v.HasValue ? 1 : 0)); if (v.HasValue) w.Write(v.Value);
}
static DefinitionReference D7Definition(string id, string text)
    => new(id, "1", H("S7-DEMING-DEFINITION-V1", w =>
       { S(w, id); S(w, "1"); S(w, text); }));
static DemingObservation D7Observation(
    string name, string pairId, string role, double value)
{
    var src = new ObservationReference(name + "-" + role + "-" + pairId,
        "r1", "", "fixture:" + name + ":" + role + ":" + pairId);
    var member = new NumericalMember(role + "-" + pairId, src,
        ObservationState.Valid, null);
    var o = new DemingObservation(member, "mm", value);
    string sha = H("S7-DEMING-SOURCE-V1", w =>
    {
        S(w, pairId); S(w, role); S(w, member.RowId);
        S(w, src.ObservationId); S(w, src.SourceRevision);
        NS(w, src.EvidenceReference); w.Write((int)member.State);
        NS(w, member.ReasonCode); S(w, o.Unit); D7Value(w, o.Value);
    });
    return o with { Member = member with { Source = src with { ContentHash = sha } } };
}
static void D7Obs(BinaryWriter w, DemingObservation o)
{
    var m = o.Member; var s = m.Source;
    S(w, m.RowId); S(w, s.ObservationId); S(w, s.SourceRevision);
    S(w, s.ContentHash); NS(w, s.EvidenceReference); w.Write((int)m.State);
    NS(w, m.ReasonCode); S(w, o.Unit); D7Value(w, o.Value);
}
static void D7Pairs(BinaryWriter w, ImmutableArray<DemingPairRow> rows)
{
    w.Write(rows.Length);
    foreach (var p in rows.OrderBy(p => p.PairId, StringComparer.Ordinal))
    {
        S(w, p.PairId); D7Obs(w, p.Left); D7Obs(w, p.Right); NS(w, p.ClusterKey);
    }
}
static void D7Task(BinaryWriter w, ConstantRatioDemingTask t)
{
    S(w, "deming-s7-task-v1"); S(w, "ConstantRatioDemingTask");
    S(w, t.TaskId); S(w, t.XRole); S(w, t.YRole);
    S(w, t.XUnit); S(w, t.YUnit); w.Write(t.CenterX);
    w.Write(t.ErrorVarianceRatio); Ref(w, t.Method);
    Ref(w, t.PairingPolicy); Ref(w, t.ErrorVarianceEvidence);
    D7Pairs(w, t.Rows); w.Write(t.ReturnDetails);
}
static void D7Input(BinaryWriter w, NumericalRequest r)
{
    var i = r.Input;
    S(w, i.SnapshotId); S(w, i.SnapshotRevision); w.Write((int)i.Mode);
    S(w, i.QueryReceiptId); S(w, i.SourceBoundary); NS(w, i.WatermarkId);
    w.Write(i.ReadComplete); w.Write(i.CanReplay); Closure(w, r.Closure);
    Ref(w, r.Method); Ref(w, r.SelectionPolicy);
    w.Write((byte)(r.ObservedSubsetApproval is null ? 0 : 1));
    if (r.ObservedSubsetApproval is not null) Ref(w, r.ObservedSubsetApproval);
    w.Write((int)r.Completeness); NPBody(w, r.Policy);
    S(w, r.Policy.Identity.ContentHash); NB(w, r.Budget);
    w.Write(r.Tasks.Length);
    foreach (var t in r.Tasks)
        D7Task(w, t as ConstantRatioDemingTask
            ?? throw new InvalidOperationException("S7-only fixture"));
}
static NumericalRequest D7Seal(NumericalRequest r)
    => r with { Input = r.Input with
       { ContentHash = H("S7-DEMING-INPUT-V1", w => D7Input(w, r)) } };
static string D7RequestHash(NumericalRequest r)
    => H("S7-DEMING-REQUEST-V1", w =>
       { S(w, r.OperationId); D7Input(w, r); S(w, r.Input.ContentHash); });
static void D7NumericValue(BinaryWriter w, NumericalValue v)
{
    w.Write((int)v.State); D7Value(w, v.Value); S(w, v.Unit); NS(w, v.Code);
}
static string D7Expected(ConstantRatioDemingResult r)
    => H("S7-DEMING-EXPECTED-V1", w =>
    {
        var m = r.Moments; w.Write(m.Count); w.Write(r.CenterX);
        w.Write(r.ErrorVarianceRatio); w.Write(m.MeanX.Value!.Value);
        w.Write(m.MeanY.Value!.Value);
        foreach (var v in new[] { m.Sxx, m.Syy, m.Sxy })
        { w.Write(v.Mantissa!.Value); w.Write(v.Exponent2!.Value); }
        w.Write((int)r.LineKind); D7NumericValue(w, r.Slope);
        D7NumericValue(w, r.CenterIntercept);
    });

const string demingMethodText =
    "unweighted;independent-pairs;uncorrelated-errors;constant-known-varY-over-varX;" +
    "exact-dyadic-centering;scaled-stable-root;point-only;no-imputation;no-OLS-fallback";
const string demingPairingText =
    "synthetic-fixture;PairId-ordinal;complete-independent-pairs;" +
    "no-cluster;no-exclusion;no-imputation";
const string demingEvidenceText =
    "synthetic-fixture-only;varY-over-varX;units=mm2/mm2;normal=4;swap=0.25;" +
    "constant-uncorrelated-errors;not-physical-qualification";
var d7Method = D7Definition("constant-ratio-deming-exact-center-v1", demingMethodText);
var d7Pairing = D7Definition("s7-pairing-v1", demingPairingText);
var d7Evidence = D7Definition("s7-error-evidence-v1", demingEvidenceText);
var d7Numeric0 = new NumericalPolicy(
    new DefinitionReference("engineering-binary64-v1", "1", ""),
    1e-14, 1e-12, 1e-10, 1e-12, 8 * Math.Pow(2, -52),
    5e-12, 5e-12, 1e-10, 1e-9);
var d7Policy = d7Numeric0 with { Identity = d7Numeric0.Identity with
    { ContentHash = H("S7-DEMING-POLICY-V1", w => NPBody(w, d7Numeric0)) } };
var d7Budget = new NumericalBudget(
    3, 3, 1, 1, 1, 3, 64, 4096, 1_048_576, 4_194_304,
    TimeSpan.FromSeconds(5), TimeSpan.FromSeconds(2), 64);
var d7Closure = new InputClosure(3,
    H("S7-DEMING-MEMBER-SET-V1", w =>
       { w.Write(3); S(w, "P0"); S(w, "P1"); S(w, "P2"); }),
    true, true, "closure-s7", ImmutableArray<InputGap>.Empty);

NumericalRequest D7Make(string name)
{
    if (name != "normal" && name != "swap")
        throw new ArgumentException("Unknown S7 fixture", nameof(name));
    bool swap = name == "swap";
    double[] x = swap ? new[] { 1d, 3d, 5d } : new[] { 0d, 1d, 2d };
    double[] y = swap ? new[] { 0d, 1d, 2d } : new[] { 1d, 3d, 5d };
    var rows = ImmutableArray.CreateBuilder<DemingPairRow>(3);
    for (int j = 0; j < 3; ++j)
    {
        string id = "P" + j.ToString(System.Globalization.CultureInfo.InvariantCulture);
        rows.Add(new DemingPairRow(id,
            D7Observation(name, id, "x", x[j]),
            D7Observation(name, id, "y", y[j]), null));
    }
    var task = new ConstantRatioDemingTask("S7-" + name.ToUpperInvariant(),
        swap ? "test" : "reference", swap ? "reference" : "test", "mm", "mm",
        swap ? 3d : 1d, swap ? .25d : 4d, d7Method, d7Pairing,
        d7Evidence, rows.MoveToImmutable(), true);
    return D7Seal(new NumericalRequest("op-s7-" + name,
        new InputReference("snap-s7-" + name, "r1", InputMode.FixedSnapshot,
            "receipt-s7-" + name, "synthetic-pairs", "", null, true, true),
        d7Closure, d7Method, d7Pairing, null, CompletenessPolicy.RequireAll,
        d7Policy, d7Budget, ImmutableArray.Create<NumericalTask>(task)));
}
static void D7Assert(NumericalRequest request, NumericalResult result, bool swap)
{
    if (result.State != ResultState.Complete || result.Tasks.Length != 1)
        throw new InvalidOperationException("S7 result incomplete");
    var t = (ConstantRatioDemingTask)request.Tasks[0];
    var r = (ConstantRatioDemingResult)result.Tasks[0]; var m = r.Moments;
    if (result.OperationId != request.OperationId ||
        result.Provenance.Input != request.Input || r.TaskId != t.TaskId ||
        r.Method != t.Method || r.PairingPolicy != t.PairingPolicy ||
        r.ErrorVarianceEvidence != t.ErrorVarianceEvidence ||
        r.CenterX != t.CenterX || r.ErrorVarianceRatio != t.ErrorVarianceRatio ||
        r.Coverage.Expected != 3 || r.Coverage.Included != 3 ||
        r.LeftCoverage.Included != 3 || r.RightCoverage.Included != 3 ||
        r.LineKind != DemingLineKind.Finite || m.Count != 3 ||
        m.MeanX.State != NumericalValueState.Computed ||
        m.MeanY.State != NumericalValueState.Computed ||
        m.MeanX.Unit != "mm" || m.MeanY.Unit != "mm" ||
        m.MeanOffsetX.Unit != "mm" || m.MeanOffsetY.Unit != "mm" ||
        m.Sxx.Unit != "mm²" || m.Syy.Unit != "mm²" || m.Sxy.Unit != "mm·mm" ||
        new[] { m.Sxx, m.Syy, m.Sxy, m.MeanOffsetX, m.MeanOffsetY }
            .Any(v => v.State != NumericalValueState.Computed) ||
        r.Slope.State != NumericalValueState.Computed ||
        r.CenterIntercept.State != NumericalValueState.Computed ||
        r.Computation.MethodRevision != "constant-ratio-deming-exact-center-v1" ||
        r.Computation.Backend.Id != "managed-deming-exact-center-v1" ||
        r.Computation.Backend.Version != "1" ||
        r.Computation.Backend.FloatingPointProfile != "exact-dyadic-binary64-rne-no-fma-v1" ||
        !r.Computation.Backend.Interruptible ||
        string.IsNullOrWhiteSpace(r.Computation.Backend.SourceCommit) ||
        r.Computation.PairsVisited != 3 ||
        r.Computation.PeakIntegerBits <= 0 || r.Computation.PeakIntegerBits > 4096 ||
        string.IsNullOrWhiteSpace(r.Computation.Backend.BuildHash) ||
        r.Computation.RootBranch != "direct-positive-d" ||
        r.Computation.ScaleExponentX != (swap ? 2 : 1) ||
        r.Computation.ScaleExponentY != (swap ? 1 : 2) ||
        r.Computation.NormalizedErrorVarianceRatio != 1 ||
        r.Computation.PairSequenceHash !=
            H("S7-DEMING-PAIR-SEQUENCE-V1", w => D7Pairs(w, t.Rows)) ||
        m.AnchorX != (swap ? 1 : 0) || m.AnchorY != (swap ? 0 : 1) ||
        m.MeanOffsetX.Mantissa != 1 || m.MeanOffsetX.Exponent2 != (swap ? 1 : 0) ||
        m.MeanOffsetY.Mantissa != 1 || m.MeanOffsetY.Exponent2 != (swap ? 0 : 1) ||
        D7Expected(r) != (swap
            ? "a40f12f9948b4b1ce70f888dac973c43ed7f3311a78cc1ae37a29a0cd2322f8a"
            : "88c350f432361b7beba36086695faff61143d313d6f93386be9656ab8bd908e0") ||
        r.Details.Length != 3)
        throw new InvalidOperationException("S7 provenance/numeric Golden mismatch");
    for (int j = 0; j < 3; ++j)
    {
        var p = t.Rows[j]; var z = r.Details[j];
        if (z.PairId != p.PairId ||
            z.CenteredX.State != NumericalValueState.Computed ||
            z.CenteredY.State != NumericalValueState.Computed ||
            z.PredictedY.State != NumericalValueState.Computed ||
            z.VerticalResidual.State != NumericalValueState.Computed ||
            z.CenteredX.Value != p.Left.Value - t.CenterX ||
            z.CenteredY.Value != p.Right.Value - m.MeanY.Value ||
            z.PredictedY.Value != p.Right.Value || z.VerticalResidual.Value != 0 ||
            z.CenteredX.Unit != "mm" || z.CenteredY.Unit != "mm" ||
            z.PredictedY.Unit != "mm" || z.VerticalResidual.Unit != "mm")
            throw new InvalidOperationException("S7 detail mismatch");
    }
}

// Host 1：qualification 的 DTO 映射形状，仅合成数值证据。
var normalRequest = D7Make("normal");
if (normalRequest.Input.ContentHash !=
        "9ff84ef026cd5a582f9807154a4a1bf2b3732c1a1f2755e0ed5e8b3c94d99e1c" ||
    D7RequestHash(normalRequest) !=
        "6983e4b6d3d37373f83c962a95344e4a15eccd48e4140aaf6a423dc6584a4279")
    throw new InvalidOperationException("S7 normal request mismatch");
await using var normalEngine = new StatisticsEngine(new EngineLimits(2, 2));
D7Assert(normalRequest,
    normalEngine.ComputeNumerical(normalRequest, CancellationToken.None), false);

// Host 2：独立工程 console，先建立自己的源/倒方差比/中心/OperationId。
var swapRequest = D7Make("swap");
if (swapRequest.Input.ContentHash !=
        "f96f050bb7d699b610d44c93715b76e5fc58356dc7cc6862237dfb30b187b608" ||
    D7RequestHash(swapRequest) !=
        "2d87fb31476b54a68e3ef7f938d1a3cb4564596c3d09a0239220b8ecff6574f9")
    throw new InvalidOperationException("S7 swap request mismatch");
await using var swapEngine = new StatisticsEngine(new EngineLimits(2, 2));
// Owner 在调用开始前即保存 engine/request/接纳 Task，ValueTask 仅 AsTask 一次。
Task<NumericalRun> swapAcceptance = swapEngine
    .ComputeNumericalAsync(swapRequest, CancellationToken.None).AsTask();
await using var swapRun = await swapAcceptance;
D7Assert(swapRequest, await swapRun.Completion, true);
var swapLookup = await swapEngine.QueryNumericalOperationAsync(
    swapRequest.OperationId, CancellationToken.None);
if (swapLookup.LookupState != OperationLookupState.Found ||
    swapLookup.Status is null || !swapLookup.Status.IsTerminal ||
    swapLookup.Status.DrainState != DrainState.Drained ||
    !swapLookup.Status.CanReuseResources || swapLookup.Status.InFlightBatches != 0 ||
    swapLookup.Result is null)
    throw new InvalidOperationException("S7 terminal root mismatch");
~~~

同步不登记 operation，不用 Query 成功与否评价正常 Host。异步完整 Owner 按 §7.1.3.8 保存接纳 Task：观察超时若接纳尚未返回，原 Task 继续持有，返回后把原 run 移交原 Owner，不销毁 engine；接纳后 cancel/观察超时用原 run.CancelAsync 独立有限 token 请求停止，再查询原 OperationId/Completion，最后等待资源确实 Drained 才 DisposeAsync。上述正常 Host 的 await using 只用于正常已完成退出；失败/超时模式禁止用它的词法退出绕过原 Owner 的独立观察期限。沿既有 §6 的测试注入在复制、排序、中心两遍、投影和明细检查点暂停/取消，并用 §7.1.3.8 的迟到接纳/取消/cleanup 断言，不为 S7 新造运行根。接纳前已取消：STAT.CANCELLED 且无 Accepted；接纳后取消：原根 Cancelled，部分矩不可冒完整；墙钟到期：TimedOut，通知/查询都必须待真实释放才终态；观察期限到而释放未确认：仍 Draining、IsTerminal=false/CanReuseResources=false，原根继续。纯托管检查可及时停止，不据它省略释放与迟到接纳验证。

**完整小 Golden 字段与字节。** 上述两个请求是完整夹具输入，State 全为 Valid=0、ReasonCode/ClusterKey/Watermark/SubsetApproval 为 null；SourceRevision=r1、SnapshotRevision=r1、DefinitionRevision=1，三个 PairId=P0/P1/P2，每侧 Unit=mm，Expected=Included=3、两侧全有效。编解码长度含一次域 ASCII + 0。本轮只以独立 Python struct/hashlib 重建字节、Fraction/80位 Decimal 核算解析值；未执行 C#、mcr 或实际后端。正常数值 n=3、MeanX=1、MeanY=3、Sxx=2、Syy=8、Sxy=4，Slope=2、CenterIntercept@1=3；交换后 MeanX=3、MeanY=1、Sxx=8、Syy=2、Sxy=4，Slope=.5、CenterIntercept@3=1。矩 mantissa 全1，normal exponents=(1,3,2)，swap=(3,1,2)；LineKind=Finite=1，两系数 Computed=0，单位分别 mm/mm、mm，Code=null。


| 完整编码对象 | 字节长度 | SHA-256 |
|---|---:|---|
| constant-ratio-deming-exact-center-v1 | 235 | `6ccddc4199edc5f5626d93cccf604d769c02b69899c0f3a97f90cd5d1678bec3` |
| s7-pairing-v1 | 147 | `1cd4b66cdeb7cf2cbaea350c954e9f524e65ecd7dddfd30242ea9e3a9887f9ae` |
| s7-error-evidence-v1 | 183 | `3ed02eb943f2e56c27afc9662635123dde8bf9b2144e1106a1033cc16ab96c88` |
| NumericPolicy | 124 | `7c38df366d66ca55b9a9ae40f86b799944b518619a6f1ae32b3b406ba11d16c4` |
| MemberSet | 46 | `84a5ffbab40f408aa5a166f033c73be77b7d78f3f93667b06f1014dafb364e75` |
| normal-x-P0 | 104 | `c64e584b8fdf57ce1895c10646d46ded32f26f7cb1e69c8a97a789520cc40b2e` |
| normal-y-P0 | 104 | `f3106e1c0defe73d6c59849678008dc42a867739b3db2afa6854ef156a50cba9` |
| normal-x-P1 | 104 | `11ca3642cf4bc0f5e8b3ba40d042ce6dce838417ffe0e25017c4080aae62b87f` |
| normal-y-P1 | 104 | `c2da9e900ad9e42d7d2fef8b50bf7d1f50d4ed882fe7f09fec77d5d1531a243c` |
| normal-x-P2 | 104 | `9774bace4d2eb0c3685f6b62c945b8b936fe8319af3b2d24480527034830c459` |
| normal-y-P2 | 104 | `27a539312981458364a061fdd6bd203af9f36799b46259f9450b446eb1df9aee` |
| normal-Pairs | 898 | `abe2a4cc43d5ee6ee5654162af23c438bf30b52a0f0a67bafabe017d3b93f87c` |
| normal-Task | 1301 | `8e8277f6a94bf52055ae20e2646f07c291a9f7b5aa8e3a50b0a5499eaaa35dda` |
| normal-Input | 1925 | `9ff84ef026cd5a582f9807154a4a1bf2b3732c1a1f2755e0ed5e8b3c94d99e1c` |
| normal-Request | 2011 | `6983e4b6d3d37373f83c962a95344e4a15eccd48e4140aaf6a423dc6584a4279` |
| normal-Expected | 145 | `88c350f432361b7beba36086695faff61143d313d6f93386be9656ab8bd908e0` |
| swap-x-P0 | 100 | `ac0d06b31875915d278a9537e0623acb2e72c98ddd22379058874fb15eea180a` |
| swap-y-P0 | 100 | `a5a50b6c2779770dd021f32717bcf6e57ce65048628feaae8eff15d75c6ab21a` |
| swap-x-P1 | 100 | `5ef8bd2ed74c30a36cb877a2d96912e0c2966ba56adbf9a411c9c367f41a527b` |
| swap-y-P1 | 100 | `01fdc34111a86b37a17a906945096914e6720b3f226338a1d4b7f42b53d6cb6f` |
| swap-x-P2 | 100 | `fc189e1acd2e9a3ee2700979d222e79f5416a3a2c827ddb99a8955bb7e34205f` |
| swap-y-P2 | 100 | `ed62df6693a2038bcebbc5b0f0785ad706af765605407fac52f43d54537e609c` |
| swap-Pairs | 874 | `a6f7fca3304e78925e1dc826d938d2fd5bf5b5f13477e43556e7e7f37ba6d598` |
| swap-Task | 1275 | `f81912bfbaa6c3f00e91a6a848381a9512098f3df4102b6ab67abfecddb1c3b5` |
| swap-Input | 1895 | `f96f050bb7d699b610d44c93715b76e5fc58356dc7cc6862237dfb30b187b608` |
| swap-Request | 1979 | `2d87fb31476b54a68e3ef7f938d1a3cb4564596c3d09a0239220b8ecff6574f9` |
| swap-Expected | 145 | `a40f12f9948b4b1ce70f888dac973c43ed7f3311a78cc1ae37a29a0cd2322f8a` |

normal Expected 全部145字节（含域，连续hex）：

```text
53372d44454d494e472d45585045435445442d5631000300000000000000000000000000f03f0000000000001040000000000000f03f0000000000000840000000000000f03f01000000000000000000f03f03000000000000000000f03f020000000100000000000000010000000000000040050000006d6d2f6d6d0000000000010000000000000840020000006d6d00
```



**解析、数值和异常验收矩阵。** CaseId 固定如下，作为既有 Core.Tests/TestHost 的消费者，不新建独立清单。除逐位字段/hash Golden 和精确退化判定外，已识别正常域系数对独立80位以上 oracle 要求相对误差≤1e-12；近零系数使用原数据尺度上 1e-12 的绝对误差，均值/尺度矩为精确有理量最近偶数投影（逐位）；不放宽请求政策。中心截距 oracle 用已返回binary64 β，明细用已返回β/aCenter，与理想真斜率误差分别核，不用残差门替代系数误差。极端/临界域只在已冻结域与门内验；任何不确定状态不能伪造成 Computed。

| CaseId | 完整输入变化/参数 | 可判定断言 |
|---|---|---|
| D7-001/002 | 上述 normal/swap 全字段请求 | 表中Source/Definition/Policy/MemberSet/Pairs/Task/Input/Request/Expected逐字节长度/hash一致；两Host数值/覆盖/单位/来源/Backend/明细一致；交换斜率乘积=1，不复用原source hash |
| D7-003 | x=(0,1,2)，y=(5,3,1)，λ=4，CenterX=1 | MeanX=1/MeanY=3，Sxx=2/Syy=8/Sxy=-4，Slope=-2，CenterIntercept=3；共线负方向不选错误正根 |
| D7-004 | x=(0,1,2)，y=(0,1,3)，λ=1，CenterX=1 | Sxx=2/Syy=14/3/Sxy=3；Slope=(4+sqrt(97))/9=1.538761977977344969…，CenterIntercept=4/3；不能给OLS斜率1.5；与mcr输入ratio=1对照 |
| D7-005 | D7-004改λ=4与1/4，分别oracle；不能只用共线数据检测ratio方向 | β=(−5+sqrt(349))/9（λ=4）或 (25+sqrt(949))/36（λ=1/4）；与mcr分别传1/4与4；结果不同，误传标准差比2亦应检出 |
| D7-006 | D7-004执行x'=1000x+10、y'=2y−7，λ'=(2/1000)²，CenterX'=1010；XUnit=um、YUnit=scaled-mm，重建来源/证据/身份 | β'=.002β，aCenter'=2*(4/3)−7=−13/3；错误沿用λ=1不能通过。通用换算与交换合成测试对含噪正/负数据都成立 |
| D7-007 | x=2^40+(0,1,2)*2^-10；y=−2^39+(1,3,5)*2^-10；λ=4；CenterX=2^40+2^-10 | 均值/Anchor/独立MeanOffset保留；Sxx=2^-19/Syy=2^-17/Sxy=2^-18，Slope=2，aCenter=−2^39+3*2^-10，垂直残差全0；禁止原尺度平方累加相消 |
| D7-008 | x=(−1,0,1)，y=(1,−2,1)，CenterX=0；λ=1/3/4 | Sxx=2/Syy=6/Sxy=0，分别Vertical/Unidentified/Horizontal；Slope与CenterIntercept均Undefined，Code=STAT.DEMING_UNIDENTIFIABLE，不能返回∞/0 |
| D7-009 | x恒0、y=(1,2,3)；再交换；再两侧恒值；全完整 | 依次Vertical/Horizontal/Unidentified，两系数Unavailable；中心矩仍各自可靠，不除零。x=(2^40,2^40+2^-14)输入已量化同值，仅据实际binary64判退化 |
| D7-010 | n=0空数组与Expected=0；n=1=(2,5)，CenterX=2/λ=1；n=2=(0,1),(1,3)/λ=4 | n0均值/矩Undefined且Count=0；n1均值(2,5)/零中心矩、系数InsufficientData；n2点β=2、aCenter@0=1，无CI/标准误；不称客户最低样本通过 |
| D7-011 | D7-004的换根边界λ*=Syy/Sxx=7/3；取L=7d/3d、Math.BitDecrement(L)、Math.BitIncrement(L)，按冻结U/V/W→λn→共同缩放路径核实际d；另取λ=4/1/4，并用D7-001作精确零d构造 | L及邻接值的实际浮点d/RootBranch按下方固定断言；不能用原尺度精确D符号替换实际分支，λ=1邻接值不覆盖负d。两稳定根系数分别对120位oracle核相对误差≤1e-12且连续/signβ=signSxy；λ=4明确负d有理化分支，λ=1/4明确正d直接分支；D7-001精确零d走直接分支 |
| D7-012 | 完全共线x=(0,1,2)，y=2^k*x，λ=2^(2k)，k=−128/+128，CenterX=1 | 原λ两端2^-256/2^256均支持，λn=1；β=2^k、中心截距=2^k。非零X/Y/CenterX=2^-400/2^400逐边界验；超边界一ulp UnsupportedDomain |
| D7-013 | x=(0,1,2)，y=x，λ=2^-128/2^128，与其外一ulp；再λ=2^-256/2^256 | λn两端允许，稳定分支仍β≈1；归一化λ越域即UnsupportedDomain；raw λ合法不等于当前数据尺度支持。λ=0/负/NaN/∞接纳前STAT.DEMING_RATIO_INVALID |
| D7-014 | x=(−1,0,1)，y=(1,−2,1+2^-42)，λ=1；以及exact oracle生成gap在2^-40下/等/上的白化散布 | 首例非零Sxy、0<absρ<2^-40，NumericUncertain；gap≤2^-40也拒绝；通过gap但ρ未过仍不能拟合；不得剪小W或把舍入各向同性判有效 |
| D7-015 | 非零anchor差范围含2^-129与1；再2^-128与1；先4096bits验证spread门，再分别显式MaxIntegerBits=128/256/4096测位门 | spread>128 UnsupportedDomain；等边界在足够bits预算时继续。位对齐/乘积/PSD核/有理投影每步都核位，超bits RangeLoss/STAT.RANGE_LOSS，不先约分掩盖。字节/明细/行/诊断预算不足为BUDGET_EXCEEDED；不扩预算重试 |
| D7-016 | CenterX使abs(CenterX−meanX)/2^ex=2^40、超一ulp；再用高精度构造投影非零下溢/溢出 | 边界允许、超界截距UnsupportedDomain而可靠Slope保留；通用投影溢出或非零→0 RangeLoss，不能输出∞/0或把依赖系数明细Computed。超double输出并非宣称在本支持域必可达 |
| D7-017 | 值/单位/SourceRevision/hash/ratio/CenterX/ReturnDetails/任一budget/方法/配对/证据逐一改字段；枚举未知/default数组/混旧family | hash/operation身份相应变；错hash/重复PairId/侧RowId/SourceId接纳前拒绝STAT.DEMING_PAIR_INVALID或IDENTITY_CONFLICT；非法单位/值结构不接纳，混family/非nullClusterKey METHOD_UNSUPPORTED；不默认补字段 |
| D7-018 | 两侧分别Unknown/Missing/Unmeasured/Invalid/NotApplicable/Excluded，非Valid Value=null；Expected=4但只给3对且一个InputGap | 全覆盖与双侧状态守恒；RequireAll阻断矩/系数STAT.INPUT_INCOMPLETE，未知未测不当0；ApprovedObservedSubset带实际批准引用后仅算完整有效对，Result Partial、预计/缺口保留；不按两侧分别删行 |
| D7-019 | 接纳前token取消；接纳Task迟到；计算各检查点取消/WallClock到期；通知不读/缓慢 | 原OperationId/控制Task/run强持；Cancel/TimedOut只在Drained后终态；DrainCompleted唯一且先于Completion；未完成矩/Details不冒完整，PairsVisited不等于Coverage；观察取消不取消worker |
| D7-020 | 同ID同闭包异步重入/同ID异λ；1/2个并发；峰值/cleanup失败注入；原资源释放晚于观察限 | 同闭包复用原根，异内容IDENTITY_CONFLICT；晚到结果只归原根，无第二次计算、无双释放；观察限不返池、不提前reuse、不丢根，完成后独立查询原结果；运行失败给定位诊断并排空 |
| D7-021 | 完整有理投影ties：±(1+2^-53)、±(1+3*2^-53)，零/进位为2、最小normal/subnormal与次正规半ulp | 最近偶数分别±1、±(1+2^-51)，m=2进位重规范；零固定m=0/e=0；非零投影为0则RangeLoss。不用普通double除法当精确有理oracle |
| D7-022 | 未请求Details与已请求Details在MaxDetailRows下/等/上的同输入 | false返回空Details且无N条明细缓冲；true等上限可返回全部、有序PairId；超上限接纳前拒绝，不截断。PredictedY/VerticalResidual只作垂直描述，无校正/放行副作用 |

D7-011 的具体复算：L=2.3333333333333335（binary64位型0x4002aaaaaaaaaaab），其下邻2.333333333333333（0x4002aaaaaaaaaaaa）、上邻2.333333333333334（0x4002aaaaaaaaaaac）。冻结U=1/2、V=round(7/24)、W=3/8、λn=λ/4，再共同除max(a,b,abs(c))后，下邻/L/上邻的d依次为+2^-52、+0、−2^-52，RootBranch依次direct-positive-d/direct-positive-d/rationalized-negative-d。原精确D=Syy−λSxx的符号依次正/负/负，L处浮点d=0是归一化舍入，不称精确各向同性；Sxy=3≠0且gap正常，仍可识别。对应120位oracle β约1.527525231651946670641、1.527525231651946667974、1.527525231651946665306；binary64可舍入相同系数，不强求邻值结果逐位不同。D7-001的U=V=W=1/2、λn=1使精确及浮点d均0且Sxy非零，作为零d分支构造；不改变其正常Golden。该归一化路径本轮以Python Fraction/Decimal独立复算，未运行C#。


**BenchmarkProfile：deming-point-managed-v1。** 唯一消费者为本模块 §12.1 既有 Exe Host/Core.Tests 的 S7 模式；不运行UI或创建benchmark工程。固定.NET10/BCL、机器/CPU/GC/构建身份及上述方法/hash。负载维度 n=1/2/3/10,000/1,000,000；两侧anchor差 exponent spread=0/64/128；λn=2^-128/1/2^128（搭配受支持原λ/单位，域外单独拒绝计时）；MaxIntegerBits=128/256/4096，Details=false/true（true明示MaxDetailRows=n），并发=1/2、tasks=1。构造、hash和排序成本必须计入端到端，不能只报2×2根耗时；输入准备另报，不从计时中暗藏生产预处理。最大n夹具采用x=i/2^20、y=1+2x或固定dyadic噪声且冻结seed/输入hash，不超过域。

分别测接纳/复制/身份核验及增量hash、Ordinal排序、两遍精确累计/位数、PSD/尺度投影/root、反尺度/明细、排空；记录端到端P50/P95/P99、PairsVisited、PeakIntegerBits、GC分配/峰值同时活跃缓冲、进程峰值working set、取消到停止检查/到Drained的时间、budget提前拒绝耗时。至少暖机5次、每档30次，百万/高位档10次且注明分位证据有限；不能把少样本P99当现场实时承诺。性能目标状态为TargetsPending，硬技术门为不超调用预算、不生成N×N矩阵、不缓存全量BigInteger差数组、不无界诊断/通知，取消检查频度至少每pair/每次位操作/root前后/明细；客户WallClock/P95/P99/内存阈值由Profile另定，不伪造实测。 n=1只测输入/均值/InsufficientData路径，λn与spread档只用于存在非零差的负载；不为单点虚构归一化比值。

算法排序O(N log N)，排序后遍历两次O(N)个算术操作；BigInteger乘/除随位宽变化，不声明单位成本O(N)运行时间。存储O(N)有界快照/排序索引及可选明细、O(B)精确累计与scratch（B≤MaxIntegerBits），按同时活跃字符串/编码缓冲/BigInteger临时副本/结果/通知计峰值；生产增量SHA，不把本小夹具MemoryStream全编码作为百万行路径。MaxBufferedBytes/MaxWorkingSetBytes由调用方按Profile显式给足，3行Golden预算不复用百万负载。所有实例合计仍受engine容量及宿主并发预算限制。仅复用§12.1 build和Exe执行约定，启动实施/运行资格后才执行并记录真实性能。


### 7.2 对照 DEV-TST-003 的通用统计方法边界

以下条款只约束统计输入的单位、分母、缺失和推断方法，不定义 PCB/PCBA 缺陷、质量放行或客户门槛。未满足声明条件时，Core 必须返回 `STAT.METHOD_UNSUPPORTED`/`NotComputable`，不得用总体比例、默认插补或未声明的合并规则替代。

1. **统计单位、分母和分层**：`MetricDefinition`/`Scope` 必须声明观察单位、计数或暴露单位、聚合粒度、分母来源和分层键。分子、分母必须在同一声明层级计算；重复观察只能按已声明的身份/cluster 规则去重或保留，不能把行数当机会数。跨设备、批次、班次、来源或其它 `stratum` 的结果，先分别保留 `DenominatorEvidence` 和适用性，再依批准的聚合政策形成总体；没有聚合政策时不得汇总或以汇总值掩盖层间差异。
2. **缺失、Unknown 和排除**：每条记录的 `Unknown`、缺测、未测、无效和排除原因必须保留，并从“未观测”“不适用”“无效输入”“排除”中区分。除非 `CompletenessPolicy`/`MethodRevision` 预先声明并可复现，否则不得插补、把 Unknown 当 PASS/FAIL、把缺失当 0、仅保留 complete case 或把排除样本移出分母；分母变更必须形成新统计意图/修订。
3. **聚类和过度离散**：计数、比例或重复观察若存在 cluster、相关观测、过度离散或层内异质性，普通独立 Bernoulli/Poisson 公式不得默认适用。§7.1.3.9 仅在 `MethodRevision=group-percentile-bootstrap-v1` 明确把整组作为等概率独立抽样单位、以组级充分计数累加比值、绑定 PCG32 字节规则和重采样顺序时可用；权重、时间块、多层 cluster、有限总体修正、GEE、negative-binomial 和其它模型仍返回不支持。否则返回不支持。 
4. **置信区间**：任何区间必须绑定点估计量、分母/暴露量、单侧或双侧方向、置信水平、计算方法、分层/cluster 处理、边界规则和样本量/精度依据，并把方法与版本写入 `Provenance`/`Diagnostics`。Clopper–Pearson 仅可作为“独立 Bernoulli、分母已冻结、无聚类”的候选，不是召回或其它业务指标的默认方法；缺少这些条件时不得输出看似精确的区间。
5. **跨来源比较与测量一致性**：跨机、跨批、跨来源或跨时间的比较只能作为显式分层、随机化/配对策略或获批模型的输入；不得仅用 Pearson 相关替代一致性或把每机修正隐藏在统计 Core。Bias、Linearity、Stability、Uncertainty、GR&R/MSA、Deming/Bland–Altman 等需要可溯源参考件、校准/环境和测量协议，保留为外部方法/计量 Owner 的候选；本 Core 按 §7.1.3 接收其已冻结的数值任务（组矩/contrast/设计/协方差/条件t/F），返回计算及诊断；实验模型、资格和客户判据不由Core决定。
6. **误报负担和产品指标**：false-call/board、人工复判负担、FPY、召回或放行等指标只有在上游 Owner 已把真值、机会单位、cluster 和观察窗口冻结为结构化输入时，才可作为普通计数/分层统计消费；本模块不定义这些产品语义、阈值或门禁。

上述测量方法的外部实验/资格责任不变；ConstantRatioDeming 的有限无权重点估计数值已在 [§7.1.3.10](#constant-ratio-deming) 补专用 S7 规格（2026-10-11 主控接收为 ModuleCoreImplementationReady，仅规格准备）。除该明确入口与支持域外，Deming 置信区间、加权/异方差/相关误差/重复测量及其它ODR仍不支持；不能据上条“候选”绕过该数值入口，也不能据新入口声明生产测量资格。

## 7.3 第二轮场景驱动验收矩阵

以下矩阵是实现和独立审核的逐场景断言。每行都要求输入、参数来源、顺序、结果状态和恢复动作可在日志/回放中定位；“可计算”不等于质量通过。

| 场景 | 输入与参数来源 | 处理顺序 | 输出、状态和错误 | 恢复/可判定验收 |
|---|---|---|---|---|
| 正常固定执行 | 固定 `SnapshotId`、完整回执、同一 `MetricDefinitionRevision`/`MethodRevision`、有效单位和已批准预算 | `Accepted`→绑定输入→分块→完整性→分组→主路线计算→封闭→`Draining(PendingOutcome=Completed)`→确认释放 | 先 `State=Draining`/`IsTerminal=false`，确认 `Drained` 后发送一次 `DrainCompleted`，再返回 `Completed`；每指标有值/单位/分母/子组/证据和快照身份 | 重放同一闭包、顺序和版本，结果语义一致；不写质量事实。 |
| 空输入 | 固定范围合法但 0 行，或实时窗口尚未产生观察；方法/单位仍有效 | 绑定范围→先判空，不执行依赖非空样本的累计或除法→逐指标适用性→排空 | 排空确认后才可 `Completed`，仅包含计数 0 和 `NotComputable`；不返回均值、0% 或控制限 | 新输入到达后必须是新计算/窗口事件；空结果不能覆盖旧非空快照。 |
| 部分成功/缺口 | 预期 N，实际读取 n<N；部分行合法、部分读取中断/权限拒绝 | 记录已读、缺口原因和水位→完成性判定→只计算允许的描述性子集 | `Partial` + `STAT.INPUT_INCOMPLETE`；不命名完整总体，不猜缺口值 | 同一快照补齐后重取并形成新封闭结果；失败重试不改变原缺口证据。 |
| 分层分母/重复观察 | 同一统计单位有重复观察，且设备、批次或其它层级不同；分母由批准的单位定义 | 先按声明的观察单位、cluster/身份和 stratum 去重或保留→分别计算分子/分母→检查聚合政策 | 每层保留 `DenominatorEvidence`、成员关系和适用性；无聚合政策时不输出总体汇总，不把行数当机会数 | 改变统计单位、去重或合并规则必须产生新 `MethodRevision`/统计意图；禁止用总体比例掩盖层间差异。 |
| 相容比例合并 | 三组反例：全部相容的多层计数；至少一层分母未知；指标/单位/观察单位/来源边界或聚合政策不相容 | 先分别验证分母/机会量→相容层合并原始分子和分母后再除法；未知或不相容层保持分层 | 相容的 `1/1` 与 `0/99` 只能得到 `1/100=1%`；分母未知返回缺口/不可计算，不平均百分比 | 固定向量验证不得得到 `50%`；未知或不相容时不得输出完整合并率；改变合并政策形成新 `MethodRevision`，并保留各层证据。 |
| 合理子组与冻结基线 | 子组/时间窗/采样键已由 Owner 预批准；输入含重复测量、缺口或后续极端值 | 按预批准顺序和断点建组；先冻结 baseline，再以其修订计算 Phase II 点和规则 | 事后按 PASS/NG、报警或数值重组时拒绝受影响方法；p/u 用逐点实际分母，np/c 仅恒定 n/暴露量适用 | 同一物理目标重复测量不自动扩为独立波动；在线新点不重估基线中心/限值参数，p/u 限值仍按实际 n/暴露量计算；记录组资格和 baseline 修订。 |
| 信号证据与缺口断点 | 同一批准规则/baseline 下的命中、不命中、重叠窗口和含 Unknown/缺点窗口 | 用完整合格输入评价有限规则→逐命中保留参与 ID/窗口与比较→遇断点清空窗口 | `ControlSignalEvidence` 保留规则/baseline 修订、方向/阈值及比较值；重复窗口证据不因显示合并丢失 | 不跨缺口续算；无命中仅表示已启用规则未命中，不声明稳定/能力；Core 不确认、关闭或抑制告警。 |
| Unknown/缺失保留 | 同时存在 Unknown、缺测、未测、无效和预先允许的排除 | 保留原记录及 reason→区分缺口类型→按 `CompletenessPolicy` 判定可计算子集 | 不插补、不把 Unknown 当 PASS/FAIL、不把缺失变 0；分母证据说明排除及其原因 | 只有预先声明且可复现的策略才可改变分母；否则返回 `Partial`、`NotComputable` 或 `STAT.INPUT_INCOMPLETE`。 |
| 聚类/过度离散 | 计数或比例含相关观察、cluster、层内异质性，或方差显著超过独立模型假设 | 检查 `MethodRevision` 是否声明 cluster 单位、协方差/设计效应、有限样本修正和重采样规则；S6 仅接受等概率独立组和整组抽样 | 未声明、含权重/时间块/多层依赖或不满足 S6 预检时 `STAT.METHOD_UNSUPPORTED`/`NotComputable`；不得静默使用独立 Bernoulli/Poisson 或删组 | S6 六项文档规格已由主控接收为 ModuleCoreImplementationReady（仅规格准备）；实际实现仍未执行，复杂 NB/GEE/多层 bootstrap 继续不支持。 |
| 置信区间/跨来源比较 | 请求区间或比较设备、批次、来源、时间层；方法可能受聚类或异质性影响 | 冻结点估计量、分母、置信方向/水平、分层/cluster 规则和方法版本→先分层再按政策合并 | 条件不足时不输出区间或总体比较；不得以 Pearson 相关替代一致性 | Bias/Linearity/Stability/Uncertainty/GR&R/MSA 等需外部计量 Owner、参考件和协议；Core 只消费已冻结结构化结果。 |
| 歧义输入 | 相同显示名但规格/被测量/观察单位/代次不同，或重复身份异 hash | 身份/版本/单位相容性→分层或拒绝→禁止按名称合并 | `STAT.SCOPE_MISMATCH` 或分层结果；不平均 Cpk/比例 | 调用方提供明确范围/修订后新请求；旧请求保持不可变。 |
| 非法数值/分母 | NaN/Inf、负机会量、`d>n`、`n=0`、负 M2、规格反转、单位未知 | 逐行/逐组 checked 校验→停止受影响指标→保留行引用 | `STAT.NONFINITE_VALUE`、`STAT.DENOMINATOR_UNKNOWN` 或 `Invalid`；其它独立指标可继续 | 修正源事实或方法后以新输入/修订重算；不得 `abs`/epsilon/默认 0 修复。 |
| 高噪声/离群/遮挡/退化 | 数值散布、极端值、重复测量、分布相关、缺观测，但未批准稳健方法 | 按原政策保留并统计质量/缺口→检查资格→不自动清洗或拟合 | 描述性结果可返回；能力/控制图按资格 `NotComputable` 或 `STAT.METHOD_UNSUPPORTED` | 由质量/方法 Owner 新增批准路线后新版本接入；当前版本不训练、不自动调模。 |
| 超大输入 | 行/组/组宽接近或超过预算，排序和图点可能膨胀 | 先预算估算→有界分块/回压→超限前停止接纳→排空 | `STAT.BUDGET_EXCEEDED`；不截取前 N 后标完整 | 宿主增配批准预算或拆成明确范围的新请求；不隐式分页改变分母。 |
| 高并发/长期运行 | 多宿主、多窗口、不同语言和方法并行；监测运行跨班次 | 每实例独立状态→有界队列→公平/背压→周期快照或显式窗口封闭 | 各 `OperationId` 结果和资源隔离；队列/水位/窗口状态可观测 | 任何实例取消/换语言/页面关闭不影响其它实例；长期运行必须按批准窗口或检查点，不能无限增长。 |
| 取消 | 在读取、分组、计算、序列化或交接前收到 token | 标记 `PendingOutcome=Cancelled`→进入 `Draining`→停止新输入→等待在途操作→释放缓冲/租约 | `State=Draining`、`IsTerminal=false`、`STAT.CANCELLED`；排空未确认时不得有 operation 终态或 `DrainCompleted` | 验收取消延迟≤请求 `CancellationResponseLimit`（实测）；确认 `Drained` 后才发送一次 `DrainCompleted` 并写入 `Cancelled`，此前不得复用资源。 |
| 超时 | 达到 `WallClockLimit`，底层读取/持久交接或资源释放状态未知 | 标记 `PendingOutcome=TimedOut`→进入 `Draining`→停止新工作→查询原操作/回执→记录 `DrainObserved`→隔离重查 | `State=Draining`、`IsTerminal=false`、`STAT.TIMEOUT`；不发送 operation 终态或 `DrainCompleted` | 仅在旧 worker 明确停止、输入仍有效且版本/范围不变时重算；确认 `Drained` 后才写入 `TimedOut`，排空确认前不返池、不复用、不盲并发重试。 |
| native/适配器排空 | 可选 Boost Beta 调用、宿主输入源适配器或外部租约在途 | 取消/失败先等待调用返回→逐项核对释放证据→仅确认全部释放后推进 `Drained` | 资源状态与统计状态分开；未知释放状态为 `Unknown`，不得发送 `DrainCompleted` | 适配器报告真实释放/超时证据；核心不提前返池、不把 native 错误变成数据 NG；后续确认释放时仅发送一次完成事件。 |
| 持久化成功/未知 | Core 计算已排空完成，宿主保存回执明确或连接中断 | Completion→宿主原保存操作→取得/查询原保存回执 | Core 保留原 Completed 计算结果；宿主保存 Unknown 是另一个状态，不能改写 Core 或换新计算身份 | 查询原保存 OperationId；提交成功不重复写，保存未知不靠重算解决。 |
| 版本修订/迁移 | 方法、单位、排序、去重、Schema 或数值策略改变；旧快照仍需读取 | 兼容矩阵→拒绝或显式迁移→保留旧 revision→新修订计算 | `STAT.VERSION_INCOMPATIBLE` 或新 `StatisticsSnapshotId`；旧结果不可原地更新 | 回退读取旧结果/旧包；禁止用新方法解释旧 hash，升级与回退都保留差异证据。 |
| 无 UI 调用 | 独立进程提供固定输入适配器、取消和预算 | 直接调用同步/异步 Core→消费结果/通知 | 不依赖窗口、Dispatcher、ViewModel；状态和错误可机器判断 | 同一测试在无 UI 宿主可复现；页面不是初始化前置条件。 |
| 可选 UI | UI 仅持有请求代次和只读投影，核心仍走同一入口 | 新筛选若改变计算语义则新请求；缩放/抽稀仅投影→旧响应代次校验 | 显示范围、完整性、适用性、错误和下一动作；不把空值绘为 0 | UIA/键盘/三语/关闭流程验证；关闭只解绑，取消必须显式。 |
| 第二消费者 | 工程数据工具使用不同输入适配器和 Profile，不引用 SPC 页面/私表 | 接入同一 Core/Contract→消费 `StatisticsResult`/EvidenceRef | 可替换宿主、语言和存储；不理解制程对象仍能处理状态 | 独立完成正常、缺口、取消/恢复、版本不兼容四组验收，结果范围关系可核对。 |

每个场景的“输出”仅说明统计能力事实。调用方必须另行决定是否展示、调查、复判或采取工艺动作；模块不产生这些决定。

## 8. 适配器和版本兼容

数据源适配必须按字段/行预算流式提供数值观察，不能让 Npgsql Reader、事务或连接跨越整场统计计算/页面生命周期。适配器在有限读取批次内将结构化数据复制到有界 Core buffer 后释放数据库 scope；需要原始图像佐证时只携带稳定 `EvidenceRef/ObjectId`，显示端再经 IM-066 取文件租约。第二消费者需以慢存储、文件缺失和超大对象验证统计核心仍可仅用结构化输入完成或明确拒绝，不因证据文件不可用而编造数值或无界重试。

### 8.1 适配器端口

| 适配器 | 输入 | 输出/责任 | 禁止 |
|---|---|---|---|
| `IStatisticsInputSource` | 固定快照或实时读端口 | 有序、typed、分块数据和完整读取回执 | 暴露 DbContext、私表或 `latest`。 |
| `IMetricDefinitionProvider` | 指标/方法/规格修订引用 | 不可变定义与适用域 | 从样本推断规格或阈值。 |
| `IStatisticsPersistence`（可选） | 已封闭快照 | 原子保存、回执查询、保持/读取 | 把计算返回当提交成功；新建第二 Store。 |
| `IObservationEvidenceResolver`（可选） | 观察引用 | 只读证据定位 | 在统计模块重新读取原图或改源事实。 |
| `IStatisticsScheduler`（可选） | 宿主调度/背压策略 | 有界并发与排空 | 隐式全局线程池/无限队列。 |

适配器隔离外部 SDK、数据库、消息和文件格式；领域契约只传稳定标识、单位化数值、版本、回执和诊断。

上述表为宿主责任，不是五个未定义端口供开发者猜测。SPC 入口唯一读取/监测/查询接口为 §3 与附录 A 的 `IStatisticsInputSource`、`IStatisticsWindowSource`、`IStatisticsOperationReceiptSource`；Definition/Methods 是请求值，不动态调用定义服务，保存/证据解析/报告/调度留宿主。Core 不接受 IStatisticsPersistence/IMetricDefinitionProvider 的隐藏容器解析；数值后端仅按 §7.1.3 已冻结端口接线。后续新增实际端口先冻结签名/所有权。

### 8.2 版本策略

- 模块包版本采用 SemVer；输入/输出 Schema 版本和 `MethodRevision` 分开记录。补充可选诊断字段可在兼容版本增加，但不能改变已有字段含义、分母或状态。
- 删除、重命名、单位改变、观察单位改变、排序/去重/浮点策略改变、错误语义改变均为不兼容版本，并生成新的统计修订；旧快照继续按原版本读取。
- 同一版本不同内容 hash、缺少兼容范围、未知方法修订、跨单位隐式转换一律 `STAT.VERSION_INCOMPATIBLE`。
- 适配器必须声明支持的输入/输出版本、方法集合、最大资源、取消能力、持久化能力和实际后端身份；能力缺失显示为不可用，不隐藏降级。
- 回放必须使用原输入快照、RuntimeManifest、参数/方法版本和数值策略。版本变化导致差异时记录明确差异原因，不以“代码变了”替代诊断。


### 8.3 可选 Boost Adapter 的工厂、调用与释放闭合

此项属于当前完整批准范围，不能只因 Core-only 不加载 native 而略过设计。沿 §7.1.3.6 的工程/namespace/ABI/返回类型，公开实现类型固定为 BoostBetaKernel : IStatisticsBetaKernel, IAsyncDisposable；已有 Create(string absoluteLibraryPath,string expectedSha256) 仍返回 IStatisticsBetaKernel，返回对象保证是该具体类型，宿主在调用前同时保存端口和其 IAsyncDisposable 释放视图。Core的IStatisticsBetaKernel签名不改、不增加 Dispose义务给任意第三方端口。没有 IDisposable/IAsyncDisposable 的外部端口，宿主应保留其真实Owner，不以cast失败擅自卸载；本明确Boost实现不会cast失败。

Create为同步工厂，无默认路径/hash，接受前验证绝对路径/64位小写hex SHA-256、Windows x64和§7.1.3.6已冻结ABI/方法身份；本处平台检查是自建native包的调用前置，不是AsunImage/DevExpress依赖核验。宿主先取得有界根槽/描述符，再在需避免阻塞的Host中用一个被根强持的Task调用工厂，不开未登记的fire-and-forget加载。通常公开异常统一用StatisticsRequestRejectedException（工厂清理不确定时用下方带原Owner的BoostBetaKernelCreationException）：路径/hash/ABI/自建浮点配置不相容STAT.VERSION_INCOMPATIBLE，文件/装载异常STAT.PORT_FAILURE；参数未合法时不创建native调用。

加载唯一已冻结且由宿主发布Owner保持不可改写的文件：FileStream只读/FileShare.Read保持期间禁止写入/替换，增量核SHA256，然后NativeLibrary.Load(absoluteLibraryPath)，NativeLibrary.GetExport(handle,"im043_beta_v1")；不搜索PATH或加载相邻候选版本，不下载依赖。导出用标注UnmanagedFunctionPointer(CallingConvention.Cdecl)的私有delegate封送：返回int，op为int，a/b/p为double，两个输出为out double；不跨ABI返回托管对象，不使用布尔/字符串封送。native签名/错误返回继续按§7.1.3.6，不在Adapter重复t/F公式。private handle、delegate、绑定FileStream、in-flight计数、closing位和释放Completion仅由该实例持有，无static库缓存。

EvaluateAsync先检查有效枚举/A/B/Argument及token，在实例短锁中检查closing并登记admitted+1后才投递工作；关闭后抛STAT.PORT_FAILURE且不进native。每实例最多一个在途native调用（有限门控SemaphoreSlim(1,1)），等待占调用方原Task、可在进入native前取消；不排无界队列，Core/Host已有Operation/预算为等待数量上界。进入delegate后不再通过取消等待提前返回；返回码映射State、成功/失败两个out的消费规则沿原ABI，取得门后登记nativeInFlight=1，finally真实调用返回后nativeInFlight=0/释放门；所有成功/失败/等待取消路径最终admitted−1；预检查和门等待取消不占native in-flight。工作在非UI线程，实际native返回前handle/delegate/FileStream强持。异常不换库、不换比值、不重复执行；取消停止意图仍由原run拥有。

DisposeAsync第一次调用在锁内冻结closing、拒绝新调用、创建该实例唯一释放Task；重复Dispose共享它。释放链等待已登记工作和native调用真实返回，再且仅一次NativeLibrary.Free(handle)，最后Dispose绑定FileStream与门；未完成时释放Task仍未完成，宿主观察超时只保留原Task/实例并继续有限观察，不强制Free、不把该库交给另根、不重新Create绕过。成功后所有调用明确拒绝且无重复Free。Free失败保存原handle/原释放异常与Unknown资源状态，不伪造已释放、不能用同handle盲目重复Free；移交原进程根继续观察，进程退出作为OS回收不冒正常释放验收。工厂Load成功后GetExport/构建delegate失败亦必须走同一确定释放；若Free失败则抛下方BoostBetaKernelCreationException，将该未释放实例和原清理Task交回工厂根，保留业务异常为InnerException，不以catch丢handle。宿主根须在开始工厂前具备这一移交槽。

宿主正常顺序：kernel工厂→显式NumericalBackendPorts(Matrix,Beta)→engine→原接纳Task/run→实际Completion及Drained→engine排空/处置→kernel.DisposeAsync。宿主可用同一个kernel供多个engine只读借用，但kernel Owner必须先停所有借用engine、核全部原根Drained再释放；不使用“最后一个页面关了”或GC引用数推断可卸载。默认隔离托管matrix没有外部native资源，其生命周期由engine owned默认实例或宿主显式端口Owner按原约定结束。

本轮实际读取 [.NET10 NativeLibrary.Free 官方签名](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.nativelibrary.free?view=net-10.0)：public static void Free(IntPtr handle)，释放OS库handle，IntPtr.Zero不操作；未提供自动等待在途delegate的保证，故本节显式串行门/关闭与原Task强持。官方页面原字节SHA-256=937c63cb7e03148b87eb6bde9e7960d8fa4b5a86444df4c3a9822c59c7f08b49（2026-10-12只读，无下载文件）；固定dotnet/runtime源码请求连接重置、测试路径404，不声称已读源码/测试。复用§7.1.3.6已完成的Boost源码/许可/算法证据；本补充没有运行native构建或卸载验收。

必要Adapter断言归既有Core.Tests Adapter组：AD-B1正常三op及参数/互补输出、AD-B2错hash/导出缺失/工厂失败释放、AD-B3调用前取消/门等待取消不进delegate、AD-B4delegate阻塞后Cancel/Dispose保留原根/handle且禁止新调用、AD-B5晚返后一次Free/一次终态、AD-B6两个engine借用与Owner先停再卸载、AD-B7Free失败/原异常不被cleanup覆盖及有界移交、AD-B8实际LibraryPath/hash/ABI/FloatingPointProfile与BackendIdentity对应。真实DLL并非Mock；可控阻塞仅验证软件生命周期，独立分布oracle及真实后端资格仍执行§7.1.3.8。



工厂清理不确定时的唯一公开错误形状属于 Boost Adapter namespace，模块内定义如下；它只交付资源恢复 Owner，不用于计算业务返回。根捕获后必须在退出前确认移交到原有界隔离槽，未确认则继续强持，不返回“已关闭”：

~~~csharp
public sealed class BoostBetaKernelCreationException : Exception
{
    public string Code { get; }
    public IAsyncDisposable CleanupOwner { get; }
    public Task CleanupCompletion { get; }
    public BoostBetaKernelCreationException(string code, string message,
        Exception originalError, IAsyncDisposable cleanupOwner, Task cleanupCompletion)
        : base(message, originalError)
    {
        Code = code; CleanupOwner = cleanupOwner; CleanupCompletion = cleanupCompletion;
    }
}
~~~

该异常Code固定STAT.PORT_FAILURE，CleanupCompletion就是该CleanupOwner第一次DisposeAsync生成的原Task；工厂不得凭Faulted/TimedOut宣称其资源已释放。Dispose只等待admitted归零（包含排队等待者），而非只看nativeInFlight，避免在门等待者的finally之前处置Semaphore。closing后已admitted尚未进入native的调用取得门时再核closing，拒绝进入delegate并释放门/admitted；已进入者仍等真实返回，业务Outcome仍由原engine根决定。门等待时取消仅取消该尚未进delegate的请求，不撤销其它原在途调用。实例关闭与Task Completion先后必须在AD-B3/B4/B7覆盖。


## 9. 最小无 UI Host 与调用顺序

下面仅是已冻结接口的调用顺序片段，`approvedDefinition/approvedMethods/approvedSubgroup/fixedInput/closure/profileBudget` 由 Host 用 §3 字段构造，均为明确测试夹具或批准值，不代表未定义类型/默认工艺常数。最小 Host 仅引用 Core 工程及 .NET 10；源可为内存异步迭代器，不引用数据库/UI。完整构造应由实现测试按照下一节向量完成，不把本片段当产品完整例程。

```csharp
var request = new StatisticsRequest(
    OperationId: "op-20261004-0001",
    MetricDefinitionId: "metric.dimension.mean",
    MetricDefinitionRevision: "3.1.0+sha256:...",
    MethodRevision: "moments-set.1",
    Definition: approvedDefinition,
    Methods: approvedMethods,
    Scope: new StatisticsScope(
        ObservationUnitKind: "approved-observation-unit",
        MeasurandId: "dimension-x",
        Unit: "mm",
        TimeRangeUtc: new TimeRange(startUtc, endUtc),
        MemberSetReference: null,
        ScopeRevision: "scope-7",
        SpecificationRevision: null,
        BaselineRevision: null,
        SourcePolicyRevision: "policy-9"),
    Input: fixedSnapshotReference,
    Subgroup: approvedSubgroupPolicy,
    Completeness: approvedCompletenessPolicy,
    Numeric: new NumericPolicy(NumericKind.Binary64, null,
        approvedAbsoluteTolerance, approvedRelativeTolerance, OverflowPolicy.Reject),
    Budget: profileBudget);

await using var statistics = new StatisticsEngine(engineLimits);
await using var run = await statistics.ComputeAsync(
    inputSource, request, cancellationToken);

StatisticsResult result = await run.Completion; // Completion 只在 DrainCompleted 后完成
var status = await statistics.QueryOperationAsync(request.OperationId, cancellationToken);
if (status.Status?.State == OperationState.Draining || status.Status?.IsTerminal == false)
    throw new InvalidOperationException("原 operation 尚在排空；继续隔离与重查，不得当作终态。");
if (result.State == ResultState.Unknown)
    throw new InvalidOperationException("计算结果仍未知；保留原操作并查询，不能用重新计算替代恢复。");
```

运行顺序：构造经审批的 Definition/Methods/预算→构造不可变固定输入或源→构造 engine→同步 Compute 或接纳异步 run→可选独立消费 Notifications→等待 Completion→核 Result.State/各指标适用性及 Provenance→宿主保存/报告→Dispose run/source/engine。通知可以完全不读，Completion 必须仍完成；若读流，使用独立消费任务并在 Completion 后等待流关闭，不能先等无限 monitor 通知读完再停止。主操作取消与等待取消分别使用不同 token；未完成排空继续 Query/Drain，不重复提交。同步结果直接返回，未知保存查原保存端口。

消费者 A：SPC 宿主用固定量测/单位分类源调用 Moments/Capability/有限 Chart/Rules，点选只通过 ChartPoint.MemberReference 导航原查询；不从图像重测、不写放行。消费者 B：独立工程 console 用 JSON/CSV 解析后形成同样 typed 源（格式解析在 Host），只调用 Moments/UnitRate/EventRate，可不安装 WPF、DevExpress、AsunImage 或平台数据库；分别验证正常、缺口、取消、版本不兼容。同一固定输入/方法在两宿主应等价；某宿主需要产品权限/报告时另接其公开应用端口。

调用方不得在收到 `Partial`、`TimedOut` 或 `Unknown` 时将结果写成生产事实；也不得把 `MetricResult.Value == null` 改成零。已接收 operation 在 `OperationState=Draining` 或 `IsTerminal=false` 时不得被当作 `Completed`、`Cancelled`、`TimedOut`、`Failed` 或 `Unknown` 终态；必须依据排空观察继续隔离与重查。


### 9.1 完整 SPC 无 UI 夹具与双消费者

补齐 §9 调用片段的构造消费者，不重算 §11/058A 已接收的算法向量。以下是既有TestHost的文档实现规格，非本轮新增代码文件；需要System/IO/Linq/Text/Security.Cryptography/Threading/Threading.Tasks/Runtime.CompilerServices/Collections.Generic/Collections.Immutable及Asun.Modules.Statistics。复用S6 Host的S/NS/H/Ref/Closure编码原语；Closure只用于本空Gaps夹具，生产用§3/6.2全字段规则。新SPC-HOST域仅用于合成提供者自己的来源/快照定义，不重hash客户事实，不改变S6/S7域。

~~~csharp
static DefinitionReference SpcFixtureDefinition(string id, string text)
    => new(id, "1", H("SPC-HOST-DEFINITION-V1", w =>
       { S(w, id); S(w, "1"); S(w, text); }));
static void SpcNullableLong(BinaryWriter w, long? x)
{
    w.Write((byte)(x.HasValue ? 1 : 0)); if (x.HasValue) w.Write(x.Value);
}
static void SpcNullableDouble(BinaryWriter w, double? x)
{
    w.Write((byte)(x.HasValue ? 1 : 0)); if (x.HasValue) w.Write(x.Value);
}
static void SpcObservation(BinaryWriter w, StatisticsObservation o, bool contentHash)
{
    S(w, o.ObservationId); S(w, o.SourceRevision);
    if (contentHash) S(w, o.ContentHash);
    S(w, o.PhysicalUnitId); w.Write(o.ObservedAtUtc.UtcTicks);
    w.Write(o.SourceSequence); S(w, o.SegmentKey); S(w, o.StratumKey);
    S(w, o.GroupKey); w.Write(o.BreakBefore); w.Write((int)o.State);
    NS(w, o.ReasonCode); S(w, o.Unit); SpcNullableDouble(w, o.Value);
    w.Write((int)o.Classification); SpcNullableLong(w, o.EventCount);
    SpcNullableLong(w, o.OpportunityCount); SpcNullableDouble(w, o.Exposure);
    NS(w, o.EvidenceReference); S(w, o.MemberReference);
}
static void SpcInputRef(BinaryWriter w, InputReference i, bool contentHash)
{
    S(w, i.SnapshotId); S(w, i.SnapshotRevision); w.Write((int)i.Mode);
    S(w, i.QueryReceiptId); S(w, i.SourceBoundary);
    if (contentHash) S(w, i.ContentHash);
    NS(w, i.WatermarkId); w.Write(i.ReadComplete); w.Write(i.CanReplay);
}
static void SpcFixtureRequest(BinaryWriter w, StatisticsRequest r)
{
    // 完整写本夹具每个字段；明确拒绝其它方法形状，而非省略字段。
    if (r.Methods.Length != 1 || r.Methods[0].Estimator != EstimatorKind.Moments ||
        r.Methods[0].Specification is not null || r.Methods[0].Baseline is not null ||
        !r.Methods[0].Rules.IsEmpty || r.Scope.TimeRangeUtc is not null ||
        r.Subgroup.FixedSize is not null)
        throw new InvalidOperationException("Not the complete SPC fixture");
    S(w, r.OperationId); S(w, r.MetricDefinitionId);
    S(w, r.MetricDefinitionRevision); S(w, r.MethodRevision);
    var d = r.Definition;
    Ref(w, d.Identity); w.Write((int)d.Kind); S(w, d.ObservationUnitKind);
    S(w, d.MeasurandId); S(w, d.Unit); S(w, d.ExposureUnit);
    Ref(w, d.SourcePolicy); Ref(w, d.SelectionPolicy);
    w.Write((byte)(d.ObservedSubsetApproval is null ? 0 : 1));
    if (d.ObservedSubsetApproval is not null) Ref(w, d.ObservedSubsetApproval);
    Ref(w, d.AggregationPolicy);
    w.Write(r.Methods.Length);
    foreach (var m in r.Methods)
    {
        S(w, m.MetricId); Ref(w, m.Identity); w.Write((int)m.Estimator);
        w.Write(m.MinimumSamples); w.Write(m.MinimumCompleteGroups);
        w.Write((int)m.Qualification); Ref(w, m.QualificationEvidence);
        w.Write((int)m.Within); w.Write((byte)0); w.Write((byte)0);
        w.Write((int)m.Phase); w.Write(m.Rules.Length);
    }
    var s = r.Scope;
    S(w, s.ObservationUnitKind); S(w, s.MeasurandId); S(w, s.Unit);
    w.Write((byte)0); NS(w, s.MemberSetReference); S(w, s.ScopeRevision);
    NS(w, s.SpecificationRevision); NS(w, s.BaselineRevision);
    S(w, s.SourcePolicyRevision); SpcInputRef(w, r.Input, true);
    Ref(w, r.Subgroup.Identity); w.Write((byte)0);
    w.Write(r.Subgroup.MaximumSpan.Ticks); w.Write(r.Subgroup.MaximumAdjacentGap.Ticks);
    Ref(w, r.Subgroup.Qualification); w.Write((int)r.Completeness);
    w.Write((int)r.Numeric.Kind); w.Write((byte)(r.Numeric.SignificantDigits.HasValue ? 1 : 0));
    if (r.Numeric.SignificantDigits.HasValue) w.Write(r.Numeric.SignificantDigits.Value);
    w.Write(r.Numeric.AbsoluteTolerance); w.Write(r.Numeric.RelativeTolerance);
    w.Write((int)r.Numeric.Overflow);
    var b = r.Budget;
    w.Write(b.MaxRows); w.Write(b.MaxGroups); w.Write(b.MaxRowsPerGroup);
    w.Write(b.MaxChartPoints); w.Write(b.ReadBatchSize); w.Write(b.WallClockLimit.Ticks);
    w.Write(b.CancellationResponseLimit.Ticks); w.Write(b.MaxWorkingSetBytes);
    w.Write(b.MaxBufferedBytes); w.Write(b.MaxPendingBatches); w.Write(b.MaxSignals);
    w.Write(b.MaxNotifications); w.Write(b.DrainObservationLimit.Ticks);
}

var spcDefinition = SpcFixtureDefinition("metric.fixture.dimension",
    "synthetic;Continuous;mm;independent-observations;not-production-qualification");
var spcSourcePolicy = SpcFixtureDefinition("source.fixture.memory",
    "synthetic-memory;immutable-values;exact-declared-order");
var spcSelection = SpcFixtureDefinition("selection.fixture.all",
    "synthetic;all-members;no-exclusion;no-imputation");
var spcAggregation = SpcFixtureDefinition("aggregation.fixture.single",
    "single-segment;single-stratum;no-cross-layer-merge");
var spcQualification = SpcFixtureDefinition("qualification.fixture.only",
    "synthetic-fixture-only;test-assumption;not-customer-qualification");
var spcMethod = SpcFixtureDefinition("moments.fixture.v1",
    "moments-welford-v1;all-eight-components;sample-and-population-distinct");
var spcSubgroup = SpcFixtureDefinition("subgroup.fixture.none",
    "individual-description;no-within-estimator;span=1s;adjacent-gap=1s");
var spcRowsBuilder = ImmutableArray.CreateBuilder<StatisticsObservation>(4);
var spcOrigin = new DateTimeOffset(2026, 10, 12, 0, 0, 0, TimeSpan.Zero);
for (int j = 0; j < 4; ++j)
{
    string id = j.ToString(System.Globalization.CultureInfo.InvariantCulture);
    var o = new StatisticsObservation("O" + id, "r1", "", "P" + id,
        spcOrigin.AddSeconds(j), j, "segment-1", "stratum-1", "group-" + id,
        j == 0, ObservationState.Valid, null, "mm", j + 1d,
        UnitClassification.NotProvided, null, null, null,
        "fixture:spc:" + id, "member-" + id);
    string sha = H("SPC-HOST-SOURCE-V1", w => SpcObservation(w, o, false));
    spcRowsBuilder.Add(o with { ContentHash = sha });
}
var spcRows = spcRowsBuilder.MoveToImmutable();
string spcMembers = H("SPC-HOST-MEMBER-SET-V1", w =>
{
    w.Write(4); foreach (var o in spcRows) S(w, o.MemberReference);
});
var spcClosure = new InputClosure(4, spcMembers, true, true,
    "closure-spc-fixture", ImmutableArray<InputGap>.Empty);
var spcReference0 = new InputReference("snap-spc-fixture", "r1",
    InputMode.FixedSnapshot, "receipt-spc-fixture", "synthetic-memory", "",
    null, true, true);
var spcReference = spcReference0 with { ContentHash = H("SPC-HOST-INPUT-V1", w =>
{
    SpcInputRef(w, spcReference0, false); Closure(w, spcClosure);
    w.Write(spcRows.Length); foreach (var o in spcRows) SpcObservation(w, o, true);
}) };
var spcInput = new StatisticsInput(spcReference, spcRows, spcClosure, spcReference.ContentHash);
var spcMetric = new MetricDefinition(spcDefinition, ObservationKind.Continuous,
    "synthetic-observation", "dimension-x", "mm", "1", spcSourcePolicy,
    spcSelection, null, spcAggregation);
var spcMethods = ImmutableArray.Create(new StatisticalMethod("fixture-moments",
    spcMethod, EstimatorKind.Moments, 1, 1, QualificationState.Approved,
    spcQualification, WithinEstimator.None, null, null,
    BaselinePhase.EstimateCandidate, ImmutableArray<ControlRule>.Empty));
var spcBudget = new ExecutionBudget(4, 4, 4, 16, 4, TimeSpan.FromSeconds(5),
    TimeSpan.FromSeconds(1), 4_194_304, 1_048_576, 1, 16, 64, TimeSpan.FromSeconds(2));
var spcRequest = new StatisticsRequest("op-spc-fixture-a", spcDefinition.Id,
    spcDefinition.Revision, "moments-set.1", spcMetric, spcMethods,
    new StatisticsScope("synthetic-observation", "dimension-x", "mm", null,
        spcMembers, "scope-1", null, null, spcSourcePolicy.Revision),
    spcReference, new SubgroupPolicy(spcSubgroup, null,
        TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1), spcQualification),
    CompletenessPolicy.RequireAll, new NumericPolicy(NumericKind.Binary64,
        null, 0, 0, OverflowPolicy.Reject), spcBudget);

static void SpcAssert(StatisticsRequest request, StatisticsResult r)
{
    if (r.OperationId != request.OperationId || r.State != ResultState.Complete ||
        r.Input != request.Input || r.Completeness.ReadRows != 4 ||
        r.Completeness.ValidRows != 4 || r.Completeness.DuplicateRows != 0 ||
        r.Completeness.UnknownRows != 0 || r.Completeness.UnmeasuredRows != 0 ||
        r.Provenance.Backend != "managed-binary64-welford-v1" ||
        !r.CandidateBaselines.IsEmpty || r.Metrics.Length != 8)
        throw new InvalidOperationException("SPC coverage/provenance mismatch");
    var expected = new Dictionary<string, double>(StringComparer.Ordinal)
    {
        ["count"] = 4, ["mean"] = 2.5, ["m2"] = 5,
        ["sample-variance"] = 5d/3, ["sample-deviation"] = Math.Sqrt(5d/3),
        ["population-variance"] = 1.25, ["min"] = 1, ["max"] = 4
    };
    foreach (var m in r.Metrics)
    {
        string unit = m.Component == "count" ? "1" :
            m.Component is "m2" or "sample-variance" or "population-variance" ? "(mm)^2" : "mm";
        if (m.MetricId != "fixture-moments" || m.SegmentKey != "segment-1" ||
            m.StratumKey != "stratum-1" || m.Applicability != MetricApplicability.Computed ||
            m.Unit != unit || !m.Value.HasValue ||
            !expected.TryGetValue(m.Component, out double e) ||
            Math.Abs(m.Value.Value-e) > 1e-12 || !m.ChartPoints.IsEmpty ||
            m.Signals is not null && !m.Signals.Hits.IsEmpty)
            throw new InvalidOperationException("SPC component mismatch");
    }
}
// 消费者A：无需SPC页面即可调用；同步返回前局部资源已释放。
await using var spcEngineA = new StatisticsEngine(new EngineLimits(4, 4));
SpcAssert(spcRequest, spcEngineA.Compute(spcInput, spcRequest, CancellationToken.None));
// 消费者B：独立工程console，以自己的OperationId和分块源调用同一值契约。
var spcRequestB = spcRequest with { OperationId = "op-spc-fixture-b" };
var spcSourceB = new SpcFixtureSource(spcInput, 3);
await using var spcEngineB = new StatisticsEngine(new EngineLimits(4, 4));
Task<StatisticsRun> spcAcceptanceB = spcEngineB
    .ComputeAsync(spcSourceB, spcRequestB, CancellationToken.None).AsTask();
await using var spcRunB = await spcAcceptanceB;
SpcAssert(spcRequestB, await spcRunB.Completion);
var spcLookupB = await spcEngineB.QueryOperationAsync(spcRequestB.OperationId, CancellationToken.None);
if (spcLookupB.Status is null || !spcLookupB.Status.IsTerminal ||
    spcLookupB.Status.DrainState != DrainState.Drained || !spcLookupB.Status.CanReuseResources)
    throw new InvalidOperationException("SPC root not drained");
~~~

**SPC-HOST-GOLDEN-001（完整字段编码投影）。** 对上方四行夹具，按 §6.2 的 stats-core-field-v1 与上述 SPC-HOST-* 域，独立 Python struct/SHA-256 逐字段重建得到：Definition（137 bytes，`da2178dca9556c487fd3586ae3bbdeed881a9fec459626f4a5408bc40f5f129a`）；四个 SourceBody（148 bytes，hash 依次 `4522c4e48fa3f8f5b17ef6a213ed0518491e41ca28a2a473326779c9aa970275`、`948f8131ca4274d556b4c84c1095e956a33ed0b3073caa32d49b5cabd89949cb`、`a288a136ed282fb674db64b1b3fb7e21061a4d29f6a5133da47f7b70a6b1acca`、`f33953785a4da2ae147bcd56dde6b845dd5979db34bf33a3aa54b16eaf6a95ea`）；完整 SPC-HOST-INPUT-V1（994 bytes，`469bf33e2eb50d1ddc504a93882d43d72eafa2c5adc65c3b5c32bd3c9045d0b5`）；完整 SPC-REQUEST-IDENTITY-V1（1406 bytes，`c075adae560d16f89ade6c5aba30e307c76656c1f39347db83714da6ec3b0aff`）。预期值为 Count=4、Mean=2.5、M2=5、SampleVariance=5/3、PopulationVariance=1.25、Min=1、Max=4，八个 component 均 Computed 且单位按 §3.3；这些 hash 是字段重建 Golden，不是运行后端或产品快照身份。实现 Host 应在 spcRequest 构造后调用 H("SPC-REQUEST-IDENTITY-V1", w => SpcFixtureRequest(w, spcRequest))，逐项断言上述 hash/长度后再送引擎。
同一console编译单元的类型声明放在顶层语句之后；此内存源没有连接/文件/native租约，借用不可变StatisticsInput，仍逐次检查取消并遵守分块上界：

~~~csharp
sealed class SpcFixtureSource : IStatisticsInputSource
{
    readonly StatisticsInput input;
    readonly int batchSize;
    public SpcFixtureSource(StatisticsInput input, int batchSize)
    {
        if (batchSize < 1 || batchSize > 4) throw new ArgumentOutOfRangeException(nameof(batchSize));
        this.input = input; this.batchSize = batchSize;
    }
    public ValueTask<InputReference> GetReferenceAsync(CancellationToken ct)
    { ct.ThrowIfCancellationRequested(); return ValueTask.FromResult(input.Reference); }
    public ValueTask<InputClosure> GetClosureAsync(CancellationToken ct)
    { ct.ThrowIfCancellationRequested(); return ValueTask.FromResult(input.Closure); }
    public async IAsyncEnumerable<IReadOnlyList<StatisticsObservation>> ReadBatchesAsync(
        StatisticsRequest request, [EnumeratorCancellation] CancellationToken ct)
    {
        if (batchSize > request.Budget.ReadBatchSize)
            throw new StatisticsRequestRejectedException("STAT.BUDGET_EXCEEDED", "Fixture batch exceeds budget");
        for (int k=0; k<input.Observations.Length; k+=batchSize)
        {
            ct.ThrowIfCancellationRequested();
            int take=Math.Min(batchSize,input.Observations.Length-k);
            yield return input.Observations.AsSpan(k,take).ToArray();
            await Task.CompletedTask.ConfigureAwait(false);
        }
    }
}
~~~

这是正常完成路径；失败/等待到期使用下一节根Owner规则，不能依靠await using无限等待。双消费者另用本源分块1/3/4绑定既有§11.1向量，按定义替换State/Gap或Classification/OpportunityCount以验证Moments、UnitRate、EventRate的同公开接线；修改字段后必须重建本合成Source/Input/Request身份，不只换Value复用hash。子组/能力/窗口、S4矩阵及分布、S6/S7两Host分别复用其已冻结构造/向量，不把Moments正常例冒充全部方法运行通过。



### 9.2 所有宿主的有限观察与原根恢复

§9/9.1和S4/S6/S7正常路径的await using仅适用于Completion已经完成且Drained的正常退出；失败/观察超时不能依靠词法Dispose无限等待，也不在方法退出时丢原Task。各宿主在engine、Boost工厂、ComputeAsync/ComputeNumericalAsync/StartMonitorAsync开始前，从**进程级有界Owner集合**预留一个根槽。槽保存原OperationId/MonitorId、完整请求引用、engine/source/端口Owner、尚未返回的接纳/工厂Task、返回后的原run/monitor及Completion、每一个已经开始的释放Task和原业务异常；容量与EngineLimits及宿主明确上限一致，满则开始工作前拒绝。它是宿主实现状态，不新增Core公开root DTO、静态全局服务或第二回执Store。

恢复确定顺序：接纳/工厂ValueTask仅AsTask一次并立即写槽→用独立观察token/有限观察期限等待→期限到先保留槽与原Task→若原run已返回，仅对它发送幂等CancelAsync，若未返回则登记“返回后停止”意图→原Task晚返回时仅归原槽，执行该停止意图→用独立有限token观察原Completion/Query/Drain→确认原run的Drained/CanReuseResources与实际source/借用Owner结束→开始唯一Dispose Task并保存在槽→释放Task真实成功后清槽。接纳前拒绝没有run，仍须核工厂/源Owner是否已释放；工厂清理异常按§8.3取CleanupOwner/Completion原样移交。观察取消不取消原运行、释放或原接纳Task，不换OperationId/输入/版本启动副本。

每轮cleanup用请求DrainObservationLimit或宿主显式有限cleanup期限；§9.1合成夹具为2秒，只是软件测试观察限，不是生产承诺。观察仍未确认时维持隔离槽，向原进程Owner移交，移交接收确认后原方法才可结束持有责任；移交槽同样有界，容量不足不能丢根或强杀资源，停止新接纳并保留当前槽。进程Owner持续以单个原Task有限观察，不不断造Timer/Task/CTS；一次观察CTS结束时处置其本地对象，但不Dispose业务资源。业务异常先保存，cleanup错误追加Diagnostic而不覆盖原异常；释放证明不足保持Unknown/Draining。进程退出清理由OS承担，不称正常排空通过。

Monitor恢复同样强持原StartMonitorAsync接纳Task；返回后StopAsync(Drain/Cancel)按宿主原意图投递，并等待其Completion、所有已接纳窗口/源枚举器真实关闭，不能只等最后一窗或通知流关闭。持久保存属于宿主原保存OperationId，其Unknown独立查询，不拿Core已完成状态掩盖持久事务。慢/不读通知不阻止完成，但阻塞宿主回调未退出仍有在途资源；测试不能通过超时放弃回调任务。

既有Core.Tests/TestHost追加必需软件断言组 HOST-ROOT-1～6：工厂前槽容量拒绝不Load；接纳迟到返回后取消归原根；等待取消不改变worker；source.Dispose/native.Free迟到后只释放一次；cleanup失败不覆盖业务异常且原Owner可取；监测停止中窗口/源/借用kernel均释放后才清槽。测试用可控闩锁与固定时钟，不用sleep概率触发；复用§6/11/12已有反例，不创建新的产品恢复协议。


## 10. 可选 UI 契约

UI 仅是宿主投影，必须调用与无 UI 相同的入口和校验。页面建议显示：范围/观察单位/单位、固定或实时、有效/预期/缺口、分母/子组、方法/基线/规则版本、指标适用性、信号、输入/统计快照身份和下一步恢复动作。显示筛选、缩放、图表抽稀和语言切换不改变计算结果。

本模块无 WPF/DevExpress 控件 DLL，UI 实现/布局比例/控件 API/主题/键盘验收不适用于 Core；真实 SPC 页面唯一在 [UI-PCS-008](../../shared-modules/guidance/14-page-contracts/UI-PCS-008_SPC_Workspace.md)，不在这里复制页面或新增 UI 工程。Core 必须提供足够的值投影供该页实施：图点与限值→Chart，层/成员→Grid/Tree，参数与修订→只读检查器，状态与恢复→状态栏。控件选择、Docking/Flyout/SuperTip 和 DevExpress 25.2.3 签名核验属于该 Host 页切片；本轮 dxdocs 不可用且官方页面 HTTP 403，未把未经核验属性写成 API。共享页的具体布局/25.2.3 API/性能门须主会话交宿主页 Owner，不阻断 Core。

宿主接线必须把 `NumericalResult`/`MetricResult` 的 SnapshotId、OperationId、TaskId、MemberSequenceHash、Coverage、`NumericalValueState`、Diagnostic.Code/Arguments、Provenance.Backends 和 `DrainState` 原样映射到 UI-PCS-008 的投影模型；不得只传一个 double 或把 `Undefined`、`UnsupportedDomain`、`RangeLoss` 映射为零。Core 的 `Accepted`/`Running`/`Draining`/终态、InputComplete 和持久保存回执分开显示：取消/超时/端口失败/权限不足分别保留原操作并给出 Query/Retry/Refresh 等安全下一步，排空未确认时禁用重算和资源复用。UI-PCS-008 宿主负责授权、查询/保存端口、三语言资源、键盘/UIA、1920×1080 实机布局、抽稀联动、迟到响应、DevExpress 控件验收和截图/交互证据；统计 Core 只负责可消费的不可变数据、状态和错误语义。宿主关闭页面只解绑投影，是否取消由宿主命令决定；不将 UI 验收或 HTML 样例冒充 Core/现场验收。

联动键为 `(StatisticsSnapshotId, MetricId, Component, SegmentKey, StratumKey, PointId)`，不能用 Grid 行号或显示时间作为 identity；选点只更新显示，打开 MemberReference 的查询携带原输入修订及请求代次。LOD 聚合点必须显示“聚合点”及覆盖成员引用，点击先列成员再选证据，不默认第一张图；缺口断线，null 不绘0。异步证据响应同时核选择键/代次/授权，迟到响应仅归还自身租约。UI 错误显示缺输入、缺分母、样本不足、方法未支持或排空中及安全下一动作，不把全部压成“统计失败”。语言变更只格式化 MessageKey/Arguments，Core 不依赖文化或共享当前语言状态。1920×1080 的真实 UI 验证由 Host 执行，不改显示设置，也不以 HTML 证明 WPF。

命令只允许：提交明确的新计算意图、取消当前宿主任务、查询原操作、打开只读证据和切换语言。页面不得直接写统计 Store、质量事实、设备状态或放行状态；关闭页面只解绑订阅，取消由宿主显式决定。文字资源覆盖 `zh-CN`、`zh-TW`、`en-US`，短句说明发生了什么和应采取的动作，不在模块 UI 重复语言切换入口。

## 11. 案例与可判定行为

| 案例 | 输入 | 期望 |
|---|---|---|
| 正常固定输入 | 10 个有序、同单位、完整读取的观察；指标/子组/规格均已修订 | 先排空确认，再返回 `Completed`；含有效计数、值、输入/方法/参数来源和统计快照身份。 |
| 合法缺测 | 预期 10，已取得 8，2 项读取中断 | `InputCompleteness` 未完成；可返回 `Partial`/`INPUT_INCOMPLETE`，不能叫完整 10 项总体。 |
| 合法 Unknown | 10 项均读到，其中 1 项源状态 Unknown | 保留 1 项 Unknown；按政策决定指标适用性，不改成合格或 0。 |
| 首检与复测 | 6 首检通过、2 首检不通过、1 未测、1 缺回执；两项复测通过 | 首检分母仍 10，复测只能形成获批的新口径；不凑成 8/10 或 9/11。 |
| 混规格 | 同名图表但规格修订不同 | 分层或拒绝混合；样本不足只阻受影响层。 |
| 显示筛选 | 只显示 5 行或后半时间 | 只改变投影提示；原分母/基线不变；重算必须是新请求。 |
| 迟到/更正 | 已封闭窗口新增值或修改值 | 形成新输入/统计快照；旧结果不回写，保留关系和差异。 |
| 取消 | 在读取、分组、计算、输出各阶段取消 | 已接收 operation 先进入 `Draining`、`PendingOutcome=Cancelled`；排空确认前 `IsTerminal=false`，不得发 `Cancelled` 终态、返池或复用；确认 `Drained` 后才发送一次 `DrainCompleted` 并写入终态。 |
| 超时排空 | 达到请求或排空截止，仍有读取/计算/native/适配器在途 | operation 保持 `Draining`、`PendingOutcome=TimedOut`；发送 `DrainObserved`，进入隔离和重查；不得把超时当终态或并发盲重算。 |
| 重查确认释放 | 初次排空为 `TimedOut`/`Unknown`，后续逐项确认租约、回调、IO、缓冲和原生对象已释放 | 先推进 `DrainState=Drained` 并发送唯一 `DrainCompleted`，再写入 `PendingOutcome` 对应终态；`Completion` 此时才完成。 |
| native/适配器排空 | 可选 Boost Beta 调用、宿主输入源适配器或外部租约在途 | 释放证据未齐时保持隔离；未知为 `Unknown`，不得提前返池；齐全后才 `Drained`/`DrainCompleted`。 |
| 未知回执 | 宿主保存后进程退出 | 分别查询原计算 OperationId 和原保存 OperationId；未确认旧 worker 已停止不盲并发重算。已完成计算保持不可变，保存 Unknown 不生成“新成功”。 |
| 非法数值 | NaN、Inf、负分母、d>n、非正暴露量 | 返回明确错误码；不以 abs、epsilon 或默认值修复。 |

### 11.1 两种审查视角的可执行反例

以下全部是合成测试夹具，不是现场资格或用户工艺阈值。统计实现者视角核计算/缺口/方法，对外集成人视角核同一输入经入口、任务、通知、关闭到下游；共用现有 §7.3，不建立第二报告。

| 反例输入/触发 | 必须得到的结果 |
|---|---|
| Moments `[1,2,3,4]`，单层/完整成员，Binary64 | n=4，mean=2.5，M2=5，sample variance=5/3，population variance=1.25；分块1/3/4结果等价。Count 为 Int64 证据，double显示不能代替计数。 |
| `[]`、`[7]`、`[7,7]` | 空无均值；单值均值7/样本方差不可估；双常量样本方差0，能力无正 sigma，不给 Infinity/绿色资格。 |
| 完整10成员中8有数值、1Unknown、1Unmeasured；与源只返回8行且Closure.ReadComplete=false对照 | 前者读取完整、数值8、未知1/未测1；后者读不全且缺口保持。RequireAll 的依赖总体方法不可计算；获批子集 Moments 必须命名为8项子集，不能宣称10项已测或补零。 |
| 同身份/修订/hash重发；同身份/修订异hash；两个不同物理观察同值/hash | 分别去重一次、IDENTITY_CONFLICT、保留两观察；不同统计单位粒度不因两行而增分母。 |
| 相容计数 `1/1`、`0/99`；加入未知分母层；同名异单位/规格/来源 | 合并率1%；未知/不相容不输出完整合并率，原各层值/原因可见。 |
| 冻结p0=.1；p两点实际n=10和100；相同输入请求np | p逐点标准误分别√.009、.03，按058A裁切限值；中心不变；np变n不适用，不自动改p。计数资格由合成Profile明确，数值反例不证明小n正态近似合格。 |
| c/u事件3、暴露2，另一点暴露4；暴露0/Unknown | c可变暴露不适用；u首点1.5不clip为1；0/Unknown暴露不可计算，不报0。 |
| IMR `[1, Missing, 4]`；8点同侧中间等于CL；点恰等于UCL | 不跨缺口建MR/规则窗口；等CL打断同侧；等UCL不触发当前严格BeyondLimits。范围/规则变更须新修订。 |
| 冻结基线后加入极端点；Phase I第二遍源失效或CanReplay=false | 极端点保留并用原中心/限值方法评价；第二遍失效SOURCE_STALE，不能换新源/删点或承诺候选稳定。 |
| 100万行/高组基数/单组超限/全部命中；多方法或多层 | 归约数据、去重/组状态、图点/信号分别扣预算；任一超限BUDGET_EXCEEDED，不截到前N标Complete。只请求Moments不分配百万图点/全明细引用。 |
| 两宿主A/B并行，A取消/等候token取消/语言切换 | A执行取消才停A；取消等待不取消运行；B结果/资源不变，语言不改数值及Scope。 |
| 不读取Notifications，慢读、回调抛异常、回调阻塞 | Completion不依赖流读完，DroppedNotifications可见；抛异常解绑/诊断；阻塞回调未退出仍在途，不能提前Drained。 |
| 源Read/Dispose忽略取消或抛异常，Drain观察截止；随后源终于释放 | 停止后先Draining非终态，截止TimedOut/Unknown只观察；晚释放后一次DrainCompleted/终态；未确认释放不返池。 |
| Tumbling Width=Step=10秒，边界t=Origin+10秒；Sliding宽10步5；迟到/更正 | Tumbling边界只入第二窗；Sliding明确两窗口可重复但不汇总；迟到新输入修订整窗重算，旧结果不变。10/5秒仅合成夹具。 |
| 相同OperationId同闭包重入/异闭包重入；未终态Forget；已完成后Forget | 前者返回原run，异闭包拒绝；未终态不删除；已完成忘记后当前实例NotFound不表示跨进程不存在。 |
| 旧0.1 bool/decimal请求、新方法/单位/基线、读旧结果与回退 | 不猜状态/分母转换，VERSION_INCOMPATIBLE；新计算新修订，旧快照由原包读取，未准入外部契约不凭新版本获批。 |

### 11.2 资格、候选与性能的停止点

多方法请求在接受时冻结 Methods 集合和每指标支持域，不能运行后挑最好结果。弱信号/遮挡/多视觉候选由上游决定状态/身份，本模块不判断图像；若输入标Unknown仍完整保留，不以额外观察推断PASS。非正常分布、相关、近量化、缺资格时描述值与能力/控制图分别返回；保持§7.2全部高级方法限制。

Core源代码测试应按上述向量和058A既有Golden逐项核expected/actual，独立解析值优先于与同一实现比自己；异常/取消/关闭使用可控阻塞源和计数租约夹具，断言每个枚举器/批资源准确释放一次。测试目录已有消费者规划，不为本轮制造新脚本或测试文件。只有未来实际执行的结果才记录为通过。

## 12. 测试矩阵和验收断言

### 12.1 唯一纯托管测试工程与执行约定

按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)，唯一纯托管测试工程为 `tests/Modules/statistics/Asun.Modules.Statistics.Core.Tests/Asun.Modules.Statistics.Core.Tests.csproj`，固定使用 `Microsoft.NET.Sdk`、`TargetFramework=net10.0`、`OutputType=Exe`，仅引用受测 Core 工程与 .NET BCL；不添加 `PackageReference`、测试 SDK 或 NUnit/xUnit/MSTest。采用确定性断言、固定时钟、可控制的异步闩锁及计数租约夹具。最小 TestHost 是第二消费者调用示例，不代替此唯一测试入口。

工程创建后的命令从仓库根目录执行；本轮只冻结约定，不创建工程或声称命令已运行：

```powershell
dotnet build src/Modules/statistics/Asun.Modules.Statistics.Core/Asun.Modules.Statistics.Core.csproj -c Release
dotnet build tests/Modules/statistics/Asun.Modules.Statistics.Core.Tests/Asun.Modules.Statistics.Core.Tests.csproj -c Release
dotnet run --project tests/Modules/statistics/Asun.Modules.Statistics.Core.Tests/Asun.Modules.Statistics.Core.Tests.csproj -c Release
```

测试入口按本次已接收的实现切片，将 §7.1.3.8、§11 和 §12.2 的必需断言绑定到稳定用例 ID，逐项输出 ID、expected/actual 和完成状态；不得把该切片的未实现断言改成可选。全部必需断言完成且通过才返回 0；任一断言失败、未完成、必需项跳过、未处理异常或执行超时均返回非零，并列明相关用例 ID。尚未接收的外部门单独列为未执行，不据此宣称整个模块验收通过。

每个用例及整轮执行都须在启动前设置有限截止点，等待和异步夹具使用可控释放而非无限等待；外层执行器另设有限进程超时。超时须列明正在运行及尚未完成的用例 ID，记录非零失败；没有退出码或完成摘要也不得判为通过。用例等待取消或外层终止不能证明受测 worker、回调或 native 资源已排空，资源断言仍按 §5–6 核实。测试截止点是测试执行上限，不是生产性能阈值。

`dotnet test` 不执行这些 Exe，不能以其无报错代替上述运行证据。§7.1.3.6 的 Boost/native 适配验证仍在同一 Core.Tests 工程的 Adapter 用例组绑定相应构建与依赖，纯托管运行不引用或加载该适配；未运行 native 必需组不得声明分布后端通过。WPF、产品 Schema、真实 Profile、Golden/Replay 和现场资格另按适用切片验收，Core harness 不代替这些证据。

### 12.2 验证矩阵

| 层级 | 必测范围 | 通过证据 |
|---|---|---|
| Unit | Welford/合并、能力指数、控制图、分母、单位、空/单值/常值、溢出 | 固定向量、expected/actual、数值容差和诊断。 |
| Contract | 字段、版本/hash、状态/错误、Owner/Authority、序号幂等 | 唯一 Schema 校验报告；未批准候选不得伪装通过。 |
| Golden/Replay | 正常、边界、迟到、混批、重复、缺测、Unknown、重启 | 输入闭包 hash、RuntimeManifest、结果差异解释。 |
| Statistical-method | 分层分母、相容比例合并、合理子组/冻结基线、逐点 n/暴露量、信号证据/断点、重复观察/cluster、Unknown/缺失、过度离散、置信区间和跨来源比较 | 分母与 cluster/子组/baseline 关系可追溯，信号可按参与点和比较值复算；未声明方法返回 `STAT.METHOD_UNSUPPORTED`/`NotComputable`；不插补、不平均百分比、不静默汇总、不以相关替代一致性。 |
| Group-interval S6 | 独立组 `1/1`、`0/99`、配对同组、PCG seed/排序、零分母、交叉计数、退化、无效重复、取消/排空 | 两 Host 与 §7.1.3.9 Golden 完全一致；精确总分子/分母、共享索引、有效/无效重复、区间边界、覆盖诊断及退出码可复核；S6 文档规格已接收；实际 Host/Core.Tests 与运行 Golden 仍记录未执行。 |
| Integration-A | SPC 工作台无 UI 核心调用 | 同一输入能接收完整、缺口、取消/恢复结果；不写质量放行。 |
| Integration-B | 工程数据工具消费同一包 | 不依赖 SPC 页面/私表；范围、单位、版本和结果可替换。 |
| Fault | 读取中断、超时、取消、重复通知、未知保存回执、适配器丢失 | 正常Accepted/Running保持非终态；停止/结束意图后才Draining。排空超时/未知不得有operation终态、DrainCompleted或资源复用；确认全部释放后仅一条幂等完成事件。 |
| Concurrency | 两宿主并行、不同语言/方法/窗口、背压和实例关闭 | 实例数据/资源隔离；旧响应不覆盖新请求。 |
| Performance | 冷/热、行数/组数/组宽、并发、峰值内存、P50/P95/P99、取消延迟 | 目标 Profile 原始测量；未测即 `Unverified`。 |
| UI（如接入） | 1920×1080、三语、键盘/UIA、八态、抽稀、错误恢复 | WPF 实测截图/UIA/交互证据；不以 HTML 或 Mock 冒充。 |

最小验收断言：同一固定输入在不同传输分块大小、operation 调度顺序和宿主语言下产生语义一致结果；单个指标归约顺序固定，不要求任意浮点合并顺序相同。合法缺测与读取不完整可区分；Unknown/Invalid/NotApplicable/NotComputable 不变成 OK。Accepted/Running 可处于 NotStarted/非终态；停止意图后排空未确认才保持 Draining/非终态，不得有业务终态/资源复用。确认全部释放后一次 DrainCompleted，再对应终态与 Completion。第二消费者无需平台页面、私表、制程对象即可接入。

## 13. 性能预算与可观测性

本节冻结测量协议与测点，不设未经真实消费者采纳的性能达标值。每个不可变 BenchmarkProfile 必须记录唯一 ID/修订/hash、构建提交与 .NET/适配器/后端版本、OS 与 CPU/内存/存储/网络配置、带 hash 的输入集及规模分布、调用混合与并发/到达模型、队列与资源预算、时钟测点边界、故障注入点，以及 ColdSampleCount、WarmupIterationCount、MeasuredSampleCount 和各指标的验收目标/阈值来源。Profile 变更必须产生新修订，不得跨 Profile 合并数据。

冷测每个样本均从新进程/新模块实例开始，并清空模块自有缓存；OS 文件缓存、数据库缓存、外部服务和设备状态无法由模块清空时，必须记录其实际状态，使用隔离可重建夹具，不标称为冷。热测先按 Profile 固定次数执行预热，再按固定样本数测量；不使用自适应停止、只报最快值或丢弃慢样本。外部副作用操作使用可重建隔离夹具和唯一操作 ID。每个样本用单调时钟记录原始耗时；P50/P95/P99 的算法按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md) 计算，并同时报告样本数、单位和原始值。吞吐量使用 Profile 固定的观察窗口计算已完成、已排空且有效的 operation 数/时间，并单列排空中、拒绝、错误、重试和未完成项。

每轮同时记录 CPU、工作集/私有字节、托管分配与 GC、native/适配器缓冲、磁盘/网络 I/O、连接/句柄峰值，队列当前/峰值条数与字节、排队等待、积压变化、接受/拒绝/丢弃计数。排空时间从关闭新接纳开始，至在途操作、回调、IO/适配器资源全部实际归还结束；期限到达只记超时和未完成项，不得强杀后宣称排空。每项验收阈值必须引用消费者要求、正式 Contract/资源风险依据或已批准资格记录的稳定 ID；没有来源时写 TargetPending，只能报告测量结果，不得判定达标。协议/资源硬上限与性能目标分开，只有唯一权威中的必要性、数值和来源均已明确时才可作为硬上限，不从基准数据臆造上限。

### 本模块固定测点
按读取/解码、去重与分层、总体/子组累计、控制图/能力计算、序列化/持久交接及 UI 投影分别测量；禁止把读取等待隐入纯计算耗时。Profile 固定输入行数/字段宽度/空值和缺测比例、组数与每组大小、方法/分母/单位修订、分块顺序、并发合并计划、存储适配器及缓存状态。报告各阶段 P50/P95/P99 与吞吐、峰值及稳态内存、分配/GC、队列、拒绝/缺口/Unknown 计数、取消响应和真实排空时间。只有已批准消费者负载和方法计算期限可成为验收目标；其余一律 TargetPending，不得改变分母、抽样语义或结果以达标。

可执行负载计划：固定N=0/1/10⁴/10⁶（合成规模），组数1/10³及批准Profile上界；批1/4096/批准最大、源延迟0/有界慢读/取消不响应；operation并发1/2/宿主上限；Methods为Moments、比例/率、两遍候选图、冻结图+多规则。各轮分别测Current/PeakBufferedBytes、去重键数、未闭合组数、结果/图点/信号数、队列批/字节、通知降载数、在途枚举器/回调及排空观察。无原图/native Core资源计数为NotApplicable而非伪称0峰值。

MaxBufferedBytes 是自有可计数内存的硬门，字符串/引用/集合复制和预留必须纳入（实际对象开销按目标运行时测量校准），MaxWorkingSetBytes 是进程Profile测量/守卫上限，不能声称Core可靠限制宿主全进程/外部源内存。跨实例总预算由宿主限制；进程触及Profile资源上限时停止新接纳并排空，不删除旧输入。排序仅允许已有稳定源顺序，本Core不自行借磁盘无界spill。失败/超时/不完整读取及排空未知另列，不能删慢样本；预热/测量次数/最低样本与P95/P99目标未获Profile时结果NotEvaluated。无谓增量检查点、持续基线自更新和任意线程合并均不作为性能优化退路。

## 14. 发布、回退和第二消费者

发布包至少包含核心、适配器契约、版本/哈希、方法兼容矩阵、迁移说明、Golden/Replay 向量、性能证据和已知不支持域。发布前必须验证依赖版本、签名/完整性、配置引用和回退包可读；缺少正式 Contract 或真实 Profile 的切片保持 `DesignReview/Prep`。

回退按快照/方法版本回到上一已验证包；不得原地改变旧统计快照、分母或方法含义。新包产生的新统计修订与旧结果并存，报告/工具按明确版本读取。发生未知持久状态时先查原回执，再决定恢复或回退；不能用重新计算掩盖未知提交。

第二消费者验收以工程数据工具为例：它只提供自己的固定输入适配器、指标定义和预算，调用无 UI Core，读取 `StatisticsResult` 与 EvidenceRef；可以不安装 SPC 页面、不共享 SPC ViewModel/数据库、不理解任何制程对象。随后质量分析工具按同一规则验证第三消费者。两个消费者必须分别覆盖正常、缺口、取消/恢复、版本不兼容和结果范围核对。

## 15. 研究依据、限制和未决项

- 本指导是统计模块的唯一实施正文；`PKG-045_Statistics.md` 是 IM-043 应用映射，`DEV-DOM-058A_QualityControl SPC与分母定义开发指导.md` 提供 SPC 公式常数参考；平台映射边界沿用 `CONTRACT-CANDIDATES.md#statistics-contract-semantics`、`DEV-CONTRACT-002` 和独立模块架构 IM-ARCH-001，不复制第二套 Schema。
- 已比较、未采用的 HALCON tuple 路线：实际读取依据为项目内26.05.0.0 [`tuple_mean`](../../../halcon算子手册/operators/tuple_mean.html)、[`tuple_deviation`](../../../halcon算子手册/operators/tuple_deviation.html)、[`tuple_sum`](../../../halcon算子手册/operators/tuple_sum.html) 的Description/Execution Information。前两者空tuple异常，sum空tuple返回空tuple且支持字符串拼接（统计不接受）；三者independent/global但明确Processed without parallelization，不能将可跨线程调用当作单次内部并行。deviation正文未给n/n−1估计定义，不能直接接within/overall；有限tuple也不提供本模块流式累计、计数/分母、身份或资源预算契约。因此当前实施采用固定托管路线，不定义 HALCON 适配端口、工程、替代能力或待实现任务；S5产品接入同样不纳入本版Core，不将未采用路线或宿主接线记作内部欠账。没有同样本运行/峰值/取消比较，未声称任一路线更快。
- 已只读查看 [`AsunControl` 只读快照](../../references/project-snapshots/AsunControl/20261004/original)：`ClassLibrary/C_SQLite.cs` 的 `GetTableStatistics` 是表级元数据统计，不是 SPC；`Vision_Variation_Model/开发文档.md` 的均值/标准差用于图像变异模型，不提供本模块的观察单位、分母或过程能力语义。两者不作为实现或契约来源。
- PKG-045 的数值实施正文迁至 §7.1.3；固定 Math.NET 隔离移植和可选 Boost 适配为明确工程路线，不自动安装/替换依赖。qcc/NIST保留公式比较依据；研究源码/测试/营销不等于生产资格。
- 对照 `H:\docs\40-development\80-quality\统计验收与计量能力开发指导.md`（DEV-TST-003，§§4–10）：吸收了统计单位/分母分层、Unknown/缺失保留、聚类/过度离散与置信区间的通用方法门槛，以及跨来源仅按显式分层比较的约束；该文件中的 AOI 缺陷召回、误报负担、人工复判、GR&R/MSA、Bias/Linearity/Stability/Uncertainty 和客户签署门槛仍由外部 Owner 管理，不复制进 Statistics Core。
- 对照来源 `H:\docs\40-development\60-data\SPC与过程控制开发指导.md`（`DEV-SPC-001`，§3、§§6.1–6.2、§8，SHA-256 `d04dd740c3d2713a8469be7158f6b90c3c2b3075f367ce2c7f00d1f7082d5d15`）：仅吸收相容计数先合并再除法、预批准合理子组、冻结基线与逐点分母、信号参与点可追溯性，并与 `DEV-DOM-058A` 既有定义核对；来源中的 AOI 工作流、客户阈值、数据库编排、图形预算、告警事务、Nelson 全规则目录、闭端点时窗和产品闭环不作为本模块契约或实现依据。来源中的实现/验收声明不转移为本平台结论。
- 2026-10-09 网络定向研究及固定源码核对：.NET [Channels](https://learn.microsoft.com/en-us/dotnet/core/extensions/channels) 明确Wait提供背压、Drop模式丢数据；[协作取消](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads) 明确Cancel是请求，CTS.Dispose不等于任务终止。采用§6.1的数据Wait/观察降载分开、资源退出后完成，不从Task等待取消推断执行停止。
- Math.NET Numerics5.0.0固定commit `4435308e1b0efcb40dc483140059a4e3a2204044`：本轮实际对照[RunningStatistics源码](../../references/open-source/mathnet_numerics/4435308e1b0efcb40dc483140059a4e3a2204044/src/Numerics/Statistics/RunningStatistics.cs)的Push/Combine、[测试](../../references/open-source/mathnet_numerics/4435308e1b0efcb40dc483140059a4e3a2204044/src/Numerics.Tests/StatisticsTests/RunningStatisticsTests.cs)的ShortSequences/Combine，并从固定GitHub raw重新核原字节SHA-256为`01465c61b69661ba029b040c03df642085757431361b845236e93d9f0c7cb03c`/`980d923bc4e4ccd99057c8e12471b1396c84dcc9c5353cc8d5953beb5743cabd`，与现有原件相同。借稳定中心矩、样本/总体分开与退化/组合测试；空Combine返回另一个可变对象、计数乘积范围和测试部分参考非独立不能照搬，§7.1.1/11冻结值隔离、checked/有限性及独立算例。MIT许可原文已读；源码目标net6/net5/net461/net48/netstandard2.0及NUnit3.13.3/TestData测试依赖不表示.NET10集成/上游执行通过。SPC 累计只借方法/测试思想；扩展矩阵核按 §7.1.3.3 固定源作隔离移植，不直接接全局provider。
- qcc2.7固定commit `11b6ecef027c315ed547e4749949ee3a7eed502c` 定向复读R/qcc.R的p/np/c/u计数及可变sizes路径、DESCRIPTION：R≥3、MASS/utils/graphics/grDevices，GPL≥2。复用既有058A/NIST公式交叉核，禁止直接复制GPL源码或其NA去除/可变np默认行为；平台只启用批准的有限方法。其源码/依赖/hash统一复用[既有研究记录](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#spc-statistics-halcon-research-20260928)，未重复下载或声称读取/运行全上游测试。
- 组级区间首发路线复用 `DEV-AI-063 §10.2–10.3/§12.3` 的独立组、整组重采样、覆盖保留和配对共享索引约束；治理消费者的原始 `IStatisticsPort` 暂仅把 GroupBootstrap 标为不支持，本切片六项模块内文档规格已接收；实际治理桥接/实现与运行资格按原消费者门验证，本指导不改消费者文件。SciPy 固定源码 commit `b1296b9b4393e251511fe8fdd3e58c22a1124899`（BSD-3-Clause，已存 [ `_resampling.py`](../../references/open-source/scipy_scipy/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/stats/_resampling.py) 与 [`test_resampling.py`](../../references/open-source/scipy_scipy/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/stats/tests/test_resampling.py)）：实际对照 `paired=True` 的同索引采样、percentile 分位和退化 percentile `[x,x]` 测试；SciPy 的 NumPy/Generator 行为不作为本模块跨运行时契约，BCa/basic/Studentized 不移植。官方 [`scipy.stats.bootstrap`](https://docs.scipy.org/doc/scipy-1.16.2/reference/generated/scipy.stats.bootstrap.html) 与 [`numpy.quantile`](https://numpy.org/doc/2.2/reference/generated/numpy.quantile.html) 文档仅作为算法语义参考，本页另行冻结整数 q 和 Binary64 投影。
- 可复现随机流采用 PCG C minimal implementation commit `bc39cd76ac3d541e618606bcc6e1e5ba5e5e6aa3`（Apache-2.0）：已对照 [`pcg_basic.c`](https://raw.githubusercontent.com/imneme/pcg-c-basic/bc39cd76ac3d541e618606bcc6e1e5ba5e5e6aa3/pcg_basic.c) 的初始化、XSH-RR 输出和 rejection-free bounded draw、[`pcg_basic.h`](https://raw.githubusercontent.com/imneme/pcg-c-basic/bc39cd76ac3d541e618606bcc6e1e5ba5e5e6aa3/pcg_basic.h) 的状态边界及官方 [`pcg32-demo`](https://www.pcg-random.org/using-pcg-c-basic.html) 的 seed `(42,54)` 向量；源码版权/许可随实现记录。实现只在 BCL 内重写这些明确字节规则，不把 C 源码作为运行依赖。
- UI依据复用UI-PCS-008及DEV-UI-040，统计Core无UI。2026-10-09 dxdocs服务器未提供；DevExpress25.2 ChartControl/TableView官方页HTTP403，因此没有冻结其属性签名或声称版本验证通过，受影响只为宿主UI切片。本轮不新增快照/研究报告，不以竞品图形或营销推断内部算法。

待决项按影响切片分开：S1–S4 六项文档规格已由主会话接收，状态为 ModuleCoreImplementationReady（仅规格准备）。S1–S3 实际消费者的Metric/SelectionPolicy、资格/规格/基线与性能目标仍待Profile采纳（可用明确合成夹具验证Core，不编物理阈值）；S4 的公开数值 API、支持域、错误状态、后端端口、最小 Host 顺序和验证矩阵已在 §7.1.3 冻结，接收范围为已冻结 Beta 端口注入下的 Core。S4 的代码、Math.NET 隔离移植、独立 oracle、Boost ABI构建和真实后端验证尚未执行，仍为各自实现/运行资格门，不是规格缺口；S5 产品字段/序列化/权限/固定总体封口/保存回执及宿主页接线明确不纳入本版Core，由宿主在另行授权的产品接入任务中界定，不记作Core内部待补任务。S6 §7.1.3.9 的组级区间六项文档规格已于2026-10-11由主控接收，状态为 ModuleCoreImplementationReady（仅规格准备）；17项完整字段、PCG及两个精确分位的文档重建核对一致，但 BCL 实现、实际算法资格验证、Core.Tests/TestHost/运行 Golden、Benchmark 和消费者桥接均未执行。增量检查点本版明确不支持，不把待定协议挂成所有Core的阻断。生产规则/基线启用与最终放行仍由外部Owner控制。

S7 的定向官方/实际源码/测试研究、固定 mcr 版本/commit/hash、GPL不复制边界及 SciPy/NIST读取限制统一见 §7.1.3.10，未新增参考原件或平行报告。S7 六项文档规格于2026-10-11由主控接收为 ModuleCoreImplementationReady（仅规格准备）；Core实现、C#编译/Exe运行、独立数值oracle资格、Benchmark、qualification真实协议/误差比来源与桥接未执行。客户物理证据只限制真实资格应用，不阻断已明确合成输入的纯Core后续实施。

### 15.1 全模块批准范围的软件设计结论（2026-10-12）

当前独立模块架构中已批准并纳入本指导的 statistics 范围，软件设计已经闭合：Core 的 SPC/质量统计、固定数值算法、条件 t/F 端口、具名配对与分类一致性、S6 组级 percentile bootstrap、S7 ConstantRatioDeming 点估计、覆盖/分组/单位资格、完整派生 codec/Golden、同步/异步/监测生命周期、取消/超时/排空、幂等/晚到和可选 Boost Adapter 均有唯一 DTO、参数/单位/有效域、确定处理顺序、错误与 Owner、线程/资源/恢复、双消费者、反例/Golden、预算与测点。本轮补充的 §6.2、§8.3、§9.1 关闭了核心装配身份、可选 native 端口释放和完整 SPC 无 UI 双宿主构造；没有需要开发者继续猜测的内部 API、算法、编码、调度或恢复决定。

批准范围结论按能力落点如下：

| 范围 | 当前文档结论 | 仍需关闭的 Owner/门 |
|---|---|---|
| SPC Moments/UnitRate/EventRate/Capability/Xbar-R/S/I-MR/p/np/c/u、窗口和信号 | §3–7、§9–13 已冻结输入、分母、058A公式/常数、方法绑定、缺口/Unknown、基线、规则、窗口、恢复和完整 SPC Host | Statistics Core 实现、Core.Tests/TestHost、实际 Profile 的样本/规格/基线/规则批准；由 058A/质量 Owner 冻结的物理与生产门不回填为 Core 默认 |
| S4 矩阵、协方差、t/F、配对和 κ | §7.1.3.1–8 已冻结 DTO、支持域、隔离矩阵/Boost 端口、数值错误、独立 oracle、Adapter 生命周期和消费顺序 | Math.NET 隔离移植、Boost ABI/真实 DLL、独立 oracle/Golden/性能和第二消费者运行 |
| S6 组级比例/配对区间 | §7.1.3.9 已接收，PCG、非等概率拒绝、整数/分位、覆盖、取消和两 Host 已冻结 | BCL PCG 实现、运行 Golden、实际治理桥接和 Profile 性能 |
| S7 常方差比 Deming 点估计 | §7.1.3.10 已接收，误差比方向、精确中心矩、稳定白化根、RNE、完整 codec/Golden、D7-011 及两 Host 已冻结 | Core 实现、BuildHash/运行 Golden、qualification 的配对/误差比/独立误差证据和真实资格 |
| Adapter/Codec/生命周期 | §6.1–6.2、§8.1–8.3、附录 A 冻结输入源/定义/证据/保存/调度边界、family codec、snapshot/subset/point/baseline 派生身份、Boost Load/GetExport/Free/晚到和借用 Owner | 宿主按公开端口实现；实际数据库/文件/消息接线、native 构建、持久化回执和长稳 |
| UI 与图像/viewport | statistics 没有直接 viewport 或 WPF 控件消费者；§10 只冻结 Statistics→UI-PCS-008 的不可变投影字段、联动身份、三语/权限/键盘/恢复边界 | UI-PCS-008 宿主 Owner 完成 DevExpress 25.2.3、1920×1080、UIA/三语/真实数据和页面性能验收；不属于 Statistics Core 内部欠账 |
| 自动参数/视觉路线 | 统计模块不消费图像、不提供视觉自动参数、不接 HALCON；自动选模、自动调参、鲁棒/加权/异方差/通用 ODR 明确不支持 | 无本模块软件欠账；若未来新增必须新方法/契约/消费者和独立准入 |

因此，当前批准范围没有仍需本会话决定的内部软件设计欠账。剩余项目是实现/运行资格或外部 Owner 事实：C# Core/TestHost、矩阵移植、Boost/DLL、真实 Golden/Replay/Benchmark、数据库/证据/保存宿主接线、UI-PCS-008 真实 WPF 验收，以及 qualification/质量 Owner 的物理假设、基线、阈值、配对和客户资格。它们不能通过降低 DEV-GOV-010 门禁或把合成夹具称作生产证据来关闭。S5 产品源/保存/报告及宿主页接线继续不纳入本版 Core；X-Ray/CT、ICT、FCT 和视觉自动参数继续按项目入口暂缓。


## 16. 自审清单（本版本）

- [x] 核心职责、禁止边界和无 UI 入口明确。
- [x] 输入/输出、强类型参数、单位、范围和默认值已写出；质量阈值无批准默认值。
- [x] 同步/异步、事件顺序、状态、错误码、取消/超时/排空、线程和资源所有权已写出。
- [x] 版本、适配器、无 UI 示例、可选 UI、正常/边界/失败案例已写出。
- [x] 测试矩阵、性能预算、可观测性、发布/回退和第二消费者已写出。
- [x] 未写入制程判定、质量放行、目标关联、工艺解释或设备副作用。
- [x] Accepted/Running与Draining分开；停止意图后实际排空未确认保持Draining/非终态，只有已确认释放后唯一DrainCompleted/终态；同步调用不伪造异步排空。
- [x] 已吸收 DEV-TST-003 可独立复用的统计方法门槛；AOI 产品指标与计量签署仍保持外部 Owner 边界。
- [x] 本轮按统计反例与外部接入两种视角核了DTO、分母、窗口、资源、调用示例及失败链；定向文件链接/锚点/表格/类型引用检查与内容自审分开，不以结构检查代替公式/状态审查。
- [x] S1–S4 明确标记 `ModuleCoreImplementationReady`（主控已接收，仅规格准备），S5 明确不纳入本版Core，未采用HALCON路线及宿主接线不列为内部待实现任务；S6 标记 `ModuleCoreImplementationReady`（2026-10-11 主控接收，仅规格准备）；未声称实现或生产通过。
- [x] S7 两轮定向文档自审：①实现者链核DTO/方差比方向/精确中心矩/稳定根/投影/不可识别与失败恢复；②空宿主链核公开签名、完整来源/请求/预算/身份及原异步Owner。独立Python重建全部27项长度/hash及145字节Expected，Fraction/120位Decimal核正常/负向/含噪/大偏置与比值边界、72组含噪稳定根及交换/单位变换（该样本最大相对差3.34e-16）；Markdown围栏/锚点、切片表连续性与旧正文hash定向核对一致。S1–S4/S6正文及S6 17项Golden/PCG/编码保持原文；未编译/执行C#、未运行性能或消费者资格，这些静态核对不替代主控接收；S7六项文档规格已于2026-10-11由主控接收为ModuleCoreImplementationReady（仅规格准备）。
- [x] 全批准范围收口：复核 §3–§7 的SPC/数值/Bootstrap/Deming/覆盖与分组，§6.2 的派生身份/codec，§8.1–8.3 的适配器与Boost装配释放，§9/9.1/9.2 的双消费者与原根恢复，§10 的无直接UI边界，以及§11–§15 的反例、Golden、预算、Owner和停止点；已明确当前无需本会话补猜的内部软件设计欠账。实际代码、native/矩阵移植、数据库/证据/保存接线、WPF宿主和客户/物理资格仍保持各自运行门，未因文档结论变为Ready。


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

## 附录 A：Module API Contract v0.3（逐切片准入）

本节定义本独立模块的核心代码边界，优先于正文中仅针对产品集成的“候选/待采纳”措辞。本文已给出的公开类型、方法、事件、错误键、状态、参数表和代码形状，作为对应切片获准后唯一实施依据；本附录的存在不代表准入通过。实现者不得另造第二套核心 DTO、状态机或错误语义。

- `Module API Contract v0.3` 只覆盖无产品事实写入的 Core、Simulator 和显式 Adapter Port。它不把平台 C-01～C-08、客户工艺阈值、最终放行、产品数据库字段或厂商私有类型冻结为模块 API。
- 正文中仍称“候选”的内容，若属于平台 Schema 映射、序列化、Owner、生产资格或客户 Profile，继续保持候选；若属于本模块 Core 的字段/方法/事件/错误/资源语义，则按本节冻结，任何未定义操作必须先补回本指导再编码。
- 当前后端只按 §7.1 固定路线和 §7.1.3 已冻结端口实施；未采用的比较路线仅作为 §15 研究依据，不形成候选实施能力。
- 本附录区分规格准备、主任务接收与实现/运行资格。具体 Core 切片在本指导明确实现范围、命名空间、唯一代码/测试工程、允许/禁止路径，并逐项满足 DEV-GOV-010 §3.1 六项条件且由主任务接收后，才可标记为 `ModuleCoreImplementationReady`。六项规格齐全但尚未接收时记录“规格准备齐全、待主会话接收”；仅存在实际规格缺口时记录 `PreparationIncomplete`。代码、构建或运行尚未执行须另行记录，不作为规格缺口，也不据规格接收宣称实现或资格通过。

### A.1 Core public entry points

S7 新增公开 ConstantRatioDemingTask/Result 及尺度矩/诊断/明细，唯一形状与两个宿主顺序见 [§7.1.3.10](#constant-ratio-deming)；仍复用同一 NumericalRequest/INumericalStatistics/NumericalRun，不新增入口或运行根。新family编码独立，旧tag/hash/请求不重解释，暂不支持同请求混family。S7六项文档规格已于2026-10-11由主控接收为ModuleCoreImplementationReady（仅规格准备），不从此导航声明已实现。

本附录与 §3、§7.1.3 同属 Core 0.3 的一套 API：§3 定义 SPC 输入/结果/源端口，以下接口冻结正文第4节 SPC 入口；§7.1.3.1–2 定义数值请求/结果、`INumericalStatistics`、`NumericalRun`、查询/通知与能力声明，§7.1.3.3/6 定义矩阵/Beta 后端端口，§7.1.3.9 定义 S6 组级区间任务与结果。数值调用顺序与断言见 §7.1.3.8–9，唯一测试执行约定见 §12.1；不在附录复制第二份数值声明。资源未释放意味着 IsTerminal=false，不意味着 Accepted/Running 要改为 Draining；仅停止/结束意图后走 Draining。终态状态必有 DrainState=Drained、CanReuseResources=true。同步调用无 operation 登记/通知，返回前已释放局部资源。

```csharp
public interface IStatisticsEngine : IAsyncDisposable
{
    StatisticsCapabilities Capabilities { get; }
    StatisticsResult Compute(
        StatisticsInput input,
        StatisticsRequest request,
        CancellationToken cancellationToken);

    ValueTask<StatisticsRun> ComputeAsync(
        IStatisticsInputSource source,
        StatisticsRequest request,
        CancellationToken cancellationToken,
        IProgress<StatisticsProgress>? progress = null);

    ValueTask<IStatisticsMonitor> StartMonitorAsync(
        IStatisticsWindowSource source,
        StatisticsMonitorRequest request,
        CancellationToken cancellationToken);

    ValueTask<StatisticsOperationLookupResult> QueryOperationAsync(
        string operationId,
        CancellationToken cancellationToken);

    ValueTask<StatisticsDrainResult> DrainAsync(
        DateTimeOffset deadlineUtc,
        CancellationToken cancellationToken);

    ValueTask ForgetOperationAsync(
        string operationId, CancellationToken cancellationToken);
}

public abstract class StatisticsRun : IAsyncDisposable
{
    public abstract string OperationId { get; }
    public abstract Task<StatisticsResult> Completion { get; }
    public abstract IAsyncEnumerable<StatisticsNotification> Notifications { get; }
    public abstract ValueTask CancelAsync(CancellationToken cancellationToken);
    public abstract ValueTask DisposeAsync();
}

public sealed record StatisticsProgress(
    string OperationId, long Sequence, string Phase,
    long ItemsProcessed, long? ItemsExpected, TimeSpan Elapsed);

public sealed record StatisticsNotification(
    string OperationId, long Sequence, string Kind,
    StatisticsOperationStatus? Status, StatisticsProgress? Progress,
    StatisticsDrainObservation? Drain, StatisticsResult? Result,
    long DroppedNotifications);

public sealed record StatisticsOperationLookupResult(
    string OperationId, OperationLookupState LookupState,
    StatisticsOperationStatus? Status, StatisticsResult? Result);

public enum OperationLookupState { Found, NotFound, Unknown }

public interface IStatisticsOperationReceiptSource
{
    ValueTask<StatisticsOperationLookupResult> QueryAsync(
        string operationId, CancellationToken cancellationToken);
}

public sealed record EngineLimits(int MaxOperations, int MaxRetainedResults);
public sealed record StatisticsCapabilities(
    string CoreApiVersion, string ImplementationVersion, string Backend,
    ImmutableArray<EstimatorKind> Estimators,
    ImmutableArray<RuleKind> Rules,
    ImmutableArray<DefinitionReference> Constants);
public sealed class StatisticsRequestRejectedException : Exception
{
    public string Code { get; }
    public StatisticsRequestRejectedException(string code, string message) : base(message)
        => Code = code;
}
```

实现类为 `public sealed class StatisticsEngine : IStatisticsEngine, INumericalStatistics`，构造签名 `StatisticsEngine(EngineLimits limits, IStatisticsOperationReceiptSource? receiptSource = null, NumericalBackendPorts? numericalBackends = null)`，不从 DI/全局取依赖；未注入 Beta 端口时仅拒绝依赖 t/F 的任务，不影响描述性数值任务。Limits 两项≥1，MaxRetainedResults≤MaxOperations；capacity 满接纳前返回 BUDGET_EXCEEDED，已经接纳任务的诊断/资源记录不能被清掉。Engine 可同时管理多个 operation，同一 run 通知单读，GetStatus/Query/Drain 并发只读状态快照，不修改结果。

`IStatisticsEngine.Capabilities`（`StatisticsCapabilities`）只读暴露本包已实现的 SPC 方法/规则集合及058A所列精度常数的确切内容身份；实现把表/公式代码随本包固定，用确定性编码生成常数内容hash后发布，调用方从此取Constants引用，不凭示例臆造hash。资格/规格/审批不在Capabilities。SPC 后端固定 `managed-binary64-welford-v1`；数值扩展的 `NumericalCapabilities` 按 §7.1.3.2–6、S6 的 §7.1.3.9 独立声明 TaskKinds、Policy、SupportDomain 和 Backends，不将 SPC 后端身份套给矩阵、Beta 或组级区间。API 0.3、实现包版本与方法/后端版本分开记录；不支持的后端/常数ID不得用“版本差不多”采纳。实现前这些声明仍为设计准备，不是既有可运行代码。

以下查询/通知规则针对本节的 SPC 类型：LookupState=Found 时 Status 非空，只有已终态才提供 Result；NotFound/Unknown 的 Status/Result 为 null，不以两个空值猜成功。`StatisticsNotification.Result` 仅允许 OutputReturned（待定、不能提交）或 WindowCompleted（该窗口已排空）；其它 Kind 为 null。Completion 正常完成返回 StatisticsResult，包括 Cancelled/TimedOut/Failed，而非仅成功 Task；接纳前拒绝抛上述稳定异常。CancellationToken 若接纳前已取消按请求拒绝返回 STAT.CANCELLED，无 Accepted；接纳后取消先停止/排空再返回 Cancelled 结果。读取源异常也由 Failed 结果保留诊断，不让未观察 Task 异常绕过排空。数值查询/通知使用 §7.1.3.2 的类型与顺序，不继承 SPC 的窗口监测能力。

同步入口只处理冻结内存输入；异步入口拥有读取枚举器、自有缓冲和任务，借用 source/receipt 对象，不拥有宿主连接/文件/窗口。StartMonitorAsync 不共享实例窗口。DrainAsync/QueryOperationAsync 的调用 token 只控制本次等待，不能取消已启动释放；排空观察截止达成返回 TimedOut/Unknown 后仍由 engine 保留 in-flight 记录并继续观察。已出现停止意图且 DrainState!=Drained 才保持 Draining；Accepted/Running 原样查询。确认释放时唯一 DrainCompleted→唯一业务终态→Completion→通知流关闭。统计结果仍只是一份能力投影，不写放行或设备命令。

### A.2 版本迁移与逐切片六项准备结论

0.1 的 decimal/bool 观察及未知默认政策不能可靠迁为 0.3：必须由原源证据补充 State、Classification、暴露/机会、方法/资格、Closure；缺失时返回 VERSION_INCOMPATIBLE，不以 IsValid=false猜 Unknown/Invalid、也不把 decimal转换误写成 Decimal128。旧结果按原包/方法只读，保留原 hash；新计算用新 OperationId/API revision，两版本并存，回退不修改旧值。Core 不负责 JSON 格式解析或数据库迁移。

0.2→0.3 保留 §3 的 SPC 字段语义与形状，但本版公共 API 新增 §7.1.3 数值入口/端口并扩展 StatisticsEngine 构造签名；不能据字段相同声明包/二进制兼容。宿主须显式核对 API 与方法版本并使用经验证的版本适配；数值入口仅按 0.3 契约调用。旧 0.2 结果保留原 API/方法/后端身份及 hash，不改标为 0.3；按 0.3 重算须形成新 OperationId 和统计快照关系。文档版本 `0.3.0-prep` 表示设计准备，`CoreApiVersion`/`NumericalCapabilities.ApiVersion` 所指 API 为 `0.3`，实现包的 SemVer 与构建身份须在实际发布时另行记录。

| 切片 | 六项定位与准备结论 | 仍需的接收/外部门 |
|---|---|---|
| S1 值契约、累计、分母/完整性、同步计算 | ①职责/两消费者§1/9；②完整值类型§3/A.1；③BCL Host§9；④向量/错误§11/12；⑤负载/预算§13；⑥唯一工程/路径开头。主会话六项规格接收通过：ModuleCoreImplementationReady（仅规格准备） | 代码/build/test 尚未执行；物理阈值不阻断纯描述夹具 |
| S2 能力、子组、Phase I/II与有限控制规则 | 同六项位置，并消费058A唯一公式/表及§7.1.1/12向量；主会话六项规格接收通过：ModuleCoreImplementationReady（仅规格准备） | 实现/运行验证尚未执行；生产资格、实际样本/基线/规则批准仅限制生产方法 |
| S3 异步分块、幂等、取消/排空、窗口监测 | 同六项位置及§6.1/7.1.2/A.1，端口源/批所有权、通知背压、容量与失败断言已确定；主会话六项规格接收通过：ModuleCoreImplementationReady（仅规格准备） | 最小Host有界源/阻塞源/关闭注入验收未执行；持久回执/源重连产品映射后续接入 |
| S4 数值扩展（计量/具名配对） | §7.1.3.1–8 已冻结职责、公开 DTO/入口、支持域、QR/SVD/EVD/Beta 端口、数值错误、样例、验证矩阵、预算与唯一落点；主会话六项规格接收通过：ModuleCoreImplementationReady（仅规格准备），范围为已冻结 Beta 端口注入下的 Core | 实现、Math.NET 隔离移植、Boost ABI/构建、独立高精度 oracle、真实后端、Core.Tests 运行和第二消费者验证尚未执行，仍为各自实现/运行资格门，不记为 PreparationIncomplete 或规格缺口 |
| S5 产品源/保存/报告及宿主页 | 边界和消费者已定位，明确不纳入本版Core；HALCON替代路线未采用，不定义适配工程或内部待实现任务 | 平台Schema/源封口与权限/保存查询/报告关系、UI008真实25.2.3/1920×1080要求由宿主在另行授权的产品接入任务中定义/验收；不作为本版Core内部欠账，不标 ImplementationSpecificationReady |
| S6 组级比例与配对区间 | §7.1.3.9 已冻结 `group-percentile-bootstrap-v1` 的公开 DTO/入口复用、独立组预检、PCG32 字节规则、线性分位插值、精确比值/配对差、退化/零分母、两 Host、Golden、关闭与 Benchmark 断言；六项文档规格于2026-10-11主控内容接收通过：ModuleCoreImplementationReady（仅规格准备） | 实现、PCG BCL 重写、两 Host/Core.Tests/运行 Golden、实际算法资格验证、真实治理桥接和 Profile 尚未执行；主控独立文档字段/有理数重建核对一致，不代表C#运行；不回退 S1–S4，不声明资格/生产 CI |
| S7 常方差比 Deming 点估计 | §7.1.3.10 六项定位：①qualification与独立工程Host消费者/边界；②完整DTO/ratio方向/单位/支持域/稳定根/状态与原执行根；③两Host完整来源与请求/结果断言；④全字段hash/数值Golden与D7-001–022；⑤deming-point-managed-v1 BenchmarkProfile；⑥复用唯一Core/Core.Tests/TestHost与§12.1执行约定。六项文档规格于2026-10-11由主控接收为ModuleCoreImplementationReady（仅规格准备） | 规格接收不代表实现或运行资格通过；实现/C#构建/Exe与数值资格/Benchmark未执行；真实资格的配对/误差比/独立假设证据及消费者桥接另接，不扩CI/权重/异方差范围 |

以上状态依据主控本轮接收结论：S1–S4 六项文档规格接收通过，标记 ModuleCoreImplementationReady（仅规格准备）；S5 明确不纳入本版Core（宿主产品接入另行界定）；S6 六项文档规格已于2026-10-11主控接收为 ModuleCoreImplementationReady（仅规格准备），均未标 ImplementationSpecificationReady。S7六项文档规格已于2026-10-11由主控接收为ModuleCoreImplementationReady（仅规格准备）。规格接收不代表代码、构建、oracle、真实后端、Golden/Replay、性能、UI或生产验收通过；各自未执行事实及外部门继续保留，不因状态同步删除或视为完成。
