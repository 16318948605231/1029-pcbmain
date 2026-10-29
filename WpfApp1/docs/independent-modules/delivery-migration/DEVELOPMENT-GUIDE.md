# 部署更新与可恢复迁移开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`纯Core, 模拟端口, 双无UI Host`

- 模块：`IM-050 delivery-migration`
- 来源：`PKG-056`；责任分组：`SM-028`
- 版本：`0.1.8-prep`
- 状态：纯 Core、模拟端口与双无 UI Host 文档规格为 `ModuleCoreImplementationReady`（主控于 2026-10-11 接收六项；UI 指定构造内容限定接收，不表示已实现、已集成或生产通过）
- 第二轮场景复审：2026-10-04（仅修订指导，不代表代码/现场验收）
- 运维资料对照复审：2026-10-06（仅吸收 Core 通用缺口，不代表平台/现场验收）
- 测试与发布资料对照复审：2026-10-06（仅补接入验收与证据要求，状态仍为 DesignReview/Prep）
- 怀疑式闭环复审：2026-10-10（补签名、Journal/fence、恢复路线、双 Host 与最小可执行验证；不表示实现或现场通过）
- 主控退修收口：2026-10-11（公开构造、双 Host、到期观察、单次清理及 Resume 权限存续；仅开发准备）
- 主控规格接收：2026-10-11（`0.1.7-prep` 纯 Core/模拟端口/双 Host 六项接收；本轮仅同步状态，不创建工程或启动实现）
- 全范围文档收口：2026-10-12（保留已接收范围，补真实Adapter/codec/凭据/保留政策及UI命令；完整结论见§16.3，由本永久会话自审验证）
- 文档准备结论：当前全部批准能力的可决定软件设计闭合；原Core准入保留，Adapter/UI内容准备与真实代码/运行/现场资格分别记录，见§16.3。
- 规划消费者：机台宿主、独立工程工具、升级服务
- 工程准入：`NewProjectRequired`；未发现契约完全匹配的 Delivery Migration Core。实现切片开始时创建 `src/Modules/delivery-migration/Asun.Modules.DeliveryMigration.Core/`，测试放在 `tests/Modules/delivery-migration/Asun.Modules.DeliveryMigration.Core.Tests/`，namespace 为 `Asun.Modules.DeliveryMigration`。

## Core implementation binding

- 上述工程路径是本模块唯一 Core 写入位置；仅在实现切片获准启动时创建。Supervisor、数据库、备份、设备停机和版本适配器不进入 Core。
- 目标运行时：C# / .NET 10；模块核心不依赖 WPF、DevExpress、AsunImage 或任何制程程序集

- 纯 Core 切片包含操作状态的原子持久化端口、manifest 信任端口、授权端口、迁移处理器登记端口和审计投影端口；它们通过接口注入，不把真实数据库、密钥服务、Supervisor 或设备 SDK 引入 Core。缺少 durable operation store 时，不能声明可恢复执行，只允许纯 validator/model 切片。

本页是脱离 PCB 检测平台仍可接入的唯一实施指导。正式 Contract、Schema、全局错误目录和恢复动作目录由相应 Owner 串行采纳后才成为可编译 API；本页中的 C# 类型是强类型契约候选，用来约束实现和测试，不能绕过 Contract Owner 直接复制为第二套 DTO。

权威关系：本页承接 [PKG-056](../../shared-modules/packages/PKG-056_Delivery.md) 的包边界、[SM-028](../../shared-modules/modules/SM-028_delivery.md) 的版本装配语义和 [DEV-PLT-016](../../shared-modules/guidance/02-platform/DEV-PLT-016_部署、Supervisor与本机隔离开发指导.md) 的 Supervisor/本机隔离约束；Contract/Schema/State/Owner 以 [DEV-CONTRACT-002](../../13-contract-candidates/DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导.md) 和获批原始 Contract 为准。历史 delivery schema（`docs/references/project-snapshots/PCBA-AOI/20260927/original/contracts/v1/schema/`）只用于字段完整性回看，不直接成为本模块 API。AsunControl 只读参考包括 `ClassLibrary/C_XmlConfigManager.cs` 的临时文件+备份保存、`ClassLibrary/C_SQLite.cs` 的事务/备份/恢复和 `Vision_Aligment2D_ShapeModel/ShapeModelEngine.cs` 的目录化模型载荷；这些实现没有被复制或引入依赖。

本轮测试来源为 `H:\docs\40-development\80-quality\自动化测试与发布门禁开发指导.md`，`DEV-TST-002 v2.6`（2026-10-03），SHA-256 为 `a99da05ca578e064674f376788454edd20935d846c06356ba090e5c6da090095`，来源登记见 [H 盘资料清单](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)。只吸收其 §2.1、§5、§13～15 中适用于本模块的真实接入链、替身边界、执行证据和升级恢复验收；故障/资源条款复用本页已有矩阵。AOI 流程、测试平台 Registry/Schema、产品发布门类与签署、硬件资格和 HALCON 24.11 算法内容不采纳为本模块契约。

本轮定向研究只用于冻结可迁移的工程约束：Velopack `0.0.1298`，源码 commit `ed8600eee530a38d2669444b03eb240e56bc5aa3`，MIT，C# 库目标 `netstandard2.0/net462/net6.0/net8.0/net9.0`，依赖含 `NuGet.Versioning 6.14.0`；已读 `src/lib-csharp/UpdateManager.cs`、Windows apply 实现和 `UpdateManagerTests.cs`。可复用强项是包 SHA-256 校验、版本 downgrade 明示开关、测试 locator/fixture 和完整包/增量包测试；局限是 Windows apply 会强停进程、rename 当前目录并可能留下 broken state，默认流程不提供本模块要求的 durable Operation Journal、数据闭包、epoch/fence 或业务 readiness，因此只作为适配器边界和反例，不复制其 updater/installer。对应正文落点为 §3.3/§4/§6/§14，不把安装器副作用带入 Core。

官方依据包括 [.NET 10 `Task.WaitAsync`](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.waitasync?view=net-10.0)（等待截止不等于终止源 Task，落点 §7）、[EF Core applying migrations](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/applying)（生产前检查/测试迁移，回滚可能有数据丢失，落点 §3.3/§14.1）和 [SQLite Online Backup](https://www.sqlite.org/backup.html)（同一连接的一致快照边界，不能替代本模块的对象闭包/独立读回，落点 §3.4/§12）。DevExpress 25.2 官方 `TreeListView` 文档确认层级数据、排序、过滤、摘要和验证能力，落点 §10.1；`DockLayoutManager`、`PropertyGridControl`、`FlyoutControl` 和 `SuperTip` 只作为已安装 25.2.3 程序集的 UI 适配候选，实际编译和 WPF 资格仍是外门。

## 1. 职责与禁止边界

### 1.1 模块职责

模块负责把一个不可变发行包安全地准备、排空、备份、应用、验证、激活和恢复。它只拥有交付操作本身的事实：发行包摘要、操作状态、阶段结果、备份引用、迁移回执和错误诊断。模块必须支持无 UI 调用，适配器由宿主注入。模块负责现有安装的升级、修复和恢复；全新安装/bootstrap 不属于本模块，必须由已批准的宿主安装器建立一个可查询、健康、不可变的当前发布槽后，才能调用本模块。

核心流程固定为：

```text
Validate -> Stage/Verify -> PromoteImmutableRelease -> RemoveQuarantine
         -> Quiesce/Drain -> StopPrevious -> Backup/Verify -> Apply -> Verify
         -> SelectActiveVersion -> StartTarget -> Readiness -> ResumeAdmission
失败时：QueryOriginalAction -> Restore/ForwardRepair（按 §14.1）
      -> SelectCompatibleRelease -> Start+Readiness
      -> ReleaseOperationResources -> ResumeAdmission
```

### 1.2 禁止边界

- 不识别 PCB、PCBA、SPI、AOI、点胶、涂覆或其它制程目标，不拥有缺陷、量测、质量放行、工艺阈值和板件关联。
- 不创建或修改设备命令，不决定运动、触发、光源、相机、PLC 或安全互锁；宿主的设备 Owner 必须先完成停机和安全确认。
- 不拥有产品配方、工单、私有数据库表、ViewModel、页面流程或客户协议；数据迁移由调用方提供已登记的迁移步骤和存储端口。
- 不把进程退出、网络 ACK、文件复制完成或 UI 显示完成当作业务 `Applied`；必须由持久化回执和健康验证证明。
- 不删除未知版本、旧配置、结果证据或用户文件；保留策略由宿主传入，模块只能执行已授权策略。
- 不把数据库不可逆迁移伪装成可回退二进制。没有可验证恢复点时必须拒绝 Apply。
- 不使用隐藏窗口、静态可变全局状态、线程中止、`Environment.FailFast` 或无界重试实现恢复。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.DeliveryMigration.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；迁移是纯数据事务，无 UI、无 HALCON/AsunImage 依赖。

**Blazor/Web**：迁移进度通过 gRPC/REST 查询，浏览器只渲染进度；迁移命令经已授权维护接口，不经浏览器。§1.4 已明确"不把进程退出或文件复制完成当作业务 Applied"——Web 端不得以进度 100% 暗示已成功迁移。

**AI/HALCON 不适用**：本模块是纯数据迁移事务，不执行视觉算法；HALCON 备选 CI 不涉及本模块。

## 2. 角色、所有权和依赖

| 角色 | 权责 |
|---|---|
| Delivery Owner | 创建操作、冻结请求、持有状态和最终回执；同一 `OperationId` 只有一个活跃 Owner |
| Package Provider | 按不可变 `PackageSourceRef` 提供原始 manifest 字节、完整成员清单和成员只读流；不解析/执行迁移，也不拥有应用结果 |
| Package Staging Adapter | 把经签名校验的文件流写入不可执行、独占 ACL 的隔离暂存区，流式计长/hash，封口后逐文件读回；不激活、不执行迁移 |
| Package Release Adapter | 将已封口并读回验证的 quarantine 晋升到不可变版本槽；不改变活动版本指针、不启动进程 |
| Quiesce Adapter | 让宿主停止接收新工作并报告在途任务；不代替设备安全 Owner |
| Storage/Migration Adapter | 在受控事务中备份、迁移、验证、恢复配置/数据；不定义领域字段含义 |
| Supervisor Adapter | 停止、启动、探活进程；不把进程启动成功当作业务激活 |
| Audit/Telemetry Sink | 消费操作存储已提交的耐久事实投影；不能成为第二个状态权威 |
| UI Host（可选） | 展示只读投影和授权命令；不持有状态、不直接写文件/数据库 |

模块仅依赖端口契约、`System.Threading`、Jcs.Net、加密摘要/签名验证和宿主注入的单调时钟；不强制具体数据库、归档容器、安装器、IPC、服务管理器或云服务。唯一操作存储端口负责原子创建、追加状态/事件、CAS 推进及重启查询；审计适配器只接收其耐久投影，不拥有第二份状态。存储可由 SQLite、PostgreSQL 或文件适配，但必须提供原子耐久语义和恢复查询，不能借“通用存储”开放任意 SQL 写入。

## 3. 输入、输出和强类型参数

所有字符串均为 UTF-8，路径为宿主平台的规范化绝对路径；路径只允许落在宿主显式授权的根目录内。金额、坐标、图像和制程单位不属于本模块。

### 3.1 公共类型候选

```csharp
public readonly record struct OperationId(Guid Value);
public readonly record struct ModuleId(string Value);       // [A-Z][A-Z0-9-]{2,63}
public readonly record struct SemVersion(int Major, int Minor, int Patch, string? Prerelease);
public readonly record struct Sha256(string LowerHex64);
public readonly record struct ByteCount(long Value);        // >= 0, bytes
public sealed record PackageSourceRef(string ProviderId, string ArtifactId, string Revision);
public enum PackageMemberKind { RegularFile, Directory, SymbolicLink, HardLink, ReparsePoint, Unsupported }
public sealed record PackageMemberMetadata(string RelativePath, PackageMemberKind Kind,
                                           ByteCount UncompressedLength);

public enum DeliveryMode { Upgrade, Repair }
public enum RollbackMode { SnapshotRestore, ForwardRepair, NotSupported }
public enum QuiesceMode { CloseAdmissionAndDrainAccepted }
public enum UnknownSideEffectPolicy { QueryBeforeRetry, RequireOperator }
public enum ActionQueryStatus { Found, ConfirmedAbsent, Unknown }
public sealed record ActionQuery<T>(ActionQueryStatus Status, T? Receipt, string? Detail)
    where T : class;
public enum DeliveryState
{
    Requested, Validating, Prepared, Quiescing, Quiesced, BackingUp,
    BackupVerified, Applying, Applied, PartiallyApplied, Verifying, Verified, Activating,
    SupervisorStopping, SupervisorStopped, VersionSelecting, VersionSelected,
    SupervisorStarting, SupervisorStarted, ReadinessVerified, Resuming, Resumed,
    Completed, CancelRequested, Draining, Drained,
    ResourcesReleased, Cancelled, RecoveryRequired,
    Recovering, Recovered, RecoveryFailed, Rejected, Failed
}

public sealed record DeliveryLimitProfileRef(string ProfileId, string Revision, Sha256 ContentSha256);
public sealed record DeliveryLimits(
    DeliveryLimitProfileRef Profile,
    TimeSpan MaxQueueWait,
    TimeSpan MaxQuiesce,
    TimeSpan MaxBackup,
    TimeSpan MaxApply,
    TimeSpan MaxVerify,
    TimeSpan MaxActivation,
    TimeSpan MaxRecovery,
    ByteCount MaxPackageBytes,
    ByteCount MaxManifestBytes,
    int MaxManifestDepth,
    ByteCount MinFreeBytes,
    int MaxPackageEntries,
    int MaxDependencyCount,
    int MaxMigrationSteps,
    int MaxRetainedBackups,
    int MaxEventQueue,
    int MaxActiveOperations);

public sealed record DeliveryRequest(
    OperationId OperationId,
    ModuleId Module,
    SemVersion TargetVersion,
    DeliveryMode Mode,
    PackageSourceRef PackageSource,
    CompatibilityPolicy Compatibility,
    QuiesceMode Quiesce,
    DeliveryLimits Limits,
    UnknownSideEffectPolicy UnknownSideEffect,
    string RequestedBy,
    string CorrelationId,
    DateTimeOffset RequestedAtUtc);

public interface IPackageSourcePort
{
    ValueTask<IPackageReadLease> OpenReadAsync(PackageSourceRef source, CancellationToken ct);
}

public interface IPackageReadLease : IAsyncDisposable
{
    // A lease pins one immutable provider revision for its entire lifetime.
    PackageSourceRef Source { get; }
    ValueTask<Stream> OpenManifestAsync(CancellationToken ct);
    IAsyncEnumerable<PackageMemberMetadata> EnumerateMembersAsync(CancellationToken ct);
    ValueTask<Stream> OpenEntryAsync(string exactRelativePath, CancellationToken ct);
}

public sealed record DeliveryOperationSnapshot(OperationId OperationId,
    Sha256 RequestDigest, DeliveryState State, long Sequence,
    long Epoch, string? FenceToken, ExecutionRootLease? RootLease,
    IReadOnlyList<DeliveryEvent> DurableEvents, DeliveryErrorAxes Errors,
    DeliveryResult? Result);
public sealed record DeliveryEvent(OperationId OperationId, long Sequence,
    string EventType, DeliveryState State, DateTimeOffset RecordedAtUtc,
    long Epoch, string? ActionId, string? LocalCode);
public enum DeliveryActionScope { Work, Recovery, Cleanup, Resume, ControlFinalize }
public sealed record DeliveryExecutionContext(OperationId OperationId, string ActionId,
    string RootId, long Epoch, string FenceToken, Sha256 InputDigest,
    DateTimeOffset DeadlineUtc, DeliveryActionScope Scope);
public sealed record ActionIntent(DeliveryExecutionContext Context, string ActionKind,
    string ResourceRootId, IReadOnlyList<string> InputLeaseIds);
public sealed record ActionJournalEntry(OperationId OperationId, string ActionId,
    long JournalSequence, string EventType, Sha256 InputDigest, long Epoch,
    string FenceToken, bool Durable, string? ReceiptHash, string? ErrorCode);
public sealed record DeliveryTransition(OperationId OperationId, long ExpectedSequence,
    DeliveryState ExpectedState, DeliveryState NextState, string Cause,
    DateTimeOffset RecordedAtUtc, string? ActionId);
public sealed record StoreCreateResult(bool Created, DeliveryOperationSnapshot Snapshot);

public interface IDeliveryOperationStore
{
    // Atomic create-by-OperationId: same digest returns the existing snapshot;
    // a different digest returns the existing snapshot for DUPLICATE_OPERATION_ID.
    ValueTask<StoreCreateResult> CreateOrReadAsync(OperationId id, Sha256 requestDigest,
        DeliveryRequest frozenRequest, CancellationToken ct);
    // Append-only CAS. A stale sequence/state never advances the operation.
    ValueTask<DeliveryOperationSnapshot> AppendTransitionAsync(
        DeliveryTransition transition, CancellationToken ct);
    // Every external side effect is first recorded as one immutable intent and then
    // appended with its durable receipt. Same identity/input is idempotent; changed
    // input, epoch or fence is rejected as a stale/conflicting action.
    ValueTask<ActionJournalEntry> BeginActionAsync(ActionIntent intent, CancellationToken ct);
    ValueTask BeginRootLeaseAsync(RootLeaseRequest request, CancellationToken ct);
    ValueTask<ActionJournalEntry> AppendActionOutcomeAsync(ActionJournalEntry outcome, CancellationToken ct);
    ValueTask<DeliveryOperationSnapshot> AppendErrorsAsync(OperationId id,
        long expectedSequence, DeliveryErrorAxes errors, CancellationToken ct);
    IAsyncEnumerable<ActionIntent> ReadIntentsAsync(OperationId id, CancellationToken ct);
    IAsyncEnumerable<ActionJournalEntry> ReadJournalAsync(OperationId id, CancellationToken ct);
    ValueTask<DeliveryOperationSnapshot> CommitResultAsync(OperationId id,
        long expectedSequence, DeliveryResult result, CancellationToken ct);
    ValueTask<DeliveryOperationSnapshot?> ReadAsync(OperationId id, CancellationToken ct);
    ValueTask<DeliveryRequest?> ReadRequestAsync(OperationId id, CancellationToken ct);
    ValueTask<DeliveryOperationDetails?> ReadDetailsAsync(OperationId id, CancellationToken ct);
    ValueTask<DeliveryOperationSnapshot> AppendDetailsAsync(OperationId id,
        long expectedSequence, DeliveryOperationDetails details, CancellationToken ct);
    IAsyncEnumerable<DeliveryOperationSnapshot> ReadIncompleteAsync(CancellationToken ct);
}

public sealed record TrustStoreSnapshot(string Revision, DateTimeOffset EvaluatedAtUtc);
public sealed record TrustedSigningKey(string KeyId, string Algorithm,
    ReadOnlyMemory<byte> SubjectPublicKeyInfo, DateTimeOffset NotBeforeUtc,
    DateTimeOffset NotAfterUtc, string RotationEpoch, bool Revoked);
public interface IManifestTrustPort
{
    ValueTask<TrustStoreSnapshot> CaptureSnapshotAsync(CancellationToken ct);
    ValueTask<TrustedSigningKey?> ResolveKeyAsync(TrustStoreSnapshot snapshot,
        string keyId, CancellationToken ct);
}

public enum DeliveryAction { Prepare, Quiesce, Apply, Cancel, Recover, Cleanup, Resume, RetainOrRemoveRelease }
public sealed record AuthorizationDecision(bool Allowed, string DecisionId,
    string? DenialCode, DateTimeOffset EvaluatedAtUtc);
public interface IDeliveryAuthorizationPort
{
    ValueTask<AuthorizationDecision> AuthorizeAsync(DeliveryRequest request,
        DeliveryAction action, CancellationToken ct);
}

public sealed record RegisteredStepValidation(bool Valid,
    IReadOnlyList<ValidationError> Errors, string RegistryRevision);
public interface IMigrationRegistryPort
{
    // Resolves only pre-registered typed handlers and preconditions; never loads code,
    // SQL, expressions, or commands from a manifest.
    ValueTask<RegisteredStepValidation> ValidatePlanAsync(ModuleId module,
        MigrationPlan plan, CancellationToken ct);
}

public interface IDeliveryAuditPort
{
    ValueTask AppendDurableAsync(DeliveryEvent @event, CancellationToken ct);
}

public sealed record ExecutionRootLease(string RootId, string AuthorizedRoot,
    OperationId OwnerOperationId, long Epoch, string FenceToken,
    ByteCount MaxBytes, DateTimeOffset ExpiresAtUtc, bool Durable);
public sealed record RootLeaseRequest(OperationId OperationId, string RequestedRoot,
    ByteCount MaxBytes, TimeSpan LeaseDuration, string OwnerIdentity,
    string LeaseActionId, Sha256 InputDigest, DateTimeOffset DeadlineUtc);
public interface IExecutionRootRegistryPort
{
    // The registry is the only owner of path roots. It validates that RequestedRoot
    // is inside an authorized root, creates one bounded lease and monotonically
    // advances Epoch. A stale Epoch/FenceToken can never write or clean the root.
    ValueTask<ExecutionRootLease> AcquireAsync(RootLeaseRequest request, CancellationToken ct);
    ValueTask<ActionQuery<ExecutionRootLease>> QueryAcquireAsync(RootLeaseRequest request,
        TimeSpan observationBudget, CancellationToken ct);
    ValueTask<ActionQuery<ExecutionRootLease>> QueryAsync(DeliveryExecutionContext context,
        string rootId, TimeSpan observationBudget, CancellationToken ct);
    ValueTask<QuarantineCleanupReceipt> ReleaseAsync(DeliveryExecutionContext context,
        ExecutionRootLease lease, CancellationToken ct);
    ValueTask<ActionQuery<QuarantineCleanupReceipt>> QueryReleaseAsync(
        DeliveryExecutionContext context, ExecutionRootLease lease,
        TimeSpan observationBudget, CancellationToken ct);
    ValueTask<AuthorityReleaseReceipt> FinalizeAuthorityAsync(
        DeliveryExecutionContext context, ExecutionRootLease lease, CancellationToken ct);
    ValueTask<ActionQuery<AuthorityReleaseReceipt>> QueryAuthorityReleaseAsync(
        DeliveryExecutionContext context, ExecutionRootLease lease,
        TimeSpan observationBudget, CancellationToken ct);
    ValueTask<ExecutionRootLease> AcquireRecoveryAsync(
        DeliveryExecutionContext context, RootLeaseRequest request, CancellationToken ct);
    ValueTask<ActionQuery<ExecutionRootLease>> QueryRecoveryAcquireAsync(
        DeliveryExecutionContext context, RootLeaseRequest request,
        TimeSpan observationBudget, CancellationToken ct);
}

public sealed record AdapterTaskLease(string TaskId, DeliveryExecutionContext Context,
    IReadOnlyList<string> HeldResourceIds, bool SourceInputHeld, bool Completed,
    bool CleanupConfirmed);
public sealed record CleanupErrorInfo(string Code, string SafeState,
    IReadOnlyList<string> OutstandingResourceIds, bool ConfirmationRequired,
    string? HandoffOwner, string? Detail);
public sealed record DeliveryErrorAxes(ErrorInfo? OperationError,
    CleanupErrorInfo? CleanupError);

public interface IPackageStagingPort
{
    // Synchronous, side-effect-free precheck; it never reserves space.
    QuarantineCapacityReport CheckCapacity(ByteCount requiredBytes,
        ByteCount requiredFreeAfterWrite);
    ValueTask<QuarantineCapacityReport> CheckCapacityAsync(ByteCount requiredBytes,
        ByteCount requiredFreeAfterWrite, CancellationToken ct);
    ValueTask<QuarantineStageRef> CreateQuarantineAsync(DeliveryExecutionContext context,
        CancellationToken ct);
    ValueTask<ActionQuery<QuarantineStageRef>> QueryQuarantineAsync(
        DeliveryExecutionContext context, TimeSpan observationBudget, CancellationToken ct);
    ValueTask<ManifestStagingReceipt> WriteAndVerifyManifestAsync(
        DeliveryExecutionContext context, QuarantineStageRef stage,
        ReadOnlyMemory<byte> exactSignedManifestBytes, Sha256 rawManifestSha256,
        CancellationToken ct);
    ValueTask<PackageEntryReceipt> WriteAndVerifyEntryAsync(DeliveryExecutionContext context,
        QuarantineStageRef stage,
        string relativePath, Stream content, ByteCount expectedLength, Sha256 expectedSha256,
        CancellationToken ct);
    ValueTask<ActionQuery<ManifestStagingReceipt>> QueryManifestAsync(
        DeliveryExecutionContext context, QuarantineStageRef stage,
        TimeSpan observationBudget, CancellationToken ct);
    ValueTask<ActionQuery<PackageEntryReceipt>> QueryEntryAsync(
        DeliveryExecutionContext context, QuarantineStageRef stage, string exactRelativePath,
        TimeSpan observationBudget, CancellationToken ct);
    ValueTask<StagingReceipt> SealAndReadbackAsync(DeliveryExecutionContext context,
        QuarantineStageRef stage,
        Sha256 manifestSha256, int expectedEntryCount, CancellationToken ct);
    ValueTask<ActionQuery<StagingReceipt>> QuerySealAsync(DeliveryExecutionContext context,
        QuarantineStageRef stage, TimeSpan observationBudget, CancellationToken ct);
    ValueTask<QuarantineCleanupReceipt> AbandonAsync(DeliveryExecutionContext context,
        QuarantineStageRef stage, CancellationToken ct);
    ValueTask<ActionQuery<QuarantineCleanupReceipt>> QueryAbandonAsync(
        DeliveryExecutionContext context, QuarantineStageRef stage,
        TimeSpan observationBudget, CancellationToken ct);
}

public interface IPackageReleaseAdapter
{
    ValueTask<ReleaseSlotReceipt> PromoteAsync(DeliveryExecutionContext context,
        QuarantineStageRef stage,
        StagingReceipt verifiedStage, ModuleId module, SemVersion version, Sha256 manifestSha256,
        CancellationToken ct);
    ValueTask<ActionQuery<ReleaseSlotReceipt>> QueryPromotionAsync(
        DeliveryExecutionContext context, ModuleId module, SemVersion version,
        Sha256 manifestSha256, TimeSpan observationBudget, CancellationToken ct);
}

public interface IActiveReleaseAdapter
{
    ValueTask<ReleaseSelectionReceipt> SelectAsync(DeliveryExecutionContext context,
        long expectedRevision,
        ReleaseSlotReceipt target, CancellationToken ct);
    ValueTask<ActiveReleaseSnapshot> QueryCurrentAsync(DeliveryExecutionContext context,
        ModuleId module, TimeSpan observationBudget, CancellationToken ct);
    ValueTask<ActionQuery<ReleaseSelectionReceipt>> QuerySelectionAsync(
        DeliveryExecutionContext context, Sha256 targetManifestSha256,
        TimeSpan observationBudget, CancellationToken ct);
}

// Found carries the durable action receipt; ConfirmedAbsent means the adapter's
// authoritative record proves no effect; Unknown means neither conclusion is safe.

public sealed record QuarantineStageRef(string Value);
public sealed record QuarantineCapacityReport(ByteCount AvailableBytes,
    ByteCount RequiredBytes, ByteCount RequiredFreeAfterWrite, bool Sufficient);
public sealed record ManifestStagingReceipt(ByteCount BytesWritten,
    Sha256 RawManifestSha256, bool Durable, bool ReadbackVerified);
public sealed record PackageEntryReceipt(string RelativePath, ByteCount BytesWritten,
                                         Sha256 ContentSha256, bool Durable);
public sealed record StagingReceipt(string StagingId, Sha256 ManifestSha256,
    Sha256 RawManifestSha256, ByteCount TotalEntryBytes, int EntryCount,
    bool ManifestReadbackVerified, bool EntriesReadbackVerified, bool Sealed);
public sealed record QuarantineCleanupReceipt(bool Removed, bool NoOpenHandles,
                                               string? Detail);
public sealed record AuthorityReleaseReceipt(bool Released, long Epoch,
    string RootId, string? Detail);
public sealed record ReleaseSlotReceipt(string ReleaseSlotId, ModuleId Module,
    SemVersion Version, Sha256 ManifestSha256, bool ContentReadbackVerified, bool Durable);
public sealed record ActiveReleaseSnapshot(ReleaseSlotReceipt? CurrentRelease, long Revision);
public sealed record ReleaseSelectionReceipt(bool Selected, bool Durable,
    ActiveReleaseSnapshot Current, string? Detail);
```

### 3.2 参数范围、单位和资源限制

除取得初始 fence 的 `AcquireAsync(RootLeaseRequest, ...)` 外，外部动作端口均显式带 `DeliveryExecutionContext`；每个 Action 拥有独立且冻结的 ActionId、InputDigest、Scope 和 deadline，同一操作共享 OperationId/RootId/epoch/fence，不共享一份跨动作 context。副作用查询复用该动作的原 context，另传正且有限的 `observationBudget`；工作截止到期不禁止只读查询历史回执，也不延长原动作。根取得应答丢失用原 `RootLeaseRequest` 查询，不能换 LeaseActionId 再占根。无副作用的容量预检、包源读取、TrustStore 和权威 Store 的操作级读取不伪造 Action 身份。详见 §6.1～§6.3。


`DeliveryLimits` 是必填、不可变的运行限制快照，必须引用宿主已批准的 `DeliveryLimitProfileRef`；引用、完整数值和 Profile 内容 hash 一并纳入 `RequestDigest`。本模块不设置跨客户通用的停机时限、包大小、磁盘余量、队列、备份保留或并发默认值。没有当前部署批准的 Profile 时，验证只可用于显式离线诊断，`ExecuteAsync` 必须拒绝，不得退回文档中的示例数值。限额是准入/资源保护约束，不是性能目标；性能目标和通过条件仍由 `BenchmarkProfile` 的来源决定。

Core 对表示域和内部一致性作固定校验：期限必须是正且有限的 `TimeSpan`；包、manifest、entry、migration step、event queue 和 active operation 的上限必须为正；dependency count 和最小剩余空间不得为负；备份保留至少覆盖当前活动恢复点；manifest 深度不得超过实际固定解析器支持的深度。实测字节、成员数、嵌套层数、并发数或阶段耗时超过快照即停止接纳/继续，返回对应错误并保持隔离；禁止用无界缓冲、整数溢出、静默截断或重置 deadline 绕过限制。`MaxPackageBytes` 只约束解压后的文件总字节，manifest 单独受 `MaxManifestBytes` 约束。

`DateTimeOffset` 只用于审计/业务时刻；期限使用注入的单调 `TimeProvider` 计算。禁止以墙上时钟回拨延长操作，也禁止把进程重启当作新操作而重置预算。请求者和关联 ID 按宿主批准的身份/追踪 Profile 校验，本模块不另设客户通用字符数上限。

SemVersion采用[SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)顺序的受限表示：Major/Minor/Patch为0..Int32.MaxValue整数，文本三段必填且无前导零；Prerelease为null或点分隔的非空ASCII字母/数字/连字符标识，纯数字标识禁止前导零。先比较三整数，正式版高于同三段预发行版；预发行标识逐段，纯数字按无溢出十进制整数比较、数字低于非数字、非数字ordinal比较，相同前缀较短列表低。现公开类型无build metadata字段，因此拒绝`+metadata`，不能偷偷忽略而产生同identity不同包。依赖区间固定`Minimum≤version<Maximum`（Maximum=null无上限），同时匹配精确manifestSha256；边界相等/倒置/多匹配拒绝，不能选最近版本。依赖闭包按moduleId ordinal遍历、同模块不同hash或循环拒绝，不把两版同模块加载为隐式回退。Guid.Empty、非64位小写hex摘要、ModuleId不符合声明正则均纯结构校验拒绝。

### 3.3 发行包和迁移计划

读取 manifest 必须拒绝 UTF-8 BOM、无效 UTF-8 和超出 `MaxManifestBytes` 的输入；只在字节数受限后解码，不以外部声明的长度分配缓冲区。`MaxManifestDepth` 限制 JSON 容器实际嵌套层数，不能只依赖解析器默认深度。`MaxPackageBytes` 是所有 manifest `entries` 的声明/实测未压缩文件字节总和上限（manifest 单独受 `MaxManifestBytes` 限制）；文件数上限只计清单中的常规文件。Provider 必须把 `PackageSourceRef` 固定到不可变 revision，并在一个 `IPackageReadLease` 生命周期内返回同一内容快照；manifest 外的成员、缺失成员、重复成员、非 `RegularFile` 成员和不匹配的目录清单均拒绝。

必须保留收到的原始 signed manifest 字节快照和其 raw SHA-256，并把同一字节写入 quarantine 的保留 manifest 文件；JCS `manifestSha256` 是 PayloadProjection 摘要，不是原始文件字节摘要。Manifest 和所有内容文件都要由 `StagingReceipt` 的读回事实覆盖，发布槽也必须保留原始 manifest 以供离线审计和历史验证。manifest 字节缓冲受 `MaxManifestBytes` 硬上限约束，禁止接受后再规范化或重新序列化来替换原签名字节。

```csharp
public sealed record PackageManifest(
    string ManifestSchemaVersion,       // semver; 当前候选 1.0.0
    string CanonicalizationRule,         // 首发必须是 delivery-manifest-jcs-v1
    ModuleId Module,
    SemVersion Version,
    string RuntimeFamily,               // 例：dotnet10-windows-x64
    IReadOnlyList<PackageEntry> Entries,
    IReadOnlyList<DependencyPin> Dependencies,
    Sha256 ManifestSha256,
    SignatureInfo Signature,
    MigrationPlan Migration);

public sealed record PackageEntry(string RelativePath, ByteCount Length, Sha256 Sha256,
                                  string ContentRole); // binary/config/schema/migration/resource
public sealed record DependencyPin(ModuleId Module, SemVersion Minimum, SemVersion? Maximum,
                                   Sha256 ManifestSha256);
public sealed record SignatureInfo(string Algorithm, string KeyId, string SignatureBase64);
public sealed record MigrationPlan(SemVersion From, SemVersion To,
                                   IReadOnlyList<MigrationStep> Steps,
                                   RollbackMode Rollback,
                                   bool RequiresProcessRestart);
public sealed record MigrationStep(string StepId, int Ordinal, string SchemaId,
                                   bool Idempotent, MigrationSafety Safety,
                                   string PreconditionId, string ForwardHandlerId,
                                   string? ReverseHandlerId,
                                   Sha256? RollbackArtifactSha256);
public enum MigrationSafety { Reversible, ExpandContractCompatible, Irreversible }
public sealed record CompatibilityPolicy(SemVersion Reader, SemVersion DataSchema,
                                         bool PreserveHistoricalRead,
                                         bool AllowForwardRepair);
```

首发 manifest 摘要/签名投影规则固定为 `delivery-manifest-jcs-v1`，按 [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) 生成严格 UTF-8 canonical JSON（无 BOM、无 token 空白、无末尾换行）。唯一 JCS 实现依赖为 [Jcs.Net 0.1.1](https://www.nuget.org/packages/Jcs.Net/0.1.1)，MIT；NuGet 包 SHA-256 为 `64771fae5544922f9958d4618bbca014dfe2e05d3f6ffe8123471d798fa0554`，上游源码固定到 [`IsraelIyonsi/Jcs.NET` commit `8aff61685300d5d94b81f05246f95d4681e7178a`](https://github.com/IsraelIyonsi/Jcs.NET/tree/8aff61685300d5d94b81f05246f95d4681e7178a)，它是本模块的运行时依赖，MIT 原件位于上游 `LICENSE`。已检查 `JsonCanonicalizer.cs`、`EcmaScriptNumberFormatter.cs`、字符串/重复键校验器及相应测试；固定 commit 的 `dotnet test Jcs.Net.sln --configuration Release` 结果为 194/194 通过。该源码/测试是 RFC 算法的可追溯实现依据，不代替本模块对签名 manifest 的自身契约测试。调用时固定 `JsonCanonicalizer.CanonicalizeToUtf8(string)`，不得实现第二套 JCS、调用 `JsonElement` 重载、替换版本或自行修补格式化器；后续升级必须重新核对 RFC 8785 官方向量、上游实现/测试、包 hash 和本模块兼容性后修改本指导。

输入首先以严格 UTF-8 解码并由 JCS 字符串入口拒绝重复属性名、未配对代理项及超出 IEEE-754 binary64 范围的数值，再按冻结的 Manifest Schema 拒绝未知字段、缺项和深度/字节预算超限。完整外部 manifest 的根字段固定为上述 8 个 Payload 字段加 `manifestSha256` 和 `signature`；`signature` 仅含 `algorithm`、`keyId`、`signatureBase64`。类型化模型使用封闭映射序列化为投影 JSON；每个外部 JSON 字段名使用显式 `JsonPropertyName`，不依赖默认命名、反射顺序、当前区域性或调用方可变 `JsonSerializerOptions`。Payload 字段集合固定为 `manifestSchemaVersion`、`canonicalizationRule`、`moduleId`、`version`、`runtimeFamily`、`entries`、`dependencies`、`migration`；对象属性次序一律由 RFC 8785 JCS 规则确定，不得由字段声明顺序或输入文本顺序覆盖。`moduleId` 为稳定字符串，`version`/迁移版本为 SemVer 字符串。entry 的字段固定为 `relativePath`、`length`、`sha256`、`contentRole`；dependency 固定为 `moduleId`、`minimumVersion`、`maximumVersion`、`manifestSha256`；migration 固定为 `fromVersion`、`toVersion`、`steps`、`rollbackMode`、`requiresProcessRestart`；step 固定为 `stepId`、`ordinal`、`schemaId`、`idempotent`、`safety`、`preconditionId`、`forwardHandlerId`、`reverseHandlerId`、`rollbackArtifactSha256`。所有枚举值使用本指导列出的固定 ASCII 名称；缺省可选字段统一显式写入 `null`，禁止省略/补 null 两种编码并存。Manifest v1 不定义小数；所有 JSON 数值只能是 `ordinal` 或字节长度这类有上界整数，范围为 0..2^53−1，超界值拒绝，其他大整数必须以 Schema 明确规定的十进制字符串表示。

投影前对路径做**校验而非静默规范化**：manifest 与包目录项的相对路径必须已经是 NFC、只使用 `/` 分隔且逐字节一致；否则拒绝并要求发行方重建并重新签名。禁止空段、`.`/`..`、绝对/UNC/盘符路径、反斜线、冒号、控制字符、Windows 保留设备名、尾随点/空格、ADS、符号链接/硬链接/重解析点以及 `OrdinalIgnoreCase` 下的文件/目录碰撞。先逐条验证路径语法、再检查文件与隐含父目录冲突、最后在不可被其他主体写入的 staging 根内逐文件创建新文件；对每级父目录和最终文件拒绝 reparse point，禁止覆盖既有文件。`entries` 依已验证 `relativePath` 的 UTF-16 ordinal 顺序排序，`dependencies` 依 `moduleId` ordinal 排序，`migration.steps` 按连续 `ordinal=0..N-1` 保序；以上集合键重复即拒绝，任何有序列表保留原序。对 PayloadProjection 的 JCS 字节计算 SHA-256，写入小写 64 位十六进制 `manifestSha256`。文件条目另对解压后原始文件字节流计算 SHA-256，并同时校验声明长度；两种摘要不得混用。解压采用流式读取，逐文件与总量均受 `DeliveryLimits` 限制，不得按归档声明一次性分配内存或跟随链接写出 staging 根。

签名输入固定为第二个 JCS 对象，其 JSON 键精确为 `domain`、`canonicalizationRule`、`keyId`、`manifestSha256`、`signatureAlgorithm`；值分别为 ASCII 常量 `asun-delivery-manifest-signature-v1`、规则 ID、KeyId、已校验的小写 manifest 摘要和算法名。签名字段自身不进入签名投影，避免循环；完整认证覆盖由 manifest 摘要、算法、KeyId 和规则 ID共同决定，不能只验文件摘要。首发仅支持 `RSA-PSS-SHA256`，验证 API 固定使用 [.NET 10 `RSA.VerifyData`](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.rsa.verifydata?view=net-10.0) 与 [`RSASignaturePadding.Pss`](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.rsasignaturepadding.pss?view=net-10.0)；PSS 盐长度采用 SHA-256 摘要长度。受信 RSA 公钥模数为 3072..8192 位并要求 SHA-256 长度盐（对应至少 NIST SP 800-57 约 128-bit 经典安全强度）；私钥只存在隔离的发行签名器/HSM，不进入 Core、客户机或模块配置。KeyId 通过宿主注入的不可变 TrustStore 快照解析，未知、停用、过期或签名无效均拒绝。验证开始时固定 `TrustStoreSnapshot.Revision`、KeyId、KeyNotBefore/NotAfter、`RotationEpoch` 和撤销观察点并写入 Journal；轮换期间不得把同一签名包改签、换 KeyId 或用“当前最新钥匙”重新解释。若策略在 Apply 前要求重新确认，必须在原 OperationId 下以新 Journal 事件确认同一 KeyId 仍获准；撤销或观察点不可确认时保持隔离/`RecoveryRequired`。`signatureBase64` 采用标准 padded Base64，禁止空白和非规范等价编码；解码后必须重新编码并与原文本逐字符相等，签名长度须与公钥模数长度一致。不得在同一 manifest 版本隐式降级到 PKCS#1 v1.5、ECDSA、裸 hash 或“只验文件摘要”；未来更换算法须发布新的 canonicalization/manifest 兼容版本和独立验证器，旧包仍由其原始规则验证。公钥信任根、有效期、吊销和轮换时刻由安全部署 Profile 提供，是集成门而不改变首发 Core 算法。依据：[RFC 8017](https://www.rfc-editor.org/rfc/rfc8017)、[NIST SP 800-57 Part 1 Rev. 5](https://csrc.nist.gov/pubs/sp/800-57/r5/final)。

最小 Golden 不能只写字段名或“hash 正确”。以下五个测试向量的文本就是完整 UTF-8 无 BOM、无末尾换行的规范字节；实现必须按对象字段的 JCS 规则独立拼接后得到相同 SHA-256（`signature` 仍需用测试密钥实际验证签名，下面只固定签名输入摘要）：

| 向量 | 规范字节（JSON 文本） | SHA-256 |
|---|---|---|
| SignatureInput | `{"canonicalizationRule":"delivery-manifest-jcs-v1","domain":"asun-delivery-manifest-signature-v1","keyId":"golden-key-01","manifestSha256":"0000000000000000000000000000000000000000000000000000000000000000","signatureAlgorithm":"RSA-PSS-SHA256"}` | `a0db9a37d00a9e1acedd19ce563441231ae1988d80a034b6f3870ede42551798` |
| PackageEntry | `{"contentRole":"binary","length":3,"relativePath":"app/Host.exe","sha256":"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"}` | `048ab9b758ca0940332d43e86e7703719f39c2e6096052412150aa8a0c911460` |
| MigrationPlan | `{"fromVersion":"1.0.0","requiresProcessRestart":true,"rollbackMode":"SnapshotRestore","steps":[{"forwardHandlerId":"schema.expand.v1","idempotent":true,"ordinal":0,"preconditionId":"schema.at.1.0.0","reverseHandlerId":"schema.reverse.v1","rollbackArtifactSha256":"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad","safety":"Reversible","schemaId":"schema-v1","stepId":"expand"}],"toVersion":"1.1.0"}` | `6e904441cf99ced7a93d558351fdb9fa400fa676397224d545dac3672ea44875` |
| ActionIntent | `{"actionKind":"Apply","context":{"actionId":"act-golden-01","deadlineUtc":"2026-10-11T00:00:01Z","epoch":7,"fenceToken":"fence-golden-07","inputDigest":"0000000000000000000000000000000000000000000000000000000000000000","operationId":"00000000-0000-0000-0000-000000000001","rootId":"root-golden","scope":"Work"},"inputLeaseIds":["input-golden-01"],"resourceRootId":"root-golden"}` | `36562704754f063aac8e7056de57df37d48200a23987624594afd8d5a1f061d0` |
| PayloadProjection | `{"canonicalizationRule":"delivery-manifest-jcs-v1","dependencies":[],"entries":[{"contentRole":"binary","length":3,"relativePath":"app/Host.exe","sha256":"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},{"contentRole":"migration","length":3,"relativePath":"rollback/schema.bin","sha256":"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"}],"manifestSchemaVersion":"1.0.0","migration":{"fromVersion":"1.0.0","requiresProcessRestart":true,"rollbackMode":"SnapshotRestore","steps":[{"forwardHandlerId":"schema.expand.v1","idempotent":true,"ordinal":0,"preconditionId":"schema.at.1.0.0","reverseHandlerId":"schema.reverse.v1","rollbackArtifactSha256":"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad","safety":"Reversible","schemaId":"schema-v1","stepId":"expand"}],"toVersion":"1.1.0"},"moduleId":"DELIVERY-TEST","runtimeFamily":"dotnet10-windows-x64","version":"1.1.0"}` | `6bbcc00420c147e3fbd837999cda6a6611be49562e8211481fbb2fda0512d832` |

这些是契约/测试向量，不是生产密钥、客户包或性能结果；ActionIntent 的全零InputDigest只验证identity编码，不代表可执行Apply输入。ActionIntent序列化键按表完整映射（context为嵌套对象，operationId小写Guid D格式，Scope为固定ASCII，deadlineUtc为UTC `yyyy-MM-ddTHH:mm:ssZ`，存在小数时固定7位小数）；InputLeaseIds按ordinal排序、重复拒绝，ResourceRootId必须等于context.RootId。字段增删、数组顺序、转义、Unicode规范化、布尔/整数类型变化须改变字节；完整intent冻结后改动即拒绝。包路径仍按校验而非修正处理；归档解压、复制、跨卷晋升及对应清理携带原操作登记的ExecutionRootLease，不把lease变更当成同一action重发。

`signature` 是强制字段，没有 unsigned/可选签名模式，也不存在关闭签名验证的 CompatibilityPolicy 开关。`preconditionId`、`forwardHandlerId`、`reverseHandlerId` 是宿主预先登记并受信任的规则/处理器 ID，不是脚本、命令行、SQL、表达式或可动态加载代码。每个 ID 必须绑定获批的 `moduleId`、源/目标 Schema 版本及强类型参数 Schema；处理器仅由宿主允许列表解析。未知 ID、未绑定 Schema、请求外副作用或不兼容回退策略均在创建 staging/排空前拒绝。manifest 文本不作为指令执行。

迁移安全性必须按步骤显式表达：`Reversible` 要求 `RollbackArtifactSha256` 和已验证的逆向前置条件；`ExpandContractCompatible` 要求旧 reader 在 expand/contract 完成前仍能读取已提交数据，健康失败时可保持旧版本；`Irreversible` 必须没有回退 artifact，失败只能进入 `RecoveryRequired/ManualRecovery` 或执行已批准的 `ForwardRepair`。布尔“可回退”不能替代这三种语义，不能因为存在一个脚本字符串就声称可逆。

上述投影规则解决 manifest 载荷的确定性摘要与签名输入，不定义迁移 Schema 中的领域含义。固定的 Prepare 顺序为：先校验请求与所有资源上限；打开并固定 `PackageSourceRef` 快照；有界读取 manifest；严格解码、Schema 校验并计算 PayloadProjection JCS 摘要；校验签名与 TrustStore；校验所有 entry 路径、完整成员集合、依赖版本、目标运行时、处理器 allowlist、当前环境、权限和迁移前置条件；随后逐个流读源文件，验证实测长度和 SHA-256，但不写 staging；容量预检通过后才创建 quarantine；第二遍从同一只读快照把文件流写入 quarantine，并再次逐流计长/hash；最后封口并逐文件读回核验。第一次完整源读取发现不匹配时，不创建 staging；第二遍读取或封口期间若源失效/变化，立即停止，隔离 quarantine、尝试清理并禁止晋升版本。只有上述检查全部成功才生成 `StagingReceipt`。quarantine 对宿主其他主体不可枚举/执行，且没有任何活动版本入口；其 opaque ref 不得暴露可执行路径。容量预检是无副作用探测而非空间预留，写入中仍可能磁盘耗尽，此时按暂存失败恢复语义处理。

验证签名、载荷摘要、逐文件摘要、依赖版本和目标运行时必须全部先于 staging 创建。任何验证失败都不创建 staging、不关闭接纳、不排空，也不调用迁移/备份写入适配器。只有开始 staging 后发生的复制、落盘或读回失败，才允许存在 quarantine；这类失败不得晋升/激活版本，必须按原操作收回 staging。若清理回执未知或仍有打开句柄，状态保持隔离并进入 `RecoveryRequired`，不得伪装为普通 `Rejected` 或释放占用资源。manifest 中的迁移步骤是数据变更声明，不是模块自行解释的业务规则；未知 `SchemaId`、重复 `StepId`、ordinal 间隙或不可满足的 precondition 必须拒绝。

验证完毕的 quarantine 仍不是可运行版本。`IPackageReleaseAdapter.PromoteAsync` 必须将封口且读回验证的 quarantine 复制/原子移入以 `ModuleId + SemVersion + manifestSha256` 唯一标识的不可变版本槽，验证所有文件 hash 后返回耐久 `ReleaseSlotReceipt`；同键同 hash 重试幂等，同键不同 hash 拒绝，且此调用不能改变活动版本。跨卷复制必须再次逐文件验证，且只有完整版本槽可被 supervisor 定位。发布槽未就绪不得 quiesce 或 apply。未引用的完整版本槽按独立保留策略回收，不在本次失败清理中盲删。

### 3.4 输出和回执

```csharp
public sealed record DeliveryResult(
    OperationId OperationId,
    DeliveryState TerminalState,
    bool Activated,
    bool HistoricalDataReadable,
    BackupReference? RecoveryPoint,
    IReadOnlyList<StepReceipt> Steps,
    DeliveryErrorAxes Errors,
    DateTimeOffset CompletedAtUtc);

public sealed record ValidationReport(bool IsValid, IReadOnlyList<ValidationError> Errors);
public sealed record ValidationError(string Code, string Path, string Message);
public sealed record ReadbackReport(bool HistoricalDataReadable, IReadOnlyList<string> Diagnostics);
public sealed record HealthReport(bool Ready, string Version, Sha256 ManifestSha256,
                                  ReadinessEvidence Evidence,
                                  IReadOnlyList<string> Checks);
public sealed record ReadinessEvidence(
    ModuleId Module,
    string ReleaseSlotId,
    Sha256 TargetManifestSha256,
    string ContractMajor,
    Sha256 CapabilityFingerprint,
    string PolicyProfileId,
    Sha256 PolicyProfileSha256,
    string PerformanceProfileId,
    Sha256 PerformanceProfileSha256,
    string MachineBootId,
    string TimingEpoch,
    IReadOnlyList<ReadinessSample> ConsecutiveSamples,
    DateTimeOffset ExpiresAtUtc);
public sealed record ReadinessSample(string CheckId, long Ordinal, bool Healthy,
    string SourceVersion, Sha256 EvidenceSha256,
    long ObservedStartMonotonicNs, long ObservedEndMonotonicNs);
public sealed record QuiesceReceipt(bool Accepted, int InFlightCount, string? Detail);
public sealed record DrainReceipt(bool Drained, int RemainingCount, string? Detail);
public sealed record RecoveryReceipt(RollbackMode Strategy, bool Succeeded,
    bool Durable, string? BackupId, string? Detail);

public sealed record BackupReference(string BackupId, Sha256 ContentSha256,
                                     ByteCount Size, DateTimeOffset CreatedAtUtc,
                                     string RestoreScope,
                                     BackupClosureManifest Closure,
                                     BackupVerification Verification);
public sealed record BackupClosureManifest(
    string SourceCheckpointId,
    Sha256 SourceReleaseManifestSha256,
    IReadOnlyList<BackupObjectReference> Objects,
    Sha256 ObjectSetSha256,
    string KeyEpoch,
    bool Approved);
public sealed record BackupObjectReference(string ObjectId, string SourceKind,
                                           Sha256 ContentSha256, ByteCount Length,
                                           string SourceRevision);
public sealed record BackupVerification(bool IndependentReadback,
    bool IsolatedRestoreDrill, bool Restorable,
    string? IsolationRootId, string? DrillReceiptId,
    string? RpoObservation, string? RtoObservation);
public sealed record StepReceipt(string StepId, string Outcome, bool Durable,
                                 string? BeforeHash, string? AfterHash);
public sealed record ErrorInfo(string LocalCode, string GlobalCode, string SafeState,
                               bool Retryable, string RecoveryActionId, string Detail);
```

`DeliveryResult` 只表示终态回执，其 `TerminalState` 必须是 `Completed`、`Recovered`、`Cancelled`、`Rejected` 或 `Failed`，并且只能在该终态耐久提交后存在于 `DeliveryOperationSnapshot.Result`。执行进行中、排空中、`RecoveryRequired` 或 `RecoveryFailed` 时，API 返回当前 `DeliveryOperationSnapshot` 且 `Result=null`；它们不能带 `CompletedAtUtc`、不能被称为 Final/Completed，也不能将 `Activated`/历史可读字段默认解释为 false。`RecoveryRequired` 表示外部动作结果未知或恢复尚未安全完成；`RecoveryFailed` 表示某次恢复动作已得到耐久、确定的失败回执，但宿主仍隔离且原操作仍可由新的获批恢复动作继续。未知回执不得标成 `RecoveryFailed`。`Activated=true` 只允许在新版本 readiness、迁移读回和回执持久化均成功后返回。`HistoricalDataReadable=false` 是明确终态事实，不能以空列表代替。任何未知副作用都使 Snapshot 保持 `RecoveryRequired`；不能返回成功或自动再执行。

`DeliveryErrorAxes` 必须分开表达业务/操作结果和清理结果：`OperationError` 说明哪一步、哪个 action 和哪个输入失败；`CleanupError` 说明仍持有的 root/lease/handle/task/订阅、是否需要确认移交和下一责任 Owner。清理未知时不能把业务错误降级为普通 `Failed`，也不能用“进程已退出”推断资源已释放；只有独立 cleanup receipt 确认所有资源归还后，才可提交对应终态。清理责任移交必须携带原 `OperationId`、原 `ActionId`、Epoch/FenceToken、资源 ID、最后一个 Journal 序号和联系人/Owner，宿主确认后仍不得覆盖原操作历史。

备份清单不是可恢复事实。`BackupClosureManifest` 必须绑定源发布 manifest、冻结 checkpoint、对象集合摘要、对象来源修订、密钥代次和批准状态；对象集合至少覆盖已提交配置/Schema、数据库快照及其 WAL 或等价提交边界、已登记 CAS/文件对象、审计封存引用和恢复所需的迁移/版本元数据。未提交草稿、无法枚举的隐式目录、只存在于日志中的对象和未登记的外部路径不得被默认为闭包成员。备份适配器按以下顺序执行：`Reserve -> FreezeCheckpoint -> EnumerateAuthoritativeClosure -> CopyAndHash -> Flush -> IndependentReadback -> IsolatedRestoreDrill -> SignOrPersistReceipt -> Publish`。任一对象缺失、长度/hash 不匹配、checkpoint/WAL 不可重放、隔离目录权限不满足、只读查询或回放烟测失败时，`Restorable=false`，不能仅因文件存在或 `BackupManifest` 已签名而继续 Apply。

隔离恢复必须使用独立根和最小凭据，不覆盖活动槽或生产数据；验证每个对象、数据库/提交边界、历史查询、引用闭包、迁移兼容性和清理回执。`RpoObservation` 和 `RtoObservation` 只有在已批准 Profile 定义事故切点、起止事件、单位和测量后才可填写；缺少批准 Profile 时保留 `NotEvaluated`，不捏造阈值。生产切换仍需在排空、停写、授权和活动指针 CAS 后单独执行。

### 3.5 请求校验和空值语义

`PackageManifest.Entries`、`Dependencies` 和 `Migration.Steps` 不能为 `null`。空发行包、缺少当前版本、空模块 ID、全空白路径、零长度 manifest 和只有备注没有可执行内容的请求都不是“无操作成功”，而是 `INVALID_REQUEST`。`Upgrade` 必须含至少一个 migration step；`Repair` 可含零个 step，但必须有至少一个经过摘要验证的可替换条目，且签名manifest必须From=To、无迁移steps，修复意图由请求Mode明确，不能读取并不存在的manifest mode字段。恢复不是 `DeliveryMode`；`RecoverAsync` 必须通过 `RecoveryCommand` 携带已验证的 `BackupId` 或指定可查询的原操作，不能以空备份引用触发“尽力恢复”。

同步`Validate(request)`只校验已传入值的结构、有效域、Limits与兼容策略内部一致性，不访问包/Trust/Store/环境/权限，不声称预检已通过。`ExecuteAsync`的异步验证顺序固定为：请求结构与范围 → 资源上限/路径根 → manifest字节长度和摘要 → 签名/密钥有效期 → 依赖闭包和版本区间 → step ID/ordinal/前置条件/回退能力 → 当前环境版本和持久状态 → 权限。任一步失败都不创建staging、不排空或写业务存储；已接纳操作的Store/Registry元数据仍按原身份收敛，错误进入Snapshot。版本区间/目标含义不明确返回AMBIGUOUS_COMPATIBILITY，不选择最近版本。无UI工具只调用Validate/Query时只能得到结构诊断/历史事实，不能把它当成真实包dry-run。

当前环境检查必须查询唯一活动发布记录，并确认其 revision、模块、版本、manifest hash、完整发布槽读回状态与运行进程 readiness 一致；记录结果及 revision 写入持久 Operation Snapshot，后续激活使用该 revision 做 CAS。当前槽缺失、未知、内容验证失败、进程未就绪或目标 migration `From` 与当前数据/Schema 不匹配时拒绝，不进入 Quiesce。首装不经本模块；不得以空当前槽的期望 revision 作为升级。

## 4. 状态、Owner 和状态转换

状态 Owner 是 Delivery Owner；适配器只能报告阶段结果，不能自行改变聚合状态。每次转换都必须以 `OperationId`、单调序号、旧状态、目标状态、触发原因和 UTC 时间持久化，使用 CAS 防止两个执行者同时推进。

```text
Requested
  -> Validating -> Prepared -> Quiescing -> Quiesced
  -> SupervisorStopping -> SupervisorStopped -> BackingUp -> BackupVerified
  -> Applying -> Applied -> Verifying
  -> Verified -> Activating
  -> VersionSelecting -> VersionSelected -> SupervisorStarting
  -> SupervisorStarted -> ReadinessVerified
  -> Draining -> Drained -> ResourcesReleased -> Resuming -> Resumed -> Completed
    Applying -> PartiallyApplied -> RecoveryRequired

任何可恢复阶段 -> CancelRequested -> Draining -> Drained -> ResourcesReleased -> Cancelled
Quiesced/Backup阶段失败且尚未Apply -> 验证旧版本健康 -> Draining -> Drained -> ResourcesReleased -> Resuming -> Resumed -> Failed
Applying/Verify/版本选择/启动失败 -> RecoveryRequired -> Recovering -> Restore/ForwardRepair -> Verify路线要求的数据与兼容包 -> 按revision CAS选择兼容发布槽（仅SnapshotRestore可选原槽） -> Start+Readiness -> Draining -> Drained -> ResourcesReleased -> Resuming -> Resumed -> Recovered
恢复动作得到确定失败回执 -> RecoveryFailed（继续隔离，不开放新工作）
恢复动作或 Resume 回执未知 -> RecoveryRequired（继续隔离，不开放新工作）
校验失败 -> Rejected
外部副作用无法判定 -> 保持当前非终态并进入 RecoveryRequired；只能查询原 OperationId/action 身份或执行批准的恢复命令
```

`Unknown` 不是可持久化的 `DeliveryState`，只表示某个外部 action 的查询知识不足；对应操作保持 `RecoveryRequired`，不发布成功或失败终态。查询确认 action 已完成时按其 durable receipt 继续；确认 action 未发生时才可依原请求重试；仍为 Unknown 时保持隔离。某次恢复动作以确定失败回执结束时进入 `RecoveryFailed`；只有前一 action 已排空、失败事实已持久化，且新 `RecoveryCommand` 使用新的 `ActionId` 并重新通过授权/前置条件检查，才允许 `RecoveryFailed -> Recovering`。未知 action 不得通过新 ID 重试。禁止的转换包括：`Rejected -> Applying`、`Cancelled -> Activating`、`RecoveryRequired -> Completed`、`RecoveryFailed -> Completed`、`Applying -> Requested`、`PartiallyApplied -> Completed`。`Completed`、`Recovered`、`Cancelled`、`Rejected` 和 `Failed` 是终态；`RecoveryRequired`、`RecoveryFailed` 不是终态。修复必须创建新的获批恢复 action，或由宿主创建新的迁移操作；不得覆盖历史回执。`PartiallyApplied` 只能进入 `RecoveryRequired`，并保留每个已持久成功步骤的回执；它不是可激活版本。

## 5. 同步、异步入口和事件顺序

核心只提供异步长操作；同步入口仅用于纯校验和读取。

```csharp
public interface IDeliveryService
{
    ValidationReport Validate(DeliveryRequest request);
    Task<DeliveryOperationSnapshot> ExecuteAsync(DeliveryRequest request,
        IProgress<DeliveryEvent>? progress, CancellationToken cancellationToken);
    // Requests cancellation of the durable operation; caller cancellation only cancels waiting.
    Task<DeliveryOperationSnapshot> RequestCancelAsync(OperationId operationId, CancellationToken ct);
    Task<DeliveryOperationSnapshot?> QueryAsync(OperationId operationId, CancellationToken ct);
    Task<DeliveryOperationDetails?> ReadDetailsAsync(OperationId operationId, CancellationToken ct);
    Task<DeliveryOperationSnapshot?> ReconcileAsync(OperationId operationId,
        TimeSpan observationBudget, CancellationToken ct);
    Task<DeliveryOperationSnapshot?> RecoverAsync(OperationId operationId,
        RecoveryCommand command, CancellationToken ct);
    Task<DeliveryOperationSnapshot?> RequestCleanupAsync(OperationId operationId,
        DeliveryCleanupCommand command, CancellationToken ct);
}

public sealed record RecoveryCommand(string ActionId, RollbackMode Strategy,
    string? BackupId, bool RequireOperatorConfirmation);
public sealed record DeliveryCleanupCommand(string ActionId, long ExpectedEpoch,
    string HandoffReceiptId, bool OperatorConfirmed);
public sealed record DeliveryOperationDetails(OperationId OperationId, long Sequence,
    DeliveryRequest FrozenRequest, PackageManifest? VerifiedManifest,
    ActiveReleaseSnapshot? OriginalRelease, ActiveReleaseSnapshot? CurrentRelease,
    BackupReference? Backup, IReadOnlyList<StepReceipt> Steps,
    HealthReport? Health, string? UnknownActionId);
public sealed class DeliveryContractException : Exception
{
    public string Code { get; }
    public DeliveryContractException(string code, string message) : base(message) => Code = code;
}
```

一次 `ExecuteAsync` 只接受一个 `OperationId`，并返回持久的当前 Snapshot；`Snapshot.Result` 仅在真实终态非空。重复请求先查权威操作存储：同摘要返回原 Snapshot（不重做副作用），不同摘要返回 `DUPLICATE_OPERATION_ID` 且不伪装成原请求成功。`QueryAsync` 对已知 OperationId 返回当前 Snapshot，仅在权威记录确认从未接纳时返回 null；`RecoverAsync` 只作用于已存在且处于 `RecoveryRequired` 或 `RecoveryFailed` 的原 OperationId，未知 ID 返回 null，不创建第二个操作。恢复策略必须与已签名 manifest 的 `RollbackMode` 一致；`SnapshotRestore` 必须提供原操作已验证的 `BackupId`，`ForwardRepair` 不接受 BackupId，`NotSupported` 一律拒绝。重试确定失败的恢复动作必须使用新 `ActionId`；存在 Unknown action 时先按原身份查询，不能以新 ID 重复副作用。事件顺序是硬约束：

1. `OperationAccepted`（持久化）→ `ValidationStarted` → `ValidationCompleted`。
2. `PrepareStarted` → 有界读取/验证全部来源字节 → `QuarantineCreated` → `StagingReady`（签名、路径、长度、摘要、落盘和读回全部验证）→ `ReleasePromotionRequested` → `ReleasePromoted`（不可变版本槽耐久且逐文件读回）。
3. `QuiesceRequested` → `QuiesceCompleted` → `DrainRequested` → `DrainCompleted`（或明确失败/超时）→ `SupervisorStopRequested` → `SupervisorStopped`（旧进程退出且共享资源已释放）。
4. `BackupStarted` → `BackupCreated`（冻结 checkpoint、权威闭包和逐对象回执）→ `BackupReadbackVerified` → `IsolatedRestoreDrillVerified` → `BackupVerified`。若闭包、独立读回或隔离演练失败，旧发布槽尚未切换；确认恢复原进程/版本 readiness 后，再排空本操作并 Resume。
5. `ApplyStarted` → 每个 `MigrationStepStarted/Completed` → `ApplyCompleted`。
6. `VerifyStarted` → `HistoricalReadbackChecked` → `VerifyCompleted`。
7. `ActivationRequested` → `VersionSelectionRequested` → `VersionSelected`（活动版本记录 CAS 耐久回执）→ `SupervisorStartRequested` → `SupervisorStarted` → `ReadinessObserved`（运行版本和 manifest hash 必须与目标发布槽相符）→ `ActivationCompleted` → `Draining` → `Drained` → `ResourcesReleased` → `ResumeRequested` → `ResumeCompleted` → `OperationCompleted`。
8. 在 `Quiesced` 后、首次 `ApplyStarted` 前失败或取消：确认原版本仍可用，先完成本操作的排空/释放，再以同一 `OperationId` 调 `ResumeAsync`，持久化接收恢复回执后才发布 `Failed`/`Cancelled`。备份失败、取消或 Apply 尚未开始都走此分支。
9. 自 `SupervisorStopped` 起直到 Resume 的任一失败/取消/未知结果，都不得假定旧进程仍运行。Apply 开始前失败时不执行数据恢复，但必须确认活动发布槽未变（或按 CAS 恢复原槽）、启动原发布槽并验证其版本/hash readiness。进入 `ApplyStarted` 后，先按 §14.1 选择唯一 Restore 或 ForwardRepair 路线并验证历史数据；Restore 路线才可在 revision CAS 后选择原发布槽并启动原版本，ForwardRepair 路线必须选择与已修复数据 schema 匹配的目标/修复槽，禁止盲选旧版本。对应版本 readiness 成功后，排空/释放本操作资源，再 `ResumeAsync` 并进入 `Recovered`。不能确定恢复结果、活动版本或 Resume 时保持 `RecoveryRequired` 隔离，禁止新工作，不发布成功终态。
10. 每个已接纳操作必须真实 `Drained → ResourcesReleased`；接纳曾关闭时再确认 Resume 回执，随后发布唯一终态。接纳从未关闭的预检拒绝/早期取消不调用 Resume。`ResourcesReleased` 仅表示 payload/借用资源已归还，进程根的控制 Owner、授权证据、Store/Quiesce 端口和 fence tombstone 保持至 Resume 与终态 CAS；详见 §6.3。排空或 Resume 超时保持 `Draining`/`RecoveryRequired`，不得伪造终态。

`ReleasePromotionRequested`、`VersionSelectionRequested`、Supervisor stop/start 都是可能在进程断开后结果未知的外部副作用；每项使用 `(OperationId, actionId)` 持久化并可查询。超时/断连不得换新 actionId 重试：先查询原动作；发布晋升结果未知时按完整 manifest key 查询；活动版本选择未知时查询当前 revision 和原选择回执；Supervisor 动作未知时查询原 actionId。任何查询仍未知则保持 `RecoveryRequired` 并隔离宿主。活动版本选择适配器必须提供单一权威记录、期望 revision CAS、原子且耐久替换语义；调用前持久化操作开始时的活动发布槽及 revision。不得用“先删旧指针再写新指针”、多文件部分更新或 Supervisor 自行选择最高版本实现切换。

`ReadinessVerified` 不是“进程启动成功”。`HealthReport.Evidence` 必须逐字段绑定正在运行的 `ReleaseSlotId`、目标 manifest hash、模块、批准的 policy/performance profile hash、machine boot/timing epoch 和有效期；每个必需 check 由连续、无缺样/重复/跨 epoch 的样本组成，样本的 source version 必须与运行版本一致。Core 在确认前重新读取或由受信适配器证明当前 staged runtime 的 manifest、能力和 profile join；过期、撤销、版本/hash 不匹配、缺样、readiness 查询未知或仅有 liveness 的报告均拒绝激活。升级前的当前版本 readiness 和升级后的目标版本 readiness 都必须真实查询并写入 Operation Snapshot；不得以旧健康缓存、静态 manifest、单次启动成功或 UI 显示代替。

事件是通知，不是事实 Owner；通知丢失可由 `QueryAsync` 从持久回执重建。事件处理器异常不得反向改变迁移状态。

`ReconcileAsync`只在有限observationBudget内按Store原intent/context查询适配器，CAS追加已确认观察/receipt并返回Snapshot，不新起Apply/Restore/Select/cleanup；源协调任务可据确定事实继续已获准路线。Unknown仍RecoveryRequired；未知ID返回null。`RecoverAsync`在原Unknown未排除时拒绝新动作；非终态已确认需要SnapshotRestore且原授权/备份完整时，Execute协调任务固定自动走该manifest路线，所以§9.2 VerifyFailsOnce预期Recovered；前置/授权不满足则RecoveryRequired，不能编造自动成功。ForwardRepair同样仅按§14.1 allowlist/幂等前置，无有效路线显式隔离。

`RequestCleanupAsync`仅供原Owner/已确认接收者在前一次cleanup确定停止、所有借用Task结束、原副作用结果已知后显式继续；验证HandoffReceiptId/OperatorConfirmed及ExpectedEpoch、Cleanup授权。新ActionId绑定原资源集合和一次CleanupBudget，结果Unknown只查此ID，不自动再试。它不执行迁移/切槽/Resume；未确认资源不能删，错误仍双轴。初次自动cleanup只有cleanup-0，显式批准的后续命令不称作重复自动finally清理。调用者token只取消等待者。所有配置/Factory/Session/槽前置拒绝抛DeliveryContractException并带稳定Code，不用可变Detail分支。

`ReadDetailsAsync`是无副作用的耐久证据投影，供面板和独立工具取得真实BackupId、原/当前槽、已验证计划、逐步回执及readiness，而不是让调用者从日志补猜。来源只能是原冻结request与adapter耐久receipt；未知字段用null，Steps为空只表示当前无已确定步骤，UnknownActionId不为空禁止盲Recover。Store.ReadRequest返回完整原请求；AppendDetails使用expectedSequence CAS使Details.Sequence与新Snapshot.Sequence相同，序列/身份不匹配拒绝；commit同时保存details（完整记录或null），不能UI自行写。已知操作尚无验证结果时返回仅FrozenRequest/空Steps/null其余值的details，未知ID返回null；返回值深复制，不含凭据。ReadDetails与Query配对读到sequence不同则有界重读，不能将旧BackupId用于新epoch恢复。

## 6. 适配器契约与资源所有权

```csharp
public interface IQuiesceAdapter
{
    Task<QuiesceReceipt> RequestAsync(DeliveryExecutionContext context, QuiesceMode mode,
                                       TimeSpan budget, CancellationToken ct);
    Task<DrainReceipt> DrainAsync(DeliveryExecutionContext context, TimeSpan budget,
        CancellationToken ct);
    Task<ResumeReceipt> ResumeAsync(DeliveryExecutionContext context, CancellationToken ct);
    Task<ActionQuery<QuiesceReceipt>> QueryRequestAsync(DeliveryExecutionContext context,
        TimeSpan observationBudget, CancellationToken ct);
    Task<ActionQuery<DrainReceipt>> QueryDrainAsync(DeliveryExecutionContext context,
        TimeSpan observationBudget, CancellationToken ct);
    Task<ActionQuery<ResumeReceipt>> QueryResumeAsync(DeliveryExecutionContext context,
        TimeSpan observationBudget, CancellationToken ct);
}

public sealed record ResumeReceipt(bool Resumed, bool AdmissionOpen,
                                   int QueuedCount, string? Detail);

public interface IStorageMigrationAdapter
{
    Task<BackupReference> CreateBackupAsync(DeliveryExecutionContext context, string scope,
                                             CancellationToken ct);
    Task<BackupReference> VerifyBackupAsync(DeliveryExecutionContext context,
        BackupReference backup, CancellationToken ct);
    Task<StepReceipt> ApplyAsync(DeliveryExecutionContext context, string stepId,
        MigrationStep step, CancellationToken ct);
    Task<ReadbackReport> VerifyReadbackAsync(DeliveryExecutionContext context,
        MigrationPlan plan, CancellationToken ct);
    Task<RecoveryReceipt> RestoreAsync(DeliveryExecutionContext context,
        BackupReference backup, CancellationToken ct);
    Task<RecoveryReceipt> ForwardRepairAsync(DeliveryExecutionContext context,
        MigrationPlan verifiedPlan, IReadOnlyList<StepReceipt> durableSteps,
        CancellationToken ct);
    Task<ActionQuery<BackupReference>> QueryBackupAsync(DeliveryExecutionContext context,
        TimeSpan observationBudget, CancellationToken ct);
    Task<ActionQuery<StepReceipt>> QueryStepAsync(DeliveryExecutionContext context,
        string stepId, TimeSpan observationBudget, CancellationToken ct);
    Task<ActionQuery<ReadbackReport>> QueryReadbackAsync(DeliveryExecutionContext context,
        TimeSpan observationBudget, CancellationToken ct);
    Task<ActionQuery<RecoveryReceipt>> QueryRestoreAsync(DeliveryExecutionContext context,
        TimeSpan observationBudget, CancellationToken ct);
    Task<ActionQuery<RecoveryReceipt>> QueryForwardRepairAsync(
        DeliveryExecutionContext context, TimeSpan observationBudget, CancellationToken ct);
}

public interface ISupervisorAdapter
{
    Task<SupervisorActionReceipt> StopAsync(DeliveryExecutionContext context,
        CancellationToken ct);
    Task<SupervisorActionReceipt> StartAsync(DeliveryExecutionContext context,
        ReleaseSlotReceipt selectedRelease, CancellationToken ct);
    Task<ActionQuery<SupervisorActionReceipt>> QueryActionAsync(
        DeliveryExecutionContext context, TimeSpan observationBudget, CancellationToken ct);
    Task<HealthReport> ReadinessAsync(DeliveryExecutionContext context, TimeSpan budget,
        CancellationToken ct);
}

public sealed record SupervisorActionReceipt(string ActionId, bool Completed, bool Running,
    ReleaseSlotReceipt? RunningRelease, bool Durable, string? Detail);
```

### 6.1 Journal、epoch、fence 与原 Task 保持

`IDeliveryOperationStore.BeginActionAsync` 必须在调用任何可能有副作用的适配器前写入不可变 `ActionIntent`；随后每次发送、回执、查询、取消请求、超时观察、清理和资源归还都追加 `ActionJournalEntry`。Intent 唯一键为 `(OperationId, ActionId)`；Journal 按该操作单调 JournalSequence 追加。同 ID 同输入只返回原 intent/receipt，同 ID 不同输入返回 `ACTION_INPUT_CONFLICT`。`Sequence`、`Epoch` 和 `FenceToken` 均由耐久 Store/Root Registry 产生，适配器不得自行生成或回退。`AppendErrorsAsync` 按 expectedSequence CAS 更新双错误轴；ReadIntents/ReadJournal 供重启查询和恢复使用，禁止从 UI 重建 ActionId。

Factory 前置条件是进程根的有界 Owner 槽，不是尚未取得的文件 lease。Factory 同步验证/装配端口，不做外部调用；`ExecuteAsync` 原 source Task 先由该槽强持，再原子接纳请求、记录 RootLeaseRequest，调用 `AcquireAsync`。Registry 返回的 RootId/epoch/fence 同时登记 payload lease 和控制权 tombstone。每项动作在发送前冻结自己的 `DeliveryExecutionContext`，不是跨动作使用同一个 ActionId。Work 命令过 deadline 或 payload lease 过期必须无副作用拒绝；Query、Cleanup、Resume 的受限权限按 §6.2/§6.3 校验，不能因原 Work deadline 到期而堵住收敛。

调用者的 `CancellationToken` 和 UI/Host 关闭只取消 waiter/subscription，不取消已经开始的 source `Task`。进程根先登记 `AdapterTaskLease` 和实际 Task/输入/释放委托的强引用，再发送动作，保存流/锁/句柄直到 source 真结束、耐久回执确定且独立 cleanup receipt 成功。迟到结果允许追加原 epoch 的观察 Journal，但不得改变新 epoch；未接纳且已过截止的迟到命令无副作用拒绝。禁止在 waiter 的 `finally` 中释放原 Task 仍使用的输入。资源 Owner 只启动 §6.2 的一次有限 cleanup，Unknown 保留资源和双错误轴，不能创建新 ID 掩盖旧 Task。

动作唯一键为 `(OperationId, ActionId)`，InputDigest 是同键冲突校验值，不能把不同 InputDigest 当作合法新键。ActionId 在首次 intent 中冻结为阶段/对象和确定 attempt 的稳定 ASCII ID（例如 `quiesce-0`、`apply-expand-0`、`select-target-0`、`restore-1`、`cleanup-0`、`resume-0`）。同键同完整 intent 返回原回执，同键不同输入/context 拒绝；Store 的唯一约束不能使用包含 InputDigest 的复合键来绕过冲突。Apply 的 `stepId` 与 `MigrationStep.StepId` 必须完全一致；文件/manifest key 和 step ID 是动作输入，不能代替 ActionId。输入摘要是该 ActionKind 的完整强类型输入（包括 module/slot/revision/step/hash/长度/授权根/借用资源 ID）的 JCS SHA-256，不含 context 自身，避免循环；DeadlineUtc、Scope、lease 与全部 intent 另整体冻结。初始Acquire无fence，以`BeginRootLeaseAsync`冻结完整RootLeaseRequest/LeaseActionId（同ID同内容幂等，不同拒绝）后发送；应答丢失查QueryAcquire，Found后再记录取得的epoch/fence，不向BeginAction传假fence。

所有副作用查询使用 `ActionQuery<T>`：Found 携带原动作的权威耐久回执，ConfirmedAbsent 只在权威记录证明未提交时返回，超时/断连/过期副本/证据不全为 Unknown。查询携带原 context，允许 deadline 已过或旧 epoch 的只读历史查询，另在本次 `observationBudget` 内返回；它不签发新的写权限，不把旧回执套到新 Action。Unknown 保持 RecoveryRequired、关闭接纳、保留资源。ConfirmedAbsent 也不能延长过期 Work 命令：截止尚有效才可重发原 intent；截止已过转失败/取消收敛或显式批准的 Recovery action。只读服务 Query 的 null 只表示确认不存在，查询异常显式失败。

Quiesce 固定采用 `CloseAdmissionAndDrainAccepted`：`RequestAsync` 先关闭新任务接纳，已接纳队列继续运行；随后 `DrainAsync` 等待运行中及已排队工作全部完成，只有 `Drained=true` 且 `RemainingCount=0` 才允许 `Backup/Apply`。拒绝新工作与完成在途工作必须是一个可查询的持久状态。激活/恢复和 readiness 验证成功后，先真实排空并释放本操作资源，再调用 `ResumeAsync` 以原 `OperationId` 幂等重开接纳；同 ID 重试返回原 ResumeReceipt，不得重复打开新 generation；回执未知时先查询原操作，禁止另造 ID 盲重试。`AdmissionOpen=false`、剩余队列非零或无法确认时不能继续并必须保持隔离。

适配器实现必须明确：线程亲和性、是否可取消、是否幂等、是否在未知结果时可查询、临时文件/连接/句柄释放者和重启后的可读范围。模块不释放适配器拥有的资源；模块只释放自己创建的 staging、订阅和计时器。备份对象在 `BackupVerified` 前由备份适配器持有保护；进入恢复策略或终态后按保留策略交还 GC Owner。任何尚在运行的迁移步骤仍持有输入、锁和临时空间时，不得在等待超时的 `finally` 中归还。

### 6.2 到期后的观察与单次有限 cleanup

本模块是文件/事务/进程恢复能力，HALCON/AsunImage 算法核验不适用。模型文件仅作为 opaque PackageEntry 字节迁移，内部语义与质量由模型资产 Owner 验证，Core 不引用视觉类型。

预算由 §9 的 `DeliveryRootOptions` 和请求 Limits 冻结：工作阶段预算、每次观察预算、一次 cleanup 总预算、Resume 预算、有限关闭观察预算分别计时，彼此不能续期。原工作截止到期只停止新 Work 发送并持久化 timeout；在途 source Task 仍由进程根持有。Query 在独立 observationBudget 下读取原回执；观察失败不会启动新副作用。Recovery 由原 OperationId 下新批准命令取得其一次 MaxRecovery 预算，不重置已过期 Work，也不重放成功步骤。

cleanup 是每操作一个 `cleanup-0` 总流水线和一个固定 deadline；只包含回执已确定且 Task 已结束的临时 payload/借用资源，按依赖逆序执行已登记 release delegate → staging Abandon → Registry Release。每一释放子动作使用 `cleanup-0/<resource-id>`，自身回执耐久并有 Query；整个流水线 deadline 不随子步骤刷新。不删除恢复点、活动/旧发布槽或正在使用的输入。deadline 前没有可安全释放的资源时保持强引用，记录 Outstanding；源任务在本次 cleanup 结束前迟到可继续同一流水线，结束后不能再自动重启 cleanup。后续只能由已确认的恢复 Owner 以显式新恢复/清理授权继续，同一旧 Task/资源/receipt 身份仍保留。Close 与 UI Dispose 不另建第二条清理循环。

清理例外写入 CleanupError；原 OperationError 保留，两个轴都投影到 Snapshot（新增字段见 §9）。未知、预算耗尽、释放委托异常或移交未确认均不报告资源已释放。清理 Task 自身晚到也按原子动作 ID 查询；重复 Close 观察同一 Task/截止，无第二次释放调用。不能在 Dispose/finally 中无限 await，不能用重置定时器或轮询直到成功替代有限收敛。

### 6.3 payload lease 与 Resume 控制权

Registry 的 payload lease 租期限制文件 Work；它到期不隐式删除根，也不把根交给下一个操作。在途任务未完成、cleanup 未确认或 Resume 未确认期间保留 root/resource key 的控制权 tombstone（OperationId/RootId/epoch/fence/Owner/授权决定及已冻结安全收敛权限），禁止第二 Owner 抢占。同 epoch 的 Cleanup 只允许处理登记资源；Resume 只允许恢复这个操作关闭的接纳 generation，不能 staging/Apply/选择新发布槽。

`ReleaseAsync` 的耐久回执只归还 payload 文件/句柄 lease，不撤销 tombstone；`ResourcesReleased` 是该事实，不宣称控制端口或进程 Owner 已释放。随后 Core 使用新 `resume-0` context，Scope=Resume，沿用原 OperationId/RootId/epoch/fence、单独有限 Resume deadline，并验证当前兼容槽/schema/readiness 和被冻结的安全收敛授权。`DeliveryAction` 增加 Resume；授权端口在关接纳前必须明确允许或拒绝该权限，恢复阶段再次确认吊销/有效性。授权不可确认时保持隔离和 RecoveryRequired；不能因文件 root 已释放免授权开放接纳。Resume 的 Query 允许在该截止后读原回执。

Resume 确定成功、终态 CAS 耐久且所有业务adapter source Task真结束后，Registry 的 `FinalizeAuthorityAsync` 原子撤销控制权，返回耐久 `AuthorityReleaseReceipt`；使用原OperationId/root/epoch/fence下唯一`authority-release-0`、Scope=ControlFinalize和独立一次AuthorityBudget。自身source Task同样由Root登记，回执Unknown保留Owner槽并在有限预算查询，不影响已提交业务终态事实，也不报告根关闭成功。该最终撤销不删除payload/发布槽、不重开接纳。Root协调Task不等待自己结束；所有adapter结果确定后可返回业务Snapshot，权限撤销迟到由Root继续强持观察。portLifetime只在Close且其余Task/控制权确认后释放，业务返回后仍可Query历史；不能让Close等待一个反过来等Close释放端口的Task。已释放payload不能用于新的Recovery写入；若Resume/终态之前确需新恢复，Registry `AcquireRecoveryAsync` 在原控制权下取得新有界payload lease并单调推进epoch，旧Task排空且旧cleanup确认后才可取得；发送前持久化旧context和新RootLeaseRequest，Unknown查QueryRecoveryAcquire，不能复用普通Acquire抢占。新的ActionId/epoch不覆盖原Journal，失败不退旧fence。

### 6.4 真实Adapter装配、模块交付与非目标

批准范围是机台、独立工具和服务的受控升级/修复/恢复及可选面板；本模块不拥有“允许部署”的决定。宿主先批准请求及维护窗口，Core才执行签名校验和软件动作。无视觉/坐标/图像操作，不直接引用viewport WPF；viewport Assembly更新不适用。首装、SDK驱动安装、任意脚本、远程推送/断点下载、自动生成领域迁移、HSM签名服务和生产放行不属于本模块。

除既有Core/Wpf外，真实文件和受控转接实现的唯一工程为`src/Modules/delivery-migration/Asun.Modules.DeliveryMigration.Adapters/Asun.Modules.DeliveryMigration.Adapters.csproj`（net10.0，不引用WPF、DevExpress、AsunImage、产品程序集或数据库驱动）；契约在Core，Adapters引用Core。其定向测试复用Core.Tests的断言，另唯一`tests/Modules/delivery-migration/Asun.Modules.DeliveryMigration.Adapters.Tests/Asun.Modules.DeliveryMigration.Adapters.Tests.csproj`为net10.0 BCL Exe，引用Core/Adapters，按§9.1分别build该两个工程再run Tests，60s合成外层截止相同。正式数据库/服务SDK/IPC端点实现留在消费者适配层，不复制本模块状态机；底层组件的具体供应商不由本指导选定。

Adapters namespace为`Asun.Modules.DeliveryMigration.Adapters`；其余公开端口、codec及维护/controller在`Asun.Modules.DeliveryMigration`。Adapters公开构造签名（均为本模块要实现的具体类，不是外部API；方法实现现有接口，不新增Shell初始化）：

```text
public sealed record DeliveryAdapterOptions(string Root, string OwnerIdentity, long MaxRecordBytes, int CopyBufferBytes = 65536)
FileDeliveryOperationStore(DeliveryAdapterOptions options, TimeProvider clock) : IDeliveryOperationStore
FileDeliveryReceiptStore(DeliveryAdapterOptions options) : IDeliveryReceiptStore
FileExecutionRootRegistry(DeliveryAdapterOptions options, IDeliveryReceiptStore receipts, TimeProvider clock) : IExecutionRootRegistryPort
DirectoryPackageSource(DeliveryAdapterOptions options) : IPackageSourcePort
FilePackageStaging(DeliveryAdapterOptions options, IExecutionRootRegistryPort roots, IDeliveryReceiptStore receipts, TimeProvider clock) : IPackageStagingPort
FileReleaseAdapter(DeliveryAdapterOptions options, IExecutionRootRegistryPort roots, IDeliveryReceiptStore receipts, TimeProvider clock) : IPackageReleaseAdapter
FileActiveReleaseAdapter(DeliveryAdapterOptions options, IExecutionRootRegistryPort roots, IDeliveryReceiptStore receipts, TimeProvider clock) : IActiveReleaseAdapter
SnapshotManifestTrustPort(TrustStoreSnapshot snapshot, IReadOnlyList<TrustedSigningKey> keys) : IManifestTrustPort
RegisteredStorageMigrationAdapter(string boundScope, IReadOnlyDictionary<string, IStorageMigrationAdapter> scopes, IMigrationRegistryPort registry, IDeliveryReceiptStore receipts) : IStorageMigrationAdapter
SupervisorBridge(ISupervisorActionTransport transport, IDeliveryReceiptStore receipts, DeliveryReadinessPolicy policy, TimeProvider clock) : ISupervisorAdapter
```

所有构造同步检查参数/非空/绝对授权根，不创建进程、不打开数据库、不复制文件。Root/Options仅绑定已由部署Owner建立且ACL受控的目录，不自动提权/修改ACL。MaxRecordBytes正且≤2^31−1；CopyBufferBytes为4096..1048576的2次幂，缺省65536 bytes（纯IO缓冲默认，不是客户负载门）；每个并行文件流一个池化缓冲，归还前清零。生产MaxRecordBytes来自部署Profile并覆盖最大Manifest/完整Snapshot/receipt，超限拒绝不截断。Path由构造根和内部稳定ID生成，禁止将异常Detail、请求者文字、HandlerId当路径。Owner/端口Lifetime仍经§9 Reserve转移，Close/原Task不重新设计。

完整消费者装配：机台服务或工具进程入口→创建options/受信时钟与receipt store→创建上表文件端口→以消费者明确实现的Quiesce、Authorization、Audit、MigrationRegistry、领域Storage scopes和Supervisor transport补齐DeliveryPorts→创建端口Lifetime聚合（每端口只登记一次，逆序释放）→Reserve→Factory→Validate/Execute/Query/Recover；不依赖产品数据库即可构造文件+模拟底层的第二消费者。适配测试须分别构造机台与工具实例，使用不同根/Owner/OperationId但同一签名fixture；一个消费者关闭/恢复不能操作另一根。

### 6.5 完整codec、耐久回执和文件提交算法

补齐Journal只有receipt hash却无可重建receipt的缺口；Store和adapter各守事实：Store拥有操作/intent/Journal，receipt store保存adapter提交的原始完整结果，不自行推进Core状态。Core读取intent/Journal后按kind读取receipt并核对hash；不得从“没有文件”推出ConfirmedAbsent。

```csharp
public sealed record DeliveryReceiptRecord(DeliveryExecutionContext Context,
    string Kind, Sha256 ContentSha256, ReadOnlyMemory<byte> CanonicalPayload);
public interface IDeliveryReceiptStore
{
    ValueTask<DeliveryReceiptRecord> CommitAsync(DeliveryReceiptRecord receipt, CancellationToken ct);
    ValueTask<ActionQuery<DeliveryReceiptRecord>> QueryAsync(DeliveryExecutionContext original,
        TimeSpan observationBudget, CancellationToken ct);
}
public static class DeliveryRecordCodec
{
    public static byte[] Encode<T>(string kind, T value) where T : class;
    public static T Decode<T>(string kind, ReadOnlyMemory<byte> bytes, int maxBytes) where T : class;
}
```

Codec签名为实现合同声明，需实现方法体后才能编译。封闭kind→T注册恰为：`request`→DeliveryRequest、`snapshot`→DeliveryOperationSnapshot、`operation-details`→DeliveryOperationDetails、`intent`→ActionIntent、`journal`→ActionJournalEntry、`root-request`→RootLeaseRequest、`root-lease`→ExecutionRootLease、`result`→DeliveryResult，以及`quarantine`→QuarantineStageRef、`manifest`→ManifestStagingReceipt、`entry`→PackageEntryReceipt、`seal`→StagingReceipt、`cleanup`→QuarantineCleanupReceipt、`release`→ReleaseSlotReceipt、`selection`→ReleaseSelectionReceipt、`quiesce`→QuiesceReceipt、`drain`→DrainReceipt、`resume`→ResumeReceipt、`backup`→BackupReference、`step`→StepReceipt、`readback`→ReadbackReport、`recovery`→RecoveryReceipt、`supervisor`→SupervisorActionReceipt、`health`→HealthReport、`authority`→AuthorityReleaseReceipt；§6.7的retention类型以独立`retention-request`/`retention-receipt`注册。任意object/多态$type/未知kind和T不匹配拒绝。所有嵌套record必须展开完整字段（例如Backup的Closure+Verification、Health的Evidence+Samples、Snapshot的Errors+DurableEvents+Result），不能只序列化摘要/局部ViewModel。

固定codec v1封套精确为`{"kind":K,"payload":P,"schema":"delivery-record/1"}`的JCS UTF-8无BOM/尾换行。P是对应完整record：显式JsonPropertyName使用C#字段名首字母小写（如`operationId`、`requestDigest`、`deadlineUtc`），与manifest专用投影不同；OperationId为小写Guid D字符串，ModuleId为Value字符串、Sha256为LowerHex64字符串、SemVersion为`major/minor/patch/prerelease`对象、ByteCount为非负整数、TimeSpan为十进制ticks字符串、DateTimeOffset转换UTC按§3.3 ActionIntent同规则。枚举固定ASCII名；int/long硬限定在±(2^53−1)，不合域拒绝；null显式输出，不能省略。列表按合同原序；InputLeaseIds/资源ID集合ordinal排序并拒绝重复；dictionary只允许已注册scope映射，按ordinal key排序。字符串不静默NFC归一（只有路径语法要求NFC），严格UTF-8/Unicode/重复键/未知字段/深度/字节上限校验后重新Encode必须与canonical输入相同。Decode不能创建任意Type，递归显式映射以本页record字段为完整schema；没有缺省字段补值。

RequestDigest固定是`Encode("request", request)`字节的SHA-256，包含全部Limits/Profile/RequestedAtUtc/关联身份；重复提交必须重用冻结请求，不以新时间改写同OperationId。receipt ContentSha256是完整封套字节SHA-256，Journal.ReceiptHash写同值。ActionIntent旧Golden是该对象裸JCS投影，继续有效；新增record封套Golden见本节末，两种域不能混用。`operation-details`必须包含全部公开字段；UI命令数据不是生产事实，不加入operation record kind，恢复仅从details/原receipt取值。

文件算法固定如下：每操作一个仅Owner可写的metadata目录；同根跨进程独占文件锁（FileShare.None打开固定lock文件，锁持有者与fence必须一致，失败RESOURCE_BUSY），同进程按OperationId异步串行门，锁内不执行adapter调用。Store每次CAS写完整新snapshot+新增intent/Journal+receipt引用到同一transaction对象，append-only序号文件；临时文件CreateNew写入→Flush(true)→关闭→同目录唯一commit文件原子改名→重新打开校验完整hash，再视为提交。已提交文件不覆盖；重启只读取完整commit文件并验证sequence连续、previous hash及CAS，未提交tmp隔离保留；缺中间commit/损坏为STORE_CORRUPT，不能跳过继续。实际transaction精确字段为`schema=delivery-transaction/1`、`operationId`、`sequence`、`previousSha256`（首条null）、`snapshot`（完整codec payload）、`intents`/`journal`（本次新增完整record列表）、`rootRequest`（有则完整否则null）、`details`（完整DeliveryOperationDetails payload或null）。单transaction原子发布防止Snapshot与Journal分开提交。

Snapshot.DurableEvents仅携带最近MaxEventQueue个已持久事件（ordinal原序），不是无界历史副本；完整历史保留在ReadJournalAsync的有界流式枚举，每次只解析一个≤MaxRecordBytes的commit。UI遇到sequence gap先以Snapshot整体重建状态再标注历史区间，不把丢弃旧投影当作事实丢失。Deep-copy所有可变byte[]/IReadOnlyList实参，提交后不可被调用者改写。每条commit≤MaxRecordBytes，旧日志归档只由批准保留策略处理，本轮不偷偷清理证据；空间不足停止新写入并保留原状态。

adapter先commit已接纳intent+Pending记录，再做副作用并持久化完整receipt；同key同输入已Found返回原结果，不重复发送。副作用完成与receipt提交无法同事务时，崩溃窗口为Unknown：staging按封口/逐文件hash重建事实，promotion按immutable slot seal+hash，selection按活动记录内原ActionId/inputDigest/revision，数据库按同事务步骤ledger，Supervisor按其耐久action查询；不能仅凭本地Pending重做。只有确定未发送且adapter的权威ledger保证没有提交可能，才ConfirmedAbsent。receipt store自身只有Pending时Query Unknown。receipt文件封套与context一并存为精确`context/kind/contentSha256/canonicalPayloadBase64`字段，payload标准padded Base64，decode后重算；不得存凭据。

`File.Replace`用于已存在活动记录的原子替换：生成包含目标槽、expectedRevision+1、原context和payload hash的完整新记录，Flush(true)，持独占锁检查revision后Replace并保留受控backup；首条基线由安装器建立，升级不创建空current。发布槽复制到同卷临时槽→逐条readback→commit seal→原子rename完整槽，跨卷只在目标卷复制/验hash后rename；目录不是“原子批量文件事务”。平台无法保证的电源故障/存储缓存持久性由部署Owner资格确认，未确认的flush/replace结果Unknown，不能由BCL API返回推导断电安全。官方依据：[FileStream.Flush(Boolean)](https://learn.microsoft.com/en-us/dotnet/api/system.io.filestream.flush?view=net-10.0)、[File.Replace](https://learn.microsoft.com/en-us/dotnet/api/system.io.file.replace?view=net-10.0)；本轮已定向读取，不变更既有JCS/签名研究。

完整最小record Golden（UTF-8无BOM/尾换行；正常ResumeReceipt全部字段，未代替其他完整域测试）：

| 向量 | 完整规范字节 | 字节数 | SHA-256 |
|---|---|---|---|
| DeliveryRecord.Resume | `{"kind":"resume","payload":{"admissionOpen":true,"detail":null,"queuedCount":0,"resumed":true},"schema":"delivery-record/1"}` | 124 | `6b4831bd68ac3048ee86a1b90649563729a2958c56eb3d0085a7496473d555d5` |

### 6.6 配置数据闭包、Supervisor与安全凭据

`DirectoryPackageSource`只读固定provider/artifact/revision对应的授权目录，生成不可变成员快照并拒绝reparse/hardlink/额外成员；打开后manifest/文件两遍读取hash变化就失效，不能把FileShare.Read当作跨进程不可变证明。压缩容器选择不是已批准范围，首发只支持目录介质，不能悄悄新增Zip/Tar依赖或download。生产包的签名在隔离发行器完成，Core从不接收私钥；部署TrustStoreRevision、KeyId、SPKI和吊销观察点是安全Owner输入。

真实文件Adapter首版面向Windows部署，Core/模拟Host仍纯net10.0。PathGuard先做§3.3相对路径/NFC/case碰撞校验，再GetFullPath(join(root,relative))并要求root+分隔符前缀（不接受仅字符串root前缀）；逐父级GetAttributes拒绝ReparsePoint，源最终文件以FileShare.Read固定打开，目标CreateNew拒绝覆盖；打开后再次核验根/父级/文件属性。hardlink不能只靠FileInfo.LinkTarget：对已打开SafeFileHandle调用[Win32 GetFileInformationByHandle](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileinformationbyhandle)，要求nNumberOfLinks=1，记录VolumeSerialNumber/FileIndexHigh/FileIndexLow并在读回时比对；失败或无法证实即拒绝。Windows专用internal P/Invoke签名固定为`[DllImport("kernel32.dll", SetLastError=true)] [return: MarshalAs(UnmanagedType.Bool)] static extern bool GetFileInformationByHandle(SafeFileHandle handle, out BY_HANDLE_FILE_INFORMATION info)`；结构Sequential按DWORD FileAttributes、三个FILETIME（CreationTime/LastAccessTime/LastWriteTime，每个Low/High两个uint）、DWORD VolumeSerialNumber/FileSizeHigh/FileSizeLow/NumberOfLinks/FileIndexHigh/FileIndexLow顺序，无SDK句柄穿透Core，SafeFileHandle由原FileStream持有并在原Task结束后归还。真实ACL必须排除其它可写主体，不能靠上述非原子路径检查抵御已授权目录被恶意替换；部署无法提供此隔离时适配器拒绝，权限条件不满足不转为较弱实现。其它OS返回明确NotSupported，未授权新增跨平台文件安全层。

安全凭据不进入PackageEntry/manifest/Store/日志/UI/复制闭包。用户身份不等于凭据，RequestedBy必须由消费方已认证会话绑定；授权端口每个危险阶段在原请求身份下重新判定，拒绝/来源Unknown不降级。数据库/备份介质/服务账号的凭据由注入参与者自行以宿主受控凭据库解析，仅将不含secret的credential revision/KeyEpoch写入闭包证据。备份若需加密，Storage参与者负责保留可恢复的key revision；缺钥或密钥撤销导致演练不可读则BACKUP_UNVERIFIED，不能删除原数据后才检查。Core不自行DPAPI加密或跨机导出密码、不迁移OS证书私钥/账号；换机安全部署由安全Owner提供目标凭据映射并验证，非猜测性凭据托管功能。

RegisteredStorageMigrationAdapter构造时以boundScope从冻结的scope→适配器映射选择唯一参与者，未知/重复拒绝，CreateBackup传入scope必须完全相同；Apply/Verify不靠“上次调用的scope”或全局变量路由。Registry确认plan全部handler/schema归属该scope。From/To/schemaId/handler/步骤参数（首版无任意参数字典）由Registry先冻结；同scope的Apply和步骤耐久ledger在同一真实事务中提交，以(OperationId,StepId)为唯一键、InputDigest作冲突校验。无事务文件迁移先写shadow数据+完整hash/readback，再以scope提交点CAS发布，原目录保留至恢复验证；不能就地半覆盖后伪称事务。按ordinal逐步执行，逐步提交receipt，失败停止；Restore同checkpoint全部对象闭包到隔离shadow，逐对象验证+历史读取+演练通过后发布scope提交点；ForwardRepair查ledger跳过成功步骤，剩余幂等步骤在当前precondition成立后前进，不自动生成逆函数。跨scope没有分布式提交，出现多个独立提交点须SnapshotRestore整闭包/明确前向路线，否则验证拒绝。

配置/配方/历史结果的字段含义与Schema映射仍由原领域Owner提供handler，不由本模块生成；迁移后的内容和原内容hash必须可读回。保留配置的默认是完整原件不修改：只有已签名计划引用已注册handler的对象才允许变更；未知文件和未登记目录不删除、不合并、不补默认值。人工编辑须形成新获批计划/包，不能覆写原操作。Upgrade无数据变更可登记受信NoOp handler（验证schema不变、仍有真实readback receipt），不接受空step当成功；Repair零step的“明确语义”来自DeliveryRequest.Mode和manifest From=To/RequiresProcessRestart，不臆造manifest未定义mode字段。

SupervisorBridge依赖下列Core中公开传输契约；这是受控进程服务的协议边界，不指定或下载SDK/IPC库：

```csharp
public enum SupervisorVerb { Stop, Start }
public sealed record SupervisorCommand(SupervisorVerb Verb, ReleaseSlotReceipt? Release);
public sealed record DeliveryReadinessPolicy(ModuleId Module, string ContractMajor,
    Sha256 CapabilityFingerprint, string PolicyProfileId, Sha256 PolicyProfileSha256,
    string PerformanceProfileId, Sha256 PerformanceProfileSha256,
    IReadOnlyList<string> RequiredChecks, int ConsecutiveCount, TimeSpan MaximumSampleAge);
public interface ISupervisorActionTransport
{
    Task<SupervisorActionReceipt> SendAsync(DeliveryExecutionContext context,
        SupervisorCommand command, CancellationToken ct);
    Task<ActionQuery<SupervisorActionReceipt>> QueryAsync(DeliveryExecutionContext original,
        TimeSpan observationBudget, CancellationToken ct);
    Task<HealthReport> ProbeAsync(DeliveryExecutionContext context,
        TimeSpan budget, CancellationToken ct);
}
```

Bridge Stop映射Verb.Stop/Release=null；Start映射Verb.Start/明确selectedRelease；发送前写intent/Pending，不发shell/任意exe路径或“最高版本”。Transport只与部署Profile绑定的Supervisor service身份连接，双向身份验证/账号权限由安全Owner的既有端点提供，不盲接广播地址。Stop成功必须原进程及其共享资源确实退出（不强杀承载Core的进程）；Start必须process receipt绑定slot/hash/version；Probe核对Health全部Evidence字段、连续样本/epoch/有效期，未知不变成Ready。Bridge观察预算与source Task按§6.1～6.3，晚到回执只加入原身份；服务实际启动方式、IPC端点与客户checks是SupervisorOwner输入，协议映射/验证算法已在此冻结。

ReadinessPolicy构造时深复制、RequiredChecks非空/唯一、ConsecutiveCount≥2、MaximumSampleAge正且有限，值及Profile hash来自部署Owner；无默认客户时限。Bridge对每check选取恰好最近N个按ordinal连续且非重复健康样本，同MachineBootId/TimingEpoch、SourceVersion=当前slot.Version、manifest/hash/module匹配；ObservedStart≤End且在本次受信单调epoch内，最老End距当前≤MaximumSampleAge，跨epoch/无法关联时拒绝；ContractMajor/Capability/两个Profile身份逐字段比对policy。ExpiresAtUtc只作额外审计有效性，不用墙钟回拨延长单调期限。Probe异常不使用旧缓存；当前版本与目标版本分别使用部署Owner批准的对应policy，不能拿目标policy要求旧版本具备未支持能力。

### 6.7 保留政策与受控清理入口

保留/删除是原规划能力，首版仅处理本模块已登记的不再引用的完整发布槽与backup，绝不枚举未知目录或客户配置/结果。当前槽、上一受支持且被Profile保留的恢复槽、任何非终态操作引用、在途lease、移交未结束、法定保留/hold对象都保护。默认`Keep`，不因MaxRetainedBackups达到上限就删活动恢复点；空间不足拒绝新升级。参数不自动推荐或后台调参，UI只能提示所需/现有字节和Profile限制，不修改deadline/保留周期。

```csharp
public enum DeliveryRetentionDisposition { Keep, Remove }
public sealed record DeliveryRetentionRequest(OperationId OperationId, string ActionId,
    ModuleId Module, string ArtifactId, Sha256 ExpectedContentSha256,
    long ExpectedRevision, DeliveryRetentionDisposition Disposition,
    string PolicyId, Sha256 PolicySha256, bool OperatorConfirmed);
public sealed record DeliveryRetentionReceipt(string ArtifactId, long Revision,
    DeliveryRetentionDisposition Disposition, bool Applied, bool Durable,
    string? ErrorCode);
public sealed record DeliveryRetentionArtifact(string ArtifactId, ModuleId Module,
    Sha256 ContentSha256, long Revision, bool Active, bool Referenced,
    bool Leased, bool Held, string AuthorizedRootId);
public interface IDeliveryRetentionCatalog
{
    Task<DeliveryRetentionArtifact> InspectAsync(ModuleId module, string artifactId,
        CancellationToken ct);
    Task<DeliveryRetentionReceipt> CommitAsync(DeliveryExecutionContext context,
        DeliveryRetentionRequest request, CancellationToken ct);
    Task<ActionQuery<DeliveryRetentionReceipt>> QueryAsync(DeliveryExecutionContext original,
        TimeSpan observationBudget, CancellationToken ct);
}
public interface IDeliveryRetentionService
{
    Task<DeliveryRetentionReceipt> ExecuteAsync(DeliveryRetentionRequest request, CancellationToken ct);
    Task<ActionQuery<DeliveryRetentionReceipt>> QueryAsync(OperationId operationId,
        string actionId, TimeSpan observationBudget, CancellationToken ct);
}
```

具体构造`DeliveryRetentionService(DeliveryProcessRoot root, DeliveryOwnerSlot slot, DeliveryPorts ports, IDeliveryReceiptStore receipts, IDeliveryRetentionCatalog catalog, DeliveryHostOptions hostOptions, DeliveryRequest authorityRequest, TimeSpan budget)`。维护使用独立新OperationId/slot，authorityRequest只作为冻结的主体/module/Profile授权输入，不调用升级Execute、不假造Completed升级回执。service在原Root中登记维护Task，发送前以同一Acquire/receipt流程取得根锁与控制fence，结束后依§6.2/6.3释放payload/控制权（无需quiesce/Resume）。使用ports.Authorization/Roots/Store和独立receipt store、catalog；authorityRequest.OperationId/module必须与RetentionRequest相同，预算来自批准维护Profile。无凭据/裸绝对删除路径穿透公开请求。

调用顺序：Root Reserve强持Task→验证request ID/revision/hash/Policy全部必填且预算有限→授权RetainOrRemoveRelease→catalogInspect→核对module/hash/revision/安全根与四保护位→构造Scope.Cleanup的原Action context/intent→catalogCommit原子重查保护位与revision，Keep只写保留标记/递增revision，Remove先将受控artifact原子标记Retired（不可新租用），等待既有lease归还；无lease才能以原ID删除登记文件列表，flush墓碑回执→receipt store耐久记录。删除的配置/发布基线授权来自PolicyOwner，不由控件选择路径；manifest引用文件集之外内容出现则ARTIFACT_CONTENT_CHANGED并保留。Query未知返回Unknown，重复同输入幂等，冲突拒绝；中断删除在Retired下由原ID查询并继续已授权登记列表，不产生新的删除目标。catalog支持的revision/引用/lease权威要与活动槽/backup registry同一事务门，做不到原子保护就拒绝Remove，不以先读后删掩盖TOCTOU。

Retention的授权输入是构造时可信冻结的authorityRequest，不能由UI随意传RequestedBy；新维护身份不替换升级操作历史。UI RetentionRequest.OperationId为新maintenance slot ID，Session仍指被观察的交付操作；controller核对两个module及artifact引用归属，写独立维护intent，结果单独查询。Retain/Remove不是恢复或生产放行，失败不覆盖原交付终态。Owner为Delivery维护者+catalog事实Owner，真实路径/ACL/Policy是外部资料门，软件步骤与默认Keep已可按文实施。具体`FileDeliveryRetentionCatalog(DeliveryAdapterOptions options, IExecutionRootRegistryPort roots, IDeliveryReceiptStore receipts)`落在上述Adapters，复用§6.5 ledger与同根锁，保护位来自同一活动/引用/lease注册权威事务，不新增通用数据库或业务表。

## 7. 取消、超时、排空和线程规则

- 取消在 `Requested`、排队和 `Quiescing` 可拒绝后续阶段；若 quiesce 已生效，先验证当前可用版本，再按原 OperationId 恢复接纳。`Applying` 后只请求安全停止并执行确定的恢复路径，不能假设原生/数据库操作立即终止。
- 等待超时只结束等待者，不终止源任务。源任务必须继续由 Delivery Owner 观察、写最终回执并归还资源。
- `RequestAsync` 先关闭新工作接纳，`DrainAsync` 再等待已接纳队列/运行任务、IPC 回调、文件写入和数据库事务真实归还；排空超时保持 `Draining` 并查询原操作，不能替换正在使用的二进制或 native 依赖。
- `ResumeAsync` 只在 payload 排空/释放且当前路线的兼容版本、readiness/readback 已验证后调用。SnapshotRestore 可恢复旧版本；ForwardRepair 使用与目标 schema 匹配的目标/修复槽，不能默认旧版本。以原 OperationId 的 `resume-0` context 调用，控制权存续见 §6.3；未知保持隔离。
- 禁止 `Thread.Abort`、强杀承载进程、在锁内 `await`、在回调中重入状态写入和无限重试。原 Work 重试不重置工作 deadline；到期只读观察、一次 cleanup、Resume 和显式批准 Recovery 使用各自有限预算，按 §6.2 保留原动作事实。
- 每个阶段有独立经过时间预算：queue、quiesce、backup、apply、verify、activation、recovery；日志同时记录实际开始/结束和排队等待。
- 并发策略默认 `MaxActiveOperations=1`（同一目标环境），不同环境可并行；同一文件根、数据库、服务或备份集的操作必须以资源键串行。宿主可提高并发，但必须证明备份一致性和容量上界。

## 8. 错误码语义与恢复动作

错误码稳定、可本地化；Detail 可变且不得作为程序分支条件。下表使用与产品无关的 `DELIVERY.*` 命名候选，待全局错误目录采纳；平台适配器如必须接入既有 `AOI.*` 目录，只能在边界做一对一映射并保留本地码。

| 本地码 | 全局码候选 | SafeState | 重试/恢复语义 |
|---|---|---|---|
| `INVALID_REQUEST` | `DELIVERY.INVALID_REQUEST` | 未写入宿主数据 | Never；修正请求后新操作 |
| `PACKAGE_HASH_MISMATCH` | `DELIVERY.PACKAGE_TAMPERED` | 未应用 | Never；重新取得签名包 |
| `PACKAGE_TRUNCATED` | `DELIVERY.PACKAGE_TRUNCATED` | 未应用 | Never；重新取得包 |
| `PACKAGE_TOO_LARGE` | `DELIVERY.PACKAGE_TOO_LARGE` | 未应用 | Never；使用获批分片或容量 Profile |
| `TOO_MANY_STEPS` | `DELIVERY.TOO_MANY_STEPS` | 未应用 | Never；拆分并重新签名迁移计划 |
| `SIGNATURE_INVALID` | `DELIVERY.SIGNATURE_INVALID` | 未应用 | Never；授权密钥/包问题 |
| `DEPENDENCY_INCOMPATIBLE` | `DELIVERY.DEPENDENCY_INCOMPATIBLE` | 未应用 | Never；选择兼容包 |
| `AMBIGUOUS_COMPATIBILITY` | `DELIVERY.AMBIGUOUS_COMPATIBILITY` | 未应用 | Never；补充明确版本区间 |
| `COLD_TARGET_NOT_INITIALIZED` | `DELIVERY.COLD_TARGET_NOT_INITIALIZED` | 未接纳 | Never；由宿主安装器建立当前槽和基线回执 |
| `INSUFFICIENT_SPACE` | `DELIVERY.INSUFFICIENT_SPACE` | 原版本可运行 | AuthorizedRecoveryOnly；释放空间并重新 Prepare |
| `RESOURCE_EXHAUSTED` | `DELIVERY.RESOURCE_EXHAUSTED` | 原版本可运行 | AuthorizedRecoveryOnly；释放并重新 Prepare |
| `RESOURCE_BUSY` | `DELIVERY.RESOURCE_BUSY` | 原操作保持 | Query/排队；不抢占活跃租约 |
| `QUEUE_FULL` | `DELIVERY.QUEUE_FULL` | 未接纳 | NewAttemptRequired；调用方退避或稍后提交 |
| `QUIESCE_TIMEOUT` | `DELIVERY.QUIESCE_TIMEOUT` | 未 Apply | Query/人工排空；不得强替换 |
| `BACKUP_UNVERIFIED` | `DELIVERY.BACKUP_UNVERIFIED` | 未 Apply | Never；建立并验证新恢复点 |
| `BACKUP_CLOSURE_INCOMPLETE` | `DELIVERY.BACKUP_CLOSURE_INCOMPLETE` | 未 Apply | Never；补齐权威闭包并重新备份 |
| `RESTORE_DRILL_FAILED` | `DELIVERY.RESTORE_DRILL_FAILED` | 保持隔离 | AuthorizedRecoveryOnly；保留演练证据并修复恢复源 |
| `MIGRATION_STEP_FAILED` | `DELIVERY.MIGRATION_FAILED` | 可能部分变更 | QueryOperationFirst；按计划 Restore 或 ForwardRepair |
| `VERIFY_FAILED` | `DELIVERY.VERIFY_FAILED` | 新版本未激活 | AuthorizedRecoveryOnly；保留旧入口 |
| `READINESS_EVIDENCE_INVALID` | `DELIVERY.READINESS_EVIDENCE_INVALID` | 新版本未激活 | QueryOperationFirst；重新收集绑定当前运行版本的样本 |
| `READINESS_TIMEOUT` | `DELIVERY.READINESS_TIMEOUT` | 激活未知 | QueryOperationFirst；查询 Supervisor，不盲重启 |
| `DRAIN_TIMEOUT` | `DELIVERY.DRAIN_TIMEOUT` | 资源仍在用 | Abort/人工恢复；不能删除 staging/旧依赖 |
| `UNKNOWN_SIDE_EFFECT` | `DELIVERY.UNKNOWN_SIDE_EFFECT` | 结果未知 | QueryOperationFirst；不可直接重试 |
| `DUPLICATE_OPERATION_ID` | `DELIVERY.DUPLICATE_OPERATION` | 原操作保持 | Query 原回执；不同请求拒绝 |
| `RECOVERY_FAILED` | `DELIVERY.RECOVERY_FAILED` | 需要人工接管 | RequireOperator；不得报告 PASS/可用 |
| `ACTION_INPUT_CONFLICT` / `STALE_FENCE` | 对应 `DELIVERY.*` 同名键 | 原动作/新epoch不变 | 同ID不同输入或旧写权限拒绝，历史Query仍可读 |
| `DEADLINE_EXPIRED` | `DELIVERY.DEADLINE_EXPIRED` | 停新Work，持有在途Task | 原Query/有限cleanup/获准Recovery，不续期Work |
| `SESSION_OPERATION_NOT_FOUND` / `SESSION_EPOCH_MISMATCH` / `SESSION_RESOURCE_BUSY` | 对应 `DELIVERY.*` 同名键 | 不创建新binding/timer | Query确认原操作/epoch；待原解绑查询结束后重绑，不取消Core |

数据库提交应答丢失、服务启动结果丢失、外部协议回执丢失都先归入 `UNKNOWN_SIDE_EFFECT`，只有对应适配器的查询证明“未发生”后才能重试。错误映射必须包含 `safeState`、`retryability`、`recoveryActionId` 和测试用例，不得只映射异常类型。

## 9. 公开构造与无 UI 接入

本节冻结 namespace `Asun.Modules.DeliveryMigration` 的公开构造面。签名块是实现后的 API 形状，不是已经存在的产品实现；Host C# 块是按这些签名编写的完整调用规格，须在获准实现后编译/执行。没有依赖隐藏 DI、全局 ServiceLocator 或窗口初始化的入口。

```csharp
public sealed record DeliveryPorts(IDeliveryOperationStore Store,
    IPackageSourcePort Source, IManifestTrustPort Trust,
    IDeliveryAuthorizationPort Authorization, IMigrationRegistryPort MigrationRegistry,
    IDeliveryAuditPort Audit, IExecutionRootRegistryPort Roots,
    IPackageStagingPort Staging, IPackageReleaseAdapter Releases,
    IActiveReleaseAdapter ActiveRelease, IQuiesceAdapter Quiesce,
    IStorageMigrationAdapter Storage, ISupervisorAdapter Supervisor);
public sealed record DeliveryRootOptions(int MaxOwnerSlots, TimeSpan ObservationBudget,
    TimeSpan CleanupBudget, TimeSpan ResumeBudget, TimeSpan AuthorityBudget,
    TimeSpan ShutdownBudget);
public sealed record DeliveryHostOptions(string AuthorizedRoot, string OwnerIdentity,
    ByteCount MaxRootBytes, TimeSpan PayloadLeaseDuration);
public sealed record DeliveryOwnerSnapshot(OperationId OperationId, long Epoch,
    IReadOnlyList<AdapterTaskLease> Tasks, DeliveryErrorAxes Errors,
    bool PayloadReleased, bool AuthorityReleased);
public sealed record DeliveryCloseReceipt(bool Closed,
    IReadOnlyList<DeliveryOwnerSnapshot> Outstanding, string? HandoffOfferId);
public sealed record DeliveryHandoffOffer(string OfferId, DeliveryProcessRoot Root,
    IReadOnlyList<DeliveryOwnerSnapshot> Outstanding, long LastJournalSequence);
public sealed record DeliveryHandoffConfirmation(string OfferId, string ReceivingOwner,
    bool Accepted, string ReceiptId);
public interface IDeliveryRecoveryOwner
{
    ValueTask<DeliveryHandoffConfirmation> AcceptAsync(DeliveryHandoffOffer offer,
        CancellationToken ct);
}
```

公开签名（下列类型由本模块 Core 实现，具体类的构造函数不是接口占位）：

```text
public sealed class DeliveryProcessRoot
  public DeliveryProcessRoot(TimeProvider clock, DeliveryRootOptions options)
  public TimeProvider Clock { get; }
  public DeliveryOwnerSlot Reserve(OperationId id, IAsyncDisposable portLifetime)
  public DeliveryOwnerSnapshot Inspect(OperationId id)
  public Task<DeliveryOperationSnapshot> ObserveAsync(OperationId id, TimeSpan budget, CancellationToken ct)
  public ValueTask<DeliveryCloseReceipt> CloseAsync(CancellationToken ct)
  public ValueTask<DeliveryHandoffConfirmation> HandoffAsync(IDeliveryRecoveryOwner receiver, CancellationToken ct)
public sealed class DeliveryOwnerSlot // constructor internal; only Reserve returns it
  public OperationId OperationId { get; }
public static class DeliveryFactory
  public static IDeliveryService Create(DeliveryProcessRoot root, DeliveryOwnerSlot slot, DeliveryPorts ports, DeliveryHostOptions options)
```

构造顺序固定为：进程入口强持一个显式 `DeliveryProcessRoot` → 创建私有端口及其 Lifetime Owner → Reserve 槽（原子转移 portLifetime，尚无异步副作用）→ Factory 同步装配 → Validate → Execute。Reserve 之前端口构造失败由创建者有界释放；Reserve 成功之后即使 Factory 抛错也只能由进程根清理，宿主不可重复 Dispose。Factory 校验全部非空、绝对/NFC 授权根、正有限预算、MaxOwnerSlots/MaxRootBytes、slot 属于该 root 且未绑定；一次 slot 只能绑定一次，失败不启动包读/Store/Registry。JCS 固定依赖由 Core 直接构造，不注入一套“内存 JCS”。一个 service 只接受 slot.OperationId，其他操作 ID 返回 INVALID_REQUEST；同 ID 重复 Execute 使用同一 source Task/耐久回执。多操作先 Reserve 新槽，容量满同步 RESOURCE_BUSY，没有隐含排队扩容。

原 source Task、所有 adapter Task、输入流/借用资源和 portLifetime 在首个外部调用前由槽强持；Execute 的 token 只取消 waiter。宿主显式保留进程根到关闭成功或移交确认，不用 `await using` 在方法离栈自动销毁根。ObserveAsync 在 budget 内等待已登记原 Task 的确定快照；超时抛 TimeoutException，取消抛 OperationCanceledException，不启动新 Task、不当作底层停止。Inspect 是内存所有权观察，不替代耐久 Query。

Close 首次调用冻结一个 ShutdownBudget，拒绝新 Reserve，通知停止发送新 Work，观察原 Task 和同一 cleanup/authority-release 流水线；重复 Close 共用第一次 source Close Task/截止。截止返回 Closed=false 和 Outstanding，仍强持所有资源，不会 Dispose 根或吞原错误。正常关闭必须 payload/控制回执都确定、Task 都结束后调用一次 portLifetime.DisposeAsync；该 Task 也登记在槽并受同一有界关闭观察，失败保留 Owner。

Handoff 在 ShutdownBudget 内生成包含原身份、epoch/fence、任务/资源 ID、双错误轴及最后 JournalSequence 的 offer，将实际 Root 引用交给接收者。接收者先强持 Root，再耐久登记 ReceivingOwner/ReceiptId 才可 Accepted=true；Root 以 OfferId CAS 验证确认，同一 offer 不转给第二 Owner。拒绝/应答丢失/超时保持原进程 Owner，不能仅写联系人就结束。确认后原宿主退出等待职责，Root 和 source Task 不 Dispose、不重新创建，接收者继续同一观察/cleanup；恢复授权是显式后续操作。真正进程崩溃不能强持 CLR Task，重启读取 Store/Registry/适配器原动作，不推断进程退出等于副作用未发生。

### 9.1 两个可构造的无 UI Host 与唯一 Core 验证工程

唯一 Core 工程和测试工程仍分别是：

- `src/Modules/delivery-migration/Asun.Modules.DeliveryMigration.Core/Asun.Modules.DeliveryMigration.Core.csproj`：`Microsoft.NET.Sdk`、`net10.0`，只引用 .NET BCL/Jcs.Net；不引用 WPF、DevExpress、AsunImage、数据库驱动、设备 SDK 或产品 Shell。
- `tests/Modules/delivery-migration/Asun.Modules.DeliveryMigration.Core.Tests/Asun.Modules.DeliveryMigration.Core.Tests.csproj`：`Microsoft.NET.Sdk`、`net10.0`、`OutputType=Exe`，只引用 Core 与 BCL，不引入测试包。该一个 Exe 内必须能构造以下两个完整 Host，不能用全局 singleton 或隐藏 factory：

1. `InMemoryRecoveryHost`：完整构造内存 Store/Trust/包源/staging/版本槽、受控 Quiesce/Storage/Supervisor/Audit/RootRegistry，经真实 Core 状态机执行；JCS 使用 Core 的固定实现。
2. `FileReplayHost`：完整构造 BCL 文件端口，Store/Journal/发布槽/备份采用文件读回；存储事务只是可控文件等价模拟，不宣称 SQLite 或真实客户数据库通过。两个 Host 的具体构造、输入和执行见 §9.2。

两个 Host 由同一 Core API/断言驱动，不直接调用适配器绕过状态机。case ID 保留 `DM-CORE-VALIDATE-001`、`DM-CORE-GOLDEN-002`、`DM-CORE-IDEMPOTENCY-003`、`DM-CORE-UNKNOWN-004`、`DM-CORE-RECOVERY-005`、`DM-CORE-FENCE-006`、`DM-CORE-CANCEL-007`、`DM-CORE-CLEANUP-008`、`DM-HOST-FILE-009`、`DM-HOST-RESTART-010`；§9.3 定义追加到期/Resume/构造/Bind断言。任一失败、未完成、必须项跳过、观察超时、cleanup 未确认或关闭未确认均非零。

从仓库根执行，先分别构建 Core 和 Tests（包含 restore；只有本轮已对两个工程完成 restore 才能用 --no-restore），再运行已构建的 Tests；仅 build Core 后 --no-build run Tests 无效：

```powershell
dotnet build src/Modules/delivery-migration/Asun.Modules.DeliveryMigration.Core/Asun.Modules.DeliveryMigration.Core.csproj -c Release
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
dotnet build tests/Modules/delivery-migration/Asun.Modules.DeliveryMigration.Core.Tests/Asun.Modules.DeliveryMigration.Core.Tests.csproj -c Release
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$dmRun = Start-Process -FilePath dotnet -ArgumentList @('run','--project','tests/Modules/delivery-migration/Asun.Modules.DeliveryMigration.Core.Tests/Asun.Modules.DeliveryMigration.Core.Tests.csproj','-c','Release','--no-build') -PassThru -WindowStyle Hidden
if (-not $dmRun.WaitForExit(60000)) {
    Stop-Process -Id $dmRun.Id
    exit 124
}
exit $dmRun.ExitCode
```

60s 是合成 harness 外层截止，不是客户节拍；外层终止只标测试失败，不能证明子任务资源正常释放。Tests 内每个等待和关闭都有更短预算，正常测试应在外层截止前归还。也允许 `dotnet run --project tests/Modules/delivery-migration/Asun.Modules.DeliveryMigration.Core.Tests/Asun.Modules.DeliveryMigration.Core.Tests.csproj -c Release` 自动构建再运行；不得用 dotnet test 的“没有测试”退出码代替。

容量预检必须同步调用 `IPackageStagingPort.CheckCapacity(...)`，确认声明解压字节、manifest、entry 数、最小余量和租约上限；它不预留空间，因此写入期间仍须处理磁盘耗尽。性能按 DEV-GOV-010 的 BenchmarkProfile 记录从接纳到 `ResourcesReleased` 的端到端时长、各阶段 P50/P95/P99、峰值字节/句柄/锁/租约和失败/删失样本；缺少批准目标为 `NotEvaluated`，不得以 Host 通过声称客户节拍。

### 9.2 两个完整 composition root 与输入

下列 Tests 私有类型只服务本页 conformance，落点为唯一 Tests 工程的 `Hosts.cs`；不是公共 DLL、第二套状态机或客户默认 Profile。每个类型的构造与行为在此冻结，不允许用“已注入变量”略去来源：

Retention/codec/真实Adapter/Details为0.1.8-prep增量：两个既有Memory/FileDeliveryPorts需实现新增Store.ReadRequest/ReadDetails/AppendDetails和同序CAS，使用本页完整Details codec；之前测试行为与五个向量不变。SignedPackageFixture及端口最终断言不因UI只读投影新增数据写入。

| 测试类型/公开于 Tests 的签名 | 具体责任 |
|---|---|
| `SignedPackageFixture.Create()` → `SignedPackageFixture`；属性 `Source`、`SignedManifest`、`Entries`、`PublicKey`、`CurrentRelease` | 用 BCL RSA.Create(3072) 产生一次测试密钥、导出 SPKI；按下文固定字节生成真实 PSS 签名，返回独立 byte[]；局部 RSA 在签名后 Dispose，私钥不注入 Core |
| `MemoryDeliveryPorts(SignedPackageFixture fixture, string root, TimeProvider clock, DeliveryFault fault)`，`Ports`，`AssertFinal(bool recovered)`，`Disposed`，实现 `IAsyncDisposable` | 私有类实现 DeliveryPorts 全部13接口，构造 `new DeliveryPorts(this,this,this,this,this,this,this,this,this,this,this,this,this)`；各接口的状态分离为不可混用字典，Store/Registry 为唯一事实 Owner |
| `FileDeliveryPorts(SignedPackageFixture fixture, string root, TimeProvider clock, DeliveryFault fault)`，同上 | 同样13接口，BCL文件流、Flush(true)、原子同目录文件替换实现测试 Store/槽/备份；初始目录只能由明确临时根生成；重建时原fixture byte[]/SPKI须保留并传回构造器，不重新生成测试密钥，不读客户路径；不模拟客户事务能力合格 |
| `DeliveryFault { None, VerifyFailsOnce, ApplyReplyLost, HoldApply, CleanupReplyLost }` | 在指定动作第一次返回处注入；VerifyFailsOnce 是 Apply已提交后readback失败，恢复后读回成功；ApplyReplyLost 是提交成功但调用/首次Query Unknown，后续原ID Query Found；HoldApply 用显式闩锁强持输入；CleanupReplyLost 是cleanup已提交但首次查询Unknown |
| `ConfirmedRecoveryOwner(string identity)`，实现 `IDeliveryRecoveryOwner`；属性 `HeldRoot`（最近一次）、`HeldRoots`（按OfferId保存全部根）、`Offers`；`TrackOriginRoot(DeliveryProcessRoot root)` | TrackOriginRoot由测试进程入口强持原Owner的全部Root，不代表已确认移交；接收offer先把实际root强存入HeldRoots，再写内存耐久等价确认receipt并 Accepted=true；测试入口强持实例直到所有迟到/资源断言结束，不以新的offer覆盖旧root。它仅证明进程内移交协议，真实耐久接收由宿主实现 |
| `DeliveryRequiredCases.RunAsync(ConfirmedRecoveryOwner receiver)` → `Task<int>` | 在同一Exe依§9.3逐case创建Memory/File fixture→端口→Reserve→Factory，执行Validate/Golden/重复不同摘要/Unknown/恢复/fence/取消/cleanup/重启及011～014。预先固定required ID集合，逐项完成记录；异常、超时、缺项、跳过或非零即非零，全部断言完成才0，不允许提供空实现 |
| `TestDeliveryTexts(string culture)`，实现 `Asun.Modules.DeliveryMigration.Wpf.IDeliveryTextProvider` | 仅UI Host工程提供；zh-CN/zh-TW/en-US表同key完整覆盖、未知culture/key拒绝；Delivery.Title分别为“部署更新”“部署更新”“Deployment”，CultureChanged只刷新投影 |

Memory/File 端口不能一律返回成功。它们必须按 context 核验 intent、epoch/fence、scope、有效预算、资源所有权和 CAS；Store 保存完整请求、Snapshot、intent、Journal及错误；RootRegistry 保存 acquire request、payload状态、control tombstone和新epoch。Trust从fixture SPKI建立golden-key-01、clock.UtcNow前后各1日有效期、rotation-1的快照；Memory可用空间1MiB，File从DriveInfo实测容量不足显式拒绝；Authorization只批准本fixture Module及测试身份的Prepare/Quiesce/Apply/Cancel/Recover/Cleanup/Resume，其它拒绝。MigrationRegistry只接受`schema.expand.v1`、`schema.reverse.v1`和schema-v1/precondition，不能执行manifest字符串。Quiesce维护关闭generation/队列计数；Storage维护schema/content/backup闭包和独立读回；Supervisor绑定选定slot/version/hash/readiness证据（每个必需check两个连续样本，固定profile/boot/epoch）；Audit只消费Store事实。AssertFinal从各独立端口核对活动slot/schema/旧数据、步骤计数、所有Task/输入句柄、payload/control lease和接纳generation，不能只读Core返回值。

固定包fixture：文件 `app/Host.exe` 内容 UTF-8 `abc`（3 bytes，SHA-256 `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`），rollback artifact `rollback/schema.bin` 同样3 bytes/hash。当前槽是Module `DELIVERY-TEST`/版本1.0.0/同一三字节文件hash作为合成当前manifest身份，已初始化且健康；目标1.1.0。两个文件都列在entries，按路径排序。Payload的8个字段按§3.3映射，migration包括 `requiresProcessRestart=true`、SnapshotRestore，以及唯一step `expand`/ordinal0/schema-v1/idempotent=true/Reversible/precondition `schema.at.1.0.0`/forward `schema.expand.v1`/reverse `schema.reverse.v1`/上述rollbackArtifactSha256。Reader/DataSchema=1.0.0，PreserveHistoricalRead=true、AllowForwardRepair=false。`SignedPackageFixture.Create()` 具体算法是：用BCL JsonSerializer创建上述固定ASCII/整数字段、按JCS属性ordinal顺序构造匿名对象并序列化（无缩进），对此受限fixture文本UTF-8求Payload hash → 用§3.3完整SignatureInput字段顺序生成固定ASCII签名输入 → RSA.SignData(SHA256,Pss) → Convert.ToBase64String → 拼入外层manifestSha256/signature。fixture只生成这一个固定数据对象，不实现通用JCS；受测Core仍独立用Jcs.Net验证，同样字段另含完整PayloadProjection Golden见§3.3。源Ref=`test-provider/package-1/revision-1`，所有流必须返回同一不可变快照。

测试限额构造无外部变量，数值只用于合成测试：

```csharp
static DeliveryRequest TestRequest(OperationId id, PackageSourceRef source)
{
    var profile = new DeliveryLimitProfileRef("test-limit", "1",
        new Sha256(new string('0', 64))); // 模拟授权Profile身份，不是生产Profile
    var limits = new DeliveryLimits(profile,
        TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1),
        TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1),
        TimeSpan.FromSeconds(2), new ByteCount(1024), new ByteCount(16384),
        16, new ByteCount(1024), 8, 4, 4, 1, 32, 1);
    return new DeliveryRequest(id, new ModuleId("DELIVERY-TEST"),
        new SemVersion(1, 1, 0, null), DeliveryMode.Upgrade, source,
        new CompatibilityPolicy(new SemVersion(1, 0, 0, null),
            new SemVersion(1, 0, 0, null), true, false),
        QuiesceMode.CloseAdmissionAndDrainAccepted, limits,
        UnknownSideEffectPolicy.QueryBeforeRetry, "test-maintainer", "test-correlation",
        new DateTimeOffset(2026, 10, 11, 0, 0, 0, TimeSpan.Zero));
}
static DeliveryRootOptions TestRootOptions() => new(1, TimeSpan.FromMilliseconds(200),
    TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1),
    TimeSpan.FromSeconds(3));
static DeliveryHostOptions TestHostOptions(string path) => new(
    Path.GetFullPath(path), "test-owner", new ByteCount(32768), TimeSpan.FromSeconds(10));
static void Require(bool condition, string caseId)
{
    if (!condition) throw new InvalidOperationException(caseId);
}
```

两个Host的完整构造函数调用规格（辅助方法和fixture/端口类型均在本节定义；本轮不声称已经编译）：

```csharp
static async Task<int> InMemoryRecoveryHost(DeliveryFault fault, ConfirmedRecoveryOwner receiver)
{
    var processRoot = new DeliveryProcessRoot(TimeProvider.System, TestRootOptions());
    receiver.TrackOriginRoot(processRoot);
    var path = Path.GetFullPath(Path.Combine(Path.GetTempPath(), "dm-memory-" + Guid.NewGuid().ToString("N")));
    var fixture = SignedPackageFixture.Create();
    var ports = new MemoryDeliveryPorts(fixture, path, processRoot.Clock, fault);
    var id = new OperationId(Guid.NewGuid());
    var slot = processRoot.Reserve(id, ports); // 转移端口生命周期，再构造Factory
    return await RunConstructedHost(processRoot, ports.Ports, slot,
        TestHostOptions(path), TestRequest(id, fixture.Source), fault,
        ports.AssertFinal, receiver);
}
static async Task<int> FileReplayHost(DeliveryFault fault, ConfirmedRecoveryOwner receiver)
{
    var processRoot = new DeliveryProcessRoot(TimeProvider.System, TestRootOptions());
    receiver.TrackOriginRoot(processRoot);
    var path = Path.GetFullPath(Path.Combine(Path.GetTempPath(), "dm-file-" + Guid.NewGuid().ToString("N")));
    Directory.CreateDirectory(path); // 本Host独占，可重建，仅合成fixture
    var fixture = SignedPackageFixture.Create();
    var ports = new FileDeliveryPorts(fixture, path, processRoot.Clock, fault);
    var id = new OperationId(Guid.NewGuid());
    var slot = processRoot.Reserve(id, ports);
    return await RunConstructedHost(processRoot, ports.Ports, slot,
        TestHostOptions(path), TestRequest(id, fixture.Source), fault,
        ports.AssertFinal, receiver);
}
static async Task<int> RunConstructedHost(DeliveryProcessRoot root, DeliveryPorts ports,
    DeliveryOwnerSlot slot, DeliveryHostOptions options, DeliveryRequest request,
    DeliveryFault fault, Action<bool> assertFinal, ConfirmedRecoveryOwner receiver)
{
    var code = 0;
    try
    {
        var delivery = DeliveryFactory.Create(root, slot, ports, options);
        Require(delivery.Validate(request).IsValid, "DM-CORE-VALIDATE-001");
        var first = await delivery.ExecuteAsync(request, null, CancellationToken.None)
            .WaitAsync(TimeSpan.FromSeconds(4));
        if (fault == DeliveryFault.VerifyFailsOnce)
        {
            Require(first.State == DeliveryState.Recovered,
                "DM-CORE-RECOVERY-005"); // 自动执行同manifest SnapshotRestore
            Require(first.Result is { Activated: false, HistoricalDataReadable: true },
                "DM-CORE-RECOVERY-005");
            assertFinal(true);
        }
        else
        {
            Require(first.State == DeliveryState.Completed && first.Result is { Activated: true },
                "DM-HOST-FILE-009");
            assertFinal(false);
        }
        var again = await delivery.ExecuteAsync(request, null, CancellationToken.None)
            .WaitAsync(TimeSpan.FromSeconds(1));
        Require(again.Sequence == first.Sequence && again.Result == first.Result,
            "DM-CORE-IDEMPOTENCY-003");
        var queried = await delivery.QueryAsync(slot.OperationId, CancellationToken.None)
            .WaitAsync(TimeSpan.FromSeconds(1));
        Require(queried?.Result == first.Result, "DM-HOST-RESTART-010");
    }
    catch (Exception ex)
    {
        System.Console.Error.WriteLine(ex); code = 2;
    }
    try
    {
        var closed = await root.CloseAsync(CancellationToken.None);
        if (!closed.Closed)
        {
            code = 3;
            var confirmed = await root.HandoffAsync(receiver, CancellationToken.None);
            Require(confirmed.Accepted && receiver.HeldRoot == root, "DM-CORE-CLEANUP-008");
        }
    }
    catch (Exception ex) { System.Console.Error.WriteLine(ex); code = 3; }
    return code; // 关闭后才返回，不能在try中return使清理失败退出码失效
}
static async Task<int> Main()
{
    var receiver = new ConfirmedRecoveryOwner("test-recovery-owner");
    var code = 0; // receiver在进程入口强持，绝不为移交成功返回0
    foreach (var fault in new[] { DeliveryFault.None, DeliveryFault.VerifyFailsOnce })
    {
        code = Math.Max(code, await InMemoryRecoveryHost(fault, receiver));
        code = Math.Max(code, await FileReplayHost(fault, receiver));
    }
    code = Math.Max(code, await DeliveryRequiredCases.RunAsync(receiver));
    return code;
}
```

Reserve前的构造异常路径：两个固定端口构造函数只创建局部资源，失败在构造器内有限释放未交出的流/密钥/handle再抛错；Fixture无持久资源。新建Root尚无slot，示例Reserve使用合法新ID/容量1，必定转移ports；专门的Reserve拒绝case创建者必须有界观察一次portLifetime.DisposeAsync，未知同样交给进程入口的资源Owner，不丢引用。Reserve成功后异常由RunConstructedHost统一Close处理。文件临时根只在关闭确认、引用/所有权核对后才可删除，本例保留用于失败读回。Guid仅隔离ID/目录，不影响Golden/故障顺序。

### 9.3 有限异常与重启断言

| case | 输入/动作/确定断言 |
|---|---|
| DM-CORE-UNKNOWN-004 | ApplyReplyLost：原apply提交一次，Execute返回RecoveryRequired/Result=null；恢复Owner通过ReconcileAsync查询原context（工作deadline已过也允许），Found后原协调任务继续同操作；apply调用/提交计数仍1；不得由Host直接调用适配器 |
| DM-CORE-CANCEL-007 | HoldApply：测试闩锁WaitForEnteredAsync(200ms)后取消waiter或Unbind；root.Inspect含原Task/输入；RequestCancel只登记请求，不能释放。ReleaseLatch后观察原Task，按SnapshotRestore收敛Recovered；Apply未开始分支为Cancelled |
| DM-CORE-CLEANUP-008 | CleanupReplyLost：Close在固定3s内Closed=false，Outstanding保留双错误轴和原资源；已提交释放只查原ID，不再次Dispose；确认receiver.HeldRoot先强持再Accepted。移交失败保留原Root引用。cleanup deadline已过时迟到不得自动新起cleanup |
| DM-CORE-FENCE-006 / DM-DEADLINE-011 | 固定BCL测试TimeProvider重写GetUtcNow/GetTimestamp/TimestampFrequency并以Advance闩锁推进，Work已过期新发送拒绝；原Query用200ms观察预算可Found；旧epoch只能追加历史观察不能写新资源；Resume scope拒绝staging/Apply |
| DM-RESUME-012 | Release payload成功后Resume仍用原控制fence，授权/兼容槽/readiness符合才打开同generation一次；授权吊销/应答Unknown不开放接纳。Authority release Unknown仅Close=false，不能倒改已提交终态 |
| DM-HOST-RESTART-010 | File端口关闭确认后新构造FileDeliveryPorts从保留root读取Store/intent/Journal/槽，new Root→Reserve原OperationId→Factory→Query原终态，不再Apply；进程崩溃模拟读取非终态时先查询旧action，未确认资源结束不能AcquireRecovery |
| DM-FACTORY-013 | null端口、非法根、零预算、slot重复绑定、容量满、不同操作ID：同步明确拒绝，无外部发送；Reserve已接纳的Lifetime只能Root释放一次 |
| DM-FORWARD-014 | 改用已签名Irreversible/ForwardRepair fixture、Apply中断：成功step不重放，剩余幂等step完成，选择目标1.1.0/schema匹配槽；断言旧1.0.0Select计数0；缺兼容槽→RecoveryFailed/隔离 |

以上未知/取消等case必须使用同§9.2完整构造路径，再操纵端口的显式测试闩锁或故障控制；不以sleep或字符串名字代替执行。Main明确调用DeliveryRequiredCases并保留退出码，必需case缺失不得返回0。每次source操作/观察/关闭均绑定该case固定有限预算，预算用尽后停止该case，不无限Query；恢复/迟到用显式闩锁触发。移交是保留Owner的错误出口而非测试通过，失败不清除输入/证据。

## 10. 可选 UI 契约

UI是可选独立程序集；批准范围包含可嵌入部署面板的展示与授权命令设计，不要求无UI宿主引用它。它复用同一IDeliveryService、校验器、权限和回执，布局与命令固定见§10.2，不留给实现者重新设计。阶段时间线、版本/hash、恢复点、阻断原因和一个下一安全动作始终可见，高级步骤渐进展开。

UI 必须支持 `zh-CN`、`zh-TW`、`en-US`，所有文字来自宿主资源；不在模块重复提供语言切换入口。普通操作员只能查看进度、错误和恢复建议；执行、恢复、保留策略和清理操作由运维权限控制。控件关闭、切页或旧请求超时只停止订阅，不取消核心操作；旧事件不得覆盖新 `OperationId` 的投影。键盘、UIA、DPI 和 1920x1080 基线由宿主验收。

### 10.1 UI Session、绑定和两个 STA Host

UI 适配器必须把 Core 投影为可解绑的 `DeliverySession`，而不是把 ViewModel 变成第二状态 Owner：

```csharp
public sealed record DeliverySessionKey(string SessionId, OperationId OperationId,
    string ConsumerId, long BoundEpoch);
public sealed record DeliverySessionSnapshot(DeliverySessionKey Key,
    DeliveryOperationSnapshot Snapshot, bool Bound, bool CanUnbind,
    DeliveryOperationDetails? Details = null);
public sealed record DeliverySessionEvent(DeliverySessionKey Key, DeliveryEvent Event);
public interface IDeliverySessionBinding : IAsyncDisposable
{
    DeliverySessionSnapshot Current { get; }
    event EventHandler<DeliverySessionEvent>? EventReceived;
    ValueTask UnbindAsync(CancellationToken ct);
}
```

具体公开Bind构造签名，namespace `Asun.Modules.DeliveryMigration`；SessionFactory是无WPF的Core投影，外部SynchronizationContext显式注入，不初始化窗口：

```text
public sealed class DeliverySessionFactory
  public DeliverySessionFactory(DeliveryProcessRoot root, IDeliveryService service, SynchronizationContext deliveryContext, TimeSpan pollInterval, TimeSpan observationBudget)
  public Task<IDeliverySessionBinding> BindAsync(DeliverySessionKey key, CancellationToken ct)
```

构造同步验证非空、service属于root及正有限预算，使用root.Clock；Root强持factory/binding及每个Query/timer Task，直到解绑与查询真结束，不能端口已Dispose后继续poll。每个slot最多一个活跃/未排空binding，前一Unbind查询未结束时新Bind返回SESSION_RESOURCE_BUSY，不无界积压。Bind先在observationBudget内Query原OperationId，未知ID返回SESSION_OPERATION_NOT_FOUND，epoch不匹配返回SESSION_EPOCH_MISMATCH且不创建timer；成功后读ReadDetailsAsync并确认同一sequence，在observationBudget内最多3次配对重读，仍不一致拒绝SESSION_RESOURCE_BUSY；捕获当前sequence再建立有界单flight轮询（pollInterval只决定频率，不续期source action）。每次Query有独立观察预算，失败保留原投影并显示诊断；事件仅来自Snapshot.DurableEvents且sequence去重。DeliverySessionEvent.Key给出session身份、Event.Epoch给出事实epoch；UI消费前检查SessionId/OperationId/BoundEpoch/Bound generation，已解绑或旧epoch的post丢弃。最多1个poll Task/1个待投递投影，连续事实由耐久Query补全。

Unbind同步先令Bound=false/advance generation，停止新poll/post，再在observationBudget内观察当前Query结束；超时抛TimeoutException（不能成功返回暗藏未结束查询），旧post无权改UI，Root强持查询/timer至真结束，Close不得提前Dispose它们借用的端口。DisposeAsync幂等观察同一Unbind Task，不启动清理。Bind不能调用Execute/Cancel/Recover；关闭窗口只Unbind。重开新SessionId，从Query读事实；恢复命令走同一Core API。Retain/Remove独立公开入口现已在§6.7冻结，面板经§10.2命令端口调用，不能直写文件。

可选WPF独立程序集 `src/Modules/delivery-migration/Asun.Modules.DeliveryMigration.Wpf/Asun.Modules.DeliveryMigration.Wpf.csproj`、namespace `Asun.Modules.DeliveryMigration.Wpf`（net10.0-windows/UseWPF；本机DevExpress25.2.3引用），具体公开构造为：

```text
public interface IDeliveryTextProvider
  string CultureName { get; }
  string Get(string key)
  event EventHandler? CultureChanged
public sealed class DeliveryPanel : System.Windows.Controls.UserControl
  public DeliveryPanel(IDeliverySessionBinding binding, IDeliveryTextProvider texts)
```

原双参数Panel构造保持只读展示；§10.2新增三参数命令构造，使用同binding与显式命令端口。CultureChanged重读同一资源键，无语言入口。测试TestDeliveryTexts在唯一WPF Host工程构造，覆盖§10.1/10.2完整key表，缺key失败；模块提供三语默认资源，宿主可按相同key覆盖，Core不携带翻译。以下原两个STA Host构造保持有效，命令Host窄接线见§10.2：

```csharp
static async Task<int> DeliveryStationStaHost(ConfirmedRecoveryOwner receiver)
{
    var root = new DeliveryProcessRoot(TimeProvider.System, TestRootOptions());
    receiver.TrackOriginRoot(root);
    try
    {
    var path = Path.GetFullPath(Path.Combine(Path.GetTempPath(), "dm-station-" + Guid.NewGuid().ToString("N")));
    var fixture = SignedPackageFixture.Create();
    var ports = new MemoryDeliveryPorts(fixture, path, root.Clock, DeliveryFault.None);
    var id = new OperationId(Guid.NewGuid());
    var slot = root.Reserve(id, ports);
    var service = DeliveryFactory.Create(root, slot, ports.Ports, TestHostOptions(path));
    var texts = new TestDeliveryTexts("zh-CN");
    return await RunStaBinding(root, service, TestRequest(id, fixture.Source), texts, ports.Ports.Authorization,
        "station", receiver);
    }
    catch (Exception ex)
    {
        System.Console.Error.WriteLine(ex);
        return await FailStaConstruction(root, receiver);
    }
}
static async Task<int> DeliveryToolStaHost(ConfirmedRecoveryOwner receiver)
{
    var root = new DeliveryProcessRoot(TimeProvider.System, TestRootOptions());
    receiver.TrackOriginRoot(root);
    try
    {
    var path = Path.GetFullPath(Path.Combine(Path.GetTempPath(), "dm-tool-" + Guid.NewGuid().ToString("N")));
    Directory.CreateDirectory(path);
    var fixture = SignedPackageFixture.Create();
    var ports = new FileDeliveryPorts(fixture, path, root.Clock, DeliveryFault.VerifyFailsOnce);
    var id = new OperationId(Guid.NewGuid());
    var slot = root.Reserve(id, ports);
    var service = DeliveryFactory.Create(root, slot, ports.Ports, TestHostOptions(path));
    var texts = new TestDeliveryTexts("en-US");
    return await RunStaBinding(root, service, TestRequest(id, fixture.Source), texts, ports.Ports.Authorization,
        "tool", receiver);
    }
    catch (Exception ex)
    {
        System.Console.Error.WriteLine(ex);
        return await FailStaConstruction(root, receiver);
    }
}
static async Task<int> FailStaConstruction(DeliveryProcessRoot root, ConfirmedRecoveryOwner receiver)
{
    try
    {
        var close = await root.CloseAsync(CancellationToken.None);
        if (!close.Closed) await root.HandoffAsync(receiver, CancellationToken.None);
    }
    catch (Exception ex) { System.Console.Error.WriteLine(ex); }
    return 3; // 已记录异常，移交/关闭都不能把构造失败变成功
}
static async Task<int> RunStaBinding(DeliveryProcessRoot root, IDeliveryService service,
    DeliveryRequest request, TestDeliveryTexts texts, IDeliveryAuthorizationPort authorization, string consumer,
    ConfirmedRecoveryOwner receiver)
{
    var code = 0;
    IDeliverySessionBinding? binding = null;
    try
    {
        var current = await service.ExecuteAsync(request, null, CancellationToken.None)
            .WaitAsync(TimeSpan.FromSeconds(4));
        var context = new System.Windows.Threading.DispatcherSynchronizationContext(
            System.Windows.Threading.Dispatcher.CurrentDispatcher);
        var sessions = new DeliverySessionFactory(root, service, context,
            TimeSpan.FromMilliseconds(100), TimeSpan.FromMilliseconds(200));
        var key = new DeliverySessionKey(Guid.NewGuid().ToString("N"),
            request.OperationId, consumer, current.Epoch);
        binding = await sessions.BindAsync(key, CancellationToken.None);
        var commands = new DeliveryPanelCommands(root, service, binding, request, authorization,
            null, TimeSpan.FromMilliseconds(200)); // Retention未配置，明确NOT_CONFIGURED
        var panel = new Asun.Modules.DeliveryMigration.Wpf.DeliveryPanel(binding, texts, commands);
        var window = new System.Windows.Window { Title = texts.Get("Delivery.Title"), Content = panel };
        window.Width = Math.Min(1920, System.Windows.SystemParameters.WorkArea.Width);
        window.Height = Math.Min(1080, System.Windows.SystemParameters.WorkArea.Height);
        window.Show();
        Require(binding.Current.Bound, "DM-UI-BIND-015");
        await binding.UnbindAsync(CancellationToken.None);
        window.Close();
        var after = await service.QueryAsync(request.OperationId, CancellationToken.None)
            .WaitAsync(TimeSpan.FromMilliseconds(200));
        Require(after?.Sequence == current.Sequence, "DM-UI-BIND-015");
        // 在同一sessions上以新SessionId重绑，Query重建当前事实。
        var rebound = await sessions.BindAsync(key with { SessionId = Guid.NewGuid().ToString("N") },
            CancellationToken.None);
        await rebound.UnbindAsync(CancellationToken.None);
        await rebound.DisposeAsync();
    }
    catch (Exception ex) { System.Console.Error.WriteLine(ex); code = 2; }
    try
    {
        if (binding is not null) await binding.DisposeAsync();
        var closed = await root.CloseAsync(CancellationToken.None);
        if (!closed.Closed)
        {
            code = 3;
            var accepted = await root.HandoffAsync(receiver, CancellationToken.None);
            Require(accepted.Accepted && receiver.HeldRoot == root, "DM-CORE-CLEANUP-008");
        }
    }
    catch (Exception ex) { System.Console.Error.WriteLine(ex); code = 3; }
    return code;
}
```

以上是完整接线/解绑规格，不代表窗口已运行验收。STA Test入口必须在进程根强持Root/Receiver集合，创建两个独立STA线程并显式 `SetApartmentState(ApartmentState.STA)`，各自运行Dispatcher；不能在UI Host局部离栈后丢失未确认Owner。WPF进程只有一个Application，由入口创建；第二Host复用该Application但使用独立Dispatcher/Window。入口通过完成信号收集各Host的返回码并有15s总截止，catch、线程异常和超时均非零，不在锁内等待Dispatcher。1920×1080固定验证视口由测试入口定位，WorkArea扣除taskbar/边框/标题后窗体内容不越界，不改变显示设置。另以HoldApply闩锁绑定在途snapshot→关窗→取消waiter→迟到完成→重新Query，断言输入由Root强持、Unbind后旧事件不改新session；每种三语/键盘/UIA/提示联动在两个Host复用同一assertion。唯一UI测试工程为 `tests/Modules/delivery-migration/Asun.Modules.DeliveryMigration.Wpf.HostTests/Asun.Modules.DeliveryMigration.Wpf.HostTests.csproj`，只在UI切片获准时创建，Core.Tests仍无WPF引用。

两个 UI Host 都在独立 STA 线程构造并使用同一 Session/端口契约：

- `DeliveryStationStaHost`：机台宿主投影版本变更、排空、进度、readiness、错误和恢复；设备安全停机、PLC/运动互锁、实际服务启动和现场凭据由宿主外部门提供，控件只显示其回执。
- `DeliveryToolStaHost`：独立工程/离线工具投影 Validate、包/依赖树、历史操作查询、备份闭包和 Recover；它使用复制数据与受控文件根，没有设备命令权限，关闭/重开不改变 Core。

按 DevExpress 25.2 WPF API 页面核对的控件组合：主工作区用 `DockLayoutManager` 分成阶段/操作树、详情和诊断停靠区；操作/迁移步骤用 `GridControl` + `TreeListView`（官方声明可显示层级数据并支持排序、过滤、摘要和验证，见 [TreeListView v25.2](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TreeListView?v=25.2)）；Profile/权限/兼容性只读项用 `PropertyGridControl`；未知副作用、清理移交和回退确认用 `FlyoutControl`，非显然字段用本地化 `SuperTip`。这些控件只承载投影，不能以绑定 setter 绕过 Core 校验。

1920×1080 窗口中，顶部为模块/源→目标版本、manifest hash 和当前安全状态；左侧为可折叠操作/step 树；中部为阶段进度和每阶段耗时/重试/Journal 序号；右侧为恢复点、当前槽、readiness 证据和资源归还；底部固定一条下一安全动作。Apply/Recover/删除/保留等破坏性或不可逆命令只能在与状态匹配的 `FlyoutControl` 中显示影响范围、OperationId、ActionId、备份/ForwardRepair 路线和确认移交 Owner。键盘顺序固定为导航树→详情→主命令→诊断；`Esc` 关闭 Flyout 不取消 source Task，`Ctrl+L` 聚焦操作检索，`Ctrl+R` 重新 Query；UIA 名称、状态和错误码来自同一资源键。长版本、路径和错误详情使用省略显示加复制/展开，不把完整 hash 截断为唯一证据。

三语资源至少覆盖按钮、状态、阶段、错误、恢复动作、权限拒绝、Unknown/RecoveryRequired、清理移交和未初始化目标；文本短而直接。UI 性能只测投影/Query/事件批处理，不将界面动画或截图存在当作交付性能；WPF、DevExpress 25.2.3 实际编译、两个 STA Host、UIA、键盘、DPI 和现场工作流均为后续 UI 门，未完成时不阻断纯 Core。

### 10.2 完整面板、授权命令与三语交互

面板范围为部署操作导航/步骤、当前与目标版本、配置数据/恢复点、签名信任、进度/错误/资源归还、原动作查询及受权维护命令；无图像画布/ROI/模型预览，不直接消费viewport，不为“影像优先”规则制造无用途图像区。1920×1080单一验证视口内，四周16 DIP、区间8 DIP；顶栏64 DIP显示模块/版本/完整hash的复制入口，底栏48 DIP常驻状态/下一安全动作；中部左约24%操作与步骤树，中约50%详情/时间线，右约26%恢复/授权/资源诊断。Dock允许在内容区域调整比例，底栏关键命令不随停靠隐藏；最小内容区不足时详情滚动，高级PropertyGrid折叠，不压缩文字/遮挡命令。主题继承宿主，字号/图标/焦点色使用既有DEV-UI-040资源；状态同时用文字与图标，不仅颜色。新Snapshot在Dispatcher一次提交树/详情/命令状态，按sequence增量保留选择，不用动画暗示尚未耐久的成功。

实际DevExpress组合冻结为DockLayoutManager→LayoutGroup/三个LayoutPanel，树为GridControl+TreeListView（KeyFieldName=NodeId、ParentFieldName=ParentId，根ParentId=null），SelectedItem联动详情/只读PropertyGridControl.SelectedObject；确认FlyoutControl显示原动作/影响/恢复策略，普通命令仍在固定底栏可见。本轮dxdocs MCP不可用且在线文档403，定向读取本机`C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/`的Docking/Grid/Grid.Core/Core/PropertyGrid官方XML：确认Flyout实际CLR类型为`DevExpress.Xpf.Editors.Flyout.FlyoutControl`，IsOpen/PlacementTarget继承FlyoutBase，ItemsSource/SelectedItem在DataControlBase，SuperTip/布局项/PropertyGrid为上述实际公共API。依赖直接使用25.2.3，未做安装/授权审查；此查阅不是WPF运行资格。

以下为实现布局的XAML规格骨架（绑定属性由下文Panel投影内部实现，不是新的公开ViewModel API；实际编译留运行门）：

```xml
<UserControl xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
 xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
 xmlns:dxd="http://schemas.devexpress.com/winfx/2008/xaml/docking"
 xmlns:dxg="http://schemas.devexpress.com/winfx/2008/xaml/grid"
 xmlns:dxpg="http://schemas.devexpress.com/winfx/2008/xaml/propertygrid"
 xmlns:dxf="clr-namespace:DevExpress.Xpf.Editors.Flyout;assembly=DevExpress.Xpf.Core.v25.2">
 <Grid Margin="16">
  <Grid.RowDefinitions><RowDefinition Height="64"/><RowDefinition Height="*"/><RowDefinition Height="48"/></Grid.RowDefinitions>
  <TextBlock Text="{Binding Header}" TextWrapping="Wrap"/>
  <dxd:DockLayoutManager Grid.Row="1">
   <dxd:LayoutGroup Orientation="Horizontal">
    <dxd:LayoutPanel Caption="{Binding Texts.Operations}" ItemWidth="24*">
     <dxg:GridControl ItemsSource="{Binding Nodes}" SelectedItem="{Binding SelectedNode}">
      <dxg:GridControl.View><dxg:TreeListView KeyFieldName="NodeId" ParentFieldName="ParentId"/></dxg:GridControl.View>
     </dxg:GridControl>
    </dxd:LayoutPanel>
    <dxd:LayoutPanel Caption="{Binding Texts.Details}" ItemWidth="50*">
     <ScrollViewer><TextBlock Text="{Binding SelectedDetail}" TextWrapping="Wrap"/></ScrollViewer>
    </dxd:LayoutPanel>
    <dxd:LayoutPanel Caption="{Binding Texts.Recovery}" ItemWidth="26*">
     <dxpg:PropertyGridControl SelectedObject="{Binding ReadOnlyRecovery}"/>
    </dxd:LayoutPanel>
   </dxd:LayoutGroup>
  </dxd:DockLayoutManager>
  <StackPanel Grid.Row="2" Orientation="Horizontal">
   <TextBlock Text="{Binding Status}" VerticalAlignment="Center"/>
   <Button x:Name="NextAction" Content="{Binding NextActionText}" Command="{Binding NextActionCommand}"/>
  </StackPanel>
  <dxf:FlyoutControl IsOpen="{Binding ConfirmationOpen}" PlacementTarget="{Binding ElementName=NextAction}">
   <ContentControl Content="{Binding Confirmation}"/>
  </dxf:FlyoutControl>
 </Grid>
</UserControl>
```

PropertyGrid展示对象仅有只读属性且不是业务DTO原对象；树Grid列只读、禁编辑处理器。底栏命令采用DevExpress.Xpf.Bars.BarButtonItem（对应BarItem.SuperTip为已核实公开属性），构造`new SuperTip()`、`tip.Items.Add(new SuperTipItem { Content = texts.Get(key) })`后赋给item.SuperTip；原XAML Button是布局骨架，真实命令栏按此BarItem映射，不将非Visual的SuperTip当任意WPF ToolTip内容。字段帮助以文本ToolTip与同key短句展示。每个图标有AutomationProperties.Name/HelpText、稳定AutomationId；Esc只关闭Flyout，Ctrl+L检索树、Ctrl+R刷新Query，Tab导航树→详情→恢复→底栏，Enter只执行已授权聚焦命令，删除/恢复需要确认，不绑定单键Delete。三语切换重建文本/Automation名称，保留OperationId/选择/CommandId，不触发新请求。

保留原双参Panel只读构造，新增公开构造`DeliveryPanel(IDeliverySessionBinding binding, IDeliveryTextProvider texts, IDeliveryPanelCommands commands)`。命令端口定义在Core，Panel消费同一binding，不取得私有Store/文件路径：

```csharp
public enum DeliveryPanelCommandKind { Refresh, Cancel, Reconcile, Recover, Cleanup, Retain }
public sealed record DeliveryPanelCommandIntent(string CommandId, DeliverySessionKey Session,
    long ExpectedSequence, DeliveryPanelCommandKind Kind,
    RecoveryCommand? Recovery, DeliveryCleanupCommand? Cleanup,
    DeliveryRetentionRequest? Retention, bool Confirmed);
public sealed record DeliveryPanelPermission(DeliveryPanelCommandKind Kind, bool Allowed,
    string? DenialCode, string DecisionId, DateTimeOffset EvaluatedAtUtc);
public sealed record DeliveryPanelCommandReceipt(string CommandId,
    DeliveryOperationSnapshot? Snapshot, DeliveryRetentionReceipt? Retention,
    string? ErrorCode, bool ObservationPending);
public interface IDeliveryPanelCommands
{
    Task<IReadOnlyList<DeliveryPanelPermission>> QueryPermissionsAsync(CancellationToken ct);
    Task<DeliveryPanelCommandReceipt> ExecuteAsync(DeliveryPanelCommandIntent intent, CancellationToken ct);
    Task<DeliveryPanelCommandReceipt?> QueryAsync(string commandId, CancellationToken ct);
}
```

具体类构造`DeliveryPanelCommands(DeliveryProcessRoot root, IDeliveryService service, IDeliverySessionBinding binding, DeliveryRequest frozenRequest, IDeliveryAuthorizationPort authorization, IDeliveryRetentionService? retention, TimeSpan observationBudget)`，无WPF引用。冻结请求必须与binding.OperationId相同，service属于root；root强持controller/原命令Task，同slot最多一个写命令在途，关闭Panel只Unbind，controller不Dispose service。宿主正常接线在Bind之后`new DeliveryPanelCommands(root, service, binding, request, ports.Authorization, retentionService, TimeSpan.FromMilliseconds(200))`→三参Panel；两个§10.1 STA Host均追加此接线（其原`request`在RunStaBinding参数中、ports通过Factory已知Authorization参数显式传入），Retention未装配时返回NOT_CONFIGURED而不冒称已执行。§6.7 retentionService构造独立maintenance槽，原操作的Retain意图经其自己的authorityRequest/新OperationId执行；不得为旧已释放Root再借已撤销fence。

命令算法：验证CommandId非空、同Session/epoch、binding仍Bound、写命令的期望sequence与最新Query一致；不符SESSION_EPOCH_MISMATCH/STALE_COMMAND且无副作用。Refresh/Reconcile仍校验Session/epoch，但不因旧sequence拒绝读取新事实。按Kind检查恰一个对应可选payload，其余null；Recover/Cleanup/Retain必需Confirmed且带具体原Action/Backup/Policy身份。Refresh→service.QueryAsync；Reconcile→service.ReconcileAsync；Cancel→RequestCancelAsync；Recover→RecoverAsync；Cleanup→RequestCleanupAsync；Retain→retention.ExecuteAsync。QueryPermissions只投影当前授权，不缓存为执行许可；Execute重新Authorize（Cancel/Recover/Cleanup/Retain对应DeliveryAction，Refresh/Reconcile仅需宿主授予该操作的读取权限）。只读权限由消费者已认证会话限制可绑定的OperationId，模块不自动提升Reader。Core命令仍再次检查状态/权限，所以按钮Allowed不会绕过Core。

同CommandId同完整intent返回原Task/receipt；不同输入COMMAND_CONFLICT。开始发送前Root登记完整意图和Task；waiter取消/超时返回ObservationPending而不删除映射，随后QueryCommand读原Task状态并用原service/retention Query查询原动作，不创建新ActionId。新进程重开只使用耐久OperationId/ActionId调用Core Query/Reconcile，UI CommandId不是新的事实主键；不重放窗口上次按钮点击。Execute确定完成/失败或ObservationPending都返回结构receipt，原OperationError/CleanupError仍保留；异常文本仅诊断，UI显示资源键及允许的下一安全动作。RecoveryRequired/RecoveryFailed只显示Query/Reconcile及满足前置的恢复，Cancelled/Completed不显示Apply/Recover；Cancel不等于立即终止。面板不提供直接Execute升级入口，宿主在选择并批准签名包后按原公开Execute启动并Bind，防止控件代产品决定升级范围。

模块默认资源最小固定词表如下；所有阶段/枚举状态使用`Delivery.State.<枚举名>`，错误使用`Delivery.Error.<本地码>`，未映射key在验证时失败，运行回退为原code+该语言“查看诊断”而非空文案。完整错误语义取§8，状态动作取§4～7，不重新解释Unknown为失败或成功。

| key后缀 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Title / Operations | 部署更新 / 操作 | 部署更新 / 操作 | Deployment / Operations |
| Details / Recovery | 详情 / 恢复 | 詳情 / 復原 | Details / Recovery |
| Refresh / Reconcile | 刷新 / 查询原动作 | 重新整理 / 查詢原動作 | Refresh / Check original action |
| Cancel / Recover | 请求取消 / 恢复 | 要求取消 / 復原 | Request cancellation / Recover |
| Cleanup / Retain / Remove | 清理 / 保留 / 删除 | 清理 / 保留 / 刪除 | Clean up / Keep / Remove |
| Confirm / Back | 确认 / 返回 | 確認 / 返回 | Confirm / Back |
| State.RecoveryRequired | 需要恢复；接纳已关闭 | 需要復原；接納已關閉 | Recovery required; admission closed |
| State.RecoveryFailed | 恢复失败；保持隔离 | 復原失敗；保持隔離 | Recovery failed; isolation retained |
| Pending / Released | 等待原动作回执 / 资源已归还 | 等待原動作回執 / 資源已歸還 | Waiting for original receipt / Resources returned |
| Tip.Cancel | 仅请求安全停止。关闭窗口不会停止迁移。 | 僅要求安全停止。關閉視窗不會停止遷移。 | Requests a safe stop. Closing the window does not stop migration. |
| Tip.ForwardRepair | 数据已向前变更。仅使用兼容目标版本。 | 資料已向前變更。僅使用相容目標版本。 | Data has changed. Use a compatible target release. |
| Tip.Cleanup | 原任务结束且资源身份已确认后才可清理。 | 原工作結束且資源身分已確認後才可清理。 | Clean up only after the original task ends and resources are confirmed. |
| Denied / Diagnostics | 无操作权限 / 查看诊断 | 無操作權限 / 檢視診斷 | Permission denied / View diagnostics |

默认文本覆盖全部用户可见错误、状态、提示和权限，不能把表中未逐项列出的枚举名直接当英文UI。实现资源时以§8每个码的“发生/影响/下一动作”各语短句填入对应key，资格断言逐码检查三语非空且没有串为另一语言；这属于本模块资源制作，不是客户领域决定。错误Detail路径/credentials脱敏，hash可复制完整值，超长路径在展开区显示。初版无自动参数/AI：限额及保留策略来自明确批准Profile，推荐只给确定的缺项/容量差值，不提供未经资格的自动修改。

补充验收`DM-UI-CMD-016`：两个STA Host分别构造只读/运维授权controller，验证相同binding下选中步骤联动、动态三语、键盘/UIA/1920×1080；未经确认或权限过期的Recover/Remove发送数0，重复CommandId发送1、不同输入拒绝；Cancel waiter/Unbind后原Task仍由Root持有，晚到receipt不覆盖新Session；Retention缺配置明确NOT_CONFIGURED。两个Host共用同一Core与策略测试，不以XAML存在代替真实WPF通过。

下一安全动作是确定投影，不由控件猜恢复方案：UnknownActionId非空→Reconcile；cleanup error且所有原Task已结束/允许清理→Cleanup，否则Reconcile；RecoveryFailed或RecoveryRequired且Unknown已排除、details.Backup验证有效且manifest=SnapshotRestore→Recover（BackupId取details原值）；ForwardRepair仅在AllowForwardRepair和Registry前置已确认时显示Recover、BackupId=null；缺条件→Refresh+诊断。Applying/Quiescing等可请求安全停止的在途状态显示Cancel，Draining/Resuming等收敛中状态显示Refresh；终态显示Refresh，维护Retain/Remove放高级区且权限/保护状态始终可见。用户确认Flyout只确认已有路线/身份/影响，不提供让操作员猜选SnapshotRestore/ForwardRepair的自由下拉框。StepReceipt.Outcome固定Succeeded或Failed，未知保持无receipt+UnknownActionId；成功步骤BeforeHash/AfterHash由原scope登记的确定性内容快照摘要给出，不能将字符串“OK”当摘要。

### 10.3 全状态与错误默认资源

表中状态键使用Delivery.State.前缀；命令Busy/Pending为UI观察，不写入DeliveryState。每行三语为模块默认值，宿主覆盖不得改变状态语义。阶段ordinal、版本、hash、字节等动态数据分别绑定，不拼接成难以本地化的句子。

| 状态后缀 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Requested | 已请求 | 已要求 | Requested |
| Validating | 正在校验 | 正在驗證 | Validating |
| Prepared | 包已就绪 | 套件已就緒 | Package ready |
| Quiescing | 正在关闭接纳 | 正在關閉接納 | Closing admission |
| Quiesced | 接纳已关闭 | 接納已關閉 | Admission closed |
| BackingUp | 正在备份 | 正在備份 | Backing up |
| BackupVerified | 备份已验证 | 備份已驗證 | Backup verified |
| Applying | 正在迁移 | 正在遷移 | Applying migration |
| Applied | 迁移已应用 | 遷移已套用 | Migration applied |
| PartiallyApplied | 迁移部分完成 | 遷移部分完成 | Migration partially applied |
| Verifying | 正在读回验证 | 正在讀回驗證 | Verifying readback |
| Verified | 读回已验证 | 讀回已驗證 | Readback verified |
| Activating | 正在激活版本 | 正在啟用版本 | Activating release |
| SupervisorStopping | 正在停止原进程 | 正在停止原處理程序 | Stopping previous process |
| SupervisorStopped | 原进程已停止 | 原處理程序已停止 | Previous process stopped |
| VersionSelecting | 正在选择版本 | 正在選擇版本 | Selecting release |
| VersionSelected | 版本已选择 | 版本已選擇 | Release selected |
| SupervisorStarting | 正在启动进程 | 正在啟動處理程序 | Starting process |
| SupervisorStarted | 进程已启动 | 處理程序已啟動 | Process started |
| ReadinessVerified | 运行就绪已验证 | 執行就緒已驗證 | Readiness verified |
| Resuming | 正在恢复接纳 | 正在恢復接納 | Resuming admission |
| Resumed | 接纳已恢复 | 接納已恢復 | Admission resumed |
| Completed | 更新完成 | 更新完成 | Update completed |
| CancelRequested | 已请求取消 | 已要求取消 | Cancellation requested |
| Draining | 正在排空原任务 | 正在排空原工作 | Draining original tasks |
| Drained | 原任务已排空 | 原工作已排空 | Original tasks drained |
| ResourcesReleased | 迁移资源已归还 | 遷移資源已歸還 | Migration resources returned |
| Cancelled | 已取消 | 已取消 | Cancelled |
| RecoveryRequired | 需要恢复；接纳已关闭 | 需要復原；接納已關閉 | Recovery required; admission closed |
| Recovering | 正在恢复 | 正在復原 | Recovering |
| Recovered | 恢复完成 | 復原完成 | Recovery completed |
| RecoveryFailed | 恢复失败；保持隔离 | 復原失敗；保持隔離 | Recovery failed; isolation retained |
| Rejected | 请求已拒绝 | 要求已拒絕 | Request rejected |
| Failed | 更新失败 | 更新失敗 | Update failed |

错误键使用Delivery.Error.前缀；同一行多个码共享说明，但code仍逐项注册/显示，不靠正则猜语义。异常Detail在诊断区另显，默认信息包含影响或下一动作；原动作/未释放资源/Owner的精确值来自双错误轴，不写死在翻译中。

| 本地码 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| INVALID_REQUEST | 请求无效。修正输入后重试。 | 要求無效。修正輸入後重試。 | Invalid request. Correct the input. |
| PACKAGE_HASH_MISMATCH, SIGNATURE_INVALID | 包验证失败。重新取得受信签名包。 | 套件驗證失敗。重新取得可信簽章套件。 | Package verification failed. Obtain a trusted signed package. |
| PACKAGE_TRUNCATED | 包不完整。重新取得原包。 | 套件不完整。重新取得原套件。 | Package is incomplete. Obtain the original package again. |
| PACKAGE_TOO_LARGE, TOO_MANY_STEPS | 超出批准限额。使用符合限额的包。 | 超出核准限制。使用符合限制的套件。 | Approved limit exceeded. Use a package within the limit. |
| DEPENDENCY_INCOMPATIBLE, AMBIGUOUS_COMPATIBILITY | 版本不兼容或关系不明确。核对兼容计划。 | 版本不相容或關係不明。核對相容計畫。 | Versions are incompatible or ambiguous. Check the compatibility plan. |
| COLD_TARGET_NOT_INITIALIZED | 目标尚未初始化。先完成基线安装。 | 目標尚未初始化。先完成基準安裝。 | Target is not initialized. Complete baseline installation first. |
| INSUFFICIENT_SPACE, RESOURCE_EXHAUSTED | 资源不足。保留原版本，核对可用资源。 | 資源不足。保留原版本，核對可用資源。 | Insufficient resources. Keep the current release and check available resources. |
| RESOURCE_BUSY, QUEUE_FULL, SESSION_RESOURCE_BUSY | 资源仍在使用。等待原任务归还。 | 資源仍在使用。等待原工作歸還。 | Resources are still in use. Wait for the original task to return them. |
| QUIESCE_TIMEOUT, DRAIN_TIMEOUT | 排空未确认。保持隔离并查询原任务。 | 排空未確認。保持隔離並查詢原工作。 | Drain is unconfirmed. Keep isolation and query the original task. |
| BACKUP_UNVERIFIED, BACKUP_CLOSURE_INCOMPLETE, RESTORE_DRILL_FAILED | 恢复点未验证。禁止迁移，核对备份闭包。 | 復原點未驗證。禁止遷移，核對備份閉包。 | Recovery point is unverified. Do not migrate; check the backup closure. |
| MIGRATION_STEP_FAILED, VERIFY_FAILED | 迁移或读回失败。按原计划恢复。 | 遷移或讀回失敗。依原計畫復原。 | Migration or readback failed. Recover using the original plan. |
| READINESS_EVIDENCE_INVALID, READINESS_TIMEOUT | 运行就绪未确认。查询原进程回执。 | 執行就緒未確認。查詢原處理程序回執。 | Readiness is unconfirmed. Query the original process receipt. |
| UNKNOWN_SIDE_EFFECT | 原动作结果未知。先查询，不要重发。 | 原動作結果未知。先查詢，不要重送。 | Original action outcome is unknown. Query before sending again. |
| DUPLICATE_OPERATION_ID, ACTION_INPUT_CONFLICT, COMMAND_CONFLICT | 原身份与输入冲突。核对原请求。 | 原身分與輸入衝突。核對原要求。 | Identity conflicts with the input. Check the original request. |
| RECOVERY_FAILED | 恢复失败。保持隔离并移交恢复负责人。 | 復原失敗。保持隔離並移交復原負責人。 | Recovery failed. Keep isolation and hand off to the recovery owner. |
| STALE_FENCE, SESSION_EPOCH_MISMATCH, STALE_COMMAND | 操作代已变化。刷新原操作，禁止重发旧动作。 | 操作代已變更。重新整理原操作，禁止重送舊動作。 | Operation epoch changed. Refresh; do not resend the old action. |
| DEADLINE_EXPIRED | 动作已超时。查询原回执并保留资源。 | 動作已逾時。查詢原回執並保留資源。 | Action deadline expired. Query the original receipt and retain resources. |
| SESSION_OPERATION_NOT_FOUND | 未找到操作。核对操作编号。 | 找不到操作。核對操作編號。 | Operation was not found. Check the operation ID. |
| STORE_CORRUPT, RECEIPT_CORRUPT | 持久记录校验失败。保持隔离并检查存储。 | 持久記錄驗證失敗。保持隔離並檢查儲存。 | Durable record verification failed. Keep isolation and inspect storage. |
| NOT_CONFIGURED | 此宿主未配置该能力。联系维护负责人。 | 此宿主未設定此功能。聯絡維護負責人。 | This host has not configured this capability. Contact the maintenance owner. |
| ARTIFACT_PROTECTED, ARTIFACT_CONTENT_CHANGED, RETENTION_CONFLICT | 资产被引用或已变化。保留资产并刷新状态。 | 資產被引用或已變更。保留資產並重新整理狀態。 | Artifact is referenced or changed. Keep it and refresh the state. |
| AUTHORIZATION_DENIED, AUDIT_UNAVAILABLE | 权限或审计不可用。停止新写入并核对授权。 | 權限或稽核無法使用。停止新寫入並核對授權。 | Authorization or audit is unavailable. Stop new writes and check authorization. |

新增本地码使用同名DELIVERY.*诊断键，产品全局码仍由边界一对一映射。任何业务错误不得被通用“操作成功”提示覆盖；缺翻译验证失败，运行最多显示稳定code与Diagnostics资源，不能空白或暴露secret。

## 11. 正常、边界和失败案例

| 案例 | 预期 |
|---|---|
| 签名包、空间和依赖均满足，当前任务已排空 | 依次完成 Prepare/Quiesce/Backup/Apply/Verify/Activate，返回 `Completed/Activated=true` |
| 重复执行同一 `OperationId` 和同一 manifest | 返回原持久回执，不再执行迁移步骤 |
| 同 `OperationId` 但 manifest 摘要不同 | `DUPLICATE_OPERATION_ID`，不覆盖原请求 |
| 包内多余文件、路径穿越、摘要错误或签名失效 | 在 staging 前拒绝，旧版本保持运行 |
| 迁移中断后进程重启 | 从持久状态恢复为 `RecoveryRequired` 或继续同一安全阶段；不重放已确认步骤 |
| 配置成功但数据库迁移不可逆且 Verify 失败 | 不宣称可回退；按批准 ForwardRepair 或人工恢复，旧结果保留 |
| 备份文件存在但读回/hash 失败 | `BACKUP_UNVERIFIED`，不得 Apply |
| Supervisor 启动成功但 readiness 超时 | `READINESS_TIMEOUT`，查询后进入恢复，不报告 Activated |
| 取消发生在 Apply 前 | 排空并返回 `Cancelled`，不写半成品 |
| 取消发生在原生迁移调用中 | 等待安全返回；资源归还前不释放输入或替换依赖 |
| 两个宿主同时升级同一根目录 | 一个获得资源租约，另一个明确 `RESOURCE_BUSY`，不互相覆盖 |
| 历史数据缺字段但仍可读 | `HistoricalDataReadable=true` 并带缺失诊断；模块不补造领域值 |

### 11.1 第二轮场景驱动复审矩阵

下面每行都是实现和接入测试的最小可判定单元。参数来源必须能追溯到请求、manifest、环境探针或已登记的适配器 Profile；不得从当前 UI、日志猜测或自动填充。

| 场景 | 输入与参数来源 | 固定处理顺序 | 输出/状态/错误 | 恢复动作 | 验收断言 |
|---|---|---|---|---|---|
| 正常升级 | 完整签名 manifest、非空条目和幂等 steps；版本/空间/权限来自请求与环境探针 | Validate → staging hash → quiesce/drain → backup+readback → 每步 CAS 持久化 → historical readback → readiness → activate | `Completed`, `Activated=true`, 每步 `Durable=true` | 无；保留恢复点按宿主策略 | 同一 manifest 在两个消费者得到相同最终 hash、事件序号连续且无旧版本写入 |
| 空输入 | `Entries=[]`、`Upgrade` 且 `Steps=[]`；来源是调用请求 | 在结构校验阶段拒绝，不访问适配器 | `Rejected/INVALID_REQUEST` | 修正 manifest 后创建新 `OperationId` | 无 staging、无 quiesce、无备份调用计数；`Repair` 的零 step 仅在 §3.5 允许条件下接受 |
| 仅修复文件 | 非空已签名条目、`Mode=Repair`、零迁移步骤且 `Repair` 语义明确 | 校验条目 → 备份 → 原子替换 → readback；不得运行不存在的 step | `Completed` 或 `VERIFY_FAILED` | 按恢复点恢复旧文件 | 修复包可读且历史数据不变；零 step 不被误报为升级 |
| 部分成功 | step 1 durable 成功，step 2 返回错误或进程在 step 2 后退出 | 记录 step 1 回执后停止；禁止跳到 Verify/Activate | `PartiallyApplied` → `RecoveryRequired`, `MIGRATION_STEP_FAILED` | 查询原操作；按 `RollbackMode` Restore 或 ForwardRepair | 重启后 step 1 不重放；未完成 step 有明确原因；不能返回 `Activated=true` |
| 歧义版本 | `From` 缺失、目标同时匹配两个迁移区间、未知 schema 或 ordinal 间隙 | 版本解析 → 兼容矩阵 → 前置条件；不调用存储 | `Rejected/AMBIGUOUS_COMPATIBILITY` 或 `DEPENDENCY_INCOMPATIBLE` | 选择明确版本的新请求 | 无写入、错误带字段/step ID；不选默认“最近版本” |
| 错误输入 | 重复路径、非 NFC、大小写碰撞、`..`、符号链接逃逸、重复 step ID、负/溢出字节数 | 校验规范路径和全量集合后拒绝；不做静默路径改写 | `Rejected/INVALID_REQUEST` | 修正包并重新签名 | 冲突路径不会落入 staging，拒绝发生在 staging 前 |
| 包被截断或退化 | 文件长度小于 manifest、随机读失败、摘要不一致；参数来自 Package Provider | 流式 hash/长度 → 签名 → 不落地可执行内容 | `Rejected/PACKAGE_HASH_MISMATCH` 或 `PACKAGE_TRUNCATED` | 重新取得包；不清理旧版本 | 峰值内存不随包大小线性复制；旧版本仍可读 |
| 超大输入 | `MaxPackageBytes`、条目数、step 数或依赖闭包超过 `DeliveryLimits` | 先读 manifest 头和声明长度，再比较上限；不得开始复制全部包 | `Rejected/PACKAGE_TOO_LARGE` 或 `TOO_MANY_STEPS` | 选分片/更大获批 Profile；不隐式放宽上限 | 磁盘、内存和队列峰值均在预算内，适配器无写入 |
| 高并发请求 | 多个不同 `OperationId` 竞争同一资源键；并发度来自宿主 Profile | 有界队列 → 资源租约 CAS → 仅一个 active owner；其余排队或拒绝 | `RESOURCE_BUSY`、`QUEUE_FULL` 或正常排队 | 取消排队项；不取消已拥有租约的操作 | 无死锁/饥饿；同一根目录最多一个 Apply；队列计数可对账 |
| 噪声/遮挡/退化外部条件 | 远端存储短读、服务探针抖动、备份介质暂时不可读；不是视觉输入 | 重试仅限无副作用读；写/启动结果未知先 Query | `BACKUP_UNVERIFIED`、`READINESS_TIMEOUT` 或 `UNKNOWN_SIDE_EFFECT` | 恢复点查询、人工接管或重新 Prepare；不盲重试 | 记录实际尝试次数和退化原因；未知不变成成功 |
| 取消/超时 | 每阶段 deadline 和 `CancellationToken` 来自请求；取消在 Apply 前/中/后分别注入 | 请求取消 → 拒绝新工作 → drain → 等源任务结束 → 持久回执 | `Cancelled`（未 Apply）或 `RecoveryRequired`（Apply 中） | 查询操作；必要时按恢复动作处理 | waiter 超时不释放源任务资源；排空未完成不删除 staging |
| 资源上限 | 空间低于 `MinFreeBytes`、句柄/连接/临时文件额度不足 | 预检空间与资源 → 全量取得或不取得 → 阶段结束归还 | `INSUFFICIENT_SPACE` 或 `RESOURCE_EXHAUSTED` | 释放获批临时空间、保留旧版本、重新 Prepare | 每项资源有唯一归还 Owner；持续负载无界增长为零 |
| 持久化断电点 | 在每次状态/step/回执提交前后注入进程终止；恢复读取操作日志 | 启动扫描 → CAS 重建 → 校验 manifest/backup → 继续或标记 RecoveryRequired | `RecoveryRequired`, `Recovered` 或 `RecoveryFailed` | 不重放已 durable 步骤；按原 RecoveryAction | 每个 crash point 都能判定；状态不会跳过 Verify/Activate |
| 版本修订/旧数据 | reader 新于 manifest、旧 schema 缺字段、同内容新 revision；参数来自兼容矩阵 | 读取旧 schema → 显式映射 → 保留原 revision/hash → 读回验证 | `HistoricalDataReadable=true/false`，缺失显式诊断 | 无法解释时隔离旧数据，不能补零或改原事实 | 旧数据 ID/hash 不变；新 revision 不覆盖旧回执 |
| 备份闭包不完整 | manifest 已签名但缺 WAL/checkpoint、CAS 对象、审计 seal、密钥代次或对象 readback | 冻结 checkpoint → 枚举闭包 → 逐对象 hash/readback → 独立隔离恢复演练 | `BACKUP_UNVERIFIED`, `Restorable=false` | 保留原版本和失败 receipt；不得 Apply/清理原对象 | 清单签名不单独产生 Restorable；缺一对象即不可恢复 |
| 隔离恢复失败 | 备份对象完整但隔离目录只读打开、历史查询、引用闭包或 replay smoke 失败 | 独立根 materialize → 每对象核验 → 只读查询/回放 → cleanup receipt | `RECOVERY_FAILED` 或 `RecoveryRequired` | 不切生产 current；保留隔离现场供人工恢复 | 生产数据/活动槽不变；演练结果可查询且不可伪造成功 |
| readiness 证据过期/错绑 | 目标进程可启动但 manifest、slot、contract/capability、policy/profile、样本 epoch 或 source version 不匹配 | 重新读取运行版本 → 验证连续样本和有效期 → 再决定 active selection | `READINESS_EVIDENCE_INVALID`、`READINESS_TIMEOUT` 或 `VERIFY_FAILED` | 保持旧 current/隔离；查询原 Supervisor action | 单次启动/liveness/旧缓存不能激活 |
| 冷目标机 | 无 current slot、可查询 OperationStore、受信 profile 或 baseline readiness | 前置检查后立即拒绝，不创建 staging/quiesce | `COLD_TARGET_NOT_INITIALIZED` | 宿主安装器建立基线后重新提交新 OperationId | Core 不执行首装、不选择空 current、不写迁移 |
| 升级失败与回退 | 已验证 backup，Apply 后 Verify 失败；回退策略来自 manifest `RollbackMode` | 停止激活 → Query 操作 → Restore 或 ForwardRepair → readback → readiness | `Recovered` 或 `RecoveryFailed` | 失败进入人工恢复；不只替换 EXE | 数据、配置、包版本成一致组合；不可逆迁移不宣称回退 |
| 无 UI 调用 | 最小 .NET 宿主注入 clock、存储、quiesce、supervisor、审计端口 | `Validate` 或 `ExecuteAsync`；无 Dispatcher/窗口 | 同 UI 的结构化 `DeliveryResult` | 客户端关闭只取消订阅，核心继续 | 无 WPF/DevExpress/设备 SDK 引用；结果可通过 Query 恢复 |
| 可选 UI | UI 仅订阅 `IProgress<DeliveryEvent>` 和 `QueryAsync`；权限来自宿主 | 显示事实 → 按状态启用命令 → 调用同一 Core | 三语状态、错误和恢复建议；无权操作隐藏并非绕过校验 | 关闭/切页解除订阅；不终止核心 | 旧 OperationId 事件不覆盖新投影；键盘/UIA/1920x1080 通过宿主验收 |
| 第二消费者 | 离线工具使用复制数据和同一 manifest；无设备控制端口 | Validate → dry-run/备份 → Apply/Verify 或只读 Query | 与机台相同状态码/回执语义 | 离线失败不影响机台数据；导出诊断 | 两消费者的 contract/conformance 用例、hash 和幂等结果一致 |
| 长期运行 | 连续升级预检/查询、事件订阅反复开启关闭；负载和冷/热 Profile 由宿主提供 | 有界事件队列 → 定期 checkpoint → 资源租约审计 | 无内存/句柄/临时文件持续增长；异常计数可查询 | 到达上限时背压或拒绝新请求，不静默丢事件 | 24 h 或获批时长趋势稳定；事件、回执、资源计数最终对账 |

“噪声/遮挡/退化”在本模块中只表示包、存储、服务探针和通信输入退化；本模块没有图像、缺陷或遮挡算法。任何视觉质量判断必须留在视觉模块和调用应用。

## 12. 测试矩阵和可判定验收

测试必须使用可控时钟、显式完成信号和真实字节/摘要，不能用 `sleep` 猜竞态。模拟适配器只能证明软件协议；客户交付仍需独立现场门。

| 类别 | 最小断言 |
|---|---|
| Contract/Schema | manifest 必填字段、路径规范化、版本/摘要/签名和拒绝未知字段 |
| JCS/签名 | RFC 8785 Appendix B 字节向量、Jcs.Net 固定版本 API、属性次序不影响摘要、数组次序按字段语义、拒绝重复/未知键及非法 Unicode/数值、载荷单字节变化导致 hash/signature 拒绝、manifest 与签名投影域隔离 |
| Golden/Journal/fence | 本页 SignatureInput、PackageEntry、MigrationPlan、ActionIntent、PayloadProjection 五组完整规范字节/hash；字段独立拼接、KeyId/RotationEpoch、原 OperationId/ActionId、epoch/fence、同键幂等/变更冲突和迟到回调拒绝 |
| 状态机 | 每个允许/禁止转换、CAS 冲突、重启后的唯一 Owner、终态不可变 |
| 流程 | 双消费者（机台宿主、独立升级工具）使用同一包完成同一回执语义 |
| 幂等 | 重复 OperationId、重复 step、重启后重放、重复 Recovery 均不重复副作用 |
| Task/cleanup | waiter 取消、UI Unbind、进程关闭、源 Task 迟到、独立 cleanup 成功/Unknown、双错误轴移交和资源持有直到 durable receipt 全部可判定 |
| 失败注入 | 空间不足、权限拒绝、锁占用、断电、数据库异常、服务不 readiness、事件 sink 失败 |
| 取消/超时 | 超时先于返回、返回先于取消、排空超期仍持有资源；Waiter 不释放源任务资源 |
| 恢复 | 备份/hash/读回、部分迁移、不可逆迁移 ForwardRepair、旧数据可读和未知回执查询 |
| 备份闭包/隔离恢复 | checkpoint/WAL 或等价边界、CAS/文件对象、配置/Schema、审计引用、密钥代次、逐对象 readback、独立根只读恢复、历史查询、回放烟测、cleanup receipt、RPO/RTO `NotEvaluated` 规则 |
| readiness/冷目标 | 升级前后真实运行版本/manifest/slot/profile join、连续样本/epoch/有效期、current 缺失拒绝、首装不进 Core |
| 并发 | 同一资源串行、不同资源隔离、租约过期回调不能推进新代、无死锁/无界队列 |
| 安全 | 未签名/篡改/过期密钥/越权路径/符号链接逃逸全部阻断，日志不泄露密钥 |
| 观测 | 每一事件有 OperationId/阶段/序号/版本/耗时；指标与持久回执可对账 |
| 性能/长稳 | 目标 Profile 的 P50/P95/P99、空间峰值、CPU/IO、长稳内存趋势和恢复时间 |
| UI（适用时） | 三语、权限、关闭/重开、旧事件隔离和 1920x1080/UIA/键盘路径 |
| Host conformance | 同一 Core case 在 InMemoryRecoveryHost 与 FileReplayHost 均执行；两个 STA Host 的 Session/Unbind/Query 语义一致，未构造 Host 或外层截止超时返回非零 |

### 12.1 BenchmarkProfile 与测量协议

通用 `BenchmarkProfile` 的不可变身份、版本/hash、冷/热与样本计划、单调计时、失败/删失保留、分位统计和 `NotEvaluated` 规则唯一见 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)。DeliveryBenchmarkProfile 仅补充本模块负载：目标 OS/CPU/内存/磁盘/文件系统/网络、构建与依赖版本、签名包/manifest/条目与载荷字节分布及 hash、签名验证和迁移步骤数、当前/目标发布槽状态、备份/恢复闭包、租约/队列/并发与到达模型、缓存状态、故障注入点及各交付阶段测点。每个目标和资源阈值必须带批准 Profile 或 Contract 的来源 ID；并行操作使用隔离根目录与唯一 OperationId，避免复用 Apply/恢复副作用。

按 DEV-GOV-010 §3.1 执行冷/热、固定样本、单调计时、分位与失败样本记录。该模块必须分别测纯 manifest 预检、签名/哈希/包复制、staging/flush/readback、Quiesce/Drain、Backup、Apply、Verify、活动槽激活/readiness 和恢复；同时报告相应阶段和完整交付耗时，不得将不含包复制的预检描述为完整升级时间。吞吐只计回读、摘要和 readiness 均验证通过的完成操作。

记录 CPU、工作集/私有字节、托管/native 缓冲、磁盘空间/IO 峰值、队列项/字节、租约/句柄、备份与 staging 字节、空间余量和资源归还。排空从关闭接纳至全部已接纳任务、Supervisor/适配器调用、文件/数据库操作和回调真实结束；阈值来源必须能定位到已批准消费者停机窗/负载要求、部署资源与签名包约束、Contract 安全边界或资格记录。事件队列、包/manifest/entry 限额、最小空间和单资源串行只有在批准的运行限制 Profile 中冻结值及来源后才作为硬上限。缺少性能目标标为 `TargetPending`；缺少测量或未真实排空按 DEV-GOV-010 标为 `NotEvaluated`。

Apply、Restore、ForwardRepair 每次从可重建初始快照开始，并记录备份/发布槽/接纳水位及适配器版本，避免副作用跨样本污染。

### 12.2 真实接入链与测试替身边界

每个消费者的 `DeliveryAcceptance` 必须通过其真实 Application 入口调用同一 `IDeliveryService`，经过真实 Core/状态机、耐久 OperationStore、实际包文件/staging/发布槽、适用的真实迁移与 Supervisor 适配器，最后核对结果投影，并在消费者重启后用 `QueryAsync` 读回同一操作的状态和回执。至少覆盖一次正常升级和一次 Apply 后验证失败的恢复；每次执行从隔离的、可重建的初始快照开始。断言必须核对最终包/配置/数据的一致组合、历史查询、readiness、接纳状态和已结束操作的资源归还，不能只断言返回 Success。

纯 Core/Simulator 测试可以先验证协议和状态不变量；耐久事务、CAS/幂等、权限、发布槽切换、恢复、进程重启和性能/资源的真实接入验收必须使用对应真实实现。Mock/Fake 的固定成功回执、方法或文件存在、Schema 通过、截图存在、报告自报 Passed 和全局测试绿灯，均不能代替上述断言。真实适配器尚未具备时，明确记录受影响接入项 `Blocked`，不抵消已完成的纯 Core 验证，也不升级为交付通过。

使用 Simulator/Fake/Replay 的用例在现有测试计划或执行证据中登记：替身 ID/类型/版本或 hash、被替代端口、原因、输入合同、可证明范围、禁止推断和对应真实用例/门禁。并行执行使用独立 OperationId、根目录、数据库和进程；成功、失败、取消及进程重启后分别核对文件锁、连接、租约、订阅/handler 和进程的所有权及释放，不能仅以测试进程退出证明无泄漏。替身登记不新增运行时依赖或第二套测试目录。

### 12.3 不可变执行证据与结论派生

接入验收复用测试/资格 Owner 的不可变 TestRun 及证据存储，本模块不定义完整测试平台 Schema、Core DTO 或新的执行证据接口。交付方必须能从现有证据重建以下最小关系：

| 绑定范围 | 必须可重验的内容 |
|---|---|
| 执行身份与基线 | run ID/版本/hash、源代码基线及未提交差异摘要（无 Git 时使用可审计源快照 hash）、依赖/Contract 基线、构建与测试二进制 hash |
| 输入与环境 | 消费者/适配器版本、OS/runtime/文件系统、批准 Profile/兼容矩阵 hash、源/目标发布槽、包/manifest 与初始快照 hash；随机用例的 seed、分片和顺序 |
| 用例与操作 | case ID、精确测试方法及数据 hash、OperationId/ActionId、attempt、UTC 起止和单调耗时、状态/错误、预期断言语义与实际回执/读回结果 |
| 原始证据与历史 | 原始结果、脱敏日志、指标及 artifact 的可读取引用/hash、失败栈、排除/阻断理由、全部重试；保留期限覆盖该发行的审计要求，按宿主信任策略签名并可验证 |

required case/gate 由获批接入范围和验收策略确定，结论从这些项的真实结果派生，不能由报告 writer 传入一个 Passed 布尔值。缺少执行、hash 不匹配、证据不可读或 scope/版本错绑，均不能得出通过；不适用项须由相应 Owner 批准并带理由。重跑生成新 run，保留原失败及 attempt；不得覆盖签名证据或不断重试只保留成功。本模块的 `Completed`/恢复回执只证明该次交付操作，不等于测试通过、产品发布或质量放行。

### 12.4 全范围Adapter/UI反例与负载验收

沿用§9/§12既有用例，新增范围只追加下列确定断言，不重复已接收Golden；同一包在机台服务与离线维护工具的独立根执行，底层真实/模拟来源在TestRun中分别标明。

| 用例 | 固定输入与期望 |
|---|---|
| DM-CODEC-017 | 新124-byte Resume封套逐字段构造→Encode字节/hash一致；Decode再Encode相同。删detail/null、改queuedCount类型、加未知键、重复key、超MaxRecordBytes、kind/T不匹配均拒绝，不补默认；注册record完整round-trip，嵌套backup/readiness不能只存hash |
| DM-ADAPTER-018 | 在Store tmp写后、Flush后、rename后、读回前各断点故障，重建只接受完整连续commit；缺中间sequence/previous hash错→STORE_CORRUPT。活动CAS竞争仅一方提交；目录未seal不被Supervisor定位 |
| DM-PATH-019 | 合法app/Host.exe=abc成功；兄弟root前缀/../ADS/保留名/NFC/case冲突/reparse/NumberOfLinks>1拒绝；第二遍源变化拒绝，无客户路径写入。路径合成测试不证明真实ACL隔离 |
| DM-SECURITY-020 | SPKI/KeyId/revision错绑、撤销观察点未知、服务端身份不匹配、backup key不可恢复→Apply/新Start发送0，原Task继续强持；日志/codec无secret，不改签名算法 |
| DM-PRESERVE-021 | 闭包完整恢复到shadow，逐对象hash/历史读取一致，未知user-file原hash不变；多scope无原子发布/一致恢复路线前置拒绝；ForwardRepair仅兼容目标槽，旧槽Select次数0 |
| DM-RETENTION-022 | 独立维护ID，Active/Referenced/Leased/Held任何true→Remove发送0；Keep同revision/hash幂等一次；删除并发新增引用原子复查失败→ARTIFACT_PROTECTED，内容变化/丢应答查原ID，不扩大文件列表 |
| DM-UI-CMD-016 | 两个STA Host同binding/controller三参Panel，权限撤销/未确认/epoch变化拒绝；重复/取消waiter/解绑/迟到按§10.2；全部状态与错误三语完整，真实WPF运行另计 |
| DM-SUPERVISOR-023 | Stop丢应答→原Query Unknown保持隔离；Start只liveness/错slot/hash不Ready；N样本缺一个、重复ordinal、跨boot/epoch、超龄、Profile错绑均拒绝 |

Adapter测点追加record encode/decode/完整commit/Flush+readback、活动CAS/receipt Query、backup key解析（不含secret）、保留保护检查与Retired清理、各scope迁移/恢复提交。负载为批准Profile中的包/manifest/record最大字节、文件数、历史日志长度、并发维护、readiness checks×N，冷/热各从可重建初态执行；单位bytes/ms/count，阈值来自部署/客户Profile。记录buffer/流/锁等待/未归还Task/lease/未决receipt/磁盘/句柄峰值及端到端P50/P95/P99，失败/Unknown/删失保留；资源未确定不报性能通过。UI测Dispatcher投影耗时/单flight队列/树节点数/长三语，不将动画当迁移性能。无实际测量仍NotEvaluated，不以Golden替代真实吞吐与恢复时限。

## 13. 可观测性、审计和数据最小化

结构化日志字段至少包括：`operationId`、`correlationId`、`moduleId`、源/目标版本、manifest hash、stage、transitionOrdinal、stepId、adapterId、attempt、elapsedMs、queueWaitMs、bytesStaged、freeBytes、resultState、errorCode、recoveryActionId。指标包括阶段计数、持续时间 P50/P95/P99、排队深度、活跃/排空操作、备份字节、恢复点验证失败、未知副作用和资源归还计数。

审计记录请求者、权限决定、包摘要、状态转换、备份引用、迁移步骤回执与恢复动作，不记录密钥/完整凭据/未授权配置。Store Journal必须耐久且是唯一权威，Audit只是投影：初次Prepare/Apply前投影不可用固定停止新副作用，返回AUDIT_UNAVAILABLE；Apply后投影错误不阻断查询/安全恢复/cleanup，单独记诊断并保留原操作错误，恢复确定后按原sequence补投影。“离线”不自动豁免审计，投影失败不覆盖原commit；消费者安全Profile只能收紧新动作准入，不能改变安全收敛。日志/UI不推断缺失回执。

## 14. 版本兼容、发布、回退和迁入

### 14.1 三条可决定的更新/恢复路线

| manifest `MigrationSafety`/`RollbackMode` | Apply 前置 | Verify/启动失败后的唯一软件路线 | 禁止推断 |
|---|---|---|---|
| `Reversible` + `SnapshotRestore` | `RollbackArtifactSha256`、逆向 precondition、完整备份闭包和隔离演练均通过 | 按原 OperationId 查询；Restore 备份、读回配置/Schema/对象，再以活动槽 revision CAS 选择原版本，启动原版本并验证 readiness；成功才 `Recovered` | 只替换 EXE、只执行字符串 reverse handler、未验证备份都不能叫回退 |
| `ExpandContractCompatible` + `SnapshotRestore` 或批准 `ForwardRepair` | 旧 reader 在 expand/contract 窗口仍可读，步骤/handler/兼容区间已登记 | 可恢复时走 SnapshotRestore；若已进入 contract 且旧 reader 不再安全，必须留在新兼容槽执行 allowlisted ForwardRepair，完成目标 Schema/readback/readiness 后 `Recovered` | 不得把新 schema 强行交给旧二进制；不得在未验证兼容性时选择上一版本 |
| `Irreversible` + `ForwardRepair`/`NotSupported` | 无 reverse artifact；ForwardRepair 的目标 schema、幂等前置和人工接管条件已批准 | 只允许查询原步骤并按 ordinal 完成剩余的幂等 ForwardRepair；启动与目标数据 schema 匹配的版本，验证后才 `Recovered`；无可执行 repair 则 `RecoveryFailed`/人工移交 | 不得声称二进制回退可以逆转数据；ForwardRepair 路线不得选择不兼容的旧 release |

`ForwardRepair` 是对当前已提交数据继续向前收敛，不是另一次隐式升级；它跳过已有 durable success 的步骤，只执行同一 manifest/approved repair plan 中剩余步骤。Restore、ForwardRepair 和发布槽选择分别写入独立 ActionIntent/receipt；任一结果 Unknown 都停在 `RecoveryRequired`。只有该路线的活动槽、数据 schema、readiness、历史读回和清理结果全部一致，才允许提交 `Recovered`。

- 模块自身使用 SemVer；公开类型的字段删除、单位改变、状态/错误码重命名、事件顺序改变均属于不兼容变更，必须提高 Major 并提供 Migration Guide。
- manifest schema 与模块版本分开。阅读旧 manifest 的能力必须显式列出 `minReader/maxReader`；未知字段只能在 schema 明确允许扩展时保留，否则拒绝。
- 每次发行必须带 manifest、逐文件 hash、签名、依赖闭包、SBOM、兼容矩阵、迁移步骤和恢复演练记录。包不可原地覆盖，先写版本化 staging，再原子切换指针。
- 回退前必须查询 Operation 状态、确认没有在途资源、验证恢复点和目标兼容性。二进制回退不能单独逆转数据库；不可逆变更使用批准 ForwardRepair 或恢复整个一致快照。
- 断电/重启后以持久操作日志和恢复点继续；不得清除用户配置、历史结果或旧发行包来“恢复成功”。旧版本可读性是独立验收断言。
- 客户项目迁入平台时先保存交付基线（版本、配置、数据、证据和验收依据），再做差异盘点、适配、回放、受控切换；旧项目不因平台基线自动升级，平台模块也不反向引用旧页面/私表。

## 15. 第二消费者接入示例与验收

第一消费者为生产机台宿主：由机台负责安全停机、在途板策略和最终重新开放生产；模块只执行软件发行和可恢复迁移。第二消费者为独立离线升级工具：它使用同一 Core 和适配器端口，在复制的客户数据上执行 Validate/Backup/Apply/Verify/Recover，能够查询和导出回执，但没有设备控制权限。

两者必须分别验证：同一 manifest hash 解析结果一致；同一 `OperationId` 幂等；取消、重启、磁盘满和未知副作用语义一致；机台 UI 和离线工具关闭/重开不改变核心状态；任一消费者不能读取另一消费者私有表或改变其权限。只有两个消费者通过同一 Contract/Conformance Test Kit 后，模块才可从 DesignReview 进入 Contracted。

### 15.1 冷目标机和现场职责

冷目标机是没有可查询的当前发布槽、有效运行时 readiness、受信配置/策略或已验证恢复来源的目标。它不满足本模块的升级/修复前置条件；Core 返回 `COLD_TARGET_NOT_INITIALIZED`，不创建 staging、不排空、不执行迁移、不选择活动版本。首次安装、OS/运行时/服务账号/ACL/证书/设备驱动建立、基线配置导入和初始备份由已批准的宿主安装器与部署 Owner 完成；完成后必须提供不可变当前槽、manifest/readiness 回执和可查询 OperationStore，才能创建本模块的 `Upgrade` 或 `Repair`。

现场运维负责确认目标身份、授权主体、签名信任来源、批准的 limit/policy/performance Profile、备份介质/恢复凭据、停机和安全前置条件，并在生产切换前执行或取得隔离恢复演练回执。Delivery Core 只验证这些输入和适配器回执，不决定 LOTO、急停、PLC/运动安全、客户 RPO/RTO、远程维护时限、网络拓扑、账号分配或客户保留策略。现场无法提供当前槽、真实 readiness、闭包对象、恢复凭据或授权回执时，保持 `NotReady/RecoveryRequired`；不得以人工勾选、文件存在、旧 PASS 或“目标机可启动”替代。

### 15.2 清洁目标环境与上一支持版本接入验收

清洁目标环境用于消除开发机残留文件、账号权限和服务配置的掩盖效应。先由宿主安装器建立 §15.1 的已验证基线，再调用本模块；未初始化目标仍按 `COLD_TARGET_NOT_INITIALIZED` 拒绝，安装器测试不计作 Core 首装能力。环境与支持版本由批准的部署 Profile/兼容矩阵确定，不虚构通用客户数值。

| 接入场景 | 可判定验收 |
|---|---|
| 清洁环境基线后升级/修复 | 使用真实目标账号、授权根目录、服务和适配器；完整依赖来自发行包及批准环境，排空、不可变槽切换、readiness 和重开接纳可读回；不依赖开发机隐藏文件或管理员绕过 |
| 上一支持版本升级 | 从兼容矩阵指定的上一支持版本及冻结旧配置/数据开始，核对真实迁移结果、旧数据/历史回执可读和完整包 hash；各支持路径按矩阵验收，不能以单一路径代表全部 |
| 升级失败与恢复 | 使用实际备份/恢复实现，验证数据库提交边界、配置和对象引用闭包；Restore 或 ForwardRepair 后只得到策略允许的一致版本组合，重启查询不重复已提交副作用，无法恢复时保持隔离和 RecoveryRequired/RecoveryFailed |
| 离线运行与旧数据 | 在批准的离线环境用本地发行包、信任和恢复来源完成适用流程；缺项显式拒绝，旧字段缺失保留诊断与原 hash，不联网补造事实、不隐式降级校验 |

每次运行记录环境、源/目标版本、适配器、包/备份 hash 与对应 TestRun 引用。模拟服务或内存存储结果只计相应协议范围；清洁环境软件验收不代替机台安全停机、HIL 或客户现场验收。

## 16. 发布门、未决项和自审结论

模块接入结论必须绑定 §12.2 的真实执行、§12.3 的可重验证据和 §15.2 的适用部署路径；构建/打包成功只证明构建/打包。P0/P1 的定义和发布审批由宿主治理 Owner 负责；未解决的适用 P0/P1、静默成功、数据不可恢复或关键证据伪造不能被全局绿灯、模拟结果或豁免包装为本模块验收通过。最终发布决定由产品流程负责，Delivery Core 不新增签署、豁免或生产放行权。

### 16.1 明确不支持能力

- 不提供跨主机/跨数据库的分布式两阶段提交或“恰好一次”外部设备动作；未知回执只能查询或人工恢复。
- 不保证无停机热替换被锁定的 native/设备依赖；排空未完成时只能保持旧版本或进入恢复。
- 不为不可逆 Schema 变更自动生成逆迁移，不自动猜测 ForwardRepair，也不把二进制回退当作数据回退。
- 不提供云端编排、远程凭据托管、任意 SQL、任意脚本执行或绕过签名/权限的维护后门。
- 不解析图像、模型质量、缺陷、遮挡、噪声或训练数据；视觉可读性由专门资产/算法模块通过适配器负责。
- 不把分片包、断点续传、压缩格式或加密密钥轮换视为默认能力；只有正式 manifest/适配器 Contract 冻结后才能接入。

后续外部实现条件：正式 Contract/Schema 位置、全局错误码和 RecoveryAction 目录、部署信任根/公钥有效期/吊销与轮换时间、客户存储事务能力、Supervisor/readiness 协议、停机窗口、保留周期、RPO/RTO、真实包规模、备份介质和两个消费者的 Profile。上述不改变已冻结的 Core 契约、canonicalization、签名算法与校验顺序；缺项只阻断依赖它的集成/现场切片，不阻断使用模拟信任库和适配端口的纯 Core、契约测试与恢复状态机实现。

### 16.2 本轮两轮自审与切片状态

第一轮（实现者）：从输入→Validate→签名/容量→Reserve/初始Acquire→逐Action intent→Apply/Verify→三条恢复路线→一次cleanup→Resume→终态→控制权撤销走读。修正跨动作同context、过期后Query被拒、释放root就丢Resume权限、ForwardRepair默认旧槽及完整Golden缺字段；取消/迟到/Unknown均保留原Task/借用输入。第二轮（外部消费者）：从空宿主按§9的具体构造签名与§9.2全部参数组装两个Host，按§10.1组装Bind/Panel，跟踪异常/有限关闭/确认移交/重复Query与退出码；修正只build Core却no-build运行Tests、try中提前return、接收者覆盖旧Root及Session离栈丢query Owner。两轮仅为有限规格自审，没有执行所示C#。

当前唯一版本`0.1.8-prep`。主控于2026-10-11对0.1.7-prep回读并接收纯Core、模拟端口与双无UI Host的DEV-GOV-010 §3.1六项文档规格，对应切片标记为`ModuleCoreImplementationReady`；UI指定构造内容限定接收，真实WPF运行资格仍为后续门。主控已按完整字段规范重建五组JCS向量并确认hash一致，该结论属于规格一致性，不是运行证据。该次仅同步状态；本轮补全范围设计但仍未创建Core/Tests/UI工程、未build/run/WPF，未执行真实适配器、部署、安全凭据、数据库、进程、性能或现场验收；这些后续门不替代已接收的内部规格，也不因本次接收视为通过。

DEV-GOV-010 §3.1 六项内容定位（纯Core/模拟端口/双Host文档规格已由主控接收）：

| 条件 | 本页唯一实施位置 |
|---|---|
| 1 边界/第二消费者/依赖 | §1、§2、§15；模型仅opaque字节，不提供视觉算法 |
| 2 公开API/单位/状态/资源/兼容 | §3、§4～§8、§9公开Factory/Root、§10.1 Bind、§14、附录A |
| 3 无UI最小宿主 | §9.1唯一net10.0工程，§9.2两个完整composition root/fixture/端口构造，§6进程Owner与有限移交 |
| 4 正常/异常/测试断言 | §9.2正常与Verify失败完整路径、§9.3有限case、§11～§12；UI仅后续切片 |
| 5 Benchmark | §12.1负载/阶段/P50/P95/P99/资源/阈值来源；目标待消费者Profile，NotEvaluated |
| 6 工程/范围/顺序/门 | Core implementation binding、§9.1具体Core与Tests构建运行、§9.2、§10.1 UI后续工程、§16.1 |

本轮只写本DEVELOPMENT-GUIDE.md，完成文档自审/验证后停止，不派发实现。后续实现仅上述Core/Adapters及相应Tests、WPF/HostTests工程，消费者特定底层适配器须其Owner单独批准。共享入口/Contract/Registry、其它模块、参考原件、AsunImage内部与客户项目禁止写。原0.1.7-prep纯Core六项接收保持，0.1.8-prep新增Details/维护/controller/codec/Adapter字段签名属本轮确定文档增量，未冒称已编译或自动扩大旧切片Ready。代码/全部case/UI接线尚未实现或编译运行，实际依赖/现场事实按§16.3精确分门，不等待总控代审内容。

本次自审已确认：本指导只定义通用部署、更新、迁移、排空、回执和恢复；没有写入 PCB/AOI 等制程判定、目标关联、工艺解释、质量放行或设备副作用。无 HALCON 算法路径，无 AsunImage 依赖；AsunControl 的配置原子保存和 SQLite 备份事务仅作为适配器设计参考，未被当作平台 API。当前纯Core/模拟端口/双Host规格为`ModuleCoreImplementationReady`；文中运行时Profile的客户采纳、项目绑定、适配器实现、集成和发布资格仍未通过。
### 16.3 当前全部批准范围的最终文档准备结论

2026-10-12由本模块永久原会话执行/内容审核/修复/验证，复用原Core六项接收、JCS/RSA-PSS研究与五完整向量、原两轮Root/双Host/恢复自审。只核对完整架构范围和实际增量：本轮已补§6.4～6.7的真实Adapter/完整codec/安全凭据/配置数据闭包/保留入口，§10.2～10.3的命令接线/布局/全部状态错误三语，以及§12.4反例/负载。同步Validate只检查实参、异步环境验证由Execute负责，消除未定义manifest Repair字段和Audit失败后安全恢复分支。没有重新设计已接收Root/Close或重复研究签名算法。

**结论：当前架构批准的完整delivery-migration范围，无剩余可决定的软件算法、API、Adapter、UI、默认/推荐规则或恢复Owner设计欠账；文档准备闭合。** 全范围含独立交付/迁移计划、签名hash与信任、配置/数据/安全引用保留、动作身份与耐久回执、原结果查询、三条恢复路线、受控保留/删除、机台/工具/服务消费者、无UI调用和可选面板。未批准的首装/任意脚本/压缩下载/分布式提交/视觉语义/凭据托管保持排除，不以此扩大模块，也不把未实现代码称为完成功能。

| 批准能力 | 唯一章节 / 文档结论 |
|---|---|
| 边界、消费者与部署决定权 | §1～2、§6.4、§15；宿主决定部署/生产许可，模块仅产生/执行获准迁移技术动作与证据 |
| 包、计划、签名/参数/codec | §3、§6.5；JCS/算法固定，完整字段/默认/版本域明确，secret不入包/日志，坐标不适用 |
| 原Action/Owner/取消/超时/移交 | §4～7、§9；既有Root/原Task/单次有限cleanup、控制fence与迟到路径保持 |
| 文件与真实存储/进程Adapter | §6.4～6.6；具体构造/文件提交/pathguard/ledger/注册scope/协议映射/Readiness验证均冻结，不将软件设计移交现场 |
| 回滚/前向修复/数据保留 | §3.4、§6.6～6.7、§14；SnapshotRestore与ForwardRepair分路，后者只选兼容目标槽，删除逐项受保护CAS |
| 可选UI完整操作链 | §10.1～10.3；同binding/controller/Core、DevExpress25.2.3布局/联动/三语/权限/键盘/恢复明确，无viewport或图像操作消费 |
| 正确性、独立双消费者与性能 | §9、§11～12.4；原Golden复用，新完整record封套与反例/负载/测点/阈值来源已给出，真实目标值不虚构 |

增量自审两个有限视角已完成：实现者从文件介质/原request→完整codec→Pending/commit→scope迁移→Supervisor→恢复/保留逐项追踪receipt与异常，不再靠nullable/文件存在猜Unknown；外部消费者从新建Root/端口构造→独立slot→Factory→无UI/STA binding/controller→预算/权限撤销/重复请求/关窗/迟到→确认移交追踪唯一Owner，核对新Retention不借用旧已撤销fence、面板不直接写事实。文档检查为标题/链接/围栏、类型/构造调用、XAML结构、状态/错误三语覆盖、codec完整字段与新增124-byte向量独立构造/hash；不把这些检查当C#编译、测试执行或UI运行。

剩余项均有准确Owner且仅影响相应实施/运行资格，不是留给实现者选择内部设计：

| 后续输入或资格 | Owner / 影响 |
|---|---|
| 目标包、支持版本、部署审批、维护窗口、保留/法定hold政策、Limit/Benchmark目标与规模 | 消费产品/部署Owner；决定真实操作是否获准与性能阈值，不阻断合成Core |
| 生产TrustStore/SPKI/吊销/密钥代次、受信身份、服务/备份/数据库实际凭据与ACL | 安全部署Owner；缺失拒绝对应新动作，不改签名规则或自动弱化验证 |
| 配置/领域Schema含义、已登记scope/handler、真实数据库事务/checkpoint与恢复闭包 | 各原数据Owner及存储适配Owner；按§6.6实现实际参与者，未知领域事实不由模块补猜 |
| Supervisor实例身份/端点、真实进程退出/资源释放、当前/目标Readiness Policy和checks | Supervisor/宿主Owner；提供受信协议结果及物理运行证据，不改变Bridge映射 |
| FileSystem/Flush/Replace断电保证、客户介质/账号权限与恢复演练 | 部署/运维Owner；需真实存储/目标环境资格，不以BCL或模拟代替 |
| Factory/Adapters/codec/fixture/Tests/WPF/资源与双消费者的实际代码、构建/执行及性能 | 后续授权实现任务在本原会话执行审核；当前没有产品代码或运行证据，不以文档闭合代替验收 |
| 产品Contract/全局错误映射/最终质量与现场签署 | 相应Contract/质量/产品Owner；只影响产品采纳与发布，模块不获得放行权 |

准入状态分别保留：原纯Core/模拟端口/双Host为ModuleCoreImplementationReady（规格）；原UI指定构造内容接收保留，本轮Adapter/codec/完整UI增量为**文档设计闭合**，不批量授予新切片代码准入；适用真实Adapter/WPF/存储/进程/性能/现场资格仍PreparationIncomplete / NotReady / NotEvaluated。DEV-GOV-010门禁未降低；总控只接收此状态，不再等待总控内容复核。达到本轮文档目标后停止，无新工程/报告/脚本/会话/子代理。


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

## 附录 A：模块核心 API Contract v0.1（核心候选契约；逐切片准入）

本节定义本独立模块的核心代码边界，优先于正文中仅针对产品集成的“候选/待采纳”措辞。本文已给出的公开类型、方法、事件、错误键、状态、参数表和代码形状，作为对应切片获准后唯一实施依据；本附录的存在不代表准入通过。实现者不得另造第二套核心 DTO、状态机或错误语义。

- `Module API Contract v0.1` 只覆盖无产品事实写入的 Core、Simulator 和显式 Adapter Port。它不把平台 C-01～C-08、客户工艺阈值、最终放行、产品数据库字段或厂商私有类型冻结为模块 API。
- 正文中仍称“候选”的内容，若属于平台 Schema 映射、序列化、Owner、生产资格或客户 Profile，继续保持候选；若属于本模块 Core 的字段/方法/事件/错误/资源语义，则按本节冻结，任何未定义操作必须先补回本指导再编码。
- 本模块没有视觉算子或 AsunImage API 核验任务。Storage、Supervisor、签名信任和文件端口保持隔离；具体外部适配器须按相应官方版本资料实现并完成真实接入验收，不能反向增加 Core 运行依赖。
- 本轮纯Core、模拟端口与双无UI Host已由主控按DEV-GOV-010 §3.1六项内容接收为`ModuleCoreImplementationReady`，范围与定位见§16.2；UI指定构造内容限定接收。新增或超出本次接收范围的切片仍须逐项接收，未接收保持`PreparationIncomplete`；本次不提升产品集成、运行或生产资格。
