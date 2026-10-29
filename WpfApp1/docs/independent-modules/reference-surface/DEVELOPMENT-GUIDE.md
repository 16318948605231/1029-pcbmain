# 参考面与板弯补偿（Reference Surface）开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`RS-C1, RS-C2, RS-C3, RS-C4`

- 模块 ID：`IM-035`
- 来源：`PKG-029`
- 文档状态：`DesignReview / Prep`
- 核心切片状态：`RS-C1 / RS-C2 / RS-C3 / RS-C4 = ModuleCoreImplementationReady`（主控2026-10-10接收，RS-C4经0.3.2-prep窄复核恢复，仅规格准备）；`RS-W1 = PreparationIncomplete / NotReady`（W1规格内容已主控接收，运行/产品资格未执行）；`RS-I1 = PreparationIncomplete`。
- 文档版本：`0.5.0-prep`
- 目标运行时：C# / .NET 10；首发算法为固定纯托管数值实现；HALCON 26.05 算子资料用于路线比较与边界核验
- 规划消费者：高度计量、翘曲分析、体积计量、通用表面计量
- 当前结论：2026-10-11本原会话已核当前架构及全部批准能力，完成§18输入消费/上游兼容/双STA补充和§19全范围自审收口；可决定的软件设计欠账已闭合，文档准备完成，不等待总控内容审核。RS-C1～C4原ModuleCoreImplementationReady规格保持；W1仍PreparationIncomplete / NotReady，I1原门保持；模块仍DesignReview / Prep，真实C#/HALCON/WPF/Golden/性能/计量与现场均未验，不授产品或生产资格。

本文是模块唯一实施指导。正式产品ContractId/SchemaId/State/Owner、客户Profile发布和真实测试资产仍由相应Owner串行采纳；模块Core的公开API/值身份/算法是本文v0.1评审基线，逐切片接收条件见附录A。不能因平台Schema未定另造平行Core DTO，也不能因本指导有API就自动授予整模块实现或生产准入。

权威关系：架构边界遵循 [`INDEPENDENT-MODULE-ARCHITECTURE.md`](../INDEPENDENT-MODULE-ARCHITECTURE.md)；历史包职责映射见 [`PKG-029_ReferenceSurface.md`](../../shared-modules/packages/PKG-029_ReferenceSurface.md)；视觉/AsunImage边界见 [`DEV-VIS-020`](../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision%20Contract与AsunImage边界开发指导.md)；三维消费场景/历史方法映射见 [`DEV-VIS-028`](../../shared-modules/guidance/03-vision/DEV-VIS-028_3D对象模型、配准与表面分析开发指导.md)；计量消费边界见 [`DEV-MET-031`](../../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md)。参考面实施算法/API/支撑资格只在本文；旧PKG/专业参考面段落不得并列规定另一实施路线或工程根，由主控串行收口迁移映射。专业指导继续拥有其领域事实/工艺/计量语义，本模块不复制产品Schema或质量判定。

## 1. 目的与边界

### 1.1 模块负责的事实

模块接收一个带修订和坐标单位的三维表面快照，在调用方声明的候选参考域、排除域和独立检查域内完成：

1. 输入一致性、有限性、单位、坐标系和域关系校验。
2. 参考模型估计：首批支持正交平面（P），限定的一阶高度回归（H）和固定六项二阶高度曲面（Q）。
3. 稳健候选选择、实际重拟合集、最终门内集、原始参考候选全体的残差重算。
4. 支撑覆盖、空间展开、外推距离、孔洞/缺口、独立检查和局部适用性评估。
5. 在不改写原始表面快照的前提下，提供有符号法向距离和指定高度轴距离的补偿评估。
6. 返回不可变结果、来源索引、排除原因、方法参数、版本和可观测性数据。

### 1.2 明确禁止

- 不决定产品缺陷、质量放行、人工复判、工单状态或客户协议。
- 不决定哪个物理表面“就是板面”；调用方必须声明物理参考含义并提供候选域。
- 不拥有目标关联、流程顺序、配方发布、持久化事实、报告和设备动作。
- 不删除或覆盖原始高度、点云、有效掩码、标定资产或历史结果。
- 不用凸包、最低点、内点 RMS 或拟合成功替代支撑资格。
- 不自动补洞、自动选阶、无限放宽离群阈值或把 Q 作为 P 失败后的隐式回退。
- 不把 HALCON `HObject`、`HObjectModel3D`、原生句柄或内部索引泄漏到核心契约/UI。
- 不以 UI 草稿、缓存命中、AI 建议或异步 ACK 产生生产事实。
- 不编排相机/FOV 采集、跨 FOV 拼接、2D 必检域归集或等待邻域帧；没有高度依赖的 2D 消费者继续由其原 Owner 执行，不能因参考面缺失而被本模块阻塞。

调用方拥有目标关联、用途资格、工艺解释、最终比较、保存/提交、质量决策以及任何设备副作用。未知、拒识、取消、超时和失败必须沿调用方原状态机保留，不能压成 PASS/OK。

Core事实Owner是本模块维护者：模型、选择集合、残差、支撑/逐点有效性、算法与值身份规范只能经本指导版本改变。宿主/上游Owner拥有采集/标定/物理域/连续性证据与Profile采纳，提供的输入不因拟合成功获得真实性/质量证明；存储Owner只保存内容不改数值，语言/UI只投影。当前永久会话为模块索引登记的`01a10307-0454-7f33-befa-cb9ada86e3b4`，无派生Owner或平行模块会话。

### 1.3 本模块实现文件绑定

首个纯 Core 切片绑定仓库相对路径 `src/Modules/reference-surface/Asun.Modules.ReferenceSurface.Core/Asun.Modules.ReferenceSurface.Core.csproj`、测试工程 `tests/Modules/reference-surface/Asun.Modules.ReferenceSurface.Core.Tests/Asun.Modules.ReferenceSurface.Core.Tests.csproj`，根命名空间固定为 `Asun.Modules.ReferenceSurface`。工程尚未创建，本指导不以文档修订代替代码创建。该切片只允许新增/修改上述 Core 与测试工程目录中的文件；WPF、宿主集成和发布配置须分别通过自己的实现准入。不得修改其他模块、产品项目、AsunImage 内部或只读参考快照。

Core 工程固定 `Microsoft.NET.Sdk / net10.0 / Nullable=enable / ImplicitUsings=enable` 类库；唯一测试工程固定同 SDK/TFM、`OutputType=Exe`，仅 ProjectReference 到上述 Core 和 .NET BCL，无 PackageReference、无待选测试框架。同一 Exe 的 `Program.cs` 提供 §9 两种宿主模式和 §12 全部确定性断言；不另建第三个 Host 工程、空产品 Shell 或复制算法。以下命令在仓库根执行，是真正实现阶段的验证命令，本次文档修订未执行：

```powershell
dotnet build src/Modules/reference-surface/Asun.Modules.ReferenceSurface.Core/Asun.Modules.ReferenceSurface.Core.csproj -c Release
dotnet run --project tests/Modules/reference-surface/Asun.Modules.ReferenceSurface.Core.Tests/Asun.Modules.ReferenceSurface.Core.Tests.csproj -c Release
```

测试入口任一失败、超时、必需项跳过或未排空均返回非零并列出用例ID；全体断言完成才返回0。`dotnet test`不执行该Exe，不能以空执行冒充通过。每case总期限10 s（包括业务、故障注入、cleanup与恢复），suite总期限120 s，外层隔离测试进程期限180 s；故意迟滞来源观察1 s也属于该case总期限。测试控制点用有限异步闩锁/内部TimeProvider，生产Factory固定TimeProvider.System，不向公开API泄漏测试时钟。suite到期停止新case并处理已持Owner；未确认归还记录失败且不清槽。外层180 s到期由执行者停止该隔离测试进程并记录未排空，不能据进程退出证明资源释放或输出成功，不终止用户宿主。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.ReferenceSurface.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Modules.ReferenceSurface.Wpf`（可选控件）可引用 WPF/DevExpress，且 Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。§1.3 首片（纯 BCL Core，无 HALCON/AsunImage 适配器）是这条门禁的天然验证面。

**Blazor/Web 宿主中的参考面结果展示**：Web 端需要"展示参考面拟合质量、残差分布、支撑覆盖、孔洞缺口与补偿评估"时，服务端调用 Core 取得不可变结果，再投影到浏览器。约束：
- 浏览器端只渲染标记与数值，不重新拟合参考面、不自行推断凸包或最低点、不改写 `ApplicabilityStatus`
- §1.2 的"不用凸包、最低点、内点 RMS 或拟合成功替代支撑资格"在 Web 投影中同样成立：前端不得以"拟合已完成"显示为可用参考面
- `ReleasedTransformSnapshot`（由 `registration-3d` 发布）被参考面模块消费时，Web 端的坐标展示须由服务端算好，浏览器只渲染已变换后的坐标

**AI 推理 Tiling 适配**：本模块的参考面补偿评估（法向距离/高度轴距离）可作为 `ai-inference` 3D 异常检测的预处理输入（去掉板翘曲基线后的高度偏差），但本模块不参与推理分块编排。适配约束：
- 补偿后高度场由本模块输出，再由 `surface-data` 或 `image-frame` 模块按 tile 粒度切出供推理使用；本模块不实现 `RequestTileAsync`，不持有推理 tile 租约
- 三态仲裁对"补偿后高度超阈值"的判定只作观察，不覆写本模块已发布的参考面候选事实

**HALCON 备选交叉验证适用性（参考面链）**：本模块已有 Open3D oracle（`PointCloudSegmentation.cpp`/`PointCloud.cpp`，见 §18 已读证据）。约束：
- H（一阶高度回归）、Q（二阶高度曲面）、P（正交平面）三种参考面估计在 HALCON 路线与托管参照路线上按**同一 Golden 数据集**双跑：拟合系数（alpha/beta/gamma，Q 另有 delta/epsilon/zeta）、内点集合（点数与坐标）、残差与支撑覆盖逐项比对，差值超容差即 CI 失败
- **已知的必然差异，不得抹平**：
  - HALCON `fit_surface_first_order`/`fit_surface_second_order` 的输入是 Region/Image；托管参照直接消费 XYZ 样本，两者在区域格式、样本排序与离群阈值（`clipping_factor`）上的处理方式不同。双跑须对同一组 XYZ 点冻结区域格式，确保两路输入等价，否则差异不可区分为"算法差异"还是"输入差异"
  - `fit_primitives_object_model_3d`（P 路线）的残差定义已核 HALCON 26.05 资料（`fit_primitives_object_model_3d.html` SHA-256 `ae7ac101...`）：`primitive_rms` 是 quadratic residual，非标准均方根，见 §18 已读证据；双跑两路须按相同残差定义比对
  - 稳健估计（Huber/Tukey 权重）的最终内点集在两路实现中可能不完全相同；双跑门禁只对**内点数量**（±1%）与**拟合系数**（绝对容差按物理单位冻结）设门禁，不对每个点的 inlier/outlier 标志设逐点门禁
- **Open3D oracle 在本模块的具体落点**：
  - `PointCloudSegmentation.cpp`（SHA-256 `44487a05...`）的 `SegmentPlane`/`EvaluateRANSACBasedOnDistance`：定义了"内点 RMSE = sqrt(Σd²/n)"（源码第 102 行），用于确认"本模块残差定义需要独立验证"这条约束；`GetPlaneFromPoints` 以最大余子式法向，非最小特征向量 TLS，**不等同** HALCON `fit_primitives_object_model_3d` 的 least_squares，不得用 Open3D 值替换 HALCON 值
  - `PointCloud.cpp`（SHA-256 `9d31ff09...`）的 `SegmentPlane/Deterministic`（`tests/geometry/PointCloud.cpp` SHA-256 `b8041cb7...`）：固定种子下可重复，支撑本模块"相同输入产生相同候选集"这条不变量（与 §1.1 第 6 条"提供可回放所需的操作状态"对齐）
  - `SegmentPlane` 的 `probability` 参数（默认 `0.99999999`）控制提前退出，不保证 iteration_count 固定；本模块不依赖固定迭代次数，支撑"不以单次拟合成功替代支撑资格"
- HALCON 仍是生产路线；Open3D 仅作语义参照，不引入生产依赖

## 2. 术语与数据流

| 术语 | 约定 |
|---|---|
| SurfaceSnapshot | 某次采集或回放的不可变三维表面快照，带 `SurfaceId`、`Revision`、单位、坐标系和内容哈希。 |
| ReferenceDomain | 允许作为参考候选的域；不等于实际最终拟合集。 |
| ExclusionDomain | 调用方声明的先验排除域、无效域或不允许借用的物理断面。 |
| IndependentCheckDomain | 不参与拟合、只用于独立检查的域。 |
| TargetDomain | 下游请求希望评估的域；模块只返回适用性，不建立业务目标关联。 |
| SupportSet | 经过输入校验、域裁切和方法筛选后实际用于拟合的点集合。 |
| Applicability | 对声明目标域的支撑、覆盖、外推和检查证据；不是质量判定。 |
| Compensation | 相对于参考模型的派生距离；原始表面和派生距离同时保留。 |

标准数据流：

```text
SurfaceSnapshot + 域/方法/Profile
        -> 校验与只读租约
        -> 域裁切、来源索引保留、排除分类
        -> 候选拟合 -> 稳健筛选 -> 实际重拟合
        -> 残差/支撑/独立检查/适用域
        -> ReferenceSurfaceResult（不可变）
        -> 调用方按用途评估 Compensation
```

## 3. 分层与依赖

```text
应用/工作流/计量宿主
  -> IReferenceSurfaceEngine（本模块公开契约）
  -> ReferenceSurface.Core（校验、固定数值算法、支撑资格和评估）
  -> 不可变平台值类型与只读表面快照
```

首发 P/H/Q 在 Core 内各只有一条已固定的确定性纯托管数值路线，不注入算法后端，不按运行环境切换。HALCON 26.05 Region/Image 拟合算子不直接接收任意 XYZ，primitive 不等同等权 TLS；但矩阵算子可以表达同样的协方差/设计矩阵，已核实的路线比较见 §17，不能把前两项局限扩大为 HALCON 能力缺口。算法替换先修订指导、算法版本和同输入验证门；不新增未授权后端。首发 Core 只依赖 .NET10 BCL（含 Immutable 集合、BigInteger 和 TimeProvider），§4 值类型在本模块命名空间；公共平台数据由宿主显式映射，不依赖未冻结公共 DTO/程序集。禁止产品 ViewModel、私有数据库、制程规则、设备 SDK、隐藏窗口与全局可变状态。

### 3.1 HALCON 与 AsunImage 核对结果

核对算子边界时以仓库 `halcon算子手册/operators` 和目标版本官方 Reference Manual 为准，记录算子版本、输入形状、参数单位及线程属性。该核对不构成本模块实现路线；本模块首发纯 Core 不调用这些算子，也不创建其句柄。当前已定位的资料包括：

- `fit_surface_first_order.html`、`fit_surface_second_order.html`：H/Q 候选路线；
- `fit_primitives_object_model_3d.html`、`gen_plane_object_model_3d.html`：三维 primitive/平面候选；
- `sample_object_model_3d.html`、`select_points_object_model_3d.html`、`surface_normals_object_model_3d.html`：采样、筛选、法向；
- `distance_object_model_3d.html`、`volume_object_model_3d_relative_to_plane.html`：距离/体积下游能力，不能反向改变本模块职责。

HALCON 26.05 页面给出的关键形状已核对：`fit_surface_first_order` 与 `fit_surface_second_order` 以 `regions,image,algorithm,iterations,clipping_factor` 为输入，并返回 alpha/beta/gamma（Q 另有 delta/epsilon/zeta）；`fit_primitives_object_model_3d` 接受 `ObjectModel3D,GenParamName,GenParamValue`；`sample_object_model_3d` 接受 `ObjectModel3D,Method,SamplingParam,GenParamName,GenParamValue`；`select_points_object_model_3d` 按 `Attrib,MinValue,MaxValue` 筛选；`volume_object_model_3d_relative_to_plane` 接受模型、平面、`Mode` 与 `UseFaceOrientation`。这些页面均标注 HALCON Operator Reference `26.05.0.0`。页面的参数形状不等于平台的单位、资格或生命周期语义。

历史 AsunControl 快照中的相关包装方法不属于本模块 Core 实现。它们只说明旧副本曾有相关封装，不能复制到本模块或推断为当前公共签名。

上述资料只用于确认边界和排除不匹配路线，不定义本模块算法实现。`fit_surface_first_order` 与 `fit_surface_second_order` 的输入是 Region/Image，不能直接替代本模块对 XYZ 样本的 H/Q 路线；`fit_primitives_object_model_3d` 不自动等同等权 TLS，HALCON 第四返回值也不能直接当作平台平面常数 `d`。`VolumeObjectModel3dRelativeToPlane` 只属于下游计量能力，不属于本模块。当前 Core 不含 HALCON/AsunImage 适配器，也不持有 native handle。

核心只接收平台值类型和 `ImmutableArray`，不持有 native handle 或依赖 HALCON/AsunImage。输入快照由宿主以只读值类型交接；算法工作集由本模块管理并在成功、取消、超时和异常路径完成清理。

## 4. 模块公开契约（Module API Contract v0.1）

本节代码形状采用 `namespace Asun.Modules.ReferenceSurface;`、`using System.Collections.Immutable;` 及 .NET 10 BCL。它定义本模块 API；平台 Schema/Owner 映射仍待采纳。下列声明是完整类型形状，调用示例为语义示例，未创建工程或编译验证。构造器不提供隐式生产参数。字符串为非空值；枚举未知值拒绝；集合 `IsDefault` 拒绝，空集合按各字段规则处理。宿主必须从稳定快照复制为真正不可变集合后调用，禁止把可变数组包装成只读接口后继续改写。

### 4.1 表面、域与连续性证据

```csharp
public enum LengthUnit { Meter, Millimeter, Micrometer }
public readonly record struct Length(double Value, LengthUnit Unit);
public readonly record struct Point3(double X, double Y, double Z, LengthUnit Unit);
public readonly record struct UnitVector3(double X, double Y, double Z);
public readonly record struct SurfacePoint(
    long SourceIndex, Point3 Position, bool IsValid, string? SourceValidityCode);
public sealed record ChartFrame(
    Point3 Origin, UnitVector3 U, UnitVector3 V, UnitVector3 HeightAxis);
public readonly record struct SupportCell(
    long CellId, long A, long B, long C, bool IsContinuous, string EvidenceReference);
public sealed record SurfaceSnapshot(
    string SurfaceId, ulong Revision, string CoordinateFrameId, LengthUnit Unit,
    ImmutableArray<SurfacePoint> Points, ImmutableArray<SupportCell> Cells,
    string ContentSha256, string AcquisitionReference, string CalibrationReference);
public sealed record SurfaceDomain(
    string DomainId, ulong SurfaceRevision,
    ImmutableArray<long> SourceIndices, ImmutableArray<long> CellIds,
    string DomainSha256);
```

所有坐标单位必须等于快照单位，内部转米。有效点NaN/Inf、重复/负来源索引、重复/负CellId、混合单位或坐标绝对值大于10,000 m拒绝。无效点也不得以非有限坐标充当几何：宿主提供实际有限平面位置及有限占位高度、IsValid=false；本模块不读其占位高度拟合。没有可知平面位置的样本不能宣称知道该缺测区，宿主不加单元，内部缺口保持Unknown。域索引必须存在；集合内重复拒绝，顺序不影响身份。R为参考候选、X先验排除、C独立检查、T声明目标；C不得与R0/X相交；T与R0相交须显式AcknowledgeTargetReferenceOverlap=true，标记非留出。X与R0/T可相交且X优先。每域SurfaceRevision必须等于快照修订，角色DomainId不同。Chart.Origin同样满足有限/同单位/10,000 m界限。

`Cells` 是上游提供的三角连续单元证据，不由本模块对离散点自动三角化。每个单元三个不同来源顶点必须存在；`IsContinuous=true` 必须带来源证据，不能跨物理断层、材料或缺测。域 `CellIds` 明确需要评估面积/支撑的区域；为空表示只有离散点，面积和连续插值证据未知。域单元的顶点须属于该域 `SourceIndices`。在请求 Chart 投影中，每个域内单元须非退化、内部不重叠，允许共享边/点；重复位置、重复三角、相交内部或自交拒绝 `RS-1004`。不同 R/T 域的投影可重合，不能据此认定同一物理层。拓扑检验用有界空间索引加精确 orientation 谓词；资源不足拒绝，不以凸包替代。拓扑来源、域和坐标必须纳入哈希。快照与输入内容身份由 §8.1 统一计算。

Chart 是显式输入，P/H/Q 均用它做支撑几何；H/Q 另用于高度回归。U/V/HeightAxis 有限且单位化，点积绝对值不超过 `64ε`，`U×V` 与 HeightAxis 同向且误差不超过 `64ε`，其中 `ε=2^-52`。不静默正交化或换轴。Chart 原点与快照同单位。`ReferenceDirection` 单位化用于 P 定向；H/Q 必须与 Chart.HeightAxis 同向（点积至少 `1-64ε`），避免轴差符号与法向语义混淆。

单位化的输入检验为稳定L2范数满足`abs(norm-1)<=64ε`；叉积误差同样用稳定L2，不以独立分量四舍五入代替。原方向/Chart保持请求值用于hash，不静默重新定向。每个参数比较包含等号；未给阈值的显式Unknown不借用工程默认。MinimumPlanarSpread范围单位为输入长度，其余数值稳定阈值为无量纲，转换米只作用于长度字段。

### 4.2 方法、参数和资格

```csharp
public enum ReferenceMethod { PlaneTls, HeightFirstOrder, HeightSecondOrder }
public enum HeightDistanceMode { SignedNormalDistance, SignedAxisHeight }
public enum RobustPolicyKind { None, FixedClipOnce }
public sealed record RobustPolicy(
    RobustPolicyKind Kind, double? ClipLimitInInputUnit,
    int MinimumRetainedPoints, double MaximumExcludedRatio);
public sealed record NumericalPolicy(
    double MinimumPlanarSpreadInInputUnit, double MinimumEigenGapRatio,
    double MaximumQrConditionOneNorm, double MinimumAxisNormalDot,
    double MaximumHeightGradient);
public sealed record SupportPolicy(
    int MinimumPoints, double? MinimumAreaRatio,
    double? MaximumTargetDistanceInInputUnit, double? MaximumGapInInputUnit,
    double MaximumExtrapolationRatio, bool AllowInterpolation,
    bool RequireIndependentCheck, int MinimumIndependentCheckPoints,
    double? MaximumCheckRmsInInputUnit,
    double? MaximumCheckP95InInputUnit, double? MaximumFitRmsInInputUnit);
public sealed record ReferenceMethodProfile(
    ReferenceMethod Method, string ProfileId, string ProfileRevision,
    RobustPolicy Robust, NumericalPolicy Numerical, SupportPolicy Support,
    string ParameterSha256);
public sealed record FrozenProfileReference(
    string ProfileId, string ProfileRevision, string ContentSha256);
public sealed record ResolvedReferenceProfile(
    FrozenProfileReference Reference, ReferenceMethodProfile Profile);
```

| 参数 | 约束/含义 | 来源与缺失行为 |
|---|---|---|
| MinimumPoints / MinimumRetainedPoints | P/H ≥3，Q ≥6；retained ≥ minimum，均 ≤资源点数上限 | Profile 必填，不能仅靠点数证明展开 |
| ClipLimit | None 必须 null；FixedClipOnce 有限 >0，单位为输入长度 | 用途 Profile；不从样本估计或放宽 |
| MaximumExcludedRatio | 有限 0..1，`(|R|-|I|)/|R|` 的上限 | Profile 必填；超限 RS-1101 |
| MinimumPlanarSpread | 有限 >0；P 为 `sqrt(λ1)`，H/Q 为 Chart 横向协方差最小主标准差 | 用途/采样 Profile；单位为输入长度 |
| MinimumEigenGapRatio | `64ε .. 1`，P 的 `(λ1-λ0)/λ2` 下限 | 数值 Profile；P 必填，H/Q 保留但不应用 |
| MaximumQrConditionOneNorm | 有限 1..1/(`64ε`)，针对列归一化 QR 的 R | 数值 Profile；H/Q 必填，P 不应用 |
| MinimumAxisNormalDot | 有限 (`64ε`,1] | 数值/误差放大 Profile；P 轴高使用 |
| MaximumHeightGradient | 有限 ≥0，H/Q 的 `sqrt(fx²+fy²)` 上限 | 允许预测坡度 Profile；P 不应用 |
| MinimumAreaRatio | null 或有限 0..1；§6.6 的参考有效单元面积比例下限 | 缺失标 Unknown；不能默认 0 冒充物理资格 |
| MaximumGap | null 或有限 >0；支撑三角最长投影边上限 | 缺失不形成连续支撑，不允许插值/外推 |
| MaximumTargetDistance | null 表示禁用外推；否则有限 ≥0 | 与 MaximumExtrapolationRatio 同时限界 |
| MaximumExtrapolationRatio | 有限 0..1，T 的外推点数/全部 T 点数 | 必填；0 禁用外推，空 T 不计算比例 |
| AllowInterpolation | bool；只在有连续单元证据时生效 | 必填；true 不许可跨洞/断层 |
| RequireIndependentCheck | bool | true 时 C 非空且两个 Check 上限均必填 |
| MinimumIndependentCheckPoints | 1..MaxPoints；实际有效 C 点数下限 | Profile 必填；必需检查不足拒绝，否则只标检查证据不足 |
| CheckRms / CheckP95 / FitRms | null 或有限 ≥0，单位为输入长度 | 用途 Profile；上限包含边界；无 Check 上限时只报告证据，不称“独立检查通过” |

所有字段受哈希保护。None 无剔点、最大排除比例为 0；null 是语义明确的缺证据/禁用，不用 0、负值、无限值做哨兵。参数/Chart/域/方向/标定变化重新计算，不在线调参。模块不推荐客户物理阈值；合成测试给出显式测试 Profile，只说明数学行为。

### 4.3 请求、运行边界与结果

```csharp
public sealed record ExecutionBudget(TimeSpan Deadline, long MaxWorkingBytes);
public sealed record ReferenceSurfaceEngineOptions(
    int MaxConcurrentExecutions, int MaxQueuedRequests, int MaxPoints,
    int MaxCells, int MaxEvaluationPoints, long MaxRetainedBytes);
public sealed record ReferenceSurfaceRequest(
    string RequestId, string CorrelationId, string ContractVersion,
    SurfaceSnapshot Surface, SurfaceDomain ReferenceDomain,
    SurfaceDomain? ExclusionDomain, SurfaceDomain? IndependentCheckDomain,
    SurfaceDomain? TargetDomain, ReferenceMethodProfile Profile,
    ChartFrame Chart, UnitVector3 ReferenceDirection,
    bool AcknowledgeTargetReferenceOverlap, HeightDistanceMode TargetMode,
    ExecutionBudget Budget);
public enum ReferenceResultStatus { Succeeded, Rejected, Unevaluated, Cancelled, TimedOut, Failed }
public enum ModelKind { Plane, HeightFirstOrder, HeightSecondOrder }
public sealed record PlaneModel(UnitVector3 Normal, double DInMeters, Point3 Origin);
public sealed record HeightModel(
    ChartFrame Chart, double CenterXInMeters, double CenterYInMeters,
    double ScaleXInMeters, double ScaleYInMeters,
    ImmutableArray<double> CoefficientsInMeters);
public sealed record SurfaceModel(
    ModelKind Kind, PlaneModel? Plane, HeightModel? Height, string ModelSha256);
public sealed record ResidualSummary(
    long CandidateCount, long FitCount, long FinalInlierCount, long CheckCount,
    double? CandidateRmsInInputUnit, double? FitRmsInInputUnit,
    double? FinalInlierRmsInInputUnit, double? MaxAbsInInputUnit,
    double? P95AbsInInputUnit, double? IndependentCheckRmsInInputUnit,
    double? IndependentCheckP95InInputUnit, bool IndependentCheckIsHeldOut);
public sealed record ReferenceSelectionSummary(
    long SurfacePointCount, long DeclaredReferenceCount, long InvalidReferenceCount,
    long PriorExcludedReferenceCount, long EligibleReferenceCount,
    long OutsideReferenceCount, long RobustExcludedCount);
public sealed record UncertaintySummary(
    bool IsAvailable, double? EstimateInInputUnit,
    ImmutableDictionary<string, double> ComponentsInInputUnit,
    ImmutableArray<string> Limitations);
public readonly record struct ProjectedPoint(long SourceIndex, double XInMeters, double YInMeters);
public readonly record struct ProjectedCell(
    long CellId, ProjectedPoint A, ProjectedPoint B, ProjectedPoint C);
public sealed record SupportEvidence(
    ChartFrame Chart, bool CoverageQualified, ImmutableArray<ProjectedPoint> FinalInlierPoints,
    ImmutableArray<ProjectedCell> ContinuousCells,
    ImmutableArray<ProjectedCell> ForbiddenCells,
    ImmutableArray<ProjectedCell> UnknownCells,
    ImmutableArray<ProjectedPoint> ForbiddenPoints,
    ImmutableArray<ProjectedPoint> ReferenceFootprintHull, string EvidenceSha256);
public sealed record ReferenceBinding(
    string SurfaceId, ulong SurfaceRevision, string CoordinateFrameId, LengthUnit Unit,
    string InputSha256, string ReferenceDomainSha256, string? ExclusionDomainSha256,
    string? CheckDomainSha256, string? TargetDomainSha256, ChartFrame Chart,
    UnitVector3 ReferenceDirection, bool AcknowledgeTargetReferenceOverlap,
    HeightDistanceMode TargetMode);
public sealed record SupportSummary(
    double? SupportedAreaRatio, double? MaximumGapInInputUnit,
    double? MaximumTargetDistanceInInputUnit, bool IsExtrapolated,
    ImmutableArray<string> Reasons);
public enum TargetSupportStatus { Supported, Extrapolated, Unsupported, Unknown }
public enum ReferenceValidity { Observed, Interpolated, Extrapolated, Invalid, Unknown }
public sealed record TargetEvaluationSummary(
    string TargetDomainId, TargetSupportStatus Status, long EvaluatedPointCount,
    long ObservedPointCount, long InterpolatedPointCount, long ExtrapolatedPointCount,
    long InvalidPointCount, long UnknownPointCount,
    ImmutableArray<long> AffectedSourceIndices, ImmutableArray<string> Reasons);
public sealed record ReferenceSurfaceResult(
    string RequestId, string CorrelationId, string ContractVersion,
    ReferenceResultStatus Status, SurfaceModel? Model,
    ReferenceSelectionSummary Selection, ResidualSummary Residuals,
    SupportSummary Support, SupportEvidence? Evidence,
    ImmutableArray<long> FitSourceIndices, ImmutableArray<long> FinalInlierSourceIndices,
    ImmutableDictionary<long, string> ExcludedSourceReasons,
    ReferenceBinding? Binding, string? RequestSha256,
    string AlgorithmVersion, FrozenProfileReference? ProfileReference,
    ImmutableArray<TargetEvaluationSummary> TargetEvaluations,
    UncertaintySummary Uncertainty, string? ResultSha256, DateTimeOffset ResourcesReleasedAt,
    string? ErrorCode, string? ErrorMessage);
```

预算仅在 `Budget.Deadline` 定义一次，是从接纳开始的相对期限；范围 1 ms..24 h，必填，无默认客户节拍。MaxWorkingBytes >0，含排序/拓扑索引/数值工作数组/输出复制的同时峰值；先 checked 估算再分配，运行中计账。Options 必填：并发 1..32、队列 0..256、点数 1..10,000,000、单元 0..20,000,000、单次求值点数 1..1,000,000、MaxRetainedBytes >0。MaxRetainedBytes 是实例已接纳不可变输入与运行工作预算总和的上限；排队仍计输入字节，不能靠队列扩大内存。消费者自行采纳更小预算；上限不是已测性能。无优先级或不完整 CacheKey；首发不建内部缓存，由 §8 的宿主只读 Artifact 复用。

成功模型必须满足互斥形状：P 仅 Plane 非空；H/Q 仅 Height 非空，系数分别 3/6 项。失败结果无可消费 Model/Evidence/距离；可保留计数与错误诊断。模型坐标、d、系数统一米，距离汇总及求值按 Result.Binding.Unit 返回；Plane.Origin 也用 Meter，Chart 保留原输入单位并在几何计算时转米。结果 Binding 显式保存方向、Chart、域身份与单位，不能只有无法解码的 hash。结果不携带质量放行或业务 TargetId，宿主以 `AffectedSourceIndices` 映射自己的目标。

Execute的T评估明确使用TargetMode；P可选择两种，H/Q只能SignedAxisHeight，即使T为空也不得声明未支持模式。TargetMode必须绑定RequestSha256，不由Profile或UI猜测；Execute只汇总T资格，数值消费按同一模式调用Evaluate/EvaluateAsync，不保存第二个未定义目标结果格式。

Succeeded 必须具非空 Binding/RequestSha256/ProfileReference/ResultSha256；Reject/Failed 在输入尚未验证时这些字段为 null，不伪造合法坐标、Profile或hash。未验证请求的错误诊断ID只能显示原文本的安全截断或 `<invalid>`，不得用它生成可消费身份；ContractVersion/AlgorithmVersion标明模块实际识别的 `rs-api-0.1/rs-managed-1`。非Succeeded不进入求值，其已验证的局部诊断不授权模型。所有失败状态的残差空集为0计数/null数值，已完成集合计数可保留；没有空/错误输出被默认平面填充。

### 4.4 完整入口、事件与求值端口

```csharp
public enum ReferenceStage { Validating, Preparing, Fitting, Refitting, Qualifying, Evaluating, ResultReady }
public sealed record ReferenceSurfaceProgress(
    string RequestId, ReferenceStage Stage, long Processed, long Total, DateTimeOffset At);
public enum ReferenceOperationState {
    RequestAccepted, Validating, Preparing, Fitting, Refitting, Qualifying, Evaluating,
    ResultReady, CancelRequested, DeadlineReached, Draining, DrainUnknown,
    Drained, ResourcesReleased, Completed, Rejected, Unevaluated, Cancelled, TimedOut, Failed
}
public sealed record ReferenceSurfaceEvent(
    string RequestId, long Sequence, ReferenceOperationState State,
    DateTimeOffset At, string? ErrorCode);
public enum ReferenceEngineState { Open, Closing, DrainUnknown, Closed }
public sealed record ReferenceEngineSnapshot(
    ReferenceEngineState State, int RunningCount, int QueuedCount,
    long RetainedChargeBytes, long CallbackFailureCount,
    ImmutableDictionary<string, ReferenceOperationState> ActiveRequests);
public sealed record ReferenceEvaluation(
    TargetSupportStatus Status, ReferenceValidity Validity,
    double? SignedDistanceInInputUnit, double? SignedAxisHeightInInputUnit,
    Point3? ReferenceIntersection, double? UncertaintyInInputUnit,
    ImmutableArray<string> Reasons, string? ErrorCode);
public readonly record struct ReferenceEvaluationPoint(
    Point3 Position, bool IsValid, long? SourceIndex);
public sealed record ReferenceEvaluationRequest(
    string RequestId, ReferenceSurfaceResult Result,
    ImmutableArray<ReferenceEvaluationPoint> Points, HeightDistanceMode Mode, ExecutionBudget Budget);
public sealed record ReferenceEvaluationBatch(
    string RequestId, ReferenceResultStatus Status,
    ImmutableArray<ReferenceEvaluation> Values, DateTimeOffset ResourcesReleasedAt,
    string? ErrorCode);
public interface IReferenceSurfaceProfileLease : IAsyncDisposable {
    ResolvedReferenceProfile Snapshot { get; }
}
public interface IReferenceSurfaceProfileSource {
    ValueTask<IReferenceSurfaceProfileLease> ResolveAsync(
        FrozenProfileReference reference, CancellationToken cancellationToken = default);
}
public interface IReferenceSurfaceEngine : IAsyncDisposable {
    event EventHandler<ReferenceSurfaceEvent>? StateChanged;
    ReferenceEngineSnapshot GetSnapshot();
    ReferenceSurfaceResult Execute(ReferenceSurfaceRequest request,
        CancellationToken cancellationToken = default);
    ValueTask<ReferenceSurfaceResult> ExecuteAsync(ReferenceSurfaceRequest request,
        IProgress<ReferenceSurfaceProgress>? progress = null,
        CancellationToken cancellationToken = default);
    ReferenceEvaluation Evaluate(ReferenceSurfaceResult result,
        ResolvedReferenceProfile exactProfile, ReferenceEvaluationPoint point, HeightDistanceMode mode,
        ExecutionBudget budget,
        CancellationToken cancellationToken = default);
    ValueTask<ReferenceEvaluationBatch> EvaluateAsync(
        ReferenceEvaluationRequest request, IReferenceSurfaceProfileSource profileSource,
        CancellationToken cancellationToken = default);
    ValueTask CloseAsync(CancellationToken waitCancellationToken = default);
}
public static class ReferenceSurfaceFactory {
    public static IReferenceSurfaceEngine Create(ReferenceSurfaceEngineOptions options);
}
public static class ReferenceSurfaceIdentity {
    public static string ComputeSurfaceSha256(SurfaceSnapshot surface);
    public static string ComputeDomainSha256(SurfaceDomain domain, string inputSha256);
    public static string ComputeProfileSha256(ReferenceMethodProfile profile);
    public static string ComputeRequestSha256(ReferenceSurfaceRequest request);
    public static string ComputeRequestSha256(ReferenceBinding binding,
        FrozenProfileReference profileReference, string contractVersion, string algorithmVersion);
    public static string ComputeModelSha256(SurfaceModel model, string requestSha256);
    public static string ComputeEvidenceSha256(SupportEvidence evidence,
        string requestSha256, string modelSha256);
    public static string ComputeResultSha256(ReferenceSurfaceResult result);
}
```

Factory 是公开签名声明，不是带空体的产品代码。Execute 与 ExecuteAsync 使用同一执行逻辑；同步入口仅用于无 UI 工作线程，也遵守队列、期限与关闭。同步 Evaluate 消费宿主已取得且复制封存的精确 Profile 值，重新校验身份与哈希，不做 IO；异步批量 EvaluateAsync 才接入 ProfileSource，解析一次且在结束前真实释放租约。单点 Evaluate 不加入长任务队列，无进度事件，检查调用取消、实例关闭和结果/Profile 有效性；结果模型不再拟合。批量入口使用同一有界调度、事件与预算，不自建无界 Task.Run。源点自身失效、点在洞内或未知均返回显式状态，错误不是距离 0。

Identity 方法为明确公开签名；只编码有限、已满足结构约束的值，不调用拟合/设备/存储，非法结构抛 ArgumentException，不把错误编码为有效 hash。传入自身 hash 可为空用于首次计算，随后 `with` 填入；其他必需身份字段不能为空。Factory 非法 options 也抛 ArgumentException。Execute/Evaluate 的业务校验、数值/资源异常用模块结果表达，不把 OperationCanceledException 作为已排空结果返回；Close 的等待取消例外见 §7。`ReferenceEvaluationPoint.SourceIndex` 仅是宿主来源标签，不能授权 Observed；IsValid=false 返回 Invalid 且不读占位高度。批量保留输入顺序，SourceIndex 如有必须非负且不重复；空批量返回 Rejected+RS-1001，不解析 Profile。批内各项均由该请求 Result.Binding 坐标系解释，混合单位/非有限有效点拒绝全批。请求点和原模型不属于同一坐标框架时由宿主先转换并绑定新的来源，不隐式转换。

进度只报阶段/计数，StateChanged 是可观测状态事件；每请求序号从 1 严增。每订阅者按请求顺序同步调用，异常隔离并记录诊断；宿主回调必须非阻塞，仅复制事件，不在回调内同步等待 Close/Execute。Core 不捕获 UI SynchronizationContext；不得因订阅者异常更改计算结果。IProgress.Report 只交付不可变消息，不把 UI Dispatcher 的处理完成称为核心排空。

进度 Report 的同步异常同样隔离；CallbackFailureCount 累计饱和到 long.MaxValue，无递归“错误回调”。GetSnapshot 只复制有界活动表、计数和实例状态，不做 IO、不调用订阅者，Closing/DrainUnknown 时仍可查询，Closed 返回空活动表和零额度；它不是历史结果 Store。每阶段 Progress 总数使用真实相应集合大小，不把 ResultReady 当请求终态。无效字段的 ErrorMessage 只用稳定错误键与字段路径/请求 ID（参数不包含点云），三语由宿主资源投影，不写原始异常堆栈给操作员。事件发布位置在释放额度之后，终态回调返回才完成执行 ValueTask；Close 等待终态回调，不产生回调自等待。

## 5. 事件、状态和错误语义

### 5.1 事件顺序

一次请求最多产生以下顺序；`Progress` 可合并但不得逆序。终态事件只产生一次。

```text
RequestAccepted
 -> StageChanged(Validating)
 -> StageChanged(Preparing)
 -> StageChanged(Fitting)
 -> StageChanged(Refitting)
 -> StageChanged(Qualifying)
 -> StageChanged(Evaluating) [仅有目标评估时]
 -> ResultReady
 -> Draining
 -> Drained
 -> ResourcesReleased
 -> Completed | Rejected | Unevaluated | Cancelled | TimedOut | Failed
```

`RequestAccepted` 只表示排入执行上下文，不代表输入有效。`ResultReady` 只表示不可变计算值已封存，不能作为operation终态。取消/超时后停止新阶段，真实计算退出才Drained；Drained只证明算法和此前阶段回调退出，不宣称正在发布的Drained通知或未来终态回调已经返回。工作集/取消注册/Profile租约全部归还才ResourcesReleased，终态回调返回后才完成ValueTask；Close等待这些生命周期通知。迟到宿主消息按RequestId+generation丢弃，不覆盖新代。

### 5.2 状态与唯一终态

`RequestAccepted → Validating → Preparing → Fitting → Refitting → Qualifying → Evaluating → ResultReady` 是正常计算阶段；None 没有 refit，无 T 不进入 Evaluating。所有已接纳请求，无论成功、校验拒绝、数值错误、取消或超时，统一经 `Draining → Drained → ResourcesReleased → 唯一终态`，不得从 Validating/Qualifying 直接发布 Rejected。接纳前队列/资源/关闭拒绝不产生 RequestAccepted 或清理事件，返回 Rejected 与对应错误；校验拒绝不会持有工作集，但仍保留一致的已接纳事件路径。

取消、deadline与结果封存共用原子决策门，记录单调时钟观察顺序，首个被观察的终态意图胜出；同一观察点并发到达时deadline优先。提交门再次检查取消/期限/关闭；成功封存后仍在排空，截止/关闭若在终态提交前被观察则废弃成功值。未真实排空不完成执行ValueTask。正常算法退出后Drained，然后释放所有工作数组/注册/Profile租约；若释放等待未知，在Drained后可报告DrainUnknown，不重新发布Drained或回到Fitting。恢复释放完成才ResourcesReleased和原终态意图，不改成迟到Succeeded。

如果外部 ProfileSource 的解析/DisposeAsync 在请求期限到达后仍不完成，立即登记 `DeadlineReached → Draining → DrainUnknown`，保持请求等待及实例预算保留，不伪造终态。该实例停止接纳新请求，Core 继续观察原任务；迟到 lease 必须归还，且不得发布迟到成功值。DisposeAsync 无 token 也受同一观察期限，等待未结束不能声称释放。宿主用有限 token 等待 Close；超时后隔离该实例或终止独立进程，不释放仍在用的资源。该端口只有值输入/只读解析，不获得产品权威。純托管数值首片无 native worker，不因正常合作取消制造 DrainUnknown。进程退出是宿主恢复事件，不能证明旧操作释放。

`Completed/Succeeded` 表示能力计算完成，不表示产品合格。Succeeded 可含局部 Unsupported/Unknown；独立检查为必需却失败时整个请求 Rejected。`Unevaluated` 用于无法验证历史求值闭包等明确缺证据，不等于成功。

批量求值阶段是 RequestAccepted→Validating→Preparing（解析Profile/验证证据/建索引）→Evaluating→ResultReady，不伪造 Fitting/Refitting。接纳前拒绝统一 Rejected（预取消为 Cancelled）；已接纳格式/几何/检查拒绝为 Rejected，超资源/内部数值失败为 Failed，缺失历史绑定为 Unevaluated；取消/超时分别 Cancelled/TimedOut。全部非 Succeeded 的 batch.Values 必须为空，不返回截断结果；逐点 Unsupported/Unknown 是 Succeeded batch 中的显式项，仍无可消费距离。

### 5.3 错误码

错误码是模块候选命名空间，采纳时须注册到公共错误目录。错误正文必须包含 `RequestId`、阶段、字段/域和可操作恢复建议。

| 代码 | 语义 | 恢复责任 |
|---|---|---|
| `RS-1001 InvalidRequest` | 必填、版本、枚举或预算非法 | 修正请求 |
| `RS-1002 UnitMismatch` | 坐标/域单位或坐标系不一致 | 重新生成一致快照 |
| `RS-1003 NonFiniteInput` | NaN/无穷/非法索引 | 修复输入质量 |
| `RS-1004 DomainConflict` | 域修订、交集或自依赖冲突 | 重新声明域 |
| `RS-1101 InsufficientSupport` | 点数、二维展开或空间覆盖不足 | 换用有支撑输入；不得自动放宽 |
| `RS-1102 RankDeficient` | P/H/Q 几何秩不足或条件性失败 | 选择合适方法或补采样 |
| `RS-1103 IndependentCheckFailed` | 独立检查不满足 Profile | 由调用方决定拒识/复核 |
| `RS-1104 ExtrapolationNotAllowed` | 目标超出声明适用域 | 缩小目标或提供新参考 |
| `RS-1201 NumericalFailure` | 固定 TLS/QR 路线无法满足有限性、收敛或结果不变量 | 保留数值诊断并拒绝本次结果；不得切算法或放宽门限 |
| `RS-1202 ResultValidationFailed` | 拟合后结果不满足固定输出契约或有限性检查 | 丢弃候选并修复输入/实现；不得发布部分模型 |
| `RS-1301 ResourceLimit` | 点数、工作内存或并发上限 | 降低请求规模并生成新修订 |
| `RS-1302 Timeout` | 截止时间到达 | 等待排空后按调用方策略重试 |
| `RS-1303 Cancelled` | 调用方取消 | 不使用部分结果 |
| `RS-1401 CacheStale` | 缓存键与输入/方法/资格不一致 | 按完整键重新计算 |
| `RS-1402 EngineClosed` | 关闭开始后新请求/求值被拒绝 | 使用新引擎实例，不重开旧实例 |
| `RS-1403 DuplicateRequest` | 同一实例活动 RequestId 重复 | 等待原请求或用新 ID；不共享取消 |
| `RS-1404 ModeNotSupported` | H/Q 法向最短距离等未定义求值模式 | 使用已支持轴差，或调用另一已批准能力 |
| `RS-1501 InternalInvariant` | 模块内部不变量破坏 | 记录诊断，阻止结果外泄 |

## 6. 算法实施语义

### 6.1 集合、固定顺序与稳健边界

R0 为调用方原参考域，R 为 R0 中有限有效且不属于 X 的候选；C 必须与 R0/X 不相交且有效，不能参与选择模型/阈值/拟合。I 是实际最终拟合集；J 为最终模型在 R 上再次计算残差后的门内集。全部集合按 SourceIndex 升序，保留 R0 分母、排除原因和 I/J 索引；I 与 J 不必相同。None：拟合 R 一次，I=J=R；FixedClipOnce：拟合 R 得候选→按 `|r|<=ClipLimit` 固定 I→检查最少点/剔除比例→只重拟合 I 一次→重算全 R 得 J，不再剔点/迭代。最终 I RMS 超 Profile 上限则拒绝。J 不足 MinimumPoints 或二维展开不足，拒绝 RS-1101/1102。

Selection计数优先级为R0中原无效→先验X→合资格R，三者相加等于DeclaredReferenceCount；SurfacePointCount=DeclaredReferenceCount+OutsideReferenceCount；RobustExcludedCount=|R|-|I|。ExcludedSourceReasons只保存R0被排除点，键值为InvalidSource/PriorExclusion/RobustOutlier，按上述优先级每点一个原因；域外仅计数，不把T/C源点标算法失败。J中的新门外点保留FinalInlierSourceIndices差集及残差，不改写为新增RobustOutlier，避免偷换I的事实。

此策略是有界裁剪，不能承诺高离群比例/多物理层的 RANSAC 效果。两个平行层、对称污染、遮挡可能使候选偏置；不得用“最大面”“最低面”或多个候选自动判物理板面。调用方须以物理参考域区分层；模块在缺独立证据时返回 Unknown，在必需检查/残差/剔除/展开不合格时拒绝。没有隐式重采样、增阶、换后端或恢复旧面。

处理固定为：验证请求/哈希/资源→裁切 R/X/C/T→建立归一化与几何索引→候选拟合→固定 I 与一次 refit→全 R/I/J/C 残差→支撑资格→T 逐点求值→封存/排空/释放/唯一终态。输入是编码高度图时，上游先还原 ZScale/ZOffset、单位与标定，来源纳入快照 hash；模块不读显示倍率或猜零点。

### 6.2 P：确定性等权 TLS/Jacobi

按 SourceIndex 升序、IEEE binary64、禁止并行归约/fast-math/FMA重排，以两遍累加求中心 μ 和 `S=Σ(p-μ)(p-μ)^T/N`；每标量使用 Neumaier 补偿求和。对角元素单位 m²。以固定 `(0,1),(0,2),(1,2)` 列序作循环对称 Jacobi，单位矩阵初始化特征向量。旋转使用 `δ=(Sqq-Spp)/2`，Spq=0跳过，δ=0时t=1，否则 `t=Spq/(δ+copysign(hypot(δ,Spq),δ))`；`c=1/hypot(1,t), s=t*c`。不先计算δ/Spq，避免几乎对角矩阵比例溢出。hypot用先缩放最大绝对量的稳定形式；同步更新对称矩阵与向量，不能覆盖尚需的旧值。每扫掠后当off-diagonal Frobenius norm ≤ `64ε * ||S||F`停止，最多64扫掠；零矩阵拒绝，未收敛RS-1201，不替换算法。更新等价 `A'=JᵀAJ, V'=VJ`，J的局部块为[[c,s],[-s,c]]；只累加p/q对应行列，避免每次乘整个矩阵造成另一舍入路线。

排序 `λ0≤λ1≤λ2`，同值按原列号；负值若绝对值 ≤ `64ε*||S||F` 置 0，否则 RS-1201。要求 λ2>0、`sqrt(λ1)` 满足 MinimumPlanarSpread、`(λ1-λ0)/λ2` 满足 MinimumEigenGapRatio；λ0≈0 是理想平面，不使用 λ2/λ0 判病态。取 λ0 对应单位向量 n，若 n·ReferenceDirection<0 则翻转 n；`abs(n·ReferenceDirection)<=64ε` 拒绝定向歧义。`d=-n·μ`，残差 `r=n·(p-μ)`，避免大偏移相消。保存 n/d/μ，验证单位法向与有限性。不同硬件/运行时数值结果按 Golden 公差评估，不承诺跨运行时逐 bit 相同；同固定运行时/算法重复请求必须确定。

### 6.3 H/Q：高度图表与确定性 QR

定义 `x=(p-O)·U, y=(p-O)·V, z=(p-O)·a`，O/U/V/a 取请求 Chart，单位米。初始 R 的 xmin/xmax/ymin/ymax 决定 `cx=(xmin+xmax)/2, sx=(xmax-xmin)/2` 和 cy/sy；sx/sy 必须 >0，归一化 `u=(x-cx)/sx, v=(y-cy)/sy`。这些参数在 refit 时不重置，避免系数角色变化。横向协方差最小特征标准差须满足 MinimumPlanarSpread。

H 固定 `[1,u,v]`，Q 固定 `[1,u,v,u²,uv,v²]`。行按 SourceIndex、列按上述顺序。各列以稳定 L2 范数归一化；列范数为 0 拒绝。执行列主元 Householder QR：每步选尾部列范数最大列，严格相等取原基函数序号小者；每步重新计算尾部范数，避免递推漂移；Householder 使用 `α=-copysign(||x||2,x0)`（零取正号）、归一化反射向量并同时作用于剩余列及 RHS，不解法方程。按主元顺序回代，再反置换/除列范数，返回原顺序系数（米）。

令 `τrank=max(N,k)*ε`，若任一 `abs(Rjj) <= max(τrank,64ε)*max_i abs(Rii)` 则 RankDeficient；计算三角 R 的 `κ1=||R||1*||R^-1||1`（仅3×3/6×6，以单位列回代），超过 MaximumQrConditionOneNorm 拒绝。它是明确命名的 QR 三角条件数，不冒称设计矩阵 SVD κ2。最终残差为 `r=z-f(u,v)`。Q 圆环有 `u²+v²=const` 的线性依赖，六点以上仍可欠秩。导数 `fx=(c1+2c3u+c4v)/sx, fy=(c2+c4u+2c5v)/sy`；H 省略二次项。求值位置和每个连续单元顶点须检查坡度上限；Q 梯度仿射，在三角顶点检查足以界定域内梯度范数最大值。轴/归一化/系数/模型域全随结果返回。

QR内所有点积按当前Householder尾部行的固定顺序Neumaier累加，Householder范数采用稳定缩放L2，不做并行归约或FMA变换。H/Q求f时按声明基函数序号生成乘积并Neumaier累加，不另选Horner舍入路线；导数按写出的项序累加。验证每个输出有限、尺度>0、系数长度/ModelKind一致，QR解在同I上重算；P验证单位n和`abs(n·μ+d)<=64ε*(abs(d)+norm(μ))`。不变量失败RS-1202，不通过重拟合/改公差绕过；Golden解析误差按§11而非生产阈值判定。

### 6.4 残差、独立检查与不确定度

对最终模型分别计算 R/I/J/C 的 RMS=`sqrt(Σr²/N)`，空集为 null，禁止分母换成原始总点数；平方和采用稳定缩放 L2 norm，RMS=norm/√N，不以直接 r² 溢出裁掉样本。`MaxAbs/P95Abs` 明确对应全 R；绝对残差排序后取 `ceil(.95*N)-1` 的元素，包含离群点。C 单独报告 RMS/P95/计数，仅当存在有效非重叠 C 才 `IndependentCheckIsHeldOut=true`。C 必需且有效点数少于 MinimumIndependentCheckPoints 或超过任一 Check 上限返回 RS-1103。非必需且超已给上限亦拒绝；没有阈值仅报告，不标通过。FitRms 超已给上限拒绝 RS-1101。数值计算非有限为 RS-1201，不能裁掉失败点再发布。

首发不具备输入噪声协方差、标定/方向误差传播和模型误差预算契约，因此固定返回 `UncertaintySummary(false,null,空字典,["InputCovarianceNotProvided","ModelErrorNotQualified"])`；逐点 Uncertainty 也为 null。保留可扩展字段，但不让实现者发明公式。未来不确定度数值切片必须先增加噪声/相关性/自由度/覆盖因子输入、传播算法和 Golden；RMS 仍不等于总不确定度。

### 6.5 类型化补偿评估

P：`dn=n·(p-μ)`；法向交点 `p'=p-dn*n`；指定 Chart 高度轴 a 时 `h=dn/(n·a), p'=p-h*a`，要求 `abs(n·a)>=MinimumAxisNormalDot`。整对 (n,d) 翻转时 dn 变号、相同 a 下 h 不变。必须对所选模式交点的 Chart 投影做支撑检查，不仅检查原 p 投影。

H/Q：仅支持 SignedAxisHeight，固定 a=Height.Chart.HeightAxis，`h=z-f(u,v)`，`p'=O+xU+yV+f(u,v)*a`。不得套用 P 公式，不求一般曲面最短法向距离，不做任意轴多根求交。SignedNormalDistance 返回 Unsupported/Invalid、空距离、RS-1404。每次求值先检验类型形状、Profile/结果/证据 hash、单位/版本和坡度，再判支撑；无支持的交点不返回可消费距离。

### 6.6 支撑几何、面积与局部有效性

连续支持集 S 仅由 R0 域中 `IsContinuous=true`、三个顶点均在 J、投影面积正且最长边≤MaximumGap 的单元组成；不得把凸包内部当支持，也不连接断层。R0 全部单元投影面积为固定分母（包括断层/无效单元），S 面积为分子；无 R0 单元、无分母、缺 Gap/MinimumAreaRatio 时连续用途资格 Unknown。`CoverageQualified` 仅在有正分母且两参数均给出、比例满足时 true；已给面积下限但证据缺失/比例不足拒绝 RS-1101。MaximumGap 输出为 S 最长边，无 S 为 null；它是单元间距指标，不声称已测孔洞直径。R0 无单元时，Profile.MinimumAreaRatio 必须 null 才允许离散模型继续计算；不隐式降低原面积资格。

按输入证据生成互斥分类：R0 中断层、任一无效/X/非 J 顶点或已知超 Gap 的单元为 ForbiddenCells；只有 Gap 缺失且其他条件满足的单元为 UnknownCells。X 自有 CellIds 对应投影也加入 ForbiddenCells；X.SourceIndices 的投影及 R0 无效/非 J 点加入 ForbiddenPoints。先验 X 面积不加到 R0 面积分母；如果 X 与 S 内部重叠（不能只凭离散索引发现），则不裁切/重三角化，拒绝 RS-1004，调用方先生成明确的新拓扑。X 与支持仅共享边/顶点也不能在那里授权插值，禁止优先级最高。

H/Q连续单元任一顶点的最终模型坡度超过MaximumHeightGradient，同样转ForbiddenCells，不能进入S；显式点求值坡度超限为Invalid/RS-1104，即使与J位置重合也不授权Observed。坡度比较只影响该位置/单元及面积分子，未违反其余参数的模型可保留；已给面积下限因此失败则整请求Rejected。任何导数/求值非有限是RS-1201/1202计算失败，不能把NaN点排除再假称局部成功。P不应用高度坡度参数，而在所选求值模式单独检查轴方向稳定性。

在 Chart 投影使用 orientation/重心包含测试，边界包含，落在多个共享边单元时按 CellId 升序，内部重叠已在输入拒绝。需要稳健谓词时不引入隐藏几何库：orientation 使用 binary64 的误差界过滤，模糊时以每个 IEEE double 解码成带整数尾数/二进制指数的精确 BigInteger 行列式确定符号；仅计算值语义，不使用手调坐标容差。谓词时间和 BigInteger 工作量计入预算，绝不为省时退回不可靠符号。

具体过滤：计算 `det=(bx-ax)*(cy-ay)-(by-ay)*(cx-ax)` 和 `detsum=abs左乘积+abs右乘积`，`abs(det)>(3+16ε)*ε*detsum`且所有中间值正常有限时接受符号；其余（含subnormal/溢出）走精确分支。binary64正规数解为符号整数尾数(2^52+fraction)×2^(exp-1023-52)，次正规数为fraction×2^-1074；差/积按最小指数左移对齐计算整数det，取其符号，零则共线。三角面积用精确det绝对值/2转double并Neumaier求和，若正面积无法有限非零表示则拒绝数值失败，不能把它丢掉改分母。资源/取消边界仍检查。

空间索引固定为AABB二叉树：按最长包围盒轴（同长X先于Y）、中位中心分割、中心相同取CellId/SourceIndex、叶≤8项；节点边界闭合，交叉/包含候选逐ID排序后用精确谓词，单元不得内部相交。点到支撑距离以AABB下界优先、相同下界按节点构建序号，扫描全部可能更近叶，不近似提前止步。树/谓词预算不足拒绝，不能用无界O(N²)全点对或用近似凸包代替。此索引是本能力的工作数据，不泄漏给调用方或变成公共几何库。

逐点优先级：调用 IsValid=false、ForbiddenPoints 精确重合或 ForbiddenCells 内（含边界）→Invalid；UnknownCells 内→Unknown；与 J 投影点精确重合且无冲突→Observed（参考位置有观测，补偿仍是模型值）；落在 S 内但 CoverageQualified=false→Unknown；落在已获资格 S 内且 AllowInterpolation→Interpolated，明确禁插值则 Invalid。S 外但仍在 ReferenceFootprintHull 内→Unknown，表示未声明拓扑的孔洞/缺域，不能以外推绕过；只有在该外边界之外，S 非空、CoverageQualified=true 且有限外推距离/比例获准才 Extrapolated；明确禁止外推或超过已知上限则 Invalid；缺必要证据→Unknown。距离是点到 S 三角并集的最小二维距离（内部0、外部到边线段距离）；不以中心距离替代。

ReferenceFootprintHull 是 R0 全部有限位置投影的凸包，仅作“内部未知缺口/外部预测”的保守分界，不授权任何内部支撑。固定 Andrew 单调链，以 (x,y,SourceIndex) 升序、精确 orientation 删除非左转共线中间点，逆时针输出且从字典序最小顶点起始；不足三个非共线点不准外推。R0 内同投影不同层/来源重复位置拒绝歧义；T 与 R 同投影是高度差的正常输入，不能误当层冲突。边界归内部。支撑、禁止域、未知域和外轮廓必须全部封存；否则重开时可能把原孔洞误授外推。

T 逐点分母包括无效/Unknown 点；外推比例用 Extrapolated/全部 T 点数。超比例时本批所有外推项变 Invalid/Unsupported，无距离；保留原因，不挑选前几个使比例刚好达标。无 T 时不制造100%覆盖；后续单点 Evaluate 只能使用原 Profile 的外推许可，不能宣称单点满足批目标比例，`MaximumExtrapolationRatio<1` 时禁止单点外推并提示需批量求值。批量求值同样使用完整输入点数分母。

Validities 映射：Observed/Interpolated→Supported；Extrapolated→Extrapolated；Invalid→Unsupported；Unknown→Unknown。域汇总若任何 Invalid 为 Unsupported，否则任何 Unknown 为 Unknown，否则任何 Extrapolated 为 Extrapolated，否则 Supported；状态计数之和等于全部目标点数。AffectedSourceIndices 只列非 Supported 的目标源索引，模块不建立业务对象关联。

SupportEvidence 保留上述全部必要投影值，拒绝区不因释放输入或重开丢失；不包含输入租约/内部索引句柄。新目标在重开求值时检查同一证据/Profile；外部拓扑/标定/用途变化须新请求，不扩大旧支持域。单点 Evaluate 注册短调用直到退出，Close 同样等待它；在实例并发/内存额度不足时返回 RS-1301，不绕过资源限额。每次验证完整结果的成本计入调用，宿主大批量用 EvaluateAsync 一次验证/建索引，不能把单点 API 当无成本热路径。

SupportSummary.MaximumTargetDistance为T中全部IsValid且有可计算投影点到S的距离最大值（含最终Invalid/Unknown），无T或无S时null，不只挑支持点；IsExtrapolated仅当最终保留Extrapolated点时true。缺面积分母输出null，缺独立证据/坡度超限/域禁止的Reasons使用稳定键并去重排序，不能以小RMS隐藏这些原因。逐点固定原因键包括SourceInvalid/ForbiddenSupport/MissingTopology/InterpolationDisabled/OutsideAllowedPrediction/BatchExtrapolationLimit/AxisUnstable/ModeUnsupported；空间不适用时ErrorCode=RS-1104，证据缺失但无法判空间失败时可null并保留Unknown。Profile/身份/版本不匹配为RS-1401，非法输入为RS-1001/1002/1003，模式为RS-1404。单点资源/关闭/取消/超时分别RS-1301/1402/1303/1302且Validity/Status=Unknown、所有数值null，完成自身清理才返回；不能混称为有效物理零值。Succeeded批量可含这些空间有效性项，但整个操作取消/超时必须空Values与相应终态。

## 7. 同步、异步、取消、超时和排空

每实例独立调度器、活动 RequestId 集、FIFO 有界队列、资源计账，无静态当前配方/共享可变参数。RequestAccepted 在入队与输入预算保留成功后产生，deadline 同时以 TimeProvider.GetTimestamp 单调时间开始（包括排队、Profile 解析与输出复制）；墙钟只用于记录。队列满、输入/工作预算超限为 RS-1301，活动重复 ID 为 RS-1403，不挂接原请求。终态回调返回且活动表移除后 ID 可再次提交，必重新执行、不具幂等事实语义；业务重试仍建议新 ID 并保留 CorrelationId。

输入 ID/修订/状态键最长128 UTF-16码元，采集/标定/连续性证据引用最长1024，SourceValidityCode 最长128；必填字符串非空且不得全空白/含未配对 surrogate，hash 必须小写64 hex。实例接纳 charge 固定为 4096 基础字节 + 全部可达字符串 `64+2*Length` + 每源点128 + 每源单元256 + 每域4096及每域索引16 + 请求 MaxWorkingBytes；即使共享快照也逐请求收费，保守上限不声称实际 CLR 字节。批量额外按每输入求值点128、每引用 Result 的规范编码字节计 charge。checked 运算溢出或超 MaxRetainedBytes 接纳前拒绝，不先分配巨型数组。结果编码只流式计长/哈希，不为计 charge 创建同尺寸 byte[]。

工作分配账固定包括 `64+elementCount*elementCharge`，long/double 每元素8，坐标/源点工作项每项128，三角/空间索引节点每项256，字典/排序索引每项64；字符串同上，BigInteger 每个 `64+ceil(bitLength/8)`，byte缓冲每字节1；其他复合记录每项256并递归计入所持集合，不双算同一工作分配。所有并存租用数组按实际容量收费，池数组也计；输出封存数组同时计入峰值。每次申请先预留，失败包括 OOM 均撤销申请账并转 RS-1301，已用数组排空后释放。预算是保守软件额度，Benchmark 另测真实 GC/进程峰值，不能把逻辑 charge 当实测内存。

已取消 token 在接纳前直接返回 Cancelled，不分配/入队。排队取消移除队列项、释放输入预算再返回；正在计算的取消只登记意图、停止新阶段，循环每≤4096点、每个 QR 列/每个 Jacobi 旋转、每个拓扑候选批检查 token/deadline，真实退出才排空，不使用 Thread.Abort 或仅 Task.WhenAny 后提前归还数组。预算到达也走该路径。数值单个基本操作无可中断 native 调用；拓扑精确谓词有界于输入 binary64 指数范围，累计工作仍受 deadline/内存限制。

执行返回前从工作集复制所有结果所需值，再清理池数组、注册、输入引用；输出由调用方持有，无 Dispose 要求。租约成功/异常/取消均在 finally 中 DisposeAsync 且等待完成。外部来源未响应的未知排空按 §5.2 隔离，不能假称已释放。计账包含输出峰值直到交付，交付后宿主负责历史结果留存上限；Core 不持有历史结果/内部缓存。

CloseAsync 原子置 Closing，停止接纳、取消队列/活动操作，等待全体 Drained/ResourcesReleased 与事件返回，然后 Closed；重复调用等待同一关闭任务。waitCancellationToken 只取消调用者等待（抛 OperationCanceledException），不撤销 Closing、不提前释放；之后仍能重新等待 CloseAsync。DisposeAsync 复用无等待取消的关闭任务，等待完成；不拥有或关闭宿主提供的 ProfileSource/诊断服务。关闭前已返回的不可变结果仍可由新引擎配原 Profile 求值；旧实例 Evaluate 返回 RS-1402。宿主断连只在它明确取消 token/Close 时影响操作，Core 不猜连接状态；迟到 UI/网络消息按 RequestId+宿主 generation 丢弃，不覆盖新代。

StateChanged 订阅者在线程执行边界收到不可变事件，不捕获 Dispatcher；宿主回调立即入自己的有界队列，不在核心回调等待 UI。进度可合并；终态/错误不合并丢失。同步入口不可从 WPF UI 线程调用；Close 不同步阻塞 Dispatcher。状态事件的回调异常不传播到算法，但诊断保留；慢回调计入排空时间，不宣布尚未退出的核心回调已 Drained。

## 8. 缓存与版本

### 8.1 内容身份、序列化和宿主缓存

首发无内部缓存；宿主可只读保存完整 Artifact 再求值。身份规则固定 `rs-binary-v1`，与显示 JSON 无关：SHA-256 小写64 hex；每个记录/struct 的起始 tag 是按字符串规则编码的 `rs-binary-v1/` 加不含 namespace 的公开类型名；嵌套记录也有 tag，原始数值/枚举/数组本身无 tag。每个记录字段按本节构造参数声明顺序，先编码字段名字符串再编码值；整型 little-endian（枚举声明次序从0递增 int32、long/int64、ulong/uint64）；bool 单字节0/1；double 为 IEEE binary64 little-endian，-0规范为+0，非有限拒绝；字符串为 int32 UTF-8字节长度加原字节，无BOM、不改大小写/Unicode、拒绝畸形Unicode；nullable（包括 string/record）先单字节0/1标记；非nullable无标记。数组先 int64长度再逐项；字典先 int64长度，按键 ordinal（long数值升序）逐个编码键值。TimeSpan 以 int64 ticks；DateTimeOffset 如参与外部编码用 UTC ticks，但时间戳不参与以下身份。每次读取明确版本，不猜 JSON 默认值；§11 给出固定向量。

各 Compute 方法仅排除自己顶层的 hash 字段及其字段名，不全局删除嵌套 hash：Surface.ContentSha256、Domain.DomainSha256、Profile.ParameterSha256、Model.ModelSha256、Evidence.EvidenceSha256、Result.ResultSha256。Surface/Domain/Profile 按其余声明字段编码；Domain 顶层 tag 后、正式字段前增加名为 InputSha256 的字段和值。Profile 内容摘要就是 FrozenProfileReference.ContentSha256，两者相等。Points/ProjectedPoint 按 SourceIndex、Cells/ProjectedCell 按 CellId、域 SourceIndices/CellIds 升序；系数维持基函数顺序，Hull 维持规范环顺序，Reasons/Limitations 是 ordinal 去重排序集合。其他数组保留声明的语义顺序；不得悄悄排序 batch 输出。

Request 身份使用 tag `rs-binary-v1/ReferenceRequestIdentity`，仅按 `ContractVersion(string), AlgorithmVersion(string，固定rs-managed-1), Binding(ReferenceBinding), ProfileReference(FrozenProfileReference)` 的顺序编码字段，Binding 从原请求的表面、域hash、Chart/Direction/重叠许可生成。不含 RequestId/CorrelationId/预算，但原始预算仍随请求留存。Model tag 后先写额外字段 RequestSha256 再写其除自身hash的声明字段；Evidence tag 后先写 RequestSha256、ModelSha256 再写其余字段。因此无循环摘要依赖。Result 编码完整声明字段，但排除自身hash、ResourcesReleasedAt、ErrorMessage；其余嵌套hash必须存在。结果将自身错误码、绑定、残差/支撑/索引纳入摘要，重开时逐层复算 Request→Model→Evidence→Result；不得仅比 Profile hash 就接受被改写支撑。SHA256只证明内容一致，不证明来源真实性/权限，Artifact须来自宿主可信存储/验签通道；不能接受任意调用者重算hash就获得生产资格。

Artifact 身份必须绑定 ContractVersion、AlgorithmVersion、原请求 hash、Model/Evidence hash 和 FrozenProfile 内容。宿主缓存按这些完整内容匹配，不能只凭 FOV/板号/文件名。新 T/用途先重新资格评估，不能复用旧目标资格。直接从外部 JSON 读为 Result 的对象必须验证全部绑定与互斥形状；旧记录缺身份链只能历史查看，不把重新计算 hash 写回成旧身份。此编码是模块 Core 的值身份，不替代平台存储事务/Schema。

### 8.2 版本与回退

Module API Contract v0.1 的线格式使用 `rs-api-0.1`，算法使用 `rs-managed-1`。任何坐标/单位/基函数顺序/符号/支撑/裁剪/数值规则变化必须新算法版本； breaking API 变更升 major。未知枚举、未知编码/算法版本安全拒绝，不能用当前算法默读旧值。可选字段添加须有明确旧值语义，不能默认增加生产权限。

宿主保留原版本 Core 与 Artifact，以旧版本重放旧记录；新算法结果写新 Artifact，不覆盖历史。Profile 修订即使仅 ID/hash 改变也重新绑定；语言、视口、主题不改变数值身份。降版读取不了新字段/算法则 Unevaluated/RS-1401，可查看摘要而不能求值。

### 8.3 算法与输入边界

P/H/Q 各只有 §6 的固定纯托管路线，无算法后端注入/运行时切换。HALCON 26.05 `create_matrix/svd_matrix/solve_matrix` 能表达任意 XYZ 设计矩阵与最小二乘，不能称其“无法处理点云”；§17 保留它为可行比较路线。当前不引入它是已冻结的独立 Core 生命周期/确定性边界与首发路线决定，不是假称视觉库能力缺口或性能优势。未来替换先修订算法版本、契约与同输入比较门；不扫描 AsunImage 内部。

### 8.4 Profile 来源、求值与重开

执行请求提供完整不可变 Profile 值，Core 验证 canonical 内容 hash 后生成 FrozenProfileReference。同步 Evaluate 必须显式提供 ResolvedReferenceProfile；校验其ID/修订/hash与原结果精确相等，并校验结果/模型/证据闭包，不解析异步来源也不读取当前配方。EvaluateAsync 接受 ProfileSource：接纳/预算→ResolveAsync 精确引用→复制/校验值→逐点求值→finally 释放 lease→ResourcesReleased→返回 batch。来源租约禁止在释放后使用；不关闭来源对象。来源错误、null、错ID/修订/hash、缺快照返回 Unevaluated+RS-1401；不替换 latest/default 或把外部错误当0高度。

首发没有“覆盖原策略”的求值参数，所有插值/外推/坡度/方向限制只取原 Profile；新策略须新请求/新 Profile，不能扩大旧资格。batch 点数与实例 MaxEvaluationPoints、请求工作预算在 Resolve 前检查。宿主存储将 Artifact、原始快照/请求和完整冻结 Profile 原文绑定为同一成功提交；这是存储/领域 Owner 后续集成门，Core 不访问数据库。缺原 Profile 的记录仍可历史查看，但不可重新求值或宣称完整重算。

### 8.5 全局/局部组合与不确定度边界

有效性与数值定义唯一见 §6.4–6.6。局部参考失效不得隐式改用全局参考；宿主必须提交另一个明确的参考域/Profile 请求，保留两次结果及替代原因，再按自己的用途资格选择。模块每请求只估计一个已声明参考，不拥有“板级/局部”物理级别或目标关联；多个参考可并行计算，各自拥有独立 RequestId/预算。不同参考的高度、翘曲、面积/积分/体积只由计量/领域消费者组合，模块不反写原 Z。

当前不确定度数值切片未定义噪声协方差与传播输入，保持显式 unavailable；它不阻塞确定性模型/残差/支撑 Core，亦不被省略或伪造为 RMS。

## 9. 最小无 UI 宿主与两个消费者

以下是语义示例：snapshot、R/X/C/T、Profile由宿主构造且按§8.1计算hash；不是已编译产品或生产参数。模块公开API保持§4不变。`root/owner/ObserveBusiness/ObserveCleanup/ReconcileOrRetain`仅表示下述测试Exe/宿主进程根的本地Owner管理逻辑，不是新增模块接口、通用库或隐含全局配方。

### 9.1 Factory前强持与有界Owner槽

宿主进程根先创建有界Owner表，测试Exe固定容量2、每槽最多1 GiB逻辑持有额度、全表2 GiB；额度按§7输入charge及所有计划工作预算/持有输出预估，例中256 MiB工作预算另计输入，不能用同大小槽省略输入charge。真实宿主明确提供更严格预算，不能创建无界失败任务列表。Factory前原子Reserve槽，记录HostId、RequestId/CorrelationId、请求/Artifact/Profile身份、case单调截止点、不可变输入及B的借用ProfileSource强引用；容量/额度不足直接拒绝且不创建Factory/任务。原Owner从Reserve成功直到确认归还一直是该进程根强引用，局部变量离栈、WaitAsync超时、页面关闭不移除它。表操作使用预留槽，不因追加无限日志失败而丢Owner；错误记录最多1个业务错误及8个cleanup错误（超限计数）。

槽内保存Engine、业务CTS、原Execute/Evaluate Task、取消Task、Close Task/等待CTS、Dispose Task、每次任务的观察状态及最新GetSnapshot；每个异步操作先把原Task存槽再观察。Factory置于try内并把成功返回的Engine直接写入槽；Factory抛异常也进入cleanup并保留业务错误，未返回Engine且无Task的槽在确认自有CTS清理后才可归还。不改Factory语义，不假称Factory半返回或Dispose失败已成功。

### 9.2 双Host正常/异常路径

```csharp
var request = new ReferenceSurfaceRequest(
    RequestId: "height-001", CorrelationId: "replay-42", ContractVersion: "rs-api-0.1",
    Surface: snapshot, ReferenceDomain: referenceDomain,
    ExclusionDomain: exclusionDomain, IndependentCheckDomain: checkDomain,
    TargetDomain: targetDomain, Profile: planeProfile,
    Chart: new ChartFrame(new Point3(0, 0, 0, snapshot.Unit),
        new UnitVector3(1, 0, 0), new UnitVector3(0, 1, 0), new UnitVector3(0, 0, 1)),
    ReferenceDirection: new UnitVector3(0, 0, 1),
    AcknowledgeTargetReferenceOverlap: false,
    TargetMode: HeightDistanceMode.SignedAxisHeight,
    Budget: new ExecutionBudget(TimeSpan.FromSeconds(2), 256L * 1024 * 1024));
// root是进程根，owner预留成功后已由root强持；槽满则在Factory前拒绝。
var owner = root.Reserve("height-host", request, borrowedProfileSource: null);
try
{
    owner.BusinessCts = new CancellationTokenSource();
    owner.Engine = ReferenceSurfaceFactory.Create(
        new ReferenceSurfaceEngineOptions(2, 8, 1_000_000, 2_000_000,
            100_000, 2L * 1024 * 1024 * 1024));
    owner.ExecuteTask = owner.Engine.ExecuteAsync(request,
        cancellationToken: owner.BusinessCts.Token).AsTask();
    // 只给观察建立期限，原Task持续在槽内，禁止覆盖成WaitAsync的包装Task。
    var result = await ObserveBusiness(owner.ExecuteTask, owner);
    if (result.Status == ReferenceResultStatus.Succeeded && result.Model is not null
        && result.ProfileReference is not null)
    {
        var exact = new ResolvedReferenceProfile(result.ProfileReference, planeProfile);
        var value = owner.Engine.Evaluate(result, exact,
            new ReferenceEvaluationPoint(measuredPoint, true, null),
            HeightDistanceMode.SignedAxisHeight, request.Budget);
        // 宿主只有在 Status/Validity 允许时交给高度计量；无值不补0。
    }
}
catch (Exception error)
{
    owner.RecordBusinessError(error); // 保留原业务错误，不在catch清槽。
}
finally
{
    try
    {
        await ObserveCleanup(owner, "cancel");
    }
    finally
    {
        try
        {
            await ObserveCleanup(owner, "close");
        }
        finally
        {
            try
            {
                await ObserveCleanup(owner, "dispose");
            }
            finally
            {
                root.ReconcileOrRetain(owner); // 不满足归还断言就保留强持槽。
            }
        }
    }
}
```

消费者 A 为高度/翘曲的无 UI 回放宿主：读取稳定快照→生成R/X/C/T→完整 Profile→ExecuteAsync→核对终态→逐点轴差→由计量模块计算统计/翘曲→外部 Owner 保存。它不要求体积消费者在线，取消只影响其 RequestId。

消费者B为另一通用表面/体积宿主，引用公开值类型；对同一Artifact新目标重新评估，不引用A的ViewModel/板/焊盘/工单/私有Store。B在独立进程使用自己的root；合成Exe的A/B模式共用容量2的进程根但槽、Engine、CTS及身份互不混用。两者无UI/设备/数据库/HALCON依赖，真正双消费者集成仍未验收。

```csharp
var evaluationRequest = new ReferenceEvaluationRequest("volume-001", artifact,
    immutablePoints, HeightDistanceMode.SignedAxisHeight, budget);
// Reserve强持Artifact、请求、精确Profile身份及借用source，先于Factory。
var owner = root.Reserve("volume-host", evaluationRequest,
    borrowedProfileSource: exactProfileSource);
try
{
    owner.BusinessCts = new CancellationTokenSource();
    owner.Engine = ReferenceSurfaceFactory.Create(options);
    owner.EvaluateTask = owner.Engine.EvaluateAsync(evaluationRequest,
        owner.BorrowedProfileSource, owner.BusinessCts.Token).AsTask();
    var batch = await ObserveBusiness(owner.EvaluateTask, owner);
    // 仅明确Supported/已获准Extrapolated的项交计量；消费/保存失败保留原错误。
    ConsumeQualifiedValues(batch);
}
catch (Exception error)
{
    owner.RecordBusinessError(error);
}
finally
{
    try { await ObserveCleanup(owner, "cancel"); }
    finally
    {
        try { await ObserveCleanup(owner, "close"); }
        finally
        {
            try { await ObserveCleanup(owner, "dispose"); }
            finally { root.ReconcileOrRetain(owner); }
        }
    }
}
```

### 9.3 独立有限cleanup观察与原Owner恢复

本页语义helper的行为在此冻结，不留编码时任选：ObserveBusiness用原Task.WaitAsync观察，合成Host业务等待最多3 s且不超过case剩余额度；等待超时只记录业务Timeout，原Task仍强持，不能把包装Task完成当资源终态。Owner的业务错误优先保留首次业务异常/拒识，cleanup错误另列；只有cleanup失败时宿主也返回失败/非零，无catch吞掉后成功。迟到业务Task的结果/异常最终由root观察一次，不提交迟到值、不改变RequestId或以清理错误覆盖业务错误。

ObserveCleanup分别启动/观察cancel、close、dispose；每步使用新的观察额度，不使用已取消的业务token。测试cancel最多0.5 s、close1.5 s、dispose1.5 s，均取case剩余单调期限最小值，不给每次重试重新生成完整10 s。cancel用BusinessCts.CancelAsync，首次启动把原Task存CancelTask，回调异常/超时记录cleanup错误；此后只观察同Task。Close首次调用CloseAsync并把原Task/独立等待CTS存槽，有限观察结束后取消该等待CTS也不能撤销Core的Closing；重复cleanup只观察已持任务或查询GetSnapshot，不能依赖Close返回成功假设业务Task已返回。独立等待CTS自身的取消观察也计该步额度并持Task，直到相关回调退出才Dispose CTS。

dispose阶段即使cancel/Close观察失败仍在嵌套finally执行：若Engine存在且尚未启动，调用DisposeAsync().AsTask一次并存DisposeTask，再以独立有限WaitAsync观察；任务仍在途、已故障、同步调用抛异常均不得再次调用DisposeAsync。同步抛异常记DisposeStarted及失败，禁止清槽或把“无Task”当成功。Close等待取消/失败不跳过dispose观察，但dispose的迟到/未知不能阻塞宿主响应；root保持隔离引用及查询。所有helper捕获并记录各自启动/观察/取消异常，记录本身使用预留有界槽、不抛异常；嵌套finally仍保证后续步骤和最终Reconcile执行。

ReconcileOrRetain只能在以下同时满足时原子清槽：原Execute/Evaluate Task及自有cancel/Close等待/Dispose Task均完成且故障已观察；若有Engine则Dispose成功、GetSnapshot=Closed/Running=Queued=0/RetainedCharge=0/ActiveRequests空；来源lease计数已归还（合成来源明确检查一次），自有CTS及等待CTS回调不再在途且Dispose已成功。Factory未返回Engine的特殊路径仍须所有实际启动Task完成、自有资源清理确认。任何Task未知、Dispose异常、查询异常/未Closed/额度非零均保持Quarantined；source是借用端口，只结束本槽借用、不Dispose宿主Source，不影响B/其它调用者。

root恢复循环每次使用有限观察片（合成故障例1 s），取case/suite剩余额度，读取同一原Task及GetSnapshot；不重复Dispose、不重用Engine、不创建替代Owner。已完成的Close等待Task若取消/失败，标记已观察但不宣称Core关闭，仍须Dispose成功及Closed查询确认。测试在首次未知观察后主动放开闩锁，随后验证实际lease归还及原Task终态；到case10 s仍未知则记录失败、强持槽不清。suite120 s停止新case并保留未确认槽，外进程180 s只终止隔离测试进程，不把退出视为归还证明。

如宿主将隔离Owner移交自己的恢复管理器，接收方须先在有界槽强持全部Engine/原Task/source借用/身份及回执，原Owner只在明确Accepted回执后原子转移持有；拒绝、超时、回执未知均由原进程根继续强持并查询，不能在finally离栈清槽。本页最小Host默认不移交；接收方容量不足不能迫使原Owner释放或再次Factory。Dispose已故障不重试：保留原故障/Engine/Task并隔离，待宿主明确恢复或进程结束记录未确认，不能仅因Closed查询成功清除Dispose异常。

B合成来源只读持Profile，精确引用Resolve返回一次lease、Dispose记录一次归还；故障模式控制Resolve/lease释放闩锁，不Mock数值算法。消费/保存失败仍走同cleanup，保留算法结果/原业务错误由相应Owner恢复，不自动重算假装保存成功。正常A/B在全部归还断言满足后清槽；异常但已确认清理可清槽并保留失败回执，未知/移交拒绝则继续占用有限槽，容量耗尽可见拒绝新任务，不累积无界僵尸。

## 10. 可选 UI 契约

### 10.1 页面职责与 DevExpress 25.2.3 构图

UI 为可选独立 WPF Inspector，只投影当前输入/Profile/模型和支撑证据，不保存第二套批准状态。查看者可读来源和失败原因；工程员经宿主授权创建预览请求/域草稿；提交草稿由宿主再次核权，控件不能发布生产配方。核心无需 UI 初始化。PageContract 标识 `RS-Inspector-01` 的唯一正文就在本节，不新建同义页。

固定1920×1080验证视口，在屏幕内最大化测试宿主，记录实际 Window/client 与任务栏/边框/标题栏尺寸；不改显示设置。客户端顶部56 DIP显示 Surface/修订/单位/方法/Profile与主要命令，底部28 DIP状态栏；余下 DockLayoutManager 中左240 DIP域树、右320 DIP Inspector、下部180 DIP残差/问题列表，其余全部给影像/表面。尺寸为布局起点，真实客户区不足时优先折叠下部明细，不压缩主要状态与取消；用 GridLength/Star 分配影像余宽。统一宿主主题、8/16 DIP间距、清楚单位列与短标签，不新增独立主题开关或语言选择器。

| 控件/已核公开成员 | 此页职责与交互 |
|---|---|
| DockLayoutManager.LayoutRoot + LayoutGroup/LayoutPanel；BaseLayoutItem.AllowClose | 影像主面板 AllowClose=false；树/Inspector/明细可折叠且“恢复布局”可找回；布局仅保存外观，不含Profile/权限 |
| GridControl + TreeListView；DataControlBase.ItemsSource | 左侧R/X/C/T树，选择节点仅改变证据筛选，不偷偷改域；修改由宿主ROI编辑器产生完整新Domain |
| PropertyGridControl.SelectedObject；PropertyDefinitionBase.IsReadOnly=true | 右侧仅get属性的投影对象，所有属性只读；不绑定可写Profile/批准对象；编辑用宿主提供的新完整请求 |
| GridControl + TableView.ShowAutoFilterRow；DataViewBase.AllowEditing=false | 下部问题/残差按SourceIndex过滤；行选择联动影像定位、树与Inspector；反向点选定位对应来源行 |
| ChartControl.Diagram=XYDiagram2D；BarSideBySideSeries2D.DataSource/ArgumentDataMember/ValueDataMember | 固定Count/区间中心字段的R/I/J/C残差直方，不把拟合RMS单独显示为准确度；数据来源和计数见§10.5 |
| BarManager/BarContainerControl/Bar.IsStatusBar | 状态、正在计算/排空、当前对象和下一动作；关键错误保持文字可见 |
| BarItem.SuperTip=SuperTip；SuperTip.Items/SuperTipItem.Content | 在预览/提交/取消BarButtonItem直接赋SuperTip；内容随语言重建，限制/不可用原因仍在状态区可见 |

以上类型/属性已读本机25.2公开XML，来源/hash见§17；本轮额外核实BarItem.SuperTip、BarItem.Command/Content、图表系列DataSource/ArgumentDataMember/ValueDataMember、TreeListView.KeyFieldName/ParentFieldName及PropertyDefinitionBase.IsReadOnly。SuperTip直接赋给BarItem，不猜附加属性；PropertyGrid的ReadOnly摘要和值说明不一致，本页使用仅get投影+逐PropertyDefinition.IsReadOnly=true，不依赖歧义项。无dxdocs可调用，复用本机资料；不核依赖授权、不声称WPF实测。

### 10.2 独立挂接、权限与代次

UI工程绑定`src/Modules/reference-surface/Asun.Modules.ReferenceSurface.Wpf/Asun.Modules.ReferenceSurface.Wpf.csproj`，`Microsoft.NET.Sdk / net10.0-windows / UseWPF=true / Nullable=enable`，namespace `Asun.Modules.ReferenceSurface.Wpf`；仅引用Core、WPF BCL及本机25.2.3 Core/Docking/Grid/Grid.Core/PropertyGrid/Charts公开程序集，用HintPath现有程序集，不从NuGet替换。以下为W1唯一`Inspector API v0.1`声明形状（语义签名、未编译，不改变Core Module API）：

```csharp
public sealed record ReferenceInspectorPermissions(
    string Revision, DateTimeOffset ValidUntil, bool CanRead,
    bool CanPreview, bool CanEditDomains, bool CanSubmitDraft);
public sealed record ReferenceInspectorStamp(
    string AttachmentId, ulong Generation, string RequestSha256,
    string PermissionRevision);
public enum ReferenceDraftState { NotStarted, Pending, Accepted, Rejected, Unknown }
public sealed record ReferenceDraftCommand(
    string OperationId, ReferenceInspectorStamp Stamp,
    DateTimeOffset PermissionValidUntil,
    ReferenceSurfaceRequest Request, ReferenceSurfaceResult Preview);
public sealed record ReferenceDraftReceipt(
    string OperationId, ReferenceDraftState State, string? DraftRevision,
    string? ErrorCode);
public sealed record ReferenceDraftEditRequest(
    ReferenceInspectorStamp Stamp, ReferenceSurfaceRequest Current);
public sealed record ReferenceDraftEditReply(
    ReferenceInspectorStamp Stamp, ReferenceSurfaceRequest? Replacement,
    bool Cancelled, string? ErrorCode);
public interface IReferenceInspectorHostPort {
    ValueTask<ReferenceDraftEditReply> EditDomainsAsync(
        ReferenceDraftEditRequest request, CancellationToken cancellationToken);
    ValueTask<ReferenceDraftReceipt> SubmitDraftAsync(
        ReferenceDraftCommand command, CancellationToken cancellationToken);
    ValueTask<ReferenceDraftReceipt> QueryDraftAsync(
        string operationId, CancellationToken cancellationToken);
}
public sealed record ReferenceInspectorInput(
    ReferenceSurfaceRequest Request, ReferenceSurfaceResult? SavedResult,
    ResolvedReferenceProfile? SavedProfile);
public sealed record ReferenceInspectorOptions(
    TimeSpan CommandDeadline, TimeSpan CleanupObservation,
    int MaxRowsPerPage, int MaxOverlayPoints, int HistogramBins, long MaxProjectionBytes);
public enum ReferenceInspectorState {
    Empty, Ready, Busy, Cancelling, Stale, Blocked, Completed,
    RecoverableError, PermissionDenied, Detaching, Detached, DrainUnknown
}
public sealed record ReferenceInspectorIssue(string Code, string FieldPath,
    string TextKey, ImmutableArray<string> Arguments);
public sealed record ReferenceInspectorSnapshot(
    ReferenceInspectorStamp? Stamp, ReferenceInspectorState State,
    ReferenceDraftState DraftState, string? DraftOperationId,
    ReferenceSurfaceResult? Preview, ReferenceEvaluationBatch? Evaluation,
    ReferenceEngineSnapshot? Engine, long ProjectionRevision,
    ImmutableArray<ReferenceInspectorIssue> Issues, long IssueOverflowCount);
public sealed record ReferenceInspectorDomainRow(
    string Key, string? ParentKey, string Role, long PointCount,
    long CellCount, string RevisionText);
public sealed record ReferenceInspectorPointRow(
    long SourceIndex, Point3 Position, string SetRole, string? ReasonKey,
    double? DisplayResidualInInputUnit, ReferenceEvaluation? Evaluation);
public sealed record ReferenceInspectorHistogramBin(
    double CenterInInputUnit, long Count);
public enum ReferenceInspectorEvidenceSet { R, I, J, C }
[Flags] public enum ReferenceInspectorLayers {
    Surface = 1, Model = 2, FinalInliers = 4, Support = 8,
    Forbidden = 16, Unknown = 32, Hull = 64
}
public sealed record ReferenceInspectorEvidenceView(
    ReferenceInspectorEvidenceSet Set, int PageIndex, ReferenceInspectorLayers Layers,
    long? SelectedSourceIndex, long? SelectedCellId);
public sealed record ReferenceInspectorProjection(
    ReferenceInspectorStamp Stamp, long Revision,
    ImmutableArray<ReferenceInspectorDomainRow> DomainRows,
    ImmutableArray<ReferenceInspectorPointRow> PointRows,
    ImmutableArray<ReferenceInspectorHistogramBin> Histogram,
    string SelectedSetRole, int PageIndex, long TotalSetPoints,
    int VisiblePointCount, int VisibleTriangleCount, long TotalTriangleCount);
public sealed record ReferenceInspectorCompletion(
    ReferenceInspectorState State, string? ErrorCode);
public enum ReferenceInspectorPresentationState { Unattached, Pending, Applied, Failed, Released }
public sealed record ReferenceInspectorPresentationCompletion(
    ReferenceInspectorPresentationState State, long ProjectionRevision, string? ErrorCode);
public sealed record ReferenceInspectorOwnerSnapshot(
    string AttachmentId, bool OwnsEngine, bool Detached, bool Quarantined,
    int PendingTaskCount, long ChargedBytes, bool TransferAccepted,
    ImmutableArray<ReferenceInspectorIssue> Issues, long IssueOverflowCount,
    ReferenceInspectorPresentationState PresentationState, long AppliedProjectionRevision);
public interface IReferenceInspectorSession {
    event EventHandler<ReferenceInspectorSnapshot>? Changed;
    ReferenceInspectorSnapshot GetSnapshot();
    ReferenceInspectorProjection? GetProjection();
    ValueTask<ReferenceInspectorCompletion> SelectEvidenceAsync(
        ReferenceInspectorEvidenceView view, CancellationToken cancellationToken = default);
    ValueTask<ReferenceInspectorCompletion> WaitUntilPreparedAsync(CancellationToken waitCancellationToken = default);
    void ReplaceInput(ReferenceInspectorInput input);
    void UpdatePermissions(ReferenceInspectorPermissions permissions);
    ValueTask<ReferenceInspectorCompletion> PreviewAsync(CancellationToken cancellationToken = default);
    ValueTask<ReferenceInspectorCompletion> EvaluateTargetsAsync(
        ImmutableArray<ReferenceEvaluationPoint> points, HeightDistanceMode mode,
        CancellationToken cancellationToken = default);
    ValueTask<ReferenceInspectorCompletion> EditDomainsAsync(CancellationToken cancellationToken = default);
    ValueTask<ReferenceInspectorCompletion> SubmitDraftAsync(CancellationToken cancellationToken = default);
    ValueTask<ReferenceInspectorCompletion> QueryDraftAsync(CancellationToken cancellationToken = default);
    ValueTask<ReferenceInspectorCompletion> CancelAsync(CancellationToken waitCancellationToken = default);
    ValueTask<ReferenceInspectorCompletion> DetachAsync(CancellationToken waitCancellationToken = default);
}
public sealed record ReferenceInspectorRootOptions(
    int MaxOwnerSlots, long MaxHeldBytes);
public sealed record ReferenceInspectorOwnerRequest(
    string AttachmentId, ReferenceInspectorInput Input,
    ReferenceInspectorPermissions Permissions, ReferenceInspectorOptions Options,
    IReferenceInspectorHostPort Host, IReferenceSurfaceProfileSource? SavedProfileSource,
    IReferenceSurfaceEngine? BorrowedEngine, ReferenceSurfaceEngineOptions EngineOptions);
public enum ReferenceInspectorTransferState { Accepted, Rejected, Unknown }
public sealed record ReferenceInspectorTransferReceipt(
    string TransferId, ReferenceInspectorTransferState State, string? ErrorCode);
// 以下具体类型的公开签名，方法体由W1实现；不是第二套Core接口。
// public sealed class ReferenceInspectorRoot
// public ReferenceInspectorRoot(ReferenceInspectorRootOptions options);
// public ReferenceInspectorOwnerHandle Reserve(ReferenceInspectorOwnerRequest request);
// public ReferenceInspectorOwnerSnapshot Query(string attachmentId);
// public ValueTask<ReferenceInspectorTransferReceipt> TransferAsync(
//     ReferenceInspectorOwnerHandle owner, ReferenceInspectorRoot destination,
//     string transferId, CancellationToken waitCancellationToken = default);
// public sealed class ReferenceInspectorOwnerHandle
// public IReferenceInspectorSession CreateSession();
// public ReferenceInspectorOwnerSnapshot GetSnapshot();
// public ValueTask<ReferenceInspectorPresentationCompletion> WaitUntilPresentedAsync(
//     long projectionRevision, CancellationToken waitCancellationToken = default);
// public ValueTask<ReferenceInspectorCompletion> CloseAsync(CancellationToken waitCancellationToken = default);
// public sealed class ReferenceInspectorFactory
// public static ReferenceSurfaceInspector CreateControl(
//     ReferenceInspectorOwnerHandle owner, string cultureName,
//     ImmutableDictionary<string,string> textResources);
public sealed record ReferenceInspectorViewAttachment(
    ReferenceInspectorOwnerHandle Owner, IReferenceInspectorSession Session, string CultureName,
    ImmutableDictionary<string, string> TextResources);
// public sealed class ReferenceSurfaceInspector : System.Windows.Controls.UserControl
// 以下为该类型公开成员签名；类体省略，不是可编译产品代码。
// public ReferenceSurfaceInspector(); // 空Detached，只创建轻量视图骨架、不订阅/启动命令。
// public void Attach(ReferenceInspectorViewAttachment attachment);
// public void SetCulture(string cultureName, ImmutableDictionary<string,string> textResources);
// public ValueTask<ReferenceInspectorCompletion> DetachAsync(CancellationToken waitCancellationToken = default);
// public System.Windows.Input.ICommand PreviewCommand { get; }
// public System.Windows.Input.ICommand RecalculateCommand { get; }
// public System.Windows.Input.ICommand CancelCommand { get; }
// public System.Windows.Input.ICommand EditDomainsCommand { get; }
// public System.Windows.Input.ICommand SubmitDraftCommand { get; }
// public System.Windows.Input.ICommand QueryDraftCommand { get; }
// public System.Windows.Input.ICommand ResetLayoutCommand { get; }
```

Session不依赖Dispatcher/窗口初始化，内部锁串行命令接纳/代次/权限；Changed是非阻塞不可变快照通知，订阅者异常隔离并计诊断，不传WPF对象。View.Attach/SetCulture须实例Dispatcher，错线程抛InvalidOperationException且不改变原挂接；Attach只在初始Detached且Session未挂到其他View时成功，重复/替换挂接抛ArgumentException并记RS-UI-1001，不替换。一个Session最多一个View，Owner与Session必须来自同一Reserve；可无View跑独立Host测试。构造/Factory非法输入抛ArgumentException，所有运行失败用Snapshot.Issues及Completion表达，waitCancellationToken的等待取消允许OperationCanceledException但原Task仍强持。控件只拥有订阅/命令包装/DispatcherOperation，不拥有借用Engine/Host/Source；Session/Owner按§10.6关闭，控件Detach观察Session.Detach与所有Dispatcher回调退出，观察取消只结束等待，保留原任务和Detaching。

Snapshot/Issue/Projection是W1投影DTO，不纳入Core.Model/Result hash；Projection仅当前View可见页，暂存于Owner后交View，只读并有明确Revision。Domain树Key固定R/X/C/T字符串与DomainId，叶Key增加SourceIndex/CellId且全表唯一，TreeListView.KeyFieldName="Key"/ParentFieldName="ParentKey"；Grid列绑定SourceIndex/Position/SetRole/ReasonKey/DisplayResidualInInputUnit/Evaluation，图表ArgumentDataMember="CenterInInputUnit"/ValueDataMember="Count"。业务物理身份仍在Core Binding，不从树显示名反推。Session.GetSnapshot不返回可写输入集合、全量残差复制或SDK句柄。

证据查看默认R/page0/Surface|Support，无选择。SelectEvidenceAsync要求有效CanRead及已验证Result，PageIndex非负且落在集合页数内（空集合仅page0）；枚举未定义位、负ID、不属于当前页/可见三角的选择拒绝RS-UI-1001。分页、集合、图层、选择只增ProjectionRevision；使用同一有界投影worker，Busy拒绝重复，取消只撤销本次显示投影。GetProjection只返回当前Stamp/读权限仍有效的最近已完成投影，否则null，不因旧投影存在而回显。无View也可检验页和bin，不能声称已呈现。

W1内部Owner/View桥固定三步：Owner锁内捕获当前Stamp、ProjectionRevision、已验证不可变Request/Result及EvidenceView（只借引用，不复制全云）；在Owner登记的单worker构造页/bin和有界Scene源索引/CellId列表；View凭登记身份取该代投影并在Dispatcher构造/应用WPF对象。桥的RegisterView/ViewPublicationFailed/ApplyPresentation回执仅内部可见，均核Owner/View身份、Stamp及Revision；没有公开Host自报Applied入口。输入/权限变化撤销捕获与待发布投影，完成回调复核才存入GetProjection，View显示完成另按§10.7回执。场景和明细共用这一捕获，不从产品全局对象取数。

ReplaceInput和已接纳Preview各递增Session.Generation（ulong溢出需Detach新Attachment，不能回绕），RequestId使用`rsui-`+Guid.NewGuid().ToString("N")，CorrelationId保留宿主关联；RequestSha256按Core.Identity复核不含UI generation。任意输入/权限Revision变化取消当前未完成命令、使其Stamp失效；Permission同Revision不同内容拒绝，过期或撤销以更高代使旧回调不可发布。全部发布核AttachmentId/generation/requesthash/permissionrevision/权限未到期，语言/布局不改计算代。ReplaceInput在Busy时只保留1个最新替换并取消旧命令，标Stale；旧Task真实排空前不开始下次Preview，不建立隐形自动队列。输入变化不自动计算/提交。只取消共享Engine中的本Session token，不能Close它。

主命令可见：预览（Ctrl+Enter）、取消（Esc）、重新计算、提交草稿（Ctrl+S）；计算/排空中禁用重复预览与提交，取消后显示“正在排空”直到ResourcesReleased。Tab依次工具条→域树→影像→Inspector→明细，F6轮转区域；树/表/命令有稳定 `RS.*` AutomationId。空输入显示“没有参考点：选择参考域”；Stale显示“输入已变更：重新计算”；Unsupported/Unknown用独立标记与原因，不用绿色“通过”替代Succeeded。高阶参数与残差图渐进展开，关键命令不藏菜单。

### 10.3 三语与投影预算

上述ICommand仅做接纳门及原Task登记，不async void链式调用；CanExecute取Session/权限状态，在点击入口再次核门，BarItem.Command绑定同一命令实例、Content本地化。Recalculate调用PreviewAsync且新RequestId，ResetLayout只恢复Dock/相机不调用Core；查询草稿按钮仅在有OperationId的Pending/Unknown或恢复流程可见。`RS.Preview/Cancel/EditDomains/SubmitDraft/QueryDraft/DomainTree/Viewport/Inspector/PointGrid/Status`为固定AutomationId，UIA.Name/HelpText随文化取资源，表SourceIndex行的AutomationId加稳定十进制ID，不用行序号造成页变身份误认。

资源由宿主按SetCulture注入当前实例，允许扩展文化；缺资源回退该模块包随附en-US文本并形成诊断，不显示原始资源键。文本不改变数值/hash。每个错误键还绑定字段路径、影响与恢复文字，日志详情另开。最低文案基线：

| 键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Preview / SubmitDraft / Cancel | 预览 / 提交草稿 / 取消 | 預覽 / 提交草稿 / 取消 | Preview / Submit draft / Cancel |
| Draining | 正在排空：请等待资源释放 | 正在排空：請等待資源釋放 | Draining: wait for resources to be released |
| Hole | 目标处缺少支撑：补充观测 | 目標處缺少支撐：補充觀測 | No support at target: add observations |
| Stale | 输入已变更：重新计算 | 輸入已變更：重新計算 | Input changed: recalculate |
| ProfileMissing | 原参数不可用：恢复该版本参数 | 原參數不可用：恢復該版本參數 | Original profile unavailable: restore that revision |
| DraftRejected | 草稿未提交：检查权限或版本 | 草稿未提交：檢查權限或版本 | Draft not submitted: check permissions or revision |
| ReadOnly | 只读：此操作需要编辑权限 | 唯讀：此操作需要編輯權限 | Read only: editing permission is required |
| PermissionExpired | 权限已过期：重新授权 | 權限已過期：重新授權 | Permission expired: renew authorization |
| Busy | 操作未结束：等待或取消 | 操作未結束：等待或取消 | Operation is running: wait or cancel |
| OwnerCapacity | 资源槽已满：先处理未结束操作 | 資源槽已滿：先處理未結束操作 | No resource slots: resolve pending operations first |
| DispatcherFailed | 页面不可用：保留任务并关闭页面 | 頁面無法使用：保留任務並關閉頁面 | Page unavailable: retain the task and close the page |
| BindingFailed | 页面数据未显示：关闭后重新打开 | 頁面資料未顯示：關閉後重新開啟 | Page data was not displayed: close and reopen |
| DraftUnknown | 草稿状态未知：查询原操作 | 草稿狀態未知：查詢原操作 | Draft state unknown: query the original operation |
| ReceiptMismatch | 草稿回执不一致：查询原操作 | 草稿回執不一致：查詢原操作 | Draft receipt mismatch: query the original operation |
| NoCheck | 未提供检查点 | 未提供檢查點 | No check points provided |
| Empty | 没有参考点：选择参考域 | 沒有參考點：選擇參考域 | No reference points: select a reference domain |
| Completed | 计算完成：检查支撑和残差 | 計算完成：檢查支撐和殘差 | Calculation complete: inspect support and residuals |
| PresentationPending | 结果待显示：等待页面更新 | 結果待顯示：等待頁面更新 | Result display pending: wait for the page update |
| Unknown | 证据不足：补充观测 | 證據不足：補充觀測 | Insufficient evidence: add observations |
| Unsupported | 目标不受支撑：调整目标或补观测 | 目標沒有支撐：調整目標或補觀測 | Target is unsupported: adjust it or add observations |
| Cancelled | 已取消计算 | 已取消計算 | Calculation cancelled |
| TimedOut | 计算超时：等待释放后重算 | 計算逾時：等待釋放後重算 | Calculation timed out: wait for release, then recalculate |
| EditDomains / Recalculate / QueryDraft / ResetLayout | 编辑区域 / 重新计算 / 查询草稿 / 恢复布局 | 編輯區域 / 重新計算 / 查詢草稿 / 恢復版面 | Edit domains / Recalculate / Query draft / Reset layout |
| Observed / Interpolated / Extrapolated / Invalid | 已观测 / 插值 / 外推 / 无效 | 已觀測 / 內插 / 外推 / 無效 | Observed / Interpolated / Extrapolated / Invalid |
| Surface / Support / Residual / Count / Unit | 表面 / 支撑 / 残差 / 数量 / 单位 | 表面 / 支撐 / 殘差 / 數量 / 單位 | Surface / Support / Residual / Count / Unit |
| PreviewTip | 按当前参数计算预览，不发布生产配置 | 依目前參數計算預覽，不發布生產設定 | Calculate a preview using the current profile; production settings are unchanged |
| SubmitTip | 提交候选草稿；生效由宿主决定 | 提交候選草稿；啟用由宿主決定 | Submit a candidate draft; the host controls activation |
| HeightOnlyTip | 一阶和二阶曲面只支持轴向高度 | 一階與二階曲面僅支援軸向高度 | First and second order surfaces support axis height only |

UI仅绑定当前代投影，进度Dispatcher队列最多1个待处理更新（合并最新）；终态/错误按当前代单独交付不合并丢失。表格每页≤1000条，图表≤200个bin，影像叠加每次≤10000个来源点，完整事实仍在不可变Result/原资产，不为显示删证据。选择/高亮只传来源ID，不复制完整点云到ViewModel。刷新起点≤10 Hz作为工程上限而非已测流畅度；DPI、键盘、UIA、主题、三语长度与真实3D联动均在同一1920×1080验证视口实测，W1未执行、不冒称已交付。

### 10.4 命令、权限、Core挂接与错误

Root options为1..16槽、MaxHeldBytes>0；每Owner Options必须提供CommandDeadline 1 ms..24 h、CleanupObservation 1 ms..10 s、页行1..1000、Overlay点1..10000、bins1..200、ProjectionBytes>0，无生产默认值。输入仍受Core限制，root预留输入/Artifact规范编码计长、命令工作预算、最大投影预算及未来一次Core返回值预留，按§7保守charge；同Result多Session逐槽计费。槽满抛InvalidOperationException并以Data["Code"]携带`RS-UI-1002 OwnerCapacity`，Factory前发生，不丢已有槽。Root预留失败不创Session/Engine/View。UI options/hash不参与Core模型身份，不能以UI预算授权更多点或更宽外推。

输入边界：AttachmentId/permission Revision非空1..128码元；DateTimeOffset.ValidUntil必填，过期权限可挂接诊断但不读数值；Permissions内任一编辑/预览/提交true而CanRead=false拒绝矛盾。Input必有原始Request且SavedResult非空时SavedProfile必填；SavedProfileSource可选，只用于后续batch重新Resolve精确引用，不作为Attach时秘密异步配置读取。SaveResult/Request/精确Profile必须来自可信宿主、Request Identity等于Result身份，不用SavedResult掩盖当前新输入。所有局部身份字段按Core校验；Host端口非空且启动调用必须非阻塞、在短同步前导后返回ValueTask，禁止在方法入口同步等UI或设备。违例卡住的外部前导不宣称可合作取消：root隔离持调用worker Task，UI等待有限，产品Adapter须满足此契约。

Reserve只做有界形状/额度/身份标签检验不运行10M点hash，完整Core.Identity/Result闭包在Session固定单worker上执行（root最多MaxOwnerSlots个worker，无Task.Run逐点扩散）；CreateSession后台启动一项受CommandDeadline约束的Prepare Task并强持，State=Busy，命令此时Busy拒绝。SavedResult通过复算Request→Model→Evidence→Result与精确Profile一致才显示，没SavedResult准备成功Ready；非法结构Blocked，空R明确Empty。Core.Identity同步方法本身无中途取消API，worker可在调用前后检查deadline但不假称Timeout已停止该调用；原workerTask未返回root不清槽。Reserve/CreateSession可在线程池进行，View Factory只负责已经有Owner的Dispatcher对象；初始化失败不得以无初始化Session虚构Engine快照。

只允许一个投影worker：min/max+bin扫描每≤4096点检查取消/代/预算，rows/mesh分页/抽取前按实际容量charge，strings+immutable buffers+mesh positions/indices/normal每元素按§7收费，WPF mesh及Materials conservatively每顶点256/每triangle128/每material4096，同时持有旧/新场景时两者计账。64MiB是最小Host显式示例，不是默认或实测。不能分配完整数百万点Residual数组供图表，固定两遍O(N)逐项统计，不排场景之外的Core源数据。ProjectionBuilder不是第二视觉/计量后端，不创建新的Surface/模型身份。

| 命令 | 前置/公开调用/唯一输出 |
|---|---|
| Attach/打开 | Reserve→CreateSession→CreateControl；validateRequest/Profile用Core.Identity，SavedResult仅在Succeeded且Binding/Result/Profile闭包校验后显示。未知版本/缺精确Profile显示Blocked及RS-1401，允许看身份摘要不交测量，不偷偷最新Profile |
| Preview / Recalculate | CanRead+CanPreview且权限有效，无在途Session命令或未知draft；强持原Engine.ExecuteAsync(...,progress,token).AsTask；RuntimeState由StateChanged/GetSnapshot，Result只有当前Stamp且终态返回后封存至Preview。不重复调用Execute同步阻塞Dispatcher |
| EvaluateTargets | CanRead且当前已验证Preview或SavedResult，目标批次/模式/预算显式输入；使用Core.EvaluateAsync，当前Preview Profile由Session内不可变精确来源adapter供给；SavedResult使用Reserve强持的SavedProfileSource或SavedProfile值adapter，不能临时Profile替代；Values保留原顺序/有效性。Unknown/Invalid无值，不补0 |
| Edit domains | CanRead+CanEditDomains；Host.EditDomainsAsync输入当前Stamp/完整请求，只返回完整新Request或Cancelled。核Stamp/单位/索引/hash，成功走ReplaceInput并产生新代；Host不得改采集坐标/原快照或算法参数，涉及Profile修改必须由宿主显式完整ReplaceInput。只读Viewer不提供拖动修改、插件私有ROI不注入核心 |
| Submit draft | CanRead+CanSubmitDraft且当前Preview Succeeded/身份匹配、不Busy/Stale/Blocked/Unknown；生成一个Guid OperationId保存强持Command与原HostTask。Host按Stamp中权限Revision/有效期限、完整请求hash、输入修订再次栅栏，保存候选草稿。Accepted只是草稿收件，不是生产配方生效/测量PASS |
| Query draft | 同OperationId，允许撤销CanRead/CanSubmitDraft后作生命周期恢复查询，可信Host只返操作元数据、不返影像/数值或额外业务对象；不是绕过读权限的查看。账本返回Pending/Accepted/Rejected/Unknown，界面只显示必要恢复状态。超时/取消只停止观察、不能重送；Unknown/Pending阻止再次Submit和Detach清Owner；新草稿不能覆盖未知提交身份 |
| Cancel | 始终可取消自身任务，不依赖读/编辑许可；CancelAsync登记一次原CancelTask。请求发出后State=Cancelling，直到原Core任务/租约/回调真实退出后恢复Ready/Stale；提交已进入Host的副作用未知只转Unknown并保留OperationId，不显示“未提交” |
| Detach / Close | §10.6；关闭与权限无关，不依赖Dispatcher可运行。不能把View.Unloaded自动当Detach成功，短暂重排/Tab隐藏不结束Session |

Session接纳时捕获权限Revision/ValidUntil，使用TimeProvider.System UTC与单调计时建立剩余授权期限Timer；每次命令接纳、每次快照发布、每次Host调用前均重新检查DateTimeOffset.UtcNow，期限到达取消当前预览/编辑/尚未发送的提交，提升generation、State=PermissionDenied、撤销可见数值/影像，不清原Task或未知draft身份。UI没有访问控制权威，Host负责真正认证与提交栅栏；日期变化不延长本次已冻结的单调授权期限。UpdatePermissions可异线程调用锁内变更，CanRead撤销后仅保留错误/操作ID与清理状态，控件立即清读投影、不能显示上一帧。恢复读权限需新Revision显式Update，已作废结果不自动复活，ReplaceInput/Preview或重新验证Saved输入。失去提交权时已经Accepted的receipt是历史草稿事实，不静默撤销/改写。

Stamp隔离与OperationId幂等同时存在：Host.Submit同ID只允许同Command内容（Stamp/PermissionValidUntil/RequestSha256/ResultSha256）且同精确候选，已处理时返原receipt、不再次写；不同payload同ID拒绝Conflict。这仅定义Host去重语义，不新增Core canonical版本。Query Unknown可表示未找到/断连/重启账本缺失，不能证明NeverStarted；只有Accepted（候选收件）或终局Rejected且Host保证无接纳副作用才解除未知。receipt OperationId必须一致；Accepted要求非空DraftRevision/无ErrorCode，Rejected要求无DraftRevision/非空错误键，其余状态DraftRevision=null；Submit返回NotStarted仅在Host保证尚未进入接纳事务且没有副作用时有效，Session保留未启动诊断并允许新OperationID，不把断连归NotStarted。违反形状RS-UI-1104/Unknown，不猜值。PermissionValidUntil明示到Host再次栅栏，不让Host猜Session时钟。产品权限/候选Store实现及信任来源属于I1消费门。

仅一项Preview/Evaluate/Edit/Submit及普通Query在途；重复点击返回`RS-UI-1003 Busy`，不默默排队。唯一例外是Pending/Unknown提交的恢复Query：它用Owner独立且最多1个的原QueryTask槽，可在原SubmitTask未返回或Detaching/DrainUnknown时启动；Session.QueryDraft与Owner.Close复用这一槽，不互相等待Detach才查询。查询终局回执解除草稿未知仍不能删除未返回的原SubmitTask；迟到同ID矛盾回执转1104并隔离，不覆盖已知草稿事实。SelectEvidence与业务/投影在途互斥，不参与草稿恢复。Core队列满/EngineClosed/ResourceLimit原码投影为RecoverableError，释放该命令Owner后才允许重试新ID；原Task未知则DrainUnknown拒绝新业务命令。Changed/按钮异常不改Core结果；UI错误独立命名`RS-UI-1001 InvalidAttachment`、1002额度满、1003忙、1004输入过期、1005权限、1101Dispatcher不可用、1102投影/绑定失败、1103等待超时/归还未知、1104Host回执不一致。业务错误与清理错误分别记录，8条有界Issue+溢出计数（溢出摘要键），不以最后清理异常覆盖第一次业务失败。

### 10.5 只读证据投影与独立场景

唯一数据来源映射：Surface/Domain/Profile为Input.Request不可变值；Selection/ResidualSummary/SupportSummary/FitSourceIndices/FinalInlierSourceIndices/ExcludedSourceReasons/Evidence/Binding为Core Result；运行阶段为StateChanged、GetSnapshot及原Task状态；合法逐点距离与支撑Validities只能来自Core.Evaluate/EvaluateAsync。不给PropertyGrid可写生产对象，不调用私有模型句柄，不接Shell单例；Permission仅改变可执行命令，不改输入/算法/判定。提供投影统计不意味着生产计量事实。

残差直方采用公开模型重算显示值而非假造未存在的Core residual列表：从原Request构造R/I/J/C索引，P用Result.Model.Plane.Normal与Origin的公开公式§6.5，H/Q用Result.Model.Height.Chart/归一化/系数的§6.3公式；仅算显示统计，不将这些值交测量/资格或替代Result.Residuals。默认R、bins=Options.HistogramBins，扫描min/max，等值时单bin；否则宽=(max-min)/bins，index=min(bins-1,floor((r-min)/宽))、边界归右、max入最后bin，计数总和等于该集合有效点数；以两遍扫描及固定bins计数，不建全量残差数组，逐步检查deadline/预算。模型求值或bin宽/索引非有限时1102，不把溢出裁成有效值。无C则显示“未提供检查点”，不绘虚构0误差柱。因原snapshot缺失不能重算时显示现有Summary，不编造分布。来源行分页按SourceIndex，证据中J/S/Forbidden/Unknown/Hull各层可独立开关；只改外观，不授支撑。Overlay点以固定SourceIndex升序等距序号抽取（端点保留），标采样数/总数；Forbidden/Unknown面不会因点采样隐藏资格Summary。

独立包提供默认只读WPF `Viewport3D` 证据场景，不依赖另一模块未冻结3D/ROI签名、不另造视觉算子：上部切换“表面/支撑/残差”，Scene以当前Chart米坐标映射，连续三角来自Request.Surface.Cells或Result.Evidence.ContinuousCells（以SourceIndex回原Points取实际XYZ；ProjectedCell只含XY不伪造实测Z），颜色分层Observed/J、中性模型、红Forbidden、灰Unknown、橙外推；图例含文字/符号不只依赖颜色。MeshGeometry3D.Positions/TriangleIndices采用原单元顶点索引，正面按Chart CCW，DoubleSided材质；表面顶点不经过新拟合/补洞。模型面只在现有证据三角顶点用公开模型求高度做投影，不扩展成填满Hull的大板。无Cells时以有界点标记/二维Chart散点视图显示，不自动三角化；无可见点显示Empty而非空黑场景。 模型层沿Chart.HeightAxis在证据顶点XY求高度；P分母近零/无可用轴交点时只隐藏模型层并标明轴向投影不可用，原表面/证据和Core合法法向值仍保留，不更换拟合路线。IsValid=false占位Z不当实测顶点，改为XY缺测标记；Unknown/Forbidden层仅表示证据，图例说明不是补出的表面。

“DoubleSided”在此仅指`GeometryModel3D.Material`和`BackMaterial`均赋相同只读材质，不是虚构DevExpress/WPF属性。原单元重映射到Scene顶点列表的index而非直接把long SourceIndex塞TriangleIndices(int)；展示上限内checked转换及SourceIndex→int表，失败RS-UI-1102。每图层Mesh/Brush/Material生成后在对应Dispatcher对可Freeze值调用Freeze并登记Owner；Freeze失败保留对应Task/对象并报投影错误，不跨线程传可变Freezable。Scene能量/颜色是显示属性，不作为测量证据。

Viewport3D投影限10000点/20000三角（参数点上限更小时取min），不完整网格按CellId升序纳入，新增顶点将超点额或三角额前停止并显示可见/总数，不声称完整显示；保留完整数值证据。相机初始看Chart+Z，OrthographicCamera.Position=(cx,cy,zmax+max(spanXY,1e-6))、LookDirection=(0,0,-1)、UpDirection=(0,1,0)、Width=max(spanX,spanY,1e-6)*1.1；平移/滚轮缩放宽度正有限且夹在初始宽的1e-3..1e3，Reset恢复该框。空间旋转用Quaternion围绕中心，View仅负责相机，坐标数值/模型不变；投影树上SourceIndex仍能键盘定位，点选RayMeshGeometry3DHitTestResult使用VertexIndex1/2/3及VertexWeight1/2/3，取最大权重顶点映射来源（同权重取SourceIndex小者），并以本层三角表定位CellId；不是虚构单一VertexIndex，也不把命中插值位置编为新观测点。命中采样外对象不能伪造来源，禁区/未知只读。

二维Chart散点 fallback 是本模块WPF DrawingVisual只读投影，不新增图像/ROI Owner：x右、y上，fit当前包围盒，选择只定位行；Edit domains通过已冻Host端口打开宿主编辑，不在这个Scene画可写ROI。独立Host可返回确定性编辑请求；产品如需其既有高级3D/ROI控件自行适配本输入/源索引，不阻断默认独立W1内部设计。图层、模型/残差、树/表/Inspector选择共用一组SourceIndex与CellId，不能双向SelectedItem更新形成递归命令；Dispatcher有重入guard并将选择限制为显示页/可见模型。

### 10.6 根Owner、Dispatcher、关闭与移交

Root.Reserve先于Engine Factory/Session/控件构造，用§9有界强持模式：存完整输入身份、Host/Source借用、Options/permissions、原Core/Host/Cancel/Close/Dispose Task、View与待执行DispatcherOperation、投影worker Task和CTS、唯一Detach Task/TransferID；Reserve已有同AttachmentId拒绝。Owner.CreateSession仅一次；BorrowedEngine非空则只订阅/取消本Session，禁止Close/Dispose借用Engine；为空时由Owner在try内Core.Factory.Create，OwnsEngine=true，Factory/Session初始化异常都进独立有限cleanup且保留原错误。借用Host/Source从不Dispose。CreateControl在对应Dispatcher用Owner预留UI额度构造并登记PartialView，赋DataContext/绑定/订阅后才Attach；创建/绑定同步异常保留View/原Operation供清理，不能只丢stack局部变量。

外部可以用无参构造+Attach，但Attach前必须有Reserve/CreateSession的匹配Owner；无参构造只做无任务Detached骨架。CreateControl内部重复调用拒绝；初次构造/Attach失败不自动new第二个View绕过PartialView，Host先走Owner.Close并确认归还后新Attachment。Session不依赖视觉控件初始化/Dispatcher。

View订阅Changed后只存最新progress快照并最多安排1个Dispatcher.InvokeAsync(Action,Background)；终态/Issue另一个不可丢失slot、同一Attachment最多1个terminal投影，在其应用/失败回执前禁新命令；无View时投影worker完成后封存只读投影并归还通知槽，PresentationState仍Unattached，不等待不存在的View回执。原DispatcherOperation及其.Task须先登记到Owner；闭包首先检查View挂接和Stamp。Detach通过锁撤销订阅，取消投影CTS，Abort待运行Operation；Abort=false说明正在执行，继续持Task等待退出，不能假设取消Dispatcher就已释放。Changed后台线程不操作DependencyObject/DataContext，不同步InvokeDispatcher。InvokeAsync启动抛异常、Task故障/Aborted、Dispatcher.HasShutdownStarted/Finished都转RS-UI-1101，ViewPublicationFailed记录于Owner（线程安全），取消未发的命令/不提交，不把Core值标失败或Succeeded换成UI成功。

DataContext/绑定表达式必须在投影事务内：先构建只get投影对象，校验必需路径，再Dispatcher一次替换ItemsSource/SelectedObject/状态/场景；所有必需Binding设NotifyOnTargetUpdated、读BindingExpression.Status及HasError，在TargetUpdated后核对投影Revision，检查回调也是Owner记录的DispatcherOperation。更改中有Presentation guard，全部必要表达式成功后才解除guard/设置“可见ProjectionRevision”；出错保持无当前代可消费数值。绑定PathError/UpdateTargetError或必需值缺失产生RS-UI-1102，撤销整代可见值/命令、保留原Core结果/Owner；不捕获全局DispatcherUnhandledException假装恢复。异步异常由原Operation.Task观察，写Owner.Issues；Dispatcher停止后禁依赖UI显示错误，Host从Owner/Session Snapshot恢复。Session是一次性生命周期，Detach后不重新Attach；恢复先确认旧Owner清理/移交，再Reserve新Attachment/CreateSession/新View，以原不可变输入重新验证，不能重新提交旧OperationId。

Session.DetachAsync第一次原子置Detaching，停止新命令、提升generation、订阅撤销一次、取消自身原Task/投影（保存CancelAsync原Task）并等原Core/Host/edit/query/presentation Task返回；每次公开调用只有限观察内部原DetachTask，到期返Completion(DrainUnknown,RS-UI-1103)，内部Task仍未完成，不把包装Completion当实际Detached，也不重发Dispose。Repeated Detach/Owner.Close观察同一底层任务，waitCancellationToken只取消观察。已送Host提交超时仍需Query，即使原Task已结束，root必须保留OperationId/借用Host直到同ID明确Accepted/Rejected或明确移交Accepted；此时View可物理移除、Session.State=DrainUnknown，绝不使用未定义DetachedUnknown枚举。恢复查询仅由root独立维护、最多一个原QueryTask，每次显式Owner.Close/Session.QueryDraft给有限观察，不定时无限重试或扩大额度。

Owner.CloseAsync首次启动独立清理协调Task；随后每次调用有限观察同一组原Task并复核最新OwnerSnapshot，Pending/Unknown草稿额外触发最多一次显式恢复Query，不定时重试。协调Task执行以下独立步骤；若其有限观察返回DrainUnknown，后续原Task完成/同ID终局Query会在Owner锁内重新核账，满足全部条件才发布Detached并清槽，不能永久复用旧DrainUnknown包装回执或重发清理：取消本Session（独立有限观察）→观察Session真实Detach/所有ViewOperation/worker退出→若OwnsEngine再启动一次Core.CloseAsync并单独观察→嵌套finally启动一次Core.DisposeAsync并单独观察→CTS/绑定/场景Freeze资源/订阅清理核对，Session实际Detached、无未知草稿、View已退出且owned Engine.GetSnapshot=Closed/零活动/零charge后才清槽；无Engine构造失败按原Task/资源确已结束判断，不伪造Closed。借用Engine则核对本Session RequestId原Task真实返回、订阅/lease归还；可有他人active请求，不要求共享Engine全Closed。Core操作/HostTask/Dispose未完成或Dispose异常等仍root强持Quarantined、独立有限Query/观察同Task；观察Session.Detach到期或失败也不跳过owned Core.Close/Dispose阶段；各阶段取独立额度，嵌套finally发起后续阶段，Close观察失败也不跳过Dispose阶段，不覆盖首次业务错误，不重复在途Dispose。View.Detach并不私自Dispose Session借用服务，真正Owner关闭是Host Window.Close路径，未完成时关闭请求可结束窗口显示但root槽继续强持。不在Closing事件同步Wait/Result阻塞Dispatcher。

Session/控件Close都必须区分“发出取消/Detach”“观察到期”“实际归还”；无限等待不占用UI事件。实际Detach只能在清理已确认后State=Detached；未确认State=DrainUnknown，Root保留它，可查询。不让IAsyncDisposable隐式await无限任务绑到窗口退出。Host以显式Owner.Close有限token观察，在callback异常、Dispatcher停机或触发窗体关闭时使用§9嵌套finally与原Task持有模式。

Session.Detach自己的完成不依赖Engine.Close：它等待本命令及presentation退出（含Host未知草稿查询或移交），随后将只读snapshot强持转Owner历史回执；Owner再处理owned Engine。View.Detach先取消展示订阅/Operation并启动Session.Detach，两者观察并行但不能互相await对方公开包装造成循环；真实Detach底层任务只由Session锁内一次生成，ViewTask仅观察它。Owner.Close可不经过失效Dispatcher仍调用同Session.Detach，UI绑定解绑动作如Dispatcher已shutdown且其排队/执行Operation均明确终结，直接移除本模块所有事件源引用并记录展示失效；需要Dispatcher执行而尚未终结的对象仍强持，不虚构“已清理”。关闭失败后的Snapshot.Engine可null（构造未返回Engine），不能以假Open/Closed快照填充。OwnerSnapshot.Detached只在上述真实Detach完成，BorrowedEngine存在时OwnsEngine=false显式保留，不误Dispose共享引擎。

Root.TransferAsync仅在源Quarantined且目的有界额度充足时可用于恢复：同进程目的Root先预留并强持整个Owner（原Session/View/Task/服务/身份，不重建），同TransferId事务记录Accepted后原子移除源槽，目的成为唯一cleanup执行Owner；任何拒绝/取消/超时/Unknown原root继续强持，重复同ID查询同回执，不启动第二Dispose。移交是宿主技术责任，不授权产品事实或改变Session Stamp；原控件已不发布，目的只作清理/查询，不跨Dispatcher搬View使用。跨进程不支持对象移交，Host需保留本进程Owner或用独立工作进程的已冻协议，不能序列化Task假装接管；进程退出只记录未知，不能证明资源归还。

### 10.7 最小Host、工程与定向验收

绑定判断精确口径：`BindingExpressionBase.HasError`仅报告ValidationRule失败，不能单独捕获PathError；必须同时检查Status=Active、必需投影字段/Revision、TargetUpdated及HasError/Validation.HasError。纯只读Binding.Mode=OneWay，NotifyOnTargetUpdated=true，不启用TwoWay、UpdateSourceTrigger或数据源写回。未Active/AsyncRequestPending等状态不宣布已呈现；投影期限到达而仍未Active为RS-UI-1102并持原Operation观察；Detached因关闭是观察清理而非UI成功。换语言必需Binding仍走同事务，不触发数据重算，绑定回退不能静默用原文本或原数字冒充本代。

Snapshot状态映射唯一：未有Engine/Session构造失败Engine=null；R为空Empty；准备/命令原Task运行Busy，收到Cancel但未真实返回Cancelling；ReplaceInput/旧stamp失效Stale；原闭包/拓扑/版本不可用Blocked；CanRead=false/expired PermissionDenied；Core succeeded且本代结果闭包可投影为Completed（Session事实；View应用确认独立按PresentationState，仍非产品PASS）；Core rejected/failed/resource队列满为RecoverableError并保留原Code；Detached/Detaching/DrainUnknown只按真实生命周期。不为了显示Completed改变Core.Status，也不让View取消Core.Unknown。ViewProjectionRevision与Session请求generation分离，局部选择/语言/相机仅加ProjectionRevision，不能更新权限Revision或算法hash。Session根Owner在发布前自身验证快照形状，Unknown/pending原Task或receipt不可记Detached。

取消、期限、权限撤销、Detach同时到达时在Session锁内按单调观察次序冻结第一业务意图，deadline与撤销同点以撤销优先（不泄漏数值），Detach总能置停止新命令。后来的cleanup错误不改已冻结业务意图；终态Core迟到只归还原Task，仍校验Stamp/权限、不能显示新代数值。权限expired时root可查清理元数据而不能露出Preview/Evaluation，Snapshot这些字段置null但旧Result对象仍Owner强持至清理确认；恢复权限不自动恢复旧View数据。

唯一W1测试/独立Host工程为`tests/Modules/reference-surface/Asun.Modules.ReferenceSurface.Wpf.Tests/Asun.Modules.ReferenceSurface.Wpf.Tests.csproj`，`Microsoft.NET.Sdk / net10.0-windows / UseWPF=true / OutputType=Exe`；仅ProjectReference Wpf/Core与本机上述DevExpress依赖，不用产品Shell/数据库/测试NuGet。Program入口`[STAThread]`显式创建Application/Dispatcher并在finally异步退出；`--mode=height`/`--mode=volume`承载两个同样Core consumer用途，`--mode=verify`运行下表及有限Dispatcher泵，不另建第三份Host。生产工程仅Wpf目录，本轮允许写路径仍只有指导，不创建工程。 后续获准W1实现仅可写该Wpf生产目录及该Wpf.Tests测试目录；Core/既有Core.Tests、其它模块、产品Shell、数据库、厂商SDK、共享Contract/Schema及原来源禁止写入。W1需要Core变化时先提交唯一指导变更并交原Owner接收，不以UI实现反改已收契约；本轮仍仅可写本文。

```powershell
dotnet build src/Modules/reference-surface/Asun.Modules.ReferenceSurface.Wpf/Asun.Modules.ReferenceSurface.Wpf.csproj -c Release
dotnet run --project tests/Modules/reference-surface/Asun.Modules.ReferenceSurface.Wpf.Tests/Asun.Modules.ReferenceSurface.Wpf.Tests.csproj -c Release -- --mode=verify
```

最小Host顺序固定：进程根new Root(2槽/2 GiB)→输入V01/V06合成请求、显式权限/20 s有效期、Options(command2 s/cleanup1 s/page1000/overlay10000/bins200/projection64 MiB)→Root.Reserve→try中owner.CreateSession→有限WaitUntilPrepared确认Ready/Completed→对应Dispatcher上Factory.CreateControl→窗口Content=control→Run实际Preview/目标Evaluate→更新只读选择/语言。所有AsyncCommand立即把原Session Task登记Owner，以有限观察（原Task始终持有）替代async void吞异常。Host在退出finally独立调用control.Detach、owner.Close，每步最多1 s且不超过case剩余时间；一个失败不跳过后步，嵌套finally最终查询/保留Owner，不给局部await using释放责任。业务/cleanup错误分开，测试假Host操作账本按ID精确查草稿、纯值Edit Domains和受控有限闩锁，非生产Store/权限验收。

以下调用片段仅说明已冻W1签名和Owner顺序，Wpf Host中的`coreRequest/host/source/resources/points`由合成模式显式供给。Dispatcher调用的原Operation先由Owner登记再await是Factory/View内部义务；Host本身在STA线程持control，command原Task在Session内部先入Owner槽再返回；Host观察到期不删除它：

```csharp
// suiteRemaining由Host唯一suite单调钟取得；每case总额不重新续期。
var caseClock = System.Diagnostics.Stopwatch.StartNew();
var caseLimit = suiteRemaining < TimeSpan.FromSeconds(10)
    ? suiteRemaining : TimeSpan.FromSeconds(10);
TimeSpan ObserveBudget(TimeSpan maximum)
{
    var left = caseLimit - caseClock.Elapsed;
    return left <= TimeSpan.Zero ? TimeSpan.Zero : (left < maximum ? left : maximum);
}
CancellationTokenSource ObservationWait(TimeSpan maximum)
{
    var left = ObserveBudget(maximum);
    var wait = new CancellationTokenSource();
    if (left == TimeSpan.Zero) wait.Cancel();
    else wait.CancelAfter(left);
    return wait;
}
void RequireBusinessBudget()
{
    if (ObserveBudget(TimeSpan.FromSeconds(1)) == TimeSpan.Zero)
        throw new TimeoutException("Inspector case deadline.");
}
var root = new ReferenceInspectorRoot(new ReferenceInspectorRootOptions(2, 2L << 30));
var permissions = new ReferenceInspectorPermissions("permission-1",
    DateTimeOffset.UtcNow.AddSeconds(20), true, true, true, true);
var options = new ReferenceInspectorOptions(TimeSpan.FromSeconds(2),
    TimeSpan.FromSeconds(1), 1000, 10000, 200, 64L << 20);
// root必须属于Application/进程生命周期，不能仅是这个async方法的局部根。
// 此示例new的root立即登记进Host进程强持表，再允许Reserve/Factory。
processOwnerRoots.Add(root); // Host本地固定容量表，满则拒绝；不是模块公开API。
var owner = root.Reserve(new ReferenceInspectorOwnerRequest("height-view-001",
    new ReferenceInspectorInput(coreRequest, null, null), permissions, options,
    host, source, null, engineOptions)); // BorrowedEngine=null：owner创建且拥有Engine。
ReferenceSurfaceInspector? control = null;
try
{
    RequireBusinessBudget();
    var session = owner.CreateSession(); // Prepare原Task强持，不依赖View初始化。
    using var prepareWait = ObservationWait(TimeSpan.FromSeconds(2));
    var preparation = await session.WaitUntilPreparedAsync(prepareWait.Token);
    if (preparation.State != ReferenceInspectorState.Ready
        && preparation.State != ReferenceInspectorState.Completed)
        throw new InvalidOperationException("Inspector input is not prepared.");
    RequireBusinessBudget();
    control = ReferenceInspectorFactory.CreateControl(owner, "zh-CN", resources);
    window.Content = control; // 仅STA Dispatcher；绑定异常仍有PartialView原Owner。
    // 实际按钮接纳使用ICommand；无View测试用Session公开方法，先检查Ready。
    RequireBusinessBudget();
    var preview = session.PreviewAsync().AsTask(); // 原Core/SessionTask内部已强持。
    using var previewWait = ObservationWait(TimeSpan.FromSeconds(3));
    var previewCompletion = await preview.WaitAsync(previewWait.Token);
    if (previewCompletion.State != ReferenceInspectorState.Completed)
        throw new InvalidOperationException("Inspector preview is unavailable.");
    var previewPresentation = await owner.WaitUntilPresentedAsync(
        session.GetSnapshot().ProjectionRevision, previewWait.Token);
    if (previewPresentation.State != ReferenceInspectorPresentationState.Applied)
        throw new InvalidOperationException("Inspector preview was not displayed.");
    RequireBusinessBudget();
    var evaluate = session.EvaluateTargetsAsync(points,
        HeightDistanceMode.SignedAxisHeight).AsTask();
    using var evaluateWait = ObservationWait(TimeSpan.FromSeconds(3));
    var evaluationCompletion = await evaluate.WaitAsync(evaluateWait.Token);
    if (evaluationCompletion.State != ReferenceInspectorState.Completed)
        throw new InvalidOperationException("Inspector evaluation is unavailable.");
    var evaluationPresentation = await owner.WaitUntilPresentedAsync(
        session.GetSnapshot().ProjectionRevision, evaluateWait.Token);
    if (evaluationPresentation.State != ReferenceInspectorPresentationState.Applied)
        throw new InvalidOperationException("Inspector evaluation was not displayed.");
}
catch (Exception error)
{
    hostErrors.RecordBusiness(error); // 宿主有界本地错误槽，不清Owner/改Core结果。
}
finally
{
    try
    {
        if (control is not null)
        {
            using var viewWait = ObservationWait(TimeSpan.FromSeconds(1));
            var viewClose = await control.DetachAsync(viewWait.Token);
            if (viewClose.State != ReferenceInspectorState.Detached)
                hostErrors.RecordCleanup(new TimeoutException("Inspector view is not detached."));
        }
    }
    catch (Exception error) { hostErrors.RecordCleanup(error); }
    finally
    {
        try
        {
            using var ownerWait = ObservationWait(TimeSpan.FromSeconds(1));
            var ownerClose = await owner.CloseAsync(ownerWait.Token);
            if (ownerClose.State != ReferenceInspectorState.Detached)
                hostErrors.RecordCleanup(new TimeoutException("Inspector owner release is unknown."));
        }
        catch (Exception error) { hostErrors.RecordCleanup(error); }
        finally
        {
            var held = root.Query("height-view-001"); // 有界查询，归还后的零额度回执保留。
            if (!held.Detached || held.Quarantined || held.PendingTaskCount != 0
                || held.ChargedBytes != 0)
                hostErrors.RecordCleanup(new InvalidOperationException("Inspector owner is retained."));
            // 未实际Detached/清账或Quarantined，processOwnerRoots继续强持并有限恢复。
            // 不因window.Close/本方法离栈移除root，也不再次调用Engine.DisposeAsync。
        }
    }
}
```

示例两个3 s业务观察与两个1 scleanup在同case10 s/suite120 s剩余额度内截短；Prepared阶段最多取CommandDeadline2 s，但不叠加使总case超10 s。不得在STA上循环GetSnapshot等待Prepare；Host使用Changed/Task闩锁信号并有限观察，Preparing超时仍走同Owner.Close。B模式Reserve提供SavedResult/SavedProfile/精确Source，借用Engine非空时Owner仅取消本Session且不关共享Engine；同示例其他顺序不变。Query(AttachmentId)在根内最多保留MaxOwnerSlots个释放回执、同ID不重用，满时替换最旧已完全释放回执（非active/unknown），root真实资源计账与回执分离；迟到未知Task永不因回执额度挤出而丢强持。Owner内部原Task/CTS/回调强持至真实退出；Host的WaitAsync/等待CTS只观察Owner原Task，等待包装已返回后可Dispose本地等待CTS，不能把它当原Task已退出或将Host局部对象冒称已登记；Cancel/Detach/Close在wait token预先取消时仍先锁内启动一次非阻塞清理前导，再结束该次观察；Case期限已耗尽也必须发起尚未启动cleanup的非阻塞前导，然后只持原Task不等待、不强制释放。

WaitUntilPreparedAsync观察唯一PrepareTask，token取消只结束当前等待不取消共享原Task；Prepare完成后按实际校验返回Ready/Completed（SavedResult已验证）、Empty/Blocked/PermissionDenied，原PrepareTask未完保留Busy/未知诊断，不能开始业务。Facade各ValueTask的原底层Task在Owner先登记；调用者保存包装Task并有限观察不会替代底层。Core初始化构造成功与输入准备完成分别记录，前者不代表权限/证据有效。 Preview/Evaluate成功Completion在本代默认投影worker完成后返回，worker超预算/失败则保留Core事实、返回RecoverableError/1102；Session与View呈现互不冒充。SelectEvidence完成亦表示投影已备妥，若有View，下一业务命令仍须等呈现事务退出。WaitUntilPresentedAsync有限观察该Revision的原呈现事务，token只取消等待；未挂View立即Unattached，应用失败Failed，已关闭Released，当前代已改变返回Failed/1004，不挂起等待已不可能呈现的旧代。 View.Detach/Owner.Close的成功Completion.State=Detached，仅当各自真实归还条件满足；有限观察未满足则DrainUnknown，不能仅看方法已返回。

PresentationState与Session.State分开：Session.Completed仅表示当前Stamp的Core求值/结果可投影，无View测试可到Completed；View只有在Owner.PresentationState=Applied且AppliedProjectionRevision等于本代已校验投影、权限仍有效才显示“计算完成”。Factory/View桥在W1内部凭注册的Owner/View身份更新PresentationState，公开Host不能用假Ack授质量/结果有效性；Pending/Failed保持显示“结果待显示/页面不可用”及原因，Core事实不改。暂无View时Unattached，不假称已渲染；真正View.Detach退出后Released，未退出仍Pending/Failed并root強持。绑定事务/Frame测量记录应用Revision，不依赖一次Changed通知就宣布UI显示完成。

| UI用例 | 输入/操作 | 可判定断言 |
|---|---|---|
| RS-U01 正常A/B | V01高度与V06孔洞，各自Root/Session，Preview→Evaluate→三语切换 | 同Core状态/距离，Unknown/Invalid不填0；树/表/场景SourceIndex联动，语言不重算/清草稿；消费者只依赖公开W1/Core |
| RS-U02 再入/队列满 | 同Session双Preview，Root槽满、共享Core队列满 | 第二命令Busy、不造原Task；槽满Factory调用0；Core1301原码可见且不丢旧结果Owner，不默排队 |
| RS-U03 过期/撤销/输入改 | Task暂停后ReplaceInput/Permissions撤销/过期，放开迟到Task | 新Stamp失效旧值，不发布/提交；CanRead=false立即清影像/数字，仍取消/查询/清理；同Revision不同权限拒绝 |
| RS-U04 草稿未知 | Host Submit原Task迟滞/receipt错ID/Unknown，撤销提交权后Query | OperationId不变、Submit次数1；只查询不重送；权限栅栏在Host，Accepted是候选草稿非放行；unknown不清槽 |
| RS-U05 关闭竞态 | Preview/Evaluate/Edit/Submit/Query各阶段关闭，Cancel或Close观察到期 | 原Task/root强持，重复Detach同底层任务，View晚通知无发布；共享Engine不Close，owned Dispose次数≤1；嵌套finally均执行 |
| RS-U06 Dispatcher/Binding故障 | InvokeAsync pending→Abort，running→Abort=false、Dispatcher shutdown、必需PathError | 观察原Operation.Task，无同步UI等待；Issue1101/1102保持原业务错误及Core结果，故障无数值/UI假成功；旧投影退出后可显式恢复 |
| RS-U07 资源/移交 | 投影额度不足、禁区mesh/页上限、RootTransfer拒绝/未知/接受 | 边界明显标采样/不足不删事实；拒绝源继续强持查询；接受后唯一目的Owner，原Task/身份保留且不再Dispose一次 |
| RS-U08 键盘/UIA/1920 | 单1920×1080固定screen内客户区，当前OS DPI/任务栏；Tab/F6/Esc/CtrlEnter/CtrlS和三语 | 命令/树/表/状态AutomationId稳定，无重叠/截断关键文本；F6焦点不落隐藏面板，Esc只Cancel不提交；View.Empty/Blocked/Error非空白 |
| RS-U09 证据/图表 | V01平面/无Cells、V02 H/Q、V06禁区/Unknown/Hull和C缺失 | 实际canvas/Viewport非空且包围盒正确、reset/缩放可用、选点ID一致，bin计数总和正确、Q不显示“法向最短距离”；不以凸包填洞 |
| RS-U10 构造/消费异常 | Factory/控件初始化/Host消费/绑定异常，Cancel/Close/Dispose同时异常或超时 | Factory前槽强持，finally每步有限；原异常保留，原Task未完/Dispose故障不得清槽，迟到不提交；触发恢复后确认资源才返0 |

每UI case总期限10 s（含Dispatcher/cleanup/恢复）；suite120 s；外隔离测试进程180 s，全部通过才0，任一未执行/超时/unknown归还非零；这些是软件测试防挂预算非客户性能目标。受控任务/Dispatcher闩锁1 s内放开，不随机Sleep或永久锁死电脑；外停止进程不证明归还。不得把Core测试Exe当WPF验收、无View Session测试当真实界面通过。仅1920×1080视口；不跑其他分辨率矩阵或改用户显示。 Host返回码须汇总业务/cleanup错误槽及最终Owner/root计账；示例记录的DrainUnknown、未Applied或仍强持都属于该case非零，不以catch吞异常继续执行当通过。

W1 Benchmark沿§13/DEV-GOV-010公共统计口径，冻结输入/hash/主题/语言/OS DPI/客户区、冷/热/两Session/页数/overlay/triangles/bins/权限变化与取消/关闭故障组；测点Command接纳→Core ResourcesReleased→投影worker完成→Dispatcher Operation Task完成→可见ProjectionRevision→View.Detach→Owner归还，分别记录渲染/Dispatcher队列延时及投影/mesh/强持slot/GC峰值，不能把Core末端当首屏显示。P50/P95/P99/n与超时/删失/权限拒绝分列，未知资源不判性能通过；客户响应/刷新阈值待Profile采纳，不编达标数字。内部UI上限1个progress+1个terminal通知、1000行/10000点/20000三角/200 bins/64 MiB示例预算已冻，额度预留失败显示RS-UI-1002、投影运行超预算显示RS-UI-1102而非丢源证据。数值精度/HIL/计量/质量资格不由W1提升。

W1与DEV-GOV-010十二项的定位如下，只导航本文正文，不新增权威或准入结论：

| 项 | W1唯一定位 |
|---|---|
| 1 任务 | §10.1角色/预览与草稿边界；RS-Inspector-01 |
| 2 输入 | §10.2 Input/权限/Options、§10.4校验与精确Profile |
| 3 输出 | §10.2 Snapshot/Projection/Receipt、§10.7计算与呈现分离 |
| 4 前置 | §10.4权限/期限/Owner额度/Prepare、无未知提交 |
| 5 算法 | Core算法沿§6不变；§10.5仅证据投影/两遍bin/真实三角 |
| 6 参数 | §10.2/4有效域、§10.3/5有界页/叠加/相机；不推荐生产参数 |
| 7 组合 | §10.4 Core/Host端口、§10.6 own/borrow/Dispatcher/移交 |
| 8 页面 | §10.1–3布局/DevExpress/三语/键盘/UIA及§10.5场景 |
| 9 异常 | §10.4错误/未知回执、§10.6–7关闭/绑定/恢复与保留 |
| 10 样例 | §10.7 A高度/B孔洞合成Host及RS-U01～U10 |
| 11 验收 | §10.7真实视口/有限预算/Benchmark；客户目标未采纳为NotEvaluated |
| 12 落点 | §10.2 Wpf工程、§10.7唯一Wpf.Tests/命令/允许禁止路径/调用示例 |

这些规格定位已获主控2026-10-10内容接收，W1内部设计欠账已闭合；W1保持PreparationIncomplete / NotReady，真实WPF/25.2.3/1920×1080/三语/UIA/性能及受影响I1接线资格未执行。Core六项准入沿附录原接收，不将带UI的W1标为ModuleCoreImplementationReady或ImplementationSpecificationReady。

## 11. 正常、边界和失败案例

| 案例 | 期望结果 |
|---|---|
| 平面点有充分二维展开、独立检查通过 | `Succeeded`，返回 P 模型、完整残差和支持域 |
| 坡面上有独立凸起 | 凸起保留为残差/排除证据；不得被静默当板弯删除 |
| 点数相同但几乎共线 | `Rejected + RS-1102 RankDeficient`，不授可靠参考 |
| 目标位于大孔洞内、凸包包围 | `Rejected` 或目标 `Unsupported`；凸包不替代局部支撑 |
| 仅单侧环带/一个角落支持 | 记录覆盖和外推原因；未满足 Profile 时拒识 |
| Q 环带点数足够但设计矩阵欠秩 | `RS-1102 RankDeficient`，不回退 P、不补洞 |
| 整体翻转 `(n,d)` | `dn` 变号；指定轴高度在相同轴方向下保持一致 |
| 参考域与目标域修订不同 | `RS-1004 DomainConflict` |
| 取消发生在数值计算中 | 停止后续阶段；当前确定性计算退出并归还工作集后返回 `Cancelled`，迟到进度/结果丢弃 |
| deadline 到达且当前计算尚未退出 | `DeadlineReached` 诊断，保持 `Draining`，不写缓存；当前计算退出并归还工作集后才终态 `TimedOut` |
| 缓存只匹配 FOV 名称 | `RS-1401 CacheStale`，重新计算 |
| 固定 TLS/QR 运算产生 NaN/Inf 或不收敛 | `RS-1201 NumericalFailure` 或 `RS-1202 ResultValidationFailed`；不得切换算法、重试到通过或发布模型 |

### 11.1 固定数学向量（仅合成软件语义）

统一测试Profile：输入Meter，None、MinimumPoints/Retained P/H=3、Q=6、MaximumExcludedRatio=0；Numerical为`(0.01,1e-6,1e6,0.1,2)`；Support为`(minimumPoints,1,null,2,0,true,false,1,null,null,1e-10)`，字段次序依§4.2。Chart原点及XYZ单位轴、ReferenceDirection=+Z、TargetMode=SignedAxisHeight、无未声明X/C/T、Overlap=false；SurfaceId=`vNN`、Revision=1、Frame=`synthetic-meter`、采集/标定引用均`synthetic-vNN`、Cell.EvidenceReference同该字符串，ProfileId=`test-method-vNN`、Revision=`1`，所有Points有效、SourceValidityCode=null。DomainId按R/X/C/T各角色命名，domain修订1，hash依§8.1现算。执行预算10 s/64 MiB，测试实例1并发/1排队/1000点/2000单元/1000求值点/256 MiB。不同例外在表中明确并重算Profile/hash；比较公差1e-10 m/系数、单位法向分量1e-10来自合成双精度oracle，非客户准确度。

| 向量 | 完整构造与预期 |
|---|---|
| RS-V01 P正常/轴差 | R0点索引0..2：(0,0,2),(1,0,2),(0,1,2)；连续Cell0=(0,1,2)，R0包含全点/该单元，无X/C/T。n=(0,0,1)，d=-2 m，μ=(1/3,1/3,2)，R/I/J均3、RMS≈0、面积比1。Evaluate (0.25,0.25,2.005)为Interpolated/Supported，轴高+0.005m、交点(0.25,0.25,2)；法向模式同距离。 |
| RS-V02 H与Q | 9个网格点(x,y)∈{-1,0,1}²，SourceIndex=3*(y+1)+(x+1)；H z=2+0.3x-0.4y，Q z再加0.1x²+0.05xy+0.2y²；每网格小方格按左下到右上对角线拆两个连续三角，全部R0。cx=cy=0、sx=sy=1；H系数(2,.3,-.4)，Q(2,.3,-.4,.1,.05,.2) m；点(0,0,2.005)轴差.005、Observed；Q法向模式返回RS-1404且距离null。 |
| RS-V03 Q圆环欠秩 | 8点(u,v)=(cos(jπ/4),sin(jπ/4))、z=2、j0..7；MinimumAreaRatio=null、Cells空。关系u²+v²≈1导致数值秩不足，Rejected+RS-1102，无P回退；只有点数不能通过。 |
| RS-V04 裁剪/独立检查 | V02 H的9点改成全z=2，仅中心索引4为2.003；FixedClipOnce=.001、MinimumRetained=3、MaximumExcludedRatio=.2、无单元且MinimumAreaRatio=null。首候选截距2+.003/9，中心排除；I/J为其余8点、最终截距2，FitRms≈0，CandidateRms=.001、MaxAbs=.003、P95=.003（全9点nearest-rank）。C另索引9=(.5,.5,2.002)，RequireIndependentCheck=true、CheckRms/P95上限.001、MinimumIndependentCheckPoints=1时Rejected+RS-1103。另变体C=null、RequireIndependentCheck=false、两Check阈值=null时Succeeded但Uncertainty unavailable。 |
| RS-V05 裁剪非高离群恢复 | V02 H的中心改z=20、其余8点z=2，clip=.001、其他同V04。候选偏移2 m，全部点越门、I空，RS-1101；不偷偷RANSAC/放宽/最低点拟合。 |
| RS-V06 孔洞重开 | R0为4×4网格(x,y)∈{0,1,2,3}²、z=2，每方格两个三角。中央方格[1,2]²两单元IsContinuous=false；其余连续。MinimumAreaRatio=.8、外推距离.5、比例1。面积比8/9；点(1.5,1.5,2.005) Invalid，无值；删掉中央单元的独立变体在该点Unknown；位置(3.25,1.5,2.005)有资格时Extrapolated。封存/重开三种状态不变，不能把洞当外部预测。 |
| RS-V07 翻转与退化 | V01改ReferenceDirection=-Z，新请求得n=-Z,d=+2，法向距-.005、同+Z轴高仍+.005；P组三点(0,0,2),(1,0,2),(2,0,2)共线，RS-1102。Height轴与U共线、单位混用或域Revision≠1则在拟合前拒绝。 |

Profile并非当前点自动推荐。参数变化只通过明确新Profile请求；同数据clip或MinimumAreaRatio改变产生新ParameterSha256/RequestSha256并按新资格重新计算，显示/语言变化不改模型身份。上述纯数学预期本轮已按公式复核，不表示托管TLS/QR代码或客户样本已运行。

### 11.2 canonical固定向量

ComputeSurfaceSha256 输入：SurfaceId=`s`、Revision=1、CoordinateFrameId=`f`、Unit=Meter（枚举0）、Points为V01三点且IsValid=true/SourceValidityCode=null、Cells为空、ContentSha256为空（自身字段排除）、AcquisitionReference=`a`、CalibrationReference=`c`。按§8.1规范编码应为 **720 bytes**，SHA256=`00fc9930a1ad57ef1f0ff5445b71908713e8ef42f4e757b07c0da54948c7f33f`。本轮以两种独立字段拼接复算一致；它验证编码定义，不是产品C#测试。输入Points逆序经规范排序摘要不变；X=-0改+0摘要不变；IsValid/单元/标定/单位/Revision变更摘要改变；模型系数顺序绝不排序。§12实现测试必须重建该向量而非抄常量当计算结果。

主控2026-10-10另从公开声明字段独立重建rs-binary-v1 Surface向量，确认720 bytes及上述SHA256一致；仅为编码规格复算，不表示产品C#编译/运行或算法/现场资格已通过，canonical规则与向量值未改。

## 12. 测试矩阵与验收断言

测试必须覆盖核心固定纯托管实现和两个真实规划消费者；参考计算不能被 Mock 或另一套算法替代，Simulator 只能证明软件链，不能冒充实机资格。

| ID | 范围 | 断言 |
|---|---|---|
| RS-T01 | Contract 格式 | 缺字段、非法枚举、混合单位、重复索引被拒绝 |
| RS-T02 | 数值有限性 | NaN/Inf/溢出、零方向、负预算形成明确错误码 |
| RS-T03 | P Golden | 已知平面恢复法向/`d`，符号按方向确定，残差可复现 |
| RS-T04 | P 几何退化 | 窄线、单角、单侧环带分别拒识或 Unknown |
| RS-T05 | H Golden | 高度轴、基底、系数和轴残差与参考实现一致 |
| RS-T06 | Q Golden | 六项系数顺序、中心/尺度、满秩和预测域一致 |
| RS-T07 | 离群 | 候选、实际 refit、最终门内、原始全体计数分开且索引可追溯 |
| RS-T08 | 独立/留出检查 | 检查点不参与拟合、剔点或模型选择；分别报告 fit 与 held-out 残差，失败不被内点 RMS 掩盖 |
| RS-T09 | 补偿 | `dn`、轴高、交点和翻转不变量正确；分母不稳定拒绝 |
| RS-T10 | 孔洞/外推 | 凸包内部大洞不授支持；目标逐点返回 Observed/Interpolated/Extrapolated/Invalid/Unknown |
| RS-T11 | Profile 重开 | 原 Profile 内容哈希匹配才可求值；缺失、错绑、被替换或调用方扩大策略均拒绝 |
| RS-T12 | 取消/超时 | 不发布成功结果；当前计算退出后才 `Drained`，工作集和 Profile 租约归还后才 `ResourcesReleased` |
| RS-T13 | 并发 | 两请求互不串参数、缓存或事件；迟到结果不能覆盖新修订 |
| RS-T14 | 资源 | 点数、工作内存上限触发 `RS-1301`；工作集和输入租约在所有路径归还 |
| RS-T15 | 回放兼容 | 相同输入/参数/版本可重放；缺输入、方法或 Profile 闭包的旧结果只能查看、不能重新求值 |
| RS-T16 | 不确定度 | 无足够噪声/模型假设时返回 `IsAvailable=false` 和限制，不把 RMS 冒称总不确定度 |
| RS-T17 | 固定数值算法 | TLS/Jacobi 与 H/Q/QR 的退化、收敛、有限性、排序和 Golden 结果；不含运行时算法切换 |
| RS-T18 | 第二消费者 | 高度计量和通用体积/表面工具只依赖公开值类型，不引用制程私有类型 |
| RS-T19 | 重复/有界调度 | 以闩锁暂停A在Preparing，提交同ID得RS-1403无RequestAccepted；队列容量1时B入队、C得RS-1301；取消B后额度归零且A仍运行，释放A才终态 |
| RS-T20 | Factory/Owner/Close等待取消 | 两Host先由进程root预留槽，再在try内Factory；容量满不调用Factory、Factory抛异常不遗留Engine但仍清自有CTS。A暂停时Close置Closing，新入口RS-1402；有限观察取消只结束等待，原业务Task/Close Task/Engine强持。Close失败或启动抛异常仍进入dispose嵌套finally；Dispose启动计数至多1。放开A后原Task完成、Dispose成功、Closed/零额度及CTS清理确认才清槽；同步Evaluate控制点也使Close等待。每case含cleanup≤10 s |
| RS-T21 | 来源迟到/Dispose未知/移交拒绝 | B source忽略token、原Evaluate Task未完时WaitAsync结束不清槽，来源借用/身份仍强持；推进到DrainUnknown无终态，放开后lease归还一次、原Task空Values/TimedOut。DisposeTask在途时恢复只观察同Task、计数1；Dispose故障/同步抛异常即使查询Closed也不清槽。移交回执Rejected/Timeout/Unknown时原Owner保持强持并查询；接受方先强持才可移交。未知用1 s观察片并在10 s case剩余额度内放开故障闩锁，不真的永远挂起 |
| RS-T22 | callback/消费异常与错误保持 | 回调异常计数增长且另一订阅者有序；A/B消费抛业务异常，同时注入cancel回调失败、Close失败/超时、Dispose失败/超时，三段独立观察及最终Reconcile均执行。错误回执保留原业务异常，cleanup分别记录不覆盖；未知或归还未确认槽仍占用、无晚到提交、进程非零，正常/异常但确认清理的槽才归还。断言每case10 s/suite120 s/外进程180 s，超时非零、不以测试进程终止证明释放 |
| RS-T23 | 身份/支持篡改 | 720-byte固定向量、逆序/-0不变；改ForbiddenCells/UnknownCells/Profile/Chart/系数即旧hash验证失败RS-1401；缺任意成功绑定字段禁止求值，旧算法未知版本不可默读 |
| RS-T24 | 批量比例/有效输入 | V06 Profile以新请求明确改比例.4，再同时求1外部点与1内部支持点，外推项变Invalid、支持项仍有效、batch Succeeded；IsValid=false无0值，空batch RS-1001不Resolve，五类Validity计数之和等于全部T |

最低验收断言：无 UI 可执行；取消、超时、排空可观测；原始表面不变；失败不产生成功缓存；两个消费者在各自用途 Profile 下能独立解释 `SupportSummary` 和 `ReferenceEvaluation`。

RS-T01～T24按§1.3唯一BCL Exe执行，真实Core算法不能替换为Mock；几何/QR oracle使用本页向量与独立解析公式。测试闩锁可暂停阶段，不改实际求解；超时使用同一单调时钟抽象，不使用随机Sleep形成证据。资源测试设小charge上限而非真的把用户电脑内存耗尽。重复取消/关闭以及100轮成功/拒绝/重开交替后GetSnapshot无活动项、RetainedCharge=0；资源未知例必须最终放开并验证清理，否则该例失败。两个消费者软件模式各自有显式Profile、独立引擎与来源，A取消不改B，B拒识不改A；真实消费者资格单列，不把这两个合成模式冒称客户集成。

## 13. 性能、资源与可观测性

### 13.1 BenchmarkProfile与阈值来源

统计定义引用[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)，不另建分位算法。测量方法已冻结，客户时延/资源目标值待消费者Profile采纳；此前无来源的200 ms/1 s/2 s建议已撤去，不作为通过线。诊断测量目标缺失时为NotEvaluated，不能宣称达标。

执行Profile必须含：ProfileId/修订/hash、输入/标定/域/Profile/算法版本、硬件/OS/.NET版本与GC模式、P/H/Q、None/FixedClipOnce、点数{3/6,10³,10⁵,10⁶}及显式上限附近、连续单元数量/形状/孔洞比、拒识与噪声/退化组、T点数、单点/批量求值、cold新进程/warm同实例、并发{1,实例上限}、队列负载、预热数、测量数/最低有效数、有限Deadline、所有charge/真实内存上限及来源、P50/P95/P99目标/来源、异常处理。相同Profile/输入用于所有可行路线比较，不把H轴差与P法向距离误当相同测量对象。

测点：接纳（含排队起点）、开始验证、哈希/拓扑/索引准备、候选、refit、R/I/J/C重算、支撑、目标求值、结果复制、Drained、ResourcesReleased；端到端到ResourcesReleased，另记取消请求→观察→Drained→ResourcesReleased。每次只记录时长/集合计数/charge/峰值资源，P50/P95/P99在样本集合上算；单请求日志不造该请求“P99”。真实GC heap与分配增量、进程峰值工作集、输入/工作/输出并存charge、队列与租约峰值都计，不用logical charge冒充实测内存。

deadline超时/失败/拒识/未知排空/删失样本均保留身份与类别，按公共口径列明，不只挑成功样本。目标缺失时仍检查硬budget不越界和真实资源释放；DrainUnknown永不判性能通过。长期软件诊断负载至少在冻结Profile中给明确次数/时长与停止条件，本指导测试的100轮只证明计账闭合，不代替数小时客户Soak。性能真实测量与同样本HALCON对比本轮未执行。

### 13.2 诊断字段

每次请求至少记录：RequestId/CorrelationId、事件Sequence、阶段测点、输入/域/Profile/算法身份、R0/R/I/J/C/T及排除计数、数值秩/λ/κ1与原因、charge/资源释放时刻、取消/超时/回调异常、错误码、模型与Evidence hash。Core通过结果、StateChanged/Progress/GetSnapshot交付，宿主诊断Owner负责持久化/限额；首片不注入未定义diagnostics接口。数值诊断详细数组如未公开，不允许从实现私有状态偷取给产品，只在受测工程内部断言或按版本扩充公开DTO。日志不写完整点云/私密数据，需要原件引用回放资产ID。样本组统计另输出n和分位，不写“单次请求P99”。

## 14. 发布、回退和第二消费者

### 14.1 发布门

发布包必须提供核心 DLL、契约/Schema 版本、错误码目录、Profile 样例、Golden 向量、回放清单、依赖版本和变更记录。发布前通过文档阶段自审、契约三层验证、测试矩阵、资源/取消/排空检查和两个消费者接入演练；没有真实硬件/Golden/现场证据时，包状态只能是 `Prep` 或 `SoftwareVerified`。

### 14.2 回退

宿主按 `ContractVersion + AlgorithmVersion + ProfileReference.ContentSha256` 选择实现，保留上一 major 的 Core 与回放资产。新版本出现符号、系数、支撑或性能回归时：

1. 停止新版本结果进入生产事实；
2. 保留失败请求、输入哈希和诊断；
3. 切回上一个已登记版本；
4. 用同一回放向量比较差异；
5. 未经 Contract Owner 和用途 Owner 采纳，不改写历史结果。

### 14.3 第二消费者接入断言

第二消费者应为独立的通用表面计量/体积工具，使用另一宿主和另一 UI/服务入口。它只引用本模块公开的 `ReferenceSurfaceRequest/Result/Evaluation` 和诊断，不引用任何板件、焊盘、胶路、工单或产品私有类型。其验收至少包括：同一参考模型可在不同目标域上重新评估；目标域变化不会命中旧用途资格；失败/Unknown 不被下游转换为 PASS；取消和排空不影响另一消费者的请求。

## 15. 当前待采纳项与自审结论

以下真实执行、产品集成与资格门按对应阶段由Owner关闭，不阻断已接收的RS-C1～C4规格；RS-C4双Host生命周期窄修已获主控接收：

- 正式 `ContractId/SchemaId`、状态/Owner、错误码注册和提交绑定；
- P/H/Q 的客户用途 Profile、物理参考/覆盖/检查阈值及真实单位与样本；本指导数值参数类型/有效域和固定算法已定义，不等于客户数值采纳；
- 固定纯托管算法的真实C#编译与数值Golden/Replay执行；Jacobi/QR顺序、停止条件、有限性与结果不变量按§6实施，不再留给开发者选；
- 两个消费者的真实输入、用途资格、性能设备和 Golden 样本；
- WPF可选独立包按§10定义Inspector API、Owner/View桥、默认只读Viewport3D及独立Host；BarItem.SuperTip公开挂接已核。W1规格内容已主控2026-10-10接收，内部设计欠账已闭合，PreparationIncomplete / NotReady保持，双STA与三语字段/上游消费影响已在§18收口，真实1920×1080 WPF/DevExpress绑定、UIA/三语/两用途与性能执行另验；产品视口/ROI适配、正式本地化/权限Owner接线为I1受影响消费门，不再作为独立默认场景的未定义内部接口。

自审确认：无制程判定/质量放行/设备或数据库写权；Core API、P/H/Q算法、canonical及§9无UI Host保持0.3.2-prep基线。主控2026-10-10窄复核§9.1–3的有界根Owner槽、Factory异常、原Task、独立有限cleanup/嵌套finally、在途Dispose只观察、迟到来源/移交拒绝及T20～22、10/120/180 s预算，确认RS-C4六项规格缺口闭合并恢复ModuleCoreImplementationReady（仅规格准备）；RS-C1～C3原接收不变。主控另独立复算720-byte向量/hash一致。W1两轮有限规格自审已修正授权期限、撤权查询、Detach恢复不可重用、Prepare等待、case剩余预算、计算/呈现分离、恢复查询不被原Submit/Detach堵住和三角命中公开成员；§10是唯一实施正文，规格内容已主控2026-10-10接收，内部设计欠账已闭合。RS-W1仍PreparationIncomplete / NotReady，RS-I1原门保留，模块仍DesignReview / Prep，不声称代码、运行或生产通过。 2026-10-11完整批准范围结论与本轮增量自审见§19；原算法/API/向量与Root/Close复用，不再等总控内容审核。

## HALCON 26.05 算子资料入口

核验替代算法候选和算子边界时，使用项目内 [halcon算子手册/operators](../../../halcon算子手册/operators/) 作为 HALCON 26.05 资料入口（该相对路径从本模块目录回到仓库根三层，已定向核对）。首发Core不调用AsunImage/HALCON；矩阵可行路线与未执行比较门见§17，算法替换须先修订指导/版本，不能把可行路线研究误当运行时任选。

## 16. 第二轮场景驱动架构复审

本节是对本指导的反例复审结果。每个场景都必须能在无 UI 的最小宿主中重放；“拟合成功”只表示得到一个数学模型，不能替代物理支撑、用途资格、质量放行或设备动作。场景中的参数只能来自请求绑定的 `ReferenceMethodProfile`、`SupportPolicy`、`ExecutionBudget`、输入快照和固定算法版本；不能从当前 UI、全局配方或上一次请求读取。

### 16.1 场景处理总规则

每个请求固定执行以下顺序：

1. 接纳前检查固定上限、活动ID和队列/预算；已接纳后校验版本/哈希/单位/坐标/域/方法，失败不得进入拟合。
2. 登记活动RequestId和显式预算、持有不可变输入引用；无外部表面lease接口，不虚构它。原始点/掩码/域分母不可变。
3. 生成有来源索引的工作集，分开原始无效、先验X、域外和算法离群；材料/台阶只能由宿主显式X/连续性证据表达，不生成隐藏语义分类。
4. 按显式方法路线执行候选、门控、一次最终重拟合和全集合重算；不以“直到通过”为停止条件。
5. 独立检查支持、秩/条件、孔洞、外推和目标适用性；允许模型成功但目标部分不可用。
6. 构造不可变结果；算法/核心回调退出才Drained，工作集/来源lease释放才ResourcesReleased，随后唯一终态；异常同样走此链。

### 16.2 关键场景矩阵

| 场景 | 输入与参数来源 | 处理顺序 | 输出与状态/错误 | 恢复动作 | 可判定验收 |
|---|---|---|---|---|---|
| 正常配置/执行 | 同一 `SurfaceSnapshot` 的 R/X/C/T 域；P/H/Q Profile、方向和预算均有哈希 | 校验→R裁切→候选→固定 I 重拟合→全 R/I/J/C 残差→支持/目标评估 | `Completed/Succeeded`；模型、来源索引、残差、支持摘要和版本闭包齐全 | 调用方按用途消费；模块不写生产事实 | 相同输入、参数、算法版本回放得到相同模型哈希和集合角色；原始快照字节不变 |
| 空输入 | 点列表为空、全点无效、R 与 T 为空；参数仍完整 | 在数值拟合前检查点数/有效分母 | `Rejected + RS-1101`；无模型、无缓存写入 | 修复采集/域；不得返回 z=0、单位法向或旧 FOV 模型 | 结果明确指出空阶段和原因；重试使用新快照/域修订 |
| 部分成功 | 模型支持充分但T含洞/外部点；C缺失且非必需 | 先完成模型/SupportEvidence，再逐目标评估 | Completed可含TargetSupportStatus.Unsupported/Unknown，不产生PASS | 由宿主补观测/检查 | 支持分母不因跳过目标改变，不支持项无距离 |
| 歧义/错误输入 | R 与 T 自依赖、混合单位、域修订不一致、参考方向零向量、方法/Profile 不匹配 | 结构/语义校验即停止 | `Rejected + RS-1001/1002/1004`；不进入数值拟合 | 修正请求并生成新 `RequestId`；不沿用旧结果 | 日志含字段、域和修复建议；没有部分模型或成功缓存 |
| 噪声/遮挡/退化 | 有限噪声、遮挡、凸起、窄线、单侧环带、Q 圆环/两线；阈值来自 Profile | 保留 R0/X/T/C；按固定 robust 路线生成 I；一次 refit；独立资格 | 可能 `Completed`（模型但目标 Unknown）或 `Rejected + RS-1101/1102/1103`；列出剔除原因 | 补采样、换已批准方法或缩小声明域；禁止无限放宽阈值、补洞、自动降阶 | 坡面上的独立凸起仍可见；窄线不授 P；Q 欠秩不回退 P；所有计数和原索引可追溯 |
| 超大输入/高并发 | 点数、候选目标和并发达到预算上限；多个请求共享只读源但参数不同 | 入队前预估工作内存；按实例并发上限排队；每请求独立工作集 | 超限 `RS-1301`；排队取消 `RS-1303`；不发生参数串扰 | 调用方拆分并生成派生快照，或等待资源；不得静默降采样/删目标 | 峰值工作内存、队列长度可观测；两并发请求结果哈希互不影响 |
| 取消/超时/计算排空 | 取消发生在排队、拟合或 refit 中；Deadline 来自请求 | 停止新阶段与结果发布→等待当前计算返回→`Draining → Drained`→清理并归还资源→`ResourcesReleased` | `Cancelled + RS-1303` 或 `TimedOut + RS-1302`，仅在 `ResourcesReleased` 后作为终态发布；迟到结果丢弃 | 调用方等待 `Drained → ResourcesReleased` 后再复用租约；可用新请求重算 | 取消期间不写成功缓存、不发布 Completed、不提前释放计算仍在使用的工作集；另一请求不受影响 |
| 资源上限 | 工作集/输出/拓扑charge达到上限 | 分配前检查，停止新阶段并排空 | 已接纳Failed+RS-1301，接纳前Rejected；无降级 | 新输入/预算明确重试 | 阶段/预算/已用量可查，排空后归还 |
| 持久化/版本修订 | 结果要保存或重开；输入、Profile、算法版本有 hash；Surface/域发生新 Revision | 先验证闭包和完整写入临时记录，再由外部存储原子提交；新修订使旧目标资格失效 | 缺字段/哈希 `RS-1401`；旧模型可只读查看但不可用于新请求 | 用原快照和明确版本回放；新修订重新计算，不覆盖历史 | 掉电/半写记录不被读取为成功；读取不查 latest；新 Revision 不命中旧资格缓存 |
| Profile 来源失配 | 精确来源缺失/错ID/修订/hash，或新Profile冒充旧值 | 解析精确引用并校验完整绑定，无求值策略覆盖参数 | Unevaluated+RS-1401，不用latest/default | 恢复原Profile，策略变化新Execute请求 | 改变旧策略被拒，来源lease真实释放 |
| 局部有效性 | 观测/插值/外推/断层/缺域点混合 | 按§6.6优先级逐点及完整分母汇总 | 五类Validity，不填有效0值 | 补观测或显式新请求，无隐式全局替代 | 计数/原因/AffectedSourceIndices可追溯，宿主映射业务目标 |
| 残差与不确定度 | 拟合点、最终门内点和独立留出点分离；噪声/预测假设可能缺失 | 先冻结拟合与留出集合，再分别重算残差；无充分假设不计算总不确定度 | Fit/FinalInlier/HeldOut 残差分开；`Uncertainty.IsAvailable=false` 时列限制 | 补独立检查或重新声明 Profile；不能把 RMS 改名为准确度/总不确定度 | 留出点未参与拟合/选模；缺假设时没有伪造不确定度数值 |
| 升级/回退 | 新旧契约 major、算法版本、系数顺序、符号、支撑规则或性能行为不同 | 预加载新 Core 版本→同一回放向量比较→Contract/用途 Owner 采纳→切换；失败立即停用新版本 | 不兼容 `RS-1401` 或显式 major 错误；回退保留历史结果 | 按版本闭包回到上一登记版本；保留差异诊断，禁止改写旧结果 | 同一向量能区分模型/符号/资格变化；回退后旧消费者仍可解释原结果 |
| 无 UI 调用 | 仅注入 snapshot、域、Profile、诊断和 CancellationToken | 使用 `ExecuteAsync` 或短任务 `Execute`；不创建窗口/Dispatcher | 返回不可变 Result；状态和错误完全由契约表达 | 宿主按错误码重试、换输入或终止流程 | 在服务/回放最小宿主中无 UI 运行；无静态当前配方、隐藏初始化或数据库依赖 |
| 可选 UI | UI 仅提供域选择、方法/Profile 显示、预览草稿和取消；核心仍由同一入口执行 | 编辑生成新请求修订→预览→异步结果核代→应用由宿主发布流程处理 | UI 显示 `Rejected/Unknown/Draining` 原因；不显示为“通过” | 操作者按原因补区域/检查支撑；取消时显示排空 | 拖动不改原快照；晚到预览不覆盖新代；三语文字说明事实、影响和下一步 |
| 第二消费者 | 另一通用表面/体积工具使用不同宿主、不同目标域和用途 Profile | 读取公开值类型和证据；重新做逐目标资格和下游量测 | 同一模型可复用，但资格按目标重新计算；失败/Unknown 原样传递 | 第二消费者独立重试；不要求第一个消费者在线 | 不引用产品/制程私有类型；目标域改变不会命中旧用途资格；取消 A 不影响 B |
| 长期运行 | Profile给出有限次数/时长、重复取消、Artifact重开 | Core有界队列/活动表；宿主缓存另限额 | 每请求完整终态，健康不替代结果 | 按冻结停止条件结束，不无限重试 | 资源无单调增长，最终额度归零；重启不伪造旧操作释放 |

### 16.3 方法路线、备用、训练和恢复条件

| 路线 | 首选处理 | 允许备用/恢复 | 明确不支持 |
|---|---|---|---|
| P `PlaneTls` | 候选 R→确定性等权 TLS→固定 I refit→全 R/I/J/C 重算；法向按 `ReferenceDirection` 定向 | 无算法替代。确定性数值失败或秩/支撑不足即拒绝；修正输入后由调用方提交新请求 | 不把最低点、HALCON primitive、加权路线或单位平面当作 P 成功 |
| H `HeightFirstOrder` | 固定高度轴和中心/尺度，以三项基函数、确定性双精度 QR 拟合；轴残差独立计量 | 无算法替代；数值或输出验证失败即拒绝，不自动重试或切换实现 | 不把 H 当正交平面，不用 HALCON Region/Image 拟合冒充点云路线，不把 H 结果自动选择积分方向 |
| Q `HeightSecondOrder` | 固定六项基底、固定中心/尺度；先满秩/条件检查，再确定性双精度 QR 拟合 | 无算法替代；欠秩、预测域未知或用途未采纳时拒识；P 只能由调用方显式发起独立请求 | 不支持任意阶、B 样条、HALCON Region/Image 拟合替代、自动选阶、补洞、一般曲面最短法向、在线调参到通过 |
| 训练/自适应 | 本模块不训练模型、不更新 Profile、不从生产结果学习 | 若未来需要校准/学习，必须在模块外形成版本化离线资产，经资格流程后作为新的 Profile 输入；回放可验证但不在线改变 | 不支持在线训练、跨请求共享可变参数、AI 赋予参考资格、用模型分数替代支撑证据 |
| 数值恢复 | 保留请求、输入 hash、参数和数值诊断；固定算法只执行请求定义的阶段 | 失败返回 `RS-1201/RS-1202`；修复输入或以新参数/Profile 明确提交新请求 | 无实现路线切换、无同请求换算法重试；不使用旧模型或零模型，不把失败包装成成功 |

### 16.4 持久化、审计和事实所有权

模块只产生不可变计算结果和诊断，不拥有数据库或结果 Store。外部持久化适配器至少保存：请求/关联 ID、输入和域 hash、Contract/Schema major、完整冻结 Profile 内容及 `ProfileReference`、算法版本、R0/X/T/C/I/J 角色和原索引、模型规范、Observed/Interpolated/Extrapolated/Invalid/Unknown 原因、不确定度可用性、状态终态、排空完成时间及错误摘要。保存流程必须是“写临时记录→校验完整性→原子提交→回读”，提交失败不得返回成功事实；Artifact、原始请求和 Profile 不得分开提交后再猜测绑定关系。

修订关系按以下规则处理：

- 新 `SurfaceSnapshot.Revision` 或内容 hash 使依赖它的模型和目标资格失效；旧结果保留为历史，不删除、不覆盖。
- 仅语言、视口或显示布局变化不使模型失效；参数、方向、域、方法或标定变化必须重新计算相应层级。
- 模型缓存与逐目标资格缓存分层；模型命中不代表目标资格命中。
- 结果缺少版本闭包、原索引、Profile 原文或排空记录时，只能回放查看，不能重新用于计量或下游事实；不能声称已完整重建原始请求。

### 16.5 第二轮复审的边界结论

本模块仍不支持：自动判断物理板面、制程目标关联、工艺阈值、质量放行、设备触发/运动/灯光、数据库提交、在线训练、任意高阶/一般曲面、跨孔洞补面、未经资格的外推、未登记方法自动回退和把体积/积分结果写回参考面。高度、翘曲、体积和表面计量宿主必须各自声明物理含义、用途 Profile、目标域和结果 Owner。

两轮有限自审按§4–14的当前契约执行，发现并关闭：第一轮H/Q求值套P公式、残差集合/指标缺失、Profile未进入API、重复deadline/无界调度；第二轮重开丢失禁止/未知支撑、坐标/方向只存hash无法恢复、循环摘要、同步求值漏Close、未知来源释放与宿主消费异常。整改直接落在本文，无第二份活动契约/报告。§16场景表是当前流程的案例导航，冲突处以§4–14精确字段/算法为准，不额外定义“材料未知”输入或AI策略。

模块整体仍为DesignReview / Prep；RS-C1～C3原规格接收保留，RS-C4的§9/T20～22窄修经主控接收，恢复ModuleCoreImplementationReady（仅规格准备）。W1本轮两轮规格自审按§10完成，Session/Owner/Host/默认场景和RS-U01～U10均可定位，已获主控2026-10-10规格内容接收，内部设计欠账已闭合；W1保持PreparationIncomplete / NotReady。真实C#构建/Golden/两消费者集成、HALCON同输入比较、WPF/性能/HIL/计量/现场资格均未执行。正式平台Contract/Schema/Owner/存储事务和客户阈值仅阻断受影响Integration/Qualification，不反过来要求无副作用Core猜产品事实。 本轮全部批准范围的软件设计结论见§19，含输入消费、无源拒绝、上游条件装配、独立显示及双STA，不以此段旧Core/W1接收替代全范围核实。
## 17. 已核依据、可迁移强项与限制

本轮复用2026-10-09实际阅读的目标版官方页、固定GitHub源码/测试和本机公开XML；未重复全篇来源审阅、未复制第三方产品代码。没有以README/星数/营销作为生产证据。 W1在2026-10-10定向补读本机公开XML及下列Microsoft .NET 10/WPF官方API，仅核成员与行为，不将资料阅读列为运行验证。

| 固定来源 | 已读能力/强项 | 本模块采纳与限制 |
|---|---|---|
| HALCON26.05官方本地[create_matrix](../../../halcon算子手册/operators/create_matrix.html)、[svd_matrix](../../../halcon算子手册/operators/svd_matrix.html)、[solve_matrix](../../../halcon算子手册/operators/solve_matrix.html)、[clear_matrix](../../../halcon算子手册/operators/clear_matrix.html) | create接收行优先任意实矩阵，svd输出降序奇异值/可选向量；solve general最小二乘以SVD求解，Epsilon截断奇异值，即使欠秩也能返回解；clear使矩阵句柄失效 | XYZ设计矩阵可行，不能声称HALCON缺该能力。模块要求欠秩拒识，若后续使用solve须独立检查秩、不能把截断解当满秩；持有所有生成矩阵并经cv2归还，不直连HOperatorSet。当前无此adapter/运行时切换。 |
| [Open3D PointCloudSegmentation.cpp](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/geometry/PointCloudSegmentation.cpp)；[PointCloud测试](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/tests/geometry/PointCloud.cpp) | commit b6c5e196384ad71e75b6e6f9c5da22d046221f1d；MIT；源依赖Eigen/TBB。候选先采样、原索引保留、种子与已知平面/退化参数测试 | 采纳原索引/集合/重算断言；GetPlaneFromPoints以最大余子式法向，不普遍等于最小特征向量TLS；final_inliers在最终refit前选，不能冒称本模块J。无源码复制/生产Open3D依赖，测试未运行。 |
| [NumPy polyutils._fit](https://github.com/numpy/numpy/blob/0532af47d6a815298b7841de00bdbc547104b237/numpy/polynomial/polyutils.py)；[polynomial测试](https://github.com/numpy/numpy/blob/0532af47d6a815298b7841de00bdbc547104b237/numpy/polynomial/tests/test_polynomial.py) | commit0532af47d6a815298b7841de00bdbc547104b237；BSD-3-Clause，NumPy/BLAS/LAPACK数值依赖。列范数缩放、lstsq秩/残差、权重与非法输入测试 | 采纳列缩放、秩/边界测试思路；原件是1D多项式/SVD、支持权重/动态阶，不是本模块双变量固定基底QR；不引入Python运行依赖，不照搬其警告后继续返回解行为。 |
| [.NET合作取消](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads) | 取消是请求，listener自行观察；CancellationTokenSource需Dispose | §5/7真实退出才释放；取消不是强杀/资源已归还证据。该文不证明外部ProfileSource一定响应，未知路径显式保留。 |
| DevExpress25.2随程序集公开XML | 已核DockLayoutManager.LayoutRoot/BaseLayoutItem.AllowClose、TreeListView.KeyFieldName/ParentFieldName、PropertyDefinitionBase.IsReadOnly、ChartControl.Diagram/XYDiagram2D/BarSideBySideSeries2D.DataSource/ArgumentDataMember/ValueDataMember、BarItem.Command/Content/SuperTip及SuperTip.Items/Content | §10按任务构图与直接挂接，不猜宿主私有接口。默认独立WPF只读场景已定义；仅查公开资料，不核许可证/安装、不改版本；真实WPF/DevExpress绑定与呈现尚未执行。 |
| WPF [.NET 10 Dispatcher.InvokeAsync](https://learn.microsoft.com/en-us/dotnet/api/system.windows.threading.dispatcher.invokeasync?view=windowsdesktop-10.0)、[DispatcherOperation.Abort](https://learn.microsoft.com/en-us/dotnet/api/system.windows.threading.dispatcheroperation.abort?view=windowsdesktop-10.0) | 异步异常经原Operation.Task观察；已执行操作Abort可false | §10.6保存原Operation/Task，有限观察不冒称已退出；同步usage异常另保留。未运行Dispatcher故障测试。 |
| WPF [.NET 10 HasError](https://learn.microsoft.com/en-us/dotnet/api/system.windows.data.bindingexpressionbase.haserror?view=windowsdesktop-10.0)、[BindingStatus](https://learn.microsoft.com/en-us/dotnet/api/system.windows.data.bindingstatus?view=windowsdesktop-10.0)、[NotifyOnTargetUpdated](https://learn.microsoft.com/en-us/dotnet/api/system.windows.data.binding.notifyontargetupdated?view=windowsdesktop-10.0) | HasError是validation失败；Status含PathError/UpdateTargetError；NotifyOnTargetUpdated=true才产生TargetUpdated | §10.6–7同时核Status、必需字段/Revision及更新事件，计算与呈现分离。资料不证明已正确挂接事件/全部绑定。 |
| WPF [.NET 10 MeshGeometry3D](https://learn.microsoft.com/en-us/dotnet/api/system.windows.media.media3d.meshgeometry3d?view=windowsdesktop-10.0)、[GeometryModel3D.BackMaterial](https://learn.microsoft.com/en-us/dotnet/api/system.windows.media.media3d.geometrymodel3d.backmaterial?view=windowsdesktop-10.0)、[RayMeshGeometry3DHitTestResult](https://learn.microsoft.com/en-us/dotnet/api/system.windows.media.media3d.raymeshgeometry3dhittestresult?view=windowsdesktop-10.0) | Positions/TriangleIndices、CCW正面；BackMaterial默认null；三顶点Index1/2/3及Weight1/2/3 | §10.5来源索引重映射、双面只读材质、确定性命中映射，不拟合/补洞。未验证实际场景、性能或计量。 |

上述源码读取SHA256：Open3D算法`44487a05b6f3b70a4da2a856220638b60e4c483350572d098fc1ea4c073d7751`、测试`b8041cb7d6f5ad0a60e2ef136d580c1a8c21704cea7aeced1b3398fdbc7241b1`；NumPy helper `99011ade80b3f57f9dd4768d757929049cd7586ce0638d960cc8c93a7f7cf0ef`、测试`3e2fd7e9385fc6055b833c809eedc57324c852fa4bf443714526a7c948e0a27f`。来源license原文同commit已读，仅研究思想，无复制交付；不据此证明当前Core正确或最快。

DevExpress公开资料根：`C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/`。实际已读文件及SHA256为：Docking.v25.2.xml=`b11b45dd7afc27b5e16b679a6a9e2e4291ecd13cb1f8e1b7c0fbe4e94a64477f`；Grid.v25.2.xml=`7537e3db16162155eda70058baccf40a6731f6dc9851ad31d382332c39c3d6bd`；Grid.v25.2.Core.xml=`9ca164e53a54e5bc0eb6432a709e95c9295e60db3b0eac4fabf6dd32604b8eba`；Core.v25.2.xml=`cf99d297b336a80f2361fa8bb79369434a6a10b9426efa670d636803433e8196`；PropertyGrid.v25.2.xml=`0e0cb8a0503889f13cd86fa4d5db7cbb975c9c4f4506dfea8d681f68fc4a65c9`；Charts.v25.2.xml=`2e80660ea0316294482e5b45096cc23c52250243e12551e84c117f692445bfb0`，文件名均带`DevExpress.Xpf.`前缀。官方网页含v25.2参数访问403、会话无dxdocs工具；使用本机资料已关闭上述成员核对，本轮BarItem.SuperTip等挂接公开成员已定向补核，未核宿主私有API不用于默认独立W1。

已保留AOI来源：`H:/docs/40-development/41-vision-platform/03-calibration-imaging/板弯与局部参考补偿开发指导.md`，71880 bytes，SHA256=`6429a7b3b0fc98e161468f762f38213a5da562aebd1cde10be84d895b7811efc`。沿用2026-10-06定向读取结论：采纳精确Profile重开、局部有效性、编码高度来源、不确定度 unavailable；不迁入AOI板级编排/CAS/客户阈值/动态选模或24.11 API。来源保持只读，没有第二份活动指导。

已冻结的首发路线裁决：托管P/H/Q使用同一不可变输入与独立Core生命周期；HALCON矩阵SVD是可行比较候选，其公开资料并不冻结与本模块QR/Jacobi同一舍入/停止/线程/排空语义。首发路线是既有主控固定决定，不以“非点云接口”排除矩阵，不宣称托管最快/准确率更高。后续若提出替换，必须按§13同样本比较正确性/误接受与拒识、R/I/J/C、支撑状态、P50/P95/P99、真实峰值/排空、参数自动化与有限性，读取实际26.05语义并通过cv2，不核算子是否存在。当前没有同输入实测，不能据资料选择新后端；外部比较门不虚构已通过，也不授权当前范围新增adapter。

## 18. 完整范围的输入消费、上游版本与独立显示装配

### 18.1 当前装配边界与来源要求

当前批准范围为§1的参考建立、P/H/Q、一次裁剪、R/I/J/C残差、支撑/用途资格、类型化高度校正、重开及§10可选Inspector。当前没有本模块HALCON拟合Adapter、surface-data H调用、通用文件导入/存储codec或viewport WPF装配的执行入口。它们不能因为架构表列“HALCON适配端口”就成为本模块第二算法/后端。§3/8.3/17的首发路线裁决保持；HALCON矩阵路线是后续替换比较候选，物理阈值与运行资格门不用于撤销已冻结软件算法。

本模块外部输入边界是完整不可变`SurfaceSnapshot`及§4请求值。§18.2是已规划表面输入的宿主消费配方，不新增模块DLL、Factory、可变缓存或第二套Core DTO；当前Core.Tests仍仅BCL，不因此引用上游程序集。实际数据Producer/用途Host执行上游读取和映射，本模块实现Owner执行现有Identity/请求/结果验证。Producer提供的AcquisitionReference、CalibrationReference必须定位准确原始资产、修订及坐标/来源闭包，不能填未获信任的文件名或以本模块新hash冒充原资产身份。转换必须在调用Core/Session之前完成并计宿主预算；Core或View都不在Prepare中秘密调用采集/存储/坐标服务。

当前批准的参数自动化边界已确定：§4.2全部物理/数值门均显式Profile输入，无隐式生产默认，无自动裁剪阈值/选阶/外推/噪声估计或调到通过。FixedClipOnce只是按冻结门限执行一次，不是参数推荐。§10只提供读参数、编辑域的宿主入口和新完整输入替换，不提供参数寻优；软件资源/页/bin上限不得冒充客户目标。本模块未获批自动参数搜索或不确定度传播切片，不为字段的可扩展性提前设计执行API。当前不确定度输出沿§6.4固定unavailable，范围外噪声/相关性/标定传播不能由后续程序员猜公式。

### 18.2 surface-data 0.6.0-prep C1–C5的确定值映射

只读依据为[IM-031 surface-data §2–5、16–19](../surface-data/DEVELOPMENT-GUIDE.md)。其C1–C5公开消费接口在0.6.0-prep保持；本模块`rs-api-0.1`不因此改版本。应用读取时用`Asun.Modules.SurfaceData`与`Asun.Modules.ReferenceSurface`别名明确类型，不强转同名enum、Frame或Surface。以下映射只适用调用方显式选定的一层/范围；不扁平化多层、不自动选最高/最低面、不从C5权重反算不存在的物理参考。

固定顺序：

1. Producer冻结一条准确SurfaceDescriptor、Range、原资产/标定引用、用途域/连续性证据、坐标Frame及预算。调用上游`Validate`、`Plan`，错误或IssuesTruncated不得当有效；顶点请求FieldIds取唯一Height字段（HeightField）或X/Y/Z字段按此序（PointCloud/Mesh），`Selection=PreserveAll`、`ReadCoordinates=true`，TargetFrame必填、generation有效，不按ValidPositions偷偷缩小R0分母。TargetFrame/Transform只按上游§3.1同Frame或准确转换规则构造。
2. Host在上游StartRead前预留自己有界原operation/暂存槽与所有副本预算，再调用`StartRead(request,consumer,token)`。保存原Operation/Completion/descriptor/generation；consumer在OnBlock内只短时复制Ordinals、SourceIndices、Positions及需要的来源/控制值，不异步保存Span/ref struct或等待该operation。块暂存不能进入Core或UI。
3. 接收块须核OperationId/generation/准确descriptor/CoordinateFrame，按上游Ordinal定位源，SourceIndex全程Int64；跨块检查重复，不能转double再转回。不重复应用字段Scale/Bias/单位倍率：Positions已由上游解码和显式坐标桥给出，同一Frame单位只能按下表逐项映射。
4. 顶点原Completion只有Outcome=Completed、Completeness=Complete（合法请求为空时Empty）、Errors为空且IssuesTruncated=false、完整Requested/Delivered计数及当前绑定相等才可采用；上游RequestedBytes/FullBuffers各自保原Integrity事实，不把范围读升级为整资产验证，NotVerified拒绝映射。若需连续面积，另以明确Face请求（Domain=Face、FieldIds为唯一TriangleIndices、ReadCoordinates=false、TargetFrame/Transform=null、Selection=PreserveAll）读取完整相应TriangleIndices/Face来源，两个请求均完成且来自同一冻结descriptor才合并；部分/取消/超时/失败使整份暂存失效，不靠早到块拼成功快照。
5. 逐点/逐单元执行下表限制，然后构造§4的不可变值，调用现有ComputeSurfaceSha256/ComputeDomainSha256/ComputeProfileSha256及Request Identity。新快照hash表达转换后的内容，不能改写上游buffer/manifest/原测量hash。未能保留来源或有效性语义时拒绝整份映射，不给旧参考/0平面回退。
6. Host借用上游service，不关闭他人实例；只取消自己的operation并观察同一Completion。自己创建的上游service按其Close契约有限观察；仍未排空/lease未知时保原operation及根账，不交新Core请求。Core和W1关闭仍只处理已有本模块Owner，不私自接管上游lease。

| 输入/问题 | 本模块消费规则 |
|---|---|
| Unit | SD.Meter(1)→RS.Meter(0)，SD.Millimeter(2)→RS.Millimeter(1)，SD.Micrometer(3)→RS.Micrometer(2)，显式switch；未知值拒绝RS-1002。使用Positions的原单位，本模块内部再按§4/6转米 |
| Surface/Frame身份 | SurfaceId=选定SD.Key.Id、Revision=Key.Revision；CoordinateFrameId固定`sd-frame:`+CoordinateFrame.Id+`:`+Revision的InvariantCulture十进制。单位另由强类型字段绑定；Id可含冒号，末段revision仅十进制，不从名称猜坐标。Chart/Direction须由准确同Frame用途Profile提供，不用默认+Z/identity掩盖缺标定 |
| 有效Observed | Position.State=Valid、Origin条目准确存在且Kind=Observed、XYZ有限，才在此桥置IsValid=true。SourceValidityCode保`sd:state=<原byte>;reason=<原uint>;origin=<原int>`（全部InvariantCulture）；原asset来源闭包由AcquisitionReference保留。Observed是来源声明，仍不证明物理板面/标定合格 |
| 显式Invalid | 仅当可信Producer另有该样本准确有限XY/三维定位时保该位置、IsValid=false及原原因；有限占位高度按§4.1不参与拟合。上游Positions未提供可知位置时拒绝RS-1001，不从邻点/显示像素反推物理XY |
| Unknown/派生来源 | 本桥不得把Unknown置Invalid以抹去未知，也不得把Interpolated/Repaired/Filtered/Cad/Fallback2D置Observed。需要纳入的任一点缺精确可消费来源时拒绝映射RS-1401，保原SD状态/Origin引用供Host诊断；不用丢点缩分母。使用其它已声明纯值输入仍须遵守其Producer的物理证据，不能以本桥拒绝为由改Core算法/旧事实 |
| HeightField | 父像素offset/旋转/单位/高度恢复全由上游ReadCoordinates/准确Mapping负责；本桥不再计算pitch、ZScale或补点。没有Cells则只能显式离散Profile，MinimumAreaRatio=null、不能声称连续面积/洞内插值。以像素栅格自行三角化不属于本桥 |
| TriangleMesh | TriangleIndices是载体vertex ordinal，先以完整Ordinal→SourceIndex表映射A/B/C；不是把ordinal当Root。CellId取准确Face SourceIndex，同层不得重复/负数；连续性bool和EvidenceReference必须由上游拓扑/物理Owner提供逐Face明确声明，MeshReport通过不替代物理连续证据。仅有三角而无该声明时拒绝所请求连续用途，不默认true或隐式忽略拓扑 |
| R/X/C/T | Host按原SourceIndex/CellId声明完整域、SurfaceRevision及独立性；SD C5的多父权重/Origin摘要不能代替本模块域或独立检查。无精确目标/物理参考声明时本模块不能选择板面或重建关联 |

Face PackedValues只按其FieldDescriptor.Encoding.Type与Layout.ByteOrder读取tight每面3个UInt32/UInt64（BCL BinaryPrimitives对应大小端ReadUInt32/ReadUInt64）；Scale=1/Bias=0、无padding，checked核offset/总长/索引≤long.MaxValue/vertex范围/三个索引不同，不拿PositionValue或float解码结构列。通过完整Ordinal→SourceIndex表查引用，Vertex/Face source根分别保Producer绑定，不混同。IsContinuous与EvidenceReference准确匹配CellId及原Face声明；R/X/C/T需要的顶点/单元必须全部在本冻结输入，缺任一项RS-1004，不自动裁面补齐。

Host副本额度在Start前checked估算并预留：点暂存/不可变副本各按128*N、单元各64*F、Ordinal/SourceIndex表16*N及排序/唯一检查副本16*N，全部字符串按2*码元+64、每数组64，预留同时存在的两份点/单元及上游Plan.ResidentUpperBound和本模块Request.Budget，不以单块大小隐藏全快照。N/F均不超Core Options、单数组可表示，任一限额/剩余deadline不足在复制/调用Core前拒绝；资源/身份校验不成功不得先调用Preview再补查。此为保守逻辑账，实际CLR/GC峰值另按§18.5验，不代替硬内存目标。Host只在原operation真实退出、暂存放弃或交付明确新所有者后归还自己的槽。

此桥是保守且可拒绝的消费规则，不要求上游把所有表面来源改成Observed，也不修改其C1–C5状态/贡献算法。若业务选择派生表面作为新的数学参考，必须由其领域Owner明确新用途/来源事实并按现有完整纯值请求交接；不能在这个观察来源桥静默提升证据。上游错误保其原Code/Path/Ordinal/Detail；输入映射错误按RS-1001/1002/1003/1004/1401，生命周期Timeout/Cancelled/资源分别RS-1302/1303/1301。没有RS结果时只给Host失败诊断，不伪造ReferenceSurfaceResult或称Core已接纳。

### 18.3 H与codec新装配的条件影响

当前reference-surface指导没有`SurfaceImageLibFactory`/`ISurfaceImageLibPort`/`SurfaceMetadataCodec`/`SurfaceAdaptersFactory`直接执行路径；尚无本模块产品/测试工程。当前Host示例只有纯值输入，不需要H运行绑定或格式注册。H1/2/3属于surface-data，不与本模块H一阶回归混称；上游H返回成功不改变本模块Profile/物理资格。

若输入Producer实际采用上游H，其调用必须按SD §17.1–4使用三参数`SurfaceImageLibFactory.Create(adapterBudget,time,runtimeBinding)`，精确WorkerExecutable/WorkerSha256/AsunImageSha256、commit/wire预算和`NativeAccuracyPolicy`由部署/用途Owner提供。H1 real往返float32不可默认为无损；0阈值表示精确往返，超限或闭区间筛选集合变化拒绝，不放宽用途Profile。H2也核单位往返；只在NativeReply.Completed/Output非空/ResourcesReleased及准确frame/slot绑定满足后采用CPU原值，不采用native量化坐标。返回SourceIndex/Origin仍受§18.2，不因nativeCompleted变Observed；未知worker/pipe清理归上游原Root，本模块不创建/杀其进程或复制HALCON算子流程。这里冻结消费前置，不新增本模块native Adapter。

若Replay/输入Host选择SD新codec，按SD §18.1–3准确Decode/Validate→scope+Id到ObjectRef→StoredSource→原C1–C5读取；新`surface-metadata/1`、`surface-raw-buffer/1`的完整VersionRef/hash及有界validator必须先加入宿主ResolvedStorageConfiguration.FormatValidators。未知schema拒绝，回退用准确旧包+旧adapter+旧manifest/原buffer，不能改旧bytes或从文件扩展名猜格式。存储/资产Owner负责可信发布、权限/保留和原子提交，本模块只接成功读取后的准确纯值。SD metadata不包含本模块Model/Result/Profile闭包，不能用它充当RS Artifact codec；RS的`rs-binary-v1`也只是值身份编码，不是对SD manifest的导入格式。RS Artifact重开继续沿§8/16.4完整绑定及原平台Schema门，不新增通用序列化器/存储写权。

### 18.4 W1显示依赖与双STA确定执行

本模块W1当前直接使用§10的WPF Viewport3D/DrawingVisual与DevExpress25.2.3图表，未装配IM-060 viewport WPF DLL/Presenter/Lifetime；因此viewport `0.3.4-prep §10.6～10.9 Assembly v0.2`迁移不适用于当前直接消费。不能为了“同步上游”强加第二Presenter、虚构lease/Unbind或重写已接收Root/Close。如果未来宿主选择其高级视口，须先明确新的实际binding消费范围并修本指导装配章节；现有只读默认场景不依赖该选择，也不授设备/质量权限。

RS-U01/U05/U06/U08/U10的双STA执行在唯一Wpf.Tests Exe中确定为：主入口[STAThread]只创建一次Application（ShutdownMode=ShutdownMode.OnExplicitShutdown）；A高度Window在主Dispatcher，B体积/孔洞Window在显式Thread上SetApartmentState(ApartmentState.STA)，线程体通过SynchronizationContext.SetSynchronizationContext(new DispatcherSynchronizationContext(Dispatcher.CurrentDispatcher))设置后Dispatcher.Run。B不再new Application，两个Window/Control均在自己的Dispatcher构造与访问；各自ReferenceInspectorRoot/Owner/Session、输入、权限、借用服务和CTS独立，Host进程有界根表保两Root。Thread不是Task.Run线程池，不能在跨线程Continuation中直接CreateControl。两线程各自构造ResourceDictionary/控件/可变Brush，只有冻结文本值和不可变Core输入可共享；使用同一冻结宿主主题，不在A/B模块修改Application全局主题资源。

主协调器用TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously)接每个STA的Ready/实际呈现/Detach退出回执，先登记原Task/DispatcherOperation；异线程只调Session线程安全API或在对应Owner登记InvokeAsync后调用View，不同步Invoke/Join/Wait/Result。所有等待取同case剩余预算；失败仍各自独立有限Detach/Owner.Close。正常确认ViewOperation退出后在B Dispatcher.BeginInvokeShutdown(DispatcherPriority.Background)并观察原线程退出信号；A最后Application.Shutdown。Dispatcher已停但原Task/lease未知时只隔离持根，不能用线程退出给Detached授信。任一STA/原Task/Owner归还未确认，整个verify返回非零，不阻塞窗口消息泵。两个模式各自独立进程也执行，不能只测共享进程后宣称独立引用成立。

已定向核Microsoft .NET10官方[Application](https://learn.microsoft.com/en-us/dotnet/api/system.windows.application?view=windowsdesktop-10.0)（每AppDomain一个实例）、[ShutdownMode](https://learn.microsoft.com/en-us/dotnet/api/system.windows.shutdownmode?view=windowsdesktop-10.0)（OnExplicitShutdown）、[BeginInvokeShutdown](https://learn.microsoft.com/en-us/dotnet/api/system.windows.threading.dispatcher.begininvokeshutdown?view=windowsdesktop-10.0)（必填DispatcherPriority）及[Thread.SetApartmentState](https://learn.microsoft.com/en-us/dotnet/api/system.threading.thread.setapartmentstate?view=net-10.0)（Windows入口）。仅为新双STA构造语义依据，不重复Root/Close研究，不声称已运行WPF。

真实UI仍只有一个固定1920×1080验证视口，不改变用户屏幕/DPI。双STA同时活跃测试命令/关闭/权限隔离；布局/三语/键盘/UIA则在同一视口内交替显示A/B Window（另一窗口保活动但不叠盖被验Window），记录各实际客户区。使用同一OS DPI、任务栏/边框/标题栏，不跑第二分辨率。三语资源覆盖§10已列命令/状态/恢复、全部可见DTO字段标签、Model/Validity/Role与错误目录；PropertyGrid禁止默认显示C#属性名或enum.ToString作为用户文字。Host异常/诊断示例中的英文字符串只作有界技术Detail；实际页面取错误码资源给出影响与恢复，不把原Exception.Message直接显示。缺资源按§10.3 en-US回退并诊断，语言不改数值/hash或重新提交。

PropertyGrid的每个公开投影属性显式设置`PropertyDefinitionBase.Path`与本地化`Header`，仍IsReadOnly=true；本机同一25.2公开XML已核两成员，不猜DisplayName API。Culture切换在原Dispatcher重建定义/enum显示值，沿§10呈现事务，实际值/精确ID/单位代码不翻译。新增字段须同时提供三语Header/值状态/影响与恢复资源；未知字段不自动生成英文属性行，保持可见诊断而不影响Core事实。资源键按`RS.Field.<公开字段名>`、`RS.Value.<类型>.<枚举值>`固定，现有§10.3资源继续沿用。补充只读字段文案基线（同一行多个字段依声明顺序对应）：

| 字段/值 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| SurfaceId / SurfaceRevision / CoordinateFrameId | 表面 / 修订 / 坐标系 | 表面 / 修訂 / 座標系 | Surface / Revision / Coordinate frame |
| ProfileId / ProfileRevision / Method | 参数集 / 参数版本 / 方法 | 參數集 / 參數版本 / 方法 | Profile / Profile revision / Method |
| SourceIndex / CellId / Position / SetRole | 来源索引 / 单元 / 坐标 / 集合 | 來源索引 / 單元 / 座標 / 集合 | Source index / Cell / Position / Set |
| ReferenceDomain / ExclusionDomain / IndependentCheckDomain / TargetDomain | 参考域 / 排除域 / 检查域 / 目标域 | 參考域 / 排除域 / 檢查域 / 目標域 | Reference domain / Exclusion domain / Check domain / Target domain |
| DisplayResidualInInputUnit / Evaluation / ReasonKey | 显示残差 / 求值结果 / 原因 | 顯示殘差 / 求值結果 / 原因 | Display residual / Evaluation / Reason |
| MinimumPoints / MinimumRetainedPoints / ClipLimitInInputUnit | 最少参考点 / 最少保留点 / 裁剪限值 | 最少參考點 / 最少保留點 / 裁剪限值 | Minimum reference points / Minimum retained points / Clip limit |
| MaximumExcludedRatio / MinimumPlanarSpreadInInputUnit | 最大排除比例 / 最小平面展开 | 最大排除比例 / 最小平面展開 | Maximum excluded ratio / Minimum planar spread |
| MinimumEigenGapRatio / MaximumQrConditionOneNorm | 最小特征值间隔比 / 最大 QR 条件数 | 最小特徵值間隔比 / 最大 QR 條件數 | Minimum eigenvalue gap ratio / Maximum QR condition number |
| MinimumAxisNormalDot / MaximumHeightGradient | 最小轴向投影 / 最大高度坡度 | 最小軸向投影 / 最大高度坡度 | Minimum axis projection / Maximum height gradient |
| MinimumAreaRatio / MaximumGapInInputUnit | 最小支撑面积比 / 最大单元边长 | 最小支撐面積比 / 最大單元邊長 | Minimum support area ratio / Maximum cell edge length |
| MaximumTargetDistanceInInputUnit / MaximumExtrapolationRatio / AllowInterpolation | 最大外推距离 / 最大外推比例 / 允许插值 | 最大外推距離 / 最大外推比例 / 允許內插 | Maximum extrapolation distance / Maximum extrapolation ratio / Allow interpolation |
| RequireIndependentCheck / MinimumIndependentCheckPoints | 必须独立检查 / 最少检查点 | 必須獨立檢查 / 最少檢查點 | Require independent check / Minimum check points |
| MaximumCheckRmsInInputUnit / MaximumCheckP95InInputUnit / MaximumFitRmsInInputUnit | 检查 RMS 上限 / 检查 P95 上限 / 拟合 RMS 上限 | 檢查 RMS 上限 / 檢查 P95 上限 / 擬合 RMS 上限 | Check RMS limit / Check P95 limit / Fit RMS limit |
| PlaneTls / HeightFirstOrder / HeightSecondOrder | 正交平面 / 一阶高度面 / 二阶高度面 | 正交平面 / 一階高度面 / 二階高度面 | Orthogonal plane / First order height surface / Second order height surface |
| SignedNormalDistance / SignedAxisHeight | 有符号法向距离 / 有符号轴向高度 | 有符號法向距離 / 有符號軸向高度 | Signed normal distance / Signed axis height |
| None / FixedClipOnce | 不裁剪 / 裁剪一次 | 不裁剪 / 裁剪一次 | No clipping / Clip once |
| True / False / null（证据值） | 是 / 否 / 未提供 | 是 / 否 / 未提供 | Yes / No / Not provided |
| SourceUnknown / DerivedSourceNotObserved / ContinuityMissing | 来源未知：恢复原证据 / 来源非观测：核对用途 / 缺连续性证据：提供单元声明 | 來源未知：恢復原證據 / 來源非觀測：核對用途 / 缺連續性證據：提供單元聲明 | Source unknown: restore its evidence / Source is not observed: check its use / Continuity evidence missing: provide cell declarations |

null只按字段语义显示：无R/C残差为未提供，未知支撑为证据不足，禁用外推为不允许；不能共用“0”或绿色通过。SourceValidityCode/技术Detail只在诊断详情保原字节文本，主页面取上述稳定原因资源；数值显示当前文化、小数位由宿主显示策略且不截改事实，精确SourceIndex/CellId始终Int64十进制，不按语言或图表double变成另一来源。

### 18.5 定向反例与验收定位

不重新审算已接收V01～07/720-byte向量/T01～24。本节补充消费检查随真实Host接入运行，由其原测试承担，不建第二模块测试栈；本轮只做规则/字段反例推演，非产品运行。

| 反例/输入 | 确定期望与验收者 |
|---|---|
| SD.Meter=1、RS.Meter=0；SourceIndex=9007199254740993 | switch得到Meter，无×1000误差；Int64原值保持，禁止经double舍入。当前Core数值/身份不变；输入Host核映射 |
| Valid的Z=-1或0；Unknown状态/Interpolated来源 | Observed有限负/零高保留；未知/派生不转Observed/Invalid或删点，映射失败保原来源，不开始Core。Producer/用途Host核物理声明 |
| 前块成功、末块Io/Cancelled；Faces未完或三角跨无效点 | 没有部分快照采用；保上游operation/暂存/lease至真实归还；连续性不从MeshReport猜。输入Host与拓扑Owner核全链 |
| 上游H1的1000000000 mm+0.001 mm、误差阈值0 | 复用SD H03：float32量化不能称无损，NativeReply拒绝且无本模块成功输入，不自动换H2/放宽。采用H的Host运行原上游断言，本模块不重复native算法 |
| 新metadata版本/format hash错；旧manifest缺原Profile | 前者在准确Decode/注册处拒绝；后者RS-1401/历史只读，不能重新hash伪造旧绑定。Replay/Store/Profile Owner按原操作恢复 |
| A Dispatcher停机/撤权/unknown草稿，B仍正常 | A只取消/关闭自己，根保持其原Task，B可完成原合法计算与呈现；双STA原线程/原操作真实退出才清账。W1原Owner执行RS-U03～U10及本节构造 |

消费Benchmark在§13/§10.7原统计口径上单列上游read/副本/单位映射/hash/Face暂存→Core接纳→ResourcesReleased→worker投影→实际呈现→两STA解绑/归还测点；不只统计Core拟合。保并存源buffer/全点副本/单元/投影/原Task/root槽的实际峰值与逻辑账，采用H/codec的Host另计其上游额度。拒绝/超时/未知、两用途/两STA/冷热/大源索引/孔洞/禁区/无单元等负载均保，客户目标缺失仅NotEvaluated；无需新建本模块原生性能后端或复制SD基准。

## 19. 全批准范围的文档准备结论与剩余Owner

### 19.1 完整能力覆盖（2026-10-11）

**当前全部批准范围的可决定软件设计已闭合，文档准备完成；没有等待总控内容审核或留给后续开发者补猜的内部算法/API/架构决定。** 本结论覆盖当前架构IM-035、§1完整职责与§10可选UI，不只是RS-C1～C4或最后一次W1状态。模块仍DesignReview / Prep；C1～C4仅原规格准入保持，W1仍PreparationIncomplete / NotReady，I1原门保持。文档准备结论不提升ImplementationSpecificationReady、代码/真实运行/产品集成或生产资格。

| 全部批准能力/场景 | 唯一实施位置与确定边界 |
|---|---|
| 参考建立/物理层与域/编码高度 | §1–4/6.1/18.1–2；物理参考、准确坐标/单位/来源由Producer/用途Owner声明，不选最低/最大面或丢Unknown分母 |
| P正交平面、H一阶、Q二阶曲面 | §4.2/6.1–3/17；TLS/Jacobi/固定QR与一次裁剪已冻，不自动升降阶或切HALCON；可行矩阵候选与选择理由/比较门保留 |
| 残差/留出检查/资格/误差 | §6.4/6.6/8.5；R/I/J/C独立、孔洞/Forbidden/Unknown/外推分开；unavailable不确定度和物理准确度均不借RMS授信 |
| 高度校正/全局与局部/板弯消费 | §6.5/8.5/9/14.3；法向与轴高/交点/方向/支撑明确，不覆盖原Z。局部失败要新显式参考请求，无源不补猜；翘曲统计/面积体积归计量消费者 |
| 无UI/并发/超时/关闭/恢复 | §4.4/5/7/9；公开Factory/Identity/Profile租约、原Task/有限根/借用与自有/cleanup/移交均已定义，Unknown不清槽 |
| 身份/原参数/重开/版本回退 | §8/11.2/14/16.4/18.3；原hash与Profile闭包精确，SD格式与RS Artifact分开，Schema/Store事务不由Core发明 |
| 独立Inspector/命令/权限/证据显示 | §10.1–7/18.4；Prepare/Select/Projection/呈现回执、草稿查询与撤权、DevExpress组合/三语/键盘/UIA/默认只读场景、双STA明确 |
| Adapter/输入与显示消费 | §3/8.3/17/18.1–4；当前批准直交值/本包场景，SD C1–C5映射可执行；直接H/codec/viewport装配不在现执行路径，条件消费前置已定，不漏掉为未设计隐式依赖 |
| 参数来源/默认/推荐 | §4.2/6.1/10.4/18.1；全部必填/可空语义明确，无生产默认，无自动阈值/选模/学习；不把扩展字段当获批数值传播能力 |
| 正确性/Golden/双消费者/负载 | §9/11–14/10.7/18.5；原解析向量/断言复用，真实高度与体积/表面用途独立；运行阈值来源/失败样本/峰值与排空测点明确 |

### 19.2 本原会话自审与验证边界

复用已完成官方HALCON26.05、固定Open3D/NumPy源码/测试、DevExpress本机25.2公开XML、Microsoft WPF API与已接收Core/W1两轮自审；未重复研究/重算旧向量或改变算法。2026-10-11两轮增量自审只沿本次消费边界：第一轮从外部输入向下核enum数值不同/Frame修订/原Int64/Origin/Invalid未知/连续性与SD H1量化/codec版本；第二轮从双STA与未知关闭向上核Application唯一/线程Dispatcher/原Task/借用与资源/拒绝无部分输入/三语原异常不直显。实际缺口修入§18，原Root/Close正确正文不重写，不新增Scope或过程报告。

本轮定向文档验证核本文本地链接、围栏、公开类型唯一、§18/19覆盖/剩余Owner/禁止路径、RS-U01～U10与十二项定位，以及原Core/API/算法/canonical/§9和§11–14保护段、C1～C4/I1原状态行保持。消费反例仅证明文字规则的确定性；没有运行surface-data、参考面C#、HALCON、WPF、存储codec、两STA或客户样本，不能把自审/文档检查当产品Golden/性能结果。

### 19.3 精确剩余Owner与运行门

| Owner | 剩余输入/执行门；不是内部待设计决定 |
|---|---|
| IM-035本永久会话/实现Owner | 按既有工程落实Core与Wpf/Test、真实编译/解析Golden/T01～24/U01～10/双STA/资源取消恢复/三语与UIA、性能与长稳；本轮禁止产品代码、工程和过程材料。公共签名形状资料核对不冒称程序集引用编译 |
| Producer/采集/标定/拓扑与SD Host Owner | 真实不可变表面/准确Frame与Mapping/来源及连续性声明、源资产引用；执行§18.2完整读取与映射。若实际采用H，提供准确worker发布包/运行预算与获批误差Profile并执行SD H03～06；没有直接H消费时该门不适用 |
| Replay/存储/原Artifact与Profile发布Owner | 准确原参数/输入/结果闭包、平台Schema/原子提交/权限保留/版本包；选择SD新codec时提供格式完整VersionRef/hash与validator注册/旧包回退。SD metadata不替代RS Model/Result；无该codec消费时不强加注册任务 |
| 本模块W1 Host/本地化与权限Owner | 真实WPF/25.2.3/1920×1080/双STA/三语/UIA与性能执行、可信授权/草稿Store/同ID回查/I1产品接线。模块默认场景无需viewport Assembly v0.2；实际选择新显示装配才由原消费Owner先定义接线范围，不在本轮猜宿主私有API |
| 高度/翘曲/体积/表面计量与客户用途Owner | 物理基准、采样/覆盖/离群/独立检查/外推阈值、计量噪声与精度要求、真实Golden/误接受拒绝/性能目标、用途采纳/计量/HIL/现场。无公开证据的物理数值不编造，只阻相应用途，不阻无副作用Core |
| 正式平台Contract/Schema/State/质量Owner | I1候选事实与质量/配方生效/持久化协议采纳；不由ReferenceSurface Succeeded、UI Applied、NativeReply或Decode获得放行权 |

达到当前完整批准范围设计准则即收口；总控只接收状态，无需再等待内容复核。存在的剩余事项均是上述准确外部输入、实现执行或真实资格，当前无可决定的软件设计欠账；不自动开代码、不迁移客户项目、不新增native/通用导入/在线调参/不确定度数值或猜测性UI能力。


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

## 附录 A：模块核心 API Contract v0.1（逐切片规格接收）

本节定义本独立模块的核心代码边界，优先于正文中仅针对产品集成的“候选/待采纳”措辞。本文已给出的公开类型、方法、事件、错误键、状态、参数表和代码形状，作为对应切片获准后唯一实施依据；本附录的存在不代表准入通过。实现者不得另造第二套核心 DTO、状态机或错误语义。

- `Module API Contract v0.1` 只覆盖无产品事实写入的 Core 和纯托管数值接口。它不把平台 C-01～C-08、客户工艺阈值、最终放行、产品数据库字段或厂商私有类型冻结为模块 API。
- 正文中仍称“候选”的内容，若属于平台Schema/持久化事务/产品Owner/生产资格或客户Profile，继续候选；本模块值身份编码、公开API/事件/错误/参数域/资源语义按§4–8冻结，不把平台序列化未定误当Core hash未定。任何未定义操作先补本指导。
- 本模块首发仅实现纯托管 Core；不得因其他模块的 HALCON/AsunImage 适配器核验要求而延迟或替换本模块固定算法路线。
- 主控2026-10-10接收0.3.1-prep的RS-C1～C3保持`ModuleCoreImplementationReady`；0.3.2-prep的RS-C4双Host/cleanup修正经窄复核闭合六项规格缺口，恢复`ModuleCoreImplementationReady`，均仅规格准备。命名空间、唯一工程/测试绑定、允许/禁止路径、算法/API/canonical/Host及case10 s/suite120 s/外进程180 s基线不变。W1的§10 Inspector/Session/Root/Host/默认场景规格在0.4.0-prep补齐并获主控2026-10-10内容接收，内部设计欠账已闭合；0.4.1-prep仅同步状态，W1仍PreparationIncomplete / NotReady；RS-I1原门保持，本结论非ImplementationSpecificationReady或运行/生产验收。

| DEV-GOV-010 §3.1项 | 本指导可定位的规格输入 | 结论（RS-C1～C3接收保留；RS-C4窄复核接收，仅规格准备） |
|---|---|---|
| 1 边界/第二消费者 | §1–3、§9、§14.3，全局/局部由宿主组合 | 已给职责、禁区与两个无UI用途；真实集成未执行 |
| 2 API/单位/生命周期/版本 | §4全类型/Factory/Identity/Profile端口、§5/7/8状态与闭包 | 唯一Core基线已获主控内容接收，仅规格准备，不授整模块Ready |
| 3 最小无UI宿主 | §1.3 BCL类库/Exe、§9强持Owner双Host及嵌套finally | 无UI/设备/数据库依赖；RS-C4强持/未知/移交拒绝窄修已获主控接收；Simulator仅软件链 |
| 4 样例/断言 | §11 V01–07/720-byte向量、§12 T01–24、§16场景导航 | 原数学/编码接收保留；RS-T20～22独立cleanup/原Owner断言获窄复核接收，主控独立重建720-byte向量/hash一致；运行未执行 |
| 5 Benchmark | §13及DEV-GOV-010唯一公共统计口径 | 方法/维度/资源/失败处理已定义；客户目标缺失为NotEvaluated |
| 6 工程/禁区/调用/后续门 | §1.3唯一工程与命令、§9调用、下表切片 | 当前仅文档，不创建工程；WPF/适配/客户门分开 |

| 切片 | 实现范围与依赖 | 当前状态与精确后续门 |
|---|---|---|
| RS-C1 值契约/Identity | §4强类型、§8 canonical、V编码向量；唯一Core/Exe | ModuleCoreImplementationReady（主控2026-10-10接收，仅规格准备）；不得把旧Artifact重新hash伪造旧身份 |
| RS-C2 P/H/Q固定数值 | §6.1–6.5、V01–05/07、T03–09/16/17；依赖C1 | ModuleCoreImplementationReady（主控2026-10-10接收，仅规格准备）；真实C#编译/解析Golden/资源执行后才SoftwareVerified，客户物理准确度不以合成值通过 |
| RS-C3 支撑/求值重开 | §4 SupportEvidence/Binding、§6.6/8、V06、T10/11/15/23/24；依赖C1/C2 | ModuleCoreImplementationReady（主控2026-10-10接收，仅规格准备）；保留禁区/未知/Hull，不能以凸包替代；客户采样/拓扑/外推资格是后续门 |
| RS-C4 运行/来源/关闭 | §4.4 Factory/ProfileSource、§5/7、§9双Host与强持Owner、T12–14/18–22；依赖C1–C3 | ModuleCoreImplementationReady（主控2026-10-10窄复核0.3.2-prep接收，仅规格准备）；Factory前槽/原Task、独立有限cleanup/嵌套finally、未知/在途Dispose/移交拒绝保持及测试预算缺口闭合，真实两宿主集成仍未验 |
| RS-W1 可选Inspector | §10.1–7/18.4独立Inspector API、Session/Root/Host、挂接/代次/权限/三语/默认场景/关闭、RS-U01～U10 | PreparationIncomplete / NotReady：规格内容已主控2026-10-10接收，内部设计欠账已闭合（本原会话2026-10-11全范围核实含双STA/三语字段）；真实构建/1920×1080 WPF/DevExpress25.2.3/UIA/三语联动/两用途/性能未执行，产品接线按I1门；不阻断无UI C1–C4 |
| RS-I1 平台/客户资格 | 正式Contract/Schema/State/Owner、存储原子提交、真实采集/标定/用途Profile/样本 | PreparationIncomplete：客户物理阈值/Golden/性能/HIL/计量/现场及版本迁移按对应Owner接收；不以代码/Mock冒充 |

0.4.0-prep的W1规格与0.4.1-prep接收同步保留历史结论；本轮0.5.0-prep补齐§18准确输入消费/SD0.6.0条件影响/独立显示双STA及§19完整批准范围结论。本原会话已完成有限增量自审和定向文档验证，当前无可决定的软件设计欠账，无需总控内容审核。RS-C1～C4原规格及RS-I1原门保持；W1保持PreparationIncomplete / NotReady，真实C#/HALCON/WPF/25.2.3/1920×1080/三语/UIA/性能及受影响I1接线/客户资格未执行。未改Core API/算法/canonical/§9或其它文件，不写产品代码/工程/新报告脚本，不新建会话/Goal/fork/子代理，不自动开下一范围。
