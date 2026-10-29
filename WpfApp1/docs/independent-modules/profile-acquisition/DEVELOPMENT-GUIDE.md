# 激光轮廓与三维传感采集模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`PA-C1, PA-C2, PA-C3, PA-C4`

- 模块键：`profile-acquisition`；模块 ID：`IM-040`；历史来源：`PKG-057`（0.1.0，DesignReview）。
- 文档版本：`0.3.3-prep`（2026-10-11；全批准范围准备收口）；模块状态：`DesignReview/Prep`、`PreparationIncomplete`。PA-C1～C4既有接收保持`ModuleCoreImplementationReady`（仅托管规格，未实现/未验真实标定）；PA-U既有指导内容接收保持，实际WPF资格/平台接线未验仍`PreparationIncomplete/NotReady`，不授`ImplementationSpecificationReady`。本轮补充逐行解码/有界Advice/可发布源适配与全部范围结论见§4.4、§7.4～7.5及§12；不据文档收口提升运行资格。
- 规划消费者：激光轮廓工具、独立 3D 传感调试/回放工具；点胶三维工具后续按公开端口接入。
- 本页是唯一实施指导，冻结模块内部规格，不覆盖平台 Schema/Owner。尚未创建工程，未执行 C#、HALCON、性能、WPF、HIL 或生产验收。
- 永久会话：`01a10307-0847-7d90-98c9-e32b45a7a714`，见 [模块索引](../MODULE-INDEX.md)。本轮只修改本页，不派生会话或代理。

## Core implementation binding

- 准入路径：`NewProjectRequired`；C# / .NET 10，Core 仅 BCL；namespace：`Asun.Modules.ProfileAcquisition`。
- 唯一计划代码工程：`src/Modules/profile-acquisition/Asun.Modules.ProfileAcquisition.Core/Asun.Modules.ProfileAcquisition.Core.csproj`。
- 唯一计划测试工程：`tests/Modules/profile-acquisition/Asun.Modules.ProfileAcquisition.Core.Tests/Asun.Modules.ProfileAcquisition.Core.Tests.csproj`。两个无 UI Host、Simulator/Replay 契约夹具及 Benchmark runner 是该 Exe 的不同模式，不另建测试栈。
- 可选WPF唯一计划工程：`src/Modules/profile-acquisition/Asun.Modules.ProfileAcquisition.Wpf/Asun.Modules.ProfileAcquisition.Wpf.csproj`，namespace `Asun.Modules.ProfileAcquisition.Wpf`，net10.0-windows/UseWPF=true，仅引用Core及本机DevExpress25.2.3程序集；无NuGet替代。唯一TestHost：`tests/Modules/profile-acquisition/Asun.Modules.ProfileAcquisition.Wpf.TestHost/Asun.Modules.ProfileAcquisition.Wpf.TestHost.csproj`，同目标/WPF Exe，仅Core+Wpf+BCL+本机DX，无测试包；STA启动。上述两个目录只在PA-U获准后允许创建/修改，不改变本轮仅写指导范围。
- 本轮允许写入仅本指导。以后明确获准的 Core 切片仅允许上述代码/测试目录，未获准前不创建空工程。
- 禁止其它模块、共享文件、产品 Shell/Domain/Integration、客户项目、参考原件、AsunImage 内部及 tools。具体 SDK/ABI/native 控制属于设备模块；DeepSight 属于 [IM-063 唯一指导](../deep-sight-control/DEVELOPMENT-GUIDE.md)，本模块不另建厂商驱动。
- 实现前绑定权威仓库/分支或已确认的可审计快照；当前目录无 .git。准入只按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)，逐切片定位见 §12。本文存在不授予整模块 Ready。

## 1. 职责、消费者与事实边界

### 1.1 负责与不负责

Core 负责能力发现、参数校验/读回、会话/连接代、显式 Arm/Start/Trigger/Stop、逐轮廓原始保全、身份/布局/顺序检查、位置及时间证据、结构封口、有界输送与排空查询。输入域可为厂商已标定高度、原始数码、disparity 或 profile image，不混用单位。

Core 不提取激光线、不三角重建、不滤波/插值/拟合/计量、不造三角面，不拥有产品配方、目标、工单、公差、PASS/FAIL 或放行。运动、发光、安全互锁与自动重采由宿主/设备 Owner 决定。Complete 只说明某头某批结构闭合，不能推出样本有效、位置合格、设备安全或产品合格。

激光轮廓工具逐条保存或传递原始输入；第二消费者为独立调试/回放工具，统计并显示原序号、无效域及位置证据。两者使用同一 Core API，不读取 PCB/点胶私表、ViewModel 或 SDK。一个运行若需要归档与重建，宿主注册一个复合完整 sink，等其全部子任务结束才归还借用；两个 Channel reader 不能充当完整流广播。

### 1.2 依赖方向与唯一 Owner

```text
无 UI Host / 可选 WPF 投影
  → ProfileAcquisition Core（本页 API；TimeProvider、buffer port、一个完整 sink）
  → Sensor Adapter Port（设备、Replay 或 Simulator）
  → 原始复制保全 → 完整 sink → 保存/重建/表面公开端口
```

物理设备只有一个写入 Owner。设备模块拥有 SDK/native 线程及停采证明；Core 拥有本模块状态、暂存/查询；宿主拥有授权及领域事实；共享帧模块仍是共享分配器 Owner。本页 buffer port 只定义边界，不复制平台帧池。独立 Core 的托管暂存替换为平台桥时仍沿用唯一公开 buffer Owner，不暴露 SDK 指针。

平台 Contract/Schema、共享租约和 DeepSight 公开端口映射需原 Owner 与主控串行接收，只阻断相关集成切片。Core 不依赖平台候选 DTO、数据库、窗口初始化或 HALCON 句柄。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.ProfileAcquisition.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"Core 不依赖平台候选 DTO、数据库、窗口初始化或 HALCON 句柄"。

**Blazor/Web**：轮廓采集状态与帧率通过 SignalR 推送；轮廓数据通过 gRPC 流传输；浏览器只渲染轮廓标记，不重建轮廓。

**AI Tiling**：激光轮廓采集结果经 `surface-data` 可供 3D AI 异常检测使用；本模块不持有推理 tile 租约，不参与分块编排。

**HALCON 不适用**：本模块是设备采集事务，不执行视觉算法；HALCON 备选 CI 不涉及本模块核心。

## 2. 路线与已查证来源

### 2.1 HALCON 26.05：采集和重建分开

采集主路线为原始直通与证据检查，属非视觉事务。重建模块按输入域选择下表路线，经 **ImageLibDotNet.cv2** 使用 HALCON 26.05；不重复核算子覆盖，不另接 HOperatorSet/halcondotnet.dll，不读 AsunImage 内部。下表为已核对算子语义，不冒充已编译 C# 调用；重载/封送歧义只在重建适配切片查看公共签名或消费项目编译。

| 输入与选择 | 已读目标版本资料 | 必须传递的约束 |
|---|---|---|
| 已标定高度：直接消费 | 设备 Profile 的单位/格式/标定 | 不再重复重建；保留原码与标定引用，不能给 code 套默认 mm |
| 激光线 image：重建模块量测 | [measure_profile_sheet_of_light](../../../halcon算子手册/operators/measure_profile_sheet_of_light.html) | 按列处理近水平激光线及 ProfileRegion；MovementPose 是相邻 profile 相对物体运动；none/xz 忽略它，xyz 非恒定运动须逐次真实 pose |
| 已有 disparity：导入重建模型 | [set_profile_sheet_of_light](../../../halcon算子手册/operators/set_profile_sheet_of_light.html) | 每行一个 profile，相邻行相对变换；一个 pose 成默认，空用默认。缺行不能压缩后继续恒定位姿 |
| 固定标定闭包后转换 | [apply_sheet_of_light_calibration](../../../halcon算子手册/operators/apply_sheet_of_light_calibration.html) | 后一输入较短需 reset，防旧尾行；模型/native 所有权留在重建 |
| 读取结果 | [get_sheet_of_light_result](../../../halcon算子手册/operators/get_sheet_of_light_result.html) | disparity 是亚像素 row 伪距离，不是 mm；score_type=none 可为空；未算结果为空；xyz 单位依 scale、frame 依标定 |
| 点云读取 | [get_sheet_of_light_result_object_model_3d](../../../halcon算子手册/operators/get_sheet_of_light_result_object_model_3d.html) | calibration 须 xyz 或 offset_scale；未量测为空；点云不带三角面；offset_scale 不自动证明物理标定 |
| 歧义参数 | [set_sheet_of_light_param](../../../halcon算子手册/operators/set_sheet_of_light_param.html) | first/last/brightest 等由重建明确选择，采集不得“取第一条”消歧 |

备用路线仅在 Host 显式选择 Replay 时替代 live，保留 Replay 来源，不在故障后静默切模拟。二维图像伪高度、无位置规则网格、自写三角重建及 AI 补洞均不选：无事实或职责依据。有界参数建议在§7.5冻结能力/预算约束、候选算法、证据/拒绝/过期及无UI入口，不Apply、不搜索物理质量阈值、不静默改参数。自动搜索最优曝光/激光功率、去噪或学习型补洞不属于本模块；它们需要重建/优化的真实数据及相应Owner。

### 2.2 源码/测试研究与迁移限度

复用已读证据，不重复下载，不以参考项目测试或 README 推导本模块通过。

| 固定来源与元数据 | 实读原件、采纳结论 | 限度 |
|---|---|---|
| Aravis 0.8.36；commit `97ff5e330919d7a44b871df4eda669feeafdf342`；LGPL-2.1，buffer 测试 SPDX Unlicense；C/GLib/GObject/Meson | [arvstream.c](../../references/open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/src/arvstream.c)、[buffer.c](../../references/open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/tests/buffer.c)：push 所有权转移、pop 后仍查 status、外部 buffer 独立释放、设备/系统时钟分开；已联网核对 [commit](https://github.com/AravisProject/aravis/commit/97ff5e330919d7a44b871df4eda669feeafdf342) | 只迁移思想/断言，不引 C 库，不证明轮廓设备协议/HIL |
| .NET runtime commit `60629d14374c56f1cb51819049ad1fa529307f8d`；MIT；BCL Channels | [BoundedChannel.cs](../../references/open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Threading.Channels/src/System/Threading/Channels/BoundedChannel.cs)、[BoundedChannelTests.cs](../../references/open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Threading.Channels/tests/BoundedChannelTests.cs)；[微软 Channels](https://learn.microsoft.com/en-us/dotnet/core/extensions/channels)：Wait/TryWrite、drop、容量断言 | Complete 仅封 writer；Channel 非广播；不在 native callback 等待或运行同步延续 |
| DeepSight 内部用户快照20261004；.NET 8；tree SHA-256 `9aba46935cd1a2750146dbbc98fcb754a4573b96f9537ecf03b1774f3f346fe0` | [manifest](../../references/project-snapshots/DeepSight/20261004/source-manifest.json)、[DeepSightFrameLease.cs](../../references/project-snapshots/DeepSight/20261004/original/src/Asun.DeepSight.Core/DeepSightFrameLease.cs)、[FrameAndPersistenceTests.cs](../../references/project-snapshots/DeepSight/20261004/original/tests/Asun.DeepSight.UnitTests/FrameAndPersistenceTests.cs)：checked 长度、可选 planes、失败归还、16-bit 强度、metadata篡改/文化无关测试 | 不搬 Clone/Dispose 并发实现或SDK；DeviceId/headA/B/配方/UI不进Core；源512MiB不转通用门槛；厂商Owner仍IM-063 |

版本/许可基线见 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)。实际复制源码须按 DEV-GOV-006 记录来源并完成目标验证；本轮未复制产品代码。

### 2.3 DevExpress 25.2.3 依据

在线官方 API 页返回403，当前无可调用 dxdocs；已读本机官方25.2.3 XML，不安装、不下载、不核授权。根路径：
`C:/Program Files/DevExpress 25.2/Components/Offline Packages/<package>/25.2.3/lib/net8.0-windows/`。

| package / 官方XML | 已核对成员 |
|---|---|
| devexpress.wpf.docking / DevExpress.Xpf.Docking.v25.2.xml | DockLayoutManager、LayoutPanel、DocumentGroup、TabbedGroup、SaveLayoutToXml(String) |
| devexpress.wpf.grid.core / DevExpress.Xpf.Grid.v25.2.xml、DevExpress.Xpf.Grid.v25.2.Core.xml | GridControl、TableView、TreeListView、TableView.ShowAutoFilterRow；本轮补查继承DataControlBase.SelectedItem/SelectedItemChanged、CurrentItem/CurrentItemChanged |
| devexpress.wpf.propertygrid / DevExpress.Xpf.PropertyGrid.v25.2.xml | PropertyGridControl、SelectedObject、PropertyDefinitions |
| devexpress.wpf.charts / DevExpress.Xpf.Charts.v25.2.xml | ChartControl、XYDiagram2D、LineSeries2D |
| devexpress.wpf.core / DevExpress.Xpf.Core.v25.2.xml | SuperTip、Items、SuperTipItem.Content、SuperTipHeaderItem、BarButtonItem、BarItem.SuperTip |

原GridControl.SelectedItem查阅只限主XML；本轮补查同版本Core.xml已确认其基类DataControlBase.SelectedItem双向绑定及SelectedItemChanged联动，不再留自有selection接口空项。Flyout不选，不猜其API。真实WPF调用与1920三语/UIA门后置，XML查阅不等于UI验收。

## 3. Module API Contract v0.3

### 3.1 唯一公开形状

本节替代旧未定义 DTO 和通用冻结附录，只有一套 Core API。以下是**待实现签名规格**，不是已存在/已编译源码文件；所有非BCL类型均在此定义。工厂构造不Open、不创建窗口/线程隐藏宿主、不读文件；记录构造后仍需校验，不静默裁剪。命令通过一个 ExecuteAsync 入口强类型分派，不另造同义方法/结果。

```csharp
namespace Asun.Modules.ProfileAcquisition;

public readonly record struct OperationId(Guid Value);
public readonly record struct RunId(Guid Value);
public readonly record struct Epoch(Guid Value);
public readonly record struct HeadId(string Value);
public readonly record struct BatchKey(RunId Run, HeadId Head, ulong Index);
public sealed record Revision(string Id, string Sha256);
public enum SourceKind { Vendor, Replay, Simulation }
public enum ValueDomain { RawCode, CalibratedHeight, Disparity, ProfileImage }
public enum ScalarKind { U8, U16, U32, I16, I32, F32, F64 }
public enum ByteOrder { LittleEndian, BigEndian }
public enum PlaneKind { Line, Image }
public enum TriggerMode { FreeRun, External, Encoder, Software }
public enum RunMode { Single, Continuous }
public enum PositionQualification { Unknown, Observed }
public enum StructuralStatus { Complete, Incomplete, Unknown }
public enum DrainState { Pending, Unknown, Released }
public enum Knowledge { Confirmed, Unknown }
public enum OperationPhase { Rejected, Accepted, Executing, Confirmed, Unknown }
public enum SessionState { Created, Open, Ready, Configured, Armed, Running,
    StopRequested, Draining, Stopped, Quarantined, Closed }
public enum StopReason { Completed, UserRequested, Cancelled, Deadline, Fault }
public enum InvalidReason { Sentinel, NonFinite, Saturated, Occluded, VendorInvalid }
public enum ErrorCode { InvalidArgument, CapabilityUnavailable, StateConflict,
    ConfigurationPartial, TriggerUnknown, LayoutInvalid, SequenceGap,
    HeadBatchMismatch, PositionUnknown, Backpressure, Cancelled, Timeout,
    StaleEpoch, AdapterFault, ResourceDrainUnknown, OperationConflict,
    LookupUnknown, EventGap, UnsupportedVersion, ConsumerFault }
public sealed record Error(ErrorCode Code, string DetailKey, string? VendorCode);
public sealed record ValidationIssue(string Field, ErrorCode Code, string DetailKey);
public sealed record Budget(TimeSpan Execution, TimeSpan Drain);
public sealed record ResourceLimits(int BufferedProfiles, long OwnedBytes,
    int MetadataBytes, int MissingRanges, int RecentSequences, int EventRecords,
    int OperationRecords, int BatchSummaries);
public sealed record SessionOptions(ResourceLimits Limits, Budget Cleanup);
public sealed record CommandContext(OperationId Id, Epoch Epoch, Budget Budget);
public sealed record NumericRange(double Min, double Max);
public sealed record PlaneFormat(string Role, ScalarKind Scalar,
    ByteOrder Order, PlaneKind Kind, int MaxRows, string Unit,
    double Scale, double Offset);
public sealed record InvalidEncoding(string PlaneRole, ulong BitPattern, InvalidReason Reason);
public sealed record FormatSpec(string Id, Revision Revision, ValueDomain Domain,
    string PrimaryRole, string Unit, int MinSamples, int MaxSamples, int MaxPayloadBytes,
    IReadOnlyList<PlaneFormat> Planes, IReadOnlyList<InvalidEncoding> InvalidCodes);
public sealed record EncoderSpec(string Id, int Bits, ulong MaxStep,
    bool SupportsReverse, double MmPerCount, int Sign, double OffsetMm, Revision Calibration);
public sealed record HeadSpec(HeadId Id, IReadOnlyList<FormatSpec> Formats,
    NumericRange? LineRateHz, NumericRange? ExposureUs,
    IReadOnlyList<TriggerMode> Triggers, IReadOnlyList<EncoderSpec> Encoders);
public sealed record Capability(string DeviceId, string AdapterId, string AdapterVersion,
    Revision Revision, IReadOnlyList<HeadSpec> Heads, bool CanPauseInput,
    bool CanStop, bool CanReadback, bool CanQueryOperation);
public sealed record ParameterSet(Revision Revision, IReadOnlyList<HeadId> Heads,
    string FormatId, TriggerMode Trigger, double? LineRateHz, double? ExposureUs,
    string? EncoderId, Revision? Calibration);
public enum FieldKnowledge { Applied, Readback, Unknown, Rejected }
public sealed record FieldReceipt(string Field, FieldKnowledge Knowledge,
    string? RequestedValue, string? ActualValue, Error? Error);
public sealed record ParameterReceipt(ParameterSet Requested, ParameterSet? Actual,
    IReadOnlyList<FieldReceipt> Fields, bool ReadbackComplete);
public sealed record HeadPlan(HeadId Head, ulong FirstSequence, uint ProfilesPerBatch);
public sealed record RunPlan(RunId Run, RunMode Mode, Revision Parameters,
    IReadOnlyList<HeadPlan> Heads, uint? MaxBatchesPerHead,
    TimeSpan BatchDeadline, TimeSpan MaxRunDuration);
public sealed record TimeObservation(ulong RawTicks, ulong TicksPerSecond,
    string Domain, string BootEpoch, long? Nanoseconds, long? ErrorBoundNs);
public enum PositionSource { Unknown, Encoder, DeviceActual, CommandOnly }
public sealed record PositionObservation(PositionSource Source, string Frame,
    Revision? Calibration, string? EncoderId, ulong? RawCount,
    ulong Segment, double? ActualYMm, double? CommandYMm);
public sealed record PlaneLayout(string Role, int Offset, int Rows, int Columns,
    int RowStrideBytes, int PixelStrideBytes, ScalarKind Scalar, ByteOrder Order);
public sealed record InvalidSpan(string Role, int Row, int Start, int Count, InvalidReason Reason);
public sealed record AdapterFrame(Epoch Epoch, BatchKey Batch, ulong Sequence,
    ulong RawSequence, int RawSequenceBits, ulong? TriggerIndex, int SampleCount, string FormatId,
    IReadOnlyList<PlaneLayout> Planes, ReadOnlyMemory<byte> Payload,
    IReadOnlyList<InvalidSpan> Invalid, PositionObservation Position,
    TimeObservation? SampleTime, SourceKind Source);
public enum SignalKind { BatchEnd, InputEnded, TriggerObserved, Disconnected, Fault }
public sealed record AdapterSignal(Epoch Epoch, RunId? Run, BatchKey? Batch,
    SignalKind Kind, ulong? Sequence, TimeObservation? Time, Error? Error);
public enum PushStatus { Copied, Refused, Stale }
public sealed record PushResult(PushStatus Status, Error? Error);
public interface IProfileIngress
{
    PushResult TryAccept(AdapterFrame borrowed);
    bool TrySignal(AdapterSignal signal);
}
public interface IWritableProfileBuffer : IDisposable
{
    Memory<byte> Memory { get; }
    long AllocatedBytes { get; }
}
public interface IProfileBufferPort
{
    bool TryRent(int payloadBytes, long remainingOwnedBytes,
        out IWritableProfileBuffer? buffer);
}
public sealed record ProfileView(AdapterFrame Metadata, FormatSpec? Format, PositionObservation Position,
    IReadOnlyList<InvalidSpan> Invalid, ReadOnlyMemory<byte> Payload,
    string PayloadSha256, string ContentSha256,
    long ReceiveTimestamp, Guid LeaseId, long AllocatedBytes);
public sealed record MissingRange(ulong First, ulong Last);
public sealed record BatchSummary(BatchKey Key, ulong FirstSequence, uint Expected,
    ulong Received, ulong Delivered, ulong InvalidElements, StructuralStatus Structure,
    IReadOnlyList<MissingRange> Missing, bool MissingDetailsTruncated,
    PositionQualification Position, Revision Parameters, Revision Capability,
    Revision? Calibration, SourceKind Source, string HashScheme, string BatchSha256,
    IReadOnlyList<Error> Errors);
public sealed record RejectedProfile(BatchKey Key, ulong Sequence,
    Error Error, ProfileView? Preserved);
public interface ICompleteProfileSink
{
    ValueTask OnProfileAsync(ProfileView borrowed, CancellationToken cancellation);
    ValueTask OnRejectedAsync(RejectedProfile rejection, CancellationToken cancellation);
    ValueTask OnBatchAsync(BatchSummary summary, CancellationToken cancellation);
}
public abstract record Command(CommandContext Context);
public sealed record OpenCommand(CommandContext Context, string DeviceId) : Command(Context);
public sealed record DiscoverCommand(CommandContext Context) : Command(Context);
public sealed record ApplyCommand(CommandContext Context, ParameterSet Parameters) : Command(Context);
public sealed record ArmCommand(CommandContext Context, RunPlan Plan) : Command(Context);
public sealed record StartCommand(CommandContext Context, RunId Run) : Command(Context);
public sealed record TriggerCommand(CommandContext Context, RunId Run, ulong TriggerIndex) : Command(Context);
public sealed record StopCommand(CommandContext Context, RunId Run, StopReason Reason) : Command(Context);
public sealed record CloseCommand(CommandContext Context) : Command(Context);
public sealed record ResourceSnapshot(DrainState State, long OwnedBytes,
    int BufferedProfiles, int ActiveCallbacks, int ActiveConsumerTasks,
    bool InputEnded, bool NativeDrained, bool ConnectionReleased, Knowledge CountersKnowledge);
public sealed record HeadProgress(HeadId Head, ulong BatchIndex, ulong Received,
    ulong Delivered, ulong InvalidElements, ulong? LastSequence);
public sealed record RunSnapshot(RunId Run, Epoch Epoch, SessionState State,
    IReadOnlyList<HeadProgress> CurrentHeads, IReadOnlyList<BatchSummary> RecentBatches, ResourceSnapshot Resources,
    ulong EventSequence, Error? Error);
public sealed record OperationReceipt(OperationId Id, Epoch Epoch, string? RequestSha256,
    OperationPhase Phase, Knowledge DeviceKnowledge, Capability? Capability,
    ParameterReceipt? Parameters, RunSnapshot? Run, ResourceSnapshot Resources,
    SessionState State, Error? Error);
public enum AdapterActivity { Unknown, OpenIdle, Acquiring, Stopped, Closed }
public sealed record AdapterReply(Knowledge Knowledge, Capability? Capability,
    ParameterReceipt? Parameters, bool InputEnded, bool NativeDrained,
    bool ConnectionReleased, AdapterActivity Activity, ulong? CommittedTriggerIndex, Error? Error);
public sealed record AdapterRequest(Command Command, RunPlan? ArmedPlan,
    ParameterSet? AppliedParameters);
public interface IProfileSensorAdapter
{
    string Id { get; }
    string Version { get; }
    SourceKind Source { get; }
    ValueTask<AdapterReply> ExecuteAsync(AdapterRequest request,
        IProfileIngress ingress, CancellationToken cancellation);
    ValueTask<AdapterReply> QueryAsync(OperationId original, Epoch epoch,
        Budget budget, CancellationToken cancellation);
}
public enum EventKind { SessionOpened, CapabilityRead, ParametersRead, RunArmed,
    StartRequested, AcquisitionStarted, StartUnknown, TriggerRequested, TriggerObserved,
    ProfileReceived, ProfileRejected, BatchSealed, StopRequested, AcquisitionStopped,
    DrainUnknown, ResourcesReleased, RunCompleted, SessionClosed, Diagnostic, EventGap }
public sealed record ProfileEvent(ulong Sequence, Epoch Epoch, RunId? Run,
    BatchKey? Batch, ulong? ProfileSequence, ulong? TriggerIndex,
    EventKind Kind, OperationId? Operation, SourceKind Source, string AdapterVersion,
    long MonotonicTimestamp, TimeObservation? SampleTime, BatchSummary? Summary,
    ulong? MissingFirstEvent, ulong? MissingLastEvent, Error? Error);
public sealed class ProfileAcquisitionException : Exception
{
    public Error Error { get; }
    public ProfileAcquisitionException(Error error); // 待实现签名
}
public sealed record ContractDecode<T>(T? Value, Error? Error) where T : class;
public static class ProfileContractCodec
{
    public static byte[] EncodeCommandForHash(Command command);
    public static byte[] EncodeReceipt(OperationReceipt receipt);
    public static byte[] EncodeRun(RunSnapshot snapshot);
    public static byte[] EncodeBatch(BatchSummary summary);
    public static byte[] EncodeEvent(ProfileEvent value);
    public static ContractDecode<OperationReceipt> DecodeReceipt(ReadOnlyMemory<byte> bytes,
        int maxBytes, int maxCollectionElements);
    public static ContractDecode<RunSnapshot> DecodeRun(ReadOnlyMemory<byte> bytes,
        int maxBytes, int maxCollectionElements);
    public static ContractDecode<BatchSummary> DecodeBatch(ReadOnlyMemory<byte> bytes,
        int maxBytes, int maxCollectionElements);
    public static ContractDecode<ProfileEvent> DecodeEvent(ReadOnlyMemory<byte> bytes,
        int maxBytes, int maxCollectionElements);
}
public interface IProfileAcquisitionSession : IAsyncDisposable
{
    Epoch Epoch { get; }
    ValueTask<OperationReceipt> ExecuteAsync(Command command, CancellationToken cancellation);
    ValueTask<OperationReceipt> QueryOperationAsync(OperationId original,
        Budget budget, CancellationToken cancellation);
    ValueTask<RunSnapshot> QueryRunAsync(RunId run, Budget budget, CancellationToken cancellation);
    IAsyncEnumerable<ProfileEvent> ReadEventsAsync(ulong afterSequence,
        CancellationToken cancellation);
}
public static class ProfileAcquisitionFactory
{
    public static IProfileAcquisitionSession Create(IProfileSensorAdapter adapter,
        IProfileBufferPort buffers, ICompleteProfileSink sink,
        SessionOptions options, TimeProvider clock); // 待实现规格签名
    public static IProfileBufferPort CreateManagedBuffers(long maxAllocatedBytes);
    public static IReadOnlyList<ValidationIssue> Validate(SessionOptions options);
    public static IReadOnlyList<ValidationIssue> Validate(ParameterSet requested, Capability capability);
    public static IReadOnlyList<ValidationIssue> Validate(RunPlan plan, ParameterReceipt applied);
}
```

工厂静态方法实现时补方法体。Create 对 null依赖/无效options 抛 ArgumentException，无设备动作；命令可预期错误用回执。CreateManagedBuffers 采用精确长度 byte[]、原子有界reservation、Dispose清内部引用并扣账，不声称GC已归还OS。自定义port必须分配前预留实际容量，实际 AllocatedBytes≥Memory.Length≥payloadBytes 且≤remainingOwnedBytes；false时buffer=null且无遗留分配。Core再次核对port回执，违规隔离Owner并拒绝继续；ArrayPool超额容量不能按payload长度少计。该暂存非第二套共享帧池。

未接纳且可完全表示的非法命令返回Rejected/PA-001，无adapter动作；本身null命令/无法冻结或编码的命令（非法字符串、未定义枚举等）抛ProfileAcquisitionException(PA-001)，该同步异常不建立伪operation/hash。Create保留ArgumentException约定。ReadEvents的非法游标、订阅额度、已闭合或故障均在首次MoveNext以ProfileAcquisitionException表达；预期Execute/Query取消和deadline以原回执表达，不把OperationCanceledException当资源完成。Dispose的PA-015同样用ProfileAcquisitionException，调用者根据Error而非Message恢复。非预期OOM等异常不能伪造成功，Owner仍保已有资源。

### 3.2 有效域、单位与来源

| 输入 | 有效域与来源 | 缺失/变更 |
|---|---|---|
| IDs/epoch/标识 | Guid非Empty；epoch由工厂创建随机Guid，跨重启不靠进程内递增；标识1..128 UTF-8 bytes、无NUL/未配对surrogate、大小写敏感，不自动Unicode规范化 | epoch必须等session；重连新session，DeviceId不猜型号 |
| Revision | Id非空、Sha256=64小写hex；能力/参数/格式/标定分开冻结 | 不用latest替历史，不拿source hash代替整个请求hash |
| 头/格式/触发 | 非空唯一头集合，均存在能力；FormatId在所选头有相同Revision及布局；Trigger均支持 | 不自动选首头/格式；异格式多头分run/session |
| 线频Hz/曝光μs | null为设备决定但必须读回；有值finite>0且在能力NumericRange；range finite、0<Min≤Max | 0不代表自动；无范围拒绝显式调参；不编通用上限 |
| 采集计划 | ProfilesPerBatch>0；Single MaxBatchesPerHead=1；Continuous为正数或null；Heads与实际参数相同；所有序号乘加checked | 空计划非法，连续仍有有限MaxRunDuration；每头独立批 |
| deadline | Budget.Execution/Drain、BatchDeadline/MaxRunDuration finite TimeSpan>0，显式Host/Profile输入；TimeProvider单调剩余 | 无生产默认秒数；Drain独立于已取消业务token |
| 资源 | ResourceLimits各项>0；一条最大合法输入及其元数据必须可容纳；列表/字符串/diagnostic/去重/摘要占MetadataBytes | 先预留slots/实际bytes/metadata；不把整批常驻内存当启动要求 |
| 布局 | Role恰符format且唯一；Line Rows=1/Columns=SampleCount；Image Columns=SampleCount、1≤Rows≤MaxRows；Offset≥0、PixelStride≥scalar bytes、RowStride≥本行跨度 | checked Offset+(Rows-1)×RowStride+(Columns-1)×PixelStride+scalar bytes≤payload；保守要求各plane包围区间不重叠，拒绝交织布局而不猜 |
| scalar/invalid | byte数依1/2/4/8；endianness明确；invalid span Role/Row/Start/Count合法；bit pattern不得超scalar位宽；所有NaN/Inf显式无效 | invalid并集按(role,row,column)计数，同点多原因保留；不填0，强度域与高度域不混 |
| 数值域 | RawCode=code；CalibratedHeight=mm；Disparity=row；ProfileImage=pixel；格式域与主plane一致且有来源 | 无默认ZScale=1 mm；X几何由标定/重建Owner定义，本版不推断 |
| Encoder | Bits 2..64、0<MaxStep<2^(Bits-1)、MmPerCount finite>0、Sign±1、Offset finite；来源设备/标定 | 无半模数以内步进证明则Unknown；reset新Segment，不能猜多圈 |
| Position | Frame/Calibration/EncoderId与冻结参数一致；ActualYMm/CommandYMm有值须finite；RawCount在位宽内 | CommandOnly不提升Observed；非规则0/1/3 mm原样保留 |
| Time | 原ticks/frequency/domain/boot epoch保留，frequency>0；ns checked宽中间整数换算，误差≥0 | 无映射ns=null，接收clock不能当采样clock，未知域不能跨头相减 |

接纳前深冻结所有请求及能力列表，限制metadata，防调用方修改；帧深拷贝规则见§4。ReadbackComplete仅在必需字段全部读回、实际值合法且与设备编码后的确切请求一致时true；本版无自动舍入/容差，设备需要舍入时Profile先定义请求编码再发送。FieldReceipt文本只用规范单位和文化无关表示，Actual ParameterSet是唯一类型化实际快照。仅ACK/部分写入为ConfigurationPartial/Unknown，不Arm；live不能读回时本版不启生产采集，不用模拟读回冒充真实。

所有枚举拒绝未定义数值，所有列表/Revision/必需字符串拒绝null；能力须有非空唯一Heads/Formats/Planes、MinSamples>0且≤MaxSamples、MaxPayloadBytes>0、MaxRows>0、Line的MaxRows=1。参数EncoderId存在时Calibration须匹配该EncoderSpec；设备已标定高度须有标定引用。RunPlan.Parameters必须等实际读回Revision，Heads与Actual完全对应；FirstSequence和最大声明批数的尾序号不能溢出。Continuous无最大批数也在每次创建下一批前checked并受控停。

PrimaryRole必须唯一存在，Unit等该plane.Unit；每plane明确Unit、finite非零Scale及finite Offset，编码数值的物理解释为scalar×Scale+Offset（无效码先拒识），原字节始终保留，派生值不写回。本版输入是未压缩标量plane，不支持PNG/私有压缩包直接冒充pixel。CalibratedHeight的主plane.Unit=mm且参数有标定；RawCode的主plane.Unit=code/Scale=1/Offset=0；Disparity=row；ProfileImage=pixel。辅助强度等plane各有自己的单位/映射，不凭主plane单位猜。

### 3.3 操作/回执/幂等

| 操作 | 前置→动作→知识 |
|---|---|
| OpenCommand | Created且宿主已授权独占→adapter注册ingress/Open→确认才Open，unknown隔离 |
| DiscoverCommand | Open/Ready/Configured或已Released的Stopped且无在途run→读能力；首次/能力变化变Ready并失效旧参数，完全相同能力及已读回参数保Configured；失败不返回空能力 |
| ApplyCommand | Ready/Configured或已Released的Stopped→Validate→adapter应用/读回→Configured或部分/unknown；运行中拒绝 |
| ArmCommand | Configured或已Released的Stopped、完全读回、计划/预算/容量闭合→Core登记新run和唯一sink→Armed；不调用adapter、不发触发 |
| StartCommand | Armed→记录StartRequested→adapter Start→实际开始证明才Running；ACK不足，未知保留原run |
| TriggerCommand | Running且Software→Run/TriggerIndex唯一动作→回执≠采样；TriggerObserved和数据是独立事实 |
| StopCommand | Armed/Running/StopRequested/Draining→停止新输入→一次原清理任务→回执含设备知识与资源；Armed未启动纯Core结束 |
| CloseCommand | 无run直接关闭；有run先同原run清理再adapter Close；ConnectionReleased及资源屏障后Closed |
| QueryOperationAsync | 有限预算读原账本，unknown只查询原adapter operation，不能重发；淘汰/缺失LookupUnknown |
| QueryRunAsync | 有限预算只读冻结本地快照；缺失run返回请求身份及LookupUnknown/Quarantined快照，不默认闲置 |
| ReadEventsAsync | reader各自游标，有界metadata广播；取消只解除订阅；落后先EventGap再保留最早记录，Query补状态 |

Created从未Open时Close是Core本地操作，不调用adapter、不伪造物理关闭，返回Closed且无本session资源；Created Dispose同理。无效Open未接纳/未调adapter也适用此路径；Open已经调adapter但未知时绝不按Created无资源处理。RunId一经Arm接纳不能在同epoch重新使用（有限已用run墓碑占MetadataBytes/BatchSummaries额度；耗尽时拒绝新Arm，而不淘汰后接受旧ID）；新run原参数可复用但必须新RunId。连续批无限不等于无限run身份内存。

adapter只执行Open/Discover/Apply/Start/Trigger/Stop/Close；Arm属于Core，adapter收到应拒绝。AdapterReply/OperationReceipt的Capability仅Discover非空、Parameters仅Apply非空；Arm/Start/Trigger/Stop或有run的Close回执带Run，其余null；始终有Resources。Confirmed必须满足对应证明，缺证明转AdapterFault/Unknown；Arm Confirmed只指无设备动作的本地登记。NativeDrained是运行借用/回调已排空，ConnectionReleased是Close已释放连接句柄，不能用前者冒充后者。

AdapterReply.Activity是对原操作关联的实际源状态，不由ACK推断：Open确认须OpenIdle/连接未释放；Start确认须Acquiring；Stop确认须Stopped且InputEnded（不自动代表NativeDrained）；Close确认须Closed、NativeDrained和ConnectionReleased。Trigger确认须CommittedTriggerIndex等原请求索引且Knowledge Confirmed，仅证明该次触发已执行，不证明数据到达；其余命令该字段null。Discover/Apply需已有打开状态及相应完整能力/实际参数证明。缺任何必需证明即Unknown，不晋升状态。活动未知时新Start/Trigger一律拒绝，仅Query/原Stop清理可观察。Query证明绑定原operation/epoch，状态变化仍保原动作知识，不拿现已停止否定曾启动。

ResourceSnapshot.CountersKnowledge=Confirmed只说明本Core当前持有计数完整，不证明native已排空；Unknown时数字0只是无法测定占位，不能用于退槽。Released须CountersKnowledge Confirmed及运行任务/暂存0、InputEnded/NativeDrained；Close另要ConnectionReleased/OperationReceipt.State Closed。无已启动run时InputEnded/NativeDrained=true指无采集借用，不虚构物理停止事件。

Core给adapter的AdapterRequest在Start/Trigger/Stop/有运行的Close包含原冻结ArmedPlan及AppliedParameters，StartCommand.Run必须等ArmedPlan.Run；其它命令ArmedPlan=null，Apply请求参数在command内，Discover/Open不能带猜测实际参数。适配器据此映射真实回调到Run/Head/BatchIndex/规范化Sequence，不能依赖Simulator私有fixture才知道计划。Id/Version/Source在Create冻结，每帧Source必须相同，Replay与Vendor不得混成一批。

Software TriggerIndex从0严格递增；仅接纳下一个索引时推进有界高水位，未知也不回退，旧索引新ID仍拒绝，从而不靠无限去重字典。完全相同operation请求返回原回执。TriggerObserved的AdapterSignal.Sequence表示TriggerIndex、Run必需；帧TriggerIndex只有能证明关联才有值，未知为null，不能以ACK强配。BatchEnd必须带BatchKey且Sequence为该批最后观察序号（无数据可null）；InputEnded带Run并作用全部头；Disconnected作用epoch，Fault带稳定Error。信号身份校验错误不推进结束证明。

动作前记录operationId/epoch/kind/run/冻结request hash/phase到有界Core账本。同ID同hash查询原回执，不二发；同ID异内容OperationConflict。新ID重复Start/同Run-TriggerIndex仍StateConflict，不能绕幂等。Stop/Close同状态可观察/继续原清理，但不重新发送未知原动作。OperationRecords额度内保留活跃记录与完成墓碑，不能淘汰未知原任务；满时动作前拒绝；最老完成墓碑最终淘汰后LookupUnknown，不等于未执行。run查询近期历史同样有界，Host归档不靠Core无限历史。

总OperationRecords中永久保留2个cleanup额度（当前run原Stop及session原Close），不被业务/墓碑占用；无法同时容纳一个业务记录和两个cleanup记录时Open/Arm拒绝PA-010无动作。满业务账本仍可用原cleanup保留项，不能因队列满使Close无法登记。Query不占动作账本，但每session至多一个原adapter Query在途：并发查询合并观察同task；前一个超时未结束不发新的native查询，不让轮询无限积任务，返回原Unknown快照。CanQueryOperation=false只读Core记录、DeviceKnowledge保持Unknown，不假造adapter查询。

状态及错误优先级固定：无法表示/深冻结输入→PA-001；可表示命令先查同operation的hash（同内容返回原，异内容PA-016）→epoch不符PA-013→有在途未知设备动作/状态冲突PA-003→能力/读回/参数验证→容量→动作。拒绝不改变原会话/参数/run。Open/Start等Confirmed只说明对应动作知识；Stop/Close须资源屏障未完成时Phase仍Executing或Unknown，不把Confirmed活动证明等同Released。执行期间Budget用单调时钟，调用取消/Execution到期不抢先释放原Task；phase Unknown可随迟到证明变Confirmed，最初超时返回的不可变receipt不原地改变。

账本仅会话内，不保证重启exactly-once。跨重启宿主保留原ID/epoch/version并由设备Owner对账，不能把NotFound当未启动。持久ledger/数据库事务不在Core。

查询参数校验失败返回PA-001且不查adapter；LookupUnknown回执的RequestSha256=null、Phase/DeviceKnowledge/Resources.State均Unknown，不伪造一个请求hash。QueryRun缺失时CurrentHeads/RecentBatches为空、Resources Unknown、State Quarantined及PA-017。运行中CurrentHeads按冻结HeadPlan给每头当前批有界进度，RecentBatches仅已封口摘要；未知/晚到任务的进度更新不重写原摘要。Closed后允许本地查询保留记录，不重新Open或访问已释放adapter；墓碑超过保留额度仍明确LookupUnknown。

request hash方案更新为`pa-command-bin-v2`，合同前缀`pa-api-v0.3`；结果编码见§3.4。字段新增造成合同版本更新，旧v0.2/schema不混入本版本；PA-C1数学规则不变，但消费者需显式选择编码版本。Query的budget非法时DeviceKnowledge保留已知原记录或Unknown，不能为了报InvalidArgument丢原知识。

### 3.4 可独立重建的规范编码与结果不变量

所有编码由ProfileContractCodec实现纯同步BCL，无设备/IO。基本类型固定：枚举uint32 LE（本文各enum声明顺序从0，新增只能末尾附加）；int/int64分别有符号32/64 LE、uint/ulong分别无符号32/64 LE，bool单byte0/1；Guid为RFC4122网络16bytes（禁止默认ToByteArray混合端序）；TimeSpan为有符号ticks int64；double IEEE754 binary64 LE，拒绝非有限且-0规范+0；字符串严格UTF8无BOM，以uint32字节长前缀，拒绝NUL及未配对surrogate；nullable先byte0/1，仅1后有值；列表先uint32条数，再依序元素，空为0而非null。record struct包裹值只写Value，不写类型名；record嵌套按本页声明字段序，不复制外层prefix。集合ParameterSet.Heads/RunPlan.Heads按HeadId UTF8无符号字典序排序；Capability.Heads同排序、Formats/Encoders按Id排序、Triggers枚举排序、Planes按Role排序、InvalidCodes按Role/BitPattern/Reason排序。输入InvalidSpans按Role/Row/Start/Count/Reason排序并去完全重复，Missing按First排序合并，errors仍按首次出现输入顺序；字段重复/交错定义不能靠排序掩盖。时间/单位不通过ToString编码。

| 方案 | 顶层字节顺序（每项使用上列编码） |
|---|---|
| pa-command-bin-v2 | 方案字符串、合同字符串、Context.Epoch、kind uint32、Budget.Execution、Budget.Drain，再写命令payload。Context.Id不参与hash |
| kind payload | Open:DeviceId；Discover/Close:无；Apply:完整ParameterSet；Arm:完整RunPlan；Start:Run；Trigger:Run/TriggerIndex；Stop:Run/Reason。不能再次编码Context或继承Command字段 |
| pa-result-bin-v1 | 方案字符串、合同字符串、kind uint32（Receipt=0、Run=1、Batch=2、Event=3），然后完整对应record字段序。OperationReceipt.Id及所有实际状态必须编码，不省error/resources |
| source revision | 方案字符串pa-source-bin-v1、合同字符串、source kind uint32（Format=0/Capability=1/ParameterSet=2）、完整record字段序但省该record自己的Revision字段，保留所有嵌套Revision；先构造下层快照，最后填其hash，禁止递归自哈希 |
| pa-batch-bin-v2 / pa-profile-bin-v2 | 取代本页旧v1；具体字段顺序见§4.2，统一上述基本/排序规则及同一合同前缀，不拿result编码直接替输入内容hash |

DecodeReceipt/Run/Batch/Event在分配前校验maxBytes/maxCollectionElements>0、实际bytes≤maxBytes、每列表及累计元素≤maxCollectionElements，checked所有长度/深度；固定record结构解码无递归自由图。未知方案/合同/kind→PA-019，截断/越限/非法UTF8/枚举/null/结果不变量/尾部多余字节→PA-001；ContractDecode.Value=null/Error非空。成功Value非空/Error=null，不能返回部分合法record。Decode只生成冻结值，不触发SDK/恢复命令；InvalidArgument/UnsupportedVersion不改生产事实。Encode无效参数抛ProfileAcquisitionException(PA-001)，合法结果须可roundtrip重编码相同字节。Error.DetailKey须匹配§5.2稳定PA-nnn键，VendorCode是nullable有限字符串，不能填混合错误自由枚举；UI恢复句由键和已知上下文投影。

结果不变量：计数非负且Delivered≤Received≤Expected（允许重复仅另记diagnostic，不能膨胀Received）；Missing闭区间在期望范围，Complete时Missing空/不截断且Received=Expected。Unknown并不免除已知字段校验。LookupUnknown的RequestSha256=null、Phase/DeviceKnowledge Unknown、State Quarantined、Resources.State/CountersKnowledge Unknown；占位0不证明释放。Confirmed回执必须带相应Capability/Parameters/Run并具对应证据；资源State=Released可与设备知识Unknown并存仅在没有已启动动作时，未知Start不得因此完成run。EventGap仅该kind拥有MissingFirstEvent/LastEvent非空且first≤last，其它kind为null；BatchSealed的Summary必有且Batch等Key，其它kindSummary=null。QueryRun.Error PA-017时CurrentHeads/RecentBatches为空而身份仍是请求Run/Epoch。

固定合成编码oracle（本輪实际用BCL等价整数/UTF8/Guid编码复算字节，不是产品测试）：

- CloseCommand：Id=00000000-0000-0000-0000-000000000001（不进hash），Epoch=00000000-0000-0000-0000-000000000002，Execution=1秒/Drain=2秒，kind=7；72bytes，SHA-256=`629b3ae75e063e83560477ad5faf449d2c06b6e9ebb3c91cdde4cddeb3060790`。
- LookupUnknown receipt：上述Id/Epoch，RequestSha256=null、Phase Unknown(4)、DeviceKnowledge Unknown(1)，Capability/Parameters/Run=null；Resources=(Unknown(1),0,0,0,0,false,false,false,Unknown(1))；State Quarantined(9)，Error=(LookupUnknown(16),PA-017,null)。134bytes，SHA-256=`385c4822bbf1f268b077f04e9658cb7715c45c2793b244eadcdf84b90df4fb2a`。完整字节如下，两Host必须独立重建，不可只hash此hex冒充字段编码测试。

```text
CloseCommand:
1100000070612d636f6d6d616e642d62696e2d76320b00000070612d6170692d76302e3300000000000000000000000000000002070000008096980000000000002d310100000000
LookupUnknown receipt:
1000000070612d726573756c742d62696e2d76310b00000070612d6170692d76302e33000000000000000000000000000000000000000100000000000000000000000000000002000400000001000000000000010000000000000000000000000000000000000000000000000000010000000900000001100000000600000050412d30313700
```

## 4. 有界接收、逐条消费与结构封口

### 4.1 原始保全和租约

1. AdapterFrame.Payload及列表在TryAccept返回前由adapter保证只读稳定，返回后可重用；Core不保存其borrowed引用。回调线程仅做身份/尺寸检查、原子额度预留、复制、TryWrite；不SHA/IO/HALCON/sink或阻塞等待。
2. 复制前预留slots、实际buffer bytes及metadata；任一失败归还已取得项、Refused/PA-010。CanPauseInput=true的源只能在adapter工作线程暂停并保同一原数据/身份，有限等待后重试**尚未Copied**的数据（TryAccept回调不阻塞）；暂时Refused本身不认永久缺行，后续序号推进/结束证明或停止超时才固化缺口。不可暂停、无法保原输入或单条本就超过总预算时立即锁存缺口/受控Stop；不能无限重试。非法布局/冲突不是容量重试，不允许包装成暂时队列满。源端adapter承担未复制输入唯一Owner，Core不伪称已保全。
3. Copied只指保全成功。专用数据调度器检查布局/格式/身份/顺序/无效域/位置并计算hash；合法送完整sink。已复制非法数据经OnRejectedAsync供Host保存，不进入重建。超大/未能复制输入仅有长度/身份/原因，不伪称已保存原字节。
4. ProfileView.Metadata是深冻结副本，Metadata.Payload替换为Core保全内存；Format为该条冻结格式，合法数据必非null，未知格式Rejected可null，使下游无需隐藏查询即可解读单位/layout；Position/Invalid为Core资格检查和哨兵/非有限传播后的结果，Metadata.Position/Invalid保留原输入。最终Invalid按(role,row,start/count/reason)排序，按相同原因合并重叠/相邻段但保留不同原因；InvalidElements计最终索引并集。借用有效直到**原sink task真正完成**。Core是暂存buffer唯一释放者；sink不Dispose，不跨task保留Memory，长期数据须在task内复制到Host有界存储，或等下游全部归还才返回。
5. 每个ValueTask只转AsTask一次，Core强持原task及对应buffer，真实完成/抛错后finally Dispose。timeout/cancel/WaitAsync完成不证明原task完成；Unknown时原Owner保持buffer/原task/session，迟到完成归原Owner，不补发布原操作成功。
6. 完整流只有一个sink，逐条处理/释放；BatchSummary没有Profiles或整批租约。1000条/2slots能边消费边推进，不等封口后才读数据。任务占用已有slots，不另开无界并发。
7. BoundedChannel完整队列为Wait+非阻塞TryWrite，AllowSynchronousContinuations=false；不能DropOldest。事件ring仅metadata、无payload。Host预览在sink任务内复制至独立有界latest-wins缓冲，覆盖归还预览Owner，慢UI不能持完整租约。

OwnedBytes直到Dispose确认才扣，交sink不扣；slots、callback、consumer tasks、命令、诊断/字符串、去重/摘要/events均受Limits。TrySignal同样有界：队列满返回false并锁存固定Fault/Stop请求，不无界堆signal，也不能静默丢InputEnded当成功。每类诊断保留首次稳定Error/已知身份及计数，VendorCode截为最多128 UTF8bytes（边界不切码点），其余Error.DetailKey固定PA-nnn，不生成无限detail文本；超metadata使用预留固定PA-010快照。

OnProfile/OnRejected的协作token以该批剩余BatchDeadline及run取消为界；到期只发取消，原Task仍被强持。OnBatch通知用独立Cleanup.Execution预算，不沿用已过期批token；通知失败PA-020、不自动重发，原Task按同样规则观察。sink方法同步抛出按原调用失败记录，finally归还只有在已进入的其它借用任务全部结束后才执行。Query/事件通知与数据调度分离，卡住sink时仍能查询Unknown和资源。

MetadataBytes使用确定计费模型`pa-metadata-charge-v1`：规范编码字节数+256×record数量+64×集合预留元素数+每字符串(64+2×UTF16字符数)，所有乘加checked；共享不可变快照只计一次，但每个索引/ring引用仍计元素reservation。集合按声明上限预留，禁止无界capacity增长；账本、摘要、信号、plane/span、错误及字符串均计费，即便buffer可租也不能越metadata预算。该保守软件计费不是精确GC对象大小，benchmark另量真实托管分配/峰值RSS及差异，不能把模型值当实测内存。port租用/复制异常在返回前归还已取得buffer和额度；归还异常保留Owner转Unknown。TryAccept未复制完绝不Copied；无法安全确定BatchKey时只记录epoch固定错误，不向合法批分配虚构身份。

### 4.2 序号、批次与封口

Sequence为adapter已规范化的非回绕ulong，保留RawSequence/RawSequenceBits（1..64）；未经证明的原窄计数回绕不得猜多圈。BatchKey=(Run,Head,Index)，index从0；期望首号=checked FirstSequence+Index×ProfilesPerBatch，尾号=checked first+count-1。Single各头一批，Continuous可在运行中逐批封口，无需停止整个run；相同index不证明多头同步。

每头一个当前批；未来批到达先封当前已知缺口；跳过大量批不得生成无限空摘要，应记录跳跃并受metadata限制。同批允许递增且有缺口；迟到逆序本版不重排，不补已封口。近期去重窗口保存payload+metadata内容hash：完全重复仅计诊断、只输送一次；同序号异内容隔离且受控停。超窗口旧序号无法证明同内容，SequenceGap/Unknown，不凭序号吞掉。错头/run/epoch/format不增加合法计数、不拼其它批。

批0的BatchDeadline及MaxRunDuration从Start接纳的单调时刻开始（未知开始也有有限观察）；后续批deadline从上一批封口时刻开始，不能不断被新帧续期。运行时限/MaxBatches到达禁止新输入并发起原Stop，等待实际停止证明，不将计划计数当设备已停。每头只保留当前批进度；完成run历史快照与摘要共用BatchSummaries/MetadataBytes额度，未排空run不能淘汰或创建替代run。

封口触发：收齐期望范围、BatchEnd、InputEnded、Stop后已确认输入静默或BatchDeadline。先经过本批已接纳校验/输送屏障，再冻结摘要。**不等整个run native/连接排空才封口**。摘要Query可见，OnBatch串行通知；连续运行接下一批。源确认结束且缺行/拒绝→Incomplete；尾部不明/冲突使完整性不可证明→Unknown；全部期望且无结构冲突→Complete。有效计划空源确认结束为Incomplete/缺全区间，未知结束为Unknown；非法空计划在接纳前拒绝，不造Empty=成功。

若原sink task卡住到BatchDeadline，由状态调度器冻结Unknown摘要/BatchSealed metadata；OnBatch仍等原数据task完成后通知，禁止并发重用其buffer。迟到交付的资源/计数进RunSnapshot诊断，不改写已冻结摘要/hash，不把原Unknown升级成功。Stopped/RunCompleted仍必须等所有原task/通知完成。

Missing是闭区间、按原索引排序合并；超MissingRanges/MetadataBytes→MissingDetailsTruncated=true、Structure Unknown、受控停。Received为不同合法序号数，Delivered为原OnProfile任务成功数，失败不当保存成功。RecentBatches只保留BatchSummaries额度；历史被淘汰应明确不可查询，Host独立保存，不无限缓存。

无效、位置、结构、排空正交：100条全收到但全哨兵仍Structure Complete，InvalidElements=全部对应元素，Position可Unknown；不能把噪声当缺行。source/能力/参数/标定/格式在批内不可变。

BatchSummary.Position仅在本批所有合法收到轮廓的核验位置均Observed且frame/标定/segment兼容时Observed，否则Unknown；空批必Unknown，不能以空集合全真提升位置。它不证明未收到行位置，不等于规则网格或完整测量。InvalidElements按plane元素索引并集计数，多plane允许因此大于SampleCount，不将强度invalid自动传播成高度invalid；域间传播须设备格式明确声明，本版不猜。

ProfileView.ContentSha256方案`pa-profile-bin-v2`精确顺序：方案字符串、合同字符串、Metadata.Batch.Head、Batch.Index、Metadata.Sequence、RawSequence、RawSequenceBits、TriggerIndex、SampleCount、完整FormatSpec、Planes列表、PayloadSha256字符串、Metadata.Invalid原列表、ProfileView.Invalid核验列表、Metadata.Position、核验Position、SampleTime。PayloadSha256为原Payload全字节SHA256（包括padding），不转数值、不将原浮点-0规范化；只有metadata double按§3.4规范。排除Run/epoch/source/ReceiveTimestamp/LeaseId/任务状态；Content相同不证明同生产来源。未校验格式Rejected只保PayloadSha256，ContentSha256为空标“未计算”；合法Profile两个hash为64小写hex。

batch hash `pa-batch-bin-v2`精确顺序：方案字符串、合同字符串、BatchKey、FirstSequence、Expected(uint32)、完整FormatSpec、完整Actual ParameterSet、Capability.Revision、Actual.Calibration(nullable)、source枚举；每个成功校验并尝试完整输送的原条目增量追加tag byte1、Sequence、ContentSha256字符串；封口追加tag byte0、Structure、Received、Delivered、InvalidElements、Missing列表、MissingDetailsTruncated、Position资格、Errors列表。无需先存整批或预先写profile数；tag0/1区分流结尾。Error列表只含首次错误及稳定顺序（按本批复制接纳次序，各类别只保首次；同回调并发由短锁分配接纳序），批摘要不记录重复日志时刻。原合法条目若sink失败仍已写hash条目，Delivered较低。Deadline Unknown封口后迟到只改run资源快照，不重写hash；所有字段按§3.4确定排序。相同source/原身份/快照/受控故障时序可复算；live改Replay或new run只比内容hash/结构，不要求BatchSha相同。

### 4.3 位置与时钟证据

Encoder差按模2^Bits取唯一落在(-半模数,半模数)的有符号步进，须≤MaxStep，反向须SupportsReverse。等半模数、超MaxStep、多圈可能或reset无Segment→PositionUnknown。累计用checked Int128，初始计数取首RawCount；Y=OffsetMm+Sign×累计count×MmPerCount，转换结果须finite。明确reset新Segment才重取原点，不能当回绕。

ActualYMm来自设备实际标定位置或已证明编码器换算；CommandYMm单独保留，CommandOnly不提升Observed。标定/frame/encoder不匹配Unknown。Core仅给Observed/Unknown，不输出RegularGrid/XYZ；网格资格、X几何/间距容差及高度场由重建/表面Owner判定，不从0/1/3 mm造0/1/2 mm。已有设备实际值与编码器换算并存不一致时保留两来源诊断，未有Profile容差则Unknown，不自行选一个。

采样原ticks/frequency/domain/boot epoch保留；已证明clock mapping时宽整数转换ns向零取整，误差含量化；超long范围保持ns=null/诊断。不同domain/boot epoch无映射不相减；接收clock只测软件延迟。跨头同步需设备Profile时钟映射/error bound及同步来源，由消费者证明，不能凭回调先后同步。温漂/低强度只是诊断，不学习阈值。

### 4.4 线扫2D/3D逐行、标量解码与厂商块桥

本节是原采集能力的确定拆行/解释补充，不替换已接收会话、位置公式或框架，不增加SDK工程。类型在Core同namespace，Pure类无设备/IO；其调用者为设备Owner的现有bridge、Replay/Simulator及两个Host。下列同样是待实现签名规格，静态/类方法需补方法体，不是现有产品源码。

```csharp
namespace Asun.Modules.ProfileAcquisition;
public sealed record ScanRowStamp(BatchKey Batch, ulong Sequence, ulong RawSequence,
    int RawSequenceBits, ulong? TriggerIndex, PositionObservation Position,
    TimeObservation? SampleTime, IReadOnlyList<InvalidSpan> Invalid);
public sealed record BorrowedScanBlock(Guid SourceBlockId, Epoch Epoch, SourceKind Source,
    string FormatId, int Width, IReadOnlyList<PlaneLayout> BlockPlanes,
    ReadOnlyMemory<byte> Payload, IReadOnlyList<ScanRowStamp> Rows);
public sealed record ScanSlice(AdapterFrame? Frame, Error? Error);
public enum ElementValidity { Valid, Invalid }
public sealed record ProfileElement(string Role, int Row, int Column, ScalarKind Scalar,
    ulong RawBits, ElementValidity Validity, double? Value, string Unit,
    IReadOnlyList<InvalidReason> Reasons);
public sealed record ElementDecode(ProfileElement? Element, Error? Error);
public static class ProfileRowDecoder
{
    public static IReadOnlyList<ValidationIssue> ValidateBlock(BorrowedScanBlock block,
        FormatSpec rowFormat, int maxRows, int maxBlockBytes, int maxMetadataBytes);
    public static ScanSlice SliceBorrowed(BorrowedScanBlock block,
        FormatSpec rowFormat, int rowIndex);
    public static int GetPackedRowBytes(BorrowedScanBlock block,
        FormatSpec rowFormat, int rowIndex);
    public static ScanSlice PackBorrowedRow(BorrowedScanBlock block,
        FormatSpec rowFormat, int rowIndex, Memory<byte> destination);
    public static ElementDecode ReadElement(ProfileView borrowed, string role,
        int row, int column);
}
```

**块与profile image不能靠Rows数量猜模态**：BorrowedScanBlock仅表示多个Line格式逐行的传输聚块；FormatSpec每plane.Kind须Line/MaxRows=1，block各plane.Rows等Rows.Count、Columns=Width。一个激光线相机image可有多pixel行，但它作为一个AdapterFrame/一次轮廓观测，plane.Kind=Image，交重建模块按§2.1提取，不能把pixel行当机械扫描行。2D线扫强度Line也是一条观测；没有高度就使用RawCode主plane及强度单位说明，不造Z。2D影像聚成二维画面是相机/图像/viewport消费者职责，位置化3D表面是重建/表面职责，Core仅保原线序。

ValidateBlock在零拷贝**借用期间**检查SourceBlockId非Empty、epoch/source/FormatId匹配、1≤Rows.Count≤maxRows、payload≤maxBlockBytes、metadata按§4.1计费≤maxMetadataBytes；plane角色/标量/端序与rowFormat一致、长度与包围区间checked且不重叠。Rows每项提供真实Batch/Sequence/原窄计数位宽/位置/时间；整块只有最后时间戳、平均encoder或命令Y时不复制为逐行实际值，缺逐行证据按Unknown/null标明。Rows来源必须与SDK公开格式相符，不做未经证明的first+i推导；均匀序号公式只有厂商Profile明确“连续N行且无丢行”时才能由bridge生成，仍保原块和原首号在设备Owner来源证据。跨batch块各row保自己的BatchKey，逐条依§4.2封口，不整块拼表面；头错配/计数回绕未证明时拒绝映射。

maxRows/maxBlockBytes/maxMetadataBytes均显式正数；ValidateBlock返回空列表才合法，不取得资源。Slice/GetPackedRowBytes/Pack没有预算参数，只执行同一结构/字段/checked跨度校验，不代替调用者的预算准入；bridge必须先ValidateBlock并保原块及metadata只读，不能以这些方法的成功暗示资源合格。row stamp.Invalid的Row必须为0、Role/Start/Count在该行格式域内；输出复制stamp字段，Frame.Epoch/Source/FormatId取block、Batch/Sequence/RawSequence/TriggerIndex/Position/SampleTime取stamp。所有元数据输出在调用者已预留额度中创建冻结副本，payload仍按借用规则，不创建隐含缓存。

SliceBorrowed纯计算且不复制：先通过上述块校验，rowIndex∈[0,Rows.Count)；对每plane计算offset=checked(block.Offset+rowIndex×RowStride)、rowSpan=(Width-1)×PixelStride+scalarBytes；该行帧Payload仍借整个block（不先拼新buffer），Planes=同role/新offset/Rows=1/Columns=Width/原stride/scalar/order，SampleCount=Width，Invalid使用该row stamp已归一到Row=0的段。因Payload仍是整块，Core复制不得将巨块误当单条。bridge必须在TryAccept前将各行plane按Role顺序打包到一个**有界行暂存**：每plane保本行原pixel stride间padding、复制rowSpan字节并重设offset，rowStride=rowSpan；行末及块间padding不代表样本，只留在设备Owner原块归档，不伪称行Payload仍含全部块字节。这个打包仅数据搬运/端序保全，不改数值，允许公共共享allocator；本版不提供跨SDK块的隐式零拷贝lease。

GetPackedRowBytes返回checked各plane rowSpan之和，非法块/row抛ProfileAcquisitionException相应错误；PackBorrowedRow要求destination.Length恰等该值且≤rowFormat.MaxPayloadBytes、与源Payload不重叠，否则ScanSlice(null,PA-001/006)，绝不部分成功。按Role UTF8排序连续复制rowSpan（含本行pixel padding）到destination，Frame.Payload只引用destination、rows=1及更新offset/stride，调用后是destination Owner借用而非新租约。源任一非法在写前拒绝，算法不持跨调用引用；打包scratch由bridge Root分配/归还，不由Core TryAccept返还。SliceBorrowed不经Pack不能直接送TryAccept，避免整块大payload被误复制为每行。

bridge唯一循环为：Root先预留最大原块+一个行暂存+Core已持有额度→原producer/reader Task立即登记→取得原块租约且校验→for每原row计算Slice→有界Pack→TryAccept→Copied后才能重用行暂存/推进row；Refused容量且source能保原块时按原deadline暂停有限重试同row，不能读下一块覆写；非法/不可保源缺口受控Stop。直到所有row已Copied/拒绝已留明确证据、原复制回调返回，才由**原producer Owner**归还原块。取消/超时中途仍保原块/reader/行暂存/已Copied Core租约各自Owner，reader晚到由同Root归还，Close不将reader等待结束当资源结束。最大native块超过显式maxBlockBytes在复制/分配前拒绝或要求设备支持分块，不以“超大批”扩大预算；100万行批仍流式而不保100万行stamp列表，单块Rows上限独立固定。不存在通用软件可以保证任意无反压高线率完整收齐，硬件持续输入与Host资源不符明确Incomplete/Unknown。

ReadElement在borrowed原任务有效期内校验Format非null及布局/索引，按ScalarKind和ByteOrder用BCL BinaryPrimitives读取RawBits；I16/I32做有符号解释，F32/F64用位级转换，U32精确转double（本版不支持64-bit scalar，避免无声明精度损失）。先按ProfileView.Invalid及InvalidCodes/非finite判断：Invalid结果Value=null、Reasons按enum顺序去重，不把NaN/哨兵解为0；Valid才计算double值=decoded×Scale+Offset，结果非finite时PA-006且不返回伪有限值。RawBits保原bit pattern（负I16只保低16位原码，例-1=65535），Unit取该plane.Unit。ReadElement不修改payload、不滤波/插值、不执行物理坐标变换，位置与scalar单位分别携带。超索引/未知role/Disposed借用属于Host违约，入口PA-001；结果Element非空/Error=null或Element=null/Error非空。由于公共Memory本身不可证明仍有lease，Host必须守原Task借用边界，不能指望解码函数检测已归还内存。

| 原设备事实 | 通用字段映射与责任 |
|---|---|
| 宽度/行数、高度16/32位、强度8/16位、线宽/无效码 | 设备Owner声明FormatSpec/planes；保原位宽（不能把16位源人为写成32位后假称原字节），逐行stamp+§4.4打包；Height16 Scale/Origin显式写plane.Scale/Offset，已标定高度Unit=mm及Calibration引用 |
| encoder array、timestamp array、reset/clock域 | 数组长度须等原Rows.Count，每row分别映射RawCount/Segment和RawTicks/frequency/domain/boot；无frequency时SampleTime=null，原ticks/域保在设备Owner证据，不填frequency=0；有frequency无映射时Nanoseconds/ErrorBoundNs=null，不用DateTime AcquiredAt当逐行采样时间；stop/回调时间只是软件观测 |
| XOrigin/XResolution、YOrigin/YResolution/标定 | X几何不在本模块API复制第二套标定：冻结Calibration引用由重建/坐标Owner解引用；真实Y来自逐行encoder/actual，不用YResolution×row下标替实际位置。缺标定只保raw，禁止输出校准表面 |
| NativeFrameLoss/TransportDrops、QualityFlags/通知 | 设备Owner将真实丢行转原Sequence跳跃/InputEnded证据，已知坏样本转InvalidSpan具体原因；无法定位质量标志映射AdapterSignal Fault/PA-014并保原码（不把裸flag当产品质量）。正常通知不是PASS；噪声/invalid与结构Completeness仍正交 |
| 厂商batch/head/device及native租约 | 厂商Owner建明确identity映射到当前Run/Head/BatchKey并绑定epoch，保厂商原身份在其证据快照；IM-063 ProfileBridge实现本页端口，不由产品页面或本模块再开SR设备连接 |

本表冻结消费方向、数据字段与拒绝条件；具体SDK公开类型、原计数单位/无效值/时钟频率来自设备Profile，未提供时只阻断live桥/物理资格，不要求编码者猜。参考DeepSight公共FrameLease已读字段仅作迁移证据，不能假定新IM-063端口与旧对象同类型；本模块不读取或改变其内部。

## 5. 状态、事件与错误恢复

### 5.1 偏序及正交资源

正常：Created→Open→Ready→Configured→Armed→Running→StopRequested→Draining→Stopped。Stopped且运行资源Released可Apply/Arm新run；Close还需ConnectionReleased才Closed。Unknown/断连进入Quarantined或Draining/Unknown，可Query/继续原清理，不能直接Ready或复用同物理资源。没有run时Resources Released只指无数据借用，不证明连接已关闭。

```text
SessionOpened → CapabilityRead → ParametersRead → RunArmed
 → StartRequested → AcquisitionStarted | StartUnknown
 → TriggerRequested* / TriggerObserved* / ProfileReceived* / ProfileRejected*
 → BatchSealed*（连续运行可继续下一批）
StopRequested → AcquisitionStopped（实际源停止证明）
 → InputEnded + callbacks/native借用排空 + 原sink任务/通知完成 + buffers归还
 → ResourcesReleased → RunCompleted
Close + ConnectionReleased + 上述屏障 → SessionClosed
```

BatchSealed可早于Stop，但RunCompleted晚于所有封口及ResourcesReleased。Armed未启动本地结束，不虚构设备停止。DrainUnknown不发ResourcesReleased/RunCompleted/SessionClosed。EventSequence为checked单调ulong，溢出前受控停；事件含适用epoch/run/batch/operation，纯会话Run/Batch=null。ring reader落后EventGap+Query；不是payload归档总线。

ProfileEvent.Sequence是事件游标，ProfileSequence是原轮廓序号，TriggerIndex是已知触发关联，三者不混用；纯会话字段为null。MonotonicTimestamp来自注入TimeProvider，只作本会话阶段时间，SampleTime只在有源证据时填写；Source/AdapterVersion取冻结端口身份。EventGap的Sequence为跳失后的保留边界，Error PA-018指出遗漏游标范围，不能冒充补发所有事件。

每session同时event reader上限为EventRecords（作为现有limit的第二用途，不增无限订阅）；每reader至多一个MoveNext在途并计MetadataBytes，无payload。afterSequence大于当前末游标抛PA-001；0从已保留首条开始，落后最早保留游标n时合成EventGap的Sequence=n-1、MissingFirstEvent=after+1/MissingLastEvent=n-1（不追加ring、不改变全局序）；随后发n。末游标已读且session未Closed等待有限调用方token；Close后按游标读完保留项再自然结束。枚举取消/DisposeAsync先注销读者、完成或观察原MoveNext，再扣订阅元数据；未完成借用任务不能假归还。reader Gap字段是数值而非仅DetailKey字符串，允许宿主无需解析文案补Query。

### 5.2 错误键与下一动作

| ErrorCode / 稳定键 | 事实与恢复 |
|---|---|
| InvalidArgument PA-001；CapabilityUnavailable PA-002 | 接纳前拒绝/无动作；改请求或重新发现真实能力，不默认 |
| StateConflict PA-003；ConfigurationPartial PA-004 | Query/读逐项实际值，完全读回前不启动 |
| TriggerUnknown PA-005 | 查原operation/run/trigger，不另发替代 |
| LayoutInvalid PA-006；SequenceGap PA-007；HeadBatchMismatch PA-008 | 隔离原件/缺口，受影响批非完整，不填洞/拼接 |
| PositionUnknown PA-009 | 可保存原件，不能当已标定网格 |
| Backpressure PA-010 | 固定缺口/水位，停止新输入；新计划调整负载/保存端 |
| Cancelled PA-011；Timeout PA-012 | 原动作仍保留，独立cleanup，不当已停 |
| StaleEpoch PA-013；AdapterFault PA-014 | 旧数据归原Owner、不推进新run；保留VendorCode |
| ResourceDrainUnknown PA-015 | 强持原Task/资源/Owner，Query或设备Owner恢复，禁复用 |
| OperationConflict PA-016；LookupUnknown PA-017 | ID异内容拒绝；淘汰/重启未知不认未执行 |
| EventGap PA-018；UnsupportedVersion PA-019 | Query补投影；旧格式只读或拒绝，不静默迁移 |
| ConsumerFault PA-020 | Received/Delivered分开，停止新输入，不把保存失败当完成 |

DetailKey为资源键及受限参数，UI不显示裸SDK堆栈。命令结束、设备知识、资源归还不是一个bool。Error的VendorCode只是来源诊断，不改变本模块错误分类。

## 6. 取消、超时、关闭与原Owner

命令状态调度器串行设备写入；Query并行只读冻结快照；ingress多callback短锁有界预留，数据调度器串行输送。Core不Wait/Result阻塞UI，不要求Dispatcher。未知原adapter任务尚未结束时不并发发送Stop/Close，先协作取消/Query原task；native并发停机能力只由设备Owner已批准Profile定义，Core不猜。

Adapter ExecuteAsync/QueryAsync必须同步部分短返回，SDK等待留其已定义worker，不能调用到ValueTask返回前阻塞宿主。Core接纳后捕获port同步异常为原operation Unknown/AdapterFault并保持Owner，不能当动作未发生；关闭链先记录原状态再调port。Core不依赖强杀托管线程恢复。迟到task若仍未完成，Query不能仅凭一个ACK宣称资源释放，必须同时满足原task与释放屏障。

接纳前取消Rejected/Cancelled、无动作；接纳后锁存取消/禁止新触发并发起一次原run停止。Execution超时返回Timeout/Unknown当前回执，后台继续强持/观察原Task，不释放设备写入锁。cleanup用独立有限token与Budget.Drain，不继承已取消业务token。迟到adapter结果更新原operation知识/资源，不把超时原调用改成成功。

释放屏障：源InputEnded；已进入TryAccept的callbacks全返回；所有复制/校验/原sink及OnBatch通知tasks真正完成；buffer Dispose确认；adapter NativeDrained确认其在途native队列/借用。writer Complete不证明排空。Close额外确认ConnectionReleased。Dispose异常资源未确认不扣账，保留原Owner查询。

IAsyncDisposable.DisposeAsync无返回值：发起/复用原Close，按SessionOptions.Cleanup有限观察；释放完成返回，否则抛ProfileAcquisitionException(PA-015)，内部观察及原Task/buffer仍保留，可继续Query，不假装Disposed。重复Dispose复用同清理而不再动作。Host应显式Close后检查receipt，不靠await using掩盖Unknown。

Host finally独立业务token，有界观察原Stop/Close Task；WaitAsync超时不能抛弃底层task。未知/异常转Host RecoveryOwner强引用槽（session、adapter、sink、原task），槽有界且满时禁新会话。原task迟到后归原Owner，Query证实Released才移出隔离。设备隔离/进程重启归设备Owner；进程结束不证明设备停，不自动运动/发光/重采。

## 7. 两个无UI消费者最小闭包

### 7.1 Factory前的进程Root及任务记录

两个Host仅Core+BCL；测试工程实现DeterministicSensor、ManualTimeProvider、ArchiveSink、InspectorSink及下述进程Root，均为Host内部夹具，不新增Core/恢复库API。--host archive与--host inspect共用同一生命周期实现。Root为进程静态强引用容器，无设备/产品全局事实；它只持有尚未确认释放的Host资源。

在任何Factory/adapter/sink构造**之前**，Root在一个短锁内预留会话条数、Host字节及原Task slots；失败不构造、不IO、不发命令。预留包含Core OwnedBytes/Metadata计费、Host归档/预览/异常/任务记录额度及固定安全余量，checked总量；模拟Host上限明确为2个session槽、每槽Host自有数据最多1 MiB、每槽32个原Task records，Root总字节上限按两个完整已冻结profile reservation求和；现场Host值来自Profile而非沿用模拟值。保留有四个保底task slots（Stop、Close、Query、Dispose），业务不能占用；满时停止创建业务任务，使用保底cleanup，不删未知record腾位。

模拟Host的SessionReservation=checked(Core.OwnedBytes+Core.MetadataBytes+1 MiB Host数据+512×TaskSlots+64 KiB Host元数据)，§7.3每槽2,179,200bytes、两个槽Root总4,358,400bytes。Host归档和Inspector preview/统计合占数据预算1 MiB，错误/CTS/移交包/墓碑采用64 KiB有界metadata及同计费规则；引用共享对象只在唯一归还Owner处计实际bytes，接收预留是保守双reservation直到Accepted，不能因“只复制引用”零预留。该模型不是RSS限值，实际托管分配/RSS另测；不足以容纳某夹具时动作前拒绝，不临时加预算。

每槽包含session/adapter/buffers/sink、Profile及epoch/run、所有冻结CommandContext/Command及request hash、Task种类及原Task、最近receipt/ResourceSnapshot、错误消费状态、当前Owner和handoff token。**先**预留record并冻结身份，**再**调用一次委托；原ValueTask立即AsTask一次存record，**然后**才允许await/通知。同步抛出也写该record，未知动作保留Owner；无返回Factory要求无IO、无后台任务/资源，能证明此前只构造纯托管对象才释放空槽。若构造违反无后台资源承诺或已有对象有未归还任务，保持隔离，不将“没有session返回”视作无资源。

Task record容量包括聚合父Task及其所有子Task，不把RecordDrive/RecordReconcile隐藏任务当一个slot；串行子任务完成、result/fault已消费且其局部借用归还后，可将record折叠为有界诊断墓碑并复用slot，未知/未消费或仍有borrower的record不得回收。Close/Dispose record一直保留至session槽退役，不因其wrapper完成回收；完成查询所得到的Unknown快照仍保在session槽，不能把query Task已完成认作底层已释放。命令历史由Core有界账本查询，Root不额外保存无限已完成Task列表。调用委托返回前同步阻塞违反§6/§8端口短返回契约；wall watchdog将该Host判失败，绝不解除原Root，不能强杀托管线程后声称无资源。

有限观察使用真实Stopwatch的绝对截止点+Task.WhenAny(original,独立wall timer)；只等待observer，不await未完成original。完成后GetAwaiter().GetResult读取并消费result/fault，Task fault仅表示任务故障，**不证明**Resources Released。wall到期锁存失败/Unknown、协作cancel、保留original，不重新Execute/Dispose、不只保存WaitAsync包装Task。Execute、Drive（含子Trigger）、Stop、Close、QueryOperation/QueryRun、事件projection及Dispose一律经过该登记函数；Drive进入前还要预留所有最大在途子Task额度，不能隐藏直接await查询/触发。有限轮询共用绝对截止点，不能每轮续期。

以下是Host内部**可实施动作伪代码**（Root/Record/Observe为本测试工程局部函数；未声明成新模块API）。两Host只替换sink，原Core API未变：

```csharp
var slot = processRoot.TryReserve(profile.SessionReservation, profile.TaskSlots);
if (slot is null) return HostFailure.Capacity; // Factory前，无任何资源或动作
bool succeeded = false;
try
{
    // 仅纯托管构造；每得到一个对象立即绑定Root。构造发生同步异常也留失败记录。
    slot.Buffers = ProfileAcquisitionFactory.CreateManagedBuffers(profile.Limits.OwnedBytes);
    slot.Sink = archiveMode ? new ArchiveSink(profile) : new InspectorSink(profile);
    slot.Adapter = new DeterministicSensor(fixture);
    slot.Session = ProfileAcquisitionFactory.Create(slot.Adapter, slot.Buffers, slot.Sink,
        new SessionOptions(profile.Limits, profile.Cleanup), clock);
    slot.Epoch = slot.Session.Epoch;
    // Record先占Task槽/保存Command，立即保存委托返回的original Task，再有限观察。
    var opened = await Observe(RecordExecute(slot, new OpenCommand(C("open"), fixture.DeviceId), ct),
                               businessWallDeadline);
    RequireConfirmed(opened);
    var cap = await Observe(RecordExecute(slot, new DiscoverCommand(C("discover")), ct),
                            businessWallDeadline);
    RequireConfirmed(cap);
    RequireEmpty(ProfileAcquisitionFactory.Validate(parameters, cap.Capability!));
    var applied = await Observe(RecordExecute(slot, new ApplyCommand(C("apply"), parameters), ct),
                                businessWallDeadline);
    RequireReadback(applied.Parameters);
    RequireEmpty(ProfileAcquisitionFactory.Validate(plan, applied.Parameters!));
    RequireConfirmed(await Observe(RecordExecute(slot, new ArmCommand(C("arm"), plan), ct),
                                   businessWallDeadline));
    RequireConfirmed(await Observe(RecordExecute(slot, new StartCommand(C("start"), plan.Run), ct),
                                   businessWallDeadline));
    await Observe(RecordDrive(slot, plan, ct), businessWallDeadline);
    // RecordDrive内部Trigger/Query也先登记original，再有限观察；不等事件枚举结束。
    var stopToken = RecordCleanupToken(slot, IndependentCleanupToken(profile));
    var stopped = await Observe(RecordExecute(slot,
        new StopCommand(C("stop"), plan.Run, StopReason.Completed), stopToken.Token),
        cleanupWallDeadline);
    RequireReleased(stopped);
    succeeded = true;
}
catch (Exception error) { slot.ConsumeAndKeepFailure(error); }
finally
{
    try
    {
        if (slot.Session is not null)
        {
            var closeToken = RecordCleanupToken(slot, IndependentCleanupToken(profile)); // 不用业务ct
            var closeRecord = GetOrRecordOriginalClose(slot, C("close"), closeToken.Token);
            await Observe(closeRecord, cleanupWallDeadline);
        }
    }
    catch (Exception error) { slot.ConsumeAndKeepFailure(error); }
    finally
    {
        try
        {
            if (slot.Session is not null)
            {
                // query原operation/run；每个original query先记录再有限观察。
                await Observe(RecordReconcileQueries(slot,
                    RecordCleanupToken(slot, IndependentCleanupToken(profile))),
                              finalWallDeadline);
                if (slot.HasConfirmedClosedAndReleased)
                {
                    // 先预留记录，再仅调用一次DisposeAsync().AsTask；保存original Dispose Task。
                    var disposeRecord = GetOrRecordOriginalDispose(slot);
                    await Observe(disposeRecord, finalWallDeadline);
                }
            }
        }
        catch (Exception error) { slot.ConsumeAndKeepFailure(error); }
        finally
        {
            // 不await无界transfer；接收方先预留完整容量并确认Root引用，再变更Owner。
            TryTransferOrKeepOriginalRoot(slot);
            // 只有§7.2全部屏障满足才退槽；拒绝/故障/通知失败仍留原Root。
            TryRetireConfirmedSlot(slot);
        }
    }
}
var completion = FreezeCompletionBeforeClearingReferences(slot, succeeded);
return completion.Succeeded && completion.ErrorsConsumed && completion.Retired
       && !completion.HadAnyFailure ? 0 : 1;
```

C冻结非空ID/epoch/显式预算，重试原命令用原ID；GetOrRecordOriginalClose/Dispose在槽锁下返回既有record，不重新发起。cleanup/finalWallDeadline均为已冻结case的绝对墙钟点（正常模拟每次观察至多1秒、case总10秒），不是每个catch延长；期限耗尽仍可同步登记/发起一次合法原cleanup并保Root，由后台有限tick观察，但不能再无限等待。Query结果未知不调用Dispose制造假闭合；已开始Dispose未知时始终保留那一个原Task，不二发。工厂失败无session返回：确认无IO/后台/任务、各纯托管对象无借用，消费错误后释放空槽，退出仍失败非0。

返回码用退槽前冻结的HostCompletion记录（Succeeded、ErrorsConsumed、Retired、HadAnyFailure），退槽清引用不得清这四个标志而丢错误。IndependentCleanupToken生成的CTS及其原token也绑定record，取消/计时到期后仍保到对应Task真实结束再Dispose；RecordReconcile负责依次登记QueryOperation/QueryRun叶Task并保聚合Task，不留下未登记的异步lambda。§7.1伪代码的每个Record/观察调用都先检查剩余reserved slots，不足则不发新查询/命令、保槽并失败；cleanup保底slot若被未知原cleanup占用，只观察同一record，不再另起任务绕上限。

RecordDrive终止条件：目标sink闩锁完成且必需batch摘要已接收，或任一原run明确错误/业务token取消/绝对业务wall deadline；Software在此前只发严格下一TriggerIndex，TriggerUnknown即停发并对账，不能发后一索引绕未知。FreeRun/Encoder/External本模拟Host不生成伪触发，只等源夹具；每次有限QueryRun返回PA-017/资源Unknown时不当结束成功。真实生产节拍由设备Profile另验。迟到batch OnBatch成功不能抹掉已冻结timeout错误。

### 7.2 两消费者、移交与退槽屏障

| Host | 数据动作/原资源 | 正常及失败链 |
|---|---|---|
| Archive | OnProfile任务内复制payload/metadata到Host有界归档（模拟最多1 MiB），保存完成才返回；OnRejected保存已有保全数据，OnBatch保存摘要 | 每个原写入task在Core和Host sink进度Owner都有引用；保存故障与cleanup故障分别消费，Delivered不计失败。全链执行§7.1嵌套finally，异常不得覆盖成0 |
| Inspector | OnProfile内统计原码/invalid并复制指定一条preview到独立有界暂存，不跨task保存Core Memory | 预览退出不终止完整采集；业务、Close/Query/Dispose未知或失败均保同Root；原任务晚到只归原Owner、不重做run |

移交动作顺序冻结为：原槽标记TransferPending并保全部引用→接收Root按**完整**条数/bytes/任务/资源包预留（不能只接session）→接收槽复制强引用及原身份/状态、校验包epoch/run与Task引用相同→在双方短锁下写同handoff token的Accepted确认→原Owner收到确认且接收槽可检索，才解除原槽资源强持/切换Owner。通知/确认丢失时双方可同时强持，但原Owner继续持有并按token查询接收方，不能将发送视作接收。拒绝、接收满、同步异常、通知失败、身份不符、token未确认均原Root保槽并禁新session；禁止关线程/丢局部变量当移交。Root容器继续持有原对象，不要求所有进程都实现另一恢复服务；单进程默认直接保原Root。

退槽需同时满足：所有已取得original Tasks完成且其result/fault已读取消费（包括Drive子Task、event projection、sink原借用、Close、Query、Dispose）；所有tracked错误已记录消费；最近有限Query证明资源Released/NativeDrained、连接ConnectionReleased、状态Closed；Host sink/preview/file借用已结束、缓冲实际归还及计账为0；同一原Dispose Task成功完成；无未确认handoff。Faulted Dispose即便Task完成也不能据此满足释放屏障，QueryUnknown不得退槽；已确认资源释放但Dispose任务故障也保故障槽待Owner处理，不再次Dispose。接收Owner确认移交只是改变强持责任，不把未释放资源当归还或把Host退出改为0。

Dispose原Task已Faulted时有限Root扫描先消费故障，再Query原Close并独立核对已持有对象/缓冲账、所有原tasks结束、资源CountersKnowledge Confirmed/Released/ConnectionReleased/State Closed。只有这些独立证明全满足，原Owner可将槽标记ReleasedWithFailure、冻结HadAnyFailure=true、记原fault处置后退槽；该分支不是“Task fault证明释放”，绝不再Dispose/重发Close。任何证明不足仍保槽。Host退出非0不变，测试分别断言资源安全退槽与业务失败。这样已证明无资源的纯托管故障不永久占槽，真实未知不能以文档裁决清掉。

移交双方锁按Root生成的单调内部RootId排序获取（编号仅进程内锁序、不充当设备epoch），两锁内先确认整个包引用已绑定，再原子写Accepted token和唯一归还Owner；不在锁内通知/await。原Owner在Accepted未被自身观察前只保引用、不再执行归还；接收方也只有token指定Owner可Dispose/退槽，防确认丢失导致double-return。失败前未写Accepted则原Owner仍唯一；接收预留空槽可释放，但不清原Root。

Root对迟到task安装一次有限工作量完成通知，读取result/fault进原record；通知抛错保record并由Root下一tick有限扫描补读取，不删除。每tick有上限，未完成只保留，不busy spin、不自动重发设备动作。完整sink多子任务原父Task强持全部子Task，一个失败后仍观察其它borrower真实结束。两个Host各自Simulator独立，同物理run由一个复合sink消费，不创建双设备Owner。

### 7.3 最小合成Profile及端口闭包

PA-T01/08的共用夹具按以下明确值构造所有必需输入，不依赖设备默认；这些值仅软件反例，不能迁为客户阈值：

- ResourceLimits：BufferedProfiles=2、OwnedBytes=128、MetadataBytes=1,048,576、MissingRanges=8、RecentSequences=16、EventRecords=64、OperationRecords=64、BatchSummaries=8；CreateManagedBuffers同128bytes上限。Budget Execution=1秒/Drain=1秒、Cleanup同预算；BatchDeadline=2秒、MaxRunDuration=4秒，均虚拟时间，case真实watchdog仍10秒。
- Capability：DeviceId=sim-device、AdapterId=sim、AdapterVersion=0.2.0、Source=Simulation；头head-1，格式code16，RawCode/PrimaryRole=height/Unit=code，MinSamples=MaxSamples=32、MaxPayloadBytes=64；唯一plane height/I16/LittleEndian/Line/MaxRows=1/code/Scale=1/Offset=0；invalid bit pattern=0x8000/Sentinel。Encoder列表空，Trigger仅FreeRun；线频范围[1,1000]Hz、曝光范围[1,1000]μs是此模拟器能力；CanPauseInput/CanStop/CanReadback/CanQueryOperation均true。
- ParameterSet：唯一head-1/code16/FreeRun，LineRateHz=1000、ExposureUs=10、EncoderId/Calibration=null；实际读回逐字段相同，全部FieldKnowledge.Readback；ReadbackComplete=true。RunPlan：新非空RunId、Single、Actual.Revision、HeadPlan(head-1,0,100或1000)、MaxBatchesPerHead=1及上述期限。正常模拟每确认一条sink原Task完成后虚拟单调clock推进1ms（sample ticks=i/frequency1000），1000条为1秒、低于批2秒/run4秒；只推进协议clock，不推进真实wall watchdog，故障路径按各断言显式推进deadline。
- 每条AdapterFrame：session.Epoch、BatchKey(run,head-1,0)、Sequence=RawSequence=i、RawSequenceBits=64、TriggerIndex=null、SampleCount=32；plane(height,Offset=0,Rows=1,Columns=32,RowStride=64,PixelStride=2,I16,LittleEndian)；64bytes按小端写32个值i%100，无invalid。Position Unknown/frame=unknown/标定和encoder/rawcount/actual/command=null、Segment=0；SampleTime保留ticks=i/frequency=1000/domain=sim-clock/boot=sim-boot，Nanoseconds=null、ErrorBoundNs=null（不冒充跨域映射）。
- 格式/能力/参数Revision由夹具按§3.3同一字段编码生成源快照SHA256（不含Revision本身），Id分别sim-format-v1/sim-cap-v1/sim-param-v1；避免占位hash。构造顺序format→capability→requested参数→读回→run，注入ManualTimeProvider/DeterministicSensor/任一sink；新run/epoch只比较ContentSha256。Simulator工作线程受控推进逐条，收到Refused按其可暂停能力有限等待容量或结束故障，不在TryAccept回调阻塞。
- OnProfile由Archive复制到Host有界暂存或由Inspector计算摘要；无延迟正常路径用闩锁观察100/1000条完成，显式Stop/Close；fault版本先让原task未完成→断言Unknown/强持→解除闩锁→检查迟到归还。两个Host均无任何需要未定义公共接口的动作。

### 7.4 可发布Simulator/Replay及原reader闭包

Simulator/Replay属于本模块已规划能力，不仅是测试私有fixture。BCL实现放在唯一Core工程的Sources目录，不机械新增DLL；厂商实现仍由原设备模块持有。以下新增签名不改变Core v0.3既有record/编码oracle，扩展协议用独立前缀`pa-source-record-v1`，所有类型在Core namespace。工厂纯构造、不读流、不后台启动；Host在Factory前按§7.1预留source Stream/reader/lease/task及字节，原任务必须登记。

```csharp
namespace Asun.Modules.ProfileAcquisition;
public enum SourceRecordKind { Frame, Signal, End }
public sealed record SourceRecord(SourceRecordKind Kind, AdapterFrame? Frame,
    AdapterSignal? Signal);
public interface IProfileRecordLease : IDisposable
{
    SourceRecord Record { get; }
    long AllocatedBytes { get; }
}
public sealed record SourceRead(IProfileRecordLease? Lease, Error? Error);
public sealed record SourceDrain(DrainState State, int ActiveReaders,
    int OutstandingLeases, long OwnedBytes, Knowledge CountersKnowledge, Error? Error);
public interface IProfileRecordSource
{
    SourceKind Source { get; }
    Capability Capability { get; }
    ParameterSet Parameters { get; }
    ValueTask<SourceRead> ReadNextAsync(Budget budget, CancellationToken cancellation);
    ValueTask<SourceDrain> CloseAsync(Budget budget, CancellationToken cancellation);
    ValueTask<SourceDrain> QueryAsync(Budget budget, CancellationToken cancellation);
}
public sealed record ReplaySourceOptions(Capability OriginalCapability,
    ParameterSet OriginalParameters, Revision Archive, int MaxRecordBytes,
    int MaxCollectionElements, long SourceBytes, Budget Cleanup);
public sealed record SimulationOptions(Capability Capability, ParameterSet Parameters,
    int Profiles, double RawValue, long SourceBytes, Budget Cleanup);
public static class ProfileSourceFactory
{
    public static IProfileRecordSource CreateReplay(System.IO.Stream borrowedStream,
        ReplaySourceOptions options);
    public static IProfileRecordSource CreateSimulator(SimulationOptions options);
    public static IProfileSensorAdapter CreateAdapter(IProfileRecordSource source,
        Budget cleanup, TimeProvider clock);
}
public static class ProfileInputCodec
{
    public static byte[] EncodeRecord(SourceRecord record);
    public static ContractDecode<SourceRecord> DecodeRecord(ReadOnlyMemory<byte> bytes,
        int maxBytes, int maxCollectionElements);
}
```

SourceRead成功必须Lease非null/Error=null，End是显式终结record（Frame/Signal均null）且有lease，不能把null/空文件冒充正常EOS；错误Lease=null/稳定PA-001/006/012/014/019等。Frame kind仅Frame非null，Signal kind仅Signal非null；Frame.payload按原顺序字节保存，stamp不推导。ReadNext任一时刻至多一个原reader及一个未归还lease，未归还时新Read拒PA-010无IO；原reader超时/协作取消未真正结束则Query SourceDrain Unknown，拒新Read。已返回lease仍计源OwnedBytes直到Dispose幂等确认；source是原归还Owner，adapter只Dispose自己取得的lease，不能Dispose借用Stream或源未返回的记录。迟到Read得到lease后原adapter/root仍接收并归还，不因为任务观察结束扔掉buffer。

source.Close仅第一次锁存关闭、取消原reader并创建原清理Task，后续Close/Query有限观察该Task及原账本，不再创建清理或Read任务；观察timer完成不证明源结束。仍开着且没有在途数据时SourceDrain.State=Pending，关闭后只有原reader/lease/缓冲全部真实归还才Released；超时、归还失败或未知计数为Unknown。Close不能强制Dispose正在借用的lease；SourceRead错误/reader fault仍须原Owner释放其已分配对象。外部Stream自身缓冲与关闭Task属于Host额度，SourceBytes只计本源的reader/解码/lease/metadata，Root总reservation同时包含两者。adapter每个实例仅一次Start遍历，Stop/End/错误后不能新run接续残余流，返回PA-003；再回放须Host显式提供新source/stream/session，旧未知Owner先保留，不静默rewind。

options/source入口校验：SourceBytes>0，MaxRecordBytes/MaxCollectionElements>0，Cleanup有限正，所有Capability/ParameterSet按§3有效并深冻结；Simulation.Profiles与source产物数量uint/ulong checked，整数域RawValue超过表示范围拒绝而不unchecked截位。ReplayFactory借用Stream必须CanRead=true、不检查Length/Seek，不在构造读一个header。每次Read先预留固定长度prefix、checksum、最多2×bodyLength（读body+解码payload深copy）及§4.1计费metadata；从字节干扫描列表/字符串长度得到精确元素上界，在materialize前计费，预算不足不创建对象/数组。maxCollectionElements限制每个列表和累计条数，body自身uint长度须≤int.MaxValue/MaxRecordBytes；SourceBytes同时计reader暂存与返回lease总占用，不只算payload。DecodeRecord成功Frame.Payload是独立冻结copy，不能在调用方改原body时改Frame。异常读取/校验/复制所有已分配对象归原source Owner，异常归还失败SourceDrain Unknown。EncodeRecord仅规范值编码，输出byte[]由Host有界Archive reservation拥有，不能无预算无限积完整file。

Replay容器固定：起始严格UTF8长度前缀字符串`pa-replay-v1`、`pa-api-v0.3`、OriginalCapability.Revision.Sha256字符串、OriginalParameters.Revision.Sha256字符串；均须与options一致，再逐条`uint32 LE bodyLength + bodyBytes + 32byte SHA256(bodyBytes)`。body=`pa-source-record-v1`字符串、合同字符串、kind uint32、nullable Frame、nullable Signal；完整record按§3.4声明字段序，AdapterFrame.Payload为uint32长度+原字节（新增byte memory编码，不改旧方案）；Invalid及Planes列表规范排序同Core，厂商原quality旁证保在其Archive版本引用，不能凭本记录丢掉缺项诊断。长度/累计集合预算及checksum先验证，无包多态自由类型/SDK对象；禁止在校验长度前分配body。End后文件须EOS，返回End lease前额外读至确切EOS，尾部多余数据PA-001；End已消费后再Read拒PA-003零IO。空文件/截断/无End/错误checksum→PA-001，方案/合同不符→PA-019，不将损坏尾当收齐。固定header/前缀/探测EOS的暂存亦计SourceBytes，header长度必须恰符固定字符串及64byte小写hex，不能先按恶意长度分配。Archive Revision由Host证据Owner事先确认原归档身份，不以读取首批完成伪造完整文件校验；无法取得完整身份可只做诊断Replay，不生产引用。借用Stream由Host Owner强持且支持异步Read，不依赖seek/Length；取消Read等待不证明IO停，原Task仍保留。Close结束source reader/leases后释放内部缓冲而不关闭borrowedStream，原Host确认后再关流。若Stream返回前同步阻塞违约，wall watchdog失败并保Root，不创建线程abort恢复。

Simulator仅支持显式小型确定source：Capability/Parameters合法且完全读回、一个头/一个Line primary plane、所有planes相同sample范围的固定最小宽度，Profiles>0、RawValue finite且在所选scalar原表示域；整数值须整数且非invalid、浮点须可表示，格式量纲仍原格式。其它能力明确PA-001/019，不把“Simulator”猜成全厂商SDK。依次生成§7.3同逻辑frame/Sequence0..Profiles-1、原RawSequence64位，Position Unknown、SampleTime ticks=sequence/frequency1000/domain sim-clock/boot sim-boot（时间为模拟证据）、Source Simulation；租用一个精确合法行buffer，副plane使用同raw输入但遵其scalar编码，不能转真实激光质量。生成数据按字节端序，不依机器endianness；每Read只生成下一条，末尾InputEnded signal和End记录；元数据/行bytes≤SourceBytes先预留。故障/多头/图像/乱序夹具通过规范Replay record源注入，仍显式Simulation来源的测试IProfileRecordSource实现，不冒称live或Simulator自动支持这些设备。

Simulator全部plane.Kind=Line/MaxRows=1，宽度取FormatSpec.MinSamples，像素stride=scalar bytes、每plane连续紧排并按Role排序。首版仅FreeRun、EncoderId/Calibration为null的RawCode/Disparity输入，LineRateHz显式正且在范围，CanPauseInput/CanStop/CanReadback/CanQueryOperation=true；不支持Software关联或物理高度资格时构造拒PA-019，不伪造标定。RawValue须适用于每个plane且不匹配任何invalid码；F32须转float后仍finite且转回double等原值，F64按原bits，拒绝静默截断。源InputEnded用固定源Epoch/Run、Batch=null/Sequence=null/Time=null/Error=null；End无payload。协议样本ticks仍按上文原模拟域，仅adapter调度依LineRate，不能当实际曝光时钟。

Simulator adapter以Start时刻为单调原点，第i条（i从0）目标延迟为ceil(i×10,000,000/LineRateHz)个TimeSpan ticks，采用§7.5同一binary64精确有理数计算及checked转换、TimeProvider驱动有界等待；过期目标立即尝试该条，仍只有一个reader/lease，反压不压缩序号。Replay adapter首版不模拟原wall节拍，按完整sink容量尽快逐条输送，保原SampleTime且不sleep到原时间戳；节拍结果只代表此离线负载，原客户速率另Profile实测。

Simulator原Frame.Epoch/Run使用source构造时生成的固定非Empty Guid，仅作Simulation源身份，Batch.Index=0/Head=唯一能力头；adapter Start要求FirstSequence=0、Single MaxBatches=1且ProfilesPerBatch=SimulationOptions.Profiles，不满足PA-003，不擅自延长/拆批。多批/多头及图像正常Replay由Host规范记录提供，不把小型Simulator限制当通用Core限制。protocol clock按已读回LineRate推进，source sample sim-clock与接收TimeProvider不同域不混算；§7.3的1000Hz夹具正常1ms/条。真实吞吐测量用真实clock及负载Profile，不把虚拟1秒当wall吞吐。

CreateAdapter输出Id固定`pa-source-replay`或`pa-source-simulator`、Version=`0.3.3`，Discover能力复制源能力但替AdapterId/Version并按pa-source-bin-v1重算能力Revision；原Capability/Archive Revision保在source options/Host证据包，不能将原厂商型号身份改为当前运行设备资格。实际参数Revision仍由source.Parameters原规范定义，输出头/格式/触发与原source一致；Apply比较ParameterSet完整内容而非只比较Revision，不能hash相同但内容不同通过。source.Source=Vendor拒绝CreateAdapter；设备SDK不能绕本声明进通用reader。

CreateAdapter冻结source.Capability/Parameters/Source/版本Id，通用DeviceId沿原capability；只处理§3.3相同命令端口。Open登记源会话/OpenIdle不读数据；Discover给冻结capability；Apply仅接受与source.Parameters规范内容完全一致（sourceRevision包含真实格式不silent替换）的请求并逐项Readback，不重演归档时的硬件写入；Arm仍Core本地，不进adapter；Start把冻结ArmedPlan/AppliedParameters与source头/格式/first0/行数核对后启动单一reader任务，返回Acquiring。原记录Frame remap仅Run/Epoch/Batch.Head映射/Batch.Index按计划范围核验，Source替为当前Replay/Simulation，逐行位置/采样原时钟/raw序号/invalid不重算；原Frame已存在缺线仍保Sequence跳跃，不能以重新读次数压缩。批次Index/尾序号根据计划及原行身份映射，无法匹配即PA-008非silent调整；source多头必须原记录明确头与参数集合匹配。真实Vendor source不能经此通用adapter冒充SDK，CreateAdapter仅Replay/Simulation。

上述first0/已知行数核对仅用于小型Simulator。Replay Start不预读整个stream或猜总行数，只核对source实际参数/头/格式及Core已冻结计划；逐record保原Head/Batch.Index/Sequence，要求Head在计划内、Sequence落在§4.2该Index期望范围，不能加减FirstSequence或重编号。仅Run/Epoch替为当前值，AdapterSignal的非null Run/Batch同步替Run/Epoch并核Head/Index；源null仍null，原Fault/时间保留。一个archive只允许一个非Empty原Run/Epoch组合，首次非null锁存，后续变化拒PA-013并发Fault；原记录的不同epoch不能借remap混入同run。Simulation记录Frame.Source须Simulation；Replay原Frame.Source可为Vendor/Replay/Simulation，由首次frame锁存原值、后续必须相同，输出统一标Replay，不混合原来源。读取失败发Fault并锁存证据不完整，不把前面InputEnded或结构Complete当archive校验成功；资源关闭可Released，仍保该错误。Signal/End都经原lease归还，End确切EOS后发送InputEnded（重复原结束通知不改变事实），没有End不确认正常结束。

FreeRun/External/Encoder模式都是重放原事件/数据，不模拟实际电气动作；Software在收到真实Host TriggerCommand索引后才允许消费已关联该索引的source记录，没有明确TriggerIndex不能ACK假关联，PA-005/019。TriggerObserved由记录提供，原数据不足时有效计划InputEnded后Incomplete。Stop锁存拒新Read并协作取消原reader、处理迟到lease、等待已有归还，再InputEnded/Stopped；Close追加source.Close原Task及Query证明；所有活动/NativeDrained/ConnectionReleased只有原reader/tasks退出和所有源租约归还后确认。Source Close无需设备关闭，但模拟/回放ConnectionReleased表示本source adapter资源释放，不冒充物理停止。取消/超时沿§6；Query仅原source账、不重发Read/Trigger，未知保留原Task。SourceDrain Released要求CountersKnowledge Confirmed、ActiveReaders/leases/OwnedBytes均0；故障原Task结束仍须计账/归还证明。不实现自动重连/重采、不静默rewind stream。

Software Replay最多先持一个record lease以检查下一条Frame.TriggerIndex或TriggerObserved.Sequence关联；Host TriggerCommand仍只返回动作接纳知识，CommittedTriggerIndex及TriggerObserved须等匹配原record证明，不能凭等候的Frame回填事件。等待索引时保该lease及原reader，不并行读后续记录，按原Execution/Run期限观察；缺关联拒PA-005/019并Fault，不跳过数据找匹配项。重复索引沿Core原幂等账本不再推进source；索引记录计source metadata，不建无限trigger字典。

两无UI消费者装配替换测试DeterministicSensor为：Root先登记Stream/options→CreateReplay（或CreateSimulator）→CreateAdapter→CreateManagedBuffers/sink/session→§7.1原Execute/Drive/Stop/Close/Query/Dispose全记录；factory无IO。source及session各有原Close/Query任务保底slot，Host预留TaskSlots必须在32中另留source2个（不占Core四个cleanup保底），容量不足不构造。line reader有独立stream/source bytes上限，不能仅用Core128bytes证明总内存128；Benchmark source/native/Host/preview分别统计。IM-063 SDK桥仍由该模块实现，模块内算法/Producer-Reader归还顺序已确定，不把通用接口设计留给未来设备Owner。

### 7.5 有界参数建议（Advice，不自动应用）

仅为已获批采集计划提供线率/缓冲容量的确定工程建议，曝光/激光功率/标定阈值无可靠物理依据时保原值或拒绝，不以软件平滑度调生产。公开形状位于Core同namespace；不修改既有ParameterSet或ResourceLimits对象，不改变既有API/hash前缀，Advice为独立`pa-advice-v1`版本数据。

```csharp
namespace Asun.Modules.ProfileAcquisition;
public enum AdviceStatus { Suggested, Rejected, Expired }
public sealed record AdviceEvidence(Revision Benchmark, bool AllSamplesReleased,
    SourceKind Source, long MaxConsumerHoldNs, long ActualBytesPerProfile,
    int MetadataChargePerProfile);
public sealed record AdviceRequest(Capability Capability, ParameterSet Parameters,
    ResourceLimits CurrentLimits, ResourceLimits HostCeiling, AdviceEvidence Evidence,
    IReadOnlyList<double> CandidateLineRatesHz, int BurstProfiles, int MaxCandidates);
public sealed record AdviceCandidate(double LineRateHz, int RequiredProfiles,
    long RequiredOwnedBytes, int RequiredMetadataBytes, bool FitsCurrent,
    bool FitsHostCeiling, IReadOnlyList<ValidationIssue> Issues);
public sealed record ParameterAdvice(string Scheme, string InputSha256,
    AdviceStatus Status, Revision Capability, Revision Parameters, Revision Benchmark,
    SourceKind Source, IReadOnlyList<AdviceCandidate> Candidates, AdviceCandidate? Selected,
    IReadOnlyList<ValidationIssue> Issues);
public static class ProfileParameterAdvisor
{
    public static ParameterAdvice Suggest(AdviceRequest request);
    public static ParameterAdvice CheckCurrent(ParameterAdvice advice,
        Revision capability, Revision parameters, Revision benchmark);
    public static byte[] EncodeInput(AdviceRequest request);
}
```

有效域：MaxCandidates∈[1,1024]为本版算法最多评估数量而非生产阈值；实际候选数1..MaxCandidates，全部finite>0、不重复且匹配每头LineRateHz公开范围。Head数量H是参数冻结Heads.Count；BurstProfiles≥0是**全部头合计**源端峰值同时在途输入，由Host/设备证据提供；MaxConsumerHoldNs>0、ActualBytesPerProfile≥对应格式可保全单条最坏bytes（含真实分配器padding）、MetadataChargePerProfile>0、AllSamplesReleased=true（任一删失/DrainUnknown/未归还数据拒绝PA-015）；CurrentLimits及HostCeiling合法，Ceiling各项≥Current，不能给“可增加资源”隐含授权。evidence.Source标记Vendor/Replay/Simulation，建议也只是同负载工程估计，模拟证据不给生产节拍资格。能力LineRate/已编码请求/负载版及hash不足拒绝PA-002/001，不补设备范围或优选值；typed Threshold均由消费者Profile提供，算法常量只用于有界计算，不造客户节拍。

算法固定：冻结/Validate→候选按Hz从高到低排序→各候选r按其IEEE754实际二进制值转精确非负有理数p/q，计算W=ceil(H×p×MaxConsumerHoldNs/(q×1,000,000,000))，不能浮点乘积向下舍入。BCL BigInteger实现：normal double p=(2^52+mantissa)×2^max(e-1023-52,0)、q=2^max(1023+52-e,0)；subnormal p=mantissa、q=2^1074；W=(numerator+denominator-1)/denominator。位宽由binary64固定，W超过int.MaxValue拒该候选PA-001；N=checked(W+BurstProfiles+1)，B=checked(N×ActualBytesPerProfile)，M=checked(N×MetadataChargePerProfile+现有固定metadata额度)。固定metadata额度=CurrentLimits.MetadataBytes-CurrentLimits.BufferedProfiles×MetadataChargePerProfile，负值说明证据/当前配置不一致，整请求拒绝。与current/ceiling逐项比较profile/bytes/metadata，其他limits保持不变。Selected为按序第一个FitsCurrent且Issues为空者；全部不适合current但有FitsHostCeiling时仅显示可选扩容Candidates、不Selected，Status Rejected/PA-010（宿主资源是否变更不由模块决定）。不自动选最大Ceiling值，更不改批数或Trigger/曝光。返回输入hash及所有候选和失败原因，不返回“推荐生产达标”。计算纯同步有限MaxCandidates，不创建后台Task。

InputSha256=SHA256(EncodeInput)：`pa-advice-v1`方案字符串、`pa-api-v0.3`合同字符串，完整AdviceRequest声明字段序（CandidateLineRates按下降排序），基本/集合/Revision编码依§3.4；HostCeiling/真实测量身份/Source均进hash。CheckCurrent只比较三个Revision.Id/Sha256：任一变化返回复制的Status Expired/Selected=null/PA-003，保持原InputSha256/候选证据；不悄悄重新Suggest。原Advice不得跨负载/InputSha不同代替新建议；Host批准新candidate时显式创建新ParameterSet Revision/ApplyCommand并按原端口验证/读回；资源限额变更需停止/释放后新session，不能live扩大limits。UI由Host参数页单独显示候选r/N/B/M、来源和过期/拒绝状态，候选保存在Host有界记录，不改变PropertyGrid Actual、RunPlan或按钮命令；“采用建议”仅写草稿，再走已批准Apply流程，宿主批准与Advice事实分开。

Advice三形状：Suggested必须Selected引用Candidates中首个FitsCurrent无Issues者，Issues空；Rejected时Selected=null且有稳定ValidationIssue，完整可表示输入仍保InputSha256；Expired保原Candidates/hash且Selected=null/PA-003。输入无法规范编码（null/非法字符串/未知enum等）按既有ProfileAcquisitionException(PA-001)而不造hash，能编码但无有效证据则Rejected。Candidate超过int/long可表示域时该项Required数量取0占位并附PA-001且FitsCurrent/FitsHostCeiling=false，0不表示无需缓冲；其它合法候选仍可评估。CheckCurrent先校验Scheme/Revision/hash/候选不变量再比较版本；不能让恶意Selected绕校验。线率/资源推荐仅工程Advice，不推导sample quality或计量精度；所需buffer还受真实源不可暂停峰值和消费者hold证据，证据不足拒绝。

Host证据Owner将Benchmark Revision绑定完整负载Profile（头/格式/最大payload/分配器/完整sink版本、Hold统计及删失、Burst来源）；任一负载/预算/Source或这些测量输入变化须以新Benchmark Revision及新AdviceRequest重算。CheckCurrent没有新Limits/负载参数，不能单凭三个版本相同证明负载未变；Host不得复用旧版本掩盖变化。到期是单调锁存：CheckCurrent对已Expired保持Expired/Selected=null，即使版本改回也不恢复采用资格。建议值展示无动作，实际采用前Host须核对原InputSha256对应当前完整request及证据，不依靠UI表格可信性。

ParameterAdvice.Source恰取AdviceEvidence.Source并随过期结果保留；UI依据此显式字段显示来源，不从Benchmark名称推断Vendor或Simulation。结果及所有候选深冻结，CheckCurrent拒绝未知Source枚举；Host核对输入hash时也核此来源一致，不能将模拟建议改标签当真实测量。

独立Suggest/EncodeInput入口也须在深冻结/编码前按§4.1扫描并计费完整request及最大候选结果，受CurrentLimits.MetadataBytes约束；超限PA-010，不先复制任意大的能力/头/plane列表再校验。固定binary64有理数位宽与MaxCandidates限制计算工作量，Head计数/各列表按计费上限扫描，预算不足不创建后台工作或完整结果数组。source工厂同样先按SourceBytes计费options能力/参数快照及最小reader/行额度，再深冻结；Host所有源/Advice reservation遵守各自独立Owner，不重复计同一共享快照或漏计新输出。

合成期望：H=1、候选[1000,500]Hz、hold=1,000,000ns、Burst=0、实际64bytes/条、charge=256bytes/条，Current=2 profiles/128bytes/1 MiB metadata，Ceiling相同，则两候选N=2、B=128、M=1 MiB，Selected=1000。hold改2,000,000ns则1000→N3/B192不适合，500→N2/B128适合，Selected=500；hold未知/AllSamplesReleased=false→Rejected且Selected=null；若全部超Current但适合显式Ceiling仍只提示扩容而非Selected。r=0/NaN、1025候选、单位遗漏、metadata固定额负、checked overflow拒绝无设备动作，benchmark/source revision变CheckCurrent Expired。

## 8. 可选WPF控件和操作链

### 8.0 Module WPF API Contract v0.2

代码/TestHost/namespace唯一绑定在Core binding。以下为待实现签名规格，非编译通过声明；接口全部归Wpf DLL（UI DTO不下沉Core），仅用BCL、Core及WPF FrameworkElement/UserControl。真实共享viewport/frame只由Host实现窄port，模块不复制影像解码、调色、缩放、GPU/native渲染算法。无viewport时Host注入空显示port并明确Unsupported，不能用测试画面冒充现场影像。

```csharp
namespace Asun.Modules.ProfileAcquisition.Wpf;
using Asun.Modules.ProfileAcquisition;
using System.Windows;
using System.Windows.Controls;

public enum UiIntent { Open, Discover, Apply, Arm, Start, Trigger, Stop, CloseSession,
    QueryOperation, QueryRun }
public enum ProjectionState { Unbound, Bound, Closing, Closed, Unknown }
public enum PreviewStatus { Available, Missing, OverBudget, Unsupported, Closing }
public enum PermissionDecision { Allowed, Denied }
public sealed record UiText(string Key, IReadOnlyList<string> Arguments);
public sealed record UiSelection(Epoch Epoch, BatchKey? Batch, ulong? Sequence, string PlaneRole);
public sealed record UiLimits(int SnapshotRows, int UpdateRecords, int PreviewLeases,
    long PreviewBytes, int MetadataBytes, int OriginalTaskSlots, double RefreshHz);
public sealed record UiOptions(UiLimits Limits, Budget Observation, Budget Cleanup);
public sealed record UiBinding(Guid Id, Epoch Epoch, string DeviceId);
public sealed record UiCommandState(UiIntent Intent, PermissionDecision Permission,
    bool StateAllowed, UiText? DisabledReason, UiText Tip);
public sealed record UiParameterField(string Name, string Unit, string? Requested,
    string? Actual, FieldKnowledge Knowledge, UiText Label, UiText? Warning);
public sealed record UiBatchRow(BatchSummary Summary, UiText StructureText,
    UiText PositionText, UiText SourceText);
public sealed record UiDiagnostic(Error Error, UiText Message, UiText Recovery,
    OperationId? Operation, BatchKey? Batch);
public sealed record UiSnapshot(ulong Revision, UiBinding Binding, SessionState State,
    RunSnapshot? Run, Capability? Capability, ParameterReceipt? Parameters,
    IReadOnlyList<UiBatchRow> Batches, IReadOnlyList<UiParameterField> ParameterFields,
    IReadOnlyList<UiCommandState> Commands, IReadOnlyList<UiDiagnostic> Diagnostics,
    UiSelection? Selection, ResourceSnapshot Resources);
public sealed record UiUpdate(ulong Sequence, UiSnapshot Snapshot, bool Gap,
    ulong? MissingFirst, ulong? MissingLast);
public sealed record UiRequest(Guid RequestId, UiBinding Binding, UiIntent Intent,
    Command? Command, OperationId? OriginalOperation, RunId? Run, Budget Budget);
public sealed record UiReply(Guid RequestId, PermissionDecision Permission,
    OperationReceipt? Operation, RunSnapshot? Run, Error? Error);
public sealed record UiRequestBuild(UiRequest? Request, Error? Error);
public sealed record UiHostOptions(UiBinding Binding, RunPlan Plan,
    Budget CommandBudget, UiOptions Projection);
public interface IProfileUiAuthority
{
    PermissionDecision Check(UiRequest request); // 宿主现有权限，短返回、无IO
    ValueTask<UiReply> ExecuteOwnedAsync(IProfileAcquisitionSession session,
        UiRequest request, CancellationToken cancellation);
    ValueTask<OperationReceipt> QueryOwnedAsync(IProfileAcquisitionSession session,
        OperationId original, Budget budget, CancellationToken cancellation);
}
public static class ProfileUiCodec
{
    public static byte[] EncodeSnapshot(UiSnapshot value);
    public static byte[] EncodeReply(UiReply value);
    public static byte[] EncodeClose(ProjectionCloseReceipt value);
    public static byte[] EncodeRequest(UiRequest value);
    public static ContractDecode<UiSnapshot> DecodeSnapshot(ReadOnlyMemory<byte> bytes,
        int maxBytes, int maxCollectionElements);
    public static ContractDecode<UiReply> DecodeReply(ReadOnlyMemory<byte> bytes,
        int maxBytes, int maxCollectionElements);
    public static ContractDecode<ProjectionCloseReceipt> DecodeClose(ReadOnlyMemory<byte> bytes,
        int maxBytes, int maxCollectionElements);
    public static ContractDecode<UiRequest> DecodeRequest(ReadOnlyMemory<byte> bytes,
        int maxBytes, int maxCollectionElements);
}
public interface IProfileUiSubscription
{
    Guid Id { get; }
    IAsyncEnumerable<UiUpdate> ReadAsync(ulong afterSequence, CancellationToken cancellation);
    ValueTask<ProjectionCloseReceipt> CloseAsync(Budget budget, CancellationToken cancellation);
    ValueTask<ProjectionCloseReceipt> QueryStateAsync(Budget budget, CancellationToken cancellation);
}
public interface IProfileViewHost
{
    UiBinding Binding { get; }
    UiRequestBuild PrepareRequest(UiIntent intent, ParameterSet? draft);
    ValueTask<UiSnapshot> GetSnapshotAsync(Budget budget, CancellationToken cancellation);
    IProfileUiSubscription Subscribe(); // 只登记有界metadata订阅，不执行设备命令
    ValueTask<UiReply> ExecuteAuthorizedAsync(UiRequest request, CancellationToken cancellation);
    ValueTask<UiSnapshot> SelectAsync(UiSelection selection, Budget budget,
        CancellationToken cancellation);
}
public interface IProfileTextResources
{
    IReadOnlyList<string> Languages { get; }
    string Resolve(string language, UiText text);
}
public interface IProfilePreviewLease : IDisposable
{
    Guid Id { get; }
    UiSelection Selection { get; }
    FormatSpec Format { get; }
    IReadOnlyList<PlaneLayout> Planes { get; }
    IReadOnlyList<InvalidSpan> Invalid { get; }
    PositionObservation Position { get; }
    ReadOnlyMemory<byte> Payload { get; }
    long AllocatedBytes { get; }
    string ContentSha256 { get; }
}
public sealed record PreviewAcquire(PreviewStatus Status, IProfilePreviewLease? Lease, Error? Error);
public interface IProfilePreviewStore
{
    PreviewStatus TryCopy(ProfileView borrowed); // sink借用有效期内同步深复制
    PreviewAcquire TryAcquire(UiSelection selection);
    ValueTask<ProjectionCloseReceipt> CloseAsync(Budget budget, CancellationToken cancellation);
    ValueTask<ProjectionCloseReceipt> QueryStateAsync(Budget budget, CancellationToken cancellation);
}
public interface IProfileViewportPort
{
    FrameworkElement Element { get; }
    ValueTask PresentAsync(IProfilePreviewLease borrowed, CancellationToken cancellation);
    ValueTask ClearAsync(Budget budget, CancellationToken cancellation);
}
public sealed record ProjectionCloseReceipt(Guid BindingId, ProjectionState State,
    int OriginalTasks, int PreviewLeases, long PreviewBytes,
    bool SubscriptionClosed, bool ViewportCleared, Error? Error);
public sealed class ProfileAcquisitionView : UserControl
{
    public ProjectionState ProjectionState { get; }
    public ValueTask<UiSnapshot> BindAsync(IProfileViewHost host, Budget budget,
        CancellationToken cancellation);
    public ValueTask<UiSnapshot> SelectAsync(UiSelection selection, Budget budget,
        CancellationToken cancellation);
    public void SetDraft(ParameterSet draft);
    public void SetAdvice(ParameterAdvice advice); // 显示独立Advice，不改草稿/实际
    public void SetLanguage(string language);
    public ValueTask<UiReply> RequestAsync(UiRequest request, CancellationToken cancellation);
    public ValueTask<ProjectionCloseReceipt> CloseProjectionAsync(Budget budget,
        CancellationToken cancellation);
    public ValueTask<ProjectionCloseReceipt> QueryProjectionAsync(Budget budget,
        CancellationToken cancellation);
}
public static class ProfileAcquisitionViewFactory
{
    public static IProfileViewHost CreateHost(IProfileAcquisitionSession session,
        UiHostOptions options, IProfileUiAuthority authority);
    public static ProfileAcquisitionView Create(UiOptions options,
        IProfilePreviewStore previews, IProfileViewportPort viewport,
        IProfileTextResources text, string language);
    public static IProfilePreviewStore CreateManagedPreviewStore(UiLimits limits);
}
```

Create须在Host STA Dispatcher调用，构造无设备/IO/订阅/后台任务，仅建立UI对象；Host依§7在Factory前预留Root及全部UI对象、previewbytes/任务额度，逐对象绑定。UiLimits所有数量/bytes>0、RefreshHz finite>0，Observation/Cleanup有限正预算；默认语言无隐式自动切换，language仅接受Host资源提供的zh-CN/zh-TW/en-US及显式扩展集合，未知语言拒绝不改当前状态。文本Resolve必须覆盖所有键、有限长度且不IO，缺键显示稳定诊断并不执行命令。Guid/epoch/字符串/选项校验同Core§3，snapshot deep freeze且列表截断标记在Diagnostics；每个UiText参数有界，不能把SDK文本塞入无限UI集合。

CreateHost纯构造并深冻结UiHostOptions，Binding.Epoch必须等session.Epoch/DeviceId非空，RunPlan及budget完整；不自动Open/订阅/发设备命令。其返回模块内部实现的IProfileViewHost桥（不再留全部投影/命令准备给应用重写）；authority为Host现有授权与§7 Root包装端口。Check按当前权限短返回，Prepare只参考Host冻结计划和已知实际快照，不IO。ExecuteOwnedAsync必须在调用Core前登记完整request/Core Command及原Task到进程Root，QueryOwnedAsync同理；root记录容量失败返回PA-010无Core动作。调用时桥再次Check，Denied不能调用ExecuteOwnedAsync；authority.ExecuteOwned内部也再次校验，权限在两检查之间撤回时返回Denied零动作，不能依赖第一次Check。权限许可不包含产品质量放行，Core设备可执行状态仍由其Validate/Execute决定。

桥正常第一次快照State=Created、Capability/Parameters/Run=null、Resources为本session无借用状态，DeviceId取冻结Binding；只有通过桥执行/原查询的真实receipt才更新Actual/State，不给初始值假Configured。被其它同Root授权Host改状态时，桥通过保存的原operation/run有限Query（Authority登记原Task）补快照，未知显示Unknown，不猜session属性；绑定至已在运行session时要求Host先用QueryOwned原operation取得真实receipt，否则仍按未知/PA-017禁Start。Subscribe的Core事件枚举由桥ProjectionOwner记录原MoveNext及游标，最后订阅关闭只注销该桥投影，不Dispose session；Host Root可持续持session。查询intent的ExecuteOwned由Host固定映射QueryOperation/QueryRun，桥的GetSnapshot只在已知待对账ID时QueryOwned，不创造operationId冒充查询。

UiLimits.MetadataBytes按§4.1同一计费模型计投影record/文本/ring/草稿/订阅容量，PreviewBytes只计复制payload实分配，各类不重复漏计；OriginalTaskSlots包含父任务/叶MoveNext/HostRequest/Present/Clear/Close，至少为cleanup预留4项。同步SetLanguage/SetDraft/TryCopy/TryAcquire及Subscribe必须短返回、不IO、不等锁外Task；异步port同步段同样短返回，所有budget入口在Execution墙钟/协议有限观察后返回结果或PA-015 Unknown，原Task仍由Root保留。枚举MoveNext由投影独立token和有限wall观察控制，未收到update只等待有限周期查询快照，不让无限空枚举阻止Close。

view内部有一个instance ProjectionOwner（保存binding/host/store/viewport/订阅/原Task records/lease、generation/字节及每错误消费标志），作为view字段由Host预留Root强持，不依赖GC/self-reference维持Owner，不建立隐藏静态恢复服务。Host先记录Bind原Task再调用，view在每port调用前预留内部task record，同一份叶Task可由Host/ProjectionOwner双强持但只有ProjectionOwner归还显示lease；外层Bind/Close wrapper结束Unknown不删除内部记录。容量不足不新发Select/Present/Request，拒绝PA-010、保Root、用预留cleanup slots关闭投影。Dispatcher只更新UI，不await卡住任务占死UI；取消不abort线程。

Bind：Unbound/已确认Closed→校验host.Binding→先记录原GetSnapshot任务并有限观察→原Subscribe登记且保存Id→原ReadAsync枚举/每次MoveNext任务由Root强持→Bound，订阅只metadata。bind失败嵌套finally Close原订阅/Clear，不Stop共享session；unknown保原host/订阅/view/原tasks。已Bound二次Bind拒绝，必须CloseProjection确认后换绑定。没有读取过快照也不能让首个preview初始化设备。Update序号/Revision单调，旧Binding/epoch update忽略且归原Owner；Gap经有界GetSnapshot补投影，不假装补全生产payload。UiSnapshot不保存ProfileView/Core Memory，近期行数≤SnapshotRows、ring≤UpdateRecords、总metadata≤UiLimits；超限诊断并断开投影而非扩大缓存。

UiUpdate.Gap=false时MissingFirst/Last=null，true时均非空且first≤last；gap只影响该订阅游标，Update.Sequence按Host projection序号单调递增。Subscribe总个数≤UiLimits.UpdateRecords（既定limit第二用途），各reader至多一个MoveNext；同view只一个订阅，枚举0从最早保留位置开始，超末游标PA-001；有间隔先Gap再快照。RefreshHz控制最新投影合并频率，状态/错误/权限改变立即入有界ring，不因节流静默丢关键未知，超ring仍Gap+Query；preview刷新不能改Core counters。ReadAsync在SubscriptionClosed且保留项已读完自然结束，关闭枚举DisposeAsync原Task也入Owner，不能只cancel就删reader。

Select只选当前Binding的批次/序号/plane，Sequence非空须Batch非空，批次须在已读投影/Host保存索引中，未知/淘汰返回PA-017并保持原选择；可查看同epoch历史批但不以选择激活运行。Host.SelectAsync只投影查询，不Start/Apply。Grid、影像和Chart同一UiSelection，selection变化保存原Select task并有限观察、标generation；旧generation迟到结果不覆盖新选择。SetDraft深冻结参数，UI显示纯Validate结果；草稿不改Actual或设备，只有授权Apply request才交Host。

正常按钮动作闭包：命令绑定UiCommandState.Intent→Host.PrepareRequest(intent,draft仅Apply有值)同步纯构造→UiRequestBuild成功非空Request/Error=null→view.RequestAsync→Host再次授权并调用Core。PrepareRequest失败Request=null/Error非空，显示对应禁用/恢复文字且零设备动作。Host用其冻结当前设备/run计划为Open/Arm等完整Command生成非空ID、Binding epoch及显式budget；Arm所需RunPlan来自宿主已提供的非产品化采集计划（TestHost用§7.3），Start/Stop用原run、Trigger索引用Host已知高水位、Query用当前待对账operation/run。无合法计划或未知索引PA-003，不留给UI临时猜字段、不自动Start。PrepareRequest只校验/冻结，不预占已执行动作，Prepared请求在执行前仍复核；同一次点击保存该prepared request，重试复用，不重新生成ID。

Select/Bind失败有已绑定上下文时返回原UiSnapshot加一条UiDiagnostic(Error/短Message/Recovery)，Revision及Selection不晋升；无法返回合法初始快照或预算非法则ProfileAcquisitionException相应PA键，ProjectionOwner先保原记录/清理。SetDraft无绑定/非法参数、SetLanguage未知语言抛PA-001且保原草稿/语言；权限Denied只抛/回报PA-003不借原操作成功。UiSnapshot.Binding须等Host.Binding/epoch，Resources取Core快照不能混作UI资源；Run/Parameters/Capability不可用时null并有对应状态，不能空类型冒充成功。Batches/ParameterFields排序按batch/字段稳定，Commands每UiIntent最多一项，缺项视Denied；Source/状态文字来自稳定enum映射，Snapshot只携带UiText而不烙语言后的字符串。

Request：UiRequest.RequestId非空，Binding相同；设备intent必须带相应Core Command（类型、Context epoch及预算一致），查询intent仅带OriginalOperation或Run及Budget、Command=null；其它组合PA-001无动作。IProfileViewHost是Host实现的授权桥，当前权限+Core状态在**调用时**重新校验，Denied返回无operation/PA-003，不凭按钮Enabled放行；Allowed立即保存原Core Execute/Query task+身份到§7 Root再有限观察，Unknown完整UiReply回传。view不直接调用session，不拥有角色/放行/设备最终权；Host传入前即已按其现有权限实现策略，本模块不建权限库。双击相同RequestId复用原Host记录，不新发Command；view保存一次原Request task，未结束不能被关闭页面抛弃。

RequestId的有界Host记录保存Binding/Intent/冻结请求hash，相同ID异内容PA-016无动作，淘汰后PA-017不认未执行；保持Core operationId原账本身份。projection token只控制订阅/显示，不能传作Host设备命令的业务取消令牌；RequestAsync的显式调用方取消仍按Core取消契约执行，由Host原Root处理，不由CloseProjection隐式取消。UiSnapshot.Commands为空不默认Allow；UiReply.Denied时Operation/Run=null，Allowed查询只对应一个查询结果，未知结果保留Error/原请求ID。

Preview：Host sink在Core原借用有效期内TryCopy；本模块CreateManagedPreviewStore用精确byte[]复制payload及format/layout/invalid/位置/selection，绝不引用Core buffer。latest-wins覆盖仅释放未借出的旧entry；已Acquire的entry用同Owner引用计数，Memory到最后lease.Dispose才清除并扣实际bytes。TryAcquire成功创建只读lease及Id/计费，额度同时限制store-owned entries与所有outstanding leases的**实际**总字节/个数，超限OverBudget不分配，不能因隐藏旧entry少计；missing不返回空成功lease。只保留每头最新preview，旧序号由Host归档port另提供或Missing，不缓存整run。TryCopy非法format或未算ContentHash返回Unsupported，不重建高度。

IProfilePreviewLease.Invalid复制ProfileView.Invalid最终核验域，Position复制核验位置，Format非null且同原内容hash；源Metadata.Invalid/Position可作为Host归档证据，但图像/曲线不以原未核验域替最终invalid。复制entry不是再计算视觉结果；同plane元素invalid不得在Chart作0点或跨空洞连线，刻度依plane.Scale/Offset/Unit，原code仍可切换显示。

PreviewLeases同时限制被store持有的entry数及outstanding lease数，各自不能超过该值；同entry多租约只计一次实际payload bytes，但每个lease计metadata/lease数量。TryCopy预留新entry容量后才复制并替换旧entry；过预算保留旧entry、返回OverBudget，不先释放仍显示的旧lease腾空间。TryAcquire必须精确匹配epoch/Batch/Sequence/PlaneRole并返回完整复制layout，不能给请求旧批静默换最新帧；null Sequence可解析为该请求头/批的最新条，并在lease.Selection返回明确实际序号。无Batch的Acquire返回Missing；过时未保存条目Missing。lease.Dispose线程安全且幂等，只释放自己的引用；store Close拒新copy/acquire，等真实lease归还才Closed，否则Unknown保entry/Owner。

view每次显示先预留原Present Task记录、取得lease立即登记，再调用viewport.PresentAsync；原Task结束且fault已消费后finally Dispose该lease。Present超时/Close/selection变更不释放仍在读的lease，转投影Unknown并保Root，迟到任务按原lease Owner归还。viewport负责自己的真实影像显示及独立资源；Element仅嵌入Dock中央，view不另实现native渲染；port Present完成承诺不再借用lease，Clear完成承诺不再显示/引用旧资源。Chart只读取有界复制的line数据及invalid，不执行重建/插值。Clear不能抢在原Present未结束时证明归还。

CloseProjection顺序：标Closing、拒绝新Request/Select/Acquire→取消本投影更新token→有限观察原Read/MoveNext/Select/Request/Present tasks（授权Host设备动作继续由原Host Root负责，关闭不能取消其生产命令）→关闭原subscription→真实Present结束归还lease→Clear原viewport task→解绑Element/事件/语言→Closed。每个original task登记/观察同§7，cleanup嵌套finally不漏Close/Clear；任一未知返回ProjectionCloseReceipt Unknown/PA-015并保view/host/previews/viewport/root，不发Stop/CloseCommand，不清预览资源冒充成功。CloseProjection重复调用复用原task；view不Dispose共享preview store，只有拥有store的Host在其所有views关闭/leases归还后CloseAsync。权限查询、语言切换、关闭投影均不能隐式复用或停止共享session。

ProjectionCloseReceipt.State只描述显示资源，不等Core.SessionState；BindingId取已绑定UiBinding.Id，未绑定view取Guid.Empty且无订阅/任务时可Closed。subscription关闭结果使用相同BindingId，仅SubscriptionClosed及其原任务状态，不虚构ViewportCleared；store关闭结果BindingId=Guid.Empty，计整个store outstanding租约/字节，不虚构subscription/viewport事实。view最终receipt组合自身证明，OriginalTasks/PreviewLeases/PreviewBytes必须为自身仍持有的实际数，shared store仍被另一view使用不妨碍本viewClosed；计数须已知、非负，Closed时全部为0且view的SubscriptionClosed/ViewportCleared=true。OriginalTasks不包括当前返回receipt自身observer wrapper，以免自等待，但必须包含所有port叶Task及借用者。viewport Element单一父容器，TestHost两view注入各自viewport port，不共享同FrameworkElement或清另一view；store可以共享，lease责任分开。

QueryProjectionAsync与subscription/store.QueryStateAsync均有限只读原Owner账，更新迟到任务/fault已消费后的实际状态，不重发Close/Clear/Present；任一未知持有计数State Unknown。Close原wrapper已完成Unknown时重复Close仅读同一原清理账，可返回新不可变receipt，但原设备/viewport操作不二发；所有原task/leases归还、subscription真闭合和Clear完成后Query才Closed。store无lease且owned latest entry不再被借用时Close清掉其引用/字节，不能永远保latest导致正常关闭卡住。返回Invalid/Unknown也保view根；Host在Query确认投影全闭合后可退**显示子槽**，共享session根继续存在，不要求关session才能离页。

UI版本/结果编码：UI合同前缀pa-ui-v0.2；UiReply/UiSnapshot/ProjectionCloseReceipt/UiRequest等record采用§3.4基本类型及声明字段序，规范日志方案pa-ui-record-bin-v1、前缀后kind uint32（Snapshot=0/Reply=1/Close=2/Request=3），无FrameworkElement/Task/lease Memory或本地化最终字符串。UiRequest含Core Command时用nullable byte+uint32长度+完整EncodeCommandForHash字节，另写command.Context.Id（hash编码本身省该ID），避免继承重复。UI id/Revision不重复生成业务身份；未知kind/version拒PA-019，MAX metadata先校验。该编码只供Host审计/Oracle，不要求UI保存第二事实库；WPF API无持久IO。三语资源对固定enum/PA键全部覆盖，错误上下文通过UiDiagnostic.Operation/Batch/Message.Arguments引用；缺资源不能默默翻成“完成”。

字段规范化：UI.Reply的Permission是本次授权决定，Unknown动作知识仍取其Operation，Denied Reply不得带Operation/Run；UiSnapshot.Resources与Run.Resources若Run非null必须同一冻结采样。snapshot的Batches按Head/Index，ParameterFields按Name UTF8排序，Commands按Intent枚举，Diagnostics按首次发生输入序；Texts Arguments有序不排序。Bind/Request/Selection及Close输出均只在UI Dispatcher提交冻结值，Task延续的数据处理在原Owner上完成；不把Dispatcher线程顺序当设备触发时间。

语言及命令映射冻结：UiIntent Title键为Cmd.<Intent>，状态键State.<SessionState>，枚举参数/单位键Enum.<Type>.<Name>/Unit.<code>，错误主句Err.PA-nnn、恢复句Recovery.PA-nnn。由Wpf程序集内默认资源表提供zh-CN/zh-TW/en-US完整键，Host资源可覆盖/扩展但必需键先Validate；本模块不硬写SDK异常文字。所有动态值以显式CultureInfo(language)显示，hash/参数readback文本仍InvariantCulture；语言切换只重Resolve.UiText，不重Prepare/Execute。错误恢复分组固定：001改输入；002重新读取能力；003/004查状态/实际参数；005/012/015/017查原操作且资源释放前禁启动；006～009保存原证据/查来源；010降低输入负载或改完整保存端；011显示已请求取消/等待释放；013不复用旧连接；014查设备连接/原厂码；016使用原请求身份；018Query补投影；019使用支持版本/旧资料只读；020检查完整保存端并查询资源。三语需自然翻译同语义，资源门PA-U06检查实际短句，不把Unknown说成成功。

ProfileUiCodec遵守Core Decode的maxBytes/累计集合额度、尾字节/UTF8/枚举/nullable检查，另核上述Binding/权限组合/Close计数不变量；成功Value非空/Error=null，拒绝Value=null/稳定Error。核心嵌套record只写其字段（不套独立result header），Core Command仅按上文特例嵌套；本版UI record排序按§8规则，不把语言投影作为hash影响因素。DecodeRequest的Command子块经已冻结§3.4kind/字段解析并恢复另存Context.Id，非法/未知版本拒绝而不执行。TestHost各自编码UI正常Reply、Denied Reply、Close Unknown/Closed并反解，对源输入再编码，验证未知version/超限全部拒绝；日志工具不是生产事实Owner。

Host UI最小顺序：§7 Root预留→CreateManagedPreviewStore→Host复合sink接TryCopy→实现authority/资源/viewport窄port并立即Root绑定→CreateHost(session,完整UiHostOptions,authority)→Create→记录Bind原Task有限观察→SetLanguage/SetDraft/Select/Request分别上述规则→finally记录CloseProjection原Task有限观察→Host store Close原Task有限观察（仅自身store且所有view归还）→满足投影与原Core释放/错误消费屏障才退槽。TestHost用两个view挂同Host桥验证关闭其中一个不停止run、不关闭共享store；授权命令由唯一Host原Root调同Core接口。

### 8.1 紧凑构图与高级联动

SetAdvice验证Scheme=pa-advice-v1、hash/候选有效域及Capability/Parameters Revision对应当前快照；Benchmark不在UiSnapshot中，必须由Host证据Owner先CheckCurrent后送入，采用前再次核对完整输入；view不猜Benchmark“最新值”。过期保持Expired且禁止采用；仅替换Host有界候选表的投影，候选硬上限1024且计MetadataBytes，容量不足拒PA-010不保留旧可采用项。采用候选仅调用SetDraft的新副本，Host批准后显式Apply新Revision；额度建议不能自动重建会话。表格显示“候选线率/所需缓冲/证据来源/已过期”，不显示“最优”或“保证达标”。所有UI资源增加Advice.Suggested/Rejected/Expired及LineRate/Buffer/Source短键，zh-CN为“参数建议/无法建议/建议已过期”，zh-TW为“參數建議/無法建議/建議已過期”，en-US为“Parameter advice/Advice unavailable/Advice expired”；未知建议不复用旧Selected。

WPF为独立可嵌入控件DLL，工程/namespace/TestHost及公开projection接口已在Core binding/§8.0冻结，指导内容已由主控接收，无新增内部设计欠账。实际WPF资格/平台接线未验，PA-U仍PreparationIncomplete/NotReady，不授ImplementationSpecificationReady。只经Host授权桥及窄viewport port，宿主切语言，关闭只结束显示、不Stop/Close共享session。

仅固定**1920×1080屏幕基线**，扣OS任务栏、边框/标题栏/状态栏，以实际client rect校验，不改显示设置，不跑窄窗/其它分辨率。设计初值顶部56任务带/底部28状态带、左约220树/右约300参数，中间图像/轮廓主区优先；尺寸不是现场DPI结果。主区可独占DocumentGroup，高级栏折叠，不能仪表卡片挤掉影像。

- DockLayoutManager：中央DocumentGroup（轮廓、强度、位置曲线）；左TreeListView（设备→头→批次），右TabbedGroup（实际值、草稿、诊断）。宿主SaveLayoutToXml，恢复布局不恢复设备动作。
- GridControl+TableView：可折叠批次明细，过滤只改变投影；DataControlBase.SelectedItem双向绑定单一VM选择，SelectedItemChanged→§8.0 SelectAsync联动批次→序号→viewport/强度/ChartControl；语言/update不回发选择命令。旧epoch来源标识且拒绝绑定新run，不发设备命令。
- PropertyGridControl.SelectedObject/PropertyDefinitions：草稿按能力渐进显示；Apply前请求/实际差异，读回前禁Start。运行中编辑草稿可以保留，但Apply禁用并说明原因。
- ChartControl/XYDiagram2D/LineSeries2D：用真实索引/实际位置横轴；invalid/缺线断线、标范围，不跨空洞连线；刷新上限来自UI Profile，preview latest-wins且独立Owner。
- SuperTip：顶部关键命令用BarButtonItem，其继承BarItem.SuperTip挂SuperTip；Items内SuperTipHeaderItem/Item.Content分别绑定本地化命令标题及UiCommandState.DisabledReason/Tip（读取实际状态/限度/恢复），不显示裸异常。Start/Stop/Query始终显式可见，不为了视觉藏关键动作。参数验证同时在右栏UiParameterField.Warning显示，权限禁用/DrainUnknown有同一恢复文本。统一中性主题、数值单位对齐、清晰层级，状态同时用文字/图标；投影动效不延迟停止/错误。

### 8.2 角色、键盘、三语与反馈

操作者任务：查看实际身份/状态→启动冻结计划→看计数/缺口→停止或查询；调试角色才编辑参数/Replay，授权由宿主决定。Unknown主动作是查询原操作，禁止重复Start；DrainUnknown显示Owner/未归还数，不显示完成。

Tab顺序：身份→主命令→批次→主图/曲线→草稿。Enter只执行聚焦合法命令；Esc退出编辑/浮层不默认停机；Space选行、Ctrl+C复制诊断身份。UIA Name/HelpText本地化，预览不跳焦点；状态不能只靠颜色。宿主切语言保持run/batch/草稿/选择/operationId，不重发命令。

| 键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Title | 轮廓采集 | 輪廓擷取 | Profile acquisition |
| Start | 开始采集 | 開始擷取 | Start acquisition |
| Stop | 停止采集 | 停止擷取 | Stop acquisition |
| Query | 查询状态 | 查詢狀態 | Query status |
| Apply | 应用参数 | 套用參數 | Apply parameters |
| DrainUnknown | 资源尚未释放 | 資源尚未釋放 | Resources not released |
| Gap | 轮廓缺失 | 輪廓缺失 | Missing profiles |
| Replay | 回放数据 | 重播資料 | Replay data |
| CleanupTip | 查询原操作。资源释放前不能重新启动。 | 查詢原操作。資源釋放前不能重新啟動。 | Query the original operation. Restart after resources are released. |

所有参数、单位、枚举、错误/权限/提示/恢复均资源化，不只按钮。视觉与可用性分开验收：固定viewport三语不截关键身份/状态/安全动作；真实键盘、UIA、当前DPI、保存布局、离页/重挂载/慢UI不影响完整流；不以XML/截图代替WPF行为验收。

## 9. 双视角场景及必需断言

以下为合成协议夹具，不是现场结果。Core Owner与外部消费者分别走输入→动作→输出→资源→恢复，所有ID为必需断言。

| ID / 输入来源 | 操作/结果/资源断言 | 消费者反例与恢复 |
|---|---|---|
| PA-T01 单头100条×32 I16，计划100，Simulation | Open/Discover/Apply读回/Arm/Start→逐条→Complete→Stop/Close Released；100序号、0缺项、0持有；Arm adapter调用=0 | 两Host同内容hash，读回未知不能启动 |
| PA-T02 空ID/头/格式、0目标/预算、NaN/Inf | 校验拒绝、adapter动作0、不分配run/buffer；非法Create异常 | 修输入，不用首头或0Hz默认 |
| PA-T03 空源/99条缺42 | InputEnded确认→Incomplete/缺全范围或42；未知尾部→Unknown，不前移 | 保存证据，重采须Host新run |
| PA-T04 收齐但全哨兵/NaN/遮挡 | Structure Complete、InvalidElements正确并集、原码保留、位置独立 | 无效不归0，质量另判 |
| PA-T05 错scalar/endianness/layout、溢出/超payload | Rejected不进重建；有保全则原件可存，无分配则只有缺口；0越限分配 | 不取第一候选，不显示未保全原件已保存 |
| PA-T06 重复/异内容/逆序/错头/批/epoch | 完全重复一次交付；冲突隔离非Complete；旧epoch不推进新run | 超窗口Unknown，不能silent吞掉 |
| PA-T07 Y=0/1/3mm；模256 raw250→3，MaxStep10 | 位置原样；步进+9；半模128/超10/reset无段号Unknown | CommandOnly非Observed，未知时钟不跨头同步 |
| PA-T08 1000条/2slots、超大长度 | 可暂停源暂满保同一原输入有限重试，未Copied才能重试，收齐后Complete；不可暂停满或单条超总预算固化缺口并停；实分配峰值≤限制 | 不整批持Profiles；慢preview不持Core buffer；CannotPause不得假成功，不能无限重试 |
| PA-T09 两event reader、慢UI、复合sink | 独立游标广播、ring过期EventGap；preview覆盖归还；子Task全结束才释放 | 移除UI不Stop；一个子Task异常不丢另一个borrower |
| PA-T10 部分配置/仅ACK/能力revision变 | ConfigurationPartial、Arm拒绝；运行中Apply无动作；新能力使旧参数失效 | Query原实际值，不silent换格式/latest |
| PA-T11 operation同内容/异内容/未知Start | 同ID不二发、异内容PA-016、新ID重复Start拒绝；ACK无Activity证据仍Unknown；原query在途并发观察合并不另发 | 业务账本满仍保2个Stop/Close额度，查询计数Unknown的0不证明归还；已用RunId墓碑满拒新Arm不靠淘汰绕身份 |
| PA-T12 Cancel/deadline/adapter或sink抛错，业务异常叠cleanup同步/异步异常 | Factory前Root预留，失败0构造/动作；原Execute/Drive/Stop/Close/Query/Dispose及身份立即保存；独立cleanup/绝对wall期限；Task fault不证明Released | 两Host嵌套finally不漏Close/Query；业务与cleanup错误都已消费仍退出非0；Factory无返回且无后台资源仅释放空槽，否则留槽 |
| PA-T13 Stop/Close/Cancel并发、native卡住、迟到Close及未知/faulted Dispose | 原Close/Dispose仅一次，未知强持原Task/全部对象；先断言未退槽/无终态，再闩锁释放迟到Close/Dispose、Query Released/ConnectionReleased及全部错误消费才退槽 | 同一在途Dispose不可二发；同步Close/Query错误不丢Owner；Dispose故障不认资源释放且保故障槽，即使Task已结束 |
| PA-T14 Continuous长稳/缺区间爆量/溢出/断连 | metadata/摘要/去重有界，截断Unknown/受控停，旧epoch隔离 | 无自动重连采集，历史归Host不无限缓存 |
| PA-T15 Replay/版本/回退及规范编码 | §3.4两个oracle独立字段重建/长度/hash一致，完整receipt/run/batch/event roundtrip；未知enum/version、截断、尾多余字节、超集合/null/Phase资源冲突拒绝 | old v0.2不能当v0.3；same source/身份快照batch hash稳定，新run比较内容hash；旧数据只读，不盲重发 |
| PA-T16 两Host异常/归档失败，恢复移交拒绝/容量满/通知失败/确认迟到 | 完整session/adapter/buffers/sink/Profile/原Task/身份/资源包先由接收Root预留绑定再Accepted；原Root确认前强持，拒绝/故障保原根，禁止新会话；迟到回执按token对账不重发 | 同时双强持允许但唯一归还Owner；未释放移交不让Host成功0；Viewer成功非保存/质量成功；所有原Task结束+错误消费+资源查询确认才退槽 |

PA-T12/13/16分别在Archive和Inspector Host执行，故障组合不仅测单一异常。测试Root容量拒绝发生在Factory前，weak reference/计数断言未知对象仍强持；成功移交只确认接收责任、不能用弱引用GC证明buffer/native已归还。真实watchdog到期仍非0，保持原Owner记录供测试外层诊断。

本轮针对全部规划范围补充以下必需断言；既有PA-T01..T16/编码oracle有效结果复用，不为补充重新全审已接收切片。这些是确定Golden规格，尚非C#运行结果：

| ID | 合成输入与逐字段期望 / 恢复 |
|---|---|
| PA-X01 拆行/原序号 | 一个block两行、Width2/I16 LE/PixelStride4/RowStride8，Payload=`01 00 aa bb fe ff cc dd 03 00 ee ff 04 00 11 22`；原row.Sequence=10/12、Y=0/3、RawCount=250/3；每packed rowSpan6、payload依次`01 00 aa bb fe ff`及`03 00 ee ff 04 00`，不复制块末padding，原顺序10/12且缺11，不改Y；合法sink ReadElement给1/-2/3/4、RawBits低16位保留；完毕原block归一次 |
| PA-X02 模态/解码/质量 | ProfileImage Rows2不是两个机械profile；block格式非Line拒绝。BigEndian I16 `ff ff`→RawBits65535、Value-1；F32 NaN及哨兵→Value=null/Invalid；已标定高度raw10/Scale0.1/Offset2→Value3mm，Calibration缺失不获表面资格；pixel和强度各单位不混 |
| PA-X03 原reader/源配额 | Replay stream返回body原reader卡住，Stop/Close wall到期→SourceDrain Unknown/原Task强持，0新Read；晚到租约归同Root再Query counters0/Released；Reader成功但lease未Dispose仍不Released；maxBlockBytes/bodyLength/SourceBytes/metadata越限动作前拒绝，无大数组偷分配 |
| PA-X04 源codec/恢复 | 正常header+Frame/Signal/End逐条checksum及EncodeRecord→DecodeRecord→reencode一致；空file、无End、损坏SHA、超列表、未知version、End后尾bytes拒绝；旧epoch/跨head/窄count回绕未知不拼新run；非0 FirstSequence保持原Sequence；Replay不自动rewind，也不执行归档中的设备命令；Software缺关联拒绝、重复索引不二推进；Simulator不支持的触发/单位域拒绝 |
| PA-X05 双Host与超大批 | Archive/Inspector两Host各装配公开ProfileSourceFactory，1000条/2 Core slots/1 source reader/1 lease有界推进；input source块上限与总batch独立；原输入丢行双方ContentHash/Missing一致，Preview不持完整reader；source.Close/Session.Close两原任务异常均保存/迟到归还 |
| PA-X06 Advice容量 | §7.5 H1/1000及500Hz/hold1ms→Selected1000/N2/B128；hold2ms→Selected500；1000Hz下一binary64数+hold1ms的精确乘积略>1，W2/N3不能错误算W1；全超current但fits ceiling→Rejected无Selected；AllSamplesReleased=false拒绝；空/NaN/1025候选/negative metadata/overflow拒绝，无Apply或自动扩容 |
| PA-X07 Advice版本及UI | 任一Capability/Parameters/Benchmark Revision变→Expired/Selected=null原hash保持；Host SetAdvice显示独立候选不改Actual/Run/权限；采用只写新draft，Host显式批准Apply；拒绝/过期三语短句，关闭投影仍不Stop/shared session |

Golden只是本模块协议/字节/单位/资源的可判定真值；客户标定标准件高度、公差、漏检误检及电气触发没有这些合成值证明，不造现场Golden。ProfileRowDecoder的打包跨度、量纲传播、Advice精确ceil及Source晚到归还均需上述assertion完成后再报实现通过。

新增独立Source End编码oracle（与既有72/134byte Core oracle分开）：Kind=End(2)、Frame/Signal=null，body为44bytes、hex=`1300000070612d736f757263652d7265636f72642d76310b00000070612d6170692d76302e33020000000000`、SHA-256=`727e12abcc0c8048475a90f9c3ed7ce8632fdac054ffaa82df857845d4948d8c`；容器record另加uint32长度44及raw32摘要。本轮内存复算只证字段/字节规格，未来两个Host须从字段独立生成并往返，不能只hash这里的hex冒充实现测试。

可选WPF TestHost必需断言（仅实现后执行；不把Core Exe替代真实WPF）：

| ID | 真实WPF及Host端口输入/断言 |
|---|---|
| PA-U01 | STA Factory前Root预留→Create/Bind首快照/订阅→选择→关闭；无设备命令自动发出；无隐藏窗口初始化；非法limit/language/Binding拒绝无动作 |
| PA-U02 | Grid.SelectedItem联动选定同Batch/Sequence/plane，viewport/Chart同身份；迟到旧generation和旧epoch不得覆盖；Gap触发一次有限GetSnapshot，原Task保留 |
| PA-U03 | PrepareRequest给齐完整Command/Context或明确失败零动作；Denied/状态冲突/双击同RequestId/同ID异内容/仅ACK配置：Host调用时重核权限，同ID一次原Command；草稿/语言不Apply，缺计划不猜Arm；UI规范snapshot/reply/close/request编码一致 |
| PA-U04 | preview2个lease/128bytes，64bytes复制源立即覆写不影响preview；latest覆盖、两borrower及budget拒绝；Present卡住→Close Unknown保lease，闩锁释放→归原Owner→Clear；invalid断线不补0 |
| PA-U05 | 两view共享Host/store、各自viewport，关闭一个只解除自身显示；subscription/view/store原Close Unknown后QueryState/QueryProjection确认迟到归还，无再Close/Clear；Case中0设备Stop/Close动作，异常保Root，清latest后store字节归0 |
| PA-U06 | 固定1920×1080测得client rect、三语/当前DPI/键盘焦点/UIA/布局恢复；关键身份/状态/Start/Stop/Query可见，SuperTip与差异提示挂接；切语言不改requestId/run/选择/草稿 |

UiLimits TestHost合成值：SnapshotRows=8、UpdateRecords=16、PreviewLeases=2、PreviewBytes=128、MetadataBytes=1 MiB、OriginalTaskSlots=32、RefreshHz=10，Observation/Cleanup=1秒；测试用64byte line及可控viewport闩锁。不是生产UI刷新/内存目标；图像输入较大须消费者Profile显式预算，不能静默扩大128bytes。

HALCON空结果、缺pose、xz忽略pose、短输入旧尾、无三角面是重建适配消费反例，本模块只证传递/拒绝伪单位，不伪造HALCON执行。真实触发/编码器/时钟/标定误差、断电/温漂/长稳/节拍另做HIL/Golden/现场门。

## 10. 验证和BenchmarkProfile

### 10.1 纯Core Exe执行

测试工程Microsoft.NET.Sdk、net10.0、OutputType=Exe，**无PackageReference、仅Core ProjectReference+BCL**。默认执行PA-T01..T16及PA-X01..X06（PA-X07显示部分归WPF TestHost），case10秒/suite120秒、外层进程180秒真实wall watchdog；任一失败、未完成、超时或必需项跳过均非0且列ID，全部断言完成/资源归还确认才0。新增范围延续同有限预算，不扩大套件期限；协议计时用可控虚拟TimeProvider，wall watchdog独立，不推进模拟时钟使挂起假通过。dotnet test空结果不能替代Exe。

计划命令（工程未创建，本轮未执行）：

```powershell
dotnet build src/Modules/profile-acquisition/Asun.Modules.ProfileAcquisition.Core/Asun.Modules.ProfileAcquisition.Core.csproj -c Release
dotnet run --project tests/Modules/profile-acquisition/Asun.Modules.ProfileAcquisition.Core.Tests/Asun.Modules.ProfileAcquisition.Core.Tests.csproj -c Release
dotnet run --project tests/Modules/profile-acquisition/Asun.Modules.ProfileAcquisition.Core.Tests/Asun.Modules.ProfileAcquisition.Core.Tests.csproj -c Release -- --host archive
dotnet run --project tests/Modules/profile-acquisition/Asun.Modules.ProfileAcquisition.Core.Tests/Asun.Modules.ProfileAcquisition.Core.Tests.csproj -c Release -- --host inspect
```

Unknown fixture用闩锁先保持任务未完成、断言资源强持/禁复用，再显式释放并断言迟到归还；不能留下永远挂起Task后返回0。benchmark另用--benchmark及已采纳Profile有限计划，不能偷偷放宽默认suite期限；外层杀进程是失败，不证明设备排空。

WPF TestHost沿case10秒/suite120秒/进程180秒受控执行PA-U01..U06及PA-X07显示部分，全部必需断言完成才0。其STA Dispatcher用于真实UI处理，协议虚拟TimeProvider与wall watchdog仍分开；harness不能因Dispatcher已退出而丢Root中的原Present/Close任务。命令（本轮未创建工程/未执行）：

```powershell
dotnet build src/Modules/profile-acquisition/Asun.Modules.ProfileAcquisition.Wpf/Asun.Modules.ProfileAcquisition.Wpf.csproj -c Release
dotnet run --project tests/Modules/profile-acquisition/Asun.Modules.ProfileAcquisition.Wpf.TestHost/Asun.Modules.ProfileAcquisition.Wpf.TestHost.csproj -c Release
```

### 10.2 模块测量定义

公共统计及失败/删失处理只引用 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)，不复制分位公式。

Benchmark runner输入为Host消费者Profile，不新增Core DTO：Profile ID/revision/hash、Core/adapter/format版本、fixture原字节/manifest hash、头数/样本/planes/位深/stride、批数/行数/速率/并发、sink延迟/故障、预算/资源、冷热/预热/测量/最低有效样本数、目标及来源。缺负载字段拒绝；缺目标允许诊断测量但NotEvaluated，不编1ms/100ms/2s/512MiB生产门槛。

| 测量项 | 方法与计数 |
|---|---|
| 负载 | 单/双头独立批，code/mm/image域；能力最大样本、8/16-bit强度、padding；1000条/2slots；可暂停/不可暂停、正常/慢sink/Cancel/断连 |
| 冷热 | 新进程/新session首Open→首条为冷；显式Profile预热后热测，预热不进分位；版本/hash冻结，不复用旧资源 |
| 阶段 | TryAccept进入→Copied/Refused；复制/校验/hash；sink调用→原Task结束；最后条→BatchSealed；Stop接纳→InputEnded；Cancel→真实排空→最后归还 |
| 端到端 | Arm接纳→ResourcesReleased，覆盖Start/采集/封口/清理；另测Open/Apply/Close原请求→对应资源屏障，不能只统计最后条封口 |
| 资源 | 实分配buffer/slots、metadata/去重/摘要/event/ledger峰值、callback/原sink任务；Host存储/adapter/native另列；逻辑归还与GC/RSS分开 |
| UI投影 | Host已采纳UiLimits/preview尺寸/格式/viewport版本及hash、选择/update/权限频率/慢viewport/双view；Bind接纳→CloseProjection全任务及预览归还，另测复制→真实Present原Task结束、语言/selection延迟；Root/原Task/store实际bytes峰值及Unknown独列，不用界面刷新FPS代替生产完整输送 |
| 逐行/Source/Advice补充 | 固定block.Rows/Width/stride/byte域/hash/row stamp数量及maxBlockBytes、source.MaxRecordBytes/SourceBytes；测原producer获得块→每row Pack/TryAccept→原reader及源lease归还，Source与Core/preview总峰值分开；Advice固定候选1/1024、heads数/证据hold与实际bytes，测Suggest执行/分配及ExactCeil边界拒绝。时延目标仅消费者Profile，不用文档合成N2证明现场节拍 |
| 结果 | P50/P95/P99/n、吞吐/拒绝/缺项/重复/invalid；失败/timeout/删失/Unknown及资源终态独列。阈值仅采纳Profile；DrainUnknown不得性能通过 |

容量按正在持有条数×单条所有planes/padding/暂存/实际buffer容量，所有乘加checked；不要求整批常驻。估算与测量并列，漏实际分配计账即失败。模拟吞吐不证明实际传感器线率/客户节拍。

## 11. 版本、发布与剩余门

SemVer：单位/布局/所有权/hash/结构或未知终态破坏兼容为MAJOR；可忽略可选能力为MINOR；不改语义修复为PATCH。本文Core v0.3/WPF v0.2是设计基线，旧示意合同不是已部署对象；编码版本显式变化，不把新字段塞旧v0.2 bytes。run冻结模块/adapter版本、source、能力/参数/格式/标定Revision；旧Replay保留原schema/hash，不重算身份冒充兼容。

升级前禁新run，对账原Task/资源并测旧Replay只读；未知设备动作隔离先Owner对账。回退旧包/配置，不重发未知Trigger/Start，不改旧batch。纯Core发布需要本页合同、Simulator/Replay、两Host及必需断言真实结果；设备版另需对应Profile/SDK/HIL。未实现不提前堆交付报告/包。

| 门 | 尚缺与影响 | 不阻断 |
|---|---|---|
| 完整范围文档准备 | PA-C1～C4/PA-U既有接收保持。本永久会话已补§4.4、§7.4～7.5逐行/源适配/Advice及全能力错误/测试、并自行内容自审/定向文档验证；当前批准范围无剩余可决定软件设计欠账，结论见§12。权威代码基线仍待实现前绑定，未创建工程 | 不等待总控代审；总控仅接收本结论/协调跨Owner，不以指导完善提高代码或运行资格 |
| 平台真实接线 | 本模块已冻结buffer/adapter/viewport及源reader消费端口/字段映射/拒绝条件；共享frame Owner与IM-063设备Owner各实现其公开桥，平台Contract Owner完成宿主正式映射，实际接线未验 | 已接收Core和本轮补充逐行/Advice可独立合成验证；具体SDK事实不是由本模块补造 |
| 可选UI实现验证 | PA-U指导内容已接收，无新增内部设计欠账；真实25.2.3编译/运行、1920三语键盘UIA/性能及平台接线未验，仍PreparationIncomplete/NotReady，不能由Core门授ImplementationSpecificationReady | 属后续实际资格/接线验证；共享viewport具体桥遵守本页固定port，不倒逼Core/UI补新DTO |
| 真实设备 | 型号/格式/无效码、Trigger/Encoder reset/clock、native Stop/Close/Query及反压证明来自设备Profile | 协议模拟/软件资源反例 |
| 物理资格 | 单位/标定/间距容差/同步误差、原始Golden、节拍/长稳/HIL及现场值 | 结构完整/原始证据，不等于测量或生产通过 |

外部门仅阻断依赖它的切片。Arm/Start分开、空源不完整、预算显式、采集Core不重建等本页工程选择已确定，不反复留常规架构裁决。


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

## 12. 六项逐切片定位与自审范围

下列六列对应DEV-GOV-010 §3.1。**PA-C1～C4均已由主控内容接收为ModuleCoreImplementationReady（仅托管规格，真实标定未验）**，既有接收保持；主控此前已独立逐字段重建72bytes CloseCommand/134bytes LookupUnknown receipt，完整hex/hash与正文一致，仅证明编码规格。PA-U指导内容已接收，无新增内部设计欠账，实际WPF资格/平台接线未验仍PreparationIncomplete/NotReady，不授ImplementationSpecificationReady；PA-I保留真实共享Owner/DeepSight/设备/标定字段映射门。整模块PreparationIncomplete，规格接收不等于代码/性能/生产验收。

2026-10-11补充范围结论：本永久原会话按架构IM-040/PKG-057全部批准采集能力（含未标代码Ready的Adapter/UI/恢复/有界参数建议）执行内容自审，**全模块可决定软件设计闭合，无待后续编码者决定的算法/API/Owner/默认或恢复顺序**。既有接收不重复审算；新增逐行解码/可发布source/Advice的六项定位在下表，状态是文档准备SelfReviewed、未授额外代码Ready/整模块ImplementationSpecificationReady。总控仅接收状态，无需另一次总控内容复核；产品实现必须继续按DEV-GOV-010及当前代码授权/实际资格门执行。本文内的模块状态PreparationIncomplete仍指未实现/未运行/真实接线资格，不能反向读成软件设计仍空缺。

| 切片 | ①职责/消费者 | ②精确API/资源 | ③无UI宿主 | ④反例/恢复 | ⑤Benchmark | ⑥唯一路径/后门 |
|---|---|---|---|---|---|---|
| PA-C1 值/布局/位置证据（ModuleCoreImplementationReady：主控已接收托管规格） | §1、§2.1 | §3.1～3.2、§4.3 | §7纯校验 | T02/04/05/07/15 | §10.2布局/hash/分配 | Core binding、§10.1；实际标定后门未验 |
| PA-C2 会话/命令/账本/查询（ModuleCoreImplementationReady：主控已接收托管规格） | §1.2、§3.3 | §3.1/3.3～3.4精确回执/Activity/错误/编码，§5～6；cleanup保留额度/Query合并、原事件Gap/游标 | §7.1全部原Task→嵌套finally，Close State可查询 | T01/10～13/15，72/134bytes oracle；故障不作释放 | §10.2原请求→资源、Unknown单列 | 同唯一Core/tests及§10.1命令；持久平台桥另接，非Core依赖 |
| PA-C3 输送/批次/资源（ModuleCoreImplementationReady：主控已接收托管规格） | §1、§4 | §3.1/§4最终invalid、复制/借用Owner、有界排序/hash/封口 | §7 sinks/Root与§4跨deadline强持 | T03～09/12～14/16；可暂停重试与不可暂停缺口区分 | §10.2实bytes/metadata/端到端 | 同唯一Core/tests；共享frame/重建只接固定port，真实物理资格另验 |
| PA-C4 Simulator/Replay/两Host（ModuleCoreImplementationReady：主控已接收托管规格） | §1.1、§7 | §3 port/§7冻结Root额度/Task算法/移交与结果退槽 | §7.1～7.3全部Factory前到最后Dispose闭包 | T01～16全必需；正常/迟到/faulted释放/拒移交各有断言 | §10.2固定fixture/冷热/删失 | 唯一tests Exe内模式/§10.1，非HIL，不建产品恢复库 |
| PA-I 设备/共享帧集成（指导SelfReviewed，实接未验） | §1.2/§4.4/§11 | §3固定port及§4.4字段解码/校准/NativeReader映射责任 | §7.1 Root、§4.4逐row bridge、§7.4 source | T05～15/X01～05+真实HIL | §10.2 source/native/总峰值/物理Profile | 本模块Core/Adapters目录仅放消费算法；IM-063等原设备模块持SDK桥，禁止本会话改其代码/指导 |
| PA-U 独立WPF（指导内容已接收；PreparationIncomplete/NotReady） | §8.1～8.2角色/任务/两view | §8.0 WPF v0.2全部DTO/Prepare/授权/codec/投影查询/lease/viewport及本地化结果，无新增内部设计欠账 | 同Core；Factory/Bind无设备IO，Host给齐命令，关闭不Stop | U01～U06/§7原Root，真实1920/25.2.3 TestHost及平台接线未验，不授ImplementationSpecificationReady | §10.2 UI实bytes/原PresentTask/投影闭合及Unknown | Core binding唯一Wpf/TestHost、§10.1；Core不引DX，自有接口全定义；实际设备/物理资格外门 |

| 同原范围补充（文档SelfReviewed，未授代码Ready） | ①边界/消费者 | ②API/Owner/单位 | ③无UI调用 | ④反例/恢复 | ⑤Benchmark | ⑥唯一路径/门 |
|---|---|---|---|---|---|---|
| PA-L 逐行解码/聚块消费 | §1/§4.4；2D intensity与3D height及Image分界，两Host | BorrowedScanBlock/ScanRowStamp/Decoder全公开、原producer与packed行Owner、标量/单位/invalid | 源bridge Validate→Slice/Pack→TryAccept→ReadElement→归还 | X01～03/05；stride/缺行/坐标/晚到/超块 | §10.2 block→每row→源归还/总bytes | 唯一Core/Adapters与唯一Core.Tests；SDK类型/物理单位事实仅原设备Owner |
| PA-S 可发布Simulator/Replay | §7.4独立source、非Vendor SDK | SourceFactory/RecordLease/InputCodec/SourceDrain及原reader预算/协议 | Factory纯构造→Adapter→同session/sink两Host | X03～05/原T12/13/16；损坏/无End/晚到/双Close | §10.2 source峰值/冷热/删失 | 唯一Core/Sources及Core.Tests，不机械新增DLL/报告；真实存储stream由Host Owner |
| PA-A 有界Advice | §2.1/§7.5，只工程建议不Apply/放行 | Advisor/证据/候选/精确ceil/过期/三语投影 | Suggest→CheckCurrent→Host显式草稿/批准Apply，同原Core | X06/07；证据缺/容量/溢出/版本/未归还 | §10.2候选数量/精确边界/资源实测来源 | 唯一Core/Advice、Wpf投影及原tests/TestHost；不造客户/设备阈值 |

剩余Owner及实质验收：本模块Owner在获准实现时完成以上C#/BCL与真实WPF TestHost、Golden/异常/Benchmark，不由现文档替代；IM-063或选定设备Owner提供官方格式/原timestamp frequency/encoder reset及native Stop/Close/排空证明并HIL；坐标/标定及重建Owner提供Calibration引用对应几何/单位/实际位姿与转换资格；共享帧/viewport Owner实现本页固定窄port、Host Owner持原Root/存储stream/授权与跨模块装配；客户/工艺Owner提供真实标定标准件、公差、同步误差/节拍验收Profile。物理事实未给则精确阻断依赖切片，不阻断纯Core/解码/Replay/Advice软件规格；运动/发光/质量放行与学习型自动优化仍不属于本模块。

本轮仅本文件合同闭合、两Host正常/失败/Unknown资源链、正文矛盾及Markdown/本地链接做两轮定向自审，不整仓全审，不新建报告/脚本/测试或产品代码。引用已查证来源；检查结果按实际执行，不将此段当自动PASS。

2026-10-11实际文档验证：两轮定向结构/引用检查通过；本页18个本地链接可解析、代码围栏成对、公开类型声明无重复，新增API类型/错误键及T/X/U验收ID闭合。内存脚本完成新增拆行字节、有符号/端序/单位、Replay字段解析/容器长度及checksum/损坏拒绝、Advice binary64精确ceil共33项断言，并另核End44字段反解重编码/hash及Simulator调度例值；未写脚本/测试文件，未重审既有72/134bytes已接收向量。以上只验证文档规格，尚未执行C#构建、真实WPF/HALCON、Golden运行、Benchmark、HIL或现场验收。
