# Viewport 二维三维影像与 ROI 控件独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`V-C1, V-C2, V-C3`

- 独立模块编号：`IM-060`

- 模块键：`viewport`
- 中文名称：二维三维影像与 ROI 控件
- 来源：`PKG-049_Viewport`；责任分组：`SM-025`
- 规划消费者：生产工作台、复判工作台、工程诊断/编程工作台、独立测量工具
- 文档版本：`0.3.5-prep`
- 本轮内容复核：2026-10-12 原会话仅闭合BC-U1公开CPU源生产者、BC-U2稳定ID只读选择及BC-U3空更新/重新呈现；准确兼容与限定自审见§20.5。§20.4全范围原结论及既有V-C1/C2/C3、U1/V-A1和V-A1-C5接收保持，不重开全审
- 文档状态：`DesignReview/Prep`
- 目标运行基线：C# / .NET 10；核心库不依赖 UI；可选 WPF + DevExpress 25.2.3 适配层
- 视觉边界：通过 `ImageLibDotNet` 公共接口使用 AsunImage；目标 HALCON 版本为 `26.05`
- 本文性质：独立模块实施金标准。当前未声明代码实现、WPF 验收、HALCON 验收或生产通过。

本文是 IM-060 的唯一模块实施指导；§3～§6、§8～§11 的 Module API Contract 定义无产品事实写入的公开边界，本文内冻结的类型不等待平台 DTO 命名。平台/客户映射、真实适配及资格按 §18 分门处理。声明描述目标 API，不声称现有代码已提供这些成员；按切片记录内容接收；已接收V-C1～C3不因其它切片欠账退回；V-U1/V-A1指导内容已接收，真实UI/backend/产品仍NotReady；本版V-A1-C5增量已由主控限定指导内容接收，不标纯CoreReady，不提升运行/生产资格。

基线资料：[`PKG-049`](../../shared-modules/packages/PKG-049_Viewport.md)、[`DEV-UI-042`](<../../shared-modules/guidance/05-ui/DEV-UI-042_视觉/3D工作区与ROI交互开发指导.md>)、[`DEV-VIS-020`](<../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md>)、[`DEV-VIS-022`](<../../shared-modules/guidance/03-vision/DEV-VIS-022_图像帧、Tile/Pyramid与Viewport开发指导.md>)、[`DEV-VIS-024`](<../../shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection Target Selection开发指导.md>)、[`DEV-GOV-005`](<../../01-governance/DEV-GOV-005_模块独立性与复用标准.md>)。链接目标是已有唯一指导；本文不创建其替代版本。

## Core implementation binding

- 准入路径：`NewBuild`。绑定类库 `src/Asun.UI.Viewports/Asun.UI.Viewports.csproj`（namespace：`Asun.UI.Viewports`）和 smoke 测试 `tests/Asun.UI.Viewports.Smoke/Asun.UI.Viewports.Smoke.csproj`。仓库当前处于开发指导完善阶段，两个工程均须在切片获授权时创建并登记入 `AsunVision.slnx`；本指导冻结其落点、命名空间与公开契约，不冻结任何实现行为。
- 未来Core实现允许范围：仅上述类库与测试工程中经本指导批准的文件；新Core文件仅在这两工程目录。可选WPF落点与已接收指导见§10.6，本版公开装配增量见§10.6～9；工程仅在后续明确代码授权后建立，本轮唯一写入仍为本指导。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。
- 切片状态：主控于2026-10-10接收V-C1纯2D Plan、V-C2 Session/授权/命令、V-C3 root/原Task/cleanup的DEV-GOV-010 §3.1六项规格内容，均为`ModuleCoreImplementationReady`（仅规格内容）。V-U1指导内容已接收，属于可选WPF切片，不标纯CoreReady；真实WPF/GPU/backend/产品仍`NotReady`。V-A1 0.3.2-prep指导范围已接收，本版V-A1-C5增量于2026-10-11由主控限定指导内容接收，不标纯CoreReady，不提升运行/生产资格，该基线保持。全模块仍DesignReview/Prep，不是运行、集成或产品资格。

## 1. 目标和非目标

### 1.1 负责的能力

Viewport 是一个有界、可取消、可观测的显示与交互协调模块，负责：

1. 接收宿主提供的只读影像/表面/叠加投影和权限上下文。
2. 生成与当前源身份、坐标修订、视图修订一致的 2D/3D 显示计划。
3. 提供平移、缩放、适应窗口、1:1、旋转、镜像（仅显示）、图层显隐和视图重置。
4. 将屏幕操作转换成带来源和修订的选择、探针、ROI 编辑候选或测量请求；不在事件回调里写业务事实。
5. 管理显示专有的纹理、Overlay、LOD、GPU/native 资源和双缓冲；源帧、Tile/Pyramid、坐标、ROI 几何、表面源数据仍由对应 Owner 管理。
6. 在无 UI 环境中执行校验、坐标映射、显示计划计算、选择排序、资源排空和回执生成。

### 1.2 明确禁止

Viewport 不拥有以下事实或副作用：

- PCB、PCBA、SPI、AOI、点胶、涂覆或其它制程的目标身份、工艺解释、缺陷分类、判定、质量放行、复判意见、设备命令和配方发布。
- 生产数据库、私有表、产品 ViewModel、机台 Shell、硬件 SDK 句柄、相机采集控制或 MES 事务。
- 原图/高度场的第二缓存、第二 Scene/Session 权威、第二坐标系统、第二 ROI 几何真源或第二量测引擎。
- 通过显示颜色、图层顺序、空值、0、绿色或隐藏文字表达 PASS/NG。
- 用渲染深度、LOD 顶点序号、截图像素或最近邻对象猜测真实测量值、原采样索引或对象身份。
- 用 UI 关闭、清屏、`Task.Cancel` 或计数清零冒充 native/GPU/租约已经释放。
- 在旧显示仍可见时以新身份标题、坐标矩阵或 Overlay 响应用户输入。

宿主负责目标关联、流程状态、权限授予、工艺规则、质量放行和设备副作用。Viewport 只返回明确的显示/选择/探针/编辑候选或错误回执。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Viewport.Core`（影像状态/租约/叠加层值类型）不得引用 `System.Windows.*`；只有 `Asun.Modules.Viewport.Wpf`（实际 WPF 控件）可引用 WPF/DevExpress，Core 不得反向引用它。§1 已明确"Viewport 是有界、可取消、可观测的显示与交互协调模块"。

**Blazor/Web**：Blazor Server 是 Viewport 的第二宿主形态（远程诊断/监控）。服务端按 tile 粒度发布影像；坐标标记由 `coordinate-geometry` 服务端计算后传递，浏览器不重写坐标变换（同 IM-007 §1A）；ROI 编辑交互走 WPF 工程台，Web 端只读。SignalR Hub 推送帧更新事件，帧字节通过 HTTP Range 分片下载，不通过 SignalR 传输原始图像。

**AI 推理 Tiling**：Viewport 渲染的帧是 AI 推理的显示层；推理 tile 由 `image-frame` 从 Viewport 已发布的帧裁切，Viewport 只消费 AI 标注结果作为叠加层渲染，不直接参与推理分块编排。

**HALCON 双跑**：Viewport 不执行 HALCON 算子（纯显示协调）；HALCON 备选 CI 不涉及本模块。叠加层坐标的双跑在 `coordinate-geometry` 模块中执行。

## 2. 权威和依赖边界

### 2.1 单一事实 Owner

| 能力 | 权威 | Viewport 接入方式 |
|---|---|---|
| 帧身份、像素布局、原图/Tile/Pyramid、有效域、租约 | `PKG-006` | 只读 source descriptor、tile lease、release 回执 |
| 坐标系、单位、方向、面别、变换组合/求逆 | `PKG-007` | 只读 transform resolver；Viewport 只组合最终显示矩阵 |
| ROI 几何、约束、草稿、撤销、提交差异 | `PKG-020` | 读取几何快照；编辑时提交 typed draft intent |
| 高度场、点云、LOD 原索引、表面有效性 | `PKG-027` | 只读 surface lease、源映射和可见性查询 |
| 二维/三维量测 | `PKG-030` | 发起测量请求并展示返回投影，不计算业务测量 |
| 证据、结果、导出、人工复判 | 宿主注入的原 Owner | 接收只读投影或 typed command port |
| 身份、会话、用途、权限、盲审、撤权 | 宿主/授权 Owner | 每个交付阶段重新校验，不缓存永久授权 |

依赖通过显式端口注入。禁止容器动态查找未登记服务，禁止为了调用方便引用生产产品程序集。多个 Viewport 可共享 `PKG-006` 的物理资源，但每个 Viewport 有独立的显示代、选择/焦点、取消令牌和预算。

### 2.2 HALCON/AsunImage 优先路径

算子语义、参数范围和版本行为以目标 HALCON 26.05 本地官方手册为准。HALCON 26.05 的算子均可通过 `ImageLibDotNet.cv2` 使用，不重复核验包装是否包含算子；只有 C# 参数类型、重载或封送方式确有歧义时才查公共签名或在消费项目编译确认；项目内资料入口为 [`halcon算子手册/operators`](../../../halcon算子手册/operators/)。适用的显示/几何能力优先通过 AsunImage 或已确认的既有控件公共能力使用，不扫描、修改或优化 AsunImage 内部，不猜测未确认的方法名、参数顺序或线程语义。

候选核对清单（不是已批准 API 签名）：

| 语义 | 需核对的 HALCON 能力 |
|---|---|
| 2D 窗口视野/显示矩阵 | `set_part`、`get_part`、窗口坐标转换 |
| 2D 点映射 | `affine_trans_point_2d` 或目标版本等价能力；确认 row/column 约定 |
| 原像素探针 | `get_grayval`；确认 reduced domain、边界、通道和调用开销 |
| Region/XLD 显示 | `disp_obj` 及现有 ROI 公共显示能力 |
| 3D 显示 | `disp_object_model_3d`；确认相机/姿态、持久化和兼容模式 |
| 3D 投影/平面交点 | `project_3d_point`、`image_points_to_world_plane`；确认标定和适用域 |

具体 C# 类型/封送歧义仅阻断相应调用；后端确实未装配或不满足能力条件时返回 `VIEWPORT-007 CapabilityUnavailable`。不因未扫描包装程序集而把官方已存在的算子判为不可用，不直接接 `HOperatorSet`/`halcondotnet.dll`。同一显示窗口及其对象由适配器串行拥有，不以算子的 reentrant 属性推断同一窗口可并发写入。HALCON 可显示不代表可拾取、可计量或拥有实机标定。

### 2.3 可借鉴资料的处理

`../../references/project-snapshots/AsunControl/20261004/original/ROI` 的 `HalconDrawControl`、`DrawCore`、`ShapeBase`、`DrawConfig`、`ShapeSerializer` 和 `WindowDisplay` 只作为行为和接入风险参考：

- 可借鉴：ROI 类型/调节点、绘制与编辑事件、HALCON row/column 交换、窗口平移缩放的用户意图。
- 不继承：.NET 8 WinForms 宿主、裸 `HObject`/`HWindow` 暴露、`List<ShapeBase>` 可变共享、静默吞异常、固定 50 步快照、`HALCON_DRAW_V1.0` 二进制文件、以屏幕/列表索引作为身份。
- 适配原则：先包成只读/租约/typed intent 端口，逐项验证坐标、版本、资源和异常语义，再决定是否复用公开能力；不重做已确认的 ROI 算法。

## 3. 分层和独立交付形状

### 3.1 四个层次

```text
Viewport.Core
  显示计划、坐标桥、状态机、命中排序、参数校验、取消/超时、资源排空、事件与错误语义
Viewport.Adapters
  Frames/Coordinates/RoiGeometry/SurfaceData/AsunImage 的显式端口适配
Viewport.Wpf
  可选 WPF/DevExpress 25.2.3 控件、输入路由、UIA、主题和语言投影
Viewport.TestHost
  无 UI 回放、模拟租约、故障注入和第二消费者最小宿主
```

Core 可在服务、控制台、测试或独立测量工具中运行，不创建窗口、不读取数据库、不依赖 `Dispatcher`。WPF 层只负责输入、布局、绘制提交、UIA 和用户可见文本；业务校验和操作均回到 Core 同一入口。

### 3.2 生命周期

每个实例按 `Create → Attach → Ready → Update/Interact → DisposeAsync → Draining → Drained` 运行。`Create` 只校验 options 并构造无资源 session；`AttachAsync` 才校验上下文并取得源租约。Dispose 可在未 Attach、Attach 失败或正常运行时调用；它立即停止接收新操作、撤销当前呈现并排空已取得资源。重复调用共享同一次关闭过程。

### 3.3 Module API Contract v0.1：factory、session与资源准入

以下为本指导唯一 factory、options、context、session 和最小宿主 API。正文其他章节必须沿用这些成员；不得再以匿名 `factory`、`null` 或上下文中的能力字段推断模式。

```csharp
public interface IViewportFactory
{
    IViewportSession Create(ViewportOptions options);
}

public enum ViewportAccessMode
{
    ReadOnly = 0,
    EditableDraft = 1
}

[Flags]
public enum ViewportFeature
{
    None = 0,
    Navigation = 1,
    Probe = 2,
    Surface3D = 4,
    SurfacePick = 8,
    RoiEditing = 16,
    Presentation = 32
}

public enum ResourceAdmissionMode
{
    BudgetOnly = 0,
    Required = 1
}

public enum ResourceAdmissionOutcome
{
    Accepted = 0,
    Rejected = 1,
    Conflict = 2,
    Unknown = 3
}

public enum ViewportResourceScopeKind
{
    Creation = 0,
    Decode = 1,
    Display = 2,
    Export = 3,
    PersistentBaseline = 4
}

public enum ViewportAllocationState
{
    Reserved = 0,
    Started = 1,
    Settled = 2,
    Unknown = 3,
    Released = 4,
    Aborted = 5
}

public sealed record ViewportAllocationRequest(
    string OwnerId,
    string AllocationId,
    string Kind,
    long ExactBytes,
    string Purpose,
    string AuthorizationRevision,
    string ScopeId,
    ViewportResourceScopeKind ScopeKind,
    DisplayGeneration Generation,
    DateTimeOffset ExpiresAtUtc);

public sealed record ViewportAllocationBinding(
    string OwnerId,
    string AllocationId,
    string ScopeId,
    ViewportResourceScopeKind ScopeKind,
    DisplayGeneration Generation,
    long ApprovedBytes,
    DateTimeOffset ExpiresAtUtc);

// Runtime-only opaque capabilities implemented by the issuing resource Owner.
// The Owner validates issuer identity and the binding on every call; never serialize or transfer them.
public interface IViewportAllocationPermit { }
public interface IViewportResourceLease { }
public interface IViewportResourceEvidence { }

public sealed record ViewportAllocationSnapshot(
    string OwnerId,
    string AllocationId,
    string ScopeId,
    ViewportResourceScopeKind ScopeKind,
    DisplayGeneration Generation,
    long ApprovedBytes,
    DateTimeOffset ExpiresAtUtc,
    ViewportAllocationState State,
    long? ActualBytes,
    string? BackingIdentity,
    string? Diagnostic);

public sealed record ViewportAllocationDecision(
    ResourceAdmissionOutcome Outcome,
    IViewportAllocationPermit? Permit,
    ViewportAllocationSnapshot? Snapshot,
    string? Reason);

public sealed record ViewportAllocationReceipt(
    ResourceAdmissionOutcome Outcome,
    IViewportResourceLease? Lease,
    ViewportAllocationSnapshot Snapshot,
    string? Reason);

public interface IViewportResourceAdmission
{
    Task<ViewportAllocationDecision> TryBeginAsync(
        ViewportAllocationRequest request, CancellationToken cancellationToken);

    // Unknown TryBegin may not return a permit. Query the SAME request identity.
    // Accepted must return its original permit; Unknown must never authorize allocation.
    Task<ViewportAllocationDecision> ResolveAsync(
        ViewportAllocationRequest originalRequest, CancellationToken cancellationToken);

    Task<ViewportAllocationReceipt> GetStatusAsync(
        IViewportAllocationPermit permit, CancellationToken cancellationToken);

    Task<ViewportAllocationReceipt> MarkStartedAsync(
        IViewportAllocationPermit permit, CancellationToken cancellationToken);

    Task<ViewportAllocationReceipt> SettleCreatedAsync(
        IViewportAllocationPermit permit, long actualBytes,
        string backingIdentity, CancellationToken cancellationToken);

    Task<ViewportAllocationReceipt> AbortUnstartedAsync(
        IViewportAllocationPermit permit, string reason,
        CancellationToken cancellationToken);

    Task<ViewportAllocationReceipt> MarkUnknownAsync(
        IViewportAllocationPermit permit, string reason,
        CancellationToken cancellationToken);

    Task<ViewportAllocationReceipt> ReleaseAsync(
        IViewportAllocationPermit permit, IViewportResourceLease lease,
        IViewportResourceEvidence evidence,
        CancellationToken cancellationToken);
}

public sealed record ViewportOptions(
    string ConsumerId,
    ViewportAccessMode AccessMode,
    ViewportFeature RequestedFeatures,
    IFramePort Frames,
    ICoordinatePort Coordinates,
    IAuthorizationPort Authorization,
    long MaxDisplayBytes,
    int MaxInFlightTiles,
    ResourceAdmissionMode ResourceAdmissionMode,
    TimeSpan DrainTimeout = default,
    TimeSpan OperationTimeout = default,
    IRoiPort? Roi = null,
    ISurfacePort? Surface = null,
    IProbePort? Probe = null,
    IPresentationPort? Presentation = null,
    IViewportResourceAdmission? ResourceAdmission = null,
    ViewportLimits? Limits = null,
    BackendPolicy BackendPolicy = BackendPolicy.HalconRequired,
    IViewportBackendFactory? Backend = null,
    IViewportIntentSink? IntentSink = null,
    TimeSpan? UpdateThrottle = null);

public sealed record ViewportContext(
    IReadOnlyList<SourceBinding> Sources,
    IReadOnlyList<OverlayLayer> Layers,
    AuthorizationSnapshot Authorization,
    string Language,
    ApiVersion Version,
    long ContextRevision,
    ViewState InitialView);

public enum OperationOutcome
{
    Succeeded,
    Partial,
    Rejected,
    Cancelled,
    TimedOut,
    Failed
}

public sealed record ViewportResult<T>(
    OperationOutcome Outcome,
    T? Value,
    ViewportError? Error,
    ViewportState State,
    CleanupSnapshot Cleanup)
{
    public bool Succeeded => Outcome == OperationOutcome.Succeeded;
}

public sealed record DisposeReceipt(
    bool Drained,
    bool WaitCancelled,
    IReadOnlyList<PendingResource> PendingResources,
    ViewportError? Error,
    CleanupSnapshot Cleanup);

// Pure 2D contract is closed in §3.4. Session/ports still have the gates in §18.
public interface IViewportPureOperations
{
    PlanValidation Validate(PlanInputs inputs);
    PlanResult BuildDisplayPlan(PlanInputs inputs);
    PointerMapping MapPointer(DipPoint pointer, DisplayPlan plan);
}

public interface IViewportSession
{
    string SessionId { get; }
    ViewportState State { get; }
    ViewportAccessMode AccessMode { get; }
    ResourceAdmissionMode ResourceAdmissionMode { get; }
    ViewportFeature EffectiveFeatures { get; }
    ViewportSnapshot GetSnapshot();
    Task<ViewportResult<AttachReceipt>> AttachAsync(ViewportContext context, CancellationToken ct);
    Task<ViewportResult<UpdateReceipt>> UpdateAsync(ViewportUpdate update, CancellationToken ct);
    Task<ViewportResult<ViewportReceipt>> ApplyAsync(ViewportCommand command, CancellationToken ct);
    Task<ViewportResult<ProbeResult>> ProbeAsync(ProbeRequest request, CancellationToken ct);
    Task<DisposeReceipt> DisposeAsync(TimeSpan timeout, CancellationToken ct);
    event EventHandler<ViewportEventArgs> EventRaised;
}
```

Required options: nonblank `ConsumerId`; defined `AccessMode` and `ResourceAdmissionMode`; `RequestedFeatures` explicitly contains `Navigation`; non-null `Frames`, `Coordinates`, and `Authorization`; explicit `MaxDisplayBytes` and `MaxInFlightTiles`. The two budget values must be supplied by the host's approved budget snapshot. `ResourceAdmissionMode.Required` requires `ResourceAdmission`; `BudgetOnly` requires it to be null and may be selected only by an explicitly offline viewing/replay consumer. Any online, shared-pool, or production-backed consumer must use `Required`; the host owns this workload declaration and the module does not infer it from product names. Optional `Roi`, `Surface`, `Probe`, and `Presentation` ports do not enable features. `Create` rejects unknown feature bits, missing ports for explicitly requested features, `SurfacePick` unless `Surface3D` and `Surface` are supplied; `Surface3D` requires `Surface`; `Probe` requires `Probe`; `Presentation` requires `Presentation`; `RoiEditing` unless `AccessMode=EditableDraft` and `Roi` is supplied, and `EditableDraft` unless `RoiEditing` was explicitly requested. A supplied ROI port may serve read-only geometry hit testing, but its ValidateDraft/CreateCommitCandidate edit entries remain unavailable without EditableDraft plus RoiEditing and current edit rights. Runtime authorization is rechecked on Attach and each protected operation; configured edit capability never grants user permission.

`Create` throws `ArgumentNullException` for a null options reference and `ViewportConfigurationException` for invalid combinations. It performs no IO, subscription, handle creation, lease acquisition, rendering, or background work. `DrainTimeout=default` 和 `OperationTimeout=default` 各解析为 5 秒；显式值须在 `[50 ms, 10 min]`。它们是有限等待/操作预算，不是性能达标目标。操作预算在接纳时以单调时钟开始，包含排队、端口调用和提交；传给端口剩余预算，排空另按 §6.2 处理，不在每次重试时重置。 `MaxDisplayBytes` and `MaxInFlightTiles` are admission budgets, not performance targets: they are required host inputs and are rejected when outside the hard ranges in §4.4; the session never supplies a default or silently clamps them. `ResourceAdmissionMode.Required` without its authority or `BudgetOnly` with an authority is rejected before session creation. The host must not select `BudgetOnly` for an online/production workload; this semantic workload boundary is explicitly declared by the consumer, not inferred from product names. The session exposes immutable `AccessMode`, `ResourceAdmissionMode` and validated `EffectiveFeatures`; callers must use these values rather than infer capability from ports.

`AttachAsync` is allowed once. Empty `Sources` is valid and returns `Empty` without taking leases. Invalid context or failed authorization returns a rejected result without acquiring leases. Cancellation during acquisition stops further acquisition, releases already-acquired leases, and returns `Cancelled`; if native release is still pending, State remains `Draining` and the caller must invoke `DisposeAsync` to observe completion. A session whose Attach was cancelled or failed is not reusable.

`DisposeAsync(timeout, ct)` is the only session close-and-drain API; content-only cleanup with admission preserved uses the existing UpdateAsync route in §4.7.1. The session intentionally does not expose a parameterless asynchronous-dispose contract. The first call closes admission, revokes presentation, cancels this session's waits, then drains native/GPU work and releases owned resources. It returns `Drained=true` only after all session execution/borrowed-resource returns have real completion evidence; root takeover is separately OwnerAccepted, never Drained. Timeout returns `Drained=false`, State `Draining`, and pending resource identities; a later call waits on the same drain. Cancelling `ct` cancels only the caller's wait (`WaitCancelled=true`); cleanup continues. Callers must invoke this method explicitly so an incomplete drain receipt cannot be hidden by automatic scope cleanup.

同步入口只允许使用调用方已经持有的不可变快照，执行有限的参数校验、矩阵组合、显示计划计算和纯指针映射；它不能读取文件、取得或归还租约、调用可能阻塞的 HALCON/native/GPU 能力、等待 UI、启动后台工作或写入事实。同步结果为确定的 `PlanValidation`、`PlanResult`、`PointerMapping`；不调用精确ROI端口命中或交付事实意图，不能把“未加载”折叠成默认值。

异步入口负责 Attach/Update、Tile/纹理解码与上传、原值/插值探针、3D 拾取、ROI 端口调用、导出端口调用和 `DisposeAsync`/Drain。异步入口复用同步入口的校验与数学实现，先校验后取得资源；取消、超时、后端失败和排空状态通过回执返回。不得为 UI 方便另写一套同步算法，也不得把异步操作用 `.Result`/`.Wait()` 包装在 UI 线程。

API Contract v0.1 保留以下语义：输入不可变或由租约保护；回执包含实际值/修订/状态；取消等待、操作取消、超时和真实排空可区分；未知结果不映射为成功；事件不包含 HALCON/native 句柄。

### 3.4 纯 2D 计划切片的闭合公开类型

本节是 `Asun.UI.Viewports` 下无 UI、无租约、无视觉对象的 Module API Contract v0.1 子集；不是另一套平台图像/坐标 Schema。006/007 的消费适配器把已发布的几何投影成这些输入，不更改其事实。类型声明如下，集合在调用边界复制成模块拥有的不可变快照，不保留调用者可写的数组/集合。record 的只读属性本身不能证明深层不可变。

```csharp
public readonly record struct DipPoint(double X, double Y);
public readonly record struct DipSize(double Width, double Height);
// Source boundary coordinates: center (u,v) is boundary (u+0.5,v+0.5).
public readonly record struct PixelRect(double Left, double Top, double Right, double Bottom);
// x'=M11*x+M12*y+Tx, y'=M21*x+M22*y+Ty. All coefficients double.
public readonly record struct AffineMap2D(
    double M11, double M12, double M21, double M22, double Tx, double Ty);
public sealed record PlanSource(
    SourceId SourceId, string SourceRevision, CoordinateRevision CoordinateRevision,
    long WidthPx, long HeightPx, PixelRect CropBoundary);
// Level center -> original SOURCE center; never infer from rounded dimensions.
public sealed record PyramidLevelPlanInput(
    int LevelId, long WidthPx, long HeightPx, int TileWidthPx, int TileHeightPx,
    AffineMap2D LevelCenterToSourceCenter, long MaxDecodedTileBytes);
public sealed record PlanView(
    DisplayMode2D Mode, double Zoom, double RotationRadians,
    bool MirrorX, bool MirrorY, DipPoint PanDip);
public sealed record PlanInputs(
    PlanSource Source, DisplayGeneration Generation, DipSize CanvasDip,
    double DpiScaleX, double DpiScaleY, PlanView View,
    IReadOnlyList<PyramidLevelPlanInput> Levels,
    int MaxPlanTiles, long MaxPlanDecodedBytes);
public enum PlanError
{
    None, InvalidInput, InputLimitExceeded, CoordinateUnavailable, NoLevelFitsBudget
}
public sealed record PlanValidation(PlanError Error, string? Field);
// Bounds half-open. Empty ranges have Start==End; long checked arithmetic.
public readonly record struct TileRange(
    long ColumnStart, long ColumnEndExclusive, long RowStart, long RowEndExclusive);
public sealed record DisplayPlan(
    SourceId SourceId, string SourceRevision, CoordinateRevision CoordinateRevision,
    DisplayGeneration Generation, PlanView ActualView,
    AffineMap2D SourceCenterToDip, AffineMap2D DipToSourceCenter,
    PixelRect VisibleSourceBoundary, int LevelId, TileRange VisibleTiles,
    DipSize CanvasDip, double DpiScaleX, double DpiScaleY,
    long PlannedTileCount, long PlannedDecodedBytes, bool WasClamped,
    bool BudgetDegraded);
public sealed record PlanResult(PlanError Error, string? Field, DisplayPlan? Plan);
public enum PointerMappingKind { Mapped, OutsideImage, InvalidInput }
public sealed record PointerMapping(
    PointerMappingKind Kind, double? ColumnCenter, double? RowCenter,
    SourceId SourceId, string SourceRevision, CoordinateRevision CoordinateRevision,
    DisplayGeneration Generation);
```

有效域：SourceId/SourceRevision 非空，修订/Generation 非负；尺寸依 §4.2，CropBoundary 在 `[0,W]×[0,H]` 内且正面积。CanvasDip 各轴有限且大于 0；未布局的零画布由 UI 等待，不调用 planner 或命中旧计划。DpiScaleX/Y 各轴遵守 §4.4；Levels 非空、LevelId 唯一非负、维度与 tile 尺寸为正、`MaxDecodedTileBytes>0`，level 变换可逆且轴向、正缩放（旋转/透视金字塔不纳入此子集）。Level 轴比例由变换导出，不用 Width/原 Width 猜倍率。`MaxPlanTiles` 和 `MaxPlanDecodedBytes` 是宿主/会话剩余计划预算，须正数并不超过已批准会话预算；不是后台队列默认大小或预取额度。

Validate 只返回首个失败字段，顺序为 source→canvas/dpi→view→levels→budgets；BuildDisplayPlan 先复用 Validate，失败 `Plan=null`，不返回旧矩阵。不实现 IDisposable、不启动任务、不调用 Frame/Coordinate/HALCON/Dispatcher。输出有限且无 float；所有 tile 数/字节乘法使用 checked long，溢出即 InputLimitExceeded。MapPointer 使用 plan 已封存的逆变换，只负责源几何位置：位于 crop 半开外边界时 OutsideImage；不宣称 mask 有效或有读取权限，原值查询仍走 §7.4。非法/非有限 pointer 返回 InvalidInput，不返回 `(0,0)`。

这是实施语义和类型闭合，不是已执行代码/编译证据。现有 `ViewportTransform` 的 float/Vector2 与此 double、像素中心约定不等价；现有 `TileRequestPlanner` 的全范围集合展开不能证明有界。未来切片须在已绑定 Core 工程内适配/替换受影响实现并定向回归，不扩散重写，也不把旧 smoke 通过视为新契约通过。

### 3.5 Session、运行态和端口的闭合模块契约

以下声明属于 `Asun.UI.Viewports`，与 §3.3/3.4/4.1 一起组成唯一公开类型。输入 record/collection 全部在边界深拷贝，字符串限额在拷贝前检查；Opaque payload 和 lease 只在其 Owner 声明的借用期可用。所有资源/IO 异步成员返回 **原始 Task**，调用方不能以 WaitAsync 产生的等待 Task 替换生命周期对象。Core 不包含 WPF、HALCON、SDK类型、object/dynamic payload 或产品 VM。

```csharp
public readonly record struct OperationId(string Value);
public readonly record struct GestureId(string Value);
public readonly record struct ApiVersion(int Major, int Minor); // initial module API 0.1
public enum ViewportState
{
    Created, Attaching, Ready, Empty, Updating, Stale, Blocked,
    RecoverableError, Disposing, Draining, Drained, Disposed
}
public enum CleanupState { None, Pending, Drained, OwnerAccepted, Unknown }
public sealed record ViewportError(
    string Code, OperationId OperationId, string Stage, string Field,
    bool Retryable, string RecoveryKey, string SafeDiagnostic);
public sealed record ViewportNotice(string Key, string Field, string ActualValue);
public sealed record PendingResource(
    string OwnerId, string ScopeId, OperationId OperationId,
    DisplayGeneration Generation, string TaskId, string? LeaseId,
    string? AllocationId, string? BackingIdentity, string Stage, long ReservedBytes);
public sealed record CleanupSnapshot(
    CleanupState State, IReadOnlyList<PendingResource> Pending,
    ViewportError? Error, string? AcceptedTransferId);
public sealed record CallContext(
    ApiVersion Version, OperationId OperationId, string TaskId,
    DisplayGeneration Generation, string AuthorizationRevision,
    TimeSpan RemainingBudget);
public enum ViewportPurpose { OfflineViewing, EngineeringDraft, EvidenceReview, ProductionDisplay }
[Flags]
public enum ViewportRight { None=0, Read=1, Probe=2, EditDraft=4, Export=8 }
public sealed record AuthorizationSnapshot(
    string OwnerId, string Revision, ViewportPurpose Purpose,
    ViewportRight Rights, string AccessDomain, DateTimeOffset ExpiresAtUtc);
public sealed record AuthorizationRequest(
    IReadOnlyList<SourceId> Sources, ViewportRight RequiredRight,
    AuthorizationSnapshot Expected);
public interface IAuthorizationPort
{
    Task<PortResult<AuthorizationSnapshot>> CheckAsync(
        AuthorizationRequest request, CallContext call, CancellationToken ct);
    // Revocation event carries a NEW snapshot, never token/credentials.
    event EventHandler<AuthorizationChangedEventArgs> Changed;
}
public sealed class AuthorizationChangedEventArgs : EventArgs
{
    public AuthorizationSnapshot Snapshot { get; }
    public AuthorizationChangedEventArgs(AuthorizationSnapshot snapshot) => Snapshot=snapshot;
}
public sealed record SourceTiming(string AcquisitionId, string TimeBasisId,
    DateTimeOffset AcquiredAtUtc, TimeSpan Uncertainty);
public enum SourceRole { Primary, Secondary, Overview, CurrentFov, Reference }
public sealed record SourceBinding(
    SourceRole Role, ImageSourceDescriptor? Image, SurfaceSourceDescriptor? Surface,
    string CorrelationId, SourceTiming? Timing = null); // at least one Image/Surface, same SourceId when both
public sealed record ViewportUpdate(
    long BaseContextRevision, ViewportContext Replacement); // full replace only
public sealed record SourceStatus(SourceId SourceId, bool Presented, ViewportError? Error);
public sealed record AttachReceipt(
    long ContextRevision, DisplayGeneration Generation, IReadOnlyList<SourceStatus> Sources);
public sealed record UpdateReceipt(
    long ContextRevision, DisplayGeneration Generation, IReadOnlyList<SourceStatus> Sources,
    EmptyTransitionReceipt? EmptyTransition = null);
public sealed record ViewportSnapshot(
    ViewportState State, long ContextRevision, DisplayGeneration Generation,
    ViewState View, IReadOnlyList<SourceStatus> Sources,
    AuthorizationSnapshot? Authorization, CleanupSnapshot Cleanup,
    EmptyTransitionReceipt? EmptyTransition = null);
public sealed record ViewState(
    ViewKind Kind, PlanView ImageView, DipSize CanvasDip,
    double DpiScaleX, double DpiScaleY, CameraView3D? Camera, int? ManualLod,
    LutWindow? Lut, double SelectionToleranceDip, SurfaceProfileRequest? Profile = null)
{
    public static ViewState Fit2D(DipSize canvas, double dpiX, double dpiY) =>
        new(ViewKind.Image2D, new(DisplayMode2D.Fit,1,0,false,false,new(0,0)),
            canvas,dpiX,dpiY,null,null,null,6);
}
public sealed record LutWindow(double Minimum, double Maximum, string StatisticsRevision);
public enum PointerAction { Down, Move, Up, Cancel }
public enum PointerTool { Navigate, Probe, Select, EditDraft }
public sealed record PointerSample(
    OperationId OperationId, GestureId GestureId, SourceId SourceId,
    string SourceRevision, CoordinateRevision CoordinateRevision,
    DisplayGeneration Generation, DipPoint PositionDip, PointerAction Action,
    PointerTool Tool, bool PrimaryButton);
public enum SelectionKind { Navigation, Probe, DraftCandidate }
public sealed record SelectionRequest(PointerSample Pointer, int CandidateLimit);
public sealed record SelectionCandidate(
    StableObjectId ObjectId, StableObjectId LayerId, SelectionKind Kind,
    double DistanceDip, int SelectionPriority);
public sealed record SelectionResult(
    PointerSample Pointer, IReadOnlyList<SelectionCandidate> Candidates, bool Truncated);
public enum ProbeValueUnit { GrayValue, PixelHeight, Micrometer, Millimeter }
public enum ProbeValidity { OriginalSample, Interpolated, MaskInvalid, NotLoaded,
    Outside, SupportInvalid, NoMapping, PermissionDenied }
public sealed record ProbeRequest(
    OperationId OperationId, SourceId SourceId, string SourceRevision,
    CoordinateRevision CoordinateRevision, DisplayGeneration Generation,
    DipPoint PositionDip, string Channel, ProbeMode Mode);
public sealed record SampleContribution(long Column, long Row, double Weight);
public sealed record ProbeResult(
    ProbeValidity Validity, SourceId SourceId, string SourceRevision,
    CoordinateRevision CoordinateRevision, DisplayGeneration Generation,
    string Channel, double? Value, ProbeValueUnit Unit, string ValueKind,
    IReadOnlyList<SampleContribution> Support);
public interface IProbePort
{
    Task<PortResult<ProbeResult>> ReadAsync(ProbeSourceRequest request, CallContext call,
        CancellationToken ct);
}
public sealed record ProbeSourceRequest(
    ProbeRequest Original, double ColumnCenter, double RowCenter);
public enum PortOutcome { Succeeded, Rejected, Unknown, Cancelled, TimedOut, Failed }
public sealed record PortResult<T>(PortOutcome Outcome, T? Value, ViewportError? Error);
public sealed record LeaseIdentity(
    string OwnerId, string LeaseId, string BackingIdentity, long RetainedBytes,
    SourceId SourceId, string SourceRevision, DisplayGeneration Generation);
public sealed record LeaseReturnRequest(string ReturnId, string Reason, TimeSpan Budget);
public enum LeaseReturnState { Returned, Pending, Unknown }
public sealed record LeaseReturnReceipt(
    LeaseReturnState State, LeaseIdentity Identity, string ReturnId, ViewportError? Error);
public interface IViewportLease
{
    LeaseIdentity Identity { get; }
    // Completion is true borrower quiescence, NOT physical refund for a shared pool.
    Task<LeaseReturnReceipt> ReturnAsync(LeaseReturnRequest request, CancellationToken ct);
    Task<LeaseReturnReceipt> QueryReturnAsync(string returnId, TimeSpan budget, CancellationToken ct);
}
public sealed record FrameRequest(
    SourceId SourceId, string SourceRevision, CoordinateRevision CoordinateRevision,
    int LevelId, long TileColumn, long TileRow, string DecodeRevision, string AccessDomain);
public enum PixelSampleKind { UInt8, UInt16, Int16, Float32, Float64 }
public sealed record PixelLayout(
    int Width, int Height, int ChannelCount, long StrideBytes,
    PixelSampleKind Kind, bool LittleEndian, bool Interleaved);
public interface IFramePayload { } // opaque adapter-owned read-only frame/tile, no exposed handles
public interface IFrameLease : IViewportLease
{
    PixelLayout Layout { get; }
    PixelRect ValidSourceBoundary { get; }
    AffineMap2D TileCenterToSourceCenter { get; }
    IFramePayload Payload { get; }
}
public interface IFramePort
{
    Task<PortResult<IFrameLease>> AcquireAsync(FrameRequest request, CallContext call,
        CancellationToken ct);
}
public sealed record CoordinateRequest(
    SourceId SourceId, CoordinateRevision Revision, string FromSpace, string ToSpace,
    IReadOnlyList<Point3D> Points);
public readonly record struct Point3D(double X, double Y, double Z);
public sealed record CoordinateResult(
    CoordinateRevision Revision, string ToSpace, LengthUnit Unit,
    IReadOnlyList<Point3D> Points, IReadOnlyList<bool> Valid);
public interface ICoordinatePort
{
    Task<PortResult<CoordinateResult>> MapAsync(CoordinateRequest request, CallContext call,
        CancellationToken ct);
}
public enum RoiGeometryKind { Rectangle, RotatedRectangle, Ellipse, Polygon, Region, Polyline }
public readonly record struct SourcePoint2D(double Column, double Row);
public sealed record RoiRing(IReadOnlyList<SourcePoint2D> Vertices, bool IsHole);
// Primitive fields preserve kind; Region keeps its 020 opaque revision, never a handle.
public sealed record RoiGeometrySnapshot(
    StableObjectId ObjectId, RoiGeometryKind Kind, GeometryRevision Revision,
    SourcePoint2D Center, double Width, double Height, double AngleRadians,
    IReadOnlyList<RoiRing> Rings, string GeometryAssetRevision);
public sealed record RoiDraft(
    GestureId GestureId, SourceId SourceId, string SourceRevision,
    CoordinateRevision CoordinateRevision, GeometryRevision BaseGeometryRevision,
    DisplayGeneration Generation, RoiGeometrySnapshot Proposed);
public sealed record RoiEditRequest(PointerSample Pointer, RoiGeometrySnapshot Geometry);
public sealed record RoiValidationResult(bool Valid, IReadOnlyList<ViewportNotice> Notices);
public sealed record RoiCommitCandidate(string CandidateId, RoiDraft Draft,
    GeometryRevision ExpectedRevision); // NOT committed geometry
public sealed record GeometryHitRequest(PointerSample Pointer, double ToleranceDip,
    AffineMap2D SourceToDip, IReadOnlyList<RoiGeometrySnapshot> Geometry, int CandidateLimit);
public interface IRoiPort
{
    Task<PortResult<SelectionResult>> HitTestAsync(GeometryHitRequest request,
        CallContext call, CancellationToken ct);
    Task<PortResult<RoiValidationResult>> ValidateDraftAsync(RoiDraft draft,
        CallContext call, CancellationToken ct);
    Task<PortResult<RoiCommitCandidate>> CreateCommitCandidateAsync(RoiDraft draft,
        CallContext call, CancellationToken ct);
}
public sealed record CameraView3D(
    IReadOnlyList<double> Projection4x4, IReadOnlyList<double> WorldToCamera4x4,
    IReadOnlyList<double> DisplayModel4x4, double Near, double Far, double ZMultiplier,
    string CameraRevision, Point3D InitialPivot, int DefaultLodId,
    double? MaxProjectedLodErrorPixels = null); // row-major; column vectors; right-handed; §8.4
public sealed record SurfaceRequest(SourceId SourceId, string SurfaceRevision, int LodId);
public interface ISurfacePayload { } // opaque 027 read-only model; adapter private types stay private
public interface ISurfaceLease : IViewportLease
{
    int LodId { get; }
    ISurfacePayload Payload { get; }
}
public enum SurfaceHitKind { OriginalSample, Interpolated, NoHit, Invalid, Ambiguous, NoMapping }
public sealed record SurfacePickRequest(
    SourceId SourceId, string SurfaceRevision, CoordinateRevision CoordinateRevision,
    DisplayGeneration Generation, long BackendGeneration, CameraView3D Camera,
    DipPoint PointerDip, DipSize CanvasDip, int CandidateLimit);
public sealed record SurfaceContribution(string OriginalIndex, double Weight);
public sealed record SurfaceHit(
    SurfaceHitKind Kind, StableObjectId? ObjectId, Point3D? SourcePoint,
    LengthUnit Unit, string SurfaceRevision, IReadOnlyList<SurfaceContribution> Support);
public interface ISurfacePort
{
    Task<PortResult<ISurfaceLease>> AcquireLodAsync(SurfaceRequest request, CallContext call,
        CancellationToken ct);
    Task<PortResult<SurfaceProfileResult>> ReadProfileAsync(
        SurfaceProfileRequest request, CallContext call, CancellationToken ct);
    Task<PortResult<IReadOnlyList<SurfaceOverlayProjection>>> ProjectOverlayAsync(
        SurfaceOverlayRequest request, CallContext call, CancellationToken ct);
    Task<PortResult<IReadOnlyList<SurfaceHit>>> PickAsync(SurfacePickRequest request,
        CallContext call, CancellationToken ct);
}
public enum IntentKind { Selection, RoiCandidate, MeasurementRequest, ExportRequest, LinkedNavigation }
public sealed record ViewportIntent(
    IntentKind Kind, OperationId OperationId, SourceId SourceId, string SourceRevision,
    CoordinateRevision CoordinateRevision, DisplayGeneration Generation,
    SelectionResult? Selection, RoiCommitCandidate? RoiCandidate,
    IReadOnlyList<Point3D> Points, string CorrelationId,
    IReadOnlyList<SurfaceHit>? SurfaceEvidence = null,
    IReadOnlyList<ProbeResult>? ProbeEvidence = null);
public interface IViewportIntentSink
{
    Task<PortResult<string>> AcceptAsync(ViewportIntent intent, CallContext call,
        CancellationToken ct); // acknowledgment/candidate ID, never quality release
}
public enum ViewportEventKind { OperationAccepted, AuthorizationChecked, SourceLeaseAcquired,
    PlanBuilt, BackendSubmitted, PresentationCommitted, PresentationRevoked, ResultReady,
    DrainStarted, Drained, ResourcesReleased, OperationCompleted, OperationFailed,
    CancelRequested, DeadlineReached, OperationCancelled, OperationTimedOut,
    LateResultDiscarded, AdmissionClosed, SessionDisposed, IntentReady, OwnerTransferAccepted,
    ObjectSelectionChanged }
public enum EventScopeKind { Operation, Presentation, Session }
public sealed class ViewportEventArgs : EventArgs
{
    public ViewportEventKind Kind { get; init; }
    public OperationId OperationId { get; init; }
    public EventScopeKind ScopeKind { get; init; }
    public string ScopeId { get; init; } = "";
    public DisplayGeneration Generation { get; init; }
    public string SourceRevision { get; init; } = "";
    public CoordinateRevision CoordinateRevision { get; init; }
    public string AuthorizationRevision { get; init; } = "";
    public DateTimeOffset TimestampUtc { get; init; }
    public long Sequence { get; init; }
    public ViewportIntent? Intent { get; init; }
    public OverlayObjectSelectionReceipt? ObjectSelection { get; init; }
    public ViewportError? Error { get; init; }
}
```

结果联合规则：Succeeded 必须 Value 非空（空的候选列表是合法 Value）；Rejected/Cancelled/TimedOut/Failed 不返回可用 Value，Unknown 只保留原 Task/查询身份及诊断，不表示不存在租约。Partial 仅在 Session 多来源独立呈现且 receipt 列出每源 Presented/Error 时使用，不用 `Succeeded` 布尔掩盖它。Probe 的 UInt64/Int64/复数不投影成不精确 double：当前原值契约只支持 PixelSampleKind 表中类型；其它格式明确 CapabilityUnavailable，扩展须先定义保真 payload，不改原源数据。ValueKind 只能是 GrayValue/Height；灰度 Unit=GrayValue，不使用长度单位；高度 Unit=PixelHeight/Micrometer/Millimeter，缺标定只允许已声明相对像素高度，不冒称物理单位。Point3D 的 Z 在二维坐标请求中为0而非高度测量。

CallContext 每个 TaskId 由 root 在调用前登记，OperationId 从根内生成唯一字符串；TaskId 不作为业务身份。ResourceAdmission成员按§3.3签名不含CallContext，所有调用仍通过root预留/原Task登记、使用当前scope有效期和剩余OperationTimeout或独立CleanupAttemptBudget，未知保留原请求/permit，由同Owner Resolve/GetStatus；不因为签名只有ct就无界等待。时间预算有限且正数，端口内部可取消；超时调用等待者由模块结果表达，原 Task 必须继续由 root 观察。端口不得同步阻塞创建 Task，不得在失败 Value 中偷带租约；即使端口违约回传资源，root 也须接住并归还、报告协议错误，不能丢弃 Value。Frame/Surface lease 的身份必须匹配请求及当前 generation 或被丢弃并返回；同一 backing 可被两会话各持独立 LeaseId，Return 只归还自己借用。

### 3.6 factory 前的有界进程根 Owner

公开入口为 `IViewportRootFactory.Create(ViewportRootOptions)`，模块提供无 IO 的 `ViewportRootFactory` 公共无参构造；RootFactory 只构造 ledger，不访问设备/文件/Dispatcher。根对象在任何 factory/session 之前由宿主持有；测试/消费者不实现这个根 Owner 来替代模块收敛。实例成员声明如下，生成和关闭实现位于已绑定 Core 工程：

```csharp
public sealed record ViewportLimits(
    int MaxSources, int MaxLayers, int MaxGeometryPoints, int MaxCandidates,
    int MaxQueuedCommands, int MaxQueuedEvents, int MaxStringUtf8Bytes,
    int MaxLevels, int MaxPlanTiles);
public sealed record ViewportRootOptions(
    string RootId, int MaxSessions, int MaxTrackedTasks, int MaxPendingReturns,
    long MaxRetainedBytes, TimeSpan CleanupAttemptBudget, int MaxCleanupAttempts);
public sealed record RootSnapshot(
    string RootId, bool AdmissionClosed, int Sessions, int TrackedTasks,
    long RetainedBytes, IReadOnlyList<PendingResource> Pending);
public sealed record RootCloseReceipt(bool Drained, bool WaitCancelled,
    RootSnapshot Snapshot, ViewportError? Error);
public interface IViewportRootFactory
{
    IViewportProcessRoot Create(ViewportRootOptions options);
}
public interface IViewportProcessRoot
{
    PortResult<IViewportExecutionReservation> ReserveExecution(ExecutionReservation request);
    IViewportFactory CreateFactory(); // returned factory is bound to THIS root
    RootSnapshot GetSnapshot();
    Task<RootCloseReceipt> CloseAsync(TimeSpan timeout, CancellationToken ct);
}
```

根/limits 全部是必填宿主资源政策：整数正数、RootId 非空，MaxSessions≤1024、MaxTrackedTasks/MaxPendingReturns≤1,000,000、MaxRetainedBytes≤long.MaxValue/2；limits 的 Source≤64、Layer≤4096、GeometryPoints≤10,000,000、Candidates≤4096、Levels≤128、QueuedCommands/Events≤1,000,000、StringUtf8Bytes≤1,048,576、PlanTiles≤1,000,000。这些是无溢出防护上限，不是推荐配置或达标目标；关系 MaxPendingReturns≤MaxTrackedTasks，按每个已接纳原Task最坏迟到lease数/返还步骤预留close/return/接管槽（每Acquire允许最多一个lease，后端/Presenter如多项须明确MaxInnerTasks），至少有一个根关闭保留槽，不让普通工作吃完收敛额度。未知资源继续占根容量；根无容量时 **在源获取/准入/后端/Dispatcher任务创建前** Rejected(InputLimitExceeded)，不能“先调用再登记”。Limits=null、Backend=null或未定义BackendPolicy在Create拒绝；Create时宿主已声明离线BudgetOnly用途，Attach再按Authorization.Purpose/访问域复核，ProductionDisplay/EvidenceReview不能BudgetOnly，EngineeringDraft仅宿主声明离线且无共享物理池时可用。有限 CleanupAttemptBudget 与 timeout 在 `[50ms,10min]`，次数1..64；预算来自宿主不当作节拍。

会话 Create 原子占根 session 槽、命令/事件额度及清理保留槽，失败不创建后台动作。每个执行保留 slot 和最大可能留存 bytes（源 lease、旧/新并存、返回任务、Dispatcher引用都计）；真实 bytes 后结算，不能重复减共享 backing 或用负值抵销未知资源。物理 allocation ledger 与逻辑执行 ledger 是两个轴：资源 backing 由原 Owner 计费，本 root 管本进程持有的工作/借用和有界强引用；原 Owner 确认池仍收费不阻止已归还的本会话借用关闭，原 Task 尚在用资源则阻止它关闭。

根为每个原 Task 保留 Task 引用、完整请求、generation、操作结果、Owner、最终资源和原错误；观察包装完成/Task.IsCompleted 不等于借用/Dispatcher排空。Timeout/Cancel 只取消等待及可中断工作，不能解除原 Task 登记。根为迟到结果预留接收和 return 额度；若迟到成功取得 lease，先登记再按原 lease 的 ReturnAsync 清理；即使用户已关页仍由根观察。ReturnAsync/QueryReturnAsync 也保留原 Task，独立清理 token 不链接操作 ct，不在 timed-out Return 上再次 Return，先 QueryReturn 同一 ReturnId。有限尝试结束仍 Pending/Unknown：根保留并关闭新接入、报警，返回非 drained；不能无限循环或强制销毁使用中的资源。

会话 Dispose 首次调用撤交互/关接纳，session→root 的内部接管在同一进程 ledger 原子进行，产生根签发的 AcceptedTransferId（含所有原 Task、尚可返回的 lease、呈现/Dispatcher队列、清理额度）；仅有“交给 root”文字、空列表或日志不成立。根未确认容量/接管时，session 保持强引用且 DisposeReceipt.Drained=false。接管成功的会话可返回 CleanupState.OwnerAccepted；**Drained 仍为 false**，只有根查到会话原工作、呈现借用和返回均真实收敛才为 true。ResourcesReleased 只表示 scope 已完成实际逻辑借用归还，不因接管发出；OwnerTransferAccepted 单独表明责任转移。

Root.CloseAsync 关闭所有会话新接入，发起每个原关闭工作，有限等待；调用者取消只取消等待，根仍存活。宿主应用退出必须先等待或记录 root 的未决回执并交给同进程还活着的受控关闭 Owner；进程确实退出后无法再宣称追踪原 Task，崩溃/断电由资源/存储 Owner 的恢复策略另管，不伪造“下次启动 continuation”。无确认的外部 transfer 不提供 API，模块不靠垃圾回收终结器清场。

## 4. Module API Contract v0.1：来源、参数、后端与操作

### 4.1 标识、修订和单位

```csharp
public readonly record struct SourceId(string Value);
public readonly record struct PresentationRevision(long Value);
public readonly record struct CoordinateRevision(long Value);
public readonly record struct GeometryRevision(long Value);
public readonly record struct DisplayGeneration(long Value);
public readonly record struct StableObjectId(string Value);

public enum LengthUnit { Pixel, Micrometer, Millimeter }
public enum PixelCoordinateConvention { CenterInteger, HalfOpenBoundary }
public enum DisplayMode2D { Fit, OneToOnePhysicalPixel, Custom }
public enum ProbeMode { OriginalSample, Interpolated }
public enum ViewKind { Image2D, Surface3D, Split2D3D, Profile }
```

`SourceId`、对象 ID、坐标修订、几何修订和显示代必须一起传播。字符串仅作外部编码，核心不能用文件名、列表行号或 hash 猜身份。长度/高度必须带单位；单位缺失、混合或转换路径未注册时拒绝。模块所有SourcePoint/Plan/Roi/ProbeSource采用整数中心约定；Descriptor.Convention只记录源原约定，HalfOpenBoundary源在进入端口投影时减0.5变中心，显示再加0.5一次。ValidityBoundary/Crop始终是0..W的半开边界；不能在UI/Probe各自再转换一次。

### 4.2 2D 源和图层

```csharp
public sealed record ImageSourceDescriptor(
    SourceId SourceId,
    long WidthPx,
    long HeightPx,
    int ChannelCount,
    int BitsPerSample,
    bool Signed,
    PixelCoordinateConvention Convention,
    CoordinateRevision CoordinateRevision,
    string SourceRevision,
    IReadOnlySet<string> Channels,
    ValidityDomain Validity,
    IReadOnlyList<PyramidLevelPlanInput> Levels,
    string DecodeRevision,
    SourceStatistics? Statistics = null);

public sealed record OverlayLayer(
    StableObjectId LayerId,
    int ZOrder,
    bool Visible,
    bool Interactive,
    OverlayPayload Payload,
    string SourceRevision);
```

约束：`WidthPx`/`HeightPx` 范围 `1..2_000_000`（默认上限，正式 Profile 可收紧）；`ChannelCount` `1..64`；`BitsPerSample` `1..64`；所有数值必须有限。超过上限返回 `InputLimitExceeded`，不能先分配再失败。大图通过 `PKG-006` Tile/Pyramid；Viewport 不复制整幅图到每个窗口。

### 4.3 3D 表面

```csharp
public sealed record SurfaceSourceDescriptor(
    SourceId SourceId,
    string SurfaceRevision,
    LengthUnit ZUnit,
    CoordinateRevision CoordinateRevision,
    SurfaceValidity Validity,
    LodDescriptor[] AvailableLods,
    bool HasOriginalSampleIndex,
    bool HasPhysicalCalibration);
```

`HasPhysicalCalibration=false` 时可以查看相对高度或像素值（若宿主明确用途），不得显示 mm/µm 标尺、声称计量或把渲染深度当物理 Z。LOD 若为插值网格、体素质心或平滑点，必须携带贡献/源映射；没有映射时 3D 只能导航。

### 4.4 显示配置和范围

| 参数 | 类型/单位 | 默认值 | 有效范围和规则 |
|---|---|---:|---|
| `ViewKind` | 枚举 | `Image2D` | 必须由源能力支持；缺 3D 不伪造 |
| `DisplayMode2D` | 枚举 | `Fit` | Fit 不裁边；1:1 按物理像素定义 |
| `Zoom` | `double`，相对 Fit 倍率 | `1.0` | `[0.01,1000]`；实际 scale=当前旋转后 Fit scale×Zoom；Fit=1，1:1 独立计算不受此倍率限制；非有限拒绝，有限越界 clamp 并回显 |
| `Rotation` | `double`，弧度 | `0` | `[-2π, 2π]`，返回规范化实际值 |
| `MirrorX/MirrorY` | `bool` | `false` | 仅显示变换，不改物理身份/坐标事实 |
| `Pan` | `DipPoint(double X,double Y)`，DIP | `(0,0)` | 必须有限；按 §7.3 旋转后外包范围 clamp；Core 不使用 float/Vector2/RectangleF 保存源几何 |
| `DpiScaleX/Y` | `double` | 宿主实际各轴值 | `(0.5,8]`；来自窗口，不由模块猜/假定等轴 |
| `ManualLod` | `int?`，LodId/LevelId | null=自动 | 非空须是已发布的LevelId或LodId，不是数组索引；自动选择回显实际ID |
| `SelectionTolerance` | `double`，DIP | `6` | `[0,64]`；0 表示精确命中 |
| `HandleSize` | `double`，DIP | `8` | `[2,32]`；不得按源像素固定 |
| `LineWidth` | `double`，DIP | `1` | `[0.5,16]`；仅显示 |
| `LutMin/LutMax` | `double`，源单位 | 自动 | 手动窗须有限且 min<max；自动仅使用源 Owner 发布的有效域统计，空域/常量/非有限按 §7.4，禁止为求范围扫描全图 |
| `ProbeMode` | 枚举 | `OriginalSample` | 插值必须标记支撑和缺值策略 |
| `MaxInFlightTiles` | `int` | `HostBudgetRequired` | `[1,64]` 硬上限；含解码/上传在途，超界由 `Create` 拒绝 |
| `MaxDisplayBytes` | `long`，bytes | `HostBudgetRequired` | `64 MiB..4 GiB` 硬上限；超界由 `Create` 拒绝，不是性能目标 |
| `UpdateThrottle` | `TimeSpan` | `TargetPending` | `[0,250 ms]`；仅在已批准 PerformanceProfile 显式提供时配置，本文不冻结目标 |
| `OperationTimeout` | `TimeSpan` | `5 s` | `[50 ms, 10 min]`；超时后进入显式恢复状态 |

表中本模块默认值是已定义的显示/预算语义，不是客户验收值；HostBudgetRequired/TargetPending不产生隐式预算或时延目标。宿主必须在 `ViewportOptions` 显式提供资源预算；正式 PerformanceProfile 只能另行冻结延迟、刷新窗口和吞吐目标，不能把本表硬上限反向解释为达标证据。任何隐式 clamp、单位转换、LOD 选择或降级都必须在 receipt 中回显实际值和原因；预算越界必须拒绝，不能先分配后失败。

### 4.4.1 运行时物理资源准入（跨宿主通用契约）

`MaxDisplayBytes`/`MaxInFlightTiles` 是会话级硬边界，不能替代每次实际 backing 分配的所有权和生命周期证明。需要接入宿主资源账本的在线 WPF/GPU、Raster、Tile、编码导出和其它可能产生物理副本的路径，必须显式选择 `ResourceAdmissionMode.Required` 并注入中性的 `IViewportResourceAdmission`；缺少该能力时在第一次分配前返回 `VIEWPORT-015 ResourceAdmissionUnavailable`，不得回退到未计费的局部缓存或旧 Loader。离线查看/回放可以显式选择 `BudgetOnly`，但该模式不能被生产宿主或 Required 导出路径隐式采用。

本端口的唯一代码形状定义在 §3.3：`IViewportResourceAdmission` 与不可序列化的 permit、lease、release evidence 均为 Core 契约；类型不引用产品页面、制程、设备或数据库。本文不在资源章节复制第二份 API。

permit 必须由持有对应 backing 生命周期的同一 `OwnerId` 签发，并绑定唯一 `AllocationId`、`ScopeId`/`ScopeKind`、`Generation`、授权修订、批准字节上限与截止时间。Viewport 只能将不透明凭据原样交回同一 Owner，不能自行构造、改写、转移或序列化。Owner 必须原子校验绑定、scope 与授权；所有端口方法须可并发调用，按 `AllocationId` 串行化状态迁移。相同请求/操作的重试幂等并返回同一逻辑结果；同一 ID 出现不同 owner、binding、actual bytes、backing identity 或 release evidence 时返回 `Conflict`，隔离资源并保留账目，禁止覆盖或重复退款。所有者回调和 API 可在不同线程发生，契约不依赖 WPF Dispatcher 的偶然串行化。

实现必须遵守以下顺序和事实：

1. 在 `new` backing、解码缓冲、显示槽、PNG 输出数组或 GPU/WPF 物理容量创建前，先以稳定 `AllocationId`、实际用途、创建 `ScopeId`、代际和**已知精确字节数**调用 `TryBeginAsync`。拒绝、取消、过期或权限撤销发生在准入前时，不得创建部分 backing。回执为 `Unknown`/超时且无法确认 permit 是否签发时，禁止继续分配；必须保留原请求的完整绑定，以 `ResolveAsync(originalRequest, ct)` 向同一 Owner 查询/收敛；它返回 Accepted+原 permit 才能继续，并重新核验期限/授权；Unknown 不得分配，绑定变化返回 Conflict。确认不存在预留由 Owner 返回明确 Rejected 及原因，Viewport 不能以空查询结果推断不存在；不得用新的请求字段覆盖原绑定。必须使用原 `AllocationId`，不得新建替代 ID 规避未决额度。
2. Owner 即将首次执行真实 backing 创建动作时，先 `MarkStartedAsync`；成功后用同一 permit 调用 `SettleCreatedAsync`。`actualBytes` 必须为正、不大于批准上限，并来自 Owner 对已创建 backing 的确定容量计算；禁止用最大预算、估算、池容量总量或预留值结算。settle 成功才产生 opaque `ViewportResourceLease`。`AbortUnstartedAsync` 仅允许 `Reserved` 且从未标记 Started 的预留。已标记 Started 后即使创建抛异常，也不能回退为未开始；异常/取消/崩溃/超时造成结果不明，必须 `MarkUnknownAsync` 并保留账目、permit 和资源隔离；不得 abort、退款或用空快照声称未创建。原 Owner 查询确认有 backing 后才可 settle；确认从未创建后由 Owner 执行其恢复/解除预留策略，Viewport 不自行释放。
3. 一个实际 `backingIdentity` 在同一宿主账本中只计一次；保留同一 backing 的引用不再重复计费。新旧 tile、转换缓冲、编码缓冲和替换期间并存副本分别计费，直到所有消费者退出且 native/GPU/Dispatcher/fence 给出真实排空证据。
4. 归池、`ArrayPool.Return`、置空引用和逻辑 frame/tile lease 归还只表示逻辑释放，不表示物理字节已退款。仅当原 Owner 获得对应物理机制的释放证据（如原 Owner 确认 CPU 容量已撤销、GPU fence/后端确认释放）后，才可对同一 permit+lease 调用 `ReleaseAsync`；证据由该 Owner 生成并绑定 owner、backing、机制和确认时刻。缺证据、未知或超时都保持已计费/待释放，禁止估算退款。失败、迟到和关闭中的任务必须继续由原 Owner 持有并可诊断。
5. 创建 scope、设备/解码执行 scope 和显示借用 scope 分开记录。scope 到期后只能结算已开始的事实；未开始的迟到工作必须拒绝，不能把未确认余量迁移到新 scope。新 scope 必须重新取得 permit。
6. WPF/GPU 无法逐对象提供释放证据的持续容量，以宿主批准的独立 baseline 上界计费且只计一次；不得把它报告成已测得、可逐对象退款的容量。Required 导出复用同一受控准入；没有独立有效 permit 时返回 `ResourceAdmissionUnavailable`。

`TryBeginAsync`、真实 backing 创建、`SettleCreatedAsync`/`AbortUnstartedAsync`/`MarkUnknownAsync`、物理释放和 `Drained` 的事件序列必须带 `OperationId`、`AllocationId`、Owner、scope、generation、授权修订、请求/实际字节、状态和 permit ID 摘要。Viewport 不复制宿主总账，也不自行决定退款、跨 Owner 转移或延长 scope；这些事实由注入端口的资源 Owner 负责。同一释放证据的重试必须幂等，冲突证据不得重复退款。Unknown 仍与本会话未完成工作或借用有关时，不得发该 scope 的 `ResourcesReleased`/`Drained`。借用已实际归还、所有本会话回调已退出，原 Owner 自身持久容量仍未退款时，可结束会话 scope；账本物理容量继续计费，不报告退款或物理销毁。若本会话执行/借用仍未决，按 §3.6 以 OwnerTransferAccepted 记录根接管，不能发 Drained/ResourcesReleased。宿主具体的 permit 签发政策、长寿命池生命周期和共享账本仍由实际消费者决定，不把 AOI 的 attempt、RUN/HMI 状态或额度方案冻结为模块语义。

本节只迁移资源安全契约，不迁移 AOI 产品准入/patch/UI 接线。来源为 `H:\docs\40-development\10-ui\统一板观察器与2D_3D视图开发指导.md`（本轮审阅时 SHA-256：`1B89BCC1B93DF50AFC9052C1732ACAEF3D5443E28C341E6FCCC20C6A665FD2B3`）；源中的 HALCON 24.11 算子和调用假设均未作为本节依据。

### 4.5 请求、响应和意图

```csharp
public abstract record ViewportCommand;
public sealed record SetViewCommand(ViewState Requested) : ViewportCommand;
public sealed record PointerCommand(PointerSample Sample) : ViewportCommand;
public sealed record SelectCommand(SelectionRequest Request) : ViewportCommand;
public sealed record SelectOverlayObjectCommand(OverlayObjectSelectionRequest Request)
    : ViewportCommand; // §4.5.1, read-only identity selection, not pointer hit testing
public sealed record ProbeCommand(ProbeRequest Request) : ViewportCommand;
public sealed record BeginRoiEditCommand(RoiEditRequest Request) : ViewportCommand;
public sealed record EndGestureCommand(GestureId GestureId, bool Commit) : ViewportCommand;

public sealed record ViewportReceipt(
    OperationId OperationId,
    ViewportState State,
    DisplayGeneration Generation,
    ViewState ActualView,
    IReadOnlyList<ViewportNotice> Notices,
    ViewportError? Error,
    SelectionResult? Selection = null,
    IReadOnlyList<SurfaceHit>? SurfaceHits = null,
    RoiCommitCandidate? RoiCandidate = null,
    IReadOnlyList<DisplayPlan>? Plans = null,
    SurfaceProfileResult? Profile = null,
    OverlayObjectSelectionReceipt? ObjectSelection = null);
```

选择结果必须包含 `SourceId`、对象稳定 ID、来源层、坐标修订、显示代和 `SelectionKind`（导航/临时探针/编辑候选）。`ProbeResult` 必须区分原样本、插值、遮罩无效、未加载、越界、无源映射和权限拒绝；0 是合法数据，不得用 0 表达失败。

#### 4.5.1 稳定对象ID只读选择、高亮与聚焦（BC-U2）

原`SelectCommand(SelectionRequest(PointerSample,CandidateLimit))`只做指针候选命中，**没有按ID选择重载**。本节在原Overlay/Selection范围增加如下明确入口（同Core namespace `Asun.UI.Viewports`，目标声明，未实现）；不增加ROI编辑/提交或产品EvidenceId类型：

```csharp
public sealed record OverlayObjectRef(SourceId SourceId, string SourceRevision,
    CoordinateRevision CoordinateRevision, GeometryRevision GeometryRevision,
    StableObjectId LayerId, StableObjectId ObjectId);
public sealed record OverlayObjectSelectionRequest(OperationId OperationId,
    long ExpectedContextRevision, DisplayGeneration ExpectedGeneration,
    OverlayObjectRef? Target, bool FocusIfAvailable);
public enum OverlayFocusOutcome { NotRequested, Applied, Unavailable }
public sealed record OverlayObjectSelectionReceipt(OverlayObjectRef? Target,
    long ContextRevision, DisplayGeneration Generation,
    OverlayFocusOutcome Focus, PresentationReceipt? Presentation);
```

唯一调用是`session.ApplyAsync(new SelectOverlayObjectCommand(request),ct)`，原Task立即由调用Host保存，内部沿原root的Work/Control/原Submit/Commit/Return登记。预检OperationId非空、ContextRevision/Generation精确为当前值、Read授权和Navigation能力；接纳前及实际呈现前重核。目标必须精确属于当前Sources及Visible且Interactive的Layer：RoiGeometry按Geometry中的ObjectId及Revision精确找**唯一对象**，禁止同层重复ID；SourcePolyline以LayerId同时作该层唯一ObjectId。Label无几何、不可交互，不伪造为可选框；其它产品无几何对象应清除视口选择并由Host在结果表独立选中，不猜一个中心点。未知ID/空白ID/类型结构错002或004，旧源/坐标/几何/ContextRevision/Generation为005，隐藏/不可选层007；预检拒绝不改现选择、不发源读取/呈现/选择成功事件。对象ID仅在Source/Layer/修订的完整复合键内有意义，不以表行号、包围框中心、ZOrder或最近对象代替。

`Target=null`表示清除当前高亮；此时FocusIfAvailable必须false，**不需要伪SourceId/几何**，仍校验expected context/generation和当前Read权限。清除仅撤本选择投影，不移除正常overlay、像素或Host表格事实。重叠/同中心A、B直接按完整键选指定B，不走HitTest；不会得到A+B候选列表或静默选A。直接ID选择不要求IRoiPort，依赖已经验证并冻结的只读Overlay快照；指针精确命中原020路线不变。无几何、不可表示Region或不支持的3D对象不会凭ID获得假框/假聚焦；只读ID入口当前限2D RoiGeometry/SourcePolyline，已支持3D拾取仍按§8。

接纳后至多一次checked递增显示generation，ContextRevision/源/几何revision不变，取消旧手势。Target投影作为`BackendScene.ObjectSelection`，renderer使用原已验证对象路径画既有选择样式，绝不把整个层其它对象一并高亮、不改Geometry/Layer事实。焦点false保持View；true用**冻结几何的既有完整显示投影路径**的源坐标bounds（含全部环/组件，不取Region包围框冒充形状）复用§7.3/7.5导航，保当前旋转/镜像/DPI，按当前canvas每侧8 DIP安全边距使目标居中可见；目标比canvas小可放大，但受既有Zoom域/clamp，ActualView和notices回显。退化点/线以每轴至少8 DIP的显示范围规划，不生成面积或ROI。聚焦是Core可无UI调用的显示计划运算，不读取native窗口取得bounds：Rectangle/RotatedRectangle用原完整四角、Ellipse用原中心与两半轴在当前线性视图下的解析极值，Polygon/Polyline用全部原顶点/环/组件；Region仅有opaque引用而没有原批准完整显示路径时Focus=Unavailable，不从粗包围框制造精确图形。按当前旋转/镜像后的目标boundary范围bw/bh，基础Fit尺度s0取§7.5，目标尺度s=min((CanvasWidth-16)/max(bw,8/s0),(CanvasHeight-16)/max(bh,8/s0))，Custom.Zoom=s/s0；平移令目标范围中点落canvas中心，再用§7.5原整图边界/Zoom范围夹紧，所有中间值有限，canvas任一轴≤16或退化/不可表达时Unavailable。相同纯投影helper由Core计划与renderer共用，不建立第二几何事实/命中引擎。没有完整路径/bounds时Focus=Unavailable，仍可对可表达的对象选择/高亮，保持原View；barcode等要求真实聚焦的调用方必须检查Focus=Applied，不能把Unavailable投影为已聚焦。没有geometry的产品记录不在本入口伪造可选对象。

UI能力已开启时Receipt.Presentation必须是**本次**submission/generation的原Commit值；仅VisibleConfirmed=true且Focus符合调用用途才能说高亮/聚焦已可见。显示失败或晚到不发成功选择事件，清理留原root，旧合法选择若不能恢复则取消高亮并标失败，不悄悄选另一对象；无UI只确认选择投影计划，Presentation=null。结果在`ViewportReceipt.ObjectSelection`，不合成PointerSample/SelectionResult/DistanceDip。成功锁外有序发新增`ObjectSelectionChanged`事件，`ViewportEventArgs.ObjectSelection`携同回执，ScopeKind=Operation、OperationId/输出Generation精确对应；null清除也发事件，重复同OperationId+完整请求返回同原Task且仅一次事件，同ID异内容016。选择事件不合并，订阅者异常按§5.3处理；循环联动Host按OperationId消回声。同OperationId重放在同调用权利仍有效时先查原请求记录，再核是否与原完整输入一致，避免本命令已增代导致自身重放被误判旧代；权利已撤销不重新交付受限旧目标。同源纯View更新可沿相同完整对象键保留选择；层删除/隐藏/失交互、源/几何/坐标修订变化、Clear或撤权立即取消旧选择，内部发Target=null事件（撤权时只给无目标的撤销通知，SourceRevision为空、CoordinateRevision为default，不泄露旧源/对象），不让旧键自动选中新版对象。

### 4.6 源域、叠加、3D描述与后端协议

```csharp
public sealed record SourceStatistics(string SourceRevision, string StatisticsRevision,
    PixelRect Domain, long FiniteValidCount, long InvalidCount,
    double? Minimum, double? Maximum, bool Complete);
public sealed record ValidityDomain(string OwnerId, string Revision,
    PixelRect Boundary, bool FullBoundaryValid, string? MaskAssetRevision);
public sealed record SurfaceValidity(string OwnerId, string Revision,
    long OriginalSampleCount, bool HasInvalidSamples, string? MaskAssetRevision);
public sealed record LodDescriptor(int LodId, long VertexCount, long TriangleCount,
    long MaxRetainedBytes, string SourceMappingRevision, double MaxProjectionErrorSourceUnit);
public enum OverlayKind { RoiGeometry, SourcePolyline, Label }
public sealed record OverlayPayload(OverlayKind Kind, SourceId SourceId,
    CoordinateRevision CoordinateRevision, GeometryRevision GeometryRevision,
    IReadOnlyList<RoiGeometrySnapshot> Geometry,
    IReadOnlyList<SourcePoint2D> Polyline, string LabelResourceKey, int SelectionPriority);
public sealed class ViewportConfigurationException : ArgumentException
{
    public string Field { get; }
    public ViewportConfigurationException(string field, string message) : base(message)
        => Field=field;
}
public enum BackendPolicy { HalconRequired, HalconWithOfflineRasterFallback, OfflineRasterOnly }
public enum BackendKind { HeadlessPlan, Halcon2D, Halcon3D, OfflineRaster2D }
public sealed record BackendCapabilities(BackendKind Kind, long BackendGeneration,
    bool SupportsRotation, bool SupportsMirror, bool SupportsSurfacePick,
    bool HasVisibleConfirmation, bool UsesPersistentBaseline, string Version);
public sealed record BackendCreateRequest(string SessionId, BackendPolicy Policy,
    ViewportLimits Limits, long MaxDisplayBytes);
public interface IViewportBackendFactory
{
    Task<PortResult<IViewportBackend>> CreateAsync(BackendCreateRequest request,
        CallContext call, CancellationToken ct);
}
public sealed record BackendScene(
    long ContextRevision, DisplayGeneration Generation, ViewState View,
    IReadOnlyList<DisplayPlan> ImagePlans, IReadOnlyList<OverlayLayer> Layers,
    IReadOnlyList<IFrameLease> Frames, IReadOnlyList<ISurfaceLease> Surfaces,
    AuthorizationSnapshot Authorization,
    IReadOnlyList<SurfaceOverlayProjection> SurfaceOverlays,
    SurfaceProfileResult? Profile,
    OverlayObjectRef? ObjectSelection = null);
public sealed record BackendSubmissionReceipt(
    string SubmissionId, DisplayGeneration Generation, long BackendGeneration,
    string PresentationId, bool VisibleConfirmed);
public sealed record BackendRevokeRequest(string PresentationId,
    DisplayGeneration Generation, string Reason);
public sealed record BackendRevokeReceipt(string PresentationId,
    bool CallbacksQuiesced, bool ReferencesDetached, ViewportError? Error);
public interface IViewportBackend
{
    BackendCapabilities Capabilities { get; }
    Task<PortResult<BackendSubmissionReceipt>> SubmitAsync(BackendScene scene,
        CallContext call, CancellationToken ct);
    Task<PortResult<BackendRevokeReceipt>> RevokeAsync(BackendRevokeRequest request,
        CallContext call, CancellationToken ct);
    Task<PortResult<CleanupSnapshot>> CloseAsync(CallContext call, CancellationToken ct);
}
public sealed record PresentationRequest(BackendSubmissionReceipt Submission,
    AuthorizationSnapshot ExpectedAuthorization, long ContextRevision);
public sealed record PresentationReceipt(string PresentationId,
    DisplayGeneration Generation, long BackendGeneration, bool VisibleConfirmed);
public interface IPresentationPort
{
    Task<PortResult<PresentationReceipt>> CommitAsync(PresentationRequest request,
        CallContext call, CancellationToken ct);
    Task<PortResult<BackendRevokeReceipt>> RevokeAsync(BackendRevokeRequest request,
        CallContext call, CancellationToken ct);
}
public sealed record RetryPresentationCommand(SourceId SourceId) : ViewportCommand;
public sealed record SetLayersCommand(IReadOnlyList<OverlayLayer> Replacement) : ViewportCommand;
public sealed record PickSurfaceCommand(SurfacePickRequest Request) : ViewportCommand;
public sealed record RequestIntentCommand(ViewportIntent Request) : ViewportCommand;
```

图像源内 Channels 必须与 ChannelCount 一一对应且名称唯一；Validity.Revision 非空且绑定 SourceRevision，FullBoundaryValid=false 必须提供原 Owner MaskAssetRevision。Module 只传播有效域并让 Frame/Probe/Roi 端口验证，不自行解析 mask/Region。LayerId 在单上下文唯一、payload 单项 kind 仅允许对应字段（Geometry/Polyline/LabelResourceKey）非空；源/坐标/几何修订匹配当前来源，不把Label当几何。输入点/矩阵/字节有限且范围检查在任何集合复制/后端请求前。已超过 Limits 的 payload 不边复制边发现越界。未知枚举/版本拒绝，重复 SourceId 允许不同 Role 但相关描述/源修订必须完全一致，Role 在单上下文唯一；同名不同修订不能在同context并存，需宿主提供独立SourceId并明确Reference/Primary，或者新ContextRevision全量替换，不隐藏覆盖。

Surface OriginalSampleCount≥0、LOD Vertex/Triangle≥0、MaxRetainedBytes>0、误差有限≥0且带源单位；空模型 Empty，不申请无意义GPU；LOD 可以无三角但有点云，可导航，拾取遵守源映射。AvailableLods 去重并复制，索引用 LodId，不用数组下标当业务 level。物理标定真假来自007/027已发布资产，不能由显示矩阵推断。3D预算预检按LOD上界+替换并存+baseline，异常容量由root继续留账。

后端主备固定：在线 ProductionDisplay/EvidenceReview 使用 `HalconRequired`，2D/ROI 通过 AsunImage cv2+既有公共显示能力，3D 使用 `disp_object_model_3d`；离线查看/回放可显式 `HalconWithOfflineRasterFallback`，只在 BackendUnavailable/上下文允许软件时转 OfflineRaster2D；OfflineRasterOnly 仅离线，给同样有界Tile计划，不提供3D拾取。权限、非法输入、超预算、源损坏 **不能**触发更宽松备用；未知关闭/未排空后端不能原地重建，先撤销并由root接管旧代，再在根还有独立预算时建新代，不重用旧句柄。无第三方渲染器自动选择，CPU线框仅外部离线诊断源投影，不进生产包。HeadlessPlan 后端仅在无 Presentation feature 的无UI宿主使用，返回Plan/Intent，不发“图像已可见”。

IViewportBackend 持有自己的适配器资源/串行执行上下文，borrow scene 中 frame/surface；lease Owner仍为006/027，不转移事实所有权。Submit成功后会话保留呈现借用，直至 Revoke/Close 原Task确认回调与后端引用均脱离，再调用源ReturnAsync。失败/timeout时仍可在后台持引用，由root继续跟踪，不先Return。提交结果包含代号必须完全一致；Presentation.Commit 是本地显示授权门与实际UI投影确认，不能只返回已排队。VisibleConfirmed=false 可返回有计划的Partial/Busy，不能发PresentationCommitted或度量“已可见”；显示确认由WPF渲染适配器证据，Dispatcher任务完成本身不足。无UI消费者不申请VisibleConfirmed。

#### 4.6.1 root签发reserve→scope/task/context→Start的唯一公开链

Core自身端口仍由会话ledger自动登记。外部WPF DLL只调用下面一条公开链：`root.ReserveExecution(new ExecutionReservation(session,...))` → runtime reservation的Work/Control只读Context → `reservation.Start(bindWorker, cleanupWorker)`。**调用者不提供RootId/SessionId/ScopeId/TaskId/OperationId/CallContext**来取得执行权；这些由创建session的同一个root签发。§3.6的ReserveExecution返回类型同步为以下reservation；旧的传scope/task/context签名删除，不保留平行入口。

```csharp
public enum ExecutionPurpose { UiBinding, BackendAdapter }
public sealed record ExecutionReservation(
    IViewportSession Session, DisplayGeneration ExpectedGeneration,
    ExecutionPurpose Purpose, long MaxRetainedBytes,
    int MaxWorkInnerTasks, int MaxControlInnerTasks, TimeSpan WorkBudget,
    bool CloseSessionAfterCleanup);
public sealed record RootExecutionContext(
    string RootId, string SessionId, string ScopeId,
    ExecutionPurpose Purpose, bool IsControl, CallContext Call);
public sealed record ExecutionObservation(CleanupSnapshot Cleanup,
    ViewportError? OperationError);
public interface IViewportExecutionReservation
{
    IViewportExecutionSlot Work { get; }
    IViewportExecutionSlot Control { get; }
    // Register both workers atomically; start Work once. Control is armed before Work starts.
    Task<ExecutionObservation> Start(
        Func<IViewportExecutionSlot,CancellationToken,Task<ExecutionObservation>> work,
        Func<IViewportExecutionSlot,CancellationToken,Task<ExecutionObservation>> cleanup);
    Task<ExecutionObservation> RequestCleanup(); // nonblocking; returns SAME Control.WorkerTask
    void AbortBeforeStart(string reason); // whole reservation, only before Start
}
public interface IViewportExecutionSlot
{
    RootExecutionContext Context { get; } // root-issued immutable diagnostic snapshot
    Task<ExecutionObservation>? WorkerTask { get; } // original ROOT-owned slot lifecycle task; null before start
    IReadOnlyList<Task> OriginalTasks { get; } // raw child tasks; immutable snapshot, not WaitAsync wrappers
    // Root prechecks & creates child identity/context before invoking startWork ONCE.
    Task StartOriginal(DisplayGeneration expectedGeneration,
        Func<CallContext,CancellationToken,Task> startWork);
    Task<T> StartOriginal<T>(DisplayGeneration expectedGeneration,
        Func<CallContext,CancellationToken,Task<T>> startWork,
        Func<T,IReadOnlyList<IViewportLease>> extractLeases);
    void RetainLease(IViewportLease lease);
    Task<ExecutionObservation> ObserveAsync(TimeSpan waitBudget, CancellationToken ct);
}
```

**签发与身份。** root验证Session为本root.CreateFactory().Create返回的同一runtime实例（reference身份+内部不可变nonce），不是仅比较SessionId文字；同名session/RootId、另root的session、用户自实现IViewportSession都Rejected，不调用委托。ExpectedGeneration等于会话当前快照，Purpose为定义值；capacity/budget预检通过后原子签发一个Work scope和一个独立Control scope、两个OperationId/TaskId及所有inner/return额度，`1+MaxWorkInnerTasks` 与 `1+MaxControlInnerTasks` 都计根预算。MaxWork/ControlInnerTasks是同时仍需强持的child槽上限（完成且所有借用已真实归还才回收，不是无限历史列表；scope内保存的已完成诊断不含Task且受MaxQueuedEvents限制）；MaxWork/ControlInnerTasks≥1、MaxRetainedBytes≥0（零只允许无资源UI安装）、WorkBudget `[50ms,10min]`；剩余额度不足拒绝，零副作用。ScopeId是本root生成且绑定该session/runtime reservation，Context只读属性给端口调用/诊断，不是可复制的执行capability。root不接受调用者传Context；复制record、更改RootId或Call字段、调用别root的slot都不能获得新槽/许可。工作与控制共用一份lease台账，不对同一borrow重复计费。CloseSessionAfterCleanup只允许UiBinding；root在Reserve时为true原子预留session固有close-controller额度，一个session最多一个OwnSession binding，false不授关闭其它session权。Start成功时同时armed该一次性controller，失败/AbortBeforeStart不关session；session关闭之后不能追加新的OwnSession binding。

**Created/绑定代。** session.Create的初始Generation=0、State=Created，允许Purpose=UiBinding在这一代预留并安装空控件/订阅，Context.Call.AuthorizationRevision为空；此时不能读取帧、创建呈现、申请probe/pick或绕过Attach授权。Attach按§4.7成功接纳后从0递增为1；binding lifetime scope保持其root身份，不用伪造新scope。Work.StartOriginal每次要求调用者提供当时`session.GetSnapshot().Generation`作为期望值，root在调用delegate前原子复核**当前**generation/状态/授权并签发child的CallContext（新TaskId，沿本scope OperationId，剩余单调预算）；接口只给delegate root-issued child context，不能用slot初始Generation=0的Context.Call交付后续像素。旧generationRejected(StaleGeneration)，delegate未调用、DispatcherOperation未创建。Created态仅允许无资源安装Task；资源型提取器在Attach前拒绝。Control允许清理它所辖既有旧代借用，禁止取得新帧/普通非空呈现/设备动作，child context带其实际清理代且授权空值不构成读取权。唯一无源呈现例外为§4.7.1的可信Empty Update：同root内部核已接纳空更新关联后，沿本binding的Control.StartOriginal(emptyGeneration,delegate,extractLeases)登记空Submit/Acquire/Confirm/Dispatcher原Task，原清理额度及同一单调deadline不重置；新空Presenter无旧payload借用且仍由extractor强持。它不调用binding.RequestCleanup导致Unbind，不等本Control worker或session关闭，不打开普通Work门；Unbind已封门则拒绝并沿原关闭清理。

**启动和关门。** Start先验证两个worker非null，再将work/cleanup委托先原子存进root再启动Work，返回root创建的**原slot生命周期WorkerTask**；此Task表示slot执行/启动本身，不是ObserveAsync/WaitAsync投影。root在调用委托时另保存其返回的原callback Task，及每个StartOriginal原Task/租约，包装生命周期不能替代或丢弃这些内层原Task。Start前再次核验root/session接纳门及ExpectedGeneration，Reserve后到Start前发生关闭或换代则拒绝不启动委托，释放明确未Started的reservation预留。UI Created可无资源Start；对于已经关闭的根不能新Reserve来伪造cleanup，只有先前已armed的Control可启动。同reservation第二次Start拒绝，不重执行；AbortBeforeStart只在整个reservation未Start时可用，Started永不撤销为未开始。WorkBudget作用于Work安装worker；安装完成后绑定scope可跨后续generation存活，后续Work child每次从session.OperationTimeout获得新的有限操作预算，而不重置同一child deadline。Control的独立清理token/每次预算取RootOptions.CleanupAttemptBudget，不链接Bind/用户操作/窗口取消；Bind启动时已预留并**armed**，所以根或session关闭/Unbind即使接纳门已关仍可RequestCleanup，root也会启动同一个已注册Control worker。关闭不自动丢弃这一未Start Control槽；只有其从未armed且reservation从未Start时才可撤预留。

未Start调用RequestCleanup抛ViewportConfigurationException(Field=start)，没有委托/资源；未Start的清理只需AbortBeforeStart。Start成功后RequestCleanup首先同步关此binding的Work新child门，并立即返回已创建的同一Control.WorkerTask，不同步等待UI/当前factory回调。root-owned Control启动worker在后台等待已被接纳的StartOriginal同步factory登记动作完成，之后才调用cleanup委托；原启动Task/原cleanup委托Task都强持，因此Control读取Work.OriginalTasks不会遗漏已被接纳而尚未登记的原Task（回调禁止同步阻塞；违约卡住时Control启动本身Pending且根强持，不强杀/漏掉资源）。Control只启动一次；root/session.Close也执行相同的门关闭/触发操作，返回相同Control.WorkerTask，不额外创建一条竞争清理链。already-started Work/Dispatcher/Acquire/Presenter/Return仍由root强持；迟到结果提取并Retain/归还，不以外层WaitAsync或worker失败丢掉。Root/Session关闭**不得**直接把Started Work标Drained/Abort；有限等候仍Pending/Unknown，责任接管另记OwnerAccepted。

**原Task和借用。** StartOriginal先预检inner额度/期望代/门，失败同步抛ViewportConfigurationException（Field为scope/capacity/generation），委托不调用、不产生新原Task或资源；Start预检失败同样抛该配置异常且Reservation仍未Started，可AbortBeforeStart。通过后由root调用startWork一次、保存并直接返回其原Task；非泛型重载可直接返回`Dispatcher.InvokeAsync(action).Task`，不能返回async wrapper/等候投影Task替代。泛型extractLeases必填纯无IO函数，非资源Task返回空列表；即使PortResult失败Value含lease也收住；extractor异常保留原结果并隔离为Unknown，不能先退容量丢资源。同LeaseId重登记幂等，binding acquired lease转Control责任是同台账逻辑交接，不转资源Owner、不退款。借用最终由其原Owner.ReturnAsync确认，root根据已登记原Task及lease回执判定真实scope终态，不相信worker给出的CleanupState字符串。Control的ObserveAsync终态覆盖本Control worker/children及它清理的Work原children/Presenter borrow，检查台账而不调用Work.ObserveAsync，不等待Unbind观察Task或slot外Session.Close，根不把这些observer反登记成本scope工作。若worker或原child仍挂起/故障后借用未确认，返回Pending/Unknown；completed-slot的空pending提示不覆盖原Task台账。Control中Return/QueryReturn也通过StartOriginal存原Task，超时原Return不再重发；必要Query同ReturnId，有限尝试耗尽根仍强持Unknown。

**避免自等待。** Work.WorkerTask是“安装/当前动作委托执行完”的Task，可能返回Cleanup.Pending，因为Presenter仍保留；Work.ObserveAsync等待worker+其所有child/borrow真实退出，是不同对象。Control可await Work.WorkerTask以确认root安装worker及其原callback Task退出，**不得await Work.ObserveAsync**（后者会等Control负责归还的Presenter）。Control只做关闭binding门、解除订阅/capture/视觉引用、等已启动children、revoke和实际borrow归还；不能在Control或任何本scope worker内await session.DisposeAsync、root.CloseAsync、自己的ObserveAsync/WorkerTask。OwnSession=true的Unbind在Control原Task退出且Control.ObserveAsync确认本UI scope收敛之后，从**所有slot外**调用session.DisposeAsync；RootClose同样由slot外宿主调用。Session/Root关闭器可在外部等待Control，Control不反向等关闭器；各scope保持有向等待关系`外层关闭器→Control→Work原worker/children→原资源Return`，不存在反向边。root终态最后包含Control worker本身退出，worker不能提前签发自己的Drained。CloseSessionAfterCleanup对应controller等待Control真实收敛后调用同一个session.Dispose关闭过程，但此controller/Dispose的调用等候Task是关闭协调者，不作为该session需排空的资源worker计入（否则session会等自己的关闭者）；其原Task仍在root的独立controller表强持。Root.Close的自身观察Task同样不计入资源排空集合；它在资源/Control及session关闭回执后才能完成，controller表与resource-worker表不得混算，未知回执仍非Drained。

#### 4.6.2 端口/配置预检的补充断言

PixelLayout的Width/Height/ChannelCount为正，Kind决定bytes/sample（1/2/2/4/8），Interleaved=true时stride≥width×channels×sampleBytes，false时stride≥width×sampleBytes且容量包括所有channel planes。checked计算stride×height×planeCount≤Identity.RetainedBytes≤请求/根预留上界，源Identity/Revision与请求匹配；stride负/溢出/大小不符ProtocolFailure，不交付像素并保留归还责任。位图负stride/未知packed格式不猜布局，由frame adapter显式转为已支持格式且物理副本准入，否则CapabilityUnavailable。Snapshot.State只是投影，不能由host设置Ready绕过权限。

SourceStatistics的min/max/finite计数与SourceRevision一致，计数非负且finite+invalid不越统计域已知采样数；Complete且FiniteValidCount>0要求有限min≤max，=0允许null；Incomplete不能触发自动窗；MaskAssetRevision及ValidityDomain由源Owner证明，Core不把缺统计当0。SourceTiming.Uncertainty非负、TimeBasisId/AcquisitionId非空；多源要求“同期”由采集/宿主Owner已经归集，Viewport只展示CorrelationId/时间，不按UTC或到达顺序自做同步判定。

Camera.DefaultLodId存在，MaxProjectedLodErrorPixels若提供有限>0且在host采纳Profile中；SurfaceHit NoHit/Invalid/NoMapping不得有原值。OriginalSample贡献必须一个weight=1，Interpolated贡献非空权重有限非负/总和1（误差≤1e-12仅数值保护），源索引由027发布，Ambiguous用候选列表而不是一个猜值；屏幕深度-1不作真实负高度。全量Layer/Source/Geometry/候选/样本/事件payload在Limits预检，注入owner返回越界结果也只走隔离/清理不当作成功。

UpdateThrottle=null时不创建隐式节流等待；已采纳host Profile传有限0..250ms时仅合并显示刷新到最新，不丢选择/候选/撤权/终结。UiBindingOptions.HandleSizeDip/LineWidthDip遵守§4.4显示域，非法先拒绝Bind不clamp。Resources/Language可扩展；ctx语言输入为空拒绝，UI资源缺所需键拒绝本次绑定/切换保持旧合法内容，不回退内部英语异常堆栈。

### 4.7 接入、全量更新和受保护意图的步骤

1. Create 先验证 Root/Options/Limits/能力组合和全部有限预算；本身无资源动作。Attach唯一一次，先预检ApiVersion(0.1)、ContextRevision≥0、语言资源、所有来源/图层/有效域及容量，后检查权限（Read）；空 Sources 合法但仍校验上下文/权限，不取得源租约。合法空附着→Empty→可Update，失败/取消Attach仅可关闭，不能重用。
2. Update只接受全量Replacement，BaseContextRevision必须等于当前，Replacement.ContextRevision=base+1且无溢出；来源、overlay、授权和关联作为一个不可变快照原子接纳。拒绝保持当前合法快照不创建资源；接纳换身份/权限时先撤旧交互/呈现再取得新源。同源参数更新可保留授权仍有效的旧图并标Updating，不允许旧matrix响应新参数指针。没有patch自动补合/乱序重排，不接受丢失base的增量。
3. 生成内部OperationId及TaskId，预留根槽/bytes后发OperationAccepted；取得剩余预算授权、frame/surface、backend、presentation，逐次验证响应Owner/身份/修订/实际bytes。成功receipt列每来源，不完整层明确Partial，操作结果不能把未知源作成功。保护性用户命令的OperationId/源修订/generation必须匹配封存快照；旧命令StaleGeneration。SetView/SetLayers/Retry从接纳点生成新generation，不静默原地变更现有计划。
4. 只读HitTest可注入IRoiPort但不授编辑；配置无Roi则只可选择有稳定几何的source polyline/不可交互label，几何精确命中需020端口，缺失返回CapabilityUnavailable，不自写几何引擎。编辑开始冻结源/几何/坐标/授权及capture；按源坐标增量更新同类型预览，Region/洞岛由020提出完整typed geometry，Viewport不重建拓扑。EndGesture先ValidateDraft再CreateCommitCandidate，当前权限/修订再核一次，发IntentReady或sink.Accept；sink未知只保留原Task，不能重复提交候选或宣称保存完成。
5. 量测请求携源点/证据坐标交030/宿主IntentSink，export为宿主Owner处理的ExportRequest，明确Export权；Viewport不写文件或生成生产证据。IntentSink返回的是接收ID，不是测量值/PASS/放行。没有sink时只发有界typed IntentReady供宿主消费（永不缓存无限队列）；宿主接收ack不是模块自增业务状态。
6. 撤权事件在会话接纳门内串行更新授权修订、取消受保护手势、撤销受限显示；再入Dispatcher前核验，迟到源/探针/意图不给用户。源断连/后台异常归SourceUnavailable/BackendFailure，保留同身份仍授权的旧图并标过期禁命中，或清屏；不在每次PointerMove无限重连。RetryPresentation仅在原Task/资源策略允许且新操作预算/权限有效时一次请求，重试次数及退避由宿主Profile明确。

#### 4.7.1 合法空更新、真实清屏与同session继续呈现（BC-U3）

原`AttachAsync`仍只允许一次。已有合法Empty Attach及§21“空后Update”的路线保持；本节明确`UpdateAsync`的空Sources全量替换也合法，作为**保持接纳的Clear**，不调用Unbind/Dispose后复活session。没有新增IViewportSession.ClearAsync或第二Close Owner。调用形状：

```csharp
// Existing signatures; empty arrays are typed and immutable at the boundary.
var replacement = new ViewportContext(Array.Empty<SourceBinding>(),
    Array.Empty<OverlayLayer>(), currentAuthorization, currentLanguage,
    new ApiVersion(0,1), checked(baseRevision+1), currentView with { Profile = null });
Task<ViewportResult<UpdateReceipt>> originalClear = session.UpdateAsync(
    new ViewportUpdate(baseRevision,replacement),ct);
// Result/query additions, in Asun.UI.Viewports:
public sealed record EmptyTransitionReceipt(OperationId OperationId,
    long ContextRevision, DisplayGeneration Generation,
    bool PreviousPresentationsRevoked, bool PreviousSourceBorrowsReturned,
    bool PreviousWorkQuiesced, PresentationReceipt? BlankPresentation,
    CleanupSnapshot PreviousCleanup);
```

§3.5的UpdateReceipt及ViewportSnapshot尾部可选EmptyTransition均为本次已接纳空更新的同一不可变观察值；GetSnapshot只观察，不重新启动Clear，开始下一非空更新时该当前字段置null，调用方核ContextRevision/generation，不拿历史Clear证据证明新图已清除。三个Previous布尔分别指**此session空更新之前**的所有presentation/backend/presenter、frame/surface/ROI借用及其工作/Dispatcher回调，不能用新Empty状态或待办数0推断。PreviousWorkQuiesced不等待本次Clear自己的Task、长寿命UI binding Work/Control worker或整个session/root关闭，避免自等；只核被撤旧代的有限内容scope。PreviousCleanup只核这些旧scope，Drained不代表session/UI基线或共享源storage关闭。空场景自己的有限任务/基线仍按原root留账，外部源服务/其它session不关闭。

1. 预检base与new ContextRevision、语言/版本/正canvas等原Context规则；空Sources要求Layers也空，InitialView只保存有限导航偏好，不保旧Profile结果/SurfaceOverlays或选中对象。重复同base/newRevision+完整replacement只观察同一个原Update Task；内容冲突016、其它旧base005。拒绝无新generation/资源。仅初次Attach合法Empty不创建源lease的旧规则不变，不将InstallEmpty当实际可见证据。
2. 成功接纳空更新时checked递增generation一次并采用new ContextRevision，State=Updating；封当前旧代交互、取消手势与选择、停止旧代新读取/预取/提交，旧晚到只归还。Clear属于撤除本方已拥有显示的安全控制操作：即使当前Read已撤/过期也允许此**仅删除**输入进入原Control清理，不能顺便换授权获得新读权；此时replacement.Authorization必须逐字段等于session当前撤权快照，Language及View保持原已接受值（Profile清为null），异内容002/008拒绝。第一次正常空更新仍保存明确授权快照；撤权/到期用原已armed Revoke权限收尾，不调用受保护Apply来重新获取源。
3. 逐项对旧PresentationId按原Owner发原`IPresentationPort.RevokeAsync`与backend.Revoke，沿原binding内部Lifetime.Revoke→Presenter Return/Query；等各原Submit/Acquire/Confirm/Dispatcher/CPU scope真实退出后，原Frame/Surface借用同ReturnId归还。失败/取消/晚到Value含lease也算旧scope。只有旧实际回执全部匹配才三个Previous=true；不能在外层Clear与Unbind各Return一遍，不为Clear关闭renderer baseline/源服务。
4. 已装配Presentation时，提交同新ContextRevision/generation的**空BackendScene**（ImagePlans/Layers/Frames/Surfaces/SurfaceOverlays皆空、Profile/ObjectSelection=null），不Acquire任何源。内置backend清除本控件全部旧像素/标题/叠加/原源引用，绘制当前资源下的中性Empty图面；同root原Submit→binding.Commit→Lifetime Acquire/Confirm走§10.6～8。空submission是可识别的真实类型分支，Acquire不索取第一张frame，renderer不能以Frames.Count=0为由沿用旧图。清空/遮罩是撤除操作，binding/backend仅对此可信空submission允许原Control授权清理，不需要重新取得已撤销的Read；任何非空scene仍走原严格授权。源授权不得伪造或延长，清屏确认不得返回旧图内容。
5. BlankPresentation只能取同新代空scene实际确认值；实际client读回/正常Empty图面完整匹配沿§10.8，属性赋null、Unloaded、仅Render事件不是确认。空图面Presenter只借当前UI基线/有界metadata，无旧source/overlay/native图像引用；可留至下一次更新的同Owner Revoke/Return，不能把它当仍持有旧image lease，也不宣称整个控件资源为零。内置renderer的空scene不因缺源统计触发LUT或像素上传。无Presentation的无UI路径BlankPresentation=null，仅证明无旧借用，不能签UI已清屏。
6. 仅三个Previous=true且PreviousCleanup=Drained，并在UI路径BlankPresentation.VisibleConfirmed=true时返回Succeeded/UpdateReceipt、State=Empty；无UI满足前三项即可Empty。源列表合法为空，但不能仅据Sources.Count=0判断Cleared。清理未知或空画面未确认返回原错误/TimedOut及Cleanup.Pending/Unknown，State=Draining或RecoverableError，EmptyTransition保实际部分值；**禁止新非空Update/Attach/选择/Retry借此绕过**。调用ct只停止本次空更新的等待/进一步采用，已开始清理用原独立Control预算继续；Cancel/超时后原root仍持全部Task/lease，GetSnapshot可见晚到的同EmptyTransition，若真实清屏/归还最终成立可转Empty。授权撤销导致取消只阻非空发布，不阻安全清屏。有限尝试耗尽仍未知则只能观察同原记录或Dispose关闭，不创建新session/binding逃账。
7. Clear确认后新的Present调用`UpdateAsync(new ViewportUpdate(空contextRevision,完整新Context且revision=空revision+1),ct)`；**不再Attach**、不重Bind，正常接纳再递增generation并重新核当前Read、来源和预算，原空Presenter先按同Owner撤回。新数据可用新SourceRevision注册；旧published key仅在PreviousSourceBorrowsReturned/PreviousWorkQuiesced真实成立后由发布Owner Retire。Retire的StorageReleased/源池退款与本session borrow Return分开；同session自身State仍非Disposed。关闭入口、OwnSession=true和Root生命周期完全保持。

Clear与另一Update并发由session接纳门串行决定：先接纳Clear则另一请求Busy/005且无新读取；先接纳换源则旧base Clear拒绝，Host须拿新的精确snapshot重新发明确Clear，不让清屏请求悄悄清除后来选择的新图。相同空更新重复不增加代次；已经Empty且旧清理确认后的新revision空更新是新的有界操作，不重新归还已Returned资源。空更新不被UpdateThrottle与非空刷新合并，清理/选择/终结事件不丢；原操作与旧presentation scope的Drained/ResourcesReleased按§5.3分别记，最后ResultReady/OperationCompleted只是本次空更新完成，不发SessionDisposed/AdmissionClosed。

## 5. 状态、错误和事件

### 5.1 状态机

```text
Created
  -> Attaching -> Ready
  -> Empty (无可呈现源，但上下文合法)
Ready <-> Updating
Ready -> Stale (源/授权/坐标修订过期)
Ready -> Blocked (能力、权限或契约缺失)
任何运行态 -> RecoverableError
任何运行态 -> Disposing -> Draining -> Drained -> Disposed
```

`Completed` 是一次操作的终态，不是 session 的长期状态。`Stale`、`Blocked`、`PermissionDenied`、`RecoverableError` 必须有可见原因和宿主可执行的恢复动作；不能以空白、禁用按钮或旧结果掩盖。

### 5.2 模块错误码

错误码遵循全局错误目录的模块前缀候选 `VIEWPORT-xxx`；正式登记前不得与全局码重复。

| 错误码 | 语义 | 是否可重试 | 恢复要求 |
|---|---|---|---|
| `VIEWPORT-001 ContractNotFrozen` | 正式字段/签名/线程语义未冻结 | 否 | 阻断实现准入，登记待决项 |
| `VIEWPORT-002 InvalidInput` | null、非有限、非法枚举或结构缺失 | 否 | 修正请求；不得部分执行 |
| `VIEWPORT-003 InputLimitExceeded` | 输入尺寸、层数、tile 或会话显示预算超过硬上限 | 仅在换 Profile 后 | 降低范围或换源；回显上限；不表示宿主准入拒绝 |
| `VIEWPORT-004 SourceUnavailable` | 源不存在、解码失败或租约失效 | 是 | 重新获取合法租约 |
| `VIEWPORT-005 StaleGeneration` | 响应/指针属于旧显示代 | 否 | 丢弃结果并归还资源 |
| `VIEWPORT-006 CoordinateUnavailable` | 缺坐标路径、修订冲突、近奇异或越域 | 否 | 只保留导航或请求宿主补链 |
| `VIEWPORT-007 CapabilityUnavailable` | 2D/3D/拾取/导出能力未装配 | 否 | 显示明确不可用原因 |
| `VIEWPORT-008 PermissionDenied` | 当前用途无读取/标注/导出权限 | 否 | 不交付内容；宿主处理授权 |
| `VIEWPORT-009 Cancelled` | 调用方取消，未声称资源已排空 | 否 | 等待 `Drained` 或读排空回执 |
| `VIEWPORT-010 Timeout` | 到达预算但工作可能仍在 native/GPU | 需策略 | 进入 Draining/RecoverableError，不能强杀未知资源 |
| `VIEWPORT-011 BackendFailure` | AsunImage/HALCON/GPU/渲染后端失败 | 受限 | 记录后端代，保留合法旧视图或降级 |
| `VIEWPORT-012 AuthorizationExpired` | 授权新鲜度失效 | 否 | 撤去不再允许的新内容，记录已见内容 |
| `VIEWPORT-013 ResourceLeakSuspected` | 释放回执/计数不一致 | 否 | 隔离资源、报警、阻断发布 |
| `VIEWPORT-014 ExportNotAttached` | 宿主未注入导出 Owner | 否 | 不在 Viewport 内写文件 |
| `VIEWPORT-015 ResourceAdmissionUnavailable` | Required 准入缺失/拒绝、授权或 scope 已失效，或准入结果未知 | 仅原 Owner 同一 AllocationId 可恢复查询 | 在分配前拒绝；Unknown 留账并按同一 Owner/AllocationId 查询，不绕过或改 ID 重试 |
| `VIEWPORT-016 ResourceAllocationConflict` | permit、Owner、AllocationId、scope、generation、字节数或 backing 身份冲突 | 否 | 隔离 backing 和凭据，保留账目；Owner 对账，禁止二次退款 |

错误结构必须包含 `code`、稳定 `operationId`、源/显示代（若有）、阶段、可重试性、宿主恢复提示键和原始异常的安全摘要。UI 显示通过语言资源键生成，不直接显示异常堆栈。

### 5.3 事件顺序

事件统一带 `OperationId`、`ScopeKind`（Operation/Presentation/Session）、`ScopeId`、`DisplayGeneration`、源/坐标/授权修订、`TimestampUtc`、单实例严格递增的 `Sequence`。操作没有源时修订为空，不伪造 revision。事件不含原像素、凭据或 native 句柄。

| 路径 | 顺序与终态断言 |
|---|---|
| 无资源纯操作 | Accepted → PlanBuilt/ResultReady → OperationCompleted；不虚构 LeaseAcquired/Drained |
| 成功呈现 | Accepted → AuthorizationChecked → SourceLeaseAcquired（若有）→ PlanBuilt → BackendSubmitted → PresentationCommitted → ResultReady → 临时操作 scope 排空/归还 → OperationCompleted |
| 保持显示 | 提交时将仍需显示的租约原子转入 Presentation scope；它们不随 OperationCompleted 归还。转移不新增 backing/计费，receipt 记录 scope 关联；撤代/换源/关闭时才排空该呈现 |
| 失败/取消/超时 | Accepted → Failed/CancelRequested/DeadlineReached → DrainStarted（若有在途）→ Drained → ResourcesReleased → OperationFailed/OperationCancelled/OperationTimedOut；无资源时直接终结，不发空排空事件 |
| 关闭 | AdmissionClosed → PresentationRevoked → Session DrainStarted → Drained → ResourcesReleased → SessionDisposed；重复调用没有第二条终结链 |

`Drained` 事件指该 scope 的执行者/提交回调不再使用其资源；`ResourcesReleased` 指该 scope 的本会话借用已实际归还；接管另发 OwnerTransferAccepted，不能替代资源归还。宿主持久池的物理容量仍可留账，事件绝不代表全宿主物理内存退款。`DisposeReceipt.Drained=true` 是更强的关闭结果：本会话所有 scope 满足上述两条件、已触发最后的SessionDisposed事件并完成投递、封口队列（订阅者卡住为Unknown）；否则返回false+PendingResources。PendingResource 必须列出 owner、scope、allocation/backing（已知时）、generation、阶段、待确认原因及可查询关联。

取消/超时的调用回执允许先返回 `Cancelled/TimedOut`、State=`Draining`；该回执与稍后恰好一次的终结事件分别记录。不能因调用者已离开而丢弃清理任务。换源/撤权先撤销旧呈现交互，再排空旧代；迟到结果只发 `LateResultDiscarded` 并归还自身租约。授权检查和 UI 提交不能原子跨 Owner 执行时，在提交 Dispatcher 回调中再次比较授权修订，撤权通知将同一呈现门关闭；不保证跨进程零延迟撤回已经看见的内容。

事件使用每会话有序投递队列，不持内部锁调用订阅者。订阅者抛异常只进入安全诊断，不改变资源计数/终结状态；回调可排队调用 API，不能同步重入状态迁移。纯显示刷新可合并到最新请求，选择、编辑候选、撤权、错误和终结事件不合并；队列容量由批准 Profile 冻结，未配置时禁止无界后台发布。Core 不触碰 Dispatcher，WPF 回调自行切线程并复核 generation。

## 6. 线程、取消、超时和资源排空

### 6.1 线程模型

- Core 参数验证、矩阵计算、命中排序和状态转换可在线程池执行；不得持有 UI 线程对象。
- 帧解码、Tile 读取、CPU 预处理和 GPU 上传由注入的调度器执行；队列有数量和字节双上限。
- WPF 控件的依赖属性、视觉树、`WriteableBitmap`/后端提交只在 UI 线程执行。
- HALCON/AsunImage 对象的创建、使用、释放线程由适配器根据确认的公共签名和官方线程语义规定；未确认时串行化到适配器专用执行上下文。
- 不使用静态可变“当前窗口/当前帧/当前标定”。

### 6.2 取消和超时

Attach、Update、Apply、Probe 使用 `ViewportOptions.OperationTimeout` 和各调用的 `CancellationToken`；Tile/Probe/Presentation 等端口接收剩余操作预算，Dispose 使用方法参数 timeout（宿主通常传 options 的 DrainTimeout）。预算不得从未定义的请求字段猜测。取消含义是“停止继续交付/尽快停止可中断工作”，不代表底层已停止；回执必须带 `Cancelled` 或 `Timeout` 和排空状态。

操作Task的完成/错误与cleanup worker是两个不同对象：public Attach/Apply/Probe可在有限OperationTimeout返回取消/超时+Cleanup.Pending，根仍存原port/backend/Dispatcher Task和单一drain worker；每次DisposeAsync只创建有限观察等待，共用该drain worker，不因观察Task完成重置次数/预算。cleanup worker的每个步骤以RootOptions.CleanupAttemptBudget独立token执行，CT不链接用户操作/WindowClosed；结果未知继续观察原Task并Query同ReturnId，不无限重发Close/Return。public关闭方法timeout/cancel从接纳起有限等待，失败回执保留root接管ID/原Task及原操作错误，不阻断UI线程。订阅者同步回调若永久阻塞不能强杀：事件投递worker及bounded queue同样由根追踪，有限等待为Unknown/非Drained，不假称事件队列已封口；Disposed后事件不再交付。

实现顺序：

1. 标记操作不再接受新结果。
2. 撤销操作对应显示代/交互手势。
3. 取消尚未开始的解码、上传和预取；共享 single-flight 只移除当前等待者。
4. 对 native/GPU 不可抢占的工作等待真实完成、fence 或适配器回执。
5. 等该 scope 的 native/GPU/渲染调用真实退出，随后在正确线程归还本会话借用；未决物理容量按 §4.4.1 留账/接管，满足 §5.3 条件后依次发 `Drained`、`ResourcesReleased`。取消/超时回执可先返回 State=Draining，真实终结事件只能在此步骤后发送。

超时后不在 UI 线程同步等待、不强制 Dispose 仍在使用的句柄、不把线程终止作为恢复策略。关闭与新增等待者并发时，由资源 Owner 原子决定是否继续共享工作；已进入释放的条目不可重新借用。

### 6.3 资源所有权

| 资源 | Owner | Viewport 权限 | 释放条件 |
|---|---|---|---|
| 原始帧/Tile/Pyramid | `PKG-006` | 持有只读租约 | 本实例最后一个 scope 归还且底层完成 |
| 坐标/几何快照 | 对应 Owner | 不可变引用 | 引用计数或 scope 结束 |
| Overlay 解析对象 | Viewport | 本实例拥有 | 当前显示代撤销且渲染队列无引用 |
| CPU 解码缓冲 | 适配器/Viewport | 预算内租用 | 操作完成/取消并无消费者 |
| GPU 纹理/Buffer | 渲染后端 | 只持有句柄封装 | fence/后端回执确认无引用 |
| UI 位图 | WPF 适配器/宿主持久容量 Owner | UI 线程更新和解除视觉引用 | Dispatcher 回调退出并解除本会话引用；`WriteableBitmap` 没有逐对象 Dispose/fence 证明，不能据此退款，持续容量按 §4.4.1 baseline 管理 |

显示预算至少同时统计 CPU、GPU、在途解码、上传、Tile、Overlay 和 UI 复制。没有可驱逐条目时应降低预取、限制 LOD、排队或拒绝；不得驱逐借用中源或 GPU 仍引用的纹理。

## 7. 2D 显示与坐标实现要求

### 7.1 三种坐标必须分开

1. 源像素中心 `(u,v)`：`u=column`、`v=row`；整数代表像素中心，外边界为 `[-0.5,W-0.5] × [-0.5,H-0.5]`。
2. WPF DIP：布局和输入使用的逻辑单位。
3. 窗口物理像素：由实际 DPI scale 转换，不可把物理像素再次当 DIP。

007 负责源/父图/物理坐标变换；Viewport 只叠加 crop/LOD、旋转/镜像、缩放/平移和 DIP→物理窗口的显示变换。HALCON 的 row/column 和半像素桥只在适配器中转换一次。

### 7.2 必须满足的算例

图像 `W=4000,H=2000`，画布 `1000×600 DIP`，Fit 得 `s=0.25 DIP/源像素`，外边界偏移 `(0,50) DIP`：

```text
pDip = offset + s * (u + 0.5, v + 0.5)
源外边界中心 (1999.5, 999.5) -> (500, 300) DIP
125% DPI -> (625, 375) 窗口物理像素
```

实现必须通过逆矩阵回到同一个源位置；不得重复加 0.5、把 625 当 DIP、用整个客户区代替图像绘图区，或在宽高为零/矩阵不可逆时用旧矩阵命中。

### 7.3 Fit、1:1、缩放和旋转

- `Fit` 保持比例且不切除图像边界；实际偏移和 clamp 写入 receipt。
- `OneToOnePhysicalPixel` 使一个源像素间距对应一个窗口物理像素间距；125% DPI 为 `0.8 DIP/源像素`，不是 1 DIP。
- 滚轮缩放以指针下源点为锚：逆旧矩阵得到源点，调整新平移使其仍映射到相同屏幕点；受边界/倍率限制时返回实际值。
- 镜像和旋转只改变显示矩阵；不得重排 Pin/Target/ROI 身份，不得写回 007 物理变换。
- 标尺从当前有效映射计算；缺标定只显示 px，不能推算 mm。非线性/透视只显示局部适用标尺。
- Viewport 不要求显示图像里包含标定板；它只消费已发布的标定/坐标资产供物理标尺或 2D/3D 联动使用。缺失/未知/越域时仍可浏览和作屏幕/像素导航，但不显示伪造 mm 标尺、不启用物理测量提示；不得用显示变换、拼接接缝或 UI 缩放替代标定资产。

### 7.4 原值、插值、LUT 和 Overlay

探针先检查源身份、维度、有效域、mask、权限和当前显示代。最近原样本候选规则为 `index=floor(centerCoordinate+0.5)`，仅在半开覆盖域内有效；插值必须回显方法、支撑、边界和“插值”标签。不得从 8 位显示纹理反读 16 位/浮点原值，不能因 `get_grayval` 的 reduced-domain 行为省略有效域检查。

LUT、伽马、伪彩、透明度、亮度窗口、平滑和 Z 倍率只影响呈现；量测值、阈值、证据原字节不变。自动灰度窗必须标明统计域（当前视野或全源）和实际数值，不随平移悄悄改变对照含义。未知/遮罩无效区域不得涂成最低高度或合格颜色。

Overlay 命中顺序：按当前呈现代和坐标逆变换 → 过滤可见/可交互图层 → 用稳定几何 ID 和 DIP 容差粗筛 → 精确几何命中 → 对重叠对象按稳定规则排序或给候选列表。不能按结果表行号、绘制顺序或标签文字命中。

### 7.5 Tile/Pyramid 计划、接纳和迟到处理

主路线保持 006 作为源 tile/single-flight/lease 的唯一 Owner，Viewport 仅调度可见需求和显示专有副本，不再建立原源缓存。§3.4 的同步计划按以下固定顺序执行：

1. 使用 crop 的源外边界，以中心为轴先镜像再旋转；旋转规范到 `[-π,π)`，将四角变换得到外包尺寸。Fit scale=`min(CanvasWidth/boundsWidth, CanvasHeight/boundsHeight)`，先居中后加 Pan；Custom 乘相对 Zoom；1:1 在物理像素平面执行等距旋转再用各轴 DPI 逆缩放，DPI 不等轴也不能假定一个 scalar。零画布/不可逆拒绝。小于画布的轴锁定居中；超画布的轴将平移夹在 `[canvasExtent-extent,0]`，避免整图被拖走；clamp 后锚点变化在 receipt 回显。
2. SourceCenterToDip 一次桥接中心→外边界坐标（+0.5）；保存 double 逆矩阵。旋转/镜像均在此组合，不把 `set_part` 的矩形视野当可表示任意旋转的完整矩阵。HALCON 适配器须用同一受控图像/overlay 变换和边界桥接实现旋转镜像；只更新 part 会使命中与显示不一致，该适配器不得宣称支持旋转。固定组合见 §7.7；具体C#类型/封送歧义仅在消费适配切片确认。
3. 将绘图区四角逆映射为源边界坐标，取外包并与 crop 相交；空交集输出空 TileRange。旋转的外包仅是粗需求范围，绘制严格裁剪到真实视口/crop，不填无效外角。由 level→source 的显式变换逆求 level 外边界（level center±0.5），奇数尾部以实际描述裁剪。
4. 计算各 level 的源→物理屏幕复合线性变换，取最大奇异值 `q`（物理屏幕像素/level 像素）。自动选择满足 `q<=1` 的最粗 level；若无满足则用最细 level，不增加不存在的细节。平局按 LevelId 升序。不得从名称推断 level 越大越粗。手动 level 必须存在；预算不足拒绝手动请求，不偷偷换层。
5. 半开可见 level 边界 `[a,b)` 的 tile 列范围为 `[floor(a/T),ceil(b/T))`，裁剪到 `[0,ceil(levelWidth/T))`，行同理；空/越域先处理，右边界恰好等于 tile 边界不多请求一列。tile 交叠/gutter 由 006 lease 描述，计划中的 tileWidth/Height 是非交叠索引网格，不用 gutter 扩张索引。`count×MaxDecodedTileBytes` 是保守接纳上界，不是实际 backing 结算值。
6. count/bytes 超剩余计划预算时，自动模式尝试下一更粗 level（以 q、LevelId 确定次序）并记 BudgetDegraded；仍不满足返回 NoLevelFitsBudget。不先枚举整图再 Take，不把所有坐标 ToHashSet，不分配无界列表。DisplayPlan 只持 TileRange；异步调度以有界窗口惰性取需求，已完成一项才补下一项。
7. 调度顺序为可见 tile→可选预取；可见项按 tile 中心到视口源中心的距离、row、column 稳定排序，预取仅在可见请求已接纳且预算仍有余量时启用。预取上限/队列容量由 Profile 明确提供；没有值则关闭预取。单个 lease 在 acquired→upload→present→return 全程占用在途计数，upload 不能另起不计数队列。
8. 请求键带 SourceId、SourceRevision、CoordinateRevision、level/row/column、decode/pyramid revision、授权访问域；缓存身份不使用 generation 阻止 006 同源共享，但每个等待者携带自身 generation。响应后及 Dispatcher 提交前各复核一次；过期者只归还自己的 lease。换源撤销旧交互，不让旧图配新标题；同源渐进 LOD 可保留合法低分辨率背景并标加载范围，不把它当当前原值证据。

断言（合成定义例）：level `513×257`、tile `256×256` 有 `3×2` 个 tile，末块有效尺寸 `1×1`；边界视野 `[256,512)×[0,256)` 只要 `(col=1,row=0)`。若 level center→source center 为 `u=2*l+0.5`，`l=0` 对应源 `u=0.5`，不能按 `513/原宽` 重估比例。`2,000,000×1,000,000` 在 `1000×600 DIP` 的 Fit scale=0.0005，Zoom=1，必须可规划；不能被旧的绝对 scale 0.01 下限拒绝。`u=1,999,999` 处相差 0.01 的 double 坐标必须仍可区分，禁止 float 中间量吞掉位移。

### 7.6 探针、灰度窗和多候选的固定分支

- OriginalSample 使用 §7.4 的索引并复核半开域、mask、源修订和权限；0、负值、高位深与有限 float 均保留原类型语义。原值在 006 的实际 tile 内使用本地 row/column，不能把两百万全图坐标直接传给普通尺寸 HALCON tile。
- Interpolated 第一条确定路线为 HALCON `get_grayval_interpolated` 的 bilinear；端口不支持或任一四邻支撑越域/无效/非有限则 Unknown（SupportInvalid），不夹边、不补洞、不忽略邻点重新归一化。多通道由端口选择明确通道并读取，不能从显示 RGB 推原通道。方法、4 个源索引/权重、源修订随结果返回；不新增自写插值视觉实现。bicubic 会越出原类型范围，不作为隐式备用。
- 自动 LUT 只采用源 Owner 提供的同一修订、声明统计域的有限有效 min/max。无有效样本：Unknown 图例，不发探针数值；min=max=c：所有有效像素映射中灰，图例“常量 c”，不编造 epsilon 或窄窗；NaN/Inf 排除并标有效计数，若统计域不完整/未加载显示等待。手动窗仍须 min<max。改 LUT 不重解码原值/不改 ROI 事实；自动窗候选冻结后保持不随平移变动，用户确认才应用新建议。
- 命中候选先以当前 Source/Coordinate/GeometryRevision、图层 Visible/Interactive 和 DIP 容差过滤，精确几何命中交 020 几何能力；顺序为当前可见控制点→几何内部→边界容差，再按宿主明确的 SelectionPriority、DIP 距离、StableObjectId 序数排序。无 priority 时为 0；不能使用 ZOrder、结果行号或到达时间改变候选身份。多个候选显示可键盘选择列表，Enter 仅接受当前高亮，Esc 取消，数量上限由 Profile 冻结，超量报告收窄范围，不静默选第一个。
- 标尺对屏幕上具体线段两端逆映射，再经 007 当前有效坐标路径求端点物理间距；各向异性/非线性给出方向和局部区间，不使用全局 mm/px。任一端点越域、缺单位、校准修订变化则隐藏物理标尺并显示 px/原因；不把视觉示例当计量资格。

### 7.7 HALCON显示矩阵与ROI共变换的确定主路线

2D旋转/镜像适配不只用set_part。将Core SourceCenterToDip复合tile→source和DIP→物理屏幕为中心坐标矩阵C，交换column/row（置换矩阵P，HALCON矩阵x=row/y=column）；HALCON affine_trans_image/region/contour_xld使用edge坐标，统一转换为`E=T(+0.5,+0.5)·P·C·P·T(-0.5,-0.5)`，这是同一中心/边界桥接一次的数学描述，不再额外给传入点加半像素。图像通过 `cv2.affine_trans_image`，显示缩小时 interpolation=`constant`（官方抗缩小混叠分支），放大使用bilinear；categorical/mask显示nearest_neighbor，不将插值作原值读取。ROI Region用 `affine_trans_region(...,'nearest_neighbor')`，XLD用`affine_trans_contour_xld`，均消费同E；派生仅用于显示，不改020几何资产。标签/控制柄最后在DIP叠加以保持固定屏幕尺寸。

affine_trans_image忽略输入domain且负坐标在左/上被裁：适配先在有界输出tile临时坐标平面平移至非负，输出上界按变换四角+gutter计算并在分配前准入，AdaptImageSize=true时右/下拓展也必须预检；输出不是整幅巨图。将有效mask/region用同E转换并裁剪，未知区纹理另投影，不能因为变换后全矩形就宣称源domain有效。HALCON window part按实际输出窗口物理边界设置，显示派生瓦片及同变换ROI；返回plan同样的SourceCenterToDip用于Core命中。必要适配C#调用以cv2官方算子顺序翻译，不接裸HOperatorSet。图像/region/XLD都在该后端串行上下文创建、提交、释放并计入临时与持久资源双轴。

验收以§7.2/7.5、90°旋转、双镜像、125%DPI和0.01源坐标差同时核图像/ROI/指针位置；边界一侧只加0.5或重复桥接应被捕捉。单tile有效mask含洞时，不应出现被LUT最低色伪填的测量有效区。超预算不选择另一未经验证算法。未经过真实HALCON图像/ROI回放的Adapter保持后续门，不妨碍Core数学与协议实现。

## 8. 3D、LOD 和 2D/3D 联动

### 8.1 3D 能力分级

| 能力 | 必要条件 | 缺失时行为 |
|---|---|---|
| 旋转/缩放/平移查看 | 合法表面或点云描述 | 进入 `Empty`/`CapabilityUnavailable` |
| 高度颜色/剖面预览 | Z 单位和有效域 | 标相对值或不可用，不显示物理单位 |
| 3D 点选 | 当前视图/投影、可见性命中、LOD→源映射 | 只允许导航，不返回测量值 |
| 2D→3D 联动 | 合格坐标/标定/表面映射和共同对象 | 并排查看并标未匹配 |
| 3D 量测 | 030 端口、源证据、物理标定和有效域 | 发 `MeasurementUnavailable`，不由 Viewport 计算 |

三角形内部命中是表面插值候选，不是原始采样点。体素质心、插值网格或平滑点必须通过贡献关系回源，不能把 LOD index 冒充原索引。拾取射线在显示模型逆变换（含 Z 倍率）后交给 027 的源查询端口；物理 Z 始终从原始源证据或显式插值贡献读取，不能把显示深度除以倍率当原值。透视深度缓冲不是线性物理高度。

### 8.2 三维拾取顺序

```text
核绘图区和显示代
  -> DIP 转后端坐标
  -> 当前相机/投影生成射线或受支持的对象查询
  -> 排除裁剪外、相机后方、w 退化和无效面
  -> 撤销显示 Z 倍率/模型变换
  -> 经 027 原索引或已声明的表面插值关系取源值
```

HALCON `disp_object_model_3d` 的展示相机/空姿态不等于实机标定；对象可见不等于可拾取或可计量。后端不支持可靠拾取时必须降级为只读旋转查看并说明原因，不读取残留深度缓冲。

### 8.2.1 已冻结的拾取 Owner 与降级路线

3D 可见性/原采样或插值贡献查询由注入的 `ISurfacePort.PickAsync`（viewport显示/交互Adapter，消费027源事实）负责，Viewport 传当前相机/显示模型、backend generation、Source/Surface/CoordinateRevision、指针和剩余预算。HALCON 的 `get_disp_object_model_3d_info` 可以作为该后端适配器的当前呈现可见性证据，不能作为物理值或原索引权威；仅在 `disp_object_model_3d` 明确启用相应 `object_index_persistence`/`depth_persistence` 且图/窗口/相机/代号匹配时查询。默认 persistence 为 false，不能读残留缓冲。没有经027公开原索引与本Adapter当前模型映射共同确认的源映射一律 NavigationOnly，不用最近 LOD 顶点猜原点。

HALCON 26.05 `disp_object_model_3d` 官方说明列出 OpenGL 2.1/GLSL1.2 与 framebuffer 扩展要求，缺少时可自动进入 compatibility mode，低显存可降 quality；这是后端能力/效果降级，不是生产资格。Viewport 不修改进程全局 `set_system` 以替别的窗口切换模式；本后端失效时撤销其 generation、排空资源并给 2D/只读查看恢复入口。CPU 线框仅限离线诊断适配器，不在 Core 增加渲染器，不作为生产 3D 拾取备用。模型多面/遮挡只返回当前可见候选；歧义列候选，后方面不能绕过可见性；退化三角/w/裁剪无效返回 Unknown，不填 Z=0。

### 8.3 联动事件

联动事件带来源 Viewport、手势关联、当前显示代和公共对象/物理点；接收方应用一次，回显不得再次广播为新手势。不同焦距/尺度的视图不能直接复制 zoom 值；缺对应点显示未匹配，不用最近相似对象代替。A/B 两源需要分别携带角色、时间、版本、单位、有效域和授权，尺寸/hash 相同不代表坐标相同。

### 8.4 3D导航、显示ROI、多源同步的确定步骤

CameraView3D 三个矩阵恰好16个有限double，row-major存储、列向量计算，WorldToCamera为右手系camera朝向 -Z，Projection把camera视锥映射到x/y/z∈[-1,1]；HALCON相机坐标/姿态由适配器在边界显式转换，不能拿这个矩阵直接充作HALCON CamParam。Near>0、Far>Near、ZMultiplier有限>0；DisplayModel可逆，不包含未知设备姿态。一般矩阵在求逆前归一化，若无法求逆或条件数>1e12拒绝（数值稳定性保护，不是校准公差），齐次除法判据`abs(w)<=1e-12*max(1,abs(x),abs(y),abs(z))`则拒绝。2D axis map仅接受正缩放、零交叉项，DIP逆映射使用double；这些容差只防数值退化，不扩张mask或物理有效域。

```csharp
public enum SurfaceNavigationKind { Orbit, Pan, Dolly, Reset }
public sealed record NavigateSurfaceCommand(SurfaceNavigationKind Kind,
    DipPoint StartDip, DipPoint EndDip, double DollyFactor,
    Point3D Pivot, string ExpectedCameraRevision) : ViewportCommand;
public enum FollowMode { FixedSelection, LatestPublished }
public sealed record FollowSourceCommand(SourceRole Role, FollowMode Mode,
    SourceId? FixedSource) : ViewportCommand;
public sealed record LinkNavigationCommand(ViewportIntent Intent,
    string OriginSessionId, GestureId GestureId) : ViewportCommand;
public sealed record SurfaceOverlayRequest(SourceId SourceId, string SurfaceRevision,
    CoordinateRevision CoordinateRevision, RoiGeometrySnapshot Geometry,
    int MaxProjectionPoints);
public sealed record SurfaceOverlayProjection(SourceId SourceId,
    string SurfaceRevision, GeometryRevision GeometryRevision,
    CoordinateRevision CoordinateRevision, IReadOnlyList<Point3D> Points,
    IReadOnlyList<bool> Valid, bool Closed);
```

Orbit 固定pivot（当前合法选点或源Owner发布包围体中心，不从屏幕深度猜），水平/垂直拖动分别按 `π*deltaX/canvasWidth` / `π*deltaY/canvasHeight` 更新camera yaw/pitch，pitch夹在±89°防极点；Pan在pivot的camera深度平面通过投影逆矩阵求起终射线与平面交点差，不能直接将DIP当mm；DollyFactor有限>0，围pivot缩放camera距离，保证near/far内，越界clamp回显。Reset使用宿主提供的初始展示camera/pivot，不重置校准资产。示例camera无有效pivot/映射只Orbit/Reset，Pan/Pick返回CoordinateUnavailable。指针捕获/拖动每次camera修订使旧pick失效，手势中使用冻结camera起点累积，不能叠加每个PointerMove再漂移。

自动Surface LOD以§15.2.5.1 viewport显示Adapter从027只读块生成并记录的误差界投影到当前视口的最大像素误差排序，目标误差仅来自消费者Profile；没有目标不猜1像素，使用Camera.DefaultLodId所指显示Adapter明确的默认LOD并标TargetPending（必须在AvailableLods中），可选MaxProjectedLodErrorPixels须来自已采纳Profile且有限>0。选择满足误差界与budget的最粗LOD，若没有则拒绝或选择宿主明确允许的NavigationOnly降级，不静默降低量测源。回显实际LodId/源映射修订，LOD切换保留旧borrow直至新呈现确认和旧revoke完成。源映射缺失可显示，不返回原采样索引。

投影误差计算固定使用完整齐次矩阵A=Projection·WorldToCamera·DisplayModel·S，S=diag(1,1,ZMultiplier,1)，输入坐标是源frame原单位；DisplayModel不得再偷偷含一次同ZMultiplier。对本层源几何误差d以及每个Valid原源点q，令(x,y,z,w)=A·(q,1)，δx=d·||A第0行前三列||₂，δy/δz/δw同理。若w区间跨0/退化保护、球投影跨Near/Far或无法证明同一裁剪chart，该层本视口误差记无穷，不能据中心深度近似；LOD0 d=0仍须合法可见投影。否则ex=(δx·|w|+|x|·δw)/(|w|·(|w|-δw))、ey同式，窗口物理像素保守界=√((W·ex/2)²+(H·ey/2)²)，取所有原点最大值。所有乘加/范数有限检查，溢出记无穷并拒该层；计算工作量受本快照N/期限预算，无单点抽样冒充全层界。该界保守，不是生产量测误差；fast点云距离界不能用于声称连续面的覆盖，Mesh仅LOD0。平局按距离更粗优先、再LodId升序；空间条件改变重新算界，不改原点/权重。正常反例：矩阵投影与源Z倍率造成同d在近面比远面更大，不能直接将DistanceSourceUnit乘一个固定mm/px。

显示ROI到3D由§15.2.5.3 viewport显示Adapter组合007坐标映射与027有界高度块生成SurfaceOverlayProjection（当前源/坐标/几何修订、逐点有效性）；随后以DisplayModel/WorldToCamera/Projection投影并裁剪，不把二维多边形硬放Z=0，不补洞。无映射保留2DROI并标3D“未匹配”；跨无效域断线，洞/岛类型与源几何保持，3D交互回020生成candidate，不直接修改表面/计量事实。所选ROI轮廓可以按当前可见性分实线/虚线，但不能把遮挡的后方点作为当前pick；显示高度采样按§15.2.5.3，专业曲面拟合/计量仍由对应027/030事实Owner。

多源图像每个Role独立DisplayPlan/呈现代/Camera，ContextRevision关联快照；同一操作的所有源状态列在receipt，不能用Primary成功覆盖Secondary未知。2D→3D或A→B联动用稳定对象/源点，007映射到目标空间，再使用目标自己的Fit/zoom定位；不直接复制pixel/zoom。LinkNavigationCommand含OriginSessionId+GestureId，接收方根内有界去重（只保留当前/上一generation，容量MaxQueuedCommands），应用后不再广播，缺映射返回NoMapping。FixedSelection只接受FixedSource合法当前role，LatestPublished由宿主最新已发布快照替换，不以到达时间重排；关闭/撤权一源不连带写其它源事实。

### 8.5 高度剖面预览的Owner与公开结果

```csharp
public sealed record SurfaceProfileRequest(SourceId SourceId, string SurfaceRevision,
    CoordinateRevision CoordinateRevision, IReadOnlyList<Point3D> SourcePath,
    int MaxSamples, ProbeMode Mode);
public sealed record SurfaceProfileSample(double PathPosition,
    Point3D? SourcePoint, double? Height, ProbeValidity Validity,
    IReadOnlyList<SurfaceContribution> Support);
public sealed record SurfaceProfileResult(SourceId SourceId, string SurfaceRevision,
    CoordinateRevision CoordinateRevision, LengthUnit PositionUnit,
    ProbeValueUnit HeightUnit, IReadOnlyList<SurfaceProfileSample> Samples,
    string SamplingMethod);
```

ViewKind.Profile必须有ViewState.Profile和ISurfacePort.ReadProfileAsync，SourcePath至少2点、有限、MaxSamples≤Limits.MaxGeometryPoints，源路径/单位由007/027明确绑定；§15.2.5.3的viewport消费Adapter按OriginalSample或bilinear支撑读取原高度并生成预览PathPosition/有效性/贡献，不拟合表面或发布专业计量事实。Viewport控件只投影二维折线预览（与高度源同一revision，未知样本断线、不得连接洞两端）。若SourcePath是二维交互选择，只产生路径意图，先007/027映射后再调用Profile；不能把屏幕距离当物理path mm。无标定PositionUnit=Pixel、HeightUnit=PixelHeight，仅相对查看；物理单位由源Owner判定。ReadProfile失败保留同源授权有效的旧剖面且标过期，不作计量/检测结果；原Task/大数组按root/limits保留与预检。

## 9. ROI 交互和编辑边界

Viewport 只负责画 ROI、命中、手势和提交候选；PKG-020 负责几何校验、拓扑、变换、草稿、撤销、版本和提交差异。

### 9.1 交互规则

1. 开始手势时固定源身份、几何修订、坐标修订和显示代。
2. 拖动中只产生预览，PointerMove 不逐次提交事实。
3. 结束手势时通过 020 的同一校验入口生成 `RoiPatchCandidate`；失败保留原草稿并说明字段/范围。
4. 换源、撤权、坐标失效或代号变化时取消手势，不把半段轨迹拼到新矩阵。
5. 旋转矩形、椭圆、多边形、洞/岛必须按原几何类型回写；不能用轴对齐外包框或首尾重合猜圆环。
6. 只读复判页只能导航/临时探针；编程和独立测量宿主显式提供编辑授权、原坐标绑定和草稿接收端口。

### 9.2 快捷键和文本输入

`Esc` 取消局部手势/浮层；文本框/IME 输入不触发查看器快捷键；删除、撤销、重做、复制、粘贴、图层移动等命令由宿主注入权限和实现。Viewport 不在按键事件中自行保存配方、不领取复判、不发送设备命令。UIA 名称、语言和工具提示来自 `PKG-003` 资源；不把内部错误码直接作为用户文字。

## 10. 可选 WPF/DevExpress UI 契约

### 10.1 UI 只做投影

WPF 控件通过 `ViewportSession` 注入 Context 和命令端口，布局建议为：顶部身份/状态条，中部影像为主区，侧边属性/图层/能力区，底部仅显示当前操作状态和恢复动作。页面不得把控件私有字段映射为产品结果。

DevExpress 25.2.3 只在可选 UI 层使用 Docking、Layout、Grid/TreeList、Command、UIA 和布局保存能力。布局保存只包含面板位置、可见性和合法显示偏好，不保存 Case 权利、token、生产事实、像素值或任意反序列化类型。

### 10.2 八态投影

`Ready / Busy / Empty / Stale / Blocked / RecoverableError / PermissionDenied / Completed` 必须都有标题、状态色、原因和安全下一步。`Busy` 可合并渲染刷新，但不得合并丢弃选择/业务回执；`Stale` 不得继续接受命中；`PermissionDenied` 不得显示缓存中的受限源。

### 10.3 三语和可访问性

默认 `zh-CN`、`zh-TW`、`en-US`，每个可见文字使用资源键；语言切换重新投影标题、状态、SuperTip 和 UIA 文本，不重载源像素或重发导出。按钮使用明确图标和短文本，非显然图标提供 SuperTip。真实 WPF 验收以 1920×1080 屏幕为固定基线，并覆盖该固定视口内的宿主实际 DPI、键盘、IME、UIA、面板折叠和长文本；物理屏幕更大时使用固定 1920×1080 验证视口，并计入任务栏、窗口边框、标题栏和状态栏。不得扩展为其它分辨率矩阵。本文不声称这些已执行。

### 10.4 1920×1080 固定验证视口的 PageContract

控件由宿主占据客户区，不自己创建 Shell 或语言入口。1920×1080 是包含任务栏/非客户区的物理验证视口，先记录真实可用客户区及 DPI，再转换 DIP 布局；不得假定客户区就是 1920×1080 DIP。仅在这一固定视口内验证三语及侧栏折叠，不改变显示设置或扩展分辨率矩阵。

| 区域/角色任务 | 具体控件与显示规则 | 命令、状态及恢复 |
|---|---|---|
| 身份条 | 位于画布外，源角色、稳定对象短名/修订、当前状态；长名称单行省略，完整名可键盘/提示获取；未知身份不展示绿勾 | A→B 切换先撤销 A 交互和身份组合，再提交 B 图+标题；Loading 显示 B 等待，不能给 A 图贴 B 名 |
| 常用命令条 | `BarManager` 管理单行栏；`BarButtonItem` 的 Fit、1:1、重置常驻；`BarCheckItem` 为导航/探针/编辑互斥工具及镜像、图层显示；`BarItem.Command` 绑定 Core 命令 | 不在工具栏放生产放行或文件 IO；授权不足保留短禁用原因。编辑只有模式与当前权限同时允许才出现可用态 |
| 主绘图区 | 双视图时主图占剩余空间，overview 保持完整板+FOV 框；当前 FOV 独立身份/代号，按 §22 跟随/固定，影像不被浮层永久覆盖 | 中键或明确平移工具拖动；滚轮指针锚缩放；框选/编辑工具明确且互斥；载入中保留同源合法背景并标缺 tile 区域 |
| 工程侧栏 | `DockLayoutManager` 的 `LayoutPanel`，默认宽 280 DIP、可收拢；图层/显示/探针结果分组，高级 LUT/LOD 放渐进展开；属性标签允许换行 | 所有参数回显实际值/单位，非法输入在字段旁说明，Enter 应用、Esc 恢复；改参数创建新 request/generation，不原地改快照 |
| 保护主图 | 主绘图区对应 `LayoutPanel` 设置 `AllowClose=false`、`AllowFloat=false`，保持工作区可见；侧栏允许调整，恢复默认布局按钮常驻 | 不把主图关掉后要求操作员找菜单恢复；收拢侧栏保留图层/错误入口 |
| 状态/恢复条 | 单行状态+当前数值/单位，原因可展开；Empty“无图像”、Stale“图像已过期”、Blocked“此功能不可用”、RecoverableError“图像读取失败”，恢复按钮使用“重试”“适应窗口”等具体动词 | 忙时只取消当前等待/操作；关闭排空显示“正在关闭”，超时“资源尚未归还”及宿主诊断入口，不显示“已安全释放” |

视觉规范：使用宿主的已安装 DevExpress 主题/资源，统一 8 DIP 间距与对齐、命令条/身份条约 40/32 DIP、底栏约 28 DIP（布局设计值，非生产时延/精度目标）；影像区低干扰深背景，未知区域有纹理+文字图例。状态不只靠颜色，选择边框与ROI候选使用不同线型，当前工具有文字+选中态。侧栏折叠后命令仍完整可达，长英文不得把安全下一步挤出栏外；避免影像渐变遮罩和装饰动效妨碍精确指针。

输入路由：只有绘图区持焦点且无文本/IME编辑时处理 Space 临时平移、Fit/1:1 快捷键；捕获 pointer 后冻结手势修订。失去 capture、窗口停用、换源、撤权、语言/布局使绘图区变换变化时取消局部预览并归还临时资源，不能悄悄提交。Esc 先关候选浮层再取消手势；Tab 可到每个工具、图层、恢复按钮，Enter/Space 执行所聚焦命令；候选列表使用方向键，不吞掉文本编辑快捷键。

SuperTip 使用 `BarItem.SuperTip` + `SuperTip`/`SuperTipHeaderItem`/`SuperTipItem`，写用途、限制、恢复；例：1:1 的短提示为“1:1 显示 / 一个源像素对应一个屏幕像素”；只读编辑提示为“只读视图 / 在编程工作台编辑”。三语由宿主传入资源/切换通知，不在模块再放语言选择器。UIA Name/HelpText 随语言重投影、Value 返回显示值/单位/Unknown，自动化找稳定 AutomationId，不以翻译文本定位。

Layout 的 Save/Restore 由宿主控制：`DockLayoutManager.SaveLayoutToXml(string)` / `RestoreLayoutFromXml(string)` 仅对宿主自己生成且版本匹配的允许布局执行；输入白名单含面板稳定 ID/位置和可见性，剔除权利、像素、token及产品事实。不能把外部任意 XML 交给 restore；恢复后重新强制主图保护和权限，损坏/旧布局仅恢复默认视觉布局，保留原配置供回退。DevExpress 不负责把布局文件变成业务授权。

### 10.5 已核实的 UI API 依据和限制

2026-10-09 本机官方 XML 文档：`C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/DevExpress.Xpf.Core.v25.2.xml` 与 `DevExpress.Xpf.Docking.v25.2.xml`，对应 DLL 的 FileVersion/ProductVersion 均为 **25.2.3.0**。已实际读取上述类型、`BarItem.Command`、`BarItem.SuperTip`、`BaseLayoutItem.AllowClose/AllowFloat/AllowDock`、DockLayoutManager 的 `SaveLayoutToXml(System.String)`/`RestoreLayoutFromXml(System.String)`；restore 官方摘要明确提示不可信反序列化风险。使用已安装程序集，不下载/替换依赖。

官方网页定位：[DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager)、[BarManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Bars.BarManager)、[SuperTip](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip)。当前 dxdocs 不可调用，网页请求为 HTTP 403；本轮版本依据为实际本机官方 XML 与 DLL 元信息，不冒称在线页面已读。WPF 线程依据：[Microsoft Threading Model](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/advanced/threading-model)（本轮直接读取）：Dispatcher.InvokeAsync 可 await，UI 同步 Task.Wait 会死锁；Core 不依赖 Dispatcher，控件在 Dispatcher 提交前复核代号。API 查阅与版号核对不等于 XAML 已编译、布局/键盘/UIA 已验证。

### 10.6 公开Binding/Unbind与Presenter借用

本轮冻结WPF Assembly Contract v0.2：显式Lifetime、同Control Presentation入口、同binding原任务观测和完整资源Catalog属于UI装配修订；Core Module API0.1、Surface Core0.4/Contribution0.1及已接收生命周期语义不变。当前这些UI声明尚未实现，不能据本文称旧二进制已有新成员；未来发布包须标对应UI版本并定向迁移Bind装配，不能用Core的ApiVersion代替UI包版本。

可选UI命名空间 `Asun.UI.Viewports.Wpf`，初次实现使用单独Windows/WPF能力DLL（目标落点`src/Asun.UI.Viewports.Wpf/Asun.UI.Viewports.Wpf.csproj`、`net10.0-windows`、UseWPF=true，引用既有Core及本机DevExpress25.2.3；具体工程仅在后续该UI切片获得代码任务授权后创建，本轮不创建空工程）。不得给现有net10.0 Core加Windows/WPF依赖或为了Smoke引用控件改Core target。WPF验证宿主切片对应`tests/Asun.UI.Viewports.Wpf.Smoke/Asun.UI.Viewports.Wpf.Smoke.csproj`，同样仅待批准后建立真实Host/断言，Core的当前唯一Smoke不变。

```csharp
// In Asun.UI.Viewports.Wpf; WPF types are allowed ONLY in this optional DLL.
public sealed record ViewportUiResources(string Language, string Revision,
    IReadOnlyDictionary<string,string> Text);
public sealed record ViewportUiExecutionBudget(long MaxRetainedBytes,
    int MaxWorkInnerTasks, int MaxControlInnerTasks);
public sealed record ViewportUiBindingOptions(string BindingId, bool OwnSession,
    ViewportUiResources Resources, TimeSpan UiCleanupBudget,
    double HandleSizeDip = 8, double LineWidthDip = 1,
    IViewportUiLifetimePort? Lifetime = null,
    ViewportUiExecutionBudget? ExecutionBudget = null);
public sealed record UiUnbindReceipt(bool Detached, bool Drained,
    bool WaitCancelled, CleanupSnapshot Cleanup, ViewportError? Error);
public interface IViewportUiBinding : IPresentationPort
{
    string BindingId { get; }
    IViewportSession Session { get; }
    Task<PortResult<string>> SetResourcesAsync(ViewportUiResources resources,
        TimeSpan timeout, CancellationToken ct);
    Task<UiUnbindReceipt> UnbindAsync(TimeSpan timeout, CancellationToken ct);
    IReadOnlyList<ViewportUiPresentationTrace> GetPresentations();
}
// Public shape; implementation is later in optional DLL (not compiled in this task).
public interface IViewportControlBinding
{
    IPresentationPort Presentation { get; }
    Task<PortResult<IViewportUiBinding>> BindAsync(IViewportSession session,
        IViewportProcessRoot root, ViewportUiBindingOptions options, CancellationToken ct);
}
public sealed record PresenterLeaseRequest(string BindingId,
    DisplayGeneration Generation, long BackendGeneration, string PresentationId);
public sealed record ViewportPresenterSubmission(PresenterLeaseRequest Request,
    PresentationRequest Presentation, CallContext SourceCall);
// Runtime-only observational snapshots. No task/lease is serialized or transferred.
public sealed record ViewportUiPresentationTrace(
    string BindingId, PresentationRequest Presentation, CallContext SourceCall,
    Task<PortResult<PresentationReceipt>> OriginalCommit,
    Task<PortResult<IViewportPresenterLease>>? OriginalAcquire,
    Task<PortResult<PresentationReceipt>>? OriginalConfirm,
    LeaseIdentity? PresenterIdentity,
    Task<PortResult<BackendRevokeReceipt>>? OriginalRevoke,
    Task<LeaseReturnReceipt>? OriginalReturn, CleanupSnapshot Cleanup);
public interface IViewportPresenterLease : IViewportLease
{
    Task<PortResult<PresentationReceipt>> ConfirmVisibleAsync(
        PresenterLeaseRequest request, CallContext call, CancellationToken ct);
}
```

公开 `ViewportControl : System.Windows.Controls.Control, IViewportControlBinding` 有无参构造，BindAsync按上面接口为实际控件实例成员，参数先无IO预检，再按§4.6.1一次ReserveExecution原子签发Work+Control；Start注册清理委托后才创建Dispatcher原Task；一个控件最多一个绑定，重复同BindingId+同session幂等，冲突拒绝，不隐式关闭旧绑定。成功绑定返回runtime `IViewportUiBinding`，控件禁止从全局容器找session。OwnSession=false时Unbind只撤UI交互/呈现borrow/事件订阅，不关闭别人session；true时在Control原Task和UI scope完成之后，于slot外调用同一Session.Dispose原Task（§4.6.1防自等待）。控件constructor不发起资源工作；Unloaded只发起请求，不证明Unbind完成，root持有PresenterLease、原DispatcherOperation.Task（不是InvokeAsync wrapper等待）与renderer borrow直至quiesced/return。

PresenterLease是WPF Adapter持有的本地UI借用，绑定identity指同一root/session/generation/backend。Commit保留对应presenter lease并记录实际可见确认；Unbind先设binding门关闭→解除事件订阅→取消手势→撤回图/标题/overlay引用→等待所有已排队Dispatcher/渲染回调退出→归还presenter→按OwnSession关闭session。Dispatcher关闭/抛异常，图像仍可能被native/backend引用时，Detached或Wait取消不可当Drained；记录UiCleanupUnknown并交root确认接管，保留Task及临时强引用。无法确认显示只能回Busy/VisibleConfirmed=false，WPF属性赋值不证明屏幕可见。没有UI的host绝不初始化这个控件。

SetResources预检语言、所有需要键及字符串长度，资源是宿主完整快照，缺键Rejected保持原资源；完整必需键、内置三语快照公开入口及动态标签规则唯一见§10.9。成功仅重新投影文本/format，不取像素或改变业务revision；重布局可能改变画布时取消在途手势并以新view计划刷新。切换到未知culture可用宿主注册资源，不硬编码“三种之外拒绝”。UIA AutomationId固定：Viewport.Canvas、Viewport.Fit、Viewport.OneToOne、Viewport.Reset、Viewport.Layers、Viewport.Recovery，§10.9同名键给Name，HelpText复用对应Tip/错误原因键，不从AutomationId猜其它文字。

**F2D-UP-UI-01公开装配闭合。** `ViewportControl`无参构造保持；`IViewportControlBinding.Presentation`是该实际控件实例的稳定、无资源`IPresentationPort`转发器，constructor不找服务。Host在Create session前即可取得它，传给`ViewportOptions.Presentation`，或者由同Host端口对象的Commit/Revoke直接`return control.Presentation.CommitAsync(request,call,ct)`/`RevokeAsync`（不使用async包装替换返回Task）。Bind成功后转发到返回的**同一个**`IViewportUiBinding : IPresentationPort`；Bind前或接纳门关闭后Commit返回007/005且不Acquire，不隐式Bind。Revoke是已接纳呈现的清理入口，关门/撤权后仍可观察同一原记录，不要求仍有Read权限。新Bind不能接收旧submission；旧binding的未决清理仍由原root保留。

`ViewportUiBindingOptions.Lifetime`必须显式传实际`IViewportUiLifetimePort`实例；null在Reserve/Dispatcher之前以007拒绝，绝不选择隐藏全局renderer。原6参数构造在源码形状上仍可表达，但真实UI必须补此参数，属于本次明确的装配行为修订，不改变Core API0.1/OwnSession/Root/Close语义。模块HALCON/离线Raster实现见§10.8；features的私有`FixtureViewportPorts`已实现本接口，传`Lifetime: vp`即可，不另造其Root。Bind将该引用冻结为本binding私有`ui`；一实例不能同时给两个控件/binding安装，串行复用须等原Unbind/Return真实完成。Lifetime为Host借用服务，Unbind仅撤销本binding的呈现，不Dispose共享Host服务。

binding.Commit在接纳门内核原`PresentationRequest`、root签发`CallContext`、同session当前ContextRevision/generation、backend generation及全部ExpectedAuthorization字段/期限，调用当前授权port重新确认；不是靠PresentationId非空自认证。Backend仅接受该session登记的原Submit结果，Host端口是该信任边界的实现者，不能拿任意new receipt取得发布权。每项以SubmissionId+PresentationId+generation/backend为键，记录原SourceCall/ContextRevision/授权和原Commit Task；完全相同重复调用返回**同一个原Task实例**，同键异内容016，不再Acquire。不同新呈现可在预算内接纳，旧呈现直到同Owner Revoke→Return确认才退账。输出仅为同binding的PresentationReceipt；实际可见证据不足返回Unknown/TimedOut或Succeeded+VisibleConfirmed=false，不伪造PresentationCommitted。唯一安全删除例外是§4.7.1原session已接纳的可信空submission：同root签发Control关联内部标记其空更新OperationId/ContextRevision/generation、同backend原Submit且零源/层/原值/原标题；Facade可在Read已撤销而binding仍存在时路由它到同空画面清理链。Host不得构造标志、伪造空receipt或以空Sources字符串猜此资格；只有本次空Control可Acquire无源空Presenter，不能打开普通Commit门、刷新授权期限或取任何旧payload。Unbind已关闭的binding不通过此例外复活。

`GetPresentations()`返回已接纳未归还项及有界保留的最新完成项的不可变观测快照，表容量/所有metadata/Task引用计入binding的root预留；达到容量先拒新Commit，不能覆盖未决项。OriginalCommit为公开Commit返回的原Task，其余为StartOriginal捕获的原Acquire/Confirm/Revoke/Return Task；PresenterIdentity仅观察，不把借用lease交Host再Return。root与binding均强持同Task/lease；业务Commit结束不删未决记录。Host可用这份快照关联失败/晚到/Return与root PendingResource，不能用它重新启动原调用。原Task失败/observer到期/清理未知分别保留原错误及Cleanup轴。

ExecutionBudget显式覆盖UI本方Task/metadata/Presenter借用预留，三个值必须正且受root/session已批准额度约束，先核算资源快照和呈现表最坏长度，超限003/015无工作。null固定使用有限软件默认(8388608,8,16)，不是客户性能/生产容量建议；1920×1080双缓冲或更大metadata实际需要更多时，Host必须按完整Profile显式传值，不能在Acquire后自动扩额。§10.7数字为这份默认的合成演示；实际实现从冻结ExecutionBudget取得三个字段，无隐藏常量。保留控制槽不得被work用尽，原pending task/lease占额度直到真实退出/归还。Facade Revoke始终按原PresentationId路由原binding，不能路由“最新”；旧binding未Drained时新Bind拒绝，不能靠重新Bind换Owner逃避Unknown。

Commit输入SourceCall的TaskId/OperationId由同session/root内部已签发调用表核验（纯实现内部关联，不增加宿主可伪造的issuer端口）；当前ExpectedAuthorization必须与原调用及会话当前完整快照相等，不能用新call覆盖原sourceCall丢出处。入口单调记录剩余deadline，Acquire/Confirm的root child预算裁为`min(本child剩余,原Commit剩余)`，不得借长生命周期binding重新给每一步5s；ct/超时停止采用与本等待，不删原Task或中断独立Control。实际Dispatcher提交前再次核原授权期限/修订及绑定gate。Revoke重复同presentation/generation只观察同原清理链，内容冲突016，找不到任何受信原提交记录时Unknown/004而非签空释放。GetPresentations按最新generation/接纳顺序稳定输出；已归还完成项按最老先淘汰，原Task/lease未归还项不淘汰，旧generation提交先005拒绝，不把表驱逐当可重新Acquire的授权。

两个STA Host须使用同一DLL与上述公开绑定：A独立测量工具，显式EditableDraft+020，OwnSession=true；B只读生产复判，Required准入/盲审，OwnSession=false（宿主控制session关闭）。每个STA线程创建自身Dispatcher/Window/Control/root/factory，在固定1920×1080物理视口内串行验证语言、焦点、工具互斥、多候选、capture丢失、A→B迟到/权限撤销、Unbind与Window.Close排序；B关控件不关闭A/共享源。测试保留原Bind/Dispatcher/Unbind/Dispose/RootClose Task，有限外层截止终止测试子进程仅记失败，不声称资源已释放。当前没有这些WPF工程或执行证据。

#### 10.6.1 v0.2兼容分类与消费者窄同步边界

本节只说明上述目标公开面相对旧装配写法的迁移，不新增契约或重开已接收Core。**v0.2不是全部为可选追加。** UI尚未实现，以下是源码形状、实现责任与绑定行为的比较，不是已发布二进制兼容或运行验证结论。

| 公开面 | 兼容分类与必需动作 |
|---|---|
| `ViewportControl()`、`BindAsync(session,root,options,ct)` | 无参构造及四参方法签名保持；构造仍无资源工作。旧调用能表达不等于旧Options可成功绑定 |
| `ViewportUiBindingOptions.Lifetime` | 尾部参数在C#语法上可选，真实Bind中必须显式非null；旧四/六实参构造省略它会在Reserve/Dispatcher前007拒绝。必须传同Control/root的实际lifetime，不另建Root或隐式renderer |
| `ViewportUiBindingOptions.ExecutionBudget` | 真正可选；null使用§10.6有限软件默认。采用实际负载时按原Profile核容量并显式覆盖，不因本字段新增重审Core容量契约。Options记录主构造扩为八参，不承诺旧构造元数据或六输出自动Deconstruct兼容 |
| `IViewportControlBinding.Presentation` | 新增调用入口，Host可直接接到Core Options.Presentation，也可由既有Host端口直接转发原Commit/Revoke Task；自定义接口实现必须补成员，并非只增加可选扩展方法 |
| `IViewportUiBinding : IPresentationPort`、`GetPresentations()` | 新增接口实现责任；模块runtime binding实现Commit/Revoke与有界原任务观测。仅接收返回binding的调用方无需为此另造实现或主动调用观测方法；自定义实现须同步，不能用假binding代替实际返回值 |
| `IViewportUiLifetimePort.AcquirePresenterAsync` | 第一参数由旧`PresenterLeaseRequest`改为`ViewportPresenterSubmission`，不是保留旧签名的备用重载。Host自有lifetime实现须改签名并保留Request、原PresentationRequest与SourceCall；ConfirmVisibleAsync/Return/Revoke签名及原资源Owner不因本项变化 |
| `ViewportUiResourceCatalog`、`ViewportUiResources`校验 | Catalog/Get/RequiredKeys是新增入口；资源记录三参形状保持，但Revision必须为`viewport-ui-text/1`且完整覆盖§10.9必需键及实际Host标签。旧`fixture-text-1`或只七键的快照不能继续Bind/SetResources成功；自定义完整语言包仍可用，不强制调用Catalog |
| `ViewportRendererFactory.Create` | 新增内置renderer构造入口；Host自有backend/lifetime仍可使用，但须满足同Control/root、原submission与资源契约，不强制换实现 |

下表仅依据当前唯一指导中的公开引用定位UI迁移Owner，不代表审核其它模块内容或宣布其已完成验收。features/measurement原会话已获同步，当前正文已包含对应接线；不重复派发。其余尚在全范围文档任务中的UI模块在各自永久原会话局部对齐即可，不以本次兼容说明触发全模块复审。

| 消费模块与唯一位置 | 实际消费与窄同步范围 |
|---|---|
| [features-2d](../features-2d/DEVELOPMENT-GUIDE.md) §7.2/8.7.1/8.8～9/17.1 | 直接Bind、自有FixtureViewportPorts/lifetime及资源；当前已写同Control.Presentation、Lifetime:vp、Submission新签名、Catalog/schema与UI预算，F2D-UP-UI-01已在其正文关闭。本次不再修改或重审该模块 |
| [measurement-workbench](../measurement-workbench/DEVELOPMENT-GUIDE.md) A.7/A.11.5.1 | PublicOwnerUiChildrenFactory直接消费Host传入Control/Session/Root/Options；当前已明确Lifetime、同Control.Presentation、schema与原binding观测。ViewportUiOwner/Mount及OwnSession=false保持；本次不重复同步 |
| [coordinate-geometry](../coordinate-geometry/DEVELOPMENT-GUIDE.md) §11.4.1 | Host的ReadonlyInspectorDisplayAdapter装配实际Viewport；旧四实参Options须补Lifetime，Create session前接同Control.Presentation，资源用完整schema。若Host自实现lifetime须改Acquire参数；Inspector接口及Managed数学/Graph/Core不变 |
| [variation-inspection](../variation-inspection/DEVELOPMENT-GUIDE.md) §8.4.1 | VariationViewportPresenter首次Present直接构造四实参Options并Bind；原会话须在自己的Host/presenter输入中明确Lifetime注入、同Control.Presentation与完整schema，不能让可选null静默通过。只对齐UI装配，不改检测Core/判定 |
| [surface-features-3d](../surface-features-3d/DEVELOPMENT-GUIDE.md) C.2～4 | BorrowedFeatureViewport bridge接受Host的bindingOptions并直接Bind；C.4旧四实参Host示例须补Lifetime/同Control.Presentation/schema，实际Profile核UI容量。Bridge公开绑定形状与OwnSession=false保持，SF-C1/C2不重审 |
| [barcode](../barcode/DEVELOPMENT-GUIDE.md) §8.4影像ImageFactory代理 | 实际影像provider内部首次Present才Bind/Attach；其Host/provider接线须给Lifetime/同Control.Presentation/完整schema，自有lifetime按新Acquire签名。BarcodeImage窄桥、decoder/Core与OwnSession=true保持 |
| [reconstruction-3d](../reconstruction-3d/DEVELOPMENT-GUIDE.md) §10.4 | 实际Host Bridge负责Bind并持binding/root/Task；该Host装配须给Lifetime/同Control.Presentation/schema。模块自己的显示Bridge无需因新增观测入口改公开签名，重建Core及原表面结果不重审 |
| [alignment-2d](../alignment-2d/DEVELOPMENT-GUIDE.md) §10.3A | AlignmentViewportBinding接收已绑定Control/UiBinding/Resources，不自造Options或lifetime；Host预绑定前置条件及SetResources完整schema需局部同步。Bridge原字段/方法保持，自定义lifetime迁移在Host，不要求算法/模型Core重审 |
| [mosaic](../mosaic/DEVELOPMENT-GUIDE.md) D.5 | MosaicControl接收已绑定UIElement与IMosaicUiDisplayPort；上游Host预绑定装配按本节迁移即可，不向Mosaic窄桥塞入新Lifetime参数。原显示复制/呈现回执/归还与拼图Core保持 |
| [ai-dataset-governance](../ai-dataset-governance/DEVELOPMENT-GUIDE.md) §8.2.1～2 | 当前使用自己的受控只读预览桥，引用Viewport Core来源/租约语义，未直接消费本WPF类型或Bind。无需改本模块桥接口；未来生产Host若实际采用Viewport，只迁移该Host的上游装配 |

上述模块中的无UI/Core切片、仅消费`IViewportSession/IFramePort/ISurfacePort`等Core契约的路径不受本次UI版本影响；Core API0.1、Session/Root/OwnSession/Close及原事实Owner不变。[metrology](../metrology/DEVELOPMENT-GUIDE.md) §20.6的公开边界为无UI服务/Reader/请求/结果/Trace/建议Provider，不消费本WPF装配，无需同步或重审。不能因模块名称出现在UI表中而重开其Core，也不能把使用自有预览桥等同于已消费本控件。

本次定向检索在`src`/`tests`的C#/XAML中未发现上述WPF公开符号引用；它只限定本仓库可见调用面，不证明外部消费者不存在或已有二进制兼容。迁移内容由各消费者永久原会话维护，本指导只保留本UI契约的兼容边界；不修改其它模块或另建兼容报告，不重跑旧Golden/C5、渲染、三语或Root/Close全审。

### 10.7 Bind/Dispatcher/Presenter/Unbind的精确公开接线伪码

本例是§10.6控件/Binding的实施伪码，**不是已编译/运行证据**。Core公开DTO/调用如下注明；`dispatcher`为这个控件所属WPF Dispatcher，UI adapter提供下面唯一公开生命周期端口（同可选WPF DLL，实际renderer是原Presenter lease的Owner，非另一Root/authority）。端口task由同root-slot登记。安装/清屏方法是adapter的无IO UI动作；所有backend/Presenter引用实际退出后才确认lease.Return，Dispatcher完成不冒充GPU完成。本伪码演示普通非空呈现；§4.7.1/10.6补充的可信空Control分支在同原Commit实现内单独核签发关联，禁止把下例普通Read预检直接套到撤权清屏而死锁，也禁止省略普通呈现授权。

```csharp
public interface IViewportUiLifetimePort
{
    void InstallEmpty(string bindingId); // Dispatcher-only; no frame/presenter acquisition
    void RemoveSubscriptionsAndVisuals(string bindingId); // Dispatcher-only; revoke input/capture
    Task<PortResult<IViewportPresenterLease>> AcquirePresenterAsync(
        ViewportPresenterSubmission submission, CallContext call, CancellationToken ct);
    Task<PortResult<BackendRevokeReceipt>> RevokePresenterAsync(
        BackendRevokeRequest request, CallContext call, CancellationToken ct);
}
```

下列`session`/`root`为公开factory返回对象，`options`为`new ViewportUiBindingOptions("binding-A", true, resources, TimeSpan.FromSeconds(2), Lifetime: hostLifetime)`；hostLifetime为Host显式构造的§10.8实现或其有限CPU fixture，resources从§10.9公开Catalog取得。预检成功后唯一`ui=options.Lifetime!`，不再存在未绑定ui变量。2s/字节/槽数仅合成fixture预算。绑定私有字段保存reservation、所有原Task、presenter及返回ID，root同样强持登记；字段不是产品VM或隐藏authority。`PendingObservation/FailureObservation`在本伪码末给出明确DTO构造函数。

```csharp
// BindAsync: Created is valid at generation 0. Caller creates NO scope/task/context.
var ui = options.Lifetime!; // nonnull/instance ownership checked BEFORE Reserve
var uiBudget = options.ExecutionBudget ?? new ViewportUiExecutionBudget(8388608,8,16);
var reserved = root.ReserveExecution(new ExecutionReservation(
    Session: session, ExpectedGeneration: session.GetSnapshot().Generation,
    Purpose: ExecutionPurpose.UiBinding, MaxRetainedBytes: uiBudget.MaxRetainedBytes,
    MaxWorkInnerTasks: uiBudget.MaxWorkInnerTasks, MaxControlInnerTasks: uiBudget.MaxControlInnerTasks,
    WorkBudget: options.UiCleanupBudget, CloseSessionAfterCleanup: options.OwnSession));
if (reserved.Outcome != PortOutcome.Succeeded || reserved.Value is null)
    return new PortResult<IViewportUiBinding>(reserved.Outcome, null, reserved.Error);
// Above rejection has not created any DispatcherOperation, backend or Presenter task.
var reservation = reserved.Value;
// Binding owns these lists/fields; root closes Work gate before Control runs.
IViewportPresenterLease? presenter = null;
PresenterLeaseRequest? presented = null;
Task<LeaseReturnReceipt>? originalReturn = null;
string returnId = options.BindingId + "/presenter-return-1";
var originalBindWorker = reservation.Start(
    work: async (work, rootToken) =>
    {
        // Returned task is DispatcherOperation.Task itself; NEVER an async wrapper.
        var install = work.StartOriginal(work.Context.Call.Generation,
            (issued, token) => dispatcher.InvokeAsync(() =>
                ui.InstallEmpty(options.BindingId)).Task);
        await install;
        return PendingObservation(); // install done, binding lifetime still open
    },
    cleanup: async (control, cleanupToken) =>
    {
        try
        {
            // Only original Work worker: NOT Work.ObserveAsync (waits presenter-return).
            if (reservation.Work.WorkerTask is { } originalWork)
            {
                try { await originalWork; }
                catch { /* root records original work error; cleanup still removes visuals */ }
            }
            var detach = control.StartOriginal(control.Context.Call.Generation,
                (issued, token) => dispatcher.InvokeAsync(() =>
                    ui.RemoveSubscriptionsAndVisuals(options.BindingId)).Task);
            await detach;
            // Work gate is sealed and no registration factory still running.
            // No newly acquired lease may be missed by this snapshot.
            try { await Task.WhenAll(reservation.Work.OriginalTasks); }
            catch { /* root retains faulted child result/late leases; continue known cleanup */ }
            if (presenter is not null && presented is not null)
            {
                var revoke = await control.StartOriginal(presented.Generation,
                    (issued, token) => ui.RevokePresenterAsync(
                        new BackendRevokeRequest(presented.PresentationId,
                            presented.Generation,"unbind"), issued, token),
                    _ => Array.Empty<IViewportLease>());
                if (revoke.Outcome != PortOutcome.Succeeded || revoke.Value is null ||
                    !revoke.Value.CallbacksQuiesced || !revoke.Value.ReferencesDetached)
                    return PendingObservation(); // root retains presenter, not Returned
                originalReturn = control.StartOriginal(presented.Generation,
                    (issued, token) => presenter.ReturnAsync(new LeaseReturnRequest(
                        returnId,"unbind",issued.RemainingBudget),token),
                    _ => Array.Empty<IViewportLease>());
                var returned = await originalReturn;
                if (returned.State != LeaseReturnState.Returned)
                    return PendingObservation(); // root QueryReturn same returnId, limited policy
            }
            // Worker cannot pronounce itself/whole root Drained while still running.
            return PendingObservation();
        }
        catch (Exception ex)
        {
            return FailureObservation(control.Context, ex);
            // root keeps raw failed/late tasks + any lease, independently cleans known borrows
        }
    });
try
{
    // Only an OBSERVER gets the finite Bind timeout/token; root keeps originalBindWorker.
    await originalBindWorker.WaitAsync(options.UiCleanupBudget,ct);
}
catch (Exception ex)
{
    reservation.RequestCleanup(); // nonblocking; keep original startup/Dispatcher tasks
    var failed = FailureObservation(reservation.Work.Context,ex);
    var outcome = ex is OperationCanceledException ? PortOutcome.Cancelled
        : ex is TimeoutException ? PortOutcome.TimedOut : PortOutcome.Failed;
    return new PortResult<IViewportUiBinding>(outcome,null,failed.OperationError);
}
// BindAsync succeeds only after empty install, not Attach/presenter. Module returns its
// IViewportUiBinding runtime instance carrying this reservation; host does not implement it.
```

真实呈现由公开`control.Presentation.CommitAsync(presentationRequest,sourceCall,ct)`转发同binding.Commit；下面是该成员在完成§10.6接纳/授权和原Task记录后的内部步骤，`presentationRequest`和`sourceCall`就是其输入，`submission=presentationRequest.Submission`，不依赖未绑定回调。不能以Host随手造presentationId代替提交证据。Attach之前只安装空控件，Bind返回后宿主才可`session.AttachAsync(context,ct)`，不会出现Bind等Attach而host等Bind的循环。`GetSnapshot().Generation`在创建child前读，root再次复核；不一致即拒绝委托调用。

```csharp
// On real submission; local adapter handler, serialized admission with Unbind.
var submission = presentationRequest.Submission;
var request = new PresenterLeaseRequest(options.BindingId, submission.Generation,
    submission.BackendGeneration, submission.PresentationId);
var input = new ViewportPresenterSubmission(request,presentationRequest,sourceCall);
var acquire = reservation.Work.StartOriginal(request.Generation,
    (issued, token) => ui.AcquirePresenterAsync(input, issued, token),
    result => result.Value is null ? Array.Empty<IViewportLease>() : [result.Value]);
var acquired = await acquire;
if (acquired.Value is { } lease)
{
    // root's extractor already retained this lease, even if callback is stale/throws.
    presenter = lease;
    presented = request;
    if (acquired.Outcome == PortOutcome.Succeeded)
    {
        var confirmed = await reservation.Work.StartOriginal(request.Generation,
            (issued, token) => lease.ConfirmVisibleAsync(request,issued,token),
            _ => Array.Empty<IViewportLease>());
        // Validate all receipt ids/generations; source auth/deadline rechecked at real UI commit.
        // Save original acquire/confirm/lease identity in GetPresentations() BEFORE adoption.
        // Return this matching result; only true permits PresentationCommitted.
    }
}
```

上面只展示一个presenter（fixture一呈现）；正式多代替换每项保持`(原AcquireTask, request, lease, returnId)`有界表，capacity取MaxWorkInnerTasks/MaxRetainedBytes；赋值与接纳/Unbind串行。Control不能仅依赖`presenter`字段抓迟到资源，**root根据原AcquireTask extractLeases捕获所有结果**，包括回调取消、失败Value带lease、task完成但handler还没赋字段；未被显式清理项由根沿同Owner/revoke/return清理策略继续收敛，未知保持Pending。原Dispatcher任务取消/失败也在root表，不把catch返回值当Drained。回调先关闭 Work 门后不得开始新的呈现；已被接纳的Acquire完成晚于Control等待期限仍被强持、继续归还。

Unbind只返回有限观察结果，不能把清理worker的await包装当生命周期根。具体执行：

```csharp
// IViewportUiBinding.UnbindAsync(timeout, ct), call from outside ANY slot worker.
var unbindClock = System.Diagnostics.Stopwatch.StartNew();
var originalCleanup = reservation.RequestCleanup(); // nonblocking; also armed for root/session close
var uiDone = await reservation.Control.ObserveAsync(timeout, ct);
// timeout/ct only stop this observer, originalCleanup + originalDispatcher/Return remain stored.
if (uiDone.Cleanup.State != CleanupState.Drained)
    return new UiUnbindReceipt(false,false,ct.IsCancellationRequested,
        uiDone.Cleanup,uiDone.OperationError);
if (options.OwnSession)
{
    // UI Control worker has already exited. Session disposal cannot wait for itself.
    if (ct.IsCancellationRequested)
        return new UiUnbindReceipt(true,false,true,PendingObservation().Cleanup,uiDone.OperationError);
    var remaining = timeout - unbindClock.Elapsed;
    if (remaining < TimeSpan.FromMilliseconds(50))
        return new UiUnbindReceipt(true,false,ct.IsCancellationRequested,
            PendingObservation().Cleanup,uiDone.OperationError);
        // Binding schedules its already-armed slot-EXTERNAL OwnSession-close continuation;
        // it is held by root's session cleanup owner, not by Work/Control execution slots.
    var originalSessionClose = session.DisposeAsync(remaining,ct);
    var closed = await originalSessionClose;
    return new UiUnbindReceipt(true,closed.Drained,closed.WaitCancelled,closed.Cleanup,closed.Error);
}
return new UiUnbindReceipt(true,true,false,uiDone.Cleanup,uiDone.OperationError);
// Root.CloseAsync is invoked later by the host, outside UI workers/Unbind implementation.

static ExecutionObservation PendingObservation() => new(
    new CleanupSnapshot(CleanupState.Pending,Array.Empty<PendingResource>(),null,null),null);
static ExecutionObservation FailureObservation(RootExecutionContext context, Exception ex)
{
    var error = new ViewportError("VIEWPORT-011",context.Call.OperationId,"ui-cleanup",
        "binding",false,"Viewport.Recovery.Close",ex.GetType().Name);
    return new(new CleanupSnapshot(CleanupState.Unknown,
        Array.Empty<PendingResource>(),error,null),error);
}
```

PendingObservation的空列表仅为worker局部提示，root.ObserveAsync回执必须用自己的实际ledger填PendingResource，不能把它视为清零；同样FailureObservation保留工作/清理错误两轴。原cleanup worker可await原Task直至实际退出，**有限的是观察/每次可中断端口预算**，观察超时后根仍强持，不强杀不可中断任务；违约永久task使root保持Unknown并关闭接纳，独立cleanup尝试数耗尽不发Drained。ExecutionReservation.CloseSessionAfterCleanup在Reserve/Start时以公开DTO向同root明确登记OwnSession关闭责任，随清理委托armed到session固有close Owner；该一次性关闭动作只在本UI scope真实收敛、Control worker退出后触发，位于Work/Control之外。即使Unbind调用者提前取消/超时也不能漏触发；新Root/authority不参与。根外Session关闭Task由session固有ledger保存，Unbind仅有限观察同一次关闭。Unbind总deadline从入口单调开始，UI观察后OwnSession Dispose只能传剩余预算而非再给完整timeout；没有剩余预算时返回本UI已Detached、session尚未Drained的Pending；root依据ExecutionReservation.CloseSessionAfterCleanup保留一次性的slot外Session.Dispose触发计划，由session固有关闭Owner在UI已收敛后发起并强持，不能仅返回Pending却永不启动OwnSession关闭，不能使总时限翻倍。根外Root.Close也用单独finite观察预算，不混进Control等待自身。

### 10.8 实际渲染、同Owner呈现与两个STA装配

模块内置生产/离线实现的唯一公开构造形状如下（同`Asun.UI.Viewports.Wpf`、目标声明，未创建工程/执行）：

```csharp
public sealed record ViewportRendererOptions(BackendPolicy Policy,
    long MaxNativeBaselineBytes, long MaxRasterBytes,
    int MaxPendingSubmissions, TimeSpan CleanupBudget);
public sealed record ViewportRendererPorts(IViewportBackendFactory Backend,
    IViewportUiLifetimePort Lifetime);
public static class ViewportRendererFactory
{
    public static PortResult<ViewportRendererPorts> Create(ViewportControl control,
        IViewportProcessRoot root, ViewportRendererOptions options);
}
```

Create只冻结control/同Dispatcher/root与配置，三种BackendPolicy沿§4.6，bytes非负且按所选路线所需项>0、MaxPendingSubmissions正且≤root允许的任务容量、CleanupBudget在§4.4有限范围；非法002/003/015、无端口对象/无native。Host显式调用一次，将结果Backend传Options.Backend、Lifetime传Bind Options.Lifetime；二者来自同内部renderer Owner且Control/root一致，交叉混用016。两个bytes是Host预留的本方容量，不是声称native精确allocator上界；Required还须沿session真实resource admission结算，未知baseline不返额。Create后的实际session/request/limits在Backend.CreateAsync及Bind时逐项核同root，不能先开窗再找预算。CPU源payload是§15.2.2已冻结Adapter私有布局/域/lease，内置实现只识别这一路径；Host自有payload必须用自有backend/lifetime（三接口公开），不通过object反射或托管类型名称猜像素。Surface显示payload同理精确按§15.2.5.1接入。

本节冻结§10.7的renderer实现责任，不能让产品Host临时挑窗口技术。生产HALCON的`IViewportBackendFactory/IViewportBackend/IViewportUiLifetimePort`在可选WPF DLL内实现，属于同一实例的三个端口面：构造输入是实际`ViewportControl`、该Control.Dispatcher、§4.4/14的显式显示Profile、§15.2冻结的源binding及本方Owner/预算。构造只冻结有限metadata，不开window/读源；Create/Install/Submit/Acquire分别沿原root槽启动。Host可以自己实现上述公开端口（features有限CPU fixture正是这一用途），但必须遵守同Owner协议；不是允许引用其它模块私有字段或随意返回true。源Adapter直接实现已公开IFramePort/ICoordinatePort/IRoiPort/ISurfacePort，逐方法配方见§15.2；不再要求一个未定义的通用factory或容器发现端口。

**HALCON窗口与线程。** WPF使用私有`HwndHost`承载Win32子窗口，不引入WinForms或把HWindow放Core。InstallEmpty在Dispatcher安装空视觉/输入路由，不读源/创建3D模型；真正HALCON窗口在该backend的已预留baseline/原Submit中通过`cv2.open_window(0,0,W,H,parentHwnd,'visible','',out handle)`建立，parentHwnd是本HwndHost真实64位句柄，不从SourceId解析。该window的open/set_part/disp/flush/query/clear/close都串行在同Control的Dispatcher执行，CPU解码/块复制/模型生成在本backend单一有界工作执行器；移交到Dispatcher前保留原Task与所有borrow。禁止Task.Run并发操作同window、全局set_system或全局当前窗口。`set_window_extents`改变尺寸不会自动重画，resize/DPI/host布局变更必须封旧命中、创建新view/generation、按新物理client尺寸重新Submit。0尺寸/不可见/最小化只保计划，不报可见。

HwndHost有airspace边界：影像、Region/XLD、选择线、显示控制柄及探针标记均在同HALCON子窗口用§7.7同矩阵绘制；不把WPF透明Canvas覆盖在child HWND之上假设可见。命令条/身份/侧栏/状态栏位于画布外，浮出候选用有焦点管理的独立Popup，关闭须解除事件/原borrow。UIA由WPF控件AutomationPeer投影稳定对象/当前工具/选点摘要，不暴露native handle。空图/错误投影使用同绘图区的WPF占位内容；切换显示宿主前先撤原HALCON交互和窗口引用。显示参数固定窗口局部设置，不修改其它实例的主题、HALCON系统参数或DevExpress全局语言。

**2D提交。** 先按§7.5只读可见tile和显式halo；§15.2.2负责保真实layout/域与tight本地copy，按UInt8/UInt16/Int16/Float32映HALCON byte/uint2/int2/real。Float64仅可在离线Raster显示经已冻结LUT投影为8位副本，原值仍由Probe读取；HALCON路径遇此格式007，不悄悄量化原值。Interleaved多通道在受控副本中按真实布局拆plane，每plane同Owner预算/生命周期，以三个plane合RGB，非RGB多通道只能选明确channel，不猜通道语义；异构多plane/多allocation限制仍按§15.2.2。Native复制使用`gen_image1`在pin的tight本方缓冲上复制，创建真退出后unpin；不使用外借pointer的gen_image1_ex。显示变换image/域/XLD严格沿§7.7，LUT/伽马仅投影副本、不改原源/测量。每次先clear再disp本次完整受控场景；用`set_window_param(window,'flush','false')`批次绘制后`flush_buffer`，后续缩放/平移由Core新Submit完整重画，不使用窗口内部交互变换。若调用HALCON内建交互则须先恢复flush=true，当前首版不采用该路径。

**3D提交。** §15.2.5.1的源保真double副本/LOD、&vp_carrier、已有mesh拓扑、显式native米制换算和baseline继续唯一有效。固定支持可精确表达的无畸变pinhole展示投影：Projection第0/1行仅P00>0/P11>0和P02/P12非零，第3行为[0,0,-1,0]，深度行等于Near/Far的标准透视项；WorldToCamera和DisplayModel为可逆affine、相机有效域按§8.4。矩阵其它族不临时猜CamParam，backend预检007并回合法已授权旧视图/明确不可用；不是默许显示与拾取使用不同camera。支持条件是后端能力边界，Core可保合法通用矩阵，不改其数据契约。展示相机不取代物理标定。

先将源点经DisplayModel（含显式Z倍率）和WorldToCamera得到右手camera坐标(x,y,z)，进入HALCON的显示点为米制(x,-y,-z)，保原Carrier/Root旁表；identity Pose由`create_pose(0,0,0,0,0,0,'Rp+T','gba','point')`取得。物理client W/H下fx=W*P00/2、fy=H*P11/2、cx=W*(1-P02)/2-0.5、cy=H*(1+P12)/2-0.5；构造HALCON CamParam `['area_scan_division',1,0,1/fx,1/fy,cx,cy,W,H]`，Focus=1只定义展示camera，Kappa=0，不是客户镜头参数。native有效正深度及Near/Far在生成显示副本前检查；跨near/far的face本首版不可拾取，不伪造未裁面的精确Support。显示与离屏pick用同一组CamParam/Pose/part/opacity/point_size与可遮挡模型；投影不匹配拒绝006/007。native meter往返仅作显示，原SourcePoint/RootIndex始终取CPU原副本；实际精度验收按显示Profile，不把double单位换算或GPU深度当无损原值。

**可见确认与归还。** Submit生成唯一SubmissionId/PresentationId，仅返回已准备/已提交的事实，不能自己回VisibleConfirmed=true绕过binding。Acquire保存完整ViewportPresenterSubmission，lease.Identity指本Owner/root/binding/generation/backend与独立borrow；Confirm在实际Dispatcher再次核同submission/context/授权期限并确认目标窗口挂到同Control、client正面积且仍可见，原disp/flush或Raster写入真实退出、目标当前输出确为该submission后才返回true。HALCON以同窗口完成的flush及受控输出记录确认窗口内容；Raster须有当前scene的已完成绘制记录和实际装载/呈现观察，单纯WritePixels/依赖属性赋值、CompositionTarget.Rendering事件或Dispatcher.Task完成均不足。呈现观察不证明人在看/跨进程遮挡零延迟撤回；窗口不可见/已知遮挡/观察证据缺失返回false/Unknown并保留原责任。真实UI smoke另用已知像素/ROI/身份的独立窗口观察验证呈现，不把mock receipt、截图或合成图当现场验收。

离线Raster固定消费同一有界Tile/DisplayPlan：选择原channel→按已冻结LUT线性截到[0,1]（常量中灰/无效独立hatch）→最近或双线性按显式显示方法生成8位仅显示副本→Dispatcher WriteableBitmap写各tile→DrawingVisual/DrawingContext以同SourceCenterToDip、实际clip与稳定层顺序绘到受控RenderTargetBitmap→当前Image.Source替换，记录同SubmissionId的完成绘制。两份pixel输出与tile staging/视觉引用计MaxRasterBytes，只有画布范围，禁止整幅超大图拼成bitmap。Capture/探针仍走Core/原源，不从该bitmap取值。Raster不支持Surface3D/pick或生产Purpose，不因资源/权限失败fallback；退化/无效域同HALCON路线拒绝或标缺口。

显示附加参数在首版明确收敛：LUT及ZMultiplier已有公开入口；Gamma固定1、整体Opacity固定1、颜色/灰度来自源Owner或显式通道，显示平滑仅§7.7已定插值，无额外滤波/调参UI。§7.4所说伽马/透明度/平滑是不得改测量事实的边界说明，并不授首版新的可调参数；§10.9保留参数文字用于只读值/宿主投影，不凭资源键创造Core参数。伪彩高度图只在源Owner已提供颜色属性时显示，Unknown不填最低色；本模块不自动猜一套质量色阈值。以后明确新增交互参数须先修同一公开契约，不交实现者临时选择颜色算法。

Renderer自身为Confirm保存的一次性可见观察必须与当前Control HwndSource、目标Image/HALCON child、SubmissionId与render revision一致，不能用任意全局Rendering通知匹配。离线Raster正常Host在绘制及后续实际UI呈现观察均确认时才true；没有可验证观察的环境以false/Unknown结束本次有限Commit，正常可见用例不允许跳过为PASS。这是可执行拒绝分支，不把未实测WPF提交能力提升为软件mock成功。相关独立观察断言仍按本节VP-U04与§14计入分母。

**默认实际观察算法固定，不留Host自选fence。** Confirm先在Dispatcher核挂载/可见/未最小化、实际物理client矩形完整位于当前桌面，冻结原SubmissionId+代号+位置/尺寸/DPI+授权及期望显示像素；Raster期望取本次已完成RenderTargetBitmap的Pbgra32/Bgr32读只副本（最终背景固定opaque，RGB规范化），HALCON在同window串行以`dump_window_image`取当前已flush输出的byte RGB，保存与原submission一致的受控输出记录。随后原root child在有界工作线程调用`DwmFlush`等待本应用已排队图形变更，不能在Dispatcher同步等；S_OK只作一步，绝不单独判可见。沿同child对该**唯一控件物理client矩形**用GetDC(null)→CreateCompatibleDC/CreateCompatibleBitmap→SelectObject→BitBlt(SRCCOPY|CAPTUREBLT)→恢复旧bitmap→GetDIBits(top-down、32bit、BI_RGB)取得实际桌面RGB；逐像素与期望RGB精确比较，忽略未定义alpha字节。GetDIBits调用时bitmap不得仍选入DC，finally恢复/释放本方GDI object/DC与原screen DC，错误/取消也保原Task到退出。不得读取窗外客户区域、保存屏幕原bytes、将读回用作源Probe/业务证据或发送日志。

完成读回后再在原Dispatcher核完全相同的submission/generation/授权/位置/尺寸/DPI与当前显示记录：全部一致且全client像素相同才VisibleConfirmed=true；已知遮挡、越桌面、desktop不可读、DwmFlush/GDI失败、色彩变换导致不等、尺寸变动或晚到均false/Unknown（撤权008/012），不自动加色差容忍、抽样少数像素或直接回true。§4.7.1可信空清理分支只核同原Control删除资格/当前空代，Read撤销不阻确认**中性无源空画面**，绝不显示原source标题/旧层/缓存像素，也不签非空呈现成功；普通内容仍严格重核当前Read。读回仅证明当次本机显示区域的内容，与物理计量、无人遮挡未来时刻或客户生产验收无关。截图/合成输入不因此升级现场证据。支持精确RGB观察的环境走正常成功；不支持的环境保明确可见未确认结果，不绕既有门。窗口后续移动/重布局仍以Core新view生成新代，不能借前一次读回确认新图。

期望图、规范化副本、GDI bitmap与读回数组的保守峰值至少`16*W*H` bytes，再加本scene tile/Native baseline/RenderTargetBitmap、数组头和旧代并存，checked后按UI ExecutionBudget/MaxRasterBytes/session/root预留；预算不足在dump/BitBlt/分配前003，不在Confirm后补账。Readback与两次Dispatcher均以同Commit剩余deadline登记原Task；每提交只一次读回，无无限捕屏重试。性能Profile单列dump/拷贝/DwmFlush/readback/比较/授权核时延与bytes，纳入§14端到端，不能只报渲染快路径。VP-U04增加实际遮挡/最小化/色彩不等、DwmFlush/GDI闩锁关闭、窗口移动与本readback失败的可判定反例；失败仍必须归还本GDI与Presenter借用。该路线可直接按Win32签名实现，不依赖未公开的WPF GPU fence。

直接读取的官方依据：[DwmFlush](https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/nf-dwmapi-dwmflush)说明等待本应用queued DirectX而非整个session；[BitBlt](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-bitblt)的CAPTUREBLT包含覆盖的layered窗口；[GetDIBits](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-getdibits)明确bitmap不能选入DC并定义top-down；HALCON26.05 [dump_window_image](../../../halcon算子手册/operators/dump_window_image.html)输出当前color table的byte显示图。这些只定义观察步骤，没有执行桌面抓取或native/GDI调用。

HwndHost.BuildWindowCore返回本实例创建的子HWND，DestroyWindowCore仅释放本实例HWND；宿主正常关闭必须先Unbind到真实Drained再Window.Close。OS/Dispatcher强制先退出时，原native/queued回调不再假称成功或主动再次close旧handle：封门、保原Task/model/容量账，返回Unknown/当前原错误，按原root清理或受控宿主退出处理；不得因WPF销毁父窗口推断HALCON/GPU/source借用已经Released。任何Dispose/Destroy异常分别保业务与cleanup错误，不吞掉初始错误。HALCON child实际可绘制client尺寸由本窗口取得（含其border差异），不能把宿主外框宽高当W/H；§10.8相机与Core物理像素使用同一client原点。`compose3`只组合三个已有plane引用，不新复制三份buffer，组合图与plane均留至最后native读退出再分别Dispose；背景/图例与HUD按本次scene全量重画，不能在旧图上仅换新标题。

Revoke先封该presentation新借用/输入，序列化原Submit/Acquire/Confirm已登记任务，移除当前图/标题/overlay/native窗口引用；以同presentation保存的原Revoke Task幂等观察，不在Unbind和Core.Revoke各clear一次。所有实际window/model/callback引用退出才CallbacksQuiesced/ReferencesDetached；随后同ReturnId归还Presenter及source/display borrow。`close_window`、`clear_object_model_3d`与每个iconic/tuple Dispose分别登记，不能用tuple.Dispose代替模型clear。HALCON/GPU缓存baseline由真实容量Owner保留，不将clear/GC当全进程显存退款；未知仍计旧/新并存与根槽，Root.Close不得以window.Close释放未知资源。源Reader/CG/ROI等借用服务不因本Control关闭而被Dispose。

**两个独立STA Host的完整入口差异。** 复用§11.2 A/B已冻结Context/端口/权限/Profile与§10.7原任务链：各Host先建立自己的有限HostOwner→root→无参Control→本Control的实际renderer/lifetime端口实例→factory.Create，Options.Backend=该renderer factory，Options.Presentation=control.Presentation→`BindAsync(session,root,new ViewportUiBindingOptions(id,own,ViewportUiResourceCatalog.Get(language).Value!,2s,Lifetime:renderer),ct)`→保存返回binding→一次Attach→真实Commit→原Control/root清理。2s仅软件Host预算；任何Get失败不继续Bind，失败回执/原Task仍保根。A的id=`measurement/view`、EditableDraft+RoiEditing/Probe+Navigation/Presentation、OwnSession=true，注入原020端口；B的id=`review/view`、ReadOnly+Navigation/Probe/Presentation、Required真实准入、OwnSession=false，RoiEditing不申请。每Host自己的STA/Dispatcher/Window/renderer/root，来源可借同Owner不同lease；没有UI的§11 Host不构造这些对象。

上段renderer端口实例具体取`ViewportRendererFactory.Create(control,root,new ViewportRendererOptions(HalconRequired,显式ProfileNativeBytes,显式ProfileRasterBytes,显式ProfilePendingCount,2s))`的Value；赋Options.Backend=Value.Backend、Lifetime=Value.Lifetime，非将record本身当IViewportUiLifetimePort。A/B原§11.2资源/权限/源端口不改，native容量/Root.MaxRetained与UI ExecutionBudget按同一已采纳软件Profile核总量，无容量直接拒绝，不把1MiB Core夹具额度当实际HALCON窗口可运行。可运行软件UI fixture时明确用各自FixtureViewportPorts实现有限CPU接口，64MiB源显示/64MiB UI、ExecutionBudget=(67108864,32,32)、root=(各自id,2,256,128,268435456,2s,2)/2呈现slots/2s为标记Synthetic的测试上限，仍在固定1920×1080视口内测实际client，输出真实所需完整buffer/readback账超64MiB时拒绝case而非扩大屏幕或超账。生产B所需真实资源/授权由原Owner提供，不拿fixture权限冒充。所有公开factory/Bind均有结果检查及同Owner有限关闭，无未定义的BuildRenderer辅助方法。

features-2d的`FixtureViewportPorts`无需新增Root/Close：保其现有vc/dispatcher/backend，实现本节IPresentationPort成员为直接转发`vc.Presentation`，Bind Options追加`Lifetime: vp`；其Acquire接收ViewportPresenterSubmission并保存Request/Presentation/SourceCall，Confirm按原request与child CallContext重核同auth，Revoke/Return用同Owner。原session.Create/ReserveExecution/StartOriginal/OwnSession/有限Close/晚到return按§3.6/4.6.1/10.7，不另设计服务。其资源直接用§10.9Catalog而非猜七个键。features本身的文字由该模块维护，不加入viewport资源。两个consumer均可通过binding.GetPresentations关联同原Task/lease身份，不能把Host表中的等待wrapper替代它们。

新增实施断言VP-U03：同Control.Presentation在Bind前拒绝且Acquire=0；Lifetime=null无Reserve/IO；正确Bind→Commit→原input逐字段一致→同Task重复返回；跨Control/root/sourceCall/context/auth/revision错拒绝；Acquire晚到/Confirm闩锁/撤权/Unbind时根仍抓lease且同Owner先Revoke后Return；同Owner清理幂等、不关共享session；GetPresentations不泄漏借用/无限记录。VP-U04：Camera P00=P11=2、P02=P12=0、W=1000/H=600、camera点(0,0,-1)映物理中心(499.5,299.5)，(0.1,0.2,-1)映(599.5,179.5)，native和Core同一结果；skew/不支持Projection/零client/缺可见证据不得true。真HALCON/WPF窗口线程/airspace/原Task/原图像验证放既有规划WPF Smoke（§10.6/13.1），不是Core运行证据。

官方局部依据：HALCON26.05 [open_window](../../../halcon算子手册/operators/open_window.html)、[set_window_extents](../../../halcon算子手册/operators/set_window_extents.html)、[set_window_param](../../../halcon算子手册/operators/set_window_param.html)、[flush_buffer](../../../halcon算子手册/operators/flush_buffer.html)、[close_window](../../../halcon算子手册/operators/close_window.html)、[project_3d_point](../../../halcon算子手册/operators/project_3d_point.html)、[create_pose](../../../halcon算子手册/operators/create_pose.html)，配合§19.5已读显示/矩阵/拾取文档与§10.5本机DX25.2.3官方XML。没有新增未核实的DevExpress控件API；dxdocs本轮仍不可调用，复用有效本机依据。HALCON调用文字为目标算子语义顺序，不假装已编译C#签名。

### 10.9 完整资源快照、三语键与缺键恢复

本节关闭F2D-UP-UI-02，属于同WPF DLL随包发布的不可变文本，不依赖宿主私有ResourceManager、隐藏窗口或网络。公开形状（目标声明，本轮未实现）：

```csharp
public static class ViewportUiResourceCatalog
{
    public const string SchemaId = "viewport-ui-text/1";
    public static IReadOnlyList<string> RequiredKeys { get; }
    public static PortResult<ViewportUiResources> Get(string language);
}
```

ViewportUiResources.Revision在本版是文本schema身份，必须精确`viewport-ui-text/1`，自定义语言也使用该schema；同schema下新文本值由每次完整快照与其Host外部版本识别，不用Revision授权限或找latest。Get按CultureInfo规范culture名称后Ordinal匹配，不接受空/无效culture；不做机器CurrentUICulture隐式发现。内置三种语言是完整声明值，额外Host文字与其授权数据独立。

Get仅接受Ordinal规范化的已知culture `zh-CN/zh-TW/en-US`并返回该culture完整内置快照，Revision=`viewport-ui-text/1`；未知语言Rejected/002，宿主可自行提供同RequiredKeys的扩展语言快照，不强制回退英语。RequiredKeys是下表中`Viewport.`前缀接键名的**完整集合**，按Ordinal排序，不从enum/AutomationId动态猜键。Get每种语言必须恰覆盖此集合；资源包与控件同版本发布，新增必需键升级SchemaId及文档，旧完整快照不能静默缺键通过。语言切换不刷新像素/重新授权或自动提交草稿。

| 键名（统一前缀Viewport.） | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Canvas | 图像 | 影像 | Image |
| Fit | 适应窗口 | 適應視窗 | Fit to window |
| OneToOne | 1:1 | 1:1 | 1:1 |
| Reset | 重置 | 重設 | Reset |
| Layers | 图层 | 圖層 | Layers |
| Recovery | 重试 | 重試 | Retry |
| Recovery.Close | 重试关闭 | 重試關閉 | Retry close |
| Cancel | 取消 | 取消 | Cancel |
| Details | 详情 | 詳細資料 | Details |
| RestoreLayout | 恢复布局 | 還原配置 | Restore layout |
| Apply | 应用 | 套用 | Apply |
| Tool.Navigate | 导航 | 導覽 | Navigate |
| Tool.Probe | 探针 | 探針 | Probe |
| Tool.Select | 选择 | 選取 | Select |
| Tool.EditDraft | 编辑草稿 | 編輯草稿 | Edit draft |
| View.Image2D | 二维 | 二維 | 2D |
| View.Surface3D | 三维 | 三維 | 3D |
| View.Split2D3D | 二维与三维 | 二維與三維 | 2D and 3D |
| View.Profile | 高度剖面 | 高度剖面 | Height profile |
| MirrorX | 水平镜像 | 水平鏡像 | Mirror horizontally |
| MirrorY | 垂直镜像 | 垂直鏡像 | Mirror vertically |
| Follow.Fixed | 固定选择 | 固定選取 | Fixed selection |
| Follow.Latest | 跟随最新 | 跟隨最新 | Follow latest |
| Status.Created | 尚未载入 | 尚未載入 | Not loaded |
| Status.Attaching | 正在载入 | 正在載入 | Loading |
| Status.Ready | 就绪 | 就緒 | Ready |
| Status.Empty | 无图像 | 無影像 | No image |
| Status.Updating | 正在更新 | 正在更新 | Updating |
| Status.Stale | 图像已过期 | 影像已過期 | Image is out of date |
| Status.Blocked | 此功能不可用 | 此功能無法使用 | Feature unavailable |
| Status.RecoverableError | 图像读取失败 | 影像讀取失敗 | Image read failed |
| Status.Disposing | 正在关闭 | 正在關閉 | Closing |
| Status.Draining | 等待任务退出 | 等待工作結束 | Waiting for tasks to finish |
| Status.Drained | 资源已归还 | 資源已歸還 | Resources returned |
| Status.Disposed | 已关闭 | 已關閉 | Closed |
| Status.Busy | 正在处理 | 正在處理 | Working |
| Status.PermissionDenied | 无访问权限 | 無存取權限 | Access denied |
| Status.Completed | 操作完成 | 操作完成 | Operation complete |
| Status.Partial | 部分内容不可用 | 部分內容無法使用 | Some content is unavailable |
| Status.CleanupUnknown | 资源尚未归还 | 資源尚未歸還 | Resources are still in use |
| Status.NotEvaluated | 尚未验证 | 尚未驗證 | Not evaluated |
| Status.TargetPending | 未设置显示目标 | 未設定顯示目標 | Display target not set |
| Status.Degraded | 已降低显示细节 | 已降低顯示細節 | Display detail reduced |
| Value.Unknown | 未知 | 未知 | Unknown |
| Value.Invalid | 无效 | 無效 | Invalid |
| Value.NotLoaded | 尚未读取 | 尚未讀取 | Not read |
| Value.Outside | 超出范围 | 超出範圍 | Outside range |
| Value.NoMapping | 缺少映射 | 缺少對應 | No mapping |
| Value.NoHit | 未选中 | 未選取 | No hit |
| Value.Ambiguous | 请选择对象 | 請選取物件 | Choose an object |
| Value.Unsupported | 不支持此来源 | 不支援此來源 | Source not supported |
| Value.Original | 原样本 | 原樣本 | Original sample |
| Value.Interpolated | 插值 | 插值 | Interpolated |
| Value.Constant | 常量 {0} | 常數 {0} | Constant {0} |
| Value.Unmatched | 未匹配 | 未配對 | Unmatched |
| Value.Uncalibrated | 未标定 | 未校正 | Not calibrated |
| Value.Relative | 相对值 | 相對值 | Relative value |
| Value.ReadOnly | 只读视图 | 唯讀檢視 | Read-only view |
| Support.Exact | 精确关联 | 精確關聯 | Exact association |
| Support.Unknown | 支持关系未知 | 支援關係未知 | Support unknown |
| Support.Unsupported | 不支持此关系 | 不支援此關係 | Support not supported |
| Parameter.Zoom | 缩放 | 縮放 | Zoom |
| Parameter.Rotation | 旋转 | 旋轉 | Rotation |
| Parameter.LutMin | 灰度下限 | 灰階下限 | Lower display value |
| Parameter.LutMax | 灰度上限 | 灰階上限 | Upper display value |
| Parameter.Gamma | 伽马 | 伽瑪 | Gamma |
| Parameter.Opacity | 不透明度 | 不透明度 | Opacity |
| Parameter.ZMultiplier | 高度显示倍率 | 高度顯示倍率 | Height display scale |
| Parameter.Lod | 显示层级 | 顯示層級 | Display level |
| Parameter.Channel | 通道 | 通道 | Channel |
| Parameter.Automatic | 自动 | 自動 | Automatic |
| Parameter.StatisticsDomain | 统计范围 | 統計範圍 | Statistics region |
| Parameter.SelectionTolerance | 选择容差 | 選取容差 | Selection tolerance |
| Parameter.HandleSize | 控制柄大小 | 控制柄大小 | Handle size |
| Parameter.LineWidth | 线宽 | 線寬 | Line width |
| Parameter.Source | 来源 | 來源 | Source |
| Parameter.Revision | 修订 | 修訂 | Revision |
| Parameter.Position | 位置 | 位置 | Position |
| Parameter.Height | 高度 | 高度 | Height |
| Parameter.Row | 行 | 列 | Row |
| Parameter.Column | 列 | 欄 | Column |
| Parameter.Method | 方法 | 方法 | Method |
| Parameter.Weight | 权重 | 權重 | Weight |
| Unit.Pixel | px | px | px |
| Unit.Dip | DIP | DIP | DIP |
| Unit.Micrometer | µm | µm | µm |
| Unit.Millimeter | mm | mm | mm |
| Unit.GrayValue | 灰度值 | 灰階值 | Gray value |
| Unit.PixelHeight | 相对高度 | 相對高度 | Relative height |
| Tip.Fit | 显示完整图像 | 顯示完整影像 | Show the whole image |
| Tip.OneToOne | 一个源像素对应一个屏幕像素 | 一個來源像素對應一個螢幕像素 | One source pixel per screen pixel |
| Tip.Reset | 恢复初始显示，不改源数据 | 還原初始顯示，不改來源資料 | Restore the initial view; source data stays intact |
| Tip.Navigate | 拖动平移，滚轮缩放 | 拖曳平移，滾輪縮放 | Drag to pan; use the wheel to zoom |
| Tip.Probe | 读取原值；插值会显示支撑 | 讀取原值；插值會顯示支援點 | Read source values; interpolation shows its support |
| Tip.Select | 重叠对象须明确选择 | 重疊物件須明確選取 | Choose explicitly when objects overlap |
| Tip.EditDraft | 仅预览草稿，提交由宿主处理 | 僅預覽草稿，提交由主程式處理 | Preview a draft; the host handles submission |
| Tip.Layers | 仅改变显示与选择范围 | 僅改變顯示與選取範圍 | Change display and selection visibility |
| Tip.Recovery | 使用当前来源重试 | 使用目前來源重試 | Retry with the current source |
| Tip.Close | 继续等待原任务并归还资源 | 繼續等候原工作並歸還資源 | Wait for the original tasks and return resources |
| Tip.ReadOnly | 在编程工作台编辑 | 在編程工作台編輯 | Edit in the programming workspace |
| Tip.DisplayOnly | 仅影响显示，不改变测量值 | 僅影響顯示，不改變量測值 | Changes display only; measurements stay intact |
| Tip.Permission | 联系宿主权限管理员 | 聯絡主程式權限管理員 | Contact the host access administrator |
| Error.001 | 接口规格未确定 | 介面規格尚未確定 | Interface specification is incomplete |
| Error.002 | 输入无效，请修正字段 | 輸入無效，請修正欄位 | Invalid input; correct the field |
| Error.003 | 超过显示预算，请缩小范围 | 超過顯示預算，請縮小範圍 | Display budget exceeded; reduce the region |
| Error.004 | 来源不可用，请检查后重试 | 來源無法使用，請檢查後重試 | Source unavailable; check it and retry |
| Error.005 | 显示已更新，请重新操作 | 顯示已更新，請重新操作 | The view changed; repeat the action |
| Error.006 | 坐标映射不可用 | 座標對應無法使用 | Coordinate mapping unavailable |
| Error.007 | 此功能未装配 | 此功能尚未配置 | Feature not configured |
| Error.008 | 无此操作权限 | 無此操作權限 | This action is not permitted |
| Error.009 | 已取消，资源归还状态见详情 | 已取消，資源歸還狀態見詳細資料 | Cancelled; see details for resource return status |
| Error.010 | 操作超时，等待原任务退出 | 操作逾時，等候原工作結束 | Timed out; waiting for the original task |
| Error.011 | 显示后端失败，请检查诊断 | 顯示後端失敗，請檢查診斷 | Display backend failed; check diagnostics |
| Error.012 | 授权已过期，请重新授权 | 授權已過期，請重新授權 | Authorization expired; request access again |
| Error.013 | 资源状态异常，请联系维护人员 | 資源狀態異常，請聯絡維護人員 | Resource state error; contact maintenance |
| Error.014 | 未配置导出，请联系宿主维护人员 | 未配置匯出，請聯絡主程式維護人員 | Export is not configured; contact host maintenance |
| Error.015 | 无可用资源额度，请等待或缩小范围 | 無可用資源額度，請等待或縮小範圍 | No resource capacity; wait or reduce the region |
| Error.016 | 资源或来源身份冲突，请检查诊断 | 資源或來源識別衝突，請檢查診斷 | Resource or source identity conflict; check diagnostics |

上表文字就是首版资源值；新增语言可由Host提供同Schema完整Text。UIA Name复用命令/参数/状态键，HelpText复用Tip与Error键；SuperTip Header=相应命令或参数，Body=相应Tip，显示设置统一Tip.DisplayOnly，恢复统一Tip.Recovery/Tip.Close。源Id/hash/修订/用户已命名通道是授权后的数据值，不翻译为另一事实；图层LabelResourceKey是Host扩展键，必须在Text中显式存在，绑定/SetLayers接纳前核验，不能用内置表补猜产品缺陷说明。源自上游的未登记RecoveryKey/诊断用本模块Error映射+安全字段值，不直接把内部英文错误输出给操作员。

资源输入限额由本模块冻结为每键1..128 UTF-16单元、每值1..1024、RequiredKeys之外最多1024个Host扩展键、全快照UTF-8 key+value和≤1MiB；先计数/计长/格式合法再深复制及root准入，不复制无界字典。Revision/Language非空，含NUL或重复/大小写碰撞键拒绝；格式参数只允许表内Constant的{0}，不执行XAML/HTML/表达式。额外语言值也须匹配同占位符集合，不以失败回退旧语言部分键。SetResources先完整冻结/校验再在同Dispatcher原子替换；缺键/超长/取消保持旧完整资源，报告002/003/009；旧快照保到原回调退出，切语言不静默降低权限。默认资源与自定义资源使用同校验入口。

VP-U05必要断言：三个Get的RequiredKeys集合完全一致且Ordinal排序、表中每命令/状态/16错误/单位/Tip/UIA均可取；删任一必需键/伪Schema revision/非法占位符/超限先拒且旧语言全保留；未知culture Get拒绝但Host合法扩展快照可Bind；两Control切语言互不污染/不读源/不自动提交；英文长串下主图与安全恢复命令可达。只有这三种真实语言和1920×1080固定验证视口，不增加其它分辨率矩阵。原七fixture键仍在完整集合，不要求features复制本表成为第二权威。

显式映射规则：ViewportState逐一用Status同名键；UI Busy/PermissionDenied/Completed/Partial/CleanupUnknown用同名键；ProbeValidity OriginalSample→Value.Original、Interpolated→Value.Interpolated、MaskInvalid/SupportInvalid→Value.Invalid、NotLoaded→Value.NotLoaded、Outside→Value.Outside、NoMapping→Value.NoMapping、PermissionDenied→Status.PermissionDenied。SurfaceHit NoHit/Invalid/Ambiguous/NoMapping使用相应Value键，SupportParentUse的拒绝原因按Error/Value.Unknown等已定义键投影，SC三态用Support三键，均不把Exact叫质量合格。单位按LengthUnit/ProbeValueUnit映Unit已列键；未知enum先拒绝002，不能用ToString当文字。VIEWPORT-001～016分别映Error.001～016，安全诊断展开仍用原错误码/原Field值，不漏译按钮/恢复说明。图表轴用Parameter.Position/Height+相应Unit，数据使用当前culture数值格式且精确长整数使用无分组十进制；日志、OriginalIndex与Golden仍InvariantCulture。

## 11. 无 UI 最小调用与可靠关闭

### 11.1 纯计划调用（按 §3.4 完整公开类型，尚未实施/编译）

模块公开无参 `ViewportPureOperations` 实现 §3.4 的纯接口；下面使用 `IViewportPureOperations pure = new ViewportPureOperations()`；它是普通实例，不需要隐藏窗口。合成几何只用于定义测试，不是生产 Profile、性能或计量证据。预算值从宿主的已批准计划预算读取。

```csharp
var input = new PlanInputs(
    new PlanSource(new SourceId("synthetic-4000x2000"), "r1",
        new CoordinateRevision(1), 4000, 2000, new PixelRect(0, 0, 4000, 2000)),
    new DisplayGeneration(1), new DipSize(1000, 600), 1.25, 1.25,
    new PlanView(DisplayMode2D.Fit, 1, 0, false, false, new DipPoint(0, 0)),
    [new PyramidLevelPlanInput(0, 4000, 2000, 256, 256,
        new AffineMap2D(1, 0, 0, 1, 0, 0), host.PlanBudget.MaxDecodedTileBytes)],
    host.PlanBudget.MaxPlanTiles, host.PlanBudget.MaxPlanDecodedBytes);
var result = pure.BuildDisplayPlan(input);
if (result.Plan is { } plan)
{
    var center = pure.MapPointer(new DipPoint(500, 300), plan);
    // center: Mapped, ColumnCenter=1999.5, RowCenter=999.5.
    // Pointer mapping is geometry only; it does NOT authorize reading pixels.
    host.ReceivePlan(plan, center);
}
else
    host.ReportPlanError(result.Error, result.Field);
```

### 11.2 两个仅依赖公开DTO/端口的独立Host

最小宿主不构造产品ViewModel，不调用旧内部runtime。以下目标示例仅使用本文公开Module API；`fixture` 是Smoke中**私有**可控端口夹具，shape如下，尚未写产品/测试代码或声明编译通过。

```csharp
// Private test fixture; implementation stays inside existing Smoke assembly.
// FixtureA and FixtureB each implement the SAME public ports, no cross-host VM.
// A: Frame/Coordinate/Authorization/Probe/Roi/BackendFactory/Presentation/IntentSink;
// B: same except no Roi; adds ResourceAdmission Required fake Owner.
var root = new ViewportRootFactory().Create(new ViewportRootOptions(
    RootId: "fixture-A", MaxSessions: 2, MaxTrackedTasks: 64,
    MaxPendingReturns: 32, MaxRetainedBytes: 256L*1024*1024,
    CleanupAttemptBudget: TimeSpan.FromSeconds(2), MaxCleanupAttempts: 2));
var factory = root.CreateFactory();
var limits = new ViewportLimits(4,32,4096,16,32,64,4096,8,128);
IViewportSession? session = null;
try
{
    session = factory.Create(new ViewportOptions(
        "fixture-A", ViewportAccessMode.EditableDraft,
        ViewportFeature.Navigation|ViewportFeature.Probe|ViewportFeature.RoiEditing,
        fixture, fixture, fixture, 64L*1024*1024, 2, ResourceAdmissionMode.BudgetOnly,
        DrainTimeout: TimeSpan.FromSeconds(2), OperationTimeout: TimeSpan.FromSeconds(2),
        Roi: fixture, Probe: fixture, Limits: limits,
        BackendPolicy: BackendPolicy.OfflineRasterOnly, Backend: fixture,
        IntentSink: fixture)); // no Presentation -> headless; no hidden WPF window
    var source = new ImageSourceDescriptor(new SourceId("sample-A"),4000,2000,1,8,false,
        PixelCoordinateConvention.CenterInteger,new CoordinateRevision(1),"r1",
        new HashSet<string>{"gray"},
        new ValidityDomain("frame-owner","r1",new PixelRect(0,0,4000,2000),true,null),
        [new PyramidLevelPlanInput(0,4000,2000,256,256,
            new AffineMap2D(1,0,0,1,0,0),256*256)],"decode-1");
    var auth = new AuthorizationSnapshot("auth-owner","a1",ViewportPurpose.EngineeringDraft,
        ViewportRight.Read|ViewportRight.Probe|ViewportRight.EditDraft,"offline-A",
        DateTimeOffset.UtcNow.AddMinutes(1)); // fixture uses injectable fixed clock in tests
    var context = new ViewportContext(
        [new SourceBinding(SourceRole.Primary,source,null,"group-A")],[],auth,"zh-CN",
        new ApiVersion(0,1),0,ViewState.Fit2D(new DipSize(1000,600),1.25,1.25));
    var attachTask = session.AttachAsync(context,CancellationToken.None);
    var attached = await attachTask;
    if (attached.Outcome == OperationOutcome.Succeeded)
    {
        var viewTask = session.ApplyAsync(new SetViewCommand(
            ViewState.Fit2D(new DipSize(1000,600),1.25,1.25)),CancellationToken.None);
        var shown = await viewTask;
        // Explicitly inspect Outcome/Error/Cleanup; a plan is NOT visible-production evidence.
    }
}
finally
{
    if (session is not null)
    {
        var closeTask = session.DisposeAsync(TimeSpan.FromSeconds(2),CancellationToken.None);
        var close = await closeTask; // preserve task; root retains pending ownership automatically
        // If !Drained, root.GetSnapshot().Pending contains the ORIGINAL tasks/borrowers.
    }
    var rootCloseTask = root.CloseAsync(TimeSpan.FromSeconds(2),CancellationToken.None);
    var rootClosed = await rootCloseTask;
    // Unknown/Pending is a failed/incomplete test, not a successful exit.
}
```

上面预算是标明的合成夹具值，不能迁入生产默认。Fixed clock经私有夹具传给授权端口；Module判断绝对期限使用root可测试时钟注入（§13），不依赖测试机器碰巧快速。代码示例中的 DateTimeOffset.UtcNow 是普通host的实钟，自动测试将context构造的时间换成固定夹具Now。A的factory不从fixture制造“根Owner已接管”的假回执；root在模块中真实保留Task。Create失败时session=null仍关闭root。原操作和finally关闭异常分别记录，测试保留两个错误，不能让finally抛错吞掉初始失败。

Host B的完整公开构造如下；`fixtureB`为Smoke私有FixtureB实例，它准确实现IFramePort/ICoordinatePort/IAuthorizationPort/IProbePort/IViewportBackendFactory/IViewportResourceAdmission（同§3.3/3.5/4.6签名），不实现IRoiPort、不注入Presentation；headless协议测试不伪称HALCON可见。Required假资源Owner只证明协议，真实生产Adapter另验。

```csharp
var rootB = new ViewportRootFactory().Create(new ViewportRootOptions(
    RootId:"fixture-B",MaxSessions:2,MaxTrackedTasks:64,MaxPendingReturns:32,
    MaxRetainedBytes:256L*1024*1024,CleanupAttemptBudget:TimeSpan.FromSeconds(2),
    MaxCleanupAttempts:2));
IViewportSession? sessionB = null;
try
{
    var factoryB = rootB.CreateFactory();
    var optionsB = new ViewportOptions(
        ConsumerId:"fixture-B",AccessMode:ViewportAccessMode.ReadOnly,
        RequestedFeatures:ViewportFeature.Navigation|ViewportFeature.Probe,
        Frames:fixtureB,Coordinates:fixtureB,Authorization:fixtureB,
        MaxDisplayBytes:64L*1024*1024,MaxInFlightTiles:2,
        ResourceAdmissionMode:ResourceAdmissionMode.Required,
        DrainTimeout:TimeSpan.FromSeconds(2),OperationTimeout:TimeSpan.FromSeconds(2),
        Roi:null,Surface:null,Probe:fixtureB,Presentation:null,
        ResourceAdmission:fixtureB,
        Limits:new ViewportLimits(4,32,4096,16,32,64,4096,8,128),
        BackendPolicy:BackendPolicy.HalconRequired,Backend:fixtureB,
        IntentSink:null,UpdateThrottle:null);
    sessionB = factoryB.Create(optionsB);
    var imageB = new ImageSourceDescriptor(new SourceId("sample-B"),4000,2000,1,8,false,
        PixelCoordinateConvention.CenterInteger,new CoordinateRevision(1),"r1",
        new HashSet<string>{"gray"},
        new ValidityDomain("frame-owner","r1",new PixelRect(0,0,4000,2000),true,null),
        [new PyramidLevelPlanInput(0,4000,2000,256,256,
            new AffineMap2D(1,0,0,1,0,0),256*256)],"decode-1",Statistics:null);
    var authorizationB = new AuthorizationSnapshot("auth-owner","b1",
        ViewportPurpose.EvidenceReview,ViewportRight.Read|ViewportRight.Probe,
        "review-B",DateTimeOffset.UtcNow.AddMinutes(1));
    var contextB = new ViewportContext(
        [new SourceBinding(SourceRole.Primary,imageB,null,"group-B",Timing:null)],[],
        authorizationB,"zh-CN",new ApiVersion(0,1),0,
        ViewState.Fit2D(new DipSize(1000,600),1.25,1.25));
    var originalAttachB = sessionB.AttachAsync(contextB,CancellationToken.None);
    var attachB = await originalAttachB;
    // Assert Outcome + Error + Cleanup; fixtureB Frame leases use their own Borrow LeaseId.
}
finally
{
    try
    {
        if (sessionB is not null)
        {
            var originalCloseB = sessionB.DisposeAsync(TimeSpan.FromSeconds(2),CancellationToken.None);
            var closeB = await originalCloseB; // retain pending root/Task; no fake clean exit
        }
    }
    finally
    {
        var originalRootCloseB = rootB.CloseAsync(TimeSpan.FromSeconds(2),CancellationToken.None);
        var rootCloseB = await originalRootCloseB;
        // Any Pending/Unknown or either error axis => incomplete/failed fixture, not PASS.
    }
}
```

A/B以各自固定clock替换示例实钟并保存操作/关闭两个错误，不让finally异常覆盖原错误；在真实host仍使用实钟。两Host可共享同FrameOwner的backing，但每Borrow LeaseId与访问域分别绑定，A取消/关闭不结束B Task，fixtureB.Context不含编辑权，传入其它Roi也不授编辑。B装配表已明确null/非null与Purpose/Mode/Required，不要求开发者从产品名猜准入；实际UI版B另显式开启Presentation并注入其Presenter，按§10.6/10.7绑定验证。三维扩展仍按§8单独验证，不以A/B headless2D证明实际3D/GPU完整。

私有夹具至少有：可控 `TaskCompletionSource<PortResult<IFrameLease>>` 闩锁（RunContinuationsAsynchronously）、唯一OwnerId/LeaseId/backing、固定内容/有效域/原始值、归还记录、被Root观察的Acquire/Submit/Commit/Revoke/Return原Task、晚到成功、失败Value带lease的违约变体、Unknown准入Resolve同请求、重复return冲突，以及以原Task触发的故障。无Sleep猜竞态、不创建生产数据库/设备或UI。发布消费者实现对应公开端口及其Owner合同，不暴露fixture或拿它当HALCON/GPU能力实现。

## 12. 正常、边界和失败案例

| 场景 | 必须结果 |
|---|---|
| 2D 原图正常加载 | 通过 006 租约读取；生成同代显示计划；显示源身份、修订和 LOD |
| 只有 2D、请求 3D | 保持 2D 可用；返回 `CapabilityUnavailable`，不补高度/相机/标定 |
| Fit + 125% DPI | 源中心逆正一致；DIP/物理像素分开；无重复半像素 |
| 非整数缩放、旋转 90°、镜像 | Overlay/命中与图像同代；设计 ID 不变 |
| 当前视野自动 LUT | 回显统计域和实际 min/max；平移不悄悄改对照语义 |
| 原值探针在 0 值像素 | 返回合法 0 和原始索引；不当作失败 |
| 探针落在 mask/未加载/越界 | 返回对应 Invalid/Unknown 原因，不夹到边界、不返回 0 |
| 3D LOD 质心命中 | 仅返回派生/无源映射；无合法映射时只导航 |
| 重叠 Overlay | 按稳定几何 ID 排序或给候选列表，不按结果表行号 |
| A→B 快速换源，A 晚到 | 撤 A 呈现代；丢弃 A 结果并归还租约，B 不被覆盖 |
| A 取消、B 仍等同源 Tile | 只移除 A 等待者；B 可完成；底层不提前释放 |
| 关闭时 native 未停 | 进入 `Draining`，保留 Owner/待释放资源；不在 UI 线程 Wait |
| GPU 丢失 | 撤后端代纹理/拾取；从仍获准源重建；可保留 2D 或原件查看 |
| 撤权后缓存命中 | 入口、命中交付、实际呈现再次检查授权；不交付受限内容 |
| 盲审影像已烘焙结论 | 标记不可盲审或提供原始证据；隐藏 Overlay 不宣称已去除答案 |
| 未装配导出 | 返回 `ExportNotAttached`；不在 Viewport 内写文件 |
| ROI 拖动后坐标修订变化 | 取消手势，不提交半段 patch |
| 非法尺寸/NaN/未知单位 | 原子拒绝，不分配部分资源，不发成功事件 |

## 13. 测试和验收矩阵

测试分为 Core、Adapter、UI 和两个消费者接入；模拟数据只能证明软件行为，不能冒充实机/HIL/工业计量资格。

| 层级 | 必测内容 | 通过断言 |
|---|---|---|
| Core 契约 | null、NaN、无限、未知枚举、尺寸/层数/字节上限、单位缺失 | 原子拒绝；稳定错误码；无租约泄漏 |
| Factory/API 组合 | 缺必需 `Frames/Coordinates/Authorization/MaxDisplayBytes/MaxInFlightTiles/ResourceAdmissionMode`、Required 缺 admission、BudgetOnly 带 admission、预算越过硬上限、未知 feature bit、`RoiEditing` 与 `ReadOnly` 冲突、请求能力缺 port、非空 ROI 但未请求编辑 | `Create` 以 `ArgumentNullException`/`ViewportConfigurationException` 拒绝；不创建后台工作、不取得租约；`EffectiveFeatures` 与请求组合一致；预算不默认、不隐式 clamp；模式与端口组合回显一致 |
| Attach/Dispose | 空 source、Attach 取消/失败、部分租约已取、Dispose 超时、重复 Dispose、取消等待 | 空 source 为 `Empty` 且无租约；失败 session 不可复用；已取租约全部归还；超时为 `Draining` 且列出 pending；后续调用共享同一 drain；调用方取消不停止清理 |
| Core 坐标 | Fit、1:1、125% DPI、奇数尺寸、半像素、旋转/镜像、非整数锚点 | 正逆落同一源位置；错误桥被反例抓到 |
| Core 交互 | 单选、重叠候选、拖动、Esc、旧代输入、文本/IME隔离 | 稳定 ID；迟到结果丢弃；不改业务事实 |
| Core 资源 | A/B single-flight、重复归还、取消、超时、`DisposeAsync`、GPU fence、Required 分配前拒绝、permit 未知/过期、精确 settle、同 backing 单计费、冲突/重复 release | 借用中不驱逐；计数恰好归还；真实 Drained；未获 permit 不分配；actual bytes 不超过批准值；无证据不退款；重复调用幂等、冲突隔离 |
| Core 3D | 无映射 LOD、体素质心、w 退化、透视、遮挡、多面相交 | 只读降级或明确 Unknown；不冒充原索引/Z |
| Adapter | ImageLibDotNet 公共签名、HALCON 26.05 算子参数/row-column/线程、后端丢失 | 仅使用已确认能力；不猜签名；错误可诊断 |
| ROI Adapter | 020 几何类型、洞/岛、旋转矩形、单位、修订冲突、草稿提交 | 统一校验入口；无轴对齐替代；失败保留原草稿 |
| WPF UI | 键盘、UIA、主题、三语、DPI、固定视口内窗口恢复、长文本 | 真实 UI 状态正确；无重叠/遮挡；命令可访问 |
| 回放 | 同一源/参数/库/坐标/授权快照重播，A→B 晚到，GPU/解码故障注入 | 显示计划、事件、错误和资源回执可重复比较 |
| 消费者一 | 独立测量工具：2D/3D查看、探针、受控 ROI 草稿 | 无 UI Core 与可选 UI 使用同一语义；不写质量结论 |
| 消费者二 | 复判/生产工作台：只读证据、稳定目标切换、权限/盲审、关闭恢复 | 不引用对方 VM/私表；复判意见/放行仍由宿主拥有 |
| 现场资格 | 实际相机/表面/标定/性能/HIL | 单独记录；未执行不得写生产通过 |

每项测试保留输入身份、修订、Profile、环境、结果事件序列、资源峰值和失败原因。不会因为“画面出现”就跳过身份、授权、迟到、排空、未知值和可回放验证。

### 13.1 测试落点、目标命令与有限截止

**工程尚不存在**（2026-10-28 审核更正）：旧措辞称"当前唯一Core工程和验证Exe已经存在"、"2026-10-10只读核对了Program.cs"、"这是真实工程命令"。该批代码已随 `c4e10cf`（2026-10-26）整体移除——`src/Asun.UI.Viewports/` 与 `tests/Asun.UI.Viewports.Smoke/` 在当前仓库**均不存在**，与本文件第 24 行"两个工程均须在切片获授权时创建"一致。以下命令是**切片获授权并创建工程后**应执行的目标命令，不是当前可运行的命令，本轮亦未运行。

历史事实仅供追溯：移除前的 `Program.cs`（2026-10-10 只读核对）逐项执行既有 smoke、汇总 failures，失败 return 1、成功 return 0，且当时**没有** case/suite 筛选与总截止。实施切片在新建工程的 `Program` 中应保留该"逐项执行 + 汇总 + 失败非零"的行为，并加入下表入口参数；不新建空 TestHost 或重复测试工程，不声称 `dotnet test` 会执行此 Exe。

```powershell
dotnet build .\src\Asun.UI.Viewports\Asun.UI.Viewports.csproj -c Release
dotnet run --project .\tests\Asun.UI.Viewports.Smoke\Asun.UI.Viewports.Smoke.csproj -c Release
```

上述是**目标工程命令**（工程当前不存在），**本轮未创建工程、未运行构建/Smoke**。新增契约用例的目标参数为 `--suite viewport-contract --case <ID或all> --case-timeout-ms <正整数> --suite-timeout-ms <正整数>`，实现前入口不支持这些参数，不得传参后误称只跑了切片。默认不传参数必须包含所有适用已绑定断言；未知case/suite、缺必需项、超时/未完成/跳过均非零。case失败打印ID+操作/清理双轴+原Task及lease终态，suite执行器观察每个原Task，计数仅完整断言完成才加成功。测试内部case和suite有独立有限截止（夹具计划采用case10s、suite120s，仅测试护栏不是模块性能目标）。外层进程180s超时：允许用已有CI/进程runner参数，不新增脚本；没有runner时用PowerShell Start-Process -WindowStyle Hidden 执行同一dotnet命令，WaitForExit(180000)，逾期停止该测试子进程并return非零。不可把杀测试进程/WaitAsync取消当产品资源释放。

### 13.2 两个复核视角的可判定用例

| case ID / suite viewport-contract | 输入/受控动作 | 核心断言 |
|---|---|---|
| VP-C01 normal/empty | §7.2矩阵、空Sources、零canvas | center与DPI正确；空不取lease；零canvas无旧矩阵 |
| VP-C02 large/odd | 2百万图、513×257 tile256、右边界恰为512 | double区分0.01；半开range/尾1×1；无全图列表/bytes越界 |
| VP-C03 weak/mask | 全常量、NaN/Inf、遮挡洞、插值4支撑之一invalid | 中灰/Unknown明确；0不作失败；invalid支撑不造值 |
| VP-C04 degenerate | 奇异矩阵、w退化、空点云/无三角、未知major | 无NaN/单位阵默认；NoHit/Blocked和源说明；旧包可回退 |
| VP-C05 candidates/ROI | 两重叠对象、反ZOrder、洞/岛、非矩形手势 | 稳定priority/ID顺序；候选不自动提交；同geometry类型/修订 |
| VP-C06 changes | view/LUT/LOD/语言/权限变化、A→B→C逆序回应 | 只呈当前C；LUT不改原值；旧pick失效；语言不取新帧 |
| VP-C07 3D/link | 可见/遮挡候选、LOD源映射缺、Z倍率、2D-3D/A-B回显 | 从027原值读取；缺mapping仅导航；联动一次无echo |
| VP-L01 concurrent/cancel | A/B共源single-flight，取消A后释放B；重复关闭 | A不影响B；每lease恰好归还；旧源权利不泄漏 |
| VP-L02 deadline/original | Acquire/Submit超时后闩锁晚回lease，再Return迟到 | 原Task持续登记；Pending占预算；晚lease被归还，非drained回执 |
| VP-L03 close/dispatcher | UI/renderer借用未退出、Revoke排队后关页 | no early Return/Drained；原Dispatcher/Presenter Task由root持有 |
| VP-L04 permit/unknown | TryBegin超时无permit、Resolve原请求、Started创建异常 | 无分配绕行；同IDResolve；Started不能AbortUnstarted |
| VP-L05 cleanup/transfer | Return Pending/Unknown、有限尝试耗尽、根槽不足 | 原Return不重复；Query同ID；接管确认独立于Drained；两轴错误保留 |
| VP-L06 callbacks/revoke | 订阅者抛异常/重入、提交前撤权、源断连 | 锁外有序事件、不漏终结/lease；无缓存敏感内容；有限Retry |
| VP-L07 root-issued binding | Created代0 Reserve/Start；跨root同名session；旧代child；关闭前armed控制槽；Start前拒绝 | 无host构造Context/Scope/Task；拒绝不InvokeAsync；清理已关门可用；Started不得Abort |
| VP-U02 self-wait/late | Bind先空安装再Attach；Control等Work原worker/children；原Acquire晚成功；UI timeout/OwnSession关闭 | Bind不等Attach；root强持原Dispatcher/Presenter/Return；Control不等自身/Session/Root；slot外OwnSession有限剩余预算 |
| VP-H01 two consumers | §11.2两个root，shared帧Owner，各自Mode/Budget/AccessDomain | 公开DTO可构造、无产品引用；编辑不传染；关A不关闭B |
| VP-U01 two STA | §10.6 Bind/Unbind、三语/IME/UIA/固定视口 | 独立UI切片，真实WPF证据；Core夹具不能替代 |
| VP-G01 golden | §13.3独立字段拼接与fixture/plan编码 | 全字节/hash相等；任何矩阵/Tile/修订变动可定位 |

模拟时间/闩锁由Smoke私有实现驱动，Root模块构造允许internal TimeProvider注入给Smoke，friend-test程序集名固定为Asun.UI.Viewports.Smoke（按现有csproj默认AssemblyName），仅实施时在受测工程添加该声明，发布公共RootFactory仍无参且TimeProvider.System；不用改系统时钟。不把假fence、假VisibleConfirmed、合成lease计数称GPU/现场事实。必要真实HALCON适配tests在其受影响工程slice独立执行，Core先以私有端口控制协议。

### 13.3 小型矩阵/Tile Golden（定义与独立复算）

仅为显示计划投影定义固定136字节编码 `PlanGolden1`，不将Runtime Lease/授权opaque/用户凭据持久化。按字段顺序拼接：ASCII `VPPLAN1` + NUL（8字节）；M11/M12/M21/M22/Tx/Ty各IEEE754 binary64 LE；VisibleSourceBoundary Left/Top/Right/Bottom四binary64 LE；TileRange ColumnStart/ColumnEndExclusive/RowStart/RowEndExclusive四int64 LE；Generation一个int64 LE；LevelId与flags两个int32 LE。flags bit0=WasClamped、bit1=BudgetDegraded，其余必须0。finite值，-0规范为+0；无文本culture/JSON重排，NaN/Inf拒绝。Encoding长度固定8+48+32+32+8+8=136。

固定合成投影：source4000×2000，crop全图、canvas1000×600、DPI1.25，level0比例1/tile256、generation1，Fit矩阵 `(0.25,0,0,0.25,0.125,50.125)`，visible `(0,0,4000,2000)`，range `(0,16,0,8)`，LevelId=0、flags=0。Fixture预算保证该level可接纳，没有其它level。其完整规范字节hex：

```text
5650504c414e3100000000000000d03f00000000000000000000000000000000000000000000d03f000000000000c03f000000000010494000000000000000000000000000000000000000000040af400000000000409f40000000000000000010000000000000000000000000000000080000000000000001000000000000000000000000000000
```

SHA-256=`28c9d1e432a41e58f9b5850540a3737b724debd0f3d2d8ca283d7d53d2c05c91`。2026-10-10本轮在内存用Python struct固定字段逐项LE拼接独立复算长度/hex/hash，未生成文件；只证明定义相等，不证明C#实现。未来Smoke的expected由独立字段常量拼接，actual由受测planner/编码器输出，不能两端调用同一serializer生成golden。另断言§7.2中心逆映射和tile半开边界，不仅比hash。

## 14. 性能预算和可观测性

### 14.1 预算指标

最终数值由消费者 PerformanceProfile 冻结；实现准备阶段至少测量并报告：

- 首个正确原图/可用 Tile 的冷启动、热启动延迟（P50/P95/P99）。
- 拖动/缩放到实际呈现的 P50/P95/P99；合并刷新不能掩盖业务选择事件。
- Tile 解码/上传并发、队列深度、取消到排空延迟。
- CPU/GPU/在途 Tile/Overlay/UI 复制的峰值 bytes；大图复制次数。
- 3D LOD 切换、拾取、GPU 丢失重建和长期运行的资源趋势。
- 两个 Viewport 并发、同源 single-flight 命中率、缓存驱逐和拒绝次数。

每个宿主必须在 `ViewportOptions` 显式提供 `MaxDisplayBytes`、`MaxInFlightTiles` 和 `ResourceAdmissionMode`；除离线 BudgetOnly 外，实际 backing 的逐次准入、结算和释放回执必须由 Required 端口完成。模块只执行 §4.4 的硬拒绝上限，不提供固定默认值，也不把资源预算当作性能目标。显示更新合并窗口没有默认值，在消费者 PerformanceProfile 获批前保持 `TargetPending`。未按真实负载验证前不得声称任何性能目标达标，也不得把单机微基准外推到整板或生产吞吐。

### 14.1.1 可执行BenchmarkProfile的模块负载与失败口径

消费者Profile须冻结：ProfileId/revision、Core/API/backend/DX/HALCON版本、输入与hash、tile/pyramid/decode/坐标/几何版本、像素格式、有效域比例、图层/几何/LOD数量、视口/DPI/源角色、单/双Host并发、冷/热与预热n、测量n/最低有效n、request/close有限deadline、root/session/CPU/GPU/UI/inflight/queue硬上限、时延目标与来源、后台worker数、目标刷新合并窗口及失败处理。Profile缺上述政策值时拒绝Qualification，允许有明确有限诊断负载的NotEvaluated测量；不填造生产阈值。

模块专属负载分别为4000×2000单图Fit/1:1/锚缩放、513×257尾块、最大允许宽高的窗内Tile、大量叠加/洞岛、原16位/float探针含缺值、双源overview/currentFOV固定/跟随、3D同源LOD切换/pick遮挡，以及A取消/B保留、backingUnknown、慢Dispatcher/GPU丢失/关闭。每组需消费者实际代表样本，合成仅验证有界及协议。对纯Plan统计调用至返回；对Session/呈现使用**有限case**：接纳→计划→source→decode/upload→提交→实际可见→case主动撤该呈现→backend/Presenter退出→源Return确认→ResourcesReleased。保持显示时OperationCompleted只是提交耗时，不冒充GOV010资源归还端到端；不能让持续持有的呈现被从分母删去。

统一分位及样本处理直接采用DEV-GOV-010 §3.1，不另写另一种算法；报告各阶段、完整排空端到端P50/P95/P99/n、取消→真实排空/归还、root pending与物理ledger两轴峰值。失败、不可见、未读、超时/删失、Root未收敛分别保留；根未知不判性能通过。实际可见由真实WPF/后端证据，软件mock或Dispatcher.Task完成仅为诊断阶段。输入预算超限在调用前拒绝为断言，非时延PASS；目标缺失NotEvaluated，资源硬界破坏或未完成case记失败。长稳时长/样本计划来自消费者Profile，不将文中8h/24h例子当通用上线门。

### 14.2 结构化诊断

每个操作记录：`traceId`、`operationId`、`consumerId`、源/层/对象 ID、来源/坐标/几何/显示修订、状态、实际视图/LOD、授权代摘要、队列/租约/内存计数、后端代、耗时和错误码。日志不得记录 token、原始图像、未授权文本或完整客户数据。

指标至少包括：

```text
viewport_operation_total{operation, outcome}
viewport_operation_duration_ms{operation, quantile}
viewport_stale_result_total{source, reason}
viewport_tile_inflight / viewport_tile_queue_depth
viewport_memory_bytes{cpu,gpu,decode,upload,ui}
viewport_resource_drain_seconds{outcome}
viewport_backend_failure_total{backend,capability}
viewport_probe_unknown_total{reason}
```

诊断是投影，不成为业务事实；`ResourceLeakSuspected`、持续排空超时和后端代失效必须触发宿主可见告警。

## 15. 版本兼容、适配器、发布和回退

### 15.1 兼容策略

- Core 公共契约使用语义版本：新增可选字段/能力为 minor；改变单位、坐标约定、有效性、事件顺序、资源所有权或删除字段为 major。
- 模块Context/CallContext用ApiVersion(0,1)，Source/Coordinate/Geometry/Context修订按公开类型传播；Core API不等待全局Schema字段。未知Major或高于已支持Minor拒绝；minor增加可选字段仅在新版能力清单声明后允许。没有序列化的runtime事件跟随session创建版本，不混用另一major。
- 版本迁移必须是纯函数、可回放、可逆（若语义允许），不得把旧 WinForms `.roi` 二进制直接当平台格式；旧格式只能由明确 Adapter 解码成候选草稿并标来源/版本。
- AsunImage、HALCON、DevExpress 版本按项目固定依赖使用；不在本模块安排安装、授权或内部兼容审查。实际 API 变更由适配器能力矩阵和编译/定向测试发现。

### 15.2 适配器边界

端口的唯一 C# 声明见 §3.5 与 §4.6，不在版本章节复制旧 FrameLease/SurfaceLease 候选。端口参数含 CallContext 和剩余有限预算；根持有原 Task，租约归还必须有Owner回执。平台006/007/020/027的公共接口通过消费Adapter映射到这些模块端口，不把实际平台DTO版本当Core API名称。HALCON/native对象不泄漏到Core/事件/日志；各后端借用和呈现契约见§4.6。

#### 15.2.1 V-A1来源、身份与权限绑定（本版可确定部分）

本节只定义消费Adapter如何使用上游已公开契约，不新增Core DTO、不替上游批准接口。只读依据为：[image-frame 0.3.2-prep §4.3/4.4/7/19.1](../image-frame/DEVELOPMENT-GUIDE.md)、[coordinate-geometry 0.3.3-prep §4.3/7](../coordinate-geometry/DEVELOPMENT-GUIDE.md)、[roi-geometry 0.4.1-prep 附录A.1/A.3/A.4/A.6](../roi-geometry/DEVELOPMENT-GUIDE.md)、[surface-data 0.6.0-prep §2/3/3.1及§15.2～15.9；H/S增量消费见本页§15.2.7](../surface-data/DEVELOPMENT-GUIDE.md)。其API分别为Resources v0.1/Core v0.2/Tiles v0.1、坐标v0.2、ROI v0.3、Surface v0.4及独立Contribution v0.1；版本不是viewport ApiVersion(0,1)。本文不以其它模块接收状态推定运行；本次只读的Surface C1～C5与坐标A～E规格接收不证明真实桥已运行。

宿主装配时建立**有界、不可变、Adapter私有的binding快照**，不是另一份源事实库。它保存以下原对象/引用与本端口字段的一一对应，受MaxSources/MaxLevels/MaxGeometryPoints及root字节预算约束；只读缓存来源，不生成上游修订。公开端口签名仍唯一见§3.5/4.6。

| 本端口字段 | binding必须保留的上游值 | 绑定/拒绝规则 |
|---|---|---|
| SourceId/SourceRevision | image FrameKey(Guid,ulong)、完整FrameDescriptor或TiledFrameDescriptor；SurfaceKey(string,ulong)及完整SurfaceDescriptor | 宿主显式提供对应关系；Ordinal比较，完整内容冻结。SourceRevision是本地引用token，禁止从文件名或裸revision猜来源；同token不同内容拒绝016，不取latest |
| CoordinateRevision/FromSpace/ToSpace | 坐标GraphSnapshot.Ref、Frame/Edge AssetRef(Id,ulong,Hash)、ExplicitPath、NumericPolicy；image CoordinateReference、Surface FrameReference/MappingReference、ROI RoiFrame | 以显式binding将本地非负long token关联到完整原引用；禁止ulong强转long、截断或只比较Id。换graph/frame/path/policy必须换binding与本地坐标token；二维轴/手性/中心约定逐项匹配 |
| GeometryRevision/ObjectId/GeometryAssetRevision | ROI DocumentId、Snapshot.Revision(long)、Node/Component/Ring/Vertex稳定ID、Source/Support/Profile；Region另保留租约Info/Grid/Method/Representation及原物化回执 | 有且仅有本binding确认的文档/对象；不能用数组序号或hash替NodeId。一个OverlayPayload只装同文档修订；文档修订可逐值投影long，源修订/资产修订分别保留 |
| Generation/AuthorizationRevision/AccessDomain | 当前root-issued CallContext与IAuthorizationPort回执；SurfaceReadRequest.Generation为checked正ulong投影 | 显示代是viewport执行身份，不替源修订；Created代0不能读源。ConsumerId、ContentHash、Profile或Calibration引用均不授业务权限 |
| OwnerId/LeaseId/BackingIdentity | 真实服务实例/ServiceEpoch、原Lease.Id、AllocationCharge(AllocationId,Kind,Bytes)；原请求与归还回执 | OwnerId由宿主绑定实例；Guid按固定D格式编码并保留原Guid，不丢epoch。不同借用不同LeaseId，同allocation保持同backing；不同服务的偶然同Guid不能合并 |

读取/Probe/EditDraft/Export先核§4.7当前权限与访问域，原Task完成后、呈现/Intent交付前再次核generation与授权；撤权不取消资源归还。上游没有业务授权服务，由宿主IAuthorizationPort承担，不从上游ConsumerId推断Read。修订失配分别返回005（显示代）、006（坐标）、004（源不可用）或016（同身份不同内容）；缺能力007、无权限008，均不触发更宽松backend。

所有上游ValueTask只调用一次AsTask，保留这一原Task，不重复await原ValueTask；本端口的组合Task及每个原调用均沿§4.6.1已预留、root签发的BackendAdapter Work/Control槽登记，真实数量含Submit/Wait/Cancel/Query/Release/Dispatcher。工厂/调用在额度预留之后启动。服务借用和已接纳操作另作为Adapter私有的零字节IViewportLease责任凭据由slot.RetainLease登记，防止WaitTask结束却丢掉仍在运行的上游操作；其Return/Query规则按下面对应Owner，不能把此凭据叫物理allocation。有限观察返回Unknown后，root仍持有原实例/操作关联/责任凭据及尚未归还资源，不重复Submit/StartRead或关闭共享服务。

#### 15.2.2 image-frame → IFramePort/IFrameLease与原值读取

**Acquire的唯一源方法。** 驻留level0用`Asun.Modules.ImageFrame.Resources.IFrameService.ReadAsync(FrameReadRequest,ct)`；多层/随机tile用`Asun.Modules.ImageFrame.Tiles.ITiledFrameSource.ReadTileAsync(TiledReadRequest,ct)`。源/cache实例由宿主借用注入，viewport不Publish源、不创建第二缓存Owner。TileColumn/Row乘绑定TileWidth/Height，checked得到level内CoreWindow；尾块裁到层实际尺寸，再checked转PixelWindow的int字段。没有正面积/超过int/能力或预算时在读前拒绝。新借用生成新Guid RequestId，固定ConsumerId与原ServiceEpoch；重复请求只回原receipt、Slice=null，不是新lease，查询不会重新交付对象。

显示请求Intent=Display，Boundary=ClipAndMarkInvalid；Halo来自已冻结的插值支撑（最近点0、bilinear所需邻域1），不能由Adapter任意放大。探针OriginalSample改用原level0的ExactSamples与RejectMissingSupport；Interpolated只向原层请求完整支撑，不能从DisplayOnly LOD取测量原值。无效/缺支撑沿§7.6返回MaskInvalid/SupportInvalid/Outside，缺tile004，不填黑块或零灰度。decode token精确绑定ContentHash/DomainRevision/层GenerationMethod/ParameterRevision/ToSource及Adapter版本；来源没有发布某层时不临时猜层或完整解码大图。

**布局与域。** 初始无损CPU路径只接一个选择plane（SinglePlane，ChannelCount=1），或一个同类型Interleaved plane；Scalar UInt8/UInt16/Int16/Float32/Float64逐名映射PixelSampleKind，ByteOrder映LittleEndian，Width/Height/StrideBytes由返回局部Layout逐值取得。Int32、异构多plane、Planar多通道不能挤入一个PixelLayout，装配前007；宿主可显式发布选择plane的视图binding，不改变原源。Adapter私有IFramePayload保留完整Layout/Metadata/SourcePlaneIndices/CoreWindow/ActualWindow及原lease；OffsetBytes/RowBytes/AccessibleBytes不丢失，也不把padding当标量。需要拆通道/native深复制属于明确的后续适配子门，不静默转换。

有效域为Layout.Domain与各选中PlaneMetadata.ValidDomain的交集，Full/Empty/RowSegments逐项保留；Rows是`[StartXInclusive,EndXExclusive)`。Viewport ValidityDomain.Boundary是源半开包围边界，**不是mask**；FullBoundaryValid只在整个该边界均有效时true，否则MaskAssetRevision引用binding保管的完整域快照。IFrameLease.ValidSourceBoundary是ActualWindow经层角映射所得源边界、裁到源尺寸；不能把带孔域改成Full或只用包围框接受原值。CPU scope.CopyRow使用局部Y与选择plane局部索引，复制标量字节到已预留缓冲；scope及CopyRow真实退出后才能归还原lease。Probe值=`raw*Metadata.Scale+Bias`，unit/channels按Metadata逐值匹配；灰度unit=1，Height仅本契约可表达的已声明单位，未知单位007，域外NaN不当有效值。

**层中心公式。** 上游PixelMap给正ScaleX/ScaleY及OriginXCorner/YCorner，level中心到源中心的平移为`OriginXCorner+0.5*ScaleX-0.5`（Y同理）。所以PyramidLevelPlanInput.LevelCenterToSourceCenter=`(sx,0,0,sy,ox+sx/2-0.5,oy+sy/2-0.5)`，注意viewport六数顺序。返回tile局部中心再加ActualWindow.X/Y：TileCenterToSourceCenter平移=`ox+sx*(ActualWindow.X+0.5)-0.5`和Y同式；halo起点可能不同于CoreWindow，不能用请求tile起点代替。奇数5×3→3×2为sx=5/3、sy=3/2，第一中心映到(1/3,1/4)，不是(0.5,0.5)。半开边界按`ox+sx*levelBoundary`映射，不再减0.5。层生成路线仍归image-frame；`IHalconFrameAdapter.PublishDisplayLodAsync`只发布结果Frame/Layer，没有返回tile lease或完整金字塔。结果须由宿主用新ResultKey/完整层描述装配后再走Read；完整Full强度/颜色、weighted/ceil链等限制沿上游，不用于Height/Mask/缺域/Float64，不完整导入超大图。

**租约与归还。** 此CPU路径恰一个真实AllocationCharge；BackingIdentity编码Owner实例+AllocationId，RetainedBytes为charge.Bytes（不是窗口字节），同Id必须同Kind/Bytes。多个不同charge但单一BackingIdentity无法保真重叠去重，初始路径007，不能把它们随意拼hash当一个allocation。LeaseId关联Owner实例+原Id，SourceRevision/Generation用本次binding/call值；root只管自己的借用，不与上游缓存账相加作RSS。

ReturnAsync先封payload新scope、等backend/Presenter/本地CopyRow实际退出，然后只启动一次原`lease.ReleaseAsync(request.Budget).AsTask()`。该上游方法没有ct；本端口ct只停止有限观察，不中止释放。ReturnId保留至本scope责任确认归还；重复同ReturnId读原记录，不生成第二析构；QueryReturn先观察原Task；它未退出时不能再次调用上游Release。原Task已真实退出但只给观察期内Draining时，Control可在同ReturnId下有限调用同一上游lease的幂等ReleaseAsync取得新观察回执（其公开契约明确重复调用不再次析构），保留每个新观察原Task/回执，不能重新开scope/创建lease或改关闭身份。此为QueryReturn内部的关闭事实观察，不重发本端口ReturnAsync，原回执不改写；次数受CleanupAttemptBudget/MaxCleanupAttempts。只有ReleaseReceipt.LeaseId匹配、LeaseClosed=true、Error=None、Drain=Drained才Returned，StorageReleased=false合法（源池/其它消费者仍持有）。Draining→Pending、DrainUnknown/释放异常→Unknown，保留原lease/scope/Task；没有公开QueryRelease，不能捏造该方法。原Task已结束且新有限观察仍Pending/Unknown时保持留账；释放异常若Owner不能确认只保Unknown，属于真实归还/恢复门，不用LeaseClosed退款、不要求上游另造QueryRelease服务。源操作Unknown查询原`QueryOperation(serviceEpoch,requestId)`，NotFound/epoch变化均不能证明没执行；未交付lease的迟到/未知源责任凭据仅在原receipt确认OperationResourcesReleased/真实Drain后归还。

##### 15.2.2.1 公开CPU发布源生产者与预装配（BC-U1）

前文描述了私有payload的内容，但旧版没有可由外部Host调用的生产者；不能把实现义务误写为已提供入口。本版冻结以下可选适配包，负责把**已经PublishCopy成功的image-frame源**接到内置renderer，不负责BarcodePixelBuffer、decoder、生产采集或像素发布。未来唯一落点`src/Asun.UI.Viewports.ImageFrame/Asun.UI.Viewports.ImageFrame.csproj`、namespace `Asun.UI.Viewports.ImageFrame`、net10.0，引用Viewport Core、image-frame Core/Resources及BCL；不加WPF/HALCON依赖到Core。本轮只定义，不创建工程。内置WPF renderer引用该适配包，通过模块内受控读接口识别其私有payload（适配包仅向`Asun.UI.Viewports.Wpf`开放内部读取成员）；Host不引用内部类型，不按类型名反射、不把任意marker当合法像素。现有外部backend仍可消费自己的payload。

```csharp
using System.Collections.Immutable;
using IF = Asun.Modules.ImageFrame.Resources;
using VP = Asun.UI.Viewports;
namespace Asun.UI.Viewports.ImageFrame;

public sealed record ViewportImageFrameSourceOptions(string ConsumerId,
    int MaxBindings, long MaxRetainedMetadataBytes);
public sealed record ViewportPublishedFrameBinding(string BindingId,
    IF.FrameDescriptor Frame, VP.ImageSourceDescriptor Image,
    ImmutableArray<int> PlaneIndices, string PixelSpace);
public interface IViewportImageFrameSource
{
    VP.IFramePort Frames { get; }
    VP.ICoordinatePort Coordinates { get; } // explicit same-pixel-frame identity ONLY
    VP.PortResult<string> Register(ViewportPublishedFrameBinding binding);
    VP.PortResult<string> Remove(string bindingId);
}
public static class ViewportImageFrameSourceFactory
{
    public static VP.PortResult<IViewportImageFrameSource> Create(
        IF.IFrameService source, VP.IViewportProcessRoot root,
        ViewportImageFrameSourceOptions options);
}
```

**预装配与映射。** Create传实际借用source实例/原ServiceEpoch、同消费root及在source.ResourceLimits预登记的read ConsumerId；返回的Frames/Coordinates实例稳定，供Create session的Options使用。它不Publish/Read/Subscribe/启动Task，不创建root、源缓存、renderer或service，不取得service所有权；Host强持至本scope所有原任务/lease收敛。ConsumerId和BindingId非空UTF8≤128；MaxBindings为1..65536，MaxRetainedMetadataBytes>0且由Host原Profile预留，单entry的字符串/levels/domain/元数据计数按ViewportLimits与image-frame原限额预检，checked合计实际保留上界后才深冻结，超限003不边复制边超账。root须是本模块factory返回的同实例，不以同名root当同Owner；Frames.Acquire只接受该root签发并仍有效的原call，Core与适配包内部核签发关联不向Host开放伪造凭据。Create不读来源来补消费者登记；第一次真实Read由image-frame再次校验ID/额度，未登记不得偷偷注册。

Register仅同步验证并冻结调用方已取得的完整PublishResult.Frame（成功Completed/Error=None/OperationResourcesReleased由发布Owner核实后传入），与Image.SourceId/SourceRevision逐值一致；Frame.Key非空/Revision正，Image.CoordinateRevision正；Frame.CoordinateReference必须精确等于明确PixelSpace，不猜FrameId或文件路径。CPU首版必须恰一个plane索引0、level0原Width/Height、identity层中心映射、有限正tile和decoded bytes，Full或原完整域保真；scalar/channel/bit数/布局/metadata/validity沿本节原规则，超出首版（多层、选择另一plane、异构/Planar、多allocation）007，可继续使用前文已有其它明确Adapter路线，不假称此工厂支持。Gray8/Gray16/RGB8分别单plane UInt8×1/UInt16×1/UInt8×3 Interleaved，原bytes不量化/换通道。Frame/Layout/Metadata返回Read时再次与冻结源描述对应，误传未发布/错误Key/错域/epoch拒绝，不靠Register成功证明源真实存在。

BindingId同值同完整内容幂等返回原ID；同值异内容016。同SourceId可注册两个不同SourceRevision以容纳替换，查找键精确为SourceId+SourceRevision+CoordinateRevision+DecodeRevision；同键歧义016。Frames将FrameRequest映到该entry的原FrameKey及ConsumerId，调用前文ReadAsync；新Read Guid、完整窗口/halo/plane等不变，private payload只由本工厂的实际原ReadResult.Slice创建。原ValueTask一次AsTask进入同root签发child，失败Value/迟到lease仍由extractor捕获；未知源operation保原epoch/request身份并QueryOperation，禁止用新RequestId重读绕Unknown。服务CPU scope退出前不得Return，原Release/Query/StorageReleased=false语义沿本节原合同。

Coordinates仅接受SourceId对应冻结entry、request.Revision匹配、FromSpace=ToSpace=该entry.PixelSpace、所有有限2D点且Z=0，返回同Points/同Revision/LengthUnit.Pixel及全true Valid。Read权限由session入口及交付点检查，源读取还核AccessDomain等于原授权domain；非identity/未知frame/3D/缺绑定006，不冒标定、不新增坐标求解。Register同SourceId+CoordinateRevision在新旧版本的PixelSpace必须完全一致，否则016，避免CoordinateRequest没有SourceRevision而歧义；跨frame仍按§15.2.3原坐标Owner装配独立ICoordinatePort，此源工厂Coordinates不必使用。

Remove不Retire源、不Close/Dispose service、无异步工作；仅当该entry所有源Read原Task/未知operation、local scope及lease实际Returned，且Host已经通过空更新或合法替换解除当前Context引用，才允许移除。内部待借用计数不为零则Rejected/015，未知返回Unknown/013；尚活跃Context即使暂时0个lease也拒绝移除：模块内部按同root所持session的冻结Context与实际Frames实例做有界使用核对（最多Root.MaxSessions个），不靠Sources.Count=0或Host布尔承诺。Core只向本适配包开放内部只读使用核对能力，Host不访问私有Context/根表；活跃时015，不加新的公共Root接口。成功只释放本adapter metadata登记，不证明原storage退款；未知时保entry占容量。同BindingId已移除重复Remove只确认此adapter无该entry，不代替曾经的Return/Retire证据。Host若过早Retire上游key导致之后Read失败必须原样报错，不从别的key补图。持续换图复用同Frames实例：Register新revision→Update→旧借用确认Return→Remove旧BindingId→由发布Owner Retire旧key，不把每次Publish后的新IFramePort塞入已经冻结的Options。

**两个独立STA Host的准确预装配输入。** 以下为本适配公开能力的合成软件装配规格，不重写barcode自己的factory/原请求；其独立display lease→IFrameInputRows→PublishCopy/Retire仍归barcode原Owner。复用其§8.6.3限额/来源/授权与§10.8固定1920×1080验证，目标调用顺序如下。

| 公开输入/步骤 | Host A | Host B |
|---|---|---|
| 借用源服务 | `new Asun.Modules.ImageFrame.Resources.FrameServiceFactory().Create(sourceLimits,new Asun.Modules.ImageFrame.Core.ManagedLayoutValidator(),TimeProvider.System,null)`成功Service；原limits明确注册`label-display/publish`及`label-display/viewport`，ServiceEpoch保存 | 独立factory/service/epoch，注册`logistics-display/publish`及`logistics-display/viewport`；同值限额也不是同实例 |
| root/producer预装配 | 原rootId=`barcode-label-viewport`；`ViewportImageFrameSourceFactory.Create(service,root,new("label-display/viewport",2,1048576))`，核Succeeded+Value并强持sourcePorts | 原rootId=`barcode-logistics-viewport`，read consumer改logistics；2 entries/1MiB metadata为显式Synthetic上限，源描述实际越界拒绝 |
| 同Control renderer/session | new ViewportControl→原ViewportRendererFactory.Create(control,root,OfflineRasterOnly/64MiB Raster/2 submissions/2s)；Options.Frames=sourcePorts.Frames、Coordinates=sourcePorts.Coordinates、Presentation=同control.Presentation、Backend=同renderer.Backend；ReadOnly+Navigation\|Presentation、BudgetOnly、64MiB MaxDisplayBytes、4 in-flight，其余原Options/limits完整提供 | 完全独立Control/Dispatcher/root/renderer/session，同行数值；生产Host沿原Required/HalconRequired及已采纳Profile，不套离线权限 |
| Bind与Publish | Catalog.Get成功完整资源；Lifetime=同renderer.Lifetime、UI budget=(67108864,32,32)、OwnSession=true，原Bind先登记；随后本方独立Acquire→PublishCopy成功完成→原provider lease退出 | 同顺序，不借decoder/A的lease；Publish和service的Owner为本Host，不变更viewport Root/Close |
| 注册输入 | `sourcePorts.Register(new(bindingId,原Publish.Frame,完整ImageDescriptor,[0],原Frame.CoordinateReference))`；ImageDescriptor为16×16/Gray8、level0 tile256/identity/MaxDecodedTileBytes=65536、CenterInteger、Full域、同source/coordinate token及DecodeRevision，Channels={Gray} | 16×16/Gray8同合成源可比；另以RGB8/Gray16源验证首版无损接受，不混改A数据。Read key/源tokens均取B自己发布值 |
| 首次呈现与后续 | 第一次Register成功后`session.AttachAsync`一次；source role=Primary，Timing=null。之后Register新entry并`session.UpdateAsync`全量替换；Clear成功后仍Update，不重Attach/Bind | 同路线；SourceId/Revision/FrameKey不能跨Host交叉，重叠对象选择用§4.5.1，Clear用§4.7.1 |

两个Host source limits/profile/root/canvas/AuthorizationSnapshot/InputFrame完整值仍取barcode原Host已冻结输入，本表不造新的业务帧/授权。像素坐标PixelSpace必须是Host显式保存的ImageFrame Id+Revision的无碰撞受控引用，FrameDescriptor.CoordinateReference、geometry目标和source binding三者同义且有原文映射。权限Check用其原Host授权实现，不能让该producer签授权。原源没有统计时不扫描全图补min/max；这些Gray8合成Host显式令InitialView.Lut=`new LutWindow(0,255,"display-range/uint8/1")`，Gray16用(0,65535,"display-range/uint16/1")，这是手动显示格式范围而非测得extrema/自动建议；RGB8走原三通道色彩路线。自动LUT仍需原Owner完整统计，缺统计不能拿null当可自动显示的承诺。

barcode的`IBarcodeViewportPublishedSourceFactory`是其本方接口，不是上述上游类型；它的Host实现只需持有一次已Create的sourcePorts，在Create(binding,同service,同root)时核精确实例、逐字段Register，并返回这同一Frames/Coordinates。不得每帧另造producer/service/root，或假定私有BarcodePixelBuffer实现IFramePayload即可被内置renderer接受。此映射由barcode永久原会话修入其唯一指导；本节只提供可调用公共生产者与输入，未代修该模块。

#### 15.2.3 coordinate-geometry → ICoordinatePort

MapAsync绑定到`Asun.Modules.CoordinateGeometry.ICoordinateGeometryService.SubmitAsync`，请求为`GeometryRequest("0.2",原RequestId,new MapWork(冻结Graph,SourceRef,TargetRef,ExplicitPath,GeometryBatch,NumericPolicy),剩余预算)`；ContractVersion固定为上游§4.1的`0.2`，不能从viewport ApiVersion自动格式化。Batch/Graph/Policy本地内容引用按上游coordinate-core-values-v1规约取得，不篡改外部SourceRef.Hash。宿主在本binding提供合法完整值快照/来源，Adapter不注册新Frame、求标定或更改路径。点列表顺序不变，2D用Point2Value且输入Z必须0，输出Point3D.Z=0；3D用Point3Value，禁止在缺PlaneLift/深度时升维。目标frame单位Pixel/Micrometre/Millimetre对应本端口Pixel/Micrometer/Millimeter；Nanometre/Metre尚不能用本端口原样表达，007或由坐标Owner提供明确同单位目标frame，不能只换标签。矩阵已含换单位比例，Adapter不再乘1000；Center/Corner与轴变化由已选图边负责，不额外补半像素。From=To仍须已登记frame及明确identity路径。

Submit返回Accepted/Duplicate后按原ServiceInstanceId/RequestId调用WaitAsync，WaitExpired/WaitCancelled只是观察结束；用QueryAsync回查同一实例。调用取消/到期只一次CancelAsync，Control继续有限Query/Wait，不调用借用服务StopAndDrainAsync影响其它消费者。零字节操作责任凭据的Return发该Cancel/Query路径，只有该操作终态且Drain=Confirmed、ResourcesReleased已成立才能Returned；Unknown/NotFound不销账。root留全部原ValueTask转换的Task以及原引用/预算，有限观察耗尽不以新ID重跑。

仅Completed+Confirmed+MappedResult精确匹配Graph/Policy/Backend/Source/Target/输入身份、输出count/次序/点类型并全部有限，才返回CoordinateResult(原Revision,原ToSpace,目标单位,Points,全true Valid)。上游是整批域/数值验证，不逐点部分成功，不能将failed batch伪装成部分false+其它有效点。失败返回无可消费Value：CG002/003/004/005/006/015/016/018→006，CG017/019→007，CG001/014→002，CG007→003，CG008→009，CG009→010，CG010→011；CG011/013或lookup不确定→PortOutcome.Unknown并留操作凭据，CG012→004，CG020→006并保原诊断。Error.Field/Stage/RecoveryKey保原定位及安全原码，不把Unknown改成NoMapping成功。

#### 15.2.4 roi-geometry → IRoiPort与可选WPF桥

**唯一Owner输入。** 以`Asun.Modules.RoiGeometry.GeometrySnapshot`完整文档和Profile为基线，NodeId映ObjectId，文档Revision映GeometryRevision；RoiFrame由binding明确映到source整数中心frame。物理文档经已发布坐标关系投影；本HitTest接口只有仿射SourceToDip，非仿射/缺映射006，不在Adapter复制几何解算。完整文档保留Parent/Visible/Locked/ZOrder/Constraints/Source/Support和Component/Ring/Vertex ID，不能从屏幕RoiGeometrySnapshot重建这些事实。

RoiGeometrySnapshot的Width/Height为完整轴长、AngleRadians在源(column,row)数值平面逆时针参数，矩形/完整椭圆半轴为`U=(W/2*cos(a),W/2*sin(a))`、`V=(-H/2*sin(a),H/2*cos(a))`；物理Y到屏幕Y换基在DocumentToViewport。原Rectangle/Curve保留原U/V不往返重新造轴；用Width/Height/angle只能表达的正交形状作为显示投影，任何舍入后不满足上游精确正交门的编辑候选按其Validate拒绝，不能自动正交化。开放Curve、非正交Curve基、Point/Segment、Group不是当前扁平Kind的无损投影，007或由原ROI Owner发布显式有误差界的显示表示，不能冒称原Ellipse。Polygon当前编辑映射限一个Outer及其直接Holes，Polyline保稳定顶点；多Component/洞中岛的扁平Rings缺组件关联，禁止从它重建编辑候选。它们可走保留完整Snapshot的上游WPF桥显示/编辑，不能以最大component替代。Region仅GeometryAssetRevision关联A.4真实lease/物化，不把opaque字符串当Runs。

HitTestAsync调用`IRoiGeometryInteraction.HitTest(HitTestRequest,Profile,ct)`：用binding完整Snapshot、当前SelectionSet，DocumentToViewport按字段名映Affine2D（顺序M11,M12,Tx,M21,M22,Ty），ViewportPoint为DIP、ToleranceDip原值，Mode=Point、ViewportBox=null、MaxCandidates=CandidateLimit、Deadline由剩余单调预算。上游排序原样保留，NodeId/LayerId显式绑定，Locked仍可选只读；DistanceDip不重算。上游超过MaxCandidates拒绝，不截断成功，所以映射SelectionResult.Truncated=false；AmbiguousCandidates是距离误差/选择歧义，**不等于Truncated**，本SelectionResult没有歧义字段，不能捏造Notice出口；此扁平导航通道对任何非空列表均要求用户明确选择，不自动取首项，精确歧义提示走A.6原HitTestResult投影。Handle/Vertex/Edge的ElementId/Part及ErrorBoundDip由Adapter保留，导航列表可按完整有序首候选去重NodeId，不能据丢失的ElementId启动局部编辑；精确编辑入口用下面A.6桥。空文档Completed+空候选是正常空值。

ValidateDraftAsync把Proposed按原稳定ID转换为typed ReplaceCommand，保持其它节点/约束/出处，构造临时完整Snapshot调用`IRoiGeometryCore.Validate(RoiValidationRequest,ct)`；再用同Commands/BaseRevision/Profile/Epoch调用`PreviewAsync(RoiEditRequest Mode=Preview,ct)`验证锁、约束、CAS与编辑语义。期限不重置，原Preview ValueTask只AsTask一次；QueryOperation核原receipt/current Adoption，只有PreviewReady、IsTerminal/ResourcesReleased、Candidate非空且当前CanAdopt才Valid。CreateCommitCandidateAsync复核同draft/generation/授权/binding，返回root关联的有界CandidateId及原Draft/ExpectedRevision，并在Adapter保留原Preview/完整Candidate，**不调用Apply或ICommitPort**。候选不表示已写入ROI文档/产品事实；持久化或真正应用由宿主IntentSink交原Owner确认。RG错误保原Code/FieldPath/RecoveryKey：RG-001/002/003/004/017→002，RG-005→006，RG-006/018/019→007，RG-007/011→003，RG-008/020→005（这是该操作基线失配，非自动覆盖），RG-009→009，RG-016→010，RG-012→002，RG-013→004，RG-014确定失败→011、未确认资源或RG-015→Unknown。验证失败RoiValidationResult.Valid=false可作为成功完成的验证结果，通知保留原因，不冒称提交成功。

Region要调用`IRoiGeometryLease.MaterializeAsync`取得受限Vector/Runs，只在Completed/IsTerminal/ResourcesReleased后用原Frame/Grid投影；RoiRun.EndColumn是闭端，checked加1转半开，Grid origin/step不能省略。物化回执的ResourcesReleased只指临时物化，不等native lease归还；本方独占借用用原Lease.DrainAsync确认Drained+ResourcesReleased，未确认保原lease及回执，不能Dispose借用的整个Backend/Core。通用连续点映射走坐标Owner，Region离散变换走ROI backend；viewport不写第二套ROI布尔/栅格化算法。

**A.6桥的双端接线。** 可选宿主Adapter实现上游`Asun.Modules.RoiGeometry.Wpf.IRoiEditorViewportBridge`：View是本次已绑定ViewportControl的UIElement，PublishOverlay按DocumentId/GeometryRevision/FrameId/ViewRevision/Sequence核binding，预留Dispatcher原Task后有界入队，不回调ROI Core/Editor。返回true仅表示接收投影，不等VisibleConfirmed；false不回滚ROI已应用事实。Snapshot/Preview分别映正式/草稿叠加，Selection保原NodeId；不能把Preview作为产品事实。Host构造RoiEditorAttachRequest，调用IRoiEditorControl.Attach/RefreshProjection/ProcessPointer/SetPermissions/SetPresentation/DetachAsync，使用同一binding/验证逻辑；三语主题由Host传，不另放语言入口。

Projection.DocumentToViewport字段取同一冻结矩阵，ClientBoundsDip取真实中央绘图区；ViewRevision由宿主局部非负long单调分配并绑定viewport DisplayGeneration+计划/画布，不能直接把两个revision当同一东西。任何view/source/geometry变化先取消旧gesture再RefreshProjection。Pointer从中央视图原WPF事件保Phase/Button/Control/Shift/Alt相对DIP传ProcessPointer，不从缺修饰键的PointerSample反造事件。CanEdit来自EditDraft权限，CanSave由宿主持久权限另定，撤权立即取消且交付前复核。关闭先Editor.Detach真实完成、撤overlay/解除View父关系，再Viewport.Unbind，最后由Host按各自所有权关闭Core/root；Detach超时保原Task及pending，不借控件Unloaded证明退出。桥只在可选WPF DLL/宿主适配，Core不引用UIElement/ROI Wpf程序集。

#### 15.2.5 surface-data → 描述/有界读取映射及不可越过的能力边界

SurfaceDescriptor.Key/Frame/Grid/Unit/VertexIndices/FaceIndices/Buffers/Fields/Origins逐字段冻结到binding，SurfaceRevision关联完整Key及描述。LengthUnit.Micrometer/Millimeter对应本端口同名值；Meter无法直接表达本端口ZUnit，先由Owner提供目标单位描述或007，不能把meter标成mm。Surface数据的物理Unit/Frame不证明HasPhysicalCalibration；该布尔只来自宿主明确资格引用，缺资格仍不放计量。VertexCount不是“有效原样本数”，SurfaceValidity.OriginalSampleCount按声明样本域计数，HasInvalidSamples/MaskAssetRevision保显式state域；未知/未扫描不能自称全有效。AvailableLods/误差上界/SourceMappingRevision不来自SurfaceDescriptor v0.4，由§15.2.5.1的viewport显示模型Owner按已冻结算法生成；不得仅看到SurfaceDescriptor就填LodId=0冒充已读/已构建。

可确定的读取链为`ISurfaceDataService.Plan(SurfaceReadRequest)`→`StartRead(request,ISurfaceBlockConsumer,ct)`→保留StartResult.Operation及其**原Completion Task**。SourceRange半开、FieldIds含真实位置/属性及依赖、Selection=PreserveAll、ReadCoordinates=true，TargetFrame/Transform来自准确binding；HeightField Grid先用`ParentColumnOffset+localColumn`、`ParentRowOffset+localRow`中心经Grid.Mapping到源Frame，XYZ已有源坐标。同Frame Transform=null，不同Frame需显式MappingReference；v0.4不跨长度单位，不能从viewport相机/model矩阵求物理坐标。只有Positions属于CoordinateFrame，PackedValues仍是源Frame属性，不换整块标签。

OnBlock只同步短计算/复制到**读取前已预留且明确Owner的有界显示副本**，拷贝Positions/字段state/reason/origin/SourceIndices/Ordinals，禁止把ref struct/Span给Dispatcher或异步保存。块是暂存；仅Completion.Outcome=Completed且Completeness符合完整请求、Errors空/未截断/输入Key与Generation匹配后采用，失败/取消/超时整批失效。原Completion完成证明surface本次读session/临时资源退出，**不证明消费者显示副本或backend/GPU已归还**；其DisplayLease须独立Owner确认。原Source session由surface操作清理，viewport不再次Dispose它、不Close共享ISurfaceDataService。操作取消用RequestCancel，Observe只有限等待；读取责任凭据等待原Completion真实退出才归还。

SourceIndices是long精确值，OriginalIndex字符串用InvariantCulture十进制无前导零编码，binding另保SourceIndexBinding.Root/Kind/OrdinalBase/FieldId与Vertex/Face domain，不通过double或屏幕点序号。OriginId查完整OriginEntry，Observed/Interpolated/Repaired/Filtered/Cad/Fallback2D/Unknown及MethodId/MethodVersion/ParametersSha256/Parents原样保留在私有payload/evidence binding。Observed且声明精确原索引才可给OriginalSample的一项weight=1；派生HasExactParentIndex=true只能证明单父Root一对一，仍保其派生来源，不能升级Observed。多父/插值/质心没有逐样本贡献表时不制造weight=1或最近原点，SurfaceHit只能NoMapping/NavigationOnly，不交付可测量的Support。Invalid/Unknown位置保state/reason/origin、NaN及缺口，不能转Z=0有效点。

**责任裁决。** surface-data v0.4没有四个viewport同名服务，**不构成四项内部设计的上游阻断**。AcquireLod/显示副本lease、当前窗口拾取、浏览剖面和显示ROI投影属于viewport消费Adapter。它们用上述公开只读块/原索引/坐标Owner，按下面步骤实现；不新增Surface持久事实、修改其Core或实现专业计量。真实HALCON/GPU/WPF/性能资格另验。

##### 15.2.5.1 AcquireLod：有界完整快照、源保真LOD与本地DisplayLease

Adapter私有冻结配置（宿主显式注入、非Core新DTO）包含Source/Coordinate/ROI binding、显示OwnerId、完整载体N/F与CPU字节上限、MaxPickPrimitives、MaxReadOperations、HALCON/backend baseline容量、允许的LOD列表`(LodId,DistanceSourceUnit)`、默认LodId和有限工作/清理预算。源索引不作为采样率；LOD0 Distance=0，其它Distance有限>0且递增，由显示Profile提供，不能在运行中降值迁就性能。输入Key/Domain/方法/单位/坐标/Profile/backend版本改变新建binding与SourceMappingRevision，旧lease不换内容。

1. 在Plan/StartRead前检查N/F、`3*F`和各数组长度可checked表示且受MaxGeometryPoints/本配置/root预算；完整读取顶点域Ordinal[0,N)、PreserveAll，ReadCoordinates=true，TargetFrame=源Frame（Height仍需Grid Mapping）；Mesh再读取Face域[0,F) TriangleIndices，ReadCoordinates=false。用同一完整expected描述、原buffer摘要与binding完成这两个独立operation。Surface Source已承诺不可变expected快照，两个session可以安全拼同修订；描述/hash失配或任一读取失败整批丢弃，不要求额外跨operation snapshot API。读取总数与字节计入共享递减预算，两次OperationLimit均取当前剩余期限，不能各自重置全预算。
2. 预分配本Adapter独有SoA显示副本：XYZ double[3*N]、CarrierOrdinal long[N]、RootIndex long[N]、State byte[N]、Reason uint[N]、OriginId int[N]、CarrierToRender/RenderToCarrier int[N]，payload上界`57*N`；Mesh另有triangle long[3*F]、FaceOrdinal/RootFaceIndex long[F]、State/Reason/Origin和双向int映射，上界`57*F`。可选颜色列按真实编码另计，不先复制所有属性。读取暂存块同时存活计SurfacePlan.ResidentUpperBound，输出/LOD tuple与新旧模型并存另计，不把Source内部峰值相加冒充RSS。数组payload是确切容量，CLR头/allocator/native内部为baseline/实测范围。只在所有Completion均Completed、DeliveredItems=RequestedItems且Errors为空/未截断（N/F=0对应Empty，其余Complete）后采用；无效样本保State/Reason/Origin，不填坐标。
3. 对Valid位置建立连续render index→载体ordinal→精确RootIndex映射；原数据及long索引仍在私有快照。HeightField显示为点云，不自动跨洞三角化；PointCloud同路。Mesh只使用上游已有TriangleIndices（当前vertex ordinal，不是RootIndex），核范围/三点不重复/位置有效，无效face显式跳过并记显示缺口；不修网格。剔除无效vertex后用CarrierToRender重映face，不能把0..N索引误作compact索引。已有mesh检查按Surface StartInspectMesh的原Owner流程，缺拓扑资格只阻相关完整表面/计量声明，不自写修复器。
4. HALCON主路`cv2.gen_object_model_3d_from_points`创建显示点模型，源mm乘1e-3、um乘1e-6显式转native meter；这只是native边界，SourcePoint仍为原源单位，不改Surface Frame/原值。Mesh用`set_object_model_3d_attrib_mod`设置`triangles`，精确compact整数且长度3*有效face数。点模型附`&vp_carrier`扩展属性，值是本地int carrier token（严格<=int.MaxValue，可精确double表示），不是long RootIndex。LOD0保全部Valid原点、误差0；点云/Height粗LOD用`sample_object_model_3d(...,'fast',distanceInMeter,[],[])`，不算normals、不用产生质心的accurate、不把mesh采样成面上新点。官方fast保留原点和扩展属性；随后`get_object_model_3d_params`读取token及XYZ，逐项核token唯一/范围及坐标与原载体一致，异常011/016，不最近点猜源索引。所有源点到保留点的距离小于等于该distance，故该层源单位几何覆盖误差保守取DistanceSourceUnit；非uniform显示倍率下按完整展示矩阵的保守投影界应用§8.4，不能直接按ZMultiplier同比缩一切误差。点云层不声称连续面的覆盖或孔内观测。TriangleMesh首片仅LOD0，不使用simplify/面采样伪造原点映射；超预算003，后续mesh简化须单独定义贡献/误差，不能称缺Surface服务。
5. Acquire每次产生独立本地显示backing与DisplayLease（无隐藏全局cache/共享池）：OwnerId=宿主绑定的viewport显示Owner，LeaseId/BackingIdentity为本次预留的独立身份，RetainedBytes是本方CPU容量+已登记显示baseline受控借用量。模型tuple/native句柄只在私有ISurfacePayload及串行backend，不进Core/日志。原Surface读session已随Completion退出，DisplayLease拥有上述本地副本/LOD/native模型；不是“027外借lease”。所有native对象创建前预留HALCON baseline/最大同时模型与tuple量，按§4.4.1准入；baseline不伪装逐对象精确allocator报价/退款。失败/取消/迟到保原Task，实际HALCON算子退出后逐个clear_object_model_3d及tuple Dispose，CPU借用消失后释放本方引用/准入；释放异常Unknown不重用backing。
6. ReturnAsync原子封新payload借用，等本lease的profile/pick/overlay/Renderer/Dispatcher全部真实退出且Revoke确认脱离，启动一次本地关闭Task；clear所有本方native model、释放本方CPU强引用并取得本Owner准入归还证据后Returned。Storage源池仍存活不影响它；GPU/window baseline由backend Owner确认，未确认Pending/Unknown。QueryReturn观察同一ReturnId/原关闭Task/本地关闭状态，可在真实callback退出后发布确认，不重新读取Surface或关闭共享服务。两个Acquire lease完全独立，A返回不得清B；按旧/新并存上界预留，无容量在读前拒绝，不因独立复制能运行就声称大模型性能已合格。

官方版本依据：本项目[gen_object_model_3d_from_points](../../../halcon算子手册/operators/gen_object_model_3d_from_points.html)、[set_object_model_3d_attrib_mod](../../../halcon算子手册/operators/set_object_model_3d_attrib_mod.html)、[sample_object_model_3d](../../../halcon算子手册/operators/sample_object_model_3d.html)、[get_object_model_3d_params](../../../halcon算子手册/operators/get_object_model_3d_params.html)、[clear_object_model_3d](../../../halcon算子手册/operators/clear_object_model_3d.html)。只读26.05算子语义，不核封装覆盖；具体C#tuple/句柄封送确有歧义才查公共签名/消费编译，属于对应V-A2调用门。

##### 15.2.5.2 Pick：当前可见primitive到精确载体/原点

`ISurfacePort.PickAsync`由本Adapter与同一串行backend私有桥调用，沿当前DisplayLease借用，不从Surface另读屏幕深度值作高度。先核请求Source/Surface/Coordinate/Generation/BackendGeneration/CameraRevision/画布及呈现身份；原可见呈现撤销或不支持精确同参数pick pass时NoMapping。backend负责把§8.4当前DIP/矩阵映为HALCON实际CamParam/Pose/窗口part；普通4×4不能直接充CamParam，不能映为同一投影的backend只导航。这是内部backend资格，不是Surface新增API门。

1. 冻结本次呈现的所有可遮挡源/显示模型（不只被选Source）；用同一DisplayModel/Z倍率/WorldToCamera/Projection投影当前LOD点及mesh三角角点，坐标换到固定canvas DIP。点的候选包围框按本次实际point_size覆盖、三角按投影AABB包围（近面交叉/齐次不确定候选只标不可可靠拾取，不错误判NoHit）。候选需覆盖指针且数量<=min(CandidateLimit,MaxPickPrimitives)，扫描工作/输出受root/剩余期限；超限003，不截断成“最近一个”。不确定投影返回NoMapping/Ambiguous，不把后方面强行升候选。
2. 主路线使用受控、同尺寸的HALCON离屏pick窗口，保留普通可见窗口不改其persistence；与本次呈现相同CamParam/Pose、part、opaque/point_size、面裁剪参数及所有遮挡源。仅将有界候选primitive逐项独立为1点模型或3点+1triangle模型，其余primitive保持分组模型且**删除已拆出的candidate**，保证无重叠重复表面。离屏native模型/窗口及分组副本最大量在调用前计入独立backend baseline与root槽；不足在pass前003。透明/不支持一致栅格覆盖的呈现不走此pick，不用不透明替代。设置object_index_persistence/depth_persistence=true，`disp_object_model_3d`完成后在窗口part内按官方edge中心约定`get_disp_object_model_3d_info(...,'object_index')`取当前可见对象。返回-1为NoHit；非candidate分组遮挡为NoHit/NoMapping，不穿透；candidate索引查本次临时映射，而非把model index当原点序号。depth只核当前pass存在/可见性，不作原Z；不查询过期可见窗口残留buffer。
3. 点candidate由LOD token回本地完整原坐标、State/Origin/RootIndex。仅Valid+Observed及精确Root绑定返回OriginalSample、SourcePoint原值、Support=[(RootIndex,1)]；缺每点精确父证据NoMapping（仍可显示），不把派生点升级Observed。位置单位为源mm/um；撤显示Z倍率或model不会改变这些原值，因为它们直接取未显示变换的快照。
4. face candidate由临时model→原FaceOrdinal→3个CarrierOrdinal/RootIndex。只处理三个顶点在同一合法未跨near/w裁剪chart、非退化投影的opaque face；用屏幕三角二维重心λ和三个clip w得到透视校正`β_i=(λ_i/w_i)/sum(λ_j/w_j)`，边界不确定/分母退化或负权拒绝/标歧义，不夹紧洗成合法。这是已可见primitive的DTO贡献换算，不是新视觉命中算法；可见性仍由HALCON pass决定。SourcePoint=sum(β_i*原XYZ_i)、Kind=Interpolated、Support三个精确RootIndex与β，同Root合并权重并保原3顶点/evidence；三个载体必须Valid且拥有可追溯Observed源值，否则NoMapping，不能从最近点恢复未知贡献。Mesh LOD0保证三角来自原已有拓扑，不返回面上插值为OriginalSample。超CandidateLimit/同面歧义不得质量自动选择。
5. 结果交付前复核代/授权，finally等pass调用真退出后clear临时candidate/分组模型并关闭本pick窗口，再归还本DisplayLease借用；pass失败/原native未退出为Unknown/011，root保留。普通窗口仍保其呈现borrow，不因pick成功清它。真实可见窗口与离屏pass覆盖一致、遮挡/裁剪/兼容模式/point-size/DPI是V-A2真实验收，未验不能标Pick qualified。

官方[get_disp_object_model_3d_info](../../../halcon算子手册/operators/get_disp_object_model_3d_info.html)仅提供object_index和camera Z depth，没有point/triangle原索引；因此需要上述临时primitive-index桥，不能凭此算子造原索引。这一选择保持HALCON可见性Owner，不另写CPU ray/栅格化引擎作未比较备用。

##### 15.2.5.3 ReadProfile/ProjectOverlay：规则高度场的显示采样

首片浏览高度采样针对HeightField；PointCloud无Grid和Mesh任意方向投影不猜规则网格，Profile/Overlay该用途007，需要消费者明确截面/表面关联后才扩展viewport显示Adapter（不是Surface同名服务外门）。HeightField无需新增源接口：可以复用已拥有的完整DisplayLease快照，或按SurfaceRange.Tile读取所需邻域；后者每点/合并tile数<=MaxReadOperations且共享剩余期限，先Plan全部需求并预留上下游峰值，再StartRead，所有Completion成功才采用。snapshot/读取仍绑定同expected Descriptor，原样State/Reason/Origin/RootIndex保留。

**唯一高度采样内核。** binding明确源Frame→父整数中心frame的已发布逆路径，`ICoordinatePort.MapAsync`得到父col/row，减Grid.ParentOffset得到本地中心；没有合法逆路径/域则NoMapping，不能从显示矩阵猜pitch。原样本模式取`floor(c+0.5),floor(r+0.5)`（恰半格取较大整数），检查范围/state，从真正原Height/Positions取值并向前用Grid映回实际样本XY。Interpolated模式取floor中心的四邻，按`(1-tx)(1-ty),tx(1-ty),(1-tx)ty,tx*ty`；零权支撑不要求域外邻点（最后整数中心合法），正权全部须在域且Valid/有原值。Invalid支撑为MaskInvalid、Unknown为SupportInvalid、尚未读取的tile为NotLoaded，不跨孔连接、不外推/填0。Height=权重原高度和，SourcePoint的XY取请求源XY、Z取该高度；Support只由精确Observed Root索引和本显示核实际权重组成，来源不具备逐样本证据则NoMapping而不伪造原父权重。Profile.HeightUnit从源单位mm/um映Millimeter/Micrometer，不显示为专业计量结果。

ReadProfileAsync固定输入SourcePath>=2、相邻点非零、MaxSamples>=2，均为源frame/单位的finite 3D路径；PathPosition为**输入路径**累计三维欧氏长度（未显示Z倍率），不是测出的剖面长度。按这一长度均匀取MaxSamples个参数点，包含两端，逐段线性插值输入XY，再调用同一原值/双线性内核；输出SourcePoint取实际高度，PathPosition仍为输入路径参数长度，不用其高度重算长度冒称测量。SamplingMethod固定`height-grid-nearest-v1`/`height-grid-bilinear-v1`并绑定源/坐标/参数revision，Invalid样本保null Height、对应Validity与断线。path超过域不clamp；点数、读次数、数组字节/时间在执行前受限，失败整批无可消费Profile；旧剖面是否保持按§8.5当前权限规则。

ProjectOverlayAsync以原ROI Owner完整几何binding为源：Polygon/Polyline取原稳定顶点/环，Rectangle按原Owner四角；完整Ellipse用`IRoiCurveTessellationPlanner.Suggest`的Segments/GeometricErrorBound与Profile之后只生成其参数式显示顶点，不新选拟合/细分算法。ROI源(frame/unit)→Surface源XY走已发布坐标路径；每条环/线在源frame内分段，显示Profile明确的MaximumOverlaySegmentLengthSourceUnit>0和MaxProjectionPoints限定`ceil(segmentXYLength/limit)`等分，所有增加点数在复制/读取前checked总计。参数是显示采样密度，不证明两点间物理域连续有效；每个点用同一Height内核，输出Points+逐点Valid，穿孔/未知断开，不补桥。两有效采样端点不证明中间无孔：需要连线时以同binding的坐标service对原Segment2Value做全段域映射验证（上游CG v0.2已公开），获得合法父grid线段，再对该线段穿越的所有闭支撑像素cell作有界supercover枚举（DDA从端点floor(c/r)起，比较下一整数网格边的参数t，恰交corner同时检查两侧和对角cell；沿边检查两侧；每cell取bilinear正支撑邻点，边界零权按前述规则；以`3*(abs(floor(c1)-floor(c0))+abs(floor(r1)-floor(r0))+3)`checked保守预占cell次数，每cell再最多4个支撑；参数t比较用原binary64的精确dyadic交叉乘，不用epsilon漏corner；超过上限拒绝），正支撑State全Valid且映射/有效域完整才可连线；该枚举只核已知grid支撑，不拟合/解算变换。非线性模型不能返回可证明全段表示、cell枚举超预算或任何未知时，插入Valid=false分隔点并Closed=false，只画独立有效点/已确认子段，不因稀疏取样把洞两端连接。显示采样误差仍不授物理资格。每Outer/Hole/Component各一SurfaceOverlayProjection，顺序严格按binding保留，Closed取原环类型；返回列表及私有几何ID关联同Source/Surface/Geometry/CoordinateRevision，不将所有环拼一条。Region先取ROI公开有界边界/materialization，缺离散边界资格007，不按GeometryAsset字符串画包围框。最终屏幕投影仍按§8.4，不把隐藏边作为可见pick；无连续域证明的显示线只作采样预览，不作为测量/观察覆盖证据。

**C5上游增量已接收。** 2026-10-11主控明确接收surface-data `0.5.1-prep` Contribution API v0.1/C5六项文档规格；本页以该接收指令及上游§15.2～15.9公开契约为基线，不因上游页首尚未同步接收状态重复退回。此前未接纳的旧候选已作废，唯一调用是`SurfaceContributionFactory.Create`→`IContributionReader.Plan/Start`→`IContributionOperation.Completion`与`IContributionPageConsumer.OnPage`。下面V-A1-C5冻结消费桥，不更改C1～C3、U1及V-A1既有接收；Observed/无Contribution路径保持，不要求所有拾取都依赖C5。

##### 15.2.5.4 V-A1-C5公开消费桥与身份/状态

本片只把**已记录的逐carrier贡献、父原值和已发布坐标链**装配成viewport预览/回溯输入；不重建权重、不替换当前carrier显示坐标、不递归展开祖父支持，不取得计量/质量放行。上游字段/CSR唯一权威见[surface-data §15.2～15.9](../surface-data/DEVELOPMENT-GUIDE.md)；不在本页复制其解码器。以下是viewport消费Adapter自身的**目标公开API规格**，不是上游新增方法、现成程序集或已编译示例。

唯一未来Adapter工程/namespace为`src/Asun.UI.Viewports.SurfaceData/Asun.UI.Viewports.SurfaceData.csproj`、`Asun.UI.Viewports.SurfaceData`，`net10.0`，引用既有Viewport Core、surface-data Core与BCL；IM007通过既有ICoordinatePort消费，不在Core增加上游/产品引用。已有Smoke在获准该片实现时显式引用此Adapter，仍是唯一Exe，不建第二TestHost。该片绑定不授权本轮建工程/写代码。factory/Create无IO、后台任务或UI初始化，深冻结有界请求/配置；对所借上游reader/service/ports不取整体关闭权。

```csharp
// In Asun.UI.Viewports.SurfaceData; alias avoids the two LengthUnit enums.
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using Asun.UI.Viewports;
using SD = Asun.Modules.SurfaceData;
using SC = Asun.Modules.SurfaceData.Contribution;

public enum SupportParentUse
{
    PreviewValue, Invalid, Unknown, NoMapping, UnsupportedDomain, PermissionDenied
}
public sealed record SupportParentBinding(
    int ParentSlot, SourceId SourceId, ImmutableArray<string> FieldIds,
    bool ReadCoordinates, CoordinateRevision CoordinateRevision,
    string FromSpace, string ToSpace, string? QualificationRef);
public sealed record SupportBridgeRequest(
    SourceId CarrierSource, SC.ContributionReadRequest Contribution,
    CoordinateRevision CoordinateRevision, SD.FrameReference? TargetFrame,
    ImmutableArray<SupportParentBinding> Parents, bool RequirePositions);
public sealed record SupportBridgeLimits(
    int MaxOperations, int MaxParents, int MaxParentReads,
    int MaxCarriers, int MaxEntries, long MaxCopiedBytes,
    long MaxTotalReadBytes, int MaxWorkTasks, int MaxControlTasks,
    SD.ResourceBudget ValueBudget, TimeSpan ExecutionBudget, TimeSpan CleanupBudget);
public sealed record SupportBridgePorts(
    SC.IContributionReader Contributions, SD.ISurfaceDataService CarrierValues,
    IViewportParentSnapshotPort Parents, ICoordinatePort Coordinates,
    IAuthorizationPort Authorization, IViewportResourceAdmission? ResourceAdmission);
public sealed record ParentSnapshotRequest(
    SC.ContributionParentReference Expected, SourceId SourceId,
    SD.ResourceBudget VerificationBudget);
public sealed record ParentSnapshotPlan(
    string EvidenceOwnerId, string EvidenceRevision,
    long MaxReadBytes, long MaxRetainedBytes);
public interface IViewportParentSnapshotLease : IViewportLease
{
    SC.ContributionParentReference Reference { get; }
    SD.SurfaceDescriptor Descriptor { get; }
    SD.ISurfaceDataService Reader { get; }
    ParentSnapshotPlan Confirmation { get; }
    long VerificationReadBytes { get; }
}
public interface IViewportParentSnapshotPort
{
    // Pure lookup of explicit immutable owner binding; no hashing/Open/IO.
    PortResult<ParentSnapshotPlan> Plan(ParentSnapshotRequest request);
    Task<PortResult<IViewportParentSnapshotLease>> AcquireAsync(
        ParentSnapshotRequest request, CallContext call, CancellationToken ct);
}
public sealed record SupportFieldValue(
    SD.FieldDescriptor Field, ImmutableArray<byte> PackedValue,
    SD.SampleState State, uint Reason, int OriginId);
public sealed record SupportParentValue(
    SC.ParentContribution Recorded, SC.ContributionParentReference Parent,
    SD.SourceIndexBinding RootBinding, long RootIndex,
    ImmutableArray<SupportFieldValue> Fields, SD.PositionValue? SourcePosition,
    Point3D? TargetPosition, SD.IntegrityScope ValueIntegrity,
    SupportParentUse Use, string? QualificationRef);
public sealed record SupportCarrierRow(
    long CarrierOrdinal, string? CarrierFieldId, int ActualOriginId,
    SC.SupportState State, SC.ContributionMethod Method,
    ImmutableArray<SupportFieldValue> CarrierFields,
    ImmutableArray<SupportParentValue> Parents);
public interface IViewportSupportBatch : IViewportLease
{
    SC.ContributionDescriptor Descriptor { get; }
    SC.ContributionReceipt Receipt { get; }
    ImmutableArray<SupportCarrierRow> Rows { get; }
}
public interface IViewportSupportOperation
{
    Task<PortResult<IViewportSupportBatch>> Completion { get; }
    void RequestCancel();
    Task<ExecutionObservation> ObserveAsync(TimeSpan budget, CancellationToken ct);
}
public interface IViewportSupportBridge
{
    PortResult<IViewportSupportOperation> Start(SupportBridgeRequest request,
        IViewportProcessRoot root, IViewportSession session, CancellationToken ct);
    Task<CleanupSnapshot> CloseAsync(TimeSpan budget, CancellationToken waitToken);
}
public static class ViewportSupportBridgeFactory
{
    // Target specification; provide body only in an authorized implementation task.
    public static PortResult<IViewportSupportBridge> Create(
        SupportBridgeLimits limits, SupportBridgePorts ports);
}
```

`Start`先检limits/请求/版本、精确Carrier/Contribution binding与当前session Attach/Generation/授权；请求Generation必须checked等于当前正DisplayGeneration，CoordinateRevision与所有父映射binding同当前图修订token。ParentSlot binding恰覆盖Descriptor.Parents、不重复，FieldIds非default/非空且有界、Ordinal唯一；RequirePositions时TargetFrame=Carrier.Frame且能以本viewport mm/um单位表达、所有参与位置的parent必须Vertex及ReadCoordinates=true。对Face/字段审计RequirePositions=false、TargetFrame=null，可读取拓扑/Attribute而不假造XYZ。调用者不得持锁并发修改集合。

Start同步只校验已持快照/纯Plan/本地额度并创建root reservation，实际IAuthorizationPort.CheckAsync、C5/C2 Start/父Acquire/坐标调用全部在已armed的Work异步委托里；不得同步阻塞Start或声称同步已调用实时授权。Work对全部Carrier/parent SourceId请求Read，点位置消费另要求Probe，Field审计仅Read；Root/session最新Snapshot与端口Authorization.OwnerId/Revision/AccessDomain/ExpiresAt再次一致才启动来源。ResourceAdmission=null只允许session明确离线BudgetOnly，Required必须同宿主资源Owner且Create/Start拒绝缺失；本Adapter不另换宽松模式。Start失败不启动任何上游IO；若失败发生在已armed执行中，返回operation并用其Completion/cleanup轴报告，不能将已启动动作伪装为未接纳。

operation关联先在bridge本地预留一个bounded内部批号，C5 Start可能在返回operation之前进入OnPage；回调只核已冻结generation/descriptor并暂存第一个OperationId，在Start返回后以Operation.Snapshot.Id/随后Completion.OperationId复核同一Guid，不因尚未取到operation而丢首page。若两个Guid/页序不一致整批Conflict；不把回调中引用的尚未赋值变量当公开调用保证。Work.StartOriginal的factory内执行一次C5 Start并返回它的原Completion（拒绝时返回已确定拒绝投影Task、无责任lease）；成功时在同factory收住operation并登记责任，Control等待root正在登记factory退出后才读取操作集合，按§4.6.1不漏该竞态。Carrier/parent C2 StartRead同此规则。

Carrier键为`(Contribution.Id,Revision,Carrier.Key,Domain,CarrierFieldId,CarrierOrdinal)`，**CarrierFieldId=null与某一显式字段不是同一支持表**。当前显示render token必须先经§15.2.5.1回到carrier ordinal，再请求该行；root显示代不替carrier/贡献revision。ParentSlot只在该Descriptor父表有效；由`ParentReference.Surface+Domain+ParentOrdinal`定位父**载体**，不是RootIndex、face顶点位置或最近点。全程long/checked、InvariantCulture十进制编码，禁止经过double/Int64→int；`9007199254740993`与`9007199254740992`不能合并。父快照及方法证据也随行保留，0权父项仍是原Owner声明的一项支持。

`SupportCarrierRow.State`原样使用SC.SupportState.Exact/Unknown/Unsupported，不另缩成bool；Use仅表示消费时父值/坐标可用性，与State是两个轴。Unknown/Unsupported正常读完可以是Succeeded Batch，Parents为空、Method/Evidence保原因，**不得**凭非空carrier值提升Exact或Observed。Exact只表示C5协议/方法绑定相符，且WeightAuthority=ProducerRecorded；不表示父值有效、标定合格或生产支持齐全。坏CSR/Origin/hash是整批错误而非默改Unknown；SnapshotMismatch属于004/016整批拒绝，无可用Batch，不用新增同义成功状态掩盖它。

##### 15.2.5.5 双scope、页暂存、父快照读取与IM007链

**确定执行顺序。**

1. `Contributions.Validate/Plan`纯预检；所选目标字段沿C5固定闭包：null/Vertex HeightField→Height，null/Vertex XYZ→X/Y/Z，null/Face→TriangleIndices，非null→精确同Domain字段。不把颜色与位置共用贡献表。C5的`IContributionSession.ReadIntoAsync`读取贡献Buffers、`ReadCarrierOriginIntoAsync`读取CarrierOriginBuffers；同名buffer也分scope，C5自己核全hash/实际Uniform或PerItem Origin与Method.CarrierOriginId，viewport不另解CSR/Origin或偷换Source。C5 FullBuffers只覆盖两集合，不覆盖其它carrier值或父payload；expected Descriptor/父Snapshot/Method Evidence必须从原Owner可信发布取得，不用任意测试hash当算法证据。
2. 非空请求在无IO的各父port.Plan明确报价后，先按§4.6.1用BackendAdapter reserve原子预留Work/Control、最大行/父项/副本字节与任务槽，并armed cleanup，再启动C5。同步`IContributionReader.Start(request,consumer,executionToken)`只调用一次并保存其返回的operation；把其**原Completion Task**通过Work.StartOriginal登记，另Retain零字节操作责任凭据，Completion真实退出才可归还。Start拒绝operation=null不伪造借用；所有调用都在root容量门后发生。不能把Observe/WaitAsync包装当原Completion。
3. OnPage在worker上同步短复制，先核operation/generation/descriptor逐字段、Sequence从1递增、CarrierStart连续、Offsets[0]=0/末=Entries.Length、长度States+1、行完整及请求边界/EOF。按`carrier=CarrierStart+i`、`Entries[Offsets[i]..Offsets[i+1])`关联State/MethodId；**不拿页内i当全表ordinal、不拼跨页半行**。页内ref struct及Span不进入Task/Dispatcher/长期对象；预留内存后将Offsets/States/MethodIds/Entries逐值复制，保原次序/UInt32解码后的int slot/Int64父ordinal/原double bits（包括+0）。MethodIds查冻结Methods，Method.CarrierOriginId先作关联声明；在第5步与真正carrier值Origin再次确认。回调不启动父IO、不等待本Completion/Close。
4. 收到最后页仍不采用；原C5 Completion必须Completed+Complete（空请求Empty）、Input carrier/ContributionId/Revision/Generation精确一致，Errors空/IssuesTruncated=false、非空请求Integrity=FullBuffers，Requested/DeliveredCarriers等于请求、DeliveredEntries等于暂存和、Exact/Unknown/Unsupported计数逐行匹配，EndOfRequest=true、EndOfTable=(Start+Count=N)。其中Complete不是“全Exact”；空请求无页、无C5/Carrier/父Source或Acquire，Integrity沿上游未读取事实NotVerified，成功空Batch，不捏造FullBuffers。任一取消/failed/late generation或末页digest Conflict使所有暂存失效，不能先用第一页Pick/Intent再宣称后来失败不影响。
5. 用借用CarrierValues按同完整Carrier descriptor和Contribution.Domain，Ordinal `[StartCarrier,Start+Count)`、PreserveAll、固定目标FieldIds、ReadCoordinates=false、Target/Transform=null调用Plan→StartRead。OnBlock同样只复制原字段PackedValues/States/Reasons/OriginIds/Ordinal，等其原Completion Completed/完整请求后join；同carrier所选字段实际OriginId必须全相同且等于该C5行Method.CarrierOriginId，包括Unknown/Unsupported和Uniform；C5已核双scope，并不免除另一个carrier值session逐字段expected/实际Origin交叉确认。源不可变承诺使不同操作可拼同修订，来源违约/字段不一致016整批失效，不用改变C5 expected hash洗白；每项状态独立保留，不将有效属性mask套位置。这里不重算C5方法真值。
6. 对Exact行的**全部条目，包括weight=+0**，按首出现的ParentSlot依原列表顺序先对`ParentSnapshotRequest(Expected,SourceId,剩余VerificationBudget)`调用父port.Plan，再AcquireAsync，原Task与迟到lease提取器沿root登记；所需Read权限包含CarrierSource及所有父SourceId，Source身份/key/domain/snapshot不等授权范围。Plan纯查已发布binding无IO，EvidenceOwnerId/Revision非空，MaxReadBytes≥0、MaxRetainedBytes≥0且满足预算；Plan失败不Acquire。port是宿主原Owner的显式消费适配能力：原Owner确认Expected.SnapshotSha256对应发布的父不可变快照证据，再返回lease.Reference逐字段等于Expected、Descriptor.Key/Frame/domain ItemCount匹配、SourceIndexBinding完整、Reader绑定该准确descriptor；Confirmation恰等预检Plan、VerificationReadBytes非负≤Plan.MaxReadBytes、Identity.RetainedBytes≤Plan.MaxRetainedBytes。hash不是默认文件hash、也不是C5 FullBuffers证明父snapshot。Acquire返回的Reference只是实现承诺，生产必须有原Owner真实证据链；fixture实现不授真实资格。错hash/同Key不同frame或count/buffer/字段/原Owner引用004/016整批拒绝，不选latest。parent lease借用持续到所有该父read/坐标原Task退出，bridge不Close该Reader或父Source。
7. 从每row原entry取parent ordinal，在同parent的完整Descriptor上Plan→StartRead`SurfaceRange(parent.Domain,Ordinal,ordinal,1,null,false)`；不把RootSourceIndex反推carrier ordinal。非重复父值读取初版逐项串行、MaxParentReads为**实际调用总数**上限（不只并发），同一个batch跨行重复地址可在预留的本地有界表复用已完成同snapshot/FieldIds读取，不重排/合并贡献row；不建跨operation缓存或hash捷径。ParentBinding.FieldIds显式选择原Owner给的XYZ/Height、Attribute或TriangleIndices；Face请求ReadCoordinates=false，不能当face ordinal去读Vertex。Vertex且ReadCoordinates=true时TargetFrame=parent.Descriptor.Frame、Transform=null，HeightField的Grid.Mapping交surface现有ISurfaceCoordinatePort；三角索引/root sourceindex保持Int64/结构类型。所有正权和零权条目都实际核原值State/Reason/Origin与Snapshot。无效/未知父项保持Use.Invalid/Unknown；位置用途不能因0系数跳过这些门。不能读取则仍整批Failed/Unknown，不假造空Exact父值。
8. 父C2 raw FieldValues来自PackedValues保原编码/单位/独立状态；RootIndex从同块.SourceIndices取得，RootBinding从parent当前Domain的VertexIndices/FaceIndices取得，**不替换SC.ParentOrdinal**。原Position取Positions中的源frame/单位且保State/Reason/OriginId；Coordinates端口只映Valid坐标，不有效化NaN。对需要位置的parent，经该ParentBinding SourceId/CoordinateRevision/FromSpace/ToSpace调用§15.2.3 ICoordinatePort.MapAsync：请求From=父frame准确binding，To=本请求TargetFrame binding，返回revision/count/单位/目标space逐项一致。跨mm/um先读parent自身同单位C2，再用IM007已发布含比例的链到目标；不得给C2设跨单位Target、不得自行再乘1000、不得用显示矩阵或未授权“默认identity”代替图。同frame也走明确登记identity。FromSpace/ToSpace不能只由文字相似判断。CG域外/无链/输出未知Use.NoMapping，留原父值和State/Evidence，仅导航；不将非Exact行父列表补出来。FieldId不同贡献不自动映成位置；Face拓扑/普通Attribute可完整回溯，但当前SurfaceHit不能把它作为原3D点，Use.UnsupportedDomain或RequirePositions预检拒绝。
9. 全部参与操作Completion退出/读取内容确认后，交付前再核generation与Read/Probe权限，创建本Adapter独立只读SupportBatch lease并使Operation.Completion返回Succeeded；父snapshot lease此时只归还本方borrow，实际父值/方法及索引副本仍归Batch，不等待父Source存储退款。batch Owner/backing/lease身份由本方预留生成，RetainedBytes精确记录受控副本payload/有界metadata，禁止把C5页源buffer冒充本方owned allocation。任何副本/FieldValues/字符串分配前按Required准入或明确离线BudgetOnly本Owner预留；native模型仍归已有DisplayLease，不因支持batch成功关闭模型。

**父权重到既有viewport Support的规则。** 仅在本行State=Exact、Authority=ProducerRecorded、所需carrier值有效、全部父项（含零权）Use=PreviewValue、required坐标链成立时，允许派生点返回SurfaceHit.Kind=Interpolated或预览ProbeValidity.Interpolated。SourcePoint仍取当前carrier原值经原坐标Owner投影，不用父weight重算它，更不把派生1父/1权升OriginalSample。每条Support保原Weight bits、次序、不合并、不归一化、不删0；观察原点无C5按旧路径。

多父`SurfaceContribution.OriginalIndex`采用版本前缀的无歧义地址：`vpsc1:{N}:{ParentId}:{ParentRevision}:{DomainCode}:{SnapshotSha256}:{ParentOrdinal}:{R}:{RootId}:{RootRevision}:{RootIndex}`。N/R是后接Id的ASCII字节数、所有数字InvariantCulture无符号十进制（long非负）、DomainCode=SD.SampleDomain的1/2；按长度切Id而非Split冒号，Id内可有冒号/slash。父地址及RootBinding两层同时保留，RootIndex可>2^53；不把不同父/域/快照同ordinal合并。此编码仅本Adapter多父support消费，旧单Root十进制不改；解析须识别前缀/版本/长度/范围并回到同binding的typed ParentValue，不能把它再转double或当数据库键。实际Origin/FieldId/Method/Evidence/Exact状态在typed Batch中随请求保留，UI/Intent关联同Batch lease直至其原消费完成，不能只留这个string丢掉Field贡献差异。

前述flat Support映射只适用**单一当前carrier**的生产者贡献row。face透视插值/Height双线性先有viewport显示采样层系数，再涉及多个carrier各自的C5 row，必须保两个层次及两种方法证据；本片不将它们相乘、合并、删0后冒称原Owner发布的实际父权重。旧Observed采样/barycentric路径保持；有派生carrier的复合显示采样可用既有SampleContribution/当前face引用加typed Rows供只读分层查看，但旧SurfaceHit.Support不能表达两层方法时NoMapping/NavigationOnly，不输出假flat Exact Support。此限制来自该旧DTO表示范围，不是C5读取缺失；将来扩展须由真实消费者冻结分层输出契约，不能悄悄重写已接收表示。

当前SurfaceHit不能表达Unknown与Unsupported这两个状态：两者分别通过公开typed Batch保持；该窄桥对应可测量点的旧口返回NoMapping/无可用Support，由宿主按明确资源键显示“来源证据未齐”或“贡献方法不支持”，不把两者压成bool，也不改成OriginalSample。任一父Invalid/NoMapping/未有实际物理资格使业务生产采纳拒绝；离线PreviewValue不等Qualified。C5 1e-12和保护仅上游一致性门，不是允差/置信度；桥不重复求和改变上游weight。

可选UI只借Batch的immutable typed行作逐父回溯，沿§10.6已预留Presenter/Dispatcher原任务登记consumer borrow，撤overlay/回溯面板引用并等原回调真退出后才归还Batch；不把ContributionPageView直接交UI。已有ViewportIntent/IntentSink只接flat SurfaceEvidence，不能独自承载此Batch方法/字段/父快照的完整审计闭包。因此本片不自动调用事实IntentSink提交多父生产支持；明确的宿主只读consumer持Batch引用完成诊断后返回，若产品需要持久化此证据，须由原Intent/事实Owner冻结保真接收契约与回执，然后在同borrowing规则下接入，不靠CandidateId或编码字符串丢掉typed三态。

##### 15.2.5.6 取消、迟到、借用与有界资源

Bridge Start只接纳本身有限MaxOperations；所有counts/bytes正且checked，MaxCarriers/Entries/Parents受ViewportLimits、root及upstream limits双重约束，MaxWork/ControlTasks受根可用额度。ExecutionBudget/CleanupBudget在§3.6的[50ms,10min]，单个upstream OperationLimit取当前**同一单调总deadline剩余量**，不每页/父样本重置。Close只封本bridge新Start、取消自己的operations，有限观察，不调用共享ContributionReader.Close/SurfaceService.Close或坐标StopAndDrain；跨Host A取消不关闭B。RequestCancel同时只向已启动本C5/C2 operations.RequestCancel及IM007原RequestId的CancelAsync发协作意图，未启动父读取/坐标立即封门。

C5计划全hash成本必须计入端到端：令C=request.CarrierCount、T=Plan.MaxRequestedEntries、F=所选字段数、U=不同PerItem Origin控制列数，`A_c=sum(贡献Buffers.ByteLength)`、`A_o=sum(CarrierOriginBuffers.ByteLength)`，C5 ReadBytesUpperBound=`A_c+A_o+16+2*(8*(C+1)+5*C+4*U*C)+20*T`。A_o包含整个Origin所在原buffer其它payload/padding，同名buffer的两scope也各算；部分carrier请求不减少该A，不缓存跨请求hash，不可只读页而跳全hash。先Contributions.Plan取得真实上界；超过MaxTotalReadBytes/贡献预算在Open前003，不能降为RequestedBytes。另预占Carrier C2 Plan.ReadBytes和最坏MaxParentReads*ValueBudget.MaxReadBytes；获取准确父Descriptor后先Plan再启动，只用实际Plan上界扣本次剩余read账，不因反复Open而重新放总额度。各ParentSnapshotPlan.MaxReadBytes加入完整总读上界，MaxRetainedBytes加入root峰值；父snapshot Owner自身验证证据若需全buffer hash/read IO，Plan必须报价其全量（或已发布证据验证所需完整bytes），Acquire报实际VerificationReadBytes且不超过预占。无报价/无法有界确认时拒015或Unknown，不以SnapshotSha256非空免费认证。空请求不调用父Plan；正常请求可预检所有声明父槽的Plan保最坏上界，仅Exact行实际参与槽才Acquire/计实际，节余在真实退出后撤。

页源驻留按C5 Plan.ResidentUpperBound，不含viewport长期副本。本方页暂存上界`13*C+24*T+8*(C+1)`（State/Method/ordinal及ParentContribution按24-byte payload；本地CSR offsets可在join后撤引用），每个Carrier/Parent需保留的PackedValue长度及State1/Reason4/Origin4、RootIndex8/position40/target24、typed metadata按128 bytes/记录+实际UTF8字符bytes、每数组64-byte软件保守overhead另计；字符串OriginalIndex按其完整编码长度预估，不能在OnPage无界造对象。贡献页+本地行结果+Carrier C2 scratch同时峰值，随后父snapshot lease/一个C2 scratch+IM007输入输出副本+最终Batch/旧显示borrow并存均入MaxCopiedBytes/root。未知task/lease占额度；无合法容量不Open，不通过自动缩fan-in/删0/截页提升预算。parent读总数最坏T（去重只是节余，不为新工作超开预留）。各Owner账分范围，不把重复借用与source池容量相加作进程RSS。

原上游Completion/Acquire/Map/Return每个Task先登记，ValueTask仅AsTask一次；若本调用有限超时，Operation.Completion只在实际执行Task退出、操作临时资源已排空后给无Value Cancelled/TimedOut/Failed，Observe可先返回Cleanup.Pending/Unknown。root仍保全部原任务及零字节上游责任凭据；非Completed页/值批永不交付Batch，晚到成功parent lease/Batch由extractor收住再归还，不能丢失败Value里的违约资源。Close不能自等待自己的Work.Observe或在Control调用session.Dispose；Control等待Work原callback/children，槽外再关闭宿主session/root。

Batch Return首先关闭新consumer借用，等Pick/Profile/Intent/UI/Dispatcher实际引用退出，撤全部本方CPU强引用并取得本Owner准入确认；本方借用清完即可Returned，不声称GC已回收物理堆/RSS。QueryReturn查询同ReturnId关闭Task/本地状态，不重做C5读取或重复Dispose。支持副本与DisplayLease是两份独立Owner资源，Unbind先撤UI引用，最终两者都真实归还；只C5 Completion不证明页长期副本/UI已退出，OwnerAccepted也不等Drained。上游ContributionSession及C2 session只由它们operation Dispose一次，释放未知Completion仍不完，bridge不得替Owner再Dispose/强杀/重新建reader猜释放。父snapshot port.ReturnAsync按原Owner公开回执确认本borrow，Pending/Unknown留原lease；bridge无父存储退款权。

错误映射：SD.Input/Layout/Version→002/007（Version能力失配为007），BudgetExceeded/BudgetUnavailable→003/015，Unit/Frame→006，Io/Closed→004，Validity/Topology→002，Native/Internal→011，Consumer→011，Conflict/Integrity→016，Cancelled→009、Timeout→010；原Error.Path/ordinal安全保留。清理未确认是PortOutcome.Unknown+Cleanup.Unknown，不提前报告业务失败已释放。合法Unknown/Unsupported行是Succeeded typed Batch的状态，不能用此错误表把它伪改成损坏或自动放行。

##### 15.2.5.7 两个完整无UI桥消费者（语义构造，尚未编译/运行）

以下为普通实现者可按公开构造逐项装配的**合成夹具配方**，不是隐藏产品factory。C5 Source与CarrierValues的副本可直接按上游§15.7 Host-P/Host-Q的逐字段完整descriptor/两scope原bytes/hash构造；引用该既有规格不复制第二份CSR解码/Owner实现。这里补齐上游示例没有的父原值Owner/坐标/viewport root/结果lease/消费闭包。两个Host独立进程、独立Source/reader/bridge/root/slot/lease，固定1s业务时钟，真实监督沿§13.1，不启动HALCON/WPF、不给fixture生产资格。

共同父源fixture（分别创建实例）实现`IViewportParentSnapshotPort`及独立lease：以expected `(SurfaceKey,Domain,SnapshotSha256)`完整key查只读ledger，ledger存深冻结Descriptor、原Owner snapshot证据bytes和专属SurfaceDataFactory创建的Reader；每Parent Plan=(synthetic-parent-owner,ledger1,MaxReadBytes256,MaxRetainedBytes256)，验证fixture证据bytes长度<=256，Acquire保Confirmation/VerificationReadBytes=实际证据bytes长度，lease.Retention=256的借用metadata（不计巨大逻辑buffer为驻留）；无IO Plan不校验新证据，Acquire才在有限预算读/核ledger既有证据。Acquire仅精确匹配、当前Read授权和预算后返回lease，Reference字段不得从请求临时复制去伪造确认。unknown key/错证据拒004/016；非空hash不足确认。snapshot证据在软件fixture是上游明确的synthetic UTF8 bytes，不声称真实源算法/父bufferhash已认证。Reader借用至lease Return等本方已启动任务退出，lease Return/Query同原ReturnId幂等，A/B independent borrow计数；服务最终Close只由各Host在所有lease归还之后做。

大ordinal父Descriptor构造：Key/Frame/ItemCount精确取上游P/Q ParentReference，PointCloud/Vertex，VertexCount=9007199254741000、FaceCount0、Grid=null、VertexIndices=(StableOrdinal,0,本Key,null)、FaceIndices=null；Origins=[Id0 Observed,Parents空,observed/1,ParametersSha256空,HasExactParentIndex=false]。三个Float64/单组件X/Y/Z字段各独立逻辑buffer，Offset0/ElementStride8/RowStride0/LE，UnitId=mm或um、Scale1/Bias0、Validity Uniform Valid/Reason0、Origin Uniform0、FrameDependent=true；buffer ByteLength=checked(8*VertexCount)。fixture `ISurfaceSource.OpenAsync(expected)`核完整Descriptor返回独立只读session，ReadInto按offset精确切一个**稀疏逻辑合成流**：未指定ordinal的XYZ均0，下面指定ordinal覆盖相应Float64字节，不分配全表、不经过double做地址；Source.Integrity=NotVerified。巨大逻辑buffer的Sha256在此故意采用固定UTF8 `synthetic-unverified:{Key}:{field}`的SHA256作为**未验证fixture声明**，不是这些巨大原bytes的真实全hash；不得把该Source/Hash用作真实Parent生产资格、也不得报告FullBuffers。C2公开接口允许NotVerified，此夹具专门验证>2^53寻址/预算/协议；真实Owner端必须提供真实buffer声明及快照证据，桥结果保ValueIntegrity=NotVerified/QualificationRef=null，所以只可Preview，不可生产采纳。Contribution与Origin两scope小buffer仍按上游真实合成bytes核SHA256，不能用此父fixture方式跳C5全hash。

共同CarrierValues用上游P/Q完整小Carrier及实际XYZ/Height/Origin bytes实现C2 source，按原Layout逐字节读，Return独立；其snapshot与C5 Carrier深等，shared Origin buffer bytes也精确同源。Face/Attribute Parent用途另用明确的同Domain Descriptor/FieldIds，不在这两个位置Host偷用面索引作点。IM007 fixture建立按坐标v0.2规约的完整Graph/Policy/Frame/Edge Ref与hash：源parent-mm/1、parent-um/1（或Q parent-mm/1）及S1当前carrier frame均Right3D，XYZ正轴、closed软件有效域覆盖下面点，S1目标um；Q无坐标调用，其合法注入服务可复用同值graph但实例独立，不声称将Q的mm载体换成um；mm→um Affine3为diag(1000,1000,1000,1)，um→um显式identity，NumericPolicy有每Frame AxisScales=[1,1,1]、BoundaryGuard0、MaximumCoordinateMagnitude=1e6、MaximumConditionNumber=1e6、MinimumDenominatorRatio=1e-12、OrthogonalityTolerance=1e-10、CovarianceTolerance=1e-12、InverseResidualTolerance=1e-10、MaxPathDepth8/MaxPathCandidates8/MaxGraphVisits64、Optional/NoCovariance、AlgorithmLimits(32,4096,100000,1024,1024,64)。该坐标服务按现有factory `CoordinateGeometryFactory().CreateManaged(RuntimeLimits(2,64,64,128,8,8,1048576,1048576,1048576,1s),TimeProvider)`装配；私有ICoordinatePort严格按§15.2.3 Submit/Wait/Query/Cancel，ParentSourceId与graph/frame/path/Profile/hash显式binding，绝不直接乘1000绕Owner。Graph/Frame/Policy软件hash按coordinate-core-values-v1真实规约计算；它们不是物理标定资格。

**Host-S1：DerivedPickSupportHost。**

1. 按上游§15.7 P完整构造Carrier=`support-carrier/1`、XYZ共享Origin列[0,1,1,1]、SC.Descriptor=`recorded-support/1`/Domain Vertex/CarrierFieldId=null、全表4行7父项、P的Options与两scope Source。调用`SurfaceContributionFactory.Create(ContributionOptions(0,1,4,4,8,2,1048576,1s),ContributionPorts(sourceP,clock))`检查Reader非null/Errors空。C5 Request与原P一致：Start0/Count4/AllowEmptyfalse、PageCarrierLimit2/PageEntryLimit4/MaxFanIn2/MaxTotalEntries7、ResourceBudget(synthetic-p,1,4,4096,262144,2,16,1s)、Generation1；读上界524 bytes，页面[0,1]/[2,3]，第3行零权项原样保留。
2. Parent0是P Carrier自己的完整C2 Descriptor/Reader，snapshot证据UTF8 `synthetic:carrier-snapshot-v1`；Parent1 raw-a/7、mm/ItemCount如上，ordinal9007199254740993→(1,0,.01)，9007199254740995→(2,0,.02)，9007199254740997→(3,0,.03)；Parent2 raw-b/9、um，同大count，ordinal9007199254740995→(1000,0,10)、9007199254740997→(2000,0,20)、9007199254740999→(3000,0,30)。各快照证据精确为P的UTF8 `synthetic:raw-a-r7`、`synthetic:raw-b-r9`，由ledger本身SHA256与expected比较，不以父值checksum代替。父FieldIds为实际X/Y/Z字段Id（固定x/y/z），Parent0用Carrier的原X/Y/Z Id；ReadCoordinates=true，Qualifications=null。源Graph binding sourceIds分别carrier-P/parent-a-P/parent-b-P，FromSpace为各准确frame token，ToSpace=fixture-um/2的graph token，CoordinateRevision=1。
3. CarrierValues及每parent Reader均`SurfaceDataFactory.Create(SurfaceOptions(0,4,4,16,16,8,2,1048576,1s),SurfacePorts(对应source,Coordinates:null,clock))`；父大点云无需Height Grid，C2源frame读XYZ不调用坐标端口。桥Limits=(MaxOperations2,MaxParents4,MaxParentReads7,MaxCarriers4,MaxEntries7,MaxCopiedBytes1048576,MaxTotalReadBytes65536,MaxWorkTasks64,MaxControlTasks64,ValueBudget(synthetic-values-p,1,4,4096,262144,2,16,1s),Execution1s,Cleanup1s)。调用`ViewportSupportBridgeFactory.Create(limits,SupportBridgePorts(PReader,CarrierService,父snapshotPort,IM007坐标port,authPort,ResourceAdmission:null))`得Succeeded bridge。
4. 独立root `ViewportRootOptions(root-support-P,2,256,128,4194304,1s,2)`，ViewportLimits(8,16,128,16,16,32,4096,4,32)；Session按§11.2的完整fixtureA options构造，ConsumerId=bridge-P、AccessMode=ReadOnly、Navigation|Probe、BudgetOnly、HeadlessPlan、Surface=null、Roi=null、Presentation=null，Operation/Drain=1s，MaxDisplayBytes1048576/MaxInFlightTiles1；该无UIfigure端口仍准确实现Frames/Authorization/Backend等同签名。Attach一个公开1×1 UInt8灰度ImageSourceDescriptor(SourceId carrier-P,revision carrier1,coord1,center整数,Full domain,(0,0,1,1),level0 tile1×1单位矩阵/1byte,decode1)，Authorization=OfflineViewing/Read|Probe/AccessDomain synthetic-P（也覆盖三个明确SourceId）、未过期三语资源zh-CN，Api0.1/View Fit2D(100,100,1,1)；检查Attach成功得Generation1。该占位图只提供真实session执行身份，不冒充表面显示。
5. `bridge.Start(SupportBridgeRequest(carrier-P,PRequest,coord1,Carrier.Frame,[上述三个slot binding],RequirePositions:true),root,session,ct)`返回operation；其Completion由bridge内部reserve原Task链持有，外部finite Observe(1s,ct)不替原Task。Completed后Batch.Rows精确4、State全Exact、ActualOrigin=[0,1,1,1]、方法0/1/1/1。Row1仍是slots1/2、父ordinals9007199254740993/9007199254740995、Weight .25/.75，映到um的父点均(1000,0,10)，原mm和um值分别保留。Row3原记录weights+0/1、两父都被读取/映射/资格核对，不能只交第二父；原Carrier.SourcePoint不由这些父值重新计算。编码/解析vpsc1保大ordinal与RootIndex逐long一致；ValueIntegrity.NotVerified/Qualifications=null明确仅合成预览，不授ProductionSupported。
6. 无UIconsumer读取Batch typed行/父值作回溯，保租约直到消费返回；调用Batch.ReturnAsync(ReturnId support-P-return,Reason host-finished,Budget1s,独立cleanup token)，Unknown时Query同ReturnId并保root，不丢原Task。bridge.Close(1s)、session.Dispose/RootClose在所有slot外有界观察；Host拥有的ContributionReader/Carrier/parent Reader/坐标服务只在自己的bridge/root均实Drained且lease归还后各Close/StopAndDrain一次（self-parent Reader与CarrierValues是同实例，按reference identity只关一次），有限失败输出非零并列pending，不能跨Host关闭。未实排空进程watchdog超时记失败，不报资源已释放。

**Host-S2：FieldSupportAuditHost。**

1. 按上游§15.7 Q完整构造独立HF Carrier support-height/2、z字段PerItem Origin [0,1,2,1,2,0]（Origin RowStride12不借z的RowStride32），SC.Descriptor audit-support/2、Domain Vertex/CarrierFieldId=z、6行/6父项、Methods[0,1,2]/Exact/Unknown/Unsupported原值；Options同S1、独立Source/clock/Reader。Q Request Start0/Count6/AllowEmptyfalse、PageCarrierLimit3/PageEntryLimit4/MaxFanIn2/MaxTotalEntries6、Budget(synthetic-q,1,6,4096,262144,3,16,1s)、Generation1；读上界586 bytes，pages[0,1,2]/[3,4,5]，未知与不支持行在CSR分别空但状态不同。
2. ledger self-slot0是Q完整HF descriptor/CarrierService，snapshot UTF8 `synthetic:height-q-snapshot-v2`；slot1 raw-q/3、mm count9007199254741000、独立稀疏PointCloud，ordinal4→(0,0,.01)、8→(0,0,.03)、9007199254740997→(0,0,.02)、9007199254740999→(0,0,.04)，证据UTF8 `synthetic:raw-q-r3`；Parent1 fieldIds[x,y,z]，slot0字段[z]，ReadCoordinates=false，Qualification=null，SourceIds carrier-Q/parent-q-Q，From/To为空（不发Map），CoordRevision1。self-slot0 Height值审计无需Grid坐标，所有C2请求ReadCoordinates=false；C2 CarrierService Factory配置同S1，SurfacePorts(sourceQ,Coordinates:null,clock)合法且不调用未装Grid。
3. BridgeLimits=(2,4,6,6,6,1048576,65536,64,64,ValueBudget(synthetic-values-q,1,6,4096,262144,3,16,1s),1s,1s)，Ports(QReader,QCarrierService,QParentPort,已构造但本次不用的合法ICoordinatePort,Q授权,null)；Factory得bridge。独立root/session按S1全部构造，仅root id=root-support-Q、consumer=bridge-Q、Source/AccessDomain/placeholder revision换Q，仍Attach成功Generation1；不能借P root/session或绕过auth。Request TargetFrame=null、RequirePositions=false，精确parent bindings上述两项。
4. Completion与所有C2实际读取退出后才消费Batch；Rows6，State=[Exact,Exact,Unknown,Exact,Unsupported,Exact]、Origin=[0,1,2,1,2,0]，Receipt Completed+Complete/Exact4/Unknown1/Unsupported1/Integrity FullBuffers仍**不**“全部Exact”。Unknown row2与Unsupported row4 Method2/Evidence保各自原因且Parents空、不读猜测父；row1 weights .25/.75读parent ordinal4/8，row3 weights .5/.5读两个>2^53 ordinal，row0/5为self exact z字段原值。Position=null/TargetPosition=null，不从z权重猜XYZ，Field audit不发SurfaceHit测量或IM007。所有NotVerified父/无Qualification状态保留，Batch只证协议回溯。
5. 部分请求Start3/Count2时新Start新Guid、EndOfRequest=true/EndOfTable=false，准确关联全表carrier3/4而非页0/1；C5预算仍按全buffers hash，不为了EOF读carrier5。空Start6/Count0/AllowEmptytrue成功Empty无页/父读取、EndOfTable=true；非法空拒002。相同carrier新增Attribute字段colour且原Owner采用不同Origin/贡献，只按该独立ContributionDescriptor(Id/revision/CarrierFieldId=colour)的新Request审计；没有该表007，不用z/null表代替。结果FieldId完整保留，纯位置接口不采colour支持。
6. Qconsumer独立按S1同Return/Query/Close/slot外session/root/host上游关闭顺序排空。A取消时B的Source/session/ledger借用计数不变；两Host同发布包但完全无产品Shell/DB/UI/static viewer，fixture只替Source/时间/授权/确认，验证/预算/错误/归还仍走本公开桥。

##### 15.2.5.8 可判定反例、Benchmark与六项定位

| ID | 输入/故障 | 唯一断言及恢复 |
|---|---|---|
| VP-SC01 | S1两页双父及>2^53 ordinal、Row3 +0/1 | 原ordinal/RootIndex/Weight bits/slot顺序不变，全部父原值均读取；IM007输出um正确，不重新算权重/当前carrier坐标；正常归还不影响另Host |
| VP-SC02 | P Origin[1,0,1,1]但Methods未变；Q Origin跨页[1,1,2,0,2,0] | 原hash先Integrity；合法新fixture expected hashes也只能通过byte门，C5实际Origin预检Conflict且OnPage=0，bridge无Batch。不能靠第二页才拒或使用上页暂存；恢复须原Owner同时发布新Carrier/Contribution修订及正确方法 |
| VP-SC03 | 只在page2篡改权重/页CarrierStart从2错成0、错误Sequence/半行/EOF | 原C5 failed或桥016，整批暂存失效；不采用第一页、不修CSR、不将短读0当EOF；原Completion真实退出再恢复新操作 |
| VP-SC04 | Complete但Unknown/Unsupported、Unavailable/NotEstablished、signed方法 | S2三个状态原样，旧口NoMapping且typed区分原因；空父不是空Exact；不补等权/nearest、归一化或质量PASS |
| VP-SC05 | null XYZ row[XOrigin0,YOrigin1,ZOrigin0]；z/colour各贡献不同 | C5 null闭包Conflict，无Batch；合法分字段各Descriptor可独立审计，不合并为位置；无colour表007，不能选X或z代替 |
| VP-SC06 | parent sameKey但SnapshotSha256/frame/itemcount/descriptor不同；换slot表不换revision | 原Owner Acquire或桥004/016、无有效Support，不取latest/把父ordinal当RootIndex。恢复经原Owner采用新引用、重新授权/绑定坐标、新贡献revision，旧snapshot不重用 |
| VP-SC07 | 父+0项Invalid/Unknown/无权限；mm→um无IM007链 | State.Exact保事实、Use.Invalid/Unknown/PermissionDenied/NoMapping阻位置支持；零权仍核域/资格；没有完整Read授权在父启动前拒008；不能删零改变证据或C2跨单位换标签 |
| VP-SC08 | parent ordinal是Face，或超过long/int地址预算，RootIndex与parent ordinal不同 | face按Face源域读拓扑/SourceIndices，不当3D点；位置Require预检007，所有Int64地址checked，溢出/限额003，RootBinding与父地址分别保留 |
| VP-SC09 | P read预算523/Q585；Carrier/parent副本上界少1byte，全hashOrigin buffer很大 | C5 Open前003；不跳A_o全hash/不按范围折减A。父/桥独立预算及同deadline有效，不能自动降fan-in、预占不够后边复制边拒绝 |
| VP-SC10 | hash/Origin reader、parent Acquire/Read/IM007、OnPage/Dispose/Return闩锁，期间cancel/close/换generation | Observe有限Pending/Unknown、root存原任务/迟到lease/账，接纳门关闭；只有实际Owner排空才能归还。旧结果不进新代；关闭/取消不重建reader、不重复session.Dispose |
| VP-SC11 | Span逃逸/回调启动父IO/等Completion；页面交付便发Intent | consumer违规失败无Batch；只能同步有界复制，全部原Completion与join/父验证后采用；UIA/Dispatcher结束不替borrow return |
| VP-SC12 | C5 hash/Origin/协议均一致，但可信Expected被换或Producer实际算法权重错 | 无可信Owner证据拒采用；协议一致不认证方法真值，synthetic/NotVerified无生产资格；C5正常Observed/no表路径保持不受强制C5影响 |

BenchmarkProfile冻结Carrier/Contribution/Domain/FieldId/Origin闭包F/U、两scope完整buffer及A_c/A_o、N/C/T/fan-in/零权率、跨页/部分/empty、父Key/domain/snapshot/巨ordinal分布与所读FieldIds/源单位/Integrity、IM007 Graph/Frame/Path/Policy/revision、页/父借用/本地batch容量/旧新并存、冷热/预热/测量n/并发/时间与权限策略/有限截止。测Plan→C5双scope全hash→Origin预检→页copy/digest→C5真实Dispose/Completion→Carrier读/Origin join→父OwnerAcquire/证据验证→父C2原值→IM007/授权复核→Batch交付→consumer/最后borrow/实际Return；C5读完与最终资源释放分开计。分别记录upstream/source原bytes、hash耗时、桥副本payload/metadata/峰值、operation/parent/页水位、Exact/Unknown/Unsupported和Use分布；完整端到端计到本方ResourcesReleased，P50/P95/P99及失败/删失按GOV010，不只统计Exact快样本。目标由采用Profile提供，未提供NotEvaluated；synthetic大父RequestedBytes/NotVerified结果不能报父全hash性能或生产支持。

| DEV-GOV-010 §3.1 | V-A1-C5本版唯一定位与结论 |
|---|---|
| 1 职责/依赖/第二消费者 | §15.2.5.4/7，S1派生点回溯、S2字段/非Exact审计，读原事实、不放行，不强制旧Observed/C5空缺路径 |
| 2 API/身份/Owner/单位/资源/结果 | §15.2.5.4～6，Contribution API0.1/Core0.4/viewport0.1分开，typed三态/实际Origin/父ordinal与Root双地址、双scope/完整hash/lease与取消 |
| 3 无UIHost/显式端口 | §15.2.5.7，S1/S2公开factory、Options/两scope bytes、Carrier/parent C2、父快照port、IM007/root/session/auth/return闭合，无隐藏窗口/DB |
| 4 正反/并发/异常/恢复 | 本节VP-SC01～12+两Host具体页/ordinal/状态/零权断言，先暂存后采用，坏行/跨页/错误父snapshot/迟到/有限close不跳过 |
| 5 Benchmark/预算/阈值来源 | §15.2.5.6及本节Profile，C5全hash524/586与父/桥/坐标总账、同deadline/源Integrity分开，未采目标NotEvaluated |
| 6 工程/测试/允许禁止/顺序 | §15.2.5.4绑定未来net10.0 Adapter及既有Smoke；只在获准实现后创建/引用，禁止其它模块/产品/AsunImage内部/原件；命令见下、真实桥资格另门 |

获准实现后的唯一定向命令为`dotnet build src/Asun.UI.Viewports.SurfaceData/Asun.UI.Viewports.SurfaceData.csproj -c Release`和`dotnet run --project tests/Asun.UI.Viewports.Smoke/Asun.UI.Viewports.Smoke.csproj -c Release -- --suite support-bridge --consumer both`。当前工程/API/suite尚未实施，不假称现有Smoke已经支持这些参数。必需VP-SC01～12与S1/S2未完成/跳过/超时返回非零并列ID，已通过的既有Core/Golden范围复用；每case10s、suite120s、外层watchdog180s沿§13.1，业务1s不控制wall watchdog。此次仅文档与合成数学检查，不执行上述命令。

2026-10-11主控回读§15.2.5.4～8，本版V-A1-C5六项**限定指导内容接收**；不标纯CoreReady，不提升运行/生产资格。原V-C1/C2/C3六项规格和U1/V-A1已接收范围保持。残余是实际Adapter/父snapshot原Owner证据与Read授权/IM007图/真实值及资格、原Task/lease/baseline排空接线、真实HALCON/GPU/WPF/性能/现场验收；这些分别影响对应消费，不反称Contribution CSR/Origin/公开读取未定义。父snapshot确认port是本消费片显式宿主接口，不是C5新增Source方法，也不由viewport自签物理证据。

#### 15.2.6 剩余内部Integration子门与定向验收

以下是内部接线/适配的**实现与验证欠账**，其软件步骤已由§10.6～9/15.2.1～7冻结，不是未决定的算法/API/架构；不能称客户/设备外部门。仅阻相关V-A1/V-A2实际能力，保留可确定映射及已接收Core。

| 子门 | 明确缺口/关闭断言 | 当前允许部分 |
|---|---|---|
| VA1-FRAME-RETURN | §15.2.2已经用现有幂等Release定义同ReturnId的有限归还观察，无新增QueryRelease契约门；真实Adapter仍须验证原Task未退出不重调、有限复观察/实际scope退出/释放异常保Unknown | 读/布局/中心/首次及迟后Drained映射已定；借用实际确认前保账，不改上游指导 |
| VA1-FRAME-FORMAT | PixelLayout单layout/BackingIdentity单身份不能无损表达异构多plane或重叠多allocation；native CopyToHalcon逐plane新matrix需本地Owner独立预算/归还链，V-A2真实实现另验 | 单plane/单allocation CPU及同plane交错；Float64 CPU可读但HALCON复制/LOD拒绝；不再泛称006合同未读 |
| VA1-COORD-BIND | 源坐标文字/ROI Frame/Surface Mapping到完整Graph/Frame/Edge/Policy真实binding及零字节操作责任凭据尚未实施；图/摘要/策略按坐标唯一规约，非本地猜hash。Nm/Meter目标不在当前viewport单位域 | 已定义Submit/Wait/Query/Cancel与全批结果映射，仿真不要求标定物理资格 |
| VA1-ROI-BIND | 既有IRoiPort/A.6消费映射接收保持，真实Adapter尚未实施/接线。当前扁平Kind不能保多Component/开放Curve/handle细节，相关编辑必须用完整ROI桥；Region原Lease/Grid/物化/Drain需真实验证 | 单component草稿/命中映射、完整WPF桥输入输出与关闭顺序已写；不复制ROI算法或改上游指导 |
| VA1-SURFACE-DISPLAY | §15.2.5.1本地Owner/副本lease/fast原点LOD/mesh LOD0/预算与return规格已定；真实AsunImage封送/模型/准入/排空接线与运行验收尚未执行 | Source/完整块/原索引现有契约足够，不等待Surface新增LOD服务；超预算明确拒绝 |
| VA1-SURFACE-QUERY | §15.2.5.2～3当前HALCON primitive可见性桥、规则Height剖面/ROI投影规格已定，真实backend/WPF/同样本精度与性能待验；C5已接收，上游读取缺口已撤，V-A1-C5消费桥在§15.2.5.4～8精确绑定，本版已限定指导内容接收；复合采样的分层表示限制见§15.2.5.5 | Observed原点/原Mesh贡献、规则Height读取/采样与投影不等新上游服务；非规则Profile/Overlay用途明确未装配007，不冒充全Surface能力 |

定向验证仍放既有§13 Core/Smoke与未来实际适配验证落点，不新建测试工程/报告。V-A1接收断言：① 5×3→3×2与非零halo起点中心/边界精确一致，带孔/Empty域不被包围框洗成Full；② 超long的上游ulong修订能经binding精确引用、旧token/同ID异内容拒绝；③ 同allocation两独立lease归还A不影响B，StorageReleased=false但本lease Drained可Returned，Unknown不得退款，原Release Task未退出不得重调；结束后的幂等关闭复观察必须同ReturnId且有界；④ 坐标WaitExpired/Cancel/Unknown期间保原实例/请求/责任，整批域失败无部分点成功；⑤ ROI Preview无Apply/Commit、锁/CAS/多Component/歧义不丢失，Editor.Detach→Unbind不关闭共享Core；⑥ Surface Span不逃逸、失败整批显示副本失效、派生索引不升级Observed，读Completion不当DisplayLease已归还；⑦ Surface四操作只调用已有StartRead/原索引/坐标Owner及本页私有显示lease，fast不能变质心、mesh compact重映正确、HALCON object_index不是point index，pick pass遮挡与透视β到原坐标/Support一致，规则Height零权边界/洞/剖面端点/ROI多环有效性不被洗白；缺派生贡献才NoMapping，不把上游无同名服务当永久阻断。用同一binding路径连接§11两无UI Host和§10两个STA Host，fixture只替源/时间/确认行为，不走更宽松校验或权限。以上为规格断言，未实施/运行。

#### 15.2.7 Surface 0.6.0-prep H/S增量的精确消费影响

只读surface-data [§17 H运行/精度绑定、§18 codec/格式注册、§19.4消费者影响](../surface-data/DEVELOPMENT-GUIDE.md)，复用C1～C5已接收读取/Origin/CSR/两scope协议与有效向量，不重复上游算法。viewport当前§15.2.5显示Adapter直接消费C2原块、C5记录及自己的HALCON显示模型，**不调用SurfaceImageLibFactory/ISurfaceImageLibPort.FilterAsync**；H不是本backend工厂、不是显示window/fence/Presenter，也不替代本方LOD/pick。故本版无需暗中迁到H、注册新H worker或把其CPU输出当显示句柄，没有H运行凭证不阻当前C2/C5读取与Core。

若某明确Host把H输出选为新的显示输入，由该Host在取得H结果前按上游唯一公开三参数`SurfaceImageLibFactory.Create(adapterBudget,time,NativeRuntimeBinding)`装配：WorkerExecutable/WorkerSha256/AsunImageSha256/WorkerCommitLimitBytes/MaxWireBytes/NativeAccuracyPolicy由实际发布包、资源Owner与用途精度Profile提供，不填假hash。H1 real是float32；H1/H2单位往返均按原单位MaxCoordinateRoundTripError核验，阈值0不表示自动放宽。错误/量化超限/边界筛选集合不符不得显示为成功原样本，也不自动降到另一H方法。只有原H operation完成、worker及pipe/资源真实退出、Result身份/状态/原CPU值与来源关系均可采用，Host才按原Producer流程发布新的SurfaceKey/完整Origin/方法证据，再用本页C2/C5 binding消费；不能把native量化XYZ覆盖原CPU值、旧Surface修订或Root索引。两个Host各有自己的原job/Task/预算；viewport取消不杀其它H消费者，H worker退出不证明viewport Presenter或父Source借用已归还。这里是可选输入的消费规则，不增本模块Filter算法/导出/生产写权。

本模块本身**不写/注册持久化codec**：布局由宿主按§10.4处理，源metadata/原buffer格式归surface-data与IM-066原Owner。对于使用新S格式重开的显示Host，准确链为受信manifest ObjectRef→有界读取/IM-066原lease归还→`SurfaceMetadataCodec.Decode(bytes,limits)`→Metadata非null且Errors空→逐字段Validate/Plan→精确(scope,BufferId)到ObjectRef冻结表→`SurfaceAdaptersFactory.CreateStoredSource`及需要时`CreateStoredContributionSource`→新的Core/C5 session→本页Adapter；没有调用`SurfaceMetadataCodec.Create`或恢复旧运行对象。Buffer的Origin/validity/原padding/Int64不改；C5 FullBuffers仍仅覆盖其两个scope，不因此证明父值/物理证据。

采用S的Host必须向原IM-066 `ResolvedStorageConfiguration.FormatValidators`精确注册`CreateMetadataFormatValidator(VersionRef,SurfaceMetadataLimits)`和`CreateRawBufferFormatValidator(VersionRef,maxBufferBytes,readChunkBytes)`，格式分别surface-metadata/1与surface-raw-buffer/1，VersionRef含发布包Hash而非仅Id。metadata读上限、原buffer长度、ReadChunk和根/解码驻留在读之前准入；schema/version/hash/权限错无半对象，无buffer时不填空成功。未知格式/版本不猜om3/PLY/旧manifest，不静默升级或覆盖原bytes；回退使用保留的旧包+旧格式validator+旧manifest/引用，重新授权/Validate/Plan，不恢复旧lease/Task/generation。没有采用S的Host保持其当前合法源格式，不被强制迁移。

Owner分别是：surface-data维护H/codec语义；实际发布/部署Owner提供worker与format版本hash；IM-066装配Owner接收validator配置并负责真实IO/权限/保留；Host/Producer决定新输出身份和可信快照；viewport本原会话实现本页只读消费与root/Presenter责任。不能将这些已有明确软件步骤标“待上游提供接口”，也不能用运行未验说明算法未定义。VP-A03新增消费断言：H1 real往返超Profile拒采用，旧输入/Root不变；H未调用的当前viewport无worker启动；S两scope同名Id不串源、未知format拒绝、解码错无半display/lease恢复、回退保原bytes。真实H/IO/权限/重开/WPF仍分别验，不重算上游已接收Golden。

### 15.3 发布和回退

发布包至少包含 Core、已用 Adapter、可选 WPF 适配、依赖版本、契约/Schema 版本、能力矩阵、迁移说明、测试摘要和回退指针。发布前必须：

1. 对两个消费者执行相同版本的离线回放和故障矩阵。
2. 检查新增/变更字段、单位、事件顺序、错误码、线程和资源所有权。
3. 做 Attach/Update/`DisposeAsync` 长稳及取消/超时/排空测试。
4. 确认没有未登记的产品程序集、私表、SDK 句柄或全局状态。
5. 生成可恢复的上一版本包和数据/配置兼容说明。

回退以版本化包和显式配置切换完成；回退失败或迁移未知时保持旧版本可用并进入 `Blocked/RecoverableError`，不自动清空用户配置、租约、原始资料或证据。新版本不得在旧 Viewport 仍持有资源时强行替换 native/GPU 后端。

## 16. 第二消费者接入要求

第二消费者采用“独立测量工具 + 复判/生产工作台”双验证策略：

- 独立测量工具启用 2D/3D查看、探针、020 ROI 草稿和 030 量测请求，但不含生产放行、设备控制或机台数据库。
- 复判/生产工作台启用只读证据、稳定目标切换、权限/盲审投影和宿主意见提交；不因复用控件得到 ROI/程序写权。
- 两者必须引用同一发布包和同一 Core 契约，各自注入主题、语言、权限、源租约和命令端口。
- A→B 快速切换、缺图、权限撤销、关闭排空、语言切换、125% DPI、迟到结果和 3D 缺映射必须在两个宿主分别验证。
- 宿主不得通过包装一个产品 ViewModel 来绕过 Core 的错误、取消或资源回执。

第二消费者计划满足Core准入第1条件；两个真实消费者已接入是后续集成/发布验收，不阻断可模拟的Core切片内容接收。本文当前不声明两者已运行。

## 17. 实施切片与DEV-GOV-010六项内容评估

### 17.1 全能力覆盖和顺序

0.3.4-prep整模块文档准备结论与全能力定位唯一见§20.4；V-U1公开装配增量见§10.6～9（WPF Assembly Contract v0.2），V-A2具体window/renderer/thread/camera/return路线见§7.7/10.8/15.2.5，Surface H/S消费边界见§15.2.7。本原会话负责内容审核/修复/验证，总控仅调度及接收状态；不再将“等待主控内容审核”作为文档完成门。旧切片内容接收保持，不据本版整模块文档结论提升ImplementationSpecificationReady/运行或生产资格。

1. 主控已接收V-C1/V-C2/V-C3六项规格内容，本页同步ModuleCoreImplementationReady（仅规格内容）；V-U1指导内容已接收，真实WPF/GPU/backend/产品仍NotReady，不标纯CoreReady。平台DTO/客户Profile只影响其消费Adapter/真实资格，不要求全平台先冻结。
2. 在现有Core与Smoke工程依次实施V-C1纯计划/精度/有界范围，V-C2 Session/授权/命令/错误事件，V-C3 root/原Task/cleanup/准入/资源归还。它们共同承担无UI能力，不能只完成V-C1就称整个viewport完整。
3. V-A1帧/坐标/ROI/Surface公开Adapter与可控夹具指导已接收；本版V-A1-C5窄增量已限定指导内容接收，六项位置及非纯Core/真实资格边界见§15.2.5.8。V-A2 AsunImage HALCON2D/3D具体backend与显示ROI/pick路线。平台Owner调用在Adapter映射，公共Module API保持不变；公开签名/封送的实际编译与资源资格只阻断实际对应调用；已决定软件路线见§10.8，不交实现者重选架构。
4. V-U1可选WPF/DevExpress控件/Binding/Presenter、两个STA Host指导内容已接收；后续实现任务按§10.6工程落点实施，不能将现有Core机械改WPF或新空工程冒进度。
5. 两真实消费者+实际HALCON/大图/3D/资源/GPU/WPF与Profile资格串行推进，后续产品映射和现场验收单独接收。模型训练/设备命令不属于本模块，没有理由把这些不相关条件设为Core门。

### 17.2 六项逐项证据位置（V-C1～C3规格内容已接收）

| GOV010 §3.1条件 | V-C1内容 | V-C2/V-C3内容 | 全模块其余切片与状态 |
|---|---|---|---|
| 1 职责/非目标/依赖/第二消费者 | §1/2/16，数学只读、无源事实写入 | 同一边界，006/007/020/027和root各有Owner | §8/10/11两个Host计划；满足内容位置，未证明已集成 |
| 2 唯一Module API/单位/域/结果/事件/资源/版本 | §3.3/3.4/4.1/7/15，闭合double矩阵与plan | §3.3/3.5/3.6/4.6/4.7/5/6，公开session/ports/root，失败与cleanup双轴 | §8.4/10.6闭合3D命令、UI Binding/Presenter；声明为目标API，非现有实现 |
| 3 无UI最小宿主、外部显式端口 | ViewportPureOperations，§11.1 | RootFactory→Factory→DTO→Attach/Apply→Dispose/RootClose，§11.2两个私有fixture | backend/存储/设备/HALCON在Adapter，§10.6WPF另DLL；Core无需隐藏窗口 |
| 4 正常/边界/重复/并发/取消/超时/关闭/回退断言 | §7.2/7.5/13 C01～C06/G01 | §5/6/11/13 L01～L07/H01与§15回退 | §8拾取/联动、§10UI、C07/U01；已给断言，未执行这些新tests |
| 5 Benchmark方法/负载/有限预算/阈值来源 | §14纯Plan测点/输入维度 | §14有限case接纳至真实ResourcesReleased、两轴峰值与失败/删失 | GOV010统一统计口径；目标值待Profile采纳，NotEvaluated不是PASS |
| 6 唯一工程/测试/路径/调用/后续门 | NewBuild+§11/13真实dotnet命令 | 同样Core/Smoke，不造新Core/TestHost | WPF具体落点§10.6指导已接收；内部Integration与产品/真实HALCON/GPU/WPF/1920/性能门§18 |

2026-10-10主控回读0.3.0-prep并独立重建PlanGolden的136bytes/hex/SHA-256，接收V-C1；随后接收0.3.1-prep的V-C2/V-C3六项规格内容及V-U1指导内容。本文同步V-C1～C3为`ModuleCoreImplementationReady`（仅规格内容），V-U1保持非纯Core切片、真实WPF/GPU/backend/产品`NotReady`。V-C1公开Plan声明/算法/Golden不变。全模块仍`DesignReview/Prep`；内容接收不表示代码已实现、运行验证或Integration/Production资格通过。

## 18. 剩余条件按受影响切片登记

| 具体条件及真实来源 | 阻断什么 | 不阻断什么 |
|---|---|---|
| 主控已接收V-C1～C3六项规格内容及V-U1/V-A1指导内容；V-A1-C5本版增量已限定指导内容接收 | 真实父Owner/授权/IM007/Adapter与HALCON/GPU/WPF/性能仍按真实用途验收；复合多carrier仅保只读分层证据，旧SurfaceHit/IntentSink不能完整表达时不输出假flat Exact支持、不自动提交生产事实 | 保留C1～C3 ModuleCoreImplementationReady（仅规格）及U1/V-A1接收；V-A1-C5不标纯CoreReady、不提升运行/生产资格 |
| **内部Integration实现/验证**：006/007/020/027确定消费设计见§15.2.1～7与§10.6～9，子门见§15.2.6；实际Adapter尚未实施/接线/验证，非留待设计 | 仅对应真实Adapter、缺失能力及产品集成；不能称外部条件 | 已接收V-C1～C3、可确定字段映射及有界fixture；不等待全上游同时Ready |
| V-A2公开签名的实际编译/参数封送验证、当前backend按§10.8规定的window/native退出/资源计费实测 | 该具体HALCON/backend调用与资源资格 | cv2算子可用性已确认，不设包装覆盖/授权/安装门；纯数学/协议Core |
| 实际GPU/renderer/Dispatcher退出、Presenter可见确认、WPF操作/三语/UIA固定1920×1080证据 | V-U1实际UI资格和GPU/后端集成通过声明 | V-C协议及STA Host实施规格；不要求改显示设置 |
| 消费者实际代表图像/表面/mask/校准真值、误差公差/LOD误差目标、性能Profile资源与延迟阈值、盲审/权限新鲜度政策 | Golden/Replay准确性、计量/性能/现场/生产接受 | 所有无产品事实写入Core；协议fixture仅验证软件行为 |
| 宿主Export/Measurement/事实审计IntentSink到原Owner的具体实现与确认边界；旧.roi迁移是否合法/精度 | 对应产品消费、旧数据导入和事实提交 | typed候选/无UI导航/本ModuleAPI；Viewport不自建文件事务/量测引擎 |
| 当前目录无.git，未来代码任务要绑定权威仓库/分支或可审计快照 | 真正代码修改基线/集成审计 | 本轮唯一指导任务；不把它伪装为HALCON/DX不可用 |

客户/设备物理值和现场授权仅由真正Owner提供；常规root、cancel/drain、默认backend/ROI/多源/UI路线已在本页决定，不再标“待工程师自选”。未执行条件只影响本表对应slice，不无限扩大外门。

## 19. 第二轮场景驱动架构复审

本轮采用反例优先方式复核：先假定输入迟到、身份错误、资源不足、后端失效或操作含义不明确，再检查模块是否会错误地呈现旧内容、虚构数值、吞掉失败或越权写入。下表是实现和审核必须逐行落地的场景契约；“参数来源”必须能追溯到端口、Profile 或宿主上下文，不能从页面默认值、文件名或历史控件状态猜测。

### 19.1 确定性视觉路线、备用和训练边界

Viewport 没有学习型算法，不需要训练集、模型、checkpoint 或推理后端。它的算法路线是确定性的显示与交互变换；任何去噪、分割、配准、缺陷分类、量测或 AI 建议必须由其它 Owner 提供结果投影。实现者不得为了“抗噪”在 Viewport 内新增滤波/插值算法，也不得把显示平滑当作测量预处理。

| 路线 | 适用输入 | 处理顺序 | 备用/恢复条件 | 输出和边界 |
|---|---|---|---|---|
| 2D 主路线 A：006 Tile/Pyramid + Core显示矩阵 + §7.7 AsunImage/HALCON窗口 | 有合法 2D 帧、源域、坐标修订和已装配显示后端 | 校验身份/授权 → 取 006 租约 → 选 LOD/tile → Core 组合 crop/LOD/旋转/镜像/缩放/平移 → 适配器按§7.7共享edge矩阵变换image/region/XLD，再按窗口part提交 → 复核呈现代 | Tile 解码失败、后端错误或 GPU 丢失时，保留同源合法旧呈现或降到原件/低 LOD；新身份不能配旧图 | 只产生显示计划/呈现回执；不改变 006 原像素、007 物理变换或业务结果 |
| 2D 备用路线 B：Core 纯 CPU 显示计划 + WPF 位图/软件栅格适配 | 无 HALCON 窗口能力但有已验证的像素/Tile 读端口 | 同主路线前半段；软件适配只消费有界 tile 和显示矩阵，不读取生产缓冲 | 后端不可用时可用于离线查看/回放；若无源映射、超预算或缺像素格式则返回 `VIEWPORT-007`/`VIEWPORT-003` | 不能把备用呈现声称为 HALCON 精确显示；记录 backend=software、LOD、插值和复制次数 |
| 3D 主路线：表面/点云 LOD + AsunImage `cv2.disp_object_model_3d` | 有 027 表面、相机/姿态或明确展示投影、LOD 和有效域 | 校验源/单位/权限 → 取 LOD 租约 → 校验相机/姿态/裁剪 → 提交显示 → 仅在后端支持时做可见性拾取 → 通过 027 源映射取值 | 无标定只允许相对/导航显示；无可靠拾取则降为旋转查看；GPU 失效则撤销该 backend generation 后重建 2D/原件 | 不从渲染深度报物理 Z；不将展示相机当实机标定；不生成新表面事实 |
| 3D 备用路线：CPU 只读投影/线框 | 有三角/点数据和源映射，但 3D 后端不可用 | 由外部离线诊断Adapter提供有限投影或线框，标记 `ReadOnlyDegraded` | 仅用于离线诊断/回放；无投影参数、w 退化、源映射缺失或超预算立即拒绝 | 不支持拾取、量测或导出原始证据；必须显示降级原因 |
| 探针路线：原样本/明确插值 | 006/027 提供值读取和有效域 | 代号/权限 → 源域/mask → `get_grayval` 或 `get_grayval_interpolated` 的已核对适配 → 返回索引/方法/支撑 | 读端口不支持插值、坐标越域或 reduced-domain 不可证明时返回 Unknown；不回读 8 位纹理 | 只返回 typed probe result；不参与质量判定 |

本轮已直接读取HALCON26.05本地官方页面核实显示、坐标、探针和3D算子语义，未扫描AsunImage内部；对应页面固定于 `halcon算子手册/operators/`，标题版本为 `26.05.0.0`。具体 .NET 入口和参数签名只能以目标消费项目实际引用的 `ImageLibDotNet` 公共程序集、公开文档和编译核对为准。AsunControl 快照中的 `HOperatorSet.cs`/`HWindow.cs` 仅是历史场景参考，不能作为当前公共签名证据。

这些是实现核对依据，不是把 `HOperatorSet`、`HWindow`、`HObject` 或 native handle 提升为 Viewport Core API。cv2已具备HALCON26.05算子集；仅当C#类型/重载/封送确有歧义时在消费工程查公共签名/编译，对象借用与窗口线程由本适配器串行Owner合同落实；不因未逐一扫描包装就判不可用。HALCON 页面中的 reentrant/parallel 描述不能替代 AsunImage 包装的线程安全承诺。

### 19.2 场景契约矩阵

文件来源与视图缓存边界：源图、原始 3D/点云/高度场只以 IM-066 `ObjectId`/不可变文件引用作为持久身份，数据库保存元数据与引用，不在数据库存图像字节。IM-060 通过 source adapter 获取有界字节流或 tile lease；不得直接把整幅超大图读入 Npgsql `bytea`、Core DTO 或 UI Dispatcher。缩略图、LOD、解码块及 GPU 副本均为可丢弃缓存，缓存键包含 ObjectId、hash、source revision、解码/金字塔版本和访问域；损坏/驱逐只清缓存并报告源错误，不更改原对象。第二消费者测试需覆盖离线 NAS、磁盘满/权限变化、源对象缺失/hash 不符、缓存重建、取消时真实归还文件租约。

| 场景 | 输入和参数来源 | 处理顺序 | 输出、状态和错误 | 恢复动作 | 可判定验收 |
|---|---|---|---|---|---|
| 正常 2D 配置/执行 | 006 `ImageSourceDescriptor`、宿主授权快照、007 显示坐标、ViewportOptions/Profile | 校验有限数/能力 → 建 generation → 取租约 → 选择 LOD/tile → 生成显示计划 → 提交并复核代号 | `Ready`，`PresentationCommitted`，回显实际 view/LOD/矩阵 | 无需恢复；宿主可按 receipt 继续导航 | 同一快照重复执行得到相同计划和事件顺序；无额外副本超过预算 |
| 空输入 | `Sources=[]` 或合法上下文但无可用帧 | 不订阅源、不启动解码；保留语言/能力上下文 | `Empty`；不返回成功图像，不产生 `SourceLeaseAcquired` | 宿主提供源后调用 Update；若权限不足则转 `PermissionDenied` | 空上下文下无旧图残留、无租约、无后台任务；UI 显示“无可呈现源” |
| 部分成功（2D 可用、3D 缺失/某层失败） | 2D 源有效，Surface 或一个 Overlay 无效 | 各源/层独立校验；可呈现部分先提交，失败层带来源错误 | `Ready` 或 `RecoverableError` + `Partial` notice；不把缺层当完整成功 | 重试失败层或由宿主移除该层；不重试已成功层造成重复事件 | 2D 仍可用；缺失层明确列出；无虚构 3D/Overlay，业务回执不被改写 |
| 歧义/错误输入 | 未知 ViewKind、重复对象 ID、混合单位、NaN、坐标修订冲突、权限用途不匹配 | 原子校验全部字段和来源关系，先于租约/后端调用 | `Blocked` 或操作失败；`VIEWPORT-002/006/008`；无成功事件 | 调用方修正并以新 operationId 重试；旧操作不得自动修补 | 任何非法字段都不分配 native/租约；错误定位到字段/来源/修订 |
| 超大输入 | 宽高/Tile 数/Overlay 顶点或预计 bytes 超 Profile 上限 | 估算 CPU/GPU/在途内存 → 选择 LOD/窗口范围 → 只请求可见块 | `Busy`、`InputLimitExceeded` 或受控降级；receipt 回显实际范围 | 宿主缩小视野/换 Profile/离线分块；不隐式改变量测输入 | 峰值不越预算；没有全图复制；超过上限不会先分配后失败 |
| 高并发输入 | 多 Viewport、快速 A→B→C、共享同一 tile、多个 probe | 每实例独立 generation/预算；006 single-flight 共享物理工作；按对象撤销等待者 | 各实例只收自己的代；旧响应 `VIEWPORT-005` 丢弃 | 取消单个等待者；全部离开才请求停止底层工作 | A/B/C 乱序下最终只呈现 C；B 不被 A 覆盖；资源归还一次 |
| 噪声/遮挡/无效 mask | 源质量等级、mask、缺值、遮挡域来自 006/027 或宿主 | Viewport 只传播 validity/mask；不去噪、不补洞、不分类；显示 hatch/unknown 图例 | `Ready` + `Unknown/Invalid` probe 或 `RecoverableError`；不涂合格色 | 宿主请求原 Owner 的质量/重建/算法路线；Viewport 可重新呈现新修订 | 缺值/遮挡显示原因；原始值不被平滑或插值覆盖；无 PASS/NG 推断 |
| 退化几何/矩阵 | 宽高为零、不可逆/近奇异矩阵、w≈0、LOD 无三角、3D 面背向 | 检查有限数、条件/适用域、齐次分母和可见性后才命中/投影 | `Blocked`/`CapabilityUnavailable`/`CoordinateUnavailable`；无命中值 | 复位 Fit、切换只读导航、请求宿主补标定/坐标链 | 退化输入不除零、不用单位阵、不返回无穷或 0 伪值 |
| 取消/超时/native 未排空 | 任意在途 Attach/Tile/Probe/`DisposeAsync`，CancellationToken 和预算 | 停止接收 → 撤代 → 取消可中断队列 → 等 native/GPU 完成 → 释放/归还 | 调用回执可先为 `Cancelled/TimedOut`+`Draining`；原工作真实排空/归还后才发终结事件 | 宿主等待/查询排空；超过政策转告警和隔离，不强杀句柄 | UI 线程无同步 Wait；未排空不 Dispose；所有资源最终有 Owner/待处理记录 |
| 资源上限/驱逐 | CPU/GPU/队列接近 MaxDisplayBytes 或 MaxInFlightTiles，或 Required `TryBeginAsync` 拒绝/结果未知 | 拒绝发生在 backing 创建前；先保护已结算且仍借用/被 GPU 引用资源 → 驱逐有真实释放证据的条目 → 限制预取/降 LOD/排队 | `Busy`、`RecoverableError`、`InputLimitExceeded` 或 `ResourceAdmissionUnavailable`；不驱逐在用资源、不以 Unknown 当拒绝已结清 | 宿主按同一 AllocationId 查询/收敛未决 permit；释放其它实例、缩小视野或等待 fence；不降低生产量测源精度 | 未获 permit 无分配；Unknown 无重复额度；实际峰值计入替换并存；无释放证据不退款；重复调用幂等、冲突隔离 |
| 持久化/版本修订 | 显示偏好、source/schema/contract/backend generation、旧 ROI 草稿或布局 | 校验 major/单位/坐标/来源；迁移纯函数；显示偏好与证据/权利分开 | 兼容则 `Ready`；未知 major/语义破坏 `Blocked` + `ContractNotFrozen`/`InvalidInput` | 保留旧包/旧配置，人工选择迁移或回退；不自动改几何事实 | 同一输入旧/新版本回放差异可解释；未知字段不改变事实；未知 major 拒绝 |
| 升级/回退 | 新旧 Core/Adapter/后端包、在途旧实例和已保存布局 | 停止新接入 → 排空旧代 → 验证 manifest/迁移 → 原子切换；失败保留旧包 | 成功为新 generation；失败 `Blocked/RecoverableError` | 切回上一包和兼容配置；记录迁移/回退原因 | 不在旧句柄仍使用时替换后端；用户配置/证据不被清空；回退可重放 |
| 无 UI 调用 | TestHost/服务调用 Core 同步纯操作或异步 session | 用不可变 snapshot；同步仅矩阵/校验/命中，异步负责租约/后端/排空 | typed plan/intent/receipt；无窗口也可完成离线链路 | 由调用方消费错误和 drain receipt；不得依赖隐藏窗口初始化 | 在无 WPF/Dispatcher 环境可运行；结果与 UI 入口相同；无裸句柄泄漏 |
| 可选 UI | WPF/DevExpress 注入控件、语言、UIA、DPI、命令能力 | UI 事件 → Core command → receipt/event → UI 投影；输入框/IME 隔离 | 八态、三语、UIA 和 SuperTip 正确；业务事实不在控件写入 | 显示宿主提供的恢复动作；语言/布局切换不重载源 | 固定 1920×1080 基线内的宿主实际 DPI、键盘/IME/UIA/面板折叠均须有证据；不增加其它分辨率矩阵。本文不宣称已执行 |
| 第二消费者 | 独立测量工具和复判/生产工作台各自 Context/权限/端口 | 同一 Core/版本，分别验证只读/编辑能力矩阵和退出排空 | 互不污染 selection/generation/租约；宿主收到 typed intent | 一方关闭/取消不影响另一方；权限撤销只影响当前 scope | 两宿主均通过 A→B 迟到、缺图、盲审、3D 缺映射和关闭场景 |
| 长期运行 | 8h/24h 等 Profile 时长、循环换源/缩放/探针、GPU 重建注入 | 周期采样内存、租约、队列、generation、后端代；限速而非无限重试 | `Ready` 或可解释降级；无单调增长；异常可关联 operationId | 触发诊断快照、隔离泄漏资源、受控重启适配器；不清空业务证据 | 峰值/均值/尾延迟、句柄/租约计数回到基线；无幽灵旧图/旧事件 |

### 19.3 复审后必须新增的测试断言

除第 13 节矩阵外，第二轮实现验收必须明确断言：

1. 空输入不会触发源租约、解码、GPU 上传或 `PresentationCommitted`。
2. 部分成功的 2D/3D/Overlay 结果带独立来源和失败原因，重试失败层不重复提交已成功层。
3. 旧代响应即使带有合法 payload，也只能进入 `LateResultDiscarded`，不能因为 payload 完整而重新呈现。
4. 噪声、遮挡、无效 mask、退化矩阵和无标定 3D 输入不会进入任何 PASS/NG、质量放行、设备命令或自动 ROI 提交路径。
5. 同一 source/参数的 single-flight 在 A 取消、B 保留时底层工作继续；A/B 都离开时才允许停止，且停止完成有可观察回执。
6. 版本升级/回退前后，源身份、坐标/几何修订、单位和授权域保持可追溯；迁移失败不覆盖旧配置/证据。
7. 无 UI Core 与 WPF UI 对同一快照产生相同显示计划、命中结果和错误分类；差异只能来自呈现后端能力，并写入 receipt。

### 19.4 已关闭的工程选择

- 006持有源Tile/Pyramid/single-flight/实际source租约Owner；Viewport仅显示副本和实例等待者，根管原Task/borrow，不建立第二源缓存。
- 默认线上HALCON2D/3D主路线、离线Raster备用及不可切換条件见§4.6；3D可见性证据不作原值，027回源/pick与020几何候选各自唯一。
- 布局保存宿主Owner控制，信任边界/格式白名单/默认视觉恢复见§10.4；未知major/旧ROI迁移见§15/18，不在模块硬解旧二进制。
- 权限Owner发Revision/期限/访问域，会话接纳门和Presenter提交前重核；已见内容由宿主审计，不伪造跨进程瞬时撤回。
- 原呈现一直保留borrow到真实revoke/Dispatcher/backend退出；Started不能回退为unstarted；未知与有限清理/root接管独立于Drained。这些选择在本页冻结，本原会话审核后按后续代码授权逐slice落实，不再要求总控内容审核或用户再次确认常规选项。

### 19.5 固定源码、官方语义与采用限制

2026-10-09在线实际读取OpenSeadragon **v5.0.1**（annotated tag对象bbfb4c5b863a42ca4eb5a4259054b968f9595ebc，`git ls-remote ... refs/tags/v5.0.1^{}`解析commit **480de92d0a13f932d5b6879c8ba85d6593da5417**）。不是仅看README/截图；读取固定commit源码/测试/包描述/许可证如下。未复制源码或引入JS/Web依赖，只迁移可验证的调度/边界/迟到处理思想。

| 原件（固定commit下可查） | 实际读取与可迁移证据 | SHA-256/限制 |
|---|---|---|
| [src/tiledimage.js](https://github.com/openseadragon/openseadragon/blob/480de92d0a13f932d5b6879c8ba85d6593da5417/src/tiledimage.js) | _getCornerTiles约1812行裁剪可见边界；_updateLevelsForViewport约1314行区分draw/load coverage及低层回退；_onTileLoad约2016行丢弃reset前tile | `06a6e9e9783bff9f2b18596971fbfc56be013053c8e5ed1faab28e67d80e1365`；时间戳reset只适于其浏览器场景，本模块用Source/Coordinate/Generation/AccessDomain精确隔离 |
| [src/imageloader.js](https://github.com/openseadragon/openseadragon/blob/480de92d0a13f932d5b6879c8ba85d6593da5417/src/imageloader.js) | addJob按jobLimit排队；clear约219行只清未开始工作，finish跟踪inprogress/回调 | `99e9089c349fbe0026df176a4a22411f180899366746e00b4511df04fe10359d`；其jobLimit=0可无界、queue/重试/网络abort不证明native/GPU排空，不能原样照搬 |
| [test/modules/tiledimage.js](https://github.com/openseadragon/openseadragon/blob/480de92d0a13f932d5b6879c8ba85d6593da5417/test/modules/tiledimage.js) | reset约198行验证缓存清空/重新加载；fullyLoaded约520行验证zoom后状态变化；_getCornerTiles without wrapping约560行包括±1e-14边界误差 | `5a422a03ff489ef7b6289e0227931a63ba9d745cf3b034340c25a76f6a4b8819`；测试没证明物理释放、权限、工业真值。本模块另加root/lease/half-open/未知分支 |
| [package.json](https://github.com/openseadragon/openseadragon/blob/480de92d0a13f932d5b6879c8ba85d6593da5417/package.json) / [LICENSE.txt](https://github.com/openseadragon/openseadragon/blob/480de92d0a13f932d5b6879c8ba85d6593da5417/LICENSE.txt) | version5.0.1、BSD-3-Clause；没有列runtime npm dependencies，devDependencies含Grunt1.6.1/QUnit2.19.4等范围依赖 | package `3efb951be70c1458bdceb2d398ce3b2bb9ed90e034a8c9f033374d0e933309fb`；license `634a1392da774db80e9880d45d4182536c4543b6b965c3081f8f95c2e22bb1b1`；只读其实际许可证，不引入/下载运行依赖 |

HALCON固定本地官方 `26.05.0.0`：[`get_grayval`](../../../halcon算子手册/operators/get_grayval.html) / [`get_grayval_interpolated`](../../../halcon算子手册/operators/get_grayval_interpolated.html) 明确不检查reduced domain，bilinear四支撑、bicubic可越原数据范围，决定§7.6显式mask/支撑和拒识；[`disp_object_model_3d`](../../../halcon算子手册/operators/disp_object_model_3d.html) / [`get_disp_object_model_3d_info`](../../../halcon算子手册/operators/get_disp_object_model_3d_info.html) persistence默认false、depth为camera Z、未显示返回-1/ -1.0、查询edge坐标，决定§8只用其做可见性证据。-1哨兵须转NoHit，不能当物理负高度。展示相机不等于设备校准。

本轮新增实质歧义阅读：[`affine_trans_image`](../../../halcon算子手册/operators/affine_trans_image.html)、[`affine_trans_region`](../../../halcon算子手册/operators/affine_trans_region.html)、[`affine_trans_contour_xld`](../../../halcon算子手册/operators/affine_trans_contour_xld.html) 的row/column、edge原点/0.5桥、domain忽略与负方向裁剪，直接决定§7.7共同矩阵路线；不是重核cv2包含哪些算子。DevExpress25.2.3本机官方API与网页403限制见§10.5，Microsoft WPF线程依据已读；本轮没有复制旧AsunControl内部HALCON wrapper、旧WinForms渲染器或把源码测试等同本平台验收。

## 20. 本轮自审及交付结论

第一视角按normal/empty/large/weak/mask/degenerate/candidates/parameters走每项2D/3D/ROI/同步能力，关闭大图绝对zoom下限、float精度、尾块/半开范围、constant LUT、mask插值支撑、显示深度冒原Z、ROI投影无Owner、多候选随ZOrder变化等缺陷。第二视角按并发/取消/timeout/late/disconnect/close/unknown/rollback/第二消费者走完整Session、root、backend、UI借用，关闭Started误Abort、成功呈现提前Return、无permit无法Resolve、丢原Task、关页丢Dispatcher/presenter、无界cleanup/计数退款与接管冒Drained等缺陷。

前述基线两轮定向自审及必要修正没有重复全仓扫描。实际检查：永久registry/本会话、入口/进度/规则、现有Core/Smoke csproj及Program的Exe退出行为、官方/固定源码证据、PlanGolden独立字段136字节/hex/hash、声明/引用/本地链接/代码围栏和定向矛盾复核。新API/控件/夹具尚未实施，**没有运行dotnet build/Smoke、HALCON调用、WPF/GPU/1920×1080/三语/UIA、大图性能、计量或生产验收**。0.3.0-prep的V-C1及0.3.1-prep的V-C2/V-C3六项规格内容已由主控接收，V-U1指导内容已接收；0.3.2-prep同步状态并定向补V-A1映射已获指导内容接收；0.3.3-prep仅新增V-A1-C5窄消费桥，状态/验证范围见§20.3，不称整个viewport完成/生产通过。

### 20.1 0.3.1-prep定向接线返修（2026-10-10）

主控确认V-C1六项内容接收及独立PlanGolden复算，本文同步其ModuleCoreImplementationReady；V-C1公开Plan与Golden保持不变。此次只修§3.6/4.6.1/10.6/10.7/11.2的公开接线及对应状态/断言，没有重审其它全能力或新建authority。第一轮局部自审沿Reserve→Created空Bind→Attach新代child→原Dispatcher/Presenter→armed Control→slot外OwnSession关闭走正常/拒绝/晚到；第二轮查跨root同名session、关闭门后cleanup、worker/observer自等待边、有限总deadline与原Task强持，并检查声明/本地链接/围栏及Golden未改。补入VP-L07/VP-U02可判定断言，尚未写/执行它们。

0.3.1-prep交付时V-C2/V-C3/V-U1尚待接收；主控随后接收C2/C3六项规格内容与U1指导内容，当前状态以§17为准。真实WPF/GPU/Adapter运行与客户资格另验。V-A1可确定映射在0.3.2-prep补入§15.2，剩余精确**内部Integration**子门不能冒充外部许可/客户门。此次仍仅写本指导，未改产品代码、共享指导、参考原件或测试工程；未执行构建、Smoke、UI/性能/生产验证。

### 20.2 0.3.2-prep接收同步与V-A1窄映射（2026-10-10）

主控接收C2/C3六项规格内容及U1指导内容，页首/§17/18/附录同步；已接收C1与136-byte PlanGolden不改。只读四上游当前唯一指导，§15.2.1～4补准确身份/修订/单位/域/中心变换/LeaseId、源方法、错误与归还确认、ROI双端WPF桥；没有把上游接收或存在公共签名当真实集成通过。§15.2.5按本次补充裁决LOD/DisplayLease/Pick/Profile/Overlay为viewport显示消费责任，用现有Surface有界块与原索引闭合；保Source持久事实与专业计量Owner。该版交付时派生多父Support缺逐carrier父index/weight读取，首片不依赖它；2026-10-11上游C5已经接收并以本版§15.2.5.4～8闭合消费映射，该旧缺口不再是活动门。

两轮局部自审：第一轮逐字段/原方法/ValueTask一次AsTask/原Task与责任凭据/归还Unknown，修正ROI歧义投影不得捏造SelectionResult字段；第二轮按完整顶点+face快照→LOD token→离屏可见primitive→精确RootIndex/透视权重、规则Height零权边界/带孔断线→Revoke/本地lease返回核闭包，确认不把Surface无同名方法包装成永久上游门。复用已有validate_docs链接函数仅核本文，本地链接/代码围栏/状态及内存Golden核对；不新增脚本、报告、工程或测试代码。文档检查和合成算例仅证明规格结构/数学，不代表实际HALCON/封送/离屏覆盖/CPU与native峰值/WPF/性能/计量资格。0.3.2-prep交付时V-A1内容待定向接收，主控随后已接收该指导范围，当前V-A1-C5增量状态以§15.2.5.8为准。实际Adapter未实施/运行；所有真实资格门按§18分开保持。

### 20.3 0.3.3-prep：C5贡献消费桥两轮局部自审（2026-10-11）

本次仅只读surface-data 0.5.1-prep §15.2～15.9及必要C2/IM007/root公开形状，已接收V-C1/C2/C3、U1/V-A1及136-byte Golden保持，不全审、不新建Goal/会话/fork/子代理/消息。以SC已接收Contribution API v0.1替换旧上游候选缺口，§15.2.5.4～8冻结typed三态、实际Origin/字段闭包、CSR页面/父slot与Int64 ordinal、双scope/hash/Completed后采用、父snapshot Plan/Acquire精确确认与C2原值/Root/IM007链、0权仍核证据、本地Batch借用和归还；S1/S2为不同无UI消费用途，不授生产支持。

第一轮实现者正常→异常→恢复：按C5预检/两scope全hash/Origin→页暂存→Completion→Carrier Origin join→父Owner/原值/坐标→交付/consumer→真实Return，核错行/跨页/字段Origin差异、0权Invalid/父snapshot错/非Exact及取消/迟到；补入父Owner纯Plan报价与actual verification bytes、空请求不造FullBuffers、两层显示采样不洗成原Ownerflat权重。第二轮外部空Host：从独立Source/reader/父ledger/稀疏大ordinal C2/graph/factory/root/session/auth构造S1/S2到最终独立Close，修正C5 Start返回前首page关联、self-parent服务只关闭一次、UI/Intent需借Batch保typed事实。没有通过协议一致/字符串hash认证真实算法或物理支持；合成大父hash声明NotVerified，C5两个小scope原bytes/hash照常验，不伪巨大全hash性能。

本页定向验证复用validate_docs的链接解析，核本地链接/围栏/公开类型/六项位置/12个反例/接收状态与旧候选退出；内存复算S1/S2 CSR页边界、Origin错行、Contribution与Origin 200/16及206/24 bytes、全读上界524/586、Int64>2^53 little-endian往返与vpsc1含冒号/slash父地址保真，旧PlanGolden136 bytes/SHA256保持。仅证明所列文档结构/合成算例，没有创建工程或执行真实dotnet build/run、Contribution Source/父Owner/IM007/上游算法、HALCON/GPU/WPF、性能或现场。V-A1-C5本版增量已由主控限定指导内容接收，非纯Core与真实资格边界见§15.2.5.8/18，当前阶段到此停止。

### 20.4 0.3.4-prep：全批准范围的文档准备结论与剩余Owner

**结论：当前IM-060全部已批准范围的可决定软件设计已闭合，文档准备完成。** 这是本永久原会话对职责/公开契约/路线/操作链/错误恢复/可判定验证的结论，不等待总控内容审核；不等于整模块ModuleCoreImplementationReady、ImplementationSpecificationReady、代码完成、真实运行或生产Ready。V-C1～C3、V-U1/V-A1及V-A1-C5原接收保持，本次UI Assembly Contract v0.2新增装配与资源明确迁移；未把Core/API或质量语义降低以达到结论。

| 已批准能力/实际消费者 | 唯一确定实施位置 | 适用边界与文档准备结论 |
|---|---|---|
| 无UI计划/Session/Root、独立测量工具与工程/复判嵌入 | §3～6/11/13/17 | 原Task、权限、准入、取消/有限观察与真实return各自明确；关闭不自等，源Owner共享借用不互关。已接收Core/Host与有效向量复用，设计闭合 |
| 超大2D图、Tile/Pyramid、缓存/分块/迟到、旋转镜像与源坐标 | §4.1～4/7.1～7/15.2.2/19.5 | 源/cache/single-flight归IM-006，viewport只显示副本与等待者；没有整图复制/无界列表，尾块/halo/半像素/DPI与硬预算已定。格式边界拒绝而非猜转换，设计闭合 |
| 原值/多通道/插值/有效域、自动LUT与2D自动LOD | §7.4～6/15.2.2 | 同修订Owner统计、无有效值/常量/NaN拒识与四邻支撑固定；建议显式采用且冻结，不随平移或生产静默改参；无学习模型/训练。设计闭合 |
| 3D点云/Height/已有Mesh、源保真LOD、导航/2D3D联动 | §8/15.2.5.1/10.8 | fast保原点/精确长索引旁表、全层保守投影误差/显式Profile、Mesh首版LOD0；展示camera与物理标定分离，当前HALCON支持条件与不支持矩阵拒绝明确，设计闭合 |
| 可见primitive拾取、规则Height剖面/ROI投影、单/多父Support | §8.2/8.5/15.2.5.2～8 | 离屏同camera/遮挡pass、透视权重/原值、两scope实际Origin/CSR、父snapshot报价+原C2+IM007链明确；零权、>2^53、三态保真。复合多carrier只读分层证据，flat口不足不假Exact/不提交事实，设计闭合 |
| ROI选择/编辑候选、全几何/洞岛/多Component、键盘 | §9/15.2.4/10.4 | 精确几何/拓扑与Preview归IM-020；扁平投影不足走完整上游WPF桥，不丢Component/ElementId或自行Apply。宿主提交，控件无持久写权，设计闭合 |
| HALCON/GPU/window与WPF实际renderer/资源Owner | §7.7/10.6～8/15.2.5.1～2 | 同Control公开Presentation/lifetime/原submission+call+auth、同binding receipt/原Task观测、真实revoke/return；本方native/baseline与源借用分开，无隐藏renderer/VM/全局状态。显示格式/相机能力拒绝分支明确，设计闭合 |
| 紧凑高品质DevExpress控件/三语/UIA/恢复 | §10.1～5/10.9/22 | 实际25.2.3 Bars/Docking/SuperTip组合、主图保护/8DIP/侧栏收拢、HWND airspace、键盘/IME与八态、完整资源Catalog/必需键/缺键原子恢复；语言入口仅Host，设计闭合 |
| Surface 0.6 H/codec/格式重开与回退 | §15.2.7（上游唯一§17～19） | 当前backend非H调用者；采用H的新输入需原runtime+精度政策，real非无损。采用S的Host精确注册两个validator/两scope映射/回退包；本模块不复制codec/生产发布算法，设计闭合 |
| 双消费者、版本/发布/性能/长稳与故障恢复 | §11～18/19/22及VP-U03～05、VP-A03 | 两无UI与两STA确定装配、同Source借用互不清理、原136-byte Golden及C5向量保持、时延到实际归还/失败分母/有限watchdog已定。真实时延/精度目标来自采用Profile，设计闭合 |

不是当前批准能力的内容保持边界：任意第三方渲染器、额外原始源缓存/坐标/ROI/计量引擎、无定义外部PLY/om3导出导入、Mesh贡献未知简化、非规则Surface专业拟合/计量、自动质量阈值/放行与设备控制不属于本片。既有接口无法表达的物理单位/格式不靠改标签适配，能力矩阵/错误/恢复已明确；若以后用户扩大支持范围，在本唯一指导新增精确设计与验收，不能把猜测性需求当当前欠账或擅缩已批准使用场景。Gamma/Opacity固定值等首版显示边界见§10.8，参数资源存在不表示新增可调能力。

| 剩余事项/Owner | 精确影响；不是待决定的软件设计 |
|---|---|
| viewport本永久会话的实现Owner | 本指导所列Core/源Adapter/renderer/WPF/Catalog/测试尚须按未来代码授权实现，公共签名实际编译、window/模型clear、原Task/晚到return、baseline/显示观察、Golden/双Host/固定1920×1080三语/UIA/性能与长稳未运行；当前无代码开工授权，不以文档检查授运行资格 |
| 实际宿主、IM-006/007/020/027及父snapshot原Owner | 提供准确不可变源/CG图与资格/ROI租约/父证据、Read授权/访问域/当前实例和实际原bytes；消费软件方法在§15.2已定。缺哪项只阻对应实际读取/映射/编辑/Support，不阻其它Core |
| 用途/计量/客户Profile Owner | 代表原图/表面/校准真值、LOD/显示误差目标、原单位往返误差、性能目标/最低样本/长稳计划与资源容量。未给值为NotEvaluated/TargetPending或明确能力拒绝，不编造客户物理验收值 |
| 发布/部署与IM-066装配Owner | 实际H worker/AsunImage及format VersionRef hash、validator配置、受信manifest/ObjectRef表/权限/保留/旧包回退；当前非H/S Host不强制迁移。软件规则见§15.2.7，上游算法不重做 |
| 产品事实/导出/量测/意图Owner | 接收typed候选、持久化分层Support或旧.roi迁移的真实产品合同与确认；本模块无设备或质量放行权，现flat Intent不足时只读诊断，不自动提交。产品未采用用途不阻本模块无UI/显示设计 |

本轮自审复用已完成研究、已接收片与有效向量，未重算旧136-byte Golden或C5 P/Q。第一遍按外部装配走Create前Presentation→显式Lifetime/资源→Bind空控件→Attach真实submission→Acquire/Confirm→同OwnerRevoke/Return/OwnSession，补原Call/授权输入、同Task幂等与可追踪表；第二遍按正常/错root/缺资源/撤权/晚到/Unbind及Surface H/S的非调用/精度拒绝/未知format回退复核，修正UI预算可显式提供、Control实例Owner交叉混用、资源必需键和显示参数可调范围，避免借旧Core内容接收宣布UI可运行。全模块覆盖走查只按架构批准能力补实际缺口，不重复已接收片研究/全量审算。

本轮文档验证仅检查本页本地链接/围栏、公开新增类型唯一性、全必需资源键和三语/状态/错误映射、公开装配引用、接收状态与旧Golden字面保持，并在内存检查新增pinhole两个算例与投影误差界反例；不新增脚本、报告、工程或测试。官方依据复用§10.5/19.5，新增本地HALCON窗口/flush/pinhole与Microsoft [HwndHost walkthrough](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/advanced/walkthrough-hosting-a-win32-control-in-wpf)、[CompositionTarget Rendering](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/graphics-multimedia/how-to-render-on-a-per-frame-interval-using-compositiontarget)已直接读取；Rendering是绘制流程通知，不充当实际可见fence。未执行产品构建/Smoke、HALCON/GPU/WPF、现场Golden、真实IO、性能或生产验收。达到本文文档准备准则后停止，总控接收状态即可。

### 20.5 0.3.5-prep：BC-U1～U3限定闭合、兼容与反例自审

2026-10-12本永久原会话仅按barcode 0.2.4-prep §16.1报告的三项公共消费欠项修订本指导；复用§15.2.2/image-frame §4.3实际公开方法及既有§7/10.8导航/渲染证据，不另选算法、重查HALCON/DevExpress或重做Root/Close/三语全审。§20.4全部批准范围原结论与既有内容接收保持；本增量现在给出可决定的精确软件规格，不冒称现有程序集/产品已实现。

| 欠项 | 唯一签名/语义位置 | 本Owner结论及消费责任 |
|---|---|---|
| BC-U1 | §15.2.2.1 `ViewportImageFrameSourceFactory.Create(service,root,options)`→稳定Frames/Coordinates；`Register(ViewportPublishedFrameBinding)`/`Remove(bindingId)`；两STA预装配表 | 公共CPU生产者、内置payload接受性、source/epoch/root/consumer/预算和替换保真已闭合。barcode仍负责其本方factory、独立provider lease/PublishCopy/Retire、完整ImageFrame绑定及双Host输入映射；不能只传私有BarcodePixelBuffer或每帧替换Options.Frames |
| BC-U2 | §4.5.1 `ApplyAsync(new SelectOverlayObjectCommand(OverlayObjectSelectionRequest),ct)`；§4.5/4.6/3.5相关目标receipt/scene/event声明 | 完整稳定对象键直接选择/高亮、可用几何聚焦、重叠确定性、null清除、旧代/权限/事件/原Task已闭合；无几何记录明确拒绝影像选择，Host表格事实独立。barcode负责EvidenceId复合键及原generation、结果事件消回声映射，不使用中心点模拟点击，不产生ROI编辑 |
| BC-U3 | §4.7.1原`UpdateAsync(ViewportUpdate(base,空Sources且空Layers的完整Context),ct)`；`UpdateReceipt.EmptyTransition`及`GetSnapshot().EmptyTransition` | 原呈现Revoke→原工作退出→源Return、同代空图实际确认、未知禁新与Clear后同session正常Update闭合。barcode负责检查全部Previous与BlankPresentation、Retire自己key和新Present接线，不Unbind/Dispose后复活，不再Attach |

**兼容范围。** Core原五个异步方法、所有源/ROI/坐标端口接口及Root/OwnSession/Close签名不变；Core基础ApiVersion仍(0,1)，本页在该基础上冻结`OverlaySelection/1`与`EmptyUpdate/1`能力说明，未修改136-byte PlanGolden或C5字段/有效向量。新增命令/typed回执、BackendScene/ViewportReceipt/UpdateReceipt/ViewportSnapshot尾部可选字段与EventArgs可选属性、ViewportEventKind新增值是本目标规格扩充，旧源码构造仍能表达，**不承诺已编译record构造元数据/Deconstruct或穷尽enum switch二进制兼容**。WPF Assembly v0.2的原构造/Bind/Lifetime/Acquire/资源schema签名保持，内置renderer须实现新ObjectSelection投影与可信空scene；这属于现有Overlay/Empty能力实现责任，非新增编辑业务。公开CPU源adapter独立Assembly Contract v0.1且可选，旧自有FramePort/backend不强制改用它。

只有采用这些能力的实际Host/自有backend需要窄同步；本次按当前真实消费者指导核对后的名单如下，不沿用§10.6.1已完成的v0.2接线队列。barcode/variation-inspection已获0.3.5输入，不重复派发；各消费者原会话维护本方设计，总控仅转发。

| 真实消费者与消费位置 | 0.3.5影响分类及理由 |
|---|---|
| [ocr](../ocr/DEVELOPMENT-GUIDE.md) §10.5（源装配及Region/Word层） | **源装配和表行框高亮需窄同步**：实际Host明确采用已发布image-frame level0 CPU源及旧§15.2.2 IFramePort Adapter，并与内置renderer组合，尚未定位本次新增的公开生产者。Host可按§15.2.2.1预装配/登记该原已发布源；不要求OCR自行Publish/生产源或改Core。§10.2表选行→框高亮及§10.5“选中变化仅改本显示层高亮”是实际承诺，当前SourcePolyline层/SelectedRoiId尚未落到按完整对象键高亮的公开调用，可按§4.5.1补映射；SourcePolyline的ObjectId=LayerId，Interactive资格须显式满足，不能用中心点点击。图像指针拾取仍按原IRoiPort用途，不重审ImageContent接口/识读Core或强制新Clear |
| [segmentation](../segmentation/DEVELOPMENT-GUIDE.md) §13.1.2（步骤1/Host源输入） | **源装配需窄同步**：实际双STA内置viewport Host仍泛指§15.2已冻结源映射，scalar/mask输入须有认可payload生产者；如采用本CPU level0路线，具体接§15.2.2.1，源Owner/发布职责不转给分割Core。§13.1.2步骤3～4已有确定自有桥：SelectComponent生成组件bbox闭合Polyline，事件经原IntentReady/Selection映LayerId→Key；ClearAndDrain只撤本桥LayerId、保留宿主图像，不采用新对象ID命令或全源Empty Update |
| [mosaic](../mosaic/DEVELOPMENT-GUIDE.md) D.5/D.5.1（复制Pixels、Present及Clear切图） | **实际Host源装配与Clear需窄同步**：正文要求把本次Pixels复制成viewport独立帧并接内置renderer，但未列认可payload生产者，故CPU显示副本可经原image-frame发布Owner和§15.2.2.1登记；不能把任意buffer当内置payload。D.5.1当前Clear只描述原Revoke链、后续同session继续Present，需按§4.7.1明确是否承担整幅图清空；若承担，核EmptyTransition后才Clear成功，后续Update而非再次Attach。仅关闭/局部叠加清理保持原路线，不重审拼图Core、Pick/贡献支持 |
| [alignment-2d](../alignment-2d/DEVELOPMENT-GUIDE.md) §10.3/10.3A（SelectedCandidateId、FocusCandidate、Clear） | **表选指定候选高亮及实际Host整图Clear需窄同步**：§10.3A的CurrentItem→overlay高亮及AlignmentOverlay.SelectedCandidateId为实际承诺，旧几何/层替换尚未定位按指定对象高亮的公开动作，可在原桥按§4.5.1映CandidateId→完整Layer/Object键，不改IAlignmentViewerPort，不用中心点模拟点击。FocusCandidate已有按原candidate支撑/点生成SetViewCommand的确定路线，可保持，不强制改用新聚焦。Clear明示“清图/叠加引用”却未定位保持接纳的公开源清空调用，需对接§4.7.1，不能由void返回证明清图；仅撤本方叠加的操作保持原层清理。源对象由已绑定Control/UiBinding/Host预提供，本次不强制新增源工厂或重审搜索/模型 |
| [features-2d](../features-2d/DEVELOPMENT-GUIDE.md) §7.2/8.7/8.10 | **不受影响**：fixture明确使用自己的FixtureFramePayload及成套FixtureViewportPorts backend/lifetime，未把私有payload交内置renderer；Clear只移本attachment图层，保原source及其它Owner层。只消费原SetLayers/Update/Task链，不采用本次源工厂、ID命令或全源清空 |
| [coordinate-geometry](../coordinate-geometry/DEVELOPMENT-GUIDE.md) §11.4.1 | **不受影响**：Display为宿主已有Source/Context与只读桥，Present用SetLayersCommand；Clear只移ConsumerId/generation层、保图及其它层，不是全源Clear。未生产私有CPU payload或声明表行ID直接选择；Managed数学/Graph/Core不变 |
| [measurement-workbench](../measurement-workbench/DEVELOPMENT-GUIDE.md) A.6/A.7/A.11.5.1 | **不受影响**：接收完整ViewportContext及已配置Session/Root/Control/Options，UiChildren只Bind/SetResources/Unbind；LinkKind.Highlight经自有IWorkbenchViewportPort及原LinkQuery/StableIds结果，不直接构造新选择命令。未实现私有源producer、整图Clear或穷尽新事件/record解构，不因名称含Highlight重新派发 |
| [surface-features-3d](../surface-features-3d/DEVELOPMENT-GUIDE.md) C.2～C.4 | **不受影响**：消费surface-data/viewport原Surface发布场景；Highlight组合原场景overlay，Clear恢复BaseLayers且保Sources，明确不清整幅源。3D sourceIndices不是本次2D OverlayObjectRef，不强行换成新ID入口 |
| [reconstruction-3d](../reconstruction-3d/DEVELOPMENT-GUIDE.md) §10.4/10.4.1；[registration-3d](../registration-3d/DEVELOPMENT-GUIDE.md) §12.3/12.5 | **不受影响**：使用3D surface来源/宿主投影桥和原binding呈现/Detach；没有本次CPU发布源、2D ID命令或保持接纳的整源Clear调用。CandidateId/原点索引/NodeId保原桥含义，不把它们自动映为新2D选择 |
| [roi-geometry](../roi-geometry/DEVELOPMENT-GUIDE.md) 附录A.6；[ai-dataset-governance](../ai-dataset-governance/DEVELOPMENT-GUIDE.md) §8.2.1～2 | **不受影响**：分别通过自有IRoiEditorViewportBridge的Snapshot/Preview/Selection以及Preview Show/Clear/QueryClear/Close桥；本轮新增能力未被其接口消费，不因Selection/Clear同名而替换原桥。其它仅用不变Session/源端口或宿主自有影像桥的Core/计量/设备模块同样不触发同步 |

以上是消费者引用影响定位，不代做其内容审核；OCR补实际源装配及表选框高亮，segmentation仅补源装配，mosaic补复制源/实际整图Clear，alignment补指定候选高亮/实际整图Clear；均限原正文已承诺用途。未发现上述指导直接构造新增record全实参、解构其旧字段数或穷尽ViewportEventKind switch的消费声明，因此新可选回执/事件值本身**没有额外强制同步名单**；实际采用SelectOverlayObjectCommand/EmptyTransition的Host才处理新字段/事件，旧IntentReady/Selection及原Task语义保持。自有backend缺高亮/空场景时明确007或未确认，不返回假VisibleConfirmed。仅Core计划、计量、旧指针选择、已有来源/关闭消费者无需重审；本轮不追认V-C2/旧UI新增实现已通过，不重派已完成v0.2任务。资源schema viewport-ui-text/1无新增键，复用已有Empty/选择样式/错误文字。

| 限定反例/未来验收ID（未实现/运行） | 必须可判定结果 |
|---|---|
| VP-BC01 source producer | 原Publish成功后经工厂Register→原Read→内置renderer识别同私有payload；BarcodePixelBuffer/自造IFramePayload在内置路线007，禁止反射猜类型。producer Create/Register不Read/Acquire，src/tests工程未创建 |
| VP-BC02 source isolation/late | A/B同值不同实例、跨root/epoch/key/consumer拒绝；Gray16不截8位，RGB不换通道。尾块/halo窗口与原ActualWindow对应；Publish/Read晚到scope仍捕获；未知不Remove/Retire/重复读；一个entry在Borrow pending时占容量，新旧2 entries上限不隐扩 |
| VP-BC03 ID overlap/clear | 同中心两个对象、反ZOrder/反列表顺序按完整B键只高亮B；同ObjectId跨layer显式LayerId区分，同层重复ID拒绝。无几何/Label拒绝且保旧合法选择，null+Focus=false清除，null+Focus=true拒绝；不取图中心命中、不调用EditDraft/Commit |
| VP-BC04 revisions/permission/tasks | 旧context/源/坐标/几何/generation、隐藏/不可交互目标拒绝无读取；重放已接纳同OperationId在同调用权利仍有效时先查同完整输入记录、返回原Task不再增代，异内容016；同源纯view不改对象身份。撤权不发可见成功，迟到旧高亮不得覆盖新图，事件不合并/不伪PointerSample |
| VP-BC05 empty/refill | 非空r7/g4→空r8/g5→新非空r9/g6，Attach/Bind各一次；空更新不取源，所有旧presenter/backend原Revoke/Return和CopyRow退出后才Previous=true。空scene实际client匹配才BlankVisibleConfirmed；新源按r8为base正常Update，旧源由其Owner精确Retire |
| VP-BC06 unknown/revoke | Revoke、CPU scope、Return或blank Confirm受控闩锁：空Sources已采用也不成功/不接新Present；Same-task重复Clear不重复析构。ct/超时不阻Control安全撤旧，晚到GetSnapshot按同EmptyTransition更新；授权撤销允许中性清屏、任何带旧图/旧标题/任意Source的伪空提交仍拒绝。遮挡/最小化/无真实画面证据保持未确认，不能以移除View签Cleared |

两轮限定自审：第一轮从两Host公开依赖沿Create producer→Register→Read私有payload→按ID呈现→Empty Update→同session新Update逐字段走查，修正“每次发布换IFramePort”与无统计默认自动LUT的消费陷阱，明确同端口有界登记及手动格式窗；第二轮按重叠/无几何/null/重复ID、旧代/撤权、Read/Return晚到和空scene无首帧路线检查，补可信Control清屏与普通授权的精确分支、PreviousCleanup作用域和UI基线继续持有的边界。执行的文档/内存检查结果随本次最终回执；反例表是未来正式测试断言，不能称C#/HALCON/WPF测试通过。barcode D1/U1本方内容由其永久原会话修，本轮不写其它模块或共享记录。

本次定向文档检查通过：复用validate_docs.targets核本文本地链接，围栏/新增类型唯一性/唯一实施小节/原Session签名与资源schema一致；内存限定算例核同中心点击歧义与完整键定位、跨层键、8 DIP聚焦及椭圆轴极值、清空成功四条件、UInt16有效行/尾块与Clear后代数。未运行全仓检查或重算旧Golden/C5。

本次三项公共消费软件设计已闭合，达到限定范围即停止；不等待总控内容审核。真实消费编译、image-frame/renderer实现、native/实际空画面/选择可见、WPF/UIA/性能与现场资格均未执行或提升，未知后端行为仍须按以上断言验收，旧接收范围保持。

## 21. AOI.Main 影像窗口与原图闭环采纳

只读复核 [影像窗口交互指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-29-camera-image-viewport-interaction-design.md)、[原图预览与保存指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-29-camera-original-preview-and-save-design.md) 和 [连续采集序列指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-29-camera-capture-sequence-browsing-design.md) 后，Viewport 必须实现以下真实操作语义：

1. 每个影像窗口独立保存缩放、偏移、模式和当前帧；工具栏命令只作用于当前窗口，不能用一个全局 zoom 值驱动多窗口。
2. `1:1` 必须以源像素到屏幕像素的数学关系验收；Fit、鼠标中心缩放和拖拽平移都要保留可逆的图像坐标映射，不能把 `PictureSizeMode` 或缩略图当作算法。
3. 全景浏览可以使用有界缩略图/LOD，但选中窗口、原始像素探针和无损导出必须读取全分辨率不可变快照；显示位图、原帧、导出位图分别计账并确定性释放。
4. 异步全分辨率转换、编码和帧切换必须携带 `CameraId + FrameRevision + DisplayGeneration`；选择或帧已变化时丢弃迟到结果并释放其资源，不得覆盖当前呈现。
5. 多帧浏览由宿主的 `CaptureSequence` 持有；Viewport 只持有当前帧租约和索引。启动前做原图内存预检，采集中的规格变化、取消、断开和窗口关闭都必须返回部分状态与释放回执。
6. 无损保存必须读取捕获操作开始时的不可变快照，临时文件完整写入并回读后原子改名；Viewport 不从屏幕截图或缩放结果反推原图，也不静默覆盖同名文件。

这些事实补强本页显示、租约、generation 和资源条款，不把 AOI.Main 的 WinForms 控件、客户相机数量、像素格式默认或产品命令迁移为公共契约。实现验收至少增加网格像素 `1:1`、同分辨率帧保持中心坐标、分辨率变化 Fit、原图像素值探针、批量导出快照一致性、序列容量预检和旧帧迟到淘汰。


## 20.1 AsunMeasure 参考采纳与 WPF 限定（2026-10-04）

只读快照中的 `RoiSkiaRenderAdapter` 可借鉴“先生成确定性绘制命令，再交给渲染后端”的思路；`ImagePreviewControl` 只能作为 WinForms/Mono8 历史行为参考。Viewport 必须保留源帧/显示代/物理坐标与屏幕坐标分离，渲染命令不拥有 HALCON、GPU 或帧 lease。

禁止直接复制 `ImagePreviewControl`、`System.Drawing` 位图生命周期或 Skia 具体控件作为 WPF API。超大图必须走本指导规定的 Tile/Pyramid、LOD、latest-wins、预算和迟到淘汰；3D 显示、拾取和测量值必须由独立端口提供，不能从截图或渲染深度反推量测事实。WPF/DevExpress 25.2.3、1920×1080、三语、UIA、DPI 和关闭排空必须以真实目标控件验收。

## 22. PCBA AOI 双视图在线显示场景（2026-10-06）

只读对照 `H:\docs\40-development\41-vision-platform\05-engineering\2D_3D视图与证据渲染开发指导.md` §3.3、§3.4、§10.1（文件 SHA-256：`6447EA61D616195ECAAD171A4444FACBC2ADC6F69D1350AE674BD275B8A4A894`）。来源标注为 `DEV-PLT-ENG-002` v1.5 候选、2026-10-04，状态 `DocMapped`/待 root 审核；其公开手册和回放设计不能证明目标设备的实时性能或生产资格。本节只吸收可复用的显示任务语义，不把来源中的产品 DTO、检测完整性、拼接算法或产品页面布局变成 Viewport 的事实 Owner 或通用 API。

对于宿主配置了“在线总览 + 当前 FOV”消费方式的场景，显示必须作为两个有界投影工作：板级总览接收合法来源后的增量覆盖/状态更新；当前 FOV 视图显示同一稳定 FOV 身份的全分辨率图像及其匹配版本的结果覆盖。操作员明确固定某 FOV 后，总览持续更新不得抢换该选择；“固定选择”和“跟随最新”要能从 UI 状态看出，切回跟随是明确的目标变更。帧、结果、权限或坐标未就绪时显示对应等待/不可用/异常状态，不得沿用上一 FOV 的 OK/NG。缺来源身份或版本不匹配时拒绝该视图更新；单个视图失败不应清除另一个仍有效且获准的视图。

所有输入、异步工作和呈现回执继续使用现有 source identity、source/coordinate/presentation revision 与 display generation 绑定。来源中的 BoardRun、Attempt、FOV、曝光组、实际位置/时间、结果版本和授权只能由宿主现有 Owner 提供；本节只用§3.5/8.4公开DTO，也不允许 Viewport 从到达顺序推断身份。固定/跟随通过§8.4的FollowSourceCommand表达，板次/结果/曝光身份仍由宿主投影到CorrelationId/源修订，产品映射不足仅阻断其适配，禁止用ViewModel私有字段、文件名或列表索引补猜。

图像解码、坐标变换、配准/派生和纹理准备在有界后台工作中执行；Dispatcher 只提交仍匹配当前 generation、授权及源修订的显示状态。取消、切源、撤权和关闭要沿现有排空/租约流程等待实际资源退出。浏览、定位、选择或框选只产生显示/选择意图，不隐式移动相机或发设备命令。跨 FOV 检查项所需的 ROI、邻域/上下文及完整曝光归集，由 RUN/采集和检测 Owner 完成一次；拼图覆盖、任一 FOV 已检或最后一帧到达都不等于检查项完整，Viewport 不建第二个归集器。

在线双视图验收必须在真实 WPF 宿主证明“画面已可见”，不能以属性赋值、Dispatcher 完成或单元测试的 ViewModel 状态冒充；记录帧组可读时刻、对应总览贡献可见时刻、结果可用/所选 FOV 结果可见时刻，并分别报告配准/派生、排队、上传、绘制耗时。未显示、取消、切选和超时均保留在分母或单独列明，不能只统计成功快样本；跨时钟相减须先有同步证据。压测同时计入 CPU/GPU、解码与上传 staging、tile/overlay、旧 generation 尚未释放资源及 UI 复制；迟到淘汰不等于资源已释放。消费者的具体延迟、内存和可视面积阈值由其 PerformanceProfile/PageContract 冻结，本模块不从来源候选虚构通用阈值；可视面积按固定1920×1080物理视口内记录的实际客户区为分母，排除工具栏、标题、空白及遮挡，不把两个不足尺寸的视图面积相加达标。

回放/真实 UI 断言至少覆盖：连续总览增量更新且固定 FOV 不变；显式切换固定/跟随；双曝光缺一、跨 FOV 待齐、错误板次/旧 hash、结果先于图像、乱序和迟到回包；切板、撤权、慢 UI、GPU/backend 故障及关闭；确认不串图、不残留旧判定，独立视图可按来源状态恢复且资源最终归还。此场景只补充 Viewport 呈现及资源验收，不表示当前模块已完成该功能或已通过 WPF、性能、HIL、计量或生产验收。


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

## 附录 A：当前Module API Contract及内容接收边界

唯一当前Module API为本页v0.1：§3.3～3.6、§4.1～4.7、§5/6、§8.4、§10.6定义公开声明/操作/Owner/版本；§7/8定义确定路线；§11/13/14给真实落点、Host、测试与Benchmark。旧正文的“候选”只用于产品映射/客户策略/现场资格，不允许把已闭合Core字段退回给实现者猜。名称变更/格式/单位/事件/所有权变化先修订本页并说明影响，不能由代码失败擅改语义。

0.3.5-prep的BC-U1～U3增量及兼容边界见§20.5，0.3.4-prep全批准范围原文档结论见§20.4；Core API0.1、WPF Assembly Contract v0.2、image-frame源适配Assembly Contract v0.1与资源schema viewport-ui-text/1分别版本化。本原会话已完成内容审核，后续产品/运行门保持。公开构造入口：Core `ViewportRootFactory()`→`Create(RootOptions)`→root.CreateFactory()→Create(Options)；纯操作 `ViewportPureOperations()`；UI `ViewportControl()`→IViewportControlBinding.BindAsync。这些是目标API，现有工程落点不等于已存在成员；没有可编译代码实现或运行证据。V-C1～C3已经主控按§17六项规格内容接收并标ModuleCoreImplementationReady；V-U1/V-A1指导内容接收保持，非纯Core、真实WPF/GPU/backend/产品NotReady；V-A1-C5本版增量按§15.2.5.8已限定指导内容接收，不标纯CoreReady，不提升运行/生产资格，其它切片仍逐项接收，ImplementationSpecificationReady/Integration/Production再按§18受影响门关闭。
