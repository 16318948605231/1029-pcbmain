# Imaging Optimization（曝光、增益与照明优化）开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2, C3`

- 模块：IM-042；来源：PKG-061
- 文档版本：0.2.6-prep；状态：DesignReview/Prep（全部批准范围的可决定文档设计已闭合，见§18；未实现、未生产验证）
- 规划消费者：独立视觉工程试验台、AOI/钢网成像优化适配器。
- 本文是脱离本平台仍可接入的唯一实施依据；不得把制程判定、质量放行或设备安全策略写入本模块。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/imaging-optimization/Asun.Modules.ImagingOptimization.Core/Asun.Modules.ImagingOptimization.Core.csproj`；namespace：`Asun.Modules.ImagingOptimization`。预定测试工程：`tests/Modules/imaging-optimization/Asun.Modules.ImagingOptimization.Core.Tests/Asun.Modules.ImagingOptimization.Core.Tests.csproj`。上述项目尚未创建。
- 允许变更范围：仅上述 Core 和测试工程目录；在明确获准的实现切片中，必要的新文件也只能放入这两个目录。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续适配/UI获准切片的唯一规划工程：`src/Modules/imaging-optimization/Asun.Modules.ImagingOptimization.Adapters/Asun.Modules.ImagingOptimization.Adapters.csproj`（namespace `Asun.Modules.ImagingOptimization.Adapters`，AsunImage/离线adapter）、`src/Modules/imaging-optimization/Asun.Modules.ImagingOptimization.UI.Wpf/Asun.Modules.ImagingOptimization.UI.Wpf.csproj`（namespace同工程名）、对应测试分别`tests/Modules/imaging-optimization/Asun.Modules.ImagingOptimization.Adapters.Tests/Asun.Modules.ImagingOptimization.Adapters.Tests.csproj`及`tests/Modules/imaging-optimization/Asun.Modules.ImagingOptimization.UI.Wpf.Tests/Asun.Modules.ImagingOptimization.UI.Wpf.Tests.csproj`。本轮均不创建；Core准入不授权这些目录，只能在各切片明确获准后允许修改其对应工程/测试；厂商SDK/产品Shell仍禁止。
- 后续获准的实现任务应把创建Core与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 当前逐切片状态（2026-10-10主控内容接收）：C1/C2/C3=`ModuleCoreImplementationReady`，既有DEV-GOV-010 §3.1六项规格接收继续有效；主控已完整回读0.2.4 §9.4–9.6并接收U1指导内容，本次无新增内部设计欠账。U1仍`PreparationIncomplete/NotReady`，不提升为`ModuleCoreImplementationReady`；真实WPF/三语/UIA/图像native桥/性能和产品接入资格未关闭。A1/A2仍`PreparationIncomplete`。设备/产品Profile未采纳，实际实施范围仍须明确派发，本轮不创建工程；不是构建、测试、集成或生产资格通过声明。

- 本轮限定内容接收（2026-10-11）：主控已回读§16.4–16.10及最新§16.8清理链/IO.QB.10，接收A1-Q公开质量桥/精确原量支持与A2-R离线settings/完整分母、双Host/Owner恢复的确定指导内容。A1/A2整体仍`PreparationIncomplete`；此接收不提升整模块、真实AsunImage/质量后端/设备存储或UI资格，不标适配/UI为无UI CoreReady。实际实现/消费编译及Native、真实样本/参数用途、持久化/设备HIL/WPF/性能门见§16.10；image-quality 0.6.0-prep服务六项接收只作为上游规格，C1/C2/C3/U1既有接收保持。

- 全模块文档准备结论（2026-10-12）：按当前架构的完整批准能力核实，Core/codec、有限参数建议与受控试采、评价/离线Adapter、实时/持久端口及可选UI的可决定软件设计无剩余欠账。补缺仅为§6.3试采交接/置信解释、§9.7现有CPU预览端口实施路线及§9.8三语资源闭合；依据和覆盖结论见§18。本原会话完成内容审核、修复与定向文档验证，总控只登记状态，不再等待其内容复核。文档闭合不授予代码/运行或生产资格，不改变C1/C2/C3与A1/A2/U1原准入状态。

## 1. 目标与边界

模块负责把已批准的成像参数空间转换为可复现的有限候选，按预算和硬约束安排观察，接收调用方提供的原始观察和质量评价，维护候选、非支配集合、独立验证和可解释建议。核心是纯编排与计算，可在无 UI、无相机、无数据库环境运行。

模块不拥有相机或光源句柄、原始帧、设备配置写权、目标关联、工艺解释、缺陷规则、最终质量判定、程序发布、报警确认、运动互锁或任何设备副作用。实时适配器由宿主持有设备 Owner 和独占租约；离线适配器只能读取历史观察。调用方负责流程、目标与试件关联、质量放行和设备命令。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.ImagingOptimization.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"核心是纯编排与计算，可在无 UI、无相机、无数据库环境运行"。

**Blazor/Web**：成像参数候选建议通过 gRPC/REST 推送到 Web 看板；参数采纳必须经 `parameter-editor` 和人工确认，不经浏览器直接写入生产配置。

**AI 参数学习集成**：本模块提供 L1 离线参数搜索能力（Optuna/Hyperband）；`ai-dataset-governance` §7.4 的 L1 搜索调用本模块，结果作为 `ParameterSuggestion` 经 `parameter-editor` 确认后生效。本模块不持有推理 tile 租约。

**HALCON 双跑**：成像质量评估依赖 `image-quality` 模块；本模块核心是纯数值搜索，无 HALCON 算子路线；HALCON 备选 CI 不涉及本模块核心。

## 2. 依赖与算法路线

公开依赖仅为参数或配置校验、诊断记录和质量评价回调。视觉评价由调用方通过 ImageLibDotNet/AsunImage 提供；HALCON 26.05 算子均经 `ImageLibDotNet` 的 `cv2` 调用，不另接 HOperatorSet/halcondotnet.dll，不核验封装是否包含算子或检查内部。intensity、gray_histo_abs、min_max_gray、deviation_image、entropy_gray、area_center_gray 等评价路线的输入域、参数范围和版本行为以项目 halcon算子手册/operators 为准；仅 C# 参数类型、重载或封送确有歧义时查看公共签名或在消费项目编译确认。这些算子只产生评价数据，不能改变候选安全约束。输入域、资源或适配端口能力不满足时显式返回不可用，不自行实现平行视觉算法。

搜索基线为确定性的有限合法集合惰性枚举、批准先验排序和可选局部细化；不默认引入 Bayesian、TPE、NSGA 或深度模型。任何高级后端只能提出候选，仍经过同一物理约束、去重、观察、评价和独立验证。

## 3. 公开强类型契约（Module API Contract v0.2）

本轮修订的是尚无实现/消费者程序集的v0.1草案，整体替换为v0.2；0.2.6-prep为当前未发布指导修订，未建立旧v0.2消费者兼容承诺。旧DTO不再是另一份活动契约。命名空间 `Asun.Modules.ImagingOptimization`，目标 .NET 10；以下是拟实现的公开 C# 声明，不是现有程序集 API。不可变快照、内容身份及端口语义与 §3.1–§8 一起构成契约。平台 Schema 仅在宿主映射。

```csharp
public readonly record struct ExposureUs(long Value);
public readonly record struct GainDb(decimal Value);
public readonly record struct LightLevel(decimal Value, LightLevelUnit Unit);
public enum LightLevelUnit
{ NativeCode, RelativePercent, CurrentMilliampere, PulseWidthMicrosecond }
public readonly record struct TemperatureC(double Value);
public readonly record struct DurationMs(long Value);
public enum AxisKind { Exposure, Gain, LightLevel, LightEnabled }
public sealed record AxisTarget(string StepId, AxisKind Kind, string? ChannelId);
public sealed record ParameterAxis(string AxisId, AxisTarget Target, string Unit,
    IReadOnlyList<decimal> AllowedValues, bool Locked, string SourceRevision);
public sealed record AxisCapability(AxisTarget Target, string Unit,
    IReadOnlyList<decimal> AllowedValues, string? ReferenceScale, string QuantizationEvidenceRef);
public sealed record CapabilitySnapshot(string Revision, string ContentHash,
    IReadOnlyList<AxisCapability> Axes, int MaxParallelObservations);
public sealed record ConstraintSnapshot(string Revision, string ContentHash,
    string RulesEvidenceRef);
public sealed record ExposureStep(string StepId, ExposureUs Exposure, GainDb Gain,
    IReadOnlyList<LightSetting> Lights, string Mode, int SequenceIndex);
public sealed record LightSetting(string ChannelId, LightLevel Level, bool Enabled);
public sealed record Candidate(string CandidateId, IReadOnlyList<ExposureStep> Steps,
    string SpaceRevision, string ConstraintRevision, string IdentityHash);
    public sealed record Budget(
        int MaxTrials,
        long MaxCandidates,
        DurationMs? MaxWallTime,
        DurationMs MaxStageTime,
        DurationMs MaxDrainTime,
        double? MaxEnergyJ,
        TemperatureC? MaxTemperatureC,
        int MaxConcurrentObservations,
        long MaxSummaryItems,
        long MaxEventQueueItems,
        long MaxMemoryBytes,
        long MaxDiskBytes);
    public sealed record BenchmarkProfile(
        string ProfileId,
        string ProfileRevision,
        string DatasetRevision,
        string RuntimeFingerprint,
        string HardwareFingerprint,
        string CollectorVersion,
        int WarmupIterations,
        int MeasurementIterations,
        int MinimumValidSamples,
        bool MeasureCold,
        int ConcurrentOperations,
        DurationMs SampleDeadline,
        Budget ResourceLimits,
        IReadOnlyList<BenchmarkInputSize> InputSizes,
        string ClockAndAffinityPolicy,
        string StatisticPolicy,
        IReadOnlyList<BenchmarkTarget> Targets);
    public sealed record BenchmarkInputSize(string Name, long Value);
    public sealed record BenchmarkTarget(
        string MetricId,
        string Statistic,
        string TargetReference,
        string AcceptanceRevision);

public enum SearchPolicy
{ BaselineOnly, DeterministicMixedRadix, DeterministicLocalRefinement, CandidateProposalOnly }
public enum ObservationPhase { Search, Verification }
public sealed record ValidationCell(string CellId, string TargetRef, string MethodRef,
    string SpecimenRef, string ConditionRef, string IndependenceGroup,
    ObservationPhase Phase, int Repetitions, IReadOnlyList<string> ObjectiveIds,
    IReadOnlyList<AxisOffset> Offsets);
public sealed record AxisOffset(AxisTarget Target, int CapabilityIndexOffset);
public sealed record ValidationPlan(string Revision, string ContentHash,
    IReadOnlyList<ValidationCell> Cells, IReadOnlyList<string> VerifyCandidateIds);
public sealed record SearchOptions(string Revision, IReadOnlyList<Candidate> PriorCandidates,
    int MaxRefinementRounds, string? ProposalRevision);
public sealed record OptimizationRequest(string OperationId, string Purpose,
    string ContractVersion, string SpaceRevision, CapabilitySnapshot Capability,
    ConstraintSnapshot Constraints, IReadOnlyList<ParameterAxis> Axes, Candidate Baseline,
    IReadOnlyList<MethodObjective> Objectives, ValidationPlan Validation,
    Budget Budget, SearchPolicy Search, SearchOptions SearchOptions,
    string InputRevision, IReadOnlyList<string> RequiredEvidenceIds);
public sealed record OptimizationPlan(OptimizationRequest Request, string ObservationRevision,
    string EvaluatorRevision, string StoreRevision, string? ProposalRevision, string PlanHash);
public sealed record MethodObjective(string ObjectiveId, string TargetRef, string MethodRef,
    ObjectiveDirection Direction,
    string Unit, bool Required, double? Lower, double? Upper, string MethodRevision);
public enum ObjectiveDirection { Minimize, Maximize }
public sealed record ObservationRequest(string OperationId, string ObservationId,
    Candidate Candidate, ValidationCell Cell, int RepetitionIndex, long AttemptIndex,
    IReadOnlyList<ExposureStep> RequestedSettings, string PlanHash, Budget Limits);
public enum ObservationState { Accepted, Rejected, Failed, Unknown }
public sealed record FrameEvidence(string EvidenceId, string PhysicalAcquisitionId,
    string IndependenceGroup, string StepId, string EvidenceRef, string ContentHash);
public sealed record ObservationUsage(double? EnergyJ, TemperatureC? PeakTemperature);
public sealed record ObservationReceipt(string OperationId, string ObservationId,
    string CandidateId, string CellId, ObservationState State,
    IReadOnlyList<FrameEvidence> Evidence, IReadOnlyList<ExposureStep> ActualSettings,
    string ActualSettingsHash, ObservationUsage Usage,
    DateTimeOffset StartedUtc, DateTimeOffset? CompletedUtc, string? DiagnosticId);
public enum ValueValidity { Valid, Missing, NotObservable, OutOfDomain, Invalid }
public sealed record ObjectiveValue(string ObjectiveId, double? Value, string Unit,
    ValueValidity Validity, string? Reason, string MethodRevision,
    IReadOnlyList<string> EvidenceIds);
public sealed record Evaluation(string ObservationId, string CellId,
    IReadOnlyList<ObjectiveValue> Values, IReadOnlyList<string> HardFailures,
    bool Complete, string EvaluatorRevision);
public sealed record CandidateSummary(string CandidateId, string IdentityHash,
    IReadOnlyList<ObjectiveValue> SearchVector, IReadOnlyList<string> ValidEvidenceIds,
    bool IndependentlyVerified, IReadOnlyList<string> Gaps);
public enum RecommendationState
{ NoCandidate, CandidateFrontier, IndependentlyVerified, NeedsReview, Cancelled }
public sealed record Recommendation(RecommendationState State,
    IReadOnlyList<CandidateSummary> Candidates, IReadOnlyList<string> Gaps,
    string SelectionPolicyRevision);
public sealed record ValidationIssue(string Code, string Path, string Message);
public sealed record ValidationResult(bool IsValid, IReadOnlyList<ValidationIssue> Issues,
    OptimizationPlan? Plan);
public sealed record SearchCursor(string PlanHash, string Branch, string NextOrdinal);
public sealed record PreviewResult(IReadOnlyList<Candidate> Candidates,
    SearchCursor? NextCursor, bool Exhausted, IReadOnlyList<string> UnsearchedRanges);
public enum OptimizationRunState
{ Created, Validating, Ready, Observing, Evaluating, Frontier, Verifying,
  Cancelling, Draining, Drained, ResourcesReleased, Completed, Cancelled,
  Failed, ReconcileRequired }
public sealed record OptimizationResult(string OperationId, string PlanHash,
    OptimizationRunState State, Recommendation Recommendation, string StopReason,
    bool SearchComplete, long LastSequence, bool ResourcesReleased);
public enum LookupState { Found, NotFound, Unavailable }
public sealed record RecommendationResult(LookupState Lookup, string OperationId,
    Recommendation? Recommendation, bool IsFinal, string? DiagnosticId);
public sealed record DrainReceipt(string OperationId, bool Drained,
    bool ResourcesReleased, IReadOnlyList<string> UnresolvedIds, string? DiagnosticId);
public sealed record ConstraintDecision(bool Allowed, IReadOnlyList<string> Failures,
    double? WorstEnergyJ, TemperatureC? WorstTemperature);
public sealed record ProposalBatch(IReadOnlyList<Candidate> Candidates,
    string? NextToken, bool Exhausted, string Revision);
public abstract record EventPayload;
public sealed record PlanPayload(OptimizationPlan Plan) : EventPayload;
public sealed record CandidatePayload(Candidate Candidate, SearchCursor? NextCursor) : EventPayload;
public sealed record IntentPayload(ObservationRequest Request) : EventPayload;
public sealed record ReceiptPayload(ObservationReceipt Receipt) : EventPayload;
public sealed record EvaluationPayload(Evaluation Evaluation) : EventPayload;
public sealed record RecommendationPayload(Recommendation Recommendation) : EventPayload;
public sealed record SearchCheckpointPayload(SearchCursor? Cursor, int RefinementRound,
    string? ProposalToken, long Generated, long Trials, double EnergyJ) : EventPayload;
public sealed record StatePayload(OptimizationRunState State, string Reason,
    IReadOnlyList<string> UnresolvedIds) : EventPayload;
public sealed record OptimizationEvent(string OperationId, string EventId, long Sequence,
    EventPayload Payload, string PayloadDigest, DateTimeOffset TimestampUtc);
public sealed record StoreReceipt(bool Accepted, bool Durable, long LastSequence,
    string? DiagnosticId);
public sealed record EventPage(LookupState Lookup, IReadOnlyList<OptimizationEvent> Items,
    long LastSequence, bool HasMore, string? DiagnosticId);
public sealed record ResultLookup(LookupState Lookup, OptimizationResult? Result,
    string? DiagnosticId);
public interface IConstraintPolicy
{
    string Revision { get; }
    string ContentHash { get; }
    ConstraintDecision Check(Candidate candidate, IReadOnlyList<ExposureStep> settings);
}
public sealed record OptimizerOptions(int MaxOwnedTasks, int ControlTaskReserve,
    int MaxConcurrentQueries, DurationMs QueryDeadline, int QueryPageSize,
    long QueryMaxMemoryBytes, DurationMs CleanupObservationLimit, InputLimits InputLimits);
public sealed record InputLimits(long MaxTextUtf8Bytes, long MaxCollectionItems,
    long MaxInputUtf8Bytes);
public sealed record ResourceCharge(long MemoryBytes, long DiskBytes,
    long SummaryItems, long EventItems);
public interface IResourceReservation : IDisposable
{
    void CommitDisk(long writtenBytes);
}
public interface IResourceQuota
{
    bool TryReserve(ResourceCharge charge, out IResourceReservation? reservation);
}
public sealed record PortContext(string OperationId, Budget Limits, IResourceQuota Quota);
public interface ICandidateProposalPort
{
    string Revision { get; }
    ValueTask<ProposalBatch> ProposeAsync(OptimizationPlan plan,
        IReadOnlyList<CandidateSummary> history, string? token, int limit, PortContext context,
        CancellationToken cancellationToken);
    ValueTask<DrainReceipt> DrainAsync(string operationId, PortContext context, CancellationToken cancellationToken);
}
public interface IObservationPort
{
    string Revision { get; }
    ValueTask<ObservationReceipt> ObserveAsync(ObservationRequest request, PortContext context,
        CancellationToken cancellationToken);
    ValueTask<ObservationReceipt> ReconcileAsync(ObservationRequest originalRequest, PortContext context,
        CancellationToken cancellationToken);
    ValueTask<DrainReceipt> DrainAsync(string operationId, PortContext context, CancellationToken cancellationToken);
}
public interface IEvaluationAdapter
{
    string Revision { get; }
    ValueTask<Evaluation> EvaluateAsync(ObservationRequest request,
        ObservationReceipt observation, PortContext context, CancellationToken cancellationToken);
    ValueTask<DrainReceipt> DrainAsync(string operationId, PortContext context, CancellationToken cancellationToken);
}
public interface IResultStore
{
    string Revision { get; }
    ValueTask<StoreReceipt> AppendAsync(OptimizationEvent @event, long expectedSequence, PortContext context,
        CancellationToken cancellationToken);
    ValueTask<StoreReceipt> CommitAsync(OptimizationResult result, long expectedSequence, PortContext context,
        CancellationToken cancellationToken);
    ValueTask<EventPage> ReadAsync(string operationId, long afterSequence, int limit, IResourceQuota quota,
        CancellationToken cancellationToken);
    ValueTask<ResultLookup> ReadResultAsync(string operationId, IResourceQuota quota,
        CancellationToken cancellationToken);
}
public sealed record OptimizerServices(IConstraintPolicy Constraints,
    IObservationPort Observations, IEvaluationAdapter Evaluator, IResultStore Store,
    ICandidateProposalPort? Proposal);
```

### 3.0 标识、轴和快照的唯一解释

- 所有必需 ID/ref/revision 非空（可选null/无意义空集合按各字段规定），按 ordinal 大小写敏感比较；枚举未知值拒绝。OperationId 由宿主生成并永久不复用。集合入口做深快照，不接受底层集合运行中被修改。请求ContractVersion固定`0.2`；观察/评价/store/Proposal各Revision固化在Plan；端口Revision属性必须为纯读取、无I/O，绑定内容变更须新修订，后续不一致按IO-012停止。Capability.ContentHash重算只能证明表内容，不能证明真实设备资格。
- 一个 AxisTarget 恰对应基线一个 Step 和一种参数；曝光/增益 ChannelId 必须为 null，光源必须指定现有 ChannelId。Mode、StepId、SequenceIndex、通道集合在一个 SpaceRevision 内固定，不作为隐含自由轴；不同模式显式开启不同请求，不再存在未定义“分支轮转”。轴按请求顺序，AllowedValues 升序且不重复、非空；搜索集合须为能力集合子集，SourceRevision 等于能力 Revision。曝光值为非负整数且可转 long；增益/照明 decimal 不做浮点 tick 推断；LightEnabled 单位 `bool`、只允许 0/1。Locked 轴只含基线值。未出现的轴保持基线。能力本身为冻结的有限离散表；范围/步长由宿主展开并检查后传入，Core 不同时解释 Min/Max/Step/AllowedValues 两套规则。没有变化轴只可显式 BaselineOnly。能力表须覆盖基线所有设置、各目标唯一，所有基线档位属于能力及搜索表（若该轴存在）；AxisCapability.QuantizationEvidenceRef为量化来源必需引用，RelativePercent的ReferenceScale必填，其余为null或显式设备标尺；任何Step/Channel重复或缺少能力拒绝。
- 每个 ExposureStep 的序号连续从 0 起、ID 唯一；Lights 按 ChannelId ordinal 排序、唯一。单位为 Exposure=`us`、Gain=`dB`、LightEnabled=`bool`；LightLevel 单位字符串须等于 LightLevelUnit 枚举名，实际值及 ReferenceScale 见 §3.1。关闭光源仍保留其 Level 供身份重演，不将 0 默认为关闭。
- Candidate.IdentityHash 是 SHA-256 小写十六进制：按序写 SpaceRevision、ConstraintRevision、步骤及通道完整设置，排除 CandidateId/OperationId。哈希对象键精确为Candidate身份`SpaceRevision,ConstraintRevision,Steps`、ActualSettings为裸Steps数组、其它record按声明字段序（hash自身字段排除）；用Utf8JsonWriter显式按上述顺序写无缩进 JSON；枚举写名称，decimal 用 invariant `G29` 字符串，整数 JSON number，double以invariant `R`字符串（-0统一为0，非有限拒绝），bool JSON boolean，UTC时间为统一UTC的`O`字符串，null显式写出、列表保序、record按本节字段顺序。EventPayload先写`Type`判别名称再写`Data`字段，不序列化CLR程序集名。字符串原值不做大小写/Unicode归一，使用默认JSON encoder；canonical格式版本为`io-canonical-v1`。PlanHash 用同法写完整请求（包括 OperationId）及 Observation/Constraints/Evaluator/Store/Proposal的绑定修订（ObservationRevision/EvaluatorRevision/StoreRevision/ProposalRevision显式放Plan，Constraints绑定使用请求快照）；字典不用作身份输入。候选IdentityHash、PlanHash、能力/验证快照ContentHash入口重算核对：能力/验证快照各排除自身ContentHash字段；PlanHash排除自身PlanHash，按Request/ObservationRevision/EvaluatorRevision/StoreRevision/ProposalRevision顺序写；PayloadDigest仅对完整Payload（不含事件元数据）计算。Constraints.ContentHash由纯策略声明与请求逐字一致，Core不从RulesEvidenceRef读文件重算外部规则；Evidence.ContentHash只校验格式并由宿主检验原件。不能把含自身hash的对象循环hash；Core候选ID为 `c-` 加完整 IdentityHash。基线也使用此 ID。ActualSettingsHash只写ActualSettings的步骤数组（同设置canonical，不含SpaceRevision/ConstraintRevision），逐字段与RequestedSettings比对成功才接纳。Evidence.ContentHash 的原图算法由上游定义，Core 不重读原图。
- ValidationCell 是目标×方法×试件×条件的一个显式格子；至少一Search格，请求验证时至少一Verification格，CellId/ObjectiveIds唯一，Repetitions正整数。ObjectiveIds非空且每项目标的TargetRef/MethodRef与格子相同；每个Required目标在Search及已请求的Verification阶段都至少一格，不遗漏请求声明的格子。MethodObjective绑定唯一TargetRef、MethodRef及MethodRevision；同一格只评价列出的目标，未列目标不算Missing；不同方法产生不同ObjectiveId，不跨方法混汇总。
- 搜索格Offsets为空；验证格空Offsets表示名义，否则只允许对Exposure/Gain/LightLevel按Capability.AllowedValues索引作已冻结有符号整数档位偏移，AxisTarget唯一、不得为Locked轴或LightEnabled。以每个被验证候选的名义档位索引为中心，checked相加后必须在能力表内，逐轴生成完整RequestedSettings；不能按搜索子集索引、clip、换单位或替换成另一固定候选。扰动幅度/合法域来自验证Profile，不造通用值；越界/约束失败生成该Cell缺口而非曝光。扰动结果挂回名义候选，IdentityHash不改变，ActualSettingsHash按该RequestedSettings核对。独立性由宿主给出物理分组证据，搜索组与验证组不得重叠；不能用随机 ID 代替分组验证。VerifyCandidateIds 可为空表示本次只搜索、不验证；预选候选不在前沿则报告缺口，不自动换另一候选。Cells不允许运行中补格；每个Evidence.PhysicalAcquisitionId需包含上游源身份/设备generation/触发链的稳定关联，宿主证据解析器核验其IndependenceGroup等于请求格组。内容hash相同本身不证明同一物理帧，内容hash不同也不证明不同采集。搜索结束后如需人工选择，以新 OperationId 和明确历史来源复演/验证，不能改在途计划。

### 3.0.1 公开 codec / 工厂路径（同 Core 程序集，拟实现）

宿主不猜内部hash helper。唯一公开工厂为`ImagingContractCodec`静态类；下面是签名表（实施时补方法体，分号不代表可直接编译的静态方法源）。下列方法都先执行§3.2预检查/资源计量，非法结构/额度抛ImagingOptimizationException且不返回半快照；hash字段仅工厂产出，不自动修改外部事实。输入draft的ContentHash必须为空（专门用于建新快照）；Seal方法返回深冻结副本并补hash，重复验hash使用Encode方法，不重新Seal旧事实。CreateCandidate输出完整hash及`c-`ID。Plan只由`optimizer.Validate(request).Plan`产出，Codec不绑定服务、不生成获批Plan。

```csharp
public static class ImagingContractCodec
{
    public static CapabilitySnapshot SealCapability(CapabilitySnapshot draft,
        Budget budget, InputLimits limits);
    public static ValidationPlan SealValidation(ValidationPlan draft,
        Budget budget, InputLimits limits);
    public static Candidate CreateCandidate(string spaceRevision, string constraintRevision,
        IReadOnlyList<ExposureStep> steps, Budget budget, InputLimits limits);
    public static byte[] EncodeCandidateIdentity(Candidate candidate, Budget budget, InputLimits limits);
    public static byte[] EncodeCapabilityContent(CapabilitySnapshot capability, Budget budget, InputLimits limits);
    public static byte[] EncodeValidationContent(ValidationPlan validation, Budget budget, InputLimits limits);
    public static byte[] EncodePlanContent(OptimizationPlan plan, Budget budget, InputLimits limits);
    public static byte[] EncodeActualSettings(IReadOnlyList<ExposureStep> steps, Budget budget, InputLimits limits);
}
```

返回byte[]归调用方；Core内部流式hash使用同字节规则且不要求先分配全部序列化数组。Encode只输出canonical内容，不解释设备真伪。wrapper值类型按其record声明写对象（如ExposureUs/DurationMs为`{"Value":100}`、GainDb为`{"Value":"0"}`、LightLevel为`{"Value":"1","Unit":"NativeCode"}`），不能另一次写成裸scalar。外部证据hash不由这些工厂代生成。

<a id="31-参数单位范围默认值"></a>
### 3.1 参数单位、范围与预算语义

设备能力必须提供每轴合法离散值、单位及量化来源；模块默认不假定厂商范围。设备轴合法值表、单位或其量化来源缺失时请求无效；Core只消费已展开离散表，不接收有歧义的连续范围。ExposureUs 为非负整数微秒，实际上限、允许档位和基线值全部由能力快照提供；模块不编造通用上限，0 不代表关闭。GainDb 仅接受适配器声明的有限档位，禁止自动按 20*log10 转换；`LightSetting.Enabled=false` 表示关闭，启用时的 `LightLevel.Unit` 必须同时满足以下语义：`NativeCode` 是设备定义的离散码，只能按能力快照中的允许值比较，禁止算术换算；`RelativePercent` 是相对某个由能力快照声明的标尺，范围和 0/100 端点由该标尺定义，不表示照度或电流；`CurrentMilliampere` 只表示光源驱动电流；`PulseWidthMicrosecond` 只表示脉冲宽度。四者不得互换、线性推导或跨通道比较，能力快照必须记录单位、允许值、参考标尺（如适用）和量化规则。`Budget` 的每个字段都必须由调用方或部署配置显式传入；可选的能量、温度或完整运行时间限制用显式 null 表示不适用，不由 Core 填默认值。正值规则适用于试验数、候选数、时长、并发、摘要、事件队列、内存和磁盘额度；MaxEnergyJ若非null必须有限且>0，MaxTemperatureC若非null必须有限（摄氏可为负，真实可用范围来自设备Profile），Capability.MaxParallelObservations正整数。SearchOptions在local模式MaxRefinementRounds>0，其它模式必须0；BaselineOnly不允许PriorCandidates（必须空），其它模式先验限MaxCandidates/MaxSummaryItems且IdentityHash唯一；ProposalRevision仅proposal模式非null，先验去重/完整设置、Revision必需。调用方配置并将具体值写入计划快照，Core 不设置静态上限。`MaxTrials` 限制观察尝试，`MaxCandidates` 限制生成/返回的候选规模，预览、摘要、队列和其他暂存数据分别受对应额度约束。

宿主连续输入先按设备tick展开为精确decimal允许表，并提供量化来源；Core不自动舍入；超界、非步进或锁定值在执行前分别返回 IO-002 ParameterOutOfRange / IO-003 LockedAxisConflict，不得写设备后静默夹紧。完整受影响曝光组作为一个候选；同一量化设置只保留一个搜索候选，但预先声明的独立复测仍单独计数。

### 3.2 同步 Validate / Preview / Codec 的先检查后分配门

不等Run创建Quota。入口先读取request.Budget的固定标量及Options.InputLimits（Codec显式传参），按§3.1校验；缺Budget/任何非法预算即IO-001，不复制列表、不遍历大文本、不调用Constraint。InputLimits三个正值由宿主显式传入，无默认：单个ID/ref/revision/Mode/诊断文本UTF8字节<=MaxTextUtf8Bytes；任何列表Count<=MaxCollectionItems且全图逻辑条目累计<=Budget.MaxSummaryItems，字符访问工作另受总UTF8字节门与deadline约束；总canonical UTF8估计/实际<=min(MaxInputUtf8Bytes,Budget.MaxMemoryBytes)。空与超限分别IO-001/007；超限返回一个固定错误（path+code），不拼接超大输入进错误消息。重复/非法Unicode代理字符拒绝，UTF8按Unicode scalar/合法代理对计数，原字符串保持原样，不作Normalization。

遍历只接受BCL数组/冻结数组或经入口复制的List/ReadOnlyCollection；传入任意自定义IReadOnlyList的Count/indexer若不可证明O(1)无I/O则IO-001，不执行其用户getter/枚举器。请求类型为本节sealed record，无可注入任意对象图；嵌套深度由声明固定；仍以reference身份记录已走集合防循环/别名重复遍历，各字段列表索引逐项计数，引用循环IO-001，共享只读列表按每处逻辑条目计量不逃额度。预扫逐字段计算string.UTF8长度/JSON转义上界（默认encoder最多6字节/UTF16单元），不调用GetBytes/ToArray/LINQ先聚合；首个不符即停。checked累计包括hash/去重表/深复制原与副本同时存活的内存、每值/条目实测类型尺寸+保守托管开销，分配前保留足量Quota；不能以宿主已经分配了输入为自己不计额的理由。64位累计溢出IO-007。

一次Validate/Preview/Codec从入口起采用单调MaxStageTime，固定处理量批次（至多256次标量/字符访问，只是检查间隔不是设备/部署上限）之间检查deadline及计数，预算/截止到期Validate给Issue无Plan，Preview/Codec抛IO-007；不生成超额度部分Plan。SHA256/Utf8JsonWriter按有界块增量写，对byte[]返回亦先计全量上界；预检查和最终实际长度双核验。Validate使用请求预算，Preview先检查Plan.Request.Budget再验Plan；Plan未验前不信任其hash。纯ConstraintPolicy.Check必须是已绑定的本机快速确定纯策略，每个candidate检查前/后查deadline，不准阻塞I/O、Thread.Sleep/native/无界循环；按合法轴/steps/通道规模有界计算。同步方法无法抢占恶意策略：不合作策略属适配契约失败，harness外层进程deadline隔离并判失败，绝不通过Task.Run遗留计算声称deadline已满足。Validate不调用store/设备；异常内部快速策略映射IO-004/006，不猜允许。

## 4. 调用入口、事件和状态

拟实现 `ImagingOptimizer(OptimizerServices services, OptimizerOptions options)`，构造时校验options/非空端口、建立实例内有界Task Owner后保存端口；不调用设备或初始化窗口。Options全部显式传入：MaxOwnedTasks>=3、ControlTaskReserve>=2且小于MaxOwnedTasks，MaxConcurrentQueries>0且不超过普通task槽数，QueryDeadline/QueryPageSize/QueryMaxMemoryBytes/CleanupObservationLimit及InputLimits正值，无隐藏默认。普通查询/观察/评价/提议/写入只用普通槽，至少两个预留控制槽只供对账/排空；槽不足先背压/IO-007，不调用端口。Query配额中DiskBytes/EventItems为0、SummaryItems上限为QueryPageSize，所有嵌套载荷仍受QueryMaxMemoryBytes；单条Result/Plan超过额限返回Unavailable/IO-007，不拆半条事实。实例可查询多个历史 OperationId，但最多推进一个运行/恢复操作；重复活动调用 IO-016。端口由宿主持有并释放，optimizer.DisposeAsync 只关闭本实例、排空自己发出的任务；不 Dispose 注入服务。公开入口固定：

```csharp
public interface IImagingOptimizer : IAsyncDisposable
{
    ValidationResult Validate(OptimizationRequest request);
    PreviewResult PreviewNext(OptimizationPlan plan, SearchCursor? cursor, int limit);
    ValueTask<OptimizationResult> RunAsync(OptimizationPlan plan,
        IProgress<OptimizationEvent>? progress, CancellationToken cancellationToken);
    ValueTask<RecommendationResult> GetRecommendationAsync(string operationId,
        CancellationToken cancellationToken);
    ValueTask<EventPage> GetEventsAsync(string operationId, long afterSequence, int limit,
        CancellationToken cancellationToken);
    ValueTask<OptimizationResult> RecoverAsync(string operationId,
        IProgress<OptimizationEvent>? progress, CancellationToken cancellationToken);
    ValueTask<DrainReceipt> CancelAsync(string operationId, CancellationToken cancellationToken);
    ValueTask<DrainReceipt> CloseAsync(CancellationToken cancellationToken);
}
```

Validate/PreviewNext 为纯计算，不调用观察、评价、store 或 Proposal；ConstraintPolicy.Check 必须纯、确定、无 I/O，只消费已绑定 RulesEvidenceRef 对应的冻结规则。Validate 输出 Plan 或路径化 Issues。Run 再校验 PlanHash/端口修订，在 store 中不存在该 OperationId 才接纳；相同ID的活动计划不重复执行（IO-016）；同hash已提交返回原Result且端口调用为零，同hash未提交返回IO-017要求Recover；异hash返回IO-012。首次PlanPayload通过expectedSequence=0的原子Append接纳，不能凭Read不存在的检查规避跨实例CAS。Validate 不证明资料当前获准，宿主在 Run 前完成适用性门，观察端口每次取得证据时再次核验。

PreviewNext：首次 cursor=null；limit 为正整数且不超过 MaxCandidates/MaxSummaryItems 和内存余量。Cursor 包含 PlanHash、Branch=`baseline`/`prior`/`mixed`、NextOrdinal（分别为该阶段列表索引/组合ordinal）；NextOrdinal 为无符号十进制 BigInteger 文本（无前导零，0 例外）；按 §6 顺序推进，预算不足/输入游标异hash/ordinal越域抛IO-007/012/001。每页最多扫描limit个阶段位置（包含已出现在基线/先验的mixed组合与非法组合），不是无限扫描到凑足limit个合法输出；非法/重复也推进ordinal，页可为空但NextCursor前进。mixed阶段只需与基线/有限先验hash比较即可跨页去重，mixed本身不同ordinal唯一，不靠隐藏游标对象/累计预览集合；Exhausted 只表示有限集合走完，阶段依次baseline→prior→mixed，游标明确转阶段；结束NextCursor=null，未搜索范围表示阶段及未枚举ordinal段。预览不消耗运行 MaxCandidates/MaxTrials，单次预览仍受同样资源额度。BaselineOnly 仅一项；局部/建议模式预览仍可分页查看默认有限空间，页在UnsearchedRanges标注“动态运行顺序依赖评价/建议”，不能把该页当动态策略运行顺序。

### 4.1 持久事件与结果

事件时间仅诊断不参与候选/计划身份；EventId、OperationId、Sequence及TimestampUtc由Core在第一次生成时固定，重复写必须传同一完整事件，不能重取当前时间。事件载荷不是摘要替身。Sequence 从 1 连续递增；EventId=`OperationId/Sequence`；PayloadDigest 按 §3.0 的 canonical 规则计算。载荷判别名就是具体 record 类型名，禁止任意 type-name反射反序列化。Append 使用 expectedSequence CAS；同 EventId 同 digest 返回原 Durable 回执，不增加序号；同 ID 异内容拒绝。Accepted && Durable且LastSequence==事件Sequence才可推进；expectedSequence为事件Sequence-1，重复Append原回执可以有原Sequence，但后续必须读出实际尾序号后继续CAS。ReadAsync返回afterSequence之后连续的至多limit条，EventPage.LastSequence为本页最后返回序号（空页为afterSequence），HasMore严格表示冻结读取快照中还有后续事件；并发追加可下次再读，新tail不回退，gap/digest冲突IO-018。ReadResult Found必须有非null Result/一致OperationId与PlanHash；NotFound/Unavailable必须null，Unavailable带DiagnosticId。Commit重复同OperationId/PlanHash/LastSequence/完整result为幂等成功，异result拒绝；不能“最后写入覆盖”。内存 store 只供模拟并明确“进程内耐久”，不得用于设备任务。

最终ResourcesReleased事件表示设备/native/活动计算/借用已归还，允许其后的有界终态写入和Commit尚在进行；IsFinal与Run返回ResourcesReleased=true仍要求最终store原Task和Core临时输出完成。最终提交后的progress只入界限已冻结的UI投影，不再持运行资源；progress未结束/未知必须留非final而不能先提交最终成功。终态事件可耐久但Commit未达成时只读查询非final。

最小事件链：PlanPayload → CandidatePayload → IntentPayload → ReceiptPayload → EvaluationPayload → RecommendationPayload（工程前沿）→ StatePayload(Verifying，如有) → 验证意图/回执/评价 → StatePayload(Draining) → StatePayload(Drained) → StatePayload(ResourcesReleased) → RecommendationPayload（最终）→ StatePayload(Completed/Cancelled/Failed)。候选、观察和评价可多次出现；每次副作用前必须耐久 Intent，回执/评价必须耐久后才能进入前沿。最终 Commit 的 LastSequence 指终态事件，CAS 不再递增；失败保持存储缺口，不显示已保存完成。Check/Preview 不发事件。

不再有排空前的 RecommendationReady：进度中的前沿始终为工程候选。任何最终 IndependentlyVerified 和 IsFinal=true 均要求无未决 ID、观察/评价/Proposal 全部 Drained 且 ResourcesReleased、终态事件与 Commit 已耐久。GetEventsAsync使用同QueryDeadline/QueryPageSize/QueryMaxMemoryBytes和原Task登记规则；limit正值且不超QueryPageSize、afterSequence非负，返回事件页用于历史/UI证据展开，NotFound/Unavailable不造空完成。返回DTO深快照已无native借用，Caller拥有返回后内存并须有界消费，模块不替调用方无限保留返回值。GetRecommendationAsync在活跃实例返回最近耐久投影，IsFinal=false；已终态且Commit耐久的同实例查询返回原结果IsFinal=true；新实例先 ReadResult，未提交则分页 Read/replay，仍 IsFinal=false。NotFound 与 Unavailable 分开，Recommendation=null，不能都变成 NoCandidate。终态历史查询仅表达当时证据，不证明当前设备适用性。

### 4.2 未知、迟到和恢复

ObservationId 在 Intent 之前确定为 `OperationId/AttemptIndex`，AttemptIndex 从 0 连续增加，包含搜索/验证及所有失败尝试；Request 保存完整候选、Cell、RequestedSettings、PlanHash 和 Limits。Observe/Reconcile 均以此原请求为幂等边界；同 ID 异请求 IO-012，不再依赖超时后才拿到的 ID。端口收到重复调用只回原事实，不再曝光；离线端口不触发设备。Accepted要求CompletedUtc非null且>=StartedUtc、完整实际设置/每一步证据及ActualSettingsHash；Rejected表示端口确认未触发设备（完成时间可有、Evidence/ActualSettings为空、ActualSettingsHash空字符串、usage为确认的零能量/null温度），Failed表示已知失败可带已发生步骤证据，Unknown表示设备结果尚未确定。Failed/Unknown不得伪造未读字段，未读列表为空、ActualSettingsHash空字符串、CompletedUtc=null；有已确认的部分事实保留但不进入评价。未知usage为null，不能填0。这里空串仅这类不可用hash允许，不违反必需ID规则。评价只接收Accepted且完整关联回执。Rejected/Failed记录该Cell缺口后可按冻结预算继续其它候选；端口未知、EvidenceConflict、版本/安全/持久化错误停止全运行、先对账。单候选缺目标/NotObservable只拒该候选，不能把候选拒识误作整个设备安全错误。

正常运行态按 Created→Validating→Ready→Observing/Evaluating/Frontier（允许循环）→Verifying（可省）→Draining→Drained→ResourcesReleased→Completed。取消先 Cancelling 再排空后 Cancelled；错误先排空后 Failed；超时/未知/native未归还进入 ReconcileRequired，未排空时ResourcesReleased=false、IsFinal=false；观察事实Unknown但所有工作确已排空时ResourcesReleased=true、仍IsFinal=false，未决ObservationId不得因此清除。这是暂停对账态而非可重新搜索的终态；不得复用设备租约或自动恢复配置。

RecoverAsync 读取耐久计划和有界事件页，验证序号/digest/契约及绑定修订，逐个未决 Intent 调用 ReconcileAsync，再排空所有端口；已 Accepted/评价过的观察不再 Observe。恢复不继续搜索、验证或生成新候选；成功归还后以旧停止原因（重启中断为 Failed/IO-017）提交保守 NeedsReview/NoCandidate/Cancelled；新试验须新 OperationId。若版本不匹配只允许历史只读查询，设备对账交旧适配器/宿主，不能换新版偷偷重触发。

迟到回执在 ReconcileRequired 中只允许与同 ID 的原意图对账，Unknown→已知可追加事实，已知→不同事实判冲突；终态后只记宿主诊断，不修改已提交推荐、事件事实或再启动运行。所有任务句柄由 Owner 跟踪至结束，不是超时后 fire-and-forget。CancelAsync 取消运行意图且可重复；其 token 只取消调用方等待，不撤销已记录的取消。CloseAsync 原子拒绝新运行，执行相同排空，可重复；超时返回未决列表并允许继续 Close/Recover。DisposeAsync使用Options.CleanupObservationLimit作为本次关闭调用的外层观察上限；当前原Run/已读Plan的排空窗另受该计划MaxDrainTime，未知时抛模块错误 IO-014 并保留宿主恢复责任，不能在 finally 伪称释放成功。

progress的Report为同步接口、没有可查询回调task；Core只登记其自有有界dispatch调用，不Task.Run无限通知。UI传入的progress实现必须同步只入其有界投影队列，不在Report里执行耗时/设备/无界Dispatcher.Post；超时仍跟踪原Report调用且无最终资源释放，宿主不合作不能伪称安全排空。进度按耐久 Sequence 通知，无 UI 时可为 null；回调异常隔离记录、不回滚事实、不直接重入运行。队列满先背压；可合并 UI 投影但不能丢 store 事实。回调不得阻塞设备排空或持有实例锁。

## 5. 错误码与恢复

稳定错误码：IO-001 InvalidRequest；IO-002 ParameterOutOfRange；IO-003 LockedAxisConflict；IO-004 ConstraintViolation（联合电流、占空、温升或时序）；IO-005 ObjectiveUnavailable；IO-006 CapabilityUnavailable；IO-007 BudgetExhausted；IO-008 ObservationFailed；IO-009 ObservationUnknown；IO-010 EvaluationIncomplete；IO-011 EvidenceMissing；IO-012 VersionMismatch；IO-013 Cancelled；IO-014 DrainTimeout；IO-015 PersistenceUnavailable；IO-016 ReentrantOperation；IO-017 Interrupted；IO-018 EvidenceConflict；IO-019 UnsupportedSearchPolicy；IO-020 OperationNotFound。ValidationIssue.Code/Path/Message 表示入口错误；异步入口抛拟实现的 `ImagingOptimizationException : Exception`（构造参数 `string code, string? operationId, string stage, bool retryable, string? diagnosticId, string recoveryAction, Exception? innerException`；同名首字母大写只读属性，其中Retryable为bool，其余为string/string?；Message为错误Code的稳定开发诊断，UI由资源映射，不把异常Message直显），运行接纳后的停止原因进入结果/StatePayload，不用异常丢弃已接纳事实。未知不等于失败或通过。

验证失败不触发设备；约束失败跳过候选并记录原因；观察失败保留已发生动作和证据；未知回执必须进入对账；排空超时保持 ReconcileRequired，禁止恢复原配置或继续搜索；持久化失败停止新副作用并导出内存摘要。取消、失败、成功均由宿主执行同一清理和设备恢复策略，恢复前检查 Owner、generation 和配置 CAS。

## 6. 搜索、评价与验证规则

### 6.0 有限搜索、局部细化及建议端口

1. Validate 固化全请求及端口修订，核对能力、基线、轴唯一性、必需目标、验证矩阵、显式预算；联合约束策略 hash 必须匹配请求。仅一次性冻结快照，不读取全局配置。所有后续候选与验证扰动再次 Check。
2. 默认先基线，然后 SearchOptions.PriorCandidates 的完整显式先验（逐项校验当前空间/全设置hash，不反求hash对应组合），再请求轴顺序的 mixed-radix：最后一个轴变化最快，各档位升序。全设置 hash 去重，基线/先验出现过的组合直接跳过；以 BigInteger 计组合数和 ordinal，不分配笛卡尔积、不溢出 long。候选生成数包括去重后的物理非法组合，非法组合记录原因但不消耗 Trial；预检查能力非法请求整体拒绝。没有随机种子/隐藏模式轮转。BaselineOnly 只处理基线。
3. 每个候选按 Cells 的请求顺序、Search 阶段格子、RepetitionIndex=0..n-1 观察；最大并发为 min(Budget.MaxConcurrentObservations, Capability.MaxParallelObservations)。端口负责同设备独占租约；声明并行能力不等于可以绕开互锁。乱序回执先有界保留，按 AttemptIndex 归约和分配下一策略轮；native 不可并行端口声明 1。并行策略基于一个完整候选/一轮的结果屏障，不依完成时间选中心。
4. MaxTrials 在写入 Intent 前预留一份额度（失败/取消/未知也占用，不回补），验证尝试同样计入。约束策略给出每次完整设置的最坏能量/温度；能量预算启用却缺 bound/实际usage 时 IO-006/009，不以估计替代事实。累计已用能量+在途预留+下一次最坏能量不得超过 MaxEnergyJ；已返回量超过预留或温度上限立即停止新请求/排空。温度/能量的物理模型和 Owner 由宿主批准，本模块不计算设备模型。限额恰等于最后需要值且没有剩余工作是正常完成；未搜完/未验证完才标 BudgetExhausted。
5. 每次真实观察/评价持久后才汇总，缺项/不可观测分别记录，不填 0；同物理采集 ID 不增加 Repetitions，独立组按 §6.1 核验。搜索全过程不使用 Verification 组数据选候选。
6. 局部细化是确定性工程策略：先基线及先验，完成一轮后按前沿候选 hash ordinal 选所有中心，按轴顺序依次生成索引 -1、+1 的单轴邻居，越界/重复跳过。完成本轮全部候选后才进入下一轮，最多 MaxRefinementRounds（正整数），邻居耗尽或预算停止。不猜半步/连续梯度，不因为“没有改善”证明全局最优；未探测多轴交互明确记未搜索，不禁用安全边界。没有完整有效中心时回退 mixed-radix，切换理由写 StatePayload/检查点，原已观测集合继续去重。
7. CandidateProposalOnly 必须注入同 ProposalRevision 的 ICandidateProposalPort。其输入仅已耐久 SearchVector/证据引用、冻结计划、token和limit；输出完整候选与稳定token，拒绝跨空间/非量化/重复/超limit/异修订。每轮所有结果归约后才能请求下一批；CandidatePayload 与 SearchCheckpointPayload 固化批次顺序/token/计数，不允许端口直接观察或写设备。明确 Exhausted、加载失败、OOD/不确定（端口以 IO-019/DiagnosticId 报告）或无有效候选时排空 Proposal，再确定性回退 mixed-radix，未决 native 时先 ReconcileRequired，不并跑两套策略。Validate 缺端口直接 IO-019。模型训练不在本 DLL 内，模型 hash、特征/数据分组、OOD与不确定性门须在宿主采纳，未采纳时只允许运行默认路线。

### 6.1 观察证据关联与独立验证

以下约束由现有 `IObservationPort`/`IEvaluationAdapter` 及调用方的证据解析完成；Core 不读取产品私有存储，不定义第二套 FrameSet、来源批准或质量指标契约。证据具体 Schema 未采纳时保留该适配切片未就绪，不用引用非空代替有效性验证。

- 固定输入版本：离线端口只消费冻结数据集版本/hash、完整候选设置、目标/方法定义及验证条件清单，不按 latest、时间接近、列表次序或坐标接近配对。缺少历史观察返回 IO-011/IO-010，不补采；历史数据身份不得因当前 OperationId 改变。
- 精确关联：按 Candidate.IdentityHash、ExposureStep.StepId/SequenceIndex 与上游曝光/触发身份解析唯一的实际设置及原帧/ROI/方法证据；校验能力、运行时、设备与机器时基的各自身份。名义观察核对名义设置，扰动观察核对该验证条件冻结的设置，不能一律与名义设置比较。端口生成 ActualSettingsHash 前须验证读回内容；请求值、命令 ACK、最终关灯值和当前会话值均不能替代曝光期间读回。终态已清空的会话字段不能否定有效的原曝光回执；缺失或歧义仍拒绝。
- 验证覆盖：沿用目标×方法×试件×条件矩阵，每个必需名义/扰动条件分别保留原值、单位、有效性与硬约束结果；仅统计去重且有效的物理观察。同一稳定物理帧或采集身份重新封装、换版本、重复评价不能增加独立样本数；不同 FrameId 也不单独证明统计独立。缺一条件或一个条件失败，不能靠平均值、样本数量或清晰度改善掩盖。重复性、均值标准误、置信区间和总计量不确定度保留评价器各自定义，不互相改名或由本模块推造。
- 当前适用性：宿主/端口在取得来源、返回观察、提交候选证据及生成新建议前复验当前来源适用性，hash 只证明内容身份。撤销、版本漂移或租约失效时停止新观察/建议，按 IO-012/IO-011 和原排空路径处理；旧结果仍可历史查询，不据旧回执重新证明当前可采用，不另造 TTL 或批准注册表。
- 快照与资源：入口对可变底层集合做受预算约束的深快照并校验唯一性、顺序；IReadOnlyList 不保证底层不可变。来源载荷、报告借用与条目缓存按显式部署额度及 Budget 在下一分配前计量；失败/取消释放已取得租约，不持有全局单槽锁跨借用期，也不递归获取来源。源项目的固定载荷数值与 canonical 域不迁入。

### 6.2 质量门、向量和 Pareto

每个 Evaluation 必须精确匹配 ObservationId/CellId/EvaluatorRevision，Values 中 ObjectiveId 唯一且属于请求，Unit/MethodRevision 与 MethodObjective 相同；Evaluation.Values必须恰覆盖Cell.ObjectiveIds，Valid值须有非空EvidenceIds；ValueValidity.Valid 要求非 null、有限数，所引用 EvidenceIds 属于该 Accepted 回执，缺失/NaN/±Infinity都拒绝。Complete=true 不是免检标志。Required=true 的目标构成按请求顺序排列的固定向量；Required目标集合必须非空，ObjectiveId全局唯一。Required=false 仅展示，不参与前沿/推荐门且 Lower/Upper 必须 null，避免“可选”绕开质量门。Lower/Upper 非 null 时有限且 Lower<=Upper，闭区间；负值是否合法由方法有效域提供，Core 不猜图像阈值。

候选搜索格全部重复必须完整有效且 HardFailures 为空，每一个值都满足批准上下限。向量为同目标在其声明的所有搜索格/重复的最坏值：Minimize 取 max，Maximize 取 min；不把不同方法、单位或 ROI 直接平均。原值保存在 Evaluation 事件，汇总值保留产生该极值的全部去重EvidenceIds（ordinal排序），Validity=Valid、MethodRevision与原目标一致，Reason=`WorstCaseSearch`；全部有效证据另列ValidEvidenceIds，同样ordinal去重。物理合法、完整但质量不达标的基线可参与改善/诊断，不进入可推荐前沿，不把真实低质量值改为 Missing。

对合格向量按方向转为“越小越好”。A 支配 B 当所有维度 A<=B 且至少一维 A<B；比较有限原始 double，无隐含 epsilon/加权和/单位换算。不完整、不同版本、不同目标维度不比较。相同向量互不支配，保留不同物理设置，以 IdentityHash ordinal 稳定显示；相同设置只一候选。基线朴素增量逐向量比较为 O(N²D) 最坏开销，受摘要与时间预算约束；Optuna 的二维加速只作为以后同输入正确性/性能比较候选，不声称当前最快。没有获批择优规则返回多候选前沿，SelectionPolicyRevision 固定 `strict-pareto-worst-v1`，不自动标唯一最优。

SearchComplete表示所选策略的冻结工作已完成：mixed为全ordinal遍历，local为邻域耗尽/完整轮数结束，proposal为提议阶段已明确结束/失败且已排空并回退mixed完成；达到预算且仍有计划工作则false。局部策略完成不表示全空间搜索，必须在Gaps注明未探测的非邻域范围，IndependentlyVerified只证明已选候选独立验证，不证明全局最优。

验证只执行 VerifyCandidateIds 中在本次合格前沿的候选，每个被选候选对应的必需Verification格/重复（含扰动）分别通过该格ObjectiveIds的同样质量门并满足独立性；验证值不改搜索排序/中心。最终：无合格前沿=NoCandidate；所选策略完整搜索且未请求验证=CandidateFrontier（候选，不是已验证）；预算/故障导致计划未搜索完或验证缺口=NeedsReview（局部策略范围外不算计划缺项，仍披露）；已显式选择的候选全部验证且排空/耐久提交成功=IndependentlyVerified，Candidates 仅含这些已选且已验证候选，完整工程前沿仍在耐久事件；取消=Cancelled。Search/Verification任一回执物理身份/分组冲突时整个受影响候选验证无效；只有部分选择验证成功保留逐候选 bool 与 Gaps，整体 NeedsReview。预算截断即使局部候选验证成功也保守 NeedsReview。如果多个失败原因同时发生，停止优先级为未决设备/native/存储（ReconcileRequired）→已知不可恢复运行错误（Failed）→Cancelled→BudgetExhausted→正常完成，保留各Gaps而StopReason用最高优先级的稳定Code（正常为`Completed`）；运行Completed只表示约定搜索/验证工作停止且资源已归还，预算耗尽可Completed/IO-007，推荐仍NeedsReview。无候选时NoCandidate优先于NeedsReview；取消无故障且已排空时Cancelled，无论有无历史候选。所有验证集、质量门和实际设备适用性值由调用方批准，不用合成例赋客户阈值。

### 6.3 参数建议、受控试采与采用交接（不增加Core API）

本模块的自动化是一次显式请求内的有限“候选→试采→评价→前沿→已选候选验证→停止/归还”编排，不是持续运行的相机自动曝光/光源控制器。曝光、增益、光源Level/Enabled可共同列入请求轴，但单位/量化、Mode/步骤/通道及联合约束仍按§3/6.0；没有阈值反推曝光、PID、自动扩大档位或私有“调亮至合格”分支。基线优先、有限离散枚举为确定性基准，local与Proposal只有显式SearchPolicy/冻结配置才启用；不从失败图像自动切策略或修改质量门。默认预算值不存在，夹具数值不移入部署。

实时Host必须按下表把现有IObservationPort接到设备Owner；本模块只规定所消费的事实及失败顺序，不新增厂商命令、设备状态机或质量写权。设备Owner的具体公开接线和真实物理Profile由该宿主集成任务采纳，不能让Core用猜测的SDK调用补齐。

| 阶段/已有入口 | 必须执行的确定顺序与拒绝条件 |
|---|---|
| Run前接纳 | Host确认工程试采授权、适用设备/样本/方法Profile及独占租约；保存原配置完整设置、配置修订/CAS、Owner/generation和设备安全恢复策略。缺其中实际依赖项零试采。Codec/Validate只证明结构；Host前置不足不以合法Plan替代授权。 |
| 每个ObserveAsync | Core先预留额度并耐久Intent；设备Owner核原请求身份/本generation/授权/互锁及约束，才按完整RequestedSettings执行本次试采。记录原ObservationId、逐步骤实际曝光期间读回、物理采集身份、能量/温度、源hash及独立组，再交Accepted回执；命令ACK或最终恢复值不能代替读回。写入/采集次序和等待条件属于该设备的已采纳Profile，未知动作结果返回Unknown并保持原Owner，不补发新曝光。 |
| 评价与下一候选 | 按已冻结MethodObjective/Profile取得原值/支持，耐久后才更新最坏向量；合法低质量不改Missing。仅完整候选/策略轮屏障结束后发下一批；任何取消、期限/资源不足、源/修订漂移、越能量温度或未知副作用，立即禁止下一Intent并进入原排空路径。单次高分、饱和比例改善或模型Confidence均不提前通过/结束验证。 |
| 正常停止或异常/取消 | 按§6.2停止优先级及§7/16.7～16.8关闭/对账原任务；不同组件各有原Owner与有限观察，任一未知保留，不从另组件成功推导整体释放。停止不继续搜索、不补缺格，不追补失败评价/推荐。 |
| 试采配置恢复 | Core资源归还不等于设备配置恢复。只有设备Owner证明原动作已停/无未决，且同Owner、generation、租约和当前配置CAS仍允许覆盖本次试采写入，才按已保存原设置和设备Profile恢复并真实读回确认。CAS冲突/断连/互锁/未知时不写恢复值、不强制抢租约；Host保留原设置、最后已知试采设置和原因，由原设备Owner对账。恢复错误与业务结果分轴保留，不能改Core旧结果。恢复行为不由本模块finally偷偷执行。 |
| 候选交给程序草稿 | Host消费最终Recommendation及原PlanHash/候选全设置/方法和证据修订/缺口；只有明确用户选择、当前适用性复验和产品原审批流程才进入新草稿。生产参数只由产品程序Owner批准/发布；前沿多候选、NeedsReview、ProtocolFixture及独立验证标签均没有隐含采用权。无获批择优规则保留多候选，UI不选“第一行最佳”。 |

**指标与“置信”**：Core没有Probability/Confidence字段或通用统计置信算法，不能把Coverage、灰度/Sobel分数、前沿位置或独立验证bool转为百分比置信。操作员看到的是逐目标原值/单位、有效性/理由、Requested/Valid/Center支持数、全部计划格/独立样本覆盖、最坏值及验证缺口；这些来自§6.1～6.2/16.6的原证据。若某已批准方法确实要求统计置信下界/重复性/不确定度，则评价器须以独立ObjectiveId、准确MethodRevision/Unit及方法证据输出该量，Core按该方法的Lower/Upper普通目标门消费，不能改成空间Deviation或自行估算。没有方法/独立组/阈值时该Required目标不可观测，不生成伪置信；本模块不承诺未批准的新统计能力。

本节复用§11/16.8的有效向量及原停止反例，不增新数值期望。补充正式断言在现有Core.Tests/Adapters.Tests由原端口fixture执行：停止后Observe次数不增加；异常/预算/Unknown不采用生产设置；配置恢复CAS冲突时设备写次数0；原配置恢复读回失败保留独立Host错误；无统计方法时展示“未评估”，没有Confidence=1或100%；历史查询不触发试采/恢复/程序发布。真实恢复写入/互锁由设备Host的HIL验证，模拟调用计数只证明软件契约。

## 7. 线程、资源、取消与排空

Core 不创建 Dispatcher、SDK句柄、原图或隐藏窗口，不阻塞同步等异步结果；单实例运行 Owner 串行写事件/状态。端口回执深快照后再投影，宿主评价/native线程创建和释放所有图像/tuple租约。Core 只留有界候选摘要与引用；MaxSummaryItems 包括已观测摘要、前沿、暂存回执及建议输入，下一候选所需容量不可预留时停止而非截断前沿。MaxEventQueueItems 为未落盘/待进度队列总额度，满则背压，不能丢事实。事件存储分页，页limit<=MaxSummaryItems；重放逐页累计至同样容量，不把完整历史载入内存。

MaxMemoryBytes/MaxDiskBytes 是运行总额度：Core缓存+端口原图/native临时资源+store本次增量，宿主在 Observe/Evaluate/Append 之前按 Limits 预留并计量，完成后归还；复用缓存仍按本次占用计，不能只数托管GC。Core不替宿主估算原图大小，端口不具备配额/租约能力则实时适配拒绝 IO-006。达到上限停止未开始动作，保留已接纳事实；无空间保存终态则 IO-015/非final，不能删 Unknown/失败证据腾空间。store滚动/compact保留可回放事实及 hash；保留期由宿主，模块不自定清理策略。

无Run/Validate失败/仅历史query时Close/Dispose及Recover尚未读出Plan，一律以构造Options.CleanupObservationLimit作有限观察窗，不能猜Plan预算。有活动/未决计划时单次Close/Dispose等待上限=min(CleanupObservationLimit,本次原Drain的MaxDrainTime剩余窗)；若该窗耗尽，保持未知，不启动第二Drain；没有未决任务且运行已完整归还时不借用过期历史Plan窗，新query收尾只用CleanupObservationLimit；超限返回未决/IO-014，原Task不取消所有权。Recover入口总观察上限先CleanupObservationLimit，读Plan后各stage还受MaxStageTime/MaxDrainTime，不能重置入口总窗。新一次Close/Recover可给新观察窗而不能开启同ID第二原工作。历史query仍QueryDeadline，成功Dispose与发起query在Owner锁内互斥，Dispose先置FinalDisposing禁止新增query；已有query归还后才能成功Disposed。

阶段计时用注入端口外的单调Stopwatch，不靠 UTC 算 deadline。MaxStageTime 覆盖每次端口 await、纯计算批次和持久化等待，MaxWallTime 非 null 覆盖接纳至资源归还，MaxDrainTime 为取消/停止后的独立排空窗；到期只撤销新动作和等待意图，不能宣称 native 结束。等待 task 句柄始终被 Owner 跟踪；排空到期返回未决 ID，保留 ReconcileRequired。不要通过 Task.Run+超时丢弃未完成HALCON/设备任务、Thread.Abort或提前Dispose句柄来“满足”时间门。对账继续使用原ObservationId；Observer/Evaluator/Proposal各自 DrainReceipt均必须OperationId一致、UnresolvedIds为空且Drained && ResourcesReleased，Core才汇总活动资源归还成功；仍未知的物理观察事实必须另留原ObservationId，即使端口Drain成功也不能完成推荐。持久化端口自身不允许遗留未知写事务，CAS/重复读取确定提交事实后再恢复。

取消调用方等待与运行取消分开，见 §4.2；所有用户请求的取消均停止新 Intent，已发请求可返回成功事实但不能复活搜索。关闭页面可以只解除投影，宿主选择继续运行或调用 CloseAsync；若关闭进程，则宿主必须先关闭/对账并保留恢复信息。任何非终态“未归还”都不可包装为 Completed。

### 7.1 调用工厂之前登记原 Task Owner

实例构造先创建内部`OwnedTaskRegistry`，不另造公共Factory DLL。每次Observe/Evaluate/Propose/Append/Commit/Read/Reconcile/Drain及progress通知均遵循以下唯一顺序；“factory”指调用上述端口的委托，不是允许事后追认已经启动的工作：

1. 在Owner锁内检查Closed/停止意图、普通或控制槽、操作/阶段deadline及所需ResourceCharge；原子预留槽、配额和`stageId=OperationId/StageKind/ordinal`条目（查询用`query/monotonicOrdinal`），登记为Starting，然后才能调用factory。无槽/额度就不调用；不在Owner锁内调用外部代码。计数checked，ordinal不复用。
2. 只调用factory一次，返回ValueTask后仅一次`AsTask()`；在同一条目绑定这个原Task和CTS/资源reservation。不可创建另一个Task.Delay/WaitAsync作为“原工作”，不可再次await消费原ValueTask。factory同步抛出/null任务/非法回执按对应失败记录，未产生资源仍须由端口finally归还；factory在返回前已启动native却抛出时，端口自身也须保有同ObservationId原工作，不可丢Owner。端口方法必须迅速返回ValueTask，native长调用须由端口有界专用执行队列承载，不能在factory的同步前半段卡住Owner。
3. 同步完成与异步完成走同一幂等收尾：读取原Task结果/异常，挂到该stageId而非当前“最新运行”；正常/取消/失败先确认原task已结束，并记录真正资源归还事实，再释放仅已归还部分的临时reservations/移出该Task条目。若Observe已返回Unknown但适配器仍持有native任务，Core的Observe Task槽可归还，适配器的独立有界Owner/配额仍保留且必须经Drain/Reconcile证明，不能因返回Unknown就Dispose原图。取消token只记录请求；原Task未完成就不能移除、释放槽/对象或把调用等待完成当native完成。
4. 超时后的仅等待task可结束，但stage超时只转TimedOutOwned、停止新工作并将原ID纳入未决列表，保持Task/CTS/Owner/配额引用。late completion由原条目完成路径处理一次，先归还真实lease/tuple/缓存/线程任务，记录成功/失败诊断，再释放Owner槽；若运行已暂停，只允许对账原意图，不续搜/改终态。资源有多个Owner时只有分配Owner释放，Core仅释放其自己的深快照/借用登记；不能在两个finally重复归还SDK句柄。
5. 对账/Drain使用控制预留槽且串行，不因普通槽满就绕开登记。已有同stageId未完成的Drain/Reconcile/Read不再创建第二task，复用原Task等待；控制槽本身也未完成时返回原未决列表，不能每次Recover追加一个挂起task。已经关闭但未排空的Registry保持可达，宿主必须保留optimizer及原端口服务，直到Close/Recover确认；new optimizer不能接管旧进程仍活跃的task，宿主Owner必须禁止重复租用。重启只能按原持久意图由端口证明物理状态，进程退出不证明设备已停。

Run操作占用实例唯一推进槽，query另由MaxConcurrentQueries和普通task槽限定，Cancel/Close只发停止意图、不重复开启推进任务。QueryDeadline覆盖store读取及所有分页，QueryPageSize限制每页，QueryMaxMemoryBytes限制查询临时载荷；旧计划未读取前也有界，不从未读Plan借未知Budget。query超时返回Unavailable/非final且其store原Task仍登记，槽不释放至late完成；不可无限查询产生挂起task。Recover读Plan后改用该Plan预算，不增加普通Owner容量。Close需要等待包括query/progress在内的原Task全部归还；其等待被取消可返回/抛取消等待，关闭意图不可撤销；没有Run/未调用相应端口时Close不虚构端口Drain请求或默认Budget，只排空实例已登记的query/progress及构造期工作；Dispose进入FinalDisposing后不接纳任何新query/Recover；Close未决允许原Root的Recover，成功Close后不允Recover（先前已冻结），需要历史对账必须在Close未确认状态完成。

GetRecommendationAsync/GetEventsAsync保持查询可用，CancelAsync仅允许本实例当前/保留未决OperationId，历史非活动结果直接返回Drained=true/ResourcesReleased=true；未知ID抛IO-020，跨实例活动运行先由宿主找到原Owner或Recover，不直接操作它的租约。Close成功后禁止Run/Recover/Validate/Preview；GetRecommendation/GetEvents历史查询需另走原Query额度，若查询启动则Dispose前再次排空；Close已确认且尚未Dispose的实例可历史query，幂等Close须等待新query，不返回缓存回执忽略在途任务。GetRecommendation/GetEvents历史查询及幂等Close保留到成功Dispose，成功Dispose后所有入口ObjectDisposedException（再次Dispose无动作）。Close未知时仅允许Close/Recover/GetRecommendation/GetEvents/Cancel，避免关闭后误开始。Dispose未知抛IO-014但不把实例标成功Disposed，宿主捕获后继续保留并对账。

### 7.2 统一资源配额与端口借用

每个Run/Recover在调用端口前建立一个Core拥有的线程安全IResourceQuota；PortContext显式携带OperationId、深冻结Limits与同一Quota，端口不持久化Quota/CLR对象。存储读取使用该Quota；纯历史query使用Options的独立内存配额（不写disk）。TryReserve原子计算已用+全部在途reserved，charge所有字段非负，不溢出、不超Limits则返回非null reservation；超额false/null、无分配。SummaryItems包括深快照条目、去重/前沿/待归约数据；EventItems包括待store/进度条目。Core复制/序列化前预留上界，port分配原图/native缓冲/模型临时资源/store字节前预留其上界；无法估计上界的端口必须拒绝，不能分配后再报告超限。

端口输出DTO为已脱离native的不可变托管快照，无SDK租约；Core在调用factory前预留输出载荷/后续深复制的声明上界，该输出reservation保留至Core消费/归约，端口另为native/临时缓冲预留并在其task结束前归还。输出仍存活时Core输出额度不释放；无需未定义的“通知factory”调用。声明上界从请求完整尺寸/端口冻结Profile提供，超上界DTO拒绝/停止，并保留实际资源诊断；返回ValueTask不授权端口保留被Core误以为已释放的SDK租约。

IResourceReservation.Dispose幂等释放临时memory/summary/event及尚未实际写入的disk预留；CommitDisk(writtenBytes)一次确认0<=writtenBytes<=预留DiskBytes，已写部分转为本次永久disk消耗，Dispose不能把该部分还成可用quota或删除事实文件。借用原图/evaluator必须在各自finally处理；任务未完成则reservation不Dispose。已耐久事实所占disk长期保留，由宿主保留策略管理；Core的ResourcesReleased仅表示本次活动lease/native/task/临时memory归还，不表示耐久文件被删除。资源诊断需记当前/峰值/计量范围，实际allocator峰值另外由Benchmark记录，quota上界不能冒充实测内存。

store.Append/Commit须预留事实和终态写入空间，运行接纳时预先保留最小收尾所需字节（来自实际序列化上界，不造固定常数）。没有收尾空间不接纳副作用；不可牺牲已有Unknown事实换空间。IResourceQuota与Owner管理内部清理，端口仍负责真实设备/native归还；Quota释放本身不是真实归还证明。

## 8. 版本、适配器、兼容与发布

计划快照包含模块契约版本、HALCON 或 AsunImage 适配器版本、相机或光源能力修订、方法或模型或预处理 hash、单位和量化规则。仅同一主版本且字段或枚举兼容可直接读取；未知可选字段由store保留但不进入新身份计算；未知必需字段/枚举/载荷型直接 IO-012，只读导出原件，不能跳过事件或默认成功。主版本或0.x次版本契约不兼容变化必须显式迁移并重新验证。迁移产生新OperationId/PlanHash并引用旧事件，原事实/结果不覆盖；仅改patch且序列化与语义未变时可读原计划，不自动继续设备动作。

适配器分为 IObservationPort（实时或离线）、IEvaluationAdapter（批准的 AsunImage/HALCON 路线）、IResultStore（调用方持久化）、IConstraintPolicy（冻结纯约束）、ICandidateProposalPort（可选建议）。适配器不得把制程名称、页面 ViewModel、私有数据库表或 SDK 类型泄漏到公开契约。

发布物为单个独立 Core DLL（本模块公开契约也在同程序集，暂不另拆无消费者的 Contracts DLL），可选 WPF UI DLL 与 AsunImage评价适配 DLL 单独发布；包括 XML API文档、SemVer版本/契约修订/依赖清单、同版本离线回放样例和迁移说明。Core仅依赖.NET10 BCL；可选UI引用本机DevExpress25.2.3，视觉适配引用现有AsunImage，均不把它们传递给纯Core消费者。回退通过保留上一版本程序集和计划快照，停止新操作后对账、恢复宿主配置，再切回上一版本。禁止以最后一次试验值自动替换生产程序。

## 9. 可选 UI 契约（PageContract IO-WPF-01；0.2.4指导内容已接收，运行资格未关闭）

可选工程 `Asun.Modules.ImagingOptimization.UI.Wpf` 为 .NET10 WPF控件DLL，引用Core及本机DevExpress25.2.3；它不加载视觉/硬件SDK。页面用于视觉工程师规划试验、比较证据与选择候选；查看者只读；宿主明确授权的工程师可以编辑新请求/开始/取消，维护者可以对账。权限来自宿主，Core不代管用户角色。所有动作调用 §4 的无UI入口；生产应用建议经宿主程序草稿审批，此控件没有写参数/放行按钮。

### 9.1 布局、联动与视觉

仅以固定1920×1080物理验证viewport验收，先记录当前DPI和扣除任务栏/窗口边框/标题栏后的实际ClientRect，布局尺寸以DIP且实际可用client为准，不把1920×1080当净内容区、不改显示设置。顶部固定命令带高48DIP，底部状态带32DIP；主区DockLayoutManager/LayoutGroup，左侧参数与预算默认300DIP（可折叠），右侧状态/证据默认340DIP（可折叠），中间占剩余空间，图像/ROI区域获得中区至少一半可用高度；底部候选表与前沿图以标签页共享剩余高度。空间不足先折叠辅助面板、允许参数区独立滚动，关键状态/取消始终可见。白/深主题继承宿主，不自设第二主题系统；统一8DIP间距、正文14DIP、数字等宽、单位紧邻数值，状态同时用文字和图标，不能只靠颜色。

- 参数区：PropertyGridControl.SelectedObject 绑定可编辑的请求草稿，PropertyDefinitions 显式列出曝光、增益、通道Enabled/Level、锁定、搜索策略及预算，ShowSearchBox 只在高级参数打开。编辑时立即执行同Core参数校验并显示Code/Path对应的自然语言；运行期间换成只读快照，修改创建新草稿/OperationId，不能原位改在途计划。高级项折叠、危险限额不可藏在工具提示里。批准能力之外的值不能提交。
- 候选区：GridControl.ItemsSource + TableView，AllowEditing=false、AllowPerPixelScrolling=true；行有Candidate短名、物理设置、质量状态、目标值/单位、缺口、验证状态。列宽先保身份/状态/主要目标，其他列可横滚。列表使用有界页/虚拟化，不能把全部候选或原图塞ObservableCollection。排序只改变显示，不改变Core顺序，SelectedCandidateId/ObservationId/CellId唯一联动；历史打开用GetEventsAsync有界分页构造投影，活跃运行用该UI自己传入的progress，重挂页面先分页后按Sequence去重衔接最新查询，不缺静态事件读取入口，过滤时保留“当前选择被过滤”提示。
- 前沿区：ChartControl/XYDiagram2D/PointSeries2D，用Series.DataSource、ArgumentDataMember、ValueDataMember绑定两目标投影，轴标注目标/单位/方向；更多维用两个选择框切换投影并提示“二维投影，完整前沿见表”，不把二维投影重新算成完整Pareto。点颜色区分候选/已验证/不可比较，点选同步表格；相同坐标保留候选列表供选择，不能遮住等值候选。刷新合并UI投影，不合并事实事件，native/设备状态不作装饰动画。
- 图像区：宿主提供证据预览控件/借用对象，控件只发EvidenceRef选中事件，宿主负责ROI叠加、缩放及关闭租约；不把ImageLibDotNet句柄放ViewModel。显示目标/条件、名义/实际设置差异和来源状态；证据缺失展示“证据不可用。检查来源后重试。”，不生成替代图片。比较采用并列基线/当前候选，同坐标ROI与显示变换，显示增强明确标记且不进入评价。
- 状态区：逐Cell/目标缺口用只读Grid（扁平表，不额外引入未绑定TreeList），运行状态、已用/上限Trials、候选、内存/磁盘、在途与未决数持续可见。未知时红色文字“观察结果未知。停止新试验，先对账。”，显示原ObservationId（高级详情）及唯一安全下一步“对账”；不能显示完成百分比=100%。总空间未知/截断时显示已处理数及未搜索范围，不用估算冒充完成。

### 9.2 命令、关闭与键盘

固定可见命令“校验 / 预览 / 开始 / 取消 / 对账”，导出和恢复默认布局放辅助区域；不因视觉效果把取消/对账藏下拉。命令带采用DevExpress.Xpf.Bars.BarButtonItem，Command/IsEnabled绑定同Core入口前置；BarItem.SuperTip显式设置SuperTip及本地化HeaderItem/Item，两个类型与属性已由本机Core.v25.2 XML确认。开始须Validate成功、Owner允许、非活动/关闭态；取消可重复，按钮点击后显示“正在停止，等待观察结束”；ReconcileRequired 只允查询、导出、对账，不重新开始。导出由宿主保存只读投影及事件来源，不创建模块内第二事实存储。对账调用RecoverAsync，完成后仍提示新试验需新请求。

Tab顺序固定命令→草稿参数→候选表→前沿轴选择→证据→恢复详情；表格方向键选行、Enter打开证据，Esc关闭详情（不绑定设备取消）；开始只由显式按钮/快捷键确认前置，焦点落图像不会触发。AutomationProperties.Name/HelpText/状态文本三语可读，焦点框可见，耗时调用不占Dispatcher。关闭Dock面板的DockItemClosing只解除投影；关闭宿主时由宿主决定继续后台或CloseAsync，正在排空不能把UI消失当资源归还。布局仅从可信宿主配置SaveLayoutToStream/RestoreLayoutFromStream；坏布局恢复默认并保留原用户文件，不覆盖未知配置，固定命令带不随Dock布局隐藏。

### 9.3 可选 UI 公开接入与三语

UI命名空间`Asun.Modules.ImagingOptimization.UI.Wpf`；公开控件`ImagingOptimizationView : UserControl`。本轮以§9.4的明确Binding/RootOwner/lease协议替换未实现草案中可直接改写Optimizer/Presenter的入口，防止绕过Owner；Core API/身份/搜索规则不变。保留两个WPF依赖属性：`CultureInfo Culture`（宿主必须注入、不猜OS语言）、`OptimizationRequest? Draft`（未绑定时可设，绑定后只由本generation编辑事件生成新深冻结草稿，不能改在途Plan）；Optimizer、两个Presenter通过Binding/lease装配，禁止直接setter。

三个普通CLR事件为`EventHandler<EvidenceSelectedEventArgs>? EvidenceSelected`、`EventHandler<DraftChangedEventArgs>? DraftChanged`、`EventHandler<ExportRequestedEventArgs>? ExportRequested`；EventArgs为sealed class:EventArgs，构造及只读属性分别`string EvidenceRef`、`OptimizationRequest Draft`、`string OperationId`，不含native/产品对象。IsActionAllowed只在Binding内注入，参数`Validate/Preview/Start/Cancel/Reconcile/Export`，未知或委托异常=false；排空期间权限撤销不能中止已有清理。事件处理器必须快速入宿主有界队列、不启动未登记设备/异步工作；事件失败记录诊断、不回滚Core事实。

Culture可zh-CN/zh-TW/en-US并扩展，由宿主切换，模块不重复入口；选中ID/数值/运行不变，显示随culture，契约仍invariant。全部用户文字资源化（验证/状态/错误/SuperTip/UIA），异常栈不直显，Code仅诊断详情。Unloaded/重绑的旧query/Dispatcher投影/Presenter归还按§9.4–9.6精确协议，FrameworkElement卸载和取消等待均不当lease归还；不再把未定义的桥长期留给“现场外门”。

| Resource key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| IO.Start | 开始试验 | 開始試驗 | Start trial |
| IO.Cancel | 取消 | 取消 | Cancel |
| IO.Reconcile | 对账 | 核對結果 | Reconcile |
| IO.Frontier | 候选前沿 | 候選前緣 | Candidate frontier |
| IO.NeedsReview | 需要复核 | 需要複核 | Review required |
| IO.Draining | 等待观察结束 | 等待觀察結束 | Waiting for observations to finish |
| IO.Unsearched | 有范围未搜索 | 有範圍未搜尋 | Some ranges were not searched |
| IO.NoCandidate | 无可推荐候选 | 無可推薦候選 | No candidate to recommend |

非明显按钮用DevExpress.Xpf.Core.SuperTip（HeaderItem/Item），说明作用、限制和恢复；例如对账提示“查询原观察结果并归还资源；不会重新曝光。”。通过已核实的BarItem.SuperTip绑定，不猜SuperTipService附加API；具体25.2.3消费编译和交互行为纳入该UI切片验收。1920×1080一次固定视口内验证三语最长文本、键盘、焦点/UIA、切语言选中保留、Dock恢复、滚动/虚拟化、取消始终可见；当前没有真实WPF结果，不能以网页资料或此布局数值当验收通过。

### 9.4 UI Binding / 根 Owner / Presenter 借用公开契约

以下是**UI.Wpf程序集拟实施公开声明**（方法形状表，不是现有程序集）；不放Core/BCL工程，不引用viewport模块私有API。Host窄端口`IImagingPresenterPort`只接受Core给出的证据ref/身份；Host自行桥接已有图像事实/显示控件及其资源Owner，不猜viewport方法。FrameworkElement、Dispatcher、view只出现WPF层。Host根池在构造view/端口和Bind前预留Root，Core自己的Owner/Quota仍照§7，UI根Owner只加上Host可跟踪的WPF调用/借用，不能改变Core事实。

```csharp
public enum ImagingUiTaskKind
{ Bind, Query, Preview, CoreRun, CoreCancel, CoreRecover, Projection,
  PresenterAcquire, PresenterReturn, Unbind, OwnerObserve, RootReturn }
public enum ImagingUiBindingState { Binding, Bound, Unbinding, Retained, Returned }
public enum ImagingPresenterSlot { Baseline, Candidate }
public sealed record ImagingUiLimits(int MaxOwnedTasks, int ControlTaskReserve,
    int MaxPendingProjections, int MaxProjectionRows, int MaxPresenterLeases,
    long MaxProjectionBytes, long MaxPresenterBytes,
    DurationMs BindObservationLimit, DurationMs ActionObservationLimit,
    DurationMs UnbindObservationLimit, InputLimits InputLimits);
public sealed record ImagingUiWork(string WorkId, string BindingId, long Generation,
    ImagingUiTaskKind Kind, long ReservedBytes, int ReservedItems);
public sealed record ImagingUiOwnerSnapshot(string RootId, bool AllTasksEnded,
    bool AllLeasesReturned, IReadOnlyList<string> PendingWorkIds,
    IReadOnlyList<string> PendingLeaseIds, long RetainedBytes, string? DiagnosticId);
public sealed record ImagingUiRetention(string RootId, string BindingId, long Generation,
    bool Accepted, string? DiagnosticId);
public sealed record ImagingUiRootReturn(string RootId, bool Returned, string? DiagnosticId);
public sealed record ImagingUiProjectionResult(string BindingId, long Generation,
    bool Applied, bool Detached, IReadOnlyList<string> DetachedLeaseIds);
public sealed record ImagingUiConsumption(string WorkId, bool Consumed, string? DiagnosticId);
public interface IImagingUiOwnedCall<T>
{
    string WorkId { get; }
    Task<T> OriginalTask { get; }
    void RequestCancellation();
}
public interface IImagingUiRootOwner
{
    string RootId { get; }
    ImagingUiLimits Limits { get; }
    void AttachBinding(string bindingId, long generation, ImagingOptimizationView view,
        IImagingPresenterPort presenters);
    ImagingUiConsumption ConfirmResultConsumed(string workId);
    IImagingUiOwnedCall<T> StartOwned<T>(ImagingUiWork work,
        Func<CancellationToken, ValueTask<T>> factory);
    void StopNewWork(string bindingId, long generation);
    ValueTask<ImagingUiOwnerSnapshot> ObserveAsync(string bindingId, long generation,
        DurationMs observationLimit, CancellationToken waitCancellation);
    ImagingUiRetention RetainAcknowledged(string bindingId, long generation);
    ValueTask<ImagingUiRootReturn> ReturnRootAsync(string bindingId, long generation,
        CancellationToken waitCancellation);
    ValueTask<ImagingUiRootReturn> ObserveRootReturnAsync(string bindingId, long generation,
        DurationMs observationLimit, CancellationToken waitCancellation);
}
public sealed record ImagingPresenterRequest(string AcquisitionId, string BindingId, long Generation,
    ImagingPresenterSlot Slot, string OperationId, string CandidateId,
    string ObservationId, string CellId, string EvidenceRef);
public sealed record ImagingPresenterReturn(string LeaseId, bool Returned,
    long ReleasedBytes, string? DiagnosticId);
public interface IImagingPresenterLease
{
    string LeaseId { get; }
    long ReservedBytes { get; }
    FrameworkElement Presenter { get; }
    ValueTask<ImagingPresenterReturn> ReturnAsync(CancellationToken waitCancellation);
    ValueTask<ImagingPresenterReturn> ObserveReturnAsync(DurationMs observationLimit,
        CancellationToken waitCancellation);
}
public sealed record ImagingPresenterAcquireSnapshot(string AcquisitionId,
    bool Settled, bool ResourcesReleased, IImagingPresenterLease? Lease,
    string? DiagnosticId);
public interface IImagingPresenterPort
{
    ValueTask<IImagingPresenterLease> AcquireAsync(ImagingPresenterRequest request,
        long maxBytes, CancellationToken cancellationToken);
    ValueTask<ImagingPresenterAcquireSnapshot> ReconcileAcquireAsync(
        ImagingPresenterRequest originalRequest, CancellationToken waitCancellation);
}
public sealed record ImagingUiBinding(string BindingId, string OperationId,
    IImagingOptimizer Optimizer, IImagingUiRootOwner RootOwner,
    IImagingPresenterPort Presenters, Func<string, bool> IsActionAllowed,
    CultureInfo Culture, OptimizationRequest? Draft);
public sealed record ImagingUiBindReceipt(string BindingId, long Generation,
    ImagingUiBindingState State, string RootId, string? DiagnosticId);
public sealed record ImagingUiUnbindReceipt(string BindingId, long Generation,
    ImagingUiBindingState State, bool ViewDetached, bool ResourcesReleased,
    ImagingUiOwnerSnapshot Owner, ImagingUiRetention? Retention,
    string? DiagnosticId);
// ImagingOptimizationView公开方法（成员签名表，实施时提供方法体）：
// ImagingUiBindReceipt Bind(ImagingUiBinding binding);
// ValueTask<ImagingUiUnbindReceipt> UnbindAsync(string bindingId, long generation,
//     CancellationToken waitCancellation);
// ValueTask<ImagingUiUnbindReceipt> ObserveUnbindAsync(string bindingId, long generation,
//     CancellationToken waitCancellation);
// ValueTask<ImagingUiBindReceipt> ChangeCultureAsync(CultureInfo culture,
//     CancellationToken waitCancellation);
// ValueTask<ImagingUiConsumption> SelectEvidenceAsync(ImagingPresenterRequest request,
//     CancellationToken waitCancellation);
```

ImagingUiLimits全部显式正值，ControlTaskReserve>=3且<MaxOwnedTasks，MaxPresenterLeases>=2（双图比较）；操作/绑定/卸载观察为正有限ms，可转换TimeSpan且不溢出；MaxOwnedTasks>ControlTaskReserve、输入限额合法，保留三个控制槽至少覆盖Unbind协调、Detach/Return动作和OwnerObserve，任何协调不得持锁等待动作。WorkId规则唯一：`BindingId/generation/Kind/monotonicOrdinal`，控制Unbind=`BindingId/generation/Unbind/0`，单个lease的归还=`BindingId/generation/PresenterReturn/LeaseId`（metadata仍Kind相同）；同lease只一次归还，WorkId冲突不fallback新ID。普通任务与控制任务各自有界；Presenter/Rows/Bytes/Projection队列分别计量，所有分配在factory前预留，单个Work的ReservedBytes/Items非负，WorkId不可复用，BindingId非空且永久不复用。Owner根池不在模块静态变量，Host通过自己的有界池构造`IImagingUiRootOwner`实例，RootId与该Binding唯一对应；AcquisitionId为view在Acquire前生成的`BindingId/generation/acquire/ordinal`，SelectEvidence请求可填此已预留值，若从用户选中内部生成也遵循同规则；每次Acquire/Reconcile以这个原ID和完整request为幂等键，同ID异内容拒绝、不再解析/借图；同一Root不得同时绑定第二view。所有UI DTO输入文本/列表沿Core Options.InputLimits同等级门（ImagingUiLimits.InputLimits显式提供，UI不能从未读Plan猜默认）。与这些接口绑定的CLR型及lease对象不可持久化，只有ID/诊断可记录。

**Bind原子路径**：Host先获得根池槽→构造Root（已强持服务/optimizer与PresenterPort，暂无view）→在目标STA Dispatcher创建view并让Root强持→在同Dispatcher调用一次Bind。Bind是同步纯快速接纳，以BindObservationLimit从入口单调检查输入/Root.AttachBinding快速契约（不合作Host同步阻塞只能由STA Host外截止判失败）；Bind只校验绑定/limits/STA/Dispatcher.CheckAccess/草稿结构，递增view单调generation、调用Root.AttachBinding(bindingId,generation,this,binding.Presenters)原子绑定root/view/服务与文化/权限，再登记订阅；不执行query/acquire/native、不自动Run。构造/Bind失败无任务/lease时Host只归还尚未占用资源的根槽；已有已登记任务/lease则必须同Root清理，不能在catch无条件ReturnRoot。

Bound后所有命令由view在Root.StartOwned之前形成深冻结请求/工作描述；校验/Preview的同步处理仍遵守Core §3.2，UI不得无界Task.Run代跑同步无限策略。SelectEvidenceAsync是给Host/UI命令共同使用的公开联动入口：只接本Binding/generation/OperationId及已耐久事件投影解析到的Candidate/Observation/Cell/Evidence关联，不允许Host凭临近列表索引给别帧；预留Acquire/投影/Return容量后走下述lease协议，完成返回Consumed=true仅表示该选中操作输出已消费，lease仍登记直至Return，超时抛UI-007但原任务保持。第一次Bound查询/页重建用既有Core.GetEventsAsync/GetRecommendationAsync，无新Core API。未获权限、未Bound、所有额度不足先给可恢复错误，不调用factory。`ChangeCultureAsync`是Projection类型原Task（仅改变UI resources），遵循同Owner/generation/deadline，不取消Core运行、无模块语言按钮。

### 9.5 StartOwned / 卸载观察 / 精确归还协议

- `StartOwned`由Host Root实现，返回值为其登记的真实原Task句柄：在根锁内先预留工作槽、内存/项数及条目Starting，再解锁调用factory恰一次、ValueTask.AsTask恰一次并绑定该原Task/CTS；同步成功/失败同一收尾。Returned原Task不得是WaitAsync/Delay包装。slot不足/StopNewWork拒普通任务时返回稳定UI错误`UI-007`（不调用factory），无界factory同步前半段属端口契约失败。WorkKind=`Unbind/OwnerObserve/PresenterReturn/RootReturn/CoreCancel`可用控制预留槽；Projection中Detach调用通过对应generation已Unbinding的WorkId前缀`detach/`明确归控制类（普通渲染Projection仍普通槽），Root只能放行真实清理意图；所有其它kind只用普通槽。同WorkId重复调用只能返回原call，若元数据不一致`UI-018`；不重复factory。
- Root构造起强持服务，AttachBinding成功起强持view/Binding/每个原call/lease及本generation投影DTO。AttachBinding必须是纯快速登记（保存PresenterPort引用但不调用它），只允本Root唯一view/Binding/generation；重复同绑定幂等，异绑定拒绝。`RequestCancellation`只通知原call的CTS，等待token只取消等待；task未结束或lease未知不得释放条目/bytes。普通Call原Task成功后，Root保留结果reservation，view消费/丢弃DTO后显式调用ConfirmResultConsumed(WorkId)，只在原Task已结束且结果DTO已消费/交付时返回Consumed=true、幂等释放结果部分；未归还lease单独保留，不阻止仅DTO的消费确认；未知/未完成false/诊断，不盲释放。Root登记Task槽与结果载荷分开计量，Task终结可释放执行槽但结果/lease载荷仍占额度。对于异常Call（无结果）Root读取异常后自行收尾；对于Acquire返回lease，ConfirmResultConsumed只证明引用已交付，不能释放该lease bytes。late结果不允许交新generation。Owner实现必须读取fault异常一次记诊断，对资源归还未知保持条目。每lease独立计MaxPresenterBytes、MaxPresenterLeases；暂时同时存在旧/新Presenter和Acquire输出时累加，不是覆盖当前槽逃额度。
- `AcquireAsync`调用前view预留输出lease预算/return控制容量，在该view的STA通过StartOwned调用窄端口。Host端口自身迅速返回ValueTask；native图像解析在Host原Owner中有界执行，Presenter在对应Dispatcher创建、每lease只有一个未挂载的FrameworkElement（无Parent、同Dispatcher）；Host有原lease表，lease创建先登记到Root兼容的借用表再返回。Root在Acquire原Task完成路径识别IImagingPresenterLease结果并登记LeaseId/ReservedBytes/分配Owner，即使view已卸载也不能让未读result丢lease；重复LeaseId不同对象/不同bytes为UI-018并保留原两份借用诊断。view读取lease后ConfirmResultConsumed确认交付，再登记Projection挂入ContentControl。Host端口在启动解析/借图之前在自己的有界表登记AcquisitionId、原request与潜在borrow任务，异常后保持原Owner；Acquire原Task结束不证明潜在解析/native结束。Root在AttachBinding存入这个PresenterPort，异常/取消/超时在收尾控制槽用ReconcileAcquireAsync(originalRequest,waitCancellation)读取原事实，只查询/对账、不重新解析/借图。Settled=false或ResourcesReleased=false且Lease=null为未决borrow，Root Snapshot保留AcquisitionId，不把fault-task结束当AllLeasesReturned。返回Lease时先由Root登记，然后正常Detach/Return；Settled=true/Lease=null/ResourcesReleased=true才证明从未借图或已由原分配Owner释放，方可删除pending-acquire。不能返回Lease非null且ResourcesReleased=true混淆尚存借用；同原request对账结果冲突UI-018。每个Reconcile原Task也登记StartOwned控制槽（Kind=OwnerObserve），未完成复用原task，不轮询追加无限等待任务。UI只使用Presenter，不Dispose native/AsunImage；EvidenceRef还须由Host核对候选/观察/条件/ROI事实，不能按列表邻近配对。
- Dispatcher投影只用view.Dispatcher.InvokeAsync(Action)的真实`DispatcherOperation.Task`，factory为`ct => new ValueTask<ImagingUiProjectionResult>(ProjectAsync(...))`，ProjectAsync在该InvokeAsync Action中先查BindingId/generation/Bound，否则不更新，并返回Applied=false的同generation结果；Detach是Unbinding允许的控制Projection，逐lease明确解除后才返回Detached=true/真实DetachedLeaseIds。其Task等待InvokeAsync的原Task并在Root登记，不再Task.Run/Post第二无界队列。Root由StartOwned原ProjectAsync Task及其闭包强持DispatcherOperation至其Task结束，原ProjectAsync在finally也记录该Operation的真实结束，不能以中途Task取消观察假装原Operation已结束。View调用ConfirmResultConsumed后才释放该投影DTO；Root必须强持原DispatcherOperation至其Task结束，Action尽可能短（只赋有界数据/Presenter，不读图、不await）。最多MaxPendingProjections；满则合并尚未发出的同类型最新投影，不能丢Core/store事实。Root.StageCall与Host端口可能各有任务Owner，只释放各自所有权；原DispatcherTask未运行或已开始时取消观察不证明完成。Dispatcher关停/拒绝投影记录`UI-009`，保留旧Root/lease，不能在后台线程Detach FrameworkElement。
- 更换候选/基线Presenter（SelectEvidenceAsync）：先有界取得新lease、再在当前STA挂新Presenter并显式从ContentControl解除旧Presenter；解除动作也由Root登记Projection Task，Root只接收该成功原Task的ImagingUiProjectionResult.DetachedLeaseIds（必须是本binding已登记lease）作为已解除事实，不能由Host直接写一个bool。完成后才以StartOwned(PresenterReturn)调用旧lease.ReturnAsync。ReturnAsync由原Host分配Owner执行真实图像/native/borrow归还并提供LeaseId/Returned/ReleasedBytes；Returned只有已确认释放且ReleasedBytes==lease.ReservedBytes才为true，不能先回true再后台释放。Root在PresenterReturn原Task完成路径核对结果为本lease的ImagingPresenterReturn、LeaseId/bytes与已登记lease一致且有Detach事实，才置AllLeasesReturned/释放lease额度；view调用ConfirmResultConsumed释放回执载荷。每个lease首次ReturnAsync只登记/启动一次真实release工作；原分配Owner在它启动之前强持release原Task/lease并建立可查询账本。ReturnAsync的公开端口call与真实release工作分开，首次端口观察同样不超过该lease绑定的Root.Limits.UnbindObservationLimit；waitCancellation只结束观察、不撤销已登记的一次释放意图：如果call有限结束Returned=false/异常，只说明该次观察未确认；真实release原Task/资源仍由分配Owner跟踪，异常call结束不释放lease额度。未结束的同端口call不重复factory；已结束的false/异常不能被永久缓存成底层终态，后续必须用ObserveReturnAsync查询/有限等待**该LeaseId的原release工作**，不重启release/Dispose、不重借图片。成功Returned=true的receipt永久幂等，重复Return/Observe仅回该真实成功事实。未知Receipt或任何观察超时保留lease/bytes，不能用“等待同一已完成false Task”当恢复。Core的ResourcesReleased不替代这个UI lease确认。
- `UnbindAsync`对显式BindingId/generation执行一次停止意图：保持原generation供对账而把状态改Unbinding（不在卸载时偷加generation使原控制ID失配）；禁止该generation新增普通命令/query/projection/acquire，卸载view可只隐藏但不能删除强引用；同时停投影订阅并RequestCancellation在途UI calls（CoreRun任务的CTS只有宿主明确取消试验时才通知，默认detach不改Core运行）。在原STA启动并登记Detach投影，清空content并等待该原DispatcherTask；所有late Acquire若带lease立即按旧Root安排同样Detach/Return，late query仅丢弃旧投影并归还DTO预算。等待过程以Root.Limits.UnbindObservationLimit单调总窗，waitCancellation只影响本调用观察，不撤销Unbind。Root停止普通工作后控制收尾仍开放，不能先StopNewWork导致自己的Unbind无法登记。
- Unbind资源归还检查覆盖view发出的所有query/preview/CoreRun/Dispatcher/progress/lease以及Host窄端口底层任务。可能CoreRun继续运行：返回Retained而非把工作偷偷移给new view。Unbind在本次总观察窗内等待已登记Acquire/query/Projection收尾，串行登记必要Detach/首次Return；Return端口call有限结束false/fault后，其真实release仍在原Owner中，后续OwnerObserve通过ObserveReturnAsync读当前归还事实，不等待旧false Task变成true；OwnerObserve不得占着最后动作槽等未开始的Return。只有旧generation普通task均结束/DTO和订阅归还、各Presenter已Detach且Return=true，OwnerSnapshot.AllTasksEnded && AllLeasesReturned且未决表为空，Unbind才ResourcesReleased=true/State=Returned（表示view绑定可归还，不代表Root槽已回池）。查询、卸载控制task自身由StartOwned收尾，不把观察task自己算作需要等待的被观察普通task形成自等待：ObserveAsync快照/等待排除当前OwnerObserve/Unbind监视条目，但Root实际回池仍必须等它们也结束。
- 截止/Dispatcher关闭/Return unknown时返回Retained，ViewDetached只能为该generation的全部已挂Presenter在实际STA Detach完成（late未挂lease直接用受控Projection确认未Parent后返回DetachedLeaseIds，不跳过协议），ResourcesReleased=false。必须同步调用Root.RetainAcknowledged得到Accepted=true且RootId/BindingId/generation匹配，Host Root池确认强持旧view/services/tasks/leases；接受失败抛`UI-015`并**仍保持view内部强引用**、禁止重绑，Host必须显式处理，不伪造已移交。`ObserveUnbindAsync`为有限重观察：同一Unbind停止意图/Detach/真实release工作不重启；上次Unbind监视call已返回Retained/异常时，重新生成一个有界OwnerObserve监视call读取**当前**原Owner账本，并对已启动release调用ObserveReturnAsync；对未启动的必要late-lease首次Return仍只一次。每个binding同一时刻最多一个监视call，未结束则复用它；结束后可用递增monitor序号登记下次有限观察，而不是永久回上次Retained快照。达到本次限额返回最新未决快照/RetainAcknowledged；不得无界定时轮询。Host新view必须另预留Root，旧Root已保留会占用池容量；满则拒新绑定。
- `Unloaded`事件仅同步标记停止意图并禁止旧generation普通投影（保留原generation数值供清理对账），不写async void排空。public UnbindAsync只发一次停止意图；Unbind/ObserveUnbind每个有限监视call先按对应确定WorkId登记Root.StartOwned，返回new ValueTask<ImagingUiUnbindReceipt>(call.OriginalTask)，真实release/Detach的原任务另外仍可达，不以监视Task结束替代它们。控制Unbind/0只表示首次停止/观察；再次ObserveUnbind用OwnerObserve/monitorOrdinal，原release WorkId永远不变。view必须在事件返回前向Root以确定`BindingId/generation/Unbind/0` WorkId登记/StartOwned同一Unbind原调用；若已经Unbind则复用，失败记录并RetainAcknowledged，Host使用ObserveUnbindAsync继续。Loaded不自动恢复绑定；同view只有旧Unbind返回ResourcesReleased且原Root已ReturnRoot确认后才可新Bind，view本地保留Returned tombstone以识别旧ID迟到调用。不合作原task超时仅有限观察，不给“已卸载=已释放”回执。
- `ReturnRootAsync`由Host显式调用：其原Task由Root自己先登记RootReturn控制条目再做检查，Host仅有限等待原Task，整次观察<=UnbindObservationLimit且不依Plan；在root锁原子拒绝新普通StartOwned；仍允许已登记资源的必要控制归还及只观察原工作（否则false回执后会死锁）。检查旧generation所有实际原call完成（含Unbind监视task）/lease returned/保留DTO清零/Detach完成/事件解绑，RootReturn及当前执行回池检查的ObserveRootReturn监视call不参与自身释放前置的自等待；其它Unbind/lease观察call必须已结束且DTO消费，不能笼统排除全部OwnerObserve（当前call原Task/错误仍由根Owner记录至返回）。首次RootReturn端口call可有限返回false/异常；这不是原资源归还工作终止。Root关闭意图及原lease/task账本保持，后续ObserveRootReturnAsync仅有限查询/等待原RootId/BindingId/generation账本并重检同一次回池前置，不启动第二Root释放、lease.Return或Dispose。底层迟到成功由原Owner更新账本，后续观察满足前置时根锁中一次CAS完成同一Root的回池并产生true成功墓碑；重复true幂等。Returned=true才从有界池删除Root并解除view/服务强引用；false/异常/超时保留Root并重新确认RetainAcknowledged，不能永久等待已完成false Task。Root释放不Dispose注入Optimizer/端口，Core是否关闭仍由Host独立决定并照Core.Close/Dispose规则；反之Core关闭也不释放UI Root。

**释放观察的收敛规则**：`ObserveReturnAsync`和`ObserveRootReturnAsync`的observationLimit显式正值，且不超过Root.UnbindObservationLimit；waitCancellation仅结束本次查询等待，不通知真实release/native退出或取消它的所有权。每lease/Root最多一个观察call在途（Root.StartOwned的OwnerObserve控制槽，WorkId含原LeaseId/RootId和递增monitorOrdinal）；还在途重复调用回原观察Task，已完成的false/异常下次可查询新账本。观察方法没有“重试释放”副作用，Lease必须已经ReturnRequested/Root必须已有ReturnRequested，否则UI-001且零release调用。false时ReleasedBytes仅是当前已确认量、不会归还总lease额度；true要求完整ReservedBytes、Detach事实、真实原release Task/所有底层资源退出。底层fault若仍无法证明释放，原Owner保留error与未决；随后经该Owner外部对账取得真实释放证据可更新账本，观察才true，不能仅因fault Task结束翻true。

Root保留最初业务/cleanup错误与每次观察诊断；原release Task成功/迟到资源对账完成只追加归还事实，不改历史false receipt或删除异常。Root在PresenterReturn原call=false/fault后，通过已登记的有限ObserveReturn调用读取Host账本当前事实：读到true先按原LeaseId/bytes/Detach核验、更新同一借用表，再释放一次quota；`ConfirmResultConsumed`只释放这次观察DTO，不额外释放lease。RootReturn观察更新的true墓碑不抹去之前cleanup错误，也不重新激活view/Core运行。已成功true的原receipt继续幂等；所有Monitor Task/DTO必须在有限额度内收尾，Root回池前不留非观察类工作。

错误键属于UI.Wpf，不改Core Code：`UI-001`非法binding/STA/父子关系、`UI-007`UI预算/槽/观察截止、`UI-009`Dispatcher/原任务未归还、`UI-015`保留Owner未接收、`UI-018`ID/generation/lease冲突。界面按三语资源显示原因和“等待归还 / 重试对账 / 关闭前保留原会话”等具体动作，不能用“自动修复成功”。不新增单独JSON/报告协议。

### 9.6 两个 STA UI Host 的完整装配卡与验证门

两个Host分别置于页首唯一`Asun.Modules.ImagingOptimization.UI.Wpf.Tests`工程内，目标`net10.0-windows`、`UseWPF=true`、按实际获准任务采用同一个Exe测试宿主，引用UI.Wpf/Core及本机25.2.3；不再创建两个空工程。STA入口各调用`new Application()`并用`Application.Run(Window)`泵Dispatcher，async工作由登记的Root.StartOwned驱动，不在STA上`.Result/.Wait()`阻塞。这里是完整装配/时序卡，拟实施签名来自§9.4；尚未构建/跑真实WPF。

| 装配步骤 | Host A 独立工程台（独立Window） | Host B 产品草稿嵌入（普通宿主Window/ContentControl） |
|---|---|---|
| 根池与配置 | 构造Host本地有界pool，先TryReserveRoot；ImagingUiLimits显式例(12 tasks,3 control,2 pending projections,100 rows,4 leases,2MiB projection,32MiB presenter,1000/2000/2000ms、InputLimits=1024单文本/256列表项/100000输入UTF8bytes)，只有合成UI样例不作默认 | 独立pool/limits同例，禁止借A的Root/view/Services，旧RootRetained占槽，无法预留则不建新view |
| Core构造 | 按§10独立Console request/services/options；先预留Core根Owner，再new optimizer，Validate返回Plan | 按§10 BuildWorker字段映射重新建request/services/options/Core根；不引用产品私表/宿主ViewModel进UI契约 |
| 预览端口 | Host按§9.7实现IImagingPresenterPort/Lease的CPU快照→BitmapSource/Image/只读ROI路线，独立事实表/LeaseId/释放计数；合成样例无native | 本Host独立按§9.7同路线映射已有CPU图像事实/坐标/显示配置，不借A的图像/view/Root。真实来源复制与native归还仍由原来源Owner确认；fixture只证明软件协议，不造viewport方法 |
| UI绑定 | 在同STA新建view并Root强持；ImagingUiBinding含BindingId=`ui-a-1`、OperationId=request.OperationId、optimizer/root/port、明确role权限、zh-CN及Draft；调用Bind一次得到generation=1（该view首次） | 在本Host STA创建独立view、Root强持，BindingId=`ui-b-1`，装入宿主ContentControl后Bind；root.Draft/权限从自身映射，role只读时Start禁止 |
| 任务/图像联动 | root.StartOwned(Query)→Core.GetEvents/GetRecommendation；user选中→PresenterAcquire→登记Lease→Projection挂载；Run进度仅同步入UI有界待发投影 | 同一API流程；历史分页不靠实时订阅填缺，同ID去重；Baseline/Candidate同时显示时分别两lease，不能共享同FrameworkElement Parent |
| 三语/权限 | ChangeCultureAsync从zh-CN→zh-TW→en-US的原Projection任务被同Root记录，输入/选择保持；撤权限不停止安全Return | Host语言入口调用同方法，不加模块语言切换；自然英文长文本/中文/繁体不截关键取消/对账 |
| 卸载/重绑 | Host关闭Window之前显式Unbind；Unloaded复用原意图；停止Core或让Core继续由Host明确决定，UI lease归还与Core状态两个轴 | ContentControl切页先对旧Binding/generation Unbind；oldCoreRun继续时旧RootRetained，另new view需新Root，禁止原view立即覆盖旧绑定 |
| 迟到/停机 | 原Acquire gate晚返回lease，old generation不投新页，Root登记Detach/Return；Dispatcher shutdown前必须确认ViewDetached，无法确认则Retained/设备Owner保留 | lease.Return gate未结束、query晚完成、旧Dispatcher队列晚执行均只旧Root；宿主Root保留接收成功后才可移开UI引用，不把新view释放旧native |
| 最后收尾 | 有限ObserveUnbind→ResourcesReleased且未决空；等本次Unbind监视Task完成→Root.ReturnRootAsync；若false/异常，同Root.ObserveRootReturnAsync有限查询至真实true；按Core.Close/Dispose独立确认→归还Core根；最后Application.Shutdown | 同顺序；ReturnRoot失败保留，不吞业务/卸载异常；关闭宿主不删除用户Dock布局/配置/证据 |

Host的`IImagingUiRootOwner`实现是WPF测试私有Owner夹具：字典WorkId→原Task/CTS/reservation，最多limits.MaxOwnedTasks；分普通/控制槽，BindingId/root/generation映射唯一；Snapshot来自这个真实表及lease表，不能用延迟到期生成成功。ReturnRoot删除动作只在全部前置真实完成，RetainAcknowledged须由仍活着的pool登记强引用并返回Accepted；不是向已关闭窗口投递日志代替接收。STA Presenter fixture `AcquireAsync`同步登记AcquisitionId/lease后返回，`ReconcileAcquireAsync`只从同ID不可变表返回Settled/Lease/真实借用状态，门控用已登记TCS原Task；`ReturnAsync`同lease只一真实release原Task；Return观察可先false/异常，ObserveReturn仅查询原gate/账本，gate释放且原工作退出后才Returned=true/释放计数+1；首次true前重复Return不再释放，已结束false/fault须用ObserveReturn读新事实；账本确认为true后重复Return/Observe均回同一成功receipt、释放计数仍1，同ID异内容才冲突测试。DispatcherTask来自真实InvokeAsync，测试可以门控普通Projection造成迟到，但不能模拟成截图成功。

**有限验证计划**：两个STA Host各单case外层30s、所有WPF软件suite120s；Root action/bind/unbind仍各自上述有限窗，外层沿§10.4 Process进程树runner，只杀无设备UI fixture且判失败，不用进程退出当native归还。固定1920×1080同一个验证viewport（扣任务栏/边框/标题/状态），沿§9.1不改显示设置、不跑其它分辨率。门包含：正常双图/候选/前沿选择与三语/Tab/UIA；未授权Start零CoreRun；卸载时待query+Dispatcher+Acquire；late lease跨generation；Acquire同步throw已启动borrow但未返回lease（同原AcquisitionId对账）；Return未知/同步throw；Dispatcher关闭拒绝Detach；retain拒收/池满；CoreRun继续且UIRootRetained；Return观察已完成false/异常后底层late退出，ObserveReturn再读true；RootReturn已完成false/异常后ObserveRootReturn收敛；重复Unbind/ReturnRoot；先Core.Close成功仍UI lease未归还、反向UIRoot返回但CoreRun未完。断言Owner条目/bytes/lease归还计数、每factory一次、旧Action不变新页、Unbind两轴不混、后续Return只能原Owner，未知无ResourcesReleased/RootReturned。

**恢复终止专项断言**：分别门控首次Return端口call为已完成false和fault，真实release保持未结束；消费该观察DTO后lease/bytes仍保留。以原LeaseId再次有限ObserveReturn，门控放行真实release后必须读到true，释放启动计数=1、lease额度归还计数=1，重复true不再减额度，旧false receipt不被改写，最初业务/cleanup错误仍可诊断。分别使首次RootReturn已完成false/fault；同RootId观察在原任务/lease/DTO/订阅清零后true，回池CAS计数=1。对尚未ReturnRequested的观察断言UI-001且释放计数=0；取消观察仅结束该次等待，原release继续受原Owner跟踪。各轮观察结束后消费DTO并退出控制槽；仍未确认时有限返回Retained，不无限等待/轮询，也不调用第二次release/Dispose。

主控已完整回读0.2.4 §9.4–9.6并接收U1指导内容：公开Root/OwnedCall/Binding、Presenter acquire对账/Detach/Return、有限观察与原释放工作区分、已完成false/fault后的ObserveReturn/ObserveRootReturn迟到收敛、预算/业务与清理错误双轴、两个STA Host及验证门均已闭合，本次无新增内部设计欠账。U1仍PreparationIncomplete/NotReady，不提升ModuleCoreImplementationReady；后续门是实际UI实现/25.2.3消费编译、真实WPF/Dispatcher/1920×1080/三语/UIA/性能、具体Host图像/native资源桥实现验证和产品接入资格，均未关闭。真实设备/样本/HIL属于各适配门，不阻断上述STA软件契约实现；保持已有HALCON §16不改。此前待接收文字是各历史修订当时的状态，当前结论以页首、本段及准入表为准。

### 9.7 现有Presenter端口的CPU快照装配、坐标与交互

本轮明确两个STA Host的参考实现均为**已取得CPU快照→WPF BitmapSource/Image + Canvas只读ROI**，仍实现§9.4原`IImagingPresenterPort/IImagingPresenterLease`，不增公开接口、不引入新的图像/ROI算法。UI.Wpf仍只引用Core/WPF/DevExpress；桥由Host实现，来源类型/存储适配只在Host。实际已有native预览Host可实现相同端口，但必须满足同一Acquire/对账/Return条件，不能用不透明native未归还来伪造本CPU路线的Returned。当前没有直接消费viewport的Control/Session/Presentation/Lifetime：viewport WPF Assembly v0.2的§10.6～10.9及其源/选择/Clear增量不适用，不造临时viewport调用或增加依赖。这里的“验证viewport”仅指1920×1080屏幕验证区。

Host在绑定前预留受额度约束的预览事实表容器；表不是产品数据库，也不进入公共模块。离线已有记录可在Bind前冻结条目，实时新观察须原回执耐久后才追加不可变条目；同完整键同内容幂等、异内容UI-018，不改旧条目。逻辑键为`OperationId/CandidateId/ObservationId/CellId/EvidenceRef`完整字段及原SourceRevision/DisplayRevision，不能仅用短显示名或EvidenceRef列表次序查询。表值必须包含：原FrameEvidence/SourceRef/hash、SourceRevision/CoordinateRevision、原宽高正int、选定PlaneId/原像素类型、行优先有限原Samples与等长ValidMask、各ROI的RegionKey及半开整数(row0,col0,row1,col1)、显示窗WindowMin/WindowMax及DisplayRevision、来源适用状态。字段类型沿原证据/quality Descriptor；CPU Samples是冻结double数组，只有源声明的UInt8/UInt16整数范围或Float32可表示的有限值，不接另一自动归一化数组。显示窗两个double有限且WindowMax>WindowMin、差值有限，无隐含默认/物理饱和推断。没有CPU快照时Host先由已批准来源Owner取得并确认复制/原lease状态再登记，不能在Image控件里偷调用AsunImage、latest文件或相机；复制未决仍归来源Owner的原Task/lease表，Acquire对账覆盖它。事实表本身的保留上限/来源lease及历史保留归Host额度，不因UI取得副本取消来源所有权。首次Acquire的快速接纳在Host锁中把当前明确选定的DisplayRevision及完整条目绑定到AcquisitionId；之后重复Acquire/对账只读该原绑定，不读新的显示配置。更新显示窗先生成不可变DisplayRevision，再通过同view.SelectEvidenceAsync对原证据发一个新AcquisitionId，按原lease替换协议采用新显示；不覆盖旧lease引用的条目，不新增Core/设备操作。

| 顺序 | 原端口内的确定处理与输出 |
|---|---|
| 1 查键/预留 | 按原AcquisitionId先登记request/Starting，核本Binding/generation、证据链及源/坐标/显示修订。缺表项/漂移/权限撤销拒绝，不返回空成功或替代图。核checked(Width×Height)、Samples/Mask长度、ROI全在原图内及maxBytes；预留原值深快照、4×像素BGRA缓冲、BitmapSource像素存储、ROI/控件/任务开销同时存活的保守上界。对象开销由发布构建的测量Profile给定，不能仅数最后4×像素。额度不足在复制/控件创建前UI-007。 |
| 2 生成显示副本 | 在Host已登记的有界CPU工作队列逐行转换，不阻塞STA，按ActionObservationLimit和固定有界批次检查停止/期限；valid像素灰度g=round-to-even(255×clamp((x−WindowMin)/(WindowMax−WindowMin),0,1))，三色通道均g且alpha=255；无效mask像素BGRA全0，Image下方棋盘背景标示无效区。只对显示缓冲做窗映射，原值/mask不变，不从本图自动统计选窗，不拿显示灰度算质量。标记“显示映射”；多通道仅显示事实中明确PlaneId，不自动RGB混灰。 |
| 3 创建Presenter | BGRA行跨度checked(4×Width)，调用.NET10 `BitmapSource.Create(width,height,96d,96d,PixelFormats.Bgra32,null,byteArray,stride)`的Array重载，不使用IntPtr零拷贝；核CanFreeze后Freeze。BitmapSource与其原CPU准备Task由该AcquisitionId强持。随后在目标Dispatcher的原InvokeAsync创建未挂载Grid，内含Image、同坐标Canvas和身份/来源标题，登记lease/ReservedBytes才返回；只有该原Task和DispatcherTask真实结束才Settled。失败后若已有lease仍按原ID对账交回，不能在Acquire fault中丢图。96是显示DPI参数，非用户显示设置/图像物理尺度。 |
| 4 坐标与选择 | 图像坐标按像素边界：x=column、y=row，像素中心(col+.5,row+.5)；矩形ROI左上(col0,row0)、宽col1−col0、高row1−row0。Image原Width/Height及Canvas相同，位于ClipToBounds容器；对整个图像+ROI Grid使用同一MatrixTransform，不能给两者分别Stretch。默认适应倍率s=min(clientWidth/Width,clientHeight/Height)，居中平移；client非正只等待布局，不除0。滚轮以指针反算的原图点为锚，每格倍率×1.2，上下界sFit/16～sFit×64（显示交互范围，非设备参数）；中键拖移，平移限制为至少有图像与可用区相交。初次/新源/用户“适应窗口”重置适应矩阵；同源刷新/切语言保留。1:1为1源像素=1DIP，文案为“1像素/DIP”，不假称物理屏幕像素。 |
| 5 双图与只读ROI | baseline/candidate各自独立Presenter/lease，同坐标修订且尺寸相同时可同步同一源坐标中心和倍率；任一不一致则独立适应并显示“坐标不同，分别查看”，不伪配准。ROI只读，点击已有RegionKey只展开其目标/支持证据，不能修改质量ROI；前沿点/表行按CandidateId选择，再精确Observation/Cell/Evidence键取图，不把图像点击当试采或择优。拖动/缩放/显示窗变化不发Core Run/Observe/Evaluate，显示窗改变只新DisplayRevision/新显示lease，原方法/质量值保持。 |
| 6 解除与归还 | 按§9.5先在原STA解除ContentControl/ROI事件/图像引用，记录真实DetachedLeaseIds；Return原工作等待CPU/Dispatcher任务退出、清Image.Source/Canvas引用及本方原值/显示缓存后才证明本方ReservedBytes全归还。冻结BitmapSource是托管对象，不以GC.Collect/终结器或Dispose虚构native退出；本方强引用/登记已清及无原任务才为CPU lease释放。未归还来源native仍在原来源Owner，Acquire/Return账本须保留相关未决项。原Return观察false/fault用同lease ObserveReturn有限重读，已有Root/Close协议不重定义。 |

CPU路线的ReleasedBytes只表示本lease已归还的活动借用/本方登记预算，不是进程RSS或WPF渲染引擎缓存已归零。WPF内部合成/图像缓存的实际内存计入§12整进程峰值/长稳验证，不把弱引用或一次GC当物理释放证据；显式来源native未确认时不能借此定义释放原来源lease。当前无自建GPU/native显示句柄，采用这类Host时必须由其原分配Owner给出真实归还证明。

Host A/B的软件夹具分别建立自己的完整键/像素/mask/ROI/显示窗表。可用§16.8已有4×1像素/显示窗[0,255]及group mask作为明确ProtocolFixture预览输入；若Core采用§10的合成评价，则标题必须保留“协议夹具”，这些显示像素不宣称生成了§11的合成评分。真实RecordedInput表直接使用该记录的Samples/ValidMask/Descriptor及FrameEvidence，group必须明确RoleKey/StepIndex选择，缺角色不借别步骤。Host自己的表解析器逐字段映射，UI不引用Adapters.Tests私类、AsunImage内部或产品表。

测试仍在同一UI.Wpf.Tests：原完整键错配/坐标漂移零成功Acquire；mask空不生成假质量；同修订ROI在缩放/平移后边界对齐，异修订禁止联动；显示窗变化不改原Samples/hash/Evaluation、无Observe；三语/1像素DIP/适应/滚轮/中键/Tab可执行。逐个门控CPU准备、Dispatcher创建、Detach及late Return，对账只能原AcquisitionId/LeaseId，两个同图槽不得共享FrameworkElement Parent。性能另记录CPU快照读取→显示转换→Dispatcher创建/实际挂载、两图/全部ROI峰值与取消到真实归还；大图/边界孔洞/满额度/慢来源/关停下沿§12同统计和Profile，不以小夹具、截图或挂载Task证明native/HIL/真实画面性能。

实施后唯一UI测试命令为`dotnet build tests/Modules/imaging-optimization/Asun.Modules.ImagingOptimization.UI.Wpf.Tests/Asun.Modules.ImagingOptimization.UI.Wpf.Tests.csproj -c Release`，随后`dotnet run --project tests/Modules/imaging-optimization/Asun.Modules.ImagingOptimization.UI.Wpf.Tests/Asun.Modules.ImagingOptimization.UI.Wpf.Tests.csproj -c Release --no-build -- --host ui-a --suite binding,presentation,recovery,localization --deadline-ms 110000`；B独立子进程仅将selector改`ui-b`，每Host执行本表完整断言，不借A对象。内部suite110s/单case25s，外层沿§10.4有限runner套build120s/suite120s/case30s；未知selector/失败/未完成/必需跳过非0，WPF窗口实际验证仍只固定1920×1080视口。本轮未创建或执行该工程。

### 9.8 三语资源、状态与错误恢复的闭合表

以下补足§9.3资源入口；`IO.State.<枚举名>`、`IO.Validity.<枚举名>`由明确表映射，`IO.Error.<Code>`为本表对应类别文案的别名，未知码统一IO.Error.Unknown并保原Code到诊断详情，不直显异常Message。其它参数/列标题按下表资源化；动态对象身份/RegionKey/MethodId/单位来自事实，数值按Culture格式显示、canonical仍invariant。Count/上限/单位用独立绑定字段，不能拼句式形成不可本地化文案。PropertyGrid的每个PropertyDefinition分别绑定标题/说明/可编辑前置；复合列表标签使用StepId/ChannelId，不翻译或改变其身份。

| Resource key / 用途 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| IO.Title | 成像参数试验 | 成像參數試驗 | Imaging parameter trials |
| IO.Validate / IO.Preview | 校验 / 预览 | 驗證 / 預覽 | Validate / Preview |
| IO.Export / IO.ResetLayout | 导出证据 / 恢复布局 | 匯出證據 / 還原版面 | Export evidence / Reset layout |
| IO.Parameters / IO.Budget | 参数 / 预算 | 參數 / 預算 | Parameters / Budget |
| IO.Exposure / IO.Gain | 曝光 / 增益 | 曝光 / 增益 | Exposure / Gain |
| IO.LightEnabled / IO.LightLevel | 光源启用 / 光源档位 | 光源啟用 / 光源檔位 | Light enabled / Light level |
| IO.Locked / IO.Strategy | 锁定 / 搜索策略 | 鎖定 / 搜尋策略 | Locked / Search strategy |
| IO.Prior / IO.RefinementRounds | 先验候选 / 细化轮数 | 先驗候選 / 細化輪數 | Prior candidates / Refinement rounds |
| IO.Trials / IO.Candidates | 观察次数 / 候选数 | 觀察次數 / 候選數 | Observation attempts / Candidates |
| IO.StageTime / IO.WallTime / IO.DrainTime | 阶段时限 / 总时限 / 排空时限 | 階段時限 / 總時限 / 排空時限 | Stage limit / Total time limit / Drain limit |
| IO.Energy / IO.Temperature / IO.Concurrent | 能量上限 / 温度上限 / 并发数 | 能量上限 / 溫度上限 / 並行數 | Energy limit / Temperature limit / Concurrency |
| IO.Memory / IO.Disk / IO.Summaries / IO.Events | 内存 / 磁盘 / 摘要数 / 事件数 | 記憶體 / 磁碟 / 摘要數 / 事件數 | Memory / Disk / Summaries / Events |
| IO.Identity / IO.Settings / IO.ActualSettings | 身份 / 请求设置 / 实际设置 | 身分 / 請求設定 / 實際設定 | Identity / Requested settings / Actual settings |
| IO.Step / IO.Channel / IO.Region / IO.Role | 步骤 / 通道 / 区域 / 图像角色 | 步驟 / 通道 / 區域 / 影像角色 | Step / Channel / Region / Image role |
| IO.Unit.NativeCode / IO.Unit.RelativePercent | 设备码 / 相对百分比 | 設備碼 / 相對百分比 | Device code / Relative percent |
| IO.Objective / IO.Value / IO.Unit / IO.Validity | 目标 / 原值 / 单位 / 有效性 | 目標 / 原值 / 單位 / 有效性 | Objective / Raw value / Unit / Validity |
| IO.Gap / IO.Verification / IO.Source | 缺口 / 验证 / 来源 | 缺項 / 驗證 / 來源 | Gap / Verification / Source |
| IO.Required / IO.Optional / IO.Lower / IO.Upper | 必需 / 仅展示 / 下限 / 上限 | 必要 / 僅顯示 / 下限 / 上限 | Required / Display only / Lower bound / Upper bound |
| IO.RequestedPixels / IO.ValidPixels / IO.CenterPixels | 请求像素 / 有效像素 / 完整中心 | 請求像素 / 有效像素 / 完整中心 | Requested pixels / Valid pixels / Complete centers |
| IO.Pending / IO.Unresolved / IO.Baseline / IO.Selected | 在途 / 未决 / 基线 / 当前候选 | 執行中 / 未決 / 基準 / 目前候選 | In progress / Unresolved / Baseline / Selected candidate |
| IO.Recorded / IO.NotEvaluated | 历史记录 / 未评估 | 歷史記錄 / 未評估 | Recorded input / Not evaluated |
| IO.Fit / IO.OnePixel / IO.WindowMin / IO.WindowMax | 适应窗口 / 1像素/DIP / 显示下限 / 显示上限 | 符合視窗 / 1像素/DIP / 顯示下限 / 顯示上限 | Fit to window / 1 pixel per DIP / Display minimum / Display maximum |
| IO.DisplayMapped / IO.CoordinatesDiffer | 显示映射 / 坐标不同，分别查看 | 顯示映射 / 座標不同，分別檢視 | Display mapping / Different coordinates; view separately |
| IO.Projection2D / IO.FilteredSelection | 二维投影，完整前沿见表 / 当前选择被过滤 | 二維投影，完整前緣請見表 / 目前選取項目已被篩選 | 2D projection; see the table for the full frontier / Current selection is filtered |
| IO.EvidenceUnavailable | 证据不可用。检查来源后重试。 | 證據無法使用。檢查來源後重試。 | Evidence unavailable. Check the source and retry. |
| IO.UnknownObservation | 观察结果未知。停止新试验，先对账。 | 觀察結果未知。停止新試驗，先核對結果。 | Observation result unknown. Stop new trials and reconcile. |
| IO.Stopping / IO.WaitReturn | 正在停止，等待观察结束 / 等待资源归还 | 正在停止，等待觀察結束 / 等待資源歸還 | Stopping; waiting for observations / Waiting for resources to return |
| IO.NewTrialRequired / IO.ReadOnly | 新试验需要新请求 / 当前仅可查看 | 新試驗需要新請求 / 目前僅可檢視 | A new trial needs a new request / Read-only access |
| IO.Tip.Start | 按冻结计划试采；不会改生产参数。 | 依凍結計畫試拍；不會更改生產參數。 | Capture trials from the frozen plan; production settings stay unchanged. |
| IO.Tip.Cancel | 停止新观察；已发出的观察须等待结束。 | 停止新觀察；已送出的觀察須等待結束。 | Stop new observations; wait for those already started. |
| IO.Tip.Reconcile | 查询原观察结果并归还资源；不会重新曝光。 | 查詢原觀察結果並歸還資源；不會重新曝光。 | Query original observations and return resources; no new exposure. |

一行多key表示各key一一对应独立短资源，不把斜线写成控件内容。各budget名称准确对应§3字段；未启用可选限额显示IO.NotApplicable（不适用 / 不適用 / Not applicable），不显示无限或0。Role授权拒绝统一IO.ReadOnly，清理仍可执行。每个控件AutomationProperties.Name采用其标题资源，HelpText复用下面命令/错误的限制与恢复；BarItem.SuperTip的HeaderItem用命令资源、Item用对应说明。Validate/Preview说明复用“仅检查计划，不曝光。”（僅檢查計畫，不曝光。/ Check the plan only; no exposure.）；Export说明“导出只读证据，不发布参数。”（匯出唯讀證據，不發布參數。/ Export read-only evidence; no settings are published.）；适应/1像素DIP说明分别复用其显示动作及“仅影响显示。”（僅影響顯示。/ Display only.），这些句子分别使用IO.Tip.Validate/Export/Display资源，不在代码写literal。

| 映射资源 / 原枚举或Code | zh-CN | zh-TW | en-US |
|---|---|---|---|
| IO.State.Created / Validating / Ready | 已创建 / 正在校验 / 可开始 | 已建立 / 正在驗證 / 可開始 | Created / Validating / Ready |
| IO.State.Observing / Evaluating / Frontier / Verifying | 正在观察 / 正在评价 / 候选前沿 / 正在验证 | 正在觀察 / 正在評估 / 候選前緣 / 正在驗證 | Observing / Evaluating / Candidate frontier / Verifying |
| IO.State.Cancelling / Draining / Drained | 正在取消 / 等待观察结束 / 已排空 | 正在取消 / 等待觀察結束 / 已完成排空 | Cancelling / Waiting for observations to finish / Drained |
| IO.State.ResourcesReleased / Completed / Cancelled | 活动资源已归还 / 试验已结束 / 已取消 | 活動資源已歸還 / 試驗已結束 / 已取消 | Active resources returned / Trial ended / Cancelled |
| IO.State.Failed / ReconcileRequired | 试验失败 / 需要对账 | 試驗失敗 / 需要核對結果 | Trial failed / Reconciliation required |
| IO.Recommendation.CandidateFrontier / IndependentlyVerified | 工程候选 / 已完成计划独立验证 | 工程候選 / 已完成計畫獨立驗證 | Engineering candidates / Planned independent verification complete |
| IO.Recommendation.NoCandidate / NeedsReview / Cancelled | 无可推荐候选 / 需要复核 / 已取消 | 無可推薦候選 / 需要複核 / 已取消 | No candidate to recommend / Review required / Cancelled |
| IO.Validity.Valid / Missing / NotObservable / OutOfDomain / Invalid | 有效 / 缺失 / 不可观测 / 超出方法范围 / 无效 | 有效 / 缺少 / 無法觀察 / 超出方法範圍 / 無效 | Valid / Missing / Not observable / Outside method domain / Invalid |
| IO.Error.Input；IO-001/IO-002/IO-003/IO-019、UI-001 | 参数无效。按标记修改后重新校验。 | 參數無效。依標記修改後重新驗證。 | Invalid parameters. Fix the marked fields and validate again. |
| IO.Error.Capability；IO-004/IO-006 | 能力或约束不满足。检查设备配置。 | 能力或限制不符。檢查設備設定。 | Capability or constraints not met. Check device configuration. |
| IO.Error.Evidence；IO-005/IO-008/IO-010/IO-011/IO-018、UI-018 | 证据不完整或冲突。检查来源及方法。 | 證據不完整或衝突。檢查來源與方法。 | Evidence incomplete or conflicting. Check the source and method. |
| IO.Error.Unknown；IO-009/IO-014、UI-009 | 结果或归还未确认。保留原会话并对账。 | 結果或歸還尚未確認。保留原工作階段並核對結果。 | Result or return unconfirmed. Keep the original session and reconcile. |
| IO.Error.Budget；IO-007、UI-007 | 预算或时限不足。检查缺口，另建试验。 | 預算或時限不足。檢查缺項，另建試驗。 | Budget or time limit reached. Check the gaps and create a new trial. |
| IO.Error.Version；IO-012 | 来源或版本已变化。停止试验，检查修订。 | 來源或版本已變更。停止試驗，檢查修訂。 | Source or version changed. Stop the trial and check revisions. |
| IO.Error.Cancelled；IO-013 | 已请求取消。等待观察结束。 | 已請求取消。等待觀察結束。 | Cancellation requested. Wait for observations to finish. |
| IO.Error.Store；IO-015 | 结果未保存。停止试验，检查存储并对账。 | 結果尚未儲存。停止試驗，檢查儲存並核對結果。 | Result not saved. Stop the trial, check storage and reconcile. |
| IO.Error.Active；IO-016 | 原试验仍在处理。查看原会话。 | 原試驗仍在處理。檢視原工作階段。 | The original trial is still active. View its session. |
| IO.Error.Interrupted；IO-017 | 试验已中断。对账后另建请求。 | 試驗已中斷。核對結果後另建請求。 | Trial interrupted. Reconcile before creating a new request. |
| IO.Error.NotFound；IO-020 | 未找到试验。检查试验身份。 | 找不到試驗。檢查試驗身分。 | Trial not found. Check the trial identity. |
| IO.Error.Retention；UI-015 | 资源仍被占用。保留原窗口并检查宿主。 | 資源仍被占用。保留原視窗並檢查宿主。 | Resources remain in use. Keep the original window and check the host. |

本表不为后端开放自由用户文字：原ReasonCode/DiagnosticId保留到详情，主显示映射上述确定类别；本模块不调用未声明的上游资源API，质量原因在主区使用对应Validity和IO.Error.Evidence，raw token只留详情。BindingState的Binding/Bound/Unbinding/Retained/Returned分别复用“正在绑定 / 已绑定 / 正在解除绑定 / 仍保留资源 / 已归还”（正在繫結 / 已繫結 / 正在解除繫結 / 仍保留資源 / 已歸還；Binding / Bound / Unbinding / Resources retained / Returned），按IO.Binding.<name>独立资源存储；LookupState复用Found（已找到 / 已找到 / Found）、NotFound和Unavailable（不可用 / 無法使用 / Unavailable）三key。SearchPolicy按声明顺序四key对应“仅基线 / 有限枚举 / 局部细化 / 候选建议”（僅基準 / 有限列舉 / 局部細化 / 候選建議；Baseline only / Finite enumeration / Local refinement / Candidate proposals）。所有enum资源由显式switch/表映射，不用ToString直显；从请求读取的单位/标识不构成用户文案。动态缺口按事件Code、CellId/ObjectiveId及原因类别显示，原自由诊断仅留开发详情；没有新增无消费者的资源文件或过程清单。

## 10. 无 UI 最小 Host、唯一执行约定与可复现测试夹具

### 10.1 唯一工程、目标框架和运行命令

Core 与唯一测试工程的工程落点见页首。最小可执行 Host 不新增产品工程：它是唯一测试工程内的 `ImagingOptimizationHostFixture`（Console 入口方法 `RunConsoleCaseAsync`）和 `ImagingOptimizationWorkerFixture`（入口方法 `RunWorkerCaseAsync`）；二者为两个独立字段映射的 fixture，不能共享静态 Services、请求、Owner、store 或游标。实现获准后，唯一工程使用 `net10.0`、`<OutputType>Exe</OutputType>` 的 Core.Tests 可执行测试宿主配置，引用 Core 与 .NET 10 BCL；不得引用 WPF、DevExpress、AsunImage、设备 SDK 或产品 Shell。测试仍可由测试 runner 调用同一公开方法，不能以另一个机械空工程替代。

固定执行命令（Windows PowerShell，工作目录为仓库根）为：

```powershell
dotnet build .\tests\Modules\imaging-optimization\Asun.Modules.ImagingOptimization.Core.Tests\Asun.Modules.ImagingOptimization.Core.Tests.csproj --configuration Release --framework net10.0
dotnet run --project .\tests\Modules\imaging-optimization\Asun.Modules.ImagingOptimization.Core.Tests\Asun.Modules.ImagingOptimization.Core.Tests.csproj --configuration Release --framework net10.0 --no-build --no-restore -- --case four-candidate --deadline-ms 30000
dotnet run --project .\tests\Modules\imaging-optimization\Asun.Modules.ImagingOptimization.Core.Tests\Asun.Modules.ImagingOptimization.Core.Tests.csproj --configuration Release --framework net10.0 --no-build --no-restore -- --suite contract,recovery,quota --deadline-ms 120000
```

命令只有在工程获准并创建后执行；当前工程尚未创建，不能声称命令已通过。`--case four-candidate` 必须只运行第11节固定合成例；`--suite` 固定为契约/生命周期恢复/资源配额三组。外层PowerShell以§10.4的Process进程树等待截止控制，单 case 30 s、suite 120 s；外层截止到期终止整个隔离进程并判失败，不能留下后台 Task 作为成功。进程终止不等于设备已停止，真实适配器仍必须按原 Task/ObservationId 对账；本 Host 仅离线 fixture，无设备副作用。

### 10.2 完整 Program 与两条独立字段映射

以下代码的落点唯一为上述Core.Tests目录中的`Program.cs`及同项目内Host fixture文件；可拆文件但不得拆第二工程。它是**按拟实施Core公开签名编写的完整Host源模板**，当前Core不存在、尚未消费编译，不能称可运行/测试通过。常量均为合成测试值，不是部署默认。`Sample.BuildConsole`与`BuildWorker`从独立的数组/标量输入重新映射；共享的仅是无状态映射函数，无共享Services/请求/Store/Owner。Observation/Evaluation均为本fixture精确计算的合成回放值，无相机/SDK/native；其它故障点在§10.3冻结。

```csharp
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.ImagingOptimization;

internal static class Program
{
    public static async Task<int> Main(string[] args)
    {
        string[] cases;
        int deadline;
        if (args.Length == 4 && args[0] == "--case" && args[1] == "four-candidate" &&
            args[2] == "--deadline-ms" && int.TryParse(args[3], out deadline) && deadline == 30000)
            cases = ["console", "worker"];
        else if (args.Length == 4 && args[0] == "--suite" && args[1] == "contract,recovery,quota" &&
                 args[2] == "--deadline-ms" && int.TryParse(args[3], out deadline) && deadline == 120000)
            cases = ["console", "worker", "invalid", "late", "store-fault", "query-only", "quota"];
        else return 2;
        using var suite = new CancellationTokenSource(deadline);
        var pool = new RootPool(); // 一次suite固定一个根槽；运行串行，没有无界恢复集合。
        foreach (string name in cases)
        {
            using var one = CancellationTokenSource.CreateLinkedTokenSource(suite.Token);
            one.CancelAfter(10000); // case的Host业务+cleanup总观察10s；外层case进程30s。
            var raw = name switch // 各方法只调用一次；两个Host各自重新映射数据/服务。
            {
                "console" => ImagingOptimizationHostFixture.RunConsoleCaseAsync(pool, one.Token),
                "worker" => ImagingOptimizationWorkerFixture.RunWorkerCaseAsync(pool, one.Token),
                _ => Host.ExecuteAsync(name, pool, one.Token)
            };
            HostResult result;
            try { result = await raw.WaitAsync(one.Token); }
            catch (Exception ex)
            {
                if (!pool.RetainAcknowledged(ex)) throw new InvalidOperationException("outer-retention-not-acknowledged",ex); // 已强持原Host/端口引用。
                Console.Error.WriteLine(name + ": outer-case-timeout-or-fault");
                return 1; // 隔离离线进程失败退出；不宣称资源/native已归还。
            }
            Console.WriteLine($"{name}: business={result.Business}; cleanup={result.Cleanup}");
            if (!result.Passed || pool.HasRoot) return 1;
        }
        return 0;
    }
}
internal static class ImagingOptimizationHostFixture
{
    public static Task<HostResult> RunConsoleCaseAsync(RootPool pool, CancellationToken ct) =>
        Host.ExecuteAsync("console",pool,ct);
}
internal static class ImagingOptimizationWorkerFixture
{
    public static Task<HostResult> RunWorkerCaseAsync(RootPool pool, CancellationToken ct) =>
        Host.ExecuteAsync("worker",pool,ct);
}
internal sealed record HostResult(string Business, string Cleanup, bool Passed,
    Exception? BusinessError, Exception? CleanupError);
internal sealed class RootPool
{
    private Root? held;
    public bool HasRoot => held is not null;
    public Root Reserve()
    {
        if (held is not null) throw new InvalidOperationException("root-capacity");
        return held = new Root(this); // 槽在任何service/factory之前占用。
    }
    public void Release(Root r)
    {
        if (!ReferenceEquals(r, held)) throw new InvalidOperationException("root-owner");
        held = null;
    }
    public bool RetainAcknowledged(Exception? diagnostic = null)
    {
        if (held is null) return false;
        held.RetentionAcknowledged = true;
        held.CleanupError ??= diagnostic;
        return true; // 本pool强持且确认接收；不是无消费者日志引用。
    }
}
internal sealed class Root(RootPool pool)
{
    public Fixture? Fixture;
    public ImagingOptimizer? Optimizer;
    public readonly List<Task> OriginalTasks = new(4);
    public Exception? BusinessError, CleanupError;
    public bool RetentionAcknowledged;
    public Task<T> Start<T>(Func<ValueTask<T>> factory)
    {
        if (OriginalTasks.Count == 4) throw new InvalidOperationException("root-task-capacity");
        // root已强持fixture/optimizer；先保留task槽，再调factory，不重复消费ValueTask。
        int slot = OriginalTasks.Count;
        OriginalTasks.Add(Task.CompletedTask);
        try
        {
            Task<T> raw = factory().AsTask();
            OriginalTasks[slot] = raw;
            return raw;
        }
        catch (Exception ex) { OriginalTasks[slot] = Task.FromException(ex); throw; }
    }
    public Task StartDispose(Func<ValueTask> factory)
    {
        if (OriginalTasks.Count == 4) throw new InvalidOperationException("root-task-capacity");
        int slot = OriginalTasks.Count;
        OriginalTasks.Add(Task.CompletedTask);
        try { var raw = factory().AsTask(); OriginalTasks[slot] = raw; return raw; }
        catch (Exception ex) { OriginalTasks[slot] = Task.FromException(ex); throw; }
    }
    public bool AllEnded => OriginalTasks.All(t => t.IsCompleted);
    public void ReleaseConfirmed()
    {
        if (!AllEnded || (Fixture?.HasPending ?? false)) throw new InvalidOperationException("not-released");
        foreach (var task in OriginalTasks) if (task.IsFaulted) _ = task.Exception;
        Fixture?.DisposeConfirmed();
        Optimizer = null; Fixture = null; OriginalTasks.Clear(); pool.Release(this);
    }
}
internal static class Host
{
    public static async Task<HostResult> ExecuteAsync(string name, RootPool pool, CancellationToken caseToken)
    {
        Root root = pool.Reserve(); // 在fixture、数组、services和optimizer构造之前。
        string business = "not-started", cleanup = "not-observed";
        bool assertion = false, constructed = false, released = false;
        OptimizerOptions? options = null;
        using var runCts = CancellationTokenSource.CreateLinkedTokenSource(caseToken);
        try
        {
            options = Sample.Options();
            root.Fixture = new Fixture(name); // 成功后立即附着；fixture构造本身不启动任务。
            var f = root.Fixture;
            var services = new OptimizerServices(f.Constraint, f.Observer, f.Evaluator, f.Store, null);
            root.Optimizer = new ImagingOptimizer(services, options); constructed = true;
            var request = name == "worker" ? Sample.BuildWorker() : Sample.BuildConsole();
            if (name == "invalid") request = request with { Budget = request.Budget with { MaxTrials = 0 } };
            var check = root.Optimizer.Validate(request);
            if (name == "invalid")
            {
                assertion = !check.IsValid && check.Plan is null && f.Observer.Calls == 0;
                business = "invalid-before-observe";
            }
            else if (name == "query-only")
            {
                var q = root.Start(() => root.Optimizer.GetRecommendationAsync("absent", runCts.Token));
                var qr = await q.WaitAsync(TimeSpan.FromSeconds(2), caseToken);
                assertion = qr.Lookup == LookupState.NotFound && !qr.IsFinal;
                business = "query-only-no-plan";
            }
            else
            {
                if (!check.IsValid) throw new InvalidOperationException("valid-sample-rejected");
                if (name is "console" or "worker") Sample.AssertGolden(request, check.Plan!);
                var first = root.Optimizer.PreviewNext(check.Plan!, null, 2);
                if (first.Candidates.Count == 0) throw new InvalidOperationException("preview");
                var raw = root.Start(() => root.Optimizer.RunAsync(check.Plan!, null, runCts.Token));
                try
                {
                    var result = await raw.WaitAsync(TimeSpan.FromMilliseconds(name == "late" ? 100 : 4000), caseToken);
                    business = result.State + "/" + result.StopReason;
                    assertion = name == "store-fault"
                        ? result.Recommendation.State != RecommendationState.IndependentlyVerified && f.Observer.Calls == 0
                        : result.ResourcesReleased && result.SearchComplete &&
                          result.Recommendation.State == RecommendationState.IndependentlyVerified &&
                          result.Recommendation.Candidates.Count == 1 && f.Observer.Calls == 5;
                    if (name is "console" or "worker") assertion &= f.Store.HasExpectedFrontier;
                    if (name == "quota") assertion &= f.Store.QuotaChecked;
                }
                catch (TimeoutException) when (name == "late")
                {
                    runCts.Cancel(); business = "observation-timeout-original-owned";
                    assertion = !raw.IsCompleted && pool.HasRoot && f.Observer.Pending;
                }
                catch (Exception ex) when (name == "store-fault")
                {
                    root.BusinessError = ex; business = "store-fault";
                    assertion = f.Observer.Calls == 0 && (ex is IOException || ex is ImagingOptimizationException { Code:"IO-015" });
                }
            }
        }
        catch (Exception ex) { root.BusinessError = ex; business = ex.GetType().Name; }
        // 不在finally返回，也不让cleanup异常覆盖业务轴。cleanup使用独立token，不链接run/case取消。
        using var cleanupCts = new CancellationTokenSource((int)(options?.CleanupObservationLimit.Value ?? 2000)); // 构造失败用suite显式启动清理值2000ms。
        try
        {
            root.Fixture?.Observer.ReleaseGate(); // late夹具的已登记原工作，非补曝光。
            if (!constructed)
            {
                // 所有fixture构造器纯分配；若失败且未启动任务，已成功附着的部分可清理。
                if (!(root.Fixture?.HasPending ?? false)) { root.ReleaseConfirmed(); released = true; }
                cleanup = released ? "factory-failed-no-work" : "factory-owner-retained";
            }
            else
            {
                var closeRaw = root.Start(() => root.Optimizer!.CloseAsync(cleanupCts.Token));
                var receipt = await closeRaw.WaitAsync(cleanupCts.Token);
                if (name == "late" && receipt.UnresolvedIds.Count != 0)
                {
                    // 完成原Run后同Root有限Recover；无第二Observe，仍使用同cleanup总窗。
                    foreach (var task in root.OriginalTasks.ToArray())
                        try { await task.WaitAsync(cleanupCts.Token); }
                        catch (Exception ex) when (task.IsCompleted) { root.BusinessError ??= ex; }
                    var recoveryRaw = root.Start(() => root.Optimizer!.RecoverAsync("case-four-candidate",cleanupCts.Token));
                    var recovery = await recoveryRaw.WaitAsync(cleanupCts.Token);
                    receipt = new("case-four-candidate",recovery.ResourcesReleased,recovery.ResourcesReleased,
                        recovery.State==OptimizationRunState.ReconcileRequired?["case-four-candidate/0"]:[],null);
                }
                if (receipt.Drained && receipt.ResourcesReleased && receipt.UnresolvedIds.Count == 0)
                {
                    // 连业务原Task也等待到完成；任意fault读出保存，不丢引用、不重调Run。
                    foreach (var task in root.OriginalTasks.ToArray())
                        try { await task.WaitAsync(cleanupCts.Token); }
                        catch (Exception ex) when (task.IsCompleted) { root.BusinessError ??= ex; }
                    var disposeRaw = root.StartDispose(() => root.Optimizer!.DisposeAsync());
                    await disposeRaw.WaitAsync(cleanupCts.Token);
                    root.ReleaseConfirmed(); released = true; cleanup = "released-confirmed";
                }
                else cleanup = "unresolved-root-retained";
            }
        }
        catch (Exception ex) { root.CleanupError = ex; cleanup = "cleanup-" + ex.GetType().Name; }
        if (!released && !pool.RetainAcknowledged(root.CleanupError))
            throw new InvalidOperationException("retention-not-acknowledged");
        return new HostResult(business, cleanup, assertion && released,root.BusinessError,root.CleanupError);
    }
}
internal static class Sample
{
    public static InputLimits Limits() => new(1024, 256, 100000);
    public static Budget Budget() => new(5, 4, null, new(1000), new(1000), null, null,
        1, 1000, 100, 1000000, 10000000);
    public static OptimizerOptions Options() => new(8, 2, 1, new(1000), 2, 1000000, new(2000), Limits());
    // 工程台源:独立decimal数组与显式名义值；Worker源:独立整数/字符串字段导出，不借A对象。
    public static OptimizationRequest BuildConsole() => Map([100m,200m], [0m,1m], 100, 0m);
    public static OptimizationRequest BuildWorker()
    {
        long[] exportedMicroseconds = [100,200]; string[] exportedDb = ["0","1"];
        return Map(exportedMicroseconds.Select(x => (decimal)x).ToArray(),
            exportedDb.Select(x => decimal.Parse(x, System.Globalization.CultureInfo.InvariantCulture)).ToArray(),
            exportedMicroseconds[0], decimal.Parse(exportedDb[0], System.Globalization.CultureInfo.InvariantCulture));
    }
    private static OptimizationRequest Map(decimal[] exposure, decimal[] gain, long nominalExposure, decimal nominalGain)
    {
        var budget = Budget(); var limits = Limits();
        var x = new AxisTarget("s0", AxisKind.Exposure, null);
        var g = new AxisTarget("s0", AxisKind.Gain, null);
        var l = new AxisTarget("s0", AxisKind.LightLevel, "l0");
        var enabled = new AxisTarget("s0", AxisKind.LightEnabled, "l0");
        var cap = ImagingContractCodec.SealCapability(new("cap-v1", "",
            [new(x,"us",exposure,null,"ticks-v1"), new(g,"dB",gain,null,"ticks-v1"),
             new(l,"NativeCode",[1m],null,"ticks-v1"), new(enabled,"bool",[1m],null,"ticks-v1")],1), budget,limits);
        Candidate CandidateAt(long e, decimal d) => ImagingContractCodec.CreateCandidate("space-v1", "constraint-v1",
            [new("s0",new(e),new(d),[new("l0",new(1m,LightLevelUnit.NativeCode),true)],"normal",0)],budget,limits);
        var baseline = CandidateAt(nominalExposure, nominalGain); var selected = CandidateAt(100,1m);
        var validation = ImagingContractCodec.SealValidation(new("validation-v1","",
            [new("search-1","target-1","method-1","sample-1","nominal","search",ObservationPhase.Search,1,["clear","sat"],[]),
             new("verify-1","target-1","method-1","sample-2","nominal","holdout",ObservationPhase.Verification,1,["clear","sat"],[])],
            [selected.CandidateId]),budget,limits);
        return new("case-four-candidate","synthetic","0.2","space-v1",cap,
            new("constraint-v1", new string('a',64), "rules-v1"),
            [new("exposure",x,"us",exposure,false,"cap-v1"),new("gain",g,"dB",gain,false,"cap-v1")], baseline,
            [new("clear","target-1","method-1",ObjectiveDirection.Maximize,"score",true,null,null,"method-v1"),
             new("sat","target-1","method-1",ObjectiveDirection.Minimize,"synthetic-unit",true,null,null,"method-v1")],
            validation,budget,SearchPolicy.DeterministicMixedRadix,new("search-v1",[],0,null),"input-v1",["source-v1"]);
    }
    public static void AssertGolden(OptimizationRequest r, OptimizationPlan p)
    {
        // 固定期望见§11.1；未调用被测codec生成期望。Candidate有完整literal字节比较。
        const string candidate = """{"SpaceRevision":"space-v1","ConstraintRevision":"constraint-v1","Steps":[{"StepId":"s0","Exposure":{"Value":100},"Gain":{"Value":"0"},"Lights":[{"ChannelId":"l0","Level":{"Value":"1","Unit":"NativeCode"},"Enabled":true}],"Mode":"normal","SequenceIndex":0}]}""";
        if (Encoding.UTF8.GetString(ImagingContractCodec.EncodeCandidateIdentity(r.Baseline,r.Budget,Limits())) != candidate ||
            r.Baseline.IdentityHash != "b0163544546b5743a113e6216872da3855ae9d117c9f812771c26612c65af4cd" ||
            r.Capability.ContentHash != Golden.Capability || r.Validation.ContentHash != Golden.Validation || p.PlanHash != Golden.Plan ||
            Encoding.UTF8.GetString(ImagingContractCodec.EncodeCapabilityContent(r.Capability,r.Budget,Limits())) != Golden.CapabilityBytes ||
            Encoding.UTF8.GetString(ImagingContractCodec.EncodeValidationContent(r.Validation,r.Budget,Limits())) != Golden.ValidationBytes ||
            Encoding.UTF8.GetString(ImagingContractCodec.EncodePlanContent(p,r.Budget,Limits())) != Golden.PlanBytes)
            throw new InvalidOperationException("canonical-golden");
    }
}
internal sealed class Fixture
{
    public readonly ReplayConstraint Constraint = new();
    public readonly ReplayObserver Observer;
    public readonly ReplayEvaluator Evaluator = new();
    public readonly ReplayStore Store;
    public Fixture(string name) { Observer = new(name == "late"); Store = new(name == "store-fault", name == "quota"); }
    public bool HasPending => Observer.Pending;
    public void DisposeConfirmed() { if (HasPending) throw new InvalidOperationException("fixture-pending"); Store.ClearConfirmed(); }
}
internal sealed class ReplayConstraint : IConstraintPolicy
{
    public string Revision => "constraint-v1";
    public string ContentHash => new('a',64);
    public ConstraintDecision Check(Candidate c, IReadOnlyList<ExposureStep> s) => new(true,[],0,null);
}
internal sealed class ReplayObserver(bool gated) : IObservationPort
{
    public string Revision => "obs-v1";
    private readonly TaskCompletionSource<bool> gate = new(TaskCreationOptions.RunContinuationsAsynchronously);
    private readonly Dictionary<string,(ObservationRequest Request,ObservationReceipt Receipt)> known = new(StringComparer.Ordinal);
    private Task<ObservationReceipt>? inFlight;
    private string? inFlightId;
    public int Calls { get; private set; }
    public bool Pending { get; private set; }
    public void ReleaseGate() => gate.TrySetResult(true);
    public ValueTask<ObservationReceipt> ObserveAsync(ObservationRequest r, PortContext c, CancellationToken ct)
    {
        if (inFlight is { IsCompleted:false })
        {
            if (inFlightId != r.ObservationId) throw new InvalidOperationException("parallel-not-supported");
            return new(inFlight); // 同ID原task；不新开曝光/后台任务。
        }
        inFlightId = r.ObservationId;
        inFlight = ObserveCoreAsync(r,c,ct);
        return new(inFlight);
    }
    private async Task<ObservationReceipt> ObserveCoreAsync(ObservationRequest r, PortContext c, CancellationToken ct)
    {
        if (known.TryGetValue(r.ObservationId,out var old))
        { if (old.Request.PlanHash != r.PlanHash || old.Request.Candidate.IdentityHash != r.Candidate.IdentityHash || old.Request.Cell != r.Cell)
              throw new InvalidOperationException("request-conflict"); return old.Receipt; }
        Calls++;
        if (gated && Calls == 1) { Pending = true; try { await gate.Task; } finally { Pending = false; } }
        var now = new DateTimeOffset(2026,10,10,0,0,0,TimeSpan.Zero);
        var digest = Convert.ToHexString(SHA256.HashData(ImagingContractCodec.EncodeActualSettings(r.RequestedSettings,r.Limits,Sample.Limits()))).ToLowerInvariant();
        var receipt = new ObservationReceipt(r.OperationId,r.ObservationId,r.Candidate.CandidateId,r.Cell.CellId,ObservationState.Accepted,
            [new("e-"+r.AttemptIndex,"physical-"+r.AttemptIndex,r.Cell.IndependenceGroup,"s0","replay-"+r.AttemptIndex,new string('b',64))],
            r.RequestedSettings,digest,new(0,null),now,now,null);
        known.Add(r.ObservationId,(r,receipt)); return receipt;
    }
    public ValueTask<ObservationReceipt> ReconcileAsync(ObservationRequest r, PortContext c, CancellationToken ct) =>
        ValueTask.FromResult(known.TryGetValue(r.ObservationId,out var v) ? v.Receipt :
            new(r.OperationId,r.ObservationId,r.Candidate.CandidateId,r.Cell.CellId,ObservationState.Unknown,[],[],"",new(null,null),
                new(2026,10,10,0,0,0,TimeSpan.Zero),null,"unknown"));
    public async ValueTask<DrainReceipt> DrainAsync(string id, PortContext c, CancellationToken ct)
    {
        if (inFlight is not null) await inFlight.WaitAsync(ct); // Drain等待原Observe，不仅看gate已set。
        return new(id,!Pending,!Pending,Pending?[id+"/0"]:[],null);
    }
}
internal sealed class ReplayEvaluator : IEvaluationAdapter
{
    public string Revision => "eval-v1";
    public ValueTask<Evaluation> EvaluateAsync(ObservationRequest r, ObservationReceipt receipt, PortContext c, CancellationToken ct)
    {
        if (r.ObservationId != receipt.ObservationId || r.Cell.CellId != receipt.CellId) throw new InvalidOperationException("mapping");
        var s = r.RequestedSettings[0]; (double clear,double sat) = (s.Exposure.Value,s.Gain.Value) switch
        { (100,0m)=>(8,2), (100,1m)=>(9,3), (200,0m)=>(7,4), (200,1m)=>(8,2), _=>throw new InvalidOperationException("unmapped-setting") };
        string[] evidence = receipt.Evidence.Select(x=>x.EvidenceId).ToArray();
        return ValueTask.FromResult(new Evaluation(r.ObservationId,r.Cell.CellId,
            [new("clear",clear,"score",ValueValidity.Valid,null,"method-v1",evidence),
             new("sat",sat,"synthetic-unit",ValueValidity.Valid,null,"method-v1",evidence)],[],true,Revision));
    }
    public ValueTask<DrainReceipt> DrainAsync(string id, PortContext c, CancellationToken ct) => ValueTask.FromResult(new DrainReceipt(id,true,true,[],null));
}
internal sealed class ReplayStore(bool failIntent, bool probeQuota) : IResultStore
{
    public string Revision => "store-v1";
    private readonly List<OptimizationEvent> events = new(100);
    private OptimizationResult? result;
    public bool QuotaChecked { get; private set; }
    public bool HasExpectedFrontier => events.Select(x=>x.Payload).OfType<RecommendationPayload>()
        .Any(x=>x.Recommendation.Candidates.Select(c=>c.IdentityHash).OrderBy(x=>x,StringComparer.Ordinal)
            .SequenceEqual(new[]{
                "b0163544546b5743a113e6216872da3855ae9d117c9f812771c26612c65af4cd",
                "c5eebb4b284ab0f443115f585ab32d0364846a9c900429561d8ed5bd4a348d1d",
                "e74b3a8af55e87705ad0e58bf7359ba6ef35209514522521410a3453ab657824"
            }.OrderBy(x=>x,StringComparer.Ordinal)));
    public ValueTask<StoreReceipt> AppendAsync(OptimizationEvent e,long expected,PortContext c,CancellationToken ct)
    {
        if (failIntent && e.Payload is IntentPayload) throw new IOException("intent-fault-before-observe");
        if (probeQuota && events.Count == 0)
        {
            if (!c.Quota.TryReserve(new(c.Limits.MaxMemoryBytes,0,0,0),out var tooLarge)) QuotaChecked = true;
            else { tooLarge!.Dispose(); throw new InvalidOperationException("quota-did-not-count-core"); }
        }
        var old=events.FirstOrDefault(x=>x.EventId==e.EventId);
        if(old is not null) return ValueTask.FromResult(new StoreReceipt(old.PayloadDigest==e.PayloadDigest,true,old.Sequence,null));
        if(expected!=events.Count || e.Sequence!=expected+1 || events.Count==100) return ValueTask.FromResult(new StoreReceipt(false,false,events.Count,"cas-or-capacity"));
        if(!c.Quota.TryReserve(new(1024,0,0,0),out var reservation)) throw new InvalidOperationException("store-memory");
        using (reservation!)
        {
            events.Add(e);
            return ValueTask.FromResult(new StoreReceipt(true,true,e.Sequence,null));
        }
    }
    public ValueTask<StoreReceipt> CommitAsync(OptimizationResult r,long expected,PortContext c,CancellationToken ct)
    {
        if(expected!=events.Count || r.LastSequence!=expected || (result is not null && result!=r))
            return ValueTask.FromResult(new StoreReceipt(false,false,events.Count,"commit-conflict"));
        result=r;
        // 仅进程内模拟耐久；events有100条硬容量，归fixture根Owner，不能用于设备任务。
        return ValueTask.FromResult(new StoreReceipt(true,true,expected,null));
    }
    public ValueTask<EventPage> ReadAsync(string id,long after,int limit,IResourceQuota quota,CancellationToken ct)
    {
        if(limit<=0 || after<0) throw new ArgumentOutOfRangeException();
        if (!quota.TryReserve(new(4096,0,0,0),out var readMemory)) throw new InvalidOperationException("query-quota");
        using var reservedRead = readMemory;
        var matches=events.Where(x=>x.OperationId==id && x.Sequence>after).Take(limit).ToArray();
        long last=matches.Length==0?after:matches[^1].Sequence;
        return ValueTask.FromResult(new EventPage(events.Any(x=>x.OperationId==id)?LookupState.Found:LookupState.NotFound,
            matches,last,events.Any(x=>x.OperationId==id && x.Sequence>last),null));
    }
    public ValueTask<ResultLookup> ReadResultAsync(string id,IResourceQuota quota,CancellationToken ct)
    {
        if (!quota.TryReserve(new(4096,0,0,0),out var readMemory)) throw new InvalidOperationException("query-quota");
        using var reservedRead = readMemory;
        return ValueTask.FromResult(result?.OperationId==id?new ResultLookup(LookupState.Found,result,null):new(LookupState.NotFound,null,null));
    }
    public void ClearConfirmed() { events.Clear();result=null; }
}
```

代码中的`Golden`为三条独立literal hash与三条对应literal bytes常量，定义见§11.1；没有未给出实现的Factory/HostOutcome/cleanupWaitToken。`Root`最多四个原Task槽（业务或query、Close、Dispose及一个恢复保留槽），暂停case/root始终可达。Start的占位槽在factory抛错时绑定Task.FromException并记录失败，不能伪装成功；若外部factory同步抛错前已启动工作，其端口Owner仍负责原ObservationId，Root.Fixture/服务引用保留，不能借“没有Task返回”释放未知资源。fixture纯构造、无SDK，无此物理事实；获准后的真实Host必须接端口Owner未决表，不能抄fixture的HasPending=false作设备证明。

### 10.3 有限 suite、故障门控与全部公开接口

上述最小Program实际实现三类公开业务端口和store的**全部**方法（Check；Observe/Reconcile/Drain；Evaluate/Drain；Append/Commit/Read/ReadResult），Revision固定；它只覆盖下表有限基础case，不冒充完整§12测试。附加测试仍在同Tests项目内使用同接口实现/独立Fixture，以下注入点必须在测试私有构造参数/record固定，不反射Core私有字段。公开端口签名以§3为准，注入动作全部有原Task Owner和外层截止。

| case/suite | 触发点/门控 | 可判定断言 |
|---|---|---|
| four-candidate / contract | Console与Worker重新构造同数据，独立根/store；§11.1 literal bytes/hash | 两者完整前沿=1/2/4、五次模拟Observe、最终仅候选2已验证；Golden四类身份相符 |
| invalid / contract | Budget.MaxTrials=0，Validate前不可调用Observer/Store | Invalid、无Plan、设备/模拟观察调用0；没有Run仍Close/Dispose有限 |
| late / recovery | 首Observe原Task等待TCS，100ms Host业务观察窗先到，随后停止意图/显式ReleaseGate | 原Task未结束时Root保留、资源不可释放；控制清理后原Task完成方可Root释放，不多一次Observe |
| store-fault / recovery | 耐久Intent之前Append抛IOException | 原业务异常/停止原因与cleanup各自保存；Observe=0；清理异常不覆盖业务；store未完成写任务/reservation须由fixtureOwner归还后才释放root；本例Append临时reservation在方法返回前已归还，事实只在有界fixture内存中模拟 |
| query-only / recovery | 没有RunPlan，查询absent | NotFound非final；构造期CleanupObservationLimit决定Close/Dispose观察，不读虚构MaxDrainTime |
| quota / quota | 首Plan写时申请整个MaxMemoryBytes，Core已预留其快照/收尾额度 | TryReserve=false、不分配、不把已用Core当零；正常路径仍资源收尾确认 |
| 补充契约断言（同Tests） | Observer同ID异request、Evaluation缺目标/NaN/方法错；Store页gap/同EventId异digest | IO-018/010/012，工程缺口不得最终已验证；所有接口有模拟调用计数 |
| 补充Owner/cleanup断言（同Tests） | 构造器同步抛错未取资源；查询TCS不合作；Close/Dispose同步IO异常、返回Task不合作；先成功Close再query/Recover | 构造前根槽预留；异常两轴；构造期期限有效；新查询与Dispose互斥；未知Root保留有接收确认，重复等待不调第二factory |

后两行是整个模块正式测试门而非最小Program已经执行的案例；实现阶段在同有限suite中补足，不以基础程序代替关键并发/恢复验证。外部端口不合作的同步无限阻塞/任意用户getter由隔离进程外截止判失败，不声称取消成功。

### 10.4 双轴、构造期预算及外层进程门

Root池槽必须在构造/分配服务之前预留，原ValueTask只AsTask一次；Host业务等待使用原Task.WaitAsync作为**观察**，观察task超时不移除OriginalTasks、不Dispose原服务。cleanup用独立`Options.CleanupObservationLimit`创建CTS，不链接已取消的Run/case token，整个Close+原业务归还+Dispose共用这一个窗，不能每await重置截止。业务及cleanup各保存字符串/异常，任何Exception进入各自轴而不从finally抛出覆盖原业务。释放Root还须确认所有原Task已完成（含fault异常已读取）、fixtureOwner无Pending及Close真实归还；失败/未知仅在RootPool.RetainAcknowledged返回true后交回原强持池。再次Close/Recover须此Root接续原task，不能新建optimizer接管。

Program入口的外层case原Task也必须在进程根池记录/强持直到返回；`Main`局部raw加RootPool是有限一个case的根持有者，超时退出前确认RetainAcknowledged，禁止开下一case。尚未有任何resource/factory启动的构造失败可释放未取得资源的槽；如端口已启动但同步throw，其端口原Owner保持在已附着Fixture/Services中，须对账/native排空，不当Task.CompletedTask占位为设备已归还证明。

根槽保持不等于“通过”：Host.Passed要求业务断言与资源释放两个轴均通过，超时/未知/不合作均exit 1。外层PowerShell必须限制build<=120s、每case进程<=30s、suite进程<=120s并kill隔离进程/等待其退出；保留退出码/stdout/stderr以已有CI日志为消费者，不生成新报告。可执行外层BCL/PowerShell方法如下（在终端直接执行，不另存脚本）：

```powershell
function Invoke-ImagingGate([string[]]$GateArgs, [int]$Seconds) {
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new('dotnet')
    $startInfo.WorkingDirectory = (Get-Location).Path
    $startInfo.UseShellExecute = $false
    # stdout/stderr沿终端或CI已有日志；不异步读到无界内存、不另生成证据文件。
    foreach ($arg in $GateArgs) { $startInfo.ArgumentList.Add($arg) }
    $proc = [System.Diagnostics.Process]::new()
    $proc.StartInfo = $startInfo
    try {
        if (-not $proc.Start()) { throw 'process-start-failed' }
        if (-not $proc.WaitForExit($Seconds * 1000)) {
            $proc.Kill($true) # 整棵隔离fixture进程树；本例没有SDK/设备。
            if (-not $proc.WaitForExit(5000)) { throw 'process-tree-exit-unconfirmed' }
            throw 'outer-deadline-failed'
        }
        if ($proc.ExitCode -ne 0) { throw 'imaging-gate-failed' }
    } finally { $proc.Dispose() }
}
$testProject = '.\tests\Modules\imaging-optimization\Asun.Modules.ImagingOptimization.Core.Tests\Asun.Modules.ImagingOptimization.Core.Tests.csproj'
Invoke-ImagingGate @('build',$testProject,'--configuration','Release','--framework','net10.0') 120
Invoke-ImagingGate @('run','--project',$testProject,'--configuration','Release','--framework','net10.0','--no-build','--no-restore','--','--case','four-candidate','--deadline-ms','30000') 30
Invoke-ImagingGate @('run','--project',$testProject,'--configuration','Release','--framework','net10.0','--no-build','--no-restore','--','--suite','contract,recovery,quota','--deadline-ms','120000') 120
```

上面仅定义实施后命令，当前未执行；PowerShell7使用Process.Kill(entireProcessTree:true)并等待退出，失败不得判门通过。fixture进程退出仅证明隔离进程生命周期，不能证明生产设备/native安全归还。工程声明与唯一引用完整形状为：

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <OutputType>Exe</OutputType>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="../../../../src/Modules/imaging-optimization/Asun.Modules.ImagingOptimization.Core/Asun.Modules.ImagingOptimization.Core.csproj" />
  </ItemGroup>
</Project>
```

这是同一Core.Tests工程的实施约定，不要求现在建空项目；不用测试包/SDK内部/额外NuGet才能执行最小Host，正式测试若已有runner可调用Host方法，不能创建第二权威接口。build生成BCL项目所需assets是正常构建，不改变AsunImage/DevExpress冻结依赖。

## 11. 可判定的合成算例与参数改变

以下仅用于Core算法/契约测试，不是客户指标、设备安全值、独立样本或性能资格。

- 一步`s0`、通道`l0`固定Enabled=true/NativeCode=1；曝光轴[100,200]us、增益轴[0,1]dB，能力允许这些值，纯约束全允许。基线(100,0)，各候选Search单格1次；两个必需目标：同一合成TargetRef/MethodRef中的清晰度Maximize（合成unit=`score`）、饱和Minimize（unit=`synthetic-unit`，值为合成相对量、不当像素比例资格），上下限null。按(100,0),(100,1),(200,0),(200,1)回放向量分别(8,2),(9,3),(7,4),(8,2)。期望前沿为第1、2、4项，第3项被第1项支配；第1/4同值不同设置均保留，显示按hash排序。VerifyCandidateIds仅选第2项，Verification单格1次（同目标清单、Offsets为空）回放(9,3)，独立组不同且物理ID不重复；MaxTrials=5、MaxCandidates=4，最后一次额度刚好消耗完且计划无剩余时，SearchComplete=true，最终推荐只含已选第2项，IndependentlyVerified（仅模拟标志）。
- 该例其它显式预算：MaxWallTime=null、MaxStageTime=1000ms、MaxDrainTime=1000ms、MaxEnergyJ/MaxTemperatureC=null、MaxConcurrentObservations=1、MaxSummaryItems=1000、MaxEventQueueItems=100、MaxMemoryBytes=1000000、MaxDiskBytes=10000000；这些只解释请求，不作默认或验收门。将MaxTrials改4，搜索仍有同一前沿，但验证缺口→NeedsReview，不能因4次搜索成功显示已验证。
- 多条件反例：Maximize目标，候选A两个条件值9/4、候选B=6/6，汇总分别4/6，B优于A；不能用平均6.5/6倒置结果。一个条件Missing时A完全不可比较，不以9替代。最小化目标同理取最大值，逐条件上下限均检查。
- 联合硬约束反例：宿主合成模型总电流<=120mA，两个通道各80mA，单轴允许但组合Check拒绝IO-004，Observe调用为零；不得把这个值迁入真实设备Profile。
- 实际读回不一致/无ROI：Accepted仍须核对完整读回/证据，错设置IO-018或缺证据IO-011，缺必需目标IO-010，推荐NoCandidate/NeedsReview而非合格。结构合法低质量基线仍保留真实值供改善。
- 参数改变：草稿曝光/能力档位、ROI、MethodRevision、Cells、预算、先验或策略变化均产生新PlanHash和新OperationId；原cursor不能用于新plan，IO-012。锁定轴改成非基线值IO-003。运行中绑定修订变化停止新Intent并排空，历史结果可读，不以新评价改写旧结果。

### 11.1 独立 canonical 字节 / SHA-256 期望（§10完整字段）

这些期望按字段直接写出并用独立标准库SHA-256复算，不运行或调用被测ImagingContractCodec。UTF8、无BOM/换行/尾空白；表中`C`/`V`/`P`指下面原字节串而非DTO ToString。四候选identity只变Exposure.Value和Gain.Value，其余同C1；对应CandidateId=`c-`+摘要。

| 对象 | 独立期望 SHA-256 |
|---|---|
| Candidate 100us/0dB | `b0163544546b5743a113e6216872da3855ae9d117c9f812771c26612c65af4cd` |
| Candidate 100us/1dB | `c5eebb4b284ab0f443115f585ab32d0364846a9c900429561d8ed5bd4a348d1d` |
| Candidate 200us/0dB | `7eef88936e60171539e80de50782f98569e8c0ffc5e442f149c31ab87b51ba84` |
| Candidate 200us/1dB | `e74b3a8af55e87705ad0e58bf7359ba6ef35209514522521410a3453ab657824` |
| Capability（排除自身ContentHash） | `67fc40fb6f10a3ddd28dd80c121edf5c0f149991c3a26067787ed319e92cd9b9` |
| Validation（排除自身ContentHash） | `544ce3e7b8d98d5c75ce4fad29bb5e2ea7a98aa7d873d55a8bd387f6ce95b0fd` |
| Plan（排除自身PlanHash，包含Request全部字段与绑定修订） | `2cfe3637f8fba0349e4d8b88627f0abb3469490acaf2bd0b813562bb29eed1ee` |

C1: Candidate identity 的完整原字节文本：

```json
{"SpaceRevision":"space-v1","ConstraintRevision":"constraint-v1","Steps":[{"StepId":"s0","Exposure":{"Value":100},"Gain":{"Value":"0"},"Lights":[{"ChannelId":"l0","Level":{"Value":"1","Unit":"NativeCode"},"Enabled":true}],"Mode":"normal","SequenceIndex":0}]}
```

C: Capability content 的完整原字节文本：

```json
{"Revision":"cap-v1","Axes":[{"Target":{"StepId":"s0","Kind":"Exposure","ChannelId":null},"Unit":"us","AllowedValues":["100","200"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"},{"Target":{"StepId":"s0","Kind":"Gain","ChannelId":null},"Unit":"dB","AllowedValues":["0","1"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"},{"Target":{"StepId":"s0","Kind":"LightLevel","ChannelId":"l0"},"Unit":"NativeCode","AllowedValues":["1"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"},{"Target":{"StepId":"s0","Kind":"LightEnabled","ChannelId":"l0"},"Unit":"bool","AllowedValues":["1"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"}],"MaxParallelObservations":1}
```

V: Validation content 的完整原字节文本：

```json
{"Revision":"validation-v1","Cells":[{"CellId":"search-1","TargetRef":"target-1","MethodRef":"method-1","SpecimenRef":"sample-1","ConditionRef":"nominal","IndependenceGroup":"search","Phase":"Search","Repetitions":1,"ObjectiveIds":["clear","sat"],"Offsets":[]},{"CellId":"verify-1","TargetRef":"target-1","MethodRef":"method-1","SpecimenRef":"sample-2","ConditionRef":"nominal","IndependenceGroup":"holdout","Phase":"Verification","Repetitions":1,"ObjectiveIds":["clear","sat"],"Offsets":[]}],"VerifyCandidateIds":["c-c5eebb4b284ab0f443115f585ab32d0364846a9c900429561d8ed5bd4a348d1d"]}
```

P: Plan content 的完整原字节文本：

```json
{"Request":{"OperationId":"case-four-candidate","Purpose":"synthetic","ContractVersion":"0.2","SpaceRevision":"space-v1","Capability":{"Revision":"cap-v1","ContentHash":"67fc40fb6f10a3ddd28dd80c121edf5c0f149991c3a26067787ed319e92cd9b9","Axes":[{"Target":{"StepId":"s0","Kind":"Exposure","ChannelId":null},"Unit":"us","AllowedValues":["100","200"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"},{"Target":{"StepId":"s0","Kind":"Gain","ChannelId":null},"Unit":"dB","AllowedValues":["0","1"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"},{"Target":{"StepId":"s0","Kind":"LightLevel","ChannelId":"l0"},"Unit":"NativeCode","AllowedValues":["1"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"},{"Target":{"StepId":"s0","Kind":"LightEnabled","ChannelId":"l0"},"Unit":"bool","AllowedValues":["1"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"}],"MaxParallelObservations":1},"Constraints":{"Revision":"constraint-v1","ContentHash":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","RulesEvidenceRef":"rules-v1"},"Axes":[{"AxisId":"exposure","Target":{"StepId":"s0","Kind":"Exposure","ChannelId":null},"Unit":"us","AllowedValues":["100","200"],"Locked":false,"SourceRevision":"cap-v1"},{"AxisId":"gain","Target":{"StepId":"s0","Kind":"Gain","ChannelId":null},"Unit":"dB","AllowedValues":["0","1"],"Locked":false,"SourceRevision":"cap-v1"}],"Baseline":{"CandidateId":"c-b0163544546b5743a113e6216872da3855ae9d117c9f812771c26612c65af4cd","Steps":[{"StepId":"s0","Exposure":{"Value":100},"Gain":{"Value":"0"},"Lights":[{"ChannelId":"l0","Level":{"Value":"1","Unit":"NativeCode"},"Enabled":true}],"Mode":"normal","SequenceIndex":0}],"SpaceRevision":"space-v1","ConstraintRevision":"constraint-v1","IdentityHash":"b0163544546b5743a113e6216872da3855ae9d117c9f812771c26612c65af4cd"},"Objectives":[{"ObjectiveId":"clear","TargetRef":"target-1","MethodRef":"method-1","Direction":"Maximize","Unit":"score","Required":true,"Lower":null,"Upper":null,"MethodRevision":"method-v1"},{"ObjectiveId":"sat","TargetRef":"target-1","MethodRef":"method-1","Direction":"Minimize","Unit":"synthetic-unit","Required":true,"Lower":null,"Upper":null,"MethodRevision":"method-v1"}],"Validation":{"Revision":"validation-v1","ContentHash":"544ce3e7b8d98d5c75ce4fad29bb5e2ea7a98aa7d873d55a8bd387f6ce95b0fd","Cells":[{"CellId":"search-1","TargetRef":"target-1","MethodRef":"method-1","SpecimenRef":"sample-1","ConditionRef":"nominal","IndependenceGroup":"search","Phase":"Search","Repetitions":1,"ObjectiveIds":["clear","sat"],"Offsets":[]},{"CellId":"verify-1","TargetRef":"target-1","MethodRef":"method-1","SpecimenRef":"sample-2","ConditionRef":"nominal","IndependenceGroup":"holdout","Phase":"Verification","Repetitions":1,"ObjectiveIds":["clear","sat"],"Offsets":[]}],"VerifyCandidateIds":["c-c5eebb4b284ab0f443115f585ab32d0364846a9c900429561d8ed5bd4a348d1d"]},"Budget":{"MaxTrials":5,"MaxCandidates":4,"MaxWallTime":null,"MaxStageTime":{"Value":1000},"MaxDrainTime":{"Value":1000},"MaxEnergyJ":null,"MaxTemperatureC":null,"MaxConcurrentObservations":1,"MaxSummaryItems":1000,"MaxEventQueueItems":100,"MaxMemoryBytes":1000000,"MaxDiskBytes":10000000},"Search":"DeterministicMixedRadix","SearchOptions":{"Revision":"search-v1","PriorCandidates":[],"MaxRefinementRounds":0,"ProposalRevision":null},"InputRevision":"input-v1","RequiredEvidenceIds":["source-v1"]},"ObservationRevision":"obs-v1","EvaluatorRevision":"eval-v1","StoreRevision":"store-v1","ProposalRevision":null}
```

同一测试工程`Golden`明确写入下列独立literal（bytes是上面同一原文，重复于源常量为其真实消费者所需）（程序/期望的消费方是§10/12身份断言，不另建manifest）：

```csharp
internal static class Golden
{
    public const string CapabilityBytes = """{"Revision":"cap-v1","Axes":[{"Target":{"StepId":"s0","Kind":"Exposure","ChannelId":null},"Unit":"us","AllowedValues":["100","200"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"},{"Target":{"StepId":"s0","Kind":"Gain","ChannelId":null},"Unit":"dB","AllowedValues":["0","1"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"},{"Target":{"StepId":"s0","Kind":"LightLevel","ChannelId":"l0"},"Unit":"NativeCode","AllowedValues":["1"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"},{"Target":{"StepId":"s0","Kind":"LightEnabled","ChannelId":"l0"},"Unit":"bool","AllowedValues":["1"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"}],"MaxParallelObservations":1}""";
    public const string ValidationBytes = """{"Revision":"validation-v1","Cells":[{"CellId":"search-1","TargetRef":"target-1","MethodRef":"method-1","SpecimenRef":"sample-1","ConditionRef":"nominal","IndependenceGroup":"search","Phase":"Search","Repetitions":1,"ObjectiveIds":["clear","sat"],"Offsets":[]},{"CellId":"verify-1","TargetRef":"target-1","MethodRef":"method-1","SpecimenRef":"sample-2","ConditionRef":"nominal","IndependenceGroup":"holdout","Phase":"Verification","Repetitions":1,"ObjectiveIds":["clear","sat"],"Offsets":[]}],"VerifyCandidateIds":["c-c5eebb4b284ab0f443115f585ab32d0364846a9c900429561d8ed5bd4a348d1d"]}""";
    public const string PlanBytes = """{"Request":{"OperationId":"case-four-candidate","Purpose":"synthetic","ContractVersion":"0.2","SpaceRevision":"space-v1","Capability":{"Revision":"cap-v1","ContentHash":"67fc40fb6f10a3ddd28dd80c121edf5c0f149991c3a26067787ed319e92cd9b9","Axes":[{"Target":{"StepId":"s0","Kind":"Exposure","ChannelId":null},"Unit":"us","AllowedValues":["100","200"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"},{"Target":{"StepId":"s0","Kind":"Gain","ChannelId":null},"Unit":"dB","AllowedValues":["0","1"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"},{"Target":{"StepId":"s0","Kind":"LightLevel","ChannelId":"l0"},"Unit":"NativeCode","AllowedValues":["1"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"},{"Target":{"StepId":"s0","Kind":"LightEnabled","ChannelId":"l0"},"Unit":"bool","AllowedValues":["1"],"ReferenceScale":null,"QuantizationEvidenceRef":"ticks-v1"}],"MaxParallelObservations":1},"Constraints":{"Revision":"constraint-v1","ContentHash":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","RulesEvidenceRef":"rules-v1"},"Axes":[{"AxisId":"exposure","Target":{"StepId":"s0","Kind":"Exposure","ChannelId":null},"Unit":"us","AllowedValues":["100","200"],"Locked":false,"SourceRevision":"cap-v1"},{"AxisId":"gain","Target":{"StepId":"s0","Kind":"Gain","ChannelId":null},"Unit":"dB","AllowedValues":["0","1"],"Locked":false,"SourceRevision":"cap-v1"}],"Baseline":{"CandidateId":"c-b0163544546b5743a113e6216872da3855ae9d117c9f812771c26612c65af4cd","Steps":[{"StepId":"s0","Exposure":{"Value":100},"Gain":{"Value":"0"},"Lights":[{"ChannelId":"l0","Level":{"Value":"1","Unit":"NativeCode"},"Enabled":true}],"Mode":"normal","SequenceIndex":0}],"SpaceRevision":"space-v1","ConstraintRevision":"constraint-v1","IdentityHash":"b0163544546b5743a113e6216872da3855ae9d117c9f812771c26612c65af4cd"},"Objectives":[{"ObjectiveId":"clear","TargetRef":"target-1","MethodRef":"method-1","Direction":"Maximize","Unit":"score","Required":true,"Lower":null,"Upper":null,"MethodRevision":"method-v1"},{"ObjectiveId":"sat","TargetRef":"target-1","MethodRef":"method-1","Direction":"Minimize","Unit":"synthetic-unit","Required":true,"Lower":null,"Upper":null,"MethodRevision":"method-v1"}],"Validation":{"Revision":"validation-v1","ContentHash":"544ce3e7b8d98d5c75ce4fad29bb5e2ea7a98aa7d873d55a8bd387f6ce95b0fd","Cells":[{"CellId":"search-1","TargetRef":"target-1","MethodRef":"method-1","SpecimenRef":"sample-1","ConditionRef":"nominal","IndependenceGroup":"search","Phase":"Search","Repetitions":1,"ObjectiveIds":["clear","sat"],"Offsets":[]},{"CellId":"verify-1","TargetRef":"target-1","MethodRef":"method-1","SpecimenRef":"sample-2","ConditionRef":"nominal","IndependenceGroup":"holdout","Phase":"Verification","Repetitions":1,"ObjectiveIds":["clear","sat"],"Offsets":[]}],"VerifyCandidateIds":["c-c5eebb4b284ab0f443115f585ab32d0364846a9c900429561d8ed5bd4a348d1d"]},"Budget":{"MaxTrials":5,"MaxCandidates":4,"MaxWallTime":null,"MaxStageTime":{"Value":1000},"MaxDrainTime":{"Value":1000},"MaxEnergyJ":null,"MaxTemperatureC":null,"MaxConcurrentObservations":1,"MaxSummaryItems":1000,"MaxEventQueueItems":100,"MaxMemoryBytes":1000000,"MaxDiskBytes":10000000},"Search":"DeterministicMixedRadix","SearchOptions":{"Revision":"search-v1","PriorCandidates":[],"MaxRefinementRounds":0,"ProposalRevision":null},"InputRevision":"input-v1","RequiredEvidenceIds":["source-v1"]},"ObservationRevision":"obs-v1","EvaluatorRevision":"eval-v1","StoreRevision":"store-v1","ProposalRevision":null}""";
    public const string Capability = "67fc40fb6f10a3ddd28dd80c121edf5c0f149991c3a26067787ed319e92cd9b9";
    public const string Validation = "544ce3e7b8d98d5c75ce4fad29bb5e2ea7a98aa7d873d55a8bd387f6ce95b0fd";
    public const string Plan = "2cfe3637f8fba0349e4d8b88627f0abb3469490acaf2bd0b813562bb29eed1ee";
 }
```

额外标量映射（不改变设备参数）：decimal `1.00m`为字符串`"1"`、decimal `0m`为`"0"`、double `-0d`为`"0"`、double `1.25d`为`"1.25"`；DateTimeOffset UTC 的`O`文本是`"2026-10-10T00:00:00.0000000+00:00"`（不得混用DateTime的Z）；字符串“板”的默认JavaScriptEncoder表示`"\u677F"`，U+1F600表示`"\uD83D\uDE00"`（hex大写，代理对保序），无Normalization；null为JSON null，enum为声明名字符串。独立Golden断言同时比较literal byte串与摘要，不能只用被测Encode再Hash与被测Hash相比较。新增数据/契约版本另建新期望修订，保留旧生产事实身份，不重写客户参数。

## 12. 测试与性能门

| 类别 | 最小矩阵与断言 |
|---|---|
| 契约 | 空轴、重复轴、单位缺失、主版本未知；Validate 给出稳定错误码且无副作用 |
| 量化 | 非步进、边界、锁定轴、重复完整设置；不静默夹紧，IdentityHash 稳定 |
| 约束 | 联合电流、占空、温升、模式互斥；非法组合不进入端口 |
| 搜索 | 1、2、大空间、基线/先验/mixed顺序、局部轮次/建议回退、预算耗尽；顺序可重演，惰性不溢出 |
| 评价 | 缺失、Unknown、NaN、越域、失败 ROI；不填零，不提升到前沿 |
| 并发 | 重复回调、乱序完成、重入；单操作串行，迟到事件不改终态 |
| 取消恢复 | 排空成功、排空超时、重启；资源释放，未知需对账 |
| 兼容 | 旧快照、未知字段、适配器版本变更；迁移或 IO-012 阻断 |
| 回放 | 固定观察序列、独立保留集；候选、前沿、停止原因一致 |
| 观察关联 | 错步骤/触发/机器时基、名义/扰动设置错配、最终关灯值替代曝光读回、同物理帧不同版本；拒绝错配或重复计数，历史路径设备调用为零 |
| 验证覆盖 | 缺必需条件、单个条件失败、来源中途撤销；输出逐条件缺口，不以平均值或样本数生成 IndependentlyVerified |
| 基线 | 完整可信且物理合法的低质量基线可进入改善搜索；结构坏或物理不安全基线拒绝；推荐门不放宽 |
| 原Task Owner | factory前无槽不调用、同步抛出/同步完成、token已取消、WaitAsync超时原Task未结束、late成功/失败；已登记槽/lease不提前归还、收尾一次、不重触发；查询/控制槽满不新增任务 |
| 格与扰动 | 同MethodRef不同目标、ObjectiveIds缺/多/重复、未列目标不算缺项；候选100us能力[50,100,200]偏移+1为200us，候选200us偏移+1越界为验证缺口、端口调用0；锁轴/单位不换算 |
| 配额 | 两个并发reservation总额越界时第二次TryReserve=false/null且零分配；Dispose临时配额只归还一次；CommitDisk后Dispose不减少已写disk；Plan未读前查询/恢复仍有界 |
| 预算边界 | 预算差一次不得多发观察；恰好处理最后必需观察时不因计数等于上限误判；独立验证仍计入 MaxTrials，缺预算不能声称验证完成 |

未完成计划即预算耗尽时保留已搜索前沿和缺口，IO-007 为停止原因，推荐只作 NeedsReview/NoCandidate，不升级为 IndependentlyVerified；终态沿 §4 原状态与排空顺序，不移植来源的 BudgetExhausted/CompletedWithGaps 状态。扩大预算须使用新 OperationId，旧结果仅作为显式先验，不自动计作新运行的独立验证证据。

Benchmark的统计方法唯一引用[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)，本文不复制分位公式。测量方法已冻结，目标值待消费者Profile采纳；未有Target或最低有效样本/资源目标未采纳时结果NotEvaluated，允许诊断测量、不宣称通过。BenchmarkInputSize名称不得重复/未知；WarmupIterations>=0，MeasurementIterations/MinimumValidSamples>0且MinimumValidSamples<=MeasurementIterations，ConcurrentOperations>0，所有deadline/资源预算满足§3.1；Targets为空可诊断，非空MetricId/Statistic/TargetReference/AcceptanceRevision非空、组合唯一，阈值从冻结TargetReference解析，未解析不可判通过。BenchmarkProfile需显式给定版本/hash/指纹、冷启动或热路径、预热/测量/最低有效样本计划、并发操作数、有限SampleDeadline、ResourceLimits（§3的Budget）、ClockAndAffinityPolicy与StatisticPolicy（必须指上述统一口径）；不能因目标缺失填造值。不同环境/数据/运行时/适配器/负载/样本口径修订不得混比。

模块InputSizes.Name仅采用下列冻结含义，Value为非负整数，必需项不得省略：`axis-count`轴数、`max-axis-cardinality`单轴最大档数、`step-count`完整曝光步骤数、`channel-count`总光源设置数、`objective-count`必需目标数、`cell-count`全部矩阵格数、`repetition-count`全部格重复数之和、`candidate-count`实际候选数、`frontier-count`最终前沿规模、`evidence-ref-bytes`UTF8引用载荷字节、`event-payload-bytes`单事件最大序列化字节、`refinement-rounds`配置轮数、`proposal-batch-count`建议批次数。组合数由Plan.Request.Axes的基数BigInteger相乘得出（空轴BaselineOnly视为1），作为诊断字符串表示，不塞long或按已搜索数冒充总量。

测点：Validate（快照/身份/约束）、PreviewNext（首/续页、非法密集页）、向量聚合、Pareto更新、事件Append/Commit和分页Read、Run端到端（接纳至ResourcesReleased）、取消意图至真实排空/租约归还。独立报告计算与端口时间、样本n/P50/P95/P99、失败/超时/未知/删失类别及资源终态，未知排空不得判性能通过，不能只挑成功样本；具体数值只与同冻结Target比较。资源峰值分Core托管/native适配/原图/事件队列/store本次disk增量及在途计数，总额度按 §7。至少有稀疏合法空间、所有候选互不支配、全部等值、空前沿、不同维度、长引用与大矩阵、乱序回执及慢store负载，不能只测两轴/单候选理想情况。

实时曝光/温升/节拍由宿主另采纳Profile并做HIL；纯计算/模拟端口测量不代表设备吞吐。未创建Core工程、本次未运行基准或正式测试。

## 13. 可观测性

每次运行记录结构化日志：OperationId、状态转移、候选身份、轴量化、约束版本、观察或评价或证据引用、耗时、队列深度、取消原因和错误码。指标至少包括候选生成数、非法跳过数、观察成功或失败或未知数、评价缺项数、前沿大小、预算消耗和排空耗时。日志不写原图或敏感工单信息；证据通过调用方引用获取。

## 14. 第二消费者与接入顺序

第二消费者为独立视觉工程试验台：只接离线端口即可验证搜索、回放、Pareto 和报告导出，不引用 AOI 或钢网对象。AOI 或钢网适配器只能把本模块建议交给各自程序草稿或工程 Owner；本模块不写程序、不决定工艺阈值。接入顺序固定为：能力快照→参数空间验证→离线回放→模拟端口→真实设备 HIL→独立保留集→宿主审批和发布。

## 15. 参考来源与审核

设计输入包括 PKG-061_ImagingOptimization、DEV-VIS-020、DEV-VIS-021、独立模块架构及 Contract/Schema 治理指导；[`AsunControl` 只读快照](../../references/project-snapshots/AsunControl/20261004/original) 中的 ROI/NCC/图像控件资料仅作只读工程参考，不构成公共 API 或生产能力承诺。原始 PKG 和历史资料保持在快照目录，本页不复制其内容作为第二权威。

2026-10-06 来源复核：只读审阅 `H:\docs\40-development\41-vision-platform\02-acquisition\曝光光源自动优化开发指导.md` 全文（DEV-PLT-ACQ-005 v1.2，SHA-256 `9d414c085bcc1986077369ce69fa5990896ed6a2e3e3d2b008cd003eaba66cf9`），与[全量来源清单](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json) 一致；此前 REF-008 仅对旧版作定向审阅，本次不重复导入已覆盖的搜索、Pareto、取消和资源原则。采纳 §6.1–6.2/§6.5 的历史精确关联、逐曝光实际读回、去重/适用性/有界租约约束及 §7/§15 的预算边界，落入本文 §6.1、§12；保留可信低质量基线可改善与推荐门分离。§6.3 的指标提取与重复性计算仍属评价器 Owner，本模块只消费具名证据、不移植算法。排除 NPI/Recipe/HMI 接线、权限与签名策略、固定五通道和单位限制、三分钟/72小时/64MiB 数值、3D 产品范围、原项目状态/API/canonical/私有存储及末尾软件交付结果。生成段与正文关于 Bayesian、预算终态和置信区间的冲突不迁入。此为文档语义审查，未审源码、未重跑来源测试，也不代表平台实现或生产验收。

### 15.1 本轮官方与实际源码研究（2026-10-09）

- HALCON：直接读取项目`halcon算子手册/operators`中26.05.0.0官方原页：[intensity](../../../halcon算子手册/operators/intensity.html)、[gray_histo_abs](../../../halcon算子手册/operators/gray_histo_abs.html)、[min_max_gray](../../../halcon算子手册/operators/min_max_gray.html)、[entropy_gray](../../../halcon算子手册/operators/entropy_gray.html)、[area_center_gray](../../../halcon算子手册/operators/area_center_gray.html)、[deviation_image](../../../halcon算子手册/operators/deviation_image.html)、[sobel_amp](../../../halcon算子手册/operators/sobel_amp.html)、[threshold](../../../halcon算子手册/operators/threshold.html)、[get_domain](../../../halcon算子手册/operators/get_domain.html)、[reduce_domain](../../../halcon算子手册/operators/reduce_domain.html)、[intersection](../../../halcon算子手册/operators/intersection.html)、[crop_domain](../../../halcon算子手册/operators/crop_domain.html)、[erosion_rectangle1](../../../halcon算子手册/operators/erosion_rectangle1.html)、[full_domain](../../../halcon算子手册/operators/full_domain.html)、[area_center](../../../halcon算子手册/operators/area_center.html)。作者/版权MVTec，依赖固定AsunImage/HALCON26.05；资料使用现有项目原件，不复制算子实现。采纳忽略domain、类型/参数域、局部空间量、乘2、滤波域/halo/backend语义，具体落§16；纠正旧候选`deviation`名称，不猜未核实重载。算子文档不能证明本产品正确率、重复性或设备节拍。
- DevExpress：联网直接读25.2官方[DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)、[TableView](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TableView?v=25.2)、[PropertyGridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.PropertyGrid.PropertyGridControl?v=25.2)、[ChartControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Charts.ChartControl?v=25.2)，并定向核对本机`C:/Program Files/DevExpress 25.2/Components/Bin/Framework/`的Docking/Grid/Grid.Core/PropertyGrid/Charts/Core XML公开文档。依赖仍本机25.2.3的商业程序集，未下载/换补丁/检查授权。无dxdocs可调用时以这些官方及匹配本机资料绑定。采纳SelectedObject/PropertyDefinitions、TableView只读/逐像素滚动、Series绑定、Dock布局存取/关闭事件与SuperTip语义；未读示例源码/测试的网页自动例子不当实现证据。§9原PageContract内容接收保持，本轮补缺见§9.7～9.8；不把网页控件说明当1920×1080真实WPF/UIA资格。
- .NET：联网直接读[Cancellation in Managed Threads](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads)，微软官方概念资料；采纳cooperative取消/取消等待不同于native结束及CTS释放不归还设备资源，落§4/7。Core依赖.NET10 BCL，不因参考引入新包。
- Optuna：读取4.5.0 tag固定commit `d7e1c1b306b995aa53719ed6ab18e871ae0d52a5` 的实际[_multi_objective.py](https://github.com/optuna/optuna/blob/d7e1c1b306b995aa53719ed6ab18e871ae0d52a5/optuna/study/_multi_objective.py)、[test_multi_objective.py](https://github.com/optuna/optuna/blob/d7e1c1b306b995aa53719ed6ab18e871ae0d52a5/tests/study_tests/test_multi_objective.py)、[LICENSE](https://github.com/optuna/optuna/blob/d7e1c1b306b995aa53719ed6ab18e871ae0d52a5/LICENSE)和[pyproject.toml](https://github.com/optuna/optuna/blob/d7e1c1b306b995aa53719ed6ab18e871ae0d52a5/pyproject.toml)。MIT；Python>=3.8，公开依赖numpy/alembic/colorlog/packaging/sqlalchemy/tqdm/PyYAML，不引入C#Core。采纳严格支配、方向/维度一致、完成/可行性过滤、等向量不互相支配及穷举二维/重复/错误维度测试思想。限制：源允许Infinity、None归入Infinity，本模块明确拒绝非有限/缺项；源Trial完成不等于物理观察有效、独立、对账/native排空或扰动覆盖。二维lexsort/cumulative-min/多维实现仅性能候选；不搬Python实现、不引入NSGA/TPE/Bayesian，也不以README/stars/宣传证明生产能力。

本次研究复用既有来源，没有新增报告、资料副本或第三方依赖。技术可决定部分冻结在正文；设备读回/Owner/generation/CAS正式映射、物理能力/热功率、质量/ROI/独立组及客户验收值、模型Profile、WPF/Golden/HIL门只阻断各自适配切片。仍DesignReview/Prep，C1/C2/C3六门接收状态见附录A；A1-Q/A2-R确定指导内容已限定接收，U1的0.2.4指导内容接收保持，运行资格未关闭。

2026-10-12只针对§9.7现有CPU显示端口补核.NET10.0.12匹配参考包的官方XML：`Microsoft.WindowsDesktop.App.Ref/10.0.12/ref/net10.0/PresentationCore.xml`的BitmapSource.Create(Array,stride)/PixelFormats.Bgra32、`WindowsBase.xml`的Freezable.Freeze/Matrix.Transform及`PresentationFramework.xml`的Image/Canvas定位能力。调用采用Array重载、Freeze与同矩阵图像/ROI显示，不用未核实IntPtr/native显示桥；未下载依赖或新增算法研究。HALCON/DevExpress及固定Optuna证据继续复用§15.1，具体API消费编译与WPF行为仍未执行。

上游image-quality当前0.6.1-prep的§24.5明确保留§16完整端口/Root/Fixture/Stop、§24.3工厂及原算法路线；本模块继续消费已接收的0.6.0-prep服务合同与原量/支持映射，不复制其新增完整范围结论、WPF Viewer/保存Owner或方法建议实现。本文上游版本号标明接收基线，不把后续文档patch当新程序集或真实资格通过。

自审边界：Core无制程判定、质量放行和设备命令权；UI/模型仅投影或建议。文档走查不证明代码、HALCON、性能或生产验收；后续发现合同歧义先改此唯一指导，不让实现者补猜。

## 16. HALCON 26.05 评价实施卡（适配器，非 Core）

视觉适配只通过ImageLibDotNet.cv2使用算子，官方依据均为本项目HALCON26.05.0.0本地operator原页，见 §15。宿主Evaluator配置须带图像类型/位深、相机线性范围/黑位/饱和码、单通道映射、ROI坐标系/来源hash、最小有效面积、方法/参数/backend修订及质量阈值。未提供物理黑位/饱和值/有效域时，只可给工程灰度摘要，不能捏造饱和、噪声或可观测性资格。多通道先按获批映射选指定通道，禁止静默RGB转灰、uint2/real转byte。

### 16.1 固定处理顺序与有效 ROI

1. 先校验观察身份/逐曝光实际读回/租约及输入类型，取得原图Domain（get_domain）；ROI须已经由宿主变换到该图像像素坐标，不让Core猜坐标。逐ROI调用intersection(ROI,Domain)，Region2会先union，故不能把多个独立ROI当第二输入偷偷合并；再与有效像素区域交，借HALCON区域面积计算检查非空和最小面积。空域/过小立即Missing或NotObservable，不调用空统计算子、不依赖全局empty_region_result返回零，更不在模块改set_system。
2. 统计算子intensity、gray_histo_abs、min_max_gray、entropy_gray、area_center_gray忽略已有image domain，必须传显式有效交集region，不把reduce_domain单独视作足够ROI约束。reduce_domain只相交domain、不缩图像矩阵，不声称节省原图内存。各ROI独立记录原面积、有效面积、排除像素原因及来源引用。
3. 主路线先计算intensity均值/空间偏差、min_max_gray稳健范围、可支持类型的gray_histo_abs及阈值区域占比，再按已声明MethodRevision执行Sobel边缘/entropy等特征；每个所需目标取预先绑定方法，不在运行时看哪个分数好就切指标。暗/饱和区域通过threshold的冻结上下界，交有效ROI后计面积/有效ROI面积；int图阈值须已为整数（HALCON会truncate，模块先拒绝非整数），real阈值保留double且有限。传感器有效range来自Profile，不拿图像类型最大码冒充真实饱和码。
4. 空结果、类型不支持、阈值/参数不合法、native异常、资源预算或lease失效返回对应目标NotObservable/OutOfDomain/Invalid与诊断，解除本次对象；未知native保持对账而非返回空数组。Required目标不能被备用路线静默替换；只有目标定义同版本事先采纳的等价方法及同样本比较证据才允许切换，否则工程显示备用摘要但本候选不可推荐。

### 16.2 指标方法与限制

| 方法/适用输入 | 冻结参数与输出解释 | 失败或不能代表的事实 |
|---|---|---|
| intensity：官方支持图像类型，单ROI | 返回Mean、Deviation，记录原灰度单位；有效区逐ROI传入 | Deviation是空间灰度离散，不是重复采集噪声；单像素Deviation=0不证明无噪声 |
| min_max_gray：含real/int4/int8可走rank | Percent由方法Profile冻结，0..50；0为原极值，50为中位数，稳健范围=Max-Min | 不能把不同Percent混比或用低跨度证明可观测；忽略image domain |
| gray_histo_abs：byte/cyclic/direction/int1/int2/uint2 | Quantization>=1，由方法固定；bin解释按类型及官方有符号偏移，计数总和核对有效ROI面积 | 不支持real/int4；不能猜bin0为零灰度，不能暗中量化/转byte |
| entropy_gray：仅byte | 原8bit分布熵0..8bit，固定原数据与ROI | 不支持uint2/real；高熵可能来自噪声，不等于清晰/稳定；不能绕Required质量门 |
| sobel_amp→intensity：byte/int2/uint2/real | 本路线固定FilterType=`sum_abs`、Size=3，评价有效边界内幅值均值，单位为该原灰度尺度的Sobel幅值 | 5..13 Gaussian/5..39binomial有平滑与幅值缩放，改窗口需新MethodRevision，同数值不直接可比；弱边缘/噪声仍需独立目标 |
| deviation_image：byte/int2/uint2/int4/real，作为局部纹理诊断 | Width/Height由方法冻结，奇数>=3且各自<对应图像尺寸2倍；输出为局部空间标准差的2倍，解读时明确除2 | 不能叫时间噪声；HALCON会调整偶窗口但适配器先拒绝；镜像边界/ROI边界不可算真实观测 |
| area_center_gray：仅明确需要灰度质心的工程方法 | Area是灰度体积（像素灰度和），不是region像素面积；零体积拒绝位置，记录坐标变换 | 全零返回row/column=0不是真实质心；不用于无定义的“均匀度”或目标关联 |

滤波不能直接对不完整reduced domain取统计（官方警示unexpected results）。Sobel Size3需1像素halo；deviation_image按半窗口halo。宿主配置原有效域内的halo，使用HALCON区域erosion_rectangle1把统计ROI收缩到窗口完整位置；Width/Height取相应窗口且须奇数、1..511（超过该ROI保护路线能力时NotObservable，不静默改窗），缩后为空NotObservable。输入先full_domain取得完整矩阵定义域（不改尺寸/不把域外像素认作有效），滤波在该图像上运行，再只在窗口完全落在原有效像素内的该收缩ROI统计。允许crop_domain降低临时矩阵时，先保留包含halo的包围矩形及原row/column offset，输出ROI回原坐标，所有额外像素分配仍计预算；未验证非矩形/孔洞边界不得切crop路线。reduce_domain并不释放原矩阵。默认评价backend为固定CPU，不自动CPU/OpenCL切换；SIMD/线程配置写运行指纹，同样本比较正确性/误接收拒绝及P50/P95/P99/峰值后才能采纳其它backend。

### 16.3 退化、重复性及方法比较

饱和/暗部、遮挡、目标位置不可信、最小有效面积不足、信号低于方法可观测门，逐格拒识，不自动放宽阈值或用entropy代替真实目标。要求重复性/时间噪声时必须调用宿主已经冻结的独立重复采集评价方法及物理样本证据；上述单帧空间量都不能替代。未提供该方法/分组/阈值的Required目标返回NotObservable，只阻断该评价适配切片。Core消费数值/证据，不自行实现另一套视觉或计量算法。

主/备用/候选方法比较使用同一批准的代表集，至少涵盖正常、弱信号、饱和、遮挡、空ROI、不同位深、边界/孔洞、重复帧、扰动、资源超限；对比逐目标有效性/拒识、独立真值误接收拒绝、端到端分位/峰值和参数建议可复现性。更高“清晰度分数”本身不能证明更好检测，宿主目标/真值与Profile采纳后才冻结方案。此次只读官方资料、未跑真实cv2/Golden，不声称HALCON算法性能/准确率已通过。

### 16.4 A1-Q / A2-R：质量服务消费桥的唯一边界与公开装配

本节是既有A1/A2的可决定子范围，不新增独立模块。A1-Q消费[image-quality 0.6.0-prep §16.2–16.11](../image-quality/DEVELOPMENT-GUIDE.md#162-完整服务端口形状)的`QualityServiceSlice-02/Core+Simulator`，该上游六项规格已由主控接收；A2-R用冻结离线数据实现已有`IObservationPort`。下列确定指导内容已由主控限定接收；A1/A2整体仍`PreparationIncomplete`，不能借本次或上游接收提升真实适配/后端/产品资格，不标为无UI CoreReady。C1/C2/C3和U1既有接收保持。唯一依赖方向：本模块Adapters→本模块Core及image-quality.Core；本模块Core不反向引用质量服务。可选实际视觉由宿主注入image-quality.AsunImage的`ImageQualityAsunImageFactory.Create(clock, limits)`，内部仍仅`ImageLibDotNet.cv2`/HALCON26.05；本模块不再实现同一质量算法。§16.1–16.3保留为方法资格/旧路线适用说明；服务支持域、参数、输出键和数值规则以质量模块唯一正文为准，不用旧表覆盖它。

命名空间`Asun.Modules.ImagingOptimization.Adapters`、目标net10.0，无WPF/DevExpress/设备SDK/产品DTO。以下是**拟实施公开形状表**，不是已经编译的代码；所有上游类型直接引用`Asun.Modules.ImageQuality`，不复制同名类。一个Session绑定一个冻结OptimizationRequest/OperationId，最多一个评价调用在途；本片要求MaxConcurrentObservations=1，不猜服务并行能力。两个消费者是独立成像工程台和无UI步组回放Worker；实时设备Owner、读回、安全互锁、配置CAS和写入权仍由宿主持有，A2-R永不发设备命令。

```csharp
public enum ImagingEvidenceBasis { ProtocolFixture, RecordedInput }
public enum ImagingMetricSelector
{ RawLowFraction, RawHighFraction, RawContrast, RawCoverage, Scalar }
public sealed record ImagingReplayFrame(string RoleKey, FrameEvidence Evidence,
    QualityMemorySource Source);
public sealed record ImagingReplayEntry(string CandidateIdentityHash, string CellId,
    int RepetitionIndex, ImmutableArray<ExposureStep> ActualSettings,
    ImmutableArray<ImagingReplayFrame> Frames, ObservationUsage Usage,
    DateTimeOffset StartedUtc, DateTimeOffset CompletedUtc);
public sealed record ImagingReplayDataset(string DatasetId, string Revision,
    ImagingEvidenceBasis Basis, ImmutableArray<ImagingReplayEntry> Entries);
public sealed record ImagingMetricBinding(string ObjectiveId, string MethodKey,
    ImagingMetricSelector Selector, string? ScalarKey, string? RawMethodRevision,
    QualitySupportModel ExpectedSupportModel, long MinimumCenterPixels,
    double MinimumValidFraction);
public sealed record ImagingQualityCell(string CellId,
    ImmutableArray<QualityRegionSpec> Regions,
    ImmutableArray<QualityMethodPlan> Methods,
    ImmutableArray<ImagingMetricBinding> Metrics);
public sealed record ImagingQualityProfile(string Revision,
    int TileWidthPx, int TileHeightPx, ImmutableArray<ImagingQualityCell> Cells);
public sealed record ImagingAdapterOptions(int MaxReplayEntries, long MaxSourcePixels,
    int MaxRetainedEvaluations, long MaxRetainedBytes,
    DurationMs BindObservationLimit, DurationMs EvaluationObservationLimit,
    DurationMs CleanupObservationLimit, InputLimits InputLimits,
    QualityBudget QualityInstanceLimits);
public sealed record ImagingQualityCall(Guid RequestId, ObservationRequest Request,
    ObservationReceipt Receipt, ImmutableArray<QualityMemorySource> Sources,
    QualityServiceRequest QualityRequest, QualityBudget InstanceLimits);
public sealed record ImagingQualityEvidence(string ObservationId, string CellId,
    string DatasetRevision, ImagingEvidenceBasis Basis, Guid QualityRequestId,
    QualityOperationSnapshot Execution, QualityServiceReport? Report,
    Evaluation? Evaluation);
public sealed record ImagingAdapterSnapshot(bool BindingEnded, bool Closing,
    bool AllTasksEnded, bool ResourcesReleased,
    IReadOnlyList<string> PendingObservationIds, long RetainedBytes,
    string? BusinessDiagnosticId, string? CleanupDiagnosticId);
public sealed class ImagingAdapterSession
{
    // 只能由本节factory构造；Session是宿主进程强持的根对象。
    public Task? OriginalBinding { get; }
    public IObservationPort Observations { get; }
    public IEvaluationAdapter Evaluator { get; }
    public Task BindAsync(OptimizationRequest request, ImagingReplayDataset dataset,
        ImagingQualityProfile profile,
        Func<ImagingQualityCall, IQualityInputPort> inputFactory,
        Func<QualityBudget, IQualityVisualPort> visualFactory);
    public void ConfirmPlan(OptimizationPlan plan);
    public Task<Evaluation>? GetEvaluationTask(string observationId);
    public ImagingQualityEvidence? GetEvidence(string observationId);
    public ImagingAdapterSnapshot GetSnapshot();
    public ValueTask<DrainReceipt> CloseAsync(CancellationToken waitCancellation);
    public ValueTask<DrainReceipt> RecoverAsync(CancellationToken waitCancellation);
}
public static class ImagingAdapterFactory
{
    public static ImagingAdapterSession CreateSession(ImagingAdapterOptions options,
        TimeProvider clock);
}
```

所有集合非Default、不含null；边界取InputLimits与上游128字符约束较小者，枚举未知拒绝。Options数量/bytes/三个观察上限正有限，MaxRetainedEvaluations≤MaxReplayEntries，MaxSourcePixels为checked完整矩阵总像素上限；QualityInstanceLimits六项及最早期限沿上游，checked(2×ManagedBytes+NativeBytes+MaxOutputBytes+8192)及Session元数据预留不得超MaxRetainedBytes。任何上限不足在复制、factory、Open前拒绝IO-007，不截短报告/像素/分母。CreateSession只校验配置并建立有界表，不借图、不调用工厂、不Start；宿主在输入数组、profile及Bind构造前把返回Session附到进程Owner，构造失败无执行副作用。构造期覆盖入参、深快照和上游memory factory副本的同时存活峰值，不以ImmutableArray天然共享逃账。

BindAsync按上游§16.3/16.8纯结构参数规则预检请求/Profile/源、所选Required目标对应方法的Required标记（Raw还须对应内层Required）；不通过不得调用任何端口factory。BindAsync先登记原Task、request/profile/两个委托及逻辑容量，再在有界后台工作执行校验/深冻结。每Session仅一次绑定；同对象/同参数重复返回`OriginalBinding`同Task，不重复副本；异参数IO-012。BindAsync不接运行/等待token，返回真实OriginalBinding；调用方对它使用WaitAsync(waitToken)只结束观察，原Task不取消所有权；绑定尚未结束，Observations/Evaluator属性拒绝IO-017，绑定fault沿原Task读取保存。绑定不调用inputFactory/visualFactory，返回前不得启动HALCON。OriginalBinding实际未结束时Close仅记录停止意图并有限观察；迟到绑定完成只进入关闭态，不开放普通端口；绑定fault/无原生工作且原Task实际结束后立即按已保留纯值归还，不等待不存在的native。工厂委托必须纯构造或符合上游§16.10第三方构造Owner规则，不能在失败中遗失未返回native资源。调用方的WaitAsync是观察包装，`OriginalBinding`始终是真实绑定Task。Revision是纯读取：观察端口`io-replay-v0.1/<Dataset.Revision>`，评价端口`io-quality-v0.1/<Profile.Revision>`，两修订≤InputLimits且内容一变须新Revision；不能事后随当前latest变化。绑定request的预算/身份不可改，Validate生成Plan时仍以这两个Revision入PlanHash，Core codec全部不变。

### 16.5 A2-R：离线实际设置、来源与上游输入的逐字段桥

1. 数据集唯一键为`CandidateIdentityHash + CellId + RepetitionIndex + EncodeActualSettings(ActualSettings)`的完整字节；用hash加速仍核全字段。ObservationRequest.RequestedSettings须与该ActualSettings逐字段一致，包括全部步骤/通道/Enabled/Mode/SequenceIndex；Verification有Offsets时核**扰动后的**设置，不能仅核名义CandidateId。绑定核所有条目属于请求有限候选空间及现有格/重复范围；未被本次策略访问的合法条目可保留，绝不因此自动评价或借图。缺键是已知离线未覆盖，返回Rejected/IO-011、空Evidence/ActualSettings/空hash、零本次设备能量/null温度；不取最近帧/替代试件/补拍，仍按Core记该计划分母缺口。
2. 每条Frames恰覆盖ActualSettings全部StepId，至少每步一个具名角色，允许同一步多个已声明平面。FrameEvidence.StepId关联ActualSettings.StepId；Descriptor.StepIndex如有须等SequenceIndex，SourceId/Revision精确定位其QualityMemorySource。Descriptor的PlaneId/PixelType/WidthPx/HeightPx/CoordinateRevision、ParentRevision、ObservationGroupRevision、StepIndex、ExposureRevision、MotionRevision、ProjectionRevision、RadiometricRevision、AcquisitionUtc/ImportUtc、EffectiveBitDepth/BlackLevel/WhiteLevel完整保留；不从像素容器上限补白电平、不RGB转灰、不改Float32精度。源数据/有效mask恰等完整矩阵面积，QualityBox半开框已在该像素坐标中；ROI坐标变换由宿主在绑定前完成，不用Core猜转换。
3. 单帧统计可以使用ImportedFile且保留ImportUtc；需要实际采集/独立验证还须有原曝光读回、物理采集身份和分组来源证据。FrameEvidence.IndependenceGroup须等该ValidationCell组；PhysicalAcquisitionId保留原稳定来源/代次/触发关联，既不因当前OperationId重命名，也不由SourceId不同推导独立。Descriptor.ObservationGroupRevision表示原采集步组，**不是**统计IndependenceGroup，不将两者混用。Derived必须ParentRevision，不把派生图当独立采集。Basis=ProtocolFixture只是因果/编码夹具；Basis=RecordedInput表示消费冻结记录，仍不能自证当前设备适用、真实曝光合法或客户质量批准。
4. 源SourceRef相同但descriptor/像素/mask冲突，EvidenceId相同异内容、角色重复、步骤缺失、group/设置/时间冲突在Bind拒绝IO-018/012；格式坏IO-001。同源重复引用只保存一份深冻结矩阵，但计每个保留关联元数据；不同SourceRef不推测共享。RecordedInput的Evidence.ContentHash按来源拥有者冻结算法核原件，输入方完成该核验后才绑定；本片没有新原图codec或生产批准注册表。ProtocolFixture明确采用原UInt8行优先字节的SHA-256作为测试来源hash，不能外推其它位深的来源算法。
5. ObserveAsync快速登记原ObservationId/完整意图及输出额度，离线查询在本Session有界表完成，生成Accepted回执时只复制请求OperationId/ObservationId/CandidateId/CellId关联，保留原Frames.Evidence、实际Settings与原时间，ActualSettingsHash用现有codec。Usage是原记录能量/温度事实，本轮离线不发设备，但不能把原未知Usage改0来绕启用预算；预算能量/温度为null的夹具可明确Usage(null,null)。重复同意图回原receipt，不重复解析/统计；同ID异意图IO-012。ReconcileAsync仅读同ID账本；恢复进程可由Core传入的原耐久Intent及已ConfirmPlan的同一冻结数据重建原历史回执（保留原物理身份/时间，无Observe/设备/质量Start），并登记原ObservationId幂等结果。缺该键或缺原来源事实则Unknown保留原ID（空已知列表/空hash/CompletedUtc=null/Usage未知），不能补取latest。Drain无在途离线任务即可Drained/ResourcesReleased；纯值路径不能编造native未知。
6. A1-Q的inputFactory接收`ImagingQualityCall.Sources`，可直接传公开`ImageQualityMemoryInputFactory.Create(profile, sources, clock, call.InstanceLimits)`，每evaluation独立port；同SourceRef多角色交给上游只Open一次。替换为宿主真实IQualityInputPort时，Session给返回port加本方内部IQualityInputPort/IQualityReadScope转发保护（不新增公开DTO）。Open Descriptor须在任何ReadBlock/visual.Observe前逐字段匹配本次冻结绑定；匹配的scope原所有权不变，保护层每次CheckCurrent/ReadBlock前后核inner当前性及原Descriptor，漂移返回Changed/InvalidSource，不换源。若Open已经返回实际scope但Descriptor错，保护层先按OpenAttemptId登记该scope，再返回Scope=null/Issue=QS-InvalidSource/ResourcesReleased=false；CheckOpen合并原输入尝试和该scope.CheckDrain，Drained后CloseOpen按未完成阶段关闭该scope及inner.CloseOpen，成功阶段不重做，不能异常离栈丢实际scope。普通成功scope由service正常反序Close；保护层不额外再关它。ReadBlock仍保持二维原位置/mask/坐标。实际帧lease/文件当前性、断连及失败OpenAttempt归还由该端口原Owner证明；不能直接复用一次fixture的Current冒充真实源持续当前。

### 16.6 A1-Q：质量请求、支持域和ObjectiveValue精确消费

**调用和身份**：Evaluator只接本绑定OperationId/原ObservationId且精确匹配Session已登记的Accepted receipt，逐步核Candidate/Cell/实际设置/证据及PlanHash；Bind完成后宿主先用已绑定端口构造optimizer并Validate，再调用Session.ConfirmPlan(plan)；ConfirmPlan核现有codec完整PlanHash、冻结Request及两端口Revision一致，纯读取且仅同一Plan重复幂等，异Plan拒IO-012。Observe/Evaluate在ConfirmPlan前拒IO-017，之后PlanHash必须逐字匹配，不把首次不受信任请求当获批Plan。MetricBinding恰覆盖Cell.ObjectiveIds且ObjectiveId唯一；其MethodKey指QualityMethodPlan，方法Revision等对应MethodObjective.MethodRevision。Cell.Regions/Methods按冻结顺序构成QualityServiceRequest，Inputs按Frames.RoleKey声明顺序由各Descriptor.Source构造；Methods/RegionKey/RoleKey及Group/Color附加角色规则直接沿上游，不靠数组下标配帧。Session首次评价生成非空Guid RequestId并保存`ObservationId→QualityRequestId`，不是把字符串截取成Guid；恢复/重复只查原ID，不再Start。ApiVersion精确`image-quality-service-v0.1`。预算=min(上游instance、Session剩余、PortContext运行剩余、原Request.MaxStageTime剩余)，UTF8输入/行/块/halo/全部报告另计量；DeadlineUtc由clock本次剩余投影并取原最早期限，不用UTC回拨续期。

Session首次Observe/Evaluate先在PortContext.Quota预留本Session运行期根ResourceCharge（MemoryBytes=Options.MaxRetainedBytes、DiskBytes=0、SummaryItems=MaxRetainedEvaluations、EventItems=0），失败则零后续factory/工作；绑定期宿主进程容量和运行期配额两层约束，不用前者逃开Core总预算。后续input/visual factory前再在这个已预留根容量内划分质量调用/输入/报告额度，并预留对应QualityHostLifetimeRoot槽，不二次计同一parent reservation；上游剩余额度和本Session全部保留报告总额分别检查。槽归本Session强持，不归UI。Session内部质量根显式为`new QualityHostLifetimeRoot(clock, new QualityHostRootLimits(1, options.MaxRetainedBytes))`；每evaluation的SlotId=该QualityRequestId，Reserve的managed容量为checked(2×InstanceLimits.ManagedBytes+InstanceLimits.MaxOutputBytes+8192)，覆盖源捕获/构造双副本/报告与控制元数据，仍与本Session现有输入/报告总额共同检查MaxRetainedBytes，不能拿根预留与本Session两个账本互相漏计。`slot.ConstructAsync(() => inputFactory(call), () => visualFactory(call.InstanceLimits), call.InstanceLimits)`只启动原构造一次；`slot.Start(call.QualityRequest, executionToken)`后强持slot.Operation及slot.OriginalCompletion，ReferenceEquals原Operation.Completion必须成立。每Session一个评价在途，另一不同ID立即IO-016；同ID相同完整请求返回GetEvaluationTask原Task，false/fault/cancel后不重算；新评价须新意图，禁止复用失败ID。无质量槽/配额则factory次数0、IO-007；质量服务Start拒绝不造operation/完成报告。每次映射前核QualityRequestValidation、操作结果/快照、报告RequestId/版本/Sources/Inputs/Regions/Methods、RuntimeRevision及所有计数/单位（Sources按SourceRef集合核，不把报告Sources顺序猜成角色顺序；Inputs才是显式RoleKey关系）。RuntimeRevision由实际后端给出，在Session首次报告锁定；后续漂移IO-012，不接受宿主提供伪HALCON指纹。

| 选择器 / 上游唯一字段 | 输出值与精确Unit | 必须核验 / 拒识 |
|---|---|---|
| RawLowFraction / RawHighFraction | `QualityMetricObservation.RawValues`内`Kind=SaturationCount`的`ManagedSaturationValue.LowFraction/HighFraction`；Unit=`Fraction` | 精确MethodId=saturation-count、内层MethodRevision=绑定RawMethodRevision、参数与QualityRawParameters声明一致；LowCount/HighCount与原ValidPixels闭合。分母是有效原像素N，不改Requested/Center；原阈值不是自动物理饱和结论。 |
| RawContrast | 内层Kind=Contrast、`ManagedContrastValue.Value`；Unit=`GrayLevel` | Statistic、分位参数/Revision来自原方法，不能把总体空间标准差叫采集噪声/不确定度；不同灰度标尺不混比。 |
| RawCoverage | 内层Kind=ValidCoverage、`ManagedCoverageValue.ValidFraction`；Unit=`Fraction` | 原ValidPixels/RequestedPixels；Requested>0。全false mask允许0，但其它灰度目标不可因此Computed。 |
| Scalar | 该MethodKey的Values按ScalarKey唯一取值；Unit严格等对应`QualityValueUnit`名称 | route和已声明参数一致；仅允许下段封闭键，不取“第一值”。不存在、多键/错单位/NaN为畸形，不默填0。 |

Scalar封闭映射：Sobel/LoG/GaussianGradient/GaussianLaplace=`response`，按Aggregation单位KernelResponse或KernelResponseSquared；Noise=`sigma`/GrayLevel；LocalDeviation=`twiceLocalStdMean`/KernelResponse（不除2，不当噪声）；Uniformity=`mean/populationStd/worstAbsMeanOffset`/GrayLevel、`worstTileIndex`/Count；DirectionResponse=`xAbs/yAbs`/KernelResponse、`anisotropy`/Fraction；ColorBalance=`rFraction/gFraction/bFraction/referenceDistance`/Fraction（referenceDistance可至sqrt(2)，不是DeltaE）；StructuredGroupSupport=`presentSteps/requiredSteps`/Count、`commonValidFraction`/Fraction。无上游具名原量（例如entropy、时间噪声、真实ΔE、相位质量、计量不确定度）不能造selector/新Unit；本片对这样的Objective在Bind拒绝IO-010，另经领域Owner冻结适用方法才扩展。ScalarKey仅Scalar非null，RawMethodRevision仅Raw选择器非null；不允许自由表达式/权重/归一化或隐式单位换算。

**支持与状态**：每输出保留原Report/Support/RawValues/Tiles为GetEvidence审计消费者，不只摘数值丢分母。ExpectedSupportModel须等方法路线；Requested为原ROI面积、Valid为实际支持、Center为完整窗口中心，核0≤Center≤Valid≤Requested及Bounds/CoordinateRevision。binding.MinimumValidFraction在[0,1]，MinimumCenterPixels≥0；Coverage允许0，其它可观测量至少1或方法更高门。支持比例门用Valid/Requested，中心门用Center；原饱和比例用Valid，不重解释为中心数。Raw观察还核Domain.RequestedPixels/ValidPixels、RegionKey和Method参数；Sobel3 5×5全有效只有9个中心，不能填25。上游有效窗口/整矩形算子边界由QualitySupportModel明确，不能把OperatorRectangleBoundary当有完整真实halo。

Raw容器NotObservable/SubmetricUnavailable仍可能有合法完整RawValues，逐内层Computed映射；其它内层缺项原样留null，不能因外容器Computed省略逐原量检查。Scalar必须外Observation.State=Computed才映射。NotObservable→Value=null/NotObservable，Unsupported→Value=null/OutOfDomain；缺方法/缺键/错误Support属于不合法发布IO-010/018，停止该次评价，不把provider故障说成客观不可观测。合法支持门不足→NotObservable/原原因或SupportInsufficient；本桥防御核验见非有限值时IO-010/输出故障，不发布Evaluation，不把坏输出当合法不可观测项；同样不得进前沿。ValueValidity.Valid的EvidenceIds精确来自本回执实际依赖角色/步骤，Group/Color取全部依赖，ordinal去重；不能附别的cell/source。Complete只有Cell全部列值Valid且HardFailures空；质量上下限由Core §6.2比较，不把质量低分改缺项。上游Failed/Cancelled/TimedOut/资源未确认没有可发布报告：分别IO-010/013/009或IO-014，原错误与Snapshot.Causes保留；不能把Completion结束单独当质量有效。

### 16.7 原Task、独立cleanup、有限恢复与受限建议

Session是原Owner的根对象，宿主进程有界表须在Bind前登记它。根Quota reservation到本Operation的两个端口Drain共享同一Operation关闭账本，都确认无在途借读/执行、质量槽可忘后才归还一次（调用任一Drain即停止该Operation新增观察/评价，未决可继续Reconcile/Recover）；对应不可变数据/完成报告作为有界宿主历史DTO继续保留不算活借读，仍占Session.MaxRetainedBytes；端口Drain之后GetEvidence不重新Open，若消费方长期保存值则其宿主额度另计，Session.Close后清数据/委托，原报告DTO由宿主消费。不会让一个端口先Dispose根预留而另一个还在用。内部最多一个Bind、一个Evaluation、一个控制观察在途；已完成评价/原报告/receipt按MaxRetainedEvaluations和MaxRetainedBytes保留，到容量前拒绝下一evaluation，不驱逐尚被评价/对账依赖的事实。绑定数据、源、质量槽、原Construct/Completion及原Evaluation Task均可达；GetEvaluationTask/GetEvidence/GetSnapshot纯读取，不Open、不重算、不延长执行窗。日志只保留有限Code/ID，异常保留原Task并读取；同一生命周期业务诊断与cleanup诊断分别保存。Profile/数据变更只能新Session/OperationId，旧未决Session继续占进程额度，不能建新Session绕过同输入lease未归还。

评价工作包含正常映射和同slot的独立finally清理。executionToken只请求质量operation取消；**cleanup用显式CleanupObservationLimit及CancellationToken.None，不能链接已取消的运行token**。正常/失败/取消都调用slot.CloseAsync(QualityStopWaitBudget(剩余清理窗,clock对应UTC最早期限), None)，原观察Task也登记。Session.Close与评价finally共享同slot的ActiveCloseObservation，未结束就只等待它，不并发再调Close；该有限观察已结束false/fault才允许后续显式Recover查询当前账本。先确认operation真实Drained/ResourcesReleased、原Completion实际结束，再确认slot.Close为Released和原construction结束；root.TryForget(slotId)才归还质量槽。成功完成报告可摘出为深冻结DTO，但质量服务关闭未确认不能发布成功Evaluation。首次释放失败后，显式slot.RecoverAsync可回收资源，原operation仍Failed/QS-ReleaseFailed，不能追补成功评价。普通纯值端口无后台时立即真实Drained，不编native待定。

评价观察/cleanup到期仅IO-014并保留原槽、原Evaluation Task/报告或故障、Quota reservation。原评价Task已fault但真实质量工作未结束的情况也保持PendingObservationIds；Session.Evaluator.DrainAsync/Session.CloseAsync返回Drained=false/ResourcesReleased=false和原未决ID。后续Session.RecoverAsync在单控制槽内对同slot显式Recover，旧有限观察false/fault已结束可重新观察当前原账本；不新Construct/Start/Evaluate、不重复已成功Close阶段。挂起原construction/native/Close未结束时不能启动第二释放Task。恢复资源后可Drained=true，但原业务错误保留、GetEvidence不从null变成功Evaluation、Core按既有Recover保守终态。观察token取消仅停止这次等待。Close先拒绝新Observe/Evaluate/Bind，再有限等待/关闭已登记槽；只有原Task真结束、所有质量scope/invocation释放、根TryForget成功及无活资源，才ResourcesReleased=true。Session解除数据/委托强引用可在此后，已完成GetEvidence的值DTO归宿主有限消费；未决时无GC/Dispose伪确认，无无限定时重试。构造失败/尚无Plan同样使用Options.CleanupObservationLimit，不等待不存在的Plan预算。

两个建议范围严格分开：质量模块§17的方法实验网格仅生成原量对照或由有真实任务标签的工程宿主选方法；上游没有公开QualitySuggestion类型，本模块不预造。宿主选定方法后冻结新QualityMethodPlan.Revision、ImagingQualityProfile.Revision及MethodObjective.MethodRevision，才建**新的**OptimizationRequest；不能在同一候选搜索中选更好看的Sobel/Noise参数。物理曝光/增益/光源候选只由Core原Capability/AllowedValues、约束和§6有限策略产生；质量分数没有设备写权，不将饱和比例反推连续曝光/擅改档位/扩轴。需要建议候选时仍用已接收C3的ICandidateProposalPort，完整Candidate须经原量化/hash/约束/预算；Proposal不得读取Verification数据选候选。无标签、方法资格或生产Profile时，质量对照和候选均仅工程/ProtocolFixture，不能声称推荐通过。

**完整分母到独立验证**：每名义候选的Search/Verification计划分别按原Cells×Repetitions及其ObjectiveIds枚举；预算失败/缺回放条目/重复物理帧/Required不可观测/失败格均保留缺口，不从计划删除。质量像素支持分母与独立物理样本分母是两层，像素数/调用数/SourceId数不能增加独立Repetitions。每一次Evaluation事件耐久后才能参与Search最坏向量；不平均ROI或借Verification替Search补洞。VerifyCandidateIds只从原合格前沿选择，验证只覆盖原独立组和扰动格，所有必需格/重复及排空/最终Commit完整才按Core原规则投影IndependentlyVerified；这个Core标签不等于客户质量放行。Basis=ProtocolFixture时Host必须同时显示/记录“协议夹具 / 協定測試 / Protocol fixture”；RecordedInput是历史记录评价，原曝光/方法/设备/客户资格及当前采用授权另验。本桥不新增生产事实/推荐批准DTO。

### 16.8 两个空Host、完整输入与正常→取消→恢复

下面是唯一Adapters.Tests内的**拟实施C#示例**（依本节公开API，未编译/运行）。仅引用本模块Adapters/Core、image-quality.Core和BCL；QualityMemoryInputFactory/ManagedVisualFactory是真实拟发布入口，不引用上游.Tests DLL。两个入口分别建立全部字段/独立数据及Session，Host A单帧工程台、Host B三步组Worker；共用的Build方法全部在本节。两者的Constraint/Store从§10本指导已给出的完整`ReplayConstraint`/`ReplayStore`声明原样复用至本Adapters.Tests的`QualityBridgeFixtures.cs`（唯一测试工程内的真实夹具消费者；不引Core.Tests程序集、不复制Program/Main）；不是从含Main的源文件选择性编译类。固定`ReplayStore(false,false)`只具进程内耐久，其旧HasExpectedFrontier专供§10原Golden，本桥使用本节新向量断言。正式工具仅引用发布DLL，由各宿主自己的IConstraintPolicy/IResultStore代替，不携测试私类/私表入模块。这里不新增产品存储factory，实际耐久store仍A2后续门。

本示例的Program串行调用同case的Run及后续显式CleanupHost，不重入清理。两个Close先分别登记并启动，再同时开始各自有限观察；未结束原Task不二次调用factory，已完成的失败观察才允许同Owner恢复。首cleanup错误与饱和计数独立于BusinessError；Released须所有原业务/控制任务真实结束、Core.Dispose正常成功及Session快照资源归还同时成立，失败Task的IsCompleted只表示执行结束。释放未确认时保留Owner，清理成功也不追补业务成功或推荐。

```csharp
using System.Collections.Immutable;
using System.Security.Cryptography;
using Asun.Modules.ImageQuality;
using Asun.Modules.ImagingOptimization;
using Asun.Modules.ImagingOptimization.Adapters;

internal sealed record BridgeInput(OptimizationRequest Request,
    ImagingReplayDataset Dataset, ImagingQualityProfile Profile);
internal sealed class BridgeCase
{
    // Program的容量=2的进程Owner表在Run之前强持BridgeCase；未归还不能移除。
    public readonly List<BridgeCall> Originals = new(8);
    public readonly TaskCompletionSource<GateVisual> GateReady =
        new(TaskCreationOptions.RunContinuationsAsynchronously);
    public ImagingAdapterSession? Session;
    public ImagingOptimizer? Optimizer;
    public ReplayStore? Store;
    public GateVisual? Gate;
    public Exception? BusinessError, CleanupError;
    public int CleanupErrorCount;
    public CancellationTokenSource? Execution;
    // 五个控制条目随进程Owner预留，不与普通Originals容量竞争。
    public readonly BridgeCall CoreClose = new(), CoreRecovery = new(),
        SessionClose = new(), SessionRecovery = new(), CoreDispose = new();
    public void RecordCleanup(Exception error)
    {
        CleanupError ??= error; // 常量空间：首错误+饱和计数，不能改BusinessError。
        if(CleanupErrorCount<int.MaxValue) CleanupErrorCount++;
    }
    public OptimizationResult? Result;
    public string? OperationId;
    public bool Released;
    public Task<T> Start<T>(Func<ValueTask<T>> factory)
    {
        if (Originals.Count == 8) throw new InvalidOperationException("host-capacity");
        var call = new BridgeCall(); Originals.Add(call); // factory前登记Starting。
        return call.Begin(factory, false);
    }
    public Task StartDispose(Func<ValueTask> factory)
    {
        if (Originals.Count == 8) throw new InvalidOperationException("host-capacity");
        var call = new BridgeCall(); Originals.Add(call);
        return call.Begin(factory, false);
    }
}
internal sealed class BridgeCall
{
    public Task? Original;
    public Exception? FactoryError;
    public bool SynchronouslyEnded, Attempted, Starting;
    public bool Ended => !Starting && (!Attempted || SynchronouslyEnded || Original?.IsCompleted==true);
    public Task<T> Begin<T>(Func<ValueTask<T>> factory, bool renewCompletedObservation)
    {
        if(Original is not null && (!renewCompletedObservation || !Original.IsCompleted))
            return (Task<T>)Original; // 未结束原Task复用，不再调用factory。
        Prepare(renewCompletedObservation);
        try { var task=factory().AsTask(); Original=task; return task; }
        catch(Exception ex) { FactoryError=ex; SynchronouslyEnded=true; throw; }
        finally { Starting=false; }
    }
    public Task Begin(Func<ValueTask> factory, bool renewCompletedObservation)
    {
        if(Original is not null && (!renewCompletedObservation || !Original.IsCompleted)) return Original;
        Prepare(renewCompletedObservation);
        try { var task=factory().AsTask(); Original=task; return task; }
        catch(Exception ex) { FactoryError=ex; SynchronouslyEnded=true; throw; }
        finally { Starting=false; }
    }
    private void Prepare(bool renewCompletedObservation)
    {
        if(Starting) throw new InvalidOperationException("control-starting");
        if(Attempted && !renewCompletedObservation)
            throw new InvalidOperationException("original-factory-failed",FactoryError);
        if(Original?.IsFaulted==true) _=Original.Exception; // 仅退休已结束的观察；组件原Owner仍强持真实工作。
        Original=null; FactoryError=null; SynchronouslyEnded=false;
        Attempted=true; Starting=true; // 在任何factory之前登记。
    }
}
internal static class QualityBridgeHosts
{
    public static Task RunA(BridgeCase owner, bool gated, CancellationToken token) =>
        Run(owner, false, gated, token);
    public static Task RunB(BridgeCase owner, bool gated, CancellationToken token) =>
        Run(owner, true, gated, token);

    private static async Task Run(BridgeCase owner, bool group, bool gated,
        CancellationToken token)
    {
        try
        {
            // 参数/时钟/执行CTS创建也在业务保护内；失败仍执行下方独立清理。
            var clock = TimeProvider.System;
            var limits = new InputLimits(1024, 256, 1000000);
            var quality = new QualityBudget(16L<<20, 1L<<20, 1000000,
                2L<<20, TimeSpan.FromSeconds(20), clock.GetUtcNow().AddSeconds(60));
            var options = new ImagingAdapterOptions(5, 60, 5, 64L<<20,
                new(2000), new(5000), new(2000), limits, quality);
            owner.Execution = CancellationTokenSource.CreateLinkedTokenSource(token);
            owner.Session = ImagingAdapterFactory.CreateSession(options, clock);
            var f = Build(group, clock); // Session已附根，再分配输入/方法/像素。
            owner.OperationId=f.Request.OperationId;
            IQualityInputPort Input(ImagingQualityCall call) =>
                ImageQualityMemoryInputFactory.Create(
                    new(group ? "bridge-b" : "bridge-a", "fixture-r1", 3, 1L<<20),
                    call.Sources, clock, call.InstanceLimits);
            IQualityVisualPort Visual(QualityBudget budget)
            {
                var inner = ImageQualityManagedVisualFactory.Create(
                    new("bridge-managed", "fixture-r1", 256, 3), clock, budget);
                if (!gated) return inner;
                var gate = new GateVisual(inner); owner.Gate = gate;
                if (!owner.GateReady.TrySetResult(gate)) throw new InvalidOperationException("gate-recreated");
                return gate;
            }
            var binding = owner.Session.BindAsync(f.Request, f.Dataset, f.Profile,
                Input, Visual);
            if (!ReferenceEquals(binding, owner.Session.OriginalBinding))
                throw new InvalidOperationException("binding-task");
            await binding.WaitAsync(TimeSpan.FromSeconds(2), clock, token);
            owner.Store = new ReplayStore(false,false); // 构造后立即附进程根。
            owner.Optimizer = new ImagingOptimizer(new(new ReplayConstraint(),
                owner.Session.Observations, owner.Session.Evaluator,
                owner.Store, null),
                new(8,2,1,new(1000),2,1L<<20,new(2000),limits));
            var check = owner.Optimizer.Validate(f.Request);
            if (!check.IsValid || check.Plan is null) throw new InvalidOperationException("plan");
            owner.Session.ConfirmPlan(check.Plan);
            var run = owner.Start(() => owner.Optimizer.RunAsync(check.Plan,null,owner.Execution.Token));
            if (gated)
            {
                // Gate已由Session slot.Construct构造；有界等Enter，不靠任意Delay碰运气。
                await WaitGateEntered(owner, clock, token);
                owner.Execution.Cancel();
                var held = await owner.SessionClose.Begin(
                    () => owner.Session.CloseAsync(CancellationToken.None), false);
                if (held.ResourcesReleased || owner.Session.GetSnapshot().PendingObservationIds.Count == 0)
                    throw new InvalidOperationException("early-release");
                owner.Gate!.Release(); // 结束测试原同步Observe，绝非再采集。
            }
            owner.Result = await run.WaitAsync(TimeSpan.FromSeconds(10), clock, token);
            if (!gated && (!owner.Result.SearchComplete ||
                owner.Result.Recommendation.State != RecommendationState.IndependentlyVerified))
                throw new InvalidOperationException("frontier-or-denominator");
            if (gated && owner.Result.Recommendation.State == RecommendationState.IndependentlyVerified)
                throw new InvalidOperationException("cancelled-recommendation");
            if (!gated)
            {
                double[] expectedContrast=[254,190,100,140,190];
                double[] expectedHigh=[.25,0,.25,0,0];
                for(int n=0;n<5;n++)
                {
                    var row=owner.Session.GetEvidence(f.Request.OperationId+"/"+n)
                        ?? throw new InvalidOperationException("denominator-gap");
                    var values=row.Evaluation?.Values ?? throw new InvalidOperationException("missing-evaluation");
                    if(values.Single(x=>x.ObjectiveId=="contrast").Value!=expectedContrast[n] ||
                        values.Single(x=>x.ObjectiveId=="sat").Value!=expectedHigh[n] ||
                        !row.Evaluation!.Complete || row.Report!.Observations.Single(x=>x.MethodKey=="raw").Support.ValidPixels!=4)
                        throw new InvalidOperationException("raw-vector");
                    if(group && values.Single(x=>x.ObjectiveId=="group").Value!=.75)
                        throw new InvalidOperationException("group-denominator");
                }
                if(owner.Result.Recommendation.Candidates.Count!=1 ||
                    owner.Result.Recommendation.Candidates[0].CandidateId!=f.Request.Validation.VerifyCandidateIds[0])
                    throw new InvalidOperationException("selected-candidate");
                var evidence = owner.Session.GetEvidence(f.Request.OperationId+"/0")
                    ?? throw new InvalidOperationException("missing-report");
                if (evidence.Basis != ImagingEvidenceBasis.ProtocolFixture ||
                    evidence.Report is null || evidence.Evaluation!.Values.Single(x=>x.ObjectiveId=="sat").Value != .25)
                    throw new InvalidOperationException("origin-or-value");
            }
        }
        catch (Exception ex) { owner.BusinessError ??= ex; }
        finally
        {
            try { await CleanupHost(owner); }
            catch(Exception ex) { owner.RecordCleanup(ex); } // 最后保护不覆盖原业务错误。
        }
        // Program核原业务结果、CleanupErrorCount和Released；清理成功不追补业务/推荐。
        // 未确认保持同BridgeCase/Session/Optimizer/Execution，下一次显式CleanupHost仍复用在途原Task。
    }
    private static void CleanupStep(BridgeCase owner, Action action)
    {
        try { action(); } catch(Exception ex) { owner.RecordCleanup(ex); }
    }
    private static TimeSpan Remaining(long start)
    {
        var left=TimeSpan.FromSeconds(2)-System.Diagnostics.Stopwatch.GetElapsedTime(start);
        return left>TimeSpan.Zero?left:TimeSpan.Zero;
    }
    private static async Task<T?> ObserveControl<T>(BridgeCase owner, Task<T>? original,
        long start) where T:class
    {
        if(original is null) return null;
        try
        {
            // 完成状态只决定能否零等待读取；fault/cancel会被await读出，绝不当释放证明。
            if(original.IsCompleted) return await original.ConfigureAwait(false);
            var left=Remaining(start);
            if(left==TimeSpan.Zero) throw new TimeoutException("cleanup-observation-expired");
            return await original.WaitAsync(left,CancellationToken.None).ConfigureAwait(false);
        }
        catch(Exception ex) { owner.RecordCleanup(ex); return null; }
    }
    private static bool Released(DrainReceipt? receipt) => receipt is not null &&
        receipt.Drained && receipt.ResourcesReleased && receipt.UnresolvedIds.Count==0;
    private static async Task<bool> ObserveCoreCleanup(BridgeCase owner, long start)
    {
        if(owner.Optimizer is null) return true; // 仅指从未构造Core。
        try
        {
            var closed=await ObserveControl(owner,owner.CoreClose.Original as Task<DrainReceipt>,start);
            if(Released(closed)) return true;
            // 原Close尚未结束只保留；同组件不并行启动第二控制释放。
            if(!owner.CoreClose.Ended) return false;
            if(owner.CoreRecovery.Original is Task<OptimizationResult> previous)
            {
                var known=await ObserveControl(owner,previous,start);
                if(known is not null && known.ResourcesReleased &&
                    known.State!=OptimizationRunState.ReconcileRequired) return true;
                if(!owner.CoreRecovery.Ended) return false;
            }
            if(Remaining(start)==TimeSpan.Zero) return false;
            var recovery=owner.CoreRecovery.Begin(() => owner.Optimizer.RecoverAsync(
                owner.OperationId ?? throw new InvalidOperationException("original-operation-id-missing"),null,CancellationToken.None),true);
            var result=await ObserveControl(owner,recovery,start);
            return result is not null && result.ResourcesReleased &&
                result.State!=OptimizationRunState.ReconcileRequired;
        }
        catch(Exception ex) { owner.RecordCleanup(ex); return false; }
    }
    private static async Task<bool> ObserveSessionCleanup(BridgeCase owner, long start)
    {
        if(owner.Session is null) return true;
        try
        {
            var closed=await ObserveControl(owner,owner.SessionClose.Original as Task<DrainReceipt>,start);
            if(Released(closed)) return true;
            if(!owner.SessionClose.Ended) return false;
            if(owner.SessionRecovery.Original is Task<DrainReceipt> previous)
            {
                if(Released(await ObserveControl(owner,previous,start))) return true;
                if(!owner.SessionRecovery.Ended) return false;
            }
            if(Remaining(start)==TimeSpan.Zero) return false;
            var recovery=owner.SessionRecovery.Begin(
                () => owner.Session.RecoverAsync(CancellationToken.None),true);
            return Released(await ObserveControl(owner,recovery,start));
        }
        catch(Exception ex) { owner.RecordCleanup(ex); return false; }
    }
    private static IEnumerable<BridgeCall> Calls(BridgeCase owner) => owner.Originals.Concat(
        new[]{owner.CoreClose,owner.CoreRecovery,owner.SessionClose,owner.SessionRecovery,owner.CoreDispose});
    internal static async Task CleanupHost(BridgeCase owner)
    {
        owner.Released=false;
        // Gate、Cancel及每个Close各自保护；任何参数/注册异常不跳过另一组件。
        CleanupStep(owner,() => owner.Gate?.Release());
        CleanupStep(owner,() => owner.Execution?.Cancel());
        var coreStart=System.Diagnostics.Stopwatch.GetTimestamp();
        CleanupStep(owner,() => {
            if(owner.Optimizer is not null)
                owner.CoreClose.Begin(() => owner.Optimizer.CloseAsync(CancellationToken.None),false);
        });
        var sessionStart=System.Diagnostics.Stopwatch.GetTimestamp();
        CleanupStep(owner,() => {
            if(owner.Session is not null)
                owner.SessionClose.Begin(() => owner.Session.CloseAsync(CancellationToken.None),false);
        }); // 两个安全停止意图/原Task均已登记，之后才观察；不以Core的异常阻断Session.Close。
        var coreObservation=ObserveCoreCleanup(owner,coreStart);
        var sessionObservation=ObserveSessionCleanup(owner,sessionStart);
        var coreReleased=await coreObservation.ConfigureAwait(false);
        var sessionReleased=await sessionObservation.ConfigureAwait(false);
        // 不建cleanup CTS：两个组件各用自起点2秒单调窗；WaitAsync只观察、原控制任务仍由条目强持。
        bool originalsEnded=true;
        try
        {
            foreach(var call in owner.Originals)
            {
                if(!call.Ended) { originalsEnded=false; continue; }
                if(call.Original is not null)
                    try { await call.Original.ConfigureAwait(false); }
                    catch(Exception ex) { owner.BusinessError ??= ex; }
                else if(call.FactoryError is not null) owner.BusinessError ??= call.FactoryError;
            }
        }
        catch(Exception ex) { originalsEnded=false; owner.RecordCleanup(ex); }
        bool sessionSnapshotReleased=owner.Session is null;
        CleanupStep(owner,() => {
            if(owner.Session is not null)
            {
                var snapshot=owner.Session.GetSnapshot();
                sessionSnapshotReleased=snapshot.AllTasksEnded && snapshot.ResourcesReleased &&
                    snapshot.PendingObservationIds.Count==0;
            }
        });
        bool coreDisposed=owner.Optimizer is null;
        bool controlsEnded=false;
        CleanupStep(owner,() => controlsEnded=owner.CoreClose.Ended && owner.CoreRecovery.Ended &&
            owner.SessionClose.Ended && owner.SessionRecovery.Ended);
        // Dispose依赖原业务及其它控制任务结束、两组件资源确认；未满足只保根。
        if(originalsEnded && controlsEnded && coreReleased && sessionReleased && sessionSnapshotReleased && owner.Optimizer is not null)
        {
            try
            {
                var original=owner.CoreDispose.Original;
                if(original is not null && original.IsCompleted && !original.IsCompletedSuccessfully)
                {
                    try { await original.ConfigureAwait(false); }
                    catch(Exception ex) { owner.RecordCleanup(ex); } // 退休失败观察前读取迟到fault/cancel。
                }
                if(original?.IsCompletedSuccessfully!=true)
                    original=owner.CoreDispose.Begin(() => owner.Optimizer.DisposeAsync(),true);
                if(!original.IsCompleted)
                {
                    var left=Remaining(coreStart);
                    if(left==TimeSpan.Zero) throw new TimeoutException("dispose-observation-expired");
                    await original.WaitAsync(left,CancellationToken.None).ConfigureAwait(false);
                }
                else await original.ConfigureAwait(false); // fault/cancel记录；必须正常返回。
                coreDisposed=original.IsCompletedSuccessfully;
            }
            catch(Exception ex) { owner.RecordCleanup(ex); }
        }
        bool allEnded=false;
        CleanupStep(owner,() => allEnded=Calls(owner).All(call=>call.Ended));
        if(originalsEnded && allEnded && coreReleased && coreDisposed && sessionReleased && sessionSnapshotReleased)
        {
            bool localReleased=true;
            try { owner.Gate?.DisposeConfirmed(); } catch(Exception ex) { localReleased=false; owner.RecordCleanup(ex); }
            try { owner.Store?.ClearConfirmed(); } catch(Exception ex) { localReleased=false; owner.RecordCleanup(ex); }
            try { owner.Execution?.Dispose(); } catch(Exception ex) { localReleased=false; owner.RecordCleanup(ex); }
            owner.Released=localReleased; // 任一未知/Dispose fault不能靠IsCompleted抬成true。
        }
    }
    private static async Task WaitGateEntered(BridgeCase owner, TimeProvider clock,
        CancellationToken token)
    {
        var start = clock.GetTimestamp();
        var gate = await owner.GateReady.Task.WaitAsync(TimeSpan.FromSeconds(5),clock,token);
        var remaining = TimeSpan.FromSeconds(5)-clock.GetElapsedTime(start);
        if(remaining<=TimeSpan.Zero) throw new TimeoutException();
        await gate.Entered.WaitAsync(remaining,clock,token);
    }
    private static BridgeInput Build(bool group, TimeProvider clock)
    {
        var budget = new Budget(5,4,new(30000),new(10000),new(2000),null,null,
            1,1000,100,128L<<20,10000000);
        var limits = new InputLimits(1024,256,1000000);
        var x = new AxisTarget("s0",AxisKind.Exposure,null);
        var g = new AxisTarget("s0",AxisKind.Gain,null);
        var caps = new List<AxisCapability>();
        var count = group ? 3 : 1;
        for(int i=0;i<count;i++)
        {
            var step="s"+i;
            caps.Add(new(new(step,AxisKind.Exposure,null),"us",i==0?[100m,200m]:[100m],null,"fixture-ticks"));
            caps.Add(new(new(step,AxisKind.Gain,null),"dB",i==0?[0m,1m]:[0m],null,"fixture-ticks"));
            caps.Add(new(new(step,AxisKind.LightLevel,"l0"),"NativeCode",[1m],null,"fixture-ticks"));
            caps.Add(new(new(step,AxisKind.LightEnabled,"l0"),"bool",[1m],null,"fixture-ticks"));
        }
        var cap=ImagingContractCodec.SealCapability(new("cap-v1","",caps,1),budget,limits);
        Candidate At(long e,decimal gain) => ImagingContractCodec.CreateCandidate("space-v1","constraint-v1",
            Enumerable.Range(0,count).Select(i=>new ExposureStep("s"+i,new(i==0?e:100),new(i==0?gain:0),
                [new("l0",new(1m,LightLevelUnit.NativeCode),true)],"normal",i)).ToArray(),budget,limits);
        Candidate[] candidates=[At(100,0),At(100,1),At(200,0),At(200,1)];
        var objectives=new List<MethodObjective> {
            new("contrast","target","quality",ObjectiveDirection.Maximize,"GrayLevel",true,null,null,"method-r1"),
            new("sat","target","quality",ObjectiveDirection.Minimize,"Fraction",true,null,null,"method-r1") };
        if(group) objectives.Add(new("group","target","quality",ObjectiveDirection.Maximize,"Fraction",true,.75,null,"method-r1"));
        var ids=objectives.Select(o=>o.ObjectiveId).ToArray();
        var cells=new[] {
            new ValidationCell("search","target","quality","fixture-search","nominal","search",ObservationPhase.Search,1,ids,[]),
            new ValidationCell("verify","target","quality","fixture-holdout","nominal","holdout",ObservationPhase.Verification,1,ids,[]) };
        var validation=ImagingContractCodec.SealValidation(new("validation-r1","",cells,[candidates[1].CandidateId]),budget,limits);
        var request=new OptimizationRequest(group?"bridge-b":"bridge-a","protocol-fixture","0.2","space-v1",cap,
            new("constraint-v1",new string('a',64),"fixture-rule"),
            [new("exposure",x,"us",[100m,200m],false,"cap-v1"),new("gain",g,"dB",[0m,1m],false,"cap-v1")],
            candidates[0],objectives,validation,budget,SearchPolicy.DeterministicMixedRadix,new("search-r1",[],0,null),
            group?"dataset-b-r1":"dataset-a-r1",[group?"dataset-b":"dataset-a"]);
        double[][] pixels=[[0,100,254,255],[10,100,200,250],[0,50,100,255],[10,80,150,250],[20,110,210,250]];
        var entries=ImmutableArray.CreateBuilder<ImagingReplayEntry>();
        var now=clock.GetUtcNow();
        for(int n=0;n<5;n++)
        {
            var candidate=candidates[n==4?1:n]; var cell=cells[n==4?1:0];
            var frames=ImmutableArray.CreateBuilder<ImagingReplayFrame>();
            for(int i=0;i<count;i++)
            {
                var sourceId=(group?"b":"a")+"-capture-"+n+"-step-"+i;
                var source=new QualitySourceRef(sourceId,"source-r1");
                var descriptor=new QualitySourceDescriptor(source,QualitySourceKind.RawAcquisition,"gray",
                    QualityPixelType.UInt8,4,1,"pixel-r1",null,"capture-"+n,i,"readback-"+n,
                    "motion-r1","projection-r1",null,now,null,8,null,null);
                var hash=Convert.ToHexString(SHA256.HashData(pixels[n].Select(v=>(byte)v).ToArray())).ToLowerInvariant();
                frames.Add(new("step-"+i,new(sourceId,sourceId,cell.IndependenceGroup,"s"+i,sourceId,hash),
                    new(descriptor,pixels[n].ToImmutableArray(),
                        (group&&i==1?new[]{true,true,true,false}:new[]{true,true,true,true}).ToImmutableArray())));
            }
            entries.Add(new(candidate.IdentityHash,cell.CellId,0,candidate.Steps.ToImmutableArray(),frames.ToImmutable(),
                new(null,null),now,now));
        }
        var plans=ImmutableArray.CreateBuilder<QualityMethodPlan>();
        var raw=new ManagedQualityMethodSet(ImmutableArray.Create<ManagedQualityMethod>(
            new ManagedSaturationMethod("raw-r1",0,255),
            new ManagedContrastMethod("raw-r1",ManagedContrastStatistic.NearestRankQuantileRange,.25,.75)),
            ImmutableArray.Create<ManagedQualityMethod>(new ManagedCoverageMethod("raw-r1")));
        plans.Add(new("raw","method-r1","roi","step-0",QualityRoute.RawStatistics,new QualityRawParameters(raw),
            new(1,0,null,null,null),true));
        var bindings=ImmutableArray.CreateBuilder<ImagingMetricBinding>();
        bindings.Add(new("contrast","raw",ImagingMetricSelector.RawContrast,null,"raw-r1",QualitySupportModel.OriginalPixels,1,1));
        bindings.Add(new("sat","raw",ImagingMetricSelector.RawHighFraction,null,"raw-r1",QualitySupportModel.OriginalPixels,1,1));
        if(group)
        {
            plans.Add(new("support","method-r1","roi","step-0",QualityRoute.StructuredGroupSupport,
                new QualityGroupParameters(ImmutableArray.Create("step-0","step-1","step-2"),ImmutableArray.Create(0,1,2)),
                new(1,.75,null,null,null),true));
            bindings.Add(new("group","support",ImagingMetricSelector.Scalar,"commonValidFraction",null,
                QualitySupportModel.OriginalPixels,1,.75));
        }
        return new(request,new(group?"dataset-b":"dataset-a",group?"dataset-b-r1":"dataset-a-r1",ImagingEvidenceBasis.ProtocolFixture,entries.ToImmutable()),
            new(group?"profile-b-r1":"profile-a-r1",2,1,cells.Select(c=>new ImagingQualityCell(c.CellId,
                ImmutableArray.Create(new QualityRegionSpec("roi",new QualityBox(0,0,1,4))),
                plans.ToImmutable(),bindings.ToImmutable())).ToImmutableArray()));
    }
}
```

GateVisual是本测试工程的因果装饰器，完整实现上游IQualityVisualPort：构造持inner、一个ManualResetEventSlim及一个RunContinuationsAsynchronously的TCS；仅首次Observe在原同步调用里登记invocationId/active并置Entered后等待gate（不链接executionToken使它假退出），实际放行后才按原token委托inner.Observe。CheckDrain在该原调用未退出时Pending；退出但未成功进入inner时Drained；Close只能在Drained后归还本方gate标记，若曾委托inner则只关闭同invocationId，重复true幂等。finally标实际退出；所有查询短锁、不在锁中等待。不能返回一个后台假的成功backend；gate在BridgeCase强持且Release幂等，最后实际退出才Dispose本case闩锁。故障版本在同装饰器按§16.9表改分支，不发布第二模拟包。

对应同工程的GateVisual完整形状如下；System、Linq、Threading、Tasks通过ImplicitUsings=enable导入。它只验证托管协调因果，没有native工作，也不声称模拟闩锁是真设备退出。

```csharp
internal sealed class GateVisual(IQualityVisualPort inner) : IQualityVisualPort
{
    private readonly object sync = new();
    private readonly ManualResetEventSlim gate = new(false);
    private readonly TaskCompletionSource<bool> entered =
        new(TaskCreationOptions.RunContinuationsAsynchronously);
    private Guid invocation;
    private bool started, active, delegated, released, disposed;
    public Task Entered => entered.Task;
    public void Release() { lock(sync) { if(!disposed) gate.Set(); } }
    public QualityBackendResult Observe(Guid id, QualityMethodPlan method,
        QualityRegionSpec region, ImmutableArray<IQualityReadScope> scopes,
        QualityBudget remainingBudget, int width, int height, CancellationToken token)
    {
        lock(sync)
        {
            if(started) throw new InvalidOperationException("fixture-only-first-invocation");
            invocation=id; started=true; active=true;
        }
        entered.TrySetResult(true);
        try
        {
            gate.Wait(); // 此同步原调用真实退出前Active始终为true。
            token.ThrowIfCancellationRequested();
            lock(sync) delegated=true;
            return inner.Observe(id,method,region,scopes,remainingBudget,width,height,token);
        }
        finally { lock(sync) active=false; }
    }
    public QualityDrainState CheckDrain(Guid id)
    {
        bool callInner;
        lock(sync)
        {
            if(!started || invocation!=id) return QualityDrainState.Unknown;
            if(active) return QualityDrainState.Pending;
            callInner=delegated;
        }
        return callInner?inner.CheckDrain(id):QualityDrainState.Drained;
    }
    public QualityCloseResult Close(Guid id)
    {
        bool callInner;
        lock(sync)
        {
            if(!started || invocation!=id) return new(false,new("QS-InvalidRequest","invocation","ImageQuality.Error.InvalidRequest"));
            if(released) return new(true,null);
            if(active) return new(false,new("QS-DrainPending","invocation","ImageQuality.Error.DrainPending"));
            callInner=delegated;
        }
        var result=callInner?inner.Close(id):new QualityCloseResult(true,null);
        if(result.Released) lock(sync) released=true;
        return result;
    }
    public void DisposeConfirmed()
    {
        lock(sync)
        {
            if(disposed) return;
            if(active || (started&&!released)) throw new InvalidOperationException("fixture-retained");
            disposed=true; gate.Dispose();
        }
    }
}
```

测试Program先创建容量2的List<BridgeCase>并登记两个新Owner，再分别调用RunA(owner,false,token)/RunB(owner,false,token)验正常；两个根确认Released并消费报告后才移除，再分别用新的Owner调用gated=true验取消/迟到恢复。--host bridge-a/bridge-b分别作为独立子进程执行，不能B从A的request/Session借对象。A正常必须四Search及一个Verification、五次质量Start；原向量依次(254,.25)、(190,0)、(100,.25)、(140,0)，前沿为100/0与100/1，独立选择100/1验证向量(190,0)，完整软件分母5/5。B另一次非gated正常执行Group共同mask3/4、requiredSteps=presentSteps=3，Search/Verification组分别独立；gated版只验证取消与恢复，不拿取消样本当数值通过。两者均Basis=ProtocolFixture，软件Core推荐标签不能作为图像质量/独立实测或客户验收结果。模板限额、4×1像素/码阈值、秒数都是夹具参数，没有生产默认值。

### 16.9 六项矩阵、可执行反例与benchmark落点

| 子范围 / 六项 | A1-Q质量服务消费桥 | A2-R冻结离线观察桥 |
|---|---|---|
| 1 边界/消费者 | §16.4/16.6；工程台/Worker，只摘原量/支持，不生产放行 | §16.4/16.5；同两个Host，零设备命令/不补拍 |
| 2 完整公开API | §16.4 Session/Factory/Options/Call/Profile/Metric/Evidence；§16.6–16.7版本/单位/错误/原Owner/关闭 | §16.4 Dataset/Entry/Frame与已有IObservationPort；§16.5精确读回键/身份/实际settings/分组 |
| 3 空Host | §16.8全部输入/工厂/Build、两入口、§10完整Constraint/Store源码复用，无UI/SDK/产品私类 | 同上独立来源及两进程；纯快照Observe/Reconcile，不依赖HALCON |
| 4 场景与断言 | 下表IO.QB.01–12；正常→故障→独立cleanup→同Owner恢复，不重Start | 下表IO.RB.01–06；缺格/重复物理ID/扰动/来源漂移与元数据冲突 |
| 5 Benchmark | 下段质量构造/读取/原量/映射/封口/真实归还测点，§12唯一统计 | 绑定预检/深快照、精确查找/receipt生成/对账与总输入容量测点 |
| 6 唯一落点/门 | 页首唯一Adapters及Adapters.Tests，net10.0；发布时引用本模块Core及image-quality.Core | 共用同一工程/测试，无新Contracts/Host/Simulator工程；厂商SDK/产品store仍禁止 |

A1-Q/A2-R的公开质量桥/精确原量支持、离线settings/完整分母、双Host/Owner恢复等确定指导内容已由主控限定接收；主控已完成§16.4–16.10全内容及最新§16.8/IO.QB.10回读。A1/A2整体仍PreparationIncomplete，不提升整模块或真实AsunImage/质量后端/设备存储资格，不标适配/UI为无UI CoreReady；C1/C2/C3/U1原接收保持。公开factory/Profile/原Task/支持映射/分母/双Host/异常恢复是内部规格，不能列为待客户提供。后续实际实现/编译和下表验证是内部执行门，不伪称外部门。

| ID / 固定反例 | 将实现的可判定断言 |
|---|---|
| IO.QB.01 双Host正常 | A/B独立进程同公开factory，无上游测试shim；A上述五组原量/2个前沿/最终选1个/五分母；B正常共同支持3/4且不输出相位质量。 |
| IO.QB.02 Raw外容器缺项 | Raw容器因另Required不可观测但所选Coverage内层Computed仍逐项映射；全false→Coverage0、Contrast/Saturation null，不删灰度Required，不抬前沿。 |
| IO.QB.03 unsupported/键/单位 | managed后端请求合法Sobel得到Unsupported/OutOfDomain且无response；wrong MethodKey/ScalarKey/Unit/NaN/重复键/provider失败分别IO-010/018，零成功向量；没有自动备用。真实输入Descriptor在Open即错必须Observe次数0，原实际scope/attempt仍登记并最终只关闭一次。 |
| IO.QB.04 支持分母 | 5×5 Sobel3 Center=9；一个中心孔洞侵蚀后0中心时NotObservable；Requested/Valid/Center分别核，饱和分母不换Center。Native数值分支需真实HALCON资格，结构/映射可先用显式端口反例。 |
| IO.QB.05 取消/迟到 | gate Enter后RequestCancel/执行token取消；释放前原Completion和scope仍持有，Close有限false；放行后原取消结果/无报告、同IDStart计数1，Session恢复归还但推荐不复活。 |
| IO.QB.06 首次释放false/fault | 上游真实Drained后首次Close失败保留；旧有限观察Task已结束false/fault，下一Recover查原Owner真实账本。最终释放true仍原Failed/QS-ReleaseFailed；成功阶段关闭计数1，无成功Evaluation。 |
| IO.QB.07 构造gate/失败 | slot.Reserve在input/visual factory前；绑定尚未Plan也Close有界，原construction晚成功只Stop、不Start；同步throw无活资源即释放，不制造native未知。 |
| IO.QB.08 预算 | checked源像素/半开面积溢出或64MiB差1、第二质量槽不足：下一factory/Open次数0；halo/重复read/输出累计不重置，Quota非提前归还。 |
| IO.QB.09 重复/并发 | 同原意图Evaluation Task ReferenceEquals，Call.Guid不变；同ID异Settings/Profile/Receipt拒IO-012；第二不同ID活动请求IO-016，无第二operation。 |
| IO.QB.10 双错误/移交 | 注入Core.Close同步throw/fault/等待到期，Session.Close仍先独立登记并调用一次；反向Session失败不跳过Core原任务观察/收尾。参数/执行CTS创建失败记业务错误，gate/Cancel/快照/后续清理错误不覆盖已有BusinessError；cleanup仅首错误+饱和计数，已取消executionToken不取消独立清理窗。未结束同原Task不重调factory；失败观察结束后显式同Owner恢复，成功恢复/Dispose读取原成功Task。Dispose已fault且IsCompleted=true仍Released=false；其它控制Task未结束不得启动Dispose。所有原任务结束、Core.Dispose正常成功、Session.AllTasksEnded/ResourcesReleased且未决空及本地释放成功才可移除Owner；否则原Task/Session/数据继续可达，不正常卸载、不追补推荐。 |
| IO.QB.11 版本/回退 | Profile/method/runtime/descriptor改修订使新Plan；旧版本只原事实查询、不再评价，不能新方法重解释旧分数；Core §11全部canonical字节/hash保持。 |
| IO.QB.12 方法建议 | 无任务标签仅NotEvaluated对照；质量方法候选不混入物理轴，无连续反推/无扩大Capability；验证数据不能选Search策略/中心。 |
| IO.RB.01 缺格 | 删除verify条目→Rejected/IO-011，总计划分母仍5，最终NeedsReview而非4/4成功；端口设备调用数0。 |
| IO.RB.02 物理重复 | 给verify使用Search原PhysicalAcquisitionId，即便改SourceRevision/hash或RoleKey也不计独立样本，候选验证无效；不以Guid不同补样本。 |
| IO.RB.03 扰动读回 | 固定能力[50,100,200]：100的+1必须实际200；记录仅100拒匹配，200的+1越界无Observe，保留格缺口。 |
| IO.RB.04 元数据 | 同SourceRef异mask、StepIndex错、ExposureRevision/ProjectionRevision/组缺失或时间回退拒对应坏输入；Group缺角色允许上游StepMissing，不能删除期望步序补Computed。 |
| IO.RB.05 对账与重复 | Observe同ID回原事实；恢复进程Reconcile用原耐久Intent/冻结记录重建同原身份，Observe/质量Start次数0，缺记录Unknown；未知/来源Changed不能补取latest；纯值无在途Drain真实true。 |
| IO.RB.06 保留/关闭 | Bind观察超时不清原Task；Close拒新普通任务但Recover可查旧Owner；恢复后所有原任务结束/质量root可忘/Quota一次归还，不Dispose活scope。 |

Benchmark消费§12 BenchmarkProfile及DEV-GOV-010 §3.1统一统计口径，不新增相同统计DTO；原InputSizes不改。本片另从Dataset/Profile/QualityRequest直接取得结构负载（源数、总矩阵像素、ROI像素、mask有效数、tile/halo读取量、方法/输出项数、quality根槽/保留报告数、managed/native追加峰值），写进测试结果阶段列，不能向Core.InputSizes塞未知名称。预热/冷启动/测量数/最低有效样本/时限/目标源沿已采纳Profile；目标未采纳=NotEvaluated。阶段测点：Session纯构造→绑定完成、质量槽Reserve→原Construction完成、Start→真实Completion（含资源）、各ReadBlock/方法Observe/核验→Objective映射、Cancel→native真实退出→scope归还、Close/Recover→TryForget、Core接纳→最终Commit且桥本次借用全归还。还记录等待超时到迟到归还的时长与持留容量，不把调用方WaitAsync结束计作端到端。负载覆盖全false/孔洞/半开边缘、重复源多角色、UInt8/UInt16/Float32、全域快照预算、慢Open/Observe/Close、错输出/源Changed和完整验证矩阵；故障/超时/删失不删样本，不以模拟时延证明native/HIL性能。

### 16.10 执行约定、两轮自审和精确资格门

获准实施后，唯一Adapters.Tests为Microsoft.NET.Sdk/net10.0/OutputType=Exe，引用本模块Adapters/Core及image-quality.Core与BCL；测试夹具在本工程`QualityBridgeHostTests`消费IO.QB/IO.RB，公开包装配示例在同工程`QualityBridgeHostExamples`，没有新增测试工程。复用§10.4外层Process.Kill(true)有限runner，build 120s、case进程30s/suite进程120s，内部单case总25s/suite总110s（外层留日志与退出余量）；外层杀验证子进程仅表示失败，不证明产品native已释放。命令为`dotnet build src/Modules/imaging-optimization/Asun.Modules.ImagingOptimization.Adapters/Asun.Modules.ImagingOptimization.Adapters.csproj -c Release`、`dotnet run --project tests/Modules/imaging-optimization/Asun.Modules.ImagingOptimization.Adapters.Tests/Asun.Modules.ImagingOptimization.Adapters.Tests.csproj -c Release -- --suite quality-bridge,replay-bridge --deadline-ms 110000`；`--host bridge-a`/`--host bridge-b`单独执行该Host的normal,cancel,late,close-fault用例（每个新Session），未知selector/失败/未完成/必需跳过返回非0。真实HALCON套件须另显式`--backend asunimage`并提供真实样本/资格Profile，缺失非0/NotEvaluated，不以托管route Unsupported当native通过。当前不创建工程、不执行命令。

第一轮自审按公开输入→Bind→数据键/实际设置→QualityHostSlot工厂→Start/原Completion→支持/单位/Objective→完整分母核对，修正Validate后显式ConfirmPlan、统计独立组与采集步组、原有效像素与窗口中心、Unsupported与provider坏输出、方法实验与物理候选的边界。第二轮按两个独立Host→取消/late→独立cleanup→原Task/根quota→重复false/fault观察→退回旧版本走查，修正factory前Starting条目、GateReady因果交接、共享原Close观察和独立cleanup总窗，补充纯参数预门/质量根容量及完整闩锁方法体；内部欠账在本正文修正，不转为客户阈值缺失。自审与定向文本验证不证明C#编译或运行。

本次Host finally窄修另做两轮局部自审：第一轮按参数/CTS失败→gate/Cancel→两个Close同步throw/fault/超时→各自Recover→原业务Task逐项走查，分别保护清理步骤并同时启动两组件观察，未结束原Task复用，业务错误不被cleanup覆盖。第二轮按已完成false/fault→late恢复→控制任务全结束→Dispose成功/fault→Session快照→本地归还走查，成功恢复/Dispose复用原结果，只有全部释放证明成立才Released=true；首cleanup错误+饱和计数、IO.QB.10及保根/不追补推荐一致。仅定向文本/声明检查；未消费编译或运行反例，A1-Q/A2-R确定指导内容现已由主控限定接收。

| 精确门 / Owner | 只限制的范围 |
|---|---|
| 主控限定内容接收；本模块Owner | A1-Q/A2-R确定指导内容已接收，A1/A2整体PreparationIncomplete及后续资格门保持；不提升整模块/真实适配/后端/设备存储或UI，不标适配/UI为无UI CoreReady。C1/C2/C3/U1原接收保持。 |
| 创建/消费编译、原Task/Root/Quota/双Host/映射断言；实现Owner | 本片内部实现与发布，不是客户外门；本轮未做build/run。上游正式发布Core/签名消费也是实际集成验证，不改上游指导。 |
| 实际image-quality.AsunImage公开工厂/26.05运行指纹、位深/ROI/mask/halo/算子Golden/峰值系数；视觉Owner | A1真实视觉路线/准确率与性能；托管协议可独立验证，不冒实测。 |
| RecordedInput的真实画像、原图hash算法、原曝光/组/坐标/方法及样本标签/任务真值；来源与方法Owner | 真实历史评价/独立验证/方法建议资格；ProtocolFixture仅软件协议。 |
| 设备能力/量化/时基/物理读回/互锁/能量温升/租约及安全写权；宿主设备Owner | A2实时观察和安全恢复，具体厂商SDK仍不纳入本轮；不阻离线零设备桥。 |
| 产品Contract/Schema/耐久store/CAS及当前适用批准、客户质量门/HIL/FAT/SAT；产品与客户Owner | 正式产品接入/生产推荐采用；不预造产品DTO、质量批准或数据库表。 |
| 真实WPF/三语/UIA/图像native桥/1920×1080及性能；U1宿主Owner | U1运行/产品资格仍PreparationIncomplete/NotReady，无UI桥不授权UI通过。 |

## 17. 双视角场景走查与验收断言

左列为实现者按契约推进，右列为集成人/操作员实际后果；每条均使用冻结计划/同端口修订，不靠辅助脚本补合同。

| 场景 | 实现者：顺序、输出、状态 | 集成人/操作员：恢复与可判定断言 |
|---|---|---|
| 正常/多候选 | §11四组合→逐格事实→最坏值→严格前沿→指定验证→全端口排空→耐久提交 | 看到3个工程候选、最终只1个选定验证候选；查询与事件可复演，无生产写参数 |
| 退化/弱信号 | §16先域交集/面积→指标/拒识，缺Required值不进前沿 | 指出具体Cell/ROI/目标原因；可改新草稿重试，原证据保留，无“零分合格” |
| 大规模/多维 | BigInteger组合数、惰性cursor、逐项额度；全体互不支配时摘要容量最坏增长 | 显示已搜及未搜范围；容量/时间不足NeedsReview，无“全局最佳”或分配全空间 |
| 参数/版本变化 | 新hash/ID，旧cursor拒绝；在途端口修订变化停止并排空 | 新草稿不覆盖运行/历史；原结果可历史查看，不能显示当前可直接应用 |
| 并发/重入/重复 | 一个Owner/CAS；乱序按AttemptIndex归约；同EventId/Intent只一事实 | 双击开始不重复曝光；回调重入拒绝；查询/取消不被UI排序阻塞 |
| 取消/超时 | 停新Intent→跟踪原task→对账→各端口Drain，等待token取消不撤销停止意图 | 按取消显示等待，不当设备已停；额度差一次不多发，一次事件重复不多消费Trial |
| Unknown/迟到 | 副作用前已有ObservationId；恢复按原request查；未决ResourcesReleased=false | 禁止重新曝光/恢复原配置；迟到事实只对原意图，终态不复活 |
| 关闭/native异常 | Close拒新操作，UI detach不代表native归还；Dispose未知抛IO-014 | 宿主保存Owner/原ID继续恢复，不提前Dispose相机/图像；未知时没有最终推荐 |
| 存储失败/重启 | Intent未耐久零副作用；receipt写失败停止；Read分页恢复只对账不续搜 | 能看到“未保存/需对账”；新实例查询区分不存在和存储不可用；不靠重启重触发 |
| 迁移/回退 | 未知枚举/必需字段拒读活动状态；新ID只读迁移；先排空再切程序集 | 旧快照/证据保持可追溯；不得把新候选写旧事件；已提交推荐不被迁移覆盖 |
| 长期运行/资源增长 | 所有在途/摘要/事件/native/disk计量预留，背压再停止 | 无无限日志/图像缓存；Unknown/失败事实不被compact丢弃，无清理用户配置 |
| 无UI/第二消费者 | Console只引用Core，替换端口不改公开DTO；回放设备调用0 | 工程台与产品草稿适配得到相同计算结果；HIL前不宣称真实设备能力 |

## 18. 全批准范围文档准备结论、覆盖与剩余Owner（2026-10-12）

**结论：当前架构和用户明确需求内，全部可决定软件设计已闭合，无剩余内部算法/API/codec/架构/UI决定需要后续开发者补猜。** 覆盖完整模块，不仅C1/C2/C3。本轮仅补§6.3参数建议/受控试采与采用交接、§9.7原Presenter端口CPU显示实施路线及§9.8三语资源，未扩大能力、改原公开型/方法或增加工程。设备/客户未知物理事实不编值，按下表精确用途与原Owner采纳；这与产品ImplementationSpecificationReady/运行资格分开。

| 全批准能力/消费者 | 唯一实施定位及可确定内容 | 不适用边界 |
|---|---|---|
| 参数/身份/codec；工程台与AOI/钢网草稿适配 | §1～3/3.0.1/8/11：完整轴/步骤/单位/量化/锁定、有限能力表、canonical字段/字节与hash、版本/快照/预分配门、迁移与回退 | 不定义厂商连续轴、不重写原物理证据hash、生产程序/产品Schema不进入Core |
| 候选/自动参数建议与试采编排 | §6.0/6.3/11/12/16.7：基线/先验/mixed、local邻域/轮屏障、Proposal身份与有界回退、共同约束/能量预算、计划验证与停止；无标签/资格拒识；试采恢复和生产采用交接明确 | 非连续自动曝光/PID；无自动扩轴、改阈值、反推档位或设备/质量写权 |
| 指标/支持/拒识/前沿/置信解释 | §6.1～6.3/16.1～16.3/16.6：完整格/重复/独立组、方向/最坏值/严格支配、逐方法域/单位/支持数、缺口、Required质量门与独立验证 | 不将单帧空间量当重复性，不从高分/覆盖/前沿制造概率置信或全局最优 |
| HALCON/质量服务Adapter | §15.1/16.1～16.10：26.05具体路线与ROI/halo/backend边界、公开质量Session/Factory/输入/报告精确键与原量支持、失败/异步Owner/恢复及双Host | 经ImageLibDotNet.cv2/上游image-quality唯一实现；不写另一视觉算法，不凭managed协议认定native方法资格 |
| 冻结离线数据/实际settings/存储与实时适配契约 | §3/4/6.1/6.3/7/8/16.4～16.5/16.7～16.10：按完整设置/名义扰动/物理身份查键、只原事实对账、事件CAS/完整分母、设备及存储Owner边界 | A2-R零设备，不取latest/相邻图/补拍；厂商SDK具体实现暂不纳入，产品库Schema与恢复写权不在公共模块 |
| 生命周期/取消超时/双component恢复 | §4～5/7/9.4～9.6/16.7～16.8/IO.QB.10：factory前登记、原Task/槽/Quota、独立停止/有限观察、late原Owner恢复、业务/清理双轴、Dispose正常成功及真实释放证明 | 无GC/等待超时/页面卸载/故障Task完成伪释放，不借新实例重做旧意图 |
| 可选WPF控件；两个独立STA Host | §9.1～9.8：25.2.3 Dock/PropertyGrid/Grid/Chart/BarButton+SuperTip、紧凑双图/表/二维前沿、角色/键盘/UIA/三语、原Binding/lease/Root与CPU快照显示步骤/坐标/显示窗 | 无UI路径用同Core；图像只读，无质量ROI编辑、产品发布按钮、独立语言入口；当前不直接消费viewport Assembly |
| 验证/性能/交付接入 | §8/10～14/16.8～16.10/17及本节：唯一DLL/测试目录、两个无UI/STA/桥Host、原有效Golden/反例、参数/源/版本/故障/恢复/取消负载及性能测点/统一Profile判据 | 模拟/协议/截图不作HALCON/WPF/HIL或客户生产证明；未采纳性能目标为NotEvaluated |

| 剩余项及准确Owner | 仍需的输入/实际验证 | 只影响的资格范围 |
|---|---|---|
| 本模块实现Owner | 获派发后创建既定工程、消费已冻结公开API/codec/三语/显示路线并执行§10/12/16.9及STA断言；实现中发现矛盾回到本文修订 | 代码构建/正式测试/发布与可调用性；这些是未执行工程验证，不是仍待设计的接口或算法 |
| image-quality视觉/运行Owner与工程用途Owner | 实际AsunImage工厂/26.05指纹、代表图像/位深/ROI/mask/halo/方法Golden；物理黑白电平、最小支持/目标真值/质量界限/任务方法及参数用途Profile、峰值/CPU路线比较 | 对应真实质量方法/准确率/建议用途；缺一项不凭软件协议上调真实资格，不阻Core/离线协议实现 |
| 原图/来源Owner与Host预览Owner | 冻结源hash算法/坐标/实际设置/独立组/RoleKey/CPU快照/显示窗与现有公开来源接线；真实来源复制与lease退出证明、WPF缓存/实际像素峰值 | RecordedInput可采用性和真实图像预览资源验证；CPU显示步骤已确定，不能把缺客户图/来源授权说成需要临时发明UI桥 |
| 设备/安全Owner | 设备实际合法档位/量化/曝光读回、时基、能量温升/互锁、独占租约/恢复写权与CAS、具体Host适配公开接线和HIL | 实时试采/安全恢复；Core不编物理阈值，不纳入暂缓厂商SDK实现，不阻A2-R |
| 产品/持久化Owner | 实际事件/结果存储实现、事务耐久/CAS/重复查询/崩溃恢复、产品正式Contract/Schema及程序草稿审批/发布映射 | 真实持久化/重启集成和生产采用；公共IResultStore/停止恢复语义已冻结，不由本模块新增产品表 |
| U1 Host/运行Owner | 按§9原Root/Presenter接口及CPU路线完成真实25.2.3/WPF消费编译、1920×1080固定ClientRect/三语/Tab/UIA/DPI/Dispatcher/来源lease/性能验证 | WPF/真实显示/卸载/交付资格；不标无UI CoreReady，不要求未消费的viewport接线 |
| 性能/客户验收Owner | 采纳§12 BenchmarkProfile的实际环境/负载/最低样本/时限/资源Target、方法用途与HIL/FAT/SAT/生产质量门 | 各自性能和现场验收；未采纳Target只诊断NotEvaluated，不编“达标”数值 |

本轮内容审核在永久原会话完成，总控仅接收状态。第一轮按真实消费者的“请求→候选/试采→原量/支持→验证→停止/恢复→草稿交接”核对已有规则，补不依概率置信和生产静默采用的确定解释；第二轮按两个STA Host的“完整预览键→CPU复制/显示窗→原Dispatcher/lease→坐标/双图交互→卸载/late归还→三语/错误恢复”核对，补具体显示路线并保持既有Root/Close不重审。再沿上表全部批准能力检查职责/输入输出/参数/Owner/异常/独立消费者及测试性能唯一落点；复用原研究、自审和§11/16.8有效向量，不重算其数值、身份Golden或重跑旧全审。本次定向文档验证通过：复用validate_docs.targets核本地链接，另核锚点、围栏/表格、原16个示例块未改、新资源对原枚举/全部IO/UI错误覆盖及各新增小节唯一落点；不新增报告/脚本。

C1/C2/C3既有ModuleCoreImplementationReady、U1与A1-Q/A2-R原内容接收均保持；A1/A2及U1实际运行/产品仍PreparationIncomplete/NotReady，整模块不提升ImplementationSpecificationReady。该保留不是内部设计未完成，也不是免除Adapter/UI设计；其实现与上述真实资格仍需独立关闭。本轮未创建产品/测试工程、未build/run、未执行HALCON/Golden/WPF/性能/HIL或现场验收，不把文档验证称代码通过。禁止范围与明确不支持能力继续生效。

## 明确不支持能力

本模块不拥有连续自动曝光/自动增益闭环、相机触发时序、光源PWM/电流控制、结构光图案编排、HDR重建、运动同步、跨板目标关联、工艺阈值推断、质量放行、设备安全互锁、训练数据采集或生产程序发布。宿主设备/采集/程序Owner通过本端口完成这些外部职责；缺少租约/读回/对账/停止边界IO-006/009。数字增亮、LUT、重复帧、模型预测不冒充真实观察。§6.3有限受控试采和§9.7只读显示映射不扩张以上边界。


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

## 附录 A：逐切片六门复核及接收状态

本模块唯一Core/测试工程和允许/禁止路径见页首；以下分切片只是实现顺序，不缩减整个模块。一个永久会话/一个Owner，本轮只改本文，不新派生模块会话或子代理。

| DEV-GOV-010 §3.1 门 | 定位与本轮准备结论 |
|---|---|
| 1 职责/第二消费者 | §1/2/10/14：边界、无生产事实写入、工程台及AOI/钢网复用计划已明确，C1/C2/C3六门内容已由主控接收 |
| 2 完整Module API | §3–8/10：v0.2字段/codec公开工厂/同步入口资源预门/构造期清理/目标格/扰动/方法/事件/单位/结果/排空/恢复/兼容/原Task Owner/资源配额/事件分页已补齐，C1/C2/C3六门内容已由主控接收；不是产品Schema批准 |
| 3 无UI最小Host | §8/10：BCL Core、五类业务端口与统一资源配额、完整Program/独立Console与Worker字段映射、唯一net10/BCL Exe及有限命令；工程未创建，构建运行属于获准后的验证 |
| 4 场景/测试 | §10–12/17：固定case/suite/外截止、独立canonical bytes/hash、正常、多候选、重复、并发、取消/超时/关闭、恢复/回退及定向断言；尚未执行Core测试 |
| 5 Benchmark | §12：负载/测点/预算与GOV010唯一统计口径已明确；测量方法冻结，目标值待消费者Profile采纳，未测量/未判通过 |
| 6 落点/调用/后续门 | 页首/§10/下表：唯一工程/测试目录、禁区、最小调用及外部门明确；C1/C2/C3主控已接收，ModuleCoreImplementationReady；其它切片仍PreparationIncomplete |

| 切片（保持完整模块责任） | 可决定的实现内容 | 本轮状态及只阻断该切片的后续门 |
|---|---|---|
| C1 Core计划/身份/有限搜索/Pareto | §3/4/6/11：DTO、快照/校验、游标、最坏值、等值/严格支配、有界摘要；纯约束与Replay测试 | ModuleCoreImplementationReady（2026-10-10主控接收0.2.2六门规格）；无需客户设备阈值/HALCON/WPF，不代表代码运行 |
| C2 Core生命周期/持久端口/Simulator | §4/5/7/10/12/17：幂等意图、CAS、对账/排空、关闭/恢复、查询、预算；进程内mock故障注入 | ModuleCoreImplementationReady（同次六门规格接收）；真实store耐久/进程崩溃/SDK停止边界留集成门，不阻断mock契约实现 |
| C3 局部细化/候选建议端口 | §6.0：固定邻域/轮次/回退、Proposal契约与模拟不确定/异常 | ModuleCoreImplementationReady（同次六门规格接收）；训练/实际模型hash、数据/OOD门属于后续宿主AI适配，不以模型缺失阻断确定性Core |
| A1 AsunImage质量评价适配 | §16.1–16.3方法资格；A1-Q见§16.4/16.6–16.10公开质量服务消费/支持/指标/根Owner/双Host/六项 | PreparationIncomplete：A1-Q公开质量桥/精确原量支持、双Host/Owner恢复的确定指导内容已限定接收；真实AsunImage/质量后端/HALCON消费编译、方法Profile/参数用途/ROI/真实样本/Golden/峰值及CPU比较仍是精确后续门，不提升真实适配资格或无UI CoreReady，不宣称整片ImplementationSpecificationReady |
| A2 真实观察/存储及产品映射 | §4/6.1/7/8实时边界；A2-R见§16.4–16.5/16.7–16.10冻结离线输入/精确设置/零设备对账/双Host/六项 | PreparationIncomplete：A2-R离线settings/完整分母、双Host/Owner恢复的确定指导内容已限定接收；实际持久化/实时正式Contract/Schema、设备能力/能量温升/互锁恢复/租约/安全写权、耐久store/设备HIL与客户验收分别后续，不提升设备存储资格或无UI CoreReady；厂商SDK具体实现仍不在当前范围 |
| U1 可选WPF UI DLL | §9.1～9.8同页PageContract、Binding/RootOwner/StartOwned、结果消费/Dispatcher Detach、Presenter lease/Return、有限Unbind/保留确认、双STA及具体CPU快照/坐标/显示窗/三语路线 | PreparationIncomplete/NotReady：0.2.4 §9.4–9.6原指导接收保持，0.2.6补缺由本永久原会话完成内容审核/验证，软件设计无欠账；真实WPF/1920×1080/UIA/三语/图像来源native归还/性能和产品接入资格未关闭，仍需实现及25.2.3消费编译；不提升ModuleCoreImplementationReady，不阻断C1/C2/C3既有六项接收 |

C1/C2/C3既有ModuleCoreImplementationReady保持；当前完整批准范围文档结论见§18，不创建工程/产品代码，不以文档定向检查替代构建、性能、真实HALCON、Golden/HIL/FAT/SAT或生产验收。本模块内容审核/修复/验证由永久原会话完成，总控只调度和登记状态/共享导航，本文不复制第二权威。以下旧修订中的待接收措辞保留为当轮历史，以页首/§18及本表为当前结论。

2026-10-10 两轮有限定向自审（0.2.1范围）：第一轮按字段→处理→副作用→恢复关闭链核对，修正目标格关联/相对档位扰动、绑定修订、CAS及原Task Owner/显式配额；第二轮按两个无UIHost→页面操作→结果/预算/版本→链接核对，补充factory前宿主预留、late归还、query有界、读取/提交与公开UI事件/BarItem.SuperTip绑定。仅本文发生修改；路径/锚点及声明形状的定向检查结果随最终回执，不把文本检查当代码执行。六门资料待主接收，剩余内部事项是主会话接收/实施时消费编译与验证，不以物理门代替未完成的内部实现。

0.2.2主控窄修接收前两轮定向核对：第一轮仅检查公开codec/完整请求与两个Host、根Owner先预留/原AsTask/业务清理双轴/构造期预算；第二轮仅检查字节Golden、同步输入预门、全部夹具签名/门控、唯一Exe/build/run/外截止和UI卸载借用。仍未创建Core/测试工程、未消费编译或运行Host，所有切片保持PreparationIncomplete。四类JSON字节/摘要独立复算及18处本地链接/锚点、受影响声明/Host调用形状定向核对通过；未消费编译，不能由文本核对宣称运行。真正外门仅为设备物理/质量Profile与样本、正式产品/设备Owner资格和U1宿主预览lease桥/真实WPF验收；内部规格接收、Core实现与上述验证不能被外门替代。

0.2.3状态接收与U1窄修（2026-10-10）：主控独立回读0.2.2全部六门及四类canonical字节/摘要后，C1/C2/C3接收为ModuleCoreImplementationReady；仅Core规格，不代表构建运行。U1增补§9.4–9.6公开UI Binding/RootOwner/lease/Acquire对账/Unbind/有限观察/保留确认及两STA装配卡，仍PreparationIncomplete待内容接收。0.2.1/0.2.2尾段“所有切片待接收”保留为历史当轮状态，以本段及页首/附录当前状态为准。未改Core身份/搜索/资源规则、未重研HALCON、未建工程/代码/报告。

0.2.3 U1两轮有限定向自审：第一轮逐个核对Binding→AttachRoot→StartOwned→Acquire/原AcquisitionId对账→结果消费→Dispatcher Detach→Return→Unbind/保留确认→Root回池的公开型/前置/Owner及迟到路径；第二轮核对两个STA装配卡、控制槽/有限观察与自等待排除、重绑/卸载/Dispatcher shutdown/图像桥失败、三语/1920×1080验证门和逐切片状态。只更新本文，不改0.2.2接收的Core代码形状、身份字节/摘要、搜索/预算语义。U1内容待主控接收，实际WPF/DevExpress/性能/图像bridge资格未执行。

0.2.4 U1恢复终止条件窄修：区分真实lease/root归还工作与有限观察call，新增ObserveReturnAsync/ObserveRootReturnAsync仅查询原LeaseId/RootId账本；已完成false/异常后可有限重新观察，不重启动释放/Dispose，late真实归还可收敛到幂等true；业务/cleanup错误保留。C1/C2/C3接收状态与Core身份/算法不变，U1继续PreparationIncomplete待主控内容接收；仅文档定向核对，无运行声明。

0.2.5-prep（2026-10-11）：定向增加§16.4–16.10 A1-Q/A2-R的image-quality 0.6.0-prep服务精确消费、公开Session/Factory/Options/Profile/输入与原量/支持映射、离线读回/对账、完整分母及独立验证、双Host/原Task/独立cleanup/反例与benchmark。主控全内容回读并核最新§16.8原业务/五控制任务/finally与IO.QB.10后，限定接收上述确定指导内容；本次仅同步接收状态。A1/A2整体仍PreparationIncomplete，C1/C2/C3与U1既有接收保持；真实Native/AsunImage/质量后端、样本/参数用途、实际持久化/设备HIL/WPF/性能和产品资格仍按§16.10精确后门，不抬整模块或把适配/UI标为无UI CoreReady。仅修本指导，无新研究/复算、工程/代码、上游/共享/原件/AsunImage内部变更，未消费编译、build/run或实测HALCON/WPF/现场。
