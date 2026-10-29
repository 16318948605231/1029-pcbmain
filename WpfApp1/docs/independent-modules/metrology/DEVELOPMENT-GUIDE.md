# 二维三维通用计量独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`M1, M2, C1, C2, C3, C4`

- 模块：`metrology`（中文：二维三维通用计量）
- 模块 ID：`IM-036`；来源映射：`PKG-030`
- 文档状态：`DesignReview / Prep`（M1/M2/C1–C4六项切片规格已达 `ModuleCoreImplementationReady`；M3/M4公开装配与基础只读桥指导已限定内容接收）
- 指导版本：`0.7.0-prep`（完整范围准备、有限Replay推荐、原图读桥与SD H/Codec消费增量，2026-10-11）
- 平台目标：C# / .NET 10；首片 Core 无 UI、无 HALCON
- 模块长期方向：可复用的二维/三维通用计量能力；每项扩展单独定义切片、契约和准入；本轮完整范围结论见§21

本文是metrology唯一实施指导。附录A记录现有二维API v0.1；§10–18定义目标基础Contract v0.2，§19补齐已规划连续计量Contract v0.3；它们以显式入口/版本接入，不静默改义旧API。主控已接收M1/M2/C1–C4六项切片的 `ModuleCoreImplementationReady` 规格，范围见§10/18；未接收的适配和产品资格保持`DesignReview / Prep`。此接收不表示代码已实现、真实工程引用迁移或产品验收通过，没有启动实现。首片是实施顺序，不收窄完整模块职责；完整能力定位§19.1，不能仅以v0.2子集宣称整模块准备完成。 §20的M3/M4公开装配与基础只读桥指导已由主控限定内容接收，ROI Codec创建与CG参数名精确消费见§20.5；此接收仅覆盖指导内容，不将M3/M4真实native、物理或产品资格标Ready。 本轮完整范围软件规格及外部门结论见§21；新增R1/R2/I1不改变原六项准入或已接收算法/向量。

准入按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)，边界按[独立模块架构](../INDEPENDENT-MODULE-ARCHITECTURE.md)，原会话按[模块索引](../MODULE-INDEX.md)；算子语义来源为[本地HALCON 26.05手册](../../../halcon算子手册/operators/)。

## 0. 首片绑定与准入状态

首个实现切片绑定 `src/Asun.Metrology.Core/`，根命名空间为 `Asun.Metrology.Core`；最小验证工程为 `tests/Asun.Metrology.Core.Smoke/`。仓库当前处于开发指导完善阶段，上述两个工程尚不存在，须在切片获授权时创建并登记入 `AsunVision.slnx`。允许修改这两个目录及对应项目文件；禁止修改其它模块、产品项目、AsunImage 内部和只读参考快照。

首片仅覆盖该 Core 当前源码公开的二维点、二维线段、二维正交坐标系、二维仿射变换及校验、点间距离结果及完整性校验、二维仿射标定及校验。Smoke 断言覆盖有限值、距离、坐标往返、仿射变换/求逆、线段长度/中点、距离结果指纹、仿射拟合残差/指纹/确定性和 tamper rejection。Smoke 数量或通过不代表算法数值资格、性能或生产验收。

首片项目当前引用 `Asun.Platform.Contracts`。因此本指导不声称 Core 是零项目依赖；实现准入前须按 `DEV-GOV-010 §3.1` 核实其所需 Contracts 是否仍满足无产品 Shell、数据库和设备 SDK 的最小宿主条件。该引用不授权将产品 DTO 或平台状态扩入 metrology API。

本文件已将旧首片与目标全模块分版本写清；异常/并发/取消/关闭断言和Benchmark方法定位§12–16，剩余规格与外部门定位§18。文档整体仍为 `DesignReview / Prep`；M1/M2/C1–C4六项切片按主控接收记录标记 `ModuleCoreImplementationReady`，也不以“旧首片有代码”代替目标契约验证。

## 1. 职责与边界

模块职责是对调用方给定的几何数据执行通用几何运算和结果校验。首片只处理二维数值几何，不读取图像、不提取边缘、不管理 ROI/标定资产、不访问设备/存储，也不作质量放行。

调用方拥有被测对象身份、物理单位/坐标含义、校准资产生命周期、输入证据、工艺公差、Required/缺项政策、提交和设备副作用。首片 `DistanceMeasurementResult.Unit` 是调用方提供的非空标签；它本身不证明单位是毫米或结果具有物理资格。仿射拟合返回残差与指纹，不构成校准资格或不确定度声明。

Core 不包含 PCB、PCBA、SPI、AOI、点胶、涂覆、孔/焊盘语义、最终质量状态、产品 ViewModel、设备动作、数据库表或静态当前配方/图像。未知、无效或失败不得变成零值或 PASS。

## 1B. 新架构适配要点

本模块的 §3A 是内部子程序集拆分（内容性），本节补充面向新平台架构的适配约束。

**架构门禁**：`Asun.Modules.Metrology.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"首片只处理二维数值几何，不读取图像"，Core 是纯几何计算模块，无 HALCON/AsunImage 依赖。§3A.7 已明确"零 HALCON 内核"。

**Blazor/Web**：测量结果、拟合残差和不确定度区间通过 gRPC/REST 查询；浏览器只渲染测量标记与数值，不重算拟合。坐标变换由 `coordinate-geometry` 服务端计算后传递，浏览器不重写矩阵（同 IM-007 §1A）。

**AI Tiling**：本模块的 `QualifiedMeasurement` 是 AI 推理**结果消费**的量化入口之一（几何量测）。约束：
- 本模块不持有推理 tile 租约，不参与推理分块编排
- AI 推理输出的几何候选若需几何验证，由宿主调用本模块的通用几何能力；本模块不解释 AI 分数、不做缺陷命名

**HALCON 双跑**：§3A.7 已明确"零 HALCON 内核"——本模块不调用 HALCON 算子，因此 HALCON 备选 CI **不涉及本模块**。计量链路的 HALCON 路线在 `features-2d`/`measurement-calibration` 等模块中执行。

## 2. 架构和消费者边界

允许的首片依赖方向：

```text
无 UI 调用方
    -> Asun.Metrology.Core
    -> Asun.Platform.Contracts（当前项目引用，具体使用须受限并经准入核对）
```

首片公开方法均为纯托管同步计算/校验，没有异步执行器、事件流、资源租约或 HALCON handle。调用方之间不得通过静态可变状态传递请求或结果。

完整模块的两个无 UI 消费者及接入顺序定位 §10/§16.2；受控fixture与双Host规格已接收，真实消费者字段映射和产品资格另行验收，不能据此扩展附录 A 的旧类型。

## 3. 唯一核心 API Contract

附录 A 定位当前源码的二维类型和签名；§10–18 是目标 v0.2 的唯一规格，目前尚无其代码。仅当对应切片被主任务接收并关闭本指导列明的准入缺口后，才按目标契约实施；不得把本文中的目标 API 说成现有实现。v0.1 的 Unit 标签、正规方程和指纹行为不能作为完整模块的计量、数值条件和跨语言完整性保证。

## 3A. 内部子程序集拆分设计

### 3A.1 设计动机

`metrology` 模块职责涵盖 2D 几何计算、3D 表面计量、视觉桥接和量测资格评定，单一程序集会导致：
- HALCON 依赖污染纯数值算法（2D 几何不需要 HALCON）
- 计量资格（GR&R、不确定度、溯源）与纯几何耦合导致测试困难
- Surface 能力依赖 surface-data 端口，几何计算不需要

**解决方案**：一个对外模块门面 + 四个内部子程序集，消费者只引用 `Asun.Metrology.Core`，内部分层。

### 3A.2 子程序集划分

```
Asun.Metrology.Core/                    ← 对外唯一门面（消费者只引用这一个）
│
├── Asun.Metrology.Geometry/           ← 子程序集 1：纯数值几何
│   - 零 HALCON 依赖，零 UI 依赖
│   - 依赖：仅 Asun.Platform.Contracts（坐标类型）
│   - 内容：点、线、圆、椭圆、多边形、仿射变换、
│           最小二乘拟合、SVD、距离、角度、面积、GD&T 几何
│   - 可作为完全独立的 .NET Standard 2.1 类库
│
├── Asun.Metrology.Qualification/      ← 子程序集 2：量测资格
│   - 依赖：Asun.Metrology.Geometry + 标定资产端口
│   - 内容：不确定度计算、GR&R（量具重复性）、
│           AffineCalibration2（带溯源要求）、
│           QualifiedMeasurement 包装（裸几何结果 + 不确定度）
│   - 不声称标定资格，只提供量化评定工具
│
├── Asun.Metrology.Surface/            ← 子程序集 3：3D 表面计量
│   - 依赖：Asun.Metrology.Geometry + surface-data 端口
│   - 内容：平面拟合、曲率、体积、翘曲、高度场统计
│   - HALCON 可选（不影响 Geometry 和 Qualification 的编译）
│
└── Asun.Metrology.Vision/             ← 子程序集 4：视觉桥接
    - 依赖：Asun.Metrology.Geometry + features-2d 端口 + AsunImage
    - 内容：从 HALCON XLD/Region 提取几何、子像素边缘拟合输入准备
    - 唯一引入 AsunImage 依赖的子程序集
```

### 3A.3 依赖方向规则

```
消费者宿主
    └─ Asun.Metrology.Core（门面，只暴露公共 API）
           ├─ Asun.Metrology.Vision（引入 AsunImage）
           │       └─ Asun.Metrology.Geometry（纯数值）
           ├─ Asun.Metrology.Surface（引入 surface-data 端口）
           │       └─ Asun.Metrology.Geometry
           └─ Asun.Metrology.Qualification（引入标定资产端口）
                   └─ Asun.Metrology.Geometry
```

**绝对禁止**：
- `Geometry` 引用 AsunImage / surface-data / features-2d 端口
- `Qualification` 引用 AsunImage 或 surface-data
- 任何子程序集引用 `System.Windows.*` / `DevExpress.*`（架构门禁测试覆盖）

### 3A.4 对外门面规则

`Asun.Metrology.Core` 是对外唯一 DLL，消费者只 `<ProjectReference>` 它，不直接引用子程序集。门面的职责：
- 重新导出子程序集的公共类型（`public using` 或类型转发）
- 提供组合根注入（`MetrologyServiceBuilder`）
- 路由能力请求到对应子程序集

```csharp
// 消费者视角：只看到这一个命名空间
namespace Asun.Metrology.Core;

// 门面转发 Geometry 子程序集类型
public static class MetrologyCore
{
    /// <summary>创建计量服务（按需注入 Surface/Vision 端口）。</summary>
    public static IMetrologyService Create(
        ICalibrationAssetPort? calibration = null,
        ISurfaceDataPort? surface = null,
        IFeatures2DPort? features2d = null)
        => new MetrologyServiceImpl(calibration, surface, features2d);
}
```

### 3A.5 Method 枚举分组

旧的 `MetrologyMethod` 枚举把 32 种方法平铺，可读性差。按子程序集分组：

```csharp
// 对外仍是单一 Method 枚举，但命名按子程序集分组
public enum MetrologyMethod
{
    // ── Geometry 子程序集 ───────────────────────────────
    PointToPointDistance2D,
    PointToLineDistance2D,
    LineToLineAngle2D,
    CircleDiameter2D,
    EllipseAxis2D,
    SegmentLength2D,
    PolygonArea2D,
    AffineFit2D,
    // ... 其余 2D 几何方法

    // ── Surface 子程序集 ────────────────────────────────
    PlaneFit3D,
    HeightFieldStats,
    VolumeBetweenSurfaces,
    WarpProfile,
    // ... 其余 3D 表面方法

    // ── Vision 子程序集（需要 features-2d 端口）─────────
    EdgeFitDistance2D,
    SubpixelCircleDiameter2D,
    // ... 其余视觉桥接方法

    // ── Qualification 子程序集 ──────────────────────────
    GaugeRepeatability,
    GaugeReproducibility,
    MeasurementUncertainty,
}
```

旧 `[Obsolete]` 兼容层在一个版本内保留，指向对应新名称。

### 3A.6 QualifiedMeasurement 包装

量测资格（Qualification 子程序集）提供显式可选层：

```csharp
// Geometry 子程序集：裸几何结果，不声称物理资格
public sealed record GeometricResult(
    double Value,
    string Unit,
    double Residual,
    string Fingerprint);

// Qualification 子程序集：有资格的量测结果
public sealed record QualifiedMeasurement(
    GeometricResult Geometry,
    double ExpandedUncertainty,
    double CoverageFactorK,
    string CalibrationRef,
    string TracebilityChain);

// 消费者拿裸几何：
IMetrologyService svc = MetrologyCore.Create();
GeometricResult r = svc.Measure(request);

// 消费者拿有资格结果：
IMetrologyService svc = MetrologyCore.Create(calibration: myCalibrationPort);
QualifiedMeasurement q = svc.MeasureQualified(request);
```

**不允许中间态**：`GeometricResult` 永不声称资格，`QualifiedMeasurement` 必须有完整溯源链。

### 3A.7 零 HALCON 内核的意义

`Asun.Metrology.Geometry` 是平台中**唯一没有 HALCON 依赖**的视觉计算核心。这解决了两个问题：
1. **HALCON 单点故障保险**：几何计算在 HALCON 不可用时仍可运行
2. **交叉验证 oracle**：`Geometry` 子程序集可作为 HALCON 视觉路线的数值参照（同一 Golden 数据集双跑 CI，差值超容差即失败）

CI 门禁：`Asun.Metrology.Geometry.Tests` 必须在无 AsunImage DLL 的环境下通过。

### 3A.8 项目文件结构

```
src/
├── Asun.Metrology.Geometry/
│   ├── Asun.Metrology.Geometry.csproj      （TargetFramework: net10.0）
│   └── ...
├── Asun.Metrology.Qualification/
│   ├── Asun.Metrology.Qualification.csproj
│   └── ...
├── Asun.Metrology.Surface/
│   ├── Asun.Metrology.Surface.csproj
│   └── ...
├── Asun.Metrology.Vision/
│   ├── Asun.Metrology.Vision.csproj        （引用 AsunImage）
│   └── ...
└── Asun.Metrology.Core/
    ├── Asun.Metrology.Core.csproj          （门面，引用四个子程序集）
    └── ...

tests/
├── Asun.Metrology.Geometry.Tests/          （无 AsunImage，必须编译通过）
├── Asun.Metrology.Core.Smoke/              （端到端 smoke）
└── ...
```

**迁移计划**：当前 `src/Asun.Metrology.Core/` 的代码按依赖方向逐步迁入四个子程序集，对外 API 不变。迁移不增加模块数量，不修改对外 API 合同。

## 4. 后续能力边界与 HALCON / AsunImage

完整模块能力及执行规格见§10–19，不属于当前首片代码。图像、ROI和表面输入由宿主提供不可变证据，模块负责本请求的拟合及量测，不负责交互绘制、重建、基面学习、工艺判定、证据Store或设备采集。多FOV只接受上游已闭合坐标和身份的输入，不新增拼接/配准。

已有首片纯数值 Core 可无 HALCON 运行；目标视觉后端使用 AsunImage HALCON 26.05 的 `ImageLibDotNet.cv2`。该 operator set 可调用全部 26.05 算子，metrology model 用 `create/apply/get/clear_metrology_model` 路线，不要求单独的 HMetrologyModel 类桥，也不接 HOperatorSet 或 halcondotnet.dll。只在实际 C# 参数类型/重载/封送有歧义时核对公共签名或消费项目编译；不重复查算子是否被封装。纯身份/生命周期/质量权限等非视觉事务不适用 HALCON。

HALCON 主路线、分支、参数和资源顺序见 §13；26.05 手册事实与项目实现证据分开记录。算子可调用不等于本模块 adapter 已编译、性能或精度通过。

## 5. 首片处理顺序与调用样例

最小调用顺序：构造有限二维点/线段或对应关系；按 Contract 调用几何操作；对变换/拟合结果执行需要的校验；由调用方解释坐标单位和校准用途。首片不接收图像、Profile、预算、取消令牌或证据 Store。

```csharp
using Asun.Metrology.Core;

var start = new MetrologyPoint2D(10, 20);
var end = new MetrologyPoint2D(40, 60);
var distance = DistanceMeasurementRuntime.Measure(start, end, "mm");

if (!DistanceMeasurementResultValidationRuntime.IsValid(distance))
    throw new InvalidOperationException("Distance result validation failed.");

Console.WriteLine($"{distance.Distance} {distance.Unit}");
```

`"mm"` 仅演示调用方标签；此样例没有标定、单位转换、不确定度或标准件证据，不可解释为经资格确认的毫米测量。仿射标定样例至少需要三个非退化二维对应点；退化/数值条件和异常按附录 A 处理。

## 6. 关闭、状态与资源所有权

首片是同步托管数值计算，不接纳长时间 native 工作，因此没有 `Accepted/Running/Completed` 事件状态机，也没有 `Draining`、`Drained` 或 `ResourcesReleased` API。进程退出由宿主负责；首片不得伪造异步生命周期事实。

任何未来含异步/native 资源的独立切片，必须在其准入指导中沿用以下关闭语义，并给出可测试状态/查询 API：

- `Draining`：停止启动新的工作，等待 native 调用、回调和本操作工作退出；输入租约继续持有。正常收尾保留计算结果；取消、超时、故障才撤销成功发布权。
- `Drained`：确认本操作全部 native 工作及回调已退出；它不表示租约、临时资源或宿主资源已经释放。
- `DrainUnknown`：排空截止已到但无法证明 native 工作已退出。它是独立的非终态/隔离状态，保留 `OperationId + RequestRevision`、句柄和所有相关租约；不得发 `Drained`、`ResourcesReleased` 或可重试成功终态，不得复用可能仍被 native 使用的资源。必须支持按同一操作身份继续查询/观察排空并完成恢复判定。
- `ResourcesReleased`：只有在 `Drained` 已确认且模块所拥有的租约/临时资源已确实归还后才能发布。宿主拥有的对象仍由宿主释放；资源释放未知须另有明示状态，不能等同释放成功。
- 终态 `Cancelled`、`TimedOut`、`Failed` 或成功完成，只能在排空确认和本模块资源释放后发布。超时取消请求不等于 native 超时退出；不可强杀仍运行的 native 句柄来伪造完成。

未来事件必须携带同一操作身份、单调序号和状态。排空未知时的恢复不得创建新身份来掩盖旧 native 工作；完成确认后再决定释放、隔离或由 Owner 批准的恢复动作。上述规则不向当前同步 Core 凭空增加 API。

## 7. 首片案例和测试断言

以下对应现有 Smoke 范围：有限点可计算距离；正交坐标系的 world/local 往返一致；有限仿射变换可变换且可求逆；有限线段给出长度/中点；距离结果校验可发现不一致/指纹篡改；至少三组非退化对应点可确定性拟合二维仿射变换，并可校验残差、点数和指纹。无效数值、退化输入和边界行为必须以后续经批准的测试补齐，不因现有 Smoke 未覆盖而推定通过。

首片回归须区分源码行为与目标要求：例如同点距离/零长线段可以为零，但不能作为方向；Unit 非空只是标签校验，不是单位合法性；旧验证器在非法输入上可能抛异常，不是 total validator；旧方法没有 RequestRevision。正常、退化、溢出、指纹篡改、Culture、并发和误用断言按 §16 补齐。首片无异步/native 工作，取消/超时不伪造可中断语义；目标 runtime 的取消、关闭和未知结果另按 §14 测试。

现有 Smoke 的一百轮重复断言是回归检查，不是统计性能样本、精度/不确定度证明、第二消费者验收或并发/取消验证。不得将面积、孔洞、体积、噪声图像、HALCON、WPF、硬件或生产场景列为首片测试通过项。

## 8. 版本、Benchmark 与资格

首片 Contract 版本为 `0.1`（只冻结附录 A 中明确列出的二维 API）。删除/改名类型或方法、改变坐标变换方向、运算/舍入/排序、异常语义、指纹输入或默认容差均为破坏性变更，须先更新 Contract 和版本策略。新增兼容 API 也须先修订唯一指导和测试。

BenchmarkProfile 按 `DEV-GOV-010 §3.1` 冻结源码/二进制版本、确定性二维样本、预热/样本数、并发、阶段测点和资源统计；测点至少区分点距离、仿射变换、拟合及校验。P50/P95/P99 使用 DEV-GOV-010 规定的方法。客户目标缺失时只能记录诊断测量并标为 `NotEvaluated`；本文不设时延、精度或内存通过阈值。首片无 native 资源，不得套用 HALCON 资源指标。

二维仿射拟合合成样例只验证定义和可复算性。客户计量资格需另有参考件、独立检查样本、适用域、单位/坐标链和 Owner 验收；在此之前不得把 `RootMeanSquareError` 或 `MaximumError` 当客户合格阈值。

## 9. 来源和待决项

本指导的上下位依据包括独立模块架构、`DEV-GOV-005`、`DEV-GOV-010`、`DEV-VIS-020`、`DEV-VIS-021`、相关 Contract Owner 冻结结果及首片源码/Smoke。只读参考快照为 DZ-XVision（`docs/references/project-snapshots/DZ-XVision/20261004/`）、AOI.Main 与 AsunMeasure（`docs/references/project-snapshots/` 下对应快照）。这些原件提供工程场景，不提供平台 DTO、单位资格、参数阈值、HALCON adapter 实现或生产证据。

当前待决按§18/20逐切片登记：基础公开只读映射指导已限定内容接收；仍待关闭的是连续/生产资格Owner映射、native资源包络、旧平台引用迁移及真实工程验证。全范围准备结论与剩余Owner见§21；R1/R2/I1软件规格见§13.3–4/20.7–8，不以未实现免除设计。六项切片的目标合同/受控复用规格已接收；§11–16已定义范围、方法和异常断言不再作为“未来待设计”的泛化阻断，不得把规格接收升格为实现或产品准入。

### 9.1 H:\docs 来源复审增量（2026-10-06）

本节只记录对本模块职责稳定、可迁移的后续切片约束；不扩展首片 Contract，也不替代平台 Contract/Owner。

- `H:\docs\40-development\40-vision\标定与计量开发指导.md`（SHA-256 `6e55b1c00230ef35da466290b57feb533be8ef239f0ba95a384a3de53da81433`）补充了可直接执行的溯源原则：标定/计量工件必须绑定不可变 identity、版本、内容 hash、方法/参数、输入观察清单、有效域、残差/不确定度、父工件和适用环境；下游按精确版本/hash解析，不能以“当前最新”替代已绑定版本。失效、过期、撤销、错机或适用域不匹配时必须 fail-closed；更新产生新工件，不能复活旧工件；运行中请求固定原工件，切换使用 CAS/回执。该约束适用于未来 calibration/measurement adapter 或资格切片，首片二维 Core 不拥有这些资产，也不新增相应 DTO。
- 同一来源还明确了量测验证与正式标定、GR&R 的边界：验证记录保留原始观察、`MeasurementDefinition`、value、validity、uncertainty、attempt、环境和 evidence；重新采集生成新 attempt，不覆盖失败样本。Bias、Linearity、Stability、Uncertainty、GR&R 分别报告，不能以全局 RMS、单板重复、保存成功或某一次统计结果替代资格。来源中的 3D、照明、移动相机、标准件证书 schema、签名/权限和具体平台接口保留为后续 Owner 设计，不写入首片。
- 来源使用 HALCON 24.11 内容；本平台不采纳其算子版本、参数或 `ImageLibDotNet` 绑定结论。未来视觉切片仍须按项目 HALCON 26.05 手册和公开 `ImageLibDotNet` 调用边界逐项确定，不能将本来源的算子清单当作已批准 API。

- `H:\docs\40-development\80-quality\统计验收与计量能力开发指导.md`（SHA-256 `342a221c4ac34019c433fe0d83fb41abad8fb378df5e3594a36f8744ece33f89`）补充了可迁移的计量研究门禁：统计结论必须声明测量单位、总体/分层、聚类结构、样本来源、缺失/排除规则、方法版本、原始数据和限制；失败、缺失和 Unknown 保留原因，不能静默删样本或把数据不足写成通过。性能/任务时间按冻结起止事件和单调时钟分阶段，P50/P95/P99 不删除失败或超时样本。该内容作为未来 `MeasurementVerificationStudy`/资格消费者的输入要求，不是首片几何算法的统计 API。
- 来源中的最终样本量、`<10%/10-30%/>30%`、99.9% 等示例、GR&R 解释、客户质量门槛、AOI 缺陷分母、AI 指标和签署流程均不采纳为本模块默认值；只能由批准的 Consumer/Quality Profile 冻结。来源中的 Study/Report/Approval 状态、质量数据库接口和 UI 也不进入 Core Contract。

上述原始来源不改变附录 A 的旧 API。目标视觉/执行切片现在定位 §10–18；资产激活、CAS、签署和资格仍归宿主资产/质量 Owner，metrology 只消费冻结引用与回执，不增加这些事务 API。

## 10. 完整模块切片、独立工程与两个消费者

本节至 §18 是目标 `Module API Contract v0.2`。M1契约/纯几何/校验与M2注入端口下托管执行/受控Host已按主控接收记录达到 `ModuleCoreImplementationReady`，其余视觉适配、工程引用和生产资格分别保留门禁；本次状态同步不启动实现。源码存在与否、文档确定与否、规格准入与生产验收分别记录。

| 切片 | 唯一工程/命名空间与测试落点（目标，除 Core/Smoke 外尚未创建） | 责任及依赖 |
|---|---|---|
| M0 旧二维基线 | `src/Asun.Metrology.Core/`、`Asun.Metrology.Core`；`tests/Asun.Metrology.Core.Smoke/` | 保留附录 A；修订前先补异常/数值/文化差异回归，不把旧接口当成新规格 |
| M1 契约/纯几何/校验 | `src/Asun.Metrology.Contracts/` → `src/Asun.Metrology.Core/`；对应根命名空间；`tests/Asun.Metrology.Core.Tests/` | Contracts 仅 BCL/System.Collections.Immutable；Core 只依赖该 Contracts，不依赖产品或平台业务 Contracts。M0 的项目引用解除须另行获准并检查真实消费者，不在文档任务改项目 |
| M2 执行/模拟/恢复 | `src/Asun.Metrology.Runtime/`、同名命名空间；`tests/Asun.Metrology.Runtime.Tests/` | Runtime → Contracts/Core；模拟器是测试注入的后端，不新增假设备产品；状态、幂等、资源、取消、查询和关闭 |
| M3 2D 视觉/ROI 桥 | `src/Asun.Metrology.Halcon/`、同名命名空间；`tests/Asun.Metrology.Halcon.Tests/` | Halcon → 本模块Contracts/Core及批准AsunImage；§20桥仅引用CG/ROI/Serialization/SD/C5/RS公开契约与装配入口，不引用内部或WPF；Runtime由Host组合 |
| M4 3D 几何/表面/体积 | 纯几何仍在 M1；HALCON 路线仍在 M3 工程，独立测试分组 `Metrology3D` | 不因能力增多另建一套 Core；表面/基面由宿主公开端口提供，metrology 不重建/分割/拟合业务基面 |
| M5 外部接入/物理资格 | `tests/Asun.Metrology.HostTests/`（最小 Console Host，两消费者 fixture） | 宿主组合/版本映射测试，无 Shell/数据库/设备 SDK；真实样本/标准件和客户阈值属于独立资格门 |

将来获准实现时允许上述 metrology 工程/测试目录；禁止写其它模块内部、共享平台 DTO、产品流程、参考树、AsunImage 内部。本次仍仅写 DEVELOPMENT-GUIDE.md。发布 Contracts/Core/Runtime 可不带 Halcon；带视觉后端时单独附 Halcon 及批准依赖清单。独立构建以单个测试/Host csproj 为入口，不强制构建 AsunVision Shell 或整平台。

真实已批准复用方一是 IM-065 `measurement-workbench`：宿主取得 source/ROI/coordinate snapshot，映射成 §11 request，工作台只投影结果与状态。第二接入规格是无工作台依赖的 `BatchReplayHost`：读取宿主冻结的 2D/3D 样本清单，直接调用同一服务并导出结果到宿主 Store。它是接入验收 fixture/获批复用计划，不声称已有交付的第二视觉产品。二者分别注入 reader/backend/profile，各自 engine/OperationId/租约计数；不得共享可变模型或调用业务 Shell。相同原始证据和方法必须产生相同量值/支持；不同坐标或版本明确拒绝，不能拷贝公式到宿主。

**六项切片规格接收（2026-10-10）**：M1（v0.2契约/纯几何/校验）、M2（v0.2注入端口下托管执行/受控Host）、C1（v0.3连续截面/沿程/轴/有限平面/具名几何）、C2（有效域线性归约/连续矩）、C3（连续面积CDF/左逆）、C4（存储模型Q有理有界归约）均由主控按 `DEV-GOV-010 §3.1` 接收为 `ModuleCoreImplementationReady`。范围仅本模块冻结公开值、端口、托管kernel、受控fixture及双Host规格。不授真实ROI/surface/reference/coordinate字段映射、native算法/资源包络、真实工程引用迁移、构建/运行/性能/Golden/计量/现场准入；没有启动实现。

### 10.1 无 UI 与语言输出

metrology 无页面、窗口、图表或 WPF 控件，因此 DevExpress 25.2.3 控件选型、1920×1080 页面验证对本模块不适用。IM-065 已有 UI 边界不变；metrology 提供只读量值、稳定样本/候选 ID、误差和事件供联动，不接收显示纹理、LOD 截图或 UI 行号作测量输入。语言由宿主切换：错误输出 `MetrologyErrorCode` 与具名数值参数，不输出拼接英文句子；宿主将错误映射为简体/繁体/英文，如“坐标不匹配／座標不符／Coordinate mismatch”“未找到边缘／找不到邊緣／No edge found”“正在停止／正在停止／Stopping”“停止状态未知／停止狀態未知／Stop status unknown”。量值和证据不随语言/显示舍入变化，详细日志键与翻译分离。

## 11. 目标 v0.2 公开契约（Asun.Metrology.Contracts）

所有输入为不可变 record/值对象；数组使用 ImmutableArray，禁止 Dictionary、任意 JSON 参数和 native/SDK 句柄。构造 record 不等于校验通过。以下声明及表中的构造字段共同定义目标 API；类型表没有省略字段。`Geometry` 和 `SourcePayload` 是封闭派生联合，仅允许本文列出的 case，未知 case 返回 Unsupported。模块不接受调用方自报物理有效的布尔量。

### 11.1 单位、来源与几何

```csharp
public readonly record struct AssetRef(string Id, ulong Revision, string Sha256);
public readonly record struct OperationKey(Guid OperationId, uint RequestRevision);
public readonly record struct P2(double X, double Y);
public readonly record struct P3(double X, double Y, double Z);
public readonly record struct V3(double X, double Y, double Z);
public readonly record struct PixelPoint(double Row, double Column);
public enum Unit { Mm, Mm2, Mm3, Rad, Ratio, Pixel, Pixel2 }
public enum Scope { Engineering, CalibratedPhysical, PixelDiagnostic }
public enum Dimension { D2, D3 }
public enum DataKind { Geometry, Image, RegionRuns, Contours, TriangleMesh }
public enum Role { Subject, Reference, Boundary, Hole, SearchRoi,
    CheckSubject, CheckReference }
public sealed record SourceRef(AssetRef Content, AssetRef Frame,
    AssetRef? Calibration, DataKind Kind, Unit CoordinateUnit);
public sealed record CoordinateBinding(AssetRef SourceFrame, AssetRef TargetFrame,
    AssetRef Mapping, AssetRef? Calibration, AssetRef? ApplicabilityReceipt);
public sealed record InputOperand(string OperandId, Role Role, SourceRef Source);
public sealed record GeometryItem(string SampleId, Geometry Shape);
public abstract record Geometry;
public sealed record Point2(P2 Value) : Geometry;
public sealed record Point3(P3 Value) : Geometry;
public sealed record Segment2(P2 Start, P2 End) : Geometry;
public sealed record Segment3(P3 Start, P3 End) : Geometry;
public sealed record Line2(P2 Origin, P2 Direction) : Geometry;
public sealed record Line3(P3 Origin, V3 Direction) : Geometry;
public sealed record Plane3(P3 Origin, V3 Normal) : Geometry;
public sealed record Circle2(P2 Center, double Radius) : Geometry;
public sealed record Arc2(P2 Center, double Radius, double StartRad,
    double SweepRad) : Geometry;
public sealed record Rectangle2(P2 Center, double PhiRad,
    double HalfLength1, double HalfLength2) : Geometry;
public sealed record Sphere3(P3 Center, double Radius) : Geometry;
public sealed record Cylinder3(P3 AxisOrigin, V3 Axis,
    double Radius, double MinExtent, double MaxExtent) : Geometry;
public sealed record Ring2(string RingId, Role Role, ImmutableArray<P2> Vertices);
public sealed record Polygon2(ImmutableArray<Ring2> Rings) : Geometry;
public readonly record struct Triangle(int A, int B, int C);
public readonly record struct PixelRun(int Row, int StartColumn, int EndColumn);
public sealed record Contour2(string ContourId, bool Closed,
    ImmutableArray<P2> Points);
public abstract record SourcePayload;
public sealed record GeometryPayload(ImmutableArray<GeometryItem> Items) : SourcePayload;
public sealed record ContourPayload(ImmutableArray<Contour2> Contours) : SourcePayload;
public sealed record RegionPayload(ImmutableArray<PixelRun> Runs) : SourcePayload;
public sealed record MeshDomain(AssetRef Receipt, Polygon2 Footprint,
    ImmutableArray<string> UnknownFaceIds);
public sealed record MeshPayload(ImmutableArray<string> VertexIds,
    ImmutableArray<P3> Vertices, ImmutableArray<Triangle> Faces,
    MeshDomain? Domain) : SourcePayload;
public enum PixelType { Byte, UInt16, Float32 }
public sealed record ImagePayload(int Width, int Height, int RowStrideBytes,
    PixelType PixelType, ReadOnlyMemory<byte> Buffer,
    ImmutableArray<PixelRun> ValidPixels) : SourcePayload;
```

AssetRef 的 Id 非空且已 NFC，revision 明确，hash 为 64 位小写 SHA-256；大小写敏感，不截断/偷偷规范化。OperationId 不为 Empty，RequestRevision 从 1 起。所有点/方向/单位/维度先校验；长度坐标规范化为 mm 或明确的 PixelDiagnostic，角为 rad。方向归一化保留原方向，零长方向拒绝；平面 normal 决定正负。D2 目标为 X右/Y上；图像 row下/column右的轴置换与手性通过 Mapping 声明，不能写 X=Row 后假定数学方向仍相同。Triangle 索引有界且三个不同；像素 run 端点包含，同行不能重叠，按 row/column 排序；Contour 声称 Closed 仍须核首尾与拓扑；Region/XLD 不能混为同一采样模型。Image 只单通道，stride/buffer/valid pixels 经 checked 验证；reader 在租约期间保证不可改写底层内存，不能把 ReadOnlyMemory 误当原数据已冻结。

Revision从1起；ID按ordinal比较。Image宽高>0、stride≥Width×每pixel字节、Buffer至少stride×Height，像素中心索引从(0,0)起，UInt16/Float32按little-endian（图像量测本版仅Byte）；有效run必须在图像内。MetrologyCanonical.HashSource(lease.Payload)须与lease.Source.Content.Sha256相同；GeometryPayload的Items即使不可变也重核，source/frame/calibration refs与绑定不一致前置拒绝。Contour点序不排序；Mesh顶点索引与VertexIds一一对应，fit-only的Mesh可Faces.Empty，表面/体积方法必须非空faces。

### 11.2 请求、参数和结果

```csharp
public enum Method {
    PointDistance, PointLineDistance, PointPlaneDistance,
    PointSegmentDistance, SegmentDistance, ParallelLineGap, ParallelPlaneGap,
    LineAngle, PlaneAngle, PrimitiveSize, Area, AreaMoments,
    SurfaceArea, SurfaceDistance, HeightSummary, ResidualRange,
    ClosedVolume, DatumVolume, ProfileWidth,
    FitLine2, FitCircle2, FitPlane3, FitSphere3, FitCylinder3,
    ImagePrimitive2, ImageEdgePair2, AffineCalibration2
}
public enum AngleMode { Directed2D, Unsigned, Unoriented }
public enum VolumeMode { NetMagnitude, Absolute, Positive, Negative }
public enum Selector { Unique, All, NearestAnchor }
public enum FitRule { LeastSquares, Tukey }
public enum EdgeTransition { All, Positive, Negative,
    AllStrongest, PositiveStrongest, NegativeStrongest }
public enum Shape2 { Line, Circle, Arc, Ellipse, Rectangle }
public enum Interpolation { Nearest, Bilinear, Bicubic }
public sealed record NumericPolicy(double LengthTolerance, Unit LengthUnit,
    double RelativeTolerance, double AngleToleranceRad);
public sealed record FitPolicy(FitRule Rule, int MaxPoints, int ClipEndPoints,
    int Iterations, double ClippingFactor, double MaxClosureDistanceMm,
    double MinArcCoverageRad, int RandomSeed);
public sealed record SearchRectangle(PixelPoint Center, double PhiRad,
    double HalfLength1Px, double HalfLength2Px);
public sealed record EdgePolicy(double SigmaPx, double Threshold,
    EdgeTransition Transition, Interpolation Interpolation,
    ImmutableArray<SearchRectangle> Rectangles);
public sealed record ModelPolicy(Shape2 Shape,
    ImmutableArray<double> InitialPixelParameters, int NumMeasures,
    int MaxInstances, double MinSupportScore, int MaxRansacIterations,
    int RandomSeed, double MeasureLength1Px, double MeasureLength2Px,
    double DistanceThresholdPx);
public sealed record SupportPolicy(int MinimumSamples,
    double MinimumSpanMm, double MinimumAngularCoverageRad,
    double MinimumLatitudeSpanRad, double MinimumAxisSpanMm,
    double MaximumRmsResidualMm, double MaximumResidualMm);
public sealed record PrimitiveFit3Policy(double MinimumRadiusMm,
    double MaximumRadiusMm, V3 OrientationAnchor);
public sealed record AffinePolicy(double RankRelativeThreshold,
    double MaximumConditionNumber, double MinimumHullAreaMm2,
    int MinimumIndependentChecks, double MaximumCheckResidualMm);
public enum SurfaceSign { Unsigned, Oriented }
public sealed record MethodProfile(string ContractVersion, string MethodVersion,
    MetrologyDefinition Definition, SupportPolicy? Support,
    PrimitiveFit3Policy? PrimitiveFit3, AffinePolicy? Affine,
    SurfaceSign SurfaceSign, bool RequireQuantitativeUncertainty,
    ExecutionBudget Budget);
public sealed record MetrologyDefinition(Method Method, Dimension Dimension,
    Selector Selector, string? CandidateId, P3? Anchor,
    AngleMode AngleMode, VolumeMode VolumeMode,
    NumericPolicy Numeric, FitPolicy? Fit, EdgePolicy? Edge,
    ModelPolicy? Model, ImmutableArray<P3> ProfileStations,
    V3? ProfileDirection, double? MaxProfileHalfLengthMm);
public sealed record ExecutionBudget(int MaxInputElements, long MaxPairChecks, int MaxCandidates,
    int MaxOutputSamples, long MaxManagedBytes, long MaxNativeBytes,
    int MaxParallelism, TimeSpan ExecutionTimeout, TimeSpan DrainTimeout);
public sealed record MetrologyRequest(OperationKey Key, Scope Scope,
    AssetRef MethodProfile, ImmutableArray<InputOperand> Operands,
    CoordinateBinding Coordinates, MetrologyDefinition Definition,
    ExecutionBudget Budget);
public enum Validity { Valid, Invalid, Indeterminate }
public enum Outcome { Measured, Partial, Unevaluated, InvalidInput,
    Unsupported, Unqualified, Cancelled, TimedOut, ResourceLimited, Failed }
public enum QuantityName { Distance, MinimumDistance, MaximumDistance, Angle,
    Radius, Diameter, Length1, Length2, AxisLength, ArcLength, Area,
    CenterX, CenterY, CenterZ, MomentXX, MomentXY, MomentYY,
    PrincipalAngle, PrincipalVariance1, PrincipalVariance2,
    Volume, MeanHeight, MinHeight, MaxHeight, RmsResidual, MaxResidual,
    ResidualRange, ProfileWidth }
public sealed record NamedQuantity(QuantityName Name, double Value, Unit Unit);
public sealed record Support(string CandidateId, ImmutableArray<string> UsedIds,
    ImmutableArray<string> RejectedIds, ImmutableArray<string> UnknownIds,
    bool Complete, string ReasonKey);
public enum UncertaintyStatus { NotProvided, NotEvaluable, Propagated }
public sealed record Uncertainty(QuantityName Quantity, UncertaintyStatus Status, double? Standard,
    double? Expanded, double? CoverageFactor, double? CoverageProbability,
    Unit Unit, AssetRef? Model, ImmutableArray<string> MissingComponents);
public sealed record Witness(string SampleId, P3 Subject, P3 Reference,
    double Residual, Unit Unit);
public sealed record CoverageReport(int InputCount, int ObservedCount,
    double SpanMm, double AngularCoverageRad, double LatitudeSpanRad,
    double AxisSpanMm, double RmsResidualMm, double MaximumResidualMm);
public sealed record EdgeObservation(string SampleId, PixelPoint Pixel,
    P3 Mapped, double Amplitude);
public sealed record AffineEvidence(ImmutableArray<double> Coefficients,
    ImmutableArray<double> SingularValues, int Rank, double ConditionNumber,
    double SourceHullAreaMm2, double TargetHullAreaMm2,
    ImmutableArray<Witness> FitResiduals, ImmutableArray<Witness> CheckResiduals);
public sealed record VolumeEvidence(Plane3 IntegrationPlane,
    double PositiveVolumeMm3, double NegativeVolumeMm3,
    double ProjectionAreaMm2);
public sealed record MeasurementCandidate(string CandidateId,
    ImmutableArray<NamedQuantity> Quantities, Geometry? FittedGeometry,
    Support Support, ImmutableArray<Uncertainty> Uncertainties,
    ImmutableArray<Witness> Witnesses, CoverageReport? Coverage,
    AffineEvidence? Affine, ImmutableArray<EdgeObservation> Edges,
    P3? SelectionPosition, Validity Validity, MetrologyError? Error,
    VolumeEvidence? Volume);
public enum MetrologyErrorCode { InvalidRequest, CoordinateMismatch,
    InputUnavailable, InputHashMismatch, Unsupported, InsufficientSupport,
    DegenerateGeometry, AmbiguousCandidate, Unqualified, BudgetExceeded,
    BackendFailure, VersionMismatch, IdentityConflict, DrainUnknown,
    ReleaseUnknown, Cancelled, TimedOut }
public sealed record ErrorArgument(string Name, string Value);
public sealed record MetrologyError(MetrologyErrorCode Code, string MessageKey,
    ImmutableArray<ErrorArgument> Arguments, bool RetryWithNewRevision);
public sealed record EvidenceClosure(AssetRef Request, AssetRef MethodProfile,
    ImmutableArray<SourceRef> Sources, CoordinateBinding Coordinates,
    string ModuleVersion, string ContractVersion, string BackendVersion,
    string AdapterVersion, ImmutableArray<AssetRef> IntermediateEvidence);
public sealed record MetrologyResult(OperationKey Key, Outcome Outcome,
    Validity Validity, Scope Scope, ImmutableArray<MeasurementCandidate> Candidates,
    MetrologyError? Error, EvidenceClosure Evidence, string ResultFingerprint);
```

InitialPixelParameters 不是自由参数袋：Line `[row1,col1,row2,col2]`；Circle `[row,col,radius]`；Arc 同 Circle 加 start/end/point_order，Arc 的方向字段由已冻结 Profile 指定（v0.2 初版 ImagePrimitive2 不开放 Arc；返回 Unsupported，纯 Arc2/显式物理点拟合可用）；Ellipse `[row,col,phi,radius1,radius2]`；Rectangle `[row,col,phi,length1,length2]`。无关参数必须为 null/empty 或默认枚举零值；不是“忽略多余参数”。Ellipse 为图像拟合 case，其 FittedGeometry 在 v0.2 不开放，ImagePrimitive2/Shape2.Ellipse 返回 Unsupported；不得把它误当 Circle2。扩展具体椭圆几何须另修契约。Method、维度、operand 数量和实际 payload 按 §12 唯一选择，禁止只依据 enum 调用未知组合。

Measured = 单一定义完成；Partial 仅在 Selector.All 中有独立成功候选和明确失败/未知候选时使用；单一量的缺边/未知面积域/未完成体积不可用 Partial 值冒充整量，返回 Unevaluated，Candidates 可留诊断但不得留该完整量值。Invalid 是请求/输入违反契约；Indeterminate 是合法但观察不足/多解/资格无法证明；二者均不是工艺 NG。Fit 成功只表示 primitive 拟合事实；score 是支持率，不是概率、尺寸误差或质量状态。Outcome/Validity 不包含 PASS/NG，guard band 和质量放行只由宿主 Quality Owner 解释。

ErrorArgument 只用于本地化/诊断，固定每个错误 key 的参数名字；不载入额外运行参数。输出值必须有限；缺量用缺 NamedQuantity 表达，并由 Outcome/Error 说明，不能 NaN、-1、Infinity、0 代替。真实同点距离/已证实的零净量可以为零，必须保留支撑。数量/ID 预算不足拒绝请求或引用外部证据，不静默截断支持摘要。

### 11.3 端口与最小服务

```csharp
public interface IInputLease : IAsyncDisposable {
    SourceRef Source { get; }
    SourcePayload Payload { get; }
    LeasePhase GetReleaseReceipt();
}
public enum LeasePhase { Held, ReleaseUnknown, Released }
public interface IMetrologyInputReader {
    ValueTask<MethodProfile> ReadProfileAsync(AssetRef profile,
        ExecutionBudget budget, CancellationToken cancellationToken);
    ValueTask<IInputLease> AcquireAsync(SourceRef source, ExecutionBudget budget,
        CancellationToken cancellationToken);
}
public enum MappingKind { Identity, Affine2, Rigid3, Pointwise }
public sealed record MappingReceipt(CoordinateBinding Binding,
    ImmutableArray<P3> MappedPoints, Unit TargetUnit, MappingKind Kind,
    ImmutableArray<double> Coefficients, AssetRef Receipt);
public interface IMetrologyCoordinatePort {
    ValueTask<AssetRef> ValidateBindingAsync(CoordinateBinding binding,
        Scope scope, ExecutionBudget budget, CancellationToken cancellationToken);
    ValueTask<MappingReceipt> MapAsync(CoordinateBinding binding,
        ImmutableArray<P3> points, Unit sourceUnit, Scope scope,
        ExecutionBudget budget, CancellationToken cancellationToken);
}
public enum Phase { Accepted, Validating, Queued, Running, Completing,
    CancelRequested, Cancelling, Draining, DrainUnknown, Drained,
    ReleaseUnknown, ResourcesReleased, Completed, Rejected,
    Cancelled, TimedOut, Failed }
public sealed record MetrologyEvent(OperationKey Key, ulong Sequence,
    DateTimeOffset UtcTime, long MonotonicTicks, long MonotonicFrequencyHz, Phase Phase,
    long CompletedElements, long TotalElements, MetrologyError? Error);
public sealed record OperationSnapshot(OperationKey Key, Phase Phase,
    Outcome? PendingOutcome, MetrologyResult? Result, MetrologyError? Error);
public sealed record CloseReceipt(bool Closed, ImmutableArray<OperationSnapshot> Pending,
    int PendingNotifications);
public enum BackendPhase { Running, ExitUnknown, Exited, ReleaseUnknown, Released }
public sealed record BackendReceipt(OperationKey Key, BackendPhase Phase,
    MetrologyError? Error);
public interface IMetrologyExecution {
    OperationKey Key { get; }
    ValueTask<MetrologyResult> GetResultAsync(CancellationToken waitCancellation);
    BackendReceipt GetReceipt();
    void RequestCancel();
    ValueTask<BackendReceipt> ReleaseAsync(CancellationToken waitCancellation);
}
public interface IMetrologyBackend {
    string Version { get; }
    ImmutableArray<Method> Methods { get; }
    IMetrologyExecution Start(MetrologyRequest request, MethodProfile profile,
        ImmutableArray<IInputLease> inputs, IMetrologyCoordinatePort coordinates,
        Action<MetrologyEvent>? observer, CancellationToken cancellationToken);
}
public sealed record RuntimePolicy(int MaximumTrackedOperations,
    int MaximumConcurrentOperations, int MaximumNotificationItems,
    TimeSpan DisposeDrainTimeout);
public interface IMetrologyService : IAsyncDisposable {
    ImmutableArray<MetrologyError> Validate(MetrologyRequest request);
    ValueTask<MetrologyResult> MeasureAsync(MetrologyRequest request,
        Action<MetrologyEvent>? observer, CancellationToken cancellationToken);
    OperationSnapshot GetOperation(OperationKey key);
    bool RequestCancel(OperationKey key);
    ValueTask<CloseReceipt> CloseAsync(TimeSpan drainTimeout,
        CancellationToken waitCancellation);
}
```

公开组合入口还包括以下目标签名；实现分别位于 Core、Runtime、Halcon 根命名空间，不由宿主自行创建隐藏初始化对象。

```csharp
// Asun.Metrology.Core
public static class MetrologyValidator {
    public static ImmutableArray<MetrologyError> Validate(MetrologyRequest? request);
    public static ImmutableArray<MetrologyError> Validate(
        MetrologyRequest? request, MethodProfile? profile);
}
public static class GeometryMeasurements {
    public static MetrologyResult Compute(MetrologyRequest request,
        MethodProfile profile, ImmutableArray<SourcePayload> normalizedInputs);
}
public static class MetrologyCanonical {
    public static string HashRequest(MetrologyRequest request);
    public static string HashProfile(MethodProfile profile);
    public static string HashSource(SourcePayload payload);
    public static string HashResult(MetrologyResult result);
}
public sealed class GeometryBackend : IMetrologyBackend {
    public GeometryBackend(); // 接口成员严格实现 §11.3
}
// Asun.Metrology.Runtime
public sealed class MetrologyService : IMetrologyService {
    public MetrologyService(IMetrologyInputReader reader,
        IMetrologyCoordinatePort coordinates, IMetrologyBackend backend,
        RuntimePolicy policy); // 接口成员严格实现 §11.3
}
public sealed class MetrologyCloseException : Exception {
    public MetrologyCloseException(CloseReceipt receipt);
    public CloseReceipt Receipt { get; }
}
public sealed class MetrologyPortException : Exception {
    public MetrologyPortException(MetrologyError error);
    public MetrologyError Error { get; }
}
// Asun.Metrology.Halcon
public sealed class HalconBackend : IHalconMetrologyBackend {
    public HalconBackend(); // §20.1未配置实例，无窗口/native初始化
    public HalconBackend(HalconBackendOptions options, IMetrologyNativeObserver? observer);
    public HalconBackendSnapshot GetSnapshot();
    public ValueTask<HalconBackendCloseReceipt> CloseAsync(TimeSpan observationLimit,
        CancellationToken waitCancellation);
    public ValueTask DisposeAsync(); // IMetrologyBackend其余成员仍沿§11.3
}
```

以上类块是成员定位签名，省略接口实现体，不能作为本轮已可编译代码。Validate 是 total：null request/default arrays/非法 union/超限/非有限/格式错误转换为具名错误，不调用 reader、坐标端口、native 或 Store；OOM/进程终止不伪装业务返回。单参仅检查结构，双参另核 Profile 内容与请求一致；MeasureAsync 必须依次完成两层校验。GeometryMeasurements 只接受 §12.0 的 M1 方法和已映射数据，重新核 payload/type/budget；不处理 reader、native、资产批准和新证据存储。GeometryBackend 通过同一 coordinate port 映射后复用同一数学kernel，不拷贝公式。构造端口非 null，policy 字段正数/有限，非法构造抛 ArgumentException；构造不读取外部资料，不使用 ServiceLocator 或静态 global provider。reader、coordinate、backend 实例由宿主拥有，服务只拥有操作 execution/输入租约/自己的调度器；Close 不 dispose 注入的端口。

公开GeometryMeasurements.Compute只允许Engineering/PixelDiagnostic，normalizedInputs数量/顺序等于Operands，坐标已经处于TargetFrame，调用者负责该工程输入解释；它不能根据传入AssetRef自批CalibratedPhysical，直接请求该scope返回Unqualified。GeometryBackend的受监管内部入口复用同一数学kernel，在实际ValidateBinding/Map回执和租约证明后才保留CalibratedPhysical Scope；不对外暴露绕过端口的资格升级方法。归一化输入与raw source hash不相等是正常的映射结果，原始hash在reader获取阶段核，计算kernel不把mapped payload hash冒认raw content hash。几何direction通过线的两点映射求差；Rigid3的normal按旋转矩阵映射，Affine2线方向按J映射；非等距3D平面/球/柱映射Pointwise拒绝，不能对normal直接MapAsync当point。

MaximumTrackedOperations 覆盖成功、拒绝和未决记录，达到上限拒绝新 key 为 ResourceLimited/BudgetExceeded；本版不逐出旧 key 以免重复调用再次执行，宿主关闭旧 engine 后创建新 engine。MaximumConcurrentOperations 与 request.Budget.MaxParallelism 取较小值；MaximumNotificationItems 是通知队列上限，不得隐式创建无限订阅。GetOperation 未找到返回 Rejected + InvalidRequest 的 snapshot（PendingOutcome/Result null），不猜已完成。后端观察回调只能发进度，不发布终态；终态/序号/资源释放由 Runtime Owner 唯一生成。

MeasureAsync先执行结构Validate再接纳：结构无效（含null/非法key/default arrays/非有限/无法canonical）抛MetrologyPortException携首个Validate错误，零reader/native、不建立操作，调用方可以先Validate取得全部错误；不能为了返回record伪造非法请求hash。结构有效才canonical/Accepted；之后Profile/数据语义拒绝可返回InvalidInput/Unsupported等结果并按已取得资源完成release。GeometryMeasurements.Compute的非法结构同样抛该异常，合法请求上的无支撑/不支持返回结果；这些抛错均不是资源终态未知。Service.Close后新key以及tracked上限同样在接纳前抛对应MetrologyPortException，不伪建终态记录。

runtime 到期可完成等待者为 TimedOut/Cancelled/Failed 的无量值结果，同时 snapshot.phase 为 DrainUnknown/ReleaseUnknown、PendingOutcome 保留原因；此“等待返回”不是执行终态。直到 ResourcesReleased 才发唯一终态与可消费结果。normal MeasureAsync 返回已释放终态；若未知 snapshot 必须附 Error DrainUnknown/ReleaseUnknown，消费者先查询同 key，不盲重试。证据 closure 中的请求 hash 按 §15 生成，不持有 native 资源。发布产品事实/持久提交不属于接口。

MethodProfile 是可反序列化的完整配置：reader 核请求指定的原始引用及 §15 canonical 内容 hash 后返回不可变值，不返回“当前最新”。ContractVersion 必须为 `0.2`；MethodVersion 非空、绑定 backend 的支持版本。Definition/Budget 与请求逐字段相等（ImmutableArray 按内容比较，不用 record 数组引用相等），不一致为 IdentityConflict；不再从 UI/全局值补字段。无关 Support/PrimitiveFit3/Affine 必须为 null；SurfaceSign 仅 SurfaceDistance 生效，其它为 Unsigned；RequireQuantitativeUncertainty=true 本版 Unqualified，保留诊断量但禁止 Measured/Valid。Core 双参可在无 reader 情况下检验完整配置；Scope 不代替 Profile 资格。

本版支持的MethodVersion精确为`<Method枚举名>/1`（ordinal、区分大小写），其它值VersionMismatch；不能仅凭Methods enum列表忽略版本。方法参数改变产生新Profile revision/hash和请求revision；数学定义/求解路线/支持语义改变才升级MethodVersion，backend必须显式支持对应版本；单位或DTO编码改变按Contract破坏性版本处理。Version getters返回实际包AssemblyInformationalVersion与内容hash标识，Evidence.AdapterVersion为GeometryBackend/HalconBackend实际build标识，不填参考项目版本。

Support 仅拟合和 ImagePrimitive2 必填：MinimumSamples 至少 line2/circle3/rectangle8/plane3/sphere4/cylinder5；MinimumSpanMm>0，AngularCoverage 仅 circle/sphere/cylinder 在 (0,2π]，sphere LatitudeSpan 在 (0,π]，cylinder AxisSpan>0；无关覆盖字段为 0。RMS/max 上限有限>0且 max≥RMS，上限来自 Engineering Profile 或获批用途，不能默认生产精度。用全部观察点对拟合体计算残差来检查门，不因 Tukey 内部权重不可见而声称支持完整。FitCircle 覆盖为相对于拟合中心的排序角之 `2π-最大循环空档`；sphere 同算经度覆盖及纬度 max-min；cylinder 以轴正向、垂轴局部基算周向覆盖和沿轴 max-min；支撑跨度为点集最远点距离，有界分块计算，禁止 bbox 对角线代替。局部基取与轴最不平行的正坐标轴构造，等值按 X/Y/Z 排序，故结果可重算。

PrimitiveFit3 对三种3D拟合必填，OrientationAnchor 有限非零；球/柱 0<MinimumRadiusMm<MaximumRadiusMm，plane 两半径字段为0。plane/cylinder 输出方向与 anchor 点积正向；近垂直到 AngleTolerance 时 Indeterminate，不靠 HALCON 朝坐标原点的默认符号。sphere/cylinder 明确 least_squares 或 least_squares_tukey；plane 仅 LeastSquares，Tukey 为 Unsupported。HALCON3D适配内部统一转 meter（坐标、半径门÷1000），输出再转 mm、mm²、mm³；不把手册 meter 默认半径套到 mm 模型。

Affine 仅 AffineCalibration2 必填：RankRelativeThreshold∈(0,1)，MaximumConditionNumber>1，MinimumHullAreaMm2>0，MinimumIndependentChecks≥1，MaximumCheckResidualMm>0，全部有限。设计矩阵归一化后每行为 `[x,y,1]`，用 `svd_matrix('reduced','none')` 的三奇异值；rank 为 `s_i > s_0*threshold` 的数目，要求3且 `s_0/s_2≤MaximumConditionNumber`。源和目标拟合集凸包面积均≥最小面积；至少规定数量的独立 CheckSubject/CheckReference 对，检查最大残差≤门。门不满足返回 Indeterminate/InsufficientSupport，不产生资格。该拟合求解是 M3，纯 Core 不被迫另写 SVD 或引入 Math.NET 产品依赖。

MappingReceipt 按输入顺序返回相同数量的点，D2 使用 Z=0；TargetUnit 只为 Mm/Pixel。Identity 系数为空；Affine2 六系数按附录 A 的矩阵方向；Rigid3 为 row-major 3×3+平移三项，核正交/行列式+1；Pointwise 系数为空。Region面积/矩只接受 Identity/Affine2 的回执，不能从若干点自行推断 Jacobian。输入 primitive 的半径/方向等只允许等距或已明确的相似变换；非相似映射下需要原观察点重拟合，否则 Unsupported。普通量测全部 operands 在同一 SourceFrame/CoordinateUnit，经请求同一 Binding 到同一 TargetFrame；宿主先统一不同 frame，模块不猜多FOV映射。AffineCalibration2 特例：Subject 与 CheckSubject 是源 frame，Reference 与 CheckReference 是 target frame，禁止预映射拟合源点；只由 coordinate port 核两 frame/单位身份，本请求求的是新映射，不使用旧映射代替求解。

端口预期故障抛MetrologyPortException携带下表错误；OperationCanceledException只在已登记取消时解释为取消，其它意外异常归BackendFailure，不根据异常文本猜错hash/资格。Arguments中所有数值InvariantCulture round-trip，键名如下；不混入任意参数。MessageKey固定`metrology.`加Code名称，不因语言变化。RetryWithNewRevision=true只表示修复原因后可新尝试，不授权重试设备或未决native。

| ErrorCode集合 | 唯一参数（均string，可空数组但不能增键） | RetryWithNewRevision |
|---|---|---|
| InvalidRequest、Unsupported、VersionMismatch | `field`,`reason` | true |
| CoordinateMismatch、Unqualified | `assetId`,`reason` | true |
| InputUnavailable、InputHashMismatch | `assetId` | true |
| InsufficientSupport、DegenerateGeometry、AmbiguousCandidate | `candidateId`,`reason` | true |
| BudgetExceeded | `limit`,`actual` | true；先确认旧资源已释放 |
| IdentityConflict | `operationId`,`revision` | true；旧操作仍保留 |
| BackendFailure | `stage`,`reason` | true仅在ResourcesReleased后；未决时false |
| DrainUnknown、ReleaseUnknown、Cancelled、TimedOut | `operationId`,`revision` | Unknown为false；取消/超时释放后true |

失效/资格不足返回Unqualified/Indeterminate；合法空观察返回Unevaluated/InsufficientSupport；未知发布权状态没有量值候选。没有backend版本可记`not-started`，不假造HALCON版本；Evidence.Sources仍保原输入refs，错误closure也有可复算request hash。ResultFingerprint在最终snapshot/返回内容形成后计算；通知的时间/进度不改变该hash。

## 12. 逐量测定义、支撑域与解析断言

每个 operand 内几何/点必须按稳定 SampleId 排序，无重复；按 table 规定的单一 shape 或数据集消费。Selector.Unique 要求恰有一个候选；All 返回每个独立候选的值/支持；NearestAnchor 按目标坐标欧氏距离与 Profile 选择，等距到 Numeric tolerance 时为 AmbiguousCandidate，绝不按“最接近公差”选取。CandidateId 显式非空时只取该稳定候选，缺失拒绝。结合异步请求身份不得使用 HALCON tuple 下标充当跨执行对象 ID。

### 12.0 operand 与字段闭合表

下表穷举 Method；数字为 operand 个数，顺序和 Role 严格一致，额外 operand 返回 InvalidRequest。所有普通方法先 ValidateBindingAsync，再取得租约、检查 payload 与 SourceRef.Kind、映射观察点、计算；拟合变换的例外见下表。M1 只含表中的 pure 方法，不包含图像、所有拟合、Region/XLD或 mesh native 方法。几何 Polygon2 的面积/矩可在 M1 解析计算；Region/Contour及所有M3/M4视觉路线属于 HalconBackend。GeometryBackend.Methods 精确回显 M1 方法，包含 Area/AreaMoments 时仍对非 Geometry payload 返回 Unsupported；不能仅按 enum 声称全输入路线已支持。

| Method 集合 | 数量、Role 和 payload | 专用字段/切片 |
|---|---|---|
| PointDistance/PointLineDistance/PointSegmentDistance/SegmentDistance/ParallelLineGap/LineAngle | 2：Subject、Reference；每个 GeometryPayload 恰1个 §12.1 同维 shape | AngleMode 仅角方法生效；M1 |
| PointPlaneDistance/ParallelPlaneGap/PlaneAngle | 2：Subject、Reference；恰1个规定 Point3/Plane3 | D3；M1 |
| PrimitiveSize | 1 Subject；GeometryPayload 一个或多个相同 shape，分别成候选 | M1；不将多shape合并为单件 |
| Area/AreaMoments | 1 Subject；单 Polygon2、RegionPayload或闭合 ContourPayload | Contour初版恰1个外环，无孔；孔用 Polygon2 显式 Ring2.Role；M1/M3 |
| FitLine2/FitCircle2 | 1 Subject；ContourPayload每 Contour2 为独立拟合集 | Fit/Support必填；M3 |
| FitPlane3/FitSphere3/FitCylinder3 | 1 Subject；GeometryPayload全部 Point3 或 MeshPayload 顶点 | Fit/Support/PrimitiveFit3必填，Fit.MaxPoints=-1/ClipEndPoints=0；M4 |
| ImagePrimitive2 | 2 Subject ImagePayload、SearchRoi RegionPayload | D2；Model/Edge/Fit/Support必填；Edge.Rectangles为空，由model生成scans；M3 |
| ImageEdgePair2 | 2 Subject ImagePayload、SearchRoi RegionPayload | D2；Edge必填，Rectangles非空；Fit/Model/Support为空；M3 |
| SurfaceArea/ClosedVolume | 1 Subject MeshPayload | D3；ClosedVolume仅 VolumeMode.NetMagnitude；M4 |
| SurfaceDistance | 2 Subject Point3集合、Reference MeshPayload或恰1 Plane3 | D3；Profile.SurfaceSign生效；M4 |
| HeightSummary/ResidualRange | 2 Subject Point3集合、Reference恰1 Plane3 | D3；M1；每点等权，集合归约一个候选 |
| DatumVolume | 2 Subject MeshPayload、Reference恰1 Plane3 | D3；VolumeMode生效；M4 |
| ProfileWidth | D2：1 Subject ContourPayload；D3：2 Subject MeshPayload、Reference恰1 Plane3 | stations/direction/half length必填；D2站Z=0、direction.Z=0；D3站到截面距离≤Numeric.LengthTolerance、direction与normal正交到AngleTolerance；M3/M4 |
| AffineCalibration2 | 4：Subject、Reference、CheckSubject、CheckReference；各 GeometryPayload全部 Point2 | D2；Fit为空（本版纯LS），Profile.Affine必填；前两集合拟合、后两集合检查，各自按 SampleId 配对，检查ID与拟合ID不相交；M3 |

无关 AngleMode=Directed2D、VolumeMode=NetMagnitude（枚举零值），Fit/Edge/Model=null，ProfileStations=Empty、Direction/half length=null；非轮廓 Fit 禁止生效字段含糊：3D Fit.Rule生效，Iterations/ClippingFactor/Closure/ArcCoverage/Seed取0且不用，原生拟合无这些可设置参数；2D LS不生效的Iterations/ClippingFactor取0，Tukey按§13必填；2D圆MinArcCoverage与Profile.Support.MinimumAngularCoverageRad一致。NearestAnchor 专用 Anchor 非空，CandidateId为空；显式CandidateId只允许 Selector.Unique且Anchor=null；Unique/All 不带Anchor。预算限制候选和输出；不设置隐含搜索半径，NearestAnchor在全部有限候选上选择。D2全几何/站/anchor Z=0，ProfileWidth以station输入序号与交点投影顺序输出，不能将站顺序当样本偶然顺序。

每个候选的 ID：显式几何/Contour使用原 SampleId/ContourId；点对用两operand ID与SampleId的长度前缀canonical摘要；image实例先对规范化拟合参数及原边坐标排序，再以该内容SHA-256作ID，相同内容合并并保全部支持ID，不用HALCON实例下标。mesh face ID按规范输入face索引；Contour点ID为ContourId加长度前缀的点序号。SelectionPosition为单点自身、点对witness中点、primitive中心、线拟合支持点均值、扫描站、mesh/区域的真实面积中心；没有定义有限位置的候选不支持NearestAnchor（Unsupported），不能给无界Line/Plane任意origin当“最近”。

Witnesses 固定对应距离最近/最远点对或逐点 residual；用于量名的顺序为MinimumDistance后MaximumDistance，其它按SampleId；SurfaceDistance每subject点为一个candidate，输出Distance与最近点witness，mesh有符号用面方向约定、Plane3用normal，Unsigned取abs。HeightSummary/ResidualRange为一个集合候选，逐点witness与缺项都保留。拟合输出geometry及RmsResidual/MaxResidual，圆/球/柱/矩形同时按PrimitiveSize量名输出；ImageEdgePair输出Distance并保Edges的原像素/物理点/amplitude；primitive的Edges需保全部可读实测边。AffineEvidence六系数顺序同附录A，FitResiduals/CheckResiduals分开；不再把尚未写Store的系数藏在AssetRef中。

MeasurementCandidate.Validity/Error用于Selector.All中的独立失败候选；失败候选Quantities为空、FittedGeometry=null，Support保原因；整个Result.Partial/Indeterminate。Unique单候选成功为Measured/Valid，全部失败为Unevaluated/Indeterminate；InvalidInput/Unsupported为Invalid，其它取消/超时/失败为Indeterminate。Uncertainty逐量名恰一项；当前仅NotProvided/NotEvaluable且数值字段全null，Propagated输入或输出拒绝。Coverage/Affine/Edges只在上列相应方法生效，否则null/Empty。结果全部有界，证据过预算返回ResourceLimited，不能静默省掉必需witness/支持。

### 12.1 距离、角度和尺寸（M1/M3/M4）

| Method / 输入顺序 | 完整定义与输出 | 必须拒绝或明确分支；合成例断言 |
|---|---|---|
| PointDistance；2 Point2 或 2 Point3 | 欧氏距离 Distance mm；以缩放 hypot 避免中间平方溢出 | 同点合法为 0；超可表示范围 Failed/Numeric，不返回 Infinity；(0,0,0)→(3,4,12)=13 |
| PointLineDistance；Point + 同维 Line | 无界线正交距离，2D 用交叉积模/方向模，3D 用叉积模/方向模 | Line.direction 不能为零；与有限段区别；(3,4) 到 X轴 =4 |
| PointPlaneDistance；Point3+Plane3 | `dot(p-origin,n)`，n 单位化且保留方向；Distance 是 signed mm | normal 零拒绝；反转 normal 则符号反转，不能 abs 消去；z=-2到Z=0,n=+Z 为 -2 |
| PointSegmentDistance；Point+同维 Segment | 投影参数 clamp 到 [0,1]；输出 MinimumDistance、MaximumDistance（最大端点距离） | 零长段退化为点，不产生方向；(2,1) 到 (0,0)-(1,0) min=√2,max=√5 |
| SegmentDistance；2同维 Segment | 有限线段最短点对（约束 s,t∈[0,1]），最大距离为四端点距离最大值 | 3D 解双参数候选并检查四边界，近平行只走边界/投影稳定分支；相交 min=0；保留 witness ID |
| ParallelLineGap；2同维 Line | 先以无向角≤AngleTolerance 验证平行，再求正交间距 | 非平行/斜交线没有通用“线距”，Unsupported/定义不适用；不求四端点平均；两条 y=0/5 得5 |
| ParallelPlaneGap；2 Plane3 | 检查平行，统一到 Reference normal 后求 signed offset | 非平行不得输出常量间距；基面变化新 revision；Z=0到Z=2、参考+Z得2 |
| LineAngle；2同维 Line | Directed2D `atan2(cross,dot)` 规范到 (-π,π]；Unsigned `atan2(|cross|,dot)`∈[0,π]；Unoriented 使用 `abs(dot)`∈[0,π/2] | Directed2D 用于D3拒绝；零方向拒绝；反向向量 unsigned=π、unoriented=0；夹角不是机械垂直度验收 |
| PlaneAngle；2 Plane3 | unsigned/unoriented normal angle 同上，Angle rad | Directed2D 不适用；normal 可比较不代表平面距离定义适用 |
| PrimitiveSize；1 Circle2/Arc2/Rectangle2/Segment/Sphere3/Cylinder3 | Circle/Sphere radius/diameter；Arc 还返回 r×abs(sweep)；Rectangle 返回2×half lengths；Segment length；Cylinder radius/diameter和extent差 | radius/half length>0，Arc |sweep|∈(0,2π]，Cylinder max>min；有些厂商中心不是重心；不拿 bounding box 当实测尺寸 |
| ImageEdgePair2；Image + SearchRoi | 每条扫描轴上的实际边缘对转换物理坐标再输出 Distance，非等距像素不乘单一比例 | 一条边、弱幅值、mask缺口、多对未选择→Unevaluated；记录 amplitudes、raw/mapped points和采样方向 |
| ImagePrimitive2；Image+冻结初值 | 采边→拟合 line/circle/rectangle→物理点重拟合/量测；result raw像素与物理几何分开 | 非等距/非线性变换禁止“半径×scale”；ellipse/arc初版未开放不得默降圆；裁剪导致闭合假象拒绝 |

2D width 仅指测量轴上两条实测边交点距离或矩形完整拟合边长。圆/矩形/线点集来自上游 segmentation/features 或本请求的显式 image ROI，不在 metrology 按工艺自动搜索对象。定量“平行度/垂直度/共面度/平面度”需要明确 GD&T 被测量及基准/关联算法；v0.2 仅返回角、参考面有符号残差或 ResidualRange，不称 ISO 最小区域平面度或产品共面合格。

### 12.2 拟合、标定与误差（M1/M3/M4）

FitLine2/ContourPayload 逐单轮廓拟合，不做分割；FitCircle2 逐单圆/弧点集至少3点且不共线；FitPlane3/MeshPayload 使用顶点或 GeometryPayload 的 Point3，至少3个非共线，支持域不能由基面预期尺寸代替。FitSphere3/FitCylinder3 用公开点集和 HALCON primitive 结果，需支撑跨空间/周向/轴向的 Profile 最小覆盖；点数足够不证明球/圆柱可辨识。输出 FittedGeometry、RmsResidual/MaxResidual、全部原点/实际使用点/排除理由和空间覆盖。Tukey 内部权重不可见时不得伪造后端精确 inlier 列表：列“输入点+逐点残差+可见 used support”，不可见权重/剔除声明为 Unknown，必须另有支持门防过拟合。拟合 score/残差不是物理不确定度。

AffineCalibration2 接受 Subject/Reference 两套 SampleId 一一对应的 Point2，不按列表偶然位置配对；至少3个非共线且跨声明覆盖域。旧正规方程作为 M0 历史数值方法；目标将源/目标平移到各自中心、缩放到 RMS 尺度，rank/条件数按 §11.3 SVD 门核对，调用 HALCON `vector_to_hom_mat2d` 求解后反归一；独立检查集不能复用拟合集。返回 AffineEvidence 六系数、RMS/max、逐点残差和覆盖报告；不自动创建/激活 calibration asset。矩阵/normal/方向反转、近奇异和镜像必须按 Frame convention 判定；只要不同手性已明确就不一律拒绝负 determinant。缺 Profile.Affine 前置 InvalidRequest，不能把少了条件门的拟合当 Engineering 成功。源/目标单位本版均须 Mm，像素标定作为新映射由 coordinate Owner 消费另行映射，不强行塞入同单位最小面积门。

### 12.3 面积、矩、表面与体积（M3/M4）

| Method / 输入 | 唯一定义与路由 | 支撑/反例与期望 |
|---|---|---|
| Area；RegionPayload | 像素 cell 数；affine 映射时乘 |det(J)|，输出 mm²；PixelDiagnostic 才为 pixel² | run并集已由ROI Owner定义，无重复面积；空 Region 无量值；非线性映射当前 Unsupported，须后续冻结有误差界的单元积分 |
| Area；Polygon2/已闭合 ContourPayload | 连续平面 Green 定理面积，outer减hole；中心为面积加权中心 | 在调用 area_center_xld 前拒绝开轮廓、自交、孔越界/相交；不让 HALCON 自动闭合当实测；2×2外环减1×1洞=3 |
| AreaMoments；同上输入 | 中心化面积协方差 MomentXX/XY/YY，单位 mm²；非归一化二阶面积矩不是同一量 | Region moments是每像素统计；对矩阵 C 用 J C Jᵀ，region cell内惯性是否包含由本版声明为“不包含”；PrincipalVariance1/2 为 eigenvalues，不是尺寸；等特征值不返回伪 PrincipalAngle |
| SurfaceArea；MeshPayload | 三角面片真实表面积 sum(0.5|cross|)，mm²；固定face顺序 | 重叠/重复面、零面和拓扑异常拒绝；不是 XY投影面积；三角(0,0,0),(1,0,0),(0,1,1)面积√2/2 |
| SurfaceDistance；点集+MeshPayload或Plane3 | subject每点到指定 target triangles/primitive 的距离及 witness；后端有符号距离仅在法向合格时允许 | 明确 distance_to，不让HALCON按属性隐式换target；MaxDistance=0防截断；不以 point-mean/bbox center 当表面距 |
| HeightSummary；Point3集合+Reference Plane3 | signed residuals；MeanHeight 按等样本权重、Min/MaxHeight；原点等权统计不称面积平均高度 | mask缺点明确Unknown；sampling revision不同不混合；负高度保留；z={-1,2,5}得mean=2,min=-1,max=5 |
| ResidualRange；同上 | max signed residual - min signed residual，mm | 这是对给定基面的残差范围，不是最小区域平面度；不自动重拟合基面消掉缺陷；上述样本range=6 |
| ClosedVolume；watertight有向Mesh | HALCON relative_to_plane(signed,true)的体积 magnitude，mm³；基准选模型邻近，避免远基面消减 | 每edge恰两face、反向配对、无自交/重复face，orientation一致；不满足为Indeterminate；不补洞；单位立方正确；边长1立方体=1 |
| DatumVolume；已冻结有限单值 height surface Mesh+Reference Plane3 | 对明确域内face投影棱柱积分；Mode NetMagnitude/Absolute/Positive/Negative对应HALCON signed/unsigned/positive/negative，UseFaceOrientation=false | 净模式输出绝对值，名为 NetMagnitude、不承诺 signed integral；face跨基面先按零线裁成正/负三角再积分；投影重叠/多层不是单值域，拒绝；signed积分另切片，不用native绝对值伪造 |
| ProfileWidth；ContourPayload/MeshPayload+Reference截面/扫描站 | 2D finite线与轮廓相交；3D intersect_plane_object_model_3d后每站扫描；按方向投影、去重、有限半长内成对交点，width mm | 重叠线段/切触/奇数交点/多个区间不默认取外包距离；有明确CandidateId才选区间，否则All或Ambiguous；本版不做隐式平滑/重采样 |

Volume 只积分已知域：未知缺口不是合法孔洞；孔洞由输入显式声明边界并排除，未观测部分不得估值。正/负模式负部输出也是体积 magnitude，不是负数；net=0若正负抵消须保留两部中间证据，否则不能宣称“无材料”。封闭体积和基面体积不能互换；把 voxel点数、µm高度或pixel面积称体积拒绝。

Polygon2每环至少3个不同顶点，首尾闭合由最后→首的边隐式定义，不重复末点；外环Role.Boundary恰1个，Hole环全部严格在内且两两不交，边界接触到Numeric tolerance时Indeterminate。对每环顺序边 `(x_i,y_i),(x_j,y_j)` 令 `c=x_i*y_j-x_j*y_i`，raw面积为Σc/2、raw一阶矩为Σ(x_i+x_j)c/6和Σ(y_i+y_j)c/6，raw二阶为Σ(x_i²+x_ix_j+x_j²)c/12、Y对称、XY为Σ(2x_iy_i+x_iy_j+x_jy_i+2x_jy_j)c/24。先按环实际方向换成正面积，再按Boundary正/Hole负汇总；中心为一阶/总面积，中心协方差为二阶/总面积减中心外积。计算先平移邻近原点并用补偿和，最后还原中心；近零总面积拒绝而非除零。Area只返回Area；AreaMoments返回Area/CenterX/Y/MomentXX/XY/YY/PrincipalVariance1/2及可辨识PrincipalAngle；主轴角在[0,π)，两特征值差≤relative tolerance×最大特征值时缺PrincipalAngle并明确ReasonKey。Region中心使用像素中心点（column,row），通过Binding到数学坐标；像素cell内惯性不计入矩，与连续Polygon采样模型明确分开。

Mesh先核vertex IDs、finite、face索引、重复无向face与零面积；有向edge相邻表、bbox有界宽阶段后逐对三角交检查。相邻面只允许登记共享边/点，非相邻面不得接触/穿插；共面相交通过投影到最大法向分量平面做二维边交/内点检查，不以最短顶点距替代。受预算的空间分块可减少候选，但不能漏共面/长瘦face；总配对数超预算时ResourceLimited，不猜无自交。ClosedVolume另要求每edge恰两face、方向反向配对且组件orientation一致；多个封闭组件允许但不得交叠。DatumVolume投影到Reference plane局部基检查三角域内不重叠/多层，再按signed height线性插值把跨零边裁成正/负多边形并扇形三角化，零线点只归一侧一次。显式合法孔是mesh中没有face的域；输入缺失观察不能单凭无face被认定合法孔，须宿主Source证据证明有限域完整，否则Unqualified。此拓扑/支撑校验是前置合同检查，体积/表面求值仍走已冻结HALCON路线。

MeshDomain仅DatumVolume必填，其它mesh方法为null；Footprint坐标位于Reference plane以§11.3同规则确定的局部基、原点为Plane3.Origin，表示显式Boundary/Hole有限投影域。reader负责核Receipt绑定精确Content/Frame/该基面/域版本且来源证据原子封存，错误抛Unqualified；不接受调用方自报“完整”。Domain.Receipt是宿主资产证据引用，其hash不能引用含自身Receipt的完整MeshPayload产生循环：宿主receipt绑定MetrologyCanonical.HashSource(mesh with { Domain=null })及frame/plane/Footprint/UnknownFaceIds，完整source hash随后覆盖Domain引用。UnknownFaceIds非空或face投影并集与Footprint不等（差集面积超Numeric.LengthTolerance²）为Unevaluated，不补面。VolumeEvidence直接保实际积分基面、正/负部magnitude及投影面积；DatumVolume四mode都保两部，net由abs(positive-negative)，negative也非负。ClosedVolume基面取vertices算术中心与+Z方向，仅为邻近数值基准，ProjectionAreaMm2=0（不适用）、正/负部不作为材料分区解释。该证据只能由backend生成，不把内部基准自动升级为业务datum。

ProfileWidth每站先核相交位置在finite半长内，重复交点按LengthTolerance合并，但切触不形成穿入/穿出。2D要求闭合、无自交轮廓；3D截面使用Reference Plane3，切面轮廓同样核闭合与拓扑；扫描direction留在截面中。按沿direction投影排序后按内外奇偶成连续区间，零宽/tangent/重叠边拒绝；每区间CandidateId为station序号+区间两端内容hash，按Selector取一或All。不得把多个区间间的空隙纳width。返回width、station位置、两个witness点；方向反转只改变witness顺序，不改变width。

FitLine2只接受open contour，输出单位Direction与末点-首点同向；首末无法定向拒绝。FitCircle2 open contour输出Arc2，按原遍历相邻角差unwrap得Start/Sweep，跨多圈/方向反复到AngleTolerance拒绝；closed contour输出Circle2，声明闭合仍须核实际gap/topology/覆盖。3D plane/cylinder方向按OrientationAnchor，Cylinder.AxisOrigin规范到轴线上距全局原点最近点，Min/MaxExtent从全部观察点沿该轴投影定义，故不依赖HALCON任意primitive中心；球中心直接求值。残差用点到无限线/圆径向/平面signed/球径向/无限柱径向定义，RMS统一sqrt(sum(residual²)/n)、max为最大绝对值；端点/轴extent不是圆柱侧面拟合残差门。

SurfaceDistance请求Unsigned就显式signed_distances=false；Oriented显式true，mesh面朝向一致且最近面反侧为负、Plane沿normal侧为正。最近foot落共享edge/vertex且不同最近face给不一致符号时Indeterminate/AmbiguousCandidate；unsigned等距witness按face规范ID取最小者并保支持，不以tuple顺序猜。HALCON最近索引只用于定位三角，witness须在该face上算投影/clamp验证实际距离；索引不可读或无法证明witness为BackendFailure，不伪造bbox/vertex位置。

## 13. HALCON 26.05 主路线、参数与 ROI 粗精分支

手册目录均为项目 `halcon算子手册/operators`，每行实际核对 Description/Attention/Parameters/Execution Information。下表冻结功能路线，候选仅作为方法版本对比，不允许运行时自动改路；没有同样本数据，未声称任何路线最快或已达精度。

| 能力 | 本版主路线（cv2 算子） | 有实质差异的候选及选择条件 |
|---|---|---|
| 已有点/线/段 | M1 已知几何解析计算；adapter用 `distance_pp`、`distance_pl`、`distance_ps`、`distance_ss`、3D `distance_point_line` 作公开视觉桥/一致性基线 | 无界 distance_pl 与有限 distance_ps 不等价，禁止用前者代后者；纯几何不增加图像/native成本 |
| 2D line angle | `angle_ll`，转换到本契约轴/方向与范围；纯几何atan2作解析检查 | 反序点/手性变化影响signed角，cannot靠abs“修复”；3D用明确定义normal/vector角 |
| 图像边缘对 | `gen_measure_rectangle2 → measure_pairs → close_measure`；一次请求多个有限扫描矩形 | `measure_pos`仅单边诊断，不补全width；fuzzy_*未冻结隶属函数，不进入本版；曲边改用模型，不能用直边前提测弯曲目标 |
| 图像line/circle/rectangle | `create_metrology_model → set_metrology_model_image_size → add_metrology_object_*_measure → set_metrology_object_param → apply_metrology_model → get_metrology_object_result/get_metrology_object_measures → clear_metrology_model` | 多局部scanline聚合只有同定义/支撑/Profile对比通过后成为新方法版本；弱信号不隐式放低阈值或扩大ROI；ellipse/arc本版不开放 |
| 已分割的2D线/圆轮廓 | `fit_line_contour_xld('tukey')`；圆/弧 `fit_circle_contour_xld('geotukey')`，按本版物理域拟合 | regression/algebraic更少鲁棒处理/计算，geometric与algebraic目标不同；LeastSquares Profile 显式选择regression/geometric；不据残差选最接近期望尺寸的算法 |
| Region面积/矩 | `area_center`、`moments_region_2nd`；空域前置拒绝 | 连续XLD `area_center_xld`、`moments_xld`是另一输入语义；不自动像素化/补闭合；`test_self_intersection_xld`前置查自交 |
| 3D面/球/圆柱拟合 | `fit_primitives_object_model_3d`，明确primitive_type；plane强制least_squares，sphere/cylinder Tukey显式策略；`get_object_model_3d_params`查结果 | 算子不分割点集，不能把混合目标一起拟合；plane的各种fitting_algorithm手册说明结果相同，不声称Tukey plane已排离群；鲁棒plane另方法切片 |
| 表面distance/area/剖面 | `distance_object_model_3d` 指定distance_to='triangles'、method='kd-tree'，primitive时显式primitive/method='linear'；`area_object_model_3d`；`intersect_plane_object_model_3d` | triangles kd-tree 与 linear候选同样本查建立成本/峰值/重复查询；voxel近似不进入精确路线；3D点mean不能作体积中心 |
| 基面/闭合volume | `volume_object_model_3d_relative_to_plane` 显式 Mode/UseFaceOrientation，先裁跨零面，核single-valued/closed条件 | 手册输出abs(sum)，不能直接作为signed volume。高度栅格积分尚未冻结cell规则，先由上游提供有效mesh，不自动三角化/补洞 |
| affine求解/像素变换 | `vector_to_hom_mat2d`；`affine_trans_point_2d`/`affine_trans_pixel`根据映射定义选 | 两者相差pixel-center/corner 0.5转换；不能全局加减0.5或混用已变换XLD；v0.1正规方程不作为跨尺度稳健性证据 |
| affine数值门与物理矩形重拟合 | `create_matrix → svd_matrix('reduced','none') → get_full_matrix → clear_matrix`；`fit_rectangle2_contour_xld`（Tukey或regression显式映射Fit.Rule） | reduced SVD避免full U，回执保存奇异值；矩形至少8点且每边有内点，缺一边/原生3266是InsufficientSupport，不返回bbox尺寸 |

### 13.1 参数有效域与变更

所有参数由 §11 的 MethodProfile 显式给出，并与 request.Definition/Budget 逐值比较，hash不匹配拒绝；下列范围是 API/数值有效域，不是客户质量阈值。Profile 内容由 ReadProfileAsync 取得并校验，不从UI当前值/进程set_system取得。配置读取仍按来源hash、预算和取消，独立于native句柄。

| 参数 | 有效域/单位和固定分支 | 默认/来源 |
|---|---|---|
| Numeric.LengthTolerance/LengthUnit | 有限>0；Engineering/CalibratedPhysical为Mm，PixelDiagnostic为Pixel，用于点去重和拓扑边界；方向零值检查用模与relative门，不把mm当单位方向阈值 | 无客户通用值，缺失InvalidRequest；不是工艺公差 |
| RelativeTolerance、AngleToleranceRad | relative∈(0,1)，angle∈(0,π/2)，用于条件/平行检查 | Profile明确，禁止double.Epsilon当工程容差 |
| SigmaPx | 26.05 measure手册范围[0.4,100]，且≤0.5×扫描HalfLength1Px | 无生产默认，0不是“不平滑”合法选项 |
| Threshold | 26.05手册列[1,255]，本版仅Byte图像该路线；UInt16/Float32源可保存但本版图像量测Unsupported | Profile值；不得偷偷normalize到byte后改响应单位 |
| Edge.Transition | pairs: all/positive/negative及*_strongest；metrology:all/positive/negative（目标联合不含uniform，因此本版不启用） | 明确枚举映射；strongest是pair transition模式，不是Select枚举 |
| 内部Select | always all，返回全部原边/实例后执行Selector规则 | 不能先first丢信息再说Unique；同分/多候选不顺序猜 |
| SearchRectangle | 全部有限，half lengths>0，中心/旋转和有效mask有完整支撑；bilinear额外1px、bicubic额外2px图像边距 | Profile/冻结ROI快照；gen_measure中心内部像素取整事实写入诊断 |
| Model lengths | measure_length1≥1px，length2≥0；Sigma限制仍检查；NumMeasures整数≥各形状最低(line2/circle3/rectangle8) | 模块主动拒绝不足数量，不依赖HALCON自动升到最小值；measure_distance本版不设置，避免与num_measures优先级冲突 |
| Model.MinSupportScore | (0,1]，只为used measure regions比例，不是置信/误差 | Profile冻结，不能采手册0.7/0.8/0.9为客户默认 |
| Model.DistanceThresholdPx | 有限≥0，RANSAC `distance_threshold`，pixel | 必填，不能隐含采用手册3.5；实例外搜索 `instances_outside_measure_regions=false` 固定 |
| MaxInstances、MaxRansacIterations | 正整数且受Budget.MaxCandidates/元素上限约束；RandomSeed非零 | 原生rand_seed=0按当前时间随机，本版拒绝；显式MaxIterations不使用-1无限路线 |
| Fit.MaxPoints | -1全点，或正数≥line2/circle3；稀疏采样只有批准Profile明示且保采样ID/分布 | 主路线-1；MaxPoints超原点数可容忍但实际数回显；ClippingEndPoints≥0且至少剩2/3点 |
| Fit.Iterations、ClippingFactor | iterations≥1有限整数；factor有限>0；圆geometric类算子忽略Iterations，不能借此宣称迭代可中断 | 不同方法生效/不生效字段写入Profile；受native排空规则约束 |
| Circle.MaxClosureDistanceMm、MinArcCoverageRad | closure≥0；coverage∈(0,2π]；不让closure距离把真实gap无证据闭成full circle | Profile显式，声明full-circle时检查周向支持；不以点数代替弧覆盖 |
| ProfileStations、ProfileDirection、MaxProfileHalfLengthMm | stations有限、同框架且不重复；direction非零；half length>0，必须有限 | ProfileWidth专用，其它Method为空/null |
| Budget | 元素/MaxPairChecks/候选/输出样本/字节/并发均正整数；所有加乘checked；execution/drain timeout有限>0 | Consumer Profile必填，不填虚构1M点/512MB/30s默认；MaxParallelism同时约束输入、native上下文、缓存建立 |

本版未开放 PixelDiagnostic→物理变换“默认scale=1”。非Byte图像、超域 sigma、invalid interpolation、缺Profile的处理是前置Unsupported/InvalidRequest，不自动降位深/改参数。变更ROI/标定/方法/采样/参数形成新RequestRevision和闭包；CalibratedPhysical Scope不自动读取建议。PixelDiagnostic只允许显式pixel Identity/Affine2，且只支持D2 pure点/线/段/角/PrimitiveSize/Area/AreaMoments及ImageEdgePair2；所有量值/Witness用Pixel/Pixel2/Rad/Ratio，Numeric.LengthUnit=Pixel，不读取物理Support门、不生成带Mm字段的Coverage/Volume证据。其它方法包括ImagePrimitive2和拟合均Unsupported，不能混合mm/pixel operands。

### 13.2 ROI、粗精与参数建议

reader消费IM-024已提交且不可变ROI引用，转换成SearchRectangle/RegionRuns/闭合Contour/明确裁切mesh。ROI编辑、布尔、Undo/Redo和公共ROI句柄由该Owner管理；metrology只检查用于本方法的合法域，不自行改变ROI。`measure_pos/measure_pairs`忽略Image.domain：必须逐扫描矩形检查valid pixels/mask（包括插值margin）全部有效；缺口拒绝该scan，不只reduce_domain然后继续。图像数据租约先取得，临时measure/model后创建；close_measure/clear_metrology_model后再归还输入。

粗路线只在原图ROI内得到候选位置/初值，缓存键绑定source/frame/ROI/mapping/Profile/backend完整hash。最终量测回到原分辨率输入与原有效mask，扩边只取请求已许可搜索边界；不能用显示LOD/压缩拼图求尺寸。Physical circle/rectangle必须将实际边点映射物理坐标后再拟合，不能在像素空间结果上缩放radius；CameraParams/plane_pose的HALCON metric结果也要核原单位及到mm转换，不能由“metric”字样猜单位。

本版ImagePrimitive2不设置camera_params/plane_pose，native模型结果固定为pixel；物理转换统一走coordinate port。参数映射逐项为NumMeasures→num_measures、MaxInstances→num_instances、MinSupportScore→min_score、DistanceThresholdPx→distance_threshold、MaxRansacIterations→max_num_iterations、RandomSeed→rand_seed；Edge sigma/threshold/transition/interpolation与Model lengths全部显式设置，measure_select='all'、instances_outside_measure_regions='false'。apply前先get_metrology_object_measures取得实际scan矩形，核SearchRoi∩Image.ValidPixels含插值margin的完整支撑；不通过时不apply，不用拟合后score掩盖扫描越界。

apply后按单instance调用get_metrology_object_result的used_edges=row/column/amplitude取得真实对应边（row/column/amplitude数量一致），get_metrology_object_measures仅保所有原scan/边诊断，不将它们冒认为该instance已使用的点。实际边按初始line的沿轴顺序、circle的绕心角序、rectangle的边编号及沿边顺序构造XLD，再映射全部边并物理重拟合；rectangle四边顺序按初值局部基循环，每边至少一个非角点、共至少8点，物理残差/支持不足拒绝。实例归属不明或同一点无法分配边到Numeric tolerance为AmbiguousCandidate，不能按最接近期望尺寸选择。line物理方向以映射的初值start→end为锚；圆/矩形最终支撑门用物理点，不用pixel min_score替代。

参数建议采用§13.3的有限Replay比较Core与§13.4的可选PE Provider。真实Replay量测仍逐项调用§11.3同一服务，Provider只消费已完成、已释放且精确绑定的比较证据，不在用户点击建议时重开native搜索。候选限sigma/threshold及原Model的measure长度，不改变方法、工艺公差、数值门、支持门、坐标、ROI或随机seed；长度候选只用于无UI完整Profile比较，当前工作台五字段Schema只能采用sigma/threshold建议。目标门缺失只比较/Abstained；采用只改草稿，新Profile仍由原Owner明确发布和验收，线上不学习或降阈值。

### 13.3 有限Replay参数推荐合同与确定步骤（R1，目标）

R1属于IM-036已规划参数推荐，使用既有Contracts/Core及同一个HostTests，不另建优化器模块。新值位于Asun.Metrology.Contracts，纯计算与canonical位于Asun.Metrology.Core。只对ImageEdgePair2、ImagePrimitive2的本版已支持line/circle/rectangle开放；同一plan固定一个Method、一个Shape（适用时）、Scope.Engineering、Selector.Unique、同一个QuantityName/Unit。点距、连续场、工艺公差、Numeric、Support、拟合拒识门及模型选择不从数据自动放宽。图像源仅原Byte全分辨率；模型/fit本版Unsupported分支保持。

```csharp
public sealed record ReplayParameterCandidate(string Id, AssetRef ProfileRef,
    MethodProfile Profile, decimal SigmaPx, decimal Threshold);
public sealed record ReplayChallenge(string Id, MetrologyRequest Template,
    AssetRef ReferenceEvidence, bool ExpectedMeasurable, double? ExpectedValue);
public sealed record ReplayRecommendationGates(AssetRef Authority,
    double MaximumAbsoluteError, int MaximumFalseAccepts,
    int MaximumFalseRejects, TimeSpan? MaximumP99,
    long? MaximumPeakResidentBytes);
public sealed record ReplayRecommendationPlan(string Version, AssetRef Applicability,
    QuantityName Quantity, Unit Unit,
    ImmutableArray<ReplayParameterCandidate> Candidates,
    ImmutableArray<ReplayChallenge> Challenges, int WarmupRuns,
    int MeasurementRuns, int MinimumCompleteSamples,
    int MaximumTrials, long MaximumResidentBytes,
    ReplayRecommendationGates? Gates);
public sealed record ReplayTrial(string CandidateId, string ChallengeId,
    bool Warmup, int RunIndex, MetrologyRequest Request,
    MetrologyResult? Result, bool ResourcesReleased,
    TimeSpan? EndToEnd, long? PeakManagedBytes, long? PeakNativeBytes,
    MetrologyError? Error);
public enum ReplayRecommendationState { Recommended, ComparisonOnly, Abstained }
public sealed record ReplayCandidateComparison(string CandidateId,
    int Issued, int Complete, int Censored, int FalseAccepts, int FalseRejects,
    double? MaximumAbsoluteError, TimeSpan? P50, TimeSpan? P95, TimeSpan? P99,
    long? PeakResidentBytes, bool Eligible, string ReasonKey);
public sealed record ReplayRecommendationComparison(
    ReplayRecommendationState State, string PlanSha256, string TrialsSha256,
    ImmutableArray<ReplayCandidateComparison> Comparisons,
    ImmutableArray<string> RankedCandidateIds,
    ImmutableArray<MetrologyError> Errors);
// Asun.Metrology.Core
public static class ReplayRecommendations {
    public static ReplayRecommendationComparison Compare(
        ReplayRecommendationPlan plan, ImmutableArray<ReplayTrial> trials);
}
public static class ReplayRecommendationCanonical {
    public static string HashPlan(ReplayRecommendationPlan plan);
    public static string HashTrials(ImmutableArray<ReplayTrial> trials);
    public static string HashComparison(ReplayRecommendationComparison comparison);
}
```

Version固定metrology-replay-recommendation/1；candidate/challenge ID非空NFC、ordinal唯一，数组非default且非空；WarmupRuns≥0，MeasurementRuns≥1，MinimumCompleteSamples在[1,Challenges.Length×MeasurementRuns]。MaximumTrials/MaximumResidentBytes显式正数，checked总行数=Candidates.Length×Challenges.Length×(WarmupRuns+MeasurementRuns)≤MaximumTrials；每个plan先有界计数/字符串/源配置/结果载荷，超限不得展开笛卡尔积。比较Core不持图像buffer、租约、native或Store；预算含plan、完整trials/result与报告的同时保留，不能仅计结果数量。规范序列长度分别P/T/O，保守托管准入账固定5P+4T+4O+256×(candidate数+challenge数+trial数)+8192，每数组另64元数据，checked；编码先有界计长，O用全部候选/错误上界预留，拒绝后不分配大输出。此为本切片受控载荷账，不声称整个CLR堆/RSS硬上限；实际峰值另测。

候选ProfileRef.Sha256=HashProfile(Profile)，其Definition/Budget过原Validator；每challenge.Template结构合法、原Operands/Coordinates精确冻结。所有候选相对于第一个Profile只能改变Edge.SigmaPx/Threshold以及ImagePrimitive2的Model.MeasureLength1Px/MeasureLength2Px；其余字段（含Fit/Support/seed、预算、MinSupportScore、DistanceThreshold）逐值相等。EdgePair长度来自原Rectangles，不能为推荐修改ROI矩形；所有challenge的原搜索支撑逐项满足§13.1–2。SigmaPx/Threshold十进制意图以精确有理最近偶数舍入得到有限binary64，与Profile字段bits相等；同时验证十进制域和输出域，不clamp。零参数/退化/无适用回执/unknown数据不能被枚举绕过。Applicability与ReferenceEvidence均由Host的样本/计量用途Owner冻结；只是精确资产引用，不自授物理资格。

**实际试验生成链（Workbench工程准备Host和独立BatchReplayHost各自执行）**：

1. 根在任何reader/backend/factory前保存plan、原样本/期望来源和全部上限；建立本Host独有reader，把每个candidate的精确ProfileRef注册到原ReadProfileAsync映射。模板只保原输入/坐标/定义用途，不能由最后一次UI草稿补值。
2. 按candidate原数组→challenge原数组→先Warmup再Measurement→RunIndex从0升序逐行。构造新request只替换Key、MethodProfile、Definition及Budget，后三项逐值等候选Profile；原输入/坐标/Scope保持。Key.OperationId为本Host试验唯一Guid，RequestRevision=1+该行全局序号，uint加法checked。两个Host不共用该Guid/engine。样本间ROI可不同，但不改变候选的算法/支撑门。
3. 逐行先登记原MeasureAsync Task/key/预算再调用一次，所有native与reader开销沿M2/M3。EndToEnd从本行接纳前单调测点到结果及本行资源确认释放，包含读图、坐标、建模、结果复制和归还；时钟/实际包/环境绑定由Host原证据保存。ResultFingerprint、Evidence.Request/Profile/Sources/版本逐项核对原值与HashRequest/HashResult，不凭返回Valid就记录为正确。
4. Measure返回后查GetOperation同key；唯一已释放终态才ResourcesReleased=true。超时/取消/DrainUnknown/ReleaseUnknown保原Task/key，不开始下一行或另建engine绕账；记录删失行与真实原因，剩余未派发行以Result=null/Released=false/Error=既有Cancelled或TimedOut明确登记。实验表每个计划行恰一次，包括未执行/失败分母，无部分表推荐。
5. 性能预热行不进稳态分位，仍核其正确性/资源，失败不能隐藏。每测量行可读有效或明确拒识终态均进入Complete时间分母，失败/取消/超时不从Issued删掉；接纳前拒绝无端到端样本。PeakManaged/Native只来自真实本次测量Owner，未知=null，实际无native路线才可0；预算/预约/工作集差不能冒精确native峰值。冷启动另用WarmupRuns=0的新plan/engine，不混到稳态行。
6. 完整冻结trials后Compare；Host保存返回值及plan/trials/实际运行包闭包（若要求持久证据，沿原Store Owner，并非本Core写IO）。建议表与生产事实分开。关闭仍§16.3原Task/单飞清理，任一unknown不报告试验完成。

Compare为有限同步total值计算：null/default/非法结构/identity/hash/版本/预算返回Abstained、空排名与既有具名错误，不调用port，不抛业务异常（OOM/进程终止除外）。trials必须恰完整计划键集合，顺序上述固定，不重复/遗漏；Request.Key唯一，Profile及其它字段符合第2步。ResourcesReleased=false不得携可采用的Measured事实，结果若留仅作诊断。比较定义：

- 正确量测：Measured/Valid、唯一candidate、完整Support、具名Quantity恰一个/单位相等且有限。ExpectedMeasurable=true时须ExpectedValue有限；false时为null，量测有效即FalseAccept。门存在时绝对误差>MaximumAbsoluteError也记FalseAccept且不得Eligible。此误接受仅是量测挑战集判据，不是工艺PASS/NG；公差/放行仍宿主Owner。
- ExpectedMeasurable=true而无正确量记FalseReject；缺量/多解/Incomplete/单位错不能给0误差。ExpectedMeasurable=false只允许有支撑解释的Unevaluated或Unqualified/Indeterminate以及InsufficientSupport/AmbiguousCandidate/Unqualified原原因作合法拒识；后台故障/资源超限/版本错/输入坏/用户取消并非成功拒识，独立Errors保存，该候选不Eligible。若无Gates，只列已有量的误差和拒识，不判“误差达标”。
- 每候选Issued=challenge数×MeasurementRuns；Censored定义为未派发/接纳前拒绝/无实际接纳到释放完整时段的测量行，包含资源未知；Complete+Censored=Issued。EndToEnd≥0，按§16.1 nearest-rank ceil(p×n)得P50/P95/P99；完整释放且有接纳/耗时的行才Complete。PeakResident为各完整行checked(PeakManaged+PeakNative)的保守峰值和，再取最大值，任一缺测即null；分量峰值即使不同时出现也相加以保守限额，不声称该和是同一时刻实测驻留。以上全行峰值和预热正确性共同用于准入。
- Gates.Authority明确，误差有限≥0、FA/FR最大数≥0，P99若给出>0、resident若给出>0。不提供Gates为ComparisonOnly/无排名；阈值不由ExecutionBudget推断。推荐还要求至少一项可量与一项明确拒识挑战、各候选完整计划/无执行错误/无删失、Complete≥最低样本且所有门通过；若性能/资源未给门，仅不评价对应资格，排名中同缺字段按candidate原数组顺序打破平局，不声称速度/内存更优。
- Eligible候选的固定字典序为FalseAccepts、FalseRejects、MaximumAbsoluteError、P99（只有全部Eligible都有实测值才比较）、PeakResident（同条件）、candidate原序。RankedCandidateIds列全部Eligible，无截断。无Eligible=Abstained；有Eligible=Recommended，含义是该冻结实验域的参数候选，不是生产批准。完全同值的基线候选允许比较但PE不输出空Edits。

编码只用于新R1域，不改§15/19已接收字节。HashPlan/Trials/Comparison分别用Asun.Metrology.ReplayPlan/1、ReplayTrials/1、ReplayComparison/1，按本节record声明序和§15原语；内嵌request/result/profile也逐声明字段序（trial.Result包括原ResultFingerprint，不生成第二数学事实），可空按tag，原数组序保持。decimal固定为符号byte+scale byte+96bit无符号系数三UInt32LE：从decimal.GetBits取得原系数/scale，末尾十进制0逐除并减scale，零固定正号/scale0/系数0；不用Culture/G29字符串或binary64替代原decimal。时间/峰值是试验证据字段，纳此新域hash；比较可复现的是同一冻结表的排序，不承诺不同实验的时延bits一致。Hash入口非法抛ArgumentException；Compare先total校验并捕获业务格式错误。

### 13.4 PE推荐Provider、双消费者与反例（R2，目标）

可选桥唯一落点src/Asun.Metrology.Adapters/Asun.Metrology.Adapters.csproj，namespace Asun.Metrology.Adapters，net10.0；仅依赖本模块Contracts/Core与IM-062 Asun.Modules.ParameterEditor.Core公开程序集。它不反向进入Core/Runtime，不引用Halcon/工作台/WPF/产品Shell，发布独立可选DLL。消费者一为IM-065工程参数工具，二为独立BatchReplayHost的无UI PE会话；后者也可直接消费R1完整Profile排名，不强制加载PE。测试仍tests/Asun.Metrology.HostTests/的ReplayRecommendation分组，BCL Exe命令沿§16.1。本节是规格修订，不授写工程或改变已接收Core范围。

```csharp
// PE = Asun.Modules.ParameterEditor
public sealed record ReplayProviderOptions(int MaximumOperationRecords,
    long MaximumResidentBytes, TimeSpan DisposeObservationLimit);
public sealed record ReplayProviderSnapshot(bool Closing, bool Closed,
    ImmutableArray<PE.OperationId> Pending, int RetainedOperations,
    ImmutableArray<MetrologyError> Errors);
public sealed class ReplayParameterRecommendationProvider :
    PE.IParameterRecommendationProvider, IAsyncDisposable {
    public ReplayParameterRecommendationProvider(
        ReplayRecommendationPlan plan, ImmutableArray<ReplayTrial> trials,
        PE.ParameterSchema schema, PE.ParameterSnapshot baseline,
        PE.ContentRef provider, ReplayProviderOptions options, TimeProvider time);
    public ValueTask<PE.RecommendationResult> RecommendAsync(
        PE.RecommendationRequest request, PE.ParameterSchema schema,
        PE.ParameterSnapshot snapshot, PE.OperationContext context,
        IProgress<PE.OperationProgress> progress, CancellationToken cancellationToken);
    public ValueTask<PE.AdapterDrainReceipt> DrainAsync(
        PE.OperationId operationId, CancellationToken cancellationToken);
    public ReplayProviderSnapshot GetSnapshot();
    public ValueTask DisposeAsync();
}
```

constructor仅冻结/校验有界plan/trials/schema/baseline/options/provider，零IO/native、无隐藏线程；无效抛ArgumentException，不拥有借用service或图像。Options均显式正数/期限≤24h；完整输入复制/规范编码/R1报告/PE响应及原操作墓碑共同计MaximumResidentBytes，原R1准入账加IM-062实际TLV载荷（schema/snapshot每4份、response上界4份、每操作256+原request/context载荷、每数组64），先有界计长后复制。record满拒新ID，不逐出旧ID。构造成本也受显式预算预检，TimeProvider/progress不从UI Dispatcher读取。provider.Id固定metrology.replay-parameters、Version=1，Sha256来自实际桥包发布Owner，不伪造二进制hash。

只接IM-065 mwb.image-edge-pair.parameters Schema Version2/pe-v2-tlv1：五字段精确为sigma_px Decimal/Pixel、threshold Decimal/None、transition/interpolation/selector Enum/None，定义/约束/身份及baseline完整hash核IM-062 ParameterCanonical，profile/单位/原意图按工作台A.10.2已接收来源。selector必须Unique；所有候选只能改前两字段，其余Edge/Rectangles、原定义和支持相等；含Model长度候选、本版不支持Schema、极端原double不能表示decimal、Selector.All均拒Unsupported，不裁去候选制造完整推荐。原baseline Sigma/Threshold按相同精确最近偶数规则与第一个候选Profile的binary64相等；草稿其它字段与原Template逐值一致。生成PE Edits直接保candidate原decimal，先对冻结baseline做Atomic完整校验；不从量测double二次舍入参数。

每次request.Profile准确映射为ContentRef(Applicability.Id,Applicability.Revision的Invariant十进制,Applicability.Sha256)；Evidence恰plan与trials两键，ContentRef Id分别metrology.replay-plan/metrology.replay-trials、Version1、Sha256分别HashPlan/HashTrials，原source/ROI/Profile/期望refs已在这两个完整内容闭包内。缺失/额外/异hash拒绝，不读latest。schema/snapshot、generation与context.Session/Operation/SnapshotSha256/RequestSha256须匹配IM-062原规范请求；不是把context hash当自报可信，重核原pe-recommendation-v2请求。实际执行期限取request.Timeout、context.EffectiveDeadlineUtc和Options观察上限最早，TimeProvider单调转换一次，后续观察不延长。临界取消保原Task。

Recommend先登记原OperationId/冻结payload/完整响应预留，最多1 active，不排队。相同ID相同原请求/前像观察原Task与原值，不再次Compare；异载荷IdentityConflict，活动槽/记录/字节满BudgetExceeded，非法绑定抛MetrologyPortException，由PE依其AdapterFault/Failed通路保原错误。锁外运行R1；progress最多起止两项，不await客户端回调；同步IProgress.Report异常保诊断、停止该progress，不让它篡改排名。回调若未退真实Task未完成，资源/Closed不提前成立。

Recommended→按排名生成最多request.MaximumCandidates个**非空**ParameterSuggestion；每个Id保原candidate.Id，Edits按sigma_px/threshold ordinal排序且仅实际差异Set，ReasonResourceKey=metrology.recommendation.candidate，Confidence=null。基线无差异项不构成PE suggestion，后继Eligible仍可列；截取只发生在声明的PE MaximumCandidates投影，完整R1报告仍保全部，不能据投影改变实验分母。无差异候选/无Eligible/无Gates分别Abstained+空Candidates，reason为metrology.recommendation.unchanged/abstained/comparisonOnly。结果字段原OperationId/RequestSha256/SnapshotSha256/Profile/Provider保持；每项Evidence=ContentRef(metrology.replay-comparison,1,HashComparison)，为计算内容引用，未持久化不能显示“已保存”。全部原因资源键交宿主zh-CN/zh-TW/en-US投影；候选不是confidence/生产决定。

Drain只观察同原Task，token仅停止等待；ExecutionStopped=true且ResourcesReleased=true必须原计算/回调/临时复制已退出，不凭无native先给ACK。unknown ID返回两个false及PE-2006 EditorError（MessageResourceKey=pe.error.PE-2006、RecoveryResourceKey按PE原表query，DiagnosticRef=null）；取消/到期的真实执行结果不采用，待退出后原PE会话终态按其StopReason，不另造Cancelled成功候选。GetSnapshot保原ID/错误有界值。Dispose先Closing拒新操作、取消自有执行并在Options有限期限等原Task退出；未知抛MetrologyPortException(DrainUnknown)、保对象/原Task，Dispose按原§16.3单飞由根保留原Task；后续仅GetSnapshot/Drain观察，不重发在途析构。真实Closed须Pending.Empty，无回调/临时借用；墓碑与不可变比较值随宿主归还实例，借用的PE session由宿主关闭，不由provider处置。

两个无UI Host配方均在§16.3根下：各自准备/冻结独立plan+trials→创建Provider→调用new PE.ParameterEditorFactory().Create(schema,baseline,options,access,time,preview:null,recommendation:provider,apply:null)，核PeResult.Succeeded/Value非null/Errors.Empty得到本Host PE session→RecommendAsync/GetOperation→先原PE GetOperation.Phase=ResourcesReleased/Outcome=Completed，确认非HistoryOnly及当前授权→显式AcceptSuggestion原ID→原工作台Full/Patch/新Profile链（Batch只保存工程草稿，不调用Apply Port）→PE Drain/Close真实ACK→Provider Dispose/GetSnapshot.Closed→各自计量服务/reader/backend按原依赖关闭。Schema/plan刷新建新实例，旧Pending继续原根。无图像真实运行时只用注入终态的合成表验证排序/协议，严禁写为HALCON推荐效果。

R1/R2必须断言：两候选两challenge的完整2×2表（无预热、每项1次），可量期望10mm及明确拒识；c0正确量10.25mm且对拒识样本Measured，c1为10mm/明确InsufficientSupport；软件测试Gates误差0.1mm、FA/FR均0且其它门null时仅c1 Eligible，c0拒。这些值仅解析fixture，不是客户门。交换trials、遗漏失败行、伪Released、result/request/profile改hash、单位错、mask不完整、seed改变均拒；全部无门ComparisonOnly且Provider Abstained；所有候选失败/删失/无变化Abstained；相同表/版本重复hash排序一致。两个PE session不同OperationId/草稿，A迟到/编辑或撤权不得影响B，建议只变原草稿且0 Apply/Store/设备动作。清理/回调迟到/Dispose同步抛错沿原根单飞；测试时记录实际待执行分母与非零退出，不用synthetic表宣称native运行或算法精度通过。

## 14. 生命周期、并发、未知结果与资源恢复（M2/M3/M4）

同 Key + 同 canonical request hash 的重复调用返回首次同一操作/结果；同Key改payload为IdentityConflict。新尝试用新RequestRevision或新OperationId，不覆盖旧结果。Runtime实例内操作状态只由单一锁/CAS写，序号按已提交转移递增；两engine完全隔离。完成记录按RuntimePolicy有界且不逐出；本版不提供跨重启持久OperationStore，宿主负责保存closed results及未决key。重启后新engine对旧key按§11.3返回未找到的Rejected/InvalidRequest；宿主依据保存的未决清单显示“状态未知”，不是模块新造Unknown枚举，也不能宣称已执行/已释放或自动重跑。

| 情形 | 必须执行的转移与可见结果 | Owner/恢复 |
|---|---|---|
| 正常 | Accepted→Validating→Queued?→Running→Completing→Draining→Drained→ResourcesReleased→Completed | Completed可携Measured/Partial/Unevaluated等计算事实，不带质量PASS；未接纳请求为Rejected，无资源阶段 |
| 校验失败 | 结构校验在接纳前抛MetrologyPortException，零资源；接纳后Profile校验为Accepted→Validating→Rejected | 有已取得租约的payload失败走Draining/release再Completed或Failed；拒绝后无伪Drained，既有操作不被覆盖 |
| 读输入断连/哈希改变 | Running或校验读阶段→Draining→Drained→ResourcesReleased→Failed，InputUnavailable/InputHashMismatch | reader不自动重连换版本；宿主修复原来源或新revision；已有输入若完整冻结不因设备现已离线改量值 |
| 取消/请求deadline | CancelRequested→Cancelling→Draining；停止排队/下一块，撤销结果发布权 | native调用不可保证抢占；等待实际退出，结果不得迟到转成功；计算块之间检查token和budget |
| 排空deadline到且仍在运行 | Draining→DrainUnknown，等待者无量值返回Error DrainUnknown；snapshot仍保PendingOutcome | runtime隔离原上下文并继续拥有租约；RequestCancel幂等；查询同key；不再分配给新请求，不clear仍工作handle |
| 后续确认退出 | DrainUnknown→Drained→ResourcesReleased→Cancelled/TimedOut/Failed | 旧成功计算只诊断；不重获发布权、不第二次发终态；延迟资源释放事实仍属原key |
| 释放抛错/无法确认 | Drained→ReleaseUnknown；无ResourcesReleased/执行终态 | native工作已退但释放权威未闭合；保留对象/租约账本，显式查询恢复；不将“Dispose已调用”当释放成功 |
| 关闭 | 先停止接纳新请求、逐key RequestCancel；CloseAsync只等待给定时间 | 全部ResourcesReleased后Closed=true；否则Closed=false+Pending快照；caller取消wait只结束等待，不撤销cleanup |
| 迟到/回调异常/慢观察者 | 校验key/revision和每操作序号；错误订阅不能改量值或状态 | 回调在锁外、有界通知队列；可合并Progress但不丢状态/终态，完整状态从GetOperation查询；抛错只记诊断 |

服务 MeasureAsync token取消不直接用TaskCancelledException省略资源结果。Start同步创建可监管的execution并登记身份，只进行有界托管初始化；返回execution以前不启动native/异步工作。Start若抛错须证明零工作、零私有资源，禁止“已启动但丢失handle”的实现。GetResultAsync完成或抛错只是计算等待完成；Runtime还必须取得同key GetReceipt().Phase=Exited，并调用ReleaseAsync得到Released，再逆序归还source leases。BackendReceipt.Exited由该backend的资源Owner在全部native/内部回调/worker退出后生成，Task.IsCompleted本身不是回执。早返回而receipt仍Running/ExitUnknown为端口违规BackendFailure，保留execution/输入并走DrainUnknown；收到旧key或未知回执同样隔离。backend不能自发模块终态/ResourcesReleased，不能dispose借来的source leases或coordinates；GeometryBackend也按相同receipt路径确认托管工作退出。

reader/profile/coordinate的异步调用也登记为本操作的在途工作：返回ValueTask以前不能隐藏失去监管的worker，任务完成/抛错的端口合同要求所有私有I/O与cleanup已结束；未返回的Acquire仍由reader拥有候选资源，runtime不能把它忘掉。取消后延迟返回lease须归入原key再dispose/核回执；尚有任何获取/映射任务未完成时为DrainUnknown，不能先给ResourcesReleased。端口若无法满足该返回合同，只阻断该端口adapter；不能用取消Token替代退出事实。

ReleaseAsync对同execution幂等，不启动计算；重复调用查询/继续已登记的清理，只在确实释放全部私有资源后回Released。抛错、迟到、未知回执保留ReleaseUnknown；Runtime在同key监管循环中继续GetReceipt/有界等待ReleaseAsync，不创建新execution。每个lease.DisposeAsync同样幂等，ReleaseReceipt=Released才确认归还；异常后Held/ReleaseUnknown保留并查询原lease，不能先置“已释放”。这些回执是端口Owner的必需合同，实现测试用闩锁证明退出/释放时机；第三方后端若不能提供该证据，不开放该adapter切片。GetOperation返回实时快照，监控在等待者返回后继续；不让宿主靠再调用MeasureAsync触发cleanup。

同key重复等待者不重复创建计算；任一等待者token取消等价于RequestCancel该共享操作（本版明确采用全操作取消），宿主不能将它当仅取消自己的等待。首次响应保留可重放；Unknown期间重复MeasureAsync立即返回该无量值响应，资源进展由GetOperation查看，最终释放结果在snapshot更新；不会第二次发终态。ExecutionTimeout从Accepted的单调时钟起计，含队列、Profile/reader/mapping；取消/到期后DrainTimeout分别给执行退出和随后释放各一个有限等待窗，过窗返回对应Unknown，监管继续。RequestCancel不存在key/已终态返回false，未决首次与重复返回true，不改变已冻结失败原因；成功结果提交与取消通过同一锁线性化，提交之前取消胜出，已ResourcesReleased+终态后取消无效。

IAsyncDisposable.DisposeAsync用RuntimePolicy.DisposeDrainTimeout调用关闭路径：全部确认后返回；未closed时抛MetrologyCloseException，Receipt保留Pending/PendingNotifications，保留runtime quarantine账本，不进行GC终结器强制clear。重复Close/Dispose继续原关闭，不重新cancel已完成操作；关闭后Validate仍可用、GetOperation仍可查，MeasureAsync新key按§11.3抛InvalidRequest且不接纳。CloseAsync的waitCancellation只取消该等待并抛OperationCanceledException，不撤销关闭/cleanup，宿主可再次Close查询。宿主必须保持engine/清理监管引用，人工退出进程不被登记为模块已排空。应用侧急停/设备取消是其它Owner，模块仅有计算取消，不发设备命令。

观察者合同为同步短回调，不能调用UI Dispatcher同步等待、递归Measure或持有payload。Runtime锁外的单一通知worker按有界队列派发：Progress可合并；状态提交先更新snapshot，再入通知队列，队列不足时停止该订阅并诊断BudgetExceeded，不丢权威状态也不堵计算worker。抛错停止该订阅；已开始但不返回的回调不能强杀，CloseReceipt.PendingNotifications>0且Closed=false，即使Pending操作数组已空。正常Close在停止接纳通知后等待该worker退出，释放通知中的纯值；观察者不持native/lease，不能让它代持资源。宿主应在语言/页面代次切换时拒旧key投影，metrology不访问UI权限；正常资源事实只由Runtime生成，通知缺失用GetOperation恢复。

事件Sequence从1起，只由Runtime提交状态递增；backend的observer参数只接收Running进度，其key先核，sequence/time由Runtime重写。MonotonicTicks来自该进程Stopwatch.GetTimestamp、FrequencyHz为Stopwatch.Frequency；UtcTime仅诊断，不用于deadline。CompletedElements≥0且不倒退，TotalElements未知时0、已知时≥Completed；完成量不是质量通过数。订阅只在MeasureAsync该次调用登记，重复调用相同delegate不重复登记；不同observer个数也受MaximumNotificationItems约束。GetOperation始终独立于通知队列，可恢复最终状态但不伪造已经丢失的每条历史进度。

资源顺序：reader拥有源缓冲→module持租约→backend拥有复制/临时XLD/Region/measure/model/ObjectModel3D→结果仅存值和AssetRef。`distance_object_model_3d`写subject的`&distance`/`&closest_index`，必须使用请求私有副本，不能改宿主共享原模型；prepared target index只在不可变target/hash、能力和限额匹配时复用。每model只一worker；reentrant/global不表示同可变句柄可并发。释放逆序：native完成/回调退出→native temporaries clear→mapped/临时buf→源lease归还；Drained与ResourcesReleased分开。峰值计入全部复制/索引/输入租约/候选/通知队列，不能只计托管对象大小。

## 15. 单位/标定/误差、canonical与版本发布

### 15.1 坐标与证据闭包

CalibratedPhysical必须由coordinate/calibration Owner端口返回exact MappingReceipt，绑定输入frame、source unit、target unit、Calibration及ApplicabilityReceipt；reader/coordinate后端重核hash/有效域/环境，不从文件名或UI选中状态推定。Engineering允许未带物理资格的mm几何，但scope明确工程输入；PixelDiagnostic仅2D点/线/面积及图像原生诊断，3D/物理volume拒绝；不把未知pixel输出标Mm。映射的每点SampleId/序号保持，对无效mask、不在标定有效域或来源frame不匹配明确Indeterminate/Unqualified，绝不套“上次标定”。

复合配准和多FOV输入需上游已经将source/frame/夹持/epoch/映射闭合到统一target frame，metrology不拼图/消重物理事实。输入间重复观测不得重复算面积/体积；无法证明覆盖互斥返回Unsupported，交给上游Owner解决。源资产失效不改历史结果，也不从当前active自动替换在途版本；生产适用性是否仍可采纳由宿主资产/质量Owner判断。

### 15.2 误差与不确定度

每结果分别保留采样/定位、标定、坐标变换、拟合、参考基面、离散/积分、环境/设备差异的来源ref和缺项；Witnesses/Coverage/Affine/Edges直接携带必需可读证据，IntermediateEvidence仅引用宿主已经存在的外部证据，不需要后端暗中写Store。v0.2没有协方差输入/传播API，Uncertainty逐QuantityName绑定且统一为NotProvided/NotEvaluable，Standard/Expanded/coverage字段为空，不把RMS/score/分辨率或0当uncertainty。未提供不确定度信息为NotProvided；用途要求但该传播路线未开放为NotEvaluable/Unqualified；两者MissingComponents用固定键列缺项。

未来定量切片先定义measurand模型与带单位/修订的协方差接口；微分可用时按 `u²(y)=JΣJᵀ` 含相关项传播，并核PSD/维度/单位。零距离、候选切换、角度wrap、裁切volume等非光滑/强非线性不能盲用一阶RSS，需冻结分布传播/Monte Carlo方法、seed、样本数/收敛/预算与拒识；本版不猜这部分算法。NIST TN1297 §5.1/§5.2强调covariance和校正不确定度，不把系统误差与uncertainty混同。是否允许缺定量uncertainty由用途Profile决定，但本模块从不自批生产。统计Bias/Linearity/Stability/GR&R由statistics/qualification或宿主按既有Owner消费，metrology只提供原始值/validity/证据，不增统计Study库。

### 15.3 canonical与兼容

NFC在所有Hash入口都是校验前提：非NFC字符串直接抛ArgumentException，total Validate分类InvalidRequest；不先Normalize再编码，不将不同原始输入偷偷归为同一身份。已NFC字符串按原UTF-8编码；本规则同样约束§19的v0.3字段。

目标hash按各record声明字段顺序写入：Magic字符串先写UTF-8字节数(int32 little-endian)及字节；普通字符串同规则，先核NFC；可空值1 byte存在tag(0/1)，非空再写值；数组int32数量后逐元素，禁止default数组；enum为int32，int/uint/ulong/long按声明位宽little-endian，bool为0/1 byte，TimeSpan用int64 ticks，Guid用RFC4122网络字节顺序，double IEEE754 64-bit little-endian，-0为+0。Geometry case tag按§11.1声明顺序从1起，SourcePayload tag按其声明顺序从1起；record本身无名称/字段名字符串。图像写声明字段、Buffer有效RowStrideBytes×Height字节及ValidPixels；仅校验的尾余buffer不纳hash也不消费。禁止非有限；非法输入Hash入口抛ArgumentException，由total Validate在业务入口捕获/分类。数组保持声明顺序，只有合同明确排序的sample/candidate按ordinal ID排序，不排序轮廓顶点/face/扫描站破坏几何。

Magic分别为`Asun.Metrology.Request/0.2`、`Asun.Metrology.Result/0.2`、`Asun.Metrology.Method/0.2`、`Asun.Metrology.Source/0.2`。输出为SHA-256小写hex。Request全部字段含Key/Budget入hash；Profile含全部字段、不含它自己的AssetRef；Source含payload；Result含全部字段但排除ResultFingerprint自身，Evidence.Request只保存request引用不引入递归。UTC/耗时不属于这些record，不纳hash；错误保MessageKey/稳定参数，不hash本地化句子。读者核Profile/source内容hash，不信自报sha。Evidence.Request是以OperationId+revision为Id、revision为Revision、HashRequest为Sha256的计算内容身份，尚未落Store；ResultFingerprint同样只证明内容，不表示已持久提交。外部资产ref/IntermediateEvidence是宿主原子封存的已有证据，Core不写文件，宿主保存返回record并提供真实提交回执。

同输入同版本在受测Runtime环境中可复算；不承诺所有CPU/本地HALCON版本bit-identical，跨环境以方法的数值容差比较并保原hash，不能重算伪造旧内容。旧v0.1 Culture相关指纹只按原环境/原文本验证，不能用新canonical重写旧指纹。改变unit/符号/支撑/area采样定义或算法升级Method/Contract版本；改变VolumeMode/参数/随机种子绑定新Profile revision/hash和RequestRevision，不无声覆盖旧配置。旧未识别契约VersionMismatch，禁止best-effort读成成功。

发布按M1/M2/M3独立包，记录API/Contract hash、依赖、方法Profile与测试Golden；Core package无WPF/设备/数据库。升级先在两个Host用相同来源生成新attempt并对比量值/拒识/支持/资源；宿主批准后原子切换完整版本闭包。在途engine继续旧包，确认释放后关闭；回退只切新请求绑定，不删除证据/测试，不覆盖历史量值，不加载不兼容的混合Core/adapter版本。

## 16. 两种审查视角、用例反例与定向验证

第一视角按“几何/观察能否证明这个被测量”检查输入、公式与支持；第二视角按“外部Host如何在并发、取消和版本变化后仍知道结果归谁、资源是否退出”检查身份、时间线与Owner。下表是产品/已有测试的执行要求，不生成审计PASS，也不要求本轮创建测试文件。

| 场景与覆盖Method | 关键输入/动作 | 可判定断言 |
|---|---|---|
| 正常/零值：全部方法 | §12解析几何；相同源重复执行 | 核已声明量名/维度/单位、witness/support、hash；同点0合法，非法输入不能填0；Fit与Measure无工艺PASS |
| 空输入：全部 | default/empty arrays、空Region/Contour/Mesh、空model结果 | null/default格式Invalid；合法空观察Unevaluated/InsufficientSupport；零native分配或完整释放；不把area_center空0视结果 |
| 大规模/溢出 | 超MaxInputElements、stripe乘法溢出、全对全segment、target索引大量内存 | 分配前checked预算，拒绝或有界块；不静默抽样；数值溢出Failed不Infinity，索引建立计峰值 |
| 弱信号/遮挡 | 幅值略上下Threshold、亮暗反转、scan跨mask缺口、完整circle少弧 | 支撑不足不改阈值；measure忽略domain仍拒无效scan；反向扫描Transition语义可复算；不沿ROI边补边 |
| 退化/多候选 | 共线calibration、零direction、near-parallel segments、重叠profile、同分model多实例 | 不是点数≥3就合格；正确dimension和AngleMode；实例顺序任意仍stable CandidateId；歧义不得first/nearest tolerance选中 |
| 区域面积/矩 | 开XLD、自交、hole交叉、empty、affine shear、同特征值 | 自动闭合前拒绝；hole符号正确，det缩放和协方差映射一致；principal angle未辨识明确缺量 |
| 3D支持/体积 | 反法向、重复face、open mesh、cross-zero triangles、双层投影、远基面 | signed height反号；closed mesh不合格不补洞；cross-plane先裁片；HALCON绝对值不伪 signed integral；远面数值不稳定拒绝/选相同定义的邻近基准 |
| 参数/坐标变更 | ROI/标定/尺度/采样/Profile改变，非等距pixel圆 | 新key修订；旧attempt只历史投影；实测点先映射再circle拟合，不按半径倍数；像素中心/corner映射Golden |
| M0验证器反例 | invalid endpoints/null fingerprint、huge point、singular tolerance、Culture zh/en | 记录旧异常/浮点非有限行为，不能把原IsValid的返回假定为total；M1目标Validate不抛业务异常，hash跨语言一致 |
| 并发/重复 | 2engine、同key重复/改payload、两个请求同target模型 | 只一次计算且首次响应重放；冲突明确；subject私有副本；不同来源/hash/实例无串扰 |
| 取消/超时/迟到 | 校验、队列、native、归约、结果阶段取消；native晚返回 | 先撤发布权，只有实际退出才Drained；同key查询/释放；结果不能回写新revision；无终态后Progress |
| 断连/输入改变 | reader访问错hash或来源中途失效 | 保原请求身份，明确失败/资格缺失；不自动重连换最新源；所有已取租约可回收 |
| 关闭/未知 | native不返回、Dispose抛错、caller取消close等待、重复cancel/close | CloseReceipt.Pending准确；DrainUnknown禁止clear/input dispose；ReleaseUnknown不发ResourcesReleased；最终唯一终态；恢复按同key |
| 版本/第二消费者 | 同一样本在工作台适配Host与BatchReplay；新旧Profile/包并行回退 | 不依赖工作台内部，contract mismatch拒绝；旧结果保原版本；两Host数值/支持一致，各自资源和订阅隔离 |

M1单测只用解析样例、契约和pure host；M2 fault backend用可控进入/退出门、回调/Dispose故障，不拿模拟native结果作HALCON精度证据。M3/M4实际26.05执行Golden/Replay包括good/bad/boundary/弱信号/遮挡/未知域，记录算子/Profile/hash/资源；不能用synthetic alone宣称真实计量能力。所有输出读者以完整release事件与snapshot核资源状态；无证据不将格子标通过。

补充解析样例绑定（都是合成定义断言，不是客户参数）：

| 用例ID / Method | 明确输入与预期 |
|---|---|
| FitLine2:axis | open点(0,0),(1,0),(2,0)，Support跨度门≤2；Line2方向+X，RMS/max=0；两个同点为InsufficientSupport |
| FitCircle2:arc | open点(1,0),(0,1),(-1,0)，覆盖门≤π；中心(0,0)、radius1、Arc2.Start=0/Sweep=π；闭合声明不能补不存在的另一半圆 |
| FitPlane3:orientation | 三点(0,0,2),(1,0,2),(0,1,2)，anchor+Z；Plane3 normal+Z、RMS/max=0；anchor+X近垂直应Indeterminate |
| FitSphere3:units | ±X/±Y/±Z六个单位点，半径门[0.5,2]mm、经度覆盖门≤3π/2、纬度跨度门≤π；Sphere3 radius1mm而非0.001mm；所有点Z=0不能通过可辨识门 |
| FitCylinder3:axis | z=-1/+1各4点(x,y)=(±1,0),(0,±1)，anchor+Z，轴向门≤2、周向门≤3π/2、radius门[0.5,2]mm；radius1、extent[-1,1]、axis origin(0,0,0)；单一z环不能通过轴向门 |
| AffineCalibration2:independent | fit源(0,0),(1,0),(0,1)，target(10,20),(12,20),(10,23)；独立check(1,1)→(12,23)。rank门1e-12/cond上限5/hull最小0.1mm²/check数1/check误差1e-8mm仅harness值；系数[2,0,0,3,10,20]、rank3、残差0；check改为(12,24)应拒绝 |
| AreaMoments:square | 连续[-1,1]×[-1,1]方形：Area4、Center(0,0)、MomentXX=MomentYY=1/3、XY=0、两variance=1/3，PrincipalAngle缺失并说明等特征值；不能把angle填0 |
| SurfaceDistance:witness | subject(0.25,0.25,2)，Reference三角(0,0,0),(1,0,0),(0,1,0)朝+Z；Distance2、witness(0.25,0.25,0)，反朝向Oriented为-2、Unsigned仍2 |
| DatumVolume:crossing | footprint[0,1]²、完整单层surface h=x-0.5，按零线裁片：positive=negative=0.125mm³；net=0、absolute=0.25，正负mode各0.125，全部保两部VolumeEvidence；不把net0称无材料 |
| ImageEdgePair2:mask | Byte0/255平直跃迁对，Sigma0.4/Threshold10、half lengths3/1、bilinear及固定扫描ROI为harness；实际运行以端点witness复算width，不事先假造subpixel数值；将scan内一pixel移出valid mask时该scan必须Unevaluated，不能返回width0 |

球覆盖中的极点（水平径向模≤Numeric.LengthTolerance）只贡献纬度，不凭atan2(0,0)贡献经度；至少两个可定义经度样本，角跨度仍按最大空档法检查。二维矩形物理重拟合的四边/8点门与native3266拒绝按§13.2执行。几何断言用相应Numeric tolerance比较，不能把浮点近零要求bit-exact；source/algorithm/seed/profile hash相同的同环境重复另核canonical指纹。

### 16.1 可执行 BenchmarkProfile 与最小Host

BenchmarkProfile冻结：Name/Revision/hash；Method/Contract/backend/build/runtime/CPU/OS；source/ROI/coord/Profile hash；Dimension/DataKind/点或face数/图像尺寸/bit depth/有效覆盖/候选数；冷/热、预热数/样本数/最低有效数、并发、queue深度；ExecutionBudget全部上限；时延/内存/拒识门及其批准来源（允许目标为空）。资源上限为可执行输入限制，不是假定客户设备值。

M0同步计函数进入到返回，无native；M1/M2计Accepted→ResourcesReleased，另计Validate/Reader/Mapping/模型创建/edge/fit/归约/evidence/Draining/release；M3/M4计所有native索引/缓冲/lease/GPU（该路线无GPU时明确0且标N/A）。使用同进程单调时钟，nearest-rank和失败/删失统计沿DEV-GOV-010 §3.1；完整排空的失败样本也参加端到端分位统计，其类别另列，DrainUnknown/ReleaseUnknown删失另列、不能删掉判通过。目标缺失结果NotEvaluated；改变样本/输入域/Backend/Profile才需重测影响范围，不重复无变化的全仓/分辨率矩阵。

资源账本分“确定分配量”“native保守上界”“实测进程峰值”，禁止将process delta或句柄数冒认为exact native bytes。M1/M2按每数组/缓冲checked长度及操作/通知上限做前置限额，计leased缓冲的完整有效区；MaxPairChecks覆盖最远点/拓扑/投影相交候选对，超限拒绝。M3/M4的每Method原生分配保守包络须在目标adapter实现前用固定26.05 build、输入规模/索引/复制/实例数及同样本峰值证据绑定；当前正文未取得该包络，不声称MaxNativeBytes已经可强制兑现。缺包络的native分支为ResourceLimited/NotEvaluated并阻断该adapter准入，不能尝试分配后把OOM当预算管理；该明确规格门不阻断pure Core或M2 fault backend。 §20.1区分配置Empty的Runtime能力Unsupported与直接Start/已配置shape不覆盖的BudgetExceeded；本轮只冻结显式Options/测点/禁止分配语义，没有取得原生包络。

最小Host无Shell/数据库/设备SDK/WPF/AsunImage；M3实际Host显式注入HalconBackend和相同reader/coordinate ports，按批准依赖部署，不检查许可证。调用顺序：载冻结Profile/源清单→构造request→Validate→MeasureAsync→异常/Unknown先GetOperation→记录释放事实/宿主存结果→CloseAsync；Closed=false保留清理监管引用。测试工程全部为Microsoft.NET.Sdk/net10.0/OutputType=Exe，仅BCL与受测工程；Halcon.Tests另通过受测Halcon工程使用已批准AsunImage。禁止引入待选测试包。每行唯一入口如下（目标工程除M0外未创建，命令本轮未执行）：

| 切片 | 唯一受测构建 / 唯一验证命令（Release） | 执行的用例 |
|---|---|---|
| M0 | `dotnet build src/Asun.Metrology.Core/Asun.Metrology.Core.csproj -c Release` / `dotnet run --project tests/Asun.Metrology.Core.Smoke/Asun.Metrology.Core.Smoke.csproj -c Release` | 附录 A 旧二维基线断言及§7/§16的旧API反例（**该工程尚未创建**，命令为切片获授权后的目标命令） |
| M1 | 同Core构建 / `dotnet run --project tests/Asun.Metrology.Core.Tests/Asun.Metrology.Core.Tests.csproj -c Release` | §12.0全部M1行、非法union/预算/canonical；§16正常到版本的适用pure断言 |
| M2 | `dotnet build src/Asun.Metrology.Runtime/Asun.Metrology.Runtime.csproj -c Release` / `dotnet run --project tests/Asun.Metrology.Runtime.Tests/Asun.Metrology.Runtime.Tests.csproj -c Release` | §14全部转移及§16重复/并发/取消/超时/关闭/通知故障，闩锁可控backend |
| M3/M4 | `dotnet build src/Asun.Metrology.Halcon/Asun.Metrology.Halcon.csproj -c Release` / `dotnet run --project tests/Asun.Metrology.Halcon.Tests/Asun.Metrology.Halcon.Tests.csproj -c Release` | §12/13实际26.05 good/bad/boundary；Metrology3D分组执行3D全方法及米单位/拓扑/体积反例 |
| M5接入 | `dotnet build tests/Asun.Metrology.HostTests/Asun.Metrology.HostTests.csproj -c Release` / `dotnet run --project tests/Asun.Metrology.HostTests/Asun.Metrology.HostTests.csproj -c Release` | §16.2两Host及§20.5只读桥两Host（软件欠账须先接收）、各自engine/observer/leases隔离、版本回退；物理资格另门 |

入口必须逐例输出稳定ID（`Method:scenario`、`Runtime:transition`、`Host:consumer`），全部必需断言完成且无未退出工作才返回0；失败、跳过必需项、测试截止或Unknown返回非零并列明ID。用固定时钟/有限闩锁验证截止，不用Sleep碰时序；外层进程截止不能把未结束判成功。`dotnet test`不运行这些Exe，禁止将其无报错当验证。benchmark独立于回归断言，不拿重复100次当时延统计。真实reference、Bias/Linearity/Stability/MSA和现场环境属于M5，物理阈值待批准不阻断pure数学/状态机定义。

### 16.2 两个无 UI Host 的完整目标调用示例

以下是**面向v0.2实现后的目标C#样例，本轮未编译**，展示完整请求、冻结Profile、两组独立reader/coordinate/service与关闭；可放入唯一HostTests的Program.cs。示例ID/hash表示合成Engineering fixture，不表示校准资产或真实样本。数值预算/截止仅用于该5mm解析样例harness，不是生产默认/性能目标。工作台适配Host与BatchReplayHost都走同一入口；前者实际接入时替换为ROI/坐标Owner的公开适配，后者替换为批量来源清单reader，不能复制公式。

```csharp
using System.Collections.Immutable;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Asun.Metrology.Contracts;
using Asun.Metrology.Core;
using Asun.Metrology.Runtime;

static AssetRef FixtureRef(string id) => new(id, 1,
    Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(id))).ToLowerInvariant());
var frame = FixtureRef("fixture:mm-frame");
var binding = new CoordinateBinding(frame, frame, FixtureRef("fixture:identity"), null, null);
SourcePayload a = new GeometryPayload(ImmutableArray.Create(
    new GeometryItem("a", new Point2(new P2(0, 0)))));
SourcePayload b = new GeometryPayload(ImmutableArray.Create(
    new GeometryItem("b", new Point2(new P2(3, 4)))));
SourceRef Source(string id, SourcePayload p) => new(
    new AssetRef(id, 1, MetrologyCanonical.HashSource(p)), frame, null,
    DataKind.Geometry, Unit.Mm);
var sa = Source("fixture:a", a);
var sb = Source("fixture:b", b);
var definition = new MetrologyDefinition(Method.PointDistance, Dimension.D2,
    Selector.Unique, null, null, AngleMode.Directed2D, VolumeMode.NetMagnitude,
    new NumericPolicy(1e-9, Unit.Mm, 1e-9, 1e-9), null, null, null,
    ImmutableArray<P3>.Empty, null, null);
var budget = new ExecutionBudget(16, 64, 4, 16, 65536, 1, 1,
    TimeSpan.FromSeconds(5), TimeSpan.FromSeconds(5));
var profile = new MethodProfile("0.2", "PointDistance/1", definition,
    null, null, null, SurfaceSign.Unsigned, false, budget);
var profileRef = new AssetRef("fixture:point-distance", 1,
    MetrologyCanonical.HashProfile(profile));
var request = new MetrologyRequest(
    new OperationKey(Guid.Parse("5b469859-8d18-4a45-a935-a8f99767c472"), 1),
    Scope.Engineering, profileRef,
    ImmutableArray.Create(new InputOperand("subject", Role.Subject, sa),
        new InputOperand("reference", Role.Reference, sb)), binding, definition, budget);

static void Assert5(MetrologyResult r) {
    if (r.Outcome != Outcome.Measured || r.Validity != Validity.Valid ||
        r.Candidates.Length != 1 || r.Candidates[0].Quantities.Length != 1 ||
        r.Candidates[0].Quantities[0] != new NamedQuantity(QuantityName.Distance, 5, Unit.Mm))
        throw new InvalidOperationException("Host:distance5");
}
// Root在factory之前预留；实际宿主由应用生命周期Owner持有，不能是会结束的页面局部变量。
var caseFailures = new List<Exception>();
var roots = new HostRoots(2, caseFailures);
using var suiteWall = new CancellationTokenSource(TimeSpan.FromSeconds(120));
foreach (var consumer in new[] { "WorkbenchAdapterHost", "BatchReplayHost" }) {
    HostRoot root;
    try { root = roots.Reserve(request, ImmutableArray.Create(a, b)); }
    catch (Exception e) { caseFailures.Add(e); break; } // 保已有roots，进入根监管，不从Main逃逸
    var start = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
    root.CaseTask = Task.Run(async () => {
        await start.Task;
        using var caseWall = CancellationTokenSource.CreateLinkedTokenSource(suiteWall.Token);
        caseWall.CancelAfter(TimeSpan.FromSeconds(6)); // 留独立close2s/dispose2s，总case≤10s
        try {
            var pure = GeometryMeasurements.Compute(request, profile, ImmutableArray.Create(a, b));
            Assert5(pure);
            root.Reader = new FixtureReader(profileRef, profile, sa, a, sb, b);
            root.Coordinates = new FixtureCoordinates(binding);
            root.Backend = new GeometryBackend();
            // 构造合同无I/O/native；构造完成以前Root已持有输入、借用端口和原Key。
            root.Service = new MetrologyService(root.Reader, root.Coordinates, root.Backend,
                new RuntimePolicy(16, 1, 32, TimeSpan.FromSeconds(2)));
            if (!root.Service.Validate(request).IsEmpty) throw new InvalidOperationException(consumer);
            root.MeasureTask = root.Service.MeasureAsync(request, null, caseWall.Token).AsTask();
            var result = await root.MeasureTask.WaitAsync(caseWall.Token);
            Assert5(result); // 即使Assert或宿主消费抛错，仍进入finally；保原业务错误。
            root.ReplayTask = root.Service.MeasureAsync(request, null, caseWall.Token).AsTask();
            var replay = await root.ReplayTask.WaitAsync(caseWall.Token);
            if (replay.ResultFingerprint != result.ResultFingerprint || root.Reader.Acquired != 2)
                throw new InvalidOperationException("Host:duplicate");
            var snapshot = root.Service.GetOperation(request.Key);
            if (snapshot.Phase != Phase.Completed || snapshot.Result?.ResultFingerprint != result.ResultFingerprint)
                throw new InvalidOperationException("Host:terminal");
        } catch (Exception e) { root.BusinessError = e; }
        finally {
            try {
                if (root.Service is not null) {
                    root.Service.RequestCancel(root.Request.Key);
                    root.CloseTask ??= root.Service.CloseAsync(TimeSpan.FromSeconds(2),
                        CancellationToken.None).AsTask();
                    using var cleanupWall = new CancellationTokenSource(TimeSpan.FromSeconds(2));
                    root.Close = await root.CloseTask.WaitAsync(cleanupWall.Token);
                }
            } catch (Exception e) { root.CleanupErrors.Add(e); }
            finally {
                // Close仍在途时不能叠加Dispose；所有原Task均留Root，晚返回由该Owner监管。
                if (root.Service is not null && !root.DisposeStarted &&
                    root.Close is { Closed: true, PendingNotifications: 0 } && root.Close.Pending.IsEmpty) {
                    try {
                        root.DisposeStarted = true; // 同步抛错也已尝试，不得因Task为null再调用
                        root.DisposeTask = root.Service.DisposeAsync().AsTask();
                        using var disposeWall = new CancellationTokenSource(TimeSpan.FromSeconds(2));
                        await root.DisposeTask.WaitAsync(disposeWall.Token);
                    } catch (Exception e) { root.CleanupErrors.Add(e); }
                }
            }
        }
    });
    start.SetResult(true); // CaseTask已登记才允许factory/业务开始
    using var outerCaseWall = CancellationTokenSource.CreateLinkedTokenSource(suiteWall.Token);
    outerCaseWall.CancelAfter(TimeSpan.FromSeconds(10));
    try { await root.CaseTask.WaitAsync(outerCaseWall.Token); }
    catch (Exception e) { root.CaseExitCode = 1; caseFailures.Add(e); } // 只结束等待，不删Root/原Task
    if (!roots.TryRelease(root)) {
        root.CaseExitCode = 1;
        caseFailures.Add(new InvalidOperationException("Host:owner-retained"));
    } // TryRelease先由原监督者保存错误；退槽不把失败变成功
    if (caseFailures.Count != 0) break; // 失败/未决停止派新case；未执行必需consumer也为非零
}
// 非零/停止派新工作不等于已清理；roots仍归应用根Owner持有，不能抛错后丢到GC。
if (caseFailures.Count != 0 || roots.Pending != 0) {
    Environment.ExitCode = 1;
    Console.Error.WriteLine($"Host:failed={caseFailures.Count}, pending={roots.Pending}");
}
// 失败后停止派发；保留同Root等迟到任务。不能从Main提前返回丢Owner。
try { await roots.ObservePendingAsync(suiteWall.Token); }
catch (OperationCanceledException) { Environment.ExitCode = 1; }
if (roots.Pending != 0) {
    Console.Error.WriteLine($"Host:suite-timeout, pending={roots.Pending}");
    roots.WritePendingDiagnostics(); // 输出原身份/phase与独立错误，不以超时冒释放
    // 外层180s进程监督器负责诊断退出；这里继续强持roots并查询，不宣称释放。
    while (roots.Pending != 0) {
        using var observation = new CancellationTokenSource(TimeSpan.FromSeconds(1));
        try { await roots.ObservePendingAsync(observation.Token); }
        catch (OperationCanceledException) { }
    }
}

sealed class HostRoots(int capacity, List<Exception> failures) {
    private readonly List<HostRoot> slots = new(); // 仅套件调度线程修改
    public readonly List<HostCaseRecord> Finished = new(); // 原监督者持有，不含service/source/Task
    public int Pending => slots.Count;
    public void WritePendingDiagnostics() {
        foreach (var r in slots) {
            Console.Error.WriteLine($"Host:key={r.Request.Key}, case={r.CaseTask?.Status}");
            if (r.CaseTask?.IsCompleted != true) continue; // 不读case仍在写的错误字段
            Console.Error.WriteLine($"Host:business={r.BusinessError}, close={r.Close?.Closed}, dispose={r.DisposeTask?.Status}");
            foreach (var e in r.CleanupErrors) Console.Error.WriteLine($"Host:cleanup={e}");
            try { Console.Error.WriteLine($"Host:snapshot={r.Service?.GetOperation(r.Request.Key)}"); }
            catch (Exception e) { Console.Error.WriteLine($"Host:query={e}"); }
        }
    }
    public HostRoot Reserve(MetrologyRequest request, ImmutableArray<SourcePayload> sources) {
        if (slots.Count >= capacity || slots.Count + Finished.Count >= capacity)
            throw new InvalidOperationException("Host:owner-capacity"); // 本harness总case也有界
        var root = new HostRoot(request, sources); slots.Add(root); return root;
    }
    public bool TryRelease(HostRoot r) {
        // 保存错误与确认归还分开；错误本身不证明仍有资源，也不证明已经释放。
        if (r.CaseTask?.IsCompleted == true) {
            foreach (var t in new Task?[] { r.CaseTask, r.MeasureTask, r.ReplayTask,
                r.CloseTask, r.DisposeTask }) {
                if (t is null || !t.IsCompleted || !r.ObservedTasks.Add(t)) continue;
                try { t.GetAwaiter().GetResult(); }
                catch (Exception e) { r.CleanupErrors.Add(e); }
            }
        }
        if (r.CaseTask?.IsCompleted != true) return false;
        if (!r.BusinessErrorSaved && r.BusinessError is not null) {
            failures.Add(r.BusinessError); r.BusinessErrorSaved = true; r.CaseExitCode = 1;
        }
        while (r.SavedCleanupErrors < r.CleanupErrors.Count) {
            failures.Add(r.CleanupErrors[r.SavedCleanupErrors++]); r.CaseExitCode = 1;
        }
        if (r.CaseExitCode != 0) Environment.ExitCode = 1; // 原监督者消费/保存，晚错误也不能归零
        if (r.MeasureTask is { IsCompleted: false } ||
            r.ReplayTask is { IsCompleted: false } || r.CloseTask is { IsCompleted: false } ||
            r.DisposeTask is { IsCompleted: false }) return false;
        if (r.Service is null) {
            // 此factory/fixture构造合同无IO/native/后台任务；失败前未取得任何私有资源。
            if (r.MeasureTask is not null || r.ReplayTask is not null || r.CloseTask is not null ||
                r.DisposeStarted || (r.Reader is not null && r.Reader.Acquired != 0)) return false;
        } else if (r.Close is not { Closed: true, PendingNotifications: 0 } ||
            !r.Close.Pending.IsEmpty ||
            r.DisposeTask?.IsCompletedSuccessfully != true || r.Reader is null ||
            r.Reader.Acquired != r.Reader.Released) return false; // 故障而无释放证明仍保槽
        Finished.Add(new HostCaseRecord(r.Request.Key, r.CaseExitCode,
            r.BusinessError?.ToString(), r.CleanupErrors.Select(e => e.ToString()).ToImmutableArray()));
        return slots.Remove(r);
    }
    public async Task ObservePendingAsync(CancellationToken stop) {
        while (slots.Count != 0) {
            stop.ThrowIfCancellationRequested();
            foreach (var r in slots.ToArray()) {
                if (r.CaseTask?.IsCompleted != true) continue; // 原case仍独占其业务/清理字段
                foreach (var task in new Task?[] { r.CaseTask, r.MeasureTask, r.ReplayTask,
                    r.CloseTask, r.DisposeTask }) {
                    if (task is null || !task.IsCompleted || !r.ObservedTasks.Add(task)) continue;
                    try { task.GetAwaiter().GetResult(); }
                    catch (Exception e) { r.CleanupErrors.Add(e); } // 晚故障被观察、独立保存
                }
                // 等待超时不自动重发Dispose。只有已结束且确认closed才可开始尚未开始的Dispose。
                if (r.CloseTask?.IsCompletedSuccessfully == true) r.Close = r.CloseTask.Result;
                if (r.Service is not null && !r.DisposeStarted &&
                    r.Close is { Closed: true, PendingNotifications: 0 } && r.Close.Pending.IsEmpty) {
                    try { r.DisposeStarted = true; r.DisposeTask = r.Service.DisposeAsync().AsTask(); }
                    catch (Exception e) { r.CleanupErrors.Add(e); }
                }
                if (TryRelease(r)) continue; // 错误已保存且归还确认才退槽，退出码仍非零
                if (!r.QueryFailed) {
                    try { _ = r.Service?.GetOperation(r.Request.Key); } // 查询不转交Owner、不变Key
                    catch (Exception e) { r.QueryFailed = true; r.CleanupErrors.Add(e); }
                } // 同一查询故障只登记一次，不让永久未知状态累积无界错误
            }
            if (slots.Count != 0) await Task.Delay(TimeSpan.FromMilliseconds(20), stop);
        }
    }
}
sealed record HostCaseRecord(OperationKey Key, int CaseExitCode,
    string? BusinessError, ImmutableArray<string> CleanupErrors);
sealed class HostRoot(MetrologyRequest request, ImmutableArray<SourcePayload> sources) {
    public readonly MetrologyRequest Request = request;
    public readonly ImmutableArray<SourcePayload> Sources = sources;
    public FixtureReader? Reader;
    public FixtureCoordinates? Coordinates;
    public GeometryBackend? Backend;
    public MetrologyService? Service;
    public Task? CaseTask, DisposeTask;
    public Task<MetrologyResult>? MeasureTask, ReplayTask;
    public Task<CloseReceipt>? CloseTask;
    public CloseReceipt? Close;
    public Exception? BusinessError;
    public readonly List<Exception> CleanupErrors = new();
    public readonly HashSet<Task> ObservedTasks = new();
    public bool QueryFailed, DisposeStarted, BusinessErrorSaved;
    public int SavedCleanupErrors, CaseExitCode;
}

sealed class FixtureReader(AssetRef profileRef, MethodProfile profile,
    SourceRef sa, SourcePayload a, SourceRef sb, SourcePayload b) : IMetrologyInputReader {
    public int Acquired { get; private set; }
    public int Released { get; private set; }
    public ValueTask<MethodProfile> ReadProfileAsync(AssetRef p, ExecutionBudget budget,
        CancellationToken token) {
        token.ThrowIfCancellationRequested();
        if (p != profileRef) throw new InvalidOperationException("Fixture:profile");
        return ValueTask.FromResult(profile);
    }
    public ValueTask<IInputLease> AcquireAsync(SourceRef s, ExecutionBudget budget,
        CancellationToken token) {
        token.ThrowIfCancellationRequested();
        var payload = s == sa ? a : s == sb ? b : throw new InvalidOperationException("Fixture:source");
        Acquired++;
        return ValueTask.FromResult<IInputLease>(new Lease(s, payload, () => Released++));
    }
    sealed class Lease(SourceRef source, SourcePayload payload, Action release) : IInputLease {
        public SourceRef Source => source;
        public SourcePayload Payload => payload;
        private LeasePhase phase = LeasePhase.Held;
        public LeasePhase GetReleaseReceipt() => phase;
        public ValueTask DisposeAsync() {
            if (phase != LeasePhase.Released) { release(); phase = LeasePhase.Released; }
            return ValueTask.CompletedTask;
        }
    }
}
sealed class FixtureCoordinates(CoordinateBinding expected) : IMetrologyCoordinatePort {
    public ValueTask<AssetRef> ValidateBindingAsync(CoordinateBinding b, Scope scope,
        ExecutionBudget budget, CancellationToken token) {
        token.ThrowIfCancellationRequested();
        if (b != expected || scope != Scope.Engineering)
            throw new InvalidOperationException("Fixture:binding");
        return ValueTask.FromResult(expected.Mapping);
    }
    public async ValueTask<MappingReceipt> MapAsync(CoordinateBinding b,
        ImmutableArray<P3> points, Unit unit, Scope scope, ExecutionBudget budget,
        CancellationToken token) {
        await ValidateBindingAsync(b, scope, budget, token);
        if (unit != Unit.Mm) throw new InvalidOperationException("Fixture:unit");
        return new MappingReceipt(b, points, Unit.Mm, MappingKind.Identity,
            ImmutableArray<double>.Empty, expected.Mapping);
    }
}
```

fixture端口的意外异常只用于揭露harness接线错误；实际端口按§11.3用MetrologyPortException分类。这里只验证5mm定义、重复一次计算、两engine各自2租约归还与关闭，不证明真实第二产品资格或HALCON/WPF性能。扩展用例：取消backend退出闩锁前Close=false/Pending含原key；释放闩锁后仅一次Cancelled终态、2租约归还；旧key变参数IdentityConflict且Acquired不增；不同ContractVersion在native开始前拒绝；回退重新创建旧版本engine仅接新key，旧结果hash不改。

### 16.3 Host 根Owner、有限截止与清理反例（v0.2/v0.3共用）

§16.2的HostRoots是**宿主harness类型**，不属于metrology公共DLL。根应用Owner在任何factory/Task.Run/端口获取之前预留槽；无槽先拒新case，不启动工作。Root强持原Request/Key/source及reader/coordinate/backend/service，所有Measure/Replay/Close/Dispose的原Task只创建并记录一次；等待用WaitAsync，超时不把原Task替换成超时代理。Task.Run通过start闩锁等Root.CaseTask已登记才启动，防factory快返回/同步抛错导致孤儿。业务异常保存BusinessError，Close与嵌套Dispose各用独立2s wall窗口及新CTS，不能用已取消的业务token；清理错误附加，不能覆盖原业务。

固定harness截止：每case真实wall 10s（业务最多6s+Close2s+Dispose2s）；suite真实wall120s；外层进程180s。虚拟时钟控制Runtime的Execution/DrainTimeout触发与闩锁顺序，**不驱动**harness wall。任何10s未完成、120s suite截止、180s外层终止、未决Root或必需case未执行均非零；外层强制终止只能标ExternalProcessTimeout/释放未知，不能作为Closed回执。benchmark仍由消费者Profile定义，不套此测试截止作生产节拍。

外层监督器在§16.1 Release构建完成后直接启动唯一HostTests apphost（避免`dotnet run`父/子进程退出混淆），目标命令如下，**本轮未执行**；只有ExitCode0且全部case/Owner断言完成才通过。外层停止的是本次明确启动的测试进程，不能清理用户其它进程/工作树。

```powershell
$hostTestApp = (Resolve-Path -LiteralPath 'tests\Asun.Metrology.HostTests\bin\Release\net10.0\Asun.Metrology.HostTests.exe').Path # 当前目录为仓库根
$hostTestProcess = Start-Process -FilePath $hostTestApp -WorkingDirectory (Get-Location).Path -WindowStyle Hidden -PassThru
if (-not $hostTestProcess.WaitForExit(180000)) {
    Stop-Process -Id $hostTestProcess.Id -Force
    throw 'Host:ExternalProcessTimeout; resources unknown'
}
if ($hostTestProcess.ExitCode -ne 0) { throw "Host:failed exit=$($hostTestProcess.ExitCode)" }
```

样例程序不得在有Pending roots时从Main返回导致监管被GC丢弃；失败套件停止派发后，根应用保留roots并运行有限监管至suite120s，继续观察原Case/Measure/Close/Dispose（不重调用正在执行的Dispose）。suite截止仍未清理，输出原key/phase/业务与清理错误，保留根Owner至外层180s诊断退出；未接收转交不得释放本地槽。本例不提供持久transfer功能；产品若转交，必须目标Owner先强持同一service/全部原Task/source/借用端口并返回带原key与Owner代次的接收确认，源Owner收到确认才退出监管。只发送通知、写一条清单或“安排后台清理”均不算转交确认。终止进程结束监管不追认资源已释放，宿主恢复清单显示Unknown。

错误保存与资源退槽是两项独立断言：TryRelease只在CaseTask结束后由原监督者观察每个原Task一次，将BusinessError及新增CleanupErrors保存到套件failures，并复制到无资源引用的Finished记录；CaseExitCode及进程退出码一经失败不归零。空factory/Compute失败且Service未创建时，本例fixture/GeometryBackend/service构造合同必须保证无IO/native/后台任务、无已取得租约；满足这一零资源断言即可退空槽，无需伪造Close/Dispose。已创建Service时须原Task均完成、Closed=true、原Dispose成功及租约归还交叉核对后才退槽，历史业务错误/等待超时错误不阻止已确认资源退槽。Finished总量与本例case总数同为2的上限；后续正式套件用其必需case数量Profile，不无限留档。

恢复只在旧Close/Dispose Task真正完成后由同Root串行决定下一步；Close=false/ReleaseUnknown/Dispose故障而不能证明归还时保持原账本，先GetOperation/lease/backend原回执；清理过程等待超时也不重发在途Dispose。只有端口明确幂等且前一调用已结束、原Owner判定可继续，才在产品恢复策略中发下一次清理并保原Task历史（数量受Root容量及恢复次数Profile有界）。本harness不自动重试；DisposeStarted在调用前置true，连同步抛错而尚无Task也不能重发。原reader/Profile/Acquire/Map尚未返回时Root持service与输入闭包，Runtime继续接管迟到lease/回执，先退出后逆序释放；不能由Host先dispose借用端口。Dispose失败原业务Task仍留Root观察结果/错误，错误相互独立。Reader.Acquired/Released仅fixture交叉断言，真实释放依据仍是Runtime与lease/BackendReceipt。

| 稳定case ID | 触发 / 必须断言 |
|---|---|
| Host:consumer-assert / consume-fault | 两Host分别在结果断言/宿主存储抛错；嵌套finally仍各一次Close/Dispose，确认归还后退槽/无Pending，不等180s；原监督者保存业务错及Finished.CaseExitCode=1，进程非零，0新测量 |
| Host:consumer-empty-root / cleanup-late-success | pure Compute/零资源factory抛错、尚无Service则保存错误后退空槽；Close/Dispose等待超时但原Task后来成功并确认全部归还则退槽，等待错误仍保存/非零；不能把Dispose真正fault且无释放证明当同例成功 |
| Host:consumer-reader-fault | reader/Profile/Map先或后抛错；所有已取得lease归还，未取得的晚Task保原Root；正常清理可移除槽，未确认不能移除 |
| Host:consumer-never-measure | 原Measure Task永不完成；6s业务wait结束，10s case不成功，原Task/Key/source/端口强持；不调用第二Measure掩盖 |
| Host:consumer-late-acquire / late-map / late-profile | 业务wait退出后原端口闩锁返回；仍归原key；晚lease唯一Dispose且释放回执确认，旧值不提交新revision |
| Host:consumer-close-unknown / dispose-fault | Close Task成功返回Closed=false仍Dispose调用0次；Closed=false或有Pending/PendingNotifications时保原Close/原Owner，有限查询，不重发在途Close/Dispose；ReleaseUnknown或Dispose真正抛错/在途且不能证明归还则保槽，Dispose同步抛错也只尝试一次，业务错误与清理错均可读；只超时的原Task后来成功按cleanup-late-success退槽 |
| Host:consumer-root-capacity / transfer-no-ack | factory前槽满或目标未确认接管；不启动新任务、不丢原Owner，suite失败而非悄悄成功 |
| Runtime:late-input / early-result / callback-hang | 端口晚返回、Backend早Result未Exited、用户回调不退；snapshot/回执与PendingNotifications准确，Close不能凭Task完成返回true |
| Runtime:dispose-single-flight / cleanup-after-cancel | cleanup用独立token，晚Dispose不重入；真实退出后才ResourcesReleased，唯一终态，10/120/180 wall不受虚拟时钟推进 |

HostTests入口按照上述Root监管嵌套finally实现；§16.2代码只展示两个正常case及fault时保留规则，单个case同步factory永久卡死也由已登记CaseTask与外层wall覆盖，不能用Task.Run声称native可抢占。真实应用根Owner有自己的关闭与恢复策略，本规格不改变设备急停/资产Owner。

## 17. 研究来源、实际采纳与局限

既有DZ-XVision/AOI.Main/AsunMeasure及2026-10-06 H:\docs范围/hash沿§9复用，不重复全树扫描。只读旧项目的流程/参数/发布结论不进入目标Contract；仍保留原证据。新增本轮直接研究如下，没有下载整仓/复制代码或新增依赖。

| 来源/版本与精确定位 | 实际核对及采纳落点 | 局限/许可/依赖 |
|---|---|---|
| 本地HALCON 26.05.0.0，`distance_pp/pl/ps/ss`、`distance_point_line`、`angle_ll`、`vector_to_hom_mat2d`、`affine_trans_point_2d/pixel` | Description区分无限线/有限段、角度方向、最少3对应点、pixel-center差异；§12/13处理 | 只证明算子语义，不证明本平台几何资格或性能；AsunImage依赖按项目批准，不复核封装存在/许可 |
| 本地 `gen_measure_rectangle2`、`measure_pos/pairs`、`apply_metrology_model`、`get_metrology_object_result`、`set_metrology_object_param/model_param`、`fit_line/circle_contour_xld` | scan忽略domain、插值边界、Sigma范围、Select/Transition、RANSAC seed和实例无序、robust参数；§13/16 | 弱信号/遮挡/支持Profile与同样本实测仍缺；min_score不是置信度/公差；没有最快结论 |
| 本地 `area_center/xld`、`moments_region_2nd/xld`、`test_self_intersection_xld`、`area_object_model_3d`、`distance_object_model_3d`、`fit_primitives_object_model_3d`、`volume_object_model_3d_relative_to_plane`、`intersect_plane_object_model_3d` | empty0、XLD自动闭合、normalized area moments、写distance属性/截断、plane各fit算法相同、volume最终abs及远面不稳；§12–16 | point moments不是volume moments；bbox center不是重心；有洞/未知/多层不补；mesh self-intersection几何检查需实际测试，不靠watertight单项证明 |
| 2026-10-10定向补读：本地 `svd_matrix.html`、`fit_rectangle2_contour_xld.html`，并复核3D fitting/distance及metrology参数/result页面 | reduced/none奇异值；矩形8点/每边内点/3266；primitive半径单位meter、plane/cylinder朝原点的native符号；method='kd-tree'；used_edges row/column/amplitude；distance_threshold与instances_outside_measure_regions。正文§11–14明确字段/重拟合/符号/单位 | 只读实际Description/Parameters，不扫描AsunImage；不是编译/图像验证。3D最少点数plane3/sphere4/cylinder5不等于可辨识或物理资格；native资源上界仍待目标adapter证据 |
| [Math.NET Numerics v5.0.0](https://github.com/mathnet/mathnet-numerics/tree/4435308e1b0efcb40dc483140059a4e3a2204044)，commit `4435308e1b0efcb40dc483140059a4e3a2204044` | 读取 `src/Numerics/LinearAlgebra/Double/Factorization/DenseSvd.cs` 和 `src/Numerics.Tests/LinearAlgebraTests/Double/Factorization/SvdTests.cs`：源码clone输入再分解、Solve需vectors，测试覆盖非方rank/奇异/重构/求解；采纳为归一化affine rank/病态反例及独立数值Oracle (§12/16) | MIT，已读LICENSE；DenseSvd受进程级LinearAlgebraControl.Provider影响且full U分配可大，不能复制global provider/不受控矩阵进入Core；项目v5 target netstandard2.0/net6等，native provider另包，本轮不增产品NuGet依赖或宣称.NET10验收。正规方程会平方条件数，不能只从Smoke residual小推稳健 |
| [NIST TN1297 §5 Combined Standard Uncertainty](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-5-combined-standard-uncertainty)，§5.1/5.2直接读网页 | 组合包含covariances，显著系统效应的correction与其uncertainty分开；§15.2严格不将RMS/score当数值uncertainty | 官方专业指导，不是本平台自动生产接受值；旧e-Handbook/Appendix网页403，未据未读正文声称采用其公式；一阶模型/相关性必须具体证明 |
| [BIPM JCGM出版目录](https://www.bipm.org/en/committees/jc/jcgm/publications) | 本轮读目录确认JCGM100:2008、101:2008、GUM-6:2020的文献身份；只作为未来非线性/分布传播查阅入口 | 未读PDF正文，不将目录/2026新增条目当已验证算法。Monte Carlo本版未准入，依具体切片再研究 |

Math.NET读取文件hash：DenseSvd `a01bedf6743e426cb03d09f840ee221f9a350d5937c8bc192134924c0dbc860d`；SvdTests `6ec5be2244f675282b471f79a0d6cd29a2800420d0a611b3f0cbee108add35d4`；LICENSE `3f87fb0bec6467d87760555e3cb246646a51912b0e97f432c159ba6baf5738f2`。只记录可复核来源，不增加临时快照或假性能数据。

## 18. 六项准入结论与外部实现者自审

外部实现者可在后续获派代码任务时据§10构建包/Host、§11构造强类型请求和注入port、§12选择唯一定义、§13设明确Profile、§14查询排空/关闭、§15读版本证据、§16运行定向断言。主控已接收M1/M2/C1–C4六项切片规格，并限定内容接收§20的M3/M4公开装配与基础只读桥指导；仍不能凭record、旧Smoke或规格接收宣称未实现v0.2/v0.3已可运行，未接收的适配与产品资格不得由编码者补猜。

| DEV-GOV-010 §3.1 | 本轮准备结论 | 尚影响的切片 |
|---|---|---|
| 1职责/非目标/第二消费者 | 六项切片的2D/3D职责、与ROI/工作台/基面/统计分界及两个受控Host接法已接收 | M5真实第二产品资格及实际消费者字段映射尚无证据 |
| 2精确API/单位/失败/资源 | §11/12/15基础v0.2与§19连续v0.3公开值/端口、主路线、预算、Owner已按六项切片接收；§20的backend公开构造/基础只读桥指导已限定内容接收 | M3/M4真实native/物理未获Ready；§20.5 Codec/参数名装配已闭合；native包络及真实连续支撑/分解/参考用途回执分别接收 |
| 3无UI最小Host/依赖 | 六项切片Contracts/Core/Runtime、独立csproj及受控fixture/双Host规格已接收；§20.5基础桥两Host装配与恢复指导已限定内容接收，UI N/A | 两Host的软件公开装配已闭合；E-Build公开程序集及消费者编译未执行，M0真实引用迁移与构建/运行未执行，不因批准HALCON依赖重复授权核验 |
| 4异常/并发/取消/恢复样例 | §12/14/16及§19.9解析反例；§16.3有界Root/原Task/单飞清理/10–120–180s独立wall规格已接收 | 实际BCL/Golden/资源释放证据未执行；不能将Host代码块/自审当PASS |
| 5BenchmarkProfile | 六项切片的§16.1及§19.9负载、测点、失败/删失口径、托管上限与测试预算已接收 | Consumer样本计划/目标待采纳则NotEvaluated；M3/4资源包络为adapter规格门，同样本正确性/拒识/性能待测 |
| 6唯一工程/路径/最小调用 | §10/16.1唯一BCL Exe/Release命令，§16.2/16.3双Host有界Owner，§19.9连续C1–4复用同工程规格已接收 | 目标工程尚不存在，示例未编译；M5标准件/客户阈值/现场物理门只阻断物理资格 |

文档整体保持DesignReview/Prep；M1/M2/C1–C4六项切片为ModuleCoreImplementationReady，仅表示§10限定范围规格准备，不表示“全部实现通过”。基础与连续能力须合看§19.1及本表，不能拿六项切片接收替代整模块适配/产品资格。§20的M3/M4公开装配、基础只读桥、逐字段消费、原Task/lease/关闭及双Host指导已由主控限定内容接收；其Engineering/有限PixelDiagnostic及Unsupported边界保持，不升级真实native/物理Ready。两轮有限反例自审沿数学/支撑和外部Host/资源生命周期修订；结构校验不代替执行。剩余门按§21.2逐Owner/实际输入与运行证据限定：工作台产品投影和连续/生产资格回执、N-Envelope逐Method真实资源proof、E-Build公开程序集/消费者编译与真实工程引用迁移、native/Golden运行和性能。参数推荐目标API现见§13.3–4，完整图像读桥见§20.7，未实现/未升准入；定量uncertainty传播/非线性Region单元积分未在本版开放，不能由编码者暗加；旧规划连续/Q能力已在§19明确，不作为泛化“待设计”。

最新独立模块架构§7.1已明确完整AsunImage薄封装，不再保留旧算子存在性门槛。跨模块port映射只交主任务串行接收，本文不写共享/其它模块文件。真实编译、BCL Exe、HALCON Golden/Replay、WPF宿主、性能/峰值资源和标准件/现场资格均未执行；metrology本身无UI，真实WPF只在工作台接入资格范围适用。六项Core规格已接收，不因客户标准件/设备条件缺失而退回猜设计；后续代码切片仍由主任务明确指定，本轮状态同步没有启动实现。

## 19. 完整模块连续量测 Contract v0.3（目标；C1–C4 Core规格已接收，尚未实现）

本节将原DEV-MET-031 §5–13中属于metrology的已有规划收进本唯一指导；C1–C4 Core规格已接收，旧共享页仅作研究/应用导航，不定义第二套活动公式或算法。v0.2 DTO编码不变；v0.3是独立版本入口，不能把旧Method加enum值后仍称Contract0.2。v0.3复用v0.2的OperationKey、AssetRef、P2/P3/V3、Polygon2、Plane3、Outcome/Validity/Error、事件、RuntimePolicy、关闭/Owner语义，不改变旧指纹。新增目标代码仍在Contracts/Core/Runtime/Halcon及原唯一测试工程，不新建“积分库/矩引擎”。

### 19.1 能力、真实消费者与实施切片

| 能力与旧规划来源 | v0.3唯一调用/输出 | 真实规划消费者/切片 |
|---|---|---|
| 连续有限截面/方向高度剖面/沿程积分；旧§5/9.3 | SectionOptions、PathOptions → SectionReport/PathReport | PG-016胶路、PG-021涂层、钢网槽；C1解析Core+已有ROI/表面适配 |
| 轴端/指定截面邻接/方向投影；旧§6/7 | AxisOptions、ProjectionOptions → AxisReport/ProjectionReport | PG-019插件、PG-020焊后；C1，不提取/识别针型 |
| 有效域积分及未知条件界；旧§9 | FieldOptions → FieldReport.Domain/Integral | PG-016胶体、PG-021合格厚度域、SPI；C2线性有限归约 |
| 连续面积矩/正部体积中心；旧§10 | FieldOptions → AreaMoments3/PositiveCenter | SPI 055C面积/体积中心、PG-016胶点独立中心偏移；C2 |
| 连续面积高度CDF/左逆分位；旧§11 | FieldOptions → CdfResult/QuantileResult | SPI FS-050/055C、PG-016 §16.4；C3线性面积分布 |
| 有限平面方向高度及局部平行层关系；旧§12 | PlaneOptions → PlaneReport | AOI本体/引脚、PG-021局部平行层模型；C1 |
| 仿射顶部减Q二阶参考的signed积分、正负包络、CDF/分位；旧§13 | QuadraticReference+FieldOptions →同FieldReport及NumericCertificate | reference-surface提供已资格Q，SPI/点胶/涂层按用途显式选用；C4 |

上述消费者的工艺身份、材料判定、Required、公差/guard band、事实存储、放行和设备动作仍归各PG/宿主；它们消费同一字段与数值Owner。两个无UI接入仍为WorkbenchAdapterHost/BatchReplayHost，增加上述fixture和组合调用，不以两个harness名称冒充两个现场产品。连续场C2–4是具名权重/精确有限归约，不重写分割、重建或Q拟合；几何/原场资格由ROI/surface/reference Owner提供。

### 19.2 强类型输入、参数与结果（Asun.Metrology.Contracts，全部字段）

```csharp
public enum ContinuousMethod { Sections, PathIntegral, AxisRelations,
    Projection, PlaneRelations, SupportedField, GeometryMeasures }
public enum DomainPurpose { GeometricHeight, MaterialWindow }
public enum DomainClass { Material, NonMaterial, UnknownMaterial, Geometric }
public enum FieldModel { AffineTriangles, AffineTopMinusQuadratic, AreaDomain }
public enum DomainMeasure { HeightField, AreaOnly }
public enum HeightTransform { Signed, PositiveOnSameDomain }
public enum CoverageRequirement { FullTarget, KnownPartDiagnostic }
public enum LayerCorrespondence { None, SameReferenceRay, TargetNormalOffset }
public enum NumericStatus { Qualified, BudgetStopped, ToleranceNotMet,
    ArithmeticConflict, OutOfRange, UnsupportedDomain }
public readonly record struct Interval(double Lower, double Upper);
public sealed record PhysicalFrame(P3 Origin, V3 U, V3 V, V3 N, AssetRef Frame);
public sealed record Triangle2(P2 A, P2 B, P2 C);
public sealed record PlanarDomain(ImmutableArray<Polygon2> Components,
    ImmutableArray<Triangle2> Triangles, AssetRef Decomposition);
public sealed record PlanePatch(string Id, Plane3 Plane, PhysicalFrame LocalFrame,
    PlanarDomain ObservedDomain, PlanarDomain PermittedPredictionDomain, AssetRef Qualification);
public sealed record SurfaceCell(string CellId, Triangle2 OriginalTriangle,
    ImmutableArray<double> TopHeightsMm, ImmutableArray<double> BottomHeightsMm,
    PlanarDomain QualifiedDomain, AssetRef WholeCellSupport,
    ImmutableArray<AssetRef> Sources);
public sealed record DomainPartition(PlanarDomain TargetD, PlanarDomain MaterialF,
    PlanarDomain NonMaterialB, PlanarDomain UnknownMaterialUs, PlanarDomain UnknownHeightUh,
    PlanarDomain GeometricKnownE, PlanarDomain GeometricUnknownU,
    AssetRef Classification, AssetRef BoundaryQualification);
public sealed record QualifiedFragment(string FragmentId, string? OriginalCellId,
    Triangle2 Triangle, DomainClass Class, ImmutableArray<AssetRef> Sources);
public sealed record QuadraticReference(AssetRef Model, P2 Center,
    double ScaleXmm, double ScaleYmm, double CenterZmm, double ScaleZmm,
    ImmutableArray<double> Coefficients, PlanarDomain Applicability,
    AssetRef Qualification);
public sealed record UnknownHeightBound(Interval HeightMm, AssetRef Proof,
    bool CoversKnownHeightDomain);
public sealed record SupportedField(PhysicalFrame Frame, DomainPurpose Purpose,
    FieldModel Model, DomainPartition Domains, ImmutableArray<SurfaceCell> Cells,
    ImmutableArray<QualifiedFragment> Fragments, QuadraticReference? Quadratic,
    UnknownHeightBound? UnknownBound);
public sealed record SectionQuery(string Id, P3 Origin, V3 Direction,
    double MinTmm, double MaxTmm);
public sealed record PathNode(string Id, double ArcLengthMm, P3 Position,
    double? ValueMm, AssetRef? Support);
public sealed record PathInterval(string LeftId, string RightId, AssetRef? WholeIntervalSupport);
public sealed record FiniteAxis(string Id, P3 Origin, V3 Direction,
    double MinTmm, double MaxTmm, P3? ObservedEndpoint, AssetRef Qualification);
public sealed record AxisPair(string Id, string FirstAxisId, string SecondAxisId);
public sealed record ProjectionPair(string Id, P3 From, P3 To);
public abstract record ContinuousPayload;
public sealed record SectionInput(PlanarDomain OccupiedDomain,
    PhysicalFrame Frame, ImmutableArray<SectionQuery> Queries) : ContinuousPayload;
public sealed record PathInput(ImmutableArray<PathNode> Nodes,
    ImmutableArray<PathInterval> Intervals) : ContinuousPayload;
public sealed record AxisInput(PlanePatch Datum, double SectionOffsetMm,
    ImmutableArray<FiniteAxis> Axes, ImmutableArray<AxisPair> Pairs) : ContinuousPayload;
public sealed record ProjectionInput(V3 Direction,
    ImmutableArray<ProjectionPair> Pairs) : ContinuousPayload;
public enum GeometryMeasureKind { EllipseSize, BoundaryPerimeter, AreaEquivalentDiameter }
public sealed record EllipseGeometry(P2 Center, double MajorRadiusMm,
    double MinorRadiusMm, double PhiRad);
public sealed record GeometryMeasureInput(EllipseGeometry? Ellipse,
    ImmutableArray<Contour2> Boundaries, PlanarDomain? Domain) : ContinuousPayload;
public sealed record PlaneInput(PlanePatch Reference, PlanePatch Target,
    ImmutableArray<P2> PositionsUv, PlanarDomain EvaluationDomain,
    double? NormalLayerThicknessMm, AssetRef? ThicknessSource,
    PlanePatch? LowerLayer) : ContinuousPayload;
public sealed record FieldInput(SupportedField Field) : ContinuousPayload;
public abstract record ContinuousOptions;
public sealed record SectionOptions(Selector Selector,
    string? IntervalId) : ContinuousOptions;
public sealed record PathOptions(bool ClosedPath) : ContinuousOptions;
public sealed record AxisOptions(double MinimumAbsNormalDot,
    double MaximumEndpointRadialErrorMm) : ContinuousOptions;
public sealed record ProjectionOptions() : ContinuousOptions;
public sealed record GeometryMeasureOptions(GeometryMeasureKind Kind) : ContinuousOptions;
public sealed record PlaneOptions(double MinimumAbsNormalDot,
    AngleMode AngleMode, LayerCorrespondence Correspondence) : ContinuousOptions;
public sealed record FieldOptions(CoverageRequirement Coverage,
    HeightTransform Transform, bool Integral, bool AreaMoments,
    bool PositiveVolumeCenter, bool EquivalentMomentEllipse,
    ImmutableArray<double> CdfHeightsMm,
    ImmutableArray<double> Probabilities) : ContinuousOptions;
public sealed record ContinuousNumericPolicy(double LengthToleranceMm,
    double RelativeTolerance, double AngleToleranceRad,
    double MaximumHeightWidthMm, double MaximumAreaWidthMm2,
    double MaximumVolumeWidthMm3, double MaximumProbabilityWidth,
    double MinimumAreaMm2, double MinimumVolumeMm3,
    double MinimumEigenGapMm2, double MaximumCenterWidthMm,
    int MaximumIntegerBits, long MaximumRationalOperations,
    int MaximumRoots, int MaximumLeaves, int MaximumDepth,
    int MaximumEvents, int MaximumQueries, int MaximumInverseIterations,
    int MaximumClipVertices, int MaximumFragments);
public sealed record ContinuousProfile(string ContractVersion, string MethodVersion,
    ContinuousMethod Method, ContinuousOptions Options,
    ContinuousNumericPolicy Numeric, ExecutionBudget Budget);
public sealed record ContinuousRequest(OperationKey Key, Scope Scope,
    AssetRef Profile, AssetRef Input, AssetRef TargetFrame,
    ContinuousMethod Method);
public sealed record DomainReport(DomainMeasure Measure, Interval TargetAreaMm2, Interval MaterialAreaMm2,
    Interval NonMaterialAreaMm2, Interval UnknownMaterialAreaMm2,
    Interval KnownHeightAreaMm2, Interval UnknownHeightAreaMm2,
    ImmutableArray<Triangle2> CompletedE, ImmutableArray<Triangle2> RemainingU,
    ImmutableArray<string> CompletedFragmentIds, bool TargetComplete);
public sealed record SectionInterval(string Id, double LeftTmm, double RightTmm,
    double WidthMm, double MidpointOffsetMm, P3 Left, P3 Right);
public sealed record SectionItem(string QueryId, ImmutableArray<SectionInterval> Intervals,
    Validity Validity, MetrologyError? Error);
public sealed record SectionReport(ImmutableArray<SectionItem> Items);
public sealed record PathPiece(string LeftId, string RightId, double LengthMm,
    double IntegralMm2, Validity Validity, MetrologyError? Error);
public sealed record PathReport(ImmutableArray<PathPiece> Pieces,
    double KnownLengthMm, double UnknownLengthMm, double? KnownIntegralMm2);
public sealed record AxisItem(string AxisId, P3? SectionPoint,
    double? NormalProtrusionMm, double? AxialProjectionMm,
    double? TiltRad, double? TangentURad, double? TangentVRad,
    Validity Validity, MetrologyError? Error);
public sealed record AxisPairValue(string PairId, double? DistanceMm,
    Validity Validity, MetrologyError? Error);
public sealed record AxisReport(ImmutableArray<AxisItem> Axes,
    ImmutableArray<AxisPairValue> Pairs, double? ValidSubsetHeightRangeMm);
public sealed record ProjectionValue(string PairId, double EuclideanMm,
    double DirectedProjectionMm);
public sealed record ProjectionReport(ImmutableArray<ProjectionValue> Values);
public enum GeometryQuantity { MajorAxis, MinorAxis, Area,
    EquivalentAreaDiameter, BoundaryPerimeter }
public sealed record GeometryQuantityValue(GeometryQuantity Name, Interval Value, Unit Unit);
public sealed record GeometryMeasuresReport(ImmutableArray<GeometryQuantityValue> Values);
public sealed record PlanePositionValue(int PositionIndex, P3? TopPoint,
    double? DirectionHeightMm, P3? LowerPoint, double? LowerDirectionHeightMm,
    bool ModelPrediction, Validity Validity, MetrologyError? Error);
public sealed record PlaneReport(ImmutableArray<PlanePositionValue> Positions,
    double AngleRad, Interval? WholeModelHeightRangeMm);
public sealed record AreaMoments3(Interval M00mm2, Interval M10mm3, Interval M01mm3,
    Interval M20mm4, Interval M11mm4, Interval M02mm4,
    Interval? CenterUmm, Interval? CenterVmm,
    Interval? CovUUmm2, Interval? CovUVmm2, Interval? CovVVmm2,
    Interval? PrincipalVariance1mm2, Interval? PrincipalVariance2mm2,
    double? PrincipalAngleRad, double? EquivalentEllipseAxis1mm,
    double? EquivalentEllipseAxis2mm);
public sealed record PositiveCenter(Interval VolumeMm3, Interval Jumm4,
    Interval Jvmm4, Interval Khhmm4, Interval? U, Interval? V, Interval? H);
public sealed record IntegralReport(Interval SignedMm3, Interval PositiveMm3,
    Interval NegativeMagnitudeMm3, Interval AbsoluteMm3,
    Interval? ConditionalWholeSignedMm3);
public sealed record CdfResult(double HeightMm, Interval KnownMassMm2,
    Interval KnownProbability, Interval? ConditionalWholeProbability);
public sealed record QuantileResult(double Probability, Interval KnownHeightMm,
    Interval? ConditionalWholeHeightMm);
public sealed record ConstantMass(Interval HeightMm, Interval AreaMm2,
    ImmutableArray<string> FragmentIds);
public sealed record NumericCertificate(NumericStatus Status,
    int RootCount, int LeafCount, int DeepestLevel, long RationalOperations,
    int PeakIntegerBits, Interval? WholeModelExtremaMm,
    ImmutableArray<string> StoppedFragmentIds, string ReasonKey);
public sealed record FieldReport(DomainReport Domain, IntegralReport? Integral,
    AreaMoments3? Moments, PositiveCenter? PositiveCenter,
    ImmutableArray<CdfResult> Cdf, ImmutableArray<QuantileResult> Quantiles,
    ImmutableArray<ConstantMass> Atoms, NumericCertificate Numeric);
public abstract record ContinuousReport;
public sealed record SectionsResult(SectionReport Value) : ContinuousReport;
public sealed record PathResult(PathReport Value) : ContinuousReport;
public sealed record AxesResult(AxisReport Value) : ContinuousReport;
public sealed record ProjectionResult(ProjectionReport Value) : ContinuousReport;
public sealed record PlanesResult(PlaneReport Value) : ContinuousReport;
public sealed record FieldResult(FieldReport Value) : ContinuousReport;
public sealed record GeometryMeasuresResult(GeometryMeasuresReport Value) : ContinuousReport;
public sealed record ContinuousResult(OperationKey Key, Outcome Outcome,
    Validity Validity, Scope Scope, ContinuousReport? Report,
    MetrologyError? Error, ImmutableArray<AssetRef> Evidence,
    string ContractVersion, string MethodVersion, string BackendVersion,
    string ResultFingerprint);
```

封闭联合只允许上述case，Method/Options/Payload按名称一一对应，无关参数为null/Empty；所有array非default，ID非空/NFC/ordinal唯一，p有限∈[0,1]且按原请求顺序回填；重复p可共享计算但不删输出。Scope只允许Engineering/CalibratedPhysical，PixelDiagnostic为Unsupported。输入为已归一到TargetFrame的mm数据；不隐含单位/多frame映射，宿主先经coordinate Owner转换。PhysicalFrame的U/V/N单位正交、U×V=N，不能平均局部normal；方向变化使全部高度/积分/层面派生量重算。GeometryMeasures扩展旧§7已规划的椭圆尺寸/连续边界周长/面积等效直径；EllipseSize只带Ellipse，BoundaryPerimeter只带Boundaries，AreaEquivalentDiameter只带Domain，不把image ellipse拟合开放给v0.2。

| ContinuousMethod | 唯一Options / Payload / Report case |
|---|---|
| Sections | SectionOptions / SectionInput / SectionsResult |
| PathIntegral | PathOptions / PathInput / PathResult |
| AxisRelations | AxisOptions / AxisInput / AxesResult |
| Projection | ProjectionOptions / ProjectionInput / ProjectionResult |
| PlaneRelations | PlaneOptions / PlaneInput / PlanesResult |
| SupportedField | FieldOptions / FieldInput / FieldResult |
| GeometryMeasures | GeometryMeasureOptions / GeometryMeasureInput / GeometryMeasuresResult |

TopHeights/BottomHeights恰3项、顺序对应OriginalTriangle A/B/C。AffineTriangles允许上下三角场已共同分片，BottomHeights为0表示**显式**平面基底，不是缺失默认；Q路线BottomHeights必须Empty、Quadratic必填；其它路线Quadratic=null。Cells由上游按原有效单元及支持提供，不在metrology自动三角化/重建。WholeCellSupport、classification/boundary/reference等资格引用由reader核原Owner证据，不能传bool自行授予完整性。Fragments是已扣孔洞/排除域且合法三角分解的候选；Core重核父cell、全片支持、域归属、面积、无重叠、并集和来源，不靠三个顶点在mask内断言内部有效。未知洞穿过原cell使该原cell失效，只有上游有独立支持的重建cell可重新进入，裁小/细分不恢复资格。

MaterialWindow用于计算的Fragments.Class只能Material且域恰为F\Uh，B/Us不得带假0高片进入；GeometricHeight的Fragments.Class只能Geometric且域恰为GeometricKnownE。NonMaterial/UnknownMaterial枚举只作合法域分类标签，不是可积高度片。上下场来自不同原网格时共同cell的WholeCellSupport必须同时追溯两个原场单元来源；Sources不能只留“新三角”，不能跨层/孔洞后重新声明有支持。

AreaDomain是无需高度/参考的独立面积消费者路线：Cells.Empty、Q/UnknownBound=null、Fragments.OriginalCellId=null，MaterialWindow的片域为F（不扣Uh），GeometricHeight为已资格面积域GeometricKnownE，来源必须来自PlanarDomain.Decomposition/Boundary证据；不能为求面积强制加载无关高度资产。FieldOptions只允许AreaMoments=true/EquivalentMomentEllipse按需，其它Integral/PositiveCenter=false、CDF/p.Empty、Transform=Signed。DomainReport.Measure=AreaOnly，CompletedE为已计算面积片，KnownHeightArea=0、UnknownHeightArea为0（此Measure不适用）；完整性只看请求的面积边界/材料未知与已处理面积，不以缺高度Uh阻断已知面积中心。其余FieldModel的DomainReport.Measure=HeightField，必须有原CellId与完整高度支撑，沿下文D/E/U规则。

PlanarDomain显式支持断开组件/孔洞，Components内每个Polygon2沿§12.3单Boundary+Hole规范；Triangles是同一已扣洞域的无重叠三角分解，Decomposition由ROI Owner资格回执绑定。空域Components/Triangles均Empty（回执仍有身份）。Observed/Prediction/Target等不同域各有独立分解，不能用单外环/凸包表示不连续材料。Core核每三角正面积、无重叠、component内外及面积守恒；三角边图内部边反向配对，边界有序链与component rings在精确共线细分后相同，任何多余/少边拒绝。面积和边界双核防“面积相等但孔洞/域错位”；源分解不合格不能由积分器自动补三角。

PlanePatch.PermittedPredictionDomain可为空域，ObservedDomain与预测域分别记录，LocalFrame.Origin位于Plane，法向与Plane.Normal同向。Axis观察端部独立于拟合extents；端部缺失时投影/伸出缺量，不取拟合端点或焊料最高点。PlaneInput的PositionsUv为参考LocalFrame坐标，EvaluationDomain需真实完整边界才报整域范围；正常positions可有局部无效，不丢ID。Layer None时厚度/source/lower=null；其它对应必须厚度≥0/source/lower patch都非空，reader核局部平行/材料适用资格；它是模型推导，不能把不可见下层当实测接触。

Numeric长度/relative/angle规则同v0.2，MinimumArea/Volume>0，MinimumEigenGap≥0，MaximumCenterWidth>0；高度/面积/体积/概率包络容差有限≥0且概率容差≤1，零容差不承诺有限细分可达。各整数/字节/根/叶/深度/事件/query/运算上限正数，所有乘加先checked；MaximumDepth允许0表示只根片。无生产默认，Profile的每一门值来自显式Engineering fixture或获批用途，禁止用本节合成值写生产默认。FieldOptions至少请求一项；PositiveCenter仅AffineTriangles且bottom全0，Q/非平面bottom为Unsupported，不能套Kh公式。EquivalentMomentEllipse要求AreaMoments=true，派生轴明确是同矩等效，不是拟合长宽。

### 19.3 公开factory、reader、执行/关闭与版本

```csharp
public interface IContinuousLease : IAsyncDisposable {
    AssetRef Input { get; }
    ContinuousPayload Payload { get; }
    LeasePhase GetReleaseReceipt();
}
public interface IContinuousReader {
    ValueTask<ContinuousProfile> ReadProfileAsync(AssetRef profile,
        ExecutionBudget bootstrapBudget, CancellationToken cancellationToken);
    ValueTask<IContinuousLease> AcquireAsync(AssetRef input, AssetRef targetFrame,
        Scope scope, ExecutionBudget budget, CancellationToken cancellationToken);
}
public sealed record ContinuousSnapshot(OperationKey Key, Phase Phase,
    Outcome? PendingOutcome, ContinuousResult? Result, MetrologyError? Error);
public sealed record ContinuousCloseReceipt(bool Closed,
    ImmutableArray<ContinuousSnapshot> Pending, int PendingNotifications);
public interface IContinuousExecution {
    OperationKey Key { get; }
    ValueTask<ContinuousResult> GetResultAsync(CancellationToken waitCancellation);
    BackendReceipt GetReceipt();
    void RequestCancel();
    ValueTask<BackendReceipt> ReleaseAsync(CancellationToken waitCancellation);
}
public interface IContinuousBackend {
    string Version { get; }
    IContinuousExecution Start(ContinuousRequest request, ContinuousProfile profile,
        IContinuousLease input, Action<MetrologyEvent>? observer,
        CancellationToken cancellationToken);
}
public interface IContinuousMetrologyService : IAsyncDisposable {
    ImmutableArray<MetrologyError> Validate(ContinuousRequest? request);
    ValueTask<ContinuousResult> MeasureAsync(ContinuousRequest request,
        Action<MetrologyEvent>? observer, CancellationToken cancellationToken);
    ContinuousSnapshot GetOperation(OperationKey key);
    bool RequestCancel(OperationKey key);
    ValueTask<ContinuousCloseReceipt> CloseAsync(TimeSpan drainTimeout,
        CancellationToken waitCancellation);
}
// Core成员签名；省略实现体，非本轮可编译代码。
public static class ContinuousMeasurements {
    public static ImmutableArray<MetrologyError> Validate(ContinuousRequest? request,
        ContinuousProfile? profile, ContinuousPayload? payload);
    public static ContinuousResult Compute(ContinuousRequest request,
        ContinuousProfile profile, ContinuousPayload payload);
}
public static class ContinuousCanonical {
    public static string HashRequest(ContinuousRequest request);
    public static string HashProfile(ContinuousProfile profile);
    public static string HashInput(ContinuousPayload payload);
    public static string HashResult(ContinuousResult result);
}
public sealed class ContinuousCoreBackend : IContinuousBackend {
    public ContinuousCoreBackend();
}
// Runtime；同v0.2无窗口/Store/隐藏初始化。
public sealed class ContinuousMetrologyService : IContinuousMetrologyService {
    public ContinuousMetrologyService(IContinuousReader reader,
        IContinuousBackend backend, RuntimePolicy policy, ExecutionBudget bootstrapBudget);
}
public sealed class ContinuousCloseException : Exception {
    public ContinuousCloseException(ContinuousCloseReceipt receipt);
    public ContinuousCloseReceipt Receipt { get; }
}
```

Profile ContractVersion=`0.3`，MethodVersion精确`<ContinuousMethod>/1`；请求Method与profile一致。bootstrapBudget是构造时明确的Profile读上限，Profile.Budget不能放大它的托管字节/执行/排空上限，其它工作量门由Profile自身声明。Profile读取与Acquire也纳原key在途账本；reader需验证canonical hash/target frame/资格闭包，失败用MetrologyPortException。Core.Compute只允许Engineering；CalibratedPhysical由Runtime/reader资格后端复用同一内部kernel，不能绕端口自批。请求hash只覆盖引用，reader再次核Profile/Input实际内容与ref相符；Core.Compute入口也核HashProfile/Input与ref，不能从相同key下偷偷替换payload。

结果Report一一对应Method，业务失败保原错误；每个区间Lower≤Upper且有限，区间代表**存储模型数值包络**，不是物理uncertainty/置信区间。输出没有合法区间时相应report为null/缺项并给错误，不以[0,0]代替未知。Measured/Valid要求请求域完整性及数值门满足；KnownPartDiagnostic可返回Partial/Indeterminate与明确E/U，完整域字段不得偷换。全B材料量0合法但CDF/中心无定义；A(E)=0且材料高度未知不是实测0。预算停止/容差未达只给诊断界和NumericStatus，不能给Measured。FieldOptions.Transform仅控制CDF/Quantiles的随机变量，Integral仍明确保原signed/positive/negative/absolute四量，Moments为相同E面积矩、PositiveCenter为原h正部，不能因选PositiveOnSameDomain静默改signed或材料域。

前置结构无效→MetrologyPortException/InvalidRequest且零reader；接纳后错hash/InputHashMismatch、错frame/CoordinateMismatch、资格缺/Unqualified均保原key；Unsupported组合→Unsupported/Invalid；原支持缺/域未知→Unevaluated或显式Partial/Indeterminate；numeric BudgetStopped→ResourceLimited/BudgetExceeded，ToleranceNotMet/OutOfRange→Unevaluated/InsufficientSupport，ArithmeticConflict→Failed/BackendFailure，取消/超时沿原PendingOutcome且释放后终态。Error Arguments沿§11.3的固定键，stage字段用Continuous:method:phase；NumericCertificate.ReasonKey使用固定`numeric.*`键，不载任意隐含参数。GeometryMeasures数值未达也用同Error分类，不能无NumericCertificate就默认为成功。

身份、接纳前total校验、重复/冲突、队列截止、取消、退出/释放回执、晚Acquire/Profile、观察者及Close/Dispose完全沿§11.3/§14，替换result/snapshot/receipt类型即可；不另造状态机。ContinuousCloseException只封装对应receipt；尚在途的Dispose不得重复调用。Runtime唯一生成事件和终态，backend释放仅私有托管临时工作，不dispose借来的input/reader；Close不dispose注入端口。Host按§16.3在factory前预留Root并持request/profile/input/source/端口和全部原Task；C1–4计算含BigInteger不可抢占单次操作，Token或wall超时不能伪退出。

canonical沿§15字段顺序/union tag规则；ContinuousPayload、ContinuousOptions、ContinuousReport分别按§19.2各自派生record的声明顺序从1起写int32 little-endian tag，三套tag独立，不能以Method enum序号代替或按类型名排序。Magic域改为`Asun.Metrology.Continuous.Request/0.3`、`Profile/0.3`、`Input/0.3`、`Result/0.3`（四者均完整前缀Asun.Metrology.Continuous.），hash排除ResultFingerprint自身；所有证据引用、Profile参数、TargetFrame/Scope/Key均入hash。Evidence按ordinal Id/Revision/Sha排序去重保来源；Report数组保请求顺序和稳定片ID，不纳事件时间。模块不会创建/激活reference/calibration，也不写Store；发布0.3包要求Contracts/Core/Runtime同闭包，v0.2调用保持旧入口，未知版本拒绝而不best-effort解析。

### 19.3.1 v0.3独立canonical向量（规格oracle，本轮内存复算）

本向量以BCL以外的独立逐字段encoder按本节声明和§15规则，在内存用Python标准库struct/uuid/hashlib重建；未调用ContinuousCanonical、未运行产品/上游/历史研究脚本，未创建脚本、报告或测试文件。正式Contracts测试须把以下固定bytes/hash作为预期，不能用受测encoder生成预期。Profile/TargetFrame的SHA仅是合成引用字段，未提供其内容，向量只证明编码而非资产资格。

完整Input是 `new ProjectionInput(new V3(0,0,1), ImmutableArray.Create(new ProjectionPair("pair:1",new P3(1,2,3),new P3(4,6,3))))`；全部字段如表，没有可空字段、record名、Method字段或隐藏frame。数值定义应给距离5mm/方向投影0mm。Payload tag=4而Method.Projection=3，两者不能混用。HashInput总是绑定固定`Asun.Metrology.Continuous.Input/0.3`域；payload没有ContractVersion不等于无版本，不能从外部Profile推断或自动改Magic。

| 字段（按此顺序拼接） | bytes | 完整字段 hex |
|---|---:|---|
| Magic | 39 | `230000004173756e2e4d6574726f6c6f67792e436f6e74696e756f75732e496e7075742f302e33` |
| ProjectionInput tag | 4 | `04000000` |
| Direction.X | 8 | `0000000000000000` |
| Direction.Y | 8 | `0000000000000000` |
| Direction.Z | 8 | `000000000000f03f` |
| Pairs.Count | 4 | `01000000` |
| Pairs[0].Id | 10 | `06000000706169723a31` |
| From.X | 8 | `000000000000f03f` |
| From.Y | 8 | `0000000000000040` |
| From.Z | 8 | `0000000000000840` |
| To.X | 8 | `0000000000001040` |
| To.Y | 8 | `0000000000001840` |
| To.Z | 8 | `0000000000000840` |

完整Input为**129 bytes**，SHA-256 **`e3d9b1cb688f2583a44804622126664fd25ecb9af72c72d6c0f2cee9b45308c4`**。

完整Request为Key=(Guid `00112233-4455-6677-8899-aabbccddeeff`, RequestRevision=7)，Scope=Engineering(0)，Profile=(Id=`profile:projection`, Revision=2UL, Sha256=64个字符`1`)，Input=(Id=`input:projection`, Revision=3UL, Sha256=上述完整Input hash)，TargetFrame=(Id=`frame:mm`, Revision=4UL, Sha256=64个字符`2`)，Method=Projection(3)。不含Profile/Input正文、不含可空tag，SHA字符串编码为64个ASCII字符而非32个原始hash字节；Guid用网络字节顺序而非Guid.ToByteArray默认次序。

| 字段（按此顺序拼接） | bytes | 完整字段 hex |
|---|---:|---|
| Magic | 41 | `250000004173756e2e4d6574726f6c6f67792e436f6e74696e756f75732e526571756573742f302e33` |
| Key.OperationId | 16 | `00112233445566778899aabbccddeeff` |
| Key.RequestRevision | 4 | `07000000` |
| Scope.Engineering | 4 | `00000000` |
| Profile.Id | 22 | `1200000070726f66696c653a70726f6a656374696f6e` |
| Profile.Revision | 8 | `0200000000000000` |
| Profile.Sha256 | 68 | `4000000031313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131` |
| Input.Id | 20 | `10000000696e7075743a70726f6a656374696f6e` |
| Input.Revision | 8 | `0300000000000000` |
| Input.Sha256 | 68 | `4000000065336439623163623638386632353833613434383034363232313236363634666432356563623961663732633732643663306632636565396234353330386334` |
| TargetFrame.Id | 12 | `080000006672616d653a6d6d` |
| TargetFrame.Revision | 8 | `0400000000000000` |
| TargetFrame.Sha256 | 68 | `4000000032323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232` |
| Method.Projection | 4 | `03000000` |

完整Request为**351 bytes**，SHA-256 **`4bf03ff3754aa0b4701ba64fdeaefd36e808eec4b32616f61a4c577163bb5ee9`**。

| 编码反例/合法变体 | 固定断言 |
|---|---|
| 将ProjectionInput tag写成Method值3 | 与完整129-byte向量不等；3在Payload联合代表AxisInput，不能接着按Projection字段解析成功；未知tag0/8也拒绝 |
| 只改Direction为(1,0,0)，其它Input字段不变 | 合法129 bytes，hash `6f1242f85216f222bb222875596ee789adc38ec509e20c3906e75206880714d0`；距离仍5、方向投影变3；Request.Input.Sha须同步改，新request hash不能沿用旧值 |
| 只改To.Z为4，其它Input字段不变 | 合法129 bytes，hash `e258b206dbc53e6efa35652cb919d9f5b09a50940c67caa9984dd7dcf30795c8`；量值/hash须变，不能把合法变体归旧内容 |
| Profile.ContractVersion为0.2或未知值 | 服务接纳前/读取后按§19.3 VersionMismatch，不能用v0.3入口执行旧版本；HashInput仍固定0.3、不跟随该Profile改域 |
| Magic尾字符0.3改0.2（长度不变） | 旧域的字节/hash必须不同；不是本入口合法编码，不能best-effort或重算覆盖旧身份 |
| Pair.Id含非NFC `pair:e\u0301`，对照NFC `pair:\u00e9` | 前者HashInput抛ArgumentException/Validate分类InvalidRequest，不先Normalize后得到后者hash；NFC合法字符串按原UTF-8字节编码 |


### 19.4 连续截面、沿程、轴与有限层面计算（C1）

GeometryMeasures：EllipseSize要求a≥b>0，输出MajorAxis=2a/MinorAxis=2b/理想Area=πab/EquivalentAreaDiameter=2sqrt(ab)，不输出(a+b)或椭圆拟合误差；BoundaryPerimeter要求每Contour闭合/无自交且来源证明是完整边界，逐连续线段长度Σhypot计mm，孔边显式每个Contour分别计入，不把raster周长/拟合曲线弧长混同该折线周长。AreaEquivalentDiameter由Domain连续面积A给2sqrt(A/π)。sqrt用§19.8有理界二分，π使用Machin公式π=16atan(1/5)-4atan(1/239)，atan有限交错级数与下一项余项给有理上下界，项数/bit/运算预算后停止；最终interval达MaximumArea/HeightWidth才有效，预算不足NumericStatus映射ResourceLimited。Ellipse Phi仅方向来源、不改这些尺寸，近圆不授方向；本case不偷偷新增ellipse image fitting或真实最小开口测法。

SectionInput的每query为q(t)=Origin+t·Direction，方向单位化，有限MinT<MaxT，线在Frame平面内。OccupiedDomain合法Boundary/Hole多边形；借已有ROI合法拓扑/公开HALCON `intersection_line_contour_xld`取得所有交点后按t排序、裁finite区间、保重叠标记与原edge归并关系。Core对polygon用逐边解析直线相交的同等定义；平行/共线与顶点触碰分支显式，不能从轮廓顺序猜第1/2点占用。相邻交点间取严格内部测试点按多边形含孔内外判定占用，非实测ROI截断边不能补边；重叠/切触无法证明两边为Indeterminate。返回每物理占用区间width=tR-tL、midpointOffset=(tR+tL)/2和两端点；Selector.All或Unique，IntervalId显式取该稳定区间；NearestAnchor本case Unsupported（未提供anchor）。查询origin是工艺路径点时宿主才解释为偏移，公共模块不取最长/最接近期望宽度区间。

PathInput.Nodes保原路径顺序，s严格递增且点间真实弧长定义由来源资格保证；Intervals恰覆盖相邻节点ID，whole interval support不能为空才可积分。两个有限ValueMm及整间隔支持成立时I=Δs(fL+fR)/2，长度mm、I mm²；缺样/缺support拆段，孤立点无正长度积分。ClosedPath只能用显式末节点表示回到起点（不同ID、s为全周长），不隐式补末→首/重复算闭环；未闭而ClosedPath=true拒绝。高度剖面采样由surface reader按原三角重心坐标取值，图像adapter选`get_grayval_interpolated`时先核边界/ROI/有效mask全邻域（bilinear4/bicubic16），算子忽略domain，禁止reduce_domain代核；显示平滑/LOD不参与数值。当前合同只消费已带support的原始PathNode，不让Core临时填洞或新增采样算法。

Projection分别给||To-From||与dot(To-From,direction)，两者不互填。Axis：datum单位normal n、d=-n·Origin，轴P+t u，在datum offset h截面t=(h-n·P-d)/(n·u)；先核abs(n·u)≥MinimumAbsNormalDot及t∈[MinT,MaxT]，再核section point在有限datum支持。端点T存在且到轴径向偏差≤门才给H=n·T+d、L=(T-Q)·u；tilt=atan2(||u×n||,abs(u·n))，TangentU/V=atan2(u·datum.U/V,abs(u·n))，轴orientation须来自Qualification，不能用显示朝向赋符号。Pairs按明确ID对在同一截面取Qi/Qj距，不最近邻重排；缺一轴保原PairId无值。ValidSubsetHeightRange只对有效端点求max-min并标有效子集，不称最小区域共面。

Plane：参考基O/U/V/N，target单位m、b=-m·target.Origin，c=m·N，a1=m·U、a2=m·V、b0=m·O+b；h=-(a1u+a2v+b0)/c。先核abs(c)≥MinimumAbsNormalDot（(0,1]），不clamp/换normal；正负c保公式。每位置分别核参考点与target交点ObservedDomain/PermittedPredictionDomain，批准预测标ModelPrediction=true，缺支持保该位置无值。整EvaluationDomain全部合格才按仿射h边界顶点给模型range；非凸/孔洞真实边界不能用凸包补。PlaneAngle按Unsigned或Unoriented，Directed2D拒绝；翻target全部平面系数不改几何高度/无向角。

局部平行层厚t≥0、LowerLayer资格与normal m从下向上证明后：SameReferenceRay给hLower=hTop-t/c，沿同N射线求LowerPoint；TargetNormalOffset给PLower=PTop-t m，参考高度降低t c且U/V坐标变动-t(a1,a2)。每个下层点重新核LowerLayer有限支持/厚度适用性；不见下表面时ModelPrediction保持true。c<0仍signed，产品要求下层更低必须由产品验证定向，不能abs。一般曲面法向、多交点、倒悬、光程→膜厚转换不属于此已规划有限平面模型，明确Unsupported，不伪装通用厚度。

### 19.5 D/F/B/Us/Uh、共同分片、线性积分和矩（C2）

GeometricHeight目的只积GeometricKnownE真实高度域（包括分类B处真实可用高度），不把B当0；此case必须D=GeometricKnownE∪GeometricUnknownU互斥，F/B/Us/Uh均空，不需要材料分类资格（Classification引用几何用途证明）。MaterialWindow目的材料F高度域E_F与已证非材料B分开，必须D=F∪B∪Us互不重叠、Uh⊆F，E=F\Uh，GeometricKnownE/U均空。B贡献材料逻辑0但不进入面积中心/高度CDF/体积矩，Unknown不能冒B。边界/分类未知时不自报精确分母。Fragments按Purpose实际覆盖域选，完整性不能靠面积覆盖率升格。D面积0拒绝；材料全B可报完整材料0但中心/分位无定义；面积可用不代表高度可用。

DomainReport.Target/Material/B/Us面积来自原冻结域；KnownHeightArea为本次**完整处理**E面积，UnknownHeightArea为原Uh加本次未处理F（几何case为原GeometricUnknownU加未处理已知片），CompletedE/RemainingU对应这些三角分解。MaterialWindow完整性判Us/Uh均空且全部F完成，B可计材料窗口完整但不增高度分母；GeometricHeight完整性判无UnknownU且全部几何片完成。部分Cdf/Quantile只能使用一个固定已处理E并明确DomainReport，取消途中某次归约不以半和/全分母返回；FullTarget缺任一范围为Unevaluated/Indeterminate、诊断Report可留，KnownPartDiagnostic为Partial。Parent Q四分中断时已保父粗界算该原域仍在E（Numeric不达门），根尚未初始化的域才留RemainingU。

整个OriginalTriangle插值支持先成立，再Q=cell∩D∩QualifiedDomain∩参考适用域扣排除/真孔；不同上下网格在surface/ROI适配处先共同分片，禁止按数组位置减或三维最近点代沿N对应。公开ROI几何端口负责合法布尔/含孔三角分解，宿主reader将QualifiedFragments传入；metrology重核每fragment在原cell内的重心坐标（不夹λ掩错）、无交叠、来源、整体域并集和预算。非凸/带洞不能扇形填外环；重复FOV须Owner提前批准去重/分配，无法证明互斥为Unsupported。准备片数/候选对/clip顶点/输出来源受Numeric与ExecutionBudget共同上限；超过拒绝或标已处理E/剩余U，不静默删小片。

新点q以原cell重心λ求top/bottom，h=top-bottom。对每子三角面积A=abs(cross2)/2，I_signed=AΣh_i/3；先按h=0直线裁正/负子三角再积Vplus/Vminus，signed=plus-minus、absolute=plus+minus，不能截零顶点或abs(signed)。这是存储分片线性模型精确积分、面积为U/V投影mm²，不用上表面3D面积；bilinear任意裁切不是同模型，FieldModel不存在该case，Unsupported而不暗换对角线。规则网格只能由surface Owner按冻结对角/中心边界提供cells，支持止外圈中心不能自动多半像素。

连续三角面积矩：Su=Σu_i、Sv=Σv_i；M00=A，M10=A Su/3，M01=A Sv/3，M20=A(Su²+Σu_i²)/12，M02对称，M11=A(Su Sv+Σu_i v_i)/12。mm²/mm³/mm⁴分别命名；同域M00作分母，中心M10/M00、M01/M00，中心协方差=(M20,M11,M02)/M00-中心外积。生产采用局部平移/稳定正权合并：d=C2-C1，C=C1+(A2/A)d，S=S1+S2+(A1/A)A2 ddᵀ；孔洞先扣片，不把负权洞套正权合并。Region点质量矩保v0.2定义；连续pixel面积单元若用本case必须提供真实矩形三角片，含单元内diag(su²,sv²)/12，不能压中心后声称连续矩。

对Σ=[[a,b],[b,c]]，gap=hypot(a-c,2b)，variance=(a+c±gap)/2；仅当有限/PSD及gap>MinimumEigenGap并且确定数值界可辨才给principalAngle=0.5atan2(2b,a-c) mod π。负特征值不能abs，只有确定舍入界内0可归零并保原因。等轴无angle；窄正面积条按面积/误差/gap检查，不统用condition数拒绝。EquivalentMomentEllipse显式请求才给全轴4sqrt(variance)，不是真实边界尺寸。center允许落孔/材料外，不自动判错。

PositiveVolumeCenter仅平面bottom=0：正部子三角h_i≥0，H=Σh_i，V=A H/3，Ju=A(Su H+Σu_i h_i)/12，Jv对称，Khh=A(H²+Σh_i²)/12；体积mm³、混合矩mm⁴，Cuv=(Ju,Jv)/V，Ch=Khh/(2V)。分母确定下界>MinimumVolume且中心输出区间宽≤MaximumCenterWidth才给中心；零材料/近零/有缺域不给完整中心，部分中心标E诊断而非整体上下界。signed抵消不计算物理质心，非平面/Q底不能套Ch；一般体积惯性张量未在旧规划开放，本版Unsupported。

条件整体界使用本次CompletedE，剩余固定高度域R在MaterialWindow为`F∖CompletedE`（含原Uh与尚未处理的已知片），在GeometricHeight为`D∖CompletedE`（含原GeometricUnknownU与尚未处理的已知片）。R不含可选材料Us；DomainReport.UnknownHeightArea对应R，RemainingU另保Us的输入三角分解，须结合Purpose及冻结分类解释，不能将Us计成已确定材料高度面积。AreaOnly不使用这些高度公式，沿§19.2的不适用0与面积完整性规则。

未知高度若整个R有Proof的[hLo,hHi]确定界，固定域条件whole signed=[VE.lower+hLo A(R), VE.upper+hHi A(R)]（面积/VE有界则完整区间运算）。MaterialWindow有可选Us时，Proof还须覆盖Us的可能材料高度，再加`[min(0,hLo) A(Us), max(0,hHi) A(Us)]`，保留其中可无材料的可能性；不能强制把Us全当材料积正下界。Proof只覆盖原Uh时不能自动扩到未处理已知片；可核完整存储模型界后合成更宽的明确包络，否则ConditionalWholeSigned=null。无Proof不给未知高度域的有界总体积。物理固定域top/ref误差ε的积分界A(E)ε与存储数值界分别保Evidence，不以RMS/样本min-max冒未知域界、共同reference偏差不除sqrtN。参数变化/材料分类/支持变化须重算，不覆盖旧attempt。

### 19.6 连续面积CDF、原子与左逆（C3）

固定非空E及投影面积权：K(t)=∫E 1[h≤t]dA，C=K/A_E，0<p≤1取inf{t:C≥p}，p0=ess inf、p1=ess sup。不是节点percentile/gray histogram/体积权。负高保signed；PositiveOnSameDomain将h变max(h,0)，保同分母与0原子，不等于仅h>0子域条件分位（未开放该case）。

每仿射三角排序顶高a≤b≤c；非恒片t≤a时f=0、t≥c时1，中间：a<b<c下a<t≤b为((t-a)/(b-a))((t-a)/(c-a))，b<t<c为1-((c-t)/(c-a))((c-t)/(c-b))；a=b<c为1-((c-t)/(c-a))²，a<b=c为((t-a)/(c-a))²；a=b=c=k时t<k为0，否则1。K_T=A f；两个同高顶点仅零面积边非原子，三同高才面积A原子。相等按精确存储模型，不用epsilon合并常值。Positive transform的CDF t<0为0、t≥0复用signed CDF；0原子包含原h≤0的面积，Atoms记录其来源。

事件是所有片顶高，≤3N（裁零正部同域按signed事件+0）；精确排序/合并相等。求第一个r使K(r)≥p A_E，前事件l满足严格<；K(r-)不含r常值原子，若K(r-)<target≤K(r)分位=r，等号不笼统判跳点。连续区间二分保持K(lo)<target≤K(hi)，相等向左缩hi；停止用height interval最终向外舍入宽≤MaximumHeightWidth，不用CDF残差小，否则空高度带会错选中点。返回KnownHeightMm区间，不另假造精确代表点。p0/1走实际模型极值；p极近1用精确质量/上尾，不能舍入C=1抢先max。

未知域CDF以本次CompletedE与§19.5的剩余固定域R计算：固定材料F，bound=[K_E/A_F,(K_E+A_R)/A_F]；GeometricHeight同式以A_D替代A_F。原Uh为空但已知片未处理时A_R仍非0，不能把诊断部分当完整分布。有可选Us时粗保守界=[K_E/(A_F+A_Us),(K_E+A_R+A_Us)/(A_F+A_Us)]，B绝不作为0高质量。ConditionalWholeProbability仅域面积/边界已知且分母确定正时返回；AF=0且Us非空包含无材料，不返回无条件整体CDF或分位。Quantile条件界：固定R有独立共同height bound时把其质量放lo/hi分别反演；Proof须覆盖本次整个R，不能仅凭原Uh证明包住未处理片。有可选Us时只有AF>0且UnknownBound.CoversKnownHeightDomain并核整个E模型及R/Us可能材料高度也在该界内，才把R+Us全加入lo/hi作包络；E在界外此简单构造不成立，返回conditional=null/UnsupportedDomain，Known部分仍可读。该条件包络不是实测whole或置信区间。

### 19.7 仿射顶部减Q、严格正负与CDF/分位包络（C4）

Q固定u=(x-xc)/Lx、v=(y-yc)/Ly，f=zc+Lz(c0+c1u+c2v+c3u²+c4uv+c5v²)，Coefficients恰6项、尺度正有限；top来自原仿射cell，裁片新顶点重心求top，bottom始终求原Q，不能连底三点改平面。以归一u/v六面积矩M00/M10/M01/M20/M11/M02（均mm²）计算signed：I=AΣ(top_i-zc)/3-Lz(c0M00+c1M10+c2M01+c3M20+c4M11+c5M02)。不能再乘LxLy，物理面积A已计尺度；Q的适用域/全片误差/物理底层资格由reference Owner，不以rank合格授予洞内底面。

二阶h=top-Q在每T构造Bernstein六系数bii=h(Pi)，bij=2h((Pi+Pj)/2)-(h(Pi)+h(Pj))/2。h=Σbiiλi²+2Σbijλiλj；min六b≤h≤max六b，三顶点同号不证明全片。ℓ=Σbiiλi，dij=bij-(bii+bjj)/2，e-=(2/3)min(0,d01,d02,d12)，e+=(2/3)max(0,d01,d02,d12)，g-=ℓ+e-≤h≤ℓ+e+=g+，δ=e+-e-。

固定四分子片(P0,M01,M02)/(M01,P1,M12)/(M02,M12,P2)/(M01,M12,M02)，面积A/4，系数b'ij=viᵀBvj，δchild=δparent/4；原Q与材料/支持不变。父片保留至四子片全部完成并核面积/预算后原子替换，取消/预算中断保父粗界，不能丢父域。积分优先当前Aδ贡献最大叶，ties按根ID/子路径ordinal；全部根初始化才有whole E界，未初始化仅CompletedE诊断。

Φ(g)=∫max(g,0)dA复用仿射裁零，positive界[Φ(g-),Φ(g+)]，negative界[Φ(-g+),Φ(-g-)]；全局累计宽度≤ΣAδ，用全局volume容差验收而非每叶各一份。标量Φ也可按a≤b≤c、I=A(a+b+c)/3：a≥0为I，c≤0为0，a<0≤b<c为I+A(-a)³/[3(b-a)(c-a)]，a≤b<0<c为Ac³/[3(c-a)(c-b)]；分支后除法，无零分母，不截零顶点。signed解析恒等plus-minus可收紧区间，不独立取中点声称恒等。

模型极值：λ=(1-s-t,s,t)，h=a s²+b st+c t²+d s+e t+f，f=b00,d=2(b01-b00),e=2(b02-b00),a=b00-2b01+b11,b=2(b00-b01-b02+b12),c=b00-2b02+b22。枚举三顶点、每边二次导数根r=-B/(2A)∈(0,1)、内部驻点[[2a,b],[b,2c]][s,t]=[-d,-e]且s,t≥0/s+t≤1；det=0时边界枚举已含驻线极值，不除零猜根。精确min/max给p0/1及非负证书，(x-1/3)²内部零线不无限细分。数值非负仍非材料资格。

同叶分区CDF界ΣK_g+(t)≤K_h(t)≤ΣK_g-(t)，同A_E归一，以最终probability/area width验收；δ小不在无密度下界时保证CDF误差。真实原子只在原六系数精确相同时，g界的人工常值不是原场原子。对0<p<1分别反演g-/g+，其区间[l-,u-]/[l+,u+]给原q∈[l-,u+]；若δ≤δtarget且两反演宽≤η，则内部宽≤δ+2η，输出向外舍入仍须实际验宽。正部同域q=max(signed q,0)；条件正域/q中心/任意曲线材料边界不由本Q扩展自动开放。

### 19.8 数值后端、预算失败和真实验收门

C2–4为存储IEEE有限double模型的严格有限归约：拆位转BigInteger有理数（分母正、约分、零规范0/1），不引入Python/NumPy/SciPy/Math.NET运行依赖。加减乘除/比较都先预估位长、操作数和bytes再分配；加法分子上界max(Bn1+Bd2,Bn2+Bd1)+1、分母Bd1+Bd2，乘/交叉比较按位长相加，除先核分子非0；GCD约分不作为事前内存保证。MaximumIntegerBits/Operations/ManagedBytes任一过门停止，保原叶与最后完整包络；单次BigInteger不可抢占，真实退出才排空。

输入几何布尔/分解在ROI adapter，C2–4只消费QualifiedFragments并精确核存储三角内插/无交叠/域关系；没有正式公共适配签名的部分只阻断该adapter，不让Core暗造几何引擎。HALCON有符号volume的abs累计、Region离散矩/gray histogram都不提供本定义的严格支持/Q包络；它们仍用于v0.2适用路线及公开几何检查，本节具名归约是已规划能力缺口，不断言HALCON所有算子均无相关能力。`get_grayval_interpolated`等官方行为只按26.05本地页面适配。

对已三角分解域的核对使用有限解析三角相交：统一CCW，逐条对方边的有向半平面Sutherland–Hodgman裁凸多边形（边界含等号），交边参数用exact cross比求、平行同侧保留/异侧清空；输出最多6顶点（共线重复精确合并），鞋带面积给重叠。只有共享边/点的零面积接触不重复计面积；候选bbox粗筛后所有潜在对逐一计MaxPairChecks，无法完成则BudgetStopped。子域关系以intersection面积等于自身并结合原边图资格核，D/F/B/Us/E差集无需在Core再生成任意布尔：RemainingU直接由输入已资格的Us/Uh分解及尚未处理Fragments组成，按Purpose保分类解释；几何目的则reader需提供其实际known/unknown同分解，不把B漏计。需要产生新含孔分解仍走上游ROI Owner，不让Core悄悄依赖未定义端口。

有理值转double区间：先取候选double（允许有界binary exponent算法），再将该double拆回exact rational比较；下端用BitDecrement直到≤exact，上端BitIncrement直到≥exact，每次计操作预算；不能形成有限双端则OutOfRange，不随意加epsilon。所有面积/积分/CDF比较精确，分位高度二分也用有理中点与严格左/非严格右条件；回传最后向外区间宽度不满足Profile为ToleranceNotMet。中心比值先证明分母下界>MinimumArea/Volume，再区间除，若宽超MaximumCenterWidth缺center并标数值未达。sqrt/atan2特征方向不从double值伪出严格证书：精确gap²和PSD判定，variance根用有理有界二分；angle/等效轴最终double以已声明角/长度容差及独立解析Oracle验证，门不足保缺angle/axis，不影响已证明的矩。ArithmeticConflict（空交集/守恒失败）是实现失败，不取中点修复。

根/叶/事件≤Numeric上限；分位预估每根δ0/4^k≤目标height预算，Σ4^k及暂存先checked，零容差不承诺收敛；query与inverse步数全部计费。CDF一次必须完成同一E归约，不能半和/全分母；取消保最后**完整**CDF/叶分区诊断，未完成query无值。clip/ref资格/管理资源/native峰值沿§16.1；本节纯有理数不需要HALCON native包络，但实际ROI/surface/HALCON adapter仍受原native门。物理误差另有Evidence；RMS、网格加密差和数值区间不能冒MSA/uncertainty。

### 19.9 无UI样例、反例与唯一测试/Benchmark落点

两个Host除v0.2 5mm例，还直接注入IContinuousReader/ContinuousCoreBackend调用v0.3：factory前Reserve Root→冻结profile/input并以ContinuousCanonical算hash→Validate→Measure原Task有界等待→消费Report/E/U→独立Close/Dispose嵌套finally→Closed/lease回执确认才释放Root。接口无隐藏初始化；fixture Geometry/原Cell/Fragments在HostTests内构造，真实输入由公开ROI/surface/reference适配转换。连续服务需要同一Root字段换成ContinuousResult/ContinuousCloseReceipt，§16.3所有late/fault case必须对两服务各跑，不能仅证明v0.2。

最小Core调用是`ContinuousMeasurements.Compute(request, profile, new FieldInput(field))`；三者完整字段由§19.2及下表一个fixture逐项构造，不以匿名字典/脚本定义缺失内容。正常全线性fixture：Frame O=(0,0,0),U=X,V=Y,N=Z；MaterialWindow目的D=F为单位直角三角、B/Us/Uh/GeometricKnownE/GeometricUnknownU为空；一个Cell 原三角(0,0),(1,0),(0,1)，Top=[0,0,1]、Bottom=[0,0,0]，QualifiedDomain=D，唯一Fragment同三角Material/原CellId及同来源，Q/UnknownBound=null，profile选SupportedField/1、AffineTriangles、FullTarget、Signed、Integral/AreaMoments/PositiveVolumeCenter=true、EquivalentMomentEllipse=false，CdfHeights=[0.5]、Probabilities=[0,0.75,1]。Qualification refs是Engineering fixture内容身份，生产reader必须核真实Owner。Numeric/ExecutionBudget每门在fixture显式赋值（例如高度/面积/体积/center宽1e-8、relative/angle1e-9、min area/volume1e-12、gap1e-10、bits8192、operations1e7、roots16/leaves4096/depth8/events12288/query16/inverse128/clip vertices4096/fragments4096，managed16MiB/native1byte、case execution≤6s/drain≤2s，仅harness，无客户意义）；这些合法值不能保证所有大样本通过。

对应完整类型构造如下，**目标样例未编译**。使用§16.2的using/BCL及FixtureRef函数；在已Reserve的Root.CaseTask业务try内执行，Compute原Task也由Root持有，不在Main根Owner以外无界执行。两个真实端口fixture把同request/profile/input注入IContinuousReader，再用§19.3服务调用与§16.3清理；本段直接验证纯Core，不伪装reader资格。

```csharp
var proof = FixtureRef("continuous:engineering-support");
var frame3 = new PhysicalFrame(new P3(0,0,0), new V3(1,0,0),
    new V3(0,1,0), new V3(0,0,1), FixtureRef("continuous:mm-frame"));
var triangle = new Triangle2(new P2(0,0), new P2(1,0), new P2(0,1));
var polygon = new Polygon2(ImmutableArray.Create(new Ring2("outer", Role.Boundary,
    ImmutableArray.Create(triangle.A, triangle.B, triangle.C))));
var domain = new PlanarDomain(ImmutableArray.Create(polygon),
    ImmutableArray.Create(triangle), proof);
var empty = new PlanarDomain(ImmutableArray<Polygon2>.Empty,
    ImmutableArray<Triangle2>.Empty, proof);
var partition = new DomainPartition(domain, domain, empty, empty, empty,
    empty, empty, proof, proof);
var sources3 = ImmutableArray.Create(proof);
var cell = new SurfaceCell("cell:0", triangle, ImmutableArray.Create(0d,0d,1d),
    ImmutableArray.Create(0d,0d,0d), domain, proof, sources3);
var fragment = new QualifiedFragment("fragment:0", "cell:0", triangle,
    DomainClass.Material, sources3);
var field3 = new SupportedField(frame3, DomainPurpose.MaterialWindow,
    FieldModel.AffineTriangles, partition, ImmutableArray.Create(cell),
    ImmutableArray.Create(fragment), null, null);
ContinuousPayload input3 = new FieldInput(field3);
var numeric3 = new ContinuousNumericPolicy(1e-9,1e-9,1e-9,
    1e-8,1e-8,1e-8,1e-8,1e-12,1e-12,1e-10,1e-8,
    8192,10_000_000,16,4096,8,12288,16,128,4096,4096);
var budget3 = new ExecutionBudget(16,64,16,64,16*1024*1024,1,1,
    TimeSpan.FromSeconds(6), TimeSpan.FromSeconds(2));
var options3 = new FieldOptions(CoverageRequirement.FullTarget, HeightTransform.Signed,
    true,true,true,false,ImmutableArray.Create(.5),ImmutableArray.Create(0d,.75,1d));
var profile3 = new ContinuousProfile("0.3", "SupportedField/1",
    ContinuousMethod.SupportedField, options3, numeric3, budget3);
var profileRef3 = new AssetRef("continuous:triangle-profile",1,
    ContinuousCanonical.HashProfile(profile3));
var inputRef3 = new AssetRef("continuous:triangle-input",1,
    ContinuousCanonical.HashInput(input3));
var request3 = new ContinuousRequest(new OperationKey(
    Guid.Parse("7046416a-0fbe-4bd1-b85e-6b1cfb8d70c1"),1), Scope.Engineering,
    profileRef3,inputRef3,frame3.Frame,ContinuousMethod.SupportedField);
if (!ContinuousMeasurements.Validate(request3,profile3,input3).IsEmpty)
    throw new InvalidOperationException("Continuous:fixture-invalid");
var computed3 = ContinuousMeasurements.Compute(request3,profile3,input3);
if (computed3.Report is not FieldResult fr || computed3.Outcome != Outcome.Measured)
    throw new InvalidOperationException("Continuous:fixture-outcome");
static bool Contains(Interval i, double x) => i.Lower <= x && x <= i.Upper;
if (fr.Value.Integral is null || !Contains(fr.Value.Integral.SignedMm3,1d/6) ||
    fr.Value.PositiveCenter?.U is not Interval cu || !Contains(cu,.25) ||
    fr.Value.PositiveCenter?.V is not Interval cv || !Contains(cv,.5) ||
    fr.Value.Quantiles.Length != 3 || !Contains(fr.Value.Quantiles[1].KnownHeightMm,.5))
    throw new InvalidOperationException("Continuous:triangle-defined-quantities");
```

包含性样例只说明字段/数值落点，正式Core.Tests必须用精确有理真值1/6、1/4等Oracle比较向外端点、最终宽度≤Numeric门、E面积/父cell/输出版本/hash及所有期望量，不能把double(1/6)落区间视为全部正确。完整两个service Host的reader映射只实现ReadProfileAsync/AcquireAsync两个公开方法、按ref返回上述冻结值/IContinuousLease（同v0.2 fixture lease的单飞Dispose/ReleaseReceipt），不依赖工作台Shell。前置Bootstrap预算显式用budget3，RuntimePolicy沿§16.2；Scope.Engineering不核物理证书。真实生产reader仍有Owner资格门。

| 稳定ID / 覆盖 | 输入与判定（解析合成，未执行产品） |
|---|---|
| C1:section-offset / multirun | t=-.4,+.6 →width1/offset+.1；两个占用区间各返回，不取最远宽；共线/缺边/ROI截断Indeterminate |
| C1:geometry-defined | 椭圆a2/b1→轴4/2、area2π、equiv diameter2sqrt2；单位方形连续闭边perimeter4；同面积等效直径不是最小开口/拟合圆直径 |
| C1:path-gap | s=[0,1,2],f=[1,null,3] →无完整区间量、known length0/unknown2，不能跨洞积分；s重复/逆序InvalidInput |
| C1:axis / pair | u=(.6,0,.8)、Q=0、T=(1.2,0,1.6)→H1.6/L2/tilt36.86989765°；u·n=0拒交点；h=2截面两轴x=0/2.74→2.74，非根部2.54 |
| C1:plane-layer | target z=1+.1x+.2y，±1角height .7/.9/1.1/1.3、range.6；m=(.6,0,.8),t=.1，同射线差.125，normal offset降Z.08/X.06；一角域外不报whole range |
| C2:triangle-moments-center | 上述完整fixture A=.5，area center(1/3,1/3)，covdiag1/18、cross-1/36；V1/6、Ju1/24/Jv1/12/Khh1/12、positive center(1/4,1/2,1/4)；不能用片面积中心×V |
| C2:clip / zero-cross | 单位方形h=u+2v全I1.5，裁u≤.5得I.625/A.5而非.75；三角h=-1+2u+2v正V5/24、Ju=Jv17/192、uv center17/40 |
| C2:holes / unknown / B | [0,3]×[0,2]真孔[0,1]² →A5/center(1.7,1.1)；同缺块Unknown则仅部分E；全B材料量0、中心/CDF无定义；重复FOV不累计；原Uh为空但归约停止时未处理F仍计R，整体CDF不等于KnownCDF；Us可全无材料，正高度Proof不能给Us正体积下界 |
| C3:continuous / atom / gap | 三角顶高0/0/1:C=2t-t²、q.75=.5；0/1/1:C=t²、q.25=.5；常片0/10等面积q.5=0，不返回5；[0,1]/[10,11]等面积q.5=1 |
| C3:unknown-conditional | E常1面积.4、Uh.6，全0/全2补全median0/2；Known median1不是whole上下界；E10/Us≤2界[0,1]不满足共同界，拒“全补1”包络 |
| C4:sign / exact / endpoints | 单位三角h=Σλ²-.5，顶高.5/重心-1/6，不凭顶点非负；h=x²-.25: signed-1/24、plus5/192、minus13/192、CDF(0)=.75/q.75=0；h=(x-1/3)²全域min0 |
| C4:subdivision / budget | h=x²-.25深度4δ=1/768，positive界需包含5/192；四子中途预算停保父片/域，不给Measured；Q归一尺度/坐标换序、同原场合法细分量不变 |
| C1–4:owners / versions | 两Host请求同模型结果等价、输入/端口租约独立；取消/10s wall/120s suite/180s外进程、late Profile/Acquire、原Task/Dispose单飞全部沿§16.3；0.2/0.3错版本前置拒绝 |

唯一工程/命令复用§16.1：C1–4纯Core `tests/Asun.Metrology.Core.Tests/...csproj` 的BCL Exe分组Continuous:C1/C2/C3/C4；Runtime故障落原Runtime.Tests，两个消费者落HostTests，ROI/HALCON适配才落Halcon.Tests。任一必需case缺失/超时/Unknown为非零，不用dotnet test冒运行。benchmark新增负载维度root/fragment/孔洞/相交对、bit峰值/有理运算、事件/p/query、最大深度/叶数、atom/间隙/未知域；分阶段计qualification/共同分片/矩/signed/正负/CDF整遍/反演/细分/输出舍入/真实排空。统计口径仍DEV-GOV-010 §3.1，目标缺失NotEvaluated；不把数学收敛当吞吐保证。

### 19.10 两轮反例自审、来源继承与精确剩余门

第一视角“数值定义与可观测支持”：逐查已迁入本页的原DEV-MET-031 §5–13规划→§19.1能力表；重核D/F/B/Us/Uh、原cell穿洞、正负裁零、投影面积、矩量纲/分母、原子/间隙左逆、Q内点负高与父片守恒。第二视角“外部消费者与资源”：factory前Root、原Task/Key/borrowed ports、late Profile/Acquire/Map、异常嵌套finally、独立cleanup、单飞Dispose、Owner转交确认、10/120/180双时钟及版本回退。主控已接收M1/M2/C1–C4六项Core规格为 `ModuleCoreImplementationReady`；该接收与自审不是实际测试或产品验收通过。

来源复用已迁入本页的原DEV-MET-031公式/合成向量及固定研究；旧共享页仅作研究与应用导航，不定义第二套活动算法：scikit-image `533b7694d2004ae84e49e2cfd0bcfc5f8e562f22`的spacing/centroid/orientation外层源码及测试（BSD-3-Clause，非高度体积矩）；SciPy1.16.2 `b1296b9b4393e251511fe8fdd3e58c22a1124899`的_quantile.py及测试（BSD-3-Clause，样本排序/端点教训，非连续面积CDF）；dhermes/bezier `cf18953a491e8568e4a4344327ed441d3e8956da` triangle_helpers.py及测试（Apache-2.0，de Casteljau/细分/预算异常，float符号不是严格证书）。继承原阅读范围和局限，不声称本轮重跑上游/研究脚本；不引入Python/NumPy/native数值包、复制源码或重复整篇网络研究。HALCON26.05语义仍§17及本地手册，AsunImage完整cv2薄封装直接用。

本轮只定向复核26.05本地`get_grayval_interpolated`（domain忽略、bilinear4/bicubic16及可能超原值域）、`integrate_funct_1d`（一维正负积分）及`gray_histo_range`（离散等bin频数）；继承已迁入本页的正式公式所需几何/量纲，不从算子名称猜连续面积CDF/Q能力。原DEV-MET-031链接[旧共享页研究与应用导航](../../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md)，十个旧anchor由主控保留并回链本页；公式、向量和合同实施按本页，不从旧页补充。bezier源码/测试原固定SHA分别`11b45dbc287ffedd6960a8fcca93ddb22ccb5cd3f05e48868ef1aad5421bd378`/`9e95fca7434f76a7336548f6c210e24e33367f8bb8729a6a55ede6a837137484`；旧研究脚本/证据保留但不成为产品运行依赖或隐藏实施权威。

确切剩余规格/外部门：六项Core切片已接收；基础ROI/surface/C5/P参考面/坐标只读映射见§20已限定内容接收指导，Codec/CG参数装配按已接收上游规格闭合；workbench/PG产品投影及连续资格由各原Owner接收，不能泛称上游公开软件契约全缺；真实WholeCellSupport/Classification/Boundary/Q预测及unknown-bound物理证明由上游Owner提供；C2–4存储模型的有理归约/向外舍入与托管上限是本节确定实现工作，不留任意算法选择。M3/M4 native资源保守包络、实际公共C#歧义仅阻断相应adapter。客户光学/材料/标准件、MSA/真实Golden/性能现场门保留；真实编译/BCL Exe/HALCON/WPF/性能均未执行。已规划的有限能力已在本节有类型、主路线、失败/预算/测试定位，不再用“以后待设计”整体退回第二权威；未规划的一般曲面法向、signed质心、Q正部中心/体积惯性/光程转换等明确Unsupported，不伪称支持。

## 20. M3/M4公开装配与只读桥（指导已限定内容接收，2026-10-11，未实现）

本节只补自有backend装配、消费上游公开值及两Host资源闭包，不改§12/13/19算法、坐标模型、连续归约或Golden。M1/M2/C1–C4六项规格接收保持；M3/M4本次公开装配与基础只读桥指导已获主控限定内容接收；Engineering/有限PixelDiagnostic和Unsupported能力边界不变。N-Envelope真实资源proof、E-Build公开程序集/消费者编译、native/Golden运行/性能、连续场分解/WholeCellSupport/物理及工作台产品映射均保原门，不将真实native或物理标Ready。桥代码计划仍在`src/Asun.Metrology.Halcon/`（namespace `Asun.Metrology.Halcon`），只引用本模块Contracts/Core/Runtime及上游公开Core契约：`Asun.Modules.CoordinateGeometry`、`Asun.Modules.RoiGeometry`及其Serialization、`Asun.Modules.SurfaceData`/`Contribution`、`Asun.Modules.ReferenceSurface`。不读取上游内部实现，不新增第五个公共DLL或第二数值引擎；不创建工程，本轮仅修改本文。

### 20.1 HalconBackend构造、能力与资源测点

保留§11.3既有成员与无参构造定位，增加以下**精确目标签名**（省略实现体）。有参构造才是M3/M4工作入口；无参构造仅为兼容的未配置实例：Methods.Empty，Start在接纳native工作前返回Unsupported错误，不隐式补生产Options或包络。不影响GeometryBackend。各getter为纯值，不访问授权/网络/文件或初始化native。

```csharp
// using Asun.Metrology.Contracts; namespace Asun.Metrology.Halcon;
public enum NativeStage { Normalize, CopyInput, BuildModel, Compute, ReadResult, Release }
public sealed record NativeEnvelope(AssetRef Proof, string AdapterBuild,
    string HalconVersion, Method Method, DataKind Kind,
    long MaximumInputElements, long MaximumPairChecks,
    int MaximumCandidates, long MaximumImagePixels,
    long MaximumManagedBytes, long MaximumNativeBytes,
    int MaximumHandles);
public sealed record HalconBackendOptions(int MaximumWorkers,
    int MaximumTrackedExecutions, long MaximumManagedBytes,
    long MaximumNativeReservedBytes, int MaximumHandles,
    TimeSpan CloseObservationLimit, ImmutableArray<NativeEnvelope> Envelopes);
public sealed record NativeObservation(OperationKey Key, NativeStage Stage,
    long MonotonicTicks, long ReservedManagedBytes, long ReservedNativeBytes,
    int OwnedHandles, bool WorkingSetMeasured, long? ProcessWorkingSetBytes,
    MetrologyError? Error);
public interface IMetrologyNativeObserver { void OnObservation(NativeObservation value); }
public sealed record HalconBackendSnapshot(bool Closing, bool Closed,
    ImmutableArray<BackendReceipt> Executions, long ReservedManagedBytes,
    long ReservedNativeBytes, int OwnedHandles, int PendingObservers,
    ImmutableArray<MetrologyError> Errors);
public sealed record HalconBackendCloseReceipt(bool Closed,
    HalconBackendSnapshot Snapshot);
public sealed class HalconBackendCloseException : Exception {
    public HalconBackendCloseException(HalconBackendCloseReceipt receipt);
    public HalconBackendCloseReceipt Receipt { get; }
}
public interface IHalconMetrologyBackend : IMetrologyBackend, IAsyncDisposable {
    HalconBackendSnapshot GetSnapshot();
    ValueTask<HalconBackendCloseReceipt> CloseAsync(TimeSpan observationLimit,
        CancellationToken waitCancellation);
}
// HalconBackend公开类及两个构造定位§11.3；不重复声明该类。
```

Options的workers/tracked/managed显式正数，workers同时受request.MaxParallelism/RuntimePolicy限制，CloseObservationLimit有限正且≤24h；Envelopes非default，可Empty表示尚无native证据。仅Empty时MaximumNativeReservedBytes/MaximumHandles允许同时为0，表示禁止native分配，不表示未知成本为0；非Empty时二者必须正。每条proof必须精确绑定本包实际AdapterBuild、HALCON26.05与表内Method/Kind/形状上限；字段正数（不适用的PairChecks/ImagePixels可0），不得用0表示“未知native成本”。同Method/Kind多条时按数组原序取**第一条完整覆盖**的已核proof，不能取平均/经验倍率。Proof由宿主在装配前核对证据内容/来源与全部包络字段并冻结catalog，本backend只核精确引用/实际build/字段及限额，不凭AssetRef字符串认证证据或签发资格；该内容核对属于N-Envelope执行门。`Methods`仅回显已配置且有覆盖条目的§13方法；Empty时Methods.Empty，Runtime按既有能力检查返回Unsupported/Unsupported，不调用Start。直接Start无覆盖条目，或已配置方法遇到build/版本/shape/预算不符，抛MetrologyPortException携BudgetExceeded（Runtime已接纳时保其ResourceLimited分类），零native分配/无execution。本节不编任何条目的native字节/handles/性能值；实际保守上界模型和同样本测量是N-Envelope门，获准以前该native路线不运行。

Start先登记OperationKey/execution槽、原Task及输入租约/coordinate引用，再校验并原子预留Options与request预算交集；只启动一个worker，不从多个engine共享可变model。预留账不是实测native bytes；观察分别记录Normalize/CopyInput/BuildModel/Compute/ReadResult/Release的单调测点、预留managed/native与实际Owner handle计数。ProcessWorkingSet为可选独立进程测量，无法采集时WorkingSetMeasured=false/值null，不填0、不用工作集变化声称精确native驻留。observer锁外短同步且无handle/输入，异常停订阅并记诊断、不改变计算事实；其原callback未退出时不得Closed。进度/订阅有界沿RuntimePolicy，不创建无限观测日志。

backend不改进程级HALCON系统参数（线程数、empty行为等），不Scan授权；各方法沿§13参数、创建/clear顺序与公共cv2消费。输入私有复制、model/measure/matrix/index/临时Region/XLD与结果复制的峰值同计账；Release先确认worker/回调退出，逆序clear私有handles再解预留。clear抛错/无法确认保ReleaseUnknown及原execution；不能仅以Task退出清账。源lease/上游服务完全借用，backend不归还。Close只封住本backend新Start并RequestCancel其原execution，等待退出/Released/观察者退出；该方法不dispose借用ports。Closed必须所有Executions.Released、两ReservedBytes/OwnedHandles/PendingObservers均0；已保存Errors不抹掉。Close=false保账和原Task，waittoken仅停观察；GetSnapshot仍可查。Dispose以Options.CloseObservationLimit执行同关闭路径，未Closed抛HalconBackendCloseException并保对象；同一原Dispose只观察、不重发。无参实例Dispose沿同路径用固定2s观察，没有native配置或生产参数。GetReceipt/ReleaseAsync仍沿§14，不添加另一质量/设备状态机。

### 20.2 只读准备桥的完整公开形状

别名仅用于本节声明：`CG=Asun.Modules.CoordinateGeometry`，`RG=Asun.Modules.RoiGeometry`，`SD=Asun.Modules.SurfaceData`，`SC=Asun.Modules.SurfaceData.Contribution`，`RS=Asun.Modules.ReferenceSurface`。新增值为装配合同`metrology-read-bridge/1`，不改Contract0.2/0.3或其编码。没有“任意算子/动态字典/自动最新”端口。

```csharp
public enum BridgeRoiOutput { PolygonGeometry, Contours, RegionRuns }
public enum BridgeSurfaceOutput { PointGeometry, Mesh }
public enum BridgeReferenceOutput { PlaneGeometry }
public enum BridgeState { Created, Preparing, Ready, Closing, Unknown, Closed }
public sealed record BridgeOptions(int MaximumSources, int MaximumOriginalTasks,
    int MaximumLeases, int MaximumPointBlock, int MaximumParentEntries,
    long MaximumRetainedBytes, TimeSpan PrepareLimit, TimeSpan CloseObservationLimit);
public sealed record CoordinateReadPlan(CG.GraphSnapshot Graph, CG.ExplicitPath Path,
    CG.NumericPolicy Numeric, CG.AssetRef Source, CG.AssetRef Target);
public abstract record BridgeInput;
public sealed record FrozenPayloadInput(SourcePayload Payload) : BridgeInput;
public sealed record RoiSnapshotInput(RG.GeometrySnapshot Snapshot,
    RG.ValidationProfile Profile, ImmutableArray<string> NodeIds,
    BridgeRoiOutput Output) : BridgeInput;
public sealed record RoiLeaseInput(RG.IRoiGeometryLease Lease,
    RG.RoiMaterializationRequest Materialization, RG.RoiFrame Frame,
    RG.ValidationProfile Profile, BridgeRoiOutput Output) : BridgeInput;
public sealed record SurfaceValueInput(SD.SurfaceDescriptor Descriptor,
    SD.SurfaceReadRequest Vertices, SD.SurfaceReadRequest? Faces,
    SC.ContributionReadRequest? Contributions,
    BridgeSurfaceOutput Output) : BridgeInput;
public sealed record ReferenceValueInput(RS.SurfaceSnapshot Source,
    RS.ReferenceSurfaceResult Result, RS.ResolvedReferenceProfile? ExactProfile,
    BridgeReferenceOutput Output) : BridgeInput;
public sealed record BridgeSourceDeclaration(string Id, ulong Revision,
    AssetRef TargetFrame, AssetRef? Calibration, CoordinateReadPlan? Map,
    BridgeInput Input);
public sealed record BridgePrepareRequest(string ContractVersion, OperationKey Key,
    Scope Scope, ExecutionBudget Budget, ImmutableArray<BridgeSourceDeclaration> Sources,
    ImmutableArray<MethodProfile> Profiles);
public sealed record BridgePorts(RG.IRoiGeometryCore? Roi,
    RG.Serialization.IRoiGeometryCodec? RoiCodec,
    SD.ISurfaceDataService? Surfaces, SC.IContributionReader? Contributions,
    CG.ICoordinateGeometryService? Coordinates,
    RS.IReferenceSurfaceProfileSource? ReferenceProfiles);
public sealed record BridgeParent(int ParentSlot,
    SC.ContributionParentReference Parent, long Ordinal, double Weight);
public sealed record BridgeCarrier(string SourceId, SD.SampleDomain Domain,
    long Ordinal, long RootSourceIndex, SD.SampleState State, uint Reason,
    SD.OriginEntry Origin, SC.SupportState? ContributionState,
    SC.ContributionMethod? ContributionMethod, ImmutableArray<BridgeParent> Parents);
public abstract record BridgeOriginalValues;
public sealed record BridgeFrozenValues(SourcePayload Payload) : BridgeOriginalValues;
public sealed record BridgeRoiValues(RG.GeometrySnapshot Snapshot,
    RG.ValidationProfile Profile, RG.RoiGeometryLeaseInfo? LeaseInfo) : BridgeOriginalValues;
public sealed record BridgeSurfaceValues(SD.SurfaceDescriptor Descriptor,
    SC.ContributionDescriptor? Contributions) : BridgeOriginalValues;
public sealed record BridgeReferenceValues(RS.SurfaceSnapshot Source,
    RS.ReferenceSurfaceResult Result,
    RS.ResolvedReferenceProfile Profile) : BridgeOriginalValues;
public sealed record BridgeSourceTrace(string OutputId,
    ImmutableArray<AssetRef> OriginalEvidence,
    ImmutableArray<BridgeCarrier> Carriers, BridgeOriginalValues OriginalValues,
    CoordinateReadPlan? OriginalMap, ImmutableArray<CG.MappedResult> CoordinateResults);
public sealed record BridgePreparedSource(SourceRef Source, SourcePayload Payload,
    BridgeSourceTrace Trace);
public sealed record BridgePrepared(OperationKey Key,
    CoordinateBinding Coordinates,
    ImmutableArray<BridgePreparedSource> Sources,
    ImmutableArray<AssetRef> ProfileReferences);
public sealed record BridgeSnapshot(OperationKey Key, BridgeState State,
    int OriginalTasksPending, int ValueLeasesHeld,
    ImmutableArray<string> PendingIds, ImmutableArray<MetrologyError> Errors);
public sealed record BridgeCloseReceipt(bool Closed, BridgeSnapshot Snapshot);
public sealed class BridgeCloseException : Exception {
    public BridgeCloseException(BridgeCloseReceipt receipt);
    public BridgeCloseReceipt Receipt { get; }
}
public interface IMetrologyReadBridge : IAsyncDisposable {
    OperationKey Key { get; }
    IMetrologyInputReader Reader { get; }
    IMetrologyCoordinatePort CoordinatePort { get; }
    ValueTask<BridgePrepared> PrepareAsync(CancellationToken operationCancellation);
    BridgeSnapshot GetSnapshot();
    ValueTask<BridgeCloseReceipt> CloseAsync(TimeSpan observationLimit,
        CancellationToken waitCancellation);
}
public static class MetrologyReadBridgeFactory {
    public static IMetrologyReadBridge Create(BridgePrepareRequest request,
        BridgeOptions options, BridgePorts borrowedPorts);
}
```

Create先total校验/冻结全部值，非法抛MetrologyPortException携既有InvalidRequest/Unsupported/VersionMismatch；零IO/native/worker、失败零私有资源，借用上游实例从不dispose。ContractVersion固定`metrology-read-bridge/1`；key/arrays/预算/Options显式正数且非default，Sources/Profiles非default且非空，Sources.Id不重复且TargetFrame逐字段一致，所有Profile维度/长度单位一致，未使用字段沿§11.2规范；本基础桥只服务Contract0.2。factory前Host已预留有界根槽，原prepare request/key、借用ports与每个RoiLease均强持；不是等Prepare返回后登记。需要的port为空先拒绝，ROI快照/Vector需要Roi和RoiCodec；未使用为空合法。不在constructor读取Query/当前active或创建隐含上游engine。Create不检查已批准依赖授权。FrozenPayloadInput声明已在TargetFrame/目标单位；不允许同时Map，不能重新套图。不导出ContinuousPayload；§19原ContinuousReader/Frozen值入口继续独立使用，连续Owner证据不由基础桥生成。封闭union未知派生/枚举拒绝；RegionRuns本桥Unsupported，不能向identity端口提供原row/column而假称已是X右/Y上。Trace只保BridgeOriginalValues/CG值，无BridgeInput、lease、service、Task或handle；materialized Vector原快照/LeaseInfo及resolved Profile先复制再归还，trace不能继续持租约。字符串/原DTO/全部trace/CG结果也计MaximumRetainedBytes，超限拒绝，不静默截去父项。

首次Prepare先在同bridge登记唯一原Task，再启动后台准备；重复调用同实例等待同Task，不重复Open/Start/Map/Resolve。只有首次调用operationCancellation绑定执行，后续重复调用的token不撤销原请求；Host取消用首次token或Close，有限观察用自己的WaitAsync。返回BridgePrepared只在所有准备调用/输出复制/自有上游profile租约已实际归还时完成，scope/输入仅Engineering或允许的PixelDiagnostic；完整values按声明深冻结。错误/超时不返回部分Prepared，资源确认后原Task抛MetrologyPortException携对应Code，并保snapshot诊断；底层仍未知时原Task在途，Host有限观察保根。Runtime后续Acquire返回bridge**自有只读值租约**，不隐藏重新读上游；按exact source/profile/input ref核canonical，错revision/hash拒绝，不从最新重取。取得值租约计ValueLeasesHeld，Dispose单飞、归还才Released；计量service原Task未退出时bridge不能清已编译payload。

Sources数组保持声明顺序；Id/revision标识新的“计量编译值”，不是上游SurfaceKey/ROI文档hash。SourceRef.Content.Sha256用§15 HashSource对编译payload计算，Frame为TargetFrame、Unit=Pixel或Mm、Kind按输出union、Calibration仅保传入精确引用；图像/SD/ROI/RS原hash不替换为此hash。BridgePrepared.ProfileReferences依次取Id=`bridge-profile.<OperationId:N>.r<RequestRevision>.n<index>`/Revision1/HashProfile，与原Profiles数组一一对应；caller不能按Method重配。引用只绑定进程内冻结值，不冒充Store已封存；请求仍用原Key、完整Definition/Budget/Prepared.Coordinates。源Id新但相同payload可同hash，不能据hash省略原来源；OriginalValues/OriginalMap/CoordinateResults各保公开值及原Owner规约。

Reader在Ready以前InputUnavailable，关闭后不发新值租约；GetSnapshot始终可查。CoordinatePort为**已编译值identity端口**：Prepare返回唯一Coordinates=(共同TargetFrame,共同TargetFrame,Mapping,null,null)，Mapping.Id=`bridge-identity.<OperationId:N>.r<RequestRevision>`、Revision1、Sha256=§15 HashSource对GeometryPayload([GeometryItem("identity-origin",Point2(0,0))])或D3 Point3(0,0,0)的摘要；这是具名工程identity证据，不是CG执行/标定hash。原CG执行结果另保Trace，不拿单source的CG结果当跨sources共同binding。ValidateBinding只接受返回Coordinates逐字段/Scope及原Key预算，Map只允许Identity/同unit回原点序，Coefficients.Empty、Receipt=Coordinates.Mapping，不做第二次变换。没有猜测FixtureRef或用新hash掩盖旧frame。CalibratedPhysical本准备桥返回Unqualified；该软件桥不签发Calibration/ApplicabilityReceipt，生产可消费必须另有原Owner资格适配。这不撤销§14/15已有生产接口。

### 20.3 IM-007/024/031/C5/035逐字段消费与原值Owner

| 实际公开上游/入口 | 本桥调用/返回映射与界限 |
|---|---|
| [IM-007 §4.3](../coordinate-geometry/DEVELOPMENT-GUIDE.md#43-冻结literal公开声明与factory)：`CoordinateGeometryFactory().CreateManaged(RuntimeLimits,TimeProvider)`，GeometryRequest/MapWork/GeometryBatch | CoordinateReadPlan固定Graph/ExplicitPath/Numeric/Source/Target；内部按§4.2 `coordinate-core-values-v1`声明算法编码新batch.Ref，点Items依原顺序为Point2Value/Point3Value，polygon/polyline/plane用对应整项类型，Uncertainty=new NoCovariance()，不伪传播。GeometryRequest=("0.2",`met-map.<Guid:N>.r<rev>.n<seq>`,MapWork,原剩余PrepareLimit)，原Submit/Wait/Query/Cancel Tasks先登记；Admission.Rejected失败，WaitExpired只是观察，须原Query.State=Completed、Drain=Confirmed、MappedResult.Graph/Policy/Source/Target/Path、Admission.InputHash=Result.InputHash、batch Ref与逐项/维度/finite核对才采用。实际MappedResult保在Trace.CoordinateResults原序并计返回字节；InputHash是已冻结执行身份，不冒原源hash。未完成只Cancel该RequestId，禁止Stop共享service。映射上限继承CG Numeric/RuntimeLimits；软件Bridge不求解或选另一链。 |
| CG帧、单位、像素语义 | Target的实际Graph.Frame.Ref必须与SourceDeclaration.TargetFrame Id/Revision/Sha匹配，D2=Oriented2D、X/PositiveX与Y/PositiveY同Basis，D3=Right3D/XYZ正轴同Basis；mm只Millimetre/None。Map.Source的Id/revision/unit/axes须匹配原SD/ROI/RS字段；没有源frame hash的上游值通过冻结Graph原Frame绑定，不能虚构其原hash。Map=null仅已是共同目标frame/单位/轴的原值，ROI Frame仅Id时绑定相同Id的冻结目标声明且Revision须由宿主提供，不从ROI文档revision推帧revision。CG v0.2的Pixel帧按其§4.1限定ImageColumnRow；不能向该服务提交新Cartesian Pixel帧绕过校验。本桥ROI Polygon/Contour的ColumnRowPixelCenters→X右/Y上 PixelDiagnostic路线返回Unsupported/Unsupported，作为明确软件能力边界，不能只换frame标签或自行写第二换轴算法；原RegionRuns可保离散原row/column供既有native诊断，须原计量映射端口另接，本桥identity端口不授有向几何。m/um→mm比例只由显式CG单位边编码，桥不再乘一次；RS模型自身米单位的正规导出见下行。polygon作为CG.Polygon2Value、轮廓作为Polyline2Value整项提交，复用CG全域核验，不拆成独立顶点冒连续域证明；只允许已冻结Affine2/Identity链。非线性连续边证书缺失Unsupported，不点采样替代。 |
| [IM-024 A.1](../roi-geometry/DEVELOPMENT-GUIDE.md#a1-coreslice-01-值对象与入口)：RoiGeometryFactory.Open、IRoiGeometryCore.Validate/Query、GeometrySnapshot | RoiSnapshotInput显式Nodes，不按Visible/Selected/Locked自动过滤；用RoiValidationRequest原冻结Snapshot/Profile/deadline作只读Validate，IsValid/ResourcesReleased都true才复制。DocumentId/Revision与Frame/Node/Source全保BridgeRoiValues；ROI无全局SourceSha入口，借用RoiCodec.Encode(operationId,snapshot,profile,原剩余deadline,token)，Errors.Empty/Bytes非default且在MaxSerializedBytes内后核SHA256(Bytes)=RoiEncodeResult.Sha256，Trace证据Id=`roi-envelope.<DocumentId>`/revision=文档revision/hash=该完整envelope hash。原roi-json-v1 payloadHash由Codec验证，桥不猜未公开的payloadHash getter，也不拿它代完整Sha256。不得用RoiSource.Sha256冒Snapshot hash；RoiSource支持字段保NotProvided/Partial/Complete，不因闭合升级Observed。PolygonGeometry接受Rectangle/Polygon，Rectangle四角Center±U±V，每Component单GeometryItem/Polygon2，Outer为Boundary、Holes为Hole；Contours接受Polyline与显式polygon rings，每ring单ContourId并保Closed语义，不隐式合外环/孔。原Curve无已材料化tessellation的snapshot返回Unsupported；桥不调用Suggest/离散曲线或生成新误差证书。Vertex/Ring顺序不变。 |
| IM-024 A.4 IRoiGeometryLease.MaterializeAsync/QueryMaterialization/Drain | RoiLeaseInput由Host持**借用lease**，不转移释放权；原Materialization ID/Task先入bridge且原Host根已持lease。receipt IsTerminal/ResourcesReleased且Errors空后才复制Vector，Running/Unknown无payload等待/回查同ID，不调用第二Materialize覆盖原请求。Info.FrameId/Unit/Grid/Precision/Report核对输入及copy预算，Grid没有Frame字段，不猜不存在属性；Info是native输出Owner身份，不等材料/物理资格。Vector全部Shape叶节点依原顺序消费，不按隐藏/锁过滤，Snapshot.Frame与输入Frame/Profile相符，LeaseInfo另保BridgeRoiValues。RegionRuns本桥Unsupported；其它批准端口消费时仍须原Pixel/Grid origin/step/尺寸和RoiRun.ObjectIndex保真，不能丢ObjectIndex后累加重叠runs或把非单位grid当原像素。Tessellated仅保原误差，不改成StoredValues。 |
| [IM-031 §3](../surface-data/DEVELOPMENT-GUIDE.md#3-公开-factory端口结果与关闭)：SurfaceDataFactory.Create/ISurfaceDataService.StartRead/ISurfaceOperation.Completion | SurfaceValueInput.Descriptor与每请求Descriptor逐字段/数组一致。Plan先预检，原Start/operation/Completion在bridge登记。Vertex选PreserveAll，FieldIds为该Kind的XYZ或Height，ReadCoordinates=true；Face选TriangleIndices、ReadCoordinates=false、Target/Transform=null。OnBlock同步把Ordinals/SourceIndices/Positions/字段state/reason/Origin复制到预留managed槽，禁止Span跨回调；Receipt Completed、Complete/合法Empty、Integrity.FullBuffers且原Completion真实退出才采用。source原buffer hash包含padding按SD算法，不另造descriptor组合hash。两个域不得混Root SourceIndex与face vertex ordinal。Plan/MaxResident同时含副本/反序索引/trace/C5父项；不是只算SD临时内存。 |
| SD源frame/units/HeightField | raw字段physical=raw*Scale+Bias由SD唯一执行，桥用PositionValue而非再解PackedValues乘Scale。HeightField的ISurfaceCoordinatePort借用host显式CG桥：Grid.Mapping匹配已冻结CG显式路径，输入父col=ParentColumnOffset+i%Width、row=ParentRowOffset+i/Width，CG像素中心→Descriptor.Frame对应单位的XY，Z保SD原高度；不是从crop宽猜Root，也不从Grid推pitch。SD.TargetFrame.Unit必须等Descriptor.Unit，故先到该源单位frame，再由CoordinateReadPlan显式CG3路径转计量目标mm；不能向SD传跨单位TargetFrame。Invalid/Unknown的NaN positions绝不进入finite计量payload；保BridgeCarrier状态与原Root索引，不填有限0冒原值。 |
| SD PointGeometry/Mesh | PointGeometry请求范围内全部点必须Valid finite；任一Invalid/Unknown拒InsufficientSupport，不过滤后给HeightSummary完整Measured，原状态留诊断/Owner原值。点SampleId及Mesh VertexId固定=`v.<ordinal不带前导零十进制>.<RootSourceIndex原Int64十进制>`，在本source内唯一，Trace另保源Id/revision/domain；保原Origin，不将Interpolated/Filtered当Observed。合法Empty仍按原计量方法无支撑拒绝，不填零。Mesh必须完整Vertex读取、Face完整读取与原三顶点当前ordinal映射；任何被面引用的无效/未知点，拒绝完整Mesh，不删面/补面。现有PointCloud不造Faces、HeightField不选对角生成mesh。MeshPayload.Domain默认null；DatumVolume需要§12.3另有真实Footprint/UnknownFaceIds/源hash绑定回执，不能由SD.MeshReport闭合或所有Valid推完整域。普通mesh接口不携来源state，旁路trace保全部来源；表面拟合只消费声明用途，原值Owner仍SD来源/生产者。 |
| [IM-031 C5 §15.2–6](../surface-data/DEVELOPMENT-GUIDE.md#152-独立-contribution-api-v01)：SurfaceContributionFactory.Create/IContributionReader.Start/IContributionPageConsumer | Contributions非null时Carrier完整Descriptor、Domain与requested字段、Generation/范围必须匹配该SD原读取。C5自身已核实际Origin列，桥再将page行按CarrierStart+行index与SD carrier.Ordinal对齐；不能按page顺序或Root SourceIndex join。保存States/MethodIds及每个ParentSlot/ParentOrdinal/Weight（Int64不转double，零权保留），通过Descriptor.Parents取父Surface/domain/Frame/SnapshotSha256，Methods记录ProducerRecorded/method/原Evidence hash，实际Carrier.Origins[OriginId]与该Method.CarrierOriginId仍一致。C5.Completion Completed/FullBuffers/EndOfRequest及计数后才采用暂存；未到EndOfTable不伪称全表。 |
| C5父原值与支持 | Trace仅证明原生产者记录，父源未自动打开；SnapshotSha256按原Owner证据规约，不能拿carrier buffer hash代替。父值需宿主从对应Surface/domain/ordinal公开StartRead再查询原状态/Origin/Root，并经自己的CG链映射；没有Parent descriptor/source或可信Snapshot时保Unknown，不从weights重算本carrier值、更不能生成等权/最近点。ObservedIdentity精确1也不授生产；ConvexCombination保持Interpolated/Repaired/Filtered/Cad，Unknown/Unsupported不造Exact。多父与单父HasExactParentIndex不互转；连续WholeCellSupport/Domain来自原算法/ROI/reference Owner，不由C5行Exact、父数或权重和推出。未选C5保持显式ContributionState=null/Parents.Empty，不把“无表”写Unknown假行。 |
| [IM-035 §4](../reference-surface/DEVELOPMENT-GUIDE.md#44-完整入口事件与求值端口)：ReferenceSurfaceIdentity、IReferenceSurfaceProfileSource.ResolveAsync、P/H/Q公开结果 | 只消费既有ReferenceSurfaceResult，桥不Execute/重拟合参考面。核Status=Succeeded、Binding/RequestSha256/Model/Evidence/ResultSha256/ProfileReference；ComputeSurfaceSha256(Source)、ComputeProfileSha256、ComputeRequestSha256(Binding,profileRef,ContractVersion,AlgorithmVersion)、ComputeModel/Evidence/Result及Binding字段原规则全部相符。ExactProfile为null时Resolve原ref并强持原Task，晚profilelease唯一Dispose实际退出后才Prepared；不换最新。P PlaneModel.Origin/DInMeters始终米；先按Binding.Unit正规导出CG.Plane3Value(normal,D)和原Origin到原frame：Meter乘1、Millimeter乘1000、Micrometer乘1e6，此步只解码RS模型单位。再走显式CG Identity/Rigid3或正均匀SI scale链到target mm；平面整体用CG.Plane3Value映射，不将法向当点，Origin另Point3映射并核n·Origin+D。输出Plane3(Origin,Normal)保模型/结果/evidence原hash引用，不能把新hash冒ReferenceSurfaceResult hash。不等距/非均匀3D affine在本基础Plane入口Unsupported。H/Q不伪装PlaneGeometry，此入口Unsupported，仍经下一行v0.3已冻结强类型消费。 |
| RS连续场与§19 | P导入按原ContinuousCells/ForbiddenCells/UnknownCells及用途Proof限定PlanePatch.ObservedDomain/PermittedPredictionDomain，不用ReferenceFootprintHull造区域。Q的Chart原Origin按Binding.Unit转mm，中心/ScaleXY(m)乘1000，固定ScaleZmm=1000、CenterZmm=0、Coefficients=原CoefficientsInMeters六项，保持f=1000×原米模型，不重拟合或更改系数；PhysicalFrame U/V/N是原Chart基，允许显式Rigid3将整体基转目标，非等距/一般Q坐标链Unsupported。Model/Qualification保原引用；适用域、原top cell/WholeCellSupport、材料F/B/Us/Uh和未知界仍需原Owner证据。Roi Polygon没有Triangulation DTO，不能宣称ROI已提供§19 PlanarDomain.Decomposition：仅接受已有公开SD/RS单元组成的冻结无重叠三角与原Boundary/资格回执，由§19 Core核边图/面积/归属；只有ROI边界时有限基础面积可算，v0.3分解请求Unsupported/Unqualified，精确欠账是上游分解证据，不把全部只读软件桥退回未定。 |

本节只读桥有明确固定版本依赖：CG API0.2、ROI Core/Lease v0.3、SD API0.4/C5 API0.1、RS rs-api-0.1/rs-managed-1；本轮读到的公开声明规格不等于本机已编译程序集，真实项目引用是E-Build门。固定六项值/算法不重审，消费者API若以后变更须主控与原Owner接收；禁止通过复制上游内部helper实现映射。

### 20.4 原Task/lease所有权、关闭与有限恢复

桥只拥有准备操作的SD/C5 operations与暂存copy、CG原RequestId、RS Resolve取得的profilelease、完成后的值租约；借用SD/C5/CG服务、ROI core/lease和profile source的整体寿命归Host。每个操作返回前Root/bridge已预留任务/lease槽。StartRead/Contribution.Start在同一已登记Prepare执行线程中返回时立刻登记operation及Completion，再投影给等待者；OnBlock/OnPage退出和Completion均需确认。Resolve/Materialize/CG Submit/Wait/Query各Task先登记启动闩锁再放行；失败也保原ID，不用超时包装覆盖底层Task。最大Task数按sources×(读取域+贡献+映射块+解析profile+Materialize+关闭)checked预检，超过槽在任何上游Start以前拒绝；CG分块ID可复用已确认无资源槽，但保已结束错误/执行身份证据的有界摘要。Root含不同service实例/原请求source/trace/port，元数据存入错误栏不等真实资源强持。OriginalTasksPending只计本桥已启动的上游业务/lease cleanup；当前Prepare/Close监督Task另由Root持，不计作自己要await的子Task，避免关闭等待自身。仍须Prepare实际退出后才能退Host槽。

CloseAsync先封新Prepare/Acquire/Map，原Prepare请求取消，逐SD/C5 operation.RequestCancel、CG.CancelAsync只针对原RequestId；原task未退时即使Close观察到期也不释放暂存/输入/借用lease。SD/C5 Completion确认退出与session.Dispose结束后才释放本桥copy的工作预留；RS profile lease.Dispose在原Resolve返回后唯一启动；ROI Materialize未终态时Query同ID，租约本身归Host，桥不先Dispose它。CG须原Query.Drain=Confirmed/唯一终态；Close可等待原Prepare退出，Prepare不能等待自己；Cancel返回只是命令观察，不等Map退出。原backend/native与valuelease全归计量服务按§14释放；bridge.Close只在其原Prepare未启动或其原Task已实际退出、OriginalTasksPending=0、ValueLeasesHeld=0和本桥工作copy清账后Closed=true，service尚在使用值时不能提前清桥。 Close参数必须有限正且≤24h，非法先抛ArgumentOutOfRangeException不改变状态；合法waitCancellation只停观察，不撤销关闭，取消抛OperationCanceledException，后续查询原Snapshot/Close。DisposeAsync以Options.CloseObservationLimit复用原关闭路径，Closed=false抛BridgeCloseException并保对象；成功须Snapshot.State=Closed、PendingIds.Empty、OriginalTasksPending=0、ValueLeasesHeld=0，Errors可保留。原Dispose唯一启动，有限观察不重发；关闭只释放本桥持有的managed引用/工作账，不宣称宿主仍持Prepared值已被GC回收。

Host关闭顺序固定：metrology service.RequestCancel→有限Close/原Dispose（§16.3 Closed/Pending双guard）→HalconBackend.Close/原Dispose（所有execution已Released）→ReadBridge.Close/原Dispose→Host自有ROI lease.Drain/原Dispose→自有ROI backend/core Drain/原Dispose→自有SD/C5 Close→自有CG.StopAndDrain。各步独立新wall CTS，每步失败仍检查其它**无依赖冲突**的cleanup；前一步未归还时不dispose依赖对象，只登记待执行后续cleanup与强持，backend未知尤其不能先清bridge。RS profile source整体借用，不Close；若Host自行创建RS engine，其Close/原Dispose也在其原业务/回调退出后独立执行，不归metrology代处置。

每个原Close/Dispose/StopAndDrain至多一个在途调用；DisposeStarted在调用前置位，同步抛错也不自动重试。重复Close可在前次结束且仍Unknown时由原监督者有限恢复查询，不重置业务deadline或另建engine。故障虽Task结束但无Owner回执继续保槽；错误已保存且资源确已归还才退槽，CaseExitCode非零不归零。移交通知无接收确认、页面关闭或Host等待超时均不转移Owner；根监督沿§16.3 case10s/suite120s/外进程180s，独立cleanup每步限min(2s,case剩余wall)，0剩余只登记待执行cleanup，Root监督有剩余wall时才启动，不能传非法零期限或释放依赖，不无界await；suite到期保原Owner诊断Unknown，进程结束不追认Released。

### 20.5 两个独立无UI Host的装配配方

唯一入口仍为`tests/Asun.Metrology.HostTests/`，分组`Bridge:roi-engineering`与`Bridge:surface-reference`；每Host独立上游实例/Source字典/OperationId/Task根，不依赖工作台Shell/VM/Store/静态缓存。以下是目标规格，尚未编译；synthetic仅验证软件桥。上游公开接口参数可以显式注入，不能猜未声明的concrete类或构造器。ROI0.4.3的Codec创建和CG0.3.5的参数名规格均已获主控接收，本节按原公开声明精确消费；本桥指导已限定内容接收，程序集实际消费编译和native执行分别留门，不再列这两项为软件待补。

**共用装配值与根**：

- 进程Root仍2槽/128MiB，Host-A先预约64MiB、Host-B先预约32MiB；这些是测试容量，非实测峰值。预约覆盖原fixture bytes、上游输入/工作/输出/保留、桥冻结值/trace/CG结果、副本、服务通知和关闭Task；运行按实际checked长度再核，超上限在相应Start前拒绝。先登记Key及下述全部原值/ports/实例/lease，再放行业务闩锁。Root强持原Prepare、Measure、SD/C5 Completion、CG Submit/Wait/Query/Cancel/Stop、RS Execute/Resolve、ROI Materialize、每个Close/Dispose及其独立CTS；观察包装Task不取代原Task，ValueTask只AsTask一次。
- BridgeOptions=`(4,64,16,64,32,1048576,6s,2s)`；计量ExecutionBudget=`(16,64,4,16,65536,1,1,5s,5s)`，与原§16.2一致。Prepare总期限6s并受case剩余wall限制，不能每个上游步骤另得6s。每个原上游operation传min(本表局部limit,Prepare剩余,case剩余)，低于上游最小有效期限时不启动；缩短期限只改预算及其请求hash，不改算法Profile。
- NativeOptions=`(1,16,65536,0,0,2s,Envelopes.Empty)`，`new HalconBackend(nativeOptions,null)`，0/0是禁止分配容量，不是native成本；Methods.Empty。Runtime下native尝试固定Unsupported/Unsupported且Start次数0。单独直接Start校验case固定抛BudgetExceeded且native分配0，不与Runtime的expected混写。GeometryBackend的纯成功case独立装配，不让HalconBackend暗回退。
- 所有服务装配均是`new MetrologyService(bridge.Reader,bridge.CoordinatePort,selectedBackend,new RuntimePolicy(16,1,32,2s))`；Prepare返回的Coordinates/ProfileReferences/Sources作为唯一请求输入。不同测量attempt必须Key的新RequestRevision，并单独bridge/service，不能同一bridge Key下换请求或payload。无参HalconBackend另测兼容Unsupported，不进入成功case。
- 各自CG服务用`new CG.CoordinateGeometryFactory().CreateManaged(new CG.RuntimeLimits(1,64,16,64,4,4,262144,262144,1048576,6s),TimeProvider.System)`。NumericPolicy为Ref、FrameRules、`1e6,1e-12,1e-10,1e-12,1e-10,4,4,64,Optional,new AlgorithmLimits(64,4096,1000000,256,256,64),SourceRef`；每个图内frame恰一条FrameNumericRule(该Ref,下述逐轴尺度,0,1e6)。这些是显式软件数值域，不是客户准确度/性能门。Frame/Graph/Policy/Batch Ref按CG §4.2值规约逐个封存，不用FixtureRef(Id)代本地内容hash。外部Basis/Source证据可用§16.2 FixtureRef具名synthetic identity，须保原UTF8 bytes，不伪称物理基准。
- 构造顺序固定：Root→上游Source/值→自有上游Factory→BridgeFactory.Create→登记唯一Prepare Task→有限观察Ready→selectedBackend/service→登记唯一Measure Task→消费Released终态→§20.4关闭。任何factory同步抛错仍由已登记Root保存错误并清已构造实例；未创建的对象不伪发关闭回执。

**Host-A / RoiEngineeringBatchHost**（Engineering，ROI正式值/Codec/CG identity）：

1. Key=(`6f7bd570-4a70-4ad3-ae70-4c36762f5f31`,1)。ROI Frame=(`roi-mm`,Millimeter,RightHandedPhysicalXY)；Snapshot=(`met-roi-a`,1,Frame,[node])，node=(`n1`,null,0,true,false,PolygonShape([component]),Constraints.Empty,null)，component=(`c1`,RoiRing(`ring0`,[RoiVertex(`v0`,(0,0)),`v1`(4,0),`v2`(4,3),`v3`(0,3)]),Holes.Empty)。Source=null只表示工程指定几何，不是假Observed。
2. ROI Profile逐字段复用其[§10.1 metric分支](../roi-geometry/DEVELOPMENT-GUIDE.md#101-两个完整-core-host-与有限进程根)正文的metric fixture构造/哈希算法（宿主按明列字段构造，不引用内部HostFixture类）：Id=host.metric.profile、Revision1、Frame如上、MaxAbsCoordinate10000、MinLength1e-6、MaxCondition1e6、MaxNodes128、MaxVertices8192、MaxRings256、MaxComponents128、MaxCandidatePairs1e6、MaxWorkingBytes16777216、MaxOutputBytes4194304、MaxUndoSteps16、MaxUndoBytes4194304、MaxInFlight2、MaxPending2、MaxReceipts128、CheckBatchSize32、MaxCurveDeviation.001、MaxTessellationVertices4096、MaxSerializedBytes1048576、MaxJsonDepth32、CloseTimeout1s、SpatialBasisTolerance1e-7、MaxBackendWorkers1、MaxHalconParallelism1、MaxPointBlockSize4096、MaxRuns65536。Hash按原`RG-HOST-PROFILE-1`字段顺序/InvariantCulture/R/UTF8/末换行算法重算，不能沿用Frame变化前hash；只用于synthetic。
3. `new RG.RoiGeometryFactory().Open(new RoiOpenRequest("met-roi-open-a","met-roi-session-a",snapshot,roiProfile,原剩余MonotonicDeadline),null,operationToken)`；Errors.Empty/Core非null方继续，借用只读core不Apply/Preview。Root已预留后构造 `RG.Serialization.IRoiGeometryCodec roiCodec = new Asun.Modules.RoiGeometry.Serialization.RoiGeometryCodec();`，并原样传BridgePorts；公开入口按[ROI0.4.3 §8.2/A.3](../roi-geometry/DEVELOPMENT-GUIDE.md#a3-interaction-01codec-01spatial-01-公开端口)。构造零IO/Task/线程/native/隐含Core，无Close/Drain/Dispose入口；Encode/Decode是有界同步纯值，参数/期限/token和完整envelope摘要沿§20.3/上游原规约。若Host将调用放进Task，Root强持原Task/输入/配置/Codec至实际退出，不能把观察到期当Codec已返回；构造实例不授持久化或物理资格。
4. CG图只有Frame.Ref(`roi-mm`,1,内容hash)、Dimension2、Axes=[(`X`,PositiveX,basisA),(`Y`,PositiveY,basisA)]、Handedness.Oriented2D、Millimetre、PixelConvention.None、Box2((-100,-100),(100,100),Closed)、SourceRef=synthetic-roi-mm-frame；Graph=(自身Ref,[Frame],Edges.Empty)，FrameRules.AxisScales=[1,1]。CoordinateReadPlan.Source=Target=该Frame.Ref、ExplicitPath.Steps.Empty；整Polygon2Value映射并核CG终态，避免仅点落域冒填充域有效。SourceDeclaration=(`met-roi-polygon-a`,1,CG Frame转metrology AssetRef,null,此Map,RoiSnapshotInput(snapshot,profile,[`n1`],PolygonGeometry))；BridgePorts=(core,roiCodec,null,null,自有CG,null)。
5. definition=`new MetrologyDefinition(Method.Area,Dimension.D2,Selector.Unique,null,null,AngleMode.Directed2D,VolumeMode.NetMagnitude,new NumericPolicy(1e-9,Unit.Mm,1e-9,1e-9),null,null,null,ImmutableArray<P3>.Empty,null,null)`；profile=`new MethodProfile("0.2","Area/1",definition,null,null,null,SurfaceSign.Unsigned,false,budget)`。Prepare=(版本,key,Engineering,budget,[source],[profile])。Measure请求=(key,Engineering,Prepared.ProfileReferences[0],[InputOperand("subject",Subject,Prepared.Sources[0].Source)],Prepared.Coordinates,definition,budget)。GeometryBackend解析面积12mm²，原Ring/vertex顺序及原完整Codec envelope hash保留；不称物理面积验收。
6. revision2独立bridge/service作同源HalconBackend Unsupported拒绝case；revision3将ROI Frame明确改ColumnRowPixelCenters/Pixel并重算Profile，尝试PolygonGeometry→PixelDiagnostic，预期软件坐标能力Unsupported，零CG/native执行；不能改成非法CG Cartesian Pixel帧获得成功。原生Region/Contour/image成功沿§12/13原fixture另验，不能把本解析Polygon成功当M3 native通过。borrowed ROI迟到lease反例沿§20.4，由原Host持lease，桥不得先Dispose；公开真实lease fixture仍需HALCON-01装配门，不使用伪raw handle。

**Host-B / SurfaceReferenceReplayHost**（Engineering，SD/C5公开值、显式CG单位链、RS既有P结果）：

1. Key=(`3b6ee6df-8b27-43e7-8ee8-f2ee342a798b`,1)。Source使用[SD §9.2](../surface-data/DEVELOPMENT-GUIDE.md#92-host-bxyz已有mesh输入诊断)的mesh-B raw bytes与[C5 §15.7 Host-P](../surface-data/DEVELOPMENT-GUIDE.md#157-两个完整无ui构造与固定数据)新carrier完整Descriptor，按P原实际Origin/贡献buffer两scope字典固定。本case只用P carrier：XYZ um=(0,0,0)/(1000,0,0)/(0,1000,-100)/(1000,1000,0)，faces=(0,1,2)/(2,1,3)，Root Int64=[9007199254740993,9007199254740995,9007199254740997,9007199254740999]保持原值，实际Origin=[0,1,1,1]。CSR offsets=[0,1,3,5,7]、States=[1,1,1,1]、MethodIds=[0,1,1,1]、slots=[0,1,2,1,2,1,2]、ordinals=[0,9007199254740993,9007199254740995,9007199254740995,9007199254740997,9007199254740997,9007199254740999]、weights=[1,.25,.75,.5,.5,0,1]；父Frame/Snapshot/Methods沿P全部字段，不用Q表或旧全Observed descriptor。
2. 自有`SD.SurfaceDataFactory.Create(new SurfaceOptions(0,4,4,32,16,16,2,131072,1s),new SurfacePorts(原只读Source,null,TimeProvider.System))`；C5 `SC.SurfaceContributionFactory.Create(new ContributionOptions(0,1,4,4,8,2,1048576,1s),new ContributionPorts(原P只读Source,TimeProvider.System))`，公开Ports实际字段按SD §3/C5 §15.2。Source字典保存完整expected Descriptor和每buffer bytes/hash，Open深比较后才回session，ReadCarrierOriginIntoAsync只取P Origin scope，父源不自动打开。 两Factory都返回错误信封：Errors.Empty且SD.FactoryResult.Service/ContributionFactoryResult.Reader非null才登记实例继续；不能把FactoryResult直接当service或用null跳过cleanup。
3. vertices=`SurfaceReadRequest(carrier,SurfaceRange(Vertex,Ordinal,0,4,null,false),[X,Y,Z原FieldId],PreserveAll,true,carrier.Frame,null,new ResourceBudget("synthetic-b",1,16,4096,65536,4,16,1s),1)`；faces同descriptor/Face/Ordinal/0/2/null/false、FieldIds=[TriangleIndices原Id]、PreserveAll/false/TargetFrame=null/Transform=null、同budget/generation。contributions=`ContributionReadRequest(P,0,4,false,2,4,2,7,new ResourceBudget("synthetic-p",1,4,4096,262144,2,16,1s),1)`。SD未被要求跨单位读，C5实际Origin必须和SD四row一致。只读当前carrier，不从父权重重算坐标。
4. 自有CG图有三帧：U=(P.Frame.Id,P.Frame.Revision,Micrometre)，M=(`synthetic-meter`,1,Metre)，T=(`met-mm-b`,1,Millimetre)。均Dimension3/Right3D、Axes=[X/PositiveX,Y/PositiveY,Z/PositiveZ]同synthetic基准、PixelConvention.None、SourceRef具名synthetic；各Closed Box3域为U=[-10000,10000]³、M=[-10,10]³、T=[-10000,10000]³。FrameRules.AxisScales为U=[1000,1000,1000]、M=[.001,.001,.001]、T=[1,1,1]；全部BoundaryGuard0/MaximumCoordinateMagnitude1e6。两edge使用CG.Affine3Model/Matrix(4,4,Values)，完整row-major Values分别为U→T `[.001,0,0,0, 0,.001,0,0, 0,0,.001,0, 0,0,0,1]`、M→T `[1000,0,0,0, 0,1000,0,0, 0,0,1000,0, 0,0,0,1]`；ValidDomain=各自source域、Inverse=(Forbidden,null,null,null)、SourceRef合成单位边证据、ParameterCovariance/QualityRef=null。ParameterOrder按已接收[CG0.3.5 §4.3.1–2](../coordinate-geometry/DEVELOPMENT-GUIDE.md#432-affine3逐项索引host-b软件单位边与一致断言)的12项精确构造如下；九系数Name=`m11,m12,m13,m21,m22,m23,m31,m32,m33`对应Values索引`0,1,2,4,5,6,8,9,10`，偏移Name=`tx,ty,tz`对应索引`3,7,11`，齐次末行不纳入。两条边各绑定自己的原Edge.Ref，Graph Frames=[U,M,T]、Edges=[U-T,M-T]、Numeric沿共同值，Graph/Frame/Edge/Policy真实内容hash按CG规约；两个Source各用ExplicitPath([对应edge/Forward])。名称表/Scale装配欠账已关闭，不再阻断软件literal绑定；本基础桥指导已获主控限定内容接收，真实编译/执行门保持。
5. revision1 sources=[point,reference]：point=(`met-surface-points-b`,1,T,null,U→T Map,SurfaceValueInput(carrier,vertices,null,contributions,PointGeometry))，冻结四mm Point3且完整trace四行/七父项/零权；reference=(`met-reference-plane-b`,1,T,null,M→T Map,ReferenceValueInput(RS-V01 Source,Result,ResolvedProfile,PlaneGeometry))。P父值没有打开，因此只能追溯，不能授WholeCellSupport；SD unknown/invalid row按§20.3保状态、不填有限0，当前四点均Valid但三个Interpolated不改Observed。
6. RS-V01先独立准备：Source=(`v01`,1,`synthetic-meter`,Meter,三有效Point3 (0,0,2)/(1,0,2)/(0,1,2),[SupportCell(0,0,1,2,true,"synthetic-v01")],现算ContentSha256,`synthetic-v01`,`synthetic-v01`)；R DomainId=R/Revision1/SourceIndices[0,1,2]/CellIds[0]/现算DomainSha256；X/C/T=null。Chart=(原点0 Meter,U+X,V+Y,HeightAxis+Z)、ReferenceDirection+Z、Overlap=false、TargetMode.SignedAxisHeight。Profile=(PlaneTls,`test-method-v01`,"1",Robust(None,null,3,0),Numerical(.01,1e-6,1e6,.1,2),Support(3,1,null,2,0,true,false,1,null,null,1e-10),现算ParameterSha256)，ResolvedProfile及FrozenProfileReference均按公开Identity算。RequestId=met-rs-v01-b、CorrelationId=met-bridge-b、ContractVersion=rs-api-0.1、Budget=(min(1s,原剩余deadline),262144)；所有Profile算法字段沿原V01，没有为计量host改算法。自有`RS.ReferenceSurfaceFactory.Create(new ReferenceSurfaceEngineOptions(1,0,16,16,16,1048576))`，原ExecuteAsync先登记；只有Succeeded/释放和全部Identity相符才交桥。也可消费原已封存同值，但不能把新Result绑定原hash。真实P为n=+Z,d=-2m,Origin=(1/3,1/3,2)m；先解码原Meter，再CG ×1000到T mm，不能换Frame标签或把它当z=0平面。
7. revision1 definition完整沿Host-A14参数形状，仅Method.HeightSummary、Dimension.D3、MethodVersion.HeightSummary/1；Profile其余字段仍null/Unsigned/false，Numeric mm，budget相同。Prepare=(版本,key,Engineering,budget,[point,reference],[该profile])；Measure operands依次("subject",Subject,Prepared.Sources[0].Source)、("reference",Reference,Prepared.Sources[1].Source)，其Coordinates及ProfileReferences[0]均直接取Prepared，Reference不是Definition额外字段。GeometryBackend按原§12.2 signed residual等权定义得MeanHeight=-2000.025mm、MinHeight=-2000.1mm、MaxHeight=-2000mm（公差沿Numeric）；这是本桥合成算例，不改原Golden，更不是有效支撑/工艺结果。本桥未调用RS Evaluate授用途支撑，Engineering仅消费显式工程平面；不能仅由几何包围报告RS Supported/物理资格。
8. revision2 sources=[mesh]独立bridge/service：mesh=(`met-surface-mesh-b`,1,T,null,U→T Map,SurfaceValueInput(carrier,vertices,faces,contributions,Mesh))；profile完整形状仅Method.SurfaceArea/D3/SurfaceArea/1，只有一个subject operand，Domain=null，禁止拿Hull/闭合门生成Volume成功。配置HalconBackend Methods.Empty时Runtime Unsupported/Unsupported，零Start/native。此case验证只读mesh装配与包络拒绝；native SurfaceArea成功仍由N-Envelope和真实执行关闭。若要减少重复读须另冻明确租约复用合同，本版不隐式跨revisioncache。
9. 关闭顺序按§20.4；metrology归还值租约之后bridge才Closed，自有SD/C5在所有Completion退出后Close，CG只用StopAndDrain，无Dispose接口；RS原Execute/Resolve/profile释放后独立Close/Dispose。原Prepare晚回只进原Key，关门后不启动业务、不把旧lease交新service。多次读取OriginalTasks计槽，不因Root已保错误而提前释放依赖。

**Host-B 第4步的完整ParameterOrder消费**（两条原Edge分别赋入同内容的不可变12项，不共享参数Owner）：

```csharp
var parameterOrder = ImmutableArray.Create(
    new CG.ModelParameter("m11", CG.ParameterUnit.TargetPerSource, 1d),
    new CG.ModelParameter("m12", CG.ParameterUnit.TargetPerSource, 1d),
    new CG.ModelParameter("m13", CG.ParameterUnit.TargetPerSource, 1d),
    new CG.ModelParameter("m21", CG.ParameterUnit.TargetPerSource, 1d),
    new CG.ModelParameter("m22", CG.ParameterUnit.TargetPerSource, 1d),
    new CG.ModelParameter("m23", CG.ParameterUnit.TargetPerSource, 1d),
    new CG.ModelParameter("m31", CG.ParameterUnit.TargetPerSource, 1d),
    new CG.ModelParameter("m32", CG.ParameterUnit.TargetPerSource, 1d),
    new CG.ModelParameter("m33", CG.ParameterUnit.TargetPerSource, 1d),
    new CG.ModelParameter("tx", CG.ParameterUnit.TargetLength, 1d),
    new CG.ModelParameter("ty", CG.ParameterUnit.TargetLength, 1d),
    new CG.ModelParameter("tz", CG.ParameterUnit.TargetLength, 1d));
```

前九项单位分别为U→T的mm/μm与M→T的mm/m，后三项均为mm；Scale=1是本Host已冻结的软件数值配置，不是单位比例、矩阵系数、标准差或FrameNumericRule.AxisScales，不因零系数省项或改Scale=0，也不乘第二次。Name没有`parameters.`前缀；本Host无协方差，不创建VariableKey。以后有协方差时按CG原规约，Owner=各自Edge.Ref、ScalarPath=`"parameters."+Name`、ParameterUnit/Scale逐项同原参数、GeometryUnit=null，不使用offset.x/m14等别名。

本次定向装配自审按CG原表独立逐项核12项Name/Unit/Scale与Values索引：线性块row-major九项再偏移3/7/11，固定末行排除；`.001`/1000沿原binary64 literal，完整Frame/Edge/Graph/Policy身份仍用原编码。U四点与RS米平面的mm预期保持Host-B原第5～7步，不改原数学Golden；交换系数名/漏零项/错单位/非正Scale沿CG原拒绝断言，不另造测试文件或算法。Host-A Codec构造按ROI已接收纯值声明，完整envelope hash与payloadHash边界保持§20.3，Codec无释放接口，原同步工作实际退出后才退Root持有。

ROI Codec创建与CG参数名称两处软件装配文档欠账均已接收并在本节消费，已移除其待补表；它们不再是Host准备阻断。M3/M4公开装配与本基础只读桥指导已获主控限定内容接收，不授真实native/物理Ready。上游各fixture唯一正文仍为完整字段/bytes权威，入口链接随原章节；不复制另一个测试或报告权威。case10s/suite120s/外180s、原Task/lease/独立cleanup与§16原基线保持；0剩余只登记待清理，不无界await。真实NativeEnvelope、公开程序集消费编译、Golden/运行/性能/物理及产品接线仍分别留门，不能覆盖现在已闭合的软件装配。

### 20.6 定向反例、可选UI影响、测点与两轮自审

| case | 可判定规格断言 |
|---|---|
| BR-01 真实类型/身份 | 两Host各自factory/ports/key，payload hash与原上游hash分开；Profile/input错ref拒绝；没有latest/全局状态，不修改上游bytes/Origin/CG图/RS模型/ROI文档 |
| BR-02 单位/frame | um→mm只显式CG边一次；SD源单位/RS模型米解码正确；Pixel ColumnRow→Cartesian不换标签，按本桥能力Unsupported；错单位/图域/轴向或重复换算拒绝，Engineering不造物理资格 |
| BR-03 C5 Origin/父 | XYZ任一实际Origin与C5 CarrierOrigin不等拒Conflict；Unknown/Unsupported行不造父；零权保留、父ordinal>2^53精确保留；父Source未读不重算carrier或授WholeCellSupport |
| BR-04 ROI租约迟到 | Materialize原Task晚回，根预留lease；同ID Query、不第二调用；先Materialize真实退出、Host lease.Drain/Dispose后才清Host槽；TemporaryResourcesReleased不当lease全部Released |
| BR-05 RS/坐标迟到 | Resolve晚profilelease只释放一次；CG Wait超时不等CG Completed；原Query/Cancel ID与mapped frame/path/InputHash一致，旧revision不提交新请求 |
| BR-06 Mesh/域缺 | PointGeometry任一Invalid/Unknown拒绝，不能滤点后报整量；无效面引用顶点拒完整mesh；Grid不造对角/洞不补；仅ROI polygon无分解时基础面积可算、连续域请求欠证拒绝；RS hull非支持，P/H/Q路由不混 |
| BR-07 N-Envelope | Empty/mismatch/shape越界在native工作前拒绝；proof预留账与working-set测量分开；未知native bytes字段不填0；Native Start/clear/callback抛错保原receipt、故障不覆盖业务 |
| BR-08 Close/根 | bridge valuelease仍被service用时不Closed；DisposeStarted同步抛错也单飞；依赖未归还时后续仅登记、不dispose。业务/清理错误各保存；已确认归还失败case退槽仍非零；transfer无ack源保持 |
| BR-09 只读/UI | 0次ROI Apply/Preview/Commit、SD原值修改、CG选新链、RS Execute（本桥消费已存结果）、Store/设备动作。Host-B为生成RS fixture的Execute独立准备，不是桥重拟合；没有新增UI切换/隐藏窗口 |

计量模块本身无UI，本次仅影响IM-065工作台对BridgePreparedSource/Trace/Scope/Unknown的投影：显示原source/frame/unit/Origin与C5贡献证据来源，Engineering/PixelDiagnostic不得投影“已标定”，迟到代次拒旧结果。可选UI不拷算法、不控制native Owner；本轮不写工作台指导/页面，由原Owner接收具体映射，真实WPF资格不提升。

测点增加：Prepare接纳→ROI Validate/Materialize退出→SD Vertex/Face Completion→C5 Origin+完整hash/Completion→CG Submit/Query Confirmed→RS Resolve/lease归还→编译hash/值Ready→service native预留/各NativeStage→execution Released→valuelease归还→bridge Closed→各Host-owned上游Closed/Confirmed。Root驻留峰值包含所有上游同时预约/桥copy/trace/native预留，不把不同包的上限当互斥峰值。客户吞吐/真实native上界/working-set和P50/P95/P99/n均NotEvaluated，沿§16.1分超时/删失/错误口径；不编native性能数。

两轮有限自审已完成：第一轮按上游公开声明核类型/Factory/namespace、摘要、实际Origin/Int64父项/零权及单位/坐标/RS模型，修正Codec摘要/无依据构造名、Pixel轴冲突、整几何域消费、RS米解码及无效点过滤；该轮记录的ROI Codec/CG参数装配欠账已由原Owner补齐并获主控接收，现按§20.5精确消费，不再列为待补。第二轮核factory前根、原Task/lease、关闭依赖、单飞/迟到/独立cleanup与10/120/180预算，修正trace持租约、自等待和零期限启动。已接收六项算法/编码/Golden与§16.2–3基线不扩审。新增BR反例留原HostTests分组，本轮没有执行它们。本节公开装配与基础只读桥指导已获主控限定内容接收；剩余门为真实公开程序集引用/编译(E-Build)、native各Method资源包络/测量(N-Envelope)、连续场/ROI分解/物理Qualification及工作台产品映射；门分别限受影响slice，不能覆盖已经存在的公开软件契约。真实C#、HALCON/AsunImage、WPF、Golden/Replay、性能/MSA/HIL/现场均未执行。


### 20.7 原分辨率图像/RegionRuns公开读桥（I1，目标增量）

§20.2基础几何桥的RegionRuns/Pixel轴Unsupported保持；图像量测通过本独立具名读桥保存原row/column离散域，并仅映射实际边点。它不把RegionRuns转成Cartesian Polygon，也不扩充既有BridgeInput union。唯一落点为Asun.Metrology.Halcon工程，另引用IM-006 Core/Resources、IM-024 Core及IM-007公开契约；仍无WPF/DevExpress依赖。IFR=Asun.Modules.ImageFrame.Resources；RG/CG别名沿§20.2。

```csharp
public sealed record ImageReadBridgeRequest(OperationKey Key, Scope Scope,
    IFR.IFrameLease Image, int LocalPlaneIndex, AssetRef SourceFrame,
    AssetRef SourceEvidence, RG.IRoiGeometryLease Roi,
    RG.RoiMaterializationRequest Materialization, RG.RoiFrame RoiFrame,
    CoordinateReadPlan Map, ImmutableArray<MethodProfile> Profiles);
public sealed record ImageReadTrace(IFR.FrameKey SourceKey,
    Guid ImageLeaseId, IFR.PixelWindow ActualWindow,
    Asun.Modules.ImageFrame.Core.ManagedFrameLayout OriginalLayout,
    ImmutableArray<IFR.PlaneMetadata> OriginalMetadata,
    ImmutableArray<int> SourcePlaneIndices, RG.RoiGeometryLeaseInfo RoiInfo,
    ImmutableArray<RG.RoiRun> OriginalRuns, AssetRef SourceEvidence,
    CG.MappedResult SupportMap);
public sealed record ImageReadPrepared(SourceRef Image, SourceRef SearchRoi,
    CoordinateBinding Coordinates, ImmutableArray<AssetRef> Profiles,
    ImageReadTrace Trace);
public interface IImageMetrologyReadBridge : IAsyncDisposable {
    IMetrologyInputReader Reader { get; }
    IMetrologyCoordinatePort CoordinatePort { get; }
    ImmutableArray<CG.MappedResult> GetCoordinateResults();
    ValueTask<ImageReadPrepared> PrepareAsync(CancellationToken operationCancellation);
    BridgeSnapshot GetSnapshot();
    ValueTask<BridgeCloseReceipt> CloseAsync(TimeSpan observationLimit,
        CancellationToken waitCancellation);
}
public static class ImageMetrologyReadBridgeFactory {
    public static IImageMetrologyReadBridge Create(ImageReadBridgeRequest request,
        BridgeOptions options, CG.ICoordinateGeometryService borrowedCoordinates);
}
```

Image/Roi均是宿主借用的原真实lease，I1不Dispose它们；根在factory前持两lease、CG服务、原请求和预算。Create仅深冻结值/校验，零CopyRow/Materialize/CG/native。Scope首版Engineering，CalibratedPhysical返回Unqualified；PixelDiagnostic用§13既有原端口路线，本桥返回Unsupported，保持CG Pixel帧限定。Profiles仅本版支持ImageEdgePair2/ImagePrimitive2，同源/同坐标，各ExecutionBudget逐值相等且取其与BridgeOptions交集计账；MaximumSources至少2、原Task/lease名额必须覆盖图/ROI/CG同时持有峰值，完整原Validator与§13参数检查。SourceFrame与Map.Source原AssetRef全等，源为CG Pixel/ImageColumnRow，目标为D2 Oriented2D/右X上Y/Millimetre；显式路径只有限Affine2/Identity组合，含Projective/局部场/CameraRead的本桥Unsupported，不能点采样冒全扫描域资格。借用CG核原Graph/Path/Policy，不选择另一链。 本节<key>字符串固定为OperationId的N格式加.r及RequestRevision的Invariant十进制，不用对象ToString/Culture/当前UI身份。

宿主取图固定步骤：受信冻结FrameDescriptor/SourceEvidence→IFR.IFrameService.ReadAsync原RequestId（Intent=ExactSamples、Boundary=RejectMissingSupport、PlaneIndices恰一项、Window恰level0全源尺寸、Halo=0）→原QueryOperation(ServiceEpoch,RequestId)为Completed且OperationResourcesReleased、Slice非null后传入。服务读取Task/lease归宿主根，不调用Retire或Close共享frame服务。由于IFrameLease不公开FrameDescriptor，Trace保SourceKey/SourcePlaneIndices/ActualWindow/原lease.Layout/Metadata及原SourceEvidence，不猜不存在的Descriptor getter；原descriptor由宿主原证据保存，不拼造新值。工厂再核CoreWindow=ActualWindow=(0,0,Width,Height)、SourcePlaneIndices对应原read、本版LocalPlaneIndex=0、Layout/Metadata恰单通道UInt8/PlaneRole.Intensity、小端/Scale1/Bias0，Metadata.Unit字符串原样留宿主SourceEvidence，仅作为原强度单位声明，不转换物理坐标；其它位深/Color/LOD/crop/halo本I1 Unsupported。完整原图过大则BudgetExceeded，不能先铺全图或自动降LOD；将来tile量测须冻结另一切片，当前显示tile不进入测量。

Prepare唯一原Task：先保存原读取与materialize槽/copy额度，调用Image.TryOpenReadScope；scope.CopyRow(0,y,destination)按逻辑行复制Width bytes，不读padding或指针，不跨await存Span。一个scope串行读，逐行检查停止/总预算；scope.Dispose必须同步CopyRow真实退出后调用。新ImagePayload Width/Height原值、RowStrideBytes=Width、PixelType.Byte、Buffer为独有冻结byte[]；ValidPixels取Layout.Domain与Metadata.ValidDomain的精确交集，RowSegments的[StartXInclusive,EndXExclusive)转本模块[StartColumn,EndColumn]仅end减1，Full为每行0..Width−1，Empty不伪全域。域外填0仅规范copy，不变valid。byte预算含原lease.Allocations受控借用、width×height目的、单行scratch、两份runs、全部trace、CG请求/结果和profile；共享原allocation按本根AllocationId去重，不能把消费者logical账当RSS。Options.MaximumRetainedBytes/MaxInputElements/输出数不足在copy前拒；无并行行scope绕限。

ROI Materialize原ID/原期限只调用一次，IsTerminal/ResourcesReleased且Errors.Empty才采用完整Runs；Info.Representation须RasterizedRegion、Unit=Pixel、FrameId=SourceFrame.Id/原RoiFrame.Id，RoiFrame.Axes=ColumnRowPixelCenters。Info.Grid非null、Width/Height等原图、Origin=(0,0)、StepX=StepY=1；不满足Unsupported，不重采样/旋转/缩放。每RoiRun保ObjectIndex/Row/Start/End，合法范围全在原图，不裁越界；原ObjectIndex层保Trace。SearchRoi是各object材料集合的显式并集：按row/start排序，仅合并重叠或相邻闭整数区间，同像素只一次，这是离散搜索mask编译，不宣称连续面积/拓扑/物理域资格；没有runs合法Empty，量测仍InsufficientSupport而非0宽。Vector输出不自动Rasterize，必须宿主已按ROI公开HALCON-01显式请求得lease，避免另一套栅格化算法。所有实际扫描及插值margin在原mask与valid域内按§13检查，不能用reduce_domain补证据。

Copy与Materialize都退出且scope真归还才Prepared；晚到/异常原Task/lease仍根保，错绑定返回MetrologyPortException既有码，零partial Prepared。Roi/Image borrowed lease仍由宿主最后归还。Image/SearchRoi是新的计量copy内容：SourceRef.Content Id分别image-copy.<key>/roi-runs.<key>、Revision1、Sha256分别HashSource(ImagePayload/RegionPayload)，Frame=原SourceFrame、Calibration=null、CoordinateUnit=Pixel；原SourceKey/lease/source证据/hash不被新hash替代。profile引用依§20.2同序hash规则，新profile需原§13完整值。Reader Acquire按精确引用返回自有值lease，后续无重新读图或materialize；值lease归还与Close屏障沿§20.4。

Prepare在原runs/valid域冻结后进行一次**显式整ROI支撑检查**：每个编译PixelRun构造闭方形支撑矩形outer=[(start−0.5,row−0.5),(end+0.5,row−0.5),(end+0.5,row+0.5),(start−0.5,row+0.5)]、Holes.Empty的CG.Polygon2Value，一run一项，不合成有接触的多polygon环、不用四个全局极值点代域。有效mask与插值扫描检查仍§13，不通过不启动native。NFC batch Id=image-support.<key>、Revision1、Frame=Map.Source、Uncertainty=new CG.NoCovariance()，batch.Ref.Hash按CG §4.2 coordinate-core-values-v1原值规约与自Ref排除规则生成。GeometryRequest("0.2",met-image.<Guid:N>.r<rev>.n0,MapWork(Graph,Source,Target,ExplicitPath,batch,Numeric),剩余PrepareLimit)；原SubmitAsync/WaitAsync/QueryAsync/CancelAsync及CG.State=Completed/Drain=Confirmed/字段hash核沿§20.3，原支持几何全域由CG核验，不新增本模块映射算法。任何run闭支撑跨CG源有效域/洞/目标域拒绝，Empty runs直接InsufficientSupport不创建假empty成功CG请求；所有run数/顶点/复制/CG响应受BridgeOptions和CG Numeric/RuntimeLimits，超限在提交前拒绝。SupportMap保存这一原MappedResult。

CoordinateBinding Source=原SourceFrame、Target=Map.Target、Mapping=AssetRef(Id=met-image-map.<key>,Revision1,Sha256=该原支持检查Admission.InputHash)，Calibration/ApplicabilityReceipt=null；原InputHash已经包含Graph/Policy/Path/batch/原backend，是本次Engineering映射执行身份，不对未公开Graph/Path复合类型猜新hash。Source/Image/SearchRoi仍Pixel原内容，不能使用§20.2已编译值identity端口进行第二物理映射。MapAsync输入sourceUnit只Pixel、P3.Z=0、(X=column,Y=row)，提交CG.Point2Value(new CG.Point2(X,Y))原点序；HALCON PixelPoint(Row,Column)只在此调用前转换P3(Column,Row,0)，不换frame标签。每次Map用met-image.<Guid:N>.r<rev>.n<正递增seq>独立原请求ID，batch/ref/预算/canonical及原Task流程同上；返回MappedPoints恰原点数/序、Unit.Mm、Kind.Pointwise、Coefficients.Empty、Receipt=AssetRef(原CG RequestId,1,原MappedResult.InputHash)。CG MappedResult不公开组合矩阵，本桥不反推/私算Affine coefficients；这些image方法只需要实际边点映射，不拿Pointwise支持几何方向/normal/连续曲线。ValidateBinding只接受Prepare返回的精确binding/Engineering/预算并确认原支持检查与借用service.BackendRef仍相符，返回Binding.Mapping；actual Map仍逐点检查原CG有效域，源资格变化由宿主撤销当前工具，不拿过去支持检查升物理资格。

每次CG返回的完整MappedResult由bridge有界保留，新增公开纯值getter `ImmutableArray<CG.MappedResult> GetCoordinateResults()`（IImageMetrologyReadBridge成员）用于宿主保存原回执证据，不持Task/lease或触发新读；记录与原mapping任务共同计MaximumOriginalTasks/MaximumRetainedBytes，不逐出未归还结果换额度。Reader引用只能由对应Profiles/Prepared源构造合法新request；CoordinatePort收到其它binding/维度/sourceUnit即InvalidRequest/CoordinateMismatch。CG晚退原key/requestId/Task仍bridge根保留，Close必须其原退出与本自有值lease归还确认，不Stop借用CG；源Frame/Graph/Policy/hash/backend变换不能复用旧Prepared。

两Host分别按本节取自己的原Byte全图/ROI native runs/显式CG像素→mm Affine链→Prepare→§11 service(Reader,CoordinatePort,各自HalconBackend)→ImageEdgePair2或受支持Primitive→释放服务execution/值lease→bridge Closed→Host归还ROI lease原Drain/Dispose及IFR lease.ReleaseAsync→关闭自己拥有的上游。IFR.Release需LeaseClosed/Drain=Drained且本lease scope已退；StorageReleased=false可因发布/别consumer仍持有，不能为等全allocation析构Retire另一Owner源。测试软件图Width32/Height32/单Byte，CG显式diag(0.5,-0.25,1)，源全闭像素域[-0.5,31.5]²、目标域[-0.25,15.75]×[-7.875,0.125]mm，原Graph/Edge/Policy来源仅Synthetic，原ROI Grid.Origin=(0,0)/StepX=StepY=1，原冻结rect中心(16,16)/half lengths(8,4)、sigma1/threshold20，全部是合成fixture，不是客户默认； native只有N-Envelope真实覆盖时启动，Empty时只验证Unsupported/零Start。I1反例必须包含crop/LOD拒、三plane/UInt16拒、source frame错、非单位ROI grid、两object重叠mask、bicubic边距缺、copy停滞/原Task迟到、ReleaseUnknown与CG晚退；均复用HostTests/§16.3，不创建或声称已跑真实图像测试。

### 20.8 surface-data 0.6.0-prep H与metadata codec消费增量

本模块现有SurfaceValueInput/连续CPU读取及C1–C5来源链依然消费SD API0.4/C5 API0.1，**不调用SurfaceImageLibFactory/ISurfaceImageLibPort**。HalconBackend按§13/14创建自己的请求私有ObjectModel3D，不能把上游H输出变成它的native句柄或漏算双份内存。SD指导新H不是本CPU桥前置依赖，也不改变已接收算法/原Source/State/Origin/Int64 root/支持资格。若宿主明确把SD H纳入输入预处理，必须在它自己的根先执行SD §17原协议并保存原回执，未完成不得传给计量reader。

H具体消费由用途Owner冻结SD.NativeAccuracyPolicy(Id,Revision,MaxCoordinateRoundTripError)，误差单位等原input.Unit、有限≥0，0要求实际精确往返；不从本模块Numeric/公差比例反推。SD.ImageLib.SurfaceImageLibFactory.Create(adapterBudget,time,runtime)三参数重载，runtime=SD.NativeRuntimeBinding(绝对WorkerExecutable、真实WorkerSha256、真实AsunImageSha256、WorkerCommitLimitBytes、MaxWireBytes、Accuracy)。固定真实发布包hash不是许可证/兼容审核。H1 double→m→nearest-even float32→gen_image1 real(4bytes)→读回源单位并逐XYZ误差核，不能写“无损double高度”；H2 double tuple仍核单位往返，H3 slot必须等CPU原坐标闭区间集合。超差/边界集合不同Integrity，无夹紧/补slot/覆盖原值。输出Positions为CPU原input副本，Invalid/Unknown的native0仅排除domain，不变有效。H只提供其往返验证，不证明本native fit/volume精度或CalibratedPhysical。

H一个请求一个Windows隔离worker/Job commit限额，最多1 active，原worker/pipe/process/句柄全部实际退出才释放；Kill请求不当ACK。父CPU账M+256N+24R+2MaxWireBytes+16384及每array64，另WorkerCommitLimitBytes纳Host与adapter/request交集；本HalconBackend资源账同时保留，不能认为H worker预算包含后续本地model。绑定/精度/工作进程失败只阻SD H路线；native adapter真实运行/资源proof仍本模块N-Envelope。SD两参数Create不能用于隐式实际runtime绑定；H原双Host软件精度示例非本模块客户默认，本轮不重新复算H/C1–C5上游向量。

原两Host直接CPU/frozen reader不保存SD descriptor，因此**不新增metadata codec或Storage依赖**。当BatchReplayHost显式选择StoredSurface来源（已有获批离线用途）时，唯一持久描述格式采用SD §18 Core SurfaceSnapshotMetadata/SurfaceMetadataLimits/SurfaceMetadataCodec.Encode/Decode；仅持descriptor/贡献关系，原buffers/padding bytes分别保留，不能序列化Task/lease/native/回执或生产状态。Decode有界完整检查、失败无半metadata，编码保SD原-0/参数序/Int64，不重用本§15的-0归一规则改上游bytes。

实际Stored模式装配严格沿SD §16/18：SDC=Asun.Platform.StorageDatabase.Contracts；创建SD.Adapters.SurfaceAdaptersFactory.CreateMetadataFormatValidator(SDC.VersionRef,limits)及CreateRawBufferFormatValidator(format,maxBufferBytes,readChunkBytes)，Format.Id分别surface-metadata/surface-raw-buffer、Revision1、Hash由格式发布Owner实际包提供，**完整VersionRef准确加入ResolvedStorageConfiguration.FormatValidators**，不能只注册Id或拿metadata信封hash当format包hash。Host提供可信scope+BufferId→原ObjectRef表，C5 carrier/parent同名Id在不同scope仍分开；漏、多、错hash拒绝。trusted manifest ObjectRef→原IFileObjectStore有界读信封/真实读lease Release→Decode/Validate→原StoredSource/StoredContributionSource bindings→SD/C5 Plan/Start原Completion→§20.3计量只读桥→结果投影。Storage技术hash/授权归IM-066，描述/原buffer/父snapshot绑定归发布Owner，计量不查私表或写新事实。

未知format/schema只保原bytes+旧manifest/旧格式包/旧适配器回退，新请求用原版本闭包重新Open；不迁写旧bytes、不复活旧Task/Complete/ProductionAccepted。断连、权限变化、缺buffer/hash错按原Owner错误并保根，不能以空surface成功兜底。本Host只消费上游接口，不把Storage API候选补猜进metrology Core。定向验收是在原HostTests Stored消费分组验证完整格式注册拒错Hash、双scope同Id隔离、H超差/边界拒绝与原CPU值保持、lease迟到释放；上游SD Golden577bytes/完整hash已有效，本轮不重复生成或把未执行Store/native当通过。

## 21. 当前架构完整范围的文档准备结论（2026-10-11）

### 21.1 本永久原会话的范围结论与唯一落点

**当前批准的有限能力及完整适配/恢复/参数推荐范围，可由本模块决定的软件契约与处理步骤已补齐；结论是文档准备完成。** 本结论不等待总控内容审核，不扩大已接收ModuleCoreImplementationReady范围、不授权代码、不把真实数据/运行/计量门关闭。R1/R2/I1为本轮新增目标规格，尚未实现/编译；基础桥和原六项接收保留。普通实现者按下表定位唯一章节，不能仅按Core或最近一次增量报告整模块完成。

| 完整能力/使用链 | 唯一实施位置 | 本版确定限制与Owner |
|---|---|---|
| 2D/3D点、线/段、角、圆/弧/矩形、球/柱具名尺寸 | §11/12.0–1、§19.4 GeometryMeasure | 明确有向/无向、有限/无限、单位；不接产品孔/针/焊盘语义 |
| 边缘对、图像line/circle/rectangle、轮廓拟合、3D plane/sphere/cylinder、affine | §12.2/13、§20.1/7 | 固定HALCON26.05主路/参数/支撑/物理边重拟合；图像arc/ellipse、鲁棒plane另方法不开放 |
| 面积/矩、mesh面积/距离、基面/闭合体积 | §12.3/13/14/15 | 原domain/face方向、single-valued、未知域/预算拒绝，不能补洞/自动选mesh对角 |
| 连续有限截面/沿程/轴/层面/方向投影 | §19.2–4/9 | 原typed ContinuousReader、有限域/端点/材料资格；不从显示中心/交点猜工艺关系 |
| 有效域线性积分/正部/连续矩/CDF左逆/Q有理有界归约 | §19.5–9及§20.3连续映射 | C1–C4已有值/算法/编码/向量保持；原存储模型证书不冒物理误差 |
| ROI/image/surface/C5/reference/坐标公开读取 | §20.2–5/7/8 | 基础几何桥/原图runs桥分入口；source/frame/hash/三态/Origin/Int64全部保真，不持私有数据库/native handle |
| 参数推荐、解释、拒识、显式采用 | §13.3–4 | 有限挑战集/完整分母/冻结表/排序、PE Provider精确绑定；无门只比较，生产Profile不自动改 |
| 取消/超时/迟到/关闭/异常/恢复 | §14/16.3/19.3/20.4、R2/I1 | 原Task/key/根预算、独立cleanup/单飞、Unknown保原Owner；无持久跨重启执行恢复，旧未决按宿主原记录未知 |
| 无UI/独立发布/语言/可选工作台/视口 | §10.1/15.3/16/20.6/13.4 | 本模块无UI；结果/建议/错误稳定键三语宿主投影；IM-065/061负责页面/viewport投影，授权由宿主原Owner持有，零设备/质量放行 |
| 离线Stored输入及版本回退 | §15.3/20.8 | 不用存储的Host无依赖；选择Stored时原格式全VersionRef/双scope表、bytes保留、新Open，不复活运行对象 |

连续输入公开装配使用§19.3 IContinuousReader/ContinuousMetrologyService：原surface/ROI/reference用途Owner把其已有单元/Boundary/Classification/WholeCellSupport/Q模型资格映射为§19.2强类型值并保原引用，调用原Validate/HashInput后只读Acquire/Release；数据读取/复制/原Task根及双Host沿§19.9/20.3/16.3。它是已有具名数据能力的消费，不因ROI无Triangulation DTO就让计量程序员自造分解。只有ROI边界且无合法原单元/分解证据时该连续请求准确Unsupported/Unqualified，基础面积仍可运行；这是精确输入/资格不足，不阻断无关Core。

对measurement-workbench/viewport的公开桥是上述Reader/CoordinatePort/请求/结果/Trace/建议Provider，不另提供本模块控件、绘图状态或订阅隐含native ownership。宿主viewport camera/zoom/LOD不进入HashRequest；原edge/Witness/候选ID可投影，旧代次/Unknown/Engineering必须原样展示。IM-061具体显示API由工作台/viewport原Owner实现，本模块无需复制DisplayBridge或以调用隐藏窗口初始化量测。宿主未接真实映射时不能说WPF验证过；不影响无UI消费契约准备。

### 21.2 仍保留的精确执行/外部门

| 门/承担Owner | 必须提供的真实内容 | 只阻断 |
|---|---|---|
| E-Build，metrology实现Owner及上游公开包发布Owner | 实际Contracts/Core/Runtime/Halcon/可选Adapters工程、原程序集引用、公共签名歧义消费编译、M0引用迁移回归 | 相应代码/装配运行；不是依赖安装/授权审核 |
| N-Envelope，metrology native实现与宿主部署Owner | 逐Method/Kind/shape/实际build保守资源上界模型及原Owner证据、真实handles/copy/index/cleanup峰值与负载验证；HALCON未承诺任意输入上界，测得最大值不自动证明包络 | 对应native路线实际启用；无proof仍Empty/0 Start，不阻托管Core |
| R-Replay，样本/用途计量Owner及metrology实验执行Owner | 原分辨率挑战集/独立参考期望/代表反例/适用域，完整试验分母、真实误差/拒识/冷热时延/峰值及认可门 | 该域推荐有效性/效率声明；缺门ComparisonOnly/Abstained，软件排序可验 |
| Continuous support，ROI/surface来源算法与制程/参考用途Owner | 原Boundary/单元/无重叠分解/WholeCellSupport/材料F/B/Us/Uh/Q适用及unknown-bound原证据；坐标/frame/source hash | 依赖该证据的连续/物理请求；不从C5 Exact/三点/convex hull推证书 |
| H-runtime/H-accuracy，SD发布与实际用途Owner | 真worker/package/AsunImage hash及commit/wire限额、源Unit误差Profile、原SD H清理回执 | 宿主明确采用SD H时；本CPU SD/C5桥不依赖 |
| Stored-format，SD格式/IM-066部署与发布Host Owner | 真VersionRef格式包注册、可信manifest/ObjectRef/双scope原buffer表、授权/读lease/耐久回执 | 明确选择Stored的Host；不让普通Core依赖数据库 |
| Physical/uncertainty，标定/计量质量与客户Owner | 真实标准件/光学/环境/误差与不确定度/适用域、MSA、客户验收；本v0.2无定量协方差传播，RequireQuantitativeUncertainty时Unqualified | CalibratedPhysical用途、相关生产资格；不自动放宽工艺公差 |
| Product/UI，IM-065/IM-061及各PG/应用Owner | 原结果/三态/来源/候选/建议投影，真实权限/迟到/1920×1080 WPF/UIA流程、实际提交/工艺Required/公差放行与设备边界 | 对应产品集成及现场验收；metrology无独立WPF页面 |

定量uncertainty、一般曲面法向、非线性Region单元积分、Q正部质心/惯性、光程换算和新图像ellipse几何没有本版获批完整契约，保持明确Unsupported/Unqualified，不借“全范围”增猜测API。误差分量/缺项/适用性拒绝已按§15设计；客户物理验收值不能由架构或本轮软件fixture生成。

### 21.3 本轮有限自审与验证范围

复用M1/M2/C1–C4/§20既有接收、算法、canonical/Golden、自审与研究，不重审上游C1–C5算法。第一视角核完整批准能力→唯一章节、实际源/单位/支撑、R1计划与期望/候选不可改变的门、H1 float32与原值、Stored格式/hash/scope；第二视角核R1完整失败分母/R2 schema/原OperationId/迟到草稿/I1原borrowed lease/实际scope退出/依赖Close、独立cleanup与单飞。对native包络/真实输入不足不伪完成，有限新类型不改已接收v0.2/v0.3算法/原codefence/向量。新增反例均定位原HostTests，未新建测试脚本或执行C#。

本轮校验只核本文结构、引用、原保护区保持及新声明/消费一致性；结构检查通过不是产品PASS。尚未执行实际C#/BCL Exe、HALCON/AsunImage/Golden/Replay、WPF、性能/峰值、MSA/HIL或现场验收。新目标规格可以按用户后续明确代码范围逐片开工评估；本文结论不将R1/R2/I1或整模块自动标ModuleCoreImplementationReady。


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

## 附录 A：现有二维基线 API Contract v0.1

本附录仅记录现有v0.1二维Core公开API，命名空间为`Asun.Metrology.Core`；目标基础v0.2定位§10–18、完整连续v0.3定位§19，不由本附录收窄。类型签名按当前公开源码记录；数学/异常文字是实现约束，不构成对当前代码未覆盖场景的通过声明。未列成员不属于v0.1 API。

### A.1 类型

```csharp
public readonly record struct MetrologyPoint2D(double X, double Y);
public readonly record struct MetrologySegment2D(
    MetrologyPoint2D Start,
    MetrologyPoint2D End);
public readonly record struct MetrologyCoordinateSystem2D(
    MetrologyPoint2D Origin,
    MetrologyPoint2D XAxis,
    MetrologyPoint2D YAxis);
public readonly record struct AffineTransform2D(
    double M11, double M12,
    double M21, double M22,
    double Tx, double Ty);
public readonly record struct CalibrationCorrespondence2D(
    MetrologyPoint2D Source,
    MetrologyPoint2D Target);
public sealed record DistanceMeasurementResult(
    MetrologyPoint2D Start,
    MetrologyPoint2D End,
    double Distance,
    string Unit,
    string ResultFingerprint);
public sealed record AffineCalibrationResult2D(
    AffineTransform2D Transform,
    int PointCount,
    double RootMeanSquareError,
    double MaximumError,
    string Fingerprint);
```

### A.2 方法

```csharp
MetrologyPoint2D.Zero -> MetrologyPoint2D
MetrologyPoint2D.IsFinite -> bool
MetrologyPoint2D.DistanceSquaredTo(MetrologyPoint2D other) -> double
MetrologyPoint2D.DistanceTo(MetrologyPoint2D other) -> double
MetrologyPoint2D.Translate(double dx, double dy) -> MetrologyPoint2D

MetrologySegment2D.IsValid -> bool
MetrologySegment2D.Length -> double
MetrologySegment2D.Midpoint -> MetrologyPoint2D

MetrologyCoordinateSystem2D.IsValid -> bool
MetrologyCoordinateSystem2D.ToLocal(MetrologyPoint2D point) -> MetrologyPoint2D
MetrologyCoordinateSystem2D.ToWorld(MetrologyPoint2D local) -> MetrologyPoint2D

AffineTransform2D.Transform(MetrologyPoint2D point) -> MetrologyPoint2D
AffineTransform2D.Identity -> AffineTransform2D
AffineTransform2D.IsFinite -> bool
AffineTransform2D.Determinant -> double
AffineTransform2D.TryInvert(out AffineTransform2D inverse,
    double determinantThreshold = 1e-12) -> bool
AffineTransform2D.Then(AffineTransform2D next) -> AffineTransform2D

MetrologyPoint2DValidationRuntime.Validate(MetrologyPoint2D point)
    -> IReadOnlyList<string>
MetrologyPoint2DValidationRuntime.IsValid(MetrologyPoint2D point) -> bool
AffineTransform2DValidationRuntime.Validate(AffineTransform2D transform,
    double determinantThreshold = 1e-12) -> IReadOnlyList<string>
AffineTransform2DValidationRuntime.IsValid(AffineTransform2D transform,
    double determinantThreshold = 1e-12) -> bool
CalibrationCorrespondence2D.IsValid -> bool

DistanceMeasurementRuntime.Measure(MetrologyPoint2D start,
    MetrologyPoint2D end, string unit) -> DistanceMeasurementResult
DistanceMeasurementResultValidationRuntime.Validate(
    DistanceMeasurementResult result) -> IReadOnlyList<string>
DistanceMeasurementResultValidationRuntime.IsValid(
    DistanceMeasurementResult result) -> bool

AffineCalibrationRuntime.Fit(
    IEnumerable<CalibrationCorrespondence2D> correspondences,
    double determinantThreshold = 1e-12) -> AffineCalibrationResult2D
AffineCalibrationValidationRuntime.Validate(
    IEnumerable<CalibrationCorrespondence2D> correspondences,
    AffineCalibrationResult2D result,
    double tolerance = 1e-9) -> IReadOnlyList<string>
AffineCalibrationValidationRuntime.IsValid(
    IEnumerable<CalibrationCorrespondence2D> correspondences,
    AffineCalibrationResult2D result,
    double tolerance = 1e-9) -> bool
```

### A.3 数学与失败语义

- `MetrologyPoint2D` 保存普通二维坐标；Core 不绑定物理单位。`DistanceTo` 是欧氏点距，返回标量坐标单位。
- `MetrologySegment2D.Length` 是 Start 到 End 的欧氏距离；`Midpoint` 为端点算术中点。
- `MetrologyCoordinateSystem2D` 的 X/Y 轴要求有限、单位长度、互相正交（当前实现容差 `1e-9`）。`ToLocal` 以相对原点点积两个轴；`ToWorld` 用两个轴线性组合加原点。
- `AffineTransform2D.Transform` 使用 `x'=M11*x+M12*y+Tx`、`y'=M21*x+M22*y+Ty`。`Then(next)` 表示先应用当前变换，再应用 `next`。求逆和有效性门要求行列式绝对值至少为阈值；`TryInvert` 在失败时返回 `false`，其 out 值不作为有效结果。
- `DistanceMeasurementRuntime.Measure` 要求端点有限且 unit 非空，输出欧氏距离；unit 经 Trim 保存，不进行单位换算。结果 SHA-256 指纹覆盖端点、规范化 unit 和距离的 round-trip 文本；源码没有定义跨 Culture 的规范序列化保证。
- `AffineCalibrationRuntime.Fit` 要求至少三个有限对应点；按 Source.X、Source.Y、Target.X、Target.Y 排序，解六参数二维仿射最小二乘正规方程，计算 RMS/最大欧氏残差并生成 SHA-256 指纹。现有 Smoke 检查同一执行环境内重复拟合相等；源码没有定义跨 Culture/运行时的规范序列化保证。退化或数值病态输入以异常拒绝；没有鲁棒剔除策略。
- 两个结果验证器重新计算期望结果，并检查数值、计数、残差与指纹。容差和行列式阈值须为有限正数；当前实现用参数默认值 `1e-9`、`1e-12`。
- 非有限坐标、溢出、无效容差、空参数、退化输入的精确可恢复分类目前不是稳定错误码 Contract。改变异常类型/边界行为前先补充本附录和测试；调用方不得依赖未列明的异常文本。

### A.4 版本与限制

Contract v0.1不含单位/像素转换、校准资格、业务DTO、异步/事件/排空、证据、HALCON、面积、3D/体积、UI或持久化。新增基础/连续能力分别定位§10–18的v0.2与§19的v0.3，准入后显式绑定入口/版本，不扩写旧类型或重写指纹；其外新增能力仍先修订本指导。DesignReview/Prep不等于已批准、可编译或生产可调用API。
