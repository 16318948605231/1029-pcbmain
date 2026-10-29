# alignment-2d：二维定位与配准开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`Core`

- 模块 ID：`IM-026`；来源包：`PKG-022`
- 文档版本：`0.5.3-prep`；状态：`DesignReview`；本轮：`IM-REVIEW-20261009/alignment-2d`；Core接收同步：2026-10-10；Assembly Contract v0.1限定内容接收：2026-10-11；完整范围增量自审：§17.4；viewport WPF v0.2窄消费同步：§10.3A.1/17.5；viewport 0.3.5-prep对象选择/清屏同步：§10.3A.2/17.6
- 本文是独立模块的唯一实施指导草案。它定义可脱离检测平台接入的能力边界，不表示已有实现、模型、Golden、WPF 或生产资格已经通过。
- 技术基线：C# / .NET 10；可选 UI 为 WPF + 本机 DevExpress 25.2.3。AsunImage 是 HALCON 26.05 薄封装，算子统一经 `ImageLibDotNet.cv2` 调用；不再核验算子是否存在。只有实际 C# 类型、重载或封送歧义才查公共签名/消费项目编译，不扫描内部。

## 1. 目标和边界

### 1.1 模块职责

模块接收一个或多个已定义的二维参考特征、候选模型和搜索图像，执行局部候选搜索、候选完整性保留、一对一对应、受限二维变换拟合和独立一致性检查，返回可追溯的候选、位姿、残差、支撑和失败原因。支持的能力族为：

1. 形状模型或其他已批准轮廓路线的单特征搜索。
2. NCC 模板路线的单特征搜索。
3. planar uncalibrated 或 local deformable 路线的候选输出；只有在后端能力和用途资格均已证明时才可启用。
4. 多特征刚体、相似变换，以及§4.12/4.14已定的仿射/投影拟合；真实用途资格按对应切片验收。
5. 固定闭集的主路线、有限备用路线和总预算控制。
6. 训练、读回、搜索和几何拟合的无 UI 调用入口。

本模块同时负责**匹配模型的算法生命周期能力**（创建/训练候选、运行前核验、在请求中租用并执行），但不拥有模型资产的持久化、全局注册、审批/发布、保留/删除、跨应用分发或备份。上述资产职责归 `model-assets` 独立模块；Alignment 通过明确的模型资产端口读取不可变模型快照，并把训练产物作为候选交回该 Owner。调用方的制程配方不直接持有 HALCON handle。因而无需再拆一个只叫“模板匹配”的独立模块：形状/NCC/受约束变形搜索与多特征位姿拟合共用同一输入、候选、坐标和生命周期契约，分开项目只会造成执行/模型状态重复；若未来出现具有独立消费者、不同非定位语义或独立发布生命周期的匹配算法，应基于真实调用证据再拆分。

模块拥有的是本次计算事实：候选集合、对应关系、变换、残差、支撑、方法和运行诊断。它不拥有产品身份、模型资产最终发布权、坐标标定权、检测目标关系、工艺解释、质量判定、复判结论、报告事实或设备动作。

### 1.2 明确禁止

- 不写入或解释 PCB、PCBA、SPI、AOI、点胶、涂覆、钢网、元件或其他制程的缺陷、允差、放行、返修和工单规则。
- 不根据候选分数推导概率、毫米不确定度或 PASS/FAIL；分数只在其原方法和 Profile 内解释。
- 不把局部配准后的零残差当作原始偏移为零；调用方必须保留原观察和配准派生量。
- 不持有数据库、产品 ViewModel、页面全局状态、相机/运动/IO SDK 句柄或隐藏窗口。
- 不用排序位置代替稳定特征 ID，不因缺失候选删除调用方的必检分母，不以空结果掩盖输入错误、超时、取消或截断。
- 不在公共核心复制 `PKG-007` 坐标数学、`PKG-020` ROI 事实、`PKG-033` 模型资产库或 `PKG-006` 帧租约；通过明确适配端口消费它们。

### 1.3 规划消费者

最小独立接入需要两个不同宿主：

- **Consumer A：通用二维视觉工具**，用已知参考特征输出导航/工程注册结果。
- **Consumer B：另一类视觉检测工具**，用同一核心完成局部目标定位，再由宿主决定如何映射其目标和质量语义。

平台内的 PCB、钢网、元件和 FPC 仅是规划消费者示例；这些名字不得进入模块核心的枚举、默认规则或判定文字。第二消费者验收必须使用不同宿主、不同参数实例和独立资源租约，关闭一个实例不得影响另一个实例。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Alignment2D.Core` 与 `Asun.Modules.Alignment2D.HalconAdapter` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 WPF 控件切片可引用，Core 不得反向引用它。

**Blazor/Web**：Web 端展示候选位姿、残差与覆盖率；服务端计算，浏览器只渲染标记。命令不经浏览器。

**AI Tiling**：Alignment 结果（位姿变换）是 AI 推理前的几何前置步骤；本模块不持有推理 tile 租约，不参与分块编排。

**HALCON 双跑**：`find_shape_model` / ICP 路线与托管参照双跑；对应内点数/残差设容差门禁，局部最优差异标为仅诊断。本仓 OpenCV 快照不含 alignment 方法，无第三方 oracle；托管参照须按 §2.2 已核对 26.05 语义自证。

## 2. 依赖、端口和数据流

```text
调用方编排
  ├─ FramePort：只读图像/域/来源和租约
  ├─ ModelPort：模型内容、方法、版本、hash 和能力声明
  ├─ CoordinatePort：坐标系、单位和变换约定
  ├─ RoiPort：搜索域、halo、有效支持
  └─ DiagnosticsPort（可选）
          ↓
      Alignment Core
          ↓
  AlignmentResult（候选、对应、变换、质量、诊断）
```

### 2.1 允许的端口

端口必须由宿主显式注入；禁止从容器按字符串暗取服务。

| 端口 | 输入 | 输出/责任 | 资源责任 |
|---|---|---|---|
| `IImageFramePort` | `FrameRef`、有效域、采集 attempt | 只读像素访问、通道/位深/尺寸、派生链 | 持有至 native 真实退出和结果复制完成 |
| `IModelAssetPort` | 模型 ID、revision、hash、用途 | 不可变模型快照和能力声明 | 不向公共结果泄漏 native handle |
| `ICoordinatePort` | frame 名、单位、方向、坐标修订 | 受批准的点/矩阵转换 | 不重复隐式半像素补偿 |
| `IRoiPort` | 名义可达域、模型支撑、halo | 已验证搜索域和支持说明 | 派生域不可覆盖原输入 |
| `IExecutionDiagnostics` | operation/event 记录 | 结构化计时、计数、native 诊断 | 不改变计算结果 |

资产端口仅提供精确只读模型内容和描述；候选交接仍由§10.3宿主接口接回执，不在IModelAssetPort增加保存入口。搜索引擎持有临时 native 模型租约并执行训练/查找。资产库不能替 Alignment 做图像匹配、几何拟合或选择制程用途；Alignment 不能私自落库、激活或发布模型。训练 UI 若存在，只编辑训练草稿并调用同一 Core，不直接操作 HALCON 对象。

### 2.2 HALCON 优先核对

实现前按项目内 [`halcon算子手册/operators`](../../../halcon算子手册/operators/) 核对目标版本及公共签名。已定位的官方资料入口包括：

- `create_generic_shape_model` / `find_generic_shape_model` / `get_generic_shape_model_result`；
- `create_ncc_model` / `find_ncc_model` / `get_ncc_model_params`；
- `create_planar_uncalib_deformable_model` / `find_planar_uncalib_deformable_model`；
- `create_local_deformable_model` / `find_local_deformable_model`；
- `vector_to_rigid` / `vector_to_similarity` / `affine_trans_point_2d` / `affine_trans_contour_xld`。

上述算子按既定 `cv2` 基线直接使用。需要裁决的是算法用途、数据类型、坐标解释和资源行为，而不是封装算子可用性；不得另接 `HOperatorSet`/`halcondotnet.dll` 或扫描 AsunImage。项目内 [`AsunControl` 只读快照](../../references/project-snapshots/AsunControl/20261004/original) 中的 Shape/NCC/Deformable 工程只作为旧接口形态和错误路径资料，不自动继承其 WinForms、NET 8、全局状态或参数默认值。

## 3. 公共契约（Module API Contract v0.2.1）

以下类型名和签名是本模块 v0.2.1 的唯一实现形状；它们冻结无产品事实写入的请求、结果、状态、错误和端口语义。v0.1 草案被取代；v0.2.1是未实施规格的定向收口，明确H2域映射/分母证据、H3场精度和W1产物交接，不更改已接收C1–C3的责任、状态与六项结论。API major=1、minor=2，EngineOptions和ModelDescriptor的ContractRevision必须为v0.2.1；缺新增必填字段的旧草案不默认兼容，不把本次修订冒充已发布二进制的兼容补丁。正式平台 Contract/Schema/State/Owner 只负责映射产品事实；客户用途、阈值、持久化字段和提交回执仍由调用方采纳。

### 3.1 强类型基础值

```csharp
public readonly record struct PixelPoint(double Row, double Column);
public readonly record struct CartesianPoint(double X, double Y);
public enum LengthUnit { Pixel, Millimetre, Micrometre }
public readonly record struct AngleRad(double Value);
public readonly record struct ScaleFactor(double Value);
public readonly record struct DurationBudget(TimeSpan Value);
public readonly record struct OperationId(string Value);
public readonly record struct Revision(string Value);
```

规则：`PixelPoint` 使用像素中心坐标，左上像素为 `(0,0)`。Core 像素几何采用 `X=Column,Y=-Row` 的右手系，正角逆时针；world 坐标必须由注入的坐标端口转换，不默认像素为毫米。HALCON 矩阵按 `x=row,y=column` 解释，适配器负责一次换基和中心/边缘转换，不能原样赋给 Core。`AngleRad` 的输出规范为 `[-π,π)`，周期等价比较。所有浮点数有限；ID/revision 非空、区分大小写，不能由译文或显示顺序生成。`FrameDefinition(Id,Revision,Unit,Axes)` 冻结单位及轴定义；`Transform2D(Source,Target,Kind,CentreMatrix)` 为行主序九元素矩阵，按列向量左乘、源→目标；仿射末行为 `(0,0,1)`。不可单传裸矩阵或再隐式补半像素。

### 3.2 请求参数与默认值

| 参数 | 类型/单位 | 合法范围 | 默认值 | 说明 |
|---|---|---:|---:|---|
| `MethodFamily/ModelRoute` | 枚举，每模型/slot | Shape、Ncc、Planar、Local；具体路线见 §3.6 | 无默认，必填 | root 不另设会与 slots 冲突的方法；不按失败自动换方法 |
| `MaxCandidates` | `int`，每 slot 结果预算 | 1..256 | 8，仅编辑草稿 | 运行必填；与原生枚举上限分开，见 §4.10 |
| `MinScore` | `double` | 0..1 | 无默认，Profile 必填 | 方法相关的检索阈值，不是概率或遮挡率 |
| `AngleRange` | `Start,Extent`，rad | start `[-π,π)`；extent `0..2π` | 无默认 | extent=0 为固定角；2π 为完整一圈；必须包含于训练角域，不接受 HALCON 静默裁剪 |
| `ScaleRange` | `Min,Max`，无量纲 | 有限正数，min≤max，且在模型训练域内 | NCC 固定 `1,1`；Shape 必填 | 硬资源门另验；NCC 不支持原生尺度搜索，不能伪造 |
| `AllowedTransform` | `FitPolicy.Kind` | TranslationOnly、Rigid、Similarity、Affine、Projective | 无默认，GlobalPose 必填 | CandidatesOnly 无 Geometry；Local 不冒全局矩阵 |
| `MinCorrespondences` | `int` | 1..1024 | `PointPairs` 刚体/相似至少 2 | `OrientedSingle` 须有已资格方向与尺度；缺失必需 slot 不自动降级 |
| `MinBaseline` | `double`，frame 单位 | `>0` | 无默认，刚体多点时必填 | 不足时返回 `DegenerateGeometry` |
| `ExecutionLimits` | 强类型预算 | 每项为有限正数且不超 executor 能力 | 无默认，宿主必填 | Bytes、NativeModelBytes、MaxCombinations、MaxQueued、MaxActive、MaxRetainedResults 分项；禁止假定 native 内存可完全计量 |
| `Deadline` | `DurationBudget` | 1 ms..30 min | 宿主必填 | 接纳时以单调时钟生成截止点；队列、训练/读回、主/备、复制共用，非 UTC 时间 |
| `CancellationToken` | .NET token | 可取消 | `None` | token 取消不等于 native 已退出 |
| `AllowFallback` | `bool` | true/false | `false` | true 仍需提供有序闭集 |
| `MaxFallbackAttempts` | `int` | 0..16 | 0 | 不可借备用绕过资格失败 |
| `OutputDetail` | 枚举 | `Summary`、`Candidates`、`FullEvidence` | `Candidates` | 证据大小计入预算 |

应用不得把 `MinScore=0` 解释为“任何候选都合格”。检索参数、候选支撑、几何残差、身份唯一性、用途资格分别记录；缺阈值则拒绝该用途资格，允许返回诊断候选。`max_overlap∈[0,1]`、`greediness∈[0,1]`（Shape）、金字塔层/精度/metric 由冻结的路线参数提供；不复制其它路线的默认值。§4.9 规定自动参数读回、训练范围和变更影响。客户 Profile 可收紧硬边界。

### 3.3 输入契约

每次操作必须冻结并记录：`operationId`、计算 attempt、frame/采集 attempt、模型 ID/revision/hash、方法族、图像通道/位深/尺寸/派生链、搜索域与 halo、模型原点和坐标约定、允许自由度、候选上限、质量来源、资源预算、调用方用途和配置修订。缺失、过期、hash 不符、frame 不相容、NaN/Inf、空图像、越界域和不支持方法在调用 native 前拒绝。

### 3.4 输出契约

每个 `AlignmentResult` 至少包含：

- `operationId`、输入引用和模块/适配器版本；
- `TerminalState`、`ErrorCode`、`UnknownReason`（如适用）；
- 完整已观察候选（包括被拒候选、拒绝原因、原始索引和模型 ID）；
- 稳定对应关系、未匹配/歧义集合及一对一规则版本；
- 变换类型、源/目标 frame、方向、矩阵或取样场引用、模型原点；
- 每点残差、总体残差、基线、有效支持、边界/遮挡说明；
- 方法分数和其语义来源，不转换为概率或不确定度；
- 搜索/拟合/复制/排空计时、资源计数、实际参数和不可查询项；
- `EvidenceCompleteness`：`Complete`、`Partial`、`Truncated`、`Unknown`。

没有候选、执行失败、证据截断和合格候选必须可区分。结果不可变；迟到结果只能关联原 operation，不得覆盖后续操作。

### 3.5 DTO 字段闭包与用途判定

下表是 v0.2.1 的规范字段结构，后续 C# 以 sealed immutable record + `ImmutableArray<T>` 实现；集合不允许 null/default，非必需项用 nullable；不使用 object/dictionary 接收未冻结的业务数据。序列化字段仍由平台映射 Owner 采纳。所有请求共享 `RequestHeader(OperationId,Attempt:int≥1,ParentOperationId?,ConfigurationRevision,ApiMajor:int=1,ApiMinor:int=2)`、`ExecutionLimits` 和 `DurationBudget`。CancellationToken 是调用参数，不进入 DTO。

| 类型 | 必填字段及结构 | 不变量/消费者 |
|---|---|---|
| `FrameRef` | `Id,Revision,ContentHash,AcquisitionAttempt,FrameDefinition,Width:int,Height:int,PixelFormat,Channels:int,ValidDomain:DomainRef,Derivation:ImmutableArray<FrameMap>` | 尺寸/通道>0；hash SHA-256；格式枚举 Byte/UInt16/Int16/Float32；native 支持范围按路线验；不包含租约/像素指针 |
| `DomainRef` / `FrameMap` | 域：`Id,Revision,FrameId,ContentHash,Bounds:PixelRectangle`；映射：`Source,Target,Transform2D,Interpolation,ValidSupportRef` | 整数 crop bounds 含两端且在图内；域的真实 mask 从 RoiPort 获取，bounds 不代替域；映射链源/目标连续 |
| `ModelRef` / `ModelDescriptor` | 引用：`Id,Revision,ContentHash,Method,Route`；描述：引用 + `ApiMajor,ContractRevision,BackendVersion,AdapterRevision,TrainingSource,PreprocessRevision,TrainingDomain?,TrainingPose,Origin,SupportRef,ResolvedTrainingParameters,CapabilityRevision` | 描述缺字段、hash 不符、方法/route 不符不得搜索；A/B 各自描述；Origin 含默认中心、偏移和类型；XLD 不编造图像/domain |
| `FeatureSlot` | `FeatureId,Required:bool,ReferencePoint:CartesianPoint,Model:ModelRef,SearchDomain,Parameters:SearchParameters,CoarsePlan?` | IDs 唯一；所有 ReferencePoint 在同一参考 frame；模型可复用但候选空间与 slot 身份独立 |
| `AlignmentRequest` | 公共头 + `Frame,ReferenceFrame,Slots,ResultMode,Geometry:FitPolicy?,OutputDetail,PurposeProfileRef,AttemptPlan?` | 1..1024 slots；ResultMode=CandidatesOnly/GlobalPose；GlobalPose 必须有 Geometry；Local 只接受 CandidatesOnly；ProfileRef 为 ID/revision/hash，核心消费显式技术门 |
| `SearchParameters` | `Route` 判别联合；公共 `AngleRange,MinScore,MaxOverlap,EnumerationMode,MaxCandidates,SearchLevels,SupportPolicy,OutputLimits` + §3.6 路线字段 | 不支持字段拒绝；support policy 为完整图内/已资格部分支撑；缺门只能诊断，不默认可用；Alignment总输出预算为各slot合计，不能各占完整Engine额度 |
| `FitPolicy` | `Kind,ObservationMode,TranslationPolicy,AnchorFeatureId?,MinCorrespondences,MinBaseline,MaxPointResidual,MaxRmsResidual,AllowedScale,PoseEquivalenceTolerance,OrientationTolerance?,GeometryGate?` | 残差/基线在源/目标同一已转换长度单位；等价门有限非负；PointPairs 不从模型角补点；Affine/Projective 必须有 GeometryGate；OrientedSingle 见 §4.7.3 |
| `TrainRequest` | 公共头 + `CandidateModelId,CandidateRevision,Route,Template:TemplateSource,RequestedOrigin:PixelPoint,TrainingParameters,OutputLimits` | 新候选身份由宿主提供；不覆盖当前模型；Coarse/Fine 分别 BeginTrain 后由资产 Owner 绑定；不能在 Align 中训练；TemplateSource 见 §3.6 |
| `InspectModelRequest` / `ExportModelRequest` | 公共头 + `Model:ModelRef,ExpectedDescriptor,OutputLimits`；Export另`CandidateModelId,CandidateRevision` | Inspect 打开→读回→比对→关闭；Export生成新候选字节/hash/revision，不能假定write/read后字节不变；无发布/删除 |
| `FitRequest` | 公共头 + `SourceFrame,TargetFrame,Pairs:ImmutableArray<PointPair>,OrientedObservation?,Policy`；pair 为 `FeatureId,ReferencePoint,ObservedPoint,ObservationRef` | PointPairs 与 OrientedSingle 输入互斥；IDs 与点数完全对应；非有限/重复/零基线拒绝；不按较短数组截断 |
| `Candidate` | `CandidateId,FeatureId,ModelRef,Stage,BackendIndex,ObservedPoint?,ModelTransform?,NativePose,Angle?,ScaleRow?,ScaleColumn?,Score,ScoreSemanticRef,SupportEvidence,LocalEvidence?,RejectionCodes` | ID=`operation/slot/stage/index`；Local 可仅给原始位置/场，ModelTransform=null；中心/原点/原始与规范角分别存；不存在字段 null，不填零 |
| `CandidateSet` | `FeatureId,Candidates,EnumerationStatus,SearchCoverage,BackendLimit,ObservedCount,SuppressedByOverlap:int?,CoarseCoverageQualified` | 枚举状态 AllReported/TopK/Truncated/Unknown；抑制数量不可查询时null，不补0；完整性仅对冻结算法与检索门成立，不代表图中物理实例全集 |
| `AlignmentResult` / `FitResult` | `InputRefs,CandidateSets,Correspondences,Alternatives,UnmatchedRequiredIds,Pose?,Residuals,GeometryDiagnostics,PurposeEligibility,EvidenceCompleteness,ActualParameters,Diagnostics` | pose 不唯一/必需点缺失时 null；`PurposeEligibility=Qualified/Rejected/NotEvaluated`，与 operation 计算结束分开；质量和设备仍归宿主 |
| `TrainingResult` / `ExportResult` | `Artifact?:ModelArtifact,ReadbackReport,ActualParameters,Diagnostics`；artifact 为 `Descriptor,Content:ImmutableArray<byte>,ContentHash` | 完整字节且预算内；失败/取消 artifact=null；结果字节所有权转调用方，Core 不持有发布权；Inspect 返回 `ModelInspection(Descriptor,Comparisons,Diagnostics)` |
| `OperationResult<T>` | `OperationId,Attempt,Generation,TerminalState,ErrorCode?,ErrorDetails,Payload?:T,EvidenceCompleteness,Timing,ResourcesReleasedAt` | ErrorDetails 为字段路径/技术值/资源键，不直接显示原始异常；唯一终态发生在真实排空释放之后，详 §5 |

`Correspondence(FeatureId,CandidateId,ReferencePoint,ObservedPoint)` 与 `Residual(FeatureId,Vector,Norm)` 保留全部要求点；缺失不删分母。`SupportEvidence` 至少含映射后支撑总量、有效量、边界交叠、Known/Unknown、证据来源；score 不代替支撑或遮挡量。标准解为同一候选对应和同一自由度；只有规范角/尺度/平移在 Profile 等价门内且对应等价的解释才去重。两个非等价解通过门就是 Ambiguous，不用分数差猜唯一性。

### 3.6 路线参数与低层类型（不允许编码时任选）

`ModelRoute=GenericShape/ScaledShape/AnisotropicShape/Ncc/PlanarUncalibrated/LocalDeformable`；前三项 MethodFamily=Shape。`TemplateSource` 为 `ImageTemplate(FrameRef,DomainRef)` 或 `ContourTemplate(XldContourSet)`；contour set 是 `FrameDefinition,SourceRef,ContentHash,Contours:ImmutableArray<ImmutableArray<PixelPoint>>`，每条≥2有限点、总点数与字节计入预算。NCC 只接受 ImageTemplate。轮廓是明确上游提取结果，本模块不猜阈值重新提取。输入模型 route 必须与训练/搜索参数分支一致。

`AngleRange(Start:AngleRad,Extent:AngleRad)`、`ScaleRange(Min:ScaleFactor,Max:ScaleFactor)`、`OriginDefinition(DefaultCentre:PixelPoint,Offset:PixelPoint,Absolute:PixelPoint,Kind:DomainCentroid/ContourBoundsCentre)`、`TrainingPose(ReferenceFrame,ModelToTraining:Transform2D,TemplateDirection:AngleRad?,OrientationQualification:ProfileRef?)`、`ProfileRef(Id,Revision,ContentHash)`。点与矩阵的 typed unit/axis 仅沿 FrameDefinition，不在 point 再塞另一 string unit。`PixelRectangle(Top,Left,Bottom,Right:int)`、`PixelRun(Row,FirstColumn,LastColumn:int)` 均闭区间。`AutoOrFixed<T>=Auto/Fixed(T)`；auto 只用于官方支持的工程训练参数。`ContrastSpec=Fixed(single≥0)/Hysteresis(low≥0,high≥low,minComponentSize:int≥0)/Auto`；adapter 映射对应算子所列支持值，不能所有分支都默认支持 Auto。`Metric=UsePolarity/IgnoreGlobalPolarity/IgnoreLocalPolarity/IgnoreColorPolarity/IgnorePartPolarity`；NCC 仅前两项，Deformable 不采用 IgnoreLocalPolarity，Shape 不采用 IgnorePartPolarity；显式通道映射，绝不默默只取第一通道。

| 训练参数类型（所有字段必填，除显式 nullable） | 字段与适用约束 | 搜索参数专属字段 |
|---|---|---|
| `GenericTrainingParameters` | NumLevels:AutoOrFixed<int>、AngleRange、IsoScaleRange、AngleStep/ScaleStep:AutoOrFixed<double>、Metric、Contrast:ContrastSpec、MinContrast:AutoOrFixed<double>、Optimization:Auto/None/PointReductionLow/Medium/High；固定数值映射必须符合官方参数域 | `GenericSearchParameters`：IsoScaleRange、Greediness、Subpixel=None/LeastSquares/LeastSquaresHigh/LeastSquaresVeryHigh；搜索角域用angle_start/end，尺度用restrict_iso_scale_min/max，border固定false |
| `ScaledTrainingParameters` | NumLevels、AngleRange/AngleStep、IsoScaleRange/ScaleStep、Metric、Contrast、MinContrast、PointReduction、Pregeneration:None/Complete；均依官方 create_scaled 的类型 | `ScaledSearchParameters`：IsoScaleRange、Greediness、Subpixel、MaxDeformationPixels:int∈[0,32]；N>0 只与 LeastSquares 组合，不当局部场 |
| `AnisoTrainingParameters` | 同 Scaled，但 RowScaleRange/ColumnScaleRange、RowScaleStep/ColumnScaleStep 分开 | `AnisoSearchParameters`：RowScaleRange/ColumnScaleRange、Greediness、Subpixel、MaxDeformationPixels；双轴缩放在模型 row/column 轴，不在全图轴 |
| `NccTrainingParameters` | NumLevels、AngleRange/AngleStep、Metric；无 scale/contrast 参数 | `NccSearchParameters`：Subpixel:bool；尺度固定1；SearchLevels 为 UseTrained/FixedHighest(int≥1)/Range(highest≥lowest≥1)，actual 不允许 native 无记录降层 |
| `DeformableTrainingParameters` | Route=Planar/Local；NumLevels、BaseRowScaleMin/BaseColumnScaleMin>0、AngleStep/RowScaleStep/ColumnScaleStep、Metric、Contrast、MinContrast、PartSize=Small/Medium/Big、MinComponentSize:AutoOrFixed<int≥0> | `PlanarSearchParameters`：BaseRowScaleRange/BaseColumnScaleRange、Greediness、Subpixel、AngleChangeRestriction∈[0,π/2]、AnisoScaleRatioMin∈[0,1]、GeometryGate；不是训练最大角域/尺度域 |
| Local 同上 | 采用完整图内支持，不设置进程 global border 模式 | `LocalSearchParameters`：基础角域/双尺度、Greediness、Smoothness:int≥3、ExpandTop/Bottom/Left/Right:int≥0、Outputs flags（Field/Rectified/Contours）、MaxFieldBytes、MaxRasterBytes、MaxContourPoints；至少选一项，典型11不是默认质量门 |

Generic AngleStep/ScaleStep 等实际 HALCON 参数值按已读 setter 的合法形式映射，auto 模式/不可查询项形成 `ParameterValue`，不是任意动态键。`ParameterId` 为上表字段闭集；`ParameterValue=FiniteNumber/Integer/Boolean/EnumValue/Auto`，`ActualParameter(Id,Requested,Resolved?,Source:Request/BackendQuery/BoundManifest,Status:Known/NotQueryable,ReasonKey?)`。同一参数不得重复；字符串参数只从 enum 映射，不将宿主自由字符串送 native。MinContrast 固定值≥0，金字塔固定层数≥1、角步长/尺度步长>0；route 的官方域再收紧，不设统一虚构上限。范围乘积/尺寸/点数先 checked 估算，再验预算。模型内持有的 backend defaults 必须查询或绑定 manifest，不能在运行时跟着版本改变。

`ExecutionLimits(Bytes:long,NativeModelBytes:long,MaxCombinations:int,MaxQueued:int,MaxActive:int,MaxRetainedResults:int)` 均>0且≤EngineOptions 对应上界；Bytes/NativeModelBytes 只对可观测/估计项保证，Unknown 暂态见 §6。`OutputLimits(MaxArtifactBytes:long,MaxEvidenceBytes:long,MaxFieldBytes:long,MaxRasterBytes:long,MaxContourPoints:int)`>0、所有实际托管单数组/ImmutableArray容量≤`Array.MaxLength`，字节总量含复制峰值；长整数预算不表示可分配>2GB单数组。`EngineOptions(MaxQueued:int≥1,MaxActive:int≥1,MaxReservedIds:int≥1,MaxRetainedResults:int≥1,MaxRetainedBytes:long>0,MaxNotificationQueue:int≥1,LimitsCeiling,ModuleVersion,ContractRevision)` 由无UI宿主提供。运行不动态扩队列。接纳保留一个结果槽及该请求的最坏输出bytes额度，终态缩为实际bytes，Release才归还账本额度；计数满或bytes预算满拒新工作，不静默逐出仍被查询的terminal。请求较小queue/active门按当前engine计数验证，不能临时降低/抬高另一在途请求的执行并发。

`GeometryGate(UseDomain:DomainRef,PixelCartesianToSource:Transform2D,MinTriangleArea:double>0,MinNormalizedDet:double∈(0,1],MaxConditionNumber:double≥1,AllowReflection:bool,MinProjectiveDenominatorRatio:double∈(0,1],JacobianScaleRange:ScaleRange,MaxShearRad:double≥0)` 按 fit kind 适用；面积在源 frame 单位²；数值退化门来自方法 Profile，客户物理门另列，不留给程序员自行填。PixelCartesianToSource是H2用途的显式必填域映射，来源为宿主已冻结的坐标链/Profile；Source为UseDomain.FrameId的PixelCartesian/Pixel FrameDefinition（含实际frame revision），Target为待验Transform.Source；身份映射也显式提供。Engine不调用不存在的Resolve接口补映射；具体约束见§4.14。核心缺适用技术门则 RequestRejected。`PoseEquivalenceTolerance(Translation:double≥0,Angle:double≥0,Scale:double≥0,MatrixRelative:double≥0)` 不是跨模型身份合并门；同位置但不同身份解释仍歧义。

`OrientedObservation(FeatureId,ReferencePoint,ObservedPoint,ReferenceDirection,ObservedDirection,ObservedScale?,OrientationQualification,ObservationRef)` 必须有方向资格；Similarity 要有尺度，Rigid 必须固定1。`AttemptPlan(Primary:ImmutableArray<SlotAttempt>,Fallback:ImmutableArray<ImmutableArray<SlotAttempt>>,Trigger:CompleteSearchNoCandidate)`；SlotAttempt 是 `FeatureId,ModelRef,SearchParameters,CoarsePlan?`，必需 slot 集不变、有序闭集、fallback≤16且≤请求预算；不用其它方法重新标注主方法候选。

### 3.7 局部证据、资格、计时及回执的具体形状

`NativePose(Row?,Column?,Angle?,ScaleRow?,ScaleColumn?,Homography:ImmutableArray<double>)` 保留原始 native 语义，空矩阵允许但不补单位阵。全局 transform 只有 Rigid/Similarity/Affine/Projective/TranslationOnly，局部场不放进这个枚举。

`LocalEvidence(Grid:RasterGrid,Field:RasterSourceMap?,Rectified:RasterImage?,Contours:ImmutableArray<ImmutableArray<PixelPoint>>,GridBinding,SamplingSupport)`；Grid=`Id,Width,Height,TrainingBounds?,ExpandTop,ExpandBottom,ExpandLeft,ExpandRight`。`RasterSourceMap(GridId,SearchFrame:FrameRef,Rows:ImmutableArray<double>,Columns:ImmutableArray<double>,Valid:ImmutableArray<bool>,Direction:GridToSearch,CoordinateConvention:PixelCentre,SourcePrecision:FieldSourcePrecision,ContentHash)`，数组长度均为checked Width×Height、row-major、索引row*Width+column。本字段是绝对采样坐标，不能叫displacement。Rectified为`GridId,PixelFormat,Channels,StrideBytes,Content:ImmutableArray<byte>,ValidDomain`，保存原搜索frame/插值/model revision，不覆盖原图。

`FieldSourcePrecision(NativeType:FieldNativeType,NativeScalarFormat:FieldScalarFormat,Extraction:FieldExtraction,ReturnedScalarFormat:FieldReturnedFormat,Conversion:FieldConversion,CoordinateUnit:LengthUnit,SampleFrame:FrameDefinition,SourceEvidence:FieldPrecisionEvidence)`是每个非null Field的必填字段，不是脱离合同的日志键。封闭值：FieldNativeType仅HalconVectorFieldAbsolute；FieldScalarFormat=Ieee754Binary32/Ieee754Binary64/Unreported；FieldExtraction仅GetGrayval；FieldReturnedFormat仅Ieee754Binary64；FieldConversion仅PreserveReturnedValue；CoordinateUnit必须Pixel，SampleFrame必须等于SearchFrame.FrameDefinition（包括其frame revision，不是图像内容revision）。`FieldPrecisionEvidence(BackendVersion:string,AdapterRevision:Revision,NativeTypeQuery:FieldNativeTypeQuery,ScalarFormatSource:FieldScalarFormatSource,BindingEvidenceRef:ProfileRef?)`；BackendVersion非空且等于本次Diagnostics.BackendVersion，AdapterRevision等于本次Diagnostics.AdapterRevision；FieldNativeTypeQuery仅Confirmed，FieldScalarFormatSource=PublicBinding/BoundManifest/NotReported。已知32/64必须有对应public binding或hash绑定manifest证据且BindingEvidenceRef非null，Unreported必须NotReported且该引用为null，不填猜测位数。get_image_type只证明vector_field_absolute类型，不从该token或返回HTuple/C# double推断原生scalar位宽；不存在自动量化误差/毫米sigma字段。

消费与有效域：adapter在每候选native Field尚有效时读取类型，按受预算约束的分批整数grid索引调用cv2.get_grayval，核每像素两值的row/column顺序及tuple长度后复制到Rows/Columns；顺序由该adapter的非对称Golden绑定，不猜内部存储。保留返回有限数的Binary64值，不round为显示精度，也不把已float32量化值称新double测量。原field真实domain由cv2.get_domain读取，get_grayval会忽略domain，故不得把读到值等同有效点；Valid同时要求native有效域、有限值、源图有效域及插值邻域支持。Valid=true的绝对row/column位于SearchFrame像素中心范围`[0,H-1]×[0,W-1]`，双线性另满足右/下邻点门；域外有限值可保留但Valid=false，不能进入map/几何。非有限值不进入公共Rows/Columns；该Field不发布（Field=null并记录Partial与原因），拒绝相关用途，不用0填洞。

SourcePrecision由§4.13步骤2/3产生，经Candidate.LocalEvidence.Field随复制、hash闭包、Replay、宿主保存值结果及§10证据详情消费；field hash绑定GridId、SearchFrame全部引用、Direction/Convention、SourcePrecision全部字段、Rows/Columns/Valid，不只hash裸double数组。输入hash/Profile/adapter revision或精度来源变化须重做该Field用途资格。Unreported允许RawRasterOnly诊断并显示资源键Aln.FieldPrecision.Unreported：“原始精度未报告/原始精度未回報/Native precision not reported”，不可QualifiedTemplateBinding或导出计量精度声明；32→64转换不能补精度资格。本定义仅冻结公开数据闭包/消费门，原生提取/manifest具体绑定仍归H3真实适配门。

GridBinding=`Status:RawRasterOnly/QualifiedTemplateBinding,GridToTraining:Transform2D?,EvidenceRef?`。RawRasterOnly 时可以显示原生栅格和场在搜索图中的绝对坐标，不能拿不明的模板/crop索引计算毫米偏移。QualifiedTemplateBinding 必须绑定 adapter revision 的非对称/非零origin/expand/border Golden，预期映射是训练 bounds 左上加整数 grid 索引再减上/左扩边，实际支持及舍入由该 Golden 对照；不凭输出尺寸宣称已通过。Local 不向调用方承诺连续逆或通用坐标边；需要逆/拓扑的消费者向 coordinate-geometry 的独立 Owner 申请资格，不在本模块造逆算法。无资格时该用途为 NotEvaluated，原生局部诊断计算仍可完成。

`SupportEvidence(Total:long,Valid:long,BoundaryCount:long,Status:Known/Unknown,SupportRef?,ReasonKeys)` 计数≥0、Valid≤Total；完全支撑门时 Unknown 一律不采用。`SamplingSupport` 为有效栅格mask及源域/插值邻域核验来源，防止 map_image 越界。`SearchCoverage(DomainRef,Mode:FullApprovedDomain/QualifiedCoarseWindows/PartialWindows,Completed:bool,QualificationRef?)`。`GeometryDiagnostics(BaselineReference?,BaselineObserved?,DistanceRatio?,TriangleArea?,NormalizedDet?,ConditionNumber?,IndependentValidation:Available/Unavailable,IndependentEvidenceRef?,Reasons)`；字段不存在用 null，不填零制造诊断。

`Timing(AcceptedAtTimestamp,NativeStartedAt?,NativeReturnedAt?,DrainedAt,ResourcesReleasedAt,Stages:ImmutableArray<StageTiming>)` 统一本 Engine TimeProvider；StageTiming=`Stage,Elapsed:TimeSpan,Attempts:int`。`ResourceCounters(ManagedKnownBytes,NativeEstimateBytes?,CandidateCount,CombinationCount,Queued,Active,NotificationDropped)` 不把未知记0；`Diagnostics(BackendVersion,AdapterRevision,NativeReturnCode?,ActualParameters,Timing,ResourceCounters,ReasonKeys)` 为有界值对象。`ErrorDetail(FieldPath:string,ReasonKey:string,NumericValue:double?,ReferenceId:string?)` 不持有 Exception/native。`ReadbackReport(Comparisons:ImmutableArray<FieldComparison>,Passed:bool)`；comparison=`FieldPath,Equal/Different/NotQueryable,Expected:ParameterValue?,Actual:ParameterValue?,SourceRef?`；NotQueryable 仅有 hash 绑定 manifest 才允许描述完整。

接纳/关闭回执的枚举值以 §5 为唯一；`ValidationError(FieldPath,ErrorCode,ReasonKey)`；`CancelReceipt(Id,Requested/AlreadyRequested/AlreadyTerminal/NotRetained)`；`ReleaseReceipt(Id,Released/Busy/NotRetained)`；`ShutdownReceipt(Completed/Pending,PendingOperations:ImmutableArray<OperationSnapshot>)`；`OperationSnapshot` 的 Phase 为 §5 状态闭集、DrainStatus=NotStarted/Draining/Drained/Isolated，Terminal 为 nullable已终态结果摘要。日志/UI只消费这些值，不获得发布或业务采用权。

`RecommendationRequest`=公共头/预算+`SourceProfile:ProfileRef,TrainingSource:TemplateSource,Candidates:ImmutableArray<ParameterCandidate>,EvaluationProfile:RecommendationProfile,Evaluations:ImmutableArray<CandidateEvaluation>`。ParameterCandidate=`CandidateId,Route,TrainingParameters,SearchParameters,CoarsePlan?`，按请求顺序稳定排序，数量1..64。RecommendationProfile=`Ref,MaxFalseAcceptRate,MaxFalseRejectRate,MinCompletedSamples,RequireCompleteDrain:bool=true,ComparisonLoadRef`；rates∈[0,1]、samples>0；参数/真值/负载必须与证据对应，同一source hash不代表同一评估Profile。

CandidateEvaluation=`CandidateId,ModelRef,EvaluationProfileRef,InputSetHash,TruthSetHash,ModuleVersion,AdapterRevision,BackendVersion,SampleCount:int,FalseAcceptCount:int,FalseRejectCount:int,ExpectedAbsentCount:int,ExpectedPresentCount:int,FailedCount:int,CensoredCount:int,AllDrained:bool,P95:TimeSpan?,PeakKnownBytes:long?,EvidenceRef:ProfileRef`；所有计数非负、分母>0且min sample满足、错率用对应absent/present分母。证据来自宿主明确授权的独立Replay评估，不由Core根据score编造；评估失败/删失非零或未drain，不参与自动择优。`ParameterProposal(SourceProfile,InputRefs,EvaluationProfileRef,SelectedCandidateId?,Assessments:ImmutableArray<ProposalAssessment>,Status:Suggested/NoQualifiedCandidate/InsufficientEvidence,ExpiryRule:InputOrRevisionChanged)`；assessment=`CandidateId,Accepted:bool,ReasonKeys,EvidenceRef?`。BeginRecommend是**纯值验证与排名**，不在内部训练/跑样本；训练/评估各自有已记录operation由host组合，符合§4.9有限闭集顺序。缺完整同负载P95/资源证据则InsufficientEvidence，不用0占位；成功只提出建议，不更新模型。该操作不调用native，仍经过账本/事件/释放/terminal；无可选项Completed+NoQualifiedCandidate，不冒NoCandidate图像未检出。

`InputRefs(Header,FrameRefs,ModelRefs,DomainRefs,ProfileRefs)`；`Alternative(AlternativeId,Correspondences,Pose,Residuals,GeometryDiagnostics,GateReasons)`；`OperationTerminalSummary(State,ErrorCode?,EvidenceCompleteness,ResourcesReleasedAt)`；Stage=Validation/Queue/Acquire/Preprocess/ModelOpen/Train/Search/Associate/Fit/GeometryCheck/Copy/Export/Readback/Drain/Release/Recommend，均为enum。FitResult不需搜索时CandidateSets为空；CandidatesOnly不拟合时Pose=null/Correspondences为空，但CandidateSet可Qualified其明示导航用途，不能宣称整体刚体。原生无法提供某个诊断项使用nullable+source，不强行造事实。

`AlignmentDraft(Frame,ReferenceFrame,Slots,ResultMode,Geometry?,OutputDetail,PurposeProfileRef,AttemptPlan?,ExecutionLimits,Deadline)` 为请求去掉Header的技术草稿；public static `ImmutableArray<ValidationError> AlignmentValidation.ValidateDraft(AlignmentDraft draft,BackendCapabilities capabilities,ExecutionLimits ceiling)` 只做纯值/路线/范围/预算校验，无lease/native/operation副作用。UI和BeginAlign都使用它；Begin另外验证header/ID/engine状态与接纳资源，不重复一套不同参数门。其它请求的纯值校验由其Begin的同一内部validator执行，UI训练草稿以TrainRequest技术字段验证且不读模型。`FrameDefinition.Axes=PixelCartesian/CartesianRightHanded`；PixelCartesian就是§3.1 X=column,Y=-row，world CartesianRightHanded必须通过显式带单位的frame链传递，不能把行列当world点。

训练UI的纯值入口同时冻结为public static `ImmutableArray<ValidationError> AlignmentValidation.ValidateTrainingDraft(TrainingDraft draft,BackendCapabilities capabilities,ExecutionLimits ceiling)`；TrainingDraft=`CandidateModelId,CandidateRevision,Route,Template,RequestedOrigin,TrainingParameters,OutputLimits,ExecutionLimits,Deadline`（不含Header），与BeginTrain共用validator。`WorkbenchDraft(Training:TrainingDraft?,Search:AlignmentDraft?)`是UI InitialDraft，至少一项非null；ViewGeneration/ContextGeneration为正long，engine Generation为Guid，不混用。typed setter/INotifyDataErrorInfo是编辑反馈，执行前仍重新验证冻结草稿。Generic ContrastSpec.Fixed的映射为contrast_low=contrast_high=single、min_size=0（单阈值不另外抑制小连通分量）；Hysteresis映射low/high/minComponentSize；Auto的resolved逐项读取封存。XLD不适用的image contrast字段必须显式NotApplicable，不偷偷补灰度图。

## 4. 算法处理规则

### 4.1 单特征搜索

1. 校验模型能力、输入模态和域支撑，保留模型原点和真实搜索坐标。
2. 在批准的可达域内搜索；模型支撑/halo 与参考点搜索范围分开。
3. 保留后端返回的全部候选至 `MaxCandidates`，记录后端结果索引；不以返回顺序绑定业务 ID。
4. 检查角度、尺度、有效支撑、边界、遮挡和分数语义；任何检查失败保留候选及原因。
5. 仅当请求允许且所有硬门满足时，候选才可标记 `UsableForRequestedPurpose`。

Shape、NCC、Planar、Local 的原生输出不能统一压成 `Row/Column/Angle/Score`。例如 generic shape 可返回 `hom_mat_2d`，NCC 的位置/原点语义需按官方说明组合变换；Planar/Local 的矩阵或场缺项时不得补造角度、尺度或逆变换。

### 4.2 多特征对应和拟合

对应必须使用稳定 feature ID、设计关系、搜索域、方法和一对一约束。相同圆或对称特征发生互换时返回 `Ambiguous`，不能静默输出 180°。

- 刚体 PointPairs：至少两个非重合、足够长基线对应；固定尺度，默认等权最小二乘，不以相似变换吞掉长度差。OrientedSingle 是显式另一观察模式，见 §4.7.3。
- 相似：尺度由对应点估计，但尺度变化必须保留为事实，不能消除应检尺寸偏差。
- 仿射：至少三个非共线对应，并检查面积/条件数/残差；未采纳前不可启用。
- 投影：至少四个充分分布对应，并检查退化；不等于非平面计量资格。
- 局部场：保留域、网格/拓扑、支持、逆资格和数值策略；未证明完整逆时只能用于限定诊断。

几何例：右手 Cartesian 设计点 `q1=(0,0), q2=(100,0)`，实测点 `p1=(10,20), p2=(10,120)` 应产生 `+π/2` 和平移 `(10,20)`。单个无方向点不能给出旋转；两点共线本身不使刚体/相似退化，仿射才要求非共线。短基线、非有限点和互换歧义必须拒绝。

### 4.3 主路线和备用

备用是预先批准的有序闭集，不是任意模型列表。所有尝试共享同一个绝对 deadline、累计候选/字节/组合数和取消令牌。以下情况不得转为 `NotFound` 并继续备用：输入/模型错误、质量或证据未知、超时、取消、资源耗尽、歧义和 native 未排空。只有明确的“完整搜索且无候选”才可进入已批准的备用触发条件。

### 4.4 具体路线、训练闭包和恢复条件

路线选择由调用方 Profile 和模型能力声明共同决定；模块不得根据分数自动换路线。每条路线的训练、运行和恢复闭环如下：

| 路线 | 训练/建模输入与参数来源 | 运行顺序 | 可发布输出 | 失败与恢复条件 |
|---|---|---|---|---|
| Generic Shape | 训练图/轮廓、明确 domain、模型原点、角度/尺度范围、金字塔/对比参数；参数来自训练请求，实际可查询值来自后端读回 | 读回模型→核图像模态和 support→在参考点可达域搜索→读取每个结果的原索引/矩阵→做支撑与质量门 | 候选、`hom_mat_2d` 或后端等价变换、角度/尺度（仅后端确实返回时）、支持和残差 | 训练失败或读回 hash 不符：`ModelUnavailable`；边界支持不足：保留候选并 `QualityRejected`；完整无候选才可触发已批准 NCC/几何备用 |
| NCC | 非退化灰度模板、训练 domain、模板原点、角度范围、最小分数、候选数；输入通道和参数快照必须与训练闭包一致 | 读回模型→核 domain/原点和通道→执行 `find_ncc_model`→按官方返回位置/角度/分数解释→应用一对一/几何门 | 原始行列/角度/分数及其来源、候选完整性和派生矩阵（仅适配器证明方向后） | 常量/近常量模板、通道不符或分数语义未知：`ContractMismatch`/`QualityRejected`；完整无候选才可触发闭集 Shape 备用；超时不可当无候选 |
| Planar uncalibrated | 参考平面图像或 XLD、明确平面模型原点、允许投影范围、实际模型参数和后端能力声明；不使用标定毫米假设 | 读回模型→核输出是否为完整投影/支持→执行 planar 搜索→验证有效覆盖、投影退化和结果字段 | 仅在完整字段可得时输出投影变换、候选、覆盖和残差；不自动降为刚体 | 后端只返回部分位置/场或覆盖不足：`UnsupportedMethod`/`QualityRejected`；不触发刚体备用掩盖字段缺失 |
| Local deformable | 训练图/XLD、局部模型参数、grid/取样/输出策略、形变域和实际可查询参数；由用途 Profile 明确允许范围 | 读回模型→固定局部域和资源上限→执行 local 搜索→复制完整场/支持→检查拓扑、孔洞、逆资格和场大小 | 候选及完整局部场、域、拓扑、支持和数值资格；不把场压成单一角度 | 场为空、只得到 Row/Column、拓扑或逆未资格：只返回限定诊断或 `UnsupportedMethod`；不得回退到刚体作为“成功” |
| 几何拟合 | 已通过身份/对应的点集、frame/单位、允许自由度、基线/分布门；参数来自请求和 CoordinatePort | 稳定 ID 对应→一对一消歧→按kind检查最小点数/基线/面积→调用§4.12固定算子→独立残差检查 | 方向、矩阵、逐点残差、几何支持和退化证据 | 零基线/非有限点退化；近共线仅按Affine/Projective条件拒；多解Ambiguous，不自动升自由度 |

训练成功只表示模型句柄/文件和训练闭包形成；模型登记还必须完成字节 hash、方法/参数快照、原图引用、原点/域语义、读回报告和用途权限。训练输入、通道、domain、原点、方法或影响搜索的参数任一变化都产生新 revision，并使依赖的搜索资格失效。取消训练时旧已发布模型保持不变，草稿模型必须在 native 真正退出后释放；部分训练结果不得注册为可运行模型。

恢复只允许从同一 operation 的原始证据继续查询：模型保存未知查保存回执，运行结果未知查运行回执，排空未知隔离实例并等待或销毁宿主隔离边界。不得通过重新搜索、重新采集或改变参数把 Unknown 改写成成功；重新搜索必须是新 attempt。

### 4.5 HALCON 26.05 与 ImageLibDotNet 核对表

实现切片必须逐项记录以下本地 26.05 页面核对结果（页面标题均标明 `Version 26.05.0.0`），并在适配器测试中保存实际公共签名和结果字段：

| 页面 | 必核事实 | 不支持时的行为 |
|---|---|---|
| `create_generic_shape_model` / `find_generic_shape_model` / `get_generic_shape_model_result` | 模型类型、训练 domain、搜索域、候选上限、原点、结果索引、`hom_mat_2d` 和可查询参数 | 缺失矩阵/结果索引时拒绝该路线，不猜字段 |
| `create_ncc_model` / `find_ncc_model` / `get_ncc_model_params` | 模板 domain/原点、角度范围、分数/候选返回、位置到原点的变换语义 | 不把 Row/Column 直接当业务中心，不跨方法比较分数 |
| `create_planar_uncalib_deformable_model` / `find_planar_uncalib_deformable_model` | 投影结果类型、支持/边界、参数读回和停止能力 | 不得补出刚体角度或毫米结果 |
| `create_local_deformable_model` / `find_local_deformable_model` | 局部场结果类型、网格/拓扑、输出大小、支持和资源上界 | 缺完整场/拓扑时仅作诊断或拒绝 |
| `vector_to_rigid` / `vector_to_similarity` / `affine_trans_point_2d` | 输入点方向、输出矩阵方向、单位和退化输入行为 | 以 `DegenerateGeometry` 拒绝，不由自写近似替代 |

适配器统一经 `ImageLibDotNet.cv2` 调用上述算子，不审查其存在性。领域层不引用 `HObject`、`HTuple` 或 HALCON handle；结果复制后释放 native 结果对象。`UnsupportedMethod` 只表示该 adapter revision 未实现/未资格某路线或请求输出，不表示 AsunImage 缺算子。C# 重载/封送歧义只阻断对应绑定，不得反射扫描内部、改 AsunImage 或另接 HALCON。没有已验证的即时停止能力时执行 §6 的等待/隔离，不能承诺硬取消。手册阅读不等于真实运行、Golden、性能或 HIL。

页面入口（本地 HALCON 26.05.0.0）必须作为实现切片的原始引用：[`create_generic_shape_model`](../../../halcon算子手册/operators/create_generic_shape_model.html)、[`find_generic_shape_model`](../../../halcon算子手册/operators/find_generic_shape_model.html)、[`get_generic_shape_model_result`](../../../halcon算子手册/operators/get_generic_shape_model_result.html)、[`create_ncc_model`](../../../halcon算子手册/operators/create_ncc_model.html)、[`find_ncc_model`](../../../halcon算子手册/operators/find_ncc_model.html)、[`get_ncc_model_params`](../../../halcon算子手册/operators/get_ncc_model_params.html)、[`create_planar_uncalib_deformable_model`](../../../halcon算子手册/operators/create_planar_uncalib_deformable_model.html)、[`find_planar_uncalib_deformable_model`](../../../halcon算子手册/operators/find_planar_uncalib_deformable_model.html)、[`create_local_deformable_model`](../../../halcon算子手册/operators/create_local_deformable_model.html)、[`find_local_deformable_model`](../../../halcon算子手册/operators/find_local_deformable_model.html)、[`vector_to_rigid`](../../../halcon算子手册/operators/vector_to_rigid.html)、[`vector_to_similarity`](../../../halcon算子手册/operators/vector_to_similarity.html)、[`affine_trans_point_2d`](../../../halcon算子手册/operators/affine_trans_point_2d.html)。

## 4.6 第二轮场景驱动复审

下表是实现和审核必须逐项可判定的场景合同。每行的“参数来源”不得由代码默认值替代；“恢复动作”由核心保证到排空/结果交付边界，业务后续由调用方负责。

| 场景 | 输入与参数来源 | 处理顺序 | 输出/状态/错误 | 恢复动作与验收断言 |
|---|---|---|---|---|
| 正常配置/执行 | 完整 frame/model/ROI/坐标修订；Profile 给方法、自由度、候选数和 deadline | 校验→租约→预处理→搜索→对应→拟合→独立质量检查→复制→排空 | `Completed` + `Complete` 证据；包含矩阵、残差、支持、方法和计时 | 同一冻结输入重复运行得到同一候选顺序/矩阵容差；两个消费者互不影响 |
| 空图、空域、缺模型 | 空像素、空有效域、模型引用缺失或 hash 不符 | native 前契约校验 | `InvalidInput`/`InputUnavailable`/`ModelUnavailable`；不得创建后端句柄 | 修正输入或换批准资产，新建 attempt；验收为 native 调用计数为零 |
| 部分成功/部分候选 | 多 feature 中部分有候选，或证据/场达到输出上限 | 保留每个 slot 原状态→只对完整允许集合拟合 | `Partial`、`NoCandidate` 或 `Rejected`；缺失 slot 不删除 | 调用方收到缺失原因和原候选；不生成“完整位姿”或触发不适用备用 |
| 歧义 | 对称/重复特征、多个解释通过硬门 | 候选保全→稳定 ID 对应→比较等价解释→停止扩展 | `Ambiguous` + 全部解释和消歧证据 | 调用方提供额外先验/人工选择后新 attempt；不得按返回顺序选第一项 |
| 错误输入/契约不符 | 单位、frame、通道、参数范围、版本或方法能力不符 | 逐字段校验，不进入搜索 | `InvalidRequest`/`ContractMismatch`/`UnsupportedMethod` | 修订请求或适配器；验收为错误可定位且无部分成功伪装 |
| 超大图/高并发 | 大像素量、多 tile、多 operation 或超过并发租约 | 估算 bytes/候选/队列→有界准入→分批搜索 | `ResourceExceeded` 或有界 `Completed`；记录队列/峰值 | 拒绝新工作或等待租约；不得无界开 Task；并发压力下两个消费者仍隔离 |
| 噪声/遮挡/退化 | Golden变体含噪声/反光/遮挡/缺损/短基线/Affine共线 | 输入质量→保守搜索→支持/几何门→拒识 | 候选保留；Rejected+QualityRejected/DegenerateGeometry，只有完整未检出才NoCandidate | 调用方决定重采/人工；不把低质候选升级唯一合格 |
| 取消/超时/native 未排空 | token 取消、绝对 deadline 到期、后端停止未知 | 停止新派发→请求后端停止→等待 native→复制可得证据→排空 | 未返回为WaitingForDrain/Isolated；释放后才Cancelled/TimedOut终态 | 未Drained的实例隔离；Completion未完成；迟到事件归原operation；无句柄/帧提前释放 |
| 资源上限 | 内存、模型驻留、候选、组合、证据或保存字节达到上限 | 每阶段前检查并累计消耗，错误也计入预算 | `ResourceExceeded` 或 `EvidenceTruncated` | 释放临时资源、保留已观察范围；不得宣称完整或最优 |
| 持久化/版本修订 | 模型/参数/坐标/adapter修订变化 | 生成候选→写出/闭流→独立读回→hash/参数核对→交宿主Owner | 完整artifact或BackendFailure/ContractMismatch；发布/持久回执归宿主 | 旧revision不变；未知保存查宿主原回执；未知模型组合拒绝 |
| 升级/回退 | 新旧二进制、适配器、模型和结果组合 | 能力矩阵→读回→Replay/Golden→切换 | 兼容则运行；不兼容显式拒绝 | 回退到完整旧包，保持原 operation 可读；不恢复设备或质量事实 |
| 无 UI 调用 | 服务/CLI/测试宿主提供端口和 token | 使用同步/异步同一核心入口 | 只返回模块结果和诊断 | 无窗口、无 Dispatcher、无静态全局状态；同一输入断言相同 |
| 可选 UI | 宿主注入语言、主题、权限、viewer 和取消等待 | UI 编辑草稿→冻结请求→调用核心→投影结果 | 只显示状态/候选/错误/排空；不写业务事实 | 1920x1080 三语和关闭页面测试；关闭不提前释放 native 资源 |
| 第二消费者 | 不同宿主、不同模型/参数、并发运行 | 各自 operation/租约/结果缓冲 | 各自终态和计时 | 关闭/取消 A 不改变 B；无共享可变模型或缓存污染 |
| 长期运行/重启 | 连续运行、租约老化、进程重启、旧任务迟到 | 有界队列→健康计数→定期释放/重建→启动恢复查询 | 无静态句柄泄漏；未决 operation 为 `Unknown` 或可查询终态 | 重启后不自动重放设备动作；内存/句柄趋势有界，迟到结果不覆盖新代 |

### 4.7 强制 Mark 反例：大图中的远距离 A/B 双子模板

这是本模块的必写、必测反例，用来防止把两个远距离小特征拼成一个巨大无信息模板。它是纯二维定位场景；A/B 的业务名称、目标关联和后续判定仍由调用方提供。

#### 4.7.1 冻结输入和编程保存

调用方提供一张参考图和一张运行图，A、B 是同一 frame 中相距很远的两个独立子模板。A、B 各自保存：

- 独立 `modelId/revision/hash`、模型方法（Shape 或 NCC）、训练图/域/通道和模型中心；
- 模型原点相对各自参考坐标的偏移、参考坐标 frame/单位/方向和 crop/resize 修订；
- 参考点 `qA=(xA,yA)`、`qB=(xB,yB)`，A-B 基线 `B=|qB-qA|` 和连线角 `alpha=atan2(yB-yA,xB-xA)`；
- 各自允许角度/尺度、模型支撑/halo、局部搜索域、候选上限和质量来源；
- A/B 的稳定 feature ID。不能用返回顺序、图像数组索引或“左边/右边”代替身份。

参数来源是冻结的编程/模型资产快照；运行请求只能引用其 revision，并提供当前 frame、粗定位策略、局部域、变换自由度、总 deadline 和资源上限。保存模型不等于发布模型，必须完成字节 hash、原点/域读回和独立未参与训练的复核。

#### 4.7.2 粗到精处理顺序与缩放闭包

首选 Generic Shape 独立 A/B 模型；稳定灰度纹理且固定尺度时可明确选 NCC。二者不按分数互换。默认精搜为原分辨率，不把粗精搜做成一次巨大双 Mark 模板。每 slot 有 Fine 和可选 Coarse 两个**分别训练**的模型引用，包含各自 hash、尺寸、原点、支撑、训练范围和派生链；不能把原尺寸 NCC 模型直接搜索缩小图。

外部降采样采用 `affine_trans_image_size`：固定有理等比因子 `k∈(0,1]`、`Interpolation='constant'`，输出尺寸 `ceil(k*W),ceil(k*H)`；传入的比例仍为 k，不以取整后的 W'/W、H'/H 改成非等比缩放。使用该算子是为显式冻结边缘坐标矩阵及抗混叠行为。禁止默认为 `zoom_image_*` 与它共享同一像素映射；后者以后采用须有自己的映射与实测反例。输入 domain 会被算子忽略，必须独立变换有效域并排除补黑/插值缺支持的像素，再 `reduce_domain`。不改全局 `int_zooming`；记录当前行为及像素格式，真实差异由 adapter Golden 核对。

令参考原图像素中心 q 经整数 crop 左上 `(r0,c0)` 再缩放进入训练图，映射 `F_t`：

`r_t=k_t*(r-r0+0.5)-0.5; c_t=k_t*(c-c0+0.5)-0.5`。

搜索原图到本次粗/精搜索图的 `F_s` 同式；逆为 `r=r_s0+(r_s+0.5)/k_s-0.5`，column 同理。单纯 `reduce_domain` 不改变坐标，`crop_rectangle1` 才减 crop 起点。粗精两个阶段各自记录实际 `F_t,F_s`，不能用计划缩放比代替实参。训练/搜索都存原图大小、crop、输出大小、插值、有效域和修订。

原点与矩阵链冻结如下（先在 row/column 中心坐标组合，最后换基到 Core）：

1. 图像训练默认中心是**训练 domain 重心** c，不是 crop 矩形中心；Generic XLD 后续路线是包围盒中心。请求的模型原点 o=`F_t(q_origin)`；Generic `origin_row/origin_column`、NCC `set_ncc_model_origin` 设置的是 `o-c` 相对偏移。NCC 搜索参考点域仍按 c，不能用 o 的域直接传 native。
2. `M_t` 为模型局部中心坐标→训练图的零旋转/单位尺度变换，平移为 o。模型中指定参考特征坐标 `u=M_t⁻¹ F_t(q_i)`；q_i 可不同于模型原点，不允许后来把 domain 重心或返回 Row/Column 偷换为 q_i。
3. Generic 使用每个 MatchResult 的 `hom_mat_2d`；NCC 先以官方序列 `vector_angle_to_rigid(0,0,0,Row,Column,Angle)` 得 `H_native`，然后以 `affine_trans_pixel` 语义恢复真实点。NCC 的 Row/Column 是适于构矩阵的调整值，不能直接赋 ObservedPoint。
4. HALCON 边缘矩阵的中心坐标等价为 `K(H)=T(-0.5,-0.5) H T(0.5,0.5)`。因此本子模型的原参考图→原搜索图变换为 `G_i=F_s⁻¹ K(H_native) M_t⁻¹ F_t`，观测 `p_i=G_i(q_i)`。native 原始 H 和链引用留证，公开 ModelTransform 为换基后的 G_i；只有适配器做一次 K，Core/Viewer 不再补半像素。训练自匹配只检查该链，不用其数值代替精确 F_t/M_t。
5. 等比时原空间尺度 `s_physical=s_native*k_t/k_s`。NCC 的 native scale 恒 1，Coarse 训练与搜索必须用同一 k；物理尺度未知的 NCC 请求拒绝，不用缩小图伪造尺度搜索。Shape 为保证原空间允许范围 `[s_min,s_max]`，native 范围换为 `[s_min*k_s/k_t,s_max*k_s/k_t]` 并检查训练闭包；取整像素支持不足时停止该粗策略。

操作顺序：读 A/B Fine/Coarse 描述→校验链/闭包→分别粗搜所有允许候选→回映每候选→对全部候选建立原图精搜窗口→窗口去重但保留 seed 关联→分别精搜→按 G_i 产生 p_i→对应/拟合/独立门→复制→排空。局部窗口的**参考点可达域**由粗定位误差界扩张；crop 像素范围另加旋转/尺度后的模型支撑和金字塔边界 halo，两者不得混同。`CoarseErrorBound` 和 halo 来自固定 Profile/模型支撑验证，无已资格界则粗层只能排序，必须扫描完整批准原图域才能声明搜索完整。

A 或 B 粗层消失、候选被截断、窗口覆盖未经资格：预配置 `DirectFineOnIncomplete` 时搜索原始批准域（不是围绕假中心的小窗），仍共用预算；否则返回 Rejected/`CoarseSupportInsufficient` 和非完整证据，不返回原图 NoCandidate。遮挡或短支撑时不自动降低 MinScore、不增尺度自由度、不扩大域。先保留真实证据，宿主可新建修订/attempt。无候选也需区分“原图完整域已搜”与“只搜粗种子附近”。

坐标合成算例（非现场精度门）：q=`(row=220,column=440)`，训练 crop=`(100,200)`、`k_t=0.5` 得 `(59.75,119.75)`；搜索像素点经 `k_s=0.25` 为 `(54.625,109.625)`，逆映正好 q。若只除以 k，会出现行列各 1.5 px 的搜索回映误差。训练搜索比例不等还必须补 `M_t⁻¹ F_t`，不能只复原搜索坐标。非对称模板、非零 origin offset、非整数 q、90°和边界裁切共同进入 adapter Golden。

#### 4.7.3 锚点平移、刚体/相似和仿射边界

若调用方明确 A 为锚点，实测 A 点为 `pA`，参考 A 点为 `qA`，刚体旋转 `R(theta)` 下平移为：

`tA = pA - R(theta) qA`。

若明确 B 为锚点，使用 `tB = pB - R(theta) qB`。锚点策略须显式 `TranslationPolicy=Anchor`；默认 `LeastSquares` 等权拟合，不能一面用 anchor 公式一面声称最小二乘。若只要求平移且角度冻结为 0，输出 `TranslationOnly` 能力结果，不能冒双 Mark 刚体资格。锚点不决定产品目标关联或质量放行。

两点向量 `v=qB-qA`、`w=pB-pA`：

- 刚体：`theta=atan2(cross(v,w), dot(v,w))`，默认 `t=(pA+pB)/2-R(theta)*(qA+qB)/2`；采用 `vector_to_rigid` 的等权最小二乘语义。Anchor 则用上述 tA/tB。尺度固定 1；`|w|≠|v|` 会留下残差，不能用距离比缩放掩盖。
- 相似：`s=|w|/|v|`，`theta` 同上，`t=pA-sR(theta)qA`；尺度 `s` 必须作为独立输出，不能被当作误差吞掉。
- 一般仿射：两点不能唯一确定一般仿射；需要至少第三个非共线对应和该切片独立资格。两点不能证明剪切、各向异性尺度或透视正确。

有长度差的反例：qA=`(0,0)`，qB=`(100,0)`，pA=`(10,20)`，pB=`(112,20)`。LeastSquares 刚体 t=`(11,20)`、两点残差各 1；Anchor-A t=`(10,20)`、A 残差 0/B 残差 2；相似 s=1.02、t=`(10,20)`、两点拟合残差 0。每种都保留长度比；任何残差是否可用由 Profile 明确门判，不根据此合成例定客户门。恰好两个点的零残差不是独立复核，应记录 `IndependentValidation=Unavailable`，不能伪造角度不确定度。

`ObservationMode=OrientedSingle` 时，一个**已验证非对称、有唯一方向**的模型可给刚体位姿：参考物理方向 θ_ref、恢复到原图后的观测 θ_obs，θ=`wrap(θ_obs-θ_ref)`，t=`p-Rq`。Generic 若拟合相似还须有已资格的尺度结果；NCC 只能固定尺度。圆、重复旋转对称、镜像或方向资格未知不能用此模式。双 Mark PointPairs 缺点默认不降级；宿主须在新请求中显式选 OrientedSingle/TranslationOnly 并保留缺失来源。这里的 θ_ref 是模板实际创建方向，不等于 A-B 连线角 α，也不把 native 相对模板角当全局绝对角。双点连线旋转和各模型方向应按 OrientationTolerance 复核（圆形无方向则标不适用）。

参考算例：`qA=(0,0), qB=(100,0), pA=(10,20), pB=(10,120)`，刚体结果应为 `theta=+π/2`、`t=(10,20)`；相似结果的尺度为 1。该算例只验证几何链，不证明物理单位、标定或生产资格。

#### 4.7.4 必测失败分支和验收

| 反例 | 必须保留的输入事实 | 状态/输出 | 恢复与可判定验收 |
|---|---|---|---|
| 只找到 A 或只找到 B | 缺失 slot、完整搜索范围、另一 slot 的候选/边界原因 | `Partial` + `NoCandidate` 或 `Rejected`；无整体位姿 | 不触发双点备用，不输出角度；验收为缺失原因和已找到候选均可追溯 |
| A/B 互换 | 两个候选均满足局部门、身份关系和交换解释 | `Ambiguous`；保留两套对应和变换 | 由调用方增加不对称先验或人工选择并新建 attempt；不得按左右/返回顺序选解 |
| 一个 slot 多个候选 | 原始候选数、分数、间距、支撑和组合预算 | `Ambiguous` 或 `EvidenceTruncated` | 先完成候选/组合预算；达到上限不能称唯一最优，不能跨方法分数比较 |
| 基线过短/零长 | `B`、像素/物理单位、误差估计和 Profile 门 | `DegenerateGeometry` | 重新编程更大基线或改用途；验收为不返回稳定角度/相似位姿 |
| 缩小后 A 或 B 消失 | 缩放比例、特征支撑、金字塔层和粗层结果 | `Rejected`/`CoarseSupportInsufficient`，非完整；原图完整域补搜后才能 NoCandidate | 预配置时回原图批准域精搜；否则停止，不把粗层失败写成原图未检出 |
| 原图回映错误 | crop 原点、resize 比例、frame/矩阵方向、模型原点 | `ContractMismatch` 或坐标校验失败 | 只复合一次变换；非对称模型、非整数缩放和 90° Golden 必须回到参考坐标误差门内 |
| 两点通过但仿射被请求 | 两对应点、请求自由度、实际点数 | `DegenerateGeometry`/`UnsupportedMethod` | 要求第三个非共线点并重新运行；不得以零残差放行一般仿射 |

该反例必须同时覆盖 Shape 和 NCC 至少一条已批准路线，并在两个消费者中使用不同 A/B 距离、搜索域和并发实例。验收只证明候选、几何、坐标和资源语义；不证明任何制程判定或设备动作。

#### 4.7.5 A/B 局部粗精调用的装配闭包（后续adapter规格）

§4.7.1–4的算法与算例保持。一个GlobalPose请求只含已冻结FeatureSlot A/B（需更多点时按原契约显式扩展），各slot.Model为Fine精确资产，CoarsePlan.CoarseModelRef为该slot独立Coarse精确资产；不把ModelAssets RootRef换成另一slot/model/hash。A/B可能引用同一源图但独立模型内容/租约/原点/ReferencePointDomain及PixelSupportDomain；其输入完全由§3/5.1的现有字段、ModelDescriptor.TrainingSource/TrainingPose/Origin/SupportRef和FrameRef.Derivation取得，不新增“双Mark业务DTO”。

| 调用 | 精确输入与中心/ROI | 输出与所有权 |
|---|---|---|
| A-Coarse / B-Coarse（分别） | operation已持有原Search FrameRef/lease；slot各自CoarseModelRef/descriptor/content；CoarsePlan的实际SearchFactor/TrainingFactor；SearchDomain原批准参考点域→Fs映射后的参考点可达域，pixel support另halo；训练crop/Ft/Mt/默认重心c/请求origin o来自该模型描述 | BackendSearchInput.Slot保持原FeatureId；Stage=Coarse，ModelLease为本次Coarse模型；保留每MatchResult原index/score/native矩阵、所有seed及完整性，原搜索观察点用§4.7.2 G_i恢复，不能直接用native Row/Column |
| A-Fine / B-Fine（各seed窗口分别） | slot.Fine模型；原Search frame实际crop/halo和对应Fs，默认k_s=1；所有seed映回原参考点域，窗口合并仍保留seed关联，crop原点与ROI几何单独留ActualParameters/InputRefs；fine ReferencePointDomain与PixelSupportDomain从原批准域及支撑规则有界生成 | Stage=Fine；同slot同原模型重复窗口候选按§4.10稳定规则去重，跨slot身份不合并；point=G_i(q_i)，A/B对应只用稳定FeatureId；两个模型方向不代替连线角 |
| DirectFineOnIncomplete | 仅预配置原slot Fine+原批准完整SearchDomain，不能从粗未检出构假小窗；同一总deadline/累计bytes/candidates | 原批准域真实完成才Completed coverage；任一必需slot缺失保留全部已知候选，Pose=null，不训练、不换资产、不自动降自由度 |

每次BackendSearchInput.Request仍为完整已冻结请求，Slot携带该阶段选定参数；FrameLease/ModelLease/ReferencePointDomainLease/PixelSupportDomainLease必须与**实际**预处理/crop/model一致，不能传原描述但换内部图。适配器在自己的operation native临时域/图上reduce/crop/resize，实际F_t/F_s/crop/size/halo写原ActualParameters及InputRefs，公共Descriptor不热改；支撑/原点元信息欠缺则拒本模型用途。训练A-Fine/B-Fine及可选A-Coarse/B-Coarse各是独立BeginTrain新OperationId，完整候选由宿主显式组回模型资产绑定；任何一步失败旧四引用不变，不自动在生产请求补train。

阶段解析是本backend私有不可变调用记录，不增Core DTO：Fine解析Model=slot.Model，Coarse解析Model=slot.CoarsePlan.CoarseModelRef；搜索参数取slot.Parameters的已冻结路线值，再按实际k_t/k_s转换native角域/scale域并核所选descriptor训练范围，不能调用任选参数回调。Coarse未独立提供合法闭包参数时拒该粗策略并仅按预配置DirectFineOnIncomplete执行Fine。记录`FeatureId,Stage,ResolvedModelRef,ResolvedDescriptor,FrameRef,SearchCrop,F_t,F_s,M_t,ReferencePointDomainRef,PixelSupportDomainRef,NativeParameterReadback,SeedIndices`，全部来自原请求/描述/ROI/实际预处理，随ActualParameters/InputRefs诊断保存；不创造asset修订、域Owner或Production fact。源ReferencePointDomain/PixelSupportDomain由IRoiPort取得真实runs后仅生成本operation临时native域，父引用与映射保留，不要求上游存在未定义CreateDerivedRoi API。公共Slot身份始终原FeatureId/Fine引用，Backend实际模型核对按该显式阶段解析；不会把Coarse lease误验成Fine hash或覆盖原Slot。

双点输出继续用Correspondences/Residuals/Pose/GeometryDiagnostics：qA/qB、pA/pB、theta/t/允许scale与LengthRatio按§4.7.3，参考/实测中点和连线是宿主从这四点生成的**显示投影**，不用新Core字段或单独姿态Owner。A/B匹配中心与参考点可不同，必须用G_i(q_i)画point/line；连线姿态不能取mean(native angles)。对原方向有资格者按OrientationTolerance核模型方向，圆形无方向为NotApplicable。所有结果数组（候选、矩阵、对应、参数、Field/Rectified/Contours、artifact bytes）在预算核验后从native/借用源深复制，嵌套ImmutableArray不能包可变backing；复制完成也不等于native/lease排空，Completion仍等真实ResourcesReleased。结果可在模型/图像lease归还后由Host复查，后续运行/native修改不改变旧结果；artifact交接另按唯一OfferId。

### 4.8 DZ-XVision 快照的可迁移场景和禁止迁移项

来源快照为 [`DZ-XVision/20261004/README.md`](../../references/project-snapshots/DZ-XVision/20261004/README.md)，原始文件校验由同目录 `source-manifest.json` 管理。快照明确是 .NET Framework 4.7.2 WinForms、AsunImage 24.11 的只读现场参考，不是本模块的实现或版本基线。

从 `Tools/ToolMark.cs`、`Tools/ToolShapeModel.cs`、`Tools/ToolNModel.cs` 和 `DZXVision.cs` 可迁移的**使用场景**如下：

1. **分别保存和读回模型。** Mark 的 Shape/NCC 路线分别创建、保存、选择、读回和释放模型；模型文件与工具名称/类型关联。迁移为不可变 `modelId/revision/hash/method` 闭包，保存成功后必须重新打开和核对原点、domain、通道及可查询参数，不能把目录存在或 UI 提示当作模型可用。
2. **运行前处理图像。** 快照在查找前可选应用图像效果，再把处理后的图像送入 Shape/NCC 查找。迁移时必须把预处理链、参数修订、输入 hash 和输出有效域作为 `FrameRef` 的派生证据；预处理失败返回 `InputUnavailable`/`BackendFailure`，不得静默改用未处理图像。
3. **参考/实测位姿成对记录。** 快照保留参考模型行、列、角度与运行结果行、列、角度，再进行位姿计算。迁移为 `ReferencePose` 与 `ObservedPose` 两组不可变证据；角度周期、row/column 方向和原点必须显式记录，不把显示坐标或返回数组序号当身份。
4. **多 Mark 的中点和连线角。** 快照在两个有效 Mark 间计算中点和连线角，再生成刚体变换。迁移时只在稳定 A/B 对应、基线和质量门通过后计算；保留逐点残差，不以中点覆盖两个原始观察。
5. **失败可解释。** 快照区分预处理异常、查找异常、查找返回空结果和成功但结果字段为空。模块必须维持这些区别：异常是 `BackendFailure`/`InputUnavailable`，完整查找无候选是 `NoCandidate`，结果字段不完整是 `EvidenceTruncated`/`QualityRejected`，不能全部压成布尔 `isSuccess=false`。

快照中“定位失败后弹窗选择继续/中止/重测，重测时回到运动流程”的行为属于产品编排、设备动作和板级重试，**禁止写入本模块**。本模块只提供以下计算级重试边界：

- 每次重试必须新建 `operationId`/attempt，固定记录原失败 operation、输入 hash、模型 revision、失败码和重试原因；旧结果不可被覆盖。
- 默认不自动重试 `InvalidRequest`、`ModelUnavailable`、`ContractMismatch`、`Ambiguous`、`DegenerateGeometry`、`QualityRejected` 或证据截断；这些需要修正配置、提供额外先验或由调用方决定新请求。
- 对明确的瞬态适配器/读取错误，可由调用方在预先批准的 `RetryPolicy` 中给出最大次数、退避和总 deadline；每次重试仍须重新取得只读帧/模型租约，不能复用未知状态的 native handle。
- `NoCandidate` 只有在同一 Profile 明确允许且完整搜索确实结束时才可进入备用或重试；缩小域、预处理、角度/偏移参数不得在重试中偷偷改变。改变任何输入或参数都形成新配置修订和新 attempt。
- 取消、超时、`DrainUnknown` 或 native 资源未知时，先完成排空/隔离，再决定是否新建 attempt；不能并发重试同一模型实例，也不能用重试掩盖排空失败。

该场景吸收的是“模型闭包、参考/实测位姿、错误分层、重试身份和资源隔离”，不吸收快照中的板级循环、MES 上传、运动回退、出板/中止、全局静态状态或制程 PASS/ERROR。快照中的 `MarkPoints`/`OldMarkPoints`、中点和连线角只作为场景证据，不成为本模块新的公共字段名；正式字段仍由 Contract/Schema Owner 采纳。

### 4.9 创建、训练、打开、导出与参数推荐

首个图像适配切片冻结 Generic Shape 与 NCC；二者共用编排/预算但训练参数为判别联合。训练是独立工程操作，不是 Align 的失败恢复。所有路径：校验→取只读模板租约→验证有效域/通道/支撑→预处理派生→新 native 模型→训练/读回→导出候选→新实例读回比对→复制 artifact→清理新旧临时句柄→终态。旧发布 revision 全程不变。

| 路线 | 必填训练项、原生顺序、查询与搜索约束 |
|---|---|
| Generic Shape（图像） | `create_generic_shape_model`→`set_generic_shape_model_param`设置metric、angle_start/end、iso_scale_min/max/step、num_levels、contrast_low/high/min_size及min_contrast、optimization→`train_generic_shape_model`→origin_row/column→`get_generic_shape_model_param`实际读回→write_shape_model→read_shape_model新句柄核对→clear_shape_model。create不等于已训练。保存域重心/原点/训练态/通道；运行在租约内设置angle_start/end、restrict_iso_scale_min/max、min_score、num_matches、max_overlap、greediness、timeout，训练结构不变；不存在restrict_angle参数。border_shape_models=false，A/B独立搜索，避免多模型border相互影响 |
| NCC（图像） | 只接受单通道 byte/uint2，通道选择或强度转换须先形成显式派生 frame；`create_ncc_model(Template,NumLevels,AngleStart,AngleExtent,AngleStep,Metric)`→`set_ncc_model_origin` 相对重心偏移→`get_ncc_model_params`/`get_ncc_model_origin`→`write_ncc_model`→`read_ncc_model` 新句柄核对→`clear_ncc_model`。训练项：levels、角域、AngleStep、Metric=`use_polarity/ignore_global_polarity`；无尺度参数。常量模板拒绝；近常量有效纹理门来自 Profile，不编造方差阈值。官方要求最高层至少八个模板点并可能降层，读回实际 levels，不把八点当生产检出证明 |

Generic 默认层/contrast 可在**训练草稿**用官方 `auto`；NCC 的 levels/AngleStep 可用官方 `auto`。`AutoOrFixed<T>` 必须是显式判别类型，不能用 0/-1 在 Core 冒充普通数值。训练结果保留 Requested 与 Resolved 两份、模板/后端/adapter/profile hash、状态、查询不可得项和理由；不可查询影响复现时该候选不可搜索。运行参数不使用 auto 门、不静默修改发布模型。Generic 查询实际估计值与 `_param` 请求值分别留存；改变官方列明需重训的结构参数必须生成新训练 revision；允许的 run-only 修改仅发生在本 operation 的模型租约内。

角域统一存规范 start + extent，adapter 转 Generic 的 start/end 或 NCC 的 start/extent；跨 ±π 时保留环域，不直接比较两个端点。NCC 创建时离散角采样可能扩张/调整实际角域/步长，读回请求与实际；搜索域必须包含于有效训练闭包且最终观测仍通过请求角域，越范围 native 前拒绝，不能依赖 native 自动 clip。固定角 extent=0 单独覆盖；不得用 extent=2π 表示“固定 0”。零 extent 的具体 adapter 绑定和结果受测试门约束，不改变 Core 的固定角语义。

`CoarsePlan(TrainingFactor:PositiveRational,SearchFactor:PositiveRational,Interpolation:Constant,CoarseErrorBound:double?,CoverageQualification:ProfileRef?,DirectFineOnIncomplete:bool,CoarseModelRef)` 由工程 Profile 选择并冻结；无粗策略用null，不另设相互冲突Enabled。PositiveRational分子/分母为正long、分子≤分母、计算乘积checked；误差界单位为原搜索frame像素且有限非负，未资格则null。自动建议采用有限闭集：Profile 提供有序 k/层数候选和最低支撑/纹理门；逐项用同一训练域构建并读回实际层数/支持，无法达门时拒绝该项；只有独立 Replay 比较误检/漏检与端到端资源后才形成 `ParameterProposal`。选择次序为先满足质量门，再按冻结 P95、峰值资源、候选顺序稳定决胜；无完整测量则不自动选择。proposal 包含输入及模型 hash、所有候选/拒绝原因、实测来源和有效 Profile revision；输入/revision 变化则过期。采用由宿主新建训练/配置 revision，不回写生产参数。推荐为独立工程操作，入口见§5，不增加生产自动调参入口。

Inspect（打开/校验）是独立无 UI 操作：读取不可变资产 bytes→校验 SHA-256→按 Method 读 native 模型→读取描述可查询项→逐项对照 ExpectedDescriptor→关闭 native 模型→返回 Comparisons；不可查询项从有 hash 绑定的训练清单取并标来源，缺清单则 ContractMismatch。Export 不改变源模型：打开→写出候选 bytes→关闭流→算 hash→用新句柄读回→参数/原点/训练闭包对照→释放；native 格式由 write/read 配对决定，不自行改字节。write/read 需要文件路径时只用 adapter 自有单操作临时文件，关流后读取并删除**该文件**，不清其它目录；无磁盘权限/空间时 BackendFailure，不退回手写格式。结果只是 artifact，由 model-assets 完成持久化、发布和未知回执查询；Core 无 Store/Activate/Delete。

### 4.10 候选枚举、遮挡、关联与备用闭包

`EnumerationMode=AllReported` 时 Generic `num_matches='all'/0`、NCC `NumMatches=0`，保留冻结 min_score/max_overlap/levels/greediness 对返回集合的影响。`TopK` 时原生取 MaxCandidates，**返回条数少于 K 也不证明没有其它有效解释**：金字塔、重叠抑制和检索门仍可能移除候选。AllReported 只表示完整取得该算法返回集合，不承诺数学全局最优或物理实例全集；部署唯一性还依赖有代表性的对称/重复/遮挡负样本资格。

MaxCandidates 是输出/组合预算。原生 AllReported 在返回前可能耗费大量内存，Core 不能靠返回后截断声称 native 有硬界。预估的搜索空间/模型规模、adapter 资源能力及必要的宿主进程边界先参与准入；无法满足内存硬界的请求拒绝或由宿主隔离运行，不能设 0 后宣称有界。返回超过预算保存允许数量及总已观察数量、截断原因；Evidence=Truncated，Pose 不具唯一性资格。TopK 仅可作候选导航/诊断；PointPairs 唯一用途禁止用它代替 AllReported，除非 Profile 已明确限定目标空间且另有覆盖/身份资格证据。

关联顺序冻结：按 slot ID 排序→筛支撑/角域/尺度/分数门（不删被拒原候选）→按已批准空间先验建立边→同一实际目标的重复观测按 Coordinate/ROI 提供的等价门分组→有限一对一组合→逐组合 fit→逐点/整体/方向/身份门→按 PoseEquivalenceTolerance 合并等价解释→0 解 Rejected 或完整无检索候选 NoCandidate、1 解有条件可用、≥2 解 Ambiguous。候选排序仅用于稳定复现，为 featureId/model revision/stage/row/column/规范 angle/原生 index；不是按分数选第一项。MaxCombinations 达限立即停止扩展并返回截断，不能称唯一最优；A×B 数量先用 checked 运算估计，溢出为 ResourceExceeded。A/B 外观相同且可达域重叠时，即使分别命名模型也不证明身份；必须保留互换解释。

遮挡不等于 score 的 `1-score`。Shape 的可见轮廓、NCC 的灰度相关、Planar 的支撑有不同语义；如无可查询/可验证可见比例，SupportEvidence 标 Unknown，不补一个百分比。Shape 可容许已资格的局部遮挡但必须验方向/几何；NCC 强遮挡下通常降相关，只返回观察，不默认采用。补黑、halo 外无数据、反光饱和和 crop 截断不能当有效支持。Profile 没有部分支撑资格时该候选 Rejected，保留支撑和拒绝原因。

备用只允许 `CompleteSearchNoCandidate`：每个必需slot在完整批准域/合法原图支持下完整搜索且**原始返回候选均为零**，native已返回且该尝试租约已排空。A找到/B缺失虽然可最终NoCandidate并保留A，但属于Partial，不触发整个双Mark备用；有原始候选但质量门全拒也不触发。TopK/Unknown/CoarseCoverageUnqualified/歧义/训练失败都不触发。路线表中的NCC↔Shape是可配置候选，不是默认链。每个AttemptPlan固定主/备模型参数和触发门，全部subattempt共用一个operation截止/预算；训练/重新编程永远新operation。改变未列入AttemptPlan的预处理/窗口/角域/scale/model revision为新配置，不是无记录搜索优化。

Planar、Local、传统 scaled/aniso shape、XLD 输入、一般仿射/投影均是架构能力，具体步骤冻结于 §4.11–4.13、类型于 §3.6–3.7，不留给实现者选路线。adapter 未实现/未关闭该路线的软件资格门时返回 UnsupportedMethod；不是因封装缺算子。复杂局部场连续逆不属于本模块承诺，不阻断原生局部诊断能力。

### 4.11 传统 scaled/aniso 与 XLD 训练搜索实施卡

触发：宿主明确引用历史/独立 scaled/aniso 模型或 XLD 模型，不凭 Generic 失败自动切换。输入为对应 TemplateSource、route 参数、模型描述和运行图。图像支持按已选择通道/有效域冻结；XLD 必須来自已记录上游轮廓/坐标版本，训练前将其坐标统一到 TrainingFrame，超过总点数/字节预算直接拒绝。

1. Scaled 图像用 `create_scaled_shape_model`，Aniso 图像用 `create_aniso_shape_model`；XLD 分别 `create_scaled_shape_model_xld`/`create_aniso_shape_model_xld`，Generic XLD 仍 create→train。XLD 无灰度 Contrast 的分支只传官方适用项，不把 image 参数全套塞给 XLD。有效训练 metric 要与 XLD 支持吻合，未记录极性来源则不宣称方向资格。
2. 按模板 domain 重心（image）/官方 XLD 包围框默认原点设置 `set_shape_model_origin`；保存原点、各训练范围及请求/actual。`get_shape_model_params` 的 Scaled 尺度元组单值、Aniso 两值按 row/column 取，长度不符则 BackendFailure；`get_shape_model_origin` 读回。write/read/clear shape 形成独立读回闭包，不能拿 native 类型名推断模型族。
3. 本 operation 独占模型；`set_shape_model_param(border_shape_models,false)`，timeout 为剩余预算（ms，向上取整，已有<=0则不派发），不改全局。调用对应 find_scaled/find_aniso，参数域为训练闭包子域；reject 越范围请求，不接受 native 自动 clip。Pregeneration=Complete 的同句柄不同图尺寸并发不安全，所有模式一律实例独占。
4. 返回数组长度完全一致、正尺度；Scaled 同一 scale，Aniso 两轴 scales。用原生 row/column轴 `H=T(Row,Column) R(Angle) D(ScaleR,ScaleC)`，再走 §4.7.2 的 K/M/F 链。Aniso 是5自由度子集，不等于一般6自由度仿射；不可补 shear。MaxDeformationPixels 只放宽匹配精修，不生成 local field，也不能用它吞掉应检缺损/尺寸变化。
5. 全部候选进入相同完整性/身份/支撑门；角域修边后仍验最终返回角/scale，越域保留诊断。唯一候选也先验用途门；模型结构/Metric/Optimization/Pregeneration 变化新 revision，结果 score 语义和 Golden 不能沿用未复核旧门。

验收：普通/Scaled 模型被送 find_aniso 时可能返回 unit/等比 scale，不赋予 Aniso 能力；只有描述 route 与训练能力都对应才接纳。合成 aniso 原点反例：训练重心 rc=(12,20)、offset=(-2,+3)、点=(11,25)，S_r=2/S_c=0.5、θ=π/2、native t=(100,200)，K(H) 输出 rc=(98.25,202.5)，原点=(99.25,200.5)，不能直接取 native t。真实算子/轮廓/score 另以 adapter Golden 核对。空 XLD、常量 image、range clip、极性丢失、max_deformation 32/33、native timeout、写出失败均走 §5–7，不产生半模型 artifact。

### 4.12 Planar 与一般 Affine/Projective 实施卡

**Planar 搜索**的消费者是可解释平面注册/透视诊断，不证明三维姿态、高度或毫米计量。处理顺序：验证平面证据与校正来源→模板有效域/轮廓→`create_planar_uncalib_deformable_model`（XLD 对应 `_xld`）→设置/查询原点与 `get_deformable_model_params`→write/read_deformable 独立读回→find_planar_uncalib→按每候选9元素拆 HomMat2D→中心/源目标链→geometry gate→候选与独立验证→复制/clear_deformable→drain。

create 的 AngleStart/AngleExtent/ScaleRMax/ScaleCMax **不使用**；adapter 传固定兼容占位，但描述中不宣称这些是训练搜索上限。BaseRow/ColumnScaleMin 影响 auto levels，AngleStep/scale step 读回。Metric/PartSize/MinComponentSize/Contrast 影响小方向标记是否被抑制，保存实际轮廓/支撑；不是只验参数合法。find 用冻结基础角域/双尺度、分数/数量/overlap/levels/greediness，GenParam 的 subpixel 与 angle_change_restriction、aniso_scale_change_restriction 显式映射；base search 范围不限制全部后续投影畸变。不得杜撰 `deformation_model='affine'`、per-model deformable timeout/border setter；本切片完整图内策略，若进程全局 border 模式不符合记录基线则拒绝适用资格，不能临时切全局影响其它实例。

HomMat2D 长度必须9×Score长度，空返回完整性按 §4.10；从 H 用 `projective_trans_pixel(H,0,0)` 得原点中心，G=`F_s⁻¹ K(H) M_t⁻¹ F_t`，K 仍同中心/corner共轭（projective矩阵保留全部9值）。不拆不存在的 angle/scale，Candidate 的这些字段 null。point domain 仍是原训练domain重心，不随设置 origin 移动。输出支撑不足/任何全域 gate失败为 Rejected，原矩阵留证；不能清零第三行改成 affine，也不能自动改为 rigid。原生无硬停止入口时 Query 等待/隔离，不能伪造 deadline 已排空。

**点对拟合**由 BeginFit/GlobalPose 的 FitPolicy 明确 kind，源目标同单位/修订。Rigid/Similarity 用 `vector_to_rigid`/`vector_to_similarity`；Affine 用 `vector_to_hom_mat2d` 等权最小二乘；Projective 固定 `vector_to_proj_hom_mat2d(Method='normalized_dlt')`，不凭 score 构 covariance，不隐藏 RANSAC 丢点。算子直接接受 Core Cartesian 数学点并返回数学中心矩阵时不用加0.5；只有转成 HALCON image-edge矩阵用于 iconic 操作才换基和 C 共轭一次。反之原生匹配矩阵按 §4.7.2 K 还原。CoordinatePort 包装既有坐标模块用于 Compose/Invert/Transform，不在 Alignment 另实现坐标库。

拟合前：刚体/相似≥2足够基线；Affine≥3非共线且至少一三角面积≥MinTriangleArea；Projective≥4，控制点任意三点不得共线至技术门且须覆盖用途域的要求分布。重复ID/数组错长/单位未转换拒绝；不得悄悄删异常点。拟合后：所有点计算 `e_i=p_i-T(q_i)`，max/rms残差分别验门；返回独立 holdout（若 Profile 无 holdout则 Unavailable）；反射/条件/支持/全域门不过拒绝用途。分布检查采用 Roi/CoordinatePort 提供的数值证据，不按图像“看起来均匀”猜测。

Projective显示/等价比较规范化：取绝对值最大矩阵元素的第一索引j，除以其有符号值使h_j=1；全零/非有限拒绝，不固定除h33。资格输入保留该candidate实际CentreMatrix的九个Binary64系数，**不以经过显示归一化舍入的矩阵代替**。全域分母证据按§4.14从现有IRoiPort完整Runs取得：将每run的闭像素支撑矩形映到源frame，求`w=h31*x+h32*y+h33`在四角的精确极值；检查每片不跨零，再以全域`min(abs(w))/max(abs(w))`验门。不同不连通片可分别为正/负，不跨孔洞补域。遗漏run、只验中心/四个外接框角或预算截断不能签WholeDomain。Jacobian尺度/方向/条件、伸缩/shear证据仍由坐标/几何端口有界查询，缺全域界不签完整几何资格；分母通过不代替这些门。一般Affine仍检查线性块的det/条件/反射/伸缩/shear。

反例：H=[[1,0,0],[0,1,0],[1,0,-0.5]] 在 x∈[0,1] 穿 w=0；四个角可各自有限，det非零也不可采用该整个域。相同 H 的任意非零倍数应得到同规范形和 gate结论。两点 affine、三点projective、共线三点affine一律 DegenerateGeometry，四点零训练残差不代替独立验证；任何重新拟合到更低自由度须新显式请求。

### 4.13 Local deformable 诊断实施卡

本切片交付原生局部搜索、场/整平图/轮廓的无UI输出，不承诺全域逆或质量事实。来源、生命周期与Planar相同：create_local_deformable（image/XLD对应分支）→set/get origin/params→独立write/read→find_local_deformable→校验数量/尺寸/支撑→复制请求 outputs→clear→drain。基本角域/scale只是基础搜索范围。Smoothness≥3，官方典型11不作为默认或硬应变上限；四方向 expand为非负整数，输出像素/场字节先 checked 和能力估计。禁止用标量 angle/scale/H 统一压缩原生 local结果。

1. ResultType 显式映射 Field→vector_field、Rectified→image_rectified、Contours→deformed_contours；未请求的项为空不是“完整场”。以匹配 index 关联 iconic 对象与 score/row/column，对象数/元组长度不符为 BackendFailure，不能 zip 截断。
2. 使用§3.7 RasterGrid/RasterSourceMap；native仍有效时以get_image_type/get_domain及有界批次get_grayval形成SourcePrecision、值和Valid。SourcePrecision缺字段/类型不符为ContractMismatch；Unreported按§3.7只给RawRasterOnly。Rows/Columns为rectified-grid→搜索图绝对像素采样，不能取负当逆。原点是domain重心，grid大小是domain包围框加扩边；model origin/返回位置不等于grid左上。
3. Field 值需有限且有真实源域/插值支持。对 integer/neighbour/灰度双线性先验各适用邻域都在原有效域，再允许 map/整平消费；不能先 map_image 再查越界。map 的线性地址类型不替调用方保证有效性。扩边不能产生原图外的有效像素，mask独立保存。Field.SourcePrecision、搜索crop与有效域都随本 operation封存。
4. GridBinding=RawRasterOnly 时可输出原生field、rectified及diagnostic；不输出模板/CAD/world 位移。QualifiedTemplateBinding 才可对 grid中心点用记录映射取模板点，并以坐标端口转同基准计算 observation；这种差值也仅是显式取样事实，不称材料应变/原生连续场Jacobian。
5. 弯曲、fold、孔洞、边界外推、跨组件重叠、非有限field或超预算分别保留原因；不能因整平后残差低判定缺陷消失。要求逆/全域单射/计量的 Profile 在本版不支持，返回 UnsupportedMethod/NotEvaluated；可请求独立 coordinate-geometry 资格，不能在本模块自建Delaunay逆。

可判定反例：source x→3x+2，目的11的逆=3；把目的点位移取负得−13，并非逆。f=(x²−y²,2xy) 在环域1≤x²+y²≤4局部det>0但(1,0)、(−1,0)同像，禁止“差分无负det就全域可逆”。输出grid 1×N没有二维cell；可以显示采样，不补二维面积。训练bounds/expand/非零origin的具体adapter索引，需真实非对称Golden验证；欠缺时RawRasterOnly是完整且诚实的诊断结果，不把资格缺失误当客户物理阈值。

### 4.14 几何证据端口与重放

Affine/Projective全域资格使用注入`IGeometryEvidencePort`：唯一签名为`ValueTask<GeometryEvidence> EvaluateAsync(GeometryEvidenceRequest request, CancellationToken cancellationToken)`，底层数值责任由coordinate-geometry宿主适配承担，Alignment不新增平行几何实现。`GeometryEvidenceRequest(Transform:Transform2D,Gate:GeometryGate,Domain:GeometryDomainSnapshot,ExecutionLimits:ExecutionLimits,TimeProvider:TimeProvider,DeadlineTimestamp:long)`；`GeometryEvidence(Status:Qualified/Rejected/NotEvaluated,NormalizedDet?,ConditionNumber?,Denominator:ProjectiveDenominatorEvidence?,Bounds:ImmutableArray<GeometryBound>,DomainCoverage:GeometryCoverage,SourceRevision,ReasonKeys)`。GeometryBound仍为`Quantity:DenominatorRatio/JacobianScaleMin/JacobianScaleMax/Shear/Orientation,Lower,Upper,DomainRef,ProofKind:WholeDomain/Sampled`；DenominatorRatio摘要必须由同结果Denominator得出，不以独立标量或WholeDomain标签代替证据。Affine的Denominator=null；Projective请求完整用途时非null且WholeDomain才可用。纯点拟合诊断可不调用端口，Qualified用途必须验全部适用门。请求TimeProvider为Engine.Create注入的同一实例，DeadlineTimestamp为本operation同一单调截止点，端口不得用UTC或另一时钟重置预算。调用和租约排空按§5–6。

**真实可取得的域输入：** `GeometryDomainSnapshot(DomainRef,PixelFrame:FrameDefinition,Runs:ImmutableArray<PixelRun>,PixelCartesianToSource:Transform2D,SupportConvention:ClosedPixelCells)`。Engine在operation内调用已有IRoiPort.AcquireAsync(Gate.UseDomain,token)，核lease.FrameId/Revision等于UseDomain.FrameId/Revision并复制完整已排序/非重叠Runs；DomainRef直接取Gate.UseDomain，PixelCartesianToSource直接取Gate同名字段，PixelFrame取该映射.Source。不得读不存在的lease.ContentHash或隐式查询映射。Acquire的宿主适配必须核输入DomainRef的ID/revision/hash与ROI Owner绑定内容一致并返回该域完整Runs，无法核实则Acquire失败；Engine核公开frame/revision、非空Runs、顺序/边界和映射，不能声称自己读取了lease未提供的hash。域revision与frame revision分别比较，不把二者混同；宿主冻结映射.Source的真实frame revision，若请求含对应FrameRef还须与之相等。复制计Bytes，lease至调用真实返回后释放。Runs是现有public返回，不假设RoiPort提供未定义的凸片接口。PixelCartesianToSource必须是该pixel frame→Transform.Source的明确已批准**Affine或Rigid/Similarity/TranslationOnly**中心矩阵，仿射末行严格为(0,0,1)、非奇异、单位/源目标/revision一致。相同frame使用显式identity；世界frame只能通过该带单位的affine映射接入，此切片不接受非线性校正/Projective域映射，欠该能力返回NotEvaluated/GeometryNotQualified，不能用四角近似冒全域。

每run`(r,cFirst,cLast)`定义像素支撑矩形`x∈[cFirst-0.5,cLast+0.5], y∈[-r-0.5,-r+0.5]`。它是请求明确的ClosedPixelCells连续域，区别于只检查整数中心点；经affine映射为凸平行四边形。相邻run共享边不重复增加支撑面积；孔洞/组件间隔不补齐。`GeometryCoverage(DomainRef,SupportConvention,ExpectedRunCount:int,EvaluatedRunCount:int,Complete:bool)`，Expected=输入Runs.Length；Projective的Evaluated为已求w界的run条数，Affine为已完成适用几何界的run条数，不要求Affine伪造Denominator；不得只靠相等计数，以下RunIndex/RunValue必须逐一对应，缺行/重复行/换revision都拒。

**可返回和复核的分母证据：** `ProjectiveDenominatorEvidence(SourceMatrix:ImmutableArray<double>,Domain:GeometryDomainSnapshot,Pieces:ImmutableArray<DenominatorPiece>,MinAbs:ExactDyadic?,MaxAbs:ExactDyadic?,RatioThreshold:double,ThresholdPassed:bool?,Coverage:GeometryCoverage,NumericMethod:ExactBinary64DyadicV1)`；SourceMatrix九值按位等于request.Transform.CentreMatrix，Domain各值等于该冻结快照，RatioThreshold等于Gate值，不能拿另一个candidate或旧域的证据充数。`DenominatorPiece(RunIndex:int,RunValue:PixelRun,MinW:ExactDyadic,MaxW:ExactDyadic,Sign:Positive/Negative/ContainsZero)`；Pieces按RunIndex从0升序一对一列完整Runs，w为由输入矩阵产生的齐次分母，无量纲比率才参与阈值。ExactDyadic为`Mantissa:System.Numerics.BigInteger,Exponent2:int`，值=Mantissa×2^Exponent2；非零mantissa规范为奇数、零=(0,0)，Exponent2∈[-8192,8192]、mantissa编码bytes与所有witness计入ExecutionLimits.Bytes。它是公共有限证据值，不暴露native handle或数值库对象。

**固定求界步骤（几何端口负责实现）：** 以输入有限Binary64的精确二进制有理值解码为dyadic；整数run边加/减1/2为精确值。对每片四角先用PixelCartesianToSource的affine系数精确乘加得(x,y)，再用未重归一化的h31/h32/h33精确乘加求w；MinW/MaxW为四值最小/最大，线性w在凸片上的极值就在角点，故证据覆盖整片而非采样。若MinW≤0≤MaxW则ContainsZero，该片MinAbs=0且完整结果Rejected/ThresholdPassed=false；否则每片绝对值最小/最大可由两端取得。所有片的MinAbs为片最小值之min，MaxAbs为片最大值之max。Gate threshold转精确dyadic，直接比较`MinAbs≥threshold*MaxAbs`，并要求无ContainsZero且MaxAbs>0，不以round后的浮点比值签阈值通过。预算/deadline/取消中途停止则Complete=false，聚合MinAbs/MaxAbs/ThresholdPassed为null（已完成piece仍可诊断），绝不能签WholeDomain。端口的输出除状态也返回这些具体值，Alignment核矩阵/域/映射/threshold绑定、逐run一一对应、符号与聚合一致性并验精确交叉乘积；逐角求界的数值正确性仍由几何Owner实现与Golden证明，不在Alignment复制其几何算法。无此实现/证据的adapter只返回NotEvaluated。ExactBinary64DyadicV1只证明**提交矩阵系数**的分母事实，不证明拟合误差、物理精度或隐藏模型不确定度。

诊断摘要DenominatorRatio只在完整非跨零且MaxAbs>0时产生，表示MinAbs/MaxAbs的显示近似，决定仍取精确交叉乘积。SourceRevision绑定实现/数值方法revision；换H/域/映射/threshold任一字段均须新Evaluate，不接受仅旧Status=Qualified。H与可精确表示的非零缩放H有相同比率/拒识；浮点输入已经发生舍入的任意“近似倍数”不承诺数学完全相同，原始系数保留以解释门边界。

Replay 冻结原FrameRef/model bytes/参数/有效域/链/route与adapter版本，历史 OperationId 仅作为 ParentOperationId：在新的 Engine generation reserve 新ID重算，不重用旧接纳/事件。固定排序/容差比较候选、对应、矩阵、field和拒绝原因；native结果顺序变化仍保留原 index，不宣称字节相同。参考图的训练自匹配与synthetic例只验证闭包，不取代独立生产样本Golden。旧模型未知兼容组合拒绝，回退加载完整旧包/旧描述/旧Profile并新attempt；已运行生产事实仍不可重写。

## 5. 同步、异步、事件和状态

### 5.1 入口

命名空间 `Asun.Modules.Alignment2D`。以下是**待按本指导创建的 Core 接口**，不是已存在的 AsunImage API。公共 DTO 见 §3，状态及 ownership 见本节/§6；不得另造平台版本。操作 ticket 为 `OperationAdmission<T>` 判别联合：`Rejected(ValidationErrors)` 或 `Accepted(OperationHandle<T>)`；Rejected 不产生计算终态。Handle 包含 `OperationId,Generation,Completion:Task<OperationResult<T>>`，Completion 从接纳到真实排空释放才完成；取消不使它提前抛 OperationCanceledException。判别联合均定义成 abstract record 的 sealed nested变体，避免 bool+nullable多种组合；名称无同义变体。

```csharp
public interface IAlignmentEngine : IAsyncDisposable
{
    OperationId ReserveOperationId();
    OperationAdmission<AlignmentResult> BeginAlign(AlignmentRequest request, CancellationToken cancellationToken = default);
    OperationAdmission<TrainingResult> BeginTrain(TrainRequest request, CancellationToken cancellationToken = default);
    OperationAdmission<ModelInspection> BeginInspectModel(InspectModelRequest request, CancellationToken cancellationToken = default);
    OperationAdmission<ExportResult> BeginExportModel(ExportModelRequest request, CancellationToken cancellationToken = default);
    OperationAdmission<FitResult> BeginFit(FitRequest request, CancellationToken cancellationToken = default);
    OperationAdmission<ParameterProposal> BeginRecommend(RecommendationRequest request, CancellationToken cancellationToken = default);
    CallResult<AlignmentResult> Align(AlignmentRequest request, CancellationToken cancellationToken = default);
    ValueTask<CallResult<AlignmentResult>> AlignAsync(AlignmentRequest request, CancellationToken cancellationToken = default);
    OperationSnapshot Query(OperationId operationId);
    CancelReceipt RequestCancel(OperationId operationId);
    ReleaseReceipt ReleaseOperation(OperationId operationId);
    ValueTask<ShutdownReceipt> ShutdownAsync(DurationBudget waitBudget, CancellationToken waitCancellation = default);
    event EventHandler<AlignmentEvent> OperationEvent;
}
```

Engine 创建为 `AlignmentEngine.Create(EngineOptions,AlignmentPorts,TimeProvider)`（没有窗口/静态初始化），先验证端口、资源能力与 ApiMajor；Options 必填 queue/active/保留结果/预留 ID 上限，不隐式开无界队列。ID 由 Engine 生成 `generationGuid/sequence`，Reserve 占有界账本槽；所有 Begin 只接纳本 Engine 的未使用预留 ID。重复、旧 generation、未预留 ID 一律 Rejected；第一次 Begin 校验失败也消费该 ID，修正请求须新 ID。Release 可释放未使用预留/被拒/终态账本，不能释放在途 operation；只保留序列高水位，不建无限历史 HashSet。删除账本后旧 ID 不能再接纳，只能 Query=NotRetained，历史由调用方存。预留/账本满 Reserve 抛有类型 ResourceExceededException，不调用 native。

`Query` 立即返回不可变 `OperationSnapshot(Id,Generation,Phase,StopReason?,DrainStatus,Terminal?,LastSequence)`，未知 ID 为 NotRetained，不启动计算；查询不会把等待排空变终态。`RequestCancel` 幂等返回 Requested/AlreadyRequested/AlreadyTerminal/NotRetained；取消终态也等 drain。`ReleaseOperation` 返回 Released/Busy/NotRetained，不强行释放。`ShutdownAsync` 关闭准入、请求取消在途并等待：Completed（全部释放）/Pending（列在途 IDs、阶段和隔离要求）；waitBudget/waitCancellation 只结束关闭调用方等待，不能改变所有权。DisposeAsync 实际等待全部 drain，可超过运行 deadline；硬截止由宿主隔离边界处理，不能以 Dispose 超时释放句柄。

同步/异步便利入口分别 `CallResult<AlignmentResult> Align(request,token)`、`ValueTask<CallResult<AlignmentResult>> AlignAsync(request,token)`：只委托 BeginAlign；Rejected 返回 `CallResult.Rejected`，Accepted 等待同一 Completion 返回 `CallResult.Terminal`。同步入口不用于 UI；中途停止等待使用宿主对 Completion 的 WaitAsync，原 Handle/Engine 继续持有资源。不提供另一状态机或 `result.DrainCompletion`；拿到正式终态已经 ResourcesReleased。

端口签名闭包（同一 Core 命名空间，均可由最小模拟宿主实现）：

| 端口 | 方法及返回 | 生命周期/失败 |
|---|---|---|
| `IImageFramePort` | `ValueTask<IFrameLease> AcquireAsync(FrameRef,CancellationToken)`；lease=`Descriptor,Planes:ImmutableArray<PixelPlane>,DisposeAsync`；plane=`ReadOnlyMemory<byte>,StrideBytes,Width,Height,PixelFormat` | 只读 byte-backed 内存，stride/checked 长度满足格式；host 不得写/复用直至归还，Backend pin/copy 自担；不暴露 SDK handle |
| `IModelAssetPort` | `ValueTask<IModelContentLease> AcquireAsync(ModelRef,CancellationToken)`；lease=`Descriptor,Content:ReadOnlyMemory<byte>,DisposeAsync` | hash/描述一致不可变；不提供 Store/Publish；保存 artifact 是外部 Owner 调用，不靠该 lease 热更新 |
| `IRoiPort` | `ValueTask<IDomainLease> AcquireAsync(DomainRef,CancellationToken)`；lease=`FrameId,Revision,Runs:ImmutableArray<PixelRun>,DisposeAsync`；run=`Row,FirstColumn,LastColumn` | 按行排序非重叠整数 run、含两端、界内；原域与参考点域/像素支持域分开，mask 不由 bounds 猜 |
| `ICoordinatePort` | `Transform2D Compose(Transform2D after,Transform2D before)`、`Invert(Transform2D)`、`CartesianPoint TransformPoint(Transform2D,CartesianPoint)`、`CartesianPoint ToCartesian(PixelPoint,FrameDefinition)`、`PixelPoint ToPixel(CartesianPoint,FrameDefinition)` | 校验 frame/revision/方向/单位/非奇异；world 转换另需带已批准映射的 Transform2D，不隐式自标定；复用 Coordinates 的宿主适配，不建同义 math 库 |
| `IAlignmentBackend` | `BackendCapabilities GetCapabilities()`；`ValueTask<BackendResult<CandidateSet>> SearchAsync(BackendSearchInput,BackendContext)`、`…<TrainingResult> TrainAsync(BackendTrainInput,BackendContext)`、`…<ModelInspection> InspectAsync(BackendModelInput,BackendContext)`、`…<ExportResult> ExportAsync(BackendModelInput,BackendContext)`、`…<FitResult> FitAsync(FitRequest,BackendContext)` | input 为冻结请求 + 此 operation 帧/模型/域 lease；backend 不取得产品服务。每个方法仅在 native 全部真实返回、DTO 已复制、native 临时句柄释放后完成；不能用外层超时任务冒充完成 |
| `IGeometryEvidencePort`（Affine/Projective用途必需） | §4.14 `EvaluateAsync` | 同样排空；无全域证据则不签用途资格，模拟结果不得当真实几何算法证明 |
| `IExecutionDiagnostics`（可选） | `void Record(AlignmentEvent)` | 异常隔离；不回调改变配置或计算，不阻塞 executor |

`AlignmentPorts(Frames,Models,Rois,Coordinates,Backend,GeometryEvidence?,Diagnostics?)`；Frames/Models/Rois可仅在 BeginFit宿主中显式注入 RejectingPort，不能 null等待隐式服务解析。`BackendContext(OperationId,Generation,DeadlineTimestamp,TimeProvider,StopToken,ExecutionLimits)` 中 StopToken 是尽力停止信号；deadline 为同一 TimeProvider 单调 timestamp，不跨进程持久化。`BackendSearchInput(Request,Slot,Stage,FrameLease,ModelLease,ReferencePointDomainLease,PixelSupportDomainLease)`；`BackendTrainInput(Request,TemplateSource,FrameLease?,TrainingDomainLease?)`（XLD无frame租约，但其immutable数组仍计bytes）；`BackendModelInput(ModelRef,ExpectedDescriptor,ModelLease,OutputLimits)`。`BackendResult<T>(Payload?,ErrorCode?,EvidenceCompleteness,NativeReturnCode?,ActualParameters,Diagnostics)` 不含 handle；NativeReturned 以方法真实返回判定，不依赖 DTO 自报布尔。`BackendCapabilities(BackendVersion,AdapterRevision,SupportedRoutes,PixelFormats,SupportedOutputs,CancellationByRoute,ResourceEstimation)` 为 immutable typed枚举列表；资源估计为 KnownBound/EstimateOnly/Unknown，cancel为BeforeDispatchOnly/NativeTimeoutAndDrain/CooperativeAndDrain，无强杀枚举。原生 stop 注册只在 adapter 内执行已验证的合法入口，Core 不直接同时调用 train/search/clear。

### 5.1A HALCON 包公开装配（Assembly Contract v0.1，限定内容已接收）

本节只补后续HalconAdapter/Wpf的自有构造与Host装配，不改§3/5.1已接收Core API v0.2.1、算法向量和Engine状态机。以下均为未来公开声明，不是已经存在的产品API。namespace=`Asun.Modules.Alignment2D.Halcon`；HALCON backend只调用既定cv2路线，公开面不含native类型。进程根是明确实例，由应用入口强持，不能用static/global、产品Shell或隐藏窗口替代。

```csharp
public enum AlignmentCallKind { Factory, Business, Query, Cleanup }
public enum AlignmentHostState { Reserved, Active, Closing, DrainUnknown, Returned }
public enum AlignmentRuntimeMode { ProductionInspect, Engineering }
public sealed record AlignmentCleanupProfile(TimeSpan ExecutionTimeout,
    TimeSpan WaitTimeout, int MaxQueryAttempts, TimeSpan QueryInterval, int MaxErrors);
public sealed record AlignmentRootOptions(int MaxHosts, int MaxCallsPerHost,
    int MaxAnchorsPerHost, long MaxHeldBytesPerHost, int MaxIdUtf8Bytes,
    int ReservedCleanupCallsPerHost, AlignmentCleanupProfile Cleanup);
public sealed record AlignmentHostObservation(string HostId, AlignmentHostState State,
    ImmutableArray<string> PendingCallIds, ImmutableArray<string> PendingResourceIds,
    ValidationError? PrimaryError, ImmutableArray<ValidationError> CleanupErrors,
    bool CleanupErrorsTruncated);
public sealed record AlignmentCleanupContext(string HostId, TimeProvider Clock,
    long DeadlineTimestamp);
public sealed record AlignmentCleanupResult(bool Released,
    ImmutableArray<string> PendingResourceIds, ImmutableArray<ValidationError> Errors);
public interface IAlignmentCleanupAction
{
    ValueTask<AlignmentCleanupResult> RunAsync(AlignmentCleanupContext context,
        CancellationToken cleanupStop);
}
public sealed record AlignmentCleanupStep(string StepId,
    ImmutableArray<string> DependsOn, IAlignmentCleanupAction Action);
public sealed class AlignmentProcessRoot
{
    public AlignmentProcessRoot(AlignmentRootOptions options, TimeProvider clock);
    public AlignmentHostSlot ReserveHost(string hostId);
    public AlignmentHostObservation Query(string hostId);
    public ValueTask<AlignmentHostObservation> ObserveCleanupAsync(string hostId,
        AlignmentCleanupProfile budget, CancellationToken waitCancellation);
    public bool TryReturn(string hostId);
}
public sealed class AlignmentHostSlot
{
    public string HostId { get; }
    public void KeepAnchor(string anchorId, object trustedAnchor, long retainedBytes);
    public void SetCleanupPlan(ImmutableArray<AlignmentCleanupStep> steps);
    public void NotePrimary(ValidationError error);
    public Task<T> StartCall<T>(string callId, AlignmentCallKind kind,
        Func<ValueTask<T>> start);
    public ValueTask<AlignmentHostObservation> CloseAsync(
        AlignmentCleanupProfile budget, CancellationToken waitCancellation);
}
public sealed record HalconAlignmentOptions(Revision AdapterRevision,
    ProfileRef BindingRevision, ImmutableArray<ModelRoute> EnabledRoutes,
    long MaxCopiedFrameBytes, long MaxModelBytes, long MaxTemporaryBytes,
    string TemporaryDirectory, int MaxNativeOperations);
public sealed record AlignmentRuntimeOptions(string SessionId,
    AlignmentRuntimeMode Mode, EngineOptions Engine, HalconAlignmentOptions Halcon);
public sealed record AlignmentRuntimeServices(IImageFramePort Frames,
    IModelAssetPort Models, IRoiPort Rois, ICoordinatePort Coordinates,
    IGeometryEvidencePort? GeometryEvidence, IExecutionDiagnostics? Diagnostics);
public sealed record AlignmentRuntimeCreateResult(AlignmentRuntimeSession? Session,
    ImmutableArray<ValidationError> Errors);
public sealed class AlignmentRuntimeFactory
{
    public AlignmentRuntimeFactory();
    public AlignmentRuntimeCreateResult Create(AlignmentRuntimeOptions options,
        AlignmentRuntimeServices services, AlignmentHostSlot owner, TimeProvider clock);
}
public sealed class AlignmentRuntimeSession
{
    public string SessionId { get; }
    public Guid Generation { get; }
    public IAlignmentEngine Engine { get; }
    public BackendCapabilities Capabilities { get; }
    public ValueTask<AlignmentHostObservation> CloseAsync(
        AlignmentCleanupProfile budget, CancellationToken waitCancellation);
    public ValueTask<AlignmentHostObservation> ObserveCleanupAsync(
        AlignmentCleanupProfile budget, CancellationToken waitCancellation);
}
```

Root/Factory constructor只做有限配置校验，无IO/native/Dispatcher/worker；非法Root options抛ArgumentException，Reserve重复HostId抛InvalidOperationException，容量满抛ResourceExceededException，未知Query抛KeyNotFoundException、TryReturn=false，不造Returned。所有计数/bytes正数且checked计费；MaxHosts≤1024，MaxCallsPerHost/MaxAnchorsPerHost≤1,000,000，MaxIdUtf8Bytes≤1,048,576，MaxHeldBytesPerHost≤long.MaxValue/2；Cleanup.MaxQueryAttempts≤64/MaxErrors≤4096，TimeSpan≤30min。这些是硬防溢出上限，不是性能目标。UTF-8 IDs非空无控制字符且≤MaxIdUtf8Bytes，ReservedCleanupCallsPerHost≥1且<MaxCallsPerHost；Cleanup各TimeSpan有限正、WaitTimeout≤ExecutionTimeout、QueryInterval≤ExecutionTimeout、次数/错误数正且≤根上界。MaxHeldBytes包含输入、防御复制峰值、待归还lease/产物/显示借用，不当RSS/原Owner物理池退款。根构造本身无子资源；**任何其它Factory/Service/Bridge/Runtime/Control之前**先ReserveHost→KeepAnchor受限私有HostLifetime及参数/源/port→SetCleanupPlan，未计划不启动StartCall。锚点object仅用于可信装配强持，不进入业务DTO/digest、反射或脚本执行。

Factory.Create在owner已预约且Clock与根相同的条件下校验Engine/路线/版本/限额，构造本包内部HalconAlignmentBackend并传给原AlignmentEngine.Create；同步入口无IO/native读取/订阅/Task。生产Mode仅开放Align/Fit/Inspect；Engineering另开放Train/Export/Recommend。通过Engine属性取得的是保留原IAlignmentEngine签名的模式门代理，受禁操作在接纳前返回Rejected/ALN-004（模式不提供该操作），不能绕回内部原Engine。ProductionInspect的Inspect仅read/hash/native读回/compare/clear，绝不train/推荐/导出/保存/设置训练结构；训练建议采用必须新Engineering session/候选revision，经host资产Owner批准后新生产请求引用，不热换session内模型。EnabledRoutes为既定ModelRoute非空子集，无新增算法；未知/未实现route只拒该请求。H2不提供GeometryEvidence时仍可运行已准入H1或纯诊断，不启用Qualified H2。

Halcon options必填来源和上界：AdapterRevision/BindingRevision绑定26.05与本包版本；MaxCopiedFrameBytes/MaxModelBytes/MaxTemporaryBytes先与Engine bytes及native估计上限核关系，MaxNativeOperations≤Engine.MaxActive且>0；临时目录为宿主显式独占工作目录，Create只词法校验，不创建/清空目录或核安装/许可。operation第一次确需file才在根登记单文件创建/IO/清理，bytes/路径留在HostLifetime，实际权限/空间故障为BackendFailure，失败只处理本operation文件，清理异常不覆盖原业务错。没有跨session模型缓存；模型handle每operation专有，run-only参数在自己的handle内改，cancel/drain/clear按§4/6，禁止并发clear正在执行模型。

Session.Generation等于Engine接纳代；SessionId非空唯一且绑定本host，不另建业务状态机。Root.StartCall在锁中先预约call/最大迟到资源/cleanup额度→登记可信start闭包和dispatch Task→锁外有限worker调用start→ValueTask只AsTask一次并保存**原Task**；returned Task是受管dispatch结果，不用WaitAsync包装代替原Task。同步抛错或卡住仍留原call/lifetime；不能启动后补登记、用无限线程/Task列表或Thread.Abort。callId采用本HostId/正long序号编码（无前导0/文化格式），同Host严格增加；重复/低于高水位callId一律拒绝，不通过反射比较Func闭包、不二次执行。高水位保留直到Host真正Returned，活动槽可复用但ID不复用，不建无界历史HashSet。正常结束仅在返回资源已写入受管HostLifetime或由该Owner真实归还后才能复用槽。所有factory结果（包括晚到Service/session/lease）、Begin返回Handle/Completion、桥原Resolve/Read/Open/Release Task和DispatcherOperation.Task均在同根或其被强持上游根中可查询，Host不得丢弃其尾项。桥的原Acquire签名未带Alignment OperationId，故桥自行在本host已预约槽生成单调call族ID并记录ModelRef/FrameRef，不声称能从token猜operation；Core的外层Acquire原Task关联原OperationId与这一族。Session.CloseAsync委托owner.CloseAsync，Observe委托根同Host的Observe；cleanup action只调用内部Engine.ShutdownAsync/Dispose及自身release，不再次调用Session.Close/owner.Close等待自己。根锁中不调用外部action/port，也不把关闭task作为其自身前置依赖。

CleanupPlan是该Host确定资源DAG，不是动态产品工作流：child读/显示/原调用→Engine drain→backend临时句柄/文件→桥自身借用→本Host拥有的上游session/service→Dispatcher退出；借用共享service/source/ports不Dispose。StepId唯一、DependsOn存在无环、总step及最坏cleanup调用数≤reserved额度，Action只释放自身资源。计划注册在Factory前，Action闭包可访问“未创建/创建中/已交付”的私有HostLifetime；迟到factory结果先原子写该Lifetime，再驱动原plan，不能交给无Owner fire-and-forget。所有调用者回调/日志抛错隔离，不能造成丢lease。

Close首次封新Factory/Business，记录唯一cleanup原Task；重复Close仅观察原task，Query/既有cleanup可继续且额度预留。运行取消锁存原operation原因，独立CleanupStop不借业务/waitCancellation，使用同Clock的唯一ExecutionTimeout；每阶段剩余deadline传递，不每步重置。Cleanup尝试到期停止启动新依赖动作，但已发Release/Dispose/Shutdown Task仍强持；观察预算/等待取消仅结束观察，状态DrainUnknown且原Owner不变。ObserveCleanup以已冻结的同Host Cleanup Profile有界查原IDs/原Tasks，不再次训练、读回、发布或重复已发Dispose；若前轮到期后真实child迟到归还，允许在新的独立有限收尾轮只启动原plan中从未发出且DependsOn已确认Released的清理步骤，不换资源身份、不重发已发effect。收尾轮次数与查询合计受原根MaxQueryAttempts/cleanup保留槽上限约束，每轮至多其ExecutionTimeout，不能通过传新Profile增限或无限轮询；额度用尽保持DrainUnknown交显式Owner处理。已确认副作用不改失败。ActionReleased=true须有本资源Owner真实退出/归还或明确已确认耐久接管的事实，不能空PendingIds/窗口关闭/GC推断。TryReturn还要求原Task全部观察、晚到结果已接管、全部依赖资源无借用且cleanup结束；单个Dispose抛错保留其原Task/Owner，独立child继续但该父依赖不释放。PrimaryError首个业务错锁存，CleanupErrors有界顺序追加，超限标截断仍DrainUnknown；不能被finally/取消/清理错误覆盖。

### 5.1B 原服务的限定消费桥（限定内容已接收）

只读消费权威：[ModelAssets Service §5A/附录B](../model-assets/DEVELOPMENT-GUIDE.md#5a-完整模块无-ui-service-设计合同-v03)、[ImageFrame Resources §4.3](../image-frame/DEVELOPMENT-GUIDE.md)、[viewport Session/WPF](../viewport/DEVELOPMENT-GUIDE.md)。下面是Alignment自有adapter参数，不给上游加同名API；上游版本/Owner不同或事实无法无损映射仅拒对应桥，直接实现已冻结Core端口的其它Host仍可工作。

**模型只读桥。** Halcon包新增的唯一公开装配如下；类型alias只引用上游实际namespace，不新定义AssetRef/Service DTO，Create无IO、不创建或关闭Service：

```csharp
using MA = Asun.Modules.ModelAssets;
using MAS = Asun.Modules.ModelAssets.Service;
public sealed record AlignmentExactModelEntry(ModelRef Model, ModelDescriptor Descriptor,
    MA.AssetRef ExactAsset, MA.AssetRef FileOwner, string Role, string LogicalPath,
    ProfileRef ProducerSnapshotRef, long DeclaredFileBytes, string RawFileSha256);
public sealed record AlignmentModelAssetsBinding(MAS.IModelAssetService Service,
    MAS.OperationContext ContextTemplate, MAS.AssetAccessRequest Access,
    ImmutableArray<AlignmentExactModelEntry> Entries, long MaxModelBytes,
    AlignmentCleanupProfile Cleanup);
public sealed record AlignmentModelBridgeResult(IModelAssetPort? Port,
    ImmutableArray<ValidationError> Errors);
public static class AlignmentModelAssetsBridge
{
    public static AlignmentModelBridgeResult Create(AlignmentModelAssetsBinding binding,
        AlignmentHostSlot owner);
}
```

Scope/principal/profile/mode与Service.SessionInfo精确相等，ContextTemplate只是合法预算/身份模板，不复用其OperationId/RequestDigest；原Core Acquire未带BackendContext，桥call族只用该模板Budget.TotalTimeout冻结自己的总单调截止点，后续Context.TotalTimeout取剩余且各步原digest保持，stopToken已取消不启动下一步。等待/恢复用独立Query预算且不重写原Context。MaxModelBytes>0且覆盖声明+hash/EOF缓冲峰值；Role/path必须确在精确闭包，single native入口文件首片可用，需多个外部文件/layout而无法映成本Core单Content时明确UnsupportedMethod，不拍平/拼接包。

IModelAssetPort.AcquireAsync按本host预约call族/model在根预登记原request族ID→用上游ModelAssetRequestProjection.ProjectResolve生成原完整digest→ResolveExactAsync(ExactAsset,Runtime,ReadForUse)→完整闭包且RootRef/文件owner/role/path/原摘要一致→ProjectAcquire+AcquireContentLeaseAsync→父lease先写Lifetime→ProjectOpen+parent.OpenFileAsync→child ReadId/实际长度/FileDigest核entry→只读流有界复制到owned byte[]，读取至EOF并核raw SHA-256等于ModelRef.ContentHash和RawFileSha256→交付本Core IModelContentLease(Descriptor,Content)。Descriptor来自生产者已冻结并hash绑定的ProducerSnapshotRef，Service Resolve没有公开Alignment ModelDescriptor getter，不能从文件名/alias/只读回部分native参数补造它；binding无完整描述或旧投影规则不可验证只拒本entry。资产Ref的包digest与raw模型文件hash分开，不把二者相互赋值。读取用受管原Task/流借用；原service观察Pending/Unknown、撤权或wait到期不交成功lease，原IDs/digests/epoch保留并QueryOperationAsync，迟到lease由原桥Owner接管且归还，不二次Resolve/Acquire取代未知调用。

RawFileSha256为64个小写hex且FileDigest.RuleId/Algorithm必须与生产者明确的raw/SHA-256规则相符，未知legacy摘要只能走原Owner验证，不改写其Digest；Descriptor所有公开字段与entry.Model/producer快照逐值匹配（immutable arrays按内容），ProducerSnapshotRef只绑定已取得的生产者证据，不称hash字符串本身认证外部授权。桥先核长度checked≤Array.MaxLength/预算，再预约独占byte[]+scratch+EOF额外1 byte，最后EOF探查也计读取预算；短读、超长、无EOF、hash/版本错拒绝并归还原child/parent。ModelAssets父lease尚提供撤权检查/permit保持时沿其原策略，不另造Alignment Authority；所有异步Acquire/stream-read Task及source原引用强持，桥没有脱离root的timer/subscription/global cache。

本Core lease释放顺序=backend真正停止读Content→清桥独占byte[]引用→child.ReleaseAsync(ResourceReleaseRequest(ReadId,固定releaseId,budget))→仅Released确认后parent.ReleaseAsync(LeaseId,固定releaseId,budget)，必要QueryResourceAsync(ResourceQuery)，原Task和service/stream继续强持。资源QueryStatus.NotFound/Unknown不是Released，不因复制完就释放还在读的child。DisposeAsync仅观察同release链，不能再次发Dispose。只读桥从不ImportAndSeal/VerifyFormat/Store/Publish；生产Inspect由本backend原只读操作完成。工程候选封存的完整生产者映射、原身份恢复及宿主接线唯一见§5.1C；该接线仍不赋予Core持久化或发布权。

**图像帧桥。** Halcon包唯一公开装配，Service借用不关闭：

```csharp
using IFR = Asun.Modules.ImageFrame.Resources;
public enum AlignmentFrameContentRule { RawPlanesRowOrderSha256V1 }
public sealed record AlignmentExactFrameEntry(FrameRef Reference,
    IFR.FrameDescriptor Descriptor, AlignmentFrameContentRule ContentRule,
    ProfileRef SourceEvidence);
public sealed record AlignmentImageFrameBinding(IFR.IFrameService Service,
    string ConsumerId, ImmutableArray<AlignmentExactFrameEntry> Frames,
    long MaxCopiedFrameBytes, TimeSpan ReadTimeout, AlignmentCleanupProfile Cleanup);
public sealed record AlignmentFrameBridgeResult(IImageFramePort? Port,
    ImmutableArray<ValidationError> Errors);
public static class AlignmentImageFrameBridge
{
    public static AlignmentFrameBridgeResult Create(AlignmentImageFrameBinding binding,
        AlignmentHostSlot owner);
}
```

consumer必须已在上游ResourceLimits登记，不冒其它consumer额度；ReadTimeout有限正并不大于宿主对该调用批准的预算。原IImageFramePort.AcquireAsync未带BackendContext，桥不声称能读取Core operation deadline；桥每call族一次启动独立单调上限，外层Core原stopToken先取消时禁止后续新read/copy，已发任务仍按原Owner排空，不按行/重试重置。FrameKey(Guid,ulong)与本Core string Id/Revision由entry显式逐值对应，不parse文件路径/文化格式/强制转有符号数；Descriptor.SourceId/SourceRevision/CoordinateReference与Reference来源/坐标绑定由SourceEvidence证明，不把Key.Revision等同FrameDefinition.Revision。

首片仅CPU驻留完整帧、批准强度plane、Byte/UInt16/Int16/Float32及现Core支持通道布局，SourceExact原样读，无Display LOD、LUT、gamma或强度转换。所有plane行宽/stride/endian/packing/角色先对照§3，预算不足完整复制在Read前ResourceExhausted；Tiles/非驻留大图/Float64高度或未知plane语义仅拒对应桥，禁止自动解码全图或当灰度图。发上游FrameReadRequest的新固定RequestId、原ConsumerId/Key、明确PlaneIndices、Window=(0,0,W,H)、Halo=0、ClipAndMarkInvalid、ExactSamples、Timeout=本桥call族ReadTimeout单调剩余预算；原ReadAsync Task注册后才观察。只在receipt Error=None、Phase=Completed、OperationResourcesReleased=true及实际Slice非null交付分支解释；保存ServiceEpoch/RequestId/lease.Id/SourceKey/CoreWindow/ActualWindow/SourcePlaneIndices，核full-frame身份/实际layout后TryOpenReadScope→每plane/localY CopyRow到checked受限独占数组（不读padding）→scope.Dispose→SHA-256按plane请求顺序/row顺序的有效row bytes串联核Reference.ContentHash。该RawPlanesRowOrderSha256V1仅在生产者entry已使用同规则时允许；旧/包hash规则未知拒桥，不重新标记旧身份。域与metadata必须分别核：DomainRow EndXExclusive转Core LastColumn=EndXExclusive−1，行/域排序完整、源有效域与IRoiPort引用匹配，不能以rect Bounds替mask。

本Core PixelPlane的ReadOnlyMemory持有桥owned数组，直到backend真实退出/归还Core lease才清引用；原Frame lease始终归原Service，scope退出后按原Id.ReleaseAsync(独立有限观察预算)单次发原release Task。LeaseClosed且无live scope/本借用退出才是逻辑归还，StorageReleased=false可能表示原帧/其它consumer仍在使用同allocation，不等于本借用失败或强制Retire；pending scope/DrainUnknown则不能宣称归还。Read观察停止/取消竞态未交付slice由原Service owning path接管，已交付迟到slice由桥Owner接管，CAS只一个Owner；QueryOperation(ServiceEpoch,RequestId)只取原观察，不能通过重复Read领第二lease。桥Dispose故障或不能证明归还，根保持DrainUnknown，原Service/数组强持；禁止清borrowed全局帧库。

### 5.1C 工程候选封存与 model-assets 0.3.1-prep 消费

本节闭合模块自有生产者软件设计，Owner为alignment-2d原会话；只新增HalconAdapter中的生产者codec、封存编排及格式/challenge adapter规格。Core v0.2.1、Assembly v0.1已接收部分、唯一ArtifactOffer签名不变。资产Service/存储/权限/物化/包导出继续使用[model-assets §5A、附录B/C](../model-assets/DEVELOPMENT-GUIDE.md)，不复制Store、SQL、Stage身份或HALCON句柄生命周期。

#### 5.1C.1 完整生产者快照与文件映射

生产者快照不是从文件名或Service.Resolve补出的描述。训练/导出终态在释放账本前由宿主保留原请求、artifact、ReadbackReport及ActualParameters；Train和Export为显式二选一来源。Export保留被导出模型的原生产者快照和父模型精确Ref，不把Export时间当新训练时间。Descriptor.TrainingSource按§3.6的TemplateSource保存，PreprocessRevision/AdapterRevision/CapabilityRevision为Revision，ResolvedTrainingParameters为ImmutableArray<ActualParameter>；SupportRef是hash绑定的ProfileRef，TrainingDomain是DomainRef?；这里补明确既有字段类型，不增删Core字段。XLD保存原ContourTemplate，不补ImageTemplate。描述、Requested/Resolved、实际Ft/Mt/crop/原点及预处理链全部逐值保留，缺影响复现的量拒此新封存路径，不改旧模型。

```csharp
// namespace Asun.Modules.Alignment2D.Halcon
// using MA = Asun.Modules.ModelAssets; using MAS = Asun.Modules.ModelAssets.Service;
public enum AlignmentArtifactSourceKind { Train, Export }
public sealed record AlignmentArtifactProvenance(AlignmentArtifactSourceKind Kind,
    OperationId SourceOperationId, Guid EngineGeneration, TrainRequest? Training,
    ExportModelRequest? Export, ModelDescriptor? ParentDescriptor,
    AlignmentModelBuildSnapshot? ParentBuild,
    ReadbackReport Readback, ImmutableArray<ActualParameter> ActualParameters,
    ImmutableArray<MA.DependencyRef> Dependencies, ProfileRef SourceBindingEvidence);
public sealed record AlignmentProducerSnapshot(ModelDescriptor Descriptor,
    AlignmentModelBuildSnapshot Build, ModelDescriptor? ParentDescriptor,
    ImmutableArray<MA.DependencyRef> Dependencies);
public sealed record AlignmentProducerProjection(ImmutableArray<byte> SnapshotBytes,
    MA.AssetManifest? Manifest, MA.SemanticSnapshot? SourceSnapshot,
    ImmutableArray<ValidationError> Errors);
public sealed record AlignmentProducerDecodeResult(AlignmentProducerSnapshot? Snapshot,
    ImmutableArray<ValidationError> Errors);
public static class AlignmentProducerCodec
{
    public static AlignmentProducerProjection Encode(ModelArtifact artifact,
        AlignmentArtifactProvenance provenance, MA.AssetIdentity identity,
        MA.CoreValidationProfile limits);
    public static AlignmentProducerDecodeResult Decode(ImmutableArray<byte> snapshotBytes, MA.AssetIdentity identity,
        MA.CoreValidationProfile limits);
}
```

投影失败SnapshotBytes.Empty、Manifest/SourceSnapshot=null；Decode失败Snapshot=null。两入口有界、无IO/native/全局状态；不能接受任意JSON/反射自动序列化或写入数据库。Train来源必须Training非null、Export/ParentDescriptor/ParentBuild=null；Export来源必须Export/ParentDescriptor/ParentBuild非null、Training=null，ParentDescriptor和原Export.Model/ExpectedDescriptor逐值一致；Provenance.SourceOperationId与该请求Header.OperationId、Offer.SourceOperationId及原终态同值，EngineGeneration同原代，原Readback.Passed=true且无影响复现的NotQueryable缺证据。Train.Build由原Training取技术字段；Export.Build由ParentBuild取得原创建技术字段，与ParentDescriptor/原生产者快照逐值一致，不伪装为新训练；仅新候选ModelRef变更。

`AlignmentModelBuildSnapshot`是本adapter的封闭值联合，按tag及以下唯一字段顺序编码：GenericBuild(Template:TemplateSource,RequestedOrigin:PixelPoint,Parameters:GenericTrainingParameters)、ScaledBuild(Template,RequestedOrigin,Parameters:ScaledTrainingParameters)、AnisoBuild(Template,RequestedOrigin,Parameters:AnisoTrainingParameters)、NccBuild(Template,RequestedOrigin,Parameters:NccTrainingParameters)、DeformableBuild(Route:PlanarUncalibrated/LocalDeformable,Template,RequestedOrigin,Parameters:DeformableTrainingParameters)。各分支生成同名Alignment前缀sealed子record，基类仅本程序集可派生；公共字段类型和范围沿§3.6，不包含候选ID/Revision、Header、ExecutionLimits、Deadline、OutputLimits。Requested Template保存原训练源；Descriptor.TrainingSource保存实际预处理源与派生链，二者不互相覆盖。ParentBuild保存原父生产者已Decode的上述完整联合，缺旧创建语义则不准新Export封存，仅保留候选原字节及旧只读能力。

生产者codec固定`aln-producer-binary-v1`：头为ASCII `ALNP`四byte及UInt16LE版本1；顶层依次Descriptor、Build、ParentDescriptor?、Dependencies。原请求OperationId/EngineGeneration/预算/ReadbackReport/资格/回执仅属于宿主原审计链（SourceSnapshot绑定原来源），不进入producer.bin或Manifest.Semantics；不同Offer但相同技术内容不因此换技术digest。复合字段严格按本页各record声明/DTO表的字段顺序编码；本codec只写下列技术snapshot字段，不编码Provenance中的request Header/ExecutionLimits/Deadline/OutputLimits或ReadbackReport；未知/重复参数、未知类型/尾部余byte拒Decode。string为UInt32LE严格UTF8长度+原bytes，无BOM/控制字符/孤立surrogate；Revision/OperationId/角度/scale等单字段wrapper仅编码内值；Guid为小写D格式string；enum为精确成员名string，不用ordinal；int/long分别Int32LE/Int64LE，bool单byte 0/1，double为IEEE754原64bit little-endian，有限且负零先规范为正零；TimeSpan为Int64LE Ticks；nullable先0/1，再值，数组先UInt32LE项数，再各项。判别联合先string类型名，再该分支字段；AutoOrFixed为Auto无payload/Fixed后payload，ParameterValue分支名为FiniteNumber/Integer/Boolean/EnumValue/Auto；Integer为Int64LE，EnumValue为已冻结枚举名string。按route选§3.6训练参数类型，不动态枚举成员；Frame/Domain/Profile/Transform/Template/ActualParameter递归按§3的固定结构，CentreMatrix恰好9个double、Contours按原顺序、各集合保序。Descriptor根ModelRef仅编码ContentHash:string、Method枚举string、Route枚举string，Id/Revision不编码，由Decode显式identity（来自原RootRef/Manifest）重建并与ModelRef绑定；ParentDescriptor的ModelRef则完整编码原ID/revision/hash/method/route。Descriptor随后依次ApiMajor、ContractRevision、BackendVersion、AdapterRevision、TrainingSource、PreprocessRevision、TrainingDomain、TrainingPose、Origin、SupportRef、ResolvedTrainingParameters、CapabilityRevision；Build为下方封闭路线联合；ParentDescriptor先nullable tag再完整描述；Dependencies沿MA完整Purpose/Role/Target Identity及Digest（rule/algorithm/UInt32LE byte数+原bytes）编码。SourceBindingEvidence必须来自宿主实际保存/读取核验，不由bool自报来源完整。解析先限长度/计数/深度/总量及checked乘加，再分配；使用CoreProfile同名预算，逻辑计费按MA §4.1，原binary bytes额外计一次；所有数组≤Array.MaxLength，IsDefault拒绝。Decode重建snapshot后用同codec内部EncodeSnapshot重编码须逐byte相同（不调用需要artifact/provenance的公开Encode，不重建原操作来源）；不解析旧未知codec、不用新codec重写旧metadata。

| MA字段/文件 | 本模块唯一映射 |
|---|---|
| Identity / Producer | NamespaceId来自Service.Scope.AssetNamespace，AssetId/RevisionId精确等artifact.Descriptor.ModelRef.Id/Revision；不自动生成latest。Producer=(alignment-2d,aln-producer-binary-v1)，不是UI语言或文档版本 |
| Files / Layout | 必需`(Model,model.bin)`=artifact.Content，必需`(ProducerSnapshot,producer.bin)`=上述bytes；两项LengthBytes实值>0，FileDigest均raw-file-sha256-v1/sha256/原32byte。Layout两项SourceAsset=null、SourcePath=TargetPath，Entrypoint=model.bin；后缀不决定reader。ModelRef.ContentHash仅等model.bin raw hash，ProducerSnapshotRef.ContentHash仅等producer.bin raw hash；包Ref digest由MA.ModelAssetCore.ProjectCanonicalCore计算，三者不混用 |
| Format | Family=alignment-2d，Id=`aln-halcon-`+固定route token（generic-shape/scaled-shape/aniso-shape/ncc/planar-uncalibrated/local-deformable），Revision=1。每route注册exact adapter，不把Generic/Aniso伪装成最小Shape observable schema |
| Semantics | schema `aln.producer.snapshot-v1`、revision=1；唯一字段`producer.snapshot`，Kind=String，Unit=null，Value=producer.bin完整bytes的标准base64（含padding），Status=Explicit，SourceId=alignment-2d，SourceRevision=aln-producer-binary-v1，Stage=Build。完整binary语义进入技术hash，不能只存一个未取得的hash来冒描述；snapshot含原Requested/Resolved/坐标/实际训练来源/参数/依赖；操作报告/资格不进入该字段。重复文件和base64造成的峰值与UTF8长度均计预算，超限拒绝，不降为丢字段快照 |
| SourceSnapshot | schema `aln.offer.source-v1`、revision=1；三String字段engineGeneration/sourceOperationId/sourceBindingEvidence，值分别Guid小写D、OperationId.Value、SourceBindingEvidence按上述ProfileRef三string binary编码后的标准base64；均Explicit、Stage=Build、Unit=null，同上述SourceId/Revision。此注册来源随ProjectImport绑定原RequestDigest；Store未接收此字段，不声称Store替宿主持久保留它；重启恢复所需完整原request由宿主原审计/交接Owner保存 |
| schema digest / Constraints | 两schema的原bytes分别为ASCII `aln.producer.snapshot-v1;1;producer.snapshot:String:null:Build:Explicit:base64(aln-producer-binary-v1)`、`aln.offer.source-v1;1;engineGeneration:String:null:Build:Explicit;sourceBindingEvidence:String:null:Build:Explicit;sourceOperationId:String:null:Build:Explicit`（无LF）；raw-file-sha256-v1/sha256。Constraints十键完全沿MA §4.2：lower/upper/defaultValue/defaultSourceId/defaultSourceRevision/elementKind/reason=null，lowerInclusive/upperInclusive=false，defaultPolicy=NoDefault。Fields按MA scalar序排序 |
| Dependencies | 原Provenance全部显式Runtime/RebuildSource/ValidationEvidence边，不仅当前Runtime。Train的图像/轮廓源、训练域/预处理证据与原来源绑定由宿主对应技术资产精确Ref提供；Export加RebuildSource角色parent-model精确边；challenge/真值有ValidationEvidence边；实际不存在的可选来源不补假边，但已知所需来源未封存/无Ref时此新封存Rejected并指出字段，不能把它改Empty通过。不是任意新Ref都足够：SourceBindingEvidence绑定模板/域/hash/父描述到这些精确Ref，原Owner核映射；原已seal旧资产保持原声明，不追改 |

没有运行样本/challenge时ValidationEvidence可以确实Empty并报告NotRequested，不得称挑战通过；训练来源不可取得只保留原artifact为待保存候选。本节不创建图像/ROI/配方事实资产，也不把外部门扩大成不能读/搜模型。

上述schema原bytes长度/hash固定：producer=102 byte / `c0925ef4e3da132dbaf754c03bd0b926134eb85c90d8e6330bb0f3db045cb00f`；source=159 byte / `64bfab5e62d15880d5ba6a4b78865d8ab99df5ff96a020b3b94cfa5515b088ad`。§5.1C.2 runtime=39 byte / `c0c3f3b6a9c69e17208084978ca5f83c790121d53d07d0f1d6ab17009d91b2b8`。binary原语固定向量（**不是完整模型快照**）：ALNP+UInt16LE(1)+string("Ncc")+double(规范正零)+bool(true)+nullable(null)共23 byte，hex=`414c4e500100030000004e636300000000000000000100`，raw SHA256=`a6cab6c3350b8e67226fda3aa7e7e260b8c0eb155d44fb89c5c3bdce791cc972`；末尾加byte、缺nullable tag、bool=2均拒绝。此向量服务ALN.ASSET.01的原语/版本边界，完整snapshot及真实模型读回仍须后续C#测试，不以原语复算冒整个codec通过。

#### 5.1C.2 有界封存、原Offer恢复和读回

公开装配为`AlignmentArtifactPublisher.Create(AlignmentArtifactPublisherBinding binding,AlignmentHostSlot owner)`，返回`AlignmentArtifactPublisherCreateResult(Publisher:AlignmentArtifactPublisher?,Errors:ImmutableArray<ValidationError>)`；binding为`Service:MAS.IModelAssetService,ContextTemplate:MAS.OperationContext,Access:MAS.AssetAccessRequest,Adapter:MAS.AdapterKey,ChallengeRef:MA.AssetRef?,MaxPendingOffers:int,MaxHeldArtifactBytes:long,Cleanup:AlignmentCleanupProfile`，全部显式，无IO。Service借用不Dispose，Scope/profile/principal核原SessionInfo；Access使用宿主登记的工程候选ReadForUse用途，不能将该用途解释为生产许可。publisher不含WPF类型：`ValueTask<AlignmentArtifactSealObservation> SubmitAsync(AlignmentArtifactSubmission submission,CancellationToken waitCancellation)`；submission=`OfferId:Guid,SourceOperationId:OperationId,EngineGeneration:Guid,Artifact:ModelArtifact,Provenance:AlignmentArtifactProvenance`，observation=`OfferId,State:AlignmentArtifactSealState（Pending/Sealed/Rejected/Unknown）,ExactRef:MA.AssetRef?,SealReceipt:MAS.SealReceipt?,Errors:ImmutableArray<ValidationError>,PendingCallIds:ImmutableArray<string>`。`ValueTask<AlignmentArtifactSealObservation> QueryAsync(Guid offerId,CancellationToken waitCancellation)`只观察同记录/原MA查询；无记录为Rejected/NotRetained，不重新封存。max offers计所有未交回/Unknown，bytes含artifact、snapshot、base64、流复制峰值和原请求；容量在登记前核，未知不淘汰腾位。

流程固定：核原代Train/Export真正终态及artifact hash→OfferId原子登记不可变submission/原源证据→Encode→MA.ModelAssetCore.ValidateManifest/ValidateContentReferences/ProjectCanonicalCore→构造AssetImportRequest(ExpectedAbsent=true,SourceSnapshot)与两个ContentInput→ProjectImport成功后替换合法占位Context.RequestDigest→root.StartCall发一次ImportAndSealAsync（Service在Stage前取得并核全部三Purpose显式依赖/保护，生产者不造完整closure）→核Succeeded/ConfirmedCommitted/精确Ref及全部实际文件→ProjectResolve/ResolveExact(Runtime,ReadForUse)→ProjectAcquire/AcquireContentLease→ProjectReadback/VerifyFormatAsync(本route adapter,RuntimeSnapshot,ChallengeRef)→归还readback全部子资源/父lease→Sealed。每步Context.OperationId固定`aln-offer-<小写N格式OfferId>-<seal|resolve|acquire|verify>`；相同OfferId不同源/hash/provenance拒冲突，身份已登记后不得换profile/epoch/adapter/预算字段。整条链同一单调deadline，各新业务步骤只用剩余预算，原已发Context/RequestDigest保持；预算到期不再发新步，收尾另用原Cleanup。

ContentInput.Source为publisher内部sealed的MAS.IAssetContentSource：SourceId=`aln-offer-<N>-model`或`-producer`，仅接受原role/path/context和实际byte长度；OpenRead先登记原资源Id并提供独占只读MemoryStream，清理确认流已停读才Released。多reader有界计费、每reader独立位置，不借一个Stream给两调用；byte[]/artifact不可提前清除；Release/Dispose只一次原Task，Query只观察。非法/hash不一致/短读/无EOF拒成功，与§5.1A排空规则相同。

Pending/Unknown/观察取消保持原Service原Task、全部原Context/RequestDigest、SourceSnapshot/bytes、lease/adapter/profile/rule/Store/generation/reconciliation引用；QueryOperationAsync(OperationQuery原ID/digest,独立观察budget)只查原调用。Found/Succeeded但Query不带SealReceipt时不得捏造回执或重发Import，继续原Task/原Store已确认回执恢复；NotFound/retention过期不证明未提交。seal已确认而verify失败，observation为Rejected并保留ExactRef/SealReceipt、说明技术资产已保存但读回未通过；没有Delete/补写/回滚已seal动作。等待超时不得返回明确Rejected冒无副作用。重启恢复由宿主带原完整submission/request/identity及MA C.1 Origin/Store route重建查询记录，不能在新Service epoch直接假定旧内存操作可查询；缺耐久恢复能力继续Unknown交原存储Owner处理，不能重新Submit换OfferId。原Unknown永远沿原Stage算法/adapter/Profile查询；新请求才显式选择model-sd-stage-jcs-v1。

RuntimeSnapshot schema为`aln.runtime.read-only-v1`、revision=1、Fields.Empty；schema bytes为ASCII `aln.runtime.read-only-v1;1;fields:Empty`，raw-file-sha256-v1/sha256。无challenge时binding.ChallengeRef=null；有值必须有对应ValidationEvidence角色alignment-challenge的精确边且登记executor/case，不能用producer未来自身Ref造循环。工程封存不以最低分挑候选或默认challenge Passed。宿主IAlignmentUiHost仍只实现唯一OfferArtifactAsync：Submit前保留不可变原offer与provenance；Sealed且宿主已保存真实回执后Accepted+非nullHostReceiptRef，Pending/Unknown→Pending，明确Rejected→Rejected。HostReceiptRef由实际回执保存Owner生成，不能把StoreReceiptRef字符串直接冒ProfileRef。页关闭/三语切换不取消这条登记链或重发Offer。无UI工程Host使用同publisher，不需初始化控件。

#### 5.1C.3 route格式读回与可选challenge

本模块自有`AlignmentModelAssetFormatAdapter.Create(AlignmentAssetFormatProfile,AlignmentHostSlot,TimeProvider)`返回`AlignmentAssetFormatCreateResult(Adapter:MAS.IModelFormatAdapter?,Errors:ImmutableArray<ValidationError>)`；profile=`Adapter:MAS.AdapterKey,Route:ModelRoute,ExecutionRoot:AlignmentProcessRoot,Runtime:AlignmentRuntimeOptions,Services:AlignmentRuntimeServices,MaxSnapshotBytes:long,ChallengeExecutor:Asun.Modules.ModelAssets.Formats.Halcon.IModelAssetChallengeExecutor?,Cleanup:AlignmentCleanupProfile`。Create无native/IO，exact FormatId/Revision/producer schema登记；Services.Models仅用于其它明确模型引用，root模型始终来自本次Materialization，禁递归Verify同root。ReadBackAsync使用原MAS.FormatReadbackInput预算：核root/layout/VerifiedFiles/metadata→有界读producer.bin和model.bin至EOF/hash→Decode(snapshotBytes,input.Closure.RootRef.Identity,limits)→用producer字段/文件实值和input.Format重建本节MA.AssetManifest.Semantics/Files/Dependencies，ProjectCanonicalCore核digest==Closure.RootRef.Digest（input没有Manifest字段，不读不存在的getter）→核ModelRef/route/hash/Origin/完整参数→以model.bin及解码Descriptor组成私有只读IModelAssetPort→在ExecutionRoot预登记独占call槽/新受管Runtime session/BeginInspectModel→等待真实terminal/ReleaseOperation→关闭该独占session及文件/tuple/native→返回MAS.ReadbackReport。Format与Adapter exact不匹配在native前Unsupported；observed保留可查询字段，NotQueryable仅指向本hash绑定snapshot、不能变Equal。只有content完整、reader真实成功且排空才FormatReadback.Supported；参数Different不改变文件身份，但用途拒绝。QueryResource/Release只操作此adapter原worker/session/pin，借用Materialization归Service，在该adapter退出前不能假归还。

MA C.5的HalconModelFormatAdapters是另一个可选最小observable reader，不是本producer schema的默认reader。若Host显式选择它，必须按C.5/C.7登记im014.halcon.<family>.observables-v1原schema和Sequence `{kind,value}`（Int64字符串/Binary64原值/String保序），对应Shape/Ncc/Deformable的Runtime fields.Empty、im014.halcon.<family>.runtime-v1，不把本producer.schema硬换成它。Generic/Aniso或额外query不在该最小route中时明确Unsupported，仍可选择上述本模块exact adapter按既定Inspect路线；不把C.5最小参数集合冒完整创建/运行语义。旧producer schema保持，无静默迁移。上游C.5默认无find，本模块格式读回同样不执行搜索；需要搜索验证必须明确challenge。

challenge公开factory=`AlignmentAssetChallengeExecutor.Create(AlignmentChallengeBinding,AlignmentHostSlot,TimeProvider)`，返回`AlignmentChallengeCreateResult(Executor:Asun.Modules.ModelAssets.Formats.Halcon.IModelAssetChallengeExecutor?,Errors:ImmutableArray<ValidationError>)`，这里接口沿上游C.7 namespace，不另造MAS同名接口。binding=`ExecutionRoot:AlignmentProcessRoot,Runtime:AlignmentRuntimeOptions,Services:AlignmentRuntimeServices,Cases:ImmutableArray<AlignmentChallengeCase>,MaxCases:int,MaxEvidenceBytes:long,Cleanup:AlignmentCleanupProfile`；case=`ChallengeRef:MA.AssetRef,RootRef:MA.AssetRef,MethodId:string,MethodRevision:string,Request:AlignmentRequest,Oracle:AlignmentChallengeOracle,EvidenceRef:ProfileRef`。全数组预绑定且hash核样本/真值/请求/Profile，不在Execute联网/找最高分/生成真值。Oracle=`ExpectedPurposeEligibility,ExpectedEvidenceCompleteness,ExpectedCandidateCountBySlot:ImmutableArray<AlignmentSlotCount>,ExpectedCorrespondences:ImmutableArray<Correspondence>,ExpectedPose:Transform2D?,ExpectedGrid:RasterGrid?,ExpectedField:RasterSourceMap?,PointTolerance:double,MatrixTolerance:double,FieldTolerance:double`，AlignmentSlotCount=`FeatureId:string,Count:int`；容差有限非负且在对应frame单位，case数量正且≤MaxCases，EvidenceRef绑定完整oracle及每个样本/hash，不能仅hash schema。方法固定`aln-replay-v1`/revision=1，Local必须CandidatesOnly；阳性场案例限定一个slot且恰好一个候选，ExpectedGrid/ExpectedField均非null；完整NoCandidate负例二者均null，多局部场案例本方法拒绝而不任选一场，GlobalPose按原route门，不补逆；有拓扑/毫米要求超本案例资格拒请求。

Execute核精确Root/ChallengeRef/Format/runtime/schema/唯一case→从借用Materialization读取原bytes/snapshot并核完整性→在ExecutionRoot预登记独占call槽/新独占runtime/fresh model（不取前reader handle）→ReserveOperationId后只替换原Request.Header的本次OperationId并以ParentOperationId记录原case请求ID，Engine.Generation在原账本关联而不向Header添加字段、保留原技术请求和case身份→BeginAlign→等待after-drain terminal→按FeatureId比对全部候选计数/完整性/资格、一对一对应ID及两端点、Pose同frame/方向/矩阵、Local Grid/SearchFrame/Direction/Convention/SourcePrecision/Valid逐值及Valid样本容差→ReleaseOperation/独占session关闭→返回上游report。CandidateId/operation/generation不是跨run期望键，对应比较按FeatureId及冻结参考点/观察点，不用新的CandidateId与旧oracle做恒等比较。多解/截断/无候选按冻结期望可Passed作为负例检验，但绝不产生用途批准；不挑一个最高分解忽略其余。expected/observed evidence分别按本节binary原语编码rule string=`aln-challenge-evidence-v1`、MethodId/Revision、RootRef、ChallengeRef、Oracle各字段，observed计数/对应/pose/field取本次原输出，同容差字段复制原请求；hash为raw-file-sha256-v1/sha256。Passed表示逐项比较门通过，容差允许不同digest，不要求两摘要恒等；ExpectedEvidenceDigest绑定已冻结完整oracle。未知样本/field精度/失败/未排空返回Unknown+限制及原Owner/PendingResources，不将零值或空数组当实测。deadline覆盖再读/执行/复制/退出，增加的成本计§13；原Task仍占根槽，禁止自等待/将最后pin交给Service提前释放。ChallengeRef=null由format adapter返回NotRequested，有ref无exact case/executor返回Unknown/MA-CAP。本模块自有adapter通过上述AlignmentAssetFormatProfile.ChallengeExecutor显式装配，完成Inspect排空后才调用；未装配不隐式构建。

#### 5.1C.4 双Host装配、兼容和增量断言

前述公开文本形状均生成sealed immutable record，Errors固定ImmutableArray<ValidationError>；source/challenge/format结果向MA返回时使用其ModelAssetError(Code,FieldPath,Context)，不把Alignment错误对象直接赋给MA。producer.bin按原RootRef.Identity严格Decode后的快照读取产生`ProducerSnapshotRef=ProfileRef(ModelRef.Id+"/producer",ModelRef.Revision,producer.bin的raw SHA256小写hex)`，仅从实际文件及严格Decode取得，不能凭目录名称创建。Descriptor.TrainingSource保存**实际**训练TemplateSource，ImageTemplate.Frame.Derivation完整记录原图→crop/resize的FrameMap链和实际域，TrainingPose.ModelToTraining记录Mt，Requested训练输入仍来自Provenance.Training；源原图、实际预处理图及轮廓SourceRef逐值绑定SourceBindingEvidence，ContourTemplate.SourceRef固定ProfileRef。不得将Ft/crop作为新的随意ParameterId塞ActualParameters，也不在codec重新猜变换。支持说明是SupportRef的完整hash绑定证据，运行前仍通过原ROI/Support端口核，不把ProfileRef本身当mask。

factory静态Create构造的是有Owner实例；publisher的Submit/Query使用上方ValueTask签名，AlignmentArtifactSealState是其本地enum，不进入Core终态枚举。format/challenge两profile.Runtime.Mode必须ProductionInspect，EnabledRoutes包含其exact route且资源Ceiling匹配；factory输入均在Root预约后纯校验，返回失败实例null。MA错误映射固定：结构/codec/来源错MA-REQ-001，预算MA-RES-001，未知schema/route/method MA-CAP，native读回MA-FMT-READBACK，资源未证释放MA-RES-UNK-001；FieldPath保留本模块原定位，Context仅有界资源键/原引用，不显示原native异常文本。publisher Closing时拒新Submit，Query保持原记录；根确认所有尾项/资源/回执交回后才允许Return，不提供清空Unknown的接口。

ExecutionRoot为宿主显式创建并被adapter/challenge原owner强持的独立有界根，TimeProvider与原caller同实例；不关闭整个借用根。每个ReadBack/Execute发起前预预约子HostId=`原owner.HostId+"/execution/"+正long递增ordinal`，只在该子slot KeepAnchor/SetCleanupPlan后创建其独占Runtime；EngineOptions/单操作预算和MA剩余deadline先收紧，禁止给每个子Host另发一整池额度。子plan只关自身runtime/读流/借用模型，不依赖caller当前ReadBack/Execute Task；Session.Close因此不会关闭caller或等待自己。成功子slot实际Released后TryReturn，Unknown保留原子slot和原Task，QueryResource映射原子HostId，不重复Reserve/Create。借用ExecutionRoot里其它Host不能被该adapter归还/关闭；根总host/bytes/call预约满即MA-RES，不能为每次未知新建无限根。caller.Close先封新并查询这些既有子槽，全部Released才完成adapter归还；两个层次的有限清理没有环依赖。

格式Manifest重建只使用input.Closure.RootRef.Identity、input.Format、两实际文件hash/长度、snapshot原Dependencies及本节固定Producer/Semantics/schema，核原RootRef技术digest后才解释Descriptor；不读取输入中不存在的AssetManifest/Semantic getter，不从Native查询补Manifest。Publisher的verify需完整MAS.ReadbackReport绑定原RootRef/GraphRefs/RequestDigest/Adapter/Runtime/ChallengeRef、ContentIntegrity.Verified、FormatReadback.Supported、无ComparisonDifferent/ParameterNotCollected影响复现限制，且请求challenge时Challenge=Passed，否则Rejected或Unknown；未请求只能NotRequested。成功回执还须来自原Task或耐久原receipt，不因纯Query.OperationOutcome=Succeeded而编造SealReceipt。

binary中的FieldComparison固定顺序FieldPath:string、ComparisonState:Equal/Different/NotQueryable enum string、Expected:ParameterValue?、Actual:ParameterValue?、SourceRef:ProfileRef?；ActualParameter顺序Id:ParameterId enum string、Requested:ParameterValue、Resolved:ParameterValue?、Source enum string、Status enum string、ReasonKey:string?。readback MAS.Parameters使用具名field path而不是动态native query：本producer字段`producer.<FieldPath>`保序映射，FiniteNumber→CanonicalNumber，Integer→规范Int64 CanonicalString，Boolean→CanonicalBoolean，EnumValue→CanonicalString；Requested.Auto声明为CanonicalString("Auto")并仅在真实Resolved存在时Status=AutoResolved。可查询固定值Status=Explicit，NotQueryable映射NotCollected/null并保留BoundManifest来源/limitation，不把清单值写Observed；实际不等保留Requested/Observed两值和ComparisonDifferent限制。MA.ParameterReadback自身不含Kind/Unit，原参数类型/单位由producer.bin与schema绑定，不能假造同名字段。仅get形状无法表达的原点/矩阵检查由本Inspect报告独立限制，缺完整读回不签Passed。

格式读取只按Materialization.EntrypointPath和原Format.Layout精确定位同代producer.bin，不枚举目录余项；保持上游物化pin/guard，路径越界/reparse/文件身份/hash不符拒读取，不能用Path.Combine后的字符串当安全证明。本snapshot/runtime schema digest须逐bytes等登记版本。各factory的MaxSnapshotBytes/MaxCases/MaxEvidenceBytes等正且≤原根/Runtime/MA预算，Cases默认数组/重复(RootRef,ChallengeRef)/无case/未知method拒Create；独占factory slot和cleanup plan先登记再读/执行，禁止Execute用已Closing的caller slot作为自己的owner。

Oracle比较顺序为完整性/用途枚举→每slot所有候选计数→对应FeatureId集合及参考/观察点欧氏距离≤PointTolerance→Pose源目标/kind/九矩阵逐系数绝对差≤MatrixTolerance→Local Grid全部字段、Frame/Direction/Convention/SourcePrecision/Valid精确相等、Valid=true的Rows/Columns逐分量绝对差≤FieldTolerance；不比较运行时间/新的OperationId/CandidateId，错误/非有限/缺资源释放证明为Unknown，完整比较不同为Failed。ExpectedCandidateCountBySlot按FeatureId ordinal排序、覆盖全部slots、Count非负；对应按FeatureId ordinal排序且恰好一项/FeatureId，候选身份歧义保持原PurposeEligibility。ExpectedPose=null要求实际Pose=null；ExpectedField=null要求不发布Field，不用空Field冒null；RawRasterOnly的Unreported仅允许绑定明确的raw诊断期望，任何Qualified/计量期望拒Create。evidence编码中的对应只编码FeatureId/ReferencePoint/ObservedPoint（三项），排除易变CandidateId；ExpectedGrid在ExpectedField前编码，完整Field数组/精度/hash保留。字节/digest只是证据绑定，实际容差仍由此逐项比较，不能用摘要相同代替资源/用途门。

Host-A（工程训练/封存）和Host-B（通用检测读取/搜索）分别创建自己的Alignment根/slot/runtime；原MA Service根/slot同样先预约。采用真实SD路径的启动次序固定：MA.StorageDatabase.ModelAssetsStorageRegistration.Create→Package.BindingCatalog/OwnerRegistration/ReferenceResolver登记到SD公开创建输入→原SD Create Task保留→Package.AttachRuntime原实例成功→MA SD桥(TechnicalBinding等原公开ports)→WindowsModelAssetMaterializer.Create原受控NTFS profile→本节route adapter（或C.5显式兼容最小adapter）→ModelAssetsHost.Create(options,ModelAssetsPorts)→Alignment只读桥/工程publisher→Alignment RuntimeFactory。物化工厂类型位置沿MA C.7 StorageDatabase工程，不因C.2简称额外造Adapters namespace。Format adapter与challenge各自有独占Alignment slot，不能以服务caller所在slot关闭自己；cleanup DAG为challenge/format独占runtime→MA readback/pin/leases→MA service→Store借用→SD原拥有者，跨两个根用已受管原Task/真实Released回执连接，禁止环依赖。A/B可借同Store不可变bytes，禁止共享native/runtime/取消域/UI语言。

Host-A提供工程来源资产/完整三Purpose边及当前授权，执行Train→原终态→publisher→原回执。Host-B只接受已精确封存且对应用途已Approved的Ref/producer snapshot，按只读桥Resolve/Acquire/Open→BeginAlign→after-drain→归还；关闭A不Dispose共享Store/Service/B。A失败/Unknown不把未保存候选热换B模型；B旧生产revision继续原许可规则。采用MA C.8时显式提供受信AU Context/Policy/action修订/ScopeId/Purpose目录/用途Provider/watch/有限budget，历史Allowed不是当前Permit，权限许可与用途证据分别保留；默认仅当前核权+订阅能力，不宣称全局即时撤回。没有真实物理阈值仅影响其用途资格，不阻已定义工程算法/模拟Core。

技术包导出仅宿主另外装配MA.Service.Adapters.WindowsDirectoryAssetExportSink.Create，走原ExportClosureAsync+独立当前Export权限，query原journal/identity，默认无持久/native缓存、不自建ZIP/发布服务。需要签名的包入口先MA.ModelAssetPackageSignature.Verify(detached envelope,可信profile)，结果不改bundle/PackageDigest/Ref、不授模型采用；本模块不持私钥。选择新注册包/adapter前保留原binding/adapter/rule/operation/FileObject/journal/profile，旧Unknown按原Scope/Store/Generation和原Stage算法查询，零重发/零改目录；新model-sd-stage-jcs-v1由MA桥自己计算，本publisher不重复实现。完整依赖保护只对新seal启用，不回改已seal旧资产或Core API。工程存储许可/来源耐久证据缺失准确拒该封存，不拿默认Empty SourceSnapshot或空依赖绕过。

未来断言加入既有HalconAdapter.Tests，不新建报告/工程：`ALN.ASSET.01`全部route快照往返及未知tag/余byte/负零/超预算，两个schema原bytes/hash与Manifest/File/Descriptor闭包；`02`Train来源缺项/Export父模型/三Purpose缺任一显式target，seal前拒且旧只读不变；`03`原Offer重复/内容冲突、seal已确认verify失败、等待取消/迟到/重启原版本Unknown，零第二Import及无假Accepted；`04`MA C.5 tuple/source/schema与本producer adapter区分、Runtime Empty不丢创建/搜索语义；`05`challenge fresh reader/负例Passed不授生产、expected/observed不同但容差通过、精度Unknown、最后native迟到及双根无cleanup自等待；`06`A封存、B独立读取/搜索及A关闭后B继续、撤权/用途Unknown/包签名失败只阻对应用途。均是规格断言，当前未编译、未运行；本节内容自审不提升H/W/I运行资格。

### 5.2 状态机

`Created → Validating → Queued → AcquiringLease → Preparing → Searching → Associating → Fitting → ValidatingResult → Draining → Drained → ResourcesReleased → Completed | NoCandidate | Ambiguous | Rejected | InvalidInput | Cancelled | TimedOut | ResourceExhausted | BackendFailure | Unknown`。Phase闭集另包含OpeningModel/Training/ReadingBack/Exporting/Recommending/WaitingForDrain；它们按Train/Inspect/Export/Recommend分支替代Searching/Associating/Fitting，不强行走不存在步骤。Isolated为DrainStatus，Phase仍WaitingForDrain；停止请求锁存于StopReason而非另一个终态。

终止状态为：`Completed`、`NoCandidate`、`Ambiguous`、`Rejected`、`InvalidInput`、`Cancelled`、`TimedOut`、`ResourceExhausted`、`BackendFailure`、`Unknown`。前置未接纳校验失败属于 RequestRejected，无 OperationTerminal；接纳后租约/像素验证失败才用 InvalidInput 等终态。`Unknown` 只表示真实排空后仍无法确定计算产物/证据；资产提交未知归 model-assets 回执，不能在本模块伪造发布状态。`DrainUnknown` 是**非终态** `WaitingForDrain/Isolated`，没有 ResourcesReleased/OperationTerminal；不得等待超时就把它改终态 Unknown。

术语归一：表中的 `Partial` 是 payload 观察情况、`QualityRejected/DegenerateGeometry/EvidenceTruncated/ResourceExceeded` 是 ErrorCode（或 reason），不是另加 TerminalState。已接纳的部分证据无可用完整解时终态 Rejected；资源超限为 ResourceExhausted；缺点且完整搜索未检出时 NoCandidate + 保留其余候选。Completed 仅表示请求计算完成，必须另读 PurposeEligibility，不能映射工艺合格。

### 5.3 事件顺序

事件是可选诊断投影，不是结果写入权威。未接纳请求的短路径为 `RequestReceived → ValidationStarted → RequestRejected`，不取得租约；已接纳请求顺序固定为：

`RequestReceived → ValidationStarted → RequestAccepted → Progress* → CandidateBatch* → FittingStarted? → LogicalResultReady? → Draining → Drained → ResourcesReleased → OperationTerminal`。

同一 operation 的事件单调递增，`AlignmentEvent(Id,Generation,Sequence:long,Kind,Phase,MonotonicTimestamp,ResourceKey,Counts)` 不持有 native/图像缓冲。`LogicalResultReady` 只表示值已复制；`Drained` 表示所有后端工作真实返回；ResourcesReleased 为 operation 的帧/域/模型租约和临时资源归还，宿主持有的 artifact/result 副本不算泄漏；OperationTerminal 唯一且随后才完成 Completion。停止/故障分支允许跳过 Searching/Fitting/LogicalResultReady，但不可跳过 drain。隔离等待可以反复发布限流状态，不重复终态。事件使用有界异步通知：Progress 可合并，丢弃计数留证；终态以 Completion/Query 为权威，订阅者慢/抛错不阻塞 drain。`CandidateBatch` 为有界快照预览而非全部结果事实，不靠收到事件次数证明完整。

终态发布与RequestCancel以同一operation锁线性化：资源已确认归还后，在锁内读取已锁存stop/failure、固定唯一OperationResult和TerminalSummary→Query即见terminal→排队terminal通知→完成Completion。此之后取消返回AlreadyTerminal；此前已锁存取消/超时不得被后到成功覆盖。重入订阅者只允许Query/RequestCancel这些非阻塞入口，不同步等待Completion/Shutdown；通知线程不持operation锁。解除订阅/host关闭不影响后台终态。

## 6. 取消、超时、资源和线程

- 每个 operation 使用独立上下文、预算、结果缓冲和 native 适配对象；禁止共享可变模型句柄跨请求并发。
- 同一 native 模型实例的 train/set/search/clear 互斥；不同实例可以在总预算内并行。多模型获取租约按稳定顺序，避免环形等待。
- 取消先停止新派发，再向后端发出可用的停止/中断请求，等待 native 真正返回；完成 `Drained` 前不得释放帧、模型、XLD、取样场或缓冲区。
- deadline 接纳时用单调时钟冻结；到期锁存 TimedOut 原因并停止新派发。native 未返回时 Query=WaitingForDrain/Isolated，不返回正式终态；返回并释放后才 TimedOut。native timeout（如 NCC 9400）同样不是 NoCandidate，也可能有清理尾时。取消和超时以第一个锁存停止原因为主，后续原因保留诊断，不能把迟到成功覆盖停止状态。
- 如果目标后端没有可证明的硬取消边界，文档只能承诺“停止后续工作并异步排空”；宿主需要硬隔离时由宿主进程边界负责。
- 资源在成功、失败、取消、异常、部分复制和订阅者抛错路径均走 finally/租约释放；任何旧代迟到结果都不能进入新请求。

释放按native临时结果/模型→ROI/图像/资产lease反向序列，逐个尝试并聚合错误，不因首个DisposeAsync异常漏掉后续释放。若任何释放未能确认，保留该owner/引用及诊断，DrainStatus=Isolated、Completion不完成/无ResourcesReleased；没有公开幂等释放/查询能力时不能盲重试double-clear，由宿主隔离边界恢复。可确认全部归还但复制/计算失败则正常BackendFailure终态。资源lease不得以CancellationToken取消它自身必要的finally归还。

Engine采用BCL有界Channel + 固定MaxActive个异步消费者，消费者调度用TaskScheduler.Default且不设置LongRunning/专用线程/全局线程数，await异步ports；同步native段在有限worker的线程池上下文执行，不每候选新Task。队列固定MaxQueued、接纳前TryWrite失败即ResourceExceeded，排队超时已接纳操作仍drain（无native则立即释放）。A/B native默认串行，共用预算；本版同operation不并行A/B，跨operation只在独立模型/只读lease及合计预算内并行。按modelId/revision/hash稳定顺序获得多租约；资源失败释放已取部分。不使用UI Dispatcher计算、不改HALCON全局线程参数。

v0.2.1 不提供跨 Engine 共享 native 模型缓存。可选实例缓存不在本版运行能力内；如后续加入须另冻结key（method/backend/adapter/preprocess/origin/训练参数/hash）、有界驻留、租用互斥、引用计数及逐出等待，不以路径/名称为唯一key。模型资产内容不可变，运行参数只改租约内native实例；训练/打开/导出/关闭与搜索同句柄互斥。operation generation防止旧结果进入新视图；host复用采集像素前必须等全部只读租约归还。

如果 backend 永久不返回，Core 保留 lease 并拒绝复用隔离实例；Shutdown=Pending，禁止强行 clear/释放。宿主进程隔离退出后的结果为 LostOperation/不可知计算事实，由宿主恢复，不能由已终止进程“补发 drain”。资源预算分为可计数 bytes/候选/组合/队列，以及估计 native 暂态；后者无可证明界则诊断 Unknown，只在有适用宿主硬界时承诺硬内存限制。取消导致未完成候选/字段必须标 Partial/Unknown，已有数据仍仅诊断。

## 7. 错误码语义

错误码稳定、可本地化文字与机器语义分离。本版冻结的机器码：

| 代码 | 语义 | 是否可由调用方重试 |
|---|---|---|
| `ALN-001 InvalidRequest` | 必填字段、范围或 frame 不合法 | 修正请求后新 attempt |
| `ALN-002 InputUnavailable` | 图像/域/租约不可读或过期 | 由宿主重新提供输入 |
| `ALN-003 ModelUnavailable` | 模型缺失、hash/revision/能力不符 | 更换已批准资产 |
| `ALN-004 UnsupportedMethod` | 公共后端不支持请求方法 | 不得自动换路线 |
| `ALN-005 NoCandidate` | 完整搜索无候选 | 由闭集策略决定是否备用 |
| `ALN-006 Ambiguous` | 两个或更多不等价解释通过硬门 | 需调用方消歧或人工处理 |
| `ALN-007 DegenerateGeometry` | 点数、基线、分布或条件数不足 | 更换有效特征/请求 |
| `ALN-008 QualityRejected` | 支撑、边界、残差或用途门不满足 | 由用途 Owner 决定 |
| `ALN-009 Cancelled` | 收到取消，终态不发布资格 | 可新建 attempt |
| `ALN-010 DeadlineExceeded` | 绝对 deadline 到期 | 不能当 NoCandidate |
| `ALN-011 ResourceExceeded` | 字节、候选、组合或并发预算耗尽 | 收紧请求或扩预算 |
| `ALN-012 BackendFailure` | AsunImage/HALCON 明确异常 | 需诊断后新 attempt |
| `ALN-013 DrainUnknown` | native工作/资源归还未确认；非终态诊断 | 隔离实例，继续查询/等待，禁止复用 |
| `ALN-014 EvidenceTruncated` | 结果因输出预算不完整 | 不能声明唯一/完整 |
| `ALN-015 ContractMismatch` | 版本、字段或能力契约不兼容 | 升级适配器或回退 |
| `ALN-016 CoarseSupportInsufficient` | 粗模型支撑/窗口覆盖未资格 | 按预配置原图域补搜，否则诊断拒绝 |
| `ALN-017 GeometryNotQualified` | 全域几何/局部grid用途资格不足 | 保留诊断；补技术资格后新attempt |
| `ALN-018 OperationIdRejected` | 未预留、重复或旧代次ID | reserve新ID；不重用旧请求 |
| `ALN-019 EngineClosing` | 关闭/隔离后拒绝准入 | 原实例排空；新实例新代次，不重放原操作 |

合法组合：OperationTerminal Cancelled→ALN-009；TimedOut→ALN-010；ResourceExhausted→ALN-011（截断诊断可另带014）；Ambiguous→006；NoCandidate→005；Rejected→007/008/014/016/017；InvalidInput→001/002/003/015；BackendFailure→012；Completed→无主错误（诊断候选仍可有拒绝原因且Purpose=NotEvaluated）。Unknown→012/014/015并明确未决产物，**禁止终态ALN-013**。004/018/019为派发前RequestRejected；若接纳后能力/模型内容验证才发现不相容，InvalidInput +004/015。其它组合是契约错误，测试必须拒绝。

RequestRejected不套用上面终态表；ValidationError允许001/003/004/007/011/015/017/018/019，分别指纯值、静态模型描述、route、预知退化、准入容量、版本、缺资格输入、ID与关闭。完整性/歧义/取消/超时来自已接纳操作，不伪装RequestRejected。BeginFit已给单点/共线则可在native前007拒绝，搜索后才发现点不足则Rejected+007。

## 8. 适配器和版本兼容

适配器负责把 `ImageLibDotNet`、帧、模型资产、坐标和 ROI 映射到模块端口；不得把 HALCON `HObject/HTuple`、native handle 或 WinForms 控件类型暴露到公共契约。适配器必须报告实际后端版本、可查询参数、不可查询参数、取消能力和结果复制完成点。

兼容策略：

1. 公共结果新增可选字段只在 minor 版本增加，并保留未知字段读取能力。
2. 坐标方向、矩阵方向、单位、方法族、模型内容或状态语义改变必须升 major 或显式能力修订。
3. 旧模型只能在适配器声明兼容且重新读回核对通过时使用；不能因文件可打开就宣称同内容。
4. 回退包必须包含旧二进制、适配器、模型闭包、参数快照和回退判定；回退不自动恢复设备生产或质量放行。
5. 升级前在两个消费者运行旧/新输入组合、边界和取消矩阵；未知组合拒绝运行。

## 9. 无 UI 调用示例

以下是基于本版拟建接口的**宿主语义示例**，不是已编译代码。BuildRequestFromFrozenProfile是宿主函数，不是新增 Core API；它只组装 §3 字段、模型/域引用，不预取帧/模型租约。Core拥有接纳之后的资源获取与释放。

```csharp
await using var engine = AlignmentEngine.Create(options, ports, timeProvider);
var id = engine.ReserveOperationId();
var request = BuildRequestFromFrozenProfile(id, frameRef, modelRefs, profile);
var admission = engine.BeginAlign(request, computeCancellation);
if (admission is OperationAdmission<AlignmentResult>.Rejected rejected)
{
    PreserveValidationErrors(rejected.ValidationErrors);
    engine.ReleaseOperation(id);
    return;
}
var handle = ((OperationAdmission<AlignmentResult>.Accepted)admission).Handle;
// UI/CLI观察等待可独立超时；超时只结束观察，不归还在途资源。
OperationResult<AlignmentResult> terminal;
try { terminal = await handle.Completion.WaitAsync(observationBudget, waitCancellation); }
catch (TimeoutException) { PreservePending(engine.Query(id)); return; }
catch (OperationCanceledException) { PreservePending(engine.Query(id)); return; }
PreserveTerminal(terminal);
if (terminal.TerminalState == TerminalState.Completed &&
    terminal.Payload?.PurposeEligibility == PurposeEligibility.Qualified &&
    terminal.EvidenceCompleteness == EvidenceCompleteness.Complete)
    ConsumeCandidateOrPose(terminal.Payload);
engine.ReleaseOperation(id); // 只释放有界账本；此时operation资源已归还
```

观察等待结束后 return 仍会进入 await using DisposeAsync 并等待实际 drain；这是后台工具完整关闭示例，**不是有界退出承诺**。交互宿主不在观察handler中Dispose engine，应让宿主资源Owner保留它，用ShutdownAsync报告Pending。进程必须硬退出时使用预定隔离边界，不清理被native持有的内存。新请求先保证原实例可用/已排空；不能重复使用id。结果消费不创建质量/设备事实。

训练产物交接使用§10.3的唯一公开签名，下面仍是宿主语义示例，trainingTerminal已真实终态且含完整artifact；PreserveOffer/PendingOffer/Receipt是宿主保管函数，不是Core新增API：

```csharp
var offer = new ArtifactOffer(Guid.NewGuid(), trainingTerminal.OperationId,
    trainingTerminal.Generation, artifact);
PreserveOffer(offer); // 宿主一次生成并绑定产物hash，先保管再调用
var handoffTask = host.OfferArtifactAsync(offer, CancellationToken.None).AsTask();
try
{
    var receipt = await handoffTask.WaitAsync(observationBudget, waitCancellation);
    PreserveReceipt(offer, receipt); // 验OfferId，并按原operation/generation归档
}
catch (TimeoutException) { PreservePendingOffer(offer, handoffTask); }
catch (OperationCanceledException) { PreservePendingOffer(offer, handoffTask); }
```

Pending回执同样由宿主保管既有OfferId的尾项；观察超时、页面关闭或切换都不生成新offer、不再提交。handoffTask的其他异常由宿主错误处理保留原offer与未知状态；未知不解释为Rejected，不触发自动重发。迟到回执只更新原交接记录；当前视图还须匹配view generation后才可显示。

### 9.1 两个独立最小消费者与执行顺序

Consumer A=无UI工程注册 Host：只引用Core、显式simulation backend/CoordinatePort测试适配，使用 §4.7 两点+π/2例；Consumer B=无UI局部目标导航 Host：独立engine/Options/ports/ModelRef，使用q=(0,0)/(50,0)、p=(5,7)/(55,7)固定尺度位姿，目标关联只在host。二者规划为BCL Exe测试工程内两个fixture，不为示例额外建产品Shell。未来真实消费接线各自引用公开Core与HalconAdapter，同fixture语义，不能把模拟host叫真实消费者验收通过。

从空宿主到调用的固定顺序：构造有限options/TimeProvider→显式ports（无UI、无数据库、无SDK）→Create→Reserve ID→冻结头/frame/model/ROI/profile→BeginFit或BeginAlign→拒绝保留ValidationErrors/Release；接纳保留Handle→可选RequestCancel/Query→Completion（真实drain/释放）→保存值结果/宿主采用→ReleaseOperation→Shutdown/Dispose。模型工程调用 BeginTrain→Completion Artifact→宿主交给资产Owner（不在Core示例冒发布）→BeginInspect→以hash绑定ModelRef搜索；BeginExport不更改运行模型。Replay换新engine generation/id，ParentOperationId引用旧记录。

并发断言：阻住A backend真实返回→取消A→Query=WaitingForDrain、A frame/model未dispose；B仍正常完成且leases归还；释放A闩锁→一次Cancelled终态→A leases归还。B结果与单独运行容差一致。A关闭不能Dispose B、写全局culture、清B缓存或改HALCON线程。Host的选择窗口从E1切E2时旧E1结果仍归E1，不覆盖E2。

### 9.2 两个独立空 Host 的公开装配与有限收尾（规格）

§9/9.1保留已接收纯Core语义示例；其await using只是CLI完整drain示例，不供本节交互Host复制。本节Host-A=离线工程双Mark编程/Replay，Host-B=只读生产Inspect/查找；各自独立root/slot/Runtime/Options/上游service租约/输入实例，真实输入各来自其生产者冻结的FrameRef、ModelDescriptor及A/B Fine/Coarse精确资产绑定。无Shell、数据库私表或隐藏窗口。两个Host都可以无UI；带UI时分别STA Thread/Dispatcher创建本Host Window/Workbench/ViewportControl，A/B不共享控件、session、culture、native handle或未返借用。公开构造全见§5.1A/B与§10.3A，下面不是已经编译/运行的样例。

装配Profile是调用前冻结的具名资源参数，不给算法/客户门默认值。用于未来Host负向验证的**软件限额例**：Root MaxHosts=1、MaxCallsPerHost=256、MaxAnchorsPerHost=32、MaxHeldBytesPerHost=512 MiB、MaxIdUtf8Bytes=256、ReservedCleanupCallsPerHost=64；Cleanup ExecutionTimeout=10s、WaitTimeout=2s、MaxQueryAttempts=8、QueryInterval=100ms、MaxErrors=32；Engine MaxQueued=8、MaxActive=1、MaxReservedIds=32、MaxRetainedResults=8、MaxRetainedBytes=64 MiB、MaxNotificationQueue=64，LimitsCeiling.Bytes=128 MiB、NativeModelBytes=64 MiB、MaxCombinations=256、MaxQueued=8、MaxActive=1、MaxRetainedResults=8，ModuleVersion=0.5.3-prep、ContractRevision=v0.2.1。Halcon MaxCopiedFrameBytes=32 MiB、MaxModelBytes=8 MiB、MaxTemporaryBytes=16 MiB、MaxNativeOperations=1，EnabledRoutes在两个Host均显式只选GenericShape/Ncc；其它已定route可后续独立Host Profile启用，不增新自由路线。UiProfile MaxVisibleCandidates=256、MaxOverlayPoints=4096、MaxQueuedUiCalls=16、MaxRetainedUiBytes=64 MiB、RefreshInterval=100ms及同Cleanup。这些值只用于有界构造/故障样例，不是已测内存/节拍或物理验收值；真实frame/model/workload超额先拒，不能缩小原图数据偷偷继续。

| 顺序 | Host-A：Engineering | Host-B：ProductionInspect | 拒绝/有限恢复 |
|---|---|---|---|
| 根预约 | 应用入口new AlignmentProcessRoot(A-profile,clockA)→ReserveHost("A")→KeepAnchor("lifetime",A私有HostLifetime,预申报bytes)→SetCleanupPlan | 独立rootB/clockB/ReserveHost("B")/B lifetime，自己的计划 | 根满/无计划在任何工厂前失败，无外部副作用；所有上游根/端口/输入保持在本lifetime，不能方法离栈丢它 |
| 原服务（若消费桥） | 原ModelAssetsHostRoot.Reserve(A Scope)→KeepAnchor/SetCleanupPlan→ModelAssetsHost.Create原全部Options/Ports/slot；FrameServiceFactory.Create原ResourceLimits/validator/clock/events | B自己的Scope/Principal/ServiceInstanceId/ConsumerId与登记limits，既有共享service仅借用 | 缺真实Store/Authority等只对应模型桥不可用；可用批准的直接Core端口，无模拟生产资产；创建失败结果/错误也保留原factory调用 |
| 内容与桥 | Entries明确A-Fine/A-Coarse/B-Fine/B-Coarse、参考及搜索frame；原Resolve runtime purpose与ReadForUse权限；AlignmentModelAssetsBridge.Create/AlignmentImageFrameBridge.Create | 独立精确Entries，CanTrain/Export=false；不取得Latest/alias | 生产者没完整descriptor/source hash/content rule则该entry拒，原因入证据，不能自己补工艺值；未知原call查询不重开 |
| runtime factory | 根预登记A/1 factory原调用，new AlignmentRuntimeFactory().Create(A-options,A-services,slotA,clockA)；成功session先写lifetime | 同公开factory，Mode=ProductionInspect、独立SessionId，结果先保管 | 失败Session=null；意外部分对象仍是factory/root清理责任，不交空壳成功；Create无native/服务IO |
| 无UI业务 | ReserveOperationId→新Train/Inspect/Align/Recommend请求：四模型训练分别新ID；Recommend只取已完成Replay评估 | Inspect所选四精确模型→只读逐字段报告；新Align双slot+原§4.7粗精输入，禁止Train/Recommend/Export | root.StartCall在发Begin之前登记start，Begin若Accepted，将Handle/原Completion即刻写lifetime，预留槽保持到原Completion真实返回；Rejected只释放账本，无假terminal；预留ID用后不重用 |
| 结果 | 保存完整深副本/原Requested+Resolved；生产参数改变需外部Owner决定新asset/config revision | 原图/候选与pA/pB连线/Residual/Purpose；不得将匹配score映PASS | 保留原operation/generation/model/hash，事件只是预览；copy/bridge/cleanup错均可恢复查询，不覆盖PrimaryError |
| 可选UI | 下列独立STA步骤，权限Engineering且host实时可撤 | 独立STA，CanView/Search，训练/保存动作不提供执行；授权规则与原viewport生产Required准入保持 | 没WPF/viewport能力只拒UI桥，无UI返回继续；Root记原Dispatcher/Bind/Attach/Detach task，不把窗口图当Golden |
| 正常或异常收尾 | slot.CloseAsync独立cleanup预算；原plan逐资源DAG运行，Observe原host；已全归还root.TryReturn | 只关B本资源；A可继续，借用共享service不关 | 返回DrainUnknown保留root/lifetime/原Task/原Service，不以using/finally强Dispose父资源；晚到factory/lease/terminal回原槽后续归还，不新发业务补结果 |

原服务Options/资源/权限的构造形状严格用上游已冻结签名，不让Host创造自己的S1/IFR释放Owner。ModelAssets需要已公开Store/UsageAuthority/format端口的实现，IFR需要原IManagedLayoutValidator及只读IFrameInputRows来源；空Host的未来软件验证可显式使用各原模块获批Simulator，但必须ServiceEvidenceMode=Simulation/离线viewer，不称生产Host验收。真实Host-B上游必须Production模式/权限/fence；缺真实适配仅记对应桥NotReady，不让整个已接收Core规格退回。

**两个STA构造步骤**（宿主私有STA入口，不是模块新增公开API）：先上述root/HostLifetime/计划，在受管call中启动独立Thread→SetApartmentState(ApartmentState.STA)→线程内取得Dispatcher.CurrentDispatcher（该线程无native初始化）→创建本Host原ViewportRootFactory/Root→同STA new ViewportControl→按§10.3A.1取得同Control/root的Renderer Backend/Lifetime及完整Resources→CreateFactory→Create原ViewportOptions（Presentation=该Control.Presentation，Backend=原Renderer.Value.Backend，全部Required/BudgetOnly、Frames/Coordinates/Authorization/Limits参数由已冻结VP Profile显式传入）→用原Control.BindAsync(session,vpRoot,完整ViewportUiBindingOptions,ct)，OwnSession=false且Lifetime显式非null；绑定原Task先保管，async continuation回所属Dispatcher，成功UiBinding即刻写HostLifetime→AlignmentViewportBridge.Create→AlignmentWorkbenchFactory.Create→将Control挂本Host显式Window（1920×1080验证viewport内）→首次显示才Session.AttachAsync→Dispatcher.Run维持UI。工厂/窗口控件都在该STA；上游Bind的原DispatcherTask由其root强持，外层Bind Task及本STA线程完成Task由Alignment根强持，不将InvokeAsync的等待包装当原Task；各异步步骤由运行中的所属Dispatcher继续，不同步Wait/Result。

独立语言A=zh-CN/B=en-US后各自切zh-TW，再切回，typed draft/selected CandidateId/各根IDs不变，不设置Thread.CurrentCulture/Application全局主题影响另一Host。同一主题资源来自本Host明确ThemeKey和本控件资源域；DevExpress全局主题如仅有全局API则不做跨Host动态切换，以固定双方一致主题验证，不冒独立主题实现。操作顺序分别原图→A/B模型详情→Inspect差异/训练候选（只A）→搜索→表行联动原图候选/连线→取消/查询→语言/权限变化→关闭；两个Host共享同DLL、不同参数和输入，当A工作被native/port闩锁阻住时B关闭/完成不释放A任何资源。

Window.Closing只启动原Host.Close受管Task并取消新的交互，先撤可见内容也不马上Shutdown Dispatcher；UI任一constructor/Attach/Bind同步抛错先NotePrimary，finally仅启动本计划的有限观察，无`await using`无限堵Dispatcher。每个cleanup step单独try/catch/finally，后步要其DependsOn真正Released；一个独立child失败不阻其它安全child，但不能关仍被borrowed的父service。waitToken已取消仍使用独立Cleanup预算；真实Detach/Unbind/viewport Dispose/Engine Shutdown/bridge release/自有service Close完成后才Window.Close/Dispatcher.BeginInvokeShutdown和join本Thread。有限join到期为DrainUnknown，根保留STA/Task，不能Thread.Abort、丢Dispatcher或宣称退出。宿主硬进程隔离仅依既定隔离边界，记录Lost/Unknown，不补资源释放事实。

## 10. 可选 UI 契约

### 10.1 任务、权限与页面组成（PC-ALN-001）

独立 `AlignmentWorkbench : UserControl`，不依赖产品Window/ViewModel；核心可无UI调用。操作者默认查看原图/候选/未检出原因；工程师显式权限下编辑训练草稿/ROI/模型原点和搜索Profile、比较候选、导出候选；模型发布与用途采用交回宿主命令，模块没有发布按钮。角色不写死成厂内职位枚举，由 `IAlignmentUiHost` 提供权限snapshot；Viewer/诊断记录均只投影。

一个紧凑工具栏+图像主区+slot/参数边栏+底部证据，不用装饰卡片。固定1920×1080物理验证viewport，记录OS taskbar/window/title/status的实际占用及DPI，以**真实客户区**分配：toolbar 44 DIP、status 28 DIP，剩余高度主图/底部证据约72:28；宽度参考slot 18%、viewer 58%、参数24%，slot至少220/参数300 DIP，不足时slot折为固定页签且参数自滚动，viewer仍占≥55%可用宽。同一1920物理屏若DPI变，按客户区DIP约束验，不改显示设置、不跑另一分辨率矩阵。普通文字13–14 DIP/分区标题16，8 DIP间距/12 DIP外边距，细分隔线、宿主题、DevExpress glyph；影像不套卡片、不被提示面板遮住；拒绝/歧义用文字+图标和受控颜色，不能只靠红绿。

面板稳定Name=`AlnSlots/AlnImage/AlnParameters/AlnEvidence`；DockLayoutManager + LayoutPanel，image/status/取消关键区域AllowClose=false/AllowFloat=false。证据可调整/收回但留可见入口，恢复布局由host保存受信视图数据，不保存配方/模型。顶部命令=打开参考/打开运行图（宿主选择）、训练、搜索、取消、导出候选、恢复布局；按route/状态/权限显式启用，不藏关键命令到DropDown。高级参数按分组折叠，无可用route不提供可执行成功按钮。

### 10.2 DevExpress 25.2.3 具体控件与联动

| 区域 | 控件/API与操作 | 状态、联动与恢复 |
|---|---|---|
| slot/模型树 | GridControl+TableView，稳定FeatureId行、Required checkbox、Fine/Coarse revision/hash、method、支撑状态；不按显示排序更换ID | 多slot可批量编辑同route草稿参数，混合值显式空/混合；单元编辑提交调用同一Core校验，不直接set模型。A/B不合并巨大模型；选择slot使viewer显示其参考点/域/模型原点 |
| 图像区 | 宿主注入Viewer公共控件；原图/训练图/粗层/精层页签、叠加图层checkbox、fit/1:1/缩放图标工具及SuperTip；双图并排仅在比较模式启用 | 叠加在图像坐标绘制，再走viewer映射，不用屏幕点当测量；候选选中高亮，全部未选候选仍可显示；鼠标定位域/原点编辑生成新draft，操作不改已运行证据 |
| 参数 | PropertyGridControl.SelectedObject绑定强类型草稿分支，分组训练/搜索/几何/预算；SpinEdit输入角度/scale/预算、CheckEdit二值、ComboBoxEdit路线/metric | UI显示角度°，提交一次转rad；单位固定标签；固定角不是0..360。只读显示actual值/auto来源与模型范围，超范围行内错误，不静默裁剪；生产引用与draft明显分开 |
| 证据表 | GridControl.ItemsSource+TableView.ShowAutoFilterRow/AllowPerPixelScrolling；按slot/阶段/拒绝原因分组、只读排序/过滤、矩阵/链详情页签；行选择以CandidateId同步 | 过滤只影响视图，顶部仍显示原始/筛选数、MissingRequired和Complete/Truncated；不能过滤掉拒绝行后显示唯一合格。matrix详情明确source→target/frame/unit；Local显示RawRasterOnly/已绑定，不展示虚构angle |
| 状态/错误 | BarItem.SuperTip，非Bar控件ToolTip承载SuperTipControl.SuperTip；固定status区带错误码、短原因和一项安全下一动作 | Searching可取消；Draining显示“正在释放资源/正在釋放資源/Releasing resources”；Isolated显示“等待算法结束/等待演算法結束/Waiting for algorithm”；取消保持可见但重复点击幂等，原实例禁止重跑 |

上述实际公开成员已从本机25.2 XML读取：DockLayoutManager/LayoutPanel、BaseLayoutItem.AllowClose/AllowFloat、SaveLayoutToStream(Stream)/RestoreLayoutFromStream(Stream)、GridControl/TableView过滤/滚动、PropertyGridControl.SelectedObject。选中绑定**冻结使用**DataControlBase.CurrentItem双向绑定typed selected row，再由CandidateId/FeatureId更新overlay；允许多选草稿slot时SelectedItem仅表示首选行，不以它推断全部多选。DataViewBase.FocusedRowChanged只作焦点通知，NavigationStyle属性属于DataViewBase，不能误写另一类型声明。PropertyGridControl.CellValueChanged触发typed草稿重校验；PropertyDefinitionBase.IsReadOnly控制actual字段，实际执行权限仍取host snapshot。也已定位PropertyGridControl.ValidateCell/ShowingEditor/CellValueChanging，但本版不依赖未经冻结的事件参数成员；编辑校验用typed草稿setter/INotifyDataErrorInfo→AlignmentValidation.ValidateDraft，不能以默认PropertyGrid提示当Core校验。SuperTip公开用法/25.2.3签名复用§16。真实编译/双向绑定行为、三语/native弹窗与WPF运行是切片验证门，非接口“以后任选”。环境无dxdocs可调用、官网403不解释为不支持；用本机公开文档，不核安装/授权、不换版本。

### 10.3 连续任务、键盘、挂接与关闭

打开参考→逐slot圈训练域/点原点→选择route/角域/尺度/粗策略→校验草稿→训练（新ID）→显示actual参数/模型轮廓/完整artifact→导出候选由宿主资产Owner接收；失败留草稿，原模型引用不变。打开运行图→冻结已选择revision与搜索请求→搜索→查看全部slot/候选/完整性→候选联动与几何/field详情；完整无候选可按预定AttemptPlan备用，不从UI静默改参数。工程师选择歧义候选只生成 `SelectionProposal` 交给宿主，新Profile/attempt后重算，不能在原结果里改Ambiguous为Completed。

Tab 顺序=toolbar→slot→viewer工具→参数→证据→状态恢复；Enter提交编辑而不自动搜索，Space切checkbox，Escape取消当前编辑/退出ROI绘制（不冒运算取消），F5只有搜索permission且draft有效且instance可用时搜索。Delete只移除草稿slot，不能删除资产。viewer方向键平移、+/- zoom使用宿主既有键盘契约不重复劫持；每个图标button有本地化AutomationProperties.Name/SuperTip，焦点框可见。保存/导出dialog由host指定，避免模块私自写路径。

挂接契约：`Attach(AlignmentWorkbenchContext)`、`UpdateHostState(AlignmentUiState)`、`SetLanguage(LanguageSnapshot)`、`ValueTask<DetachReceipt> DetachAsync(DurationBudget waitBudget,CancellationToken waitCancellation)`。context=`HostId,Engine:IAlignmentEngine,Viewer:IAlignmentViewerPort,Host:IAlignmentUiHost,ThemeKey,LanguageSnapshot,PermissionSnapshot,InitialDraft`；Engine由host拥有，控件不Dispose它。state=`HostId,ContextGeneration,FrameRefs,ModelRefs,ProfileRef,PermissionSnapshot,IsClosing`；View generation每次context/frame/profile更改递增，记录 operation id+engine generation+view generation，旧结果可保留hosthistory但不能进入当前viewer/参数。

`IAlignmentViewerPort`（不包含厂商viewer类型）：`FrameworkElement View`、`ShowFrame(FrameRef,ViewGeneration)`、`SetOverlay(AlignmentOverlay,ViewGeneration)`、`FocusCandidate(CandidateId,ViewGeneration)`、`Clear(ViewGeneration)`；Overlay=`OperationId,Lines:ImmutableArray<OverlayLine>,Points:ImmutableArray<OverlayPoint>,Domains:ImmutableArray<DomainRef>,SelectedCandidateId?`，line/point为PixelPoint和SemanticStyle/资源键；坐标链来自结果，由host实际viewer公共能力转换。viewer仅自己所需display lease，Clear不得归还engine帧。`IAlignmentUiHost`：`PermissionSnapshot GetPermissions()`、`ValueTask<UiSelection> SelectInputAsync(InputKind, CancellationToken)`、产物交接按下方唯一签名、`void RecordSelectionProposal(SelectionProposal)`、`void PreserveOperation(OperationId,Generation)`；InputKind=ReferenceImage/SearchImage/ModelSnapshot，UiSelection=Cancelled/SelectedFrame/SelectedModel；SelectionProposal含operation/candidate IDs/profile revision/理由，不能输出设备动作。

`PermissionSnapshot(Revision,CanView,CanEditDraft,CanTrain,CanSearch,CanExport,CanProposeSelection)`，命令执行前取当前snapshot再验；权限变化阻止新命令，已运行结果可按hostview权限处理，不能提前释放。LanguageSnapshot=`CultureName,Revision,Resources:IAlignmentTextSource`；text source `string Get(string resourceKey)`，允许文化zh-CN/zh-TW/en-US及扩展，不改Thread/进程全局culture；所有本模块UI/原生启用弹窗文字按040有限实例策略，语言更新保留typed草稿/选中ID/焦点，不从译文反推enum。宿主授权/持久化/异步输入接口超时只终止UI等待，迟到回执按handoff id交host处理，不由控件第二次保存。

`IAlignmentUiHost`的产物交接仅有这一签名（无ModelArtifact重载、无省略身份的版本）：

```csharp
ValueTask<ArtifactHandoffReceipt> OfferArtifactAsync(
    ArtifactOffer offer, CancellationToken cancellationToken);
```

`ArtifactOffer(OfferId:Guid,SourceOperationId:OperationId,EngineGeneration:Guid,Artifact:ModelArtifact)`；`ArtifactHandoffReceipt(OfferId:Guid,Status:ArtifactHandoffStatus,HostReceiptRef:ProfileRef?)`，ArtifactHandoffStatus仅Accepted/Pending/Rejected。OfferId与EngineGeneration均非空Guid，SourceOperationId属于该代训练/导出终态，artifact完整且hash匹配；OfferId由宿主在一次交接开始时生成并固定，不从UI generation生成。Accepted必须有非null宿主回执引用；Pending未确认接收，Rejected明确拒收，二者不冒发布或Alignment OperationTerminal。

宿主先按OfferId原子登记不可变offer（绑定source operation/generation及artifact hash）再启动资产Owner交接；重复同offer返回既有状态，不再次持久化，同ID不同内容拒绝。cancellationToken只停止该调用的观察等待，已登记的尾项仍归host，未登记且取消不产生副作用；UI观察超时/Pending/未知都不得重发或换ID。同一方法调用无论页面是否还打开，host都保存最终回执并匹配OfferId及已存source generation；view generation只决定当前页面能否显示。尾项、artifact bytes与回执受宿主明确容量/保留策略约束，不放控件私有无界Task列表。宿主input selection只返回不可变引用，迟到SelectedFrame/Model不应用旧view generation；若内部打开了显示租约由host清理，控件不取得隐式资源。

Detach先禁止命令/解绑事件/停止绘制→RequestCancel本视图发起且仍在途的operation→host PreserveOperation接管→清viewer显示lease→有限等待；已drain返回Detached，未drain返回DetachedWithPending(ids)，仍由hostEngine持有资源，不阻塞Dispatcher Dispose。已登记ArtifactOffer尾项继续由host按原OfferId保管，Detach/UpdateHostState/重新Attach均不触发重发。重新Attach必须新view generation；页面关闭不disposehostshared Engine，不清其它页/消费者。host退出执行ShutdownAsync，Pending显示等待/隔离动作，不能把关闭窗口当native停止。Theme/语言/布局恢复只改视图，不运行训练/算法。

### 10.3A WPF 自有构造与原 viewport 消费（Assembly Contract v0.1）

以下只补可选Wpf包装配，原§10.3 Attach/UpdateHostState/SetLanguage/Detach及唯一ArtifactOffer签名保留，不增加产品Shell或语言入口。公开声明namespace=`Asun.Modules.Alignment2D.Wpf`，Factory使用§5.1A Halcon包的强持根，不把WPF类型带回Core；不同Host在各自STA构造自己的Control/Dispatcher。

```csharp
public sealed record AlignmentUiProfile(ProfileRef Revision,
    int MaxVisibleCandidates, int MaxOverlayPoints, int MaxQueuedUiCalls,
    long MaxRetainedUiBytes, TimeSpan RefreshInterval,
    AlignmentCleanupProfile Cleanup);
public sealed record AlignmentWorkbenchOptions(string BindingId, AlignmentUiProfile Profile);
public sealed record AlignmentWorkbenchServices(AlignmentRuntimeSession Runtime,
    IAlignmentViewerPort Viewer, IAlignmentUiHost Host, string ThemeKey,
    LanguageSnapshot Language, PermissionSnapshot Permissions, WorkbenchDraft InitialDraft);
public sealed record AlignmentWorkbenchCreateResult(AlignmentWorkbenchSession? Session,
    ImmutableArray<ValidationError> Errors);
public sealed class AlignmentWorkbenchFactory
{
    public AlignmentWorkbenchFactory();
    public AlignmentWorkbenchCreateResult Create(AlignmentWorkbenchOptions options,
        AlignmentWorkbenchServices services, AlignmentHostSlot owner);
}
public sealed class AlignmentWorkbenchSession
{
    public string BindingId { get; }
    public AlignmentWorkbench Control { get; }
    public ValueTask<DetachReceipt> CloseAsync(DurationBudget waitBudget,
        CancellationToken waitCancellation);
}
// Existing public Attach/UpdateHostState/SetLanguage/DetachAsync remain §10.3.
public partial class AlignmentWorkbench : UserControl
{
    public AlignmentWorkbench();
}
```

Factory constructor无控件/IO/后台工作；Create必须当前STA、有运行Dispatcher且owner已Reserve/计划/anchor，校验profile/BindingId/语言/权限/资源长度/预算在控件分配前完成，错误返回Session=null+原ValidationError（参数/资源码），无半绑定交付。AlignmentWorkbench无参constructor只创建本控件视觉树/命令绑定，无native/服务查找/文件/隐藏Window/查询；单独构造也要宿主先预约根，Attach前不可执行。Factory在该STA构造控件、原Attach上下文，services.Viewer.View只能属于同Dispatcher且无其它Parent；一个BindingId与Runtime.Generation只绑定一套services，不按名字从全局找Engine/Viewer/ModelAssets。Factory及Context结果先写HostLifetime再给窗口Content，WPF Application不是依赖解析器；每Host显式dispatcher/resources。

UiProfile所有计数/bytes/RefreshInterval正且受根/Engine对应资源上界，MaxQueuedUiCalls保留至少一个Detach/语言刷新槽，MaxVisibleCandidates不能改变完整结果分母；超过可见上限显示摘要+选中窗口和原始/显示数量，不把视图裁切写成唯一候选。Refresh为有限合并间隔，任务额度预约在Dispatcher.InvokeAsync**之前**，原DispatcherOperation.Task强持至实际执行/取消确认；更新仅替换尚未执行的同view-generation预览，不丢Detach/归还或终态回执。根StartCall的trusted start在有限worker执行；UI分支不得在那里构造控件，须闭包调用已强持的所属Dispatcher.InvokeAsync并在该Dispatcher原Operation.Task中完成创建，原Task先登记再有限观察。该STA同步Create/Attach只校验并挂接，native/像素hash/服务IO由受管worker，禁止Dispatcher同步Wait/Result。

ProductionInspect界面默认只读运行图/已批准A/B与参数、搜索/取消/查询状态；CanTrain/CanExport/CanEditDraft/CanProposeSelection与runtime模式、当前host权限共同判，Production禁止工程操作即使host误授CanTrain。Engineering参考编程与推荐分开页签，训练生成新候选、推荐读取已完成独立Replay评估，显式“导出候选”才进入宿主交接；“搜索”不隐式Inspect改参数或train。主动作按状态只有一项：可运行→搜索；在途→取消（资源正在释放时显示状态，重复取消幂等）；DrainUnknown→查询状态；缺模型→重新选择。Inspect进度/差异在证据区，不能称“已发布”。核心校验原validator、角度rad/显示°和三语保持§3/10。

**原viewport窄桥唯一装配。** 同Wpf namespace，公开面仅用原Viewport类型：

```csharp
using VP = Asun.UI.Viewports;
using VPW = Asun.UI.Viewports.Wpf;
public sealed record AlignmentViewportSourceEntry(FrameRef Frame,
    VP.ImageSourceDescriptor Source, VP.SourceRole Role);
public sealed record AlignmentViewportBinding(VP.IViewportSession Session,
    VPW.ViewportControl Control, VPW.IViewportUiBinding UiBinding,
    VPW.ViewportUiResources Resources, ImmutableArray<AlignmentViewportSourceEntry> Sources,
    VP.AuthorizationSnapshot Authorization, AlignmentUiProfile Profile);
public sealed record AlignmentViewerBridgeResult(IAlignmentViewerPort? Viewer,
    ImmutableArray<ValidationError> Errors);
public static class AlignmentViewportBridge
{
    public static AlignmentViewerBridgeResult Create(AlignmentViewportBinding binding,
        AlignmentHostSlot owner);
}
```

三对象是Host按§10.3A.1在原ViewportRoot→同STA Control/Renderer→CreateFactory/Create(ViewportOptions)→BindAsync(session,原root,完整options,ct)取得并强持的精确实例；OwnSession=false、同Control.Presentation和显式Lifetime是预绑定前置条件。Create只核对象/代次/budget，不创建第二session/不装配隐式backend。Assembly reference单向Wpf→Viewport Core/Wpf公开包，Halcon/Core不引用它。

Bridge.View即该Control。ShowFrame按entry精确FrameId/图像revision/hash与source identity/source revision/coordinate revision配对；不得猜SourceId字符串，entry缺射影/像素链拒该显示用途。Source整数像素中心约定，原图与参考图同revision可用Role Reference/Primary；相同SourceId不同revision不能同Context偷偷并存，须生产者独立SourceId或新context全替。Bridge在root预登记原Task后用Session.AttachAsync(ViewportContext)（第一次）或UpdateAsync(ViewportUpdate)提交原source/空或完整layers，返回Task为viewport原Task；void ShowFrame只表示入有界队列，状态/诊断等待原ViewportResult与PresentationCommitted，不说同步已经可见。继承原viewport授权purpose/AccessDomain、ResourceAdmission Required的生产规则；未知service/mask/坐标桥只拒对应呈现，Core无UI结果仍可保留。

精确context构造使用原类型：`SourceBinding(entry.Role,entry.Source,null,CorrelationId=本次OperationId编码,Timing=null)`（没有原采集时间事实则不补TimeBasis），初始`ViewportContext(Sources,Layers,原Authorization,Resources.Language,ApiVersion(0,1),ContextRevision=1,ViewState.Fit2D(实际CanvasDip,实际DpiX,DpiY))`；替换用`ViewportUpdate(BaseContextRevision=上次已成功receipt.ContextRevision,Replacement=完整新Context)`，ContextRevision checked递增，不用source/engine代次替它。所有ShowFrame/SetOverlay/Focus/Clear与SetResources按本binding单一有界队列串行投影；旧base/权限过期拒绝时保留原权威receipt和失败原因，新view不拿旧图当成功。Create在Created未Attach或与binding.Source精确相容时可用，接管一个已Attach异源context必须先拒，不静默覆盖别人呈现。语言刷新只UiBinding.SetResourcesAsync，不重Attach；原Authorization变化由Host先更新原ViewportSession合法context再恢复受限交互，业务工厂无伪授权。

SetOverlay把本Overlay的PixelPoint→SourcePoint2D(Column,Row)，source为原搜索图；ModelTransform仅原参考→原搜索中心变换，K/Ft/Fs已在backend做过，viewer不再补0.5、不用屏幕点回写结果。用原OverlayLayer/OverlayPayload(SourcePolyline/Label/RoiGeometry)及稳定LayerId/CandidateId/SourceRevision/CoordinateRevision/GeometryRevision，line两端为观测pA/pB，中点和参考连线只是view投影；未知DomainRef→RoiGeometry映射只省该层并列原因，不从bounds画假mask。原图保持可切回，无整平/候选图覆盖原FrameRef；选中候选表的CurrentItem通过§10.3A.2完整对象键选择调用改变指定候选高亮/详情，全部原候选数、MissingRequired、完整性仍显式可见。FocusCandidate在原candidate source坐标按其支撑/点生成有限SetViewCommand，保留原只读source与selected CandidateId，不发设备定位/质量采用。Clear封旧preview代后按§10.3A.2提交合法整图空Update；原borrow/return由原Viewport UI/session清理，void返回只表示已入队，不证明清屏或资源已归还。只撤本方overlay的操作仍用保留Sources的完整层替换，不冒整图Clear。

原图/候选对照默认同一原搜索图配overlay开关；参考/运行比较首片冻结为页签（原Viewport SourceRole Reference/Primary切换当前完整context），明确当前Frame revision，每页图像区≥55%客户区；不从Session多source能力推断已支持并排双画布。若后续确需同时并排，Host须用相同公开构造创建第二独立Viewport session/Control/Binding及自己的Root额度/关闭步骤，接收前不启用这一扩展，不用截屏当源。DevExpress DockLayoutManager紧凑分区、GridControl.CurrentItem联动、PropertyGrid typed草稿和SuperTip继续§10.2已读25.2.3成员；新增容器只用本机原公开控件，不换版/下载/检查许可。资源失败/英文长文案优先详情和自然换行，关键搜索/取消/查询始终可见；UIA Name/固定AutomationId/焦点/Tab保持§10.3，动态语言由host调用SetLanguage并将完整ViewportUiResources走UiBinding.SetResourcesAsync，权限撤销先禁止新操作，原native/viewport work继续由各Owner真实归还。

WorkbenchSession.Close只启动原Control.DetachAsync受管原Task并有限观察UI借用，不Dispose借用Runtime/Viewport session；重复Close观测同task。Detached表示事件/交互和视图引用已撤，尚未退出Dispatcher/presenter/显示lease仍须pending字段/根资源列明，不能以Detached当Drained。完整Host关闭依§5.1A计划：禁新→本页cancel→原Task/late lease接管→Control Detach→UiBinding.UnbindAsync→Viewport Session.DisposeAsync→Runtime Engine.Shutdown/Dispose→各桥/本Host拥有的Service归还→Dispatcher.Shutdown，先child后parent；彼此独立且每step own=true才关。Close/Observe不自动重Attach；原关闭任务未决时只能按原Root查询及受限未发清理步骤恢复，原Task不重建。恢复使用新UI binding须旧资源已确认归还后新BindingId/view generation；未知viewport/backend仍用原Root.GetSnapshot/Session.GetSnapshot/原Lease.QueryReturnAsync查询，不换实例绕账。关闭失败旧HostLifetime/Dispatcher/Runtime根仍强持，窗口可撤交互但不能提前Shutdown Dispatcher令归还丢失。

#### 10.3A.1 viewport 0.3.4-prep / WPF Assembly v0.2 的宿主预绑定

唯一上游权威为[viewport §10.6～10.9及兼容表§10.6.1](../viewport/DEVELOPMENT-GUIDE.md#106-公开bindingunbind与presenter借用)。本次只同步实际WPF宿主接线；AlignmentViewportBinding/AlignmentViewportBridge/IAlignmentViewerPort、Core v0.2.1及本模块Assembly v0.1公开签名保持。它们消费**实际Bind成功返回**的UiBinding，不实现或伪造上游binding；Core.ApiVersion(0,1)不是viewport WPF包版本。

宿主先预约两模块原root/HostLifetime和清理责任，在所属STA构造`new VPW.ViewportControl()`，再调用`VPW.ViewportRendererFactory.Create(control,vpRoot,new VPW.ViewportRendererOptions(明确BackendPolicy,ProfileNativeBytes,ProfileRasterBytes,ProfilePendingCount,有限CleanupBudget))`并检查Outcome/Value；使用**返回Value.Backend**填ViewportOptions.Backend、使用**Value.Lifetime**填Bind options.Lifetime，不能把ViewportRendererPorts record当Lifetime。生产只读显示选已批准HalconRequired/Required路线；离线Raster仅对上游允许的非生产用途显式选择，不因权限/容量失败自动降级。Host自有backend/lifetime可保持，但须同Control/root/Owner，`AcquirePresenterAsync(VPW.ViewportPresenterSubmission submission,VP.CallContext call,CancellationToken ct)`使用新版完整submission，保留Request、原Presentation及SourceCall；不保留旧PresenterLeaseRequest重载来绕过出处。既有ConfirmVisible/同Owner Revoke/Return沿上游签名，不新建authority或Root。

创建session**之前**将`ViewportOptions.Presentation=control.Presentation`，Host已有Presentation代理时Commit/Revoke直接返回该Control转发器的原Task，不用async/WaitAsync包装替换。Control.Presentation稳定且构造无资源；Bind前Commit明确拒绝且不Acquire。Factory/Create成功session即写原HostLifetime后，调用`control.BindAsync(session,vpRoot,new VPW.ViewportUiBindingOptions(BindingId,OwnSession:false,resources,UiCleanupBudget,Lifetime:rendererPorts.Lifetime,ExecutionBudget:显式ViewportUiExecutionBudget),ct)`并保存原Task及成功Value。BindingId稳定绑定同Control/session/root；Lifetime必须非null，缺失在Reserve/Dispatcher前007拒绝，冲突实例016拒绝。ExecutionBudget从宿主已冻结Profile取得正的MaxRetainedBytes/MaxWorkInnerTasks/MaxControlInnerTasks，计资源快照/呈现表/旧新代并存及上游显示观察预算（至少16×实际client W×H加其它已声明buffer/native），受root/session总额限制，不能把本页Core夹具额度当真实显示容量。null虽然有上游有限软件默认，也不作为本宿主真实负载的容量证据。Bind只安装空控件，不等Attach/Acquire；其成功后才构造本Alignment窄桥并按原ShowFrame链首次Attach，避免循环等待。

Resources使用`VPW.ViewportUiResourceCatalog.Get(LanguageSnapshot.CultureName)`的成功完整Value，或宿主自有同schema完整扩展快照；Revision必须`ViewportUiResourceCatalog.SchemaId`=`viewport-ui-text/1`，覆盖`RequiredKeys`及实际Overlay.LabelResourceKey等Host扩展键。保持上游每键/值/快照预算和占位符规则，不复制七键fixture或本模块资源替代完整Catalog。Get失败/缺键/错schema先拒对应UI接线；未知语言Get拒绝时可由宿主显式提供合法完整扩展语言，禁止隐式英语回退。SetLanguage后将完整快照通过同binding.SetResourcesAsync登记原Task，成功才更新桥已采用资源；缺键/超限/取消保持旧完整资源，不混语言、不重Attach/读取像素/修改业务修订。

HostLifetime强持原Bind/Attach/Update/SetResources/Unbind Task及原vpRoot/session/control/renderer。实际Commit/Revoke同原submission由viewport root/binding登记，`UiBinding.GetPresentations()`只取不可变观测用于关联BindingId、Presentation/SourceCall、OriginalCommit/Acquire/Confirm/Revoke/Return及PresenterIdentity/Cleanup；不取lease二次归还，不凭trace生成新sourceCall或新Commit。相同受信呈现重复得到同原Task，旧代/错ContextRevision/授权到期拒采用；属性赋值、Dispatcher完成或void viewer返回都不等VisibleConfirmed。采用只凭同binding/原submission的真实PresentationReceipt；上游HALCON/Raster显示与可见观察全由原renderer负责，Alignment不另做窗口绘制/抓屏/真值解释。

关闭继续原§5.1A/10.3A顺序：封新→本页Detach→从viewport任何slot worker**之外**发同binding.UnbindAsync(独立有限timeout,waitCancellation)→检查UiUnbindReceipt.Detached和Drained分别→仅Drained后关闭本Host拥有的viewport session，再关闭其原root/renderer拥有资源，最后Dispatcher/Window退出。OwnSession=false使Unbind不Dispose借用session或共享来源。超时/WaitCancelled/Detached而未Drained保原Unbind及所有trace原任务、PresenterIdentity/原returnId/cleanup两轴，由viewport原root收敛；Acquire晚到也由其extractLeases路径抓原lease，先同Owner Revoke确认CallbacksQuiesced/ReferencesDetached，再同原ReturnId归还/QueryReturn。Alignment不因handler未写字段就丢lease，不重发Acquire/Commit/Revoke/Return或重新Bind逃Unknown，不提前Destroy/Shutdown Dispatcher。观察可用原GetPresentations/root/session snapshot及原Owner有限QueryReturn；Unbind有限观察只结束等待，原Cleanup继续强持，原租约真正Returned才退账。恢复或新binding须原binding真实Drained；一个Host关闭不得Dispose另一Host的Control/session/renderer或共享Source服务。

窄兼容断言在既有未来Wpf.Smoke中定位，不新增工程/报告：`ALN.UI.VP02`依次检查Control先于session、同Control.Presentation/Renderer.Lifetime及完整schema、Lifetime=null前置拒绝、Bind空安装后Attach、原Commit重复Task恒等/完整submission、资源缺键保持旧快照、Acquire晚到和有限Unbind未Drained仍保原Task/lease、OwnSession=false及A/B隔离。这里只冻结定向断言，当前未执行WPF/native/可见观察/资源运行验收。

#### 10.3A.2 viewport 0.3.5-prep：稳定源、指定候选高亮与整图Clear

本节仅落实§10.3的SelectedCandidateId/CurrentItem、原FocusCandidate和Clear已有承诺；不改变AlignmentViewportBinding/Bridge或IAlignmentViewerPort签名，不重开§10.3A.1的Lifetime/Presentation/资源装配。公开调用权威：[viewport §15.2.2.1 CPU发布源](../viewport/DEVELOPMENT-GUIDE.md#15221-公开cpu发布源生产者与预装配bc-u1)、[§4.5.1稳定对象选择](../viewport/DEVELOPMENT-GUIDE.md#451-稳定对象id只读选择高亮与聚焦bc-u2)、[§4.7.1合法空更新](../viewport/DEVELOPMENT-GUIDE.md#471-合法空更新真实清屏与同session继续呈现bc-u3)。这是目标规格消费，当前没有新增API实现或运行证据。

**稳定显示源。** Alignment桥继续接Host预提供的精确SourceEntry/Control/UiBinding，不从Core byte[]或ModelArtifact生成viewport payload。实际Host选用内置renderer及已发布image-frame CPU level0时，在创建session之前调用`Asun.UI.Viewports.ImageFrame.ViewportImageFrameSourceFactory.Create(sourceService,vpRoot,new ViewportImageFrameSourceOptions(已登记ConsumerId,ProfileMaxBindings,ProfileMetadataBytes))`，核Succeeded/Value并强持返回IViewportImageFrameSource；`ViewportOptions.Frames=sourcePorts.Frames`永久使用该实例。Coordinates仅在本显示源同PixelSpace identity路线可赋sourcePorts.Coordinates；需要跨frame/标定链时保持原公开坐标Owner端口，不让本工厂伪造校准。Factory绑定的是实际service实例/ServiceEpoch、同vpRoot与ConsumerId，**不是某张FrameKey**，不能每次换图新Create再替换已冻结Options.Frames/Coordinates；未采用此工厂的既有合法源adapter保持，不强制新增源factory或源发布职责。

逐帧调用同步`sourcePorts.Register(new ViewportPublishedFrameBinding(bindingId,实际发布Owner取得的IF.FrameDescriptor,完整VP.ImageSourceDescriptor,ImmutableArray.Create(0),明确PixelSpace))`并核结果，成功后才首次Attach或后续完整Update。BindingId与Frame.Key、Image.SourceId/SourceRevision/CoordinateRevision/DecodeRevision分别保存；Alignment FrameRef.Id/Revision/hash/FrameDefinition与上述descriptor/source完整映射由Host已取得的来源证据核，不把工厂identity当逐帧键或从文件名猜身份。原Publish成功/Completed/Error=None/OperationResourcesReleased由发布Owner核实，Register成功不证明源真实存在。限定一个plane0、CPU level0、真实layout/域/metadata与原中心identity映射；多层/其它plane/异构/Planar/多allocation仅此工厂不支持时拒对应显示接线，不截断、量化或隐式全图解码。MaxBindings/metadata按Host原Profile预留并checked计费，原Read ValueTask一次AsTask登记到viewport root，失败Value/晚到lease归其extractor；Unknown保原epoch/request/lease，不另Read绕过。持续换图Register新revision→成功Update→旧work/lease真实退出/Returned且旧Context引用已解除→`sourcePorts.Remove(oldBindingId)`成功后才由源发布Owner决定Retire旧key；Remove不Dispose service或证明池退款，Rejected/Unknown保持条目占容量。源scope/CopyRow尚活跃时不得Remove/退账；A/B工厂实例、consumer、源键/lease互不混用。

**完整对象键高亮。** Bridge在每次已采用的完整overlay snapshot内维护有限私有索引`(Alignment OperationId,EngineGeneration,ViewGeneration,CandidateId)→VP.OverlayObjectRef`；容量计原MaxOverlayPoints/MaxRetainedUiBytes，索引值来自实际已提交可选几何，不加入Core结果/另造事实Owner。对象键完整六项：`SourceId,SourceRevision,CoordinateRevision,GeometryRevision,LayerId,ObjectId`。RoiGeometry对象用其真实ObjectId/Revision，SourcePolyline以其唯一LayerId同时作ObjectId；每候选自身可显示支撑/轮廓path独立LayerId，LayerId用CandidateId原字符串的无padding base64url编码加固定前缀`aln-candidate/`（先核UTF8/ID预算），不得用表行号/中心/ZOrder。同一A/B连线是组合投影，不将整条公共连线冒某一个candidate对象；Label或只有无法表达为原几何的点记录不制造假框，此时表中候选仍可选，viewport选择明确清除/报告无几何。只有Visible=true且Interactive=true的只读候选层登记可选键；Interactive只授Navigation选择，不授ROI编辑/模型采用。

完整layers更新成功后，以其原receipt.ContextRevision/Generation及当前view关联构造`new VP.OverlayObjectSelectionRequest(vpOperationId,expectedContextRevision,expectedGeneration,target,FocusIfAvailable:false)`，调用`Task<VP.ViewportResult<VP.ViewportReceipt>> originalSelect = binding.Session.ApplyAsync(new VP.SelectOverlayObjectCommand(request),ct)`。vpOperationId为本bridge一次生成并保留的原调用ID，串行记录至原Task观察/资源完成，完全相同请求重放只观察同Task；不拿Alignment业务OperationId跨多次不同选择复用。target按SelectedCandidateId精确索引；null/无可选几何用Target=null且FocusIfAvailable=false，清除高亮不移除普通overlay/源图/表选择。旧key/错源坐标几何/ContextRevision/Generation、隐藏或不可交互层拒绝，保持失败原因，不通过模拟中心点点击/任选第一候选完成高亮。核返回ObjectSelection.Target/ContextRevision/Generation及本次Presentation.VisibleConfirmed才声明影像高亮可见；属性/表选行/void SetOverlay返回或仅Focus结果不作该证明。

接纳选择会按viewport规则增显示Generation一次，ContextRevision不变；bridge保存原receipt输出代，后续Focus/Update/Clear从最新已确认同session snapshot/receipt取expected值，不沿用选择前旧代。事件只消费`ObjectSelectionChanged`及EventArgs.ObjectSelection，按原vpOperationId消回声、原六项键反查CandidateId和同view关联；Clear/撤权的Target=null通知仅清影像选择，不改Core歧义/候选结果或创建SelectionProposal。跨view/旧源晚到事件不选中新版本对象；原Task/lease归root收尾。FocusCandidate仍按既有候选支撑/点生成SetViewCommand导航，保持原只读source与选中candidate，不强制用新FocusIfAvailable=true或新增聚焦算法。

**保持session接纳的整图Clear。** `Clear(ViewGeneration)`进入同binding原有有界串行队列，封旧preview/view代并取得最新已接受baseContextRevision/currentAuthorization/currentLanguage/currentView；不与普通预览合并或丢弃。仅构造原`VP.ViewportContext(Array.Empty<VP.SourceBinding>(),Array.Empty<VP.OverlayLayer>(),currentAuthorization,currentLanguage,new VP.ApiVersion(0,1),checked(baseRevision+1),currentView with { Profile=null })`，立即登记`Task<VP.ViewportResult<VP.UpdateReceipt>> originalClear = binding.Session.UpdateAsync(new VP.ViewportUpdate(baseRevision,replacement),ct)`；不调用不存在的ClearAsync，不Unbind/Dispose后复活、不再次Attach。清屏处不发Select(null)代替整图清空，也不另发Revoke/Return与viewport重复析构。当前Read撤销时只使用session当前逐值相等的撤权Authorization/已接受Language/View（Profile清null）进入可信删除Control路线，不能趁空更新更换权限读新源。

成功必须核同原OperationId/new ContextRevision/Generation的`UpdateReceipt.EmptyTransition`：PreviousPresentationsRevoked、PreviousSourceBorrowsReturned、PreviousWorkQuiesced三项皆true，PreviousCleanup.State=Drained，且本UI路径BlankPresentation为**同新代空scene**真实VisibleConfirmed=true。旧呈现按原Owner Revoke→Submit/Acquire/Confirm/Dispatcher/CPU scope退出→同ReturnId源borrow归还；新空scene不Acquire旧源，只保原UI baseline/有限空Presenter，真实空画面由原renderer确认。State=Empty/空Sources/画面引用置null/void Clear/Window未显示不能代替上述回执；PreviousCleanup只证明旧内容scope，不关整session/renderer/source service或退原帧池容量，更不释放Engine.FrameLease。

观察取消/超时/EmptyTransition部分值或Unknown保原Clear Task、全部原旧代Revoke/Return/lease及错误/cleanup两轴；本bridge禁新非空ShowFrame/选择/Retry，不换binding/session/新Clear绕账。恢复仅有限观察原Task、`Session.GetSnapshot().EmptyTransition`和§10.3A.1原root/binding原记录，按同revision/generation核晚到结果；资源未归还继续pending，额度耗尽保持Unknown或由原宿主Close，不强杀/清目录。确认Cleared后下一ShowFrame对已Register的新源执行`UpdateAsync(new ViewportUpdate(空contextRevision,完整新Context且revision=空revision+1),ct)`，重新当前核权与预算，原空Presenter沿同Owner撤回；不再Attach/Bind。仅撤本方overlay时依原完整Update保原Sources，移除本方Layers/选择键，明确不报告整图Cleared。Clear与换图并发由session门决定，旧base005拒绝后只按最新snapshot发用户当前明确Clear，不能默默清后来新图。

定向规格反例归既有未来Wpf.Smoke：`ALN.UI.VP03`同中心A/B选择B核六项键、SourcePolyline.ObjectId=LayerId、无几何/null清除、旧代拒绝/事件消回声、同请求原Task且零模拟点击；`ALN.UI.VP04`空全量Update→三个Previous及同新代Blank确认→同session下一非空Update，Revoke/Return/Confirm闩锁或cancel保持禁新/原lease，禁止第二Attach/Unbind后复活；`ALN.UI.VP05`可选CPU源一次Create稳定Frames/Coordinates、两FrameKey逐条Register/换图/Remove条件、同key歧义/epoch变化/未知Read不替换Options。内容自审只核公开字段/有限异常/恢复及既有消费边界，不新增源发布功能、不重算Golden/三语/算法；运行断言均未执行。

上述Clear仅用于该session已经成功Attach的内容链；Created且尚无呈现时只撤待采用preview，保留“尚未载入”状态与一次合法首次Attach权，不用非法Update或InstallEmpty声称真实清屏。候选对象索引随原几何/层投影生成并一同冻结，只有原payload中已明确归属该CandidateId的路径才登记；无归属/多对象无法唯一对应则拒影像高亮，保表格选中，不按数组位置配对。组合连线与纯Label不进入候选索引。选择operation ID用`new VP.OperationId("aln-view-select/"+Guid.NewGuid().ToString("N"))`在首次入队时生成一次，保存至原Task/关联回执已观察完成；root另持未归还scope/lease，该字符串不是凭证。队列/索引/原Task/仍未归还的呈现引用及新旧资源并存合计使用原UiProfile和viewport/root额度，满时先拒新动作，Clear/原查询及归还使用既有保留控制槽，不重置每步预算。全部原Select/Clear Task先登记再有限观察，WaitAsync只用于观察不替换原Task。Clear原OperationId从viewport原回执/root登记关联取得，Update输入本身没有OperationId字段，不补造同名字段；原Task未给该回执时按已冻结base/newRevision和原登记查询，不能把另一Clear的EmptyTransition拼进本次结果。

### 10.4 UI 验收与容量

只在固定1920×1080验证三语、当前及目标DPI客户区、键盘/UIA、错误恢复/关闭/代次、主题与高级联动。验证英文最长caption/错误状态不会覆盖原图与按钮；PropertyGrid长路径/三语自然文案可换行或详情，不裁成无意义省略。样本文案：未找到A/未找到A/A not found；找到多个候选/找到多個候選/Multiple candidates；模型已变化，请重新选择/模型已變更，請重新選擇/Model changed. Select it again。三语资源覆盖所有title/命令/参数/units/status/validation/SuperTip/diagnostic/restore，不能只译toolbar。

viewer及证据刷新采用批量immutable快照，Progress按宿主UI Profile限频/合并，不每候选创建Dispatcher任务；grid仅绑定预算内候选，视图虚拟化/viewport帧传输能力须真实测，不靠开启属性声称流畅。Local field不转成百万行grid，显示摘要/选择点/受限raster；原图/field可见区域与租约有界。关闭/语言切换/连续选帧时旧UI回调全部检查三代次关联。UI Benchmark另测帧显示/选中联动/草稿验证/语言切换/关闭响应与UI高水位，真实阈值由host Profile冻结。此轮是指导修订，未运行WPF、截图、UIA或真实性能，视觉品质与功能可用分别验收。

## 11. 正常、边界和失败案例

| 场景 | 期望结果 |
|---|---|
| 两个非重合、足够基线特征，刚体位姿唯一 | Completed，返回两点对应、矩阵、残差；独立复核Unavailable不能伪造 |
| 只有一个无方向点且请求PointPairs | RequestRejected/DegenerateGeometry；OrientedSingle有方向资格是显式另一模式 |
| 两个相同圆互换身份 | `Ambiguous`，保留两个解释和消歧缺口，不输出 180° |
| 短基线或Affine近共线三点 | DegenerateGeometry；共线本身不使Rigid/Similarity退化 |
| 模型越搜索边界或支撑不足 | 候选可显示但用途不合格；不得补黑后当完整支持 |
| 无候选且搜索完整 | `NoCandidate`，才允许进入已批准备用 |
| 候选组合达到上限 | `EvidenceTruncated` 或 `ResourceExceeded`，不得称唯一最优 |
| native 忽略取消或迟到 | Query=WaitingForDrain/Isolated且Completion未完成；真实返回/归还后Cancelled，迟到结果只归原attempt |
| artifact交付宿主存储回执未知 | Alignment计算结果只陈述已生成artifact；宿主查询原资产回执，不标Alignment排空未知 |
| 局部注册把真实偏移变为零 | 输出注册残差和原始观察分离；模块不改写偏移事实 |

## 12. 测试和验收矩阵

实现切片必须为每个适用方法和两个消费者提供冻结输入、参数、预期状态和证据 hash。最小矩阵如下：

| 类别 | 必测断言 |
|---|---|
| 契约 | 缺字段、越界、NaN/Inf、frame/单位/版本不符在 native 前拒绝 |
| 坐标 | row/column 与 x/y、原点、方向、crop、非整数缩放、90°和镜像反例一致 |
| 候选 | 多候选完整性、原索引、top1 截断、不同方法分数不可直接比较 |
| 几何 | 刚体/相似算例、零基线、近共线、共线面积、角度周期、互换歧义 |
| 变体 | shape/NCC 原生输出分别核对；Planar/Local 缺字段不补造 |
| 资源 | 同模型互斥、两个实例隔离、帧/模型租约覆盖 native 全生命周期 |
| 取消 | 搜索前、搜索中、拟合中、复制中取消；终态、排空和迟到结果正确 |
| 超时 | 外层 deadline 与 native 返回分别验证，不把超时转 NoCandidate |
| 备用 | 仅完整 NoCandidate 可触发；总 deadline/累计预算不重置 |
| 持久/回退 | 模型 hash/revision、旧新组合、Unknown 查询和回退包可复现 |
| UI（如有） | 1920x1080、三语、窄内容、键盘焦点、关闭等待与错误恢复 |
| 消费者 | Consumer A/B 同一核心、不同参数和并发实例；一方失败不影响另一方 |

单元测试不能替代 HALCON/AsunImage 公开签名验证、Golden/Replay、真实 WPF 行为、HIL 或现场计量。测试报告必须区分软件行为、算法资格和生产验收。

### 12.1 纯 Core 的固定 BCL Exe 验证约定

唯一测试工程见附录A，`Microsoft.NET.Sdk`、TargetFramework=net10.0、OutputType=Exe、Nullable/ImplicitUsings=enable，仅ProjectReference本Core及.NET BCL；沿用 DEV-GOV-010 §3.1 冻结的 BCL Exe 执行约定，不另选测试包、不以dotnet test空执行当通过。模拟backend只返回脚本候选/字段/数学oracle，**不模拟真实模板检出率**；本模块Core负责契约/关联/门控/lifecycle，数学拟合由注入backend，不自行写平行视觉算法。FakeTimeProvider为测试工程内BCL TimeProvider实现，所有闩锁可控制释放；不能因无native就跳过租约ownership验证。

| 用例ID | 固定输入/步骤 | 必须断言（未来执行，当前未执行） |
|---|---|---|
| ALN.C01 | 非预留/重复/旧代ID、NaN、空slot、route与模型不符、错单位、default集合 | RequestRejected；0后端调用/0租约；预留slot消费/释放行为一致，旧ID不再接纳 |
| ALN.C02 | §4.7 q/p刚体oracle；长度差反例；PointPairs单点；OrientedSingle无方向资格 | +π/2/t(10,20)；LS残差1/1、Anchor残差0/2、Similarity尺度1.02分别留证；无方向不猜旋转 |
| ALN.C03 | A/B互换；TopK1；A×B组合预算1；coarse无候选但Fine有候选 | 两解释Ambiguous；TopK不得Qualified唯一；组合截断无唯一Pose；预配置补搜原批准域，未补搜不是原图NoCandidate |
| ALN.C04 | 模型hash/revision错；NCC不同k训练/搜索；domain重心≠origin；非整数缩放链 | native前拒不相容；§4.7.2精确值/逆映与axis/半像素桥一致；ReduceDomain不平移 |
| ALN.C05 | Backend闩锁阻住搜索→token取消/假时钟deadline→Query/Shutdown有限等待→放闩锁 | Completion不先完成；lease未释放；Pending；放锁后一次terminal且ResourcesReleased早于Completion；先锁存stop原因不被迟到成功覆盖 |
| ALN.C06 | A阻住取消，B独立正常；同实例MaxActive/queue压力；第二租约Acquire异常 | B结果不变；queue满拒新接纳；已取部分lease释放；无无限Task/无跨engine状态，所有await尾项可枚举 |
| ALN.C07 | 复制抛错、frame/model/ROI DisposeAsync故障、通知满/订阅者抛错 | 有界证据且BackendFailure；释放未确认则Isolated，禁止假ResourcesReleased；通知不阻塞计算，无重复terminal |
| ALN.C08 | BeginTrain/Inspect/Export脚本artifact：hash错/字段错/取消/部分字节；旧模型仍运行 | 失败artifact=null；新旧revision不混，旧引用不热变；readback NotQueryable无manifest拒，Core无发布副作用 |
| ALN.C09 | Local脚本1×N/NaN/错field长度/未知GridBinding；Planar9×N错长；projective跨w=0 | 错字段失败；RawRasterOnly不签模板/逆用途；禁止补angle/H；全域证据失败拒用途，矩阵倍数门一致 |
| ALN.C10 | Replay新generation+parent；终态Release/重复Release；Shutdown后Begin；重放旧ID | 同冻结技术输入得到等价值；旧代不能写新operation；释放Busy/Released/NotRetained正确，EngineClosing拒准入 |
| ALN.C11 | BenchmarkProfile缺目标、失败/timeout/未drain样本；候选字节/field数组checked溢出 | 性能NotEvaluated，失败/删失分项且未drain不判通过；溢出ResourceExhausted或准入拒绝，不尝试分配 |
| ALN.C12 | CandidatesOnly/GlobalPose、必需/可选slot、diag候选支撑Unknown | 候选查询不强制拟合；GlobalPose缺必需点Pose=null；未知支撑不Qualified；所有状态/错误组合符合§7 |
| ALN.C13 | Recommend有序候选2项：同样本/真值/负载、0失败/删失且drain、均过错率门；P95=2/1 ms；再删一项P95或改变Profile hash | 完整证据选第二项；缺证据为InsufficientEvidence、修订变化旧proposal过期；不调用native/不更改生产模型。该ms为排名合成例，不是性能验收值 |

测试每例逻辑deadline≤10s，套件≤120s；外层进程上限180s是**测试悬挂检测**而非产品性能门。assert失败、未完成或必需项skip返回非零并列用例ID，全部适用项执行通过才0。闩锁finally解除且观察所有在途Task；模拟永不返回分支由harness隔离子进程验证Pending，外层终止仅测试子进程，不当产品native drain。下面命令在“仓库根”执行，绑定未来工程；当前工程尚未创建，此轮不执行：

```powershell
dotnet build src/Modules/alignment-2d/Asun.Modules.Alignment2D.Core/Asun.Modules.Alignment2D.Core.csproj -c Release --no-incremental
dotnet run --project tests/Modules/alignment-2d/Asun.Modules.Alignment2D.Core.Tests/Asun.Modules.Alignment2D.Core.Tests.csproj -c Release
```

执行器必须为每条命令设置180s外层进程上限并检查exit code；build也不得无限等待，dotnet run非零不得只取最后输出当通过。非UI纯值测试不需HALCON/WPF安装检查；真实adapterGolden、同样本路线比较、读写/停止、UI、耐久/客户现场另用对应工程和Profile，不能在上述Exe中skip后声称整模块通过。

### 12.2 H2/H3/W1 定向验收断言（规格，未运行）

这些断言只补本次退修对应的未来验收，不重审C1–C3；脚本证据可验证Alignment消费门，逐角数值算法必须由几何Owner真实实现/Golden验证，H3 native提取和W1运行仍分别归adapter/WPF工程。

| 用例ID/消费者 | 冻结反例输入 | 必须断言（未来执行，当前未执行） |
|---|---|---|
| ALN.H2.D01 几何Owner/Alignment | identity域映射，run=(0,0,0)，H前两行为identity、末行=(1,0,0.25) | 中心w=0.25但闭像素支撑w∈[-0.25,0.75]；ContainsZero、MinAbs=0、Rejected，不能按中心通过 |
| ALN.H2.D02 几何Owner/Alignment | identity域映射，同一行两run=(0,0,0)/(0,4,4)，H末行=(1,0,-2)，ratio门0.5 | 两片w分别[-2.5,-1.5]/[1.5,2.5]，min/max=1.5/2.5，分母门通过；孔洞不补域、正负片可共存。只通过分母门不自动Qualified全部几何 |
| ALN.H2.D03 Alignment消费/ROI适配 | D02漏第二run、重复RunIndex、旧H/DomainRef/hash/映射/threshold；复制后端口取消/预算截断 | 不以计数相等判完整；逐run/引用绑定错拒用途；ROI适配不能核hash则Acquire失败；中止Complete=false、聚合null、无WholeDomain，lease覆盖真实返回 |
| ALN.H2.D04 几何Owner/Alignment | run=(0,0,0)，H末行=(2.25,0,1.375)，threshold为Binary64 0.1；再换精确倍数-2H | w=[0.25,2.5]、精确ratio=1/10，Binary64 0.1略大于1/10，精确门拒绝；显示同为0.1不改决定，-2H同一比率与拒识。精确相等门值须通过 |
| ALN.H3.P01 native适配/结果消费 | 原生位宽Unreported；另一例32位但复制到double；backend/adapter证据错代 | Unreported+NotReported仅RawRasterOnly；32→64保留原32来源，不宣称精度提高；缺精度字段/已知位宽缺绑定/错代拒Field用途 |
| ALN.H3.P02 native适配/结果消费 | get_grayval返回native domain外有限值、非对称row/column、源域缺邻点、NaN/错tuple长度 | 域外读值不变有效点；顺序/长度按adapter Golden；缺源/插值支撑Valid=false；非有限/错长度不发布Field，Partial且拒用途，不补0 |
| ALN.W1.O01 WPF/宿主 | 同OfferId同内容重复；同ID换artifact；观察timeout/Pending；页面换代/Detach后Accepted迟到 | 同offer只一次持久化，不因观察结束重发；同ID换内容拒；host保管尾项并按原OfferId/source generation归档，旧回执不进入新视图、不改Alignment终态/发布事实 |

H2四项里的解析数值是数学反例，H3/W1是行为断言；它们没有产品执行结果、性能目标或生产通过结论。真实coordinate/ROI/资产Owner接线须按相应边界接收，不把本页端口规格写成其它模块已经实现的能力。

### 12.3 后续装配断言（规格，未运行）

| 用例ID | 反例/步骤 | 必须断言 |
|---|---|---|
| ALN.ASSEMBLY.01 | Factory前不Reserve/不设CleanupPlan；重复HostId/未知HostId；Session/Bridge Create失败后仍有迟到factory/port Task | 无IO/native/Dispatcher副作用；失败不交半对象；原Task、输入和迟到资源仍在HostLifetime，可由同一plan收尾，不由GC/窗口退出代替 |
| ALN.ASSEMBLY.02 | A/B分别登记四个A/B精确模型，模型包digest与raw文件hash不同；缺Descriptor、闭包、source hash或多入口layout | 只交付完整精确单入口ContentLease；缺失项拒对应entry，不能以文件名/包digest/部分native读回补字段或拍平多文件包 |
| ALN.ASSEMBLY.03 | Frame Read窗口不足、domain mask/hash规则未知、Slice迟到；B关闭而A仍持源/共享Service | 预算在Read前拒绝；规则未知不交PixelPlane；迟到slice归原Owner并单次Release；B关闭不Retire/Dispose A或共享Service |
| ALN.ASSEMBLY.04 | ProductionInspect提交Train/Export/Recommend；Engineering取消训练后旧模型运行；Runtime无GeometryEvidence运行Projective Qualified | 模式门在接纳前拒绝；旧revision继续可读；H2仅诊断或NotEvaluated，不能由模式绕过用途资格 |
| ALN.ASSEMBLY.05 | 两STA切换语言、候选筛选、迟到Overlay/Presentation；Window.Closing取消等待到期 | 各自Dispatcher/root/generation隔离；原始候选分母不被视图裁剪；旧代不更新当前viewer；有限等待返回Pending/DrainUnknown并保留原Task，不强杀线程 |

这些是装配和消费边界的未来断言，当前没有工程、模拟器运行或WPF/HALCON结果；不把断言ID计为已执行测试。

## 13. 性能、容量和可观测性

### 13.1 预算基线

每个消费者必须提供不可变 `BenchmarkProfile`，冻结 Core/adapter/HALCON/AsunImage、模型及算法 revision/hash、OS/CPU/GPU/运行时、图像尺寸/像素格式/有效域、模型点数、ROI/子模板/特征 slot 数、角度/尺度范围、候选上限、并发、队列和冷/热状态。Profile 在运行前明确预热次数、测量次数、最低有效样本数、有限总 deadline、候选/组合/证据/native 模型/托管内存上限、固定吞吐窗口、分阶段测点及阈值来源。冷模型装载/训练、热搜索、变形模型、大图和多子模板分别成桶；热态按固定次数预热且排除预热样本，冷启动单独测量。本文不设置单 ROI 毫秒或单操作内存验收值；无批准目标则为 `TargetPending`，资源超限仍按请求预算返回 ResourceExceeded。

以单调时钟测排队、预处理、模型装载/训练、find、候选收集、对应、拟合、结果复制/保存、端到端至 `ResourcesReleased`，并测取消到 native 停止/排空。分别记录候选、组合、证据字节、模型驻留、native/managed 峰值、分配、队列深度/高水位、固定窗口吞吐、阶段耗时和输出完整性；native 暂态无法观测时写 `Unknown`，不得当作 0。通用分位、样本有效性、失败/删失和未排空规则按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)。本模块另分项报告无候选、歧义、证据截断和资源拒绝。验收阈值只可来自已采纳的消费者/客户 Profile（含机器、输入和质量门）；缺少阈值标 `TargetPending`。

### 13.2 结构化观测

每个 operation 记录 `operationId`、attempt、模块/适配器版本、方法、模型 hash、输入修订、状态转换、候选数、对应数、残差摘要、支持比例、预算使用、取消/超时时间、native 返回码和排空完成时间。日志不得写入完整图像或敏感产品资料，除非宿主明确授予证据保存权限。指标和 UI 是只读投影，不改变结果。

## 14. 发布、迁移和回退

发布包至少包含模块二进制、公共契约版本、适配器版本、依赖版本清单、能力矩阵、模型闭包规则、Golden/Replay 结果摘要、性能预算版本和回退包。发布前必须完成：

1. 两消费者无 UI 接入和并发隔离验收。
2. 公开 HALCON/AsunImage 签名及关键算子反例核对。
3. 取消、超时、排空、资源归还和迟到结果验收。
4. 版本组合读写、模型 hash、配置修订和回退演练。

回退时保持原 operation、模型和结果可读；不得把新模块结果覆盖旧生产事实。模型更新、坐标修订、训练输入、方法或默认参数变化均产生新 revision；已运行 attempt 不热换模型。未知回执必须查询原 operation，不能用重新搜索替代原回执。

## 15. 开发顺序和准入门

本轮只修订指导。主控于2026-10-10已逐项接收ALN-C1/C2/C3的DEV-GOV-010 §3.1六项文档规格，三片同步为`ModuleCoreImplementationReady`，仅表示规格准备；未创建/编译工程、未运行BCL验收。本次不重审已接收规格，不启动实现。整体仍为DesignReview；完整批准范围内部软件设计结论见§17.4，新增生产者/资产接线见§5.1C；ALN-H1/H2/H3/W1/I1均为`PreparationIncomplete`，不得由三片Core接收推出真实适配/UI/生产准入。平台映射/物理验收值不阻断无产品事实的Core规格；核心内部欠字段/算法/接口不得冒作客户外部门。

| 切片 | 明确交付与步骤位置 | 六项文档条件定位（DEV-GOV-010 §3.1 顺序） | 当前规格状态与剩余门 |
|---|---|---|---|
| ALN-C1 契约/验证/账本/executor | §3、5–7，含Train/Inspect/Export/fit端口、接纳/排空/关闭 | ①§1–2；②§3/5–8；③§9；④§11/12.1 C01,C05–08,C10–12；⑤§13；⑥附录A | ModuleCoreImplementationReady（2026-10-10主控已接收六项规格）；后续需授权实现、创建/构建/BCL Exe运行，尚未执行。真实native/WPF不是此纯Core门 |
| ALN-C2 候选关联/粗精/备用/门控 | §4.1–4.10/4.14，注入脚本搜索/拟合/几何证据，不自写视觉匹配 | ①§1；②§3/4/5；③§9.1；④C02–04,C09,C12；⑤§13；⑥附录A | ModuleCoreImplementationReady（2026-10-10主控已接收六项规格）；BCL断言后续只证编排/数学链，不证真实HALCON正确率 |
| ALN-C3 工程训练/推荐/Replay闭包 | §3.7/4.9/4.14，独立候选artifact/参数建议，host资产交接 | ①§1–2；②§3/4.9/5；③§9；④C04,C08,C10,C13；⑤§13；⑥附录A | ModuleCoreImplementationReady（2026-10-10主控已接收六项规格）；后续验证BeginRecommend有限纯值排名及评估证据复现；真实训练/资产提交仍需外部适配接线 |
| ALN-H1 Generic/NCC/传统Shape/XLD | §4.7/4.9/4.11完整adapter训练读回/搜索/导出/关闭；§5.1A公开装配 | ①②均本页；③无UI host；④adapterGolden/ALN.ASSEMBLY按§12；⑤§13；⑥附录A adapter | PreparationIncomplete；Assembly Contract v0.1限定内容已由主控接收；真实C#重载/封送歧义绑定、原点/半像素/粗精/范围/score/遮挡Golden、cancel/drain/临时文件仍未关闭；已确定cv2算子不再availability audit |
| ALN-H2 Affine/Projective/Planar | §4.12/4.14，严格区分搜索与点拟合、全域证据端口 | 同六项位置；显式域映射§3.6、输入/返回证据§4.14、资格§4.12；定向断言§12.2 | PreparationIncomplete；实际fit与native矩阵Golden、几何Owner实现ExactBinary64DyadicV1及适用全域界并真实接线、真实平面/范围/独立点Profile；不以det非零/四点零残差授资格 |
| ALN-H3 Local诊断 | §3.7/4.13，raw field/rectified/contours与预算，不输出未经证明的逆 | 六项位置齐；精度必填闭包§3.7、raw诊断与templatebinding分开；定向断言§12.2 | PreparationIncomplete；native字段/索引/场精度来源/有效域/复制/expand Golden；GridBinding资格另门。逆/毫米消费者不在本切片承诺 |
| ALN-W1 可选工作台 | §10完整view契约/任务/三语/permissions/generation/close；§10.3A公开STA/Viewport装配 | ①§1；②§3/10；③无UICore独立；④§10.4/12.2/12.3；⑤UIProfile；⑥附录A Wpf | PreparationIncomplete；Assembly Contract v0.1限定内容已由主控接收；按已冻结CurrentItem/CellValueChanged/typed草稿与唯一ArtifactOffer签名编译；真实1920×1080 WPF/UIA/三语/视觉品质/性能/关闭仍未关闭；不计无UICore已运行 |
| ALN-I1 真实两个消费者/资产/用途集成 | §5.1C、9、14、17.4；不修改产品事实权限 | 本页模块侧+宿主正式映射/Owner | PreparationIncomplete；宿主frame/ROI/坐标/资产/geometry/Viewer能力接收；两个真实消费者/客户Profile/Replay/耐久/现场，按适用边界验 |

主控接收C1–C3已完成；本轮新增H1/HALCON装配、ModelAssets/ImageFrame消费桥、W1/WPF/Viewport装配已限定内容接收，未提升切片状态。后续顺序为另行授权明确切片实现和BCL/装配验证→逐route适配→真实两个消费者→可选工作台→同样本Golden/性能/耐久/现场。不是规格接收就宣称整模块完善。真实设备HIL仅对宿主发生设备/触发副作用的集成适用；本模块无设备操作，不能造HIL数据证明定位。客户物理精度/误定位/吞吐门来源缺失准确记录TargetPending，内部UI/几何接口缺项仍归对应技术Owner。

## 16. 来源与自审边界

- [PKG-022_Matching](../../shared-modules/packages/PKG-022_Matching.md)：历史包映射/研究入口，独立模块职责和实现以本页为唯一权威。
- [DEV-VIS-023](../../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md)：复用已有匹配/几何/局部场反例与研究；本模块实际步骤已采纳于§3–4，不构成第二份活动API/方法权威。
- [DEV-VIS-020](../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision%20Contract与AsunImage边界开发指导.md)：Vision Contract 与 `ImageLibDotNet` 边界。
- [PKG-007_Coordinates](../../shared-modules/packages/PKG-007_Coordinates.md)：坐标、单位、矩阵方向和半像素边界。
- [INDEPENDENT-MODULE-ARCHITECTURE](../INDEPENDENT-MODULE-ARCHITECTURE.md)：独立模块准入、端口、消费者和指导章节要求。
- HALCON 本地算子手册：`halcon算子手册/operators/`，目标版本 26.05；实现前逐算子核对。
- [DZ-XVision 快照说明](../../references/project-snapshots/DZ-XVision/20261004/README.md)及其只读源码：仅用于本节的 Mark/模板/失败恢复场景观察；快照声明原项目为 .NET Framework 4.7.2 + AsunImage 24.11，不得当作 .NET 10/HALCON 26.05 公共接口证据。
- `../../references/project-snapshots/AsunControl/20261004/original/Vision_Aligment2D_ShapeModel`、`...NCCModel`、`...DeformableModel`：只读同类资料。其旧 `ShapeModelEngine`、`DeformableModelEngine`、事件和 `CancellationToken` 形态可作为迁移观察，不能直接作为本模块契约。

### 16.1 本轮复用的实际源码/测试与官方依据

HALCON语义权威为本地26.05.0.0页面；本轮实读create/train/set/get Generic、NCC create/find/get/origin、affine_trans_image_size/affine_trans_pixel/vector_angle_to_rigid、vector_to_rigid/similarity/hom_mat2d/proj_hom_mat2d、scaled/aniso与deformable create/find/get/set及crop/zoom说明。线上[affine_trans_image_size 26.05](https://www.mvtec.com/doc/halcon/2605/en/affine_trans_image_size.html)响应200并确认相同版本/corner语义；不是实际算子运行。补充本地入口：[affine_trans_image_size](../../../halcon算子手册/operators/affine_trans_image_size.html)、[affine_trans_pixel](../../../halcon算子手册/operators/affine_trans_pixel.html)、[vector_angle_to_rigid](../../../halcon算子手册/operators/vector_angle_to_rigid.html)、[get_shape_model_params](../../../halcon算子手册/operators/get_shape_model_params.html)、[vector_to_hom_mat2d](../../../halcon算子手册/operators/vector_to_hom_mat2d.html)、[vector_to_proj_hom_mat2d](../../../halcon算子手册/operators/vector_to_proj_hom_mat2d.html)。全部经cv2，不另接官方C#类。

| 固定来源与实读范围 | 可迁移结论 / 不采用及边界 |
|---|---|
| [OpenPnP commit 5bd404cfc70f34103a3ca0fbb6b50c2b465f407c](https://github.com/openpnp/openpnp/tree/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c)：Utils2D.java 572–739双点/多点源码、ReferenceFiducialLocatorTest.java全文，已有[来源/hash/源码测试](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#matching-research)复用 | 双点比例scale与刚体不同、多点短列表截断危险；test主要1/2/3数量/共线退两点，不能证明身份/精度。GPLv3，Java/OpenCV/Guava/Swing/JNA/相机全局Configuration生态，仅借鉴反例/测试思想，不复制或引入运行依赖 |
| [OpenCV commit a0cda081f8d769f40ab2f4904738b4787b44d07c](https://github.com/opencv/opencv/tree/a0cda081f8d769f40ab2f4904738b4787b44d07c)：templmatch.cpp 870–910，test_templmatch.cpp 145–230，固定原件见同REF-002 | 常量TM_CCOEFF_NORMED源码与oracle都返回全1，参考一致不等工业纹理可观察。Apache-2.0及C++/CMake/OpenCV测试依赖沿已读来源；只借鉴退化拒识，不推断HALCON相同输出，不引入OpenCV |
| [DevExpress布局示例 commit bf801b30a0e7cdf6c1e54a708ec324087b758b4a](https://github.com/DevExpress-Examples/wpf-dock-layout-manager-upgrade-layouts-between-versions/tree/bf801b30a0e7cdf6c1e54a708ec324087b758b4a)，[MainWindow.xaml及code-behind/csproj](../../references/open-source/DevExpress_layout_upgrade/bf801b30a0e7cdf6c1e54a708ec324087b758b4a/CS/) | 稳定Name/LayoutVersion/Workspace与升级只改布局可借鉴；示例net472/DX24.2，不导入其依赖。官方示例as-is/EULA条款沿已保存研究，不视为MIT；未见相应行为测试，不证明25.2.3运行 |
| [SuperTip官方历史示例 commit 0c534a44e832d2e3af6bbf9defb82ab23e28e7b4](https://github.com/DevExpress-Examples/how-to-create-supertips-for-bar-items-ribbon-items-and-standard-controls-in-code-and-xaml-e2702/tree/0c534a44e832d2e3af6bbf9defb82ab23e28e7b4)，标准控件XAML/code全文；[040公开能力来源](../../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress%20Design%20System开发指导.md#localization-public-surface-method) | SuperTipControl承载到标准ToolTip，25.2.3公开构造/属性复用既有签名记录；旧net6/22.2例不迁依赖、不证明动态三语/关闭实测。许可as-is/EULA指向，未见行为测试 |

DevExpress官方Dock/Grid/SuperTip/PropertyGrid网页本轮403，环境无dxdocs工具；实际读取`C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/DevExpress.Xpf.Docking.v25.2.xml`、Grid.v25.2.xml、PropertyGrid.v25.2.xml的§10列出成员，SuperTip复用既有25.2.3公开记录。来源版本/commit/hash元信息均沿现有REF-002及原件，不新建快照/报告，不重复全库研究。源码/测试为静态实读，未编译/运行上游、不宣称算法/控件验证通过。

## 17. 已冻结选择与剩余门

已冻结：Core像素中心/Cartesian换基、Generic首选及NCC固定尺度、A/B分别建模、显式训练/搜索缩放链、候选保全与有限关联、默认LS与显式Anchor、所有架构route的输入步骤/输出/拒识、无自动生产训练、after-drain唯一终态、无共享native缓存、有限UI投影。它们是本模块技术责任，不再等待客户替程序员作决定。

ALN-C1/C2/C3六项规格已于2026-10-10获主控接收，仅三片为ModuleCoreImplementationReady，实际实现/构建/BCL验收均未执行。2026-10-11 Assembly Contract v0.1 §5.1A/B、§9.2、§10.3A及ALN.ASSEMBLY.01–05已获主控限定内容接收；这不改变H1/H2/H3/W1/I1的PreparationIncomplete/NotReady、真实来源/适配接线、HALCON/native/WPF/Golden/性能/物理/运行资格门。真实待关闭项按§15逐切片：对应adapter真实C#重载/封送与测试；coordinate/ROI全域几何证据实现接线；WPF选中/事件、Viewport呈现确认及ArtifactOffer挂接和真实UI；独立样本/两个真实消费者/BenchmarkProfile/耐久。物理验收值只影响相应用途：客户精度、误接受/误拒绝、遮挡范围、物理标定链、吞吐/资源目标。未给目标时可做诊断测量但NotEvaluated，不能凭合成例赋值或让其阻断无关Core。

产品/资产Owner仍负责序列化映射、模型封存/发布/保留/回执、质量采用、目标关联和设备流程；没有mapping不做产品集成，但Core不依赖其私有数据库。局部场逆/毫米用途是明确未提供能力，不以低残差/渲染图暗示已通过。原模型或产物hash无法核实则拒绝相应调用，不以重新搜索覆盖未知。

### 17.1 两轮内容自审（2026-10-09）

第一轮按算法与能力场景反例：非整数缩放只除比例会差1.5px；训练/搜索k不同漏训练链会改变物理尺度；A/B长度差下Anchor与LS残差不一样；固定角extent=0不能当全圈；单个有资格方向模型能定刚体但单圆不能；两点共线不使刚体退化；TopK/粗层漏检不能证唯一/原图未检出；projective det非零但w穿零；Local绝对场不是负位移逆。已在§3–4、§11–12同步对应字段/步骤/断言，清除Generic不存在的restrict_angle参数写法，使用真实angle_start/end与restrict_iso_scale参数。

第二轮按并发、生命周期、消费者与操作员场景：取消后native仍跑、lease归还抛错、事件队列满/订阅者重入、重复/旧代ID、页面切换迟到、host存储迟到、观察超时后Dispose阻塞、A关闭污染B。已在§5–10统一：等待排空不是终态Unknown；任何归还未确认保持Isolated；payload与账本保留受bytes+槽双预算；UI只取消自己的operation等待并交host保管，不Dispose共享engine；资产回执不冒Alignment终态。示例/状态表/错误表/附录同版，不用旧result.DrainCompletion。

以上两轮为2026-10-09本Owner历史内容走查，当时各片PreparationIncomplete等待主控接收；没有派生代理/会话，来源研究静态阅读与数学反例不冒运行通过。当时仅修改本文件，未创建代码/测试工程、未执行HALCON、WPF、BCL产品测试、Golden、性能、HIL或现场验收。当前接收状态见§15与§17.2/17.3，不覆盖原检查日期或冒充运行验收。

本文件定向检查已执行：本地Markdown链接目标存在、代码围栏成对、标题不重复、旧终态后排空示例/旧v0.1附录/发布越权措辞已移除；以精确有理数复算缩放/逆映/1.5px反例与aniso原点算例一致。它只验证本指导结构和所列数学命题，不替代C#编译或真实算法/UI验证。

### 17.2 两轮定向反例自审（2026-10-10）

第一轮只查H2证据闭包与反例：中心安全但闭像素支撑穿零；孔洞/不同组件符号；漏run与重复run；旧H、域、映射和阈值；显示规范化舍入；1/10与Binary64 0.1阈值边界；取消/预算截断。修正了lease未公开hash却要求读取、域映射没有公开来源、跨零时最小绝对值未明确为0三处缺口。当前§3.6/4.12/4.14/5/12.2统一：请求显式映射、ROI适配核引用内容、完整Runs闭像素支撑、原矩阵精确dyadic乘加、逐run绑定和精确交叉乘积；相应真实几何实现/接线仍属H2门。

第二轮只查H3/W1与状态：未知原生位宽不因double复制变已知；get_grayval忽略domain不能形成假Valid；非有限Field不能违反公共有限值规则；Offer观察超时/Pending/迟到/页面换代与关闭不得重发；同OfferId换产物必须拒；规格Ready不能冒实现Ready。当前§3.7/4.13/9/10/12.2/15/附录A统一场精度闭包和唯一ArtifactOffer签名；所有迟到尾项归host，回执不改Alignment终态或发布事实；C1–C3仅同步主控六项规格接收，其他五片保留PreparationIncomplete。

两轮为本Owner定向内容自审，无新建/fork/派生会话；本次仅修改本指导，复用既有官方资料与来源，不改共享文件、产品代码或参考原件。定向文档校验检查本文件正文/API/示例/六项表/版本/引用及Markdown结构，并以内存精确有理数复算§12.2分母反例；不替代产品构建、BCL验收、HALCON、WPF、Golden、性能、HIL或现场验证，以上运行均未执行。

### 17.3 2026-10-11 装配增量两轮有界自审

第一轮按Factory→Root→HostLifetime→Service/Frame/Viewport桥→Runtime/Workbench→双Mark搜索→结果深副本→Close的正常、拒绝、迟到和恢复路径检查：补齐了根预约先于所有Factory、Mode隔离Train/Inspect、ModelAssets包digest与raw文件hash分离、ImageFrame原始行读取规则、Viewport不冒同步可见、独立STA和A/B共享资源隔离。不能无损映射的多文件模型、未知mask/hash/descriptor、非驻留Tile/Float64或缺GeometryEvidence均改为对应桥拒绝/NotEvaluated。

第二轮专查异常和生命周期：原ValueTask只转Task一次、factory/Begin/Acquire/Read/Bind/Dispatcher晚到结果强持、Close不等待自身、观察超时不清root槽、Child失败不越过父依赖、B关闭不污染A、旧ViewGeneration不覆盖新视图、语言/权限变化不改Core事实。补入有限Cleanup DAG、原Owner Release/Query、STA Shutdown顺序、ALN.ASSEMBLY.01–05未来断言和“限定内容已由主控接收、真实资格仍未关闭”状态。该增量只修改本指导，未创建工程/产品代码/测试/报告，未扫描封装或重研究已定算法。 本文件定向检查已执行：本地链接目标存在、围栏/标题一致、单一ArtifactOffer及各新增公开声明、精确注入参数数量、Core/Assembly版本与三片Ready/五片PreparationIncomplete同步；既定双Mark缩放/刚体/相似、全域分母/拓扑反例文本保持。仅为文档结构/契约走查，未编译C#、未运行HALCON/WPF/Golden/性能/物理/现场验收。

### 17.4 2026-10-11 完整批准范围增量结论

本轮以IM-026架构范围及本页§1的全部能力族作结论，复用§17.1–17.3的已接收研究/算法/Core/Assembly内容及固定向量，不再次全面审核或复算。实际欠账为工程产物的生产者来源/metadata/封存/读回/Unknown恢复、MA 0.3.1-prep兼容接线，已在§5.1C收口；未写产品代码、修改其它模块或新建会话/报告。**当前完整批准范围内可决定的软件设计欠账已闭合**；该结论是指导内容准备结论，不表示整模块ImplementationSpecificationReady或真实运行/生产验收通过，逐切片状态继续见§15。

| 完整能力/真实消费者 | 已冻结实施位置与完整链 | 尚未执行的资格/Owner |
|---|---|---|
| 图像/XLD Generic、Scaled、Aniso、NCC模板创建/查找/读回/导出，缩小训练与小ROI搜索 | §3.5–3.7、4.9/4.11、5.1A/B；Requested/Resolved、原点/完整来源、模型hash、支撑、精确训练与运行变换链，无生产隐式训练 | alignment-2d H1 Owner：实际C#公共重载/参数封送、真实模型/非对称/角域/缩放/原点Golden、失败/取消/native/临时文件资源验证；不安排依赖安装/授权检查 |
| A/B独立Fine/Coarse子模板、单/双/多Mark，中心/连线角/平移/刚体/相似 | §4.7/4.10、9/9.2；完整域/种子/直接Fine闭包、LS和Anchor区别、候选互换/一对一、退化/尺度/镜像/歧义/截断明确拒识 | alignment-2d算法/消费者Owner：独立真实样本与负例正确率/用途Profile、性能/负载；既有数学固定向量仅作为软件oracle，不代替真实精度 |
| Affine/Projective/Planar及全域证据 | §4.12/4.14；拟合与搜索分开、显式域/单位/中心换基、ExactBinary64DyadicV1逐run分母、独立验证、反射/Jacobian/条件门 | alignment-2d H2 Owner：真实fit/native Golden及消费接线；coordinate-geometry Owner：全域证据实现/Golden及适用数值界；消费者Owner：真实批准域/平面/holdout/物理门。缺一项只阻相应Qualified用途 |
| Local场/整平图/轮廓与诊断 | §3.7/4.13；原采样方向/精度来源/有效域/预算/expand、RawRasterOnly与QualifiedTemplateBinding，禁止未经证明逆/全域单射 | alignment-2d H3 Owner：真实native数据顺序/SourcePrecision证据/expand索引/有效域Golden；要求毫米/逆的消费者及coordinate Owner另取得明确资格，本版不承诺逆 |
| 无UI Core、推荐/Replay、异常/取消/唯一终态/双Host | §3–9、12.1/12.3/13；有限账本/闭集建议/同负载证据/after-drain、根Owner/原Task/child→parent清理、实例隔离 | C1–C3原ModuleCoreImplementationReady仅规格接收保持；alignment-2d实现Owner：授权切片后真实C#编译、BCL Exe/Assembly断言；尚未执行，不等Simulator/native/第二真实Host已通过 |
| 工程候选资产与MA新装配/恢复 | §5.1C.1–4；完整producer/source snapshot、文件/技术hash分离、三Purpose、新SD registration/Materializer/adapter/Authority/Sink/可选签名、原Offer/原Unknown、无发布/采用权 | alignment-2d Owner：生产者codec/格式/challenge/publisher及ALN.ASSET.01–06实现/验证；MA/SD原Owner：真实注册/Origin/耐久/Windows guard及恢复验收；Host来源/回执Owner：精确来源资产/可信证据/原请求耐久保留，不能凭空填客户输入 |
| 可嵌入WPF专业工作台/三语/双STA/Viewport | §10、12.2/12.3；typed草稿与同validator、影像优先/候选联动/参数渐进、权限/键盘/恢复/唯一Offer、真实呈现回执与借用释放 | alignment-2d W1/Viewport接入Owner：真实1920×1080（含边框/任务栏）WPF/UIA/焦点/三语长度/视觉品质/资源关闭/性能验证；DX公开成员资料复用，无下载替换/依赖许可证门 |
| 两个真实消费者及客户交付 | §1.3/9.2/13/14；独立Profile/lease/取消域，精确新旧revision、原事实不覆盖、发布/回退可恢复 | 工程工具/检测宿主Owner：实际图像/ROI/坐标/Viewer/模型与用途装配、客户允许搜索范围/拒识与残差/独立标定/误接受拒绝目标、机器节拍/峰值预算及现场验收；未给物理目标记TargetPending，不阻无关Core |

本轮两轮有界增量自审在本永久原会话完成。第一轮按新封存正常→缺来源→冲突/并发→预算/取消→未知/重启→资源归还检查，仅修实际错误：不把未提供的SourceSnapshot说成Store已保存，MA.Core和Service类型namespace准确，不在Import前声称已获得全部依赖图；新旧Stage身份恢复分开，seal成功后verify失败不假回滚。第二轮从空Host→显式adapter/profile→无UI→两个Host/STA→有限关闭检查，修正challenge的Generation不进入Header、Correspondence.CandidateId不作跨run真值、Local场不任选多候选/不补精度、format与challenge的独占root避免清理自等待；唯一Offer签名与原Runtime/Workbench构造保持。

增量文档结构/相对链接/公开类型与状态核对，以及三schema原字节/长度/SHA256和23-byte原语向量/损坏反例已在本会话验证；完整snapshot往返、C# codec/编译/BCL/真实MA/SD/Authority/Windows/HALCON/WPF/Golden/性能/耐久/物理/现场均未运行。未把新断言/静态资料/原语数学核算当上述资格结果，不等待总控代做本模块内容审核。

新增资产恢复UI资源固定为`Aln.Asset.SourceMissing`：“训练来源未保存。先保存来源，再重试。/訓練來源未儲存。先儲存來源，再重試。/Training source is not saved. Save the source, then retry.”；`Aln.Asset.Pending`：“正在保存。请等待原操作结果。/正在儲存。請等待原操作結果。/Saving. Wait for the original operation.”；`Aln.Asset.Unknown`：“保存结果未确认。查询原操作，不要重复保存。/儲存結果未確認。查詢原操作，不要重複儲存。/Save result is unconfirmed. Query the original operation; do not save again.”；`Aln.Asset.ReadbackFailed`：“资产已保存，读回未通过。保留原模型并检查详情。/資產已儲存，讀回未通過。保留原模型並檢查詳情。/Asset saved; readback failed. Keep the current model and check details.”。三语只投影状态，查询/恢复不获取质量或设备权。

### 17.5 2026-10-11 viewport WPF v0.2窄兼容同步

只读viewport 0.3.4-prep §10.6～10.9/10.6.1，实际消费位置为本页§9.2的双STA预绑定及§10.3A.1。已明确Control→同Owner Renderer/Presentation→Factory/session→显式Lifetime/ExecutionBudget/完整schema Bind→本模块窄桥→Attach的顺序，原submission/Task观测、晚到lease同Owner Revoke/Return、有限Unbind及OwnSession=false的关闭责任；本模块桥公开签名不变，自有lifetime的新版Acquire签名只由实际Host迁移。§17.4完整批准范围内部软件设计闭合结论保持，C1–C3既有规格接收保持，H1/H2/H3/W1/I1仍PreparationIncomplete/NotReady。

原会话定向自审仅沿预绑定正常/缺Lifetime/错Control/资源缺键→Commit/授权与旧代拒绝→Unbind超时/Acquire晚到→双Host关闭走查；保留Core/算法/资产/Root/既有Close/三语及向量有效内容，不全审或重算。已核对引用/结构/公开成员与上游字段，以及未受影响正文摘要保持；未写代码/工程/报告/其它文件，未运行C#、WPF、HALCON、可见观察、UIA、资源/性能/现场验证。W1运行门由alignment-2d Wpf.Smoke及实际Viewport Host/renderer Owner完成同1920×1080真实验证，I1由两个实际宿主Owner完成来源/权限/生命周期接线验收；本次兼容规格不提升上述运行资格，不等待总控内容审核。

### 17.6 2026-10-12 viewport 0.3.5-prep实际消费收口

本轮仅只读viewport §15.2.2.1/4.5.1/4.7.1/20.5，补本页§10.3A.2及§10.3A原高亮/Clear定位。原桥签名、FocusCandidate的SetViewCommand、已对齐v0.2 Lifetime/Presentation/资源、Core/算法/模型/Root/Close/三语/固定向量均保持。稳定源是实际Host可选采用，不强制本模块新建发布源或替换冻结Frames；完整六项对象键与合法空Update两项实际承诺已有公开调用/Task/lease/代/预算/Unknown恢复。§17.4完整批准范围可决定内部软件设计闭合结论保持；C1–C3原规格接收保持，H1/H2/H3/W1/I1实际运行资格不提升。

原会话有限反例走查：同中心重叠对象直接指定B/无几何/旧键拒绝且不伪点击；选择增代与旧事件消回声；Clear已空Sources但旧Return/blank Confirm受阻不成功、不接新ShowFrame；晚到原EmptyTransition确认后同session Update而非再次Attach；源工厂一次identity与逐帧key分开、活跃Context/未知borrow时Remove拒绝。定向文档结构/引用/公开类型/状态检查及保护段摘要核对已完成；没有复算旧向量或执行C#、HALCON、WPF、原Task恒等/资源运行测试、真实空画面、高亮/UIA/性能或现场验收。本任务只改唯一指导，无代码/工程/新报告/脚本/其它文件/新会话，达窄兼容即停；W1由本模块与实际Viewport Host/renderer Owner执行真实1920×1080呈现/选择/Clear/资源验证，I1由两个实际消费者Owner验证来源/权限/租约恢复，不等待总控代审。

## 18. 交付项目只读参考采纳

AsunMeasure的TemplateMatchingContracts、revision、训练/查找分离、Cross-FOV证据及空输入/取消/迟到/释放负向测试思路复用；不直接复制旧WinForms/.NET8模型引擎/阈值/事件或旧wrapper签名。当前唯一实施正文是本页，023只作迁移研究来源。

此前已读的[PCBA-AOI Mark指导](../../references/project-snapshots/PCBA-AOI/20261004/original/docs/40-development/41-vision-platform/04-recognition/Mark与通用定位开发指导.md)、[模板模型注册中心](../../references/project-snapshots/PCBA-AOI/20261004/original/docs/40-development/41-vision-platform/04-recognition/模板模型注册中心开发指导.md)、[AOI.Main Pad闭环](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-27-m13-pad-inspection-full-closure-design.md)仅提供观察/定位/业务判定分离及子模板场景。训练产生新候选artifact，搜索失败后宿主可另起工程训练operation，不是在原生产请求中保底改模型；现场运动回退/重采/出板/MES/放行完全排除。


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

## 附录 A：Module API Contract v0.2.1 与唯一工程绑定

当前契约唯一位置为§3（值/DTO/参数/局部证据）、§4（路线步骤/全域证据端口）、§5（Engine/适配端口/状态事件）、§6–8（资源/错误/兼容）、§10（可选UI公开挂接）。附录只定位这些定义，不另加候选API；v0.1旧草案被替代。公开Core命名空间=`Asun.Modules.Alignment2D`；adapter=`Asun.Modules.Alignment2D.Halcon`；UI=`Asun.Modules.Alignment2D.Wpf`，不能泄漏native类型到Core或UI DTO。

本轮Assembly Contract v0.1已由主控限定内容接收，范围为§5.1A/B、§9.2、§10.3A、§12.3的Root/Runtime/桥/Workbench装配；Core Module API Contract v0.2.1仍保持。本包RuntimeFactory的6项RuntimeServices、WorkbenchFactory的7项WorkbenchServices及三桥binding字段均以对应公开声明为准，附录不再省略/并列第二构造。下面工程仍为未来绑定，不创建新Host/报告工程；Host-A/B分别是既有adapter/Wpf验收工程内有Owner的两个fixture，不将无UI或Simulator通过冒真实WPF/native/生产资格。

| 唯一工程（未来获准切片创建，当前不创建） | 引用/目标与责任 |
|---|---|
| `src/Modules/alignment-2d/Asun.Modules.Alignment2D.Core/Asun.Modules.Alignment2D.Core.csproj` | net10.0类库，BCL；契约/校验/编排/关联/资源账本/模拟可替换端口，无WPF/产品/AsunImage引用 |
| `tests/Modules/alignment-2d/Asun.Modules.Alignment2D.Core.Tests/Asun.Modules.Alignment2D.Core.Tests.csproj` | net10.0 BCL Exe，仅Core引用；§12.1两fixture/脚本后端/固定时钟闩锁/全部ALN.C断言 |
| `src/Modules/alignment-2d/Asun.Modules.Alignment2D.HalconAdapter/Asun.Modules.Alignment2D.HalconAdapter.csproj` | net10.0-windows类库，Core+现有AsunImage直接引用；§5.1A/B Root/Runtime及ModelAssets Service/Core、ImageFrame Resources/Core公开消费桥；§5.1C生产者codec/publisher/route格式adapter/challenge及ModelAssets Formats.Halcon公开端口消费；cv2全部既定native路线/临时模型资源，禁另引用halcondotnet/HOperatorSet |
| `tests/Modules/alignment-2d/Asun.Modules.Alignment2D.HalconAdapter.Tests/Asun.Modules.Alignment2D.HalconAdapter.Tests.csproj` | net10.0-windows Exe，Core+adapter，真实route Golden/训练读回/负样本/资源/性能，输入Profile必须显式提供 |
| `src/Modules/alignment-2d/Asun.Modules.Alignment2D.Wpf/Asun.Modules.Alignment2D.Wpf.csproj` | net10.0-windows、UseWPF，Core+HalconAdapter的Runtime/Root公开类型+本机DX25.2.3；§10嵌入控件/Factory及原Viewport Core/Wpf公开桥，viewer/hostports注入，不引用产品Shell，Core不会反向引用它 |
| `tests/Modules/alignment-2d/Asun.Modules.Alignment2D.Wpf.Smoke/Asun.Modules.Alignment2D.Wpf.Smoke.csproj` | net10.0-windows WPF Exe，Core+Wpf；真实1920×1080/三语/权限/代次/关闭/UIA/视觉与性能，不用CoreExe冒证 |

未来允许范围仅对应明确获准的本模块上述工程；禁止其它模块、Shell/Domain/Integration、共享契约/入口/规则/进度、参考原件/用户配置/正式证据及AsunImage内部。当前本任务允许范围仍仅本指导文件。创建产品工程前确认权威代码仓库/分支，不用本地无.git目录冒已提交。调试工具/报告/样例额外工程不默认获准。

版本兼容按§8；Core ContractRevision=v0.2.1保持，Assembly Contract v0.1限定内容已由主控接收；模块模型与artifact hash、坐标revision、route与API revision全部绑定，不跨旧新组合猜兼容。逐切片六项定位及剩余门见§15；ALN-C1/C2/C3六项规格主控已接收并同步ModuleCoreImplementationReady，H1/H2/H3/W1/I1真实来源、HALCON/native/WPF/Golden/性能/物理/运行资格仍PreparationIncomplete/NotReady；整体DesignReview。没有产品实现/编译/运行结果，不能把规格准备等同真实视觉/UI/生产资格。

