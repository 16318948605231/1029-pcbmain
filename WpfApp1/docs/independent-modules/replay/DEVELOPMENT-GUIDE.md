# 历史回放与差异实验（Replay）开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`R-Core-Contract, R-Core-Lifecycle`

- 模块 ID：`IM-016`
- 既有来源：`PKG-043`、`SM-021`
- 版本：`0.2.3-prep`
- 状态：`DesignReview/Prep`；当前批准模块范围的指导准备完成（§17.3），产品资格另验
- 规划消费者：算法回归、离线调参、客户问题复现
- 适用技术：C# / .NET 10；核心无 UI；视觉后端经适配端口使用 HALCON 26.05 / `ImageLibDotNet`
- 工程准入：`NewProjectRequired`；本次未发现可复用且契约完全匹配的 Replay Core 工程。实现切片开始时创建 `src/Modules/replay/Asun.Modules.Replay.Core/`，测试放在 `tests/Modules/replay/Asun.Modules.Replay.Core.Tests/`，namespace 为 `Asun.Modules.Replay`。
- 本文是本独立模块唯一实施指导；Module API Contract v0.3保持，Simulator/Adapter/显示装配为本版扩展规格，不改旧Core形状或Golden身份。当前批准范围的内部软件设计欠账已由本永久会话自审闭合，结论及外部Owner见§17.3/§21/§23。原R-Core-Contract与R-Core-Lifecycle纯托管编排/协调/根Owner的ModuleCoreImplementationReady保持；文档准备完成不表示代码、真实HALCON/WPF、耐久、性能或现场资格通过。

## Core implementation binding

上述工程路径是本模块唯一 Core 写入位置；仅在实现切片获准启动时创建。适配器、Replay UI、产品 Shell、生产数据库和制程 DTO 不进入 Core。

## 1. 目标与边界

### 1.1 职责

模块接收不可变的历史证据闭包和明确的实验变更，完成以下工作：

1. 读取、校验和报告证据/程序/方法/模型/标定/运行环境的完整性。
2. 在隔离命名空间装配工程计算，支持历史解释、原版本重放、变更试验和控制流程模拟四种用途。
3. 按冻结的比较策略先比身份与有效性，再比离散语义和数值/几何内容。
4. 生成不可变的工程结果、差异明细、缺项诊断、耗时和资源摘要。
5. 支持取消、期限、崩溃恢复、重复请求去重和资源排空，且不影响生产运行队列。

### 1.2 禁止边界

- 不创建、修改或覆盖生产 `MeasurementSet`、`InspectionFact`、`MachineDecision`、SPC、Outbox、质量放行、复判决定或客户处置。
- 不发送相机、光源、运动、PLC、MES、机器人或其它设备命令；不加载可任意执行 DLL、脚本或外部命令。
- 不决定 PCB、SPI、AOI、点胶、涂覆或任何制程的目标关联、工艺阈值、缺陷类别、质量分母和放行规则。
- 不把候选结果、差异报告或 UI 保存动作解释为生产提交、资格批准或 Golden 更新。
- 不用 `latest`、同名文件、缩略图、零值、上一案例结果或“最接近坐标”补齐缺项。
- 不在核心中持有产品页面、ViewModel、私有数据库表、全局可变状态、设备 SDK 句柄或原生 HALCON 句柄。
- 不声明跨 CPU/GPU/驱动/线程调度的逐位一致；固定 seed 不是复现证明。

调用方拥有流程编排、身份和目标关联、工艺解释、最终判定、权限、质量放行、设备副作用和生产提交。模块只拥有本次工程计算及差异事实。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Replay.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"不在核心中持有产品页面、ViewModel 或原生 HALCON 句柄"，Core 在无 WPF 宿主中完整运行。

**Blazor/Web**：回放结果通过 gRPC/REST 查询；回放帧图像通过 HTTP Range 分片加载；浏览器不重新执行算法。回放命令经已授权接口，不经浏览器。

**AI 回放集成**：Replay 模块回放时须复现仲裁时的模型版本和置信度（`ArbitrationEvidence`），不得用当前模型版本重新仲裁历史帧。§1 已明确"不声明逐位一致；固定 seed 不是复现证明"——AI 推理的非确定性须标注。

**HALCON 双跑**：本模块协调回放编排，不直接调用 HALCON 算子；具体算子的双跑 CI 在被复现的视觉模块中执行。

## 2. 角色、依赖和数据流

```text
调用方冻结请求
    -> IReplayEvidenceReader（040/041 只读保持）
    -> IReplayProgramResolver（035 公开只读端口）
    -> IReplayExecutionEngine（038/算法节点适配）
    -> IReplayComparisonPolicy（策略提供者）
    -> 隔离的 ReplayResultStore（工程输出）
    -> 调用方的报告/UI/资格研究投影
```

依赖通过组合根注入；核心不通过容器暗取服务。建议的端口职责如下：

| 端口 | 输入/输出 | 约束 |
|---|---|---|
| `IReplayEvidenceReader` | 稳定引用 -> 只读租约、内容摘要、来源版本 | 先保持再读取；保持失败不进入执行；不返回生产写权限 |
| `IReplayProgramResolver` | 精确程序/算法/模型/标定引用 -> 已解析闭包 | 禁止同名替换；撤销/过期/权限不足显式返回 |
| `IReplayExecutionEngine` | 类型化节点图、输入租约、预算 -> 节点结果/工程错误 | 不注册设备命令；节点结果带 `ReplayRunId`、目标身份和修订 |
| `IReplayComparisonPolicy` | 原/候选结果 -> 比较项与汇总分类 | 策略版本、单位、方向、容差和缺失政策冻结在请求中 |
| `IReplayResultStore` | 按原 `RequestId` 查询操作/结果；保存完成报告/检查点并返回工程回执 | 仅隔离命名空间；写入采用幂等键，不能写生产事实；读回须区分 Found/NotFound/Unknown |
| `IReplayClock`（必填） | 单调期限/虚拟流程时间 | 真实性能时钟与控制模拟时钟分开；不建立第二套事实时钟 |

计划中的第一消费者是算法回归；第二消费者是客户问题复现工具。二者使用同一核心，仅由各自适配器提供证据读取、执行图和报告投影。

## 3. Module API Contract v0.3：输入、输出与值

以下为 `Asun.Modules.Replay` 的公开声明规格，引用 `System`、`System.Collections.Immutable`、`System.Threading`、`System.Threading.Tasks`；不是已存在程序集。局部契约由本文冻结，平台 Schema 仅映射。集合不得为 default；字符串为有效 Unicode，不隐式 trim、改大小写或 NFC/NFKC。协议 ID 使用区分大小写 ASCII `[A-Za-z0-9._:-]`、1–128 字符，显示名称不承担身份。

```csharp
public enum ReplayPurpose { HistoricalExplain, ExactReplay, ChangeExperiment, FlowSimulation }
public enum ReplayStartMode { FromRoot, FromCheckpoint }
public enum ReplayComparisonKind { Exact, Tolerance, DiagnosticOnly }
public enum ReplayDeterminism { Unspecified, SemanticTolerance, BitwiseSameEnvironment }
public enum ReplayValueKind { Boolean, Text, Int64, Decimal, Float64, Artifact }
public enum ReplayValidity { Valid, Missing, NotRun, Invalid, NonFinite, Ambiguous }
public enum ReplayCaseOutcome {
    CompletedEqual, CompletedChanged, CompletedIncomparable, Failed, CancelledOrNotRun, Unknown
}
public enum ReplayState {
    Created, Preflighting, Ready, Running, Completing, ResultSealed,
    CancelRequested, FailureObserved, UnknownObserved, Draining, Drained, ResourcesReleased,
    Completed, Cancelled, Failed, Rejected, Unknown
}
public sealed record ContentRef(string AssetId, string Revision, string Schema,
    string DigestAlgorithm, string Digest, long ByteLength);
public sealed record EvidenceClosureRef(ContentRef Manifest);
public sealed record ProgramClosureRef(ContentRef Manifest);
public sealed record ComparisonPolicyRef(ContentRef Manifest);
public sealed record TargetRef(string ProductId, string SideId, string TargetId,
    string DefinitionRevision);
public sealed record FovRef(string ProductId, string SideId, string FovId,
    string CoordinateRevision);
public sealed record ReplayCutPoint(ContentRef Checkpoint, string NodeId,
    string NodeRevision, ContentRef State, string EnvironmentDigest);
public sealed record ReplayScope(ImmutableArray<TargetRef> Targets,
    ImmutableArray<FovRef> Fovs, bool IncludeUnresolved);
public sealed record ResourceBudget(TimeSpan Deadline, long MaxInputBytes,
    long MaxOutputBytes, int MaxCases, int MaxConcurrency, long MaxNativeBytes,
    long MaxGpuBytes, int MaxQueuedCases);
public sealed record ReplayRuntimeProfile(string BackendId, string BackendVersion,
    string? ModelRuntimeVersion, string NumericProfile, int? RandomSeed,
    ReplayDeterminism DeterminismLevel, string EnvironmentDigest);
public sealed record ReplayChange(string Path, ContentRef Before, ContentRef After,
    ReplayValueKind ValueType, string Unit, string Reason, string Author);
public sealed record ReplayRunRequest(string ReplayRunId, string RequestId,
    ReplayPurpose Purpose, ReplayStartMode StartMode, EvidenceClosureRef Evidence,
    ProgramClosureRef Program, ReplayScope Scope, ReplayCutPoint? CutPoint,
    ImmutableArray<ReplayChange> Changes, ComparisonPolicyRef ComparisonPolicy,
    ResourceBudget Budget, ReplayRuntimeProfile Runtime, string OutputNamespace,
    string ContractRevision);
public sealed record ReplayError(string Code, string MessageKey, string? Path,
    bool Retryable, ImmutableArray<string> Details);
public sealed class ReplayPortException : Exception {
    public ReplayError Error { get; }
    public ReplayPortException(ReplayError error) : base(error.Code) => Error = error;
}
public sealed record MissingDependency(string CaseId, string Role,
    ContentRef? Expected, string Code, bool RequiredForExecution);
public sealed record ReplayCaseInput(string CaseId, TargetRef? Target, FovRef? Fov,
    ImmutableArray<ContentRef> Inputs, ContentRef? Baseline,
    ImmutableArray<MissingDependency> Missing);
public sealed record ReplayValue(ReplayValueKind Kind, ReplayValidity Validity,
    string? CanonicalValue, ContentRef? Artifact, string Unit,
    string? CoordinateId, string? CoordinateRevision);
public sealed record DifferenceItem(string CaseId, string FieldId,
    ReplayValue Original, ReplayValue Candidate, ReplayValue? Delta,
    ReplayComparisonKind Kind, string PolicyRuleId, ImmutableArray<string> Tags,
    ImmutableArray<ContentRef> Evidence);
public sealed record ReplayPreflightResult(string ReplayRunId, bool IsAccepted,
    ImmutableArray<ReplayError> Errors, ImmutableArray<MissingDependency> Missing,
    string FrozenClosureDigest, ResourceBudget EffectiveBudget);
public sealed record ReplayProgress(string ReplayRunId, long Sequence,
    int CasesAccepted, int CasesCompleted, string? CurrentCaseId, ReplayState Phase,
    long InputBytes, long OutputBytes, long NativeBytes, TimeSpan Elapsed);
public sealed record ReplayCaseResult(string CaseId, string TargetIdentity,
    string? OriginalDigest, string? CandidateDigest, ReplayCaseOutcome Outcome,
    ImmutableArray<DifferenceItem> Differences, ImmutableArray<ReplayError> Errors,
    TimeSpan Elapsed);
public sealed record ReplaySummary(long Denominator, long CompletedEqual,
    long CompletedChanged, long CompletedIncomparable, long Failed,
    long CancelledOrNotRun, long Unknown);
public sealed record ReplayPhaseDuration(string Phase, long ElapsedNs);
public sealed record ReplayResourceUsage(long? PeakManagedBytes, long? PeakNativeBytes,
    long? PeakGpuBytes, long PeakInputBytes, long PeakOutputBytes, long CopiedBytes,
    int PeakConcurrency, int PeakQueuedCases, long PeakQueueBytes,
    long? CancelToDrainedNs, long? DrainedToReleasedNs,
    ImmutableArray<ReplayPhaseDuration> Phases);
public sealed record ReplayResult(string ReplayRunId, string RequestId,
    string Namespace, string FrozenClosureDigest, ContentRef CaseResults,
    ReplaySummary Summary, ReplayState FinalState, long ProductionFactWrites,
    ReplayResourceUsage ResourceUsage, ImmutableArray<ReplayError> Errors,
    string SealedResultDigest);
public sealed record ReplayCasePage(int Offset, int NextOffset, bool IsLast,
    ImmutableArray<ReplayCaseResult> Items);
```

### 3.1 字段、单位、域与默认值

| 字段 | 有效域与来源 | 不满足时 |
|---|---|---|
| ContentRef | AssetId/Revision/Schema 非空；新 digest 为小写 SHA-256、64位十六进制，ByteLength>=0；历史算法由适配器支持表明确列出 | 长度/hash 不符 0002，未知 schema 0013；不能同名替换 |
| Scope | Targets/Fovs 为联合选择器；两者皆空选择闭包全目录；重复选择器拒绝；IncludeUnresolved 保留既有未关联 CaseId，不做目标关联 | 目录为空 0004；禁止空目录成功、数组配对 |
| Target/Fov | ProductId/SideId/TargetId/FovId 及修订来自宿主；大小写敏感；同 ID 不同定义修订不能视为同语义 | 身份冲突/歧义 0004，坐标不可比 0008 |
| CutPoint | FromRoot 必须 null；FromCheckpoint 必填完整封存状态、节点/环境摘要和上游输入闭包 | 0012；不得只因文件存在就复用 |
| MaxCases | Budget 中唯一一处；1–int.MaxValue，受宿主 Profile 硬限；无模块默认值 | 分配前 0006，不截断目录 |
| Deadline | 有限正 TimeSpan，宿主必填；从原子接纳时刻按真实单调时钟计时，重复请求不重置 | 超限 0010，停止接纳后排空 |
| MaxInputBytes/MaxOutputBytes/MaxNativeBytes | 正 long，宿主必填；展开/复制/暂存均计费；仅不可变数据可共享 | 0006；不能先展开再检查 |
| MaxGpuBytes/MaxQueuedCases | GPU 字节>=0，0禁用GPU；队列案例>=1；宿主必填，队列同时受输入字节限 | 0006/背压；禁止无限队列 |
| MaxConcurrency | >=1 且不超过组合根共享 permit 上限，默认1 | 不改 HALCON 全局线程；不机械等同 CPU 核数 |
| Runtime | Backend/Version/NumericProfile/EnvironmentDigest 必填；随机算法/状态在程序闭包登记，seed 可空 | seed 本身不证明确定性；声明不成立 0013 |
| OutputNamespace | 宿主授权的隔离逻辑域，1–128字符；允许分段路径但禁 `..`、绝对盘符/UNC、空段；端口映射实际位置 | 0005；Core 不拼接客户本机路径 |
| A/R/周期 | 策略逐字段给出有限非负 A/R 和正周期、单位；无通用容差默认值 | 0008；以 a=候选、b=基线计算 `abs(a-b)<=A+R*abs(b)` |
| ResourceUsage | 不可观察峰值用 null 并附 NotObserved；无取消的 CancelToDrainedNs 为 null/NotApplicable；非负实际纳秒 | 不以0伪装测量成功；排空未知不判性能通过 |

闭包 manifest 必须列出角色、必需性与传递引用，环依赖拒绝0004。保留模型资产自身 `model-core-jcs-v1` 或历史 digest 规则，Replay 不重算其身份。只检查本次执行真正读取的闭包：推理不因缺无关训练集/标签而拒绝。图像描述必须包含像素类型、宽高、通道、有效域引用、单位、坐标修订、来源与父引用；Region/XLD/3D 同样使用不可变 ContentRef 和自描述 schema，不传 native 句柄。

预检得到固定案例目录，按 `(ProductId, SideId, TargetId, FovId, CaseId)` ordinal 排序，缺身份用空排序键但不造关联；目录包含基线/候选案例的外连接，新增/缺失案例有明确 ID。IncludeUnresolved=false 时报告排除数和目录摘要。运行后不能增加/删除分母；原案例新增输出字段只增加 DifferenceItem，不增加案例数。

### 3.2 变更与比较值

ReplayChange.Path 为 RFC 6901 JSON Pointer，指向程序 manifest 登记的可变位置；Before/After 是可解析的不可变值文档，不能只给无从读取值的 hash。先验证 Before 等于父值，再以 After 构造候选闭包。重复/祖先子路径重叠、类型/单位不符拒绝0001/0004。Reason/Author 必填。ExactReplay/HistoricalExplain 的 Changes 为空；ChangeExperiment 非空；FlowSimulation 只在测试控制面使用场景。改变参数、模型、预处理、标定、裁剪/脱敏、后端、精度或线程配置均建立新实验；所有受影响下游结果失效。Checkpoint 只有与变更无关且状态/环境完整一致时可用。

ReplayValue 为判别联合。Valid 时 Boolean=规范 `true/false`，Text=原字符串，Int64=无前导零的十进制整数文本，Decimal=无指数/无多余尾零十进制文本，Float64=有限 JCS 数字文本，Artifact 仅 Artifact 非空；其余仅 CanonicalValue 非空。非 Valid 两个值字段均为空并保留原因 Tags；NaN/Inf 表示 NonFinite，不进入 JSON 数字。整数/decimal 精确比较，禁止先转 double；例如 `9007199254740993` 与 `9007199254740992` 必须 Changed。单位为策略注册代码（mm/px/rad/1 等），坐标 ID/修订同时存在或同时为空。

比较策略 manifest schema `replay-comparison-v2` 每条规则给出 RuleId、FieldId、Kind、ValueKind、Unit、CoordinateId/Revision、A/R、角周期、同维度转换的精确版本/引用、缺失政策和有效性要求。未列字段不可比较，不默认忽略。标签目录固定 Equal/Changed/StateEqual/MissingOriginal/MissingCandidate/Ambiguous/Invalid/UnitMismatch/CoordinateMismatch/DomainChanged/DiagnosticOnly；可附适配器命名空间诊断标签，不改变分类。任何不可比项使案例 CompletedIncomparable；其余任一变化为 CompletedChanged；全部可比且相等才 CompletedEqual；多候选在Artifact的replay-candidates-v2 schema中提供CandidateId、Role、Rank、Score(ReplayValue)、Value(ReplayValue)，集合按CandidateId唯一且ordinal排序；保留节点提供的稳定CandidateId与角色，身份集合变化或关联歧义单独标记，不挑最高分/最接近候选。双无效仅 StateEqual，不能算量测一致。整数/decimal 的 A/R 同样使用精确文本运算，Float64 溢出或非有限中间结果不可比较。角周期P>0时先在共同单位中计算u=((a-b)%P+P)%P，最短无向差min(u,P-u)，Delta保留有向归一值(u>P/2 ? u-P : u)，恰好半周期取正；再按冻结A/R比较。不先按UI位数舍入或自动换周期。

### 3.3 输出与分母

CaseResults 是按冻结目录顺序封存的分页 manifest 引用，包含每页 digest、首 CaseId、记录数、总数与 schema；每个目录项恰好一条结果。报告返回引用/汇总，禁止把百万案例构造成单一内存数组。分页读取 Offset 从0起，NextOffset=Offset+本页数，末页等于总数；页大小受读取预算且至少1。TargetIdentity 为[ProductId,SideId,TargetId,FovId,CaseId]的规范 JSON 文本，缺身份字段为原空字符串、不造关联，Definition/Coordinate修订仍在CaseInput保留并比较。原/候选摘要引用实际节点输出，未执行侧为空，不填上次结果。

Summary 六类和严格等于 Denominator。HistoricalExplain 无重算只记录可解释内容及 StateEqual/DiagnosticOnly，案例为 CompletedIncomparable；Completed 是操作成功封存，不代表数值一致或生产 PASS。部分节点失败仍可完成批报告，失败案例归 Failed；范围/全局隔离或封存故障使操作 Failed/Unknown。ProductionFactWrites 固定为0，NodeOutput.SideEffects两计数均非负，Core逐节点汇总校验，设备命令计数也必须为0；任何非零以 REPLAY-0018 隔离并停止接纳，保留诊断，不以报告计数证明权限隔离。

## 4. 服务、端口与最小调用顺序

Core 仅提供异步受预算入口；同步读取由宿主自行消费已封存报告，不提供阻塞 Run 包装。PreflightAsync 不执行算法、不登记操作，所有短期检查租约在返回前归还。它的 IsAccepted 仅表示该时刻可执行；StartAsync 必须重新验证权限/引用并原子接纳，不能信任过期预检。

```csharp
public sealed record ReplaySubjectBinding(string TenantId, string SubjectId,
    string AuthenticatedSessionId);
public interface IReplaySubjectScoped { ReplaySubjectBinding BoundSubject { get; } }
public enum ReplayAccessAction {
    Inspect, Start, QueryOperation, ReadCases, ReadEvents, ReadContent, Cancel, Export
}
public sealed record ReplayAccessResource(string? RequestId, string? OutputNamespace,
    ContentRef? Content, string? HostDestinationId);
public enum ReplayAccessDisposition { Allowed, Denied, Unavailable }
public sealed record ReplayAccessDecision(ReplayAccessDisposition Disposition,
    string PolicyRevision);
public interface IReplayAuthorization {
    ValueTask<ReplayAccessDecision> CheckAsync(ReplaySubjectBinding subject,
        ReplayAccessAction action, ReplayAccessResource resource, CancellationToken ct);
}
public enum ReplayLookupState { Found, NotFound, Unknown }
public enum ReplayReservation { Created, Existing, Conflict, Unknown }
public sealed record ReplayOperationLookupResult(string RequestId,
    ReplayLookupState LookupState, ReplayState? OperationState,
    ReplayResult? Result, ReplayError? Error, string? RequestDigest,
    long? Revision, string? ContractRevision, string? RecordSchema);
public sealed record ReplayStartResult(ReplayPreflightResult Preflight,
    IReplaySession? Session, bool OwnsExecution, ReplayOperationLookupResult Operation);
public interface IReplayService : IAsyncDisposable {
    ValueTask<ReplayPreflightResult> PreflightAsync(ReplayRunRequest request, CancellationToken ct);
    ValueTask<ReplayStartResult> StartAsync(ReplayRunRequest request, CancellationToken ct);
    ValueTask<ReplayOperationLookupResult> QueryOperationAsync(string requestId, CancellationToken ct);
    ValueTask<ReplayOperationLookupResult> RunAsync(ReplayRunRequest request,
        IProgress<ReplayProgress>? progress, CancellationToken ct);
    ValueTask<ReplayCasePage> ReadCasesAsync(ContentRef manifest, int offset,
        int pageSize, CancellationToken ct);
}
public interface IReplaySession : IAsyncDisposable {
    string ReplayRunId { get; }
    Task Completion { get; }
    IAsyncEnumerable<ReplayEvent> ReadEventsAsync(long afterSequence, CancellationToken ct);
    ValueTask CancelAsync(CancellationToken ct);
    ValueTask RequestCloseAsync(CancellationToken ct);
    ValueTask<ReplayDrainStatus> DrainAsync(TimeSpan waitBudget, CancellationToken ct);
}
public sealed record ReplayDrainStatus(ReplayState State, bool ResourcesReleased,
    ImmutableArray<ReplayError> Errors);
public sealed record ReplayEvent(string ReplayRunId, string RequestId, long Sequence,
    long StateRevision, string Kind, ReplayState State, DateTimeOffset RecordedUtc,
    string SourceId, string? CaseId, string? NodeId, string? ErrorCode);
public interface IReplaySessionRetention {
    void Retain(IReplaySession session);
}
public interface IReplayContentLease : IAsyncDisposable {
    ContentRef Reference { get; }
    ValueTask<System.IO.Stream> OpenReadAsync(CancellationToken ct);
}
public sealed record ReplayEvidenceIndex(ContentRef Directory, int CaseCount,
    string DirectoryDigest, ImmutableArray<MissingDependency> Missing);
public interface IReplayEvidenceReader : IReplaySubjectScoped {
    ValueTask<ReplayEvidenceIndex> ResolveScopeAsync(EvidenceClosureRef evidence,
        ReplayScope scope, ResourceBudget budget, CancellationToken ct);
    IAsyncEnumerable<ReplayCaseInput> ReadCasesAsync(ContentRef directory, CancellationToken ct);
    ValueTask<IReplayContentLease> AcquireAsync(ContentRef reference, CancellationToken ct);
}
public sealed record ReplayResolvedProgram(ContentRef Graph,
    ImmutableArray<ContentRef> Dependencies, string EnvironmentDigest);
public interface IReplayProgramResolver : IReplaySubjectScoped {
    ValueTask<ReplayResolvedProgram> ResolveAsync(ProgramClosureRef program,
        ImmutableArray<ReplayChange> changes, ReplayRuntimeProfile runtime, CancellationToken ct);
}
public sealed record ReplayEngineCapabilities(string AdapterId, string Revision,
    bool CooperativeCancel, bool IsolatedWorker, bool NativeUsageObservable,
    bool GpuUsageObservable, ImmutableArray<string> SupportedSchemas);
public sealed record ReplayExecutionContext(string ReplayRunId, string RequestId,
    long Generation, ReplayCaseInput Case, ReplayResolvedProgram Program,
    ReplayCutPoint? CutPoint, ResourceBudget Budget, ReplayRuntimeProfile Runtime);
public sealed record ReplayFieldValue(string FieldId, ReplayValue Value);
public sealed record ReplaySideEffects(long ProductionFactWrites, long DeviceCommandWrites);
public sealed record ReplayNodeOutput(string NodeId, string NodeRevision,
    ImmutableArray<ReplayFieldValue> Fields, ImmutableArray<ContentRef> Artifacts,
    ImmutableArray<ReplayError> Errors, ReplaySideEffects SideEffects);
public interface IReplayCaseExecution : IAsyncDisposable {
    Task<ImmutableArray<ReplayNodeOutput>> Completion { get; }
    ReplayResourceUsage GetResourceUsage();
    ValueTask RequestCancelAsync(CancellationToken ct);
    ValueTask<ReplayDrainStatus> DrainAsync(TimeSpan waitBudget, CancellationToken ct);
}
public interface IReplayExecutionEngine : IReplaySubjectScoped {
    ReplayEngineCapabilities Capabilities { get; }
    ValueTask<IReplayCaseExecution> StartCaseAsync(ReplayExecutionContext context, CancellationToken ct);
}
public interface IReplayComparisonPolicy : IReplaySubjectScoped {
    ValueTask<ImmutableArray<DifferenceItem>> CompareAsync(ComparisonPolicyRef policy,
        ReplayCaseInput input, ImmutableArray<ReplayNodeOutput> candidate, CancellationToken ct);
}
public sealed record ReplayReservationResult(ReplayReservation Disposition,
    ReplayOperationLookupResult Operation);
public interface IReplayResultStore : IReplaySubjectScoped {
    ValueTask<ReplayReservationResult> ReserveAsync(ReplayRunRequest request,
        string requestDigest, string frozenClosureDigest, ContentRef caseDirectory,
        int denominator, CancellationToken ct);
    ValueTask<ReplayOperationLookupResult> QueryByRequestIdAsync(string requestId, CancellationToken ct);
    ValueTask<ReplayOperationLookupResult> RecordStateAsync(string requestId,
        long expectedRevision, string expectedContractRevision,
        ReplayState next, CancellationToken ct);
    ValueTask AppendCaseAsync(string requestId, ReplayCaseResult result, CancellationToken ct);
    ValueTask<ContentRef> SealCasesAsync(string requestId, int denominator, CancellationToken ct);
    ValueTask<ReplayCaseLookup> QueryCaseAsync(string requestId, string caseId, CancellationToken ct);
    ValueTask AppendEventAsync(ReplayEvent item, CancellationToken ct);
    IAsyncEnumerable<ReplayEvent> ReadEventsAsync(string requestId, long afterSequence,
        CancellationToken ct);
    ValueTask<ReplayOperationLookupResult> SealResultAsync(string requestId,
        long expectedRevision, string expectedContractRevision,
        ReplayResult result, CancellationToken ct);
    ValueTask<ReplayCasePage> ReadCasesAsync(ContentRef manifest, int offset,
        int pageSize, CancellationToken ct);
}
public sealed record ReplayCaseLookup(ReplayLookupState State, ReplayCaseResult? Result,
    ReplayError? Error);
public sealed record ReplayServiceOptions(TimeSpan IoTimeout, int MaxEventBuffer,
    long MaxEventBytes, int MaxReadPageSize, long MaxReadBytes);
public interface IReplayPermit : IAsyncDisposable { string RequestId { get; } }
public interface IReplayResourceCoordinator {
    ValueTask<IReplayPermit> AcquireAsync(string requestId, ResourceBudget budget, CancellationToken ct);
}
public interface IReplayClock {
    DateTimeOffset UtcNow { get; }
    string BootId { get; }
    long MonotonicNs { get; }
}
```

**端口操作协议：** 已知字段/依赖/权限错误返回结构化 ReplayError；服务 StartResult.Preflight.IsAccepted=false、Session=null、OwnsExecution=false，Operation=NotFound/Rejected诊断（只有有权主体的已知校验错误；授权拒绝按§4.0 Unknown/0005脱敏），不留持久执行记录。端口无法返回结构化结果时以模块内 ReplayPortException(Error) 传播（该类型继承 Exception，公开只读 ReplayError Error，构造参数 ReplayError）；Core 捕获并按错误级别转为预检/案例/操作结果。调用前 token 已取消抛 OperationCanceledException、无新登记；接纳后的取消按本节处理，不用异常伪装终态。不可预期 CLR 异常映射0007，诊断保留内部异常引用，事件/协议只带稳定代码；存储回执不明映射0014。

**接纳/幂等：** Start先校验请求结构并按§4.0检查本次主体Start/Query权限，再计算RequestDigest→查询绑定租户原RequestId（同摘要既有操作仅返回，不重新解析已撤销模型；不同摘要0016）；权威NotFound后解析闭包/目录→校验预算能力→非阻塞Acquire资源permit→Reserve再次原子确认。Reserve 必须原子以 RequestId 比较摘要、保存原 ReplayRunId/闭包/目录：Created 才能执行；Existing 返回原会话或原状态，不能再执行；Conflict 为0016；Unknown 为0014且不执行。RequestDigest 排除 RequestId/ReplayRunId/当前时间，包含输出逻辑域、用途、完整预算、变更及所有执行语义；同 RequestId 不同预算也是冲突。相同摘要换新 RunId仍返回原 RunId。不同 RequestId 即新工程操作。Operation Store 的读写与状态修订为单 Owner；RecordStateAsync 用 expectedRevision CAS，冲突不重放。已授权但Store不可查询时LookupState=Unknown/0014，授权失败为Unknown/0005，不是NotFound；Found可以是非终态且Result=null；Revision/版本字段按§4.2同快照回读。Unknown 不意味着必须重复计算。

**会话/取消：** Start token在Created之前撤销准备，只有Created接纳者的token在之后成为该操作取消来源；Existing调用者token只撤销这次附着/观察，不能给原运行添加取消源。Created返回OwnsExecution=true且Session非空；Existing可返回同主体观察Session或Session=null，OwnsExecution=false；拒绝/Conflict/Unknown也为false。观察Session仅绑定本次实例和主体，不共享另一主体的句柄。Completion为无数据Task信号，仅在真实收尾/报告事务已知或未知结果后完成；不是读取权限，await后必须QueryOperationAsync获取当前已授权快照。服务生命周期异常可使信号以无客户内容的通用ReplayPortException faulted，Host仍须finally关闭句柄，不以fault证明资源释放。

RunAsync先Start；Session=null直接返回已授权Operation；有Session则等Completion后Query，取消后仍等真实收尾；finally关闭本次句柄，不能取消Existing原运行。Completion.WaitAsync(waitToken)只取消等待，不取消执行。CancelAsync是用户动作：每次校验Cancel授权，幂等；调用ct只撤销发送/等待，不撤销已接受取消。RequestCloseAsync是原创建句柄的安全生命周期动作，不读取报告/不新增执行：拥有者停接纳并请求停止，观察句柄仅撤订阅；权限撤销不阻安全收尾。关闭已开始后内部继续至真实释放，即使调用ct取消观察。DrainAsync.waitBudget为本次有限正真实单调观察期，ct只撤观察；未释放返回false/0010，未知不当释放。无Inspect授权时只回Released布尔、Draining或ResourcesReleased生命周期状态及通用错误，不给案例、阶段细节或资源诊断。

DisposeAsync先RequestClose：拥有者等待真实归还和报告IO观察结束，底层可能长期未完成；观察句柄只等自身订阅/回调退出，不取消或等待别人计算结束。两类句柄关闭均幂等。Host必须在Factory前按§12.2预留进程Root槽，原Dispose Task也归Root强持；调用栈只有限观察。IReplaySessionRetention仅保留v0.3旧入口，必须是同一预留Root的兼容facade，不能在关闭时另申请槽；Retain失败不返回无限等待本地Dispose，改查原Root确认原有持有关系，关闭Task继续归Root，禁止丢句柄。UI退出不得在Dispatcher同步阻塞，也不能关闭仍拥有在途资源的服务/进程。

**资源/引擎：** Reader lease 只保留内容，OpenReadAsync 每次创建独立只读流，消费者先关流再归还租约，归还幂等且不得发生在执行中。Engine 组合根显式注入同 Reader 和已允许的本地算法注册表；Graph schema 只列 NodeId/Revision/输入依赖/参数引用，不包含 DLL路径或脚本。StartCase 返回执行对象后引擎拥有该案例 native/GPU/回调，Completion 不证明释放；Core 必须 Drain 再 Dispose。Start失败前全部资源由引擎自回收；产物引用成功封存后归 Store持有。Reader目录与闭包资产在预检后至接纳期间须在短保持lease内稳定；接纳成功后保持转到会话，禁止目录遍历期间源对象被删除。Core 持有的输入租约必须晚于引擎排空归还。GetResourceUsage返回截至调用时的累计/峰值不可变快照，Drain后值完整，之后不改变；不可观测字段null。Core本身计读取/复制/队列/permit并聚合适配器用量，同一共享分配按唯一allocation Owner计一次；并发峰值由资源协调器同时水位计数，不相加各案例不同时间峰值作实际峰值。未观察并发水位时报告NotObserved，不判预算已满足。不可观察 native/GPU 时不能宣称满足严格字节上限；只允许已配置隔离 worker 的进程资源限制或拒绝0013。Store AppendCase 按 RequestId+CaseId+内容摘要幂等，不同摘要0016；SealCases 验证固定目录每项恰好一次，无半写可见页。封存/响应丢失先查询，不重 Append/Execute。

**进度/事件：** ReadEventsAsync 从 afterSequence 独占之后读取，不传 native资源；ct撤订阅不取消操作。事件保留到宿主配置保留期，失效起点返回0017并要求 Query快照；禁止无界内存事件缓存。事件/进度投影与执行解耦，有界邮箱仅合并 Progress；不可合并状态/封存/排空事件由 Store/隔离 spool保持，慢订阅者不阻塞 native退出。IProgress 回调异常只记诊断，不改变运行结果。

### 4.0 可信主体绑定、逐入口授权与无泄漏查询

ReplayService构造追加ReplaySubjectBinding subject、IReplayAuthorization authorization（完整顺序见§12）。TenantId/SubjectId/AuthenticatedSessionId是可信组合根从已认证宿主会话取得的稳定ID，不是ReplayRunRequest字段，不从UI/文件/JSON/环境全局变量或Author推定；不包含凭证本体。绑定构造后不可改，切换登录主体新建服务/控制器并撤旧显示订阅。每实例Reader/Resolver/Engine/Comparison/Store均实现IReplaySubjectScoped并返回相同BoundSubject；构造ReplayService时逐一检查与subject三字段ordinal完全一致，缺字段或不一致构造失败0005，不初始化执行/查询。它们是该绑定的受控scope facade；底层物理存储/permit可共享，裸未授权Store/Reader不能交UI或不可信插件。测试Host显式注入固定主体与确定性授权替身，不能以生产默认Allowed代替。

IReplayAuthorization.CheckAsync由宿主授权适配器提供当前会话有效性、动作、对象所属租户/可见性与范围政策。Allowed须来自非空PolicyRevision且匹配本次主体/资源；Denied/Unavailable/过期会话/错误/取消未完成都不许可继续读取或提交。已知否决与授权不可确认统一0005安全拒绝，不回退缓存的Allowed。每次Check使用ServiceOptions.IoTimeout有限等待，不能拿历史运行时许可当现在许可。Core只消费结果，不创建权限角色或覆盖授权模块的事实；授权Decision不是生产放行。

| 公开入口/输出面 | 动作与精确对象 | 固定顺序 |
|---|---|---|
| PreflightAsync | Inspect：请求逻辑域、Evidence/Program/Policy引用及其实际读取依赖 | 授权后解析，逐引用受控Reader再次检查；无权限不返回缺项/目录摘要 |
| StartAsync、RunAsync | Start：RequestId、OutputNamespace和本次闭包；既有报告另需QueryOperation/ReadCases | Start权限通过后才按租户键查询/Reserve；同载荷只幂等返回，绝不因缺Read而重执行 |
| QueryOperationAsync；Store Query/Reserve回执 | QueryOperation：绑定租户中的原RequestId/操作Owner与范围 | 请求级授权后，受控Store在同次查询内检查对象ACL并返回快照；请求在不可见scope外时，不论ID实际存在与否均为同一0005脱敏响应；只有有权scope内权威确认不存在才NotFound |
| ReadCasesAsync；Store页/QueryCase/源Reader流 | ReadCases或ReadContent：完整ContentRef及其授权所属操作/资产 | 每页/每次OpenRead前检查，引用可解析/hash已知不等于可读；无法证明租户/操作归属拒绝0005 |
| IReplaySession.ReadEventsAsync与进度投影 | ReadEvents/Inspect：本句柄绑定RequestId | 建订阅和每次交付前查当前授权；撤销停止交付并撤订阅，不通过迟到回调泄漏结果 |
| Session.Completion | 无数据完成信号 | 不附带Result/错误细节/revision；报告须后续授权Query |
| Session.CancelAsync；Workbench Controller.CancelAsync | Cancel：绑定租户/原RequestId，必须本主体拥有或明确被授委托 | 不允许UI跨主体传句柄取消；服务再校验，不能以CanCancel投影代授权 |
| Session.RequestCloseAsync/DrainAsync/DisposeAsync、Service.DisposeAsync | 原句柄/本服务的安全收尾 | 允许权限撤销后的资源归还；不读取或导出生产/客户内容，Drain输出按当前Inspect授权脱敏 |
| Controller.Query/Preflight/Start/ReadCases | 同上，控制器与Core同主体实例 | 参数不能另携SubjectId改变scope；ReplayUiPermissions只决定呈现 |
| Controller.ExportAsync、影像显示适配器 | Export：RequestId、精确report/证据引用、HostDestinationId；显示另需ReadContent | Export先查已授权封存报告再逐对象/目标授权；取消/撤权停止后续交付，暂存输出按宿主导出Owner恢复 |

操作唯一键为(TenantId,RequestId)，Record保存原Owner与OutputNamespace；同租户其它主体也不能仅凭ID查询。确需委托查询，授权适配器必须显式确认对象可见性，禁止“同租户一律允许”。Reader的ContentRef到租户/操作/资产ACL关联由其scope facade核对，不能靠用户报称的OutputNamespace或AssetId直接拼存储路径。执行阶段内部Core/Store写回使用接纳时绑定的唯一执行Owner能力，只允许原操作收尾，不能借它开新操作或提供撤权后的查询。原创建句柄/资源Owner安全关闭不需要用户读取许可，但该收尾能力不向普通Host提供CAS写入口。权限撤销按§8停新案例/安全排空；Owner身份不写回请求hash，也不改变已封存报告，操作记录保留绑定审计。

拒绝Query/Start既有对象返回LookupState.Unknown、OperationState/Result/RequestDigest/Revision/ContractRevision/RecordSchema全null及通用0005；错误Path/Details不含Owner、案例、闭包或实际存在性。授权通过且Store权威确认不存在才NotFound；Store不可达为Unknown/0014，禁止与拒绝混作NotFound。授权检查与结果交付之间须由scope facade校验会话/政策仍有效；传输前撤权则拒绝整份快照；已合法交付的不可变内容不能声称可被追溯撤回。新订阅/新页/导出持续交付仍重新检查。OpenReadAsync返回scope受控只读流，仅支持异步内容读取；每次ReadAsync在有限授权检查后交付本次字节，同步Read/ReadByte不支持，不用同步阻塞CheckAsync。Seek/Position只在授权对象范围内，不切到其它资产。撤权终止后续读并关闭观察流，底层仍在使用的lease须等Engine真实退出再归还；已交native的合法缓冲不假称可追溯清除。Core不跨主体缓存结果或快照；UI切主体清旧客户投影和显示lease，不删除源证据。

### 4.1 内部 manifest 的序列化结构与持久回执

以下为模块自己的schema语义，序列化按§9.1，不复制平台证据事实：

```csharp
public sealed record ReplayDependency(string Role, ContentRef Content, bool Required);
public sealed record ReplayClosureManifest(string Schema, ImmutableArray<ReplayDependency> Dependencies);
public sealed record ReplayInputBinding(string Name, string? FromNodeId,
    string? FromFieldId, ContentRef? ExternalInput);
public sealed record ReplayGraphNode(string NodeId, string NodeRevision, string AdapterNodeType,
    ImmutableArray<ReplayInputBinding> Inputs, ContentRef Parameters,
    ImmutableArray<ContentRef> ExecutionDependencies, ImmutableArray<string> OutputFieldIds);
public sealed record ReplayGraphManifest(string Schema, ImmutableArray<ReplayGraphNode> Nodes,
    string EnvironmentDigest);
public sealed record ReplayCaseDirectory(string Schema, int Count, int ExcludedUnresolved,
    ImmutableArray<ContentRef> Pages);
public sealed record ReplayCaseDirectoryPage(string Schema, int Offset,
    ImmutableArray<ReplayCaseInput> Items);
public sealed record ReplayResultPageDescriptor(int Offset, int Count,
    string FirstCaseId, ContentRef Page);
public sealed record ReplayCaseResultManifest(string Schema, int Count,
    ImmutableArray<ReplayResultPageDescriptor> Pages);
public sealed record ReplayCaseResultPage(string Schema, int Offset,
    ImmutableArray<ReplayCaseResult> Items);
public sealed record ReplayComparisonRule(string RuleId, string FieldId,
    ReplayComparisonKind Kind, ReplayValueKind ValueKind, string Unit,
    string? CoordinateId, string? CoordinateRevision, string? AbsoluteTolerance,
    string? RelativeTolerance, string? AnglePeriod, ContentRef? UnitConversion,
    string MissingPolicy, bool RequireValid);
public sealed record ReplayComparisonManifest(string Schema,
    ImmutableArray<ReplayComparisonRule> Rules);
public sealed record ReplayRuntimeManifest(string Schema, ReplayRuntimeProfile Profile);
public sealed record ReplayOperationRecord(string Schema, ReplaySubjectBinding Owner,
    string OutputNamespace, string ContractRevision, string RequestId, string ReplayRunId,
    string RequestDigest, string FrozenClosureDigest, ContentRef CaseDirectory,
    int Denominator, long Revision, ReplayState State, string BootId,
    long AcceptedMonotonicNs, long ConsumedTicks, ContentRef? CaseResults,
    ContentRef? Report, ImmutableArray<ReplayError> Errors);
```

Schemas精确为replay-closure-v2、replay-graph-v2、replay-case-directory-v2、replay-case-directory-page-v2、replay-case-results-v2、replay-case-result-page-v2、replay-comparison-v2、replay-operation-v3；基线节点值文档schema=replay-node-outputs-v2（ImmutableArray<ReplayNodeOutput>），变更值schema=replay-value-v2（ReplayValue）。每ContentRef.Schema必须与解析对象Schema一致。源closure可由明确reader转换为模块只读目录，保留原引用；不覆盖原源Schema。图像/Region/3D等native对象schema由其证据适配器提供，Core只核完整引用，实际执行适配器必须支持其schema。

Asun.Modules.Replay.ReplayService为sealed类，实现IReplayService和IAsyncDisposable，公开构造参数见§12；DisposeAsync先停本实例接纳，只请求本实例Created拥有的运行停止并等真实释放/报告IO观察结束；Existing观察句柄仅撤订阅，不取消原运行，不关闭外部共享Reader/Store/协调器。ReplayCanonical为public static类，四个公开方法均返回string且参数形状见§9.1；本页是声明规格不留NotImplemented占位实现。

Graph是DAG；NodeId唯一，输入绑定Name唯一，FromNodeId/FromFieldId同时存在且指向前驱，或ExternalInput单独存在。二者互斥，环/空图/悬空依赖0004；Nodes按拓扑顺序，同层NodeId ordinal。Parameters和ExecutionDependencies是完整引用；AdapterNodeType只查已注册允许节点，不反射任意DLL。输出FieldId唯一，DifferenceItem.FieldId使用节点ID+节点修订+FieldId的规范JSON元组文本，节点值以NodeId/Revision/FieldId稳定标识，重复/额外输出0013，不按顺序配对。Resolver不能忽略Changes；实际执行用候选Graph，Comparison读原Baseline。HistoricalExplain只验证原可读结果/证据引用，不解析执行Graph/模型或要求Engine可用；Program/Runtime原描述仅来源投影，不宣称本次执行环境。

目录/结果页Count与Items一致、Offset连续不重叠、Pages摘要完整、每CaseId唯一且符合Scope已冻结顺序；以页流式遍历，MaxCases先按Count拒绝，实际计数/hash不符0002。候选缺输入案例在目录标Missing，不返回空结果。Comparison MissingPolicy本版为ReportIncomparable，RequireValid=true；Exact容差/周期为空，Tolerance数值A/R必填，角字段周期可空；UnitConversion只能是宿主已注册公开比较适配器的精确转换引用，未支持0013，不临时推算标定或按UI格式转换。DiagnosticOnly不能产生CompletedEqual。

Reserve原子固定目录/分母/原run/request摘要、Revision=1/Running和唯一执行Owner；跨进程Created只授予一个调用者执行，Existing/Conflict/Unknown持有的临时permit立即归还。预查Found仍以Reserve或权威快照确认，已有终态不申请计算permit。Created响应丢失先查原ID，能查到Running不等于新调用者可以执行；重启发现旧Owner死亡，由Store恢复能力核封存案例/进程退出并标Unknown，Core不抢旧执行。恢复计算用新RequestId与完整Checkpoint，引用旧资产，不改原记录。

AppendCase回执丢失用QueryCaseAsync；Found核内容摘要后继续，NotFound确认未封存才重复Append已持有结果，Unknown停封存/0014；禁止重复StartCase。SealCases同内容反复返回同ContentRef，不同内容0016。RecordState修订冲突按§4.2查询同版本权威Revision，不从事件序号推测；SealResult原子引用完整Report、终态及摘要，回执不明先Query。报告事务流/连接归外部Store Owner，不属于已释放的Core执行资源，IO耗时和资源另计；ResourcesReleased后Core不重新获取证据/native/permit，只提交不可变小报告。不能以Core已释放冒称Store IO耐久完成；Completion仍等报告事务结果。Store AppendEvent同Sequence同内容幂等，不同内容0016；ReadEvents游标缺失0017。不具备持久Store时只声明进程内查询，不承诺跨重启恢复。

IReplayClock是Core期限/测量时钟，生产实现基于Stopwatch单调读数；Simulator固定可推进时钟只验证软件deadline，外层真实超时保护；Runner虚拟Clock不用于真实性能。ReplayServiceOptions的IoTimeout及各限均有限正且宿主必填。ReadCases同时受MaxReadPageSize/MaxReadBytes限制；非末页NextOffset无进展0002、越界offset/size0001。查询/读取/导出以§4.0可信主体scope和授权端口逐次校验，撤销不能靠缓存绕过；只读等待期限不修改原运行Deadline。

### 4.2 Revision 权威回读与 CAS 恢复

ReplayOperationLookupResult是一次权威原子快照，不把Report、State、Revision拼自不同查询。Found必填RequestDigest、Revision>=1、ContractRevision、RecordSchema及OperationState；Report存在则Result.RequestId/ReplayRunId/FinalState必须与同快照操作一致。当前新记录RecordSchema=replay-operation-v3、ContractRevision=replay-contract-v3；Report/CaseResults保持自身精确schema。NotFound/不可确认Unknown/授权拒绝时Revision和版本字段为null，不能猜0、从事件Sequence推修订或用本地最后值CAS。资源已释放但Store不可达的Completion仍仅信号；后续Query Unknown不得生成权威Revision。

Reserve.Created回原子Revision=1/Running快照；Existing回当前快照。RecordStateAsync/SealResultAsync成功均返回提交后的快照，Revision=expectedRevision+1，checked溢出拒绝0016；报告内容与最终状态同事务提交，不能先提交报告再另加终态。expectedContractRevision必须匹配该记录并为写适配器支持版本，版本不匹配0013，revision不匹配0016；失败不改源记录。RecordState只允许§5合法前迁，不能将终态或他人Owner的记录改写。SealResult先校验契约/执行Owner，再检查已封存相同摘要；同内容幂等重复调用即使expectedRevision因该次提交已过期，也返回原终态/原Revision，不再次递增；不同报告或状态0016。报告不可变，事件重送/游标读取不改操作Revision；StateRevision引用该次已提交Revision。

仅唯一原执行Owner可恢复CAS，外部Host拿到Revision也不获得写权限。顺序：Query原RequestId→检查Found且版本可写→核对同一RequestDigest/闭包/执行Owner和当前状态→用该Revision/ContractRevision提交合法下一状态→保存返回快照。若0016或IO回执丢失，重新Query：已达相同目标且报告digest相同，则采纳原提交回执；状态变动须按§5重评，不盲目加一/重试旧状态；Unknown或NotFound不能CAS、更不能重跑；发现不同载荷/报告冲突保留原记录并诊断。跨进程旧Owner死亡仍只按§4.1查询/监督恢复Unknown，不让查询Host抢执行。

兼容读取须按RecordSchema与ContractRevision二元组选择显式decoder。原replay-operation-v2/replay-contract-v2记录可从其已有Revision与Owner的可信存储ACL映射成只读Lookup；缺可证明Owner/Revision/版本任一项返回0013且不披露report，不填默认值。旧报告通过原精确decoder投影，保留原报告digest；不改为v3。v3写适配器不CAS旧记录，需迁移时由获授权Store Owner建立新记录/映射并保留旧资产，本Host只消费既有结果。请求/Scenario/Result仍使用replay-jcs-v2，ContractRevision变更自然进入请求投影；不能重算旧hash冒充v3。当前版本变更为尚未实现模块契约收口，不声称已完成迁移或兼容运行验证。

## 5. 状态、事件与错误

### 5.1 单一状态 Owner 与封存顺序

Core 会话协调器是状态迁移的唯一写者，Store 保存同一 revision；适配器、UI 和回调只报观察，不写状态。预检没有持久执行副作用：

```text
Created -> Preflighting -> Ready
                     \-> Rejected
Ready --atomic Reserve.Created--> Running
Running -> Completing -> Draining -> Drained -> ResourcesReleased
       -> [停止原因] ---^                                  |
                                                        v
                                                ResultSealed -> Completed/Cancelled/Failed
                                                        \----> Unknown（回执无法证明）
```

CancelRequested、FailureObserved、UnknownObserved 是 Running/Completing 的停止原因状态，随后进入 Draining；禁止把仍占用资源的操作直接跳成终态。历史解释也经同样流程，但不调用 Engine。Drained=执行任务、IO、回调和 GPU 工作已退出；ResourcesReleased=Core/适配器拥有的租约、流、缓冲、订阅、permit 均归还；两者不能混写。Drain 未知保持 Draining，并可在查询中报0014，不能因请求时限到达就返回“释放完成”。

**统一收尾顺序：** 关闭接纳 → 完成或明确标注每条案例 → AppendCase/SealCases（工程内容封存）→ 等全部执行和案例 IO/回调结束 → Drained → 释放租约/permit → ResourcesReleased → 生成包含最终资源摘要的 ReplayResult → SealResult（报告及操作终态原子提交）→ ResultSealed/终态事件 → Completion。SealCases 不是报告终态；不会在 native 使用资源时读取虚假的最终峰值。ResultSealed 只表示报告封存有权威回执，不先于排空。封存期间只用独立有限 IO 预算（由宿主储存 Profile 注入），不能复用已取消执行 token；执行 Deadline 不承诺报告 IO/排空已结束。

终态规则：
- Completed：工程批报告完整封存，允许案例 Changed/Incomparable/Failed，不能解释为生产 PASS。
- Cancelled：取消在终态提交前被接受且无更高优先级原因；已经完成的案例保留，未启动/已中止案例 CancelledOrNotRun。
- Failed：已知全局执行、期限、隔离或封存失败；deadline 排空后为 Failed+0010，不偷换 Cancelled。局部节点 Failed 不一定使整操作 Failed。
- Unknown：执行/封存回执不明，且已证明所有资源释放，允许 Result=null。Store 不可达时本地完成信号不提供快照；后续已授权查询返回LookupState.Unknown/OperationState.Unknown（如资源状态只能在本地确定，则权威OperationState仍null），不能伪装持久终态已提交。
- Rejected：接纳前校验失败，无执行登记；已有 RequestId 冲突不改原操作，返回0016。

并发取消与结果提交按同一会话串行门处理：SealResult 原子提交是终态线性化点；协调器在提交事务期间锁定停止原因，取消与提交按该串行门排队，不发生“序列化Completed后接受取消再提交旧报告”的竞态。提交后 Cancel 只查询终态不改变它；提交前优先级固定 Unknown > 隔离/全局失败/Deadline > 已接受取消 > 正常完成。迟到停止请求不得改不可变报告。因排空/资源归还不明而无法提交时保持 Draining，服务保留所有权；Core 不以 Dispose 或等待取消绕过门。

### 5.2 事件目录与投影

ReplayEvent.Kind 仅允许下面注册目录，ReplayState 同 §3，不另造 Failure/NotReady 状态：

| 路径 | 按序观察 |
|---|---|
| 接纳前 | RequestReceived → PreflightStarted → DependencyChecked → ScopeFrozen → Ready；失败则 Rejected |
| 接纳成功 | Accepted → CaseStarted/NodeCompleted/CaseCompared/Progress（逐案例）→ CompletionStarted → IntakeStopped → CaseResultsSealed → DrainingStarted → Drained → ResourcesReleased → ResultSealed → Completed |
| 取消/失败/未知 | CancelRequested/FailureObserved/UnknownObserved → IntakeStopped →（已完案例保留、未完项标注）→ CaseResultsSealed? → DrainingStarted → Drained? → ResourcesReleased? → ResultSealed? → Cancelled/Failed/Unknown |

CaseResultsSealed 是内容事件，不是 ReplayState；状态仍 Completing/Draining。报告 IO 已知失败可不出现 ResultSealed，以 Failed 明确无报告；回执未知事件为 UnknownObserved/Unknown。终态事件在 Store 提交后才能发布，失败无持久回执仅本地查询/诊断，不发布“已封存”事件。进度可合并；状态/封存/排空不能合并。每运行 Sequence 从1单调递增，StateRevision 仅迁移时增长；SourceId 是适配器稳定 ID，不用线程 ID 当顺序。UTC 只显示，真实并发记录按协调器接收顺序，不声称跨次相同。

ReadEventsAsync 可以至少一次重送，消费者按 (ReplayRunId,Sequence) 去重。每次执行 generation 递增，回调必须关联 RequestId/CaseId/NodeId/generation；旧 generation 的迟到消息仅记诊断，不更新案例、计数、缓存或租约。断连后 QueryOperationAsync/ReadCases 恢复快照；不存在“重新订阅即重新运行”。进度回调异常、慢 UI、已关闭页面都不能阻碍真实排空。

### 5.3 稳定错误码与恢复身份

| 代码 | 含义 | 恢复 |
|---|---|---|
| REPLAY-0001 | 字段/版本/值格式或变更路径无效 | 修请求，新 RequestId |
| REPLAY-0002 | 所需证据缺失、损坏、长度/hash 不符 | 补齐新闭包，新请求；原报告保留 |
| REPLAY-0003 | 所需程序/模型/标定/后端版本不可用或撤销 | 明确新实验，不自动 latest |
| REPLAY-0004 | 空范围、歧义、闭包/切点不完整 | 修范围/闭包，不猜关联 |
| REPLAY-0005 | 权限/逻辑域不允许或撤销 | 宿主重新授权，不升权重试 |
| REPLAY-0006 | 资源/队列/案例预算超限 | 新预算/批次新请求，不截断 |
| REPLAY-0007 | 已知节点或执行错误 | 默认不自动重试节点；完整封存案例可按恢复规则复用 |
| REPLAY-0008 | 策略、单位、坐标或支持域不可比 | 保留不可比较项，新策略新请求 |
| REPLAY-0009 | 操作取消已接受 | 按§4.0当前主体授权查询原操作，等待排空 |
| REPLAY-0010 | 执行期限或观察排空期限到达 | 查原操作，不把 native 当已退出 |
| REPLAY-0011 | 已知输出封存失败 | 查原回执；明确未提交后才修复 IO，不重执行节点 |
| REPLAY-0012 | 检查点不完整/不兼容 | 从合法切点新尝试 |
| REPLAY-0013 | 适配器/schema/能力不支持 | 明确更换适配器/范围，不降级 |
| REPLAY-0014 | 执行/封存/查询状态未知 | 原 RequestId 查询；不得盲重放 |
| REPLAY-0015 | 未注册场景事件/fault/版本 | 预检拒绝，修场景 |
| REPLAY-0016 | 相同幂等键不同载荷或状态 revision 冲突 | 保留原记录，定位冲突；不能覆盖 |
| REPLAY-0017 | 事件游标失效/不可恢复缺页 | 查询权威快照，不猜丢失事件 |
| REPLAY-0018 | 生产副作用/隔离边界被突破 | 停止接纳、排空和审计；无自动重试 |

Retryable 只表示同一只读/幂等查询在明确策略下可再尝试，不授权新 Execute。业务错误以 ReplayError 返回；Details 为稳定诊断键/ID，不向操作员直接显示异常栈、凭证或客户敏感值。查询 Store 暂不可达为 Unknown；权威确认没有记录才 NotFound。六类案例始终保留，Unknown 不折算 Failed、Cancelled 或相等。

## 6. 四种运行用途

| 用途 | 允许输入 | 结果含义 | 禁止结论 |
|---|---|---|---|
| 历史解释 | 原结果、规则快照、原证据 | 当时保存内容及缺项 | 不称重新计算一致 |
| 原版本重放 | 原程序、参数、模型、输入和环境闭包 | 在声明策略下的精确/容差/不可比较 | 不覆盖原事实 |
| 变更试验 | 父历史引用 + 非空变更集 | 候选与原基线差异 | 不归因于原生产机判 |
| 控制流程模拟 | 明确模拟端口、虚拟时间和事件 | 软件协议/故障行为 | 不代表真实采集、节拍或设备安全 |

预检必须先冻结范围、切点、依赖、变更、比较策略、资源预算和输出命名空间。缺少上游中间状态时只能报告差异发生在两个可观察切点之间，不得定位到未保存节点。

### 6.1 合成输入与回放派生输入的来源链

Replay 可以消费外部生成器的固定输出，但不生成数字孪生、不随机化物理模型、不训练模型，也不判断 Sim-to-Real 资格。以下元数据由证据读取适配器从原闭包提供，不在本页另建平台 Evidence Schema。

- 每个输入分别记录原始来源类别（`RealCapture`、`Synthetic`、`EngineeringSpecimen`、`Unknown`）和派生链（包括 `FaultInjected`、`ReplayDerived`）。这些维度不能互相覆盖：真实采集帧经故障注入后仍须保留真实父引用；合成帧回放后仍为合成来源。客户/制程对样件的解释由调用方提供，Replay 不推断。
- 对声明为 `Synthetic` 的输入，闭包必须包含生成器 ID/精确版本或 hash、原始生成参数及单位、随机算法与 seed/状态、物理假设、域随机化范围、原生成输出 digest 和父引用。未启用随机化时显式记为不适用，不伪造 seed。已有输出可读不表示生成器能够重建；两项能力分开报告。
- `ReplayDerived` 输出保留原输入 digest、父来源、实际参数/算法/模型/后端版本和本次运行 ID；不能因输出与真实基线一致而改为 `RealCapture`。同一父数据的重复回放不增加独立实物样本数。
- 上述来源描述及传递引用属于 §9.1 的语义内容，纳入闭包/场景 canonical hash；本地路径、显示标签和用户筛选不构成来源证据。旧包未提供类别时保留 `Unknown`，不得从文件名、画面逼真程度或缺少合成标记推定真实采集。

**处理顺序：** 固定输入集合 → 读取并校验来源/父引用/digest → 校验当前任务所需的生成信息 → 按 §7 进行同语义比较 → 按来源类别及派生链分别汇总 → 封存报告。汇总仍保留 §3.3 的原始分母和六类结果，分层计数不得遗漏 `Unknown` 或取消项；跨来源比较必须显示原/候选两侧来源，不将差异统计包装成实物召回率、Bias/GR&R 或现场节拍。

**错误与恢复：** 父引用/hash 损坏返回 `REPLAY-0002`；任务要求生成过程可重建而缺生成闭包时返回 `REPLAY-0004`。仅历史解释或固定像素的数值回归，不因缺生成器执行环境一律拒绝；须说明生成过程不可重建。补齐或更正来源建立新闭包/运行，旧报告不可改写。外部已给出的 `EngineeringOnly`/资格限制原样作为来源注记投影，Replay 不计算 guard band、不激活模型、不改变质量或设备状态。

**可判定验收：** 同一合成父帧重复回放十次，案例数按冻结请求记录，独立实物数不得报为十；真实、合成、注入和派生来源不能混标。生成器版本、假设或随机化范围改变时场景 hash 必须改变，即使最终像素恰好相同；缺生成参数不得声称生成过程可重建。真实与合成帧数值一致只支持本次工程比较，不产生 `Verified`、生产资格或设备授权。

## 7. 比较规则

1. **身份**：按稳定目标、产品/面/FOV、功能和被测量定义外连接；禁止按数组顺序、显示顺序或数值排序配对。重复、缺失、新增和歧义分别报告。
2. **有效性**：`Missing`、`NotRun`、`Invalid`、`NaN/Inf` 与有效零值不同；双无效只能表示状态一致，不能算准确量测一致。
3. **单位/坐标**：只在策略批准的同维度转换后比较；无标定的像素与物理单位不可比较。保留原值、单位、坐标版本和转换来源。
4. **数值**：不先按 UI 位数舍入；按字段冻结的 `A/R` 和方向计算；有限性、溢出和支持域先校验。
5. **图像/区域/曲线/3D**：同时比较类型、shape、通道、有效域、覆盖和误差。自动对齐只可作为诊断副本，不能替换冻结坐标的主结果。
6. **离散语义**：判定、拒识原因、覆盖、方法版本和模型 hash 单独比较；数值接近不能掩盖语义变化。

视觉差异如需计算，按 §20 使用本地 HALCON 26.05 语义并经 `ImageLibDotNet.cv2` 调用，适配器记录算子/版本/参数；只在具体 C# 重载/封送歧义时编译核对。事务、身份、统计分母和权限不使用视觉算子替代。核心不复制 Variation Model、定位或其它算法；AsunControl 的 `C_VariationModel_Compare.Compare`、`C_VariationModel_Parameters` 和事件仅作历史借鉴，不能直接依赖其 `HObject`、同步事件或 `ErrorMessage` 字符串。

## 8. 取消、断连、关闭和资源所有权

取消是协作式请求，期限只停止接纳和通知 Engine，不证明 native/GPU 已退出。进程内不可中断调用等待真实返回；需有界客户关闭/强资源限制的后端使用显式隔离 worker，不能通过释放仍在使用的对象中断。worker 的终止由宿主进程监督器确认进程退出、子进程树/IPC/句柄已回收后才报告 Drained；进程死亡仍可能使输出 Unknown，不能默认节点失败或成功。Core 不启动任意进程，不包含厂商 SDK。

| 资源 | 申请/持有 Owner | 释放条件 |
|---|---|---|
| 源证据持久保持 | Reader/源资产 Owner | 生命周期由其保留策略决定，Core不删除原证据 |
| 只读 lease/Stream | Core 获 lease，消费方获每次独立 Stream | 所有案例/Engine/IO完成后先关流，再归还一次 |
| 案例 native/GPU/模型实例 | Engine 每案例上下文 | native/GPU/回调真实结束；可共享只读模型但禁止并行修改句柄 |
| 候选产物临时内容 | Engine/Store暂存 | 成功转移并获得 Store回执后不再由原方释放；失败仍由原 Owner回收 |
| 已封存案例/报告 | Store | 保留/归档/访问/删除由宿主授权策略决定，不随会话 Dispose删除 |
| permit/队列槽/缓存 | 单一宿主资源协调器分配，Core持有 | 资源不用后归还；Draining项继续占配额 |
| 事件订阅/图像显示 lease | UI投影 | 页面关闭先撤订阅、释放显示副本，不影响计算源 lease |
| CTS/回调登记 | Core会话 | 使用者退出后 Dispose；CTS.Dispose 不等于 Cancel或排空 |

执行适配器断连、权限被撤销、证据 lease 无法继续保持：停止新案例，原 CaseId 保留，已知未执行=CancelledOrNotRun/缺项标签，已知失败=Failed，执行回执不明=Unknown。保持失败不能用缓存替代未经完整性验证的原证据。取消和关闭也必须完成固定分母报告，磁盘/Store 故障例外用权威操作记录说明无报告。

宿主关闭先停止 Start 接纳、对自己拥有的会话 Cancel、逐个观察 Drain。观察期限到达：留在 Draining，保留服务/监督器引用与原 RequestId；生产宿主不能关闭相同进程仍在使用的 native运行时。UI 页面关闭默认仅脱离显示；若是独占运行的宿主退出，则走上述关闭流程，UI 不同步等待 Dispose。调用方因 WaitAsync 取消而失去响应时仍可 Query；Start回执丢失必须先查 RequestId。引用归还、资源释放和终态证据均未知时，不另起同摘要计算。

暂存文件经完整写入/关闭、长度/hash 验证与不可变 publish 后才被 Store引用；原子可见不等于断电耐久，Store能力必须声明耐久级别及真实 crash恢复验收。Core不自造文件事务或删除未知目录。取消/失败路径仅回收本次未封存暂存对象，不删除已封存内容/客户配置/正式测试/来源原件。

## 9. 线程、并发和确定性

核心不依赖 UI 同步上下文；事件在调用方提供的调度器上投影。默认每个会话 `MaxConcurrency=1`，批量并发必须由宿主 Profile 允许并计入内存/native/GPU预算。不得在每个会话私改 HALCON 进程全局设置；线程数、随机源和 GPU 确定性由唯一运行时 Owner 或隔离进程管理。

恢复只复用完整封存的案例：输入/参数/节点/环境/随机状态/输出均可校验，且版本兼容。否则从合法切点新建工程计算尝试并关联父请求，不伪造原机器尝试。相同输入 hash 只证明内容相同，不证明算法结果正确。

## 9.1 唯一摘要规则：replay-jcs-v2

本模块只使用 RFC 8785 JCS + SHA-256；不是“排序后任意 JSON”。旧 Replay 包保留原 hash/规则，v2新增资产不覆盖旧摘要。模型资产仍保持其自己的规则，本规则只封装精确引用。公开 Core 工具类 ReplayCanonical 的静态方法为 ComputeRequestDigest(ReplayRunRequest)、ComputeScenarioDigest(ReplayScenarioManifest)、ComputeResultDigest(ReplayResult)、ComputeClosureDigest(ImmutableArray<ReplayClosureItem>)，返回小写64位十六进制；输入无效以 ReplayPortException(0001/0015) 返回，不尝试修复。

计算为 SHA256(UTF8(domain) || 0x00 || JCS(projection))。domain 分别为 replay-request-jcs-v2 / replay-scenario-jcs-v2 / replay-result-jcs-v2 / replay-timeline-jcs-v2 / replay-closure-jcs-v2；domain 不可互用。投影顶层含 schema="replay-jcs-v2"、kind、content，kind分别为request/scenario/result/timeline/closure，与对应domain唯一对应；content 使用声明字段名称首字母小写的 JSON 键，枚举写其英文名称，所有可选字段显式 null，所有字段无隐含默认值。拒绝重复键、无效 UTF-8/孤立 surrogate、未知必需字段、NaN/Inf及不符合 schema 值，不先做 Unicode规范化。

**数值编码：** 所有 Int32/Int64/UInt64/字节数/sequence/timestampNs/TimeSpan.Ticks 编为规范十进制字符串（允许负值的字段保留负号；无+号/前导零；0唯一）；Duration 编 ticks 字符串，不把七天纳秒转为易失真 JSON number。double 必须有限，JCS 按 ECMAScript 最短数值表示，-0变0；如需保留 IEEE 位模式，须以 artifact内容摘要或单独 rawBits hex 文本比较，不能声称 JCS保留-0/NaN位模式。Decimal/Int64 的 ReplayValue 保留 §3.2 的文本，不经过double。日期使用UTC的固定七位小数格式 yyyy-MM-ddTHH:mm:ss.fffffffZ。对象键按 UTF-16 code units ordinal 排序，不按UTF-8字节/文化；数组保持定义的顺序：有序图/事件/调度原顺序不可重排，集合字段在建模时按稳定ID排序一次并拒绝重复，不能在hash期间另猜集合意义。

**投影覆盖/排除：**
- RequestDigest 排除 RequestId/ReplayRunId；覆盖其余全部请求语义和所有 ContentRef。OutputNamespace 必须为与运行ID独立的稳定逻辑域，实际文件落点另由Store以RequestId分区。变更 Author/Reason保留为审计语义，改动产生新摘要。FromCheckpoint 包含精确状态/环境摘要。
- FrozenClosureDigest 投影为已解析 Program Graph、Evidence目录、比较策略、输入/模型/标定/来源传递引用列表以及实际 Runtime；按 (Role,AssetId,Revision,Digest)排序。闭包条目是 ReplayClosureItem(Role,ContentRef)，不包含路径/显示标签/读取时间。Runtime全字段以ReplayRuntimeManifest(schema=replay-runtime-v3,Profile=实际ReplayRuntimeProfile)规范UTF-8原字节生成ContentRef并作为runtime-profile角色纳入；不能只纳入EnvironmentDigest而漏backend/精度/确定性/seed。该manifest是模块封存的请求值快照、无环境自指，不更改replay-jcs-v2域或旧hash；旧闭包不补写/重算。所有引用先验证，再hash；循环/不可解析拒绝0004。
- ScenarioDigest 排除 ScenarioCanonicalHash 与请求运行身份；包含逻辑场景ID/修订、Request投影、Clock逻辑 BootId/初始UTC、Schedule、Participants/ContractVersions、事件/fault/断言/非确定性政策和传递引用。事件里的 OperationId/CorrelationId/IdempotencyKey 只能是包内逻辑ID，运行时映射实际 RequestId，不能混入随机运行ID。Payload 使用精确 ContentRef，纳入传递校验。断言不得引用正在计算的本场景hash或其自身摘要，不能产生自指。
- SealedResultDigest 排除自身 SealedResultDigest，保留实际RunId/RequestId、FinalState、资源摘要、完整CaseResults引用和全部诊断；报告只生成一次。相同工程数值但不同运行时间的报告摘要可以不同。SealResult需持久化含完整报告的对象和其操作回执；报告摘要不是“算法一致摘要”。
- TimelineDigest 投影为完整有序 ReplayEvent 数组；只有确定性模拟器使用逻辑RunId/RequestId/虚拟UTC与固定调度生成可复验摘要。真实运行封存原时间线，不删除资源/时间来伪造逐位一致。

向量门：对象键顺序/缩进不改hash；显式null与缺字段（schema拒绝）不混用；组合 Unicode与分解 Unicode不自动等同；JSON重复键拒绝；整数9007199254740993仍与9007199254740992不同；JCS数值333333333.33333329规范为333333333.3333333、1E30为1e+30。同义数值表述允许JCS等价，语义改变断言在规范schema上判定，不能声称原始字节任意变化必变hash。旧规则 hash只验证，不迁移重算。

### 9.1.1 完整场景/断言类型

以下类型仅用于 Core诊断/测试包，不创建平台 Schema 或生产故障控制面：

```csharp
public sealed record ReplayClosureItem(string Role, ContentRef Content);
public enum ReplayClockMode { RealTime, Virtual }
public enum ReplayScheduleMode { Declared, Explore }
public sealed record ReplayClockProfile(ReplayClockMode Mode, DateTimeOffset UtcStart,
    string BootId, long MonotonicStartNs, bool AllowUtcJump, bool AllowBootChange);
public sealed record ReplayScheduleChoice(long Step, string ParticipantId, string YieldPointId);
public sealed record ReplaySchedulePlan(ReplayScheduleMode Mode, ulong? Seed,
    int MaxSteps, ImmutableArray<ReplayScheduleChoice> Choices);
public sealed record ReplayParticipantRef(string ParticipantId, string Role,
    string AdapterId, string ContractRevision);
public sealed record ReplayContractRef(string ContractId, string SchemaVersion, string Digest);
public sealed record ReplayPackageRef(string Role, ContentRef Package);
public sealed record ReplayScenarioEvent(string EventId, string SourceId, string TargetId,
    string Type, string SchemaVersion, long AtMonotonicNs, int Priority, long Sequence,
    string? CorrelationId, string? OperationId, string? IdempotencyKey, ContentRef Payload);
public enum ReplayAssertionKind {
    FinalState, CaseOutcomeCount, ErrorPresent, ErrorAbsent, EventBefore, EventAbsent,
    ArtifactDigest, ResourceAtMost, ProductionWritesEqual
}
public sealed record ReplayAssertion(string AssertionId, ReplayAssertionKind Kind,
    string SubjectId, string ExpectedValue, string? OtherSubjectId);
public sealed record ReplayExpectedAssertions(ImmutableArray<ReplayAssertion> Items);
public sealed record ReplayNondeterminismPolicy(ReplayDeterminism Level,
    ImmutableArray<string> MetadataPaths, ComparisonPolicyRef NumericPolicy);
public sealed record ReplayScenarioManifest(string ScenarioId, string ScenarioRevision,
    string ScenarioCanonicalHash, ReplayRunRequest Request, ReplayClockProfile Clock,
    ReplaySchedulePlan Schedule, ImmutableArray<ReplayParticipantRef> Participants,
    ImmutableArray<ReplayContractRef> ContractVersions,
    ImmutableArray<ReplayScenarioEvent> EventScript, ImmutableArray<ReplayFaultSpec> Faults,
    ReplayExpectedAssertions Expected, ReplayNondeterminismPolicy Nondeterminism,
    ImmutableArray<ReplayPackageRef> TransitivePackageRefs);
public sealed record ReplayScenarioRunManifest(string ScenarioCanonicalHash, string RunId,
    string TimelineHash, string ResultDigest, ImmutableArray<string> HitFaultIds,
    ImmutableArray<ReplayError> Errors, ImmutableArray<ReplayScheduleChoice> ActualSchedule);
public interface IReplayScenarioRunner {
    ValueTask<ReplayScenarioRunManifest> RunScenarioAsync(ReplayScenarioManifest scenario,
        CancellationToken ct);
}
```

场景 schema=replay-scenario-v2；ScenarioCanonicalHash 在创建前可空字符串，加载时必填且校验。Participants/ContractVersions/Packages 按稳定ID/Role排序且唯一。Expected至少有 FinalState、六分类计数、错误存在/禁止、资源/副作用断言；Items非空且AssertionId唯一。FinalState/CaseOutcomeCount ExpectedValue为枚举/非负十进制；EventBefore的两个Subject为EventId或目录Kind；ArtifactDigest为ContentRef.Digest；ResourceAtMost Subject只允许§3 Usage字段，ExpectedValue为非负整数，null资源实际值使断言NotObserved/失败，不能跳过；ProductionWritesEqual只能期望0。Unknown也须明确断言。MetadataPaths只可排除实时时间/显示元数据，不允许身份、结果、状态、错误、单位、坐标、来源、生产副作用或资源归还；数值容差由NumericPolicy逐字段提供。断言表达语言不是自由脚本/JSONPath执行器。

## 9.2 时间、boot 与稳定调度

真实 deadline 用宿主单调时钟，从接纳开始取 elapsed，checked溢出/时钟倒退停止0001；避免绝对 deadline相加溢出。虚拟UTC可跳变但不改变同boot单调顺序。真实时钟BootId在进程启动固定；测试BootChange必须显式场景事件，旧lease/token失效，旧monotonic值不用于新boot。真实恢复不延长原deadline：Store保存已消耗持续时间/剩余期限；无法证明剩余期限时原操作只查询，恢复计算使用新RequestId。

事件排序键固定 AtMonotonicNs → Priority（小值先）→ SourceId ordinal → Sequence → EventId ordinal。At>=0；同Source Sequence严格递增，EventId唯一，重复/负值/溢出0015。Declare模式执行Choices中每步指定的已就绪参与者和YieldPoint；无Choice事件按上述键，不按真实任务完成快慢。涉及重启事件按Boot逻辑epoch分段执行，At相对所在boot；Payload schema必须登记新逻辑BootId，不让跨boot At被全局混排。Yield点为 BeforeValidate/BeforeReserve/BeforeNodeExecute/AfterNodeExecute/BeforeCaseSeal/BeforeResultSeal/BeforeResourceRelease，只存在于替身端口，不能修改真实HALCON调用调度。

Explore仅测试适配器运行，MaxSteps>=1、Seed非零且必填，保存每一步选择；唯一采用xorshift64*固定算法：无符号64位模2^64，x ^= x>>12；x ^= x<<25；x ^= x>>27；返回x*2685821657736338717，state为乘前x。就绪项按ParticipantId/YieldPointId ordinal排序，取返回值 modulo就绪数；记录选择后才能推进。无就绪且有未来事件推进虚拟时间，否则判死锁/0015。超过MaxSteps失败，不假称完成。失败schedule按删除选择前缀/连续区段后重放的确定性缩减顺序保存能保持相同断言失败的最短已找到序列，不宣称全局最小。Declared保存该序列即可独立复验，不依赖Random实现或线程Sleep。

虚拟时间只检验软件顺序；真实性能/取消到真实释放使用真实单调时钟。调试改变取消时机、deadline、Yield选择必须新场景hash，标DiagnosticOnly。

## 9.3 故障登记与崩溃点

故障只在测试替身/隔离测试worker中发生；Core生产路径不读取registry，不使用if(simulation)。场景不支持字符串反射、概率或自由条件表达式；每个fault是明确边界/第N次触发，以可判定向量取代“随机偶发故障”。

```csharp
public enum ReplayFaultKind {
    Delay, Drop, Duplicate, Reorder, Corrupt, Exception, ProcessKill, ClockJump,
    BootChange, CapabilityChange, ResourceExhaustion, DiskFull, PermissionRevoke, AdapterUnavailable
}
public enum ReplayFaultPoint {
    BeforeValidate, AfterReserve, BeforeNodeExecute, AfterNodeExecute, BeforeCaseSeal,
    AfterCaseSealBeforeReceipt, BeforeCheckpointCommit, AfterCheckpointCommitBeforeReceipt,
    AfterResultSealBeforeCompletion, ResourceAcquire, ResourceRelease, ProcessRestart
}
public sealed record ReplayFaultSpec(string FaultId, ReplayFaultKind Kind,
    ReplayFaultPoint Point, string ScopeId, int Occurrence, string? ExactEventId,
    ContentRef Parameters, ImmutableArray<string> ExpectedAssertionIds);
```

FaultId唯一；Occurrence>=1，ScopeId存在且ExpectedAssertionIds引用本包断言；ExactEventId若有必须注册。Parameters唯一schema=replay-fault-v2，完整判别字段及范围见§9.5；旧描述“fault kind-v2”不是可接受schema。未知/不匹配/schema缺项执行前0015。不在Core公共API注入任意异常类型。

命中/未命中/拒绝都封存事件和FaultId；Expected要求命中而未命中使测试失败。Drop仅可作用测试通知/回执，不允许默默丢原证据改变事实。ProcessKill只用于宿主启动的独立测试worker，进程内Core测试不杀当前进程；停点如下：
- BeforeCaseSeal：无封存案例；复用必须新尝试，旧输入Owner回收。
- AfterCaseSealBeforeReceipt：按原RequestId+CaseId查询Store内容，禁止重算/重复Append。
- BeforeCheckpointCommit：不完整点不能被解析为CutPoint；Checkpoint由外部Engine产生完整状态资产，Core不提供训练checkpoint接口。
- AfterCheckpointCommitBeforeReceipt：查询原ContentRef/回执，不新增节点执行。
- AfterResultSealBeforeCompletion：原RequestId可回查同一封存报告；终态事件可重送，不重复Seal或执行。

## 9.4 模拟器与共同 Contract Suite

ReplayDeterministicSimulator 是测试工程内 BCL替身，实现同 Reader/Resolver/Engine/Comparison/Store公开端口；固定案例值/时钟、可控制异步闩锁、真实计费的模拟缓冲及计数Owner。它不提供平台PLC/MES/培训UI，不授予任何生产写权限。IReplayScenarioRunner位于测试专用命名空间Asun.Modules.Replay.Testing，只通过替身端口安排事件/fault/调度；生产服务不暴露它。FlowSimulation经Runner组合Service执行软件合同；生产组合根拒绝带fault的Program schema，不能用FlowSimulation绕过边界。

共同Suite按同输入语义验证预检、身份/有效性、六分母、错误、幂等、取消/超时、真实排空、版本拒绝和副作用0；接口能力不同的测试必须具体列RequiredCapability，缺必需能力使该适配器资格失败，不能记通过。只有Simulator及显式声明BitwiseSameEnvironment的固定后端，才要求逻辑timeline/数值artifact逐位重复；真实并发后端验证因果偏序、稳定身份和字段级容差，原始timeline/result报告digest不要求跨次相等。重复RequestId仍必须返回同一个原报告digest，这是幂等，不是跨运行确定性。

Simulator专属：hash向量、event tie-break、UTC/Boot故障、xorshift schedule复验、每个fault命中/未命中、半写/crash边界；真实适配器专属：HALCON/GPU实际结果、真实取消/进程回收、持久耐久/断电、WPF呈现。分别记录NotApplicable/NotObserved/Failed，不把Simulator通过变成真实适配器、性能或现场资格。

### 9.5 公开 Simulator、Runner 与注入协议

Simulator是可独立引用的测试能力包Asun.Modules.Replay.Testing，net10.0/BCL，生产Core不依赖该包；当前全部批准模拟能力按下列公开形状实施，不再只给类名。它模拟Replay接口行为/资源，不模拟设备工艺。

```csharp
public sealed record ReplaySimulatorOptions(int MaxEvents, int MaxFaults,
    int MaxAssertions, int MaxParticipants, long MaxPackageBytes,
    int MaxScheduleSteps, TimeSpan RealObservationBudget);
public sealed record ReplaySimulatorPorts(ReplayDependencies Dependencies,
    IReplaySimulationControl Control,
    IReplayDependencyHold Hold);
public interface IReplaySimulationControl {
    void Release(string gateId);
    void Revoke(string scopeId);
    ReplaySimulationTrace Snapshot();
}
public sealed record ReplaySimulationTrace(long Steps, long EngineStarts,
    long ProductionWrites, long DeviceWrites, long ActiveBytes,
    long ReturnedLeases, ImmutableArray<string> HitFaultIds,
    ImmutableArray<ReplayScheduleChoice> Schedule);
public static class ReplaySimulatorFactory {
    public static ReplaySimulatorPorts Create(ReplayFixtureInput input,
        ReplaySubjectBinding subject, ReplayFixtureAuthority authority,
        ReplayResourceCoordinator resources, ReplaySimulatorOptions options);
}
public sealed class ReplayScenarioRunner : IReplayScenarioRunner {
    public ReplayScenarioRunner(ReplayProcessRoot root, ReplayRootTicket ticket,
        IReplaySimulationControl control, ReplaySimulatorOptions options);
    public ValueTask<ReplayScenarioRunManifest> RunScenarioAsync(
        ReplayScenarioManifest scenario, CancellationToken ct);
}
```

Factory无IO冻结输入/完整limits，使用§12.3具体Reader/Resolver/ScalarEngine/Comparison/MemoryStore/FixtureClock；Control/Runner共享该组实例，绝不为Runner再造第二Store/时钟/Root。Factory只返回Dependencies/Control/Hold；Runner必须在已AttachHold/Factory完成的ticket上公开构造，没有未绑定的半成品Runner。依赖创建无Task，Start与事件工作均经原Root登记；control只向该模拟器固定gate/authority操作，不触及宿主设备/其它模块。Options固定合同Host值=(4096,64,256,16,1048576,10000,10s)，域均正、RealObservationBudget[50ms,10min]，scene任何计数/引用展开超过limits在预检0015/0006，无副作用；所有hold retainedBytes按真实可保留上界计费，拒绝后不执行。

调用：原进程Root.TryReserve→SimulatorFactory.Create→AttachHold→Root.CreateAsync→new ReplayScenarioRunner(root,ticket,ports.Control,options)→RunScenarioAsync；RunScenario请求必须与ticket原RequestId/Subject绑定（逻辑ID映射只在包内完成，不能覆盖主体），scenario.Request.OutputNamespace与该scope完全一致，ScenarioCanonicalHash/传递引用先核；同一Runner只一场景在途且一次Start，多场景分别新ticket。Control在Factory内部不可变关联同Dependencies/Subject/fixture RequestDigest，Hold标识同一组合实例；Root.Create采用该Dependencies，Runner构造从原ticket的Dependencies核相同Control实例及options，错Root/ticket/control在Start前0001且零执行。Runner内部Root.StartAsync、ObserveCompletion、Query、ReadCases均沿§12原Task/cleanup，不在ct取消后离栈丢控件或资源；RunManifest只有TimelineHash/ResultDigest等无敏感结果的授权投影，撤权不返回包引用。

EventScript仅注册以下Type/Schema及payload（普通UTF-8/JCS对象，Parameters不是匿名自由对象）：EventDeliver/replay-sim-event-v1含eventId；GateRelease/replay-sim-gate-v1含gateId；Cancel/replay-sim-cancel-v1含requestLogicalId；Assert/replay-sim-assert-v1含assertionId。其它0015；payload键全部必填、未知键/重复键拒绝。Fault Parameters schema为replay-fault-v2，内容共用kind及**只对应kind的字段**：
Delay(durationTicks,gateId)、Drop(eventId)、Duplicate(eventId,count>=1)、Reorder(eventId,beforeEventId)、Corrupt(content,offset>=0,xorMask=1..255)、Exception(errorCode)、ProcessKill(workerId)、ClockJump(offsetTicks)、BootChange(bootId)、CapabilityChange(adapterId,capabilities排序唯一)、ResourceExhaustion(resource,bytes>0)、DiskFull(storeDomain)、PermissionRevoke(scopeId)、AdapterUnavailable(adapterId)。durationTicks有界于scenario/真实观察预算，负offsetTicks仅UTC跳变允许；腐蚀只改自己的测试副本并仍保父hash，核实际损坏0002。ProcessKill/ProcessRestart只交§10.3的已登记隔离worker；进程内Runner声明不支持时预检0013而非假命中。BeforeCheckpointCommit等只有明确注册checkpoint participant才支持，缺则RequiredCapability失败；不凭空模拟真实Engine内部停点。

调度单协调器控制明确yield闩锁，Declared choice不存在/未就绪/重复Step/超MaxSteps为0015，未用choice也失败；Explore按§9.2唯一固定xorshift算法，以指定seed和ParticipantId/YieldPointId排序及modulo选择，记录后才释放gate。Delay暂停目标gate直到对应逻辑时间且不堵协调器；drop仅吞指定通知/回执，原Task/Store提交仍真实发生；duplicate是观察重送，不能再Engine.Start；reorder只改测试消息交付不改Case目录或事实提交。同boot事件总序/跨bootepoch规则保持。Assertion在其事件或最终点逐项判定，EventBefore为已记录两首次命中序号、相同序号不满足；缺事件/不支持资源(null)/未命中必需fault/断言未评均失败0015，所有反例保faultId/assertionId。

最小二消费者向量直接使用§12.4Regression/Customer两独立input；各新增同种模拟scene：虚拟boot=fixture-boot-1、UTC=2026-10-11T00:00:00Z、MaxSteps=100、Explore Seed=1/Choices=[]、participant=[scalar,store]、无fault时两个分类与原Golden一致，ProductionWritesEqual=0、DeviceWrites通过Usage/trace=0、活动lease最终0。反例同场景在AfterCaseSealBeforeReceipt做Drop回执、ClockJump(+10s)、PermissionRevoke及ResourceRelease闩锁；新scenario hash，不改变旧Golden：原Case查询Found后不重Execute，UTC跳不触Deadline，撤权Query0005且Root安全收尾，闩锁未释放时ActiveBytes>0/BackgroundOwned，显式Release后归还一次。Explore seed=1的首次xorshift返回5180492295206395165、state=33554433，就绪2项取index1；固定模数验证非随机框架依赖。真实性能使用外层Stopwatch，虚拟Advance不冒充耗时。

## 10. 适配器与版本兼容

适配器至少实现：证据读取、程序解析、执行引擎、比较策略、输出存储和诊断。每个适配器声明能力集合、输入格式版本、HALCON/AsunImage 桥版本、线程/取消能力、最大尺寸和确定性等级。旧适配器不能解析新契约时返回 `REPLAY-0013` 或 `REPLAY-0003`，不能静默忽略字段。

兼容规则：新增可选字段保持读取兼容；改变单位、有效性、身份组成、比较公式、状态语义或删除字段必须提高 ContractRevision 并提供迁移/回退策略。二进制回退不回滚已封存工程结果；旧结果保留原 Schema/算法/环境引用。发布包必须包含契约版本、适配器清单、依赖 hash、迁移说明和回退验证记录。

### 10.1 受控公开 Adapter Factory、codec 与内容事务

本节固定本模块Adapter的实现责任，不把“以后接真实Store/Engine”作为算法/API欠账。持久介质、客户资产目录与已有节点的业务语义属于各Owner的配置/事实；Replay自己的解析、装配、执行、CAS/错误/分页映射按下述实施。命名空间Asun.Modules.Replay.Adapters（net10.0，仅BCL）与Asun.Modules.Replay.AsunImage（用户既有依赖）分包，UI另包。

```csharp
public sealed record ReplayCodecLimits(long MaxDocumentBytes, int MaxDepth,
    int MaxStringUtf8Bytes, int MaxCollectionItems, int MaxDomainRuns);
public sealed record ReplayAdapterOptions(ReplayCodecLimits Codec,
    ReplayServiceOptions Service, long MaxRetainedBytes, int MaxConcurrentReads);
public interface IReplayAssetCatalog : IReplaySubjectScoped {
    Task<IReplayContentLease> OpenAsync(ContentRef reference, CancellationToken ct);
}
public sealed record ReplayStoreMutation(string RequestId, long? ExpectedRevision,
    string ContractRevision, ReplayStoreMutationKind Kind, ImmutableArray<byte> CanonicalBytes);
public enum ReplayStoreMutationKind { Reserve, State, Case, Cases, Event, Result }
public sealed record ReplayReservePayload(ReplayRunRequest Request, string RequestDigest,
    string FrozenClosureDigest, ContentRef CaseDirectory, int Denominator,
    string BootId, long AcceptedMonotonicNs);
public sealed record ReplaySealCasesPayload(int Denominator, int MaxItemsPerPage, long MaxPageBytes);
public sealed record ReplayStorePayload(ReplayReservePayload? Reserve, ReplayState? State,
    ReplayCaseResult? Case, ReplaySealCasesPayload? Cases,
    ReplayEvent? Event, ReplayResult? Result);
public sealed record ReplayStoreEnvelope(string Schema, ReplaySubjectBinding Owner,
    string OutputNamespace, string RequestId, long? ExpectedRevision,
    string ContractRevision, ReplayStoreMutationKind Kind, ReplayStorePayload Payload);
public sealed record ReplayStoreCommit(ReplayReservation? Reservation,
    ReplayOperationLookupResult? Operation, ContentRef? Content, ReplayError? Error);
public interface IReplayAtomicStore : IReplaySubjectScoped {
    Task<ReplayStoreCommit> CommitAsync(ReplayStoreMutation mutation, CancellationToken ct);
    Task<ReplayOperationLookupResult> QueryAsync(string requestId, CancellationToken ct);
    Task<IReplayContentLease> OpenAsync(ContentRef content, CancellationToken ct);
    Task<ReplayCaseLookup> QueryCaseAsync(string requestId, string caseId, CancellationToken ct);
    IAsyncEnumerable<ReplayEvent> EventsAsync(string requestId, long afterSequence, CancellationToken ct);
}
public sealed record ReplayAdapterPorts(IReplayEvidenceReader Reader,
    IReplayProgramResolver Resolver, IReplayComparisonPolicy Comparison,
    IReplayResultStore Store);
public sealed class ReplayMemoryAtomicStore : IReplayAtomicStore {
    public ReplayMemoryAtomicStore(ReplaySubjectBinding subject, string outputNamespace,
        long maxBytes, IReplayClock clock, IReplayAuthorization authority);
}
public static class ReplayAdapterFactory {
    public static ReplayAdapterPorts Create(ReplaySubjectBinding subject,
        IReplayAssetCatalog source, IReplayAtomicStore output,
        IReplayAuthorization authority, ReplayAdapterOptions options,
        ImmutableArray<IReplayArtifactComparer> artifactComparers);
}
public static class ReplayDocumentCodec {
    public static T Decode<T>(ContentRef reference, ImmutableArray<byte> canonicalBytes,
        ReplayCodecLimits limits);
    public static ImmutableArray<byte> Encode<T>(T value, string schema, ReplayCodecLimits limits);
}
```

Create无IO/不获租约，校验source/output主体完全匹配和全部options；ReplayStoreCommit成功Reserve须Reservation与Operation非null，成功State/Result须Operation非null，成功Cases须Content非null，Case/Event成功返回本次Operation；Error=null不得代表未知。提交结果不明Operation.LookupState=Unknown/Error=0014，不得伪装Created/已封存。输出端口是唯一隔离工程事务Owner，不接生产写/SQL/设备命令。Codec类型T不是任意反射类型：仅§3/4.1/9.1.1明确register的DTO、ImmutableArray<ReplayNodeOutput>、本节ReplayStoreEnvelope及其payload、§9.5固定fault/event、§10.2image描述；其它0013，unknown schema/contract pair不重释。Decode以Utf8JsonReader单遍先限制原总bytes/depth/token/string/array，再逐字段映schema精确大小写、必填/显式null/重复键/未知键，所有数值遵循§9.1字符串与判别联合；UTF8严格、surrogate/I-JSON/RFC8785规则复用§18固定证据，不用默认JsonSerializer枚举/TimeSpan/宽松数字。原ContentRef长度/hash先核原字节，再JCS规范化验语义；输入可接受合法非canonical whitespace/key order，但资产身份始终按原bytes，不用canonical新hash冒原对象。Encode预计长度后有界写JCS，当前新资产强制canonicalUTF8；新hash为原输出bytes，request/result域向量仍按原§9.1单独算，无混域。文档codec错误路径字段名/代码不回客户字节。

Reader.ResolveScope按EvidenceClosureManifest精确引用获取directory并流式核页Count/Offset/hash/CaseId与Scope，必需传递引用递归DFS三色检测环、同完整引用只验证一次；无权限/租约/语义错误按§4分类，不能先全包展开再限。每document受Codec limits，目录/结果manifest的Pages数量也受MaxCollectionItems，超限拒绝而不构造大数组；宿主大批次Profile须显式提高受预算的页描述上限，case实体仍逐页，不能用“流式”绕过单文档上限。ReadCases按固定ordinal目录分页读取，Release每页IO租约但源持久保持由资产Owner，不能删除源。每次Stream.ReadAsync前授权；body累计byte<=Ref.ByteLength，末块hash完成才允许执行。Resolver读取Program Manifest→Graph DAG拓扑核对→所有传递依赖→Changes JSON pointer逐字段类型验证→比较Before值与父值→创建独立候选值/Graph暂存（不覆盖旧AssetId/Revision）→新闭包摘要；同节点多个Change按ordinal Path且互不父子，引用型After必须可解析，不支持修改位置0013。HistoricalExplain不解析执行环境，保持原结果只读；FromCheckpoint由注册node decoder校验State/NodeRevision/EnvironmentDigest和其受影响上游，缺完整state0012，不默认重训/继续最新模型。

Comparison实现§7与§3.2：Baseline精确读replay-node-outputs-v2，以(nodeId,nodeRevision,fieldId)键外连接；不可比标签按ordinal唯一排序。整数使用BigInteger，Decimal规范文本→整数mantissa+十进制scale比较（不受CLR decimal溢出影响）；Float64有限double按已冻结A/R/周期，非有限中间结果0008，不舍入；Text/Boolean exact，Artifact按声明schema交§20图像/对应专业比较注册器（唯一公开注入与计费见§10.1.1），不自动用文件hash代像素；缺注册器0013/CompletedIncomparable。案例Outcome优先不可比→变化→相等，节点异常Failed，已取消未执行项CancelledOrNotRun，Unknown保持独立六类。不复用UI/统计模块的业务表。

AtomicStore不是新平台数据库：模块Memory实现和持久接线消费同一事务接口。每mutation CanonicalBytes编码ReplayStoreEnvelope（schema=replay-store-mutation-v3，camelCase，数字/枚举/null沿§9.1），外层RequestId/ExpectedRevision/ContractRevision/Kind与envelope逐值相同，否则0002。Owner/OutputNamespace固定原scope；Payload六字段全部出现，恰Kind对应字段非null，其余显式null；Reserve含完整原request/run/digest/闭包/目录/分母/boot/接纳时钟，State为next state，Case/Event/Result为原DTO，Cases为ReplaySealCasesPayload；Denominator须等于原目录，MaxItemsPerPage/MaxPageBytes为facade显式Service.MaxReadPageSize/MaxReadBytes且正。AtomicStore从已持有原Case表按原目录顺序逐页生成ReplayCaseResultPage，单页达到条数或预计编码bytes上限前切页；单项超MaxPageBytes拒0006。完整页hash/offset/count与manifest由Store同一原子封存中生成，Content是最终ReplayCaseResultManifest引用，失败不暴露半页；不能让调用方先传未在Store存在的page引用。Reserve expectedRevision=null，成功Revision=1；其它ExpectedRevision为正且ContractRevision等于原版本。Operation.Revision仅State/Result迁移增长；Case/Cases/Event在同操作串行事务内核当前Revision、前置及幂等键，不因append擅增状态revision。Facade为无revision参数的AppendCase/AppendEvent/SealCases在同一操作写入门先获取已持有执行Owner的当前版本；冲突回读后只重核已计算同一payload，不执行节点。幂等查同CaseId/Sequence/已封Cases或Result先于CAS：内容同返回原回执，内容不同0016；非重复旧revision不写且返回当前已授权Operation+0016。Store facade逐请求验证归属/当前授权与执行Owner capability，不能把外部查询Revision升写权。Cases提交完整page descriptors/count/hash且每CaseId一次，Result封存小报告和操作终态同事务；真实持久实现用现有storage-database的RegisteredBinding/Transaction技术端口，由Replay注册payload/decoder/命令，不把Raw SQL/连接交Core，介质失败Unknown按原ID恢复；部署Owner只提供backend与耐久级别，不补算法。契约不要求所有项目都用同数据库：CPU ReplayMemoryAtomicStore公开构造(subject,outputNamespace,maxBytes,clock,authority)，maxBytes>0，单有界锁表/不可变对象字典，原子CAS与页hash，自身实现完整IReplayAtomicStore，拒超限0006不半写、不承诺跨重启。持久Backend必须实现上述完整变更语义方可接入，技术资格另验。

最小无UI正式装配：原Root槽/host scope hold→ReplayAdapterFactory.Create(subject,catalog,atomicStore,authority,new(codec=(1048576,64,65536,4096,65536),service=§12值,retained=262144,reads=2),artifactComparers:[])→ReplayDependencies(ports.Reader,ports.Resolver,explicitEngine,ports.Comparison,ports.Store,ReplaySystemClock(processBootId),options,coordinator,subject,authority)→同Root.Factory/Start/Query。上述数字仅合成adapter合同Profile；生产Limits由宿主显式Profile，非法不clamp。AlgorithmRegression catalog读Golden只读映射，CustomerRepro catalog读授权脱敏包；两输入逐asset取§12.4，ReplayMemoryAtomicStore两独立实例并生成实际结果。第二消费者真实catalog仍需外部资产ACL/租约/合法客户包，但完整解析/装配规则已经固定。

### 10.1.1 Artifact比较的显式注册与资源汇总

§10.1Factory的artifactComparers由可信组合根显式传入，纯Scalar两Host为[]；不是隐藏静态注册或让Reader猜HALCON后端。以下扩展保持§4原IReplayComparisonPolicy及其普通值形状；Core调用已注入策略时若它实现明确的IReplayContextComparisonPolicy就采用完整本次context入口，普通旧策略沿原入口。上下文入口由本版Adapter实现，旧入口仅可做纯值比较；遇需artifact执行而没有完整context则0013，不通过CaseId偷猜request/budget。

```csharp
public sealed record ReplayArtifactComparison(DifferenceItem Difference, ReplayResourceUsage Usage);
public interface IReplayArtifactComparer : IReplaySubjectScoped {
    ReplayEngineCapabilities Capabilities { get; }
    Task<ReplayArtifactComparison> CompareAsync(ReplayExecutionContext context,
        ReplayComparisonRule rule, ReplayValue original, ReplayValue candidate,
        CancellationToken ct);
}
public interface IReplayContextComparisonPolicy : IReplayComparisonPolicy {
    ValueTask<ImmutableArray<DifferenceItem>> CompareAsync(ReplayExecutionContext context,
        ComparisonPolicyRef policy, ImmutableArray<ReplayNodeOutput> candidate, CancellationToken ct);
    ReplayResourceUsage TakeResourceUsage(string requestId, string caseId, long generation);
}
// Asun.Modules.Replay.AsunImage；不泄漏native对象。
public sealed class ReplayHalconArtifactComparer : IReplayArtifactComparer {
    public ReplayHalconArtifactComparer(ReplaySubjectBinding subject, IReplayEvidenceReader reader,
        ReplayHalconOptions options, ReplayEngineCapabilities capabilities);
    public ReplaySubjectBinding BoundSubject { get; }
    public ReplayEngineCapabilities Capabilities { get; }
    public Task<ReplayArtifactComparison> CompareAsync(ReplayExecutionContext context,
        ReplayComparisonRule rule, ReplayValue original, ReplayValue candidate, CancellationToken ct);
}
```

Factory核每comparer同主体、Capabilities的AdapterId/Revision/SupportedSchemas，(schema,AdapterId,Revision)唯一；当前image-v1默认只登记一个ReplayHalconArtifactComparer，多个能处理同规则却缺显式规则绑定时0013，不取第一个。Artifact类型字段仍由原ComparisonRule提供完整Unit/Coordinate/Kind/精度，原/候选schema/单位/坐标/域等前置按§20，不支持0013或明确Incomparable。HALCON comparer完整算法为§20.2、搬运为§10.2，专业Region/XLD/3D只接各原模块已批准公开比较的本方薄Adapter，未注册保Incomparable，不发明solver。每artifact返回Difference的CaseId/FieldId/Original/Candidate必须与本次输入完全相等，标签与证据引用受schema/预算校验；不能只返回Equal而漏不可比/工程证据。

context包含原request/case/generation/Runtime/Budget；当前Comparer首版CPU、每case内artifact串行，case并发由原Coordinator限制。源/副本/native/temp/工程输出预留与实耗遵循§3/§10.2，未知native观察能力按原严格预算规则拒绝或只在已配置隔离后端用途接纳，不把null写0。Compare原Task真实返回/抛错前必须完成本方native/IO排空及租约归还；ct封新项但不取消已经运行的native，原Core Completion与Root仍强持原Task/全部借用，外层Wait到期不能令其提前返回释放。错误也在finally留下本次不可变Usage；不能以throw省掉资源摘要。

Adapter按(requestId,caseId,generation)有界保留本次Usage，容量为当前接纳case/queue上限，接纳前预留，不能累计存所有历史case。Core在Compare真实结束的finally调用TakeResourceUsage一次，将snapshot纳本次case资源账后删除该条；取错身份/重复取报0001，不误取另一run。源/共享allocation按唯一Owner计费，Engine与Comparer的native峰值由同协调器时间水位观察，不能相加不同时刻峰值；两者任务无同时水位证据时相应字段NotObserved/null。最后报告仍沿§5排空/释放后生成，诊断模块不代预算Owner。原纯值策略无此扩展时没有native比较资源，Core计其自己的托管/读取费用。R-C35另断言artifact比较是实际像素而非hash、超预算分配前拒、资源finally汇总且Compare迟到归原Root。

### 10.2 原节点 Engine、HALCON搬运与大图执行

```csharp
public sealed record ReplayNodeRegistration(string NodeType, string Revision,
    ImmutableArray<string> InputSchemas, ImmutableArray<string> OutputFields,
    bool SupportsCheckpoint, ReplayEngineCapabilities Capabilities);
public interface IReplayIsolatedNode {
    ReplayNodeRegistration Registration { get; }
    ValueTask<IReplayCaseExecution> StartAsync(
        ReplayExecutionContext context, IReplayEvidenceReader reader, CancellationToken ct);
}
public sealed class ReplayRegisteredEngine : IReplayExecutionEngine {
    public ReplayRegisteredEngine(ReplaySubjectBinding subject,
        IReplayEvidenceReader reader, ImmutableArray<IReplayIsolatedNode> nodes,
        ReplayEngineCapabilities capabilities);
}
public sealed record ReplayImageRun(long Row, long BeginColumn, long EndColumnExclusive);
public sealed record ReplayImagePlane(int Index, string ScalarType, long RowBytes,
    string ByteOrder, ImmutableArray<string> Channels, ContentRef Bytes,
    ImmutableArray<ReplayImageRun> ValidRuns);
public sealed record ReplayImageManifest(string Schema, long Width, long Height,
    ImmutableArray<ReplayImagePlane> Planes, string Unit,
    string CoordinateId, string CoordinateRevision, ContentRef? Pyramid);
public sealed record ReplayHalconOptions(long MaxWidth, long MaxHeight,
    int MaxChannels, int MaxDomainRuns, long MaxCopyBytes, int TileWidth, int TileHeight);
public static class ReplayHalconEngineFactory {
    public static IReplayExecutionEngine Create(ReplaySubjectBinding subject,
        IReplayEvidenceReader reader, ImmutableArray<IReplayIsolatedNode> approvedNodes,
        ReplayHalconOptions options, ReplayEngineCapabilities capabilities);
}
```

Factory在Asun.Modules.Replay.AsunImage，无native在公共DTO，approvedNodes是可信组合根显式已登记的原算法能力对象（其它模块公开端口的本方薄adapter，不从DLL名/JSON反射加载）；Registration(NodeType,Revision)唯一ordinal，Graph每node的类型/修订/inputs/outputs必须完全匹配，不能按最接近节点替代。默认不支持任意checkpoint、未登记3D/Region/XLD专业比较0013；每已批准原节点消费者自己提供真实NodeType/资产/物理业务输出，不代表Replay缺未定义的“通用算法”。RegisteredEngine按Graph拓扑逐节点await，case内首版串行，跨case使用原MaxConcurrency，原Task/执行句柄/lease由case Owner强持至真实Drain；读取/模型注册不获生产写权限。只有RegisteredEngine所有注册能力一致可声明BitwiseSameEnvironment，否则降为显式能力/拒不满足请求，不能悄悄改request.Runtime。

本方固定可实施image manifest schema=replay-image-v1，Width/Height正≤Options，planes按Index从0连续，ScalarType只byte/uint2/int2/int4/real，ByteOrder=little，单plane单channel rows tight（RowBytes=Width*sampleBytes）且Bytes长度=RowBytes*Height，无隐含stride/padding。RGB为三个明确R/G/B单plane，不猜多通道；channel身份/单位/坐标完整；此image-v1要求非空CoordinateId/CoordinateRevision，即使旧数值比较字段允许坐标null，也不能把缺坐标的图像改为identity。ValidRuns半开、有序、非重叠相邻合并、0≤row<height、0≤begin<end≤width，空数组=空域不是Full；Full也逐行明确runs，超MaxDomainRuns拒而不造满域。大图Pyramid只能是既有图像源Owner的精确level/tile/中心映射引用，首版replay-image-v1全图bytes不假称随机压缩tile可访问；不能从缩略图恢复原采样。不同codec源由Reader公开只读适配成该manifest，保持原父引用/长度hash；未知复杂/64bit/多allocation数据拒0013，不以有损转float盖Exact。

CPU搬运路线（HALCON26.05官方依据，调用均ImageLibDotNet.cv2）：
1. Reader有限页/行buffer取得稳定只读原字节，逐stream核完整长度/hash/真实域；checked估算源、tight copy、native plane/domain/temp差图/编码缓冲/旧新并存，超Budget/Options在分配前0006。MaxCopyBytes是本方上限，不能冒native实际allocator观测；实际HALCON transient峰值另测。原plane先用<=Service.MaxReadBytes的独立buffer完整流式核hash，不为核hash分配全图；稳定原lease保持到第二次读取结束，防TOCTOU。核成功后全图路线才分配tight副本；tile路线在同稳定lease按行读取窗口，source不支持有界Seek则顺序扫行仅保当tile行缓冲，额外扫描计Load/IO。source不能保证原bytes稳定时拒0002，不用未核全图的局部tile先发结果。输出tile写本Store受预算的未封存工程暂存，逐stream增量hash、全覆盖验证后一次发布原ContentRef；暂存/索引/磁盘容量与cleanup须Profile显式允许，缺能力拒0006/0013，不靠全图数组或无限临时文件。
2. 每plane内存pin住本方tight little-endian副本→gen_image1(Type,Width,Height,实际64bit地址)→原调用**真实返回后**unpin。gen_image1复制而不借用源pointer，禁止gen_image1_ex；多plane仅明确RGB可用compose3（结果域为三输入域交集、共享原plane存储，保活三输入）；其它channel逐plane处理。端序不是little拒0002，不猜平台。
3. gen_region_runs(rows,begin,endExclusive-1)→reduce_domain，空runs显式gen_empty_region，不依HALCON全局empty结果设置。HALCON row/column=源整数中心(row,column)，Pixel boundary半开只在run转换一次；Domain不能为空当“0误差”。原处理/模型固定节点按其唯一算法指导执行，本方不训练prepare历史模型；工程差走§20已固定顺序/类型提升/tile halo=0。
4. 导出不可变工程artifact按count_obj=1、count_channels→access_channel→get_image_pointer1(Type,width,height)→get_domain→get_region_runs，核3tuple等长/上限及closing end+1 checked转换；仅在原channel/object真实存活期间只读逐行复制，不经pointer写共享矩阵，reduce_domain共享底图也不写。原source借用直到copy/编码IO真实退出，再Dispose channel/domain/tuple/image。输出是完整原值image manifest/bytes的新ContentRef，不拿渲染截图/灰度拉伸当原证据；失败/晚到只回本方未交付产物，已封存不删。
5. 大图工程差默认逐tile原分辨率同域/同halo0且严格全覆盖，各tile按同样HALCON路线，maxAbs/maxResidual取全tile最大，domain差异area按tile整数像素计数checked long累加无重复；全图像素量先checked Width*Height，溢出拒0001，不用double累加吞掉整数； tile边界半开不漏最后一列/行，Count/width/height/hash不同0002，不降采样找相等。只有原节点本身声明tile equivalence/边界上下文时才tile其执行，否则全图预算不足直接0006；不拆模型/坐标算法以省内存。
6. 非中断native任务不能被ct终止；Deadline/close封后续节点，原Task/native source强持交同Root、Drain false/Unknown，真实返回再按原ID封存结果或弃晚到副本。Device/Production side effect检测0018沿原规则。实际图像结果与native池退款分开，返回Task不证明GPU完成；options/capabilities明确CPU默认，GPU候选仅在原Profile资格声明。

依据本轮直接读取[gen_image1](../../../halcon算子手册/operators/gen_image1.html)、[get_image_pointer1](../../../halcon算子手册/operators/get_image_pointer1.html)、[get_region_runs](../../../halcon算子手册/operators/get_region_runs.html)、[gen_region_runs](../../../halcon算子手册/operators/gen_region_runs.html)、[gen_empty_region](../../../halcon算子手册/operators/gen_empty_region.html)、[compose3](../../../halcon算子手册/operators/compose3.html)：gen_image1新建存储后可释放源pointer；get_image_pointer1仅图像变量存活时有效且域共享矩阵不能写；get_region_runs仅单Region、空域返回三个空tuple；gen_region_runs不检查end≥begin故本方先验证。§18固定来源/HALCON证据沿用，无新增第三方视觉算法。C#参数类型/重载实现时在消费程序集编译确认仅是签名验证，不重开依赖核验；本文确定算法/封送/Owner，不要求开发者猜。

### 10.3 原事实只读、持久/隔离 worker 与导出恢复责任

以下worker声明在Asun.Modules.Replay.Adapters，导出声明消费§11.4原IReplayExportSink，位于Asun.Modules.Replay.Wpf的非Control实现；均不要求隐藏窗口初始化。公共值不含native/进程/连接句柄。

```csharp
public interface IReplayWorkerPort : IReplaySubjectScoped {
    ReplayEngineCapabilities Capabilities { get; }
    Task<IReplayCaseExecution> SubmitAsync(ReplayExecutionContext context, CancellationToken ct);
    Task<ReplayCaseLookup> QueryAsync(string requestId, string caseId, long generation,
        CancellationToken ct);
    Task<ReplayDrainStatus> StopAndObserveAsync(string requestId, string caseId,
        long generation, TimeSpan observeBudget);
}
public sealed class ReplayWorkerNodeAdapter : IReplayIsolatedNode {
    public ReplayWorkerNodeAdapter(ReplayNodeRegistration registration,
        IReplayWorkerPort worker, IReplayEvidenceReader reader);
    public ReplayNodeRegistration Registration { get; }
    public ValueTask<IReplayCaseExecution> StartAsync(ReplayExecutionContext context,
        IReplayEvidenceReader reader, CancellationToken ct);
}
public enum ReplayExportCommitStatus { Committed, NotCommitted, Unknown }
public sealed record ReplayExportCommit(string RequestId, string HostDestinationId,
    string ResultDigest, ReplayExportCommitStatus Status, ImmutableArray<ReplayError> Errors);
public interface IReplayExportDestination : IReplaySubjectScoped {
    Task<IReplayExportStage> BeginAsync(string requestId, string destinationId,
        string resultDigest, CancellationToken ct);
    Task<ReplayExportCommit> QueryAsync(string requestId, string destinationId,
        string resultDigest, TimeSpan observeBudget);
}
public interface IReplayExportStage : IAsyncDisposable {
    Task WriteAsync(string logicalObjectName, ContentRef content, Stream source,
        CancellationToken ct);
    Task<ReplayExportCommit> CommitAsync(CancellationToken ct);
    Task<ReplayExportCommit> QueryAsync(TimeSpan observeBudget);
}
public sealed class ReplayEngineeringExportSink : IReplayExportSink {
    public ReplayEngineeringExportSink(ReplaySubjectBinding subject, IReplayAssetCatalog catalog,
        IReplayExportDestination destination, IReplayAuthorization authority,
        ReplayCodecLimits codecLimits, ReplayServiceOptions serviceOptions);
    public ReplaySubjectBinding BoundSubject { get; }
    public Task<ReplayExportReceipt> ExportAsync(ReplaySubjectBinding subject,
        ReplayResult sealedReport, string hostDestinationId, CancellationToken ct);
}
```


本模块原事实永远只读；source AssetCatalog与program node ports不包含WriteFact/DeviceCommand。StoreMutation输出仅工程域，OriginalDigest/parent引用保留，Sim fault只能改本方副本/通知，不污染输入。权限Check的角色/期限/租户事实仍由既有authorization Owner，Replay scope facade只校验不缓存历史Allow。实际部署采用本地/远端/文件/数据库介质是宿主Profile输入，不改变上面mutation/CAS合同；无真实持久端口只能标进程内，不能承诺crash恢复。

隔离worker是选择使用无法中断/可崩溃后端时的**宿主预启动**公开受控节点adapter，Replay Core不启动任意exe/DLL。本方ReplayWorkerNodeAdapter公开构造(registration, IReplayWorkerPort worker, reader)，worker端口必须提供SubmitAsync(ReplayExecutionContext,ct)→IReplayCaseExecution、QueryAsync(requestId,caseId,generation,ct)→ReplayCaseLookup、StopAndObserveAsync(requestId,caseId,generation,TimeSpan budget)→ReplayDrainStatus，caps.IsolatedWorker=true、支持schema/版本/最大bytes逐项核；StartAsync的reader须与构造reader为同scope原实例，否则0001零提交。Query只恢复原提交回执，Found不重新执行；Submit原Task丢回应仍由worker/root持借用，进程确认死亡+IPC/lease真实归还才DrainReleased，不能以连接断开/ProcessKill事件当释放。payload仅本DTO规范值/ContentRef，消息单frame上限=Codec.MaxDocumentBytes，接收body长度/hash/schema/租户/原generation逐项校验；worker端口实际IPC/OS/HALCON运行时由部署Owner与其SDK包提供，所需软件可观测性/恢复请求已冻结，未具上述能力0013明确不支持worker用途。真实进程/断电资格保持。

ExportSink目标永远是宿主授权HostDestinationId逻辑键，Core不拼盘符。规范工程导出按上述ReplayEngineeringExportSink构造；destination/stage的明确三态回执见本节声明，每call经原Root预登记。catalog必须是同主体授权的输入/工程输出内容联合只读视图，不能只读原输入而丢新报告/页。报告按§9.1原result canonical envelope生成规范bytes及新ContentRef（原ResultDigest核相同），逻辑名report.json；完整case-results及页按cases/<SHA256>.json、允许工程artifact按artifacts/<SHA256>.bin，SHA256先按规范小写64hex校验，重复同digest仅一次写。遍历报告→完整case-results及其页→所选允许工程artifacts；目录/hash先核完，未允许对象不导出，逻辑名只能上述registered relative key禁止../绝对路径，chunk按serviceOptions.MaxReadBytes逐授权/长度hash校验，原source不写。Commit幂等键=(tenant,request,destination,resultDigest)，同digest原回执、异0016；Unknown查原stage不重复导出/重写。Begin回执不明由destination.Query按原三元身份查，不重Begin；Query用独立[50ms,10min]预算=min(Service.IoTimeout,本次剩余cleanup观察预算)，不复用已取消业务ct。Commit.Status=Committed只在完整对象长度/hash核实、原子目标采用及介质承诺均有权威回执时成立；NotCommitted仅已知未采用且Errors解释拒绝/失败，Unknown必含0014（撤权0005可并列），不能当未导出。映§11.4旧ReplayExportReceipt：Committed为true/Errors空；NotCommitted为false/无0014；Unknown为false/含0014，Controller按错误分类显示“导出结果待确认”，禁止仅用bool判失败。三态原回执在Root/Host保持，目标不存在返回NotCommitted，无法查返回Unknown。ct/撤权停止新chunk，原stream/Write/Commit真实结束再stage cleanup；cleanup不取消已提交事实，未commit暂存由destination Owner撤本方stage，不能删旧报告/客户文件。无完整允许资产/真实destination Profile时CanExport=false+具体缺项，不代表本方缺导出算法。

## 11. 可选 Replay Workbench PageContract

### 11.1 角色、布局和联动

可选控件 ReplayWorkbench 位于独立 Asun.Modules.Replay.Wpf 程序集（net10.0-windows/UseWPF），不放Core。消费者为算法工程师和客户问题复现支持工程师；先查证据/缺项，再选用途/变更，预检，运行，按身份查看差异，导出工程报告。查看者仅查报告；预检/开始/取消/导出权限分别由宿主给出，权限撤销更新命令并交Core再次检查，不按按钮是否隐藏证明权限。

固定1920×1080物理验证画面，扣除实际任务栏/窗框/标题/宿主状态栏测客户区，不改显示设置。布局单位为WPF DIP；客户区比例分配，禁止假设1080全是内容高度。顶部两行紧凑状态与命令（各约36 DIP），底部约28 DIP状态，内容剩余部分：
- 左侧约18%：案例导航/用途筛选、六分类计数和缺项标记，固定身份列；批量选择只生成Scope草稿，不能改既有运行。
- 中部约60%：原/候选两幅图并排优先，标题显示版本、单位/坐标/有效性；下部约30%内容高度为差异Grid，身份、字段、原值、候选值、差值、标签、证据列。文本不与影像叠盖。
- 右侧约22%：默认收起的变更/依赖/时间线文档页；高级设置展开不挤掉取消和状态。原参数只读，候选草稿逐项给Before/After、Unit、Reason/Author，经预检冻结。
- 状态条保持阶段、分母、完成/未知数、资源、排空状态和诊断码；Progress不代表PASS。图像区域不能用模拟随机图冒充证据。

采用本机25.2.3的 DockLayoutManager + LayoutGroup/LayoutPanel/DocumentGroup 构成可恢复工作台，DXTabControl区分“变更/依赖/时间线”，GridControl + TableView用于差异和案例，BarManager/BarButtonItem保持关键命令。TableView.AllowPerPixelScrolling=true，DataViewBase.AllowEditing=false；NavigationStyle按单元格键盘导航配置，ShowSearchPanelMode显示搜索；通过GridControl.SelectionChanged把稳定CaseId/FieldId投影到两图、详情与时间线。禁止行号或显示顺序作为联动键。参数草稿使用独立字段编辑，不把结果Grid变可编辑。

按CaseId请求§4分页；Grid当前加载页与总计数明确区分。搜索/筛选全报告由宿主的报告索引适配器或逐页流式消费提供，不把仅已加载100行误称“全部无差异”。选择/筛选不改变固定分母或报告digest。图像缩放/平移以同坐标版本时才联动；坐标不匹配显示锁定原因，允许独立查看，不能自动配准以藏差异。双图请求异步取消与generation绑定，迟到显示任务仅释放自身显示lease，不覆盖新选择。可选像素差异/叠加为DiagnosticOnly，主图坐标和摘要始终可见。

布局用宿主注入的主题/图标/字号资源，浅/深由统一主题控制；8/12 DIP间距、对齐列、单一强调色，状态同时用图标/文字/颜色，不仅红绿。只对展开/加载反馈做短动效，错误、取消/排空文字立即更新，不动画掩盖资源状态。布局保存为宿主用户偏好并带控件版本，不携带客户证据/token；损坏布局恢复内置构图，不重置用户配方/配置。

### 11.2 输入和控件公共能力

```csharp
// Asun.Modules.Replay.Wpf；这是规划声明，不是现有控件API。
public sealed record ReplayUiPermissions(bool CanInspect, bool CanStart,
    bool CanCancel, bool CanExport);
public sealed record ReplayRunSnapshot(ReplaySubjectBinding Subject,
    string RequestId, string? ReplayRunId, long? Revision, string? ContractRevision,
    ReplayLookupState Lookup, ReplayState? State, ReplaySummary? Summary,
    ContentRef? CaseResults, ImmutableArray<ReplayError> Errors, bool ResourcesReleased);
public interface IReplayWorkbenchController : IReplaySubjectScoped {
    ValueTask<ReplayRunSnapshot> QueryAsync(string requestId, CancellationToken ct);
    ValueTask<ReplayPreflightResult> PreflightAsync(ReplayRunRequest request, CancellationToken ct);
    ValueTask<ReplayStartResult> StartAsync(ReplayRunRequest request, CancellationToken ct);
    ValueTask CancelAsync(string requestId, CancellationToken ct);
    ValueTask<ReplayCasePage> ReadCasesAsync(ContentRef manifest, int offset, int size, CancellationToken ct);
    ValueTask ExportAsync(string requestId, string hostDestinationId, CancellationToken ct);
}
```

ReplayWorkbench为UserControl，公开void Bind(IReplayWorkbenchController,ReplayUiPermissions)、void SetSnapshot(ReplayRunSnapshot)、void SetCulture(string cultureName)及ValueTask DetachAsync(CancellationToken)；Bind重复前必须Detach，SetCulture支持zh-CN/zh-TW/en-US，未知文化保留当前并显示可恢复诊断。Bind锁定Controller.BoundSubject；SetSnapshot要求Subject与该绑定完全相同、Revision来自§4.2快照，低修订同操作不得覆盖高修订，授权拒绝投影须清旧客户结果/图像并保留通用错误。切主体必须Detach再以新controller绑定，不能只改CanInspect或Author。方法在控件Dispatcher调用，Controller操作异步、不捕获Core同步上下文；Detach撤订阅并等显示回调退出/归还，只detach本实例，不取消宿主其它会话。Snapshot为不可变投影，控制器是宿主装配的ReplayWorkbenchController，不持有生产权限。Export仅导出已封存报告及允许证据，hostDestinationId由宿主选择/授权，不来自任意相对路径。

影像由宿主既有viewport公开控件接入：控制器将ContentRef交宿主的只读证据视图适配器，适配器获得独立显示租约并负责关闭/失败归还，Workbench只传CaseId/证据引用/坐标，不传HObject。实际双图按§11.5消费viewport公开端口；本文冻结装配与Owner，真实接口消费编译/运行仍单独验证，不阻Core/WPF布局与文本行为切片。Host只能在BindingsReady后开启图像联动；无证据/不支持schema时保留缺项文字和差异表，不画替代图。

### 11.3 命令、键盘、三语与恢复

| zh-CN / zh-TW / en-US | 启用条件与反馈 |
|---|---|
| 预检 / 預檢 / Check | 有合法草稿和查看权限；缺项定位字段/证据 |
| 开始 / 開始 / Start | 预检有效、可执行权限；Start仍再校验；运行中禁重复提交 |
| 取消 / 取消 / Cancel | 本宿主拥有的非终态会话且授权；点击显示“正在停止接纳，等待排空” |
| 查看排空 / 查看排空 / View drain | 运行/Draining/Unknown；查原请求，不重放 |
| 导出工程报告 / 匯出工程報告 / Export engineering report | 权威已封存结果+导出权限；Unknown/半写无报告禁止导出 |
| 缺少证据 / 缺少證據 / Evidence missing | 列缺项与影响案例，提示补齐后新实验 |
| 无法比较 / 無法比較 / Incomparable | 单位/坐标/有效性原因和策略版本可见 |
| 等待排空 / 等待排空 / Waiting for drain | 保留运行ID，提示继续查看状态 |
| 结果待确认 / 結果待確認 / Outcome unknown | 仅查原请求/查看诊断，不提供盲重试 |

Tab顺序：用途/范围 →变更→预检→开始→取消→案例→双图→差异→详情→导出；Ctrl+F进搜索，F6在导航/图像/差异/详情轮转，Enter仅执行聚焦命令，不在编辑IME组合中启动；Escape取消草稿编辑，不取消计算；Ctrl+Shift+C触发取消需当前会话权限，禁止占用系统快捷键。错误后焦点回到首个错误字段；运行期间保留取消可达，页面关闭重开按RequestId恢复快照，不丢身份。BarItem.SuperTip解释取消只停止接纳、Export隔离域、诊断对齐不改主比较；三语覆盖列头、工具提示、枚举、错误/恢复、空表、分页和原生搜索/筛选菜单，自定义本地化按宿主localization公开实例接口，不写DevExpress全局Active。

SetCulture保留选中ID、筛选、滚动、草稿和活动编辑，不重建会话/重算；机器码、单位代码、hash不翻译，显示格式按文化但内部规范值不变。UIA为图像、状态、命令和差异格提供名称/状态/禁用原因，状态更新合并朗读避免每Progress刷屏。UI性能Profile单列页大小、图像字节、更新合并频率/队列上限及响应目标来源，限制显示缓存/取消旧显示任务，不用Dispatcher阻塞Wait/GetResult。真实WPF测试仅固定1920×1080，在现有DPI记有效客户区并检查三语最长标题、键盘/UIA、布局恢复、同进程双控件和关闭后迟到回调；未执行，不能以Core/harness/截图代替。

### 11.4 Controller、Bridge 与双 STA 的确定装配

本模块提供ReplayWorkbenchController（Wpf程序集中的纯异步投影适配器，不持native），ReplayWorkbenchBridge（实例Dispatcher投影/解绑Owner）和控件；不要求每Host再猜Controller实现。Controller只转发Root已登记的原Task、调用§4授权及实例ExportSink，生成ReplayRunSnapshot，不复制比较/统计/产品判定。图像接线为宿主已有viewport公开端口的显示Adapter，Replay不定义第二viewport/坐标/渲染API；固定WPF自身验证明确不启用图像，仍可完整验证差异表/任务/恢复/三语。

```csharp
// Core追加生命周期参与者端口；没有WPF依赖。
public interface IReplayRootParticipant {
    long RetainedBytes { get; }
    Task RequestCloseAsync();
    Task<ReplayDrainStatus> DrainAsync(TimeSpan observeBudget);
    Task DisposeAsync();
}
// ReplayProcessRoot分节声明同一类型，不是第二个Owner。
public sealed partial class ReplayProcessRoot {
    public void AttachParticipant(ReplayRootTicket ticket, IReplayRootParticipant participant);
    public Task<T> InvokeParticipantAsync<T>(ReplayRootTicket ticket, Func<Task<T>> operation);
    public Task CancelAsync(ReplayRootTicket ticket, CancellationToken ct);
    public Task<ReplayPreflightResult> PreflightAsync(ReplayRootTicket ticket,
        ReplayRunRequest request, CancellationToken ct);
}

// 以下在Asun.Modules.Replay.Wpf。
public sealed record ReplayExportReceipt(string RequestId, string HostDestinationId,
    bool Committed, ImmutableArray<ReplayError> Errors);
public interface IReplayExportSink : IReplaySubjectScoped {
    Task<ReplayExportReceipt> ExportAsync(ReplaySubjectBinding subject,
        ReplayResult sealedReport, string hostDestinationId, CancellationToken ct);
}
public sealed class ReplayRejectedExportSink : IReplayExportSink {
    public ReplayRejectedExportSink(ReplaySubjectBinding subject);
    public ReplaySubjectBinding BoundSubject { get; }
    public Task<ReplayExportReceipt> ExportAsync(ReplaySubjectBinding subject,
        ReplayResult sealedReport, string hostDestinationId, CancellationToken ct);
}
public sealed record ReplayWorkbenchOptions(int MaxVisibleCases, int MaxPendingUpdates,
    long MaxDisplayBytes, TimeSpan UpdatePeriod, TimeSpan UiObserveBudget,
    bool EnableEvidenceImages);
public sealed class ReplayWorkbenchController : IReplayWorkbenchController {
    public ReplayWorkbenchController(ReplayProcessRoot root, ReplayRootTicket ticket,
        IReplayAuthorization authority, IReplayExportSink exportSink);
}
public sealed class ReplayWorkbenchBridge : IReplayRootParticipant {
    public ReplayWorkbenchBridge(System.Windows.Threading.Dispatcher dispatcher,
        ReplayWorkbench view, IReplayWorkbenchController controller,
        ReplayProcessRoot root, ReplayRootTicket ticket, ReplayWorkbenchOptions options);
    public Task BindAsync(ReplayUiPermissions permissions, string cultureName);
    public Task RefreshAsync(string requestId, CancellationToken ct);
    public Task SetCultureAsync(string cultureName);
    public Task UnbindAsync();
    public long RetainedBytes { get; }
    public Task RequestCloseAsync();
    public Task<ReplayDrainStatus> DrainAsync(TimeSpan observeBudget);
    public Task DisposeAsync();
}
public sealed class ReplayWorkbench : System.Windows.Controls.UserControl {
    public ReplayWorkbench();
    public void Bind(IReplayWorkbenchController controller, ReplayUiPermissions permissions);
    public void SetSnapshot(ReplayRunSnapshot snapshot);
    public void SetCulture(string cultureName);
    public ValueTask DetachAsync(CancellationToken ct);
}
// WPF TestHost命名空间Asun.Modules.Replay.Wpf.Testing。
public sealed class ReplayStaHostLifetime : IReplayRootParticipant {
    public ReplayStaHostLifetime(System.Threading.Thread thread,
        Task ready, Task exited);
    public void BindDispatcher(System.Windows.Threading.Dispatcher dispatcher);
    public long RetainedBytes { get; }
    public Task RequestCloseAsync();
    public Task<ReplayDrainStatus> DrainAsync(TimeSpan observeBudget);
    public Task DisposeAsync();
}
```

Root.AttachParticipant在Bind之前纯内存原子接收，必须占预留retainedByteCeiling内的字节和Task上限，失败保证未转移；Bridge构造不注册事件、不调用Dispatcher、不取图像lease，故Attach失败可无异步资源地弃用Bridge。Attach成功后Root强持Bridge、Controller、控件、Dispatcher及原DispatcherOperation.Task；InvokeParticipantAsync内部先预登记再调用delegate，支持Task<T>及以bool为无结果回执的任务。不允许先发Dispatcher操作再登记Task。Close时先关闭所有participant准入/撤显示，等各自Drain/Dispose及排队回调退出，再Service Dispose/Hold释放；内存强引用不代表Dispatcher仍有泵，宿主必须让原STA继续Dispatcher.Run，直到该STA全部参与者确认解绑。

Options硬域：MaxVisibleCases>=1且<=ServiceOptions.MaxReadPageSize，MaxPendingUpdates>=1，MaxDisplayBytes>=1，UpdatePeriod/UI观察预算在[50ms,10min]；EnableEvidenceImages=false时不能加载影像/native。固定双STA验证=(1,4,65536,100ms,2s,false)，实际图像功能只在现有viewport Adapter装配后按预算开启。资源标识/状态/错误的三语键在Wpf自身Resources/ReplayText.{zh-CN,zh-TW,en-US}.resx，ResourceManager实例按CultureInfo查；默认实例zh-CN，未知culture保留原值+REPLAY-0001。机器代码不翻译；DevExpressGrid本机25.2.3 AllowEditing=false；差异表NavigationStyle=Cell、案例导航表NavigationStyle=Row，分页一页，控件元素本地标注UIA名称，不设置全局DevExpress Localizer.Active/线程静态culture。上游localization能接入宿主实例文化事件，但自身三语与Bind不等待它实施。

Controller构造核ticket.Subject、Authority、ExportSink.BoundSubject完全匹配；Root内部Service属该ticket，只允许本RequestId，Query/Cancel不同ID拒0005不泄漏。QueryAsync由Root.QueryOperationAsync映射快照，Summary/CaseResults只有已授权Result存在才给；Revision/ContractRevision取原快照。ResourcesReleased只能来自同槽可信Drain或同权威状态证据，不能从Found/Completed字样猜释放。Preflight用Root预登记的Service.PreflightAsync（Root另公开Task<ReplayPreflightResult> PreflightAsync(ticket,request,ct)，只用于本slot草稿）；Start转Root.StartAsync一次；ReadCases转Root.ReadCasesAsync；Cancel转Root.CancelAsync并做Cancel授权，关闭观察不是Cancel。Export先Root Query原ID已封存报告，再Check(Export,精确report/允许对象/HostDestinationId)，把原ExportSink Task预登记于Root；Sink逐对象/目标检查当前授权、保存工程隔离输出，返回Committed=false/Unknown时同RequestId和destination查宿主导出Owner，不盲重导。固定自身UI用ReplayRejectedExportSink(subject)，公开构造该subject，ExportAsync返回Committed=false/0005，BoundSubject=subject；因此CanExport=false，不伪造导出。正式Sink属于宿主，无产品处置权。

Bridge.BindAsync必须先确认Root已拥有它，然后以InvokeParticipantAsync预登记调用Dispatcher.InvokeAsync：原dispatcher内view.Bind(controller,permissions)→view.SetCulture(culture)，绑定generation+1、锁定主体；控件默认构造的空状态没有隐藏初始化。RefreshAsync在UI外做Controller.QueryAsync和页读取，原Task均Root登记；每个呈现Dispatcher回调在执行前复核当前generation/主体/§4.0 Inspect授权。Controller取消或撤权得到0005仍投递**脱敏清空**快照，清Summary/CaseResults/图像，不保留旧结果显示；异常也按本RequestId显示通用恢复提示。排队上限4，状态/拒绝/清空不得丢；普通progress合并至最新、慢Dispatcher背压，不临时无界Task.Run。快照revision旧值/错误主体不采用，重复同revision幂等。

UnbindAsync立即封Bridge的Refresh/SetCulture/新Bind接纳、generation失效、撤实例事件；预登记原view.DetachAsync Task（在原Dispatcher异步调用一次），等待原在途Query/Read/显示lease和回调返回，最后清controller/view绑定；不取消别人Existing计算，不Dispose共享Coordinator/Store。Detach内ct只撤观察；Bridge内部Unbind没有业务ct，前台用UiObserveBudget有限等待，原Unbind Task始终Root持有。Root两轴清理纳入该participant，在释放失败时BackgroundOwned；Dispatcher不可用/关闭中不能宣布解绑完成，拒该Root后续新UI准入并保持资源句柄，原线程仍泵/宿主恢复处理。重复Unbind/Dispose复用原关闭Task；重新Bind必须原解绑确认后新Bridge或新generation，不能复活旧引用。

**双STA具体装配与验收顺序（独立WPF测试入口，仍未执行）：**

1. 进程入口建§12固定Root但MaxSlots=2、MaxRetainedBytes=1048576，Coordinator相同；A使用Regression输入/主体、B使用Customer输入/主体，分别TryReserve→独立Authority/Reader/Resolver/Engine/Comparison/Store/Clock/Hold→Root.CreateAsync。hold.RetainedBytes=65536，另外Bridge上限65536，仍在每槽262144内。两份纯托管Host结果先满足§12.4。
2. 创建两个Thread，将ApartmentState设STA**后**Thread.Start；入口第一件事取得Dispatcher.CurrentDispatcher，new ReplayWorkbench()/new Window，Window.Content=view，建立ReplayWorkbenchController(root,ticket,authority,new ReplayRejectedExportSink(subject))及ReplayWorkbenchBridge(dispatcher,view,controller,root,ticket,fixedOptions)，Root.AttachParticipant，然后注册ready的TaskCompletionSource（RunContinuationsAsynchronously）、Closed事件与原线程退出Task到participant内部持有。ready信号携Bridge，之后Dispatcher.Run；不在ThreadPool创建WPF，不把一个Dispatcher传两控件。
3. 外层按2s有限观察ready，Root从启动前已通过另一个线程participant持Thread、ready/退出原Task；线程启动抛错仍回原Root清理，ready到期不能丢线程或提前关闭hold。线程participant是WPF TestHost对IReplayRootParticipant的具体实现ReplayStaHostLifetime(Thread,Task ready,Task exited)，与公开声明统一为三参数，不增加Dispatcher构造重载；构造只强持无UI/启动，在Thread.Start之前AttachParticipant。进入STA后取得Dispatcher.CurrentDispatcher，并调用该实例BindDispatcher(dispatcher)一次，不使用静态全局。退出Task只在线程真实finally后完成。
4. A调用Bridge.BindAsync(new(true,true,true,false),"zh-CN")，B同permissions但culture="en-US"，分别RefreshAsync原ID；A SetCultureAsync("zh-TW")后B仍en-US且保持所选case-01/分页。A/B各自RequestId/Revision/分类严格匹配Golden，不显示对方CaseResults。让A的Query闩锁/排队呈现阻塞，B仍Refresh/键盘可用；以闩锁释放验证迟到generation只诊断不写A新绑定。
5. A撤权并Refresh原ID，A旧客户投影清空/0005，B仍原摘要；A关闭调用UnbindAsync而不取消B。close按钮事件只先Cancel=true/隐藏窗口显示“关闭未完成”，将原Unbind Task交Root后有限观察；Task未完不调用Dispatcher.InvokeShutdown。A的STA直到Unbind/participant退出就绪才Dispatcher.BeginInvokeShutdown并完成线程exited；**线程寿命participant的Drain以UI回调/Unbind就绪为条件，Dispose触发Dispatcher退出再等exited，避免等线程退出才允许Shutdown的环**。Core Root据Dispose真实完成归还hold。
6. 反例：Bind/Query/Read/呈现委托/Detach抛错、Dispatcher队列满、撤权后迟到快照、第二次Bind未Unbind、错误Subject、慢Dispose、STA ready到期；前台有限返回，Root确认BackgroundOwned并同IDQuery/Drain；测试显式释放闩锁后ResumeCleanup，最终每个显示/Store/hold一次归还、两个STA线程真实退出。禁止强杀线程、把Window.Closed=资源释放或Clear控件=Detach完成。
7. 两窗口按当前屏幕已有DPI、**同一固定1920×1080验证viewport**内顺次激活验证（另窗口可隐藏但STA/Root不销毁），扣除任务栏/标题/状态栏；不改用户显示设置、不做其它分辨率矩阵。真实WPF验证包括三语长文本、UIA/键盘、实例隔离、取消/排空文字及关闭迟到回调。以上为内部可实施装配规格，实际viewport图像接线与真实UI运行按各自门验证，不能把Controller/Bridge装配欠账转写现场门。

### 11.5 双图的实际 viewport WPF Assembly v0.2 接线

Replay实际消费viewport WPF，不再把显示接线全部留为未来Host决定。本节只消费该唯一指导最新§10.6～10.9 Assembly v0.2及§15.2.2公开CPU源工厂（当前0.3.5-prep，兼容v0.2），不复制Backend/Presenter/Return/Root/Close算法。ReplayRoot和ViewportRoot分别持本方资源账，组合根强持二者至真实关闭；同binding的renderer端口来自同Control，不借另一窗口或scope。

```csharp
// Asun.Modules.Replay.Wpf；依赖仅在可选WPF/显示Adapter包。
public sealed record ReplayViewportOptions(string BindingPrefix,
    long MaxSourceBytes, long MaxDisplayBytes, long MaxRasterBytes,
    int MaxSources, int MaxInFlightTiles, TimeSpan UiBudget);
public interface IReplayDisplayPublisher : IReplaySubjectScoped {
    Task<ReplayDisplayPublication> PublishAsync(string requestId, string caseId,
        ContentRef image, CancellationToken ct);
    Task<ReplayDrainStatus> RetireAsync(string publicationId, TimeSpan budget);
}
public sealed record ReplayDisplayPublication(string PublicationId, ContentRef Original,
    Asun.Modules.ImageFrame.Resources.FrameDescriptor Frame,
    Asun.UI.Viewports.ImageSourceDescriptor Image, string PixelSpace);
public sealed record ReplayViewportPorts(
    Asun.Modules.ImageFrame.Resources.IFrameService Frames,
    Asun.UI.Viewports.IAuthorizationPort Authorization,
    Asun.UI.Viewports.IViewportResourceAdmission? Admission,
    IReplayDisplayPublisher Publisher);
public sealed class ReplayViewportBridge : IReplayRootParticipant {
    public ReplayViewportBridge(ReplayProcessRoot replayRoot, ReplayRootTicket ticket,
        Asun.UI.Viewports.IViewportProcessRoot viewportRoot,
        Asun.UI.Viewports.Wpf.ViewportControl originalControl,
        Asun.UI.Viewports.Wpf.ViewportControl candidateControl,
        ReplayViewportPorts ports, ReplayViewportOptions options, bool offlineEngineering);
    public Task BindAsync(string cultureName);
    public Task ShowAsync(string requestId, string caseId,
        ContentRef? original, ContentRef? candidate, CancellationToken ct);
    public Task ClearAsync();
    public Task SetCultureAsync(string cultureName);
    public Task UnbindAsync();
    public long RetainedBytes { get; }
    public Task RequestCloseAsync();
    public Task<ReplayDrainStatus> DrainAsync(TimeSpan observeBudget);
    public Task DisposeAsync();
}
public sealed record ReplayDisplayCoordinateBinding(string CoordinateId,
    string CoordinateRevision, string PixelSpace, long ViewportCoordinateToken);
public sealed class ReplayDisplayPublisher : IReplayDisplayPublisher {
    public ReplayDisplayPublisher(ReplaySubjectBinding subject,
        IReplayEvidenceReader reader, Asun.Modules.ImageFrame.Resources.IFrameService frames,
        string publishConsumerId, ReplayCodecLimits limits, long maxSourceBytes,
        ImmutableArray<ReplayDisplayCoordinateBinding> coordinates);
}
```

Host将双ViewportControl放中央两个LayoutPanel，Workbench构造仍无图像初始化；选择CaseId后按已授权image role/Evidence的完整ContentRef交ShowAsync，不猜文件名或CandidateDigest就是图像。Bridge构造纯内存，AttachParticipant于ReplayRoot先于Bind；两个Controls同原工作台Dispatcher（两STA各有一组），核subject/ticket/FrameService的consumer登记/不同Control/同ViewportRoot，失败零Task。RetainedBytes含两个scope留存及原Task上界；正式端口从可信已认证组合根传入，不生产默认Allow。

**原Task/frame/发布Owner。** Publisher按§10.2replay-image-v1解码原bytes/域。UInt8 Gray、UInt16 Gray、明确R/G/B UInt8可无损通过image-frame.IFrameInputRows逐行PublishCopyAsync到独立CPU frame；Reader逐异步stream完整核hash后在MaxSourceBytes内预物化本方稳定tight CPU数组，CopyRow只同步复制已经在内存的行，不阻塞等待ReadAsync/权限请求或在回调中IO。该源数组与FrameService的复制storage同时峰值均计宿主/Replay预算，发布真实结束后才归还源数组；超过双份峰值预算拒0006，不假称只占一份。两个Control随后共享已发布frame，而非每Control另发布。RGB三plane按明确channel交错为一个Interleaved plane，不改原像素。首版Publisher不量化int2/int4/real，直接0013且差异表/原artifact引用保留；宿主其它已登记显示Adapter可给有父引用及显式DiagnosticOnly/LutRevision的新Gray8资产，再通过此Publisher发布，不能把副本当原量测或在本构造缺少LUT入口时隐藏转换。非有限/缺坐标/未知role0013，不擅自全图min/max。使用公开FrameServiceFactory/ManagedLayoutValidator/TimeProvider.System创建源service（或借宿主已有）；源consumer/profile预登记，Replay不去改共享服务配置。

每次publish的Guid/ServiceEpoch/FrameKey/原ContentRef/CaseId/侧别保存，原ValueTask一次AsTask经ReplayRoot预登记；成功Frame只在Receipt完成/Error=None/OperationResourcesReleased=true交付。晚到未交付的成功Frame仅Retire本方Key并查询原ID；复制中stream/row/source保活，观察到期不卸source。Publisher为Frame发布持有Owner；viewport source factory只Read/Return，不Retire。两binding全部Return/Context解引用后，Publisher才Retire原Key。已封存工程资产不删；CPU帧是可恢复的显示副本。MaxSources满先拒新Show，不能丢旧frame/entry或用新ID绕Unknown。

**每Control一次实际装配，所有字段明确：**

1. 原Dispatcher内new ViewportControl；预先创建并强持ViewportRootFactory().Create(ViewportRootOptions)。调用ViewportImageFrameSourceFactory.Create(ports.Frames,viewportRoot,new(已登记readConsumerId,MaxSources,metadataBytes))取Succeeded+Value，稳定Frames/Coordinates供两个Control引用；两个viewport独立lease可共享同Frame物理storage。两STA各自scope/renderer可共享宿主源服务的引用计数，不能各Close共享service。
2. ViewportRendererFactory.Create(control,viewportRoot,new(policy,nativeBaseline,rasterBytes,2,UiBudget))取**该Control**的Backend/Lifetime。显式离线/无共享生产池才OfflineRasterOnly+BudgetOnly；真实证据查看采用HalconRequired+Required且ports.Admission必填真实Owner，不将合成值当授权。Profile显式允许才HalconWithOfflineRasterFallback，不悄切仍称原后端。
3. 原root.CreateFactory().Create(new ViewportOptions(consumerId,ReadOnly,Navigation|Presentation,sourcePorts.Frames,sourcePorts.Coordinates,ports.Authorization,MaxDisplayBytes,MaxInFlightTiles,admissionMode,DrainTimeout:UiBudget,OperationTimeout:UiBudget,Presentation:control.Presentation,ResourceAdmission:ports.Admission,Limits:明确limits,BackendPolicy:policy,Backend:renderer.Backend))。ROI/Probe/Surface/IntentSink未请求时保持null；identity Coordinates只同原pixel space，不冒物理标定。
4. ViewportUiResourceCatalog.Get(culture)取完整成功Resources；同control.BindAsync(session,viewportRoot,new ViewportUiBindingOptions(bindingId,true,resources,UiBudget,Lifetime:renderer.Lifetime,ExecutionBudget:new(displayRetainedBytes,32,32)),ct)，保存原Bind Task及runtime binding。Presentation=同Control.Presentation，Lifetime=同renderer.Lifetime，两个BindingId独立固定，不另造Presenter/Root/authority。OwnSession=true，Unbind仅关闭自己显示Session，不Cancel另一观察者的Replay执行。
5. Publish成功后sourcePorts.Register(new ViewportPublishedFrameBinding(publicationId,Frame,Image,[0],PixelSpace))；完整ImageDescriptor映Frame真实Width/Height/ChannelCount/Bits/Signed/CenterInteger/CoordinateRevision/SourceRevision/Channels/原Validity、level0 identity、tile256×256、MaxDecodedTileBytes=checked(256*256*channelBytes)、DecodeRevision。此桥只使用source factory当前CPU单planeUInt8/UInt16 Gray/RGB8域保真能力，不冒多层/复杂layout支持。PixelSpace=Frame.CoordinateReference同原源资产，不猜r1或文件名；CoordinateRevision必须有显式源映射。
6. 首次Register后session.AttachAsync(new ViewportContext([new SourceBinding(Primary,Image,null,CaseId)],[],trustedAuth,culture,new ApiVersion(0,1),0,view))一次，view=ViewState.Fit2D(actualCanvasDip,dpiX,dpiY) with { Lut=明确LUT }。trustedAuth由正式AuthorizationPort/宿主提供当前Read/domain/expiry，不由Publisher签。Gray8手动LutWindow(0,255,"display-range/uint8/1")、Gray16(0,65535,"display-range/uint16/1")仅格式范围非测得统计；RGB走原色彩路线，自动LUT必须原Owner完整可信Statistics。
7. 后续Show预留两侧source槽/旧新并存预算→Publish→Register新revision→session.UpdateAsync(new ViewportUpdate(session.GetSnapshot().ContextRevision,replacementContext))全量替换。只能在合法授权/实际提交回执后采用；Partial/Unknown超时保原Task/Frame/Binding.GetPresentations中的OriginalCommit/Acquire/Confirm/Revoke/Return与leaseIdentity，不能从WPF赋值猜VisibleConfirmed。ViewportRoot持底层原task/lease，ReplayRoot持public Bind/Update/Unbind/Bridge和frame发布；两种账不互代。
8. 缺失一侧、换Case或撤权Clear：同session.Update Sources=[]/Layers=[]走viewport§4.7.1可信空分支，核EmptyTransition.ReferencesDetached/VisibleConfirmed，未确认“图像待清除”并封新非空交付。读撤权不阻该binding无源清理；不得Unbind/RequestCleanup当临时Clear、不得重新Attach，旧标题/层不保留。随后合法Show用同session/Frames/Binding继续Update。旧entry Remove只在旧Context解除且Read/Return真实归还；Remove成功才Publisher.Retire本方FrameKey。Return未知查原ReturnId/ServiceEpoch+RequestId，不换ID再读。
9. 同CoordinateId/Revision/单位及已登记实际映射一致时双图导航intent携SourceId/Revision/Generation/originSessionId/gestureId，转LinkNavigationCommand防环；不相符独立缩放/平移并显示“坐标不同，分别查看”，不自动配准/裁剪。默认Features无Probe/ROI编辑，原值看Difference表。3D/Region/XLD专业artifact显示只有已批准source端口适配可转同viewportSurface/Overlay明确binding，专业mesh/根支持与算法仍原Owner；该双图image-v1固定2D，不造Replay通用3D solver。
10. 语言通过同binding.SetResourcesAsync(Catalog.Get(...),UiBudget,ct)，两图完整资源快照一致、另一STA不变。Unbind封Show/联动/订阅→原binding.UnbindAsync(UiBudget,独立cleanupToken)并强持原Task→上游root/trace原ReturnId确认Detached+Drained→entry Remove→Publisher.Retire/Query→participant.Dispose成功后ReplayRoot释放hold。到期/晚到Frame/Presenter Return未完仍BackgroundOwned，强持两个root/frames/control/Dispatcher泵；不能以waitCancelled/Closed当Released，不在viewport Control slot里Dispose自身Session。原Root/Close算法沿v0.2复用不重审。
11. 大图source只每完整Original引用一份不可变frame storage，不每Control全幅复制；viewport仅按可见tile Read独立leases。首版source factory无Pyramid时level0，超过MaxSourceBytes/FrameBudget先0006并仍可看报告/做tile工程差，不悄降采样Exact。已有Pyramid由其注册Frames端口提供真实level/中心映射，UI沿viewport选层，本方不发明LOD/统计。budget含完整source发布、旧新并存、readback/renderer/tile真实backing；图像失败不删报告/改变分母。

**两个STA的完整合成显示Profile与输入。** 沿§11.4线程生命周期，但图像切片的ReplayRoot Options显式改为(2,256,2147483648,2s)，每原ticket预留retainedByteCeiling=1073741824，含Bridge预留源/复制/原Task与同scope元数据上界；这是新合成图像Profile，不改§11.4纯文本Profile及其Golden。两scope共享allocation不相加冒RSS，字节满在Publish/Bind前拒。各STA两个Control、一个原ViewportRoot：MaxSessions2/TrackedTasks256/PendingReturns128/RetainedBytes536870912/CleanupAttemptBudget2s/MaxCleanupAttempts2。source factory metadataBytes=262144；session limits=(Sources2,Layers8,GeometryPoints4096,Candidates16,Commands32,Events64,String4096,Levels8,PlanTiles128)。ReplayViewportOptions=(BindingPrefix=本ticket稳定SlotId,SourceBytes268435456,DisplayBytes67108864,RasterBytes67108864,Sources4,InFlightTiles4,UiBudget2s)；OfflineRasterOnly renderer nativeBaseline0/raster64MiB/Pending2，UI ExecutionBudget=(268435456,32,32)。源service ResourceLimits按image-frame§4.3：CPU512MiB/native=GPU=cache=0、Frames8、Active4/Queued4/Receipts128/Retention1min/Drain2s；publish consumer replay-display/publish、read consumer replay-display/viewport分别Held512MiB/Leases8/Active2/Queued2，FrameBudget=new BudgetLimit(536870912,268435456,65536,65536,"replay-display-test-deployment","1","replay-display-test","1")，来自本节合成软件Profile，不当生产限额。

**image-frame与viewport逐字段映射。** 仅使用image-frame.Core的BudgetLimit/ManagedFrameLayout/PlaneLayout/DomainDescriptor，Resources的FrameDescriptor/PlaneMetadata/IFrameService；两个namespace不可混用。Width/Height经checked转int且每row可表示Span，plane0的Scalar=UInt8或UInt16、ByteOrder=LittleEndian、Bits=8或16；Gray为ChannelCount1/Packing.SinglePlane/Role.Intensity，RGB8为ChannelCount3/Packing.Interleaved/Role.Auxiliary（metadata明确[R,G,B]，不把整个彩色plane宣称仅ColorR）。Offset=0，StrideBytes=RowBytes=checked(width*channelCount*sampleBytes)，AccessibleBytes=DeclaredBufferBytes=RowBytes*height，恰一个plane。RGB每channel原ValidRuns取精确交集；相同完整域可共享不可变值但段计费仍按上游输入/metadata/交集规则，不用共享对象逃限。空交集→DomainKind.Empty/Rows=[]，每行[0,width)完整→Full/Rows=[]，否则RowSegments/完整DomainRow；缺口绝不改包围框Full。PlaneMetadata(Unit="1",Scale=1,Bias=0,Channels=明确原通道,ValidDomain=实际域,InvalidReason=Full时""否则"replay.source.domain")；首版Gray/RGB非Unit="1"拒0013，不偷换物理单位。发布前预算包括原runs、转换域、metadata域及生成交集的峰值段数，超限先0006。

coordinates由可信组合根显式提供、<=Codec.MaxCollectionItems、(CoordinateId,CoordinateRevision)唯一，与原manifest逐值匹配，PixelSpace非空、ViewportCoordinateToken>0；同PixelSpace/token不得映不同原引用，未知不显示。合成映射恰("fixture-coordinate","1","fixture-pixel-1",1)，第二STA独立pixel space/token映射。不从r1/文件名/ulong解析token；真实物理坐标用原Owner的准确引用映射，identity仅本pixel space，不证明跨图标定。首次publication分配本地Guid/FrameKey(Guid,1)/PublishRequestId且永久关联原image ContentRef/原坐标binding；SourceId用本地稳定PublicationId，SourceRevision="1"为该新本地发布token，原AssetId/Revision/hash保存在publication映射，不以这个token替原事实。重复同Show操作复用已登记原Task/Key，不新Guid绕Unknown；换源为新publication/sourceId，旧新分开。Frame.SourceId/SourceRevision与Image.SourceId.Value/SourceRevision相等，Frame.CoordinateReference=PixelSpace，Image.CoordinateRevision=new CoordinateRevision(ViewportCoordinateToken)，DecodeRevision="replay-image-v1/cpu-display-v1"。Image.Validity=new ValidityDomain("replay-image-domain",SourceRevision,new PixelRect(0,0,width,height),实际域Full,Full时null否则完整原image.Digest)，此mask token关联Publisher强持的完整域快照；不是用hash凭空证域。level0整数中心identity AffineMap2D(1,0,0,1,0,0)、tile256，MaxDecodedTileBytes=checked(256*256*channels*sampleBytes)；所有cap/数字在源Register前验证。

源工厂Create不启动Read/native，但其实际scope对象、renderer/session/Bind原Task均登记本方Bridge与ViewportRoot；Bind某侧失败也要关闭已建的另一侧session/renderer、Remove已注册entry、Return并Retire本方frame，迟到成功不交付控件，原Dispatcher继续泵到真实释放。借宿主IFrameService只Retire本方Key，不Close；本组合根创建的服务仅两个STA/全部bindings真实Returned后由Host.CloseAsync/Dispose一次，并将原Task纳Root cleanup预算。Bind重复同实例幂等，跨Dispatcher/Control/Lifetime拒；Unbind不可用原已取消Show token。

首图16×16 Gray8第y行第x样本=(x+16*y)%256，原/候选完整Original asset各有独立ContentRef/hash/source revision，元数据Unit="1"、Scale1/Bias0、channel Gray、Full真实域、CoordinateId=fixture-coordinate/CoordinateRevision="1"，PixelSpace显式fixture-pixel-1、viewport token1。第二STA独立epoch/source IDs，使用16×16 UInt16 Gray，值=256*(x+16*y)，两个样本0/65280正确；A/B不同Reader与Publisher，两图完整输入预先用§10.2codec生成不可变图像asset，不在UI生成随机图。Fault/反例：A撤权清空不影响B；A旧Show/Read/Presenter/Return闩锁到期，旧图generation不得写新Case，原帧持有直到Returned；空Update后合法Show不重Bind/Attach；图像超budget、域空/错hash、signed首版不支持、SourceId/epoch混交/错Lifetime拒；最后lease/frame retire各一次，真实1920×1080UI运行另验。Production显式Required/Profile，不套离线权限。

UI视觉与可用性并列：§11.1比例/主题/icon/8或12DIP间距保持，差异Grid统一NavigationStyle.Cell+AllowEditing=false，案例导航Grid=Row；Check/Start/Cancel/Drain/Export关键命令常驻，高级三页渐进显示，状态有图标+短词而非仅红绿，取消可达。时间线有界虚拟Grid按Sequence/StateRevision，统计不复制；全报告筛选首版逐页流式评估受预算且标已扫描/总数，不依未定义外部索引也不声称仅当前页是全部。三语新增：图像待清除/影像待清除/Image clearing；导出结果待确认/匯出結果待確認/Export result pending confirmation；坐标不同，分别查看/座標不同，分別查看/Different coordinates. View separately.；图像超出显示预算/影像超出顯示預算/Image exceeds display budget.，均实例资源键。键盘/UIA/文化保选择与不改Core沿§11.3。

本轮已定向读取viewport签名，同Control Presentation/Lifetime、原Task/lease、资源catalog/有限Unbind接线确定；无须等总控内容审核。DevExpress细节沿本机25.2.3 XML，补读Grid.TableView.AllowPerPixelScrolling/GridControl.SelectionChanged；当前无dxdocs callable，不声称已执行真实UI。

## 12. 两个无 UI Host、公开 Factory 与进程 Root

### 12.1 完整公开构造与借用边界

v0.3已接收的主体/授权/CAS语义不变；本节补齐该契约的装配声明，不更改replay-contract-v3或旧hash。新增类型位于Core，不引用WPF；测试专用类型在Testing。所有构造均验证有限值，不读取证据、不登记操作、不起后台工作。Factory才完成scope验证，失败不调用Engine/Store写端口。

```csharp
public sealed record ReplayDependencies(IReplayEvidenceReader Reader,
    IReplayProgramResolver Resolver, IReplayExecutionEngine Engine,
    IReplayComparisonPolicy Comparison, IReplayResultStore Store,
    IReplayClock Clock, ReplayServiceOptions Options,
    IReplayResourceCoordinator Resources, ReplaySubjectBinding Subject,
    IReplayAuthorization Authority);
public static class ReplayServiceFactory {
    public static Task<IReplayService> CreateAsync(
        ReplayDependencies dependencies, CancellationToken ct);
}
public sealed class ReplaySystemClock : IReplayClock {
    public ReplaySystemClock(string bootId);
    public DateTimeOffset UtcNow { get; }
    public string BootId { get; }
    public long MonotonicNs { get; }
}
public sealed record ReplayResourceLimits(int MaxRuns, int MaxConcurrency,
    long MaxInputBytes, long MaxOutputBytes, long MaxNativeBytes,
    long MaxGpuBytes, int MaxQueuedCases);
public sealed class ReplayResourceCoordinator : IReplayResourceCoordinator {
    public ReplayResourceCoordinator(ReplayResourceLimits limits);
    public ValueTask<IReplayPermit> AcquireAsync(string requestId,
        ResourceBudget budget, CancellationToken ct);
}
public sealed class ReplayService : IReplayService {
    public ReplayService(IReplayEvidenceReader reader,
        IReplayProgramResolver resolver, IReplayExecutionEngine engine,
        IReplayComparisonPolicy comparison, IReplayResultStore store,
        IReplayClock clock, ReplayServiceOptions options,
        IReplayResourceCoordinator resources, ReplaySubjectBinding subject,
        IReplayAuthorization authority);
    // 各方法唯一声明见§4；此处只固定构造参数顺序。
}
```

这些是公开声明规格，分号构造不作为待编译源文件。Factory返回新ReplayService，逐端口核BoundSubject、选项、Clock/资源限及§4.0授权适配器非空；不隐式调用Preflight/Start。Factory异步方法须在首个await前只做有限内存工作，正常/异常/取消均返回Task，禁止同步阻塞外部端口。构造失败0001/0005，异常保留于Root内部诊断，外部文本使用稳定MessageKey。直接构造仍可用，但Host关闭恢复必须遵循同一Root。

ReplaySystemClock的BootId为宿主本次进程启动ID，Stopwatch计单调ns，UTC只显示；不在每Service重置boot。Coordinator为同进程共享实例，按整个ResourceBudget原子预留；不足立即0006，取消准备不留permit，归还幂等，旧运行未排空不腾容量。固定纯Core验证的native预算为1字节/GPU=0（Engine实际不申请native），不把正预算规则改为默认零。Options各字段范围见§4.1：IoTimeout、MaxEventBuffer、MaxEventBytes、MaxReadPageSize、MaxReadBytes必填；不允许无限/负值或静默clamp。Authority由宿主实现IReplayAuthorization并负责真实认证，Core没有AllowAll生产实现。

Dependencies全部为借用，Service不Dispose外部Reader/Resolver/Engine/Store/Comparison/Clock/Coordinator/Authority。组合根须为这组借用取得IReplayDependencyHold：强持每个实例及实际底层资源Owner；Hold仅在该Root槽全部原Task、回调、服务/Session关闭已确认后归还。Hold不能仅保存弱引用/名称，不能借用已关闭scope，不能因撤权销毁仍运行的Engine；共享底层引用计数在Owner归还，不由Core猜测。测试hold只拥有自己的字典/Store，生产hold封装宿主已有scope lease，不另建容器或native运行时。

### 12.2 Factory前预留、两轴有限清理与确认移交

Root是可信组合根的有界进程生命周期组件；Root存在于方法/Window之外，由进程入口强持到Shutdown确认。它负责本模块调用Task/句柄监督，不替代操作事实Store/授权Owner，不运行产品处置。进程入口退出前必须Query所有槽；未settled拒绝关闭共享运行时，显示“关闭未完成”，由原Root继续观察；异常返回/方法离栈不销毁Root。

```csharp
public enum ReplayRootStage { Factory, Start, Completion, Query, Read, Close, Drain, Dispose, Ui }
public enum ReplayRootState { Reserved, Active, Closing, BackgroundOwned, Settled }
public sealed record ReplayRootOptions(int MaxSlots, int MaxTasksPerSlot,
    long MaxRetainedBytes, TimeSpan CallObserveBudget);
public sealed record ReplayCleanupBudget(TimeSpan QueryObserveBudget,
    TimeSpan ReleaseObserveBudget);
public sealed record ReplayRootTicket(string RootId, string SlotId,
    ReplaySubjectBinding Subject, string RequestId);
public sealed record ReplayRootSnapshot(ReplayRootTicket Ticket, ReplayRootState State,
    int PendingTasks, bool BorrowedResourcesReturned, bool ResourcesReleased,
    bool BackgroundOwnerConfirmed, ImmutableArray<ReplayError> Errors);
public sealed record ReplayRootShutdownSnapshot(string RootId, ReplayRootState State,
    bool BorrowedResourcesReturned, ImmutableArray<ReplayRootSnapshot> Slots);
public sealed record ReplayCleanupReceipt(ReplayRootSnapshot Ownership,
    ReplayOperationLookupResult? Operation);
public interface IReplayDependencyHold : IAsyncDisposable {
    long RetainedBytes { get; }
    ReplayDependencies Dependencies { get; }
}
public sealed record ReplayRootAdmission(ReplayRootTicket? Ticket, ReplayError? Error);
public sealed partial class ReplayProcessRoot {
    public ReplayProcessRoot(string rootId, ReplayRootOptions options);
    public ReplayRootAdmission TryReserve(ReplaySubjectBinding subject,
        string requestId, long retainedByteCeiling);
    public void AttachHold(ReplayRootTicket ticket, IReplayDependencyHold hold);
    public Task<IReplayService> CreateAsync(ReplayRootTicket ticket, CancellationToken ct);
    public Task<ReplayStartResult> StartAsync(ReplayRootTicket ticket,
        ReplayRunRequest request, CancellationToken ct);
    public Task ObserveCompletionAsync(ReplayRootTicket ticket, CancellationToken ct);
    public Task<ReplayOperationLookupResult> QueryOperationAsync(
        ReplayRootTicket ticket, CancellationToken ct);
    public Task<ReplayCasePage> ReadCasesAsync(ReplayRootTicket ticket,
        ContentRef manifest, int offset, int pageSize, CancellationToken ct);
    public Task<ReplayCleanupReceipt> CloseAndObserveAsync(
        ReplayRootTicket ticket, ReplayCleanupBudget budget);
    public ReplayRootSnapshot QueryOwnership(ReplayRootTicket ticket);
    public ReplayRootSnapshot ConfirmBackgroundOwner(ReplayRootTicket ticket);
    public Task<ReplayCleanupReceipt> ResumeCleanupAsync(
        ReplayRootTicket ticket, ReplayCleanupBudget budget);
    public Task<ReplayRootShutdownSnapshot> ShutdownObserveAsync(TimeSpan observeBudget);
}
```

1. TryReserve是无IO有限锁内原子准入；必须先于创建资源hold/Factory。校验主体、RequestId/RootId和有限正retainedByteCeiling；MaxSlots>=1、MaxTasksPerSlot>=16、MaxRetainedBytes>=1，CallObserveBudget在[50ms,10min]。槽/字节不足返回0006+Ticket=null，此时Factory/Start调用数增量均0。关闭中的Root拒新准入。相同操作的多个观察槽允许，但每槽只Start一次；事实去重仍为Store(TenantId,RequestId)。
2. 预留槽立即归进程Root，Ticket只是操作权限受控的本地定位值，不能序列化给外部或凭Ticket升客户读取权。AttachHold是纯内存原子转移：检查hold字节不超预留、主体匹配且槽未装配，成功后Root成为唯一归还Owner；拒绝时保证未转移，调用方仍持hold。制造hold只能纯内存/已取得宿主lease，无异步未登记的scope初始化。Attach失败调用CloseAndObserve释放空槽；未转移hold仍由宿主scope Owner归还。测试路径字节预算提前算好，不故意制造Attach失败泄漏。
3. Root每入口先在槽中预登记一个有限Task位置与被借用闭包，再调用原Factory/Service的ValueTask.AsTask()一次，原Task及其结果强持。预登记不足先拒调用0006；普通调用最多占MaxTasksPerSlot-8，余8固定留给cleanup两轴/Dispose/hold，禁止业务页读占完后无法关闭。Factory/Start/Session.Completion/页Read/Close/Drain/Dispose均记录原Task，WaitAsync派生Task也观察fault；不能只保存等待代理或ct，不能再await同一ValueTask。完成的页在交付或迟到丢弃并观察异常后清内容引用，仅留有界阶段诊断，循环复用Task槽；MaxTasksPerSlot不是累计全生命调用数。Factory/Start结果提升为Service/Session强引用直至settled。同步调用抛错也落该槽记录。Factory/Start迟到成功后Root接管结果；若槽已Closing立即启动唯一安全关闭，不把晚到Session交已解绑UI。运行中的Start被观察取消，不重Start；恢复只有按原ID Query。
4. 外部ct只取消对应等待/准备，Created的stopToken按§4成为执行取消源；Completion观察ct不停止计算，Existing原运行不接新取消源。CallObserveBudget到期返回0010/TimeoutException观察诊断，原Task继续强持；业务状态不因此改Completed/Failed。Root封住新的Start/Read，保留原RequestId、BorrowedDependencies与Store访问能力。
5. CloseAndObserve是Root自身有限内存工作启动的cleanup任务，**不接受业务取消token**。两轴独立、同时启动：Q轴用新的有限QueryObserveBudget查原ID/当前授权，L轴用新的有限ReleaseObserveBudget观察关闭/Drain/Dispose。各预算在[50ms,10min]，从本次cleanup开始按真实Stopwatch绝对期限计算；不得每个步骤重置，也不得拿已取消stopToken/执行deadline当cleanup预算。每次等待仅用剩余时长；逾时挂原Task，返回对应轴Unknown/未释放，不顺序累加无界等待。Q轴Found/Unknown/0005均不代替L轴释放证明，L轴释放也不证明报告事务已知。Query授权撤销时Operation为Unknown/0005，Root所有权信息仅为脱敏本地生命周期。
6. L轴先封准入，Created Session一次RequestClose，Existing只关闭本观察；Factory/Start尚未返回时挂迟到续接。Session真实Drain ResourcesReleased且原Completion/Read/Query等调用结束后才Dispose Session/Service；Service Dispose可能长期占用Store IO，Root只有限观察原Task。所有原Task完成、Service/Session Dispose成功、显示回调退出、Hold.Dispose成功后才Settled、释放槽/hold计费。任一fault未证明释放则保留槽、Errors，不能以Task faulted=资源释放。Hold.Dispose原Task也强持，一次失败由Hold的幂等恢复协议继续，不能换一把不相关hold。
7. cleanup有限返回后调用ConfirmBackgroundOwner：这是**同一预留槽**的纯内存原子确认，不新分配、不再Retain；正常返回State=BackgroundOwned及BackgroundOwnerConfirmed=true，已Settled则返回Settled。不依赖Store/Authority响应。重复幂等；若确认调用自身失败，QueryOwnership必须显示原槽仍由同一进程Root持有，故本地离栈也不会丢Owner；同时拒后续准入并报0007。不存在“Retain失败→无限await本地Dispose”后备路径。Root不允许空槽早释放后靠事后登记挽救。
8. 后台不无界轮询、不并行重发同一Task：每槽每轴至多一个未完成端口调用，原Task完成后才决定下一步。采用单进程有界监督队列，间隔从250ms指数到5s，最大活动槽=MaxSlots；每轮重新开有限Q/L观察，所有权保持到确证。人工ResumeCleanup也是同槽同Task，没有再次Factory/Execute。主异常用原ExceptionDispatchInfo/Operation保存；cleanup异常另存Errors，不能在finally抛新异常覆盖原业务错误。Confirm/恢复事件不泄露客户内容。
9. Root QueryOwnership不声称报告授权，它只给调用方本槽的本地资源信息。QueryOperationAsync始终调用当前授权Service.Store；Factory仍未返回不能伪造NotFound，Root返回Unknown/0014并持原Factory。无法证明Factory曾开始前，仅空Reserved槽可确认释放；任何Start结果Unknown一律先查原ID，不以Unknown当未接纳重跑。
10. IReplaySessionRetention兼容实现只定位已经Root持有的原session并确认BackgroundOwner，抛错后也不移除预留槽；新Host只用Root接口。RunAsync便利方法底层按同一预登记Root/有限外层等待使用，长期未结束的原Task由Root持有，不要求调用栈无限停留。

关闭接纳停止Start/Read/UI，Q轴查询在Service.Dispose开始前仍可按当前授权执行；L轴先等待这些原Query/Read任务，故不会边Dispose边查同一Store。Service开始Dispose后禁止新的Q端口调用，Operation只保留本次已合法交付值/明确Unknown，不伪造当前授权快照。Settled清Service/Session/Task内容与hold强引用，仅保留有界Ticket生命周期tombstone；QueryOwnership仍可确认释放，旧槽不再读取客户结果。需要随后重新查报告时，以同可信主体、新Root观察槽/hold/Factory只Query**同一原RequestId**，不Start、不创建新操作；新scope授权也须重查。tombstone最多MaxSlots条，被淘汰返回0001/本地定位失效，不能猜释放；宿主保存已确认释放回执只作生命周期记录，不授报告读取权。

### 12.3 两个从空 Host 的独立组合根

以下构造公开类型在Asun.Modules.Replay.Testing，仅消费§4端口，不改变Core的生产行为：

```csharp
public enum ReplayFixtureHost { Regression, CustomerRepro }
public sealed record ReplayFixtureInput(ReplayRunRequest Request,
    ImmutableArray<ReplayFixtureAsset> Assets);
public sealed record ReplayFixtureAsset(ContentRef Reference, string CanonicalUtf8);
public sealed record ReplayFixtureScalar(string CaseId, ReplayValue Value);
public sealed record ReplayFixtureScalarManifest(string Schema,
    ImmutableArray<ReplayFixtureScalar> Values);
public static class ReplayFixtureCatalog {
    public static ReplayFixtureInput Create(ReplayFixtureHost host);
}
public sealed class ReplayFixtureClock : IReplayClock {
    public ReplayFixtureClock(DateTimeOffset utc, string bootId, long monotonicNs);
    public void Advance(TimeSpan elapsed);
    public DateTimeOffset UtcNow { get; }
    public string BootId { get; }
    public long MonotonicNs { get; }
}
public sealed class ReplayFixtureAuthority : IReplayAuthorization {
    public ReplayFixtureAuthority(ReplaySubjectBinding subject, string outputNamespace,
        ImmutableArray<string> requestIds, ImmutableArray<ContentRef> readableAssets,
        ImmutableArray<string> exportDestinations, string policyRevision);
    public void Revoke();
    public void Restore(string policyRevision);
    public ValueTask<ReplayAccessDecision> CheckAsync(ReplaySubjectBinding subject,
        ReplayAccessAction action, ReplayAccessResource resource, CancellationToken ct);
}
public sealed class ReplayDictionaryReader : IReplayEvidenceReader {
    public ReplayDictionaryReader(ReplaySubjectBinding subject,
        ReplayFixtureInput input, IReplayAuthorization authority);
}
public sealed class ReplayCustomerPackageReader : IReplayEvidenceReader {
    public ReplayCustomerPackageReader(ReplaySubjectBinding subject,
        ReplayFixtureInput input, IReplayAuthorization authority);
}
public sealed class ReplayFixtureResolver : IReplayProgramResolver {
    public ReplayFixtureResolver(ReplaySubjectBinding subject,
        IReplayEvidenceReader reader, IReplayAuthorization authority);
}
public sealed class ReplayCustomerResolver : IReplayProgramResolver {
    public ReplayCustomerResolver(ReplaySubjectBinding subject,
        IReplayEvidenceReader reader, IReplayAuthorization authority);
}
public sealed class ReplayScalarEngine : IReplayExecutionEngine {
    public ReplayScalarEngine(ReplaySubjectBinding subject, IReplayEvidenceReader reader,
        IReplayClock clock);
}
public sealed class ReplayFixtureComparison : IReplayComparisonPolicy {
    public ReplayFixtureComparison(ReplaySubjectBinding subject,
        IReplayEvidenceReader reader);
}
public sealed class ReplayMemoryStore : IReplayResultStore {
    public ReplayMemoryStore(ReplaySubjectBinding subject, string outputNamespace,
        IReplayClock clock, IReplayAuthorization authority, long maxStoredBytes);
}
public sealed class ReplayFixtureHold : IReplayDependencyHold {
    public ReplayFixtureHold(ReplayDependencies dependencies,
        ReplayFixtureInput input, long retainedBytes);
    public long RetainedBytes { get; }
    public ReplayDependencies Dependencies { get; }
    public ValueTask DisposeAsync();
}
```

省略实现方法不是省略契约：上述端口实现全部§4成员；FixtureCatalog必须按§12.4正文数据创建，不能读.work/隐含文件/latest。DictionaryReader按引用完整匹配查内存UTF-8字典；CustomerPackageReader使用独立只读逐页包映射/流，逐引用查长度/hash且将原父引用保留，不复用前者静态缓存。两Resolver分别从自己Reader解析Program Manifest/DAG，支持Changes并验证Before，返回候选图/精确依赖/环境；本固定ExactReplay Changes为空。ScalarEngine仅注册fixture.scalar.v1，解析每CaseId对应参数值并产出一个scalar/1/value，无其它输出/side effect；能力AdapterId=fixture.scalar、Revision=1、CooperativeCancel=true、IsolatedWorker=false、NativeUsageObservable=true、GpuUsageObservable=true、SupportedSchemas=[replay-test-scalars-v1,replay-test-environment-v1]；无native/GPU申请，任务闩锁由测试调度显式控制。Comparison读取自己Reader的Baseline和Policy，按§7纯托管比较，不根据Host名分支；MemoryStore实现完整Reserve/CAS/page/封存和scope ACL，容量>=报告/页总字节，输出引用归本操作，可授权ReadCases但不能用输入白名单阻自己报告。Authority固定主体/域/请求及输入asset完整集合，输出对象须Store的Owner/域证明；默认其它请求/租户/主体Denied，明确exportDestinations=[]时导出Denied，Revoke后全读取动作Denied但安全清理允许。两套只为软件合成验证，不算客户权限集成。

固定装配常量如下，所有values必填而非外部变量：Options=(IoTimeout=2s, MaxEventBuffer=64, MaxEventBytes=65536, MaxReadPageSize=1, MaxReadBytes=16384)；Coordinator Limits=(MaxRuns=2, MaxConcurrency=2, MaxInputBytes=131072, MaxOutputBytes=262144, MaxNativeBytes=2, MaxGpuBytes=0, MaxQueuedCases=2)；Root Options=(MaxSlots=2, MaxTasksPerSlot=32, MaxRetainedBytes=1048576, CallObserveBudget=2s)，每Host预留retainedByteCeiling=262144，hold.RetainedBytes=65536；Cleanup=(Q=2s,L=3s)。Clock=(2026-10-11T00:00:00.0000000Z, fixture-boot-1,0ns)，闩锁释放前Advance=0，仅软件时间控制，不用于性能。Regression subject=(tenant-fixture,algorithm-01,auth-reg-1)，Customer subject=(tenant-fixture,support-01,auth-cust-1)，policyRevision=fixture-policy-1。生产组合根用ReplaySystemClock与正式Authority/Reader，不能把测试Subject/政策复制去客户现场。

```csharp
// using System.Linq; 其余using见§3。两Host独立执行本函数，Root在进程入口创建并保持；没有隐含replay/ref/token。
async Task<ReplayOperationLookupResult> RunHostAsync(
    ReplayFixtureHost host, ReplayProcessRoot root,
    ReplayResourceCoordinator coordinator, CancellationToken stopToken)
{
    var input = ReplayFixtureCatalog.Create(host);
    bool regression = host == ReplayFixtureHost.Regression;
    var subject = regression
        ? new ReplaySubjectBinding("tenant-fixture", "algorithm-01", "auth-reg-1")
        : new ReplaySubjectBinding("tenant-fixture", "support-01", "auth-cust-1");
    var admission = root.TryReserve(subject, input.Request.RequestId, 262144);
    if (admission.Ticket is not { } ticket)
        throw new ReplayPortException(admission.Error!); // Factory增量0
    ReplayOperationLookupResult? operation = null;
    System.Runtime.ExceptionServices.ExceptionDispatchInfo? primary = null;
    bool cleanupOwnershipConfirmed = false;
    try {
        var authority = new ReplayFixtureAuthority(subject, input.Request.OutputNamespace,
            [input.Request.RequestId], input.Assets.Select(a => a.Reference).ToImmutableArray(),
            [], "fixture-policy-1");
        var clock = new ReplayFixtureClock(
            DateTimeOffset.Parse("2026-10-11T00:00:00.0000000Z",
                System.Globalization.CultureInfo.InvariantCulture), "fixture-boot-1", 0);
        IReplayEvidenceReader reader = regression
            ? new ReplayDictionaryReader(subject, input, authority)
            : new ReplayCustomerPackageReader(subject, input, authority);
        IReplayProgramResolver resolver = regression
            ? new ReplayFixtureResolver(subject, reader, authority)
            : new ReplayCustomerResolver(subject, reader, authority);
        var engine = new ReplayScalarEngine(subject, reader, clock);
        var comparison = new ReplayFixtureComparison(subject, reader);
        var store = new ReplayMemoryStore(subject, input.Request.OutputNamespace,
            clock, authority, 262144);
        var options = new ReplayServiceOptions(TimeSpan.FromSeconds(2), 64, 65536, 1, 16384);
        var dependencies = new ReplayDependencies(reader, resolver, engine, comparison,
            store, clock, options, coordinator, subject, authority);
        root.AttachHold(ticket, new ReplayFixtureHold(dependencies, input, 65536));
        await root.CreateAsync(ticket, stopToken);
        var started = await root.StartAsync(ticket, input.Request, stopToken);
        operation = started.Operation;
        if (started.Session is not null) {
            await root.ObserveCompletionAsync(ticket, stopToken); // 只撤等待
            operation = await root.QueryOperationAsync(ticket, stopToken);
        }
        if (operation.LookupState == ReplayLookupState.Found &&
            operation.Result is { } report) {
            var cases = ImmutableArray.CreateBuilder<ReplayCaseResult>(2);
            for (int offset = 0; ;) {
                var page = await root.ReadCasesAsync(ticket, report.CaseResults, offset, 1, stopToken);
                cases.AddRange(page.Items);
                if (page.IsLast) break;
                offset = page.NextOffset;
            }
            ReplayFixtureAssertions.AssertHost(host, input.Request, operation, cases.ToImmutable());
        } // Found无结果/Unknown/拒绝交原ID恢复，不称通过
    }
    catch (Exception error) {
        primary = System.Runtime.ExceptionServices.ExceptionDispatchInfo.Capture(error);
    }
    finally {
        // 独立Q/L预算，不传已取消业务token；任何失败仍有预留Root。
        try {
            await root.CloseAndObserveAsync(ticket,
                new ReplayCleanupBudget(TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(3)));
        }
        catch { /* 原cleanup task/错误已在Root；不得覆盖primary */ }
        try {
            var owned = root.ConfirmBackgroundOwner(ticket);
            cleanupOwnershipConfirmed = owned.BackgroundOwnerConfirmed ||
                owned.State == ReplayRootState.Settled;
        }
        catch {
            try { root.QueryOwnership(ticket); } catch { }
            // 原Root仍持预留槽；未拿到确认回执不称收尾成功，不覆盖primary。
        }
    }
    if (primary is not null) primary.Throw();
    if (!cleanupOwnershipConfirmed)
        throw new ReplayPortException(new ReplayError("REPLAY-0014",
            "Replay.CloseNotConfirmed", null, true, []));
    return operation!;
}
```

下面是进程入口对上述RunHostAsync的完整调用，参数全部在入口构造；独立两Host不是共享外部Service的两个名字。CancellationTokenSource是业务观察/停止源，Root清理预算独立；RunHostAsync正常返回Unknown/Found无Result时同样不判入口通过。

```csharp
async Task<int> RunIndependentHostEntryAsync(ReplayFixtureHost host,
    ReplayFixtureProcessOwner processOwner)
{
    var root = new ReplayProcessRoot(host == ReplayFixtureHost.Regression
            ? "replay-test-root-reg" : "replay-test-root-cust",
        new ReplayRootOptions(2, 32, 1048576, TimeSpan.FromSeconds(2)));
    processOwner.Register(root); // 纯内存有界登记，先于RunHost/Factory
    var coordinator = new ReplayResourceCoordinator(
        new ReplayResourceLimits(2, 2, 131072, 262144, 2, 0, 2));
    using var stop = new CancellationTokenSource(TimeSpan.FromSeconds(10));
    int exit = 0;
    try {
        var operation = await RunHostAsync(host, root, coordinator, stop.Token);
        if (operation.LookupState != ReplayLookupState.Found ||
            operation.Result is null) exit = 1;
    }
    catch { exit = 1; } // 详细主错误已由测试入口记录，不改成成功
    ReplayRootShutdownSnapshot shutdown;
    try { shutdown = await root.ShutdownObserveAsync(TimeSpan.FromSeconds(3)); }
    catch { return 2; } // Register早已强持Root；退出码待Main监督归还后才交进程
    if (shutdown.State != ReplayRootState.Settled ||
        !shutdown.BorrowedResourcesReturned) {
        exit = 2;
        // 原root交由下面入口级ProcessOwner强持；主函数不能此刻退出进程。
    }
    processOwner.Hold(root, shutdown);
    return exit; // 已在finally之外决定退出码
}

var processOwner = new ReplayFixtureProcessOwner(2);
var regressionExit = await RunIndependentHostEntryAsync(ReplayFixtureHost.Regression, processOwner);
var customerExit = await RunIndependentHostEntryAsync(ReplayFixtureHost.CustomerRepro, processOwner);
// 真实测试Main先按下文ProcessOwner协议确认所有槽，之后才返回合并退出码。
int finalExit = Math.Max(regressionExit, customerExit);
bool allReleased = await processOwner.ObserveShutdownAsync(TimeSpan.FromSeconds(3));
if (!allReleased) finalExit = 2; // 继续入口级监督，不立即Environment.Exit
```

ReplayFixtureProcessOwner为TestHost进程入口创建的**有界实例**：公开构造ReplayFixtureProcessOwner(int maxRoots)、void Register(ReplayProcessRoot root)、void Hold(ReplayProcessRoot root, ReplayRootShutdownSnapshot snapshot)、Task<bool> ObserveShutdownAsync(TimeSpan budget)。此参数是公开有界进程Owner，不是未定义业务依赖。Register纯内存强持最多两个不同RootId的Root，满则在Factory前拒绝；Hold仅核原RootId/Owner更新状态，无新分配。入口先Register后Factory，因此后面的关闭确认失败也不丢Root。无待关闭槽的Root仍由入口持有直到main最终清理；剩余根ObserveShutdownAsync(3s)有限返回false，测试Main记录退出码2并继续原入口监督循环，最后显式释放测试闩锁后所有Root Settled才能退出。生产不用测试ProcessOwner，进程组合根自己从入口强持Root；此测试实例不进入Core公共契约。

还须公开Testing类型ReplayFixtureAssertions，public static void AssertHost(ReplayFixtureHost host, ReplayRunRequest request, ReplayOperationLookupResult operation, ImmutableArray<ReplayCaseResult> cases)：按§12.4逐项断言，任一偏差throw稳定测试诊断并Exe非零。控制台Main创建一次Root("replay-test-root-1",固定Options)及一次Coordinator(固定Limits)，用CancellationTokenSource(10s)调用Regression，再用**新的Root/Coordinator**独立调用Customer；每个入口最后用ShutdownObserveAsync(3s)并检查Settled/资源归还，非settled退出码2且进程Root继续运行监督，不直接终止进程。再做同进程共享Root/Coordinator的双Host并发软件用例，不能把独立与共享测试混为一条。没有try内return退出码再靠finally修改的示例。以上代码是实现后调用形状，未编译/执行。

### 12.4 固定完整 Golden、引用与正常/反例恢复

下方JSON均为完整规范UTF-8文本，无BOM/换行；普通资产ContentRef为(AssetId=表名, Revision="1", Schema=正文schema, DigestAlgorithm="SHA-256", Digest=表hash, ByteLength=表bytes)。request/closure/result六行是domain+NUL+投影的编码向量，不作为Reader资产或ContentRef，不能将含domain的长度/hash拿去校验单独JSON。数组基线/候选schema固定replay-node-outputs-v2；catalog按此构造，不使用假hash/无内容引用。所有Int32/Int64/Ticks按§9.1字符串。环境asset同时固定Runtime.EnvironmentDigest；FromRoot、CutPoint=null、Changes=[]、Scope Targets/Fovs=[]及IncludeUnresolved=true，无隐藏目标关联。

FixtureCatalog输入Assets只包含本Host的param、两份baseline、policy、environment、runtime、graph、directory-page、directory、evidence、program共11个普通输入资产；两Host可共享不可变policy/environment/baseline-one字节，但不能共享主体scope、可变Store或授权缓存。candidate-one/candidate-two及results/case-results是期望输出编码向量，不预装进输入Reader、不伪造执行/封存结果；由Engine/Store运行生成后再逐字段/字节比较。完整request投影解码时由Catalog补正文给出的run/request ID，不能在ComputeRequestDigest中把它们重新加入。FixtureScalars的两CaseId唯一且ordinal排序，缺/多case键0004，值schema按§3.2；environment字段完整固定见下方，Catalog同时断言Runtime中modelRuntimeVersion=null、randomSeed=null、determinismLevel=BitwiseSameEnvironment，不允许其它Runtime借相同env名称运行。

完整bytes/hash表（普通资产为原UTF-8字节；request/closure/result为domain+NUL+投影字节）：

| 名称 | 字节数 | SHA-256 |
|---|---:|---|
| policy | 352 | `b37082abbfbaacfeeff606a8e13d55afbae740b1c0f44bd3eb599f82f19b796e` |
| param-r | 366 | `789870c0d67a93c46a5731d29db67d72d66809a644d3181648e141814bec8ba0` |
| baseline-two-c | 310 | `3700265331b6f6e9538441702a36dffaba68a01bc8b831c2ffcb1248d11bf99a` |
| baseline-one | 307 | `29fea2e9add57d35a65b79a0e113a67e08c870eca8ceb8590ce85d658bbd0bde` |
| param-c | 369 | `4771bafe2923b3c0cacceb0d76b800892634d36584b6ffa52493e8591e60c07a` |
| baseline-two-r | 305 | `80a1bf52e6cadf69cb94c6ccdd854105fb7329c643f1e3b9801282038ec526e6` |
| environment | 139 | `6f62f21022819430a15b479ab930b2b2b54bc3a0c40ebe04270a432ca6bbf495` |
| directory-page-r | 629 | `9ef7a4a4fe6ec2238918f608d184cb740aaad298ebe1d4f46175a34caf568aeb` |
| graph-r | 676 | `b942a6d248ab33c121efa36da6b83d26df84206a4f6bb9bae38045a7573297d9` |
| graph-c | 676 | `cf77140e09fec290d3c5cec6f8199b250db486d7b518754f86d79f64e6620845` |
| directory-page-c | 629 | `813a39732d455d2d745ba2b9979fb8d2d498d2a2981114f4ba9c64ae531b02db` |
| directory-r | 294 | `4043f22f45eb0b0b63be7c308ce5e3203b29090fb2b86631b1407a591751cbfe` |
| directory-c | 294 | `7bea860f995f734ba9051ab2ae8c3cf13eee36c8ed06c7a809bec7d1cdf5775c` |
| evidence-c | 299 | `86ca85a5ffdef5797feabc7618c43ddfafa971f6d1cf7ce194fe02cc9a9b8cfe` |
| program-c | 277 | `d3767e8ed4ea51b29f8dadb75811fbd6faa187454af02efe4bc18efa4c4973e6` |
| evidence-r | 299 | `47e75c16cb1c297f0fb2609366ffcb2123720068e03575a1fb5d097f498086c4` |
| program-r | 277 | `88c4ab3be7ef3a4e9a088935b6391178f692df35d6697c385ddec850dc1d10bb` |
| candidate-one | 307 | `92e3de29232e97e12bd5ecb1150570df9dc4a14ab99f24e7e1cfe561d5cca0f3` |
| candidate-two-r | 305 | `80a1bf52e6cadf69cb94c6ccdd854105fb7329c643f1e3b9801282038ec526e6` |
| candidate-two-c | 308 | `b78fffe45f3ff351b7f951cf8383e39f9125fad01240ce0c055e9d51909682d1` |
| results-r-0 | 941 | `16b1da489efcc3a7dd4d43fead44166d225f65aa5110b1c38913b33634912c92` |
| results-c-0 | 941 | `16b1da489efcc3a7dd4d43fead44166d225f65aa5110b1c38913b33634912c92` |
| results-r-1 | 937 | `cb20f232bbc611861f6751aed46f7fdc53045a87a6b05560a0c5d0a0f4f59fa6` |
| results-c-1 | 848 | `d5c94ace28d6118a383a38e2fd409932f07020c12adc966624af33b06dab4407` |
| closure-r | 2653 | `aa1ef78940e50098e798ace6227d411db291fa1dbedaaa8740263724edd9a49e` |
| closure-c | 2653 | `e0b6c7beddc948925bfe6e05bc6d547626bf711ce26caaf86610d79ae0d044cc` |
| request-r | 1402 | `365f8aeb2242e3408d76151ad16feeb80884dc9e88d033048d0f1325f12a630e` |
| case-results-r | 577 | `21d22498aa6601c1a80f907aae4c92ba16f95d1cb8d249df1f27022fdc8b49b7` |
| request-c | 1406 | `118769077598e2a5ada7de90111cafbd6d94102036d84abf3b1ce9bfe05dd4e5` |
| case-results-c | 577 | `1e4d873e191043d3237a6f6c195fa3ccc9e42453f5eb4cd3303f2291ca97301d` |
| result-r | 1057 | `e134375041865303c8e04141898d545dcf75a0b5a3232f0eae3678b3dbdf1ffe` |
| result-c | 1063 | `5ce27fd96e54bdcec2356ce1643b3242cebb840fb44451c4ae9dca49b22a3e8e` |
| runtime | 298 | `23c425f941908c41a066d56346cde6bcd22f574209d172225dcf7d02a516d1ce` |

**param-r**

```json
{"schema":"replay-test-scalars-v1","values":[{"caseId":"case-01","value":{"artifact":null,"canonicalValue":"101","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"}},{"caseId":"case-02","value":{"artifact":null,"canonicalValue":"0","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"}}]}
```

**param-c**

```json
{"schema":"replay-test-scalars-v1","values":[{"caseId":"case-01","value":{"artifact":null,"canonicalValue":"101","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"}},{"caseId":"case-02","value":{"artifact":null,"canonicalValue":null,"coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Missing"}}]}
```

**baseline-one**

```json
[{"artifacts":[],"errors":[],"fields":[{"fieldId":"value","value":{"artifact":null,"canonicalValue":"100","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"}}],"nodeId":"scalar","nodeRevision":"1","sideEffects":{"deviceCommandWrites":"0","productionFactWrites":"0"}}]
```

**baseline-two-r**

```json
[{"artifacts":[],"errors":[],"fields":[{"fieldId":"value","value":{"artifact":null,"canonicalValue":"0","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"}}],"nodeId":"scalar","nodeRevision":"1","sideEffects":{"deviceCommandWrites":"0","productionFactWrites":"0"}}]
```

**baseline-two-c**

```json
[{"artifacts":[],"errors":[],"fields":[{"fieldId":"value","value":{"artifact":null,"canonicalValue":null,"coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"NonFinite"}}],"nodeId":"scalar","nodeRevision":"1","sideEffects":{"deviceCommandWrites":"0","productionFactWrites":"0"}}]
```

**policy**

```json
{"rules":[{"absoluteTolerance":"1","anglePeriod":null,"coordinateId":null,"coordinateRevision":null,"fieldId":"[\"scalar\",\"1\",\"value\"]","kind":"Tolerance","missingPolicy":"ReportIncomparable","relativeTolerance":"0","requireValid":true,"ruleId":"scalar-abs-1","unit":"1","unitConversion":null,"valueKind":"Int64"}],"schema":"replay-comparison-v2"}
```

**environment**

```json
{"backend":"fixture.scalar","gpu":"None","native":"None","numericProfile":"Int64Exact","schema":"replay-test-environment-v1","version":"1"}
```

**graph-r**

```json
{"environmentDigest":"6f62f21022819430a15b479ab930b2b2b54bc3a0c40ebe04270a432ca6bbf495","nodes":[{"adapterNodeType":"fixture.scalar.v1","executionDependencies":[{"assetId":"environment","byteLength":"139","digest":"6f62f21022819430a15b479ab930b2b2b54bc3a0c40ebe04270a432ca6bbf495","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-test-environment-v1"}],"inputs":[],"nodeId":"scalar","nodeRevision":"1","outputFieldIds":["value"],"parameters":{"assetId":"param-r","byteLength":"366","digest":"789870c0d67a93c46a5731d29db67d72d66809a644d3181648e141814bec8ba0","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-test-scalars-v1"}}],"schema":"replay-graph-v2"}
```

**directory-page-r**

```json
{"items":[{"baseline":{"assetId":"baseline-one","byteLength":"307","digest":"29fea2e9add57d35a65b79a0e113a67e08c870eca8ceb8590ce85d658bbd0bde","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-node-outputs-v2"},"caseId":"case-01","fov":null,"inputs":[],"missing":[],"target":null},{"baseline":{"assetId":"baseline-two-r","byteLength":"305","digest":"80a1bf52e6cadf69cb94c6ccdd854105fb7329c643f1e3b9801282038ec526e6","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-node-outputs-v2"},"caseId":"case-02","fov":null,"inputs":[],"missing":[],"target":null}],"offset":"0","schema":"replay-case-directory-page-v2"}
```

**graph-c**

```json
{"environmentDigest":"6f62f21022819430a15b479ab930b2b2b54bc3a0c40ebe04270a432ca6bbf495","nodes":[{"adapterNodeType":"fixture.scalar.v1","executionDependencies":[{"assetId":"environment","byteLength":"139","digest":"6f62f21022819430a15b479ab930b2b2b54bc3a0c40ebe04270a432ca6bbf495","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-test-environment-v1"}],"inputs":[],"nodeId":"scalar","nodeRevision":"1","outputFieldIds":["value"],"parameters":{"assetId":"param-c","byteLength":"369","digest":"4771bafe2923b3c0cacceb0d76b800892634d36584b6ffa52493e8591e60c07a","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-test-scalars-v1"}}],"schema":"replay-graph-v2"}
```

**directory-page-c**

```json
{"items":[{"baseline":{"assetId":"baseline-one","byteLength":"307","digest":"29fea2e9add57d35a65b79a0e113a67e08c870eca8ceb8590ce85d658bbd0bde","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-node-outputs-v2"},"caseId":"case-01","fov":null,"inputs":[],"missing":[],"target":null},{"baseline":{"assetId":"baseline-two-c","byteLength":"310","digest":"3700265331b6f6e9538441702a36dffaba68a01bc8b831c2ffcb1248d11bf99a","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-node-outputs-v2"},"caseId":"case-02","fov":null,"inputs":[],"missing":[],"target":null}],"offset":"0","schema":"replay-case-directory-page-v2"}
```

**directory-r**

```json
{"count":"2","excludedUnresolved":"0","pages":[{"assetId":"directory-page-r","byteLength":"629","digest":"9ef7a4a4fe6ec2238918f608d184cb740aaad298ebe1d4f46175a34caf568aeb","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-directory-page-v2"}],"schema":"replay-case-directory-v2"}
```

**directory-c**

```json
{"count":"2","excludedUnresolved":"0","pages":[{"assetId":"directory-page-c","byteLength":"629","digest":"813a39732d455d2d745ba2b9979fb8d2d498d2a2981114f4ba9c64ae531b02db","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-directory-page-v2"}],"schema":"replay-case-directory-v2"}
```

**evidence-r**

```json
{"dependencies":[{"content":{"assetId":"directory-r","byteLength":"294","digest":"4043f22f45eb0b0b63be7c308ce5e3203b29090fb2b86631b1407a591751cbfe","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-directory-v2"},"required":true,"role":"case-directory"}],"schema":"replay-closure-v2"}
```

**program-r**

```json
{"dependencies":[{"content":{"assetId":"graph-r","byteLength":"676","digest":"b942a6d248ab33c121efa36da6b83d26df84206a4f6bb9bae38045a7573297d9","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-graph-v2"},"required":true,"role":"graph"}],"schema":"replay-closure-v2"}
```

**evidence-c**

```json
{"dependencies":[{"content":{"assetId":"directory-c","byteLength":"294","digest":"7bea860f995f734ba9051ab2ae8c3cf13eee36c8ed06c7a809bec7d1cdf5775c","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-directory-v2"},"required":true,"role":"case-directory"}],"schema":"replay-closure-v2"}
```

**program-c**

```json
{"dependencies":[{"content":{"assetId":"graph-c","byteLength":"676","digest":"cf77140e09fec290d3c5cec6f8199b250db486d7b518754f86d79f64e6620845","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-graph-v2"},"required":true,"role":"graph"}],"schema":"replay-closure-v2"}
```

**candidate-one**

```json
[{"artifacts":[],"errors":[],"fields":[{"fieldId":"value","value":{"artifact":null,"canonicalValue":"101","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"}}],"nodeId":"scalar","nodeRevision":"1","sideEffects":{"deviceCommandWrites":"0","productionFactWrites":"0"}}]
```

**candidate-two-r**

```json
[{"artifacts":[],"errors":[],"fields":[{"fieldId":"value","value":{"artifact":null,"canonicalValue":"0","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"}}],"nodeId":"scalar","nodeRevision":"1","sideEffects":{"deviceCommandWrites":"0","productionFactWrites":"0"}}]
```

**candidate-two-c**

```json
[{"artifacts":[],"errors":[],"fields":[{"fieldId":"value","value":{"artifact":null,"canonicalValue":null,"coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Missing"}}],"nodeId":"scalar","nodeRevision":"1","sideEffects":{"deviceCommandWrites":"0","productionFactWrites":"0"}}]
```

**results-r-0**

```json
{"items":[{"candidateDigest":"92e3de29232e97e12bd5ecb1150570df9dc4a14ab99f24e7e1cfe561d5cca0f3","caseId":"case-01","differences":[{"candidate":{"artifact":null,"canonicalValue":"101","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"},"caseId":"case-01","delta":{"artifact":null,"canonicalValue":"1","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"},"evidence":[],"fieldId":"[\"scalar\",\"1\",\"value\"]","kind":"Tolerance","original":{"artifact":null,"canonicalValue":"100","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"},"policyRuleId":"scalar-abs-1","tags":["Equal"]}],"elapsed":"0","errors":[],"originalDigest":"29fea2e9add57d35a65b79a0e113a67e08c870eca8ceb8590ce85d658bbd0bde","outcome":"CompletedEqual","targetIdentity":"[\"\",\"\",\"\",\"\",\"case-01\"]"}],"offset":"0","schema":"replay-case-result-page-v2"}
```

**results-r-1**

```json
{"items":[{"candidateDigest":"80a1bf52e6cadf69cb94c6ccdd854105fb7329c643f1e3b9801282038ec526e6","caseId":"case-02","differences":[{"candidate":{"artifact":null,"canonicalValue":"0","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"},"caseId":"case-02","delta":{"artifact":null,"canonicalValue":"0","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"},"evidence":[],"fieldId":"[\"scalar\",\"1\",\"value\"]","kind":"Tolerance","original":{"artifact":null,"canonicalValue":"0","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"},"policyRuleId":"scalar-abs-1","tags":["Equal"]}],"elapsed":"0","errors":[],"originalDigest":"80a1bf52e6cadf69cb94c6ccdd854105fb7329c643f1e3b9801282038ec526e6","outcome":"CompletedEqual","targetIdentity":"[\"\",\"\",\"\",\"\",\"case-02\"]"}],"offset":"1","schema":"replay-case-result-page-v2"}
```

**results-c-0**

```json
{"items":[{"candidateDigest":"92e3de29232e97e12bd5ecb1150570df9dc4a14ab99f24e7e1cfe561d5cca0f3","caseId":"case-01","differences":[{"candidate":{"artifact":null,"canonicalValue":"101","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"},"caseId":"case-01","delta":{"artifact":null,"canonicalValue":"1","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"},"evidence":[],"fieldId":"[\"scalar\",\"1\",\"value\"]","kind":"Tolerance","original":{"artifact":null,"canonicalValue":"100","coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Valid"},"policyRuleId":"scalar-abs-1","tags":["Equal"]}],"elapsed":"0","errors":[],"originalDigest":"29fea2e9add57d35a65b79a0e113a67e08c870eca8ceb8590ce85d658bbd0bde","outcome":"CompletedEqual","targetIdentity":"[\"\",\"\",\"\",\"\",\"case-01\"]"}],"offset":"0","schema":"replay-case-result-page-v2"}
```

**results-c-1**

```json
{"items":[{"candidateDigest":"b78fffe45f3ff351b7f951cf8383e39f9125fad01240ce0c055e9d51909682d1","caseId":"case-02","differences":[{"candidate":{"artifact":null,"canonicalValue":null,"coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"Missing"},"caseId":"case-02","delta":null,"evidence":[],"fieldId":"[\"scalar\",\"1\",\"value\"]","kind":"Tolerance","original":{"artifact":null,"canonicalValue":null,"coordinateId":null,"coordinateRevision":null,"kind":"Int64","unit":"1","validity":"NonFinite"},"policyRuleId":"scalar-abs-1","tags":["Invalid","MissingCandidate"]}],"elapsed":"0","errors":[],"originalDigest":"3700265331b6f6e9538441702a36dffaba68a01bc8b831c2ffcb1248d11bf99a","outcome":"CompletedIncomparable","targetIdentity":"[\"\",\"\",\"\",\"\",\"case-02\"]"}],"offset":"1","schema":"replay-case-result-page-v2"}
```

**case-results-r**

```json
{"count":"2","pages":[{"count":"1","firstCaseId":"case-01","offset":"0","page":{"assetId":"results-r-0","byteLength":"941","digest":"16b1da489efcc3a7dd4d43fead44166d225f65aa5110b1c38913b33634912c92","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-result-page-v2"}},{"count":"1","firstCaseId":"case-02","offset":"1","page":{"assetId":"results-r-1","byteLength":"937","digest":"cb20f232bbc611861f6751aed46f7fdc53045a87a6b05560a0c5d0a0f4f59fa6","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-result-page-v2"}}],"schema":"replay-case-results-v2"}
```

**closure-r**：前置域 `replay-closure-jcs-v2` + 0x00

```json
{"content":[{"content":{"assetId":"baseline-one","byteLength":"307","digest":"29fea2e9add57d35a65b79a0e113a67e08c870eca8ceb8590ce85d658bbd0bde","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-node-outputs-v2"},"role":"baseline:case-01"},{"content":{"assetId":"baseline-two-r","byteLength":"305","digest":"80a1bf52e6cadf69cb94c6ccdd854105fb7329c643f1e3b9801282038ec526e6","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-node-outputs-v2"},"role":"baseline:case-02"},{"content":{"assetId":"policy","byteLength":"352","digest":"b37082abbfbaacfeeff606a8e13d55afbae740b1c0f44bd3eb599f82f19b796e","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-comparison-v2"},"role":"comparison-policy"},{"content":{"assetId":"directory-r","byteLength":"294","digest":"4043f22f45eb0b0b63be7c308ce5e3203b29090fb2b86631b1407a591751cbfe","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-directory-v2"},"role":"evidence-directory"},{"content":{"assetId":"evidence-r","byteLength":"299","digest":"47e75c16cb1c297f0fb2609366ffcb2123720068e03575a1fb5d097f498086c4","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-closure-v2"},"role":"evidence-manifest"},{"content":{"assetId":"directory-page-r","byteLength":"629","digest":"9ef7a4a4fe6ec2238918f608d184cb740aaad298ebe1d4f46175a34caf568aeb","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-directory-page-v2"},"role":"evidence-page"},{"content":{"assetId":"graph-r","byteLength":"676","digest":"b942a6d248ab33c121efa36da6b83d26df84206a4f6bb9bae38045a7573297d9","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-graph-v2"},"role":"program-graph"},{"content":{"assetId":"program-r","byteLength":"277","digest":"88c4ab3be7ef3a4e9a088935b6391178f692df35d6697c385ddec850dc1d10bb","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-closure-v2"},"role":"program-manifest"},{"content":{"assetId":"param-r","byteLength":"366","digest":"789870c0d67a93c46a5731d29db67d72d66809a644d3181648e141814bec8ba0","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-test-scalars-v1"},"role":"program-parameters"},{"content":{"assetId":"environment","byteLength":"139","digest":"6f62f21022819430a15b479ab930b2b2b54bc3a0c40ebe04270a432ca6bbf495","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-test-environment-v1"},"role":"runtime-environment"},{"content":{"assetId":"runtime","byteLength":"298","digest":"23c425f941908c41a066d56346cde6bcd22f574209d172225dcf7d02a516d1ce","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-runtime-v3"},"role":"runtime-profile"}],"kind":"closure","schema":"replay-jcs-v2"}
```

**request-r**：前置域 `replay-request-jcs-v2` + 0x00

```json
{"content":{"budget":{"deadline":"100000000","maxCases":"2","maxConcurrency":"1","maxGpuBytes":"0","maxInputBytes":"65536","maxNativeBytes":"1","maxOutputBytes":"131072","maxQueuedCases":"1"},"changes":[],"comparisonPolicy":{"manifest":{"assetId":"policy","byteLength":"352","digest":"b37082abbfbaacfeeff606a8e13d55afbae740b1c0f44bd3eb599f82f19b796e","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-comparison-v2"}},"contractRevision":"replay-contract-v3","cutPoint":null,"evidence":{"manifest":{"assetId":"evidence-r","byteLength":"299","digest":"47e75c16cb1c297f0fb2609366ffcb2123720068e03575a1fb5d097f498086c4","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-closure-v2"}},"outputNamespace":"engineering/replay/regression","program":{"manifest":{"assetId":"program-r","byteLength":"277","digest":"88c4ab3be7ef3a4e9a088935b6391178f692df35d6697c385ddec850dc1d10bb","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-closure-v2"}},"purpose":"ExactReplay","runtime":{"backendId":"fixture.scalar","backendVersion":"1","determinismLevel":"BitwiseSameEnvironment","environmentDigest":"6f62f21022819430a15b479ab930b2b2b54bc3a0c40ebe04270a432ca6bbf495","modelRuntimeVersion":null,"numericProfile":"Int64Exact","randomSeed":null},"scope":{"fovs":[],"includeUnresolved":true,"targets":[]},"startMode":"FromRoot"},"kind":"request","schema":"replay-jcs-v2"}
```

**case-results-c**

```json
{"count":"2","pages":[{"count":"1","firstCaseId":"case-01","offset":"0","page":{"assetId":"results-c-0","byteLength":"941","digest":"16b1da489efcc3a7dd4d43fead44166d225f65aa5110b1c38913b33634912c92","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-result-page-v2"}},{"count":"1","firstCaseId":"case-02","offset":"1","page":{"assetId":"results-c-1","byteLength":"848","digest":"d5c94ace28d6118a383a38e2fd409932f07020c12adc966624af33b06dab4407","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-result-page-v2"}}],"schema":"replay-case-results-v2"}
```

**closure-c**：前置域 `replay-closure-jcs-v2` + 0x00

```json
{"content":[{"content":{"assetId":"baseline-one","byteLength":"307","digest":"29fea2e9add57d35a65b79a0e113a67e08c870eca8ceb8590ce85d658bbd0bde","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-node-outputs-v2"},"role":"baseline:case-01"},{"content":{"assetId":"baseline-two-c","byteLength":"310","digest":"3700265331b6f6e9538441702a36dffaba68a01bc8b831c2ffcb1248d11bf99a","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-node-outputs-v2"},"role":"baseline:case-02"},{"content":{"assetId":"policy","byteLength":"352","digest":"b37082abbfbaacfeeff606a8e13d55afbae740b1c0f44bd3eb599f82f19b796e","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-comparison-v2"},"role":"comparison-policy"},{"content":{"assetId":"directory-c","byteLength":"294","digest":"7bea860f995f734ba9051ab2ae8c3cf13eee36c8ed06c7a809bec7d1cdf5775c","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-directory-v2"},"role":"evidence-directory"},{"content":{"assetId":"evidence-c","byteLength":"299","digest":"86ca85a5ffdef5797feabc7618c43ddfafa971f6d1cf7ce194fe02cc9a9b8cfe","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-closure-v2"},"role":"evidence-manifest"},{"content":{"assetId":"directory-page-c","byteLength":"629","digest":"813a39732d455d2d745ba2b9979fb8d2d498d2a2981114f4ba9c64ae531b02db","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-directory-page-v2"},"role":"evidence-page"},{"content":{"assetId":"graph-c","byteLength":"676","digest":"cf77140e09fec290d3c5cec6f8199b250db486d7b518754f86d79f64e6620845","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-graph-v2"},"role":"program-graph"},{"content":{"assetId":"program-c","byteLength":"277","digest":"d3767e8ed4ea51b29f8dadb75811fbd6faa187454af02efe4bc18efa4c4973e6","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-closure-v2"},"role":"program-manifest"},{"content":{"assetId":"param-c","byteLength":"369","digest":"4771bafe2923b3c0cacceb0d76b800892634d36584b6ffa52493e8591e60c07a","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-test-scalars-v1"},"role":"program-parameters"},{"content":{"assetId":"environment","byteLength":"139","digest":"6f62f21022819430a15b479ab930b2b2b54bc3a0c40ebe04270a432ca6bbf495","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-test-environment-v1"},"role":"runtime-environment"},{"content":{"assetId":"runtime","byteLength":"298","digest":"23c425f941908c41a066d56346cde6bcd22f574209d172225dcf7d02a516d1ce","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-runtime-v3"},"role":"runtime-profile"}],"kind":"closure","schema":"replay-jcs-v2"}
```

**request-c**：前置域 `replay-request-jcs-v2` + 0x00

```json
{"content":{"budget":{"deadline":"100000000","maxCases":"2","maxConcurrency":"1","maxGpuBytes":"0","maxInputBytes":"65536","maxNativeBytes":"1","maxOutputBytes":"131072","maxQueuedCases":"1"},"changes":[],"comparisonPolicy":{"manifest":{"assetId":"policy","byteLength":"352","digest":"b37082abbfbaacfeeff606a8e13d55afbae740b1c0f44bd3eb599f82f19b796e","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-comparison-v2"}},"contractRevision":"replay-contract-v3","cutPoint":null,"evidence":{"manifest":{"assetId":"evidence-c","byteLength":"299","digest":"86ca85a5ffdef5797feabc7618c43ddfafa971f6d1cf7ce194fe02cc9a9b8cfe","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-closure-v2"}},"outputNamespace":"engineering/replay/customer-repro","program":{"manifest":{"assetId":"program-c","byteLength":"277","digest":"d3767e8ed4ea51b29f8dadb75811fbd6faa187454af02efe4bc18efa4c4973e6","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-closure-v2"}},"purpose":"ExactReplay","runtime":{"backendId":"fixture.scalar","backendVersion":"1","determinismLevel":"BitwiseSameEnvironment","environmentDigest":"6f62f21022819430a15b479ab930b2b2b54bc3a0c40ebe04270a432ca6bbf495","modelRuntimeVersion":null,"numericProfile":"Int64Exact","randomSeed":null},"scope":{"fovs":[],"includeUnresolved":true,"targets":[]},"startMode":"FromRoot"},"kind":"request","schema":"replay-jcs-v2"}
```

**result-r**：前置域 `replay-result-jcs-v2` + 0x00

```json
{"content":{"caseResults":{"assetId":"case-results-r","byteLength":"577","digest":"21d22498aa6601c1a80f907aae4c92ba16f95d1cb8d249df1f27022fdc8b49b7","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-results-v2"},"errors":[],"finalState":"Completed","frozenClosureDigest":"aa1ef78940e50098e798ace6227d411db291fa1dbedaaa8740263724edd9a49e","namespace":"engineering/replay/regression","productionFactWrites":"0","replayRunId":"run-reg-001","requestId":"req-reg-001","resourceUsage":{"cancelToDrainedNs":null,"copiedBytes":"0","drainedToReleasedNs":"0","peakConcurrency":"1","peakGpuBytes":"0","peakInputBytes":"0","peakManagedBytes":null,"peakNativeBytes":"0","peakOutputBytes":"0","peakQueueBytes":"0","peakQueuedCases":"0","phases":[{"elapsedNs":"0","phase":"Managed.NotObserved"},{"elapsedNs":"0","phase":"FixtureCounters"}]},"summary":{"cancelledOrNotRun":"0","completedChanged":"0","completedEqual":"2","completedIncomparable":"0","denominator":"2","failed":"0","unknown":"0"}},"kind":"result","schema":"replay-jcs-v2"}
```

**result-c**：前置域 `replay-result-jcs-v2` + 0x00

```json
{"content":{"caseResults":{"assetId":"case-results-c","byteLength":"577","digest":"1e4d873e191043d3237a6f6c195fa3ccc9e42453f5eb4cd3303f2291ca97301d","digestAlgorithm":"SHA-256","revision":"1","schema":"replay-case-results-v2"},"errors":[],"finalState":"Completed","frozenClosureDigest":"e0b6c7beddc948925bfe6e05bc6d547626bf711ce26caaf86610d79ae0d044cc","namespace":"engineering/replay/customer-repro","productionFactWrites":"0","replayRunId":"run-cust-001","requestId":"req-cust-001","resourceUsage":{"cancelToDrainedNs":null,"copiedBytes":"0","drainedToReleasedNs":"0","peakConcurrency":"1","peakGpuBytes":"0","peakInputBytes":"0","peakManagedBytes":null,"peakNativeBytes":"0","peakOutputBytes":"0","peakQueueBytes":"0","peakQueuedCases":"0","phases":[{"elapsedNs":"0","phase":"Managed.NotObserved"},{"elapsedNs":"0","phase":"FixtureCounters"}]},"summary":{"cancelledOrNotRun":"0","completedChanged":"0","completedEqual":"1","completedIncomparable":"1","denominator":"2","failed":"0","unknown":"0"}},"kind":"result","schema":"replay-jcs-v2"}
```

**runtime**

```json
{"profile":{"backendId":"fixture.scalar","backendVersion":"1","determinismLevel":"BitwiseSameEnvironment","environmentDigest":"6f62f21022819430a15b479ab930b2b2b54bc3a0c40ebe04270a432ca6bbf495","modelRuntimeVersion":null,"numericProfile":"Int64Exact","randomSeed":null},"schema":"replay-runtime-v3"}
```



Request投影排除运行ID，实际Regression=(run-reg-001,req-reg-001)，Customer=(run-cust-001,req-cust-001)。以上request的完整投影由固定Request字段生成；case-results两页各1案例，分页偏移0→1→2，最后IsLast=true；未关联TargetIdentity本版冻结为["","","","","CaseId"]（Product/Side/Target/Fov均空），不是臆造目标。closure角色集合为baseline:case-01、baseline:case-02、comparison-policy、evidence-directory、evidence-manifest、evidence-page、program-graph、program-manifest、program-parameters、runtime-environment、runtime-profile，排序按§9.1；各引用完整公开，Runtime环境证据包含在图ExecutionDependencies，不混运行时间。

Existing/Found/Unknown恢复用例显式共享**原MemoryStore实例/操作Owner**与同主体scope（分别新Root槽借用hold），不能各new空Store后假称查原ID。原Store在观察者关闭时由运行Root/测试组合根继续持有；创建者hold与观察hold共享底层scope引用计数，两个Store facade可共享同一已登记后端但不复制事实。Query响应/封存回执丢失由Testing闩锁仅阻返回、不删除已提交记录；原Task晚到后同ID查询必须回原digest/revision。撤权恢复仅FixtureAuthority.Restore("fixture-policy-2")显式恢复同Subject/Session的软件授权状态，生产恢复由可信宿主认证，不能按钮调用测试Restore；跨主体依旧Denied。cleanup结束后如需要新Query scope，先预留新Root再借同Store/正式scope，Factory只装配并Query，不Start。

Report完整编码Golden中的资源数值是**编码测试输入**：Managed.NotObserved=null说明托管峰值未测，FixtureCounters阶段明确其它固定零值来源于编码替身，不称实际加载/计费为零。ComputeResultDigest要逐字节匹配Golden；真实Host运行Report只断言正确六类计数、case页/字段/身份、ProductionFactWrites=0、设备命令0、不可观察字段null带原因、实际计费在预算内、lease/permit恰好归还一次、Revision与封存同快照，真实时间/资源改变须算它自己的新ResultDigest，不强迫与编码替身一致。ResultPage.Elapsed=0仅适用于固定FixtureClock不推进；真实Clock另测。报告资源golden不充当benchmark。

| 原ID恢复分支 | 正常输入与断言 | 反例与禁止行为 |
|---|---|---|
| Created | Start一次，OwnsExecution=true；Completion信号后授权Query Found、同RequestDigest/Revision>=1；两页完整Golden分类 | Start等待到期但原Task未结束：Root持原Task，Query同ID先Unknown后Running/Found；不二次Start/Execute，不释放原permit |
| Existing观察 | 第二槽同tenant/subject/request同内容，OwnsExecution=false；Query原ID等同原快照，取消本观察不改原执行 | 原Engine/Program现撤销仍Query已有结果；不Preflight挡读取、不把观察ct接原取消源 |
| Found无Session | 封存Store按原ID查到同结果；Start返回Session=null，直接逐页消费 | Found无Result仍运行时只返回快照/按原IDQuery；不造空报告/完成，不重新Execute |
| Unknown | Store返回0014或回执丢失：查询原RequestId；恢复后Found同摘要/Revision，不复算 | Query持续未知、原Factory/Start迟到：两轴预算到期BackgroundOwned，Root/借用资源仍在；不知道不等不存在 |
| 撤权 | Revoke后Query原ID为Unknown/0005、敏感字段全null，清旧UI；授权恢复同可信主体才能再Query | Completion已完成、已知报告引用也不可读页/导出；Cleanup安全关闭/Drain继续，禁止缓存Allowed；其它主体不查到Owner/存在性 |
| cleanup与槽满 | Root占两槽，第三TryReserve0006且Factory/Start计数不增；旧Task迟到后同槽Resume/QueryOwnership Settled | Close/Dispose闩锁永久不放、Retain故障：前台<=独立预算返回，Confirm原Owner；不无限阻本地栈、不把L到期当执行结束；测试最后显式放闩锁证明迟到归还 |

## 13. 正常、边界和失败案例

| 案例 | 输入 | 预期 |
|---|---|---|
| 历史解释 | 原结果可读、算法不可用 | `Completed`；报告保存时内容；不执行算法 |
| 精确重放 | 原程序/模型/标定/输入闭包完整 | 按冻结策略比较；原事实 hash/版本不变 |
| 变更试验 | 仅阈值改动，父请求完整 | 新 `ReplayRunId`；差异标明变更路径；生产写入为 0 |
| 缺 FOV | FOV1 存在、FOV2 缺失 | FOV2 `Incomparable/NotRun`；禁止复制 FOV1 |
| 双无效 | 原/候选均 Invalid | 记录无效状态一致；不计准确量测一致 |
| 单位不匹配 | 像素 vs 毫米且无标定 | `REPLAY-0008`；不可比较，不自动单位阵 |
| 身份冲突 | 重复目标 ID 或多对一 | 预检拒绝或目标级歧义；不得最后覆盖 |
| 取消 | 一个节点运行中请求取消 | 停止接收、排空、保留已完成案例；未排空不能 Completed |
| 期限 | Deadline 到达且 native 未返回 | `Draining` + `REPLAY-0010`；资源仍由原 Owner 持有 |
| 断电恢复 | 检查点缺输出 hash | 丢弃不完整点，从合法切点新尝试；不复用半写文件 |
| 重复请求 | 相同 `RequestId`、载荷相同 | 返回原工程回执；不同载荷拒绝冲突 |
| 后端缺失 | 原模型撤销、候选后端可用 | 只能作为新变更试验；不能称原版本重放 |

## 14. 测试矩阵与验收断言

测试必须分为模块单测、适配器契约测试、两个真实消费者集成测试和隔离/恢复测试。Mock 只能验证协议，不冒充 HALCON、WPF、工业样本或现场节拍。

| 类别 | 最小覆盖 | 通过断言 |
|---|---|---|
| 契约/校验 | 空 ID、范围、单位、有限数、预算、版本、命名空间 | 预检拒绝精确原因；不分配大对象 |
| 身份/有效性 | 缺失、新增、重复、歧义、Invalid/NaN/零 | 外连接保留全部差异；不按索引配对 |
| 容差/溢出 | 零基线、有向边界、整数 >2^53、Inf/NaN | 公式方向正确；溢出返回不可比较 |
| 图像/几何 | shape/通道/域/单位/坐标/覆盖变化 | 主比较不被对齐诊断掩盖；有效域差异可见 |
| 生命周期 | 正常、案例失败、取消、期限、迟到事件 | 终态和事件序列符合定义；迟到不推进新代 |
| 资源 | 共享读、租约、GPU/native、异常退出 | 归还一次；排空前不返池/Dispose |
| 幂等/恢复 | 重复请求、回执丢失、半写、断电 | 同载荷返回原回执；半写不成为恢复点 |
| 输入来源链 | Synthetic/RealCapture/Unknown、FaultInjected/ReplayDerived、重复父输入和生成闭包缺项 | 保留父来源和固定分母；按来源分层；像素一致不改来源或授予资格；生成语义改变必变 hash |
| ScenarioManifest | 语义字段、递归包引用、默认值/数组顺序、hash 篡改 | 同规范schema投影重复生成同hash；语义/引用/fault/断言变化产生新hash，JCS等价数字不误判变化 |
| 时钟/调度 | UTC 跳变、boot 变化、monotonic 溢出、同刻度事件、schedule seed | UTC 不改变 deadline 顺序；boot 失效旧 lease；tie-break 和失败 schedule 可重验 |
| fault/crash registry | 未注册类型、精确 fault、每个封存/回执崩溃点 | 未知 fault 预检拒绝；命中证据可定位；恢复不重复封存结果 |
| 共同合同测试 | ProductionAdapter + ReplayDeterministicSimulator 同一向量 | 状态、错误、幂等、取消、排空和资源断言一致；模拟器额外 fault 不泄漏 |
| 隔离 | 生产写端口、设备命令、latest 替换、路径穿越 | 组合根无法注入或调用；生产事实写入计数为 0 |
| 适配器 | HALCON 26.05/AsunImage 公共桥能力声明 | Core无供应商类型；只在具体适配器重载/封送歧义时编译；能力/域缺失显式错误 |
| 双消费者 | 算法回归 + 客户问题复现 | 同一核心、不同适配器均完成相同状态/错误/资源断言 |

### 14.1 Core Exe 必须执行的可判定向量

均为合成软件合同向量，无物理真值/现场资格含义。每向量独立重建Store/闩锁/时钟，并在finally释放替身闩锁，输出CaseId及断言失败定位；全部绑定§16 Exe，不另建测试框架。

| ID | 具体输入/注入 | 断言 |
|---|---|---|
| R-C01 | 空目录；重复CaseId；Exact非空Changes；Before不等原参数 | 分别0004/0004/0001/0004；EngineStartCount=0，准备lease归还一次 |
| R-C02 | baseline b=100，a=101；A=1/R=0；a=101.0001；b=0,a=0.1,A=0/R=0.1 | 前者Equal，第二Changed，零基线Changed；A/R非有限预检0001 |
| R-C03 | Int64 9007199254740993 vs 9007199254740992；两侧Invalid；有效0与Missing | 整数Changed；双无效StateEqual/Incomparable；0不等Missing，未填零 |
| R-C04 | 目录C1/C2/C3，乱序返回；C2缺FOV，C3候选新增字段；多对一身份冲突 | 冻结分母3，完整结果各一次，缺FOV不复制C1；新增字段不扩分母，歧义不最近坐标匹配 |
| R-C05 | 相同RequestId两个同时Start，闩锁在Reserve；第三个同ID改Budget | 仅一Created/EngineStart，第二Existing；第三0016；原run/report/hash不变 |
| R-C06 | C1完成，C2Engine闩锁未释放，C3未开始；Cancel与Deadline分别触发 | IntakeStopped；Completion未完成、Draining，租约未返池；放闩锁后归还一次，分别Cancelled/Failed+0010，六和=3 |
| R-C07 | 已知C2失败；取消和SealResult提交并发，两个明确schedule | 案例C2=Failed但完整报告可Completed；取消先线性化则Cancelled，提交先则Completed且迟到Cancel不改报告 |
| R-C08 | observer WaitAsync token取消，随后Engine完成；关闭页面/慢回调/回调异常 | 观察取消不停止Engine；原RequestId可查；事件订阅撤销不阻排空、不重复执行 |
| R-C09 | Store封存成功后丢回执；Query暂不可达；半写案例/Checkpoint | Unknown不当NotFound/Failed，查询原ID回同report；半写不恢复，Append只查/幂等，不再Execute |
| R-C10 | 旧generation NodeCompleted在新案例启动后迟到；事件重复/游标失效 | 不改新结果/分母/lease；序号去重；0017后查快照，不凭空补事件 |
| R-C11 | MaxCases=2但目录3；MaxQueuedCases=1，permit不足；压缩头低报实际展开 | 分配前0006或立即拒绝；实际输入字节有硬计费，超限后无静默截断/无界queue，释放计数守恒 |
| R-C12 | §9.1 RFC/JCS向量、两个domain同content、显式null/缺字段、递归包改hash | 数字规范结果符合官方向量；domain不同摘要不同；缺字段/重复键拒绝；无自指，旧hash不重算 |
| R-C13 | 同时刻两source事件反序输入、Declared schedule、Explore固定Seed；UTC跳变/BootChange | tie-break稳定，ActualSchedule可Declared复验；UTC不延长期限，旧Boot lease失效；超MaxSteps失败 |
| R-C14 | 每fault/封存crash停点、未注册kind、预期fault未命中 | 0015执行前拒绝；命中/未命中可见，required未命中失败；ProcessKill在Core向量以消息模拟，不杀自己 |
| R-C15 | v2合法包、未知schema、v1无decoder、升级/回退源hash | 不支持0013；历史原件保留，回退不修改封存结果/源hash、不产生设备或质量写入 |
| R-C16 | Synthetic父帧重复10次、RealCapture故障派生、缺生成器环境但固定像素可读 | 来源不混标；独立实物数不增加；固定像素路径可运行，要求再生成路径缺闭包0004 |
| R-C17 | RegressionCli/CustomerReproCli分别装配§12目录；换相同数据的两Reader | §12两个不同预期正确；换相同目录后身份/标签/错误/资源契约等价，不依UI/产品DB |
| R-C18 | 断连/权限撤销/宿主关闭；Engine状态不明且资源未退出 | 不再接纳，旧操作查询Unknown/Draining；未退出不释放；进程内替身返回后才能终态 |
| R-C19 | 结果分页100条，总205；损坏页digest、断开页/零进展NextOffset | 合法页100/100/5，六和205；损坏/重复/缺页0002，循环不得卡死成功 |
| R-C20 | 有已知原结果但Program/Engine不可用的HistoricalExplain | EngineStart=0；可读原结果完整投影，案例Incomparable，操作Completed；不称重算相等 |
| R-C21 | Existing返回Session=null+Found/Result，原Program已撤销；同主体合法查询 | §12同路径消费原报告/页，返回原digest，EngineStart增量0；不把Session=null当错误，不先预检新执行依赖 |
| R-C22 | Created后Completion等待取消、Query/页读取/消费者抛错；Engine闩锁未释放，兼容Retain故障 | §12.2预留Root始终持原Task/Session/Service/hold；finally独立Q/L有限返回并确认原Owner，禁止Retain失败后无限等本地Dispose；未释放占原permit，Existing关闭不取消原运行 |
| R-C23 | CAS按Revision=r读回；别的合法迁移先提交r+1；原提交回执丢失；同报告SealResult重送 | 返回0016不写旧状态；授权同Owner重查当前Revision/版本；同目标/摘要采纳原回执；未知不CAS，重复封存不重复增revision/Execute |
| R-C24 | Query混合旧report/新state/revision；旧record缺Revision或Owner；旧v2只读结果 | 混合快照0002/0013不能消费；不从事件序号/0猜Revision；旧精确decoder合法查询，v3写端口不CAS旧记录/重算hash |
| R-C25 | 同RequestId在租户A/B，同租户不同Subject，已知另一主体CaseResults引用；伪造Author/绑定UI主体 | 只有显式授权scope可Query/读页；拒绝Unknown+0005且所有敏感字段null，无法由ID获Owner/报告/Revision/存在性；绑定不匹配构造失败，Author不升权 |
| R-C26 | 已允许事件/查询/源stream，在交付/下一页/导出前撤权；授权端口不可达；Completion已发信号 | 停止新内容交付、清旧UI投影；无缓存Allowed后备，Completion不含结果；Query拒绝0005，安全RequestClose/Drain/保持仍可进行，旧合法交付不假称撤回 |
| R-C27 | Start只获执行许可但无现存操作Query许可；Existing观察token取消；共享底层Store不同scope facade | 不泄漏既有回执/冲突摘要、不二次执行；Existing token不取消原运行；Store/Reader/Controller BoundSubject逐一匹配，原Owner保持唯一、无跨实例静态主体 |
| R-C28 | §12.3两个空Host、独立Reader/Resolver与完整Options/resources/clock/authority；§12.4全部普通资产与六个domain向量 | 字节/hash/完整引用、request/closure/result编码分别匹配；Engine生成候选、Store生成结果，不预装输出；Regression六类(2,2,0,0,0,0,0)，Customer(2,1,0,1,0,0,0)，两页偏移0/1/2，绝不从Host名决定比较 |
| R-C29 | Root两槽未settled，第三预留；Factory/Start/Completion/Read闩锁逐处超ObserveBudget，迟到成功/异常 | 第三Factory/Start增量0；原Task/结果与借用scope强持，同ID先Unknown后Found；普通任务不占cleanup保留8槽，页Task完成复用位置；不重Start/Engine，释放闩锁后同槽一次归还 |
| R-C30 | stopToken已取消，Q Store闩锁2s、L关闭闩锁3s；Confirm/兼容Retain故障，Dispose/Hold未完 | cleanup预算独立并行，前台以max(Q,L)+调度开销有限返回；Q失败不覆盖原业务异常，L到期不证执行结束；QueryOwnership仍原Root，BackgroundOwner确认不新分配；后来Resume同原Task/ID，不退出共享runtime |
| R-C31 | §11.4 A/B两个STA、三语、错误Subject/旧revision、撤权、慢Dispatcher/Detach与线程ready超时 | 启动前Root持线程任务；各Dispatcher创建/更新/解绑本控件；A清投影/Unbind不取消B，旧generation不回写；Unbind就绪后才Shutdown/线程退出，所有participant Dispose后归还hold；固定1920×1080真实WPF另运行，文档不冒充通过 |

### 14.2 新增装配与显示切片的定向断言

以下随对应实现执行，未执行不得标通过；原R-C01～31和§12.4完整Golden保持。

| ID | 具体输入/故障 | 必须断言 |
|---|---|---|
| R-C32 | §9.5两Host+seed1、错control/ticket、Declared未就绪choice、fault未命中 | 固定state/首结果/index；错绑定零Start；每必需fault/断言有结论，未命中/缺事件失败0015；ProcessKill未接真实worker0013 |
| R-C33 | codec重复/未知键、缺/null、非法UTF8、depth65、超单文档、整数9007199254740993 | 原bytes长度/hash先核，数值无double损失；允许空白不重算旧identity；schema/T组合错0013；超限拒且无半对象交付 |
| R-C34 | mutation Kind/payload不匹配、旧Revision、同时append/state、AfterCommit回执丢失 | Owner/原scope不换；Reserve唯一；串行页/事件完整；同幂等键同内容原回执、异0016；原ID回读Unknown不重Execute；Memory超限零半写 |
| R-C35 | 257×259/末像素、空域/半开run、RGB交集、错误RowBytes、big-endian、native迟到 | 最后tile/域保真；非法run在gen_region_runs前拒；源pin及compose3输入保活至真实返回；共享pointer从不写；HALCON数值断言按§20 |
| R-C36 | worker Submit迟到、QueryFound、IPC断开、Stop观察超时 | 不二次Submit；Found不当Released；原Task/reader保持，确认进程退出+实际lease/IPC退款才释放；generation/subject错拒 |
| R-C37 | Export Begin/Commit回执丢失、撤权、同key异digest | 原destination/stage三元身份查询，独立cleanup预算；Unknown含0014、旧boolfalse不误报已知未提交；不得再Begin/重写/删原资产 |
| R-C38 | 两STA四Control，错误Lifetime/epoch/source、coordinate缺映射、signed、域带孔 | 同Control公开端口；无坐标/不支持格式0013；Gray/RGB布局/交集不变；publisher稳定数组CopyRow无IO；源/复制峰值计账 |
| R-C39 | Show旧Task迟到、A撤权Clear、Clear后Show、Bind半失败、Unbind慢Return | 空Update实际Detached/VisibleConfirmed后才清成功；不重Attach/Bind；A不影响B；原entry Remove后才Retire，Return未知持两Root/Dispatcher且不清账 |
| R-C40 | §15.2全部负载与预算邻接值 | 目录/页/分母守恒、有界内存、超限拒绝不截断；合成限额与客户目标分开；未测/删失/Unknown列明，Targets空不称性能达标 |

真实HALCON向量另测byte有向差255-0/0-255、int2 -32768与32767差65535、域外亮点不能入统计、空域、三通道仅第三通道变化、real非有限、light_dark两个角色Region、多候选/不同坐标/变化模型；逐项按§20预期。真实持久Store测断电/耐久、worker测确认退出/IPC释放，UI测§11三语/键盘/关闭/双实例；均属于对应切片验证，当前未执行。

## 15. 性能预算和可观测性

本节冻结测量协议与测点，不设未经真实消费者采纳的性能达标值。每个不可变 BenchmarkProfile 必须记录唯一 ID/修订/hash、构建提交与 .NET/适配器/后端版本、OS 与 CPU/内存/存储/网络配置、带 hash 的输入集及规模分布、调用混合与并发/到达模型、队列与资源预算、时钟测点边界、故障注入点，以及 ColdSampleCount、WarmupIterationCount、MeasuredSampleCount 和各指标的验收目标/阈值来源。Profile 变更必须产生新修订，不得跨 Profile 合并数据。

冷测每个样本均从新进程/新模块实例开始，并清空模块自有缓存；OS 文件缓存、数据库缓存、外部服务和设备状态无法由模块清空时，必须记录其实际状态，使用隔离可重建夹具，不标称为冷。热测先按 Profile 固定次数执行预热，再按固定样本数测量；不使用自适应停止、只报最快值或丢弃慢样本。外部副作用操作使用可重建隔离夹具和唯一操作 ID。每个样本用单调时钟记录原始耗时；P50/P95/P99 的算法按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md) 计算，并同时报告样本数、单位和原始值。吞吐量使用 Profile 固定的观察窗口计算已完成且有效的操作数/时间，并单列拒绝、错误、重试和未完成项。

每轮同时记录 CPU、工作集/私有字节、托管分配与 GC、native/适配器缓冲、磁盘/网络 I/O、连接/句柄峰值，队列当前/峰值条数与字节、排队等待、积压变化、接受/拒绝/丢弃计数。排空时间从关闭新接纳开始，至在途操作、回调、IO/适配器资源全部实际归还结束；期限到达只记超时和未完成项，不得强杀后宣称排空。每项验收阈值必须引用消费者要求、正式 Contract/资源风险依据或已批准资格记录的稳定 ID；没有来源时写 TargetPending，只能报告测量结果，不得判定达标。协议/资源硬上限与性能目标分开，只有唯一权威中的必要性、数值和来源均已明确时才可作为硬上限，不从基准数据臆造上限。

### 本模块固定测点
分别测证据/工程包加载、校验与预检、首个案例结果、全批完成、结果比较、封存、取消到源执行真正退出/资源归还，以及外部Store报告事务至Completion的独立时长。Profile 固定案例数与各案例像素/点云/模型/图像字节分布、证据闭包 hash、HALCON/AsunImage 与 GPU/native 后端及版本、确定性等级、并发/批次、冷/热缓存、I/O 和故障注入计划。记录节点与案例有效吞吐、逐阶段耗时、队列/租约、复制字节、CPU/GPU、托管/native/显存峰值、失败/重试和 drain 未完成数；不可通过省略慢案例、丢弃错误或改变比较语义改善结果。真实性能阈值和样本规模无消费者批准来源时为 TargetPending。

### 15.1 BenchmarkProfile 的模块输入形状

```csharp
public sealed record ReplayBenchmarkTarget(string Metric, string Unit,
    string Limit, string SourceId, string SourceRevision);
public sealed record ReplayBenchmarkProfile(string ProfileId, string Revision,
    ContentRef Inputs, ContentRef BuildEnvironment, ResourceBudget Budget,
    ReplayPurpose Purpose, int ColdSampleCount, int WarmupIterationCount,
    int MeasuredSampleCount, int MinimumValidSamples, TimeSpan ObservationWindow,
    ImmutableArray<string> StageIds, ImmutableArray<ReplayBenchmarkTarget> Targets);
```

Profile以§9.1引用规则封存；Inputs包括案例数/像素或点数/通道/有效域/模型/图像大小分布与cold/warm状态，BuildEnvironment包括构建快照、OS/CPU/内存/存储、.NET/适配器/后端/驱动/全局线程版本与摘要。并发/排队/资源上限是Budget硬约束，不能用最快样本反推。Cold/Measured>=1、Warmup>=0、MinimumValidSamples>=1且<=MeasuredSampleCount（热测最低有效数；cold全部ColdSampleCount须有效并另报）、ObservationWindow有限正；无明确样本计划不运行“达标评估”。StageIds必须包含Load、Preflight、Queue、Execute、Compare、CaseSeal、CancelToDrained、DrainedToReleased、AcceptedToReleased、ReportCommitToCompletion，不发生取消的测点NotApplicable；引用§3资源字段同时记录观察能力。阶段可重叠，不把阶段时长相加冒称端到端。

Targets每项Metric来自上述阶段/资源或Throughput/拒绝失败计数，Unit固定ns/byte/casesPerSecond/count，Limit为非负规范数值文本且方向在Metric定义（latency/peak上界，throughput下界）；SourceId/Revision必须来自消费者要求/资格Profile。为空Targets可做诊断，结论NotEvaluated，不造目标；未知测点NotObserved/删失/排空未知禁止判通过。统计/分位和失败样本口径仅按DEV-GOV-010§3.1；Core fixture规模/字节预算证明计费、背压及复杂度趋势，不称现场性能。真实HALCON和UI加载/刷新各自Profile与Core分开测量；真实阈值/样本批准来源待§21门，不阻本节方法实现。

### 15.2 固定合成软件负载与失败边界

本节是可执行的诊断负载，ProfileId=replay-software-load/Revision=1，各行独立Inputs/BuildEnvironment/hash，不构造客户节拍、准确率或性能目标。仍取两个§12.4原夹具为模板；只在新负载中生成新的CaseId/request/namespace/目录引用，不改原Golden。所有生成值和请求在第一次调用前codec冻结，Inputs包含生成规则/参数与每实际asset引用；重复生成byte/hash不同即失败。

| 负载 | 固定输入与执行范围 | 调用/样本与合成限额 | 可判定的软件断言 |
|---|---|---|---|
| S-small | Regression/Customer原两case，Case值原样 | 两Host独立root；cold3、warmup5、measured100、minimum100；观察窗口60s；预算沿§12 | 两原分母/分类不漂移；同ID重复不启动第二Engine；最终本方lease/permit零 |
| S-directory | 1,000,000 case；i=0..999999，ID="load-"+i的6位十进制，克隆case-01并替CaseId，输入/baseline仍引用同只读原资产；目录页256，末页64，共3907页 | 仅ResolveScope/Preflight与顺序分页全扫，不运行百万节点；codec=(4194304,64,65536,4096,65536)、MaxReadPageSize256/MaxReadBytes1048576、MaxInputBytes2147483648、MaxCases1000000；cold3/warmup1/measured10/minimum10，单样本deadline10min，窗口600s | ordinal/offset/Count/每CaseId唯一及最终计数1,000,000；只持当前case页与有界页描述/已登记摘要，输出不造百万ReplayCaseResult数组；MaxCases999999在读case前0006；页3908错offset/重复ID/超bytes拒 |
| S-batch | 10,000 case；ID按5位i生成，其余同case-01；每256一页，共40页/末页16；ScalarEngine逐案运行，输出页有界 | Budget=(10min,268435456,67108864,10000,4,0,0,8)，Store64MiB；cold3/warmup3/measured20/minimum20，窗口600s；单次一run、内部并发4 | 分母10000、无重复/遗漏；结果页hash/分类与模板一致；输出累计到限额拒而非截断；取消保全部未执行分母与已封案例，最终同ID查 |
| S-image | Gray8 257×259，v=(x+17*y)%256；候选仅(256,258)由原34改35；Full；追加原/候选各一空域及逐奇数行[1,256)带孔域 | tile256×256 halo0：4块，末块1×3；完整Gray8每plane66563 bytes；HALCON工程差单并发，CPU原/复制/native/tmp显式预算256MiB，native128MiB；cold3/warmup5/measured100/minimum100，窗口60s | 最末像素不漏；Full maxAbs=1；域外变化不入统计，空域Incomparable；RGB仅B通道变化可见；int2两极差65535沿§20；真实HALCON执行才能判图像断言 |
| S-large-image | Gray8 16385×8193，v=(x+17*y)%256按行生成，候选仅最后一点+1；Full原runs8193 | 每plane134242305 bytes；tile256×256共65×33=2145块，末块1×1；单并发，流式source，MaxCopyBytes1048576仅工程差tile，CPU128MiB/native32MiB，受控工程暂存512MiB；cold3/warmup1/measured10/minimum10，窗口600s，deadline10min | 完整原stream hash先核、无整幅tight数组；maxAbs=1、tile完整覆盖、峰值/暂存计费；未声明tile equivalence的原节点全图预算不足0006；若无已批准暂存能力明确0013，不跳过当成功 |
| S-protocol | 每原Host同ID16并发Start，40事件、MaxEventBuffer32；BeforeResultSeal/Return闩锁；UTC跳+10s、撤权与回执丢失分别独立run | Simulator§9.5 limits；cold3/warmup3/measured100/minimum100，窗口60s；各闩锁真实观察2s，到期显式Release，外层10s | Created唯一/EngineStarts一次；Progress可合并，状态/封存事件不得丢或伪成功；超队列拒；Unknown原ID恢复；执行/Store两轴与所有实际借用守恒 |
| S-dualSTA | §11.5两STA各双Control、16×16完整Gray8/Gray16各两源，依次Show→Clear→Show→culture zh-CN/zh-TW/en-US→Unbind | 原显示限额；cold3/warmup3/measured20/minimum20，每样本100次换Case循环，窗口60s；实测固定1920×1080 viewport | 同Control Presentation/Lifetime；空后不重Attach/Bind；晚到Return保原frame；A撤权不清B；收尾frame退休/lease归还一次，三语身份/命令不变 |

通用软件失败门是契约与本节合成Profile的已声明上限：错hash/域/分母、重复执行、权限泄漏、未完成断言、资源超限、错误丢弃和排空未知均失败；不能将NotObserved字段当零。cold/热样本失败、超时或资源未知全部保留独立计数，minimum不足不判通过；这些不是客户性能阈值。P50/P95/P99仅按§15公共方法报告，Targets=[]时结论NotEvaluated，实际客户Profile由消费者冻结。普通合同Exe不强制执行长时Benchmark；本节由同Exe显式诊断入口运行，外层时限=单样本计划×次数+cleanup余量，有限且不占用§16短合同门的120s；每样本到期保原Owner并判失败，不拿中止进程当Drain。

参数来源保持§20.3：Replay不推荐或静默改生产阈值/模型。tile尺寸本Profile固定256，生产由宿主冻结且仅已证明tile-equivalent的计算路径采用；checked峰值估算不满足就拒/请求显式新Profile，不自动缩小tile改变原节点语义。视口Fit为显示导航；手动格式LUT与可信完整统计驱动的自动显示窗按viewport原Owner，无统计不补全图min/max。这些均不修改原测量、容差或生产事实。

## 16. 独立构建、发布、回退与第二消费者

WPF双STA验证唯一工程为tests/Modules/replay/Asun.Modules.Replay.Wpf.Tests/Asun.Modules.Replay.Wpf.Tests.csproj，net10.0-windows/UseWPF/OutputType=Exe，引用本模块Core/Wpf和本机冻结DevExpress25.2.3；不引用产品Shell/其它模块私有UI。公开Wpf测试类型ReplayStaHostLifetime按§11.4实施。三语resx属于Wpf程序集自身资源，不把Core变成Windows工程；无图像基线EnableEvidenceImages=false，真实viewport Adapter只在正式显示用途单独接线。规划dotnet run --project该Wpf.Tests.csproj -c Release会构建测试与受测引用，不能仅build Core后用--no-build声称UI可运行。本次未创建这些工程。

唯一工程：Core=src/Modules/replay/Asun.Modules.Replay.Core/Asun.Modules.Replay.Core.csproj（Microsoft.NET.Sdk/net10.0，仅BCL）；Core验证=tests/Modules/replay/Asun.Modules.Replay.Core.Tests/Asun.Modules.Replay.Core.Tests.csproj（net10.0/OutputType=Exe，仅受测工程+BCL，无待选测试包）。Simulator/RegressionCli/CustomerReproCli为此Exe内不同Host装配入口和用例组，不要求额外工程。纯BCL Adapter唯一工程=src/Modules/replay/Asun.Modules.Replay.Adapters/Asun.Modules.Replay.Adapters.csproj（net10.0，仅Core+BCL）；Core.Tests按需引用此受测Adapter，R-C33/34在同Exe运行，不引UI/native。真实AsunImage适配器及WPF程序集后续分别位于src/Modules/replay/Asun.Modules.Replay.AsunImage/与Asun.Modules.Replay.Wpf/，不能泄漏其依赖到Core；AsunImage真实验证唯一工程=tests/Modules/replay/Asun.Modules.Replay.AsunImage.Tests/Asun.Modules.Replay.AsunImage.Tests.csproj（net10.0/OutputType=Exe，仅Core/Adapters/本AsunImage包及既有冻结依赖），执行R-C35/§20向量；Wpf.Tests图像切片显式引用本Adapters及上游image-frame/viewport公开程序集，禁止上游私有代码。每包build同名csproj、每对应Exe用dotnet run --project同名测试csproj -c Release；实际可运行性逐包验收，Core Exe通过不代替。规划命令（本轮未创建工程、未执行）：

```powershell
dotnet build src/Modules/replay/Asun.Modules.Replay.Core/Asun.Modules.Replay.Core.csproj -c Release
dotnet run --project tests/Modules/replay/Asun.Modules.Replay.Core.Tests/Asun.Modules.Replay.Core.Tests.csproj -c Release
```

每命令外层有限超时为300s（软件验证停止门，不是现场性能指标），测试每用例真实观察期限10s、整批120s；可控制闩锁保证测试自己能在失败后释放替身资源，禁止Sleep碰运气。超时外层停止测试进程并记失败/未完成，不将强杀当真实Engine排空。Exe执行§14全部Core用例及两个Host，任一断言失败/必需项跳过/未完成返回非零并列用例ID；全部完成通过返回0。不使用dotnet test无报错代替执行；HALCON/进程耐久/WPF切片另用真实适配器资格入口。

Core允许写上述代码/测试目录，只读本指导、已批准公共契约、消费方公开签名；禁止其它模块/共享Schema、入口、客户项目、历史原件、AsunImage内部、生产事实/设备端口。当前文档任务仅允许本指导，不因这段规划创建工程。开始代码前绑定权威可审计仓库/快照（当前无.git）及用户指定实现切片；内容自审由本永久会话负责，总控仅调度/收状态；发布Core不要求其它模块同时实施完毕。

发布工件为版本化Core DLL+XML公共API文档+本指导版本与契约schema+已执行验证摘要；实际适配器/WPF包只包含本机冻结依赖引用及其独立验收，不能把供应商依赖安装/许可证检查当待办。Replay自身状态/错误Owner为Core，平台C-01/C-04/C-07映射及产品Page接入由主会话串行采纳，不回写平台第二套DTO。发布门逐切片见附录A，未满足者不能混入“已完成”发布。

兼容矩阵：当前模块Contract v0.3的新操作写replay-contract-v3/replay-operation-v3，旧v2操作仅按§4.2可信Owner/Revision/精确decoder只读映射；案例/比较/摘要schema未改变，不重算旧hash。v1资产只保留原decoder/hash规则，未提供明确decoder的旧包仅以原始证据查看且报告UnsupportedSchema，不能忽略字段后执行。v2字段/单位/状态/公式改变升契约；新增可选字段只有schema明确default/null及读写规则才兼容。迁移创建新manifest引用，保留旧资产和映射，旧报告不重写；回退先拒新接纳→等/隔离旧资源→保留旧二进制/配置/报告→切旧包→同样案例做读/解释/执行/差异检查，失败保持可查询/历史查看但不执行，服务能力Unavailable不等ReplayState新增NotReady。第二消费者CustomerReproCli使用同Core/契约，独立Reader与脱敏输入，不复制算法、处置或质量放行。两个Host输入与§12共同断言必须真正在独立组合根跑通，文档例不等集成证据。

## 17. 两轮自审与当前准备结论

本轮自审按两个视角逐项走正常/空/大规模/弱信号/遮挡/退化/多候选/改参，以及取消/期限/迟到/断连/关闭/Unknown/迁移/第二Host：
- 第一轮，数据与算法正确性：修复未定义引用/输出类型、重复MaxCases、无来源默认硬限、Before/After只给hash无法执行、Int64>2^53丢精度、来源/训练依赖误扩大、hash自指与UTF-8错误排序、原图domain被忽略/整数差裁剪、六分母及百万结果单数组。具体规则见§3、§6.1、§7、§9.1、§20。
- 第二轮，外部宿主与生命周期：修复同步阻塞示例、Start拒绝/Existing/Unknown不能表达、CTS取消与等待取消混淆、Drained误当资源已归还、ResultSealed先于最终资源摘要、取消/提交竞态、迟到generation/事件游标、原RequestId查询/封存幂等、页面关闭/断连误重跑、第二Host只是名称。具体端口/Owner/恢复见§4–5、§8–12、§14–16。
- 本轮为文档审查与定向结构/引用/契约校验，不是代码运行证明；未执行Core、HALCON、WPF、benchmark或客户现场验收。仍为DesignReview/Prep；原Core接收保持，本轮全部批准范围的文档准备与各实际资格分别按§17.3/§23（附录A）记录，不再以旧全部PreparationIncomplete覆盖当前接收。六项定位和真实外部门见该表，不用文档章节数代替准入。

定向检查结果：本文件Markdown代码围栏成对；公开声明无重复Owner（ReplayProcessRoot按两处partial合并），代码片段使用的模块类型均可定位至正文声明/明确类形状；§3/4/11.4/12构造参数、主体绑定、Revision回读、状态目录、错误0016–0018、分页与四个摘要入口已交叉核对。文件链接全部解析到现存目标；原H盘Sim-to-Real链接改为同SHA-256的保留副本，原文hash未改变。旧v0.1仅作禁止沿用的历史文字，无同步GetAwaiter/GetResult和CancelAccepted旧事件。上述为文档定向检查，不是编译/API重载/WPF/性能或现场验证。

### 17.1 2026-10-10 三项定向退修与两轮反例走查

本次只接续主控明确退修，不重研或重写其它正确规格。①§12统一Existing+Result与Created消费，所有持有句柄的return/等待取消/读取异常进入finally，按OwnsExecution关闭或仅Detach；Draining/Unknown先成功保持或本地继续等真实释放。②§4/4.2 Lookup新增原子Revision/ContractRevision/RecordSchema，CAS返回提交快照、匹配版本、冲突/回执丢失先回读，不借事件序号猜revision。③§4.0绑定可信Tenant/Subject/AuthenticatedSession，明确CheckAsync及各入口/页/流/事件/导出当前授权；Completion改无数据信号，拒绝跨主体ID/引用查询泄漏。

第一轮按Host数据消费视角走Existing无Session报告、Found无结果、Unknown/拒绝、Created读取抛错、半程取消、旧v2只读和CAS回执丢失，核对正文/API/样例输出分支。第二轮按并发/撤权/资源视角走Revision竞争、同租户不同主体/跨租户同ID、事件/流交付前撤权、Existing取消token、保持失败/迟到关闭，核对没有重新Execute、跨主体快照或提前释放。新增R-C21～27为未来Exe的验收向量，本轮未执行这些测试/编译，不以文档走查冒充通过。

当时Module API Contract升v0.3（指导0.2.1-prep）；变更集中公开会话/lookup/授权形状与操作record-v3，replay-jcs-v2及既有案例/图像/比较规则保持原定义。当时各切片PreparationIncomplete，等待主控对三项/API及scope装配的串行确认；当前接收以§23（附录A）为准，不沿用该历史停点。真实Store、授权适配器与旧记录可信ACL映射仍为对应适配器/集成门，不能默认为已经满足；纯托管Root/保持与装配六项文档规格已在0.2.2-prep接收范围内。只修改本指导，无新增报告/脚本/产品工程。

### 17.2 2026-10-11 公开装配、Root收尾与双STA定向收口

指导升0.2.2-prep，Module API Contract保持v0.3；0.2.1-prep可信主体/逐入口授权/原子Revision/CAS接收意图保持，不重复全审。新增§12.1公开Factory/全部依赖构造，§12.2 Factory前有界进程Root槽、强持原Task/资源hold、独立Q/L cleanup与后台Owner确认，§12.3两个完整空Host，§12.4完整输入/输出编码Golden及原ID正常/反例查询；§11.4公开Controller/Bridge/实例三语/Unbind/双STA线程寿命。旧Retain仅同Root兼容facade，不再以登记失败后无限Dispose作为离栈恢复。

实现者视角按准入→Factory→Start→Completion→两页→关闭正常链，再逐处取消/异常/回执丢失/撤权/迟到回调/槽满/Dispose闩锁走恢复；收口普通Task槽复用与cleanup预留8槽、Service开始Dispose后不再查已关闭Store、Hold真正归还与tombstone不泄漏内容。外部消费者视角从空net10.0 Host逐构造reader/resolver/engine/store/comparison/clock/resources/options/authority，核完整内容与引用不是外部变量，独立Reader输入与固定分母不同；从双STA线程启动前Owner走到Dispatcher内Bind/Refresh/撤权/Unbind/线程真实退出，消除Shutdown与Drain环依赖。

定向编码核对在内存通过正文完整JSON生成UTF-8/domain字节，用PowerShell .NET SHA-256生成，另以Python读取本指导复算33项bytes/hash及所有ContentRef关联；普通资产和六个域向量分开，零失败。Markdown围栏与本地链接、唯一partial类型声明定向检查通过。R-C28～31是未来真实Exe/WPF执行断言，本次仅文档自审与编码校验，未build/run/Core Test/HALCON/WPF/性能/现场验收。未新建报告/脚本/工程，唯一写入本指导。

本次可决定的内部装配/cleanup/UI接线规格不转外门。主控回读后已接收R-Core-Contract及纯托管运行编排、协调、根Owner六项文档规格为ModuleCoreImplementationReady；R-Wpf公开装配/恢复指导限定内容接收，当前状态见§23（附录A）。主控已复核33项完整Golden canonical bytes/长度/hash一致，其中25项按独立字段与引用图重建（含两完整request/closure），不是仅复制hash；本次窄修不重审、不改编码契约。§11.4步骤3已统一三参数ReplayStaHostLifetime构造，进入STA后BindDispatcher一次，不增重载。正式客户节点/资产ACL、真实Store/Authority/ExportSink/viewport、Store耐久/worker监督、真实HALCON/WPF/性能/现场仍分别按§21验收；可审计代码基线与实际实现验证尚未完成。以上是0.2.2-prep当时的范围记录；本轮可决定的内部指导准备见§17.3，不沿用当时等待内容接收的停点，不自授产品Ready。

### 17.3 2026-10-12 全批准范围的模块自审结论

指导0.2.3-prep/API v0.3。当前架构批准的Replay职责是回归、离线调参实验与客户问题复现；覆盖历史解释/重新执行/Checkpoint入口、工程候选变更、值与图像差异、场景/fault测试、报告分页/导出、无UI组合与可选工作台。全部仍为工程域，生产事实只读、不训练/发布模型、不控制设备/放行。X-Ray/ICT/FCT不扩展。

**文档准备结论：DocumentPreparationComplete。** 本永久会话从实现者和宿主两个视角完成新增内容自审，当前批准范围中可由软件/架构决定的API、算法、数据流、Owner、资源、恢复、三语/UI、测试入口与负载方法欠账已闭合；无需总控再做模块内容审核。该结论是指导准备，未授产品ImplementationSpecificationReady/SoftwareClosed；此前已接收的两Core切片Ready保持，不以本文版本撤销或扩成实测通过。

| 批准能力/输入→输出 | 唯一实施章节与自审结果 | 验证及真实后门 |
|---|---|---|
| 原证据/程序/完整目录→预检、历史解释、执行请求 | §3～6、§9.1、§10.1；codec/闭包/目录/主体授权、缺项/不支持明确 | 原Golden保持；R-C01～31/33；真实客户输入/ACL及节点版本由消费者/资产Owner提供 |
| 显式Before/After/原Graph→候选工程输出与值/图像差 | §6～7、§10.2、§20；精确数值/域/类型/节点注册/HALCON路线、tile与预算固定 | R-C35/§20；节点专业语义归原算法模块，实际HALCON/AsunImage消费编译/运行由本模块实现Owner验证；物理容差不造 |
| 场景+事件/fault/schedule→有断言的运行manifest | §9.1.1～9.5；公开Factory/Control/Runner、固定xorshift/schema和未知处理 | R-C32/§15.2；仅测试namespace，真实ProcessKill/OS资格另门 |
| 原请求/封存案例→页/终态报告/幂等回执 | §4～5、§10.1/10.3、§12；typed mutation/CAS、Root双轴/原Task、worker与Export三态明确 | R-C34/36/37；Memory合同可实现，介质耐久/保留/worker死亡证据及导出目标由各实际Owner提供并验收 |
| 同Core两Host→独立回归/客户复现 | §12.1～12.4/§16；原输入/Factory/生命周期不重审，无UI算法完整 | 原33项完整Golden内容保持、原接收复用；实际build/run与第二真实消费者由本模块实现Owner负责 |
| 已授权报告/图像→三语双图工作台、差异/时间线、可恢复导出 | §11.1～11.5；同Control Presentation/Lifetime、FrameBudget/域/坐标/CopyRow/空后Update/Return/Retire与双STA已固定 | R-C31/38/39；仅2D image-v1公开CPU源，专业3D/Region/XLD为只读artifact/原Owner适配；真实1920×1080 WPF视觉/键盘/UIA/native资源验证未执行 |
| 固定输入/环境/资源→诊断时延、吞吐/资源与尾延迟 | §15.1～15.2；小批/百万目录/大图/协议/双STA样本与硬边界可照文执行 | R-C40；实测由本模块实现Owner完成，客户目标/代表包/现场条件由消费者与资格Owner冻结；Targets空只NotEvaluated |

本轮定向文档验证：所有本地Markdown链接目标存在，55组代码围栏配对；公开重复声明只有既有ReplayProcessRoot的两段partial。新增§9.5/§10.1～10.3/§11.5/§14.2/§15.2定位及R-C32～40唯一；固定xorshift首步、图像字节/tile边界与目录末页计数已在内存独立复算。§12.4原33项完整Golden段SHA-256仍为b04ab92216d60bfee708639cc10f663032982331df37fd5badc4c3b6019b8008，未重算或重审已接收向量。以上只证明本轮结构/规格算例一致性，不是产品C#、HALCON/WPF或负载运行证明。

仅留下真正外部事实与执行资格，逐项Owner见§21；不再把Simulator装配、codec/CAS、HALCON搬运/工程差、Export未知、viewport对接、三语、软件负载计划作为等待上游/总控设计的欠账。缺实际资产/节点/坐标事实时按明确错误拒绝对应用途，无关Core工作可继续。本轮只修本指导，未创建产品/测试工程、脚本或报告，未运行产品构建、HALCON、WPF或性能/现场验收。

## 18. 依据与只读借鉴

- [PKG-043 Replay](../../shared-modules/packages/PKG-043_Replay.md)：包职责、规划消费者、隔离运行和取消排空边界。
- [SM-021 Replay](../../shared-modules/modules/SM-021_replay.md)：通用视觉回放职责、依赖与版本迁移原则。
- [DEV-QLF-070 Golden Sample 与 Replay](../../shared-modules/guidance/08-qualification/DEV-QLF-070_Golden%20Sample与Replay开发指导.md)：闭包、切点、确定性、比较顺序和 Golden 资格边界。
- [独立模块架构](../INDEPENDENT-MODULE-ARCHITECTURE.md)：独立模块准入、层次、第二消费者和金标准章节。
- [INTERFACE-MAP](../../shared-modules/INTERFACE-MAP.md)：资源租约、状态/事件/事实交接和适配器方向。
- [DEV-CONTRACT-002](../../13-contract-candidates/DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导.md)：候选 Contract/Schema/State/Owner 的采纳限制；本页不创建第二套生产 DTO。
- HALCON 26.05 操作手册：`halcon算子手册/operators`；目标版本语义和cv2入口已按§20冻结，不把手册HOperatorSet签名当成封装重载验证。
- 只读对照：`H:\docs\40-development\80-quality\模拟器与确定性回放开发指导.md`（DEV-TST-001，重点 §§3–8、12–14）。本页仅吸收 ScenarioManifest/hash、虚拟时钟/boot、稳定调度、Replay fault/crash registry 和共同适配器合同测试；其余平台模拟器内容按 §22 排除。
- 只读来源：[视觉数字孪生与 Sim-to-Real 开发指导保留副本](../../references/project-snapshots/PCBA-AOI/20260927/original/docs/40-development/80-quality/视觉数字孪生与Sim-to-Real开发指导.md)（`DEV-TST-004` v1.1，2026-08-09；2026-10-06 全文对照，SHA-256 `816295abb3525b49de80fd1852467101a87f6b818ae2d646ba6aa5aaed5f678f`）。来源定位复用 [full-hdocs-inventory/source-manifest.json](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)；清单状态不在本模块会话修改。§§1、2、4、5 的来源保全/分层要求落实于 §6.1 和 §14；生成器实现、物理模型、训练/挑战集隔离、Sim-to-Real 指标/guard band/自动降级、HIL/FAT/SAT 与生产签署属于外部 Owner，均未迁入。§3 的合成验证不替代真实资格已由 §14、§16 和 §22 覆盖。本次不引入视觉算法或 HALCON 24.11 API，也不继承来源“开发基线”或验收状态。
- [AsunControl Variation Model 参考快照](../../references/project-snapshots/AsunControl/20261004/README.md) 中的 [`C_VariationModel.cs`](../../references/project-snapshots/AsunControl/20261004/original/Vision_Variation_Model/C_VariationModel.cs)（只读借鉴）：`C_VariationModel_Compare.Compare` 的同步回调、`C_VariationModel_Parameters` 的参数组织和 `HObject` 资源释放模式。该项目为 .NET 8/示例能力，不是本模块 API、版本或生产证据。

本次仅复用已固定.NET源码/取消依据，补查.NET10官方[Task.WaitAsync](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.waitasync?view=net-10.0)、[Dispatcher.InvokeAsync](https://learn.microsoft.com/en-us/dotnet/api/system.windows.threading.dispatcher.invokeasync?view=windowsdesktop-10.0)、[Thread.SetApartmentState](https://learn.microsoft.com/en-us/dotnet/api/system.threading.thread.setapartmentstate?view=net-10.0)（2026-10-11直接读取，HTTP200）。WaitAsync只规定等待代理完成/到期；原Task保留Owner来自本文资源契约，不能由等待代理反推底层停止。Dispatcher工作在指定实例线程、STA须在线程启动前设置；因此§11.4采用两个明确线程/原Dispatcher任务及Unbind后关闭顺序，不引入第三方框架或复制视口实现。

### 18.1 本轮实质技术分歧的研究结论（2026-10-09）

| 来源/固定版本与实际读取位置 | 依赖/许可和可迁移内容 | 限制与本文决定 |
|---|---|---|
| [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) §§3.1–3.2、Appendix B/D；读取官方全文 | JCS/I-JSON：重复键拒绝、UTF-16 ordinal键排序、ECMAScript数字、无Unicode归一化、UTF-8输出 | JCS不保留NaN/Inf/-0和大整数精度；§9.1以整数/decimal文本和判别有效性解决，不把JsonSerializer排序等同JCS |
| [cyberphone/json-canonicalization](https://github.com/cyberphone/json-canonicalization/tree/19d51d7fe467d4706a3ff08adf8a748f29fc21e0)，commit 19d51d7fe467d4706a3ff08adf8a748f29fc21e0；实际读dotnet/jsoncanonicalizer/JsonCanonicalizer.cs、jsoncanonicalizer.csproj、dotnet/es6numberserializer/NumberToJson.cs、es6numberserializer.csproj，及testdata/input/values.json、testdata/output/values.json和LICENSE | Apache-2.0；netstandard2.0/BCL，canonicalizer依同仓es6numberserializer项目，无该两个csproj外部PackageReference；SortedDictionary(StringComparer.Ordinal)、严格UTF-8及数字向量有实际源码/测试数据依据 | 库只接Object/Array根，JSON数字解析为double；不能直接处理Replay整数/decimal语义。借鉴规范/向量，不引入NuGet或复制源码为产品依赖；纯BCL实现JCS须以RFC Appendix B与上述对照向量验收，错误即阻摘要切片 |
| [.NET协作取消官方文档](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads)；[dotnet/runtime v10.0.0](https://github.com/dotnet/runtime/tree/60629d14374c56f1cb51819049ad1fa529307f8d) commit 60629d14374c56f1cb51819049ad1fa529307f8d；实际读src/libraries/System.Private.CoreLib/src/System/Threading/CancellationTokenSource.cs及src/libraries/System.Runtime/tests/System.Threading.Tasks.Tests/Task/TaskCancelWaitTests.cs、LICENSE.TXT | MIT；.NET自身BCL，公开取消与等待测试依据，非引入第三方框架 | token/Cancel只是通知，CTS.Dispose不等待native；§4–5/8分开请求取消、等待取消、执行排空和资源归还，不照抄runtime测试框架依赖；公开WaitAsync语义只取消等待 |
| DevExpress25.2.3本机官方XML：C:/Program Files/DevExpress 25.2/Components/Offline Packages/devexpress.wpf.{grid.core,docking,core}/25.2.3/lib/net8.0-windows/ | 用户已冻结授权依赖直接使用，不进行授权核验。实际读Grid.v25.2.xml/Core.xml中TableView.AllowPerPixelScrolling、DataViewBase.AllowEditing/NavigationStyle/ShowSearchPanelMode、GridControl.SelectionChanged；Docking中DockLayoutManager/LayoutGroup/LayoutPanel/DocumentGroup；Core中BarManager/BarButtonItem/BarItem.SuperTip/DXTabControl | 当前没有dxdocs callable工具，官网API页访问403；以匹配安装版官方XML作具体控件依据，不声称已查官网或真实UI。PropertyGrid.ReadOnly文档return描述与摘要矛盾，本页直接用已明确AllowEditing=false的结果Grid，不依该矛盾写编辑行为。实际1920×1080 WPF资格未执行 |
| 本地HALCON26.05.0.0页面与类别，精确链接见§20 | 使用cv2与既有公共控件；本轮读实际算子说明，复用原有Variation/读写/域裁剪证据；不扫描AsunImage | abs_diff/sub_image裁剪、OpenCL差异、min_max_gray/get_grayval忽略domain、reduce_domain不缩矩阵等约束已写固定分支；无真实样本性能/精度证明 |

来源强项和限制均进入正文处理/测试；研究不是软件、客户资格或依赖准入证明。不新增本轮研究报告、外部源码副本或重复manifest。DEV-TST-001/004与旧项目证据沿用§18已有来源，不重复全文扫描/下载；历史封装签名断言已由§20更正为算子语义，不成为重复核验算子存在的门。

## 19. 第二轮场景驱动复审

本节是实现前的反例门禁。每个场景都必须能从输入、参数来源和顺序推导出唯一的状态、错误、恢复动作及验收断言；“函数返回成功”不能代替这些断言。

### 19.1 正常配置与精确执行

**输入与来源：** `EvidenceClosureRef`、`ProgramClosureRef`、切点、原算法/模型/标定 hash 来自 040/035/038 公开只读端口；比较策略和资源预算由调用方冻结，不能由 UI 临时改写。

**顺序：** `Preflight` 校验引用、权限、shape/通道/域/单位、切点和预算 → 建立只读租约 → 固定运行时 profile → 按原节点图执行 → 逐节点封存输出 → 先身份/有效性后数值比较 → 原子封存工程报告 → 排空并归还租约。

**输出与状态：** `Ready → Running → Completing → Draining → Drained → ResourcesReleased → ResultSealed → Completed`，每个案例为 `CompletedEqual`、`CompletedChanged` 或 `CompletedIncomparable`；生产事实写入必须为 0。

**验收：** 相同闭包、同一策略和同一确定性等级的重复运行具有相同案例分母、身份配对和差异标签；原生产事实的版本/hash 未改变；结果可由 `SealedResultDigest` 重新读取。若仅元数据不同，比较策略必须明确排除字段，不能用整份报告字节相等冒充精确回放。

### 19.2 空输入、缺项与部分成功

**输入与来源：** 空证据集合、空图像、缺一个 FOV、缺模型、缺中间节点或只剩缩略图；缺项来自证据读取端口的结构化诊断，不由调用方填零。

**顺序：** 先读取闭包目录和对象摘要 → 按案例建立缺项集合 → 仅执行不依赖缺项的案例 → 固定原始分母并为未执行案例生成缺项结果 → 封存部分报告。

**输出与状态：** 全部不可执行时为 `Rejected`（`REPLAY-0002/0004`）；批次部分成功时为 `Completed`，案例分别记 `Completed*`、`CompletedIncomparable` 或 `CancelledOrNotRun`，不能将批次压成一个 `Success`。

**恢复与验收：** 补齐证据后必须创建新 `ReplayRunId`；FOV1 不得复制成缺失的 FOV2，缩略图只允许历史查看。验收检查缺项对象、原因和分母完整，且生产写入仍为 0。

### 19.3 歧义与错误输入

**输入与来源：** 重复目标 ID、多对一候选、冲突坐标系、非有限容差、错误单位、路径穿越、未知契约字段或 `ExactReplay` 带变更。

**顺序：** 在分配图像/模型前做规范化、有限性、ID 唯一性、单位/坐标和版本校验 → 收集全部错误 → 按错误严重度决定拒绝或案例级不可比较；不执行有歧义的节点。

**输出与状态：** 请求级结构错误为 `Rejected` 和 `REPLAY-0001/0004/0005/0008`；可隔离的单案例错误保留其它案例，并返回 `DifferenceItem` 的歧义标签。

**恢复与验收：** 只能修正输入或建立明确变更实验后重新提交；禁止最近坐标、数组顺序和 `latest` 自动消歧。验收必须证明错误码稳定、错误集合不因输入顺序改变、无半写输出。

### 19.4 超大输入与高并发

**输入与来源：** 多百万案例、超大多通道图像、压缩包展开后超过字节预算、多个宿主同时请求；并发上限来自 `ResourceBudget` 和宿主 Profile。

**顺序：** 先读取压缩头、shape 和预计展开大小 → 申请全局 permit/队列槽 → 分块执行并周期性报告用量 → 背压而非无限排队 → 每案例封存后释放其租约。

**输出与状态：** 超过输入、输出、native、GPU 或队列预算为 `REPLAY-0006`；允许的批次保持固定分母，未接纳案例为 `CancelledOrNotRun`。禁止静默降采样、删目标或降低精度。

**恢复与验收：** 调低并发或拆分为显式案例批次，批次身份不同；同一 `RequestId` 不得因重试产生重复工程结果。压力验收记录峰值字节、permit 数、P95/P99 和排队上界；不存在未释放租约或负 permit。

### 19.5 噪声、遮挡与退化输入

**输入与来源：** 原始图像含噪声、遮挡、过曝/欠曝、空域缩小、退化模型或缺少必要中间状态；这些是证据事实，不由 Replay 生成“干净替代图”。

**顺序：** 校验图像类型/shape/domain/有效支持 → 按原程序预处理和模型能力执行 → 由算法适配器返回 `Invalid`、拒识或候选结果 → 比较有效性和遮挡/支持域差异 → 报告差异原因。

**输出与状态：** 算法拒识或不可观测为 `CompletedIncomparable` 或案例 `Failed`，不得填零或转为 PASS；`REPLAY-0007/0008` 仅在节点失败或比较不适用时使用。

**恢复与验收：** 只能使用证据中明确存在且版本固定的预处理/模型变更作为新实验；不自动训练、不自动增强、不用显示插值补证据。验收覆盖噪声、遮挡、空域和双无效，确认数值接近不能掩盖有效性变化。

### 19.6 取消、超时与 native 排空

**输入与来源：** 运行中 `CancellationToken`、真实单调 deadline 或宿主关闭；native/GPU 中断能力由执行适配器能力声明。

**顺序：** 接受取消 → 停止接收新案例 → 通知节点停止/等待可用中断 → 记录 `CancelRequested` 或 `REPLAY-0010` → 停止接纳并按 §5 标注/封存案例 → 等待 native、GPU、回调、案例IO退出 → `Drained` → 归还租约等资源 → `ResourcesReleased` → 封存报告 → `Cancelled`/`Failed`；回执不明为 `Unknown`。

**输出与状态：** 排空前只能是 `CancelRequested`/`Draining`；未排空禁止 `Completed`、复用 generation 或释放 native 对象。

**恢复与验收：** 没有可靠中断时使用隔离 worker 或等待返回，不强杀进程内句柄；排空完成后从完整封存案例或合法切点新建尝试。验收注入迟到回调和超时，确认旧回调不能推进新请求，且每个资源只归还一次。

### 19.7 资源上限与持久化失败

**输入与来源：** 磁盘满、输出 hash/长度不匹配、写入中断、回执丢失、内存/native/GPU 水位超过预算。

**顺序：** 写临时对象 → flush/关闭 → 校验长度和 hash → 原子封存 → 写工程回执；任何一步失败都保留临时对象诊断并阻止可见结果发布。

**输出与状态：** `REPLAY-0006/0011/0014`；未知写入状态必须查询同一 `RequestId`，不能盲目创建新输出。半写文件不计入恢复点。

**恢复与验收：** 确认回执后才能重试；恢复点必须包含输入、参数、节点、环境、随机状态和输出完整性。验收模拟磁盘满和断电，证明不存在“文件存在即成功”或重复工程结果。

### 19.8 持久化与版本修订

**输入与来源：** ContractRevision、Schema、算法/模型/标定/后端版本和迁移映射来自精确引用；旧结果不可变。

**顺序：** 读取版本 → 检查适配器能力和迁移规则 → 计算 canonical closure digest → 仅在规则允许时迁移可选字段 → 执行/读取 → 结果保留原版本与实际版本。

**输出与状态：** 不兼容为 `REPLAY-0003/0012/0013`；兼容读取必须显式标记迁移版本；改变单位、身份、有效性或比较公式不得按兼容处理。

**恢复与验收：** 无迁移规则时仅允许历史解释或拒绝执行；迁移失败回到原读路径，不覆盖旧结果。验收用同一闭包做旧/新读取、解释、重放和比较，确认修订后旧报告仍可读且差异可归因。

### 19.9 升级与回退

**输入与来源：** 新旧模块/适配器、旧封存工程结果、迁移工具和兼容矩阵。

**顺序：** 停止新会话 → 等待/隔离旧会话排空 → 保留旧二进制和配置 → 安装新包 → 运行读取/解释/重放/比较门禁 → 失败则切回旧适配器；不回滚已封存结果。

**输出与状态：** 升级失败时宿主执行能力为Unavailable；已接纳操作按§5为Failed/Unknown，历史解释仍可用；回退不重发设备或生产提交。

**恢复与验收：** 回退只改变可执行组件，不改变事实和工程结果。验收要求升级前后相同 Golden/Replay 集合的分母、身份、错误和资源释放语义可解释；不以新结果覆盖旧基线。

### 19.10 无 UI 调用与可选 UI

**无 UI 输入/顺序：** 可信主体Host按§12预留Root/hold→Factory→请求（新草稿可预检）→ `StartAsync` → 既有Operation或无数据Completion后授权Query → 统一分页消费 → finally独立有限Q/L cleanup并确认同Root后台Owner，事件通过 `IProgress<ReplayProgress>` 或诊断端口接收；不依赖 Dispatcher、隐藏窗口或控件初始化。

**无 UI 输出/验收：** 以 `ReplayResult`、错误码、工程回执和 `ProductionFactWrites==0` 判定；取消和版本错误可由自动化测试重现。

**可选 UI 输入/顺序：** UI 只绑定不可变 snapshot → 调核心预检/执行 → 显示原/候选、单位、有效性、缺项和排空状态；关闭页面先撤订阅，再等待/观察排空，不取消其他宿主会话。

**边界：** UI 不持有 `HObject`、模型句柄、数据库连接、质量放行按钮或设备命令；UI 的“导出工程报告”只消费已封存结果。验收包含键盘、UIA、语言和 1920×1080 视口，但不把截图当算法证据。

### 19.11 第二消费者与长期运行

**第二消费者输入/顺序：** 客户问题复现适配器提供脱敏后的证据闭包和问题范围，仍执行同一预检、隔离运行、比较和封存顺序；客户处置/返修结论留在宿主。

**长期运行输入/顺序：** 连续运行数小时/数万案例，周期性检查租约、句柄、队列、磁盘和内存水位；按固定窗口封存 checkpoint，窗口间不共享可变 native 状态。

**输出/状态/恢复：** 第二消费者复用同一错误和状态；长期运行发现泄漏趋势、句柄增长、队列无界或 checkpoint 不完整时进入 `Failed/Draining`，保留已封存窗口，从最近完整切点建立新运行。

**验收：** 两个消费者的状态/错误/取消/排空断言一致；长稳测试结束后 native、GPU、租约和临时文件回到宿主允许水位，旧窗口可独立读取，重复恢复不重复案例。

## 20. HALCON 26.05 视觉路线与训练边界

### 20.1 执行主路线与比较路线分开

所有算子均由 AsunImage 的 ImageLibDotNet.cv2 调用；用户已确认完整operator set，不重复检查算子是否存在，不扫描封装内部，不直连HOperatorSet/halcondotnet。下表为已读本地26.05页面的语义依据，不把手册中HOperatorSet签名声称为已验证的AsunImage重载。只有实际C#参数/tuple/封送歧义影响调用时，在消费适配器编译核对；公共Core无native类型。

| 职责 | 冻结路线及依据 | 分支/参数 |
|---|---|---|
| 原算法执行 | 原Graph/NodeRevision/完整状态，原Variation节点使用compare_variation_model或compare_ext_variation_model | prepared模型状态必须存在；缺则0003/0004，不在Replay训练/prepare重建 |
| Variation扩展 | compare_ext_variation_model的absolute/light/dark/light_dark | Mode来自原参数；light_dark有两Region，按亮/暗角色保存，不能合并顺序或当一个缺陷 |
| 工程像素幅度比较 | get_domain→symm_difference/area_center→intersection→reduce_domain→逐access_channel→类型提升→abs_diff_image(Mult=1)→min_max_gray(Percent=0) | 同shape/通道/坐标，显式valid mask；每通道分别摘要，不彩色转灰 |
| 有向差值诊断 | 类型提升后sub_image(Mult=1,Add=0) | 原图a候选、b基线；方向固定，不能在byte上截负差为0 |
| 既有域/裁剪/变换 | reduce_domain/crop_rectangle2/affine_trans_image | 只从原闭包执行；自动对齐仅另存DiagnosticOnly副本，不更改主比较 |
| 读/封存 | read_image/write_image、不可变对象ContentRef | 原始文件字节hash不等于像素等价；有损写出不是Golden或精确baseline |

资料入口：[算术类别](../../../halcon算子手册/operators/toc_filters_arithmetic.html)、[domain类别](../../../halcon算子手册/operators/toc_image_domain.html)；已核读 [abs_diff_image](../../../halcon算子手册/operators/abs_diff_image.html)、[sub_image](../../../halcon算子手册/operators/sub_image.html)、[convert_image_type](../../../halcon算子手册/operators/convert_image_type.html)、[min_max_gray](../../../halcon算子手册/operators/min_max_gray.html)、[abs_image](../../../halcon算子手册/operators/abs_image.html)、[scale_image](../../../halcon算子手册/operators/scale_image.html)、[get_grayval](../../../halcon算子手册/operators/get_grayval.html)、[access_channel](../../../halcon算子手册/operators/access_channel.html)、[get_domain](../../../halcon算子手册/operators/get_domain.html)、[reduce_domain](../../../halcon算子手册/operators/reduce_domain.html)、[intersection](../../../halcon算子手册/operators/intersection.html)、[symm_difference](../../../halcon算子手册/operators/symm_difference.html)、[area_center](../../../halcon算子手册/operators/area_center.html)、[compare_variation_model](../../../halcon算子手册/operators/compare_variation_model.html)、[compare_ext_variation_model](../../../halcon算子手册/operators/compare_ext_variation_model.html)。读过的get_region_points说明空Region返回空tuple且只允许单Region；get_grayval忽略domain且大量逐像素调用开销高，本模块不把它作为大图主计算路线。

### 20.2 像素路线的固定处理与拒绝

1. Reader先校验ContentRef文件完整性，再解码验证类型、宽高、通道、坐标修订及证据有效性；单纯相同文件digest只能说明内容相同，不替代Valid/坐标检查。同像素不同压缩文件只能按像素路线判断，不按文件hash判Changed。
2. 以get_domain取得单图有效域，并与外部invalid/occlusion有效mask显式intersection。用symm_difference及area_center报告原/候选有效域不一致；重叠域为空时CompletedIncomparable/Invalid，不将area_center空域0当“误差0”。有域变化主比较记录DomainChanged；重叠域数值摘要只为DiagnosticOnly，不覆盖全域不可比。
3. 同域时两图reduce_domain到同一有效mask，逐access_channel按1..n比较。min_max_gray必须传这个mask，因其忽略Image原domain；不能传full rectangle。缺valid mask且real像素可能含NaN/Inf时拒绝0008，不依靠最小最大值自动筛掉非有限值。
4. 幅度路线默认CPU、Mult=1。byte/uint2差幅不会超过其非负范围，可直接abs_diff_image；int1/int2在两侧convert_image_type为int4后求差，避免极值差裁剪；int4→real仅DiagnosticOnly（HALCON real单精度导致大整数损失），不能用容差覆盖转换误差后宣布相等，int8及精确raw浮点位比较不走提升像素判等，使用原像素内容schema的精确序列摘要或拒绝此比较能力0013，不自行造另一图像算法。real有限值→real求差若溢出/非有限/范围不支持则0008；不能静默缩放。
5. 单位相同、A绝对容差、R=0的CPU图像规则：对每通道有效域取maxAbs（Percent=0，不剔尾部），maxAbs<=A为数值相等，否则Changed；同shape/类型/坐标/域仍须逐项记录。图像R>0时两侧在可表示范围内convert_image_type为real（byte/int1/int2/uint2可精确表示，int4/int8不以有损提升判等），基线abs_image→scale_image(Mult=R,Add=A)得到逐像素容差T，再sub_image(absDiff,T,1,0)得残差D，显式同mask取min_max_gray Percent=0；maxD<=0为容差内，>0为变化。不能用单个全图max基线替代逐像素T。real浮点按NumericProfile声明精度，Scale/Sub/Abs非有限或舍入风险无法满足已冻策略则不可比较0008；Exact或要求double精度的像素策略不能以HALCON real单精度降级。边界代表图与CPU数值真值须资格核对，不把显示阈值代替算术结果。标量R遵守§3.2；图像多路候选不得由Replay挑“最佳”候选，输出集合身份/顺序schema不匹配为Ambiguous。
6. 若要有向差图，byte/uint2同样提升int4，再sub_image(1,0)；int1/int2提升int4。诊断显示拉伸/伪彩色是单独视图映射，保存未拉伸摘要/参数，不能将显示clip后的灰度当差值。complex/direction/cyclic/vector-field和3D/XLD专用语义由对应算法结果适配器提供Field值/稳定artifact schema；通用像素差不代替周期、拓扑、孔洞、3D物理单位比较，未支持schema0013，保留HistoricalExplain。
7. 每案例由Engine负责顺序释放访问channel/domain/intersection/提升图/diff临时对象；成功转移不可变artifact后释放native，失败/取消在真实退出后释放。估算原矩阵+两提升副本+差图+mask+编码暂存，超预算前拒绝或按冻结tile策略执行。tile必须完整覆盖同mask且顺序/边界/halo（像素差halo=0）进入Program/profile；同tile与全图max聚合应一致，不能抽样、降采样或略过坏tile。reduce_domain不缩矩阵，因此不能把ROI面积当native矩阵内存。

原算法无法执行时不得静默切像素诊断并仍称Exact：宿主明确新用途HistoricalExplain或新DiagnosticOnly策略/请求，具备可读双图才运行诊断。弱信号/噪声/遮挡/退化仍由原节点输出拒识/Invalid，不能Replay“修复”补量测。诊断配准需单独保存变换/插值/新有效域和父引用；主身份/坐标差异仍可见。

### 20.3 同样本路线比较与参数来源

工程比较候选固定为CPU全有效域 vs 预算允许的同语义tile/ROI route；GPU只在消费者Profile声明容差与环境时测候选，不作为未验证默认。HALCON手册明确abs_diff_image/sub_image的OpenCL结果可能与CPU/SIMD略异；不得每会话set_system改全局优化/线程。真实样本以正常、弱对比/噪声、过曝/遮挡、空域、通道变化、整数极值/real非有限、候选歧义及变更模型/参数分层，输入hash/策略/环境相同。核对结果身份/域覆盖/数值误差与不可比率，误接受/拒绝仅在消费者提供真值/阈值时统计；同时测端到端P50/P95/P99、复制/native/GPU峰值、排空、tile开销。无真值/真实测量只记NotEvaluated，不编排名。

参数来源：原节点阈值/mode/preprocess来自父程序或显式ReplayChange；像素A/单位/模式来自比较策略；tile大小/并发/缓冲上限来自宿主ResourceBudget/Profile。Replay不自动推荐/冻结生产阈值，不训练Variation或AI模型。仅报告“哪一显式参数改变造成哪些可观察字段差异”，缺中间状态时只定位两个保存切点之间，不能宣称因果证明或猜更好参数。§15 Profile采纳后冻结最可靠满足语义与预算的route，未经实测不声称优化有效。

### 20.4 模型执行依赖边界

Replay不训练、不更新、不重建模型，无IReplayTrainingAdapter。候选模型由宿主选定不可变ContentRef，带本次推理实际所需预处理/类别映射/标定/后端版本；缺这些执行依赖0003/0004，缺无关训练集、标签/划分或训练checkpoint不阻固定资产推理。外部训练/治理审批状态可作为来源注记，不获得生产激活权。模型内部prepare状态缺失则原模型不可执行；不在Replay补训练或将当前模型偷偷替代历史模型。外部生成/训练可由宿主独立编排再输入新ChangeExperiment，Replay不持有该外部状态。

## 21. 已冻结决定与真正后续门

本模块局部技术决定已在正文冻结，不再等待常规选型裁决：Core自身契约/状态/错误Owner、replay-jcs-v2域隔离、case分页、提交/取消线性化、纯托管两个Host/Exe验证、不可中断执行的等待/显式worker策略、主坐标比较禁止自动对齐、Replay不训练。变更这些决定须修唯一指导再实现，不把“等待Owner”用来掩盖模块内部规格。

真正外部门只影响对应切片：
1. 代码基线与实现授权：用户/仓库Owner提供权威可审计仓库或快照，并指定实现切片；本模块原会话完成内容审核，总控不再承担模块内容接收门。本轮不创建代码。
2. 消费者实际节点Graph/模型/标定/单位与坐标、物理真值/容差和客户数据权限：只阻其真实算法/产品用途，不阻Core合成合同验证；未给值不造阈值。
3. 消费项目C#重载/封送若发生具体歧义则在该AsunImage适配器编译解决，不重复核验算子存在/授权；实际HALCON/CPU/GPU结果与native资源上限/worker回收需真实资格，不用Simulator顶替。
4. 宿主持久Store耐久级别、保留/加密/脱敏/访问与删除政策、进程监督器OS边界：只阻其持久/worker客户用途。Core内存Store协议和明确Unknown恢复仍完整。
5. 产品Owner与authorization/存储/viewport各原模块Owner负责正式C-01/C-04/C-07映射、宿主Page、可信ACL/资源池/导出目标政策与其实现；总控仅整合共享调度。Replay的消费/显示/导出软件接线已在§10.3/§11.5冻结，本模块实现Owner承担消费编译及运行验证；真实上游端口不可用只阻对应集成资格，不阻Core/离线夹具/自身WPF验证。
6. 消费者/资格Owner提供两消费者BenchmarkProfile真实代表负载与资源/时延目标来源；本模块实现Owner执行§15.2已冻结合成样本计划，以及1920×1080真实WPF/Golden/现场资格：未提供或未执行结果NotEvaluated/TargetPending，不阻按方法准备Core测量，不宣称达标。

## 22. DEV-TST-001 对照取舍

本模块吸收的内容都直接服务于 Replay Core 的可重验输入、确定性执行和恢复测试：ScenarioManifest/canonical hash 防止语义场景漂移；UTC、同 boot monotonic 与 boot ID 防止时间和租约混淆；稳定调度键和 schedule exploration 防止并发顺序依赖；强类型 fault/crash registry 使故障点可枚举、可定位；共同 Contract Test Suite 让生产适配器与确定性模拟适配器验证同一公开语义。

以下内容保持在平台模拟器、设备/数据/协议 Owner 或产品宿主，不复制进 Replay Core：

- PLC、轨道、安全、相机、光源、投影、运动、AI Host、MES、Review/Rework、Supervisor 的模拟器矩阵；它们包含设备动作、协议业务规则和各自状态 Owner。
- 通用 OperationStore、Inbox/Outbox、CAS、权限/签名、跨服务 transport、partner profile 和 wire capture；Replay 只消费已批准的只读证据/执行/结果端口，不成为第二事实或协议 Owner。
- 全平台 Simulation UI、培训数据隔离、Simulation banner、Seek/Inject 命令和 CapacityApproximation；Replay UI 只投影工程回放状态，见 §11/§19.10。
- 全量 HIL/现场 SDK 等价性、光学/运动/投影读回、计量和客户 MES 互操作门禁；Replay 只能报告适配器/证据缺口，不能把模拟通过转为现场资格。

这样不会把模拟器框架整体塞入 Replay，也不更改平台级或共享 Contract；Replay 只定义其 Core 需要的 manifest、时钟、调度、fault、crash 和共同测试边界。

## HALCON 26.05 算子资料入口

回放涉及视觉算子时，使用项目内 [halcon算子手册/operators](../../../halcon算子手册/operators/) 作为目标版本 26.05 的资料入口；算子语义/参数按 §20，全部经 `ImageLibDotNet.cv2` 使用；不重复核验算子存在，只有具体重载/封送歧义才在消费适配器编译核对。

### AOI.Main 软件闭环与回放门

只读复核 [焊盘检测闭环指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-27-m13-pad-inspection-full-closure-design.md)、[线路检测闭环指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-27-m12-trace-inspection-software-closure-design.md) 和 [孔位检测闭环指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-27-m15-hole-inspection-production-closure-design.md) 后，Replay 案例必须把软件行为、真实金样和硬件资格分开记录：

- `SoftwareClosed` 只表示契约、算法路径、UI、资源、性能和软件测试完成；`GoldenDatasetAccepted` 与 `HardwareAccepted` 是独立门，不能由回放通过自动推导。
- 回放输入闭包包含原图/派生图、参考数据、参数、标定、模型、版本和有效域；缺任一必需项进入 `MissingInput`/`NonReproducible`，不能静默加载当前默认值。
- 当前运行的参数、模型或算法发生变化时创建新 attempt，保留旧结果和差异；不在历史记录上原地覆盖“通过”。
- 批量回放区分每项结果和整批状态，取消、资源超限、部分输入和未知保存回执均可见且可查询。

AOI 的制程模块编号、准确率、现场节拍和客户验收值仅是回放消费者的 Profile 候选，不能进入 Replay Core 默认。

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

## 附录 A：Module API Contract v0.3 与逐切片六项定位

本节为§23（附录A），维护当前逐切片六项与接收状态。唯一当前模块契约为正文§3–5、§9.1.1～9.5、§10.1～10.3、§11.2/11.4～11.5、§12.1～12.4、§15.1～15.2；不复制第二份DTO/Schema。Core命名空间Asun.Modules.Replay，测试控制面Asun.Modules.Replay.Testing，可选UI Asun.Modules.Replay.Wpf。正式平台Contract映射不自动进入Core；任何新增字段/操作需先补正文，不从脚本/附录/旧v0.1猜测。主控已将R-Core-Contract及R-Core-Lifecycle的纯托管运行编排、协调、根Owner六项文档规格接收为ModuleCoreImplementationReady，R-Wpf公开装配/恢复指导仅限定内容接收；本轮其余批准模块能力的内部指导准备由本会话自审闭合，见§17.3；不因文档准备或Golden编码一致提升真实实现/产品资格。未授予产品ImplementationSpecificationReady，未执行实际编译、Core/WPF、HALCON、性能或现场验证。

| 切片/真实消费用途 | ①边界/二消费者 | ②唯一API/Owner/单位/错误/版本 | ③独立无UI Host | ④可判定验证 | ⑤性能方法/来源 | ⑥工程/最小顺序/禁止路径 | 准备结论与后续门 |
|---|---|---|---|---|---|---|---|
| R-Core-Contract：预检、目录/闭包/显式变更、值比较、报告分页 | §1–2、§6–7；Regression/CustomerRepro | §3、§4.0–4.2、§9.1、§10；Core Owner、引用schema与精度 | §12.1/12.3两完整Factory组合根，仅BCL端口 | §12.4完整Golden；§13–14，R-C01–04/11–12/15–17/19–20/23–28 | §15/15.1，预算计费/加载/比较/页开销；真实目标待Profile | §12/16唯一Core/Test Exe，禁止其它模块/事实写 | ModuleCoreImplementationReady；主控已接收六项文档规格（0.2.2-prep/API v0.3）。代码开工仍绑定权威可审计基线；未实际实现或编译/运行，不含真实Store/Authority及产品资格 |
| R-Core-Lifecycle：接纳幂等、事件、取消、排空、Unknown/恢复协议 | §1–2、§8两Host共有 | §4–5/4.0–4.2，主体授权/原子Revision/线性化/Store/CAS/lease/回执/generation | §12.1–12.3 Root预留/原Task/hold/Factory/双轴有限cleanup | R-C05–10/18–19/21–30、§12.4/19.6–9/11 | §15取消/资源/尾延迟，端到端至ResourcesReleased另测报告事务 | §12/16同Core/Test，非UI调度 | ModuleCoreImplementationReady（限定纯托管运行编排、协调、Root Owner）；§12.1–12.4六项文档规格已接收。代码基线及实际实现/运行未完成；真实Store/Authority、耐久与worker回收仅阻其适配器用途，不提升真实资源资格 |
| R-Adapter-BCL：严格codec、证据/Graph解析、纯值比较、工程Memory事务 | §10.1/10.1.1；两无UI消费者 | 公开Factory/typed payload/身份/CAS；artifact显式注入，不含native | §10.1最小装配；§12原Root与两Host | R-C33/34及原Golden；真实HALCON另验 | §15.2目录/批次/单文档/页/Store预算 | §16唯一Adapters/Core.Tests，仅Core+BCL | DocumentPreparationComplete；本会话六项定位与自审，普通值/Memory无外部设备依赖；新上下文artifact比较扩展不以原Core接收自动授真实运行资格 |
| R-Simulator：场景/hash/调度/fault共同suite | §9.1～9.5、§22测试专用范围 | 强类型完整manifest/registry/断言，replay-jcs-v2与固定随机算法 | §9.5公开Factory/Control/Runner；§12/16同Test Exe两个Host | R-C12–14/16–18/32，固定闩锁/逻辑时钟；必需未命中失败 | §15.2固定load；§15虚拟顺序与真实性能分开，步骤/资源/观察期限 | §16唯一Test Exe；无Core if(simulation)/生产故障入口 | DocumentPreparationComplete；本会话六项自审，公开装配/执行与断言已闭合，代码基线与实际执行另验。ProcessKill/真实crash另外资格，不拿消息模拟证明耐久 |
| R-AsunImage：原节点复用和工程图像差异适配 | §1/2、§20、两个视觉消费者 | §4 Engine/Capabilities、§10.2公开Factory/manifest/封送、§20域/类型/参数/Owner与失败 | §12同CoreHost注入真实Engine | §14.2 R-C35/§14真实HALCON向量、§20同样本route比较 | §15.2/20.3真实冷热/CPU/GPU/native/复制/排空Profile | §16 AsunImage工程，cv2、禁止内部/直连DLL/设备副作用 | DocumentPreparationComplete；内部软件规格闭合；真实消费节点和证据映射、具体C#歧义编译、真实HALCON样本与Profile门。相对容差路线已在§20.2冻结；专用3D语义由对应稳定结果适配器覆盖，unsupported显式0013不伪实现 |
| R-Store/Worker：隔离持久报告/监督回收 | §2/8/16宿主注入，二Host同回执 | §10.1 typed mutation/§10.3公开Worker/Export与三态；§4.1操作/事件/Case查询、§5/8耐久Owner，不自建平台事务 | §12独立隔离Store/监督器，无产品DB | §9.3、R-C09/14/18/34/36/37，真实断电/进程退出另测 | §15封存IO/资源/排空与Completion时长、Store Profile | §16适配器在replay范围，Core不启动任意进程、不清客户源 | DocumentPreparationComplete；软件端口/恢复已闭合；实际Store耐久与保留访问政策、监督器OS行为及真实crash资格，只阻该用途 |
| R-Wpf：可选工作台与影像/差异联动 | §11两工程角色、只读投影 | §11.2/11.4～11.5控件/Controller/Bridge/权限/实例语言/Unbind/Root参与者 | Core不依UI；§12两个完整Host、§11.4双STA具体构造 | R-C31/38/39及§11.3/11.4/11.5三语/UIA/键盘/双STA/关闭，固定1920×1080真实WPF | §11.3/11.5/15.2单列显示负载/缓存/响应目标来源 | §16 Wpf工程；禁止native句柄/质量写/语言入口重复 | 原限定内容接收保持；本轮含双图的软件指导DocumentPreparationComplete；运行资格PreparationIncomplete。Controller/Bridge/Unbind/双STA与三参数ReplayStaHostLifetime装配已接收；真实Store/Authority/ExportSink/viewport、实际WPF/显示Profile仍按用途验收，不能以Core规格接收声明WPF完成 |
| R-Product-Mapping：消费者制程/平台投影 | §1.2/6/21，宿主负责最终质量/设备动作 | §21 C-01/C-04/C-07只映射、单位/权限/真值外Owner | 复用§12相同Core | 正式消费者Golden/权限/迁移/现场门，Mock不替代 | §15真实消费者Profile | 仅宿主集成，不许本会话改共享文件/客户项目 | PreparationIncomplete；六项在模块局部已有依据，但产品合同/页面/物理值与外部验收未关闭，不授予产品实施准入 |

当前外部门按§21精确限定；本永久会话负责本模块内容自审、修复与定向文档验证，总控仅接收状态/转发依赖，不另审模块内容。本会话不发消息、新建/fork/派生会话或子代理，不修改共享入口、Registry或其它模块；交付仅本指导。跨模块签名改变由对应原Owner修其唯一指导，本会话再定向修受影响消费，不改登记或重开已接收无关片。
