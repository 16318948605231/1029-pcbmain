# 图像帧与大数据资源独立模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`CPU三切片, GPU v0.1`

- 模块：`image-frame`（中文名称：图像帧与大数据资源）
- 模块 ID：`IM-006`；现有来源：`PKG-006`
- 文档版本：`0.3.3-prep`；状态：`DesignReview`（2026-10-11 全部批准范围文档准备收口，运行资格未验）
- 目标运行时：C# / .NET 10；视觉后端适配目标：HALCON 26.05，经项目已批准的 `ImageLibDotNet` 公共接口接入
- 规划消费者：相机采集、视觉算法、Replay、Viewport；第二消费者验收最少覆盖相机适配器与 Replay/算法宿主各一套
- 本文是独立模块的唯一实施指导。首片 `ManagedLayoutValidation` 的当前规格为 Core API v0.2；进程内复制发布/租约为 §4.3 Resources API v0.1；三个CPU切片及GPU v0.1托管协调/Simulator已接收为 `ModuleCoreImplementationReady（规格准备）`；HALCON/IPC v0.1为“适配设计已接收（规格准备）”，接收边界见 §16/附录 A。平台 Frame Schema 不反向定义模块 API。本文不声称代码已实现、已编译或生产通过。

## Core implementation binding

- 准入路径：`NewProjectRequired`；当前首片只针对纯托管布局/平面/域/预算验证，不包含不可变存储、Tile、Lease 或事件服务。
- Core 工程：`src/Modules/image-frame/Asun.Modules.ImageFrame.Core/`；namespace：`Asun.Modules.ImageFrame.Core`。
- 测试工程：`tests/Modules/image-frame/Asun.Modules.ImageFrame.Core.Tests/`。
- 只在实现切片开始时创建。首片只引用 .NET 基础类库及 `System.Collections.Immutable`；HALCON、AsunImage、相机、GPU、文件、IPC、WPF、数据库和报告代码均禁止进入首片。

## 首片 Core 范围与后续切片边界

首片名称为 `ManagedLayoutValidation`，只接收托管值并返回确定性的验证结果：尺寸、plane 布局、stride/offset 访问范围、有效域行段和有来源的预算。它不取得、拥有、复制或释放任何像素；不发布 Frame，不打开文件，不调用 native，不创建异步工作，不维护 lease/cache/event 服务。

以下能力必须作为后续独立切片，不能为了让首片“看起来完整”而把未决 Owner 或适配器签名塞进首片：

| 后续切片 | 首片禁止内容 | 开工前新增门 |
|---|---|---|
| Storage/PixelProvider | allocation、裸指针、`HObject/HImage`、相机环形 buffer、复制策略 | 进程内复制与租约按§4.3接收；HALCON/零拷贝另按适配门 |
| CrossProcessLease | IPC handle、共享内存、跨进程 lease、强制终止恢复 | IPC Schema、进程 Owner、权限/租约回执、`DrainUnknown` 语义 |
| Tile/Cache/Pyramid | tile 读取、LOD、halo 扩展、缓存对象、GPU 副本 | 模块端口/缓存Owner按§7接收；算法层、GPU与正式平台映射另关门 |
| Event/OperationService | 异步事件、请求回执、取消、超时、排空和重试服务 | 进程内回执/事件按§4.3接收；IPC 实例内回执见§19.2，不承诺跨重启持久回执 |
| HALCON/AsunImage Adapter | 任何 `ImageLibDotNet` 类型或未验证的 native 签名 | 目标程序集公开签名、HALCON 26.05 页面、适配器资源测试 |

### 后续跨进程资源切片的来源增量（DEV-ARC-007，限本职责）

只读复核 `H:\docs\40-development\00-standards\共享内存单消费者租约协议开发指导.md`（SHA-256 `8e2af5a210cc7d15d068da92e1925521620f502d7705da9a821fa8e023e5f4bb`）后，确认以下内容优于当前抽象，纳入后续 `CrossProcessLease/Storage` 切片的约束；它们不进入首片 `ManagedLayoutValidation`，也不改变平台 Frame Schema/Owner：

1. **跨进程只允许显式 SPSC。** 一个共享段/slot 只能有一个生产者和一个消费者；算法、DataService、UI、回放等多消费者必须使用独立派生段、进程内受控资源或 durable staging 后的不可变引用，不能给同一 slot 增加引用计数来绕过回收边界。首片和进程内 Core 不受此 SPSC 约束扩展影响。
2. **身份闭包必须包含 endpoint epoch 和 generation。** descriptor/lease 至少绑定 `pair/segmentId + slotIndex + generation + producerEpoch + consumerEpoch + payloadLength + payloadHash`；进程 ID、文件名、板号、UTC 过期时间不能作为回收或身份依据。token/capability 不写共享内存或日志。当前复制主路的HMAC/可信绑定见§19.2；mmap/跨身份的ACL与能力协议不启用，不留作本版未定项。
3. **共享slot的状态只能原子转换。** 若未来批准mmap，候选状态为`Free → Writing → Ready → Reading → Released`，失败进入Poisoned。发布前完成header/payload/hash写入并以release语义发布Ready；消费者以CAS由Ready取得Reading后，以acquire语义读取并校验generation/epoch/长度/hash。校验失败隔离，不把slot直接回Free。状态观察用Volatile，状态所有权转换用CAS/等价已核原子操作，不以普通字段或仅内存屏障替代跨进程原子性证明。当前§19.2的逻辑slot由单个Broker门串行所有权转换，没有共享内存跨进程字段，不使用这套候选枚举。
4. **超时、心跳失联或 PID 消失不是释放证明。** 只有匹配的 Release 回执、受监督的进程退出证明 + quarantine，或整段停止并完成 generation rollover 才允许复用；未知状态必须 `Poisoned`/`DrainUnknown` 并背压或隔离，不能回池。`ResourcesReleased` 只有真实 Owner 观察到释放后才能发布。
5. **内存边界和降级必须有界。** segment/slot/总字节必须受来源明确的部署硬上限与消费者 Profile 约束；无空闲 slot 返回 `Backpressure` 并暂停上游，不动态创建无界段。共享内存协议不满足门禁时，后续切片可以回退为 chunked gRPC → durable staging → immutable reference，但不能为性能绕过生命周期和完整性不变量。

上述增量中的共享指针/CAS/进程监督回收只适用于未来获准的共享内存适配。当前§19.2复制主路没有远程映射；真实停止本方IO/CopyRow即可证明本方source借用退出，不声称证明对端native已释放。原文的 Windows DACL、服务 SID、控制 journal、具体 Protobuf/segment header、AOI 错误前缀、100 万次压力目标和生产启用结论属于来源项目/安全或部署 Owner；本指导不采纳为 image-frame Core API、平台默认值或本模块已完成证据。H:\docs 使用 HALCON 24.11 语境，未用于本模块任何算子或 `ImageLibDotNet` 签名判断。

首片与平台 Schema 的关系是“值验证后映射”：平台的 `FrameId`、来源、采集代、工艺语义、质量事实和数据库字段不进入首片 DTO；平台 Owner 负责把已验证值映射到自己的 Schema。首片 Validator 不拥有平台事实写权，也不替平台定义状态机。

## 首片准入状态

主会话已逐项接收 DEV-GOV-010 §3.1 六项文档规格：`ManagedLayoutValidation / Core v0.2`、`CPU CopyStorage/Lease / Resources v0.1`、`CPU Tile/cache 与纯值 Recommend / Tiles v0.1` 均为 `ModuleCoreImplementationReady（规格准备）`。该状态不表示已实现、已测试或批准本轮写产品代码，也不提升整模块状态。主会话已接收§19的六项文档规格：GPU v0.1托管协调/Simulator为 `ModuleCoreImplementationReady（规格准备）`，HALCON/IPC v0.1为“适配设计已接收（规格准备）”。HALCON/IPC不标为无UI纯Core或真实适配验收；真实D3D12 Owner/native SDK不在本模块本轮实现范围。整模块继续 `DesignReview`。工程落点明确是准入条件，提前创建空工程不是条件。生产资源操作无有来源的部署/消费者上限必须拒绝；纯 Core 可用显式标注的合成测试 Profile 验证拒绝/边界，不依赖客户物理节拍。性能目标未采纳时允许测量但为 `NotEvaluated`，不阻断无关纯计算规格的接收。

## 1. 目的与边界

模块负责大图像/高度场资源的结构描述、布局验证、不可变发布、只读租约、有效域携带、按需 tile/pyramid 读取和有界缓存。模块可在无产品 Shell、无 WPF 窗口、无隐藏初始化的宿主中运行。

调用方负责采集顺序、目标/板件/工单关联、坐标和工艺解释、缺陷或质量判定、证据提交、质量放行、设备命令、数据库事实和页面组合。模块不得包含 PCB、PCBA、SPI、AOI、点胶、涂覆等制程规则，不持有相机 SDK 句柄、产品数据库、ViewModel、质量状态机或全局可变资源。

当前全部批准范围的文档准备结论见§20：三个CPU切片及GPU v0.1托管协调/Simulator为 `ModuleCoreImplementationReady（规格准备）`，HALCON/IPC v0.1为”适配设计已接收（规格准备）”。真实D3D12 Owner/native SDK不在本模块本轮实现范围。实际编译、26.05 Golden/借用稳定性、真实跨进程、真实GPU/driver/fence/device-lost/峰值、正式消费者及物理资格全部未执行；整模块保持 `DesignReview`。

模块输出是资源事实和读取结果，不是检测结论。空域、缺测、Unknown、取消和超时必须显式返回；不得以 0、背景、空框或 PASS 替代。

### 1A. 新架构适配要点

**架构门禁**：`Asun.ImageFrame.Core` 及所有子程序集不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。CI 架构测试强制扫描程序集引用，违反即构建失败。

**Blazor/Web 宿主兼容性**：Core 不使用 WPF Dispatcher，所有异步操作使用标准 `Task`/`ValueTask` + `CancellationToken`，可直接在 Blazor Server 宿主中调用。当 Web 端需要展示图像时，由服务端按 tile 粒度传递 tile 字节引用，不将原始大图通过 SignalR 传输。

**AI 推理 Tiling 适配**：
- `ai-inference` 模块按 ROI 对大图分块推理时，通过 `RequestTileAsync` 获取每个 tile 的只读张量字节，租约在推理完成后立即释放。
- 推理模块不直接持有 `FrameLease`，只通过标准 tile 请求接口获取数据，避免跨模块资源所有权混乱。
- tile 的 `EffectiveDomain` 必须随 tile 字节一起传递，推理结果的坐标逆变换由 `coordinate-geometry` 模块负责。

**HALCON 备选策略适用性**：本模块不直接执行视觉算法，不涉及 HALCON/OpenCV 双跑。图像存取是基础设施，HALCON 备选 CI 在消费本模块的视觉算法模块（`features-2d`、`segmentation` 等）中执行。

## 2. 术语与不变量

| 术语 | 语义 |
|---|---|
| `Frame` | 一次不可变发布的多 plane 数据描述，含身份、布局、物理语义、域和来源修订 |
| `Storage` | 底层 allocation/native/GPU 资源及唯一释放 Owner；同一 storage 可有多个 lease |
| `Lease` | 一个消费者的持有权，幂等释放；释放后不能新开 read scope |
| `ReadScope` | 一次实际读取的短作用域；结束前 storage 不能归还，不能把裸指针/Span 带出作用域 |
| `Tile` | 帧或 pyramid 某 level 的实际半开窗口，带父坐标映射、有效域和 lease |
| `Pyramid` | 绑定源修订、实际尺寸、缩放/抗混叠方法和层级映射的派生资源 |
| `EffectiveDomain` | 样本可用域；不等于 buffer 可访问范围、业务 ROI 或算子支撑域 |
| `Revision` | 内容、布局、域、标定/变换或派生参数的不可变修订；缓存命中必须检查全部相关修订 |

必须保持：发布后不得写入；storage 归还恰好一次；lease/read scope 释放幂等；关闭后不从计数 0 复活；迟到结果不得覆盖新请求；未知结果不默认为成功。

## 3. 依赖、端口与适配器

首片只依赖 BCL 与 `System.Collections.Immutable`；后续进程内资源工程单向引用 Core，HALCON/File/IPC/GPU 适配工程单向引用 Resources。宿主负责组合与平台 Schema 映射，不要求引用任何平台程序集。外部端口仅由构造/请求显式注入，禁止静态注册表或服务定位器。

§4.3 的行输入端口是同步借用：宿主保证调用期间来源稳定，模块完成逐行复制后不再引用来源；设备 handle、文件 stream、HALCON 对象、GPU texture 和 Dispatcher 均不进入 Core/Resources 公共类型。原生零拷贝是另一适配切片，不靠 `ReadOnlyMemory` 的名称证明不可变。API 调用均不在锁内回调外部代码。

## 4. 强类型契约

### 4.1 统一单位与版本

Core v0.2见§4.4，Resources v0.1见§4.3、Tiles v0.1见§7；三个 CPU 切片均已接收为 ModuleCoreImplementationReady（规格准备）。HALCON/IPC v0.1公开契约见§19，适配设计已接收（规格准备）；GPU v0.1仅托管协调/Simulator为ModuleCoreImplementationReady（规格准备）。它们是本模块API规格，不是正式平台Schema或已编译声明。旧v0.1 Core不静默接受新字段；本文没有核验已交付包/实际消费者，实施前须按§15核对。旧`FrameIdentity/FrameLayout/StorageWriteSource`占位API不再作为入口；`FrameReadRequest`仅指§4.3的闭合类型。

身份使用非空 Guid，`FrameKey.Revision` 为 `ulong >= 1`，同一 Id 的新修订严格递增，耗尽时换 Id；RequestId 在服务 epoch 与回执保留期内绑定同一规范化请求摘要。ConsumerId/来源/修订字符串按 Ordinal 比较，UTF-8 1..128 字节，不 trim 或大小写折叠。坐标 x=列、y=行；整数中心坐标从 (0,0) 开始，窗口半开；字节量全部为 long，checked。单次行大小还必须 <= int.MaxValue，超过时只允许后续 chunk/tiled source，不能分配单个不可表示的 Span。

时间戳用于诊断，不用于寿命证明。有限等待参数为 TimeSpan 0..24h，0 仅观察现状、不发强制释放；期限使用注入 TimeProvider 的单调时间戳，同一次操作不延长。枚举未定义整数一律拒绝。公共状态、错误和事件不含制程 PASS/NG。

Timeout=0的新Publish/Read调用不接纳新工作，返回Rejected/Timeout；查询已有RequestId仍返回原回执。Release/Retire/Close的observationTimeout=0可提交关闭意图后立即返回当前观察，不强制释放；负值/超过24h返回Error=InvalidArgument且不改变资源状态。Create的ReceiptRetention/DrainTimeout、Tile SourceReadTimeout要求>0且<=24h。Query空Guid返回Unknown，不创建工作。计数/预算所有加乘checked；服务Sequence达到long.MaxValue时停止新接纳、保留清理及旧查询，不回绕覆盖事件身份。

### 4.2 像素、有效域与来源

Core 只验证结构，不扫描像素。Resources 携带每 plane 的单位/通道/值映射和有效域，`physical = raw * Scale + Bias`，Scale 为有限非零数、Bias 有限；强度/颜色/Mask 使用单位 `1`、Scale=1、Bias=0；Height 单位由来源明确提供，绝不从显示 LUT 推断。单位字符串是宿主已登记标识，模块不转换单位或坐标，也不定义工艺阈值。

所有 plane 共享 Width/Height；不同尺寸的高度、置信度或预览必须发布为不同 Frame，并携带显式映射，由宿主/坐标模块解释。每 plane 有独立 ValidDomain，与布局 Domain 取交集；共同 ROI 不替代各 plane 的缺测域。行段采用 §4.4 的规范排序，允许同一行多段；Resources 发布扫描有效域内浮点样本，发现 NaN/Infinity 返回 `InvalidSample`，不得自动填洞或扩大有效域。域外字节可存在但不能作为有效测量值；导出时单独携带域和无效原因。有限哨兵值/packed/压缩须由来源解码成标量和域后进入模块。选择多个 plane 读取时返回各自域，不偷取并集。

Metadata数必须等于Planes数，各Channels数等于ChannelCount，通道标识非空且在该plane内唯一。ValidDomain必须非null且按Core域规则验证；InvalidReason为空仅限Full域，带缺口/空域必须有来源原因键。Layout.Domain与各ValidDomain的Rows.Length先checked求和，与FrameBudget行段上限比较，再遍历内容，避免多plane重复扩大元数据工作量。PlaneMetadata中的原域与Layout.Domain交集为实际有效域；发布返回规范化交集，预算先同时计输入行段和新交集行段，不靠交集缩小绕过输入限制。

CopyRow可传输完整标量行（含域外原始值），调用者必须在解释样本时消费相应域；它不等于证据导出。导出必须同时保存域/无效原因，容器无法表达时拒绝，或由宿主显式产生带填充值标志的派生Artifact。源padding不传输，域外字节不冒充有效样本。

### 4.3 Module API Contract v0.1：进程内 CopyStorage/Lease

下列是唯一资源公开形状，全部在 `Asun.Modules.ImageFrame.Resources`。引用 Core v0.2，`FrameError` 是资源错误，不复用布局验证错误枚举。仅复制发布与 level=0 行/窗口读取可在纯 CPU 软件切片实施；HALCON、GPU、IPC 与显示金字塔不能为填充本接口而伪造成功。

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.ImageFrame.Core;
namespace Asun.Modules.ImageFrame.Resources;

public readonly record struct FrameKey(Guid Id, ulong Revision);
public readonly record struct PixelWindow(int X, int Y, int Width, int Height);
public enum FrameError
{
    None, InvalidArgument, UnsupportedFormat, LayoutOutOfBounds,
    BudgetUnavailable, BudgetExceeded, LeaseClosed, InsufficientSupport,
    Cancelled, Timeout, AdapterFailure, DrainUnknown, StaleRevision,
    Conflict, NotFound, Unknown, InvalidSample, Closed
}
public enum OperationPhase
{
    Requested, Validating, Rejected, Accepted, Reading, Draining,
    Drained, ResourcesReleased, Completed, Empty, Cancelled, TimedOut,
    Failed, Unknown
}
public enum DrainState { NotStarted, Draining, Drained, DrainUnknown, Isolated }
public enum LookupState { Found, NotFound, Unknown }
public enum ReadIntent { ExactSamples, Display }
public enum BoundaryPolicy { RejectMissingSupport, ClipAndMarkInvalid }
public enum ResourceEventKind
{
    OperationChanged, LeaseClosed, StorageReleased, Closing, Closed,
    Isolated, Diagnostic
}
public enum ResourceKind { Cpu, Native, Gpu }
// Stable physical identity; CPU Bytes equals the owning byte[].LongLength.
public sealed record AllocationCharge(Guid AllocationId, ResourceKind Kind, long Bytes);
public sealed record PlaneMetadata(
    string Unit, double Scale, double Bias,
    ImmutableArray<string> Channels, DomainDescriptor ValidDomain,
    string InvalidReason);
public sealed record FrameDescriptor(
    FrameKey Key, ManagedFrameLayout Layout,
    ImmutableArray<PlaneMetadata> Metadata, string SourceId,
    string SourceRevision, string CoordinateReference);
public sealed record ConsumerLimit(
    // Held bytes count unique allocations per consumer plus its pending byte reservations.
    // A closed lease with live scopes still occupies one lease slot.
    string ConsumerId, long MaxHeldBytes, int MaxLeases,
    int MaxActiveOperations, int MaxQueuedOperations);
public sealed record ResourceLimits(
    // CPU limit covers owned/borrowed tracked payload plus outstanding reservations, not CLR heap/RSS.
    BudgetLimit FrameBudget, long MaxCpuBytes, long MaxNativeBytes,
    long MaxGpuBytes, long MaxCacheBytes, int MaxFrames,
    int MaxActiveOperations, int MaxQueuedOperations, int MaxReceipts,
    TimeSpan ReceiptRetention, TimeSpan DrainTimeout,
    ImmutableArray<ConsumerLimit> Consumers);
public interface IFrameInputRows
{
    FrameError CopyRow(int planeIndex, int y, Span<byte> destination);
}
public sealed record CopyPublishRequest(
    Guid RequestId, string ConsumerId, FrameDescriptor Descriptor,
    IFrameInputRows Source, TimeSpan Timeout);
public sealed record FrameReadRequest(
    Guid RequestId, string ConsumerId, FrameKey Key,
    ImmutableArray<int> PlaneIndices, PixelWindow Window, int Halo,
    BoundaryPolicy Boundary, ReadIntent Intent, TimeSpan Timeout);
public sealed record OperationReceipt(
    Guid ServiceEpoch, Guid RequestId, long Sequence, OperationPhase Phase, FrameError Error,
    DrainState Drain, bool OperationResourcesReleased,
    DateTimeOffset ObservedUtc, Guid? ResultLeaseId);
public sealed record PublishResult(OperationReceipt Receipt, FrameDescriptor? Frame);
public sealed record ReadResult(OperationReceipt Receipt, IFrameLease? Slice);
public sealed record OperationLookup(LookupState State, OperationReceipt? Receipt);
public sealed record ReleaseReceipt(
    Guid LeaseId, FrameError Error, bool LeaseClosed, int DuplicateReleaseCount,
    DrainState Drain, bool StorageReleased, DateTimeOffset ObservedUtc);
public sealed record DrainReceipt(
    FrameError Error, DrainState State, bool ResourcesReleased,
    ImmutableArray<Guid> OutstandingLeaseIds, long RetainedBytes,
    DateTimeOffset ObservedUtc);
public sealed class FrameDrainException : Exception
{
    public DrainReceipt? Drain { get; }
    public ReleaseReceipt? Release { get; }
    public FrameDrainException(DrainReceipt? drain, ReleaseReceipt? release)
        : base("IFR-010") { Drain = drain; Release = release; }
}
public sealed record ResourceEvent(
    ResourceEventKind Kind, Guid ServiceEpoch, long Sequence,
    string ConsumerId, FrameKey? Key, OperationReceipt? Operation,
    ReleaseReceipt? Release, DrainReceipt? Drain, FrameError Error,
    FrameDiagnostic? Diagnostic, ResourceSnapshot? Snapshot);
public sealed record FrameDiagnostic(
    string Code, string Stage, int PlaneIndex, int RowIndex,
    FrameError SourceError, string AdapterVersion);
public sealed record ResourceSnapshot(
    long CpuBytes, long NativeBytes, long GpuBytes, long ReservedCpuBytes,
    long CacheBytes, int ActiveOperations, int QueuedOperations,
    int LeaseCount, int ScopeCount, long CopiedBytes);
public interface IFrameEventSink { void OnEvent(ResourceEvent value); }
public interface IFrameReadScope : IDisposable
{
    // coordinates are local to Layout; copies only scalar row bytes, never padding.
    FrameError CopyRow(int planeIndex, int localY, Span<byte> destination);
}
public interface IFrameLease : IAsyncDisposable
{
    Guid Id { get; }
    string ConsumerId { get; }
    FrameKey SourceKey { get; }
    PixelWindow CoreWindow { get; }
    PixelWindow ActualWindow { get; }
    ManagedFrameLayout Layout { get; }
    ImmutableArray<PlaneMetadata> Metadata { get; }
    ImmutableArray<int> SourcePlaneIndices { get; }
    ImmutableArray<AllocationCharge> Allocations { get; }
    FrameError TryOpenReadScope(out IFrameReadScope? scope);
    ValueTask<ReleaseReceipt> ReleaseAsync(TimeSpan observationTimeout);
}
public interface IFrameService : IAsyncDisposable
{
    Guid ServiceEpoch { get; }
    ValueTask<PublishResult> PublishCopyAsync(CopyPublishRequest request, CancellationToken ct);
    ValueTask<ReadResult> ReadAsync(FrameReadRequest request, CancellationToken ct);
    OperationLookup QueryOperation(Guid serviceEpoch, Guid requestId);
    ValueTask<DrainReceipt> RetireAsync(FrameKey key, TimeSpan observationTimeout);
    ValueTask<DrainReceipt> CloseAsync(TimeSpan observationTimeout);
}
public sealed record FrameServiceCreateResult(FrameError Error, IFrameService? Service);
public interface IFrameServiceFactory
{
    FrameServiceCreateResult Create(ResourceLimits limits,
        IManagedLayoutValidator validator, TimeProvider timeProvider,
        IFrameEventSink? events);
}
```

**请求和结果规则。** Create 全部限额必需，CPU/frames/全局active/receipts/消费者held/leases/active为正，native/GPU/cache/全局及消费者queued可为0（禁用），时间有限，消费者唯一；FrameBudget 必须有效。预算来源沿 Core 字段，所有资源上限属于该 Profile 修订。纯 CPU Create 要求 MaxNativeBytes=MaxGpuBytes=MaxCacheBytes=0。Factory 的计划实现类名为 `FrameServiceFactory`；其余接口由请求/工厂返回，不要求宿主实现释放 Owner。

Factory成功Error=None且Service非null；失败Service=null，不创建隐式部分服务或静态后台工作。Resources/TileCache构造仅校验配置，不接管失败时的source，不读像素；正整数/集合/来源无效用InvalidArgument，预算关系/缺少可用预算用BudgetUnavailable，CPU切片不支持的native/GPU能力用UnsupportedFormat。这些工厂返回值不同于已接纳操作回执，不伪造Draining。

Resources请求首错依次为：对象/RequestId存在性→同ID请求等价/Conflict（有效原请求直接返回回执）→已Closed→ConsumerId登记与必填来源→Timeout/枚举→FrameKey/修订→Publish的Core布局与Metadata，或Read的plane索引/窗口/halo/域→回执容量→FrameKey注册冲突/版本→consumer及全局字节/计数额度→接纳。ct已取消在取得资源前返回Rejected/Cancelled，不触发Source。Core.InvalidArgument/Dimension/PlaneCount/PixelFormat/Stride/Domain映为Resources.InvalidArgument，LayoutOverflow/OutOfBounds映LayoutOutOfBounds，BudgetUnavailable/Exceeded按同名映射；保留Core具体错误的诊断Code，不制造第二首错顺序。任何请求拒绝均不复制像素或触发native。

PublishCopyAsync先完成结构/格式/域/限额预检，然后预占目的存储和一行scratch，再复制所有plane行（每行恰为RowBytes）、规范成正stride紧凑小端布局，扫描有效浮点值、冻结后在门内发布。来源只是借用，不转移所有权，模块不Dispose Source。CopyRow不允许保存destination、启动异步写入或跨返回继续访问；接口不能证明违反约定的来源安全，宿主必须提供稳定来源租约。ct接纳前取消为Rejected/Cancelled，复制中逐行观察。同步CopyRow无法被强制中断，停滞返回DrainUnknown后仍保持原操作source借用；必须以原ServiceEpoch/RequestId查询到OperationResourcesReleased才可归还来源。设备SDK若无法遵守此借用期，不能直接接入此端口，应先由相机适配器制作独立稳定快照。发布失败无Frame/无半发布；成功Frame仅为规范化元数据，注册表保留storage发布持有权。

ReadAsync 是一次租约交付，不执行消费者算法。必须指定已登记 ConsumerId、原 FrameKey、非空严格递增唯一 plane 索引、level=0 的合法窗口及 Halo 0..1,048,576。ExactSamples 只读源标量，不做 LUT、插值或 LOD。CoreWindow 必须在源内；ActualWindow 为 core+halo 的 checked 扩张，RejectMissingSupport 缺域/越边拒绝，ClipAndMarkInvalid 返回交集、逐 plane 域与缺口，不合成边缘像素。返回的 Layout 为实际窗口局部布局，Metadata 域平移到局部；结果 planeIndex 使用请求中的排列后的局部索引。CPU slice 为受控共享视图，不复制整块；CopyRow 只把本行精确字节复制到调用方缓冲，长度必须恰好等于该行 RowBytes，错误不写 destination。成功为 Completed/Empty + Slice，布局或读取错误为 Slice=null。Empty 仅是有效域为空，仍可能持有真实像素，必须释放 Slice。

**固定 CPU 容器与硬界限。** CopyStorage 的目的存储只用一维、零起点、精确长度的 `new byte[checked((int)destinationBytes)]`；scratch只用一块 `new byte[checked((int)maxRowBytes)]`。不使用ArrayPool、分段数组、native内存、可扩容buffer或实现者自选容器。模块支持上限固定为 `CpuBufferHardMaxBytes = 1_073_741_824L`（1 GiB），运行时有效容器上限 `C = min(CpuBufferHardMaxBytes, (long)Array.MaxLength)`；每plane的RowBytes、destinationBytes与maxRowBytes均须在1..C。单行检查后按plane顺序checked计算planeBytes=Height*RowBytes、planeOffset=此前planeBytes之和、destinationBytes=sum(planeBytes)，再检查总容量；溢出为LayoutOutOfBounds，超过C为UnsupportedFormat/IFR-002，Stage=CpuContainerLimit。两者在接纳/分配/调用Source之前拒绝。1 GiB是本模块容器能力边界，不是客户内存预算或分配保证；Resources总CPU限额可大于C以容纳多个独立buffer，FrameBudget/consumer/global仍分别校验。Core的long布局数学值域不因此收窄，超过此驻留能力的图走§7有界ITiledFrameSource，不能静默分段复制全图。

目的Frame.Layout按源plane顺序排入该byte[]：OffsetBytes=planeOffset，StrideBytes=RowBytes，ByteOrder=LittleEndian，AccessibleBytes=DeclaredBufferBytes=destinationBytes；接纳前再次用Core和同一FrameBudget校验目的布局。源plane即使alias重叠也各复制一份，sum可能大于源buffer容量；不靠源RequiredBytes估目的占用。预占量为checked(destinationBytes+maxRowBytes)，全局CPU及发布consumer逻辑额度均须足够，FrameBudget只比较目的布局容量而非scratch。先分配目的数组，再分配scratch；已分配但尚未登记actual的部分仍由原reserved覆盖，每次成功在服务门内以实际array.LongLength将对应预占原子转成actual，未分配部分保持reserved，转换不得重复加容量。目的数组一个新AllocationId，scratch一个内部AllocationId，Bytes均为实际LongLength，不能按有效域、请求窗口或同一array的plane数重计。

每次行复制按逻辑plane/y次序执行：检查取消/deadline→取scratch.AsSpan(0,checked((int)RowBytes))并清零→Source.CopyRow→成功后按标量换序并校验有效域内浮点值→将域外样本字节置零→复制到目的array.AsSpan(checked((int)(planeOffset+y*RowBytes)),checked((int)RowBytes))。所有offset/end先checked且验证不超过destinationBytes，再转int；不形成跨行Span。CopyRow错误/异常不得发布半帧，零填域外不改变无效域、单位或质量事实。最后一行后再检查取消/修订/关闭，冻结全部布局/域/元数据，按下述移交步骤提交。scope仍不暴露数组；它按已验证局部行offset向调用方复制。

在有效容器/预算内也可能OutOfMemoryException。分配失败为已接纳操作Failed/AdapterFailure/IFR-009，Stage=CpuDestinationAllocation或CpuScratchAllocation，SourceError=None；不降级、不重试扩容、不发BudgetExceeded假装容量拒绝，也不触发Source。已成功分配的数组先移除全部模块引用，再撤actual；未分配部分撤reserved，归还执行槽/借用后才置OperationResourcesReleased=true。scratch在成功、取消、失败路径都到最后同步CopyRow真实退出才移除引用；未知占用保持原账。byte[]的StorageReleased指本Owner已撤所有强引用及pin/使用，并非CLR已回收或RSS下降，不强制GC。CpuBytes只统计仍持有/执行/待释放的像素与scratch数组payload，CLR对象头、对齐、元数据、已释放尚未GC的数组及托管堆提交量另测，不能宣称MaxCpuBytes限制整个进程堆/RSS。

切片Layout.Width/Height取ActualWindow尺寸，plane的OffsetBytes=源offset+ActualWindow.Y*源stride+ActualWindow.X*通道数*标量字节数，StrideBytes仍为源stride，RowBytes按实际宽度计算，AccessibleBytes/DeclaredBufferBytes仍为被持有allocation容量；Layout.Domain取源域裁剪并平移，不重建不存在的像素。SourcePlaneIndices记录局部plane到源plane的索引，Metadata按相同次序；源为TiledReadResult时依据source返回的实际buffer布局，不假定全图allocation。Allocations至少一项，非空Guid、Bytes>0、同Id只出现一次，CPUslice对应唯一CPU AllocationCharge，其Bytes为实际物理容量而非窗口样本量。

Read的Empty只有所有选中plane的实际有效域均为空时；一部分plane空而其它非空返回Completed，各自域与原因完整保留，不用Partial或并集掩盖缺测。RejectMissingSupport检查全部所选plane，因此任一空域即InsufficientSupport；ClipAndMarkInvalid允许Empty结果但仍移交lease。TryOpenReadScope成功返回None+非null scope；失败为LeaseClosed或Unknown且scope=null，不返回虚假可读对象。CopyRow仅读取ActualWindow对应行，算法若只需core必须按CoreWindow相对ActualWindow偏置裁出，不把halo当有效输出。

CoreWindow.X/Y非负、Width/Height正，以long checked验证右/下端不超过源尺寸，非法core为InvalidArgument；halo expanded端计算溢出为LayoutOutOfBounds；core合法但halo越边或有效域支撑不足为InsufficientSupport（RejectMissingSupport）。ClipAndMarkInvalid裁图像边界但保留CoreWindow/ActualWindow的真实范围，不能声称提供了缺失halo。FrameKey未见为NotFound、已Retire为LeaseClosed；源发布注册表没有“最近图像”猜测。共享view的租约占用按整个allocation记，不按小窗口减低consumer held计费。

Source.CopyRow的非None错误统一映为AdapterFailure（资源回执保留失败plane/y诊断），不把来源返回的Cancelled等误写为本操作已排空；该调用真返回后再清理。source异常捕获为AdapterFailure并同路清理，不能保留半写destination后继续下行。IFrameReadScope.CopyRow仅返回None、InvalidArgument（索引/长度）、LeaseClosed；内容复制前完成全部检查，成功把整行复制，错误不写destination。Unknown/Faulted allocation不得开放新scope。

**完成与持有权。** OperationResourcesReleased 只指本请求的临时 scratch、在途借用及执行槽已归还，成功发布转为注册表持有、成功读取转为 ResultLeaseId 持有，不声称源 storage 已析构。结果租约可在 Task 返回后读取；本请求至该移交点计时，另外测 ResultLeaseId 从交付到释放及最后 storage 释放，不能把读取 API 返回当算法端到端完成。失败/取消不移交结果。Lease Release 先原子关闭新 scope，已有 scope 持有权直到 Dispose；重复 Release 返回同一关闭事实并累计次数。LeaseClosed 不等于 StorageReleased，只有最后发布/缓存/lease/scope/native/GPU 持有均归零才发 StorageReleased。ReleaseAsync/CloseAsync/RetireAsync 没有清理取消 token，期限只限制观察，不取消真实清理；IAsyncDisposable 使用配置的 DrainTimeout，若超期必须以异常携带关联和 DrainUnknown 回执，不能正常返回伪称已释放。

**幂等、回执和事件。** RequestId 首次调用绑定元数据及操作参数摘要；Source 不参与对象引用相等比较，重复 Publish 不重新调用来源，不替换内容。相同 ID/摘要重复调用只返回原回执（Read 的 Slice=null，原 ResultLeaseId 在回执中）；不同摘要返回 Rejected/Conflict，不覆盖原回执。查询只读，不创建 lease，不用当前 Frame 快照替代旧操作。成功重复 Publish 的 Frame 可返回原不可变元数据；晚到修订不得覆盖较新 FrameKey。业务需要第二 lease 必须新 RequestId。同 FrameKey 已存在时不重新复制，返回 Conflict；内容一致的重放由宿主映射为同一已知引用，模块不猜来源内容相同。

“请求摘要”在进程内以字段等价比较为权威，不依赖JSON序列化或record/ImmutableArray引用Equals：Publish比较ConsumerId、完整输入Descriptor（所有layout/domain/metadata字段、来源/坐标）、Timeout.Ticks；Read比较ConsumerId、FrameKey、plane索引值序列、窗口、halo、边界、Intent、Timeout.Ticks。字符串Ordinal、枚举/整数精确、有限double以IEEE位模式比较，数组逐值且不自动重排；Source对象不比较。可计算内部hash加速索引，但hash命中后仍逐字段核对，不以碰撞等于请求相同。回执只保留描述/参数，不保留Source对象或结果lease对象；source引用在真实操作完成才移除。

所有请求先预留回执容量；未完成回执不可驱逐，完成回执按 ReceiptRetention 保留并有 MaxReceipts 硬上限，容量不足接纳前 BudgetExceeded。保留期之外 Query 为 NotFound（不能据此认定未执行），进程重启丢失的 epoch 为 Unknown，由持久化宿主对账；本模块没有 durable exactly-once 承诺。重试可用 ID 的边界必须由宿主保留原 epoch。事件在提交状态后、锁外同步发给可选 sink；sink 必须快速、不可阻塞，抛异常记诊断不回滚发布或越过清理。不得把回调成功当事务提交。每服务 epoch 的 Sequence 单调递增，回调允许重入查询，通知可能因并发先后到达，消费者按 Sequence 投影，Query 是状态权威；不能依赖事件到达顺序获取所有权。无订阅者仍可运行。

无有效RequestId/参数或回执容量耗尽的未接纳调用直接返回Rejected回执，不为其创建持久记录或无限诊断；返回的ServiceEpoch仍为当前epoch，ResultLeaseId=null、Drain=NotStarted、OperationResourcesReleased=false。Rejected不是执行失败，表示从未获得操作资源。相同ID的冲突拒绝不覆盖其Query原回执；重复读取不会再次交付对象，调用方必须保留首次Slice。终态操作的ResultLeaseId只为关联元数据，Query不会恢复丢失的租约对象。源实际工作完成而首次调用已返回DrainUnknown时只在Query发布终态；取消/超时后不得迟交成功Slice或Frame。

**资源关闭。** Retire 只撤销指定 FrameKey 的新读取及发布持有权，不取消别的修订/消费者。Close 关闭服务的新发布/读取并请求取消本服务在途操作；外部已经交付的 lease/scope 仍由其消费者归还。期限内未完成为 Draining/DrainUnknown + OutstandingLeaseIds/RetainedBytes，保留查询与后续 Close/Release；禁止强制置零。成功 Close 返回 Drained/ResourcesReleased，之后查询历史允许、新工作返回 Closed。Retire/Close 重复幂等。服务不可重新打开，重启必须新 ServiceEpoch。

QueryOperation 必须同时传入原ServiceEpoch与RequestId；epoch不同为Unknown，不把重启丢失回执写成NotFound。ReleaseReceipt.Drain只指该lease的scope是否归还，Drained时StorageReleased仍可false（其它消费者仍持有）。DisposeAsync只等自己的持有，不等待无关消费者；自己scope未结束则抛FrameDrainException(Drain=null,Release=原回执)，服务Dispose失败携带DrainReceipt，保留原对象后续查询/释放。普通Release/Close观察超时返回回执而不抛该异常。OutstandingLeaseIds包含已经LeaseClosed但scope仍在使用的关联；RetainedBytes计真实未释放字节，不以关闭标志归零。

**物理容量与consumer逻辑额度。** Create只校验每项限额的值域/来源和实际资源维度关系；不要求消费者MaxHeldBytes、active或queued上限之和小于全局上限，也不把每consumer额度预先占成物理容量。限额表示独立接纳上界，不是保证同时可用的预分区。每次请求在同一服务门内分别判定全局实际+物理预占、consumer逻辑held+逻辑预占、全局及consumer的active/queued、consumer的lease、全局frame和receipt槽；任一不满足为BudgetExceeded，不写入部分接纳状态。不同服务/上游/协调器的账是各自受控范围，宿主不能相加它们的同一AllocationId快照冒充进程实际物理总量。

全局allocation表键为AllocationId，保存不可变Kind/Bytes与各类持有引用数；CpuBytes/NativeBytes/GpuBytes是相应仍存活唯一allocation的Bytes之和，ReservedCpuBytes只含尚未转actual的物理预占。相同Id的新增引用不加actual；同Id不同Kind或Bytes为Conflict，不修改旧条目/旧租约。consumer表键为(ConsumerId,AllocationId)，保存该consumer的发布注册、缓存、在途操作、lease及pending-release holder引用数：0→1加整个Bytes，1→n只加引用，n→0减Bytes；跨consumer各自首次加Bytes。同consumer两个窗口/lease共享同allocation只计一次held字节，每个lease仍独占一个MaxLeases槽，scope不新增lease槽。所有资源Kind的逻辑Bytes合计受MaxHeldBytes约束，scratch及尚未落实的复制预占也计入发起consumer；发布未读的注册持有不能绕过额度。已有allocation的普通共享Read不预占新物理字节；其consumer逻辑delta为该consumer尚未持有的allocation之和，多项先去重再checked求和。

**原子接纳、移交与归还顺序。** ① 门内先核回执/身份/关闭/取消和所有额度；同次提交请求记录、frame/operation或等待槽、lease预留、物理与consumer逻辑预占，以及共享Read所需受保护allocation引用，之后才启动Source/分配；接纳竞争不能先检查后锁外增账。排队操作仍保留字节及结果lease预留，queued→active需同时检查两层active限额并原子换槽；等待期间取消且未启动工作可整笔撤销。② 新数组分配成功，门内以实际capacity替换该部分physical/consumer reservation并建立operation holder，不能在两个账转换之间让其它请求占用空隙。③ 成功Publish或Read交付点，门内再次核取消/deadline/关闭/修订，先建立注册holder或结果lease及其关联，再移除operation holder/结果预留；同allocation只换引用，不能先减bytes再加。scratch及来源借用实际结束、执行槽归还后才发布本操作ResourcesReleased/终态；失败不创建结果holder。④ Release门内封闭新scope；若现有scope或该lease名下pin/fence尚在，则将lease holder转pending-release holder，保留consumer bytes及lease槽；全部退出后才移除holder/lease槽。重复Release不再减账，scope Dispose等自己的同步CopyRow结束。Retire/Close只移除自己的发布/cache holder，不能减其它consumer。⑤ consumer最后引用结束且本方使用已确认归还才可减其logical bytes。全局最后holder申请释放时先标记不可复活，将其转成释放中holder并保留actual及该holder所属consumer logical；锁外移除数组/归还上游，确认真实Owner释放后门内撤释放中holder、其logical及actual并发StorageReleased。其他consumer使用已确认结束可先撤其自身holder，不等待无关consumer；未知释放的所属holder/额度/槽及关联必须保留，不能以超时、取消或LeaseClosed清账。

同FrameKey的发布/退休墓碑在相应回执保留期内阻止重用，容量计入MaxReceipts；调用方在保留期外也不得重用FrameKey/RequestId指代不同内容，模块不提供无限历史去重。重启/过期的旧工作需宿主对账。

计账范围是本实例受控allocation及其尚未落实的承诺：CopyStorage输入Source仍由外部Owner持有，未交给模块的相机/Replay源buffer与调用方CopyRow目的数组不自动计入本实例CpuBytes；宿主在Profile中另计来源/下游缓冲的同时峰值。Tile wrapper对已借用上游charges计其受控借用量，同物理Id在不同Owner范围重复出现不能相加作RSS。Snapshot.LeaseCount为已交付/持有/pending-release租约数，不含尚未交付的预留槽；ScopeCount到同步使用真实退出才减。接纳MaxLeases使用此consumer实际+预留槽；Snapshot.ActiveOperations/QueuedOperations按已接纳客户端请求所在槽计，不重复计同请求。所有reservation→actual/holder移交按整笔净增量核验并提交，一致快照不观察过渡双计。

Release/Drain观察回执Error=None仅在其作用域真实Drained时；在途且有限期限尚可观察为Timeout/Draining，不能证明使用是否停止为DrainUnknown/DrainUnknown，ResourcesReleased/StorageReleased保持false。Retire未见key返回NotFound/NotStarted而非成功析构。回执带真实观察时间，不把上次时间复制成新的释放时间。Snapshot是服务门内各预算/计数的一致只读采样，非质量事实；操作诊断Code沿IFR键，Stage用稳定阶段键、PlaneIndex/RowIndex不适用=-1，SourceError只保留来源枚举，不用来源状态代替本操作状态。Snapshot/事件中不传像素/异常对象/句柄，详细异常由宿主诊断端口按RequestId关联。ConsumerId仅做持有隔离和额度键，不是权限凭据，授权由调用宿主保证。

Publish接纳预占FrameKey，复制完成在服务门内再次检查Close/取消/deadline与同Id最新修订，过期则不发布并清理。同Id已发布r2后迟到r1为StaleRevision；已发布r1仍可按确切FrameKey读取直到Retire，不提供隐式latest帧入口。同key只允许一个在途发布，新RequestId同key为Conflict。Retire无该key为DrainState.NotStarted/RetainedBytes=0（未见过不能当已释放），有该key重复返回其已知事实。超期观察只返回Draining或DrainUnknown，不发业务终态；Close撤销全部注册表持有及新接纳，但不替外部消费者归还。Lease重复Release计数最多int.MaxValue，达到上限保留该值并发Diagnostic，不抛溢出或重新析构。
### 4.4 首片唯一 API Contract v0.2：`ManagedLayoutValidation`

首片只冻结下列纯托管类型和一个同步入口。字段顺序、枚举成员、单位和错误键属于本模块 Core API；不得用平台候选 DTO 替换，也不得增加隐式默认字段。

```csharp
using System.Collections.Immutable;

namespace Asun.Modules.ImageFrame.Core;

public enum PixelScalarKind { UInt8, Int16, UInt16, Int32, Float32, Float64 }
public enum ByteOrder { LittleEndian, BigEndian }
public enum PlanePacking { SinglePlane, Interleaved, Planar }
public enum PlaneRole { Intensity, ColorR, ColorG, ColorB, Height, Mask, Auxiliary }
public enum DomainKind { Full, RowSegments, Empty }
public enum ValidationStatus { Valid, Empty, Invalid, BudgetRejected }
public enum ValidationErrorCode
{
    None, InvalidDimension, InvalidPlaneCount,
    InvalidPixelFormat, InvalidStride, LayoutOverflow, OutOfBounds,
    InvalidDomain, BudgetUnavailable, BudgetExceeded,
    InvalidArgument
}

public sealed record BudgetLimit(
    long DeploymentHardMaxBytes,
    long ProfileMaxBytes,
    int DeploymentMaxDomainSegments,
    int ProfileMaxDomainSegments,
    string DeploymentSourceId,
    string DeploymentSourceRevision,
    string ProfileId,
    string ProfileRevision);

public sealed record PlaneLayout(
    PixelScalarKind Scalar,
    ByteOrder ByteOrder,
    int BitsPerSample,
    int ChannelCount,
    PlanePacking Packing,
    PlaneRole Role,
    long OffsetBytes,
    long StrideBytes,
    long RowBytes,
    long AccessibleBytes);

public sealed record DomainRow(int Y, int StartXInclusive, int EndXExclusive);

public sealed record DomainDescriptor(
    DomainKind Kind,
    ImmutableArray<DomainRow> Rows);

public sealed record ManagedFrameLayout(
    int Width,
    int Height,
    ImmutableArray<PlaneLayout> Planes,
    DomainDescriptor Domain,
    long DeclaredBufferBytes);

public sealed record ManagedLayoutValidationRequest(
    ManagedFrameLayout Layout,
    BudgetLimit? Budget);

public sealed record LayoutValidationResult(
    ValidationStatus Status,
    ValidationErrorCode Error,
    int ErrorPlaneIndex,
    int ErrorRowIndex,
    ManagedFrameLayout? AcceptedLayout,
    long RequiredBytes,
    long EffectiveMaxBytes);

public interface IManagedLayoutValidator
{
    LayoutValidationResult Validate(ManagedLayoutValidationRequest request);
}
```

Core v0.2 增加显式 ByteOrder、域行段工作量上限和 InvalidArgument，将旧 DeclaredPayloadBytes 更名为 DeclaredBufferBytes，修正旧预算/错误顺序歧义；这是规格版本变更，不宣称旧包已迁移。相同契约版本保持字段、枚举整数顺序和值域，新增/放宽均升契约版本；未知枚举拒绝，平台新增字段不得回填到 Core。

**存在性和首错唯一顺序。** ① null request/Layout/Domain或default Planes/Rows数组为Invalid/InvalidArgument，索引=-1；不预先遍历数组。② Budget为null、非正上限、来源为空白或Profile子限高于Deployment上限（字节或行段）为BudgetRejected/BudgetUnavailable，EffectiveMaxBytes=-1。③ Width、Height、plane数按此顺序。④ 每plane依索引先判null元素（InvalidArgument，定位plane），依次校验Scalar/ByteOrder/Packing/Role、bits/channel/role/packing匹配、checked RowBytes乘积与字段匹配、容量/offset值域、stride行重叠、checked访问范围。⑤ DomainKind/Rows形状、Rows.Length门禁、逐段null元素（InvalidArgument，定位row）、范围及排序。⑥ 容量预算。多错输入依此唯一顺序，不与§5资源发布预检混用。任何错误AcceptedLayout=null；Valid/Empty时保留同一不可变值、Error=None、两个错误索引=-1。OOM/宿主失效不伪造正常验证结果。

Width/Height 为 1..int.MaxValue，plane 数 1..64，通道数 1..4；Scalar 的字节数固定 1/2/2/4/4/8，BitsPerSample=字节数*8；SinglePlane/Planar 为单通道，Interleaved 为 2..4 通道；ColorR/G/B 单通道，Mask 为 UInt8 单通道，Height 为 Float32/Float64 单通道，Interleaved 不从 Role 猜通道次序。ByteOrder 8位仍须显式 LittleEndian（无字节换序），其余接受两个注册值，纯 Validator 不进行换序或值解释。压缩、packed bits、自定义扩展不在本契约。PlanePacking.Planar 只描述当前单通道 plane，不隐式要求另外两 plane。

**布局公式。** 所有 plane 指向同一抽象 buffer 原点；AccessibleBytes 是从该原点起的可访问前缀长度，不是从 OffsetBytes 起的长度。要求 0 < AccessibleBytes <= DeclaredBufferBytes，DeclaredBufferBytes > 0；OffsetBytes >= 0。RowBytes=checked((long)Width*ChannelCount*bytesPerSample)>0，不能把 padding 加在 RowBytes；d=checked((Height-1)*StrideBytes)，lo=checked(OffsetBytes+min(0,d))，hi=checked(OffsetBytes+max(0,d)+RowBytes)。要求 lo>=0 且 hi<=AccessibleBytes；Height>1 时以 `stride >= rowBytes || stride <= -rowBytes` 判断，不调用 Abs(long.MinValue)。Height=1 允许任意 stride（不访问第二行）。乘加溢出为 LayoutOverflow，单行不匹配为 InvalidPixelFormat，行重叠为 InvalidStride，容量不够为 OutOfBounds。多个只读 plane 可指向同一字节，验证器不宣称物理隔离；发布适配必须按每 plane 语义复制。RequiredBytes=DeclaredBufferBytes；有效样本量=sum(Height*RowBytes) 与 buffer容量/行间padding不同，不得用有效量放行 buffer预算。相同 allocation 不按 plane 重复计容量。

**有效域。** Full/Empty 的 Rows 必须为 Empty 而非 default；RowSegments 必须有至少一段。每段 0<=Y<Height、0<=StartXInclusive<EndXExclusive<=Width；按 (Y,StartXInclusive) 严格递增，同一行相邻/重叠均为 InvalidDomain（原数据由来源显式规范化，Validator 不自动排序/合并）。未出现行表示无有效样本，Empty 仍须校验真实布局和预算，不能让空域绕过容量拒绝。Rows.Length 超过 min(DeploymentMaxDomainSegments,ProfileMaxDomainSegments) 先返回 BudgetRejected/BudgetExceeded、ErrorRowIndex=-1，不线性扫描巨量元数据。两行段限额均正且 Profile<=Deployment；其实际值来自明确 Profile 修订，合成测试限额不用于生产。

**预算与同步行为。** RequiredBytes<=min(ProfileMaxBytes,DeploymentHardMaxBytes) 才可 Valid/Empty；容量超过限额为 BudgetRejected/BudgetExceeded，EffectiveMaxBytes 为已验证的有效上限。所有整数计算 checked，不截断、饱和或改变首错。只有 Domain.Kind=Empty 时返回 Empty；其他合法域为 Valid，不表示像素质量合格。本接口不分配像素、启动线程、native/IO/事件/lease/cache 或持久化。调用期间宿主不可通过 unsafe/ImmutableCollectionsMarshal 修改输入底层数组；并发只读相同值可复用，结果字段等价而不要求数组引用 Equals。首片无异步资源，CancellationToken/timeout/DrainUnknown/ResourcesReleased/lease release/native 排空均 NotApplicable；后续使用 §4.3 真正可观察的回执。

值域错误映射固定：Width/Height→InvalidDimension；plane数→InvalidPlaneCount；未知DomainKind或Rows形状/内容→InvalidDomain；未知Scalar/ByteOrder/Packing/Role、Bits/Channels/RowBytes不匹配→InvalidPixelFormat；AccessibleBytes/DeclaredBufferBytes非正、AccessibleBytes高于DeclaredBufferBytes、负Offset或访问越界→OutOfBounds；stride行重叠→InvalidStride；checked溢出→LayoutOverflow。plane错误定位该plane，域元素错误定位该row；非元素错误索引=-1。步骤④全部通过后RequiredBytes=DeclaredBufferBytes，此后域错误或预算拒绝仍保留该值；此前为-1。步骤②通过后EffectiveMaxBytes恒为min两字节上限，即使随后结构错误也不改；此前为-1。Valid/Empty不计算sum(H*RowBytes)作为结果字段，因为只读plane可重叠，sum不代表实际allocation。

### 4.5 首片最小宿主调用与测试计划

最小宿主只创建 `ManagedFrameLayout`、提供来源明确的 `BudgetLimit`，调用一次同步 `IManagedLayoutValidator.Validate`，读取结果并退出；它不需要窗口、文件、数据库、设备、HALCON、AsunImage 或后台线程：

```csharp
var budget = new BudgetLimit(
    DeploymentHardMaxBytes: 256L * 1024 * 1024,
    ProfileMaxBytes: 64L * 1024 * 1024,
    DeploymentMaxDomainSegments: 10000,
    ProfileMaxDomainSegments: 1000,
    DeploymentSourceId: "deployment-profile",
    DeploymentSourceRevision: "2026-10-05",
    ProfileId: "image-frame-core-test",
    ProfileRevision: "v1");

// Synthetic software-test input; these limits are not customer production limits.
var layout = new ManagedFrameLayout(3, 3,
    ImmutableArray.Create(new PlaneLayout(PixelScalarKind.UInt16,
        ByteOrder.LittleEndian, 16, 1, PlanePacking.SinglePlane,
        PlaneRole.Intensity, 0, 8, 6, 22)),
    new DomainDescriptor(DomainKind.Full, ImmutableArray<DomainRow>.Empty), 22);
IManagedLayoutValidator validator = new ManagedLayoutValidator();
var request = new ManagedLayoutValidationRequest(layout, budget);
var result = validator.Validate(request);
if (result.Status is ValidationStatus.Valid or ValidationStatus.Empty)
    Console.WriteLine(result.RequiredBytes); // 22; effective scalar bytes are 18.
```

`ManagedLayoutValidator`为本规格的计划实现类名（无构造参数），工程开启Nullable与ImplicitUsings；本段只是未来公开接口调用样例，当前未生成/编译产品代码。

首片唯一测试工程为 `tests/Modules/image-frame/Asun.Modules.ImageFrame.Core.Tests/`；只允许修改首片 Core 工程、该测试工程和本指导，禁止触碰适配器、产品宿主、平台 Schema、AsunImage 内部及客户项目。测试必须覆盖：

1. 单 plane 正常帧、合法多 plane、`Empty` domain 和合法负 stride。
2. 宽/高为 0 或溢出、plane 数 0/65、未知 enum、bits/sample 不匹配、packing/channel 不匹配。
3. `H=3,rowBytes=6,stride=8,offset=0` 的 22/21 字节边界、负 stride 的 `offset` 边界、`long` 加乘溢出、padding 计入 buffer容量而不计入有效样本；AccessibleBytes 与 DeclaredBufferBytes 的共同原点。
4. 域行段越界、重叠、相邻、未排序、`Empty` 带行段、`Full` 带行段，以及同一坏输入的确定性首错。
5. 缺失 Budget、空白来源、Profile 大于部署硬上限、字节/行段数超限、空域超预算；确认不分配像素、不调用外部端口；多错输入按 §4.4 唯一首错顺序。
6. 重复调用和并发只读调用返回等价结果；验证期间无共享可变状态、文件、线程、事件、lease、cache 或释放操作。

首片 BenchmarkProfile 只测托管 `Validate`：输入桶为 `1/2/4/16/64` plane、域行段 `0/1/1,000/10,000`、合法/拒绝/溢出三类；测量冷启动、固定预热、固定样本、Validate 总时长、托管分配字节和峰值。端到端样本不包含任何资源取得，`ResourcesReleased`/排空测点标记 `NotApplicable`。部署硬上限和 Profile 子限必须来自部署/消费者配置文件并记录来源 ID/修订；没有 Profile 的测量只能是 `NotEvaluated`，不能标记通过或放行。P50/P95/P99 统计沿 DEV-GOV-010 §3.1，失败/拒绝/未完成样本单列。

## 5. 布局验证与发布流程

本节为资源发布，Core 的首错严格依 §4.4。Publish 先检查 RequestId/ConsumerId/FrameKey、来源和元数据闭包，调用 Core 校验布局/预算，再检查每 plane 单位、通道数、有效域和端口能力。在取得 scratch 或启动 native 前拒绝未知格式。每 plane 单独使用原点与 checked 访问公式，不从 domain 推断 buffer 大小。

进程内主路线固定复制：依§4.3先checked计算单行/紧凑总量并验证C和目的Core布局，再原子预占全部目的存储及最大一行scratch，以精确长度byte[]分配。逐plane逐逻辑行按§4.3执行清scratch、CopyRow、标量换序、有效浮点值检查、清域外、写紧凑目的行。源padding和域外旧字节不得导出；清域外只规范存储，不使其有效。导出若另需填充，用明确导出配置及派生身份。接纳后分配/来源异常走相同清理；未知仍被native/来源占用则留账隔离。复制完成才冻结并在线性化点先移交holder再撤operation，不能先发事件或提前减账。

发布前源会写入则复制必须在宿主稳定借用期内完成；ReadOnlyMemory/对象别名只能约束访问接口，不能阻止原生产者写入。`copy_obj`、`reduce_domain` 不证明物理隔离。来源回调返回后会重用的相机必须在有效回调期内完成复制，或先由相机适配器持有独立来源租约；不能排入本模块队列后等待借用已失效的指针。

## 6. 租约、读取、取消与排空

模块是自己复制存储的唯一析构 Owner；来源 Owner 保持来源所有权。发布注册表、缓存、lease、scope、native/GPU fence 是不同持有者。租约、scope 的创建/关闭与持有计数在同一短门内线性化，最后计数变零时先标记不可复活，再在锁外析构。CPU 原始数据不暴露 array/Memory/指针，scope 通过同步 CopyRow 返回复制字节；原生零拷贝和 GPU 只在适配器握持独立 pin/fence 后可用。

一个scope同时只允许一个CopyRow；同scope第二并发CopyRow返回InvalidArgument且不写destination，与Dispose竞争时或完整复制、或在写destination前返回LeaseClosed，不读回池字节。Dispose标记停止接纳，等该scope正在执行的同步复制退出后归还；不持全局锁复制。需要并行读时每个任务另开scope，不能共用一个scope的Dispose影响另一个任务。资源模块不拥有消费者算法Task，其取消/释放不证明下游native已结束。

事件与终态按作用域区分：

```text
未接纳：Requested → Validating → Rejected（无资源释放事件）
已接纳：Accepted → Reading → Draining → Drained → ResourcesReleased
       → Completed | Empty | Cancelled | TimedOut | Failed | Unknown
发布成功：门内先移交目的持有权到注册表，再释放临时资源/报告操作终态
读取成功：门内先移交结果持有权到 ResultLeaseId，再释放临时资源/报告操作终态
lease：Open → Closing → LeaseClosed；scope 可继续到其实际 Dispose
storage：Published → Retiring → 等发布/cache/lease/scope/fence归零
         → StorageReleased；未知则隔离保留
服务：Closing → 等所有资源真实释放 → Closed；未知不发 Closed
```

ResourcesReleased 事件字段是 OperationResourcesReleased，不等同 ReleaseReceipt.StorageReleased；两者禁止互相补写。业务终态错误只在本操作排空和借用归还后发布；观察期限到了而源仍运行，返回原 RequestId、Error=DrainUnknown、Drain=DrainUnknown、Phase=Draining，不把超时观察写成 TimedOut 终态。稍后真实停止才能发布 TimedOut/Cancelled。取消与完成竞争以线性化点为准：成功交付后收到取消不追溯撤销已移交的 Slice，调用方显式 Release。

Lease 没有自动到期强回池，MaxHold 只可作为监测阈值；慢消费者达到自己的held/lease上限时只拒绝该消费者新工作。字节依§4.3的(consumer,allocation)首次/最后引用计账，同consumer多lease不重复加Bytes，所有lease及pending-release分别保留槽。其它consumer仍须满足全局容量/槽限制，独立额度不保证全局一定有空位。队列 MaxQueuedOperations=0 时立即背压；非零使用 .NET 10 bounded Channel Wait 模式，并在排入前取得等待槽，不无限创建 WriteAsync 等待者。生产原帧不 Drop；显示 latest-wins 由 Viewport 取消自己的请求和释放自己的结果。

超时、断连和关闭只停止新接纳/发停止意图；在用资源以原请求 QueryOperation 查询，不重新发可能仍运行的复制/native 工作。DrainUnknown 的资源、source 借用和预算保持占用，直到原 Owner 观察完成或监督进程退出/整段隔离重建。不得因 GC、PID消失、UTC期限到达或窗口关闭归零。
## 7. Tile、Pyramid 与缓存

### 7.1 真实超大图与公开 source 端口

不得为虚拟全图分配完整像素或先解码整图再称按需读取。CopyStorage只接收§4.3固定byte[]容器及预算支持的驻留帧；逻辑全图超过C或驻留预算时进入外部有界tile source，不自动分段复制全图。来源为Replay/对象存储或已发布tile序列，由宿主装配，不新造文件库。单个CPU tile仍用Core及§4.3单行/单allocation硬界限校验，按预算拒绝；Core的long访问公式保留，全图逻辑尺寸不当作已分配字节。本切片工程 `Asun.Modules.ImageFrame.Tiles`、namespace 同名，只引用 Core/Resources。下列端口是已接收的 Tiles API v0.1 规格，未实现，所有权沿 §4.3：

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.ImageFrame.Resources;
using Asun.Modules.ImageFrame.Core;
namespace Asun.Modules.ImageFrame.Tiles;
public enum LayerPurpose { SourceExact, DisplayOnly }
public enum TileSourceOwnership { Borrowed, Transferred }
public sealed record TileSourceCapabilities(
    int MaxTileWidth, int MaxTileHeight, int MaxHalo, int MaxInFlight,
    long MaxReturnedCpuBytes, long MaxReturnedNativeBytes,
    long MaxReturnedGpuBytes, long MaxScratchBytes,
    bool SupportsRandomRead, string AdapterVersion);
public sealed record PixelMap(
    double ScaleX, double ScaleY, double OriginXCorner, double OriginYCorner);
public sealed record TileLayerDescriptor(
    int Level, int Width, int Height, LayerPurpose Purpose,
    PixelMap ToSource, string GenerationMethod, string ParameterRevision);
public sealed record TilePlaneDescriptor(
    PixelScalarKind Scalar, ByteOrder ByteOrder, int ChannelCount,
    PlanePacking Packing, PlaneRole Role, string Unit,
    double Scale, double Bias, ImmutableArray<string> Channels);
public sealed record TiledFrameDescriptor(
    FrameKey Key, int SourceWidth, int SourceHeight,
    ImmutableArray<TilePlaneDescriptor> Planes,
    string ContentHash, string DomainRevision, string CoordinateReference,
    ImmutableArray<TileLayerDescriptor> Layers);
public sealed record TiledReadRequest(
    Guid RequestId, string ConsumerId, FrameKey Key, int Level,
    ImmutableArray<int> PlaneIndices, PixelWindow Window, int Halo,
    BoundaryPolicy Boundary, ReadIntent Intent, TimeSpan Timeout);
public sealed record TiledReadResult(
    ReadResult Read, TileLayerDescriptor? Layer);
public interface ITiledFrameSource
{
    Guid ServiceEpoch { get; }
    TiledFrameDescriptor Descriptor { get; }
    TileSourceCapabilities Capabilities { get; }
    ValueTask<TiledReadResult> ReadTileAsync(TiledReadRequest request, CancellationToken ct);
    OperationLookup QueryOperation(Guid serviceEpoch, Guid requestId);
    ValueTask<DrainReceipt> CloseAsync(TimeSpan observationTimeout);
}
public sealed record TileCacheLimits(
    ResourceLimits Resources, string SourceConsumerId,
    int MaxEntries, int MaxWaitersPerKey,
    int MaxSourceOperations, TimeSpan SourceReadTimeout);
public sealed record TiledSourceCreateResult(FrameError Error, ITiledFrameSource? Source);
public interface ITiledFrameCacheFactory
{
    TiledSourceCreateResult Create(ITiledFrameSource source,
        TileSourceOwnership ownership, TileCacheLimits limits,
        TimeProvider timeProvider, IFrameEventSink? events);
}
public readonly record struct TileSize(int Width, int Height);
public sealed record TileRecommendationRequest(
    TiledFrameDescriptor Frame, TileSourceCapabilities Capabilities,
    TileCacheLimits Limits, ImmutableArray<TileSize> AllowedTileSizes,
    int Halo, int ConcurrentRequests, ReadIntent Intent,
    int ViewportWidth, int ViewportHeight);
public sealed record TileRecommendation(
    FrameError Error, FrameKey Key, string ContentHash,
    string ProfileId, string ProfileRevision,
    string DomainRevision, string LayerParameterRevision,
    string AdapterVersion, TileSize? Tile,
    int DisplayLevel, long WindowScalarBytes, long ReservedCpuBytes,
    ImmutableArray<TileSize> RejectedSizes);
public interface ITileRecommendationService
{
    TileRecommendation Recommend(TileRecommendationRequest request);
}
```

Descriptor为来源不可变快照；Planes数1..64，每项Scalar/ByteOrder/Packing/Role及通道值域沿Core，单位/Scale/Bias/Channels沿§4.2。Layers按level从0连续，数量1..32；0为SourceExact、源实际尺寸及单位映射，其余为DisplayOnly。Width/Height正，ContentHash为来源冻结的算法标识+摘要（不是裸文件名）；DomainRevision、坐标、GenerationMethod/ParameterRevision非空，default/null集合拒绝。PixelMap为有限正缩放和有限角原点，映射公式：`sourceCenterX = OriginXCorner + ScaleX*(ActualWindow.X + localX + 0.5) - 0.5`，Y同理；Scale不因tile索引重算。源层crop为Scale=1、Origin=0；主路线尺寸归一化LOD为ScaleX=SourceWidth/LayerWidth、ScaleY=SourceHeight/LayerHeight。来源必须验证该映射与生成过程一致，不能只填写比例数字。

Tiles协调工厂的计划实现名为FrameTileCacheFactory，Create校验source能力、描述及ResourceLimits；MaxEntries/MaxWaitersPerKey/MaxSourceOperations正，SourceReadTimeout有限，source尺寸/halo/in-flight与上限来源明确，scratch及CPU/native/GPU返回最大量非负且总量不为0。MaxSourceOperations不得高于source.MaxInFlight或Resources.MaxActiveOperations；MaxCacheBytes<=MaxCpuBytes，MaxEntries<=MaxReceipts。随机访问主路必须SupportsRandomRead=true，否则只允许宿主顺序流读取、不装随机缓存。任何资源维度不满足在source启动前BudgetExceeded/UnsupportedFormat，不能依赖source分配后OOM来限流。

当前可先接收的Tiles软件切片只允许CPU可同步复制的source（MaxReturnedNativeBytes=MaxReturnedGpuBytes=0），拒绝调用其它后端；保留多资源字段用于后续显式适配接收，不混入该切片。CPU lease对应一块§4.3有界byte[]，MaxReturnedCpuBytes在1..C，MaxScratchBytes在0..C；source其它容器路线须另行接收，不由实现者任选。source回报的Allocations/Metadata/SourcePlaneIndices必须与Descriptor和请求一致，不因为ContentHash相同绕过验证。MaxReturnedCpuBytes可大于窗口标量量（例如共享整帧）；每个不同in-flight key保守预占最大返回+scratch，同key新等待者不重复预占全局物理字节，成功后按AllocationId去重结账。

Source成功返回带AllocationCharge的lease，AllocationId全生命周期稳定且同Id必须同Kind/Bytes，正字节数且无重复项；片段Layout容量不冒充实际allocation容量。source在自身账内执行真实分配及scratch限额，协调器的预占只是其受控范围的保守承诺；不能将两层快照相加。结果门内先核全部charge，计算新增唯一allocation的actual delta，再整笔以预占换actual/受保护引用，释放去重节余；同Id已记账时actual delta=0。source返回后scratch或操作借用仍未确认结束时保留对应预占，不能只看到lease即清账。返超能力或同Id身份变了为Conflict，旧账/旧lease不变，新结果隔离并追踪异常实际量直至归还，不用改小Bytes掩盖来源违约；这是source验收失败，不能声称该次峰值满足硬上限。缓存握持每个entry唯一上游lease，以自己的注册/外部lease/scope计数派生只读包装，不把同一上游lease对象交给两个等待者。不同entry若共享同allocation，physical/cache bytes各按唯一Id计一次，entry/上游lease槽各自计数；SourceConsumerId在上游也按§4.3首次/最后allocation引用计logical，不能按entry数重复加Bytes。

缓存wrapper是独立source epoch，QueryOperation以wrapper回执为准，保留原source请求关联用于未知排空对账。Borrowed的Close只关闭wrapper请求/cache/自身借用，不调用共享source.Close；Transferred只在Create成功后接管source的关闭责任，Create失败仍由调用方拥有。内部in-flight用自己的token，不以单个等待者token取消共同source；已有交付lease不能被取消等待者撤销。descriptor/source版本改变不在原wrapper内更新，必须新建实例和key修订。源原件持久化仍归外部Owner。

Transferred的source关闭必须等wrapper在途及包装lease退出；source.Close的DrainUnknown沿用其真实回执，不伪造wrapper Closed。Borrowed只在wrapper持有的上游lease及source操作借用实际结束后可声明ResourcesReleased，不等待其它外部消费者。缓存MaxCacheBytes仅限制cache自身持有的CPU allocation，cache未持有但已交付/在途的资源仍计MaxCpuBytes；同allocation只有一份物理容量但全部存活引用保留至最后释放。source版本/Descriptor在实例期内变化视为Conflict并停止新工作，而非取新的Descriptor覆盖旧回执。

SourceConsumerId由宿主显式登记到上游source并传入TileCacheLimits，所有内部上游读取使用该id，不冒用某个等待者ConsumerId。wrapper对自己Consumers分别隔离/计费；上游只看wrapper这一个source消费者及自己的限额。未登记上游id返回InvalidArgument且不重试其它id，不从服务名称自动推断。TiledReadRequest幂等比较包含level和所有Resource Read字段，并绑定Create时Descriptor完整快照；默认相同尺寸不同层/Intent不能共享回执。上游限额不足为其明确拒绝，wrapper不扩容/修改source配置。

wrapper的Resources.ActiveOperations/QueuedOperations及每consumer相应限额计客户端等待/交付操作；共同source工作另由MaxSourceOperations按不同in-flight key计一个工作槽，不再作为第二个客户端操作计数，上游则按其自己的操作计数。共同key已有source运行时，新客户端请求取得自己的active/queued槽与MaxWaitersPerKey槽，不能绕过这些限制。缓存自身是内部Owner holder，不伪造某个A/B consumer发布；仅其真实交付/在途逻辑预占记到对应consumer，cache物理容量由MaxCacheBytes及MaxCpuBytes约束。

ExactSamples只接受level0/SourceExact；DisplayOnly用于浏览、不得返回测量原值。本版不批准算法金字塔，未来算法层必须另增资格引用后升契约，不能把DisplayOnly改名放行。ReadTileAsync使用实际level尺寸校验窗口，返回的Slice以实际窗口为局部原点、逐plane域，不额外改变强度/单位。错误时Slice/Layer为null；成功层必须等于请求层的冻结描述。消费者拥有返回lease；source/cache只能撤销自己的持有权。source可被多个宿主共享，关闭一个宿主只能Release自己的lease，只有source Owner可Close。缺tile为NotFound/AdapterFailure，不能输出黑块当正常数据。source断开后保留已交付lease，不能强制回池。

### 7.2 halo、分块与缓存执行

Core窗口严格在level内；先checked扩大halo再与实际边界比较。RejectMissingSupport要求每个选择plane的ActualWindow内样本全部有效；ClipAndMarkInvalid可返回缺口，但不提供物理填充。调用算法按组合支撑请求halo：连续半径r1/r2的局部运算所需至少r1+r2，不取最大值；具体算子支撑由算法Owner给出。运算输出只裁core，不能把halo重复计为检测结果。连通组件、全局归一化、频域、长轮廓和跨tile拟合没有等价合并资格时，宿主请求有预算全局执行或拒识，本模块不实现这些业务算法。

缓存key固定含SourceKey/ContentHash/DomainRevision、level/plane/format、window/halo、边界/ReadIntent、目的层GenerationMethod/ParameterRevision、坐标映射及适配器版本；ConsumerId不进物理内容key，但宿主授权/交付与模块配额每次独立验证。同key in-flight只运行一份source工作，每位等待者独立取消及lease；最后等待者离开只发停止意图，source真实完成后才归还预算。已有结果同key不可变，同key不同内容为Conflict。

缓存预算先对每个新key原子预占source最大返回+scratch（返回allocation已覆盖source持有，不另加窗口标量量）；cache自身预计持有也占MaxCacheBytes，结果按allocation去重换账。使用LRU，仅无外部lease/scope/fence的条目可驱逐。没有可驱逐项为BudgetExceeded，禁止强驱逐已交付tile。MaxCacheBytes=0禁用复用而不是无界；持有与在途容量仍受全局CPU预算。停止source新请求→取消等待者→等待in-flight→撤销cache自身引用→等待交付lease/fence→释放；禁止Close直接清空活跃条目。entry最后包装/cache引用退出后Release其上游lease；该lease的Drain=Drained证实wrapper借用退出后才撤wrapper对应引用，即使上游StorageReleased=false（source/其它消费者仍持有）。同allocation仍有其它entry引用时不减wrapper actual。失败条目不长期缓存为Empty，失败后新RequestId可重新读取，但原未知工作未释放前不得重跑同key。

wrapper在同一门内接纳每个等待者并预留其结果lease槽、receipt、active/queued与MaxWaitersPerKey槽。cache命中时已知allocation，consumer logical delta只为首次未持有Id的Bytes；未完成key无法证明实际allocation身份时，每位等待者保守预占MaxReturnedCpuBytes的consumer逻辑额度（同consumer多未完成请求也分别预占，不猜共享），同key的全局物理仍只预占一份。结果确认后按(consumer,allocation)去重，门内先建结果holder再撤该等待者逻辑预占；同consumer后续lease bytes delta=0，lease槽仍+1。此保守预占可能拒绝在完成后可共享的请求，调用方可在结果已知后新RequestId命中重试，不能绕过在途限额。协调器共同source执行/scratch预占归新key内部operation holder，不冒用等待者consumer；真实source内的执行/scratch按上游SourceConsumerId计账，不按等待者重复计物理；全部consumer额度不求和限制Create。source内部调用使用独立SourceReadTimeout和wrapper生成的RequestId；DrainUnknown保持关联/物理预占及未结束holder并查询原source epoch/request。单等待者取消只撤自己的未交付逻辑预占/结果槽，不能撤共同工作容量；取消后迟到lease只向仍合法的等待者移交，否则先Release上游且确认借用归还再撤共同容量。上游重复RequestId只有回执无lease时不伪造租约。LRU命中/驱逐/Close与新holder门内线性化，不留暂时减账窗口。

### 7.3 金字塔路线、参数改变与建议

显示LOD主路线是全域合法强度/颜色平面 `zoom_image_size(...,'weighted')`，按实际尺寸生成、缓存不可变层；每层目标 `ceil(previousDimension/2)`，任一目标边小于2就停止（遵守算子值域），不造1像素 native层。层的映射绑定源实际尺寸及生成方法，奇数尺寸如5×3→3×2，比例5/3和3/2，不能按2^level反推。Byte/Int16/UInt16/Float32在所读算子输入范围，Float64等不支持格式拒绝派生，不静默降精度。

该路线 `weighted` 缩小有预滤波；bilinear/bicubic不作缩小抗混叠，不能作为静默性能退路。域有洞或有效非有限值时不执行全图weighted，也不将 nearest-neighbor mask 宣称为滤波核完整支撑；返回InsufficientSupport，由宿主使用源层有效tile浏览。高度/Mask不以显示强度路线派生物理数据；需要LUT投影由Viewport/已批准显示适配器明确产生DisplayOnly来源。全图+输出+scratch预算不足时只使用来源已提供且合格的globally aligned DisplayOnly层或源层有界窗口；不对孤立tile各自zoom然后拼接。这样明确保留超大图入口，局部滤波等价资格未关不伪造层。

系统int_zooming必须由独立视觉运行宿主统一冻结；主派生路线要求false，缺失/不匹配则拒绝该派生能力或进入已配置独立worker，模块实例不调用set_system修改进程全局状态。GPU路线与CPU不是自动等价，独立资格前不启用。参数/目标尺寸/domain/算法/backend改变产生新Layer ParameterRevision并使缓存不命中，原lease仍读取旧值。

自动建议只输出候选，不写生产配置。宿主传入有限AllowedTileSizes、source能力和Profile限额；按下列唯一计算规则排除不支持/超额选项，输出选择与消耗分解、源/Profile修订及拒绝项。候选由宿主显式采纳并产生参数修订；FrameKey、ContentHash、DomainRevision、source参数/AdapterVersion或Profile改变令其过期。ExactSamples永远0层；无峰值/时延实测不把建议称最优。

公开入口为§7.1 ITileRecommendationService.Recommend，计划无参数实现类TileRecommendationService；仅纯值计算，不读source、持lease或创建线程。请求结构/能力/限额先依本节Create规则校验，AllowedTileSizes非default且1..64项、严格唯一且各维正，Halo在0..min(1,048,576,Capabilities.MaxHalo)，ConcurrentRequests在1..min(MaxSourceOperations,MaxInFlight)，ViewportWidth/Height正。仅当前CPU source适用。以选定层最坏窗口宽高`min(layerDimension,tileDimension+2*Halo)`计算checked标量量：宽*高*sum(ChannelCount*scalarBytes)。tile+halo不得超source.MaxTileWidth/Height；这些能力尺寸表示包括halo的实际输出窗口，不是core尺寸。sort按面积降序、再宽/高降序，超过实际层的候选视为裁后实际core（仍返回原候选，尾块依实际窗口）。不支持几何对齐的来源不能装随机缓存，不凭空猜alignment字段。

ReservedCpuBytes=checked(ConcurrentRequests*(MaxReturnedCpuBytes+MaxScratchBytes))，表示空缓存下ConcurrentRequests个不同未知key的最坏物理承诺，同key共享/已知allocation命中实际接纳按§7.2去重；纯值Recommend没有运行时allocation表，不能预先减掉假定共享。返回allocation已含WindowScalarBytes，不重复加，pin只延长其持有期。候选每plane单行及WindowScalarBytes须<=C，MaxReturnedCpuBytes/MaxScratchBytes沿§7.1容器能力；能力超C用UnsupportedFormat，候选容量或checked溢出不支持时列入拒绝项。WindowScalarBytes不得超MaxReturnedCpuBytes/FrameBudget有效字节上限，ReservedCpuBytes不得超MaxCpuBytes，域限额沿FrameBudget。Recommend不保证运行时consumer余量，Read每次独立检查其logical/lease/operation限额。显示层选Dimensions同时不低于min(viewportDimension,sourceDimension)的最大level；无合格DisplayOnly层回到0，ExactSamples固定0。无合法tile返回BudgetExceeded、Tile=null、DisplayLevel=-1、字节测值=-1，并列出所有拒绝项；其它无效输入Error=InvalidArgument或UnsupportedFormat，同样无候选。成功Error=None并记录Profile/Domain/Adapter修订，RejectedSizes保留此前被拒候选（排序后次序），不带“最快”结论。候选不代表域支撑合格：具体窗口仍须ReadTileAsync按各plane域验证。

## 8. 状态、错误码与恢复语义

公共错误以 §4.3 FrameError 为唯一枚举，IFR 键用于三语诊断显示和稳定映射，不另造返回状态。Core 使用 ValidationErrorCode，不套资源生命周期。单次 Read 不返回 Partial；批量部分缺项由宿主逐项汇总，各项保留原回执，不把 Partial 当 durable 提交状态。

| 诊断键 | FrameError | 条件与恢复 |
|---|---|---|
| IFR-001 | InvalidArgument | 空身份、非法单位/索引/窗口/时间/枚举；修正参数后新请求 |
| IFR-002 | UnsupportedFormat | 未注册格式/压缩/能力，或CopyStorage单行/单块超过§4.3的C；超大图接有界tile source，不分段复制或降位深 |
| IFR-003 | LayoutOutOfBounds | checked 溢出或越界；拒绝，无 native |
| IFR-004 | BudgetExceeded / BudgetUnavailable | 字节/元数据/队列/回执/消费者限额缺失或超限；背压，不 OOM |
| IFR-005 | LeaseClosed | 关闭/已释放不能新开 scope；在用 scope 完成后 Release |
| IFR-006 | InsufficientSupport | core/halo/domain 支撑不够；算法请求扩大合法窗口或拒识 |
| IFR-007 | Cancelled | 已实际停止并归还操作资源；消费方自行释放独立 Slice |
| IFR-008 | Timeout | 实际停止后 TimedOut；未停止用 IFR-010，不自动重跑 |
| IFR-009 | AdapterFailure | 来源/native/解码失败或有效预算内byte[]分配失败；清理独占临时物，保留原件/诊断。CPU分配失败按§4.3撤actual/reserved，不重试扩容、不视为预算拒绝 |
| IFR-010 | DrainUnknown | 在途使用或析构未确认；隔离、继续查原请求，禁止回池 |
| IFR-011 | StaleRevision | 旧修订/旧视图显示权失效；仅释放自己的结果 |
| IFR-012 | Conflict | 相同请求/帧身份不同摘要或已存在；不覆盖原资源 |
| IFR-013 | Unknown | 结果不能证明；保留关联与事实缺口，不伪造成功 |
| IFR-014 | InvalidSample | 有效域内非有限标量；来源修正缺测域，新修订重发 |
| IFR-015 | NotFound | 当前 epoch/保留期查不到；不能据此认定此前未执行 |
| IFR-016 | Closed | 服务已关闭；查回执，使用新服务 epoch |

## 9. 线程、资源与所有权

只读描述并发可用。锁只保护接纳、预算、计数、关闭和注册状态；外部回调、行复制、native、IO、析构均在锁外。锁序固定服务接纳门→storage门→lease/scope门；不反向调用，不同步等 UI/事件回调。对每次操作单独联结取消，不能把一个窗口 token 注入所有消费者。

CPU 和 pinned CPU 是同一物理 allocation，另计 pin 持有时长而不重复计 CPU字节；HALCON 独立拷贝和 GPU纹理是新副本，分别计 native/GPU预算。GPU按§19.3先同步复制源CPU至独立upload buffer，源scope在SubmitUpload真返回后可结束；upload及GPU资源提交后持有至fence/Owner确认退出。未来直接读源pin的后端才需源pin延长至其最后使用完成，本版不启用。设备 lost 或 fence无法观察为 DrainUnknown，UI放弃显示不能视为已释放。不得把像素/GPU纹理放入模块事件或 ViewModel 长期保存。

FrameService 不执行数据库/文件提交、相机重连、ROI编辑、算法判定、工艺关联或质量放行。持久化只经公开不可变对象端口由 storage-database/Replay宿主提供，文件保留/事务/恢复规则归该 Owner。本模块只校验返回窗口的字节/域/修订；不复制一个私有对象存储或 manifest提交器。
## 10. UI 适用性与宿主投影

IM-006 是无 UI 资源 DLL，不交付控件、独立页面或 WPF 工程；本轮 UI/DevExpress 控件 API 审核 NotApplicable，不凭空新增资源面板。既有“可选 UI”指 Viewport/宿主消费 ResourceEvent/OperationReceipt 的只读投影，绘制、Docking/Grid、布局、语言切换和权限归这些消费者的唯一指导，不把它们的控件/状态写入本模块 API。

投影可显示帧修订、尺寸/格式、有效域、占用/上限、持有者、队列及真实排空状态；不得编辑 FrameDescriptor 或显示制程 PASS/NG。查询必须用原 RequestId；旧视图仅淘汰自己的结果显示权并 Release，不取消其它消费者。三语错误键由宿主资源解析，例如 IFR-004：`资源已满，请等待` / `資源已滿，請等待` / `Resources full. Wait.`；IFR-010：`资源仍在使用，请查询状态` / `資源仍在使用，請查詢狀態` / `Resources still in use. Check status.`；详细技术字段与简短操作文字分开。接入验收只在固定1920×1080基线中复用 Viewport检查，任务栏/边框由宿主扣除，不运行额外分辨率矩阵、不改显示设置。

## 11. 无 UI 最小 Host 与两个消费者

首片 §4.5 为显式合成值算例。Resources 的 console TestHost 只引用本模块 Core/Resources 和 BCL；以注入的工厂、ResourceLimits、TimeProvider、IFrameInputRows 构造服务。合成来源为按 plane/y/x 固定生成的 UInt16 小端渐变，不冒充相机数据。调用顺序：Create→PublishCopyAsync→两个不同 ConsumerId 与 RequestId 各 ReadAsync→各 TryOpenReadScope/CopyRow/Dispose→各 ReleaseAsync→RetireAsync→CloseAsync。任何失败查原回执；不能在仍 Draining 时释放来源。

以下为使用 §4.3 接口的局部调用示例，`frames`、`descriptor` 和 `consumer` 由上述宿主提供；尚未构建执行：

```csharp
var result = await frames.ReadAsync(new FrameReadRequest(
    Guid.NewGuid(), consumer, descriptor.Key,
    ImmutableArray.Create(0),
    new PixelWindow(0, 0, descriptor.Layout.Width, descriptor.Layout.Height),
    0, BoundaryPolicy.ClipAndMarkInvalid, ReadIntent.ExactSamples,
    TimeSpan.FromSeconds(2)), CancellationToken.None);
if (result.Slice is { } slice)
{
    try
    {
        if (slice.TryOpenReadScope(out var scope) != FrameError.None)
            throw new InvalidOperationException("Read scope unavailable");
        using (scope!)
        {
            var row = new byte[checked((int)slice.Layout.Planes[0].RowBytes)];
            var error = scope!.CopyRow(0, 0, row);
            // Consumer checks error and domain before interpreting the scalar.
        }
    }
    finally
    {
        var release = await slice.ReleaseAsync(TimeSpan.FromSeconds(2));
        // LeaseClosed is not proof of StorageReleased; keep/query unknown resources.
    }
}
```

这里只示范同步行复制；下游异步/native算法必须独立持有原 lease或适配 pin直至真实完成，不能把 scope关掉再用指针。正式可运行 Host 要检查每个 error、记录 RequestId，并在退出前要求 Close.ResourcesReleased；本示例的2秒、尺寸及容量只属于合成测试，不是现场阈值。

第二消费者验收固定为相机适配器的 CopyRow稳定借用输入+算法consumer-A，以及 Replay行输入+回放consumer-B；二者独立引用 DLL、不引用平台Shell。对同一已发布 FrameKey 分别取得 A/B lease：A取消或关闭scope→B仍可读同样值→Retire阻断新读而B仍可读→B归还后storage析构恰一次。再以两个服务实例发布相同 Guid验证无静态串扰。Viewport作为第三个可选观察者验证latest-wins，不是代替第二无UI消费者的条件。

资源合成计账例（字节值仅用于软件断言）：UInt16、5×3、row=10、单plane目的容量30、scratch10；全局MaxCpuBytes=40，发布consumer-P的MaxHeldBytes=40，A/B各MaxHeldBytes=30，其余frame/receipt/operation限额显式足够，A的MaxLeases=2。Create成功，即使held上限之和100>40。P发布峰值actual+reserved=40，scratch归还后全局actual=30、P logical=30。A/B各读同allocation成功，全局仍30、A/B logical各30；A第二个新RequestId取得第二lease，A logical仍30而lease数2；A第三个请求仅因MaxLeases拒绝，不按held60拒绝。Retire撤P holder后，A一个lease已Release但scope未退出仍占其lease槽且logical30；另一lease已退出也不能提前减30。B归还不影响A scope，A最后scope Dispose后所有引用退出、array引用移除，global/consumer账归零且StorageReleased恰一次。另一个新30B allocation即使消费者未超限，在第一个30B仍活跃时其目的+scratch40需要总70>40，分配/Source之前BudgetExceeded；不能用共享例扩大真实容量。

Tiles最小Host使用一个FakeTiledFrameSource：其内部只用Resources发布5×3 UInt16单plane合成渐变`value=y*10+x`、Full域，并把Resources.ReadAsync的slice附加0层描述（Scale=1、Origin=0）；不访问文件/HALCON。宿主显式给source注册`tile-cache-input`、wrapper注册A/B，FrameTileCacheFactory.Create(source,Borrowed,limits,TimeProvider.System,null)，两个不同请求读相同(0,0,4,2)，各取得不同wrapper lease而上游只读一次；A归还后B局部(2,1)仍为12。Close wrapper并归还B后上游仍可由另一合法消费者读取，最后由source Owner Retire/Close内部Resources。Transferred变体在wrapper关闭和全部lease退出后关闭source一次；Create失败不关闭source。断连/迟到/不释放测试fake用受控TaskCompletionSource和计数器注入，无固定sleep假定时序。

上述Tile fake在wrapper全局MaxCpuBytes=40、MaxCacheBytes=30、A/B各MaxHeldBytes=30、MaxReturnedCpuBytes=30、MaxScratchBytes=8时：同key两个等待者global reserved只38，各consumer logical reserved各30；结果完成后wrapper actual=30、reserved=0、cache=30、A/B logical各30，上游只一lease，P保留原图的上游actual也30但不与wrapper快照相加。A的第二个已知key命中只加lease槽。A取消但B仍等待时不得把共同38预占减为0；全部等待者取消且source未退出时仍保留38。两个不同key在身份未知时各需38，global40拒绝第二个；完成后如第二key也返回同Id的30B，则需先具备保守预占空间才能启动，成功结账后actual仍30，不能在启动前猜共享而减预占。

参数建议的合成确定性例：source 5×3、UInt16、0层和已有DisplayOnly 3×2层；能力MaxTile=4×2、MaxHalo=0、MaxInFlight=2、MaxReturnedCpuBytes=30、MaxScratchBytes=8；候选{4×2,2×2}，并发2、CPU限96、FrameBudget字节64（其余必须有合法来源与限额）。ExactSamples结果tile4×2、level0、WindowScalarBytes=16、ReservedCpuBytes=76；CPU限改64时两候选都BudgetExceeded，无tile。Display视口3×2时选level1，映射5/3与3/2；该例只证明有界推荐计算，不证明weighted实际像素误差、HALCON性能或现场吞吐。

## 12. 正常、边界与失败案例

| 案例 | 期望 |
|---|---|
| 正常 Gray16 正 stride | 发布、算法 lease、tile 读取和释放完成；底层归还一次 |
| `H=3,rowBytes=6,stride=8,offset=0`、可访问 21 字节 | `IFR-003`，不调用 native；22 字节才可接受 |
| 负 stride=-8、offset=16 | 逐 plane checked 校验通过时可读；offset=0 必须拒绝 |
| A 取消、B 仍读同一 storage | A 只失去自身 lease；B scope 结束前 storage 不归还 |
| H=1或合法空域 | H=1仍校验offset/format；有布局且有效域空用Empty，payload缺失为非法输入，不造0×0 native图 |
| tile 跨尾块/奇数 pyramid | 返回实际窗口和父坐标映射；不重复/丢失边界像素 |
| domain 有洞、halo 不足 | 返回有效域/`IFR-006`；不把洞补成 0 后量测 |
| native 取消后迟到 | 等待真实完成或隔离；迟到结果不得发布到新 revision |
| 同FrameKey/RequestId冲突 | `IFR-012`，不重新复制或覆盖；新内容新Revision，新读取新RequestId |
| cache超预算/外部source读取失败 | 分配前IFR-004，来源失败IFR-009；释放已确认独占的临时资源，保留原帧；磁盘IO不由CPU Core执行 |
| CPU单行/紧凑总量超过C，Core long布局仍合法 | IFR-002/UnsupportedFormat，Source/分配次数均0；可改有界tile source，不静默分段 |
| 预算内目的或scratch数组分配失败 | IFR-009/AdapterFailure而非IFR-004；无Frame/Source调用，清除已分配引用及预占后OperationResourcesReleased=true，不声明CLR已回收 |

## 13. 测试与验收矩阵

实现必须先有可无UI运行的确定性断言harness，再接适配器。Core、纯CPU Resources、Tiles/fake source首版测试沿DEV-GOV-010 §3.1：Microsoft.NET.Sdk、net10.0、OutputType=Exe，无PackageReference，只引用对应受测工程/其模块依赖与BCL；使用固定TimeProvider、可控异步闩锁及有限测试deadline，不引入待选测试包。执行方式唯一见§16。全部必需断言完成才exit 0；任一失败、未完成或必需项跳过返回非零并列用例ID，进程级超时同样不得判成功。HALCON/native/GPU/IPC等后续资格不由该harness代替。至少包含：

| 类别 | 断言 |
|---|---|
| Contract/Schema | Core v0.2/Resources v0.1必填/空值、端序、单位、版本和首错稳定；未知枚举/旧字段缺失拒绝；null/default不抛NullReference作为契约错误 |
| 布局数学 | 正/负 stride、padding、H=1、最小负整数、checked 溢出、21/22 字节边界 |
| 资源竞争 | 获取与关闭线性化；A/B lease、重复释放、最后归还恰好一次；不从 0 复活 |
| CPU-R01：共享/双层额度 | §11的30B allocation、global40、P40/A30/B30 Create成功；A/B logical各30、global30；A第二lease bytes不变，第三lease依槽拒绝；消费者active/queued上限之和也不限制Create，实际全局/consumer槽分别拦截 |
| CPU-R02：真实容量/回滚 | 不同30B目的allocation在global40不能并存；目的+scratch接纳checked且原子；竞争者只一方取得最后容量/lease/receipt槽。失败/取消无半接纳，reserve→actual无空隙/双计，交付先增holder后撤operation |
| CPU-R03：pending/身份 | 同consumer多lease最后引用才减Bytes；Release有scope时保留logical及lease槽，直到同步CopyRow退出；Retire/Close不能撤外部引用，重复Release不负计。source同Id不同Kind/Bytes返回Conflict，旧条目/lease数值不变 |
| CPU-R04：容器/分配失败 | 预检独立验证row=C/C+1及total=C/C+1；在.NET10的C=1GiB时，UInt8 W=536870913,H=1两alias plane各row合法，紧凑sum=1073741826>C，Core可合法但Publish分配/Source次数0。row=536870912,H=2的total=C仅通过容器预检，不据此声称能分配1GiB。测试内部故障点在目的/scratch分配分别注入OOM，不改变生产new byte[]路线；AdapterFailure、无Source/Frame，部分实际数组引用清除且账归零 |
| TILE-R01：共享等待者 | §11的同key A/B只38B物理预占、各30B逻辑预占；已知同consumer命中bytes delta0但新增lease槽。取消A保留B与共同账，最后等待者离开未知source仍留共同预算；不同key身份未知不能猜共享；不同entry同Id成功结账actual/cache去重，上游lease各自归还 |
| 发布隔离 | 相机环形 buffer 重写不改变已发布帧；复制分支保留来源修订 |
| 取消/排空 | native 迟到、超时、取消、worker 关闭；排空失败进入 `Isolated`，不回池 |
| domain/halo | ROI 外/洞/边缘核被排除；halo 组合支撑和跨 tile 结果可追溯 |
| tile/pyramid | 5×3尾块/3×2层父映射、HALCON闭区间与模块半开端点、域洞与halo；分块算法等价由算法Owner资格，不由本模块crop测试放行 |
| cache/预算 | key完整、同key一份in-flight/两等待者取消隔离、active/queued/receipts/行段上限、在用tile不驱逐、CPU/native/GPU分账；Close与生成/最后借用竞争 |
| 参数建议 | §11合成4×2/76字节算例，容量96→64的确定性拒绝、候选排序、halo超过能力、未知枚举、source/Profile/domain修订过期；Recommend不执行source/native、不写配置 |
| 适配器 | AsunImage 公共签名按 HALCON 26.05 资料核对；不把 native 类型穿透核心 |
| Replay | 固定输入/版本可重放；读取失败、缺资源和旧 revision 显式可见 |
| 第二消费者 | §11两个无UI宿主独立引用，A取消/B持有、Retire/Close/Release交错；第三Viewport投影不替代两消费者资源验收 |
| HALCON适配 v0.1 | §19.1 HAL-R01..03：导入/独立副本/LOD、scalar/域/通道、借用/alias/pin/异常与两消费者；fake与真实26.05资格分别判定 |
| IPC适配 v0.1 | §19.2 IPC-R01..04：IFCP/1.0鉴权/严格长度与hash、子进程复制、重连查询/重复释放/epoch与generation、截断和阻塞不伪释放 |
| GPU协调 v0.1 | §19.3 GPU-R01..04：报价capacity/footprint、提交丢回执、两消费者use/fence、device lost保账、读回原值；真实Owner资格独立 |
| 长稳/恢复 | 多小时有界队列、进程重启、磁盘满/设备断开；无资源残留或未知归还 |

Mock 只能验证核心时序，不能代替 native/HIL/真实相机或现场性能资格。无 HIL、Golden 和真实 Profile 时验收结论只能是软件可验证。

## 14. 性能、容量与可观测性

性能统计不复制算法，沿 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)。Core测Validate入口到返回，异步源/native测接纳到本操作借用与临时资源ResourcesReleased；租约交付后的持有时间、Retire到StorageReleased、Close到所有资源释放单列。调用方算法端到端需把其独立持有/fence纳入，不从本模块Read返回推断完成。

| 切片 | 冻结工作负载与测点 | 资源/失败判定 |
|---|---|---|
| ManagedLayoutValidation | §4.5 plane/行段桶，加null、多错、最小负stride、上下限相等/±1；冷/热、并发1与Profile并发 | 输入构造不计Validate时间；测托管分配/总时长；同值首错等价；无客户目标为NotEvaluated |
| CopyStorage/Lease | UInt8/UInt16/Float32、正负stride/padding、1/3/64plane、Full/Empty/稀疏域、2消费者快/慢、Profile最大驻留帧；阶段为预检/队列/目的分配/scratch分配/复制/注册/交付/归还 | 实际array.LongLength逐Id计payload，actual+reserved<=MaxCpuBytes；每consumer唯一allocation逻辑量/预占、lease/pending槽独立测。超额分配前拒绝；OOM单列失败；Retire/Release后Owner活跃payload归零或保留隔离量，不据此声称托管堆/RSS归零 |
| Tile/cache | 源尺寸含大于驻留预算的逻辑帧；1×N/N×1/奇数/尾块；tile候选尺寸和halo0/组合核支撑、重复热点/随机访问、不同domain/param修订、多等待者一人取消 | 记录source读取字节/次数、cache命中、队列、held及LRU驱逐；热命中不重新source读取；同key只一份在途工作；不能缺块补零 |
| 参数建议 | AllowedTileSizes数1/4/16/64，1..64plane、合法/全拒绝/溢出、Exact/Display、halo0/能力上界±1、Profile允许并发；单独测Recommend入口到返回 | 不含输入构造/图像读取，测托管分配、确定性结果与最坏checked预算；纯值取消/排空NotApplicable，无时延目标为NotEvaluated |
| HALCON/显示LOD | 相同源比较copy主路/qualified extern候选；Full域、UInt16近极值、缩小<0.5、局部有洞、不同backend；ROI裁剪与全图同坐标读取 | 标量/通道/domain/映射正确性先于速度；copy次数/CPU/native峰值/释放；weighted/constant/nearest候选同样本比较但只主路可实施；未知排空不判通过 |
| IPC/GPU | §来源增量的generation/epoch/slot耗尽，进程异常与迟到Release；GPU fence延迟/device lost | 分别量slot总字节、GPU副本及pin寿命；未证释放不回池；实际跨进程/设备证据只用于相应适配资格 |

每个可执行Profile明确冻结输入/hash、源端口版本、适配器/库版本、工作负载/并发、预热数/测量数/最低有效样本数、有限deadline、各资源硬上限、目标及来源修订。无真实尺寸/节拍可先跑显式synthetic profile以测机制；客户目标待采纳时不判性能通过。完成/拒绝/失败/取消/超时/删失/DrainUnknown样本分别保留，不能只挑成功快样本。软件CI断言资源与等价性，不填虚构客户毫秒或计量公差。

诊断按结构化字段记录epoch/RequestId/FrameKey/ConsumerId、版本、plane/window/halo、domain修订、阶段、queue wait、copy bytes/count、CPU/native/GPU实际及预占字节、consumer唯一held/逻辑预占、allocation引用/pending/lease/scope/pin/fence计数、缓存键摘要、析构次数、取消原因、观察时间与Owner释放时间。ResourceSnapshot保持§4.3公开形状，consumer内部账由harness定向断言/宿主诊断查看，不为测试造新公开API。Profile另外测GC托管堆分配/存活/提交峰值及进程RSS/commit，注明与payload不同，不把GC时间算作Owner已观察的释放。日志/事件不写像素、指针、token或凭证；输入证据由宿主提供受控hash引用，不另建文件日志Owner。

## 15. 版本、独立发布与回退

Core、Resources、Tiles的契约/包版本分别冻结，Resources显式绑定Core v0.2，Tiles绑定Resources v0.1；HALCON适配包按当前ImageLibDotNet/26.05引用独立发布。只引用Core或Resources即可运行console，不需平台Shell/WPF/DevExpress/数据库或native隐式初始化。程序集名称和namespace见 §16，不搞静态全局Runtime。

发布在实现后生成实际API/依赖版本、公开能力、变更/回退说明和真实测试结果，当前不提前造交付清单。独立包通过模块自己的测试工程构建/打包；运行时外部原生依赖由适配宿主配置，不下载替换用户程序集。Core v0.1到v0.2没有静默反序列化兼容；含ByteOrder/容量/域限额缺失的旧输入必须由显式转换或拒绝，不能抄默认值。进程内lease/指针/Task不序列化、不跨包版本重用。

迁移顺序：停止旧版新接纳→保留旧epoch查询→旧lease/fence真实释放→保留immutable输入与配置→新实例/新epoch离线重放→比较标量/domain/坐标及资源→宿主切换。DrainUnknown时不卸载DLL或强制复用池，旧Owner隔离保留。回退用原输入/原契约和已资格包创建新实例，不让旧包解释新版缓存；缓存可丢弃，但原输入/用户配置/测试和证据不删除。Replay/Shadow正确且实际Profile通过后才谈相应集成资格。

## 16. 切片落点、允许路径与具体未决门

本轮只有本指导可写，不创建任何工程/代码/测试。以下是后续获准实施的唯一落点：

| 切片 | 工程/namespace（目录根为src/Modules/image-frame） | 测试落点（根为tests/Modules/image-frame） | 最小消费者与当前门 |
|---|---|---|---|
| ManagedLayoutValidation | Asun.Modules.ImageFrame.Core | Asun.Modules.ImageFrame.Core.Tests | §4.5相机布局/Replay布局；ModuleCoreImplementationReady（规格准备），本轮不开代码 |
| CopyStorage/Lease | Asun.Modules.ImageFrame.Resources | Asun.Modules.ImageFrame.Resources.Tests | §11两个无UI消费者，§4.3工厂及行输入；ModuleCoreImplementationReady（规格准备） |
| Tile/cache/参数建议 | Asun.Modules.ImageFrame.Tiles | Asun.Modules.ImageFrame.Tiles.Tests | §7/11固定CPU source→工厂→两消费者及Recommend；ModuleCoreImplementationReady（规格准备） |
| HALCON import/copy/显示LOD | Asun.Modules.ImageFrame.Halcon | Asun.Modules.ImageFrame.Halcon.Tests | §19.1公开端口、Camera/Replay/算法消费者、§17.1算子；适配设计已接收（规格准备），真实适配验收未执行 |
| CrossProcessLease | Asun.Modules.ImageFrame.Ipc | Asun.Modules.ImageFrame.Ipc.Tests | §19.2 IFCP/1.0命名管道复制、可信pair映射、两个独立pair；适配设计已接收（规格准备），真实跨进程验收未执行 |
| GPU resource | Asun.Modules.ImageFrame.Gpu | Asun.Modules.ImageFrame.Gpu.Tests | §19.3托管协调/Simulator及Owner/fence公开端口；ModuleCoreImplementationReady（规格准备），真实D3D12 Owner/native SDK不在本轮范围 |
| 最小Host（验证工具，不是模块UI） | Asun.Modules.ImageFrame.TestHost | 由对应模块测试调用 | 只在真实实现需要时创建，§11console；不得造空Host代替功能 |

工程namespace与程序集名一致；同切片一个Owner。实施允许本切片上述工程、其测试和本指导；禁止其它模块、平台Shell/ViewModel/共享Schema/私有数据库/制程页面/AGENTS/入口/架构/会话登记、参考项目和AsunImage内部。主会话串行更新solution/共享接入与契约映射，模块不越权。引用SDK或File/GPU/native只在对应适配工程；当前没有UI工程。

各切片的唯一工程文件名为相应程序集名加.csproj，工程/测试目录沿上表；实现获准后从仓库根执行：

| 切片 | 构建命令 | 验证命令（net10.0 BCL Exe） |
|---|---|---|
| ManagedLayoutValidation | `dotnet build src/Modules/image-frame/Asun.Modules.ImageFrame.Core/Asun.Modules.ImageFrame.Core.csproj -c Release` | `dotnet run --project tests/Modules/image-frame/Asun.Modules.ImageFrame.Core.Tests/Asun.Modules.ImageFrame.Core.Tests.csproj -c Release` |
| CopyStorage/Lease | `dotnet build src/Modules/image-frame/Asun.Modules.ImageFrame.Resources/Asun.Modules.ImageFrame.Resources.csproj -c Release` | `dotnet run --project tests/Modules/image-frame/Asun.Modules.ImageFrame.Resources.Tests/Asun.Modules.ImageFrame.Resources.Tests.csproj -c Release` |
| Tile/cache/参数建议 | `dotnet build src/Modules/image-frame/Asun.Modules.ImageFrame.Tiles/Asun.Modules.ImageFrame.Tiles.csproj -c Release` | `dotnet run --project tests/Modules/image-frame/Asun.Modules.ImageFrame.Tiles.Tests/Asun.Modules.ImageFrame.Tiles.Tests.csproj -c Release` |
| HALCON import/copy/显示LOD | `dotnet build src/Modules/image-frame/Asun.Modules.ImageFrame.Halcon/Asun.Modules.ImageFrame.Halcon.csproj -c Release` | `dotnet run --project tests/Modules/image-frame/Asun.Modules.ImageFrame.Halcon.Tests/Asun.Modules.ImageFrame.Halcon.Tests.csproj -c Release` |
| CrossProcessLease | `dotnet build src/Modules/image-frame/Asun.Modules.ImageFrame.Ipc/Asun.Modules.ImageFrame.Ipc.csproj -c Release` | `dotnet run --project tests/Modules/image-frame/Asun.Modules.ImageFrame.Ipc.Tests/Asun.Modules.ImageFrame.Ipc.Tests.csproj -c Release` |
| GPU resource | `dotnet build src/Modules/image-frame/Asun.Modules.ImageFrame.Gpu/Asun.Modules.ImageFrame.Gpu.csproj -c Release` | `dotnet run --project tests/Modules/image-frame/Asun.Modules.ImageFrame.Gpu.Tests/Asun.Modules.ImageFrame.Gpu.Tests.csproj -c Release`；真实Owner资格同命令追加 `-- --gpu-owner-host`，宿主注入方式见§19.4 |

上述命令是实施绑定，工程当前未创建，本轮未执行。`dotnet test`不会执行这些Exe，不能以其无报错判通过；§13/19必需断言逐项列明且未完成/跳过/失败必须非零。harness应有有限截止点并由执行宿主设置有限进程超时，阻塞Source测试先释放受控闩锁再完成清理；若超时杀进程，结果为失败/未知，不凭进程退出记录ResourcesReleased。HALCON真实运行、IPC子进程软件验证、GPU模拟协调/真实Owner资格各自区分，不以任何命令未报错声称现场通过。

已作技术决定：进程内复制存储Owner为Resources；Partial只属宿主批量汇总；cache首版仅内存LRU，持久对象归外部存储Owner；源标量level0与DisplayOnly层分离；主路不使用extern。无关Core不再等待这些常规选择。

仍影响特定切片的门：

- 平台正式Frame Schema/域原因/事件映射及identity来源映射：只阻断平台接入，不阻断模块自己的值/资源契约接收。
- CPU资源与Tiles规格已接收；真实source实现与性能分别验收，不把模拟source当文件/native后端交付。
- HALCON主路公开输入/输出与方法已按§19.1冻结，官方HObject/HTuple调用形状见§18.0；仅实际C#重载/封送有歧义时查公共签名或消费工程编译。算子存在性不是门，extern本版不启用。
- §19 IPC可信启动配置、GPU设备Owner与工作注册及各适配真实资源释放/性能资格，仅阻断对应部署/集成；公开协议和端口不再待定。
- 实际客户图像/尺寸/并发/节拍/长期运行目标、相机借用期、真实HIL与现场验收：只影响对应性能或设备集成资格；合成测试不得冒充。
## 17. 逐能力反例与执行断言

这里从两个视角约束开发：图像输入/数值语义视角（buffer、样本有效性、单位与映射），外部接入/故障时序视角（身份、持有者、可查询的真实释放）。弱信号、遮挡与多候选不是帧模块的缺陷算法；模块携带其域/来源，不把低对比误当空图，也不替消费者选目标。

| 能力/反例 | 处理与可判定断言 |
|---|---|
| 正常/负stride | UInt16 W=3,H=3,row=6,stride=8,offset0,buffer22为Valid；buffer21为OutOfBounds。stride=-8,offset16,buffer22为Valid；offset0拒绝。scope值按逻辑行顺序相同，原padding不导出 |
| 空输入与空域 | null对象为InvalidArgument，0宽高为InvalidDimension；合法布局+Empty域为Empty仍计预算；空文件由Replay来源拒绝，不造0×0 HALCON图。Read Empty仍可有Slice并必须Release |
| 大规模/退化 | H=1任意stride只访问一行；Height>1行重叠为InvalidStride；乘加溢出LayoutOverflow；巨量行段在扫描前限额拒绝。1×N/N×1保持源层，不造低于2×2的zoom层；逻辑超大图source只读取实际请求tile |
| 弱信号/遮挡/缺测 | UInt16全0但Full域仍合法，不当Empty；高度有效域内NaN/Infinity为InvalidSample；域外NaN不提升为有效值；每plane不同洞分别返回。低对比和遮挡不触发平滑/补洞/质量PASS |
| 通道/多候选 | 3平面R/G/B与交错3通道由明确顺序解码，不能只读get_image_pointer1第一通道伪称RGB；多FrameKey/多plane选择严格唯一排序，不挑“看起来最好”的帧；物理单位和通道标签缺失拒绝 |
| 参数/版本变化 | ByteOrder改动、域/映射/LOD参数修订生成新描述/缓存key，旧lease值保持；未知枚举/旧Core v0.1缺字段拒绝或显式迁移。UInt16高值缩小与hole域能复现路由拒绝，不能降精度掩盖差异 |
| 接纳/重复/并发 | 相同RequestId不再次调用Source或增lease；不同摘要Conflict；无回执容量/CPU/消费者额度时不复制。Publish/Read与Retire竞争只有接纳或Closed/LeaseClosed，不产生悬空读；两个服务实例不串状态 |
| A取消/B读取 | A/B持不同lease及scope，A取消/Release/窗口关闭只影响A；B仍读原值。Retire阻断新读，B scope退出前StorageReleased=false，全部持有退出析构恰1次 |
| 超时/迟到 | 测试Source在CopyRow中阻塞，期限后原操作Draining/DrainUnknown且保持source/预算；解除阻塞后实际归还，才发TimedOut。迟到旧结果只Release、不覆盖新视图；WaitAsync返回不当底层已停 |
| GPU/native/断连 | 未完成fence、外部callback、进程回执不能观察时保持资源；无特定适配完成证明不返回池。source断开不撤销已交付租约；重连/设备复位不由image-frame发命令 |
| 关闭/未知结果 | scope CopyRow与Dispose竞争不得读回池字节；Close遇到外部held lease返回OutstandingLeaseIds，不伪发Closed；之后Release/Close可继续观察。不同ServiceEpoch查询Unknown，同epoch过保留期NotFound，不由NotFound推定未执行 |
| 缓存/尾块/halo | source5×3, tile4×2，尾块实际1×1；层3×2映射5/3、3/2。两阶段核r1=2,r2=3要halo5，halo3不足拒绝。相同key两等待者只一source工作，取消一个不取消另一个；持有tile不可LRU驱逐 |
| 持久化/第二消费者/回退 | 文件/对象完整提交/hash由storage/Replay Owner证明，模块不生成manifest。两无UI消费者按§11能独立引用、运行、归还；升级保留旧epoch未知资源，不让旧DLL解释新缓存，不删除原输入/配置 |

### 17.1 HALCON 26.05 主路、分支与资源顺序

本轮实际读项目内算子正文 Description/Attention、涉及输入域和参数/Execution说明；静态入口统一为 `ImageLibDotNet.cv2`，不是 HImage 猜测方法名。下列参数为已核语义顺序，不冒充尚未编译的C#重载。模块没有缺陷/测量/分类视觉算法，图像资源适配仍须按这些算子行为实现。

| 功能/实查页 | 冻结路线与分支 | 拒绝/资源顺序 |
|---|---|---|
| [count_obj](../../../halcon算子手册/operators/count_obj.html)、[count_channels](../../../halcon算子手册/operators/count_channels.html)、[access_channel](../../../halcon算子手册/operators/access_channel.html)、[get_image_pointer1](../../../halcon算子手册/operators/get_image_pointer1.html) | 单次导入只接受1个image；每通道以HALCON 1-based编号access_channel，再pointer1读取Type/Width/Height，映射Core scalar。3同类型同尺寸通道可用[get_image_pointer3](../../../halcon算子手册/operators/get_image_pointer3.html)等价批取，但不作为默认快捷分支 | 输入tuple多个image、complex/vector_field等未注册类型拒绝；指针只在原image/独立来源借用存活期读。共享domain对象可能同matrix，不写其指针 |
| [get_domain](../../../halcon算子手册/operators/get_domain.html)、[get_region_runs](../../../halcon算子手册/operators/get_region_runs.html)、[gen_region_runs](../../../halcon算子手册/operators/gen_region_runs.html)、[reduce_domain](../../../halcon算子手册/operators/reduce_domain.html) | image域取单region runs，HALCON端点闭区间ColumnEnd显式checked+1映为模块半开；空runs=Empty。模块域生成HALCON时EndExclusive-1，先自行校验再reduce_domain取交集 | 不用[change_domain](../../../halcon算子手册/operators/change_domain.html)扩张未知域；它不校验region匹配矩阵，越界可崩溃。get_region_runs单region，不能一次传多对象。region/tuple在各自适配finally释放 |
| [copy_image](../../../halcon算子手册/operators/copy_image.html)、[copy_obj](../../../halcon算子手册/operators/copy_obj.html)、[gen_image1](../../../halcon算子手册/operators/gen_image1.html)、[gen_image3](../../../halcon算子手册/operators/gen_image3.html)、[gen_image_interleaved](../../../halcon算子手册/operators/gen_image_interleaved.html) | 主路为逐行稳定借用→紧凑buffer→逐plane gen_image1复制；gen_image3/interleaved是已核语义的候选，不在§19.1首版公开端口启用。已有HALCON需要独立原生图时copy_image物理复制所有通道 | copy_obj仅新引用；interleaved x/alpha可能被舍弃，未批准alpha丢弃，四通道须显式拆/保留。输入pointers有效由适配器负责，算子不验证。buffer直到复制算子真返回后才解pin，失败同样确认无在途使用 |
| [gen_image1_extern](../../../halcon算子手册/operators/gen_image1_extern.html) | 可行性能候选，但当前生产主路不启用。只对紧凑单通道正向矩阵、明确独占稳定allocation、精确ABI/生命周期资格启用 | HALCON不复制、不校验指针/长度；ClearProc为`void(void*)`、cdecl；NULL回调合法却不证明资源会释放。callback delegate须强引用到最后alias析构，异常不可跨native边界，析构exactly-once握手。不满足任一条件回到copy，不反复查“算子是否存在” |
| [crop_rectangle1](../../../halcon算子手册/operators/crop_rectangle1.html) | crop主路先以模块窗口裁/校验，HALCONRow1=y,Col1=x,Row2=y+h-1,Col2=x+w-1；core/halo以实际窗口带父映射 | HALCON允许右下超出但其域只保留来源部分；模块不据返回尺寸假设全部有效。源对象/crop lease覆盖最后使用，尾块不补齐标称大小 |
| [zoom_image_size](../../../halcon算子手册/operators/zoom_image_size.html)、[zoom_image_factor](../../../halcon算子手册/operators/zoom_image_factor.html)、[affine_trans_image](../../../halcon算子手册/operators/affine_trans_image.html) | §7.3固定实际尺寸weighted显示主路。factor作为候选不用于推算尺寸；affine几何重采样归相关视觉模块，本模块只验证其来源/域/映射 | 三者忽略输入domain；bilinear/bicubic缩小无平滑、constant均值类/weighted高斯类预滤波；int_zooming影响UInt16极值/边缘，false由宿主统一配置。affine用角坐标且矩阵x=row/y=col，不把模块x=col直接塞矩阵 |

主路线选择基于物理隔离、域正确性与可观测释放；未跑同样本实际HALCON性能，不宣称copy/weighted最快。比较候选时同一输入/域/参数/后端版本逐一核标量、通道、域和父映射，再量ROI/global、复制次数/峰值、完整排空P50/P95/P99；extern候选无释放资格不进入速度比较。算法ROI与粗精路线由算法模块定义；本模块先验证core+halo/域再读实际窗口，不主动搜索ROI或目标。
### 17.2 明确不支持能力

当前模块不支持：任意 HALCON handle 直接穿透核心；未注册压缩/编码或未知 stride；未经证明的跨进程共享内存零拷贝；把 `copy_obj`/`reduce_domain` 当深复制；在 tile 内独立完成需全局上下文的算法；自动填补遮挡/缺测；隐式改变单位/坐标；任意序列化类型激活；无界队列、无界缓存、无限重试；把网络/设备 ACK、UI 保存或 native 返回值当质量放行或设备 Applied。

上述能力若要加入，必须由 Contract/Owner 另行采纳字段、能力、资源和恢复语义，并新增对应第二消费者、Replay、并发和长稳验收。

## 18. 来源依据与采纳边界

沿用已核证据：[PKG-006](../../shared-modules/packages/PKG-006_Frames.md)、[DEV-VIS-022](<../../shared-modules/guidance/03-vision/DEV-VIS-022_图像帧、Tile/Pyramid与Viewport开发指导.md>)、[DEV-VIS-020](<../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md>)、[REF-002帧资源研究](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#foundation-source-research)。资料仅为来源，模块当前API/Owner/流程唯一以本文为准；不查AsunImage内部或把历史HImage源码作为公开签名依据。

### 18.0 本轮实查（2026-10-09）

- HALCON项目内页面标题为 `Operator Reference / Version 26.05.0.0`，本轮直接读 §17.1 各链接的Description/Attention及相关输入/参数/Execution部分。依据落实于 §4.2、§5、§7、§17.1；没有编译/执行算子、没有实测速度或Golden结论。
- [.NET Memory/Span使用规则](https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/memory-t-usage-guidelines)：借用期与所有权不同；Rule3/4同步/异步返回后的Memory使用边界、Rule7/8 Dispose或移交只能一方负责。落点§3/§4.3/§6：source显式借用、输出lease显式移交、scope同步行复制；ReadOnlyMemory不等于底层不可变。
- 本轮退修实查 [.NET 10 Array.MaxLength](https://learn.microsoft.com/en-us/dotnet/api/system.array.maxlength?view=net-10.0)：SZ array元素数运行时上限，低于它不保证分配成功；[C#数组](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/arrays)长度固定、new元素初始化为默认值；[.NET 10 Span.Slice](https://learn.microsoft.com/en-us/dotnet/api/system.span-1.slice?view=net-10.0)的start/length为int且越界抛错。落点§4.3/5/7/13：固定精确长度byte[]，C=min(1GiB,Array.MaxLength)，checked后转int，容器超限与OOM分别返回，不让实现者选容器。[.NET 10.0.0官方Array.cs](https://github.com/dotnet/runtime/blob/v10.0.0/src/libraries/System.Private.CoreLib/src/System/Array.cs)实读MaxLength=0x7FFFFFC7（2147483591）；原文SHA-256=`3beb7a940a8ff7b4949141fa8934167c346c047b776a6b250426ba04fc34aae3`。只作运行时上界依据，不复制源码/安装依赖，1GiB是本模块保守支持边界，不将上游理论上限当分配保证。
- [.NET协作取消](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads)：取消发意图，listener负责清理，不证明native停止；不同操作token独立。落点§6的实际停止后终态、§9跨消费者隔离。沿用REF-002的.NET Channels源码/测试研究，不重复下载；bounded Channel缓冲不等于挂起写入有界，接纳等待槽必须计入限额。
- §19.1公开类型依据：只读 [AsunControl/HalconDrawControl.cs](../../references/project-snapshots/AsunControl/20261004/original/ROI/HalconDrawControl.cs) 的 ImageLibDotNet、HObject/HTuple声明及SetHImage消费者形状；不以旧Cv2命名推断26.05入口。项目内26.05 get_image_pointer1/get_region_runs官方C#输出HTuple，gen_image1/copy_image/zoom_image_size输出HObject；实际cv2重载有歧义再通过消费编译核定，不查内部。
- IPC原件在H盘不可用时复用 [已保留快照](../../references/project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/共享内存单消费者租约协议开发指导.md)，本轮核SHA-256=`8e2af5a210cc7d15d068da92e1925521620f502d7705da9a821fa8e023e5f4bb`，与既有来源一致。§19.2保留SPSC/Owner/epoch/未知释放原则，具体命名管道复制协议是本模块设计，不冒充来源mmap实现。
- 本轮直接读 [.NET10 PipeOptions](https://learn.microsoft.com/en-us/dotnet/api/system.io.pipes.pipeoptions?view=net-10.0)（Windows CurrentUserOnly核账号与提升级别；FirstPipeInstance）及 [ReadExactlyAsync](https://learn.microsoft.com/en-us/dotnet/api/system.io.stream.readexactlyasync?view=net-10.0)（未填满即EndOfStreamException）；落实§19.2端点边界和半包拒绝。密钥/启动映射由可信宿主提供；BCL随.NET10，不复制上游源码或新增包。
- 本轮直接读 [D3D12队列与fence](https://learn.microsoft.com/en-us/windows/win32/direct3d12/user-mode-heap-synchronization)、[GetCompletedValue](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12fence-getcompletedvalue)、[texture upload/readback](https://learn.microsoft.com/en-us/windows/win32/direct3d12/upload-and-readback-of-texture-data)、[GetCopyableFootprints](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12device-getcopyablefootprints)。落实§19.3 queue/value归属、UINT64_MAX设备丢失、默认256/512对齐与invalid footprint sentinel；未调用GPU、未安装SDK绑定或实测。Texture capacity由Owner承诺，footprint不能充当VRAM驻留证明。

实质方案分歧为超大图按需计算与缓存关闭，联网读取 **libvips v8.17.0**，固定git commit `603730e50f486bf731cd9ba133fb05c230728c5e`（git ls-remote核定tag）。仅移植思想/反例，不加入运行依赖、不复制C代码；没有构建或运行上游测试。

| 固定原文 | 实读证据、可复用点与局限 | SHA-256 |
|---|---|---|
| [region.c](https://github.com/libvips/libvips/blob/603730e50f486bf731cd9ba133fb05c230728c5e/libvips/iofuncs/region.c) | vips__region_check_ownership（约392行）、region_buffer与region_prepare：区域clip、调用线程同步准备、线程所有权检查；支持§7按需窗口与scope线程约束，不能由其API推断跨await/跨线程安全 | `9205737d5e26f9f4eadde44228be9d55ec966a3f99afbdb40bdf3cffb7ee8650` |
| [tilecache.c](https://github.com/libvips/libvips/blob/603730e50f486bf731cd9ba133fb05c230728c5e/libvips/conversion/tilecache.c) | DATA/CALC/PEND状态和ref_count>0不能flush、tile私有region；drop_all源码FIXME明确活跃线程时直接清空危险，不能照搬Close。落点§7.2等待者/在用tile不驱逐和先停接纳再排空 | `85472d78a4261713013cb842d42c98f496b9302a20bf6feff3dbcc42e698ffd6` |
| [test_conversion.py](https://github.com/libvips/libvips/blob/603730e50f486bf731cd9ba133fb05c230728c5e/test/test-suite/test_conversion.py) | test_crop约307行核父点(30,30)与裁图(5,5)值；test_byteswap约192行两次换序保持尺寸/均值；移植§13坐标/通道/换序样例思想。所读文件没有test_tilecache/test_linecache，不能把crop测试当缓存并发/关闭证据 | `f0bc86138ab4f0812ad7becd7ed436161afd43f1b2902040988411a2fe8fb900` |
| [meson.build](https://github.com/libvips/libvips/blob/603730e50f486bf731cd9ba133fb05c230728c5e/meson.build) · [libvips/meson.build](https://github.com/libvips/libvips/blob/603730e50f486bf731cd9ba133fb05c230728c5e/libvips/meson.build) | 依赖GLib>=2.52/GIO/GObject/Expat/threads及可选编码库；不是纯C#无部署成本组件，未全审传递依赖；不替换AsunImage/HALCON | `cead81e95eedbd73a16d9fb968d4587c39b4664d076ab8f78674decaed353d18` / `d70996e2c43b16c8cea114dcc4ce7b5f36612a3823ea630e20d2df95e87f513c` |
| [LICENSE](https://github.com/libvips/libvips/blob/603730e50f486bf731cd9ba133fb05c230728c5e/LICENSE) | 根为LGPL2.1文本，所读C文件头为LGPL2-or-later；逐文件头不以README替代。此次没有复制/链接，未来实际引入另按DEV-GOV-006确定再分发范围 | `dc626520dcd53a22f727af3ee42c770e56c97a64fe3adb063799d8ab032fe551` |

没有新增快照/报告：固定URL+版本/hash为本指导设计和审核的直接消费者。若来源未来改变仍核对这些固定字节，不引用main或营销性能代替实现证据。
### 18.1 AOI.Main 原图快照与采集序列采纳

依据 [原图预览与保存指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-29-camera-original-preview-and-save-design.md) 和 [连续采集序列指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-29-camera-capture-sequence-browsing-design.md)，沿用以下来源约束；其中相机序列/CameraId/CaptureRevision/FrameIndex的Owner为相机或宿主，本模块只收来源修订与不可变数据，不接管序列状态：

- 原始帧是不可变快照，显示缩略图、全分辨率显示位图和导出对象不能互相冒充；相机环形缓冲区不能在发布后继续修改已发布帧。
- 批量采集按 `CameraId + CaptureRevision + FrameIndex` 去重并丢弃迟到回调；同一相机新轮次只替换自己的序列，其他相机序列保持独立。
- 序列启动前估算像素、缩略图、转换副本和索引占用；预检失败不改变已有序列。首帧规格与预计规格不符时停止相关序列并保留已收齐帧，状态为 `Partial`/`StoppedForCapacity`，不能补成完整。
- 从 Frame 租约读取单像素或导出原图时，结果必须包含当前帧 revision、坐标约定、像素格式和有效域；禁止从 LOD、屏幕截图或插值显示值反推原值。

序列数量、内存比例、相机 SDK 和保存格式由宿主 Profile/适配器冻结；本快照不证明本平台已经完成相机或性能验收。


### 18.2 AsunMeasure 参考采纳与性能边界（2026-10-04）

只读核对 [`AsunMeasure` 快照](../../references/project-snapshots/AsunMeasure/20261004/README.md) 的 `ImageContracts`、`MeasurementSourceArtifactContracts`、`ImageBufferLeaseFactory`、`InMemoryImageBufferStore`、`LargeImageStitchPlanner`、`ThumbnailService` 及 Image Tests 后，采纳三点：帧身份与来源模式必须进入不可变 `FrameIdentity`；原图、预览/缩略图和测量来源必须分成不同 Artifact；lease/read scope、哈希、取消、异常和重复释放要有负向测试。

禁止把 `InMemoryImageBufferStore` 的完整数组复制、`ThumbnailService` 的元数据 URI 或 `LargeImageStitchPlanner` 的布局/残差规划当作超大图生产实现。它们没有证明真实 Tile/Pyramid、GPU 上传、跨 tile 算法等价、峰值内存或长稳性能。实现必须按本页 Tile/Pyramid、Owner、预算和排空合同，以代表性大图测量冷/热 P50/P95/P99、峰值字节、命中率、取消到真实排空和长稳趋势；没有实测证据不得声称零拷贝或大图达标。

AsunMeasure 是 .NET 8/WinForms 参考；平台使用 .NET 10/WPF。旧 `System.Drawing`、WinForms 控件和旧 AsunImage 方法名不得进入 Core 或公共合同。
## 19. 适配切片公开契约与实施绑定 v0.1

本节是 HALCON、IPC、GPU 的当前实施规格，不再以“由适配器以后决定”代替契约。三个适配各有独立实例 epoch、请求表、接纳门和预算；复用 §4.3 的错误、操作/释放/排空回执及 §4.1 的标识/期限规则，不向 Core/Resources 增加 native、管道或设备类型。工厂失败不接管任何注入对象，成功也只借用目标 Resources/设备 Owner；Close 不关闭共享目标服务、调用方 HObject 或设备。适配实例只关闭自身工作、结果和借用。所有 Query 使用原 epoch/request，内部目标请求以独立 Guid 关联，不把两个服务的回执混为一个。

接纳前检查版本、消费者、完整描述、容器和全部资源/回执/工作槽，门内整笔预占；成功移交前再核取消/期限。错误结果不带资源。外部同步调用、IO、Owner/native 方法都在锁外；接纳后没有强杀操作。未知在途工作保持预算/源借用与原请求，实际退出后才返回终态。重复请求按规范化参数摘要去重；有副作用的调用失败或丢回执先查询，不再次提交新请求。源对象实例只参与本地借用关联，不把其地址序列化或写日志。

### 19.1 HALCON import、独立副本与显示 LOD

工程/namespace 为 `Asun.Modules.ImageFrame.Halcon`，引用 Core v0.2、Resources v0.1、Tiles v0.1 及本项目既定 AsunImage。`HObject/HTuple` 只出现在此适配包，类型来自 `ImageLibDotNet`；静态算子入口始终 `cv2`。公开形状如下（规格，未编译）：

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using ImageLibDotNet;
using Asun.Modules.ImageFrame.Core;
using Asun.Modules.ImageFrame.Resources;
using Asun.Modules.ImageFrame.Tiles;
namespace Asun.Modules.ImageFrame.Halcon;
public sealed record HalconRuntimeBinding(
    string BackendVersion, string HostConfigurationRevision, bool IntZooming);
public sealed record HalconAdapterLimits(
    ResourceLimits Resources, int MaxChannels, long MaxDomainRuns,
    long MaxMatrixBytes, long MaxCopyCpuBytes);
public sealed record HalconImportRequest(
    Guid RequestId, string ConsumerId, FrameKey Key, HObject Source,
    ImmutableArray<PlaneRole> Roles, ImmutableArray<PlaneMetadata> Metadata,
    string SourceId, string SourceRevision, string CoordinateReference,
    TimeSpan Timeout);
public sealed record HalconCopyRequest(
    Guid RequestId, string ConsumerId, IFrameLease Source, TimeSpan Timeout);
public sealed record HalconLodRequest(
    Guid RequestId, string ConsumerId, IFrameLease Source, FrameDescriptor SourceDescriptor,
    FrameKey ResultKey,
    int Level, string ParameterRevision, TimeSpan Timeout);
public sealed record HalconCopyResult(OperationReceipt Receipt, IHalconImageLease? Images);
public sealed record HalconLodResult(
    OperationReceipt Receipt, FrameDescriptor? Frame, TileLayerDescriptor? Layer);
public delegate void HalconImageReader(int planeIndex, HObject image);
public interface IHalconImageScope : IDisposable
{
    FrameError VisitPlane(int planeIndex, HalconImageReader reader);
}
public interface IHalconImageLease : IAsyncDisposable
{
    Guid Id { get; }
    string ConsumerId { get; }
    FrameKey SourceKey { get; }
    ManagedFrameLayout Layout { get; }
    PixelWindow CoreWindow { get; }
    PixelWindow ActualWindow { get; }
    ImmutableArray<int> SourcePlaneIndices { get; }
    ImmutableArray<PlaneMetadata> Metadata { get; }
    ImmutableArray<AllocationCharge> Allocations { get; }
    FrameError TryOpenScope(out IHalconImageScope? scope);
    ValueTask<ReleaseReceipt> ReleaseAsync(TimeSpan observationTimeout);
}
public interface IHalconFrameAdapter : IAsyncDisposable
{
    Guid ServiceEpoch { get; }
    ValueTask<PublishResult> ImportCopyAsync(HalconImportRequest request, CancellationToken ct);
    ValueTask<HalconCopyResult> CopyToHalconAsync(HalconCopyRequest request, CancellationToken ct);
    ValueTask<HalconLodResult> PublishDisplayLodAsync(HalconLodRequest request, CancellationToken ct);
    OperationLookup QueryOperation(Guid serviceEpoch, Guid requestId);
    ValueTask<DrainReceipt> CloseAsync(TimeSpan observationTimeout);
}
public sealed record HalconAdapterCreateResult(FrameError Error, IHalconFrameAdapter? Adapter);
public interface IHalconFrameAdapterFactory
{
    HalconAdapterCreateResult Create(IFrameService target, HalconAdapterLimits limits,
        HalconRuntimeBinding runtime, IManagedLayoutValidator validator,
        TimeProvider timeProvider, IFrameEventSink? events);
}
```

计划工厂类 `HalconFrameAdapterFactory`。Resources限额沿 §4.3，但本实例允许 Native，Gpu/Cache=0；MaxChannels=1..64、MaxDomainRuns正且不超过 FrameBudget 的有效行段上限；MaxMatrixBytes正且不高于MaxNativeBytes；MaxCopyCpuBytes正且不高于MaxCpuBytes及C。工厂只校验参数，不读图。runtime.BackendVersion 必须为 `26.05`，HostConfigurationRevision非空，IntZooming=false；这是宿主已配置事实，模块不调用 set_system，也不把它当授权核验。target 的对应消费者注册及可用 CPU 预算由宿主在装配时保证；target仍独立接纳，拒绝时适配器按已完成阶段清理，不能预设必成功。HALCON Source仅借用：调用方不得写、Dispose或改变domain，直到原适配回执 OperationResourcesReleased；传入的CPU lease同样不得并发Release，模块只开/关自己的scope，不Release调用方lease。

**导入顺序。** ① count_obj必须1，再count_channels<=MaxChannels，Roles/Metadata数量相等。按1-based access_channel→get_image_pointer1取得pointer/type/width/height；将 UInt8/UInt16/Int16/Int32/Float32 分别映为 byte/uint2/int2/int4/real，不支持的类型、维度差异或缺少通道/单位语义拒绝，不猜RGB。② 各channel get_domain→get_region_runs，先检查tuple长度及MaxDomainRuns，再checked闭→半开转换、规范化；每plane有效域为HALCON域与请求Metadata.ValidDomain交集，保留缺测原因。布局Domain设Full，真实plane域放Metadata；Empty不是Full。已存在的native tuple临时量另测，不把事后拒绝称为分配前限制。③ 构造单通道Planar plane的紧凑布局，按原机器小端标记；pointer按checked row偏移仅在借用存活时复制，封送由本包的 IFrameInputRows 负责，不能向Resources泄漏指针。④ target.PublishCopyAsync只复制到独立CPU storage；其原请求仍未知时保留channel/tuple/source借用。目标回执证明复制实际退出才Dispose临时channel/domain/tuple，再置适配OperationResourcesReleased。成功Frame是target持有的发布，后续Read/Retire归target；适配Close不Retire已经交付的发布。

**CPU→HALCON 深复制。** 逐plane先核SinglePlane/ChannelCount=1；交错plane在进入本端口前由显式转换宿主拆为单通道，不在本包暗中丢alpha。Float64无本版无损raw映射，拒绝。先预占所有plane精确紧凑CPU数组及native matrix payload；打开source scope，CopyRow到各 `new byte[checked((int)planeBytes)]`，有效域外清零、有效浮点非有限拒绝。每plane在pin存活期调用 gen_image1，真返回后解pin；gen_region_runs/reduce_domain附上原域，reduce_domain仅alias同matrix，不重复计allocation。临时无域image Dispose后剩下的域image拥有同一matrix；输出仍是独立的每plane HObject，不默认拼为RGB。空域使用空region，禁止以Full替代。创建结果lease并移交native holder后才撤临时CPU/source scope，成功结果需调用方Release。失败、取消、异常对已生成对象逐一清理；同步算子未真退出不能解pin/Dispose输入。相同Source重发不同RequestId形成新matrix、新allocation，不推测HALCON自动去重。

VisitPlane同步执行reader，回调期间只读借用该image，不允许保存HObject、取得其指针后逃逸、Dispose、写入或启动异步使用。需要异步算法的宿主必须在回调内通过cv2.copy_image建立自己独立持有/计账的副本；否则不能接入。本模块不能证明恶意回调遵约。reader异常转AdapterFailure，但在finally关闭使用；Scope.Dispose等待本scope正在执行的回调真实返回。LeaseClosed阻止新scope，旧scope/回调退出前保留native账和lease槽，最后matrix实际Dispose一次后StorageReleased=true。

**显示LOD。** PublishDisplayLodAsync只接受完整原图lease（ActualWindow覆盖源尺寸）、Full域、Intensity/ColorR/G/B、支持的单通道类型；Height/Mask、缺域和Float64按§7.3拒绝。Level从1开始，按逐层ceil(/2)且目标每维>=2的既定链核定；5×3的level1为3×2、映射5/3与3/2，不创建1维层。本版逐级完整图weighted，不能跳过中间层假称相同算法；源copy→逐plane zoom_image_size→copy_image隔离最终matrix→按导入路线发布target独立CPU结果。前层所有plane真退出才Dispose，最终native对象及借用退出后才适配终态。ResultKey须新身份/修订，ParameterRevision包含实际层链、weighted、26.05、int_zooming=false和宿主配置修订；返回Layer.Purpose=DisplayOnly，ToSource角原点0，不改物理强度/颜色映射。结果仅发布本次层，不隐式建立整套缓存/source；宿主可把此发布装配为§7的DisplayOnly层，且必须提供完整冻结层描述。ExactSamples不得从此Frame取原值。

**计账和限制。** 本实例CPU账为临时精确数组payload；native账为已生成独立matrix的 `width*height*scalarBytes` 及尚未落实的矩阵预占，同matrix域alias按allocationId去重。LOD接纳预占源native copy、最大相邻层及最终隔离copy同时存活的payload、CPU源copy与导入期间target副本的各自Owner峰值；上界checked按请求层链计算，锁内预占后才调用算子。target预算独立检查，跨Owner重复出现不求和为进程RSS。MaxNativeBytes是受控matrix payload上限，**不是HALCON allocator、算子内部scratch或进程native堆的硬上限**；这些无法由算子返回值精确报价，真实峰值另按§14测量。部署Profile必须额外留出实测runtime/scratch余量；未测仅阻断相应性能/生产资格，不伪造精确上限或阻断复制规格。MaxCopyCpuBytes/C超限在分配前拒绝，超大图使用有界tile源，不完整导入再声称按需。

LOD完整图验证以SourceDescriptor为准：其Key等于Source.SourceKey，ActualWindow=(0,0,描述宽,描述高)，全部SourcePlaneIndices/格式/Metadata与描述一致；不得把局部slice自报成全图。CopyToHalcon和LOD均要求请求ConsumerId等于Source.ConsumerId，且资源来自仍开放的合法source；布局/域按Core/Resources重新校验。

CopyToHalcon保留源的CoreWindow/ActualWindow/SourcePlaneIndices；输出Layout以副本局部坐标描述，pointer不对外返回，SourceKey和窗口共同确定父帧位置。该端口不变更来源修订或冒充完整原图。VisitPlane每个scope串行调用，不允许reader同步等待自身scope/lease关闭；调用方要复制后异步执行时，独立副本归其Owner。适配公开回执与原target回执分别保留，在途/隔离项不按ReceiptRetention驱逐，满表即拒绝新接纳。

native Dispose/tuple清理抛错时不能证明释放：保留未证实对象关联和payload账，返回DrainUnknown并阻止复用；成功Dispose才撤相应holder。模块没有强制销毁HALCON运行时的端口。输出scope内的派生alias若逃逸属于调用方违反借用约定，无法由本模块证明安全，不宣称ReadOnly接口能防止任意native写入。

**两个消费者与验收。** HAL-R01：CameraSnapshotHost借用3×2 UInt16 HObject导入，源随后由其Owner Dispose；AlgorithmHost A和ReplayHost B从target各Read，A释放不影响B。HAL-R02：ReplayHost从CPU lease CopyToHalcon，两个native lease分别独立copy，改调用方原buffer不改结果；scope/lease并发释放恰一次，tuple/native故障和阻塞算子用受控fake验证保账，再以真实26.05绑定核值/域/Dispose。HAL-R03：Viewport无UI投影调用5×3→3×2 LOD，只核显示层及映射；AlgorithmHost的ExactSamples继续用原lease；UInt16高值、Full/Empty/hole、通道/Float64/Height/未知runtime配置均覆盖。真实HALCON Golden及峰值资格不能由fake通过替代。

### 19.2 跨进程 SPSC 有界复制与可信 Owner

首版选定 **Windows本机命名管道、双向鉴权、有界分块复制**，不启用MemoryMappedFile/共享指针/跨进程零拷贝，也不落盘staging。来源SPSC、epoch/generation、Broker唯一Owner和未知不回池不变量保留；来源256字节ASUNFRM1 header、Protobuf、AOI journal与服务SID配置不移入本协议。这里的slot是Broker逻辑传输槽，不是共享内存slot；不把单进程锁冒充跨进程CAS。本版只支持同Windows用户账号、同提升级别，拒绝远程/跨身份。未来需服务身份或mmap时升级契约，当前不以它们“待选”拖延本版。

工程/namespace `Asun.Modules.ImageFrame.Ipc` 只引用Core/Resources及BCL。计划实现 `NamedPipeFramePairFactory`；一个pair一producer一consumer，一个实例最多SlotCount个在途slot（首版固定SlotCount=1），多消费者各自独立pair。每pair独立host注入32字节随机共享密钥，密钥由可信启动通道传递，仅在进程内保存；不从wire、PID、ConsumerId自报、日志或共享文件取得身份。CurrentUserOnly双端验证用户与提升级别，FirstPipeInstance防止同名server意外复用；密钥鉴权进一步隔离同账号其他进程。宿主是密钥/启动/端点映射Owner，module Broker是slot、借用和回执Owner；客户端本地Resources是复制结果Owner。

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.ImageFrame.Resources;
namespace Asun.Modules.ImageFrame.Ipc;
public enum IpcSlotState { Free, Sending, AwaitingRelease, Released, Poisoned }
public sealed record IpcPairBinding(
    Guid PairId, string PipeName, string ProducerConsumerId,
    string ReceiverConsumerId, string AuthorizationRevision,
    ReadOnlyMemory<byte> SharedKey);
public sealed record IpcPairLimits(
    ResourceLimits Resources, int SlotCount, int ChunkBytes,
    int MaxMetadataBytes, long MaxPayloadBytes, TimeSpan HandshakeTimeout);
public sealed record IpcTransferKey(
    Guid PairId, Guid ProducerEpoch, Guid ConsumerEpoch, int SlotIndex, ulong Generation);
public sealed record IpcSendRequest(
    Guid RequestId, IFrameLease Source, FrameDescriptor Descriptor, TimeSpan Timeout);
public sealed record IpcFetchRequest(
    Guid RequestId, FrameKey SourceKey, FrameKey LocalKey, TimeSpan Timeout);
public sealed record IpcSendReceipt(
    OperationReceipt Operation, IpcTransferKey? Transfer, IpcSlotState? Slot);
public sealed record IpcOfferLookup(LookupState State, IpcSendReceipt? Receipt);
public sealed record IpcFetchResult(
    OperationReceipt Operation, IpcTransferKey? Transfer, FrameDescriptor? LocalFrame);
public sealed record IpcTransferLookup(
    LookupState State, IpcTransferKey? Transfer, IpcSlotState? Slot,
    bool SourceBorrowReleased, FrameError Error);
public interface IFrameIpcBroker : IAsyncDisposable
{
    Guid ServiceEpoch { get; }
    ValueTask<IpcSendReceipt> OfferAsync(IpcSendRequest request, CancellationToken ct);
    IpcOfferLookup QueryOffer(Guid serviceEpoch, Guid requestId);
    IpcTransferLookup QueryTransfer(IpcTransferKey transfer);
    ValueTask<DrainReceipt> CloseAsync(TimeSpan observationTimeout);
}
public interface IFrameIpcClient : IAsyncDisposable
{
    Guid ServiceEpoch { get; }
    ValueTask<IpcFetchResult> FetchCopyAsync(IpcFetchRequest request, CancellationToken ct);
    OperationLookup QueryOperation(Guid serviceEpoch, Guid requestId);
    IpcTransferLookup QueryTransfer(IpcTransferKey transfer);
    ValueTask<IpcTransferLookup> ObserveTransferAsync(IpcTransferKey transfer,
        TimeSpan observationTimeout, CancellationToken ct);
    ValueTask<DrainReceipt> CloseAsync(TimeSpan observationTimeout);
}
public sealed record IpcBrokerCreateResult(FrameError Error, IFrameIpcBroker? Broker);
public sealed record IpcClientCreateResult(FrameError Error, IFrameIpcClient? Client);
public interface IFrameIpcPairFactory
{
    IpcBrokerCreateResult CreateBroker(IpcPairBinding binding, IpcPairLimits limits,
        TimeProvider timeProvider, IFrameEventSink? events);
    IpcClientCreateResult CreateClient(IpcPairBinding binding, IpcPairLimits limits,
        IFrameService localTarget, TimeProvider timeProvider, IFrameEventSink? events);
}
```

Create复制SharedKey到自己的固定32B私有数组，不保存可被调用方改写的Memory；成功/失败/关闭均清理本方密钥，未知在途需保留鉴权服务能力至排空。Guid及修订沿§4.1，PipeName为本地非路径 ASCII `[A-Za-z0-9_-]` 1..80，不能含server/share或反斜线；绑定双方固定ConsumerId，发送端Source.ConsumerId必须等于ProducerConsumerId，接收请求没有wire ConsumerId选项。Resources仅CPU，Native/Gpu/Cache=0。SlotCount=1、ChunkBytes=4KiB..1MiB且2的幂、MaxMetadataBytes=1..1MiB，MaxPayloadBytes=1..min(C,MaxCpuBytes,FrameBudget有效上限)，HandshakeTimeout为(0,24h]。实际工作槽/回执/消费者限额照§4.3；源lease为借用，不计入新payload但在宿主源Owner计持有，Broker每slot最多一个chunk buffer。Client预占整帧紧凑CPU staging、chunk及本地target目的/scratch的同时峰值；没有能力容纳整帧则拒绝，超大图须把有界tile各自作为Frame传输。target也独立限额，不把chunking称作无整帧复制。

**线协议 IFCP/1.0。** 使用NamedPipeServerStream/ClientStream异步byte模式、CurrentUserOnly，server附加FirstPipeInstance；不允许反序列化CLR类型、路径、指针、lease或句柄。固定176B小端header：0..7 ASCII `IFCOPY01`；8 major UInt16=1；10 minor UInt16=0；12 kind UInt16；14 reserved UInt16=0；16 bodyLength UInt32；20 slotIndex UInt32；24 sequence UInt64；32 RequestId16B；48 PairId16B；64 producerEpoch16B；80 consumerEpoch16B；96 generation UInt64；104 reserved8B=0；112 bodySHA25632B；144 HMACSHA25632B。Guid按 .NET Guid.ToByteArray()/new Guid(bytes)固定混合端序表示，不能与文本UUID/network序混用。每方向sequence从1严格递增，溢出关闭新接纳；新连接随机32B nonce，session key=HMACSHA256(sharedKey,ASCII `IFCP1`+PairId+两epoch+serverNonce+clientNonce)，MAC覆盖header[0..144)与body，常数时间比较。SHA256仅完整性摘要，HMAC才鉴权。未知major/minor/kind、非零reserved、超body上限、错误MAC/hash/epoch/generation/seq均隔离并终止该连接，不尝试扫描magic恢复同步。

kind值固定：1 ServerHello、2 ClientHello、3 Ready、4 Fetch、5 Descriptor、6 Chunk、7 Copied、8 Release、9 ReleaseAck、10 Query、11 Status、12 Error、13 Close。握手hello body各含nonce32B和AuthorizationRevision的UTF-8长度前缀；ServerHello暂consumerEpoch=Empty，ClientHello带客户端实例epoch，Ready确认两epoch；hello使用sharedKey MAC，Ready及以后用session key。只有双方校验PairId/修订、MAC/nonce/epochs并完成Ready才接受Fetch；握手sequence也逐条计数。未握手不能用ConsumerId自报取得slot。sharedKey不上传，不记录HMAC/nonce作为“可信进程退出”证明。

控制body以固定顺序BCL BinaryWriter/BinaryReader语义编码（UTF-8 strict；字符串UInt32字节长度+原字节，禁用BinaryReader隐含7-bit字符串格式），整数小端、bool仅0/1、enum固定UInt32拒绝未知。FrameKey=Guid16+UInt64 Revision；Descriptor编码 SourceKey、宽高Int32、planeCount UInt32、plane各Scalar/Role/ChannelCount/ByteOrder/packing、RowBytes/Offset/Stride/Accessible Int64，紧凑DeclaredBufferBytes Int64；再各Metadata的Unit/Scale/Bias（IEEE754 Float64小端）/Channels/ValidDomain.Kind及rowCount+每行3个Int32/InvalidReason，最后SourceId/SourceRevision/CoordinateReference与整帧SHA25632B。Layout.Domain固定Full，plane域必须完整携带；所有计数在分配前核1..64、域总行段预算、字符串§4.1及MaxMetadataBytes，缺字段、尾随字节或重复plane拒绝。紧凑plane按index顺序，Offset为前面plane bytes累加，Stride=RowBytes，LittleEndian；禁止跨plane alias/padding/负stride进入wire。整帧hash按规范化后的连续像素bytes计算，域/元数据受Descriptor MAC保护，不把它当完整证据artifact hash。

Fetch body=SourceKey；Descriptor用于指定transfer及payloadLength（紧随DeclaredBufferBytes的UInt64同值），必须先验证后预占/分配。Chunk body=UInt64 offset+UInt32 count+bytes，count<=ChunkBytes，严格顺序无重叠/空洞，offset从0至payloadLength，每包body<=ChunkBytes+12；控制body<=MaxMetadataBytes（hello亦受限，最少能容纳nonce及绑定修订，否则Create拒绝）。Copied body=payloadSHA25632B；Release/ReleaseAck/Query body为空；Status body=UInt32 state+bool SourceBorrowReleased+UInt32 FrameError；Error body=UInt32 FrameError；Close body为空。每种kind只允许对应状态和方向，slot未绑定时slotIndex=0/generation=0，仅握手/Fetch/Error/Close可用；其他消息必须精确transfer。ReadExactlyAsync先读176B并核长度，分配有界body，再读满并验MAC/SHA；截断/EndOfStream/取消为连接失败，不处理半包。SHA采用IncrementalHash逐chunk；Broker第一遍source行读取计算hash、第二遍发chunk，同一稳定scope覆盖两遍，不先拷整帧；不可稳定两遍的相机来源须先经Resources快照。

**Owner状态与释放。** Offer借用源lease并登记不可变SourceKey，仅一个slot，Offer可先于连接，重复请求不再取得借用；源未知不换新Offer。认证Fetch只匹配该SourceKey，Broker门内Free→Sending、generation checked+1；客户端staging校验全部hash、域/有限值后，以LocalKey调用localTarget.PublishCopyAsync，错误不发布。Copied表示已独立复制并完成校验，随后客户端发Release；Broker等本slot最后同步CopyRow/IO实际退出、关闭自己的source scope及借用关联后，Sending/AwaitingRelease→Released，SourceBorrowReleased=true，再ReleaseAck并回Free。ReleaseAck证明远端借用退出，**不表示调用方源lease已Release或本地CPU结果已Retire**。Offer OperationResourcesReleased在该证明后才true；客户端操作在staging/chunk/目标复制退出且远端释放回执可核后才终态。localTarget已发布但ReleaseAck丢失时，LocalFrame仍不交付给调用方，保留内部关联，查询原transfer恢复后交付；取消/期限先到则Retire这次本地发布并等真实释放后终态，不交付迟到结果。

复制路线没有远程访问源指针。断连时Broker停止本方所有IO，等本方行复制真实退出并关闭scope即可证明自身借用结束，不需要PID/进程监督证明；先Poisoned隔离当前slot，发布原transfer Released事实后，**只有新握手/新连接generation** 才再用slot。客户端已经交付的独立本地Frame不因断连撤销。若本方行复制仍阻塞，保持Poisoned/DrainUnknown、源借用与slot账；超时/杀对端不能释放它。同双方epoch重连可Query原transfer/RequestId，返回 retained Status/ReleaseAck，重复Release幂等；原epoch不同返回Unknown，保留期过后NotFound不证明释放。Broker/Client重启换epoch，首版无durable journal，不能恢复旧操作终态；新服务不得替旧Owner发释放证明。generation达到ulong.MaxValue停止接纳并关闭pair，新pairId/new epochs后重建，不回绕。未终态/隔离记录不能按ReceiptRetention驱逐，回执表满即背压。

**两个消费者和断言。** IPC-R01：CameraSnapshotHost producer→AlgorithmWorker consumer，父进程Borrow源lease，子进程target独立Read；ReplayHost producer→ArchiveWorker consumer是第二独立pair，密钥/epoch/ConsumerId不共享；A断连不影响B。IPC-R02：截断header/body、过长计数、非法域/enum、单bit破坏、旧epoch/seq/generation、伪ConsumerId/修订/MAC一律未发布；回执丢失重连Query不二次复制/增slot。IPC-R03：ReleaseAck丢失、客户端已copy后退出、源CopyRow阻塞、Offer/Close竞态、重复Release、全槽及回执满、generation极值，断言SourceBorrowReleased仅本方真实退出。IPC-R04：child进程真实named-pipe握手及复制/hash/退出按BCL Process启动受控测试子模式，不使用共享内存，不把软件协议测试称为服务身份/现场资格。

Broker实际CPU预占为一块精确RowBytes的row scratch与一个ChunkBytes+12的chunk body数组，均<=C且计入本方global/producer额度；CopyRow一次需完整行，不能仅凭chunk上限声称行buffer有界。逐行清域外并规范小端后依次hash/切chunk，跨行chunk无空洞。Client staging与chunk也分别计实际payload；metadata/header/MAC小数组及对象计入独立元数据上限/进程测量，不混为像素账。OfferAsync接纳即返回Accepted（不是等待Fetch终态），调用方之后Fetch及QueryOffer观察释放；无Fetch也受原Offer期限，未启动IO/CopyRow即可撤借用后TimedOut。发送全部chunk后Sending→AwaitingRelease；断连释放按上文真实退出路径，不等待不存在的共享指针使用者。Descriptor中的BitsPerSample由注册scalar唯一导出，不接受任意值；payloadLength紧随DeclaredBufferBytes，整帧hash放body尾，字段顺序唯一。

Offer的Descriptor必须来自Source所属发布服务：Key、完整窗口、全部plane顺序/布局/Metadata相符，SourceId/SourceRevision/CoordinateReference非空；局部tile须先发布为自己的有界Frame，不能把slice标签当全图。Client以LocalKey创建本地发布，保留wire来源标识/修订与坐标引用，SourceKey→LocalKey关联留在原Fetch回执记录，不能把本地新Id当新的采集事实。Offer RequestId与客户端Fetch RequestId分别登记，一次transfer关联两者；wire Fetch/Descriptor/Chunk/Release/Query沿客户端Fetch RequestId，Broker QueryOffer沿原Offer RequestId。相同Fetch摘要重试必须先查本地请求表，不能再发送Fetch。

CreateBroker成功建立独占本地pipe endpoint并启动本实例唯一有界连接监听；创建OS端点失败返回AdapterFailure/null，清理未发布端点。CreateClient只创建状态，不连接；首个Fetch负责有限握手。连接处理最多一个发送工作和一个控制读取器，统一串行写入队列，queue受Resources槽约束，不能每个Query新起线程或未限额Task。QueryOffer/QueryOperation/QueryTransfer只读当前已观察状态，不执行同步网络IO；ObserveTransferAsync是显式恢复入口，按原transfer重连握手并发送Query，observationTimeout=0仅看缓存，取消只结束本次观察、不取消原Fetch。收到可核Status/ReleaseAck后更新原Fetch/Offer，必要时完成已保留本地结果的交付/清理；Unknown/NotFound原样返回，不能换新transfer或重发像素工作。Broker Close停止新Offer/Fetch，已有释放/查询通道保留到本方真实排空，Closed后不提供重启持久查询。

### 19.3 GPU 资源、提交与 fence/设备 Owner 端口

工程/namespace `Asun.Modules.ImageFrame.Gpu` 只引用Core/Resources及BCL。本版模块只协调设备Owner公开端口，不实现硬件SDK或接管device/queue；明确实现路线为宿主 **D3D12 Copy queue 上传/只读资源、已登记只读工作与 Copy readback**。RendererHost登记显示工作，InferenceReadbackHost登记读回工作；两者无UI依赖，可用相同模拟Owner先验证协调。BackendId固定 `d3d12-copy-v1`，替代GPU后端必须新Binding/资格，不能当作自动等价；没有真实Owner时只允许显式CPU路径或本版模拟器，不能伪装GPU成功。

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.ImageFrame.Core;
using Asun.Modules.ImageFrame.Resources;
namespace Asun.Modules.ImageFrame.Gpu;
public enum GpuFenceState { Pending, Completed, DeviceLost, Unknown }
public enum GpuWorkKind { ReadOnlyRender, Readback }
public sealed record GpuDeviceBinding(
    Guid DeviceEpoch, string BackendId, string AdapterId, string DriverRevision,
    string OwnerVersion, ImmutableArray<string> ReadOnlyWorkIds);
public sealed record GpuFootprint(
    int PlaneIndex, long OffsetBytes, long RowPitchBytes, long RowBytes, int Rows);
public sealed record GpuAllocationQuote(
    Guid QuoteId, Guid DeviceEpoch, string DescriptorDigest,
    ManagedFrameLayout Layout,
    long TextureCapacityBytes, long UploadCapacityBytes, long ReadbackCapacityBytes,
    ImmutableArray<GpuFootprint> Footprints);
public sealed record GpuQuoteResult(FrameError Error, GpuAllocationQuote? Quote);
public readonly record struct GpuResourceKey(Guid DeviceEpoch, Guid ResourceId);
public readonly record struct GpuFencePoint(Guid DeviceEpoch, Guid QueueId, ulong Value);
public sealed record GpuSubmission(
    FrameError Error, Guid OwnerOperationId, GpuResourceKey? Resource,
    ImmutableArray<GpuFencePoint> Fences, bool Submitted);
public sealed record GpuOwnerObservation(
    LookupState Lookup, Guid OwnerOperationId, GpuFenceState FenceState,
    GpuSubmission? Submission, bool OperationResourcesReleased,
    FrameError Error);
public enum GpuResourceReleaseState { Active, ReleasePending, Released, Unknown }
public sealed record GpuOwnerRelease(
    LookupState Lookup, GpuResourceReleaseState State, FrameError Error,
    GpuResourceKey Resource, bool ResourceReleased);
public interface IGpuDeviceOwner
{
    GpuDeviceBinding Binding { get; }
    GpuQuoteResult Quote(ManagedFrameLayout layout);
    GpuSubmission SubmitUpload(Guid ownerOperationId, GpuAllocationQuote quote,
        ImmutableArray<PlaneMetadata> metadata, IFrameReadScope source);
    GpuSubmission SubmitReadOnlyWork(Guid ownerOperationId, GpuResourceKey resource,
        string workId, GpuWorkKind kind);
    GpuOwnerObservation Query(Guid deviceEpoch, Guid ownerOperationId);
    FrameError CopyReadbackRow(Guid ownerOperationId, int planeIndex, int y, Span<byte> destination);
    GpuOwnerObservation ReleaseOperation(Guid deviceEpoch, Guid ownerOperationId);
    GpuOwnerRelease ReleaseResource(GpuResourceKey resource);
}
public sealed record GpuCoordinatorLimits(ResourceLimits Resources, int MaxPendingSubmissions);
public sealed record GpuUploadRequest(
    Guid RequestId, string ConsumerId, IFrameLease Source,
    FrameDescriptor SourceDescriptor, TimeSpan Timeout);
public sealed record GpuUploadResult(OperationReceipt Receipt, IGpuFrameLease? Frame);
public sealed record GpuWorkRequest(
    Guid RequestId, string ConsumerId, IGpuFrameLease Source,
    string WorkId, GpuWorkKind Kind, FrameKey? ReadbackKey, TimeSpan Timeout);
public sealed record GpuWorkResult(OperationReceipt Receipt, FrameDescriptor? ReadbackFrame);
public interface IGpuFrameLease : IAsyncDisposable
{
    Guid Id { get; }
    string ConsumerId { get; }
    FrameKey SourceKey { get; }
    FrameDescriptor Descriptor { get; }
    ManagedFrameLayout Layout { get; }
    ImmutableArray<PlaneMetadata> Metadata { get; }
    ImmutableArray<AllocationCharge> Allocations { get; }
    ValueTask<ReleaseReceipt> ReleaseAsync(TimeSpan observationTimeout);
}
public sealed record GpuShareResult(FrameError Error, IGpuFrameLease? Lease);
public interface IGpuFrameCoordinator : IAsyncDisposable
{
    Guid ServiceEpoch { get; }
    ValueTask<GpuUploadResult> UploadAsync(GpuUploadRequest request, CancellationToken ct);
    GpuShareResult Share(IGpuFrameLease source, string consumerId);
    ValueTask<GpuWorkResult> ExecuteAsync(GpuWorkRequest request, CancellationToken ct);
    OperationLookup QueryOperation(Guid serviceEpoch, Guid requestId);
    ValueTask<DrainReceipt> CloseAsync(TimeSpan observationTimeout);
}
public sealed record GpuCoordinatorCreateResult(FrameError Error, IGpuFrameCoordinator? Coordinator);
public interface IGpuFrameCoordinatorFactory
{
    GpuCoordinatorCreateResult Create(IGpuDeviceOwner owner, IFrameService readbackTarget,
        GpuCoordinatorLimits limits, IManagedLayoutValidator validator,
        TimeProvider timeProvider, IFrameEventSink? events);
}
```

计划工厂 `GpuFrameCoordinatorFactory`。Resources允许Cpu/Gpu但Native/Cache=0，MaxPendingSubmissions正且<=MaxActiveOperations；Owner Binding非空固定DeviceEpoch、adapter/driver/owner修订及唯一WorkIds，工厂借用Owner，不重置或Dispose设备。本版只支持单通道SinglePlane、LittleEndian、UInt8/UInt16/Float32，按plane映为R8_UINT/R16_UINT/R32_FLOAT，不量化、不启用sRGB、不丢域；Height等物理语义仅透传，显示投影不能用作测量。其他布局先由显式CPU转换或拒绝，不隐式转换。quote为无allocation、无设备命令的纯能力/报价查询，DescriptorDigest绑定完整布局；quote寿命限当前deviceEpoch和该请求，不跨设备复用。

Owner用目标D3D12资源描述给出独立texture的受控capacity承诺和GetCopyableFootprints的upload/readback offsets、rowPitch、rowBytes、rows，capacity/rowPitch/rowBytes/rows为正、OffsetBytes非负，所有运算checked且不为UINT64_MAX；默认pitch 256B、placement 512B，对齐不由RowBytes猜测。本版即使设备支持放宽对齐仍用默认路线。协调层验证每plane footprint覆盖实际行、offset有界不重叠、Upload/Readback capacity<=C，逐项核资源全局及consumer限额后预占texture+upload；readback仅其工作接纳时预占readback capacity和target目的/scratch，不提前分配。TextureCapacityBytes为Owner控制的独立allocation承诺上界，实际不得超过；不是整个驱动VRAM/驻留量保证。一个plane一个独立资源，本版禁用shared heap/suballocation/跨设备句柄；Owner内部opaque ResourceId绑定这组plane的唯一释放，不向调用方泄漏COM指针。若Owner不能报价/保证capacity则拒绝，不能先创建后报告超预算。

**上传。** 接纳后协调层打开CPU source scope并保留调用方lease借用。SubmitUpload同步按footprint逐行CopyRow到Owner上传buffer，空padding/无效域清零；不得保存source scope或跨方法返回继续读它。Owner提交前完成行复制并按metadata域校验，任一步失败且Submitted=false必须无资源副作用并已清理；提交线性化后Submitted=true，Resource与非空fence返回，错误/异常可能发生在提交后时必须仍以原OwnerOperationId的Query发现，不允许重新调用Submit。Owner在提交线性化前先登记请求，用相同OwnerOperationId查询能够区分NotFound（保证该epoch未提交）与Unknown（不能证明），异常不等于未执行。模块在Submit真返回后可关闭本方source scope/借用，因为Owner不再读取源；Owner上传buffer和texture仍保持到全部fence完成。这里没有把pin当新allocation：D3D12主路先同步复制至独立upload buffer，模块不把调用方CPU pin保留到GPU fence；采用直接读取源的后端不属于本版。

Owner每queue fence值严格递增、1..ulong.MaxValue-1；queue/device epoch不同不可比较。GpuFenceState.Completed仅在所有对应queue观察完成>=各提交值且设备仍有效时成立；ID3D12Fence.GetCompletedValue返回UINT64_MAX为DeviceLost，不能当“最大完成值”。模块只能Query，不signal/wait/reset设备或提升fence。deadline/ct提交前可拒绝；提交后只关闭交付意图，原工作保留GPU/upload和pending槽直至真实Owner完成。查询到Completed再ReleaseOperation，Owner确认上传临时资源已释放后可交付GPU lease、OperationResourcesReleased=true；texture已移交结果holder，不能一起释放。Cancelled/Timeout已提交上传不交付结果，先等fence、ReleaseOperation及ReleaseResource全确认后终态；未知DeviceLost不自动释放、不重建设备。

**只读使用、读回与共享。** Share只接受同coordinator的开放source，门内增加目的consumer独立lease、同allocation逻辑首引用与lease槽，全局不重复计texture。两个lease不可共享Id。Execute检查Source.ConsumerId==请求ConsumerId、来源同实例/开放、WorkId在Binding登记、ReadbackKey仅Readback必需且是独立FrameKey；读取禁止写原texture，Owner工作登记的宿主能力决定只读命令，不从wire或随意delegate获得SDK handle。执行接纳时增加独立use holder和consumer逻辑/槽保护，源lease关闭不能撤它。SubmitReadOnlyWork返回本工作实际全部fence；协调层保留use至所有fence完成及ReleaseOperation确认，ReadOnlyRender结果ReadbackFrame=null（不替UI声称已显示）。Readback在完成后由Owner.CopyReadbackRow提供稳定行给readbackTarget.PublishCopyAsync，直到目标复制真实退出才ReleaseOperation清理readback staging；目标成功Frame归target，协调Close不Retire已交付发布。Readback保持逐plane域、单位、source修订，只复制原始样本，不读取显示渲染结果。Owner不得后台写已完成的readback rows；row端口仅同步scope式借用，不逃逸destination。

Release lease阻止新工作，pending use/fence保留其consumer bytes/lease槽；A关闭不取消B工作。最后holder等全部使用完成，再ReleaseResource；Owner确认资源实际释放后才StorageReleased并撤GPU账。`ReleaseOperation` 只表示该 `OwnerOperationId` 关联的上传/工作临时资源已释放，**不表示 texture 的 `ResourceReleased`**，协调层不得用它清除 texture 账。texture 唯一释放/恢复入口是 `ReleaseResource(resourceKey)`：它是同一 `DeviceEpoch + ResourceId` 上的幂等 release-and-observe 调用。首次调用可返回 `Lookup=Found, State=ReleasePending, Error=None, ResourceReleased=false`；Owner 真正释放后返回 `Lookup=Found, State=Released, Error=None, ResourceReleased=true`，并在同一 epoch 的 `ReceiptRetention` 内保留该 Released tombstone。释放回执丢失、或Owner在内部已释放后抛异常，调用方都必须用同一个 resourceKey 重复 `ReleaseResource`；再次返回的稳定 tombstone 才是可重放的释放证明，不得重新Submit或以 `Query(ownerOperationId)` 代替。重复调用不得重新释放、递增引用或创建新Resource。

同一 epoch 的活动/排队资源返回 `Found + Active/ReleasePending`；tombstone过期后返回 `NotFound + Unknown + Error=NotFound`，该结果不能反推此前释放成功。设备丢失、Owner无法判断、回调异常且没有可核tombstone时返回 `Lookup=Unknown, State=Unknown, Error=Unknown, ResourceReleased=false`，继续保留GPU实际/预占、pending槽和lease账。Owner以新 `DeviceEpoch` 重启时，旧epoch key不得在新epoch上被当作NotFound或释放；新Owner返回上述Unknown，旧Owner若仍可访问其同epoch tombstone才可继续重查。只有 `State=Released` 且 `ResourceReleased=true` 才允许协调层撤GPU账/发布 `StorageReleased`；`Query` 的 `OperationResourcesReleased=true` 单独不足以清账。Owner必须在同epoch保留未终态/Unknown记录直到可恢复或明确隔离，不以GC、PID消失、重连、device lost或Close超时作释放证明。真实设备销毁/进程监督只由设备Owner提供可核的旧epoch释放结论，模块不发设备命令、不用PID/GC/重连推断。Share不制造异步请求回执，失败Lease=null，引用不增加；其它服务操作沿§4.3保留可查询回执。

**两个消费者与反例。** GPU-R01：Replay CPU样本Upload→Share给RendererHost A及InferenceReadbackHost B，A执行只读显示、B读回，A Release且fence未完时B仍合法；最终每独立texture恰一次Owner释放。GPU-R02：3×2 UInt16 rowBytes=6，quote rowPitch=256、rows=2、upload capacity至少512（仅一plane样例），若预算按12B预留必须拒绝；多plane placement/溢出/quote摘要或epoch不匹配也拒绝。GPU-R03：提交前取消/提交后取消、返回异常但Query已Submitted、`Query` 返回 `OperationResourcesReleased=true` 但 texture 仍为 `ReleasePending`、首次 `ReleaseResource` 回执丢失、Owner 已释放后抛异常、随后用同一key重复调用并得到稳定 `Found/Released/true` tombstone、fence Pending/UINT64_MAX/queue错位、Owner重启、旧epoch重查、Close及Share竞态；断言不重提、不用OperationResourcesReleased清texture账、不用NotFound/Unknown/device lost/超时作释放证明，只有稳定Released tombstone撤账。GPU-R04：Readback=原scalar/domain/单位且无sRGB变化；模拟Owner只核协调时序，真实D3D12提交/driver/设备lost/峰值资格需宿主Owner绑定后执行。

Upload要求完整SourceDescriptor与lease的Key/窗口/全部plane/Metadata一致，Source.ConsumerId等于请求ConsumerId；本版不接受局部slice直接上传，tile以自己发布的Frame接入。IGpuFrameLease.Descriptor保留原FrameDescriptor和坐标来源；Readback以独立ReadbackKey发布，保持来源字段及原GPU帧关联，不改采集事实。Share只分享资源holder，不改变Descriptor。Quote/Submission/Observation null/default/字段矛盾为AdapterFailure：成功quote非null、QuoteId非空且完整；Submitted=true必须有Resource和完整Fences，Submitted=false不能带任何资源/在途fence；Lookup=Found必须带原Submission，Lookup=Unknown/NotFound不能伪造Completed。Query发现丢失的Submit回执时用Submission恢复原Resource/Fences及已提交事实；ReleaseOperation后仍保留原提交摘要和释放结果，不提前销毁可核记录。Owner方法可能阻塞，协调层观察期限到则DrainUnknown保留工作槽和引用；不把Task.WaitAsync返回当Owner真实退出。

GPU账按quote中的texture独立capacity承诺与upload/readback CPU capacity记actual+reserved：Owner native buffer虽非byte[]仍占本实例CpuBytes维度，另注明Owner管理而非CLR数组。CPU源仍归源Owner、pin不重复计量；CPU readbackTarget是独立Owner。实际capacity不得高于quote，本版端口不暴露实际容量缩减回执，因此一直保守按完整quote计，不能猜驱动只用了rowBytes。Owner未知时保留该承诺全额及pending槽，不因消费者放弃显示撤账。quote.Layout必须与输入值逐字段相符，Footprints覆盖同布局；它是完整不可变报价值，不要求Owner保留无界quote表。Owner按绑定版本对提交quote重校验，禁止调用方篡改报价越过容量限制。

### 19.4 实施顺序、测试计划及真实外部门

实现顺序按切片：公开DTO/校验与实例工厂→请求去重/两层预算→受控fake端口→最小无UI两消费者及异常/并发断言→真实HALCON或BCL子进程绑定→真实GPU设备Owner集成。每次先完善该切片产品能力和必要测试，再记录已有harness结果，不新增过程报告。HALCON真实引用仍用现有AsunImage；IPC不引入Protobuf/gRPC/NuGet；GPU native SDK实现属于宿主设备Owner，本模块端口/模拟协调可独立实现。

§13测试计划补充HAL-R01..03、IPC-R01..04、GPU-R01..04为对应工程必需用例。三个适配Tests仍采用Microsoft.NET.Sdk、net10.0、OutputType=Exe、无PackageReference；HALCON Tests按当前项目程序集引用，IPC Tests使用同一Exe的受控`--ipc-child`内部测试模式（不是产品CLI），GPU Tests默认FakeOwner确定性执行；真实GPU资格另以同Exe显式`--gpu-owner-host`绑定宿主测试Owner，缺Owner返回非零/NotEvaluated，不默跳必需资格。真实HALCON缺样本/绑定、IPC子进程未执行或资格用例失败必须非零；各软件/真实资格分别输出结果，不能把fake通过提升为适配生产通过。可控TimeProvider与闩锁验证时序，真实IO采用有限取消/进程deadline，杀进程只证明测试未完成，不替资源Owner宣告释放。

所有本节异步端口统一执行同一交付规则：`ImportCopyAsync`、`CopyToHalconAsync`、`PublishDisplayLodAsync`、`OfferAsync`/`FetchCopyAsync`、`UploadAsync`/`ExecuteAsync` 在接纳后到交付线性化前若 deadline 或取消先到，只关闭调用方的交付意图，不交付迟到的 lease、Frame、Halcon image 或 ReadbackFrame；已提交的底层工作仍按原 epoch/request 或 owner operation 排空。交付线性化后再收到取消不撤回已移交结果，调用方必须显式 Release。观察超时只返回 `Draining`/`DrainUnknown`，不把 `WaitAsync`/调用返回当真实停止或释放；旧结果随后只能进入原请求的释放/查询路径，不覆盖新请求或新视图。GPU texture 还必须满足 §19.3 的 `ReleaseResource` 稳定 `Released` tombstone 才能撤账，不能因 async 端口返回或 `ReleaseOperation` 成功而提前释放。

GPU真实测试Owner注入固定为测试工程内 `GpuAcceptanceOwnerBinding.Create()` 的直接编译绑定，返回 `IGpuDeviceOwner`；宿主设备Owner集成获准时在该测试工程通过ProjectReference/已有程序集Reference接入对应Owner工厂。未绑定时该模式返回非零并列GPU-R真实资格NotEvaluated，不从字符串加载任意插件、下载SDK或创建假native成功。默认FakeOwner模式不调用此绑定。HALCON Tests直接引用本项目既定ImageLibDotNet；IPC child由父harness用当前Exe绝对路径和明确参数启动，使用ArgumentList，不经shell插值，父/子分别注入自己的Resources限额和pair密钥，密钥只经重定向stdin传递、不置于进程命令行或日志。

§14适配Profile增加：HALCON导入/导出/逐级LOD各阶段的CPU矩阵/native payload与实际HALCON堆/临时峰值分别测；IPC两遍source扫描、序列化/hash/MAC、chunk IO、客户端staging/target副本、Release到Ack/重连Query分别量，同pair每次<=1slot；GPUQuote/排队/同步CPU staging复制/提交/fence/读回/Owner释放分开测，记录capacity、实测driver驻留、旧epoch隔离量。目标缺客户来源时NotEvaluated，不编造P95/吞吐/物理上限。§15包固定为Halcon/Ipc/Gpu API v0.1、依赖Core v0.2及Resources/Tiles适用v0.1；IPC只接受IFCP/1.0，无静默降协议；设备/后端/参数修订变化新实例epoch及缓存key。

真实外部门只有对应平台Frame映射、客户样本与物理验收值、宿主稳定借用资格、可信启动密钥配置及同账号部署、GPU宿主D3D12 Owner/工作登记与真实设备验收、HALCON公开调用的实际编译/Golden/资源测量。它们不替代本节已决定的DTO、Owner、生命周期和恢复路线，不阻断无关CPU或模拟协调工作。extern/mmap/跨身份/其它GPU后端本版明确不启用，新增时另采纳契约，不列作当前主路待实现项。

### 19.5 适配交付清理、恢复保留与模拟验证闭合

本节仅补充已批准适配范围的执行细节，复用§4.3/§19的公开端口，不新增产品API或SDK实现。进程内幂等比较沿§4.3逐字段值等价规则：HALCON Import比较除Source对象外的全部请求字段；Copy比较ConsumerId、Source.Id/SourceKey/窗口/plane映射/布局/Metadata及Timeout；LOD另加SourceDescriptor、ResultKey、Level、ParameterRevision；IPC Offer比较Source.Id及完整Descriptor/Timeout，Fetch比较SourceKey/LocalKey/Timeout；GPU Upload比较ConsumerId、Source.Id及完整SourceDescriptor/Timeout，Execute比较ConsumerId、Source.Id、WorkId/Kind/ReadbackKey/Timeout。借用对象不得在同Id下改变内容；Source对象不入持久回执。相同请求只返回原回执，不重新交付image/GPU lease，重复结果对象为null；发布元数据仅在原操作成功交付过时可按原值返回。查询不重建丢失的lease，旧epoch/未知工作按原Owner恢复，不换新Id重复提交。

**内层已发布、外层尚未交付。** HALCON Import/LOD及GPU Readback通过target.PublishCopyAsync发布时，先登记本操作与目标ServiceEpoch/RequestId/FrameKey的关联，成功目标Frame在外层交付前仍是本操作拥有的发布持有权。门内最终检查ct/deadline/Close；交付成功才把该发布的后续Read/Retire责任移交调用方。若期限、取消或关闭先到，即使内层成功，也不得把Frame放入外层结果/事件；通过target.RetireAsync仅撤本操作成功创建的FrameKey，再等本操作临时对象/源scope/native/GPU使用实际退出，才发Cancelled/TimedOut终态。外层失败的Frame/Layer/Images/GpuFrame/ReadbackFrame均为null，ResultLeaseId不得指向未交付对象。target失败/Conflict不能Retire既有他人帧；内层结果未知须查原目标操作，只有证实本操作成功发布才Retire。目标查询Unknown/NotFound不表示未执行，保留关联、必要借用及无法证明已退出的预算并返回DrainUnknown。Release/Retire尚未知时继续用原对象/id有限观察；不重复分配、不全局Close共享target。已交付帧不因适配器Close撤销，沿既有规则由其新Owner归还。

§19.2的重连“恢复后交付”仅适用于原Fetch仍等待、交付意图开放且原期限未到的调用；Fetch已返回DrainUnknown或ct/deadline/Close先到后，ObserveTransferAsync只恢复Status/ReleaseAck及本次LocalFrame的Retire/清理，不复活旧交付意图，不从Query/Observe返回已撤销的LocalFrame。其他适配亦复用§4.3规则，首次调用因期限/取消返回未知后不二次交付对象；未知回执保持原因，真正排空后才记录Cancelled/TimedOut。客户端调用方须保留原epoch/request/transfer用作释放对账，不依赖重新Fetch取得迟到对象。

**GPU恢复记录与期限。** §19.3中Owner的Released tombstone保留从资源真实释放时起算，固定至少24h，覆盖本模块允许的所有ReceiptRetention（最大24h），不是每次ReleaseResource重试重新延长；同epoch重复返回相同Released事实。协调器资源对象及待释放holder独立于已完成业务回执，ReleaseAsync观察到期后仍保留原Owner任务/ResourceKey，待该次Owner调用真退出才串行重查ReleaseResource，禁止在同一原调用未退出时并发启动无限重试。已观察有效Released事实可在协调器门内提交后释放holder；未观察到则即使过24h也保持隔离关联与账，NotFound不能替代证明。Owner的操作/资源恢复记录必须有界：Simulator采用本次Resources.MaxReceipts分别限制操作记录和资源记录（含tombstone），上传接纳先各预留一条、只读工作先预留操作记录，满表提交前BudgetExceeded且Submitted=false；未终态/Unknown不按期限驱逐，完整终态24h后可逐条驱逐，ResourceId在整个deviceEpoch内不得重用。真实Owner采用同一保留语义及其显式部署容量，宿主装配时以OwnerVersion对应的公开配置确认其保留不少于24h和容量足够；这属于现有Owner接入责任，不要求本模块扫描SDK。即使Owner容量小于协调器也只按明确拒绝回执处理，不扩大Owner。device lost不删除已有Released证明；旧Owner的同epoch、匹配ResourceKey且Lookup=Found/State=Released/Error=None/ResourceReleased=true可继续作为释放证明，新epoch仍不得代答旧key。矛盾字段或不同ResourceKey为AdapterFailure，继续隔离，不能撤账。

**已有GPU模拟端口的确定行为。** 本版Simulator是§19.3 IGpuDeviceOwner的纯托管受控实现，由同一Gpu.Tests harness注入GpuFrameCoordinatorFactory，供RendererHost A与InferenceReadbackHost B验证协调；不新增独立GPU模拟产品或公开驱动工厂。测试OwnerVersion=`simulator-v0.1`、AdapterId/DriverRevision显式含`synthetic`，无native/真实VRAM，记录的GpuBytes是模拟容量承诺。每用例构造新实例/DeviceEpoch、传入同一ResourceLimits及可控TimeProvider；脚本由有限的逐提交顺序表构成，每项指定Upload/Render/Readback、Pending→Completed或DeviceLost/Unknown、完成闩锁、一次throw-after-submit、一次throw-after-release，不允许自动随机成功/模拟重置旧epoch释放。脚本仅改变完成与故障时序，正常像素仍由真实CPU source.CopyRow复制并按原plane域保存，Readback复用这些原样本，不编造算法/检测结果；选择未登记WorkId、脚本耗尽或顺序不符为未提交AdapterFailure。

模拟Quote算法固定：逐plane RowBytes取已校验布局值，RowPitch=checked((RowBytes+255)/256*256)，Offset=checked((previousEnd+511)/512*512)，Rows=Height，end=checked(Offset+RowPitch*Rows)；Upload/ReadbackCapacity为最后end，TextureCapacity为checked(sum(RowBytes*Height))的synthetic承诺，不能称D3D12真实资源capacity。源拷贝一行scratch与存储数组仍按C及harness显式CPU预算检查，所有数组精确长度、域外/padding零化。QuoteId为无allocation身份，提交按全部Layout/footprint/capacity逐字段重核，不用DescriptorDigest碰撞放行；Digest只是本Owner对该完整值生成的不可变标识，协调器跨Owner不比较它作内容证明。每queue从1单调生成fence，有限脚本闩锁没打开始终Pending；打开才Completed，DeviceLost/Unknown脚本不自动转Completed。Query仅读取注册状态，不递进脚本；重复Submit同OwnerOperationId/参数只能读取原提交事实，不再复制/递增fence，参数不同Conflict。ReleaseOperation及ReleaseResource各自仅释放对应临时资源/texture，达到真实模拟释放线性化点后先存tombstone再执行一次抛异常分支，后续重查稳定返回。原行复制仍阻塞时不得释放借用；脚本本身与元数据占用另测，不计作真实GPU资源。

**补充可判定验收。** GPU-R03续用3×2 UInt16（行6B、2行、单plane）：Quote应为Offset=0、RowPitch=256、Upload/ReadbackCapacity=512、synthetic TextureCapacity=12。先放行Upload fence并ReleaseOperation，保留texture 12B；最后lease Release首次Owner已释放并存tombstone后抛异常，协调器仍保持12B/释放中holder，原调用真退出后同key重查Found/Released/true，仅此时撤12B且析构次数恰1。将时间推进超过24h且协调器从未观察Released的独立用例，应得到NotFound/Unknown并继续隔离12B；换DeviceEpoch亦Unknown，不能从新设备空表清账。A/B共享后A超时只结束其工作交付意图，B原scalar仍完整；完整终态前不驱逐记录，回执满时Submit次数不增加。HAL-R01/03、GPU-R04增加target成功后、外层提交前闩锁触发ct/deadline/Close：外层Frame及ResultLeaseId为空，恰一次Retire本次key，既有其他消费者帧/lease保持；Retire未知直到解除闩锁仍保关联，实际释放后才取消/超时终态。IPC-R03复用既有LocalFrame未交付→Retire规则，不另造协议或外部Owner。

## 20. 全部批准范围的文档准备结论（2026-10-11）

**结论：当前全部批准范围文档准备完成，没有仍需开发者补猜的可决定软件算法、API或架构欠账。** 本原会话复用已完成研究、CPU接收、自审和§19.3释放恢复核对，仅补§19.5的Owner恢复期限/有界记录、内部target未交付发布清理及现有Simulator可执行规则；未重新审算CPU准入片、未扩大范围。此结论是指导准备与切片规格结论，整模块继续DesignReview，不授予整模块代码或运行/生产资格。

| 当前批准能力/消费者 | 唯一实施位置与文档结论 | 保持的切片规格状态 |
|---|---|---|
| 相机/Replay输入布局；plane/像素/有效域/单位/坐标/预算首错 | §4.2/4.4/4.5/5，纯值验证、半开域、正负stride/alias/checked边界明确；文档完成 | Core v0.2 ModuleCoreImplementationReady（规格准备） |
| CPU不可变发布、共享读取/Lease/ReadScope、复用/取消/归还 | §4.3/6/9/11–14，byte[]/C/双层额度及原子移交、双消费者与未知保账明确；文档完成 | Resources v0.1 ModuleCoreImplementationReady（规格准备） |
| 有界CPU tile、halo、cache/LRU、DisplayOnly层消费和纯值Recommend | §7/11/13/14，尾块/父中心映射、Source Owner/借用/移交、确定建议和拒绝边界明确；文档完成 | Tiles v0.1 ModuleCoreImplementationReady（规格准备） |
| HALCON导入/CPU深复制/逐plane native副本及显示LOD | §17.1/18/19.1/19.4–5，26.05 cv2顺序、domain交集与端点转换、weighted实际尺寸、pin/native Owner和反例明确；文档完成 | HALCON v0.1适配设计已接收（规格准备） |
| IFCP/1.0 SPSC命名管道有界复制、可信pair/epoch/generation、查询/释放 | §19.2/19.4–5，完整wire/鉴权/长度/域/hash、双pair和本地/远端Owner恢复明确；文档完成 | IPC v0.1适配设计已接收（规格准备） |
| GPU托管协调/模拟端口，上传/Share/只读工作/原样readback/fence/释放 | §19.3–5，报价/两消费者/原提交恢复及独立texture tombstone、确定模拟负载与故障脚本明确；文档完成 | GPU v0.1托管协调/Simulator ModuleCoreImplementationReady（规格准备） |
| 无UI调用与宿主投影 | §10/11；本模块不交付UI DLL，错误键三语与观察/恢复边界已定，具体页面/DevExpress组合归Viewport/宿主；文档完成 | UI NotApplicable，不表示宿主WPF已通过 |

本版的Region为§4.4 DomainDescriptor/DomainRow有效域值及§19.1适配内部region，不新增ROI编辑或跨模块region对象。所有已批准操作使用相同源值/域/单位事实；显示层不用于原值测量，AI/质量/证据/设备命令不在本模块。extern零拷贝、共享映射零拷贝、跨身份/远程IPC、其他GPU后端、完整超大图驻留及全局跨tile算法不在已批准主路；拒绝/有界tile替代见§7/17.2/19，不把未启用能力列成软件设计欠账。

| 仍未执行的实现/运行/接入资格 | 责任Owner与精确输入 | 对指导准备的影响 |
|---|---|---|
| C#实际构建、公开重载/封送确认、BCL Exe断言、真实26.05 scalar/domain/借用/清理Golden | 本模块后续实施Owner及CameraSnapshot/Replay来源Owner；按§13/16/19向量、真实稳定借用与现有AsunImage引用执行 | 实施与运行未验；不再等待算法或DTO选择 |
| 真实IFCP父/子进程、密钥启动/同账号提升级别配置及完整性/断连恢复 | IPC部署宿主Owner；显式PairBinding/AuthorizationRevision/密钥传递及§19.2子进程用例 | 软件协议与可信映射已定，只缺真实执行/部署参数 |
| 真实D3D12 Owner/SDK、注册只读Work、driver/fence/device-lost/实际capacity与资源峰值 | 设备/渲染/推理宿主Owner；对应OwnerVersion、24h恢复记录策略与容量配置、设备/驱动及实际资源证据 | native实现不在本轮模块范围；不阻断托管协调/模拟端口 |
| 正式Frame身份/来源/坐标/事件映射、正式两个产品消费者装配 | 平台Frame事实Owner、Camera/Replay/Algorithm/Viewport宿主Owner；按§3/4/11/19的显式接入契约映射 | 不反向改Core值类型；集成资格未验，没有在本模块待定的映射算法 |
| 代表图像/全图与tile负载、并发/节拍/长期运行、物理及现场验收值 | 客户/机台Profile与计量/质量验收Owner；提供输入hash、Profile修订/容量/时延目标及有效样本/拒绝判据 | §14/19.4测点和机制判据已定；目标未采纳为NotEvaluated，禁止编造数值 |

实际编译、真实HALCON/跨进程/GPU/driver/fence/device-lost/峰值、正式消费者与WPF/HIL/物理/现场资格全部未执行。本轮定向文档验证检查链接/表格/公开声明与API字段闭合、已接收状态及新增模拟算例/释放/取消反例，只证明本指导一致，不声称产品或测试通过。达到当前批准范围的准备准则后停止扩写，不新增过程材料。


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

## 附录 A：逐切片六项准入接收位置

下表只记录规格准备。三个CPU切片保持既有 `ModuleCoreImplementationReady（规格准备）`；主会话已逐项接收HALCON/IPC v0.1的适配设计六项文档规格，状态为“适配设计已接收（规格准备）”；GPU v0.1仅托管协调/Simulator及公开端口为 `ModuleCoreImplementationReady（规格准备）`，真实D3D12 Owner/native SDK不在本模块本轮实现范围。整模块维持DesignReview。首片纯同步取消/排空/释放为NotApplicable，后续回执不能套回Core。没有授权本轮产品实现，未创建工程、运行harness或形成生产资格。

| DEV-GOV-010 §3.1 | ManagedLayoutValidation | CPU CopyStorage/Lease | CPU Tile/cache/Recommend | HALCON v0.1 | IPC v0.1 | GPU v0.1 |
|---|---|---|---|---|---|---|
| 1. 职责/非目标/依赖/消费者 | §1/3/4.5，相机布局与Replay布局；已接收 | §3/11，两个无UI消费者；已接收 | §7/11，有界source与两等待者、纯值建议；已接收 | §19.1，相机导入、Replay导出/算法/显示宿主；适配设计已接收（规格准备） | §19.2，Camera→Algorithm与Replay→Archive独立pair；适配设计已接收（规格准备） | §19.3，Renderer/InferenceReadback、D3D12宿主Owner；托管协调/Simulator规格已接收 |
| 2. 公开契约/单位/Owner/生命周期 | §4.4 Core v0.2值类型/首错；已接收 | §4.3固定byte[]/C、双层额度/引用去重、原子移交/真实释放；已接收 | §7.1/7.2能力、同key预占/consumer逻辑量、上游归还；已接收 | §19.1工厂/import/copy/LOD/scope、HObject边界与matrix payload；适配设计已接收（规格准备） | §19.2 IFCP/1.0 DTO/176B header/鉴权/可信映射/slot/query/ack；适配设计已接收（规格准备） | §19.3 DTO/quote/Owner提交与查询、fence/Share/use/readback/释放；托管协调/Simulator规格已接收 |
| 3. 最小无UI宿主 | §4.5合成值样例；已接收，未实现 | §11工厂与两consumer共享30B/global40；已接收，未实现 | §11同key38B、A/B各30B、Borrowed/Transferred与Recommend；已接收，未实现 | §19.1 HAL-R01..03借用→CPU→native/LOD→各Owner释放；未执行；适配设计已接收（规格准备） | §19.2 IPC-R01/04 broker/client→子进程target→Read→Query/释放；未执行；适配设计已接收（规格准备） | §19.3 GPU-R01 Upload→Share→两工作→读回→各Release；未执行；托管协调/Simulator规格已接收 |
| 4. 正常/边界/并发/异常断言 | §4.4/4.5/17多错/空域/溢出/工作量；已接收 | §13 CPU-R01..04双层额度/pending/Conflict/C/OOM/回滚；已接收 | §7/13 TILE-R01等待者隔离/同key/不同key/去重/LRU；已接收 | §13/19.1 HAL-R01..03类型/域/alias/pin/未知借用/显示限制；适配设计已接收（规格准备） | §13/19.2 IPC-R01..04截断/鉴权/hash/重连/epoch/generation/未知；适配设计已接收（规格准备） | §13/19.3 GPU-R01..04容量/丢回执/fence/device lost/两消费者；托管协调/Simulator规格已接收 |
| 5. BenchmarkProfile | §4.5/14 Validate/域桶，目标未采纳NotEvaluated；已接收规格 | §14actual+reserved/consumer账、payload与GC/RSS分开；已接收规格 | §14逻辑大图/热点/读取量与§7.3最坏容量；已接收规格 | §14/19.4导入/导出/逐级LOD、matrix及HALCON临时峰值分别测；无实测；适配设计已接收（规格准备） | §14/19.4两遍源扫描/hash/MAC/chunk/staging/target/Ack；无实测；适配设计已接收（规格准备） | §14/19.4报价/CPU staging/提交/fence/读回/释放/driver峰值；无实测；托管协调/Simulator规格已接收 |
| 6. 工程/测试/允许路径/顺序 | §Core binding/4.5/13/16，BCL Exe及dotnet run；已接收 | §11/13/16，发布→两读→Release→Retire→Close；已接收 | §7/13/16，factory→Read→还→Close与纯值Recommend；已接收 | §16/19.4 Halcon独立工程/Tests、现有引用、HAL-R必需；适配设计已接收（规格准备） | §16/19.4 Ipc独立工程/Tests、BCL child与IPC-R必需；适配设计已接收（规格准备） | §16/19.4 Gpu独立工程/Tests、fake与真实Owner资格分开；托管协调/Simulator规格已接收 |

定向自审结论：CPU接收状态一致；新增适配的参数、工厂、输出、资源Owner、两个消费者、超时/丢回执查询与释放顺序都有正文位置。HALCON未向Core泄漏对象或扩大有效域；IPC不依赖wire自报身份、不启用mmap；GPU不以UINT64_MAX/设备重连推断fence完成。实际编译、26.05 Golden、跨进程执行、GPU设备、性能和现场验收均未执行，不写通过结论。
