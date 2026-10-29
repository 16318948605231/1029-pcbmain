# 高度场、点云与表面数据模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2, C3, C4, C5`

- 模块：`IM-031 surface-data`；来源映射：`PKG-027 / SM-012`。
- 版本：`0.6.0-prep`；日期：`2026-10-11`；状态：C1–C5已接收规格保持；全批准范围的本原会话文档准备结论见§19。本版补桥、元数据codec、有限根及H封送/隔离规格，未实施或运行；真实桥、H/Viewport及运行资格未提升。
- 永久会话：`01a10306-ff29-7463-a87d-5727c4691bbf`；任务：`IM-REVIEW-20261009/surface-data`。
- 固定基线：C# / .NET 10；视觉桥经 `ImageLibDotNet.cv2` 使用 HALCON **26.05**；不直连 `HOperatorSet/halcondotnet.dll`，不检查 AsunImage 内部。
- 规划消费者：无 UI 的 3D Replay/检测输入工具、无 UI 的计量输入/已有网格诊断工具；查看通过独立 Viewport 挂接。
- 本轮仅修订本文。没有产品代码、工程、运行验收或新参考快照；不改变平台 Contract、资源/坐标 Owner 或制程判定。
- 模块级设计评审态：`DesignReview`（方案可评审）。§19「全批准范围的文档准备、自审与剩余Owner」已给出本模块当前批准范围的软件设计与自审结论；该状态只表示方案可供评审，不表示已实现、已集成、已测性能、已过 WPF/HIL 或已获生产资格。

本版补齐整模块职责，替代 `v0.3-prep` 的扁平描述器和仅计划接口。结构、实际读取、有效性、来源、物理映射和资格分别表达；不再把计划的 `Complete` 当实际数据完整。已交付版本/消费者未建立证据，本次预发布契约不承诺与旧候选二进制兼容；开工前若发现真实旧消费者，先补显式迁移，不静默兼容。

唯一架构入口为[独立模块架构](../INDEPENDENT-MODULE-ARCHITECTURE.md)，会话映射为[模块索引](../MODULE-INDEX.md)。历史 [PKG-027](../../shared-modules/packages/PKG-027_SurfaceData.md)、[SM-012](../../shared-modules/modules/SM-012_surface.md)用于来源/消费关系，不定义第二套实施 API。本文自身 API 不冒充产品 Schema；平台集成映射由原 Owner 接收。

## Core implementation binding

| 交付物 | 唯一工程/命名空间 | 依赖及用途 |
|---|---|---|
| Core DLL | `src/Modules/surface-data/Asun.Modules.SurfaceData.Core/Asun.Modules.SurfaceData.Core.csproj`；`Asun.Modules.SurfaceData` | `Microsoft.NET.Sdk / net10.0`，仅 .NET BCL；包含 §2 值协议、§3 API、§4–6 托管流程和注入端口 |
| BCL 验证 Exe | `tests/Modules/surface-data/Asun.Modules.SurfaceData.Core.Tests/Asun.Modules.SurfaceData.Core.Tests.csproj`；`Asun.Modules.SurfaceData.Tests` | `Microsoft.NET.Sdk / net10.0 / OutputType=Exe`，只引用 Core 与 BCL；同一入口执行 §10 全部指定断言、A/B 宿主和受控端口，不另建 TestHost DLL |
| HALCON 适配 DLL（后续） | `src/Modules/surface-data/Asun.Modules.SurfaceData.ImageLib/Asun.Modules.SurfaceData.ImageLib.csproj`；`Asun.Modules.SurfaceData.ImageLib` | 引用 Core；§7/17，父进程只监督值协议，worker才引用既定AsunImage |
| 隔离HALCON Worker（后续） | `src/Modules/surface-data/Asun.Modules.SurfaceData.ImageLib.Worker/Asun.Modules.SurfaceData.ImageLib.Worker.csproj` | net10.0-windows / Exe，引用Core与既定AsunImage；每次H调用一个有硬commit上限的进程，无窗口/设备/存储发布权限 |
| 源/坐标桥 DLL（后续） | `src/Modules/surface-data/Asun.Modules.SurfaceData.Adapters/Asun.Modules.SurfaceData.Adapters.csproj`；`Asun.Modules.SurfaceData.Adapters` | 引用Core及IM-006 Resources/Core、IM-007、IM-066 Contracts公开程序集；§16精确接线，Core保持BCL-only |

本轮只允许写本文。获准实现才允许写上述对应工程目录；禁止其它模块、共享契约、产品 Shell/Domain/Integration、设备 SDK、AsunImage 内部、参考项目/原件。当前没有 `.git`，代码开工须绑定权威仓库/分支或可审计快照；不阻断文档修订。工程尚未创建，不先造空项目充当进度。

2026-10-10主控已接收C1描述/集合/plan、C2受控Source读取/选择/关闭、C3本地坐标转交及Simulator、C4已有网格组合检查的六项文档规格，状态为 `ModuleCoreImplementationReady`。绑定仍是预定工程与允许路径，不表示工程已建、代码已编译/测试或本轮授权写产品代码；真实IM-006/066源桥、IM-007映射链、H/X/Viewport与运行资格分别按§12保留后续门。

2026-10-11增量仅为§15 C5父贡献公开读取，沿同一Core DLL/BCL Exe工程与禁止路径，不改§2–5已接收API v0.4/Factory Api0.4。C5使用独立 `SurfaceContributionFactory` 和 Contribution API v0.1，按需装配；没有贡献的旧消费者照常调用C1–C4，不回退其状态、不机械新增DLL/UI/测试工程。

## 1. 职责、Owner 与完整功能链

模块承载**已有**规则高度场、非规则 XYZ 点集、显式三角网格及多层集合，验证布局/域/单位/来源，计划有界读取，扫描数值及独立属性状态，保留源索引，转交已知坐标映射，检查已有网格的组合结构，并桥接 HALCON 数据表达。全部业务能力无 UI 可调用。

| 功能/输入→结果 | 实施位置 | Owner 与非目标 |
|---|---|---|
| 不可变描述/多层集合→字段诊断 | §2、§3 Validate、§4 | SurfaceData拥有模块值协议；上游拥有来源事实/修订；集合不自动选最高/最近层 |
| range/tile + 字节/项数预算→确定计划 | §4 Plan | 不读payload，不证明可测/覆盖完整，不降采样 |
| 源端口→原值/状态/原因/来源/索引→回执 | §5 StartRead | IM-006拥有allocation/lease；本模块拥有本次CPU临时副本和短read session |
| 高度/XYZ + 已有映射引用→坐标块 | §5.3、§3坐标端口 | IM-007拥有frame/链/映射数学；不猜pitch/轴/原点/变换，不求解配准 |
| 显式已有faces→索引/边关联报告 | §6 StartInspectMesh | 只检组合结构；共线、相交、闭合体积资格与几何容差归视觉/计量Owner |
| 可用数据→HALCON→显式坐标区间筛选/属性回读 | §7 | 不生成normals/mesh，不做重建/滤波/离群/体素/参考面/特征的第二算法 |
| 重开/外部格式→保真声明及拒绝 | §8 | 文件对象/事务/压缩归IM-066；不定义数据库/CAS/head/journal或质量事实 |
| 两个无UI消费者→同一包接入 | §9–10 | 宿主拥有用途、保留结果、目标关联、参数批准、生产事实及放行 |

单向依赖：宿主→Core；ImageLib adapter→Core+ImageLibDotNet；IM-006/007/066桥由宿主显式注入Core端口。Core不引用WPF/WinForms/DevExpress/HALCON/GPU/设备/文件数据库实现/产品类型，不用静态当前表面/标定、服务定位器或隐藏窗口初始化。宿主创建/释放端口服务，模块不取得其整体所有权。

不做PCB/SPI/AOI/涂覆等制程判定、目标关联、量测定义/不确定度资格、厚度/体积公式、放行/审批/设备动作、训练/在线学习。显示LOD/色彩/Z倍率、score、文件存在、非空object model、完整数据都不是生产PASS；人工/AI建议不改事实或设备命令。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.SurfaceData.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"Core 不引用 WPF/WinForms/DevExpress/HALCON/GPU/设备/文件数据库实现/产品类型"。

**Blazor/Web**：高度场/点云的 Web 预览通过 tile 粒度 HTTP Range 分片加载；浏览器只渲染当前视口对应的 tile；有效域掩码随 tile 一起传递，前端不自行推断域。

**AI 推理 Tiling**：本模块是 3D AI 推理的表面数据来源；`ai-inference` 按 `SurfaceRef` 请求表面 tile，本模块按 tile 粒度提供只读访问；Open3D `PointCloud.cpp`（SHA-256 `9d31ff09...`）的 `VoxelDownSample`/`EstimateNormals` 已作为本模块采样/法向语义参照（见 §17 已读证据）。

**HALCON 双跑**：本模块桥接 HALCON 的 `ObjectModel3D` 表达；本模块自身不执行拟合算法，HALCON 备选 CI 在消费表面数据的下游视觉模块（`surface-features-3d`/`reference-surface`）中执行。

## 2. Module API Contract v0.4：不可变数据

§2–3为C1–C4唯一当前API v0.4；独立可选C5 Contribution API v0.1仅在§15定义，不改本节公开形状。代码是**待实现的精确公开声明**，不是已编译程序集；规则由随后的表和流程冻结。只用BCL，ImmutableArray位于目标框架自带程序集，不加NuGet。列表在边界深复制/冻结，default数组非法；调用方不得unsafe修改存储。名称按Ordinal比较，不trim/大小写折叠。

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
namespace Asun.Modules.SurfaceData;

public enum SurfaceKind { HeightField = 1, PointCloud = 2, TriangleMesh = 3 }
public enum LengthUnit { Meter = 1, Millimeter = 2, Micrometer = 3 }
public enum SampleDomain { Vertex = 1, Face = 2 }
public enum ScalarType { UInt8 = 1, UInt16 = 2, UInt32 = 3, UInt64 = 4,
    Int16 = 5, Int32 = 6, Int64 = 7, Float32 = 8, Float64 = 9 }
public enum ByteOrder { LittleEndian = 1, BigEndian = 2 }
public enum FieldRole { X = 1, Y = 2, Z = 3, Height = 4, Attribute = 5,
    TriangleIndices = 6, SourceIndex = 7, State = 8, Reason = 9, Origin = 10 }
public enum SampleState : byte { Unknown = 0, Valid = 1, Invalid = 2 }
public enum OriginKind { Observed = 1, Interpolated = 2, Repaired = 3,
    Filtered = 4, Cad = 5, Fallback2D = 6, Unknown = 7 }
public enum IndexKind { StableOrdinal = 1, DeclaredField = 2 }
public enum ValidityKind { Uniform = 1, PerItem = 2 }
public enum OriginBindingKind { Uniform = 1, PerItem = 2 }
public enum RangeKind { Ordinal = 1, Tile = 2 }
public enum SelectionKind { PreserveAll = 1, ValidPositions = 2 }
public enum IntegrityScope { NotVerified = 1, RequestedBytes = 2, FullBuffers = 3 }
public enum Completeness { Complete = 1, Partial = 2, Empty = 3, NoResult = 4, Unknown = 5 }
public enum OperationOutcome { Completed = 1, Cancelled = 2, TimedOut = 3, Failed = 4 }
public enum OperationPhase { Accepted = 1, Opening = 2, Reading = 3,
    Mapping = 4, Inspecting = 5, Delivering = 6, Draining = 7,
    Drained = 8, ResourcesReleased = 9, Terminal = 10 }
public enum ServicePhase { Open = 1, Closing = 2, Closed = 3 }
public enum SurfaceErrorCode { Input = 1, Layout = 2, Unit = 3, Frame = 4,
    Validity = 5, Topology = 6, Capability = 7, BudgetExceeded = 8,
    BudgetUnavailable = 9, Cancelled = 10, Timeout = 11, Resource = 12,
    Io = 13, Native = 14, Version = 15, Closed = 16, Consumer = 17,
    Conflict = 18, Integrity = 19, Internal = 999 }

public readonly record struct SurfaceKey(string Id, ulong Revision);
public readonly record struct FrameReference(string Id, ulong Revision, LengthUnit Unit);
public readonly record struct MappingReference(string Id, ulong Revision);
public readonly record struct BufferSlice(string BufferId, long Offset, int Length);
public readonly record struct TileWindow(int X, int Y, int Width, int Height);
public sealed record BufferDescriptor(string Id, long ByteLength, string Sha256);
public sealed record FieldLayout(string BufferId, long Offset, long ElementStride,
    long RowStride, ByteOrder ByteOrder);
public sealed record ValueEncoding(ScalarType Type, int Components,
    string UnitId, double Scale, double Bias);
public sealed record ValidityBinding(ValidityKind Kind, SampleState UniformState,
    string? StateFieldId, uint UniformReason, string? ReasonFieldId);
public sealed record OriginBinding(OriginBindingKind Kind, int UniformOriginId,
    string? OriginFieldId);
public sealed record FieldDescriptor(string Id, FieldRole Role, SampleDomain Domain,
    ValueEncoding Encoding, FieldLayout Layout, ValidityBinding Validity,
    OriginBinding Origin, bool FrameDependent);
public sealed record OriginEntry(int Id, OriginKind Kind,
    ImmutableArray<SurfaceKey> Parents, string MethodId, string MethodVersion,
    string ParametersSha256, bool HasExactParentIndex);
public sealed record GridDescriptor(int Width, int Height, MappingReference Mapping,
    long ParentColumnOffset, long ParentRowOffset);
public sealed record SourceIndexBinding(IndexKind Kind, long OrdinalBase,
    SurfaceKey Root, string? FieldId);
public sealed record SurfaceDescriptor(SurfaceKey Key, SurfaceKind Kind,
    long VertexCount, long FaceCount, LengthUnit Unit, FrameReference Frame,
    GridDescriptor? Grid, SourceIndexBinding VertexIndices,
    SourceIndexBinding? FaceIndices, ImmutableArray<BufferDescriptor> Buffers,
    ImmutableArray<FieldDescriptor> Fields, ImmutableArray<OriginEntry> Origins);
public sealed record SurfaceSet(string Id, ulong Revision,
    ImmutableArray<SurfaceDescriptor> Layers);
public sealed record SurfaceRange(SampleDomain Domain, RangeKind Kind,
    long Start, long Count, TileWindow? Tile, bool AllowEmpty);
public sealed record ResourceBudget(string ProfileId, ulong ProfileRevision,
    long MaxItems, long MaxReadBytes, long MaxResidentBytes, int MaxBlockItems,
    int MaxIssues, TimeSpan OperationLimit);
public sealed record SurfacePlan(SurfaceRange Range,
    ImmutableArray<string> FieldIds, long RequestedItems, long ReadBytes,
    long PackedBytes, long ResidentUpperBound, int BlockItems);
public sealed record SurfaceError(SurfaceErrorCode Code, string Path,
    long? Ordinal, string Detail);
public sealed record ValidationResult(ImmutableArray<SurfaceError> Errors,
    bool IssuesTruncated);
public sealed record PlanResult(SurfacePlan? Plan, ValidationResult Validation);
public sealed record SurfaceReadRequest(SurfaceDescriptor Descriptor,
    SurfaceRange Range, ImmutableArray<string> FieldIds,
    SelectionKind Selection, bool ReadCoordinates,
    FrameReference? TargetFrame, MappingReference? Transform,
    ResourceBudget Budget, ulong Generation);
public sealed record MeshRequest(SurfaceDescriptor Descriptor,
    ResourceBudget Budget, ulong Generation);
public readonly record struct PositionValue(double X, double Y, double Z,
    SampleState State, uint Reason, int OriginId);
public sealed record MeshIssue(long FaceOrdinal, string Kind,
    long VertexA, long VertexB);
public sealed record MeshReport(long FacesChecked, long BoundaryEdges,
    long NonManifoldEdges, long OrientationConflicts, long DuplicateFaces,
    long RepeatedIndexFaces, bool AllIndicesInRange,
    ImmutableArray<MeshIssue> Issues, bool IssuesTruncated);
public sealed record SurfaceReceipt(Guid OperationId, ulong Generation,
    SurfaceKey Input, OperationOutcome Outcome, Completeness Completeness,
    long RequestedItems, long DeliveredItems, long ValidPositions,
    long InvalidPositions, long UnknownPositions, IntegrityScope Integrity,
    MeshReport? Mesh, ImmutableArray<SurfaceError> Errors, bool IssuesTruncated);
public sealed record OperationSnapshot(Guid Id, ulong Generation,
    OperationPhase Phase, long Sequence, long DeliveredItems,
    bool CancellationRequested, bool DeadlineExceeded);
public sealed record OperationObservation(OperationSnapshot Snapshot,
    SurfaceReceipt? Terminal, bool WaitExpired);
public sealed record CloseReport(ServicePhase Phase, int ActiveOperations,
    bool ResourcesReleased, bool WaitExpired);
public sealed record SurfaceOptions(int ApiMajor, int ApiMinor,
    int MaxLayers, int MaxFields, int MaxBuffers, int MaxOrigins,
    int MaxActiveOperations, long MaxServiceResidentBytes,
    TimeSpan CloseObservationLimit);
public sealed record SurfacePorts(ISurfaceSource Source,
    ISurfaceCoordinatePort? Coordinates, TimeProvider Time);
public sealed record FactoryResult(ISurfaceDataService? Service,
    ImmutableArray<SurfaceError> Errors);
public sealed record StartResult(ISurfaceOperation? Operation,
    ImmutableArray<SurfaceError> Errors);
```

### 2.1 字段约束与数值

| 字段 | 有效域、来源和拒绝 |
|---|---|
| Id/ProfileId/MethodId/MethodVersion/UnitId | ID为1–128个ASCII字母/数字及 `._:-/`；UnitId为注册标识。同引用不同内容为Conflict；revision正ulong，耗尽后上游换Id。不用latest/路径/板号作身份 |
| Sha256/ParametersSha256 | 非空时64个小写十六进制字符，SHA-256；Buffer摘要必填，非Observed/Unknown来源的参数摘要必填。不证明真实性/授权/标定合格 |
| 数量/字节 | VertexCount/FaceCount/ByteLength/Offset非负long，stride正；所有乘加checked。单次Memory/Span及块项数<=int.MaxValue，不分配不可表示单数组 |
| Kind | HeightField正宽高且width*height=VertexCount，FaceCount=0、有Grid、一个Height、无XYZ。PointCloud：Grid=null、FaceCount=0、各一个X/Y/Z。TriangleMesh：Grid=null、各一个X/Y/Z、FaceCount可0且显式一个TriangleIndices。不猜拓扑，未知enum拒绝 |
| 原值编码 | 元素宽度1/2/4/8；Components 1–4，组件紧密连续。XYZ/Height/索引/状态/原因/来源为1，TriangleIndices为3。不把Int64源索引转double。拓扑UInt32/UInt64，解码后<=long.MaxValue |
| 物理值 | physical=raw*Scale+Bias；Scale有限非零、Bias有限，raw/乘积/最终值都检查有限。保留负高度/有效0，不夹紧/补零。已损失float32精度不靠double恢复；用途精度由上游/Profile负责 |
| 单位 | FrameReference.Unit=SurfaceDescriptor.Unit，TargetFrame.Unit也必须相同；结构阶段即拒绝跨单位。XYZ/Height UnitId匹配Unit的m/mm/um，Scale/Bias已转到该单位，不再自动乘比例。结构列UnitId=`1`、Scale=1、Bias=0。属性上游登记单位，概率/不确定度语义不由模块猜 |
| Field layout | AoS多个字段共buffer不同offset；SoA不同buffer或offset及各自stride。正向stride，不支持压缩/packed/负stride。offset是字段首元素绝对buffer偏移；HeightField Vertex列按row/col用RowStride，其它Domain RowStride=0 |
| 容量 | 平列N>0末字节offset+(N-1)*ElementStride+componentBytes；N=0不读且offset<=length。网格末字节offset+(height-1)*RowStride+(width-1)*ElementStride+componentBytes。ElementStride>=componentBytes；RowStride>=(width-1)*ElementStride+componentBytes；末字节<=ByteLength，不用N*stride错误拒绝无尾padding布局 |
| 有效性 | Uniform明示Unknown/Valid/Invalid且StateFieldId=null；PerItem绑定同Domain UInt8 State列。缺声明拒绝。原因UInt32字典码，0未提供；不猜厂商码含义。Valid非有限是错误，Invalid/Unknown保留原编码但不当有效物理值 |
| 独立属性 | 自己的状态/原因/来源及完整Domain长度，不沿用位置mask。半截属性拒绝；声明Valid但坏数值拒绝操作，显式Invalid/Unknown才不可用保留。Normals三分量为属性，零向量不获法向资格 |
| 控制列 | State/Reason/Origin/SourceIndex/TriangleIndices自身Uniform Valid、结构编码，无循环引用。State仅0/1/2，Origin索引Origins且Domain匹配。控制列不递归应用自己的来源列 |
| 来源 | Origin Id恰为0..n-1、顺序固定。Observed：MethodId=observed、MethodVersion=1，参数摘要可空；Unknown可空且HasExactParentIndex=false。派生有Parents、方法/版本/参数摘要。Fallback2D不能Valid高度/XYZ；插值Valid仍是Interpolated |
| 源索引 | range是当前载体Ordinal，SourceIndex是Root原位置。StableOrdinal=OrdinalBase+ordinal，Base>=0、Root明示；DeclaredField为同Domain Int64非负索引、Base=0。Mesh三角索引是当前vertex ordinal，不是Root索引。仅按请求范围验唯一，不冒充全表；多返回按层分开 |
| Grid | Mapping解释父源整数中心(col,row)→本Frame的XY；crop使用ParentOffset+本地row/col，offset非负。数值/域归IM-007，不再存一份pitch/原点；旋转/非正交也走此端口 |
| 集合 | SurfaceSet非空Layers且各Key唯一、<=MaxLayers，保生产者次序。层可不同尺寸/frame/unit。无扁平MultiSurface/默认max-min；请求显式选一层，整集合由宿主逐层调用 |

相同buffer Id的长度/hash必须一致；FieldId/BufferId/Origin Id唯一。DTO不含native/GPU handle、lease、裸指针、私表、VM或生产结果。SurfaceKey/FrameReference/MappingReference是本地精确引用，跨模块类型仅在桥中映射。

控制列精确类型：State=UInt8、Reason=UInt32、Origin=UInt32（解码须<=int.MaxValue）、SourceIndex=Int64；仅TriangleIndices允许3组件UInt32/UInt64。ValidityBinding的Uniform必须StateFieldId=null；PerItem必须StateFieldId非空且UniformState=Unknown（未用字段规范值）。ReasonFieldId非空时UniformReason=0，否则使用UniformReason。OriginBinding的Uniform必须OriginFieldId=null/UniformOriginId在表内；PerItem必须OriginFieldId非空/UniformOriginId=0。控制列自身Origin为Uniform Id0，该条不用于提升数值来源。SurfaceDescriptor.Origins至少一条，至少Id0可表达Unknown；FaceIndices仅Mesh必填，其它kind必须null。同SurfaceKey的嵌套内容不同拒绝Conflict；本服务不维护跨调用身份注册表，跨请求一致性由不可变Source保证。

### 2.2 参数、计划与推荐

资源值来自有身份/修订的消费者Profile，不含工艺值。Budget全部数量/字节上限和MaxIssues>0，OperationLimit在(0,24h]；Options各上限>0，CloseObservationLimit在(0,24h]。等待参数[0,24h]，0仅观察；执行期限基于注入TimeProvider单调时间，不用UTC作释放证据。

Plan.BlockItems是可解释内存建议：取min(MaxBlockItems,RequestedItems,int.MaxValue)，按§4上界二分取最大可容纳整数；非空容不下1项则拒绝。输入/域/字段/Profile修订改变旧plan失效。无视觉噪声阈值自动推荐/插值/滤波默认；仅Profile显式修订产生新请求，不运行中降采样。

## 3. 公开 factory、端口、结果与关闭

```csharp
// 续用§2的using与namespace；具体实现尚未创建。
public static class SurfaceDataFactory
{
    public static FactoryResult Create(SurfaceOptions options, SurfacePorts ports);
}
public interface ISurfaceDataService
{
    ValidationResult Validate(SurfaceSet surfaces);
    PlanResult Plan(SurfaceReadRequest request);
    StartResult StartRead(SurfaceReadRequest request, ISurfaceBlockConsumer consumer,
        CancellationToken cancellationToken);
    StartResult StartInspectMesh(MeshRequest request, CancellationToken cancellationToken);
    ValueTask<CloseReport> CloseAsync(TimeSpan observationLimit, CancellationToken waitToken);
}
public interface ISurfaceOperation
{
    OperationSnapshot Snapshot { get; }
    Task<SurfaceReceipt> Completion { get; }
    void RequestCancel();
    ValueTask<OperationObservation> ObserveAsync(TimeSpan observationLimit,
        CancellationToken waitToken);
}
public interface ISurfaceSource
{
    ValueTask<ISurfaceReadSession> OpenAsync(SurfaceDescriptor expected,
        CancellationToken cancellationToken);
}
public interface ISurfaceReadSession : IAsyncDisposable
{
    SurfaceDescriptor Descriptor { get; }
    IntegrityScope Integrity { get; }
    ValueTask<int> ReadIntoAsync(BufferSlice slice, Memory<byte> destination,
        CancellationToken cancellationToken);
}
public sealed record CoordinateBatch(SurfaceDescriptor Descriptor,
    FrameReference Target, MappingReference? Transform,
    ImmutableArray<long> Ordinals, ImmutableArray<PositionValue> InputPositions);
public sealed record CoordinateReply(FrameReference Frame, LengthUnit Unit,
    ImmutableArray<PositionValue> Positions, MappingReference AppliedMapping);
public interface ISurfaceCoordinatePort
{
    ValueTask<CoordinateReply> MapAsync(CoordinateBatch batch,
        CancellationToken cancellationToken);
}
public interface ISurfaceBlockConsumer { void OnBlock(in SurfaceBlockView block); }
public readonly ref struct SurfaceFieldView
{
    public FieldDescriptor Descriptor { get; }
    public ReadOnlySpan<byte> PackedValues { get; }
    public ReadOnlySpan<SampleState> States { get; }
    public ReadOnlySpan<uint> Reasons { get; }
    public ReadOnlySpan<int> OriginIds { get; }
}
public readonly ref struct SurfaceBlockView
{
    public Guid OperationId { get; }
    public ulong Generation { get; }
    public SurfaceDescriptor Descriptor { get; }
    public SampleDomain Domain { get; }
    public FrameReference CoordinateFrame { get; }
    public ReadOnlySpan<long> Ordinals { get; }
    public ReadOnlySpan<long> SourceIndices { get; }
    public ReadOnlySpan<PositionValue> Positions { get; }
    public int FieldCount { get; }
    public SurfaceFieldView GetField(int index);
}
```

声明中的factory方法和View访问器仅列签名，必须在实现工程提供方法体；不是把无方法体static类当可编译示例。Factory为唯一服务构造，options/ports非null，Source/Time必填、Coordinates可空。ApiMajor=0/Minor=4才接纳；错误Service=null/Errors非空，成功Service非null/Errors为空。Factory不读源/开native/启动线程/扫描授权，冻结Options，服务实例隔离，端口只借用。record直接按§2构造后校验；View仅Core内部构造，无公共constructor，GetField越界ArgumentOutOfRangeException。

Validate/Plan纯同步无源/lease/外部回调。Errors为空且IssuesTruncated=false才有效；Plan失败Plan=null。null/default数组/未知enum返回字段错误；OutOfMemory/内部损坏不吞成空成功。Start在当前线程校验值、并发槽/驻留预留，失败Operation=null/Errors非空，不触碰Source/consumer；成功新Guid并后台开始。每次重复提交独立只读，无隐式重试/幂等写入。Generation正ulong原样输出；宿主按operation+generation匹配。回执只由调用方持有Operation保管，无无界注册表。

Completion恰一个SurfaceReceipt，**真实排空/临时释放后才完成**。无进度事件/订阅总线；Snapshot为投影，Sequence在phase/计数/取消变化时递增。Observe只限制等待：waitToken取消抛OperationCanceledException，不取消执行；0立即快照；届满WaitExpired=true/Terminal=null，不是终态。RequestCancel幂等，终态后无作用；输入token和RequestCancel都请求执行取消。

已取消的执行token在Start前返回Cancelled错误且不接纳；接纳后的取消走排空。非法Observe/Close等待参数在改变状态前抛ArgumentOutOfRangeException；合法Close即使waitToken已经取消也先停准入/发取消再抛等待取消，不能恢复Open。factory非法参数按FactoryResult错误信封（不同于ImageLib配置constructor异常）报告；consumer=null在Start前Input。端口返回null/default数组/未知Integrity枚举归Resource/Validity错误并清理；只能正常Completed时Errors为空，Cancelled/TimedOut分别至少含对应码。

consumer在worker上逐块串行同步调用、不在锁内；同consumer跨operation并发安全由宿主保证。异常Consumer错误，停止下一块，清理后Failed。回调只短计算或复制到宿主预留的受限资源，不等本operation.Completion、不重入阻塞Close、不异步保存Span。长期结果在回调内通过IM-006自己复制，记录operation/generation；副本预算/寿命归宿主，不算模块已释放的结果。先前块均为**暂存输入**，仅Completed后宿主可采用；取消/超时/失败必须使整批暂存失效。

### 3.1 来源、坐标与资源端口

- Open固定expected修订，session.Descriptor逐字段/嵌套数组相等，不能只比较Key/hash或使用latest。Source保证同一不可变快照；IM-006桥持真实read scope/lease，session.Dispose归还，不暴露/转移内部类型。Source整体归宿主，session归本operation清理。
- ReadInto：Length>0、destination.Length等于Length，已登记buffer和checked区间合法；返回恰Length才成功，短读/0为Io，不无限补读。调用退出前可访问destination，退出后不得访问；取消信号不代表退出。
- FullBuffers仅Source已验证Descriptor**全部**buffer完整字节SHA-256且固定快照才可声明；RequestedBytes有范围校验依据，NotVerified无完整校验承诺。Core不提升范围结果到FullBuffers。hash输入为buffer `[0,ByteLength)` 原bytes含padding，非点值/压缩file，不发明组合hash/描述hash算法。
- Core拥有临时byte/解码块/索引排序/mesh工作区及取得的session；所有异步调用真实退出后释放。端口临时native在task结束前清理，session资源在Dispose实际完成后归还。GC回收时间不冒充native释放。
- CoordinateBatch为块值副本。HeightField输入Valid项的Z为物理高度，X/Y未映射占位；端口用Grid.Mapping和ParentOffset+ordinal父row/col求XY。XYZ提供原坐标。无Transform且Target=源Frame：XYZ不调用端口，HeightField仍需Grid；不同Frame必须显式Transform，不自己选路径。
- Map返回Positions等长、Frame=Target、Unit=Descriptor.Unit；AppliedMapping为无Transform时Grid.Mapping，有Transform时该引用。Grid先到源Frame再Transform；只有Valid位置检查XYZ有限，Invalid/Unknown位置不参与数值映射，输出NaN及原状态/原因/Origin。不得将Valid无提示降为Invalid或把Invalid/Unknown提升Valid；域外/模型不可用以Frame错误定位本块，不自动部分成功。错误Frame/Unit/Validity禁止本块交付。
- IM-006/007公开类型在桥中显式映射，未接收只阻断真实桥，不阻断本地纯值/受控Source/坐标Simulator。不另建底层引用计数/buffer池/frame注册/变换求解/事务。

## 4. 结构校验、访问计划与预算账

固定校验顺序：版本/必填→ID/重复/枚举→kind/domain数量→buffer/field引用→checked布局→单位/frame/grid→控制列/来源/index绑定→range→字段闭包→预算。错误按阶段、输入layer/field次序、字段路径排序，不因字典遍历改变首错。Validate校验全部层；Plan/Start独立校验请求层，不能假设先Validate过。Validate最多保留256项错误（诊断硬上限，不是客户值）；运行按Budget.MaxIssues限报告，截断不得视为有效。

range为半开：Ordinal `[Start,Start+Count)`，Start/Count>=0，Tile=null，结束<=当前domain数量。Tile仅HeightField Vertex，Start=Count=0、Tile必填，X/Y/Width/Height非负、checked终点<=网格宽高；按row-major枚举，数量=Width*Height。空range必须AllowEmpty=true；Selection不改变请求数量。Face读取ReadCoordinates=false、Selection=PreserveAll，否则Capability。零face网格合法但不证明闭合；空请求不打开session/不回调，接纳后释放预留并Completed+Empty，预算仍须有效。

FieldIds非空、无重复且均为该Domain值字段（X/Y/Z/Height/Attribute/TriangleIndices），输出按请求次序。Core加入不可见的SourceIndex/State/Reason/Origin依赖；选择位置/返回坐标时加入Height或XYZ及各控制列。不需要位置时不假装扫描过位置，receipt三种位置计数均0；控制列不跨Domain借用。

ReadCoordinates=true时TargetFrame必填；不同Frame必须Transform，缺Coordinates（HeightField或需Transform）在Open前Frame拒绝。ReadCoordinates=false时TargetFrame/Transform均须null，否则Input；Selection=ValidPositions虽扫描位置也不隐式请求坐标。FrameDependent在XYZ/Height为true，在结构列为false，Attribute由生产者明确声明（normal/vector/坐标/协方差必true，强度/颜色标量可false），不能靠字段名猜。目标Frame不同且所选Attribute.FrameDependent=true在Open前Capability；原XYZ/Height packed列仍表达源Frame，只有Positions表达CoordinateFrame，不把同块所有字段换frame标签。

TargetFrame与源Frame相同必须Transform=null（不暗忽略多余变换）；不同Frame需精确非空Transform。HasExactParentIndex=true只允许单一Parent等于当前Domain的SourceIndexBinding.Root，SourceIndex就表示该父精确位置；多父/插值支持域不声明一对一父索引，必须false。OriginEntry的Parents/该布尔仍只是摘要，不能以一个Root索引证明全部融合来源；需要实际逐carrier多父及权重时读取§15独立C5贡献表，不改变此v0.4字段含义。

计划不分配逐样本清单：字段闭包按Options有界；以range行段与字段stride计算跨度并迭代生成固定大小块。每块先按buffer Id的Ordinal次序、offset排序，合并重叠/相邻字节区间；AoS共buffer不重复计同字节，SoA/mask/来源/索引都计。不同元素之间的padding只在实际连续跨度读取时计入，禁止为减少ReadBytes跨洞读更大跨度。本版默认逐元素紧密区间、仅合并相邻/重叠，不自动跨padding合并；row gap不读。超过int.MaxValue在完整元素边界拆块；容不下一个元素及依赖则拒绝，不拆组件作半值。Plan.ReadBytes是固定策略的整请求物理输入量，PackedBytes为所选输出列tight原值量，二者不同；ReadBytes<=MaxReadBytes，RequestedItems<=MaxItems。计划不输出Completeness。

固定资源账（所有算式checked，数量是逻辑payload字节，不宣称CLR RSS硬上界）：

1. 一块输入合并区间字节为R(k)，全部值/控制依赖tight字节为D(k)，公开所选值为P(k)。依赖和输出共享底层解码值时仍保守计两份D；每公开字段状态/原因/Origin共9*k字节，ordinal/sourceindex共16*k；需位置时按每项40字节对齐计PositionValue。
2. `BlockUpper(k)=R(k)+2*(D(k)+9*k*公开字段数+16*k+位置项40*k)`。坐标端口的输入/输出副本包含在两份位置账；若实现产生第三份，必须增加计划上界并重验，不能藏复制。描述/闭包/区间metadata的M按全部ID的UTF-8字节+记录数*128，加每array64字节保守账；块区间最多依赖字段数*k，按每区间32字节加入M。错误/issue各样本最多256个ASCII Detail/Kind字符、Path最多512字符，固定每项2048字节纳入 `MaxIssues*2048`，buffer/parent/field记录及其数组计入记录数。超过字符截断只影响诊断文字，不截断ID/hash或数值。不得在Start之前建立O(N)工作区。
3. DeclaredField源索引按请求保留long原值+排序副本共16*RequestedItems；排序Array.Sort，不建逐点HashSet/对象。StableOrdinal无需整请求工作区。Mesh另计§6。Core无cache/prefetch/队列，每operation最多一块in-flight。
4. Plan.ResidentUpperBound为M+索引工作区+BlockUpper(k)+array开销，<=请求MaxResidentBytes与Options.MaxServiceResidentBytes。Start在短锁内原子预留上界及active槽，不能满足即BudgetExceeded，**不排队**；两个请求各通过仍须通过实例总账。实际释放才减账，未排空不复用槽。

BlockItems取可容纳最大整数；固定字段数的线性保守账用于二分，不因区间合并偶然变化破坏单调性。Plan用最坏R(k)=依赖componentBytes*k、区间数量=依赖字段数*k，不把整场ByteLength搬入预算。非空容不下1项拒绝；空BlockItems=0、ReadBytes/PackedBytes=0，仅描述工作区预算有效。实际读bytes因合并可更小，Plan记录上界，不宣称精确IO次数。

真实managed/native/GC/LOH峰值仍按§11测量；Profile目标超限失败，不能以逻辑账通过掩盖。Native预留由adapter另外计，未知不能填0。预算/块建议只改变传输粒度，不改变输入、mask或算法。

## 5. 分块读取、数值扫描、选择与生命周期

### 5.1 固定执行流程

接纳冻结request/consumer/端口引用并启动单调deadline → Open session → 精确比较Descriptor → 按plan读依赖 → 解码控制列 → 建当前ordinal/Root SourceIndex → 验索引唯一 → 扫raw/物理值/状态/来源 → 可选坐标端口 → 可选ValidPositions压缩 → 同步OnBlock → 下一块 → session.Dispose及临时释放 → 唯一回执。没有视图/设备/持久发布阶段。

DeclaredField源索引在首块交付前读完**请求范围索引列**，排序副本查负值/重复；该预读计预算，后续复用，不再读一次。重复诊断定位原请求顺序中第二次出现的ordinal，不能以排序后的slot作来源。仅验请求域，不认证整表。StableOrdinal checked计算；crop用上游声明映射/索引保父源位置，不能用crop宽度重算父索引。索引工作区不能表示为单数组时Capability拒绝；不临时造外部排序/落盘实现。

逐项状态：非法State/来源Id/控制列为Validity错误；声明Valid的坐标raw、scale、bias、中间/最终非有限拒绝本块。XYZ综合状态：任一Invalid→Invalid，否则任一Unknown→Unknown，否则Valid。原因按X/Y/Z顺序取首个Invalid的非零原因，其次Unknown，无则0；综合Origin必须各分量一致，否则缺来源关联错误。Height使用自身状态/来源。Z负值/0合法，Invalid/Unknown保原编码，不输出伪Valid物理坐标。属性独立扫描，不能因位置Invalid跳过属性长度/编码；Fallback2D永不形成Valid高度/XYZ。

ReadCoordinates=false时Positions为空；PackedValues保原编码组件/ByteOrder、去padding，Encoding附在FieldView。true时Positions长度与返回ordinal一致；Invalid/Unknown XYZ设NaN但保状态/原因/来源，不用于测量。ValidPositions仅Vertex且已扫描位置时按原顺序保综合Valid槽；全部公开列/状态/索引同一选择表压缩。无有效点仍Completed+Complete（原请求已完整读检、Delivered=0），不同于原请求0项的Empty。receipt三种位置计数基于完整扫描的请求项，不只输出项。

Complete仅所有请求槽及字段已读检，不表示都Valid/可量测；Empty仅请求0项。Partial为失败/取消前已交付暂存块且未完成；NoResult为未交付且已知失败/取消。Unknown只用于无终态的恢复事实，正常终态不以Unknown掩盖错误。Completed只允许Complete/Empty，其余Outcome禁止Complete。mesh检查完成可含问题，不授予合格。

### 5.2 取消、期限、关闭、迟到与恢复

状态：Accepted→Opening→Reading/Mapping/Inspecting/Delivering（块间可循环）→Draining→Drained→ResourcesReleased→Terminal。Sequence递增，phase数值不保证单调。取消/超时停止启动下一块/端口/回调；已启动调用的buffer仍持有至实际退出。每个await后及OnBlock前重查取消/deadline，迟到成功丢弃清理，不交付。同步consumer不能抢占，待返回排空，不强杀线程/提前归还Span。

末块完成提交、错误/取消/期限观察在短锁中确定唯一决议：先提交成功则Completed；先记录故障则Failed；否则先观察到deadline则TimedOut，先观察取消则Cancelled；同次观察两者均成立取TimedOut。其余诊断仍保留，终态恰一次。deadline只设置DeadlineExceeded/请求取消并Draining，不能立即完成Completion或释放active。等待届满≠排空。

Dispose未退出仍Draining；Dispose抛错且无法证明全部资源归还时，Completion**不完成为Released**，资源/slot隔离，Snapshot保持Draining，有限Observe回pending。只有真实Owner证明隔离资源已结束才可归还，本版没有ForceRelease/伪证明命令。session只Dispose一次，不盲重试或两次clear；清理未知交宿主监督。A取消只清A的session，不能释放B持有的同源read scope。

CloseAsync原子Open→Closing，停准入并请求全部active取消；与Start用同一锁竞争：先Start由Close排空，后Start返回Closed。仅观察min(参数,Options.CloseObservationLimit)；全归还才Closed/ResourcesReleased=true，届满Closing/false/WaitExpired=true，后台清理继续，宿主保留实例/监督器根引用。waitToken仅取消观察，不撤销关闭；重复Close幂等；0立即快照但仍发起关闭。模块不释放宿主整体Source/Coordinates、不强清队列、不自动创建新实例。Closed后Validate/Plan仍纯值可用，Start拒绝。

服务不实现会伪装有限释放的IAsyncDisposable；有限CloseReport和Completion分别表达等待结束与资源已归还。Close未知不妨碍其它operation独立清理，但不再接纳新请求。端口native需独立进程隔离时归宿主监督器；没支持则pending，不宣称取消成功。

恢复只读新请求：修输入/Profile/Source后新operation；内容/布局/域/标定/来源变则新revision。无隐式重试同损坏快照、不改Id遮冲突。重启不恢复旧lease/native/operation成功；旧暂存批次Unknown且不采用，从已确认不可变Source重开。未知存储提交由IM-066查，本模块无写入回执。

### 5.3 坐标、裁切与属性保真

合成裁切例：IM-007 Mapping表达父原点(10,20)mm、pitch(.5,.25)mm，ParentOffset=(4,8)，本地(0,0)→父(4,8)→物理(12,22)。原点/pitch不在SurfaceData再建权威。XYZ单位比例仅Transform中一次，本版明确**跨长度单位映射拒绝**；host先由坐标Owner发布同单位结果/新descriptor，不只换Frame标签。

物理高度、色带、检测灰阶、binary mask是不同字段/用途。frame相关属性不随Position Transform偷偷改；目标Frame不同而请求这种属性时Capability拒绝，宿主先由对应Owner生成完整派生属性。投影/非刚性/法向协方差归IM-007/计量Owner，模块仅接已发布结果。

## 6. 已有网格组合结构检查

StartInspectMesh只接TriangleMesh完整face域，读TriangleIndices及face源索引；无ROI默认裁面，不读XYZ/不做共线几何/不调HALCON。每面3个UInt32/64索引须在[0,VertexCount)、可表示且互不同。布局/字节/编码损坏直接Failed；结构越界可完整报告Completed但AllIndicesInRange=false，调用方拒绝几何消费，不能删坏面继续声称原mesh有效。

固定算法：合法无重复索引面生成三有向边 `(min(a,b),max(a,b),方向,faceOrdinal)`，按无向端点/faceOrdinal排序；一面为Boundary，>2面NonManifold，恰2面方向同为OrientationConflict。三索引排序后加faceOrdinal作重复面键排序，相同三元组的第二及以后各计一DuplicateFaces（绕序不同仍重复），不自动删除。RepeatedIndexFaces单列、不入边账；越界面不入边账，仍报告全face覆盖。Issue按faceOrdinal/Kind/端点排序后限MaxIssues，截断显式、总计数完整。

MeshIssue.Kind闭集为 `IndexOutOfRange / RepeatedIndex / BoundaryEdge / NonManifoldEdge / OrientationConflict / DuplicateFace`，不是自由文案；VertexA/B为对应边端点，面级问题以该问题的首两个索引填值（Repeated取重复值/其后一项，Duplicate取排序前两值）。边级issue的FaceOrdinal取关联最小ordinal，每坏边一项；越界每坏face一项，Repeated每face一项，Duplicate每额外face一项。不得生成O(F)字符串issue全集：保留最多MaxIssues个按固定排序最小的候选，计数继续；可用有界堆，堆payload和字符串账在MaxIssues*2048内。

完整faces原值24*F，边记录32*3*F，重复键32*F，Declared face索引原/排序16*F，另加读取块/描述工作区，全部checked；容不下Open前BudgetExceeded。数组任一长度>int.MaxValue明确Capability，不落盘fallback。Array.Sort+线性分组，O(F logF)时间/O(F)空间，不保留旧稿O(V+F+E)虚假上界。大数据可较大Profile或上游显式拆分，但分块报告不证明跨块关联。

InspectMesh接纳复用§4完整Face range的布局/引用/源索引/合并读取预算检查，FaceCount<=MaxItems，faces与源索引实际输入bytes<=MaxReadBytes，F个face原始/源工作区及3F边数组均可表示；不读无关vertex属性。MaxIssues只限制诊断样本，不停止扫描。Mesh操作RequestedItems=FacesChecked目标F，DeliveredItems=0（无OnBlock），三种位置计数0；完成Complete/原F=0为Empty，取消/失败NoResult，Mesh仅Completed提供全报告、否则null，不交付半份拓扑报告。

Boundary=0/NonManifold=0/OrientationConflicts=0不等于闭合体、顶点流形、无自交、可量体积。本模块不输出IsClosed/MeasurementReady、不生成连通域/孔洞修补/翻面/normals/三角化。共线/近零面积/顶点非流形/交叉/物理覆盖是专业Owner后续门，不是组合报告已检项。

## 7. HALCON 26.05 固定数据桥与筛选路线

依据§13已读本地官方页，算子经ImageLibDotNet公共入口使用；§17给出本次公开签名、H1图像精度及隔离执行闭包，不重复核“封装有没有算子”。下表是算子语义序列，实际ImageLib Worker按§17封送/唯一释放；目标消费编译与真实保真/资源仍须执行。

| 路线 | 固定主分支/参数 | 输出保真/拒绝/fallback |
|---|---|---|
| H1 规则XYZ图像→对象 | Core按grid/单位生成同尺寸X/Y/Z物理值，仅综合Valid域进入三图的**相同**domain；桥显式转m一次，不改源descriptor；xyz_to_object_model_3d | 算子只取domain交集、忽略NaN/Inf，产生mapping_row/col/size。回读num_points/has_xyz_mapping/mapping_size/mapping_row/col/point_coord_*；用row/col查本次父ordinal/Root索引，不假设返回次序。点数/唯一映射/范围/有限值/物理值须逐项核对，丢点/映射错为Integrity/Native，不以非空表示齐全 |
| H2 非规则XYZ→对象 | 可用坐标转m，chunk-local slot 0..n-1只作CPU旁表索引；gen_object_model_3d_from_points→set_object_model_3d_attrib设 &sd_slot，AttachExtAttribTo=points，值为整数slot且n<=int.MaxValue | set生成新对象不改输入，保管所有成功创建handle。回读num_points/XYZ/&sd_slot，slot整数/唯一/在界且与旁表XYZ对应。Root Int64保CPU旁表，不经double；无2D关联不造一行假grid、不供xyz_mapping法向/三角化。失败Capability/Native，保留CPU源，无自动算法替换 |
| H3 显式坐标区间筛选 | 仅X/Y/Z物理区间，轴无重复，min/max有限且min<=max；select_points_object_model_3d的point_coord_x/y/z，上下界数量匹配，多轴AND | 闭区间端点保留；回读mapping或&sd_slot重建旁表，按原ordinal规范输出。算子会调整三角/多边形不引用删点，本模块仍禁止重编号结果充作原mesh，仅对点输入开放。不用score/neighbor临时删噪，失败保留原源 |
| H4 已知变换 | 主路线§5坐标Owner端口；native对象变换仅获批Transform映射HomMat3D后affine_trans_object_model_3d，不求解/选链 | 点/法向会变，其它属性多为原样copy，primitive与距离预计算结构不复制；不是完整属性变换保证。v0.4不开放含frame属性/primitive的通用native变换，拒绝而非暗丢属性 |
| H5 属性读取/资源 | 先查has_points/point_normals/triangles/xyz_mapping及extended_attribute_names/types，再读存在属性/num_*；副本copy_object_model_3d显式属性列表 | 不存在属性会异常；copy无属性或请求不存在属性也异常。all不等于消费者所需字段齐全。每handle独立scope；仅成功创建者退出后clear_object_model_3d或wrapper等价唯一释放，不能双路clear。clear后失效，共用handle必须同步 |

H1/H2由输入表示确定，不是同输入自动试最快。H3是显式派生候选，不覆盖源值/域/来源；native handle不进公共DTO/ViewModel。操作独立工作对象，不共用正在clear的handle。reentrant/global说明算子线程范围，不证明同一可变对象任意并发、wrapper可取消或硬实时；不改全局HALCON system配置。没有 `xyz_image_to_object_model_3d` 别名路线，本地26.05实际名称为xyz_to_object_model_3d，不用不存在页推设计。

已读triangulate：polygon_triangulation需已有polygons，xyz_mapping依2D关联且可能填孔，greedy可能隐式算法向；已读surface_normals：mls/triangles/xyz_mapping支撑不同，估不了给零向量。这些归重建/表面特征/计量Owner冻结方法/参数/质量及同样本比较，**不是本模块执行入口**；旧T1/N1不继续作为默认。本模块只携带已有normals，不重新估计。

同样本真实验证：规则高度有孔/NaN边界、非规则大Root索引、有效0/负高、非零crop offset、独立属性域、多返回。检查XYZ/index/state/origin对应、误接收/拒绝、P50/P95/P99、峰值资源/释放。三domain不一致在native前拒绝，不让交集静默吞缺失。本轮未执行真实HALCON，不声称效率/精度胜出。

### 7.1 ImageLib值端口与factory

Core读取service不依赖该端口；宿主先持自己的受限已验证CPU副本，再显式调用，不开放“任意调算子”逃生口。DTO/接口仍在Core namespace；实际factory在ImageLib namespace。

```csharp
public enum NativeInputKind { OrganizedGrid = 1, UnorganizedPoints = 2 }
public enum CoordinateAxis { X = 1, Y = 2, Z = 3 }
public sealed record CoordinateInterval(CoordinateAxis Axis, double Min, double Max);
public sealed record NativePointInput(SurfaceKey Source, FrameReference Frame,
    LengthUnit Unit, NativeInputKind Kind, int Width, int Height,
    ImmutableArray<long> Ordinals, ImmutableArray<long> SourceIndices,
    ImmutableArray<PositionValue> Positions, ResourceBudget Budget);
public sealed record NativePointOutput(FrameReference Frame, LengthUnit Unit,
    ImmutableArray<int> SelectedSlots, ImmutableArray<PositionValue> Positions);
public sealed record NativeReply(OperationOutcome Outcome,
    NativePointOutput? Output, ImmutableArray<SurfaceError> Errors,
    bool ResourcesReleased);
public interface ISurfaceImageLibPort
{
    ValueTask<NativeReply> FilterAsync(NativePointInput input,
        ImmutableArray<CoordinateInterval> intervals, CancellationToken cancellationToken);
}
```

ImageLib namespace中的唯一factory精确签名为 `public static ISurfaceImageLibPort SurfaceImageLibFactory.Create(ResourceBudget adapterBudget, TimeProvider time)`（类名/方法名如示，不是C#带点方法声明）；无无参构造/服务查找。配置非法ArgumentException，time/budget为null则ArgumentNullException；成功只是实例，无native工作。Budget冻结，端口实例无缓存/持久handle，公开输入错误返回NativeReply Failed/Output=null及错误，不开native。取消发生于native前可直接Cancelled+资源已归还。

NativeInput三数组等长、ordinal/sourceindex非负唯一。OrganizedGrid数量=width*height、ordinal完整本地row-major，Invalid/Unknown保槽；UnorganizedPoints width=height=0，ordinal保调用方顺序但必须严格递增。Position.State/OriginId/Reason保留，adapter不自己查产品事实。区间按input.Unit解释、转m调用、回读转回同Unit，输出不偷换米标签。SelectedSlots为原input数组下标int，严格递增、与Positions同长，只选Valid，Origin/Reason不变。intervals空为仅保真转换、无筛选；不默认阈值。空input无native，Completed空输出。

Filter各调用独立scope，无队列/全局状态。请求budget与adapterBudget各项取较小值，先验证输入/物理有限值及§17 CPU/隔离进程commit总账再调用；不以经验native倍率或0填预算。旧两参数Create为显式无运行绑定入口，所有非空native请求返回BudgetUnavailable；真实H固定调用§17三参数Create，不从环境/全局目录找worker。slot/图domain/释放按§17冻结，实际编译/运行另验。

ValueTask只在真实排空/native全部归还后返回ResourcesReleased=true；取消/期限不提前回终态。调用方有限等待观察pending，保留input/adapter根引用，迟到reply不得采用。清理未知仍pending，宿主监督隔离，不返回false字段冒充Released。adapter无整体native缓存，不需隐藏Close；Service.Close不拥有此独立端口调用，宿主分别监督。

## 8. 格式、无损策略、版本与回退

无损读取公开形式仍为**§2 Descriptor+已登记Buffers**，统一ISurfaceSource；本版§18补同Core内的有界元数据codec，服务Replay重开和独立输入审计两个消费者，不新建codec DLL/数据库Schema。原buffer独立、原bytes不改；IM-006/066桥见§16。导出/存储事务归宿主Owner，无Write/Publish/Activate。

| 表示 | 固定处理/损失边界 |
|---|---|
| Descriptor+Buffers | expected完整快照、byteorder/type/stride显式，所有状态/来源/index保留。重开只读，不初始化存储/更新head/修复log；full hash归Source，不冒充范围已全验 |
| HALCON om3 | read对om3忽略Scale，原样读；外部meta必须给frame/unit/source/map/validity，缺失不能构成完整载体。serialize与om3同数据语义，不是portable契约，不恢复旧handle |
| PLY/OBJ/STL/OFF/PCD | 仅显式Import候选，不当无损核心交换。未知属性可能忽略；OBJ normals数量错不返回，STL三角法向不保留。需LossReport列缺失/量化/来源，当前未开放通用Import API |
| STEP/补法向/三角化 | STEP读取会三角化且单位从文件，属于几何派生，不伪装原始测量，不默认启用 |

HALCON读显式file_type与来源Scale；普通format转内部m，om3忽略Scale，STEP用文件单位。write坐标写m，再读Scale=m避免二次缩放。format转换可能改精度/面/属性，不以sourcehash相等声称无损。具体Import/Export只有消费者确定格式、LossReport/DTO、metadata映射和上限后进入本文X切片；明确规格门，不由扩展名/第三方默认补猜。

Source若解压，分配前限manifest字节/深度/条目、单块/累计decoded/input字节，由Profile冻结；实际产出逐步核限，重复/截断/长度/hash错拒绝半成品。compressed小不代表decoded小，hash不授予权限。跨进程slot遵IM-006 epoch/generation/quarantine，不另造引用计数。压缩/提交/恢复归IM-066/Source Owner，不固定gzip/CAS。

包SemVer；C1–C4 v0.4及C5 v0.1已接收，不由本轮扩展改其含义。未知版本/enum/必需字段fail closed；更改index/单位方向/stride/有效性/所有权/关闭/终态含义为不兼容版本。升级A/B同只读快照比原值/index/state/origin/mesh报告/错误，保留旧包+adapter+input。回退不删写原数据，不成功但缺属性；新manifest旧版不可读则Version。输入hash/layout/frame/domain/origin/Profile任变旧plan不可用，Core无隐藏cache。

## 9. 两个无 UI 最小宿主与可选查看挂接

下面是**待实现的宿主顺序规格**，不是已编译示例；仅用本文精确类型/factory，无未定义Service.Create/自动DI。

### 9.1 Host-A：规则高度Replay输入

Core.Tests Exe的 `--consumer heightfield`：构造BCL内存ISurfaceSource/坐标Simulator（实现§3）→注入TimeProvider→factory→Validate一层SurfaceSet→Plan→StartRead→有限Observe→查Completed→采用暂存摘要→Close→Closed。真实接入换IM-006桥、不改Core。

固定合成fixture HF-A：Key=`hf-a/1`，Frame=`fixture-mm/1`，Unit=mm；3×2，ParentOffset=(4,8)，Grid.Mapping=`grid-a/1`；z Float64 LittleEndian，offset=8、ElementStride=8、RowStride=32、buffer=64bytes，首行0/1/2、次行3/4/5、padding固定0。z状态独立UInt8 `[1,1,2,1,0,1]`，原因UInt32索引2为7其余0；源Int64 `[28,29,30,36,37,38]`（父width=8，不用cropwidth=3算）；来源Uniform Observed Id0。各buffer hash由固定原bytes算，不能sha256:...占位。HeightField的控制列同Grid RowStride按各列紧密行bytes设置，不按z的32错套。

坐标Simulator仅合成测试：父原点(10,20)/pitch(.5,.25)mm；本地0→父(4,8)→(12,22,0)，本地3→父(4,9)→(12,22.25,3)。完整tile3×2、FieldIds=[z]、PreserveAll、ReadCoordinates=true、Target=源Frame、Transform=null、Generation=1。Profile synthetic-a/1：MaxItems6/MaxReadBytes4096/MaxResident65536/MaxBlockItems2/MaxIssues16/OperationLimit1s，仅软件边界值。Options Api0.4/MaxLayers4/Fields32/Buffers16/Origins16/Active2/ServiceResident131072/Close1s。

OnBlock同步验序/坐标，累计ordinal/sourceindex/state摘要不保存Span；Completed Requested6/Delivered6/Valid4/Invalid1/Unknown1/Complete，invalid/unknown坐标NaN、原z/state保留。新请求ValidPositions输出ordinal `[0,1,3,5]`、Root `[28,29,36,38]`，Requested6/Delivered4仍Complete，不改buffer/origin。重复等值结果但新operation；旧generation不覆盖新摘要。

### 9.2 Host-B：XYZ/已有mesh输入诊断

同Exe的 `--consumer mesh`为另一入口/配置，可独立进程；真实计量接入不同Source，不依赖A的UI/私表/静态缓存。SoA X/Y/Z各4个Float64、um、Frame=`fixture-um/2`，顶点 `(0,0,0),(1000,0,0),(0,1000,-100),(1000,1000,0)`，Root Int64 `[9007199254740993,9007199254740995,9007199254740997,9007199254740999]`，不可转double。Faces UInt32 `(0,1,2),(2,1,3)`、face StableOrdinal Base100；全部显式Valid/Observed。Key=`mesh-b/1`；对应纯点输入用PointCloud不同Key、无face列，不改原descriptor kind。

先Read Vertex四项XYZ、ReadCoordinates=true/同Frame无Transform，不注入坐标端口仍可读取；保负Z/Int64。再Read Face两项TriangleIndices、ReadCoordinates=false，确认面索引0..3非Root。再InspectMesh：AllIndicesInRange=true/Boundary4/NonManifold0/OrientationConflict0/Duplicate0。Profile synthetic-b/1：Items16/ReadBytes4096/Resident65536/Block4/Issues16/1s。不可把um当mm或报告闭合/可量体积。

B无A的Grid端口；两个独立进程只依赖同Core，均有限关闭/计数平衡，不改源码。不同kind/unit/layout/Profile构成具体复用计划；两个模拟入口不是实际第二消费者已验收。

### 9.3 可选UI/Viewport挂接

本模块**无专属UI DLL**，没有稳定表面编辑/渲染Owner。查看/色表/相机/LOD/ROI/高级联动归[Viewport指导](../viewport/DEVELOPMENT-GUIDE.md)，WPF+本机DevExpress25.2.3紧凑布局由其Owner实施，不把旧WinForms或临时查看器塞Core。

宿主创建IM-006受限显示副本，以operation+generation+精确frame/unit/index挂接；DisplayOnly/Derived与测量源分开，迟到代次不更新视图，切层/crop明确物理位置。影像优先，短三语状态“数据不完整 / 資料不完整 / Data incomplete”，恢复“重新读取 / 重新讀取 / Read again”；无数据不显示0高度/通过。查看/导出权限归宿主，模块不授放行。语言/主题/只读注入，Code/Path机器值稳定，Detail不直接当本地化UI文案。

关闭：取消对应读取→停新挂接→撤视口引用/宿主订阅→等待该读排空→归还显示副本。Core.Close不强释放仍被视口借用的宿主副本。键盘/UIA/DPI/长三语/实际关闭由Viewport验证，**仅1920×1080固定视口**含任务栏/边框/标题/状态栏；文档阶段不建原型/改显示。不虚构本模块UI Ready，也不省数据挂接生命周期。

## 10. 有限反例与BCL Exe验证

以下是必需断言计划，非已运行证据。受控时钟/闩锁不冒充真实HALCON/物理精度/现场。错误以§2枚举为唯一机器编码，含Code/Path/可选Ordinal/短Detail；旧SD字符串仅宿主历史显示映射，不在核心维护第二套码。

| ID/切片 | 输入/操作 | 期望断言 |
|---|---|---|
| SD-C01/C1 | HF-A、B SoA、XYZ AoS offset0/8/16 stride24 N2 length48；Z列N2 offset0 stride16 length24 | 合法末字节布局，不要求N*stride；padding不当Z；重复计划一致且Source调用0 |
| SD-C02/C1 | long.MaxValue跨度溢出/少1byte/负stride/default数组/控制循环或Domain错/缺单位frame状态/未知enum | Layout/Input/Unit/Frame/Validity/Capability字段错误；Plan=null、无payload/大分配，截断非成功 |
| SD-C03/C1 | 允许/不允许空range、tile越界、两层同XY不同Key/重复Key、crop非零 | 允许空0项，非法空Input；两层不max/min，重复Conflict；range非SourceIndex，crop保父位置 |
| SD-C04/C2 | HF两Selection，有效0/负高、Unknown非零/Invalid NaN，Valid raw=double.MaxValue Scale2，normals独立Unknown | 源槽/选择如§9；物理溢出Validity不发本块；normals不借位置Valid，保0/负值 |
| SD-C05/C2 | B Root>2^53、跨块重复Declared索引、State3/Origin越界、Fallback2D高度Valid | Int64保真；重复首块前Conflict；非法控制Validity；回退拒绝，不提升来源或复用旧Z |
| SD-C06/C2 | Open同Key但不同stride/hash/origin；Read短读/IO；Integrity仅RequestedBytes | 精确Conflict、短读Io，本块不发；真实scope归还；不提升FullBuffers，先前暂存失效 |
| SD-C07/C2 | 重复请求；A/B共源并发，A取消B继续；active/实例总账超限 | 新operation等值结果、独立session；A不释放B；超限Open前拒绝、无排队 |
| SD-C08/C2 | 端口闩锁，先取消仍访问destination，后放锁成功 | 未放锁Completion未完/Observe届满、资源仍计账；放锁丢迟到块、Dispose一次、Cancelled+NoResult终态在释放后 |
| SD-C09/C2 | 时间到deadline端口不退出，首块后取消，Dispose阻塞/清理未知 | 超时不提前Released；首块后Partial；清理未知Draining/Close=false，槽不复用 |
| SD-C10/C2 | Start/Close竞态、重复Close/0观察、观察token取消、consumer抛错/等待同Completion | 锁先后决定接纳/Closed；等待取消不撤关闭；Consumer Failed。违规阻塞由host有限测试检测并非零，模块不声称能强杀回调 |
| SD-C11/C3 | HF crop坐标；缺端口；Map长度/frame错/提升Unknown；XYZ同Frame；跨单位/frame属性请求 | (12,22)/(12,22.25)一致；缺端口Open前拒绝；坏reply不交付；XYZ不调用；跨单位/属性Capability |
| SD-C12/C4 | B双面、face含4、(0,0,1)、重复面、同向共边、三面共边 | 正常Boundary4；越界AllIndicesInRange=false不量测；Repeated/Duplicate各定位；Orientation/NonManifold正确，不删/翻/补面 |
| SD-C13/C4 | face预算少1byte、UInt64>long.MaxValue、重复face来源、F乘加溢出、共线不同索引 | 预算Open前拒绝，编码/拓扑定位；共线不声称已检；Issues截断但总计数完整 |
| SD-C14/C1–4 | 未知Api/enum/旧v0.3 DTO，新frame/revision/hash、旧包回退 | Version/Capability，不默认降级；旧candidate不静默兼容；旧数据保留、旧plan不复用 |
| SD-H01/H | HF invalid/NaN、三domain不一致、无序XYZ/大Root索引 | H1 mapping对原源；H2 &sd_slot对旁表、Int64不丢；domain不一致native前拒绝 |
| SD-H02/H | 闭区间端点/AND/empty/get缺属性/copy错属性/native异常或取消/clear竞态 | 端点保留、AND正确、slot源关联可复核；不当空成功；每成功创建对象唯一释放，pending不提前归还 |
| SD-X01/外部Source | 小压缩大decoded/重复/截断/hash错、om3单位、PLY未知属性 | 实际解压上限核验、拒绝半成品；未声明损失不当完整载体；只读不写head/log |
| SD-AB01/C1–4 | §9两入口、独立进程配置，无WPF/HALCON/设备/DB | 同Core直接运行、fixture值/错误一致，session/资源平衡，不依赖A内部状态 |

测试沿[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)BCL Exe约定。获准建项后的唯一Core构建/执行命令：

```powershell
dotnet build src/Modules/surface-data/Asun.Modules.SurfaceData.Core/Asun.Modules.SurfaceData.Core.csproj -c Release
dotnet run --project tests/Modules/surface-data/Asun.Modules.SurfaceData.Core.Tests/Asun.Modules.SurfaceData.Core.Tests.csproj -c Release -- --suite core --consumer both
```

Exe固定fixture原bytes/hash、受控TimeProvider/异步闩锁；验证期限固定如下，仅为软件验证保护，不是客户性能目标。§9合成Profile的业务OperationLimit=1s保留。

| 层级 | 真实wall期限/起止 | 到期判定 |
|---|---|---|
| 每case | 10s，从该用例进入起，包含fixture初始化、断言、取消和清理 | 列用例ID并失败；停止该消费者后续用例，未完成/卡死/未排空不得通过 |
| 每消费者suite | 120s，从该子进程进入suite起，包含全部case及最终Close/资源核对 | 列消费者和在途用例ID并失败，不因为单case各未超时而延长suite |
| 外层监督进程 | 180s，从被监督的验证进程启动起，包含启动及两个子进程运行/退出观察 | 未取得完整结果、子进程卡死或退出未知均失败，外层返回非零；不能把结束等待报告成ResourcesReleased |

业务TimeProvider可虚拟前进、冻结以验证1s执行期限和竞态；上述10s/120s/180s使用真实单调wall计时（进程内Stopwatch/系统计时、进程外独立监督），不得使用注入的虚拟TimeProvider，也不得依赖被测worker/consumer执行watchdog。虚拟clock不前进、consumer同步阻塞或线程池迟迟未调度，真实监督仍须判失败。case/suite/外层期限均只建立一次，不因重试、进度或取消重置。

`--suite core`覆盖SD-C01–14/SD-AB01受控端口；`--consumer heightfield/mesh`可独立执行。both是监督入口：并行启动两个独立子进程，各用对应消费者参数，分别记录120s期限、case结果、退出码及排空观察；两者均完成全部必需断言、真实排空并退出0才返回0，不能两次函数调用冒充独立host。任一失败/跳过/未完成即总体非零；另一子进程仍由原监督者取消并观察，不遗弃其任务/结果。180s为整个被监督进程树的外层上限，不为每个child重新计180s；构建按前述build命令独立完成，外层保护从验证进程启动计，若dotnet run触发额外构建也不延长期限。

watchdog届满只请求现有operation取消、通过原实例发起有限Close并报告失败；原Owner继续持有仍在途task、Source/session、临时buffer及资源账，直至真正排空。不得重建service/Source/session绕过未知占用、回收仍被访问buffer、重跑同case掩盖失败。清理仍pending时保留诊断与监督引用，不将等待超时或非零退出码当归还回执；若外层180s需终止隔离的测试进程树，记录终止/退出证明与“排空未证实”，本次非零，不能反写被测operation为Released。外部资源只有真实Owner的退出/释放证据才能解除隔离，不由测试监督者假定成功。

必需项失败/跳过/未完成/未排空均非零并列ID，全部完成才0。不以dotnet test空执行代替；H/X实际适配另绑定运行入口，不用Core Simulator充资格。本轮未建工程或执行上述验证。

## 11. BenchmarkProfile与可观测性

纯Validate/Plan也须测，不性能免验。统计唯一按DEV-GOV-010 §3.1，不复制算法。端到端接纳→ResourcesReleased，另记交付、cancel→真实drain/session/native归还。未排空/Unknown不通过，失败/超时/删失/未读不静默删；目标未采纳NotEvaluated，不编客户节拍。

| 切片 | 负载/测点/资源 |
|---|---|
| C1 | small/nominal/max层/字段/buffer/origin数量、宽高/stride/gaps、SoA/AoS、tile/区间、checked拒绝；入口→return、GC分配/plan内存，payload读取0 |
| C2 | 输入bytes/SHA256、kind/count/独立mask/属性、三state比例、Declared/Stable索引、block/budget、consumer时延；Open/read/decode/有限扫描/index排序/选择复制/交付/Dispose/全排空 |
| C3 | 同物理点不同crop、grid/transform版本、坐标输入/输出复制/Map/响应检查；真实IM-007与Simulator分别报，不把端口时延0 |
| C4 | F/V/索引宽度、共边度、重复/越界比例、face来源；faces/read/sort/group/issue，O(F logF)/O(F)实测，不报未检几何质量 |
| H | HALCON26.05/ImageLib二进制hash、H1图/H2tuple/H3区间/domain/source mapping；CPU→native/算子/读回/CPU/clear、native峰值/对象水位/复制 |
| Source | 已批准codec/对象版本、compressed/decoded比例、hash范围/IO、manifest/block上限、未知排空；无真实format消费者不造资格 |

Profile必填Id/revision、输入hash/固定生成器版本或真实来源、Core/adapter/runtime/OS/CPU/内存、工作负载/并发/拒绝策略、冷/热/预热/测量数/最低有效n、操作与外层观察deadline、request/service/端口上限、阶段测点、目标与批准Owner/失败处理。冷独立进程，热固定预热数后只排除明确预热。并发至少单worker、Profile批准并发、总账边界及慢consumer/取消混合。合成方法验证不替代Golden/真实精度。

记逻辑预留/实际数组payload/复制数、managed/native峰值/GC/LOH、active/block、物理bytes/tight输出、首末块、cancel/deadline/Drained/Released时刻。allocator/native不可观测Unknown，非0。服务无队列/cache，host等待Task归host负载。日志含operation/generation/key/Profile/frame/unit/mapping/range/fields/三state数/origin/completeness/Integrity/Code/Path/ordinal，不默认全点值/客户路径；日志为投影，无事实写权。

## 12. 分片、六项准入与确切后续门

六项按DEV-GOV-010 §3.1：①边界/复用②API/资源③无UIhost/端口④反例⑤Benchmark⑥工程/路径/顺序。2026-10-10主控已逐段接收C1–C4及§10的10s/120s/180s监督规格，四片为 `ModuleCoreImplementationReady`，仅文档规格；真实桥、H/X/Viewport门未提升，接收不等于代码/测试或生产资格。

| 切片 | ① | ② | ③ | ④ | ⑤ | ⑥ | 当前结论/门 |
|---|---|---|---|---|---|---|---|
| C1 描述/集合/plan | §1/9 | §2–4 | factory/纯Plan | C01–03/14 | §11 C1 | binding/§10 | ModuleCoreImplementationReady，六项文档规格主控已接收；不依赖客户阈值/Schema/native |
| C2 Source读取/选择/关闭 | §1/9 | §3/5 | 受控Source/两host | C04–10/AB | §11 C2 | Core/Exe | ModuleCoreImplementationReady，受控Source六项文档规格已接收；真实IM-006/066桥仍待Owner映射，清理Unknown不强闭合 |
| C3 坐标转交 | §1/9 | §3.1/5.3 | Simulator | C11/AB | §11 C3 | Core/Exe | ModuleCoreImplementationReady，本地端口及Simulator文档规格已接收；真实IM-007 frame单位/映射链未提升，跨单位/frame属性明确拒绝 |
| C4 网格组合 | §1/6/9 | §2/3/6 | B入口 | C12/13/AB | §11 C4 | Core/Exe | ModuleCoreImplementationReady，组合检查六项文档规格已接收；共线/交叉/顶点流形/计量不是此片 |
| C5 逐carrier父贡献读取 | §15.1/15.7双消费者 | §15.2–6 API v0.1/Owner/排空 | §15.7完整构造及受控Source | SD-P01–12，§15.8 | §15.9 | 同Core/Exe，§15.9 | ModuleCoreImplementationReady，六项文档规格及实际Origin核对主控已接收；C1–C4保持，不授插值/计量/Viewport实施权 |
| H native桥/筛选 | §1/7/17 | §7.1/17公开绑定 | §17两个输入Host | H01/02、H03–06 | §11/17 | ImageLib/Worker | 文档准备在§19自审收口；真实编译/HALCON/隔离/精度/性能未验，不冒充Core接收 |
| S 元数据codec/只读源与坐标桥 | §8/16/18 | §16/18 | Replay重开/审计 | §19 S01–06 | §11/19 | 同Core+Adapters | 准确codec与桥规格已补；对应实现、真实Owner端口及资格未运行 |
| X 通用format Import/Export | §8 | 不发布API | 无已批准format消费者 | X01拒绝原则 | 不作生产Benchmark | 无codec工程 | 不属于当前批准执行入口；未来明确新增format需求须另补规格，不阻Descriptor+Buffer/§18元数据codec |
| UI挂接 | §9.3/19 | 对照Viewport §15.2.5/§15.3 | IM-060已有公开Adapter | Viewport固定视口 | Viewport Profile | 无本模块UI | LOD/拾取/剖面/显示ROI归IM-060；本模块数据/借用/失败链明确，真实UI资格未验 |

本轮§16–19关闭本模块可决定的源/坐标接线、元数据codec、H封送/数值与隔离预算、有限根的设计缺口；全范围自审结论由本原会话负责，不等待总控内容审核。C1–C5已接收六项文档规格保持，新增范围不据此冒称已获产品代码授权。C5贡献只承载ProducerRecorded记录协议，不证明算法真值、父值或坐标物理资格。**运行门**另列：Core/Adapters/ImageLib/Worker编译和断言、真实权重生产者/第二消费者、真实Source/IM-007/Viewport桥、HALCON Golden/保真/异常资源、性能/长稳/取消排空、Viewport/WPF/1920×1080、客户精度/MSA/HIL/FAT/SAT均未执行。外部输入及Owner精确见§19，不声明整模块运行Ready或生产通过。

从一个Core DLL发布，有真实H依赖才建ImageLib，无UI/codec空壳。包记录net10.0/API/错误差异/支持矩阵/hash/HALCON26.05/实际测试性能及限制。升级回退按§8，宿主采用，原数据不变。发现Contract/Owner冲突先修本页/原Owner指导再实现，不能借编译失败改单位/判定/资源语义。

## 13. 来源、研究结论与排除

- 工程权威：[DEV-GOV-005](../../01-governance/DEV-GOV-005_模块独立性与复用标准.md)、[DEV-GOV-010](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)、[DEV-VIS-020](../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md)。当前准入GOV010 v2.1.2，不复制第二标准。
- 原Owner：[image-frame](../image-frame/DEVELOPMENT-GUIDE.md)、[coordinate-geometry](../coordinate-geometry/DEVELOPMENT-GUIDE.md)、[storage-database](../storage-database/DEVELOPMENT-GUIDE.md)、[viewport](../viewport/DEVELOPMENT-GUIDE.md)。本轮只读边界，跨模块bridge由原会话串行接收。
- 算法边界：[DEV-VIS-027](../../shared-modules/guidance/03-vision/DEV-VIS-027_3D HeightField与重建开发指导.md)、[DEV-VIS-028](../../shared-modules/guidance/03-vision/DEV-VIS-028_3D对象模型、配准与表面分析开发指导.md)。具体重建/normals/三角化以对应独立模块当前权威为准，历史路线不授本模块算法权。

### 13.1 已读HALCON 26.05证据

2026-10-09原会话实际读本地Operator Reference 26.05.0.0的Description/Execution/相关参数；10-10增量读set页。SHA256锁原件（只读），非算法运行证据：

| 页/采纳 | 原件SHA256 |
|---|---|
| [xyz_to_object_model_3d](../../../halcon算子手册/operators/xyz_to_object_model_3d.html)：domain交集/NaNInf/mapping | `1e05ea7cc9ffa12a4433883cc127e782eaf49f0a45c3b63ef82ff55f7b2ee7d6` |
| [gen_object_model_3d_from_points](../../../halcon算子手册/operators/gen_object_model_3d_from_points.html)：XYZ tuple | `560e8be9b2911d2885c216e58195ca68d36c50f5f16e54bcdfe6c8370c536bb8` |
| [get_object_model_3d_params](../../../halcon算子手册/operators/get_object_model_3d_params.html)：has/num/mapping/异常 | `f2a7a313eb79f11d14e095af651301e47bd6e33118797890537189c62a1d70e6` |
| [select_points_object_model_3d](../../../halcon算子手册/operators/select_points_object_model_3d.html)：AND/关联调整 | `a872b35566397be3fb6ef3282d56b5fb8a6f1312d5010da58e81fe35833a5eee` |
| [affine_trans_object_model_3d](../../../halcon算子手册/operators/affine_trans_object_model_3d.html)：属性/primitive损失 | `63fb2aa241760de56d05f928dc692385d05ffce2d6b243f7505ab09a7a31832a` |
| [copy_object_model_3d](../../../halcon算子手册/operators/copy_object_model_3d.html)：副本/缺属性 | `89e0175b68799a7a22120536903759af2842255defe54183b549b30134aef0ad` |
| [clear_object_model_3d](../../../halcon算子手册/operators/clear_object_model_3d.html)：失效/同步 | `5ea108d16ceabb87f3bc8a2aa9f3d14056b880bb73327cbe4e451f5d8b9513d3` |
| [read_object_model_3d](../../../halcon算子手册/operators/read_object_model_3d.html)：format/Scale/例外 | `9881cc7618e9da9f9c639deef94d39ae334df3c366da6cbab6afbfec73ca3ebe` |
| [write_object_model_3d](../../../halcon算子手册/operators/write_object_model_3d.html)：写m/format损失 | `fa65828b8691185d37bc5938c1cfafd614cf6e7d369b945b95a84fcde760d063` |
| [triangulate_object_model_3d](../../../halcon算子手册/operators/triangulate_object_model_3d.html)：只核移交 | `1e427c07cbc93639922f344371cb6552bacdef8645a568f4aae7c9814641a452` |
| [surface_normals_object_model_3d](../../../halcon算子手册/operators/surface_normals_object_model_3d.html)：支撑/零法向，移交 | `04ee4996f6452f51e3ab53cf5274f92d839f194c23c18489e16bc8335fe2b05c` |

另读[set_object_model_3d_attrib](../../../halcon算子手册/operators/set_object_model_3d_attrib.html)、[set_object_model_3d_attrib_mod](../../../halcon算子手册/operators/set_object_model_3d_attrib_mod.html)：副本/原位差异、points附着/长度、不自动一致性校验；选非mod副本路线，仍实际消费验证。[serialize_object_model_3d](../../../halcon算子手册/operators/serialize_object_model_3d.html)只确认om3同语义，不造portable codec。旧25.11/H来源24.11/25.05技术断言不作当前依据。

### 13.2 固定GitHub源码/实际测试研究

复用[REF-002 surface-source-research](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#surface-source-research)。2026-10-09联网读实际源码/测试，固定isl-org/Open3D commit `b6c5e196384ad71e75b6e6f9c5da22d046221f1d`（开发快照，非生产release）；tree API限流后该commit raw读取成功，不重试全仓下载。没有运行/引入Open3D/C++/Python/rply生产依赖。

| 固定链接/已读段 | SHA256 |
|---|---|
| [PointCloudIO.cpp](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/io/PointCloudIO.cpp#L107)：107–114/161–168可选删NaN/Inf | `d11250042e7433f55cb89137f008c0551d749a9fc085edebb30ccdd5fc106569` |
| [FilePLY.cpp](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/io/file_format/FilePLY.cpp#L458)：458–520/header resize/失败；531–570固定XYZ/normal/color | `78b39349df6b60c41c595f9c2fe812912fae5cd79b8e747f7145683dac60a15e` |
| [tests/io/PointCloudIO.cpp](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/tests/io/PointCloudIO.cpp#L125)：65–120参数，125–180 Basic，419–451 progress，455–475内存，478–480禁用 | `97404901e12846f7fcccc7473bd81414bdff7b9b1f7192d509549ad233c9861a` |
| [LICENSE](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/LICENSE)：MIT/2018–2026 Open3D | `e2105d24aa1dae0fb5450f5b974dbf369b44d3c91a100d1b134922edb0647175` |
| [io/CMakeLists.txt](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/io/CMakeLists.txt)：IO/第三方入口 | `0fa72bbd9f797eb18ee245b0a1ba0c3f52e6898c6b8964871077ee4d6d1310f5` |

强项：格式/支持属性分支清楚；实际测试PCD ASCII/binary/compressed、PLY ASCII/binary/属性子集，Basic分别断言首次量化误差/再次稳定往返；progress/in-memory有实际测试。限制：Basic允许点/normal/color格式误差且color量化uint8，非本模块原数值无损；PLY按header resize无本模块统一资源预算，读取失败可留下部分容器，不能完整结果；删NaN/Inf压缩位置，未自动保本模块Root索引；PLY固定输出不覆盖独立mask/origin/frame/自定义列；InMemory仅点数3，两个Create DISABLED/NotImplemented不是覆盖。采纳到§8损失拒绝与§10源索引/半成品/量化反例，不复制容器/算法。

依赖证据：FilePLY含rply/geometry/io/utility，geometry用Eigen，IO CMake调open3d_link_3rdparty_libraries；根Eigen3/TBB及可选GUI/CUDA/ML沿REF-002既有版本证据。不重审未变化依赖许可、不拷源码，MIT只来源追踪，不成为AsunImage/HALCON授权待办。PointCloud.cpp已锁hash `9d31ff094145e2be55d17b18da1ada84039522fc7878914c347c118ec5fb1ee1`，已有体素/配准限制直接复用，不借营销证明性能。

### 13.3 既有内部来源保留

10-06已全文只读 `H:\docs\40-development\41-vision-platform\01-foundation\高度图点云与3D基础开发指导.md`，SHA256 `0be448fd2faa83cb20d526cd0f8a0c33f2e9a3a29bd32f6fa972a45e432f289d`，身份见[全量来源清单](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)，不重复读。沿用换算后有限性/crop闭合/来源分离/有界解压/只读重开，现§2/5/8/10；排除AOI流程/SurfaceBuild发布聚合/CAS/gzip/head/journal/H11固定灰度统计默认/旧API及验收声明。AsunControl .NET8 WinForms 2D ROI只借职责组织，不定义3D契约，旧Cv2/WindowDisplay/序列化不迁入。

## 14. 两轮有限怀疑式自审与当前结论

第一轮数据/功能反例：扁平stride不能SoA/rowpadding→逐字段布局；计划Complete混实际→plan无完整标签/receipt独立；crop重算索引/单位改标签→Root/parentoffset/单位桥；mask共用/插值变观测/2D带旧Z→独立状态来源拒绝；native丢NaN后错序号/文件丢属性→mapping/slot旁表及损失门；无边界就闭合→组合报告边界。

第二轮并发/生命周期/接入：session同Key异内容→精确descriptor；跨块Declared重复→首交付前请求域排序；A取消释放B/槽早重用→独立session/实例账；结果提前释放→短ref struct同步回调/回执不含大值；超时/Dispose异常当释放→有限观察/后台排空隔离；慢consumer/异常/Close重入→无锁回调/host违规断言；factory/DTO/测试未知→精确公开形状/两个host/唯一Exe命令。定向修正落本页，不无限全审。

本轮定向文档检查：本地链接31项全部存在，8个代码围栏成对；已记录的11个HALCON原件SHA-256与磁盘一致。API/正文交叉复核补齐FrameReference.Unit/CoordinateReply.Unit、FieldDescriptor.FrameDependent、控制列编码和Mesh结果/预算，确认§9两host的4/1/1位置分类和双面Boundary=4算例。仅证明上述文档与算例一致，不表示Core编译或真实算法运行通过。

2026-10-10主控已完成内容复核并接收C1–C4为 `ModuleCoreImplementationReady`，仅文档规格，包含既有两Host、SD-C01–14/AB、Benchmark及10s/120s/180s监督要求。本次只同步接收状态，不改API/样例、不重做研究或全审。真实IM-006/066源桥、IM-007链、H/X/Viewport仍按§12原门；真实构建/Core Exe/HALCON/WPF/性能/Golden/硬件/现场未运行，不能由本次接收推出通过。共享映射由主控串行交原Owner，本文不写第二权威；状态同步后等待后续指令，不自动扩大范围。

2026-10-11主控已回读并接收0.5.1-prep §15.2–15.9 C5父贡献及实际Origin核对的六项文档规格，C5状态为 `ModuleCoreImplementationReady`。主控独立字段复算P/Q读上界524/586、metadata digest132/150 bytes及逐Origin关联一致。本次仅同步接收状态，不改契约/算法、不重新全审或降低C1–C4接收范围；真实运行及物理资格门保持未验，状态同步后停止等待。

## 15. C5：逐 carrier 多父贡献支持读取（六项文档规格主控已接收，`ModuleCoreImplementationReady`）

### 15.1 边界、表示和复用

C5仅读取生产者**已经记录**的实际贡献：当前carrier对应哪些父Surface/domain中的Int64 ordinal，每个父项实际权重、绑定的方法/参数/证据是什么。第一消费者为无UI Replay贡献回溯；第二为无UI Support审计（向Viewport挂接Adapter提供支持事实）。不实现Viewport、插值、重建、计量、LOD、最近点/逆距离权重、等权猜测或任何平行视觉算法。Observed未发布贡献表时也不自动造表；旧C1–C4调用不需要C5。

首版固定一种布局：**规范CSR**，没有可选FanIn实现分歧。每carrier一行，offsets为N+1个Int64，引用和权重为E个条目，父表可含多个稳定SurfaceKey/domain。一行完整放在一页；页内再规范为从0开始的CSR，不拆一个carrier的父列表。更高fan-in超预算拒绝，不无界扩容、不自动截断支持。生产者按自己批准的方法发布原本使用的权重，C5只验证编码/关联/声明的权重规则；本规格不证明算法或物理真值。

### 15.2 独立 Contribution API v0.1

所有新增类型在 `Asun.Modules.SurfaceData.Contribution`，引用现有 `Asun.Modules.SurfaceData` 值类型，沿同一Core DLL。声明仅为待实现的精确公开形状，factory/accessor方法体在以后实现，不称已经编译。现有v0.4 API和SurfaceDataFactory Api0.4不改；C5自己的factory只接Api0.1。

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.SurfaceData;
namespace Asun.Modules.SurfaceData.Contribution;

public enum SupportState : byte { Exact = 1, Unknown = 2, Unsupported = 3 }
public enum WeightMeaning { ObservedIdentity = 1, ConvexCombination = 2,
    Unavailable = 3 }
public enum WeightAuthority { ProducerRecorded = 1, NotEstablished = 2 }
public readonly record struct ContributionColumn(string BufferId,
    long Offset, long ElementStride, ByteOrder ByteOrder);
public sealed record ContributionParentReference(SurfaceKey Surface,
    SampleDomain Domain, long ItemCount, FrameReference Frame,
    string SnapshotSha256);
public sealed record ContributionMethod(int Id, int CarrierOriginId,
    string MethodId, string MethodVersion, string ParametersSha256,
    string EvidenceId, string EvidenceSha256, WeightMeaning Meaning,
    WeightAuthority Authority, ImmutableArray<int> AllowedParentSlots);
public sealed record ContributionLayout(ContributionColumn Offsets,
    ContributionColumn States, ContributionColumn MethodIds,
    ContributionColumn ParentSlots, ContributionColumn ParentOrdinals,
    ContributionColumn Weights);
public sealed record ContributionDescriptor(string Id, ulong Revision,
    SurfaceDescriptor Carrier, SampleDomain Domain, string? CarrierFieldId,
    long EntryCount, ImmutableArray<ContributionParentReference> Parents,
    ImmutableArray<ContributionMethod> Methods,
    ImmutableArray<BufferDescriptor> Buffers,
    ImmutableArray<BufferDescriptor> CarrierOriginBuffers,
    ContributionLayout Layout);
public sealed record ContributionReadRequest(ContributionDescriptor Descriptor,
    long StartCarrier, long CarrierCount, bool AllowEmpty,
    int PageCarrierLimit, int PageEntryLimit, int MaxFanIn,
    long MaxTotalEntries, ResourceBudget Budget, ulong Generation);
public sealed record ContributionOptions(int ApiMajor, int ApiMinor,
    int MaxParentSurfaces, int MaxMethods, int MaxBuffers,
    int MaxActiveOperations, long MaxServiceResidentBytes,
    TimeSpan CloseObservationLimit);
public sealed record ContributionPorts(IContributionSource Source,
    TimeProvider Time);
public sealed record ContributionFactoryResult(IContributionReader? Reader,
    ImmutableArray<SurfaceError> Errors);
public sealed record ContributionPlan(long RequestedCarriers,
    long MaxRequestedEntries, long ReadBytesUpperBound,
    long ResidentUpperBound, int PageCarrierLimit, int PageEntryLimit);
public sealed record ContributionPlanResult(ContributionPlan? Plan,
    ValidationResult Validation);
public sealed record ContributionStartResult(IContributionOperation? Operation,
    ImmutableArray<SurfaceError> Errors);
public readonly record struct ParentContribution(int ParentSlot,
    long ParentOrdinal, double Weight);
public sealed record ContributionReceipt(Guid OperationId, ulong Generation,
    string ContributionId, ulong ContributionRevision, SurfaceKey Carrier,
    OperationOutcome Outcome, Completeness Completeness,
    long RequestedCarriers, long DeliveredCarriers, long DeliveredEntries,
    long ExactCarriers, long UnknownCarriers, long UnsupportedCarriers,
    IntegrityScope Integrity, bool EndOfRequest, bool EndOfTable,
    ImmutableArray<SurfaceError> Errors, bool IssuesTruncated);
public sealed record ContributionSnapshot(Guid Id, ulong Generation,
    OperationPhase Phase, long Sequence, long DeliveredCarriers,
    bool CancellationRequested, bool DeadlineExceeded);
public sealed record ContributionObservation(ContributionSnapshot Snapshot,
    ContributionReceipt? Terminal, bool WaitExpired);
public sealed record ContributionCloseReport(ServicePhase Phase,
    int ActiveOperations, bool ResourcesReleased, bool WaitExpired);

public static class SurfaceContributionFactory
{
    public static ContributionFactoryResult Create(ContributionOptions options,
        ContributionPorts ports);
}
public interface IContributionReader
{
    ValidationResult Validate(ContributionDescriptor descriptor);
    ContributionPlanResult Plan(ContributionReadRequest request);
    ContributionStartResult Start(ContributionReadRequest request,
        IContributionPageConsumer consumer, CancellationToken cancellationToken);
    ValueTask<ContributionCloseReport> CloseAsync(TimeSpan observationLimit,
        CancellationToken waitToken);
}
public interface IContributionOperation
{
    ContributionSnapshot Snapshot { get; }
    Task<ContributionReceipt> Completion { get; }
    void RequestCancel();
    ValueTask<ContributionObservation> ObserveAsync(TimeSpan observationLimit,
        CancellationToken waitToken);
}
public interface IContributionSource
{
    ValueTask<IContributionSession> OpenAsync(ContributionDescriptor expected,
        CancellationToken cancellationToken);
}
public interface IContributionSession : IAsyncDisposable
{
    ContributionDescriptor Descriptor { get; }
    ValueTask<int> ReadIntoAsync(BufferSlice slice, Memory<byte> destination,
        CancellationToken cancellationToken);
    ValueTask<int> ReadCarrierOriginIntoAsync(BufferSlice slice,
        Memory<byte> destination, CancellationToken cancellationToken);
}
public interface IContributionPageConsumer
{
    void OnPage(in ContributionPageView page);
}
public readonly ref struct ContributionPageView
{
    public Guid OperationId { get; }
    public ulong Generation { get; }
    public long Sequence { get; }
    public ContributionDescriptor Descriptor { get; }
    public long CarrierStart { get; }
    public ReadOnlySpan<long> Offsets { get; }
    public ReadOnlySpan<SupportState> States { get; }
    public ReadOnlySpan<int> MethodIds { get; }
    public ReadOnlySpan<ParentContribution> Entries { get; }
    public bool EndOfRequest { get; }
    public bool EndOfTable { get; }
}
```

Factory冻结options，借用Source/Time；null/非法配置返回Input/BudgetUnavailable、未知版本Version，失败Reader=null/Errors非空，成功Reader非null/Errors空。不读Source、不创建线程/native。options所有容量正、CloseObservationLimit∈(0,24h]。Validate/Plan纯同步无IO/资源副作用，Validation规则沿§3；Plan失败null，不将工艺缺证据当合法权重。Start先做值校验/原子active和驻留总账预留，失败不Open/不创建operation，成功分配新Guid；已取消token在接纳前Cancelled拒绝。Generation正ulong。operation回执/Snapshot独立，不借旧SurfaceReceipt表达贡献。

无需可选string版Domain或另一个层级枚举：carrier/parent都用Vertex或Face；字段支持通过**同Domain + CarrierFieldId**明确选择。目标字段及顺序固定如下，Validate/Plan/读取均用同一闭包，不根据字段名或读取到的数值猜选项：

| CarrierFieldId / Domain | 必选值字段（顺序也用于预检digest） |
|---|---|
| 非null | 按Ordinal精确匹配Carrier.Fields中唯一Id，必须同Domain且为X/Y/Z/Height/Attribute/TriangleIndices值字段；空字符串非法Input，不等于null，不包含控制列 |
| null / Vertex / HeightField | 唯一FieldRole.Height字段 |
| null / Vertex / PointCloud或TriangleMesh | 唯一FieldRole.X、Y、Z字段，固定X→Y→Z |
| null / Face | 仅TriangleMesh，唯一FieldRole.TriangleIndices字段 |

缺字段/角色不唯一/域不符按既有Input/Layout/Capability规则拒绝。所选字段共有F个，不扩到无关Attribute。每个carrier的这些字段必须拥有相同实际OriginId，并等于该行Method.CarrierOriginId；XYZ中任一来源不同即Conflict，不能选一个代替其余。位置与某一字段贡献不同，应由生产者按非null CarrierFieldId发布各自独立ContributionDescriptor.Id/Revision，不共表猜它们相同。parent references仍指载体domain，不把属性组件当父点ordinal。

### 15.3 描述、布局与身份闭包

| 项 | 固定规则 |
|---|---|
| 所有精确引用 | Id/方法/证据Id按§2 ASCII规则；revision>0，hash为64位小写hex；Parents/Methods/Buffers数组非default、非空且受options上限；CarrierOriginBuffers非default，全Uniform时才可为空。Carrier按已接收§2描述规则校验，Validate不读bytes。父SurfaceKey/domain组合唯一、Parents数组顺序稳定，slot只在这份descriptor有效 |
| 父数量/快照 | ParentReference.ItemCount≥0、Frame含单位；SnapshotSha256绑定由原Owner发布的父快照证据。不是父值/文件hash默认值，更不是调用方权限。同SurfaceKey的不同Domain引用必须共享同Frame/同SnapshotSha256；不得因domain不同悄悄换快照。C5只核精确引用格式与一致性，不从该字符串自行认证父物理事实/跨模块hash算法；consumer从原Owner精确快照确认此引用 |
| 当前carrier域 | N为Carrier.VertexCount或FaceCount，checked范围[StartCarrier,Start+Count)；只Ordinal，无隐式tile/Root映射。CarrierFieldId引用的domain一致。Carrier.Origins中的摘要和方法逐项绑定，不猜高度/颜色是否同贡献 |
| CSR列编码 | Offsets：N+1个Int64；States：N个UInt8；MethodIds：N个UInt32（解码≤int.MaxValue）；ParentSlots：E个UInt32（解码在Parents）；ParentOrdinals：E个Int64；Weights：E个Float64。无Scale/Bias、无压缩packed/negative stride；ByteOrder显式LE/BE，ElementStride≥该类型宽度 |
| 容量/非空 | 列末字节按§2 offset+(count-1)*stride+width检查；count=0时不读且offset≤buffer长度。E=EntryCount非负long；全部checked，shared buffer只同一Id/length/hash。offsets至少有首项，N=0仍有offset0=0。布局元数据和数组数量有限，Validate不造O(N)清单 |
| 方法表 | Method.Id恰0..M-1；CarrierOriginId在Carrier.Origins中。MethodId/Version/ParametersSha256与该Origin一致（Observed/Unknown摘要允许按旧约定空）；EvidenceId/EvidenceSha256必填，内容由生产者/原算法Owner保管。AllowedParentSlots非default、严格递增无重复且在Parents范围，Unavailable必须为空，ObservedIdentity恰1个允许slot，ConvexCombination至少1个；实际每项ParentSlot必须在对应允许集合。未知Meaning/Authority/State枚举拒绝，不取第一个值 |
| 来源摘要对应 | 非Observed方法允许的父Surface集合（去重）须等于该Origin.Parents；不能补进未声明父源。ObservedIdentity允许Carrier本身精确自映射（Origin.Parents可空），或旧Root的明确单父关系；不自动生成实际表。HasExactParentIndex=true仍仅旧单父含义；C5多父不能将其改true |
| 不同domain | ParentDomain可与carrier不同，例如face由vertex贡献，但必须producer方法明确声明且parent.ItemCount约束该domain；不把face索引私自当vertex/Root索引 |

**实际Origin控制列闭包**：逐个所选字段解析OriginBinding。Uniform直接取已校验的UniformOriginId，不做byte IO。PerItem按OriginFieldId精确引用Carrier.Fields中的同Domain、FieldRole.Origin控制列；类型固定UInt32、Components=1、UnitId=`1`、Scale=1、Bias=0，ByteOrder/offset/ElementStride/RowStride按该控制列自身Layout，不借Height/XYZ布局。HeightField Vertex的ordinal i以row=i/Grid.Width、col=i%Grid.Width计算地址 `Offset+row*RowStride+col*ElementStride`；其它域平列地址 `Offset+i*ElementStride`，RowStride=0。均checked并遵守§2容量规则，零项不计算除零地址。读取原UInt32，须≤int.MaxValue且在Carrier.Origins中，否则Validity；合法但与行方法或其它所选字段Origin不同则Conflict。**Exact、Unknown、Unsupported三类行均核对**，零父项也不免检。

CarrierOriginBuffers恰为上述PerItem控制列所引用Carrier.Buffers记录的精确副本（Id/ByteLength/Sha256全相等），按BufferId的Ordinal次序去重排列；缺、多、重复或顺序不规范为Input，同Id的ByteLength/Sha256与Carrier记录不相等为Conflict。所有所选字段Uniform时该数组必须为空。U为不同OriginFieldId控制列数，共享同一列只读一次；不同列即使在同一buffer仍分别取其地址，不以buffer相同推断Origin相同。MaxBuffers约束 `Buffers.Length+CarrierOriginBuffers.Length` 合计，两scope即使Id同名也各计一条；不要求Carrier全部buffer纳入C5读取。

IContributionSource.Open返回**逐字段/数组深相等**的Descriptor（含Carrier与两buffer集合），session将贡献表revision和Carrier.Key/revision绑定到**同一个不可变快照**，保证两scope原bytes直到Dispose实际完成不变。ReadIntoAsync只读ContributionDescriptor.Buffers；ReadCarrierOriginIntoAsync只读CarrierOriginBuffers，是明确公开的Origin读取端口。同名BufferId由方法选择scope，不混用、不替换hash、不隐式打开另一个Source/C2 session。Source服务由宿主持有，session/读取buffer由本operation持有；两个reader均沿§3.1：Length>0、destination.Length恰Length、checked区间合法，返回恰Length才成功，短读/0为Io，未实现Origin端口抛NotSupportedException映Capability，不能回退Uniform/默认Origin。没有native/lease被序列化出来。父Ordinal为非负Int64且<对应ParentReference.ItemCount，允许>2^53；不是Root SourceIndex，不是double、相机像素、三角面顶点位置或最近点序号。需要Root值时另读该父Surface的已接收SourceIndexBinding，引用/坐标链保持原Owner。

### 15.4 实际权重、状态、和与证据

本v0.1只承载两种可判定的**无量纲实际权重**，不开放可配置 signed/单位/和算法让程序员补猜。

| Meaning/Authority/State | 条件/输出 |
|---|---|
| ObservedIdentity / ProducerRecorded / Exact | 该carrier恰1条父、weight按Float64精确等于1；方法为observed/1且对应Origin.Kind=Observed。父等于Carrier自身时要求同Domain/ordinal；明确父Root关系则由生产者发布精确parent ordinal和证据，不由C5算最近点 |
| ConvexCombination / ProducerRecorded / Exact | 对应非Observed派生Origin（Interpolated/Repaired/Filtered/Cad）；父数≥1、≤MaxFanIn；权重有限且≥0，无量纲；归一和1，固定数值保护见下文。父项与权重是方法实际使用/发布的记录，不是C5重算结果。1条父/权重1也不把派生提升Observed |
| Unavailable / NotEstablished / Unknown或Unsupported | offset相等、0父项；Method/Evidence精确记录为何未知/不支持。Unknown表示证据尚未确立/不完整，Unsupported表示已知方法类型当前v0.1不承载。允许读取其状态，但Support消费者不能采用为Exact，不能造等权/最近点或当完整支持 |
| 坏编码/未知enum/Exact缺证据 | Layout/Validity/Integrity/Capability错误，停止本请求；不是把损坏页悄悄改成Unknown |

Exact每行父项按 `(ParentSlot,ParentOrdinal)` 词典序**严格递增**；同一父Surface/domain/ordinal重复为Conflict，不合并权重/排序修复。这只是**生产者规范顺序**，读取者验证不重新排列；算法若重复使用同一个父样本，生产者须在唯一方法证据中记录实际合并后的系数，不能在本读取模块临时合并。不同slot域/Surface允许相同ordinal。每项权重finite；负权、NaN/Inf拒绝。+0允许且必须保留父引用（不删支撑），-0拒绝非规范编码，至少一项>0。零权仍计fan-in/预算，不能利用零系数省掉方法声明的支持域。

ConvexCombination按存储顺序补偿求和：初始s=c=0，每项x设t=s+x；若abs(s)≥abs(x)，c+=(s-t)+x，否则c+=(x-t)+s；再s=t，最终sum=s+c。所有中间/最终值检查finite，`abs(sum-1)≤1e-12`。该数是纯Float64一致性保护，与Viewport已声明的Support和约束一致，不是客户精度；**不重归一化/夹紧/删零/把NaN当0**。ObservedIdentity不走容差，必须精确1。带负权的bicubic、面积/能量/非归一系数、置信度score/概率等其它语义当前不承载：producer发布Unavailable+Unsupported且空父列；不把原系数改成正权或归一后冒充实际使用值。权重无m/mm/um单位，不等同不确定度、可信度、贡献面积或质量分数。

EvidenceSha256绑定原算法Owner保留的**方法与输入快照证据原bytes**，原Owner决定证据内容与签发。调用方从可信发布端取得expected Descriptor/父SnapshotSha256/Method Evidence；C5不自称签名验证器、不把synthetic声明当算法真值。如果实际权重没有生产者记录和方法证据，Authority必须NotEstablished，State不能Exact。结构校验通过只证明这批记录符合协议，不证明插值准确/父数值正确/物理来源齐全。篡改后的表/方法若同时换hash与expected输入，需要原Owner拒绝未经采用的新版；C5不能对恶意Source或任意被替换的可信expected承诺鉴伪。

### 15.5 预检、完整哈希、预算、分页及EOF

固定请求字段范围：PageCarrierLimit/PageEntryLimit/MaxFanIn/MaxTotalEntries>0且MaxFanIn≤PageEntryLimit，CarrierCount≤Budget.MaxItems，Budget有效规则沿§2.2。PageCarrierLimit≤Budget.MaxBlockItems；PageEntryLimit及CSR页数组长度须可表示int（含K+1）；非空单carrier所有父项超过MaxFanIn/PageEntryLimit即BudgetExceeded，不能拆父列表。MaxTotalEntries为**本请求**最大父项总数，checked，超过即拒绝/失败，不按平均fan-in猜。空请求需AllowEmpty=true；成功Empty/不Open，预算仍有效。

Plan在不读源下采用保守上界：
- K=本页最大carrier数，L=`min(PageEntryLimit,K*MaxFanIn,EntryCount,MaxTotalEntries)`；K、K+1数组可表示，实际分页到任一上限前只在carrier边界结束。整请求父项上界T=`min(CarrierCount*MaxFanIn,EntryCount,MaxTotalEntries)`。
- A_c=sum(ContributionDescriptor.Buffers.ByteLength)，A_o=sum(CarrierOriginBuffers.ByteLength)，A=A_c+A_o；A_o核完整原buffer，含与Origin共存的其它payload和padding，不只算Origin列。未纳入集合的Carrier buffer及父payload不读取。ReadBytesUpperBound=`A+16+2*(8*(CarrierCount+1)+5*CarrierCount+4*U*CarrierCount)+20*T`；16保守覆盖全局offset0/offsetN检查，先两scope全buffer串流hash读A，再对请求offset/state/method及每个PerItem Origin做预检一次、交付读取一次，各页共享边界offset保留一项复用，父slot/ordinal/weight合20 bytes/条。Origin按4字节逐元素读取，共享列每阶段每row仅读一次；Uniform无额外byte IO。stride padding仅完整hash阶段读，后续不跨洞。实际metadata行最大fan-in会在预检确认；预算以本式上界而非猜真实T分配。
- 驻留：一块hash/read scratch≤`min(65536,Budget.MaxReadBytes)`且>0（65536仅IO chunk上限）、页CSR原metadata `8*(K+1)+5*K`、Origin原4*U*K、entry原20*L、解码offset8*(K+1)/state1*K/method4*K/OriginId4*U*K/ParentContribution24*L；各两份保守临时账。按§4有限metadata M、每array64、MaxIssues*2048加入。引用表/method/AllowedParentSlots/Descriptor（含两buffer集合）全部字符/记录、F个目标字段与U个控制列映射、逐行F个实际OriginId及21+4*F字节digest编码scratch计M；不保存O(N) Origin数组。结果方法/父表借同一冻结descriptor，不逐行分配对象。Plan.ResidentUpperBound≤request及service两上限；不足则二分降本次PageCarrierLimit，PageEntryLimit/MaxFanIn不降，1条carrier也容不下则拒绝。不降低或改权重。
- operation先原子预留全部上界/active槽，无队列/cache/prefetch；一页in-flight，真实归还减账。逻辑账不冒充CLR RSS硬上限，实际峰值按Profile测。ContributionPlan.MaxRequestedEntries=T为上限，预检若实际总数>T则BudgetExceeded，不能因为表不满足声明而扩账。

新增Origin页数组长度U*K、原bytes长度4*U*K、逐行F值及21+4*F编码scratch也须checked且可表示int；算术溢出或1条carrier都容不下时在Open前BudgetExceeded，不把long截成int，不临时扩为全域数组。预检使用同一有界页工作区，交付阶段复用，预算仍按上述两份保守账。

执行顺序：Open精确session → 以固定scratch通过IncrementalHash SHA256**分别串流核验两scope每个已登记buffer全部原bytes**（包括padding，同名Id也各读） → 比较各自BufferDescriptor.Sha256 → 按请求行串流预检CSR/States/MethodIds及实际Origin → 页级重读Origin、完整父项/权重并逐行验证 → OnPage → 真实Dispose/释放 → 唯一Completion。不得把Source自报PageVerified代替本模块hash。先验完整buffer可保护请求页，却仍不表示范围外CSR/Origin语义已扫描；C5的Integrity=FullBuffers精确表示ContributionDescriptor.Buffers加CarrierOriginBuffers完整byte hash，**不表示Carrier其它buffer或父payload已验证**。预算包含A，A过大则在Open前BudgetExceeded，没有隐式降到不验hash/不核Origin路线。Source须保证验hash后两scope同session bytes仍不可变；违约可定位异常，恶意重写不可能仅凭读取协议认证，归原Owner安全/完整性边界。

CSR预检不存全请求数组：读全局offset0与offsetN（N表carrier数）确认0/E；以固定metadata块读取所请求offset区间的相邻值，单调且[0,E]，控制列状态/方法编号合法；Exact有非空row、Unknown/Unsupported空row，Meaning/Authority一致，累计父项数和max fan-in。每行按§15.2/15.3逐个解出所选字段实际Origin（Uniform元数据或同session PerItem列），验证表内合法性、字段间一致及与Method.CarrierOriginId相等。首块交付前整个**请求**元数据及Origin预检完成，所以超限/非法metadata/错行Origin均无OnPage。N=0的offset0一次读/验0；范围外row内容不被本请求认证。

预检按carrier顺序将每行 `(Int64绝对起offset,Int64末offset,UInt8 state,UInt32 method)` 的21字节后，依冻结目标字段顺序追加F个UInt32实际OriginId（Uniform也追加），全部规范little-endian，共21+4*F字节，串流SHA256。页交付阶段重读PerItem/重取Uniform并逐行核对，再同序重算digest（不保存O(N)元数据），末页后必须相同，否则Conflict且暂存全部失效。逐页重验单调/范围/行状态、Origin和页边界，不假装仅一个全域digest能定位每行篡改。Parent贡献条目没有预读，当前页核其实际值、顺序/权重，再依session不可变和全bufferhash保证；不声称preflight已经查过这些权重或父物理值。digest scratch两个256bit结果和固定编码buffer也计M。

分页固定贪心：从下一carrier开始，连续加入完整row，直到再加入将超过Plan.PageCarrierLimit或Plan.PageEntryLimit为止；本身一row超限先拒绝，Unknown/Unsupported的零row仍占carrier名额。每页CarrierStart严格连续，Offsets.Length=States.Length+1=MethodIds.Length+1，本地offset0=0/末=Entries.Length，全部row完整；carrier[i]=CarrierStart+i，无单独double索引。Entries序和State/Method按原表保留，不压缩Unknown/Unsupported。EndOfRequest只在请求末端 true，EndOfTable只在该末端等于N时 true；部分范围最后一页可以(true,false)，不会为了等全表EOF扩读；不得把ReadInto短读/0当EOF。两标志由reader从expected range/N计算，Source不提供可伪造的EOF。完成非空请求=Completed+Complete，Unknown/Unsupported计数仍报告，**Complete只指已完整读取请求，不代表Exact支持**；空=Completed+Empty，EndOfRequest=true，EndOfTable=(Start=N)。取消/错误先前页Partial暂存，未交付NoResult；非Completed不得报告EndOfRequest/EndOfTable完成或完整支持。

### 15.6 Owner、取消、有限关闭和坐标链

ContributionPageView为Core内部构造的ref struct；States/MethodIds/Offsets/Entries只在同步OnPage内借用，没有公开构造。模块不转移底层buffer/lease，不能回调返回后保留Span或在Task捕获；host若长期需要，先预留自己的字节预算，再复制或摘要。OnPage锁外worker串行、每operation唯一消费者；异常Consumer错误并停下一页，回调内不等待同Completion/阻塞Close。页Sequence从1递增；所有页operation/generation/descriptor相同。任何已交付页仅暂存，Completed之后host才采用整批；晚到/取消/篡改失败均使暂存失效。

Source服务/TimeProvider整体归host，session/当前scratch/页存储由operation归还；父Surface资源根本没打开，不替其Owner释放。执行状态、故障/取消/deadline决议、Observe等待token、限时Close与Dispose未知隔离严格沿§3/5.2（贡献类型自己的回执），没有提前Released。具体Phase：Accepted→Opening→Reading(hash/preflight)→Reading/Delivering(逐页)→Draining→Drained→ResourcesReleased→Terminal；hash期间也检查执行期限/取消。阻塞Read/OnPage/Dispose不抢占、不重建实例绕过，不重复Dispose猜释放。重复Start新ID/不重试同坏snapshot；修表/证据/权重/方法变更新Contribution Revision和所属派生Surface revision，由原Owner发布后新请求。重启旧in-flight/页批Unknown，不恢复native/lease或假成功。Closed仅禁止Start，纯Validate/Plan可用。

权重绑定**原父carrier**，与显示/世界frame无关；ContributionReader不变换坐标/单位。ParentReference.Frame精确携单位；若Viewport需要父值/位置，先用ParentSurface/domain/ordinal读原数据，再经已批准IM-007链投影，保Transform revision和父Snapshot/源有效性。跨父frame/单位合法贡献事实仍可读取，但消费坐标缺链/域外/值无效只能Unknown/NavigationOnly，不能在C5将父ordinal当XYZ、Root、最近LOD点或等权再拼；不能只按权重证明支撑的有效域/质量。C5自身完成方法摘要与所选字段**逐carrier实际Origin**核对，不依赖消费端另开C2补足；两个scope共用本operation的session/取消/deadline/Dispose与驻留账，Origin读取未退出时同样不得Released。该核对证明关联一致，不证明方法证据/父值/物理真值。父值有效性/必需支撑（包括零权父项）由算法/消费Owner查询，C5不提供ProductionAccepted。

### 15.7 两个完整无UI构造与固定数据

下述为**语义构造配方**，每项参数/公开入口已定义；测试Source类是测试内实现IContributionSource/IContributionSession，不是新增未声明产品factory。Source的每个session持两个独立冻结字典：贡献字典以Descriptor.Buffers提供ReadIntoAsync，Origin字典以CarrierOriginBuffers提供ReadCarrierOriginIntoAsync；同session固定同一Carrier及Contribution修订。提供深相等Descriptor、独立session/Dispose计数及两个reader各自闩锁；同Id也不得串字典。使用BCL BinaryPrimitives写指定endian数据、SHA256.HashData算实际原bytes。不得把字符串`sha256:...`当hash。父SnapshotSha256/EvidenceSha256在软件fixture由固定UTF-8证据bytes计算，明示Synthetic，不当真实算法/现场证据。

**Host-P（ReplayContributionHost）**：
1. carrier使用§9 mesh-B已有descriptor的副本（四个Vertex、XYZ/源索引/Origins完整）；新Key=`support-carrier/1`。保原XYZ布局，无更改既有Host-B。Origins Id0=Observed（Parents空、observed/1），Id1=Interpolated（Parents=[`raw-a/7`,`raw-b/9`]，bilinear-recorded/2，参数摘要SHA256(UTF8 `synthetic:recorded-weights-v1`)），两者HasExactParentIndex=false。在这个新carrier副本新增tight UInt32 Origin控制列[0,1,1,1]及对应buffer/hash，XYZ三字段都以PerItem Origin绑定同一列（其它字段仍明确Uniform Origin0）；不改旧mesh-B。该新Surface是synthetic，method名称表示**已记录权重**，不执行bilinear求权重。
2. parent slots按表顺序：slot0=carrier自身，Vertex ItemCount4/Frame=fixture-um/2，Snapshot摘要SHA256(`synthetic:carrier-snapshot-v1`)；slot1=raw-a/7，Vertex ItemCount=9007199254741000，Frame=parent-mm/1；slot2=raw-b/9，Vertex同ItemCount，Frame=parent-um/1。大父数仅逻辑fixture容量，C5不分配/读取巨大父payload。父摘要分别SHA256(`synthetic:raw-a-r7`)、SHA256(`synthetic:raw-b-r9`)。
3. Methods Id0绑定Origin0、ObservedIdentity/ProducerRecorded、AllowedParentSlots=[0]，MethodId/Version=observed/1、ParametersSha256空、EvidenceId=synthetic-observed/1；Id1绑定Origin1、ConvexCombination/ProducerRecorded、AllowedParentSlots=[1,2]，Method tuple如上、EvidenceId=synthetic-dual/1。两EvidenceSha256各由UTF8 `synthetic:identity-evidence-v1`、`synthetic:dual-evidence-v1`算。
4. CSR：Offsets Int64 [0,1,3,5,7]；States UInt8 [1,1,1,1]；MethodIds UInt32 [0,1,1,1]；ParentSlots UInt32 [0,1,2,1,2,1,2]；ParentOrdinals Int64 [0,9007199254740993,9007199254740995,9007199254740995,9007199254740997,9007199254740997,9007199254740999]；Weights Float64 [1,.25,.75,.5,.5,0,1]。六tight little-endian独立buffers：offset0/stride分别8/1/4/4/8/8，各长度为元素数*width，hash按实际bytes；layout六列引用这些Id。新Origin控制字段Id=`origin`、Role Origin/Domain Vertex，Encoding=(UInt32,1,`1`,1,0)，Layout=(BufferId=`carrier-origin`,Offset0,ElementStride4,RowStride0,LittleEndian)，Validity Uniform Valid/Reason0、自身Origin Uniform0、FrameDependent=false；XYZ.Origin=(PerItem,0,`origin`)。该buffer为UInt32 [0,1,1,1]的16原bytes，Carrier.Buffers登记其实际SHA256，CarrierOriginBuffers恰为该记录单元素数组，Source Origin字典持相同原bytes。ContributionDescriptor Id=`recorded-support`/Revision1，Carrier上述完整descriptor，Domain Vertex/CarrierFieldId=null，EntryCount7，Parents/Methods/Buffers/CarrierOriginBuffers/Layout如上。
5. Options=(ApiMajor0,ApiMinor1,MaxParentSurfaces4,MaxMethods4,MaxBuffers8,MaxActive2,MaxServiceResidentBytes=1048576,CloseObservationLimit1s)；Ports=(内存Source,受控TimeProvider)。Create→Reader非null→Validate.Errors空→构造ReadRequest(Start0,Count4,AllowEmpty=false,PageCarrierLimit2,PageEntryLimit4,MaxFanIn2,MaxTotalEntries7,Budget=`synthetic-p/1`,MaxItems4,MaxReadBytes4096,MaxResidentBytes262144,MaxBlockItems2,MaxIssues16,OperationLimit1s,Generation1)→Plan非null→Start(consumer,token)→有限Observe。
6. consumer只摘要/复制受限父项：第一页Carriers0,1，Offsets[0,1,3]，三条父；第二页Carriers2,3，Offsets[0,2,4]，四条父，最后零权仍保留。ParentOrdinal大于2^53值逐long断言不变；第一页EndOfRequest=false/EndOfTable=false，第二页true/true；Receipt Completed/Complete，Delivered4/Entries7/Exact4/Unknown0/Unsupported0、Integrity FullBuffers。等Completion后才采用摘要→CloseAsync(1s,token)应Closed/ResourcesReleased=true。重复调用新Guid/等值页，不重写源。

P预算复算：六贡献buffer长度40+4+16+28+56+56，A_c=200；Origin buffer16，A_o=16，A=216。F=3，U=1（XYZ共一控制列），C=4、T=7，ReadBytesUpperBound=`216+16+2*(8*5+5*4+4*1*4)+20*7=524` bytes；MaxBuffers合计7≤8。每行digest为33 bytes，共132 bytes；预检/页重读均从同一Origin列恢复三个字段Id，不三次读列。页K=2的Origin原/解码各8 bytes，各两份计32 bytes，另将字段映射/digest scratch计M；沿§15.5并入262144驻留预算，不省略新增Origin账。读预算523应在Open前拒绝，4096允许本读上界。

**Host-Q（SupportAuditHost）**：Core.Tests独立子进程，不依赖P的Source/缓存/Viewer。选§9 HF-A完整carrier副本、Key=`support-height/2`，Domain Vertex、CarrierFieldId=`z`（该Height值字段也允许明确支持，不只Attribute）。保六槽/grid，Origin0 Observed，Origin1 Interpolated Parents=[`raw-q/3`]、MethodId/Version=`recorded-pair/1`、参数摘要SHA256(UTF8 `synthetic:pair-q-v1`)，Origin2 Unknown（Parents空、unknown/1、空参数摘要、HasExactParentIndex=false）新增。新carrier增UInt32 Origin列[0,1,2,1,2,0]（HeightField布局offset0/stride4/rowstride12/length24、hash实际bytes），z字段PerItem绑定它，旧HF-A不改。Method0=ObservedIdentity/ProducerRecorded、允许slot0(HF自身)；Method1=ConvexCombination/ProducerRecorded、绑定Origin1精确方法/参数、允许slot1(raw-q/3 Vertex count9007199254741000/frame parent-mm/1，Snapshot摘要SHA256 UTF8 `synthetic:raw-q-r3`)；Method2=Unavailable/NotEstablished、对应Unknown Origin2、AllowedParentSlots=[]、MethodId/Version=`unknown/1`、参数摘要空、证据明确缺权重，不套bilinear未知权重。Methods的EvidenceId分别synthetic-q-observed/1、synthetic-q-pair/1、synthetic-q-unknown/1，对应EvidenceSha256取同名Id的UTF8 bytes；self-parent Snapshot摘要取UTF8 `synthetic:height-q-snapshot-v2`，均不冒充真实证据。
CSR Offsets=[0,1,3,3,5,5,6]，States=[1,1,2,1,3,1]（Exact,Exact,Unknown,Exact,Unsupported,Exact），MethodIds=[0,1,2,1,2,0]，slots=[0,1,1,1,1,0]，ordinals=[0,4,8,9007199254740997,9007199254740999,5]，weights=[1,.25,.75,.5,.5,1]。同样六tight buffers/hash，Id=`audit-support`/Revision2。新Origin字段Id=`origin`、BufferId=`carrier-origin`，其Role/Encoding/Validity/自身Origin/FrameDependent同P，Layout=(Offset0,ElementStride4,RowStride12,LittleEndian)；z.Origin=(PerItem,0,`origin`)。Carrier.Buffers持24原bytes的精确SHA256记录，CarrierOriginBuffers恰为该单元素记录，Q的独立Source Origin字典持UInt32 [0,1,2,1,2,0]实际bytes，不能复用P字典。Method2允许Unknown及Unsupported记录，不声称两者相同事实；行状态各自保留。PageCarrierLimit3/PageEntryLimit4/MaxFanIn2/MaxTotalEntries6，Budget synthetic-q/1 MaxItems6/ReadBytes4096/Resident262144/Block3/Issues16/Limit1s，其余Options同P；同Create/Validate/Plan/Start/Observe/Close流程。
Q预算复算：六贡献buffer长度56+6+24+24+48+48，A_c=206；A_o=24，A=230。F=1、U=1、C=6、T=6，ReadBytesUpperBound=`230+16+2*(8*7+5*6+4*1*6)+20*6=586` bytes；MaxBuffers合计7≤8。每行digest25 bytes，共150 bytes，Unknown/Unsupported行也保留Origin2。页K=3的Origin原/解码各12 bytes，各两份计48 bytes，字段映射/digest scratch另计M；262144驻留预算包含这些账。读预算585应Open前拒绝。HeightField跨行地址使用Origin的RowStride12，不使用z原布局RowStride32；部分Start3/Count2也从原ordinal3、4取Origin1、2。
第一页carrier0..2本地offset[0,1,3,3]，第二页3..5=[0,2,2,3]；carrier3的双父完整在第二页，不把父项跨页切开，carrier5为Observed自父5/权重1。Receipt Completed+Complete但Exact4/Unknown1/Unsupported1；Q必须拒绝将整表作为全部Exact Support，仅允许显式精确行的诊断摘要，派生点有值也不填未知权重。Q读取部分范围Start3/Count2结束时EndOfRequest=true/EndOfTable=false，不能跳去读carrier5等EOF；坐标缺链不采用物理投影。
Core.Tests的`--suite contribution --consumer both`分别监督P/Q独立子进程（参数replay/support-audit），两者完整断言+排空退出0才0，沿§10真实10/120/180s watchdog。生产Source替换只在显式构造注入，不改C5 API；实际Viewport挂接/Replay业务采用仍归其Owner。

### 15.8 正常→故障→恢复与两轮有限反例

| ID | 输入/事件 | 唯一断言 |
|---|---|---|
| SD-P01 | P Observed self-parent，权重1；根本无C5表 | 前者索引0/同domain/1；Source明确无表抛NotSupportedException映Capability，不从Origin布尔造表 |
| SD-P02 | P双父不同Surface；Q未知/unsupported | slot+SurfaceKey/domain/Int64全部保留；Complete读取不等全Exact；unknown行0父不伪空Exact |
| SD-P03 | 父ordinal>2^53、负/越界、同row重复/乱序、跨页大索引 | 原long逐位不变，非法Layout/Validity/Conflict；顺序不修复、重复不合并 |
| SD-P04 | NaN/Inf/负权/-0、零权、和1.2 | 前几项Validity、零权保留、和超1e-12拒绝；不删零/归一化/夹边 |
| SD-P05 | 方法证据缺、Origin method/parent集合不匹配、signed算法想标Convex | Input/Conflict/Capability或发布Unavailable；不自造签发/等权，原Owner重发已知证据后新revision读取 |
| SD-P06 | offsets负/不递增/末≠E，Unknown行有条目，单row跨页/短Read | metadata首交付前Layout/Validity；短读Io非EOF；所有之前暂存不采用 |
| SD-P07 | 翻转buffer一byte、换expected未采用hash、Open同Id异Method/Parent | core SHA256不符Integrity/Open深不等Conflict；可信expected改变需原Owner采纳，不声称无信任根鉴伪 |
| SD-P08 | 单row>MaxFanIn/PageEntryLimit、total超限、read/resident上界少1byte | 相应BudgetExceeded，不能拆row/截断/扩容；metadata预检保证首交付前总项数约束 |
| SD-P09 | source闩锁时取消/期限，consumer阻塞、Dispose清理未知、重复Close | 有限Observe pending、Completion未归还前不完；原Owner/task/session/数组保留，槽不复用，不重建服务 |
| SD-P10 | A/B共immutable源、A取消B继续；重复Start/迟到generation | 独立session、A不释放B、新ID同值、迟到页不入新批；服务总账超限Open前拒绝 |
| SD-P11 | range部分/空/最后N、读0、page标末尾 | 精确EndOfRequest/EndOfTable如§15.5；0字节非EOF；允许空不Open，非法空Input |
| SD-P12 | P交换Origin行0/1，Q跨页交换行0/3但方法不变；XYZ各自Origin不同；Uniform实际0而方法绑定1；Origin端口不可读；parent frame缺链、未知Api/枚举 | 未更新原hash先Integrity；更新合法fixture hash后错行在首交付前Conflict且无OnPage；所选字段不一致Conflict，不挑X代替XYZ；全Uniform集合空、无Origin byte IO仍核对；短读Io/不支持Capability，不另找Source；缺IM-007不采用；Version/Capability不默认降级，分字段独立表；C1–C4原样使用 |

Source抛NotSupportedException→Capability；无法取得既有snapshot→Io/Conflict由诊断定位；返回null/session不匹配→Resource/Conflict；回调异常→Consumer。运行错误仍用既有SurfaceErrorCode，不新增同义码。清理异常按§5.2pending隔离，不伪Failure+Released。纠正字节、权重、方法或父身份后由原Owner新revision；旧hash/旧已读页不复用。

SD-P12固定反例：P Origin改为[1,0,1,1]，Methods仍[0,1,1,1]；Q改为[1,1,2,0,2,0]，Methods仍[0,1,2,1,2,0]。原expected hash不改时完整Origin hash先失败Integrity；测试生产者发布新的Carrier/Contribution revision、按实际bytes同步Carrier.Buffers与CarrierOriginBuffers hash后，全hash可通过，但预检row0实际Origin1与Method0.CarrierOriginId0不等，Conflict、OnPage调用数0，Q不等到第二页再发现。另设XYZ三个不同Origin控制列，row0=[0,1,0]、方法Origin0，三列均hash有效仍Conflict；不允许一Method代表不同字段来源，生产者可按各FieldId独立表表达。全Uniform值0且方法Origin1同样预检Conflict，CarrierOriginBuffers=[]合法但不能免核。实际Origin UInt32超int.MaxValue/不在表内则Validity，Unknown/Unsupported错配也失败。Origin reader闩锁时取消/超时与贡献reader相同，原Task未退出不得终态/Released；短读0非EOF，不支持不得假用C2或均匀来源。缺实际方法证据、恶意Source或被替换的可信expected仍按§15.4信任边界，Origin一致不证明算法物理正确。

实现者视角有限走查：从P目标XYZ→Origin闭包→两scope预算/全hash→CSR及实际Origin预检→重读核对/完整双父→末页digest→Dispose，逆例覆盖metadata越界、首/后页错行Origin、字段不一致、后页坏权重、停于两个reader/hash/consumer/Dispose的取消。后页坏权重虽前页已暂存，整批不能采用；预检只证明请求meta与Origin关联，不证明原方法物理正确。外部空Host视角：P/Q完整Options/Ports/Descriptor/两buffer集合/双reader/Method/Request/consumer由公开factory装配，Uniform/PerItem、HeightField地址及MaxBuffers合计均明确，没有隐藏UI、另一Source、未定义共享registry、Parent double索引或Source返回伪EOF；两个host分别复制自己预算内摘要，父值/坐标消费另用原Owner。两视角是文档有限自审，不冒充C#运行断言。此轮不重审C1–C4/H/X。

### 15.9 Benchmark、工程与六项定位

C5仍引用binding的唯一Core csproj/BCL Exe，无新DLL/测试包。获准后构建命令同§10，新增执行为：
```powershell
dotnet run --project tests/Modules/surface-data/Asun.Modules.SurfaceData.Core.Tests/Asun.Modules.SurfaceData.Core.Tests.csproj -c Release -- --suite contribution --consumer both
```
必需SD-P01–12和P/Q全部完成、实排空才0；未完成/跳过/超时非零并列ID。真实wall watchdog10/120/180s，虚拟业务1s clock不控制watchdog，退出不证明外部资源已归还。本轮未建工程、未compile/run。

BenchmarkProfile按§11/GOV010统计：绑定Contribution Descriptor/revision、Carrier.Key/revision及两scope完整buffer hash、目标字段顺序/OriginBinding/F/U、父snapshot/方法证据hash、N/E/fan-in分布（1/2/max，零权比例）、Parents/Methods数量、stride/endian（含Origin RowStride）、页尺寸/范围/全hash A_c/A_o与requested T、冷热/预热/测量n/并发、Source/慢consumer/取消、请求/service预算与deadline。测Plan→两scope全hash→metadata/实际Origin preflight→页Origin重读/digest及read/decode/顺序/权重和→consumer→Dispose/Released，计两reader实际bytes、逻辑预留/实际复制/峰值/页水位、Exact/Unknown/Unsupported、全部失败删失。完整hash及Origin重复IO代价单列，不以只页吞吐推全表性能；不建跨operation hash缓存。目标未采纳NotEvaluated，权重数值1e-12不是性能/现场精度目标。

| GOV010 §3.1项 | C5具体位置/结论 |
|---|---|
| ①边界/复用 | §15.1/15.7两个无UI不同Surface/页/状态消费者，算法/Viewport/计量不在模块 |
| ②API/资源/版本 | §15.2–6精确目标字段/Origin闭包、同session双scope/双reader、CSR/权重/全hash及预算/digest/EOF/取消关闭/真值边界；API0.1独立，不改C1–C4 |
| ③空host/端口 | §15.7 P/Q两集合实际bytes/hash/双reader/BCL Source/TimeProvider，读上界524/586 bytes及Origin驻留明确；无设备/AsunImage/UI/DB隐藏初始化 |
| ④可判定案例 | §15.7/15.8 SD-P01–12，正常/重复/并发/异常/取消超时/排空/恢复/部分范围与版本拒绝，实际Origin错行/跨页/字段不一致/Uniform反例 |
| ⑤Benchmark | 本节固定全hash、preflight、fan-in/page、阶段与资源/统计；目标来自采用Profile，未有目标不造PASS |
| ⑥落点/顺序/禁止 | 同binding Core/Exe，新增suite命令/10–120–180监督；本轮仅本文，真实桥与真实运行/现场未做 |

C5六项**文档规格已由主控接收，状态ModuleCoreImplementationReady**，含§15.2–15.9实际Origin关联闭包；没有内部DTO/CSR/资源/工厂选择留给实现者临时决定。贡献只是ProducerRecorded记录协议，不证明算法真值、父值或坐标物理资格。实际生产权重/可信方法证据由算法原Owner发布，没有记录则Unknown/Unsupported，不能填假值；实际父snapshot/IM-007/Viewport映射仍由其原Owner接收。C1–C4已接收状态不变，真实Core build/run、权重生产者、Source/IM-007/Viewport桥、性能/HALCON/UI/现场均未验，H/X门不提升。此窄补不要求新HALCON路线/外部算法研究：只承载既有原始记录，已读Viewport Support约束和本模块Source/资源证据直接复用，未拷/运行/修改外部源码。

本轮定向验证仅为文档/合成数学检查：P/Q贡献/Origin原bytes分别200/16与206/24，读上界524/586、digest长度132/150 bytes复算一致；按页重算digest等于整请求digest，交换Origin使原buffer hash及含Origin的digest改变，错配行分别为[0,1]与[0,3]，符合首交付前Conflict反例。Q按Origin RowStride12恢复六行及部分范围Origin1/2；XYZ不同来源与Uniform错配断言一致。CSR页边界与规范offset、Int64大父ordinal little-endian往返、权重/Unknown/Unsupported合成算例均一致；本页本地链接存在、围栏成对、公开类型无重名、SD-P01–12及六项位置齐全。C1–C4四行仍ModuleCoreImplementationReady，旧factory Api0.4保留。未创建/编译/运行C#工程、真实权重算法、Source/IM-007/Viewport、UI、性能或现场资格，不将上述检查写成软件/生产PASS。

## 16. 有限宿主根与源/坐标 Adapter 闭包

### 16.1 构造前根与失败恢复（Host辅助规格）

以下是两个Host及所有桥必须实现的相同有限辅助流程，不新建通用监督模块。根由Host进程持有，建立在任何factory/Source.Open/native启动前。其固定参数为MaxWorkSlots、MaxCleanupSlots、MaxHeldBytes、ObservationLimit、CleanupObservationLimit，全部显式正值，两个时限≤24h；无默认无限等待。一个Host一根，不用静态全局槽。每条根记录为 `(Guid CallId, owner强引用集合, 原Task, byte预留, CTS, 原清理Task, 生命周期, 业务错误, 清理错误)`；未创建Task时Task=null，状态Reserved。slot/byte原子预留失败不得调用factory/Open/reader。根持有记录，方法离栈和窗口关闭不删除。

固定顺序：预留work和独立cleanup槽→保存工厂参数/借用服务/input强引用→同步factory→把返回service绑定原槽→接纳前先在槽内登记启动委托→启动一次Open/Start/native原调用并保存原Task（ValueTask.AsTask仅一次）→有限观察→只有原Task真实退出才可用结果/启动清理→清理真实完成且逐Owner回执确认才减账/退槽。启动同步异常保留原错误并进入清理；factory成功、第一次Close前Host异常也走该槽，不能依赖“已经进入正常finally”。Root锁内仅状态/账，不执行用户委托、回调或Dispose。

有限观察到期/等待token取消不等于终态：仅向原CTS/operation.RequestCancel发信号；已启动的清理用独立token，绝不复用已取消业务token。C2/C5等待原Completion；H等待§17进程/pipe排空；IM-006等lease Release回执；IM-066等Release/ResourceStatus；IM-007保原service/requestId的Query/Cancel/Wait事实。清理槽不等待自己、不阻塞worker的同Completion。只有原清理调用退出后且该Owner公开允许幂等重观察时才可观察同一释放身份，不发第二次析构。业务错误和清理错误分轴保存，finally异常不得覆盖原错误。

Host shutdown先封work入口、取消在途、逐槽有限观察并关闭自己创建的Core服务，最后关自己拥有的上游；借用服务不Close。根若仍Pending/Unknown必须保持进程可查询的强引用和账，退出报告“不完整”，禁止重建服务/复用槽绕过；进程强制终止只对§17自有隔离worker有明确OS归还证明。若Host需把责任交监督器，必须在监督器返回同CallId/owner集合/原Task的接管确认前继续持有；未实现接管能力则不假设有人接管。重新读修订是新业务操作，不能恢复旧Task为成功。

### 16.2 公开桥构造（仅Adapters DLL）

以下类型在 `Asun.Modules.SurfaceData.Adapters`，使用别名 `IFR=Asun.Modules.ImageFrame.Resources`、`SDC=Asun.Platform.StorageDatabase.Contracts`、`CG=Asun.Modules.CoordinateGeometry`。桥无设备、UI、事实发布权；借用服务整体仍归Host。固定公开类和构造入口如下，不需隐藏DI/注册表：

```csharp
public sealed record SurfaceBridgeLimits(int MaxActiveSessions,
    long MaxHeldBytes, long MaxVerificationReadBytes, int MaxSliceBytes,
    TimeSpan ExecutionLimit, TimeSpan ReleaseObservationLimit);
public abstract record FrameBufferBinding(string BufferId);
public sealed record FramePlaneBuffer(string Id, int PlaneIndex)
    : FrameBufferBinding(Id);
public sealed record FrozenFrameBuffer(string Id, ImmutableArray<byte> Bytes)
    : FrameBufferBinding(Id);
public sealed record FrameSurfaceBinding(SurfaceDescriptor Surface,
    IFR.FrameDescriptor Frame, ImmutableArray<FrameBufferBinding> Buffers);
public sealed record StoredSurfaceBuffer(string BufferId, SDC.ObjectRef Object);
public sealed record StoredSurfaceBinding(SurfaceDescriptor Surface,
    ImmutableArray<StoredSurfaceBuffer> Buffers);
public sealed record GridCoordinateBinding(MappingReference Mapping,
    CG.AssetRef Graph, CG.AssetRef SourcePixelFrame, CG.AssetRef TargetFrame,
    ImmutableArray<CG.EdgeStep> Path);
public sealed record TransformCoordinateBinding(MappingReference Mapping,
    CG.AssetRef SourceFrame, CG.AssetRef TargetFrame,
    ImmutableArray<CG.EdgeStep> Path);
public sealed record SurfaceCoordinateBindings(CG.GraphSnapshot Graph,
    CG.NumericPolicy Policy, ImmutableArray<GridCoordinateBinding> Grids,
    ImmutableArray<TransformCoordinateBinding> Transforms);
public static class SurfaceAdaptersFactory
{
    public static ISurfaceSource CreateFrameSource(IFR.IFrameService frames,
        string consumerId, FrameSurfaceBinding binding,
        SurfaceBridgeLimits limits, TimeProvider time);
    public static ISurfaceSource CreateStoredSource(SDC.IFileObjectStore files,
        SDC.IStorageDiagnostics diagnostics, SDC.CallContext context,
        StoredSurfaceBinding binding, SurfaceBridgeLimits limits,
        TimeProvider time);
    public static ISurfaceCoordinatePort CreateCoordinates(
        CG.ICoordinateGeometryService geometry,
        SurfaceCoordinateBindings bindings, SurfaceBridgeLimits limits,
        TimeProvider time);
}
```

所有Create只做有界值校验/深冻结/建账，无IO/后台/lease；null抛ArgumentNullException，非法形状抛命名字段ArgumentException。Limits全部整数/bytes>0、时限∈(0,24h]；MaxSliceBytes≤int.MaxValue。factory冻结的借用服务保持同一实例，adapter不实现整体服务Dispose；每session有自己的§16.1槽。Open/Map前原子核MaxActiveSessions与MaxHeldBytes；无队列，不无限补读。三个桥允许独立装配，某个没有真实输入不阻其它桥。版本随Adapters包冻结，不更改Core Api0.4或Contribution Api0.1。

Source/Map的精确失败用新增Core公共 `SurfacePortException : Exception`（只读 `SurfaceError Error`，唯一构造 `SurfacePortException(SurfaceError error)`，error非null）表达；C2/C5/坐标调用catch后保其Code/Path/Ordinal，限长复制Detail，不引用Adapters类型。它是已有错误值的端口异常载体，不新建错误码/改终态：Cancelled/Timeout仍由原operation决议，资源仍须排空。NotSupportedException/IOException/未知异常沿既有Capability/Io/Internal规则。Adapters不可在未清理session/lease时抛该异常假装资源已归还；未知清理由原Task/根强持。Create有限metadata总字节≤MaxHeldBytes、每字符串≤原ID上限或2048诊断字节；复制前计长，非法超限不先深复制。

**FrameSource：**只接同宽高HeightField的标量位置/属性plane与显式冻结控制/索引bytes；PointCloud/Mesh若上游不是二维frame则走StoredSource/已有ISurfaceSource，不把点云塞伪图。FramePlaneBuffer必须引用frame已有single-channel plane，Scalar精确映射UInt8/Int16/UInt16/Int32/Float32/Float64，ByteOrder原样；Core field同Domain Vertex、紧密本地row-major，buffer.ByteLength=Width*Height*scalarWidth，无AoS、无padding、无多buffer偏移共享。Scale/Bias/Unit与PlaneMetadata逐项一致，原ValidDomain必须等于producer声明的Core位置Valid域（行段比对），另有独立属性状态仍用其冻结控制列，不借位置mask。ImageFrame不支持的UInt32 Origin/Int64 Root只能用FrozenFrameBuffer真实记录bytes，不把位置ordinal冒Root。映射表恰覆盖Surface.Buffers，每Id唯一；Frozen bytes深复制前预检MaxHeldBytes，长度/hash精确符合descriptor。上游2D Intensity/显示8位/DisplayOnly不得冒Height；没有明确高度/Frame/单位/Grid来源时Create拒绝。

Open深比较expected→预留frame完整访问/单行scratch/冻结副本与hash scratch→以新Guid请求 `frames.ReadAsync(FrameReadRequest(...,frame.Key,精确planeIndices,全幅PixelWindow,0,ClipAndMarkInvalid,ExactSamples,剩余ExecutionLimit),token)`。ClipAndMarkInvalid只允许保原缺测槽/域，不补值；RejectMissingSupport不能用于有孔的高度载体。只接受Completed或Empty（全域无Valid仍保原槽）且Drained/OperationResourcesReleased及精确SourceKey/SourcePlaneIndices/无crop的ActualWindow/原Metadata.ValidDomain；错误返回若带lease也登记清理。TryOpenReadScope成功后，每次CopyRow先复制紧密rowBytes到单行scratch，ReadInto按BufferSlice offset算row/row内片段，跨行按顺序复制到destination；scope只在同步CopyRow期间借用，不把Span跨await。每次可检查token/deadline，未写满失败不报成功。Open流式核全部frame plane与Frozen bytes SHA256（非行padding），总原bytes≤MaxVerificationReadBytes，核完才能Integrity=FullBuffers；若上游对Invalid/Unknown槽改变原编码而不保真实bytes，则hash失败，本桥不承诺该Source全原值，不修hash洗成无损。否认时Io/Integrity异常且先清理，不把producer摘要当验证。session保持该lease直至所有read退出；dispose先关闭scope，再原lease.ReleaseAsync(ReleaseObservationLimit)，按同lease后续幂等观察至StorageReleased+Drain确认，无确认保持pending。ImageFrame租约持有字节取实际AllocationCharge总额去重，full-frame太大则拒绝本桥，而非擅自假budget/拼碎快照；需大图tile消费者使用IM-006已批准tile接口，不能拿每tile不同修订拼当前session。

FrameError精确投影：InvalidArgument→Input、UnsupportedFormat→Capability、LayoutOutOfBounds→Layout、BudgetUnavailable/BudgetExceeded同名、LeaseClosed/Closed→Closed、InsufficientSupport/InvalidSample→Validity、Cancelled/Timeout同名、AdapterFailure→Native、StaleRevision/Conflict→Conflict、NotFound→Io；Unknown/DrainUnknown不证明释放，保持pending。Slice!=null不等读取成功，每错误带slice均登记归还；对合法明确的Empty源按Core空range不Open，Frame高度桥自身不发布零宽高HeightField。

FrameSource单行RowBytes须≤MaxSliceBytes及int.MaxValue，冻结控制bytes+metadata M+frame.Layout.DeclaredBufferBytes+2*MaxSliceBytes≤MaxHeldBytes才Open；一lease返回后实际AllocationCharge去重总额不得超过这份预留，违约先清理再Resource失败。每session完整hashscratch/单行scratch不并行分配，预留两份保守账；Buffers/Fields/Metadata/DomainRows总数与字符串均受原SurfaceOptions/FrameBudget限额及byte账，不能先无界深拷贝再校验。scope CopyRow串行，session不接受同时两ReadInto（Input）；Dispose在真实read退出后进行，不早关scope。

**StoredSource：**输入表恰覆盖每buffer，Object.Bytes=ByteLength、Object.Hash与Buffer.Sha256精确相等，Format必须为宿主登记的`surface-raw-buffer/1`原bytes（无压缩/单位转换）；ObjectKey不是文件路径，context由Host权限Owner提供。一个session固定这些ObjectRef，不读latest/目录head。Open用 `files.OpenReadAsync(FileReadRequest(context,obj,0,obj.Bytes),token)` 逐对象流式SHA256核原bytes（scratch≤MaxSliceBytes），计总量MaxVerificationReadBytes；读取完成需真实Release确认后关闭验证lease，全部成功才标FullBuffers。每ReadInto以同ObjectRef和准确offset/count重新Open范围lease，验证Metadata深相等，从Content逐步读到恰Length；Stream允许短Read，桥补齐最多Length次正向读，0为Io，不将Stream的正常短读传成C2成功/EOF。scope登记原Open/read/release任务；失败含lease仍清理。Release使用同ResourceReleaseRequest.OperationIdentity/Handle及diagnostics.GetResourceStatusAsync(ResourceQuery)，只有Released才完成，Draining/Unknown保原句柄和任务，不再次Dispose猜成功。资源operation身份由本session新Guid及固定context生成，按IM-066规则填完整hash/epoch；先冻结release身份再Open，不复用业务输入Id。无需隐式AcquireRetentionHold/GC写权：对象若在两次窄读之间不可用，整请求Io失败、暂存失效；必须持续保留时由原对象Owner在外部按其已批准保留契约持有hold，本模块借用其已保留ObjectRef，不自动续约/写事实。新revision重开可恢复，原对象不修复。

Contribution的Stored Source在本Adapters DLL的SurfaceAdaptersFactory公开新增静态 `CreateStoredContributionSource(SDC.IFileObjectStore files,SDC.IStorageDiagnostics diagnostics,SDC.CallContext context,Contribution.ContributionDescriptor descriptor,ImmutableArray<StoredSurfaceBuffer> contributionBuffers,ImmutableArray<StoredSurfaceBuffer> carrierOriginBuffers,SurfaceBridgeLimits limits,TimeProvider time)`，返回Contribution.IContributionSource；同名Id按两个传参scope分开，原ObjectRef全绑定descriptor两集合，session共用同一冻结Carrier与贡献revision。它不在Open自验全hash（C5 reader按§15必验），两scope都走上述范围读/lease释放规则，避免重复全hash但不降低C5。没有真实贡献记录则Capability，不从Frame Origin摘要生成表。

StoredSource的release身份固定：OperationIdentity.Scope/StoreId/StoreGeneration取冻结context，OwnerKey=`surface-data`，OperationId=本次release Guid的`N`格式，IdempotencyKey同OperationId；PayloadHash=SHA256(ASCII `SDREL1\0\0`+session Guid16+scope字节0贡献/1Origin/2Core+BufferId的UInt32LE ASCII串+Object.Key的五个声明字段+Object.Bytes Int64LE+Object.Hash.Hex的ASCII串+slice offset Int64LE+count Int64LE)，ObjectKey.Generation按Int64LE、其它字符串为UTF8 UInt32LE长度，无culture。验证lease用offset0/count完整长度。ResourceReleaseRequest.Handle取原lease.Handle，不用请求临时造handle；context的ExecutionBudget/WaitBudget分别裁到原剩余期限与ReleaseObservationLimit，清理独立有限budget不延长业务采用。身份在预登记后固定，Query沿其原epoch，失败再发同对象新读用新release身份。

**Coordinates：**仅消费冻结CG GraphSnapshot/Policy/AssetRef，不做第二套坐标数学。Grids以MappingReference精确匹配，其Graph=bindings.Graph.Ref；源像素Frame为2D Pixel且Convention明确integer-center、Axis方向Column/Row与Grid引用证据一致；Target为同单位3D源Frame。Transform精确引用同单位3D→3D已有CG path；MappingReference无hash，由binding中的AssetRef hash和Path冻结，不从相同Id推不同资产。路径只ExplicitPath，不ResolveUnique/查latest。FrameReference按Id/revision/unit匹配AssetRef对应Frame，Graph/Policy所有bytes/字段均冻结。

Map只把Valid项按原顺序形成CG.Point2Value/Point3Value批；Invalid/Unknown位置不提交、不补0，回来原State/Reason/Origin不变。Height先用 `ParentColumnOffset+i%Width`、`ParentRowOffset+i/Width` 的精确整数父像素中心，经Grid path到源3D Frame；整数>2^53或不能精确binary64表示则Frame拒绝，不舍入。Z不是相机未知深度：Grid路径固定只允许二维Affine/Translation/Identity后接一个PlaneLift，lift的origin.Z与basis两列Z精确0，后续3D只可保持Z=0平面的Affine/Translation/Identity（矩阵第三行[0,0,a]、offset.Z=0），输出必须Z=0；不接camera/projective/LocalField/非平面模型。点返回X/Y采用，Z始终来自该carrier物理高度；非平面/Height相关模型Capability拒绝，原IM-007能力若将来扩展须明确合同，不丢原Height去猜。如Target不同，第二次用显式Transform path映3D `(X,Y,Z)`；XYZ同Frame无需Map，上游仍按Core规则。PixelConvention精确为CG.PixelConvention.Center，axes按CG既有ImageColumnRow约定验证（Pixel row正下、lift通过明确矩阵表达符号），不能把显示负row规约借进此Grid路径。

调用为 `geometry.SubmitAsync(GeometryRequest("0.2",新requestId,MapWork(graph,source,target,ExplicitPath(path),GeometryBatch(本批AssetRef,source,items,NoCovariance),policy),剩余ExecutionLimit),token)` → 以原requestId WaitAsync/QueryAsync，MappedResult必须Completed且Drain Confirmed、frame/path/backend/inputhash精确、项数/Point3类型/有限值合法。NoCovariance明确NotProvided；Policy允许Optional，否则本桥拒绝，不制造0误差。批AssetRef hash为本批冻结CG值的官方canonical编码，不用Core bufferhash替代；CG负责计算/确认其InputHash。本地先编码冻结这批并计MaxHeldBytes；不依赖运行全局资产库。取消用原实例CancelAsync，保原Task/identity至Drain确认才完成Map；旧service epoch无法查询时pending，不重建服务。

CG错误精确投影：CG001/006→Input，CG002/014/016→Conflict，CG003→Unit，CG004/005/015→Frame，CG007→BudgetExceeded，CG008→Cancelled，CG009→Timeout，CG010→Native，CG012→Closed，CG017/019/020→Capability，CG018→Frame；CG011/013只是Lookup/Drain未知，保原Task/根为pending，不造已清理失败。保原Diagnostic.Code/Ref作为Detail，SurfacePortException只在CG真实资源确认之后投出。Convention不符→Frame、非平面Grid→Capability、>2^53父像素→Frame、同Id异asset hash→Conflict。上游错误投影不能替改变CG裁决/状态。

### 16.3 双消费者和上游证据边界

Replay-A将HF-A的Float64高度tight拷贝到3×2 IM-006 CopyStorage（字段layout更新到offset0/stride8/rowstride24、buffer48 bytes并由producer新Key/hash发布，不改旧fixture）；State/Reason/Origin/Int64 Root按HF-A真实合成bytes作为Frozen绑定。frame service由其公开IFrameServiceFactory配合new Asun.Modules.ImageFrame.Core.ManagedLayoutValidator()创建，PlaneMetadata单位mm、Scale1/Bias0、位置Valid域row0=[0,2)、row1=[0,1)与[2,3)；只检域一致不把Invalid/Unknown混为一类。frame.Layout.Domain=Full（所有原槽可寻址）、Metadata.ValidDomain=上述三段。完整软件ResourceLimits为FrameBudget=(65536,65536,16,16,synthetic-deployment,1,synthetic-frame,1)，MaxCpuBytes262144/Native0/Gpu0/Cache0、MaxFrames4/Active4/Queued1/Receipts64、Retention1min/Drain1s，consumer-Publish与consumer `surface-replay-a` 各ConsumerLimit=(65536,4,2,1)，eventSink=null；frame实例/epoch/Key由PublishCopy原回执取得，不手造lease；本adapter限制可更严不能抬上游账。SurfaceBridgeLimits固定软件参数=(2,262144,4096,4096,1s,1s)，Time为各Host独立受控clock。

Coordinates用CG冻结PlaneLift path：origin(10,20,0)、basis列(.5,0,0)/(0,.25,0)，source Pixel目标mm，绑定Grid=`grid-a/1`。CG service按 `new CG.CoordinateGeometryFactory().CreateManaged(RuntimeLimits(2,16,16,16,8,8,65536,65536,262144,1s),clock)` 准确创建；Policy软件参数MaxConditionNumber=1e6、MinDenominatorRatio=1e-12、Orthogonality/Covariance/InverseResidual容差各1e-12、MaxPathDepth4/MaxPathCandidates4/MaxGraphVisits64、Uncertainty Optional、AlgorithmLimits=(64,4096,100000,64,256,32)。Pixel/mm FrameRules AxisScales各全1、BoundaryGuard0、MaximumCoordinateMagnitude1e6；源domain为覆盖父像素(4..6,8..9)的Closed Box2，目标Frame domain为Closed Box3 min(12,22,-100)/max(13,22.25,100)，PlaneLift自身固定Z=0而该Frame允许真实高度，assets/数值Policy来源标Synthetic。每AssetRef hash由CG已有canonical来源规则和本fixture完整值生成，发布账冻结，不拿任意字符串当真实asset证据。此图仅测试确定的plane数学，不依赖真实标定。原crop仍产生(12,22,0)/(12,22.25,3)，Invalid/Unknown状态保留；Host仍保原Core读取Profile并分别给桥计额外预读/asset账，不能在Core Budget外悄悄消费它们。

Audit-B独立进程使用mesh-B以及P/Q元数据和原buffer对象，通过IM-066 IFileObjectStore/Diagnostics的独立读Host装配（§7.1.2），将每原buffer以raw format登记ObjectRef、Object.Bytes/hash按真实fixture bytes；不需A的frame服务。只读Host不调用StageAndSeal。两个Host分别保自己的根/借用session；真实Store/Profile/CG资产hash由发布Owner输入，合成测试只使用其有限内存端口，不假称已有真实对象。这两个构造是桥的具体消费者，与已接收Core A/B/P/Q验算分开。

Audit-B SurfaceBridgeLimits与Replay-A相同，每次源验证额外读量另计4096独立限额；Core逻辑Budget不宣称涵盖上游额外IO/lease。两个Host的根都固定work/cleanup各16槽、MaxHeldBytes1048576、观察与cleanup各1s（H单独按§17较大账）。用IM-066已定义内存File Backend/Runtime及只读CallContext，权限缺失单独反例；StorageProfile采用其Host-B的完整有限配置，raw format/metadata validator按§18.3明确注册，不能让开发者自选写入事务或数据库表。H与桥case有独立Profile和真实wall watchdog，不无限等后运行下个case。

## 17. H公开封送、数值策略与隔离执行

### 17.1 公共签名与固定调用

2026-10-11只读公共程序集 `AsunImage/bin/Debug/net8.0-windows7.0/AsunImage.dll`，AssemblyVersion=26.5.0.0，SHA256=`5d16a30a9ec73dad9dc6c2faf08001ae645ab66d4b0acda5c34ba881a0d9cf88`。未读/反编译内部；此读取是公开重载/封送证据，不安排旧程序集版本迁移/授权审核。实际公开类型为 `ImageLibDotNet.Cv2`，Worker明确 `using cv2 = ImageLibDotNet.Cv2;`，下表用该别名，避免把类型大小写猜成另一个API：

| 调用名/参数顺序 | 已查公共形状/资源 |
|---|---|
| cv2.GenImage1(out HObject image, HTuple type,width,height,pixelPointer) | 输入紧密float[]，Type=`real`；固定pin后以HTuple(IntPtr)传实际64位地址，调用真退出才unpin；HALCON复制像素，禁止gen_image1_ex外借内存 |
| cv2.GenRegionRuns(out HObject region, HTuple rows,begins,ends) | 有限int[]，同长、按row/col排序、end≥begin闭端；只用Valid域，零Valid提前空输出不造region |
| cv2.ReduceDomain(HObject image,HObject region,out HObject reduced) | 三图用同region、各保存原图及返回图直到模型创建退出；不修改全局system配置 |
| cv2.XyzToObjectModel3d(HObject x,y,z,out HTuple model) | H1，读mapping_size/row/col和XYZ核唯一关联 |
| cv2.GenObjectModel3dFromPoints(HTuple x,y,z,out HTuple model) | H2，三double[]长度=Valid数量，按输入slot次序 |
| cv2.SetObjectModel3dAttrib(HTuple model,name,attachment,values,out HTuple copy) | name=`&sd_slot`、attachment=`points`、values精确int[] slot，产生新model，原model仍需clear |
| cv2.SelectPointsObjectModel3d(HTuple model,names,min,max,out HTuple selected) | H3，轴按X/Y/Z固定排序，值按input.Unit→m，闭端多轴AND；empty intervals跳此调用 |
| cv2.GetObjectModel3dParams(HTuple model,names,out HTuple values) | 每次只查一个属性，先num_points/has_xyz_mapping及extended_attribute_names，再XYZ/mapping/slot，避免混合长度猜解析 |
| cv2.ClearObjectModel3d(HTuple model) | 每成功创建的独占model一次，反创建序；clear真退出才Dispose承载HTuple，不用HTuple.Dispose代替模型clear |

HObject公共Dispose、HTuple公共构造(double[]/int[]/long[]/IntPtr/string)/Length/ToDArr/ToIArr/ToLArr已查；iconic region/image在最后读使用退出后逐一Dispose，控制tuple亦独立Dispose。typed object model handle不进入Core/pipe/视口；每成功out立即登记Owner，不先执行下一算子。异常时仍按登记清理；无法确认clear则由隔离worker退出事实处理，不宣称托管Dispose释放对象模型。参数属于worker唯一线程，无同model并发clear。

### 17.2 float32误差与输入策略

H1图像`real`为4字节float，不是binary64。新增值类型 `NativeAccuracyPolicy(string Id,ulong Revision,double MaxCoordinateRoundTripError)`（Core namespace），阈值以NativePointInput.Unit表示，必须有限≥0、显式来自用途Profile；0表示要求精确往返，不提供默认客户误差。该策略通过§17.3 RuntimeBinding提供，不改已接收Core读取。不能从测量公差自动取某比例、从图像色带猜单位或把float转double称恢复精度。

H1固定转换：Valid原double坐标按Unit倍率(m1/mm0.001/um0.000001)转m并检查finite→round-to-nearest-even转float并检查finite→gen_image1。读回double m→同Unit，逐坐标 `abs(readback-original)≤MaxCoordinateRoundTripError`，且需唯一mapping/点数正确。无局部原点/静默自适应策略，超误差Integrity拒绝，保CPU源可由Host明确选另一输入表示/新请求，不自动fallback。原Invalid/Unknown三float图槽填固定0但domain排除，不能据填值生成点；使用pin自己生成的图，不读原source pointer。

H2使用double tuple，仍逐XYZ单位往返与误差阈值核对。H3结果所选slot集合必须等于原CPU坐标在显式闭区间内的集合（这只是协议校验，native仍实际执行筛选）；量化/单位换算导致边界进出不一致即Integrity，不能夹紧/偷偷补slot。输出SelectedSlots按原slot递增，Positions从CPU原input拷贝，State/Reason/Origin保持，native量化坐标仅用于验证不覆盖原测量值。全无Valid或空input明确Completed空；非空Valid调用失败不得降为空成功。有效0/负高不删，派生Origin仍派生。

参数推荐边界：本模块不拟合高度、不估误差、不自动选父/权重/阈值、无学习参数。Core计划按§4/15.5预算二分块大小只改变执行分块，source/域/权重不变；H1/H2按表示固定选择、H3轴区间必须显式、MaxCoordinateRoundTripError来自用途Owner。若要求建议，Host可显示本计划BlockItems及拒绝原因作为纯建议，只有新显式请求采用；没有隐藏采样率/LOD质量默认。

### 17.3 精确运行绑定与内存硬界

HALCON对象模型算子页不提供可证明的逐点native峰值上界；本模块不能用经验倍率假定。H真实主线因此固定**每请求一个Windows隔离worker**、值copy IPC、进程commit硬上限；这是原H能力的执行/资源策略，不新增视觉算法或独立模块。父进程ImageLib DLL不调用native，不依赖全局HALCON池。公开新增同名Create重载（ImageLib namespace）和Core值：

```csharp
public sealed record NativeRuntimeBinding(string WorkerExecutable,
    string WorkerSha256, string AsunImageSha256, long WorkerCommitLimitBytes,
    int MaxWireBytes, NativeAccuracyPolicy Accuracy);
// SurfaceImageLibFactory member; original two-argument member remains defined.
public static ISurfaceImageLibPort Create(ResourceBudget adapterBudget,
    TimeProvider time, NativeRuntimeBinding runtime);
```

WorkerExecutable必须绝对路径，明确部署包版本/hash，factory只freeze/形状校验不读文件；执行前stream hash worker及其绑定AsunImage程序集，错误Integrity且不启动native。不是许可/版本兼容核验。MaxWireBytes正int、WorkerCommitLimitBytes正long且可表示目标x64 SIZE_T，Accuracy按§17.2；不使用PATH/当前工作目录寻找任意exe，不接插件程序。三个参数factory无hidden thread/native，配置错误沿§7.1异常规则。每adapter最多一个active Filter，原子预留失败BudgetExceeded，不排队；同时需两个请求的Host明确建两个adapter且根总账覆盖两份，不为绕pending重建。

N=input数组数，R≤N为Valid行段数。父CPU保守账为 `M+256*N+24*R+2*MaxWireBytes+16384`（原3数组/两个封送copy/解码/slot/排序/日志控制块，M沿§4全部字符串记录）；每数组加64元数据，并检查每乘加/int长度。完整原input借用也计账，输出长期保留归Host另账。进程账另加WorkerCommitLimitBytes：两者总和≤request/adapter MaxResidentBytes和Host根MaxHeldBytes；N须同时≤MaxItems/MaxBlockItems（H的单次图/tuple工作块），不能把单幅图拆模型偷省关联。读预算原input tight量16*N+40*N（两个long列和保守Position40）≤两MaxReadBytes，pipe重复量单列且≤MaxWireBytes，不把IPC叫源读取。没有足够runtime baseline的低预算在启动前拒绝，不把synthetic-a65536当能启动HALCON。

Windows JobObject固定limit flags：PROCESS_MEMORY|JOB_MEMORY|ACTIVE_PROCESS|KILL_ON_JOB_CLOSE，ProcessMemoryLimit=JobMemoryLimit=WorkerCommitLimitBytes、ActiveProcessLimit=1；无BREAKAWAY/SILENT_BREAKAWAY。这是OS committed memory上限，**不等于RSS/全部kernel/GPU byte上限**，GPU能力未启用。native/CLR子进程commit都在job内；父CPU/pipe另计。factory不宣称内存工作集硬实时，实际PeakProcessMemoryUsed/PeakJobMemoryUsed/managed/native/OS失败单列Profile。CreateJobObjectW→SetInformationJobObject(JobObjectExtendedLimitInformation)→CreateProcessW(CREATE_SUSPENDED|CREATE_NO_WINDOW、仅所需pipe句柄白名单、固定exe)→AssignProcessToJobObject→ResumeThread；任一步失败清尚未运行进程及句柄，Resource拒绝，不以无job方式fallback。父句柄用SafeHandle、stdcall/System.Runtime.InteropServices公开ABI；结构SIZE_T/指针用nuint/IntPtr，BOOL按Win32、不得int截指针；SetInformation长度Marshal.SizeOf，与官方结构一致。Windows外或job绑定被策略拒绝Capability/Resource，不自动在主进程跑。唯一工作进程不启动子进程，不接受客户命令/文件路径/native handles。

worker stdin/stdout分别独占一有界frame，stderr有限8192 bytes诊断截断并持续读至EOF（超限只丢后续诊断，不停止drain导致阻塞）；stdout只协议不混log。请求frame编码：8-byte ASCII `SDNAT1\0\0`，UInt32LE版本1，Guid.ToByteArray的16个原bytes CallId，UInt32LE payload长度，payload依§18原语规则按 `(NativePointInput各声明字段, intervals数组, Accuracy各声明字段)` 递归编码，末32-byte SHA256核前缀及payload。状态enum按Int32，Position无效槽NaN保原IEEE bits，Valid非有限拒绝；Budget.OperationLimit ticks Int64，原已取消deadline不刷新。响应相同frame但magic `SDNAR1\0\0`，payload为NativeReply声明字段（错误Code/Path/Ordinal/Detail按UTF8长度≤2048、条数≤MaxIssues）；Output只有Completed允许非null。schema固定，不序列化类型名/指针/Task，decoder不得Activator/反射构造未知类型。整体frame length≤MaxWireBytes；分配前check长度/数组项数/checked，未读齐/超长/hash/CallId错/多余frame或尾字节失败，消费前复核原generation/取消。父写完stdin即关闭写端，worker只允许这一帧后EOF；父并行drain stdout/stderr，任何超长/bad frame立即拒绝采用、Terminate原job后仍等原pipe/process退出，不把未读stdout的worker死锁隐藏成“观察超时已释放”。

worker运行顺序：有界收完整frame→核hash/shape/预算/取消时限→按H1/H2创建→保真核对→可选H3→输出CPU原值→finally清全部native/iconic/tuple/pin→ResourcesReleased=true响应→正常退出。父读响应并等原stdout/read/process退出，只有exit0/完整响应/清理确认才Completed；响应先到但process未退继续pending，不采用。调用deadline由父TimeProvider单调固定，worker收到剩余预算不延长父期限。用户取消/时限到：请求TerminateJobObject一次，保原Process/pipe tasks和根槽，等待进程确已终止、pipe task退出、父句柄归还后才Cancelled/TimedOut且Output=null；kill请求成功不是退出。进程终止证明仅本自有worker内存/句柄OS归还，不证明外部服务/源lease已归还（worker没有这些借用）。资源不明/Terminate失败仍pending，Host有限观察而不早return。中途崩溃/commit耗尽非零exit Resource/Native失败，不允许成功响应覆盖；没有可靠内存上限通知时不要臆断OOM，可报原exit/native诊断。

### 17.4 H的双Host、测试和官方证据

H-A用HF-A已完成Core读的CPU副本（完整6槽和原Int64来源），H1运行：仅4个Valid slot [0,1,3,5]参与，NoCoordinates不是H输入。H-B独立worker用mesh-B的PointCloud副本H2，1000um→0.001m，Root大Int64仅CPU旁表；显式Z区间[-100,0]um结果四slot，不借A缓存。两Host各自runtime、CPU副本、job及根；部署worker/hash与进程commit值由实际发布包/有限测试Profile填写，不伪造本轮二进制hash。原Core fixture Budget仍不变；H专用软件Budget分别MaxItems/MaxBlockItems=6/6与4/4、MaxReadBytes4096、MaxResidentBytes1073741824、OperationLimit10s、MaxIssues16；Runtime.MaxWireBytes=65536、WorkerCommitLimitBytes=536870912，adapterBudget同对应H Budget，根MaxHeldBytes1073741824、work槽8/cleanup槽8、观察/cleanup各2s，超限先拒绝。此512MiB commit只定义有限软件测试负载，不称足够所有HALCON环境或现场性能；启动OOM也是必需失败结果。软件fixture的H精度阈值显式1e-3mm(A)/1e-3um(B)，只是错误保护算例，真实用途必须替换其批准Profile。H-A float坐标可能有微小量化，按阈值检查，返回原CPU值。

新增必要断言H03–06：H03=1mm/1um转换、1000000000mm+1e-3mm的real图精度损失/阈值0应拒绝，不静默选择双精度路线；H04=float坐标x=0.1mm与显式下界0.1mm，原/返回m边界集合不一致则Integrity；H05=job绑定失败native调用0、低commit启动失败、stdout超限/坏hash/坏slot/重复slot，全部无采用；H06=read/native/clear/退出闩锁取消及Host factory后异常，原task/job强持、取消后不早Released，A停止不杀B。现H01/02不重复验算；真实算子输出/mapping、Job退出、进程峰值及1h+Profile长稳均后续运行门。

新增本地官方页已读Description/Parameters： [gen_image1](../../../halcon算子手册/operators/gen_image1.html)（复制/pointer64，SHA256 `d268da1562bab640cc506296c1684eaa643f97b84b705d3c9cf47bbdd5c019c3`）、[gen_image_const](../../../halcon算子手册/operators/gen_image_const.html)（real=4 bytes）、[gen_region_runs](../../../halcon算子手册/operators/gen_region_runs.html)（闭端/顺序、不自动检合法，SHA256 `8f7f1845b85bc1873e1507f815f2153d956b6b7561fcdde61396dde4a3b2f203`）、[reduce_domain](../../../halcon算子手册/operators/reduce_domain.html)（域交集不改matrix，SHA256 `36db6809bb11f45ad9c373fa8dfd54fb1f62ac27aaa63ba7d46338189c064fa7`）。gen_image1选复制而非external指针别名；不选set_grayval逐点修改/额外开销，无新算法比较。既有对象模型与固定源码研究§13有效复用。

2026-10-11实读Microsoft [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)、[Extended Limit](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)、[Basic Limit](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information)、[TerminateJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject)：commit limits、active process、关闭kill和退出观察按原API；OS权威无本地新参考副本，不复制二套协议。Terminate并非完整同步回收确认，父仍等process/pipe；不是SDK设备硬停止。此部署策略仍须目标Windows/x64实际验证，不由文档/公开签名推出PASS。

## 18. S：无损元数据序列化与有界重开

### 18.1 唯一公开值codec（Core/BCL）

需要序列化的是不可变描述/贡献关系，原buffer继续独立保留原bytes和hash；图像文件/om3/mesh压缩不成为本codec。公开API在Core namespace：

```csharp
public sealed record SurfaceSnapshotMetadata(SurfaceSet Surfaces,
    ImmutableArray<Contribution.ContributionDescriptor> Contributions);
public sealed record SurfaceMetadataLimits(int MaxMetadataBytes, long MaxResidentBytes,
    SurfaceOptions Surfaces, Contribution.ContributionOptions Contributions);
public sealed record SurfaceMetadataEncodeResult(ImmutableArray<byte> Bytes,
    ImmutableArray<SurfaceError> Errors);
public sealed record SurfaceMetadataDecodeResult(SurfaceSnapshotMetadata? Metadata,
    ImmutableArray<SurfaceError> Errors);
public static class SurfaceMetadataCodec
{
    public static SurfaceMetadataEncodeResult Encode(SurfaceSnapshotMetadata value,
        SurfaceMetadataLimits limits);
    public static SurfaceMetadataDecodeResult Decode(ReadOnlySpan<byte> bytes,
        SurfaceMetadataLimits limits);
}
```

无factory/IO/Source/线程；Create不存在。Limits含Api0.4及Contribution Api0.1、全既有quota，MaxMetadataBytes正int，MaxLayers同时限制Contributions数量；Contribution数组可Empty不可default。null/无效limits及载荷返回Input/Version/BudgetExceeded，不抛作为常规协议错误；fatalOOM等不承诺回执。成功Encode.Bytes非default（完整信封），Errors空；失败Bytes=Empty、Errors非空。Decode成功Metadata非null/Errors空，失败Metadata=null/Errors非空，不发布半解码对象；错误最多256沿§4。纯Encode前先有界计长再分配，Decode在分配前核层/字段/buffer/origin/parent/method及长度，不给用户enumerable/JSON无限遍历。

MaxResidentBytes正long。Encode计元数据M（§4每record128、每数组64、全部原字符UTF8长度，字符串托管副本另按2*字符数+64）+2*编码信封bytes+256*2048诊断；Decode先以固定cursor无分配扫描/计长/核结构（固定schema深度≤16），同样计解码对象M+输入信封借用bytes+256*2048诊断。任一checked溢出/总上界>MaxResidentBytes在分配结果前BudgetExceeded；输入已有DTO/bytes仍归调用方，无codec端无限缓存。结果数组/DTO长期保留由Host以返回实际大小另计，不在函数return后暗持第二份。

metadata.Surfaces按§2–4完整Validate；每贡献按§15完整metadata Validate。贡献Carrier必须与Surfaces.Layers中同Key完整深相等，Contribution `(Id,Revision,Carrier.Key,Domain,CarrierFieldId)`不得重复；不同FieldId有各自独立descriptor。Layers/Contributions保输入顺序，不自动排序/选层；两scope buffers照原序列编码并遵§15.3 Origin数组规范顺序。每descriptor受对应Options quota，整manifest所有嵌套记录字节受MaxMetadataBytes，单Id最多128 ASCII/hash64，不因重复Carrier让总账遗漏。Decode的单数组项数≤其语义quota及`remainingBytes/最小元素宽度`，字节串/递归记录先checkCount再allocate。模式无递归对象引用：贡献Carrier嵌入值，不能指自身、不能创建CLR反序列化类型/任意constructors。

### 18.2 编码、信封与版本

格式Id=`surface-metadata/1`；magic8 bytes ASCII `SDMETA1\0`，UInt32LE schemaVersion=1，UInt32LE payloadLength，payload，32-byte SHA256(header+payload)。总长度=48+payloadLength，必须恰输入长度，不接受尾字节/多对象拼接；hash只完整性不授予信任/权限。限制在hash计算前检shape与总长，hash错误Integrity，未知magic/version Version。压缩未开放、无ZIP/Brotli/Gzip探测。读取原对象/网络host在任何读入前限该MaxMetadataBytes，不能先readAll再叫Decode。

原语固定：bool=1-byte 0/1；enum=Int32LE（含SupportState，不用C5 buffer编码宽度冒manifest编码）；int/uint/long/ulong对应4/4/8/8 LE；double按原IEEE754 binary64 LE、元数据finite、保-0位、不改Scale/Bias。string为UInt32LE ASCII字节数+原ASCII，无BOM/culture/Unicode折叠，不null则须符合原字段规则；nullable以1-byte 0=null/1=存在后编码值（空字符串存在，按字段是否允许）；ImmutableArray为UInt32LE count+原顺序元素，default非法。record逐字段**按本文公开声明参数顺序**递归展开：SurfaceSnapshotMetadata→SurfaceSet→SurfaceDescriptor/FieldDescriptor/Layout/Binding/Origins→ContributionDescriptor/Parents/Methods/Layout；SurfaceKey/FrameReference等record struct同序。ResourceBudget/Options/TimeProvider/plan/operation/receipt/native/session不在manifest，不能顺手持久化运行对象。Field/Buffer Unit/ByteOrder/Domain/Origin定义全部来自§2/15，不靠字符串`System.Type`推分支。payload中无重复字段名、扩展字段或隐含版本；新增必需字段/改顺序须新schema，不偷偷ignore。

snapshot身份由可信发布Owner绑定manifest全信封SHA256、所有原BufferDescriptor hash和父证据；本文不创造第二个生产事实Owner。Storage Object.Format采用该format，元数据hash与对象原byteshash对应；原buffer采用`surface-raw-buffer/1`、MediaType application/octet-stream且所有原padding保留。绑定ObjectRef的查找表不进Core manifest：由Host受信发布包精确提供scope+Id→ObjectRef，漏、多、异hash拒绝；权限/保留/提交归IM-066/业务Owner。C5两scope同名Id仍分开映射，不能裸Id全局检索另源。源反序列化只恢复DTO值，必须重新Validate/Plan并Open新的真实session，不恢复旧lease/handle/Task/generation/Complete/ProductionAccepted。

完整最小合法Golden：SurfaceSet Id=`s`/Revision1，Layers恰一层，Contributions=[]。该层Key=`e/1`、Kind PointCloud、VertexCount=FaceCount=0、Unit Millimeter、Frame=`f/1`/Millimeter、Grid=null；VertexIndices=(StableOrdinal,0,Root=`e/1`,FieldId=null)，FaceIndices=null。Buffer恰`b`/ByteLength0/hash SHA256(empty)=`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`；三个字段x/y/z的Role X/Y/Z、Domain Vertex、Encoding=(Float64,1,mm,1,0)、Layout=(b,0,8,0,LittleEndian)、Validity=(Uniform,Unknown,null,0,null)、Origin=(Uniform,0,null)、FrameDependent=true。Origins恰Id0 Unknown、Parents=[]、MethodId=`unknown`/MethodVersion=`1`、ParametersSha256空、HasExactParentIndex=false。空PointCloud合法，不改变§2“SurfaceSet.Layers非空”的规则。

该payload529 bytes、header16、trailer32、完整577 bytes；trailer SHA256(header+payload)=`f64c10f2909c0ac7a969da8b9d57f43d655696dd37290876f306bf8d096e454f`，整个信封SHA256=`66bc511cb63bf21d738fbaa17631dc50e2e01b0d4983e95623bdcbcf615fa9c0`。完整原bytes如下（无换行字节）：

```text
53444d455441310001000000110200000100000073010000000000000001000000010000006501000000000000000200000000000000000000000000000000000000020000000100000066010000000000000002000000000100000000000000000000000100000065010000000000000000000100000001000000620000000000000000400000006533623063343432393866633163313439616662663463383939366662393234323761653431653436343962393334636134393539393162373835326238353503000000010000007801000000010000000900000001000000020000006d6d000000000000f03f0000000000000000010000006200000000000000000800000000000000000000000000000001000000010000000000000000000000000001000000000000000001010000007902000000010000000900000001000000020000006d6d000000000000f03f0000000000000000010000006200000000000000000800000000000000000000000000000001000000010000000000000000000000000001000000000000000001010000007a03000000010000000900000001000000020000006d6d000000000000f03f00000000000000000100000062000000000000000008000000000000000000000000000000010000000100000000000000000000000000010000000000000000010100000000000000070000000000000007000000756e6b6e6f776e0100000031000000000000000000f64c10f2909c0ac7a969da8b9d57f43d655696dd37290876f306bf8d096e454f
```

Golden软件Limits=MaxMetadataBytes65536/MaxResidentBytes1048576、SurfaceOptions沿Host-A、ContributionOptions沿P；codec无native/Source。HF-A/mesh-B/P/Q另外按完整构造配方独立字段展开全部descriptor（尤其Layout.RowStride/Encoding/OriginBinding/CarrierOriginBuffers/Int64父数），不得只用最小向量证明所有场景。原buffer不重序/不转double；比较Encode→Decode逐字段及原byteshash全部相同、再Encode信封byte-for-byte相同；actual调用codec，expected由独立字段fixture拼接，不双端使用同一个编码器造假覆盖。

### 18.3 重开、损失和恢复

存储格式注册在Adapters公开新增两个静态factory成员：`SDC.IStorageObjectFormatValidator SurfaceAdaptersFactory.CreateMetadataFormatValidator(SDC.VersionRef format,SurfaceMetadataLimits limits)` 与 `SDC.IStorageObjectFormatValidator SurfaceAdaptersFactory.CreateRawBufferFormatValidator(SDC.VersionRef format,long maxBufferBytes,int readChunkBytes)`。返回内部实现只提供上游Format和ValidateAsync；factory冻结format（Id分别surface-metadata/surface-raw-buffer、Revision1、完整发布包Hash）及有限limits，无IO。注册Hash由该格式发布Owner的版本包给出并精确登记，不伪造本轮二进制Hash；对象Format必须整条VersionRef相等，不能只比Id。raw最大长度正long、chunk正int且≤maxBufferBytes，metadata按§18.1limits；校验前bytes≥0且≤指定上限，已知超限不读/分配。

Metadata validator最多读bytes≤MaxMetadataBytes的独立byte[]，stream允许短读、0早于长度为Io，读取完恰bytes再Decode；失败抛SurfacePortException(Error)，无metadata对象发布。raw validator只有限scratch串流读恰bytes，不解释Height/单位/状态、不修改原buffer，0提前Io；hash由IM-066已批准技术层实际核验，与BufferDescriptor相等由Source/producer核，不重复造另hash权威。两个validator不Dispose/保留传入stream，不seek、不开外部IO、不触发Core Source/CG/H或读取其它对象；ValidateAsync原Task退出才归还本scratch。创建者把它们准确加入ResolvedStorageConfiguration.FormatValidators，原Runtime拥有调用/技术错误投影，借用validator无native，无需Close。业务写入仍由Producer/Host的原IFileObjectStore流程完成，不在surface公开发布入口。

Replay读取链：受信Owner的准确manifest ObjectRef→IM-066有界读原信封/lease真实Release→Decode/Validate→精确scope表→§16 StoredSource/StoredContributionSource→原Core Plan/Start→原Completed后采用。Audit独立CLI同链但不调显示、不依赖Replay数据库私表；命令配置/API/版本/Profile各自冻结。offline/权限变化/hash错/缺buffer不写“空成功”，保上游诊断，修原Owner引用/权限后新读。解码失败无半descriptor/无native，运行失败原根继续清理；新manifest旧包Decode Version，可回退旧包+旧适配+旧manifest，不覆原bytes。

§8 X候选PLY/OBJ/STL/PCD/OFF/STEP/om3导入仍无当前执行权：它们不携全domain/index/Origin/贡献/单位事实，调用此codec不能补丢失信息。本模块没有通用文件选择器/外部格式猜测、LossReport未知默认、自动反射Deserialize/native handle序列化；若以后获批实际format需求须单独冻结格式/属性映射/损失/双消费者/API，本轮不把未获批需求伪装已设计生产能力。


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

## 19. 全批准范围的文档准备、自审与剩余Owner

### 19.1 覆盖和本原会话结论（2026-10-11）

**当前全部已批准范围的可决定软件设计已闭合；本原会话结论为文档准备完成，不等待总控内容审核，不等于代码/集成/生产Ready。** C1–C5六项已接收范围/算法/API/有效向量未重新审算；本轮实际缺口在§16–18补足并按§19.2有限自审。Adapter/Core codec/native隔离与误差拒绝都有明确实现者、本模块工程落点及步骤，不能笼统转成“未来Owner待设计”。无产品代码授权，本轮无工程/测试文件/过程报告。

| 批准能力/用途 | 唯一实施章节 | 明确不适用/准备结论 |
|---|---|---|
| 2D高度输入、规则HeightField、XYZ PointCloud、已有Mesh、多层 | §1–6/9/16.2 | 单纯2D灰度/颜色是IM-006图像，不自动生成Z；Depth由明确Height plane构成。多层不默认最高/最近；已完成设计 |
| 有效域、属性独立state/reason/Origin、单位/crop/源索引 | §2/4/5/16 | Invalid/Unknown/0/负高明确，Int64不double化，像素/物理域不混；上游丢float精度不能恢复 |
| 误差/坐标/计量资格 | §5.3/16.2/17.2 | CG path/asset精确引用、NoCovariance非零误差；H float误差显式拒绝。质量/协方差/客户精度归原Owner，本模块不出计量合格 |
| 实际多父、方法/权重、Origin关联、CSR分页 | §15 | ProducerRecorded协议，实际方法/输入证据必须上游给；不造权重/物理真值 |
| HALCON数据桥/筛选/属性与唯一释放 | §7/17 | H1/H2/H3固定，float/domain/slot完整核；无重建/normals/三角化/滤波或mesh显示重编号，隔离预算已定 |
| 独立Source/IM-006/IM-066与IM-007接线 | §3/16 | 包引用/公开factory/字段/lease/task/回执具体，单个真实Owner输入缺失只阻其调用；桥不存在隐式global registry |
| 元数据序列化、无损重开、版本与回退 | §8/18 | 原payload全部独立字节/hash，typed有界codec；不持久handle、receipt或质量状态；X候选标准文件不在执行范围 |
| 可选View/LOD/2D联动与多父Support消费 | §9.3/15/Viewport §15.2.5及§15.3 | IM-060已给AcquireLod/ReadProfile/ProjectOverlay/Pick/Support桥，显示LOD不送硬量测；不在SurfaceData新建UI/LOD算法 |
| 并发、预算、取消/异常、有限根与恢复 | §4/5.2/15.6/16.1/17.3 | 全原task/owner/cleanup强持，未知不Released，H硬界只指OS commit；无自动重试坏快照 |
| 参数/建议与Golden/性能/双消费者 | §9–11/15.7–9/17.2–4/18–19 | 无隐藏高度算法阈值，分块建议不改事实；新桥/codec/H分别双Host，负载与资格判断可执行 |

Viewport有完整既有公开接入与三语/DevExpress25.2.3 PageContract，本模块对照其§15.2.5/§15.3不再写“公共类型待猜”。ISurfacePayload私有包装只存精确descriptor/CPU受限副本、Root/Ordinal/domain/state/Origin/C5引用，borrow归Viewport.DisplayLease；其Root+backend generation由IM-060控制。显式选择显示LOD0/其它DisplayOnly token须保源identity+可逆原ordinal映射，显示ZMultiplier/相机不改原坐标。显示sample或体素质心没有真源映射则NavigationOnly，不返回可测量源；Observed精确root与C5派生贡献在查看桥分开。Core未提供AcquireLod/Pick不是本模块软件欠账，详见IM-060已定义能力责任。语言/快捷键/权限/关闭与1920×1080验证仍按原PageContract，不在Core重复DevExpress控件、影像/语言切换入口；本模块无页面不适用其独立UI验收。

### 19.2 本轮有限自审、必要反例与验证计划

第一视角沿外部空Host：原服务factory前异常也有根→IM-006真实lease/scalar类型缺失→紧密新descriptor/冻结UInt32与Int64控制bytes→codec→IM-066精确ObjectRef→Map冻结CG path→H job准入/pipe→回读原slot/误差→真实drain。每步有公开入口、按原单位/domain编解码、budget预检、错误及恢复；不同module名同类型用alias，无暗调用AsunImage内部/产品Schema。新配方不改HF-A/B/P/Q原向量，bridge新tight输入有新身份。第二视角逆向：压缩小decoded大→raw拒绝；同Id换scope→两表比对；Frame.CopyRow不能还padding→只允许新tight；real量化靠近边界→集合一致或拒；job请求kill未退出→pending；lease Release未确认/Host finally抛错→业务与清理分轴/原根；file/parenthash无可信发布→不取得质量事实。修入§16–18后再有限复核，不无限扩大研究。

| ID（新增工程验证计划，未运行） | 具体输入/唯一断言 |
|---|---|
| SD-S01 codec | §18完整577-byte零点PointCloud向量及HF-A/B/P/Q，字段顺序/hash/再编码一致；父ordinal>2^53保持Int64；空Layers/旧scope/unknown enum/尾字节拒绝，不仅比较hash |
| SD-S02 codec bounds | payloadLength长1/短1/uint.MaxValue、集合count过quota、截断nullable/string、hash错、非ASCII、Carrier深不等；分配前拒绝，Metadata=null，禁止半解码 |
| SD-S03 FrameSource | scalar plane紧密边界/跨行slice、独立Frozen State/Origin/SourceIndex、复制后值域/全hash；缺高度/Unsupported UInt32 plane/native DisplayOnly/单位错拒绝；A关闭不释放Blease |
| SD-S04 StoredSource | 同obj hash异内容/元数据漂移、stream每次1byte后0、离线/撤权、读完Release Unknown/异常带lease；读量和补读有限，所有task真退出/Released才完成session，不更新head |
| SD-S05 Coordinates | HF非零crop、Pixel方向/Convention不符、>2^53父像素、NoCovariance Required、Graph sameId异hash、Grid非平面模型、取消后迟到Completed；合法保持原物理值，非法按下文明确码拒绝/迟到不采用 |
| SD-S06 root | factory后第一次Close前抛错、所有work槽满/cleanup槽独立、同步启动异常、Close再取消、原Task晚到/清理错/接管未确认；不遗弃owner/不早退槽、不覆盖业务错误 |

S05期望：合法沿HF-A同物理值；Convention→Frame、非平面Grid→Capability、无法精确父像素→Frame、asset hash错→Conflict，Required协方差→Capability；迟到批不采用，保原CG实例/identity至Drain确认。SD-S01–06加H03–06写在本模块指定验证工程suite中，不创建新过程脚本。Core BCL Exe新增`--suite metadata --consumer both`（Replay/Audit独立子进程）、Adapters验证Exe `tests/Modules/surface-data/Asun.Modules.SurfaceData.Adapters.Tests/Asun.Modules.SurfaceData.Adapters.Tests.csproj --suite adapters --consumer both`、ImageLib验证Exe同根 `Asun.Modules.SurfaceData.ImageLib.Tests/Asun.Modules.SurfaceData.ImageLib.Tests.csproj --suite native --consumer both`；实际命令均 `dotnet build <对应csproj> -c Release` 后 `dotnet run --project <验证csproj> -c Release -- <上述参数>`。均net10.0-windows Exe（metadata为原net10.0 Exe）、只真实引用被测包/公开上游/BCL；10/120/180s真wall监督及必需未完/skip非零沿§10，不新加同义标准。H03/04期待真实native正确拒绝，不以Python浮点或simulator替运行。

新增Benchmark测点：元数据预检/计长/encode/hash/decode/Validate，small零点合法PointCloud/nominal HF+mesh/max层/field/Origin/贡献方法/fan-in及超quota坏长度；Frame单行scratch/full verification/lease账，Stored开窄scope/补短读/full hash/释放，CG Submit/Map/Query/drain；H冷新进程启动/二进制hash/job准入/pin/real量化/对象/筛选/pipe/clear/exit峰值。至少单Host、双Host、上限、慢流/迟到/清理Unknown/内存拒绝/取消混合；输入bytes/version/hash及n/预热/最低有效n明确。正确性门为全部必需断言零差异（H误差≤显式Profile且slot完全一致），资源门为逻辑账未越限/0未归还/OS commit未越job；latency目标仅来自用户采用的Profile，缺目标NotEvaluated而非软件缺算法或造PASS。极大数据不声称整云默认驻留，Core chunk可读而native全幅容不下明确拒绝；LOD由IM-060以其有界路线显示，不能暗降采样满足H。

### 19.3 仅剩外部输入与实际运行资格

| 项/精确Owner | 仅影响/必须提供或执行 |
|---|---|
| 数据Producer/IM-032/IM-034/采集Owner | 正确Height/XYZ/已有mesh/state/Origin、版本/hash、实际支持/方法权重证据；本模块协议不能认证算法真值。缺它只阻相应真实源/派生支持 |
| IM-006 allocation Owner、IM-066对象/权限/保留Owner | 真实服务实例/lease/已发布ObjectRef、raw format注册/可信manifest binding、有效context。桥软件已定；真实IO/release/撤权/损坏验证未运行 |
| IM-007/标定资产Owner | Graph/Frame/ExplicitPath/Policy真实hash、Pixel方向/单位/有效域、可用平面XY资产及资格；误差/协方差/线性化证据仍原Owner。本桥不自行标定 |
| IM-060/产品Host | Viewport Adapter/实际WPF+DevExpress/HALCON呈现、DisplayLease/LOD/pick/probe/support权限/代次，真实1920×1080/三语/UIA/关闭/性能；本模块只读数据资格不等显示或计量通过 |
| 本模块实现Owner（本永久会话） | Core codec/Adapters/ImageLib/Worker真实build/run、公共API实际引用编译、pin/domain/误差/IPC/job ABI/取消清理/升级回退、Golden及性能/长稳；属于未执行工作，**不是留待设计的内部决定** |
| 发布/部署Owner（使用本模块的Host） | 准确worker/existing AsunImage二进制hash、Windows x64 job可用性、有限commit/CPU/pipe/执行Profile；物理MaxCoordinateRoundTripError/时延目标由用途Owner批准；不足硬拒绝，不放宽门禁 |
| 计量/客户质量/设备Owner | 相应物理精度/MSA/HIL/FAT/SAT/生产采用。本模块无质量放行、设备命令和用户权限赋权，C5/Completed/Complete不替代它们 |

本轮只完善唯一指导，完成结论不以文档数量/合成算例/原会话completed冒充模块运行验收。C1–C5原接收保持；所有新增规格由本原会话自审与文档验证收口，总控只接收状态。达到本范围设计准则即停，不自动开始实现或扩大标准文件/UI/视觉算法范围。

本轮实际文档验证（不运行产品）：按字段独立重建并反向解析§18全部577-byte信封，payload529、全信封hash和trailer一致；新增H float数值示例中1e9mm+1e-3mm量化回读误差约0.0010000467mm，阈值0拒绝；0.1mm作下界的real值略小于原m边界，验证了H04集合不一致拒绝的必要性。HF父像素(4,8)/(4,9)平面映射及新增有限CPU/worker预算算术一致。C1–C4四行和§15.2–15.9已接收规格SHA256与本轮前相同，未重算旧向量。新增公开声明无重名、围栏成对、本地链接存在，三个新HALCON页hash与§17记录一致；错误投影/参数及工厂名已按上游当前公开声明交叉核对。两轮有限自审只覆盖新增缺口及全范围导航，不替真实C#构建/HALCON/Windows Job/Source/CG/存储/WPF/性能或现场验收。

### 19.4 本轮兼容影响与消费者协调

兼容比较基线为本轮前的0.5.1-prep及已接收C1–C5规格，不对更旧候选或尚未建立证据的二进制作兼容保证。新增软件设计闭合不表示消费者已经接入；本轮没有修改其它模块、产品配置或持久化对象。

| 公开输入/输出或语义 | 相对基线的影响 | 需同步的消费者/Owner |
|---|---|---|
| C1–C4 API v0.4、C5 Contribution v0.1 | 原公开签名、字段/单位/ByteOrder、源ordinal与Int64父索引、有效域/state/Origin、控制buffer编码及session读取/取消/关闭契约保持；没有把原值转成native量化值 | 只消费这些契约的Viewport、reconstruction-3d、surface-features-3d、metrology无需因本版修改其DTO、贡献算法或源索引映射。Viewport §15.2.5/§15.3现有C1–C5桥继续适用；其引用0.5.1-prep仍对应未变的API范围 |
| §16 Source/Contribution/Coordinates factory与绑定值 | 新增可选Adapters公开入口，不替换原注入端口。采用Frame桥得到新紧密快照身份；不把它伪装原padding快照。Stored两scope查找表、精确ObjectRef、CG Graph/Policy/Path及有限根均显式提供；单位仍沿原Core/CG，不猜深度 | 采用新桥的Replay/Audit/产品Host需更新组合根、绑定表、预算及恢复接线。image-frame、coordinate-geometry、storage-database仍提供其原公开服务，不需修改上游Core接口；真实资产/服务与Owner输入按§19.3协调 |
| `SurfacePortException(SurfaceError)` | 新增Core公开异常载体，C2/C5/坐标处理保留端口的精确错误，不改变成功输出或终态/释放权。此前落到通用异常码的此类失败将得到更准确的既有Code/Path/Ordinal，错误投影属于实现行为补充 | 新Adapters采用该载体；采用者检查诊断/恢复分支，不能把任意非Internal误当已Released。原成功调用消费者无需改签名；旧自定义端口仍可沿原通用异常规则使用 |
| §17三参数`SurfaceImageLibFactory.Create`与RuntimeBinding | 新增重载；旧两参数签名保留，但非空native请求明确BudgetUnavailable，属于**行为兼容变化**。真实H需显式worker/AsunImage hash、commit/wire预算与Accuracy；无隐式部署发现 | 所有实际调用本模块H的Host及本模块ImageLib验证工程须迁到三参数装配，并由部署Owner发布worker、用途Owner批准精度Profile。Viewport自己的HALCON呈现backend不是本Filter消费者，不因本版强制迁移其路线 |
| H输入/输出精度与筛选 | H1 float32、H2单位往返都受显式原单位误差上限；H3集合必须与CPU原坐标闭区间一致，偏差拒绝。Positions返回CPU原值，native值只验证；这是**精度/结果与失败行为的明确变化**，不能描述成无影响补字 | 采用本H的Replay/诊断/计量输入Host需更新期望结果及H03–06断言，核用途Profile；不自动修改计量公差、已有重建/特征算法或C1–C5数据。误差上限0的拒绝与边界Integrity均不可由Host静默放宽 |
| §18 metadata codec及两个format validators | 新增完整`surface-metadata/1` schema与`surface-raw-buffer/1`注册。manifest enum Int32LE不是C5原控制列宽度；原buffer原字节/单位不变。此前无已冻结完整codec，不能承诺兼容未知旧manifest；未知版本拒绝，保旧包/旧快照按§18.3回退，不自动迁写 | 采用元数据无损重开的Replay/Audit Host，以及选择保存该格式的inspection-evidence/产品发布Host，须协调格式VersionRef/hash注册、有界读、精确scope表与回退包。storage-database格式注册Owner接收新validator配置，原存储API不变；未采用此codec的既有消费者无需修改持久化格式 |
| Owner/生命周期与权限 | Source服务/TimeProvider仍借用，lease/原Task按原session真实退出归还；新增worker/job/pipe由本adapter及Host有限根持有到退出。取消请求不等释放，codec不恢复旧运行对象。数据Producer、坐标资产、存储发布、Viewport显示及质量/设备事实Owner均不变 | 新装配Host同步根账、独立cleanup、部署与关闭验证；不把进程终止当上游lease释放，不把Decode/Completed/C5当质量放行。其它模块无新增事实写入权或设备权限 |

本轮在`docs`、`src`、`tests`排除本模块后的定向检索，未检出对`SurfaceImageLibFactory`、`ISurfaceImageLibPort`、`SurfaceAdaptersFactory`或`SurfaceMetadataCodec`的既有直接引用；这只说明当前可查范围未发现调用，不能证明外部部署没有消费者。Viewport/metrology及其它已列模块的原Core消费关系已按唯一指导定向核对，Replay/Audit是本指导的新codec规划消费者；inspection-evidence仅在选择采用此格式时协调，不声称其已经依赖该codec。若开工发现未登记的真实H调用或旧持久化包，由其Host Owner按本节显式迁移并验证；本轮无须也无权代改其它模块指导或代码。

