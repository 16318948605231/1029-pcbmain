# 标定资产与资格模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`CAL-C1, CAL-C2, CAL-C3, CAL-JC, CAL-CR`

- 模块：`calibration-assets`（IM-013；来源 PKG-015）
- 版本：`0.3.3-prep`
- 状态：`DesignReview / Prep`
- Core 规格状态：`CAL-C1 / CAL-C2 / CAL-C3 / CAL-JC / CAL-CR = ModuleCoreImplementationReady`（CAL-C1/C2/C3 于2026-10-09接收；CAL-JC/CR 于2026-10-11接收六项文档规格；均非实现或运行验收）。
- 日期：2026-10-11
- 责任：标定观测组织、求解适配、独立验证证据、不可变标定资产、用途适用性解析和失效通知。
- 规划消费者：相机校正工具、计量工具；共同标定消费者为 `structured-light`、`reconstruction-3d`，见 §7.4。第二消费者验收见 §16。
- 本文是独立交付指导。附录 A 冻结无产品事实写入 Core 的模块内 Contract v0.2；CAL-C1/C2/C3/CAL-JC/CAL-CR 的规格准备按 §17 已获主控接收，不批准平台 Schema、真实算法资格、集成或生产准入。
- 本轮完整范围补充见 §7.3A、§9.2.1/9.2A/9.4、§10.1/10.2及§17.3；新增专用合同仅文档自审，不提升已接收Core或真实运行资格。
- 共同标定 `Joint API v1` 见 §7.4，已解参数读取 `Camera Read API 1` 见 §9.3；CAL-JC/CR 已接收为 `ModuleCoreImplementationReady`，CAL-JA 的固定算子/求解/文件路线及 CAL-JI 的公开交接指导内容已限定接收；§7.4.6B 资格绑定技术桥增量已获主控限定内容接收。真实资格Owner、消费者桥/C#编译、HALCON/native、Writer/Store、性能、样本/物理与现场资格仍未提升。不改 v0.2 的二维 DTO/摘要/已接收状态，不声称消费者已经接线。

## 1. 目的与边界

模块面向不同视觉应用管理可追溯的标定资产及其限定用途资格。主流程为：准备输入 → 求解候选 → 独立验证 → 形成不可变资产 → 由有权主体签发/关联资格 → 按完整条件解析 → 传播失效。求解器成功只表示产生候选，不表示资产已发布、已合格或可用于生产。

模块拥有其观测/求解/验证证据、候选和已发布资产内容身份、资产依赖闭包校验、用途适用性查询结果，以及自身资源与运行状态。资格决定及激活绑定始终由模块外的原 Owner 执行；即使宿主拥有授权，也不能把该权限注入 Core 来增加隐式写入入口。Core 只提供计算证据、未资格内容发布和只读适用性查询。

模块不拥有采集流程、目标关联、设备控制、产品配方、工艺解释、测量结果、最终质量放行、返修/停机策略、客户协议、证书签发、用户权限策略、全局配置或生产事实提交。调用方负责流程、目标关联、工艺解释、质量放行及设备副作用。模块不会因为发现资产失效而自行停机、改写历史结果或选择另一份“最新”资产。

不得写入 PCB、SPI、AOI、点胶、涂覆或其他制程判定。宿主可以把制程外的明确用途标识及技术配置传入解析请求，但制程规则、公差和放行语义留在宿主。资产覆盖几何/辐射/显示/局部基准等不同能力时须区分类型和用途；当板注册、瞬时基准面、显示校正不等于设备标定资产。

### 1A. 新架构适配要点

**架构门禁**：`Asun.CalibrationAssets.Core` 与各子程序集不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。仅 `Asun.CalibrationAssets.Wpf`（工作区控件）可引用 WPF/DevExpress，且 Core 不得反向引用它。

**Blazor/Web 宿主中的标定适用性查询**：Web 端（Blazor Server）需要展示"当前标定资产是否适用于该工件"时，服务端调用本模块的只读 `ResolveAsync` / `QueryApplicabilityAsync`，把结论（含资产修订、资格修订、匹配/不匹配字段、Unknown 原因）投影到浏览器。浏览器端不自行判定适用性，也不缓存长期可用布尔值——`ApplicabilityResult` 是本次快照结论，资产失效后必须重新解析。

**L1-L4 参数学习与标定的边界**：标定资产（几何/辐射/局部基准）与算法参数属不同 Owner。`ai-dataset-governance` 的 L1-L4 参数学习只调整算法参数，不重新求解或发布标定资产。若参数学习发现需要重新标定，只能产出"建议重新标定"的人工待办，不得自动触发本模块的求解/发布路径。

**HALCON 备选交叉验证适用性**：本模块的相机/平面/投影路线依赖 HALCON 26.05 算子（`vector_to_proj_hom_mat2d`、`projective_trans_point_2d`、`projective_trans_pixel` 等），是双跑 CI 交叉验证的主要落点之一。约束：
- HALCON 是官方 normalized_dlt 拟合的固定 Owner；C# 仅重算矩阵预测、值限额与包含校验，不新增 OpenCV 拟合实现
- OpenCV 4.12.0 固定 commit `49486f61fb25722cbcf586b7f4320921d46fb38e` 的 `calib3d` 只作为独立对照（见 §18.3 已读证据），不引入平行生产算法
- 两路输出的差异只作诊断报告，不自动选择某一路作为发布依据；发布仍由本模块的验证流程与资格 Owner 决定

## 2. 依赖和分层

```text
视觉应用 / 工具宿主 / 工作流
  ├─ 定义采集与目标关联、用途、资格策略、权限和生产处置
  └─ 注入资格/资产/诊断端口
       ↓ 稳定公共契约
CalibrationAssets.Core（无 UI，可独立调用）
  ├─ CalibrationAssets.AsunImageAdapter（可选）
  ├─ CalibrationAssets.PersistenceAdapter（可选）
  └─ CalibrationAssets.Wpf（可选投影控件，不承载业务权威）
       ↓
  ImageLibDotNet 公共接口 / 宿主存储与事务端口
```

Core 不引用 PCB 产品 Shell、制程 ViewModel、私有表、具体相机/运动 SDK、产品静态全局状态或 UI 程序集。AsunImage、存储、资格审批与诊断以端口注入；只装配本次需要的适配器，不通过 Service Locator 动态找未登记服务。目标 HALCON 为 26.05，其算子均通过 `ImageLibDotNet.cv2` 调用，不重复核验封装是否包含算子。算子语义、参数、线程及取消行为以项目内 `halcon算子手册/operators` 为准；仅当 C# 参数类型、重载或封送方式有实际歧义时，查看 AsunImage 公共签名或通过消费项目编译确认，不检查内部。未解决的调用映射只阻断对应适配切片，不阻断无 native 依赖的 Core。

## 3. 公共类型和输入输出

以下 C# 类型和操作名是本模块 Core Contract v0.2 的**模块内冻结语义**，用于指导独立接入；它们不是平台 Schema，也不是已存在程序集 API。适配平台 Contract/State/Owner 时由对应 Owner 串行确定显式映射及事实写入权，不得改变本模块 DTO 的含义。跨系统传递稳定 ID、版本和内容摘要，不传 HALCON 句柄或 UI 对象。

### 3.1 强类型通用值

单位不可由裸 `double` 猜测。内部建议以 .NET 10 `readonly record struct` 表达，边界序列化需同时传数值与明确单位：

```csharp
public readonly record struct Pixel(double Value);
public readonly record struct PixelSize(double Value, LengthUnit Unit);
public readonly record struct Length(double Value, LengthUnit Unit);
public readonly record struct Angle(double Value, AngleUnit Unit);
public readonly record struct Temperature(double Value, TemperatureUnit Unit);
public readonly record struct DurationLimit(TimeSpan Value);
public readonly record struct Digest(string Algorithm, string Hex);
public readonly record struct RevisionId(string Value);
public readonly record struct AssetId(string Value);
public readonly record struct CalibrationSessionId(Guid Value);
```

当前单位枚举是封闭集合：`LengthUnit={Meter,Millimeter,Micrometer}`、`AngleUnit={Radian,Degree}`、`TemperatureUnit={Celsius,Kelvin}`，不是“至少”集合。其它单位/未知枚举拒绝 CAL-100，未来扩展须修订版本及转换合同。只在明确转换处归一化，原始值和原单位仍保留。所有浮点输入必须有限；`Length` 值类型本身允许有符号有限值，包括坐标零、负坐标和负平移，不做绝对值修正。`Point3.X/Y/Z`、`RigidPose.Translation`、`MotionPerRow` 各分量和域坐标上下界允许零/负值；平面 Z=0 正常，线扫 Vy 的正值限制是该模型专用约束。

尺寸字段逐项校验正值：PointPitch、CenterPitchX/Y、DotDiameter、CircleDiameter、SquareSize、物理半径、PixelSize、WorkingDistance、ExpandedUncertainty（声明时）、ExposureMicroseconds（声明时）、图像宽高、预算时长/容量；覆盖因子正。残差及像素误差上限允许零而不允许负；Temperature/Celsius、GainDb 和姿态角允许负，Kelvin 不允许负。宽高、索引、样本计数使用整数且不得溢出；单位缺失、坐标系方向缺失或非有限数拒绝，不默认为 mm、像素原点或零。最小断言见 CAL.CORE.13。

### 3.2 请求语义与字段来源

| 请求组 | 强类型字段 | 单位/范围/缺省 | 权威来源及校验 |
|---|---|---|---|
| 方法 | `MethodProfileRef(Method,Revision,Digest)`、`Device.CameraModel` | 非空标识；具体 HALCON 模型无隐式默认，Profile 与设备模型必须一致 | 已审方法/Profile；型号支持情况由适配器能力声明 |
| 采集配置 | `DeviceFingerprint`, `OpticalFingerprint`, `SensorMode=AreaScan\|LineScan`, `ReadoutLayoutDigest`, 快照宽高/ROI/binning, `ExposureMicroseconds?`, `GainDb?` | 宽高正整数；ROI 在传感器坐标域内；binning 正整数；其他工程单位由对应类型定义；可选字段无默认 | 宿主冻结的实际相机/光学配置快照；必须包含方法认定为敏感的字段 |
| 线扫时序证据 | `LineTimingEvidenceRef?`, `ScanDirection?`, `ClockEpoch?`, `EncoderEvidenceRef?` | 仅线扫模型所需字段必填；时间戳/编码器单位、插值和同步误差定义与来源不可缺省；不得用命令位置替代实际反馈 | 采集/运动 Owner 提供曝光或行时间与反馈来源。只作为相机模型输入证据；扫描轴误差补偿与跨 FOV 全局映射仍归 mosaic |
| 参考件 | `ReferenceArtifactId`, `ReferenceRevision`, `ReferenceDigest`, `ReferenceGeometry`, `CertificateRef?` | 坐标数值带长度单位、轴/方向、坐标系和真值来源；不设通用几何默认 | 参考件 Owner/证书原件；标称 CAD 与溯源实测值分开 |
| 观测 | `ObservationId`、`Image.Digest`、`Points:ObservedPoint[]`、`PoseIndex`、`ObjectInCameraInitialPose?`、`ObservedAtUtc`、`QualityEvidenceDigest` | row/column 为原始像素坐标；点关联一一校验；时间为 UTC；姿态单位与坐标定义明确 | 输入图像/帧及检测适配器；保留来源、拒识和剔除原因 |
| 数据分区 | `FitSet`, `ValidationSet`, `PartitionRevision` | 两集合不得按观测点拆分泄漏同一物理采样组；默认不自动随机拆分 | 预先冻结的采样/分组计划；无法证明独立时验证结果标为非独立 |
| 环境和范围 | `OperatingDomain`, `EnvironmentRange`, `ValidUntil?` | 温度、工作距离、Z/视场、曝光等各自带单位；上/下界有序；有效期无默认 | 设备用途 Profile/资格 Owner；不存在的领域条件标为未声明，不伪造通用范围 |
| 执行预算 | `CalibrationExecutionBudget` | 取消令牌必需；默认单调执行上限 10 min、观察上限 10 min 30 s（§6.1），图像数上限 100，单图像最大解码字节 256 MiB；超出由调用方显式覆盖且不得超过宿主安全上限 | 此处为单次工具/离线任务的保守软件默认，不是算法采样下限、生产目标或现场性能承诺；宿主 Profile 可收紧或批准扩大 |
| 独立验收条件 | `ValidationPlanRef` | 物理误差限、残差界、覆盖最小量及统计方法均必填且有版本/单位；无批准来源时不得签发用途资格 | 独立计量/资格 Owner；不由模块或算法作者猜默认阈值 |

手眼、多相机、结构光、平场或复合标定仍按各方法指导另加有单位字段、可观测条件、支持域及反例；线扫也须按具体 HALCON 相机模型声明它所需的线时序字段、参数化和退化条件。不得把不同物理模型压成通用 `Options` 字符串包。目标模型没有已绑定适配器或所需字段/资格条件未冻结时，接口返回 `MethodNotQualified` 或 `UnsupportedMethod`，可保留离线研究输入但不得发布可用资格。

适用性解析必须区分设备/传感器允许工作的环境范围与该资产通过独立证据验证、且资格 Owner 批准的有效域；两者分别取自其权威来源，不能互相推导或用设备运行规格替代精度有效性。实际配置与环境须同时满足两类约束；必需边界缺失或当前无法确认时返回 `Unknown`，边界完整且确认越界时返回 `NotApplicable`，并逐项列出缺项或不匹配。不得自行补门限或扩大有效域；设备允许运行范围和客户/计量验收门限仍由各自 Owner 冻结。

### 3.3 主要输出

`CalibrationSolveResult` 至少包含：`SessionId`、`CandidateArtifactRef?`、方法和适配器版本、输入/参考/分区摘要、状态、逐组残差统计及单位、有效域候选、覆盖诊断、失败观测及原因、起止时间、资源统计、诊断关联 ID。`CalibrationArtifact` 是不可变内容：资产 ID/修订/hash、方法和算法/运行库版本、设备/光学/采集配置快照、参考件引用、原始观测引用、求解参数、残差证据、域声明、依赖闭包、创建时间及格式版本。大图和原生校准数据用租约或内容引用，不内嵌无上限像素数组。

`ApplicabilityResult` 必须返回 `Applicable`, `NotApplicable` 或 `Unknown` 三态、资产引用、资格引用及修订、匹配/不匹配字段、未知字段、域内检查、失效原因和权威水位。`Unknown` 不得折叠为可用。拟合残差、独立物理误差、不确定度、重复性及资格状态分别表达；不得以单一 `IsSuccess` 代替。

### 3.4 Contract v0.2 的资产引用和 DTO 形状

以下引用是三个不同的强类型概念，不允许用一个 `AssetId` 在入口之间通用：

```csharp
public readonly record struct OperationId(Guid Value);
public readonly record struct QualificationId(string Value);

public sealed record CandidateArtifactRef(
    AssetId CandidateId, RevisionId CandidateRevision, Digest CandidateDigest);

public sealed record PublishedArtifactRef(
    AssetId AssetId, RevisionId AssetRevision, Digest AssetDigest);

public sealed record QualifiedAssetRef(
    PublishedArtifactRef Artifact,
    QualificationId QualificationId,
    RevisionId QualificationRevision,
    DateTimeOffset QualifiedAtUtc,
    DateTimeOffset? ValidUntilUtc);
```

`CandidateArtifactRef` 只能由 `SolveAsync` 的 `CandidateReady` 结果产生，只能作为 `ValidationRequest` 和 `PublishRequest` 的输入；它不能传给 `ResolveAsync`，不能作为运行资产或绑定对象。`PublishedArtifactRef` 由 `PublishAsync` 的成功回执产生，表示内容已按 hash 原子写入并可回读，但**不表示 Qualified**。`QualifiedAssetRef` 只能由资格 Owner 的只读结果与 `ResolveAsync` 共同形成；模块不得自行创建、猜测或升级它。任何把候选 ID 传入 Resolve、把已发布但未 Qualified 的资产当作 Qualified、或把 Qualified 引用重新作为 Publish 输入的请求，在预检阶段返回 `CAL-105 NotApplicable`。

Core Contract v0.2 使用下列不可变 DTO；字段是最小完整集合，不能由实现者省略、改名或添加含义相同的第二字段：

```csharp
public sealed record PrepareRequest(
    string ContractRevision,
    CalibrationSessionId SessionId,
    MethodProfileRef Method,
    CalibrationTargetDescriptor Target,
    ReferenceGeometryRef ReferenceGeometry,
    DeviceConfigurationSnapshot Device,
    IReadOnlyList<ObservationRef> Observations,
    PartitionPlan Partition,
    CalibrationExecutionBudget Budget,
    OperationId OperationId);

public sealed record SolveRequest(
    string ContractRevision,
    CalibrationSessionId SessionId,
    Digest PreparedInputDigest,
    SolverParameterSet Parameters,
    CalibrationExecutionBudget Budget,
    OperationId OperationId);

public sealed record ValidationRequest(
    string ContractRevision,
    CandidateArtifactRef Candidate,
    ValidationPlanRef Plan,
    IReadOnlyList<ObservationRef> IndependentObservations,
    CalibrationExecutionBudget Budget,
    OperationId OperationId);

public sealed record PublishRequest(
    string ContractRevision,
    CandidateArtifactRef Candidate,
    ValidationEvidenceRef ValidationEvidence,
    CalibrationExecutionBudget Budget,
    OperationId OperationId);

public sealed record ResolveRequest(
    string ContractRevision,
    PublishedArtifactRef Asset,
    IntendedUse Use,
    DeviceConfigurationSnapshot ActualDevice,
    OperatingDomain ActualDomain,
    CalibrationExecutionBudget Budget,
    OperationId OperationId);

public sealed record PrepareResult(
    OperationId OperationId,
    OperationCompletion Completion,
    CalibrationSessionId SessionId,
    Digest? PreparedInputDigest,
    PreparationStatus Status,
    IReadOnlyList<ObservationRejection> RejectedObservations,
    CalibrationError? Error,
    DiagnosticRef Diagnostic);

public sealed record CalibrationSolveResult(
    OperationId OperationId,
    OperationCompletion Completion,
    CalibrationSessionId SessionId,
    SolveStatus Status,
    CandidateArtifactRef? Candidate,
    ResidualReport? Residuals,
    DomainReport? CandidateDomain,
    IReadOnlyList<ObservationDiagnostic> ObservationDiagnostics,
    ResourceReport Resources,
    CalibrationError? Error,
    DiagnosticRef Diagnostic);

public sealed record ValidationResult(
    OperationId OperationId,
    OperationCompletion Completion,
    CandidateArtifactRef Candidate,
    ValidationStatus Status,
    ValidationEvidenceRef? Evidence,
    IReadOnlyList<ValidationFinding> Findings,
    CalibrationError? Error,
    DiagnosticRef Diagnostic);

public sealed record PublishReceipt(
    OperationId OperationId,
    OperationCompletion Completion,
    PublishStatus Status,
    PublishedArtifactRef? PublishedArtifact,
    bool QualificationIssued,
    CalibrationError? Error,
    DiagnosticRef Diagnostic);

public sealed record ApplicabilityResult(
    OperationId OperationId,
    OperationCompletion Completion,
    ApplicabilityStatus Status,
    PublishedArtifactRef Asset,
    QualifiedAssetRef? QualifiedAsset,
    IReadOnlyList<ApplicabilityFinding> Findings,
    CalibrationError? Error,
    DiagnosticRef Diagnostic);
```

结果约束仅对 Completion=ResourcesReleased 生效：`PrepareResult.Status == Prepared` 时 `PreparedInputDigest` 非空；`CalibrationSolveResult.Status == CandidateReady` 时 `Candidate`、残差、域和观测诊断均非空；其他状态 `Candidate` 必须为 null。`ValidationResult` 只验证候选，不把候选改写成资产；`PublishReceipt.Status == Published` 时 `PublishedArtifact` 非空且 `QualificationIssued == false`，因为资格由外部 Owner 决定；`ApplicabilityResult.Status == Applicable` 时 `QualifiedAsset` 非空，其他状态必须为 null。错误结果仍返回可审计的输入/操作 ID和诊断引用，不能用 null 结果吞掉失败原因。

`CalibrationTargetDescriptor` 是受限联合类型，不使用一组可互相矛盾的可空字段：

```csharp
public abstract record CalibrationTargetDescriptor(
    AssetId TargetId, RevisionId TargetRevision, Digest TargetDigest,
    LengthUnit CoordinateUnit, string OriginConvention,
    string RowDirection, string ColumnDirection);

public sealed record HalconRectangularDotPlateDescriptor(
    AssetId TargetId, RevisionId TargetRevision, Digest TargetDigest,
    LengthUnit CoordinateUnit, string OriginConvention,
    string RowDirection, string ColumnDirection,
    string DescriptionFileRef, int Rows, int Columns,
    Length PointPitch, Length DotDiameter, Digest CertificateDigest,
    Digest FlatnessEvidenceDigest)
    : CalibrationTargetDescriptor(TargetId, TargetRevision, TargetDigest,
        CoordinateUnit, OriginConvention, RowDirection, ColumnDirection);

public sealed record UniformSolidCircleGridDescriptor(
    AssetId TargetId, RevisionId TargetRevision, Digest TargetDigest,
    LengthUnit CoordinateUnit, string OriginConvention,
    string RowDirection, string ColumnDirection,
    int Rows, int Columns, Length CenterPitchX, Length CenterPitchY,
    Length CircleDiameter, Digest PatternDigest,
    Digest CertificateDigest, Digest FlatnessEvidenceDigest)
    : CalibrationTargetDescriptor(TargetId, TargetRevision, TargetDigest,
        CoordinateUnit, OriginConvention, RowDirection, ColumnDirection);

public sealed record ChessboardCompatibilityDescriptor(
    AssetId TargetId, RevisionId TargetRevision, Digest TargetDigest,
    LengthUnit CoordinateUnit, string OriginConvention,
    string RowDirection, string ColumnDirection,
    int InnerCornersX, int InnerCornersY, Length SquareSize,
    string CornerObservationMethod, RevisionId CornerObservationRevision,
    Digest PatternDigest, Digest CertificateDigest)
    : CalibrationTargetDescriptor(TargetId, TargetRevision, TargetDigest,
        CoordinateUnit, OriginConvention, RowDirection, ColumnDirection);
```

`HalconRectangularDotPlateDescriptor` 是 HALCON 原生 finder 标定板路线；`UniformSolidCircleGridDescriptor` 表示无定位框、等直径实心圆、均匀周期排列的圆点板，不能与有 finder 的 HALCON 标准板混为一类；`ChessboardCompatibilityDescriptor` 表示棋盘格内角点拓扑。三种描述均须有稳定原点、轴向、物理尺寸和目标修订。圆点板描述另含行列数、X/Y 中心距、圆径、PatternDigest、证书与平面度证据；若 X/Y 中心距不相等或点径不一致，不得实例化为该类型。棋盘格必须用内角点数和方格边长，不得传外部方格数。任何 TargetKind 与 DTO 变体不一致、字段缺失或证据摘要无效，均在 `PrepareAsync` 返回 `CAL-100 InvalidRequest`，不改用另一靶标。

`CalibrationTargetKind` 在 v0.2 仅有 `HalconRectangularDotPlate`、`UniformSolidCircleGrid`、`ChessboardCompatibility`，与三个 DTO 分支一一对应；当前各适配器仍须按 §7 方法链完成实现和资格验证。`MeasuredPlaneArtifact` 与编码靶专用几何是后续专用切片的领域概念，不是当前二维 DTO 的第四分支；不允许实例化基类绕过封闭联合。未绑定适配能力或方法不适用时，分别返回 `CAL-101 UnsupportedMethod` 或 `CAL-105 NotApplicable`；不得用通用字典拼造靶标。

### 3.5 错误、生命周期和事件 DTO

错误和生命周期也属于 Core Contract v0.2，不能退化为异常文本或单一 `bool`：

```csharp
public enum CalibrationStage { Prepare, Solve, Validate, Publish, Resolve, QueryReceipt, Drain }

public sealed record CalibrationError(
    CalibrationErrorCode Code,
    CalibrationStage Stage,
    bool Retryable,
    bool SideEffectOutcomeUnknown,
    string MessageKey,
    OperationId OperationId,
    DiagnosticRef Diagnostic);

public sealed record CalibrationEvent(
    OperationId OperationId,
    CalibrationSessionId? SessionId,
    long Sequence,
    DateTimeOffset OccurredAtUtc,
    string EventName,
    string ContractRevision,
    CalibrationStage Stage,
    string? State,
    DiagnosticRef Diagnostic);

public enum PreparationStatus { Prepared, Rejected, Cancelled, TimedOut, Faulted }
public enum SolveStatus { CandidateReady, Rejected, Cancelled, TimedOut, Faulted }
public enum ValidationStatus { Validated, ValidationFailed, Rejected, Cancelled, TimedOut, Faulted }
public enum PublishStatus { Published, PublishFailed, PublishUnknown }
public enum ApplicabilityStatus { Applicable, NotApplicable, Unknown }
public enum OperationCompletion { ResourcesReleased, DrainPending }

public enum CalibrationErrorCode {
    InvalidRequest, UnsupportedMethod, InsufficientObservations, ObservationRejected,
    ValidationFailed, NotApplicable, QualificationUnknown, RevisionConflict,
    ContentIntegrityFailure, PersistenceOutcomeUnknown, Cancelled, DeadlineExceeded,
    ResourceLimitExceeded, AdapterFailure, InvalidState, ModuleStopping,
    InternalFailure, CandidateNotPublishable
}
```

`CalibrationEvent.EventName` 只能取正文 §4.3 已列出的固定事件名；未知值不是兼容扩展而是契约错误。`MessageKey` 是资源键，不是供调用方解析的自由文本。`SideEffectOutcomeUnknown` 只在发布/存储回执未知时为 `true`；求解取消不能伪造持久化未知。错误码的序列化名称使用表中的 `CAL-100`～`CAL-117`，枚举数值不写入跨进程协议。

请求中使用的嵌套类型也必须保持封闭和有界：

```csharp
public readonly record struct CalibrationMethodId(string Value);
public readonly record struct CameraModelId(string Value);
public readonly record struct ReferencePointId(string Value);
public readonly record struct ObservationId(string Value);
public readonly record struct DiagnosticRef(string TraceId);
public readonly record struct ValidationEvidenceRef(ContentRef Content);
public readonly record struct IntendedUse(string Name, RevisionId Revision);

public sealed record DeviceConfigurationSnapshot(
    string DeviceFingerprint, string OpticalFingerprint, SensorMode SensorMode,
    CameraModelId CameraModel, RevisionId ConfigurationRevision,
    string LensIdentity, string FocusState, string MagnificationState,
    string MountingConvention, Digest ReadoutLayoutDigest,
    int ImageWidth, int ImageHeight, int RoiX, int RoiY, int RoiWidth, int RoiHeight,
    int BinningX, int BinningY, double? ExposureMicroseconds, double? GainDb,
    Length? WorkingDistance, Temperature? Temperature,
    string? IlluminationFingerprint);

public enum SensorMode { AreaScan, LineScan }

public sealed record ObservedPoint(
    ReferencePointId ReferencePoint, Pixel Row, Pixel Column,
    Digest QualityEvidenceDigest);

public sealed record ObservationRef(
    ObservationId ObservationId, ContentRef Image, Digest DeviceSnapshotDigest,
    string GroupId, int PoseIndex, DateTimeOffset ObservedAtUtc,
    PixelCoordinateLayout PixelLayout, IReadOnlyList<ObservedPoint> Points,
    RigidPose? ObjectInCameraInitialPose, LineScanEvidence? LineScan,
    ContentRef IdentityEvidence, Digest QualityEvidenceDigest);

public sealed record PartitionPlan(
    RevisionId Revision, IReadOnlySet<string> FitGroups,
    IReadOnlySet<string> ValidationGroups);

public sealed record CalibrationExecutionBudget(
    TimeSpan Deadline, TimeSpan WaitLimit, int MaxImages, long MaxImageBytes, int MaxPoints,
    long MaxResidentBytes, int MaxConcurrentSolves)
{
    // Core defaults are conservative software limits, not qualification thresholds.
    public static CalibrationExecutionBudget Default =>
        new(TimeSpan.FromMinutes(10), TimeSpan.FromMinutes(10.5), 100, 256L * 1024 * 1024, 100_000,
            1L * 1024 * 1024 * 1024, 1);
}

public abstract record SolverParameterSet(
    RevisionId ParameterRevision, Digest ParametersDigest);

public sealed record AreaCameraSolverParameters(
    RevisionId ParameterRevision, Digest ParametersDigest,
    CameraModelId CameraModel, CameraParameterVector InitialParameters,
    IReadOnlySet<string> EstimatedParameters, MethodProfileRef Profile)
    : SolverParameterSet(ParameterRevision, ParametersDigest);

public sealed record ChessboardCompatibilitySolverParameters(
    RevisionId ParameterRevision, Digest ParametersDigest,
    CameraModelId CameraModel, CameraParameterVector InitialParameters,
    IReadOnlySet<string> EstimatedParameters, MethodProfileRef Profile)
    : SolverParameterSet(ParameterRevision, ParametersDigest);

public sealed record LineScanCameraSolverParameters(
    RevisionId ParameterRevision, Digest ParametersDigest,
    CameraModelId CameraModel, CameraParameterVector InitialParameters,
    IReadOnlySet<string> EstimatedParameters, MethodProfileRef Profile)
    : SolverParameterSet(ParameterRevision, ParametersDigest);
```

相机求解不公开 `MaxIterations`：26.05 `calibrate_cameras` 没有这个入参，不能把椭圆拟合的迭代数或手眼优化选项套到相机求解。初值、估计项、曝光、增益和工作距离须来自冻结 Profile；`EstimatedParameters` 仅允许 §7.2C 目标模型可估计项，经 `set_calib_data` 的 `calib_settings/excluded_settings` 映射。未知参数名拒绝，不忽略。`CalibrationExecutionBudget.Default` 是离线软件上限，不是采样下限或性能承诺；真实消费者没有 Profile 时性能状态为 `TargetPending`，不因此取得资格。`PartitionPlan` 按物理采样组分区，禁止把同一组拆点伪装成独立验证。

### 3.6 嵌套合同和不可变内容（v0.2）

本次补齐图/姿态成组观测、实测点表、结果空形状和回查入口，属于设计合同升版，不声明与旧 v0.1 DTO 二进制/序列化兼容。尚无本模块已实现程序集，本轮不迁移历史资产。下表使用 `Type(Field:Type, …)` 给出 C# record 等价形状；`?` 为可空，集合不为 null 且在构造时防御性复制，禁止下游修改 `IReadOnlyList` 背后的数组。除列出的联合分支外，不开放字符串属性包。

| 类型 | 唯一形状与约束 |
|---|---|
| `ContentRef` | `(Digest:Digest, Format:string, FormatRevision:RevisionId, ByteLength:long)`；长度非负且在预算内，引用按摘要查找，无文件路径执行权限 |
| `ReferenceGeometryRef` | `(TargetId:AssetId, TargetRevision:RevisionId, Nominal:ContentRef, Measured:ContentRef?, Certificate:ContentRef?, GeometryDigest:Digest)`；未实测可离线拟合名义候选，但验证不得伪称实测 |
| `ReferenceGeometry` | `(Reference:ReferenceGeometryRef, Frame:CoordinateFrame, Points:IReadOnlyList<ReferencePoint>, ReferenceTemperature:Temperature?, FlatnessEvidence:ContentRef?, CertificateValidUntilUtc:DateTimeOffset?)` |
| `ReferencePoint` | `(Id:ReferencePointId, Nominal:Point3, Measured:Point3?, ExpandedUncertainty:Length?, CoverageFactor:double?)`；一一对应稳定点号，修正后的实测 XYZ 不再假装理想等距；不确定度与覆盖因子成对且正 |
| `CoordinateFrame` / `Point3` | frame=`(Id:string, Handedness:Handedness, AxisConvention:string)`，handedness=`RightHanded/LeftHanded`；point=`(X:Length,Y:Length,Z:Length)`，必须同单位；到 HALCON 的右手/米转换有记录 |
| `RigidPose` | `(FromFrame:CoordinateFrame, ToFrame:CoordinateFrame, Translation:Point3, RotationRowMajor:IReadOnlyList<double>, Source:ContentRef)`；9 个有限数，正交/行列式容差来自 Profile；只收刚体、不猜 Euler 次序 |
| `PixelCoordinateLayout` | `(SourceWidth:int,SourceHeight:int,CropRow:int,CropColumn:int,CropHeight:int,CropWidth:int,BinningX:int,BinningY:int,Orientation:PixelOrientation,Revision:RevisionId)`；orientation=`Native/Rotate90/Rotate180/Rotate270/MirrorRows/MirrorColumns`，复合变换由显式版本化步骤列表表达，不由宽高猜测；ObservedPoint 一律已经回写原始传感器 row/column |
| `LineScanEvidence` | `(Timing:ContentRef,Encoder:ContentRef,ClockEpoch:string,MotionFrame:CoordinateFrame,MotionPerRow:Point3,FirstLineObjectPose:RigidPose,DirectionNormalized:bool,ConstantVelocityEvidence:ContentRef,RowIntegrityEvidence:ContentRef)`；方向已归一、行完整性与恒速必须成立，MotionFrame 必须为相机 frame，向量单位是长度/行 |
| `CameraParameter` / `CameraParameterVector` | parameter=`(Name:string,Value:double,Unit:CameraParameterUnit)`；unit=`Meter/Dimensionless/Pixel/PerMeterSquared/PerMeterFourth/PerMeterSixth/PerMeter/MeterPerRow`；vector=`(Model:CameraModelId,Parameters:IReadOnlyList<CameraParameter>)`，顺序/单位严格按 §7.2C 和该模型官方定义，不重复键，不以列表长度猜模型 |
| `MethodProfileRef` | `(Method:CalibrationMethodId,Revision:RevisionId,Digest:Digest)`；由 `IReferenceResolver.ReadMethodProfileAsync` 读取；只允许相机/靶类型与检测策略匹配的记录 |
| `OperatingDomain` / `DomainBound` | domain=`(Frame:CoordinateFrame,Bounds:IReadOnlyList<DomainBound>,Evidence:ContentRef?)`；bound=`(Quantity:DomainQuantity,Unit:DomainUnit,Lower:double,Upper:double)`；quantity=`Temperature/WorkingDistance/ObjectZ/ImageRow/ImageColumn/Exposure/Gain/ScanSpeed`；unit=`Celsius/Meter/Pixel/Microsecond/Decibel/MeterPerSecond` 按 quantity 一一限定，有限有序；本次实际值用 Lower=Upper，缺维度为 Unknown |
| `ValidationPlanRef` / `ValidationPlan` | ref=`(Revision:RevisionId,Digest:Digest)`；plan=`(Reference:ValidationPlanRef,IndependentGroups:IReadOnlySet<string>,Checks:IReadOnlyList<ValidationCheck>,RequiredDomain:OperatingDomain,AuthorityEvidence:ContentRef)`；check=`(Id:string,Metric:ValidationMetric,Unit:ValidationUnit,UpperLimit:double,MinSamples:int,ReferenceEvidence:ContentRef)`，metric=`PixelReprojection/PhysicalLengthError/PhysicalPositionError/AngleError/Repeatability`，unit=`Pixel/Meter/Radian` 与 metric 匹配；本版用逐点绝对误差最大值判断，不自选统计门限；更复杂统计须新方法修订 |
| `ResidualReport` / `ResidualGroup` | report=`(Groups:IReadOnlyList<ResidualGroup>,Evidence:ContentRef)`；group=`(GroupId:string,Metric:ValidationMetric,Unit:ValidationUnit,Count:int,Rms:double,MaximumAbsolute:double,PointErrors:ContentRef)`；空组不报 RMS=0，Count 正，所有数有限；拟合/独立验证报告分存 |
| `DomainReport` | `(ProposedDomain:OperatingDomain,MissingConditions:IReadOnlyList<string>,CoverageEvidence:ContentRef)`；候选域不等于外部批准域 |
| `ResourceReport` | `(StartedAtUtc:DateTimeOffset,ReleasedAtUtc:DateTimeOffset?,PeakManagedBytes:long?,PeakNativeBytes:long?,PeakHandles:int?,QueueWait:TimeSpan)`；未知统计为 null，非零替代；资源释放确认的最终结果 ReleasedAtUtc 非空；DrainPending 观察结果 ReleasedAtUtc=null，不能报释放/性能通过 |
| `ObservationRejection` / `ObservationDiagnostic` | rejection=`(Observation:ObservationId,Code:CalibrationErrorCode,MessageKey:string,Evidence:ContentRef?)`；diagnostic=`(Observation:ObservationId,AcceptedPoints:int,RejectedPoints:int,Findings:IReadOnlyList<ObservationRejection>)`；保留原始点及原因，不删除审计来源 |
| `ValidationFinding` / `ApplicabilityFinding` | validation=`(CheckId:string,Status:CheckStatus,Actual:double?,Unit:ValidationUnit,MessageKey:string,Evidence:ContentRef?)`；applicability=`(Field:string,Status:CheckStatus,MessageKey:string,Evidence:ContentRef?)`；CheckStatus=`Satisfied/Failed/Unknown`，未知 Actual=null，不猜零 |
| `CalibrationArtifact` | `(FormatRevision:RevisionId,Candidate:CandidateArtifactRef,Method:MethodProfileRef,InputDigest:Digest,Device:DeviceConfigurationSnapshot,Reference:ReferenceGeometryRef,Observations:IReadOnlyList<ObservationRef>,Partition:PartitionPlan,Parameters:SolverParameterSet,SolvedParameters:ContentRef,FitResiduals:ResidualReport,Domain:DomainReport,Dependencies:IReadOnlyList<ContentRef>,CreatedAtUtc:DateTimeOffset,Adapter:AdapterCapabilities)`；CandidateDigest 为规范序列化内容摘要，摘要计算排除自身份摘要，摘要投影见 §3.7；Store 存放该投影规范字节（哈希覆盖的资产内容）与独立 Candidate/Published envelope，Published.AssetDigest=Candidate.CandidateDigest，不将 envelope 字节混入自摘要；读取重建 CalibrationArtifact 并独立校验 envelope/内容映射，不改写该内容 |
| `CalibrationProgress` | `(OperationId:OperationId,SessionId:CalibrationSessionId,Sequence:long,Stage:CalibrationStage,CompletedUnits:int,TotalUnits:int?,MessageKey:string)`；未知总量为 null，无假百分比，进度不成为阶段/资格事实 |
| `DrainRequest` / `DrainResult` | request=`(OperationId:OperationId,WaitLimit:TimeSpan)`；result=`(OperationId:OperationId,Status:DrainStatus,Pending:IReadOnlyList<PendingOperation>,Error:CalibrationError?,Diagnostic:DiagnosticRef)`；DrainStatus=`ResourcesReleased/DrainUnknown`；pending=`(OperationId:OperationId,Stage:CalibrationStage,HeldResources:IReadOnlyList<string>)`，全部释放时 Pending 为空 |
| `ReceiptQueryRequest` / `ReceiptQueryResult` | request=`(ContractRevision:string,OriginalOperationId:OperationId,Budget:CalibrationExecutionBudget,OperationId:OperationId)`；result=`(OperationId:OperationId,Completion:OperationCompletion,OriginalOperationId:OperationId,Status:ReceiptQueryStatus,Receipt:PublishReceipt?,Error:CalibrationError?,Diagnostic:DiagnosticRef)`；status=`Found/NotCommitted/Unknown`；Found 的回执是原 ID且其状态不得为 PublishUnknown；NotCommitted 必须由 Store 权威证明无在途提交及未落盘，超时/本地没找到只能 Unknown |
| `QualificationSnapshot` / `AuthorityWatermark` | snapshot=`(Artifact:PublishedArtifactRef,Use:IntendedUse,Status:QualificationStatus,Qualified:QualifiedAssetRef?,ApprovedDevice:DeviceConfigurationSnapshot?,ApprovedDomain:OperatingDomain?,Evidence:ContentRef?,Watermark:AuthorityWatermark)`；status=`Qualified/Suspended/Revoked/Expired/Unknown`；watermark=`(Authority:string,Epoch:string,Revision:RevisionId,ObservedAtUtc:DateTimeOffset,ValidUntilUtc:DateTimeOffset)`，有效性区间必须显式给出，Core 无缓存 TTL 默认 |
| `InvalidationNotice` | `(Artifact:PublishedArtifactRef,QualificationId:QualificationId?,Reason:InvalidationReason,Watermark:AuthorityWatermark,MessageKey:string)`；reason=`QualificationChanged/AuthorityDisconnected/DeviceChanged/DomainExceeded/ContentInvalid`；不含 Stop/Activate 等设备命令 |

`ObservationRef` 是一张图/一个 PoseIndex 的成组观测，不是单点。CameraIdx 在本模块固定 0，CalibObjIdx 固定 0，PoseIndex 非负且会话内不重用；同一 PoseIndex 只一次成组调用 `set_calib_data_observ_points`，Row/Column/Index 等长，Index 经稳定点表映射，不逐点覆盖。同组 Image.Digest 重复、PoseIndex 冲突、像素布局与设备不一致、图/点超预算均在 native 前拒绝。同一个 Physical Group 可以有多帧但只能属于一个分区。Image 引用的内容须包含原始未校正图；显示 crop 不替代求解输入。

`PrepareResult` 拒绝时摘要可 null；`ValidationResult.Evidence` 仅完整验证通过时非空，失败诊断由 Findings 保存，不伪造可发布证据。Solve 的失败/DrainPending 结果 Residuals/Domain 可以 null，Resources 与 Diagnostic 必填；CandidateReady 的报告和 Candidate 均必须非空。全部结果带原 OperationId，ContractRevision 在请求/协商与事件记录，不声称结果 DTO 中存在未定义字段。描述符中的名义 Pitch/SquareSize 只决定拓扑，实际求解真值来自 ReferenceGeometry；目标 digest 必须与点表、证书和描述文件依赖闭包一致。


### 3.7 摘要、幂等和容量

v0.2 使用 SHA-256；Digest.Algorithm 固定 `SHA-256`、Hex 为 64 位小写十六进制。原件/图像摘要按原始字节，不重编码后冒称原 hash。结构编码标识固定 `calibration-core-binary-v2`；本次是未实现的 v0.2 设计修订，历史资产不重算。编码规则唯一如下：

- 单个摘要流先写 ASCII 原始头 `calibration-core-binary-v2`（无长度、无 BOM、无终止符），只在流开头出现一次；随后写投影 record，不先写字段数/字段名。record 名为本文短类型名（无 namespace），按 string 规则编码；字段按下表/类型签名的明确顺序递归。strong wrapper record struct 也先写短类型名后写字段；枚举不是 record，不加枚举类型名。
- string：UInt32 小端 UTF-8 字节长度+严格 UTF-8（无 BOM，不做 Unicode 归一化；无效 surrogate 拒绝）；Guid：小写 D 格式 string；bool：0/1 单字节；int/long 为 Int32/Int64 小端。double 为有限 IEEE754 binary64 小端，负零归正零。DateTimeOffset 为 UTC DateTime ticks Int64；TimeSpan 为 ticks Int64。单位保留原声明值，不在摘要时自行换算；1 mm 和 0.001 m 数值等价但来源摘要不同。
- nullable 先写 0/1 单字节，非空再写实际类型；list 写 UInt32 数量后依序编码；set 写 UInt32 数量，按元素完整规范编码的无符号字节字典序排序，重复输入拒绝而非摘要时删除。record/联合只写具体分支短类型名和本指导字段，继承字段在前且只出现一次；例如 SolverParameterSet 分支先 ParameterRevision，再参数摘要（普通请求编码时包含），然后 CameraModel/InitialParameters/EstimatedParameters/Profile。摘要投影明确排除的字段直接省略，不写空标记或占位摘要。各分支遵循参数签名；不反射排列属性，不依赖 JSON/字典遍历顺序。
- 未知单位/联合/枚举、非有限数、无效大小及长度溢出在编码前拒绝；写入过程受 MaxResidentBytes/内容限额约束，不先建立无限内存缓冲。ContentRef.Digest 按封存字节计算，不是 ContentRef record 的结构摘要。

| 摘要及根 record 名 | 精确投影字段顺序 | 排除与校验 |
|---|---|---|
| `PreparedInputDigest`，根 `PreparedCalibrationProjection` | `ContractRevision:string,Method:MethodProfileRef,Target:CalibrationTargetDescriptor,ReferenceGeometry:ReferenceGeometryRef,Device:DeviceConfigurationSnapshot,Observations:IReadOnlyList<ObservationRef>,Partition:PartitionPlan`（全部直接取 PrepareRequest） | 不含 SessionId/Budget/OperationId，不含 SolverParameterSet；Prepare 解析方法/几何后核依赖内容与引用摘要，不能把未绑定参数添入此摘要。列表保留请求顺序，绝不按点/组另排序 |
| `SolverParameterSet.ParametersDigest`，根名为具体参数分支名 | `ParameterRevision:RevisionId,CameraModel:CameraModelId,InitialParameters:CameraParameterVector,EstimatedParameters:IReadOnlySet<string>,Profile:MethodProfileRef` | 只省略本分支自身 ParametersDigest 字段；嵌套 Profile/ContentRef/其它证据 digest 保留，既不删除全部 Digest 类型字段也不追加基类名。Core 重算比对，不接受自引用 hash 作为输入 |
| `CalibrationArtifact.Candidate.CandidateDigest`，根 `CalibrationArtifactContent` | `FormatRevision,Method,InputDigest,Device,Reference,Observations,Partition,Parameters,SolvedParameters,FitResiduals,Domain,Dependencies,CreatedAtUtc,Adapter`，类型分别与 §3.6 同名字段一致 | 整个 Candidate 字段（ID/Revision/Digest）省略；不写 Published/Qualified 引用、不含 OperationId/诊断/预算。InputDigest 严格等于本次 PreparedInputDigest；Parameters 包含已核验的 ParametersDigest。资产内容身份同时绑定准备输入和实际求解参数，不反过来改变准备摘要；CandidateId/Revision 属独立身份 envelope，Store 仍逐项验证 envelope 和内容 |
| 每入口 `RequestDigest`，根为入口 DTO 短名 | `PrepareRequest/SolveRequest/ValidationRequest/PublishRequest/ResolveRequest/ReceiptQueryRequest`：按各 DTO 签名顺序取**除顶层 OperationId 外的全部字段**；DrainRequest：只取 WaitLimit；InvalidationWatchRequest：按签名取 After/Budget | **包含完整 Budget.Deadline/WaitLimit/每项资源上限**；Solve 保留 SessionId/PreparedInputDigest/Parameters，QueryReceipt 保留 OriginalOperationId；只排除顶层作为幂等键的 OperationId。不排除嵌套来源 ID/摘要。CancellationToken、progress、模块实际时钟、诊断、当前外部资格响应不是请求字段，不编码 |

不增建摘要 Owner：所有结构摘要由 Core 同一编码器生成/核验；外部原件摘要按其真实字节核验。至少执行以下可独立复算固定向量（是编码断言，不是实际产品测试）：

| 输入（含原始流头） | 规范字节十六进制 | SHA-256 |
|---|---|---|
| `Length(-1,Millimeter)` | `63616c6962726174696f6e2d636f72652d62696e6172792d7632060000004c656e677468000000000000f0bf0a0000004d696c6c696d65746572` | `c3ab47b8bceec3a0e557e789c06811957455905ec53ebe93ccc9b91d35131cd3` |
| `Length(0,Meter)`，-0 编码相同 | `63616c6962726174696f6e2d636f72652d62696e6172792d7632060000004c656e6774680000000000000000050000004d65746572` | `fd0f719b51b58f3590072ee1e693b0f44a4b6f25c3521fd7d5e7050c33990b0f` |

投影断言：同 PrepareRequest 仅改 SessionId/OperationId/Budget，PreparedInputDigest 相同而 RequestDigest 按变更字段不同（仅改顶层 OperationId 时 RequestDigest 相同）；首次 Solve 参数此前不在 Prepare，无摘要循环；任一有效参数值变化使 ParametersDigest 和候选内容摘要变化但 PreparedInputDigest 不变；仅替换 ParametersDigest 为错误值重算参数投影仍得到原值，并在入口 CAL-108 拒绝。仅变 Candidate envelope 三字段不改变内容摘要，但 envelope/内容不匹配仍拒绝，不能把“不参与内容 hash”当作允许伪造候选身份。

同 OperationId 在一个模块实例内全入口唯一，Core 保存 RequestDigest、接纳状态、执行任务和结果。不同入口或不同 RequestDigest（包括改预算）返回 CAL-107；相同 ID/摘要不重开端口/native，在执行中按 §6.1 有限等待原记录，完成后回放原结果，不重新计算截止点。等待者取消只取消其等待；原发起调用的 token 才请求取消执行。每 session 同时一个变更操作，新 ID 竞争 CAL-114；Prepared 后首次 Solve 可传已核验参数，已有候选后更改观测/Profile/参数须新 session，绝不篡改 PreparedInputDigest。

MaxRetainedOperations 满时拒绝新业务 CAL-112，不淘汰仍可幂等重放的身份；查询/停止有独立保留的 MaxRecoveryOperations 槽，满则 CAL-112（Stop 仍原子发停止请求并返回 DrainUnknown），不能无限绕过预算。ReadEvents/GetOperationState 为有界内存读取，不开 IO/新槽。所有已接纳 IO（含 QueryReceipt/订阅）在账本有 OperationId 和真实执行任务；观察窗口结束也保留 Pending 记录。Dispose 后实例记录/候选不可再用；发布回执与内容独立由 Store 持有，新实例仍可按原发布 ID 回查。

## 4. 操作入口、状态和事件顺序

### 4.1 同步与异步入口

CPU/native 求解、独立验证、内容存取和只读资格访问均提供异步入口并要求 `CancellationToken`；同步入口仅用于纯内存、有限规模、无 IO 的验证/匹配计算，且不得阻塞 UI Dispatcher 或隐含启动设备操作。以下为 Core Contract v0.2 唯一方法签名：

```csharp
ValueTask<PrepareResult> PrepareAsync(PrepareRequest request, CancellationToken cancellationToken);
ValueTask<CalibrationSolveResult> SolveAsync(SolveRequest request, IProgress<CalibrationProgress>? progress,
    CancellationToken cancellationToken);
ValueTask<ValidationResult> ValidateAsync(ValidationRequest request, CancellationToken cancellationToken);
ValueTask<PublishReceipt> PublishAsync(PublishRequest request, CancellationToken cancellationToken);
ValueTask<ApplicabilityResult> ResolveAsync(ResolveRequest request, CancellationToken cancellationToken);
ValueTask<ReceiptQueryResult> QueryPublishReceiptAsync(ReceiptQueryRequest request, CancellationToken cancellationToken);
ValueTask<DrainResult> StopAsync(DrainRequest request, CancellationToken cancellationToken);
EventReadResult ReadEvents(EventReadRequest request);
OperationStateResult GetOperationState(OperationId operationId);
IAsyncEnumerable<InvalidationNotice> WatchInvalidationsAsync(InvalidationWatchRequest request, CancellationToken cancellationToken);
```

`PublishAsync` 只接受已通过独立验证的 `CandidateArtifactRef`，并要求显式注入资产 Store；它提交不可变的 **PublishedUnqualified** 内容，不签发资格、不改变当前绑定。未注入 Store 时返回 `CAL-113 AdapterFailure`；验证证据缺失或候选状态不允许发布时返回 `CAL-117 CandidateNotPublishable`。不可变资产写入采用幂等 `OperationId`、内容摘要比较和 Store 的原子回执；回执未知时按原 `OperationId` 查询，禁止换 ID 盲重试。资格端口只服务 `ResolveAsync` 和失效通知的只读观察，Binding 端口不属于 Core v0.2 的公开入口。异步操作使用 `ValueTask<T>`，DisposeAsync 使用 ValueTask；有界 ReadEvents/GetOperationState 是仅有的同步查询，不暴露同步 native/IO 入口。

### 4.2 状态机

会话内容阶段与作业生命周期分开。会话阶段仅为 `Created → Prepared → CandidateReady → Validated | ValidationFailed`；Prepare、Solve、Validate 各使用不同 OperationId，是顺序调用的独立作业，不让一个 Solve 作业跨越宿主尚未调用的 Validate。已接纳作业生命周期统一为 `Accepted → Executing → OutcomePrepared → Draining → Drained → ResourcesReleased → Terminal`。OutcomePrepared 是内部结果意图，不允许外部消费临时候选；Solve 终态 CandidateReady、Validate 终态 Validated/ValidationFailed 以及各自失败终态，仅在 ResourcesReleased 后返回；§6.1 的 DrainPending 只是有界观察结果，不是终态。候选内容与引用属于模块内容目录，不属于已释放的临时 native 上下文；后续验证/发布重新打开不可变内容。

Publish 的内部意图为 PublishedUnqualified/PublishFailed/PublishUnknown；查询原回执的 QueryPublishReceipt 是新的只读作业，携带原发布 ID，不复写发布事实。只要存储通信已退出且本地资源归还，就可返回 PublishUnknown；它不代表远端事务已回滚。Resolve 同样在自身资源释放后返回三态，资格 Owner 返回 Qualified 且配置/域/水位都满足时才能形成 QualifiedAssetRef。资格是外部状态，不属于会话阶段，适用性是本次快照，不能成为长期可用缓存布尔值。

非法迁移返回 `InvalidState`; 重复只读请求可幂等；重复提交必须命中同 OperationId 的原回执或返回冲突。取消请求与取消完成不同；进入 `Cancelled` 之前必须等 native 调用结束、清理资源并完成排空。超时后端可能仍在执行时状态为 `Draining`，绝不提前报 `Stopped`。

### 4.3 事件顺序

事件身份唯一用 `OperationId`，不另造 JobId。每个 ID 的 Sequence 从 1 开始严格递增。EventName 封闭集合为 `OperationAccepted/OperationRejected/StageChanged/Progress/OutcomePrepared/DrainStarted/OperationDrained/ResourcesReleased/OperationCompleted/DrainUnknown`。Prepare/Solve/Validate/Publish/Resolve/QueryReceipt 通过 Stage 区分，不定义同义 PublishDrained 或 Qualified 事件。已接纳顺序是 Accepted → StageChanged → 零或多个 Progress → OutcomePrepared → DrainStarted → OperationDrained → ResourcesReleased → OperationCompleted；State 在 OutcomePrepared 为内部意图名，在 OperationCompleted 为本操作结果枚举名。预检未接纳仅 OperationRejected，不打开 provider/native。Draining 未确认可发 DrainUnknown，不能发 Drained、Released、Completed；后续确认后才继续原序列。StageChanged 的 State 只允许 §4.2 的生命周期值，Progress 的 State 为 null。

事件先写入模块有界序列账本，再在锁外投递。进度可合并（软件缺省不超过 10 Hz），阶段/错误/终态不能静默丢弃。订阅者通过 `ReadEvents` 从序列水位补读；超出保留窗口明确返回 Gap 并从权威操作结果重建，不假装连续。UI 调度关闭/订阅者异常只关闭该投影，不改变作业结果；作业排空只等待内核生产者与账本写入完成，不等待 Dispatcher 执行回调或观察者确认。这样关闭 UI 不会与 Dispose 等待形成死锁。已入终态的 OperationId 不再接收进度，重入调用不得在核心锁内执行。

## 5. 错误模型

每个失败包含稳定 `CalibrationErrorCode`、阶段、是否可重试、是否已有持久副作用/回执、关联 ID、短消息资源键；原生安全细节仅留诊断端。原生异常仅留诊断端，不跨公共 DTO 边界直接序列化。最低错误码：

| 错误码 | 语义 | 重试规则 |
|---|---|---|
| `CAL-100 InvalidRequest` | 缺字段、数值非有限、单位/坐标缺失或范围错误 | 修正输入后新请求 |
| `CAL-101 UnsupportedMethod` | 没有已绑定实现/适配能力的方法 | 不能自动换算法 |
| `CAL-102 InsufficientObservations` | 数量/可观测性/覆盖不足 | 按诊断补采，不降低条件 |
| `CAL-103 ObservationRejected` | 输入图、目标点、参考关联或质量无效 | 保留失败来源，修正后建立新观测 |
| `CAL-104 ValidationFailed` | 独立验证未通过或不完整 | 候选保留，不能发布；新证据/修订重验 |
| `CAL-105 NotApplicable` | 配置、用途、域或资格不匹配 | 不重试同一条件；由调用方选择流程 |
| `CAL-106 QualificationUnknown` | 资格权威不可达或返回未知水位 | 可按原查询重试；未知期间不可假定合格 |
| `CAL-107 RevisionConflict` | CAS 预期修订过期 | 读取当前权威状态并重新审查，不自动覆盖 |
| `CAL-108 ContentIntegrityFailure` | hash、依赖闭包或格式校验失败 | 隔离内容；禁止加载和激活 |
| `CAL-109 PersistenceOutcomeUnknown` | 写入结果/回执未知 | 只查原 OperationId，不造新操作 |
| `CAL-110 Cancelled` | 调用方取消且工作已停止/清理完成 | 仅新会话可重做 |
| `CAL-111 DeadlineExceeded` | 预算到期；可能伴随排空 | 先等待/查询 Drain，再决定新会话 |
| `CAL-112 ResourceLimitExceeded` | 图像/内存/句柄/队列等硬上限将超出 | 调整经批准预算或缩小输入 |
| `CAL-113 AdapterFailure` | AsunImage/存储/资格端口失败 | 按适配器诊断与幂等属性处理 |
| `CAL-114 InvalidState` | 非法状态迁移或释放后使用 | 调用方修正时序 |
| `CAL-115 ModuleStopping` | 正在排空/停止，不接受新长任务 | 等待停止完成后重新创建实例 |
| `CAL-116 InternalFailure` | 未归类内部异常 | 不宣称可重试；保留关联 ID |
| `CAL-117 CandidateNotPublishable` | 候选不存在、未完成独立验证、验证证据不匹配或已被撤销 | 保留候选与证据；修正输入后新建候选 |

有效计算但不满足资格条件属于 `ValidationFailed`/`NotApplicable`，不是运行错误。没有异常不代表资格为 `Qualified`。

## 6. 取消、超时、排空、线程和资源

- 每个会话独占可变求解上下文、native handle 和临时文件。非线程安全的 HALCON 句柄不跨请求共享；只读不可变内容若适配器确认线程安全才可共享。
- 调用方提供取消令牌；模块在排队前、每个可中断步骤边界和完成回传前检查。若 HALCON/native 操作不支持中断，取消只撤销结果发布权并等待该调用真实退出，不用 `Task.Run` 外层取消伪造 native 已停止。
- 每次操作有 §6.1 的单调执行 Deadline、有限 WaitLimit 和显式资源预算。预算耗尽进入 `Draining`；资源仍由实际执行者持有，直到实际任务结束且归还确认，或隔离进程边界确认退出（观察等待结束不代表退出）。进程内无法安全强杀的 native 卡死属于宿主隔离/进程监督策略，不由模块谎报完成。
- 请求只传内容引用；图像租约由注入 provider 在执行期间打开，模块拥有本次打开的 lease，适配器只借用，不逃逸或自行释放。租约 CopyPlaneAsync 的写入目的地由调用它的适配器拥有；复制完成前计入双缓冲峰值预算。候选持久内容独立复制/封存后才释放输入租约。未接纳请求不打开 lease，已接纳请求无论成功、取消或异常均在返回终态前归还本次全部 lease；有限观察可以提前返回 DrainPending，但 lease/task 仍在模块账本，不交给调用者清理。
- `StopAsync` 原子拒绝新业务作业、请求取消并按 WaitLimit 等待；等待超时或其取消只结束本次等待，返回 `DrainUnknown` 和 Pending/HeldResources，不代表实际作业停止。Stopping 中仍可调用 StopAsync、ReadEvents/GetOperationState、有限预算查原发布回执；开始 Dispose 进入 Disposing 后禁止新查询/订阅 IO，仅允许内存查询/Stop，已接纳的查询仍须排空。`IAsyncDisposable.DisposeAsync()` 的真实签名是 `ValueTask`，没有结果 DTO、取消令牌或超时参数：它复用停止流程并等待实际释放，卡住的进程内 native 可使它保持未完成；宿主须先用有界 StopAsync 取得状态并按自己的进程监督策略隔离，不能阻塞 UI 等待 Dispose。
- 工厂注入端口是借用依赖：模块只释放自己打开的 lease、上下文、订阅与候选临时存储，不 Dispose 外部共享 solver/store/qualification/diagnostics/provider。宿主负责其生命周期；不能因一个控件或实例关闭而释放另一消费者的存储端口。Stop 后释放候选目录前，成功发布内容已由 Store 独立持有；未发布候选若需保存，由宿主明确导出证据，不能声称 Dispose 后候选仍可验证。
- Core 计算在线程池/native 调度策略运行；不自行创建固定线程池或变更进程级 HALCON 并行参数。UI 适配层只在宿主调度上下文更新控件；回调不得重入修改当前会话。
- 并行隔离按实例和输入租约保证。MaxConcurrentSolves 是该实例作业上限，默认 1，不能声称它限制另一个实例。跨实例共享 native 内存/并发时由宿主显式注入同一个 `ICalibrationExecutionGate`（§9），不建 static 全局信号量。先预约峰值字节再打开图像；输入规模超过上限直接 CAL-112，不允许无界排队。成功、异常、取消均归还预约；Stop 不接纳新预约，但在途预约保持到真实释放。


### 6.1 每入口执行截止、观察等待及迟到资源

每个 Prepare/Solve/Validate/Publish/Resolve/QueryReceipt 请求均显式携带 `CalibrationExecutionBudget`，不从未存在的 session 推导查询预算。Deadline 是**执行上限**，WaitLimit 是**本次调用观察上限**，两者正且有限；本版软件支持 Deadline<=1 h、WaitLimit<=1 h 30 s（不是现场节拍，扩大须合同修订）；WaitLimit>=Deadline，默认 10 min/10 min 30 s，仅为软件限制。所有资源字段正且受宿主上限约束，不适用的资源仍保留为上限，不记录实际消耗为零假充测量。Solve/Validate/Publish 的有效资源上限为本次预算与准备会话资源上限逐项取小；候选内容不保存执行预算，Core 在实例记录保留候选所属会话资源约束。每次操作单独计时，不把 Prepare 的已耗时间重置成 Solve 的任意免费资源；跨流程总上限由宿主另设令牌。Resolve/QueryReceipt 无 session，仅用自身 Budget 与实例上限。

| 入口 | 有限等待及计时来源 | 到期/取消时可返回的观察结果 |
|---|---|---|
| Prepare / Solve / Validate | 完成有界值预检、摘要、幂等核对及分配记录后，在**接纳入队**瞬间用注入 TimeProvider.GetTimestamp 记单调 t0；queue/gate/引用读取/内容 IO/图像/native 均计入 Deadline；剩余时长逐步传给内部链接 token，不因开始下一步重置 | 截止使结果发布权撤销、取消内部任务并 Draining；截至 WaitLimit 仍未释放，分别 PreparationStatus.TimedOut/SolveStatus.TimedOut/ValidationStatus.TimedOut + Completion=DrainPending + CAL-111（原 token 取消为 Cancelled/CAL-110）。这是观察快照，不是终态事件 |
| Publish | 同上，本次预算及会话约束均生效；真正调用 Store 前检查发布权与剩余时间 | 未发送提交且已释放可 PublishFailed；提交已发送且实际结果尚未确认为 PublishUnknown，CAL-109，Completion 依真实资源状态为 DrainPending/ResourcesReleased。取消不等于撤回提交，不交付迟到 Published 回执至已关闭调用 |
| Resolve / QueryReceipt | 本次显式 Budget，自接纳时 t0 开始，读取完整资产闭包/资格/原回执/回读均纳入；即使 CancellationToken.None 也启用内部 Deadline/WaitLimit | 返回 Unknown，QualifiedAsset/Receipt=null，CAL-111 或 CAL-110；若已获完整 Store 事实但内容回读未完成，仍不返回 Found。Completion 标真实释放状态；不返回迟到 Qualified/原发布成功至关闭调用 |
| WatchInvalidations | `InvalidationWatchRequest(OperationId:OperationId,After:AuthorityWatermark?,Budget:CalibrationExecutionBudget)`，首次 MoveNext 接纳/起钟；是有限 lifetime 观察，无隐含永久后台 IO；每次 move 使用同一剩余 Deadline，不能每到通知重置 | lifetime 到期/枚举取消立即关闭投递、记录原因并取消底层 MoveNext；后台 move/Dispose 尚未完成则 Draining；只用本模块账本/操作查询证明释放，不能以枚举结束充当底层释放。需继续观察由宿主在释放后新 ID/水位续订 |
| Stop | DrainRequest.WaitLimit 正且<=30 s（软件观察上限，不限制真正释放耗时），从该调用进入起单调计时；Stop 总是先原子关闭业务接纳并请求取消，再等待；同停止 ID 改 WaitLimit 为 CAL-107，但停止请求仍已生效 | 有限等待截止或 token 取消返回 DrainUnknown/Pending；它只结束该次等待，不取消后台清理。可用新 Stop ID 继续等待，或直接有界 GetOperationState 读原操作 |
| ReadEvents / GetOperationState | 纯有界内存读取，不开端口/不建任务；只读现有实例账本，UnknownOperation 明确表达 | 无隐式 IO，返回当前真实记录；终态结果只在 ResourcesReleased 后可见 |

Deadline 检查以 TimeProvider.GetElapsedTime(t0,now) 的单调耗时为准，UTC 仅作诊断/证书到期判断。内部链接取消包含原操作 token、Deadline、Stop；超时/取消竞争取账本上**最先发生**的原因且只登记一次，后续调用者取消不得篡改原作业意图。重复 ID/同摘要不延长原 t0；重复调用自己的观察窗口从该调用进入起算，但不超过原作业剩余 WaitLimit，原窗口已经关闭则立即给原 DrainPending 快照/已完成结果，不续跑第二任务。外层 ValueTask 只表示一次有界观察；转换 AsTask 只一次后交给运行记录监督，不能多次消费同一 ValueTask。

`Completion=DrainPending` 表示原 OperationId 的执行任务和资源仍由模块持有；必须附 Error，Prepare 摘要可 null、Solve Candidate/Residuals/Domain=null 且 ResourceReport.ReleasedAtUtc=null、Validate Evidence=null、Resolve QualifiedAsset=null、QueryReceipt Receipt=null、Publish PublishedArtifact=null。不可发布进度/候选/资格/Completed 终态；仍可读取非终态 OperationStateResult。释放后的最终结果才能 Completion=ResourcesReleased，事件仍遵守 Drained→ResourcesReleased→OperationCompleted。Publish 的迟到提交事实由 Store 原 ID 保留，最终执行记录仍为 PublishUnknown，宿主通过**新的查询操作**获得该事实；不把原已结束观察悄悄改成 Published。只读资格迟到结果丢弃，新 Resolve 须重查当前水位；不能将其缓存为可用。未释放状态不限于 native，也包括任何未完成 IO/stream read/预约释放。

`OperationStateResult(OperationId:OperationId,Status:OperationExecutionStatus,HeldResources:IReadOnlyList<string>,FinalResult:OperationResultSnapshot?,Error:CalibrationError?,Diagnostic:DiagnosticRef)`；Status=`UnknownOperation/Executing/Draining/ResourcesReleased`。FinalResult 为封闭联合 `PrepareOperationSnapshot(PrepareResult Result)` / `SolveOperationSnapshot(CalibrationSolveResult Result)` / `ValidationOperationSnapshot(ValidationResult Result)` / `PublishOperationSnapshot(PublishReceipt Result)` / `ResolveOperationSnapshot(ApplicabilityResult Result)` / `ReceiptOperationSnapshot(ReceiptQueryResult Result)`；Status=ResourcesReleased 才可非空（Stop/订阅不属于六种业务结果，FinalResult=null，状态/错误/诊断为其结束与释放证据）。未知/在途必须 null，快照只能读原 ID，不引入新计算或第二事实写入者。订阅本模块对外 MoveNext 在投递关闭后返回 false，不等待底层 move；账本 Error 为 CAL-110/111，底层任务尚未退出则 Status=Draining，真正结束后为 ResourcesReleased。无 token 的订阅同样受预算限制，不吞失后台清理记录。

**所有异步迟到交接遵循同一责任：** 在调用 provider/Reserve/reference/content/Store/qualification/底层枚举前，模块或 solver scope 将该原始任务、操作 ID、参数/源 buffer 与资源 reservation 登记到该操作 child-task ledger；当 child-task 完成且返回值已安全接收/释放才移除，不能 await 的观察超时后即丢弃任务。Core 注入的 provider/gate/reference/workspace 为带 operation ID 的跟踪代理；scope 对其内部 native/子任务也须登记并在父任务完成前等待实际结束。Core 可观察代理在途数，父任务提前返回但子任务未归零仍 Draining，资源/作用域/借用依赖保持强引用，不完成父作业。

| 迟到项 | 唯一保管/清理责任与允许交付条件 |
|---|---|
| OpenImageAsync → image lease | 模块跟踪代理接收 late lease，只有操作仍有发布权才借给 scope；已关闭则 await lease.DisposeAsync 一次。lease 归还未知仍记 HeldResources，不能丢给已返回的调用方 |
| ReserveAsync → IAsyncDisposable reservation | 跟踪 gate 代理即使预约忽略 token 后迟到也接收、await DisposeAsync 归还；归还前仍计额度/child count，不发起图像/native，不让新实例误占同容量 |
| workspace OpenReadAsync → Stream / WriteAsync / CopyPlaneAsync | 模块跟踪代理保管 late stream 并 DisposeAsync；Write/Read/Copy 在途期间执行者保留 source/destination 强引用和借用权限，观察结束不关闭仍在读写的 stream/内存。晚完成后丢弃未发布新内容，再释放 stream/内存/预约；scope 必须等其实际退出而不是把外层 canceled Task 当结束 |
| ReferenceResolver / Qualification / Store 的 DTO | 值结果复制后可丢弃，任务内资源由各端口实现清理；契约要求返回前其内部 lease/连接请求真正退出。若不退出，即使操作 token 已取消也由 ledger 继续监督；Qualification 晚到 Qualified 不进入缓存/调用方，Store 晚到回执只能归 Store 原发布事实，不能触发激活 |
| watch MoveNext/DisposeAsync | 模块订阅记录持有原 enumerator/任务，投递关闭后晚通知丢弃，等待 move 真实结束再 DisposeAsync；二者没有确认前不能清空 pending 或 Dispose 外部共享资格端口 |

内部释放没有用超时伪造“已释放”：无法确认则保持 Draining、公开 held 类型/操作 ID，宿主可按已定义进程监督策略隔离，不得再用该 scope/内存。Stop/Dispose 自己不清理仍被 child-task 使用的对象；DisposeAsync 可保持未完成是明确的资源责任，业务请求不能借 CancellationToken.None 无限阻塞调用者。验证断言 CAL.CORE.15–18 覆盖端口忽略取消/迟到/释放闩锁。

## 7. 标定方法及 HALCON/AsunImage 选择

开发者对每一项视觉算法先查项目 `halcon算子手册/operators`（HTML 标题版本应为 HALCON Operator Reference 26.05.0.0），按其语义经 `ImageLibDotNet.cv2` 调用；句柄所有权、异常和取消映射在适配器契约中明确。C# 参数类型、重载或封送方式有实际歧义时才核公共签名或消费项目编译结果，不猜调用签名，不访问 wrapper 内部，也不另接 `HOperatorSet`/`halcondotnet.dll`。

已定位的能力资料入口包括 `calibrate_cameras.html`、`camera_calibration.html`、`set_calib_data_observ_points.html`、`find_calib_object.html`、`threshold.html`、`dyn_threshold.html`、`connection.html`、`select_shape.html`、`edges_sub_pix.html`、`fit_ellipse_contour_xld.html`、`saddle_points_sub_pix.html`、`calibrate_hand_eye.html`、`calibrate_sheet_of_light.html`、`gen_radial_distortion_map.html`、`map_image.html`、`image_points_to_world_plane.html`、`project_3d_point.html`。算子可调用不表示方法已完成适配、验证或取得用途资格。只有 HALCON 26.05 本身存在能力缺口时，才记录准确缺口、官方依据及同样本对比后提交指导变更；不得以未查 C# 重载为由重复核验算子可用性、私自加第二视觉库或自行实现平行标定算法。

求解必须先验证采样可观测性和参考几何、固定参数化模型与分区，再构造私有 native 上下文。残差按像素或物理单位分开报告；低像素重投影 RMSE 不是毫米精度、计量资格或产品放行。独立验证必须使用未参与求解和调参的采样组；同帧、同一靶标姿态拆点不构成独立集。独立域/标准件不满足时只能保留候选或“不足以判断”。任何剔点策略预先冻结，记录被剔点及理由，不允许反复删除难点直到通过。

### 7.1 标定板/参考靶选择（必须显式声明）

标定请求必须声明 `CalibrationTargetKind`、参考靶资产 ID/修订/hash、标称尺寸及单位、制造/计量证书、可见覆盖、允许姿态范围和目标相机模型。目标不能由文件名、图案外观或算法默认值推断。相机模型须注明面阵或线扫及 HALCON 26.05 的具体模型标识；只接受目标相机模型和采集方式都有已绑定适配器的请求。

| 参考靶 | 默认用途 | 检测和索引 | 限制与准入条件 |
|---|---|---|---|
| `HalconRectangularDotPlate`（HALCON 标准矩形排列圆点板） | 面阵及该 HALCON 模型允许的线扫相机内参、畸变和单 FOV 平面几何原生路线 | 使用对应 `.descr` 和 `find_calib_object`；板上 finder 必须可见，按描述文件点表索引 | 保存描述文件、点距、圆径比、行列数、平面度/证书；finder 遮挡、覆盖/姿态不足、饱和或检测多解时拒绝 |
| `UniformSolidCircleGrid`（无定位框、均匀等大实心圆点板） | 面阵及适用线扫相机的二维几何兼容路线 | 受限圆心检测与亚像素定位；必须按已知拓扑生成观测，不能调用 `find_calib_object` 当作带 finder 标准板 | 点径、间距、板面和证书可追溯；全局原点/方向及每点 ID 必须由靶标坐标定义、可见范围或独立外部证据唯一确定；周期重复导致的整体平移/旋转/镜像歧义无法消除时拒绝 |
| `ChessboardCompatibility`（棋盘格） | 面阵及适用线扫相机的二维几何兼容路线 | 棋盘格适配器输出亚像素内角点和稳定 ID，再注入已验证观测 | 固定内角点拓扑、方格尺寸、原点、行列方向和手性；角点数量不足、拓扑歧义、遮挡/反光、多解或边缘覆盖不足时拒绝 |
| `MeasuredPlane/Artifact` | 结构光、平面高度、3D/计量方法所需的物理参考 | 由对应物理模型读取平面/尺度/高度证据 | 不自动授予二维内参、手眼或拼接资格；不能把二维 homography 当作深度模型 |
| `AprilTagBoard`/其它编码靶 | 手眼或其它方法中的姿态/稀疏身份辅助 | 依赖明确编码 ID 和姿态解算 | 不作为本节三种二维标定板的隐式替代；须由具体方法 Profile 明确接收和验证 |

三种二维标定板均需提供可追溯的坐标系：稳定原点、X/Y 或行/列轴向、手性、尺寸单位、靶标修订/hash、平面度和证书。`HalconRectangularDotPlate` 是 HALCON 原生优先路径；无框周期圆点板和棋盘格是显式支持的适配路径，不声称能由 `find_calib_object` 直接检测。目标类型、拓扑、间距、方格/圆径、证书或平面度证据变化均产生新靶标修订和新的标定资产/资格，不能沿用旧 hash。

所有用于几何求解的参考靶必须把设计名义几何与计量实测几何分开保存。证书/目标几何引用应提供点位实测坐标或可审计的偏差模型、坐标系和单位、测量不确定度、平面度/稳定性、参考温度及证书修订；只有标称 Pitch 而没有适用的实测几何证据时，不得把理想等距点阵当作无误差真值。若目标类型或 HALCON 描述格式只表达理想规则图案，实测点位修正必须作为同一目标修订下可解析的独立几何数据参与对应点求解及验证，不能暗改描述文件或拟合后再以板误差解释残差。安装重复性或温度变化若会影响方法有效域，也须列为目标/资格证据；缺项时缩小用途或拒绝资格，不以标称值补齐。

无框等大周期圆点板有固有的格点置换歧义：观测到相同圆心集合本身不能证明靶标坐标原点、行列方向、整体平移或旋转/镜像方向。只有靶标注册表中固定的板坐标约定，加上当前图像/序列中可见的非对称边界/缺点编码，或独立且同步的相机/靶标位姿与坐标证据，足以唯一给出每个检测圆心的稳定 `TargetPointId` 时，才可接受。若所有可见证据仍与另一组靶标点号映射同样相容，必须返回 `CAL-102 InsufficientObservations` 或 `CAL-103 ObservationRejected`；严禁按最近邻、采集顺序、运动指令、相邻 FOV 的上一点号或“最像的方向”猜索引。这里的 `TargetPointId` 只表示注册靶标坐标内的稳定点身份，不表示跨 FOV 工作区/拼接点号；后者由 mosaic 负责。

棋盘格必须固定 `InnerCornersX`、`InnerCornersY`、`SquareSize`（带单位）、`OriginConvention`、`RowDirection`、`ColumnDirection`、手性、角点检测方法/版本及稳定 ID。检测输出必须匹配指定拓扑；棋盘纹理周期造成的行列翻转/平移不能由图像唯一排除时，需有可见边界、已知姿态或独立位姿先验消歧，否则拒绝。点数/覆盖不足、严重遮挡或反光、角点亚像素质量不达预先冻结标准、边缘/角落覆盖不足或姿态激励退化均保留观测与原因并拒绝，不允许删点凑数或自动改变阈值。

**目标专用检测顺序（参数须由方法 Profile 固定）：**

1. 无框实心圆点板按 Profile 选定的灰度/颜色通道和前景极性做单一受限分割；均匀照明用固定 `threshold` 区间，照明缓变只有在同一代表集验证通过后才能固定为 `dyn_threshold`/局部阈值路线。随后以 `connection` 分离连通候选，以 `select_shape` 按证书给出的投影面积范围及预先验证的形状条件筛选；不在运行时轮换算子或放宽区间。对完整候选轮廓使用 `edges_sub_pix` 形成亚像素边缘并由 `fit_ellipse_contour_xld` 拟合投影椭圆，按拟合残差、轴比、边缘覆盖和分割区域一致性拒绝粘连、破损、截断、过曝/欠曝或多解。**斜视平面上的物理圆心投影通常不等于图像椭圆中心**：适配器只能在近法向视图使用已验证的中心近似，或在已具独立合格内参的透视面阵相机上使用 get_circle_pose（真实半径、center_normal 输出），用独立板面/正深度证据从两解中恰好选出一解，再以 project_3d_point 投影其三维中心；不得把椭圆中心直接当成标定点。绕圆法向的角度无法由单圆解出，不能把它当点阵方向证据。内参未知时只允许有独立偏差预算的近法向路线；禁止用本次待估内参反复校正圆心后自证内参正确。远心/线扫不套用该透视圆路线。两解仍相容、滤波中心偏差越界或无法独立证明近法向近似质量时 CAL-103，不新增自制 conic 优化器。投影尺寸/轴比范围按已知相机与姿态域冻结，不能因候选失败临时放宽。
2. 棋盘格固定使用 `saddle_points_sub_pix` 的 gauss 方法产生亚像素鞍点候选；根据黑白交替棋盘的局部极性、邻接几何和声明的 `InnerCornersX/Y` 按固定候选 ID 顺序构建满足拓扑的有限候选映射，候选数量达到 Profile.MaxTopologyCandidates/MaxIdentityMappings 即停止并 CAL-112，不能截取首解称唯一。只在恰有一个映射与规定原点、行列方向/手性以及可见边界或独立姿态证据一致时输出角点 ID。图像坐标近邻只能用于构造候选邻接，禁止用贪心最近邻、按行/列排序或采集顺序单独决定 `TargetPointId`；零解、多解、断裂拓扑、遮挡跨越关键交叉点或角点质量越界均拒绝。
3. 所有分割区间、形状/残差/亚像素质量界、区域覆盖、角点响应界和允许遮挡条件须在独立验证前冻结，来源绑定相机/镜头/照明、靶标证书、工作距离/姿态与 HALCON 26.05 版本。至少用合格、无结果、低对比、亮度变化、反光、模糊、污损、局部遮挡、边缘裁切和方向歧义样本验证接受/拒绝行为；没有已批准的量化界时不猜常数，方法保持 `PreparationIncomplete`，不得发布可用资格。

上述分割/亚像素算子仅定义无框圆点板与棋盘格适配器的候选路线，不表示代码或 API 已验收；名称、语义和参数以本地 HALCON 26.05 operator 页面为准，调用经 `ImageLibDotNet.cv2`。HALCON 标准板仍固定走 `.descr`/`find_calib_object`，不经过自定义圆点路线。


**二维码/编码与几何资产职责：** 二维码、Data Matrix 等板载编码是身份辅助，不是第四类通用几何靶。解码只消费 [barcode 唯一指导](../barcode/DEVELOPMENT-GUIDE.md) 的只读观察，由宿主/参考件 Owner 将有效载荷映射到明确的 TargetId/Revision/Digest；本模块保存解码观察、原图 hash 和映射证据于 ObservationRef.IdentityEvidence，不生成编码、不训练码模型、不从解码文本猜尺寸。ReferenceGeometry 的名义内容附带 `TargetIdentityMetadata(CodingScheme:string,ExpectedPayloadDigest:Digest,RegistryRevision:RevisionId,CodeToTargetFrameEvidence:ContentRef?)`；仅需识别板身份时最后一项可空，要用于原点/方向消歧时必须非空并在当前图/同步序列可验证。无读码、多个冲突 ID、载荷字节不可用或注册映射不唯一，保持未知/拒绝，不能按“最像的板”继续。二维码定位角不直接替代有实测坐标的圆心/棋盘内角点；若将编码角点作为计量点，必须另有专用方法、实测几何、定位偏差与独立验证，本 v0.2 返回 CAL-101。跨 FOV 全局点号和二维码辅助 Tile 身份恢复归 mosaic；本模块只验证单图点号与靶坐标的一致性。

### 7.2 单相机/FOV 几何标定、相机资产和恢复条件

本模块生成一个相机配置下的标定资产：面阵相机可发布内参/畸变及其适用 FOV 的局部平面几何；线扫相机可发布所选 HALCON 线扫相机模型的参数及经验证的局部几何。资产按单个相机身份、序列号/配置修订、分辨率或线传感器布局、ROI、镜头/焦距、曝光/采集模式、工作距离和有效域独立管理。Core 不建立跨相机组事实，也不把多相机校正结果汇成组资产；宿主负责组合多个独立相机资产及其组关系，并保留各自引用和资格。

**光学资产按兼容配置复用，不按生产 FOV 或 Tile 重复标定。** 同一相机及其镜头、倍率/焦距、焦点、安装姿态、传感器读出模式和工作距离等方法敏感配置保持一致，且新图像仍在资产声明的有效域内时，可在不同 XY 生产位置复用同一相机内参、畸变和相机坐标系局部映射；相机平移到另一个 FOV 本身不要求重新求解光学参数。生产中不得逐 FOV 调 `calibrate_cameras` 或另建一份内容相同的光学校正资产。每帧仍须保留其相机身份、采集配置、原始像素坐标和 crop/像素布局变换，供 mosaic 根据实际位置形成各自的全局 Pose。

复用判定由方法版本化的敏感字段表执行：至少区分几何身份字段（相机/传感器模式与布局、分辨率、ROI/binning、镜头/焦距/倍率/焦点、安装方向、工作距离或线扫配置）和观测质量/资格域字段（曝光、增益、照明、温度、速度等）。某字段只有被该方法明确声明为不影响几何且其质量域已覆盖时才能变化后复用；不得把“通常不影响”当作默认。未声明的字段或缺少实际快照时返回 `Unknown/NotApplicable`。敏感字段变化时须创建新候选并独立验证；只有方法已冻结且验证过的确定性坐标归一化（例如带准确来源的严格 crop-origin 变换）才能生成派生引用，禁止按宽高比、相邻 FOV、像素尺寸近似或运行时拟合悄悄缩放旧资产。

复用范围止于相机坐标系的成像模型/畸变及其有效域。随相机 XY 位置变化的相机—载台/工作区绝对位姿和误差补偿不属于可复制的光学矩阵，必须由 `mosaic` 对该次实际运动位置求值。若焦平面、倾角、工作距离或目标表面变化超出本资产已验证的局部几何域，则不能只因内参仍相同就宣称 pixel-to-world 关系有效。

HALCON 26.05 `calibrate_cameras` 对 calibration-data model 中配置的相机模型求内外参数；`camera_calibration` 说明包含线扫模型及其特定限制。因此本模块支持面阵与线扫两类方法，但不将所有相机型号或采集模式视为等价：必须根据 26.05 文档确认所选模型的约束、参数化与可观测条件，并通过目标消费项目的适配与标准件验证。线扫请求须携带与行采集同步的必要运动/编码器时间证据；这里验证并固化相机模型所需的几何输入，不校准跨 FOV 拼接网格、扫描轴运动误差或工作区全局位置误差，这些由 `mosaic` 唯一指导负责。

**公共求解与验证顺序：**

1. `PrepareAsync` 校验相机模型/类型、靶标描述、证书摘要、单位、传感器布局、相机配置、采样分区及方法适配器；线扫同步证据缺失、靶标类型不匹配或模型未绑定时返回明确错误，不调用 HALCON。
2. 先按靶标专用适配器提取/验证圆心或内角点。HALCON 标准矩形圆点板可用 `.descr`/`find_calib_object`；均匀实心圆点板和棋盘格使用显式适配器形成有稳定点号的观测，再通过已核对的 `set_calib_data_observ_points` 路线注入。未经唯一消歧的 ID 映射、缺少拓扑或不满足边缘覆盖/姿态条件时拒绝。
3. 对每个拟合姿态保存原始图/线帧来源、相机配置、目标修订、可见点和点 ID、覆盖、曝光/饱和/反光/遮挡诊断、姿态及线扫同步证据。按 HALCON 26.05 目标相机模型及冻结参数调用 `calibrate_cameras`；不自动切换面阵/线扫模型、畸变阶数或靶标。
4. 独立验证使用未参与求解和调参的采样组/姿态及已知物理标准；输出重投影像素误差、局部物理误差和适用域，分别记录，不以低像素 RMSE 推导计量资格。边缘/角落覆盖、目标模型限制或线扫运动同步验证不满足时不得发布可用于测量的资格。
5. 只有独立验证通过才能发布不可变的未资格资产；用途资格由相应 Owner 单独授予。相机配置、靶标、求解模型或观测变更产生新 session/hash，不原地修补旧资产。

**失败和恢复：**检测失败保留失败观测，不降阈值、不换靶标、不缩减点集凑数。只有请求预先声明的同一靶标重采/重放策略时，才可依该策略恢复；重采或修订创建新 session。人工审核后的固定点观测可以作为离线输入，但必须携带操作者/来源、点号映射、修订和内容摘要，不能跳过独立验证。任何圆点阵或棋盘格在全局点号/方向无法消歧时均拒绝，不因 HALCON 求解器返回数值而继续。

面阵与线扫均需覆盖中心、边缘/角落及相机模型要求的有效姿态范围。拟合集和独立验证集按独立采样组分开；同帧拆点不构成独立验证。靶标物理尺寸、平面度、温度稳定性和相机配置属于资产证据。显示校正、相机/FOV 几何和 3D 计量资格是不同用途，不得相互推导。

#### 7.2A FOV 局部几何与拼接责任边界

FOV 局部几何只描述一个相机在声明配置和有效域内，从该相机像素坐标到其观测平面/局部相机参考系的变换，以及畸变校正。它可以由校准靶在同一 FOV 内的多姿态观测求解，并作为 `calibration-assets` 的相机资产组成部分。对线扫相机，仅采用其 26.05 相机模型所定义且经验证的成像/坐标参数；不能借用面阵投影模型套算线扫图像。

以下内容归 `mosaic` 唯一指导和资产责任：跨 FOV/相机的共同拼接几何、全局工作区坐标映射、重叠区注册与闭环、扫描/运动轴误差、编码器误差补偿、拼接 cell/瓦片关系及大图测量坐标资格。本模块可向 mosaic 提供已发布的单相机标定资产引用及其适用域；不得持有这些跨 FOV 参数、产生 `PositionTransformArtifact`、规划运动扫描/验证轨迹，或把单 FOV 平面映射声明成工作区/产品坐标。多相机资产依旧逐相机发布，宿主组合关系由宿主维护；mosaic 消费所需引用完成自身的跨视场方法。

一张板跨越多个 FOV 的图像或一组逐站采集帧可以提供 mosaic 的标定观测，但不会因此改变观测资产的责任归属：`calibration-assets` 只负责每个相机/FOV 的局部相机模型输入；全局点号跨帧关联、平台反馈、运动误差拟合、独立往返/闭环检查和补采 cell 规则全部属于 mosaic。发现本指导与 mosaic 指导有相反责任文本时，按模块唯一会话修订对应指导；本节不授权本会话改写 mosaic 文件。

#### 7.2B 独立 HandEyeMethodProfile：路线、姿态链与拒识（2026-10-06）

**增量采纳判据：** 现行指导只列手眼用途，没有定义求解选项、六自由度观测、噪声诊断及取消条件。本节依据本地 HALCON 26.05 [calibrate_hand_eye](../../../halcon算子手册/operators/calibrate_hand_eye.html) 的 Description、Preparing the calibration input data、Checking the success of the calibration、Recommendations 和 Execution Information 补足这些语义；因此采纳该方法增量。没有同样本实测，不能宣称 stochastic 或新增设计已优于现行机台算法。来源 §1.1 的 HALCON 24.11 参数基线，以及将绝对 X/Y 直接解释为 `tool_in_base_pose` 的表述**不采纳**。

**独立适用域：** 本 Profile 处理相机/传感器、机器人 base/tool 和标定对象之间的固定刚体变换，不处理 XY 周期点阵跨视场关联、工作区 cell、平面畸变或拼接。线性轴位置反馈或 X/Y 平移加零值 Z/Rx/Ry/Rz 不会成为具有足够激励的六自由度 `tool_in_base_pose`。没有经核验的完整刚体姿态与独立尺度证据，手眼分支预检拒绝。Profile 的采样、计算和验证不授权机器人运动、重采命令、安全动作或质量放行。

| optimization_method | 技术选择与输入条件 | 限制、验证和恢复 |
|---|---|---|
| `linear` | 官方说明为快速线性路线；可对 camera 或有可信物体姿态的 3D sensor 做受限基线对照 | 实际场景可能不够准确；不得因耗时短自动成为运行路线。与 nonlinear 使用相同 fit/check 数据比较变换链误差、独立空间误差和资源；不足时结束为验证失败，不偷偷换路线 |
| `nonlinear` | 本模块手眼 Profile 的默认设计路线；官方说明可获得更准确的标定 pose；使用成对 `obj_in_cam_pose` 与高精度 `tool_in_base_pose` | 默认选择不构成精度保证。允许方法 Profile 显式选择其它路线，但必须创建新求解修订并复验，不覆写候选 |
| `stochastic` | 对全部测量观测及输入 robot poses 的不确定性建模，同时使用提取的 calibration marks；**只用于 camera + calibration plate** | 不用于仅提供 3D 物体姿态的 3D sensor，也不能只给相机物体 pose 却不提供圆点观测。关节机器人可能同时精化手眼 pose 和相机参数，所有变化须输出新引用；不原地更新既有内参 |

**采集字段与参数来源：** 下表是该方法的必要语义字段，按独立 Profile 保存；不将它们塞入 v0.2 的面阵 DTO、`Options` 字典或 XY 位置请求。专用请求/结果合同见 §7.3A，当前 Core v0.2 仍对 hand-eye 请求返回 `CAL-101 UnsupportedMethod`，仅新 Specialized API 1 接收该分支。官方算子能力已确定，不再核验 AsunImage 是否包含算子；只对实际 C# 参数/重载/封送歧义设置待适配门，不猜 `ImageLibDotNet` 签名，不扫描 wrapper 源码。

| 字段组 | 类型/单位和完整性约束 | 来源 |
|---|---|---|
| Profile 身份 | `MethodId=HandEye`、方法修订/hash、`optimization_method` 三选一；不得缺省到 stochastic | 本节选择基线和冻结的消费者方法 Profile |
| 系统拓扑 | `MovingCamera` / `StationaryCamera`；robot 类型 `Articulated` / `SCARA`；明确 camera / 3D sensor。关节机器人分别映射 `hand_eye_moving_cam` / `hand_eye_stationary_cam`，SCARA 分别映射 `hand_eye_scara_moving_cam` / `hand_eye_scara_stationary_cam` | 实际固定安装和坐标链；不是 UI 根据图像猜测 |
| 坐标约定 | base/tool/camera/object 四个稳定 frame ID、左右手性、变换方向、translation 单位、完整 rotation convention；HALCON pose 类型/旋转次序及来源转换修订 | 设备公开姿态定义与参考件坐标定义；不能只传无类型六个数 |
| 实际 tool pose | 每次观测的 `tool_in_base_pose`：三平移、三旋转/经核验可转换的完整刚体姿态；保留原姿态和单位，适配器统一平移为 m、HALCON 旋转为 degree | 曝光时刻实际机器人反馈；附设备实例、base/tool 配置修订、axis epoch、硬件时刻、配对 ID、同步误差及高精度证据；命令 pose 不代替反馈 |
| 视觉观测 | 图像/参考件 hash、物体到相机姿态 `obj_in_cam_pose` 及估计来源；camera+plate 另含每图 Row/Column（pixel）、稳定 mark ID、有效/遮挡/拒识原因 | 原帧与参考板几何；同一 `PoseNumber` 绑定对应视觉观测和 tool pose，禁止覆盖/错配 |
| 内参与靶标 | 相机内参引用/修订、像素布局、参考板描述/点表/证书、物理尺度/平面度；显式声明冻结已有内参或估计新内参，默认冻结；SCARA 要求预先完成相机标定且不得选择重估 | 原资产与参考件证据；不能给 3D sensor 伪造板点，不能让 SCARA 用近乎平行观测自证内参；估计新内参只能输出新候选引用 |
| 噪声和修正 | robot pose/mark 定位精度证据、重复观测、误差来源及单位；stochastic 原输入和 corrected tool poses/误差分别保存 | 方法实验与 HALCON 输出；不编造六维 covariance，不把残差当输入不确定度 |
| 采样/检查 | fit/check 的物理采样组、姿态数、旋转轴变化、视场/工作距离范围、留出方案和允许退化政策 | 采样前冻结计划；补采不能使原 check 数据回流 fit 后仍称独立 |
| 预算/验收 | 有限 deadline、驻留/handle/点数/并发上限、同步误差限、平移/角误差界、空间检查和覆盖条件 | 软件预算与消费者验证 Profile；物理门限未知时只阻断该资格，不设虚假默认 |

**pose convention 与链方向：** 采用 `A_H_B` 表示将 B 坐标中的点变换到 A；旋转/平移组成刚体变换，乘法顺序不可交换。机器人输出可能对应 HALCON pose type 0/2（`gba`/`abg`），这只是官方常见映射说明，不是所有机器人都通用的默认。ZYZ、四元数或其它表示须按其实际定义转换为矩阵并核方向/手性、正交性和单位后再转 HALCON pose；未经确认不得交换角顺序。输入原值与转换证据都保存。

```text
MovingCamera:
camera_H_object = camera_H_tool * inverse(base_H_tool) * base_H_object
输出固定量: tool_in_cam_pose (camera_H_tool), obj_in_base_pose (base_H_object)

StationaryCamera:
camera_H_object = camera_H_base * base_H_tool * tool_H_object
输出固定量: base_in_cam_pose (camera_H_base), obj_in_tool_pose (tool_H_object)
```

**采样建议与可观测性：** 官方说明三组是理论下限，通常建议至少 10 个充分变化的 pose；stochastic 建议至少 25 poses。25 是该方法的采样建议，**不是 HALCON 参数硬限制、不是 Qualified 的充分条件、不是面阵内参/平面/XY 点阵的门槛**。计划少于建议值时必须显式记录理由与方法验证证据；缺该证据则 `CAL-102 InsufficientObservations`，不能凭“算子返回了结果”接受。关节机器人应具备至少两个不同旋转轴，页面建议相对旋转至少 30 degree、60 degree 更好；这是实验设计参考，实际运动由设备 Owner 规划，模块不发动作。大量相同 pose、仅平移 XY 或单轴旋转不能充当一般六自由度覆盖。SCARA 的单轴旋转须走对应 SCARA setup，Z 平移的固有歧义不能默认为已辨识；缺独立高度/接触标定证据时保持限定域/未验证，不进入完整手眼 Qualified。

**固定处理顺序：**

1. 校验安装拓扑、setup、方法/传感器组合和坐标定义，再核 pose/image 配对、tool pose 精度、标定板/内参证据及资源预约；缺字段/错误单位为 `CAL-100`，错方法为 `CAL-101`，同步/反馈不可信为 `CAL-103`。stochastic + 3D sensor 在 native 前拒绝。
2. 检查 fit/check 分组、姿态/旋转激励与可观测域；退化或不足为 `CAL-102`。重复帧/pose 不补足独立样本数，不能靠增大同轴采样数消除退化。
3. 私有上下文按目标 setup 执行 `create_calib_data`；camera+plate 设置相机与标定对象，经 `find_calib_object` 或已确认的观测注入路线存图点/物体 pose，再以 `set_calib_data` 的 tool/PoseNumber/`tool_in_base_pose` 配对存入实际 tool pose。关节机器人冻结已有内参时，按官方 `set_calib_data(CalibDataID,'camera','general','excluded_settings','params')` 排除相机参数优化；显式估计新内参时保留相机标定/精化并输出新引用，SCARA 始终使用已标定内参。设置 model/general/`optimization_method` 后调用 `calibrate_hand_eye`。3D sensor 仅由批准的 pose 适配器输入可信 `obj_in_cam_pose`，只走 linear/nonlinear。调用经 `ImageLibDotNet.cv2`；此处是官方算子流程，不声明具体 C# 重载已编译。
4. 用 `get_calib_data` 读取拓扑对应固定变换、实际内参修订及误差。`Errors` 四项顺序为平移 RMS、旋转 RMS、平移最大值、旋转最大值；平移随输入单位（本适配规范为 m），旋转为 degree。另有 camera 重投影误差（pixel）。stochastic 的 corrected-tool 链误差须与原 tool 链误差分别保存；不能以优化后更低的误差抹去原反馈精度问题。
5. 冻结求解量，使用未参与拟合/调参的成对 pose/image 重新验证对应链等式、独立物理位置/角度和边界域。有限残差与拟合平均值不足以证明精度；方向、单位、同步、留出误差或 SCARA 未辨识轴任一不满足，`CAL-104 ValidationFailed`，保留候选及原因，不发布为 Qualified。
6. 验证通过后仍沿 Candidate → PublishedUnqualified → 外部资格 Owner → Resolve 的分层链；资产绑定方法、拓扑、frame ID、pose convention、输入精度证据和工作域。更改安装/base/tool、内参、同步或方法修订时重新解析资格；模块不产生设备动作或产品判定。

**取消与恢复：** 26.05 页面正文明确 stochastic 支持取消 timeout/interrupt；Execution Information 也给出可重入/全局线程范围、内部并行和对 `CalibDataID` 的写入。可重入不允许同一可变上下文并发；每作业独占句柄。宿主 `CancellationToken` 不自动等价于 HALCON 中断，实际中断/timeout 机制的 C# 类型或映射未确定时设 `AdapterCancellationBindingPending`，依正文 §6 撤销结果发布权并等待 native 真实退出。对于 linear/nonlinear 不把正文针对 stochastic 的取消说明推演为已验证停止行为。中断/超时后无论算子是否返回局部参数，都不能作为完整候选发布；排空和资源释放完成后才结束为 `CAL-110`/`CAL-111`，否则保持 Draining。无法确认退出或租约归还时记录 `DrainUnknown`，保留隔离和资源所有权，禁止重跑、复用上下文或报告 OperationDrained。确认退出并释放后，重新执行使用新 attempt/context，保留原取消结果；不得静默回退到 linear。

| 定向场景 | 输入、处理与可判定断言 |
|---|---|
| 正常移动/固定相机 | 成对实际 tool pose 与板点、冻结单位/拓扑；求解后分别代入对应链，留出物理检查通过；输出两个固定量及独立误差，发布只得 PublishedUnqualified |
| stochastic + 3D sensor | 缺板点、只有 3D pose；预检 `CAL-101`，native 调用次数为 0，不自动改 nonlinear |
| 25 个重复 pose / XY-only | 数量达建议但无有效旋转激励或六维实际姿态；`CAL-102`，没有手眼候选；单相机/FOV 标定仍按 §7.2 的独立方法与证据判断 |
| pose 单位/角次序/配对错误 | m/mm、gba/abg 或曝光配对不符；预检拒绝或留出链失败，不能自动绝对值/交换角/取最近 pose 修复 |
| 有噪声 tool pose | 相同输入比较三路线，保存原与 corrected 误差、独立检查及资源；仅训练代价下降不授资格，精度证据缺失仍拒绝 |
| SCARA 未辨识 Z | 对应 SCARA setup、单轴旋转，但没有独立 Z 证据；输出受限候选/限制说明，不声称完整六维 Qualified |
| native timeout/取消 | 发布权立即撤销，记录请求与实际退出/释放时刻；迟到参数不得发布，Draining 未完成不能报 OperationDrained |
| 资产升级/第二消费者 | 新内参/方法/安装修订产生新 hash；旧消费者按旧引用可查历史，当前资格重新解析；相机工具和 robot 工具只交换变换/证据引用，不共享设备句柄或产品逻辑 |

**来源与审核范围：** 只读来源 `H:\docs\50-test\在线AOI采检拼显并行架构与竞品证据研究_2026-10-02.md` §1.1，SHA-256 `4851d0540935a9b1f3bf6bde29842b5c3b58eaa19554c1ebd51b86510df6d837`，已与 [全量 source-manifest](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json) 中同路径条目及原件实际字节核对。只吸收上述手眼方法增量；报告其余章节、竞品性能、24.11 版本行为及生产结论不随本节采纳。本文保持 `DesignReview / Prep`；无真实 HALCON 执行、代码/性能/HIL/计量或生产验收结论；手眼专用 DTO/错误映射现见 §7.3A；真实输入/公开调用编译/native/资格只阻断对应切片，不阻无关二维 Core。

运行时不要求把标定板留在每一帧中。运行帧只消费已发布且适用的标定资产；若相机、镜头、分辨率、ROI、binning、焦距、工作距离或机械安装改变，必须重新解析适用性。没有合格资产时，允许 `DiagnosticOnly` 的像素/相对结果，但不得返回可用于物理计量、拼接世界坐标、设备定位或生产放行的映射；禁止以单位阵、最近资产或默认棋盘格尺寸回退。

变换方向、坐标系、尺度、姿态单位和有效域随资产显式保存。单平面映射不得用于离面点；相机内参不自动成为外参、手眼、三角测量、平场或高度资格。ROI、分辨率、binning、镜头/焦距状态或相关配置改变时重核适用性；映射与资产 key 至少绑定这些敏感项、方法/资产 hash、输出布局和插值设定。不得猜测 map 内存布局。原始帧和变换后投影分别保留，显示图不得替代计算输入。


### 7.2C 相机模型、实测点注入和线扫约束

本版模型白名单如下。初始模型必须由设备/光学事实给出；普通镜头优先 division，polynomial 只有相同代表集比较并显式采用新 Profile 后使用，不在失败时自动增加畸变自由度。远心模型不能通过改 Focus 名称冒充。其它 tilt/hypercentric 等 HALCON 能力未被本版 Profile 接收，返回 CAL-101，不表示 HALCON 不支持。

| 模型 | 相机参数向量（模型名之后的固定顺序） | 本版估计约束 |
|---|---|---|
| `area_scan_division` | Focus,Kappa,Sx,Sy,Cx,Cy,ImageWidth,ImageHeight | Sy 固定；尺寸固定；估计项显式列出 |
| `area_scan_polynomial` | Focus,K1,K2,K3,P1,P2,Sx,Sy,Cx,Cy,ImageWidth,ImageHeight | Sy/尺寸固定；P1/P2 同组选择 |
| `area_scan_telecentric_division` / `area_scan_telecentric_polynomial` | 对应面阵序列中 Focus 换为 Magnification | 不把未知深度当作可辨识 Z；采用模型规定的有效域 |
| `line_scan_division` / `line_scan_polynomial` | 对应透视面阵序列后加 Vx,Vy,Vz | Sx、Sy 和尺寸固定；运动向量按相机 frame 的 meter/row，显式选择可估计分量 |
| `line_scan_telecentric_division` / `line_scan_telecentric_polynomial` | 对应远心面阵序列后加 Vx,Vy,Vz | 单相机 Vz 不可观测，初值固定 0、不得估计；多相机共运动解不属于本模块 |

Focus/Sx/Sy 单位 meter，Magnification 无量纲，Cx/Cy/尺寸单位 pixel（尺寸值还须为正整数），Kappa/K1 为 meter^-2、K2 meter^-4、K3 meter^-6、P1/P2 meter^-1；Vx/Vy/Vz 为 meter/row。CameraParameter.Name 固定使用表中名称。EstimatedParameters 同名字段映射为官方小写 `focus/magnification/kappa/k1/k2/k3/cx/cy/sx/sy/vx/vy/vz`，P1/P2 必须成对映射 `poly_tan_2`，禁止传未列名或 all/params 等宽泛别名造成额外优化。每次构造私有 model 时先排除全部可配置内参/运动项，再仅加入声明的估计项，保留单相机外部 pose 的官方默认排除；calib_obj_pose 按该模型估计靶姿态。不要误将 model/general/optimization_method 用于相机求解，它是手眼选项。输出完整参数向量与实际优化项，检查有限、合法、可观测域和独立误差；calibrate_cameras 的 Error 是像素 RMSE，没有可用 MaxIterations。

标准板路线用一个仅检测用的私有模型设置原 .descr，经 find_calib_object/get_calib_data_observ_points 取稳定索引与每图观测；另一个仅求解用私有模型通过 set_calib_data_calib_object 设置经证书修正的 XYZ 点表（统一 meter），再按同一稳定点表一次性 set_calib_data_observ_points 注入 Row/Column/Index/Pose。无框点阵和棋盘直接走后一模型。不能检测使用实测修正但求解仍用理想 Pitch。实测点位变化、证书或映射修订变化纳入 InputDigest；姿态初值是数值求解初值而非独立真值。透视面阵近水平点表采用 vector_to_pose 的 planar_analytic，非共面实测点表采用 analytic；远心采用 telecentric_planar/telecentric 对应分支。线扫必须提供与第一行相符的可信 ObjectInCameraInitialPose，不套用面阵姿态初始化；其实际 C# 调用/收敛由线扫适配门验证。算子理论最小点数与资格采样最小组数分开，后者来自 Profile。

HALCON 线扫模型要求直线恒速、姿态恒定且各图运动向量一致；位姿指第一图像行，相机 y 方向按文档约定使 Vy 为正，坐标为右手系。加减速、反向未归一、行丢失/重复、时钟 epoch 不同、各组速度不同或同步误差无证据时 CAL-103，不把 meter/second 直接传 Vx/Vy/Vz；从时间/编码器换算 meter/row 必须保留实际行间隔及转换修订。运动误差/时空重采样归 mosaic，本模块不拟合轴补偿。不满足该模型时仅拒绝该方法，不能静默换静态面阵模型。

### 7.3 结构光及其它专用方法的限定门

HALCON 26.05 calibrate_sheet_of_light 处理特殊三维参考物的一张 disparity image：参考物须符合 create_sheet_of_light_calib_object 的斜面/截锥 DXF，设定 calibration_object 和 camera_parameter，当前该算子仅支持 area_scan_division；运动方向、截锥四面可见和有效域无孔条件按官方页面。create_sheet_of_light_model → set_sheet_of_light_param → measure_profile_sheet_of_light/已观测 profile → calibrate_sheet_of_light → 读取结果的链必须使用私有 model。返回 Error 是点到参考物的 RMS（meter），不是二维重投影误差，也不构成全域独立计量资格。普通二维棋盘、任意平面或 QR 板不能直接代入该算子。此方法、手眼和辐射/平场/显示校正的专用 DTO、输入模型和验证计划现见 §7.3A；v0.2 通用相机联合仍不承接它们，必须使用新 Specialized API 1。它们保持整模块规划范围，后续门只阻对应切片，不阻二维资产 Core；不得用二维 homography 实现结构光深度。

### 7.3A 专用方法的封闭软件合同（Specialized API 1）

本节补齐原 CAL-A4 的内部设计，不以“后续 Owner”代替软件决策。范围是 §7.2B 手眼、§7.3 线激光特殊参考物、相机相对辐射响应/暗场平场和显示校正资产；投影条纹共同标定仍唯一在 §7.4。其它多相机组几何/工作区/运动误差归 mosaic；未明确的其它三维物理模型、彩色 ICC/光谱仪控制和设备 LUT 写入不因“3D/显示”字样获得批准范围。本模块可接收外部形成的合法校正内容和证据，但不能给未知方法补通用 Qualified。首版所有方法都有独立输入/结果，v0.2 仍对这些请求 CAL-101，不把新增数据塞进旧二维 DTO。namespace=`Asun.Modules.CalibrationAssets.Specialized`；以下为规划合同，尚无代码/真实公开调用编译结果。

#### 7.3A.1 公共包络、字节与端口

使用 §3.7 原语/record编码规则，但独立头 `calibration-specialized-v1`。`SpecializedCandidateRef(Id:AssetId,Revision:RevisionId,Digest:Digest)`、`SpecializedPublishedRef(Id:AssetId,Revision:RevisionId,Digest:Digest)` 为不同 sealed record，不可替代二维或 Joint 身份。`SpecializedMethod={HandEye,SheetOfLight,RadiometricResponse,FlatField,DisplayTransfer}`；`SpecializedMetric={ChainTranslation,ChainRotation,SpatialPosition,ResponseRatio,FlatUniformity,DisplayLuminance}`，对应单位枚举 `SpecializedUnit={Meter,Radian,Dimensionless,CandelaPerSquareMeter}`，逐行绑定 meter/radian/meter/dimensionless/dimensionless/cd/m²，不复用二维 ValidationUnit 伪装光度单位。

| 类型 | 完整字段与规则 |
|---|---|
| `SpecializedLimits` | `(MinFitGroups:int,MinCheckGroups:int,MaxGroups:int,MaxElements:int,PoseTolerance:double,Checks:IReadOnlyList<SpecializedCheck>,Source:ContentRef)`；数量正且 minfit+mincheck<=maxgroups，MaxGroups<=100、MaxElements<=100000 是软件默认上限，批准扩大仍受 Budget；pose tolerance正有限；客户指标在 Checks，不能为空 |
| `SpecializedCheck` | `(Id:string,Metric:SpecializedMetric,Unit:SpecializedUnit,MaximumAbsolute:double,MinSamples:int,Reference:ContentRef)`；上界非负有限，样本正；Reference 为独立真值/计量依据，不是拟合残差。按逐样本最大绝对误差与最小样本数判断 |
| `SpecializedFinding` | `(CheckId:string,Status:CheckStatus,Actual:double?,Unit:SpecializedUnit,Samples:int,Evidence:ContentRef?,MessageKey:string)`；未知 Actual=null，不将零样本 RMS 报零 |
| `SpecializedArtifact` | `(Revision:RevisionId,Method:SpecializedMethod,Input:SpecializedInput,Solution:SpecializedSolution,Dependencies:IReadOnlyList<ContentRef>,Producer:JointAdapterVersion,CreatedAtUtc:DateTimeOffset)`；Revision=`1`，输入含原独立 check/Plan，Solution 的方法分支必须一致；候选 digest 根 SpecializedArtifact，按表全字段，不包含候选 envelope/验证/资格 |
| `SpecializedValidated` | `(Candidate:SpecializedCandidateRef,Status:ValidationStatus,Findings:IReadOnlyList<SpecializedFinding>,Evidence:ContentRef?)`；Validated 才 Evidence 非空，证据编码根 SpecializedValidationEvidence、字段 Candidate/Input的check组/Checks/Findings；其余保留诊断，无成功证据 |
| `SpecializedSolved` | `(Candidate:SpecializedCandidateRef,Method:SpecializedMethod,Solution:SpecializedSolution)`；解决量全部为纯值/内容引用 |
| `SpecializedReceipt` | `(OriginalOperationId:OperationId,Status:PublishStatus,Asset:SpecializedPublishedRef?,QualificationIssued:bool)`；Published 才有 Asset，资格字段恒 false |
| `SpecializedReceiptResult` | `(Status:ReceiptQueryStatus,Receipt:SpecializedReceipt?)`；Found精确原操作，NotCommitted 必须权威证明未提交且无在途写；Unknown 不允许新 ID 重写 |
| `SpecializedUse` | `(Asset:SpecializedPublishedRef,Purpose:SpecializedPurpose,ActualConfiguration:ContentRef,ActualDomain:OperatingDomain,ExposureFrom:DateTimeOffset,ExposureTo:DateTimeOffset)`；purpose=`HandEyeTransform/SheetReconstruction/RelativeRadiometry/FlatFieldCorrection/DisplayOnly`，与方法一一对应；ActualConfiguration 是下面该方法 typed configuration 的规范内容，精确可解码、hash/EOF校验，非任意不透明 Options；曝光 UTC 闭区间 |
| `SpecializedQualificationQuery` | `(Use:SpecializedUse,ValidationEvidence:ContentRef,OperationId:OperationId)` |
| `SpecializedQualificationSnapshot` | `(Status:QualificationStatus,Asset:SpecializedPublishedRef,Purpose:SpecializedPurpose,Configuration:ContentRef,ApprovedDomain:OperatingDomain,ValidationEvidence:ContentRef,Id:QualificationId?,Revision:RevisionId?,Watermark:AuthorityWatermark?,ValidFrom:DateTimeOffset?,ValidTo:DateTimeOffset?)`；Qualified 时全部 identity/watermark/有效期必填，不能签发方法之外用途；端口由原 qualification Owner 映射，模块不写决定 |
| `SpecializedResolution` | `(Status:ApplicabilityStatus,Qualified:SpecializedQualificationSnapshot?,Artifact:SpecializedArtifact?,Contents:IReadOnlyList<SpecializedContentBytes>,Findings:IReadOnlyList<ApplicabilityFinding>)`；Applicable才返回两个纯值副本，Contents仅在Applicable有值且为解决量依赖的独立bytes副本，不含源图/证书或native handle |
| `SpecializedStored` | `(Asset:SpecializedPublishedRef,Content:SpecializedArtifact,Validated:SpecializedValidated)`；引用/摘要/证据完整匹配 |
| `SpecializedInvalidationNotice` | `(Asset:SpecializedPublishedRef,Reason:InvalidationReason,Watermark:AuthorityWatermark,MessageKey:string)`；只读通知，不生成设备动作 |
| `SpecializedCall<T>` / `SpecializedReply<T>` | call=`(Revision:string,OperationId:OperationId,Budget:CalibrationExecutionBudget,Payload:T)`，revision=`1`；reply=`(OperationId:OperationId,Completion:OperationCompletion,Value:T?,Error:CalibrationError?,Diagnostic:DiagnosticRef)`；语义同 JointReply，Pending无 Value |
| call payload | 五种封闭类型：`SpecializedSolveInput(SessionId:CalibrationSessionId,Input:SpecializedInput)`、`SpecializedValidateInput(Candidate:SpecializedCandidateRef)`、`SpecializedPublishInput(Candidate:SpecializedCandidateRef,Evidence:ContentRef)`、`SpecializedResolveInput(Use:SpecializedUse)`、`SpecializedQueryInput(OriginalPublishId:OperationId)`；不开放其它 T |
| `SpecializedOperationState` | `(OperationId:OperationId,Status:OperationExecutionStatus,HeldResources:IReadOnlyList<string>,Final:SpecializedOperationSnapshot?,Error:CalibrationError?,Diagnostic:DiagnosticRef)`；Final 是五个sealed分支 `SpecializedSolveSnapshot(Reply:SpecializedReply<SpecializedSolved>)`、`SpecializedValidateSnapshot(Reply:SpecializedReply<SpecializedValidated>)`、`SpecializedPublishSnapshot(Reply:SpecializedReply<SpecializedReceipt>)`、`SpecializedResolveSnapshot(Reply:SpecializedReply<SpecializedResolution>)`、`SpecializedQuerySnapshot(Reply:SpecializedReply<SpecializedReceiptResult>)`，Released 才非空 |
| `SpecializedAdapters` | `(Factory:ISpecializedSolverFactory?,Source:ISpecializedContentSource?,CameraReader:ICameraParametersReader?,Store:ISpecializedStore?,Qualifications:ISpecializedQualificationPort?,ExecutionGate:ICalibrationExecutionGate,Diagnostics:ICalibrationDiagnostics,Clock:TimeProvider)`；借用依赖，缺solver/source CAL-101，缺Store Publish CAL-101、Query CAL-113，Resolve权威缺失Unknown/CAL-106 |

`ICalibrationSpecializedModule : IAsyncDisposable` 提供 `SolveAsync(SpecializedCall<SpecializedSolveInput>,token):ValueTask<SpecializedReply<SpecializedSolved>>`，Validate/Publish/Resolve/QueryPublishReceiptAsync 分别以其专用 call 和 SpecializedValidated/Receipt/Resolution/ReceiptResult 为返回 Value；另有 `GetOperationState(id)`、`ReadEvents(EventReadRequest)`、`WatchInvalidationsAsync(InvalidationWatchRequest,token):IAsyncEnumerable<SpecializedInvalidationNotice>`、`StopAsync(DrainRequest,token)`。唯一工厂 `CalibrationSpecializedModule.Create(options,adapters)` 建立自身有界账本/workspace，单实例全入口 ID 唯一；不得替换原 CalibrationAssetsModule。

每个方法Profile.Domain为明确候选物理/环境域（Sheet原Domain保持），ActualDomain必须在当前资格ApprovedDomain且不超Profile.Domain；边界缺失Unknown，不从设备可运行域推导精度域。HE域Frame为CameraFrame、SH为WorldFrame、RAD/FF为设备原pixel frame，Display为显示pixel frame；各frame稳定身份由对应配置Owner输入，Origin/Orientation不从宽高猜测。LUT灰度/亮度覆盖另由Profile的256目标/有效灰度字段检查，OperatingDomain未定义的物理量不塞DomainQuantity字符串。所有源温度/曝光/工作距离必须实际可确认，缺字段不能报告Applicable。

所有Checks.Id按方法封闭：HE必须 `he.chain.translation`/`he.chain.rotation`（ChainTranslation/Meter和ChainRotation/Radian）；SH必须 `sh.spatial`（SpatialPosition/Meter）；RAD必须 `rad.ratio`（ResponseRatio/Dimensionless）；FF必须 `ff.bright`/`ff.dark`（均FlatUniformity/Dimensionless）；Display必须 `display.luminance`（DisplayLuminance/CandelaPerSquareMeter）。不得缺/重/添加不适用metric，也不得把同一两项FF的最大误差交换。每种方法要求的MinSamples分别取该明确CheckId，原真值Reference和界保留。

端口完整方法：`ISpecializedContentSource.OpenAsync(ContentRef,SolverExecutionContext,CancellationToken):ValueTask<Stream>`；`ISpecializedSolverFactory.Version:JointAdapterVersion` 和 `CreateScope(ISpecializedContentSource):ISpecializedSolverScope`；scope继承 IAsyncDisposable，`SolveAsync(SpecializedInput,ICalibrationContentWorkspace,SolverExecutionContext,CancellationToken):ValueTask<SpecializedArtifact>`、`ValidateAsync(SpecializedCandidateRef,SpecializedArtifact,ICalibrationContentWorkspace,SolverExecutionContext,CancellationToken):ValueTask<SpecializedValidated>`。`ISpecializedStore.WriteAsync(candidate,artifact,validated,sourceWorkspace,execution,token):ValueTask<SpecializedReceipt>`、`ReadAsync(asset,execution,token):ValueTask<SpecializedStored>`、`QueryAsync(originalId,execution,token):ValueTask<SpecializedReceiptResult>`、`OpenAsync(asset,exactDependency,execution,token):ValueTask<Stream>`；写入必须耐久复制全部闭包并原子封口。`ISpecializedQualificationPort.ReadAsync(query,execution,token):ValueTask<SpecializedQualificationSnapshot>`、`WatchAsync(AuthorityWatermark?,execution,token):IAsyncEnumerable<SpecializedInvalidationNotice>`。上述形状为本模块合同，非声称已存在的第三方 API。

`SpecializedContentBytes(Reference:ContentRef,Bytes:ReadOnlyMemory<byte>)` 的byte副本由Resolve在原账本内通过Store.OpenAsync读取并核hash/长度/EOF后产生：HE只NativeFiles、SH只ModelFile、FF只D/G/ValidRegion，RAD和Display无文件（纯值LUT）。这些引用必须属于该asset闭包，全部副本同时峰值计本次驻留和MaxImageBytes，超限CAL-112无Applicable；副本归调用方，关闭模块不使已交副本悬空，使用前消费者在自己的提交门重查资格。

Input 和 Solution 是以下五种封闭分支，按各行完整签名编码，禁止自由字段包。同一 Method/配置下的旧 asset 历史可读，新生产使用必须重新 Resolve；DisplayOnly永远不可成为测量/质量证据。配置内容由 `SpecializedCodec.EncodeConfiguration(input)` 得到，根为相应 configuration 类型；完整configuration wrappers为 `HandEyeConfiguration(Installation:HandEyeInstallation)`、`SheetConfiguration(Installation:SheetInstallation)`、`RadiometricConfiguration(Profile:RadiometricProfile)`、`FlatConfiguration(Profile:FlatProfile)`、`DisplayConfiguration(Device:DisplayDevice,Target:IReadOnlyList<DisplayTarget>,TargetEvidence:ContentRef,Domain:OperatingDomain)`；方法/runtime/测量源身份也由artifact/Profile检查，环境范围另核ActualDomain；原完整字段/依赖纳 hash，不用只比较文件名。

codec公开 `EncodeInput/DecodeInput`、`EncodeArtifact/DecodeArtifact`、`ComputeCandidateDigest`、`EncodeConfiguration/DecodeConfiguration`；固定头/实际分支短名/字段顺序、依赖字节hash与摘要投影按上述规定。请求摘要 root=具体 SpecializedCall payload 的短类型名，字段 Revision/Budget/Payload（省顶层 OperationId）；相同 ID/不同入口或摘要 CAL-107。元数据上限1MiB、字符串256 UTF8bytes、集合受 Limits/Budget、单普通内容<=MaxImageBytes，decode 前检查长度/类型，未知分支 CAL-101、篡改/尾随/非有限 CAL-108。Solve使用的外部ContentRef依赖先在本次账本中Source.Open→有界hash/EOF核验→workspace.WriteAsync按原format/revision封存，返回引用必须精确等源引用；不重新编码并冒称原hash。成功artifact Dependencies闭包包括被使用的Profile/参考/输入/源证据/原图转换与新解文件，Validate新增实测证据同样封存，Store只从workspace复制完整闭包，不要求它暗中访问已释放Source。

所有 raw Stream/写读任务/工厂scope/native句柄在 §6.1 原任务 ledger；每作业独占 native context，观察超时无成功 payload，Dispose 等真实退出/租约归还，不释放借用端口。

**源 raster 不是旧 UInt8 lease 的隐含扩展。** 三维 disparity/flat样本内容格式 `cal-sp-raster-v1`，头ASCII同名，随后 UInt32LE width,height，UInt8 kind（0=Gray8、1=DisparityPixel、2=CorrectionReal），UInt32LE count=checked(width*height)，依次 count 个有限 Float64LE 数值和 count 个0/1 validity字节，EOF精确；mask=0 数值固定0，Gray8有效数为0..255整数，Disparity有效数为非负pixel，CorrectionReal为有限有符号值。长度=头字节数+13+9*count，width/height与本方法配置精确一致、count<=int.MaxValue及本次MaxImageBytes/驻留；全frame mask的domain来自此mask，不能把缺测零当有效。FlatProfile.ValidRegion 使用同format的CorrectionReal分支、全部值0、validity精确表示允许域，不能传任意region路径。仅 Adapter 将此纯值格式通过已批准公共映射生成其私有 HALCON图/region，native real精度转换纳误差/资源验证，不把 double原字节直接解释为 HALCON real指针。每个来源原图/设备disparity仍保留原 hash 与转换证据。公开 `SpecializedRasterCodec.Encode/Decode` 无 IO、有界、防御复制，不改旧图 provider。

#### 7.3A.2 手眼（CAL-HE）

| 封闭类型 | 字段、单位与来源 |
|---|---|
| `HandEyeInstallation` | `(CameraConfiguration:DeviceConfigurationSnapshot?,SensorIdentity:string,SensorConfiguration:ContentRef,Sensor:HandEyeSensor,Topology:HandEyeTopology,Robot:HandEyeRobot,BaseFrame:CoordinateFrame,ToolFrame:CoordinateFrame,CameraFrame:CoordinateFrame,ObjectFrame:CoordinateFrame,RobotPoseConvention:ContentRef,ToolRevision:RevisionId,BaseRevision:RevisionId)`；Sensor=`Camera/SpatialSensor`、Topology=`MovingCamera/StationaryCamera`、Robot=`Articulated/Scara`；Camera分支要求配置非空且有效，SpatialSensor不伪造 CameraModel；frame不同且已转右手，原单位/旋转源定义在 RobotPoseConvention |
| `HandEyeProfile` | `(Revision:RevisionId,Installation:HandEyeInstallation,Optimization:HandEyeOptimization,InitialCamera:CameraParameterVector?,CameraRead:CameraReadRequest?,EstimateCamera:bool,Reference:ReferenceGeometry?,Domain:OperatingDomain,Limits:SpecializedLimits,MaxCaptureSkew:TimeSpan,MinRotationAxisSeparation:Angle,MinRelativeRotation:Angle,ScaraHeightEvidence:ScaraHeightWitness?)`；Optimization=`Linear/Nonlinear/Stochastic`，默认工程选择Nonlinear；物理角/同步界由 Profile 来源明确，禁止相同pose/XY-only凑数量；SCARA冻结内参、HeightEvidence必需才允许完整用途资格 |
| `HandEyeObservation` | `(Id:ObservationId,Group:string,PoseIndex:int,ExposureUtc:DateTimeOffset,FeedbackUtc:DateTimeOffset,FeedbackEpoch:string,ToolInBase:RigidPose,ObjectInCamera:RigidPose,Marks:ObservationRef?,FeedbackEvidence:ContentRef)`；ToolInBase=tool→base，ObjectInCamera=object→camera；同PoseIndex唯一次配对，同步证据/真实反馈，不能命令pose或最近时间补配 |
| `HandEyeInput` | `(Profile:HandEyeProfile,Fit:IReadOnlyList<HandEyeObservation>,Check:IReadOnlyList<HandEyeObservation>)`；物理组/观测 ID/poseIndex无泄漏，Camera分支的全部fit/check观测均要求Marks/Reference/初始camera，Marks目标点号对应同一实测几何；SpatialSensor只Linear/Nonlinear且EstimateCamera=false、Marks/Reference均空；估计camera只Articulated+Camera |
| `HandEyeSolution` | `(Topology:HandEyeTopology,FirstFixed:RigidPose,SecondFixed:RigidPose,SolvedCamera:CameraParameterVector?,FitTranslationRms:Length,FitRotationRms:Angle,FitTranslationMax:Length,FitRotationMax:Angle,OriginalChainEvidence:ContentRef,CorrectedChainEvidence:ContentRef?,NativeFiles:IReadOnlyList<ContentRef>)`；Moving的固定量camera_H_tool/base_H_object，Stationary为camera_H_base/tool_H_object；meter/radian，原HALCON角degree显式转换 |

`ScaraHeightWitness(Topology:HandEyeTopology,ObjectInCamera:RigidPose,ToolAtExposureInBase:RigidPose?,ToolAtObjectOriginInBase:RigidPose,ContactEvidence:ContentRef,ExpandedUncertainty:Length)`；Moving要求两个ToolPose，Stationary曝光ToolPose可空；接触/已知高度操作在模块外已完成、有实际反馈及计量证据，模块不发运动。SCARA只Camera、有独立已合格内参；SpatialSensor+SCARA当前CAL-101，避免套未经证据的camera高度流程。依官方手眼页面的Z消歧，Moving以原固定A计算 U=inverse(A)*ObjectInCamera、V=inverse(ToolAtExposureInBase)*ToolAtObjectOriginInBase，z=U.translation.Z-V.translation.Z；Stationary以原固定C计算 U=inverse(C)*ObjectInCamera，z=U.translation.Z-ToolAtObjectOriginInBase.translation.Z。统一meter，调用set_origin_pose(原FirstFixed,0,0,z)沿该pose自身local Z修正，不沿camera world Z直接加。另一个固定量也必须按同一gauge重表达：选最小PoseIndex的fit工具T0与原两个固定量形成原链预测O0，Moving新Second=T0*inverse(newFirst)*O0，Stationary新Second=inverse(T0)*inverse(newFirst)*O0；保留原量/修正量/height证据，随后全部独立check链和空间真值验证。不能只修First仍输出不一致的旧Second。若非平行SCARA轴/pose定义不能满足官方gauge、单位/接触误差未知，CAL-103/104，不默认Z=0合格。例Moving原A=I、接触关系U.z=1m/V.z=0.9m，则z=0.1m、newA平移(0,0,0.1)m；固定B相应降0.1m，原预测链保持；仅作为gauge软件断言。

嵌套CameraRead（手眼/圆姿态）是请求模板而非可重放的权威缓存：每次实际读取为它生成新child OperationId、按本次execution剩余时间/预算取小，原template ID保留在输入来源但不用于再次调用Reader；child ID/root ID映射入当前ledger。Reader原Task/Stop生命周期仍由其实例持有，特殊作业取消仅取消该次Readtoken、不Stop共享Reader；任何迟到Applicable不交已关闭作业。以后新Solve/Validate/Resolve重新查询，不借同ID幂等回放旧水位。

Camera且EstimateCamera=false时 CameraRead 非空、预算/曝光窗口覆盖本次所有组、ActualDevice等Installation.CameraConfiguration；服务在同一次作业账本调用借用 CameraReader.ReadAsync，以已解快照精确匹配InitialCamera并要求Applicable，未知/撤销拒绝该方法，不以调用方传入旧Qualified引用自证。SCARA必走该冻结读取。EstimateCamera=true时CameraRead为空、给独立初值/实测板和方法证据，输出新相机候选不得声明已有相机资格；SpatialSensor两个字段均空。端口CameraReader缺失只阻冻结相机的手眼片。

路线和链完全沿 §7.2B，补齐可实施拒识：用所有 fit pose 两两相对旋转的 axis/angle，角度低于 Profile.MinRelativeRotation 的对不计激励；Articulated 至少存在两条非平行旋转轴，其夹角（正负轴等价取acos(abs(dot)))>=MinRotationAxisSeparation，否则 CAL-102；SCARA只对应setup且外部高度证据缺失不得完整验证。最少组数遵守官方理论下限和Profile，低于10/25建议须 Limits.Source 中明确方法验证依据，不把建议当资格充分条件。所有RigidPose按PoseTolerance核正交/行列式1、方向/平移unit；链位置逐点长度、旋转用相对rotation的acos(clamp((trace(R)-1)/2,-1,1))，输出radian。Check不能改固定变换或相机参数。Camera Check 的 ObjectInCamera 必须以冻结SolvedCamera/CameraRead已解内参从该组Marks重新估pose（§7.2C的vector_to_pose模型分支），不能拿旧参数下的producer pose验证新内参；SpatialSensor核原独立pose证据。不同frame/原pose来源仍保留。

HandEye Camera输入采用显式已测Marks路线：校验每组原图hash/布局/采样来源与Marks，统一实测Reference XYZ为meter，按稳定点表成组set_calib_data_observ_points（ObjectInCamera只作为初值）；不从本节未定义的find参数重新检测、不逐点覆盖。Camera Check用同一冻结marks点表求独立pose；来源字段/pointIndex/布局不完整CAL-103。

Adapter 按 §7.2B 建私有calib-data；camera branch保持 camera0/object0，原tool pose按PoseIndex set；SpatialSensor以create_calib_data(setup,0,0)建立generic模型，Camera以(setup,1,1)；均用camera/object index0，SpatialSensor 使用 set_calib_data_observ_pose 注入已核 object_in_camera，不能伪造图点。get_calib_data逐项读取 camera0 tool_in_cam_pose/base_in_cam_pose 与 calib_obj0 obj_in_base_pose/obj_in_tool_pose，输出方向与表严格一致。原与 corrected 链证据分开，误差向量四项读后转换单位；未知 corrected不可编造为零。两个固定pose分别 write_pose→read_pose比对方向/矩阵/单位，native文件格式 `halcon-pose-file`/`26.05`；可选完整calib-data write_calib_data→read_calib_data只保存初始参数/对象/观测/设置，官方明确不保存求解结果；因此不从读回model查询并冒充已解固定变换。读回验证输入项一致，求解结果仍由独立pose文件与HandEyeSolution保真；若需要重新求解则新作业/新结果，不把该可变model跨消费者共享。读写roundtrip沿 §9.4 私有路径/账本规则。外来pose文件作为有来源输入，不自动取得手眼资格。

EstimateCamera的新已解向量只属于本Specialized候选/完整手眼链，改变旧camera仍产生新依赖身份；不能把它直接装成旧CameraSolution已发布/合格引用。若需单独光学资产，另走二维显式Solve/Validate/Publish与相应用途资格，手眼资格不替代它。

软件oracle：Moving取camera_H_tool=I、base_H_object平移(0,0,1)m、base_H_tool平移(0.1,0,0)m，则对应camera_H_object平移(-0.1,0,1)m；错误乘法顺序/方向不得通过链。Stationary取camera_H_base平移(0.2,0,0)m、base_H_tool平移(0.1,0,0)m、tool_H_object平移(0,0,1)m，则相机观测(0.3,0,1)m。它们仅检查链/单位，不作为能求解的pose样本；完整harness另用具两轴旋转的输入测试退化拒绝、stochastic+SpatialSensor零native、25重复pose、SCARA无高度、取消迟到、两消费者与升级。真实消费者为独立robot标定工具和离线三维计量工具；机器人协议/真实反馈/高度/物理误差由设备与计量Owner提供，不阻本合同/纯值链工作。

#### 7.3A.3 线激光特殊参考物（CAL-SH）

`SheetInstallation(Camera:DeviceConfigurationSnapshot,InitialCamera:CameraParameterVector,WorldFrame:CoordinateFrame,CameraFrame:CoordinateFrame,LightFrame:CoordinateFrame,MotionEvidence:ContentRef,TimingEvidence:ContentRef)`；model严格area_scan_division、各frame右手，曝光反馈不是运动指令。`SheetProfile(Revision:RevisionId,Installation:SheetInstallation,CalibrationObjectDxf:ContentRef,MeasuredArtifact:ContentRef,Domain:OperatingDomain,Limits:SpecializedLimits)`；Dxf必须为create_sheet_of_light_calib_object对应特殊物、实物尺寸/平面/截锥面证书与该文件一致。不能向算子传任意逐点实测修正后仍声称官方CAD模型；偏离CAD超过计量Profile允许值拒绝方法资格。

`SheetObservation(Id:ObservationId,Group:string,Disparity:ContentRef,DisparityConversion:ContentRef,MovementEvidence:ContentRef,FourFacesEvidence:ContentRef,ReferencePoints:IReadOnlyList<SheetReferencePoint>)`；reference point=`(Id:string,Row:int,Column:int,WorldPoint:Point3,ExpandedUncertainty:Length,Reference:ContentRef)`，真值来自独立参考/计量；不能从重建结果拟合真值。`SheetInput(Profile:SheetProfile,Fit:IReadOnlyList<SheetObservation>,Check:IReadOnlyList<SheetObservation>)`；官方一次标定一个disparity，首版Fit恰1且Limits.MinFitGroups=1，不能合并多个姿态为官方单图；Check至少Limits.MinCheckGroups，每组重采独立，可用独立标准，所有参考点进入检查。`SheetSolution(Camera:CameraParameterVector,CameraPose:RigidPose,LightPose:RigidPose,MovementPose:RigidPose,FitRms:Length,ModelFile:ContentRef)`；单位meter/原向量，CameraPose=camera→world、LightPose=light→world、MovementPose的from/to都为world（允许同frame增量刚体），不能把官方“坐标变换”文字误解为inverse。

固定native序列：检查四面可见/domain无截锥holes/运动平行参考物Y且姿态恒定 → create_sheet_of_light_model(ProfileRegion为Installation.Camera完整原始栅格矩形，预分配num_profiles=输入disparity高度；method=center_of_gravity、ambiguity_solving=brightest、min_gray=100为已输入disparity路线不使用的占位值，不开放为有效调参；不调用measure_profile、不重新提线) → set camera_parameter/calibration_object/calibration=none → set_profile_sheet_of_light(有效domain disparity，空MovementPoses，官方统一default关系由参考模型求解) → calibrate_sheet_of_light → 逐个get_sheet_of_light_param(camera_parameter/camera_pose/lightplane_pose/movement_pose) → set calibration=xyz/scale=m → write_sheet_of_light_model/read_sheet_of_light_model独立model逐项比对 → 封存原file `halcon-sheet-of-light-file`/`26.05`。读取须正确定义完整pose并保留官方原pose convention；不是仅保存误差和裸scale。

独立Check每组使用从冻结file读出的新私有model，reset_sheet_of_light_model后 apply_sheet_of_light_calibration → get_sheet_of_light_result('x'/'y'/'z')，各原始(row,column)仅在输入及输出domain都valid时提坐标，全部真值点计算norm(reconstructed-reference) meter，最大值/MinSamples/完整覆盖按Limits.Checks；缺点失败，不把缺测点删除。原fit RMS只是点到特殊物面的距离，不能代替独立SpatialPosition；算法估计可能物理外参不真实的官方限制随资产记录，禁止用这些参数控制设备。模块不采集、不规划扫描轴误差补偿。真实消费者为激光离线标定工具与三维计量工具，实际disparity/同步/特殊参考物证书/域和误差限由采集/设备/计量Owner提供。

oracle：真值(0.01,0.02,0.03)m，已解投影读值(0.011,0.02,0.03)m，对应SpatialPosition=0.001m；界=0.0009失败，界=0.0011通过（仅计算断言）。普通棋盘Dxf、少一截锥面、domain hole、native roundtrip方向错、Check组泄漏、取消时model迟到均不得返回Validated。真实native/实体重建和参考物测量未运行。

#### 7.3A.4 相对辐射响应与暗场平场（CAL-RAD / CAL-FF）

`PhotometricFrame(Id:ObservationId,Group:string,Image:ContentRef,Device:DeviceConfigurationSnapshot,ExposureMicroseconds:double,SceneEvidence:ContentRef,UniformityEvidence:ContentRef?)`；Image固定cal-sp-raster-v1的Gray8分支/单通道、全图有效（mask有缺项拒绝而不让mean_n补零），原图与转换证据在SceneEvidence中保留，曝光正，其他设备/镜头/增益/照明/布局保持Profile规定，不能更改光圈模拟曝光，自动曝光关闭证据须存在。`RadiometricProfile(Revision:RevisionId,Device:DeviceConfigurationSnapshot,Smoothness:double,PolynomialDegreePlaceholder:int,ValidGrayLow:int,ValidGrayHigh:int,MinHistogramCount:int,Domain:OperatingDomain,Limits:SpecializedLimits)`；Smoothness正、placeholder=5但discrete算法不使用，不开放作有效调参；灰度域0..255、low<high、最少计数正。`RadiometricInput(Profile:RadiometricProfile,Fit:IReadOnlyList<PhotometricFrame>,Check:IReadOnlyList<PhotometricFrame>)`；fit/check分别至少两图、各场景静止/配准证据可信，曝光严格递减且每个相邻比在(0,1)，不能跨不同SceneEvidence做像素对应。`RadiometricSolution(InverseResponse:IReadOnlyList<int>,ValidGrayLow:int,ValidGrayHigh:int,FitEvidence:ContentRef)`；恰256整数0..255、单调不减、官方归一化端点255，不是绝对辐照度/彩色白平衡。

RadiometricConfiguration中的Device是固定几何/采集基线，每个PhotometricFrame.Device只允许ExposureMicroseconds按其同名正值变化；配置修订保留源身份，但实际几何敏感字段/增益/布局/illumination与Profile精确匹配，曝光序列本身纳Input hash。FlatConfiguration不允许曝光变化。

固定调用 radiometric_self_calibration(原UInt8图序列、相邻曝光ratio、2d_histogram、discrete、Profile.Smoothness、5)。调用前用 gray_histo_abs/histo_2dim 核声明灰度域覆盖、每值达到MinHistogramCount，二维直方图在count>=1区域具有连续strip；缺覆盖拒绝，不让Smoothness补孔自证。算子后核LUT完整/单调/有限/端点/域。Validate 在未参与fit的同场景check序列用 lut_trans，逐相邻有效同pixel检查 abs(LUT(I_next)/LUT(I_prev)-exposure_next/exposure_prev)，分母为0或饱和/不在声明域的点不计；但必须满足Checks.MinSamples和全部声明灰度覆盖，缺失失败。输出所有被排除点及其原因，不能剔错到通过。响应LUT只在已验证域用于相对线性化，不能声明绝对能量/色度资格；uint2/RGB是需新增版本的范围，当前CAL-101，不引用未经规范的白平衡系数。

`FlatProfile(Revision:RevisionId,Device:DeviceConfigurationSnapshot,ValidRegion:ContentRef,MinDenominator:double,MaximumGain:double,Domain:OperatingDomain,Limits:SpecializedLimits)`；MinDenominator>0灰度单位、MaximumGain>=1，来自独立代表集与uniformity证据。`FlatInput(Profile:FlatProfile,DarkFit:IReadOnlyList<PhotometricFrame>,BrightFit:IReadOnlyList<PhotometricFrame>,DarkCheck:IReadOnlyList<PhotometricFrame>,BrightCheck:IReadOnlyList<PhotometricFrame>)`；四集合物理组/图不泄漏，fit暗/亮各至少MinFitGroups，check各至少MinCheckGroups；全部曝光/增益/布局相同，暗场遮光/温度证据、亮场独立均匀照明证据必需。`FlatSolution(DarkMean:ContentRef,GainMap:ContentRef,ValidRegion:ContentRef,ReferenceSignal:double,FitEvidence:ContentRef)`；DarkMean/GainMap 为CorrectionReal raster，尺寸/valid region一致，ReferenceSignal>0；参数变化重新求解，不用曝光比例放大旧flat。

采用HALCON CPU固定序列：原图 convert_image_type real → 同一暗/亮集合各用 append_channel + mean_n 求每pixel均值 D/B（append_channel只引用输入矩阵，输入须保持至mean_n退出）→ sub_image(B,D,1,0) 得 S → 以声明ValidRegion核全部pixel S>=MinDenominator，不合格像素记录且从valid mask移除，不能扩域/填零 → intensity(valid,S) 的均值为μ → div_image(常量μ图,S,1,0) 得G。G>MaximumGain或非有限者同样无效；无有效域/覆盖不足 CAL-103，不利用div_image“零除返回0”冒充可用。输出D/G/原域/实际有效mask与诊断。运行校正定义 (I-D)*G，通过 sub_image→mult_image，但本模块只生成校正资产/验证图；生产校正执行仍是preprocessing原Owner，不写设备LUT。顺序需在线性传感域；如果上游先做响应线性化，则fit/check/device必须绑定同一Radiometric asset资格/版本，作为依赖，不能在运行悄悄换顺序。

Validate用独立check暗/亮帧按冻结D/G算checkSignal，亮场有效μcheck>0，metric FlatUniformity=max(abs(pixel/μcheck-1))，暗场用同一检查归一尺度计算max(abs(correctedDark)/μcheck)，两项独立CheckId/MinSamples/界均必需；区域覆盖依Limits.Source声明，少点/域缺失失败。例：D=[10,10],B=[110,210]，S=[100,200]，μ=150，G=[1.5,0.75]；独立亮帧[110,210]校正为[150,150]，uniformity=0；S=0的位置无效，不能输出零作为成功均匀结果。真实消费者为相机调试与离线影像计量工具，真实均匀光源/暗场/传感稳定性由设备/计量Owner提供。代表集拒识/准确率/资源/native及现场未执行。

#### 7.3A.5 显示校正资产（CAL-DIS）

显示校正不得更改原始图或算法输入。批准范围内软件能力是创建、验证和解析仅显示用的灰阶transfer资产；现有显示/几何映射资产也可作为外部版本化内容由其方法Owner导入，但未知格式不解释、不替代内参。物理显示器色度/ICC、系统显卡gamma、投影图样和设备LUT写入没有隐含授权；宿主若另需这些行为须先明确其方法/范围。

`DisplayDevice(Id:string,ConfigurationRevision:RevisionId,ModeDigest:Digest,OutputChannel:string,CalibrationInstrument:ContentRef,Environment:ContentRef)`；OutputChannel首版固定Gray，记录显示器/OS输出配置/亮度状态、测量仪器与环境，模块不调设置。`DisplaySample(Id:string,PhysicalGroup:string,InputCode:int,Luminance:double,MeasuredAtUtc:DateTimeOffset,MeasurementEvidence:ContentRef)`；code0..255，cd/m²非负有限，独立测量证据。`DisplayTarget(Code:int,Luminance:double)`；必须256个依code0..255排列、严格递增目标亮度且有独立来源。`DisplayProfile(Revision:RevisionId,Device:DisplayDevice,Target:IReadOnlyList<DisplayTarget>,TargetEvidence:ContentRef,Domain:OperatingDomain,Limits:SpecializedLimits)`；用户确认的显示目标不是从图像max/min自推。

`DisplayInput(Profile:DisplayProfile,Fit:IReadOnlyList<DisplaySample>,CheckPlan:ContentRef)`；Fit恰每个0..255 code一条测量、严格递增，重复/缺code/非单调CAL-103，不拟合曲线“修好”物理异常；CheckPlan是采样前固定的独立实测计划；实际应用LUT之后的测量在Validate通过Source按计划原引用读取，不要求Solve前伪造未来测量。`DisplayCheckEvidence(Plan:ContentRef,LutDigest:Digest,ConfigurationDigest:Digest,Samples:IReadOnlyList<DisplaySample>,AppliedLutEvidence:ContentRef)`为实际证据：Plan匹配冻结CheckPlan，LutDigest按新头/根DisplayLut/256个整数列表计算，ConfigurationDigest为本DisplayConfiguration的规范字节hash；AppliedLutEvidence记录实际显示配置/应用LUT和仪器测量来源。该证据完整副本纳验证闭包，所有fit/check物理组不得相交、边界/全域覆盖必需。`DisplaySolution(Lut:IReadOnlyList<int>,Device:DisplayDevice,TargetEvidence:ContentRef)`；256个0..255整数非降，无native状态。

求解是纯值映射：对每一target亮度 y，必须在fit实测[L0,L255]内，否则CAL-103、不外推；二分找唯一夹段Li<=y<=Li+1，计算 c=i+(y-Li)/(Li+1-Li)，用 floor(c+0.5)四舍五入并检查0..255（不是依赖当前Culture/默认ToEven），端点直接0/255。该步骤是实测表反查，不另造视觉拟合器。目标/实测严格升序保证可判定唯一性；离线oracle Fit L[i]=i cd/m²、Target[i]=i 时LUT[i]=i，Target255=256时拒绝。Validate从独立Check实际显示输出亮度计算max(abs(measured-target[InputCode])) cd/m²；Check不得拿Fit的插值预测代替仪器测量，缺实际应用证据仍Unknown/验证失败。首版全范围完整检查要求check所有256code，否则不得取得全灰阶域资格；首版Target和Check均要求0..255完整域，不提供范围缩小分支；若未来确需局部域，须新合同版本，不让实现者自行删点。

显示Host通过已资格的DisplayOnly引用对显示副本调用HALCON lut_trans（256 LUT/byte），不在Core写OS/硬件状态；物理显示实测失败仍可显示原图，明确“显示校正未验证”，不能影响生产事实。实例恢复/模式/显示器/OS输出修订变化重新Resolve，过期/撤销停止使用该显示投影并保留原图。真实消费者为独立标定工作台与离线复判显示工具；显示测量Owner提供仪器/曲线/环境/证据与物理亮度误差限。缺这些只阻CAL-DIS物理资格，不能让软件算法/DTO/舍入规则留待实现者选择。

#### 7.3A.6 作业、恢复、交付与定向断言

所有方法从空Host的固定顺序是：构造配置/Profile与fit/check原件 → Create(显式端口) → Solve(新session/operation) → 只对冻结候选Validate → 验证成功Publish未资格内容 → 外部资格Owner签发限定用途 → 另一个无UI Host Resolve(精确配置/时间/域) → 消费纯值与有界依赖 → Stop/真实Dispose。同一输入保持方法和路线，不自动切linear/改Smoothness/补孔/选择最新文件。两个Host各自scope、workspace/IDs/clock，只有显式只读Store/gate可共享；不要求第一Host/UI初始化第二Host。

Publish原子复制依赖及验证，超时保存原操作PublishUnknown，只有Query Found或权威NotCommitted后才允许相应恢复，不建第二Store。Resolve按本次完整配置、原证据、有效期/水位和用途检查；Unknown/撤销/越域不发设备动作。新方法/靶/内参/安装/曝光/同步/目标曲线修订创建新session，旧资产与正式测试保留。输入不可可信、缺独立真值/域时保留候选诊断，不能把软件校验通过升为物理验收。

CAL.SP.01–08 固定软件harness：01五个方法分别检验分支/序列化/未知分支/EOF/hash/有限值与上述各oracle；02错误单位/拓扑/方法组合在native前拒绝；03fit/check同物理组拒绝；04同ID相同完整预算只执行一次、改ID内容冲突CAL-107；05两个Host无UI独立装配且资源互不释放；06各Open/Read/Write/native/Dispose用闩锁注入迟到/取消/超时，Wait到期无Value，真实释放后才有Final，取消Validate无证据；07PublishUnknown只查原ID、QueryFound回读闭包、NotCommitted不能本地猜；08撤销/epoch变化/配置或目的不匹配无Applicable、旧版本不可替代新候选。方法专属拒识/数值例与物理样本分别按本节各卡执行，不能用模拟SP.01宣称真实手眼/线激光/辐射/显示完成。

代码落点只使用既定Core的 `Specialized/`、AsunImageAdapter的 `Specialized/`、PersistenceAdapter的 `Specialized/` 和原对应测试工程，不另建产品/脚本/通用3D包。纯值Codec/Display反查/手眼链/编排属于Core；native solver由 `SpecializedAsunImageSolverFactory` 实现上述factory，Display纯值分支不加载AsunImage。adapter版本/模型白名单按分支明确，native文件读回及domain/mask/精度转换纳Golden。Benchmark负载在§15增加method、pose数/参考点数/disparity尺寸、暗亮帧数/LUT尺寸、驻留native模型数及完整closedown；目标值仍由消费者Profile，缺值NotEvaluated。产品工程本轮未创建；新专用规格为原会话自审的文档内容，不自动列为已接收ModuleCoreImplementationReady。

### 7.4 相机—投影器共同标定首版内部规格（Joint API v1）

#### 7.4.1 范围、Owner 和固定模型

本节是共同标定唯一内部规格，不用 §3 的二维请求承载第二相机。首版固定一台静态面阵相机 index 0、一台逆针孔投影器 index 1，两端均为 `area_scan_division`；只优化各端 `Focus/Kappa/Cx/Cy`，各端 `Sx/Sy` 及宽高固定，像素 pitch/焦距/主点不跨端共享。初始化值和固定 pitch 必须来自各端光学/设备事实或已验证的参数初始化证据，不能默认相机和投影器同尺寸。setup/world frame 固定为相机 0 的右手 frame；`setup_H_camera0=identity`，`setup_H_projector=camera0_H_projector`，`A_H_B` 将 B 点变换到 A。原生长度 meter，交付给 reconstruction-3d 的 `NativeLengthToMm=1000`，只转换一次。

`calibration-assets` 拥有成对观测预检、共同求解、候选、验证/发布内容、只读适用性和 camera_setup 导出。`structured-light` 拥有图案生成及投影执行；`reconstruction-3d` 拥有解码、命名对应层和运行重建。标定适配器只采样解码结果，不复制解码器、不生成/投影图案、不发相机/设备命令；参考件 Owner 提供实测 XYZ/点号/证书，资格 Owner 签发或撤销决定。宿主负责采样计划、实际稳定/同步证据和授权流程。

首版共同采样固定 `gray_code_and_phase_shift / both / global`（以下简记 `HybridBoth`），取得投影器 **row 和 column**；运行时 `HybridVertical` 用 vertical 重建，运行时 `HybridBoth` 的 horizontal 是诊断。单方向结果不足以共同标定。投影像素为实际光学投影栅格，禁用未记录的 OS 缩放、keystone、裁切、翻转或重采样；PhysicalMapping 摘要改变须新资格。telecentric/polynomial/tilt/hypercentric、线扫、多相机/投影器、动态/rolling-shutter 组、镜面 deflectometry、sheet-of-light、手眼和 mosaic/workspace 补偿不在首版，返回 CAL-101，不表示 HALCON 不具备相关能力。反光、黑面、饱和、遮挡、运动导致对应不可用时拒识，不靠质量总分补救。

#### 7.4.2 专用值合同、Profile 与观测包

新增公开类型位于 `Asun.Modules.CalibrationAssets.Joint`；复用 §3 的值类型、Status/错误/预算/资源/事件，不复用二维候选身份。以下 `Type(Field:Type,…)` 是完整 record 等价形状；字段顺序同时是规范编码顺序。集合防御性复制，禁止隐藏句柄/窗口初始化或自由 Options 字典。

| 类型 | 唯一字段与校验 |
|---|---|
| `JointAdapterVersion` | `(Id:string,Revision:RevisionId,RuntimeVersion:string,BuildDigest:Digest)`；Id非空，BuildDigest原公开adapter构建字节hash；solver RuntimeVersion=26.05，decoder另绑其真实实现版本 |
| `JointInvalidationNotice` | `(Asset:JointPublishedRef,QualificationId:QualificationId?,Reason:InvalidationReason,Watermark:AuthorityWatermark,MessageKey:string)`；原因复用v0.2枚举，绝不转换为二维InvalidationNotice.Asset |
| `JointProfileRef` | `(Revision:RevisionId,Digest:Digest)`；引用下述完整 Profile 规范字节 |
| `JointOptics` | `(Camera:DeviceConfigurationSnapshot,Projector:DeviceConfigurationSnapshot,CameraFrame:CoordinateFrame,ProjectorFrame:CoordinateFrame,PhysicalMapping:ContentRef)`；两端CameraModel固定division、ImageWidth/Height>=2、AreaScan/Native/full active raster，裁切为全尺寸、binning=1，非原生坐标先由来源 Owner 生成新规范输入并保留转换证据；两 frame 非空且不同/RightHanded，宽高/pattern尺寸匹配 |
| `JointPattern` | `(Width:int,Height:int,MinStripeWidth:int,MinGrayDifference:int,Manifest:ContentRef,Decoder:JointAdapterVersion,DirectionMapping:ContentRef)`；pattern_type/orientation/normalization 固定上述值，不另设矛盾字段；Width/Height>=2，MinStripeWidth>=4且为2的幂，不超过宽/高分别向上取2幂的最小值，宽高各>MinStripeWidth/2；MinGrayDifference为integer∈[0,255]（本版UInt8相机输入限域，不改官方>=0范围），必须显式给值，无场景默认 |
| `JointVolume` | `(Frame:CoordinateFrame,Min:Point3,Max:Point3,TemperatureMin:Temperature,TemperatureMax:Temperature)`；meter/Celsius，各轴 min<max，Zmin>0，frame=CameraFrame；只声明实测留出覆盖的盒域，不能从设备工作距离推导精度域 |
| `JointRuntimePattern` | `(Width:int,Height:int,MinStripeWidth:int,MinGrayDifference:int,Route:JointRuntimeRoute,Manifest:ContentRef,Decoder:JointAdapterVersion,DirectionMapping:ContentRef)`；JointRuntimeRoute封闭enum=`HybridVertical/HybridBoth`，type固定gray_code_and_phase_shift、normalization=global，orientation依Route为vertical/both；尺寸/stripe/gray界同JointPattern，manifest为该实际路线原件，不能伪用calibration both manifest |
| `JointLimits` | `(MinFitGroups:int,MinCheckGroups:int,MinPointsPerGroup:int,MaxPointsPerGroup:int,MinSpanFraction:double,MinNormalSeparation:Angle,MinDepthSpan:Length,MinBaseline:Length,MinRayAngle:Angle,MaxFitRmse:Pixel,MaxFitPointError:Pixel,MaxCheckRmse:Pixel,MaxCheckPointError:Pixel,MaxRayDistance:Length,MaxDistanceError:Length,MaxPlaneDeviation:Length,MaxExpandedUncertainty:Length,MaxCaptureSkew:TimeSpan,MinStableWindow:TimeSpan,PoseTolerance:double)`；软件下限 fit>=3/check>=2/点>=6，MaxPointsPerGroup∈[MinPointsPerGroup,32767]，每组还受本次MaxPoints/驻留预算约束（非物理资格充分条件），span ∈(0,1]；角度 Radian ∈(0,π/2)，长度 meter、残差界非负、其余物理/时间/姿态容差正且有限；上界/覆盖全部来自版本化 Profile，不设客户精度默认 |
| `JointSamplingProfile` | `(Revision:RevisionId,InnerRadius:Pixel,SplitRadius:Pixel,OuterRadius:Pixel,MaxSupportPixels:int,MinFitPerQuadrant:int,MinCheckPerQuadrant:int,MinHullMargin:Pixel,MinWhiteLevel:int,MaxWhiteLevel:int,MinWhiteBlackDelta:int,MaxLeaveOutError:Pixel,MaxInverseError:Pixel,MaxCentreShift:Pixel,MinAbsDenominator:double,MaxLocalPlanarity:Length,MaxCentreBias:Pixel,Qualification:ContentRef)`；0<inner<split<outer、radii有限，outer<=32是首版软件上限；支持数<=4096且全patch像素在本次预算；fit每象限>=3/check>=2，像素误差界非负，denominator正，planarity meter正，gray是0..255且min<max。Qualification引用独立采样方法证据，不由低局部RMSE合成 |
| `JointLocalMap` | `(OuterMatrix:IReadOnlyList<double>,InnerMatrix:IReadOnlyList<double>,MaxLeaveOutError:Pixel,MaxInverseError:Pixel,CentreShift:Pixel,SamplingQualification:ContentRef)`；两个row-major 3×3、Frobenius norm=1且首个非零为正，normalization tolerance=Profile.Limits.PoseTolerance；坐标row→projector row，col→projector col。Method固定normalized_dlt，不设RANSAC/robust自动剔除分支 |
| `JointSamplingQualification` | `(Revision:RevisionId,TargetGeometryDigest:Digest,Optics:JointOptics,SamplingRevision:RevisionId,InnerRadius:Pixel,SplitRadius:Pixel,OuterRadius:Pixel,LocalPlanarity:Length,CentreBiasBound:Pixel,WitnessEvidence:ContentRef,Domain:JointVolume,ValidFrom:DateTimeOffset,ValidTo:DateTimeOffset)`；公开可读的独立实测白/黑共面与中心预测偏差上界；WitnessEvidence为可核源数据/方法/计量原件，不是拟合统计。Optics/target/sampling/radii必须精确匹配，资格域覆盖全部采样pose/视场/深度/温度，未知时CAL-104 |
| `JointProfile` | `(Reference:JointProfileRef,Pattern:JointPattern,CameraInitial:CameraParameterVector,ProjectorInitial:CameraParameterVector,Limits:JointLimits,Volume:JointVolume,ValidationPlan:ContentRef,ParameterSources:ContentRef,CompatibleRuntimePatterns:IReadOnlyList<JointRuntimePattern>,Sampling:JointSamplingProfile)`；CompatibleRuntimePatterns非空/无重复，至少含与标定JointPattern一致的HybridBoth，HybridVertical需单独manifest和DirectionMapping；两 vector 按 §7.2C division 8 参数固定顺序/单位；Focus/Sx/Sy>0，所有参数有限，Cx/Cy 在本端有效栅格，width/height 精确匹配；Reference.Digest 投影排除自身 Reference 的整个 envelope |
| `JointGroupRef` | `(Id:ObservationId,PoseIndex:int,CaptureGroupId:string,ObservedAtUtc:DateTimeOffset,Packet:ContentRef)`；index>=0，每物理组唯一，不按点拆 fit/check；Packet 格式 `cp-joint-observation-v1` |
| `JointSupportPixel` | `(Row:int,Column:int,ProjectorRow:Pixel,ProjectorColumn:Pixel,InPatternRegion:bool,Unsaturated:bool,QualityAccepted:bool)`；row/col 是对应层的相机栅格，两个浮点为命名层值 |
| `JointPairedPoint` | `(Id:ReferencePointId,CameraRow:Pixel,CameraColumn:Pixel,Support:IReadOnlyList<JointSupportPixel>,ProjectorRow:Pixel,ProjectorColumn:Pixel,Mapping:JointLocalMap)`；Support是下面白区环带内全部有效integer像素，row/column排序，无重复，不是暗区中心取样；Mapping和输出由adapter按固定HALCON路线重算，不能信任producer给值 |
| `JointObservationPacket` | `(Group:JointGroupRef,Optics:JointOptics,Pattern:JointPattern,CameraImage:ContentRef,WhiteImage:ContentRef,BlackImage:ContentRef,WhiteSurfaceMask:ContentRef,ProjectorRows:ContentRef,ProjectorColumns:ContentRef,ValidMask:ContentRef,QualityEvidence:ContentRef,StableEvidence:ContentRef,ClockEpoch:string,CaptureSkew:TimeSpan,StableWindow:TimeSpan,Points:IReadOnlyList<JointPairedPoint>)`；Group.Packet 引用整个包的字节，编码投影省略 Group.Packet 防自引用；CameraImage是相机原始全尺寸单通道UInt8 row-major无padding（格式`image-gray8-rowmajor`），对应层是同尺寸 row-major Float64LE（格式`projector-coordinate-f64le`），mask 是每像素 0/1 byte（格式`valid-mask-u8`），尺寸来自 Camera，字节数 checked 后核限额 |
| `JointInput` | `(Profile:JointProfile,Optics:JointOptics,Target:CalibrationTargetDescriptor,Geometry:ReferenceGeometry,Fit:IReadOnlyList<JointGroupRef>,Check:IReadOnlyList<JointGroupRef>)`；首版只用HalconRectangularDotPlateDescriptor及 §7.2 检测/实测映射，要求每个参与点有 Measured/证书/FlatnessEvidence/不确定度；黑点中心由同平面白区环带局部映射求projector坐标，不能直接在黑心取值；不自动转棋盘/名义板 |
| `JointValidationPlan` | `(Reference:ContentRef,TargetGeometryDigest:Digest,PlaneOrigin:Point3,PlaneNormal:IReadOnlyList<double>,IndependentQualificationEvidence:ContentRef,SamplingQualification:ContentRef)`；plane在Geometry.Frame，origin meter，normal恰3有限数且范数1（PoseTolerance内）；参考plane由参考件实测Owner提供，禁止拟合重建点决定真值；编码投影省略Reference，只依序编码其它字段，格式`cp-joint-check-plan-v1` |
| `JointPhysicalEvidence` | `(Candidate:JointCandidateRef,Profile:JointProfileRef,Plan:ContentRef,CheckGroups:IReadOnlyList<JointGroupRef>,ExpandedUncertainty:Length,CoverageFactor:double,UncertaintyMethod:ContentRef,TemperatureLowEvidence:ContentRef,TemperatureHighEvidence:ContentRef,RepeatabilityEvidence:ContentRef,Authority:string,Revision:RevisionId)`；独立计量Owner提供，meter不确定度与正覆盖因子、源证书/方法修订/原实测重复及温度端点可核验。真实Solve前Plan只引用预登记实验/计量输入包，Validate时ReadPhysicalEvidence以该candidate取正式候选绑定结果；不可把input包的低不确定度默认拷给新candidate |
| `JointCandidateRef` / `JointPublishedRef` | candidate=`(Id:AssetId,Revision:RevisionId,Digest:Digest)`；published=`(Id:AssetId,Revision:RevisionId,Digest:Digest)`；不同 sealed record，不能互换、不能替换二维引用 |
| `JointQualifiedRef` | `(Asset:JointPublishedRef,QualificationId:QualificationId,QualificationRevision:RevisionId,Watermark:AuthorityWatermark,ValidFrom:DateTimeOffset,ValidTo:DateTimeOffset?)`；只来自权威 Qualified，曝光时间按闭区间校验，撤销水位每次重查 |
| `JointPoseReport` | `(Group:JointGroupRef,ObjectInCamera:RigidPose,CameraRmse:Pixel,ProjectorRmse:Pixel,MaxCameraError:Pixel,MaxProjectorError:Pixel,PointCount:int,SpanRow:double,SpanColumn:double,MinRayAngle:Angle,MaxRayDistance:Length)`；pose 方向 object→camera0；每端/span 均记录，两端不能合并掩盖异常 |
| `JointFitReport` | `(GlobalRmse:Pixel,Groups:IReadOnlyList<JointPoseReport>,CameraParameters:CameraParameterVector,ProjectorParameters:CameraParameterVector,CameraCovariance:ContentRef,ProjectorCovariance:ContentRef,SetupHProjector:RigidPose,ParameterSources:ContentRef)`；covariance 来源算子且有参数 labels/shape，不把 covariance 当独立不确定度 |
| `JointArtifactContent` | `(FormatRevision:RevisionId,Input:JointInput,Fit:JointFitReport,SetupFile:ContentRef,Adapter:JointAdapterVersion,CreatedAtUtc:DateTimeOffset)`；版本 `1`，真实SetupFile.Format=`halcon-camera-setup-file`，FormatRevision=`26.05`；只有 §7.4.6A 的RuntimeVersion=`Synthetic/1`模拟scope可用`cp-joint-synthetic-setup-v1`/`1`，该分支只允许Purpose=CalibrationReplay，不交真实HALCON，也不映射生产consumer；file 原字节 hash 和 ByteLength（>0且<=int.MaxValue/本次MaxImageBytes/MaxResidentBytes），由 Write/Read roundtrip验证；不含 candidate envelope/验证结果/资格/自身 digest |
| `JointCheckReport` | `(Candidate:JointCandidateRef,Plan:ContentRef,Groups:IReadOnlyList<JointPoseReport>,MaxDistanceError:Length,MaxPlaneDeviation:Length,ExpandedUncertainty:Length,Volume:JointVolume,Physical:JointPhysicalEvidence,Evidence:ContentRef)`；Plan=Profile.ValidationPlan，Evidence 内容含Physical的独立计量结果/源/hash/计算方法及全部依赖闭包，报告不冒充资格 |
| `JointUse` | `(Asset:JointPublishedRef,ActualOptics:JointOptics,Pattern:JointRuntimePattern,ExposureFrom:DateTimeOffset,ExposureTo:DateTimeOffset,ActualVolume:JointVolume,Purpose:JointPurpose)`；Purpose 仅 `CalibrationReplay/SurfaceReconstruction`；非空曝光闭区间/实际域必须包含请求的全部点，不把重建结束时间当曝光时间 |

原图检测和结构光序列必须是同一 CaptureGroup 的静止窗口、同 ClockEpoch、CaptureSkew<=Profile限额且 StableWindow>=要求；稳定证据来自实际捕获 Owner，不是命令或帧数猜测。`CameraImage`是白场reference（可与WhiteImage同引用），供find_calib_object和实测点关联；WhiteImage/BlackImage为同一窗口的全白/全黑图，pixel format同CameraImage。解码Owner给两层及有效mask；producer bridge给白面mask，白面mask=1仅表示平面白色漫反射区域，排除黑圆/边缘/板外/污染/饱和/混合像素，不是算法猜证书。

`get_structured_light_object('correspondence_image')`未承诺both数组次序；DirectionMapping必须用不对称Golden证明vertical=projector column、horizontal=projector row，不能写死[0]/[1]。原包中每个靶点列出采样算法下的完整支持集合，三个UInt8图/mask和Float64层按公开ContentRef保存；按checked尺寸预留再读取，支持值必须与原层逐像素相等。黑心解码mask=0是正常情况，不判整组必然失败。

**首版目标与观察准备：** 带证书的HALCON标准圆点板，黑圆/白背景同一薄涂层平面，背景是不透光的哑光漫反射白面。禁用背透玻璃、多层厚黑贴纸、镜面釉面、亮膜和投影纹理混入finder曝光。采集Owner在固定曝光/增益下，板不动地取得white/black及完整HybridBoth序列；板材实测局部平面度及黑/白高度差必须满足SamplingQualification，不把标准板证书只给中心点距视为材质证明。相机以原白场图find_calib_object取得稳定靶中心；黑圆周围必须有足够白面支持，主路线通过它求中心projector坐标，**取消0.3.0稿的暗区中心直接采样/剔除补采主路线**。

**固定局部映射（不实施整板全局homography，不写新优化器）：** 对中心(r,c)，按row/col顺序枚举其完整integer外接窗口，保留InnerRadius²<=((row-r)²+(col-c)²)<=OuterRadius²的所有像素，超过MaxSupportPixels则CAL-112而非抽样。窗口越相机边界拒该点；mask/WhiteSurfaceMask均1，WhiteImage处于[MinWhiteLevel,MaxWhiteLevel]，White-Black>=MinWhiteBlackDelta，所有图案曝光的质量/未饱和证据成立；两命名层有限且在projector范围。缺任一证据不接纳该支持，禁止从黑点/跨深度边缘/板外补值。

支持在(row+column) mod 3 == 0时为局部check，否则为fit；按dr/dc的符号分四象限（轴线上归正侧），outer及radius<=SplitRadius的inner集合分别要求四象限fit>=MinFitPerQuadrant、check>=MinCheckPerQuadrant。各fit/check集合不共线，中心须在两fit凸包内且到各边距离>=MinHullMargin；Core有限坐标验证固定采用lexicographic(row,col)排序的monotone chain：对连续三点cross<=0弹中点，构造逆时针凸包；边长度>0，中心到每条有向边的signed cross/边长均>=MinHullMargin。integer支持差的cross在Int64 checked内，subpixel中心距离用有限double；这只是传入值的包含校验，生产拟合仍唯一调用HALCON。gen_region_polygon_filled会round亚像素，不用于这个亚像素包含判据，包围盒也不能代替凸包。不存在允许外推中心的分支；缺环带/一侧支持/整板低信号返回CAL-103，并诊断更换材质/调整已验证曝光或靶/光学采样Profile，不称无限补采能修好。

adapter对outer fit、inner fit各调用`vector_to_proj_hom_mat2d`，Px=相机row、Py=相机col、Qx=projector row、Qy=projector col，Method='normalized_dlt'、六covariance输入为空。结果规范化为Frobenius1；只与`projective_trans_point_2d`组合：纯point坐标系统无需+0.5；不调用projective_trans_pixel/warp image，因此不混图像角点原点约定。各支持/中心w的绝对值>=MinAbsDenominator且在凸包顶点及中心同号（跨w=0极点拒识）；逆矩阵存在且有限。outer/inner各对自己的局部check算二维欧氏预测max<=MaxLeaveOutError，全部支持逆映射误差max<=MaxInverseError，两个中心预测差<=MaxCentreShift。点projector输出固定outer中心预测，Core据matrix/支持重算这些数和阈值；不能按provider的结果直接通过。

两端lens distortion和真实板翘曲使raw小patch映射只是近似：合格局部check和inner/outer中心稳定**不是中心真实偏差证明**。provider.ReadSamplingQualificationAsync按Profile.Sampling.Qualification读取/核摘要；绑定本靶实测几何/材质、两端Optics、sampling/radii、整个采样域/时间，LocalPlanarity<=MaxLocalPlanarity、CentreBiasBound<=MaxCentreBias。WitnessEvidence须来自独立采样方法实验：同材质平板上的可直接解码白面计量点，在不改变光学/同步条件下遮住中心的数值采样（只遮用于fit输入，不改实际原帧）后与原中心真实decoder值/独立光学定位对照，覆盖黑点相等/更大的孔半径、全视场、角度/深度/温度及非零畸变；实测点/尺度资格另按JointPhysicalEvidence。缺该证据真实ValidateFailed，模拟fixture明确Synthetic不冒签证书。unsupported材质/孔大于环带/强畸变超近似/黑白不同平面不提供fallback，仅关闭该native方法，不阻Core完整模拟夹具。

#### 7.4.3 服务、适配端口与结果闭合

所有下述方法的 public DTO 在 Joint namespace，不向 v0.2 接口增方法或结果 union；新实例内 OperationId 仍全入口唯一。`JointCall` 是唯一请求 envelope，JointRevision 固定 `1`；具体 payload 是封闭的五种分支。

| 类型 | 完整形状 |
|---|---|
| `JointCall<T>` | `(JointRevision:string,OperationId:OperationId,Budget:CalibrationExecutionBudget,Payload:T)`；只允许 T 为以下五种；每入口完整预算，不将工厂预算当永久业务截止 |
| `JointSolveInput` | `(SessionId:CalibrationSessionId,Input:JointInput)`；Solve 内先准备/预检/封存输入；不新增另一 Prepare 存储状态 |
| `JointValidateInput` | `(Candidate:JointCandidateRef)`；只能读该候选冻结的 Check/Plan，改 Check/Plan 必须新候选，不能把 fit 组回灌 |
| `JointPublishInput` | `(Candidate:JointCandidateRef,CheckEvidence:ContentRef)`；证据必须是成功 Validate 形成且绑定 candidate digest/Plan 的内容 |
| `JointResolveInput` | `(Use:JointUse)`；只读当前资格并输出有界文件字节，不激活/绑定 |
| `JointReceiptInput` | `(OriginalPublishId:OperationId)`；新的查询 ID，保持原写入身份 |
| `JointReply<T>` | `(OperationId:OperationId,Completion:OperationCompletion,Value:T?,Error:CalibrationError?,Diagnostic:DiagnosticRef)`；只有真实执行/所有 IO资源释放后可 Value 非空；否则 null 并带 CAL-110/111/109 等错误，DrainPending 无成功 payload；只读不适用/未知 Value 可非空（业务三态） |
| `JointSolved` | `(Candidate:JointCandidateRef,Fit:JointFitReport)` |
| `JointValidated` | `(Status:ValidationStatus,Report:JointCheckReport?,Findings:IReadOnlyList<ValidationFinding>)`；Validated 才可 Report 非空，失败保留 findings，不改候选 |
| `JointPublishReceipt` | `(OriginalPublishId:OperationId,Status:PublishStatus,Published:JointPublishedRef?,QualificationIssued:bool)`；Published 才有引用，QualificationIssued 恒 false；未知保持原写入记录 |
| `JointResolution` | `(Status:ApplicabilityStatus,Qualified:JointQualifiedRef?,Export:JointSetupExport?,Findings:IReadOnlyList<ApplicabilityFinding>)`；Applicable 才有两者，其余均 null |
| `JointSetupExport` | `(Asset:JointPublishedRef,File:ContentRef,Bytes:ReadOnlyMemory<byte>,CameraFrame:CoordinateFrame,WorldFrame:CoordinateFrame,NativeLengthToMm:double,CameraIndex:int,ProjectorIndex:int)`；Bytes 是独立托管防御副本，其 hash/长度=File；两个frame同CameraFrame，比例1000、index0/1；不传序列化句柄/全局路径 |
| `JointReceiptQuery` | `(Status:ReceiptQueryStatus,Receipt:JointPublishReceipt?)`；沿 §3/§9 Found/NotCommitted/Unknown，Found 有OriginalPublishId精确等原id的回执，Store 不可达 Unknown；NotCommitted 仅权威确定无提交/无在途写入 |
| `JointOperationState` | `(OperationId:OperationId,Status:OperationExecutionStatus,HeldResources:IReadOnlyList<string>,Final:JointOperationSnapshot?,Error:CalibrationError?,Diagnostic:DiagnosticRef)`；Final 仅 Released 非空 |
| `JointOperationSnapshot` | 五种 sealed 分支 `JointSolveSnapshot(Reply:JointReply<JointSolved>)/JointValidateSnapshot(Reply:JointReply<JointValidated>)/JointPublishSnapshot(Reply:JointReply<JointPublishReceipt>)/JointResolveSnapshot(Reply:JointReply<JointResolution>)/JointReceiptSnapshot(Reply:JointReply<JointReceiptQuery>)`；Stop/watch Final=null |
| `JointSolverResult` | `(Content:JointArtifactContent)`；adapter不制造候选引用、不持 Store；returned时内部任务/lease实际结束 |
| `JointQualificationQuery` | `(Use:JointUse,ContentDigest:Digest,CheckEvidence:ContentRef,OperationId:OperationId)`；带当前完整scope和操作身份 |
| `JointQualificationSnapshot` | `(Status:QualificationStatus,Asset:JointPublishedRef,Scope:JointUse,CheckEvidence:ContentRef,Id:QualificationId?,Revision:RevisionId?,Watermark:AuthorityWatermark?,ValidFrom:DateTimeOffset?,ValidTo:DateTimeOffset?,RuntimeValidationEvidence:ContentRef?)`；Status复用 §3 的资格 enum；Qualified 必填 identity/watermark/time/与本Use.Pattern精确绑定的RuntimeValidationEvidence；资格Scope曝光窗口是资格覆盖期，不只当前请求；只能匹配本次Purpose/RuntimePattern，Owner批准别的Purpose不自动共用 |

```csharp
public interface IJointCalibrationModule : IAsyncDisposable
{
    ValueTask<JointReply<JointSolved>> SolveAsync(JointCall<JointSolveInput> request, CancellationToken token);
    ValueTask<JointReply<JointValidated>> ValidateAsync(JointCall<JointValidateInput> request, CancellationToken token);
    ValueTask<JointReply<JointPublishReceipt>> PublishAsync(JointCall<JointPublishInput> request, CancellationToken token);
    ValueTask<JointReply<JointResolution>> ResolveAsync(JointCall<JointResolveInput> request, CancellationToken token);
    ValueTask<JointReply<JointReceiptQuery>> QueryPublishReceiptAsync(JointCall<JointReceiptInput> request, CancellationToken token);
    JointOperationState GetOperationState(OperationId operationId);
    EventReadResult ReadEvents(EventReadRequest request);
    IAsyncEnumerable<JointInvalidationNotice> WatchInvalidationsAsync(InvalidationWatchRequest request, CancellationToken token);
    ValueTask<DrainResult> StopAsync(DrainRequest request, CancellationToken token);
}
public interface IJointObservationProvider
{
    ValueTask<Stream> OpenContentAsync(ContentRef reference, SolverExecutionContext execution, CancellationToken token);
    ValueTask<JointObservationPacket> ReadAsync(JointGroupRef group, SolverExecutionContext execution, CancellationToken token);
    ValueTask<JointSamplingQualification> ReadSamplingQualificationAsync(ContentRef reference, SolverExecutionContext execution, CancellationToken token);
    ValueTask<JointValidationPlan> ReadPlanAsync(ContentRef plan, SolverExecutionContext execution, CancellationToken token);
    ValueTask<JointPhysicalEvidence> ReadPhysicalEvidenceAsync(JointCandidateRef candidate, JointValidationPlan plan,
        SolverExecutionContext execution, CancellationToken token);
}
public interface IJointSolverScope : IAsyncDisposable
{
    ValueTask<JointSolverResult> SolveAsync(JointInput input, ICalibrationContentWorkspace workspace,
        SolverExecutionContext execution, CancellationToken token);
    ValueTask<JointCheckReport> ValidateAsync(JointCandidateRef candidate, JointArtifactContent content,
        ICalibrationContentWorkspace workspace, SolverExecutionContext execution, CancellationToken token);
}
public interface IJointSolverScopeFactory
{
    JointAdapterVersion Version { get; }
    IJointSolverScope CreateScope(IJointObservationProvider provider);
}
public interface IJointArtifactStore
{
    ValueTask<JointPublishReceipt> WriteAsync(JointCandidateRef candidate, JointArtifactContent content,
        ContentRef checkEvidence, ICalibrationContentWorkspace source,
        SolverExecutionContext execution, CancellationToken token);
    ValueTask<JointStoredArtifact> ReadAsync(JointPublishedRef asset, SolverExecutionContext execution, CancellationToken token);
    ValueTask<JointReceiptQuery> QueryAsync(OperationId originalPublishId, SolverExecutionContext execution, CancellationToken token);
    ValueTask<Stream> OpenContentAsync(ContentRef content, SolverExecutionContext execution, CancellationToken token);
}
public interface IJointQualificationPort
{
    ValueTask<JointQualificationSnapshot> ReadAsync(JointQualificationQuery request,
        SolverExecutionContext execution, CancellationToken token);
    IAsyncEnumerable<JointInvalidationNotice> WatchAsync(AuthorityWatermark? after,
        SolverExecutionContext execution, CancellationToken token);
}
```

`JointStoredArtifact(Asset:JointPublishedRef,Content:JointArtifactContent,CheckEvidence:ContentRef,Report:JointCheckReport)`；ReadAsync 核所有内容闭包，OpenContent 返回的 Stream 由 Core唯一 Dispose。WriteAsync 在 Published 前复制全部依赖/验证字节并原子封口，不只存引用；按执行 OperationId 和请求摘要幂等保存原事实。Query Found(Published) 后 Core 必须 Read/OpenSetup/核闭包，损坏 CAL-108，不改 Store 事实。资格不接缓存；晚到资格值丢弃，下一次 Resolve 新查询；通知 epoch/gap/失联使宿主投影 Unknown。

唯一构造为 `JointCalibrationModule.Create(CalibrationAssetsOptions options, JointAdapters adapters)`；options复用 §9.1 的有限容量，借用依赖不被模块 Dispose。`JointAdapters(Factory:IJointSolverScopeFactory?,Observations:IJointObservationProvider?,Store:IJointArtifactStore?,Qualifications:IJointQualificationPort?,ExecutionGate:ICalibrationExecutionGate,Diagnostics:ICalibrationDiagnostics,Clock:TimeProvider)`；无UI Core静态工厂/显式参数，不使用服务定位。Create只校验/复制值、建立本地workspace并创建软件scope；factory.CreateScope同步、本地、失败自身清理，不启动 native/设备/IO。Factory/provider缺失时Solve/Validate CAL-101，Store缺失Publish CAL-101、Resolve/Query CAL-113，Qualification缺失Resolve Unknown/CAL-106；只读消费者允许factory/provider为空。scope每模块独占、native模型每作业独占；shared gate 不允许绕过峰值预约。

真实适配构造固定 `new JointAsunImageSolverFactory(JointAdapterVersion version, TimeProvider clock)`，`CreateScope(provider)` 借用provider，方法中的 workspace/execution 为操作跟踪代理；source解析/IO不在构造执行。全部HALCON经 ImageLibDotNet.cv2，factory Version.RuntimeVersion固定目标26.05，具体C# pose/tuple/covariance/文件IO形状仅实际歧义时按公开签名/消费编译确认，不能扫描封装内部。

#### 7.4.4 处理顺序、可观测性与独立检查

JointOperationState/Reply/事件仅是新实例ledger投影；事件ContractRevision="1"，阶段及事件名沿 §4.3，Prepare发生在Solve内部。原业务每session一个变更操作；Resolve/Query只读仍计有限队列/资源槽；同OperationId/RequestDigest重放不重开adapter，改入口或budget返回CAL-107。超时先撤销结果发布权；原task/内容仍held，晚到Solve结果不得生成候选，晚到Validate不生成成功证据，晚到Publish只归Store原id事实、原最终结果保持PublishUnknown；只有新Query返回它。

1. Core先检查 JointRevision、数值、每入口预算、可用端口、两端模型/layout、Profile摘要/初值/来源、几何实测证书和采集/分区引用。Fit/Check的 Id/CaptureGroupId/Packet摘要任一交叠、重复PoseIndex或重复帧都拒绝；每组point Id唯一/有效绑定实测点，不超过Profile.Limits.MaxPointsPerGroup且最多32767（vector_to_pose硬界）且不超过MaxPoints。未知/完整性错误CAL-100/108、非支持模型CAL-101、观测质量CAL-103、数量/覆盖CAL-102。预算算入两层float64/mask、原图、支撑/点表、setup/workspace/报告；按checked尺寸和ByteLength预约后再开内容，分批读取，不能先分配全组。原件闭包通过跟踪provider.OpenContentAsync核hash、copy到模块workspace，所有late stream随ledger负责Dispose；不依赖共享字典/目录。
2. provider在读/采样时按原层字节核hash、white/black/mask及环带值，返回包的摘要由Core重算核group.Packet；源证据不可达不是有效。每个组预检 span=(max-min)/(该端宽高-1)，camera/projector row和col四项均>=MinSpanFraction；按白区局部映射规范拒识点，少于MinPointsPerGroup拒组；不丢组后继续宣布满足原计划。planar点坐标必须至少4个非共线；以vector_to_pose('analytic')从各端同名XYZ/row/col得到各端 object pose 初值，点非平面亦走analytic，不丢实测Z。正深度和矩阵正交/行列式+1按PoseTolerance，姿态初值不是独立真值。
3. 计算各组cam0靶normal=`R*(0,0,1)`、中心深度；至少有一对normal夹角（acos clamp dot）>=MinNormalSeparation，max(centerZ)-min(centerZ)>=MinDepthSpan。由同组两个初pose求 camera0_H_projector，每组初基线长度>=MinBaseline、方向按已声明pose链，未知方向/非刚体拒绝；组间物理一致性以优化后固定基线及独立check判定，不由实现自设初值差门限。用户Profile三维域和角/深度门来自采样设计，无数值时不能启动真实求解，但无硬件Core模拟可以用明确软件断言Profile。
4. 每次私有 `create_calib_data('calibration_object',2,1)`，`set_calib_data(...'model','general','reference_camera',0)`。`set_calib_data_cam_param`两端不同初值，`set_calib_data_calib_object`使用实测XYZ meter；`set_calib_data`各端先exclude所有内参，再 `calib_settings`只加入 focus/kappa/cx/cy；camera0外部pose保持reference固定，projector外部pose参与优化，不把reference排除套给projector。同一CalibObjIdx=0/PoseIdx，一次成组 `set_calib_data_observ_points`注入每端Row/Column/Index/对应object-in-that-camera初pose；不逐点覆盖、不用只在检测侧修正过的名义板求解。
5. `calibrate_cameras`返回pixel全局RMSE，没有 MaxIterations 或相机 optimization_method。读取 `camera/0,1/params,pose,params_covariances,params_labels` 和 `calib_obj_pose/[0,pose]/pose`；保存完整参数/协方差及实际优化项。两端参数合法/有限，Sy/Sx/尺寸固定未变；各实测XYZ用优化靶pose和逆projector pose分别project_3d_point得到camera/projector预测坐标，逐点二维欧氏误差，RMSE=sqrt(sum(err²)/N)，各组/各端max和global分别核Profile。失败CAL-104，不优化重试/增加自由度/回流check。
6. `get_calib_data('model','general','camera_setup_model')`取优化setup，固定reference_camera=0；核 `num_cameras=2/reference_camera=0`、index0/1类型/参数/pose，cam0 identity/projector pose= camera0_H_projector。pose转矩阵方向通过已知非零基线/不对称点正逆Golden验证，不能用身份阵冒充缺姿态。`write_camera_setup_model`到operation-private临时文件→按实际字节write workspace并hash→`read_camera_setup_model`同字节回读核两端参数/pose/reference。所有句柄/file/stream纳ledger，真实native退出后清理；无全局固定目录或按asset ID执行输入路径。首版文件路线可靠，不把serialize_camera_setup_model的serialized-item handle当 byte[]。
7. Core封存 `JointArtifactContent`生成JointCandidateRef。独立Validate不改变内参/基线，Check组不进入fit；用同一观测/采样规则，vector_to_pose只用**camera端**点估check object-in-camera，再用固定setup预测projector点；优化后再按步骤3核fit normal/depth激励和baseline，避免两端共同优化后把误差隐藏。check按两端RMSE/max阈值检查；`get_line_of_sight`两端ray，按setup变换到camera0，要求forward depth>0、夹角>=MinRayAngle。`intersect_lines_of_sight`RelPose=**camera0_H_projector**，输出camera0点和点到ray最短Dist，核MaxRayDistance；输出为最近点midpoint，不称真实ray交点。
8. 逐check group将重建点转回object frame，在Profile.MaxPointsPerGroup/操作Deadline内对实测稳定点号的全部i<j距离计算（分块遍历，不分配N²数组；步间检查cancel/deadline，预算不够则取消/超时而非抽样改变验收） max |d_reconstructed-d_measured| <=MaxDistanceError；点到实测靶基准平面的最大偏差<=MaxPlaneDeviation（基准plane来自ValidationPlan，不把已拟合重建面当真值）。通过provider.ReadPlanAsync读取并核Plan的规范字节/TargetGeometryDigest/plane；点到plane偏差=abs(dot(normal,reconstructedObjectPoint-PlaneOrigin))。provider.ReadPhysicalEvidenceAsync按本次candidate获取独立计量Owner的候选绑定证据，核candidate/profile/plan/check groups、certificate/UncertaintyMethod/覆盖因子/重复性及温度端点引用完整，ExpandedUncertainty<=MaxExpandedUncertainty；本模块不发明误差传播或用pixel residual估计计量U，缺真实独立证据为ValidationFailed。Check点全部在SamplingQualification.Domain内，其每轴样本min/max必须包围待验证Volume.Min/Max；允许验证点在Volume外的已批准采样域里，不要求每一点同时落在较小运行Volume内，温度覆盖由Plan实测端点证据给出；不能由一个pose或fit空间外推验证体积。只有全部检查通过才形成与候选hash绑定的报告和Evidence，adapter将CheckReport的规范投影写workspace，Core回读重算摘要并独立复核Plan/阈值/绑定后才返回Validated；证据字段缺失不能记零或N/A冒称合格。
9. Publish只接该实例已完成成功验证的Candidate/Evidence；Core核canonical artifact/check绑定，Store复制原件闭包并原子发布PublishedUnqualified。Resolve先回读同精确asset/hash/check，再查Qualification，逐项匹配两端设备/安装/光学/readout/ROI/binning、PhysicalMapping、pattern尺寸/stripe/global/decoder修订、target/method/Profile、frame/用处/verifiedVolume/温度和曝光时间；实际JointRuntimePattern须与Input.Profile.CompatibleRuntimePatterns中的一项精确匹配（不是强行等标定both manifest），资格当前Scope.Pattern和RuntimeValidationEvidence必须覆盖同一runtime route/manifest/decoder（该真实重建回放证据由reconstruction-3d/资格Owner提供，桥Core不实现它）；缺runtime独立验证Unknown，无批准兼容项NotApplicable。设备Device/Optical/ConfigurationRevision、Model、Lens/Focus/Magnification/Mounting、Readout、ROI/Binning、Illumination逐字段精确匹配，曝光/增益本版固定匹配，当前Temperature/WorkingDistance须声明并满足资格/Volume，缺必需字段Unknown。资格撤销/Suspended/Expired/越域NotApplicable，权威缺失/水位未知、ObservedAt/ValidUntil过期或epoch无法核验Unknown。Applicable才打开setup stream、有界复制/核原字节hash并关闭，再交付独立托管Bytes；复制时保留原任务/缓冲，不先Dispose stream；峰值预约须同时覆盖store读缓冲、Export副本、workspace/native在途字节，先获Host根的输出字节额度再交付，不能先归还gate后在无额度下另拷一份。当前权限/激活/生产提交仍由宿主在自己事务重核水位。

#### 7.4.5 摘要、内容闭包和兼容

`cp-joint-binary-v1` 使用 §3.7 的primitive/record/list/set/nullable规则，但头是ASCII原始 `cp-joint-binary-v1`，不写v0.2头。枚举以声明名称string编码（不写数值）；不能重算二维资产身份。JointGroup包根 `JointObservationPacket` 只省略 Group.Packet 字段（Group其它字段全部保留）。Profile根 `JointProfileContent` 按Profile字段顺序但省略整个Reference，参数/Plan/来源digest都保留。JointPrepared根 `JointInput` 编码全部Input，摘要不含SessionId/预算/OperationId。Candidate根 `JointArtifactContent` 编码全部内容，外部candidate envelope全部不入hash；artifact嵌套Input含已核Profile.Reference与观测/来源digest，SetupFile.Digest按真实file bytes。Validation独立根 `JointCheckReportContent` 按CheckReport签名省略Evidence字段；Evidence原字节封口，CandidateDigest与Plan/独立源绑定，不反写artifact。请求根为具体payload短名加 `JointRevision:string,Budget:CalibrationExecutionBudget,Payload:T`（顺序固定），只排顶层OperationId；改变预算会冲突，Resolve包含精确曝光区间/域，Query保留OriginalPublishId。跨实例Store幂等须原id/摘要，不把session/run GUID换成新写入操作。

固定小请求编码向量：root=`JointReceiptInput` 的request投影，JointRevision=`1`，Budget=`(10ms,20ms,1,2,3,4,1)`（Deadline/WaitLimit/MaxImages/MaxImageBytes/MaxPoints/MaxResidentBytes/MaxConcurrentSolves，对应既有字段类型），Payload.OriginalPublishId=`00000000-0000-0000-0000-000000000001`；这是codec断言，容量不足以真实业务，不作为软件预算默认。规范hex/hash见下表，须独立复算；改顶层OperationId不变，改任一Budget字段改变，改OriginalPublishId改变。

| 向量 | 规范十六进制 / SHA-256 |
|---|---|
| JointReceipt request | `63702d6a6f696e742d62696e6172792d7631110000004a6f696e7452656365697074496e70757401000000311a00000043616c6962726174696f6e457865637574696f6e427564676574a086010000000000400d03000000000001000000020000000000000003000000040000000000000001000000110000004a6f696e7452656365697074496e7075740b0000004f7065726174696f6e49642400000030303030303030302d303030302d303030302d303030302d303030303030303030303031` / `54f9854dc9a19d1c02a68bf4d0c1cea8b5dcd371097b1da547377109df144ca8` |

#### 7.4.6 两个完整 Host、根所有权和消费者映射

Host A `Consumers/JointStructuredLightHost.cs` 独立装配 provider/solver/workspace/gate/mock Store/只读资格源，以producer规范化组构造JointInput→Solve→Validate→Publish；不直接操作投影器，也不在标定模块写decoder。成功发布仍未Qualified。Host B `Consumers/JointReconstructionHost.cs` 独立装配只有Store/Qualification/gate的module，读取明确PublishedRef→Resolve→读取Export bytes→由自己的reconstruction adapter `read_camera_setup_model`→绑定结构光model→decode/reconstruct→释放其私有模型/文件。两个Host不引用彼此类/UI/配置，不共享candidate scope；可显式共享Store/gate，真实producer/decoder桥后续接收。

Host调用必须从factory前开始有Owner：测试/宿主根注册器一次预留 `MaxRoots=2、MaxTasksPerRoot=64、MaxBuffersPerRoot=8` 及依赖/输出字节预算（这是软件测试上限，可显式Profile收紧），否则factory/外部调用次数为0。根强持原构造Task、options/adapters/请求、所有原业务Task、cleanupTask和返回module/bytes；每个异步调用在启动时登记原Task及OperationId，在交付调用方前先强写返回值到同根。构造/IO慢/业务等待超时都只结束观察，不丢原Task；晚到module归根关闭、晚到Bytes归根保管/释放，根Closing后不产生新业务/重建/发布。

finally先Closing，原业务异常保持原栈，cleanup错误独立保存。取到module才登记**一次**StopAsync(DrainRequest new cleanup-id,WaitLimit<=30s)，cleanup用独立有限30s token/预算，后续只观察该原Task和各原OperationId；确认全部ResourcesReleased后登记**一次**DisposeAsync原Task，有限观察，Dispose未完成不退根/不释放借用端口。未交付构造结果时不伪造Stop对象，保留factory原Task并由唯一根Owner对晚到module首次Stop。根pending时移交是全量offer同OwnerTransferId，接收者先有界预留并强持全部Task/依赖/module/bytes/错误/额度，再确认唯一Owner切换；拒绝/异常/超时/迟到未确认都保持原根，移交不等于释放。无接收者则根留在宿主进程恢复面板，禁止退栈丢scope；不得无限CancellationToken.None清理。借用Store/Qualification/provider由根在所有模块/任务确认退出后按自身生命周期释放。

JointSetupExport是值输出而非native租约：Core在返回前关闭store stream、释放读预约，caller根在交付前已持Bytes；原 module释放不销毁caller副本。Bytes长度/hash/模型/两个index/frame必须被B再次核验，B的临时文件属于B原重建操作，直到native退出/排空才删除；A停止不能影响B。使用公开桥映射如下，消费者指导需原Owner另行接收，本次不改消费者/共享文件：

两个Host的实际调用序列固定如下；`Capture/Observe/Close` 是测试工程本地根注册器（非新增公共API），按上面的容量/原Task/交付前强持/有限观察和唯一移交规则实现：

```text
A: root=ReserveRoot(options,adapters,input);
   module=Observe(root.CaptureFactory(() => JointCalibrationModule.Create(options,adapters)));
   solved=Observe(root.Capture(() => module.SolveAsync(new JointCall<JointSolveInput>("1",solveId,budget,
      new JointSolveInput(sessionId,input)),businessToken).AsTask()));
   若Completion!=ResourcesReleased或Value==null：停止业务并进finally，禁止Validate/Publish。
   checked=Observe(root.Capture(() => module.ValidateAsync(new JointCall<JointValidateInput>("1",checkId,budget,
      new JointValidateInput(solved.Value.Candidate)),businessToken).AsTask()));
   仅checked.Value.Status==Validated且Report非空：
   receipt=Observe(root.Capture(() => module.PublishAsync(new JointCall<JointPublishInput>("1",publishId,budget,
      new JointPublishInput(solved.Value.Candidate,checked.Value.Report.Evidence)),businessToken).AsTask()));
   PublishUnknown：保存原publishId，新queryId有限QueryPublishReceipt；不重新Publish。
B: 独立ReserveRoot/Create（Factory/Observations=null），use.Asset=明确同一JointPublishedRef；
   resolved=Observe(root.Capture(() => module.ResolveAsync(new JointCall<JointResolveInput>("1",resolveId,budget,
      new JointResolveInput(use)),businessToken).AsTask()));
   仅Released且Applicable：根先持Export及Bytes，核hash/frame/index，在B自己的有限任务内重建；
   原生B不能按Mock直接成功，其读file/decode/reconstruct与租约归还另属CAL-JI。
finally(A/B各自): Closing；Capture一次Stop；有限Observe；逐原GetOperationState核held；
   全部Released才Capture一次Dispose；仍pending保留根/全量offer并等接收确认；
   主业务异常与各cleanup错误分别保存，不用cleanup重试或新模块消除未知。
```

CaptureFactory在调用前预留并登记原构造执行Task，构造同步Create只能在此已登记委托内执行；委托返回前把module强写根。Capture先预留entry并强持委托/原请求/依赖再调用委托，同入口锁内保存返回的原Task；调用在返回Task前抛错也保留entry和原异常。业务ValueTask恰一次AsTask，登记该原Task，捕获/交付完成路径也计额度，不能仅登记一个Canceled wrapper。A候选/check/receipt每步同样先保存再观察；B只有Applicable输出才启动其自己的重建执行，原Resolve任务timeout晚到不会触发B重建。Findings/错误Status不能按payload非空直接放行。

| 消费者现字段 | 本模块映射与拒绝 |
|---|---|
| structured-light `AssetRef` / projector width/height / camera_setup | 只能由 `JointConsumerBindingProjection` 生成 `AssetRef(Id=SourceAsset.Id,Version=BridgePackageVersion, Sha256=SourceAsset.Digest)`；`Version`固定为桥包SemVer，不承载任意Joint `RevisionId`。完整 `SourceAsset`、源revision、`JointQualificationSnapshot`、快照指纹、projector尺寸、PhysicalMapping/Manifest/decoder仍随同一绑定保存并逐项核验；缺少伴随值时拒绝普通AssetRef路径，改走Joint专用绑定 |
| reconstruction-3d `CalibrationRef.Asset` / `CalibrationScope.Asset` | `CalibrationScope.Asset=RevisionRef(SourceAsset.Id,SourceAsset.Digest)`；`CalibrationKind`固定`CameraProjectorJointV1`，每direction精确引用同一Joint资产。源 `JointPublishedRef`（含任意RevisionId）完整伴随保存，不伪装进只有`Id,Sha256`的RevisionRef |
| reconstruction-3d `CalibrationScope.Qualification` | `RevisionRef(SourceQualification.Id,QualificationSnapshotContent.Digest)` 是有界技术绑定指纹；源 `QualificationRevision`、AuthorityWatermark、有效期、Scope、CheckEvidence、RuntimeValidationEvidence和完整快照继续伴随保存。它不是资格原件签名；缺完整快照或指纹即拒绝组装，不调用native |
| `CalibrationRef.CameraFrame/WorldFrame/ValidFrom/ValidTo` | CameraFrame=WorldFrame=Export.CameraFrame（setup参考camera0）；有效期为权威资格区间，按曝光时间判断；工作台/板/mosaic frame需宿主另做显式变换，不能把world字段改成每pose的板frame |
| `ICalibrationAssets` / Optical source / `NativeLengthToMm` | 校验JointSetupExport.File hash/bytes；bridge在自身原操作租约下生成私有临时file并交 `read_camera_setup_model`；机密路径/handle不出adapter、排空后删除。meter→mm=1000一次，非production物理测量不能借Diagnostic/未资格绕过 |

#### 7.4.6B 两消费者资格绑定技术桥（JointQualificationBinding v1）

7.4.6 的旧直接映射不能成立：`JointPublishedRef` 是 `(Id,Revision,Digest)`，`reconstruction-3d.RevisionRef` 只有 `(Id,Sha256)`；`structured-light.AssetRef` 是 `(Id,Version,Sha256)` 且 `Version` 必须是 SemVer，而 `Joint` 的 `RevisionId` 允许任意已校验字符串。`JointQualifiedRef` 也不包含完整资格查询快照指纹。以下是本模块唯一公开技术桥；它不改变已接收 Joint DTO、两个消费者的原合同或资格 Owner 的事实权威。

```csharp
namespace Asun.Modules.CalibrationAssets.Joint;

public sealed record JointQualificationExpectation(
    QualificationStatus Status,
    JointPublishedRef Asset,
    QualificationId? QualificationId,
    RevisionId? QualificationRevision,
    AuthorityWatermark? Watermark,
    DateTimeOffset? ValidFrom,
    DateTimeOffset? ValidTo,
    JointQualifiedRef? ResolveQualified,
    JointUse ExpectedScope,
    ContentRef ExpectedSnapshotContent,
    OperationId ResolveOperationId,
    OperationId QualificationQueryOperationId);

public sealed record JointConsumerBindingRequest(
    JointQualificationExpectation Expected,
    AuthorityWatermark? RecheckedWatermark,
    QualificationStatus RecheckedStatus,
    ContentRef? RecheckedSnapshotContent,
    OperationId WatermarkRecheckOperationId,
    JointUse RequestedUse,
    DateTimeOffset EvaluatedAtUtc,
    string BridgePackageVersion); // 本版固定 "1.0.0"，只表示桥包SemVer

public readonly record struct JointTechnicalRevisionFingerprint(string Id, string Sha256);

public sealed record JointConsumerBindingProjection(
    string BridgePackageVersion,
    JointPublishedRef SourceAsset,
    JointQualificationSnapshot SourceQualification,
    ContentRef QualificationSnapshotContent,
    JointTechnicalRevisionFingerprint ReconstructionAsset,
    JointTechnicalRevisionFingerprint ReconstructionQualification,
    string StructuredLightAssetId,
    string StructuredLightAssetVersion,
    string StructuredLightAssetSha256);

public sealed record JointConsumerBindingResult(
    ApplicabilityStatus Status,
    JointConsumerBindingProjection? Projection,
    ContentRef? SnapshotContent,
    IReadOnlyList<ApplicabilityFinding> Findings);

public static class JointQualificationBinding
{
    public static JointConsumerBindingResult Bind(
        JointQualificationSnapshot snapshot,
        JointConsumerBindingRequest request);
}
```

`Bind` 只核对传入纯值，不查询 Authority、不签发资格，也不验证调用方本身可信。真实 Host 必须按本节取得并保管原 Owner 返回值后才能调用；把同一可篡改副本同时填入 Expected、snapshot 和 RecheckedWatermark，至多证明副本一致，不能证明来源。缺原 Task/原响应关联时 Host 先返回 Unknown，不调用下游。主控已完整回读本节、原JointQualificationQuery/SolverExecutionContext/公开codec及双Host，限定内容接收本次资格绑定技术桥增量；CAL-C1/C2/C3/JC/CR 原六项规格接收保持，不据此提升真实实现或资格门。

**期望与比较域：** `Expected` 保留原只读响应的 Status、Asset、Id→QualificationId、Revision→QualificationRevision、Watermark、ValidFrom/ValidTo、Scope→ExpectedScope 和完整快照的 ExpectedSnapshotContent。Qualified 时还保存同次成功 Resolve 返回的完整 `JointQualifiedRef` 为 ResolveQualified；逐字段比较其 Asset、QualificationId、QualificationRevision、Watermark 的 Authority/Epoch/Revision/ObservedAtUtc/ValidUntilUtc 及 ValidFrom/ValidTo，不以只比时间窗代替。非 Qualified 响应 ResolveQualified 必须 null，不能由 Host 人工制造 Qualified 引用。

`ResolveOperationId` 和 `QualificationQueryOperationId` 非空，本版内部 ReadAsync 查询沿 Resolve 的 execution.OperationId，二者必须相等；这是同一个 Resolve 的 child 调用，不伪造第二个 Query ID。`WatermarkRecheckOperationId` 非空且不同于 Resolve ID，是装配前复查的原查询 ID。ID 只定位根内原任务/请求/结果，不是签名、不进入快照 hash，不凭 GUID 相等推断来源。`BridgePackageVersion` 固定严格文本 `1.0.0`，仅表示技术桥包 SemVer；源 RevisionId 仍为原 string，不截取、清理、替换或推测版本。Asset/Qualification Id 还须分别满足消费者原 ID 域（SL 1..128 ASCII `[A-Za-z0-9._:-]`，IM-032 非空、≤128字符、无控制字符及未验证 latest）；不合法就拒绝该桥，不改写 ID。

**唯一编码与限额：** 扩展既有 `JointCodec` 的 `byte[] EncodeQualificationSnapshot(JointQualificationSnapshot value)` 与 `Digest ComputeQualificationSnapshotDigest(JointQualificationSnapshot value)`，后者是对前者完整输出调用既有 ComputeDigest。头 ASCII `cp-joint-binary-v1`（无长度/BOM/终止符）；根名按 string 规则写 `JointQualificationSnapshotContent`；依次编码 `Status,Asset,Scope,CheckEvidence,Id,Revision,Watermark,ValidFrom,ValidTo,RuntimeValidationEvidence`，无任何字段投影排除。嵌套短 record 名、全部字段顺序/原单位、nullable 单字节标记、enum 名称、有限 binary64（-0归+0）、UInt32 UTF-8长度、Int32/Int64LE、UTC DateTime ticks 均复用 §3.7/§7.4.5；不使用 JSON/ToString/反射排列，不重算已接收资产/请求/候选摘要。ContentRef 的完整 Digest/Format/FormatRevision/ByteLength 均编码，Scope 包含完整 Asset、ActualOptics、Pattern、曝光覆盖窗、ActualVolume、Purpose。

编码前拒绝无效 surrogate、单字符串>256 UTF-8 bytes、未知 enum、非有限数、字段非法/checked溢出；输出总长≤65536 bytes，先计长再分配，不能造无限缓冲。Unknown/撤回快照允许保留原声明的可空字段并逐一编码；Qualified 缺必需字段可以编码合法空形状作审计，但不可 Applicable。快照 `ContentRef` 固定 Format=`cp-joint-qualification-snapshot`、FormatRevision=`RevisionId("1")`、ByteLength=实际规范字节长、Digest=SHA-256完整字节。它是技术绑定指纹，非资格原件签名/客户授权；CheckEvidence、RuntimeValidationEvidence、asset/candidate digest 都不能替代它。编码无解码入口，不声称检验并不存在的尾字节输入；Host 比较复算的完整 ContentRef 与原封存值。

**Bind 的确定顺序及失败值：** 所有比较逐字段/Ordinal（包括嵌套集合内容），不得依赖 C# record 对底层数组的引用相等。沿下列顺序遇首个失败立即返回一个 Finding，Applicable时Findings为空；Field为对应路径、Status=Failed/Unknown、MessageKey=`Calibration.NotApplicable`/`Calibration.QualificationUnknown`，无外部证据时Evidence=null。非法编码/版本/容量由helper返回Unknown、Projection=null、SnapshotContent=null，Field=`Binding.Encoding`/`Binding.Version`/`Binding.Budget`，不逃逸部分成功；直接codec非法参数抛ArgumentException，超限抛ArgumentOutOfRangeException，Bind转成上述有限结果。

1. 核请求 ID 关联/桥版本/有限结构与 ExpectedSnapshotContent 格式；无法核验→Unknown。对原 snapshot 编码得 SnapshotContent；后续不 Applicable 的合法快照仍保留它用于审计，Projection 一律 null。
2. 原可信复查 `RecheckedStatus=Suspended/Revoked/Expired` 直接 NotApplicable（Field=`RecheckedStatus`），撤回优先于旧 Qualified；Unknown、复查缺完整指纹或水位→Unknown。此结论只在 Host 已取得真实复查响应的前提下成立。
3. `snapshot.Status != Expected.Status` 或原快照完整 ContentRef 不等 ExpectedSnapshotContent，或 `snapshot.Scope != Expected.ExpectedScope`→Unknown（`ExpectedSnapshotContent/ExpectedScope`），覆盖只换 evidence 的篡改；不能把待绑定对象重新编码后同时覆写 Expected。原 snapshot 合法且与 Expected 一致但 Status=Suspended/Revoked/Expired→NotApplicable；Unknown→Unknown。
4. 核 `snapshot.Asset == snapshot.Scope.Asset == Expected.Asset == RequestedUse.Asset`；非时间 Scope 与 RequestedUse 的 ActualOptics/Pattern/ActualVolume/Purpose 精确相等，RequestedUse.ExposureFrom≤ExposureTo，且曝光闭区间落在原资格 Scope 覆盖窗和资格有效期内。不匹配→NotApplicable（`Asset/Scope/Exposure`），缺必要字段→Unknown。资格 ValidFrom 必填；ValidTo=null 保留无上界语义，不伪造日期。
5. Qualified 必须有 Id、Revision、Watermark、RuntimeValidationEvidence，并与 Expected 身份/修订/有效期以及 ResolveQualified 的**全部字段**相等；缺 ResolveQualified/任何字段不符→Unknown（`ResolveQualified`）。Snapshot.Watermark、Expected.Watermark、RecheckedWatermark 五个字段完全相等，RecheckedSnapshotContent=ExpectedSnapshotContent；不同 authority/epoch/revision/时间或只换 evidence→Unknown（`RecheckedWatermark/RecheckedSnapshotContent`）。EvaluatedAtUtc 在 ObservedAtUtc..ValidUntilUtc 闭区间内；水位时间不有序/过期→Unknown。pure helper 不证明水位无限有效。
6. 全部满足才 Applicable。SourceAsset/SourceQualification 防御复制并保持原值；Projection.QualificationSnapshotContent 与结果 SnapshotContent 精确相同。`ReconstructionAsset=(SourceAsset.Id.Value,SourceAsset.Digest.Hex)`，`ReconstructionQualification=(snapshot.Id.Value.Value,SnapshotContent.Digest.Hex)`（前一个Value解nullable，后一个Value取QualificationId原string）；Sha256为64位小写hex。SL三字段为`(SourceAsset.Id.Value,"1.0.0",SourceAsset.Digest.Hex)`。原Asset.Revision、QualificationRevision、AuthorityWatermark、Scope/两种evidence仍由完整伴随快照保真保存，技术桥不得将`source-A`、`qual-A`或`"1"`改成SemVer。

**可信取得及两个无 UI Host：** 原 Qualification Owner 由宿主显式注入的端口身份/配置确定，不从待绑定 snapshot.Authority 临时挑来源。使用本地转发观察器实现既有 IJointQualificationPort（不是新公共 API/存储）：在 module.Resolve 调用 Qualifications.ReadAsync 时，调用前在同根登记原 Query、execution、token、原 Owner 对象，Owner 的 ValueTask 恰一次 AsTask；强持原 Task，响应完成路径先防御复制完整响应和规范字节/指纹到根，再把原语义值交 Core。查询.OperationId=execution.OperationId=resolveId；根只接该 Resolve 对应一次 Owner Read（0次/多次/ID冲突为Unknown），禁止另查一份最近快照填补缺失。同根保留 Resolve 原 Task/Reply、Captured Query/Owner Task/完整响应；只有 Reply.Completion=ResourcesReleased、Error=null、Value.Status=Applicable 和完整 Qualified/Export 时才继续。Resolve.Qualified 与捕获响应全部资格字段相等、Export.Asset=捕获 Asset、CheckEvidence 等于捕获 Query，Query.Use 等于请求 Use、ContentDigest 等于其 Asset.Digest；缺关联即 Unknown。Captured snapshot.RuntimeValidationEvidence 的用途/路线绑定沿 Resolve 原预检，本 helper 仅保存/核引用，不能凭引用自身验证隐藏证据正文。

在装配前用**同一原 Owner 对象**新 recheckId，再调用既有 `ReadAsync(new JointQualificationQuery(originalQuery.Use,originalQuery.ContentDigest,originalQuery.CheckEvidence,recheckId), new SolverExecutionContext(recheckId,remainingBudget), linkedToken)`；执行上下文沿原公开形状，以父剩余时间和额度传入，Host作为这次调用的ledger Owner，不冒称由Core创建新的作业。同根先登记再启动原Task，完整复查snapshot先检查原Asset/Scope.Asset、Purpose/Pattern等本次请求关联，再复制/编码/封存；关联缺失或返回别的asset时Unknown，不能拿其它asset的Revoked回执当本次撤回。按原响应填RecheckedStatus/Watermark/SnapshotContent。不新增“查最新水位”未定义接口，也不只看通知推断水位。原Owner必须返回当前权威的不可变查询快照；即使只是ObservedAtUtc/ValidUntilUtc变化也按完整指纹变化拒绝旧绑定，不删除这两个字段去凑hash一致。支持域是本次Resolve到复查之间该快照仍精确当前的情况；不能保证该条件的来源只能Unknown，不能无界重试。

装配前复查结束后立即Bind/封存请求，在同一根准入锁内核Closing=false、无已知invalidation/epoch gap、期限/水位有效、父预算仍足；中间有异步等待/重新排队/已知invalidation则旧binding失效，不重复延长当前复查，在新操作按原Owner重新取得并重新Resolve。复查不是与下游提交原子事务；宿主真实执行/激活/提交仍按自己原事务重核权限和水位，不能把快照hash缓存成无限资格。

| 无 UI Host（原根本地调用，不新增公共 Host API） | 准确顺序及拒绝 |
|---|---|
| JointStructuredLightHost，A 发布后读/消费自己的明确 Joint asset | 沿 §7.4.6A 原 Solve/Validate/Publish，PublishedUnqualified 不绑定；另 new resolveId，用显式观察器/原 Owner Resolve→捕获 q1/s1 和 Qualified/Export→原 Owner recheckId/q2/s2→Expected 从 ResolveQualified+s1 原封存值投影→Bind(s1,request)→只在 Applicable 且伴随快照可保真保存时装配 SL AssetRef/projector dimensions/PhysicalMapping/Manifest/decoder；无先验标定的首次图案生成仍走原 non-measurement 路径，不制造 Qualified |
| JointReconstructionHost，B 只读独立实例 | Factory/Observations=null，显式同 Store/Gate 但自己的 root/options/观察器；明确 Use/PublishedRef→自己的 resolveId/q1/s1/Qualified/Export→自己的 recheckId/q2/s2→同一 Bind→核 Export.File 原hash/bytes、CameraFrame=WorldFrame、index0/1、NativeLengthToMm=1000及两端尺寸→CalibrationRef.Asset/DirectionCalibration/CalibrationScope.Asset 同 ReconstructionAsset，CalibrationScope.Qualification=ReconstructionQualification，ValidFrom/To 来自完整 Qualified→在本地准入锁封存→才开自己的 native file/decode/reconstruct。Synthetic/CalibrationReplay 仅断言装配，不交真实 HALCON |

两 Host 均复用原有 MaxRoots=2、MaxTasksPerRoot=64、MaxBuffersPerRoot=8 根，从构造/查询前预留。桥增量逻辑费用固定1MiB：原/待绑定/复查编码各≤64KiB（合计≤192KiB），其余≥832KiB用于有限字段的深复制快照、helper输出、请求/期望和根记录；既有 Export.Bytes、Store读缓冲、workspace/native在途费用另按 §7.4.4/6 原额度相加，不能把任意大小的 Export 藏进桥的1MiB。checked合计不超过父 MaxResidentBytes/根总预算/共享gate实际剩余；同一费用只有一个Owner，借用已有snapshot记录不能重复申请、也不能漏计仍Held资源。原根预留峰值已包含桥增量；不持gate预约跨再次预约Resolve而制造自锁，模块IO预约按原流程执行，桥以独立root输出额度强持快照/指纹到消费者归还。它是逻辑预算，实际CLR峰值另验。

根输出槽固定至多8项：①Export及Bytes、②原Owner快照与原规范字节、③ResolveReply、④Expected/RequestedUse、⑤复查快照与规范字节、⑥待绑定快照与helper临时字节、⑦BindingResult、⑧封存下游请求/伴随引用；深副本依上述额度计费，组件不另外无限开槽。Dispose只是归还模块资源，不提前退桥根输出。原Resolve Task、内部Owner Task和直接复查Task/请求/响应均在64任务槽内，caller取消/有限等待后仍保管原任务与缓冲到真实结束；超时/取消/迟到只有Unknown，不Bind、不触发native。finally原一次Stop/Dispose/全量移交照旧；Core Stop不能假称关闭Host直接复查任务，root等其真实结束且下游归还输出后才释放额度，pending不退根。provider/Store/Qualifications借用不Dispose。无完整伴随快照的B API直接走Joint专用绑定对象或拒绝，不剥离源revision后仅用普通AssetRef/RevisionRef运行。消费者接线和共享采纳仍待主控交各原会话更新。

**具体纯值 oracle 与完整向量（CAL.JOINT.BIND.01–08）：** 这组是独立软件编码样本，不由实际 solve/store 产生，不证明资格。复用 §7.4.6A 的 R/M/T/Frame/Dev/C/D、optics、runtimeBoth、volume 和 Id(n)；只取那些已完整指定值，不引用未定 candidate/check hash。t0=2026-10-11T00:00:00Z，a=t0−1day，b=t0+1day（UTC ticks 依次639271872000000000/639272736000000000/639273600000000000）。
asset=`JointPublishedRef(AssetId("syn-bind-asset"),R("source-A"),D(UTF8("SYNTHETIC|binding-asset|v1")))`；其 digest=`a3b5783df1fcf87c3e9192b923ed9c9cba8e238f2ee0660784fc9f6b42b74c58`。scope=`JointUse(asset,optics,runtimeBoth,a,b,volume,CalibrationReplay)`，requestedUse 同形只 ExposureFrom=t0、ExposureTo=t0+1ms。w1=`AuthorityWatermark("Synthetic","epoch-1",R("wm-A"),t0,b)`；s1=`JointQualificationSnapshot(Qualified,asset,scope,C("binding-check"),QualificationId("syn-q"),R("qual-A"),w1,a,b,C("runtime-HybridBoth"))`。qref1=`JointQualifiedRef(asset,QualificationId("syn-q"),R("qual-A"),w1,a,b)`。
Expected 全字段按 s1+qref1 取值，ExpectedSnapshotContent 按完整编码计算、ResolveOperationId=QualificationQueryOperationId=Id(201)；复查 Id(202)、RecheckedStatus=Qualified、RecheckedWatermark=w1、RecheckedSnapshotContent 同 s1，EvaluatedAt=t0、BridgePackageVersion="1.0.0"。两个 Host 各使用独立的 Id(201/202) 和 Id(301/302)，其余值等同但根不共享；IDs 不进以下向量。

| 具体变体（其余字段精确同 s1） | Bind/Host oracle 与技术摘要 |
|---|---|
| 正常：s2=s1、qref/Expected/recheck 全匹配 | Applicable；asset RevisionRef digest 为原 asset digest；Qualification RevisionRef digest 为 `c28ce09df20e2237cbb31357bd70a2f20113841e64fdfe0a9e1fd3c72c982a17`；源 source-A/qual-A 原string保持 |
| 改水位：s2仅 Watermark.Epoch="epoch-2"（Authority/Revision/时间不变），Expected/qref/s1仍epoch-1 | 复查 digest=`c0e16a99eb8dc57fdd7e512354ad4e9898a1d4e1465c820d2b33efed53e10d6e`，Unknown/Projection=null；仅 EvaluatedAt 在窗内不能接受，旧指纹无效。若另新 Resolve/新 Expected 全部由 Owner 的 epoch-2 结果取得并一致，可成为另一操作的 Applicable，不能原地改旧 Expected |
| 撤回：s2仅 Status=Revoked，保留所有其它字段 | 复查完整digest=`982a9327fbed9cd79e6933d5f4497190adfb377db6810fc1eb6cbe388d7bbf7a`，NotApplicable/Projection=null；旧qref不能盖过当前撤回。原首次查询本身Revoked时 Expected 由原Owner返回，ResolveQualified=null，也为NotApplicable |
| 仅换证据：s2仅 CheckEvidence=C("binding-check-2")，其它含 watermarks 都相同 | 完整digest=`df73ce1b44edcd91090747f25c34f27167752d7a2fbf4211d07d9429ea77229a`，Unknown/Projection=null；不得用水位未变宣称原快照相同。待绑定 s1 同样被替换而 Expected仍原封存指纹时也Unknown |

.01正常/深副本修改不影响已封存值；.02逐字段改变Asset Revision、QualificationRevision、Scope、两类evidence/有效期时指纹变化；.03撤回/Suspended/Expired拒绝；.04Authority/Epoch/Revision/ObservedAt/ValidUntil任一与期望或复查不符、缺值/过期Unknown；.05仅换evidence按上表，不借candidate hash填资格；.06非法bridge SemVer/源ID/缺伴随快照拒绝；.07原Owner来源被同副本替代、query/Resolve ID关联错误、迟到/超时均由Host Unknown；.08逐字节复算下面两个完整输出及SHA-256，差异仅Epoch最后字节，不修改旧二维/Joint请求/CR向量。

<details>
<summary>完整规范字节向量：正常与只改水位 Epoch（各2904 bytes；无省略/占位）</summary>

正常 s1：

```text
63702d6a6f696e742d62696e6172792d7631210000004a6f696e745175616c696669636174696f6e536e617073686f74436f6e74656e74090000005175616c6966696564110000004a6f696e745075626c697368656452656607000000417373657449640e00000073796e2d62696e642d61737365740a0000005265766973696f6e496408000000736f757263652d4106000000446967657374070000005348412d3235364000000061336235373833646631666366383763336539313932623932336564396339636261386532333866326565303636303738346663396636623432623734633538080000004a6f696e74557365110000004a6f696e745075626c697368656452656607000000417373657449640e00000073796e2d62696e642d61737365740a0000005265766973696f6e496408000000736f757263652d4106000000446967657374070000005348412d32353640000000613362353738336466316663663837633365393139326239323365643963396362613865323338663265653036363037383466633966366234326237346335380b0000004a6f696e744f70746963731b000000446576696365436f6e66696775726174696f6e536e617073686f740700000073796e2d63616d0e00000073796e2d6f70746963732d63616d08000000417265615363616e0d00000043616d6572614d6f64656c496412000000617265615f7363616e5f6469766973696f6e0a0000005265766973696f6e496401000000310c00000073796e2d6c656e732d63616d0500000066697865640b00000070657273706563746976650800000073796e2d63616d3006000000446967657374070000005348412d32353640000000316635313536613739636435383764366537366636623363353733363462363461313436663463333733653633346264636661323935306235636130353062304000000030000000000000000000000040000000300000000100000001000000010000000000408f4001000000000000000001060000004c656e677468000000000000d03f050000004d65746572010b00000054656d706572617475726500000000000034400700000043656c73697573010a00000073796e2d6879627269641b000000446576696365436f6e66696775726174696f6e536e617073686f740800000073796e2d70726f6a0f00000073796e2d6f70746963732d70726f6a08000000417265615363616e0d00000043616d6572614d6f64656c496412000000617265615f7363616e5f6469766973696f6e0a0000005265766973696f6e496401000000310d00000073796e2d6c656e732d70726f6a0500000066697865640b00000070657273706563746976650900000073796e2d70726f6a3106000000446967657374070000005348412d3235364000000032386533663366323162333339663536363530656335343639626165366433333461623166366332353662646530383336656532626665313631643535363165500000003c0000000000000000000000500000003c0000000100000001000000010000000000408f4001000000000000000001060000004c656e677468000000000000d03f050000004d65746572010b00000054656d706572617475726500000000000034400700000043656c73697573010a00000073796e2d6879627269640f000000436f6f7264696e6174654672616d650800000073796e2d63616d300b000000526967687448616e6465641a000000582072696768743b205920646f776e3b205a20666f72776172640f000000436f6f7264696e6174654672616d650900000073796e2d70726f6a310b000000526967687448616e6465641a000000582072696768743b205920646f776e3b205a20666f72776172640a000000436f6e74656e7452656606000000446967657374070000005348412d32353640000000323439333365616332356562333262643239373061313736636431343563323366393761663563653139366332393031633664363862303366646530623430361200000073796e7468657469632d65766964656e63650a0000005265766973696f6e496401000000312000000000000000130000004a6f696e7452756e74696d655061747465726e500000003c000000040000001e0000000a000000487962726964426f74680a000000436f6e74656e7452656606000000446967657374070000005348412d32353640000000646437333132636131663561626463353530643132316635363039363464363361353135376462663161653132313237663234303932363866326639653532611a00000073796e7468657469632d7061747465726e2d6d616e69666573740a0000005265766973696f6e496401000000312100000000000000130000004a6f696e744164617074657256657273696f6e110000006465636f6465722d73796e7468657469630a0000005265766973696f6e496401000000310b00000053796e7468657469632f3106000000446967657374070000005348412d32353640000000623838383832636564636631383635666538613530636231303366383833333137663139653538383536306333613163653936313463316331633661666336390a000000436f6e74656e7452656606000000446967657374070000005348412d32353640000000393834663237623263626263396439373837326231313566653332326638643336313436353638383037643336643436636664323432396331646636643636641200000073796e7468657469632d65766964656e63650a0000005265766973696f6e496401000000312b000000000000000080756d6126df08000049c2f327df080b0000004a6f696e74566f6c756d650f000000436f6f7264696e6174654672616d650800000073796e2d63616d300b000000526967687448616e6465641a000000582072696768743b205920646f776e3b205a20666f727761726406000000506f696e7433060000004c656e677468ec51b81e85eba1bf050000004d65746572060000004c656e6774687b14ae47e17a84bf050000004d65746572060000004c656e67746814ae47e17a14ce3f050000004d6574657206000000506f696e7433060000004c656e677468ec51b81e85eba13f050000004d65746572060000004c656e6774687b14ae47e17a843f050000004d65746572060000004c656e677468f6285c8fc2f5d03f050000004d657465720b00000054656d706572617475726500000000000034400700000043656c736975730b00000054656d706572617475726500000000000035400700000043656c736975731100000043616c6962726174696f6e5265706c61790a000000436f6e74656e7452656606000000446967657374070000005348412d32353640000000363061383135343838363534303566376165386536326437383161616131316631366239313530393136656664396434666437383731306231343565623261351200000073796e7468657469632d65766964656e63650a0000005265766973696f6e496401000000311a00000000000000010f0000005175616c696669636174696f6e49640500000073796e2d71010a0000005265766973696f6e4964060000007175616c2d410112000000417574686f7269747957617465726d61726b0900000053796e7468657469630700000065706f63682d310a0000005265766973696f6e496404000000776d2d410040df972a27df08000049c2f327df08010080756d6126df0801000049c2f327df08010a000000436f6e74656e7452656606000000446967657374070000005348412d32353640000000626539373537383061383136336333626237636136643766373761396331373832663266303231643538396633343030343963333961373237323536363330651200000073796e7468657469632d65766964656e63650a0000005265766973696f6e496401000000311f00000000000000
```

SHA-256：`c28ce09df20e2237cbb31357bd70a2f20113841e64fdfe0a9e1fd3c72c982a17`。

改水位 s2（只将 Epoch 从 epoch-1 改为 epoch-2）：

```text
63702d6a6f696e742d62696e6172792d7631210000004a6f696e745175616c696669636174696f6e536e617073686f74436f6e74656e74090000005175616c6966696564110000004a6f696e745075626c697368656452656607000000417373657449640e00000073796e2d62696e642d61737365740a0000005265766973696f6e496408000000736f757263652d4106000000446967657374070000005348412d3235364000000061336235373833646631666366383763336539313932623932336564396339636261386532333866326565303636303738346663396636623432623734633538080000004a6f696e74557365110000004a6f696e745075626c697368656452656607000000417373657449640e00000073796e2d62696e642d61737365740a0000005265766973696f6e496408000000736f757263652d4106000000446967657374070000005348412d32353640000000613362353738336466316663663837633365393139326239323365643963396362613865323338663265653036363037383466633966366234326237346335380b0000004a6f696e744f70746963731b000000446576696365436f6e66696775726174696f6e536e617073686f740700000073796e2d63616d0e00000073796e2d6f70746963732d63616d08000000417265615363616e0d00000043616d6572614d6f64656c496412000000617265615f7363616e5f6469766973696f6e0a0000005265766973696f6e496401000000310c00000073796e2d6c656e732d63616d0500000066697865640b00000070657273706563746976650800000073796e2d63616d3006000000446967657374070000005348412d32353640000000316635313536613739636435383764366537366636623363353733363462363461313436663463333733653633346264636661323935306235636130353062304000000030000000000000000000000040000000300000000100000001000000010000000000408f4001000000000000000001060000004c656e677468000000000000d03f050000004d65746572010b00000054656d706572617475726500000000000034400700000043656c73697573010a00000073796e2d6879627269641b000000446576696365436f6e66696775726174696f6e536e617073686f740800000073796e2d70726f6a0f00000073796e2d6f70746963732d70726f6a08000000417265615363616e0d00000043616d6572614d6f64656c496412000000617265615f7363616e5f6469766973696f6e0a0000005265766973696f6e496401000000310d00000073796e2d6c656e732d70726f6a0500000066697865640b00000070657273706563746976650900000073796e2d70726f6a3106000000446967657374070000005348412d3235364000000032386533663366323162333339663536363530656335343639626165366433333461623166366332353662646530383336656532626665313631643535363165500000003c0000000000000000000000500000003c0000000100000001000000010000000000408f4001000000000000000001060000004c656e677468000000000000d03f050000004d65746572010b00000054656d706572617475726500000000000034400700000043656c73697573010a00000073796e2d6879627269640f000000436f6f7264696e6174654672616d650800000073796e2d63616d300b000000526967687448616e6465641a000000582072696768743b205920646f776e3b205a20666f72776172640f000000436f6f7264696e6174654672616d650900000073796e2d70726f6a310b000000526967687448616e6465641a000000582072696768743b205920646f776e3b205a20666f72776172640a000000436f6e74656e7452656606000000446967657374070000005348412d32353640000000323439333365616332356562333262643239373061313736636431343563323366393761663563653139366332393031633664363862303366646530623430361200000073796e7468657469632d65766964656e63650a0000005265766973696f6e496401000000312000000000000000130000004a6f696e7452756e74696d655061747465726e500000003c000000040000001e0000000a000000487962726964426f74680a000000436f6e74656e7452656606000000446967657374070000005348412d32353640000000646437333132636131663561626463353530643132316635363039363464363361353135376462663161653132313237663234303932363866326639653532611a00000073796e7468657469632d7061747465726e2d6d616e69666573740a0000005265766973696f6e496401000000312100000000000000130000004a6f696e744164617074657256657273696f6e110000006465636f6465722d73796e7468657469630a0000005265766973696f6e496401000000310b00000053796e7468657469632f3106000000446967657374070000005348412d32353640000000623838383832636564636631383635666538613530636231303366383833333137663139653538383536306333613163653936313463316331633661666336390a000000436f6e74656e7452656606000000446967657374070000005348412d32353640000000393834663237623263626263396439373837326231313566653332326638643336313436353638383037643336643436636664323432396331646636643636641200000073796e7468657469632d65766964656e63650a0000005265766973696f6e496401000000312b000000000000000080756d6126df08000049c2f327df080b0000004a6f696e74566f6c756d650f000000436f6f7264696e6174654672616d650800000073796e2d63616d300b000000526967687448616e6465641a000000582072696768743b205920646f776e3b205a20666f727761726406000000506f696e7433060000004c656e677468ec51b81e85eba1bf050000004d65746572060000004c656e6774687b14ae47e17a84bf050000004d65746572060000004c656e67746814ae47e17a14ce3f050000004d6574657206000000506f696e7433060000004c656e677468ec51b81e85eba13f050000004d65746572060000004c656e6774687b14ae47e17a843f050000004d65746572060000004c656e677468f6285c8fc2f5d03f050000004d657465720b00000054656d706572617475726500000000000034400700000043656c736975730b00000054656d706572617475726500000000000035400700000043656c736975731100000043616c6962726174696f6e5265706c61790a000000436f6e74656e7452656606000000446967657374070000005348412d32353640000000363061383135343838363534303566376165386536326437383161616131316631366239313530393136656664396434666437383731306231343565623261351200000073796e7468657469632d65766964656e63650a0000005265766973696f6e496401000000311a00000000000000010f0000005175616c696669636174696f6e49640500000073796e2d71010a0000005265766973696f6e4964060000007175616c2d410112000000417574686f7269747957617465726d61726b0900000053796e7468657469630700000065706f63682d320a0000005265766973696f6e496404000000776d2d410040df972a27df08000049c2f327df08010080756d6126df0801000049c2f327df08010a000000436f6e74656e7452656606000000446967657374070000005348412d32353640000000626539373537383061383136336333626237636136643766373761396331373832663266303231643538396633343030343963333961373237323536363330651200000073796e7468657469632d65766964656e63650a0000005265766973696f6e496401000000311f00000000000000
```

SHA-256：`c0e16a99eb8dc57fdd7e512354ad4e9898a1d4e1465c820d2b33efed53e10d6e`。

</details>

上述字节严格含流头、根、两次完整资产ref、两端设备/optics、runtime pattern/decoder、volume、Scope曝光、全部evidence引用、资格身份/revision/watermark/有效期。主控已按每个公开字段独立构造正常/改epoch/撤回/仅换CheckEvidence四个完整输出：正常与改epoch各2904 bytes，与正文hex逐字节相等；撤回2902 bytes、仅换CheckEvidence2904 bytes，四个SHA-256均与本节一致。本次桥增量已限定内容接收；上述结论仅为软件oracle核对，不代表实际模块/JointCodec/C#/BCL Exe/HALCON/native/资格Owner或消费者桥运行。内部接口缺口按本节技术闭合，真实资格Owner、消费者桥/C#编译、HALCON/Store/性能/物理现场验收继续独立保留；消费者指导由主控派原SL/R3D Owner接线，本模块不修改其文件。


#### 7.4.6A 完整 Synthetic 小夹具与双 Host 实施卡

本卡取代上面的概念流程作为 CAL-JC 测试实施依据。所有值由公开DTO/codec、BCL生成，**Synthetic/1** 不运行真实光学模型，不使用假HALCON文件；native工程/物理资格不得直接引用这个夹具。测试辅助类固定在原测试工程 `Joint/JointSyntheticFixture.cs`，两个Host沿 §7.4.6 的Consumers路径；没有第三个交付项目。

为使外部Host可按公开合同建值，Core新增公开静态 `JointCodec`：`byte[] EncodeProfileContent(JointProfile profile)`（省Reference）、`byte[] EncodeObservation(JointObservationPacket packet)`（省Group.Packet）、`byte[] EncodeValidationPlan(JointValidationPlan plan)`（省Reference）、`byte[] EncodeSamplingQualification(JointSamplingQualification value)`、`byte[] EncodeArtifact(JointArtifactContent value)`、`byte[] EncodeCheckReport(JointCheckReport value)`（省Evidence）、`byte[] EncodeQualificationSnapshot(JointQualificationSnapshot value)`、`JointCheckReport DecodeCheckReport(ReadOnlySpan<byte> bytes,ContentRef evidence)`（核同格式/限额/EOF并补已核Evidence，禁止猜隐藏字段）、`Digest ComputeQualificationSnapshotDigest(JointQualificationSnapshot value)`、`Digest ComputeDigest(ReadOnlySpan<byte> bytes)`。编码头均 `cp-joint-binary-v1`、根短名分别为 §7.4.5 的投影名及 `JointValidationPlanContent/JointSamplingQualification/JointQualificationSnapshotContent`；按签名顺序，全部有界（普通Synthetic内容单次最多1MiB；资格快照另受7.4.6B的65536 bytes上限，均不能超过caller请求预算，不反射/JSON）。这不是HALCON解码/持久化入口；这些小值codec不读图像层/设备。任何引用和下表typed内容均先编码再给ContentRef，不填全零/固定占位digest。

**共同的构造记法（BCL辅助函数，非新模块公开服务）：** `R(x)=new RevisionId(x)`，`M(x)=new Length(x,Meter)`，`P(x)=new Pixel(x)`，`A(x)=new Angle(x,Radian)`，`T(x)=new Temperature(x,Celsius)`，`Frame(x)=new CoordinateFrame(x,RightHanded,"X right; Y down; Z forward")`；`D(bytes)=JointCodec.ComputeDigest(bytes)`。`C(label,format="synthetic-evidence",version="1")`把UTF8无BOM字节 `SYNTHETIC|{label}|v1` 放到容量8MiB的fixture内容字典，返回 `ContentRef(D(bytes),format,R(version),bytes.Length)`；`Put(bytes,format)`同样存真实bytes返回引用，`Typed(value,format,encode)`用指定公开codec，禁止hash一个record的ToString。字典key是完整Digest（ordinal）；Read不存在或digest/format/length不等即CAL-108，不访问路径。普通证据只有Synthetic标签，声明Unknown现场证据，不把它们当设备/客户原件；mock端口明确只在本卡测试过程中接收这些标签。规范typed证据仍逐字節核digest。所有Guid采用 `00000000-0000-0000-0000-{n:000000000000}`、`Id(n)=new OperationId(Guid.Parse(...))`，UTC时间 `t0=2026-10-11T00:00:00Z`。

| 完整构造对象 | 每一个字段/生成规则（无未定义变量） |
|---|---|
| frames/adapter | camFrame=Frame("syn-cam0")、projFrame=Frame("syn-proj1")、objFrame=Frame("syn-board")；solverVersion=`JointAdapterVersion("joint-synthetic",R("1"),"Synthetic/1",D(UTF8("SYNTHETIC|solver|v1")))`；decoderVersion同形Id="decoder-synthetic"/Build字节label="decoder" |
| 设备 | `Dev(role,w,h,frame)` 返回 DeviceConfigurationSnapshot：DeviceFingerprint="syn-"+role，OpticalFingerprint="syn-optics-"+role，SensorMode=AreaScan，CameraModel=CameraModelId("area_scan_division")，ConfigurationRevision=R("1"), LensIdentity="syn-lens-"+role, FocusState="fixed", MagnificationState="perspective", MountingConvention=frame.Id, ReadoutLayoutDigest=D(UTF8("SYNTHETIC|native-"+role+"|v1")), ImageWidth=w,ImageHeight=h,RoiX=RoiY=0,RoiWidth=w,RoiHeight=h,BinningX=BinningY=1,ExposureMicroseconds=1000,GainDb=0,WorkingDistance=M(0.25),Temperature=T(20),IlluminationFingerprint="syn-hybrid"`；cam=Dev("cam",64,48,camFrame)，projector=Dev("proj",80,60,projFrame)；两个frame参数不引入未声明设备字段 |
| Optics | `new JointOptics(cam,projector,camFrame,projFrame,C("native-1to1-mapping"))`；两端配置/Mapping显式且不同 |
| 参数 | `Vector(f,sx,w,h,cx,cy)`固定Model="area_scan_division"，Parameters依次 `Focus=f Meter,Kappa=0 PerMeterSquared,Sx=sx Meter,Sy=sx Meter,Cx=cx Pixel,Cy=cy Pixel,ImageWidth=w Pixel,ImageHeight=h Pixel`；cameraInitial=Vector(.0098,.0001,64,48,32,24)、projectorInitial=Vector(.01176,.00012,80,60,40,30)，mock solved分别Vector(.010,.0001,64,48,32,24)/Vector(.012,.00012,80,60,40,30)。测试必须证明读到的是solved而非initial |
| nominal/measured几何 | 稳定id P0..P5，i=0..5，nominal x=(i%3-1)*.04、y=(floor(i/3)-.5)*.04、z=0 meter；measured除了P1.x=.00001、P4.x=-.00001，其余等nominal。各ReferencePoint(Id,Nominal,Measured,M(.000001),2)。Nominal/Measured内容是ASCII无BOM行 `P{i},{x:R},{y:R},0\n`（InvariantCulture，nominal与measured分别生成），以Put(UTF8(...),"synthetic-xyz-csv")存，Certificate=C("board-certificate")，GeometryDigest=D(UTF8的按id排序measured同一bytes)；ReferenceGeometryRef(AssetId("syn-board"),R("1"),NominalRef,MeasuredRef,Certificate,GeometryDigest)，Geometry(frame=objFrame,Points=6点,ReferenceTemperature=T(20),FlatnessEvidence=C("flatness"),CertificateValidUntilUtc=t0+1day) |
| 标准板描述 | `HalconRectangularDotPlateDescriptor(AssetId("syn-board"),R("1"),GeometryDigest,Meter,"P0 lower indexed origin; centred coordinates","+Y down rows","+X right columns","synthetic-board.descr",2,3,M(.04),M(.004),Certificate.Digest,FlatnessEvidence.Digest)`；descr字符串只做模拟拓扑，不执行路径/native finder，真实板.descr仍按 §7.2 原件依赖 |
| Volume /采样域 | Volume=`JointVolume(camFrame,Point(-.035,-.010,.235),Point(.035,.010,.265),T(20),T(21))`，Point(x,y,z)的三个Length全meter；samplingDomain同形Min=(-.06,-.06,.20)、Max=(.06,.06,.31)、温度20..21 |
| samplingProfile | `JointSamplingProfile(R("1"),P(2),P(4.5),P(6),256,3,2,P(.5),120,245,60,P(.000001),P(.000001),P(.000001),.000001,M(.000005),P(.05),samplingRef)`；samplingRef稍后按无循环顺序产生 |
| samplingQualification | `JointSamplingQualification(R("1"),GeometryDigest,optics,R("1"),P(2),P(4.5),P(6),M(.000001),P(.01),C("sampling-centre-witness"),samplingDomain,t0-1day,t0+1day)`；先Typed(...,"cp-joint-sampling-qualification-v1",JointCodec.EncodeSamplingQualification)取得samplingRef，再构造samplingProfile。模拟值不证明真实CentreBiasBound |
| plan | `JointValidationPlan(reference,GeometryDigest,Point(0,0,0),new double[]{0,0,1},C("pre-registered-independent-physical-plan"),samplingRef)`；先以任一合法临时Reference构造，EncodeValidationPlan省Reference，Put产生planRef后以with{Reference=planRef}封存。placeholder Reference必须只是内部构造前的合法C("plan-build"),不写入最终hash/任何请求 |
| pattern两端/运行路线 | `bothManifest=C("hybrid-both-80x60-s4","synthetic-pattern-manifest")`、verticalManifest=C("hybrid-vertical-80x60-s4","synthetic-pattern-manifest")，direction=C("vertical-column-horizontal-row")；`JointPattern(80,60,4,30,bothManifest,decoderVersion,direction)`；runtimeBoth=`JointRuntimePattern(80,60,4,30,HybridBoth,bothManifest,decoderVersion,direction)`，runtimeVertical同形HybridVertical/verticalManifest。它们明确是模拟pattern元数据，没有伪造实际HALCON pattern数量/文件 |
| Limits | `JointLimits(3,2,6,6,.10,A(.05),M(.05),M(.015),A(.04),P(.02),P(.05),P(.02),P(.05),M(.00001),M(.00001),M(.00001),M(.00001),TimeSpan.FromMilliseconds(2),TimeSpan.FromMilliseconds(50),1e-9)`；按 §7.4.2 最新签名：去掉旧MaxSamplingSpread/MaxSamplingError，MaxPointsPerGroup=6，所有数仅软件fixture，不是现场标准 |
| Profile | `JointProfile(reference,pattern,cameraInitial,projectorInitial,limits,volume,planRef,C("separate-optics-parameter-sources"),[runtimeBoth,runtimeVertical],samplingProfile)`；profileRef=`JointProfileRef(R("1"),D(JointCodec.EncodeProfileContent(profile)))`，编码省整个Reference，先用R("1")/D(UTF8("SYNTHETIC|profile-build|v1"))构造临时Reference，然后with新ref封存，无自引用；最后实例引用该final profile |
| Budget/options/clock | Budget=`CalibrationExecutionBudget(2s,3s,32,65536,10000,8388608,1)`；options=`CalibrationAssetsOptions(2,128,8388608,1s,64,8)`；FixedTimeProvider.GetUtcNow=t0，GetTimestamp单调且TimestampFrequency=1000000，Delay只由fixture显式Advance推动，正常调用立即完成无需推进；timeout注入以Advance过相应单调Deadline/WaitLimit触发，不把UTC跳变当执行截止 |

**五个观测包与支持层，完全指定算法/数值：** 组g=0..4，Fit=g0/g1/g2、Check=g3/g4；depth d=[.22,.25,.28,.23,.27]，rotation Rx(angle) 的angle=[-.12,0,.12,-.08,.08] Radian，Rx行优先 `[1,0,0, 0,cos(a),-sin(a), 0,sin(a),cos(a)]`、translation=(0,0,d)。RigidPose.From=objFrame/To=camFrame/Source=C("pose-g"+g)。对每实测点，Q=R*Measured+translation，camera `(r,c)=(24+100*Qy/Qz,32+100*Qx/Qz)`，projector `(pr,pc)=(30+100*Qy/Qz,40+100*(Qx-.02)/Qz)`。setupHProjector.From=projFrame/To=camFrame、rotation identity、translation=(.02,0,0)、Source=C("setup-baseline"); native forward rays在各端Z均正。

每个64×48相机integer pixel的plane深度 `Z(r,c)=cos(a)*d/(-sin(a)*(r-24)/100+cos(a))`，correspondence layer `ProjectorRows=r+6`、`ProjectorColumns=c+8-2/Z(r,c)`，Float64LE按row-major写。中心对应矩阵（row/col约定）未规范化时是
`H=[1,0,6, .02*tan(a)/d,1,8-2/d-.48*tan(a)/d, 0,0,1]`。
outer/inner Matrix均H/其Frobenius范数，首项为正，maxLeaveOut/inverse/centreShift=0；adapter模拟独立按公式核matrix及中心，而真实adapter另调用HALCON估矩阵。原image WhiteImage为哑光白180；距离任一6个相机中心<=1.8 pixel的圆区域值20（黑圆），BlackImage全10；WhiteSurfaceMask仅非黑圆pixel为1，解码ValidMask还要求pr/pc位于80×60栅格，其它为0。每个包CameraImage=WhiteImage，其hash可在相同g重复，但不同g黑圆位置不同；BlackImage相同不是重复物理组判据。fit/check duplicate frame禁止的是同原CaptureGroup/同white+pattern sequence证据，不禁止自然相同黑场。

每点枚举 §7.4.2 的radius[2,6]完整integer支持，仅保留两mask1/white条件满足像素，顺序row/col；没有>256支持。`JointSupportPixel` Row/Col是该pixel、ProjectorRow/Column由上述两层、三bool全true。`JointLocalMap(Hnorm,Hnorm,P(0),P(0),P(0),samplingRef)`，`JointPairedPoint(Pi,P(r),P(c),support,P(pr),P(pc),map)`。Group Id=ObservationId("g"+g)、PoseIndex=g、CaptureGroupId="capture-g"+g、ObservedAtUtc=t0+g ms。先以C("packet-build-g"+g)作临时Packet，构造包各字段为group,optics,pattern,WhiteRef,WhiteRef,BlackRef,WhiteMaskRef,RowsRef,ColsRef,ValidRef,C("quality-g"+g),C("stable-g"+g),"syn-clock-1",1ms,100ms,6 points；EncodeObservation省Group.Packet，Put(format="cp-joint-observation-v1")后with{Group=group with{Packet=finalPacketRef}}封存。取finalGroup给Fit/Check，Input=`JointInput(profile,optics,target,geometry,[g0,g1,g2],[g3,g4])`，没有第二Partition/隐藏session。

**所有公开端口fixture（正常方法同步完成ValueTask；故障闩锁使用原Task，禁止返回Canceled wrapper冒结束）：**

| 装配/完整端口 | 固定返回、状态、失败和所有权 |
|---|---|
| `IJointObservationProvider` | OpenContentAsync精确Input/读包/Plan/采样或独立物理证据已声明ref→字典只读MemoryStream深副本，无任意路径，caller唯一Dispose；ReadAsync精确group→上述finalPacket深副本；ReadPlanAsync(planRef)→finalPlan；ReadSamplingQualificationAsync(samplingRef)→finalSamplingQualification；其它引用CAL-108。ReadPhysicalEvidenceAsync(candidate,finalPlan)→`JointPhysicalEvidence(candidate,profile.Reference,planRef,Input.Check,M(.000002),2,C("uncertainty-method"),C("temperature-20"),C("temperature-21"),C("repeatability"),"Synthetic",R("1"))`；不缓存/改变candidate，无设备/背景任务/lease |
| `IJointSolverScopeFactory/IJointSolverScope` | Version=solverVersion；CreateScope只建本地scope保存借用provider。SolveAsync校验Input/exec、读五包和采样资格，mock每pose报告=`JointPoseReport(finalGroup,上述RigidPose,P(0),P(0),P(0),P(0),6,实际camera row span/47,实际camera col span/63,A(.06),M(0))`；covariance bytes是36个0的Float64LE，参数labels按各端Focus/Kappa/Sx/Sy/Cx/Cy，存Format="synthetic-covariance-f64le"；FitReport=GlobalRmse0、Groups=fit三份、两个solvedVector/covRef、setupHProjector、Profile.ParameterSources；Setup bytes固定UTF8 `SYNTHETIC|SETUP|cam=0|proj=1|meter|baseline=.02|v1`，经workspace.WriteAsync("cp-joint-synthetic-setup-v1",R("1"),MemoryStream(bytes),65536,exec.OperationId,token)存；Content=`JointArtifactContent(R("1"),input,fit,setupRef,solverVersion,t0)`。mock不能声称实际测得covariance/ray/statistics；ValidateAsync读两check包、plan/sampling/physical输出`JointCheckReport(candidate,planRef,两checkPoseReport,M(0),M(0),M(.000002),volume,physical,evidence)`，EncodeCheckReport省Evidence、workspace封存原bytes后替換Evidence；Dispose scope一次，无其它对象释放 |
| `IJointArtifactStore` | dict每PublishedRef→JointStoredArtifact、每原OperationId→(RequestDigest,Receipt)，容量16。WriteAsync重算candidate/content/check，按exec.OperationId拒不同内容CAL-107，复制source中Input/Setup/证据引用闭包所有实际bytes进store-owned字典；Published=`JointPublishedRef(AssetId("syn-joint-asset"),R("1"),candidate.Digest)`，receipt=`JointPublishReceipt(exec.OperationId,Published,PublishedRef,false)`，stored报告由成功Check规范字节解回/不自由补字段。同id同摘要回原值不重写；读asset精确校验dict/闭包；Query原id Found/不存在NotCommitted（无在途写入正常fixture），故障写入尚在途Unknown。OpenContentAsync以store-owned副本返回只读MemoryStream、Core负责Dispose；无输入路径。若原Publish迟到，仍归原id，不自动触发激活 |
| `IJointQualificationPort` | 一个显式测试bool `DecisionAvailable=false`，只允许fixture驱动在A发布后改true模拟外部Owner（模块无写API）。ReadAsync false→`JointQualificationSnapshot(Unknown,query.Use.Asset,query.Use,query.CheckEvidence,null,null,null,null,null,null)`；true→Qualified/精确Asset、Scope=query.Use with ExposureFrom=t0-1day/To=t0+1day,同checkEvidence、QualificationId("syn-q"),R("1"),Watermark("Synthetic","epoch-1",R("1"),t0,t0+1day),ValidFrom=t0-1day,ValidTo=t0+1day,RuntimeValidationEvidence=C("runtime-"+query.Use.Pattern.Route)。只允许CalibrationReplay且所有label为Synthetic；SurfaceReconstruction返回Unknown。WatchAsync正常序列空并立刻结束；故障用可取消闩锁保持原enumerator/MoveNext和Dispose任务 |
| `ICalibrationExecutionGate` | shared gate总容量8388608、并发Solve1；ReserveAsync正peakBytes<=剩余额度返scope lease，Dispose一次归还；不够返回CAL-112。Root输出byte额度同有限总预算、held时不复用；测试可按Id指定Reserve闩锁/释放闩锁，late lease仍同ledger一次Dispose。验证released计数及peak<=额度，不用GC当归还 |
| diagnostics/time/options | `ICalibrationDiagnostics.Record`保存最多128条CalibrationDiagnosticEntry，overflow记有界计数不抛原业务异常；异常注入仅该sink自己throw，Core隔离。clock/options/Budget如上。没有其它ReferenceResolver/Binding/ServiceLocator。所有端口读/写/Dispose有计数器，资源归还预期0held，factory/Stop/Dispose失败不假记成功 |

Store闭包遍历只沿typed record中ContentRef（Profile/plan/sampling/packets/物理证据和其typed内容），不遍历证据标签字符串或执行descr。Core在各provider.Read前后的跟踪调用把本次Input/返回包/Plan/采样/physical证据所声明的原ContentRef经provider.OpenContentAsync核原字节hash并导入自己的workspace（format/revision保持不变，额度内复制）；source完整且内容不可变，构造期不能偷偷启动IO。每个Stream都有原operation/ledger、真实Dispose后才能解除预约；Validate新增独立证据也在Publish前导入同workspace。Store只用公开source.OpenReadAsync从workspace复制完整闭包，**不访问fixture私有字典、不假设provider和Store同实例**。正常fixture所有引用由C/Typed/Put存好，导入的内容有真实字节；scope只产生它自己的新setup/check/covariance。真实耐久Store和source仍留CAL-JI接线门，公开copy路径本卡可以无native验证。

**双Host完整卡（不是未定义的input/adapters变量）：** A调用 `JointSyntheticFixture.Build()` 返回上述全部构造对象及端口；B只从同fixture显式借同Store/Gate/Clock/Diagnostics，自己的options/请求/root均独立，Factory/Observations=null，不调用A私有类或scope。factory前根槽的具体字段固定：`RootSlot(RootId,Closing,Options,Adapters,Input?,OriginalTasks[64],Modules[1],Outputs[8],OperationIds[64],StopTask?,DisposeTask?,ExceptionDispatchInfo?,CleanupErrors[16],OfferId?,TransferTask?,OwnerConfirmed,ReservedBytes)`，根注册器最多2槽，保留lookup不自动淘汰。root Input保存已构造值直到清理/确认；原Task结果在完成路径先写Modules/Outputs，再投递caller；业务Task与完成路径都计64额度。

```csharp
// 本地测试Host卡；RootRegistry的精确实现行为紧随本块，不是产品服务依赖。
var fixture = JointSyntheticFixture.Build(); // 本卡所有构造规则，不能另选门限/模型
var roots = new RootRegistry(maxRoots: 2, maxTasks: 64, maxOutputs: 8, maxBytes: 8_388_608);
JointPublishedRef? published = null;
var slotA = roots.Reserve(1, fixture.Options, fixture.AdaptersA, fixture.Input, 4_194_304);
ExceptionDispatchInfo? businessA = null;
try {
    var moduleA = await slotA.ObserveFactory(
        () => JointCalibrationModule.Create(fixture.Options, fixture.AdaptersA), TimeSpan.FromSeconds(3));
    var solved = await slotA.Observe(Id(1), () => moduleA.SolveAsync(
        new JointCall<JointSolveInput>("1",Id(1),fixture.Budget,
        new JointSolveInput(new CalibrationSessionId(Id(100).Value),fixture.Input)),slotA.Token).AsTask(),TimeSpan.FromSeconds(3));
    RequireReleasedValue(solved); // Completion==Released、Error==null、Value!=null，否则固定HostContractException
    var validated = await slotA.Observe(Id(2), () => moduleA.ValidateAsync(
        new JointCall<JointValidateInput>("1",Id(2),fixture.Budget,
        new JointValidateInput(solved.Value!.Candidate)),slotA.Token).AsTask(),TimeSpan.FromSeconds(3));
    RequireReleasedValue(validated);
    Require(validated.Value!.Status==ValidationStatus.Validated && validated.Value.Report!=null);
    var receipt = await slotA.Observe(Id(3), () => moduleA.PublishAsync(
        new JointCall<JointPublishInput>("1",Id(3),fixture.Budget,
        new JointPublishInput(solved.Value!.Candidate,validated.Value!.Report!.Evidence)),slotA.Token).AsTask(),TimeSpan.FromSeconds(3));
    if (receipt.Completion!=OperationCompletion.ResourcesReleased || receipt.Value?.Status==PublishStatus.PublishUnknown || receipt.Error?.SideEffectOutcomeUnknown==true) {
        // 且只在原publish任务/resources实际Released后允许本卡继续；否则保留根，进finally。
        Require(moduleA.GetOperationState(Id(3)).Status==OperationExecutionStatus.ResourcesReleased);
        var query = await slotA.Observe(Id(4), () => moduleA.QueryPublishReceiptAsync(
            new JointCall<JointReceiptInput>("1",Id(4),fixture.Budget,new JointReceiptInput(Id(3))),slotA.Token).AsTask(),TimeSpan.FromSeconds(3));
        RequireReleasedValue(query); Require(query.Value!.Status==ReceiptQueryStatus.Found && query.Value.Receipt?.Status==PublishStatus.Published);
        published=query.Value.Receipt!.Published;
    } else { RequireReleasedValue(receipt); Require(receipt.Value!.Status==PublishStatus.Published); published=receipt.Value.Published; }
    Require(published!=null); Require(receipt.Value is null || receipt.Value.QualificationIssued==false);
} catch (Exception error) { businessA=ExceptionDispatchInfo.Capture(error); }
finally { await roots.CloseOrRetain(slotA, Id(5), cleanupLimit:TimeSpan.FromSeconds(1)); }
// 业务失败照原栈抛；CloseOrRetain绝不覆盖它，保留槽时可把原异常交根/抛回caller。
businessA?.Throw(); Require(published!=null);

var adaptersB=new JointAdapters(null,null,fixture.Store,fixture.Qualifications,
    fixture.Gate,fixture.Diagnostics,fixture.Clock);
var slotB=roots.Reserve(2,fixture.Options,adaptersB,null,4_194_304);
ExceptionDispatchInfo? businessB=null;
try {
    var moduleB=await slotB.ObserveFactory(
        () => JointCalibrationModule.Create(fixture.Options,adaptersB),TimeSpan.FromSeconds(3));
    var use=new JointUse(published!,fixture.Optics,fixture.RuntimeVertical,
        fixture.T0,fixture.T0+TimeSpan.FromMilliseconds(4),fixture.Volume,JointPurpose.CalibrationReplay);
    var before=await slotB.Observe(Id(6),()=>moduleB.ResolveAsync(
        new JointCall<JointResolveInput>("1",Id(6),fixture.Budget,new JointResolveInput(use)),slotB.Token).AsTask(),TimeSpan.FromSeconds(3));
    Require(before.Completion==OperationCompletion.ResourcesReleased && before.Value?.Status==ApplicabilityStatus.Unknown && before.Value?.Export==null);
    fixture.Qualifications.DecisionAvailable=true; // 明确外部模拟决定，非模块API
    var after=await slotB.Observe(Id(7),()=>moduleB.ResolveAsync(
        new JointCall<JointResolveInput>("1",Id(7),fixture.Budget,new JointResolveInput(use)),slotB.Token).AsTask(),TimeSpan.FromSeconds(3));
    RequireReleasedValue(after); Require(after.Value!.Status==ApplicabilityStatus.Applicable && after.Value.Export!=null);
    var export=after.Value.Export!; // 此值及原Bytes先已登记slotB.Outputs，再交付
    Require(export.File.Format=="cp-joint-synthetic-setup-v1" && export.CameraIndex==0 && export.ProjectorIndex==1);
    Require(export.CameraFrame==fixture.Optics.CameraFrame && export.WorldFrame==export.CameraFrame);
    Require(export.NativeLengthToMm==1000 && JointCodec.ComputeDigest(export.Bytes.Span)==export.File.Digest);
    Require(export.Bytes.Span.SequenceEqual(fixture.SetupBytes));
    // B完整托管消费：核精确导出/资格/版本/字节；Synthetic格式绝不传read_camera_setup_model。
} catch(Exception error) { businessB=ExceptionDispatchInfo.Capture(error); }
finally { await roots.CloseOrRetain(slotB,Id(8),TimeSpan.FromSeconds(1)); }
businessB?.Throw();
```

代码块是C#调用卡，所有new类型/枚举以上述公开字段为准。`Require(false)`抛本地 `HostContractException`（继承Exception）、`RequireReleasedValue<T>`按行内三项判断，不解读MessageKey文本。Build的输出完整为 `(Input,Options,AdaptersA,Budget,Optics,Volume,RuntimeVertical,Store,Qualifications,Gate,Diagnostics,Clock,T0,SetupBytes)`；AdaptersA是`JointAdapters(factory,provider,store,qualifications,gate,diagnostics,clock)`、所有端口如表，Helper没有未定义的隐藏解析器/配置选择。允许将等价卡直接整理成正式C#，不得改参数/字段/判据。

**RootRegistry完整结束/故障卡：** Reserve锁内先核槽数/bytes/tasks额度，强持options/adapters/input再建立有界slot；ObserveFactory先登记原执行Task（构造委托在已登记task内执行）、delegate及依赖，成功先写module再完成交付；Observe先登记预留entry/请求/id/捕获闭包，再调用一次原ValueTask.AsTask、强持原Task与完成路径，观察用WaitAsync和有限ct，WaitAsync的wrapper绝不代替原Task。token只请求原业务取消；slotClosing时晚结果写根后丢弃发布/消费权，仍保管module/Bytes，不能靠weak reference/Task异常已观察当资源释放。root完成路径本身有Task条目，未完成即held。

CloseOrRetain进入finally第一步Closing=true，独立1s cleanup CTS；捕获所有cleanup异常到有界CleanupErrors（overflow计数保留第一条/最后一条）、绝不向外抛以覆盖business异常。已经获得module仅首次启动StopAsync(DrainRequest(stopId,1s),cleanupCt)并保留原Task；Stop卡住/抛错/DrainUnknown都逐原OperationId.GetOperationState核held，不能并发第二Stop。只有Stop真实返回ResourcesReleased、所有业务原Task/完成路径结束且无held，才首次登记DisposeAsync原Task；dispose失败/卡住都留根。不取得module时保留factoryTask，若其晚到，完成路径先持module并在**新独立有限恢复窗口**执行首次Stop/Dispose，原Host不重Create。

正常全部确认后清理Outputs、所有借用方作用域已结束，退槽释放root byte预约；同共享fixture端口须A/B都退槽后才能由fixtureOwner Dispose，不在A finally清空Store/Gate。pending时`OfferId=Guid固定rootId`的一次全量offer携带slot全部字段/任务/module/输入/Outputs/错误及reservation；本卡Receiver有2槽/8MiB、方法`TryAdopt`先在同进程锁内预留并强持slot再确认原OfferId及OwnerConfirmed，不能仅返回bool而未持有。receiver拒绝/throw/确认延迟超过1s时，原注册器保留槽并返回`Retained`；迟到确认仅在同锁下提交一次Owner切换，原槽不和receiver并发Dispose。`CloseOrRetain`结果只可为`Released/Retained/Transferred`，后两者不是ResourcesReleased。无接收者则root留进程registry可lookup；调用方法离栈不删root。callee归还后registry恢复执行同已登记Stop/Dispose及原id查询，不重发业务。正式Host恢复面板可投影同记录，不新增第二事实Owner。

故障fixture至少逐公开方法和factory/Stop/Dispose/Root.TryAdopt指定`ThrowBeforeTask/TaskPending/ReturnLate/DisposePending`四种可控闩锁，Entry保管源对象/原Task；factory前满槽调用0次、provider/Reserve迟到不发布候选、Store迟到仍原id回查、资格晚到不缓存、Export晚到不触发重建。每种断言同时核操作final/held、root状态、调用次数（原Stop/Dispose最多1）、Gate字节未提前归还、异常原栈与cleanup错误均存在。Mock所有权通过不代表真实构造或HALCON释放通过。

#### 7.4.7 断言、性能和六项切片核对

| 固定case | 必须可判定的结果 |
|---|---|
| CAL.JOINT.01 正常Core | 模拟fit 3组/check2组、每组>=6点，Profile显式meter/Radian限值、非零基线、两端不同宽高/pitch、实测Z修正；A Solve/Validate/Publish后未Qualified，B Unknown；mock外部决定后B Applicable，index0/1、frame和1000完全匹配；模拟只证明合同 |
| CAL.JOINT.02 栅格/方向 | 缺horizontal、数组顺序未经DirectionMapping证明、改manifest/decoder/mapping或runtime route不在批准列表、宽高不等/镜像/裁切/单方向；CAL-101/103/108/105按发生阶段，native或resolve成功次数0，无近似asset回退 |
| CAL.JOINT.03 采样 | §7.4.6A的黑心mask=0/白环双homography预测通过Synthetic误差界；缺四象限、窗口出界、非共面证据、留出误差/inner-outer shift/centre witness偏差超限拒识；一侧fit低误差也不外推。保留遮中心的独立native Golden门 |
| CAL.JOINT.04 身份/几何 | 重复点号、同组跨fit/check、点号错配、名义代实测、证书/平面度缺失、单位错、rotation非刚体；CAL-100/103/108，无候选。三组重复pose、共线、近零baseline、负depth、缺角/深度/域覆盖CAL-102/104，不以数量或低RMSE救回 |
| CAL.JOINT.05 独立检查 | 优化只fit、check仅camera初pose；fit低误差但projector留出/距离/平面/不确定度失败→ValidationFailed、Publish CAL-117；重建输出mm重复换算或pose求逆错误被不对称Golden捕获 |
| CAL.JOINT.06 内容/资格 | 篡改file bytes/params/Check证据、原id改Budget、二维Ref冒用/新id重复写、PublishUnknown晚成功→CAL-108/107/109或预检拒绝；只原发布id回查，新查询回读闭包。撤销/过期/曝光越期/水位unknown/域越界不Export；历史id不被新revision替换 |
| CAL.JOINT.07 所有权 | factory前满槽、构造/Reserve/provider/Read/OpenStream/Solve/Write/Qualification/watch迟到或忽略cancel；先强持原Task/晚到value，有限观察DrainPending，GetOperationState保持held；实际释放后才终态。输出晚到不重建；Stop/Dispose仅一次，transfer失败原根不退，late owner确认仅切换一次；原业务错误不被cleanup覆盖 |
| CAL.JOINT.08 双Host/native | A失败/停止/卸载不影响B已独立Bytes和租约；B read file roundtrip并绑定HybridVertical/HybridBoth实际reconstruction。真实fixture按固定非对称点/已知camera0_H_projector/实测板覆盖和曝光链验证，Mock/filehash/截图不冒充该结果 |

Benchmark复用 §15 Profile/分位统计：专门分桶camera+projector不同尺寸、fit/check组数/有效点比例、两层/mask/原图/导出byte大小、冷热/并发，测producer采样、预检/pose/共同solve/check/file roundtrip/store/qualification/export/接纳至真实释放和cancel至释放；记录托管/native峰值、root/task/stream/file/handle高水位及删失。预算是执行上限，非性能目标；两消费者目标未提供时NotEvaluated(TargetPending)，不影响纯Core规格/模拟断言，但不签发性能或物理资格。

| DEV-GOV-010 §3.1条件 | 本节准确落点/新增切片结论 |
|---|---|
| 1 边界/消费者 | §7.4.1/6：共同solve/asset Owner明确，structured-light producer及reconstruction-3d export消费者；桥待各Owner接收 |
| 2 唯一API/资源/错误 | §7.4.2–5：Joint专用refs/DTO/方法/有界budget/摘要/迟到ledger，沿v0.2不重复资格/设备权威 |
| 3 无UI Host | §7.4.6：两完整独立Host，从根预留→工厂→业务→Stop/Dispose/未确认全量保管；HALCON未装亦可模拟 |
| 4 可判定断言 | §7.4.7 CAL.JOINT.01–08，包含输入失败/正常/未知/并发/重复/取消/迟到/关闭/完整性，native Golden/独立计量单列 |
| 5 Benchmark | §7.4.7/§15固定测法、输入版本/分桶/资源/排空，目标Pending不自授结果 |
| 6 工程/调用/禁区 | 复用Core与BCL Exe，Core `Joint/`、测试 `Joint/` 与上述Consumers两个Host；适配器仍既定AsunImageAdapter/PersistenceAdapter，不新建重复DLL。构建/run命令见Core binding，测试入口必须执行原CAL.CORE.01–18及新CAL.JOINT.01–08、非零失败/跳过/timeout。CAL-JC仅Core/Test目录；CAL-JA/I未授权前不动adapter/消费者/产品/其它模块/源资料 |

2026-10-11 两轮有限规格自审按本轮窄修重新执行：①按正常/缺方向/白区环带hole/退化/姿态方向/独立holdout追踪可判定结果；②逐端口/两个Host根槽/工厂迟到/Store回查/资格水位/Export副本/Stop和Dispose实际退出走查。它们是规格自审，未运行C#或HALCON。`CAL-JC`已按六项文档规格由主控接收为`ModuleCoreImplementationReady`；`CAL-JA`的固定算子/求解/文件路线及`CAL-JI`的公开交接指导内容已限定接收，仍分别需要真实C#调用/native Golden/file roundtrip，以及两个原消费者映射、真实采集/独立计量Plan/范围值、资格/性能与现场结果，不以外部门阻无关二维Core。自审纠正了Gray阈值整数/原件字节形状、回查NotCommitted及独立Joint通知引用、调用前根捕获、Export峰值、标定both与运行vertical/both的独立兼容列表/资格证据。此句记录 Joint 窄修当时的范围；本轮其它手眼/专用方法的软件补充以 §7.3A 与 §17.3 为准，原真实验收门未提升。

## 8. 资产、持久化、资格与激活

候选与已发布资产使用不同身份。已发布内容按内容 hash 不可变，修正必须新建修订；验证报告、参考证书和资格决定作为不同引用保存。加载时校验完整依赖闭包、格式版本、内容 hash、字段单位和兼容范围。损坏、依赖缺失、未识别的必要字段和签名/摘要异常均 fail closed。

资产储存由 `ICalibrationArtifactStore` 负责，资格查询由只读 `ICalibrationQualificationPort` 负责，精确形状见 §9。Core 将完整候选内容与匹配验证证据提交 Store，不只给 Store 一个无法读取的候选 ID。内容及索引必须原子可回读；索引成功但内容失败、内容成功但索引失败均不可报告成功。原 OperationId 重放且请求摘要相同返回原回执；同 ID 不同候选/证据摘要返回 CAL-107，不覆盖旧内容。PublishUnknown 后唯一恢复入口为 QueryPublishReceiptAsync，Core 对 Found(Published) 再按引用回读 hash/依赖；回读损坏返回 CAL-108，不把错误改成新的发布事实。

资格至少绑定：PublishedUnqualified 资产 hash、方法修订、参考件修订、具体被测量/用途、设备/光学/传感配置、坐标与单位、有效域、环境和试验 Profile、独立验证证据、算法/库版本、决定者/来源及有效时间。资格不由一次低残差自动签发。解析要求逐项比对用途、配置和域，不得“最相近”回退；没有外部 `Qualified` 决定时只能返回 `Unknown` 或 `NotApplicable`，不能创建 `QualifiedAssetRef`。

激活若由宿主授权，提交必须携带资产 hash、scope、OperationId 和预期当前绑定修订；Owner 在同一权威事务中重核资格、权限、依赖和 CAS。并发冲突不覆盖，返回实际修订。运行开始固定资产闭包；新版本出现不改变在途引用，但资格撤销、设备配置变化或越域事实仍须向宿主发失效通知。模块只提供受影响 scope/原因，宿主按自己的流程执行隔离或复验。

## 9. 适配器契约

适配器接口必须可替换、可测且无产品含义：

- `ICalibrationSolver` / `ICalibrationSolverScopeFactory`：声明支持的方法/格式和底层版本；接收不可变规范输入；返回参数、残差、域和可诊断的失败；不持有持久化、资格或激活权。
- `IReferenceResolver`：以引用/修订读取参考几何与证据；验证来源完整性；不将 CAD 名义值改写为实测溯源值。
- `ICalibrationArtifactStore`：内容寻址读写、原子性、幂等键、修订 CAS、回执查询和依赖闭包校验；不得只写数据库行不存内容。
- `ICalibrationQualificationPort`：始终只读资格权威及水位/修订；不可达返回 `Unknown` 或错误，不返回最近缓存的 Qualified。
- `ICalibrationBindingPort`：不属于 Core v0.2；宿主若需要受控绑定，在 Resolve 得到 `QualifiedAssetRef` 后于模块外执行授权、事务 CAS 和幂等回执。Core 不自行维护第二份当前绑定。
- `ICalibrationDiagnostics`：结构化日志、指标和 trace sink；默认不记录图像内容、证书敏感数据或操作者隐私字段。

适配器能力在启动时以不可变 `AdapterCapabilities` 暴露；目标版本不兼容直接拒绝创建对应方法会话。没有装配持久化/资格端口时，纯离线 `Solve`/验证可以运行，但不得假报已发布或可用资格。

### 9.1 精确端口、工厂及查询形状

以下签名全部位于 Core 命名空间；Adapter 单向引用 Core。端口方法的返回意味着其自身任务/内部资源实际退出，Completion 字段取 ResourcesReleased（Core 再按全部 child ledger 决定调用方观察 Completion）；不得在资源未归还时返回一个成功 DTO。端口返回失败使用已定义 CalibrationError，异常由 Core 统一转成 CAL-113/诊断，不以 exception message 参与判定。

```csharp
public interface IReferenceResolver
{
    ValueTask<ReferenceGeometry> ReadGeometryAsync(ReferenceGeometryRef reference, OperationId operationId, CancellationToken token);
    ValueTask<CalibrationMethodProfile> ReadMethodProfileAsync(MethodProfileRef reference, OperationId operationId, CancellationToken token);
    ValueTask<ValidationPlan> ReadValidationPlanAsync(ValidationPlanRef reference, OperationId operationId, CancellationToken token);
}
public interface ICalibrationObservationProvider
{
    ValueTask<ICalibrationImageLease> OpenImageAsync(ContentRef reference, OperationId operationId, CancellationToken token);
}
public interface ICalibrationImageLease : IAsyncDisposable
{
    DecodedImageDescriptor Descriptor { get; }
    ValueTask CopyPlaneAsync(int plane, Memory<byte> destination, CancellationToken token);
}
public interface ICalibrationSolver : IAsyncDisposable
{
    AdapterCapabilities Capabilities { get; }
    ValueTask<SolverOutput> SolveAsync(PreparedCalibrationInput input,
        SolverParameterSet parameters, SolverExecutionContext execution,
        IProgress<CalibrationProgress>? progress, CancellationToken token);
    ValueTask<ValidationOutput> ValidateAsync(CalibrationArtifact candidate,
        ValidationPlan plan, IReadOnlyList<ObservationRef> observations,
        SolverExecutionContext execution, CancellationToken token);
}
public interface ICalibrationArtifactStore
{
    ValueTask<PublishReceipt> WritePublishedUnqualifiedAsync(CalibrationArtifact content,
        ValidationEvidenceRef evidence, ICalibrationContentWorkspace contentSource,
        OperationId operationId, CancellationToken token);
    ValueTask<CalibrationArtifact> ReadPublishedAsync(PublishedArtifactRef reference, OperationId operationId, CancellationToken token);
    ValueTask<ReceiptQueryResult> GetOperationReceiptAsync(ReceiptQueryRequest request, CancellationToken token);
}
public interface ICalibrationQualificationPort
{
    ValueTask<QualificationSnapshot> ResolveQualificationAsync(ResolveRequest request, CancellationToken token);
    IAsyncEnumerable<InvalidationNotice> WatchInvalidationsAsync(
        AuthorityWatermark? after, OperationId operationId, CancellationToken token);
}
public interface ICalibrationExecutionGate
{
    ValueTask<IAsyncDisposable> ReserveAsync(long peakBytes, OperationId operationId, CancellationToken token);
}
public interface ICalibrationDiagnostics
{
    void Record(CalibrationDiagnosticEntry entry);
}
```

| 类型 | 固定字段/行为 |
|---|---|
| `CalibrationAssetsOptions` | `(MaxQueuedOperations:int,MaxRetainedEvents:int,MaxResidentCandidateBytes:long,StopWaitLimit:TimeSpan,MaxRetainedOperations:int,MaxRecoveryOperations:int)`，正值；离线软件默认 `8/4096/268435456/30s/1024/8`，宿主可收紧，扩大须预算许可；候选字节与在途峰值合计受总预算约束 |
| `CalibrationAssetsAdapters` | `(SolverFactory:ICalibrationSolverScopeFactory?,ObservationProvider:ICalibrationObservationProvider?,References:IReferenceResolver,Store:ICalibrationArtifactStore?,Qualifications:ICalibrationQualificationPort?,ExecutionGate:ICalibrationExecutionGate,Diagnostics:ICalibrationDiagnostics,Clock:TimeProvider)`；Core/模拟宿主允许空 solver/provider，实际调用缺能力返回 CAL-101/113；StopWaitLimit 正且<=30 s，缺省用于宿主创建 DrainRequest，不隐含重置实际 Deadline；Clock 由宿主显式给 TimeProvider.System 或确定性测试时钟；不静态默认造真实依赖 |
| `AdapterCapabilities` | `(AdapterId:string,Revision:RevisionId,RuntimeVersion:string,Methods:IReadOnlySet<CalibrationMethodId>,CameraModels:IReadOnlySet<CameraModelId>,TargetKinds:IReadOnlySet<CalibrationTargetKind>,NativeCancellation:NativeCancellationCapability)`；capability=`NotSupported/BoundedStepOnly/VerifiedNativeInterrupt`，最后一项必须有该算子该调用映射证据 |
| `DecodedImageDescriptor` | `(Width:int,Height:int,PlaneCount:int,PixelType:ImagePixelType,BytesPerPlane:long,SourceDigest:Digest)`；本版只接 UInt8 单通道、行优先无 padding，BytesPerPlane=checked((long)Width*Height)，且不超过 int.MaxValue 与预算；CopyPlaneAsync 的 destination.Length 恰等 BytesPerPlane。实际分配前校验并预约，OOM 为 CAL-112 并归还预约，不默默截断；源多通道须先由独立批准转换形成新内容引用并保留原图，不能用未定义通道选择混入本联合 |
| `SolverExecutionContext` | `(OperationId:OperationId,Budget:CalibrationExecutionBudget)`；本次入口有效资源上限（§6.1 的逐项取小）/时限，由 Core 传入，不从 PrepareRequest.Budget 重建本次截止。child 的 operationId 必须匹配该上下文，未知 ID/关闭后新 IO 拒绝 CAL-114；已经在途的 child 仍受 ledger 监督 |
| `PreparedCalibrationInput` | `(OperationId:OperationId,Request:PrepareRequest,InputDigest:Digest,Geometry:ReferenceGeometry,Profile:CalibrationMethodProfile)`；消除输入/配置/引用/参数不一致后封存；Solve adapter 的 OperationId 来自本次 Solve，Request.OperationId 保留 Prepare 原 ID，不混为一作业 |
| `SolverOutput` | `(Status:SolveStatus,SolvedParameters:ContentRef?,Residuals:ResidualReport?,Domain:DomainReport?,Observations:IReadOnlyList<ObservationDiagnostic>,Resources:ResourceReport,Error:CalibrationError?)`；成功所需内容须被模块内容目录独立接收，adapter 不制造 CandidateArtifactRef；该引用只由 Core 生成；adapter Resources 仅为自己的测点，Core 聚合所有 child/lease 的释放时刻到公开结果，不采用 adapter 的早到 ReleasedAtUtc 伪造整个操作已释放 |
| `ValidationOutput` | `(Status:ValidationStatus,Evidence:ValidationEvidenceRef?,Findings:IReadOnlyList<ValidationFinding>,Error:CalibrationError?)`；Evidence 内容封存于模块内容目录，不借用已释放 lease |
| `CalibrationDiagnosticEntry` | `(OperationId:OperationId,Stage:CalibrationStage,MessageKey:string,Code:CalibrationErrorCode?,OccurredAtUtc:DateTimeOffset,Diagnostic:DiagnosticRef)`；sink 抛错不能反转发布事实，记录至 Core 有界故障计数并隔离 sink，无图像/隐私载荷 |
| `EventReadRequest` / `EventReadResult` | request=`(OperationId:OperationId,AfterSequence:long,MaxCount:int)`；result=`(Status:EventReadStatus,Events:IReadOnlyList<CalibrationEvent>,LastSequence:long)`；status=`Available/Gap/UnknownOperation`，MaxCount 1..256；同步内存读取，不启动 IO。由模块公开 `EventReadResult ReadEvents(EventReadRequest request)` |

本版 solver 通过注入 provider/reference 和模块创建的有界 `ICalibrationContentWorkspace` 产生/打开内容，不持有产品 Store。接口签名如下；只有工厂创建并拥有目录，禁止跨实例共享可变目录。WriteAsync 将输入按 byteLimit 有界读入、计算摘要并封存，超限或格式无效拒绝，不执行输入路径；OpenReadAsync 核摘要后打开只读流，读取者 Dispose。Factory 和其依赖由宿主拥有，scope 和私有目录由模块拥有；scope 每实例一个，native 上下文每作业独占。Adapter 不得返回未写入目录的 ContentRef，不得以本地路径冒充内容引用。

```csharp
public interface ICalibrationContentWorkspace
{
    ValueTask<ContentRef> WriteAsync(string format, RevisionId revision,
        Stream source, long byteLimit, OperationId operationId, CancellationToken token);
    ValueTask<Stream> OpenReadAsync(ContentRef reference, OperationId operationId, CancellationToken token);
}
public interface ICalibrationSolverScopeFactory
{
    AdapterCapabilities Capabilities { get; }
    ICalibrationSolver CreateScope(ICalibrationContentWorkspace workspace,
        ICalibrationObservationProvider provider, IReferenceResolver references);
}
```

`ICalibrationSolver` 继承 IAsyncDisposable；DisposeAsync 释放本 scope 持有资源，不释放借用 provider/reference。缺 provider 或 solver factory 时 Create 不创建 scope，仍允许只读 Resolve/回查与纯值预检；Solve 直接 CAL-101，不调用空依赖。CreateScope 只建本地软件上下文，不采集、不连接设备、不打开图像。Store 的 WritePublishedUnqualifiedAsync 另接收只读 `ICalibrationContentWorkspace contentSource`，在返回 Published 前将全部依赖复制到它自己持有的持久内容域；ReadPublishedAsync 读取资产和校验全部闭包，无悬空借用引用。Validate 成功证据在目录中由摘要可读，Store 也复制该内容；不能只持有 EvidenceRef 却没有证据字节。

资格通知由 Core 持有可取消订阅，映射到宿主只读 `IAsyncEnumerable<InvalidationNotice> WatchInvalidationsAsync(InvalidationWatchRequest request, CancellationToken token)`；Core 不补造资格决定。水位 epoch 改变、断线或接续缺口使所有受影响在途投影失效并通知 AuthorityDisconnected；不能用订阅健康替代本次 Resolve 权威查询。Resolve 禁用 Qualified 缓存，每次读取完整当前决定和 ValidUntilUtc，未知/失联为 CAL-106；撤销/过期为 NotApplicable。应用开始固定资产闭包，但运行中收到撤销通知仍由宿主重新解析并处置；本模块不声称一次 Resolve 消除了与设备操作的竞争，宿主需在自己的实际提交事务中重核资格水位。

### 9.2 相机方法 Profile 的封闭输入

`CalibrationMethodProfile(Reference:MethodProfileRef,SensorMode:SensorMode,CameraModel:CameraModelId,TargetKind:CalibrationTargetKind,Detection:TargetDetectionProfile,SensitiveFields:IReadOnlySet<DeviceField>,RequiredDomain:OperatingDomain,MinFitGroups:int,MinValidationGroups:int,MaxIdentityMappings:int,MaxTopologyCandidates:int,MaxCandidateContours:int,PoseOrthogonalityTolerance:double,QualityPlan:ValidationPlanRef)`；数量/容差正且有限，来源必须有修订。不把官方理论最小点数当作资格采样下限。DeviceField 封闭列举为 `DeviceIdentity/OpticalIdentity/CameraModel/ReadoutLayout/Roi/Binning/Lens/Focus/Magnification/Mounting/WorkingDistance/Exposure/Gain/Temperature/Illumination/LineScanTiming`；至少包含 §7.2 的几何敏感项，资格域字段只能在证据完整时声明可变。

TargetDetectionProfile 是下列受限联合：

- `HalconDotDetection(Alpha:double,StartThreshold:double,MinimumThreshold:double,ThresholdStep:double,MaximumMarkDiameter:double)`：映射矩形 finder 路线对应 `alpha/start_thresh/min_thresh/delta_thresh/max_diam_marks`，范围按 find_calib_object 26.05；不混入其它板的 sigma 参数。阈值递减是在 Profile 预声明的算子内搜索，不是失败后模块扩大搜索。
- `CircleDetection(ThresholdLow:double,ThresholdHigh:double,Foreground:ForegroundPolarity,MinimumArea:double,MaximumArea:double,EdgeAlpha:double,EdgeLow:double,EdgeHigh:double,MaximumClosureDistance:Pixel,MinimumAxisRatio:double,MaximumFitResidual:Pixel,CenterPolicy:CircleCenterPolicy,MaximumCenterBias:Pixel,KnownCamera:QualifiedAssetRef?,PoseEvidence:ContentRef?)`：ForegroundPolarity=`Dark/Light`，CenterPolicy=`QualifiedNearNormal/QualifiedKnownCameraCirclePose`；后者要求 KnownCamera 非空且当前 Resolve=Applicable，独立板面 PoseEvidence 非空；前者 KnownCamera 可空但独立近法向偏差证据必填；主线固定 threshold→connection→select_shape→edges_sub_pix→fit_ellipse_contour_xld，单独完整轮廓，一阶边缘偏差必须计入实测预算；illumination 缓变的 dyn_threshold 是后续新 Profile 而非当前联合的隐含分支。椭圆拟合固定 `geotukey`，MaxNumPoints=-1、ClippingEndPoints=0、ClippingFactor=3 固定为本路线的设计基线；MaxClosureDist 来自 MaximumClosureDistance。Iterations/VossTabSize 是该调用位置所需的占位入参（分别 1/200），geotukey 不使用二者，不能把它们公开成有效调参或停止预算。固定 edges_sub_pix 的 canny，Alpha/Low/High 全取上述字段，保留剔除轮廓和 robust 权重证据，不以稳健拟合隐藏缺损/过曝。全部常数为软件路线定义，质量界仍由实测 Profile 验证。
- `ChessboardDetection(Sigma:double,HessianThreshold:double,ChannelIndex:int,HaloPixels:int,MaximumSubpixelError:Pixel,IdentityEvidence:ContentRef)`：固定 saddle_points_sub_pix 的 gauss 路线，Sigma/Threshold 非负；通道、crop+halo 和响应/拓扑界先固定，禁止尝试 facet 直到凑成功。原点/方向证据独立于鞍点响应强度。

Profile 与参数建议只离线进行，唯一封闭请求/结果、候选边界与确定评分见 §9.2A；参数候选上限与检测内部 MaxTopologyCandidates 分开。建议按独立工程调参集的完整身份/拒识/定位误差排序，不用 ValidationSet 或一次时延选参。路线正确性/误接受拒绝/P50/P95/P99/资源仍用相同代表集实测；目前无该实测结果。

#### 9.2.1 圆点/棋盘身份与拓扑可执行闭环

IdentityEvidence不是点号随意注释。其规范内容 `TargetIdentityEvidenceV1(Target:ReferenceGeometryRef,ImageDigest:Digest,VisiblePointIds:IReadOnlyList<ReferencePointId>,Windows:IReadOnlyList<TargetPointWindow>,MappingAuthority:ContentRef,NearNormalEvidence:ContentRef?,CentreBiasBound:Pixel?)`，window=`(PointId:ReferencePointId,RowMinimum:Pixel,RowMaximum:Pixel,ColumnMinimum:Pixel,ColumnMaximum:Pixel)`，一一对应稳定ID，有限有序且在原始栅格内。头 `calibration-target-identity-v1`、根同类型、按§3.7字段顺序，上限1MiB/每观测MaxPoints；VisiblePointIds原顺序和窗口同序，不重排求解点表。MappingAuthority是独立可核的靶边界/非对称点/同步可信pose投影身份依据，明确当前靶原点、方向和手性；窗口是该依据给出的保守pixel支持范围，不能由本检测点先配ID再填窗口循环自证。纯无框周期靶若任何独立来源不能排除另一置换，必须拒绝，不要求客户“给一个映射”来掩盖物理不可观测。

冻结匹配流程：检测所有有限候选、按(row,column,原始候选索引)排序仅作枚举顺序 → 由每个候选落入哪些PointWindow建立二部相容边 → 以VisiblePointIds原顺序深度优先枚举一对一映射（不选最近，不按row/col决定ID） → 对每个映射核目标拓扑/棋盘交替极性与邻接、规定边界和MappingAuthority → 完整枚举恰一有效映射才输出；零解CAL-103、多解CAL-103，枚举达到Profile.MaxIdentityMappings/MaxTopologyCandidates且仍存在未检查分支CAL-112，不能截断自称唯一。输入点/轮廓数先受MaxCandidateContours/MaxPoints约束，所有扩展节点（包括最终被拒节点）计MaxTopologyCandidates，避免指数路径绕过预算。邻接按靶点整数行列拓扑及window重叠关系确定，图像中不越过未声明遮挡去拼接缺行；本版Chessboard输出恰InnerCornersX*InnerCornersY全部角点，Circle为Evidence声明可见且满足覆盖的点集，不无声删点。

圆点的QualifiedNearNormal必须有NearNormalEvidence和非负CentreBiasBound<=CircleDetection.MaximumCenterBias，其独立姿态域/当前Device/Target/Image证据匹配；KnownCameraCirclePose按既定合格内参/两解独立选择路线，不将该窗口当已解内参。棋盘每组Observation.IdentityEvidence读取上述内容，Detection.IdentityEvidence是该方法身份依据模板的精确引用；模板/当前组关联证据不一致拒绝。CodeToTargetFrameEvidence可作为MappingAuthority的一部分，但barcode文本本身不是pixel窗口/点真值。人工输入窗口/标记保留操作者和来源，只是候选输入；物理计量仍需独立Validate。

软件例：2×2点ID P00/P01/P10/P11，四窗口分别[9,11]×[9,11]、[9,11]×[19,21]、[19,21]×[9,11]、[19,21]×[19,21]pixel，独立非对称边界证明方向；候选(10,10),(10,20),(20,10),(20,20)只有一映射。若窗口/Authority同样允许所有180°置换，必须两解拒绝；若(10,20)和(10.2,20)都完整满足P01窗口且无法质量拒其中一个，仍两解拒绝。这些只核枚举/身份，不证明近法向偏差或真实鞍点/圆心精度。该内容增量只解释已有IdentityEvidence字段，不改v0.2 DTO/摘要；目标身份真值/窗口依据由参考件/采集Owner提供，软件枚举与拒识不转交外部Owner设计。

### 9.2A 离线自动参数建议（Recommendation API 1）

本增量位于 `Asun.Modules.CalibrationAssets.Recommendation`，不向 v0.2 的 SolverParameterSet、请求、摘要或状态联合添加字段。真实消费者为相机校正工具及离线计量工具的工程调参流程；二者使用同一无 UI 服务。建议不是已批准参数、标定资产或资格。禁止修改传入 Profile、生产配置、靶标身份、参考真值、fit/check 分区、内参模型或物理验收值。Joint 和 §7.3A 专用方法只接受显式修订，不被此服务自动搜索。

| 类型 | 完整字段与有效域 |
|---|---|
| `RecommendationCase` | `(Id:string,PhysicalGroup:string,Image:ContentRef,Expected:RecommendationExpectation,Truth:IReadOnlyList<ObservedPoint>,IdentityEvidence:ContentRef)`；expectation=`Accept/Reject`，Reject 的 Truth 为空，Accept 必须有独立标注点号/原始 pixel 真值，不能以同一检测器输出自标注；图/组唯一 |
| `RecommendationChoice` | `(Id:string,Profile:CalibrationMethodProfile,Parameters:SolverParameterSet)`；完整不可变候选，不是自由参数字典；方法/靶/模型/敏感字段/域/采样下限/质量界与基线精确一致，只允许 Detection 数值、以及同模型已批准可估参数的初值变化。固定算子、CenterPolicy、KnownCamera/身份和近法向证据不可搜索；每个候选用其独立修订/摘要 |
| `RecommendationRequest` | `(Revision:string,OperationId:OperationId,Budget:CalibrationExecutionBudget,Baseline:RecommendationChoice,Candidates:IReadOnlyList<RecommendationChoice>,Cases:IReadOnlyList<RecommendationCase>,ReservedValidationGroups:IReadOnlySet<string>,MaximumLocalizationError:Pixel,MinAcceptedCases:int,MaxCandidates:int)`；revision=`1`，Candidates 非空、按宿主冻结顺序、不含重复 ID/hash；1<=count<=MaxCandidates<=64，Cases<=MaxImages，所有 points<=MaxPoints；误差上限非负、最小接受数正；物理组不得与 ReservedValidationGroups 相交；允许值表由宿主给出，不生成笛卡尔无限域，不用随机种子/运行时随机搜索 |
| `RecommendationTrial` | `(ChoiceId:string,FalseAccepts:int,FalseRejects:int,AcceptedCases:int,MaximumLocalizationError:Pixel?,CaseFindings:IReadOnlyList<ObservationRejection>,Resources:ResourceReport,Eligible:bool)`；错拒以应接受而未完整正确关联点号计算，错受含应拒而被接受、错误 ID/镜像映射；定位误差为各真值点 row/col 欧氏距离的最大值；任何缺真值、点号缺失、多解、未知统计均不 Eligible |
| `RecommendationValue` | `(Status:RecommendationStatus,Selected:RecommendationChoice?,Trials:IReadOnlyList<RecommendationTrial>,SourceDigest:Digest,RequiresEngineeringConfirmation:bool)`；status=`Suggested/NoSuggestion`，Suggested 才 Selected 非空；确认字段恒 true。取消/预算/端口异常不是 NoSuggestion 成功结果 |
| `RecommendationReply` | `(OperationId:OperationId,Completion:OperationCompletion,Value:RecommendationValue?,Error:CalibrationError?,Diagnostic:DiagnosticRef)`；DrainPending/失败时 Value=null，不能输出“到目前最优” |
| `RecommendationDetection` | `(Accepted:bool,Points:IReadOnlyList<ObservedPoint>,Findings:IReadOnlyList<ObservationRejection>,Resources:ResourceReport)`；Accepted 要完整唯一身份，拒识保留原因；在实任务/租约结束后返回 |
| `RecommendationState` | `(OperationId:OperationId,Status:OperationExecutionStatus,HeldResources:IReadOnlyList<string>,Final:RecommendationReply?,Error:CalibrationError?,Diagnostic:DiagnosticRef)`；Final 仅 Released 有值 |
| `RecommendationAdapters` | `(Evaluator:IRecommendationEvaluator,ExecutionGate:ICalibrationExecutionGate,Diagnostics:ICalibrationDiagnostics,Clock:TimeProvider)`；借用至真实排空，不被服务 Dispose |

封闭的 CalibrationMethodProfile 数据限定 ChannelIndex=0（当前单通道UInt8）且 HaloPixels>=ceil(3*Sigma)；不在建议中搜索通道/布局。

公开入口：`ICalibrationRecommendationService : IAsyncDisposable` 提供 `ValueTask<RecommendationReply> RecommendAsync(RecommendationRequest request,CancellationToken token)`、`RecommendationState GetOperationState(OperationId id)`、`ValueTask<DrainResult> StopAsync(DrainRequest request,CancellationToken token)`。唯一工厂 `CalibrationRecommendationService.Create(CalibrationAssetsOptions options,RecommendationAdapters adapters)` 只创建有界账本。`IRecommendationEvaluator.EvaluateAsync(RecommendationChoice choice,RecommendationObservation sample,SolverExecutionContext execution,CancellationToken token):ValueTask<RecommendationDetection>` 是唯一定向端口；真实实现复用 §9.4 同一检测器，不另造算法，模拟实现只供协议测试。服务仅把 `RecommendationObservation(Id:string,PhysicalGroup:string,Image:ContentRef,IdentityEvidence:ContentRef)` 传给端口，不传 Expected/Truth；评分留在Core，避免真值引导检测。

固定流程：预检并核全部内容引用 → 预约本次工作区峰值 → 先基线再逐候选、每候选按 Cases 原顺序串行评估 → 核身份/真值和逐例拒识 → 只有 falseAccepts=0、falseRejects=0、AcceptedCases>=MinAcceptedCases、最大定位误差<=声明上限，且所有统计/退出可确认才 Eligible → 对 Eligible 按 `(最大定位误差,原候选顺序索引)` 字典序取一个 → 返回完整证据和新候选修订；基线仅作对照，不加入 Selected 集合。时延/峰值逐例记录，但不参与确定性排序，避免调度噪声改变建议。真实路线性能比较仍用 §15 的重复 BenchmarkProfile，不把一次 trial 当 P99。MaxCandidates 是参数组合上限，MaxTopologyCandidates 是检测器内部拓扑上限，二者不能混用。候选级拒识计入 trial；完整端口故障、取消或总截止失败立即停止，等真实排空后无建议返回。全部候选不 Eligible 为 NoSuggestion，原参数不变。

摘要头 `calibration-recommendation-v1`，请求根 RecommendationRequest 按表字段顺序省顶层 OperationId，其余包括 Budget 全编码；SourceDigest 为同头、根 RecommendationSources、字段 `(Baseline,Candidates,Cases,ReservedValidationGroups,MaximumLocalizationError,MinAcceptedCases,MaxCandidates)`。使用 §3.7 原语，候选 ParametersDigest 仍按原 v0.2 投影核验，不重定义它。最多 1 MiB 规范请求元数据/单内容其原上限，图像与 native 驻留另计。推荐过期规则：源图/标注/设备/靶标/方法/参数/证据任何 hash 变化均不得确认旧建议；宿主确认时重新核 SourceDigest，再建立新方法/参数修订和新标定 session，使用未参与建议的 ValidationSet。没有自动 Apply/Publish 方法。

CAL.AUTO.01：基线与两个候选均无错受错拒、最大误差分别为 0.4/0.2/0.2 pixel，最小接受数=1、界=0.3；选择第一个 0.2 候选，时延交换不改变选择。02：第一候选在一个 Reject 样本错误接受，即使零定位误差也不能入选；全部失败 NoSuggestion。03：同 PhysicalGroup 出现在保留验证集，native 次数=0/CAL-100。04：候选更改中心政策/模型/参考 hash 拒绝；源修订改变后旧建议不可确认。05：中途取消/迟到 Evaluator/Stop/重复 ID 按 §6.1 原任务账本，Pending 无 Selected，释放完成才能重跑；不同实例不相互取消。以上为固定软件断言，真实标注、拒识、准确率和性能未运行。

### 9.3 已解相机参数公开读取增量（Camera Read API 1）

本节专门闭合 mosaic v0.4 C.8 的源数据缺口：从精确二维 `PublishedArtifactRef` 和 `CalibrationArtifact.SolvedParameters` 读出**实际解出的**参数。`InitialParameters`仍只用于求解初值，不得作此结果；JointRef/camera_setup不是此接口的输入。新服务/format独立为 `Camera Read API 1`，namespace `Asun.Modules.CalibrationAssets.CameraRead`；不修改Module API Contract v0.2的请求、接口、结果union、四种摘要投影及已接收CAL-C1/C2/C3。`CAL-CR`已按六项文档规格由主控接收为`ModuleCoreImplementationReady`；真实format writer、耐久ContentSource、Qualification和mosaic接线仍是后续门，不借旧Core接收自动准入。

#### 9.3.1 固定格式与纯值codec

`CameraSolutionV1(Parameters:CameraParameterVector,CalibrationDeviceDigest:Digest,Method:CalibrationMethodId,ParameterRevision:RevisionId,ProducerId:string,ProducerRevision:RevisionId,RuntimeVersion:string)` 是已解内容唯一形状。format=`calibration-solved-camera`、FormatRevision=`1`，字节头ASCII `calibration-solved-camera-v1`（无长度/BOM/终止符），根名`CameraSolutionV1`，后按签名用 §3.7 primitive/record/list/enum规则编码；Parameters中的Model是完整原HALCON模型名（例如line_scan_division），参数保持 §7.2C 该模型的严格顺序/单位，不改成消费者自己命名的11个数。CalibrationDeviceDigest按 §3.7 v0.2头、根DeviceConfigurationSnapshot和全部字段计算，必须等资产真实Device摘要；不纳Candidate/Published自身身份。原bytes的SHA-256=ContentRef.Digest，最大65536bytes且>0；每模型参数数量依 §7.2C（division面阵8、line division11等）且<=32，字符串每项<=256 UTF8bytes，record根/format/单位/Model/顺序/count全部精确，未知必要字段/尾随字节/非有限/溢出CAL-108（未知format/version CAL-101），不反射/JSON/猜模型。

`CameraSolutionCodec.Encode(CameraSolutionV1 value):byte[]`，`CameraSolutionCodec.Decode(ReadOnlySpan<byte> bytes):CameraSolutionV1`，`CameraSolutionCodec.ComputeDeviceDigest(DeviceConfigurationSnapshot device):Digest`是公开、有界、无IO的静态函数，Encode/Decode前检查上述限额。Decode保留实际Parameters数值、原模型名和原单位；长宽必须为正整数pixel、Focus/Sx/Sy/倍率合法、线扫Vy按方法正、telecentric线扫Vz固定0、rotation/motion不跨模型猜分量。Decode只证明内容格式，不签资格；不返回native tuple/handle、任意路径或delegate。参数求解writer在获准CAL-A1/A3等适配切片中输出此format并写workspace，原v0.2 SolvedParameters字段保持ContentRef且Candidate摘要仍包含它；未知旧content format只拒绝本读取，不迁移/重算旧资产身份，不让Core把initial写成新版solved。

#### 9.3.2 公开服务、内容端口与工厂

| 增量类型 | 完整字段/意义 |
|---|---|
| `CameraReadRequest` | `(ReadRevision:string,Asset:PublishedArtifactRef,ExpectedSolvedParameters:ContentRef,Use:IntendedUse,ActualDevice:DeviceConfigurationSnapshot,ActualDomain:OperatingDomain,ExposureFrom:DateTimeOffset,ExposureTo:DateTimeOffset,Budget:CalibrationExecutionBudget,OperationId:OperationId)`；ReadRevision="1"、曝光闭区间有序；ExpectedSolvedParameters须精确等Store回读的asset.SolvedParameters，不让caller替换另一个向量；mosaic Use=IntendedUse("LineScanRow0Projection",RevisionId("1"))，其它已批准明确用途可读取，但不同Use不共享资格 |
| `CameraParametersSnapshot` | `(Asset:PublishedArtifactRef,SolvedParameters:ContentRef,Solution:CameraSolutionV1,CalibrationDevice:DeviceConfigurationSnapshot,Qualified:QualifiedAssetRef,Watermark:AuthorityWatermark,ApprovedDomain:OperatingDomain,ObservedAtUtc:DateTimeOffset)`；CalibrationDevice取资产真实快照，不是request冒充；Solution.Parameters是已解向量，内容hash/完整引用可复核，Qualified/Watermark是本次权威查询，无native对象 |
| `CameraReadReply` | `(OperationId:OperationId,Completion:OperationCompletion,Status:ApplicabilityStatus,Snapshot:CameraParametersSnapshot?,Findings:IReadOnlyList<ApplicabilityFinding>,Error:CalibrationError?,Diagnostic:DiagnosticRef)`；仅Released/Applicable/无Error时Snapshot非空，其余null；真实失联Unknown/CAL-106，篡改/format拒绝无成功快照 |
| `CameraReadOperationState` | `(OperationId:OperationId,Status:OperationExecutionStatus,HeldResources:IReadOnlyList<string>,Final:CameraReadReply?,Error:CalibrationError?,Diagnostic:DiagnosticRef)`；仅ResourcesReleased有Final，其它空；Stop无Final |
| `CameraReadAdapters` | `(Store:ICalibrationArtifactStore,Content:ICalibrationSolvedContentSource,Qualifications:ICalibrationQualificationPort,ExecutionGate:ICalibrationExecutionGate,Diagnostics:ICalibrationDiagnostics,Clock:TimeProvider)`；全部显式非空，借用端口，调用方持有至Reader所有原Task释放；不调用solverFactory/provider/AsunImage |

```csharp
public interface ICameraParametersReader : IAsyncDisposable
{
    ValueTask<CameraReadReply> ReadAsync(CameraReadRequest request, CancellationToken token);
    CameraReadOperationState GetOperationState(OperationId operationId);
    ValueTask<DrainResult> StopAsync(DrainRequest request, CancellationToken token);
}
public interface ICalibrationSolvedContentSource
{
    ValueTask<Stream> OpenReadAsync(PublishedArtifactRef asset, ContentRef exactSolvedParameters,
        SolverExecutionContext execution, CancellationToken token);
}
// CameraParametersReader.Create(CalibrationAssetsOptions options, CameraReadAdapters adapters)
// 是唯一构造：只本地创建有限ledger/能力，不启动IO/native/连接，不改变原CalibrationAssetsModule.Create。
```

ContentSource实现只从此精确已发布asset的SolvedParameters闭包以hash打开只读Stream，非此asset的ContentRef/未发布candidate/Joints均拒绝；不存在任意路径/string的重载。Store.ReadPublishedAsync原v0.2签名不变，由增量reader代理加入操作ledger/执行预算；它返回前检查资产内容hash/闭包。ContentSource.OpenReadAsync返回Stream只表示交付，唯一Dispose责任移到reader ledger；迟到stream在Closing状态先接收再Dispose，不交caller；Stream读取/复制原Task/缓冲/预约均持有至真实完成。reader不释放借用Store/Content/Qualifications/Gate；不会因为请求WaitLimit到期清理仍在读取的Stream。

#### 9.3.3 唯一读取链与适用性

1. 预检revision、单位/Device.Domain、Time/ExpectedRef格式/长度（1..65536和本次MaxImageBytes/ResidentBudget）、依赖可用与精确Asset；重复OperationId同完整RequestDigest回原结果、不重IO，改变Budget/Use/曝光/ExpectedRef CAL-107。增量摘要头`calibration-camera-read-request-v1`、根`CameraReadRequest`，按签名省顶层OperationId，包含其余全部字段，不修改v0.2 RequestDigest根表。UTC只用于权威/曝光区间；执行/等待沿 §6.1 内部单调截止和child ledger。
2. 预约artifact/streambuffer/decodedSnapshot峰值后Store回读完整asset，核identity/hash/闭包及exactSolvedRef/format；返回的内容/引用不匹配CAL-108。从source精确打开stream，最多65536bytes，实际必须等ByteLength且EOF，hash核原字节，Decode检查Model/顺序/单位/finite，与artifact.Device.CameraModel/CalibrationDeviceDigest/Method和ParameterRevision逐项匹配（ParameterRevision=artifact.Parameters.ParameterRevision）；不能用asset.Parameters.InitialParameters补字段。结果Producer和asset.Adapter.AdapterId/Revision/RuntimeVersion也一致；格式不支持时CAL-101，无参数快照。
3. 用同原操作Id/剩余budget组成既有`ResolveRequest("0.2",Asset,Use,ActualDevice,ActualDomain,Budget,OperationId)`给只读Qualifications.ResolveQualificationAsync；这是内部一次查询，不能在原module另接纳同ID/制造第二个幂等执行。Qualified条件沿 §8/§9.1：ApprovedDevice/Domain/Evidence/Qualification及Watermark完整、Source等本Asset、Use精确匹配，current Clock在watermark观察/有效区间，ExposureFrom>=QualifiedAtUtc且ExposureTo<=ValidUntilUtc（若无上限不能伪造过去validFrom），资格Unknown/断联/epoch/过期权威Unknown，撤销/Suspended/Expired/配置域不符NotApplicable。actual配置的geometry敏感项按 §7.2C/asset方法Profile，当前readout/模型/尺寸/ROI/binning/镜头/焦距/倍率/安装/曝光/增益必须匹配；未知必需字段Unknown、显式不等NotApplicable。LineScanRow0Projection只授权读已解光学/静态首行参数，完整扫描速度/同步/运动/工作区资格仍属mosaic和运动Owner，不能从本快照推导整幅线扫物理合格。
4. 读/资格全部原Task真实结束、stream已Dispose/预约归还后，Snapshot给独立不可变DTO（防御复制参数list）；ObservedAtUtc=本次readerClock，不把外部缓存时间冒充。所有不Applicable结果无Snapshot。外部资格晚到丢弃，再读必须新operation/query；一次read与后续设备执行之间仍由mosaic实际提交重核水位。Stop先取消接纳/发取消、有限等待<=30s，不改变真实released；未知保留本reader ledger，并按原OperationId查询。Dispose可未完成且仅Host根确认后退槽，不泄漏native/路径。

消费者mosaic显式桥：Snapshot.Solution.Parameters.Model="line_scan_division"、按精确顺序/原单位取Focus/Kappa/Sx/Sy/Cx/Cy/ImageWidth/ImageHeight/Vx/Vy/Vz，填其LineDivisionParameters；pixel width/height核整数后转换，平移/运动仍meter/meter-per-row，禁止把Vx/Vy/Vz当m/s。Reference、SolvedParameters.Digest、CalibrationDevice、Qualified及Watermark原值传其受控快照；其它line polynomial/telecentric只在mosaic自身方法已批准时按同名vector字段映射，不把本模块全模型支持当consumer已实现。真实只读Store/ContentSource/Qualification bridge由两Owner接收，不改mosaic正文或共享合同。

#### 9.3.4 独立仿真断言、双消费与真实门

固定无native软件夹具复用 §7.4.6A 的C(label)/Put/D/R/M/T/clock，但只以二维v0.2引用装配，绝不用JointPublishedRef。line device=`DeviceConfigurationSnapshot("syn-line","syn-line-optic",LineScan,CameraModelId("line_scan_division"),R("1"),"syn-line-lens","fixed","perspective","line-camera0",D(UTF8("SYNTHETIC|line-native|v1")),64,2,0,0,64,2,1,1,1000,0,M(.25),T(20),"syn-line-light")`。solved vector按 §7.2C 固定11项：Focus=.010m、Kappa=0m^-2、Sx=Sy=.00001m、Cx=32px、Cy=0px、Width64/Height2px、Vx=0/Vy=.00002/Vz=0meter/row；Initial vector只Focus=.009且Vy=.000018，其余同。solution=`CameraSolutionV1(solved,CameraSolutionCodec.ComputeDeviceDigest(lineDevice),CalibrationMethodId("LineScanCamera"),R("1"),"synthetic-line-solver",R("1"),"Synthetic/1")`，Encode/Put(format="calibration-solved-camera",version1)产生exactSolvedRef。

本读取夹具固定直接装配一个**Synthetic只读Store**的完整值，不需要先实现/启动Joint或真实持久化，也不伪造生产Publish回执。构造公开纯值校验增量 `CameraSolutionCodec.ComputePreparedDigest(PrepareRequest request)`、`ComputeParametersDigest(SolverParameterSet parameters)`、`ComputeArtifactDigest(CalibrationArtifact artifact)` 沿 §3.7 原v0.2精确投影/原头，只公开调用既有编码器的只读校验，不改任何旧投影；各自受64KiB（小值）/1MiB（artifact/prepare）上限。临时envelope/Digest只在计算前合法局部构造，最终fixture请求和Mock Store均换成重算digest，读时再核，不能把这些校验helper改成发布写入接口。

| 完整二维Synthetic artifact/端口 | 构造规则 |
|---|---|
| frame/domain | lineFrame=Frame("line-camera0")；domain=`OperatingDomain(lineFrame,[DomainBound(ImageRow,Pixel,0,1),DomainBound(ImageColumn,Pixel,0,63),DomainBound(WorkingDistance,Meter,.25,.25),DomainBound(ObjectZ,Meter,0,0),DomainBound(Temperature,Celsius,20,20),DomainBound(Exposure,Microsecond,1000,1000),DomainBound(Gain,Decibel,0,0),DomainBound(ScanSpeed,MeterPerSecond,.02,.02)],C("line-domain"))`；各Bound.Quantity/Unit用 §3.6 enum，域是软件fixture明确值，不声明现场模型有效 |
| pose/line evidence | pose=`RigidPose(objFrame,lineFrame,Point(0,0,.25),identity9,C("line-first-pose"))`；每图 `LineScanEvidence(C("timing-L"+i),C("encoder-L"+i),"syn-line-clock",lineFrame,Point(0,.00002,0),pose,true,C("constant-L"+i),C("rows-L"+i))`，i0/1/2分别LF0/LF1/LC0；没有传m/s代替meter/row |
| Observations | 每图Image=64×2 byte，byte[k]=k，byte0再置i以区别（i=0..2）；Put(format="image-gray8-rowmajor")。ObservationRef(Id(group),Image,ComputeDeviceDigest(lineDevice),group,i,t0+i ms,PixelCoordinateLayout(64,2,0,0,2,64,1,1,Native,R("1")),[ObservedPoint(P0,Row0,Col8,D(C("p0-"+group))),P1/0/32、P2/0/56同形],pose,上述lineEvidence,C("identity-"+group),C("quality-"+group).Digest)；D(C(...))等价该ContentRef.Digest，不再次hashHex字符串 |
| Method/Parameters | methodRef=`MethodProfileRef(CalibrationMethodId("LineScanCamera"),R("1"),C("line-method-definition").Digest)`；initial已在上一段确定，parameters=`LineScanCameraSolverParameters(R("1"),tempDigest,CameraModelId("line_scan_division"),initial,new HashSet<string>(StringComparer.Ordinal){"focus"},methodRef)`，tempDigest=C("parameters-build").Digest；后以ComputeParametersDigest换ParametersDigest。fixture表示估计focus且已解Vy有不同值以**只读来源挑战**验证不取initial（其非focus改变不能冒称真实本方法solver已通过，真实writer另按实际估计项验证） |
| Prepared/candidate内容 | PrepareRequest("0.2",CalibrationSessionId(Id(201).Value),methodRef,上述syn-boardTarget,syn-boardGeometry.Reference,lineDevice,[LF0,LF1,LC0],PartitionPlan(R("1"),{LF0,LF1},{LC0}),Budget(2s,3s,8,65536,128,1048576,1),Id(202))，InputDigest=ComputePreparedDigest(prepare)。FitResiduals=`ResidualReport([ResidualGroup("LF0",PixelReprojection,Pixel,3,0,0,C("errors-LF0")),LF1同形],C("fit-evidence"))`，DomainReport(domain,Array.Empty<string>(),C("domain-coverage"))；Adapter=`AdapterCapabilities("synthetic-line-solver",R("1"),"Synthetic/1",{CalibrationMethodId("LineScanCamera")},{CameraModelId("line_scan_division")},{HalconRectangularDotPlate},NotSupported)` |
| CalibrationArtifact/refs | `CalibrationArtifact(R("0.2"),CandidateArtifactRef(AssetId("syn-line-candidate"),R("1"),tempDigest),methodRef,InputDigest,lineDevice,Geometry.Reference,[LF0,LF1,LC0],prepare.Partition,parameters,exactSolvedRef,FitResiduals,DomainReport,dependencyRefs,t0,Adapter)`。dependencyRefs是其所有规范typed值中ContentRef加上述C原件去重，按Digest.Hex ordinal排序，全部存在内容字典；CandidateDigest=ComputeArtifactDigest排整个Candidate，with finalCandidate封存。published=`PublishedArtifactRef(AssetId("syn-line-published"),R("1"),CandidateDigest)`，Store读取时维护该published→artifact映射并独立核envelope/内容。Mock读取不授真实Published事实，只实现公开端口受控返回 |
| ICalibrationArtifactStore | 仅ReadPublishedAsync精确published→上述深复制artifact/hash闭包；其它asset CAL-108。WritePublishedUnqualifiedAsync在这个reader-only mock返回`PublishReceipt(op,ResourcesReleased,PublishFailed,null,false,CalibrationError(UnsupportedMethod,Publish,false,false,"Calibration.UnsupportedMethod",op,DiagnosticRef("syn-read-only")),DiagnosticRef("syn-read-only"))`，op取实参operationId；GetOperationReceiptAsync固定NotCommitted/Receipt=null/CompletionReleased、原请求两个ID回写、Error=null、Diagnostic="syn-read-only"，不建新事实。接口签名仍 §9.1原样 |
| ICalibrationSolvedContentSource | OpenReadAsync只接受精确published/exactSolvedRef/operationId登记；核字典原bytes/length/hash再返回只读MemoryStream深副本，reader唯一Dispose；错误asset/ref CAL-108，可注入OpenTask/ReadTask/Dispose闩锁，由reader原ledger留存 |
| ICalibrationQualificationPort | Read-only mockbool DecisionAvailable=false：ResolveQualificationAsync→`QualificationSnapshot(published,request.Use,Unknown,null,null,null,null,watermark)`。true→`QualificationSnapshot(published,IntendedUse("LineScanRow0Projection",R("1")),Qualified,QualifiedAssetRef(published,QualificationId("syn-line-q"),R("1"),t0-1day,t0+1day),lineDevice,domain,C("line-q-evidence"),watermark)`；watermark=`AuthorityWatermark("Synthetic","line-1",R("1"),t0,t0+1day)`，不同Use/配置reader核不匹配。WatchInvalidationsAsync正常空枚举；注入迟到时仍原MoveNext/Dispose ledger，不按枚举结束改read事实 |
| options/adapters/resources | readerOptions=`CalibrationAssetsOptions(2,64,1048576,1s,32,8)`，Gate共享总1MiB/并发1，Diagnostics容量64，Clock=t0/单调确定时钟；adapters=`CameraReadAdapters(readonlyStore,contentSource,qualificationPort,gate,diagnostics,clock)`。方法fault shape/异常映射/lease规则沿 §7.4.6A同指定闩锁，不注入JointFactory或ReferenceResolver |

Core纯仿真消费者 A=测试 `Consumers/SolvedCameraToolHost.cs`，B=`Consumers/MosaicCameraReadHost.cs`：各自预留根槽/显式CameraReadAdapters→Create→用新id、exactSolvedRef、Use及同lineDevice/domain、Exposure t0..t0+1ms、Budget(2s,3s,8,65536,128,1048576,1)调用Read→Unknown无Snapshot→模拟外部Qualified后另id再Read→断言solved.Focus=.010而非.009、Vy=.00002而非.000018、原模型/units/ref/hash/Device/q/watermark不变→有限Stop/一次Dispose或保留原根，borrowedStore共享而实例/请求/root独立。具体root/catch/finally使用 §7.4.6A同完整卡但替换Factory为CameraParametersReader.Create、业务为ReadAsync、OperationState为CameraReadOperationState，不借JointModule/JointRef。B仅测试映射到mosaic公开值前的参数/单位断言，不改其工程或冒称真实LineScanRow0Projection已接线。

断言编号 `CAL.READ.01–06`：①format往返与solved!=initial；②未知format/尾字节/NaN/错unit/model/count/deviceDigest/asset/hash拒绝；③同id重放次数1、改budget/expectedRef冲突；④撤销/过期/Use/曝光或配置域不符无Snapshot、权威未知不缓存；⑤迟到OpenStream/read/Dispose/qualification/Reserve保留原task/buffer、有限DrainPending/真实归还后终态；⑥双Host关闭互不影响/返回vector深副本/line11项逐单位准确。冷/热Read/Decode/Store/资格/stream release的P50/P95/P99和峰值/排空沿 §15，无目标NotEvaluated。公开codec/DTO/纯mockreader为CAL-CR；真实format writer、耐久ContentSource/qualification接线、HALCON数值和mosaic实测资格分别属CAL-A1/A3/I1，不能由模拟通过一并接收。

### 9.4 二维 Adapter 实施卡与局部平面内容

本节闭合 CAL-A1/A2/A3 的软件读写语义，不提升真实 API 编译/Golden/物理资格。唯一真实工厂为 `CameraAsunImageSolverFactory(AdapterCapabilities capabilities,TimeProvider clock,ICameraMethodContentSource methodContent,ICameraParametersReader? cameraReader)`，实现 §9.1 的工厂与 scope；capabilities 与实际方法/模型/靶白名单精确匹配，CreateScope 只保存借用端口，不开 IO/native。同一 scope 的不同作业也不共享可变 calib-data handle。

`ICameraMethodContentSource.OpenAsync(ContentRef reference,SolverExecutionContext execution,CancellationToken token):ValueTask<Stream>` 为新增方法证据只读端口，由宿主显式注入真实Reference/内容Owner；它只打开本次靶/Profile/观测中声明的identity/pose/certificate/domain依赖，不允许任意路径。factory和scope借用此端口/CameraReader，所有原Task/Stream经本次execution账本，有界核hash/长度/EOF后decode，不能假设workspace含尚未导入的外部内容。Decoded证据须经宿主冻结的参考件/采集Owner注册映射和当前输入核验；hash只证明字节完整，不证明来源可信。缺可信MappingAuthority拒识，不把ContentRef当签名。证据被使用即纳Candidate.Dependencies与输入闭包，不在Dispose之后留下悬空源。

已知内参圆姿态证据固定 `CirclePoseEvidenceV1(CameraRead:CameraReadRequest,PlaneInCamera:RigidPose,MaximumPlaneDistance:Length,MaximumNormalAngle:Angle,ActualDomain:OperatingDomain,AuthorityEvidence:ContentRef)`；头 `calibration-circle-pose-evidence-v1`/根同名/64KiB，PlaneInCamera的原点/朝向是独立板面物理pose，不取本次待估内参拟合的板姿态；距离meter非负、角radian∈[0,π/2)、当前图Device/曝光/域精确匹配。CameraRead.Asset=CircleDetection.KnownCamera.Artifact，读取实际SolvedParameters且本次资格Applicable（CameraRead按§7.3A.2嵌套模板规则生成新child ID/取小预算查询），其资格ID/修订必须精确等KnownCamera；未知/撤销拒绝，原KnownCamera不是永久授权。cv2.get_circle_pose使用本已解透视模型和证书真实半径、center_normal；对两解分别检查正深度、中心到独立平面的绝对距离<=MaximumPlaneDistance、法向与已知正向dot对应的夹角<=MaximumNormalAngle以及有效域，恰一满足才用project_3d_point输出物理中心pixel。两解/零解拒绝，禁止用较小残差挑一解。近法向模式按IdentityEvidence.NearNormalEvidence独立核偏差上界，不以本椭圆轴比推导偏差资格。encoder/pose/原图Owner来源仍是外部事实，所有数值域/选择公式为本节软件职责。

1. Solve 核 PreparedInputDigest、参数摘要、模型/初值/估计项和 Profile；设备敏感字段、数据分区和证书几何在打开图前检查。以 execution.Budget 作本次唯一截止/资源上限，先预约托管与 native 同时峰值，再逐图打开/核 UInt8 lease；copy 后的 native 图必须是独立拥有的对象，不能在 lease 归还后使用借用指针。
2. 检测只用 fit 物理组，严格执行 §7.1/§9.2 的固定分支；请求的 Points 是显式离线已测观测时逐点核质量/独立身份和原图证据，否则用检测器从原图形成完整 ObservedPoint。两来源不能混合挑选更好点。Crop/halo 仅优化检测：crop row/column 加回原始传感器坐标，旋转/镜像/binning 按 PixelCoordinateLayout 版本化逆变换；halo>=ceil(3*Sigma) 为 gauss 路线软件支持下限，ROI 边缘未获完整邻域的点拒绝。线扫只接受本模型的第一行姿态/恒速/行完整性证据。
3. 标准板的检测模型和实测点求解模型分别创建/释放，点表按 ReferenceGeometry.Points 原顺序，Index 是该表零起索引、不能把字符串 ID 转 int 猜索引；每 PoseIndex 一次 set_calib_data_observ_points。调用 set_calib_data 的 excluded_settings/加入估计项严格沿 §7.2C；对两种 polynomial 的切向项用 poly_tan_2，禁止将 p1/p2 单独加作配置名。calibrate_cameras 完成后逐项 get_calib_data 读取 camera 0 params、每个 calib_obj_pose 及每组实际观测；完整已解向量写 CameraSolutionV1，不能把初值与局部返回拼为结果。
4. 重算逐点重投影误差：透视面阵使用 project_3d_point，线扫使用该模型支持的投影语义；远心点/深度遵守不可观测约束。solver Error 单独保存，逐组 RMS=sqrt(sum(rowError²+columnError²)/点数)，MaximumAbsolute=max(hypot(rowError,columnError))。与独立物理误差分开。无法读取完整解或模型越界 CAL-103/104，无候选。
5. `SolvedParameters` 仅为 §9.3 的 intrinsics/motion 内容。可选 HALCON `.dat` 由 write_cam_par 写作业唯一私有文件，再 read_cam_par，在 Profile.PoseOrthogonalityTolerance 作为无量纲相对容差内逐项比较（整数尺寸/模型名必须精确；标量比较 abs(a-b)<=tol*max(1,abs(a),abs(b))），封存原字节 `halcon-camera-parameter-file`/`26.05`，作为 Dependencies。临时路径由 Adapter 生成不接受外来路径；写/读任务、文件流/原字节/tuple 都入同一账本，真实退出后才清理本作业文件。读取外来 .dat 只作离线参数初值且保存 source ContentRef，不能直接复制别的 asset/资格身份或绕过 Solve→Validate。
6. Validate 冻结已有解，不再 calibrate_cameras、不改检测阈值、不删留出点。使用独立 ValidationGroups 提取所有声明观测并核同样的拒识条件；物理距离/位置/角度按 ValidationPlan 引用的独立标准与坐标转换逐点计算，最大绝对误差和 MinSamples 同时满足才 Validated。新验证组若被用于重新拟合，必须新分区/新 session；旧验证证据不能复用。

**局部平面不是光学内参的隐含字段。** `CameraLocalPlaneV1(CameraSolution:ContentRef,DeviceDigest:Digest,PlaneInCamera:RigidPose,PlaneDomain:OperatingDomain,Reference:ReferenceGeometryRef,PoseEvidence:ContentRef)` 为完整形状，format=`calibration-local-plane`/revision=`1`，头 `calibration-local-plane-v1`、根同类型名，按 §3.7 规则编码、上限64KiB。PlaneInCamera 为 plane→camera，单位 meter/正交右手；PlaneDomain.Frame 是该 plane frame。PoseEvidence 必须说明局部参考面的独立固定位置/平面度；仅从 fit 靶姿态得到而没有实际用途平面证据的 pose 不可发布为该用途局部平面。允许只发布内参；平面域未知不妨碍相机 intrinsic 用途，但拒绝 pixel-to-world 平面用途。该内容放同一资产 Dependencies，不改变 CameraSolutionV1 或 Camera Read API 1。实际映射执行归 image-rectification/计量消费者；相机移动后 PlaneInCamera 是否仍成立需依据实际参考面域重查，不能复制工作区绝对位置。

新增无 UI 读取位于 `.CameraRead`：`CameraPlaneReadRequest(ReadRevision:string,Asset:PublishedArtifactRef,ExpectedPlane:ContentRef,Use:IntendedUse,ActualDevice:DeviceConfigurationSnapshot,ActualDomain:OperatingDomain,ExposureFrom:DateTimeOffset,ExposureTo:DateTimeOffset,Budget:CalibrationExecutionBudget,OperationId:OperationId)`，ReadRevision=`1`。`CameraPlaneSnapshot(Plane:CameraLocalPlaneV1,PlaneContent:ContentRef,Camera:CameraParametersSnapshot)`；`CameraPlaneReply(OperationId:OperationId,Completion:OperationCompletion,Status:ApplicabilityStatus,Snapshot:CameraPlaneSnapshot?,Findings:IReadOnlyList<ApplicabilityFinding>,Error:CalibrationError?,Diagnostic:DiagnosticRef)`，只有 Released/Applicable 有 Snapshot。`ICameraLocalPlaneReader : IAsyncDisposable` 提供 `ReadAsync(request,token):ValueTask<CameraPlaneReply>`、`GetOperationState(id):CameraPlaneReadState`、`StopAsync(request,token):ValueTask<DrainResult>`；state 字段与 CameraReadOperationState 相同，仅 Final 类型为 CameraPlaneReply。工厂 `CameraLocalPlaneReader.Create(options,CameraPlaneAdapters)`，adapters=`(Store:ICalibrationArtifactStore,Content:ICameraPlaneContentSource,Qualifications:ICalibrationQualificationPort,ExecutionGate:ICalibrationExecutionGate,Diagnostics:ICalibrationDiagnostics,Clock:TimeProvider)`；Content.OpenReadAsync(asset,exactDependency,execution,token):ValueTask<Stream> 仅允许该 asset 的 solved/plane 依赖闭包。

PlaneReader 是一次原操作内的完整链：回读资产/核闭包 → 精确 ExpectedPlane 属 Dependencies → 有界读取解与平面两个原字节/hash/EOF → CameraSolution/DeviceDigest/Reference/PlaneDomain 匹配同一资产 → 只读当前资格，必须覆盖本次平面用途、曝光区间和完整域 → 防御复制两个快照。不能拼两个分别查询的 Qualified。缺 plane CAL-101；pose/frame/内容不一致 CAL-108；未知域/权威 Unknown；确认越域 NotApplicable。请求头 `calibration-camera-plane-read-v1`，请求根/省顶层 ID/其它字段全纳摘要；同 §9.3 的单调截止、原 Task/Stream/迟到 ledger、借用端口和关闭规则。公开 `CameraLocalPlaneCodec.Encode/Decode` 按上述形状执行，不为 Core v0.2 增字段。CAL.PLANE.01：同解+plane资格通过返回两个同 asset 快照；02：另一asset的同名 plane 拒绝；03：只存在内参时 Intrinsic 读取仍可成功，plane用途无假单位阵；04：参考面越域/姿态方向颠倒/撤销/迟到流不得返回平面快照。

**部署与落点：** 上述工厂/检测/CameraSolution writer/native文件位于唯一 AsunImageAdapter 工程；Recommendation 服务、codec 与 PlaneReader 位于既定 Core 工程相应 namespace 子目录，定向测试沿既定 Core.Tests 的 CAL.AUTO.01–05/CAL.PLANE.01–04。HALCON检测/文件roundtrip测试沿既定 AsunImageAdapter.Tests，两个消费者分别仅依赖 Core，注入自己的 provider/reference/gate。共享原图由只读内容 Owner 提供，不共享 solver/native句柄。未运行源码编译不能把算子语义写成“可编译 C# 调用”；实际公开重载确认是实现验证，不是仍待设计参数/算法/Owner。

## 10. 可选 UI 契约

核心能力必须可无 UI 调用。可选 WPF 控件消费上述 Core 请求、进度、残差和结果；控件不创建隐藏窗口以初始化服务，不持有唯一参数校验，不存资产事实，不签发资格，不激活、不停机。宿主负责权限、审批、采集、业务导航和设备副作用。

可选 `CalibrationWorkspaceControl` 以工程师完成“确认配置/靶标 → 检查观测和覆盖 → 求解 → 独立检查 → 请求发布”为主任务；操作者模式仅看资产/资格/失效原因，发布权限由宿主提供命令许可并在提交时复核。状态始终区分候选、验证通过、已发布未资格、用途适用、未知和撤销；默认主动作只有当前阶段的安全下一步。不会把所有 native 参数铺在主页面。

固定 1920×1080 验证 viewport，先扣 OS 任务栏、宿主标题/边框/状态区；剩余 client 内顶部命令带 48 DIP、底部状态 28 DIP，左侧观测列表 240 DIP、右侧参数 300 DIP，中部影像获得其余宽度且不少于工作区宽度 60%，下部可折叠残差区 180 DIP；若实际 client/DPI 不足，右侧改为明确“参数”抽屉，优先保留影像与主命令，不更改显示设置。以下是控件组合与接收断言，不宣称真实 WPF 已运行。

| 区域 | 控件/行为 | 验收 |
|---|---|---|
| 工作区 | DevExpress DockLayoutManager + LayoutPanel/DocumentGroup；主影像 panel 的 AllowFloat=false、AllowClose=false，观察/参数允许折叠；主题继承宿主，不改进程全局 ThemeManager | 同主题排版、8 DIP 间隔、图标与短文字并用；主图不会被关闭/浮出；仅恢复宿主可信布局，不反序列化外来布局文件 |
| 观测列表 | GridControl + TableView：组、图/姿态、点数、覆盖、接受/拒绝和原因；按组分区显示 Fit/Validation，拒绝原因可筛选 | 选 ObservationId 同步图上点和残差；更改选择不重跑求解；虚拟化，禁止每个点创建独立 WPF 元素 |
| 影像与残差 | 复用宿主注入影像 presenter；拟合点、剔除点、原始图/crop 坐标和域边界分层；ChartControl + XYDiagram2D + PointSeries2D，SeriesPoint.Tag 绑定 ObservationId/ReferencePointId | 图/列表/图表点击互相定位，不修改原观测；颜色加符号/文本区分；百万点不全部绑定 chart，显示有界采样并标明原总量，完整报告可查 |
| 参数与诊断 | PropertyGridControl.SelectedObject 绑定不可变投影，PropertyDefinitions 显式白名单；基础尺寸/模型常显，高级参数渐进展开 | 所有编辑经同一 Core 验证；Prepared 后首次 Solve 单独冻结参数摘要；已有候选后改参数须新会话，不声称参数改变了准备摘要，不原地修补候选 |
| 命令/恢复 | 准备、求解、独立检查、发布、取消；发布未知显示“查询发布结果”，调用原 ID 回查；非显然限制由 BarItem.SuperTip 解释原因和恢复 | 发布中禁重复点击；取消是请求，不先显示已停止；没有资格批准/激活/设备动作按钮 |

WPF 对外接入形状：`void CalibrationWorkspaceControl.Attach(ICalibrationAssetsModule module, ICalibrationImagePresenter presenter, ICalibrationUiHost host)`、`ValueTask DetachAsync()`；仅 UI Dispatcher 调用 Attach/Detach，重复 Attach 先显式 Detach。`ICalibrationImagePresenter.ShowObservationAsync(ObservationRef, CancellationToken)` 返回 ValueTask，清空为 `ValueTask ClearAsync(CancellationToken)`，由宿主显式实现影像展示/显示 lease，禁止模块扫描 viewport 内部；展示取消后仍等待自己的 display lease 归还，不能释放 Core 输入租约。`ICalibrationUiHost` 公开 `string CultureName { get; }`、`event EventHandler CultureChanged`、`string GetText(string key)`、`bool CanExecute(CalibrationUiCommand command)`，以及 `event EventHandler PermissionsChanged`；command=`Prepare/Solve/Validate/Publish/QueryReceipt/Cancel`。它只投影宿主权限，不代替提交授权。UI 需图像/Host 适配且尚未绑定真实 presenter 的切片保持 PreparationIncomplete，不能用模拟图片声称接入通过。

Tab 顺序为观测 → 主动作 → 参数 → 诊断；Ctrl+Enter 执行当前启用主动作，Esc 请求取消本控件发起的当前作业（无活动时只关参数抽屉），Space 在列表选中图，Enter 定位所选异常。快捷键不绕过许可/校验，确认发布只在明确操作中显示一次，不随进度抢焦点。关闭控件取消观察/显示订阅并 await display 清理；Core 共享实例不被 Dispose，不自动取消其他调用方作业。进度默认合并到不超过 10 Hz，终态/错误从账本补读；关闭后的迟到更新被本控件 generation 丢弃，Dispatcher 关闭不阻塞 Core 排空。

宿主动态注入 zh-CN、zh-TW、en-US，不在模块重复语言入口，所有标题/参数/状态/错误/恢复资源同源。最低词条：`cal.solve`=求解/求解/Solve，`cal.validate`=独立检查/獨立檢查/Validate，`cal.publish.unqualified`=发布未资格资产/發佈未取得資格的資產/Publish unqualified asset，`cal.publish.unknown`=发布结果未知，请查询原操作/發佈結果未知，請查詢原作業/Publish outcome unknown. Query the original operation.，`cal.drain.unknown`=尚未确认停止，暂不能重试/尚未確認停止，暫不能重試/Stop is unconfirmed. Retry is unavailable.；其余 CAL-100～117 各有原因、影响和恢复资源，诊断不把原生异常直接显示给操作者。文字、UIA 可访问名称与键盘提示随 CultureChanged 刷新，不重建 Core 会话；三语长度、DPI、键盘/UIA、真实主图行为均是后续 WPF 验收门。

### 10.1 完整方法接入、编辑与安全下一步

`CalibrationWorkspaceBindings(Camera:ICalibrationAssetsModule?,Joint:IJointCalibrationModule?,Specialized:ICalibrationSpecializedModule?,Recommendation:ICalibrationRecommendationService?,CameraReader:ICameraParametersReader?,PlaneReader:ICameraLocalPlaneReader?)` 全部为借用，至少装配当前任务的一项，不在控件构造中创建/查找业务服务。新增Attach重载 `Attach(CalibrationWorkspaceBindings bindings,ICalibrationImagePresenter presenter,ICalibrationAuxiliaryPresenter auxiliary,ICalibrationUiHost host)`；旧Attach仅Camera路径的兼容重载，不重定义Core API。重复Attach先Detach。`SetDraft(CalibrationUiDraft draft)`、`SetReadRequest(CameraReadRequest request)`、`SetPlaneReadRequest(CameraPlaneReadRequest request)` 均只Dispatcher、复制输入/同一public codec校验；读取请求只检查其明确Asset/Expected引用，不能加载latest。

`CalibrationUiDraft` 是封闭联合：`CameraUiDraft(Preparation:PrepareRequest,Parameters:SolverParameterSet,Plan:ValidationPlanRef,IndependentObservations:IReadOnlyList<ObservationRef>)`、`JointUiDraft(Input:JointSolveInput)`、`SpecializedUiDraft(Input:SpecializedSolveInput)`、`RecommendationUiDraft(Request:RecommendationRequest)`。完整字段、预算、session与源身份均来自宿主显式加载；Joint/SP/Recommendation预算由下面UiRunOptions提供，Camera保留Prepare预算但每入口有自己执行预算。`UiRunOptions(Solve:CalibrationExecutionBudget,Validate:CalibrationExecutionBudget,Publish:CalibrationExecutionBudget,Query:CalibrationExecutionBudget,WaitForDetach:TimeSpan)` 由宿主 `SetRunOptions` 显式给出，WaitForDetach∈(0,30s]。缺options/相应端口时当前主动作不可执行并显示具体缺项，不假装调用成功。

控件参数表编辑生成新的不可变draft值，单击“准备/求解”前按同一Core校验。Camera未开始时编辑参数不修改PreparedInputDigest；已Prepare后只允许首次Solve的SolverParameterSet新值；观测/靶/Profile/布局发生变更或已有候选后改任何参数，原候选作为历史只读保留、当前草稿新SessionId（Guid.NewGuid）并清除当前验证/发布引用。Joint/SP输入的任一变更均新session；Recommendation source变更清除旧建议。不得从ViewModel写Profile源文件、Store或生产参数。“确认建议”只向宿主发 `RecommendationConfirmed(RecommendationValue value)` 本地事件，宿主复核SourceDigest并显式加载新的CameraUiDraft，不自动Apply。

| 任务与区域 | 可见数据和固定操作顺序 | 禁止/恢复 |
|---|---|---|
| Camera | 常显设备/镜头/模型/靶修订与单位、fit/check组、布局、参考件证书、内参初值/估计项；左组列表→原图/点ID→覆盖→准备→求解→独立检查→发布未资格 | 方向歧义/覆盖不足定位观测；修改后新草稿，不降低物理界；线扫另显恒速/第一行pose/epoch/行完整性 |
| Joint | 常显相机0/投影器1、both标定pattern、实测靶、白/黑图、白环/有效row+column层、fit/check分区、两端残差和独立ray误差 | 直接Solve→Validate→Publish；原白/黑mask/局部映射失败有具体原因，不把黑心无信号隐藏为“求解失败”；runtime pattern兼容与资格只读 |
| HandEye | 安装拓扑/robot类型/frame链、实际tool/图姿态配对/同步、激励轴/角、原与corrected链分别显示 | 6D缺失/SCARA高度/旧内参不适用均阻动作，UI不发机器人运动、不提供“自动回零” |
| Sheet | 特殊物Dxf/实测证书、disparity/domain四面和holes、已解camera/light/movement poses、拟合和独立meter误差 | imported disparity唯一路线，缺域点不以0显示合格；无扫描/补采设备按钮 |
| RAD / FF | 相对响应用曝光递减和256LUT/有效灰度；平场显示暗/亮独立组、无效mask/增益图/均匀性 | 相对能量/绝对光度分开文字；无效pixel棋盘透明叠层，不填0误导；不写硬件LUT |
| Display | 显示器配置/测量仪器、实测和目标cd/m²曲线、256LUT、独立实测检查 | 仅“预览显示副本”，原图hash/生产输入保持；不动OS/显卡设置，过期退回原图并显示原因 |
| Recommendation | 明确“参数建议”；基线/有限候选/调参组和保留Validation组、每例错受错拒/定位误差/资源 | 主动作“计算建议”；取消无部分建议；来源变化不可确认；确认后仍需新session独立检查 |
| Camera/Plane Read | 原资产/hash/解格式、真实已解参数、可选局部参考面与资格/水位/有效域 | 主动作“读取参数”；不带求解/发布按钮；未知/不适用时无图上物理坐标 |

控件发起每入口都生成自己的新OperationId并保存为本次原身份；回查另新ID且携原PublishId；重复点击不新发，取消只向该作业原token请求，不调用共享module.StopAsync（它会影响其它调用方）。Camera走Prepare→Solve→Validate→Publish，其它求解方法按专用接口顺序；Read/Recommendation与求解作业同样独立generation/ledger观察。GetOperationState仅用于自己的已知ID，UI不把别的调用方作业借来取消。PublishUnknown时唯一安全主动作QueryReceipt，Found后校验回读闭包；NotCommitted需权威证明后转宿主受控恢复，不由UI产生新PublishId；Camera沿CAL.CORE.06保留/重放原O1和完整摘要，但在当前实例已终结为PublishUnknown时同ID只重放原结果，不会再开Store写入。当前公开接口未提供durable重提写入命令，UI明确保持未发布并通知宿主恢复，不能显示已重新发布；未来若确需重提，由原Store/宿主显式实现保持原幂等身份的恢复事务并单独接收，不篡改本Core去绕幂等。Joint/SP同样保持原身份/摘要，Unknown继续原回查。已Released的验证失败可编辑/建立新session，DrainPending/Stop未确认时保留取消/诊断和排空观察，不允许再次求解占用同资源。

`ICalibrationAuxiliaryPresenter.ShowAsync(CalibrationVisualSelection selection,CancellationToken token):ValueTask`、`ClearAsync(token):ValueTask`；selection仅四个sealed分支 `RasterSelection(Content:ContentRef,Device:DeviceConfigurationSnapshot,Layer:CalibrationVisualLayer)`、`SheetSelection(Disparity:ContentRef,Installation:SheetInstallation)`、`PoseSelection(Observation:HandEyeObservation)`、`TransferSelection(Solution:SpecializedSolution)`；layer枚举=`Raw/White/Black/ProjectorRows/ProjectorColumns/Validity/DarkMean/GainMap`。Joint用packet对应ContentRef与camera配置，FF使用Photometric Device；原 ObservationRef 仍走旧presenter。Presenter由宿主通过只读内容端口获取并拥有显示副本，控件不能扫描影像模块内部或转交Core输入lease；缺展示能力显示明确缺项/内容ID，不能伪造示图。图上坐标/值和legend说明原始pixel、meter或cd/m²，残差完整数据在公开报告，显示采样不能修改结果。

Detach立即撤本UIgeneration、取消自己的观察/显示token，等待所有已接纳display任务与ClearAsync实际退出；WaitForDetach只用于显示“关闭中”，Detach原Task仍持有真实display ledger，不能返回已卸载或放弃迟到lease。Core在途作业已被独立实例ledger持有；Detach可有限停止观察，不Dispose借用模块/端口。Dispatcher关闭时清理在非UI拥有者执行，不借Dispatcher排空native；既有helper可安全释放但不得重入已经销毁窗口。宿主在真实Detach完成前保留presenter/host，本控件可关闭视觉树但不能重新Attach在途显示ledger。

### 10.2 三语、视觉与真实验收

继承宿主DevExpress主题，明暗均由宿主选择、不设置进程全局主题。主图深中性背景、8 DIP间隔、标题/数字/单位层级、相同状态同图标+短文字，错误不单靠红绿；诊断详情与高级native参数在明确可达侧栏。BarItem.SuperTip说明参数边界和失败后动作，关键“查询发布结果/取消”常显。布局宽度按实际client/DPI计算，左240+右300+gap在中图不足60%时先移参数至抽屉，再折叠观测列表；不用固定像素宽高破坏1920×1080基线。Docking/Grid/Charts/PropertyGrid API沿§18.3已读本机匹配版官方XML，未重复研究/下载依赖。

基础命令三语资源必须含：准备/準備/Prepare，求解/求解/Solve，独立检查/獨立檢查/Validate，发布未资格资产/發佈未取得資格的資產/Publish unqualified asset，查询发布结果/查詢發佈結果/Query publish result，取消/取消/Cancel，读取参数/讀取參數/Read parameters，计算建议/計算建議/Compute suggestion，确认建议/確認建議/Confirm suggestion，新会话/新工作階段/New session，参数/參數/Parameters，诊断/診斷/Diagnostics。所有参数标题/单位/域/组/pose方向/legend/Method枚举/资格/错误均取同一key资源；技术型号/ID/hash是事实数据，不翻译或作状态文案。新增UiCommand=`ReadCamera/ReadPlane/Recommend/ConfirmRecommendation/NewSession`，与原六命令形成固定集合；宿主CanExecute覆盖它们，控件不通过快捷键绕过权限或把“发布”改成“合格”。

下表是 CAL-100～117最低完整三语错误资源；每格依次为“原因；影响；动作”，实现分别保存三个稳定子key，原异常仅在diagnostic可查，插值ID/单位/数值使用指定Culture格式（hash保持原值）。

| 码 | zh-CN | zh-TW | en-US |
|---|---|---|---|
|100|输入缺失或格式错误；未开始；修正所列字段|輸入缺失或格式錯誤；未開始；修正所列欄位|Input is missing or invalid; Not started; Correct the listed fields|
|101|方法或格式未支持；未计算；选择已支持的方法或适配器|方法或格式未支援；未計算；選擇已支援的方法或配接器|Method or format is unsupported; No calculation; Select a supported method or adapter|
|102|观测或覆盖不足；不能求解；按缺项补充观测|觀測或覆蓋不足；無法求解；依缺項補充觀測|Observations or coverage are insufficient; Solve is unavailable; Add the listed observations|
|103|观测未通过检查；未接纳；检查原图、点号和参考证据|觀測未通過檢查；未接納；檢查原圖、點號與參考證據|Observation checks failed; Not accepted; Check source images, point IDs, and reference evidence|
|104|独立检查未通过；不能发布；检查失败项并建立新会话|獨立檢查未通過；無法發佈；檢查失敗項並建立新工作階段|Independent checks failed; Publishing is unavailable; Review failures and start a new session|
|105|资产不适用；不能用于当前用途；核对配置和有效域|資產不適用；無法用於目前用途；核對設定與有效範圍|Asset is not applicable; Unavailable for this use; Check configuration and valid domain|
|106|资格尚未确认；不能使用；恢复权威连接后重新查询|資格尚未確認；無法使用；恢復權威連線後重新查詢|Qualification is unconfirmed; Asset is unavailable; Restore the authority connection and query again|
|107|修订或操作身份冲突；未重复执行；核对当前修订和原操作|修訂或作業識別衝突；未重複執行；核對目前修訂與原作業|Revision or operation identity conflicts; No repeated execution; Check the current revision and original operation|
|108|内容校验失败；内容不可用；恢复精确版本原件|內容驗證失敗；內容無法使用；恢復精確版本原件|Content verification failed; Content is unavailable; Restore the exact source version|
|109|发布结果未知；不能重复发布；查询原发布操作|發佈結果未知；無法重複發佈；查詢原發佈作業|Publish outcome is unknown; Do not publish again; Query the original publish operation|
|110|已请求取消；尚待资源退出；等待排空状态|已請求取消；仍待資源退出；等待排空狀態|Cancellation was requested; Resources may still be active; Wait for drain status|
|111|执行期限已到；无可用结果；确认排空后检查预算|執行期限已到；無可用結果；確認排空後檢查預算|Deadline reached; No usable result; Confirm drain and review the budget|
|112|资源上限已到；未完成；缩小离线输入或审核预算|資源上限已到；未完成；縮小離線輸入或審核預算|Resource limit reached; Not completed; Reduce offline input or review the budget|
|113|适配器操作失败；本次结果不可用；查看诊断并确认排空|配接器作業失敗；本次結果無法使用；查看診斷並確認排空|Adapter operation failed; This result is unavailable; Review diagnostics and confirm drain|
|114|当前状态不允许；未执行；完成当前操作或建立新会话|目前狀態不允許；未執行；完成目前作業或建立新工作階段|Current state prevents this action; Not executed; Finish the current operation or start a new session|
|115|模块正在关闭；未接纳新操作；等待关闭完成|模組正在關閉；未接納新作業；等待關閉完成|Module is closing; New operation was not accepted; Wait for shutdown|
|116|模块操作异常；结果不可用；保留操作ID并查看诊断|模組作業異常；結果無法使用；保留作業ID並查看診斷|Module operation failed; Result is unavailable; Keep the operation ID and review diagnostics|
|117|候选尚不能发布；未发布；完成独立检查并核对候选|候選尚無法發佈；未發佈；完成獨立檢查並核對候選|Candidate cannot be published; Not published; Complete independent checks and verify the candidate|

取消文案根据Completion区分“已请求取消/尚未确认停止”与“已取消，资源已释放”（已取消，資源已釋放 / Cancelled. Resources released.）；三语切换只刷新文本/可访问名/数值显示，不重新求解或重载内容。无权限/缺字段禁用SuperTip明确原因。1920×1080固定viewport内验证任务全链、最大语言长度/系统原DPI、Tab/快捷键/UIA、图表点/列表/图像联动、两Host语言/权限隔离、Dispatcher关闭/迟到显示/发布Unknown恢复。真实presenter、WPF/DevExpress行为和UIA实测尚未执行；缺接线/运行证据是CAL-W1实现/验收门，不是把UI软件流程留给未来Owner。

## 11. 无 UI 调用流程示例

下面是 v0.2 的语义调用示例；模块签名是本文定义的计划合同，Handle… 为宿主流程，不冒充已编译源码。生产宿主只读解析既有资产，无需创建 UI。创建/Dispose 由宿主服务生命周期统一负责，不在每个 UI 事件中反复创建。

```csharp
var module = CalibrationAssetsModule.Create(options, adapters);
using var cts = new CancellationTokenSource(TimeSpan.FromMinutes(10));
var executionBudget = CalibrationExecutionBudget.Default; // 每入口显式预算，None 仍受模块时限
try
{
    var prepared = await module.PrepareAsync(request, cts.Token); // request.ContractRevision == "0.2"
    if (prepared.Completion == OperationCompletion.DrainPending)
        return HostObservePending(module, prepared.OperationId);
    if (prepared.Status != PreparationStatus.Prepared || prepared.PreparedInputDigest is null)
        return HandleInputFailure(prepared.Error);
    var solved = await module.SolveAsync(
        new SolveRequest("0.2", prepared.SessionId, prepared.PreparedInputDigest.Value,
            frozenSolverParameters, executionBudget, solveOperationId), progress, cts.Token);
    if (solved.Completion == OperationCompletion.DrainPending)
        return HostObservePending(module, solved.OperationId);
    if (solved.Status != SolveStatus.CandidateReady || solved.Candidate is null)
        return HandleSolveOutcome(solved);
    var validation = await module.ValidateAsync(
        new ValidationRequest("0.2", solved.Candidate, independentPlanRef,
            independentObservations, executionBudget, validateOperationId), cts.Token);
    if (validation.Completion == OperationCompletion.DrainPending)
        return HostObservePending(module, validation.OperationId);
    if (validation.Status != ValidationStatus.Validated || validation.Evidence is null)
        return KeepCandidateForEngineeringReview(solved, validation);
    var persisted = await module.PublishAsync(
        new PublishRequest("0.2", validation.Candidate, validation.Evidence.Value,
            executionBudget, publishOperationId), cts.Token);
    if (persisted.Completion == OperationCompletion.DrainPending)
        return HostObservePending(module, persisted.OperationId);
    if (persisted.Status == PublishStatus.PublishUnknown)
    {
        var query = await module.QueryPublishReceiptAsync(
            new ReceiptQueryRequest("0.2", publishOperationId, executionBudget, queryOperationId), cts.Token);
        return query.Completion == OperationCompletion.DrainPending
            ? HostObservePending(module, query.OperationId)
            : HandleOriginalPublishQuery(query); // Unknown 不新建发布 ID；Found 后核回读
    }
    if (persisted.Status != PublishStatus.Published || persisted.PublishedArtifact is null)
        return HandlePublishFailure(persisted);
    var applicability = await module.ResolveAsync(
        new ResolveRequest("0.2", persisted.PublishedArtifact, intendedUse,
            actualConfiguration, actualDomain, executionBudget, resolveOperationId), cts.Token);
    return applicability.Completion == OperationCompletion.DrainPending
        ? HostObservePending(module, applicability.OperationId)
        : HandleApplicability(applicability); // 无外部 Qualified 时 Unknown/NotApplicable
}
finally
{
    // 独立的停止等待令牌；原计算令牌取消不能跳过清理。
    var drain = await module.StopAsync(
        new DrainRequest(stopOperationId, TimeSpan.FromSeconds(30)), CancellationToken.None);
    if (drain.Status == DrainStatus.ResourcesReleased)
        await module.DisposeAsync();
    else
        HostRetainAndSupervise(module, drain); // 宿主持有引用并隔离，不能静默丢弃或重复启动
}
```

生产宿主应优先只读解析既有资产。求解/验证工具不因为计算结果好就隐式发布；资格签发和当前绑定按各自 Owner 操作，不属于以上核心 Solve。

## 12. 案例和失败恢复

| 场景 | 期望结果 |
|---|---|
| 合法二维相机采样、参考件单位一致、独立边缘样本验证完成 | 返回候选、残差和域；发布前仍无资格结论 |
| RMSE 为低像素值，但独立长度偏差超出引用验收界 | `ValidationFailed`；资产不发布/不激活，保留两类误差原单位 |
| fit/check 来自同帧或相同物理姿态组 | 拒绝独立验证声明，返回数据泄漏诊断 |
| 图像分辨率相同但 ROI 起点或 binning 改变 | 若配置被声明为敏感则 `NotApplicable`；不得按宽高碰巧匹配 |
| 单平面资产收到离面 3D 点 | 返回超域/`NotApplicable`，不把点投影到 Z=0 冒充真实位置 |
| 参考件证书过期、单位/坐标方向未知 | 需要该证据的验证不能完成；保留已收数据，不推断单位或有效值 |
| native 求解期间取消且底层不可取消 | 先进入 `Draining`；native 真实结束并释放后才OperationDrained → ResourcesReleased → 终态 Cancelled；迟到候选丢弃 |
| 写入已提交但应答丢失 | 使用同一 OperationId 查询原回执；未知期间不新建“通过”记录 |
| 宿主两调用方以同一旧绑定修订并发激活 | 模块外 Binding Owner 一个 CAS 成功，另一个 RevisionConflict；Core 无激活入口，该集成断言不混作 Core 测试 |
| 资格 Owner 不可达、当前水位未知 | Resolve 为 `Unknown`/错误，调用方不得当成 Applicable |
| 原资产撤销而任务固定旧引用 | 发影响通知；模块不改历史。宿主依冻结流程决定隔离/复验 |
| 停止时 native worker 未归还图像租约 | `StopAsync` 返回未完成 Drain 状态和作业 ID；不能释放仍在用的底层资源 |

重试以错误码所列语义为准。不能恢复的候选及源引用保留以便调查，但必须标明不可发布；内容完整性失败进入隔离，不能自动修复原始字节。


### 12.1 固定软件断言输入（非生产门限）

| ID | 可执行输入 | 唯一期望 |
|---|---|---|
| CAL.CORE.01 | 模拟单相机 640×480、3×3 圆点、名义 Pitch=1 mm；实测点 P11=(1.002,1.001,0) mm，fit 组 F1/F2 与 check 组 C1 不交叠；模拟 solver 返回有限报告 | 规范 meter 点 P11=(0.001002,0.001001,0)，一次成组注入每 PoseIndex 的 9 点；候选 hash 包含实测修订；发布只有未资格内容 |
| CAL.CORE.02 | Observations=[]；或重复 PoseIndex=0；或 Image.ByteLength 超 256 MiB 的离线缺省 | 分别 CAL-102、CAL-100、CAL-112；无 provider/native 调用，不生成候选 |
| CAL.CORE.03 | 同一组 G 同时列于 FitGroups/ValidationGroups；已产生候选后修改参数并使用原 Solve OperationId 调用 | 分别 CAL-100、CAL-107；独立验证/旧候选不得发布 |
| CAL.CORE.04 | 宿主预注入周期板两个同等映射/QR ID 冲突，或靶被遮挡无可见原点 | CAL-103，不取第一映射，不换棋盘/默认点距；真实检测拒识另由 adapter golden 验证 |
| CAL.CORE.05 | 模拟独立误差 0.021 mm、仅测试的计划上限 0.020 mm；拟合 RMSE=0.01 pixel | ValidationFailed，无可发布 Evidence；像素/物理报告分别保存，该数字不成为生产门限 |
| CAL.CORE.06 | Store 已提交 O1，返回 PublishUnknown；回查权威 Found(Published)，或 Unknown，或 NotCommitted | Found 核原 hash 后返回原回执；Unknown 继续未知；NotCommitted 仅明确无在途提交时允许宿主重放原 O1；不自动创建 O2 发布 |
| CAL.CORE.07 | 双调用同 ID/同摘要，同 ID/不同摘要，两实例共享显式 gate 容量=1 | 第一对只运行一次 solver，第二对 CAL-107；跨实例预约串行且释放前不通过第二预约，无 static 状态 |
| CAL.CORE.08 | 模拟 native 闩锁不退出；请求取消；Stop 等待截止 | Stop=DrainUnknown 且持有 lease；无 CandidateReady/Drained/Released/Completed；闩锁退出后按原事件序列归还一次资源并 Cancelled，迟到参数不能发布 |
| CAL.CORE.09 | UI Dispatcher 已关闭、事件回调抛错；只读订阅被取消 | Core 仍真实排空，不等待 UI ack；取消仅该订阅；超过账本窗口读事件返回 Gap，不伪造连续 |
| CAL.CORE.10 | Qualified 水位 W1 后收到 Revoked W2 或权威断线，Resolve 仍传旧资产 | 撤销 NotApplicable，断线 Unknown/CAL-106；旧引用可查历史，不成为当前可用；软件版本回退不复活资格 |
| CAL.CORE.11 | 合同请求 0.1、未知枚举/必需字段、内容摘要不符 | 旧合同/未知必要形状 CAL-100，坏内容 CAL-108；不忽略字段、不迁移原字节，旧应用独立保留历史读取能力 |
| CAL.CORE.12 | 全部预算均满足且 Stop 无在途；重复 Stop 和 Dispose | Pending 空、ResourcesReleased；释放幂等，外部 Factory/provider/store 不被释放；释放后新业务 CAL-114 |
| CAL.CORE.13 | Point3=(-1,0,2) mm、Translation=(0,-2,0) mm；Pitch=0/-1 mm、WorkingDistance=0、ExpandedUncertainty=-0.1 mm；Length NaN、未知 LengthUnit=99 | 有符号点/平移接受并保留方向，换算=(-0.001,0,0.002) m；尺寸/不确定度非正及非有限/未知单位 CAL-100；Z=0 不拒绝，不调用 Abs |
| CAL.CORE.14 | §3.7 两个 Length 固定向量；Prepare 仅改 session/预算；同 O1 请求仅把 Deadline 从 10 min 改 9 min；第一次 Solve 两组不同有效参数 | 字节/hash 精确匹配；PreparedInputDigest 不因 session/预算变化；RequestDigest 因 budget/session 变化，同 O1 改预算 CAL-107；参数影响候选 hash 但不回流准备摘要，自 ParametersDigest 不参与其自摘要 |
| CAL.CORE.15 | 无 session Resolve、token=None，Deadline=100 ms/WaitLimit=150 ms；资格端口忽略取消，200 ms 返回 Qualified W1 | t=100 撤销发布权；t=150 返回 Unknown/CAL-111/DrainPending、QualifiedAsset=null；原 ID GetOperationState=Draining；t=200 清理后原记录完成 Unknown/ResourcesReleased，W1 不交付/缓存，新 ID Resolve 重查，不凭迟到 W1 可用 |
| CAL.CORE.16 | 分别 OpenImage/Reserve/OpenRead 在 200 ms 才返回 lease/reservation/stream，操作预算 100/150 ms；Dispose 闩锁再延迟至 250 ms；另有 CopyPlane/Write source 在途 | t=150 观察已结束，原 child/task/buffer 在账本；t=200 late 资源被代理接收不交已关闭请求，Dispose 一次；t=250 前 GetOperationState=Draining/Stop=DrainUnknown，之后 Released；Write/Copy 未退出前不释放源 stream/buffer，成功清理后预约归还一次 |
| CAL.CORE.17 | Publish 已发送后 100 ms 截止、150 ms 观察结束、200 ms Store 提交成功并释放；QueryReceipt 无 session、None token、同预算且端口迟到 Found | 原 Publish 返回 PublishUnknown/DrainPending，晚提交不变原结果或新建发布；查询亦在 150 ms Unknown/DrainPending/Receipt=null，Store 原 ID 事实可在释放后新查询查到，CAL-109/111、投递/资源状态不混淆 |
| CAL.CORE.18 | 同请求重复 ID 在 80 ms 重等，原 Deadline=100 ms/WaitLimit=150 ms，None token；Watch 100/150 ms 生命周期后 MoveNext 在 200 ms 晚通知；Stop WaitLimit=30 ms | 重复 ID 不重置 t0/不增端口调用，不超过原 150 ms 观察上限；订阅到期关闭投递，晚通知丢弃、enumerator 在实际结束后 Dispose 一次；Stop 有界返回 Pending 并能内存查询，None 不能无限阻塞 API 观察 |

这些是未来 BCL Exe harness 的固定场景，不是本轮执行记录。真实图像的空图/低对比/边缘裁切/棋盘拓扑歧义/圆轮廓偏差/线扫时序/手眼激励须由相应适配测试使用版本化 Golden/Replay；软件模拟的预注入诊断只证明 Core 分类与资源协议。

## 13. 版本兼容与迁移

模块包版本、公共 Contract 版本、资产格式版本、算法/求解器版本、HALCON 运行版本、AsunImage 程序集版本、资格 Profile 修订分别记录。语义化版本只对已批准契约执行：新增可选字段需旧读者安全忽略并有明确未知语义；删除/改名字段、改变单位/坐标方向、放宽适用域、改残差含义、改变资源所有权或状态迁移属于破坏性变更。

旧资产只读读取；迁移先完整校验，写新格式/新 hash 并保留旧资产引用和转换证据。禁止原地重写 hash 内容、把未知枚举映射为默认 Qualified 或把“缺字段”解释成无限域。不能证明向后兼容时返回 `CAL-101 UnsupportedMethod`（格式不支持，MessageKey=cal.format.unsupported），调用方可按自己的升级计划保留旧运行版本。回退仅能重新部署兼容旧格式的模块/应用并重新解析旧资格；已撤销资格不能因软件回滚复活。

HALCON/AsunImage 版本变化要比较同一冻结输入的参数、残差、坐标方向、异常行为和资源生命周期；不以编译成功宣布资产兼容。每种资产声明允许读取版本范围和求解版本。读旧资产不等于能用新算法重新验证。

## 14. 测试矩阵与验收断言

| 范围 | 必测断言 |
|---|---|
| 类型/单位 | 非有限数、缺单位、mm/m 换算、row/column 反置、坐标方向缺失均精确拒绝或转换；无隐式默认 |
| 求解数据 | 重复身份、同组 fit/check、缺观测、覆盖缺片、全局/局部退化及明确剔点理由可重放 |
| 算法正确性 | 冻结合成数据验证变换方向、参数有限性、独立像素残差；标准件物理误差另由有资格方案测试，不以合成数据代替 |
| 适用性 | 分辨率、ROI、binning、镜头、焦距、环境、用途和域逐项匹配；未知、过期、撤销拒绝；不得取 latest |
| 资源 | 成功、输入拒绝、native 异常、取消、超时、Dispose、存储失败均释放图像租约/句柄/临时文件；迟到结果不能发布 |
| 并发 | 双实例不同参数隔离、单实例变更求解不重入、预算上限、事件序列单调、回调重入不死锁 |
| 持久化/幂等 | 内容损坏、半写、索引/内容不一致、回执丢失、同 OperationId 重放及 CAS 冲突保持事实唯一 |
| 版本 | 旧格式可读/拒绝边界、未知必需字段 fail closed、迁移生成新 hash、回退不复活 revoked 资格 |
| UI（如交付） | 相同 Core 校验、取消/关闭/迟到进度、三语长度、键盘、权限投影和双宿主主题隔离；真实宿主按 1920x1080 验收 |
| 独立消费者 | 相机校正与离线二维计量工具引用同一包但不同适用域；错误、取消和资产版本处理一致且不引用彼此私有对象 |

关键数值算法使用固定版本 golden 输入与公开算子路径；mock 只验证端口合同，不替代 HALCON 26.05 真实适配验证。UI 截图、合成样本、单测与硬件/标准件/现场资格证据分别标注，不互相冒充。

## 15. 性能预算、可观测性和发布

每个消费者须在运行前冻结不可变 `BenchmarkProfile`，绑定硬件/OS/运行时、HALCON/AsunImage 与 adapter 版本、校准方法/资产 revision、输入 hash。负载按图像尺寸/数量/字节、采样点数、方法、并行度、资格端口正常/未知/撤销/失联状态、冷/热状态分桶。Profile 必须给出预热次数、测量次数、最低有效样本数、有限 deadline、最大输入/点数/驻留字节、并发/队列上限、吞吐观察窗口和阈值来源；冷启动另桶测量，热态执行固定预热且不把预热计入样本。只有 HALCON/接口文档明示的硬限制才作为不可调 API 边界并记录原始来源；其它输入规模和资源目标属于 Profile；未绑定目标时性能结论 NotEvaluated，仍受 §3/§9 明确软件硬上限约束。

分别测采样/观测提取、求解、独立验证、资产序列化/读写、资格解析和从接纳到 `ResourcesReleased` 的总时长；另测取消请求至真实停止、`OperationDrained` 和 lease 归还。记录阶段吞吐、队列深度/高水位、并发、托管/native 峰值及分配、handle 峰值和结果状态。无法通过公共接口观测的 native 资源标 `Unknown`，不得记零。通用分位、样本有效性、失败/删失及未排空规则按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)；本模块另区分 solver 无解、证书/资格失败、预算拒绝和 `DrainUnknown`。通过线只能来自已采纳消费者/客户 Profile，并绑定硬件、方法、输入和版本；无阈值标 NotEvaluated（TargetPending 原因）。

独立发布至少包括 Core、实际需要的适配器和可选 UI 包；各自锁定版本、依赖清单、格式兼容范围、变更说明、测试来源和 hash。发布流程为候选包 → 单元/契约/native Adapter 检查 → 双消费者离线接入 → 影子解析/并行对照 → 宿主批准升级 → 逐步替换。回退包及旧资产解析能力先验证；不删除旧版本数据，不改变客户验收基线。文档阶段不表示包、测试、现场精度或生产资格已经完成。

## 16. 第二消费者验收

消费者 A：独立相机校正/镜头工具提供相机与光学配置、二维参考靶观测和独立视场检查；调用 Core 生成并验证候选，宿主获取资产引用，再经 Resolve 检查原帧配置。消费者 B：独立离线二维计量工具只读解析已发布相机资产，按明确的平面/用途/配置使用，不依赖 A 的采集与标定页面；共同标定另有 §7.4 的structured-light A及reconstruction-3d B，专用Joint引用/实测几何/资格不能由二维资格推导。B 不直接依赖 A 的 ViewModel、数据库或配置类型。

验收须证明 Core/公共契约可由两个独立进程或宿主引用；同一资产存储格式可由双方读取，设备域不串用，二维资格不会授权离面 3D 测量；双方各自使用模拟存储测试和至少一组固定真实标准件/采集回放输入完成方法级验证；一个宿主取消、停止或卸载控件不影响另一宿主租约；双方对资产 hash、资格版本、失败码、未知和撤销呈现一致。模拟器和合成数据只证明软件契约，真实标准件精度与现场部署另立资格结果。

## 17. 自审和准入状态

二维 Core 唯一合同仍为 Module API Contract v0.2，Joint API v1 与 Camera Read API 1 的已接收类型/摘要/向量保持；本文及附录是同一权威。0.3.3-prep 本轮按完整架构方法范围补充 §7.3A 专用方法、§9.2.1 身份/拓扑证据、§9.2A 自动参数、§9.4 二维Adapter/局部平面读写和 §10.1–10.2 完整UI/三语恢复。已接收 C1/C2/C3/JC/CR 与 JA/JI限定内容状态不因新增规格而提升或撤回。跨FOV工作区/运动误差/多相机组事实归mosaic、解码归barcode、采集和物理真值归原Owner；模块内方法/参数/codec/失败恢复由本指导明确，不转交客户补设计。新增合同与既有工程规划独立相容，尚未进行产品构建/真实运行或生产验收。

### 17.1 DEV-GOV-010 §3.1 六项规格核对

| 条件 | 对应正文及可核对结果 | 当前接收状态 |
|---|---|---|
| 1 边界与第二消费者 | §1–2、§7.2A、§7.4.1/6、§9.3.4：二维工具 A/B 仍沿 v0.2；Joint 的 structured-light/reconstruction-3d 双 Host 与 Camera Read/mosaic 已列出增量边界，不抬高旧 Core 状态 | 主控已接收 CAL-C1/C2/C3/CAL-JC/CAL-CR 文档规格；CAL-JA 为固定路线/指导内容限定接收，CAL-JI 为公开交接指导内容限定接收 |
| 2 唯一 API/单位/错误/资源 | §3–6、§8–9、附录 A：v0.2，封闭单位/有符号坐标、准备/参数/候选/请求摘要投影、各入口预算/观察与后台排空、迟到任务所有权唯一；无 Owner 写入资格和设备动作 | 主控已接收 CAL-C1/C2/C3/CAL-JC/CAL-CR 文档规格；真实 adapter 签名不冒称已编译，JA/JI限定内容不改变此边界 |
| 3 无 UI 最小宿主 | §11、§16、§7.4.6A、§9.3.4：旧 Core BCL 双消费者及新增 Joint/Camera Read Synthetic 双 Host 均给出公开装配卡；无 HALCON 的夹具只验证协议 | CAL-C1/C2/C3/CAL-JC/CAL-CR 宿主规格已接收；新增 Host 尚未创建/运行 |
| 4 可判定全生命周期断言 | §12.1 CAL.CORE.01–18、§14、§7.4.7 CAL.JOINT.01–08、§9.3.4 CAL.READ.01–06：旧 Core 与新增增量的正常/错误/重复/并发/取消/超时/关闭/回退分别列出；真实检测另立 Golden | CAL-C1/C2/C3/CAL-JC/CAL-CR 文档规格已接收；增量只完成文档自审，尚未执行产品 harness |
| 5 BenchmarkProfile | §15：输入/版本/冷热/队列/内存/native/排空与 P50/P95/P99，通用统计按 DEV-GOV-010；目标缺失为 NotEvaluated | 主控已接收测量方法规格；目标值待消费者 Profile，尚无性能结果 |
| 6 唯一工程/测试/禁区/调用 | Core binding、§11/16：Core、BCL Exe、最小双 Host 和未来 adapter/Wpf 独立落点；本轮不创建工程 | 主控已接收 CAL-C1/C2/C3/CAL-JC/CAL-CR 工程/测试/范围/调用规格；实际开工仍须确认权威代码基线/分支，JA/JI不因内容接收获得实现资格 |

### 17.2 整模块切片门

| 切片 | 范围与真实接收对象 | 当前结论与仅阻本片的后续门 |
|---|---|---|
| CAL-C1 | DTO/单位/摘要/分区/引用/纯内存预检；A/B 无 UI 工具 | ModuleCoreImplementationReady（规格准备，主控已接收六项）；尚无 C# 构建/BCL Exe 结果 |
| CAL-C2 | Core 作业编排、模拟 solver/provider/workspace、资源/事件/取消/Stop/幂等 | ModuleCoreImplementationReady（规格准备，主控已接收六项）；CAL.CORE.01–18 的实际任务闩锁/资源验证尚未执行；模拟 solver 不证明相机/手眼/线扫算法通过 |
| CAL-C3 | 发布/原回执回查/只读资格/失效投影，模拟 Store/Qualification | ModuleCoreImplementationReady（规格准备，主控已接收六项）；真实持久化原子性、权威水位/产品提交复核仍是 Integration 门 |
| CAL-A1 | HALCON标准板/面阵division/polynomial/远心 | §7.1/7.2C/9.4已明确检测、实测注入、估计项、已解writer、文件roundtrip和独立检查；物理Profile值/公开调用编译/native Golden未完成，不抬高实现准入 |
| CAL-A2 | 无框圆点/棋盘、ROI+halo/身份 | §9.2.1/9.4补齐封闭身份内容/有限枚举/已资格圆姿态证据；缺实际可信边界/姿态/偏差/代表图与量化质量仅阻真实方法接收，不给猜测点号 |
| CAL-A3 | 线扫模型/恒速/第一行pose/时序 | §7.2C/9.4已明确模型、meter/row、注入、解读写与拒识；真实同步/行完整性/目标Profile/native标准件未执行，不阻无关Core |
| CAL-A4 | 专用方法总索引 | 五个已明确方法现拆为下面HE/SH/RAD/FF/DIS实施卡，唯一合同§7.3A；不再把内部DTO/算法/恢复欠项列为后续Owner；Joint仍独立JC/JA/JI |
| CAL-HE | 手眼/SCARA高度消歧 | §7.3A.1/2/6文档设计已补齐；真实机器人反馈/相机资格/接触高度/pose精度、C#与native/独立物理链未运行，不列为已接收Core |
| CAL-SH | 线激光特殊三维参考物 | §7.3A.1/3/6文档设计已补齐；真实disparity/四面/domain/参考物证书/native文件roundtrip/实体计量未运行 |
| CAL-RAD / CAL-FF | 相对响应/暗场平场 | §7.3A.1/4/6文档设计已补齐；真实稳定光学/曝光/均匀场/灰度域/校正执行/拒识/性能未运行 |
| CAL-DIS | DisplayOnly transfer | §7.3A.1/5/6文档设计已补齐；实际测量仪器/目标曲线/显示配置/独立LUT实测/资格未运行，不写OS/设备 |
| CAL-AUTO | 有界离线参数建议 | §9.2A请求/端口/评分/确认与过期完整；独立标注/代表图/真实Evaluator/软件harness及性能未运行，不列为已接收Core |
| CAL-LPR | 局部平面内容/读取 | §9.4独立增量合同/codec/读链完整；真实平面pose/证书/用途域/资格与C#接线未运行，不扩旧CameraRead DTO |
| CAL-JC | §7.4 Joint API v1值/摘要/端口/编排/完整Synthetic双Host；§7.4.6B为本轮独立增量 | 原已接收范围维持ModuleCoreImplementationReady（规格准备，六项已接收）；§7.4.6B资格绑定技术桥增量已获主控限定内容接收，四个软件oracle输出独立核对一致；0.3.0概念Host/直接黑心采样不作准入依据，真实资格Owner/消费者桥/C#编译/HALCON/Store/性能/物理现场门保持 |
| CAL-CR | §9.3 Camera Read API 1/固定solved format/公开codec/有限read/独立Synthetic双Host | ModuleCoreImplementationReady（规格准备，主控已接收六项）；不改已接收v0.2类型/接口/摘要；真实writer/Store/Qualification/mosaic桥另门 |
| CAL-JA | HALCON26.05成对实测求解/文件roundtrip/留出检查 | 固定算子/求解/文件路线及指导内容限定接收；真实native/C#、Golden、代表图、资源排空与file roundtrip尚未完成 |
| CAL-JI | structured-light/reconstruction-3d bridge/资格/物理域 | 公开交接指导内容限定接收；真实消费者bridge/Store/Qualification/样本/同步/物理Profile/证书/计量/资格水位/性能及现场结果仍待完成；不阻旧二维Core |
| CAL-W1 | 完整方法WPF/宿主展示/权限/三语 | §10.1/10.2补齐typed draft/bindings、Joint/专用/建议/Read、own-operation取消、迟到显示排空、全错误三语；真实presenter/WPF/UIA/原DPI与1920×1080未运行 |
| CAL-I1 | 真实 Store/资格 Owner/平台合同、消费者现场闭包 | 正式映射、权威事务、真实双消费者、性能/计量/现场结果独立关闭，不用模拟测试代替 |

整体状态维持 DesignReview / Prep；已接收Core及JA/JI限定内容保持原范围。新增设计补充不自动获得ModuleCoreImplementationReady/ImplementationSpecificationReady，更不代表代码/native/物理/WPF/集成完成。本轮只写本唯一指导，不创建产品/测试工程、脚本或报告，不修改消费者、共享文件、登记或外部原件。

### 17.3 完整批准方法范围的自审结论与精确外部门

**文档结论：本轮已补齐当前明确批准方法范围内可决定的软件设计，内部待设计项为0；这是唯一指导正文的可实施性结论，不是全部方法已实现/已接收Core/已通过物理验收。** 手眼/线激光/相对响应/平场/显示资产不再仅靠A4“待后续”占位；其专用合同/算法/参数域/独立验证/恢复/双消费者/代码测试落点已在§7.3A落定。标准靶/无框圆点/棋盘/面阵/线扫、多相机逐相机资产、相机—投影器、FOV边界、解读取和局部平面、自动参数与UI均在下表定位。未明确物理模型的其它3D、ICC/设备写入不属于已明确方法范围，不能凭该模块名称任意扩张或声称已有资格。

| 全范围能力 | 唯一实施章节 | 尚须取得的外部事实/运行结果及Owner |
|---|---|---|
| 资产/资格/发布回查/失效/恢复 | §3–6/8/9.1/12–16 | qualification原Owner的正式产品映射/决定水位与证据，storage原Owner耐久事务/原回执，宿主原Owner用途/激活与提交复核；模块Owner负责真实Adapter实现/并发/重启/排空，不把这项运行工作转成客户设计 |
| 靶型/身份/二维参数/实测注入 | §7.1/7.2C/9.2/9.2.1/9.4 | 参考件Owner点位/半径/平面度/温度/证书与注册身份；采集Owner独立边界或pose来源；计量/工程Owner代表集量化拒识/偏差/用途界，模块Owner真实cv2/Golden |
| 线扫/多相机/FOV分工 | §7.2/7.2A/7.2C/9.4 | 采集/设备Owner真实行时序/反馈/epoch/恒速/安装，mosaic原Owner工作区组关系/运动误差/跨FOV资格；本模块只逐相机局部资产，不另造组求解 |
| 手眼/线激光 | §7.2B/7.3A.2–3 | 机器人/设备Owner实际反馈/接触高度/同步/真实disparity；参考件/计量Owner真值/参考物/空间误差/有效域；模块Owner native/C#及file roundtrip |
| 投影共同标定/消费者桥 | §7.4 | structured-light原Owner采样/图样/命名层/实际投影栅格与同步，reconstruction-3d原Owner接线/重建用途，参考件/计量Owner实测靶/白环偏差/独立物理Plan/范围；qualification与storage原Owner事实，模块Owner真实decoder/native/桥运行 |
| 相对响应/平场/显示 | §7.3A.4–5 | 采集/设备Owner稳定曝光/暗亮/均匀光场/显示实际模式；计量/显示测量Owner参考值/仪器/目标曲线/独立测量/误差限；执行消费者Owner校正副本与源图隔离，模块Ownernative/软件/域验证 |
| 自动参数/解与局部平面读取 | §9.2A/9.3/9.4 | 工程/计量Owner独立标注/窗口依据/保留Validation组/实际平面pose/域；宿主Owner参数确认/修订；模块Owner真实writer/codec/Evaluator/双工具接线，qualification原Owner当前用途资格 |
| 完整UI/三语/键盘/关闭 | §10/10.1/10.2 | 展示模块/宿主Owner实现借用presenter/权限/主题，模块Owner真正WPF/DevExpress接线、1920×1080固定viewport/原DPI/UIA/三语/迟到display验收 |
| 性能/发布/现场 | §14–16/各方法卡/Core binding | 消费者Owner实际负载/设备/节拍/资源目标，模块OwnerP50/P95/P99/失败样本/取消到真实排空及双Host、现场计量/客户OwnerFAT/SAT与物理资格 |

第一次内容自审从每种方法的输入沿处理/输出/消费走正常和具体反例，修正calib-data不保存结果、SCARA双固定量gauge、相机已资格读取、delay-display实测绑定、flat零除/域与native图通道平均；第二次自审按无UI/typed UI各走取消/超时/迟到Stream/native/Dispose、原ID回查、两Host、版本与用途失配，修正参数搜索上限与拓扑上限混用、truth流入Evaluator、缺外部content读取端口、UI误发新Publish及已终结原ID重放被误当重新提交。有限内存oracle只核规定的链/flat/display/评分公式与边界，定向Markdown/引用/新增合同一致性检查只核文档；旧Joint/CameraRead/二维编码向量复用原有效结果，不重复宣称真实运行。

仍未执行：真实C#工程构建/BCL harness、AsunImage公共重载实际编译与HALCON/native、检测代表图/Golden/Replay/独立标准件、Writer/file roundtrip/Store崩溃恢复、资格与两个原消费者正式接线、完整WPF/三语/UIA/DPI、性能/长稳、HIL/计量/FAT/SAT/客户现场。实际代码开工仍须绑定权威仓库/分支或可审计快照并派发明确切片；本地无.git不阻文档工作。外部事实的缺失只阻依赖它的真实方法/资格，不能阻旧已接收纯Core，也不能由模块编造数值。

## 18. 权威来源和只读研究

- 独立模块边界与章节基准：[INDEPENDENT-MODULE-ARCHITECTURE.md](../INDEPENDENT-MODULE-ARCHITECTURE.md)
- 平台原模块：[PKG-015_Calibration.md](../../shared-modules/packages/PKG-015_Calibration.md)、[SM-009_calibration.md](../../shared-modules/modules/SM-009_calibration.md)
- 标定方法与资格边界：[DEV-MET-030](../../shared-modules/guidance/04-metrology/DEV-MET-030_Calibration与标定资格开发指导.md)、[DEV-MET-033](../../shared-modules/guidance/04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md)
- 模块隔离：[DEV-GOV-005](../../01-governance/DEV-GOV-005_模块独立性与复用标准.md)；Contract/Schema/State/Owner：[DEV-CONTRACT-002](../../13-contract-candidates/DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导.md)
- 视觉边界：[DEV-VIS-020](../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md)；HALCON 路线：[DEV-VIS-021](../../shared-modules/guidance/03-vision/DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md)
- HALCON 26.05 operator reference：本地 `halcon算子手册/operators/` 中 `calibrate_cameras.html`、`camera_calibration.html`、`set_calib_data_observ_points.html`、`find_calib_object.html`、`threshold.html`、`dyn_threshold.html`、`connection.html`、`select_shape.html`、`edges_sub_pix.html`、`fit_ellipse_contour_xld.html`、`saddle_points_sub_pix.html`、`calibrate_hand_eye.html`、`calibrate_sheet_of_light.html`、`gen_radial_distortion_map.html`、`map_image.html`、`image_points_to_world_plane.html`、`project_3d_point.html`。
- 2026-10-06 定向来源复核：`H:\docs\40-development\40-vision\标定与计量开发指导.md`（SHA-256 `6e55b1c00230ef35da466290b57feb533be8ef239f0ba95a384a3de53da81433`；限 §7/§8/§10 中区分设备运行环境与标定有效性的约束）及 `H:\docs\40-development\41-vision-platform\03-calibration-imaging\标定Artifact与有效性开发指导.md`（SHA-256 `96d8efef8118f3c9df4d17c49574d758851d8dbadd196d17ed72b595f1fc8cc2`；仅作 Artifact/适用性边界复核）。来源中的 HALCON 24.11 路线、制程/宿主流程、产品状态机、客户阈值及审批/激活结论均不随本条采纳；算子语义仍以本项目 26.05 手册为准。
- 只读来源：[PCBA AOI 标定 Artifact 与有效性指导（原件快照）](../../references/project-snapshots/PCBA-AOI/20261006/original/docs/40-development/41-vision-platform/03-calibration-imaging/标定Artifact与有效性开发指导.md)。来源基于 HALCON 24.11；本稿只采纳与 Profile/独立验证组织有关的增量，HALCON 行为以本项目本地 26.05 operator 页面为准。
- AsunControl 只读同类参考：`../../references/project-snapshots/AsunControl/20261004/original/Vision_CameraCalib\` 的标定指导与 `Calibration*` 类型；其 WinForms/.NET 8 参数默认、别名事件、路径存储和 `HTuple` 泄漏到 UI 的设计仅作为历史实现观察，不视为本模块契约或生产资格。目标实现只依据目标消费项目的 `ImageLibDotNet` 公共程序集/公开文档和编译核对，不读取或推断 AsunImage wrapper 内部。
- 用户参考只读快照：[500×500 FOV 拼接最终结论](../../references/user-notes/USER-003_500x500_FOV拼接最终结论_2026-10-06.md)，原路径 `H:\500x500_FOV拼接_最终结论.md`，SHA-256 `B4E1E924DCF56A723CA9701E31A89A154B09985AAD7A92428ECE1F99FD090FAF`。本模块只吸收“相机成像模型按兼容相机/光学配置跨生产 FOV 复用，不按 Tile 重复标定”及“标称靶标几何和实测几何应分开追溯”两项；工作区/运动误差场、实际轴反馈和 Tile Pose 归 mosaic。原件中的尺寸、点距、步距、误差和耗时均为示例，不作为本平台参数；未核验的运行算子/精度结论不采纳。

### 18.1 HALCON 26.05 算子资料入口

实现涉及标定算子时，使用项目内 [halcon算子手册/operators](../../../halcon算子手册/operators/) 作为目标版本 26.05 的资料入口；具体算子、参数、线程、资源和取消语义以目标手册为准，仅在 C# 参数类型/重载/封送确有歧义时核公共签名或消费工程编译。


### 18.2 AsunMeasure 参考采纳与标定资产边界（2026-10-04）

快照中的 `CalibrationWorkflowContracts`、`CalibrationWorkflowService`、`CalibrationAffineSolver`、`CalibrationSnapshotValidator` 和残差投影测试可借鉴阶段 revision、输入快照、残差/精度报告、Publish/Activate/Retire 以及失败回退的组织方式。平台必须把这些事实写入本指导规定的资产 Owner、能力声明和回执，不能由 UI 或文件名推断资格。

旧标定参数、文件格式、默认值、WinForms 控件和旧 AsunImage 句柄不直接迁移；目标签名、单位、坐标方向、HALCON 26.05 能力和真实标定板/Golden 证据仍是独立准入门。

### 18.3 本轮方法与 UI 资料采纳

HALCON 26.05 已直接读取 [相机模型章](../../../halcon算子手册/operators/toc_calibration.html)、[set_calib_data](../../../halcon算子手册/operators/set_calib_data.html)、[create_calib_data](../../../halcon算子手册/operators/create_calib_data.html)、[实测对象点表](../../../halcon算子手册/operators/set_calib_data_calib_object.html)、[ellipse 拟合](../../../halcon算子手册/operators/fit_ellipse_contour_xld.html)、[圆的两解与边缘偏差](../../../halcon算子手册/operators/get_circle_pose.html)、[鞍点](../../../halcon算子手册/operators/saddle_points_sub_pix.html)、[姿态初始化](../../../halcon算子手册/operators/vector_to_pose.html)、[结构光专用标定](../../../halcon算子手册/operators/calibrate_sheet_of_light.html)。采纳模型参数/可估计项、成组观测注入、实测坐标参与求解、线扫 meter/row 与第一行 pose、透视圆两解/边缘偏差、geotukey 忽略 Iterations、结构光特殊三维靶等限制；这些资料不证明本模块 C# 调用/算法/精度已经运行通过。

OpenCV 4.12.0 固定 commit `49486f61fb25722cbcf586b7f4320921d46fb38e`：实际阅读 [chessboard.cpp](https://github.com/opencv/opencv/blob/49486f61fb25722cbcf586b7f4320921d46fb38e/modules/calib3d/src/chessboard.cpp)（SHA-256 `3c02377401015e4d15420b042ba9eb88dd4d95938b2a74c5303d7803f4f48752`；findChessboardCornersSB 与局部对称性）、[test_chesscorners.cpp](https://github.com/opencv/opencv/blob/49486f61fb25722cbcf586b7f4320921d46fb38e/modules/calib3d/test/test_chesscorners.cpp)（`0e4e3bc81afc21303692bc837817c38f7e617eb1a84aa8bc4d16da26a0d6cdab`；拓扑/误差/marker 回归）、同 commit LICENSE（Apache-2.0；`cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`）与 calib3d/CMakeLists（`285d11f88c466101283da9d9eb5af5b6645fd5b9fe5e2d4e3a7ff1677278291c`；依赖 imgproc/features2d/flann，可选 LAPACK/highgui debug）。只采纳有界候选搜索、检测元数据与稳定身份分开、合成 ground truth 和标记回归的测试思想；不复制代码/魔数、不引入 OpenCV 平行生产算法。编码 marker 的唯一性不等于纯周期靶唯一性；未运行上游测试/性能，不采纳其生产精度结论。

本机 DevExpress 25.2.3 官方 XML 路径模板为 `C:/Program Files/DevExpress 25.2/Components/Offline Packages/<package>/25.2.3/lib/net8.0-windows/DevExpress.Xpf.<Module>.v25.2.xml`。已读 Docking 的 AllowFloat/AllowClose/LayoutPanel/DocumentGroup 与布局 Stream API（SHA-256 `b11b45dd7afc27b5e16b679a6a9e2e4291ecd13cb1f8e1b7c0fbe4e94a64477f`）、Grid 的 GridControl/TableView（`7537e3db16162155eda70058baccf40a6731f6dc9851ad31d382332c39c3d6bd`）、Charts 的 ChartControl/XYDiagram2D/PointSeries2D/SeriesPoint.Tag（`2e80660ea0316294482e5b45096cc23c52250243e12551e84c117f692445bfb0`）、Core 的主题及 BarItem.SuperTip（`cf99d297b336a80f2361fa8bb79369434a6a10b9426efa670d636803433e8196`）、PropertyGrid 的 SelectedObject/PropertyDefinitions/ShowProperties（`0e0cb8a0503889f13cd86fa4d5db7cbb975c9c4f4506dfea8d681f68fc4a65c9`）。无可用 dxdocs 接口，在线官方站返回 403，故复用本机匹配版本官方 API 说明；没有据此宣称已验证真实 WPF。AsunMeasure 的 CalibrationAffineWorkflowTests 只采纳输入变更失效、保存竞争与读回内容比对断言，不迁移 PixelToStage 产品 Owner 或激活流程。

### 18.4 共同标定定向研究与取舍（2026-10-11）

本次窄修只补此前未读的procam局部映射证据，不重新下载 §18.3/18.4 已读的旧固定资料。HALCON 26.05 [vector_to_proj_hom_mat2d](../../../halcon算子手册/operators/vector_to_proj_hom_mat2d.html)给至少4点及normalized_dlt/gold_standard取舍、row作为x/col作为y；[projective_trans_point_2d](../../../halcon算子手册/operators/projective_trans_point_2d.html)给纯点homogeneous变换；[projective_trans_pixel](../../../halcon算子手册/operators/projective_trans_pixel.html)给其与point坐标原点差，混warp/region才须0.5平移。[gen_region_polygon_filled](../../../halcon算子手册/operators/gen_region_polygon_filled.html)明确round亚像素，因此局部中心凸包包含不能按region近似通过；本节固定纯点坐标/有限值包含校验，不调用图像warp。官方normalized_dlt是固定拟合Owner，C#仅重算矩阵预测/值限额/包含与审计，不新增OpenCV拟合实现。

| 新读固定来源 | 实际读到的代码/测试、采纳及限制 |
|---|---|
| kamino410/procam-calibration [calibrate.py](https://github.com/kamino410/procam-calibration/blob/09e58d5b17c390fa0912e0f7191c1a0772aeae14/calibrate.py) | commit `09e58d5b17c390fa0912e0f7191c1a0772aeae14`，SHA-256 `afd852daef8b391b0d9165347047a09005ea36d5e42a4952630f9e2b54bb8efc`；实际读取109/133–171：white图检测corner、邻域white-black阈值筛解码点、局部findHomography后预测dark corner的projector亚像素坐标；185–218分别camera/projector/stereo求解。借“亮区估局部映射，不直接取暗点”的数据流；其width/180 patch魔数、未明示图边界（Python负index可能绕回）、支持下限/无独立中心check/裸RMSE不迁入；本版改为固定Profile环带/四象限/凸包/独立留出/inner-outer与采样偏差资格。读取不是认定上游工业合格 |
| 同commit [README](https://github.com/kamino410/procam-calibration/blob/09e58d5b17c390fa0912e0f7191c1a0772aeae14/README.md) / [LICENSE](https://github.com/kamino410/procam-calibration/blob/09e58d5b17c390fa0912e0f7191c1a0772aeae14/LICENSE) | SHA-256 `195d63d26f0a19abe58ddbd3531ec52c076bc22ada5202f04c34aa1034110aef` / `d43ebf8b8396513b6c0839305d6c7c87ed94259bddda699501a989a4c3420f71`；MIT，源码imports Python3/OpenCV-contrib/NumPy（上游未固定依赖版本）；README引用Moreno/Taubin2012 local homography论文，只用于原作者路线归因，不把README/论文题名当运行证据。上游目录有sample_data无专用独立中心偏差/现场资格测试。本轮不复制Python/引依赖/执行其samples |
| OpenCV固定commit [test_homography.cpp](https://github.com/opencv/opencv/blob/49486f61fb25722cbcf586b7f4320921d46fb38e/modules/calib3d/test/test_homography.cpp) | SHA-256 `0639623204245f813982ae64b9e22158dea12f75d0766b3c2b53dbb8c53af136`；实际读取accuracy、EKcase 601–609的透视预测/最大误差断言、minPoints两点拒绝、not_normalized返回矩阵与固定参考。借非整数坐标/最小点/误差与矩阵归一回归，阈值不迁入；仅数学test不能证明黑心物理偏差。许可/依赖复用已读 §18.3 OpenCV证据 |
| OpenCV contrib固定commit [projectorcalibration.cpp](https://github.com/opencv/opencv_contrib/blob/d943e1d61c8bc556a13783e1546ee7c1a9e0b1cf/modules/structured_light/samples/projectorcalibration.cpp) | SHA-256 `e9b2a9625d81d64cfa46b88c2e52891e4d9b0c5e27b9cc15b06f4e891dbfbd8f`；实际275–294 camera→plane→projector→stereo、375–410用平面/逆相机矩阵给投影点world。这是sample而非资格test，本版保留实测靶点与联合多视图Owner，不照搬其理想Z=0/默认参数与无独立资格路线；文件BSD风格头，依赖OpenCV calib3d/highgui等，不复制代码 |

上述sources只补方法与断言，未运行上游/OpenCV/HALCON/native/实体材质验证。采样路线可由实际白背景和黑圆平面板执行，低信号黑中心不再是必需前置；支持边界准确限定于共面、可解码白环、近似偏差经过独立证据验证的域。材料/光学/Profile实测值仍是CAL-JA/JI门，不转成Core不能构造的内部门。

直接阅读本地 HALCON 26.05 [多视图标定](../../../halcon算子手册/operators/toc_calibration_multiview.html)、[calibrate_cameras](../../../halcon算子手册/operators/calibrate_cameras.html)、[成组点观测](../../../halcon算子手册/operators/set_calib_data_observ_points.html)、[get_calib_data](../../../halcon算子手册/operators/get_calib_data.html)、[camera_setup参数/pose](../../../halcon算子手册/operators/set_camera_setup_cam_param.html)、[参考frame](../../../halcon算子手册/operators/set_camera_setup_param.html)、[camera_setup读取](../../../halcon算子手册/operators/get_camera_setup_param.html)、[结构光参数](../../../halcon算子手册/operators/set_structured_light_model_param.html)、[解码结果](../../../halcon算子手册/operators/get_structured_light_object.html)、[结果参数查询](../../../halcon算子手册/operators/get_structured_light_model_param.html)、[结构光重建](../../../halcon算子手册/operators/reconstruct_surface_structured_light.html)、[亚像素取值](../../../halcon算子手册/operators/get_grayval_interpolated.html)、[姿态初始化](../../../halcon算子手册/operators/vector_to_pose.html)、[ray](../../../halcon算子手册/operators/get_line_of_sight.html)、[双ray交会](../../../halcon算子手册/operators/intersect_lines_of_sight.html)、[写文件](../../../halcon算子手册/operators/write_camera_setup_model.html)、[读文件](../../../halcon算子手册/operators/read_camera_setup_model.html)、[序列化](../../../halcon算子手册/operators/serialize_camera_setup_model.html)。本节不迁移旧24.11行为。官方允许投影器 division/polynomial、相机多种非hypercentric面阵模型；首版选两端division控制可观测/参数与验证范围，未来扩模型需另Profile与同样本比较，不宣称其余官方不支持。

方案比较：单方向Gray整数解码不能提供joint row+column/subpixel；普通二维homography不提供相机/投影器三维内外参；sheet-of-light特殊物路线和deflectometry镜面路线物理模型不同。采用both hybrid有名层→白区局部映射→实测点成对观测→HALCON两相机校准→camera0参考camera_setup文件→独立holdout/计量资格。它复用现producer/decoder Owner和HALCON多视图求解，不引入平行优化器。0.3.0稿黑圆中心四邻直接采样会整板低信号，本轮改为白区局部映射；仍不能宣称所有现有靶材质直接可用；客户靶材质/稳定图样/真实组能否满足Profile由代表集验证，缺口仅阻native/physical接收。

| 固定源码/测试（本轮只读） | 身份、实际采纳与限制 |
|---|---|
| OpenCV 4.12.0 [calibration.cpp](https://github.com/opencv/opencv/blob/49486f61fb25722cbcf586b7f4320921d46fb38e/modules/calib3d/src/calibration.cpp) | commit `49486f61fb25722cbcf586b7f4320921d46fb38e`，SHA-256 `d5da59d74ff69d186d0ae75a48f6439a68bfdd0599846ae7316d41a8d46654c8`；实际读stereoCalibrateImpl内固定/估计内参、SAME_FOCAL_LENGTH和两端projectPoints残差。借分端/per-view与固定参数测试思想，禁止无事实共享焦距/pitch；不复制优化器/系数模型，OpenCV畸变不能填HALCON向量 |
| 同commit [test_cameracalibration.cpp](https://github.com/opencv/opencv/blob/49486f61fb25722cbcf586b7f4320921d46fb38e/modules/calib3d/test/test_cameracalibration.cpp) | SHA-256 `e69bfcdcbe8f37e893bc3dc5d6a0c4348b8706a7f54bce4fbe714a66b88afdd9`；实际读1771–1815逐view左右误差、2064–2075 extrinsic guess重跑非增误差及2端err维度断言。借误差形状/初值回归思想，不采纳重跑优化为生产策略；这些测试不证明HALCON或现场joint资格 |
| OpenCV contrib 4.12.0 [graycodepattern.cpp](https://github.com/opencv/opencv_contrib/blob/d943e1d61c8bc556a13783e1546ee7c1a9e0b1cf/modules/structured_light/src/graycodepattern.cpp) / [test_getProjPixel.cpp](https://github.com/opencv/opencv_contrib/blob/d943e1d61c8bc556a13783e1546ee7c1a9e0b1cf/modules/structured_light/test/test_getProjPixel.cpp) | commit `d943e1d61c8bc556a13783e1546ee7c1a9e0b1cf`，SHA-256分别 `eb2840559d4ee81d49a589376f8f0e2c8760bda3bd86e0630879d5ce145e2a7e` / `846a2937852a009e124f95f37ef1aadb1e248f520cdddf15b7cb6734a3b441b0`；借投影坐标roundtrip/越界/正反图阈值拒识测试。合成整数Gray roundtrip不能代替HALCON phase subpixel、实体标定或独立计量 |

OpenCV根 [LICENSE](https://github.com/opencv/opencv/blob/49486f61fb25722cbcf586b7f4320921d46fb38e/LICENSE)（Apache-2.0，SHA-256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`）和 [calib3d/CMakeLists](https://github.com/opencv/opencv/blob/49486f61fb25722cbcf586b7f4320921d46fb38e/modules/calib3d/CMakeLists.txt)（`285d11f88c466101283da9d9eb5af5b6645fd5b9fe5e2d4e3a7ff1677278291c`，依赖imgproc/features2d/flann、可选LAPACK/highgui）已读；源文件保留旧BSD风格头，若未来复制须同时保留相应许可。contrib依赖/许可证据复用structured-light指导 §16.3，不重建快照/引入OpenCV依赖。本轮未运行上游测试、HALCON、C#、性能、Golden或现场采集；源码采纳只是合同/断言设计依据。

### 18.5 完整范围补充的官方依据与取舍（2026-10-11）

复用§18.3/18.4已有固定源码、许可证/依赖和测试思想，不重新下载或运行上游。新增方法仍使用项目HALCON26.05官方Operator Description/Parameters/Execution Information；以下SHA-256是本地原页完整字节身份，实际采纳为列出的定向语义，不声明其示例/default等于本项目物理Profile。display transfer二分反查与身份枚举是纯值/身份事务，不另造视觉优化器；flat/radiometric主计算仍HALCON，不引OpenCV生产依赖。未选择gamma_image代替显示器测量，不选择1d_histograms处理运动场景、polynomial补缺灰度域，也不把div_image零除行为当有效校正。比较与适用性局限留在§7.3A，真实同样本/错误接受拒绝/性能仍未运行。

| 实际采纳/限制 | 目标26.05原页及SHA-256 |
|---|---|
| 原生参数/pose输入输出；calib-data只保存输入、不保存求解结果 | [read_cam_par](../../../halcon算子手册/operators/read_cam_par.html) `af01d8b8f3346043bcb0c9caf300540682b586c5e0cb85fc9459c524856881d9`；[write_cam_par](../../../halcon算子手册/operators/write_cam_par.html) `4ec41eaf7eea06ba94b59e397c1cd1d73d5b25c66815855ea027e13d73d3cb4c`；[read_pose](../../../halcon算子手册/operators/read_pose.html) `c22ccc28f6a4c3029527a82dac61978430a3a2d59b5e099721b08887b1f5b8fa`；[write_pose](../../../halcon算子手册/operators/write_pose.html) `422f5ba63b81b0e27630615419857673c3df64509e38204be2ddac349edd911c`；[read_calib_data](../../../halcon算子手册/operators/read_calib_data.html) `de6be5d9b947ec1a31476c92728c5a2a8bb0b1ea42bb5d650ee6c7a55fd6eace`；[write_calib_data](../../../halcon算子手册/operators/write_calib_data.html) `a06f04fdc5219afdd28657f7c14e80bbd80784d20cb3d02c71f1a8f85c41eb6e` |
| 手眼拓扑/generic sensor/固定量/SCARA local-Z消歧 | [calibrate_hand_eye](../../../halcon算子手册/operators/calibrate_hand_eye.html) `cb14ee6aebe0ab94a81e6edb7e1c983bb8c1a35d3d2f71aaabe0a41b46104b35`；[create_calib_data](../../../halcon算子手册/operators/create_calib_data.html) `32aad47f41369a5292ce86e063900b0d1c1fab0723627f7d4e5bd866973bc683`；[get_calib_data](../../../halcon算子手册/operators/get_calib_data.html) `bd86ddd7b58962d65c398f5b7700b353920b0c9f979bf416e3629233fba30342`；[set_calib_data_observ_pose](../../../halcon算子手册/operators/set_calib_data_observ_pose.html) `b9c058246c1718392e5d710f550f8b72476926e83aeef3ea81ed90c998279168`；[set_origin_pose](../../../halcon算子手册/operators/set_origin_pose.html) `d00bebb52e2fbab55f614ea074a974703c2a518e2fbaee6679920568db7a4c8f` |
| 特殊物/单disparity/参数方向/xyz独立检查及model文件 | [calibrate_sheet_of_light](../../../halcon算子手册/operators/calibrate_sheet_of_light.html) `2981afa7a547316b26f68563a3034fa6707051bf7fbcdcbd9aedc0fa847cd06e`；[create_sheet_of_light_model](../../../halcon算子手册/operators/create_sheet_of_light_model.html) `326eb6633535a5d29387a54bdae3c9dfd1efa77ffa410576dcd9f260ae0ddb5a`；[set_sheet_of_light_param](../../../halcon算子手册/operators/set_sheet_of_light_param.html) `b4a7acbc5bd0ffba210540a2798c99757e83de3a44365ba89bb23234ccdba4ca`；[get_sheet_of_light_param](../../../halcon算子手册/operators/get_sheet_of_light_param.html) `8e155c5e8c2f61d20287f11f8e70b06f202478c029e3588ddf787fa102d425b9`；[set_profile_sheet_of_light](../../../halcon算子手册/operators/set_profile_sheet_of_light.html) `ecfee9046b79030bf72ceb186a7cc3a85e7614fe9ba6754f4d10ff3eb0405d8b`；[apply_sheet_of_light_calibration](../../../halcon算子手册/operators/apply_sheet_of_light_calibration.html) `6b8e3885c84f5d1300b6ae9a7f96231acf715624bfcd12393497ee0fa721a4a3`；[get_sheet_of_light_result](../../../halcon算子手册/operators/get_sheet_of_light_result.html) `1dcbcb82ea752adb305d3b904c6cb3319e124164eaa3fa9d6083357007b0eb6f`；[read_sheet_of_light_model](../../../halcon算子手册/operators/read_sheet_of_light_model.html) `a79cb2263d98f5ff076969c68a4dff145e570c164bffad52e6540206aefd4d45`；[write_sheet_of_light_model](../../../halcon算子手册/operators/write_sheet_of_light_model.html) `ee70274b58a32418d29d7ab65c0e4f536da843459cd03a0a53dd9a6fec115da5` |
| 相对响应/曝光比/离散256LUT/灰度覆盖，不取得绝对能量 | [radiometric_self_calibration](../../../halcon算子手册/operators/radiometric_self_calibration.html) `ebe733406375dbf66c3b1d29005f2484f0ad8b9f9bcece9b075c99ebb229842a`；[lut_trans](../../../halcon算子手册/operators/lut_trans.html) `27139faf00a54b940b6f34ffc3d2049a8946f224fe84824622b51b767c8666c6`；[gray_histo_abs](../../../halcon算子手册/operators/gray_histo_abs.html) `f7b347ad5f33d3e76637a92c346df349edff8657abeb9b25a5de788bfd7cfc9f`；[histo_2dim](../../../halcon算子手册/operators/histo_2dim.html) `0f76e8876ca442f1f18ccf791d092eb2461f3e7e46ffd21089e50aaee736842c` |
| real域暗亮均值/差/有效分母/增益；零除为0须预拒绝 | [append_channel](../../../halcon算子手册/operators/append_channel.html) `ee61084767d5621c0a595609914a024c63960b87dba8051d0aaa8bdf3fcb1dd3`；[mean_n](../../../halcon算子手册/operators/mean_n.html) `e258472ad7c318ade054aa6f4002fe352371598c40117af166ca8abe9e5c3ba0`；[convert_image_type](../../../halcon算子手册/operators/convert_image_type.html) `4e7ea41cc5be0f7e5dc4e95fc98a49441e8eb03788bf45c36d46776832d2312d`；[sub_image](../../../halcon算子手册/operators/sub_image.html) `f4ccfc5a4f2c44e7e9ba846e31f6a1c2d7b402c43557cf42ae541a58592dd9f3`；[div_image](../../../halcon算子手册/operators/div_image.html) `83406a1f20cb3bccbfd6bfcede5b98888cbca88359c98d207ccb47dffae8a15f`；[mult_image](../../../halcon算子手册/operators/mult_image.html) `7a8adb0899467312fcf2a0b527a66b97c55a995457e6ea97909ecea9f33aa6f8`；[intensity](../../../halcon算子手册/operators/intensity.html) `9fd38efcae33058a8cf955d6e8980ff61e03b965505d7de3014771e283fe8f43` |

DevExpress API继续复用§18.3已读的本机25.2.3官方XML及原hash；本会话当前无dxdocs可调用能力，不再重复在线403尝试。该限制只描述文档来源，不成为依赖安装/授权/兼容门。既有SDK/视觉公开签名实际编译、native/文件/显示行为与物理测量仍由对应实现切片验证，本轮未执行。

## 附录 A：模块核心 API Contract v0.2（核心语义冻结；逐切片准入）

本节定义本独立模块的核心代码边界，优先于正文中仅针对产品集成的待绑定映射。本文已给出的公开类型、方法、事件、错误键、状态、参数表和代码形状，作为对应切片获准后唯一实施依据；本附录的存在不代表代码准入、HALCON 适配器通过或生产资格通过。实现者不得另造第二套核心 DTO、状态机或错误语义。

- `Module API Contract v0.2` 只覆盖无产品事实写入的 Core、Simulator 和显式 Adapter Port。它不把平台 C-01～C-08、客户工艺阈值、最终放行、产品数据库字段或厂商私有类型冻结为模块 API。
- “候选”只表示 `CandidateArtifactRef` 生命周期状态，不再作为泛称入口、结果别名或可持久化 Qualified 资产的替代词。平台 Schema 映射、序列化、Owner、生产资格和客户 Profile 仍需按职责绑定；本模块 Core 的字段/方法/事件/错误/资源语义按本节和正文冻结，任何未定义操作必须先补回本指导再编码。
- 适配器按 HALCON 26.05 `halcon算子手册/operators` 经 `ImageLibDotNet.cv2` 实施，并在目标消费项目编译和验证；仅对实际 C# 参数/重载/封送歧义核对公共签名。未解决的映射只阻断该适配器或 UI/硬件切片，不阻断可替换的 Core、Simulator 和契约测试，也不触发算子可用性或依赖准入复核。
- Contract 状态：CAL-C1/C2/C3/CAL-JC/CAL-CR 为 `ContractFrozen / ModuleCoreImplementationReady`（CAL-C1/C2/C3 于2026-10-09、CAL-JC/CAL-CR 于2026-10-11由主控接收六项文档规格）；CAL-JA 的固定路线/指导内容与 CAL-JI 的公开交接指导内容为限定接收，其余切片按 §17.2 保留各自后续门。本文不因此声明代码、适配器、集成或生产资格已通过。

### A.1 Core API、类型和映射边界

Core 唯一命名空间为 `Asun.Modules.CalibrationAssets`。正文 §3、§4 已定义通用值、请求组、主要结果、方法签名、状态、错误、资源与 Owner 端口。其类型按如下职责成组；开发者不得另造 DTO 或把下游 Owner 数据复制成第二权威：

| Contract 类型组 | 公开类型/入口 | Core 所有权和边界 |
|---|---|---|
| 稳定值 | §3.1 `Pixel`、`PixelSize`、`Length`、`Angle`、`Temperature`、`DurationLimit`、`Digest`、`RevisionId`、`AssetId`、`CalibrationSessionId`；§3.2 的 `CalibrationMethodId`、`MethodProfileRef`、`CameraModelId`、设备/光学指纹、设备快照宽高/ROI、`ObservedPoint`、`ObservationId`、`ReferencePointId`、`RigidPose`、`PartitionPlan`、`ValidationPlanRef` 及其封闭单位/枚举 | 值校验、单位完整性与输入摘要由 Core 拥有；物理/证书真值仍由参考件 Owner 提供 |
| 作业输入 | `PrepareRequest`、`SolveRequest`、`ValidationRequest`、`PublishRequest`、`ResolveRequest`、`DrainRequest`；`InvalidationWatchRequest`、`CalibrationExecutionBudget` | 不可变快照；图像/观测内容通过显式 lease/provider 端口读取，DTO 不装裸 native 句柄或无界像素数组 |
| 求解与验证结果 | `PrepareResult`、`CalibrationSolveResult`、`CalibrationProgress`、`ValidationResult`、`CalibrationArtifact` | Core 拥有候选和 `PublishedUnqualified` 内容、计算证据、依赖闭包和运行状态；验证计划/实际物理阈值由独立资格 Owner 提供 |
| 用途解析和副作用回执 | `ApplicabilityResult`、`PublishReceipt`、`ReceiptQueryResult`、`OperationStateResult`、`OperationCompletion`、`DrainResult`、`CalibrationErrorCode`、`CalibrationEvent` | 解析结果是本次只读三态；发布只写 `PublishedUnqualified`；`QualifiedAssetRef` 只能来自资格 Owner 的只读决定；绑定与资格事实由原 Owner 持有 |
| 唯一异步服务入口 | `PrepareAsync(PrepareRequest, CancellationToken)`、`SolveAsync(SolveRequest, IProgress<CalibrationProgress>?, CancellationToken)`、`ValidateAsync(ValidationRequest, CancellationToken)`、`PublishAsync(PublishRequest, CancellationToken)`、`ResolveAsync(ResolveRequest, CancellationToken)`、`StopAsync(DrainRequest, CancellationToken)`、`QueryPublishReceiptAsync`、`ReadEvents`、`GetOperationState`、`WatchInvalidationsAsync` | 与正文 §4.1 签名完全一致；异步业务操作返回 `ValueTask<T>`，其余按 §4.1，不得另建同步/native 入口 |

```csharp
namespace Asun.Modules.CalibrationAssets;

public interface ICalibrationAssetsModule : IAsyncDisposable
{
    ValueTask<PrepareResult> PrepareAsync(PrepareRequest request, CancellationToken cancellationToken);
    ValueTask<CalibrationSolveResult> SolveAsync(
        SolveRequest request, IProgress<CalibrationProgress>? progress, CancellationToken cancellationToken);
    ValueTask<ValidationResult> ValidateAsync(ValidationRequest request, CancellationToken cancellationToken);
    ValueTask<PublishReceipt> PublishAsync(PublishRequest request, CancellationToken cancellationToken);
    ValueTask<ApplicabilityResult> ResolveAsync(ResolveRequest request, CancellationToken cancellationToken);
    ValueTask<ReceiptQueryResult> QueryPublishReceiptAsync(ReceiptQueryRequest request, CancellationToken cancellationToken);
    EventReadResult ReadEvents(EventReadRequest request);
    OperationStateResult GetOperationState(OperationId operationId);
    IAsyncEnumerable<InvalidationNotice> WatchInvalidationsAsync(InvalidationWatchRequest request, CancellationToken cancellationToken);
    ValueTask<DrainResult> StopAsync(DrainRequest request, CancellationToken cancellationToken);
}
```

模块实例由构造工厂 `CalibrationAssetsModule.Create(CalibrationAssetsOptions, CalibrationAssetsAdapters)` 建立；`CalibrationAssetsAdapters` 字段唯一见 §9.1，使用 ICalibrationSolverScopeFactory 创建由模块拥有的 solver scope；注入 provider/reference/gate/store/qualification/diagnostics，不再注入 singleton solver。Binding/激活端口不属于 Core v0.2；需要时由宿主在模块外组合。缺失 Store 只关闭 Publish，缺失 QualificationPort 只使 Resolve 返回 `CAL-106 QualificationUnknown`，不可由全局服务定位或静态默认启用。`Create` 只校验依赖与能力声明，不自动连接设备或激活资产。

状态、错误与事件顺序以正文 §4.2–§5 为唯一详述；`SolveStatus`、`ValidationStatus`、`PublishStatus`、`ApplicabilityStatus` 是封闭类型，作业状态不替代资格状态，`ApplicabilityStatus` 只允许 `Applicable/NotApplicable/Unknown`。Prepare/Solve/Validate/Publish/Resolve/ReceiptQuery 请求携带 ContractRevision="0.2"，每项均显式 Budget；Watch/Drain/内存查询使用已建立实例合同版本。结果 Completion 明确区分有限观察 DrainPending 与真实 ResourcesReleased，字段按 §3/§6.1，不增造不存在的 ContractRevision。`SolveAsync` 是唯一产生 `CandidateArtifactRef` 的入口；`PublishAsync` 只接受该候选并产生 `PublishedArtifactRef`；`ResolveAsync` 只接受已发布引用并在外部资格为 `Qualified` 时产生 `QualifiedAssetRef`。附录中的类型分组给出唯一归属索引，正文 §3.4–3.6、§9 是字段及端口签名权威；不能由开发者补猜第二套入口或把任一引用类型互换。CAL-C1/C2/C3/CAL-JC/CAL-CR 的六项文档规格已由主控接收，状态为 ModuleCoreImplementationReady（仅规格准备）；CAL-JA/JI 仅为固定路线/公开交接内容限定接收，不获得真实实现资格；整体仍 DesignReview / Prep，A1–A4/W1/I1 按 §17.2 保留各自后续门，真实构建/算法/UI/性能/物理验收均未执行。

Joint API v1 的专用类型、五入口、Store/Qualification/notification和双Host只以 §7.4 为权威，不是本附录v0.2的兼容别名。Camera Read API 1 的增量仅按 §9.3 管理；CAL-JC/CAL-CR 的文档规格已按 §17.2 由主控接收，复用工程仍在 `Joint/`、`CameraRead/` 子目录实现，不改CAL-C1/C2/C3的类型与固定向量；JA/JI的限定内容接收不代表代码、适配器、集成或生产资格通过。

依赖 Owner：观测源 Owner 提供不可变数据及租约；求解器适配器执行声明的方法并返回计算证据；标定资产模块持有候选/资产格式和适用性评估；资格 Owner 决定资格；资产 Store Owner 执行内容持久化；Binding Owner 管理当前绑定。Core 不创建资格、批准者或生产事实。

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

- 准入路径 NewProjectRequired；Core 唯一工程 `src/Modules/calibration-assets/Asun.Modules.CalibrationAssets.Core/Asun.Modules.CalibrationAssets.Core.csproj`，namespace `Asun.Modules.CalibrationAssets`，net10.0，无 UI/产品/AsunImage 直接引用。测试唯一工程 `tests/Modules/calibration-assets/Asun.Modules.CalibrationAssets.Core.Tests/Asun.Modules.CalibrationAssets.Core.Tests.csproj`，net10.0、OutputType=Exe、Microsoft.NET.Sdk，仅引用 Core 和 BCL；采用仓库既有确定性断言约定，不临时选测试包。
- Core 构建命令：`dotnet build src/Modules/calibration-assets/Asun.Modules.CalibrationAssets.Core/Asun.Modules.CalibrationAssets.Core.csproj -c Release`；测试命令：`dotnet run --project tests/Modules/calibration-assets/Asun.Modules.CalibrationAssets.Core.Tests/Asun.Modules.CalibrationAssets.Core.Tests.csproj -c Release`。入口执行 CAL.CORE.01–18 及相应 §14 全部必需断言，任一失败、超时、未完成或跳过退出非零；全部完成且资源归还才为 0。dotnet test 无输出不能代替 Exe 测试。
- 最小两个无 UI Host 固定在测试工程 `Consumers/CameraToolHost.cs` 与 `Consumers/OfflineMetrologyHost.cs`，独立构造各自模块/参数/依赖，A 走 Prepare→Solve→Validate→Publish，B 独立 Resolve/失效观察；二者仅共享外部显式 Store/ExecutionGate，不引用彼此类或 UI。测试入口串行及双实例并发调用二者，按 §16 验证。模拟数据不是现场计量证据，真实独立进程接入另属 CAL-I1。
- Core 切片允许写入只有上述 Core/测试目录；所有项目目前均为计划落点，未创建。后续独立适配目录固定为 `src/Modules/calibration-assets/Asun.Modules.CalibrationAssets.AsunImageAdapter/`、`src/Modules/calibration-assets/Asun.Modules.CalibrationAssets.PersistenceAdapter/`、`src/Modules/calibration-assets/Asun.Modules.CalibrationAssets.Wpf/`，相应测试在 `tests/Modules/calibration-assets/Asun.Modules.CalibrationAssets.AsunImageAdapter.Tests/`、`Asun.Modules.CalibrationAssets.PersistenceAdapter.Tests/`、`Asun.Modules.CalibrationAssets.Wpf.Tests/`；仅明确获准的 A/I/W 切片才可创建。Wpf 使用 net10.0-windows/UseWPF 及本机 DevExpress 25.2.3，Adapter 使用既有 AsunImage；禁止下载替代依赖。各新工程 csproj 与目录同名，namespace 对应 Core 后缀 `.AsunImageAdapter/.PersistenceAdapter/.Wpf`。
- 禁止修改其它独立模块、产品 Shell/Domain/Integration、asunimage 内部、只读参考快照、docs/references 原件、共享入口/进度/登记。共享契约映射由主控串行接收。本轮仅允许改本 DEVELOPMENT-GUIDE.md。
- CAL-C1/C2/C3/CAL-JC/CAL-CR 的 §17.1 六项文档规格已获主控接收；CAL-JA/JI仅为固定路线/公开交接内容限定接收，不获得真实实现资格。开始产品实现前仍由主控确认权威仓库/分支/可审计代码基线并派发明确切片。A1–A4/W1/I1 不因 Core 接收而开门；本 binding 和计划命令不代表已构建/运行、集成或资格通过。
