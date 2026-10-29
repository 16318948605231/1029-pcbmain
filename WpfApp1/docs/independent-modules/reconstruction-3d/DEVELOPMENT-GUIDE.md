# 三维重建与多方向融合独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`Core, Simulator`

- 模块 ID：`IM-032`
- 既有来源：`PKG-028_Reconstruction`
- 模块键：`reconstruction-3d`
- 版本：`0.2.9-prep`（2026-10-11；仅同步viewport0.3.4的WPF Assembly Contract v0.2实际消费；0.2.8完整范围结论及原接收保持，不代表实现）
- 状态：整体 `DesignReview/Prep`；Core 与可发布 Simulator 切片分别为 `ModuleCoreImplementationReady`（2026-10-10 主控六项内容接收，仅规格准备）
- Core 接收范围：值校验、分桶等权融合、参数建议、执行协调及已冻结端口下的测试 stub/TestHost；不包括可发布 Simulator、HALCON/Adapter、WPF、平台集成或现场资格。
- Simulator 独立接收范围：发布模拟包的明示值、端口、有限脚本、clock/gate控制、资源Owner及两个无UI Host；不授真实算法、HALCON/标定、WPF、产品集成或现场资格。实际工程、编译、运行与性能验证均未执行。
- 角色/诊断增量：§4.2.2/4.4.1/13.6.1/13.7.1已于2026-10-11由主控内容接收，沿Core/Simulator六项软件规格为ModuleCoreImplementationReady；主控独立重建D01/D02八份1185/1189/1181/841-byte层编码，全部length/hash一致。实际HALCON/运行资格未验。
- 本轮接收切片：§7.6无标定decode-only与Both命名对应交接，R3D-Decode-C1/S1为`ModuleCoreImplementationReady`（仅规格准备）；R3D-Decode-A1固定HALCON路线/公开工厂内容限定接收，真实native/Golden/Envelope/消费者封存和运行资格仍`PreparationIncomplete / NotReady`。原重建签名、Vertical诊断和0.2.5已接收范围保持。
- 本轮Joint消费增量已获主控限定内容接收：§8.1.1–4/§11/A.1复用CAL0.3.2-prep §7.4.6B唯一资格技术桥；不改Core/Simulator API、旧fixture/Golden或接收状态，真实资格Owner/native/公开程序集编译/性能/物理仍`PreparationIncomplete / NotReady`。
- 技术基线：C# / .NET 10；视觉执行通过 `ImageLibDotNet` 公共接口；目标 HALCON 26.05
- 规划消费者：结构光工具、3D AOI、表面实验工具
- 本文是独立模块的唯一开发指导。它定义能力边界和接入语义，不表示接口已获 Contract/Schema/Owner 正式采纳，也不表示已实现、完成计量资格或生产验收。

## 1. 目的与边界

### 1.1 模块职责

模块把已冻结的三维输入转换为带来源和质量状态的三维结果：

1. 校验输入序列、方向、标定、坐标系、单位和版本。
2. 对结构光图案序列执行解码和表面重建。
3. 对已资格化的多视图输入执行立体表面重建。
4. 接收已经提供高度/点云的传感器结果，做统一的类型、单位和质量适配；空间变换只消费 IM-033 已发布快照。
5. 对多个方向的结果应用 IM-033 `registration-3d` 已发布的不可变变换/标定快照一次，随后执行支持域核验、冲突分类和可追溯融合。
6. 输出高度场/点云的无句柄不可变值结果、有效域、缺失域、冲突域、不确定度（只有输入或算法提供可靠值时）和来源索引。`ObjectModel3D` 是适配器内部载体或上游来源类别，公开输出固定为 `SurfaceResult + SurfaceGeometry`，不发布 native 模型/指针。
7. 提供取消、超时、排空、诊断和可回放所需的操作状态。

### 1.2 明确禁止

- 不识别 PCB、PCBA、SPI、AOI、点胶、涂覆或任何其它制程目标，不解释工艺意图。
- 不持有产品页面、ViewModel、产品私表、工单/配方发布、质量规则、最终 PASS/FAIL、复判、放行或返修状态。
- 不控制相机、投影器、灯光、运动、PLC、触发或其它设备；设备采集由上游适配器和宿主负责。
- 不把缺失、冲突、未知、不可观测区域填成零值或合格值；不以最高分方向静默覆盖其它方向。
- 不估计、拟合、优化、资格化或发布方向变换；不读取未发布的候选变换，不重复应用已发布变换。
- 不在核心层依赖隐藏窗口、WPF Dispatcher、静态可变单例或特定产品启动顺序。
- 不把 HALCON 原生句柄暴露给产品领域；句柄只存在于适配器/执行层并由操作租约持有。
- 不猜测 HALCON 或 `ImageLibDotNet` 未确认的签名、参数、线程属性或内存语义。

调用方负责调用顺序、目标关联、业务适用性、质量解释、事实提交、设备副作用和最终处置。IM-033 `registration-3d` 是方向变换的唯一 Owner，负责估计、资格化和发布不可变变换快照；IM-032 只消费快照，拒绝候选/未发布变换，按快照目标坐标应用一次，不重新估计、不重新资格化、不重复应用、不发布变换。模块只返回本模块拥有的重建/融合事实。

### 1.3 本模块实现文件绑定

首个纯 Core 切片绑定仓库相对路径 `src/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.Core/Asun.Modules.Reconstruction3D.Core.csproj`、测试工程 `tests/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.Core.Tests/Asun.Modules.Reconstruction3D.Core.Tests.csproj`，根命名空间固定为 `Asun.Modules.Reconstruction3D`。工程尚未创建；本指导只允许该 Core 与测试工程路径写入。HALCON/AsunImage 适配器、WPF、设备/宿主集成和发布配置须另行准入。禁止修改其他模块、产品项目、AsunImage 内部或只读参考快照。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Reconstruction3D.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Modules.Reconstruction3D.Wpf` 可引用 WPF/DevExpress，Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。§1.3 首片（纯托管 Core）在无 WPF、无 HALCON runtime、无 AsunImage 程序集的宿主中即可完整运行。

**Blazor/Web 宿主中的重建结果展示**：Web 端需要"展示高度场/点云分布、缺失域、冲突域与不确定度"时，服务端调用本模块 Core/Simulator 取得不可变 `SurfaceResult + SurfaceGeometry` 值结果，再按 tile 粒度或采样点投影到浏览器。约束：
- 浏览器端只渲染标记与热图，不重建高度场、不自行插值缺失域、不重新执行解码
- §1.2 的"不把缺失/冲突/未知区域填成零值或合格值"在 Web 投影中同样成立：前端不得以"空白区域"代替明确的缺失域掩码
- 重建质量证据（来源索引、方向索引、不确定度）随结果一起投影，不在浏览器端二次计算

**AI 推理 Tiling 适配**：本模块的高度场/点云可作为 `ai-inference` 异常检测（anomalib PatchCore）的输入来源，但本模块不参与推理分块编排。适配约束：
- 推理所需的高度场 tile 由 `image-frame` 按已发布的 `SurfaceGeometry` 平面裁切，本模块不实现 `RequestTileAsync`，不持有推理 tile 租约
- 三态仲裁（`ai-inference` §1A）判定本模块输出的高度场"异常"时，本模块的重建事实不被覆写；仲裁只作观察层

**HALCON 备选交叉验证适用性（重建链）**：本模块是 3D 视觉链中双跑 CI 的**点云生成落点**。约束：
- 结构光解码与表面重建（`reconstruct_surface_stereo`、`xyz_to_object_model_3d`）在 HALCON 路线与一条纯托管高度场参照路线上按**同一 Golden 数据集**双跑：输出点云的点数、XYZ 坐标（允许容差内不同）、有效域、缺失域与冲突域标志逐项比对，差值超容差即 CI 失败
- **已知的必然差异，不得抹平**：
  - 结构光解码（相位展开、条纹频率方案）在 HALCON 26.05 `reconstruct_surface_stereo` 中是黑盒，托管参照不可能逐像素复现；双跑门禁只对**有效域掩码结构**（有效点数/缺失分区/冲突分区计数）设强门禁，不对单点高度值设严格容差门禁
  - 深度排序和方向融合的不确定度传播是实现相关的，标为仅诊断
- **Open3D oracle 在本模块的定位**：固定 commit `b6c5e196384ad71e75b6e6f9c5da22d046221f1d` 的 `PointCloud.cpp` 的 `VoxelDownSample`/`RemoveStatisticalOutliers`/`RemoveRadiusOutliers`（见 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)）仅用于验证**体素下采样索引保留**和**离群过滤后点数**语义，支撑"下采样后原始索引可追溯"这条契约不变量。Open3D 不引入生产依赖，仅作独立语义参照
- HALCON 仍是生产路线；托管参照只作交叉验证与降级保险，不作发布依据。实际读取 SHA-256（`PointCloud.cpp` LF 归一化）= `9d31ff094145e2be55d17b18da1ada84039522fc7878914c347c118ec5fb1ee1`；`PointCloudSegmentation.cpp`（供关联模块参考）= `44487a05b6f3b70a4da2a856220638b60e4c483350572d098fc1ea4c073d7751`

## 2. 依赖、权威与数据流

### 2.1 依赖方向

```text
结构光工具 / 3D AOI / 表面实验工具
          │ 公开契约、取消令牌、诊断接收器
         ▼
IM-032 Reconstruction3D Core
          │ 端口
          ├── IStructuredLightEngineAdapter
          ├── IStereoReconstructionAdapter
          ├── ISurfaceInputAdapter
          ├── Published IM-033 transform/calibration snapshot (read-only)
          └── IFrameSource / ISurfaceInputSource / IReconstructionClock / IReconstructionDiagnostics
          │
          ▼
ImageLibDotNet 公共接口（AsunImage） / HALCON 26.05
```

公共图像帧、相机/投影标定、坐标、表面数据和证据契约分别由IM-006 image-frame、IM-013 calibration-assets、IM-007 coordinate-geometry、IM-031 surface-data、IM-015 inspection-evidence原Owner管理。IM-033唯一负责方向间变换估计、资格和发布。本文只定义IM-032消费快照的语义，不复制第二套变换事实或估计器；storage-database是IM-066技术存储Owner。

### 2.2 一次操作的数据流

```text
RequestReceived
 → Validate（身份/序列/单位/标定/能力/资源）
 → Prepare（只读输入租约、方向计划、预算）
 → DirectionDecode（结构光时，按输入模式可选）
 → DirectionReconstruct（结构光/立体/已给高度适配，成功方向才进入）
 → NormalizeUnits（标定原生单位到 mm，保留原始有效域/来源；不估计变换）
 → ApplyPublishedTransform（仅应用 IM-033 已发布不可变变换快照一次；AlreadyInOutput 分支验证后跳过）
 → Normalize（有效域、输出网格、来源索引；不再次变换或补洞）
 → CrossDirectionCheck（多方向且至少两个成功方向时）
 → Fuse（仅在 FusionPolicy 启用且输入满足条件时）
 → QualitySummary（成功分支）
 → DrainStarted → Drained → ResourcesReleased
 → Completed | Partial | Rejected | Failed | Cancelled | TimedOut
```

每一步都使用同一 `OperationId` 和不可变请求快照。重试计算必须使用新的 `CalculationId`；模块不执行提交事务，不生成或重用调用方的 `CommitId`。

## 3. 调用角色与最小接入

| 角色 | 允许调用 | 不允许交给模块 |
|---|---|---|
| 结构光工具 | 提供完整图案组、实际曝光顺序、标定引用，取得方向结果/融合结果 | 投影器控制、重拍策略、工艺判定 |
| 3D AOI | 提供已冻结的多方向采集或传感器高度，取得可量测候选及覆盖证据 | 目标/缺陷关联、板级聚合、放行 |
| 表面实验工具 | 提供离线帧/点云和实验参数，回放不同融合策略 | 把实验参数直接发布为生产配方 |

宿主最小流程：创建模块实例 → 注入适配器/诊断 → `Validate` → `Reconstruct` 或 `ReconstructAsync` → 消费结果或明确错误 → `DisposeAsync`。宿主必须在停止前等待模块报告 `Drained`，不得直接释放仍被 native 运算使用的输入。

## 4. 模块公开契约（v0.2-prep；平台映射候选）

以下类型是本文唯一模块 API 形状，等待逐切片接收。平台 Contract/Schema 映射、跨模块发布信封与持久化策略仍须公共 Owner 采纳，不得将模块值类型写成第二套平台事实库。命名空间、落点、六项门见附录 A。

### 4.1 基础值类型

```csharp
public readonly record struct LengthMm(double Value);
public readonly record struct CoordinateMm(double Value);
public readonly record struct AngleDeg(double Value);
public readonly record struct Fraction(double Value);
public readonly record struct PixelCount(long Value);
public readonly record struct ByteCount(long Value);
public readonly record struct CoordinateFrameId(string Value);
public readonly record struct RevisionRef(string Id, string Sha256);

public enum LengthUnit
{
    Millimeter
}
```

校验：所有浮点值必须为有限数；`LengthMm.Value > 0`；`CoordinateMm.Value` 可为负；`0 <= Fraction.Value <= 1`；`PixelCount.Value >= 1`；`ByteCount.Value >= 1`；ID 非空、≤128字符、无控制字符，不含未验证的 `latest`；Sha256必须64位十六进制，接纳时规范为小写。集合键/ordinal/camera对应明确且不可重复；不接受未定义枚举值。所有公式/单位转换后的值亦必须有限，Grid两轴端点/半开边界溢出在预检拒绝，不以unchecked cast继续；适配器给出的非有限XYZ为R3D-024。

### 4.2 输入描述

```csharp
public enum ReconstructionMode
{
    StructuredLight,
    Stereo,
    SensorProvidedSurface
}

public enum SampleKind
{
    GrayCode = 0,
    PhaseShift = 1,
    SingleStripe = 2,
    StereoPair = 3,
    HeightField = 4,
    PointCloud = 5,
    ObjectModel3D = 6,
    NormalizationBlack = 7,
    NormalizationWhite = 8,
    GrayCodeInverted = 9
}

public sealed record FrameRef(
    string FrameId,
    RevisionRef Revision,
    SampleKind Kind,
    int Width,
    int Height,
    string PixelFormat,
    DateTimeOffset AcquiredAt,
    int SequenceOrdinal,
    string DirectionId,
    string? PatternId,
    string? ExposureProfileId);

public sealed record DirectionCapture(
    string DirectionId,
    IReadOnlyList<FrameRef> Frames,
    RevisionRef? DirectionCalibration,
    CoordinateFrameId SourceFrame,
    LengthUnit Unit,                   // only Millimeter is enabled in v0.2
    Fraction DeclaredSupport);

public sealed record CalibrationRef(
    RevisionRef Asset,
    CoordinateFrameId CameraFrame,
    CoordinateFrameId WorldFrame,
    string CalibrationKind,
    DateTimeOffset ValidFrom,
    DateTimeOffset? ValidTo);

public sealed record PublishedTransformSetRef(
    RevisionRef PublishedSnapshot,
    bool IsPublished,
    bool IsWithdrawn,
    bool IsHashVerified,
    string CaptureEpoch,
    CoordinateFrameId ToFrame,
    IReadOnlyList<PublishedDirectionTransformRef> Directions);

public sealed record PublishedDirectionTransformRef(
    string DirectionId,
    RevisionRef TransformRevision,
    CoordinateFrameId FromFrame,
    CoordinateFrameId ToFrame,
    RevisionRef CalibrationRevision,
    IReadOnlyList<double> Matrix3x4RowMajor);

public sealed record ReconstructionInput(
    string InputSetId,
    RevisionRef InputRevision,
    ReconstructionMode Mode,
    IReadOnlyList<DirectionCapture> Directions,
    CalibrationRef? Calibration,
    CoordinateFrameId OutputFrame,
    PublishedTransformSetRef? DirectionTransforms,
    ReconstructionExecutionSpec Execution,
    CoordinateMm? ZMin,
    CoordinateMm? ZMax,
    PixelCount MaxPixels);
```

输入硬限制：方向数 `1..16`（默认 `1`）；单方向像素 `1..16,777,216`（默认由帧实际尺寸决定但不得超过上限）；总帧数 `1..256`；`ZMin < ZMax`；同一方向的 `SequenceOrdinal` 不可重复；结构光序列每帧 `PatternId` 必须逐项匹配有序 manifest，曝光配置、attempt/epoch 和方向必须一致且可追溯；宿主 source 必须核对该冻结输入集/外部工件关联和 epoch；不同输入集帧不得混用，模块不持有板/工件业务对象。数值是软件防护默认，不是生产资格阈值。

### 4.2.1 时序、物理模型与快照展开字段

下面类型属于同一模块 API；它们是宿主从已发布资产展开的只读值，不是第二套资产库。`SourceFrame` 表示重建结果的标定世界坐标/传感器原坐标，不能以相机 ID 代替。IM-032 校验适用性与来源完整性，不重新标定或资格化资产。

```csharp
public enum TransformUse { AlreadyInOutput, ApplyPublished }
public enum PatternRoute { HybridVertical, HybridBoth, GrayVertical, SingleStripeVertical }
public enum SurfaceLayout { CameraSamples, PointCloud, OutputGrid }
public sealed record PixelRoi(int Row, int Column, int Width, int Height);
public sealed record GridSpec(int Width, int Height, CoordinateMm X0,
    CoordinateMm Y0, LengthMm StepX, LengthMm StepY,
    LengthMm MaxCenterDistance, LengthMm MaxWithinDirectionSpread);
public sealed record FrameTiming(string FrameId, string AttemptId,
    string CaptureEpoch, string DeviceId, string ClockDomain,
    long ExposureStartNs, long ExposureEndNs, long? PatternStableStartNs,
    long? PatternStableEndNs, RevisionRef ExposureRevision,
    int ExpectedOrdinal, string? ExpectedPatternId);
public sealed record AcquisitionScope(string CaptureEpoch,
    RevisionRef TimingProfile, TimeSpan MaxSequenceSpan,
    TimeSpan MaxStereoSkew, bool SceneStationaryVerified,
    IReadOnlyList<FrameTiming> Frames);
public sealed record DirectionTransformUse(string DirectionId, TransformUse Use,
    int PreviousApplicationCount, RevisionRef? PreviouslyAppliedSnapshot);
public sealed record CalibrationScope(string DirectionId, RevisionRef Asset,
    RevisionRef Qualification, double NativeLengthToMm,
    CoordinateFrameId ReconstructionFrame, int CameraIndex, int ProjectorIndex,
    int CameraWidth, int CameraHeight, int ProjectorWidth, int ProjectorHeight);
public sealed record PatternSpec(RevisionRef Profile, PatternRoute Route,
    int ProjectorWidth, int ProjectorHeight, int MinStripeWidth,
    int? SingleStripeWidth, string Normalization, int MinGrayDifference,
    bool CapturePhaseDiagnostics, IReadOnlyList<string> OrderedPatternIds)
{
    public StructuredLightSequenceSpec? Sequence { get; init; }
    public StructuredLightDiagnosticRequest? Diagnostics { get; init; }
}
public sealed record StereoPairSpec(int FromCamera, int ToCamera,
    int MinDisparity, int MaxDisparity);
public sealed record StereoCameraFrameSpec(string DirectionId,
    int CameraIndex, string FrameId);
public sealed record StereoSpec(RevisionRef Profile,
    IReadOnlyList<StereoPairSpec> Pairs,
    IReadOnlyList<StereoCameraFrameSpec> CameraFrames,
    IReadOnlyList<CoordinateMm> BoundingBox,
    int NumLevels, int MaskWidth, int MaskHeight, double TextureThreshold,
    double ScoreThreshold, LengthMm Resolution, LengthMm SurfaceTolerance,
    LengthMm MinThickness, double Smoothing);
public sealed record ReconstructionExecutionSpec(AcquisitionScope Acquisition,
    IReadOnlyList<CalibrationScope> Calibrations,
    IReadOnlyList<DirectionTransformUse> TransformUses,
    PatternSpec? Pattern, StereoSpec? Stereo, PixelRoi? Roi, GridSpec? Grid,
    RevisionRef? QualificationProfile, ResourceBudget Budget,
    TimeSpan DrainTimeout);
public sealed record ResourceBudget(ByteCount Managed, ByteCount Native,
    ByteCount Result, long MaxPoints, long MaxVoxelCells);
```

- 每帧 timing 必须与 `FrameRef` 一一对应；结构光顺序是生成 manifest 的 ordinal，而非按到达时间/文件名排序。同一方向只有一个 attempt/epoch/曝光 revision；曝光区间必须被对应 pattern 稳定区间完全包含。不同设备的时间差只在同一已同步 `ClockDomain` 比较。缺稳定区间、跨时钟未同步、负时间跨度、总序列超过已发布 `TimingProfile` 上限、场景静止证据缺失，返回 `R3D-021 AcquisitionTimingMismatch`；不靠重排修复运动伪相位。立体各对曝光中点差不超过 `MaxStereoSkew`。传感器表面可以没有图案 timing，但仍须有采集 epoch 和输入 revision。
- `CalibrationScope.Asset` 与每方向标定 revision 相等；资格引用、有效时间、相机/投影器尺寸、模型类型、坐标与本次 ROI 都适用。结构光 index 固定相机 0、投影器 1。HALCON 标定原生长度（常见为 m）只按资产中的有限正 `NativeLengthToMm` 转为 mm，一次完成；不从数值大小猜单位，不用配准矩阵暗含比例。标定过期按曝光时间而非计算时间判断。
- `PatternSpec.OrderedPatternIds` 不能为空，数量与输入精确相等；`MinStructuredLightFrames` 等于该 manifest 数量，非结构光模式为 0。PatternId 每帧不同，要求匹配 manifest，不要求整组 PatternId 相同。生成结构光图案由 IM-011/宿主负责；IM-032 可在隔离模型中调用 `gen_structured_light_pattern` 建立解码布局并核对既有 manifest，不投影、不生成采集任务。
- `TransformUses` 与方向一一对应。`AlreadyInOutput` 要求源坐标等于 `OutputFrame`；previous count 只能是 0（原生目标坐标）或 1（已变换，须带已发布快照 provenance），应用次数不增加。`ApplyPublished` 要求 previous count=0、previous snapshot=null，并消费对应方向已发布矩阵，输出记 count=1；再次请求应用、count>1 或标记矛盾返回 `R3D-020`。不能把“已应用”输入一律拒绝，也不能给 AlreadyInOutput 再乘 identity。IM-033 发布快照由宿主在接纳时提供已验证 hash/发布状态；接纳后固定该快照，撤回只影响新请求/下游接纳，不在在途计算中替换矩阵。
- `PublishedTransformSetRef` 没有单一 FromFrame：每方向可有不同源坐标；目标一致、每方向矩阵为 12 个有限值的 HALCON 3×4 行主序，平移单位 mm。模型语义/资格由 IM-033 发布；IM-032 不做拟合或逆求变换。候选平台映射仍待公共 Owner 采纳。
- 公开 record 中所有列表/字典接纳时深复制；`IReadOnlyList` 本身不等于不可变。冻结后修改调用方数组不能影响在途操作。费用计入 Managed 预算。`Roi` 不改变原图尺寸或坐标原点；不得隐式裁图后套用原标定。

模式必需性固定如下；与模式无关的非 null 参数直接 R3D-001，不默默忽略。结构光必须有 Calibration、每方向 CalibrationScope、PatternSpec、QualificationProfile 可空、Stereo=null；立体必须有 Calibration、每方向 CalibrationScope、StereoSpec、Pattern=null；传感器必须有 SurfaceInputs/Surface 端口，Calibration/Calibrations 可空、Pattern/Stereo=null，输入 XYZ 已是 mm，TransformProvenance.NativeLengthToMm=1。每种模式都必须有 Acquisition（epoch 非空）、TransformUses、Budget、DrainTimeout。FrameTiming 中稳定窗/ExpectedPatternId 仅结构光必填，立体为 null 且仍核对曝光/相机时钟；传感器 Acquisition.Frames 可空。光学模式 Acquisition.Frames 必须与全部 FrameRef 一一对应；MaxSequenceSpan 为正且≤30min，MaxStereoSkew 为非负且≤MaxSequenceSpan，TimingProfile 声明同步时钟和静止证据，不能仅信任 bool 判断现场静止。ZMin/ZMax 可同时 null 或同时有限且有序；拒绝只填一端。Fusion=null 时 Grid 可空，非 null Grid 仍须完整校验。

Stereo.CameraFrames 在每个方向内以 CameraIndex 唯一绑定 FrameId，与该方向全部 StereoPair 帧一一对应；CameraIndex 非负且存在于同一 setup，所有 Pairs 的 From/To 不同、对不重复、按 Profile 顺序冻结且两端都能映射；不以 FrameId、ordinal 或到达顺序猜相机。CalibrationScope.CameraIndex 在立体为首 pair 的 FromCamera，ProjectorIndex/ProjectorWidth/ProjectorHeight 为 -1/0/0；其它相机内参/pose/尺寸由同一只读 setup 资产读取。结构光两端尺寸正且匹配，传感器不造投影器参数。DirectionCalibration 与 CalibrationScope.Asset 在光学模式必填且相等，Calibration.Asset 绑定 setup，全部方向 ReconstructionFrame 必须与 SourceFrame 一致。

传感器 ApplyPublished 分支仍必须提供 DirectionCapture.DirectionCalibration（其原始传感器标定/坐标来源 revision），与该方向已发布变换的 CalibrationRevision 精确相等；不要求 HALCON setup 或非空 CalibrationScope。传感器原生目标坐标且 AlreadyInOutput/count=0 时才可没有标定引用。不得用“传感器不重建”绕过变换作用域。

### 4.2.2 完整结构光角色增量（r3d-sl-sequence-v1）

新增能力是显式 opt-in；ApiVersion仍为`0.2`，旧positional构造器、SampleKind的0..6值、F0/F0-S/ST0及其预期保持。Sequence/Diagnostics默认null，不将旧六帧synthetic向量解释成真实HALCON布局。新版Core/Simulator可消费下列增量；旧部署不能仅因ApiVersion相同接收新字段，宿主须核对实际模块版本和部署能力`r3d-sl-sequence-v1`/`r3d-sl-diagnostics-v1`。缺能力在获取源前R3D-007，未知version为R3D-015；序列化端点拒绝未知字段/枚举，不静默剥离增量。0.2.5的本节及诊断/Simulator增量已由主控沿六项软件规格接收，不表示真实Adapter/运行已验。

```csharp
// Core namespace，System.Collections.Immutable；集合均为非default不可变值。
public enum PatternAxis { None = 0, Vertical = 1, Horizontal = 2 }
public sealed record StructuredLightPatternBinding(string PatternId,
    int SequenceOrdinal, SampleKind Kind, PatternAxis Axis, int RoleOrdinal,
    int? PhaseStepIndex, string GeneratedPatternSha256);
public sealed record StructuredLightSequenceSpec(string Version,
    RevisionRef ManifestRevision,
    System.Collections.Immutable.ImmutableArray<StructuredLightPatternBinding> Patterns);
```

Patterns数量1..256，逐项ordinal从0连续且与OrderedPatternIds及每方向FrameRef.Kind/PatternId/SequenceOrdinal精确相等；不从文件名、曝光、亮度或到达次序猜角色。RoleOrdinal是同一axis同一角色组的0起始序号；GrayCodeInverted与对应GrayCode共用RoleOrdinal，每对恰一原图一反图。启用Phase的route每axis恰四帧，RoleOrdinal/PhaseStepIndex均为0..3且相等；其生成相位顺序由原manifest固定，不能假定index0必为0 rad。非Phase的PhaseStepIndex=null。NormalizationBlack/White各RoleOrdinal=0、Axis=None；Gray/GrayInverted/Phase/SingleStripe的axis必须适用route，StereoPair/表面角色在此拒绝R3D-001。None是图案axis，FrameRef.DirectionId仍是原光学采集方向，不写成None。HybridBoth的V/H不是两个物理采集方向。

global要求整组恰一Black和一White（供全部axis使用），且没有GrayCodeInverted；inverted_pattern不注入全局黑白，要求每个GrayCode有紧随的同axis/RoleOrdinal反图，二者均进入decoder，不能只保留原图。每个route启用的axis至少一个GrayCode；GrayVertical禁止Phase/SingleStripe；HybridVertical/Both禁止SingleStripe；SingleStripeVertical必须有SingleStripe、Gray和四步Phase。各role组ordinal连续；Gray顺序由粗到细，SingleStripe顺序为原生成平移序；这些是核对条件，不授权重排。缺必需成员R3D-003，同ordinal/帧重复沿原R3D-004，角色或绑定不符R3D-002，非法字段R3D-001。黑白帧仍有独立真实采集Bytes/revision/timing/PatternId，不用人工常数图替代相机曝光，不作为Gray位或单独产生XYZ。新增7/8/9角色仅在StructuredLight且Sequence非null时接收；其它模式或未opt-in为R3D-001，不能扩展立体或表面语义。

GeneratedPatternSha256是**投影器生成图**的原W×H、Mono8逐行无padding字节SHA256（非相机采集FrameRef.Revision）；ManifestRevision由原生成Owner提供并校验，不由IM-032发布新manifest。真实Adapter在独占模型设置同PatternSpec后gen_structured_light_pattern，逐对象按原顺序核对数量、尺寸和该hash；Black/White生成图分别须全0/255，互补Gray逐像素和255。投影器生成图checked(W×H)也限16,777,216，全部图案/native/核对成本先计费，不能只按相机MaxPixels预留。全部核对通过才把相机帧按原ordinal concat给decode；不推断Both对象排列、不按role重新分组拼接。生成对象和核对buffer计入native/managed账本并及时释放。未带Sequence的旧请求仍按旧Core/stub规格校验；真实Adapter仅接受明确完整Sequence，缺项R3D-007/SequenceMetadataRequired，不以旧F0证明真实布局。这项软件合同不依赖共同标定新DTO；真正重建仍沿已有CalibrationRef/Scope消费边界。

### 4.3 参数与策略

```csharp
public sealed record ReconstructionParameters(
    string AlgorithmProfileId,
    RevisionRef AlgorithmProfileRevision,
    int MinStructuredLightFrames,
    Fraction? MinValidFraction,
    Fraction? MaxInvalidFraction,
    LengthMm? MaxDirectionDisagreementMm,
    int MaxDirections,
    ByteCount MaxNativeBytes,
    TimeSpan Timeout,
    PartialResultPolicy PartialResult);

public enum PartialResultPolicy
{
    RejectOperation,
    KeepSuccessfulDirections
}

public sealed record FusionPolicy(
    string PolicyId,
    RevisionRef PolicyRevision,
    FusionMethod Method,              // only EqualSupported in v0.2
    int MinContributingDirections);   // required: 2..MaxDirections

public enum FusionMethod { EqualSupported }
```

参数校验规则：

- `MinStructuredLightFrames` 属于 PatternProfile，必须显式提供；无 PatternProfile 时拒绝结构光执行，不用代码默认值绕过缺帧检查。结构光范围 `1..256`，其它模式为 0。
- MaxDirections必须1..16且不少于实际方向数，DeclaredSupport仅上游声明且在0..1，不能代替实际掩膜计算。AlgorithmProfileId必须等于AlgorithmProfileRevision.Id；版本/hash有效性和其他Profile引用在接纳时冻结。
- `MinValidFraction`、`MaxInvalidFraction` 无默认值，须来自已发布、带 hash 的消费者 Qualification/Geometry Profile，并满足 `MinValidFraction + MaxInvalidFraction == 1`（按 double 误差≤1e-12；同一有效/无效分母）。缺失时允许返回各方向原始候选及可观测掩膜，但禁止输出依赖该门槛的资格/覆盖结论或融合结果，返回 `R3D-017 QualificationProfileMissing`。
- `MaxDirectionDisagreementMm` 无默认值，须由同一 Qualification/Geometry Profile 显式提供且大于 0；单位为毫米，不接受像素或米的隐式转换。缺失时拒绝方向差异判断及融合用途。
- 首发融合不含体素分辨率、闭面厚度/容差或平滑参数；这些属于 HALCON `fuse_object_model_3d` 的闭面重建语义，不得进入托管高度/点融合契约。
- `Timeout` 必须显式提供，范围 `100 ms..30 min`；`default(TimeSpan)`、零、负值均为 `R3D-001 InvalidRequest`，不得在构造器或模块内补默认值。
- `ReconstructionRequest.Deadline` 与 `Parameters.Timeout` 同时存在时按 §5.1.1 取更早的单调截止点；`Deadline` 不能晚于宿主的整体操作截止点。到期只产生一次 `TimedOut`，不由模块自动延长。
- `MaxNativeBytes` 是资源防护预算，不是资格/几何参数；宿主显式提供，范围 `64 MiB..8 GiB`。必须显式提供（宿主可预填 `2 GiB` 防护建议），缺失直接拒绝，超限在分配前返回 `ResourceLimitExceeded`。该上限不能推出算法资格、精度或性能通过。
- 空方向、空帧列表、零像素或只有非法帧描述在 `Validate` 阶段拒绝，不以 `Partial` 掩盖空输入。`PartialResultPolicy.KeepSuccessfulDirections` 只允许“至少一个方向完成且每个失败方向有明确错误”的部分结果，不能把零个成功方向包装为成功。
- 任何资格/几何阈值、融合策略或回退路线都必须来自带 hash 的已发布 Profile；资源防护和执行 Deadline 来自宿主请求或明示软件安全上限。不得用资源/超时默认值代替 Qualification Profile，也不得由它们宣称资格或性能通过。
- 首发 `FusionMethod` 仅含 `EqualSupported`；`MinContributingDirections` 必须由 Profile 显式提供，在 `2..MaxDirections` 内且不得大于本次请求的方向数。融合只对共同支持、满足方向差异门且贡献方向数达到该下限的元素生成等权结果；单方向支持留在 per-direction 输出，缺失和冲突元素无数值替代，不插值、不补洞。执行阶段若失败/不合格方向使可参与方向少于该下限，保留每方向结果、返回 `Fused=null` 和有类型的 `FusionIssue`，不得降低门槛或以部分方向凑数。

`MaxNativeBytes` 与 `Execution.Budget.Native` 必须一致，不允许两套预算。Managed/Result/Native 均须显式正预算，范围 64 MiB..8 GiB，建议宿主初始 native=2 GiB 仅作软件防护；`MaxPoints` 为 1..16,777,216，`MaxVoxelCells` 为 1..Int64.MaxValue，仍受字节预算约束。无调用方预算直接拒绝。资格缺失以 nullable 字段表达，不能填零；仅输出 Unverified 候选，任何需要门槛的融合不执行。

### 4.4 输出描述

```csharp
public enum QualityState
{
    QualifiedCandidate,
    Unverified,
    Partial,
    Conflict,
    NotObservable,
    NotQualified,
    Invalid
}

public sealed record SurfaceResult(
    string ResultId,
    string CalculationId,
    ReconstructionMode Mode,
    CoordinateFrameId CoordinateFrame,
    LengthUnit Unit,                   // Millimeter
    int Width,
    int Height,
    IReadOnlyList<CoordinateMm?> ZValues,
    IReadOnlyList<bool> ValidMask,
    IReadOnlyList<byte> ValidityReason,
    IReadOnlyList<double?>? UncertaintyMm,
    IReadOnlyList<string> SourceFrameIds,
    IReadOnlyList<string> SourceDirectionIds,
    IReadOnlyList<int> ContributionCount,
    QualityState Quality,
    Fraction ValidFraction,
    Fraction ConflictFraction,
    RevisionRef AlgorithmRevision,
    IReadOnlyList<RevisionRef> Provenance);

public sealed record ReconstructionResult(
    string OperationId,
    IReadOnlyList<SurfaceResult> PerDirection,
    IReadOnlyList<DirectionIssue> DirectionIssues,
    SurfaceResult? Fused,
    FusionIssue? FusionIssue,
    QualityState OverallQuality,
    IReadOnlyList<string> Warnings,
    TimeSpan Elapsed,
    IReadOnlyDictionary<string, TimeSpan> StageDurations,
    IReadOnlyDictionary<string, long> ResourcePeaks,
    IReadOnlyList<SurfaceGeometry> Geometry)
{
    public System.Collections.Immutable.ImmutableArray<StructuredLightDiagnosticLayer>
        DiagnosticLayers { get; init; }
        = System.Collections.Immutable.ImmutableArray<StructuredLightDiagnosticLayer>.Empty;
}

public sealed record DirectionIssue(
    string DirectionId,
    string ErrorCode,
    bool Recoverable,
    string ReasonKey);

public enum FusionIssueCode
{
    InsufficientCompletedDirections,
    NoElementMetContributionMinimum
}

public sealed record FusionIssue(
    FusionIssueCode Code,
    int CompletedDirections,
    int RequiredDirections);
```

`ValidMask=false` 必须有原因码且 Z=null；Z 的类型是可正、负、零的 `CoordinateMm`，不能使用仅允许正数的 `LengthMm`。`ValidityReason` 按下表固定字节值，不由适配器自由造枚举：Valid=0、NoCorrespondence=1、Saturated=2、Occluded=3、OutOfRange=4、CalibrationGap=5、DirectionConflict=6、InsufficientContributingDirections=7、Interpolated=8、WeakModulation=9、AmbiguousDepth=10、DecodeRejected=11。首发不插值，8 仅用于标识上游插值候选，不计入真实贡献。不能因无对应就声称 Occluded；只有已知可见性/上游原因支持才用 3，否则用 1。

```csharp
public sealed record StereoSampleSource(int PairOrdinal, int CameraIndex,
    double RectifiedRow, double RectifiedColumn,
    double OriginalRow, double OriginalColumn);
public sealed record SampleSource(string DirectionId, string FrameId,
    int SampleIndex, int? ImageRow, int? ImageColumn,
    StereoSampleSource? Stereo);
public sealed record TransformProvenance(string DirectionId, TransformUse Use,
    RevisionRef? Snapshot, int ApplicationCount, double NativeLengthToMm);
public sealed record SurfaceGeometry(string ResultId, SurfaceLayout Layout,
    GridSpec? Grid, IReadOnlyList<CoordinateMm?> XValues,
    IReadOnlyList<CoordinateMm?> YValues, IReadOnlyList<int> SourceOffsets,
    IReadOnlyList<SampleSource> Sources, IReadOnlyList<int> ConflictPairCount,
    IReadOnlyList<TransformProvenance> Transforms);
```

`Geometry` 与每个 PerDirection/Fused 按 ResultId 一一对应，N=checked(Width×Height)，XYZ/mask/reason/contribution/conflict 数组均长 N。CameraSamples 保留相机映射的原图 Width/Height 和显式 XYZ；PointCloud 使用 Width=N、Height=1、Grid=null，不宣称它是规则高度图。OutputGrid 必须有 GridSpec。多层点云仍可输出；投影到单值网格出现重叠深度时不得挑最高/最低层。无效元素 XYZ 均 null；有效元素必须有限，ZMin/ZMax（含端点）在输出坐标检查；合法 Z=0 不表示空点。

来源使用 CSR：SourceOffsets 长 N+1、首项 0、单调不减、末项=Sources.Count。每元素片段保留完整输入 FrameId/方向/原索引；ContributionCount 是不同有效方向数，不是帧数/点数；ConflictPairCount 是逐对超门槛的方向对数。SourceFrameIds/SourceDirectionIds 是由 CSR 推导的唯一有序摘要，不能代替逐元素来源。ValidFraction 分母为冻结请求有效 ROI/网格域大小；失败/遮挡方向不能通过缩小分母提高覆盖。没有请求域的点云只报告自身保留率，不冒充覆盖率。

结构光每个有效 camera pixel 的来源包含本次完整解码 manifest 的 FrameId/同一原图 row/column；SampleIndex=checked(row*Width+column)，Stereo=null。立体按 §7.2 构造两个相机的子像素射线来源：ImageRow/ImageColumn=null，Stereo 非 null，不能将整流像素索引冒充原图整数像素。传感器整数采样可有 ImageRow/ImageColumn；纯点云二者 null，SampleIndex 仍须可定位输入不可变快照。无效格可保留冲突/候选来源，不能让这些来源增加 ContributionCount；无效元素 ContributionCount=0、不确定度=null。XYZ/domain/CSR 不一致为 R3D-024。

融合请求未达到方向完成数门槛时不创建融合表面，保留每方向产物并返回 `FusionIssue(InsufficientCompletedDirections, completed, required)`；达到方向数门槛但没有任何元素满足贡献门槛时返回 `FusionIssue(NoElementMetContributionMinimum, completed, required)`。两者 Fused=null；前者 OverallQuality=Partial，后者=NotQualified。若仅部分元素满足门槛，Fused.Quality=Partial，其余元素保持无效。PerDirection 只存成功产生的表面，失败放 DirectionIssues，不造 SurfaceResult 占位。

UncertaintyMm 是每元素输出 Z 的标准不确定度（mm，有限非负），未知=null，数组整体未知=null；不是匹配 score、有效率或制造公差。AlreadyInOutput可保留上游同坐标/同单位且有误差模型revision来源的标量。首发API只有源Z标量，没有完整XYZ/变换协方差：ApplyPublished后及Fused的不确定度一律null，不能假设变换精确或方向独立。未来完整协方差需显式新版API/误差模型后才能采用 `Σout=RΣinRᵀ+Σtransform`、独立等权时 `sqrt(sum(u²))/n`；当前不靠未定义隐藏端口实现。没有真实计量资格不得输出 QualifiedCandidate。

### 4.4.1 无句柄诊断层增量（r3d-sl-diagnostics-v1）

```csharp
public enum StructuredLightDiagnosticKind {
    Correspondence = 0, PatternRegion = 1, Phase = 2, GrayBinary = 3,
    GrayCorrespondence = 4, SingleStripe = 5, Defect = 6
}
public enum DiagnosticUnit {
    ProjectorPixel = 0, Membership = 1, BinaryClass = 2,
    HalconPhaseValue = 3, HalconGrayCorrespondenceValue = 4,
    HalconSingleStripeValue = 5
}
public enum DiagnosticObservation { Observed = 0, NotObservable = 1 }
public enum DiagnosticOrigin { Decoder = 0, Simulator = 1 }
public sealed record StructuredLightDiagnosticRequest(string Version,
    System.Collections.Immutable.ImmutableArray<StructuredLightDiagnosticKind> Layers,
    ByteCount MaxOutputBytes, int MaxLayers, RevisionRef RuntimeRevision);
public sealed record DiagnosticFrameSource(string FrameId, RevisionRef Revision,
    int SequenceOrdinal);
public sealed record StructuredLightDiagnosticLayer(string Version, string LayerId,
    string DirectionId, StructuredLightDiagnosticKind Kind, PatternAxis Axis,
    int ObjectOrdinal, int? GrayRoleOrdinal, int Width, int Height,
    DiagnosticUnit Unit, DiagnosticObservation Observation, DiagnosticOrigin Origin,
    RevisionRef InputRevision, RevisionRef ManifestRevision,
    RevisionRef PatternProfile, RevisionRef AlgorithmRevision,
    RevisionRef RuntimeRevision,
    System.Collections.Immutable.ImmutableArray<DiagnosticFrameSource> SourceFrames,
    System.Collections.Immutable.ImmutableArray<bool> Domain,
    System.Collections.Immutable.ImmutableArray<double?> Values,
    string ContentSha256);
```

PatternSpec.Diagnostics非null时Version精确为`r3d-sl-diagnostics-v1`、Sequence必填且匹配§4.2.2。Layers非default、非空、无重复、按enum递增；枚举未定义R3D-001，不支持组合R3D-007。RuntimeRevision必填，由宿主展开原部署Owner已核定的adapter/算子配置包revision；实际适配器核对自己的部署身份，不匹配R3D-015，不以HALCON版本字符串冒充整个部署包。Simulator为原script的SyntheticRevision。MaxLayers是整个operation硬上限1..1024；MaxOutputBytes显式1..8GiB且不大于Execution.Budget.Managed/Result。所有实际层的预留字节总和和数量在取得源前预检；不得截去末层、返回少层或新建副请求延长deadline。Stereo/传感器不支持这些层。旧Diagnostics=null仍输出DiagnosticLayers.Empty，旧CapturePhaseDiagnostics=true仅保持内部persistence，不因本增量自动增加结果或改旧预算。

| 请求kind / 原HALCON object | 首版支持路线 / 层数（每物理方向） | DTO域、单位与值 |
|---|---|---|
| Correspondence / correspondence_image | HybridVertical、GrayVertical、SingleStripeVertical / 1 | Axis=Vertical，ProjectorPixel；原相机pixel对应投影器column的有限实数；0是合法对应，不是缺失 |
| PatternRegion / pattern_region | 上述三路线 / 1 | Axis=None，Membership；Domain为冻结ROI（无ROI为全图），Values为region内1、ROI内region外0，ROI外null。它表示解码支持，不等于表面可见性或质量通过 |
| Phase / decoded_phase_shift_image | HybridVertical、SingleStripeVertical / 1 | Axis=Vertical，HalconPhaseValue；保留HALCON原相位值，不解包、不转mm；每周期覆盖min_stripe_width投影器pixel |
| GrayBinary / binarized_image | 上述三路线 / 原GrayCode数量，不含互补帧 | Axis=Vertical，BinaryClass；原byte黑0→0、白255→1，其它值R3D-024。GrayRoleOrdinal绑定原GrayCode，ObjectOrdinal从1起按原Gray序；inverted_pattern只交每对第一原图的二值判决 |
| GrayCorrespondence / gray_code_correspondence_image | 上述三路线 / 1 | Axis=Vertical，HalconGrayCorrespondenceValue；保留仅Gray解码的原值，不加phase/single-stripe细化，不当公制高度 |
| SingleStripe / decoded_single_stripe_image | SingleStripeVertical / 1 | Axis=Vertical，HalconSingleStripeValue；仅单条纹原解码值，不当混合correspondence或mm |
| Defect / defect_image | 不支持 / 0 | 仅deflectometry提供；本模块3d_reconstruction在副作用前R3D-007/DiagnosticKindUnsupported |

HybridBoth的重建/完整序列仍支持；本重建接口Diagnostics非null明确R3D-007/DiagnosticAxisLayoutUnsupported。26.05 get原文说明Both返回对象数组，但未承诺方向次序，不能猜第一个一定Vertical或将Horizontal冒成另一个高度。本接口支持域不变；CAL-JC首次标定的Both原始row/column由§7.6独立decode-only入口按已核DirectionMapping交付，不绕进重建结果。GrayVertical请求Phase、非SingleStripe路线请求SingleStripe同为明确NotSupported。四个持久化kind（Phase/GrayBinary/GrayCorrespondence/SingleStripe）要求CapturePhaseDiagnostics=true，false为R3D-001/PersistenceRequired；Correspondence/PatternRegion可false。effective persistence在decode前固定，不在decode后开true读取旧结果。

**域/来源/状态**：每层Width/Height是原相机尺寸，N=checked(W×H)≤16,777,216，Domain/Values均恰N，index=row*W+column；不crop、不降采样、不改原点、不套world变换。除PatternRegion外，Domain为该原object自身HALCON domain与冻结ROI相交，domain外Values=null、域内必须有限；不得用Surface.ValidMask缩小phase域，也不凭相位0/对应0猜域。Phase/Gray/SingleStripe的数值尺度和wrap端点没有由所读get页规定，故本版明确使用上述HALCON原值单位，**不宣称rad/deg、Gray stripe编号或单条纹中心pixel**；需要rad的上游请求须按精确单位拒绝，不能改单位字符串。Correspondence的投影器pixel语义来自decode原文。不同层的domain允许不同；PatternRegion的region与Correspondence域须一致，否则R3D-024。PatternRegion因ROI非空始终Observed（可全0）；其它层domain非空=Observed，否则NotObservable/全null，不补0。Observation仅表示是否有该解码观测，不能改变Surface.Quality或生产判定。

SourceFrames为该方向**完整采集序列**，按ordinal0..n−1，包含Black/White或全部互补帧的实际FrameId/Revision；GrayBinary另用GrayRoleOrdinal明确相关原Gray帧，仍保留完整normalization依赖。InputRevision/ManifestRevision/PatternProfile/AlgorithmRevision逐项等于本次冻结请求，RuntimeRevision精确等于Diagnostics.RuntimeRevision（实际部署Owner引用，Simulator为SyntheticRevision）；Origin必须与执行后端一致。LayerId固定`DirectionId+"/"+Kind数值+"/"+ObjectOrdinal`（数值用InvariantCulture十进制），本派生ID独立上限160字符、无控制字符，其他输入ID仍≤128；scalar及PatternRegion的ObjectOrdinal=1、GrayRoleOrdinal=null，GrayBinary按原Gray顺序ObjectOrdinal=RoleOrdinal+1。层排序固定物理Directions原序、Kind数值、ObjectOrdinal；不存在native对象、窗口、路径、句柄或SDK回调。Values/Domain/SourceFrames均是限额复制的非default ImmutableArray；Core返回对象不会暴露任何builder/可变buffer，调用方保留结果无需持有native或帧lease。

**内容hash唯一编码**：ContentSha256=SHA256以下字节，小写hex，排除ContentSha256自身：ASCII `R3DL`、U16LE=1；按DTO声明顺序写Version、LayerId、DirectionId；Kind/Axis用U8，ObjectOrdinal I32LE，GrayRoleOrdinal先U8有值标志后有值I32LE；Width/Height I32LE，Unit/Observation/Origin U8；五个revision（Input/Manifest/Pattern/Algorithm/Runtime）各按Id、Sha256字符串；SourceFrames先U32LE条数，每项FrameId、Revision.Id/Sha256、SequenceOrdinal I32LE；Domain先U32LE=N后N个U8(0/1)；Values先U32LE=N，每项U8有值标志，有值再IEEE754 binary64 LE。每字符串为严格UTF8、U32LE字节长度+原字节（不BOM、不trim、不Unicode重写），hash字段使用已规范小写64hex，double −0规范为+0，NaN/Infinity拒绝；null不写double。所有数量/长度checked且受本节硬限，不能先无界编码再核预算。ManifestRevision引用由原Owner核验，该内容hash证明本次复制值一致，不代替来源Owner签名/物理资格。

**执行、预算、失败和Owner**：Validate核对请求支持域、序列角色、persistence、层数和保守费用，不运行HALCON。计费每层`checked(512 + 32*N + Σ(max(2*字符串.Length, StrictUtf8ByteCount(字符串))+32) + 512*SourceFrames.Length)`，字符串包含本层全部字符串/revision成员（ContentSha256按64字符计入），包括SourceFrames成员，每个出现处计一次；另512/Source为对象/索引预留。Length按.NET UTF16码元，StrictUtf8ByteCount只计严格UTF8字节、不先生成buffer，非法代理字符在预检R3D-001。总额是DTO/不可变域和值/规范编码缓冲保守上界，不是实测峰值。预检尚无结果hash时按64字符预留，其余来源/revision已从请求展开，不增加新部署端口或资产Owner。预留诊断额外复制至少两份（adapter+Core），与既有surface/来源/输入费用累加分别受Managed/Result约束，同时总单份层额≤MaxOutputBytes；转换/Transform不得再造无预算副本。实际费用/峰值超估仍R3D-010。persistence原生费用沿§7.4部署实测保守envelope，未知/不足时native前R3D-010，不以32*N冒充HALCON内部内存公式。

Adapter在同一次decode后读取请求object、核对数量/尺寸/域/值与来源→限额复制→算hash→全部层校验成功→重建/归还native和source；每方向只原子交一个完整AdapterDirectionResult。缺层、对象多/少、shape/domain/hash不符R3D-024；不支持请求R3D-007；预算R3D-010；operator异常保原stage/AdapterCode走既有R3D-013。Core验证层集合精确覆盖请求/原Gray数量，再复制入最终DiagnosticLayers；错误使该方向失败，按原PartialPolicy处理，不用warnings掩盖漏交必需层。Diagnostics=null却有层同为R3D-024。诊断非独立decoder入口；仅附在原重建成功方向，零成功/重建失败不凭诊断宣布操作成功，新共同标定DTO不在此增量中定义。

复制的具体算子链：对每个已选单image用`get_image_size`核原camera W/H、`count_channels`必须=1、`get_image_type`限定byte/int2/uint2/int4/real（每次get_grayval tuple恰等于请求pixel数，禁止复数/向量/多通道展平）；`get_domain`后与原ROI求交，仅将该域交给`get_region_runs`。此算子每次只接受一个region，返回按row升序/同row左到右的闭区间runs；核对三tuple等长、整数、0≤row<H、0≤start≤end<W、无重复/交叠，数量≤N。依run填Domain，在域内按row/column升序每批≤4096像素调用`get_grayval`，核返回数/有限值再写Values；**get_grayval本身忽略image domain，绝不能读全图后把域外值填入DTO**。PatternRegion只枚举原region与ROI的runs，ROI内先置0、region内置1，不调用灰度读取。Binary/Membership域内只接受0/1（binary按表中0/255显式转换），其它kind保持所选单位原值；Core同样验单位/值集合，不只验hash。各批不缓存完整像素tuple，复制间观察取消/Deadline；未完成层不发布。三个run tuple及managed展开scratch每次单层计费并释放，Managed另预留`checked(32*N+65536)`瞬时上界、Native沿部署envelope，不混入MaxOutputBytes的最终层费用；Simulator无此native/run scratch。生成图hash亦按逐行≤4096pixel批限额读取/流式SHA256，不新增图案算法。全部经ImageLibDotNet.cv2，公共C#参数/tuple重载在Adapter定向消费编译，不检查封装内部。

ApplyPublished仅改变Surface/Geometry，诊断仍在相机pixel域、原hash/axis/来源保持，禁止融合DiagnosticLayers或重命名为OutputFrame数据。取消/到期后不开始新object读取/复制；已完成原子方向可沿既有Partial结果保留，未完成层组不交；在途get/复制及原Task/lease仍由原operation Owner强持并排空。DrainUnknown时Result=null，包括DiagnosticLayers；不得先把有值phase发送给上游再释放未决模型。native/source归还、回调/原Task真实退出条件和有限根恢复沿§9/§11/§13.5，不增加“诊断已复制即可Released”的旁路。

## 5. 公共 API、同步/异步和取消

### 5.1 入口

```csharp
public interface IReconstruction3D : IAsyncDisposable
{
    ValidationReport Validate(ReconstructionInput input,
                              ReconstructionParameters parameters,
                              FusionPolicy? fusion);

    ReconstructionReply Reconstruct(
        ReconstructionRequest request,
        CancellationToken cancellationToken = default);

    ValueTask<ReconstructionReply> ReconstructAsync(
        ReconstructionRequest request,
        CancellationToken cancellationToken = default);

    ValueTask<ReconstructionReply> ReconstructAsync(
        ReconstructionRequest request,
        IProgress<ReconstructionProgress>? progress,
        CancellationToken cancellationToken = default);

    ReconstructionOperationSnapshot Query(string operationId);
    ValueTask<ReconstructionOperationSnapshot> StopAndDrainAsync(
        string operationId, TimeSpan waitBudget,
        CancellationToken cancellationToken = default);
}

public sealed record ReconstructionRequest(
    string ApiVersion,
    string OperationId,
    string CalculationId,
    ReconstructionInput Input,
    ReconstructionParameters Parameters,
    FusionPolicy? Fusion,
    DateTimeOffset? Deadline,
    string AuthorityScope);

public sealed record ReconstructionProgress(
    string OperationId,
    string Stage,
    string? DirectionId,
    int CompletedUnits,
    int TotalUnits,
    TimeSpan Elapsed);
```

### 5.1.1 回执、诊断与宿主端口（同一 API v0.2）

```csharp
public enum OperationState { Created, Validating, Accepted, Running, Draining,
    DrainUnknown, Drained, ResourcesReleased, Completed, Partial, Rejected,
    Failed, Cancelled, TimedOut }
public enum DrainState { NotStarted, Pending, Unknown, Drained, Released }
public sealed record ReconstructionError(string Code, string ReasonKey,
    string Stage, string? DirectionId, bool Recoverable, string? AdapterCode);
public sealed record ValidationReport(bool IsAccepted,
    IReadOnlyList<ReconstructionError> Errors);
public sealed record ReconstructionOperationSnapshot(string OperationId,
    string CalculationId, long Sequence, OperationState State, DrainState Drain,
    ReconstructionError? Error, ReconstructionResult? Result);
public sealed record ReconstructionReply(ReconstructionOperationSnapshot Operation);
public sealed record ReconstructionEvent(string OperationId, string CalculationId,
    long Sequence, string Kind, OperationState State, string? DirectionId,
    TimeSpan Elapsed, ReconstructionError? Error);
public interface IReconstructionDiagnostics { void OnEvent(ReconstructionEvent value); }
public interface IReconstructionClock {
    DateTimeOffset UtcNow { get; }
    long Timestamp { get; }
    TimeSpan Elapsed(long startTimestamp);
    ValueTask WaitUntilAsync(long startTimestamp, TimeSpan elapsedBudget,
        CancellationToken cancellationToken);
}
public interface IFrameLease : IAsyncDisposable {
    FrameRef Descriptor { get; }
    ReadOnlyMemory<byte> Bytes { get; }
    int RowStrideBytes { get; }
}
public interface IFrameSource {
    ValueTask<IFrameLease> AcquireAsync(FrameRef frame, CancellationToken cancellationToken);
}
public interface ISurfaceInputLease : IAsyncDisposable {
    AdapterDirectionResult Value { get; }
}
public interface ISurfaceInputSource {
    ValueTask<ISurfaceInputLease> AcquireAsync(DirectionCapture capture,
        CancellationToken cancellationToken);
}
public interface ICalibrationAssetLease : IAsyncDisposable {
    RevisionRef Asset { get; }
    ReadOnlyMemory<byte> SerializedCameraSetup { get; }
}
public interface ICalibrationAssetSource {
    ValueTask<ICalibrationAssetLease> AcquireAsync(CalibrationRef calibration,
        CancellationToken cancellationToken);
}
public sealed record ReconstructionPorts(IFrameSource Frames,
    ISurfaceInputSource? SurfaceInputs,
    ICalibrationAssetSource? CalibrationAssets,
    IStructuredLightEngineAdapter? StructuredLight,
    IStereoReconstructionAdapter? Stereo, ISurfaceInputAdapter? Surface,
    ISurfaceTransformAdapter? Transform, IReconstructionClock Clock,
    IReconstructionDiagnostics Diagnostics);
public interface IReconstructionFactory {
    IReconstruction3D Create(ReconstructionPorts ports);
}
public interface IReconstructionIsolationOwner {
    void Retain(IReconstruction3D engine, ReconstructionOperationSnapshot snapshot,
        IReadOnlyList<Task> pendingWork);
}
```

代码块为要求实现的公开声明，不是声称当前 DLL 已存在；后续 `public sealed class ReconstructionFactory : IReconstructionFactory` 提供无参数公开构造器和 `public IReconstruction3D Create(ReconstructionPorts ports)`，不依赖平台 DI 容器。Core 只依赖 BCL 与这些端口。FrameSource 对光学帧只接受 PixelFormat="Mono8"、单通道 byte（stride≥Width），长度≥checked(stride×Height)，由 source 校验冻结 revision/hash；其它格式明确 R3D-007。光学 CalibrationAssets 必填，普通资产按 CalibrationRef.Asset 提供同 hash 的 HALCON camera_setup 序列化字节；`CameraProjectorJointV1`必须走§8.1独立绑定，Asset核Joint资产摘要，字节另核Export.File摘要/长度，不要求二者摘要相等。适配器负责只读加载，若 read_camera_setup_model 需要临时文件，由操作拥有唯一临时路径并在排空后删除，仅访问该租约，不猜全局目录/数据库。资产引用/hash 未匹配为 R3D-005。传感器表面由 Surface adapter 消费只读表面快照，不能把 SDK handle 编进 Bytes。Core 把 source 端口显式传给适配方法，不另外重复获取同一租约；适配器以操作上下文持有租约并在 native/回调真实退出后唯一归还。图像转 native 的临时对象由适配器持有；回执只有值对象、无句柄。

`Validate` 不加载图像/资产，检查冻结值、manifest、预算和端口存在性。实例同时最多接纳一个操作，内部无排队；忙时短拒绝 `R3D-022 BusyOrClosing`。保留窗内重复 OperationId/CalculationId 不重算，原 ID 通过 Query 读取，提交重复返回 `R3D-023 DuplicateOperation`；即使内容相同也不当缓存执行。终态查询记录实例内 FIFO 有界保留 256 项（连同两个 ID），不驱逐在途项；重请求的短拒绝回执不覆盖原记录。驱逐后 Query 返回 State=Rejected、Drain=NotStarted、R3D-016、Result=null，表示该实例没有记录，不能推断原操作失败。模块不承诺跨驱逐/重启去重，宿主永久不重用两个 ID；释放实例前取走所需结果。Deadline 是可空绝对 UTC；接纳时将 UTC 剩余预算与显式 Timeout 取最小值并转单调时钟，时钟后调不能延长请求，已到期直接短拒绝。

确定性预检优先序：request版本/基本值 → 保留窗重复ID/实例busy/closing → input基本值/模式与端口 → 重复FrameId/ordinal → manifest缺项 → ordinal/PatternId/相机身份不匹配 → timing → 标定/变换作用域 → 预算。ValidationReport列出该阶段可确定的错误，回执主Error采用最早一项；不继续加载资产找次级错误。缺帧先于随后的一一timing缺项，避免同一fixture在不同实现中返回不同主错误。

ReconstructionFactory.ApiVersion 公开常量为 "0.2"，Request.ApiVersion 必须精确相等；Reconstruct 预检检查 request身份/版本/Deadline，Validate(input,parameters,fusion) 只校验其三个参数，不能声称单独 Validate 已检查整个 request。OperationId/CalculationId/AuthorityScope 均非空、长度≤128、无控制字符。Query的256项是身份/终态保留窗；结果值引用另受每实例64MiB历史结果保留上限约束，按终态FIFO丢弃最早结果引用（不删身份），单个超过上限的结果仅原回执交付、Query不保留大数组。此时 Query保留已知终态/Drain，Result=null、R3D-016/ReasonKey=ResultNotRetained，表示结果未留存，不能改为操作Unknown/失败；宿主自行保存原回执。不得在途删引用或归还资源以满足历史缓存上限。

IsHashVerified是宿主从IM-033已发布资产读取/校验后给出的消费证明，Core要求true，否则R3D-018；它不赋予宿主估计/发布权，也不把bool当签名认证。IM-032不对未定义的平台信封自行造序列化算法求hash。Frame/资产source必须核对descriptor与实际载荷hash；纯Core fixture将该校验动作模拟为明确的true/false输入，不能宣称证明了真实发布系统。

Clock.Elapsed必须单调，WaitUntilAsync使用同一时间域，预算正且到Elapsed(start)≥budget时完成、令牌取消时只取消等待。真实Host用Stopwatch/单调timer；fixed-clock harness推进时间时主动完成到期闩锁，不让Core靠真实Sleep或轮询猜虚拟时间。Core在等待adapter/source任务时同时观察这个截止任务，到期停止并有限排空；同步托管分桶/融合/建议每4096个元素或更小循环块核对取消/单调deadline。进度CompletedUnits/TotalUnits按该阶段有界帧/方向/块计数（≤Int32.MaxValue），不把总帧像素乘积硬塞int。

诊断 Sequence 每操作严格递增；进度是可合并投影，异常接收器不得改计算结果，捕获接收器异常并向宿主返回诊断失效 warning。IProgress 不保证执行线程；核心不捕获 UI SynchronizationContext，UI 桥按 OperationId/Sequence 去迟到更新。StopAndDrainAsync 幂等请求取消并等待至 waitBudget（100ms..60s）；等待令牌只取消等待，不撤销已发出的停止，不释放在途资源。未知返回快照，不伪造取消完成。Query 无 IO；未找到返回 Unknown 错误并无 Result。

DisposeAsync 先拒绝新请求，再对在途操作停止/等待；DrainUnknown 时抛带 R3D-014 的 InvalidOperationException，保留隔离上下文和 Query/StopAndDrain 可用，不能宣称释放成功；确认 worker 终止且 native 不再访问资源后才可发布 Drained/ResourcesReleased。宿主隔离 worker 的动作在模块外，模块不擅杀设备进程。

DisposeAsync 无在途时立即完成，有在途时最多等待该请求 DrainTimeout；重复 Dispose 共享关闭状态，不重复归还。Core 的等待采用单调有限观察截止点：即使适配端口忽略取消/未按 waitBudget 返回，观察到期也返回 DrainUnknown，并持有/观察原任务、租约和上下文，不能继续 await 到无限期。适配器异常退出不代表 Drained，仍按 QueryDrain/StopAndDrain 核对。IReconstructionIsolationOwner.Retain 正常返回是接收确认，契约承诺不抛异常；只保留同一 engine 一次，接收 pendingWork（run/stop/dispose 的已发出 Task，含已完成任务）并观察迟到异常。Host 必须在 factory 前预留有界强持槽（§11）；确认前原槽继续持有 engine、全部已发出任务和两个ID，即使接收器违约抛错也不能丢原Owner或返回成功。确认后原槽才可移交；后台 Owner 在真实Drained、全部原任务退出后唯一完成释放。未决实例不能重建或在原操作上重试。外层独占测试进程终止仅证明测试已停止，不能声称 native 成功排空。

同步 `Validate` 只做确定性的输入和资源检查，不创建 native 句柄、不读取设备、不启动线程。同步 `Reconstruct` 仅供离线/控制台宿主使用：它在当前调用线程完成同一状态机和排空规则，不能在 WPF/UI 线程调用，且仍必须接收取消令牌和截止时间。生产宿主和 UI 宿主使用 `ReconstructAsync`；异步入口不能通过 `Task.Run` 把不可取消的 native 调用伪装成可取消。

### 5.2 事件顺序

诊断接收器按以下顺序接收事件；同一 `OperationId` 的 `Sequence` 严格递增，允许合并进度但不允许重排终态：

预检路径为 `RequestReceived → ValidationCompleted(Rejected) → RequestRejected`；若预检曾创建资源，先归还并发送 `ResourcesReleased`。未接纳请求不得发送 `RequestAccepted`、`Running`、`QualityEvaluated` 或 `ResultAvailable`。已接纳路径为 `RequestReceived → ValidationCompleted(Accepted) → RequestAccepted → DirectionStarted → DecodeCompleted? → DirectionReconstructed → DirectionQualityEvaluated? → CrossDirectionChecked? → FusionStarted/FusionCompleted? → ResultAvailable? → DrainStarted → Drained → ResourcesReleased → Completed | Partial | Rejected | Failed | Cancelled | TimedOut`。`ResultAvailable` 只表示不可变值结果已复制完成并可供终态回执引用，不表示异步调用已返回或资源已释放。接纳后的运行前失败也必须排空并归还资源后才发布唯一终态。

`ResultAvailable` 仅表示不可变结果快照已构造，宿主只能在最终响应返回后消费；`Drained` 表示 native 运算与回调均已退出，`ResourcesReleased` 表示图像/模型/缓冲区租约已归还。取消请求事件 `CancelRequested` 不代表已停止。

### 5.3 无 UI 的参数建议 API

```csharp
public sealed record ContrastSample(byte Contrast, bool ExpectedValid);
public sealed record ContrastRecommendationRequest(RevisionRef Input,
    RevisionRef Pattern, RevisionRef Exposure, RevisionRef Calibration,
    IReadOnlyList<ContrastSample> LabelledSamples,
    IReadOnlyList<int> Candidates);
public sealed record ThresholdEvaluation(int Threshold, int FalseAccept,
    int FalseReject, int TrueAccept, int TrueReject);
public sealed record ContrastRecommendation(int? SuggestedThreshold,
    string StatusKey, IReadOnlyList<ThresholdEvaluation> Evidence,
    RevisionRef? Input, RevisionRef? Pattern, RevisionRef? Exposure,
    RevisionRef? Calibration, string MethodVersion);
public interface IContrastRecommender {
    ContrastRecommendation Recommend(ContrastRecommendationRequest? request,
        CancellationToken cancellationToken = default);
}
```

Core 唯一公开创建入口冻结为 `public sealed class ContrastRecommender : IContrastRecommender`，公开无参构造器 `public ContrastRecommender()`，实现上述同签名 Recommend 方法；调用为 `IContrastRecommender recommender = new ContrastRecommender();`，不依赖DI/反射/Reconstruction实例、UI或外部资产端口，不隐藏factory/静态可变实例。类声明在此描述实现要求，不用空方法体冒充已有代码。

对应 §7.5 的唯一算法，MethodVersion 固定 `contrast-labelled-v1`；状态键 Suggested/Abstain/Invalid/Cancelled。停止在样本/候选循环边界检查，不伪造 native 生命周期。确定返回优先序：进入时令牌已取消先返回Cancelled（即使request=null）；否则null request、任一null/非法revision、null集合/样本元素、空/越上限/重复或越界候选、缺正负两类均返回Invalid；合法请求循环中取消返回Cancelled。上述情况不抛ArgumentException/NullReferenceException/OperationCanceledException。Invalid/Cancelled的SuggestedThreshold=null、Evidence为空；四个来源引用仅保留通过基础校验的revision，其余null，不能造占位有效hash。Suggested/Abstain四来源必须非null、Evidence为完整候选计数，Suggested才有阈值。取消丢弃未完成计数，不包装成完整Evidence。资源耗尽等不可恢复运行时异常不承诺吞掉或转换成功；Host记录非零失败。输入列表接纳时深复制，结果Evidence不可变；取消/校验不改变生产Profile。此能力属于Core完整范围，必须无 UI 可调用。

## 6. 状态和错误语义

### 6.1 状态机

`Created → Validating → (Rejected before admission | Accepted → Running → Draining → Drained → ResourcesReleased → Completed | Partial | Rejected | Failed | Cancelled | TimedOut)`。预检拒绝不进入执行状态；若预检暂有资源须先归还。接纳后即使在首个 native 阶段前发生失败，也必须走排空/资源归还路径。终态不可回到运行态。进程重启后只能从调用方保存的请求快照重新创建新的 `CalculationId`，不读取 `latest` 猜测旧状态。

### 6.2 错误码

| 错误码 | 语义 | 调用方动作 |
|---|---|---|
| `R3D-001 InvalidRequest` | 必填字段、有限值或范围错误 | 修正请求后新 CalculationId |
| `R3D-002 IdentityMismatch` | 输入集/方向/epoch/版本不一致 | 重新冻结输入；禁止拼接 |
| `R3D-003 MissingFrame` | 结构光步序或立体配对不完整 | 按批准策略重采集或标记未覆盖 |
| `R3D-004 DuplicateFrame` | 同 ordinal/同帧重复 | 保留原始证据并拒绝该请求 |
| `R3D-005 CalibrationInvalid` | 标定缺失、过期或作用域不匹配 | 由宿主处理标定，不在模块内替换 |
| `R3D-006 UnitOrCoordinateMismatch` | 单位或坐标图不兼容 | 由上游/IM-033 提供匹配的已发布变换快照后，以新请求重新调用；IM-032 不自行估计或转换 |
| `R3D-007 CapabilityUnsupported` | 适配器/算子不支持请求模式 | 使用已登记能力或拒绝 |
| `R3D-008 QualityInsufficient` | 输入或算法质量 Gate 未通过 | 输出 `NotQualified`/`Partial`，不伪造完整结果 |
| `R3D-009 DirectionConflict` | 同域多方向差异超策略 | 保留冲突域，由调用方解释 |
| `R3D-010 ResourceLimitExceeded` | 像素、内存、并发或队列超限 | 降低请求规模或稍后重试 |
| `R3D-011 Cancelled` | 调用方取消且已排空 | 不产生提交副作用 |
| `R3D-012 Timeout` | 截止时间到且已排空 | 查询本次计算状态；不得隐式重试 |
| `R3D-013 AdapterFailure` | AsunImage/输入适配器返回错误 | 记录原错误和句柄状态，按策略恢复 |
| `R3D-014 NativeDrainFailed` | 取消/异常后 native 未能在预算内排空 | 进程隔离或实例废弃，不能复用句柄 |
| `R3D-015 VersionIncompatible` | 算法/标定/契约版本不兼容 | 按兼容矩阵选择适配器或回退 |
| `R3D-016 Unknown` | 操作结果无法确认 | 保持 Unknown，查询原 operation，不生成新事实 |
| `R3D-017 QualificationProfileMissing` | 资格/几何判定 Profile 缺失或未发布 | 保留候选/掩膜，拒绝资格结论和融合；补齐 Profile 后新计算 |
| `R3D-018 PublishedTransformUnavailable` | IM-033 变换快照缺失、撤回或 hash 不可验证 | 不执行共同坐标融合；查询/重新获取已发布快照后新计算 |
| `R3D-019 TransformScopeMismatch` | 方向、坐标、epoch 或 CalibrationRevision 与快照不一致 | 拒绝应用；由 IM-033/宿主重新发布匹配快照 |
| `R3D-020 TransformAlreadyApplied` | ApplyPublished 分支要求对已有 count=1 再应用、count>1 或标记矛盾 | 拒绝重复应用；已在目标坐标的输入改用可验证 AlreadyInOutput 分支 |

新增错误与稳定回复：

| 错误码 | 触发/阶段 | 保留与恢复 |
|---|---|---|
| R3D-021 AcquisitionTimingMismatch | Validate，曝光不在 pattern 稳定窗、跨时钟/attempt/epoch 或时间跨度越界 | 无 native 执行；宿主提供完整新采集 |
| R3D-022 BusyOrClosing | 实例忙/正在关闭 | 短拒绝，不排队；查询既有操作 |
| R3D-023 DuplicateOperation | ID 曾提交或仍在途 | 不再执行；Query 原 ID 或用新计算身份 |
| R3D-024 SourceEvidenceUnavailable | 立体无 m3d_pairwise/来源，导入 mask/XYZ/CSR 不完整 | 接纳后排空再 Rejected；保留诊断，不给有效量测 |

异常对象必须同时携带 `OperationId`、`CalculationId`、阶段、方向、原始适配器错误（如有）、是否已产生结果、是否已排空和可恢复建议。异常消息不得泄漏文件密钥或设备凭据。

## 7. 算法路线与 HALCON/AsunImage 边界

### 7.1 结构光：物理模型、图案与质量

采用非镜面表面的相机—投影器三角测量，投影器是 inverse camera；`deflectometry` 不是本模块高度重建的替代路线。项目本地 HALCON 26.05 原文确认 camera_setup_model 相机 index=0、投影器 index=1，输出在该标定世界坐标。完整图案组必须来自同一曝光/静止 attempt；滚动快门、运动、漂移或多路径不能靠像素质量分数补救。

生产主路线冻结 `HybridVertical`：`pattern_type=gray_code_and_phase_shift`、`pattern_orientation=vertical`、`normalization=global`。`HybridBoth` 只消费上游已冻结的双向采集，用 vertical correspondence 重建，不再生成第二套高度；本重建入口不接受Both的具名诊断请求，ProjectorRows/Columns交接仅走§7.6的decode-only入口，不能把horizontal解码存在误写为本回执已支持诊断层。`GrayVertical` 只在消费者已批准整数对应精度的独立 Profile 时使用；`SingleStripeVertical` 只在部分反光的专门采集/Profile 已资格化时使用，仍非纯镜面保证。它们是请求明确选定的物理采集分支，不是失败后换模式、挑帧或在线训练的备用。纯镜面/黑面不可观测则返回掩膜/原因，由宿主决定新采集；全失效为 NotObservable，不补零。

执行顺序冻结：

1. 校验 timing、PatternSpec、标定 scope、完整 ROI 与资源；创建独占 `3d_reconstruction` 模型。
2. 依次设置图案尺寸、类型、方向、normalization、stripe 宽、min_gray_difference；调用 `gen_structured_light_pattern` 建立当前模型解码布局，按§4.2.2完整Sequence逐对象核对数量/顺序/生成图hash/角色，再绑定已发布 camera_setup_model。normalization黑白/互补帧不得删去或冒充GrayCode；生成对象只作布局核对，用后释放，不向设备发送。
3. 对整组图像应用同一 `reduce_domain`（原像素坐标/尺寸不变），不单独缩放/裁图；固定是否 persistence 后调用 `decode_structured_light_pattern`。只有 `CapturePhaseDiagnostics=true` 且预算允许时启用 persistence，不能运行中开关。
4. 读取 `get_structured_light_object` 的 `correspondence_image`、`pattern_region`；无 persistence 也可读取。显式Diagnostics按§4.4.1读取phase/binarized/gray/single-stripe支持项，限额复制原domain/值/来源/hash后释放临时对象；Diagnostics=null不导出层。不得把 `defect_image` 用于 3d_reconstruction，它仅属于 deflectometry。
5. 调用 `reconstruct_surface_structured_light`，按 `object_model_3d_to_xyz('from_xyz_map')` 取原映射支持域和各 XYZ domain 交集；其real图像不是无损double量测载体。量测XYZ按§7.7.1从模型原坐标tuple与mapping逐项提取。无重建像素不在domain，不由Z=0猜有效性。原始domain与输入ROI、饱和/解码拒识域相交。
6. 按 CalibrationScope.NativeLengthToMm 转换 XYZ，保留 origin/来源；之后才能按 §7.3 应用已发布方向变换。参数/标定变化使旧 decode 失效，新 operation 从完整冻结输入重新执行。

| 参数 | 实际可用范围/单位 | 来源、变更与建议边界 |
|---|---|---|
| pattern_width/height | int≥1，投影器 pixel；须等于标定投影器尺寸 | PatternSpec；不采用 HALCON 1024 默认猜投影器 |
| min_stripe_width | int≥4、2 的幂；≤尺寸各自向上取 2 的幂后的较小值 | 已批准 PatternSpec；取值还须满足尺寸>width/2；变化须重新采集，不用新布局解旧帧 |
| single_stripe_width | 仅 SingleStripeVertical；2 的幂、≥min_stripe_width 且不大于上述尺寸约束 | 显式 Profile；非 single_stripe 必须 null |
| normalization | global 或 inverted_pattern | 主路线 global；inverted_pattern 仅伴随专门完整互补图案 manifest，不是运行时替换 |
| min_gray_difference | byte 灰度差 0..255；HALCON 原文为 integer≥0，本模块 byte 输入收紧上限 | 无生产默认，Profile 显式冻结；0 只允许离线未资格化诊断，不能形成 QualifiedCandidate |
| persistence | false；诊断请求可 true | true 存中间图且显著增内存；设置变化清结果，必须解码前固定 |

相位质量必须与高度不确定度分开。HALCON `gen_structured_light_pattern` 每方向产生四幅等间隔相位图（不能套OpenCV三步相位顺序）。四幅对应0、π/2、π、3π/2时，`C=I0−I2`、`S=I3−I1`、`A=sqrt(C²+S²)/2`、`DC=(I0+I1+I2+I3)/4`、`M=A/max(DC,1)`仅解释调制度的离线研究含义；M不是mm或置信概率。当前公开请求和六类诊断输出没有M层/阈值，故本版不额外计算、返回或按M裁生产域，不暗加新enum/codec。上游已明确标记WeakModulation可保留原因9；不得由本模块猜阈值生成它。额外M路线须有真实消费者并修订同一请求/输出/验收后才实施。现版按冻结min_gray_difference、HALCON解码域与明确饱和证据裁域；相位/Gray边界不一致、周期歧义或多路径候选记DecodeRejected/AmbiguousDepth，不选“最平滑”的深度。不确定度无误差模型则null，不能以1/M代替。

### 7.2 多视立体：保留既定 surface_fusion 主路线，分开观测与展示

HALCON 26.05 `reconstruct_surface_stereo` 的 surface_fusion 原文明确优化 isosurface、平滑/补洞并尝试闭合；它不能直接作为 PerDirection 原始量测事实。既定主路线仍为 `create_stereo_model(...,'surface_fusion',...) → set_stereo_model_param → set_stereo_model_image_pairs → reconstruct_surface_stereo`。运行前必须 persistence=true；运行后读取 `get_stereo_model_object_model_3d('m3d_pairwise')` 保留原始中间云核查，并逐对读取该次运行的 disparity/score/rectified 图，按下列确定步骤生成带索引的原始观测 PerDirection。m3d_pairwise 返回 -1 或逐对证据不完整时 R3D-024，不把 isosurface 填进去。m3d_pairwise 没有公共逐顶点 pair/pixel 对照，不假定其顶点顺序等于图像扫描序，也不靠最近邻猜来源；PerDirection 的顺序以该次持久化 disparity 为准。isosurface 只作 Interpolated/Unverified 独立展示，由宿主受控证据投影，不参与 EqualSupported/量测；核心回执不持有其 native 句柄。

- 主 disparity_method 固定 binocular，binocular_method=ncc、binocular_filter=left_right_check、binocular_sub_disparity=interpolation、point_meshing=none。NCC 抵抗均值/对比变化；其 score 低于门槛拒绝，不能套 mg/ms 的相反 score 方向。这里的 subpixel disparity 细化是对应计算，不是无效域补洞。
- StereoSpec.NumLevels≥1；MaskWidth/Height 为≥3 奇数且不大于图像尺寸；TextureThreshold≥0；ScoreThreshold 为 NCC 的 [-1,1]，已发布 Profile 显式冻结；每对 min_disparity≤max_disparity 且在图像可搜索宽度内。默认不读取 bounding box 自动估算视差；每对显式范围必须与标定和物理 Z 范围核对。粗到细 pyramid 只在 NumLevels 冻结且同样本微细纹理通过时启用；不随机器/当前 score 动态提高层数。
- bounding_box 是 6 个有限 mm 值，x1<x2、y1<y2、z1<z2，在标定世界坐标；向 HALCON 边界换回原生标定长度一次。先 set bounding_box，再显式设置 resolution、surface_tolerance、min_thickness、smoothing，因为重设 box 会重置这些参数；min_thickness≥surface_tolerance>0、resolution>0、smoothing≥0，必须由 StereoSpec 提供。不能从示例抄物理数值。
- 输入图像按 camera setup index 固定排序，曝光中点时差符合冻结 TimingProfile；漫反射、纹理、重叠、标定外参须成立。重复纹理/低纹理/反光/极短基线是拒识情况，不能按最高 score 静默给唯一真深度。左右一致性失效像素不参与输出。
- 明确设置 rectif_method=viewing_direction、rectif_sub_sampling=1.0、rectif_interpolation=bilinear；不依赖环境默认或运行时降低采样。先设这些值再 set_stereo_model_image_pairs，后改 rectification 参数须新操作/重新设 pairs。首发原始观测不再下采样；point_meshing=none。HALCON 多对云通常没有 xyz_mapping，禁止对它调用 from_xyz_map；也不能用 display cartesian_faces 将插值像素反造支持域。

逐对来源恢复是同一 surface_fusion 调用的证据提取，不额外运行第二种匹配算法：

1. 冻结 pair 顺序 N=0..Pairs.Count−1；用 `get_stereo_model_object` 的 PairIndex=[FromCamera,ToCamera] 取 from_image_rect/to_image_rect/disparity_image/score_image。用 `get_stereo_model_param` 分别查询 `from_cam_param_rect N`、`to_cam_param_rect N`、`from_cam_pose_rect N`、`to_cam_pose_rect N`、`rel_pose_rect N`（tuple 参数不得塞进一个混合查询）。它们须对应同一模型/运行/标定 revision。
2. 对 pair 的 disparity 调用 `disparity_image_to_xyz`，传上述 rectified 两端内参与 rel_pose_rect；得到每个 disparity(row,column) 在 rectified From 相机中的 XYZ。支持域为 disparity/score/XYZ domains 的交集且 score≥ScoreThreshold、disparity 在本对范围、全部值有限；不把 Z=0 或 score=0 当无效。原图 ROI 不直接套在整流 row/column 上，按第4步投回原图核对。三角测量/投影退化记 NoCorrespondence。
3. `pose_to_hom_mat3d(from_cam_pose_rect N)` 得 HorigFrom←rectFrom；`get_camera_setup_param(FromCamera,'pose')` 得 Hsetup←origFrom。按 `affine_trans_point_3d` 先 rectFrom→origFrom、再 origFrom→setup；两步仍在标定原生长度，之后乘 NativeLengthToMm 一次。setup 必须是 CalibrationScope.ReconstructionFrame/SourceFrame；这两步是标定内部映射，不增加 IM-033 ApplicationCount。禁止把 camera pose 反向使用或省掉整流 pose。
4. 构造两端来源射线：From 原图坐标用 origFrom XYZ 和该相机 `get_camera_setup_param(...,'params')` 经 `project_3d_point`；To 端先对 rel_pose_rect 经 pose_to_hom_mat3d/hom_mat3d_invert 得 HrectTo←rectFrom，变换到 rectTo，分别用 to_cam_param_rect 投影为整流子像素坐标、用 to_cam_pose_rect 变到 origTo 后用原 To 内参投影为原图子像素坐标。这里不猜 disparity 的正负号，也不把 To 坐标四舍五入。两端原图坐标须有限、位于图像和冻结 ROI，bilinear 所需 floor/ceil 支撑像素均在有效原图域且未饱和，否则拒识；边界重复邻点只计一次。这是观测射线的原图定位，不能宣称它记录了 NCC 整个窗口的每个内部权重；窗口大小/整流方法/标定 hash 同时保留在 provenance。
5. 按 pair ordinal、rectified row、column 固定顺序枚举；SampleIndex 为跨 pair 的 checked 前缀像素数加 row*rectifiedWidth+column，不靠压缩点号猜原位置。每个有效观测生成两个 SampleSource（From/To FrameId、同一 SampleIndex、各自 StereoSampleSource）；不存在原图整数 ImageRow/ImageColumn。结果是 PointCloud，Width=保留点数、Height=1、Grid=null、CSR 每点两条来源，同一方向重复 pair 观测仍只算一个方向。BoundingBox 在 setup mm 坐标按闭区间过滤；ZMin/ZMax 在最终 OutputFrame 才过滤。没有任何观测时该方向 R3D-008、无伪造点云；所有方向无产物则 Rejected/OverallQuality=NotObservable（Result 可仅含 DirectionIssues）。
6. m3d_pairwise 和 isosurface 均在复制必要值、完成核查后清理；不把二者与原始逐对 XYZ 强行按序拼接。用真实 pair fixture 验证各相机 ray、setup 坐标、范围、CSR 与中间云几何一致性；发现无法解释的对应/坐标差异时 R3D-024，原始源证据保留给宿主。公制差异公差来自消费者计量 Profile，不由模块或 OpenCV 测试抄数。来源射线不确定度未知仍 null。

实质候选比较：surface_pairwise + point_meshing=none 更直接保留观测且避免体素 isosurface 费用；当前已冻结 surface_fusion，故它只作同样本评测/未来新 Profile 变更候选，不是首发 runtime fallback。binocular_mg/ms 的平滑与 score 语义不同，当前主路线不自动切换；可离线比较误接受/拒绝、薄台阶/孔边保真和峰值后发布新 MethodRevision。photometric_stereo 推导法向/反射假设，未给本模块绝对公制三角测量；fuse_object_model_3d 也补闭面，不是等权观测融合替代。未做代表样本 benchmark，本文不声称哪条路线最快。

### 7.3 一次应用配准、共同网格与有来源融合

IM-033 是方向变换估计、资格化、发布、撤回唯一 Owner。宿主将发布快照与状态/hash 校验结果冻结注入；IM-032 只检查本次消费作用域，不以自身 residual 再资格化矩阵。`ApplyPublished` 验证输入 epoch、CalibrationRevision、每方向 FromFrame 与实际重建 frame、ToFrame=OutputFrame、上一应用数=0；通过后只在 ApplyPublishedTransform 阶段调用一次。`AlreadyInOutput` 按 §4.2.1 验证并跳过。标定原生单位规范化在矩阵前，不把 HALCON camera setup 内部已完成的 camera→world 变换当作 IM-033 方向变换再做一次。

快照缺失/未发布/已撤回/hash 错 → R3D-018；方向缺项/epoch/坐标/标定 revision 不匹配 → R3D-019；申请重复应用/标记矛盾 → R3D-020。不执行 CrossDirectionCheck/Fuse，原始 SourceFrame 候选可保留但不得写 OutputFrame 标签。已有快照被撤回的历史结果保持原 provenance，不改成新结果；下游是否接受由其 Owner 决定。

网格消费算法冻结为观测点分桶，而非最近邻补洞：

1. FusionPolicy 非 null 时 GridSpec 必需；Width×Height 在 MaxPixels 内、StepX/StepY>0，坐标定义 `x(c)=X0+c*StepX`、`y(r)=Y0+r*StepY`。不把相机 row/col 当 world XY。
2. 对变换后的每个真实有效 XYZ，用半开单元范围 `[x(c)−StepX/2,x(c)+StepX/2)`、同理 Y 分桶；边界相等落入右/下单元。实现用 floor((x−X0)/StepX+0.5)，并检查范围。点到单元中心距离超过 MaxCenterDistance 不贡献；该上限与 MaxWithinDirectionSpread 来源为已发布几何 Profile，不编物理值。
3. 每个 direction/cell 内若有效样本 max(Z)−min(Z)>MaxWithinDirectionSpread，标 AmbiguousDepth，该方向不贡献，保留全部候选来源，不挑最高/最低/最接近。否则以 `(distance², SampleIndex)` 稳定升序选实际点一次；这是单元内有限支持代表点，不从邻格借点、不合成插值。多层云本身仍可输出，单值高度融合明确拒绝重叠层。
4. 按 DirectionId Ordinal 排序，每格合格方向数 k≥MinContributingDirections，才逐对比较；差异统计为 max(Z)−min(Z)，超过 MaxDirectionDisagreementMm 即 DirectionConflict。等号允许。以固定 double 累加顺序 `sum(Z/k)`（先逐项除k，避免有限坐标累加溢出） 生成唯一融合 Z，X/Y 为网格中心且 Geometry 表示 OutputGrid；保留原始 XYZ 与 CSR 索引，网格中心是表示坐标，不宣称每个观测都来自中心。
5. 各方向自己的遮挡/无支撑域保留；互补而无共同支持的格不能因为合并“覆盖变大”生成有效融合。贡献方向不足则无效 7；冲突则无效 6；Qualified/Unverified/Partial 状态按门槛证据与完整性分开。不同 epoch、输入集、参数 revision 或标定时段不可混合缓存。

当完成且通过软件覆盖门的方向总数不足 MinContributingDirections 时 Fused=null，Issue=InsufficientCompletedDirections；足够但没有任何格达到贡献数门槛时 Fused=null、NoElementMetContributionMinimum。达到贡献数但全为深度冲突时仍返回 Fused 冲突掩膜/CSR，全部XYZ=null、Quality/OverallQuality=Conflict；不能用“无有效融合”丢掉冲突证据。部分格有效时 Fused.Quality=Partial，其余原因/来源保留。这里的软件覆盖门和真实计量资格分开：synthetic/未有真实资格但 Profile 数学门齐备时完整正常结果只能生成 Unverified 融合候选，部分/冲突按其质量状态标记，不能产生 QualifiedCandidate 或生产结论；Profile 数值缺失则 §4.3 禁止融合。保留所有 PerDirection/DirectionIssues，不降低门槛。示例为合成语义测试：同格 A 的 Z=-0.25、B=0.25，门槛=2、差异门=0.5mm，输出0；差异门改为0.49时冲突且Z=null；A仅覆盖格0、B仅覆盖格1时无融合产物。这些数值不是客户公差。

### 7.4 超大图、ROI 与内存执行顺序

预检用 checked Int64 核对像素、总帧 bytes、XYZ/mask/CSR 拷贝与模型预算，防护上限不等于能在预算内运行。结构光单方向≤16,777,216 pixels、方向≤16、帧总数≤256、点≤Budget.MaxPoints；逐方向串行，完成一个方向复制必要值并清 native 中间对象后再处理下一方向。FrameLease→iconic view/copy→独占模型→临时图→XYZ managed snapshot→释放临时图/模型→归还 FrameLease，失败和取消遵循相同逆序；输出 managed 值由消费者 GC 生命周期拥有。

ROI 主路线使用全尺寸 reduce_domain，不能认为 ROI 一定减少所有底层帧存储。结构光采用固定 ROI，不按当前结果收缩支持域；立体 stereo 需保留完整整流/匹配邻域，仅在已资格化 Profile 明确整流 ROI 与 window/视差余量时缩域。当前首发不做独立 tile 解码/拼接（边界支持、Gray/phase 时序、立体搜索域均可能变义）。超限由宿主以新请求给已验证 ROI/采集方案，不悄悄降采样或自动 tile。

surface_fusion 预估体素数 `V=ceil((x2−x1)/resolution)*ceil((y2−y1)/resolution)*ceil((z2−z1)/resolution)`，每轴必须正且乘法不溢出；V>MaxVoxelCells 在 native 前拒绝。三维 box/解析度须同单位。仅按像素估内存不够；适配器在本机部署 Profile 冻结 voxel/rectification/persistence 的实测保守 envelope，估算上界不明则 R3D-010，不冒充精确 HALCON 分配公式。Managed/Native/Result 同时预算；Result 复制必须预留且超过时不得“先成功后丢来源”。采样/display 降精度由视口投影负责，不改核心事实。

### 7.5 有界参数建议与生产冻结分离

本模块可无 UI 调用 §5.3 的纯诊断灰度差建议；唯一装配顺序为 `IContrastRecommender recommender = new ContrastRecommender();` → `recommender.Recommend(request, cancellationToken)`，不需要先创建重建engine/注入DI。null/非法/已取消的返回优先序和nullable来源按§5.3；这些预期输入情况返回Invalid/Cancelled而非抛异常，不执行生产Profile变更。离线调用方提供已标注的 byte contrast 样本、候选阈值（1..255、唯一、最多32个），LabelledSamples最多1,000,000项和输入/Profile revision。每候选 t 统计误接收 `contrast≥t && !ExpectedValid`、误拒收 `contrast<t && ExpectedValid`。边界contrast=t计入接收（本地26.05原文为小于min_gray_difference才排除）。只有误接收为0的候选才可建议；再按误拒收最少、阈值最小稳定择一；没有候选满足则 Abstain。没有正/负两类、空/越软件数量上限样本返回Invalid；ExpectedValid即宿主给出的明确标签，不由模块自动声明或推断，不以现场像素自动造标签。建议记录所有候选计数、hash、方法版本和适用输入；输入/曝光/图案/标定 revision 改变即过期。它只为解码灰度差提供候选，不能证明三维精度、反光鲁棒性或资格；宿主评测/人工采纳后发布新 Profile 才可生产使用。stripe/曝光/pattern_type 的改变需新采集，不在既有帧建议里改。

### 7.6 CAL-JC 初始化交接：无标定 decode-only（独立软件切片）

本节关闭首次共同标定的初始化循环。职责仍属IM-032：接收同CaptureGroup完整HybridBoth采集，解码并交具名projector row/column；没有CalibrationRef/Scope、camera_setup、初始内外参、SurfaceResult、world/mm或质量放行字段，不调用reconstruct、共同求解、设备、Writer/Store。真实消费者为structured-light共同标定producer和reconstruction-3d离线共同标定观测工具；二者把原结果交已接收[CAL-JC §7.4.2](../calibration-assets/DEVELOPMENT-GUIDE.md#742-专用值合同profile-与观测包)。这是同模块的`R3D-Decode-C1`协调/值切片和`R3D-Decode-S1`模拟切片；真实算子执行为`R3D-Decode-A1`，不新建独立模块/交付DLL、不改原IReconstruction3D、ReconstructionPorts或0.2.5诊断支持域。

#### 7.6.1 公开C#形状、唯一工厂和前置校验

下列新类型随既有Core发布，namespace `Asun.Modules.Reconstruction3D.Decoding`，using `System.Collections.Immutable`及原Core namespace。它们是要求实现的声明，本轮没有工程/编译/运行。

```csharp
public enum DecodeOrigin { Decoder = 0, Simulator = 1 }
public enum DecodeMappingState { Candidate = 0, Accepted = 1, Withdrawn = 2 }
public sealed record DecodeMappingProbe(int CameraRow, int CameraColumn,
    double ProjectorRow, double ProjectorColumn, double Object1, double Object2);
public sealed record DecodeDirectionMapping(string Version, RevisionRef Reference,
    RevisionRef RuntimeRevision, RevisionRef PatternProfile, RevisionRef ManifestRevision,
    int CameraWidth, int CameraHeight, int ProjectorWidth, int ProjectorHeight,
    int ColumnObjectOrdinal, int RowObjectOrdinal, DecodeMappingState State,
    DecodeOrigin Origin, RevisionRef GoldenEvidence, double MaxErrorPixel,
    ImmutableArray<DecodeMappingProbe> Probes);
public sealed record DecodeAcceptedMapping(DecodeDirectionMapping Mapping,
    bool EvidenceHashVerified, bool EvidenceAccepted);
public sealed record DecodeBackendInfo(RevisionRef RuntimeRevision, DecodeOrigin Origin,
    string EngineVersion, bool SupportsBoth, RevisionRef NativeEnvelope,
    long FixedNativeBytes, long NativeBytesPerCameraPixel, long NativeBytesPerPatternPixel);
public sealed record DecodeWhiteSurfaceRef(string SourceId, RevisionRef Revision,
    int Width, int Height, string CaptureGroupId, string ClockEpoch,
    RevisionRef ParentWhiteRevision, RevisionRef DerivationRevision);
public sealed record DecodeCaptureEvidence(RevisionRef StableEvidence,
    RevisionRef QualityEvidence, string CaptureGroupId, string CaptureEpoch,
    string ClockEpoch, string ClockDomain, long StableStartNs, long StableEndNs,
    TimeSpan CaptureSkew, TimeSpan MaxCaptureSkew, TimeSpan MinStableWindow);
public sealed record DecodeAuxiliarySources(string BlackFrameId, string WhiteFrameId,
    DecodeWhiteSurfaceRef WhiteSurface);
public sealed record DecodeBudget(long ManagedBytes, long NativeBytes, long ResultBytes,
    long MaxInputBytes, long MaxPixels, int MaxFrames, int MaxRowStrideBytes);
public sealed record DecodeRequest(string Version, string OperationId,
    string CalculationId, string AuthorityScope, string CaptureGroupId, string DirectionId,
    RevisionRef InputRevision, ImmutableArray<FrameRef> Frames, PatternSpec Pattern,
    AcquisitionScope Acquisition, DecodeCaptureEvidence Evidence,
    RevisionRef DirectionMapping, DecodeAuxiliarySources Auxiliary, DecodeBudget Budget,
    TimeSpan Timeout, TimeSpan DrainTimeout, DateTimeOffset? Deadline);
public sealed record DecodeFrameSnapshot(FrameRef Descriptor, int RowStrideBytes,
    ImmutableArray<byte> Bytes);
public sealed record DecodeMaskSnapshot(DecodeWhiteSurfaceRef Reference,
    int RowStrideBytes, ImmutableArray<byte> Bytes);
public interface IDecodeMaskLease : IAsyncDisposable {
    DecodeWhiteSurfaceRef Reference { get; }
    int RowStrideBytes { get; }
    ReadOnlyMemory<byte> Bytes { get; }
}
public interface IDecodeMaskSource {
    ValueTask<IDecodeMaskLease> AcquireAsync(DecodeWhiteSurfaceRef reference,
        CancellationToken token);
}
public sealed record DecodedObjectPlane(int ObjectOrdinal, int Width, int Height,
    ImmutableArray<bool> Domain, ImmutableArray<double?> Values);
public sealed record DecodedObservation(RevisionRef RuntimeRevision,
    ImmutableArray<DecodedObjectPlane> Correspondences, ImmutableArray<bool> SupportUnion,
    ImmutableDictionary<string, long> ResourcePeaks);
public interface IStructuredLightDecodeAdapter {
    DecodeBackendInfo Info { get; }
    ValueTask<DecodedObservation> ExecuteAsync(DecodeRequest request,
        ImmutableArray<DecodeFrameSnapshot> frames, DecodeMaskSnapshot mask,
        CancellationToken token);
    AdapterDrainSnapshot QueryDrain(string operationId);
    ValueTask<AdapterDrainSnapshot> StopAndDrainAsync(string operationId,
        TimeSpan waitBudget, CancellationToken token);
}
public sealed record DecodePorts(IFrameSource Frames, IDecodeMaskSource Masks,
    IStructuredLightDecodeAdapter Decoder, ImmutableArray<DecodeAcceptedMapping> AcceptedMappings,
    IReconstructionClock Clock, IReconstructionDiagnostics Diagnostics);
public sealed record DecodeRaster(string Format, int Width, int Height,
    ImmutableArray<byte> Bytes, string Sha256);
public sealed record DecodeCoordinatePlane(PatternAxis Axis, int ObjectOrdinal,
    DecodeRaster Coordinates, DecodeRaster Domain);
public sealed record DecodeResult(string OperationId, string CalculationId,
    string RequestSha256, RevisionRef InputRevision, string CaptureGroupId, string ClockEpoch,
    DecodeOrigin Origin, RevisionRef RuntimeRevision, RevisionRef DirectionMapping,
    RevisionRef ManifestRevision, RevisionRef StableEvidence, RevisionRef QualityEvidence,
    ImmutableArray<FrameRef> SourceFrames, DecodeCoordinatePlane ProjectorRows,
    DecodeCoordinatePlane ProjectorColumns, DecodeRaster ValidMask,
    DecodeRaster BlackImage, DecodeRaster WhiteImage,
    DecodeWhiteSurfaceRef WhiteSurfaceSource, DecodeRaster WhiteSurfaceMask,
    ImmutableDictionary<string, long> ResourcePeaks);
public sealed record DecodeOperationSnapshot(string OperationId, string CalculationId,
    long Sequence, OperationState State, DrainState Drain, ReconstructionError? Error,
    DecodeResult? Result);
public sealed record DecodeReply(DecodeOperationSnapshot Operation);
public interface IStructuredLightDecoder : IAsyncDisposable {
    ValidationReport Validate(DecodeRequest request);
    ValueTask<DecodeReply> DecodeAsync(DecodeRequest request, CancellationToken token = default);
    DecodeOperationSnapshot Query(string operationId);
    ValueTask<DecodeOperationSnapshot> StopAndDrainAsync(string operationId,
        TimeSpan waitBudget, CancellationToken token = default);
}
public interface IStructuredLightDecodeFactory {
    IStructuredLightDecoder Create(DecodePorts ports);
}
```

唯一具体工厂`public sealed class StructuredLightDecodeFactory : IStructuredLightDecodeFactory`，公开无参构造器及`public const string Version="r3d-decode-v1"`，公开`IStructuredLightDecoder Create(DecodePorts ports)`。Create只验证非null端口/Backend.Info和限额复制AcceptedMappings，建立有限原Task/lease账本，不取得源、不调用native/外部Authority；null为ArgumentNullException、非法配置为ArgumentException、均无资源残留。Info只读，在Create时冻结。Validate(null)返回001/不启动作业，DecodeAsync(null)在任务/资源登记前ArgumentNullException；其它非法请求短Rejected/NotStarted、不覆盖已有原Query。每实例**一个**作业、无队列；同ID再调用R3D-023，不覆盖原Query，不同ID在途R3D-022，已终态实例提交新ID仍R3D-022/SingleUseInstance；宿主取新Owner当前映射快照、预留新槽后才创建新实例。调用方提供的注入端口归宿主，模块只拥有本operation取得的lease/native上下文/快照；Dispose不关闭无关共享端口，但实例要求独占decoder adapter，不能两个Root共用一个可变model。

Validate是纯值/当前factory快照检查：Version精确、ID≤128无控制字符/严格UTF8、全部revision/hash合法，Frames1..256、单方向/同相机W/H各≥2、N≤16,777,216 pixels/Mono8。Pattern固定HybridBoth/global、SingleStripeWidth=null、CapturePhaseDiagnostics=false、Diagnostics=null、完整Sequence非null，至少V/H各一个Gray与各四Phase、恰一Black/White；沿§4.2.2生成图hash/角色/完整原ordinal规则，不给deflectometry/GrayOnly/单axis/custom自动fallback。非法值001、布局/来源身份002、缺帧003、重复004、版本015、不支持007；没有任何Calibration端口，缺setup不得触发005。正常事件/状态沿§5.2/6的Created→Validating→Accepted→Running→Draining→Drained→ResourcesReleased→Completed；期间Stage固定AcquireFrames/AcquireWhiteSurface/GenerateLayout/Decode/CopyCorrespondences/Encode/Release，诊断回调异常隔离记录、不影响真实lease归还。单实例只存原一个作业，Query/Stop的未知ID为016/Rejected/NotStarted/Result=null，不停止当前原作业；Query在Dispose后仍只读/无IO，旧快照不可变。

Frames、Sequence.Patterns、AcceptedMappings/Probes非default ImmutableArray；Pattern.OrderedPatternIds及Acquisition.Frames在本新入口须实际为boxed ImmutableArray（类型/IsDefault先于Count/自定义getter），其余字符串/record深复制。只提交immutable规范图，禁止Unsafe/MemoryMarshal重写共享存储。Auxiliary.Black/White恰指Sequence对应原Black/White帧（各一，不额外Acquire），WhiteSurface尺寸/组/epoch/ParentWhiteRevision精确绑定White；DerivationRevision明确原producer白面域方法，非null，不能由IM-032按亮度猜“白面”。mask源唯一，格式固定每pixel 0/1 UInt8，stride规则同帧。

Acquisition沿§4.2.1逐帧12字段、原ordinal/PatternId/曝光revision、同attempt/同步clock/epoch/静止证据核对；Evidence.CaptureGroupId=请求原组、Evidence.CaptureEpoch=Acquisition.CaptureEpoch，每FrameTiming.ClockDomain=Evidence.ClockDomain，mask.ClockEpoch=Evidence.ClockEpoch。CaptureEpoch与ClockEpoch各是原Owner事实，不强行等同/重命名。CaptureGroupId及InputRevision是原捕获Owner核验的同组快照，不由本模块用相等名字造证据。Evidence.StableStartNs≥0、End>Start，每帧图案稳定窗/曝光完全在组稳定窗；组StableEvidence/QualityEvidence为可核原引用，SceneStationaryVerified只配合原证据。CaptureSkew精确等于最晚曝光中点−最早中点（以整数ns/100转TimeSpan tick，不能整ms截断；半ns情形用checked两倍ns比较并向上至100ns）；MaxCaptureSkew/MinStableWindow正且≤30min，CaptureSkew≤MaxCaptureSkew、稳定窗长度≥MinStableWindow，来源TimingProfile明确阈值。不同clock不计算差；不成立R3D-021。Timeout100ms..30min、DrainTimeout1..60s、Deadline最早单调规则沿§5/9；一次受控采集后解码，不在线重新投影/重拍。

#### 7.6.2 DirectionMapping：不承诺数组顺序，冻结可判定映射

Mapping Version=`r3d-direction-mapping-v1`，Reference.Sha256为§7.6.4正文编码hash；它是解码部署/生成布局映射，不是内外参/质量资格。单作业factory的AcceptedMappings限0..1项（非default），正文≤65536bytes、Probes≤256，Create只做类型/数量/字段硬限与限额复制；空目录允许构造并在Validate准确007，非法目录形状在Create ArgumentException。请求只引用完整mapping revision，factory快照唯一定位正文；State=Accepted、两个Evidence bool=true才可消费，Candidate/Withdrawn/未登记为R3D-007/DirectionMappingNotAccepted；hash不符002、Runtime/Profile/Manifest/双方W/H或Origin不符015，形状合法但Golden不唯一/与显式ordinal不符002。AcceptedMappings由部署/解码Owner在创建前核Golden原件和接收记录后展开；Core验证正文/hash/证明值一致，不以self-declared Accepted代替外部原件核验，两个bool不是安全授权或物理证书。单一目录快照及其编码临时计入262144-byte控制预约，不缓存其它mapping或靠全局可变注册表。

HALCON object ordinal用**1起始**的select_obj索引，ColumnObjectOrdinal/RowObjectOrdinal分别必须是{1,2}的一种排列。只把已核ColumnOrdinal对象标Vertical/projector column，RowOrdinal标Horizontal/projector row；不写死array[0]是列，不从本次板面的“更像水平梯度”推断，也不翻转、交换row/col单位或做+0.5修正。

校验优先序固定为：非法enum/ordinal排列、probe数量/重复/共线/越界/非有限、非法MaxErrorPixel先001；Version不符015；正文hash不符002；未登记/非Accepted/任一Evidence bool为false或SupportsBoth=false为007；Runtime/Profile/Manifest/双方尺寸/Origin不符015；其余合法形状的probe不满足指定排列或不能排除交换排列为002。均在Acquire/native前拒绝，不能因坏证据转而猜另一排列。

公开Golden证明字段已在DTO冻结：CameraWidth/Height、ProjectorWidth/Height、与本decode相同Runtime/Profile/Manifest、GoldenEvidence以及3..256个Probes，(CameraRow,Column)唯一且在原camera域；至少三个camera点非共线。每个Probe保存**独立已知投影器row/column**与get返回Object1/Object2原域内值，四double有限，预期row∈[0,PH)、column∈[0,PW)。MaxErrorPixel的纯软件数值有效域为有限且≥0的binary64（排NaN/±Inf/负数、-0规范+0）；绝对误差非负且运算/编码要求有限是此有效域的依据，不另设经验上界或真实精度默认值。具体容差由部署Owner已接收的Golden计划给出，并与GoldenEvidence原件一致；软件夹具固定0。按两个显式ordinal选择Object值，与预期两坐标逐probe比较abs误差≤MaxErrorPixel；同时反向排列至少一个probe在任一坐标误差>MaxErrorPixel，才能排除对称/重复数据。有限输入相减若溢出，误差必大于任何有限容差，按不满足处理、不封存Inf。容差再大也不得跳过交换排列排除；只有一组排列可以满足。Core做此有界一致性检验，**不替换**请求的显式ordinal，不把方向唯一性检验容差用作真实标定/解码精度验收，不把“软件检验通过”发布为native Golden已运行。

不对称oracle见§7.6.6：PW12/PH8、camera3×2，三个probe(0,0)=(row1,col3.25)、(0,2)=(2,8.5)、(1,0)=(5,4.75)。Host A返回Object1=column/Object2=row，映射Column1/Row2；Host B反序返回Object1=row/Object2=column，映射Column2/Row1。两者必须交同一具名结果，错误映射、同ordinal、方形/对称且两种排列都能过的假证明均在源前拒绝。非方形、非整数及非共线坐标可捕获轴交换/转置；需检测镜像/偏置时Golden原件还要含边界和翻转反例，不能由此合成oracle证明真实camera/projector坐标关系。

真实mapping证据生成路线已定：同一实际部署/完整manifest，用无setup的本节HALCON链读取两个**未命名**correspondence，记录原对象1/2、各自domain和独立已知投影器坐标不对称测试；部署Owner比较两种排列，仅唯一排列满足原Golden计划时签收上述mapping。测试和产线解码均禁止估内外参来制造mapping truth。26.05 operator正文及HDevelop Example证实create→gen→decode→get可以先于重建/标定；Example本身为deflectometry，仅说明解码先后，不授权该模式或数组索引。已锁OpenCV4.12.0 `test_getProjPixel.cpp`实际测试在1024×768遍历，分别断言projPixel.y==row、x==column；复用其独立坐标oracle思想，不能把OpenCV布局或无噪声identity当HALCON对象顺序/真实光学精度。原源码hash/依赖/许可/未运行限制沿§19.2，不复制测试实现或引新runtime。

#### 7.6.3 固定处理、CAL-JC字节形状和资源所有权

执行步骤唯一为：值/证据/mapping/预算/部署能力预检→按原ordinal逐帧Acquire、核Descriptor/stride/原Bytes hash并限额复制自有snapshot→取得white-surface mask lease、核完整引用/父White/0或1字节并复制→adapter在独占model中create('3d_reconstruction')→set尺寸/HybridBoth/global/stripe/min_gray_difference/persistence=false→gen原布局、逐对象hash/role核对→整组原序decode→get('correspondence_image')取两对象→逐对象get_domain/原相机有限值限额复制→清所有native/get/生成对象→Core按已核mapping命名/编码/全校验→按逆序唯一归还mask/全部frame原lease→Released后原子交结果。没有set camera_setup/reconstruct/find_calib_object/fit/cv2测量、假setup或设备命令；原重建Adapter可复用同一私有decode session/复制实现，再做自己的标定重建后段，禁止包装新ReconstructionFactory当decoder或重复另一套视觉算法。

Raw Correspondences恰两对象，ObjectOrdinal恰1/2，无增删；每个W/H原camera、Domain/Values各N、域外null/域内有限，SupportUnion长N且逐pixel等于两个原domain的OR。该字段是可重算的支持投影，一致性核对后才接纳；CAL-JC不需要额外读取Both pattern_region并猜其对象排列。复制算子/runs/4096-pixel批/单通道/get_grayval忽略domain的防护沿§4.4.1；不crop、warp、降采样、插值/补洞，不套world变换。Core按映射核row在[0,PH)、column在[0,PW)，域内越界或shape/hash/runtime错误为024（operator故障013）；不把不合理坐标截回范围。允许两原domain不同，共同valid=RowsDomain AND ColumnsDomain；不把white-surface mask强加到原decode域，不把黑圆的domain空点补值。全共同valid=0时仍可Completed、结果mask全0并保留原对应/原图；只说明本次没有共同支持，CAL-JC另按采样/资格拒识，解码器不发PASS/Qualified。Raw ResourcePeaks只接受NativeBytes键及非负值且≤Native预算；返回Result字典固定五个键InputBytes（实际全部原lease最大驻留bytes）、ManagedReservationBytes（本节预约上界）、NativeBytes（adapter账本原native峰值）、PayloadBytes（八raster实际22N bytes）、ResultReservationBytes（本节结果预约），不把预约数称GC/native实测峰值。WhiteSurfaceSource完整等于Aux.WhiteSurface，结果保留其来源/父White/Derivation，不仅保一张匿名mask。

`DecodeRaster`只含独立ImmutableArray<byte>、尺寸/固定format和原载荷SHA256。ProjectorRows.Axis=Horizontal/Column.Axis=Vertical，Coordinates.Format=`projector-coordinate-f64le`，恰8*N bytes；逐row-major IEEE754 Float64LE，域内保留原有限值、-0规范+0，域外使用唯一quiet-NaN位模式`0x7ff8000000000000`（LE `000000000000f87f`）。它仅是mask=0的空值编码，不是观测坐标，绝不置0或把NaN作为DTO数值/有效点。每层Domain、ValidMask、WhiteSurfaceMask.Format=`valid-mask-u8`/N bytes、每byte0或1；BlackImage/WhiteImage.Format=`image-gray8-rowmajor`/N bytes，无padding/normalize，CameraImage由CAL-JC宿主直接复用WhiteImage同ContentRef，不另造一图。两层独立域可保留只在一个axis可观测的原值；CAL-JC支持只有共同valid=1时读取两层并要求有限，在其它位置忽略qNaN，不能把未知值判0误差。白面mask从原producer取得并原样封存，不能由decoder造平面/材质/中心资格。

公开桥逐字段：JointGroup.CaptureGroupId/ClockEpoch/Evidence/原曝光窗来自DecodeRequest；JointPattern.Manifest/DirectionMapping/Decoder分别绑定实际Sequence.ManifestRevision、本文mapping正文原件及Backend.Info真实部署（ContentRef/JointAdapterVersion由原Owner按已接收类型展开，RevisionRef不编码路径/Format/ByteLength，不能自己猜）；ProjectorRows/Columns、ValidMask、White/Black/WhiteSurface六个payload按上述format/checked字节长度/SHA由宿主原内容Owner封存，Rows/Columns原域mask另保留原证据。CameraImage=WhiteImage。宿主封存mapping正文format=`r3d-direction-mapping-v1`，其hash=Reference.Sha256；JointPattern.DirectionMapping引用该原件，不用只保存一对indices的私造内容。Joint观察Points/白区环带/实测证书/PhysicalEvidence仍由CAL-JC/原producer执行，IM-032不输出伪点/Joint DTO/候选资产。Origin=Simulator永不映入生产Joint用途；只给CalibrationReplay/合成验证。首次初始化流程因此是采集→Decode→封存观测→CAL-JC Solve/Validate/Publish→既有重建消费setup，软件接口不依赖先验setup。

预算显式：Managed/Native/Result各64MiB..8GiB，MaxInputBytes1..8GiB，MaxPixels1..16,777,216、MaxFrames1..256、MaxRowStrideBytes≥W且≤Int32.MaxValue。预检N=checked(W*H)、G=checked(PW*PH)同像素上限，F完整manifest数；`checked((F+1)*MaxRowStrideBytes*H)≤MaxInputBytes`（mask也计），至少(F+1)*N。每lease实际stride在[W,maxStride]、Bytes.Length恰stride*H，不接受超尾随载荷；hash核整个原payload含padding，取像素另去padding。Managed预约`checked(4*MaxInputBytes + 192*N + 8192*F + 1024*Probes.Count + 262144)`，Result预约`checked(22*N + 8192*F + 1024*Probes.Count + 16384)`；包括两原Nullable plane、native复制scratch、snapshot/编码/不可变结果/来源、hash临时及有限事件，不依赖仅16N的float估计。Source原lease字节属于来源Owner，但本作业驻留账本仍计其借用量；所有额外复制计入峰值，超限010、不丢层/补默认/放大父预算。Native按已测部署Info `fixed + F*N*CameraCoeff + F*G*PatternCoeff` checked预留；真实Info EngineVersion=26.05/SupportsBoth=true、Envelope来源/hash可核、fixed≥0/coeff>0，未知/不足010或007，不猜内部公式；Simulator系数/fixed全0/EngineVersion=Synthetic/1，实际Native0，不伪称真实envelope。事件/历史只保一作业及256个事件，结果Query限64MiB，超限只原回执交Result，Query保终态/Released但Result=null和016/ResultNotRetained，不能改作业Unknown。

Core是frame/mask原lease唯一Owner；adapter只借**自有immutable snapshots**，不调用源第二次/不Dispose宿主原lease，native所有权仍独占adapter。账本在调用源/adapter/Dispose之前预留任务位置，原Task立即强持，不能只持WaitAsync；容量固定524，包括≤257 Acquire、≤257 lease Dispose、1 Execute/1 adapter-stop及≤8 clock/drain观察Task，不无限重试/重新Dispose。迟到Acquire立即登记late value：停止后不启动decoder，等原调用真实结束再唯一归还；mask/descriptor校验失败也保lease直至清理。Cancellation/Deadline沿§9首次停止意图、Timeout同观察优先、停止新Acquire/get/copy，进行中的native/复制真实退出后再归还。失败/取消不交未完成结果，DrainUnknown一律Result=null；Stop观察令牌取消只取消观察，不能取消后台归还。StopAndDrain每实例一个底层停止pipeline，重复调用只是有限观察，Dispose同一底层关闭Task；R3D-014/Unknown时保持原Root/Info/mapping/snapshots/所有lease/原Task，不建第二实例绕过。所有任务故障需观察异常；ActiveNative/Callbacks=0且所有内层Task/lease已归还才Released，原外层run/stop/dispose退出仍由Host另核，State不代资源真实结束。

真实公开装配在既定`Asun.Modules.Reconstruction3D.AsunImage.dll`/A.1的AsunImage工程`Decoding/`追加公开`Asun.Modules.Reconstruction3D.Adapters.Decoding.StructuredLightDecodeAsunImageFactory`：无参构造，`IStructuredLightDecodeAdapter Create(DecodeBackendInfo deployment)`；只校验冻结部署/envelope配置、无native/设备/工作，非法配置ArgumentException/null为ArgumentNullException。Core装配为`new StructuredLightDecodeFactory().Create(new DecodePorts(frameSource,maskSource,adapter,acceptedMappings,clock,diagnostics))`，没有CalibrationAssets/DI。公共C# cv2/tuple重载在本Adapter消费编译后确认，不另接halcondotnet.dll、不检查AsunImage内部；真实get Both对象数/域/Golden与native envelope/fault/取消需R3D-Decode-A1验收，不把已知算子能decode说成运行通过。

真实部署Owner须把RuntimeRevision和NativeEnvelope绑定到实际运行部署及其已测原件；Adapter在首次Execute分配model前核实际运行身份与冻结Info一致，不符015。Create只验证声明形状，不把调用方自填26.05/SupportsBoth=true或envelope系数视为实测或能力证明；此核对使用部署证据与公开运行信息，不扫描AsunImage内部，不做依赖安装或许可审查。

#### 7.6.4 固定编码和身份（唯一字段顺序）

primitive沿§4.4.1：严格UTF8字符串U32LE字节数+bytes，bool/enum U8，int I32LE、long I64LE、double binary64LE（-0→+0，语义数值NaN/Inf拒绝），revision依Id/Sha256字符串，小写hash；TimeSpan为I64LE ticks，DateTimeOffset为I64LE UtcTicks，nullable先U8存在标志。ImmutableArray先U32LE count再原序项，所有长度checked/硬限先于分配。不用JSON/反射/字符串插值hash。下面均为唯一公共`StructuredLightDecodeCodec`（无参构造），`ImmutableArray<byte> EncodeMapping(DecodeDirectionMapping mapping)`、`string HashRequest(DecodeRequest request)`、`ImmutableArray<byte> EncodeResult(DecodeResult result)`；非法形状ArgumentException、null ArgumentNullException；编码前按上述有效域/预算检查，不启动工作。HashRequest流式hash、不把整个payload无界缓存；可核规范字节按以下规则重建。

| 域 | 固定头和完整正文（按声明顺序） |
|---|---|
| Mapping | ASCII R3DM、U16LE=1；Version、Reference.Id（排Reference.Sha256自身）、RuntimeRevision/PatternProfile/ManifestRevision、CameraW/H/ProjectorW/H、ColumnOrdinal/RowOrdinal、State/Origin、GoldenEvidence、MaxErrorPixel、Probes各CameraRow/Column/ProjectorRow/Column/Object1/2；hash=Reference.Sha256。所有成员不删Evidence/State，不能只hashindices |
| Request | ASCII R3DR、U16LE=1；DecodeRequest声明顺序全部字段。Frames每项按原FrameRef声明顺序：FrameId/Revision/Kind/W/H/PixelFormat/AcquiredAt UTCticks/SequenceOrdinal/DirectionId/nullable PatternId/ExposureProfileId；Pattern按原PatternSpec Profile/Route/PW/PH/MinStripe/nullable SingleStripe/Normalization/MinGrayDiff/CapturePhaseDiagnostics/OrderedPatternIds，再Sequence存在标志1及其Version/ManifestRevision/Patterns各PatternId/ordinal/Kind/Axis/RoleOrdinal/nullable PhaseIndex/GeneratedPatternSha256，Diagnostics存在标志固定0；Acquisition按CaptureEpoch/TimingProfile/MaxSequenceSpan/MaxStereoSkew/SceneStationaryVerified/Frames各12字段声明顺序；Evidence按本节声明；DirectionMapping完整revision；Aux按BlackFrameId/WhiteFrameId/WhiteSurface全部声明；Budget七字段；Timeout/DrainTimeout/nullable Deadline；RequestSha256为此正文SHA256，排结果/自身hash |
| Result | ASCII R3DO、U16LE=1；DecodeResult全部字段依声明。SourceFrames编码同Request；每CoordinatePlane依Axis/ObjectOrdinal/Coordinates/Domain；Raster依Format/W/H/Bytes(count+原bytes)/Sha256；ResourcePeaks按StringComparer.Ordinal键递增写count/key/value I64LE。Result包括RequestSha256、mapping/runtime/源和全部payload，不把生产内容Owner身份编进内部返回。每Raster.Sha256只hash原Bytes（无此正文头），空/长度错误/尾随非法编码拒绝；浮点影像qNaN是byte载荷，不能通过通用double编码当作语义值 |

EncodeMapping为构造正文只检查Reference.Id及其它声明字段，不核排除的Reference.Sha256与正文相等；调用方先Encode/SHA，再填该Sha，factory/Validate在消费时核完整hash，避免生成自身hash的循环。HashRequest先做请求独立形状/数量/预算校验，AcceptedMappings/实际部署适用性只由服务Validate判定；EncodeResult逐Raster/域/来源/固定键核合法，但不启动源/事务。CAL-JC六个payload的SHA原形固定，Request/Mapping/Result各域不自引用。Result codec用于两Host直接比较/保存本模块Replay，CAL-JC只封存已接受的payload/元数据，不把R3DO envelope冒成cp-joint-observation-v1。层域/格式/单位/关联均保持，跨Owner封存后的ContentRef身份由宿主原Owner给出；payload和mapping的FormatRevision=1，Manifest/部署原资产的Format/Revision/ByteLength仍按原Owner信息保留；本节不建立第二Store或提交协议。

#### 7.6.5 发布Simulator增量与有限关闭

类型仍在既有Simulator包/namespace，using Core `.Decoding`。原`ReconstructionSimulationFactory.Create`/ScriptVersion和原脚本/枚举值保持；同一公开无参factory追加常量`DecodeScriptVersion="r3d-decode-simulator-v1"`及`IDecodeSimulation CreateDecode(DecodeSimulationScript script,IReconstructionClock clock,ISimulationGates gates,IReconstructionDiagnostics diagnostics)`、`SimulationScriptValidation ValidateDecode(DecodeSimulationScript? script)`。没有第二模拟DLL/私有测试stub依赖。

```csharp
public sealed record DecodeSimulationScript(string Version, string ScriptId, ulong Seed,
    DecodeRequest Request, ImmutableArray<SimulationFrame> Frames,
    DecodeWhiteSurfaceRef MaskReference, int MaskRowStrideBytes, ImmutableArray<byte> MaskBytes,
    DecodeBackendInfo Backend, DecodeDirectionMapping Mapping,
    ImmutableArray<DecodedObjectPlane> RawObjects, ImmutableArray<bool> SupportUnion,
    ImmutableArray<SimulationStep> Steps, ByteCount MaxSnapshotBytes);
public interface IDecodeSimulation : IAsyncDisposable {
    DecodePorts Ports { get; }
    DecodeRequest Request { get; }
    RevisionRef SyntheticRevision { get; }
    SimulationSnapshot Query();
    ValueTask<SimulationStopReply> StopAndDrainAsync(TimeSpan waitBudget,
        CancellationToken token = default);
}
```

新SimulationPoint追加MaskAcquire=9、MaskRelease=10（原FrameAcquire0/CalibrationAcquire1/SurfaceAcquire2/DirectionExecute3/TransformExecute4/CallbackExit5/FrameRelease6/CalibrationRelease7/SurfaceRelease8保持）；旧重建脚本明确拒绝9/10为SIM-004，不更改旧行为。Decode脚本仅FrameAcquire/FrameRelease、MaskAcquire/MaskRelease、DirectionExecute和CallbackExit；DirectionExecute.ResourceId=Request.DirectionId，CallbackExit为DirectionId+"/decode"，mask resource=MaskReference.SourceId，frame resource=FrameId，不接受Calibration/Surface/Transform步骤。Continue/Reject/Fail/Observe/CompleteLate、NotBefore0..60s、≤128steps/≤32gates/256events、事件enum0..13与有限clock/gate沿§13.4/5。FrameAcquire Reject只003、MaskAcquire只024、DirectionExecute只007/024，Fail只013；各种释放/Callback仅Continue/CompleteLate，不能注入伪释放成功。

Source端口只按冻结Request逐ordinal提供每个frame一次、mask一次；第一匹配Acquire绑定本script单作业，不靠原重建adapter的ambient context/隐藏初始化。直接调用这些公开source取得的lease亦归调用者，Root仍跟踪，重复取得R3D-023、不改原lease；正常Core为唯一消费者。Execute只核14等完整snapshot绑定并返回RawObjects/SupportUnion明示值，不跑gen/decode、不根据Byte亮度/seed改变对应、不需要fake标定字节。Backend.Origin=Simulator/EngineVersion=Synthetic/1/coeff全0，RuntimeRevision=SyntheticRevision；Mapping同runtime/origin/manifest且Accepted，Golden只为本脚本软件oracle。SyntheticRevision.Id="synthetic:"+ScriptId、Sha256=SHA256(UTF8(DecodeScriptVersion+"\n"+ScriptId+"\n"+seed InvariantCulture))，ScriptId≤96；它非脚本全文hash，完整输入由Request/Mapping/Result codec及原script保留，不能当物理Golden。

CreateDecode成功后，Ports.Frames/Masks/Decoder绑定同一个script根，Clock/Diagnostics为调用方原注入引用，AcceptedMappings固定为单项`ImmutableArray.Create(new DecodeAcceptedMapping(Mapping,true,true))`。两个true仅表示已核本synthetic正文及软件oracle，受Simulator Origin隔离，不产生真实Golden接收记录；真实装配仍由部署Owner提供其已核映射目录。

PrepareSnapshot仍一次：全部immutable类型/数量门→checked预算→限额复制同一图→在规范快照上核源Bytes/hash/绑定/Mapping正文和probe/形状→Create保留同一快照；default集合SIM-001、身份/hash/缺层/shape/域不符SIM-002、预算SIM-003、不支持步骤/版本能力组合SIM-004。语义version不符SIM-001；Native实际始终0。Raw对象各N≤4096、2N≤8192，全部帧字节≤8MiB、MaxSnapshotBytes1..16MiB；新baseBytes固定`Σ所有Frame.Bytes.Length + MaskBytes.Length + 35*N + 8192*F + 1024*Probes.Count + 16384`，result/managed峰值保留`4*baseBytes+524288`，同时须≤MaxSnapshotBytes/请求Managed/Result。35*N覆盖两个nullable double/domain原对象及SupportUnion；四倍覆盖冻结/lease/snapshot/adapter回执与编码临时，禁止无预算缓存。Query旧Events/计数跨late/gate释放不变；Byte/Domain/Values/返回嵌套集合只含immutable快照。Mask来源/Derivation/ParentWhitehash原样，不把script复制值解释成material证书。

Host根沿§11/13.6容量2、factory前Reserve；本切片槽的公开内部操作为`AttachDecode(IStructuredLightDecoder)`、`AttachDecodeSimulation(IDecodeSimulation,IReconstructionClock,ISimulationGates)`、Track/Work/RecordOutcome/Release原语，最多五原Task(run/core-stop/core-dispose/sim-stop/sim-dispose)。恢复接收内部形状`RetainDecode(IDecodeSimulation? sim,IStructuredLightDecoder? decoder,DecodeRequest identity,IReconstructionClock clock,ISimulationGates gates,IReadOnlyList<Task> originals)`；正常返回才移交确认，原槽/容量不提前退，接收throw仍原Owner强持。CreateDecode与Core Create纯校验，不开始工作；任何factory失败仍有限关闭已创建sim。各Task/引用在发调用前有槽，调用返回后立即Track原Task，不保WaitAsync包装；模块的Decode/Stop/Dispose ValueTask均由同底层cached Task支持，重复Close不创建第二释放pipeline。

有限finally逐对象捕获：先保首业务错误/exit，decoder.StopAndDrain(100ms虚拟budget)原Task真实观察≤1s；只有Released且原run真实退出/已观察故障才发decoder.Dispose原Task真实观察≤1s；然后sim.StopAndDrain(100ms)与sim.Dispose各原Task观察≤1s，核两个根所有active/pending/lease=0且Acquired=Released。所有清理均独立catch，不覆盖业务2/3/4；业务0而cleanup未知/错则5。五原Task真实退出、两个Root资源Released且无cleanup错才0；未决/释放异常不退槽，RetainDecode仅移交引用不声称资源释放。迟到gate放行后原Acquire/Callback/Dispose pipeline继续，复用同Stop/Dispose原Task做有限观察并更新Query，确认真实Released后才退容量，原业务错误不改。faulted lease.Dispose不能证明归还，保持Unknown并由原来源Owner处理；不再次调用同lease.Dispose冒称恢复，不用sim.Copy完成/Native0当证明。

#### 7.6.6 两个全字段Synthetic Host与规范oracle

两个消费者沿既有Simulator.Tests的A（structured-light共同标定producer）和B（离线共同观测工具），不建新工程。每case各fresh roots，Clock=`new SimulationClock(new DateTimeOffset(2026,10,11,0,0,0,TimeSpan.Zero))`/Timestamp0，Gates=`new SimulationGates(ImmutableArray<string>.Empty)`、独立diagnostics。以下`rev(id)=RevisionRef(id,SHA256(严格UTF8(id)))`，所有列表为ImmutableArray/字典Ordinal ImmutableDictionary，nil只在注明项；固定seed7。这些值不是HALCON真实布局/光学真值，不交Native/生产Joint。

| 完整字段组 | Host A | Host B |
|---|---|---|
| script/identity | Script.Version=r3d-decode-simulator-v1/ScriptId=decode-A/Seed7，Request.Version=r3d-decode-v1，OperationId=decode-A-op/CalculationId=decode-A-calc，AuthorityScope=fixture-only，CaptureGroupId=capture-A/DirectionId=A，InputRevision=rev(input-A) | Script.Version/Request.Version同A；decode-B/seed7、decode-B-op/decode-B-calc、fixture-only、capture-B/B、rev(input-B) |
| Frames（14项） | FrameId=A0..A13/Revision=RevisionRef(FrameId,SHA256(实际source bytes))、Kind/PatternId按下表，W3/H2/Mono8、AcquiredAt=t0+ExposureEndNs/100 ticks、ordinal0..13、DirectionId=A/ExposureProfileId=exp-A；RowStrideBytes3、每帧6bytes下表 | B0..B13、DirectionId=B/exp-B，其它同A；stride5，每row原3pixel后padding[99,88]，总10bytes/hash包含padding |
| Pattern（原字段+Sequence） | Profile=rev(pattern-A)、HybridBoth/PW12/PH8/minStripe4/single=null/global/minGrayDiff10/CapturePhaseDiagnostics=false、OrderedPatternIds按表；Sequence Version=r3d-sl-sequence-v1/Manifest=rev(manifest-A)/14完整binding。Diagnostics=null | rev(pattern-B)/rev(manifest-B)，其余同A |
| Acquisition（六字段/完整timing） | CaptureEpoch=epoch-A/TimingProfile=rev(timing-A)/MaxSequenceSpan1s/MaxStereoSkew0/SceneStationaryVerified=true；每FrameTiming(FrameId,attempt-A,epoch-A,device-A,clock-A,ExposureStart=i*10000+1000,End=i*10000+2000,StableStart=i*10000,End=i*10000+3000,rev(exp-A),ExpectedOrdinal i,ExpectedPatternId表值) | epoch-B/rev(timing-B)，attempt-B/device-B/clock-B/exp-B；同公式 |
| Evidence（全部字段） | StableEvidence=rev(stable-A)/QualityEvidence=rev(quality-A)/capture-A/epoch-A/clock-epoch-A/clock-A，StableStart0/End200000ns、CaptureSkew1300ticks=130µs、MaxCaptureSkew10000ticks=1ms、MinStableWindow2000ticks=200µs | refs/group/epoch/clock标识均换B，其余同A |
| Auxiliary/原mask源 | BlackFrameId=A0/WhiteFrameId=A1，WhiteSurface=DecodeWhiteSurfaceRef(mask-A,RevisionRef(mask-A,SHA256([1,0,1,1,1,1])),3,2,capture-A,clock-epoch-A,原A1.Revision,rev(white-surface-A))；MaskStride3、bytes[1,0,1,1,1,1] | B0/B1、mask-B同6原byte，ParentWhite=原B1.Revision/rev(white-surface-B)，stride3不padding，其组/clock换B |
| Budget/timeout | DecodeBudget(67108864,67108864,67108864,1024,96,16,5)、Timeout1s/Drain1s/Deadline=null | 同A；没有Calibration/Setup字段；MaxPixels96同时覆盖camera N6与projector G96 |
| Backend（八字段） | RuntimeRevision=synA（下文），Origin Simulator/EngineVersion Synthetic/1/SupportsBoth true/NativeEnvelope=rev(envelope-A)/Fixed0/CameraCoeff0/PatternCoeff0 | synB/envelope-B，其余同A |
| Mapping（全部字段） | Version=r3d-direction-mapping-v1/Reference=(mapping-A,正文SHA)/Runtime=synA/Profile=rev(pattern-A)/Manifest=rev(manifest-A)/camera3×2/projector12×8/ColumnOrdinal1/RowOrdinal2/State Accepted/Origin Simulator/GoldenEvidence rev(golden-A)/MaxErrorPixel0/三probe如下 | mapping-B/synB/原B Profile/Manifest/golden-B，Column2/Row1、其余同A，probe Object1/2互换 |
| raw decoder | object1列/object2行；各W3/H2、Domain=[1,0,1,1,1,1]、Values见下表，SupportUnion同此domain；Runtime=synA/ResourcePeaks仅NativeBytes→0 | object1行/object2列；Domain/命名值相同、Runtime=synB |
| script剩余字段 | Request完整以上值/DirectionMapping=Mapping.Reference，Frames14 SimulationFrame(A,完整ref,stride3,原bytesImmutable)，MaskReference/stride/bytes按表，Backend/Mapping/RawObjects/SupportUnion按表，Steps.Empty，MaxSnapshotBytes2097152 | 14 SimulationFrame(B,完整ref,stride5,含paddingbytes)，其余B对应值/Steps.Empty/2097152 |

synA/synB精确为RevisionRef(`synthetic:decode-A/B`,SHA256(UTF8(`r3d-decode-simulator-v1\ndecode-A/B\n7`)))，实际字符串按A/B选一个、不含斜线。Mapping.Reference.Id分别mapping-A/B，先按§7.6.4 EncodeMapping排自身Sha构造正文，再填Reference.Sha256；Request方向ref随后绑定，不自引用。

| PatternId / ordinal | Kind/Axis/RoleOrdinal/PhaseStepIndex | 原camera 3×2 pixels（row-major） / synthetic投影器12×8 |
|---|---|---|
| black / 0 | NormalizationBlack/None/0/null | 全10 / 全0 |
| white / 1 | NormalizationWhite/None/0/null | [180,20,180,180,180,180] / 全255 |
| vg0 / 2 | GrayCode/Vertical/0/null | 全60 / column<6为0否则255 |
| vg1 / 3 | GrayCode/Vertical/1/null | 全90 / floor(column/3)偶数0奇数255 |
| vp0..vp3 / 4..7 | PhaseShift/Vertical/j/j（j0..3） | 全[70,100,130,100]中的第j值 / 全[64,128,192,128]中的第j值 |
| hg0 / 8 | GrayCode/Horizontal/0/null | 全60 / row<4为0否则255 |
| hg1 / 9 | GrayCode/Horizontal/1/null | 全90 / floor(row/2)偶数0奇数255 |
| hp0..hp3 / 10..13 | PhaseShift/Horizontal/j/j | 同Vertical对应第j值 / 同第j值 |

每binding.PatternId/SequenceOrdinal=表值，GeneratedPatternSha256=该synthetic投影器96个byte的SHA；非phase PhaseStepIndex=null。generation/phase constant图只验证元数据/脚本软件协议，不是实际gen图/四步相位正确性证据。14原帧均保SourceFrames，mask单独归还。

| 不对称probe | 预期projector(row,column) | A(Object1,Object2) / B(Object1,Object2) |
|---|---|---|
| camera(0,0) | (1,3.25) | (3.25,1) / (1,3.25) |
| camera(0,2) | (2,8.5) | (8.5,2) / (2,8.5) |
| camera(1,0) | (5,4.75) | (4.75,5) / (5,4.75) |

具名Rows.Values=[1,null,2,5,6,7]、Columns.Values=[3.25,null,8.5,4.75,9.25,10.5]；两Domain/共同Valid均[1,0,1,1,1,1]，CameraImage/White/Black/WhiteSurface分别原White同引用/[180,20,180,180,180,180]/全10/[1,0,1,1,1,1]。两Host数值/六payload byte/hash必须相同，metadata/mapping/Request身份不同；native0、取得/归还=14frame+1mask=15，mask不算标定lease。Result各八raster（两coordinate/两domain/valid/black/white/white-surface）22N=132bytes；不把metadata预算128000等当实际裸payload大小。

Result其余全字段：OperationId/CalculationId/RequestSha256及Input/CaptureGroup/ClockEpoch/Origin/Runtime/Mapping/Manifest/Stable/Quality/SourceFrames逐项原请求/冻结Info；WhiteSurfaceSource=原Aux.WhiteSurface。A Rows.ObjectOrdinal2/Columns1，B Rows1/Columns2，Axis分别Horizontal2/Vertical1、Coordinates/Domain按§7.6.3。ResourcePeaks五键为InputBytes A90/B146、ManagedReservationBytes385152、NativeBytes0、PayloadBytes132、ResultReservationBytes134276，Ordinal排序。新Simulator脚本预约A1062064/B1062288 bytes≤各2097152，source原payload按padding计、输出payload无padding；这一独立账本复算不代真实GC/native性能测量。

以下为从上述全字段独立构造的**文档oracle**。六payload与Mapping/Request/Result均无额外尾随字节/JSON，不是产品或HALCON运行结果；DC01必须逐字段独立重建预期，不能从受测codec生成自己的expected。

| A/B共同payload | 长度 / SHA256 | 全部原hex |
|---|---|---|
| ProjectorRows | 48 / `533ad483e0d95c9ba7c8f24f6b43edd30e5da92176a9ad22a546d8d820658ea3` | `000000000000f03f000000000000f87f0000000000000040000000000000144000000000000018400000000000001c40` |
| ProjectorColumns | 48 / `c7a87a3eb413be436b30e689cb5af34abfdabe0527661af178d6dd9af9741aa1` | `0000000000000a40000000000000f87f0000000000002140000000000000134000000000008022400000000000002540` |
| ValidMask/Rows.Domain/Columns.Domain/WhiteSurfaceMask | 各6 / `720f38c53dc2c0bd04f77ab4f1e2876b59a4c2db97c8fb75758818b6d73919b5` | `010001010101` |
| WhiteImage/CameraImage同引用 | 6 / `624ac66d2c910888d60cf0fc5b319dea10d1c4023c72d2ad214cf631b2bc8fd8` | `b414b4b4b4b4` |
| BlackImage | 6 / `d088784b7ecb87f1ea17e6f982fa968ffefcc07b79de6ecc548fc00242868da6` | `0a0a0a0a0a0a` |

| 全字段域 | 规范byte长度 / SHA256 |
|---|---|
| A Mapping | 538 / `dc9152e2e2ced0b73fedf378396daf59967d193eced9ca6c7986fed06ed53018` |
| B Mapping | 538 / `b7d3d250ce33394948603cfd5d7b60de00decf8584fcfc5eca23d6d345c3e812` |
| A Request | 6894 / `a3101d8f63b4d0c516c84b2a7ecf0bbbe75d7e77046030ae83802510c5d59cfc` |
| B Request | 6894 / `56bbf21246c6f730d813780b60cec03a5875297e1a53c4c64f61ac33ab6a26a6` |
| A Result | 3895 / `8f872e3f109e834dbb0b94897a0cda8fbfb2535c46f02dc376f4cafd19098d01` |
| B Result | 3895 / `234ab2c9351332b476b30b9cab55643ff922379a3beefc574e9c983a0d3f905e` |

无UI实际调用形状：各根先预留容量槽→`var sim = new ReconstructionSimulationFactory().CreateDecode(script,clock,gates,diagnostics);`立即AttachDecodeSimulation→`var decoder = new StructuredLightDecodeFactory().Create(sim.Ports);`立即AttachDecode→`decoder.Validate(sim.Request)`→`Task<DecodeReply> run=decoder.DecodeAsync(sim.Request).AsTask();`立即Track→`await run.WaitAsync(TimeSpan.FromSeconds(3))`→核Completed/Released、原SourceFrames/Runtime/Mapping/Request hash、上述八raster和源15lease→仅在同finally清两对象后返回0。A/B两个script所有字段已列，不能隐藏缺值到BuildFixture/DI/假标定；可以用本表驱动既有测试Host内部BCL构造，无额外便捷public方法。原sim-stop/dispose/decoder-stop/dispose观察与保首错/根移交严格§7.6.5；不能await using未决根或把调用脚本初始化完成当工作结束。CAL-JC宿主消费六payload时还保留两个axis原域和source/timing/evidence/mapping原件；未真实封存/调用Solve，本轮不宣称两消费者已接线运行。

#### 7.6.7 本切片验收、Benchmark和六项定位

| case / 子例（既有Core.Tests或Simulator.Tests） | 断言 |
|---|---|
| DC01 双Host/编解码 | §7.6.6 A/B具名八raster/源15/不同padding及反序mapping全部逐字段/byte/hash一致；Mapping/Request/Result独立编码核oracle。不请求Calibration source、不创建重建engine/Surface/Joint/Solver；可无硬件执行 |
| DC02 mapping/能力 | 合法ordinal排列改错/对称probe→002；同ordinal/共线/重复/非法tol→001；candidate/withdrawn/两Evidence bool任一false/缺mapping或Both capability→007；runtime/manifest/profile/dims或Version错→015，正文hash错→002；有限非负tol不因大于0.5单独拒绝，但使两排列同时满足仍002，不绕过Golden计划原件核验；组合错误按§7.6.2优先序，源/native调用0；不采用array0/1猜方向 |
| DC03 输入/shape/预算 | 缺Black/White/V/H/四Phase、跨CaptureGroup/epoch/clock/窗、FrameRevision/Mask ParentWhite错、stride>5/length多尾/0或1以外mask、过预算/整数溢出、raw少或多对象/非有限/错域长度/越界坐标；001/002/003/004/010/021/024准确，所有取得lease最终归还；Simulator先拒坏script，不代Core原stub出参检查 |
| DC04 取消/迟到/失败 | frame A0 Acquire/Observe；另MaskAcquire mask-A/CompleteLate gate late；另CallbackExit A/decode/CompleteLate；另MaskRelease mask-A/CompleteLate gate release。A停止不改B，Unknown无Result；开gate后源/回调/原release Task退出、原root15lease归还/5外Task观察/Released才清槽，保原业务错，重复Stop/Dispose不二次归还 |
| DC05 低支持/原值 | commonValid全0仍Completed/Released但不能Observed坐标/质量通过；单axis有值只保其原域，valid仍AND。域内合法0原Float64零、域外qNaN/byte mask0不可混；white-surface0不静默改decode坐标，CAL-JC独立筛选支持；不得自动归一化原图 |
| DC06 roots/immutable | factory前满容量/首factory错误/第二factory错误/业务消费抛/Close错/移交违约、default/mutable嵌套collection、旧Query跨放gate；两轴exit/原引用不丢。late放行最终必须恢复Released，不以预期Unknown让case0；没有强杀/重置其它进程 |

原Core.Tests内部stub新增DC出参反例、Simulator.Tests用CreateDecode发布入口，直接复用原工程/双Host/完整dotnet run命令，不建工程/夹具报告。每子例真实10s、S/D/DC整个Simulator suite120s/外进程180s；Core原套件180/240s维持。harness按S03停止后100ms≤20次推进/Query且总真实限时，finally只放本case gates、观察五原Task，失败/跳过/期限非零。故障gate只模拟原Task/租约恢复，不证明native或物理资格。

Benchmark沿§14唯一口径：从接纳到全部ResourcesReleased，新增纯托管source/hash/命名/F64编码/副本资源测点；native另计gen/decode/get/copy/clear，Both14等完整manifest、N/G/原stride/支持域/全部层/双Root各单飞固定。目标缺失NotEvaluated，虚拟clock不是P50/P95/P99。六项C1/S1定位：职责/消费者§7.6首段；API/单位/状态/错误/所有权§7.6.1–5；双无UI Host§7.6.6；异常/取消/重复/关闭§7.6.7；Benchmark本段/§14；工程/允许路径复用A.1/A.2的Core/Simulator/原Tests，按`Decoding/`子目录实施而不是复制一个重建产品。主控2026-10-11已完整回读并接收R3D-Decode-C1/S1六项规格为`ModuleCoreImplementationReady`（仅规格准备），A1固定HALCON路线/公开工厂内容限定接收；真实native/Golden/Envelope/消费者封存和运行资格仍`PreparationIncomplete / NotReady`，0.2.5接收保持。

### 7.7 数值提取与已给表面导入（完整能力的确定边界）

单幅普通灰度、强度或彩色图没有本模块可用的公制Z。本模块2D→3D仅指§7.1完整结构光或§7.2已标定立体；HeightField导入已有物理高度，显示重投影不产生新量测。不增加单目AI、photometric_stereo积分或以显示亮度推高度。

#### 7.7.1 结构光tuple与立体real图像的精度策略

HALCON 26.05的`object_model_3d_to_xyz`输出real图像是float32；`get_object_model_3d_params`公开`num_points`、`point_coord_x/y/z`、`mapping_row/col/size`。结构光固定分别查询这些属性（不混合不同长度输出），以同一模型原点ordinal关联XYZ和row/col；坐标经公共`HTuple.ToDArr`复制为double，整数映射经整数tuple读取，不能先转double再cast。num_points须非负且在MaxPoints内，三个坐标及row/col长度均等于它；mapping_size精确匹配原相机宽高。每个映射必须在图像/冻结ROI内、无重复row/col，并与from_xyz_map有效domain一一对应；少项、多项、重复、维度错误、非有限或无mapping一律R3D-024，不改用压缩ordinal/最近点。按原图row-major散射到CameraSamples，支持域外保null/原因；XYZ乘NativeLengthToMm一次，来源按§4.4完整manifest构造。tuple大小、散射表与三幅real域图同时计入Managed/Native/Result，不因最终只用tuple漏预算。

立体保持§7.2同次disparity→XYZ原始观测路线；其real图像已含float32量化，后续double变换不会恢复它。禁止把m3d_pairwise不明顶点顺序拿来替换像素XYZ。§8.2的Precision显式声明允许此路线且给出原生坐标绝对范围及量化上限；缺声明或消费者要求超出此表达能力则R3D-007，不能悄悄换匹配路线。在原生范围内，以binary32相邻值间距的一半为round-to-nearest表示误差上界，乘NativeLengthToMm后检查MaxImageQuantizationMm；非有限/超范围拒绝，边界测试包含binade交界和subnormal，不能用一个固定相对误差替代。这里只验证表示/复制误差，不声称三角测量、标定或float32算子累计误差合格；真实计量另门。结构光量测固定tuple路线，三幅real图只核域/显示，不以其值覆盖tuple。

本版普通native/传感器工厂产出的正常完整结果为Unverified；部分、冲突、不合格按现有QualityState保留。非空QualificationProfile/CalibrationScope.Qualification、合法Profile数值或source自称QualifiedCandidate均不授予资格，普通Import将该声明降为Unverified并记录警告，Core不得自行提升。Joint绑定仍按§8.1核原资格Owner，资格有效也不代替本模块真实算法/计量验收。真实生产接纳由原资格/应用Owner依据封存结果决定，不能借本模块bool或QualityState发布质量事实。

#### 7.7.2 SurfaceData公开读取桥与可表示性

普通`ISurfaceInputSource`可由宿主直接提供已冻结`AdapterDirectionResult`，Import逐项核§4.4的XYZ/mask/CSR、capture身份/采集epoch/源Frame/mm/Calibration revision；不加载SDK、不从ObjectModel3D句柄取值。上游ObjectModel3D必须先由其Owner复制公开值与确切来源，本模块不接裸handle。Import输出CalculationId采用本次request，ResultId固定为`request.CalculationId + ":" + capture.DirectionId`，总长须≤128，否则预检001；不能拿上游旧计算身份冒本次结果。SourceFrame/provenance保持原值，不提前应用方向矩阵。

对SurfaceData的标准接入新增唯一公开factory，放在现有`.Adapters` namespace/AsunImage Adapter DLL内（只是消费桥；不新增项目）。以下`SD`为`Asun.Modules.SurfaceData`别名，引用其Core公开程序集，Core/Simulator/WPF不因此引用SD。

```csharp
public sealed record SurfaceReadBinding(DirectionCapture Capture,
    SD.SurfaceReadRequest Read, RevisionRef MetadataRevision,
    RevisionRef ReadMethodRevision, SD.SurfaceKey Root, FrameRef RootFrame,
    TransformProvenance SourceTransform,
    IReadOnlyDictionary<uint, byte> InvalidReasons, ByteCount MaxCopiedBytes,
    TimeSpan ObservationBudget);
public static class ReconstructionSurfaceBridgeFactory {
    public static ISurfaceInputSource Create(SD.ISurfaceDataService service,
        SurfaceReadBinding binding, IReconstructionClock clock);
}
```

Create无IO/无任务，null抛ArgumentNullException，非法配置抛ArgumentException；深复制binding/字典/SD请求嵌套数组，端口只借用。一个桥一个冻结capture、一次Acquire（再次拒R3D-022）；服务和真实Source由宿主独占或共享管理，桥不Close别人服务。MetadataRevision是源Owner封存的原metadata身份（沿SD §18），不是本模块私造hash。Capture含一个HeightField/PointCloud FrameRef代表当前载体，RootFrame不同则另声明一项（见下文根Frame规则）；TriangleMesh、跨层SurfaceSet、Face域和需C5多父权重输入明确R3D-007，原对象交源Owner保存，不丢拓扑/权重伪造flat观测。Read.Range.Domain=Vertex、Ordinal全域Start0/Count=VertexCount/AllowEmpty=false、PreserveAll、ReadCoordinates=true、TargetFrame=Descriptor.Frame、Transform=null；单位已是SD Millimeter且Frame映射到capture.SourceFrame，HeightField的Grid/父offset由SD坐标端口计算真实XY。本桥不从Grid猜pitch、不再调用H过滤/转换单位。XYZ三列或Height一列是FieldIds全部内容；额外属性/不确定度不隐式读取，UncertaintyMm=null。N在1..MaxPoints且≤16,777,216；HF宽高与capture匹配，点云Width=N/Height=1，公开Layout分别CameraSamples/PointCloud，Grid=null，不冒OutputGrid。

Root明确等于Descriptor.VertexIndices.Root；RootFrame由源Owner绑定该Root实际快照/hash，不能用当前载体ordinal替代Root。Capture及MetadataRevision/RootFrame的修订关联由source在读前核对；同名字不构成证明。Read.Generation正，Budget/SD Plan上限完整显式；本桥复制账预检包括逐槽XYZ、mask/reason、源long暂存、CSR、每项来源、描述与警告，按§13.2保守账加long暂存8*N及其排序副本8*N，≤MaxCopiedBytes与重建Managed/Result剩余预算。SD Plan.ResidentUpperBound另占宿主总账，不能把SD释放等同桥副本释放。ObservationBudget100ms..60s，取消/超时不Close共享service。

固定流程：SD Plan→预留整批副本和原Operation/Completion槽→StartRead→短同步OnBlock复制→观察原Completion→仅Outcome=Completed/Completeness=Complete/RequestedItems=DeliveredItems=N、Generation/Input精确且Integrity至少RequestedBytes时采用。OnBlock核Generation/Descriptor/源Frame；StartRead可能在返回前回调，预留consumer槽先把首次block.OperationId作为待关联值强持，所有后续块须同ID，Start返回后必须等于原Operation.Snapshot.Id，未完成关联不可采用；ordinal按原全域严格递增、无少重项；Span不越回调，任何异常/取消使整批暂存失效。consumer不可等待Completion；Start拒绝不触源。取消后RequestCancel一次、有限Observe原Operation，不用Wait超时宣布释放；Completion未退出或source释放不明时Acquire仍由原Task强持，外层Import/engine按§9进入DrainUnknown。迟到Complete只归还副本，不恢复已关闭消费权。完成后返回只读值lease；Dispose幂等、共享同一真实释放Task，唯一释放桥副本。

逐槽映射不能靠byte截断：

source接口未接ReconstructionRequest，不能靠隐藏当前operation取得CalculationId。桥中暂存SurfaceResult.ResultId/CalculationId固定为MetadataRevision.Id（仅本次原metadata读取的本地值身份），AlgorithmRevision=ReadMethodRevision，Mode=SensorProvidedSurface；ReadMethodRevision.Id固定`r3d-surface-read-v1`，hash取实际发布桥方法版本，全部原producer算法/状态仍在metadata来源中。Import收到request后再复制成本次CalculationId及上述ResultId，AlgorithmRevision采用request.Parameters.AlgorithmProfileRevision并把ReadMethodRevision追加Provenance；二者不互换成资产hash。软件fixture显式用SHA256(UTF8(`synthetic:r3d-surface-read-v1`))作为此synthetic读方法hash，只验证值形状，不冒真实发布包。source阶段Transforms保binding.SourceTransform原事实：DirectionId相同、scale1、ApplicationCount0时AlreadyInOutput/Snapshot=null；count1时原发布Snapshot必需并由producer绑定原已应用事实，Import再核request.PreviousApplicationCount/PreviouslyAppliedSnapshot，不能只填1声称应用过。非法count/来源020；本次ApplyPublished只由Import后Core调用，不用目标请求初始化source。两software正例SourceTransform=(原direction,AlreadyInOutput,null,0,1)。

桥的复制费用明确为`M=65536+192*N+256*N+8192*F+16*N+Σ(max(2*s.Length,StrictUtf8ByteCount(s))+32)`，F为capture/RootFrame引用数、s遍历本binding/descriptor全部字符串出现处；前两N项保守覆盖XYZ/mask/reason/计数/CSR及每槽一条来源，16N为原long索引与排序副本。Acquire峰值预约4*M（桥暂存、返回lease防御副本、Import/Core必要复制），另加SD Plan.ResidentUpperBound；分别满足MaxCopiedBytes、request的Managed/Result和宿主总账。实现若多复制一份须先增加预算，不隐藏在GC。此公式补足上文§13.2只有fixture而非桥预算公式的歧义，不改变已接收Core数值/限额。

Capture.Frames为当前载体一个FrameRef，加RootFrame（两者完整相同则只一项）；否则1..2项、FrameId/ordinal不重，RootFrame也必须与capture.DirectionId及原Owner快照绑定。载体帧尺寸匹配Descriptor形状，RootFrame尺寸是原Root尺寸，不用载体crop尺寸取代；RootFrame不作为第二个表面读取。输出CSR只引用已声明RootFrame，Provenance保MetadataRevision及RootFrame.Revision，来源摘要仍从CSR推导，避免回执出现未在输入声明的根FrameId。Kind为表面值类型而非光学帧，Acquisition.Frames仍可空，不伪造第二次曝光。

- SourceIndices为原Int64 Root索引，核非负、≤Int32.MaxValue、无重复，checked转SampleIndex；任一超限R3D-024，包含>2^53反例，不通过double中转。本版API不能表示的大Root完整交还原Owner，不把局部ordinal当根。ImageRow/Column只在源Owner证明Root是二维原图且索引/RootFrame尺寸一致时按Root宽度计算，否则二者null；当前载体HF坐标不冒根像素。
- SD综合State=Valid、Origin=Observed、Method observed/1、HasExactParentIndex=true且单一Parent=Root时才形成有效观测；XYZ有限、原因为0。Unknown状态/Unknown来源、有效Fallback2D或任何有效派生Origin不能保真表达为本模块真实单根贡献，整批R3D-024，保原源证据；不提升、猜父或静默丢槽。无效Interpolation只有原Reason显式映8时保原因8，其余无效槽按下面字典处理。
- State=Invalid时XYZ置null、ContributionCount=0、SourceOffsets仍可保一条明确Root来源。InvalidReasons须由该producer的原字典显式逐项映射，目标限原因1..11；code0也必须显式映“无对应”1，未知uint不猜语义，未登记/与Origin矛盾R3D-024。不将所有厂商uint按低8位cast。原State/Reason/Origin及全部buffer/hash留在MetadataRevision封存对象，回执provenance引用它，桥不覆盖源。
- 每有效槽CSR恰一条RootFrame来源、ContributionCount=1、ConflictPairCount=0；无效也只保可证来源、不增加贡献。SourceFrameIds/SourceDirectionIds从CSR推导。NativeLengthToMm=1、TransformUses沿输入声明，Quality按§7.7.1；有效0/负值原样保留，全Invalid仍不包装PASS。

该桥的两消费者沿原A/B的SensorProvidedSurface子场景，分别以2×2 HeightField（显式Grid坐标端口）和4×1 PointCloud调用同一factory/Import，无UI/SDK。软件正例四槽源索引0/1/2/3、XYZ=(0,0,0)/(1,0,-0.25)/(0,1,0.25)/(1,1,0.5)，均Observed/Exact；反例另建fresh桥，不重复使用已调用桥。范围/Root、不能保真的来源和失效块只拒绝该输入能力，不阻断已接收Core或直接提供符合§4.4的managed source。

## 8. 适配器与资源所有权

```csharp
public interface IStructuredLightEngineAdapter
    : IAdapterLifecycle
{
    ValueTask<AdapterDirectionResult> DecodeAndReconstructAsync(
        ReconstructionRequest request,
        DirectionCapture capture,
        CalibrationScope calibration,
        IFrameSource frames,
        ICalibrationAssetSource assets,
        ReconstructionParameters parameters,
        CancellationToken cancellationToken);
}

public interface IStereoReconstructionAdapter
    : IAdapterLifecycle
{
    ValueTask<AdapterDirectionResult> ReconstructAsync(
        ReconstructionRequest request,
        DirectionCapture capture,
        CalibrationScope calibration,
        IFrameSource frames,
        ICalibrationAssetSource assets,
        ReconstructionParameters parameters,
        CancellationToken cancellationToken);
}

public interface ISurfaceInputAdapter
    : IAdapterLifecycle
{
    ValueTask<AdapterDirectionResult> ImportAsync(
        ReconstructionRequest request,
        DirectionCapture capture,
        ISurfaceInputSource source,
        CancellationToken cancellationToken);
}

public interface ISurfaceTransformAdapter : IAdapterLifecycle {
    ValueTask<AdapterDirectionResult> ApplyAsync(string operationId,
        AdapterDirectionResult source, PublishedDirectionTransformRef transform,
        CancellationToken cancellationToken);
}
public interface IAdapterLifecycle {
    AdapterDrainSnapshot QueryDrain(string operationId);
    ValueTask<AdapterDrainSnapshot> StopAndDrainAsync(string operationId,
        TimeSpan waitBudget, CancellationToken cancellationToken);
}
public sealed record AdapterDrainSnapshot(string OperationId, DrainState State,
    long ActiveNativeCalls, long PendingCallbacks, ReconstructionError? Error);
public sealed record AdapterDirectionResult(SurfaceResult Surface,
    SurfaceGeometry Geometry, IReadOnlyList<ReconstructionError> Warnings,
    IReadOnlyDictionary<string, long> ResourcePeaks)
{
    public System.Collections.Immutable.ImmutableArray<StructuredLightDiagnosticLayer>
        DiagnosticLayers { get; init; }
        = System.Collections.Immutable.ImmutableArray<StructuredLightDiagnosticLayer>.Empty;
}
public sealed record AdapterFailureContext(string OperationId,
    string CalculationId, ReconstructionError Error,
    bool HasCopiedResult, DrainState Drain);
public sealed class ReconstructionAdapterException : Exception {
    public AdapterFailureContext Context { get; }
    public ReconstructionAdapterException(AdapterFailureContext context,
        Exception? innerException = null)
        : base(context.Error.ReasonKey, innerException) { Context = context; }
}
```

适配器是唯一允许接触 `HStructuredLightModel`、`HObjectModel3D`、`HImage`、`HStereoModel` 等 native 类型的边界。适配器必须：

- 在操作开始时创建并登记句柄，在成功、失败和取消路径均 `Dispose`；
- 保持输入只读，输出仅复制托管值，native句柄不转移给Core/产品；
- 取消时先停止新工作，再等待 native 调用返回和回调排空，最后释放句柄；
- 适配器报错保留原错误码/消息和 operator 名，不把异常转换为有效结果；
- 不在静态字段缓存句柄，不跨操作复用可变结构光模型；
- 用操作私有资源账本记录估算/实际 native、托管和 GPU 字节，按 ResourcePeaks 返回，超出预算前拒绝；账本不是未定义的公共 IResourceLease API；
- 不主动重拍、不重连设备、不写数据库、不提交质量事实。
- 各适配器注册 OperationId/DirectionId 上下文，所有 native 调用、回调和 FrameSource 租约按此登记。成功返回 managed 值快照并等待 native 调用结束；失败路径仍可 QueryDrain。三个重建/导入适配器只输出 SourceFrame 的原始 XYZ，不应用 IM-033 变换；ApplyPublishedTransform 阶段才经 ISurfaceTransformAdapter 调用 `ImageLibDotNet.cv2` 的 `affine_trans_point_3d`；首发公开输入已复制为托管XYZ，固定使用该点算子，不依赖另一个适配器私有的native对象缓存，复制输出并标记 count=1。导入器不能因为 request 含目标坐标就提前转换。

核心层每个操作一个执行上下文；方向并行固定为 `1`，本 API 不提供运行时提高入口。HALCON 内部并行由部署 Profile 固定线程配置并记录，不能将原文“内部并行”误写为共享模型安全。未来方向并行 2..4 需新 MethodRevision 和资源/结果顺序验证；当前不是运行时选项。核心计算不得使用 `Task.Run` 包住同步 HALCON 调用来伪造取消；应由适配器在受控执行器中调用并在返回后排空。

适配器有类型故障抛 ReconstructionAdapterException 并保留 Context，Core核对身份并转换 DirectionIssue/操作Error；未知异常/OCE分别按AdapterFailure/已请求的取消意图处理，仍查询排空，不能信任异常对象的Drain作为资源释放证据。首发真实适配使用CPU执行，GPU/OpenCL启用需显式新部署Profile及设备内存预算/资格，不由机器有GPU而自动改变；GPU资源计数首发为0。

QueryDrain的State还覆盖在途source/asset获取及其迟到Task；ActiveNativeCalls=0且PendingCallbacks=0本身不等于Drained。停止后迟到获取的租约由原操作接收并归还、不再启动native，也不交给新操作。各lease的DisposeAsync必须幂等、共享同一释放Task；释放Task未完成或抛异常时Core保持DrainUnknown/所有权、不能发布Released，也不凭“native已退出”推断source归还成功；后台Owner继续观察原Task，不能丢引用或重复有副作用的释放。

### 8.1 Joint重建消费：原资格响应、装配前复查与完整绑定

本节为`R3D-Joint-Consumer`指导增量，消费者为§11原A结构光实验Replay与原B的3D AOI光学重建接入场景；B原表面导入场景不变。资格事实、判定顺序、技术编码和`JointQualificationBinding.Bind`唯一来自[CAL0.3.2-prep §7.4.6B](../calibration-assets/DEVELOPMENT-GUIDE.md#746b-两消费者资格绑定技术桥jointqualificationbinding-v1)。这里不复制codec/资格算法、不增加Core/Simulator依赖、API、状态或第二资格服务；§7.6首次decode-only仍无标定前置，不消费本绑定。调用发生在宿主Joint集成边界，Core只收原合同，完整Joint伴随对象由同一Host根和操作私有source/adapter强持。

#### 8.1.1 同次Resolve的可信原响应与复查

1. 两Host分别在CAL工厂/查询及重建工厂前预留§8.1.4同一个有界组合根。显式注入固定的原`IJointQualificationPort owner`；来源由Host配置决定，不按返回snapshot的Authority字符串重新选Owner。将本地转发观察器注入`new JointAdapters(null,null,store,observer,gate,diagnostics,clock)`，通过`JointCalibrationModule.Create(options,adapters)`创建只读模块，不创建solver、不Solve/Publish/激活设备。观察器实现原接口，不成为新公共服务；Watch只按同Owner原语义转发，不从通知制造资格快照。
2. 用新resolveId调用`ResolveAsync(new JointCall<JointResolveInput>("1",resolveId,budget,new JointResolveInput(use)),token)`。观察器在内部`ReadAsync(query,execution,token)`调用前登记原Owner对象、query/execution/token及完成路径，Owner的ValueTask恰一次AsTask，根立即强持原Task。`query.OperationId=execution.OperationId=resolveId`，每次Resolve恰一次Owner Read，0次/多次/ID冲突均Host Unknown。完成路径先限额深复制原完整snapshot s1，用**CAL原JointCodec**编码/取得完整ContentRef c1并封存，才把原语义值交CAL。不得在Resolve后另查最近s1填补缺捕获，也不得从拟绑定副本反填Expected。
3. 根同时保存原Resolve Task/Reply和该内部Owner Task/原响应/规范字节。仅Reply.OperationId=resolveId、Completion=ResourcesReleased、Error=null、Value.Status=Applicable且Qualified/Export俱全才继续。Captured query.Use=本次use、ContentDigest=use.Asset.Digest、CheckEvidence=s1.CheckEvidence；s1.Asset=s1.Scope.Asset=use.Asset=Export.Asset，Resolve.Qualified全部字段与s1一致。Scope.Pattern证据正文用途由原CAL Resolve核验，本Host保留引用，不凭hash自身证明隐藏证据。任何关联不全Host Unknown、不装配、不native；原CAL NotApplicable/Unknown及Findings原样保留。
4. 在装配前取**同一Owner对象**，用不同于resolveId的新recheckId调用`owner.ReadAsync(new JointQualificationQuery(q1.Use,q1.ContentDigest,q1.CheckEvidence,recheckId),new SolverExecutionContext(recheckId,remainingBudget),linkedToken)`。根先登记原请求/调用再强持原Task；remainingBudget逐项取父剩余额度/时间，不复用已耗尽的初始预算。完整返回s2先核本次asset/scope.asset、Purpose/Pattern/optics/volume及曝光覆盖关联，再限额复制/用CAL codec封存c2。别的asset返回Revoked不能冒作本次撤回；迟到、取消、期限、来源/关联缺失只有Host Unknown，不能Bind或启动native。
5. `JointQualificationExpectation`逐声明字段从原封存s1、c1和同次Resolve.Qualified取值，ResolveOperationId=QualificationQueryOperationId=resolveId；非Qualified原响应不造Qualified引用。`JointConsumerBindingRequest`依声明为(Expected,s2.Watermark,s2.Status,c2,recheckId,use,本次Clock.UtcNow,"1.0.0")；调用`JointQualificationBinding.Bind(s1,request)`，只接受Applicable且Projection/SnapshotContent非空。完整水位五字段及两类evidence由原helper判定，撤回优先；epoch/revision/ObservedAt/ValidUntil或证据变化不得删字段凑旧hash。即使只更新时间也不无界重试；新操作重新Resolve/复查。
6. 复查后立即在同根准入锁中Bind、核Closing=false/无已知invalidation或epoch gap/未取消/父单调期限与水位仍有效、封存下游请求和完整绑定，并启动已登记的重建原调用；中间不得await/重新排队。若需要异步准备frame或其它资源，须在复查之前完成。锁只用于本地准入/登记，不跨await或native持有；之后的已知撤回停止新native步骤并请求原操作有限排空，不能强杀在途算子。复查不构成跨Owner原子事务、无限有效资格或最终质量放行；后续产品提交仍由原产品Owner重核。

#### 8.1.2 独立Joint绑定对象与逐字段装配

Host内部使用一个独立不可变`JointReconstructionBinding`值，字段固定为`Projection:JointConsumerBindingProjection`、`Export:JointSetupExport`、`BindingRequest:JointConsumerBindingRequest`、`Request:ReconstructionRequest`；这些是组合Host私有类型/构造，不加入Core/Simulator、不另发DLL。构造前深复制全部嵌套值/Export.Bytes，保存原CAL规范字节及完整s1/s2的根输出槽仍在；Projection包含源`JointPublishedRef`的任意RevisionId、完整资格snapshot/资格Revision、水位/Scope/两类evidence。没有完整伴随对象则拒绝Joint路径，不能只取两个RevisionRef继续执行；也不能改写源revision为SemVer。这里不为绑定另造编码/签名，重建结果仍原Core值，需保存的Joint来源由Host原内容Owner伴随保管，不塞进虚构Result字段。

| 下游字段/证据 | 唯一来源与必须核对 |
|---|---|
| CalibrationRef.Asset / 每direction.DirectionCalibration / CalibrationScope.Asset | 均`RevisionRef(projection.ReconstructionAsset.Id,projection.ReconstructionAsset.Sha256)`；等于SourceAsset.Id及**源asset digest**。不可换成setup file、candidate、CheckEvidence或资格摘要 |
| CalibrationScope.Qualification | `RevisionRef(projection.ReconstructionQualification.Id,projection.ReconstructionQualification.Sha256)`；ID为源资格ID，hash为**完整资格snapshot技术hash**，等于Projection.QualificationSnapshotContent.Digest，不是CheckEvidence/RuntimeValidationEvidence/candidate hash。完整资格修订/水位/Scope/evidence仍随绑定保存 |
| CalibrationRef | CalibrationKind=`CameraProjectorJointV1`；CameraFrame=WorldFrame=Export.CameraFrame，完整CAL frame相等且等于RequestedUse.ActualOptics.CameraFrame；ValidFrom/ValidTo来自Resolve.Qualified并与源snapshot一致，ValidTo=null保留无上界。全部帧曝光UTC闭区间均在use及资格有效/Scope覆盖窗内 |
| CalibrationScope | NativeLengthToMm=1000、CameraIndex0/ProjectorIndex1；camera W/H=ActualOptics.Camera的原full raster，projector W/H=ActualOptics.Projector且等于RuntimePattern.Width/Height；ReconstructionFrame=上述camera frame。`DirectionCapture.SourceFrame`同此frame、Unit=Millimeter；不把每pose板frame或输出工作台frame冒成setup world |
| Pattern/帧/原采集scope | 原Request.Mode=StructuredLight；PatternSpec.Route明确映射CAL HybridVertical/HybridBoth，W/H、MinStripeWidth、MinGrayDifference逐值相等，Normalization=global、SingleStripe=null；Sequence及真实manifest/decoder/DirectionMapping完整原件按源Owner展开核对，不能只比短ID。Frame W/H/Mono8/full raster、曝光配置/ActualOptics.PhysicalMapping、完整Acquisition attempt/epoch/ClockDomain/窗和§4.2.1/4.2.2条件全部成立；不套标定Both的manifest去运行Vertical |
| 世界变换/实际域 | OutputFrame与setup frame相同时AlreadyInOutput/count0；需要工作台/板坐标时仅沿原IM-033 ApplyPublished、匹配FromFrame/ToFrame/asset/epoch、一次变换。ActualVolume/温度/用途由原CAL核适用并覆盖本次全部点；超域点不伪称资格内，不自动扩域或更换Purpose |
| JointSetupExport | Export.Asset完整含revision/digest等于SourceAsset；File完整Digest/Format/FormatRevision/ByteLength保持，实际独立Bytes的SHA/长度精确匹配File，ByteLength>0且不超int.MaxValue/父MaxImageBytes/MaxResidentBytes。真实Format=`halcon-camera-setup-file`、FormatRevision=`26.05`；CAL Synthetic/1分支仅`cp-joint-synthetic-setup-v1`/`1`且CalibrationReplay软件断言，不交read_camera_setup_model。Export.CameraFrame=WorldFrame、scale1000/index0/1均核；Asset.Digest与File.Digest各司其职，不要求相等 |

实际装配必须双边保管：Host本地Joint source按构造实参持绑定，仅实现既有`ICalibrationAssetSource`，Acquire核传入CalibrationRef逐字段等于绑定Request，返回操作私有lease，Asset仍源asset指纹，SerializedCameraSetup仍Export原字节且按File核hash/length；每lease继续强持整个绑定直到真实Dispose。Host本地Joint adapter实现既有`IStructuredLightEngineAdapter`/生命周期，构造时显式持同一绑定；`DecodeAndReconstructAsync`在取得帧/资产或任何native前核原request/capture/calibration/parameters、source实参及绑定均匹配，不从全局注册表找绑定。真实加载实现从这个专用上下文取Export.File和源asset两套身份，不转交给仅懂“SHA(setup)=Asset.Sha”的普通loader。缺绑定/不匹配R3D-005、明确不支持的真实装配R3D-007，不退回普通路径；本地Host Unknown/NotApplicable不伪造Core已运行错误回执。真实adapter public接线/编译及运行仍为受影响资格门，本节不是声称已实现的工厂。

真实执行仍唯一read_camera_setup_model→set camera_setup→原gen/manifest核对→decode/reconstruct→按1000从meter转mm一次；模型、私有临时file/流/lease归原操作，所有native/回调退出后按原序清理，文件hash失败不read。不能将Asset摘要拿去比较setup字节而错误拒绝合法Joint，也不能仅核setup file正确就绕过资格完整绑定。Core Validate不读取CAL或证明资格，不能凭Validate.IsAccepted为Joint放行。

每次开始read/gen/decode/reconstruct前，专用adapter核同绑定仍被根强持、非Closing、无已知撤回/epoch gap、父deadline及资格水位仍有效；frame/lease异步等待跨过水位期限同样拒绝新的native步骤。这里不新增资格查询循环或静默刷新c1；已在途native先有限排空，其结果不再拥有生产发布权。

#### 8.1.3 原两个无UI Host的Joint装配子场景与反例

原§11 A/B新增Joint子场景，原F0/F0-S、Simulator S/D/DC和Golden全部保持。有限纯软件场景放在A.1已有AsunImage.Tests的Host集成目录，直接引用CAL已批准公共Joint/Core和重建Core，使用本地spy/Owner故障闩锁；不引HALCON运行、不引用其它测试工程私有fixture、不改Core.Tests/TestHost/Simulator.Tests的仅Core依赖。完整值复用CAL §7.4.6A公开构造规则：fixture准备阶段先以原mock solver/Store/Qualification/Gate经原Solve/Validate/Publish形成真实内容闭包及PublishedRef，关闭准备模块/归还根，再启本节两只读Host；借用Store等由fixture Owner持有到二者全部结束。准备步骤的调用不计消费者只读调用。不能拿§7.4.6B纯值oracle的label资产摘要冒成这个Store内完整artifact摘要，也不导入私有Build方法。§7.4.6B原s1/s2/qref1仅用于JRC01/03的独立helper纯值反例，原codec和资格判定都直接调用CAL，不复制；本轮不重算或新增向量。

| 原Host | 完整Joint子场景输入 | 调用与可判定输出 |
|---|---|---|
| A结构光实验Replay | 原独立root/options/observer/固定t0；resolveId=CAL Id(201)、recheckId=Id(202)，重建IDs=`joint-A-op/joint-A-calc`。Asset为准备阶段Store已发布的`JointPublishedRef(syn-joint-asset,RevisionId("1"),candidate.Digest)`；原资格fixture DecisionAvailable=true、两次返回同一完整Qualified snapshot（syn-q/RevisionId("1")、Synthetic/epoch-1/水位Revision1/t0..t0+1day、有效期t0±1day、Scope覆盖t0±1day/CheckEvidence=原Store Check/RuntimeValidationEvidence=C("runtime-HybridBoth")）。Use明确取本Asset/原Optics/runtimeBoth/原Volume/CalibrationReplay，曝光[t0,t0+1ms]；Export为原Resolve真实导出值，Frames=原syn-cam0/index0/1/scale1000，Bytes为CAL原公开synthetic setup字节 | 经观察器Resolve→同Owner复查→Bind→核§8.1.2适用的资格/Export/CalibrationRef/Scope投影：asset hash为本次源digest，qualification hash为本次完整快照hash，源修订原值保留、QualificationSnapshotContent与Expected相同。只产本地BindingPrepared/装配字段断言，Synthetic禁止真实loader/native；此状态是Host测试结果，不新增Core/CAL状态 |
| B的3D AOI离线光学接入 | 同公开值、自己的root/options/observer，resolveId=Id(301)、recheckId=Id(302)，重建IDs=`joint-B-op/joint-B-calc`；显式同Store/原Owner但独立请求/Task/Export深副本，Factory/Observations=null | 相同Bind/装配断言，独立保存伴随资格对象。A取消/关闭/未知不改变B结果或Owner；B原表面Replay仍无需CAL，此Joint子场景不制造产品SurfaceReconstruction资格。实际生产Use必须Owner批准SurfaceReconstruction后再走全链 |

两卡是**完整资格绑定/装配层**软件验证，停在BindingPrepared，不借CAL synthetic manifest/SETUP标签拼造真实完整相机采集请求或执行Core重建；§8.1.2的Request封存/真实source/adapter则须宿主提供原完整采集输入后验证。原Core/Simulator完整运行双Host仍按§11/13，不能以本卡提升它们范围或真实native资格。Spy记录Resolve1、内部Owner Read1、直接复查Read1、Solve/Publish0、native0；所有Task完成路径/桥输出与归还计数可判定。

两卡的装配预期明确为：CalibrationRef kind=CameraProjectorJointV1、Asset=(本PublishedRef.Id,本PublishedRef.Digest)、CameraFrame=WorldFrame=syn-cam0、ValidFrom=t0−1day/ValidTo=t0+1day；每direction.DirectionCalibration及Scope.Asset等此Asset，Scope.Qualification=(syn-q,本次c1完整Digest)、NativeLengthToMm1000、ReconstructionFrame=syn-cam0/index0/1、Camera64×48/Projector80×60。任意source-A/qual-A原string保真的独立helper断言取CAL原纯值s1，和本次Store的RevisionId("1")分别保留，不能互换。专用JointReconstructionBinding的Request在实际采集输入存在前不构造；本卡以根保存Projection/Export/Expected/Use及这些装配预期，不能填null/伪请求冒已封存运行绑定。

| 既有验证工程中的新增子例 | 确定断言（每项A/B独立，主错误不被cleanup覆盖） |
|---|---|
| JRC01 正常/身份 | 两Host上述装配成功，完整SourceAsset/SourceQualification/ContentRef均保真；另以CAL原helper纯值s1断言任意source-A/qual-A原string保持，不把该oracle冒Store资产。只留下普通RevisionRef/去源revision/资格revision/Scope/evidence即拒绝，Setup hash不等Asset hash不能作为坏数据理由；BindingPrepared不等Completed/QualifiedCandidate |
| JRC02 原Owner关联 | 缺/两次内部Read、query/execution/Resolve ID错、Owner对象被替换、取最近缓存替代、snapshot与Qualified/Export asset不符→Host Unknown，Bind/下游调用0；另一asset的Revoked同样Unknown |
| JRC03 当前资格 | s2 Revoked/Suspended/Expired→NotApplicable优先；epoch/authority/revision/ObservedAt/ValidUntil变化、只换CheckEvidence或RuntimeValidationEvidence、复查Unknown/缺水位/过期→Unknown；保原Findings/完整快照，不改Expected凑成功 |
| JRC04 文件与scope | setup Bytes/length/hash/format-revision、scale/index/frame、两端尺寸、route/manifest/decoder/mapping、曝光窗/ActualOptics/volume/Purpose逐一不匹配，装配失败/不native；有效期null不造截止；真实双端原生坐标/计量另验 |
| JRC05 迟到/关闭 | Resolve、内部Owner、复查或完成路径各卡住/忽略cancel/ThrowBeforeTask/ReturnLate；观察有限Unknown，Closing后值先入根而不Bind/不装配，原Owner Task仍强持；开闩锁后真实退出、输出归还才清槽，不二次Read/重建 |
| JRC06 根与收尾 | factory前满槽零调用；CAL或重建factory失败、Stop/Dispose异常/卡住、移交抛错、业务失败叠加cleanup失败；原Task/原异常/桥对象及bytes不丢，业务2/3/4保持、业务成功但cleanup失败5，接收未确认不退根/容量；A/B借用Owner不Dispose |

每子例真实观察≤10s、Joint软件suite120s/外层独占进程180s，虚拟Clock只推业务截止，不算性能。finally只放本case闩锁，有限观察原Task/释放，pending/跳过/期限非零；不调用本轮未获授权的工程命令。Benchmark复用§14，后续测点区分Resolve/Owner封存/复查/Bind/Export验证与原native链，端到端到真实释放；本轮无编码、编译、运行或性能数值。

#### 8.1.4 组合根预留、原Task与真实释放

Joint子场景在§11原两消费者各自槽内增加组合上下文，最多**2个**含隔离/移交未决根，不为CAL/重建再各占两个而扩大容量。原Core三Task/Simulator五Task规格不变；仅本集成根采用CAL原MaxTasksPerRoot64/MaxBuffersPerRoot8：创建CAL与重建的构造执行Task、Resolve原Task、内部Owner原Task、直接复查原Task、所有封存/交付完成路径、两组件Stop/Dispose及重建run（若实际启动）都在同64槽中。先登记角色/身份/委托依赖，执行委托前有容量；ValueTask恰一次AsTask，返回立即写原Task，同步throw也保存entry/原异常。晚到factory实例先写根再交付或进入关闭，不能以engine=null清空仍在途factory根；不持WaitAsync wrapper冒原Task。

组合根的Host内部字段冻结为RootId/Closing、两个重建ID/resolveId/recheckId、原Owner/observer/借用依赖、CAL module/重建engine、原Tasks[64]/Outputs[8]、每组件唯一Stop/Dispose Task、首业务异常/cleanup错误、ReservedBytes/OwnerConfirmed；根由容量2注册器强持，原Task与完成路径均计槽。内部恢复入口`void RetainJointRoot(JointHostRoot root)`只接这个完整根，不把它拆成只含engine的旧Core Retain；接收前复制/强持全部引用和容量计费，正常返回才确认，幂等且失败仍原根清理权。本定义只用于本集成Host，不新增模块public API。

桥增量逻辑费用固定1MiB、三份规范字节各≤64KiB/合计≤192KiB，其余至少832KiB计有限快照/Expected/Projection/根记录。Export.Bytes原/防御副本、frame/lease、重建结果和真实native费用另checked相加，逐项不超父请求、CAL gate/根剩余额度及重建预算，不以1MiB包住无限Export。不持CAL IO gate预约跨再次Resolve自锁。8输出槽按CAL原约定分别强持Export+bytes、原响应+编码、ResolveReply、Expected+Use、复查+编码、拟绑定临时、BindingResult、下游request+伴随对象；只引用同一冻结值的记录计一次实际占用，有新深副本则另计，不能漏计仍Held。宿主借用Store/Qualification/Gate/Clock不Dispose。

finally先Closing=true，锁内关闭接纳，保首业务异常与最多16项cleanup错误（溢出保计数/首末），每组件各自独立有限收尾，不让一个throw跳过另一个可安全关闭组件。重建已启动按§11一次Stop/确认Released及原run退出后一次Dispose；CAL一次Stop并逐resolveId GetOperationState核held/Final，再仅在其全部业务原Task/完成路径真实结束后一次Dispose。每原Stop/Dispose真实观察≤1s，观察取消不撤销后台归还；各任务只发一次、失败不重建组件或重试有副作用Dispose。尚未退出的直接复查是Host持有任务，CAL Stop/Dispose不能证明它结束；实际启动下游时lease/native/临时file未归还也不能退桥输出额度。若待复查真实结束才能安全Dispose CAL依赖，则保持根并由有限恢复窗口接续，不边Dispose边让观察器访问已关闭上下文。

退出0仅本次业务完成且所有已发原Task/完成路径已退出、各组件真实Released/Dispose成功、全部输出/lease已归还且无cleanup错误。Unknown只保原Owner/Task/完整绑定与bytes、有限移交；恢复接收方先在同一根容量内独立强持全部对象/64原Task/8输出槽并确认，正常确认前原根唯一清理Owner、未确认/抛错不退槽。确认只转Owner不算释放；原迟到值不重新获得Bind/native权限，后台放闩锁后观察原Task并真实归还，再退根/费用，不改原失败回执。真实资源结束与状态投影分别核，不以CAL Resolve已Released、Native0、GC或方法离栈替代组合根释放。

### 8.2 普通Adapter的公开装配、预算与清理

本节是普通setup/已给表面的唯一创建入口，namespace `.Adapters`，沿A.1既有AsunImage工程；不替换§7.6 decode-only工厂，也不绕过§8.1 Joint伴随绑定。以下是待实现签名，不是已存在程序集。公共能力包只有Core端口/值，不把AsunImage native类型暴露给宿主。

```csharp
public sealed record ReconstructionNativeEnvelope(RevisionRef Revision,
    long FixedBytes, long BytesPerInputByte, long BytesPerCameraPixel,
    long BytesPerPatternPixel, long BytesPerPoint, long BytesPerVoxel);
public sealed record ReconstructionPrecisionPolicy(RevisionRef Revision,
    double MaxAbsNativeCoordinate, bool AllowStereoRealImages,
    double? MaxImageQuantizationMm);
public sealed record ReconstructionAdapterProfile(RevisionRef Revision,
    RevisionRef RuntimeRevision, string EngineVersion, int NativeThreads,
    ReconstructionNativeEnvelope Envelope, ReconstructionPrecisionPolicy Precision,
    TimeSpan DrainTimeout);
public interface IReconstructionAdapterSet : IAsyncDisposable {
    ReconstructionAdapterProfile Profile { get; }
    IStructuredLightEngineAdapter StructuredLight { get; }
    IStereoReconstructionAdapter Stereo { get; }
    ISurfaceInputAdapter Surface { get; }
    ISurfaceTransformAdapter Transform { get; }
    AdapterDrainSnapshot QueryDrain(string operationId);
    ValueTask<AdapterDrainSnapshot> StopAndDrainAsync(string operationId,
        TimeSpan waitBudget, CancellationToken token);
}
public sealed class ReconstructionAsunImageFactory {
    public ReconstructionAsunImageFactory();
    public IReconstructionAdapterSet Create(ReconstructionAdapterProfile profile,
        IReconstructionClock clock, IReconstructionDiagnostics diagnostics);
}
```

Create只纯校验并深复制值、初始化有限账本，不读frame/setup/file、不创建native模型/线程/窗口；null抛ArgumentNullException，非法Profile抛ArgumentException，无残留。EngineVersion精确`26.05`，各RevisionRef按§4.1，NativeThreads≥1且须等于宿主冻结运行配置（模块不调用set_system改变进程全局）。RuntimeRevision指消费部署封存的运行身份，Envelope是该部署/算法路线/版本的实测保守上界，不是AsunImage安装或授权核验。系数全非负、FixedBytes>0，unknown envelope不得以零系数伪装已知；原Owner没有实测依据时不创建真实native运行Profile，受影响运行为NotReady。Precision.MaxAbsNativeCoordinate有限正；AllowStereoRealImages=true时MaxImageQuantizationMm有限非负，否则必须null。Profile.DrainTimeout为1..60s，请求不得超过此部署上限，set关闭使用该显式预算，不偷取最后请求值。这个软件表示限额由消费者精度用途发布，不猜客户公差；真实标定/计量验收不是工厂工作。所有class工厂声明仅列签名，具体工程必须提供方法体，不把无方法体class当可编译示例。

Joint实际装配不再留未命名构造器。仅AsunImage Adapter DLL新增`JointReconstructionAdaptersFactory`，显式引用CAL已批准Core/Joint公开程序集；Core/Simulator/WPF不新增CAL依赖。下列`CJ`为`Asun.Modules.CalibrationAssets.Joint`别名，类型是原上游公开合同。§8.1的Host私有binding仍保根内原响应；真实factory接下列完整公开伴随值，不复制上游codec/Bind实现。

```csharp
public sealed record JointReconstructionAdapterBinding(
    CJ.JointConsumerBindingProjection Projection, CJ.JointSetupExport Export,
    CJ.JointConsumerBindingRequest BindingRequest, ReconstructionRequest Request);
public sealed record JointReconstructionLifetime(bool Closing,
    bool SourceOwnerConfirmed, bool KnownWithdrawn, bool EpochGap,
    DateTimeOffset WatermarkValidUntilUtc, DateTimeOffset OperationDeadlineUtc);
public interface IJointReconstructionLifetimePort {
    JointReconstructionLifetime GetSnapshot(); // no IO; original Host root owns it
}
public sealed record JointReconstructionAdapters(IReconstructionAdapterSet Adapters,
    ICalibrationAssetSource CalibrationAssets);
public sealed class JointReconstructionAdaptersFactory {
    public JointReconstructionAdaptersFactory();
    public JointReconstructionAdapters Create(ReconstructionAdapterProfile profile,
        JointReconstructionAdapterBinding binding,
        IJointReconstructionLifetimePort lifetime, IReconstructionClock clock,
        IReconstructionDiagnostics diagnostics);
}
```

Host仅在§8.1同次原响应/复查/helper Applicable及强持原Owner得到确认后构造binding/lifetime。Create无IO/无native/无任务，按普通Profile及§8.1.2逐项校验，重用原CAL JointQualificationBinding.Bind核封存SourceQualification/BindingRequest纯值一致，原规范字节/摘要由CAL原codec计算。Bind不能证实来源，SourceOwnerConfirmed必须由原根已完成Task/响应关联产生；不接受单独bool为资格依据。null/非法同普通factory，失败不交付半个set/source。成功复制完整binding及Export.Bytes（计§8.1.4副本），set和source强持同一冻结对象至操作/文件/lease及所有Task真实退出；lifetime借用至关闭，不Dispose原CAL Owner。GetSnapshot为Host对原根/已知撤回/epoch的无IO投影，不静默再次Read资格；每开始read/gen/decode/reconstruct及异步Acquire返回后核Closing=false、原Owner确认、无撤回/gap、UTC不晚于水位/原OperationDeadline，单调request deadline另照常核。水位截止从BindingRequest.RecheckedWatermark原值展开，操作deadline从原request接纳时冻结，不得人为延长；未知/违约拒005，在途先排空，关后不获新native调用权。

返回source仅实现原ICalibrationAssetSource，Acquire严格匹配binding.Request.Calibration，Asset核Projection源asset，bytes独立核Export.File，唯一operation lease，迟到只归还。set.StructuredLight核整个绑定Request/capture/calibration/parameters及传入source为本次返回对象，其它模式拒007，不退普通loader。Joint loader用原File身份read camera_setup、meter→mm1000一次，再沿§7/8.2同一受控执行器/账本/tuple精度及清理链；Synthetic setup明确007且native0。构造顺序为组合根预留→§8.1 Resolve/复查/Bind→new JointReconstructionAdaptersFactory().Create→返回source/set端口传原Core工厂；set仍归组合根，Close按§8.1.4，不能只移交engine。§8.1提及的Host本地source/adapter是软件spy边界，真实可发布实现以本公开入口为准；公共程序集编译/运行仍未验。JRC01～06仍停BindingPrepared，真实采集/Export/native需要原Owner输入，不拼假Request。

受控执行器每个set一条专用CPU执行线程，在首次接纳且预留后才启动；方向串行，set只借给一个engine，至该engine真实Released/Dispose后才关闭set。每次native调用原Task/模型/临时file/asset/frame获取与释放Task立即记入同一有界操作账，最大64项在途原Task、最大512个lease/native对象登记（数量是软件防护，超限在发出下一调用前010）；完成记录只留总量/首末错误，不无界累积日志。无内部作业队列、同set并发操作022；同operation的方向序列和最后变换按Core唯一执行链串行。不同Host各自Create，互不共享可变模型/线程。同步HALCON在专用执行器运行，取消仅阻止下一步、等待当前返回，不以Task.Run/线程中断伪造终止。专用线程卡住按DrainUnknown强持；只有宿主独占进程确认终止后才按实际可归还资源恢复，不擅杀共享设备/宿主进程。

每方向native前计算checked上界：`FixedBytes + BytesPerInputByte*B + BytesPerCameraPixel*C + BytesPerPatternPixel*P + BytesPerPoint*Q + BytesPerVoxel*V`。B为该方向全部原stride×height输入bytes及setup实际bytes；C为该方向camera full raster总pixels（立体每camera一次）；P为本次生成完整pattern manifest的总pixels（非SL为0）；Q为请求MaxPoints的保守点上限；V为§7.4立体体素上限（非Stereo为0）。这些系数含内部模型、rectification/persistence/tuple/domain图重叠峰值，未知/不匹配Runtime/Profile或算术溢出010，不能以ROI面积替换full frame减账。上界须同时≤Parameters.MaxNativeBytes/Execution.Budget.Native；Managed及Result仍按§13.2预留，与Native分账，不把从native复制的tuple漏计。实际超过封存envelope即资源故障并停止新调用/有限清理，不声称已受硬内存隔离保护。纯managed Import原生费用0，不要求调用native或H-filter；其Managed/Result仍必需。

普通StructuredLight/Stereo在native前拒CalibrationKind=`CameraProjectorJointV1`（005/JointBindingRequired），只接受普通source可核`SHA(setup bytes)=Asset.Sha256`的setup；真实Joint仍专用Host/Adapter上下文，不能通过本factory只传两个RevisionRef获准。Surface逐项核source并复制结果、不调用native；Transform用§7.3的double tuple affine_trans_point_3d，不先GenImage1(real)量化、不重复应用、范围/非有限024，转换和来源保真。set.Profile/Envelope/Precision/Runtime revisions加入每方向Provenance及运行诊断，不替换AlgorithmRevision。

句柄释放按真实依赖逆序：等所有native/回调退出→clear_structured_light_model/clear_stereo_model/clear_object_model_3d/clear_camera_setup_model各自匹配清理→Dispose保存其handle的HTuple→Dispose临时HObject/数据tuple→关闭文件流并删除本操作唯一临时file→归还frame/asset/surface lease。HObject.Dispose不代替clear句柄，Clear抛错/卡住不得提前Dispose丢handle；继续关闭其它已证明无依赖的资源，保首业务错误和cleanup明细，失败对象与原Task强持，不反复clear制造双释放。正常全退出才QueryDrain=Released。set.DisposeAsync关闭接纳，按显式调用方已有DrainTimeout观察每在途操作一次；无在途立即完成，Unknown抛R3D-014并保持Query/Stop与全部原根可用，不能Dispose借用clock/diagnostics/source。

两原无UI Host的native装配固定：先预留§11根及Profile/envelope/输出预算→new ReconstructionAsunImageFactory().Create(profile,clock,diagnostics)→把set的四端口连同显式source/clock/diagnostics传ReconstructionFactory.Create→原Validate/Run/Stop→engine真实释放→set一次Dispose。根沿本set的64Task/512对象账强持set、engine、source/lease、profile，set未退出不能只移交engine；未知时宿主接收同一完整根后才移权，满槽不factory。A为已有SL消费者、B为已有Sensor/Stereo消费者，各自独立set，实测Profile与图像/标定来自它的Owner；软件spy只验证构造/预算/错误/Owner，绝不造“已知native envelope”供真实运行。正常构造未知Profile拒绝不是算法不支持；实际性能/Golden/native释放另验。

#### 8.2.1 CAL 0.3.3消费兼容影响

普通native托管复制账另明确：每方向最终槽数上界N取camera pixels（SL）/MaxPoints（Stereo）/输入N（Surface）；来源数上界S取N*manifest帧数/2*N/输入实际CSR条数。`ResultUpper=65536+192*N+256*S+8192*F+字符串账`，F为所有frame/asset/profile记录数，字符串账同§7.7.2；诊断层按§4.4.1额外相加。`ManagedUpper=4*(B+ResultUpper)+48*C+524288`，含借用input/setup、三个tuple及domain/mapping散射scratch、模型原值/adapter回执/Core冻结副本；各项checked且≤各自预算，所有多方向已留结果再累计、不能只看当前方向。结果和scratch任何额外副本均增加实际账；native预算仍上面封存envelope，不能拿此式声称HALCON内存已实测。Transform从source实际N/CSR计同ResultUpper/ManagedUpper，不改source原数组、不用N*1假计完整多帧来源。

已定向核对CAL 0.3.3-prep §7.4.6B/§9.4/§17.3：既有Joint API v1、同次Resolve原响应、JointConsumerBindingRequest/Projection/helper、Export两域身份与资格/根Owner边界保持；§8.1原接收内容沿用，不重算其向量。新增CameraLocalPlaneReader/CameraLocalPlaneV1及二维CameraSolution/参数初值、专用手眼方法不是camera-projector setup，IM-032不将局部平面或.dat相机参数冒JointSetupExport，不自动拼投影器外参。没有本次Joint Export及专用绑定时005，需组合/发布由CAL原Owner负责；IM-032只消费已给原setup。CAL自动参数也不改本模块min_gray_difference，§5.3独立建议来源/版本/人工采纳边界保持。实际Joint source/专用adapter公共程序集编译与资格Owner调用仍由本模块及两宿主实施验证，真实资产/Scope/水位由CAL/qualification提供，不把未知交接转成客户补算法设计。

## 9. 取消、超时、排空和恢复

1. 收到取消后发布 `CancelRequested`，停止尚未开始的方向和融合，不再接收新输入。
2. 当前 native operator 返回前不得释放输入图像、模型、标定或工作缓冲区。
3. native 调用与回调全部退出才发布 `Drained`；随后释放临时 native 对象和输入租约，发布 `ResourcesReleased`，最后发布唯一终态。
4. 排空归还成功后终态为 Cancelled（R3D-011）；可附已复制完成的部分候选，其 Quality=Partial，不把操作终态改为 Partial。不在取消信号后构造新融合结果。
5. Deadline 到期走相同排空流程，终态为 `TimedOut`。超时不隐式重试、不复用旧句柄。
6. 排空超过显式 `Execution.DrainTimeout`（范围 `1..60 s`；宿主可预填 5s）时返回非终态 ReconstructionReply：State=DrainUnknown、Drain=Unknown、Error=R3D-014、Result=null。租约仍由隔离上下文持有，禁止 ResourcesReleased/Completed/Cancelled/TimedOut。实例拒绝新请求；宿主保留 Query/StopAndDrain 入口，待真实退出或独占 worker 确认终止后再串行完成资源归还和原终态意图。不能把等待超时当作 native 停止。
7. 计算重试创建新的 `CalculationId`，保留原操作和失败证据；本模块无提交重试语义。
8. 进程崩溃/重启后，宿主根据原始不可变请求和已保存的输入快照重新计算；未知结果不推断为成功或失败。

停止意图以首次单调观察到的取消/到期冻结；同一次观察两者同时成立时Timeout优先，后来的信号不能改终态。StopAndDrain在已有终态时只返回同一已知快照，不追加CancelRequested或改Completed为Cancelled。Quality/操作终态独立：正常计算无失败方向为Completed，即使Quality=Unverified/Conflict/NotQualified；KeepSuccessfulDirections且有失败方向为Partial；RejectOperation遇任一方向失败停止后续，排空后Rejected，已复制候选可附但Quality=Partial，不给Fused；零成功方向为Rejected（不把AdapterFailure造成的零成功写NotObservable，只有确有无观测证据才用它）。基础设施失败为Failed，取消/到期按原冻结意图；DrainUnknown始终非终态。失败方向和不合格方向都不能缩小请求覆盖分母。

## 10. 可选 UI 契约（模块内嵌控件，不是产品工作台）

已有可选 UI 范围继续保留，全部算法/导入/变换/融合/建议均可无 UI 调用。控件只显示不可变结果与诊断，接收宿主注入的视口公开端口、资源、主题和命令；不复制 IM-065 测量工作台、不含 ROI/计量编辑、资产发布或最终质量放行。高级诊断用于算法工程师/维护；操作员默认只见影像、输入身份、状态、结果与一个下一步。角色/命令授权由宿主决定，控件不能把 AuthorityScope 字符串当作安全许可。

### 10.1 内嵌布局与真实控件组合

仅按物理屏 1920×1080 验证，记录 OS taskbar/窗口框/标题/状态栏实际扣除后的 client rectangle，DIP=实测像素/DPI 比例，不硬写 1080 为内容高度。默认比例相对于剩余 client：顶部命令/身份栏 48 DIP、底部状态栏 28 DIP；主体左方向/错误 Grid 18%（最少200 DIP）、中央图像/点云视口 60%（至少剩余宽的55%）、右参数/来源 22%（最少260 DIP）；下方诊断可折叠区占主体高≤22%，展开后视口仍占主区域高≥65%。高 DPI/英文长文字导致最小宽不足时右区改 AutoHideGroup，保留中央影像与可见取消/状态；不做其它分辨率矩阵。

- `DockLayoutManager` + `LayoutGroup`/`LayoutPanel`/`DocumentPanel`：中央“高度 / 原始点 / 有效域”标签与左右面板；工程角色可停靠/自动隐藏辅助区，取消/排空状态不能移入隐藏区。宿主保存纯布局版本，恢复失败回默认，不写算法参数或 UI 全局主题。控件内部不创建 ThemedWindow。
- 左 `GridControl` + `TableView.AllowPerPixelScrolling=true`：最多16方向，列为方向、完成状态、有效率、冲突数、来源 revision；行状态同时文字/图标，排序只改变显示顺序。选行联动视口该方向；Ctrl 多选仅对照，不能改变生产贡献集合。来源使用可展开明细表（FrameId、ordinal、曝光窗/PatternId），避免无语义 TreeList 堆叠。
- 右 `PropertyGridControl` 绑定只读已冻结 Profile/ExecutionSpec；类别“采集、标定、融合、资源”，可搜索。离线建议作为独立 draft object 显示，选中变化只更新 draft；显式“预检”后新请求执行，不修改在途或活动 Profile。输入单位紧随数值；范围/缺项原位显示并定位来源。
- 下方 `ChartControl` 的 `XYDiagram2D` 显示阶段时长与方向差异统计（真实统计有单位和分母），点击 bucket/方向只投影视口 domain；有限聚合 bins≤256，不把每个像素/点建成 chart object。展示降采样/色阶只能影响绘图，不覆盖数值、来源或 ValidMask。
- `FlyoutControl` 用于行内错误“影响 + 下一步”，绑定 PlacementTarget，IsOpen/StaysOpen 控制；重复忙/弱信号错误在同一行合并，不弹连续模态框。`SuperTip` 放在非显然的“一次变换、未知不确定度、排空等待”命令/标签；普通 SimpleButton 使用 ToolTip 中的 SuperTipControl，BarButtonItem 使用 SuperTip 属性，不猜控件属性。
- 色阶按冻结显示范围，有效高度为连续色、无效为透明/斜纹、冲突为橙色轮廓；无效不染成“低高度”。展示 isosurface 常驻“展示表面 / Display surface”，原始观测常驻“观测点 / Observed points”；未资格化显示“未验证 / Unverified”。字体跟随宿主主题，标题16DIP、正文13DIP、数值等宽，间距8/12/16DIP，状态动画只给非关键视图切换≤150ms、关闭动画时状态不延迟。

### 10.2 命令、联动、键盘和状态

固定可见主命令“预检 / 預檢 / Validate”“计算 / 計算 / Run”“取消 / 取消 / Cancel”；辅助“保存证据 / 儲存證據 / Save evidence”由宿主执行。无 Accept/Release/RetryDevice/生产参数发布按钮，无模块独立语言切换入口。候选灰度建议仅工程角色离线请求，不能把建议直接变成生产值。

状态与下一步：空输入→选择输入（宿主）；预检失败→定位缺项；可运行→计算；Running→取消；Draining→显示“正在结束计算 / 正在結束計算 / Finishing”；DrainUnknown→“结束状态未知 / 結束狀態未知 / Completion unknown”及“查询状态”（宿主）；Completed/Partial→核查来源或保存；Failed/Rejected→修正输入后新计算。关闭时先有限 StopAndDrain；Unknown 可把后台所有权交还宿主后仅卸载 UI 订阅，不能由控件 Dispose 核心/租约。

键盘顺序：命令→方向表→中央视口→参数/来源→诊断；F5 仅在可运行触发一次 Run，Esc 在 Running 请求取消一次，在 Flyout 内仅关闭 Flyout，Ctrl+S 只触发已授权 SaveEvidence；方向表上下键联动、Enter 展开来源；缺项焦点跳到对应参数，不抢用户其它操作焦点。稳定 AutomationId=R3D.Validate/Run/Cancel/DirectionList/Viewport/Parameters/Status/Errors，Flyout LiveSetting/LiveRegionChanged 和触发器 HelpText 用于屏幕阅读。三语各条状态、范围、原因/恢复文案必须有资源键，使用 `{count}`/`{direction}` 参数，不拼中文字符串。

UI bridge 每次只接收最新 OperationId/Sequence，进度更新合并≤10Hz，终态/错误不得丢弃；一次结果只取绘图子集，不重复整帧拷贝。语言/主题切换、Dock 布局重排、选择方向、关闭图表都不触发算法、不变 provenance。事件迟到到旧 UI generation 丢弃但记录计数。UI 时间/内存目标由消费者 Profile 采纳；本轮未执行真实 WPF/UIA 验证。

### 10.3 UI 公开接入形状

```csharp
public sealed record ReconstructionViewOptions(string CultureName,
    string ThemeName, bool CanRun, bool CanSuggest, bool CanSaveEvidence);
public interface IReconstructionViewCommands {
    ValueTask<ValidationReport> ValidateAsync(ReconstructionRequest request,
        CancellationToken cancellationToken);
    ValueTask<ReconstructionReply> RunAsync(ReconstructionRequest request,
        CancellationToken cancellationToken);
    ValueTask<ReconstructionOperationSnapshot> StopAndDrainAsync(string operationId,
        TimeSpan waitBudget, CancellationToken cancellationToken);
    ValueTask SaveEvidenceAsync(ReconstructionResult result,
        CancellationToken cancellationToken);
    ValueTask<ContrastRecommendation> RecommendAsync(
        ContrastRecommendationRequest request, CancellationToken cancellationToken);
}
public interface IReconstructionViewSession : IAsyncDisposable {
    void SetOptions(ReconstructionViewOptions options);
    void SetRequest(ReconstructionRequest request);
    void SetRecommendationInput(ContrastRecommendationRequest request);
    void Show(ReconstructionOperationSnapshot snapshot);
    void SetProgress(ReconstructionProgress progress);
    ReconstructionUiCloseSnapshot QueryClose();
    ValueTask<ReconstructionUiCloseSnapshot> CloseAsync(TimeSpan waitBudget,
        CancellationToken waitToken);
}
```

后续WPF `ReconstructionView : UserControl`有无参公开构造器，唯一入口为`Bind(IReconstructionViewCommands commands, ReconstructionViewOptions options, ReconstructionUiServices services)`返回IReconstructionViewSession。完整注入值与关闭语义见§10.4，旧二参数文字不是保留重载，不允许隐式创建默认viewport/source/语言包。Show/SetProgress在本控件Dispatcher调用，Core不引UI；核心Owner仍是宿主。CultureName支持zh-CN/zh-TW/en-US并可增资源；ThemeName只用宿主已有DevExpress25.2.3主题，不改Application全局状态。视口由宿主/公开IM-060能力组合，控件不自带第二套3D viewer算法。

### 10.4 显式视口Bridge、UI根和完整任务流

以下新增形状仅在`.Wpf`命名空间/可选WPF DLL；using System.Collections.Immutable及System.Windows。这是UI投影合同，不是新生产状态机或renderer。

```csharp
public enum ReconstructionDisplayKind { Height, ObservedPoints, Validity, Diagnostics }
public sealed record ReconstructionUiResources(string Revision,
    IReadOnlyDictionary<string, IReadOnlyDictionary<string, string>> Cultures);
public sealed record ReconstructionUiLimits(long MaxHeldBytes, int MaxDisplaySamples,
    int MaxPendingTasks, TimeSpan CleanupBudget);
public sealed record ReconstructionDisplayRequest(string BindingId, long Generation,
    string OperationId, long OperationSequence, SurfaceResult Surface,
    SurfaceGeometry Geometry, ReconstructionDisplayKind Kind,
    ImmutableArray<int> DisplaySlots,
    ImmutableArray<StructuredLightDiagnosticLayer> Diagnostics);
public sealed record ReconstructionDisplayReceipt(string BindingId, long Generation,
    bool Accepted, bool VisibleConfirmed, string? ErrorKey);
public sealed record ReconstructionViewportDetach(bool Detached, bool ResourcesReleased,
    string? ErrorKey);
public interface IReconstructionViewportBridge {
    UIElement Element { get; }
    ValueTask<ReconstructionDisplayReceipt> PresentAsync(
        ReconstructionDisplayRequest request, CancellationToken token);
    ValueTask<ReconstructionViewportDetach> DetachAsync(TimeSpan waitBudget,
        CancellationToken waitToken);
}
public sealed record ReconstructionUiCloseSnapshot(bool Closing, bool Detached,
    bool UiResourcesReleased, bool CoreResourcesReleased, int PendingOriginalTasks,
    string? ErrorKey);
public interface IReconstructionUiRetentionSlot {
    void Attach(IReconstructionViewSession session);
    void Track(Task originalTask);
    void RetainViewport(IReconstructionViewportBridge viewport);
    void ReleaseAfterConfirmedClose();
}
public sealed record ReconstructionUiServices(string BindingId,
    IReconstructionViewportBridge Viewport, ReconstructionUiResources Resources,
    ReconstructionUiLimits Limits, IReconstructionUiRetentionSlot Retention,
    IReconstructionClock Clock);
```

宿主先预留容量2的UI强持槽，再构造控件/Bind；slot跨窗口关闭继续由Host root强持，Attach/Track/RetainViewport正常返回为接管确认，不抛且不隐藏线程。满槽不Bind/不发Task；未确认时原root持有所有引用，不能丢session/任务。BindingId遵§4.1，Generation初值1，展示/输入/选层/语言改变checked递增，耗尽拒绝新投影并关闭；Limits全部显式，MaxDisplaySamples1..1,000,000、MaxPendingTasks至少16最多64、MaxHeldBytes正且≤宿主UI预约、CleanupBudget100ms..60s。MaxHeldBytes计输入深副本、当前结果借用payload、诊断、显示索引、所有迟到投影和Task元数据；根引用同对象不重复计，真正复制必另计，超限前拒绝且保原显示。构造器/Bind不运行算法/取得frame/启动IO；null或资源/element非法以ArgumentException拒绝，无半绑定。Element必须属于当前Dispatcher、未有Visual/Logical Parent且为宿主已经完成IM-060公开BindAsync的控件；禁止从Application.Current/静态DI找它。一个控件只有一绑定，重复Bind拒绝，不关旧session。

Host Bridge按Viewport现公开`ViewportControl.BindAsync(session,root,ViewportUiBindingOptions,token)`先绑定，OwnSession=false；保存原binding/root/Task。Present只消费已冻结结果/逐slot源关系并用IM-060公开surface/layer/update能力；不可表示的输入/权限/多层/C5关系明确返回Accepted=false，不发假flat来源、假VisibleConfirmed或新测量事实。IM-060确认可见才VisibleConfirmed=true，普通UI赋值只能Accepted。Detach调用原IViewportUiBinding.UnbindAsync并等真实presenter/renderer borrow归还；Detached与ResourcesReleased独立，Wait取消/Unloaded/Dispatcher结束不能当归还。该Bridge由实际宿主实现，UI不依赖其私有renderer/Source。借用session的关闭仍由宿主原viewport root负责，模块不Dispose别人session。

显示子集固定为：对N个原槽取K=min(N,MaxDisplaySamples)，slot(j)=floor(j*N/K)、j=0..K−1，checked Int64乘除，严格升序；无效槽仍保域/原因，不能只挑有效点提高显示覆盖。独立层按原slot保完整CSR、source refs、transform/provenance，多层不压成一个代表父；颜色/高度值读原immutable数组，DisplaySlots只是绘图索引，绝不改N/ValidFraction/结果。Diagnostics仅在原请求已输出层内选择，仍原Bytes/domain/units/hash，不重新计算M或phase。Bridge不能呈现diagnostics则标“当前视口不支持此图层”，仍可查数值/保存原证据，不代做renderer。Fused/方向切换用ResultId匹配Geometry；不存在选层明确空状态，不拿上一operation图冒本次结果。

所有session同步方法只允许所属Dispatcher（否则InvalidOperationException，调用前无状态改变）。SetRequest深复制/Validate身份，不触源；Running/Draining/Unknown时拒换当前输入，宿主可在自己draft保新请求。Validate命令走commands.ValidateAsync完整request检查，Run前仍由Core独立复检，不把ValidateResult当资格。每命令发出前预留Task槽/捕获输入generation，原ValueTask恰一次AsTask，Track原Task；禁双击/键盘重复Run。Run/Save/Recommend不在UI线程阻塞等待，保存由宿主事实Owner执行，完成前不能显示“已保存”。CanRun/CanSuggest/CanSaveEvidence是宿主投影，命令端仍检查真实权限；权限撤销先关闭对应命令接纳，已在途结果只按原Owner决定采用，不自动放行或发布。

Show仅接本绑定当前OperationId、严格更高snapshot.Sequence（首次可0）；SetProgress无Sequence字段，仅在同operation运行态按阶段有界计数合并，终态后丢弃迟到进度，不能伪造递增Core事件。多次进度最多10Hz/一项pending；终态/错误直接投递且只保最新snapshot，不建无界队列。每个DispatcherOperation.Task及Present原Task入根；Present完成必须核BindingId/generation/operation，旧代只归还引用不覆盖新图，错误呈现不改核心结果。关闭/切语同样提高generation，捕获旧代事件不能复活控件。

建议输入仅接受§5.3完整人工标签/32候选限制，commands.RecommendAsync调用同一无参ContrastRecommender；不得从现场图自造标签。Suggested/Abstain/Invalid/Cancelled完整显示，阈值与四来源/MethodVersion并列；来源任何一项改变立刻显示“建议已过期”。建议结果只为draft核对，不直接更新PatternSpec或生产Profile，没有“应用到生产”入口；宿主显式新Profile/新请求后再SetRequest/Validate/Run。与CAL自动参数服务不混用。

关闭顺序：Closing=true/关闭命令/提高generation→解绑事件与键盘/capture→若有run向commands.StopAndDrainAsync发一次独立有限停止→撤图/参数/Chart引用并调用Bridge.DetachAsync一次→有限观察所有原Run/Save/Recommend/Present/Dispatcher/Stop/Detach任务。每个清理任务独立try/有限观察，首业务错误保留，最大16项cleanup诊断；一个throw不跳过另一可安全收尾。UiResourcesReleased仅全部UI原Task退出及真实detach归还，CoreResourcesReleased仅原核心Released且run退出；QueryClose无IO，CloseAsync仅等待不重复发任务，waitToken取消只取消观察。DisposeAsync用Limits.CleanupBudget调用同一Close，未归还抛InvalidOperationException/UiCleanupUnknown，root继续保原任务/桥/结果，不能ReleaseAfterConfirmedClose；即使UI已Detached而Core未释放也保宿主核心根。真实确认两个分支均完成才退UI槽，Unknown不退容量、不重建默认viewer。原core/set/SurfaceData/viewport root分别归其Owner，本slot不替代它们的停止协议。

两个真实STA Host沿原A/B：各自线程创建Dispatcher/Window/View，Host先创建独立Viewport root/factory/session并OwnSession=false Bind，再将Element/bridge/完整资源/根/clock传本Bind→SetRequest→Validate/Run→Show原回执→Close确认→按原viewport协议关闭session/root→Window.Close/Dispatcher退出。A为工程Replay允许Suggest/Save，B为只读3D AOI复核CanRun=false/CanSuggest=false且Save按宿主权限；二者互不共享session/可变UI对象，关闭A不影响B。软件Fixture Limits=(8MiB,4096,32,1s)，仅防护例值不作产品帧时目标；输入沿原完整F0/F0-S并用已经实现的公开Viewer Bridge，缺Bridge不得填空UIElement冒完成。真实1920×1080/client/DPI/UIA/三语、关闭迟到与线程归还验收另门。

#### 10.4.1 Viewport 0.3.4的实际Host预绑定（WPF Assembly Contract v0.2）

本节只对齐[viewport §10.6～10.9](../viewport/DEVELOPMENT-GUIDE.md#106-公开bindingunbind与presenter借用)及其§10.6.1的实际消费者迁移；本模块`IReconstructionViewportBridge`、三参数ReconstructionView.Bind、结果/算法/Core/原UI根与Close不改。上文“宿主已经完成IM-060 Bind”现在必须满足以下公开装配，而非省略Lifetime的旧Options。Viewport无参Control及四参数Bind签名保持，Options尾部Lifetime在语法上可选、真实Bind必填；这不是已发布二进制兼容声明。

两个原STA Host各自沿既有有限HostOwner创建viewport root→所属Dispatcher上的`new ViewportControl()`→实际renderer端口→原factory/session→公开Bind→保存实际binding→一次session.AttachAsync→本模块Bind。创建session前将该**同Control**的`control.Presentation`传入`ViewportOptions.Presentation`，不得用另一个控件或只返回true的Host端口；若已有Host转发器，其CommitAsync/RevokeAsync须直接return同Control.Presentation的原Task，不能async包装替换原Commit/Revoke关联。Bind先安装空视图，Attach在成功Bind之后，不让Bind等待Attach形成互等。A/B仍OwnSession=false，来源/权限/请求、两个STA隔离、原核与视口root关闭顺序沿§10.4，不新建根绕过资源Unknown。

实际内置renderer通过`ViewportRendererFactory.Create(control, root, new ViewportRendererOptions(BackendPolicy.HalconRequired, profileNativeBytes, profileRasterBytes, profilePendingCount, cleanupBudget))`构造；四个Profile变量是宿主既有显示Profile提供的显式预算，非本模块另定物理/性能默认。检查其PortResult成功且Value非null后，`Value.Backend`传原ViewportOptions.Backend，`Value.Lifetime`传下面Bind的Lifetime；record本身不是Lifetime。二者必须来自同Control/root/renderer Owner，创建只冻结配置，原预留/实际native/Presenter归还仍viewport负责。已有Host自有backend/lifetime可以沿公开接口提供，不强制替换，但必须遵守本节同Owner/Submission/资源规则。内置CPU/surface payload能力保持上游§10.8边界；源payload不能保真表达时拒对应显示，不在本模块自写renderer或静默Raster替代Surface3D。两Host原8MiB本模块UI fixture限额不是HALCON窗口或1920×1080可见读回容量证明；原Profile必须另外核viewport的完整scene、旧代并存及上游§10.8至少16*clientWidth*clientHeight读回峰值，容量不足先拒，不自动放大本模块限额。

以下示例是宿主在原session创建后、Attach之前调用的准确公开形状；`rendererPorts`为上述成功Value，`uiBudget`是按同root/session既有额度批准的`ViewportUiExecutionBudget`，`language`来自宿主CultureName，`cleanupBudget`沿既有有限显示Profile。它们不是未定义的创建工具或新契约，也不是已编译/运行证据。

```csharp
// using Asun.UI.Viewports; using Asun.UI.Viewports.Wpf;
// session/root/control already belong to this Host.
var text = ViewportUiResourceCatalog.Get(language);
// Continue only when text.Outcome is Succeeded and text.Value is nonnull.
var options = new ViewportUiBindingOptions(
    BindingId: bindingId, OwnSession: false, Resources: text.Value!,
    UiCleanupBudget: cleanupBudget, Lifetime: rendererPorts.Lifetime,
    ExecutionBudget: uiBudget);
Task<PortResult<IViewportUiBinding>> originalBind =
    control.BindAsync(session, root, options, token);
// Original task is immediately retained by the existing Host root before observation.
var bound = await originalBind;
// Continue only when bound.Outcome is Succeeded and bound.Value is nonnull.
// Save bound.Value as this Bridge's binding; Attach once, then mount control as Element.
```

Catalog失败或Bind失败无Element交本模块；保原失败/Task及上游已预约根作有限清理。`uiBudget`三个值明确计viewport本方Tasks/资源快照/Presenter表/显示与读回费用，不能复用ReconstructionUiLimits数值冒已批准上游预约。Lifetime=null在Reserve/Dispatcher前007拒绝，无默认renderer；交叉Control/root/backend 016拒绝。成功返回`IViewportUiBinding : IPresentationPort`为同Control转发的实际binding，Host不造假binding。一个Lifetime实例不能同时安装到两个binding，Unbind后也仅在原Revoke/Return真实完成后才可串行复用。

自有Lifetime仅迁移`AcquirePresenterAsync(ViewportPresenterSubmission submission, CallContext call, CancellationToken ct)`的新第一参数（返回原`Task<PortResult<IViewportPresenterLease>>`），旧PresenterLeaseRequest重载不是后备入口。保存完整`submission.Request`、`submission.Presentation`、`submission.SourceCall`及原Acquire Task：Request给binding/generation/backend/presentation身份，Presentation含原backend Submit事实/ContextRevision/授权，SourceCall是原session/root签发调用；child参数call用于本次root步骤，不能覆盖SourceCall。ConfirmVisibleAsync仍核同原提交与当前授权/窗口/代号，Revoke/Return仍同Owner/同原身份；不可随手new receipt或PresentationId证明显示。直接消费内置Lifetime时无需在本模块实现这些成员。

Bridge.PresentAsync保持§10.4的逐slot/CSR/诊断输入，经原session的Attach/Update/Apply公开流程产生backend真实Submit→同Control.Presentation/同binding.Commit→完整Submission的Acquire→Confirm；不直接调用Lifetime绕过Core接纳/授权，不在Bridge另造CallContext、Root或SubmissionId。Bridge的Accepted仅表示对应显示请求已接纳，VisibleConfirmed只有匹配同binding/原提交/当前代的真实确认可为true；本模块Generation与viewport DisplayGeneration各自保原值并由Host显式关联，不能把重建OperationSequence cast成Viewport代。关门/撤权后Revoke仍路由原binding的原呈现清理，不以最新binding替换Owner。Host按需用binding.GetPresentations()关联原Commit/Acquire/Confirm/Revoke/Return及Cleanup快照；它只观察、不移交lease/重发任务，无需向本模块Bridge新增字段。原Unbind/Root/Close、Unknown强持和只停自己run边界保持，不以GetPresentations返回空或Commit完成宣称已归还。

Viewport资源与本模块§10.5资源是两个schema：Host显式取`ViewportUiResourceCatalog.Get(language)`，其Revision须精确`viewport-ui-text/1`、Text覆盖该Catalog.RequiredKeys及实际Host标签；不得把ReconstructionUiResources.Revision或旧fixture-text-1/七键快照塞入ViewportUiResources。本模块只维护重建文案，viewport必需键/单位/UIA/动态标签占位符由其原Owner定义。扩展culture使用宿主同schema完整快照，不自动回退英文；切换时Host向**原binding**调用SetResourcesAsync并检查回执，资源缺项/占位符错误拒绝且保持原快照，不刷新输入像素/重算、不擅自重Bind。实际LayerLabel/SourceLabel等附加文字逐项给当前语言，不用ID或CLR属性名猜显示标题。

窄验收沿§13.8原W01/W02/W03适用子例：缺Lifetime零Reserve/Acquire、跨Control/root拒绝、Bind前Commit拒绝、成功Bind后一次Attach与完整Submission原字段关联、重复同呈现返回同原Commit Task、自有Lifetime迁移旧签名不可采用、schema/必需键失败保持旧资源、旧代/撤权/关闭迟到Presenter仍原root Revoke→Return。只新增这些实际兼容断言，不重审原算法/三语表/Root/Close或重算旧向量；真实WPF/Renderer/可见读回/资源预算/双STA执行仍未验，保持原运行门。

### 10.5 三语资源及错误恢复

§10.4的关闭只停止由本session命令启动的run；B的只读外部Show不获取核心控制权、不发Stop，只卸自己的展示borrow。没有本UI启动run时CoreResourcesReleased表示“本UI未持有核心操作”，不能宣传外部核心已Released；外部run仍由宿主原根管理。SaveEvidenceAsync正常返回必须来自宿主原证据Owner的真实保存确认，迟到/Unknown由其原查询身份处理，控件不重发保存。

Resources.Cultures在Bind完整深复制，必须含zh-CN/zh-TW/en-US的全部下表键及§6全部错误键；其它culture由宿主注册同键快照扩展。无键/空串/占位符不匹配拒绝，保持原资源；Revision是宿主版本，切语言只重投影，不重新Run/读取像素。Scope/FrameId/hash等事实不翻译，日期/数值按culture格式并保mm/ns/byte等技术单位，数值与计数不变。下表是本模块全部固定用户文字的键基线，动态参数统一`{count}`/`{direction}`，不得把exception.Message直接当操作文案；原operator/message保诊断明细。Viewport内部资源沿其自身完整表，不复制第二套语言入口。

| 资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Title | 三维重建 | 三維重建 | 3D reconstruction |
| Validate / Run / Cancel | 预检 / 计算 / 取消 | 預檢 / 計算 / 取消 | Validate / Run / Cancel |
| Save / Suggest / Query | 保存证据 / 参数建议 / 查询状态 | 儲存證據 / 參數建議 / 查詢狀態 | Save evidence / Suggest parameters / Check status |
| Input / Direction / Status | 输入 / 方向 / 状态 | 輸入 / 方向 / 狀態 | Input / Direction / Status |
| Height / ObservedPoints / Validity | 高度 / 观测点 / 有效域 | 高度 / 觀測點 / 有效範圍 | Height / Observed points / Valid domain |
| Diagnostics / Parameters / Sources | 诊断 / 参数 / 来源 | 診斷 / 參數 / 來源 | Diagnostics / Parameters / Sources |
| Acquisition / Calibration / Fusion / Resources | 采集 / 标定 / 融合 / 资源 | 擷取 / 校正 / 融合 / 資源 | Acquisition / Calibration / Fusion / Resources |
| ValidFraction / Conflicts / Revision | 有效率 / 冲突数 / 修订 | 有效率 / 衝突數 / 修訂 | Valid fraction / Conflicts / Revision |
| Frame / Ordinal / Exposure / Pattern | 帧 / 序号 / 曝光区间 / 图案 | 影格 / 序號 / 曝光區間 / 圖案 | Frame / Ordinal / Exposure interval / Pattern |
| Empty / Ready / Validating / Accepted | 选择输入 / 可以计算 / 正在预检 / 请求已接纳 | 選擇輸入 / 可以計算 / 正在預檢 / 請求已接受 | Select input / Ready / Validating / Request accepted |
| Running / Draining / DrainUnknown | 正在计算 / 正在结束计算 / 结束状态未知 | 正在計算 / 正在結束計算 / 結束狀態未知 | Running / Finishing / Completion unknown |
| Drained / Released / Completed / Partial | 计算已结束 / 资源已归还 / 计算完成 / 部分结果 | 計算已結束 / 資源已歸還 / 計算完成 / 部分結果 | Work stopped / Resources released / Completed / Partial result |
| Rejected / Failed / Cancelled / TimedOut | 请求被拒绝 / 计算失败 / 已取消 / 已超时 | 請求已拒絕 / 計算失敗 / 已取消 / 已逾時 | Request rejected / Failed / Cancelled / Timed out |
| QualifiedCandidate / Unverified / Conflict | 资格候选 / 未验证 / 方向冲突 | 資格候選 / 未驗證 / 方向衝突 | Qualified candidate / Unverified / Direction conflict |
| NotObservable / NotQualified / Invalid | 无可观测结果 / 未满足要求 / 无效 | 無可觀測結果 / 未符合要求 / 無效 | Not observable / Requirements not met / Invalid |
| UncertaintyUnknown / DisplaySurface | 不确定度未知 / 展示表面 | 不確定度未知 / 顯示表面 | Uncertainty unknown / Display surface |
| Suggested / Abstain / RecommendationInvalid / RecommendationCancelled | 候选阈值 / 无可用建议 / 建议输入无效 / 建议已取消 | 候選閾值 / 無可用建議 / 建議輸入無效 / 建議已取消 | Candidate threshold / No suggestion / Invalid suggestion input / Suggestion cancelled |
| RecommendationExpired / DraftOnly | 建议已过期 / 仅供离线核对 | 建議已過期 / 僅供離線核對 | Suggestion expired / For offline review |
| Saving / Saved / SaveFailed | 正在保存 / 证据已保存 / 保存失败，请查询原保存任务 | 正在儲存 / 證據已儲存 / 儲存失敗，請查詢原儲存作業 | Saving / Evidence saved / Save failed; check the original save operation |
| LayerUnsupported / UiCleanupUnknown | 当前视口不支持此图层 / 界面资源尚未归还，请查询状态 | 目前視埠不支援此圖層 / 介面資源尚未歸還，請查詢狀態 | This layer is unsupported / UI resources are still in use; check status |
| OnceTransformTip | 仅应用一次已发布变换；已在目标坐标的输入跳过 | 僅套用一次已發佈轉換；已在目標座標的輸入略過 | Apply the published transform once; skip inputs already in the target frame |
| UncertaintyTip | 未知不确定度不表示零误差 | 未知不確定度不表示零誤差 | Unknown uncertainty does not mean zero error |
| DrainTip | 取消会请求停止；资源归还前不能重新计算 | 取消會要求停止；資源歸還前不可重新計算 | Cancel requests a stop; wait for resources before running again |
| Progress / DirectionCount | 已处理 {count} 项 / 方向 {direction} | 已處理 {count} 項 / 方向 {direction} | Processed {count} items / Direction {direction} |
| Reason0 / Reason1 / Reason2 / Reason3 | 有效 / 无对应 / 饱和 / 遮挡 | 有效 / 無對應 / 飽和 / 遮擋 | Valid / No correspondence / Saturated / Occluded |
| Reason4 / Reason5 / Reason6 / Reason7 | 超出范围 / 标定缺口 / 方向冲突 / 贡献方向不足 | 超出範圍 / 校正缺口 / 方向衝突 / 貢獻方向不足 | Out of range / Calibration gap / Direction conflict / Too few contributing directions |
| Reason8 / Reason9 / Reason10 / Reason11 | 插值来源 / 调制度低 / 深度不唯一 / 解码拒绝 | 插值來源 / 調制度低 / 深度不唯一 / 解碼拒絕 | Interpolated source / Weak modulation / Ambiguous depth / Decode rejected |

斜杠分组在实现中是逐个独立资源键，不把组合串拆作运行时语言解析。PropertyGrid本版只展示下述显式参数白名单（不自动枚举所有§4 CLR属性），以原字段路径作固定AutomationId，显示键采用`Parameter.<field>`；常用中文/繁体/英文为“灰度差阈值/灰階差閾值/Gray difference threshold”“图案宽度/圖案寬度/Pattern width”“图案高度/圖案高度/Pattern height”“条纹宽度/條紋寬度/Stripe width”“方向差异上限/方向差異上限/Direction disagreement limit”“贡献方向下限/貢獻方向下限/Minimum contributing directions”“执行期限/執行期限/Execution timeout”“排空期限/排空期限/Drain timeout”“托管预算/受控記憶體預算/Managed budget”“原生预算/原生記憶體預算/Native budget”“结果预算/結果預算/Result budget”。原Profile完整内容由来源Owner提供已封存原件供打开/复制，当前控件不自动展开未登记标签，不自动把未登记CLR属性名作为可见标签；新增可见字段须先扩同表资源并核三语，缺键不隐藏参数或用英文fallback。

错误键采用`Error.R3Dnnn`，恢复文字即下表，含影响/下一步；Range错误另有`ParameterRange`模板“{direction}：参数不在允许范围，请核对来源 / {direction}：參數不在允許範圍，請核對來源 / {direction}: parameter out of range; check its source”。诊断UIA Name/HelpText复用同一资源，不另写硬编码。

| 错误后缀 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| 001 | 请求无效；修正参数后新建计算 | 請求無效；修正參數後建立新計算 | Invalid request; fix parameters and start a new calculation |
| 002 | 输入身份不一致；重新冻结输入，勿混用 | 輸入身分不一致；重新凍結輸入，勿混用 | Input identity mismatch; freeze a new input set |
| 003 | 帧不完整；由宿主按批准方案重新采集 | 影格不完整；由宿主依核准方案重新擷取 | Incomplete frames; recapture through the host's approved workflow |
| 004 | 帧重复；保留原证据并修正输入 | 影格重複；保留原證據並修正輸入 | Duplicate frame; keep evidence and correct the input |
| 005 | 标定不可用；核对资产、有效期和用途 | 校正不可用；核對資產、有效期及用途 | Calibration unavailable; check asset, validity and use |
| 006 | 单位或坐标不匹配；提供匹配的已发布变换 | 單位或座標不相符；提供相符的已發佈轉換 | Unit or frame mismatch; provide a matching published transform |
| 007 | 此输入能力不支持；使用已登记路线 | 此輸入能力不支援；使用已登錄路線 | Unsupported input capability; use a registered route |
| 008 | 质量要求未满足；核查输入和质量配置 | 品質要求未滿足；核查輸入及品質設定 | Quality requirements not met; check input and quality profile |
| 009 | 方向结果冲突；核查冲突域和来源 | 方向結果衝突；核查衝突範圍及來源 | Direction results conflict; inspect the domain and sources |
| 010 | 资源预算不足；缩小请求或补齐部署上界 | 資源預算不足；縮小請求或補齊部署上界 | Resource budget insufficient; reduce the request or provide a deployment envelope |
| 011 | 计算已取消；资源已归还 | 計算已取消；資源已歸還 | Calculation cancelled; resources released |
| 012 | 计算已超时；查询原计算状态 | 計算已逾時；查詢原計算狀態 | Calculation timed out; check its original status |
| 013 | 适配器失败；查看诊断并确认排空 | 配接器失敗；查看診斷並確認排空 | Adapter failed; review diagnostics and confirm drain |
| 014 | 排空未确认；保留原实例并查询状态 | 排空未確認；保留原執行個體並查詢狀態 | Drain unconfirmed; retain the instance and check status |
| 015 | 版本不匹配；使用匹配的包和资产 | 版本不相符；使用相符的套件及資產 | Version mismatch; use matching packages and assets |
| 016 | 记录或结果未保留；查询原Owner，勿推断成功 | 紀錄或結果未保留；查詢原Owner，勿推定成功 | Record or result not retained; query its owner without inferring success |
| 017 | 资格配置缺失；保留候选，补齐后新建计算 | 資格設定缺失；保留候選，補齊後建立新計算 | Qualification profile missing; retain candidates and use a new calculation after fixing it |
| 018 | 已发布变换不可用；查询原发布Owner | 已發佈轉換不可用；查詢原發佈Owner | Published transform unavailable; query its publisher |
| 019 | 变换作用域不匹配；提供匹配的快照 | 轉換作用範圍不相符；提供相符快照 | Transform scope mismatch; provide a matching snapshot |
| 020 | 变换已应用或标记矛盾；核对输入来源 | 轉換已套用或標記矛盾；核對輸入來源 | Transform already applied or inconsistent; check input provenance |
| 021 | 采集时序不匹配；重新提供完整采集 | 擷取時序不相符；重新提供完整擷取 | Acquisition timing mismatch; provide a new complete capture |
| 022 | 实例忙或正在关闭；查询原操作 | 執行個體忙碌或正在關閉；查詢原作業 | Instance busy or closing; check the original operation |
| 023 | 操作身份重复；查询原操作，勿重算 | 作業身分重複；查詢原作業，勿重算 | Duplicate operation identity; query the original operation |
| 024 | 来源无法完整表达；保留原表面并核对来源 | 來源無法完整表達；保留原表面並核對來源 | Source cannot be represented completely; retain the original surface and inspect its provenance |

只有原错误证实Released时才能用011的资源归还文字；Unknown优先显示014/UiCleanupUnknown，不让Cancel按钮响应冒充取消终态。全部文案与SuperTip、动态参数、状态、原因、命令在1920×1080三语真实测；长诊断可展开复制，关键恢复可见，不靠截图冒交互验收。

## 11. 无 UI 最小 Host 与两个消费者

以下是后续实施的 C# 调用形状，并非当前已编译代码。Core 实例只通过 `new ReconstructionFactory().Create(ports)` 构造，无 DI、WPF、产品 Shell、数据库或设备 SDK。Host 实现输入端口、固定时钟、诊断和隔离 Owner；同一端口作为显式实参传入适配方法，不能让适配器暗读全局资产目录。下列 IHostRetentionSlots/IHostRetentionSlot 只在 BCL 测试Host内定义，是宿主所有权闭包，不加入Core API或可发布Simulator。

消费`CameraProjectorJointV1`时，原A/B改用§8.1的组合Host外层：先预留组合根→CAL原Resolve内部响应捕获→同Owner复查→原Bind Applicable→完整Joint伴随对象/专用source与adapter封存→原`ReconstructionFactory.Create`/Validate/ReconstructAsync→有限收尾。不能在本节普通RunHostAsync之外先丢弃CAL资格对象再仅传RevisionRef；组合根是§8.1.4的64Task/8输出槽扩展，原Core三Task/Simulator五Task流程和两个原fixture不改。Joint纯软件双Host的完整输入/Bind与失败断言见§8.1.3，实际native场景另按§8.1.2受影响门验收。

宿主启动时建立容量2的强持槽（双Host各占一槽，连同已移交隔离的未决实例共用该上限）；TryReserve是factory前的原子容量预留，满时拒绝创建、退出5。预留槽由Host管理器强引用，含两个ID、engine引用、最多3个原始Task位置（run/stop/dispose；不是WaitAsync包装Task）、首业务错误/cleanup错误与最终退出码。Attach/Track/RecordOutcome及释放方法在预留容量内无分配失败/不抛异常；同一角色Task只登记一次，Track立即登记已发出Task。ReleaseAfterTransferConfirmed仅移交原槽引用及容量计费，不让未决隔离实例提前腾出名额；后台真实收尾后才释放容量，不转移到无界队列。槽未释放时该实例/两个ID保持未决，不能另建替代实例。这里只冻结最小Host内部操作契约，不引入平台DI/全局静态状态。

```csharp
// 以下声明由独立测试Host实现，管理器和槽跨RunHostAsync返回继续强持。
interface IHostRetentionSlots {
    bool TryReserve(string operationId, string calculationId, out IHostRetentionSlot slot);
}
interface IHostRetentionSlot {
    void Attach(IReconstruction3D engine);
    void Track(Task originalTask);
    IReadOnlyList<Task> Work { get; }
    void RecordOutcome(int exitCode, string? firstBusinessError,
        IReadOnlyList<string> cleanupErrors);
    void ReleaseAfterCleanClose();
    void ReleaseAfterTransferConfirmed();
}
// 放在独立 BCL Exe 的 Host 类内；取消/停止等待与资源释放分开。
static async Task<int> RunHostAsync(ReconstructionPorts ports,
    ReconstructionRequest request, IReconstructionIsolationOwner isolation,
    IHostRetentionSlots slots,
    CancellationToken cancellationToken)
{
    if (!slots.TryReserve(request.OperationId, request.CalculationId, out var slot)) return 5;
    IReconstruction3D? engine = null;
    Task<ReconstructionReply>? run = null;
    int exitCode = 4;
    string? firstBusinessError = null;
    var cleanupErrors = new List<string>(5);
    bool started = false;
    try {
        engine = new ReconstructionFactory().Create(ports);
        slot.Attach(engine);
        var validation = engine.Validate(request.Input, request.Parameters, request.Fusion);
        if (!validation.IsAccepted) {
            exitCode = 2;
            firstBusinessError = validation.Errors.Count > 0
                ? validation.Errors[0].Code : "ValidationRejected";
        } else {
            started = true;
            run = engine.ReconstructAsync(request, cancellationToken).AsTask();
            slot.Track(run);
            var reply = await run.WaitAsync(request.Parameters.Timeout
                + request.Input.Execution.DrainTimeout + TimeSpan.FromSeconds(2));
            if (reply.Operation.Drain != DrainState.Released) {
                exitCode = 3;
                firstBusinessError = reply.Operation.Error?.Code ?? "DrainNotReleased";
            } else if (reply.Operation.State is not (OperationState.Completed or OperationState.Partial)) {
                exitCode = 4;
                firstBusinessError = reply.Operation.Error?.Code ?? "OperationNotSuccessful";
            } else {
                // 此处消费reply.Operation.Result；消费异常也进入catch/finally。
                // 候选结果不在本Host转成质量放行；0此时只是待收尾的局部值。
                exitCode = 0;
            }
        }
    } catch (Exception ex) {
        firstBusinessError ??= ex.GetType().Name;
        if (exitCode == 0) exitCode = 4;
    } finally {
        bool cleanClose = engine is null; // factory未成功，未创建执行上下文。
        bool canDispose = !started;
        if (engine is not null && started) {
            try {
                var stop = engine.StopAndDrainAsync(request.OperationId,
                    TimeSpan.FromSeconds(2), CancellationToken.None).AsTask();
                slot.Track(stop);
                var closed = await stop.WaitAsync(TimeSpan.FromSeconds(3));
                canDispose = closed.Drain == DrainState.Released;
                if (!canDispose) cleanupErrors.Add("Stop:DrainNotReleased");
            } catch (Exception ex) {
                canDispose = false;
                cleanupErrors.Add("Stop:" + ex.GetType().Name);
            }
            // Released快照不代替原run Task退出；故障Task允许已完成但需观察异常。
            if (canDispose && run is not null) {
                try { await run.WaitAsync(TimeSpan.FromSeconds(1)); }
                catch (Exception ex) {
                    cleanupErrors.Add("RunObservation:" + ex.GetType().Name);
                    canDispose = run.IsCompleted;
                }
            }
        }
        if (engine is not null && canDispose) {
            try {
                Task dispose = engine.DisposeAsync().AsTask();
                slot.Track(dispose);
                await dispose.WaitAsync(request.Input.Execution.DrainTimeout + TimeSpan.FromSeconds(1));
                cleanClose = true;
                foreach (Task task in slot.Work) cleanClose &= task.IsCompleted;
                if (!cleanClose) cleanupErrors.Add("PendingOriginalTask");
            } catch (Exception ex) {
                cleanClose = false;
                cleanupErrors.Add("Dispose:" + ex.GetType().Name);
            }
        }
        if ((!cleanClose || cleanupErrors.Count != 0) && exitCode == 0) exitCode = 5;
        bool transferred = false;
        if (!cleanClose && engine is not null) {
            try {
                // 正常返回才算接收确认；槽在确认前一直强持engine/原Task/身份。
                isolation.Retain(engine, engine.Query(request.OperationId), slot.Work);
                transferred = true;
            } catch (Exception ex) {
                cleanupErrors.Add("Retain:" + ex.GetType().Name);
                // 接收器违约也保留原槽，后台管理器继续有限观察；不重建实例。
            }
        }
        slot.RecordOutcome(exitCode, firstBusinessError, cleanupErrors);
        if (cleanClose) slot.ReleaseAfterCleanClose();
        else if (transferred) slot.ReleaseAfterTransferConfirmed();
        // 未确认转移不释放原槽。所有cleanup错误独立保存，不覆盖首业务错误。
    }
    return exitCode; // 只在finally之后决定对外退出码。
}
```

退出码0的充分必要条件是业务消费完成、Stop（若启动过run）报告Released、Dispose正常完成、全部已发出原run/stop/dispose Task均IsCompleted、没有cleanup错误；未发出的Task不补造。先业务失败时保持原2/3/4，cleanup错误另列；业务原本成功但收尾Unknown/异常/未完成改为5。Retain接收成功仅转移Owner，不使本次Host恢复0；后台最终恢复也不改写原回执。槽的RecordOutcome先把必要ID/错误/退出码复制到宿主诊断记录，再释放无未决引用的槽，不因清槽丢错误。

finally 的截止点与 run 的等待截止点都有限；WaitAsync 超时只停止观察，不杀原任务。Query在隔离/Dispose失败后仍无IO、可用且不抛出；不存在记录则返回§5.1.1的R3D-016快照。Retain应幂等：同engine/两个ID的重复确认只返回原接收，不二次释放；接收端必须在返回前独立强持engine/两个ID并复制最多三项原Task引用到预留容量，不能把slot.Work视图留作将来读取清槽后的数据。正常返回才转移清理权；违约抛错即使已被动保存引用，原槽仍唯一Owner，接收端没有并发清理权。后台仅在已登记原Task全部退出/异常已观察、资源真实释放后清槽；同一未决实例不替换、不重复Dispose副作用、不使用await using自动释放。factory抛异常且未创建engine时清空预留槽、返回业务失败4；实现不得在factory抛出前遗留未交付实例/任务。

两个无 UI 消费者使用同一 Core DLL、各自 factory/ports/实例：

| 宿主 | 显式构造与调用 | 可判定接入结果 |
|---|---|---|
| A：结构光实验 Replay | 用 §13 F0 的完整 Mono8 manifest、PatternSpec/标定 scope、AlreadyInOutput 和预算创建请求；Frames/CalibrationAssets 提供只读离线资产，StructuredLight 注入端口；SurfaceInputs/Stereo/Surface/Transform=null，无融合。纯 Core 验证中换成 synthetic StructuredLight 端口，仍收到相同 Frames/Assets 实参 | Validate→ReconstructAsync→消费 SourceFrame 候选→有限 Stop/Dispose；native 版必须另过真实 Adapter 门。A 可后来绑定可选视图，无 UI 模式完全不加载 WPF |
| B：3D AOI 表面 Replay | 用 F0-S 的两方向表面、显式 SurfaceInputs/Surface、ApplyPublished/Transform、IM-033 快照和 Grid/Fusion 构造请求；StructuredLight/Stereo/CalibrationAssets=null；Frames 注入不应被调用的拒绝 source | 两方向先 import、各应用一次、同格等权融合；无需投影器、相机 SDK、WPF、产品 AOI 私表/配方。纯 Core 用 synthetic Surface/Transform，不声称 HALCON 变换已验证 |

A/B 同时启动各自操作；A 取消、source 断连、消费结果抛异常、关闭或变更显示语言都不能改变 B 的状态、租约、矩阵/输出和事件。最小 Host 不自己估计方向变换，不把 synthetic 资产送进真实 AsunImage 适配器。Core.Tests/TestHost内部stub只实现现有端口与故障闩锁，输入/输出带synthetic hash，不是可发布Simulator包；真实设备/项目接入在宿主层另验。

## 12. 正常、边界和失败案例

| 案例 | 预期行为 |
|---|---|
| 单方向完整结构光组，标定有效 | 逐序列解码/重建，返回方向结果；无融合时 `Fused=null` |
| 两个方向同坐标、支持域重叠 | 显式声明无需变换或验证 IM-033 已发布快照后，仅当两方向都完成且通过质量门时按批准策略融合；保留贡献计数 |
| 方向间局部遮挡互补 | 只在贡献数达到门槛的共同支持格融合；单方向互补域留在 PerDirection，不补洞；有可见性证据才用 Occluded，不得将无支撑区域补零 |
| 某方向缺一个 pattern | 在 decode 前 `R3D-003 MissingFrame`；不得使用剩余帧重建 |
| 同 ordinal 但 PatternId 不同 | `R3D-002 IdentityMismatch`；不得按到达顺序替换 |
| 镜面/多路径材料 | 质量 Gate 失败或返回 `NotObservable/NotQualified`；不承诺单算子覆盖 |
| 单位为 inch、坐标图不同 | `R3D-006 UnitOrCoordinateMismatch` 或 `R3D-019 TransformScopeMismatch`；由上游/IM-033 发布匹配快照后新请求，IM-032 不自行转换 |
| 有效比例低于 Profile | 返回显式质量和缺失域；不能变成完整高度场 |
| 融合冲突超过阈值 | 冲突域保留为 `Conflict`，结果可部分可读但非 Qualified |
| 方向失败后成功数低于融合门槛 | 保留 `PerDirection` 和 `DirectionIssues`；`Fused=null`，返回 `FusionIssue(InsufficientCompletedDirections, completed, required)`；不降低门槛 |
| 方向数达到门槛但无共同支持元素 | 保留 `PerDirection`；`Fused=null`，返回 `FusionIssue(NoElementMetContributionMinimum, completed, required)`；总体质量 `NotQualified` |
| 取消发生在解码中 | 请求取消，等待 native 返回并排空，最终 `Cancelled` |
| 超时发生在融合中 | 停止后排空，最终 `TimedOut`；不自动启动第二次融合 |
| native 内存预算不足 | 分配前或检测到峰值时 `R3D-010`；输入租约正常归还 |
| 适配器抛出未知异常 | `R3D-013 AdapterFailure`，保留原异常摘要和排空结果 |
| 进程重启后结果回执未知 | 宿主查询原 operation 或重新计算；不生成“成功”替代事实 |

## 13. 测试与验收矩阵

### 13.1 测试层

| 层级 | 最小覆盖 | 证据 |
|---|---|---|
| Unit | 单位/坐标校验、序列排序、原因码、冲突分类、确定性融合数学 | 输入/输出快照、期望与实际 |
| Contract | 候选字段、枚举、版本、hash、事件顺序、错误码 | Validator 报告 |
| Adapter | 真实 `ImageLibDotNet` 公共签名、句柄转移、异常和排空 | operator trace、句柄生命周期日志 |
| Integration | 结构光工具与 3D AOI 两个不同宿主调用同一包 | 端到端 trace、结果和资源报告 |
| Golden/Replay | 平面、台阶、球、遮挡、反光、黑表面、方向冲突、缺帧 | 数据集 hash、差异报告 |
| Fault injection | 取消、超时、重复帧、版本错、内存上限、适配器异常、进程重启 | recovery evidence |
| Performance | 冷/热、单/多方向、不同像素和点数、每实例并发1、独立实例负载、P50/P95/P99 | 原始 benchmark，不用平均值代替长尾 |
| UIA（有 UI 时） | AutomationId、键盘、DPI、三语、八态、取消后排空 | UIA/截图报告 |

### 13.2 纯 Core 的确定性 fixture 与必需 case

纯值/调度测试唯一工程见 A.1；`Microsoft.NET.Sdk`、`net10.0`、`OutputType=Exe`，仅引用 Core 与 BCL。测试端口类在该测试工程实现本文接口，不引入待选测试包、HALCON、WPF、真实文件/SDK/数据库。fixture 与 oracle 是以下明示值，不从被测实现生成期望；每 case 新 factory/实例/操作 ID，不复用有状态 adapter。

**F0（synthetic 光学 Host A）**：Request.ApiVersion="0.2"，每方向DeclaredSupport=1、每实例source/adapter私有，所有未另填可空字段为null；AlgorithmProfileId=algo-A/AlgorithmProfileRevision=rev(algo-A)，ResultId/CalculationId与本case固定身份一一对应、Surface.SourceFrameIds/SourceDirectionIds从CSR推导、ValidFraction=1/ConflictFraction=0、TransformProvenance=count0/unitScale1，时间/资源字典由固定clock/账本填入。所有 revision 用 `RevisionRef(id, SHA256(UTF8(id)))` 小写 hex，只有 FrameRef.Revision 用实际 Bytes 的 SHA256；这些 hash 是软件 fixture 身份，非真实发布资产。UTC 起点固定 `2026-10-10T00:00:00Z`，单调时钟初始 0，以受控 clock 推进。InputSetId=fixture-A、epoch=epoch-A、方向=A、SourceFrame=OutputFrame=world、TransformUse=AlreadyInOutput/count=0/previous=null。6个 FrameId=A0..A5、Width=2/Height=1/Mono8/stride=2、Bytes=[10,20]、ordinal=0..5，PatternId 顺序为 g0,g1,p0,p1,p2,p3，前2个 Kind=GrayCode，其余 PhaseShift；曝光窗 `[i*10000+1000,i*10000+2000]ns`、稳定窗 `[i*10000,i*10000+3000]ns`、同 attempt-A/device-A/clock-A/曝光 revision；AcquiredAt 对应曝光末端。TimingProfile=timing-A，MaxSequenceSpan=1s、MaxStereoSkew=0、SceneStationaryVerified=true（仅 synthetic 声明）。Calibration=cal-A/world、ValidFrom=起点−1day、ValidTo=起点+1day；scope qualification=q-A、NativeLengthToMm=1、CameraIndex=0/ProjectorIndex=1、camera=2×1/projector=8×8；Pattern HybridVertical/global/8×8/minStripe=4/single=null/minGrayDifference=10/phaseDiagnostics=false、manifest 正是上列6项。该 manifest 只测试托管顺序，不声称等于真实 HALCON 生成布局；真实 Adapter 必须以 gen_structured_light_pattern 的真实资产核对。QualificationProfile=null，ZMin/ZMax=null，MaxPixels=2，Roi/Grid/Stereo/DirectionTransforms=null；Parameters MinFrames=6、valid/invalid/disagreement=null、MaxDirections=16、Timeout=1s、Partial=RejectOperation、Fusion=null。Budget 的 Managed/Native/Result 均64MiB（MaxNativeBytes 同值）、MaxPoints=16、MaxVoxelCells=16、DrainTimeout=1s。AuthorityScope=fixture-only、Deadline=null。

测试光学端口接收 Frames/Assets，按 descriptor 获取六个租约；资产 source 提供明确 synthetic 字节，仅模拟端口使用，不能交真实 AsunImage。输出固定2×1 CameraSamples：X=[0,1]、Y=[0,0]、Z=[−0.25,0]mm，mask=[true,true]、reason=[0,0]、contribution=[1,1]、conflict=[0,0]、Uncertainty=null、Quality=Unverified。每像素 CSR 含 A0..A5 六条完整 row=0/column=0或1 的来源，offsets=[0,6,12]；provenance 有 synthetic 与输入/Profile hash。Adapter QueryDrain 在闩锁开前为 Pending/ActiveCalls=1，开后 Drained/ActiveCalls=0/Callbacks=0；租约各计数归还一次。测试 clock 是 BCL Host 的 IReconstructionClock 实现，不靠实际睡眠制造时序。

**F0-S（synthetic 表面 Host B）**：沿用 F0 的时钟、预算/超时/正单位和版本规则（两个Request.ApiVersion="0.2"），AlgorithmProfileId/Revision改algo-B、每方向DeclaredSupport=1、结果ID及CSR摘要按各自输入生成，InputSetId=fixture-B/epoch-B；两个方向 B0、B1 各一 FrameRef Kind=HeightField、PixelFormat=HeightFieldMm、2×1、ordinal=0；各FrameRevision分别SHA256(UTF8("surface:B0:X=0,1;Y=0,0;Z=-0.25,0"))/SHA256(UTF8("surface:B1:X=0,1;Y=0,0;Z=0.25,0.5"))、AcquiredAt为固定起点、PatternId/ExposureProfileId=null，Acquisition.Frames=[]、Calibrations=[]、Calibration=null、Pattern/Stereo=null、SourceFrame 分别 source-B0/source-B1、OutputFrame=world；source 表面已是 mm，DirectionCalibration分别为cal-B0/cal-B1并与对应transform引用相等。B0 Z=[−0.25,0]、B1 Z=[0.25,0.5]，各 X=[0,1]、Y=[0,0]、mask全true、reason全0、contribution全1、CSR每像素一条原传感器来源、offsets=[0,1,2]、Quality=Unverified。TransformUses 均 ApplyPublished/count=0/previous=null；PublishedSnapshot=t-B/published=true/withdrawn=false/IsHashVerified=true/epoch-B，目标world，每方向独立 transform/calibration revision，12元素矩阵为 `[1,0,0,0,0,1,0,0,0,0,1,0]`，模拟 Transform 端口只做恒等并标记 count=1。qualification=q-B（synthetic）、MinFrames=0、MinValid=0.5/MaxInvalid=0.5、MaxDisagreement=0.5mm；Grid=2×1/X0=0/Y0=0/StepX=StepY=1mm/MaxCenterDistance=0.5mm/MaxSpread=0.25mm，MinContributing=2、EqualSupported、Partial=KeepSuccessfulDirections。预期 Fused.Z=[0,0.25]、CSR offsets=[0,2,4]、contribution=[2,2]、conflict=[0,0]、Uncertainty=null，正常完整合成候选为Unverified；Partial/Conflict按支持与冲突标记，任何合成结果都不能QualifiedCandidate。Profile gate 在这里仅验证数学条件，不是生产资格；真实 QualifiedCandidate 须真实计量资格。

| case ID | 从 fixture 作出的唯一变化/触发 | 必须断言（完整性/数值/资源） |
|---|---|---|
| R01 | F0 正常 | Completed/Released，2像素含负值和零，六帧逐像素来源、无 Fused，租约各归还一次 |
| R02 | Directions空、Frames空、尺寸0三个子例 | 各 R3D-001/Rejected，source/adapter 调用次数0；所有子例必跑 |
| R03 | 缺A2；重复ordinal；错PatternId；跨attempt四子例 | 分别 R3D-003/004/002/021，在 decode 前拒绝，不能按文件名修复 |
| R04 | 改曝光窗跨稳定末端；clock域不一致；过期标定三子例 | R3D-021/021/005，无 native 工作 |
| R05 | F0-S 正常 | 两次 import/各一次 Transform；Fused数值/CSR/方向计数如上，Unverified不变 |
| R06 | 差异门改0.49；另例B0只支持cell0、B1只支持cell1 | 前例返回两格全无效Fused/Conflict/reason6/CSR且contribution=0，不丢冲突证据；后例 Fused=null/NoElementMetContributionMinimum，不借邻格 |
| R07 | B1 adapter报错后真实Drained | B0保留、B1 DirectionIssue，Fused=null/InsufficientCompletedDirections、OverallQuality=Partial；零成功子例不返回成功 |
| R08 | B0改PointCloud/3×1，X=[0,0,1]/Y全0/Z=[0,0.5,0]，来源SampleIndex=0..2/CSR一致，MaxSpread=0.25；边界子例将第二点Z改0.25 | 前例AmbiguousDepth/不贡献，保留两来源；等号子例可稳定选真实点；不选高/低层 |
| R09 | B0第0点X=0.5、第二点mask=false/XYZ=null；另子例第0点X=1.5（最右半开外边界） | 0.5进入cell1；外边界排除；距离/ROI分母不随结果缩小 |
| R10 | ApplyPublished输入count=1；另例AlreadyInOutput/source=world/count=1带历史发布provenance | 前例R3D-020；后例Transform调用0，count保持1、不得全拒已变换输入 |
| R11 | 缺/撤回/IsHashVerified=false快照；错epoch/FromFrame/CalibrationRevision子例 | R3D-018或019；均无第二次变换或融合，原始坐标不得贴world标签 |
| R12 | 用闩锁保持A在途，重复两个ID/提交另一新ID | DuplicateOperation/BusyOrClosing，不排队、不覆盖原Query记录；ID两个维度分别检查 |
| R13 | 接纳后修改调用方列表/矩阵/参数引用 | 输出/provenance不变，深复制受预算计入，端口不读修改后的源列表 |
| R14 | Adapter运行闩锁前请求取消，再开闩锁 | 信号后不开新方向/融合；开前不Dispose租约；开后Cancelled/Released，仅一个终态 |
| R15 | 单调clock到Timeout；另例Deadline更早并在接纳后UTC回拨 | TimedOut唯一、Deadline更早生效，UTC回拨不延长，等待native真实退出 |
| R16 | native/callback闩锁不打开，推进DrainTimeout | DrainUnknown/R3D-014/Result=null，无Drained/Released/终态，新请求Busy；再开闩锁只归还一次并发原终态 |
| R17 | adapter Stop忽略取消且任务不完成；重复Stop；取消Stop等待令牌 | Core观察有界，保留原Task/Owner；等待取消不撤销停止；迟到回调不写新操作 |
| R18 | 两个无UI Host同时执行；A source断连/消费异常/关闭；另子例业务成功但Dispose永不结束、Dispose抛错、Stop返回Unknown、Retain违约抛错；业务失败叠加Dispose抛错；预留槽满与factory抛错子例 | 正常成功仅在原run/stop/dispose三Task均退出且Released/Dispose成功后0；业务成功但任一收尾失败/未知为5，业务失败首2/3/4不被cleanup覆盖。首业务错误与cleanup错误均保留；factory前槽满不创建实例，factory抛错清预留槽。Retain正常返回前原槽强持engine/三原Task/两个ID，抛错后原槽仍在且非零，不重建未决实例。B输出/Query/资源不变；Unknown不await using或Dispose在用资源 |
| R19 | 256条终态后第257条、再查最早ID | 有界FIFO；R3D-016不是原操作失败；不得驱逐在途；新进程不冒称持久去重 |
| R20 | 将F0尺寸改4096×4096、MaxPixels相应放宽但Managed/Result仍64MiB；另子例超像素/points/voxel及体素乘法溢出 | R3D-010，无分配后成功、无自动tile/降采样；各子例明确预算命中位置 |
| R21 | 依次将F0第0点XYZ=null/mask=false/contribution=0，reason=WeakModulation/Saturated/Interpolated/Occluded四子例；Occluded带上游原因provenance | 无效XYZ=null/contribution=0；Z=0仍合法；无观测证据不强称Occluded；score不当mm不确定度 |
| R22 | 错CSR末项、错XYZ长度、非有限值、空來源子例 | 坏adapter/source输出统一R3D-024；请求中的非有限值预检为R3D-001，不能生成Qualified/有效融合；保留原错误定位 |
| R23 | 仅引用Core，直接 `new ContrastRecommender()`；阈值候选[10,20]、labelled contrasts=(5,false),(15,true),(25,true)及有效revision | Suggested=10，FA均0、FR为0/1，TA为2/1、TN均1、MethodVersion固定；去掉负类/空或null集合/重复或越界候选/null样本/非法revision/null request各返回Invalid、不抛预期输入异常。labels=(25,false),(15,true)且candidates=[10,20]为Abstain。已取消令牌含null request返回Cancelled且空Evidence/null阈值；合法请求循环中取消亦同，来源仅保留基础校验有效项。Suggested/Abstain完整计数/四来源齐备；无需DI/反射/重建factory/native/UI |
| R24 | 诊断接收器抛异常；进度/旧UI generation迟到 | 计算结果不变，有诊断失效warning；核心无Dispatcher，事件Sequence/Drained→Released→终态顺序成立 |
| R25 | API major不匹配/旧结果回退；synthetic含不支持SampleKind/格式 | R3D-015/007，不静默解析或切路线；旧不可变字节/hash/历史provenance保留 |

R01～R25 每 case 独立且全部子例必跑。普通 case 外层5s，R12～R18每 case10s；固定clock驱动计算/排空期限，真实 `Task.WaitAsync` 是 harness 观察保护，不伪造 native 已退出。suite总观察截止180s，外层独占测试进程240s；fixture创建、闩锁等待、case finally、suite清理均在期限内。闩锁用 TaskCompletionSource + RunContinuationsAsynchronously，失败 finally 打开本 case 自建闩锁并有限观察，未完成任务交本 Host隔离Owner；绝不清理其它进程/目录。任一失败/未完成/必需子例跳过输出 ID 并退出非零（断言=1，fixture/期限/未完成=2），只有全部完成通过为0。外层240s到期终止本次独占测试子进程、记录未完成ID并非零，不宣称资源排空通过。

### 13.3 Simulator、真实 Adapter、WPF 的后续验证

TestHost 是独立net10.0 BCL Exe，已接收Core切片仍只引用Core/BCL，用本测试Host内部端口stub从F0/F0-S接入双Host并按§14跑明示BenchmarkProfile，不增加Simulator编译依赖。Core.Tests中的stub只是协调反例，不能代替可发布Simulator；本轮发布模拟包的双Host接入在Simulator.Tests按§13.6验证。没有正式目标返回NotEvaluated，不能把执行完成当性能达标；运行期限由Profile冻结且外层增加有限排空余量。

Simulator 的独立公开形状、脚本、控制、调用和验收在§13.4～13.7冻结；2026-10-10主控已接收六项规格为ModuleCoreImplementationReady，仅明示值/端口/脚本/控制/资源Owner和两个无UI Host，本轮不创建工程。Core已接收范围及其内部stub保留；可发布Simulator只由自己的工程实现，双消费者及S01～S03直接引用它，不能把Core.Tests私有stub作为发布包。Simulator.Tests为net10.0 BCL Exe，仅引用Simulator/Core，真实Adapter/WPF验证仍是下段独立门；实际编译/运行/性能未执行。

真实 AsunImage 适配验证另需同一版本实际图案/资产与图像：结构光 manifest/四相位/无domain/正负高度、立体两pair不同原图/整流坐标与setup坐标、m3d_pairwise缺失/来源不完整、重复纹理/反光/遮挡、不确定度未知、bbox/资源envelope、取消/故障真实排空。逐对CSR必须可重建全部 FrameId、pair/sample、两端原图子像素射线；从 isosurface 补洞的点有效率为0。对比的公制公差/误接收/拒收、超大图资源/期限来自已采纳消费者 Profile。WPF验证仅固定1920×1080 viewport，真实控件/三语/键盘/UIA/窗口关闭，不能以Console模拟替代。此次没有编写或执行任何上述测试。

### 13.4 可发布 Simulator：唯一构造与有限脚本

程序集 `Asun.Modules.Reconstruction3D.Simulator.dll`、namespace `Asun.Modules.Reconstruction3D.Simulation`，仅引用Core与.NET 10 BCL，不引用Core.Tests、HALCON、WPF、产品/设备/数据库。职责为两个离线消费者重现端口值/故障和资源交接，不重建真实图像、不生成公制真值、不估计配准。既有Core构造保留，§4的可选角色/诊断增量已于2026-10-11接收；§7.6 decode-only C1/S1六项规格同日已接收为`ModuleCoreImplementationReady`，以下原模拟控制类型仍在Simulator包。

```csharp
using System.Collections.Immutable;

namespace Asun.Modules.Reconstruction3D.Simulation;

public enum SimulationPoint {
    FrameAcquire = 0, CalibrationAcquire = 1, SurfaceAcquire = 2, DirectionExecute = 3,
    TransformExecute = 4, CallbackExit = 5, FrameRelease = 6, CalibrationRelease = 7,
    SurfaceRelease = 8, MaskAcquire = 9, MaskRelease = 10
}
public enum SimulationOutcome { Continue, Reject, Fail }
public enum SimulationCancellation { Observe, CompleteLate }
public enum SimulationEventKind {
    RootCreated = 0, WorkStarted = 1, StepEntered = 2, StepCompleted = 3,
    LeaseAcquired = 4, StopRequested = 5, Draining = 6, DrainBudgetExpired = 7,
    WorkFailed = 8, CallbackExited = 9, LeaseReleased = 10, Drained = 11,
    ResourcesReleased = 12, Disposed = 13
}
public sealed record SimulationStep(string StepId, string DirectionId,
    SimulationPoint Point, string ResourceId, TimeSpan NotBefore,
    string? GateId, SimulationCancellation Cancellation,
    SimulationOutcome Outcome, string? ErrorCode);
public sealed record SimulationFrame(string DirectionId, FrameRef Descriptor,
    int RowStrideBytes, ImmutableArray<byte> Bytes);
public sealed record SimulationCalibration(string DirectionId,
    RevisionRef Asset, ImmutableArray<byte> Bytes);
public sealed record SimulationDirection(string DirectionId,
    AdapterDirectionResult RawObservation);
public sealed record ReconstructionSimulationScript(string Version,
    string ScriptId, ulong Seed, ReconstructionRequest Request,
    ImmutableArray<SimulationFrame> Frames,
    ImmutableArray<SimulationCalibration> Calibrations,
    ImmutableArray<SimulationDirection> Directions,
    ImmutableArray<SimulationStep> Steps, ByteCount MaxSnapshotBytes);
public sealed record SimulationScriptError(string Code, string Path, string ReasonKey);
public sealed record SimulationScriptValidation(bool IsValid,
    ImmutableArray<SimulationScriptError> Errors);
public interface ISimulationGates {
    bool Contains(string gateId);
    ValueTask WaitAsync(string gateId, CancellationToken cancellationToken);
    bool Release(string gateId);
}
public sealed record SimulationEvent(long Sequence, string OperationId,
    string CalculationId, string? StepId, SimulationEventKind Kind, DrainState Drain,
    long ActiveWork, long PendingCallbacks, long ActiveLeases, string? ErrorKey);
public sealed record SimulationSnapshot(string OperationId, string CalculationId,
    DrainState Drain, bool StopRequested, long ActiveWork,
    long PendingCallbacks, long ActiveLeases, long PendingLeaseReleases,
    long AcquiredLeases, long ReleasedLeases, long DroppedEvents,
    ImmutableArray<SimulationEvent> Events);
public sealed record SimulationStopReply(SimulationSnapshot Snapshot,
    bool IsDisposed);
public interface IReconstructionSimulation : IAsyncDisposable {
    ReconstructionPorts Ports { get; }
    ReconstructionRequest Request { get; }
    RevisionRef SyntheticRevision { get; }
    SimulationSnapshot Query();
    ValueTask<SimulationStopReply> StopAndDrainAsync(TimeSpan waitBudget,
        CancellationToken cancellationToken = default);
}
```

创建入口唯一为 `public sealed class ReconstructionSimulationFactory`，公开无参构造器，公开常量 `ScriptVersion="reconstruction-simulator-v1"`，公开方法 `SimulationScriptValidation Validate(ReconstructionSimulationScript? script)` 和 `IReconstructionSimulation Create(ReconstructionSimulationScript script, IReconstructionClock clock, ISimulationGates gates, IReconstructionDiagnostics diagnostics)`。Create不启动工作/获取租约，只做同Validate校验、预算与深复制，返回独立根Owner；所有端口通过返回的Ports取得，不靠反射/DI/隐藏初始化。Validate无副作用；非法/null脚本返回错误列表。Create非法脚本抛 `ArgumentException`（ParamName=script）、任一null注入端口抛 `ArgumentNullException`，均在注册实例/任务前，不遗留资源。端口实现类型为包私有，消费者只用本文接口。Create成功后Request是冻结深复制，Host把它原样传给Core；同实例只执行该OperationId/CalculationId一次，不提供Reset/换脚本/随机热改/设备控制入口。

**Simulator 单一不可变输入边界**：上述持久公开集合及gate构造参数统一为.NET 10 `System.Collections.Immutable` 的ImmutableArray（框架引用，不新增待选NuGet包）；字节载荷也用ImmutableArray<byte>，不在脚本中接受可能别名可变array的ReadOnlyMemory。default/IsDefault不是空集合，Validate返回SIM-001；允许空时必须用ImmutableArray<T>.Empty，元素为null同样SIM-001。Records/字符串不可变，但Core类型的IReadOnlyList/IReadOnlyDictionary签名保留原接收范围：**Simulator入口额外要求其全部非null嵌套集合实际为boxed ImmutableArray<T>或ImmutableDictionary<K,V>**（具体元素类型与Core声明一致，ImmutableArray非default），包括Request的方向/帧/时序/manifest/配对/矩阵/变换、RawObservation的XYZ/mask/CSR/摘要/provenance/warnings/resource字典。可空字段仍可null；任何List、array、ReadOnlyCollection、builder或自定义不稳定实现均在读取Count/索引/枚举之前按类型拒绝SIM-001/对应Path，不尝试边枚举边猜快照，也不调用其自定义getter。ImmutableDictionary仅用于Core已声明的string→long等字典，采用StringComparer.Ordinal，key/value皆已冻结值。此限制仅是Simulator脚本准入，不改Core公开API及通用调用方的接收规则。

Validate/Create共用内部唯一PrepareSnapshot过程：先类型/IsDefault及每层硬数量门，随后checked预算，再把该**同一不可变图**复制为Simulator拥有的不可变规范快照（含有界字节拷贝），最后仅在规范快照上做hash/绑定/语义校验；不先Validate调用方对象、稍后重读它复制。Validate丢弃该规范快照，仅返回不可变Errors；Create在它自己的单次PrepareSnapshot中校验并直接保留同一规范快照，不要求调用者先调用Validate。若调用者对同一script分别Validate/Create，两次都读同一immutable对象图；用with生成另一个script就是新输入，不能当成前一个验证结果。禁止从builder/Unsafe/CollectionsMarshal/MemoryMarshal无拷贝转换后继续写共享存储，Host构造ImmutableArray.Create/ToImmutableArray时先独占其源buffer，之后只提交不可变值；Simulator不会承诺对违反不可变集合契约的unsafe篡改提供原子快照。正常调用者后续改原List/array/builder，或换本地变量，不影响已提交不可变图和根Owner。

Simulator.Request、返回RawObservation及Query/StopReply也必须只含上述不可变嵌套集合；Errors/Events每次封装从私有builder ToImmutable而来，builder/ring buffer绝不外露，不将内部会变化的数组cast成IReadOnlyList返回。Query在锁内捕获同一账本字段与事件序列成不可变快照，锁外返回；后续事件逐出/修改账本不能改变旧Snapshot。Core端口仍要求ReadOnlyMemory<byte>的lease.Bytes/SerializedCameraSetup，Simulator从冻结字节按已核预算给每lease独立复制buffer后才暴露ROM，不能把它指向输入载荷或root共享buffer；ROM仅是lease只读契约，不被误认为防止外部MemoryMarshal写入的安全屏障。该leasebuffer只归该lease Owner，归还后不复用给下一lease；任何从ROM来的外部准备载荷都须在Host独占时先限额拷贝为ImmutableArray，再进入本边界。四倍预算原式保持，输入冻结/规范快照/lease/回执占用按同式计入，禁止为不可变改造增加无预算复制。

有限值与校验算法按以下固定顺序执行，Errors按该顺序/输入索引输出，不加载真实资产：

1. Version精确等于ScriptVersion；ScriptId非空≤128、无控制字符；Request满足已接收Core值契约、ApiVersion=0.2、两个ID非空。Seed任意ulong；首发不使用Random、不随seed扰动测量，seed仅标识可复现场景/来源，值全部由脚本给定。相同版本/seed/冻结脚本和同一clock/gate控制顺序得到相同端口值、错误/事件顺序；真实调度耗时/线程ID不是确定性结果。不同seed仅SyntheticRevision不同，不声称生成独立计量样本。
2. Directions与Request.Input.Directions一一对应，数1..16；Frames最多256，光学模式完整一一绑定每方向FrameRef，Mono8/stride/实际bytes/hash满足§5.1.1。传感器Frames=[]；DirectionCapture的表面描述保留在Request，SurfaceAcquire从Directions读取RawObservation。光学Calibrations按每方向一个条目，Asset等于该方向scope及Request.Calibration.Asset；传感器Calibrations=[]。标定bytes为1..4096长度synthetic载荷、不交给HALCON，hash精确等于Asset.Sha256。描述revision和字节相符才校验通过；不拿标定字节模拟真实geometry。
3. 每RawObservation是该方向SourceFrame/mm的SurfaceResult/SurfaceGeometry，满足§4全部数组/CSR/原因码/有限值，CalculationId等于Request.CalculationId、Mode一致、各ResultId唯一。每方向N≤4096，所有方向总N≤65536；每元素Sources≤256，CSR总≤1048576。Result/Geometry无native句柄、UncertaintyMm全null；Quality允许Unverified/Partial/Conflict/NotObservable/NotQualified/Invalid，拒绝QualifiedCandidate，任何synthetic输出不得被脚本伪造真实资格。一般输入尚未应用IM-033，Transforms为ApplicationCount=0/AlreadyInOutput/NativeLengthToMm=1的原始provenance；传感器输入AlreadyInOutput/PreviousApplicationCount=1时允许已有count1，但Snapshot必须精确等于PreviouslyAppliedSnapshot且SourceFrame=OutputFrame，不再启动模拟Transform。ApplyPublished输入仍只接受count0，Core目标变换分支另按请求执行。输入SourceFrameIds/DirectionIds摘要从CSR校验，不因seed造新FrameId。传感器原输入可有Partial/mask，光学输出是明示候选，不是从bytes推算的三角测量。
4. MaxSnapshotBytes显式1..16MiB，同时所有输入深复制不超过Request.Budget.Managed/Result；Frames字节≤8MiB、Calibration合计≤65536bytes。checked Int64预估baseBytes（每原byte=1、XYZ三个nullable double按48bytes/元素、mask/reason按2bytes/元素、两个int数组按8bytes/元素、CSR offset按4bytes、来源按256bytes/条、其余字符串按2*Length+32、DTO每项按512bytes），保守预留totalBytes=checked(4*baseBytes+524288)；4倍覆盖冻结输入/源租约副本/adapter回执/变换拷贝峰值，固定512KiB覆盖有限事件/控制wait/账本，不允许实现额外无预算缓存。totalBytes必须≤MaxSnapshotBytes及请求Managed/Result；返回Core的结果复制仍由Core本身执行预算。所有重复拷贝计入、不共享调用方可变数组。越界/溢出返回SIM-003，不分配后假成功；Native/GPU账本始终0。执行期间保留最多256条查询事件和≤128个阶段状态、最多1个执行方向；不设无界线程/队列/缓存。
5. Steps最多128、StepId唯一非空≤128，DirectionId已绑定；时间NotBefore相对实例第一次adapter调用登记的operationStart，范围0..60s、tick有限非负。该start全operation只登记一次，方向/transform不重置。ResourceId规则在§13.5，无重复(point,direction,resource)；没有给出的计算/acquire步骤默认立即Continue/Observe，CallbackExit/Release默认立即Continue/CompleteLate（释放使用不可取消的根清理观察），不自动补随机失败。GateId可null或非空≤128，每脚本最多32个不同gate，不能与其它实例共享gate对象；Unknown/迟到由有限时间+指定gate组合形成，不提供“强杀成功”脚本动作。
6. Continue必须ErrorCode=null；Reject按Point收紧：FrameAcquire只R3D-003、CalibrationAcquire只R3D-005、SurfaceAcquire只R3D-024、DirectionExecute只R3D-007/008/024、TransformExecute只R3D-007；不符合阶段的值为SIM-004。Fail只允许上述五个Point且ErrorCode=R3D-013，不得配成图像原因/PASS。CallbackExit/各种Release只允许Continue/CompleteLate；要模拟释放未完成采用关闭gate，不注入不可恢复释放异常再造第二个Dispose。脚本只能声明本模式实际会执行的阶段及resource：Frames/Calibration对应光学、Surface对应传感器、Transform只对应ApplyPublished；未知资源/无法到达的模式阶段返回SIM-002，不默默跳过故障。故障事件固定ReasonKey，不允许任意脚本文案/秘密凭据。Core Busy/重复/资格/版本等预检由Core真实实现产生，不由Simulator替它发终态。

脚本校验错误Code固定SIM-001 InvalidScript（Version/必填/枚举/形状）、SIM-002 BindingMismatch（身份/资产/坐标/CSR绑定）、SIM-003 ResourceLimit（数量/bytes/时间越界）、SIM-004 UnsupportedOutcome（非法阶段/错误组合）；ReasonKey分别 `R3D.Sim.InvalidScript/BindingMismatch/ResourceLimit/UnsupportedOutcome`，Path形如`Steps[2].GateId`/`Directions[0].RawObservation.Geometry`，不把完整Bytes/客户信息写错误。基础null脚本Path=script。错误键交宿主三语资源，模拟包无UI/本地化选择入口。

SyntheticRevision规则固定：Id="synthetic:"+ScriptId（ScriptId在此收紧≤96字符），Sha256=SHA256(UTF8(Version+"\n"+ScriptId+"\n"+Seed.ToString(InvariantCulture)))小写hex。它是场景身份**不等于脚本全文hash/签名或生产资产**；完整可复现输入必须保留深复制Request/脚本及控制顺序。每返回RawObservation的Provenance追加此revision且不得删原输入来源；AlgorithmRevision/帧/标定/变换revision仍各保留，不以同一身份hash冒充内容完整性证明。脚本换值要新ScriptId/两个操作ID，不重用身份。Synthetic标志通过revision与Unverified/Partial等候选质量同时保留，下游不因门槛字段齐全把它当计量资格。

**角色/诊断模拟增量**：ScriptVersion仍为v1，Sequence/Diagnostics=null及DiagnosticLayers.Empty的所有旧脚本语义/费用式保持。新script的Sequence.Patterns、Diagnostics.Layers、RawObservation.DiagnosticLayers及每层Domain/Values/SourceFrames逐层执行上述非default不可变边界；增量version/角色/支持域/shape依§4验证，unsupported请求在Create前SIM-004、未知version/非法字段SIM-001，身份/hash/域/遗漏或多交层SIM-002，数量/费用SIM-003。每层Origin=Simulator、RuntimeRevision精确为该script的SyntheticRevision、AlgorithmRevision仍原请求；Create不重写诊断runtime/hash。生成图hash只核字段格式与冻结绑定，Simulator不运行gen/decode、不声称证明其为真实HALCON布局；真实图案逐像素/hash校验只由Adapter执行。脚本RawObservation是明示数值，持久化开关不生成phase，缺请求层不得用随机值补造。新增诊断的baseBytes按§4.4.1每层费用一次加入，避免又按其DTO/数组双算；Sequence及请求新增record/字符串按原规则计入。四倍`4*baseBytes+524288`及16MiB脚本限保持，所有返回/Core复制仍计入各自峰值，不绕开MaxOutputBytes/MaxLayers。Transform模拟器保持同一immutable诊断层及内容hash，不乘矩阵。DirectionExecute/CallbackExit/Release现有gate覆盖诊断值返回与迟到/释放，不另造无消费者后台Task；正常与失败均沿同一root账本/五原Task恢复。

### 13.5 模拟执行、控制与资源唯一 Owner

**公开clock/gate可直接构造**：`public sealed class SimulationClock : IReconstructionClock`，无设备/BCL定时线程，公开构造 `SimulationClock(DateTimeOffset initialUtc)`（UTC offset=0），Timestamp以TimeSpan ticks计、初始0；`void Advance(TimeSpan delta)`范围0..60s/次、checked累加，UtcNow同增；WaitUntilAsync以登记start+budget等待，到点完成、同到期按登记序唤醒，已到期立即完成，取消只撤销该wait且OCE，Elapsed不得回退/负start/未来start（非法throw ArgumentOutOfRangeException）。Advance/读取/wait登记线程安全，以锁冻结时间和移出待唤醒列表，锁外完成TaskCompletionSource(RunContinuationsAsynchronously)，最多512个未完成wait，满时InvalidOperationException，不丢已登记wait；模拟停止取消内部timer观察时要移除wait登记。clock由Host拥有，不提供回拨/重置；这里的OCE是控制等待，不是伪造Core已取消完成。

`public sealed class SimulationGates : ISimulationGates`，公开构造 `SimulationGates(ImmutableArray<string> gateIds)`，非default、0..32个唯一有效ID，开始全部关闭；default/null元素/非法或重复ID均ArgumentException(gateIds)，检查数量后复制到私有Ordinal字典，不保留调用方builder或任何可变集合别名。每gate单向Release，不可Reset。WaitAsync未知ID抛ArgumentException、已释放立即完成，否则登记可取消wait（总≤128），取消只移除该等待；Release未知ID=false、已释放=true，无二次完成；释放时按登记序在锁外完成所有wait。clock/gate均只属于本模拟实例，不进入静态状态。注入其它实现必须保持这些语义/有限容量，Create在开始前要求script全部GateId已在注入gates登记；通过上述公开Contains查询，false为Create ArgumentException(gates)，此方法无IO/不改变gate。超pending容量InvalidOperationException；都是控制器输入/容量错误，已登记wait不受影响，Host保留根槽并记录非零。宿主每次Create提供新且独占的控制器；同一个factory实例用实例私有弱身份表拒绝重复注入（ArgumentException），跨factory仍由宿主显式隔离，不宣称用static全局表验证其它实例。弱表条目不强持已释放root，不建跨进程注册表。

步骤执行按point精确定位，不按墙钟、线程完成先后或任意“脚本下一项”消费：

| Point / ResourceId | 确定调用及完成路径 | 取消、故障及Owner |
|---|---|---|
| FrameAcquire / FrameId | optical adapter按FrameRef.SequenceOrdinal取得本方向全部帧；source核对Descriptor/冻结字节，产生IFrameLease | acquire前登记ActiveWork并持有原Task；late取得只交原operation，不启动新阶段 |
| CalibrationAcquire / Asset.Id | optical adapter在帧后取得该方向唯一ICalibrationAssetLease，返回synthetic bytes | 同一方向一次；不同方向可独立租约，不共享释放Task |
| SurfaceAcquire / DirectionId | Import adapter调用SurfaceInputs.AcquireAsync，lease.Value为冻结RawObservation副本 | 表面源不用设备/文件/FrameSource；late回执必须归还原lease |
| DirectionExecute / DirectionId | structured-light、stereo各自方法在所有输入lease取得后，按该步骤返回RawObservation候选；import先校验其surface lease再返回该同值候选 | 三者是互斥请求模式，执行方法参数必须与冻结Request/方向/端口实例匹配；不实际decode/disparity，不从图推高 |
| TransformExecute / DirectionId | ApplyAsync核对发布矩阵/源值绑定，仅模拟12元素恒等矩阵（精确[1,0,0,0,0,1,0,0,0,0,1,0]）；复制XYZ不改变数值，Frame改ToFrame/Transforms count=1、snapshot/hash匹配，保留CSR | 非恒等矩阵明确R3D-007/SIM-TransformUnsupported，不借托管重写HALCON；正常B消费者用恒等fixture，实际任意变换仍真实Adapter门 |
| CallbackExit / DirectionId+"/reconstruct" 或 DirectionId+"/transform" | 每重建/导入或变换调用各至多模拟一个回调退出闩锁；ActiveWork完成不表示回调已退出 | 回调只登记/退出计数，不改写managed结果或下一operation；stop后late出口仍完成原QueryDrain；ResourceId区分两个阶段，不能用同一步骤消费两次 |
| FrameRelease / FrameId；CalibrationRelease / Asset.Id；SurfaceRelease / DirectionId | 每lease的DisposeAsync唯一Task应用本release步骤后ReleasedLeases++、ActiveLeases-- | DisposeAsync幂等共享同Task；Release gate仅允许它自然完成，不能从外部强减计数或重新造lease；release不受调用方已取消令牌中断 |

所有source/adapter调用在入口绑定一个已登记operation，方向按请求顺序串行；source签名没有OperationId，因此由该实例adapter为本次异步调用建立明确的私有context token并沿调用链使用（可用实例持有的AsyncLocal只定位该token，不用static全局状态），外部对Ports source直接Acquire没有token时抛ReconstructionAdapterException/R3D-013、AdapterCode=SIM-SourceContextMissing，不创建lease。adapter调用在锁内单飞登记；执行同一point/resource重复或另一方向重叠抛R3D-013/SIM-DuplicateCall，不启动第二Task、不覆盖原上下文。不同方向按请求序各可执行一次，方向重建后其transform可执行一次；必须上一调用callback/lease清理退出才开始下一调用，正常方向Released不把root标Disposed或阻止下个合法方向。Core与Ports使用同一factory所给root；错误注入其它source/资产/参数对象或source快照不匹配一律SIM-BindingMismatch/R3D-013，进入前拒绝。Stop/Query不消费脚本步骤、不创建新工作；同一端口故障只用原OperationId/CalculationId的AdapterFailureContext，不允许latest。传感器Request仅Surface adapter；其它模式端口仍由包实现但调用不匹配方法为R3D-007/SIM-ModeMismatch，无资源。

进入步骤先发布StepEntered，随后等待clock NotBefore与gate**两个条件都满足**，二者Wait Task要登记且finally移除/观察，不能只WhenAny放行。NotBefore=0或clock.Elapsed(operationStart)已达到它时不调用正预算WaitUntilAsync；GateId=null不调用gate.Wait，立即视为该条件完成。Observe在等待或执行拷贝块边界观察操作取消；CompleteLate忽略业务停止令牌继续等待已登记条件，但不忽略根Owner保留/计数、不新起后续工作。CallbackExit在DirectionExecute/TransformExecute进入前已登记且每调用最多一个，不是每source一个；acquire阶段取消则没有尚未登记的callback。CallbackExit/Release必须Cancellation=CompleteLate，其他值Validate返回SIM-004。任一取消后停止启动新方向/步骤，例外仅当前已登记步骤的late完成、已取得资源的逆序release、已登记CallbackExit；后两者是排空，不是新计算。当前执行step在停止前已全部条件满足时以先冻结的结果/故障完成；同时到期按§9终态意图，Simulator不替Core选择Cancelled/TimedOut。

故障Outcome在等待条件满足后触发：Reject抛ReconstructionAdapterException，Error.Code为脚本ErrorCode/Recoverable=true/Stage=SimulationPoint名称/AdapterCode=SIM-Rejected；Fail同型、R3D-013/Recoverable=false/AdapterCode=SIM-Failed。原始source的拒绝/失败也同型，由adapter向Core原样保留且在逆序release后抛；§9 PartialResultPolicy处理正常/拒绝/部分/Failed终态。没有成功方向不能伪Partial；B0正常+B1 Reject/Fail且KeepSuccessfulDirections应有B0产物+DirectionIssue/Fused=null，而不是Simulator自己制造Core OperationState.Partial。Observe收到取消抛OCE（token是该operation内部linked停止token），经过同样callback/资源排空；CompleteLate在stop后拿到的候选丢弃、不发成功结果，late source拿到lease即归还。应用变换不修改RawObservation缓存，任务正常/异常均回到原方向上下文。

根Owner只在Create成功时建立一个上下文；各端口/lease强引用同一root，root持有全部原work/wait/callback/release Task及只读payload。登记在先，原Task赋值在释放锁之前，异步运行在锁外；已取得lease按surface或calibration→frames逆序归还。模拟ActiveNativeCalls固定0（没有native），AdapterDrainSnapshot.PendingCallbacks是真实模拟回调数；State必须综合work/source等待/lease释放而非看native=0。ActiveWork计入当前实际acquire/拷贝/execute阶段，工作结束后先减，再进入已登记callback/release；不把等待自身finally的adapter包装Task计作永不退出的计算阶段，原包装Task仍单独在root登记/观察，Released不替代Host对它已退出的断言。成功adapter回执前完成该方向CallbackExit及所有release，返回managed候选；异常/取消也走同一个清理pipeline，外部finite观察到期时adapter原Task仍在根Owner登记，Core按已接收机制产生DrainUnknown，不能用catch提前报Drained。将release gate关住可使native=0而资源未知，正是S03必验反例。

每adapter.QueryDrain对绑定OperationId返回root该operation合并状态（单方向/transform串行，不重复求和）；未知ID=NotStarted/R3D-016。StopAndDrainAsync与root同名方法幂等发内部停止，waitBudget100ms..60s，截止用注入单调clock，外层Host观察用真实WaitAsync保护。wait令牌只取消等待，不撤销stop，抛OCE且root仍可Query；预算到时work/callback/lease/release任一未退出返回Unknown，Query记录StopRequested/Draining→DrainBudgetExpired/Unknown，无Released事件。真实工作/callback退出后Query从Unknown转Drained，再在所有lease/release完成时Released；迟到完成允许继续该恢复链而不产生新operation/结果。无stop正常路径NotStarted→Pending→Drained→Released，各合法下一方向开始可Released→Pending（模拟端口工作快照，不是Core终态回退）；stop已发则禁止任何新调用，Released保持。Query字段全部来自账本、从不自动“修正”计数。

root.DisposeAsync单飞先stop，采用Request.DrainTimeout虚拟预算；未知抛InvalidOperationException/Message=R3D-014，保持Ports/Request/Query/Stop入口可用、root不释放payload。共享的是底层唯一释放pipeline，不把已抛出的某次观察Task当永远无法完成的释放pipeline；迟到lease/callback退出会自然推动原pipeline至Released/Disposed，StopReply.IsDisposed可确认。再次Dispose只有限观察同pipeline，不二次副作用；每次观察Task退出后才可启动下一次，根Owner只保留一个当次观察Task，不累积历史Task或副作用。根Dispose必须在Core engine已Released/原run/stop/dispose全部退出后才由Host关闭，不能在Core使用端口时先Dispose。无任何adapter启动且没有lease时Dispose立即Released；关闭后新adapter/source调用R3D-013/SIM-Disposed。所有物理/现场Gate均不适用于这个纯BCL包，但是否符合上述协议要由真实软件测试证明。

Query()无IO、不抛输入异常、不可变快照最多256事件；Sequence实例内自增（checked long，越界停止/失败而非回绕），同operation点严格有序。Kind使用§13.4明确赋值0..13的SimulationEventKind，不接受任意string或undefined enum，脚本没有自定义event入口；将来新增种类须ScriptVersion变更，不重排/复用既有数值，回放不识别时明确不兼容而非默默跳过。新事件逐出最早条、DroppedEvents递增，不驱逐未决Task/lease；旧Query.Events/字段保持不变。source/adapter诊断用SimulationEvent供宿主Query，不伪造Core的ReconstructionEvent终态；注入Diagnostics由Ports供Core按§5.2真实发事件，接收器异常按已接收规则只造成warning。正常/错误键固定R3D.Sim.Rejected/Failed/BindingMismatch/SourceContextMissing/DuplicateCall/ModeMismatch/TransformUnsupported/Disposed（对应AdapterCode），没有自由自然语言/PASS/发布事实。SIM线程/进度不改变生产/UI权限。

### 13.6 两个无 UI 消费者直接引用发布包

Simulator.Tests的A消费光学实验流程，B消费两方向表面Replay；各自新factory/session/clock/gates/diagnostics/root槽，没有Core.Tests引用或私有stub。各Host在factory前按§11预留容量2之一，强持root槽扩展保留simulation/clock/gates与engine/原run/stop/dispose，root移交/拒绝/迟到规则同§11；隔离中仍占容量，不await using未知对象、不创建替代实例。

唯一装配顺序（以下为构造形状，变量payload来自§13.2的明示值；不是当前编译代码）：

```csharp
using System.Collections.Immutable;
using Asun.Modules.Reconstruction3D;
using Asun.Modules.Reconstruction3D.Simulation;

var simFactory = new ReconstructionSimulationFactory();
var clockA = new SimulationClock(new DateTimeOffset(2026, 10, 10, 0, 0, 0, TimeSpan.Zero));
var gatesA = new SimulationGates(ImmutableArray<string>.Empty);
var scriptA = new ReconstructionSimulationScript(
    ReconstructionSimulationFactory.ScriptVersion, "host-A", 7UL, requestA,
    framesA, calibrationA, observationsA, ImmutableArray<SimulationStep>.Empty, new ByteCount(1_048_576));
IReconstructionSimulation simA = simFactory.Create(scriptA, clockA, gatesA, diagnosticsA);
// 预留的A根槽立即持有simA/clockA/gatesA；其后Core factory也使用同槽。
IReconstruction3D engineA = new ReconstructionFactory().Create(simA.Ports);

var clockB = new SimulationClock(new DateTimeOffset(2026, 10, 10, 0, 0, 0, TimeSpan.Zero));
var gatesB = new SimulationGates(ImmutableArray<string>.Empty);
var scriptB = new ReconstructionSimulationScript(
    ReconstructionSimulationFactory.ScriptVersion, "host-B", 7UL, requestB,
    ImmutableArray<SimulationFrame>.Empty, ImmutableArray<SimulationCalibration>.Empty, observationsB,
    ImmutableArray<SimulationStep>.Empty, new ByteCount(1_048_576));
IReconstructionSimulation simB = simFactory.Create(scriptB, clockB, gatesB, diagnosticsB);
// B独立根槽，不把simB放进A的finally。
IReconstruction3D engineB = new ReconstructionFactory().Create(simB.Ports);
Task<ReconstructionReply> runA = engineA.ReconstructAsync(simA.Request).AsTask();
Task<ReconstructionReply> runB = engineB.ReconstructAsync(simB.Request).AsTask();
// 各原Task立即登记各自槽；await run.WaitAsync(...)、业务/清理错误和最终exit按§11。
```

requestA为F0，其所有嵌套Core列表用ImmutableArray.Create/私有builder.ToImmutable、ResourcePeaks用ImmutableDictionary<string,long>.Empty.WithComparers(StringComparer.Ordinal)构造（空字典也非null）；逐字段值仍按原fixture，不改Core签名。framesA是ImmutableArray<SimulationFrame>，按A0..A5用 `new SimulationFrame("A", frameRef, 2, ImmutableArray.Create<byte>(10,20))` 构造；calibrationA是 `ImmutableArray.Create(new SimulationCalibration("A", asset, ImmutableArray.CreateRange(System.Text.Encoding.UTF8.GetBytes("synthetic-cal-A"))))`，requestA的Calibration.Asset、DirectionCalibration与scope.Asset.Sha256全部改为该字节hash，ID仍cal-A。observationsA为 `ImmutableArray.Create(new SimulationDirection("A", F0明确的AdapterDirectionResult))`，每个嵌套数组/字典按§13.4不可变规则构造，保留所有6帧来源。SourceCalibration资产不是HALCON文件，A正常源lease计数=6帧+1标定=7，归还也7。

requestB与observationsB分别为F0-S Request和ImmutableArray.Create的B0/B1 SimulationDirection，其全部嵌套Core集合仍按§13.4用ImmutableArray/ImmutableDictionary值，Matrix3x4RowMajor也是ImmutableArray<double>而非double[]。每条DirectionId匹配，除ResultId/CalculationId由本Host固定绑定外不另生成任意数值；surface source正常各一个lease，总Acquired/Released=2；Transform端口仅恒等快照且每方向调用一次，Fused=[0,0.25]、Uncertainty=null、含synthetic来源、不Qualified。ST0及S01～S03同样遵循这一构造规则；Steps=[]/gates=[]代表各自ImmutableArray.Empty，有gate时用ImmutableArray.Create("work")/Create("late")/Create("release")，有step时ImmutableArray.Create(step)；不把List直接传给公开构造器。

**Stereo专用fixture ST0**：沿F0时钟/方向A/标定资产/预算/SourceFrame=world/AlreadyInOutput，ScriptId=host-ST、OperationId=ST0、CalculationId=ST0-calc。请求Mode=Stereo、帧仅A0/A1，两帧Kind=StereoPair/PatternId=null/ExposureProfileId=exp-A，ordinal0/1，3×3/stride3/Mono8/Bytes九个10，revision用实际九字节SHA256重算；camera scope CameraIndex=0、CameraWidth/Height=3、ProjectorIndex=-1/Width=Height=0。Pattern=null/minFrames=0/MaxPixels=9，FrameTiming各ExpectedPatternId/两个稳定窗=null、ExpectedOrdinal=0/1，曝光沿F0同设备/时钟的两窗，MaxStereoSkew=1ms以容纳中点差0.01ms。Stereo.CameraFrames=[(A,0,A0),(A,1,A1)]/Pairs=[(0,1,0,1)]；StereoSpec.Profile=rev(stereo-ST)、BBox=[−1,−1,−1,2,2,2]mm、NumLevels=1、MaskWidth/Height=3、TextureThreshold=0、ScoreThreshold=0.5、Resolution/SurfaceTolerance/MinThickness=1mm/Smoothing=0。Frames两条/Calibrations一条，均用§13.6明示synthetic资产，source candidate为PointCloud/Width2/Height1/X=[0,1]/Y=[0,0]/Z=[−0.25,0]/mask全true/contribution全1/conflict全0/Uncertainty=null/Quality=Unverified。每点两条Source A0/A1，ImageRow/Column=null，SampleIndex=i（0或1）；StereoSampleSource=(PairOrdinal0,CameraIndex0或1,RectifiedRow0,RectifiedColumn=i,OriginalRow0,OriginalColumn=i)，CSR=[0,2,4]、Grid=null，摘要FrameIds=[A0,A1]/DirectionIds=[A]，所有ID/revision/provenance照F0规则明确绑定。这里的射线字段是标签synthetic的契约坐标，不能当真实标定/disparity来源；计数为2帧+1资产=3。这些值只验证模拟契约，不验证NCC/三角测量精度。

Host成功0还须sim.StopAndDrain/Dispose原Task真实结束、SimulationSnapshot所有active/pending计数0且AcquiredLeases=ReleasedLeases/Drain=Released；sim收尾未知/异常时业务0改5，原业务错误仍保留。sim根Stop/Dispose任务作为两个附加位置登记于Simulator Host槽（原Core三Task位置不变），总≤5个原Task，原slot容量预先冻结，不发无限查询/重试队列。Query未知/rootDispose失败不能清root槽；Retain需要一起确认接收sim/clock/gates/五原Task，接收前仍原Owner。engine和sim按序关闭，不因engine已归还就漏sim Task；槽中的错误记录和完成条件需覆盖两个对象，不靠GC声称已释放。

Simulator.Tests宿主将§11的slot作局部扩展：`void AttachSimulation(IReconstructionSimulation simulation, IReconstructionClock clock, ISimulationGates gates)`，同一槽至多一次，factory返回后立即Attach；Track容量预留为5，保留其他语义。这是宿主内部接口，不是生产Core API。局部隔离Owner明确增加 `void RetainSimulation(IReconstructionSimulation simulation, IReconstruction3D? engine, ReconstructionRequest identity, IReconstructionClock clock, ISimulationGates gates, IReadOnlyList<Task> originalWork)`；正常返回前独立强持所有对象/最多五Task，违约throw原槽不释放，幂等/容量规则同§11。engine factory失败时仍有simulation，不能用engine=null而跳过sim收尾：先记录首业务错误4，再sim.StopAndDrain/Dispose，各原Task登记槽，有限完成后才清槽，否则RetainSimulation(engine:null)，不得丢sim根Owner。无engine实例时simulation无工作、两个关闭Task通常立即完成，仍须观察。

扩展Host流程精确为：预留槽→Create sim/AttachSimulation→Create engine/Attach→业务run→§11 core stop/原run观察/core dispose→若core cleanClose则sim.StopAndDrain(waitBudget=100ms)→await原Task真实WaitAsync(1s)且Drain=Released→sim.DisposeAsync→await原Task真实WaitAsync(1s)→核对五Task已退出/两个根资源计数全0→RecordOutcome→清槽；任何一处未知/异常按首业务错误与cleanup5规则保存后RetainSimulation，不能先清Core槽再构造第二个无容量sim槽。真实断言finally将本fixture gate和clock放行后重用原Task观察，再验证资源回基线；后台恢复不改原失败回执。该附加100ms虚拟wait由harness推进，不将100ms解释成真实现场停止目标。

### 13.6.1 D01/D02：两个原 Host 的完整角色/诊断夹具

本增量直接消费§13.6的两个发布包Host和同一根槽/五原Task/finally流程，不创建测试工程/第三种根Owner。D01为光学诊断工程师无UI Host，D02为离线表面实验无UI Host；分别独立factory/clock/gates/diagnostics。全部值明示synthetic，继承F0的未改字段（ApiVersion0.2、日期2026-10-10、A/world/mm、device-A/clock-A/exp-A、timing-A/q-A、SourceFrame=OutputFrame、AlreadyInOutput/count0、MaxDirections16、Timeout/Drain1s、无资格/Fusion/Stereo/Grid/方向变换、预算各64MiB/MaxPoints16/MaxVoxelCells16），绝不交给真实AsunImage。`rev(id)`仍SHA256严格UTF8(id)，所有新集合用ImmutableArray/Create/ToImmutable、字典用Ordinal ImmutableDictionary；下表省略的nullable均null。

| 全字段差异 | D01（Host A） | D02（Host B） |
|---|---|---|
| 运行/输入身份 | ScriptId=host-D01/seed7，OperationId=D01/CalculationId=D01-calc，InputSetId=fixture-D01/InputRevision=rev(fixture-D01)，epoch-D01/attempt-D01 | host-D02/seed7，D02/D02-calc，fixture-D02/rev(fixture-D02)，epoch-D02/attempt-D02 |
| source/calibration | FrameId D0..D7，camera2×1/stride2/Mono8；Calibration.Asset=RevisionRef(cal-D01,SHA256(UTF8(synthetic-cal-D01)))，DirectionCalibration/Scope.Asset同值，Serialized字节即该UTF8 | E0..E3，相机/stride/格式同A；cal-D02/SHA256(UTF8(synthetic-cal-D02))，全部asset引用同值 |
| 帧/timing全部字段 | ordinal i=0..7，PatternId按下表；Kind按role，DirectionId=A，ExposureProfileId=exp-A，Revision=RevisionRef(FrameId,实际两byte的SHA256)，AcquiredAt=F0 UTC起点+曝光末端；FrameTiming同FrameId/epoch-D01/attempt-D01/device-A/clock-A，曝光[i*10000+1000,i*10000+2000]ns、稳定[i*10000,i*10000+3000]ns，ExposureRevision=rev(exp-A)，ExpectedOrdinal=i/ExpectedPatternId同PatternId | i=0..3，相同公式；epoch/attempt改D02，FrameId E0..E3 |
| Pattern全部字段 | Profile=rev(pattern-D01)，HybridVertical、8×8/minStripe4/SingleStripeWidth=null/global/minGrayDifference10/CapturePhaseDiagnostics=true，OrderedPatternIds=[black,white,g0,g1,p0,p1,p2,p3]；Sequence Version=r3d-sl-sequence-v1/ManifestRevision=rev(manifest-D01)/下表8项 | rev(pattern-D02)，GrayVertical、其余尺寸/normalization/stripe/灰度差同A，Capture=false，OrderedPatternIds=[black,white,g0,g1]；Sequence同version/rev(manifest-D02)/前四项 |
| Diagnostics全部字段 | Version=r3d-sl-diagnostics-v1，Layers=[Correspondence,PatternRegion,Phase,GrayBinary,GrayCorrespondence]，MaxOutputBytes=65536/MaxLayers=6/RuntimeRevision=下文synthetic:host-D01 | 同version，Layers=[Correspondence,PatternRegion]，MaxOutputBytes=65536/MaxLayers=2/RuntimeRevision=下文synthetic:host-D02 |
| 原ROI/minFrames | Roi=null/MinStructuredLightFrames=8，MaxPixels=2 | Roi=(Row0,Column1,Width1,Height1)/MinFrames=4/MaxPixels=2 |
| Surface/Geometry | F0的2×1 CameraSamples数值不变；ResultId=result-D01/CalculationId=D01-calc/SourceFrameIds D0..D7/SourceDirectionIds=[A]。每像素Sources含8帧同row0/column i/SampleIndex i/Stereo=null，CSR=[0,8,16] | ResultId=result-D02/CalculationId=D02-calc、X=[null,1]/Y=[null,0]/Z=[null,0]mm/mask=[false,true]/reason=[1,0]/contribution=[0,1]/conflict=[0,0]/ValidFraction=1（分母为ROI的1个请求像素）/ConflictFraction=0/Quality=Unverified/Uncertainty=null；CSR=[0,0,4]、Sources只原column1/SampleIndex1的E0..E3，摘要四帧/A |
| 其它原回执字段 | AlgorithmRevision=rev(algo-A)，Geometry.ResultId对应、Layout=CameraSamples/Grid=null、TransformProvenance=(A,AlreadyInOutput,null,0,1)。Provenance依次InputRevision/Pattern.Profile/Sequence.ManifestRevision/AlgorithmRevision/Calibration.Asset/rev(timing-A)/rev(q-A)；warnings/resource字典Empty，Core后加synthetic来源 | 同规则，用D02对应revision/ResultId；无变换/融合 |
| 脚本剩余字段 | Version=ReconstructionSimulationFactory.ScriptVersion，Frames为上表8个SimulationFrame(A,完整FrameRef,2,ImmutableArray两byte)，Calibrations恰一个SimulationCalibration(A,上述asset,UTF8字节不可变值)，Directions恰SimulationDirection(A,上述AdapterDirectionResult含下列6层)，Steps.Empty/MaxSnapshotBytes=1048576 | 同字段构造，4帧/1标定/2层，Steps.Empty/MaxSnapshotBytes=1048576 |

Sequence.Patterns每项全部字段按下表：PatternId/SequenceOrdinal=行序；Kind如下；RoleOrdinal和PhaseStepIndex如下；GeneratedPatternSha256由最后列的**synthetic投影器8×8逐行byte**计算。phase列常数图仅验证冻结hash字段和模拟绑定，Gray条宽也不证明真实HALCON minStripe布局；Adapter不得接受该夹具作为真实生成组。

| PatternId / ordinal | Kind / Axis / RoleOrdinal / PhaseStepIndex | 相机Bytes | synthetic生成图8×8逐像素byte |
|---|---|---|---|
| black / 0 | NormalizationBlack / None / 0 / null | [0,0] | 全0 |
| white / 1 | NormalizationWhite / None / 0 / null | [255,255] | 全255 |
| g0 / 2 | GrayCode / Vertical / 0 / null | [10,20] | column<4为0，否则255 |
| g1 / 3 | GrayCode / Vertical / 1 / null | [20,10] | floor(column/2)为偶数0、奇数255 |
| p0 / 4 | PhaseShift / Vertical / 0 / 0 | [10,20] | 全64 |
| p1 / 5 | PhaseShift / Vertical / 1 / 1 | [10,20] | 全128 |
| p2 / 6 | PhaseShift / Vertical / 2 / 2 | [10,20] | 全192 |
| p3 / 7 | PhaseShift / Vertical / 3 / 3 | [10,20] | 全128 |

每层Version=r3d-sl-diagnostics-v1、DirectionId=A、Width2/Height1、Origin=Simulator、Observation=Observed，Input/Manifest/Pattern/Algorithm逐项为所在Host原请求revision。RuntimeRevision=RevisionRef(`synthetic:host-D01`或`synthetic:host-D02`,SHA256(UTF8(`reconstruction-simulator-v1\nhost-D01\n7`或D02字符串)))；SourceFrames完整D0..D7或E0..E3，每项实际FrameRevision和ordinal；LayerId/ContentSha256依§4.4.1规范字段构造，不能以rev(LayerId)替代内容hash。以下是Domain/Values/axis/unit/object/GrayRole全部oracle：

| Host / Kind / ObjectOrdinal / GrayRoleOrdinal | Axis / Unit | Domain / Values |
|---|---|---|
| D01 / Correspondence / 1 / null | Vertical / ProjectorPixel | [true,true] / [0,4.25] |
| D01 / PatternRegion / 1 / null | None / Membership | [true,true] / [1,1] |
| D01 / Phase / 1 / null | Vertical / HalconPhaseValue | [true,true] / [0,1.25] |
| D01 / GrayBinary / 1 / 0 | Vertical / BinaryClass | [true,true] / [0,1] |
| D01 / GrayBinary / 2 / 1 | Vertical / BinaryClass | [true,false] / [1,null] |
| D01 / GrayCorrespondence / 1 / null | Vertical / HalconGrayCorrespondenceValue | [true,true] / [0,4] |
| D02 / Correspondence / 1 / null | Vertical / ProjectorPixel | [false,true] / [null,4.25] |
| D02 / PatternRegion / 1 / null | None / Membership | [false,true] / [null,1] |

规范编码oracle由上述完整字段独立构造，长度不含ContentSha256自身；不是产品/Simulator执行结果。D01每层费用7914 bytes、六层合计47484，D02每层4938、两层9876，均≤65536；脚本包括原surface/输入/序列费用，按原四倍整体计入后仍须≤1MiB，新增方向不重置此operation总限。

| Host / Kind / ObjectOrdinal | 规范字节数 / ContentSha256 |
|---|---|
| D01 / Correspondence / 1 | 1185 / `e182e946b178184bed667374418a32a54ea61366ff461d78dba6b579ee378029` |
| D01 / PatternRegion / 1 | 1185 / `b1c086000b27ca5ef5fe4168ea42d2d9df103b48f1f1281c89fa60e857a0e14b` |
| D01 / Phase / 1 | 1185 / `3794bf2958a1cf19d29893cd2d446f7d1592090761e3cb693816402b5adaad87` |
| D01 / GrayBinary / 1 | 1189 / `9ebcdde597d1af429b1bc00e163f975f08fda090257eab0d11b049fccfc2abe4` |
| D01 / GrayBinary / 2 | 1181 / `950e263acc0afd249d2afac0b97c40124ccabb2ccb563523d102edc7b80c5fcc` |
| D01 / GrayCorrespondence / 1 | 1185 / `29bdcac9a18500dd6fa28d4114a162c665667b78f39e17b79fda0b654ad364f4` |
| D02 / Correspondence / 1 | 841 / `7fe186803f1d05ffe9343d606f4f434eb971c4c01f3e9c154e57b724a67b072e` |
| D02 / PatternRegion / 1 | 841 / `09627b7dcabf02ef7c22f2a1b909852704052155c6ce1964f9ab18b65b41832e` |

在§13.6装配代码分别以requestD01/framesD01/calibrationD01/observationsD01替换A的四个payload，以D02四payload替换B（B的Frames/Calibrations现在非空）；ScriptId分别host-D01/host-D02，两个SimulationClock仍该UTC，gates各`new SimulationGates(ImmutableArray<string>.Empty)`，`new ReconstructionSimulationFactory().Create(script,clock,gates,diagnostics)`后立即AttachSimulation到预留槽，再`new ReconstructionFactory().Create(sim.Ports)`/Attach、Validate、`engine.ReconstructAsync(sim.Request).AsTask()`/Track。这是两个**完整已列payload的现Host实例**，不依赖额外BuildFixture/DI/stub或不存在的便捷decoder。两个run可同时启动，但两槽分别持有原对象和五Task，不在A取消时关闭B。消费回执处必须逐项核对上表8个层内容/来源/hash/顺序/单位、Surface数值及D01 lease9、D02 lease5取得/归还各一次；0值/域外null不同，B的ROI外像素不能压缩掉。只有原run/core-stop/core-dispose/sim-stop/sim-dispose均已观察真实退出且两个根Released/全部计数0，Host才最终0；业务异常/lease未知依§13.6有限finally保首错与cleanup5，factory失败仍收尾已创建sim。

### 13.7 Simulator S01～S03 fixture、反例和有限验收

唯一 `tests/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.Simulator.Tests/Asun.Modules.Reconstruction3D.Simulator.Tests.csproj`：Microsoft.NET.Sdk/net10.0/OutputType=Exe，仅引用发布Simulator/Core与BCL。S01/S02/S03各主case及下列每个子例真实观察期限**10s**，suite从fixture构造至最后finally总**120s**，外层本次独占进程**180s**。虚拟clock预算（Request1s、DrainTimeout1s/step0..60s）与上述真实截止点严格分开；Advance驱动算法时间/排空观察，不能当性能计时或让测试未完成返回成功。每子例fresh脚本/根槽、seed7/日期固定，既有F0/F0-S只改明确列出的字段，计数由公开Query与返回lease断言，不反射私有stub/native状态。

| case / 子例 | 明示脚本与控制动作 | 精确验收 |
|---|---|---|
| S01-A/B/Stereo | §13.6两Host及ST0；Steps=[]，clock不推进、gates=[] | A/立体候选XYZ及CSR等于明示值，A lease7、立体lease3、B lease2，全部归还一次；B Fusion=[0,0.25]/count2/transform1，三种模式端口均可直接构造；无native/WPF。每个engine和sim所有原Task退出、Released才Host0 |
| S01-Replay/Invalid | 同seed/脚本/版本两fresh实例按同控制顺序运行；改seed=8子例；改Version/重复step/QualifiedCandidate/bytes-hash不一致/超snapshot/gate缺登记子例 | Replay值/错误/事件序列一致（剔除Host真实耗时）；seed8只改SyntheticRevision，不改XYZ。Version/重复step/QualifiedCandidate为SIM-001，hash不一致SIM-002，MaxSnapshotBytes改1且保留原数据为SIM-003；Create在无原任务/lease前抛script参数异常，缺gate抛gates参数异常 |
| S01-ImmutableBoundary | Frames/Calibrations/Directions/Steps逐一用default而非Empty；nested Request.Directions/RawObservation.CSR分别换成可变List与自定义IReadOnlyList（Count/index/enumerator一访问就抛）；另外从独占原byte[]/List/builders构造ImmutableArray快照，再修改原容器并分开Validate/Create | default返回SIM-001/精确Path，gateIds default构造ArgumentException；nested可变/自定义集合在读取前SIM-001，getter触达次数0，不把它异常当绑定结果。改原容器不能改Validate/Create所见不可变脚本/hash/候选/事件；同一规范快照完成绑定校验后被Create保留。另取Errors，后续Validate不改变旧Errors；验证器返回的Errors非default且无builder别名。所有新增子例沿10/120/180s、无新测试工程 |
| S02-Reject/Partial/Fail | F0-S B1 DirectionExecute步骤用ImmutableArray.Create：`StepId=b1-exec,Direction=B1,Resource=B1,NotBefore=0,Gate=null,Cancellation=Observe`；Reject/R3D-008；另子例用with创建新脚本Fail/R3D-013；再改PartialPolicy=RejectOperation；最后两方向均Reject | Keep策略B0保留、B1 Issue代码精确/Fused=null/操作Partial；Reject策略Rejected、不继续方向/融合；两方向零成功Rejected、非Partial；源lease已取得仍各归还一次，错误ReasonKey/AdapterCode/两个ID完整。所有事件Kind均Enum.IsDefined且值固定0..13、回放比较enum而非自由文本；Simulator不自己发布Core终态 |
| S02-Cancel/Timeout/Busy | F0 DirectionExecute A设Gate=work/Cancellation=Observe，等公开StepEntered后取消Core或Advance(1s)到Timeout；busy/重复子例在同gate前提交新请求/原ID；FrameAcquire/CalibrationAcquire/SurfaceAcquire分别Reject允许的003/005/024三个子例 | 开始取消后不再起融合；Observe wait退出并归还7lease，CoreCancelled/TimedOut唯一；RootStop/query一致。Busy R3D-022、Duplicate R3D-023无第二模拟work，gate.Release重复不二次完成；A停止不影响B。拒绝第一个frame时0lease，拒绝标定时已取得6帧均归还，拒绝surface时该方向0lease；主Issue错误和source来源完整 |
| S03-LateSource/Callback | FrameAcquire A0设Gate=late/Cancellation=CompleteLate；子例CallbackExit ResourceId=A/reconstruct设同gate且CompleteLate；注册Core stop并观察root Draining后按100ms分段Advance、最多20次直到Core/Query Unknown，随后Release(late) | late-source停止前0lease、Release后取得1立即归还，不取得其余5帧/标定；late-callback已有7lease但回调未出不得释放，Release后退出/逆序归还；无新结果/无替代实例，Root仍持有原Task，Core恢复原取消终态一次 |
| S03-Lease/Close/Wait | FrameRelease A0设Gate=release/Cancellation=CompleteLate；正常计算已复制候选但release卡住。Core到期Stop后分段Advance至DrainUnknown；再Release(release)。另子例Stop等待令牌取消、重复Stop、engine factory异常（合法sim但null Core ports参数）/Retain违约；source/adapter非法外部直接Acquire/重入子例 | native=0不等Drained/Released；PendingLeaseReleases=1、7取得且6已释放、无最终成功回执；收到DrainUnknown的Host保留业务3（不是业务0），根槽占用。Release后同底层release pipeline完成、最后lease只归还1次、原run/stop/dispose加sim停止/关闭全部退出才清槽；取消Stop观察不撤销stop，Retain抛错原Owner/Task不丢；factory失败仍关闭sim或保留根。无context直接Acquire为SIM-SourceContextMissing/0lease、重入SIM-DuplicateCall不影响原任务 |

S03每个Unknown快照保存oldSnapshot/oldSnapshot.Events及计数值，然后gate放行/Advance/新Query；断言旧Events非default、序列/Kind/元素/计数与保存时完全相同，新Snapshot递增事件也不能修改旧值（包括ring-buffer逐出后的事件）。在fresh实例重放同脚本/control序列比较同enum事件顺序。改调用方bytes源、原List/builders及with后的新脚本都不能改变原root的late回执/lease数据/旧快照，验证输入和输出两侧都没有可变别名；不使用unsafe篡改作为普通不可变契约测试。

所有步骤Gate在fixture构造前显式注册，StepEntered同步通过Query的有限观察等待，harness每次观察最多真实1s且总计纳入子例10s，不无限sleep等待虚拟clock。为防止Advance先于异步deadline wait登记，S03停止后按100ms最多20次Advance，每步让出异步continuation并核对Query；超过20步/真实截止仍未观察到Unknown即失败，不能无界推进。超时控制命令也记录为本case的固定序列，Replay采用同序列。测试finally先记录首断言/业务错误，然后仅对本子例所有已登记gate调用Release，并推进虚拟clock至该脚本最大NotBefore及等待截止点（分次≤60s、最多32次），有限等待engine原Task退出/已归还，再stop/dispose sim；advance不能超越测试真实10s保护。成功异常Task也要观察异常、不是只看IsCompleted；资源/原Task未完成保留容量根槽并输出非零。外层180s只终止本次测试进程、不杀其它应用或清目录，也不声称排空通过。退出：断言失败1、fixture/期限/未完成/必需子例跳过2，全部完成通过0；S03暂时Unknown是预期反例，但case最终必须放行并证明全部原Task/资源退出，不能让未收尾Unknown以“预期”为由返回0。

发布Simulator保证无残留资源的成功adapter回执，不提供“先Completed再伪造Dispose未知”的隐藏控制；该Host违约反例仍由已接收Core R18的专用故障stub验证，不算Simulator能力。这里测试真实可达的release阻塞→Core DrainUnknown→非零Host/根槽保留，再放行恢复；不为凑反例添加无消费者的后台任务。

Simulator Benchmark沿§14口径以脚本版本/seed/明示payload/控制序列为输入、记录合成端口全链与lease计数、独立root并发1；测试虚拟time不冒充实测P50/P95/P99。真实测量改用宿主BCL Stopwatch clock注入（无advance），steps=[]或已释放gate，样本计划/截止/预算沿diagnostic-F0，不含native/计量精度目标、结果NotEvaluated；这是模拟软件负载测量，不提升真实Adapter/Golden/计量/性能/HIL门。

### 13.7.1 D01～D05 增量验收（沿原工程/真实10/120/180s）

| case / 子例 | 冻结输入/动作 | 可判定断言 |
|---|---|---|
| D01-DualHost/Replay | §13.6.1两个完整Host；各fresh实例重放一次，原F0/F0-S/ST0也仍执行 | 8层逐值/域/来源/长度/hash与oracle一致，A9/B5 lease各归还一次，两根互不影响；旧脚本DiagnosticLayers.Empty、0..6enum/原结果不变，所有原Task/两个根Released才0 |
| D02-Roles/Unsupported | 缺Black/White各一、Black冒Gray、重复ordinal、inverted缺配对、phase少一、axis错、GeneratedPatternSha256非64hex；Diagnostics未知enum/default/empty/重复/未知version、Capture=false+Phase；Defect、GrayVertical+Phase、HybridVertical+SingleStripe、HybridBoth+Diagnostics | Core在源前依§4分别拒绝003/002/004/001/015或007；Simulator非法形状/version为SIM-001，绑定缺项SIM-002，不支持组合SIM-004；无native/source工作，不删帧修复。生成hash合法但与真实gen不符另属Adapter的R3D-002，不由Simulator证明 |
| D03-Inverted/SingleStripe | fresh D01-I：Script/Operation/Calculation及fixture/epoch/attempt/manifest/pattern各加-I，normalization=inverted_pattern，8项顺序g0,g0i,g1,g1i,p0..p3；Kinds前四0/9/0/9，RoleOrdinal0/0/1/1，原Gray及反图相机bytes=[10,20]/[245,235]/[20,10]/[235,245]，生成图为表中g0/逐像素255-g0/g1/255-g1，phase仍表中值，全部frame/timing/hash/revision按同公式重绑，6层数值同D01但来源/hash重算。fresh D01-S各身份加-S，route SingleStripeVertical/SingleStripeWidth8，在D01末加D8/s0/KindSingleStripe/AxisVertical/RoleOrdinal0/phaseIndex null/Bytes[10,20]/生成8×8全255，MinFrames9/manifest9项/CSR[0,9,18]及所有来源重绑；Layers再加SingleStripe，MaxLayers7/MaxOutputBytes131072 | I不含Black/White，全部8原帧来源保留，二值只对应g0/g1且层数仍6、lease9；S的追加SingleStripe层Object1/GrayRole=null/Unit HalconSingleStripeValue/Domain[true,false]/Values[0,null]，其余6层值同D01、全部9帧来源/hash重算、lease10。runtime为各ScriptId的SyntheticRevision，Quality全Unverified；不宣称真实布局/算法 |
| D04-Shape/Hash/Budget/Immutable | D01 script分别删一个层、重复层、来源漏Black、RuntimeRevision错、Origin伪Decoder、改值不改hash、array长度错、域外填0、Phase单位改ProjectorPixel、任一新ImmutableArray为default；另MaxOutputBytes=47483/MaxLayers5/MaxSnapshotBytes1；从原builder生成Immutable后修改builder | 前项SIM-002（字段/enum非法为001），default为SIM-001；预算三个子例SIM-003，分配/工作前拒绝。改builder不改规范快照/旧Query/返回层；内容0与null不可互換。Core.Tests沿内部stub另交这组坏AdapterDirectionResult验证R3D-024/不附有效方向；不借Simulator提前拒绝证明Core出参检查。domain全false/Values全null/Observation NotObservable的Phase合法，region全0仍Observed；内容hash须重算 |
| D05-Cancel/Late/Isolation | D01 DirectionExecute(A) gate=work/Observe；另CallbackExit(A/reconstruct) gate=late/CompleteLate；另FrameRelease(D0) gate=release/CompleteLate，各fresh；D02正常同时运行。沿S03有限观察/clock推进/根恢复，最后放本case所有gate | 取消不开始新诊断/融合；迟到/未释放的原Task强持、Result含层一律不提前交，DrainUnknown.Result=null、A根槽不清。B两层/hash/lease5不受影响。放gate后沿原pipeline归还A9lease、五原Task真实退出，原业务错误保留；未收尾非零，不以phase已复制或Native=0宣布Released |

D04的Core出参stub反例增入既有Core.Tests（不发布stub、不引用Simulator）；支持请求和全字段oracle直接按§13.6.1构造，原R01～R25限时及套件总限保持。其余D01～D05在既有Simulator.Tests，case/子例10s、整个S/D套件120s、外层180s，必需子例不得跳过。D01-I/S是两个原Host的fresh后续case，不创建第三Host/工程。此处只定义后续验收规格，本轮未执行任何C#测试。新增copy/hash阶段Benchmark与Persistence false/true分别记录，沿§14目标缺失NotEvaluated；原Core/Simulator已接收范围不因这些新增case重新审核。

### 13.8 全范围收口新增验收（沿既有工程）

下列是后续实现的必需反例/断言，本轮只做规格走查，不编写或运行测试。普通Adapter/Joint/SD桥在A.1既有AsunImage.Tests，UI在既有Wpf.Tests；原Core/Simulator/Decode suites和向量保持，不重测其无影响范围。非native软件spy仅验证装配/复制/预算/失败资源，真实算子另以同ID标native门，不混淆二者。

| case | 正向与反向输入 | 必须断言 |
|---|---|---|
| NA01 工厂/部署 | A/B各自new普通factory、同Profile不同source；缺/错revision、unknown envelope、overflow、预算不足、非法precision、threads与冻结环境不符 | 拒绝前无frame/file/native/线程，成功端口完整；A取消不影响B；真实envelope未取得时运行NotReady，软件spy不授资格 |
| NA02 tuple/mapping | 同模型XYZ原tuple点序反转但row/col正确；float32图舍入与tuple不同；重复/少映射、错误size、非有限/域外；零/负Z | 输出按row-major关联原tuple，零/负保留；real值不覆盖；mapping不可证024，无最近点/序号fallback；tuple路线只保模型数值，不宣称原算法无误差 |
| NA03 Stereo量化 | MaxAbs/quantization边界、binade/subnormal/overflow，AllowStereoRealImages=false；两pair ray/isosurface | 不允许或表示上界超限007，非有限024；不从m3d_pairwise猜像素，不把display surface当贡献；物理误差/算子累计误差独立NotEvaluated |
| NA04 生命周期 | native不返回、source晚到、clear/lease释放throw或卡住、set Dispose超时；重复Stop/Dispose、根满/接管抛错 | 64Task/512对象槽预留、原Task/handle/lease强持；Unknown不clear第二次/不丢tuple，不伪Released，不重建；清理可安全组件继续，首业务错误保持 |
| NA05 Joint实际构造 | 原JRC完整绑定→专用factory；普通factory+Joint kind、只传RevisionRef、文件hash与asset hash混淆、SourceOwner未确认、已Closing/撤回/水位过期、Synthetic文件 | 只有原Owner关联/Applicable/完整实际Request才专用装配；源asset/资格snapshot/file三个域保真；CAL0.3.3局部平面/.dat不冒setup；拒绝时native0，旧JRC不重算 |
| SB01 managed值/SD桥 | 两Host§7.7.2完整Observed4槽；直接value source和SD public StartRead；有效0/负、全Invalid | 同XYZ/CSR/Frame/mm、不确定度null/Unverified；HF XY由SD端口，PointCloud不伪Grid，根Frame已声明；Complete才采用，来源hash不猜 |
| SB02 不可表示输入 | Int64 index=Int32.MaxValue/MaxValue+1及9007199254740993；Unknown/派生/C5多父/Fallback2D/mesh、uint原因未映/超255 | 允许int最大值仅当Root证明范围内；超限024、C5/mesh007，无double化/截断/假flat父；无效原state/reason仍在原metadata |
| SB03 部分/迟到 | 第1块正常后第2块失败；取消/timeout、Generation/Ordinal/Frame错、consumer异常、source释放未退出 | 整批暂存失效、不发布半成功；RequestCancel一次、不Close共享service；原Completion/Acquire/lease任务保根，关后迟到Complete不恢复采用 |
| W01 双STA/三语 | §10.4两真实Host、1920×1080实际client/DPI；最长英文、焦点F5/Esc/CtrlS/方向表，缺资源键/element已有Parent/错Dispatcher | 三语完整/缺键保持旧资源；Bind无全局依赖，不偷默认viewport；原UiGeneration/权限/键盘不改算法或Core target；截图不证明运行 |
| W02 绘图与迟到 | N>K显示、无效/冲突、CSR多源、诊断单位、A→B旧Present迟到，终态后进度；控件只读关闭 | 固定slot算法保N/分母/源；不支持层明确拒/保原事实；旧代只释放不覆盖；≤10Hz无无界队列；B不Stop别人核心，不Dispose借用viewport |
| W03 推荐/保存/恢复 | 来源四revision变化、Abstain/Invalid/Cancelled、权限撤销、保存Unknown；Run/Present/Detach/Dispatcher卡住或throw，接管未确认 | 建议过期/无生产写入；保存只有Owner确认才Saved，不自动重试；关闭有限、原任务/root保留，Detached不等Released，槽未确认不退容量 |

SB01完整software fixture不要求客户样本：用SD §9公开HF-A元数据/原bytes构造独立派生测试输入`r3d-hf/1`，保3×2/Grid/offset/Root[28,29,30,36,37,38]及padding，**显式新producer**将State改全Valid、Reasons全0、Origin Observed/Parent=Root/Exact=true并封存新metadata/hash，不改上游HF-A。其Grid坐标端口固定`X=parentColumn`/`Y=parentRow`mm；预期XYZ=(4,8,0)/(5,8,1)/(6,8,2)/(4,9,3)/(5,9,4)/(6,9,5)，Root是原Producer的40槽PointCloud，RootFrame.Width40/Height1/Kind=PointCloud/PixelFormat=PointCloudMm，ImageRow/Column=null；SourceIndices原值保持，不把Grid parentoffset当Root索引证据。根buffer固定1000bytes：offset0存40项XYZ Float64LE AoS stride24，offset960存40项UInt8 State；初始XYZ全0/State=Invalid(2)，在原ordinal28/29/30/36/37/38分别写上述六XYZ并改State=Valid(1)。RootFrame.Revision核这1000原bytes的SHA256，根Source可按原ordinal读对应值；不能用label hash冒原bytes。metadata用SD §18原codec，buffer按原固定bytes实际hash；Source/坐标端口仍只在本Host实例。

B从这份新HF producer值生成不同Key=`r3d-pc/1`的6×1 PointCloud（XYZ SoA各6个Float64LE、State全Valid、Reason全0、同原Root索引/Observed），Frame/mm及六XYZ原样、Grid=null、Faces0，登记新原bytes/hash/metadata。这不是改原mesh-B单位/index或偷偷降其>2^53根，只是两个合法本地synthetic消费者。旧mesh-B/原HF-A分别作为SB02的大Root/Unknown完整反例，原件保持；Root producer自引用单根、SourceIndex StableOrdinal/Base0、Unit mm、Frame=fixture-mm，三XYZ共享AoS原layout offset0/8/16/stride24，State在offset960/stride1，Reason Uniform0、Origin Observed/Exact单父Root；原metadata也用SD原codec封存。正例预算SD资源=(profile synthetic-r3d,revision1,MaxItems6,MaxReadBytes65536,MaxResidentBytes1MiB,MaxBlockItems2,MaxIssues16,OperationLimit1s)，SurfaceOptions=(0,4,1,16,16,4,1,1MiB,1s)，桥MaxCopiedBytes8MiB/Observe1s，重建请求沿F0-S单方向AlreadyInOutput、Frame=fixture-mm、MaxPixels40、64MiB/MaxPoints16/Drain1s、无Fusion/光学Pattern/Calibration，MetadataRevision来自封存原metadata。Root40槽仅来源证明，当前读取只6槽；Root实际保存/X/Y/Z内容由fixture Source可定位，缺根原件必须024，不通过人工Root尺寸声明凑通过。

case真实观察≤10s、每个新增software/native/UI suite120s、外层独占测试进程180s；native客户Profile可明确更大有限预算并记录来源，不能无限挂起。闩锁finally仅打开本case并有限观察，未决根保留、输出非零，外层终止只停止测试不证明资源排空。入口沿A.1/A.2既有完整工程路径，参数分别`--case adapter-full`/`--case surface-bridge`/Wpf `--case ui-full`；只执行实际获授权/建成的适用工程。Benchmark沿§14，补tuple/domain/量化、SD Plan/复制/释放和UI Presenter可见/Detach测点，目标缺失NotEvaluated。

## 14. BenchmarkProfile 与资源计划

统计口径唯一引用 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)，不复制另一套分位算法。端到端=RequestAccepted 至 ResourcesReleased；取消另计 CancelRequested→Drained 和资源归还。短拒绝、超时、失败、删失与 DrainUnknown 单列，不挑成功样本判性能通过。客户/消费者时延、误接受/拒绝和资源目标未采纳时状态=NotEvaluated，不能写 Unverified 性能“通过”。

执行前由 Host 冻结其私有 BenchmarkProfile（不是未定义的Core公开DTO）：Profile/模块/API/输入/Pattern/标定/配准/策略 hash、硬件与 HALCON线程配置、冷启动/预热次数、测量次数与最小有效样本数、有限 deadline、Managed/Native/Result/point/voxel 预算、时延/误接受/拒绝目标及来源。没有正式目标仍可诊断测量，但 sample plan 不可在看结果后修改。不同消费者不共用臆造节拍。

| 切片/负载 | 冻结维度和测点 | 判定/计数 |
|---|---|---|
| 纯 Core/模拟器 | 1/2/4/16方向，1格/边界格/16,777,216格预算边界；来源长度、冲突比例、缺失比例、输入顺序反转；实例1与双实例 | 深复制、分桶/排序、等权求和、CSR构造、候选建议阶段；managed peak/复制bytes/有效元素数；输入顺序改变数学结果不变 |
| 结构光 | HybridVertical、HybridBoth、资格化 Gray/SingleStripe，manifest帧数/ROI比例/尺寸上下限；黑/饱和/镜面/孔/台阶 | Acquire、模型/图案布局、decode、重建、XYZ/domain复制、单位/变换、清模型/归还；persistence=false/true 单独负载 |
| 立体 | 实际相机对、每对视差跨度、NumLevels、纹理/重复纹理/反光、bounding box/体素数、persistence=true | 整流、NCC、surface_fusion、m3d_pairwise/逐对证据、来源构造、isosurface展示复制与清理；内存包括原云+isosurface+iconic持久中间图 |
| 导入/融合 | 已给高度/多层点云、不同世界坐标、AlreadyInOutput/ApplyPublished、grid collisions/支持域、MinContributingDirections | Import、一次变换、分桶、差异门、结果CSR；每格 contributor/conflict 数能重算；不得只测 HALCON 算子 |
| 生命周期 | 预检/运行前/解码/变换/融合/结果复制时取消；native 不返回；UI关闭；双实例并发；ID重复 | native calls/callbacks/FrameLease/input bytes/result bytes/活跃模型必须回基线；DrainUnknown 不达标，不提前终态 |
| 可选 UI | 固定1920×1080实测client/DPI/三语最长文案；16方向/256帧明细；256 bins图表、快速切视图/语言 | UI投影帧时/内存/迟到计数；原始点只投影有限绘图集，更新≤10Hz，终态不丢；真实 WPF/UIA 实测另门 |

防护值在请求里显式提供：Timeout 100ms..30min，DrainTimeout 1..60s，Native 64MiB..8GiB；宿主可预填30s/5s/2GiB，但不由核心补默认。方向并行=1、实例接纳=1、内部队列=0；未来并行改变须新方法切片。Budget 的保守 native envelope 来源于实际部署测量；缺 envelope 或运算溢出在分配前 R3D-010。

后续实施时按同一代表图/版本比较完整主路线与只读评测候选：逐元素公制误差、误接受/拒绝、弱信号拒识、共同支持覆盖、P50/P95/P99、托管/native峰值、取消到释放与ROI细节丢失。参数建议评估带标签的 holdout，生产 freeze 独立；没有代表样本和真值不宣称最快/高精度。真实标准件、计量不确定度、HIL与现场节拍属于具体 Adapter/消费者门，纯值算法可用明确 synthetic 负载诊断验证。

首个无native诊断Profile固定为TestHost内置 `--profile diagnostic-F0`：使用F0/F0-S明示值与synthetic适配器（不加载WPF/HALCON），Clock改为真实BCL Stopwatch时钟；单实例并发1、两Host独立实例对照，预热3次/测量30次/最低完整样本30，单次Timeout=1s/DrainTimeout=1s、suite deadline=60s、外层独占进程90s，预算沿用64MiB与16points/voxels，正式时延/质量目标全部null、结论NotEvaluated。记录模块/API/fixture/Profile/hash、.NET/OS/CPU/内存、阶段和端到端原始时长、完整/失败/超时/Unknown样本及资源终态，按DEV-GOV-010统计，不把fixed-clock功能测试的0时间当性能数据。fixture/计划无效或任何未完成返回非零；完整诊断返回0仅表示测量完成，输出仍NotEvaluated。真实图像Profile单独冻结样本/数量/目标和finite deadline，禁止看过结果再改变计划。

## 15. 可观测性

每次操作至少记录结构化事件：`OperationId`、`CalculationId`、模块版本、契约版本、输入/参数/标定/策略 hash、方向和帧计数、阶段、开始/结束时间、线程/并发、托管/native/GPU 峰值、队列等待、取消/超时/排空状态、质量摘要、错误码和结果引用。

日志分为 `Trace`（逐方向/阶段）、`Info`（开始/终态）、`Warn`（降级、部分结果、冲突）、`Error`（适配器/资源/排空失败）。原始图像、密钥、客户身份和设备凭据不写日志；高频进度采用采样或合并，但终态和错误不得采样丢失。

## 16. 版本兼容、发布和回退

### 16.1 兼容矩阵

| 变更 | 兼容规则 |
|---|---|
| 新增可选输出字段/原因码 | 读取方必须忽略未知字段；版本 minor 增加 |
| 改变单位、坐标语义、有效性或事件顺序 | major 变更；旧输入拒绝或经显式迁移器转换 |
| HALCON/AsunImage 版本变化 | 重新核对算子签名、线程/内存和 Golden；适配器版本化 |
| 参数默认或融合数学改变 | 新 AlgorithmProfile/策略 hash；不得覆盖旧回放结果 |
| 删除字段、缩小范围或改变错误语义 | major 变更并保留读取旧证据的兼容层 |

序列化结果必须携带模块版本、Contract 版本、算法 Profile、标定/策略 hash 和单位/坐标。禁止依赖文件名或 `latest` 选择版本。

### 16.2 独立发布

发布包包含核心 DLL、随Core发行的公开值契约/适配器接口（不另造空Contract DLL）、版本清单、变更记录、兼容矩阵和 Replay/Golden 指纹。发布前必须通过 Contract、Adapter、Integration、Fault、Performance（目标缺失明确NotEvaluated，不算通过）检查；缺少真实 Profile 时不能标记 Qualified。

### 16.3 回退

回退先停止新操作、等待在途操作排空或按宿主策略隔离，再恢复旧 DLL 和兼容配置。已生成的旧结果保持原版本和来源，不用新算法重写历史；不可解析的结果标为 `Unknown` 并保留原字节。回退不能重发设备命令、修改产品事实或清空调用方配置。

## 17. 第二消费者接入断言

结构光工具和 3D AOI 必须使用同一核心包、同一公开接口和不同宿主配置完成以下验证：

1. 各自创建独立模块实例，不共享句柄、静态状态或缓存。
2. 一个宿主取消操作时，另一宿主的操作不被取消或改写。
3. 两个宿主可使用不同 `AuthorityScope`、语言和宿主证据存储；核心输出语义一致。
4. 一个宿主使用结构光输入，另一个使用已提供表面或多视图输入；不强制消费者采用不存在的设备能力。
5. 任一宿主发生失败、超时或回退时，另一宿主仍能读取自己的结果和诊断。

本文整体保持 DesignReview/Prep。主控于2026-10-10已分别接收Core和可发布Simulator切片为ModuleCoreImplementationReady。Core范围仍仅值校验/分桶等权/建议/执行协调及已冻结端口下测试stub/TestHost；Simulator独立范围仅§13.4～13.7的明示值/端口/脚本/控制/资源Owner和两个无UI Host，不混入既有Core接收。两者均为规格准备，不表示真实消费者已运行；真实Adapter/Integration/计量/性能/生产资格仍分别验收。

## 18. 实施前未决项

- 正式 Contract/Schema 字段、状态 Owner、事件信封和错误枚举尚待公共 Owner 采纳。
- HALCON 26.05 算子路线按 §7 冻结，全部经 ImageLibDotNet.cv2 调用；不核验“封装是否包含算子”。仅真实 C# 参数类型/重载/封送歧义在 Adapter 切片查看公共签名或编译解决，不扫内部，不另接 halcondotnet.dll。真实算法/异常/资源验证仍须执行。
- 模块PatternSpec、camera_setup资产端口、StereoSpec/CameraFrames和处理布局已在§4/7/8冻结；实际消费者图案/标定/资格阈值资产与PerformanceProfile尚待提供/采纳，仅阻断真实Adapter/Integration/资格。
- 公开输出没有ObjectModel3D handle，不设计私有模型持久格式，也不在本模块创建Store/事实库。宿主需要封存值表面时沿SurfaceData v0.4原SurfaceDescriptor/原raw buffers及§18 `surface-metadata/1`与`surface-raw-buffer/1`；实际多父权重沿C5原Contribution metadata，而非只存一个Root索引。生成新载体的生产者/宿主Owner负责原完整buffers、坐标/单位/三态/原因/Origin/Root、完整CSR及权重的无损映射；不能保真表达则不封存假flat结果，继续保原API值/来源并拒对应导出。存储事务/耐久/证据提交归IM-066 storage-database与IM-015 inspection-evidence的实际Owner；本模块只交不可变值和现有诊断/Decode编码，CAL原文件/资格规范编码仍CAL独占。全ReconstructionResult聚合投影暂无独立落盘codec消费者，不新增空格式/manifest；若具体产品需要整体聚合封存，产品Owner先在其唯一指导批准对应映射/codec登记，不能把当前一般措辞当第二套发布契约。
- 真实标准件、镜面/黑表面/遮挡样本、计量不确定度和 HIL 资格尚未取得。
- IM-033 `registration-3d` 已由主会话裁决为方向变换估计、资格化、发布和撤回的唯一 Owner。IM-032 只消费已发布不可变变换/标定快照，应用一次并记录 provenance；不估计、不资格化、不重复应用、不发布变换。正式字段、错误信封和跨模块 Contract 仍待串行采纳。
- `PartialResultPolicy`、`DirectionIssue`、`FusionPolicy` 的模块API已在本文冻结，映射到 IM-031/IM-033 的正式字段和错误信封仍待公共 Contract Owner 串行采纳；不得以正式映射未完成否定纯Core值契约，也不能成为第二套平台Schema。
- 0.2.5-prep角色/诊断增量已接收；structured-light原Owner按主控接收合同补原角色/RequestedLayers映射，当前上游未更新桥不能声称已运行。CAL-JC共同标定软件合同已接收；§7.6首次标定decode-only C1/S1六项规格已接收，A1固定路线/公开工厂内容限定接收，两消费者实际桥/封存/运行仍未验。原重建接口Both诊断、Defect、错误route层组合、rad/deg解读仍明确不支持。真实共同求解/camera_setup读取与光学运行验收分别保留，不再把“必须先有setup才能decode”作为初始化要求。
- 0.2.7-prep的§8.1 Joint重建消费沿已限定接收CAL0.3.2-prep §7.4.6B原helper，补同次Owner原响应/完整复查/技术指纹与Export真实文件身份、专用伴随绑定及两原Host组合根；Joint消费增量已获主控限定内容接收。真实资格Owner/来源、source/adapter公开程序集装配编译、native释放/文件处理、性能/物理与产品提交资格仍`PreparationIncomplete / NotReady`；不把普通RevisionRef或synthetic绑定测试当生产运行，原Core/Simulator/Decode接收保持。

以上历史接收与原后门保持。0.2.8本轮已冻结普通/Joint公开factory、tuple/real精度、SD桥及WPF资源/恢复；真实编译/执行仍未验。CAL消费者当前按0.3.3-prep §7.4.6B/9.4定向核兼容，见§8.2.1；不要求上游重复研究。SurfaceData0.6.0公开读/metadata/精度/绑定边界按§7.7.2保持；本桥不调用H滤波，若宿主独立调用H必须沿其§17.3三参数SurfaceImageLibFactory.Create(adapterBudget,time,runtime)及真实Worker/hash/commit/Accuracy，不用旧两参数入口、不把float32复制声称无损。

剩余条件只阻断依赖它的运行/集成/资格，不允许脚手架、隐式默认或第二套字段绕过。精确Owner与影响：

| 剩余条件 | 唯一Owner | 阻断范围 |
|---|---|---|
| 实际程序集C#重载/封送、Adapter/native clear及有限排空、部署envelope实测、Golden与精度表示反例 | IM-032原模块会话/实现Owner，使用批准依赖 | 对应真实Adapter运行资格；不是未决定算法或依赖准入 |
| 原完整图案/采集epoch/曝光/白面mask、传感器metadata/root/buffers | structured-light/采集或原Surface生产者Owner；IM-032负责实际消费桥 | 对应真实输入路径，不能阻无关Core/Simulator |
| Joint资产/Export完整文件/用途及原资格快照/水位 | CAL原Owner + qualification资格Owner；两宿主保原关联，IM-032专用factory执行 | 真实Joint路径；二维局部平面不替代它 |
| 已发布变换/撤回/完整坐标链 | IM-033 registration-3d Owner；原坐标Owner | ApplyPublished/共同坐标消费，AlreadyInOutput无关能力保持 |
| Viewport真实Presenter/OwnSession=false归还、WPF三语/UIA/固定client/DPI/响应实测 | IM-060 viewport原Owner负责其renderer；IM-032负责控件；宿主负责Bridge/root | 对应可选UI及实际Viewer接线 |
| 产品Schema/聚合codec登记/证据与存储事务、用途/权限/提交采纳 | 对应产品事实Owner、inspection-evidence/storage-database原Owner | 对应产品集成/持久提交，不阻模块纯值合同 |
| 客户误接受/拒绝/公制精度/节拍、标准件/物理样本/计量不确定度/现场HIL | 客户/设备/计量资格Owner提供事实与目标；模块Owner执行验证 | 具体生产用途及物理资格，不能编造或转成所有软件停工门 |

## 19. 依据与只读核对记录

既有架构/消费者输入：PKG-028、DEV-VIS-027、FS-012、FS-013、PKG-027 和独立模块架构；它们只提供来源与平台接入约束，模块实现以本文为唯一当前权威。HALCON 25.11 历史摘录只作差异对照，不覆盖本地26.05；不扫描 AsunImage 内部，不核验依赖许可/安装/兼容性。

### 19.1 HALCON 26.05 本地原文

读取 `halcon算子手册/operators` 内 Operator Reference **26.05.0.0** 原文；下列关键页 SHA-256 为本轮只读文件身份（原件未修改），普通读者按对应原文核查 API，不依赖一次性研究脚本。所有算子经 ImageLibDotNet.cv2；本文给处理语义和公开端口，真实 C# 重载/封送歧义在 Adapter 消费项目定向编译。

| 本地算子页 | SHA-256 | 采纳落点/限制 |
|---|---|---|
| [gen_structured_light_pattern](../../../halcon算子手册/operators/gen_structured_light_pattern.html) | `18d525eeb3fb1475afb1aea1cf9473dc35de5a8cf471a7c3e9c073f8678cb948` | §7.1 四步相位、图案布局；不套三步相位 |
| [decode_structured_light_pattern](../../../halcon算子手册/operators/decode_structured_light_pattern.html) | `6647813490fb72589068375f1ce21cd9639b147467555588921c71c044e70c6c` | §7.1 帧序/persistence/诊断 |
| [create_structured_light_model](../../../halcon算子手册/operators/create_structured_light_model.html) | `d5792a723895470b0e66514d87fcb6967fd7197c90f3d1587ea223e580aa6170` | §4.4.1/7.1 3d_reconstruction与deflectometry分开 |
| [get_structured_light_object](../../../halcon算子手册/operators/get_structured_light_object.html) | `058227815d2bd5e50f9cf7bd91652f6b19e6b1e93a434bcf7f1aa31bbf012b31` | §4.4.1 六种支持object/persistence/原domain，Defect拒绝；未定义的phase/Gray/stripe数值尺度不猜 |
| [get_region_runs](../../../halcon算子手册/operators/get_region_runs.html) | `39ae03235b99a4b34f24ff019d5738280f3da12ae1be1ebbfa81211193cd6c15` | §4.4.1 单region、闭区间runs按row/column递增、空域空tuple |
| [get_grayval](../../../halcon算子手册/operators/get_grayval.html) | `930d4a89168dd7f5a3780e1ce21ec595c62ecf026a79342abe87e8f29042d2cf` | §4.4.1 有界读取；算子忽略domain，必须先取真实域 |
| [get_domain](../../../halcon算子手册/operators/get_domain.html) | `a5e227e173652cb2b0eb48e3afb1044c43378b6f3dac5be8ae19adc3c87703ab` | §4.4.1 每原image的支持域，不套Surface mask |
| [get_image_size](../../../halcon算子手册/operators/get_image_size.html) | `9f9dfacddacf8cea96986fe2478e84e139a15e944aac2c7720be7020db0d4d78` | §4.4.1 原camera W/H核对 |
| [get_image_type](../../../halcon算子手册/operators/get_image_type.html) | `e1d0eb3106ecc726f03493acd2ab860e5e254f248ae96697cda51d2ac857d7ec` | §4.4.1 类型核对；多通道时只报首通道类型，不能代通道数检查 |
| [count_channels](../../../halcon算子手册/operators/count_channels.html) | `27f21bc0e0589ef514da1c2b94059912d64125b09d75fe527229a80ab6d888ce` | §4.4.1 灰度读取前强制单通道，不分配后才发现多通道 |
| [set_structured_light_model_param](../../../halcon算子手册/operators/set_structured_light_model_param.html) | `898dddd8137f941ec78c0ae187886ac954abd455d06183dc4d98962afc2618be` | §7.1 decode前固定参数/persistence；变更清旧结果 |
| [reconstruct_surface_structured_light](../../../halcon算子手册/operators/reconstruct_surface_structured_light.html) | `86e3ebf6dd45e4348ea34dc5914097159ad17b1571a5dba561d55e7b0bd16b75` | §7.1 标定世界坐标与vertical对应 |
| [object_model_3d_to_xyz](../../../halcon算子手册/operators/object_model_3d_to_xyz.html) | `be1f9872038965ebcbe1e7a9cad8655e63a63a679e27e2f568f53c20dcdf8e52` | §7.1 from_xyz_map/domain，不以Z=0判空 |
| [get_object_model_3d_params](../../../halcon算子手册/operators/get_object_model_3d_params.html) | `f2a7a313eb79f11d14e095af651301e47bd6e33118797890537189c62a1d70e6` | §7.7.1原模型double坐标tuple与同point ordinal的mapping，mapping_size顺序width/height；不把real图当无损值 |
| [reconstruct_surface_stereo](../../../halcon算子手册/operators/reconstruct_surface_stereo.html) | `773e4250c65388a0dfc63b6debb7f64e49addd9b56a10af7662b5e35ed23b68f` | §7.2 surface_fusion补洞仅展示 |
| [get_stereo_model_object_model_3d](../../../halcon算子手册/operators/get_stereo_model_object_model_3d.html) | `dccaf9f3320ad2a726ba76f6c8506fbb475aa96132589b8e5ce7bf64108e3fba` | §7.2 persistence/m3d_pairwise/-1；无逐顶点来源排序保证 |
| [get_stereo_model_object](../../../halcon算子手册/operators/get_stereo_model_object.html) | `b039e7e97854349101a3ff0535f4502cc6d444b5e489e65ee71789c2cc18f973` | §7.2 [From,To]的持久化disparity/score |
| [get_stereo_model_param](../../../halcon算子手册/operators/get_stereo_model_param.html) | `06e7f9d4daacc795eaf0e7a68539fdfbab15bd57bbccde9542dffdc2caff78ec` | §7.2 每对整流参数/pose分开查 |
| [set_stereo_model_param](../../../halcon算子手册/operators/set_stereo_model_param.html) | `38d3045881fa2d15565b59b31372b5c091cf137671fc553f0190814411655ebd` | §7.2 NCC/filter/rectif参数；bbox先设 |
| [set_stereo_model_image_pairs](../../../halcon算子手册/operators/set_stereo_model_image_pairs.html) | `4531da49ba162283a5de519900657a3906ce403f1b48fcd18fa700c411c255c0` | §7.2 冻结相机对与整流模型 |
| [disparity_image_to_xyz](../../../halcon算子手册/operators/disparity_image_to_xyz.html) | `4c230d0bd3815b3ddb6b9ad74550760bb8366f03240fa384320da84bfc3ea3bb` | §7.2 像素映射至rectified From XYZ |
| [get_camera_setup_param](../../../halcon算子手册/operators/get_camera_setup_param.html) | `e376e8d7503924994720ef6d1e7178d4da2a9f7d4102fcfc378d844ca7e59565` | §7.2 原相机params/pose相对setup |
| [gen_binocular_rectification_map](../../../halcon算子手册/operators/gen_binocular_rectification_map.html) | `ef35548d931c020063c89982db3762d295c56614b6ab792ea853cb9a9bbef4b3` | §7.2 子像素映射与bilinear支持；非整数原图索引 |
| [project_3d_point](../../../halcon算子手册/operators/project_3d_point.html) | `75072695206dd30171a7c115b6a8329bd870bda37056f6158acf49d77cae18af` | §7.2 原相机/整流相机射线子像素定位 |
| [pose_to_hom_mat3d](../../../halcon算子手册/operators/pose_to_hom_mat3d.html) | `6a561410d067782f2ce8382cc6643e2806a8b7cf64feef3668406a53ba10fc2c` | §7.2 标定pose矩阵方向 |
| [hom_mat3d_invert](../../../halcon算子手册/operators/hom_mat3d_invert.html) | `6a0a21ccf062dae020548d1173462520922082eea0c4f3e4b23fe4d8d34441d8` | §7.2 rectFrom→rectTo，仅标定内部逆变换 |
| [affine_trans_point_3d](../../../halcon算子手册/operators/affine_trans_point_3d.html) | `d9b4b57141a357e1598b70561c0f715f66f1701c05cdde7c34f94cedec046be0` | §7.2/7.3 标定坐标链和独立一次方向变换 |
| [affine_trans_object_model_3d](../../../halcon算子手册/operators/affine_trans_object_model_3d.html) | `63fb2aa241760de56d05f928dc692385d05ffce2d6b243f7505ab09a7a31832a` | §7.3 一次变换；通用属性需单独保护provenance |

create/set/get_structured_light_model/object、create_stereo_model、binocular_disparity、fuse_object_model_3d 同版本原文亦已核对：结构光camera=0/projector=1、投影器inverse camera、correspondence/pattern_region不需persistence、解码中间图需要；NCC高分好而mg/ms低分好；闭面融合不能替代真实支持。未运行 HALCON 图像/计量/内存试验，官方语义不是性能或现场证据。

### 19.2 OpenCV 实际源码/测试（只移植诊断和测试思想）

仓库 [opencv/opencv_contrib](https://github.com/opencv/opencv_contrib)，tag **4.12.0**；`git ls-remote` 的 `refs/tags/4.12.0` 引用为 `7deb35fde4d38d73b6173c7ab2aeddc8df5a89e3`。已读 tag raw 和该 revision 的 codeload tar 流源码/测试/CMake/许可，未把 tar 落入仓库。该引用未额外证明 annotated tag 的 commit 解引用；文件内容以下列hash固定，不把一次revision raw 404/API403说成已成功读取。研究输入不是本模块 runtime依赖。

| 实读路径（均在 modules/structured_light，LICENSE在仓库根） | SHA-256 | 可借鉴/不能借鉴及正文落点 |
|---|---|---|
| src/sinusoidalpattern.cpp | `cce9bb6189e6eac13b01f9e29353bddfcaebe4e966fa28138f146b223e1e13ff` | phase/shadow/modulation诊断思想→§7.1；decode只CV_UNUSED+return true、findProCamMatches空，不能作完整重建；三步/固定灰度10不能替代HALCON四步/Profile |
| src/graycodepattern.cpp | `eb2840559d4ee81d49a589376f8f0e2c8760bda3bd86e0630879d5ce145e2a7e` | 正反图弱差/越界拒绝→§7.1/7.5；同projector pixel多相机像素取均值不能成为本模块多层真值 |
| test/test_faps.cpp | `07567f20166736fb68702fd85720baedd4cc5f15d51193e504979b5e2a4211bc` | 实际测试使用8-bit参考、有符号平均差/整数除法，可误差抵消；§13不采用其指标为公制验收 |
| test/test_getProjPixel.cpp | `846a2937852a009e124f95f37ef1aadb1e248f520cdddf15b7cb6734a3b441b0` | 完美生成图逐像素identity思想→§13来源映射fixture；不证明反光/运动/噪声现场鲁棒 |
| test/test_plane.cpp | `d1baeade13b44e11fa9c33db59c98b46620637b267653e5470ac3fbc1652cd40` | 标定单位/reproject/平面距离→§7.2/13真实标准件；上游3mm不作客户公差，value!=0不适用合法零/负高度 |
| CMakeLists.txt | `b94fff5b53d627d4e04fe0f5417a178a1d2a3a21db590770affc662b9be4f2d8` | deps core/imgproc/calib3d/phase_unwrapping、optional viz；不整库复制、不引OpenCV runtime |
| LICENSE | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | 仓库Apache-2.0；相关旧源文件头还保留BSD-3-Clause形式声明。当前只借思想，未来拷源码须按DEV-GOV-006保留对应来源/声明 |

没有执行这些上游测试，不把README、星数、营销、截图或上游测试名字当生产证明；本模块oracle是§13明示值与消费者真实计量Profile。

### 19.3 DevExpress 官方25.2 API（保持项目25.2.3）

dxdocs工具当前未提供，直接HTTP读取403；已在浏览器实读以下官方V25.2页面及程序集信息。页面现在示例25.2.10不表示本项目升级；继续用本机**25.2.3**，不下载或替换。

- [DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)：LayoutGroup/LayoutPanel和布局保存恢复→§10.1。
- [PropertyGridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.PropertyGrid.PropertyGridControl?v=25.2)：SelectedObject、搜索/属性定义→§10.1只读Profile/draft。
- [TableView.AllowPerPixelScrolling](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TableView.AllowPerPixelScrolling?v=25.2)：bool、异高末行可能部分显示→§10.1方向表/长英文行实际验证。
- [ChartControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Charts.ChartControl?v=25.2)：Series.DataSource/ArgumentDataMember/ValueDataMember→§10.1有限聚合统计。
- [FlyoutControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Editors.Flyout.FlyoutControl?v=25.2)：IsOpen/StaysOpen/PlacementTarget、LiveSetting/LiveRegionChanged/HelpText→§10错误恢复/UIA。
- [SuperTip](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip?v=25.2)：普通控件ToolTip中的SuperTipControl、BarItem.SuperTip→§10非显然行为提示。

真实 WPF 25.2.3 控件、1920×1080、DPI、键盘/三语/UIA 和响应验证未执行，不能以官方页面代替本项目UI验收。

## 20. 自审结论（2026-10-11，文档阶段）

### 20.1 0.2.8完整批准范围的准备结论

**本轮已补齐当前架构批准能力内可决定的软件设计；正文没有仍需程序员补做的模块算法、公开装配、值映射、UI任务/资源Owner或恢复设计欠项。** 该结论仅指唯一指导的文档可实施性，整体仍DesignReview/Prep；原Core/Simulator/角色诊断/Decode六项接收保持，新增Adapter/SD/Joint factory/WPF指导不自动取得ImplementationSpecificationReady、ModuleCoreImplementationReady或生产资格。§18逐Owner列的是实际实现/集成/输入/测量门，不能把本文收口当作未运行的编译/native/WPF/现场通过。

| 完整批准能力/真实消费者 | 唯一软件实施位置 | 准备与后续验证边界 |
|---|---|---|
| 完整结构光、Hybrid/Gray/SingleStripe、来源与诊断；结构光工具/3D AOI | §4.2.2/4.4.1/7.1/7.7.1/8.2 | 参数/序列/域/tuple/precision/预算/公开factory与clear闭合；无domain、映射不可证拒绝，真实图像/Golden/调用/计量未验 |
| 无先验setup的Both解码、CAL-JC输入封存；初始化工具 | §7.6七子节 | 已接收C1/S1保持，既有六向量不改；实际Mapping/白面/采集/封存、native与共同求解仍原门 |
| Joint资产/资格消费与普通setup分流；两个原Host | §8.1/8.2/8.2.1/11 | CAL0.3.3原helper兼容，真实专用工厂/源公开；原Task/原响应/水位/file三域与根保真，原JRC结果不替代真实装配 |
| 多视立体/NCC/原观测与显示表面；3D AOI/表面实验 | §7.2/7.7.1/8.2 | 保surface_fusion主路线、disparity射线、float32表示上限；不猜m3d顶点对应、不补洞成量测；实际公差/envelope/native另验 |
| 已给HeightField/PointCloud/ObjectModel来源的无句柄值；表面实验 | §4.4/7.7.2/8.2 | 管理值source与SD明确factory/StartRead/Root/int可表示性/失败整批失效；ObjectModel仅源类别，不接句柄。TriangleMesh/C5多父无法映入当前值形状时明确拒绝，原源保留；直接完整CSR值仍可无UI消费 |
| 一次已发布变换、网格代表/等权融合/冲突与不确定度 | §4.2.1/4.3/4.4/7.3/8/9 | 既有Core接收保持，原数学/CSR/半开域/全部冲突输出不改；真实IM-033快照/坐标/资格归原Owner |
| 无UI参数建议、来源/候选/弃权/过期与生产分离 | §5.3/7.5/10.4/10.5 | 已有公开无参算法不改，UI只请求和投影、不生成标签或发布生产值；holdout/客户用途另验 |
| 可嵌入WPF高级联动/三语/键盘/权限/错误/关闭；工程A/只读B | §10.1–10.5/13.8 | 公开三参数Bind/Viewport bridge/限额/原Task根/只停自己run/迟到代/Detach归还闭合；真实1920×1080/UIA/DPI/可见/资源未验 |
| 独立发布Simulator/Replay、版本/双Host/升级回退/证据投影 | §11–18/A.1–A.3 | 原接收/fixture/预算及独立工程保持；原事实不变、格式沿SD/CAL/原codec，不造第二Store；产品实际桥/保存事务/性能/现场另门 |

有限自审两轮：第一轮从独立Host正向构造普通/Joint/SD factory、原Core及两个STA UI装配到有限退出，发现并修正native装配未命名、real图误当无损、source无request却借CalculationId、RootFrame不在输入、WPF未注入Viewport/不存在Validate与Suggest入口、只读关闭误停核心、持久格式/证据Owner编号和旧Joint表格列数问题。第二轮从失败逆向追踪缺映射/量化超限/unknown Origin/Int64不可表示/部分块/资格撤回/源晚到/clear失败/保存Unknown/旧代投影/Dispatcher与Detach未退出/接管违约，确认原Task/lease/handle/完整资格伴随对象仍保原根，有限观察与资源释放独立、无假终态或默认viewer。实际新增验收明细在§13.8；不重复旧研究/向量/无影响已接收范围。

消费者兼容影响明确：Core公开值/端口、Simulator及Decode既有编码不改；新增普通/Joint factory与SD读桥仅Adapter依赖CAL/SD的公开合同；CAL0.3.3局部平面/.dat/专用方法和自动参数不改变本Joint消费；SurfaceData0.6.0的原Int64/三态/Origin/精度和H运行绑定保持，当前桥只接受能无损表达的单根观测。WPF尚无投产ABI，本版冻结三参数Bind及完整命令/关闭类型，未来消费者必须显式注入已绑定Viewport、资源、限额和根，不保留隐藏默认旧重载。真实源码编译、工程/Host/native/SDK/WPF运行、Golden、Benchmark/HIL/计量/现场本轮均未执行，没有修改代码/上游/共享文件或新建脚本/报告。

### 20.2 0.2.9上游UI装配窄同步结论

仅§10.4.1补齐viewport0.3.4-prep WPF Assembly Contract v0.2的实际Host消费：同Control.Presentation进入原session Options、Options.Lifetime必填且同renderer/root、Acquire完整ViewportPresenterSubmission、Catalog/schema/实际标签资源和原binding观测。按原A/B装配正向及缺Lifetime/跨Owner/旧schema/旧Acquire签名/迟到呈现逆向核对后，**§20.1完整批准范围的内部软件设计闭合结论保持**；本模块Bridge公开面/Core/算法/原根/Close/三语与向量不变，不借上游UI修订重开已接收切片。上游必需成员/资源schema由viewport原Owner定义，真实Host装配和自有Lifetime迁移由消费Host负责，IM-032负责本可选控件与Bridge正确消费。

本轮已执行定向检查：新增章节唯一、围栏闭合、本地链接及§10.6目标锚点、公开类型/Acquire方法/具名Options字段及schema均与上游声明匹配；本模块Bridge公开形状无Lifetime/Submission新成员。复用`python -B tools/validate_docs.py`的结构/链接/DAG/消费者映射校验通过。旧正文修改仅版号及本节插入，不重算或重审旧接收范围。未创建或执行C#/工程/新报告脚本、真实Control/renderer/native/GDI读回、UIA/双STA、性能或现场验收。对应运行门仍PreparationIncomplete / NotReady，全模块DesignReview/Prep和原Core/Simulator/Decode/Joint已接收范围保持；总控只登记该原会话结论，不再安排内容审核。

以下0.2.4–0.2.7记录是当时有限自审/接收沿用依据，不代替§20.1全范围结论及§20.2窄兼容结论。

本轮已执行文档验证：复用`python -B tools/validate_docs.py`通过当前指导结构/链接/DAG/消费者映射；本文定向围栏/表格列数/新增章节唯一性/本地链接、CAL/SD公开类型引用与新增声明重名检查通过。旧Decode六个hash字面值仍在、未重算其旧接收向量；新Root1000-byte合成原件布局/6有效槽及显示slot算法的边界在内存核对一致，不写新脚本或证据文件。StartRead返回前可能先回调的OperationId关联已显式保待关联槽、完成关联前不采用；UI只读关闭和有限根恢复已反向检查。以上是文档/合成值核对，不是产品编译/Host/算法/性能/现场运行结果。

0.2.7-prep仅在§5.1.1/§8.1/§11/A.1补Joint消费者指导，两轮有限自审完成：①按CAL §7.4.6B逐声明核同次Resolve/Owner Task/Query关联、复查新ID/同Owner、Expected取原封存值及撤回/epoch/证据变化的拒绝，核asset摘要/完整资格快照技术摘要/setup文件摘要三域独立、全Scope/Revision/水位/evidence随伴随对象保真；修正普通setup hash规则的Joint专用分支，明确两软件Host Store使用CAL原完整内容闭包，不拿纯值label asset冒真实artifact。②走两Host正常装配、缺伴随对象/来源、错误Scope/Export、迟到查询/factory/关闭/移交失败及输出未归还分支，核组合根先预留、64原Task/8输出与桥1MiB加真实Export/其它费用、独立有限Stop/Dispose/首业务错误/真实释放；native各阶段开始前再核失效/期限，关闭后迟到值不重新获得消费权。定向检查已通过本文fence闭合/表格边界、新§8.1标题唯一、本地文件链接和CAL目标锚点、上游公开类型引用/Host私有边界/JRC01～06/根恢复及旧向量字面值/接收状态保留；没有重算或新增CAL/本模块编码向量，没有创建文件/工程、编译、执行Host/资格Owner/真实native、Benchmark或物理验收。0.2.5/0.2.6及原Core/Simulator/Golden接收保持；Joint消费增量已获主控限定内容接收，真实资格Owner/native/公开程序集编译/性能/物理仍`PreparationIncomplete / NotReady`。

0.2.5-prep仅在本文补§4.2.2/4.4.1、§7.1接线、Simulator新可选值的校验/计费、§13.6.1两原Host全字段输入输出及八份编码oracle、§13.7.1增量验收。Black/White/GrayInverted不冒Gray，序列与生成图hash按原顺序核对；诊断不交句柄、不改变原pixel域、不冒rad/mm/质量真值，显式不支持项/失败/取消/Unknown/预算均有固定路径。主控于2026-10-11已完整回读并沿Core/Simulator六项软件规格接收此增量，另独立字段重建八份规范编码，全部length/hash一致。旧enum0..6、API0.2/构造、F0/F0-S/ST0及R01～R25/S01～S03保持；这是规格准备，不是实现/真实算法运行。本轮0.2.6-prep追加§7.6独立decode-only/Both具名对应软件切片，主控已完整回读§7.6.1–7，独立重建A/B两组Mapping538、修正MaxPixels96的Request6894、Result3895 bytes及五种payload48/48/6/6/6 bytes，全部长度/SHA一致；R3D-Decode-C1/S1六项规格已接收为`ModuleCoreImplementationReady`（仅规格准备），R3D-Decode-A1固定HALCON路线/公开工厂内容限定接收，真实native/Golden/Envelope/消费者封存和运行资格仍`PreparationIncomplete / NotReady`。

0.2.6-prep两轮有限自审已完成：第一轮逐字段走查公开Factory/DTO、Both显式映射、producer白面mask来源、两原域/共同支持、CaptureEpoch与ClockEpoch、源晚到/取消/Unknown、524内层Task和五Host原Task/根移交；补全Request.Version、校验错误优先序及实际部署与冻结Info身份绑定。主控预读指出的夹具MaxPixels6不足以容纳projector G96已修为两Host均96，原N/G预算契约未放宽；无依据的容差0.5硬上界已移除，具体容差仍来自已接收Golden计划，软件夹具0及唯一排列条件保持。第二轮以独立内存Python按公开声明重建A/B Mapping538、Request6894、Result3895 bytes，六份长度/hash及五种原payload/hash均匹配最终正文；受预算修改影响的四份Request/Result hash已同步，mapping/payload与Input90/146、Managed385152、Result134276、Simulator1062064/1062288预约保持并复算一致。定向检查确认本文fence闭合/表格边界、§7.6七个子节唯一、本地文件链接存在、旧enum数值保持、SupportUnion无新PatternRegion残留；gen/decode/get三个本地26.05原件hash与§19记录一致。以上仅文档/字节与预算核对，未执行C#编译、双Host、真实HALCON/Native Golden、WPF、共同标定封存/Solve或消费者运行；不提升本切片接收状态及产品资格。

本轮两轮有限走查只依据当前正文与保留的来源，不重复下载/全仓审计：

1. **物理/数据反例**：完整/缺帧/跨attempt、空和超大图、弱调制/饱和/遮挡/反光、多周期/多层候选、参数变化、合法负/零高度、立体整流与世界坐标、半开网格边界/同方向深度歧义/跨方向冲突。关闭了m3d_pairwise顶点顺序猜来源、isosurface补洞成为观测、零高度判空、单位/坐标二次转换以及全冲突时丢CSR的缺口。立体来源现在由同一运行的逐对disparity枚举，两端子像素射线与FrameId显式保存；没有现场资料的物理公差仍为外部门。
2. **独立接入/生命周期反例**：两无UI Host、duplicate/busy、调用方修改输入、source断连/消费异常、取消/超时/迟到任务、source释放异常、Unknown关闭、Query驱逐、APImajor/版本回退。关闭了finally释放在途实例、无限等待外部端口、未知后丢Task/Owner、传感器漏标定revision匹配及Windows/WPF混入纯Core测试入口的缺口。Host有限观察后唯一Retain，两个ID保留与结果引用预算分开；同步/异步/质量/终态不互相冒充。

§19已经记录实际读取的HALCON26.05、OpenCV4.12.0源码/测试的固定版本/hash及强项/限制、DevExpress官方25.2 API落点，本次未重做研究。Core F0/F0-S、R01～R25及已接收范围保持；Simulator新增§13.4脚本/构造、§13.5控制/租约/查询、§13.6发布包双Host、§13.7 S01～S03/ST0与10/120/180s真实期限和虚拟clock区别。A.1/A.2绑定BCL Exe与执行命令。以上是规格走查，不是任何C#或上游测试执行。

本次追加两轮有限定向核对：第一轮走正常业务→成功清理、业务成功→Stop/Dispose未知或异常、业务失败→清理异常、Retain违约与槽满/factory失败，确认finally后才返回、错误分开且未确认前原槽不丢Owner；第二轮从空BCL Host直接构造ContrastRecommender，走Suggested/Abstain/null/非法/Cancelled优先序及R23，并对照Simulator后续门/测试stub边界。上述分支是正文自审与静态定向核对，没有执行Host或推荐器C#实现。

本轮Simulator两轮有限自审：①脱离Core.Tests从公开factory/clock/gates构造A/B/ST0，核对payload/hash/CSR/模式参数、synthetic不可Qualified、恒等变换一次、Replay/脚本非法及有限预算；②从source晚到/执行拒绝/partial/取消/回调阻塞/lease释放阻塞走到Draining/Unknown、gate放行、原Task退出/五Task根槽、engine factory异常与接收违约，核对首业务错误和cleanup不覆盖、观察超时不释放、finally不以未知返回0。修正了CallbackExit的重建/变换ResourceId区分、release默认不可取消、ST0匹配窗口尺寸/时序、两个根Owner顺序及非法不可到达步骤；不是HALCON/运行测试。

0.2.4-prep只追加一次公共集合边界走查：Simulator持久集合/字节/gate输入改ImmutableArray，嵌套Core集合仅接受真正immutable值，单次PrepareSnapshot先限额复制、后在同一快照上校验并保留；Errors/Events/返回值不暴露builder/ring-buffer别名，事件Kind固定显式enum。同步§13.6双Host与S01～S03的default、恶意不稳定IReadOnlyList读取前拒绝、修改原容器不影响快照、旧Query跨gate释放不变断言。Core契约和已接收范围、算法、四倍预算、10/120/180s及真实验收门未改；此次仍未执行Simulator实现。

Core六项内容在A.3定位，主控于2026-10-10已内容接收为ModuleCoreImplementationReady；范围不变，没有代码或测试通过结论。Simulator六项规格已由主控独立内容接收为ModuleCoreImplementationReady，范围仅§13.4～13.7发布模拟包的明示值/端口/脚本/控制/资源Owner和两个无UI Host，不授真实算法或标定，不改变Core范围。实际工程/编译/运行/性能均未执行。真实Adapter需实际标定/图案/时序/样本/计量Profile及native资源故障验证，WPF需1920×1080真实控件/三语/UIA验证，Integration需平台映射/发布Owner和两真实消费者，性能目标缺失为NotEvaluated。当前全模块DesignReview/Prep；没有产品代码、真实HALCON/WPF、Benchmark、HIL或现场验收结论。

## 附录 B：第二轮场景驱动架构复审（2026-10-04）

本附录用反例重新推导模块边界。每个场景都必须能在无 UI 宿主中执行和判定；表中的默认值是软件防护，不是工艺阈值或现场资格。除非特别说明，参数来源依次为：不可变输入快照 → 已 hash 的 Calibration/Pattern/Stereo/Algorithm Profile → 本请求显式参数 → 模块固定资源上限。方向变换只由 IM-033 估计、资格化、发布和撤回；IM-032 仅消费已发布不可变快照一次。缺失来源时拒绝，不用默认值补齐。

### B.1 逐场景执行与验收

| 场景 | 输入与参数来源 | 处理顺序 | 输出与状态/错误 | 恢复动作 | 可判定验收 |
|---|---|---|---|---|---|
| 正常单方向结构光 | 完整同一 `InputSetId` 的图案帧；`PatternProfile`、`camera_setup_model` 和 `AlgorithmProfile` 均有 hash | 校验序号/PatternId → 创建独占 `3d_reconstruction` 模型 → 设置PatternSpec → gen_pattern核对布局 → 设置标定/persistence → 解码 → 重建 → 有效域检查 | 一个 `PerDirection`；`Fused=null`；`Completed`；质量为 `QualifiedCandidate` 或 `Unverified` | 若质量不足，保留结果和原因；宿主决定受控重采集 | 每帧来源可回溯，解码前无缺帧，单位/坐标明确，重复 Replay 输出在允许误差内一致 |
| 正常多视立体 | 已校准相机 setup、按模型顺序排列的 image array、StereoModel Profile；首发仅接受模型固定为 `surface_fusion` | 校验相机顺序/配对/ROI → 调用 `ReconstructSurfaceStereo` → persistence=true 的 m3d_pairwise核查/逐对disparity→XYZ→setup/原图子像素来源 → 原生单位转 mm → 显式一次变换 | `PerDirection` 或立体表面；`Completed`；路线和 Profile 进入 provenance | 模型路线不是 `surface_fusion` 或能力/配对不满足时返回 `R3D-008`，不得切到 `surface_pairwise` | 相机顺序错位被拒绝；实际执行路线与 Profile 一致；输出不被当作最终质量事实 |
| 多方向融合 | `MinContributingDirections` 在 2..请求方向数内；`FusionPolicy`/`AlgorithmProfile` 已 hash；IM-033 已发布快照可验证 | 逐方向质量门 → `ApplyPublishedTransform`（消费 IM-033 已发布不可变快照一次）→ 若完成合格方向不足门槛则跳过融合，否则执行共同支持域/差异门及确定性等权平均 | 缺失/未发布/作用域不匹配返回 `R3D-018`/`R3D-019`，不执行融合；正常时保留每方向和 `Fused`；方向数不足时保留每方向、`Fused=null`、`Partial` 及 `InsufficientCompletedDirections`；没有任何元素满足支持/贡献门时 `Fused=null`、`NotQualified` 及 `NoElementMetContributionMinimum` | 由上游/IM-033 重新发布匹配快照；IM-032 不自行转换或估计。冲突域隔离；不降低最小贡献门槛，不插值、不补洞，不以部分成功绕过门槛 | 任意融合点可反查方向/帧和变换 revision；不足门槛时无 Fused 数组且 issue 数值正确；局部无效点有原因码；冲突比例可重算 |
| 空输入/空方向/零像素 | `Directions=[]`、空帧列表、宽高为零、只有非法帧描述或 `InputSetId` 为空 | 仅执行 `Validate`，不创建 native 句柄、不排队 | `Rejected` + `R3D-001 InvalidRequest`；全局不生成结果 | 修正输入并创建新的 `CalculationId` | 没有 `ResultAvailable`、没有句柄泄漏、没有 Partial/Qualified 伪结果 |
| 部分成功 | 多方向中至少一个方向完成，另一些方向因遮挡/资源/适配器错误失败；`PartialResultPolicy=KeepSuccessfulDirections` | 每方向独立租约和错误隔离 → 记录成功/失败集合 → 仅对成功且同坐标方向尝试融合 | `DirectionIssues` 含失败记录；`PerDirection` 只含成功表面；至少一个成功结果；总体 `Partial`/`NotQualified`；失败方向保留错误 | 宿主可只重算失败方向，必须新 `CalculationId`；不得覆盖成功方向 | 零成功方向自动变为 `Rejected`；失败方向不能缩小冻结请求覆盖分母；融合不会读取失败占位 |
| 歧义身份/顺序 | 同一 ordinal 两个不同 PatternId；FrameId 相同 hash 不同；相机序列与 StereoModel 不一致 | 在任何 native 调用前比较身份、revision、ordinal、方向和 epoch | `Rejected` + `R3D-002 IdentityMismatch` 或 `R3D-004 DuplicateFrame` | 重新冻结输入；不按到达顺序、不按文件名、不按 `latest` 选择 | 拒绝日志包含冲突双方的稳定 ID/hash；无部分 native 结果 |
| 单位/坐标歧义 | 一方向 `Millimeter`，另一方向缺单位或 frame 不同；Z 范围非有限 | 校验单位枚举、源坐标和 IM-033 已发布快照作用域 → `ApplyPublishedTransform` 一次（目标坐标已一致时显式声明无需变换）→ 再校验范围 | `R3D-006 UnitOrCoordinateMismatch`、`R3D-018 PublishedTransformUnavailable` 或 `R3D-019 TransformScopeMismatch`；不执行重建/融合 | 上游/IM-033 发布匹配快照；IM-032 不猜比例、不自行估计或重复转换 | 负坐标合法；米/英寸不能静默当毫米；变换来源、revision 和应用次数进入 provenance |
| 噪声/低对比/饱和 | 输入质量报告显示饱和、低调制度、噪声或无 correspondence；阈值来自质量 Profile | 输入质量门 → 仍按固定路线计算可观测域 → 质量门分类 | `Partial`、`NotObservable` 或 `NotQualified`；无效原因分别标记 `Saturated`/`NoCorrespondence` | 由宿主按同一采集 Profile 受控重采或改用已资格 setup；模块不调设备 | 缺失点不填零；质量失败不能生成 `QualifiedCandidate` |
| 遮挡/退化表面 | 镜面、多路径、黑表面、局部遮挡、极小重叠 | 保留原支持域 → 固定路线计算可观测域 → 按支持/残差/方向差异分区 | 观测域、遮挡域、冲突域分开；必要时 `R3D-008 QualityInsufficient` | 不提供运行时替代路线；提交新采集/Profile revision 后可建立新请求；不以 AI/训练结果替代物理可观测性 | 首发不补洞、不插值，退化原因和来源可回查 |
| 超大输入 | 达到像素/帧/方向/点数或 `MaxNativeBytes` 上限；参数来自 Profile 和请求预算 | 预估 native/托管峰值 → 分配前预算门 → 固定全尺寸 ROI 域（首发不自动 tile） | 超限返回 `R3D-010 ResourceLimitExceeded`；不隐式降采样 | 宿主缩小 ROI/分批创建新操作；分片结果必须带分片边界和来源，模块不自动拼业务事实 | 超限在分配前可复现；不发生 OOM 后才报告；分片缺口可见 |
| 高并发/队列背压 | 多宿主同时提交，向同一忙实例提交；宿主独立管理进程资源限额 | Admission → 每实例固定 1 个操作 → 忙时短拒绝，无内部队列 → 独立租约 | R3D-022 BusyOrClosing，不接纳执行；不共享可变模型 | 宿主退避并重试新计算；公平性和取消按 operation 隔离 | A 取消不影响 B；队列长度、等待时间和拒绝原因可观测；无无界增长 |
| 取消/超时/native 排空 | 取消发生在解码、重建或融合中；Deadline 早于 `Parameters.Timeout` | 发布 `CancelRequested` → 停止未开始阶段 → 等 native 返回 → `Drained` → 释放租约 → ResourcesReleased → 唯一终态 | `Cancelled` 或 `TimedOut`；已有部分候选可保留但取消操作终态仍 Cancelled，排空未知为 DrainUnknown | `NativeDrainFailed` 时废弃实例并隔离进程；不复用句柄、不重试同 CalculationId | `Drained` 前不释放 HImage/model；迟到回调不能产生新结果；DrainUnknown 无终态/资源归还，真正退出后终态只出现一次 |
| 持久化/版本修订 | 宿主保存结果、输入引用、Profile/标定 hash、模块/Contract 版本；随后读取新版本 | 模块只生成不可变结果/证据引用 → 宿主调用已采纳存储Owner的公开提交契约（不在本模块规定文件事务算法） → 读取时校验 hash/版本/单位 | 读取成功返回原字节和 provenance；不兼容为 `R3D-015 VersionIncompatible` 或 `R3D-016 Unknown` | 读取旧结果用显式兼容层；重新计算生成新 CalculationId，不覆盖旧结果 | 断电写入不会出现半个成功文件；版本/单位变化不会静默解析 |
| 升级/回退 | 在途操作、旧结果和新 DLL 并存；包清单/哈希不同 | 宿主停止新派发（非模块Quiesce API） → 等待或隔离在途 → 备份包/配置 → 验证新包 → 切换；失败恢复旧包 | 模块只报告执行结果；升级编排由宿主负责；新包不兼容返回 `R3D-015` | 回退到旧 DLL 和兼容配置；历史结果保持旧版本；禁止重发设备动作 | 升级中断后旧结果可读；新旧结果差异有 Profile/版本解释；无双 Owner |
| 无 UI 调用 | 控制台/Replay 宿主注入适配器、诊断、Clock 和取消令牌 | `Validate` → `Reconstruct`/`ReconstructAsync` → 等 `Drained` → 释放实例 | 只返回类型化结果/错误/事件；无窗口初始化 | 失败按错误表恢复；核心不依赖 Dispatcher | 在无 WPF 进程中可运行；同步入口不阻塞 UI 语义、不隐藏线程 |
| 可选 UI | UI 只消费进度、不可变结果和错误键，语言/主题由宿主注入 | Validate → Run → 取消 → 显示排空 → 结果/错误投影 | UI 可显示每方向/融合/原因域；不含 Accept/Release/设备命令 | UI 关闭先取消并等待 `Drained`；异常只影响投影 | 关闭/切语/切换视图不改计算事实；三语文字不改变数值/来源 |
| 第二消费者与长期运行 | 结构光工具、3D AOI、表面实验使用不同适配器和 Profile；连续运行数小时/数千次 | 每次操作独立 snapshot/lease → 周期性统计 → 失败隔离 → 结束时释放 | 结果语义一致；诊断含操作计数、峰值、句柄活跃数、失败率 | 达到泄漏/错误预算时停止接收新操作并隔离实例；不热重载可变模型 | 长稳后 native/托管/GPU 活跃数回到基线；无跨宿主状态污染；重启可从快照回放 |

### B.2 路线、备用、恢复和训练边界

| 能力 | 主路线 | 备用路线与触发 | 恢复条件 | 明确不支持 |
|---|---|---|---|---|
| 结构光 | `create_structured_light_model("3d_reconstruction")` → 设置已批准参数 → `decode_structured_light_pattern` → `reconstruct_surface_structured_light` | 单次请求使用 PatternProfile 冻结的 `pattern_orientation`；无运行时替代模式 | 新 Operation 使用完整输入快照；旧 native model 排空后才释放 | 缺帧、模型类型错、标定失效或模式不匹配直接拒绝；不切换 `vertical`/`both`、不挑帧、不跨 attempt 拼图案、不用训练模型兜底 |
| 多视立体 | 仅使用已资格 StereoModel 固定的 `surface_fusion` 路线 | 无运行时备用路线 | 重新校验 image-pair、bounding box、模型 revision；新的 CalculationId | `surface_pairwise` 不属于首发；`fuse_object_model_3d` 不代替缺失的 stereo 标定/配对；未经资格的自动参数搜索被拒绝 |
| 已给高度/点云 | `ISurfaceInputAdapter` 验证单位、源坐标、mask、来源；方向变换仅在独立 ApplyPublishedTransform 阶段消费 IM-033 快照；若已在目标坐标则显式声明无需变换 | 导入器仅做格式适配；非目标坐标由独立变换阶段应用已发布快照一次，不回退到结构光/立体重建 | 缺快照/未发布/作用域不匹配返回 `R3D-018`/`R3D-019`；上游/IM-033 提供匹配快照；IM-032 不自行转换、估计或重复应用 | 从显示网格反推量测、从 Z=0 推断有效点 |
| 方向融合 | 检查方向数、源/目标坐标和已发布快照 → 逐方向质量门 → 只有完成且通过软件覆盖门的方向数达到 Profile 最小贡献值才融合共同支持元素 | 少于最小值则保留 per-direction，`Fused=null` 并写入 `FusionIssue`；达到方向数后逐元素应用支持/冲突门，局部不足保留无效原因 | 新请求须提供新的输入/Profile revision 和匹配快照；不可在原 operation 降低门槛或重新估计变换 | 置信度加权、少数方向强行凑数、运行时降低最小值、最高分覆盖冲突、插值/补洞、调用 `FuseObjectModel3d` |
| 训练/AI | 本模块无训练、模型拟合、在线学习或 AI 推理入口；算法参数来自版本化 Profile/标定 | 不提供 AI fallback。AI 若由宿主另行运行，只能作为候选/解释，不能改写本模块输入、结果或状态 | 训练/模型变更必须在模块外完成离线评价、版本 hash 和人工批准，再形成新 Profile | 用训练结果填无效域、绕过质量 Gate、自动改变融合或质量放行 |

### B.3 第二轮复审结论

- 空输入/歧义身份/可预估超限资源在HALCON前拒绝；零成功方向只在实际运行后能确认，排空后拒绝；部分成功仅在显式策略下成立，并且不改变完整性语义。融合成功数低于 `MinContributingDirections` 时不生成 Fused，不降低门槛，保留 per-direction 与有类型原因。
- 26.05 原文已核到结构光、立体、变换和有效域路线；ImageLibDotNet.cv2 可调用全部算子，不重复核验封装存在性。
- 首发多视立体固定 `surface_fusion`，结构光模式由单一 Profile 固定，方向融合仅在共同支持域作等权平均；`surface_pairwise`、运行时切换 `vertical`/`both` 和 `fuse_object_model_3d` 均不是首发 fallback。
- 模块不拥有持久化、升级编排、训练、设备控制或质量放行；这些场景只定义宿主交接、证据和恢复约束。
- 长期运行、高并发和排空失败均以实例隔离/停止接收为恢复边界，不依赖静态状态或隐式热修复。
- Owner 边界已裁决：IM-033 唯一负责方向变换估计、资格化、发布和撤回；IM-032 只消费已发布不可变快照一次，并记录 provenance。


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

## 附录 A：Module API Contract v0.2（唯一代码形状与逐切片六项门）

§4/§5/§8/§10 中公开声明共同构成本模块唯一 API v0.2；C# BCL 引用 `System`、`System.Collections.Generic`、`System.Threading`、`System.Threading.Tasks`。版本由旧候选0.1更新，修正 required 参数位于 optional 后和非常量 struct 默认值的不可编译形状；旧候选不是已经投产的程序集，不宣称二进制兼容。所有公开字段类型已在本指导定义，禁止实现者到历史 PKG/脚本另找 DTO。平台 Schema/发布资产信封仍是公开映射门，不改本模块状态机；批准职责边界与 IM-033/IM-065 Owner 不变。

### A.1 工程、允许路径与独立包

根命名空间 `Asun.Modules.Reconstruction3D`，以下是后续实施唯一落点，当前文档任务不创建工程：

| 切片 | 代码工程 / namespace | 测试工程（相对仓库根） |
|---|---|---|
| Core：值验证/单位/来源/分桶等权融合/参数建议/执行协调 | `src/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.Core/Asun.Modules.Reconstruction3D.Core.csproj`；根 namespace | `tests/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.Core.Tests/Asun.Modules.Reconstruction3D.Core.Tests.csproj` |
| Simulator（六项规格已独立接收）：synthetic 回执/阻塞排空/租约与故障注入 | `src/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.Simulator/Asun.Modules.Reconstruction3D.Simulator.csproj`；`Asun.Modules.Reconstruction3D.Simulation`；§13.4唯一factory/脚本 | `tests/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.Simulator.Tests/Asun.Modules.Reconstruction3D.Simulator.Tests.csproj`；§13.7 S01～S03与双发布包Host，不引用Core.Tests |
| AsunImage Adapter：三种输入/一次变换与真实资源 | `src/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.AsunImage/Asun.Modules.Reconstruction3D.AsunImage.csproj`；`.Adapters` | `tests/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.AsunImage.Tests/Asun.Modules.Reconstruction3D.AsunImage.Tests.csproj` |
| 可选 WPF控件 | `src/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.Wpf/Asun.Modules.Reconstruction3D.Wpf.csproj`；`.Wpf` | `tests/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.Wpf.Tests/Asun.Modules.Reconstruction3D.Wpf.Tests.csproj` |
| 无UI BCL Exe TestHost与Benchmark | `tests/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.TestHost/Asun.Modules.Reconstruction3D.TestHost.csproj`；`.TestHost` | Host用于两个消费者/§13/§14，不作为产品 Shell |

Core/Simulator、Core.Tests/Simulator.Tests/TestHost 均规划target net10.0，无WPF/SDK/native引用；上述验证工程全部Microsoft.NET.Sdk、OutputType=Exe，仅引用受测工程和BCL。已接收Core.Tests/TestHost仍仅引用Core/BCL，内部stub不发布；Simulator只引用Core，其Simulator.Tests仅引用Simulator/Core/BCL、双Host直接用§13.6发布入口，不引Core.Tests。Simulator规格已独立接收，仍不成为Core编译依赖。Adapter/WPF及其适用验证target net10.0-windows，WPF仅在Wpf及其专用验证工程启用。端口值类型与公开契约随Core发行，不机械分拆无消费方的空Contract DLL。包可单独build/publish；纯Core验证只用下方dotnet run，真实Adapter/WPF另绑定适用验证；WPF是可选依赖，Core包加载不初始化窗口。AsunImage引用项目现有程序集，DevExpress用本机25.2.3；不安装、另接halcondotnet.dll、NuGet替换、授权核验或扫描内部。

§8.1的Joint组合软件Host在上述AsunImage.Tests的Host集成目录复用原两Host角色；§8.2真实Joint工厂在本模块AsunImage DLL显式引用CAL公共Joint/Core，Surface桥同DLL显式引用SD Core，适用验证工程引用这些公开合同，不引用CAL测试工程、不搬其私有Build/codec/资格逻辑，不扩Core/Simulator/普通TestHost编译依赖。测试只加载公开托管类型/本地spy验证绑定和所有权，真正AsunImage调用另分适用case；本轮不创建或修改工程。后续获代码授权并建成原工程后，该软件suite入口为`dotnet run --project tests/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.AsunImage.Tests/Asun.Modules.Reconstruction3D.AsunImage.Tests.csproj -c Release -- --case joint-bindings`，必须包含JRC01～06全部子例并按§8.1.3有限退出，不以无native软件通过提升Adapter资格。

后续每切片授权后只可写表内本模块相应工程/测试路径；其它模块、平台Shell/ViewModel/产品库表、机台SDK、共享Contract/页面、客户项目、tools、skill、原始参考与AsunImage内部全部禁止。本文修订权限仅该 DEVELOPMENT-GUIDE.md，不因表中路径成为本轮代码授权。没有.git的权威代码快照门由主任务处理，不能伪称当前HEAD。

### A.2 最小执行与完整能力接收

Core既有接收范围包括§4值验证及0.2.5角色/诊断增量，§7.3共同支持网格/等权融合数学，§5.3/§7.5有明确无参创建入口的参数建议，§5/§8/§9协调、深复制/预算/一次应用分支/幂等拒绝/事件查询；实际视觉变换经公开适配端口，纯Core不另写HALCON算法。Core验收仅需测试工程内部stub，既有接收范围不撤回。Simulator按§13.4～§13.7含已接收D夹具/诊断增量实现相同端口、唯一公开factory/脚本/clock/gate和查询/资源闭包、显式synthetic provenance；只模拟明示观测与恒等变换，非真实算法，不默认Qualified、不污染生产资产，规格已独立接收，实际代码任务另派。§7.6的decode-only C1/S1六项规格已由主控接收为`ModuleCoreImplementationReady`，使用原Core/Simulator/Tests的Decoding子目录及原build/run命令，不新建DLL/工程。Adapter覆盖结构光/立体/表面导入/变换全能力及本节真实decode-only路线，WPF覆盖全部投影/离线建议调用；不得用“首片缩小”为理由省去模块其余规格。

后续命令按对应切片获准且实际工程创建后执行，例：`dotnet build src/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.Core/Asun.Modules.Reconstruction3D.Core.csproj -c Release`；`dotnet run --project tests/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.Core.Tests/Asun.Modules.Reconstruction3D.Core.Tests.csproj -c Release`。Core TestHost用 `dotnet run --project tests/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.TestHost/Asun.Modules.Reconstruction3D.TestHost.csproj -c Release -- --profile diagnostic-F0`，仅用Core/内部stub。Simulator规格已独立接收，代码任务另行获授权并创建工程后执行 `dotnet build src/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.Simulator/Asun.Modules.Reconstruction3D.Simulator.csproj -c Release` 和 `dotnet run --project tests/Modules/reconstruction-3d/Asun.Modules.Reconstruction3D.Simulator.Tests/Asun.Modules.Reconstruction3D.Simulator.Tests.csproj -c Release`；当前不创建或实施该包。dotnet test不执行这些Exe，不能以无报错冒充验证；Simulator case/suite/外层进程10/120/180s及非零退出按§13.7，其余按对应§13规则。其余工程使用上表同样完整路径，不跑无关全仓测试。测试必须来自§13断言，不能复制实现逻辑作为oracle；视觉比较使用正式真值与本地算子资料，不让mock证明精度。

### A.3 DEV-GOV-010 §3.1 六项准备判定

0.2.5角色/诊断增量六项定位：职责/消费者§4.2.2/4.4.1、公开DTO/单位/状态/预算/资源Owner同两节、两无UI Host§13.6.1、异常/取消/重复/关闭/验证§13.7.1、Benchmark沿§14并区分新增copy/hash/persistence负载、允许工程/完整命令沿A.1/A.2。主控2026-10-11已完整回读接收为Core/Simulator的ModuleCoreImplementationReady软件增量，八份编码独立重建一致；不提升Adapter/WPF/产品/现场门。新增decode-only C1/S1六项定位见§7.6.7，主控同日已独立接收为`ModuleCoreImplementationReady`；A1路线/公开工厂内容限定接收，真实Both Golden/native/Envelope/消费者封存及运行资格仍`PreparationIncomplete / NotReady`。

| 条件 | 本文可直接审查的落点 | 剩余影响 |
|---|---|---|
| 1 职责/依赖/第二消费者 | §1/§2、§11/§17，IM-033唯一变换Owner；无设备/产品事实写入 | Core规格已由主控内容接收；真实第二消费者运行属于Integration |
| 2 精确API/单位/状态/资源/版本 | §4/§5/§8/§9/§16，candidate→模块值契约；错误+查询/Unknown | Core值形状已明确；跨模块发布/Schema映射只阻断Integration，具体C#封送歧义仅Adapter |
| 3 无UI最小Host/端口 | §5.1.1/§8/§11，factory前预留强持槽、finally后最终退出码、三原Task观察；§5.3建议无参入口 | Core已接收；Simulator公开构造/双Host/五Task根Owner在§13.4～13.6已独立接收；真实视觉适配与客户资产只阻断Adapter |
| 4 失败/并发/取消/关闭/回退与测试 | §6/§9/§12/§13、B.1，Partial事实与Cancelled终态分开 | 测试计划已可执行，尚未编写或运行，不能宣称通过 |
| 5 BenchmarkProfile | §7.4/§14，全链与资源/删失/目标来源 | Core诊断可执行；时延/精度/内存正式目标待消费者Profile，真实性能NotEvaluated |
| 6 唯一工程/路径/调用/后续门 | §1.3/A.1/A.2，net10分层，允许/禁止路径 | Core规格切片已接收；本轮完整指导收口；没有代码派发或实施证据 |

Core：2026-10-10主控已完整内容复核并接收六项规格，状态 `ModuleCoreImplementationReady`；范围仅值校验、分桶等权融合、参数建议、执行协调及已冻结端口下测试stub/TestHost，不包含可发布Simulator、HALCON/Adapter、WPF、集成或现场。Simulator：同日主控已独立接收§13.4～13.7/A.1～A.3六项规格为 `ModuleCoreImplementationReady`，范围仅发布模拟包的明示值/端口/脚本/控制/资源Owner和两个无UI Host；不授真实算法、HALCON/标定、WPF、产品集成或现场资格，不把测试stub当发布实现。实际工程/编译/运行/性能均未执行。Adapter：真实样本、计量/TimingProfile、物理geometry/阈值、native内存envelope 与故障验证阻断对应资格；算子存在性不阻断。WPF：25.2官方API依据已记录，真实1920×1080/UIA/DPI/三语/响应验证未执行；平台集成：跨模块发布/Schema映射和事实Owner采纳待关闭。全模块仍 `DesignReview/Prep`；接收只证明对应切片规格准备，不表示已实现、测试通过或生产就绪。

Simulator独立六项准备位置（2026-10-10主控内容接收，独立于Core接收）：

| 条件 | 本文唯一规格位置 | 状态/后续边界 |
|---|---|---|
| 1 职责/依赖/第二消费者 | §13.4纯BCL合成端口职责与非目标；§13.6 A/B直接引用发布包 | 两消费者真实调用形状已给；不控制设备/发布质量事实 |
| 2 公开API/单位/状态/资源/版本 | §13.4全部DTO/factory/有效域/版本与synthetic来源；§13.5clock/gate/Query/单飞/lease | 数值仍mm、Unknown不释放、不可Qualified；不猜HALCON/平台信封 |
| 3 无UI最小Host | §13.6 factory/Request/Ports双Host、根槽/五原Task/engine失败路径 | 不引用Core.Tests/DI/WPF；有限异常finally/接收确认原Owner保留 |
| 4 异常/取消/重复/关闭/测试 | §13.5步骤及资源闭包；§13.7 S01～03与10/120/180s | 正常/拒绝/partial/失败/取消/迟到/DrainUnknown/释放控制可判定；尚未运行 |
| 5 BenchmarkProfile | §13.7末段与§14唯一统计口径 | 软件合成负载/资源计数，虚拟时间不当性能；目标缺失NotEvaluated |
| 6 工程/路径/调用/禁止范围 | A.1/A.2发布Simulator及唯一BCL Exe完整命令；§13.6直接构造 | 六项规格已独立接收；本轮补全指导而非只同步状态，代码任务另派，不扩到Adapter/WPF/现场 |
