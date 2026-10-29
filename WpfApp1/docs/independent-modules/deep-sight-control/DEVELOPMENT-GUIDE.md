# DeepSight SR/SRI 设备控制与轮廓采集模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`DS-C1, DS-C2, DS-C3`

- 模块键：`deep-sight-control`
- 候选模块 ID：`IM-063`（本轮厂商适配候选；架构总表和会话登记由主会话维护）
- 当前状态：`DesignReview/Prep`
- 文档版本：`0.2.2-prep`（2026-10-11）
- 规划消费者：深视设备调试/回放工具、3D 轮廓采集工具、其它视觉项目的 profile/surface 数据宿主；第二消费者必须独立于平台生产 Shell
- 技术目标：C# / .NET 10 / WPF / DevExpress 25.2.3 / x64
- 来源基线：[DeepSight 只读快照](../../references/project-snapshots/DeepSight/20261004/original/README.md)；文件校验见 [source-manifest.json](../../references/project-snapshots/DeepSight/20261004/source-manifest.json)
- 来源项目：`../../references/project-snapshots/DeepSight/20261004/original`（只读，禁止修改）

本页是 `deep-sight-control` 的唯一开发指导。来源项目的 .NET 8 实现只用于核对设备事实、原生边界和测试思路；没有把来源项目迁移到平台，也没有代码、实机、HIL 或生产验收结论。正式 Contract/Schema/State/Owner 仍须由平台 Contract Owner 采纳后绑定实现。本页不创建第二套平台契约；当前唯一模块 API 为 §3 的 v0.2 准备稿。主控已接收 DS-C1/C2/C3 的 Core/Simulator/双 Host 规格；B1/U1 仅接收指定公开接线内容，未提升为集成或运行资格。

## 1. 目的与边界

### 1.1 负责的事实

模块为深视 SR/SRI 系列线扫激光器提供可独立引用的设备控制与轮廓采集能力：

1. 发现、连接、初始化、DeviceId 租约、断线、重连、停止、排空和释放。
2. 设备能力报告、型号/头（A/B）差异、参数读取/写入/读回、配方 0..63 和配置快照。
3. 单批、连续、高速、异步以及阻塞兼容采集；软件、外部 I/O 和编码器触发。
4. 16/32 位高度、强度、线宽、编码器、时间戳、批次、序号、无效码、质量标志和原始 payload 的保全。
5. 完整轮廓流（不得静默丢帧）与 UI 预览流（有界、latest-wins）的隔离。
6. 帧租约、有界队列、背压、取消/超时、排空和资源释放证明。
7. 原生 ABI 能力探测、导出角色、错误映射、回调隔离和 x64 运行时清单。
8. 可替换的原生适配器、Replay 适配器和 Simulator，使 Core 在无硬件时可验证。

`Complete`、`BatchSealed` 或 `FramePublished` 只表示本模块的结构和生命周期事实，不表示坐标有效、测量完成、质量合格或设备安全动作完成。

### 1.2 明确禁止

模块不得拥有或推断：

- ROI 创建/编辑、边缘或 Pin 算法、工件尺寸、量测、公差、缺陷、OK/NG、质量放行、复判或工单语义。
- PCB/PCBA、AOI、SPI、点胶、涂覆或任何制程目标和工艺流程。
- 运动路径、夹具、急停、安全回路、激光安全联锁或设备级放行决定；`IM-010 motion-control` 只由宿主按其自身权限组合。
- `AsunImage`、HALCON、SImagePro 或任何视觉算法运行时依赖。模块只输出原始或位置化轮廓；需要算法时由 `IM-031 surface-data`、`IM-036 metrology` 或宿主经各自端口处理。
- 深视厂家类型、裸指针、SDK 句柄、私有数据库、产品 ViewModel、隐藏窗口初始化或静态可变全局状态进入公共契约。

调用方负责尝试/工件身份、采集顺序、目标关联、运动编排、工艺解释、结果提交和质量处置。模块不能因为 UI 按下”开始”而自行移动平台、执行 ROI、计算测量或提交放行。

### 1A. 新架构适配要点

**架构门禁**：Core 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；深视 SDK（`DeepSight.SR.*`）只在 Native 适配器程序集内，不进入公共契约。§1.2 已明确”不得有 AsunImage、HALCON 或任何视觉算法运行时依赖”。

**Blazor/Web**：Web 端只展示设备状态、批次计数、最近轮廓 hash；写采集配置必须经已授权维护接口。UI 预览流（latest-wins）与完整轮廓流隔离（§1.1）的约束在 Web 端同样成立。

**AI/HALCON**：本模块输出原始轮廓；视觉算法由 `surface-data`/`metrology` 负责。双跑 CI 不涉及本模块。

## 2. 只读来源与技术裁决

来源快照由 `source-manifest.json` 固定：捕获日期 `2026-10-04`，`fileCount=77`，树 SHA-256 为 `9aba46935cd1a2750146dbbc98fcb754a4573b96f9537ecf03b1774f3f346fe0`。来源 README 和 `docs/development-guide` 的事实必须与以下边界一起解释，不能把其完成状态直接迁入平台。

| 事实 | 当前处理 |
|---|---|
| 来源工程为 .NET 8、WPF、x64 | 仅作只读参考；本模块目标为 .NET 10/WPF/DevExpress 25.2.3 |
| `SR7Link.dll` 版本 `3.3.3.106`、x64、未签名、再分发需审批 | 只允许通过版本/架构/hash/许可证清单的适配器接入；不把 DLL 放入默认包 |
| `SR7Link.h` 登记 81 个函数、7 个回调 | Interop 逐项登记和角色裁决；声明存在不等于公共能力可用 |
| 2.5D 资料缺少 `SR7Link25D.h` | `UnavailableBecauseContractMissing`，禁止猜测签名或存储布局 |
| SImagePro 151 项为资料审计 | 不进入本模块运行时、API、依赖或发布包 |
| 16 位数据需要 Scale，32 位高度和无效值有设备语义 | 必须随 `DataLayout`、单位、无效码和能力快照传递；不得用 0 填补 |

来源的 `README.md`、`docs/development-guide/00..09`、原生 manifest、Core/Interop/WPF/测试文件均是证据，不是本平台的实现承诺。当前来源已包含 `SR7Link.h`，其 81 个函数/7 个回调可作为 Interop 审计输入；仅 2.5D 对应的 `SR7Link25D.h` 和存储契约缺失。任何与目标设备手册、批准 Profile 冲突的地方，以 Contract Owner 和设备 Owner 的新裁决为准。

### 2.1 已查证的通用实现依据

| 依据 | 版本/定位 | 可迁移结论与限制 |
|---|---|---|
| [.NET `BoundedChannelFullMode`](https://learn.microsoft.com/en-us/dotnet/api/system.threading.channels.boundedchannelfullmode?view=net-10.0)、[`Task.WaitAsync`](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.waitasync?view=net-10.0) | .NET 10 文档 | 完整流使用 `BoundedChannelFullMode.Wait`；满时 `TryWrite=false` 必须转为 `Backpressure/Incomplete`。`WaitAsync` 只结束等待，不证明厂家动作已停止。 |
| [`dotnet/runtime` `BoundedChannel.cs` 与测试](https://github.com/dotnet/runtime/tree/9d5a6a9aa463d6d10b0b0ba6d5982cc82f363dc3/src/libraries/System.Threading.Channels) | tag/commit `v9.0.0` / `9d5a6a9aa463d6d10b0b0ba6d5982cc82f363dc3`，MIT，许可证 [LICENSE.TXT](https://raw.githubusercontent.com/dotnet/runtime/9d5a6a9aa463d6d10b0b0ba6d5982cc82f363dc3/LICENSE.TXT) | `Wait` 模式的 `TryWrite` 在满时返回 false，完成不会清空已有数据；同步 continuation 可能造成锁内重入，故创建 Channel 时固定 `AllowSynchronousContinuations=false`。只借鉴语义，不复制 runtime 源码；.NET 10 必须以消费项目测试确认。Channel 锁语义不能宣称 lock-free 或实时保证。 |
| [DevExpress DockLayoutManager 25.2](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)、[GridControl 25.2](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.GridControl?v=25.2)、[PropertyGridControl 25.2](https://docs.devexpress.com/WPF/DevExpress.Xpf.PropertyGrid.PropertyGridControl?v=25.2)、[ChartControl 25.2](https://docs.devexpress.com/WPF/DevExpress.Xpf.Charts.ChartControl?v=25.2) | 官方 25.2 页面；本机程序集仍按 25.2.3 绑定 | Dock/Layout 可保存恢复，Grid 支持虚拟化/排序/条件格式，PropertyGrid 适合绑定不可变草稿，Chart 的 XY 图用于诊断曲线。网页 25.2 分支不等于本机 25.2.3 编译证据；不能用它证明现场布局或 API 编译通过。 |
| [平台 UI 指导 §10](../../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress%20Design%20System开发指导.md#10-精美视觉与高级交互的设计基准) | 现行平台权威 | `SuperTip` 提供作用、限制、快捷键和恢复步骤；关键命令、错误和恢复动作仍必须可见，不能只放在提示或 Flyout。 |

上述资料只约束通用实现形状。设备停止确认、数据布局、参数范围和现场性能仍以目标 SR/SRI Profile、头文件和 HIL 证据为准。

## 3. 分层架构与依赖方向

```text
宿主 / 调试工具 / 工作流
  ├─ 组合 IM-040 ProfileView/BatchSummary、IM-031 surface-data、IM-060 viewport、IM-010 motion
  └─ 注入 DeepSight.Core 的设备命令与数据端口
          ├─ DeepSight.Interop（SR7Link ABI、回调复制、能力探测）
          ├─ DeepSight.Replay
          └─ DeepSight.Simulator
```

模块按 Core、Interop、WPF、Simulator/Replay 与 ProfileBridge 分层；首版纯托管 Simulator 随 Core 验证，稳定发布边界后再独立分包：

### 3.1 Core：Module API Contract v0.2

Core 负责设备控制、能力、参数事务、命令账本和设备资源屏障；不定义通用轮廓、批次或帧租约。以下为**待实现签名规格**，不是已编译代码。所有非 BCL 类型在本页定义；record 在入口深冻结，工厂纯构造，不启动后台任务、不读文件、不加载 SDK。命令只经 `ExecuteAsync` 强类型分派；旧 `ConnectAsync/ReadBatchesAsync` 和弱类型 `object/TypeCode` API 不再是实施依据。

```csharp
namespace Asun.Modules.DeepSightControl;
public readonly record struct OperationId(Guid Value);
public readonly record struct ConnectionEpoch(Guid Value);
public readonly record struct DeviceId(string Value);
public enum SourceKind { Vendor, Simulation, Replay }
public enum SessionState { Created, Connecting, Ready, Configuring, Configured,
    Armed, Running, Stopping, Draining, Disconnected, Quarantined, Closed }
public enum Knowledge { Unknown, Confirmed }
public enum Phase { Rejected, Executing, Confirmed, Unknown }
public enum DrainState { Pending, Unknown, Released }
public enum ErrorCode { InvalidArgument, CapabilityUnavailable, StateConflict,
    NativeLoadFailed, AdapterFault, ReadbackMismatch, ConfigurationUnknown,
    Backpressure, Cancelled, Deadline, DrainUnknown, OperationConflict,
    LookupUnknown, StaleEpoch, UnsupportedVersion, PermissionDenied, Capacity }
public sealed record Error(ErrorCode Code, string DetailKey, string? VendorCode);
public sealed record Budget(TimeSpan Execution, TimeSpan Drain);
public sealed record Limits(int Sessions, int Commands, int Operations, int Events,
    int EventReaders, int Parameters, int BlobBytes, int MetadataBytes);
public sealed record ManagerOptions(Limits Limits, Budget Cleanup);
public sealed record Context(OperationId Id, ConnectionEpoch Epoch, Budget Budget);
public sealed record Revision(string Id, string Sha256);
public sealed record DeviceDescriptor(DeviceId Id, string Model, string Firmware,
    string Address, SourceKind Source);
public sealed record DiscoveryRequest(IReadOnlyList<string> Addresses, Budget Budget);
public sealed record DiscoveryReply(Knowledge Knowledge,
    IReadOnlyList<DeviceDescriptor> Devices, IReadOnlyList<Error> Errors);
public enum ValueKind { Boolean, Integer, Real, Enumeration, Text }
public abstract record Value;
public sealed record BoolValue(bool Data) : Value;
public sealed record IntValue(long Data) : Value;
public sealed record RealValue(double Data) : Value;
public sealed record EnumValue(int Code) : Value;
public sealed record TextValue(string Data) : Value;
public enum Head { Common, A, B }
public enum WriteDepth { Volatile = 1, Persistent = 2 }
public sealed record ParameterKey(string Id, Head Head);
public sealed record Setting(ParameterKey Key, Value Value, string Unit);
public sealed record ParameterDefinition(ParameterKey Key, ValueKind Kind, string Unit,
    Value? Minimum, Value? Maximum, Value? Step, IReadOnlyList<int> EnumCodes,
    int MaxTextBytes, bool ReadOnly, bool CanPersist, bool ChangesLayout,
    IReadOnlyList<ParameterKey> MustApplyBefore, double ReadbackTolerance);
public enum TransferMode { Single, Continuous, HighSpeed, Async, BlockingCompatibility }
public enum TriggerMode { FreeRun, Software, ExternalIo, Encoder }
public sealed record TriggerSetting(TriggerMode Mode, int ProtocolCode);
public sealed record HeadSettings(Head Head, ParameterKey Rate, ParameterKey Exposure,
    ParameterKey Trigger, IReadOnlyList<TriggerSetting> TriggerCodes);
public sealed record FormatSupport(string Id, int HeightBits, bool HasIntensity,
    bool HasWidth, Revision Evidence, ParameterKey SettingKey, int ProtocolCode);
public sealed record OrderConstraint(ParameterKey Lower, ParameterKey Upper);
public sealed record Capability(Revision Revision, DeviceDescriptor Device,
    IReadOnlyList<Head> Heads, IReadOnlyList<TransferMode> Modes,
    IReadOnlyList<TriggerMode> Triggers, IReadOnlyList<FormatSupport> Formats,
    IReadOnlyList<ParameterDefinition> Parameters, IReadOnlyList<HeadSettings> HeadSettings,
    IReadOnlyList<OrderConstraint> OrderConstraints,
    IReadOnlyList<int> InputPorts,
    IReadOnlyList<int> OutputPorts, bool CanQuery, bool CanReboot, bool CanClearError,
    bool CanStop, bool CanReadback, bool CanReadWhileRunning, uint MaxProfilesPerBatch);
public sealed record ParameterSnapshot(Revision Revision, Revision Capability,
    int ActiveRecipe, IReadOnlyList<Setting> Settings, bool ReadbackComplete);
public enum ItemState { NotAttempted, Rejected, Applied, RolledBack, Unknown }
public sealed record ItemReceipt(ParameterKey Key, Value Requested, Value? Before,
    Value? Actual, ItemState State, Error? Error);
public sealed record ConfigurationReceipt(ParameterSnapshot? Actual,
    IReadOnlyList<ItemReceipt> Items, bool RollbackConfirmed);
public sealed record RunPlan(Guid Run, TransferMode Mode, TriggerMode Trigger,
    IReadOnlyList<Head> Heads, string FormatId, Revision Parameters,
    uint ProfilesPerBatch, uint? MaxBatches, TimeSpan MaxRunDuration);
public sealed record DeviceBlob(string Format, Revision DeviceProfile,
    ReadOnlyMemory<byte> Bytes, string Sha256);
public enum IoDirection { Input, Output }
public sealed record IoValue(int Port, IoDirection Direction, bool Value);
public sealed record DiagnosticSnapshot(string DeviceCode, double? TemperatureC,
    ulong? Encoder, int? EncoderBits, IReadOnlyList<Error> Errors);
public enum MaintenanceKind { ClearError, Reboot }
public enum StopReason { Completed, User, Cancelled, Deadline, Fault }
public abstract record Command(Context Context);
public sealed record OpenCommand(Context Context) : Command(Context);
public sealed record ReadCapabilityCommand(Context Context) : Command(Context);
public sealed record ReadParametersCommand(Context Context) : Command(Context);
public sealed record ApplyCommand(Context Context, Revision Expected,
    WriteDepth Depth, IReadOnlyList<Setting> Patch) : Command(Context);
public sealed record SelectRecipeCommand(Context Context, int Recipe) : Command(Context);
public sealed record ExportRecipeCommand(Context Context) : Command(Context);
public sealed record ImportRecipeCommand(Context Context, DeviceBlob Blob) : Command(Context);
public sealed record ArmCommand(Context Context, RunPlan Plan) : Command(Context);
public sealed record StartCommand(Context Context, Guid Run) : Command(Context);
public sealed record TriggerCommand(Context Context, Guid Run, ulong Index) : Command(Context);
public sealed record StopCommand(Context Context, Guid Run, StopReason Reason) : Command(Context);
public sealed record ReadIoCommand(Context Context) : Command(Context);
public sealed record WriteIoCommand(Context Context, int Port, bool Value) : Command(Context);
public sealed record DiagnoseCommand(Context Context) : Command(Context);
public sealed record MaintenanceCommand(Context Context, MaintenanceKind Kind,
    string? DeviceErrorCode) : Command(Context);
public sealed record CloseCommand(Context Context) : Command(Context);
public sealed record Resources(DrainState Drain, Knowledge Counters, int OriginalTasks,
    int Callbacks, long OwnedBytes, bool InputEnded, bool NativeDrained,
    bool ConnectionReleased);
public sealed record RunSnapshot(Guid Run, RunPlan Plan, ulong NextTrigger,
    SessionState State, Knowledge Activity, Resources Resources);
public sealed record Receipt(OperationId Id, ConnectionEpoch Epoch, string? RequestSha256,
    Phase Phase, Knowledge DeviceKnowledge, bool SideEffectPossible,
    SessionState State, Resources Resources, Capability? Capability,
    ParameterSnapshot? Parameters, ConfigurationReceipt? Configuration,
    DeviceBlob? Blob, IReadOnlyList<IoValue>? Io, DiagnosticSnapshot? Diagnostics,
    RunSnapshot? Run, Error? Error);
public enum EventKind { Opened, CapabilityRead, ParametersRead, Armed, Started,
    StartUnknown, ConfigurationUnknown, StopRequested, Drained,
    ResourcesReleased, Closed, Disconnected, Diagnostic, Gap }
public sealed record DeviceEvent(ulong Sequence, ConnectionEpoch Epoch,
    OperationId? Operation, Guid? Run, EventKind Kind, long Timestamp,
    Resources Resources, Error? Error, ulong? MissingFirst, ulong? MissingLast);
public enum DeviceActivity { Unknown, OpenIdle, Acquiring, Stopped, Closed }
public enum StepKind { DeviceCommand, ReadSetting, WriteSetting, RestoreSetting }
public sealed record StepContext(Context Transaction, string RequestSha256,
    uint Index, StepKind Kind);
public sealed record AdapterRequest(Command Command, StepContext Step, DeviceDescriptor Device,
    RunPlan? ArmedPlan, ParameterSnapshot? Actual);
public sealed record AdapterReply(OperationId Original, ConnectionEpoch Epoch, uint StepIndex,
    Knowledge Knowledge, bool SideEffectPossible, DeviceActivity Activity,
    bool InputEnded, bool NativeDrained, bool ConnectionReleased,
    Capability? Capability, ParameterSnapshot? Parameters,
    ConfigurationReceipt? Configuration, DeviceBlob? Blob,
    IReadOnlyList<IoValue>? Io, DiagnosticSnapshot? Diagnostics,
    ulong? CommittedTrigger, Resources Resources, Error? Error);
public sealed record SettingReadRequest(StepContext Step, DeviceId Device, ParameterKey Key);
public sealed record SettingWriteRequest(StepContext Step, DeviceId Device,
    Setting Setting, WriteDepth Depth);
public sealed record SettingReply(OperationId Original, ConnectionEpoch Epoch, uint StepIndex,
    Knowledge Knowledge, bool SideEffectPossible, Value? Actual, Resources Resources, Error? Error);
public interface IDeviceTransport
{
    string Id { get; }
    string Version { get; }
    SourceKind Source { get; }
    ValueTask<DiscoveryReply> DiscoverAsync(DiscoveryRequest request, CancellationToken cancel);
    ValueTask<AdapterReply> ExecuteAsync(AdapterRequest request, CancellationToken cancel);
    ValueTask<AdapterReply> QueryAsync(OperationId original, ConnectionEpoch epoch,
        Budget budget, CancellationToken cancel);
    ValueTask<SettingReply> ReadSettingAsync(SettingReadRequest request, CancellationToken cancel);
    ValueTask<SettingReply> WriteSettingAsync(SettingWriteRequest request, CancellationToken cancel);
    ValueTask<SettingReply> QuerySettingAsync(StepContext original, Budget budget,
        CancellationToken cancel);
}
public enum ActionKind { Discover, Connect, Configure, Acquire, Trigger, Stop, Close,
    ReadIo, WriteIo, Diagnose, ClearError, Reboot, Query }
public interface IDeviceAuthority
{
    bool Allows(DeviceId device, ActionKind action); // 调用时检查；无 IO、有限返回
}
public interface IDeepSightDeviceSession : IAsyncDisposable
{
    DeviceDescriptor Device { get; }
    ConnectionEpoch Epoch { get; }
    ValueTask<Receipt> ExecuteAsync(Command command, CancellationToken cancel);
    ValueTask<Receipt> QueryOperationAsync(OperationId original, Budget budget,
        CancellationToken cancel);
    RunSnapshot? GetRunSnapshot(); // 深冻结本地快照；无设备 IO
    Receipt? GetLatestReceipt(); // 当前知识，不发Query；不冒充缺失操作的回执
    Resources GetResources(); // 包含原transport调用/回调实际资源，Unknown不填假Known
    IAsyncEnumerable<DeviceEvent> ReadEventsAsync(ulong after, CancellationToken cancel);
}
public interface IDeepSightDeviceManager : IAsyncDisposable
{
    ValueTask<DiscoveryReply> DiscoverAsync(DiscoveryRequest request, CancellationToken cancel);
    IDeepSightDeviceSession CreateSession(DeviceDescriptor device, ConnectionEpoch epoch);
    IReadOnlyList<Resources> GetResources();
}
public sealed class DeepSightException : Exception
{
    public Error Error { get; }
    public DeepSightException(Error error); // 待实现构造签名
}
public static class DeepSightFactory
{
    public static IDeepSightDeviceManager Create(IDeviceTransport transport,
        IDeviceAuthority authority, ManagerOptions options, TimeProvider clock);
    public static IReadOnlyList<Error> Validate(ManagerOptions options);
}
public static class DeepSightCodec
{
    public static byte[] EncodeCommand(Command command);
    public static byte[] EncodeCapability(Capability capability);
    public static byte[] EncodeParameters(ParameterSnapshot snapshot);
    public static byte[] EncodeStep(AdapterRequest request);
    public static byte[] EncodeStep(SettingReadRequest request);
    public static byte[] EncodeStep(SettingWriteRequest request);
}
```

`CreateSession` 在 Manager 容量内原子登记 DeviceId/epoch，立即返回 `Created`；无设备动作。重复 DeviceId 返回 DS-003，不新建第二写者；即使旧连接断线或未知也保留租约，只有原 Session 确认 Closed 才退槽。Descriptor 来源须等 transport.Source；发现枚举和 Capability/ParameterSnapshot 是纯托管深冻结值，不需要 Dispose。Manager 不拥有宿主注入的 transport/authority；Session 管理自己经 transport 发起的原 Task、设备资源和回调 Owner，设备释放前不得释放注入实例。

Execute/Query 的预期错误以 Receipt 表示；无法深冻结的 null、未知值变体、非法 UTF8/枚举以 `DeepSightException(DS-001)` 表示，工厂无效配置抛 `ArgumentException`。Dispose 在 Cleanup 预算内复用 Close，未 Closed 时抛 `DeepSightException(DS-011)` 并强持资源；调用方还须 Query，不把异常/方法返回视为释放。Adapter Arm/Apply 不经ExecuteAsync调用：Arm纯Core，Apply由Core按§8以ReadSettingAsync/WriteSettingAsync逐项执行并组装ConfigurationReceipt；transport只做单项映射和知识回执，不拥有第二参数事务。SettingReply.Actual只有读回值已知才非null，write ACK不能造Actual；各步骤带原Context、key、depth与尝试次序在原事务账本中记录。ReadParameters仍经Execute读取全部实际快照，SelectRecipe/Import的读回由Core重用ReadCapability/ReadParameters，并强持各阶段原Task；不能把Adapter自动填猜值算确认。有限预算只观察原任务；SDK不支持取消时不得取消强持或另发同动作。

### 3.1.1 原步骤身份、资源证明与关闭承诺

每个设备副作用和读回阶段先建立 `StepContext`，共享原事务 Context/RequestSha256，Index从0单调递增，Kind依实际操作；调用前冻结完整StepRequest、状态和原Task。普通命令只有DeviceCommand/Index0；SelectRecipe/Import索引0原动作、1 ReadCapability、2 ReadParameters，Command低层类型按阶段变化但Step.Transaction仍是原请求；Apply依确定拓扑每项BaselineRead、Write、Readback，再依逆序Restore/Readback逐步编号。ReadSetting与Readback同Kind但不同Index，不以相同Context当成同一次读。拒绝/超时后Index不回退；序列上限checked且总步骤记录≤`6×Limits.Parameters+3`，预留到元数据预算；未完成步骤不能淘汰。

Transport仅按 `(OriginalId,Epoch,Index,Kind,冻结步骤内容)` 去重，不按OriginalId合并全事务；同tuple异内容DS-012。SettingReply/AdapterReply的Original/Epoch/StepIndex必须匹配且 Resources 有真实计数。普通 QueryAsync查原Index0设备动作；配置事务由Core读步骤账本，只有未确定SettingStep通过QuerySettingAsync查询该原步骤。Core组装整事务Receipt，查询不执行下一项写/回滚；未知写后来查到已执行也只确认已执行，仍需显式ReadParameters确认实际配置，不能声称整Patch完成。步骤Query缺失为DS-013，不证明未执行。

AdapterReply.Resources/SettingReply.Resources是该设备当前真实资源快照，计所有回调/Native持有的托管暂存/未退出叶任务；当前返回reply自身不计。Core的Resources将设备计数、自己在途步骤/排队观察/Blob暂存分别checked合并；不重复计同一原Task，任一Counters Unknown时合并Unknown。只含InputEnded/NativeDrained两个bool而无Counters不能证明资源零。PA缓冲与Host历史复制不进入DS Native归还计数，但必须在各自Root屏障里单独查零。初始未Open的Session为无本会话资源（InputEnded/NativeDrained/ConnectionReleased=true），不得据此宣称物理传感器已停止。

工厂/Session构造只登记托管槽。每个实际设备Owner在一个Host进程中只有一个Manager与一个transport实例；Archive/Inspector若消费同真机共享同Manager/Session，不各建Manager。两独立Simulator fixture是互相隔离的虚拟设备域，不能据此证明跨进程独占；跨进程/另台Host设备占用由宿主设备Owner负责。Manager.Dispose拒新Session/发现，依创建顺序串行复用每个Session Close/Dispose；一次Session失败仍尝试其它已知可关闭Session，整体Cleanup总预算有限而非逐台重新无限延长。未知者保Root、Manager抛DS-011，GetResources继续可查；不Dispose宿主注入transport/authority。

已发Open不确定时Close可以在原OpenTask结束后执行实际Close来隔离资源；Stop只有原Run存在，单纯CurrentState Unknown不能创造Run。Stop或Close新OperationId到达时若原cleanup已存在，作为观察别名复用原Task/原设备身份，返回请求Id并保该别名hash，绝不第二次调用SDK；Query该别名同样观察原操作。Close会内部创建一次原Stop，原内部身份预留独立ID（Factory创建Session时存Guid.NewGuid，不在调用中重选），发SDK前与用户ID冲突检查；冲突拒DS-012且保原资源。Dispose只复用保存的CloseContext，不每次生成新Close动作；Created无动作可直接本地Closed。

权限映射唯一：Open→Connect；ReadCapability/ReadParameters/Apply/SelectRecipe/ExportRecipe/ImportRecipe→Configure；Arm/Start→Acquire；Trigger→Trigger；Stop/Close/Query分别对应同名ActionKind；ReadIo/WriteIo/Diagnose/ClearError/Reboot同名。CreateSession检查Connect但不发动作，所有调用在实际SDK dispatch前再次检查，排队期间撤权必须拒绝。已执行操作的只读查询和本会话已登记Stop/Close收尾责任保留，不因撤权丢Owner；创建Session时Host明确授予本会话查询/清理责任，这不是提升I/O/重启/安全回路或质量权。公共Apply的恢复步骤在当次Configure许可允许范围内，撤权后不发新的恢复写；保Quarantined。事件订阅无设备写，仅允许已建立会话的读取。

### 3.2 Interop

Interop 只包含 SR7Link 原生加载、导出探测、P/Invoke/委托、结构布局、错误码、回调和 native buffer 的受控复制。指针不得越过 Interop；厂家 ABI 类型不得泄漏到 Core/WPF。每个导出必须标记 `PublicControlCapability`、`InternalImplementationEntryPoint`、`CompatibilityEntryPoint` 或 `NotApplicableContractMissing`。

### 3.3 WPF

WPF 层提供可选 `DeepSightControl`/工作台投影，使用 DevExpress 25.2.3。它只能调用 Core 公共接口，不能直接 P/Invoke、持有 SDK 句柄或把 UI 状态写成设备事实。Simulator、Replay 或厂家 Adapter 均由宿主组合根显式注入；控件不暗建设备、不隐藏初始化。外部宿主注入的 Session 由宿主拥有，控件卸载不应自动停用共享设备。

### 3.4 Simulator

Simulator 实现同一 Core 端口，可脚本化设备数量、能力、参数失败、断线、延迟、乱序、丢帧、短帧、无效段、噪声、飞点、批次中断、停止失败和读回不一致。Simulator 输出必须标识 `Source=Simulation`，只能证明逻辑、资源和 UI 行为，不能替代实机数据保真、性能、长稳或安全验收。

Core 只定义设备会话、数据和适配端口，不引用任何具体厂商实现；Interop 实现 Core 所需的原生端口，Simulator/Replay 实现同一端口，最终由宿主组合根注入。依赖方向为 `WPF -> Core contracts`，`Interop/Simulator/Replay -> Core contracts`，宿主装配具体实现。禁止 Core/WPF 反向依赖厂商实现、ROI、IM-040、IM-031、IM-010、宿主页面或私有数据库。

## 4. 与其它模块的组合

| 模块 | 组合边界 |
|---|---|
| `IM-040 profile-acquisition` | DeepSight 是 SR/SRI 厂商设备 Adapter/数据源；IM-040 Module API v0.3 提供唯一 `AdapterFrame/ProfileView/BatchSummary`、位置完整性、缺线和借用合同。ProfileBridge 使用其公开端口，§7给出确定接线；Core不引用IM-040实现，产品采纳/设备资格另验。 |
| `IM-060 viewport` | DeepSight WPF 只提供设备调试/采集投影；统一影像、轮廓和点云显示由宿主选择 IM-060。预览帧必须标记降采样、丢弃和来源，不能成为完整采集事实。 |
| `IM-031 surface-data` | 交付原始 profile、位置/编码器、强度、无效 mask、单位和标定引用；surface-data 决定表面表示、规则/不规则网格和后续数据事实。DeepSight 不做曲面、滤波、补点、参考面或缺陷。 |
| `IM-010 motion-control` | 宿主先由 motion-control 完成运动状态与权限，再把外部触发/位置证据注入采集计划。DeepSight 可读取设备编码器数据，但不拥有运动轴、路径、夹具或急停。 |
| ROI | ROI 工具/宿主可消费已冻结帧租约或 surface-data 结果；DeepSight 不引用 ROI 类型、不生成 ROI、不执行 ROI 量测。ROI 需要的 lease 由公共 Contract 提供，不能从本模块私取 native buffer。 |

### 4.1 DZ-XVision 参考的吸收规则

DZ-XVision 的流程、页面或设备编排只能作为宿主组合体验的参考。可吸收的内容限于：宿主选择连接/参数/采集端口、把状态投影到工作台、把完整 batch 交给 IM-040/IM-031、把显示交给 IM-060，并在宿主层组合 motion-control 和 ROI。不得把整机步骤、板件流程、质量判定、运动路径、配方发布或页面导航写入 DeepSight Core/WPF 公共契约；本模块不因参考流程而获得新的产品职责。

## 5. 有效域、身份编码与公开结果

### 5.1 输入有效域和容量

- Guid 身份非 Empty；DeviceId/Address/版本/参数 ID 使用严格 UTF8、无 NUL、非空、不做大小写折叠或 Trim。每字符串最多 512 UTF8 bytes；TextValue 还受 MaxTextBytes；列表数量不超过 Limits 对应额度；累计字符串/列表/账本计入 MetadataBytes。地址只接受 Host 已授权的 IPv4 地址列表，不扫描任意网段，不接受文件路径。发现容量不足拒绝，不静默截断已发现设备。
- Budget.Execution/Drain、MaxRunDuration 有限正值，使用单调时钟；预定阈值来自 Profile。Limits 各值 >0，Operations≥4（至少一业务项、Stop/Close 保底和一查询任务），Commands≥2。Factory 先 checked 核对总 reservation，再创建对象；拒绝无后台任务。每 Session 原写任务至多 1、原 adapter Query 至多 1，发现原任务至多 1；队列和账本满时拒新动作，不覆盖未知记录。
- Capability 不空且身份/Source 等 Session；Head.Common 只用于公共参数，不用于 RunPlan.Heads。Heads 只 A/B、唯一非空；FormatSupport.HeightBits 只能 16/32；TransferMode/TriggerMode 只接受声明且设备支持的值。SourceKind 明确 Simulation/Replay/Vendor，不混批。
- ParameterKey=(Id,Head) 唯一；Value 变体必须匹配 Definition.Kind。Integer 为 Int64 且原生写宽度由 Interop 目标 Profile 决定；Real 必须 finite；布尔/枚举/字符串精确比较。Real 容差 finite≥0，单位在 descriptor 中非空，`1` 表示无量纲，`mm/us/Hz/degC/count` 为本模块固定单位键；不根据语言改变数值。无物理范围证据的设备参数不暴露为可写，不以类型上限充当量程。
- 数值 min≤max、step>0。整型使用 checked 整数 `(value-min)%step==0`；Real step 表示建议刻度，范围和读回按明确 tolerance，不能假称浮点取模精确。枚举使用 EnumCodes 内的实际协议值，绝不使用列表位置。ReadOnly 禁写，Persistent 需 CanPersist；bool/text 无 min/max/step，枚举只有 EnumCodes，不能混入 numeric bounds。依赖图 MustApplyBefore 唯一且无环；出现缺引用拒绝整能力快照。OrderConstraints各key必须存在、同数值kind/单位，校验合并Baseline+Patch后的Lower≤Upper；未知当前关系值拒写，不能临时猜设备依赖。
- Apply 先验证整个 Patch，无重复 key，Expected 等实际 Revision，然后按依赖拓扑/ParameterKey 排序。RunPlan.Parameters 等完全读回快照；ProfilesPerBatch>0、MaxBatches Single=1/Continuous 为有限正值、MaxRunDuration>0，所有选择须在能力内。Single 等 transfer single；HighSpeed/Async/BlockingCompatibility 的接口模式仍须上限和明确停止证据，不代表任意支持。
- DeviceBlob.Bytes≤BlobBytes，Sha256 为实际原始字节 SHA256 小写 64hex，Format/Profile 版本等目标；不接受路径。Capability.MaxProfilesPerBatch>0；RunPlan.ProfilesPerBatch不得超过该值，Start需CanStop且所选FormatSupport.SettingKey的Actual EnumValue等其ProtocolCode（格式布局有明确证据），各头实际Trigger值等Capability.HeadSettings对所选Trigger的ProtocolCode；HeadSettings的Rate/Exposure为真实同头Real/Hz与Real/us、Trigger为Enum/1，必需键不存在/实际未知拒绝，不按参数名猜值，Apply/Arm需CanReadback。Recipe=0..63；Io port 必须 Capability 清单内；ClearError 要非空 DeviceErrorCode，Reboot 不带该字段。维护/网络副作用不能用 Unknown 重试。

### 5.2 命令、hash 与版本规则

`DeepSightCodec` 为纯 BCL 同步编码，无设备 IO。当前唯一 scheme `ds-command-bin-v2`、contract `ds-api-v0.2`。UTF8 字符串 uint32 LE byte-length+bytes，无 BOM；bool 单 byte0/1；enum uint32 LE，按声明序从0（WriteDepth 使用显式1/2）；int32/int64/uint32/ulong 均 LE；Guid RFC4122 网络16bytes；TimeSpan int64 ticks；double IEEE754 binary64 LE，拒绝 NaN/Infinity、-0规范+0；nullable byte0/1再值；byte memory uint32 byte-length再原始bytes（无逐byte nullable/enum），列表 uint32 count 再各元素。record 按声明字段序，不写 CLR 类型名；union Value 先 kind uint32（Boolean0/Integer1/Real2/Enumeration3/Text4）再相应单字段。

EncodeCommand 顺序：scheme、contract、Context.Epoch、command kind uint32、Budget.Execution、Budget.Drain、payload；Context.Id 不进 hash。kind 固定 Open0/ReadCapability1/ReadParameters2/Apply3/SelectRecipe4/ExportRecipe5/ImportRecipe6/Arm7/Start8/Trigger9/Stop10/ReadIo11/WriteIo12/Diagnose13/Maintenance14/Close15。payload 按各 command 声明中 Context 之后字段序完整编码；无字段为空。集合 Patch 按 ParameterKey.Id UTF8 无符号字典序/Head 排，RunPlan.Heads 按 enum 排，不修改字符串/原始 Blob 字节。Apply/Arm 后续引用的是冻结完整快照，不以 hash 代替 AdapterRequest 实际参数。

EncodeCapability scheme=`ds-capability-bin-v1`，EncodeParameters scheme=`ds-parameters-bin-v1`；均先 scheme/contract，再完整相应 record 字段，省顶层 Revision（含 Id/hash），保嵌套 Revision。Capability 的 Heads/Modes/Triggers/Ports/EnumCodes 排序去重需先验证输入重复（重复拒绝，不能编码时掩盖）；Formats按Id、HeadSettings按Head及TriggerCodes按Mode、Parameters/依赖按key排序、OrderConstraints按Lower/Upper key排序。Settings按 key；保存它们的 SHA256 与 Revision.Id；避免自哈希循环。未来字段/字节序/语义改变更新 contract/scheme，不静默读新值成旧格式。Encode只产生当前scheme，不自行接收未知contract；Blob/映射输入携带未知版本时返回DS-015，无设备动作；本 Core 不保证跨重启 exactly-once，Host须归档原身份/Receipt，设备Owner对账。

同 ID+epoch+hash 返回原任务/不可变回执，不二发；同 ID异 hash→DS-012。新 ID 同 Run Start 或旧 TriggerIndex→DS-003，未知不回退高水位；RunId 在同 epoch 不复用（有界墓碑，满拒新 Arm）。Operation 账本活跃项不淘汰，业务满仍有原 Stop/Close 两保底额度；已完成墓碑可淘汰，之后 Query 为 DS-013 LookupUnknown，不能理解为未执行。取消 Token 不进 hash，预算进 hash；重观察原操作不能修改原命令预算。


步骤规范编码：DeepSightCodec.EncodeStep方案`ds-step-bin-v1`，合同`ds-api-v0.2`，先写request tag（Adapter0/Read1/Write2）、Step.Transaction.Id、Epoch、Budget.Execution/Drain、原RequestSha256字符串、Index、StepKind，再payload。Adapter payload写Command kind/payload（不重复Context）、DeviceDescriptor、nullable完整ArmedPlan/Actual；Read payload写DeviceId/ParameterKey；Write写DeviceId/Setting/Depth。底层Command的Context等Step.Transaction；原动作hash仍取其最外层Command，SelectRecipe重读phase不可拿新的Command hash替旧原hash。步骤SHA256计入账本，异常不会省略原步骤字段；blob与DS所有nested列表仍按本节声明顺序/排序规则。Decode不在当前公开API，宿主只能保完整当前类型/明确版本，不能临时猜二进制反序列化。

固定合成命令编码 oracle（本轮按字段独立复算；不是 C# 产品测试）：CloseCommand.Context.Id=00000000-0000-0000-0000-000000000001（不进hash）、Epoch=00000000-0000-0000-0000-000000000002、Execution=1秒/Drain=2秒、kind15，无payload。完整72bytes，SHA256=`c834aefcb5a74bfa357c2280d558af762a9ff0fcf00c0244d49b2922c9d3cb76`；两个Host从字段独立编码再比较以下字节，不只对常量hex做hash。

```text
1100000064732d636f6d6d616e642d62696e2d76320b00000064732d6170692d76302e32000000000000000000000000000000020f0000008096980000000000002d310100000000
```

### 5.3 结果不变量与 Owner

Receipt 的 Id/epoch 原样回传，RequestSha256 为接纳时 hash；缺失查询 null，Phase/DeviceKnowledge Unknown、Error DS-013、Resources.Counters/Drain Unknown。未知计数 0 只是占位，不证明释放。Counters Confirmed 时所有计数非负，设备运行资源Drain Released需原叶Task/Callbacks/运行暂存OwnedBytes=0、InputEnded/NativeDrained=true；元数据账本单独由MetadataBytes计费，纯托管导出Blob保留值另受BlobBytes×Operations的已预留额度计费，不作为Native运行暂存OwnedBytes；Close 另需 ConnectionReleased 和 State Closed。当前回执 observer 自身不计 OriginalTasks，所有叶adapter/query/步骤Task必须计；sink属于PA轴不得混进DS或重复计费，Receipt观察本身不计，Close当前叶Task返回的资源证明不自等待自己。

Capability只在ReadCapability/SelectRecipe/ImportRecipe（后两者为重读结果）、Parameters只在ReadParameters/Apply/SelectRecipe/ImportRecipe；Configuration 只在 Apply/ImportRecipe；Blob 只在 ExportRecipe；Io 只在 ReadIo/WriteIo；Diagnostics 只在 Diagnose；其它字段 null。Arm/Start/Trigger/Stop/运行中的 Close 带原 Run，其它可为空。Confirmed 要对应设备事实证明；Arm 只证明本地无副作用登记。已发调用+未知结果 SideEffectPossible=true；查询当前已停止不能否定原 Start 曾执行。AdapterReply 必须绑定原命令，不能拿任意新状态改写历史知识。

ParameterSnapshot.ReadbackComplete 只在所有公开关键项均已读回、activeRecipe/Capability/hash一致为true；RollbackConfirmed 要每个已发写项恢复并读回基线。数值不匹配不能把 Requested 写成 Actual。Receipt/事件是深冻结托管值，无须 Dispose；Blob 要复制到本模块有界 OwnedBytes 中；交付采用Core保留深冻结副本、Host另复制到自己的reservation，两份实际bytes分别计费，Core账本保留期间不做未经定义的自动Owner转移，不能持有 native 指针。Core Resources只计设备命令和运行暂存；IM-040 copied payload/消费者借用由其唯一 Owner 计费，不把独立历史副本阻止 native 关闭。

## 6. 状态、命令证明与错误恢复

### 6.1 状态与命令矩阵

Manager 发现任务独立于 Session；Created 未 Open 可以纯本地关闭。已发 Open/Start 即使超时也不能退回 Created/Ready。设备知识、命令 Phase 和 Resources 是正交的，不因某一个轴成功而升级其它轴。

| 入口 | 状态/处理顺序 | 证明和恢复 |
|---|---|---|
| DiscoverAsync | Authority 对 `$discovery`/Discover 检查→有界地址→单发现Task | Knowledge Confirmed可返回零设备；错误不伪装空成功。无 Session 或设备句柄创建 |
| CreateSession/OpenCommand | 先纯构造与登记租约，再 Created→Connecting→adapter Open | OpenIdle且未释放连接才Ready；Unknown为Quarantined，保原Task/租约 |
| ReadCapabilityCommand | Ready/Configured、无在途Run→读取/验证/hash | 首次或能力变化回Ready并失效旧参数；相同且完全读回保持Configured |
| ReadParametersCommand | Ready/Configured、无在途Run→读全部公开项/配方 | 完整读回Configured；部分读回DS-007，留旧快照不覆盖 |
| ApplyCommand | Configured且Expected相同→整Patch校验→依赖顺序写→读回→提交或逆序回滚 | 全确认才新Revision；未知ConfigUnknown投影/Quarantined，允许Read/Query恢复而不Start |
| SelectRecipe/ImportRecipe | Ready/Configured、无运行→权限/版本/hash→一次动作→重新读能力和全部关键参数 | 未读回为Unknown；不自动恢复采集。Import byte附件原样，不猜内部格式 |
| ExportRecipe | Ready/Configured→一次有界读取→验证blob hash | 空/超容量/未知格式拒绝，不能以截断附件成功 |
| ArmCommand | Configured、完全读回、RunPlan/资源/权限有效→Core登记唯一Run | Armed；不调adapter，无物理开始事实 |
| StartCommand | Armed且Run等原计划→一次原adapter Start | Activity Acquiring才Running；ACK不足StartUnknown/Quarantined |
| TriggerCommand | Running+Software，Index等NextTrigger→登记→一次调用 | CommittedTrigger等请求才Confirmed；只证明触发，不证明数据到达；未知也推进高水位 |
| StopCommand | Armed/Running/Stopping/Draining/Quarantined且原Run匹配→原唯一清理 | Armed无Start的Stop纯本地；已Start需Stopped+InputEnded，NativeDrained/资源另证；Known/Released后回Configured（实际能力/参数仍有效）否则Ready，保原RunSnapshot；未知不能回Ready |
| ReadIo/Diagnose | Ready/Configured；Running只在Capability.CanReadWhileRunning且SDK序列化可达时 | Unsupported/查询不可达明确错误，不排队到无期限；温度/编码器未知null |
| WriteIo | Ready/Configured无Run、port属于OutputPorts，Authority再查 | 每次写一次并读回；未知保原identity，不能盲目反写默认0 |
| Maintenance | Ready/Configured无Run，明确支持/授权 | ClearError须原码及错误消除读回；Reboot后Disconnected，设备重启证据不等于重新Ready |
| CloseCommand | 禁新业务→复用Run Stop/Drain→adapter Close | Closed须连接释放、原调用/回调退出且计数Known/零；否则Quarantined |
| QueryOperationAsync | 有限预算读原记录；有原未完写Task时不新增SDK query | 未完写返回已有Unknown；可查时一次原query，观察超时保原Task，不无限轮询堆任务 |
| ReadEventsAsync | reader游标独立、有界metadata广播 | 落后给Gap(first,last)再最早保留；取消只解除该订阅；不是完整数据通道 |

Quarantined 只允许原 Query/Stop/Close、不会造成新副作用的读回（且原写已结束）、显式查询已恢复证据。ReadParameters 确認仅解除配置未知；StartUnknown还须原动作对账/Stop屏障。重新连接采用原Session Close确认后、新epoch/CreateSession/Open；不得假造 Reconnecting 自动恢复运行。SDK卡死只保留隔离Owner；若目标适配必须可强终止，需专用原生Worker隔离切片和设备停止证明，不用Thread.Abort/Task.Run假取消解决。

Close/Dispose成功后GetLatestReceipt/GetResources/QueryOperation仅查询已保留托管账本，不再SDK IO；未知操作仍DS-013。ReadEvents合法after≤当前sequence，首次MoveNext完成当前剩余事件/Closed后正常终止；非法游标/订阅满抛DeepSightException(DS-001/017)，每个reader归还自身计费。Gap的MissingFirst/Last只在Gap非空且first≤last，其它事件null。GetRunSnapshot在从未Arm时null；Stop封口后仍保最近Run/Plan/Activity事实，不以null假称没有未决Run。GetLatestReceipt只是最近结果，不能替代Query原ID；错误拒绝Receipt不覆盖已知原Run/Actual内部快照。

### 6.2 事件与并发身份

事件Sequence每epoch从1递增；事件ring有界并计MetadataBytes，reader不得执行用户回调到SDK线程。Gap只表示诊断事件遗漏，不替代数据完整性；Query补知识。Drained仅在原设备调用/回调真实结束、InputEnded证明后发；ResourcesReleased需模块资源零且Known，Closed另需连接释放。未知时只发诊断/StartUnknown/ConfigurationUnknown，禁止发Drained/Closed。快照Immutable，迟到确认发布新Receipt，不原地修改先前返回值。

命令错误优先级：输入可表示/冻结→同Operation/hash→epoch→权限→状态/未知动作→能力/参数→容量→执行。拒绝不改变实际参数/原Run。不同设备可并行，同一DeviceId单写；所有SDK读写走该设备执行门，不以查询另起线程绕过互斥。Stop/Close保底槽只是保证登记和观察，不保证能越过卡死原调用；不支持独立停采入口时准确报Unknown。

### 6.3 停止、排空和断线

1. Stop接纳后拒新Run/Trigger/参数写，允许本Run在途回调持续保全，不能先清空完整队列。
2. Native返回仅“请求已接受”时保持Stopping；InputEnded/Stopped证明后，等在途回调离开、完整队列已消费/显式拒绝，再确认NativeDrained。PA consumer Task在其Owner内另排空。
3. Close只有原任务退出、SDK句柄释放、委托不再被native调用才ConnectionReleased；Unknown时保句柄/委托/未完Task和设备租约。SDK错误和cleanup异常分别记录，不以finally覆盖原业务错误。
4. 断线使当前批不完整、live epoch隔离；旧迟到live不能推新状态。已封存的历史副本可继续只读；其Owner独立归还，不能因epoch已变而拒绝读取历史。
5. 调用方Cancellation/Deadline只停止观察；Core发起原Run清理使用独立Cleanup预算和原Stop identity，不沿用已取消token。不重发Unknown写动作；错误导致受控Stop属于独立已登记cleanup动作，保留关联原Run/错误。
6. DrainUnknown既不能算性能通过，也不证明机械/激光安全停止。本模块无运动/安全联锁权限；操作员应查询设备并按Host既定恢复流程处理。

### 6.4 唯一错误键与下一动作

| 键/Code | 触发 | 保留与恢复 |
|---|---|---|
| DS-001 InvalidArgument | null/非法值/单位/格式/字符串 | 无动作；修正输入 |
| DS-002 CapabilityUnavailable | 型号/头/模式/端口不支持 | 保能力，换支持配置；不暗降级 |
| DS-003 StateConflict | 重复设备、运行中写、旧Run/TriggerIndex | 保原身份与状态；Query/Stop |
| DS-004 NativeLoadFailed | 缺DLL/架构/hash/导出不符 | 仅原生切片不可用；用已授权来源修复部署，不影响模拟 |
| DS-005 AdapterFault | SDK错误、异常、无必需证明 | VendorCode保留有界，设备可能动作则Unknown/隔离 |
| DS-006 ReadbackMismatch | 请求与实际不一致 | 逐项回执+原值；逆序读回回滚 |
| DS-007 ConfigurationUnknown | 部分写/回滚不确定/布局变更未排空 | 不Arm/Start；读回原操作或人工恢复 |
| DS-008 Backpressure | 完整数据/临时blob超容量 | 显式不完整/拒绝并受控Stop，不能丢后Complete |
| DS-009 Cancelled | token取消 | 未发可Rejected；已发Unknown，保原Task并清理 |
| DS-010 Deadline | 执行观察到期 | 保原identity/资源；Query，不等于SDK已退出 |
| DS-011 DrainUnknown | 原Task/回调/资源/Close未确认 | 强持Owner，不回池、不重连接同设备 |
| DS-012 OperationConflict | 同ID异hash | 零新动作；查原请求 |
| DS-013 LookupUnknown | 历史缺失/淘汰/进程重启 | Unknown；设备对账，不推断从未执行 |
| DS-014 StaleEpoch | 新live/命令引用旧epoch | 拒绝live；历史已封存数据不受此限制 |
| DS-015 UnsupportedVersion | API/blob/映射版本不支持 | 不动作、不原地重写旧文件；显式适配 |
| DS-016 PermissionDenied | Host撤权/操作未授权 | 零动作；仍保原任务查询/cleanup责任 |
| DS-017 Capacity | Factory/会话/队列/账本/根额度满 | 构造前拒绝，原Unknown不删除腾槽；cleanup保底可用 |

Error.DetailKey固定上述键，VendorCode nullable有界；UI按键与Receipt事实投影恢复句，不能把厂家自由文本当本地化合同。异常只用于不可表示输入、Dispose未知或非预期故障；每个异常仍须被Root消费并保留原资源，不以异常证明无动作。

## 7. 完整轮廓 Bridge、预览与 IM-040 接线

### 7.1 唯一公开数据合同与可构造的 Bridge

当前接线消费 [IM-040 API v0.3](../profile-acquisition/DEVELOPMENT-GUIDE.md#3-module-api-contract-v03) 的AdapterFrame/ProfileView/BatchSummary/IProfileIngress/ICompleteProfileSink/IProfileSensorAdapter。Core不定义RawProfile/ProfileBatch/DeepSightFrameLease；架构“批次”责任由PA唯一Owner封口，不能用旧聊天名字编译。以下在ProfileBridge工程待实现，输入/依赖由Host显式提供，无SDK隐藏初始化：

```csharp
namespace Asun.Modules.DeepSightControl.ProfileBridge;
using DS = Asun.Modules.DeepSightControl;
using PA = Asun.Modules.ProfileAcquisition;
public sealed record HeadMapping(DS.Head DeviceHead, PA.HeadId ProfileHead,
    DS.ParameterKey Rate, DS.ParameterKey Exposure, DS.ParameterKey Trigger);
public sealed record TriggerCode(PA.TriggerMode Mode, int DeviceCode);
public sealed record FormatCode(string FormatId, DS.ParameterKey Key, int DeviceCode,
    PA.Revision? Calibration);
public sealed record EncoderCode(string EncoderId, DS.ParameterKey Key, int DeviceCode,
    PA.Revision Calibration);
public sealed record ProfileBinding(DS.ConnectionEpoch DeviceEpoch, PA.Epoch ProfileEpoch,
    PA.Revision Revision, IReadOnlyList<HeadMapping> Heads,
    DS.TransferMode Transfer, PA.Capability Capability,
    IReadOnlyList<TriggerCode> TriggerCodes, IReadOnlyList<FormatCode> FormatCodes,
    IReadOnlyList<EncoderCode> EncoderCodes);
public sealed record BridgeLimits(int Operations, int OriginalTasks, int MetadataBytes,
    long RawCopyBytes, int RawCallbacks);
public sealed record InputResources(DS.Knowledge Counters, int Callbacks,
    int OriginalTasks, long OwnedBytes, bool InputEnded, bool NativeDrained);
public interface IProfileInputBinding
{
    InputResources GetResources();
    ValueTask<InputResources> CloseAsync(DS.Budget budget, CancellationToken cancel);
}
public interface IDeepSightRawSource
{
    string Id { get; }
    string Version { get; }
    DS.SourceKind Source { get; }
    IProfileInputBinding Bind(ProfileBinding binding, PA.RunPlan plan,
        PA.ParameterSet parameters, PA.IProfileIngress ingress);
}
public interface IDeepSightProfileAdapter : PA.IProfileSensorAdapter
{
    void AttachEpoch(PA.Epoch epoch);
    InputResources GetResources(); // Bridge与raw自己的资源；不冒充DS/PA资源
    DS.OperationId? GetOriginal(PA.OperationId operation, uint stage);
}
public static class DeepSightProfileBridgeFactory
{
    public static IDeepSightProfileAdapter Create(DS.IDeepSightDeviceSession session,
        IDeepSightRawSource raw, ProfileBinding binding, BridgeLimits limits,
        DS.Budget cleanup, TimeProvider clock);
}
```

Factory深冻结且纯构造：不Open、不raw.Bind、不注册callback、不创建原Task。所有limits正，Operations≥4（业务+Stop/Close保底）、OriginalTasks≥8，metadata/raw实bytes先预留；构造无效ArgumentException。每次原PA请求和全部派生DS阶段/原Task在Bridge有界账本登记后才调用；异常/超时保持原记录，活跃项不淘汰。session/raw/clock是借入由Host Root持有；raw自身设备Owner必须与session同transport/物理设备，不能另开第二SDK句柄。

DeviceEpoch必须等session.Epoch，ProfileEpoch不预猜：Host先以Factory返回adapter创建PA Session，取其Epoch后通过 `AttachEpoch` 固定到该adapter；因此ProfileBinding.ProfileEpoch在Factory为Guid.Empty占位且不得Bind数据。公开入口补为 `void IDeepSightProfileAdapter.AttachEpoch(PA.Epoch epoch)`：只一次纯托管绑定，epoch非空；相同重复幂等、不同值拒DS-014，无IO。Attach后所有PA Context.Epoch匹配才执行；Host从未Attach则PA-013 StaleEpoch。此单一装配步骤消除预定PA epoch与PA工厂自己生成epoch冲突；Binding实例身份在Attach后冻结（静态Binding.Revision按§12.3编码，不因实例epoch改变），不擅自让PA工厂接受外部epoch。

Source按名称映射DS Vendor/Simulation/Replay→PA Vendor/Simulation/Replay，不整数强转（序不同）；Knowledge同样DS Unknown0/Confirmed1→PA Unknown1/Confirmed0。Head只A/B一一映射非空唯一PA HeadId；Binding.Capability.DeviceId=session.Device.Id、AdapterId/Version等raw。每个Head Rate/Exposure/Trigger key须同该head且等DS.Capability.HeadSettings中明确键，FormatCodes须等DS.FormatSupport.SettingKey/ProtocolCode，真实Capability内类型/单位分别Real/Hz、Real/us、Enumeration/1。TriggerCodes一一映射PA.FreeRun/Software/External/Encoder→DS.FreeRun/Software/ExternalIo/Encoder和实际协议值，缺/重/未支持拒绝。

确定桥范围：单行未压缩I16/I32高度与可选U8/U16强度/线宽；Binding.Capability给每头FormatSpec完整scalar/布局/单位/无效码及证据。FormatCodes把FormatId映射到设备实际格式参数/协议码，EncoderCodes把EncoderId映射到编码器参数/协议码及Calibration，均唯一且在DS能力中；Common键一次写，分头键逐头写。PA EncoderId非空必须同EncoderCode和每头EncoderSpec，PA Calibration需同其Calibration；CalibratedHeight的FormatCode.Calibration必须与参数Calibration相同，才允许主plane.Unit=mm和真实Scale/Offset；其它PA域遵循PA原规定。不从数据内容猜标定/坐标，也不把原始encoder原码推断成设备实际位置。若无EncoderId而使用标定高度，Calibration取FormatCode.Calibration；RawCode主plane.Unit=code/Scale1/Offset0，宿主可显示物理证据换算但不升级坐标资格。Image/私有压缩/Disparity不在当前线扫SR/SRI桥实现范围，SDK支持时须补相应格式映射和验证，不能按通用PA能力猜布局。

PA Capability与DS Capability是不同scheme，绑定保存两份完整值/Revision对应，而非要求hash相同；DS实际型号/firmware/Heads/format/参数定义/支持trigger/频率曝光要逐项匹配Binding且有证据，改变后旧Binding拒绝PA-003/PA-019，不能拿旧Capability回执仍使用。Host在Bridge管理Run时Authority禁止UI直接Arm/Start/Apply/切Recipe；设备面板仍查询/Stop/Diagnose，防两套Run Owner混用。

在Bridge使用PA Replay/Simulator source path时，source必须通过 `PA.ProfileSourceFactory`/`PA.ProfileInputCodec` 构造，再由 `CreateAdapter` 接入本桥；DeepSight 不复制 `SourceRecord` codec、End 编码或另造 source reader。§12.3 的 `DeepSightProfileSimulationFactory` 是设备回调/transport 模拟器，可继续驱动 `IDeepSightRawSource` 验证Bridge映射，但不替代PA source path。Source的 `Frame`/`Signal` 原身份、序号、时间、invalid 和 payload 原字节必须逐条保留，仅按本次PA session映射当前 `Epoch/Run`；显式 `SourceRecordKind.End` 的 lease 在确切EOS验证后才归还，并由adapter至多发一次 `InputEnded`。`InputEnded`/End 不是 DS Stop、NativeDrained 或 ConnectionReleased 的替代证明。Bridge账本须登记PA source的原reader task、每个 `IProfileRecordLease` 和 `SourceDrain`；同一source至多一个在途reader/未归还lease，Close/Query只观察原source任务，迟到lease归原Root，不能以观察超时、End到达或reader返回代替实际归还。Vendor source不得绕过设备Owner经此通用source adapter伪装。

### 7.2 命令、阶段身份与恢复映射

每个PAOperation原ID/epoch/hash在Bridge账本保留。全部DS内部阶段使用确定映射 `ds-pa-step-id-v1`：ASCII方案字节（无长度）+RFC4122 ProfileEpoch16bytes+PA原OperationId16bytes+stage uint32 LE，SHA256前16bytes作为RFC4122 GUID（不改版本位）。Empty或已登记碰撞→PA-016零新动作，不换随机ID；映射(stage,完整两端命令/hash/原Task)先登记，GetOriginal公开可查。Core继续校验相同DS ID异hash拒绝；有冲突的Arm无物理动作，任何后续阶段冲突都停链并清理已建raw binding，不能Start。阶段ordinal在下表固定，内部阶段时间只分摊原PA Execution预算，不每步重置总期限；cleanup用独立已冻结cleanup预算。

Source adapter 的 `ReadNextAsync` 只能使用当前原PA命令剩余的 `Budget.Execution`，`Source.CloseAsync/QueryAsync` 使用同一原PA `Budget.Drain` 或已冻结 cleanup 预算；每条record、每个DS阶段和每次Query不得重新给一整段预算。PA source 的 `SourceDrain.State=Released` 只有原reader、lease、source owned bytes 和计数都已确认归还后才能映射为 Bridge `InputResources.InputEnded/NativeDrained`；`Pending/Unknown` 必须保留原Root/原epoch并阻止退槽。

| PA入口 | 固定阶段/DS动作与InputBinding | 结果证明 |
|---|---|---|
| Open | stage0 DS Open；无条件调用Core，其已Open时只接受先前桥登记的同原PA操作 | OpenIdle确认才PA Confirmed；Host必须以Created DS Session交Bridge，不用“已Ready只读复用”冒充原Open |
| Discover | stage0 ReadCapability | 验证Binding真实匹配后返回PA Capability；不自动ReadParameters，不暗改设备 |
| Apply | stage0 ReadParameters→1 DS Apply（必要时）→2 ReadParameters确认 | 每所选头rate/exposure/trigger和格式/编码器显式键完整映射，实际不可省；无Patch改变仍以完全读回作证，保完整PA Requested/Actual/FieldReceipt |
| Arm | PA Core本地，不调用Adapter | 本Bridge收到Arm拒PA-003 |
| Start | stage0 ReadParameters→1 DS Arm→2 DS Start；Read验证DS参数Revision仍等Apply的pair，Arm确认后raw.Bind，再Start | PA Plan.Heads按HeadMapping转DS、profiles各头须相同；模式PA.Single→Transfer Single，PA.Continuous→Binding.Transfer非Single；差异profiles/无上限本版拒，不能截断；DS Run=PA Run.Value、MaxBatchesPerHead/MaxRunDuration原样，Trigger/format来自原AppliedParameters |
| Trigger | stage0 DS Trigger，Index原样 | DS Receipt Confirmed且原请求索引确认才CommittedTriggerIndex；Receipt.Run.NextTrigger须Index+1，无数据关联证据不能造TriggerObserved |
| Stop | stage0 DS Stop→InputBinding.Close同一个原Task | DS Stopped/InputEnded真实证明后才结束raw输入；raw.Close在原callback退出才NativeDrained； PA Core自行排sink借用 |
| Close | stage0 DS Close（Core复用原Run Stop）→InputBinding.Close（可证明已停才解除） | DS.ConnectionReleased与raw Counters Known/零/NativeDrained共同确认；失败仍有限观察，不放弃raw强持 |
| Query | 原Bridge各阶段账本→已发DS阶段QueryOriginal、raw原Close观察 | 不执行未发的下一阶段；Unknown保持原PA身份，不凭查询“补发Start/参数”；原Task迟到仅更新知识 |

Apply只请求所选Heads；未选头保基线。PA ParameterSet.Heads/格式/Trigger必须支持且唯一；Hz/us的null表示读当前各头实值，各头不一致则PA-004而非取首头。触发码显式TriggerCodes，格式码显式FormatCodes，EncoderId有值用EncoderCodes；无EncoderId不得凭空写默认编码器码，保实际参数且输出null位置来源。若“禁用编码器”有设备副作用，必须以独立Capability/明确参数Patch先配置，不由null暗发。禁止Enum.Ordinal直接写。DSApply期望Revision等stage0实际；成功后PAActual按全部实际rate/exposure/trigger/格式码/编码器与冻结标定引用/所选Heads构造，Revision用PA自己的source编码重建，其Revision.Id=`ds-pa-actual-v1`；PA.Requested保原Revision/字段，无需等Actual hash。绑定保存(actual PA Revision,actual DS Revision) pair，PA Start.Plan.Parameters须等PA.Actual，stage0 DS Read须等pair.DS，变化拒绝。

PA.AdapterReply.Activity和Proof：Open→OpenIdle；Start→Acquiring；Stop→Stopped/InputEnded；Close→Closed/NativeDrained/ConnectionReleased；来自匹配DS Receipt/Run和rawResources，不能只按enum当前State猜。普通DS Query的原Phase Confirmed允许证明原动作曾发生，当前Session/Run是否Stopped另由GetLatestReceipt/GetRunSnapshot/GetResources；DS.Stop资源屏障后保RunSnapshot Activity Confirmed、State Configured（或能力失效Ready），PA映射仍Stopped。GetOriginal未找到null→PA-017，不以null证明未发。

DS错误映射固定：001→PA-001/InvalidArgument；002→PA-002/CapabilityUnavailable；003或016→PA-003/StateConflict（VendorCode可存DS-016，不发权限拒绝为未知成功）；004/005→PA-014/AdapterFault；006/007→PA-004/ConfigurationPartial；008/017→PA-010/Backpressure；009→PA-011/Cancelled；010→PA-012/Timeout；011→PA-015/ResourceDrainUnknown；012→PA-016/OperationConflict；013→PA-017/LookupUnknown；014→PA-013/StaleEpoch；015→PA-019/UnsupportedVersion。保DS原码在PA.VendorCode有界且不塞自由文本；PA Knowledge由原事实映射不数值强转。

Bind只登记映射和callback上下文且无采集动作，有限分配计RawCopyBytes/MetadataBytes；若注册SDKcallback有IO，必须由transport Start步骤的Owner执行，不在同步Factory/Bind暗发。InputBinding.Close幂等、仅解绑已停止后的回调，不调用设备Stop；重复预算观察原CloseTask，不丢借用ingress。未证明停止时返回Unknown并保持注册，不能先解绑丢在途payload；没有Bind的Close为已知空资源。Bridge.GetResources只计自己的metadata任务/binding/rawCopy，DS/PA各轴另查询；Close后账本历史值依Profile保留不能当Native持有。

派生身份合成oracle：ProfileEpoch=00000000-0000-0000-0000-000000000002、PA OperationId=00000000-0000-0000-0000-000000000001、stage1。完整52bytes=`64732d70612d737465702d69642d7631000000000000000000000000000000020000000000000000000000000000000101000000`，SHA256=`bdb0dd31cc29d73ab39d8be3449294aa3270451acad28f3d316fed421983979b`，派生DS GUID=`bdb0dd31-cc29-d73a-b39d-8be3449294aa`。本轮按字段复算，Bridge测试从字段重建，不直接hash固定hex。

### 7.3 callback 到 PA ingress 的保全

厂家raw callback在native指针有效期内校验checked长度/stride/offset/epoch/Head/Batch/序号。由于PA Payload是ReadOnlyMemory<byte>，首版RawSource在RawCopyBytes内预留并将native span复制到有界托管buffer，再构造PA.AdapterFrame的**借用**视图并调用TryAccept，不把裸指针硬转换ReadOnlyMemory。PA Core同步复制后才返回Copied；source不能在Copied之前释放/覆盖指针所对应内存，Refused/Stale不会获得Owner转移。Bridge不另建完整Channel，完整有界队列使用IM-040的Wait+TryWrite/预算。首版source native→托管一次、PA同步保全再一次，两次actual bytes和Owner分别计；TryAccept返回后RawSource可归还自己的暂存。Simulator已是托管fixture时可以直接借原immutable bytes而不重复native复制；优化unmanaged MemoryManager是后续明确切片，当前不假称零复制。

- Callback不await磁盘/UI/消费者，不抛异常跨ABI；完整队列满/池空/越界→PA Refused及Backpressure/Rejected，不完整封口并请求原Run受控Stop。停止接纳新Run与保全原Run在途callback分开；仍有在途数据时不得先Complete Channel或丢队列后Complete batch。
- 使用PA source时，Bridge在 `TryAccept`/`TrySignal` 返回后只按PA规则释放当前Frame/Signal lease；`Refused`、取消或异常不转移source所有权，必须等原source任务结束并由 `SourceDrain` 确认。End lease也必须走同一归还路径；不得把PA source的lease归还、`InputEnded`或`SourceDrain.Released`写成设备已Stop/NativeDrained，迟到reader仍由原Root持有并可被Query对账。
- Mode/32位路径高度通常为signed Int32；16位高度为signed Int16，强度可能unsigned U16且使用其独立Scale。原源 `Sr7LinkClient` 的 short/ushort路线可作为布局候选，具体32位0.00001mm、16位Get16BitScale及灰度scale不能直接冻结为全部型号事实。FormatSpec逐plane冻结Scalar/端序/Scale/Offset/Unit/InvalidCodes与证据，缺证拒绝有效高度，不把灰度scale用于Z。
- 飞点/弱信号/遮挡/厂家invalid保留原字节与InvalidSpan；不补0、不插值、不抹除序号。Position.Unknown保持Unknown，没有真实位置不生成规则网格。编码器RawCount/Bits/segment和设备ticks/domain必须保全；跨设备钟不自动当同域。
- BatchEnd/InputEnded/Disconnected/Fault使用PA.AdapterSignal公开形状，匹配Run/BatchKey/epoch；仅停止ACK不足以InputEnded。触发Ack不凭空关联帧。A/B分头batch，不能把头缺失压成一头Complete。

### 7.4 两消费者和预览

ICompleteProfileSink.OnProfileAsync中的ProfileView只在原返回Task退出前借用有效；异步超时不代表Task退出。需要长期读的Archive/Inspector分别在其Root字节额度内复制全Payload与深冻结metadata/hash/Invalid/Position，不能持有借用后返回。两个消费者有各自副本Owner；关一个不清另一个。PA封口规则及hash原样保存，不从UI重建。

预览使用 [IM-040 §8.0](../profile-acquisition/DEVELOPMENT-GUIDE.md#80-module-wpf-api-contract-v02) 的 `IProfilePreviewStore/IProfilePreviewLease`；只有明示预览投影允许latest-wins，最多一个待刷新项，替换前按实际bytes预留新项，不抢回当前Present仍借用的lease。PreviewDropped是投影计数，不把预览丢弃计为生产缺失。Z/强度图的Invalid画空洞，不跨遮挡连线；选Grid中的Head/Batch/Sequence只定位相应只读快照，不能把旧选择静默替换成新数据。

## 8. 参数、配方、I/O 与持久化操作卡

### 8.1 参数事务的唯一步骤

角色为设备调试/维护人员，Host授权后选择设备和目标头；输入ApplyCommand仅是设备设置，不含工单、ROI、量测或质量。动态Capability.Parameters是唯一Schema，Category/Item/原生宽度只在Interop映射文件登记，不进入操作员输入。

1. 读取并保留完整ParameterSnapshot作为Baseline；Expected不符或无CanReadback先拒绝，无写动作。
2. 深冻结Patch，校验类型/单位/范围/步长/ReadOnly/目标头/Depth/能力依赖；整份不合法则全部NotAttempted。
3. 运行中Apply拒绝，不暗自Stop后重启。Host显式Stop/Drain后再提交；ChangesLayout的项要等旧raw binding回调释放，再由新Binding建立新Run。
4. 按MustApplyBefore拓扑次序，独立同级按Key排序；写前登记原Task/每项尝试证据。每项写ACK后读回，Bool/Int/Enum/Text精确相同、Real在明示容差才Applied。
5. 全部Applied且最终能力/配方仍一致，生成新实际Revision/ParameterSnapshot；Requested永远不覆盖未知Actual。
6. 某项失败时停止后续写；只有原调用已真实退出、写入知识可确定且恢复已授权时，按已写顺序逆序恢复Baseline。当前项/SDK仍在途或动作未知时先查原操作，不发新逆向写覆盖未知。每个回滚仍需读回证据，使用独立Cleanup预算而不是已取消token；rollback只是同原配置事务的恢复阶段，不替换原OperationId。
7. 回滚全确认→返回旧Baseline/RollbackConfirmed=true，不自动Start；任何未知→Quarantined/DS-007，保逐项Requested/Before/Actual/错误。查询/重新读回解除未知前阻新Run。

WriteDepth `Volatile=1/Persistent=2`是协议值，不能传UI索引0/1。来源Z ROI offset有符号16位、-32768..32764且4倍数，height无符号32位且8倍数、A/B Target0/1、配方0..63和动态频率等是**目标Adapter候选映射**，需对应设备资料与固件Profile收窄后纳入Capability；不在通用Core硬编码某型号列表或读回容差。旧项目 `ApplyRestartsAcquisitionAfterSuccessfulParameterChange` 行为不迁入，平台必须显式启动新Run。

### 8.2 配方/诊断/维护操作

| 任务 | 输入→步骤→输出 | 失败恢复与验收 |
|---|---|---|
| SelectRecipe | Recipe0..63→无运行/授权→一次切换→重读能力和关键参数/activeRecipe | DS-007保旧快照/新号未知，不回写旧号盲重试；边界0/63成功，-1/64零动作 |
| ExportRecipe | 设备有界读取→DeviceBlob.Format/Profile/hash→交Host | 超BlobBytes拒绝，不截断；无文件路径进入SDK合同 |
| ImportRecipe | 明确设备Profile/hash/容量→一次加载→读回全部关键项 | 设备可能接受后超时Unknown，查询原ID；不把JSON草稿自动转换厂商二进制 |
| Read/WriteIo | Capability端口/方向→现场Host授权→单写/读回 | 输出未知不自动置0；模块不承担安全回路/急停；撤权零新动作 |
| Diagnose | 无干扰读→温度/编码器位宽/原码快照 | 无温度/位宽证据为null，不填0假正常；脱敏记录设备/版本 |
| ClearError | 保留原ErrorCode→一次清除→重新读取错误 | 清命令Ack不证明原因消失；仍Error保恢复建议 |
| Reboot | 明确维护权限/支持→一次重启→Disconnected | 新会话须原任务/连接排空后显式Open，不自动Start |

### 8.3 本地文件与回放职责

Core不读写文件或产品数据库；Host利用已批准存储端口保存DeviceBlob、原DS Receipt与PA完整副本。写入使用临时对象→校验hash/长度→原子提交→版本化索引；失败保最后完整版本，不把部分成功注册为配置。文件路径由Host在授权目录内校验，拒绝越界/重解析点/未授权覆盖；SDK只接收Bytes，不接受操作者拼接路径。

PA数据/事件/Receipt编码直接使用IM-040 `ProfileContractCodec` 当前scheme，原始Payload全字节（含padding）单独hash；本模块不发明第二Replay格式。DS参数/能力由DeepSightCodec编码，版本前缀和完整冻结值保留；未知schema只读拒绝/显式迁移。跨版本回退保旧副本，不原地篡改hash，不自动恢复采集。这些是Host适配规则，正式Store接线/耐断电文件事务证据属于产品集成门，不用纯Core单测冒充。

## 9. ABI、借用、资源与部署

### 9.1 原生事实及未确认范围

SR7Link.dll仅x64、来源版本3.3.3.106；原manifest SHA256=`16ce6456de5a9c43c24464ca491f32c154f9d3aab593950cb7be56858f1c10b9`，header SHA256=`891b5c55c0cc99473d5e1fc3bc394d94e3eb89ae11352ebf70615af17f879f59`。SR7Link.h的81函数/7回调按`PublicControlCapability/InternalImplementationEntryPoint/CompatibilityEntryPoint/NotApplicableContractMissing`角色分别登记。原运行时MSVCP120/MSVCR120等依赖以只读manifest为部署输入，现场包固定来源路径/架构/hash，不随机加载厂家Debug/Release文件。按用户已授权工具直接使用，不新增许可核验作为Core阻断；原厂家再分发元数据保留，实际包由部署Owner处理。

每个实际P/Invoke的calling convention、字符集、结构SizeOf/OffsetOf、pointer方向、长度、错误码以目标头文件确认；C#公开签名有疑义只看消费侧公开声明，不扫描AsunImage内部。本模块不依赖AsunImage/HALCON，不做算子编译核对。2.5D九个导出仍缺匹配SR7Link25D.h/布局，只阻2.5D；不试调用猜ABI。

### 9.2 Owner 和两类数据屏障

| 资源 | Owner/生命周期 | 归还屏障 |
|---|---|---|
| Manager/Session/原Task/identity | Host进程Root；Session内执行器登记 | 所有原叶Task退出+Close证明；Observer返回不退槽 |
| SDK句柄/委托/native buffers | DeviceTransport/RawSource设备Owner | 已停止事实、回调退出、句柄Close确认；未知强持 |
| PA ingress完整暂存 | PA IProfileBufferPort/Session | sink原Task退出后归还；只认PA资源快照 |
| Host Archive/Inspector历史副本 | 各Host有界reservation | 各自显式归还；旧epoch仍可读，互不清空 |
| UI IProfilePreviewLease/Present借用 | 各view/preview store | 原PresentTask结束/真实Clear确认，不能超时强收 |
| 文件流/原子暂存对象 | 已授权Store/Host | 原IO Task和commit事实，业务异常和cleanup分别保存 |
| 注入transport/authority/text/viewport | 注入Host | 模块不擅自Dispose共享实例；最后借用者离开后Host释放 |

数据已被PA复制后，native资源和已封存历史副本可以独立关闭；不能因为历史epoch而拒绝合法只读，也不能为了native关闭抢收仍借用native内存的引用。Core不发布native lease；任何适配器若无法复制保全就拒绝并标不完整，不把其指针交给Host。

### 9.3 卡死/资源未知

Task.WaitAsync到期、Cancellation、GC、窗口关闭、进程Task fault均不等于资源释放。原调用卡死时保持设备独占和原对象强引用；不循环重建session、无限poll或回池句柄。原生Worker隔离只在明确的新适配切片中定义IPC/workerOwner/退出及设备停止证明，当前不宣称已提供可杀Worker；卡死不阻纯托管模拟。失败/异常/取消均保VendorCode与请求身份，不自动重发激光、I/O或重启。

### 9.4 SR7Link 适配器的可执行装配与模式矩阵

Interop 的设备实现必须由下列唯一工厂和配置记录装配；名称是本模块自己的公开适配边界，SR7Link 类型仍为内部类型：

```csharp
public sealed record Sr7LinkRuntimeOptions(
    string NativeRuntimeDirectory, string ExpectedSha256, string ExpectedFileVersion,
    string Architecture, TimeSpan ProbeBudget);
public sealed record Sr7LinkProbe(
    string FileVersion, string Sha256, string Architecture,
    IReadOnlyDictionary<string, bool> Exports,
    IReadOnlyList<string> MissingRequired, IReadOnlyList<Error> Errors);
public sealed record Sr7LinkAdapterOptions(
    Sr7LinkRuntimeOptions Runtime, bool AllowLegacyConnection,
    bool AllowBlockingCompatibility, uint MaxLinesPerCallback,
    IReadOnlySet<string> EnabledModes);
public static class Sr7LinkAdapterFactory
{
    public static Sr7LinkProbe Probe(Sr7LinkRuntimeOptions options);
    public static IDeviceTransport Create(
        Sr7LinkAdapterOptions options, Sr7LinkProbe probe,
        IDeviceAuthority authority, TimeProvider clock);
}
```

`Probe` 只检查绝对目录中的 `SR7Link.dll`、PE x64、版本、SHA-256 和 81 个登记导出；缺失必需导出返回 `NativeLoadFailed`，不加载其它目录、不修改进程 `PATH`，也不把 2.5D 的 9 个契约缺失导出列为必需项。`Create` 只建立托管 transport 和执行门，不打开设备；`ExpectedSha256`、`ExpectedFileVersion`、`Architecture=x64` 为空或不匹配时拒绝。进程内 native handle 由 runtime 单例持有，`Dispose` 只撤销本实例使用资格；没有所有设备 Session 的 `Closed/ConnectionReleased` 证明前不得卸载 DLL。`ProbeBudget` 只约束探测等待，不覆盖设备命令的 Execution/Drain 预算。

下表是每种能力的唯一调用顺序、结果归属和默认选择。括号内是已在只读 `Sr7LinkClient`/`Sr7LinkNativeMethods` 中核对的导出；Interop 只能在这些步骤内调用，不能让 Core 直接调用导出。

| Core/设备能力 | SR7Link 调用顺序 | 默认和适用边界 |
|---|---|---|
| Discover | `SearchOnline(timeout)`→校验返回计数 `0..256`→复制 IPv4 | 只返回发现事实；不创建 Session、不自动 Open。 |
| Open | 校验 IPv4→`EthernetOpenExt`（disconnect callback）→`GetVersion`、`GetModels`、`GetHeaderSerial(A/B)`、`GetOnlineCameraB`、`GetActivityProgramNo`、`GetCurrentFrequencyUpperLimit`、`Get16BitScale`、`ProfileData_XPitch` | Extended 是默认；`AsyncEthernetOpen` 仅在 Profile 明确支持异步连接时启用；Legacy `EthernetOpen` 只作兼容入口。打开后必须完成能力/关键参数读取，不能仅凭 socket Ready。 |
| Read/Apply setting | 每项 `GetSetting`→验证 bytes 1/2/4 和目标数组→`SetSetting(depth=1/2)`→同 key `GetSetting` | category/item/target/原生宽度来自目标设备 Profile；不能把参数 Id 猜成 category/item。Persistent 写入必须显式权限和审计。 |
| Recipe | Export=`ExportParameters`→复制 pointer/size；Import=`LoadParameters(bytes)`；Select=`SwitchProgram(0..63)`→`GetActivityProgramNo` | pointer 只在 adapter 内复制；size 超预算拒绝；成功仍须 Core 重读能力和全部关键参数。 |
| Single | `GetSingleProfile`；可选 `GetSingleProfile3DMode` 只在目标 Profile 明确允许时；按能力再取 encoder/intensity | 3D mode 没有当前 2.5D storage contract 时返回 `UnsupportedVersion`，不把它映射成通用 surface。 |
| Roll/Continuous | `RollDataCallbackInitialize`→`StartMeasure`（软件）或 `StartIOTriggerMeasure`（外部 I/O）→`Sr7RollDataCallback`；停止=`StopMeasure` | 一次 callback 行数 `1..MaxLinesPerCallback`，来源实现上限 15000 只作兼容上界，最终以 Profile 收窄；完整流使用 Wait 背压。 |
| OneTime | `SetBatchOneTimeDataHandler`→可选 `SetBatchOneTimeDataValidRange`→`StartMeasureWithCallback`→`Sr7BatchOneTimeCallback`；停止=`StopMeasure` | 每批必须保存 `Sr7BatchCallbackInfo` 的字段与布局证据；回调结束前完成复制。 |
| HighSpeed | ASCII 终止字符串→`HighSpeedDataCallbackInitialize`→`StartMeasureWithHighSpeedCallback`→`Sr7ProfileCallback`（getter 16/32 位、强度、编码器）→`StopMeasureWithHighSpeedCallback` | 仅在 Profile 给出网络端点、行数、带宽和 stop 证据时启用；兼容导出不能默认变成公共能力。 |
| Async | `AsyncCallbackInitialize(profileBits, maximumLines)`→软件触发 `AsyncSoftStartBatch` 或等待外部触发→`Sr7AsyncCallback`→`AsyncSoftStopBatch` | 16 位高度、64 位编码器和时间戳按实际 capability 分开声明；停止 ACK 不等于 NativeDrained。 |
| Blocking compatibility | `StartMeasure/StartIOTriggerMeasure`→`ReceiveData`→读取宽/行数、height、可选 intensity/encoder/width→finally `StopMeasure` | 只供 Replay/兼容诊断，禁止 UI 线程和生产默认；任何超时仍保原调用任务。 |
| Trigger | 异步模式=`AsyncSoftStartBatch`；其它已运行模式=`TriggerOneBatch` | 只确认设备 trigger 接纳；不把 frame 到达或位置观察写成 TriggerObserved。 |
| I/O/diagnostic | `SetOutputPortLevel`/`GetInputPortLevel`；`GetCurrentEncoder(32/64)`；`GetCameraTemperature`/`GetCameraBoardTemperature`；`GetBatchStatus`；`GetError`/`ClearError` | 端口、位宽、温度换算和错误码需 Profile 证据；未知不填零，不承担安全回路。 |
| Close | 匹配模式 Stop→等待 callback/原生缓冲退出→`CommClose`→保留 callback root 至 ConnectionReleased | 任何一步未知都保留句柄和 DeviceId 租约；不调用 `NativeLibrary.Free` 解决未排空。 |

回调边界固定如下：`Sr7RollDataCallback(int*,byte*,uint*,width,lineCount,result,deviceId)`、`Sr7ProfileCallback(data,compressType,xPoints,count,notify,deviceId)`、`Sr7AsyncCallback(data,userData,state,deviceId)`和一次回调 `Sr7BatchCallbackInfo` 均先校验 device/epoch、checked 维度、stride/offset，再复制到 RawSource；异常只进入 `CallbackFailed`，不得穿过 C ABI。一次回调结构在目标 x64 中按来源测试为 size 40，字段偏移 `0/4/8/16/24/28/32`；若目标头文件或型号证据不一致，禁用该 Profile，不按 C# 自动布局继续调用。`SR7IF_ReceiveData` 与旧高速初始化保持 CompatibilityEntryPoint；frame getter、encoder getter、callback initialize 等内部导出不能泄漏为 Core API。

### 9.5 断线、重连与数据缺失的固定策略

断线事件只封口当前 live epoch：保留已复制的历史帧/批次，当前 BatchSummary 标记 Incomplete 或 Unknown，迟到旧 epoch 回调只记录 Stale，不更新新状态。重连是新 `ConnectionEpoch`：原 Session 必须先 Close 或进入隔离 Owner；新 Session 重新 Probe/Open/ReadCapability/ReadParameters，比较 `(DeviceId, Model, Firmware, CapabilityRevision, ParameterRevision)`，任一差异使旧 RunPlan 失效。模块不自动恢复 Start、Trigger、输出或持久化参数；宿主必须显式重新 Apply/Arm/Start。

完整流缺少、重复、逆序、短 payload、非法 stride、头 A/B 不对齐、FrameLoss 非零或 callback result 失败时，按原序号和原字节保留 `MissingRange/InvalidSpan`，发送 PA `Rejected/Backpressure/Fault`，执行受控 Stop；不能补 0、插值、重排后返回 Complete。预览只允许 latest-wins，丢弃计入 PreviewDropped，不影响完整流的缺失计数。重连次数、退避和是否人工确认由宿主设备 Owner 的 Profile 冻结；本模块只提供一次受控新 epoch，不把网络超时当成可安全重试。

## 10. 线程、取消和有限收尾

每设备执行门至多一个SDK调用；不同设备并行受ManagerOptions.Limits.Sessions限制。队列操作不持SDK锁等待UI/磁盘。RAW callback只校验/保全/同步TryAccept，允许短锁但不宣称lock-free/常数时间实时。

调用Budget.Execution从接纳单调时间计；观察到期给不可变Unknown Receipt。原ValueTask只AsTask一次并在等待前存账本/Root，取消不丢它。Cleanup用ManagerOptions.Cleanup独立预算；到期仍保Root条目、原Task、epoch/request hash和borrow资源。查询旧操作只能观察原状态或有限一次SDK查询，不因反复Query积累任务。

Stop/Close有保底任务槽，不被业务占完；Close复用原Stop，失败仍继续可证明的安全释放步骤，不能skip全部cleanup，也不能释放正在执行的SDK对象。DisposeUnknown抛DS-011后Root留槽；只有Closed且Resources Known/Released/零、raw Binding及PAOwner也分别Released才退整套宿主槽。Host错误出口有限wall deadline，需交给进程Root待收责任，不能以method离栈清对象。

## 11. WPF/DevExpress PageContract 与模块控件 API

### 11.1 可构造的投影和宿主端口

Core目标`net10.0`；WPF目标`net10.0-windows/UseWPF=true`，直接引用本机DevExpress25.2.3。WPF只依Core及PA公开预览合同，Simulator/Interop/Replay由Host显式装配，控件不暗建Manager或设备。以下签名属于 `Asun.Modules.DeepSightControl.Wpf`，待实现，不是已编译API：

```csharp
using DS = Asun.Modules.DeepSightControl;
public enum UiIntent { ReadCapability, ReadParameters, Apply, SelectRecipe,
    Arm, Start, Trigger, Stop, Diagnose, Close, Query }
public sealed record UiBinding(Guid Id, DS.IDeepSightDeviceSession Session,
    DS.RunPlan Plan, DS.Budget Budget);
public sealed record UiOptions(int DeviceRows, int DiagnosticRows, int OriginalTasks,
    int MetadataBytes, double RefreshHz, DS.Budget Observation, DS.Budget Cleanup);
public sealed record UiAction(Guid RequestId, Guid BindingId, UiIntent Intent,
    DS.Command? Command, DS.OperationId? Original);
public sealed record UiReply(Guid RequestId, DS.Receipt? Receipt, DS.Error? Error);
public sealed record DeviceRow(Guid BindingId, DS.DeviceDescriptor Device,
    DS.Receipt? Last, string StatusKey);
public sealed record UiSnapshot(ulong Sequence, IReadOnlyList<DeviceRow> Devices,
    DS.ParameterSnapshot? Actual, IReadOnlyList<DS.Setting> Draft,
    IReadOnlyList<DS.DeviceEvent> Diagnostics, string Language, bool Truncated);
public interface IDeepSightUiAuthority
{
    bool Allows(UiBinding binding, UiIntent intent);
    ValueTask<DS.Receipt> ExecuteOwnedAsync(UiBinding binding, DS.Command command,
        CancellationToken cancel);
    ValueTask<DS.Receipt> QueryOwnedAsync(UiBinding binding, DS.OperationId original,
        DS.Budget budget, CancellationToken cancel);
    DS.Receipt? Last(Guid bindingId); // Root的深冻结本地快照，不IO
}
public interface IDeepSightText
{
    IReadOnlyList<string> Languages { get; }
    string Resolve(string language, string key); // 有界/无IO；覆盖所有模块UI键
}
public sealed record ProjectionResources(DS.DrainState Drain, int Subscriptions,
    int OriginalTasks, int PendingUpdates, long OwnedBytes);
public interface IDeepSightUiHost
{
    UiSnapshot Snapshot();
    void SetPlan(Guid bindingId, DS.RunPlan plan); // 纯冻结校验，当前无Run才能替换
    UiAction Prepare(Guid bindingId, UiIntent intent, IReadOnlyList<DS.Setting> draft,
        int? recipe, ulong? triggerIndex, DS.OperationId? original);
    ValueTask<UiReply> ExecuteAsync(UiAction action, CancellationToken cancel);
    ValueTask<ProjectionResources> CloseAsync(DS.Budget budget, CancellationToken cancel);
    ProjectionResources Resources();
}
public sealed class DeepSightDeviceControl : System.Windows.Controls.UserControl
{
    public ValueTask<UiSnapshot> BindAsync(IDeepSightUiHost host,
        DS.Budget budget, CancellationToken cancel);
    public ValueTask<UiSnapshot> SetLanguageAsync(string language,
        DS.Budget budget, CancellationToken cancel);
    public ValueTask<ProjectionResources> CloseProjectionAsync(DS.Budget budget,
        CancellationToken cancel);
    public ProjectionResources ProjectionResources();
}
public static class DeepSightViewFactory
{
    public static IDeepSightUiHost CreateHost(IReadOnlyList<UiBinding> bindings,
        IDeepSightUiAuthority authority, UiOptions options);
    public static IDeepSightText CreateDefaultText(); // 内嵌三语resx，无IO/全局语言
    public static DeepSightDeviceControl Create(IDeepSightText text,
        UiOptions options, string language);
}
```

SetPlan只在无未完Arm/Start且当前实际读回存在时深冻结/校验Plan.Parameters等实际Revision；不自动生成RunId/参数revision，不发设备IO。Apply改变实际参数后旧Plan失效，Host用新实际Revision和新RunId构造完整RunPlan再SetPlan，不能继续Start旧计划。

Create/CreateHost纯构造；Create在Host现有STA Dispatcher调用，不Open/订阅/创隐藏Window。Bind只建立有界事件订阅和首快照，不发设备命令。Bindings唯一、Session.Epoch非空且Plan参数与实际快照匹配（尚未读回时保计划候选但禁止Arm）且资源预算完整，所有options值正有限，RefreshHz不作现场吞吐保证；非法language/预算/绑定拒绝零设备动作。实际订阅Task由UIHost记录到Root；定时刷新至多一个待处理Dispatcher操作，不无限BeginInvoke。

Prepare由**模块Host实现**：深冻结draft/实际基线/Plan/预算、生成非空RequestId及DS Context(Id=RequestId,Epoch=session.Epoch,Budget=binding.Budget)，构造相应公开Command。Apply只用真实Actual.Revision/Volatile默认、SelectRecipe必须recipe、Trigger必须triggerIndex；Arm用binding.Plan，Start/Stop用其Run；Query只Original非空、Command=null；无实际参数不准备Apply/Arm。预期错误抛DeepSightException或UiReply.Error，无副作用。不能要求应用替模块补所有命令分派；Authority仅负责既有授权和Root登记/观察。

Execute按RequestId复用一次原任务；同ID异payload拒绝。发起前再次Allows，Authority.ExecuteOwned内部和Core IDeviceAuthority还要检查撤权；按钮Enabled不是权限。Root容量拒绝零调用。Module Host把该原Task/Command/Binding强持到真实结束，不靠View关闭丢命令；Last只投影原Receipt。UiHost禁止Prepare Open/网络/Reboot隐式命令，这些由Host显式维护入口及原Core合同执行。

UiSnapshot.Language由当前view的实例文案投影填写，UiHost快照Language空字符串表示尚未绑定语言，不是另一个全局语言Owner；Bind/SetLanguage返回的view快照必须是实际语言，Host不写语言。UiHost首Snapshot以Session.GetLatestReceipt/Resources深冻结，仅Latest包含的Actual不能假称完整参数，缺时显式未读取。UiHost的Draft来自Prepare收到的深冻结值，SetPlan不改Draft。

CloseProjection只取消本view订阅、释放自己的投影/未执行更新；已经发起命令归进程Root，不能把移交成功当设备完成。Authority.ExecuteOwned在调用前已由进程Root强持**原CoreTask**；UiHost另持有Authority返回的有限观察Task，后者返回Unknown Receipt即可真实结束，其结束不证明Root原CoreTask完成。UiHost.Close清本host订阅并等自己的有限观察Task真实退出；Root已接纳原Task无需关闭时再进行隐式移交。若Authority违反原Task登记/有限返回合同，UI保原AuthorityTask并报Unknown，不强收。ProjectionResources Released要Subscriptions/OriginalTasks/PendingUpdates/OwnedBytes=0。不Stop/Dispose外部Session，不关闭共享text/preview；Unknown保原对象。双控件共享Session但独立UiHost/Dispatcher操作/文案/Root槽，互不清除订阅或草稿。

预览工作区由宿主组合 [IM-040 §8.0](../profile-acquisition/DEVELOPMENT-GUIDE.md#80-module-wpf-api-contract-v02) 的ProfileAcquisitionView/IProfilePreviewStore/viewport端口；本控件不复制PA预览服务。设备选择与PA预览通过binding的epoch/head/batch/sequence明示关联，不将UI截图当Complete。未注入预览显示“无轮廓预览”，控制/诊断仍独立可用。

### 11.2 固定视口构图与联动

只在固定1920×1080验证视口，扣任务栏、边框、标题栏/状态栏后测实际客户区，不改用户显示设置、不扩分辨率矩阵。DIP=客户区pixels×96/实际DPI；初始100%DPI软件基线，现有DPI只按此视口核对，不安排其它分辨率。

- 命令带高48DIP、状态带28DIP；左设备Grid初始260DIP、右参数336DIP、底诊断180DIP，中央占剩余且初始至少客户区宽50%。高DPI在同一视口若不足，缩左至240并将非关键参数组渐进展开；关键状态/Stop/Query保持固定可见，不能用指定宽度造成横向溢出。编辑行32DIP、标题/间距遵循平台设计系统，长英文列名允许包行，关键ID可复制。
- `DockLayoutManager`负责布局与文档区域，状态条和Stop不允许被布局文件隐藏；非法/旧布局仅重置本控件布局不改设备配置。统一主题/对比度/图标，未知黄色+文字、错误红色+文字、Running状态有文字和计数；不靠颜色唯一表达。
- 左Grid固定DeviceId/model/epoch/状态，筛选排序/搜索虚拟化，不丢断线行；选择A/B/批次后右参数/诊断/中央曲线同步到同identity。悬停显示hash/版本/原码明细，主要错误仍在状态区可见。批量只按选中设备逐台Receipt，不吞部分失败。
- 右 `PropertyGridControl` 绑定草稿代理（实际快照+独立draft），`SpinEdit/ComboBoxEdit/ToggleSwitch`按definition选择，不绑定Session可写属性；单位/范围/actual-vs-draft/是否需排空可见。应用/撤销固定底部；只读/不支持给原因，未读回项不显示“已应用”。配方切换先处理未应用草稿，取消不发命令。
- 诊断Grid含原OperationId/Run/epoch/阶段/VendorCode/资源轴，选中记录定位相关曲线/数据；Curve `ChartControl+XYDiagram2D`仅诊断，不替3D视口；invalid点画空洞，不连线填0。预览latest-wins与完整received/delivered/missing分别标识。
- 次要布局/详细信息可用菜单/Flyout，Stop、取消观察、Query、错误与恢复保持可见。SuperTip提供作用/限制/shortcut/恢复，不能成为关键错误唯一出口；具体WPF类型以本机25.2.3公开API实现确认，当前未提供未核实的Flyout命名空间/XAML。

### 11.3 操作链、权限、键盘和三语

连续任务：选择设备→Host显式Open→读能力/参数→编辑Draft→Apply/逐项Readback→Arm→Start→观察Running与PA数据→Stop→查排空→交Host保存→关闭投影。Start在Ready未配置/Unknown/Disconnected/Quarantined禁用且Core复查；Stop/Query保留，状态区给“一次查询原操作”而非自动重连。维护人员可进入网络/I/O/清错/重启显式Host入口，生产操作者无该权限；设备控制不是质量放行。

Tab顺序设备Grid→命令→参数→应用/撤销→诊断；Ctrl+Enter仅有合法Draft时Apply，不启动采集；Esc关闭次要详情/撤销未发草稿，不暗Stop；Stop有可见按钮和独立可配置shortcut，绑定前显示SuperTip，不抢全局急停键。执行期间焦点不跳到异步弹窗，结果回到原命令/错误行；三种语言长文本同一视口检查截断、UIA.Name及禁用原因。

Host调用SetLanguageAsync动态切换zh-CN/zh-TW/en-US，扩展来自Text.Languages；先核对全部键再原子发布，未知/缺键保旧语言+明确错误；资源键包括标题/列/按钮/参数/状态/错误/恢复/SuperTip/UIA，值不来自SDK自由Message。仅切本实例，不改DevExpress全局Active、不丢Draft/Run/hash/单位；模块内不重复语言入口。三语状态例如“停止未确认 / 停止未確認 / Stop not confirmed”，恢复句“查询原操作 / 查詢原操作 / Query the original operation”；不出现“智能赋能/高效可靠”等无事实文案。

UI 资源表至少冻结以下键和值；同一键的三语文本在 `IDeepSightText` 中原子切换，错误正文保留可复制的 OperationId/RunId/epoch/VendorCode，恢复按钮只调用已允许的 Query/Stop/Close：

| Resource key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| `ds.status.ready` | 已就绪 | 已就緒 | Ready |
| `ds.status.running` | 采集中 | 採集中 | Acquiring |
| `ds.status.unknown` | 状态未知 | 狀態未知 | State unknown |
| `ds.error.configurationUnknown` | 配置未确认。查询原操作或读取实际参数。 | 設定未確認。查詢原操作或讀取實際參數。 | Configuration not confirmed. Query the original operation or read actual parameters. |
| `ds.error.backpressure` | 数据流已拒绝。已停止继续接收，请检查负载。 | 資料流已拒絕。已停止繼續接收，請檢查負載。 | Data was refused. Intake stopped; check the load. |
| `ds.error.deadline` | 操作未在期限内确认。请查询原操作。 | 操作未在期限內確認。請查詢原操作。 | The operation was not confirmed before the deadline. Query the original operation. |
| `ds.error.drainUnknown` | 资源未排空。保持设备占用并联系维护人员。 | 資源未排空。保持設備占用並聯絡維護人員。 | Resources are not drained. Keep the device reserved and contact maintenance. |
| `ds.error.permissionDenied` | 当前权限不允许此操作。 | 目前權限不允許此操作。 | Current permissions do not allow this operation. |

`DockLayoutManager` 使用已安装 25.2 公开成员 `SaveLayoutToStream/RestoreLayoutFromStream` 保存面板布局；状态栏、Stop、Query 的 `BaseLayoutItem.AllowHide/AllowClose/AllowFloat` 固定为 false，损坏或未知布局只恢复模块默认布局。左 `GridControl` 使用虚拟化只读行，右 `PropertyGridControl` 只绑定草稿代理，曲线使用 `ChartControl + XYDiagram2D`；这些控件和成员已在本机 25.2 XML 中定位，仍须在真实 WPF TestHost 编译/运行验证。布局保存不包含设备参数、权限、OperationId 或租约。

## 12. 两个无 UI 消费者、Simulator 和最小构造闭包

### 12.1 Simulator 公共入口及合成 Profile

纯托管 Simulator 首版同Core工程内实现，不单独分包；后续稳定消费者/发布需求再拆DLL。它实现同IDeviceTransport，完整数据模拟在ProfileBridge/PA fixture中独立组合，不给Core塞第二轮廓类。公开待实现签名：

```csharp
namespace Asun.Modules.DeepSightControl;
public enum SimFault { Hold, RejectBefore, FaultBefore, FaultAfter,
    ReadbackMismatch, RollbackUnknown, StopAckOnly }
public sealed record SimRule(DeviceId Device, string CommandKind, int Ordinal,
    SimFault Fault, string? Gate);
public sealed record SimulationPlan(IReadOnlyList<Capability> Capabilities,
    IReadOnlyList<ParameterSnapshot> InitialParameters, IReadOnlyList<SimRule> Rules);
public sealed record SimCall(DeviceId Device, string CommandKind, int Count);
public interface IControlledSimulator : IDeviceTransport
{
    void Release(string gate); // 只释放已登记闩锁；不制造停止证明
    IReadOnlyList<SimCall> Calls();
}
public static class DeepSightSimulationFactory
{
    public static SimulationPlan CreateFixture(int devices);
    public static IControlledSimulator Create(SimulationPlan plan, Limits limits);
}
```

CreateFixture只允许0/1/2，纯构造。设备`sim-01/sim-02`、地址`192.0.2.1/192.0.2.2`（测试地址，不发网络）、model=`sim-sr`、firmware=`sim-v1`、Source Simulation；Revision.Id `sim-cap-v1/sim-param-v1`，hash按DeepSightCodec完整重建。Heads A/B，Transfer全部五值、Trigger全部四值；Formats `sim-i16`高度16/有Intensity无Width与`sim-i32`高度32/无Intensity有Width，SettingKey=Common format、ProtocolCode=0/1，Evidence.Id=`sim-format-i16-v1/sim-format-i32-v1`、Sha256为严格UTF8 `ds-sim-format-v1:sim-i16` / `ds-sim-format-v1:sim-i32` 字节SHA256（非现场资料hash）。Inputs[0]、Outputs[0]，CanQuery/ClearError/Reboot/Stop/Readback=true、CanReadWhileRunning=false、MaxProfilesPerBatch=4。

Capability.HeadSettings为A/B各一条明确rate/exposure/trigger对应key、TriggerCodes FreeRun0/Software1/ExternalIo2/Encoder3；Parameters每头都有`rate`Real/Hz/min1/max1000/step1/tolerance0、`exposure`Real/us/min1/max1000/step1/tolerance0、`trigger`Enumeration/1/codes[0,1,2,3]，Common有`upper/lower`Integer/1/0..100/step1，lower.MustApplyBefore为空、upper也空；Capability.OrderConstraints明确(lower,upper)，合并baseline+patch后验证lower≤upper，不硬编码参数名称关系或引入DSL。Baseline每头rate100/exposure10/trigger0、lower20/upper80、activeRecipe0、ReadbackComplete true，Common还有format Enum/1/codes[0,1]、Baseline0（sim-i16）；format.ChangesLayout=true，其余false，空MaxTextBytes=0/非Real容差=0、无依赖；所有CanPersist=true、ReadOnly=false；最小/最大/step在Boolean/Text/Enumeration为空，EnumCodes只有枚举非空；所有MustApplyBefore为空，数字MaxTextBytes=0、ReadbackTolerance=0。其它数值/枚举范围不虚造为真机Profile。

SimRule.CommandKind只允许transport实际入口/步骤名（ReadSetting/WriteSetting/RestoreSetting/Open/ReadCapability/ReadParameters/SelectRecipe/ExportRecipe/ImportRecipe/Start/Trigger/Stop/ReadIo/WriteIo/Diagnose/Maintenance/Close/Discover），不允许只在Core执行的Apply/Arm，Ordinal从1，每(device,kind,ordinal)唯一；Rules≤Limits.Operations，Gate仅Hold非空、唯一且UTF8有界。Simulator不发真实IO、不创隐藏线程；Hold原任务等待闩锁，未Release前不产生确认。StopAckOnly返回Knowledge Unknown/Activity Unknown/InputEnded=false/NativeDrained=false；FaultAfter先标动作可能发生再fault，不恢复Created。ReadbackMismatch作用ReadSetting，Real实际值加1/Int checked加1，针对其它kind返回DS-006而不猜变体；Baseline仍保留；RollbackUnknown针对已写项恢复失败，必须逐项Unknown。RejectBefore零动作；FaultBefore不虚造设备实际成功。正常SelectRecipe/Import重新返回全部参数，Reboot返回Disconnected知识/连接未释放，Close完整证据才Closed。

Simulator必须验证初始Actual与Capability/hash/单位/配方全部一致，未知值变体拒绝。正常IO输入false/输出false；WriteIo后ReadIo返回该端口新actual。Diagnose DeviceCode=sim-ok、TemperatureC=25、Encoder=null/EncoderBits=null、Errors空。ExportRecipe Bytes为当前DeepSightCodec.EncodeParameters原字节，Format=ds-sim-recipe-v1、DeviceProfile=Capability.Revision、Hash实bytes；Import只接受本版本且等已存同设备历史快照字节（Create深冻结初始、Export登记当前，记录条数≤Operations，累计Blob/metadata计费），不需要猜native格式解码；未知附件DS-015。ParameterSnapshot更新Revision.Id固定sim-param-v1，hash取完整Actual，SelectRecipe新号反映到hash。

参数比较/Revision身份来自完整Profile；fixture数值为确定合成断言，不是频率、容差、吞吐或现场指标。数据Bridge合成样例用A/B各4profiles、每行4个I16高度原code[0,10,-32768,30] LE、物理证据候选Scale0.001/Offset0/mm（本RawCode合成输出主plane仍Scale1/Unitcode）、sentinel -32768；强度U16[0,65535,16,32]、Scale1/Unit1，位置Unknown、无编码器/时钟证据。Bridge只保全结构/无效域，不生成规则表面。真实设备的Scale/invalid仍来自设备证据。

### 12.2 Factory 前的 Host Root 和原 Task 记录

ArchiveHost和InspectorHost都由同一外层进程Root接纳，不能各自产生无人拥有的后台Task。Root必须在Factory/Simulator/Manager/Session/UI构造**之前**原子预留manager/session/元数据/Blob副本/原Task/cleanup槽：合成例每Host一个manager/一个session、MetadataBytes=1MiB、BlobBytes=4096、Commands=4、Operations=16、Events=32、EventReaders=2、Parameters=32；Root最大2Host、每Host32个原Task records，其中5个保底（Stop/Close/Query/Session.Dispose/Manager.Dispose），字节reservation每Host=1MiB Core metadata+16×4096 blob上限+1MiB Host副本+1MiB Root辅助=3,211,264 bytes，两Host=6,422,528 bytes，Root硬上限8,388,608 bytes。Root拒绝时0Factory/IO。设备多会话容量测试另用Sessions=2，不套此单session例。

每Root条目存Manager/Session/Transport/Authority/options、epoch/device/run、冻结命令/hash、原Task和所有借用资源、最近Receipt/Resources、业务错误列表、cleanup错误列表和当前Owner。账本有限；不能为创建新任务删除未完或FaultAfter记录。登记先于发调用，原ValueTask.AsTask只一次；任务fault也消费Exception并保存，fault不证明资源释放。`await using`在finally丢资源并抛覆盖原异常不满足本Host。

以下为**语义C#示例**，不是已构建的产品源码。HostRoot/HostSlot/HostRecord为对应TestHost工程内BCL助手：Core.Tests、ProfileBridge.Tests和Wpf.Tests各自在本工程实现下列签名与算法，不引用其它测试Exe，不新增公共产品包；不由产品实施者再设计恢复服务：

```csharp
// tests命名空间 Asun.Modules.DeepSightControl.Core.Tests；引用Core和BCL。
public enum HostKind { Archive, Inspector }
public enum Stage { Business, Cleanup, Recovery }
public sealed record RootBudget(int Slots, int RecordsPerSlot, int CleanupRecords,
    long Bytes, int ErrorRecords);
public sealed class HostRecord<T>
{
    public Task<T>? Original { get; } // 同步抛出可null且已有明确错误记录
    public OperationId? Operation { get; }
}
public sealed class HostSlot
{
    public void Own(object value);
    public Context NextContext(ConnectionEpoch epoch, Budget budget);
    public HostRecord<T> Start<T>(string role, Command? command, OperationId? original,
        Func<ValueTask<T>> invoke, bool cleanup);
    public HostRecord<bool> StartVoid(string role, Func<ValueTask> invoke, bool cleanup);
    public ValueTask<T> Observe<T>(HostRecord<T> record, TimeSpan remaining);
    public void RecordError(Exception error, Stage stage);
    public void RecordReceipt(Receipt receipt, Stage stage);
    public Receipt? Latest(Guid bindingId); // UI关联键，只有该binding原任务已知值
    public OperationId? LastUnconfirmedOrClose();
    public void SaveArchive(Receipt receipt); // 有界深复制值；不复用native引用
    public void AssertProjection(Receipt receipt); // Inspector身份/hash/类型/资源不变量
    public int ExitCode(); // 0只在必需项全执行/全确认/释放/无错误
}
public sealed class HostRoot
{
    public HostRoot(RootBudget budget);
    public HostSlot? TryReserve(Limits limits, long hostCopyBytes);
    public bool TryRetire(HostSlot slot);
    public void KeepPending(HostSlot slot);
    public ValueTask RecoverPendingAsync(Budget budget, CancellationToken cancel);
    public bool TryHandoff(HostSlot slot, HostRoot receiver, Guid token);
}
public sealed class TestAuthority : IDeviceAuthority
{
    public bool Allows(DeviceId device, ActionKind action); // 合成案例明示允许；撤权case由闩锁策略拒绝
}
```

TestAuthority构造纯托管，默认允许枚举内全部动作，非法action拒绝；不能作为现场权限。Start在短锁内先预留角色/Operation/hash/原Command/borrow记录，再invoke一次/AsTask一次存Original，然后才await；同步抛出登记错误，返record但Observe重新抛已记录的原异常。StartVoid把同一个原ValueTask.AsTask保存，再用一次原Task完成映射bool，不把wrapper完成当设备资源证明。Root将每条原Task指向slot和最近资源关联，Own强持所有对象，不用静态全局字典。RootBudget.ErrorRecords/Metadata限额包括原异常有界摘要，但OriginalTask本身持有异常由Root强持至消耗。Observe的finite remaining≤0仅抛TimeoutException且不丢record；执行中取消只结束观察。NextContext使用slot的有界checked操作计数构造新Guid（RFC网络前8bytes固定Host槽/类型，后8bytes递增），slot启动前预留原stop/close身份，发生冲突DS-012而非换随机GUID；业务counter到期拒容量，cleanup保底不占业务counter。示例的Guid仅合成，真实Host默认Guid.NewGuid仍发前登记检测冲突。Start role="business"时由slot递增business-N，cleanup同role只复用原record，不能覆未完记录。

错误记录只保异常类型名/有界消息各≤512 UTF8 bytes、Stage/原Id，Original.Exception由Root消费不将无限StackTrace复制入新集合；超ErrorRecords保总错误数与Truncated标志，仍非0，不无限保存StackTrace。

Start角色固定business-N/stop/close/query/dispose-session/dispose-manager；CleanupRecords=5明确独立叶记录，无业务使用该5条。session Dispose未完也不覆盖其record，manager Dispose另记录；Core内部Operations保底与Host Root独立。Root.TryReserve事前为Limits.MetadataBytes+BlobBytes×Operations+Host副本+1MiB额外固定Root元数据额度checked预留，该1MiB涵盖32条task/32条错误及签名/deep冻结辅助；实际变量字符串累计超额拒绝，不以估算无限分配，Error与原Task对象引用受条数/metadata上限；Raw/PA/UI模式另增实预算，不借此无限自涨。

HostRunner只在finally之后返回；Stop/Close/Query/Dispose所有步骤共享一次新Cleanup wall deadline 6秒，步骤观察min(1秒,remaining)，不能每个finally重置6秒。模块Budget用于自身单调时钟；Host watchdog另用System Stopwatch。达到总wall期限仍先登记允许的原cleanup任务/身份，再立即结束观察，把已启动原Task/资源留Root，不使用同步等待卡死线程。Root容量足够且Start invoke必须有限返回ValueTask（不可在同步调用内长期阻塞，native调用由adapter受控执行门执行）。

```csharp
async Task<int> RunHost(HostRoot root, HostKind kind)
{
    var limits = new Limits(1, 4, 16, 32, 2, 32, 4096, 1_048_576);
    var budget = new Budget(TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1));
    var slot = root.TryReserve(limits, 1_048_576); // 所有Factory之前
    if (slot is null) return 2;
    IDeepSightDeviceManager? manager = null;
    IDeepSightDeviceSession? session = null;
    try
    {
        var fixture = DeepSightSimulationFactory.CreateFixture(1); slot.Own(fixture);
        var transport = DeepSightSimulationFactory.Create(fixture, limits); slot.Own(transport);
        var authority = new TestAuthority(); slot.Own(authority);
        manager = DeepSightFactory.Create(transport, authority,
            new ManagerOptions(limits, budget), TimeProvider.System); slot.Own(manager);
        session = manager.CreateSession(fixture.Capabilities[0].Device,
            new ConnectionEpoch(Guid.Parse("00000000-0000-0000-0000-000000000002")));
        slot.Own(session);
        async Task<Receipt> Execute(Command c)
        {
            var record = slot.Start("business", c, c.Context.Id,
                () => session.ExecuteAsync(c, CancellationToken.None), false);
            var r = await slot.Observe(record, TimeSpan.FromSeconds(1));
            slot.RecordReceipt(r, Stage.Business);
            if (r.Phase != Phase.Confirmed || r.Error is not null)
                throw new InvalidOperationException("Required command not confirmed");
            if (kind == HostKind.Archive) slot.SaveArchive(r);
            else slot.AssertProjection(r);
            return r;
        }
        await Execute(new OpenCommand(slot.NextContext(session.Epoch, budget)));
        var capability = await Execute(new ReadCapabilityCommand(slot.NextContext(session.Epoch, budget)));
        var actual = await Execute(new ReadParametersCommand(slot.NextContext(session.Epoch, budget)));
        if (capability.Capability is null || actual.Parameters is null)
            throw new InvalidOperationException("Required snapshot missing");
        var applied = await Execute(new ApplyCommand(slot.NextContext(session.Epoch, budget),
            actual.Parameters.Revision, WriteDepth.Volatile,
            new[] { new Setting(new ParameterKey("rate", Head.A), new RealValue(120), "Hz") }));
        if (applied.Parameters is null) throw new InvalidOperationException("Actual missing");
        var plan = new RunPlan(Guid.Parse("00000000-0000-0000-0000-000000000003"),
            TransferMode.Single, TriggerMode.FreeRun, new[] { Head.A }, "sim-i16",
            applied.Parameters.Revision, 4, 1, TimeSpan.FromSeconds(4)); slot.Own(plan);
        await Execute(new ArmCommand(slot.NextContext(session.Epoch, budget), plan));
        await Execute(new StartCommand(slot.NextContext(session.Epoch, budget), plan.Run));
    }
    catch (Exception e) { slot.RecordError(e, Stage.Business); }
    finally
    {
        var started = System.Diagnostics.Stopwatch.StartNew();
        TimeSpan Remaining() => TimeSpan.FromSeconds(6) - started.Elapsed;
        async Task ReceiptCleanup(string role, Command c)
        {
            try
            {
                var record = slot.Start(role, c, c.Context.Id,
                    () => session!.ExecuteAsync(c, CancellationToken.None), true);
                var r = await slot.Observe(record, TimeSpan.FromSeconds(1) < Remaining()
                    ? TimeSpan.FromSeconds(1) : Remaining());
                slot.RecordReceipt(r, Stage.Cleanup);
            }
            catch (Exception e) { slot.RecordError(e, Stage.Cleanup); }
        }
        if (session is not null)
        {
            try
            {
                var run = session.GetRunSnapshot();
                if (run is not null)
                    await ReceiptCleanup("stop", new StopCommand(slot.NextContext(session.Epoch, budget), run.Run, StopReason.User));
            }
            catch (Exception e) { slot.RecordError(e, Stage.Cleanup); }
            finally
            {
                try { await ReceiptCleanup("close", new CloseCommand(slot.NextContext(session.Epoch, budget))); }
                finally
                {
                    try
                    {
                        var original = slot.LastUnconfirmedOrClose();
                        if (original is not null)
                        {
                            var q = slot.Start("query", null, original,
                                () => session.QueryOperationAsync(original.Value, budget, CancellationToken.None), true);
                            slot.RecordReceipt(await slot.Observe(q, Remaining()), Stage.Cleanup);
                        }
                    }
                    catch (Exception e) { slot.RecordError(e, Stage.Cleanup); }
                    finally
                    {
                        try { await slot.Observe(slot.StartVoid("dispose-session", () => session.DisposeAsync(), true), Remaining()); }
                        catch (Exception e) { slot.RecordError(e, Stage.Cleanup); }
                    }
                }
            }
        }
        // 包括Session Create未返回但Manager已创建的路径，Manager仍收尾。
        if (manager is not null)
        {
            try { await slot.Observe(slot.StartVoid("dispose-manager", () => manager.DisposeAsync(), true), Remaining()); }
            catch (Exception e) { slot.RecordError(e, Stage.Cleanup); }
        }
        if (!root.TryRetire(slot)) root.KeepPending(slot);
    }
    return slot.ExitCode(); // finally之后，不提前把成功返回值冻结
}
```

Launcher在方法外持有 `new HostRoot(new RootBudget(2,32,5,8_388_608,32))`，先await RunHost(root,Archive)，再await RunHost(root,Inspector)，每个RunHost在Root预留自己的隔离Simulator域；可并发测试两Host，用相同Root原子槽。两个退出码和Root是否为空共同决定测试结果；业务异常/观察超时即使后来资源收完也非0（保错误）。Archive实际调用SaveArchive深复制完整Receipt/Capability/Parameters/Blob与scheme/hash；Inspector调用AssertProjection检验§5结果不变量、DS-T18字段编码和资源，绝不是只换HostKind而不消费结果。

TryRetire检查session.GetResources和manager.GetResources全部Counters Confirmed/Drain Released、Session已Closed（LatestReceipt.State或原Close）、原Task全部真实退出、异常均被消费、Host副本用途完成已归还、PA/raw/UI各自屏障通过。session构造无返回而工厂纯构造已证明无资源时仅释放空session reservation；若违反纯构造承诺保Root不能猜0。TryRetire成功后ExitCode仍从有限错误/验收摘要取，不再访问已退引用。

RecordReceipt的非Confirmed/Error均记当前Stage错误，业务命令必需项确认计数不被cleanup结果覆盖；Closed/Released也不清先前deadline错误。

KeepPending将同slot转为Root Recovery所有者，Owner仍是Launcher长期持有的Root。RecoverPendingAsync使用独立finite budget，按slot保存的原ID调用Query（配置步骤由Core查询），真实原Task结束/异常消费后再观察原Stop/Close/Dispose；不会发新Start/Apply/Trigger，不重新Factory、不覆盖旧identity。每轮每slot至多一个原Query在途，Unknown保持Root；迟到值只增加知识并在完整屏障后退槽。Root.TryHandoff先在receiver保留完整相同对象/Task/借用及容量、确认token，原Root才停止承担；拒绝/接收者异常原Root保留。测试watchdog前执行一次RecoverPending，未退槽非0并输出原ID/资源，不把结束进程当安全归还。

### 12.3 两消费者的数据模式与双 STA 控件 Host

Archive保存完整DS快照/Receipt与PA借用期复制的全Payload/metadata；Inspector核对identity/hash/invalid/序号/错误，并从自己的副本读取，不写质量或依赖页面初始化。Core例已给两类实际消费调用。数据模式复用 [IM-040 §7.1～7.3](../profile-acquisition/DEVELOPMENT-GUIDE.md#7-两个无ui消费者最小闭包) 的Root、ManagedBuffers、sink复制、PAFactory和原Task/有限cleanup，不复制第二Replay类型。只替换adapter且在Root中新增DS/raw/Bridge资源屏障；以下为本模块确定模拟装配签名：

```csharp
namespace Asun.Modules.DeepSightControl.ProfileBridge;
public sealed record SimulatedProfileFixture(ProfileBinding Binding,
    PA.ParameterSet Parameters, PA.RunPlan Plan);
public interface IControlledRawSource : IDeepSightRawSource
{
    ValueTask<InputResources> DriveAsync(CancellationToken cancel);
}
public static class DeepSightProfileSimulationFactory
{
    public static SimulatedProfileFixture CreateFixture(DS.ConnectionEpoch deviceEpoch,
        DS.Capability actualCapability, DS.ParameterSnapshot actualParameters);
    public static IControlledRawSource Create(DS.IDeepSightDeviceSession session,
        SimulatedProfileFixture fixture, BridgeLimits limits);
}
```

CreateFixture仅接受§12.1完整Simulation能力/初始参数或已读回参数（仅模拟域允许从SimulationPlan输入，不当作设备读取证据），纯构造不改变设备。PA Epoch空占位等待Attach；HeadMapping A→HeadId("A")/B→"B"，每头rate/exposure/trigger分别参数key；TriggerCodes FreeRun0/Software1/External2/Encoder3；FormatCodes sim-i16→Common format0/Calibration null，sim-i32→format1/null。EncoderCodes空，PA.EncoderId/Calibration=null。Transfer=Single；PA Capability DeviceId取实际设备、AdapterId="ds-sim-raw"/AdapterVersion="sim-raw-v1"，CanPauseInput=false/CanStop=true/CanReadback=true/CanQueryOperation=true；每头频率[1,1000]Hz/曝光[1,1000]us、Triggers四值、Encoders空。

PA FormatSpec.Id=sim-i16/Domain RawCode/PrimaryRole="height"/Unit="code"/MinSamples=MaxSamples=4/MaxPayloadBytes=16。height PlaneFormat I16/LittleEndian/Line/MaxRows1/Unitcode/Scale1/Offset0；intensity U16/LE/Line/MaxRows1/Unit1/Scale1/Offset0；InvalidEncoding(height,0x8000,Sentinel)。Format.Revision.Id="sim-pa-format-v1"/hash按PA source scheme完整重建。sim-i32另格式仅height I32 code/Scale1与width U16 1，maxbytes24/invalid0x80000000，其同名sim-i32只在Capability可选，本最小Drive固定sim-i16。Capability.Revision.Id="sim-pa-cap-v1"/hash按PA source scheme，ParameterSet.Id="ds-pa-actual-v1"，选A/B、sim-i16、FreeRun、实际Rate/Exposure（A/B必须相同）和空Encoder/Calibration/hash按PA scheme。Binding.Revision.Id="sim-pa-binding-v1"，hash用下列完整Binding规则，不拿DS参数hash冒充PA参数hash。

Binding编码 `ds-pa-binding-bin-v1` + `ds-api-v0.2`，采用§5 primitives；完整字段顺序，省自己的Revision、ProfileEpoch（Factory前未定）、保DeviceEpoch/Heads/Transfer/完整PA Capability/TriggerCodes/FormatCodes/EncoderCodes；PA嵌套record用PA §3.4 primitives/字段序，无额外PA scheme前缀，其nested Revision保留。Heads按DeviceHead，TriggerCodes按PA.Mode，FormatCodes按FormatId UTF8，EncoderCodes按EncoderId排序；拒重复后排序。Attach只确定实例epoch，不改变静态设备映射revision；Host Root另把(ProfileEpoch,DeviceEpoch,BindingRevision)固定为实例身份。实际Binding改变不能原地替换活动桥。

PA Plan.Run=00000000-0000-0000-0000-000000000003/Single/Parameters=上述实际PARevision，A/B两HeadPlan各FirstSequence=0/ProfilesPerBatch=4，MaxBatchesPerHead=1、BatchDeadline=2s、MaxRunDuration=4s。BridgeLimits(16,32,1MiB,128,2)，DS/Bridge cleanup1s，PA ResourceLimits沿PA §7.3有界128bytes/2队列配置；Root在Factory前预留三Owner/128raw+128PA+Host两个完整副本，各实际payload16bytes/行，且metadata槽/Task记录预留足够。

模拟装配顺序（Factory前Root reservation）：由纯SimulationPlan取得Capability/InitialParameters构造fixture，DS Session保持Created→rawFactory→BridgeFactory→PAFactory.Create→adapter.AttachEpoch(paSession.Epoch)→PA Open/Discover/Apply/Arm/Start→raw.Drive→PA Stop/Close/Dispose→DS Manager.Dispose。控制Host与数据Host采用不同装配模式：数据Host设备IO全部由Bridge执行，实际Discover/Apply核对fixture输入，不能把预构造模拟值冒充设备读回。真机Profile输入来自批准资料和设备Owner，PA阶段仍实际核对，不暗自Open第二会话。

对应可调用装配片段（语义签名示例，Root.Start/Observe沿§12.2及PA Root助手，所有Task调用前登记）：

```csharp
// ProfileBridge.Tests Host内，slot已按本节Root预算预留，尚无Factory对象。
var dsLimits = new DS.Limits(1, 4, 16, 32, 2, 32, 4096, 1_048_576);
var dsBudget = new DS.Budget(TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1));
var paBudget = new PA.Budget(TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1));
var bridgeLimits = new BridgeLimits(16, 32, 1_048_576, 128, 2);
var paLimits = new PA.ResourceLimits(2, 128, 1_048_576, 8, 16, 64, 64, 8);
var deviceEpoch = new DS.ConnectionEpoch(Guid.Parse("00000000-0000-0000-0000-000000000002"));
var clock = TimeProvider.System;
var authority = new TestAuthority(); slot.Own(authority);
var completeSink = new ProfileCopySink(slot, kind, 1_048_576, 8); slot.Own(completeSink);
var dsPlan = DS.DeepSightSimulationFactory.CreateFixture(1); slot.Own(dsPlan);
var dsTransport = DS.DeepSightSimulationFactory.Create(dsPlan, dsLimits); slot.Own(dsTransport);
var dsManager = DS.DeepSightFactory.Create(dsTransport, authority,
    new DS.ManagerOptions(dsLimits, dsBudget), clock); slot.Own(dsManager);
var dsSession = dsManager.CreateSession(dsPlan.Capabilities[0].Device, deviceEpoch); slot.Own(dsSession);
var fixture = DeepSightProfileSimulationFactory.CreateFixture(deviceEpoch,
    dsPlan.Capabilities[0], dsPlan.InitialParameters[0]); slot.Own(fixture);
var raw = DeepSightProfileSimulationFactory.Create(dsSession, fixture, bridgeLimits); slot.Own(raw);
var adapter = DeepSightProfileBridgeFactory.Create(dsSession, raw, fixture.Binding,
    bridgeLimits, dsBudget, clock); slot.Own(adapter);
var buffers = PA.ProfileAcquisitionFactory.CreateManagedBuffers(paLimits.OwnedBytes); slot.Own(buffers);
var paSession = PA.ProfileAcquisitionFactory.Create(adapter, buffers, completeSink,
    new PA.SessionOptions(paLimits, paBudget), clock); slot.Own(paSession);
adapter.AttachEpoch(paSession.Epoch); // 实际PA factory epoch，不能外部猜GUID
// 此后PA公开CommandContext均用paSession.Epoch；设备只由该桥写，ControlHost不并发Arm。
```

ProfileCopySink是ProfileBridge.Tests内明确`sealed class ProfileCopySink : PA.ICompleteProfileSink`，构造`(HostSlot owner, HostKind kind, long maxBytes, int maxProfiles)`纯托管；实现OnProfileAsync/ProfileRejected/OnBatchAsync原签名。Archive和Inspector分别创建自己的sink，每条先slot预留实际payload bytes+完整metadata、count≤maxProfiles，再复制全Payload/metadata/hash/Invalid/Position，函数返回后绝不保borrow；额度满抛ProfileAcquisitionException(PA-010)，不省点成功。OnRejected深冻Error与Preserved（有时null），不能将Rejected视Complete；OnBatch记录完整BatchSummary/hash并核对received/delivered/missing，Inspector复算PA contentHash/invalid并比较Archive副本（由Root explicit copy借入），无质量判断。关闭用途完成后slot归还自己副本，已借给Inspector的独立复制不受影响。所有sink原Task由PA Owner强持，本次方法返回Fault也不造buffer释放。Drive是显式有界模拟驱动任务，仅在同session.GetRunSnapshot存在且Running、epoch/Run/format参数匹配、Bind已建立时发送8条frame；每Head 4条sequence0..3/RawSequenceBits64、Head批次Index0，PlaneLayout height offset0/rows1/columns4/rowStride8/pixelStride2/I16/LE、intensity offset8/.../U16，Payload全16bytes。height原[0,10,-32768,30]，强度[0,65535,16,32]、InvalidSpan(height,row0,start2,count1,Sentinel)，Position.Unknown/frame="sim-frame"/Calibration null/segment0/实际与命令坐标null、SampleTime=null/SourceSimulation；TriggerIndex=null。每头BatchEnd(lastSequence3)、然后InputEnded，真实模拟驱动退出后InputResources.InputEnded/NativeDrained=true；设备活动由Stop证明，不能InputEnded自动伪装DS Stopped。Refused立即发PA Fault(Backpressure)、保不完整并结束驱动；Drive原Task未结束时Close不能回收其ingress引用。

Bridge Stop/Cleanup在normal Drive完毕后才DSStop；异常case源Task/PA sinkTask按各Owner强持。raw GetResources计回调/原DriveTask/实际bytes，fixture托管静态字节由Root reservation计，不声称CPU复制或GC已释放OS。PA/DS/raw/Bridge四资源轴分别Query，任一UnknownRoot留槽；两个消费者在PA sink借用期间各预留/复制，借用内超过副本额度拒绝而不是丢点后成功。

两个STA Host沿§12.2Root先预留UIOptions(2,32,32,1MiB,10Hz,1sObservation,1sCleanup)、文本/Dispatcher/viewHost两独立槽。根保留UI原Task/资源，**两Host均给完整构造**（Wpf.Tests语义例）：

```csharp
// 使用已由控制Host显式Open/Read完成的shared DS Session，同一Manager/写门；
// actual来自其真实ReadParameters Receipt，Root强持，不从Session私有字段获取。
var uiOptions = new UiOptions(2, 32, 32, 1_048_576, 10, budget, budget);
var text = DeepSightViewFactory.CreateDefaultText(); slot.Own(text);
var authority = new RootUiAuthority(root, slot); slot.Own(authority);
var runPlan = new DS.RunPlan(Guid.Parse("00000000-0000-0000-0000-000000000004"),
    DS.TransferMode.Single, DS.TriggerMode.FreeRun, new[] { DS.Head.A }, "sim-i16",
    actual.Revision, 4, 1, TimeSpan.FromSeconds(4));
var binding = new UiBinding(Guid.Parse("00000000-0000-0000-0000-000000000005"),
    sharedSession, runPlan, budget);
var host = DeepSightViewFactory.CreateHost(new[] { binding }, authority, uiOptions); slot.Own(host);
// 在本Host已建立STA Dispatcher执行，全部ValueTask先通过Root.Start再观察；
// Host A语言zh-CN，Host B en-US，自己的bindingId及新RunId（避免错误共享计划）。
var view = DeepSightViewFactory.Create(text, uiOptions, initialLanguage); slot.Own(view);
var boundTask = slot.Start("ui-bind", null, null, () => view.BindAsync(host, budget, cancel), false);
var bound = await slot.Observe(boundTask, TimeSpan.FromSeconds(1));
var action = host.Prepare(binding.Id, UiIntent.Diagnose, Array.Empty<DS.Setting>(), null, null, null);
var actionTask = slot.Start("ui-action", action.Command, action.Command?.Context.Id,
    () => host.ExecuteAsync(action, cancel), false);
var reply = await slot.Observe(actionTask, TimeSpan.FromSeconds(1));
// Unknown只通过host.Prepare(Query, original=reply.Receipt.Id)追原身份，不再次Prepare同写动作。
```

RootUiAuthority为Wpf.Tests内 `public sealed class RootUiAuthority : IDeepSightUiAuthority`，构造(HostRoot root,HostSlot slot)纯存依赖，Last从slot已保存Receipt按BindingId取；Allows映射UiIntent到§3.1.1 ActionKind并委托Host真实策略（合成TestAuthority显式允许，撤权case拒绝）。ExecuteOwned入口用单调Stopwatch固定一次总观察deadline（本例1秒），调用前slot.Start记录原DS Command/Task；所有Observe只用该deadline的剩余时间，不为后续Query重新给1秒。原命令尚未确认时，最多一次先保底登记session.QueryOperationAsync原QueryTask；它仅查原身份，按§3不为未完写增加SDK query。Query若已完成立即取其原ID/hash回执；否则只观察剩余时间，时间耗尽不再等待，原QueryTask仍留Root。没有可用Query回执时，用session.GetLatestReceipt中原ID/hash均匹配的已有值；无匹配值则构造DeviceKnowledge=Unknown、Resources.Counters=Unknown/Drain=Unknown、DS-010、保原ID/hash、StateQuarantined，不抛掉原动作知识。未得到Receipt时UI仍保Prepared.action.Context.Id为Original，Query UI不依赖首次有回执。QueryOwned每次入口同样只固定一个总观察deadline，先记录原QueryTask后按剩余时间观察；不能由UiHost自己绕Root调用Session。两个view的RootAuthority共享Root但各自slot/BindingId，Owner有唯一原DS任务记录，不重复调用。

每Host try内构造/Bind/语言/Prepare/Execute，catch保存业务或UI错误；finally嵌套：CloseProjectionAsync→host.CloseAsync→查询两者ProjectionResources→原任务观察；每项同步/异步异常分别RecordError，下一项仍执行，统一独立Cleanup wall deadline6s/单步1s，finally之后才ExitCode。Projection Unknown强持view/host/原Task、两槽不能退；原设备动作在进程Root中不受投影关闭影响。Host A关闭不Stop/sharedDispose、不改Host B Draft/语言；Host B仍收到事件/可Query。两view关闭且投影屏障通过后Root才能显式Stop/Close设备，设备Unknown仍保其独立Owner。

两个STA用各自正常可见测试Window/Dispatcher，Window构造也须先Root reservation，不是模块隐藏依赖；viewport若组合PA UI每Host各自FrameworkElement，不跨Dispatcher共父。只同1920×1080基线先后验证两窗口，不改变用户显示设置。此轮未运行真实控件/DevExpress/三语，不用伪代码或截图宣称UI完成。

### 12.4 Replay 与自动参数能力边界

```csharp
public sealed record ReplayPlan(
    string SourceId, string SourceRevision, string RecordSetSha256,
    TimeSpan InterRecordDelay, IReadOnlyList<SimRule> Faults,
    bool PreserveRecordedTimestamps);
public static class DeepSightReplayFactory
{
    public static IDeviceTransport Create(
        IReadOnlyList<Receipt> receipts,
        ReplayPlan plan, Limits limits, TimeProvider clock);
}
```

`receipts` 必须已经由 Host 按当前 codec 解码并深冻结；Factory 不打开文件、不读取网络、不接受路径。`Faults` 只能引用已存在的原 Operation/Run/sequence，新增或改写身份返回 DS-015；`InterRecordDelay` 只改变模拟时钟等待，不改变 Receipt 的原始时间戳或 hash。Replay 的资源计数、取消、迟到归还和 Close 仍遵守 Core 同一 Owner 规则。

Replay 不另造一套设备 API：Host 读取已批准的 `DeepSightCodec` Receipt/Capability/Parameter/Step 字节，并按PA当前 `ProfileInputCodec` 解码 `pa-source-record-v1`（旧的Batch/Event合同仅在其版本仍被当前PA codec接受时可读），先校验 scheme、版本、hash、epoch、Run、序号和完整 payload，再通过 `PA.ProfileSourceFactory` 与 ProfileBridge 的受控 RawSource 接入。Core 不读文件、不解析任意路径；文件/对象存储、索引、版本迁移和只读权限由 Host/Store Owner 负责。Replay 的每个原操作沿原 `OperationId + RequestSha256` 回放，禁止把成功回放成现场确认；输出 `Source=Replay`，延迟、错误、缺失和回调顺序由 `ReplayPlan` 明确脚本化，脚本不改变原字节。Replay 至少覆盖正常闭环、重复 Operation、断线重连、短 payload、逆序/缺失、StopAckOnly、迟到 Query 和旧 schema 拒绝。

PA 的 `ProfileSourceFactory`/`ProfileParameterAdvisor` 是桥接输入能力，不由 DeepSight 重实现。Host若使用PA `ParameterAdvice`，必须保留其 `Scheme=pa-advice-v1`、`InputSha256`、Capability/Parameters/Benchmark 三个Revision、`Source` 和 `AdviceEvidence`，并在提交前用当前完整Capability/Parameters/Benchmark调用 `CheckCurrent`；过期、来源不一致、`AllSamplesReleased=false`、`SourceDrain` 未 Released、模拟来源或证据负载变化均不得转为设备事实。`Suggested` 只可映射为新的有限参数草稿，不能直接改 DS `RunPlan`、`ResourceLimits`、频率/曝光或触发配置；Host经权限校验、显式 Apply、完整读回并生成新Revision后才可写设备。`RequiredProfiles/OwnedBytes/MetadataBytes` 只是PA有界容量建议，不能替代DS/Bridge当前预算，也不能按建议自动扩容。Advice候选的三语显示和拒绝/过期状态由Host投影，关闭投影不停止共享session。

设备自带的自动模式只作为动态 Capability 参数处理：如果目标 Profile 声明 `Enumeration`/`Boolean` 自动模式，Definition 必须给出实际 protocol code、读回值和与手动字段的依赖；切换自动模式仍需显式 Apply、Readback 和权限，不得由 UI 选择格式或 Start 隐式打开。模块不拥有基于图像、轮廓或节拍的自动调参算法，也不把 `Source=Simulation` 的建议写成设备事实。需要软件推荐时，由 `IM-042 imaging-optimization` 或宿主提供候选 `(ParameterKey, Requested, BasisRevision, EvidenceId, ExpiresAt)`；DeepSight 只展示、校验 capability/range/permission 并在操作者确认后按普通 Apply 执行。候选过期、能力 hash 变化、输入证据缺失或读回不一致时标记 Stale/Unknown，零新写入。这样保留设备原生自动参数能力，同时不把调参算法、质量判定或生产放行塞入设备模块。


## 13. 双视角场景、反例与可判定断言

下列都是合成软件用例；先从实施人员按输入走命令/字段/资源，再从集成人按Factory→Host→Owner→关闭走一遍。客户量程/容差/节拍不由这些数值赋值。

| ID/输入 | 实施人员断言 | 集成人/Owner断言 |
|---|---|---|
| DS-T01 正常§12 fixture，A rate100→120 | Open/Read/Apply/Arm/Start/Stop/Close证明完整；Requested/Actual=120且Revision按完整值变化 | Archive/Inspector各独立调用同合同，Close Known/Released，零残余Root |
| DS-T02 Discover0/1/2设备 | 零设备Confirmed空列表，不是PASS；型号/来源不变；超容量DS-017不截断 | Root先预留；同DeviceId重复Session拒绝；不同设备互不封闭 |
| DS-T03 rate=0/NaN/单位us、HeadCommon采集、enum99、Depth0 | DS-001/002且0adapter写；不Clamp | Draft保留错误，切语言不改变数值/hash；不可表示UTF8拒绝不动作 |
| DS-T04 lower90/upper80、Patch重复/依赖环 | 整Patch拒绝无写；合法lower30/upper70按拓扑/Key顺序 | 不靠UI单字段验证，Core同断言 |
| DS-T05 多项write首成功次失败/读回+1/回滚失败 | 保逐项Before/Actual；回滚全确认保持Baseline，部分Unknown阻Start | 原Task/identity和业务+cleanup错误都保留；不自动重启 |
| DS-T06 Recipe0/63/-1/64及导入hash/版本不符 | 0/63读回一致；-1/64/hash错无动作；更新Capability+Snapshot | 老快照可读；无路径进入SDK；未知不盲切回旧配方 |
| DS-T07 同ID同hash/同ID异hash/新ID同Run Start | 原调用次数1/DS-012/DS-003；旧TriggerIndex不二发 | 两并发点击合并原记录，不删除未知墓碑腾位 |
| DS-T08 Start Hold→观察到期→迟到Release | 初Receipt Unknown/SideEffectPossible，后Query可以确认原动作；不能把当前Stop否定曾Start | 原Task/epoch/hash强持、设备槽不退，Root移交只转责任 |
| DS-T09 执行前cancel/执行后cancel/FaultAfter | 前者拒绝0动作；后者不回Created；独立cleanup预算 | Stop/Close/Query/Dispose嵌套finally皆有限且不覆盖business；一错误仍非0 |
| DS-T10 StopAckOnly、Close未知、SDK卡住 | 不Drained/Closed/ResourcesReleased；DS-011 | 查询不新起无限Task，不回池同设备、不强收raw borrow |
| DS-T11 账本/队列/Root满，2设备竞争 | DS-017零新业务；Stop/Close保底有效但不绕卡死SDK | 拒绝在Factory前；Root保旧record，同设备单写/不同设备并行有界 |
| DS-T12 I/O写/读回不符、撤权、ClearError/Reboot | 输出未知不置0；撤权DS-016零动作；Reboot不自动Ready/Start | 权限前检查+执行时检查，读快照不升级安全/质量权 |
| DS-T13 epoch隔离/旧封存副本/版本回退 | 旧live拒绝；旧历史副本仍可读；未知contract不动作 | 原native独占未释放不新epoch，旧副本不原地重写 |
| DS-T14 Bridge A/B各4行、I16(-32768)/U16(65535) | RawCode高度[0,10,invalid,30]code；物理证据Scale0.001候选投影[0,0.01,invalid,0.03]mm不升级标定，强度65535无signed溢出，两plane各8bytes、合计16bytes/行布局/独立Scale保留 | 无位置Position.Unknown；不造规则表面，不强制normalization |
| DS-T15 缺行/重复/逆序/短帧/池空/完整队列满 | PA封口Incomplete/明确range/Backpressure；Wait+TryWrite拒绝不静默Drop | preview丢弃不影响完整hash；保在途callback，Stop不能提前Complete |
| DS-T16 两消费者/一方borrow超时或抛错 | ProfileView借用在原Task退出前有效，不偷Retain | 双副本hash/invalid/序号一致；一方关闭不清另一方；PA资源Unknown留Root |
| DS-T17 两STA/切三语/草稿/卸载 | Bind不Open，长英文不藏Stop/错误；语言不改Core/Draft/单位；原命令和Query均Hold时Authority总观察共用1秒deadline，Query不重置预算 | 独立viewHost/Dispatcher/订阅；观察返回Unknown后原命令及QueryTask仍由Root强持；关A不Stop shared session，关B仍等原Task/lease |
| DS-T18 编码完整Close/Capability/Parameter | §5Golden72bytes精确；不同语言/文化同字节，换budget/epoch变化hash、换ID不变 | 两Host字段重建而非只hash常量；新schema拒绝，旧hash不覆盖 |

大量用例按冻结Profile重复10,000次状态/字节往返并周期清理，计Root/task/metadata峰值，无增长性残留；10,000是软件压力用例次数，不是长稳时长/吞吐达标目标。乱序/丢失明细超过容量明确截断与不完整，不创建无限Set。Timestamp的吞吐/延迟仍须§15实测。

## 14. 实施验证工程与必需执行

尚未创建工程/执行以下C#检查。准入后的Core/Test都`Microsoft.NET.Sdk/net10.0`；Test `OutputType=Exe`，仅引用Core和BCL，沿DEV-GOV-010 v2.1.2规定执行，不新增待选测试包、不用dotnet test无报错替代Exeharness。

```powershell
dotnet build src/Modules/deep-sight-control/Asun.Modules.DeepSightControl.Core/Asun.Modules.DeepSightControl.Core.csproj -c Release
dotnet run --project tests/Modules/deep-sight-control/Asun.Modules.DeepSightControl.Core.Tests/Asun.Modules.DeepSightControl.Core.Tests.csproj -c Release
```

入口无参数执行DS-T01～T13/T18全部Core必需断言，两种Host分别覆盖正常、拒绝、同步fault/异步fault、cancel、迟到归还、cleanup叠异常、Root拒容量/移交拒绝和回退；不跳过“难测”Unknown。每case固定虚拟clock/可控闩锁（自有BCL TimeProvider派生实现，不选外部包），case真实wall watchdog10秒，整个Exe外层120秒；任何失败/未完成/必需项跳过/Unknown残留非0，全部通过才0。

| 切片/用例 | 实施证据 | 不可代替 |
|---|---|---|
| DS-C1 命令/状态/身份/权限 | T01～03/07～13/18，两无UI Host实际构造/运行 | SDK/设备停止、跨重启幂等 |
| DS-C2 参数/配方/I/O/诊断 | T04～06/12/18，type/range/order/readback/rollback | 目标设备量程、调试批准 |
| DS-C3 Simulator/Host | 两种Host所有Core场景，原Task/Root容量/迟到强持 | 现场吞吐/长稳/安全 |
| DS-B1 ProfileBridge | 引用PA公开工程，按§7绑定；T14～16/PA原Exe相关断言 | native布局、真图数据精度 |
| DS-N1 Native | 81函数/7回调ABI角色、SizeOf/OffsetOf、回调GC/异常隔离/数据字节 | 目标型号全部能力/停止HIL |
| DS-U1 WPF | T17两STA真实25.2.3/UIA/1920viewport/三语/权限，PA预览Owner | 操作员客户现场验收 |
| Qualified/现场 | 目标Profile的Golden/Replay、触发/编码器/IO、断网/断电/重启、性能、长稳与FAT/SAT | Simulator/截图/单元测试 |

只读来源测试思想定位：[DeviceLifecycleTests](../../references/project-snapshots/DeepSight/20261004/original/tests/Asun.DeepSight.UnitTests/DeviceLifecycleTests.cs)、[FrameAndPersistenceTests](../../references/project-snapshots/DeepSight/20261004/original/tests/Asun.DeepSight.UnitTests/FrameAndPersistenceTests.cs)、[ParameterRecipeAndServiceTests](../../references/project-snapshots/DeepSight/20261004/original/tests/Asun.DeepSight.UnitTests/ParameterRecipeAndServiceTests.cs)。文件逐项hash由同来源manifest绑定；复用多设备/溢出/16位强度/篡改/文化无关/逐项回滚断言思想，不复制旧类型/UI/设备ID池/全局状态。`DisposeClosesAndReleasesSessionEvenWhenTransportStopFails`直接Closed与`StartCancellationRollsBackResourcesAndAllowsRetry`未区分已发动作的Ready结论禁止迁入。该来源为内部用户资产，不当作第三方MIT代码；外部runtime仅借鉴Channels语义，实际源码/测试定位见§2.1。

## 15. 性能、容量与可观测性

每种设备和消费者必须提供不可变 `BenchmarkProfile`，绑定传感器/固件/Adapter/API capability revision、采样格式、OS/驱动/运行时、数据 fixture hash。负载按 profiles、samples、bytesPerSample、heads、channels、stride/padding、payload/流长度、采集速率、预览策略、并发和冷/热状态分桶。容量预算还包括 lease 快照、Interop/Adapter 缓冲和 Replay 写入；不能以二维宽高替代实际数据布局。Profile 必须在运行前冻结预热与测量次数、最低有效样本数、有限 deadline、队列/lease/字节硬上限、固定吞吐窗口及验收阈值来源。冷启动另测；热态按固定预热次数执行，预热数据不计入统计。既往来源项目的开发数值不作为本模块指标。

分别测回调入队、完整流封口、链路吞吐、每 Run/epoch 的接收/接受/缺失/重复/逆序、预览丢弃、队列峰值、字节/复制数、lease 持有、GC、停止确认与 drain。记录各阶段单调时钟、队列等待、托管/native 资源峰值和真实取消到停止时间；无法观测的 native 资源记 `Unknown`，不得记零。通用冷/热、分位、样本有效性、失败/删失和未排空规则按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)。本模块另分项保留数据缺失、重复、逆序、预览丢弃及 `DrainUnknown`。阈值只来自已采纳设备/消费者 Profile；目标缺失标 `TargetPending`，不能用其它项目门槛或估算值声称达标。

具体测量驱动：Core冷样本从Root reservation/Factory开始，热样本固定预热后由同能力不同新Run测完整Open/Read/Apply/Arm/Start/Stop/Close闭环；起点请求接纳单调timestamp，终点已确认Close ResourcesReleased/Root中实际归还，另外计业务返回Receipt和迟到底层退出两条时间，不能用Unknown快速返回作为端到端低延迟。Bridge同时记录nativeCopy/PA.TryAccept/PA.OnProfile原Task/batch封口/raw.Close/PA.Close四轴；UI另记Bind首快照、语言发布、Dispatcher呈现与CloseProjection实际结束。Profile明确每case预热数/测量数/最小n/冷或热/负载/并发/执行与cleanup预算、Root/DS/raw/PA/Host/UI各额度和目标来源；测试合成fixture默认软件诊断预热0/测量10/最低有效10，但无时延/吞吐目标为NotEvaluated，不能填P95通过阈值。失败/取消/未排空样本单列，不从成功分位中偷偷筛掉。资源硬上限超即失败，目标数值待Profile不妨碍测量方法冻结。

结构化诊断至少包括 `OperationId`、`RunId`、`BatchId`、`ConnectionEpoch`、DeviceId（脱敏）、Adapter/设备版本、请求/实际参数、能力 hash、原生错误码、事件序号、队列/资源水位、是否已发送副作用、取消时间和 Drain 结果。日志不写入 ROI、量测或质量结论，不把原始秘密和完整帧默认写入日志。

## 16. 发布、迁移与回退

发布包候选内容：Core、Interop、WPF（可选）、公开契约、Simulator/Replay、RuntimeManifest、示例宿主、三语言资源、兼容矩阵和测试报告。来源记录中的 DLL 版本、签名状态、SHA-256、依赖和部署目录必须保留；是否再分发由部署方按许可和客户环境确认，不能把许可待确认表述为整个模块不可用。默认客户端包不内置厂家 DLL；获准的原生部署包必须按 x64、版本、hash、依赖和部署约束生成。

状态只允许按证据提升：`DesignReview/Prep -> Development -> HardwareVerified -> Qualified -> Released`。本页当前保持 `DesignReview/Prep`，没有代码或实机证据，不得声称任何后续等级。

迁移/升级前保存模块版本、Adapter/RuntimeManifest、能力 hash、参数/配方 hash、在途 Run/epoch 和 lease 状态。发现 ABI、布局、单位、事件或 lease 不兼容时：停止新 Run，隔离未排空 epoch，保留旧 Replay 只读，恢复上一版本，先查询原操作回执后再决定动作；禁止盲重发 Start、Stop、触发、运动或参数。旧 batch 不被新版本原地重写。

## 17. 逐切片六项准入与真实资格门

### 17.1 六项规格定位

主控本轮已按DEV-GOV-010 v2.1.2 §3.1定向回读完整Core/Simulator/双Host与Owner，并接收下表DS-C1/C2/C3六项文档规格为`ModuleCoreImplementationReady`。主控已独立按字段复算Close命令72bytes及派生身份52bytes，完整字节与hash一致。DS-B1的PA v0.3 Bridge、DS-U1的公开装配/接线内容仅限定接收；其集成与运行资格仍为`PreparationIncomplete / NotReady`。真实PA程序集、SDK、数据保真、WPF、性能及设备资格均未验证；无SDK最小Host和语义示例仍是规格，当前未构建运行。此处记录主控接收决定，不新增复审或实现授权。

| 切片 | 1 职责/消费者 | 2 唯一API/Owner | 3 无UI/SDK装配 | 4 场景断言 | 5 Benchmark口径 | 6 工程/路径/顺序 |
|---|---|---|---|---|---|---|
| DS-C1 控制/状态/身份/权限 | §1、Archive/Inspector | §3/5/6 typed Execute、Error、资源 | §12 Root→Factory→Session→Simulator | §13 T01～03/07～13/18 | §15命令阶段/原任务/删失 | Core/Test binding；§12完整顺序 |
| DS-C2 参数/配方/I/O/诊断 | §8设备事务，Host权限 | §3 typed Value/Definition/Receipt、codec/回读 | 同C1，无设备量程假设 | T04～06/12/18，逐项回滚/未知 | §15Patch项/Blob/metadata字节 | 同Core/Test；不写产品文件/DB |
| DS-C3 Simulator/双Host | §12明确合成、两个独立消费者 | §12公开Factory/fixture/故障/强持Owner | §12.1～3全部构造、原Task、有限cleanup | 两Host执行Core全部必需项，Root拒绝/移交/fault | 固定fixture、虚拟clock、冷热/删失 | Core Test Exe，§14命令，不建新测试栈 |
| DS-B1 ProfileBridge/完整流/Replay消费 | §7 PA唯一批次Owner | §7具体PA v0.3公开Adapter/借用/映射 | §12.3替换已定义PAHost adapter | T14～16、PA既有相关用例 | raw/PA/Host字节分别计费 | ProfileBridge/Bridge.Tests唯一工程；Core不引PA |
| DS-U1 独立WPF工作台 | §11角色/构图/连续任务 | §11公开Create/Host/Prepare/原Task/语言/投影Owner | 两STA纯构造，设备由Host装配；UI本身非纯Core | T17/§12.3，双view关闭/三语/UIA | 设备view订阅/原AuthorityTask/更新/metadata，组合PA view的Present/viewport另计 | Wpf/Wpf.Tests唯一工程，绑定本机25.2.3 |
| DS-N1 SR7Link/真实RawSource | §9厂商设备和ABI边界 | Core transport/§7 RawSource均明确；实际P/Invoke消费签名仍待目标设备 | 不需修改Core；原生对象只在Adapter | §14 Native/HIL矩阵 | 目标型号/固件/吞吐/停止资源 | Interop/Interop.Tests唯一工程；缺25D只阻25D |

### 17.2 实施顺序和准入状态

1. C1/C2/C3六项文档规格已接收为`ModuleCoreImplementationReady`；实际实现仍须另行明确派发并绑定权威代码仓库/分支，随后只按Core/Test目录开发。本地无.git及SDK外门不撤销或降级已接收Core规格；不等待真机或PA产品Schema，不只实现校验器而遗漏状态/参数/Simulator/恢复。本轮仅同步接收状态，不创建产品工程。
2. B1按现PA Module API v0.3公开形状的指定接线内容已限定接收，整体集成/运行资格仍`PreparationIncomplete / NotReady`；不将“共享签名未提供”作为永久阻断。真实PA程序集构建/Golden/端口语义一致、设备Profile、数据字节保真及Host资源断言在其适配/集成门验收，当前未验。
3. U1的§11/12.3指定公开装配/接线内容已限定接收，整体集成/运行资格仍`PreparationIncomplete / NotReady`；后续按明确派发构造TestHost，实测本机DevExpress25.2.3/WPF/固定视口/三语。本轮不创建工程、不下载DevExpress，不做其许可/版本准入审查。
4. N1以既有SR7Link.h/来源ABI注册表和批准目标Profile完成消费侧签名/回调/停止/Close实证；硬件厂商SDK具体代码不在当前文档任务，实现派发另限定。
5. HIL、客户量程/触发/编码器/时钟、Golden/Replay、目标性能/长稳及现场FAT/SAT关闭后才讨论HardwareVerified/Qualified/Released。

外门精确限定：支持SR/SRI型号/固件/头/量程及采样布局；16/32位单位/Scale/sentinel/stride/压缩/头同步；编码器回绕/校准/设备钟/封口证据；原生Stop/回调/Close真实证明；2.5D匹配头文件；客户/设备不能从资料得到的物理验收数值；部署目录/现场网络策略。目标缺失只阻依赖它的N1/产品资格，Core/Simulator不受影响。PA/Viewport产品接线、Store原子持久、Host正式权限与真实WPF运行也是后续受影响资格门，不等于要求在Core补产品业务。

旧§17“先统一全部共享合同才实现Core”顺序不再有效；批准技术依赖按用户决定直接使用。本页不调整近期客户交付代码/版本/节奏，不整项目搬入，不删除原快照/正式测试/被引用证据。

### 17.3 全模块文档准备结论

本轮按当前架构范围逐项复核，软件设计决定已经闭合；没有需要后续开发者补猜的内部算法、命令、Owner、线程、资源、恢复、Replay、自动参数或 UI 组合决定。各范围结论如下：

| 范围 | 当前文档结论 | 剩余门与责任 Owner |
|---|---|---|
| C1 控制/状态/身份/权限 | 六项规格已接收 `ModuleCoreImplementationReady`；§3/5/6/8/9/10/12/13/14 已冻结调用顺序、错误、账本、取消、排空和双 Host 断言 | Core/Test 实现与构建由本模块后续执行；无软件设计欠账 |
| C2 参数/配方/I/O/诊断 | 动态 Capability、单位/有效域、逐项读回/回滚、Recipe bytes、I/O/维护副作用和自动模式边界已冻结 | 设备 Profile Owner 提供真实量程、协议键、温度/编码器语义；不阻无设备的 Core/Simulator |
| C3 Simulator/双消费者 Host | 两消费者 Root reservation、原 Task 强持、可控故障、双 STA、有限收尾、完整流与预览流隔离已冻结 | Core.Tests/Bridge.Tests/Wpf.Tests 各自实现本工程助手；未运行不等于设计缺口 |
| N1 SR7Link Interop/Adapter | 9.1/9.4 已给 runtime manifest、81 导出角色、公开/内部/兼容分类、每模式导出顺序、回调布局、复制和关闭规则 | 目标 SR/SRI Profile、匹配头文件、DLL 部署和 HIL 由设备/部署 Owner；2.5D 因缺 `SR7Link25D.h` 保持不可用 |
| B1 ProfileBridge | 7.1～7.4 及 12.3 已冻结 PA v0.3 映射、AttachEpoch、派生身份、两次复制、借用/拒收/Stop/Close 责任 | PA 程序集构建、公开端口真实签名、数据字节保真和 Golden/Replay 由 PA 集成 Owner；当前仍 `PreparationIncomplete / NotReady` |
| U1 WPF 控件 | 11.1～11.3 已冻结 DevExpress 控件组合、布局持久化白名单、1920×1080、三语键、UIA、权限、键盘和恢复；无 UI 调用仍走 Core | WPF/DevExpress 25.2.3 编译、双 STA/UIA/DPI/客户操作验证由 WPF 集成 Owner；当前仍 `PreparationIncomplete / NotReady` |
| Replay | 12.4 已冻结同一 Core/PA codec、原身份回放、Fault 脚本、只读存储边界和禁止现场成功语义 | Store/Host Owner 提供对象读取、版本迁移和耐断电证据；不新增 DeepSight 文件格式 |
| 自动参数 | 12.4 已冻结设备原生自动模式的动态参数处理；软件推荐只接受 IM-042/宿主候选，过期/证据变化零写入 | `IM-042 imaging-optimization` 或宿主负责推荐算法和 EvidenceId；DeepSight 仅校验并经确认 Apply |

因此当前无“需要本模块继续决定的软件设计欠账”。未关闭内容均是准确 Profile、外部公开程序集、部署/设备、真实 WPF、Golden/Replay、性能、HIL 或客户物理验收门；它们只阻止受影响的 N1/B1/U1/产品资格，不降低已经接收的 C1/C2/C3 门禁，也不应通过编造数值或降低 `DEV-GOV-010` 标准解决。

## 18. 自审与状态声明

- [x] 本会话仅写入本模块DEVELOPMENT-GUIDE.md；架构总表、[模块索引](../MODULE-INDEX.md) 和共享契约由主会话统一维护。
- [x] 明确 Core/Interop/WPF/Simulator、完整轮廓流/预览流、参数/配方、连接/断线/重连/停止/排空、ABI、lease、资源和安全边界。
- [x] 明确与 IM-040、IM-060、IM-031、IM-010、ROI 的端口组合，且不把整机流程或 DZ-XVision 业务写入模块。
- [x] 明确不做 ROI、量测、质量判定，不依赖 AsunImage/HALCON/SImagePro。
- [x] 覆盖输入输出、状态错误、取消超时、线程、UI、第二消费者、测试、性能、发布回退和未决项。
- [x] 已将完整流 `Wait + TryWrite`、停止证明与资源排空、历史 lease 归还、参数 typed 有效域、WPF 固定视口操作链和逐切片准入矩阵写入本页。
- [x] 已闭合 SR7Link runtime/81导出/采集模式矩阵、断线新epoch、完整流缺失策略、Replay 输入边界、设备自动模式与软件推荐边界。
- [x] 已闭合 DevExpress 25.2.3 的布局保存白名单、三语错误恢复键、UIA/键盘/1920×1080 约束，并保留真实 WPF 运行门。
- [x] 保留来源 .NET 8 为只读参考，不宣称迁移、代码、实机、HIL、Qualified 或 Released 完成。

本版有限自审：实现者视角逐命令追到设备知识/资源轴和异常恢复，补齐参数StepContext及QuerySetting、Format/HeadSettings实际值证明、CanReadback/CanStop有效域、权限撤回后的清理责任；外部消费者视角从Factory前Root追至两种Host/Bridge/双STA构造和finally，补齐PA实际epoch Attach、分头键/格式/编码器映射、派生步骤GUID与原任务账本、真实raw复制计费、五保底task槽/6秒总收尾及离栈后Root恢复Owner；本轮再补齐SR7Link运行时/采集模式矩阵、Replay/自动参数边界和UI资源目录。上述都是内部准备规格，不能用SDK/HIL待验替代。

本轮交付边界是 `DesignReview/Prep` 指导文档；未执行代码构建、测试、真实设备、ABI 运行探针、性能或生产验收。

## 附录 A：模块核心 API Contract v0.2（核心冻结；逐切片准入）

本节定义本独立模块的核心代码边界，优先于正文中仅针对产品集成的映射措辞。§3 的公开类型、方法、事件、错误键、状态、参数表和代码形状，作为对应切片获准后唯一实施依据；本附录的存在不代表准入通过。实现者不得另造第二套核心 DTO、状态机或错误语义。

- `Module API Contract v0.2` 只覆盖无产品事实写入的 Core、Simulator 和显式 Adapter Port。它不把平台 C-01～C-08、客户工艺阈值、最终放行、产品数据库字段或厂商私有类型冻结为模块 API。
- 正文中仍称“候选”的内容，若属于平台 Schema 映射、序列化、Owner、生产资格或客户 Profile，继续保持候选；若属于本模块 Core 的字段/方法/事件/错误/资源语义，则按本节冻结，任何未定义操作必须先补回本指导再编码。
- 适配器必须以 `SR7Link.h`、目标设备 Profile 和实际公共程序集签名逐项核对；本模块是非视觉设备控制，HALCON/AsunImage 不适用且不进入合同。未核实的签名只阻断该适配器或 Bridge/UI 切片，不阻断可替换的 Core、Simulator 和契约测试。
- 准入状态：主控本轮已接收§17.1的DS-C1/C2/C3六项文档规格为`ModuleCoreImplementationReady`；DS-B1（PA v0.3 Bridge）/DS-U1仅指定公开装配与接线内容限定接收，集成/运行资格仍`PreparationIncomplete / NotReady`。真实PA程序集、SDK、数据保真、WPF、性能与设备资格未验；本地无.git或SDK外门不退回已接收Core。本轮仅同步此接收范围，不据此派发实现。

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

## Core implementation binding

- 准入路径`NewProjectRequired`。namespace `Asun.Modules.DeepSightControl`；Core `src/Modules/deep-sight-control/Asun.Modules.DeepSightControl.Core/Asun.Modules.DeepSightControl.Core.csproj`、Test `tests/Modules/deep-sight-control/Asun.Modules.DeepSightControl.Core.Tests/Asun.Modules.DeepSightControl.Core.Tests.csproj`，全部尚未创建。当前文档任务只允许本DEVELOPMENT-GUIDE.md写入。
- 后续明确派发C1/C2/C3只准上述Core/Test目录；Simulator首版在Core的Simulation子目录，Host/Root助手在Test，不成为产品隐藏全局服务。Core只BCL/net10.0；不得引用WPF/DX/PA/SDK/AsunImage。
- B1唯一 `src/Modules/deep-sight-control/Asun.Modules.DeepSightControl.ProfileBridge/Asun.Modules.DeepSightControl.ProfileBridge.csproj`、`tests/Modules/deep-sight-control/Asun.Modules.DeepSightControl.ProfileBridge.Tests/Asun.Modules.DeepSightControl.ProfileBridge.Tests.csproj`，namespace `Asun.Modules.DeepSightControl.ProfileBridge`，net10.0，显式引用Core和PA公开工程；不修改PA工程。
- U1唯一 `src/Modules/deep-sight-control/Asun.Modules.DeepSightControl.Wpf/Asun.Modules.DeepSightControl.Wpf.csproj`、`tests/Modules/deep-sight-control/Asun.Modules.DeepSightControl.Wpf.Tests/Asun.Modules.DeepSightControl.Wpf.Tests.csproj`，namespace `Asun.Modules.DeepSightControl.Wpf`，net10.0-windows/WPF、本机DevExpress25.2.3，TestHost OutputType=Exe、双STA只同1920viewport；不改显示设置。
- N1唯一 `src/Modules/deep-sight-control/Asun.Modules.DeepSightControl.Interop/Asun.Modules.DeepSightControl.Interop.csproj`、`tests/Modules/deep-sight-control/Asun.Modules.DeepSightControl.Interop.Tests/Asun.Modules.DeepSightControl.Interop.Tests.csproj`，namespace `Asun.Modules.DeepSightControl.Interop`，net10.0-windows/x64，依Core/Bridge公开合同。该绑定不授权本轮实现厂家SDK。
- 禁止写其它模块的src/tests、Shell/Domain/Integration、共享指导/架构/模块索引、AsunImage内部、参考原件/快照。具体工程仅在相应切片获准后创建，创建前确认权威代码仓库/分支；本目录无.git，不声称当前HEAD/CI。
- 本版交付阶段仍`DesignReview/Prep`；DS-C1/C2/C3文档规格已为`ModuleCoreImplementationReady`，B1/U1指定公开接线内容限定接收，其集成/运行资格仍`PreparationIncomplete / NotReady`，N1及产品资格未验。接收不是产品实现或运行通过；本轮同步后即停，不创建工程、不改共享，不继续旧队列或创建/派生模块会话。
