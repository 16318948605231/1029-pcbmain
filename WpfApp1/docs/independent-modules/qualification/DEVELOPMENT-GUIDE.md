# qualification 算法计量与性能资格开发指导

> 状态标记：review=`Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`Core请求/身份/生命周期, Study/Replay, Benchmark`

- 文档 ID：`IM-049-DEV`；来源能力：`PKG-055`；版本：`0.2.6-prep`；日期：2026-10-12。
- 状态：`Prep`，按切片记录。Core请求/身份/生命周期与Study/Replay纯托管协调、Benchmark执行/录制分析软件切片已由主控接收为 `ModuleCoreImplementationReady`（仅文档规格准备）；statistics已明确支持路线桥及U1公开装配恢复指导为限定内容接收。本轮Deming专用桥确定指导内容已由主控限定接收；真实Adapter/能力与运行/数值资格仍PreparationIncomplete，产品/现场资格未完成，整个模块不标生产Ready。
- Owner：qualification 独立模块会话；本轮唯一写入文件为本指导。源指导、共享合同及客户项目只读，由主会话串行接收涉及它们的变更。
- 技术基线：C# / .NET 10；核心无 UI；可选 WPF 控件使用本机 DevExpress 25.2.3；视觉适配经 AsunImage 的 `ImageLibDotNet` 公共边界，目标 HALCON 26.05。
- 交付消费者：标准件/MSA 工具、Golden 回归工具、性能资格工具；第二项目规划消费者为独立光学尺寸测量工具，见 §13。规划接入不等于已运行。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/qualification/Asun.Modules.Qualification.Core/Asun.Modules.Qualification.Core.csproj`；namespace：`Asun.Modules.Qualification`。预定测试工程：`tests/Modules/qualification/Asun.Modules.Qualification.Core.Tests/Asun.Modules.Qualification.Core.Tests.csproj`。上述项目尚未创建。
- 允许变更范围：仅上述 Core 和测试工程目录；在明确获准的实现切片中，必要的新文件也只能放入这两个目录。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 当前规格准入：主控于2026-10-11按 DEV-GOV-010 §3.1 六项接收 Core请求/身份/生命周期与Study/Replay纯托管协调，以及新增Benchmark执行/录制分析软件切片，状态为 `ModuleCoreImplementationReady`（仅文档准备）。statistics支持路线桥/U1公开装配恢复指导仅限定内容接收，上游S7六项规格已由主控接收；本轮Deming专用桥确定指导内容已由主控限定接收；真实Adapter/能力与运行/数值资格仍PreparationIncomplete。该接收不授权本轮创建工程，不是已实现、真实端口接线、运行或生产资格通过；精确后续门见A.7。

## 1. 职责、权威和禁止边界

本模块检查声明的实验设计，组织既有数值能力计算，返回具名统计量、可识别性、失败分母、限制、证据引用及性能条件比较。它拥有一次分析的计算身份、运行状态和不可变分析报告；不拥有测量原值、参考证书、Golden 基线、样本标签、用途批准或生产事实。

调用方负责被测量定义、目标关联、物理件身份、采集动作、实际独立性证明、稳定性与抽样假设、环境记录、接受规范、流程、工艺解释、质量放行和设备副作用。模块检查这些声明的结构、版本和可识别性，不能仅凭文件 hash 证明物理真实性。

| 归属 | 本模块执行 | 留在调用方或依赖端口 |
|---|---|---|
| 试验计划 | 校验计划格、实际格、重复/缺失、方法前提、数值预算 | 选择研究总体、实际样本、操作者、采集/卸装顺序及接受限 |
| 标准件/证书 | 消费有来源的只读投影，按请求时间/条件核必要字段，列依赖关系 | 原件导入/严格解析、信任、实物核验、证书签发和用途批准 |
| MSA | 偏差、受限线性、稳定性、交叉/嵌套矩估计和不确定度的实验组合 | 数值累计/回归/分布/PSD 由 statistics 端口执行；量测由原算法执行 |
| Golden | 固定全体案例与分母，消费 Replay 差异、真值来源及独立性诊断 | 比较器、运行图、Golden 发布、人工标注/更正各守原 Owner |
| 性能 | 执行明确的无设备计算探针，记录真实单调时间/资源/失败/排空，比较预定预算 | 设备/HIL/安全动作、宿主线程/provider 配置、客户节拍承诺 |
| 报告 | 组装报告值、内容版本和稳定证据引用，返回依赖影响清单 | 保存/查询回执、报告导出、签名、批准/撤销及历史保持 |

禁止核心引用产品页面、ViewModel、私有数据库、工单/配方类型、SDK 句柄或可变静态状态；禁止创建第二 QualificationStore、CertificateStore、Golden 注册表、统计库或 Replay 比较器。禁止自动重采、重跑到通过、剔除困难样本、覆盖旧报告/原读数、修改标定、停止机台、提高模型质量等级或签发资格。公共接口不返回一个代表所有层次的 `IsQualified`。

权威范围：本指导及附录 A 定义 `Asun.Modules.Qualification` 的 Module API Contract v0.2；内容接收与实际实现/运行资格按A.7逐切片记录；不以指导内容接收提升整个模块为生产Ready。程序员不得自行更换算法、参数语义、端口责任或结果状态。平台 C-01～C-08、既有持久字段和消费者 Profile 是外部集成映射，不反向定义核心。旧报告保留原版本/字节，禁止以新 codec 重算旧身份。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Qualification.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"禁止自动重采、重跑到通过"，Core 在无 WPF 宿主中完整运行。

**Blazor/Web**：Golden 数据集状态、资格报告与 MSA 结果通过 gRPC/REST 查询；资格签发必须经已授权工程台，不经浏览器。§1 已明确"禁止自动重采、重跑到通过"——Web 端不得以"一键资格评定"暗示自动资格。

**AI 集成**：本模块是 `ai-dataset-governance` §7.4.4（L4）的下游消费者——L4 新物料自适应闭环达到 Cpk>1.33 后，推荐结果由本模块的资格评定流程确认，不绕过本模块直接写入生产。本模块的 Golden 数据集是 AI 模型评估的基准，不被 AI 自动修改。

**HALCON 双跑**：资格验证的 Golden 比对（几何/计量）在 `metrology`/`features-2d` 等视觉模块中执行；本模块协调测量结果与资格判定，不直接调用 HALCON 算子；HALCON 备选 CI 在被调用的视觉模块中执行。

## 2. 包结构和依赖装配

唯一 Core 包、程序集为 `Asun.Modules.Qualification.Core`，全部公共契约和实现 namespace 为 `Asun.Modules.Qualification`；工程/测试落点只取顶部 Core implementation binding，不另建大写 `Qualification` 目录或空 Contracts 工程。公开值与端口同 Core 包交付，但无厂商或产品依赖。可选控件程序集为 `Asun.Modules.Qualification.Wpf`，namespace 为 `Asun.Modules.Qualification.Wpf`；唯一设计落点为src/Modules/qualification/Asun.Modules.Qualification.Wpf/Asun.Modules.Qualification.Wpf.csproj，net10.0-windows/UseWPF=true，引用本Core与本机DevExpress25.2.3。验证落点为tests/Modules/qualification/Asun.Modules.Qualification.Wpf.Tests/Asun.Modules.Qualification.Wpf.Tests.csproj，Exe/同target；§12/A.4双STA模式在该同一验证工程，不另建产品Shell。设计落点冻结不授权本轮创建工程。Core 必须在不启动 WPF、Shell 或隐藏窗口的进程运行。

Core 包内 Contracts 责任只含不可变 .NET 值、枚举、诊断和端口；实现仅依赖这些值与注入端口。Wpf 依赖 Core 公共入口和局部语言/主题上下文。宿主将原契约映射为本页语义，不把厂商、第三方矩阵或产品对象透传到核心。

| 注入端口候选 | 必须提供的操作与返回 | 必要性/生命周期 |
|---|---|---|
| `IQualificationNumerics` | 分组 n/mean/M2、具名残差 SS、中心化回归或受限设计诊断、明确 Lower/Upper 的 t/F、协方差/PSD 检查与传播；返回数值、误差/支持域、实际 method/provider/build 身份 | MSA 必需；复用 statistics/PKG-045 公共能力；不在核心复制实现。每次请求绑定只读 capability 快照 |
| `IObservationSnapshotReader` | 打开指定 revision+hash 的只读、可重读标量快照，分页读固定顺序；返回实际数量、保持租约与封口证明 | 文件/大数据模式必需；小型内存输入不必装配。宿主保留原数据，模块持租约至排空 |
| `IReplayQualificationReader` | 返回精确运行/比较策略/输出/案例全集及每例差异、失败、拒绝证据 | Golden 必需；复用 replay/PKG-043；不触发生产图或覆盖 expected |
| `IReferenceProjectionReader` | 读取原件与解析投影引用、原字段位置/单位/u 或 U-k-覆盖、条件/时间及已核实的用途关系 | 依赖外部参考时必需；复用现有内容/标定证据接收能力 |
| `IBenchmarkProbe` | 受限无设备计算的 `PrepareAsync`、`InvokeAsync`、`DrainAsync`；各次返回 outcome、真实完成屏障、运行身份和输出摘要 | 执行基准时必需；调用方拥有被测算法，不能注册设备控制或生产提交端口 |
| `IResourceSampler` | 时间点、metric/unit、作用域、值及可用性；scope 为 Operation 或 Process，无法归因时明确说明 | 需要该资源预算才必需；不支持的指标不能返回0 |
| `IQualificationOperationLedger` | 以 `CalculationId`、canonical request hash 和实例代次原子保存 Accepted、阶段、报告引用、终态、排空和诊断摘要，并提供只读查询 | 需要跨进程幂等、重启恢复或 `QueryCalculationAsync` 时必需；由宿主/平台 Owner 注入，不得在本模块创建私有 store |

表中 `I*` 端口及请求/回执结构属于本模块 v0.2 Adapter Port 契约，适配器实现必须遵守这些操作、结果字段和资源语义。它们不是既有上游组件的同名公共签名：接入时用薄 adapter 映射实际获批 API，并保持 Core 不变。能力发现返回支持的方法 ID/版本、数值域、最大可接纳维度、可否中断、线程要求和已验证操作路径；缺能力拒绝对应分支，不用临时服务定位器或隐式 fallback。端口实例由宿主所有，本模块只归还自己取得的租约，不自动 Dispose 宿主共享服务。`QueryCalculationAsync` 必须读取同一 `IQualificationOperationLedger` 的原记录，不能从内存缓存、最新报告或 UI 状态拼出回执。

## 3. 通用数据契约

以下字段是 v0.2 模块 API 的规范强类型语义；每个 union 必须使用独立变体，禁止用任意字典、裸字符串算法名和一组无关可空字段拼装请求。模块内部/本模块包间编码按固定版本化 codec 实现；平台映射不得增删、重解释字段。

### 3.1 基础值和版本

| 类型/字段 | 类型、单位、约束 | 默认/缺失语义 |
|---|---|---|
| `CalculationId` / `ExperimentId` / `ObservationId` / `PhysicalSpecimenId` | 独立 ID 包装类型；非空、不含控制字符、最长160字符，Ordinal 比较，命名域明确 | 无默认。计算 ID 不能代替物理观察 ID |
| `ArtifactRef` | `Namespace, Id, Revision, Sha256`；revision 非空；SHA-256 为64个小写十六进制字符 | 精确引用，不支持运行中解析 Current/latest |
| `MethodRef` | 方法 ID、语义版本、参数内容引用、数值策略引用、实际 backend/build 引用 | 无默认，方法或参数改变产生新计算身份 |
| `QuantityValue` | 有限 `double Value` + `UnitId`；UnitId 指向不可变量纲/缩放词表 | 无默认；缺测是状态，无效不能用 NaN/0 表示 |
| `UnitId` | 固定单位注册表中的 ID、量纲及修订；首批支持长度/面积/体积/角度/时间/无量纲；偏移温标转换由适配器登记 | 未登记单位拒绝；不根据显示后缀猜量纲 |
| `Duration` | `TimeSpan`，传输记录整数100ns ticks；真实计时另存 Stopwatch 原 tick 与 Frequency | 无负值；测量分辨率不因显示 ns 提高 |
| `Count` / `Bytes` | `long`，非负；格、矩阵和字节乘法使用 checked 算术 | 未取得是 Unknown，不填0 |
| `EvidenceLevel` | `Synthetic / SoftwareReplay / RecordedMeasurement / PhysicalMeasurement` | 必填，不从文件位置推断；工程成熟度、方法适用性、批准状态分别表达 |
| `Scope` | 被测量 ID/修订、单位、单次或平均、支持域引用、量程、来源系统/光路/标定/环境/时间条件 | 本模块不解释制程目标或材料政策；范围未知不扩大用途 |

原单位和值永久保留；规范化后再计算，输出附转换词表与比例。均值/标准差按线性比例转换，SS/方差/协方差按对应单位乘积转换，敏感度反向转换。跨量名、坐标或支持定义的相同数值不混合统计。输出方差单位是输入单位平方，斜率单位是响应/自变量，百分比显示 `100 × ratio`，不能与 ratio 混写。

### 3.2 试验计划与观测

`QualificationRequest` 包含合同版本、CalculationId、ExperimentId、MethodRef、Scope、InputSnapshot、EvidenceLevel、资源预算、截止策略及一个明确分析变体。计划必须先于结果冻结；重算使用相同快照及方法但新 CalculationId，并关联 parent。

| 对象 | 必填字段与语义 |
|---|---|
| `ExperimentPlan` | 精确计划引用/hash；计划格集合；因素及固定/随机水平/总体声明；顺序或随机化算法+seed+输入排序；排除/补采规则引用；预声明假设证据；期望总格/观测数 |
| `PlanCell` | CellId、物理件、操作者或明确设置、重复次序、实际重复层级、所需方法/被测量；嵌套还含父因素关系；时间试验保留设计时间/实际时间分别 |
| `Observation` | 唯一 ObservationId、CellId、PhysicalSpecimenId、物理状态修订、TargetRef（不透明宿主引用）、CaptureId/ReplayId、RepositionCycleId、操作者/设置、实际 UTC 时刻、环境、输入/量测/方法/标定引用 |
| `ObservationOutcome` | `Measured(QuantityValue)` 或 `Failed(Reason,EvidenceRefs)` 或 `NotCollected(Reason)`；`Excluded` 是独立的预声明规则投影，必须仍能读取原 outcome |
| `ReferenceAssignment` | 物理件/特征/被测量、证书原件与解析投影引用、赋值、原单位、不确定度变体、相关组、实际条件及用途关系；无参考仅允许相应散布描述 |
| `RepeatLevel` | `SameInputReplay / IndependentCapture / RepositionedCapture / OperatorOrSetup / CrossDay`；不同因素组合由计划表达，不通过高枚举自动取得更高资格 |
| `AssumptionEvidence` | 稳定性、独立性、正态/同方差/总体/线性化等具名声明及证据引用，状态 `Declared / Supported / Contradicted / Unknown`；数值结果不能替代声明来源 |

相同源图复制成新文件或更换 ID 不增加物理独立 n；检测到同一 CaptureId/Replay 来源重复时列诊断，未检测到重复不等于证明独立。补采保留原失败格和新观察关联，选取哪次进入估计由事先冻结规则确定，禁止取最佳结果。物理件/状态/观察身份冲突拒绝该分析；合法缺格可返回局部描述，不能返回完整平衡 GR&R。

### 3.3 分析变体与参数

| 变体/参数 | 强类型范围、单位、条件 | 默认值/策略 |
|---|---|---|
| `BiasPlan` | 单一参考/被测量；n≥1 可给差值，n≥2 才有样本方差；推断另需条件 | 必须显式选择；不默认需要区间 |
| `LinearityPlan` | 固定参考水平、中心化仿射偏差；N>2、至少两不同参考；范围与重复层级明确 | 冻结中心化OLS描述路线，不自动启用加权/误差变量模型 |
| `StabilityPlan` | `TimeTrajectory / LinearDrift / BalancedRandomDay`；实际时间单位，窗口和条件；随机日 h,r≥2 | 必选；没有历史基线只给轨迹 |
| `GrrPlan` / `GRRPolicy` | `BalancedCrossedMoments / BalancedNestedMoments`；a,b,r≥2、格完整；交互模型固定 | 无默认，不能依据结果选择交叉/嵌套或池化 |
| `VarianceComponentPolicy` | `RawOnly / PreserveRawAndClampNegative`，后者仅明确选定时给边界点估计 | `RawOnly`；负数不取平方根，不偷偷截断 |
| `UncertaintyModelId` | 不可变模型引用、分量角色/相关组/敏感度、线性化条件 | 无默认；不靠 GRR 一项代表完整预算 |
| `ConfidenceLevel` | 可空 `Probability`，0<C<1，保留原十进制文字和已验证的数值表示；仅受支持推断使用 | null=不请求区间。请求区间而缺值拒绝，不能默认95% |
| `StudySpanFactor` | 可空有限无量纲 `double`，>0，预声明规范引用 | null=不计算公差占比；不默认6 |
| `ToleranceInterval` | 可空同量纲 LSL/USL，有限且USL>LSL | null=只给绝对量/研究比例；不默认接受线 |
| `CoverageDefinition` | `StandardOnly / ExplicitFactor`；后者要求 k>0、覆盖含义/依据、概率或其未知原因 | `StandardOnly`；k与研究跨度系数分开，k=2不自动等于95% |
| `UncertaintyComponent` | Type A/B、原来源、具名 u≥0 或已知 U≥0/k>0、敏感度及单位、自由度或未知、分布及依据、是否已经计入 | 无自动分布；±范围不自动转矩形 |
| `Covariance` | p×p，元素有限，维度/单位对应，对称及PSD按已冻结无量纲/尺度政策验证；相关ρ∈[-1,1] | 未知相关保留 Unknown；绝不默认0 |
| `NumericPolicyRef` | 方法支持域、累计顺序、缩放、秩阈值、误差与PSD容差、尾表示及实际数值后端的精确引用 | 必填；无通用1e-6，不从 UI 位数生成 |
| `ExclusionRule` | `None` 或运行前冻结的规则引用、受影响范围和理由 | `None`；运行后编辑形成新研究，不改旧分母 |

接受条件为单独的 `AcceptanceCriteriaRef`，必含度量 ID、单位、比较方向、界限、是否要求区间/完整性/独立性及来源版本。缺条件只给结果和 `NotEvaluated`。技术上的输入合法上下限不代表客户接受限；本模块不批准这些条件。

### 3.4 Golden 与性能输入

`GoldenPlan` 固定案例全集、父物理组、基线/真值/人工意见的不同来源、原/候选运行和比较策略、计划重复次数/种子集、必需输出。每例返回 `Consistent / Changed / Incomparable / ExecutionFailed / NotExecuted`，预期拒绝断言独立保存。训练/调参/测试分组来源从数据治理或宿主读取，不按文件随机拆同一物理父组。要求分类区间时消费已有数据集评估端口的精确报告，首版不实现第二分类估计器。

`BenchmarkPlan` 固定 probe+build、输入负载引用/摘要、冷/热模式、Prepare 边界、缓存模式、预热/测量次数、并发、到达计划、超时和失败策略、资源采样范围与比较预算。`ExecutionMode=ExecuteProbe / AnalyzeRecordedRun` 显式选择；后者不能声称本模块运行了被测算法。冷启动的 fresh worker 由宿主提供，已运行进程里的重复调用不标冷启动。

| 参数 | 范围、单位 | 保守软件默认与解释 |
|---|---|---|
| `WarmupIterations` | int，0..1,000,000 | 0；不自动推断稳态；预热失败仍单列 |
| `MeasuredIterations` | int，1..1,000,000 | 无默认；未指定则拒绝 |
| `BenchmarkParallelism` | int，1..64，受 probe 能力与宿主额度限制 | 1；改变并发形成新计划 |
| `ArrivalMode` | `ClosedLoop / RecordedSchedule` | ClosedLoop；不能用其结果保证外部突发排队 |
| `FailurePolicy` | `StopOnFailure / ContinueIndependentCases` | StopOnFailure；Continue 仅案例独立/资源可恢复时允许，无自动重试 |
| `ResourceSamplePeriod` | TimeSpan，10ms..60s | 100ms；仅为候选采样周期，不能证明捕获了采样间峰值 |
| `LatencyBudget` | 按阶段 `TimeSpan` 上限，P50≤P95≤P99，均>0；附方法/环境/负载/所需次数 | 无默认。缺预算 NotEvaluated；不是硬实时保证 |
| `ResourceMetricBudget` | metric+scope+unit、峰值/保持容量、预定测量窗口及允许斜率 | 无默认；Byte/count/rate 不混合，要求的不可用指标 NotEvaluated |

## 4. 同步/异步入口和返回

下列 C# 是 v0.2 模块 API 的规范签名形状；逐字照搬仍需对照附录 A 全部公开类型完成编译。它不是既有平台 DTO，也不是 AsunImage 签名。

入口的唯一公开签名见附录 A.3 的 `IQualificationService`；本节只规定各入口的处理和生命周期语义，避免再维护第二份接口声明。

`ValidateDesign` 同步纯检查，只访问已物化计划/引用元数据，不读取文件、UI 或运行探针；返回全部可定位错误及该分支前提。`Analyze` 只接收有界内存标量快照以及公开声明可同步调用的数值端口，使用同一检查/方法/错误语义；不得用 `.Result`/`.Wait()` 包装异步读取。宿主不得在 UI 线程运行大规模同步计算。

`AnalyzeAsync` 负责只读快照打开/分页、数值能力调用、报告组装；Golden 消费已有封存比较；Benchmark 才执行显式注入的纯计算 probe。异步不等于每次任意 `Task.Run`，执行器按单实例额度调度，同步请求也占相同额度。每实例默认最多一个在途操作，满额立即返回 `QLF-OP-BUSY`，没有隐藏无界队列。

先在根 Owner 预约输入/索引/报告/数值端口工作区/订阅的合计容量，再执行 PrepareInput：检查版本、声明 Count、实际数组长度、字符串与集合字节上界、checked 格数/矩阵乘积；超限在复制和 hash 前拒绝。仅接受数组或已冻结页，拒绝任意 IEnumerable 的无界枚举。预约成功后复制并冻结→校验所有字段→按附录 A 编码/hash→接纳，原数组不能在复制期间被调用方修改；无法保证时必须使用封口 Reader。Reader 必须逐页及全集核 hash/Count/封口，重复读取总量计入预算；输入更正只产生新快照。

同 CalculationId+同 request hash 在实例中返回 Duplicate；异 hash 返回 `QLF-OP-CONFLICT`，均不重算。QueryCalculationAsync 返回原实例/代次/回执版本/阶段/请求hash/原报告引用，不能从最新报告拼装。内存 ledger 仅证明本进程，重启不可恢复；持久 ledger 来自宿主。查询 NotFound 不证明未执行。接纳写回执 Unknown 时保持 `AdmissionUnknown`，停止派发并按原身份查询；只有 ConfirmedAccepted 才派发一次，ConfirmedAbsent 只返回未接纳，不自动重新提交。

生命周期为 `Created → Ready → Stopping → Stopped → Disposed`。创建时绑定端口能力及实例预算后进入 Ready；Ready 才接收新请求。停止后不原地重启，需新实例；DisposeAsync 先停止接收再等真实排空，未结束则等待，不能强释放。StopAsync 的 waitBudget 只限制等待，waitToken 只取消等待；返回 `Drained` 或 `StillDraining(Completion)`，不把未退 native 变为停止。宿主可关闭视图并保留服务 Owner 等待 Completion。

### 4.1 根 Owner、关闭与移交

Factory 前必须由已经存活的 `QualificationRecoveryOwner.CreateRoot(rootId,RootLimits)` 原子创建并登记根，预约固定 Service/Task/Lease/观察/保存槽与保留字节；根满则 Factory 不运行，不能先创建服务或开线程再找 Owner。根按实例持有 Service、原 Analyze/Reader/Numeric/Probe/Ledger/EvidenceSink/Stop/Dispose Task、输入/报告、CTS、观察订阅与迟到租约。Task 完成不等于其借用资源已归还；端口 Completion 必须证明全部子工作和租约退出。查询/观察等待超时只解除本次等待，不移除这些强引用。

`CloseAsync(CleanupBudget, token)` 停新接纳→取消本根操作→断开观察/撤 UI Binding→并行观测已登记原 Task→启动且登记一次 Stop 与 Dispose→等待独立 cleanup 截止。cleanup 不复用业务取消令牌，且使用单调总截止，不为每个资源重新给完整预算。Dispose 只有真实排空后完成；cleanup 截止返回 Draining/DrainUnknown，未确认的任务继续由根强持，字节/槽不归还。业务 outcome 与 cleanup diagnostics 分字段，后者不能覆盖原失败、取消或保存未知。

根转交进程监督者采用 `BeginTransfer(TransferId,targetRecoveryOwner) → TransferOffer(原身份/任务/资源/容量) → AcceptTransfer → TransferReceipt`；目标预留全部容量并原子承认持有后源才交还槽。失败/响应未知由源继续持有、查询同 TransferId，不重复移交；源和目标不得双重 Dispose。原 Task 迟到返回租约时在当前已确认 Owner 的串行释放队列处置，重复 callback 通过 LeaseId 去重。根为实例对象，禁止静态 Task 列表、GC finalizer、遗忘 Task 或仅保留异常日志代替 Owner。独立 Exe Host 无监督者时超时退出非零，由隔离进程外层终止软件测试；不得将此当作设备/native 已安全排空。

## 5. 输出、状态、事件与错误

### 5.1 输出不能压成一个 bool

`QualificationOutcome` 返回 OperationTerminal、CalculationId、实际完成范围、可空报告、结构化诊断及资源释放摘要。`QualificationReport` 必含原输入/计划/方法/环境/参考/比较策略/build 的精确引用、原单位与转换、全体计划/有效/失败/排除/未执行计数、可复算数值/SS/df、残差/秩/谱诊断、原与边界估计、比例分母、预算缺口、证据层和适用限制。数值带 `Available(Value,Unit,MethodRef)` 或 `Unavailable(Reason)`，不以 null 或 NaN 无解释地替代失败。

| 维度 | 状态 | 含义 |
|---|---|---|
| 执行终态 | `Completed / Rejected / Cancelled / TimedOut / Failed` | Completed 是计算/组织动作完成，不保证任何指标合格；Rejected 未进入算法；Cancelled/TimedOut 只在排空后终结 |
| 报告完整性 | `Complete / Partial` | 依声明输出与固定范围；合法完整报告可以全部是不可测诊断，不能因此算合格 |
| 数值项 | `Computed / UnsupportedDomain / Indeterminate / NotRequested` | 一个不支持区间不抹掉有效点估计；不可表示尾概率不是精确0 |
| 方法适用性 | `ApplicableWithinDeclaredScope / Limited / NotApplicable / NotEstablished` | 绑定假设证据；可算不等于实验假设已经验证 |
| 条件比较 | `MeetsDeclaredCriteria / DoesNotMeetDeclaredCriteria / NotEvaluated` | 只对应调用方预先提供条件；必要证据/区间缺失不能选前两项 |
| 用途决定 | 外部决定引用或 `NotProvided` | 核心没有 Approve/Release/ProductionAccepted 状态及命令 |

缺格/失败输入完整读取后可以完成一份 Partial 报告；读到8/预计10且另外2条读取中断时是读取未完成，不能当完整10条中合法2条缺测。各状态与证据层同时显示，报告不得把计算完成印成“认证通过”。

### 5.2 事件顺序

每操作带 `InstanceId, CalculationId, RequestRevision, Sequence(long), Stage, CompletedUnits, PlannedUnits, MonotonicTimestamp`，Sequence 递增。通知传不可变摘要，不带图像、矩阵或隐式所有权转移。返回值为结果权威，通知只供观察。

正常序列为 `Accepted → StageStarted(Validation) → StageFinished → StageStarted(Read/Compute/Compare/Report) → Progress* → StageFinished* → Draining → Drained → ResourcesReleased → Terminal`；不用的阶段明确 NotRequired。输入非法可 `Rejected → Terminal(Rejected)`，不发 Accepted。失败/停止路径为当前阶段诊断、`CancelRequested / DeadlineExceeded`（实际触发者）、停止新派发、`Draining → Drained → ResourcesReleased → Terminal`。Terminal 恰一次且在实际子调用退出、自有租约/额度归还之后；接纳的请求 Task 在 Terminal 状态固定后完成。触发先后用实例内原子记录决定，不因迟到成功改写已选取消/超时原因；结果提交线性化之后的取消不回改完成结果。

Progress 可合并，终态/阶段结果不得合并丢失。观察者订阅采用独立有界邮箱，运行线程只入队，不调用任意订阅者代码；默认每订阅容量256、进度最新值合并。订阅者异常/堵塞/溢出时断开该订阅，记 `QLF-OBS-DETACHED`，原操作继续；可按操作读取最终状态。FIFO 保证每订阅已交付项的顺序，订阅被断开时不承诺全部通知送达。终态保存在操作返回值，不靠邮箱保证完成。

UI 调度由控件/宿主 Dispatcher 完成，核心不捕获 SynchronizationContext。不在模块内部同步 Invoke UI。控件按 InstanceId+CalculationId+Revision 过滤晚到通知，新请求不接管旧请求结果；事件订阅关闭只断开观察，不隐式取消其他消费者。

### 5.3 结构化错误和恢复

`QualificationDiagnostic` 含稳定 code、Severity、Stage、FieldPath/CellId/ObservationId、原因资源键/参数、EvidenceRefs、可选原后端 code/type 与实际 build。以下编码是本候选命名域，平台适配时逐项映射原合同；未知错误码必须显示通用错误并保留原码，不能转成功。

| code | 语义 | 调用方恢复 |
|---|---|---|
| `QLF-INPUT-INVALID` | 类型/有限性/必填/预算非法 | 修请求，生成新计算身份 |
| `QLF-INPUT-UNIT` | 量纲/单位词表或转换不符 | 提供明确转换，不改原值 |
| `QLF-INPUT-IDENTITY` | 重复观察、件/格/源冲突 | 查原采集关联，保留冲突 |
| `QLF-INPUT-INCOMPLETE` | 快照缺页/未封口/hash不符 | 固定正确来源重新计算，不把已读前缀当全集 |
| `QLF-DESIGN-GAP` | 缺格/不足自由度 | 可保留局部描述，按原计划补采由宿主执行 |
| `QLF-DESIGN-UNIDENTIFIABLE` | 因素/时间共线、模型不可识别 | 修改并批准新的实验，不换估计器凑结论 |
| `QLF-REFERENCE-INCOMPLETE` | 必要赋值/u/覆盖/实物关系未知 | 仅依赖参考的输出不可评价；补源投影 |
| `QLF-REFERENCE-OUTSIDE-SCOPE` | 用途/条件/时间不满足声明 | 原 Owner 审查用途，历史原件保持 |
| `QLF-METHOD-UNSUPPORTED` | 所声明模型/区间/数值能力未提供 | 返回点估计/限制（若有效），不静默换方法 |
| `QLF-NUMERIC-DOMAIN` | 后端支持域或表示精度不足 | 保留原参数与诊断，新方法须另批准 |
| `QLF-NUMERIC-INVALID` | 非有限、SS恒等式/秩/PSD/残差校验失败 | 查询具名输入及数值策略，不用截断修复非法矩阵 |
| `QLF-BUDGET-EXCEEDED` | 行/格/矩阵/字节/工作范围超限 | 停新工作、排空；明确未完成，不截断后算完整 |
| `QLF-OP-BUSY` / `QLF-OP-DUPLICATE` | 在途额度满/ID重复 | Busy 可待原完成；Duplicate 查询原状态，不自动重算 |
| `QLF-OP-CONFLICT` | 同计算ID异request hash | 保留原请求，修正调用身份；不覆盖原回执 |
| `QLF-PORT-CONTRACT` | 回执版本/身份/计数/完成屏障/租约不符 | 停对应分支、保留原Task和租约，查询原Owner，不重新发起副作用 |
| `QLF-DRAIN-UNKNOWN` | 断连/端口异常后实际工作或租约释放未确认 | 非终态DrainUnknown；当前Owner强持，按原身份查询或确认移交 |
| `QLF-OP-CANCELLED` / `QLF-OP-TIMEOUT` | 原因已选并实际排空 | 可保留部分诊断，新运行保留 parent 与失败尝试 |
| `QLF-OP-NOT-READY` | 已停止或已 Dispose | 使用新实例，不复用旧资源 |
| `QLF-PROBE-FAILED` / `QLF-PROBE-CONTRACT` | 被测调用失败/未提供真实完成屏障或结果角色冲突 | 排空，保留失败尝试；不测成功子集冒称全负载 |
| `QLF-RESOURCE-UNAVAILABLE` | 指标无权限/无计数器/无法归因 | 该预算 NotEvaluated，不填0 |
| `QLF-OBS-DETACHED` | 观察订阅无法继续 | 重新订阅/查询，不改变计算结果 |

预期拒绝/取消/后端数值失败使用明确 outcome。null 请求、已释放契约对象等程序错误可抛 ArgumentException/ObjectDisposedException；未处理异常在操作边界记录并转换 Failed，进程致命故障由宿主处理。裸异常文字不直接作为操作员文本。

## 6. MSA 和计量的实施步骤

本节将既有 DEV-MET-033 的通用数学模型整理为独立包流程，不扩大其已知方法范围。数值端口执行稳定累计/代数/分布，qualification 组合模型、解释假设和报告；下面公式为组合断言，不授权在本包另写统计内核。

### 6.1 公共前置和偏差/线性

1. 固定输入引用、全体行/格、量名/单位/支持、实际重复层级、方法及预算；校验封口、ID、维度/hash和数量，核参考投影与声明时间/条件。
2. 按预声明规则标有效/失败/排除并保留原行；检查该分析的识别条件。重复软件输入不进入物理重复的有效 n；无实际独立性证据则只给声明层次结果/限制。
3. 偏差使用 `d_i=y_i-x_ref`；数值端口返回 n、mean、M2，`bias=mean(d)`，n≥2 时 `s²=M2/(n-1)`、随机标准误 `s/sqrt(n)`。参考共同 u 不除 sqrt(n)。n=1 只给差值，n=0 没有偏差值。
4. 请求条件 t 区间且假设/支持域满足时，令 `alpha=1-C`，直接传 t Upper `alpha/2` 与 df=n-1；区间为 `bias ± quantile*s/sqrt(n)`。原置信文字、alpha 和尾表示保留；不先构造接近1的概率。s=0 只报告该样本散布为0及退化限制，不据零宽条件区间证明物理无误差；共同参考/其它误差仍在。
5. 线性首版固定 `d=alpha0+beta*(x-x0)+epsilon`，`x0=mean(x)`；数值端口稳定中心化给 `Sxx,Sxd`，`beta=Sxd/Sxx`、`alpha0=mean(d)`，N>2、Sxx>0才有残差方差 `SSE/(N-2)`。中心截距与原零点截距分开。逐参考/残差/df/测量范围返回，不用 R² 授资格。
6. 重复参照的失拟：g个不同水平，`SS_PE=sum(d_lk-mean(d_l))²`、df=N-g；`SS_LOF=sum(n_l*(mean(d_l)-prediction_l)²)`、df=g-2；核 SSE=PE+LOF。g≥3、df_PE>0且模型条件满足时请求 F Upper，分子/分母 df 不换序；PE=0保留退化，不除0给普通p。
7. 参考 x 不确定度不可忽略、相关/异方差/聚类或量程外使用时，OLS最多是受限描述；首版不支持误差变量、GLS、通用同时覆盖曲线或自动重新加权。无显著失拟、区间含0均不证明满足精度或等价。

### 6.2 稳定性与 GR&R

稳定性先给预定窗口内实际时间轨迹、每时点偏差/散布/失败与条件变化。漂移仅按线性时间模型给量值/时间斜率，不外推证书有效期；没有固定基线不自动生成稳定合格。平衡随机日模型 h,r≥2，`SS_day=r*sum(dayMean-grandMean)²`、df=h-1；`SS_within=sum(y-dayMean)²`、df=h(r-1)；`ve=MS_within`、`vDay_raw=(MS_day-MS_within)/r`。确定漂移、相关、参考自身漂移或因素混杂时不得解释为独立随机日分量。

交叉模型固定为 `y_ijk=mu+P_i+O_j+(PO)_ij+epsilon_ijk`，a,b,r≥2且完整。先核 a*b*r 的受控计数和物理件稳定声明，再由数值端口两遍得到总均值m、件均值p_i、操作者均值o_j、格均值c_ij及格内残差。大偏置小散布禁止使用 `sum(y²)-sum(y)²/N`。

| 交叉项 | SS | df | 原矩估计 |
|---|---|---|---|
| P | `b*r*sum(p_i-m)²` | a-1 | `(MS_P-MS_PO)/(b*r)` |
| O | `a*r*sum(o_j-m)²` | b-1 | `(MS_O-MS_PO)/(a*r)` |
| PO | `r*sum(c_ij-p_i-o_j+m)²` | (a-1)(b-1) | `(MS_PO-MS_E)/r` |
| E | `sum(y_ijk-c_ij)²` | a*b*(r-1) | `MS_E` |

回核 SS_total 为四项和、df和为abr-1及有限性/冻结尺度误差。交互保留，不根据 p 值或负分量事后池化。负原估计与预选的边界点估计并列；仅非负采用分量齐全时汇总 `vGRR=ve+vo+vpo`、`vTotal=vGRR+vp`。件间变化不进入设备GRR。

分别返回绝对 `sigmaGRR=sqrt(vGRR)`、方差贡献 `100*vGRR/vTotal`、研究变差 `100*sqrt(vGRR/vTotal)`、公差占比 `100*StudySpanFactor*sqrt(vGRR)/(USL-LSL)`。缺策略/分母为0/公差或跨度未知则相应项 Unavailable；不默认10%/30%线，天然件差放大不会变成测量能力改善。本首版没有 GRR/方差分量置信区间；要求区间的条件不可评价。

嵌套模型仅用于每个操作者拥有自己的a个可交换稳定件、每件r次观测：`y_ijk=mu+O_i+P_j(i)+epsilon`，a,b,r≥2，物理件不能跨操作者重复编码。`SS_O=a*r*sum(o_i-m)²`、df=b-1；`SS_P(O)=r*sum(c_ij-o_i)²`、df=b(a-1)；`SS_E=sum(y_ijk-c_ij)²`、df=ab(r-1)。`ve=MS_E`、`vp_raw=(MS_P(O)-MS_E)/r`、`vo_raw=(MS_O-MS_P(O))/(a*r)`；不估交叉交互。r=1的新件/破坏试验只能给合成散布，不可分离纯重复性。

多因素/不平衡/缺格的完整 GRR 首版不支持。设备差与时间线性列完全共线时返回 Unidentifiable；一般设计诊断使用已验证 QR/秩端口，不用默认伪逆或改模型制造识别性。ABBA 仅证明特定线性时间列可识别，不证明消除所有漂移。

### 6.3 相关不确定度预算

1. 固定报告量 `z=f(x)`、单次/平均方式及线性化点；逐分量绑定原来源、单位、Type A/B、u/覆盖来源、敏感度和是否已含；Type A/B不是随机/系统分类。
2. 明确U和k/覆盖含义时才用u=U/k。量化步距q且±q/2均匀模型适用时用q/sqrt(12)；矩形±a用a/sqrt(3)、三角±a峰值0用a/sqrt(6)，均须显式来源。显示位数不证明步距，未知分布不能补矩形。
3. 单位一致后检查协方差Σ的对角u²、相关项ρ*u_i*u_j、对称/PSD与相关组完整性；未知相关不置0。敏感度c与Σ交给数值端口，返回 `uc²=cᵀΣc` 及各贡献；非法Σ不能用负方差策略修补。
4. 缺分量/关系仅给标明范围的小计，不标总uc。强非线性、阈值跨越或支持域变化超出线性化范围时拒绝该传播用途，不自选蒙特卡洛替代。
5. 只有显式覆盖模型成立才给 `U=k_cov*uc`，注明覆盖含义/概率/自由度或未知。首版不提供相关混合分量通用有效自由度和自动覆盖因子。
6. 共同参考、标定等共同项不随平均次数下降；核 GRR/量化/采集已含项去重。修正偏差由原 Owner 决定，核心保留原读数/修正来源并分析对应预算，不覆盖测量值。

### 6.4 跨机、跨批与条件一致性比较（受限变体）

本变体只比较同一被测量、单位、支持域和同一 `ReferenceAssignment`/challenge 的成对或可追溯观测。`ExperimentPlan` 必须把机台/采集实例、批次、日期或班次、温度/环境、重启/重标定条件声明为因素，并在既有 `PlanCell`/`Observation` 的来源、时间和环境引用中给出实际值；随机顺序、配对键、独立性和排除规则由计划冻结。缺少这些因素或不能证明同一 reference/challenge 的对应关系时，不进入跨机结论。

v0.2 固定方法为 `IndependentPairsBlandAltman`，可显式附加 `ConstantRatioDeming`；组合MethodId固定为 `IndependentPairsBlandAltman+ConstantRatioDeming`，不接受任意拼接；不派发任意 EIV/误差模型。先全外连接计划 PairId 与 A/B ObservationId，核对量名/单位/状态/支持、物理件状态和同层条件；一个 PairId 一对值，不按文件顺序 zip。未测、失败、排除、单侧缺失分别保留；重复物理件的多次配对不当独立 n，不默取平均，未提供重复测量模型时只给描述和 `NotEvaluated`。

每个计划层单独计算 `d=B-A`、`m=(A+B)/2`（以稳定中心化避免溢出）、n、mean(d)、M2(d)，`s_d=sqrt(M2/(n-1))`；n=0 无值、n=1 仅差值。n≥2 且独立性、差值近似正态及恒定散布证据成立时，LoA 为 `mean(d) ± LoaMultiplier*s_d`，系数>0、来源和覆盖含义由 MethodRef 显式冻结，无默认1.96。LoA 是差值分布界限，不是均值置信区间、客户允差或总不确定度；若请求 bias 的 t 区间，沿 §6.1 使用 n-1 和 Upper 尾。v0.2 不提供 LoA 置信区间/重复测量/异方差/百分比或对数变换 LoA；条件要求这些输出则为 `NotEvaluated`，不能用普通 LoA 冒充。s_d=0 保留退化限制，不证明物理零误差。

Deming使用已冻结的 [statistics S7唯一算法/公开合同](../statistics/DEVELOPMENT-GUIDE.md#constant-ratio-deming)，上游六项规格接收不代表已发布可运行后端。资格请求的ErrorVarianceRatio为**原输入单位下**Var(error_B)/Var(error_A)>0；显式DemingPointPlan给CenterX、两侧单位变换、配对/误差比证据/方法、明细与有限预算。x=A/Left、y=B/Right，Slope单位Y/X；x'=a*x+c、y'=b*y+d（a,b>0）时必须同时用λ'=(b/a)²λ、CenterX'=a*CenterX+c，源/方法/派生身份形成新请求。不默认ratio=1/CenterX=0；禁止显示标签换单位、OLS替代、由Pearson普通double矩恢复极端Sxy或在qualification复制S7算法。

每个层的Deming与Bland–Altman分成两个具名数值操作，S7单family请求不混PairTask/DistributionTask。S7的Finite/Horizontal/Vertical/Unidentified/NotEvaluated、全覆盖与双侧Coverage、ScaledValue及中心截距逐字段保留，Sxy=0的Horizontal/Vertical仅方向诊断，系数都Unavailable（不补0/∞）。RangeLoss/UnsupportedDomain/NumericUncertain保留原Code与已得矩，不将Completed当可识别或物理资格。点估计只支持已冻结无权重、独立配对、恒定已知误差方差比、两侧误差不相关的模型；CI/ODR/加权/异方差/重复测量/相关误差、校正或用途批准仍不支持。实际Capabilities未声明S7时仅该附加斜率Unavailable、QLF-METHOD-UNSUPPORTED/NotEvaluated，其它描述继续；精确构造/来源/hash/结果/Owner与两Host配方见A.3.1.1。

逐层返回 bias、LoA、散布、Deming 斜率（如请求）、残差和所有分母；全局只汇总计数并展示各层，不汇总成一个“总体一致”。方法/参数变更产生新 MethodRef/CalculationId，支持域外条件不外推。任何层条件未满足必须保留，平均改善不能抵消它。

报告逐层返回计划/实际 n、失败与未执行分母、bias/slope、Bland-Altman 界限或其不可用原因、边界条件和数值 backend/build；不把不同支持域、批次或条件强行合并。未提供 EIV/界限所需能力时返回已计算的受限描述和 `QLF-METHOD-UNSUPPORTED`/`NotEvaluated`，不静默退回 OLS 或用相关系数替代一致性。配对不完整、条件共线或参考超范围分别保留 `QLF-DESIGN-GAP`、`QLF-DESIGN-UNIDENTIFIABLE` 或 `QLF-REFERENCE-OUTSIDE-SCOPE`，不得删掉困难层后重算。

修复必须由宿主以新计划/快照/`CalculationId` 补齐实际配对、声明方法或修正参考关系；旧报告和失败分母只读。该变体不生成 machine-specific correction、Recipe 修改、设备迁移动作或生产适用性批准。验收断言为：每个声明层均能从引用重算；相关性高而一致性界限不满足时仍返回不满足/不可评价；没有成对 agreement 证据时不能输出跨机一致性结论。

### 6.5 证据层分母与签署边界

接纳后先按 `EvidenceLevel` 分区，再执行任何 MSA、跨机比较或 Golden 汇总：`Synthetic` 和 `SoftwareReplay` 只能证明软件/方法或回放链路，不能进入真实计量或生产能力分母；`RecordedMeasurement` 与 `PhysicalMeasurement` 必须分别报告，返修、注入和合成来源也不得在未获批准的规则下混合。每层保留计划、有效、失败、未采集和排除计数；证据层不足以支持目标用途时返回结果及限制并标 `NotEvaluated`，不把层级提升为物理事实。

`EvidenceLevel` 是请求级，v0.2 一次请求只接纳一个层；混层输入为 `Rejected + QLF-INPUT-INVALID`，宿主分别提交后只读并列显示。返修/工程样件/注入/合成是来源类别，不是层级排序，必须在 plan 来源分层声明；缺来源不能推测为真实。对 Synthetic，EvidenceRefs 必须解析到生成器版本/hash、非空物理假设、随机化域/参数；seed 若生成器无随机性须显式标无随机性。SoftwareReplay 必须解析输入全集/运行/比较策略版本，seed 仅随机分支必需；不得要求确定性回放编造物理假设或随机种子。缺必要 provenance 记 `QLF-INPUT-INCOMPLETE`，相应用途 `NotEvaluated`；补齐后新计算，旧报告不变。重建一致性不提升物理证据层。

模块负责在固定输入、方法和数值后端下可重复计算并组装报告；质量、计量、客户或工艺 Owner 负责目标、阈值、样本充分性、用途判断和最终签署。报告完成、条件比较满足或所有软件案例通过，都不产生签署、放行、再认证或生产批准权；这些决定只能由外部 Owner 依据其批准的计划和真实证据作出。

## 7. Golden 与性能的实施步骤

### 7.1 Golden 证据消费

固定完整案例与各层分母 → 按精确引用读取既有 Replay 报告 → 校验运行/比较策略/环境/输入角色及全体案例关系 → 全外连接计划案例与实际结果 → 返回每例分类、差异/失败/拒绝和覆盖 → 组装带限制的报告。逐目标关联与图像/几何容差由原比较器合同负责，本模块不自动对齐/ICP消除偏位。

Golden 是回归基线而非天然真值。原机判、人工意见、参考赋值、合成预期和新算法输出分别标来源。双 Invalid 可满足预声明负例“应拒绝”断言，不能算正常测量准确。冻结100例仅95例一致时其余5例保留；无可比较例不记100%。每例只归一个汇总类别，重复运行和 seed 集另作层次，不增加独立物理 n。

预先冻结等价界、重复次数和选择规则；没有差异显著性不证明等价。训练/调参曝光和父样本分组检查由原数据治理报告提供；模块不新建标签/划分库。请求发布新基线由宿主提交原资产流程，不从本报告自动执行。

### 7.2 性能执行及归约

1. 校验 probe 的输入/输出角色、无设备/生产提交端口、真实完成屏障、线程和取消能力。对完整计划计数/内存/并发预算；固定 build/runtime/HALCON/AsunImage、OS/硬件、线程/provider、缓存及负载。性能或物理测量依赖硬件时，环境引用还必须能定位机台/板卡身份及固件、驱动和关键配置版本；模块只消费这些只读引用，不执行硬件资格或安全判定，缺失时相应比较为 `NotEvaluated`。依赖直接使用，不安排安装或授权核验。
2. 宿主按冷/热模式准备指定 worker 和只读输入；Prepare 和数据加载单独计时。不将数据准备、模型加载、排队或证据开销藏入“算法耗时”之外仍标整链结果。
3. 执行预热，预热统计另列；失败按预选策略处理，不多预热直到结果满意。MeasuredIterations 的所有计划序号先固定，后续失败/超时/未执行不删除。
4. 每次记录 ready/enqueued/start/actualCompletion 的单调 tick，阶段分开；probe Task 的完成必须表示其全部实际计算结束，启动GPU/native后立即返回的 Task 不合约。GPU等异步工作须公开完成栅栏，不能把提交时间当完成时间。
5. 探针分段：queue=start-enqueued、service=actualCompletion-start、probeElapsed=actualCompletion-ready。模块资格 endToEnd 唯一为 Accepted→ResourcesReleased，另列取消请求→Drained→ResourcesReleased；不能把 probeElapsed 标整模块端到端。每次探针实测保留自己的完成与资源归还时刻，外层模块请求也记录加载、报告和所有租约退出。ClosedLoop 下一次在前次真正完成/资源归还后执行；RecordedSchedule 固定到达点，未能派发按 NotExecuted 保留。
6. 完整排空的端到端样本（成功和失败分别带 outcome）按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md) 的公共统计口径归约；完整成功探针的分位是独立描述，绝不能据其判全负载。失败/超时/删失/未执行、最低有效样本数和排空未知均进入完整计划的判定，缺目标只为 NotEvaluated；不复制第二分位算法。
7. 吞吐为声明窗口内实际完成数量/真实elapsed，给成功/全部完成分别计数和剩余在途数。RecordedSchedule 的观察窗口必须按计划封口并排空；未排空仍是局部结果，不能宣称稳定最大容量。
8. 资源分别记录 managed retained/private/GPU bytes、句柄等支持指标、基线/采样峰值/排空后值、scope及采样期。高水位计数优先消费实际端口；仅轮询时标“采样峰值”，不宣称真正绝对峰值。Process 指标受其它负载影响时标受污染，需独占 worker 的条件不能据此通过。
9. 长稳按预定窗口/阶段、缓存容量/淘汰/重置点记录保持量与斜率，保存逐点证据及拟合方法；不自动强制GC或清缓存改变被测系统。Known leak注入由独立软件探针实现并单列故障试验，需验证资格工具能够判预算超限；不往客户进程注入。
10. 将结果与同环境/负载/范围/样本数要求的预定预算比较。没有所需次数、负载封口、资源指标或真实排空时 NotEvaluated；某一次失败保留完整失败依据。性能通过只表示该计划的条件满足，不授予光学/计量/现场资格。

## 8. 取消、超时、线程、排空与恢复

| 环节 | 必须执行的生命周期 |
|---|---|
| 接纳前 | 先校验令牌、剩余截止和额度；已取消不打开输入/运行 probe；Rejected 不取得资源 |
| 读数据/标量循环 | 每批≤1,024行检查取消/截止和实际预算；检查格/输出增长；执行不可拆数值调用前再次检查 |
| 数值/HALCON/probe执行 | 仅用已确认公开取消能力；没有内部取消的调用等真实退出；不能因 Task.WhenAny 超时就完成操作或归还内存/租约 |
| 取消/截止触发 | 记录原原因、停止新的行批/案例/probe派发；向已接纳任务传取消；保持在途额度/租约至实际结束 |
| 等待排空 | 外部 waitBudget 到期返回 StillDraining；不释放被访问数组/图像/模型/矩阵；诊断有 ActualWorkPending；操作 Task 尚未结束 |
| 实际退出 | 丢弃不能发布的迟到数值，保留计数/部分诊断；释放本操作取得的全部租约/缓冲/并发额度，固定 Terminal，返回 outcome |
| UI关闭/服务Dispose | 关闭UI撤订阅/释放显示资源；操作是否取消由持有运行的宿主决定。DisposeAsync等真实排空，不以关窗回滚已存证据 |
| 进程崩溃/重启 | 核心无持久状态；宿主读取原封存报告/执行证据，未封存计算记录为 Interrupted，新尝试保留 parent；不恢复半写报告当完成 |

Deadline 为接纳时固定的单调期限，UTC 仅供审计，系统时钟变化不延长期限。DeadlineExceeded 与真实工作结束是两事件；同一操作不得未排空即开放复用槽位。软件检查周期和行批大小不能证明native硬时限；不可中断后端时长须由实测可接纳规模限定，尚无实测就不承诺停止耗时上界。

默认单实例串行；不同实例可并行，但宿主统筹 CPU/native/GPU 额度。全局 HALCON `set_system`、数值 provider、线程数由宿主启动时固定，不由本模块每请求切换。两个实例“设置前后相同”不证明中途无人更改；缺运行环境稳定保证的分支只能给限制。依赖端口串行使用其可变句柄，官方算子 reentrant 不代表同一模型可以并发 apply/读结果。

报告返回的是受本模块持有的不可变值，不带须隐式 Dispose 的 native 对象；大明细由有界页/稳定引用表示，宿主存证前须保持依赖。报告导出/保存失败不改分析数值；核心没有 Commit。宿主保存回执 Unknown 时查原提交身份，以同身份重试保存，不能重新计算换键清除 Unknown；已提交证据不因取消撤回。

## 9. 资源和性能预算

下列是防止无界资源的软件候选默认，非工业样本要求或已测性能指标；正式实现接收时按真实后端验证，可降低。提高上限必须重新检查峰值/不可中断时长/消费者，不允许悄悄增大。资源预算进入计算身份与报告。

| 请求/实例预算 | 类型、范围、默认 | 拒绝/计账范围 |
|---|---|---|
| MaxRows | long，1..10,000,000，默认100,000 | 已读/计划行，重读遍数另计；实际超限不忽略尾行 |
| MaxCells | long，1..1,000,000，默认10,000 | 计划及实际格，a*b checked；不以稀疏行绕过格预算 |
| MaxDesignColumns / MaxCovarianceDimension | int，1..1,024，默认32 | QR、PSD及输出规模各核，不只核二次型 |
| MaxResidentBytes | long，≥1，默认256MiB，上限由宿主部署额度冻结 | 输入页/索引、均值/矩阵/work、返回明细、观察邮箱合计；开调用前按端口上界预留 |
| MaxReportDetailRows | long，0..1,000,000，默认10,000 | 摘要不缩分母；完整详情由稳定证据引用，不截明细后称范围缩小 |
| MaxInFlightPerInstance | int，首版固定1 | 同步/异步同账，无排队默认 |
| OperationDeadline | 可空 TimeSpan，指定时>0，最大24h；默认null | null不设时间期限，但仍受规模/内存额度；不是默认工作永不取消 |
| Stop waitBudget | TimeSpan，0..24h，默认由调用显式提供 | 0立即查排空状态；超时仍保留Completion/Owner |
| MaximumObservationSubscriptions | int，1..64，默认8 | 默认每邮箱256项、有限消息大小；超额度拒绝新订阅 |

复杂度预算：交叉/嵌套 SS 为两遍 O(N+ab)、汇总 O(ab+a+b)；单参考/中心化线性为O(N)，前提是可重读快照。设计薄QR约O(Np²)、工作区O(Np+p²)；秩谱/PSD另计O(p³)级时间及O(p²)空间。不可将单次 `cᵀΣc` 的O(p²)称为完整PSD验证成本。分位排序O(n log n)和duration/输出数组计入预算，probe本身耗时/峰值单独受声明能力限制。

性能验收先由消费者冻结真实 `PerformanceProfile`：负载/并发/样本数、各阶段P50/P95/P99、峰值及保留量、读取/返回、取消检查/真实排空。当前不填无来源ms值，不声称达标。首版性能预算不足不修改方法/精度/分母；拒绝该规模并给降低负载或适用分块的明确建议。分块仍保持原全体格、聚合顺序、数值策略和实际预算。

## 10. HALCON 26.05、AsunImage 与研究依据

已直接读取项目 `halcon算子手册/operators` 的 26.05.0.0 页面；以下是官方算子能力，非 `ImageLibDotNet` 方法声明。

| 核对项 | 能力与限制 | 本模块取舍 |
|---|---|---|
| [tuple_mean](../../../halcon算子手册/operators/tuple_mean.html)、[tuple_deviation](../../../halcon算子手册/operators/tuple_deviation.html) | 官方可求数值tuple均值/标准差；空tuple抛异常；读取页未给本研究需要的n-1/分组层级/完整ANOVA/相关预算合同 | 不凭同名替换045稳定M2/模型组合；若数值适配使用须证明分母/稳定性/误差域等价。资格核心不为标量事务强制转换HTuple |
| [apply_metrology_model](../../../halcon算子手册/operators/apply_metrology_model.html) | 26.05忽略输入image domain；尺寸变化重建测区会增加耗时；修改模型handle，同一handle跨线程必须同步 | 量测端口由原视觉模块优先经AsunImage提供，返回实际支持/失败/方法证据；qualification不重实现量测、不能据ROI缩domain证明范围限制 |
| [get_metrology_object_result](../../../halcon算子手册/operators/get_metrology_object_result.html) | 返回声明的几何/实例结果；读取官方结果角色 | 不把score/拟合参数当协方差或计量资格；公开桥生命周期由量测适配负责 |
| [count_seconds](../../../halcon算子手册/operators/count_seconds.html) | 时间差以秒表达，clock_mode可配置；官方明确受负载影响、不精确 | 外部基准使用统一Stopwatch单调tick+Frequency，保留时间分辨率；不由模块改变clock_mode或把CPU时间混成wall latency |

`ImageLibDotNet` 公共调用证据来自只读 AsunControl 消费者，例如 `Vision_Aligment2D_NCCModel/C_NccModel.cs` 的 `cv2.*` operator 调用、CancellationToken/IProgress/Stopwatch/finally释放，以及 `Vision_CameraCalib/Control_CameraCalibration.cs` 的核心/控件分离。实际大小写/重载按目标程序集公开调用/编译核对，本页不从HALCON .NET示例猜大小写或重载签名，不新增直接halcondotnet依赖，不扫描/修改AsunImage内部。AsunControl是.NET 8 WinForms来源，不自动迁移其宿主、参数或事件bool语义；本页不提供未经目标26.05核实的wrapper代码。

| 已有只读来源 | 本轮使用和限制 |
|---|---|
| [PKG-055](../../shared-modules/packages/PKG-055_Qualification.md) 0.2.2-prep；[DEV-MET-033](<../../shared-modules/guidance/04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md>) §6～15 | 试验模型、证书/报告/决定分离、共同误差和失败反例；不迁入其制程消费者逻辑 |
| [PKG-045](../../shared-modules/packages/PKG-045_Statistics.md) §7.5～7.7；[FS-018](../../shared-modules/guidance/12-function-specs/FS-018_Uncertainty_budget.md) | 四参数键保留；数值/尾支持域、不具内部取消的限制；实际数值API/政策以A.3.1及statistics唯一指导为准，旧候选不重新选后端 |
| [DEV-QLF-070](<../../shared-modules/guidance/08-qualification/DEV-QLF-070_Golden Sample与Replay开发指导.md>) §7；[DEV-QLF-071](<../../shared-modules/guidance/08-qualification/DEV-QLF-071_Performance Benchmark与容量资格开发指导.md>)；[DEV-QLF-072](<../../shared-modules/guidance/08-qualification/DEV-QLF-072_HIL、故障恢复与长稳开发指导.md>)；[DEV-QLF-073](<../../shared-modules/guidance/08-qualification/DEV-QLF-073_视觉/计量Qualification与GR&R开发指导.md>)；[DEV-QLF-074](<../../shared-modules/guidance/08-qualification/DEV-QLF-074_产品Acceptance与Production Gate开发指导.md>) | 冻结基线、性能分段、恢复与接受的分层；不将HIL/放行状态作为本核心线性生命周期 |
| [原Contract采纳约束](../../13-contract-candidates/CONTRACT-CANDIDATES.md#qualification-contract-semantics) | 输入身份/量名/SS/df/尾/证书投影、终态与排空、Owner分离；本页候选须串行映射 |
| [源性能Schema](../../references/project-snapshots/PCBA-AOI/20260927/original/contracts/v1/schema/performance-profile.schema.json)、[源参考证书Schema](../../references/project-snapshots/PCBA-AOI/20260927/original/contracts/v1/schema/metrology-reference-certificate.schema.json)、[源硬件资格Schema](../../references/project-snapshots/PCBA-AOI/20260927/original/contracts/v1/schema/hardware-qualification-profile.schema.json) | 只读历史结构；借鉴精确环境/build/阶段/证书字段，不搬入特定板件负载、强制有效期、Approved、签名规范或设备安全动作。JSON结构合法不能证明实物/信任/用途 |
| NIST测量过程手册[重复性](https://www.itl.nist.gov/div898/handbook/mpc/section4/mpc441.htm)、[线性](https://www.itl.nist.gov/div898/handbook/mpc/section4/mpc452.htm)、[相关不确定度](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-5-combined-standard-uncertainty)；已有2026-09-29原件 | 自由度/假设/覆盖与相关性，不移植案例样本数或把日模型当交叉模型 |
| SciPy 1.16.2，commit `b1296b9b4393e251511fe8fdd3e58c22a1124899`，[回归源码](https://github.com/scipy/scipy/blob/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/stats/_stats_py.py)、[TestRegression](https://github.com/scipy/scipy/blob/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/stats/tests/test_stats.py) | 复用既有固定源码/测试研究并定向读实际测试；借鉴大偏置/同x/空值/两点反例，不能照搬两点零stderr为资格。不引入Python运行时或称上游测试已跑 |
| Math.NET Numerics 5.0.0，commit `4435308e1b0efcb40dc483140059a4e3a2204044`；Boost.Math 1.88.0，commit `529f3a759d83aa9437613666ea6293c9336d4069` | 复用045已记录实际源码/测试研究，受限数值端口候选；累计/QR/PSD/尾后端不由本页重新选为生产依赖；不声称本轮重跑或完整新审 |

附加来源已定向读取：[pyCompare v1.5.4](https://github.com/jaketmp/pyCompare/tree/436a26d5e7f105927a1d7d12cb4a9d8525b7f9c7)，commit `436a26d5e7f105927a1d7d12cb4a9d8525b7f9c7`，MIT；依赖numpy≥1.18.1、scipy≥1、matplotlib≥3，测试依赖pandas。实际读plotBlandAltman、CI、detrend和tests：借鉴均值差/LoA与其CI的区分；其ddof=0、未固定随机seed、去趋势改变原数据、图存在测试和mock CI不能作为本模块计量/数值正确性证据，不复制为生产算法。[Giavarina 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4470095/)用于配对差值/一致性限的解释，不能把LoA当bias CI或相关性资格。已读 [.NET 10 Task.WaitAsync](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.waitasync?view=net-10.0)：等待包装取消/超时不证明原Task或native退出，故本页由Root持有原工作及真实释放屏障。

Benchmark新范围复用DEV-QLF-071/DEV-PLT-014已有负载/分段/冷热方法；本轮实际读取.NET 10公开说明 [WorkingSet64](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.process.workingset64?view=net-10.0)、[GC.GetTotalMemory](https://learn.microsoft.com/en-us/dotnet/api/system.gc.gettotalmemory?view=net-10.0)、[PeriodicTimer.WaitForNextTickAsync](https://learn.microsoft.com/en-us/dotnet/api/system.threading.periodictimer.waitfornexttickasync?view=net-10.0)。WorkingSet需Refresh且含共享/私有物理页，GC.GetTotalMemory(false)排除碎片且不强制GC；timer只允许一个consumer并合并ticks，取消单次wait不停止timer。另实读dotnet/runtime v10.0.0固定commit `60629d14374c56f1cb51819049ad1fa529307f8d`（MIT，无新增部署依赖）的 [Stopwatch源码](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Private.CoreLib/src/System/Diagnostics/Stopwatch.cs)、[Stopwatch测试](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Runtime/tests/System.Runtime.Extensions.Tests/System/Diagnostics/Stopwatch.cs)、[PeriodicTimer源码](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Private.CoreLib/src/System/Threading/PeriodicTimer.cs)与[测试](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Runtime/tests/System.Runtime.Tests/System/Threading/PeriodicTimerTests.cs)：借鉴Frequency/raw tick与Dispose/取消/重复等待边界，测试中的sleep重试仅用于runtime自身不作客户时限证据；未运行上游测试、不复制运行库，Stopwatch官方网页本轮DNS失败，以固定官方源码/测试为依据。采用BCL显式有限调度/资源原Task而不引入BenchmarkDotNet自动预热/过滤和宿主控制，使本模块计划分母及Owner可见；不以本次文档研究声称backend硬实时或峰值覆盖。

版本/许可证追溯沿既有来源：SciPy为BSD-3-Clause，声明Python≥3.11、NumPy≥1.25.2且<2.6及编译工具；Math.NET为MIT，工程声明多个.NET目标与测试依赖；Boost为Boost Software License 1.0。实际引用/源码复制保留对应通知；本轮仅研究，不安装这些后端，也不作AsunImage/DevExpress授权或版本准入审查。数值端口决定实际部署依赖并记录其完整构建来源，候选源码的许可证不能代替未来native二进制说明。

## 11. 可选 UI、语言和操作契约

控件只在有实际研究用户时开发，角色为试验配置者/分析查看者；采集与审批命令由宿主提供。紧凑工作流：计划格/缺口 → 原观察与参考来源 → 方法/假设 → 结果/残差/限制 → 返回报告。核心可无控件完整调用，不从隐藏窗口取语言或初始化模型。

控件输入只读请求/报告、局部主题/语言/格式上下文、命令能力及取消作用域；输出为选中证据、计划编辑草稿、显式发起分析意图和取消本控件持有操作意图。控件不直接持久化、不签发、不批准基线、不启动采集、无“一键合格”。图表选中/过滤/抽稀不能改变报告分母，显示位数不能更改计算值。

### 11.1 研究任务与紧凑布局

U1 是可选可嵌入控件，规格完整，真实WPF资格另门；不在当前文档任务创建控件工程。研究用户进入后默认看到冻结试验身份、计划/实际/失败数和原报告，按“检查缺口→查看参考→核方法→计算→查看限制→返回报告”完成任务。标题只用“资格分析 / 資格分析 / Qualification analysis”。没有批准/认证/一键放行命令。

1920×1080物理屏幕验证扣任务栏/外框；控件按宿主可用DIP布局，不能把屏幕像素当DIP硬写固定窗宽。顶栏48DIP含身份、方法、计算/取消/刷新状态；底栏28DIP含阶段、失败数和真实排空。中央 `DockLayoutManager + LayoutGroup + LayoutPanel`：左计划/观察 Grid 约52%，中 Chart约30%，右证书/参数/限制18%；右栏默认320DIP，可折叠，关闭图表后列表扩展，拖停靠只能改投影。Docking只在中央，关键命令不能被停靠隐藏或浮出屏幕。中心宽<1000DIP时图表改为下方36%高度、来源变Tab；<700DIP时列表/图/来源为同一 `TabbedGroup`，顶栏命令换行而非挤没。这只是同屏幕内宿主布局适应，不新增分辨率测试矩阵。

Grid用 `GridControl`/`TableView`，`ItemsSource` 接预备好的有界行、`SelectedItem` 保持 ObservationId/CaseId 选择；列为层/格/观察/来源/值与单位/结果/原因/时间，数值右对齐，身份路径按需展开。失败为图标+自然文字，颜色不单独承载意义；计划缺口、原负分量和边界估计并列，不显示绿色总体认证灯。Grid筛选/排序只作用 View；上方完整分母固定，筛选显示“显示n / 全部N”。双击/Enter定位原证据引用，不自动开文件或触发采集。

图表用 `ChartControl + XYDiagram2D + PointSeries2D/LineSeries2D`：Bias显示差值/参考，稳定性显示实际UTC时间和条件分隔，GRR显示具名分量/原负值，跨机显示pair mean/difference和LoA，性能显示阶段分布/资源时间序列。Chart点与Grid通过稳定ID双向选择，选一组时突出同层并显示单位、来源和失败；禁止 Chart 默认拟合/趋势线重算报告。空/不可用项不画0点，取消/Partial用已封存范围，不补全曲线。一次预览最多10000行、图最多2000点，确定性按时间桶取首末、min/max并保留异常标识；超出时分页/按层选择，不能丢失败后还声称全部可见。参数 `PropertyGridControl.SelectedObject` 只绑定本次局部草稿或只读报告对象，已接受方法/阈值锁定；高级参数渐进展开，变更形成新revision并重新校验。

主题来自宿主局部上下文，8DIP网格、正文14DIP、数值等宽、卡片标题16DIP；只在页切换/停靠用≤150ms轻动效，禁用无限闪烁或演示动画。BarItem.SuperTip用本机已核验 `SuperTip/ SuperTipItem` 给出单位/方法限制/恢复，关键失败原因直接显示在行与底栏。重绘合并进度≤10Hz，终态/错误立即呈现；UI线程只投影有界页，不读取证书、不做数值/图像运算。预览内存计入RootLimits，不让虚拟化掩盖底层全量复制。

### 11.2 Session、权限、命令和 Unbind

WPF namespace为 `Asun.Modules.Qualification.Wpf`。公开QualificationControl无业务构造副作用；Bind(session)在同Dispatcher返回Binding，重复绑定拒绝QLF-UI-BOUND。Session的唯一字段见A.4，包含显式RootReservation；UiContext局部locale/culture/theme/preview容量，Permissions具备Read/Edit/Analyze/CancelOwn/OpenEvidence、Epoch、ExpiresUtc。无Read/过期不复制敏感内容；每命令核原Epoch，撤权清预览/禁命令，不改原生产/计算结果；是否取消原operation由宿主显式决定。

Binding公开 `UpdateRequest(QualificationRequest,long revision)`、`UpdateReport(QualificationReport,long revision)`、`SetContext(UiContext)`、`SetPermissions(UiPermissions)`，同Dispatcher、单调revision，晚到/另一Instance忽略并记诊断；UpdateRequest只在无本Binding在途时接受，不接管旧请求。`Task<UiUnbindReceipt> UnbindAsync(TimeSpan waitBudget,CancellationToken waitToken)` 与 `IAsyncDisposable.DisposeAsync()`：先停止新命令/撤事件订阅/丢Dispatcher晚到投影，再等预览租约归还；超时返回UnbindPending及原Completion，根强持，不能释放仍被后台使用的数组。Unbind不等于Cancel、Service.Dispose或资源排空；需要Cancel先显式发本Binding操作意图。Session/Binding不是生产Owner。

UI入口、Session、四个意图及回执的唯一完整签名见A.4；每个命令都有发送前固定的IntentId和PermissionEpoch。HandleAsync只接纳意图，不能把Accepted当分析成功；原Service Task仍为结果权威。Unknown使用 QueryIntentAsync(UiIntentQuery(SessionId,Revision,IntentId),waitToken) 查原身份，不新建ArtifactRef、不借ReturnReport替代查询、不重新Analyze；Root登记Host原Task和晚到结果。

Tab焦点顺序为身份→方法→计算→取消→Grid→Chart→来源→恢复；F5刷新原回执，Ctrl+Enter计算（权限与校验满足），Esc只取消本Binding持有的分析，键盘选择Chart点可Enter跳Grid行。隐藏状态不吞焦点；错误优先定位字段，参考缺失显示“补齐参考信息 / 補齊參考資訊 / Complete reference data”，未知结果显示“查询原记录 / 查詢原記錄 / Query original record”，排空中显示“等待结束 / 等待結束 / Wait for completion”；三语资源键、占位符一致，不改任何业务值或请求hash。

两个STA Host规格：`QualificationStudyWindow` 使用独立标准件请求+右侧参考；`QualificationReplayWindow` 使用另一个Root/Service+Golden/性能请求+原案例引用。两者各自 `[STAThread] Main` 创建 `Application`、自己的UiContext/权限/Session，Bind→执行正常/空/失败/撤权/取消→Unbind→根Close；全用公开类型，无产品Shell/VM/私表。测试窗不能改显示设置；窗口外框在1920×1080可用工作区内，三语/DPI长度、Chart/Grid双向选择、任务中关闭、旧Task晚到、Root移交后迟到资源均有断言。真实编译/窗口/UIA与两个Host运行未执行，U1保持PreparationIncomplete。

状态文字示例：`正在计算 / 正在計算 / Calculating`、`正在结束 / 正在結束 / Finishing`、`样本不足 / 樣本不足 / Insufficient samples`、`条件未满足 / 條件未滿足 / Criteria not met`、`未评价 / 未評估 / Not evaluated`、`参考信息不全 / 參考資訊不完整 / Reference incomplete`。错误用一句原因+一项恢复动作，如“缺少参考不确定度。补齐证书信息。”；不得用“智能认证”“完美结果”等措辞。

宿主通过 `QualificationUiSession.Context` 与 `QualificationBinding.SetContext(UiContext)` 切换语言，支持zh-CN/zh-TW/en-US并可扩展；不在模块重复放语言入口，不改进程CurrentCulture/线程文化或其它实例。语言只投影，数字解析按固定输入文化并显式转换到契约值；切语言不改请求/阈值/计算身份。验证只用固定1920×1080视口，扣除任务栏/标题/状态栏，覆盖三语、键盘焦点、UIA名称、参数错误定位及关闭时仍在排空；不改变用户显示设置。当前未做真实WPF验证。

## 12. 两个无 UI Host 与有限离栈恢复

本节为实施后应能编译的公开API调用例，当前仅文档；两请求/端口/Root独立，不假称现有工程已运行。构造helper的全部正文都在本节，无外部fixture生成器或产品对象。Fixture包含实际bytes，其内容hash通过A.5的公开Codec产生；Synthetic与Replay来源分开。调用方须先创建并持有RecoveryOwner，再创建Root；Root、任务、输入和晚到租约不以Host栈帧为唯一强引用。

```csharp
using System.Diagnostics;
using System.Text;
using Asun.Modules.Qualification;

static QualificationRequest CreateStudyRequest()
{
    var unit = new UnitId("um","L","1");
    var cells = new[] {
        new PlanCell("C1",new PhysicalSpecimenId("P1"),"S1",1,RepeatLevel.IndependentCapture,"","Bias.v1"),
        new PlanCell("C2",new PhysicalSpecimenId("P1"),"S1",2,RepeatLevel.IndependentCapture,"","Bias.v1"),
        new PlanCell("C3",new PhysicalSpecimenId("P1"),"S1",3,RepeatLevel.IndependentCapture,"","Bias.v1") };
    var pb = QualificationCodec.EncodePlanContent(cells,"f","r","a",3);
    var plan = new ExperimentPlan(QualificationCodec.ArtifactFromBytes("plan","study","1",pb),cells,"f","r","a",3);
    var rows = new[] {
        new Observation(new ObservationId("O1"),"C1",new PhysicalSpecimenId("P1"),"CAP1","","T1",
            new DateTimeOffset(2026,10,11,0,0,0,TimeSpan.Zero),RepeatLevel.IndependentCapture,
            new Measured(new QuantityValue(9,unit)),QualificationCodec.ArtifactFromBytes("e","1","1",Encoding.UTF8.GetBytes("image-1"))),
        new Observation(new ObservationId("O2"),"C2",new PhysicalSpecimenId("P1"),"CAP2","","T1",
            new DateTimeOffset(2026,10,11,0,0,1,TimeSpan.Zero),RepeatLevel.IndependentCapture,
            new Measured(new QuantityValue(10,unit)),QualificationCodec.ArtifactFromBytes("e","2","1",Encoding.UTF8.GetBytes("image-2"))),
        new Observation(new ObservationId("O3"),"C3",new PhysicalSpecimenId("P1"),"CAP3","","T1",
            new DateTimeOffset(2026,10,11,0,0,2,TimeSpan.Zero),RepeatLevel.IndependentCapture,
            new Measured(new QuantityValue(11,unit)),QualificationCodec.ArtifactFromBytes("e","3","1",Encoding.UTF8.GetBytes("image-3"))) };
    var ib = QualificationCodec.EncodeInputContent(plan,rows);
    var ir = QualificationCodec.ArtifactFromBytes("snapshot","study","1",ib);
    var reference = new ReferenceAssignment(
        QualificationCodec.ArtifactFromBytes("cert","test-reference","1",Encoding.UTF8.GetBytes("reference=10 um;synthetic")),
        new QuantityValue(10,unit),null,"","c","test-only");
    var provenance = QualificationCodec.ArtifactFromBytes("synthetic","v1","1",
        Encoding.UTF8.GetBytes("synthetic:v1;values=9,10,11 um;stable object;independent errors;no randomness"));
    return new QualificationRequest("0.2",new CalculationId("B01"),new ExperimentId("SB01"),
        new MethodRef("Bias.v1","1.0",
            QualificationCodec.ArtifactFromBytes("method","bias","1",Encoding.UTF8.GetBytes("bias-v1")),
            QualificationCodec.ArtifactFromBytes("numeric","policy","1",Encoding.UTF8.GetBytes("engineering-binary64-v1")),
            QualificationCodec.ArtifactFromBytes("backend","bias","1",Encoding.UTF8.GetBytes("fixture-bias-v1"))),
        new Scope("length","1",unit,"s","study","c"),
        new InputSnapshot(ir,3,ib.LongLength,ir.Sha256,rows,plan),EvidenceLevel.Synthetic,
        new ResourceBudget(100,100,32,8,1048576,TimeSpan.FromSeconds(30)),
        new DeadlinePolicy(TimeSpan.FromSeconds(30),TimeSpan.FromSeconds(2)),
        new BiasAnalysis(new BiasPlan(reference,null)),null,
        new[] {new AssumptionEvidence("synthetic","independent errors on stable object; no randomness",
            "Declared",new[] {provenance})},null,null);
}

static QualificationRequest CreateReplayRequest()
{
    var pb = QualificationCodec.EncodePlanContent(Array.Empty<PlanCell>(),"f","r","a",0);
    var plan = new ExperimentPlan(QualificationCodec.ArtifactFromBytes("plan","replay","1",pb),
        Array.Empty<PlanCell>(),"f","r","a",0);
    var ib = QualificationCodec.EncodeInputContent(plan,Array.Empty<Observation>());
    var ir = QualificationCodec.ArtifactFromBytes("snapshot","replay","1",ib);
    var cases = new[] {new GoldenCaseResult("C01","P01","Consistent","E","A")};
    var cb = QualificationCodec.EncodeCases(cases);
    var gp = new GoldenPlan("P01",QualificationCodec.ArtifactFromBytes("cases","r01","1",cb),
        QualificationCodec.ArtifactFromBytes("cmp","r01","1",Encoding.UTF8.GetBytes("exact-v1")),
        1,"PARENT","exact-v1","",cases);
    return new QualificationRequest("0.2",new CalculationId("G01"),new ExperimentId("RG01"),
        new MethodRef("Golden.v1","1.0",
            QualificationCodec.ArtifactFromBytes("method","golden","1",Encoding.UTF8.GetBytes("golden-exact-v1")),
            QualificationCodec.ArtifactFromBytes("numeric","policy","1",Encoding.UTF8.GetBytes("engineering-binary64-v1")),
            QualificationCodec.ArtifactFromBytes("backend","replay","1",Encoding.UTF8.GetBytes("fixture-replay-v1"))),
        new Scope("result","1",new UnitId("one","1","1"),"s","replay","c"),
        new InputSnapshot(ir,0,ib.LongLength,ir.Sha256,Array.Empty<Observation>(),plan),EvidenceLevel.SoftwareReplay,
        new ResourceBudget(100,100,32,8,1048576,TimeSpan.FromSeconds(30)),
        new DeadlinePolicy(TimeSpan.FromSeconds(30),TimeSpan.FromSeconds(2)),
        new GoldenAnalysis(gp),null,Array.Empty<AssumptionEvidence>(),null,null);
}

// Owner is constructed once by Main and held until process exit, not inside the operation scope.
static async Task<int> RunHostAsync(QualificationRecoveryOwner owner,bool replay,CancellationToken token)
{
    var rootId = replay ? "root-replay-01" : "root-study-01";
    QualificationRoot? root = null;
    RootReservation? reservation = null;
    QualificationOutcome? business = null;
    RootCloseResult? cleanup = null;
    string? businessError = null, cleanupError = null;
    int businessCode = 5, cleanupCode = 0;
    try
    {
        root = owner.CreateRoot(rootId,new RootLimits(8388608,1,4,32,16,TimeSpan.FromSeconds(2)));
        reservation = root.Reserve(replay ? "replay-01" : "study-01",8388608,1,32,16);
        var request = replay ? CreateReplayRequest() : CreateStudyRequest();
        root.RetainInput(reservation,request);
        var gp = (request.Analysis as GoldenAnalysis)?.Plan;
        var ports = new QualificationFactoryPorts(
            new TestNumericsPort(TestNumericVector.BiasQ01,TimeSpan.Zero,false),
            new TestLedgerPort("ConfirmedAccepted"),null,
            gp is null ? null : new TestReplayPort(gp.CaseManifest),null,null,null,null,null,null);
        var service = QualificationFactory.Create(root,reservation,ports);
        var validation = service.ValidateDesign(request);
        if (!validation.CanAnalyze) { businessCode=2; businessError="design-rejected"; }
        else
        {
            var operationCancel=CancellationTokenSource.CreateLinkedTokenSource(token);
            root.RegisterCancellation(reservation,operationCancel);
            Task<QualificationOutcome> original = root.StartOwned(reservation,"analyze",() => replay
                ? service.EvaluateGoldenAsync(new GoldenRequest(request,gp!),operationCancel.Token)
                : service.AnalyzeAsync(request,operationCancel.Token));
            try { business = await original.WaitAsync(TimeSpan.FromSeconds(30),token); }
            catch (TimeoutException) { businessCode=7; businessError="host-wait-timeout"; }
            catch (OperationCanceledException) { businessCode=4; businessError="host-wait-cancelled"; }
            if (business is not null) businessCode = TerminalExitCode(business.Terminal);
        }
    }
    catch (OperationCanceledException) { businessCode=4; businessError="cancelled-before-admission"; }
    catch (Exception e) { businessCode=5; businessError=e.GetType().Name; }
    finally
    {
        if (root is not null) {
        // Close starts/cancels/drains registered work itself; no nested fresh cleanup budgets.
        try
        {
            Task<RootCloseResult> originalClose = root.CloseAsync(TimeSpan.FromSeconds(2),CancellationToken.None);
            // Close is a root control task: internally retained, never part of its own drain dependencies.
            try { cleanup=await originalClose.WaitAsync(TimeSpan.FromSeconds(2)); }
            catch (TimeoutException) { cleanupCode=6; cleanupError="cleanup-wait-timeout"; }
            if (cleanup is not null && !cleanup.Drained) cleanupCode=6;
        }
        catch (Exception e) { cleanupCode=6; cleanupError=e.GetType().Name; }
        owner.RecordHostCompletion(rootId,new HostCompletion(replay ? "G01" : "B01",business,businessError,
            cleanup,cleanupError,businessCode,cleanupCode));
        } // no registered root means CreateRoot failed atomically; business failure remains nonzero
    }
    return cleanupCode != 0 ? cleanupCode : businessCode; // only return, after cleanup
}

static int TerminalExitCode(OperationTerminal terminal) => terminal switch {
    OperationTerminal.Completed => 0,
    OperationTerminal.Cancelled => 4,
    OperationTerminal.Failed => 5,
    OperationTerminal.TimedOut => 7,
    _ => 3
};

// Two independent Exe entry points; each Main remains the process owner until actual exit.
static async Task<int> StudyMain(string[] args)
{
    var owner = new QualificationRecoveryOwner("study-process",2,64,32,16777216);
    int code = await RunHostAsync(owner,false,CancellationToken.None);
    try {
        if (owner.QueryRoot("root-study-01") is null) {GC.KeepAlive(owner); return code==0 ? 5 : code;}
        Task<RootCloseResult> recovery = owner.ObserveRootAsync("root-study-01",TimeSpan.FromSeconds(1),CancellationToken.None);
        var state=await recovery.WaitAsync(TimeSpan.FromSeconds(1));
        if (!state.Drained) code=6;
        else owner.AcknowledgeReleased("root-study-01");
    } catch (TimeoutException) { code=6; }
    catch { code=6; }
    GC.KeepAlive(owner);
    return code; // process exits; outer isolated harness enforces its finite process deadline
}
static async Task<int> ReplayMain(string[] args)
{
    var owner = new QualificationRecoveryOwner("replay-process",2,64,32,16777216);
    int code = await RunHostAsync(owner,true,CancellationToken.None);
    try {
        if (owner.QueryRoot("root-replay-01") is null) {GC.KeepAlive(owner); return code==0 ? 5 : code;}
        Task<RootCloseResult> recovery = owner.ObserveRootAsync("root-replay-01",TimeSpan.FromSeconds(1),CancellationToken.None);
        var state=await recovery.WaitAsync(TimeSpan.FromSeconds(1));
        if (!state.Drained) code=6;
        else owner.AcknowledgeReleased("root-replay-01");
    } catch (TimeoutException) { code=6; }
    catch { code=6; }
    GC.KeepAlive(owner);
    return code;
}
```

上述两个Exe各选一个Main为入口；上述Main中的Owner由程序生命周期持有，不能将局部Owner创建后也丢掉。CreateRoot原子失败时Main非零5，未登记Root不调用Observe/Close、不编造Drained摘要；已登记则两轴保存并继续观察。实际Exe固定为 `Main` 持有Owner局部并在软件隔离进程的有限外层截止内处理返回码；如返回6/7且Root未Drained，进程仍活着时调用 `owner.ObserveRootAsync(rootId,waitBudget,token)` 查询原Root。若需离开该Main任务但保持进程，**必须把Owner对象作为返回值/现有宿主字段移交给调用者**，不能返回裸int后让它失根。测试Main以非零退出交给外层隔离进程终止软件测试，不声称设备/native安全结束。

更长寿命监督者在Host调用之前显式创建。转交使用同一个TransferId：`offerTask=root.BeginTransferAsync(id,target,waitToken)`（原Task先登记）→`target.AcceptTransferAsync(offer,waitToken)`→核receipt的RootId、TransferId、ConfirmedOwnerId和ResourcesOwned；未确认源Owner保持原Root、全部槽、输入、原Task和晚到租约。超时/Unknown只查 `root.QueryTransferAsync(id,...)` / `target.QueryTransferAsync(id,...)`；不建另一个offer。目标容量先预约，原子变更currentOwner后才允许源释放；重复Accepted返回原receipt；Query NotFound不证明工作已结束。Root的所有迟到LeaseId只由已确认currentOwner串行Dispose一次。转交对象是同进程引用，不序列化Task/native资源；跨进程只保存身份查询，不能把进程内资源假转交。以下公开签名支持恢复：

```csharp
static async Task<TransferReceipt?> TransferRootAsync(QualificationRoot root,
    RootReservation reservation,QualificationRecoveryOwner target,string transferId)
{
    Task<TransferOffer> offerTask = root.BeginTransferAsync(transferId,target,CancellationToken.None);
    root.RegisterTask(reservation,"transfer-offer-"+transferId,offerTask,RootTaskRole.ControlWait);
    try {
        TransferOffer offer = await offerTask.WaitAsync(TimeSpan.FromSeconds(1));
        Task<TransferReceipt> acceptTask = target.AcceptTransferAsync(offer,CancellationToken.None);
        root.RegisterTask(reservation,"transfer-accept-"+transferId,acceptTask,RootTaskRole.ControlWait);
        return await acceptTask.WaitAsync(TimeSpan.FromSeconds(1));
    }
    catch (TimeoutException) {
        Task<TransferReceipt> query = root.QueryTransferAsync(transferId,CancellationToken.None);
        root.RegisterTask(reservation,"transfer-query-"+transferId,query,RootTaskRole.ControlWait);
        try { return await query.WaitAsync(TimeSpan.FromSeconds(1)); }
        catch (TimeoutException) { return null; } // source RecoveryOwner still owns root
    }
}
```

Fixture port构造固定为 `TestNumericsPort(TestNumericVector vector,TimeSpan delay,bool drainLate)`、`TestLedgerPort(string admissionState)`、`TestReplayPort(IReadOnlyList<GoldenCaseResult> cases)`，TestNumericVector仅有BiasQ01枚举值。BiasQ01接受MethodId=Bias.v1、三个差值[-1,0,1]，给n=3/mean=0/M2=2；其他输入返回Unsupported，不能给任意数组同一结果。这是**编排oracle**，真实计算正确性由statistics后端解析向量另验；Core不得实现第二统计累计器。`ConfirmedAccepted`、`AdmissionUnknown`、`ConfirmedAbsent`、`Duplicate`、`Conflict`为ledger固定状态，Unknown不派发数值/probe，按原CalculationId+RequestSha256查询；确认Absent只返回拒绝，不自动再次接纳。TestReplayPort核原manifest hash/完整身份，不能现场改expected。

| case（两Host各自执行） | 输入或交错 | 业务断言 | Owner/cleanup断言 |
|---|---|---|---|
| 正常 | 两个原请求 | Study bias=0、sample variance=1、随机SE=sqrt(1/3)、Criteria=NotEvaluated；Replay N=1/Consistent=1、RequestSha256=A.5.1 | businessCode=0且cleanupCode=0才退出0 |
| 接纳前非法/预算满 | Count异实际、resident预约不足、预取消 | 2/5/4，不执行数值/Replay/probe | Factory之前已Root登记；无reservation时Close仍可处理空根，不假成功 |
| 运行失败 | Numeric/Replay抛指定测试异常 | 5（Failed），保留原异常类型/阶段 | 原Task登记，finally必执行；不能用cleanup异常抹业务字段 |
| Cancel/业务截止 | 可控制闩锁卡Read/Compute/Report，取消或30s等待截止 | 4/7，原Analyze仍在Root中；终态只在真实释放后 | Close总2s，Unknown=6，槽不返还 |
| AdmissionUnknown | ledger在接纳响应丢失 | 零次派发，查原身份，Unknown记录保持 | 查询/迟到ledger Task与CTS均Root强持，不重提交 |
| 迟到租约/转交Unknown | Close后才返回LeaseId；Accept响应丢失 | business字段不变 | 源强持直到Accepted确认；目标满拒绝；重复LeaseId只Dispose一次 |
| UI关闭后继续恢复 | U1 UnbindPending后退出原窗口任务 | 不暗取消另一消费者 | 恢复Owner还在，按原root/intent/transfer查询，不能从控件重建结果 |


## 13. 正常、边界、失败案例与第二消费者

所有数值例为设计验证向量，不是工业样本量、接受阈值或已执行产品结果。

| ID | 输入/事件 | 可判定期望 |
|---|---|---|
| Q01 | 参考10，独立观测9/10/11，同单位，点估计 | bias=0、s²=1、随机标准误sqrt(1/3)；无接受条件NotEvaluated |
| Q02 | n=1；或三行复制同CaptureId | 前者仅差值；后者不增物理n，保留重复诊断，不给物理重复性通过 |
| Q03 | 交叉2×2×2，`y=100+4p+2o+p*o+e`，p/o/e各±1，唯一观察身份 | SS_P/O/PO/E=128/32/8/8，df=1/1/1/4；ve/vpo/vo/vp=2/3/6/30，vGRR=11、vTotal=41 |
| Q04 | Q03去交互项；预声明截断 | vpo_raw=-1始终保留，采用vpo=0；vGRR=10。RawOnly不自动产生截断汇总，不改模型池化 |
| Q05 | Q03缺一观察或重复身份补格 | 缺格/重复明确，不能产完整平衡GRR；所有原失败保留 |
| Q06 | 嵌套b=a=r=2，`y=100+4o+2p(o)+e` | SS_O/P(O)/E=128/32/8，df=1/2/4，vo/vp/ve=28/7/2；不估交叉交互 |
| Q07 | x=0/1/2各两次，差值(0,2)/(1,3)/(4,6) | x0=1、alpha0=8/3、beta=2；PE=6、LOF=4/3、SSE=22/3 |
| Q08 | 两点/同x/设备列等时间列 | 无残差df/零Sxx/不可识别分别说明，不用stderr0或伪逆授资格 |
| Q09 | 4次独立随机σ=2µm，共同参考u=3µm，平均值预算 | uc²=4/4+9=10µm²；不把共同项分成四份 |
| Q10 | u1=u2=2µm，ρ=1；或ρ=2；或3×3对角1、非对角-.9 | 单一共同项的和/差u=4/0µm；ρ=2非法；3×3逐对合法但整体PSD非法，不能截负修复 |
| Q11 | µm改mm；大常数偏置小散布 | 均值/σ除1000、SS/方差除1e6，比例不变；数值稳定性按冻结误差政策核验，不擅用绝对1e-6 |
| Q12 | 证书U有值而k未知/过期历史用于新用途/实物不同 | 不猜k/有效期，不授新用途；可保留历史参考解释及来源缺口 |
| Q13 | 100个Golden案例95一致、2变化、1不可比、2失败 | 总分母100，每类保留；双Invalid预期拒绝不记正常测量准确；不取最好重复 |
| Q14 | latency序列1..100ms，全部完成 | nearest-rank P50=50、P95=95、P99=99ms，附n=100与模式；不能当可信尾区间 |
| Q15 | 99次1ms成功+1次超时未退native | 成功分位附n=99，计划N=100且失败保留；StillDraining保持槽/租约，不能判整体预算满足 |
| Q16 | n=0成功项、采样不可用、只有预热或未封口 | 分位/资源/吞吐相应NotEvaluated，不写0ms/0bytes/完整通过 |
| Q17 | A取消/超时、旧A事件晚到，新B语言不同 | B参数/结果/语言不变；A实际退完才释放；终态一次，迟到A不盖B |
| Q18 | 保存响应丢失/导出磁盘满/报告输入更正 | 查原提交回执；导出失败不改分析；更正新引用/新计算关联旧报告 |
| Q19 | 被测probe先返回Task后native继续/Process指标有别的负载 | ProbeContract拒绝该完成语义并等待Owner实际排空；污染指标不能用于独占资格通过 |
| Q20 | 订阅者抛异常、同步阻塞、超过邮箱额度 | 核心不等回调，断开并记诊断；操作继续，最终状态可查，另一订阅/实例不受影响 |

第二消费者契约验证使用同一个包而非复制核心：

| 消费者 | 实际规划链 | 核心不承担的内容 | 接收断言 |
|---|---|---|---|
| 标准件/MSA独立工具（第一消费者） | 物理件独立重采→原量测→只读标量/证书投影→同一Analyze→宿主存证 | 实物/参考检查、采集/装夹、方法和用途审批 | Q01/Q03/Q05/Q09/Q12、取消及单位转换；无WPF可完成 |
| 独立光学尺寸测量工具（第二视觉项目规划消费者） | 宿主提供自己的量名/单位/参考/方法→同一偏差或GRR核心→返回报告给其计量流程 | 目标关联、被测量/光学/量程含义和质量放行 | 只写适配器而不改Core；正常/缺项/未知参考/取消/报告接收全链，无私表/产品VM引用 |
| Golden/算法基准工具（补充真实规划消费者） | 固定Replay差异→同一Golden报告；或独立probe→Benchmark→宿主归档 | 原图编排、Golden批准、算法/后端选择、设备动作 | Q13～Q20，同包在无UI服务进程运行；资源和负载显式 |

当前未运行上述宿主，不以规划名称冒称已有接入。两个不同配置文件不是第二消费者；须至少两个独立宿主/视觉项目用各自适配输入、同一发布包、正常/失败/取消路径证明边界。若可选控件发布，再由两个WPF宿主注入不同局部语言和主题验证，不改核心。

## 14. 测试、可观测性和发布回退

### 14.1 实施测试矩阵

| 范围 | 必测输入/交错 | 验收证据与边界 |
|---|---|---|
| 契约/序列化 | union错变体、未知版本/枚举、单位/ID冲突、checked溢出、非法有限值、未知字段语义 | 契约测试；拒绝错误可定位。未知必要语义不能忽略后继续 |
| 计量组合 | Q01～Q12及输入排列、单位转换、恒等式/df、大偏置/近退化 | 独立有理/高精度或解析参考对照；实际数值端口测试另验，不镜像实现自证 |
| 真实数值后端 | t/F尾/端点/表示损失、df顺序、秩亏/近共线、PSD反例、provider稳定与不可中断 | statistics适配验证；不把数学端点和有限观测舍入0混合，不声称本页验证后端 |
| Golden | Q13、案例缺失/重复、父组泄漏、训练曝光、拒绝断言、环境变化/未执行 | 与原Replay/Data治理契约接线，原基线/标签不变 |
| Benchmark | Q14～Q16/Q19、冷热、排队、GPU完成栅栏、已知泄漏、采样漏峰、并行污染 | 真实运行数据与完整分母；测试工具自校验与被测模块资格分开 |
| 并发/恢复 | Q17～Q20、取消每阶段、超时先后、Dispose等待、订阅堵塞、Busy/重复ID、崩溃 | 真实排空/租约归还/终态一次；Simulator仅软件验证，无设备命令/生产写入 |
| 宿主接入 | 两不同消费者、同步/异步、只读快照关闭、保存Unknown/更正影响 | 最小可编译无UI示例+实际接入测试，无产品Shell/VM/私表 |
| UI/语言（若发布） | 固定1920×1080、三语长文本/数字输入、键盘/UIA、晚到/关闭排空 | 真实WPF；HTML/截图不代替控件接入 |
| 物理/现场 | 实际稳定件、独立参考、环境/光学范围、真实采集层级、客户接受规范 | 原计量/质量Owner审定，核心软件测试和Replay不代替计量/生产通过 |

本轮是文档阶段，只核边界、方法/合同一致、步骤、案例、来源/链接和候选状态；不为证明进度新增产品测试、运行时依赖或性能数字。既有数学/研究证据可在其原版本/范围内复用，不能回标新接口运行通过。

### 14.2 可观测性

每操作至少记录实例/计算/实验/方法/输入摘要、证据层、阶段真实时间、计划与实际计数、数值backend/build/支持域、预算/峰值/在途、取消请求时刻/真正结束/排空耗时、诊断码和依赖引用。Activity关联同一计算，日志用稳定码及资源键；不记录受限制的图像/标签明文或证书敏感字段到通用日志。

报告保留实际观测时刻、分析时刻、外部决定发布时刻及适用起点分别；只有外部原Owner决定才有后两者。影响检查读取宿主提供的封口依赖清单，返回匹配证书/方法/标定变更的报告与依据；未提供完整索引就声明非穷尽，不自己建事实库或隐式执行撤销。进度/计数不作为质量批准证据。

### 14.3 版本、发布和回退

程序集/API采用SemVer，合同、算法方法、数值策略、单位词表、报告格式分别版本化。破坏单位/模型/失败/资源所有权、事件终态或尾概率语义是major变更；新增可忽略的诊断为minor但客户端需保留未知码；不能将必要前提改成可空且空等于已验证。旧结果按原版本解释，不根据新默认重算后覆盖。

适配器发布必须注明支持的源/目标合同、精确映射、原值/来源保留、未知字段与枚举行为和完整性限制；源历史Schema的Approved/签名/工件维度不迁为本核心权限。读取不支持报告版本返回明确Unsupported，保留原件供宿主；不通过丢字段维持表面兼容。

发布包包含实际DLL、公开契约与方法修订、依赖/实际build摘要、上述可编译无UI两消费者示例、必要契约/数值/并发/预算验证和变更说明；只使用本机既定AsunImage/DevExpress，不下载替换它们。纯标量Core不得因未装WPF启动失败；需要视觉probe的适配宿主按其明确依赖启动。

回退顺序：停止新接纳→等待真实排空→封存已完成/中断操作身份→宿主切回先前包与明确兼容的合同/方法→新计算引用旧版本。保留两版DLL/配置/输入/报告与可读取路径，不回写旧结果、不自动回退用途批准。重大契约迁移先验证两消费者再切换，失败沿原版本恢复，外部证据Unknown继续查原回执。

## 15. 外部接入门与本轮自审

以下事项是适配实现/实测后续门，不代替本页当前内部规格。数值桥已定部分见A.3.1，新增Benchmark内部规格已定部分见A.3.3；Deming确定桥指导本轮已限定接收，真实Adapter/能力与运行/数值资格仍PreparationIncomplete，后续实现须另行主控授权。不允许变成Core的临时算法选择：把 v0.2 端口映射到统计、Replay、参考件、数值和资源的实际公共程序集签名；真实后端容量与不可中断规模；两个独立宿主的接线；获批 WPF 的 DevExpress API/布局验收。物理稳定性/溯源、光学范围、实际独立采集、客户接受限及现场验收只阻断相应用途资格。

2026-10-04自审按下列断言完成文档检查；结论限本页设计候选，不是独立审核或产品测试：

- 核心只拥有计算/报告，不写生产判断、审批、工艺规则、设备命令、基线/证书/标签或事实Store；第二消费者无需平台私有类型。
- 四个既有参数键保持语义；置信/跨度/公差/接受线无行业默认；raw负估计、缺格、共同误差、尾数值失败和局部预算没有被成功布尔值掩盖。
- 同步/异步共享校验与方法；资源额度跨入口统一；等待取消/超时不等native退出；终态在实际排空和自有租约归还后固定。
- Golden比较器和数值库均经端口复用；量测优先AsunImage；本页未给猜测wrapper签名，没有把厂商类型泄漏到核心。
- 用途决定/签发撤销/保存回执仍由宿主Owner持有；UI只投影，语言/参数/取消跨实例隔离，设计预算明确为候选未实测。
- 状态保持DesignReview/Prep；未执行产品C#、HALCON/AsunImage、真实WPF、两个宿主、资源性能或物理/现场资格，不声称它们通过。

本页引用的来源与既有方法在 §10 可直接追溯，程序员执行需要的通用步骤/参数/异常/案例已写正文，无需依赖会话或临时脚本补规格。主会话审定独立接口及共享合同映射后才可进入对应实现切片。

## 16. 第二轮场景驱动架构复审（2026-10-04）

本节是对前述契约的反例审查，不是新的状态机、Schema 或生产批准。每个场景都必须能从冻结输入定位到一个结果、一个错误或一个排空中的明确状态；“函数返回”不等于原生工作结束，“计算完成”不等于方法适用或资格批准。下表中的参数来源只能来自请求快照、批准的 MethodRef/NumericPolicyRef、能力端口或宿主显式提供的证据引用；不从当前配置、UI显示值或运行时默认猜测。

### 16.1 关键场景闭环

| 场景 | 输入与参数来源 | 固定处理顺序 | 输出、状态和错误 | 恢复与可判定验收 |
|---|---|---|---|---|
| 正常配置与执行 | 封口的 ExperimentPlan、有限 Observation、Scope/Unit、ReferenceAssignment、MethodRef、NumericPolicyRef、预算；宿主提供证书/Replay/数值端口 | 接纳→校验版本/ID/量纲/计划格→读取完整快照→检查物理重复声明和方法前提→调用指定数值路线→交叉回核 SS/df/单位→生成报告→由宿主保存 | `Completed`；报告分别给计算完整性、方法适用性和条件比较；缺接受条件为 `NotEvaluated`；无生产放行状态 | Q01/Q03/Q07 可复算，输入顺序置换结果符合冻结数值容差；同一 CalculationId 不重复执行，报告引用完整输入 hash/方法/build |
| 空输入与部分成功 | 空 Observation、空 PlanCell、空证书字段、或固定计划中部分格 `Measured`、部分 `Failed/NotCollected`；不把空 tuple 当合法零样本 | 先检查空/未封口/缺页，再决定拒绝或允许局部描述；逐格保留失败原因；只对满足最小条件的子分析调用数值端口；计算后标缺口范围 | 空必需输入：`Rejected + QLF-INPUT-INCOMPLETE`；部分有效：`Completed + Partial`，缺格/分母/未执行显式；不能用0、空字符串或NaN代缺测 | Q02/Q05/Q16；读到8/预计10且读取中断不得冒称完整10条；重采或补采由宿主创建新 Observation/CalculationId，旧失败不删除 |
| 歧义与错误输入 | 重复 ObservationId/CaptureId、跨单位、物理件/Cell 冲突、未知方法/枚举、非法置信度、非有限值、错误证书实物关系、同一事件异内容 | 在获取大对象或原生句柄前执行结构→身份→单位→方法→资源预算校验；错误按 FieldPath/CellId 定位，不进入部分计算 | `Rejected`；分别使用 `QLF-INPUT-IDENTITY/QLF-INPUT-UNIT/QLF-REFERENCE-INCOMPLETE/QLF-METHOD-UNSUPPORTED`；不得返回看似有效的局部报告 | 修正快照或选择已批准方法后用新身份重试；Q08/Q10/Q12 断言错误不能通过截断、伪逆、默认k或默认95%消除 |
| 超大或高并发输入 | MaxRows/Cells/Columns/Covariance/ResidentBytes、订阅数、并行度、截止时间来自请求预算；多个实例共享宿主额度 | 接纳前 checked 乘法和上界估算→预留工作区→按≤1,024行检查点读取→按实例额度调度；不建立无界队列 | 预算不足：`Rejected + QLF-BUDGET-EXCEEDED`；在途满：`QLF-OP-BUSY`；队列/等待/服务/完成分别计时；不截断后标完整 | Q14/Q15/Q16；提高上限必须形成新 Method/计算身份并重测峰值；两个实例不得共享累加器、句柄、语言或取消状态 |
| 噪声、遮挡与退化视觉证据 | 量测适配器提供固定 frame/ROI/calibration/model revision、图像质量/有效支持、失败对象和 `EvidenceLevel`；遮挡/饱和/低对比原因来自原视觉模块 | 先确认图像尺寸/坐标/标定与模型快照→执行量测→逐对象读取 result 与 measure samples→检查 finite/cardinality/support→复制成标量证据→再进入 MSA/Golden | 缺边、歧义拟合、越界、非有限、支持不足为逐对象 `Invalid/Unavailable`，整体可为 `Partial`；HALCON score/拟合残差不转协方差/质量放行 | 主视觉路线失败只允许按批准的备用路线重新计算同一输入并显式标变更；无备用资格则保留失败证据，不换ROI、不自动补洞、不把遮挡从分母删除；Q13/Q19 延续同样语义 |
| 取消、超时与 native 排空 | CancellationToken、Deadline、Stop waitBudget、端口可中断能力和不可中断规模均来自请求/能力快照 | 接纳前检查取消→每批/每阶段检查→向已确认可取消端口发取消→停止新派发→等待原生真实退出→释放本操作租约/槽位→固定终态 | 触发原因记录为 `QLF-OP-CANCELLED` 或 `QLF-OP-TIMEOUT`；未排空只能 `StillDraining`，操作 Task 不完成、槽位不复用；迟到结果丢弃但诊断保留 | Q15/Q17/Q19；`Task.WhenAny`、窗口关闭或等待超时不等于 native 停止；真实排空后才可重试，新计算保留 parent 和失败尝试 |
| 资源上限与长期运行 | MaxResidentBytes、句柄/缓存/邮箱、采样周期、长稳窗口、斜率规则、重置/淘汰点来自 BenchmarkPlan/ResourceBudget | 预估→采样 baseline→执行预热与测量→按阶段采样→排空后采样→比较峰值/保持量/斜率；不强制 GC/清缓存掩盖泄漏 | 超限 `QLF-BUDGET-EXCEEDED` 或资源不可观测 `QLF-RESOURCE-UNAVAILABLE`；采样峰值标注为采样峰值；性能报告与计量报告分开 | 长稳必须覆盖冷/热、缓存命中、取消/异常/重启边界；发生正斜率或泄漏注入失败保留全部窗口，不能只取稳定前缀或重置后数据通过 |
| 持久化、回执未知与版本修订 | 报告/原输入/证据引用的 immutable snapshot、ContentSha256、Contract/Method/NumericPolicy/ReportSchema 版本；宿主持久化端口和 CommitId | 先完成计算并封存报告内容摘要→宿主提交→回执未知时按原 CommitId 查询→修订输入/方法/证书产生新 CalculationId/ReportRevision→建立 supersedes/impact 关系 | 保存失败不改报告；未知回执是 `CommitUnknown`（由宿主表达），不重算换键；旧报告只读；输入更正/证书撤销产生影响记录，不改原字节 | Q18；断电/重启后半写报告只能 `Interrupted`，不可当完成；同一 ContentSha256 可去重内容但不能合并物理件、批准决定或用途关系 |
| 升级与回退 | 新旧包、契约、方法、单位词表、数值 provider、报告版本及适配器映射都带 hash/支持范围；切换窗口由宿主控制 | 停止新接纳→排空→封存旧实例状态→兼容性检查→双消费者离线回放→切换→监控→必要时按同序回退 | 不支持版本 `QLF-METHOD-UNSUPPORTED`/`UnsupportedReportVersion`；回退不回写旧结果、不自动撤销/批准用途；新旧结果各按原版本解释 | 旧报告可读且数值/单位不变；迁移丢必要字段必须硬失败；升级后 Q01/Q03/Q13/Q14 在两个消费者保持同义，不能用新增可空字段伪造兼容 |
| 无 UI 调用 | 只读内存快照或封口 Reader、显式端口、CancellationToken、宿主诊断/存证回调；没有窗口/Dispatcher | `ValidateDesign`→`Analyze/AnalyzeAsync`→消费 outcome→宿主存证/查询回执→`StopAsync/DisposeAsync` | 同 UI 使用完全相同的校验、状态、错误、报告；无 UI 时事件无人订阅仍不影响结果；无隐藏窗口初始化 | 最小 console/service 宿主可在无 WPF 进程执行；断开订阅不改变计算；示例必须实际编译后才可标接入通过 |
| 可选 UI | 只读 Request/Report、宿主语言/主题上下文、有限命令能力；不传 native handle、不直接写 Store | 计划格/来源→方法/限制→结果/残差→显式取消或提交意图；Dispatcher 只投影，按 InstanceId/Revision 丢弃晚到 | UI 关闭撤订阅；运行是否取消由宿主决定；显示 `Partial/NotEvaluated/StillDraining` 原因，不显示“已认证”；`QLF-OBS-DETACHED` 不改操作 | 固定1920×1080、三语、键盘/UIA、390px窄布局和长文本不遮挡；图表筛选/抽稀不改分母；真实 WPF 未验收前保持 Prep |
| 第二消费者 | 不同视觉项目使用自己的 `Scope/TargetRef/Reference/Adapter`，只引用同一发布包和公开 Contract；禁止引用第一消费者 VM/私表 | 各自 Validate→同一 Core 路线→各自证据 Owner 保存；对同一失败输入保留同样的 Invalid/Unknown 语义 | 两消费者报告字段/错误/取消/版本语义相同，产品解释不同；任一消费者不能给另一消费者的结果加权或覆盖 | 第一消费者标准件/MSA 与第二消费者独立光学尺寸工具各完成正常、缺项、取消、升级/回退接入；没有两个真实宿主时仅记设计门，不记通过 |

### 16.2 具体算法路线、备用、训练和恢复条件

qualification 不训练视觉或统计模型。`Training` 在本模块的唯一语义是“无支持”：若调用方要求训练、在线更新、根据失败案例修改阈值或重建 Golden，返回 `QLF-METHOD-UNSUPPORTED`，由原模型/数据 Owner 另行治理；不得把“重算”命名为训练。确定性 MSA/GR&R/不确定度组合也没有随机训练阶段。

| 路线 | 主路线及处理步骤 | 备用/不支持条件 | 恢复条件与证据 |
|---|---|---|---|
| R1 标量 MSA | 宿主封口标量→`IQualificationNumerics` 稳定 n/mean/M2→按 MethodRef 计算 bias/线性/稳定性/GR&R→回核 SS/df/单位→报告 | 端口不提供所需模型、秩/尾/PSD域不足时只返回已计算点值和限制；不静默换正态、伪逆、加权或库 | 端口故障/取消后同快照新 CalculationId 重算；报告记录原 backend/build/顺序/方法身份和失败阶段 |
| R2 协方差预算 | 固定具名分量→单位/敏感度/相关组检查→`IQualificationNumerics` 对称/PSD→二次型→按声明覆盖方法输出 u/U | 相关未知、PSD非法、非线性/支持域变化或覆盖方法缺失时不输出总 uc/U；不以 GRR 负分量策略修协方差 | 修正分量/关系产生新 MethodRef 和报告 revision；旧预算只读，逐贡献/来源/单位保留 |
| R3 HALCON 26.05 2D 几何量测证据 | 量测适配器按固定 model 快照，经 ImageLibDotNet 的 cv2 operator set 调用已登记的 metrology operators（对象/参数以目标公开 C# 重载为准）→apply→读取 result 与 measures→复制 typed 结果/采样/失败为标量证据→释放适配器持有资源 | 同一公开 ImageLibDotNet 版本若缺某个 C# overload、模型尺寸/坐标/参数不匹配、对象结果缺失、遮挡/歧义或 native 不可中断：返回 QLF-METHOD-UNSUPPORTED/Invalid/StillDraining；不得改用另一个几何模型或把 score 当 u | 只在实际 C# 参数类型/重载或封送存在歧义时，按 HALCON 26.05 手册和 ImageLibDotNet 公共签名编译核实；不直接引用 HOperatorSet/halcondotnet.dll，不检查 wrapper 是否“包含算子”。模型 handle 在 apply/result 读取前独占，适配器按成功/异常/取消/超时路径释放资源；结果未复制前不得清 handle |
| R4 HALCON 标量描述备用 | 仅对已取得的有限标量使用 26.05 `tuple_mean`/`tuple_deviation`（官方空 tuple 抛异常），或已有数值端口做描述性 mean/deviation；输入/分母/稳定累计/分组语义仍由 R1 负责 | 不支持 n-1、分组、GR&R、协方差或请求的稳定误差域时只能作诊断投影，不能替换 R1 或形成资格结论；空 tuple 是拒绝/缺失，不是0 | 备用结果报告 `MethodRef=R4`、只读描述用途；R1能力恢复后新计算身份重跑，不能覆盖 R4历史 |
| R5 Golden/Replay | 消费既有 Replay 的封存全案例和比较器结果→校验案例身份/父组/环境/策略→全外连接分母→归类一致/变化/不可比/失败/未执行→报告 | 缺比较器/案例全集/父组隔离或策略不支持时不自行图像对齐、ICP、重分类、训练或补案例；无正例不能报100%召回 | 读取中断保留 partial 但不封存完整；数据/标签修订走原 Owner，新报告关联 supersedes，旧报告不改 |
| R6 性能 Benchmark | `BenchmarkPlan`→固定 worker/build/cache/并发→Prepare→预热→测量→实际完成栅栏→阶段/资源采样→排空→按 DEV-GOV-010 §3.1 统一统计并做容量比较 | probe Task 未代表 native 完成、资源指标被外部负载污染、失败/超时删失、样本不足时只给局部诊断/NotEvaluated；不以成功子集达标 | probe/资源端口失败保留尝试和排空证据；重跑必须新 RunId/CalculationId，不能挑最好窗口；泄漏注入由独立软件探针，非客户进程 |

### 16.3 持久化、升级和长期运行的边界结论

本模块是无持久事实写权的计算服务。可恢复的最小单元是“不可变输入快照引用 + CalculationId + MethodRef/NumericPolicyRef + 运行状态/诊断 + 已封存报告引用”；不是内存累加器、native handle 或 UI 草稿。宿主负责两阶段保存/回执查询，必须能区分 `Calculated`、`EvidenceSealed`、`CommitUnknown`、`Interrupted`；模块只返回计算结果和依赖关系，不能伪造提交状态。

版本兼容按四个独立维度检查：合同字段/状态、算法方法/参数、数值后端/表示、报告投影/单位词表。任一必要维度不兼容，旧结果仍可读但新用途阻断；迁移工具必须保留原字节、原 hash、原计算身份和转换日志。回退只切换新接纳版本，已完成报告继续按生成版本解释；正在排空的 native 工作不因回退强杀或释放。

长期运行接收条件是预定窗口、负载、资源指标和排空屏障均有证据；任何缓存/句柄/订阅/租约正增长、观察者拖慢计算、重启后无法区分半写报告或跨实例串身份，均为失败或 NotEvaluated。不能靠定时清缓存、强制 GC、重启进程或只保留成功记录掩盖泄漏。

### 16.4 第二轮架构结论与接收门

- **边界保持正确：** 模块只拥有实验设计校验、确定性计算编排、证据投影和性能分析；目标关联、制程解释、质量放行、设备命令、参考/Golden/报告事实 Owner 均在调用方或既有模块。
- **已补齐的可实施路线：** R1/R2 的标量计量与不确定度、R3 的 HALCON 26.05 量测证据主路线、R4 的受限标量备用、R5 Golden/Replay、R6 Benchmark；每条都有失败条件、恢复身份和不支持能力。
- **明确不支持：** 本模块不训练模型、不更新阈值、不创建 Golden/证书/统计事实库、不执行采集/设备/HIL、不提供自动放行或通用 GR&R 置信区间、不把视觉拟合 score 变成不确定度。
- **接收门保持开放：** 真实上游端口签名映射、R3 实际 C# 重载编译核对、两个无 UI Host 编译、两个消费者各自 PerformanceProfile、报告 CommitUnknown/影响索引的宿主 Owner 接线。公开字段、状态、错误和资源语义已由本指导冻结，不能由实现者另造。
- **文档状态：** 本轮仍为 `DesignReview / Prep`。没有运行产品 C#、真实 HALCON/AsunImage、WPF、两个消费者、长稳、HIL、标准件或现场验收；场景断言是实施前的可判定门，不是通过证据。

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

## 附录 A：模块核心 API Contract v0.2（公开契约；逐切片准入）

本附录是 `Asun.Modules.Qualification` 的唯一公开 DTO、端口、状态和错误契约。v0.2 修订只改变未实施的准备规格；旧报告继续按其原版本和原字节读取。所有类型均为 Core 程序集中的公开、可构造类型；实现不得以任意字典、反射参数、裸 `object` 或一组无关可空字段替代下列 union。每个 canonical domain 单独定义字段顺序、排序和分隔规则；未列字段不得隐式加入。

### A.1 基础值、请求变体和报告值

```csharp
namespace Asun.Modules.Qualification;

public readonly record struct CalculationId(string Value);
public readonly record struct ExperimentId(string Value);
public readonly record struct ObservationId(string Value);
public readonly record struct PhysicalSpecimenId(string Value);
public readonly record struct ArtifactRef(string Namespace,string Id,string Revision,string Sha256);
public readonly record struct MethodRef(string MethodId,string Version,ArtifactRef Parameters,
    ArtifactRef NumericPolicy,ArtifactRef BackendBuild);
public readonly record struct UnitId(string Id,string Dimension,string Revision);
public readonly record struct QuantityValue(double Value,UnitId Unit);
public readonly record struct Scope(string MeasurandId,string Revision,UnitId Unit,
    string SupportRevision,string SourceSystem,string ConditionsRef);
public readonly record struct ResourceBudget(long MaxRows,long MaxCells,int MaxColumns,
    int MaxCovarianceDimension,long MaxResidentBytes,TimeSpan? Deadline);
public readonly record struct DeadlinePolicy(TimeSpan? OperationDeadline,TimeSpan StopWaitBudget);
public readonly record struct AcceptanceCriteriaRef(ArtifactRef Source,string MeasureId,UnitId Unit,
    double Lower,double Upper,bool RequiresInterval,bool RequiresCompleteness,bool RequiresIndependence);
public enum EvidenceLevel { Synthetic, SoftwareReplay, RecordedMeasurement, PhysicalMeasurement }
public enum RepeatLevel { SameInputReplay, IndependentCapture, RepositionedCapture,
    OperatorOrSetup, CrossDay }
public enum ObservationKind { Measured, Failed, NotCollected, Excluded }
public sealed record ExperimentPlan(ArtifactRef Plan, IReadOnlyList<PlanCell> Cells,
    string FactorsRef,string RandomizationRef,string AssumptionsRef,int ExpectedCount);
public sealed record PlanCell(string CellId,PhysicalSpecimenId Specimen,string SetupId,
    int RepeatIndex,RepeatLevel RepeatLevel,string ParentCellId,string MethodId);
public sealed record Observation(ObservationId Id,string CellId,PhysicalSpecimenId Specimen,
    string CaptureId,string ReplayId,string TargetRef,DateTimeOffset CapturedUtc,
    RepeatLevel RepeatLevel,ObservationOutcome Outcome,ArtifactRef Evidence);
public abstract record ObservationOutcome;
public sealed record Measured(QuantityValue Value) : ObservationOutcome;
public sealed record Failed(string Reason,IReadOnlyList<ArtifactRef> EvidenceRefs) : ObservationOutcome;
public sealed record NotCollected(string Reason) : ObservationOutcome;
public sealed record Excluded(string RuleId,string Reason,ObservationOutcome Original) : ObservationOutcome;
public sealed record ReferenceAssignment(ArtifactRef Certificate,QuantityValue Assigned,
    QuantityValue? StandardUncertainty,string CorrelationGroup,string ConditionsRef,string UseRelationRef);
public sealed record AssumptionEvidence(string Name,string Statement,string Status,
    IReadOnlyList<ArtifactRef> EvidenceRefs);
public sealed record InputSnapshot(ArtifactRef Snapshot,long Count,long ActualBytes,
    string ContentSha256,IReadOnlyList<Observation> Observations,ExperimentPlan Plan);
public sealed record BiasPlan(ReferenceAssignment Reference,ConfidenceLevel? Confidence);
public sealed record ReferenceLevelAssignment(ObservationId ObservationId,QuantityValue Reference);
public sealed record LinearityPlan(IReadOnlyList<QuantityValue> Levels,
    IReadOnlyList<ReferenceLevelAssignment> Assignments,ConfidenceLevel? Confidence);
public sealed record StabilityPlan(string ModelId,TimeSpan Window,int MinimumDays,int RepeatsPerDay);
public enum GrrVariancePolicy { RawOnly, PreserveRawAndClampNegative }
public sealed record ToleranceInterval(QuantityValue Lower,QuantityValue Upper);
public sealed record GrrPlan(string ModelId,int Parts,int Operators,int Repeats,bool Crossed,
    GrrVariancePolicy VariancePolicy,double? StudySpanFactor,ToleranceInterval? Tolerance);
public sealed record UncertaintyPlan(IReadOnlyList<UncertaintyComponent> Components,
    IReadOnlyList<Covariance> Covariances,CoverageDefinition Coverage);
public sealed record GoldenPlan(string PlanId,ArtifactRef Cases,ArtifactRef Comparator,int PlannedCases,
    string ParentGroupingRef,string StrategyRef,string SeedSetRef,IReadOnlyList<GoldenCaseResult> CaseManifest);
public enum BenchmarkExecutionMode { ExecuteProbe, AnalyzeRecordedRun }
public sealed record ResourceMetricBudget(string Metric,string Scope,string Unit,double? PeakLimit,
    double? RetainedLimit,TimeSpan Window,double? AllowedSlope,ArtifactRef? TargetSource=null);
public sealed record BenchmarkPlan(ArtifactRef Probe,ArtifactRef Build,ArtifactRef Input,
    int WarmupIterations,int MeasuredIterations,int Parallelism,TimeSpan? Deadline,
    string ArrivalMode,string CacheMode,string FailurePolicy,IReadOnlyList<ResourceMetricBudget> Budgets,
    BenchmarkExecutionMode ExecutionMode,ArtifactRef Profile,ArtifactRef? RecordedRun=null);
public abstract record AnalysisVariant;
public sealed record BiasAnalysis(BiasPlan Plan) : AnalysisVariant;
public sealed record LinearityAnalysis(LinearityPlan Plan) : AnalysisVariant;
public sealed record StabilityAnalysis(StabilityPlan Plan) : AnalysisVariant;
public sealed record GrrAnalysis(GrrPlan Plan) : AnalysisVariant;
public sealed record UncertaintyAnalysis(UncertaintyPlan Plan) : AnalysisVariant;
public sealed record NumericDefinitionText(string Id,string Revision,string Body,ArtifactRef Source);
public sealed record DemingAxisConversion(UnitId SourceUnit,UnitId TargetUnit,double Scale,double Offset,
    ArtifactRef Evidence);
public sealed record DemingBridgeBudget(int MaxRows,int MaxGroups,int MaxColumns,int MaxCategories,
    int MaxTasks,int MaxDetailRows,int MaxDiagnostics,int MaxIntegerBits,long MaxBufferedBytes,
    long MaxWorkingSetBytes,TimeSpan WallClockLimit,TimeSpan DrainObservationLimit,int MaxNotifications);
public sealed record DemingPointPlan(string XRole,string YRole,QuantityValue CenterX,
    DemingAxisConversion XConversion,DemingAxisConversion YConversion,
    NumericDefinitionText Method,NumericDefinitionText Pairing,NumericDefinitionText ErrorVarianceEvidence,
    bool ReturnDetails,DemingBridgeBudget Budget);
public sealed record AgreementPair(string PairId,string Stratum,ObservationId? SideA,ObservationId? SideB);
public sealed record AgreementAnalysis(string MethodId,double LoaMultiplier,double? ErrorVarianceRatio,
    ArtifactRef PairingPolicy,IReadOnlyList<AgreementPair> Pairs,DemingPointPlan? Deming=null) : AnalysisVariant;
public sealed record GoldenAnalysis(GoldenPlan Plan) : AnalysisVariant;
public sealed record BenchmarkAnalysis(BenchmarkPlan Plan) : AnalysisVariant;
public sealed record QualificationRequest(string ContractVersion,CalculationId CalculationId,
    ExperimentId ExperimentId,MethodRef Method,Scope Scope,InputSnapshot Input,
    EvidenceLevel Evidence,ResourceBudget Resources,DeadlinePolicy Deadlines,
    AnalysisVariant Analysis,ReferenceAssignment? Reference,IReadOnlyList<AssumptionEvidence> Assumptions,
    AcceptanceCriteriaRef? Criteria,ArtifactRef? ParentCalculation);
public sealed record MaterializedAnalysisRequest(QualificationRequest Request);
public readonly record struct ConfidenceLevel(double Probability,string OriginalText);
public sealed record UncertaintyComponent(string Id,string Type,string Source,QuantityValue U,
    QuantityValue Sensitivity,string CorrelationGroup,string Distribution,string DegreesOfFreedom);
public sealed record Covariance(string Group,UnitId[] Units,double[,] Values);
public sealed record CoverageDefinition(string Kind,double? K,string Basis,string Probability);
public sealed record GoldenRequest(QualificationRequest Request,GoldenPlan Plan);
public sealed record BenchmarkRequest(QualificationRequest Request,BenchmarkPlan Plan);
public sealed record CalculationQueryRequest(CalculationId CalculationId,string RequestSha256);
public readonly record struct AvailableValue(QuantityValue Value,MethodRef Method);
public readonly record struct UnavailableValue(string Reason);
public abstract record ReportValue;
public sealed record Available(AvailableValue Value) : ReportValue;
public sealed record Unavailable(UnavailableValue Value) : ReportValue;
```

`IReadOnlyList` 在接纳前必须是有限、已计数的数组或封口页；不能把可延迟执行的 `IEnumerable` 传入。所有字符串、数组和矩阵均按 `RootLimits` 计字节；`double` 必须 finite，除A.3.1.1显式双侧Deming轴单位外，Observation.Measured与参考Assigned的单位必须匹配Scope；方差/协方差/灵敏度/数值结果按各自声明的量纲和轴单位校验，不能把um²强制当um。`Covariance.Values` 维度、对称性和 PSD 由请求的 `NumericPolicy` 校验。`ReferenceAssignment`、`PlanCell`、`Observation` 的身份冲突拒绝；`Excluded` 保留原 outcome，不能删除失败分母。

### A.2 状态、诊断、报告和事件

```csharp
public enum OperationTerminal { Completed, Rejected, Cancelled, TimedOut, Failed }
public enum ReportCompleteness { Complete, Partial }
public enum NumericStatus { Computed, UnsupportedDomain, Indeterminate, NotRequested }
public enum Applicability { ApplicableWithinDeclaredScope, Limited, NotApplicable, NotEstablished }
public enum CriteriaStatus { MeetsDeclaredCriteria, DoesNotMeetDeclaredCriteria, NotEvaluated }
public enum RootState { Created, Ready, Stopping, Stopped, Disposed, Draining, DrainUnknown }
public enum QualificationPhase { Validation, Read, Compute, Compare, Report, Draining, ResourcesReleased }
public readonly record struct QualificationDiagnostic(string Code,string Severity,
    QualificationPhase Phase,string? FieldPath,string? CellId,string? ObservationId,
    string MessageKey,IReadOnlyList<ArtifactRef> EvidenceRefs,string? BackendCode,string? Build);
public sealed record QualificationReport(CalculationId CalculationId,string ReportSchemaVersion,
    ArtifactRef Input,ArtifactRef Plan,MethodRef Method,Scope Scope,EvidenceLevel Evidence,
    long PlannedCount,long ValidCount,long FailedCount,long ExcludedCount,long NotExecutedCount,
    IReadOnlyDictionary<string,ReportValue> Values,IReadOnlyList<QualificationDiagnostic> Diagnostics,
    ReportCompleteness Completeness,Applicability Applicability,CriteriaStatus Criteria,
    string RequestSha256,string ContentSha256,IReadOnlyList<NumericResult> NumericalResults,
    BenchmarkReport? Benchmark=null);
public readonly record struct ResourceReleaseSummary(bool Drained,long ReleasedBytes,long ReleasedSlots,
    TimeSpan DrainElapsed,IReadOnlyList<QualificationDiagnostic> CleanupDiagnostics);
public sealed record QualificationOutcome(OperationTerminal Terminal,CalculationId CalculationId,
    QualificationReport? Report,IReadOnlyList<QualificationDiagnostic> Diagnostics,
    ResourceReleaseSummary Resources);
public readonly record struct QualificationEvent(string InstanceId,CalculationId CalculationId,
    long RequestRevision,long Sequence,QualificationPhase Phase,long CompletedUnits,long PlannedUnits,
    long MonotonicTimestamp,string Kind);
public sealed record DesignValidation(bool CanAnalyze,IReadOnlyList<QualificationDiagnostic> Diagnostics,
    string RequestSha256);
public sealed record QualificationOperationSnapshot(CalculationId CalculationId,string InstanceId,
    string RequestSha256,string AdmissionId,string? TransferId,string Stage,string? ReportRef,
    string AdmissionState,bool Drained,long RequestRevision);
public sealed record StopResult(bool IsDrained,Task Completion,IReadOnlyList<QualificationDiagnostic> Diagnostics);
public enum UiReceiptState { Accepted, Rejected, Unknown }
public sealed record UiUnbindReceipt(bool IsUnbound,Task Completion,IReadOnlyList<QualificationDiagnostic> Diagnostics);
```

`QualificationOutcome` 的业务诊断和 `ResourceReleaseSummary` 的 cleanup 诊断分开。`Terminal` 仅在子任务、端口租约和已登记观察邮箱真实退出后发布；等待超时只返回 `StopResult(IsDrained=false, Completion)`。事件是不可变观察投影，结果和查询是权威。

### A.3 端口、Root、Factory 和公开服务

本小节为公开声明片段，不是可独立编译的 class 实现；分号方法及 internal 构造边界均须按 §4.1 实施。不存在空方法体、假完成 Dispose 或未实现异常的默认实现。

```csharp
public interface IQualificationNumerics {
    NumericCapabilities Capabilities { get; }
    ValueTask<NumericResult> CalculateAsync(NumericRequest request,CancellationToken token);
}
public sealed record NumericCapabilities(string Backend,string Build,IReadOnlySet<string> Methods,
    int MaxDimension,bool SupportsCancellation,string SupportDomain);
public abstract record NumericInput;
public sealed record ScalarNumericInput(IReadOnlyList<QuantityValue> Values) : NumericInput;
public sealed record GroupedNumericInput(IReadOnlyList<PlanCell> Cells,IReadOnlyList<Observation> Observations) : NumericInput;
public sealed record CovarianceNumericInput(IReadOnlyList<UncertaintyComponent> Components,
    IReadOnlyList<Covariance> Covariances,CoverageDefinition Coverage) : NumericInput;
public sealed record AgreementNumericInput(IReadOnlyList<Observation> SideA,
    IReadOnlyList<Observation> SideB,double LoaMultiplier,double? ErrorVarianceRatio) : NumericInput;
public enum DemingMemberState { Valid, Unknown, Missing, Unmeasured, Invalid, NotApplicable, Excluded }
public sealed record DemingBridgeObservation(string RowId,string SourceObservationId,string SourceRevision,
    ArtifactRef? OriginalEvidence,DemingMemberState State,string? Reason,UnitId Unit,double? Value);
public sealed record DemingBridgePair(string PairId,DemingBridgeObservation Left,
    DemingBridgeObservation Right,string? ClusterKey);
public sealed record DemingNumericInput(string Stratum,DemingPointPlan Plan,
    double SourceErrorVarianceRatio,double CenterX,double ErrorVarianceRatio,IReadOnlyList<DemingBridgePair> Pairs) : NumericInput;
public sealed record NumericRequest(string OperationId,ArtifactRef SourceSnapshot,string MeasurandId,
    ArtifactRef SelectionPolicy,ArtifactRef? SubsetApproval,bool ReadComplete,bool PopulationClosed,
    long ExpectedRows,IReadOnlyList<Observation> Members,string MethodId,AnalysisVariant Analysis,
    NumericInput Input,MethodRef Method,string NumericPolicyId,string UnitSystem,string InputOrderHash);
public sealed record NumericCoverage(long Expected,long Included,long Unknown,long Missing,
    long Unmeasured,long Invalid,long NotApplicable,long Excluded);
public sealed record NumericBackendIdentity(string Id,string Version,string SourceCommit,string BuildHash,
    string FloatingPointProfile,bool Interruptible,string Validation);
public sealed record NumericProvenance(string CoreApiVersion,string ImplementationVersion,
    string OperationId,string StatisticsSnapshotId,string ResultState,ArtifactRef SourceSnapshot,
    string DerivedInputSha256,bool ReadComplete,bool PopulationClosed,long ExpectedRows,
    MethodRef Method,ArtifactRef SelectionPolicy,ArtifactRef? SubsetApproval,
    string MemberSequenceHash,IReadOnlyList<NumericBackendIdentity> Backends);
public sealed record NumericValueEvidence(string Key,string State,string Unit,string? Code);
public sealed record NumericPsdEvidence(string State);
public sealed record NumericDistributionEvidence(string Distribution,string Operation,string Side,
    bool HasPerRequestConvergenceCertificate);
public sealed record NumericInferenceEvidence(string Kind,string Alternative,long Degrees,
    ArtifactRef AssumptionEvidence);
public sealed record NumericScalarValue(string State,double? Value,string Unit,string? Code);
public sealed record NumericScaledValue(string State,double? Mantissa,int? Exponent2,string Unit,string? Code);
public sealed record NumericDemingMoments(long Count,double? AnchorX,double? AnchorY,
    NumericScalarValue MeanX,NumericScalarValue MeanY,NumericScaledValue MeanOffsetX,
    NumericScaledValue MeanOffsetY,NumericScaledValue Sxx,NumericScaledValue Syy,NumericScaledValue Sxy);
public sealed record NumericDemingComputation(string MethodRevision,int? ScaleExponentX,int? ScaleExponentY,
    double? NormalizedErrorVarianceRatio,double? Correlation,double? RelativeEigenGap,string? RootBranch,
    int PeakIntegerBits,long PairsVisited,string PairSequenceHash,NumericBackendIdentity Backend);
public sealed record NumericDemingPointDetail(string PairId,NumericScalarValue CenteredX,
    NumericScalarValue CenteredY,NumericScalarValue PredictedY,NumericScalarValue VerticalResidual);
public sealed record NumericBackendDiagnostic(string Code,string MessageKey,string? MetricId,
    string? ObservationId,IReadOnlyList<string> Arguments);
public sealed record NumericS7DefinitionReference(string Id,string Revision,string ContentHash);
public sealed record NumericS7InputIdentity(string SnapshotId,string SnapshotRevision,string Mode,
    string QueryReceiptId,string SourceBoundary,string ContentHash,string? WatermarkId,
    bool ReadComplete,bool CanReplay);
public sealed record NumericS7Closure(long ExpectedMembers,string ExpectedMemberSetHash,
    bool ReadComplete,bool PopulationClosed,string ClosureReceiptReference,int GapCount);
public sealed record NumericS7Policy(NumericS7DefinitionReference Identity,double RankAbsolute,
    double RankRelative,double DecompositionTolerance,double PsdTolerance,double CorrelationRoundoffTolerance,
    double TQuantileAbsolute,double TQuantileRelative,double FQuantileRelative,double TailRelative);
public sealed record NumericDemingIdentity(NumericS7InputIdentity Input,NumericS7Closure Closure,
    NumericS7DefinitionReference Method,NumericS7DefinitionReference Pairing,
    NumericS7DefinitionReference ErrorVarianceEvidence,NumericS7DefinitionReference SelectionPolicy,
    NumericS7DefinitionReference? SubsetApproval,NumericS7Policy Policy,DemingBridgeBudget Budget,
    string MemberSequenceHash);
public sealed record NumericDemingDetail(string Stratum,string TaskId,NumericCoverage Coverage,
    NumericCoverage LeftCoverage,NumericCoverage RightCoverage,NumericDefinitionText Method,
    NumericDefinitionText Pairing,NumericDefinitionText ErrorVarianceEvidence,double ErrorVarianceRatio,
    double CenterX,string LineKind,NumericDemingMoments Moments,NumericScalarValue Slope,
    NumericScalarValue CenterIntercept,NumericDemingComputation Computation,
    IReadOnlyList<NumericDemingPointDetail> Details,string UpstreamInputSha256,string UpstreamRequestSha256,
    NumericDemingIdentity Identity,IReadOnlyList<NumericBackendDiagnostic> BackendDiagnostics,
    IReadOnlyList<NumericBackendDiagnostic> ResultBackendDiagnostics);
public sealed record NumericTaskDetail(string TaskId,NumericCoverage Coverage,
    IReadOnlyDictionary<string,long> Integers,IReadOnlyDictionary<string,ReportValue> Values,
    IReadOnlyList<QualificationDiagnostic> Diagnostics,IReadOnlyList<NumericValueEvidence> ValueEvidence,
    NumericPsdEvidence? Psd,NumericDistributionEvidence? Distribution,NumericInferenceEvidence? Inference,
    NumericDemingDetail? Deming=null);
public sealed record NumericResult(IReadOnlyDictionary<string,ReportValue> Values,
    IReadOnlyList<QualificationDiagnostic> Diagnostics,string BackendCompletionId,
    NumericProvenance Provenance,IReadOnlyList<NumericTaskDetail> Tasks);

public interface IObservationSnapshotReader : IAsyncDisposable {
    ValueTask<SnapshotHeader> OpenAsync(ArtifactRef snapshot,CancellationToken token);
    IAsyncEnumerable<ObservationPage> ReadPagesAsync(int pageSize,CancellationToken token);
    ValueTask<SnapshotSeal> SealAsync(CancellationToken token);
}
public sealed record SnapshotHeader(long DeclaredCount,long ActualBytes,string Sha256,string Revision);
public sealed record ObservationPage(long Offset,IReadOnlyList<Observation> Rows,string PageSha256);
public sealed record SnapshotSeal(long Count,string Sha256,bool Complete);
public interface IReplayQualificationReader { ValueTask<ReplayResult> ReadAsync(GoldenPlan plan,CancellationToken token); }
public sealed record ReplayResult(int Planned,int Executed,string CasesSha256,IReadOnlyList<GoldenCaseResult> Cases);
public sealed record GoldenCaseResult(string CaseId,string ParentId,string Status,string ExpectedRef,string ActualRef);
public interface IReferenceProjectionReader { ValueTask<ReferenceProjection> ReadAsync(ReferenceAssignment assignment,CancellationToken token); }
public sealed record ReferenceProjection(ReferenceAssignment Assignment,bool Complete,string SourceSha256);
// Benchmark ports, receipts and lease ownership have their only declarations in A.3.3.
public interface IQualificationObserver { ValueTask<ObserverLease> SubscribeAsync(
    Func<QualificationEvent,ValueTask> handler,int capacity,CancellationToken token); }
public sealed record ObserverLease(string LeaseId,Task Completion,IAsyncDisposable Registration);
public interface IEvidenceSink { ValueTask<EvidenceReceipt> SealAsync(
    QualificationReport report,CancellationToken token); ValueTask<EvidenceReceipt?> QueryAsync(
    string commitId,CancellationToken token); }
public sealed record EvidenceReceipt(string CommitId,string State,string ContentSha256);
public sealed record TransferOffer(string TransferId,string SourceOwnerId,string TargetOwnerId,
    string RootId,RootReservation Capacity,RootLimits Limits,QualificationRoot Root);
public sealed record TransferReceipt(string TransferId,string RootId,string ConfirmedOwnerId,
    string State,bool ResourcesOwned);
public interface IQualificationTransfer {
    Task<TransferReceipt> QueryTransferAsync(string transferId,CancellationToken waitToken);
}
public sealed record HostCompletion(string CalculationId,QualificationOutcome? Business,string? BusinessError,
    RootCloseResult? Cleanup,string? CleanupError,int BusinessExitCode,int CleanupExitCode);
public sealed class QualificationRecoveryOwner {
    public QualificationRecoveryOwner(string ownerId,int maxRoots,int maxTasks,int maxLateLeases,
        long maxResidentBytes);
    public QualificationRoot CreateRoot(string rootId,RootLimits limits);
    public QualificationRoot? QueryRoot(string rootId);
    public HostCompletion? QueryHostCompletion(string rootId);
    public void RecordHostCompletion(string rootId,HostCompletion completion);
    public Task<RootCloseResult> ObserveRootAsync(string rootId,TimeSpan waitBudget,CancellationToken waitToken);
    public Task<RootCloseResult> CloseRootAsync(string rootId,TimeSpan cleanupBudget,CancellationToken waitToken);
    public void AcknowledgeReleased(string rootId);
    public Task<TransferReceipt> AcceptTransferAsync(TransferOffer offer,CancellationToken waitToken);
    public Task<TransferReceipt> QueryTransferAsync(string transferId,CancellationToken waitToken);
}
public interface IQualificationOperationLedger {
    ValueTask<AdmissionReceipt> AdmitAsync(CalculationId id,string requestSha256,CancellationToken token);
    ValueTask<QualificationOperationSnapshot?> QueryAsync(CalculationQueryRequest query,CancellationToken token);
    ValueTask RecordAsync(QualificationOperationSnapshot snapshot,CancellationToken token);
}
public sealed record AdmissionReceipt(string AdmissionId,string State,string RequestSha256);
public sealed record RootLimits(long MaxResidentBytes,int MaxInstances,int MaxObservers,
    int MaxTasks,int MaxLateLeases,TimeSpan CleanupBudget);
public sealed record RootReservation(string ReservationId,string RootId,string InstanceId,
    long ReservedBytes,int ReservedSlots,int ReservedTasks,int ReservedLateLeases);
public interface IQualificationLease : IAsyncDisposable { string LeaseId { get; } long RetainedBytes { get; } }
public enum RootTaskRole { Work, ControlWait, UiCoordinator }
public sealed class QualificationRoot : IAsyncDisposable {
    // Constructor is internal; RecoveryOwner.CreateRoot publishes an already registered root.
    public string RootId { get; }
    public void RetainInput(RootReservation reservation,QualificationRequest request);
    public void RegisterTask(RootReservation reservation,string taskId,Task originalTask,
        RootTaskRole role=RootTaskRole.Work);
    public Task<T> StartOwned<T>(RootReservation reservation,string taskId,Func<Task<T>> start,
        RootTaskRole role=RootTaskRole.Work);
    public void RegisterLateLease(RootReservation reservation,IQualificationLease lease);
    public void RegisterDisposable(RootReservation reservation,string id,IAsyncDisposable resource);
    public void RegisterCancellation(RootReservation reservation,CancellationTokenSource source);
    public RootReservation Reserve(string instanceId,long bytes,int slots,int tasks,int lateLeases);
    public Task<RootCloseResult> CloseAsync(TimeSpan cleanupBudget,CancellationToken waitToken);
    public Task<TransferOffer> BeginTransferAsync(string transferId,
        QualificationRecoveryOwner target,CancellationToken waitToken);
    public Task<TransferReceipt> QueryTransferAsync(string transferId,CancellationToken waitToken);
    public ValueTask DisposeAsync(); // completes only after registered work and leases exit
}
public sealed record RootCloseResult(RootState State,bool Drained,Task Completion,
    IReadOnlyList<QualificationDiagnostic> Diagnostics);
public sealed record QualificationFactoryPorts(IQualificationNumerics Numerics,
    IQualificationOperationLedger Ledger,IObservationSnapshotReader? Reader,
    IReplayQualificationReader? Replay,IReferenceProjectionReader? References,
    IBenchmarkProbe? Probe,IResourceSampler? Sampler,IQualificationObserver? Observer,
    IEvidenceSink? EvidenceSink,IQualificationTransfer? Transfer,
    IBenchmarkAssetReader? BenchmarkAssets=null,IBenchmarkClock? BenchmarkClock=null);
public static class QualificationFactory {
    public static IQualificationService Create(QualificationRoot root,RootReservation reservation,
        QualificationFactoryPorts ports); // declaration fragment
}
public interface IQualificationService : IAsyncDisposable {
    DesignValidation ValidateDesign(QualificationRequest request);
    QualificationOutcome Analyze(MaterializedAnalysisRequest request,CancellationToken token);
    Task<QualificationOutcome> AnalyzeAsync(QualificationRequest request,CancellationToken token);
    Task<QualificationOutcome> EvaluateGoldenAsync(GoldenRequest request,CancellationToken token);
    Task<QualificationOutcome> BenchmarkAsync(BenchmarkRequest request,CancellationToken token);
    Task<QualificationOperationSnapshot> QueryCalculationAsync(CalculationQueryRequest request,CancellationToken token);
    Task<QualificationOperationSnapshot> CancelCalculationAsync(
        CalculationQueryRequest request,CancellationToken waitToken);
    Task<StopResult> StopAsync(TimeSpan waitBudget,CancellationToken waitToken);
}
```

NumericRequest明确携带SourceSnapshot、原Members、方法/选择/子集、完整性、变换输入、单位和稳定成员序。A.3.1逐字段映射当前statistics v0.3，A.3.2保证原NumericalRun/Completion/Dispose仍在同Root；ConstantRatioDeming专用Task/Result已由上游S7冻结并主控接收，本轮桥规格见A.3.1.1；无运行能力不能声称后端已发布。

QueryRoot只读返回本Owner登记的原Root（已转交时沿原路由），null仅表示未创建/已经确认释放的登记，不证明一个未知资源已排空；CreateRoot须原子失败且不启动端口。RecordHostCompletion只更新原rootId的两轴摘要，不消除原Task异常或释放容量。

Factory 之前必须由 RecoveryOwner 原子创建/登记 Root 并由 Root.Reserve 预约容量，Factory 负责核预约并登记 Service、原始 Task、Reader/Numeric/Probe/Ledger、报告、观察和租约。`Create` 不启动隐藏线程；`Root.CloseAsync` 使用独立、单调总 cleanup 截止，未排空继续由 Root 强持。`AdmissionReceipt.State=AdmissionUnknown` 时停止派发并按原 `AdmissionId` 查询，不换 `CalculationId` 重提交。Ledger 是宿主唯一事实写入者；Core 不创建私有 Store。

### A.3.1 与 statistics v0.3 的逐字段数值桥

唯一上游为 [statistics数值合同](../statistics/DEVELOPMENT-GUIDE.md#qualification-numerical-operations)（Asun.Modules.Statistics，当前Module API v0.3；只读定位§7.1.3.1–§7.1.3.8及本轮S7 §7.1.3.10）。已实读公开NumericalRequest/Tasks/Results/INumericalStatistics，以下映射为本页适配规格，**不是已运行接线**。Core仍只引用自己的BCL端口，统计桥程序集/代码切片另由主控接收，不把Asun.Modules.Statistics类型塞进Core。

| qualification输入/生命期 | statistics公开字段/入口 | 唯一转换 |
|---|---|---|
| 一个NumericRequest | NumericalRequest.OperationId | CalculationId + "/" +固定stage/task-batch编号，重查同ID，不使用新的随机GUID |
| SourceSnapshot/完整派生工作输入 | InputReference(SnapshotId,SnapshotRevision,Mode,QueryReceiptId,SourceBoundary,ContentHash,WatermarkId,ReadComplete,CanReplay) | SnapshotId=SourceSnapshot.Namespace+"/"+Id；Revision=原Revision；Mode=FixedSnapshot；QueryReceiptId=SourceSnapshot.Id；Boundary=NumericRequest.UnitSystem及原量名范围；ContentHash=派生QLNI hash；WatermarkId=null；ReadComplete=显式请求值；CanReplay=true仅冻结内存可重读 |
| 完整性 | InputClosure(ExpectedMembers,ExpectedMemberSetHash,ReadComplete,PopulationClosed,ClosureReceiptReference,Gaps) | ExpectedMembers=ExpectedRows；ExpectedMemberSetHash=null（未提供原总体成员集合hash，不把有序输入hash冒充集合封口）；二个bool取显式值；ClosureReceiptReference=SourceSnapshot.Id+"/"+Revision；缺测是原成员State，不是读缺页；未封口不运行全体估计；Gaps只由真实缺成员证据形成 |
| Method/选择/子集 | DefinitionReference、CompletenessPolicy | Method=(MethodId,Version,Parameters.Sha256)；SelectionPolicy/SubsetApproval按ArtifactRef Namespace+"/"+Id/Revision/Sha256；全体=RequireAll，预批准子集=ApprovedObservedSubset且必须有SubsetApproval；不编造批准 |
| NumericPolicyRef | NumericalPolicy全部10字段 | Identity解析正式政策引用；九个double阈值逐字段按statistics§7.1.3.1固定engineering-binary64-v1（秩absolute/relative、decomposition/PSD/correlation、t abs/relative、F relative、tail relative），不能把Host fixture的短字符串当正式容差对象；缺正式政策只影响真后端，不影响合同oracle |
| 额度/截止 | NumericalBudget全部13字段 | MaxRows/Groups/Columns/Categories/Tasks/DetailRows/Diagnostics/IntegerBits/BufferedBytes/WorkingSetBytes/WallClockLimit/DrainObservationLimit/Notifications显式冻结；上限取请求、root、上游工程上界三者较小值；times>0；null业务截止用部署Profile显式有限数值调用预算，不靠无限Wait |
| 观测/变换值 | NumericalMember(RowId,Source,State,ReasonCode)、NumericRow(Member,GroupKey,Value) | RowId=ObservationId；Source=(ObservationId,Evidence.Revision,Evidence.Sha256,Namespace+"/"+Id)；Measured→Valid；Failed→Invalid；NotCollected→Unmeasured；Excluded→Excluded。变换值只有Valid才非null，单位转换/参考差值由qualification预校验，不换Source身份 |
| 无UI同步 | INumericalStatistics.ComputeNumerical | 只限上游允许的managed任务，不能用.Result包装异步/native；不支持条件区间时返回Unsupported |
| 异步 | ComputeNumericalAsync→NumericalRun.Completion→NumericalRun.DisposeAsync | adapter把原接纳Task、NumericalRun、Completion、Cancel、Dispose都注册原Root；Completion返回后仍等run Dispose真实退出才返回NumericResult，不因等待超时放掉数组。原OperationId用于QueryNumericalOperationAsync |
| 返回 | NumericalValue、Coverage、Provenance、Diagnostics | Computed finite才映射Available；UnsupportedDomain/RangeLoss/NumericUncertain等保留原code并映射Unavailable；df/count保留整数，谱/SS/单位/来源/后端身份不能丢。尾数学端点不当有限置信区间 |

NumericalBudget的唯一小软件Profile N01为：
`new NumericalBudget(100,100,32,16,16,100,100,256,1048576,8388608,TimeSpan.FromSeconds(2),TimeSpan.FromSeconds(1),64)`。它只供小解析向量/软件验证，不是客户时限；大规模Profile另按真实后端和root上界冻结。请求剩余单调期限更小则取更小值；已耗尽先拒绝，不再派发。MaxRows上游1,000,000/维数128等上界不被qualification更大的MaxRows默认自动放大。

固定分析任务映射（GroupKey编码用“各ID的UInt32 UTF8长度+bytes”的hex串，禁止分隔符碰撞）：

| 分支 | 上游Task及全部实质参数 | 返回组合 |
|---|---|---|
| Bias | GroupMomentsTask(taskId="bias-moments",Unit=Scope.Unit machine ID,Rows=每个Measured的d=y-reference,GroupKey="bias") | NumericalMoments.Count/Mean/M2/SampleVariance；qualification做§6.1的bias/随机SE与共同参考隔离。请求t区间才追加DistributionTask(StandardT,Quantile,Upper,df=n-1,Degrees2=null,Argument=alpha/2) |
| Linearity/LinearDrift | AffineTask(TaskId, XUnit, YUnit, CenterX, PairRows, ReturnDetails=true) | X为正式参考水平或实际UTC差/声明timeunit；Y为偏差/量值。CenterX来自GroupMomentsTask.meanX；PairRow含同RowId两侧Source和State，ClusterKey=null只在独立设计。DesignResult系数ID=center-intercept/slope，ResidualDegrees/SSE/Variance/Residuals/covariance逐字段保留 |
| Linearity PE/LOF | GroupMomentsTask按参考水平分组；AffineTask的残差映射再GroupMomentsTask取稳定平方和；必要ContrastTask | PE=各水平M2和；LOF按§6.1预声明组均值与预测差；核SSE=PE+LOF。F Upper请求Degrees1=g-2、Degrees2=N-g，不换顺序。PE=0不普通除0 |
| BalancedCrossedMoments | ContrastTask(TaskId,Unit,Rows按part×operator cell,Contrasts) | 每格核r。以整数系数避免1/a舍入后不满足“精确系数和0”。P_i对cell(k,l)系数a·[k=i]−1，Divisor=a²b/r；O_j为b·[l=j]−1，Divisor=ab²/r；PO_ij为ab·[k=i,l=j]−a·[k=i]−b·[l=j]+1，Divisor=a²b²/r。SumSquare按P/O/PO族分别累加，WithinSumSquare=SS_E；其余df/MS/负分量策略由qualification§6.2组合 |
| BalancedNestedMoments | ContrastTask按operator i的part j格；b操作者/a件/r重复 | O_i系数b·[k=i]−1，Divisor=ab²/r；P_j(i)在本操作者格内系数a·[l=j]−1（其他操作者项省略），Divisor=a²/r；Within=SS_E。不同操作者不共享PhysicalSpecimenId，核ΣSS/df，不造交叉交互 |
| BalancedRandomDay | ContrastTask按day格，h天/r次 | day_i系数h·[g=i]−1，Divisor=h²/r；ΣSS=SS_day，Within=SS_within；随机日/漂移的识别与自由度仍在qualification |
| 一般设计诊断 | DesignTask(TaskId,Model=Method.Parameters引用,ResponseUnit,Members,Columns,RowMajorDesign,Response,RequireResidualVariance,ReturnDetails) | 每列公开Id/Unit/Role，Intercept全1、Indicator0/1。矩阵显式冻结，不由上游猜因子；QR秩/谱/condition/SSE/df完整投影，不伪逆凑识别 |
| Uncertainty | CovarianceTask(TaskId,BudgetModel=Method.Parameters,OutputUnit=Scope.Unit,ComponentIds,InputUnits,RowMajorCovariance,Sensitivities) | Id/Units/Σ轴/sensitivity按同一顺序；一份完整Σ必须覆盖全分量，或显式已证独立块，未知跨组相关不填0。CovarianceResult.Psd/Scales/Eigenvalues/Residuals/Variance/StandardUncertainty/Contributions都保留；Coverage.k仅由qualification显式乘，统计库不决定概率 |
| Bland–Altman | PairTask(TaskId,Statistic=Difference,LeftRole="A",RightRole="B",LeftUnit/RightUnit,PairingPolicy,Rows,Inference=null或PairedMeanT,ReturnDetails=true) | 逐层PairRow含完整PairId与两侧Source/State/ClusterKey。Difference得到mean(d)、M2、sample variance和差值明细；LoA由qualification显式LoaMultiplier组合。需要biasT才给ConditionalInference(PairedMeanT,AssumptionEvidence,TwoSided,NullMean=0,Alpha=1-C) |
| ConstantRatioDeming | S7 ConstantRatioDemingTask/Result（A.3.1.1逐字段） | 单family、显式CenterX/λ/来源/双Coverage/ScaledValue/中心截距；真实运行能力门不省略 |
| Golden/Benchmark | 不调用这些统计任务来代替Replay比较器/probe完成屏障 | 全分母/失败/时长仍按原Owner与DEV-GOV-010口径 |

**ConstantRatioDeming上游内部DTO/算法缺口已关闭。** 主控已接收statistics S7规格，本页直接映射公开ConstantRatioDemingTask/Result和DemingScaledValue，详见A.3.1.1。本轮不修改上游指导，不重建第二算法权威；附加桥确定指导内容已由主控限定接收，真实Adapter/Capabilities/实现运行与数值资格仍PreparationIncomplete，CI/异方差等排除范围不变。

NumericResult.Values为**封闭输出词表**：组矩n/mean/m2/sample-variance；contrast family.P/O/PO/E/day/within及对应SS/df；回归center-intercept/slope/SSE/residual-variance；uncertainty.variance/u/contribution.<预声明Id>；agreement.mean-difference/sample-variance/loa-lower/loa-upper；tail.quantile/probability。dynamic后缀仅来自已冻结组/分量/列ID，未知键拒绝QLF-PORT-CONTRACT，不把任意第三方map当契约。子任务TaskId、整数计数/df、Coverage和Provenance保存在NumericResult.Tasks/Provenance，并原样进入QualificationReport.NumericalResults，不靠double显示代替原整数。NumericTaskDetail.Integers仅允许count.<GroupKey>、df.<预声明族/列Id>、design.rows/columns/rank、pair.left/right-tie-groups/max-tie、tail.iterations；Values允许上述输出词表及明细residual.<RowId>、coefficient-covariance.<RowId>.<ColumnId>、design.singular/center/scale.<ColumnId>、design.response-center/response-scale/rank-threshold/reconstruction-error/orthogonality-error/condition、covariance.scale/eigenvalue.<ComponentId>/reconstruction-error/orthogonality-error、tail.argument/degrees1/degrees2/small-tail、inference.statistic/probability/lower/upper/alpha。后缀只取请求声明稳定ID；每个Values键恰有一NumericValueEvidence，State原样使用上游NumericalValueState词表，有限Computed才Available；Code/Unit原样，MathematicalEndpoint保留状态但Unavailable且不写非finite值。PSD、Distribution/Operation/Side/收敛证书、InferenceKind/Alternative/整数Degrees/AssumptionEvidence分别进入公开Psd/Distribution/Inference字段；string字段仅接受A.3.1对应上游枚举已声明词表，未知值拒绝。不能藏在日志。所有任务来源和未定义状态保留，明细超预算先拒绝而不静默截断。NumericProvenance绑定原请求全字段/QLNI及上游原MemberSequenceHash，后者按statistics自己的序列codec取值，不能与本页QLMS强行等同。以上旧family Closure字段仅完整封口请求走此桥；ReadComplete=false/PopulationClosed=false/ExpectedRows与Members.Count不符在派发前拒绝；S7的ExpectedRows按PairId计，完整性/状态及两侧成员的例外映射唯一见A.3.1.1，原缺页证据保留在qualification诊断，不伪造空Gaps成功。

### A.3.1.1 ConstantRatioDeming S7 精确桥（本轮新增范围）

唯一上游为 [statistics §7.1.3.10](../statistics/DEVELOPMENT-GUIDE.md#constant-ratio-deming)，使用其现有INumericalStatistics、NumericalRequest、NumericalRun和专用Task/Result，不增加statistics入口或第二算法。主控已接收S7六项文档规格，上游当前状态为ModuleCoreImplementationReady（仅规格准备）；不能从规格接收推运行能力。Adapter namespace为Asun.Modules.Qualification.Statistics；只有该桥接程序集消费Asun.Modules.Statistics，Core保持BCL公开类型。代码工程/发布接线须另行授权，本轮只修此指导。未来本桥唯一工程落点为src/Modules/qualification/Asun.Modules.Qualification.Statistics/Asun.Modules.Qualification.Statistics.csproj，net10.0，仅引用本Qualification.Core与已冻结Statistics.Core；新增桥唯一验证工程tests/Modules/qualification/Asun.Modules.Qualification.Statistics.Tests/Asun.Modules.Qualification.Statistics.Tests.csproj，Microsoft.NET.Sdk/OutputType=Exe/net10.0，仅上述桥/两Core+BCL，无WPF/testSDK。两个Host与QDEM-01..08在该同一Exe的host deming-noise/host deming-unit或suite qualification-deming模式，外层10s截止，任何必需断言失败/skip非0。本页Core.Tests仍只Core+BCL，旧Core/Benchmark授权范围和命令保持，不把statistics引用塞入原Core.Tests。本轮仅冻结消费者和未来路径，创建工程及跨程序集引用另须主控明确实现授权；禁止其它模块/共享/原件/AsunImage/产品Shell写入。

**qualification新增输入闭包。** AgreementAnalysis.MethodId仍是IndependentPairsBlandAltman或显式附加ConstantRatioDeming；Deming=null时维持已有配对差值分支。Deming非null时ErrorVarianceRatio必需且是YConversion.SourceUnit²/XConversion.SourceUnit²数值单位下原λ=VarY/VarX，CenterX.Unit等于X.SourceUnit。每侧转换必须Scale>0 finite、Offset finite，Source/Target相同Dimension且转换Evidence非空；原Observation.Unit分别等于本侧SourceUnit，不再把这两侧都硬要求等于Scope显示单位。没有显式转换只接受Scale=1、Offset=0、SourceUnit=TargetUnit的有证据恒等变换，不按"mm/um"标签猜倍数。y/x目标单位可不同，Bland–Altman另要求统一单位，不能把Deming的不同数值单位直接当差值。

NumericDefinitionText.Body为完整已冻结ASCII正文（≤4096bytes、无NUL），Source.Sha256=SHA256(UTF8 Body)；Id/Revision非空，Method.Id固定constant-ratio-deming-exact-center-v1且Revision="1"，Body采用S7对应方法正文；Pairing与ErrorVarianceEvidence正文写实际范围/独立性/恒定误差比方向/原单位与变换后单位/证据角色，合成例明说fixture、非物理。Source仅是原内容来源，S7 DefinitionReference另按S7-DEFINITION域计算，不以Source.Sha256冒充其定义hash。Agreement.PairingPolicy必须与Deming.Pairing.Source全字段相等；NumericRequest.SelectionPolicy取同一明确完整配对政策源、SubsetApproval=null。本桥首片RequireAll，不开放隐式删对或ApprovedObservedSubset；有原批准子集也需上游已冻结路径的独立后续桥授权，不把未接本片子集变成全体。

同一Calculation的每Stratum独立一个数值操作OperationId=CalculationId+"/deming/"+hex(UInt32 UTF8长度+Stratum bytes)，TaskId="deming-point"，只一task；PairTask/区间另具名操作，不同family不混投。预先核该层PairId唯一、A/B ObservationId分别唯一，Members是该层全计划配对所引用的原观测（按ObservationId稳定序），没有被引用的别层行不可混入。NumericRequest.ExpectedRows=该层计划Pair数，**不是Members.Count/两侧行总和**；原InputSnapshot.Count仍是真观测行数。Pair外连接以Analysis.Pairs显式ID，不按位置zip，Reader完整/PopulationClosed明确；ReadComplete=false或源未封口先拒绝本桥、保留原缺页诊断，不伪造InputGap。每个计划Pair都输出一DemingBridgePair，单侧缺失是一行Missing状态，不在Closure.Gaps重复登记；Gaps为空仅因计划Pair全集已逐项材料化，不能从原IO前缀结束推封口。

Measured→Valid（Value=变换后的finite值）；Failed→Invalid/原Reason；NotCollected→Unmeasured/原Reason；Excluded→Excluded/RuleId及Reason（原Outcome仍在Members）；计划一侧ID=null→Missing/plan-side-missing、Value=null、OriginalEvidence=null，保留该侧的确定派生身份，不声称真实Observation。其RowId/SourceObservationId="missing/"+hex(UInt32 PairId长度+PairId+单byte x/y角色)，SourceRevision=原SourceSnapshot.Revision；非缺侧RowId=原Observation.Id、SourceObservationId同原Id、Revision=原Evidence.Revision、OriginalEvidence全ArtifactRef。缺侧身份与真Id冲突先拒绝；两侧也不共用同Source。S7的ClusterKey首片null，只在计划独立性明确且没有跨PairId重复PhysicalSpecimenId/捕获相关组（同一Pair的A/B共享物理件是预期配对，不当额外独立样本）时允许；当前AgreementPair未携cluster公开字段，实际关联必须由原计划/来源证明：发现跨Pair重复件/捕获身份、原Assumptions未声明独立或相关组不可排除时Materialize返回QLF-METHOD-UNSUPPORTED而不派发、不凭空造cluster；低级DemingNumericInput若调用者显式给非nullClusterKey则原样传S7并拒绝模型，不清空cluster骗独立n。DemingBridgePair.Pairs按PairId Ordinal，Stratum跨层不归并。

**单位转换与派生输入identity。** 转换值x'=a*x+c、y'=b*y+d按明确标量binary64顺序（不FMA）执行，λ'=(b/a)²λ、CenterX'=a*CenterX+c同时求得；转换中任何非finite/正λ变0/不可信范围变换为QLF-NUMERIC-DOMAIN并不派发S7，不补epsilon或截值。S7独立检其输入/ratio/Center支持域；本桥不把单位变换扩大为不限double域。effective Budget至少128≤MaxIntegerBits≤4096，MaxRows/Groups≥该层计划对数、MaxTasks=1、MaxDetailRows≥Included（ReturnDetails=true）、MaxWorkingSet/Buffered/Root预算先checked预留；return-details=false不分配全明细。峰值/分位及百万/高位负载方法直接复用S7 deming-point-managed-v1与本页§9/DEV-GOV-010，不复制造新性能算法或未测目标。变换前原输入Evidence/SourceSnapshot hash保持；转换后的值/单位/来源映射/方法/ratio/预算加入新QLNI与QLDP。比例或单位变更必须新CalculationId/源方法修订，不只改显示。

| qualification → S7公开字段 | 确定构造/绑定 |
|---|---|
| NumericalRequest.OperationId / Tasks | 原NumericRequest.OperationId；ImmutableArray仅含一个ConstantRatioDemingTask，TaskId=deming-point，不含Pair/Affine/Distribution |
| task XRole/YRole/XUnit/YUnit | Plan.XRole/YRole（非空不同），TargetUnit.Id逐侧传机器ID；每DemingObservation.Unit同目标ID |
| CenterX/ErrorVarianceRatio | DemingNumericInput.CenterX/λ是上述已转换值，task显式给，不由均值自动定CenterX；Slope=YUnit/XUnit |
| Method/PairingPolicy/ErrorVarianceEvidence | 三个NumericDefinitionText分别用S7-DEMING-DEFINITION-V1域+Id/Revision/Body建立DefinitionReference；外层NumericalRequest.Method=task.Method，SelectionPolicy=task.PairingPolicy；无审批/生产角色 |
| Rows.Left/Right.Member | 每DemingBridgeObservation分别NumericalMember(RowId,ObservationReference(SourceObservationId,SourceRevision,newS7SourceHash,EvidenceReference),State,ReasonCode)；State逐位置映射S7 Valid0/Unknown1/Missing2/Unmeasured3/Invalid4/NotApplicable5/Excluded6，不把Value=null当状态 |
| EvidenceReference / Source.ContentHash | EvidenceReference="qualification:qldp/"+SHA256(QLDP)+"/original/"+(OriginalEvidence非null时hex其完整四字段ArtifactRef编码，否则"missing")+"/pair/"+hex(PairId UTF8)+"/x"或"/y"，它是确定派生来源引用，QLDP保留原SourceSnapshot/OriginalEvidence及双侧映射。ContentHash严格按S7 SOURCE域+PairId/role(x或y)/RowId/SourceObservationId/Revision/EvidenceReference?/State/Reason/Unit/Value，排除自身；不用原Evidence.Sha256替代，原hash在QLDP仍可追溯 |
| InputReference的全部9字段 | SnapshotId="qualification-deming/"+SHA256(QLNI)、SnapshotRevision=SourceSnapshot.Revision、Mode=FixedSnapshot、QueryReceiptId="qlni/"+SHA256(QLNI)、SourceBoundary="qldp/"+SHA256(QLDP)、ContentHash=最后S7 INPUT hash、WatermarkId=null、ReadComplete=显式true、CanReplay=true仅冻结内存输入 |
| InputClosure全部6字段 | ExpectedMembers=ExpectedRows(计划Pair数)、ExpectedMemberSetHash=S7 MEMBER-SET域+count(Int32)+排序PairId字符串、ReadComplete/PopulationClosed取已核true、ClosureReceiptReference="qualification:"+hex(原SourceSnapshot的完整四字段ArtifactRef编码)、Gaps=Empty（上述每计划对均已形成行）。Expected/实际对守恒，非Valid不删除 |
| Policy全部10字段 | engineering-binary64-v1 Id/Revision=1，九参数严格S7引用的§7.1.3.1常量；Identity.ContentHash按S7 POLICY域（与旧family不同），不是旧policy hash。NumericRequest.NumericPolicyId与原Method.NumericPolicy须对应相同数值政策内容；Source仍原引用，QLNI绑定它 |
| Budget全部13字段 | DemingBridgeBudget原13字段逐位置构造NumericalBudget；不从N01的256bits误套S7。数值上限/字节/root剩余/单调deadline取较小值，若需缩小则先形成冻结的有效Budget并编码入QLNI+S7请求再接纳；WallClock/Drain均有限，不在派发后偷偷更改身份 |
| Completion/Result关联 | OperationId/TaskId/Input/全部定义/CenterX/λ及两侧覆盖核同请求；错误匹配QLF-PORT-CONTRACT，保留原工作并排空，不把不相关上游结果当本次数值 |

QLDP只含原SourceSnapshot、Stratum、全部公开Plan/SourceErrorVarianceRatio原λ、全部已转换Pairs（含OriginalEvidence/State/Unit/Value），不含QLNI或S7 Input/Request hash；QLNI含原NumericRequest全字段与完整DemingNumericInput，不含任何S7 hash。随后用已固定QLDP/QLNI的hash作为S7输入身份/来源引用，计算S7 SOURCE→Task/PairSequence→INPUT（排除自身ContentHash）→REQUEST（包含已得Input.ContentHash），是单向DAG。不能把S7 Input hash写回QLNI、把自身Definition hash写入Body、把InputOrderHash冒PairSequence或从未来NumericResult反算输入。正文中"newS7SourceHash"/empty临时hash只是builder内部，封口前不送引擎；S7全字段编码唯一按上游§7.1.3.10，Adapter typed writer按原规则实现，无新算法。

**能力、入口与Owner。** IQualificationNumerics.Capabilities的Methods含ConstantRatioDeming只在注入的INumericalStatistics.NumericalCapabilities.TaskKinds含确切ConstantRatioDemingTask、支持域及实际Backends身份完整且本发布可运行时声明；不因API版本同0.3、S7规范存在或Unverified标志自动宣称有运行能力。Backend.Validation仍原值，不自行改Validated；正常Host逐7字段核对原engine.NumericalCapabilities.Backends，不仅核非空或两处投影互相一致；无实际运行Capabilities→该附加NumericResult的deming.slope/deming.center-intercept均Unavailable/QLF-METHOD-UNSUPPORTED、NumericTaskDetail.Deming=null、Provenance.ResultState=NotDispatched（本桥未派发标记，不冒充上游ResultState）、Backends与MemberSequenceHash空、BackendCompletionId/StatisticsSnapshotId空、CoreApiVersion/ImplementationVersion记录桥自身实际版本、原SourceSnapshot/QLNI/Method/Selection/ExpectedRows保持，Diagnostics明确缺能力；不伪造上游Input/Run/Computation。上层Criteria=NotEvaluated，不派发ComputeNumerical。合法未可识别数值域由实际S7返回对应状态，不无故改成缺能力；没有重选Pearson/OLS/native ODR。

同步Analyze的纯托管S7可调用INumericalStatistics.ComputeNumerical（本片无native不可中断段），只在同Root已预留engine/request/输出/内存并实际声明可同步运行时允许，不能用.Result包装异步。异步桥在Root.StartOwned内调用ComputeNumericalAsync(...).AsTask()一次→保存原acceptance→接纳返回时登记NumericalRun租约/Completion/通知（未消费也不能失引用）→等原Completion。waitToken只结束等待，业务token由原操作CTS持有；超时/取消请求由原run.CancelAsync独立有限等待、QueryNumericalOperationAsync用原OperationId查真实Status/DrainState。Dispose run/engine原任务启动前预留，真实Drained/CanReuseResources/全部借用资源归还后才回收容量，未确认继续Root；迟到接纳返回run也进入原Root当前Owner，不销毁engine或再算一次。Bridge不Dispose宿主共享engine；Host专用engine以Root.RegisterDisposable明示所有权，Root关门先取消/排空bridge原工作，再Dispose专用engine，engine不递归Root.Close。业务结果和cleanup分轴沿§12，不在finally空Dispose/假完成。桥的返回Task不得依赖Root.Close才能完成：它只等本S7 run自己的实际释放屏障/Dispose，不等待Host dedicated-engine Dispose（该engine由Root在桥已退出后清理），避免Close等桥、桥再等Close/engine的环。

**无损结果投影。** NumericTaskDetail.Deming承载全部专用结果：TaskId/Stratum、总体Coverage及Left/Right Coverage全部8个Int64、Method/Pairing/ErrorVarianceEvidence与源正文、CenterX/λ、LineKind、Moments Count/AnchorX/Y/MeanX/Y/MeanOffsetX/Y/Sxx/Syy/Sxy、Slope、CenterIntercept、Computation全部11字段及Details全部5字段。NumericScaledValue仅按原State/Mantissa/Exponent2/Unit/Code保留：非零Computed须1≤|mantissa|<2；零(0,0)，非Computed无mantissa/exponent。不得为了ReportValue显示先Math.ScaleB恢复超大原矩；转普通double的消费者超域必须Unavailable/RangeLoss。MeanOffset独立保留，不用Mean−Anchor恢复已舍入偏移。

NumericScalarValue逐上游State/Value/Unit/Code，Slope与CenterIntercept各自仅在原State=Computed且Value finite时Available；Horizontal/Vertical/Unidentified方向诊断保留而两系数Undefined/STAT.DEMING_UNIDENTIFIABLE，n<2为InsufficientData。NumericUncertain/RangeLoss/UnsupportedDomain即使Moments已可靠也不给有效系数；Slope可靠、CenterIntercept量程外Unsupported时分别保留，不把整结果抹空或补零。Computation保留MethodRevision/ScaleExponentX/Y/NormalizedRatio/Correlation/RelativeEigenGap/RootBranch/PeakIntegerBits/PairsVisited/PairSequenceHash/Backend全部原字段，Backend的Id/Version/SourceCommit/BuildHash/FloatingPointProfile/Interruptible/Validation映到NumericBackendIdentity。Diagnostics原Code及Arguments（含Pair/侧/位数/阶段）须保留，新增BCL NumericBackendDiagnostic(Code,MessageKey,MetricId,ObservationId,Arguments有序string列表)见公开DTO；BackendDiagnostics逐条保留原task.Diagnostics、ResultBackendDiagnostics逐条保留原NumericalResult.Diagnostics，各自顺序/重复均保留，不能合并去重而丢层级，也不只日志。Details为有序PairId+CenteredX/Y/PredictedY/VerticalResidual，仅垂直描述，不作误差修正或正交距离。

外层NumericalProvenance的Input/Closure/Method/Selection/Policy/Backends与MemberSequenceHash保持原值及本桥原SourceSnapshot/QLNI关联：NumericDemingIdentity显式保存9字段Input、6字段Closure（本桥GapCount必须0，非0为PORT-CONTRACT而不是丢gap）、各S7 DefinitionReference完整三字段、9政策参数+新policy hash、有效13字段Budget及MemberSequenceHash；后端列表/版本沿NumericProvenance，不能只留hash而丢原字段；S7 Computation.PairSequenceHash是其PAIR-SEQUENCE域，不能强行等于QLMS。NumericDemingDetail另携UpstreamInputSha256/UpstreamRequestSha256用于身份核对，完整NumericResult纳入既有QualificationReport.NumericalResults。Values若需要列表投影仅新增deming.slope/deming.center-intercept，不把ScaledValue塞进double map；完整资格解释以专用字段为准。独立配对/参考/误差比来源的物理真实性与客户判据仍由原Owner，点估计Computed不赋予用途批准。

#### A.3.1.1.1 两个有限Host完整配方与Golden消费者

Adapter仅公开声明，不是已存在实现，后续接线只能按本页和S7：

```csharp
// Asun.Modules.Qualification.Statistics; this optional bridge assembly alone references Statistics.
public sealed class QualificationDemingStatisticsBridge : IQualificationNumerics {
    public QualificationDemingStatisticsBridge(QualificationRoot root,RootReservation reservation,
        Asun.Modules.Statistics.INumericalStatistics engine);
    public NumericCapabilities Capabilities { get; }
    public NumericRequest Materialize(QualificationRequest request,string stratum);
    public Asun.Modules.Statistics.NumericalRequest CreateNumericalRequest(NumericRequest request);
    public byte[] EncodeS7Request(Asun.Modules.Statistics.NumericalRequest request);
    public string GetS7InputSha256(Asun.Modules.Statistics.NumericalRequest request);
    public string GetS7PairSequenceSha256(Asun.Modules.Statistics.NumericalRequest request);
    public ValueTask<NumericResult> CalculateAsync(NumericRequest request,CancellationToken token);
}
```

Materialize执行前述验证/转换→有效13字段Budget先冻结→实际QLDP/QLMS/QLNI生成；SourceSnapshot取原请求，Method/Analysis保留原字段；SelectionPolicy=Deming.Pairing.Source、SubsetApproval=null、ReadComplete/PopulationClosed=true来自源封口，ExpectedRows按计划Pair数、Members全部两侧原观测、MethodId=ConstantRatioDeming、Input=上述DemingNumericInput、NumericPolicyId=engineering-binary64-v1、UnitSystem="X="+目标ID+";Y="+目标ID、InputOrderHash=QLMS hash。CreateNumericalRequest纯typed builder按上述表，调用前返回封口非空hash；它不执行/登记上游operation，不能把本例helper名假当statistics公共Codec。CalculateAsync接受相同完整NumericRequest执行已有异步入口；同ID异闭包拒绝/原查询、同ID同闭包不重新计算。

以下两独立软件Host配方均给完整来源、单位/ratio/Center、原Task与有限排空；它们从资格同层原观测创建S7输入，**不会与S7的2011/1979-byte原Host请求字节相等**（来源/ID不同）。原S7正常/交换Golden直接引用上游原件作为数值/编码消费者，不复制第二公式；本桥不同来源identity另断言。

```csharp
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.Qualification;
using Asun.Modules.Qualification.Statistics;
using StatisticsEngine = Asun.Modules.Statistics.StatisticsEngine;
using EngineLimits = Asun.Modules.Statistics.EngineLimits;

static QualificationRequest CreateDemingQualificationRequest(bool converted)
{
    static ArtifactRef Ref(string ns,string id,string body) =>
        QualificationCodec.ArtifactFromBytes(ns,id,"1",Encoding.UTF8.GetBytes(body));
    static NumericDefinitionText Def(string id,string body) => new(id,"1",body,Ref("definition",id,body));
    var mm=new UnitId("mm","L","1");var um=new UnitId("um","L","1");
    var xTransform=new DemingAxisConversion(mm,converted ? um : mm,converted ? 1000 : 1,
        converted ? 10 : 0,Ref("unit-transform","x",converted ? "x'=1000*x+10;mm-to-um;fixture" : "x'=x;mm;fixture"));
    var yTransform=new DemingAxisConversion(mm,mm,1,0,Ref("unit-transform","y","y'=y;mm;fixture"));
    var method=Def("constant-ratio-deming-exact-center-v1",
        "unweighted;independent-pairs;uncorrelated-errors;constant-known-varY-over-varX;"+
        "exact-dyadic-centering;scaled-stable-root;point-only;no-imputation;no-OLS-fallback");
    var pairing=Def("qualification-pairing-v1","fixture-only;PairId-ordinal;complete-independent-pairs;no-cluster;no-exclusion;no-imputation");
    var ratio=Def("qualification-ratio-v1",converted
        ? "fixture-only;raw-varY-over-varX=1;raw-mm2/mm2;target-mm2/um2;lambda'=0.000001;constant-uncorrelated;no-physical-qualification"
        : "fixture-only;varY-over-varX=1;units=mm2/mm2;constant-uncorrelated;no-physical-qualification");
    var budget=new DemingBridgeBudget(3,3,1,1,1,3,64,4096,1048576,4194304,
        TimeSpan.FromSeconds(5),TimeSpan.FromSeconds(2),64);
    var deming=new DemingPointPlan("reference","test",new QuantityValue(1,mm),xTransform,yTransform,
        method,pairing,ratio,true,budget);
    double[] x={0,1,2},y={0,1,3};var cells=new List<PlanCell>();var obs=new List<Observation>();
    var pairs=new List<AgreementPair>();
    for (int i=0;i<3;i++) {
        string pair="P"+i,physical="SPEC"+i;
        foreach (string side in new[] {"x","y"}) {
            string id=side+"-"+pair,cell="cell-"+id;
            cells.Add(new PlanCell(cell,new PhysicalSpecimenId(physical),side,1,
                RepeatLevel.IndependentCapture,"","Deming.v1"));
            obs.Add(new Observation(new ObservationId(id),cell,new PhysicalSpecimenId(physical),
                "capture-"+id,"","target-"+pair,new DateTimeOffset(2026,10,11,0,0,i,TimeSpan.Zero),
                RepeatLevel.IndependentCapture,new Measured(new QuantityValue(side=="x" ? x[i] : y[i],mm)),
                Ref("fixture-measurement",id,"fixture:"+id+";record="+(side=="x" ? x[i] : y[i]).ToString(System.Globalization.CultureInfo.InvariantCulture))));
        }
        pairs.Add(new AgreementPair(pair,"fixture-layer",new ObservationId("x-"+pair),new ObservationId("y-"+pair)));
    }
    var pb=QualificationCodec.EncodePlanContent(cells,"machine-side","no-randomness","fixture-independent-pairs",6);
    var plan=new ExperimentPlan(QualificationCodec.ArtifactFromBytes("plan","deming","1",pb),cells,
        "machine-side","no-randomness","fixture-independent-pairs",6);
    var ib=QualificationCodec.EncodeInputContent(plan,obs);
    var source=QualificationCodec.ArtifactFromBytes("snapshot",converted ? "deming-unit" : "deming-noise","1",ib);
    var template=CreateStudyRequest(); // existing §12 helper; has declared synthetic evidence resources
    return template with {CalculationId=new CalculationId(converted ? "D7Q-UNIT" : "D7Q-NOISE"),
        ExperimentId=new ExperimentId("D7Q-STUDY"),
        Method=new MethodRef("IndependentPairsBlandAltman+ConstantRatioDeming","1",ratio.Source,
            template.Method.NumericPolicy,Ref("backend-plan","deming","planned-S7;not-a-released-backend")),
        Scope=new Scope("length","1",mm,"synthetic-support","two-fixture-sides","fixture-only"),
        Input=new InputSnapshot(source,6,ib.LongLength,source.Sha256,obs,plan),
        Resources=template.Resources with {MaxResidentBytes=8388608},
        Analysis=new AgreementAnalysis("IndependentPairsBlandAltman+ConstantRatioDeming",2,1,pairing.Source,pairs,deming),
        Reference=null,Criteria=null,Assumptions=new[] {new AssumptionEvidence("deming-fixture",
            "three distinct synthetic specimens; independent pairs; constant uncorrelated errors; no randomness; no physical qualification",
            "Declared",new[] {pairing.Source,ratio.Source})}};
}
static void AssertDemingHostResult(QualificationDemingStatisticsBridge bridge,
    Asun.Modules.Statistics.INumericalStatistics engine,NumericRequest request,NumericResult result,bool converted)
{
    static void Require(bool ok,string field) {if (!ok) throw new InvalidOperationException(field);}
    static void Near(NumericScalarValue value,double expected,string unit) {
        Require(value.State=="Computed" && value.Value is { } v && double.IsFinite(v) &&
            Math.Abs(v-expected)<=1e-12*(expected==0 ? 1 : Math.Abs(expected)) && value.Unit==unit && value.Code is null,"scalar");
    }
    static void Scaled(NumericScaledValue value,double mantissa,int exponent,string unit) {
        Require(value.State=="Computed" && value.Mantissa==mantissa && value.Exponent2==exponent &&
            value.Unit==unit && value.Code is null,"scaled");
    }
    static void Coverage(NumericCoverage value) {
        Require(value==new NumericCoverage(3,3,0,0,0,0,0,0),"coverage");
    }
    Require(result.Tasks.Count==1 && result.Tasks[0].Deming is not null,"one-S7-task");
    var detail=result.Tasks[0].Deming!;var input=(DemingNumericInput)request.Input;
    Require(detail.TaskId=="deming-point" && detail.Stratum==input.Stratum && detail.LineKind=="Finite","identity");
    Coverage(detail.Coverage);Coverage(detail.LeftCoverage);Coverage(detail.RightCoverage);
    Require(detail.Method==input.Plan.Method && detail.Pairing==input.Plan.Pairing &&
        detail.ErrorVarianceEvidence==input.Plan.ErrorVarianceEvidence &&
        detail.CenterX==input.CenterX && detail.ErrorVarianceRatio==input.ErrorVarianceRatio,"policy");
    Require(detail.CenterX==(converted ? 1010 : 1) && detail.ErrorVarianceRatio==(converted ? 0.000001 : 1),"unit-ratio");
    Coverage(result.Tasks[0].Coverage);
    Require(detail.Moments.Count==3 && detail.Moments.AnchorX==(converted ? 10 : 0) &&
        detail.Moments.AnchorY==0 && detail.Computation.PairsVisited==3,"moments-count");
    Near(detail.Moments.MeanX,converted ? 1010 : 1,converted ? "um" : "mm");
    Near(detail.Moments.MeanY,4d/3,"mm");
    Scaled(detail.Moments.MeanOffsetX,converted ? 1.953125 : 1,converted ? 9 : 0,converted ? "um" : "mm");
    Scaled(detail.Moments.MeanOffsetY,1.3333333333333333,0,"mm");
    Scaled(detail.Moments.Sxx,converted ? 1.9073486328125 : 1,converted ? 20 : 1,converted ? "um²" : "mm²");
    Scaled(detail.Moments.Syy,1.1666666666666667,2,"mm²");
    Scaled(detail.Moments.Sxy,converted ? 1.46484375 : 1.5,converted ? 11 : 1,converted ? "um·mm" : "mm·mm");
    // Fixed expected coefficients from S7 D7-004; no regression algorithm is implemented here.
    Near(detail.Slope,converted ? 0.001538761977977345 : 1.538761977977345,converted ? "mm/um" : "mm/mm");
    Near(detail.CenterIntercept,4d/3,"mm");
    var backend=detail.Computation.Backend;
    Require(backend.Id=="managed-deming-exact-center-v1" && backend.Version=="1" &&
        backend.FloatingPointProfile=="exact-dyadic-binary64-rne-no-fma-v1" && backend.Interruptible &&
        !string.IsNullOrWhiteSpace(backend.SourceCommit) && !string.IsNullOrWhiteSpace(backend.BuildHash),"backend");
    Require(System.Linq.Enumerable.Any(engine.NumericalCapabilities.Backends,b =>
        b.Id==backend.Id && b.Version==backend.Version && b.SourceCommit==backend.SourceCommit &&
        b.BuildHash==backend.BuildHash && b.FloatingPointProfile==backend.FloatingPointProfile &&
        b.Interruptible==backend.Interruptible && b.Validation.ToString()==backend.Validation),"actual-backend-identity");
    Require(detail.Computation.PeakIntegerBits>0 && detail.Computation.PeakIntegerBits<=input.Plan.Budget.MaxIntegerBits &&
        detail.Computation.MethodRevision=="constant-ratio-deming-exact-center-v1","computation");
    Require(detail.Computation.ScaleExponentX==(converted ? 10 : 1) &&
        detail.Computation.ScaleExponentY==1 && detail.Computation.RootBranch=="direct-positive-d" &&
        detail.Computation.NormalizedErrorVarianceRatio==(converted ? 0.262144 : 1) &&
        detail.Computation.Correlation is { } rho && double.IsFinite(rho) &&
        Math.Abs(rho-0.9819805060619657)<=1e-12 &&
        detail.Computation.RelativeEigenGap is { } gap && double.IsFinite(gap) && gap>Math.ScaleB(1d,-40),"scaled-computation");
    Require(result.Provenance.Backends.Count>0 &&
        System.Linq.Enumerable.Contains(result.Provenance.Backends,backend),"backend-provenance");
    var upstream=bridge.CreateNumericalRequest(request);
    string requestHash=QualificationCodec.ArtifactFromBytes("s7-request","assert","1",bridge.EncodeS7Request(upstream)).Sha256;
    Require(detail.UpstreamInputSha256==bridge.GetS7InputSha256(upstream) &&
        detail.UpstreamInputSha256==upstream.Input.ContentHash && detail.UpstreamRequestSha256==requestHash &&
        detail.Computation.PairSequenceHash==bridge.GetS7PairSequenceSha256(upstream),"S7-hashes");
    string qlni=QualificationCodec.ArtifactFromBytes("numeric","assert","1",QualificationCodec.EncodeNumericRequest(request)).Sha256;
    Require(result.Provenance.SourceSnapshot==request.SourceSnapshot && result.Provenance.DerivedInputSha256==qlni &&
        result.Provenance.OperationId==request.OperationId && result.Provenance.ResultState=="Complete","provenance");
    static bool Definition(NumericS7DefinitionReference a,Asun.Modules.Statistics.DefinitionReference b) =>
        a.Id==b.Id && a.Revision==b.Revision && a.ContentHash==b.ContentHash;
    var identity=detail.Identity;var si=upstream.Input;var sc=upstream.Closure;var sp=upstream.Policy;
    Require(identity.Input.SnapshotId==si.SnapshotId && identity.Input.SnapshotRevision==si.SnapshotRevision &&
        identity.Input.Mode==si.Mode.ToString() && identity.Input.QueryReceiptId==si.QueryReceiptId &&
        identity.Input.SourceBoundary==si.SourceBoundary && identity.Input.ContentHash==si.ContentHash &&
        identity.Input.WatermarkId==si.WatermarkId && identity.Input.ReadComplete==si.ReadComplete &&
        identity.Input.CanReplay==si.CanReplay,"input-identity");
    Require(identity.Closure.ExpectedMembers==sc.ExpectedMembers &&
        identity.Closure.ExpectedMemberSetHash==sc.ExpectedMemberSetHash &&
        identity.Closure.ReadComplete==sc.ReadComplete && identity.Closure.PopulationClosed==sc.PopulationClosed &&
        identity.Closure.ClosureReceiptReference==sc.ClosureReceiptReference &&
        identity.Closure.GapCount==0 && sc.Gaps.Length==0 && identity.SubsetApproval is null &&
        Definition(identity.Method,upstream.Method) && Definition(identity.SelectionPolicy,upstream.SelectionPolicy) &&
        Definition(identity.Pairing,upstream.SelectionPolicy) &&
        Definition(identity.ErrorVarianceEvidence,((Asun.Modules.Statistics.ConstantRatioDemingTask)upstream.Tasks[0]).ErrorVarianceEvidence),"closure-definitions");
    Require(Definition(identity.Policy.Identity,sp.Identity) && identity.Policy.RankAbsolute==sp.RankAbsolute &&
        identity.Policy.RankRelative==sp.RankRelative && identity.Policy.DecompositionTolerance==sp.DecompositionTolerance &&
        identity.Policy.PsdTolerance==sp.PsdTolerance &&
        identity.Policy.CorrelationRoundoffTolerance==sp.CorrelationRoundoffTolerance &&
        identity.Policy.TQuantileAbsolute==sp.TQuantileAbsolute && identity.Policy.TQuantileRelative==sp.TQuantileRelative &&
        identity.Policy.FQuantileRelative==sp.FQuantileRelative && identity.Policy.TailRelative==sp.TailRelative &&
        identity.Budget==input.Plan.Budget && identity.MemberSequenceHash==result.Provenance.MemberSequenceHash,"numeric-policy");
    Require(result.Provenance.ReadComplete && result.Provenance.PopulationClosed && result.Provenance.ExpectedRows==3 &&
        result.Provenance.Method==request.Method && result.Provenance.SelectionPolicy==request.SelectionPolicy &&
        result.Provenance.SubsetApproval is null && !string.IsNullOrWhiteSpace(result.BackendCompletionId) &&
        !string.IsNullOrWhiteSpace(result.Provenance.StatisticsSnapshotId) &&
        !string.IsNullOrWhiteSpace(result.Provenance.CoreApiVersion) &&
        !string.IsNullOrWhiteSpace(result.Provenance.ImplementationVersion),"source-provenance");
    Require(detail.Details.Count==3,"all-details");
    for (int i=0;i<3;i++) {
        var row=detail.Details[i];Require(row.PairId=="P"+i,"pair-order");
        Near(row.CenteredX,(converted ? 1000 : 1)*(i-1),converted ? "um" : "mm");
        double y=i==2 ? 3 : i;
        Near(row.CenteredY,y-4d/3,"mm");
        double predicted=detail.CenterIntercept.Value!.Value+detail.Slope.Value!.Value*row.CenteredX.Value!.Value;
        Near(row.PredictedY,predicted,"mm");Near(row.VerticalResidual,y-predicted,"mm");
    }
}
static bool DemingCleanupConfirmed(RootCloseResult state) =>
    state.Drained && state.Completion.IsCompletedSuccessfully && state.Diagnostics.Count==0;
static string AppendDemingCleanupError(string? prior,string next) =>
    string.IsNullOrEmpty(prior) ? next : prior+";"+next;
static async Task<HostCompletion> RunDemingQualificationHostAsync(QualificationRecoveryOwner owner,bool converted)
{
    string rootId=converted ? "root-deming-unit" : "root-deming-noise";
    QualificationRoot? root=null;QualificationOutcome? business=null;RootCloseResult? cleanup=null;
    string? businessError=null,cleanupError=null;int businessCode=5,cleanupCode=0;
    try {
        root=owner.CreateRoot(rootId,new RootLimits(16777216,1,4,64,16,TimeSpan.FromSeconds(2)));
        var reservation=root.Reserve(rootId,16777216,1,64,16);
        var resources=new DemingHostResources(); // empty, no engine/CTS/task/side effect
        root.RegisterDisposable(reservation,"deming-host-resources",resources);
        var request=CreateDemingQualificationRequest(converted);root.RetainInput(reservation,request);
        var engine=resources.CreateEngine(); // already covered by the registered holder
        var bridge=new QualificationDemingStatisticsBridge(root,reservation,engine);
        var numeric=bridge.Materialize(request,"fixture-layer");
        if (!bridge.Capabilities.Methods.Contains("ConstantRatioDeming")) {
            businessCode=3;businessError="QLF-METHOD-UNSUPPORTED";
        } else {
            var cancel=resources.CreateCancellation(); // strong-held before Register can reject
            root.RegisterCancellation(reservation,cancel);
            resources.CancellationRegistered(); // transfer only after successful atomic registration
            Task<NumericResult> original=root.StartOwned(reservation,"deming-numerics",() =>
                bridge.CalculateAsync(numeric,cancel.Token).AsTask());
            NumericResult result=await original.WaitAsync(TimeSpan.FromSeconds(5));
            AssertDemingHostResult(bridge,engine,numeric,result,converted);
            businessCode=0; // numeric assertion; no production QualificationOutcome or use approval
        }
    } catch (TimeoutException) {businessCode=7;businessError="deming-host-wait-timeout";}
      catch (OperationCanceledException) {businessCode=4;businessError="deming-host-cancelled";}
      catch (Exception e) {businessCode=5;businessError=e.GetType().Name;}
    finally {
        if (root is not null) {
            try {
                Task<RootCloseResult> originalClose=root.CloseAsync(TimeSpan.FromSeconds(2),CancellationToken.None);
                cleanup=await originalClose.WaitAsync(TimeSpan.FromSeconds(2));
                if (!DemingCleanupConfirmed(cleanup)) {
                    cleanupCode=6;
                    cleanupError=AppendDemingCleanupError(cleanupError,"cleanup-unconfirmed-or-diagnostic");
                }
            } catch (Exception e) {
                cleanupCode=6;cleanupError=AppendDemingCleanupError(cleanupError,"close:"+e.GetType().Name);
            }
            try {
                owner.RecordHostCompletion(rootId,new HostCompletion(converted ? "D7Q-UNIT" : "D7Q-NOISE",
                    business,businessError,cleanup,cleanupError,businessCode,cleanupCode));
            } catch (Exception e) {
                cleanupCode=6;cleanupError=AppendDemingCleanupError(cleanupError,"completion-record:"+e.GetType().Name);
            }
        }
    }
    // Keep both axes even when recording failed; Main receives the actual local summary.
    return new HostCompletion(converted ? "D7Q-UNIT" : "D7Q-NOISE",
        business,businessError,cleanup,cleanupError,businessCode,cleanupCode);
}
static async Task<HostCompletion> ObserveDemingHostRootAsync(QualificationRecoveryOwner owner,
    string rootId,HostCompletion completion)
{
    try {
        if (owner.QueryRoot(rootId) is null) {
            // Atomic CreateRoot failure: no root to observe. No acknowledgement has occurred yet.
            if (completion.Cleanup is null && completion.BusinessExitCode!=0) return completion;
            return completion with {CleanupExitCode=6,
                CleanupError=AppendDemingCleanupError(completion.CleanupError,"root-registration-missing")};
        }
        // One bounded observation of the original root; no second Close or fresh cleanup deadline.
        Task<RootCloseResult> originalObserve=owner.ObserveRootAsync(rootId,TimeSpan.FromSeconds(1),CancellationToken.None);
        RootCloseResult state=await originalObserve.WaitAsync(TimeSpan.FromSeconds(1));
        completion=completion with {Cleanup=state}; // original business and previous cleanup errors retained
        if (!DemingCleanupConfirmed(state)) completion=completion with {CleanupExitCode=6,
            CleanupError=AppendDemingCleanupError(completion.CleanupError,"recovery-unconfirmed-or-diagnostic")};
        bool recorded=false;
        try {owner.RecordHostCompletion(rootId,completion);recorded=true;}
        catch (Exception e) {completion=completion with {CleanupExitCode=6,
            CleanupError=AppendDemingCleanupError(completion.CleanupError,"recovery-record:"+e.GetType().Name)};}
        if (DemingCleanupConfirmed(state) && recorded && owner.QueryHostCompletion(rootId)==completion)
            owner.AcknowledgeReleased(rootId); // only the real release barrier and recorded summary allow removal
        return completion; // late recovery never upgrades a prior failure code to zero
    } catch (Exception e) {
        return completion with {CleanupExitCode=6,
            CleanupError=AppendDemingCleanupError(completion.CleanupError,"observe-or-acknowledge:"+e.GetType().Name)};
    }
}
static async Task<int> DemingNoiseMain(string[] args)
{
    var owner=new QualificationRecoveryOwner("deming-noise-process",1,64,16,16777216);
    HostCompletion completion=await RunDemingQualificationHostAsync(owner,false);
    completion=await ObserveDemingHostRootAsync(owner,"root-deming-noise",completion);
    int code=completion.CleanupExitCode!=0 ? completion.CleanupExitCode : completion.BusinessExitCode;
    GC.KeepAlive(completion);GC.KeepAlive(owner);return code;
}
static async Task<int> DemingUnitMain(string[] args)
{
    var owner=new QualificationRecoveryOwner("deming-unit-process",1,64,16,16777216);
    HostCompletion completion=await RunDemingQualificationHostAsync(owner,true);
    completion=await ObserveDemingHostRootAsync(owner,"root-deming-unit",completion);
    int code=completion.CleanupExitCode!=0 ? completion.CleanupExitCode : completion.BusinessExitCode;
    GC.KeepAlive(completion);GC.KeepAlive(owner);return code;
}

// Registered empty before creating engine/CTS; Root retains any failed-transfer resource.
sealed class DemingHostResources : IAsyncDisposable
{
    private StatisticsEngine? engine;
    private CancellationTokenSource? pendingCancellation;
    private Task? disposal;
    private readonly object gate=new();
    public StatisticsEngine CreateEngine() {
        if (engine is not null) throw new InvalidOperationException("engine-already-created");
        return engine=new StatisticsEngine(new EngineLimits(2,2));
    }
    public CancellationTokenSource CreateCancellation() {
        if (pendingCancellation is not null) throw new InvalidOperationException("cancellation-already-created");
        return pendingCancellation=new CancellationTokenSource();
    }
    public void CancellationRegistered() {pendingCancellation=null;} // Root now owns CTS disposal
    public ValueTask DisposeAsync() {
        lock (gate) {return new ValueTask(disposal ??= DisposeCoreAsync());}
    }
    private async Task DisposeCoreAsync() {
        // RegisterCancellation failed before commit: no bridge work was started.
        var pending=pendingCancellation;pendingCancellation=null;
        try {if (pending is not null) {try {pending.Cancel();} finally {pending.Dispose();}}}
        finally {if (engine is not null) await engine.DisposeAsync();}
    }
}
```

每个Exe独立engine/root/input/source/hash；两个Main各编译入口名Main。等待5s、cleanup单总2s，Main再对原Root有限Observe最多1s（不是新的cleanup期限），外层隔离软件进程10s截止。DemingCleanupConfirmed要求Drained、原Completion.IsCompletedSuccessfully且Diagnostics空；本小型软件Host保守地将任何cleanup诊断记非零6，原Diagnostics完整保留在HostCompletion.Cleanup，不从一个bool推成功。Close/Observe的控制Task由原Root/Owner内部强持，不进入自身排空依赖；超时/故障/取消或未确认的Completion均不无限await、不重建Root。RecordHostCompletion异常独立追加cleanupError，不改businessError；Run返回完整HostCompletion，Main在Owner外仍强持该本地摘要，记录失败不会把业务/清理证据都丢掉。最终Observe保留旧非零码，只有三项确认及HostCompletion已在原Owner记录并回读一致才AcknowledgeReleased；Acknowledge须按原Root契约复核所有Work/lease归还后原子移除，拒绝/异常不部分移除。未确认或摘要未记录则原Root/输入/原Task/迟到租约与槽仍在Owner，Main强持Owner和摘要到软件进程退出；长寿命宿主必须沿§12保留或移交Owner和该摘要，不返回裸int后失根。软件隔离进程非零退出/外层终止不证明设备/native归还。

本Host的注册确定语义：RegisterDisposable/RegisterCancellation先校验同根有效reservation、独立ID/引用和预留容量；拒绝必须发生在所有权提交之前，成功后唯一Owner为Root，不允许部分登记再向调用方抛拒绝。预先登记空DemingHostResources（构造不创建engine/CTS/Task），登记失败时只有无副作用空对象；engine构造成功即写入已登记holder，只有holder.DisposeCoreAsync调用原engine.DisposeAsync一次，不再单独注册或双Dispose。CTS先由holder强持，RegisterCancellation失败则holder保持并在无桥Work启动的Close路径Cancel/Dispose；成功返回后CancellationRegistered以不可抛字段赋值移交CTS释放权给Root。两个Main各自是本Root唯一Close/注册写入者，转交之前不并发外部Close；成功注册和移交之间不存在清理竞争。holder Dispose原Task归Root，Root先取消业务CTS并等bridge实际退出再Dispose holder/engine；holder/engine不调用或等待Root.Close。预约覆盖holder、engine、CTS、原启动/Dispose及恢复控制槽，不赌启动后登记容量；Root最终Completion必须等这些已登记资源真实归还。

Host字段business=null表示这是NumericResult桥的测试assertion（无产品Outcome），BusinessExitCode/BusinessError仍记录数值检查与cleanup两轴；不把空Outcome解释成物理PASS。AssertDemingHostResult是本轮桥接测试消费者的具名断言helper（完整正文已给），其公开字段与固定期望如下，不依赖会话或未声明算法：必须Result.Tasks.Count=1且Deming非null、TaskId=deming-point、三覆盖Expected=Included=3其它0、LineKind=Finite、n=PairsVisited=3、两系数Computed、原Definition/Unit/λ/Center/来源hash逐字段相同、Details=3原PairId，backend实际Id/Version/FloatingPointProfile匹配S7且SourceCommit/BuildHash非空、Validation保持原值；源QLNI与UpstreamInput/Request/PairSequence各核对应codec。该helper按以下QDEM-01/02的期望和S7误差口径，任何不符抛InvalidOperationException；不能因未发布能力而skip返回0。

| 新Case/原S7消费者 | 输入/固定期望（只验证桥，不另造数值算法） |
|---|---|
| QDEM-01 / D7-004 | Noise Host，x=(0,1,2)mm、y=(0,1,3)mm、λ=1、CenterX=1；n=3、Anchor=(0,0)、Mean=(1,4/3)、Sxx=2/Syy=14/3/Sxy=3（各原ScaledValue）、Slope=1.538761977977344969…（S7 D7-004 oracle）、CenterIntercept=4/3；明确不等OLS=1.5；双侧六个Source原证据不共hash，全部3明细 |
| QDEM-02 / D7-006变换规则 | Unit Host仅x'=1000x+10 um，y'=y mm，λ'=1e-6 mm²/um²、CenterX'=1010um；MeanX=1010、Sxx=2000000um²/Syy=14/3mm²/Sxy=3000um·mm、Slope约0.001538761977977344969 mm/um、CenterIntercept=4/3mm；原SourceSnapshot内容与Noise同原数值/原hash但原ID不同、新QLDP/QLNI/S7 SOURCE/INPUT/REQUEST均不同，不能沿用λ=1或仅换标签 |
| QDEM-03 / D7-001/002原Golden | 直接消费上游normal/swap两个原件，Expected145-byte hashes分别88c350f432361b7beba36086695faff61143d313d6f93386be9656ab8bd908e0、a40f12f9948b4b1ce70f888dac973c43ed7f3311a78cc1ae37a29a0cd2322f8a；原Request2011/1979-byte及26项字段Golden沿主控已核结果，不重建或复制其算法/完整hex |
| QDEM-04 / D7-008/009/010 | 同fixture原ID和新封口值/身份，x=(-1,0,1)、y=(1,-2,1)，CenterX=0，λ=1/3/4分别Vertical/Unidentified/Horizontal；λ=3表示各向同性，不是除3。三种两系数Undefined，不∞/0；n0/n1 InsufficientData，n1的零尺度矩仍可靠；缺对/Failed/Excluded由RequireAll阻断Count0、coverage保留，任何行不删 |
| QDEM-05 / D7-007/012..016 | 消费S7原极端/范围/位数/gap/center案例，bridge只比全部ScaledValue/MeanOffset/状态/Code与可信上游结果，绝不从Pearson或普通double原矩恢复；Slope可靠而CenterIntercept Unsupported只该项Unavailable；明细与矩状态不互相覆盖 |
| QDEM-06 / D7-017/018 | 改任一侧证据revision/hash、role/unit/Center/λ/转换、Pairing/Ratio Body/预算必须新派生身份；重复side ID/PairId、单侧空、非nullcluster与实际来源状态逐字段核对；源ReadComplete=false先阻本桥，不用合成Gaps掩原缺页 |
| QDEM-07 / D7-019/020 | 接纳迟到/原Completion延迟、cancel/墙钟/cleanup失败、同ID异闭包：原acceptance/run/CTS/Cancel/Query/Dispose Task一直归原Root，Close不会等自身或双Disposeengine；未知释放/Completion未成功/cleanup诊断/摘要记录异常均非0；最终有限Observe只查原Root，真释放且摘要记录后才Ack，不再次Compute；空holder注册失败不创建资源、CTS登记拒绝仍由holder强持 |
| QDEM-08 / D7-022及能力门 | ReturnDetails=false空Details，true需3≤MaxDetailRows；超限拒绝，清理无丢Task。实际Capabilities未含S7时零次Compute、Unavailable/NotEvaluated且测试非0；不据文档称后端可运行或Validated |

数值容差与Scale/状态的Golden依上游S7原权威：正常域系数相对1e-12、近零按原尺度绝对门，Mean/Scaled矩为其精确最近偶数投影；本桥记录固定期望仅作消费者断言，不实现另一累计/求根器。缺actual backend时QDEM运行不可声称通过；不添加CI、ODR、误差比估计或用途批准。

### A.3.2 Root 预约、控制任务、恢复与 Fixture公开闭包

RootLimits的bytes/instances/observers/lateLeases>0，MaxTasks≥10；Reservation.ReservedTasks≥10且至少保留8控制/恢复槽和2启动槽；CleanupBudget∈(0,24h]。RecoveryOwner上限是所有根的**总和**，CreateRoot在构造/Factory/任何异步工作之前一次预约limits并登记Root；超限无对象/Task/端口副作用。Root.Reserve核每项不超过所建limits且剩余额度充足，ReservationId/RootId/InstanceId不可伪造/跨根复用。ResourceMetricBudget.Scope仅Operation/Process，Metric与Unit须匹配Sampler能力；Window>0且≤24h，限值有限且非负，AllowedSlope有限且按Unit/s，缺值不判达标。BenchmarkPlan.Profile必须引用完整冻结性能Profile，ResourceBudget仅限制本模块工程资源，不再兼任probe指标门。Profile与RecordedRun只按A.3.3公开DTO及A.5的QLBP/QLBR解析，执行/录制两Host及有限预算也在A.3.3；没有客户目标仍可诊断但Criteria=NotEvaluated。

Factory消耗一个预约且自动登记Service；Factory异常保留已取得租约并归根，不能向调用方丢一个“未成功创建”的半服务。

容量覆盖全部分支：每reservation固定至少4个cleanup控制槽、4个查询/移交槽，其余给操作/端口/订阅/预览；Host小样本32Task槽、16lateLease、8MiB只是软件工程Profile，不承诺工业上界。每个StartOwned在调用delegate前原子预约最多两个Task槽（wrapper+delegate原Task）并登记启动身份，delegate返回的原Task同样被Root强持；二者引用相同只计一个，委托同步抛错时回收未使用槽并保留wrapper异常；无两个剩余槽时不调用delegate。保留至少4个cleanup控制槽与4个查询/移交槽供关闭/恢复，Work不能占用；32包含这8个槽，最多剩24给业务及端口。ControlWait仅为无资源借用的等待包装，Stop/Dispose若真实负责释放则其原Task是Work；root.Close自身协调Task才是ControlWait且不等自己。RegisterTask只用于端口/Service**已在Root拥有的Task**附加名字或无副作用的已启动软件任务，重复同reference不再计容量；不能启动未知provider任务后才赌登记成功。completed Task只有自身全部借用资源真实释放后才可回收槽。接口声明中的RootTaskRole是显式职责，不从字符串taskId猜：

- Work：真实端口/operation/preview/释放工作，Close等待它们及租约退出。
- ControlWait：Close自身、Stop/Dispose等待包装、状态查询/transfer观察的等待包装Task，仍强持但不成为其自身Completion依赖；实际所代表Work由另一已登记原Task承载。
- UiCoordinator：窗口/Dispatcher的协作Task，保留原Task、异常与输入，但不把“UI等Close”反向加入Close资源屏障。真正借用的预览/Unbind释放Task仍按Work计账。

Service.Stop/Dispose只排空本实例工作，不调用Root.Close/Dispose或等待Root的协调Task；Root.Dispose本身是控制协调，不进入自己的Work集合。这样不形成Root等Service.Dispose、Service.Dispose再等Root的环。

Close第一次调用建立单调cleanup总截止，后续调用只能观察/缩短等待，不能续期、重复Dispose或重启停下来的Service。Close停新派发→取消已登记业务CTS→撤订阅/绑定→对已登记Service启动**一次**Stop和Dispose原Task→等真实Work/租约→Drained。DisposeAsync可以等真实完成，但它由Root启动并持有，Host不无限await它；Close等待截止只能返回Drained=false及原Completion/diagnostics。自有Task异常不证明native已排空；资源确认缺失为DrainUnknown，恢复Owner保留byte/slot/原Task/CTS。空根/接纳前异常也有同一有限Close路径。root关闭后返回的Lease由RegisterLateLease进入当前确认Owner串行队列，按LeaseId去重、bytes校账；未取得释放确认不提前删引用。

同进程TransferOffer包含原Root引用、完整RootLimits和预约容量，是运行时移交票据，禁止持久化/跨进程序列化它。BeginTransfer建立一个原TransferId及目标Owner引用，保留原所有权；AcceptTransfer先预约目标limits再原子更新root.currentOwner并确认receipt；源只在Accepted+ResourcesOwned+ConfirmedOwnerId正确时交还容量。Accept异常/响应未知保留源转发表/原Task，通过同TransferId查真实currentOwner；不重新Dispose、不创建第二Root。已确认目标拥有资源后，源转发表只保留身份和查询路由，不再作为第二释放者。ObserveRoot/CloseRoot在转交后路由原Root；AcknowledgeReleased只能在Drained且全部lease归还、HostCompletion已记录时释放该Owner的槽。容量不足不转交，源继续恢复；RecoveryOwner不能被GC finalizer或静态Task列表替代。

Fixture声明仅位于唯一Core.Tests工程的HostExamples测试消费者namespace，不进入产品Core程序集；它们都只依赖本Core+BCL：

```csharp
public enum TestNumericVector { BiasQ01 }
public sealed class TestNumericsPort : IQualificationNumerics {
    public TestNumericsPort(TestNumericVector vector,TimeSpan delay,bool drainLate);
    public NumericCapabilities Capabilities { get; }
    public ValueTask<NumericResult> CalculateAsync(NumericRequest request,CancellationToken token);
}
public sealed class TestLedgerPort : IQualificationOperationLedger {
    public TestLedgerPort(string admissionState);
    public ValueTask<AdmissionReceipt> AdmitAsync(CalculationId id,string requestSha256,CancellationToken token);
    public ValueTask<QualificationOperationSnapshot?> QueryAsync(CalculationQueryRequest query,CancellationToken token);
    public ValueTask RecordAsync(QualificationOperationSnapshot snapshot,CancellationToken token);
    public void ConfirmAdmission(CalculationId id,string requestSha256,bool accepted);
}
public sealed class TestReplayPort : IReplayQualificationReader {
    public TestReplayPort(IReadOnlyList<GoldenCaseResult> cases);
    public ValueTask<ReplayResult> ReadAsync(GoldenPlan plan,CancellationToken token);
}
```

TestNumericsPort支持域只含BiasQ01精确向量；delay∈[0,5s]，drainLate=false在delay/返回前检查token；true等待原delay真实结束再返回，模拟不可中断托管工作，不能提前另起未持有的native任务。TestLedger容量每实例≤16身份，ordinal字典无静态；同ID异hash=Conflict，同ID同hash=Duplicate，不换键；AdmissionUnknown先保留候选记录、Query只读Unknown，ConfirmAdmission只供闩锁测试显式释放原接纳，不触发第二Admit。Query Unknown/Absent不当Completed。TestReplay容量≤100 cases，构造即有界复制、核QLCS hash、返回整份ReplayResult，ExpectedRef=E/ActualRef=A在这个fixture分别解析到相同UTF-8 `result=ok` 原输出，所以exact-v1为Consistent；case metadata/hash不冒充真值资格。所有fixture身份按§12正文内容生成，禁止一个固定hash代替不同plan/snapshot/method正文。

### A.3.3 Benchmark Profile、录制输入与公开执行闭包

此节是本轮新增Benchmark唯一合同，Core/Study/Replay及Root语义沿已闭章节。输入资产为有界BCL值，不带产品表、设备命令、native句柄或任意对象参数；只能执行宿主明确注入的无生产副作用probe。Profile内部工程字段在此冻结，客户目标缺失只影响判断。以下仍是实施声明，未创建产品代码。

```csharp
public sealed record BenchmarkClockIdentity(string DomainId,long Frequency,string Source);
public interface IBenchmarkClock {
    BenchmarkClockIdentity Identity { get; }
    long GetTimestamp();
    Task WaitUntilAsync(long timestamp,CancellationToken token);
}
public sealed record BenchmarkAsset(ArtifactRef Source,ReadOnlyMemory<byte> Bytes);
public interface IBenchmarkAssetReader {
    ValueTask<BenchmarkAsset> ReadAsync(ArtifactRef source,int maxBytes,CancellationToken token);
}
public sealed record WorkloadDimension(string Name,string Unit,long Value);
public sealed record ArrivalSlot(int Iteration,TimeSpan Offset);
public sealed record LatencyTarget(string Stage,int MinimumSamples,
    TimeSpan? P50,TimeSpan? P95,TimeSpan? P99,ArtifactRef? TargetSource);
public sealed record BenchmarkFailureTarget(int MaxFailed,int MaxCancelled,int MaxTimedOut,
    int MaxNotExecuted,ArtifactRef TargetSource);
public sealed record ResourceMetricSpec(string Metric,string Scope,string TargetId,string Unit,
    string Acquisition,string Attribution);
public sealed record BenchmarkSampling(TimeSpan Period,TimeSpan ReadBudget,IReadOnlyList<ResourceMetricSpec> Metrics,
    int MaximumSamples,bool RequireCompleteSampling);
public sealed record BenchmarkLimits(TimeSpan PrepareBudget,TimeSpan InvokeBudget,TimeSpan TotalBudget,
    TimeSpan CleanupBudget,long MaxResidentBytes,int MaxAssetBytes,int MaxDetailRows);
public sealed record BenchmarkProfile(string ProfileId,string Revision,ArtifactRef Environment,
    ArtifactRef Workload,IReadOnlyList<WorkloadDimension> Dimensions,
    IReadOnlyList<ArrivalSlot> Arrivals,IReadOnlyList<LatencyTarget> LatencyTargets,
    BenchmarkSampling Sampling,BenchmarkLimits Limits,BenchmarkFailureTarget? Failures);
public sealed record BenchmarkDecodeLimits(int MaxBytes,int MaxStringBytes,int MaxCollectionItems);
public enum BenchmarkSamplePhase { BeforePrepare, AfterPrepare, AfterWarmup, Measured, AfterProbeRelease }
public enum ProbeOutcome { Succeeded, Failed, Cancelled, TimedOut, NotExecuted }
public enum RecordedOrigin { Executed, SoftwareFixture }
public sealed record ProbeWorker(string WorkerId,string Mode,ArtifactRef Environment);
public sealed record ProbeCapabilities(ArtifactRef Probe,ArtifactRef Build,int MaxParallelism,
    long MaxSessionBytes,int MaxSessionTasks,int MaxSessionLeases,bool SupportsCancellation,
    bool SupportsFreshWorker,bool HasProductionSideEffects);
public sealed record ProbePrepareRequest(string OperationId,string SessionId,int Lane,
    BenchmarkPlan Plan,BenchmarkProfile Profile,BenchmarkClockIdentity Clock,long AcceptedTick,
    TimeSpan RemainingPrepareBudget);
public sealed record ProbeReady(IQualificationLease Lease,ProbeWorker Worker,ArtifactRef Build,
    ArtifactRef Input,BenchmarkClockIdentity Clock,long PrepareStartTick,long PreparedTick);
public sealed record ProbeInvocation(string OperationId,string InvocationId,int Iteration,bool Warmup,
    int Lane,long ReadyTick,long EnqueuedTick,BenchmarkClockIdentity Clock,TimeSpan RemainingInvokeBudget);
public sealed record ProbeRun(string InvocationId,int Iteration,bool Warmup,int Lane,string WorkerId,
    ProbeOutcome Outcome,long ReadyTick,long EnqueuedTick,long? StartTick,long? ActualCompletionTick,
    long? ResourcesReleasedTick,string? OutputSha256,string? Reason);
public sealed record ProbeDrain(string LeaseId,bool Drained,Task Completion,string? Reason);
public interface IBenchmarkProbe {
    ProbeCapabilities Capabilities { get; }
    ValueTask<ProbeReady> PrepareAsync(ProbePrepareRequest request,CancellationToken token);
    Task<ProbeRun> InvokeAsync(ProbeReady ready,ProbeInvocation request,CancellationToken token);
    Task<ProbeDrain> DrainAsync(ProbeReady ready,TimeSpan waitBudget,CancellationToken waitToken);
}
public sealed record SamplerPrepareRequest(string OperationId,ArtifactRef Environment,
    BenchmarkClockIdentity Clock,BenchmarkSampling Sampling,TimeSpan RemainingPrepareBudget);
public sealed record SamplerReady(IQualificationLease Lease,BenchmarkClockIdentity Clock,
    IReadOnlyList<ResourceMetricSpec> Metrics);
public sealed record ResourceSample(long Tick,BenchmarkSamplePhase Phase,string Metric,string Unit,
    string Scope,string TargetId,double? Value,string Attribution,string? Reason);
public sealed record ResourceSampleBatch(IReadOnlyList<ResourceSample> Samples);
public sealed record SamplerDrain(string LeaseId,bool Drained,Task Completion,string? Reason);
public sealed record ResourceSamplerCapabilities(string SamplerId,long MaxSessionBytes,
    int MaxSessionTasks,int MaxSessionLeases,IReadOnlyList<ResourceMetricSpec> Metrics);
public interface IResourceSampler {
    ResourceSamplerCapabilities Capabilities { get; }
    ValueTask<SamplerReady> PrepareAsync(SamplerPrepareRequest request,CancellationToken token);
    ValueTask<ResourceSampleBatch> SampleAsync(SamplerReady ready,BenchmarkSamplePhase phase,
        CancellationToken token);
    Task<SamplerDrain> DrainAsync(SamplerReady ready,TimeSpan waitBudget,CancellationToken waitToken);
}
public sealed record ProbeSessionRecord(string LeaseId,string WorkerId,int Lane,string Mode,
    long PrepareStartTick,long PreparedTick,long? ReleasedTick);
public sealed record BenchmarkRecordedRun(string RunId,CalculationId OriginCalculationId,
    string OriginRequestSha256,RecordedOrigin Origin,string WorkPlanSha256,ArtifactRef Profile,
    ArtifactRef Probe,ArtifactRef Build,ArtifactRef Input,ArtifactRef Environment,
    BenchmarkClockIdentity Clock,long AcceptedTick,long? PreparedTick,long? MeasuredStartTick,
    long? MeasuredEndTick,long? ProbeReleasedTick,long? ResourcesReleasedTick,
    bool Complete,long DroppedSamples,long? CancelRequestedTick,
    IReadOnlyList<ProbeSessionRecord> Sessions,IReadOnlyList<ProbeRun> Attempts,
    IReadOnlyList<ResourceSample> Samples);
public sealed record BenchmarkQuantiles(string Stage,int Samples,TimeSpan? P50,TimeSpan? P95,
    TimeSpan? P99,CriteriaStatus Criteria,string? Reason);
public sealed record ResourceMetricResult(string Metric,string Scope,string TargetId,string Unit,
    string Acquisition,string Attribution,int Samples,double? Baseline,double? SampledPeak,
    double? RetainedDelta,double? Slope,CriteriaStatus Criteria,string? Reason);
public sealed record BenchmarkThroughput(TimeSpan? Window,int Completed,int Succeeded,int InFlight,
    double? CompletedPerSecond,double? SucceededPerSecond);
public sealed record BenchmarkReport(BenchmarkExecutionMode Mode,string RunId,RecordedOrigin Origin,
    ArtifactRef Profile,ArtifactRef? RecordedRun,string WorkPlanSha256,int Planned,int Succeeded,
    int Failed,int Cancelled,int TimedOut,int NotExecuted,bool ResourcesReleased,
    long DroppedSamples,IReadOnlyList<BenchmarkQuantiles> Quantiles,
    IReadOnlyList<ResourceMetricResult> Metrics,CriteriaStatus Criteria,
    IReadOnlyList<ProbeRun> Attempts,IReadOnlyList<ResourceSample> Samples,
    BenchmarkThroughput Throughput,BenchmarkRecordedRun SourceRun);
```

**字段与有效域。** ProfileId/Revision、RunId、WorkerId、InvocationId、DomainId、TargetId均非空NFC，string≤4096 UTF-8 bytes；hash为64字符小写hex。Dimensions按Name唯一，Value≥0、Unit非空；不从图像文件名猜负载。Environment与Workload是宿主的实际只读封口引用，不是许可证检查。Profile不能包含自身hash；Plan.Profile绑定QLBP完整bytes，Workload必须与Plan.Input描述同一冻结负载。LatencyTarget.Stage只允许Prepare、Queue、Service、ProbeElapsed、ProbeReleased、EndToEnd、CancelToRelease，MinimumSamples∈[1,1,000,000]；非null时限>0且已提供的P50≤P95≤P99，任一目标非null必须有TargetSource，全部null允许且NotEvaluated。ResourceMetricBudget任一限值非null时也必须有TargetSource，不能拿工程MaxResidentBytes冒充客户资源目标。Failures的Max*判断使用Warmup+Measured完整计划所有失败/取消/超时/未执行计数，报告Measured摘要与Warmup原行分别保留，不能用预热阶段隐藏失败；Failures=null不补“零失败”默认；非null各容许计数≥0且有来源，完整计划分母不缩小。

Sampling.Period∈[10ms,60s]、ReadBudget>0且≤Limits.TotalBudget、Metrics≤32，键(Metric,Scope,TargetId)唯一；MaximumSamples∈[1,1,000,000]按**单metric行**计。Scope=Process/Operation；Acquisition=Polled/InstrumentedHighWater；Attribution=Attributed/Shared/Unknown。内置BCL适配仅声明Process/Polled：managed-live-bytes(byte，GC.GetTotalMemory(false))、working-set-bytes(byte，Refresh后的WorkingSet64)、private-bytes(byte，Refresh后的PrivateMemorySize64)、handle-count(count，Windows Process.HandleCount)。BCL适配默认Attribution=Shared，只有Environment明确提供专属隔离过程保证且实际目标匹配才可Attributed；请求Attributed而无法证明则降为Shared并NotEvaluated。全部为过程采样，不叫native/GPU分配峰值或泄漏证明；Operation/HighWater须由实际instrumented端口明确声明，否则返回Value=null+Reason=metric-unsupported。数值必须finite且非负，Attribution=Shared/Unknown不能授Operation达标。Budgets按(Metric,Scope,Unit)唯一；同metric多个TargetId时逐Target判断，不平均，缺匹配指标NotEvaluated。每一Max/Window/Slope的单位按A.3.2；Slope为Unit/s。取样阶段/时刻必须来自真实原调用，timer合并/延误不补造理想时间点。

Limits各TimeSpan>0且≤24h，CleanupBudget还取Root.CleanupBudget较小值；Prepare/Invoke≤Total。MaxAssetBytes∈[1,16MiB]、MaxDetailRows∈[1,1,000,000]，MaxResidentBytes>0且不超过请求/Root剩余额度。读取、解析、数组/排序/记录/报告及端口最坏保留量**合计**预留；不能只核文件大小。DecodeLimits的工程上限固定(MaxBytes=min(Profile或Recorded资产上限,Root剩余),MaxStringBytes=4096,MaxCollectionItems=1,000,000)，调用方可缩小不能放大。第一份Profile未解析前以min(请求MaxResidentBytes/4,1MiB)为读取字节额度，解析分配另在已预约剩余字节内checked预留（额度<8-byte header则先拒绝）；Profile解析后Recorded预算取Limits.MaxAssetBytes与剩余额度较小值。拒绝超长域、checked乘积溢出、尾随字节、非法enum/重复键，原字节仍由Root持有到真实返回/释放。

Plan.Deadline与Request.Resources.Deadline/Deadlines.OperationDeadline同时提供时相同；本分支有效总期限=min(这些非null期限,Profile.Limits.TotalBudget)，所以null不形成无限benchmark。所有原调用的prepare/invoke/sample等待还取剩余总期限，清理独立取一次cleanup总截止。MaxDetailRows≥WarmupIterations+MeasuredIterations且也覆盖Sessions数；不允许截断失败明细或录制行后仍Complete。预估MaximumSamples必须覆盖每metric的5个阶段采样+ceil(TotalBudget/Period)次测量轮询；全量bytes和Task/Lease上界按Parallelism×ProbeCapabilities.MaxSession*及ResourceSamplerCapabilities.MaxSession*（都必须正数、Tasks至少覆盖原准备/调用/释放任务）另加本Core协调/资产/取样/报告/cleanup/query槽计入Root预约。不足先拒绝，不开线程后才找容量。Warmup∈[0,1,000,000]、Measured∈[1,1,000,000]、Parallelism∈[1,64]且≤能力。

**解析、身份与录制闭包。** 必须注入BenchmarkAssets；读Profile原Task由Root.StartOwned在调用前预约并强持，await→核Source的全部ArtifactRef字段/Bytes长度/SHA→公开DecodeBenchmarkProfile→Encode重建byte相等→关联验证，不从JSON或ambient配置补字段。reader的ReadAsync ValueTask必须在StartOwned delegate内转原AsTask持有且只消费一次；其余Prepare/Sample同样，不丢原ValueTask或重复AsTask。Clock.WaitUntil原Task也先预约；上述ports不能外部先启动未知工作再RegisterTask。ExecuteProbe要求RecordedRun=null、Probe/Clock必需、Capabilities.Probe/Build与Plan全引用相同；AnalyzeRecordedRun要求RecordedRun非null，仅同reader读取QLBR并解析，Probe/Sampler/Clock可null且**零次**Prepare/Invoke/Sample/Clock.GetTimestamp，不能称本次运行算法。Run.WorkPlanSha256核A.5的QLBW；Profile/Probe/Build/Input/Environment完整引用与当前计划逐字段相同；录制行的Arrival/CacheMode/Parallelism也核固定计划，RecordedSchedule.ReadyTick=MeasuredStart+按clock频率向上取整的Offset，不能重新排时间让旧结果匹配新计划。ClosedLoop须每lane前一Release≤下一Ready。OriginCalculationId/OriginRequestSha256是原执行来源，保留而不要求等于这次AnalyzeRecordedRun的不同计算身份。Origin=SoftwareFixture只能SoftwareReplay/Synthetic证据，不升级为实测；Executed也不凭hash证明机台资格/真实性。

QLBR的Attempts恰含全部Warmup与Measured索引；各范围index从0起，Warmup与Measured分别唯一，InvocationId固定OperationId+"/warmup/"或"/measure/"+iteration，不能重跑换原index。NotExecuted各时间可null但ReadyTick记录其应到达/计划时刻；其它行须StartTick≤ActualCompletionTick≤ResourcesReleasedTick，且ReadyTick≤EnqueuedTick≤StartTick；失败/取消已实际运行行仍记录实际完成/资源归还，否则这些字段null、Complete=false。NotExecuted的WorkerId可为空、Lane固定−1、EnqueuedTick=ReadyTick仅为计划占位（不计队列时长），不要求存在session；不得把其Start/Complete/Release填0。Sessions含每个已准备session的LeaseId/worker/lane/mode/PrepareStart/Prepared/Released，LeaseId唯一，WarmReuse一个worker对应一个session；Warmup/Measured的lane必须0≤lane<Parallelism（NotExecuted用−1），WarmReuse同lane只一session，已实际派发的Attempts.WorkerId必须存在且lane/阶段在其准备和释放期间；准备未完成只记诊断及原Task、不伪造session。PreparedTick=WarmReuse初始session集合的最大Prepared、FreshWorker首session的Prepared（之后各worker准备只记录Sessions），MeasuredStart不早于预热全结束，MeasuredEnd不早于已在窗口完成的行；ProbeReleasedTick不早于全部session.Release。Samples必须在Accepted≤Tick≤源ResourcesReleased范围（最后点缺失则只诊断），Sample.Attribution与Metrics声明一致或从Attributed降Shared/Unknown，禁止升级；Sample按Phase核BeforePrepare≤首session.PrepareStart、AfterPrepare≥首准备完成且≤MeasuredStart、AfterWarmup≤MeasuredStart、Measured∈[MeasuredStart,MeasuredEnd]、AfterProbeRelease≥ProbeReleased。全记录tick以一个DomainId/Frequency>0/Source声明；负差、跨域、溢出、伪造阶段顺序拒绝，nullable不补0。Complete表示源生命周期/计划读取已封口，不等于每行Succeeded；NotExecuted可有但未开始不伪造运行时刻。Complete=true必须尝试全集、DroppedSamples=0、全部已派发行资源归还、最终ResourcesReleasedTick非null且不早于ProbeReleasedTick/所有session释放/所有行/样本；Incomplete只能局部报告，Criteria=NotEvaluated。Read成功、Task Faulted或某Disposed字段不能单独证明Complete。

**执行次序与真正完成。**

1. 接纳身份→解析Profile→核能力/副作用=false/字节及所有槽→固定全体iteration/lane/schedule→借用Clock；Clock.DomainId/Source非空，Frequency>0，运行期间不变。实际适配用Stopwatch.GetTimestamp/Frequency；测量ticks保留Int64，转换(TimeSpan/秒)用checked商余分解，不先把绝对巨大tick转double相减。WaitUntilAsync用同单调clock与业务token有限等待；超过目标/总截止则停止派发，不忙等或重新延长deadline。TimeSpan到clock tick用checked向上取整（不足1tick至少1tick），相减先核同域与非负/Int64溢出；Frequency极大导致换算不可表示时拒绝，不能wrap。测试clock只供软件fixture。
2. 有Metrics时先Sampler.Prepare→Root登记返回lease及全部原Task→BeforePrepare baseline→Probe.Prepare每lane→核Build/Input/Clock/Worker.Mode/Environment并登记其lease→AfterPrepare采样（仅初始准备集合一轮，FreshWorker后续准备归Sessions；周期仍覆盖实际Measured）。Prepare原Task返回之前只能拥有“正在准备”的原Task，不能Invoke；返回后关闭已开始也必须登记晚到lease并释放。Metrics空则Sampler不需要、不调用。Prepare失败/预算耗尽对未派发iteration记NotExecuted，清理已取得session；不从部分准备重试。
3. CacheMode=WarmReuse时每lane一个专属session，probe不能在不同lane并用同句柄。Warmup全局索引round-robin分lane，全部真实结束并归还每次借用后记录AfterWarmup→进入Measured；预热失败依FailurePolicy停止或仅在该session已恢复证明后继续。CacheMode=FreshWorker时WarmupIterations必须0，SupportsFreshWorker=true，**每次调用前独立Prepare新worker且真实Dispose后不再复用**；WorkerId不能在两次iteration复用，启动/加载独立Prepare指标与整链并计。Parallelism可支持多个独立worker，不自动清客户cache、GC或重启客户应用。
4. ClosedLoop的Arrivals必须空；空闲lane才派发下一个固定index，前一次Invoke原Task真实完成且ResourcesReleasedTick已证明iteration借用归还才再用lane。RecordedSchedule必须恰有Measured个ArrivalSlot、iteration唯一、Offset≥0且≤TotalBudget、按Offset再Iteration升序；到达基准为MeasuredStartTick。到达点无空lane就NotExecuted/concurrency-full，**没有无界队列/隐式延迟重排**；选择最低可用lane。scheduler延误另记实际EnqueuedTick，不冒充准时硬触发。MeasuredEnd在全索引已处理且所有已派发iteration真实归还时记录；总deadline或cancel先到则立即封口观察窗，仍在途列InFlight，迟到完成保持原ActualCompletion但不回改窗和吞吐。RecordedSchedule所有计划点也必须已到达/明确NotExecuted后封口，不能在无工作时提前结束丢掉未来到达；截止后尚未到达的固定index同样NotExecuted/deadline。ClosedLoop不据其结果承诺外部突发容量。
5. Invoke返回的原Task是实际计算/子工作及该iteration借用资源归还屏障，不能只代表提交GPU/native。provider在请求同Clock域记录实际Start/Completion/Release（跨进程backend需返回已校准或由host观测的同域屏障点；无法做到拒绝，不相减不同进程私有clock）。运行失败仍尽可能返回ProbeRun真实终态；抛错时原任务Faulted只保留错误，不证明native退出，Root随后Drain。InvokeBudget/总期限耗尽只停止等待/要求取消，lane和worker仍占用直到原释放屏障，不启动替代调用。所有Task/lateLease沿A.3.2当前Owner，外层Close不等待UI/自己。
6. 取样只有一条Root持有的协调循环，Sample原Task串行；每次实际batch逐metric恰一行，缺指标Value=null+reason，不以0补。第一轮到达点为MeasuredStart+Period，随后依固定序号到达点（不累计Sample耗时漂移）等待，再Sample；Sample等待=min(ReadBudget,剩余业务/cleanup期限)，超时仅停止等待，原Task继续Root持有且不启动并发Sample。忙于一次读取导致tick合并则记录实际轮数及DroppedSamples，不能补虚假样本。每固定到达轮次在准备新的Sample时用当前clock核错过的序号，未执行轮次×Metrics.Count加DroppedSamples；尚在途的一次Sample不重复计，返回缺metric的batch以null行保留而不算另一个timer漏测。预算到达停止采样、记录漏测而不截掉计数。取消后停止周期，但AfterProbeRelease最终采样用独立cleanup剩余token；取样循环自身有Root登记的linked CTS，MeasuredEnd到达即取消该循环等待、await其原Task退出，再发AfterProbeRelease最终样；不会等到整个30s总截止才停周期。其原Task也在Root持有，过期未返回为cleanup未知。
7. 停新派发→请求业务取消（若需要）→对所有ProbeReady启动一次DrainAsync（waitBudget=cleanup剩余）→Root登记返回Completion原释放Work→Dispose每lease**一次**且等真实归还→材料化有限报告草稿→AfterProbeRelease末样（在probe已释放之后，Sampler自身尚未关）→Sampler.Drain→其Completion+lease.Dispose真实结束→核所有资源退出→最终报告。每lease以原LeaseId由同一原子cleanup协调门启动Drain/Completion/Dispose一次；Root.Close与BenchmarkAsync并发清理都加入原协调Task，不能各起一份cleanup或延长首次总截止。cleanup剩余≤0不发新Sample/Prepare/Invoke，Drain可用0等待取得原Completion但不能补一份新budget；原Dispose一经开始仍由Root持有、Host不无限await。Dispose/Drain不递归Root.Close；端口实例属宿主且不被Core Dispose。Drain=false/异常/超时保留原Completion/lease，Root=Draining/DrainUnknown、Criteria=NotEvaluated，业务/cleanup两轴不互相覆盖。无Metrics仍须Probe真实释放。Execute派发前固定RunId=CalculationId+"/benchmark"，每lane SessionId=CalculationId+"/lane/"+lane（FreshWorker再加"/iteration/"+index），每个InvocationId按既定索引固定。Execute在终态前产生BenchmarkRecordedRun SourceRun（所有已取asset、Sessions、Attempt与Sample原字段），最终tick仅指该次benchmark计算/port借用归还，报告不可变值在Root保留；报告投影/Host Close对Service本体的释放不反向纳入SourceRun自身工作屏障，外层Root/QualificationOutcome.Resources另记。SourceRun能由公开EncodeBenchmarkRecordedRun导出、由宿主存证而不写Core私有store；哈希不含自身或其报告hash，避免循环。Recorded输入没有probe租约，仅asset读取/本Core资源排空；报告分别展示**源记录ResourcesReleased**与本次Root排空，不混成一个成功。

**归约与判定。** Attempt全分母：Measured Planned=S/F/C/T/NotExecuted守恒，Warmup另列；ActualCompletion不全或资源未知不标完整性能。Queue=Start−Enqueued，Service=ActualCompletion−Start，ProbeElapsed=ActualCompletion−Ready，ProbeReleased=ResourcesReleased−Ready；Prepare按Sessions每个session的Prepared−PrepareStart，EndToEnd=源Accepted→源ResourcesReleased（一次完整Run一个样本），CancelToRelease=源ResourcesReleased−CancelRequestedTick，仅源CancelRequestedTick非null且位于Accepted与ResourcesReleased之间才给值，不从Deadline推造。所有p分位唯一按DEV-GOV-010 §3.1，只归约完整已排空duration，成功子集另描述但不代全计划判断；返回Prepare/Queue/Service/ProbeElapsed/ProbeReleased/EndToEnd/CancelToRelease七个固定Stage条目，按Stage UTF8序；无样本则Samples=0、三个分位null和原因，不省略条目。Stage样本不足MinimumSamples、不支持目标阶段或缺目标NotEvaluated。完整排空失败样本也保留并进入对应Stage统计；未开始/删失不能当0毫秒。SourceRun.Complete与Sampling.RequireCompleteSampling分开：采样不全可以封存原记录但Complete=false并保留DroppedSamples；不以profile开关把丢样归0。BenchmarkThroughput.Window是MeasuredStart→MeasuredEnd且须>0，Completed/Succeeded仅计该窗口内ActualCompletion实际出现的Measured行，InFlight=窗口封口时已Start未Complete的行；速率=计数/Window秒且finite，窗口缺失/零长时两个速率null，不补零。分成功/全部实际完成数，剩余在途另列，不把准备/排空整体时长叫纯服务吞吐。

资源按每(Metric,Scope,TargetId,Unit)归约：baseline取BeforePrepare第一可用值；SampledPeak=max所有阶段可用采样，只有InstrumentedHighWater且实测端口声明完整覆盖才可叫真实高水位；RetainedDelta=AfterProbeRelease末值−baseline（可为负）；Window从MeasuredStart起，完整覆盖指定Budgets.Window才给Slope=(窗口内末值−首值)/真实间隔秒，至少两点且间隔>0。这是明确冻结的**端点斜率**，不叫回归泄漏预测。null/污染/共享归因/漏测（RequireCompleteSampling=true）/未完整Window时对应项NotEvaluated；它们不变成达标0值。任一明确有限目标超限→DoesNotMeetDeclaredCriteria；至少一项Latency/Resource显式目标存在、必需目标全有值并在范围、失败预算也有来源且满足、资源全部退出及输入/采样完整才MeetsDeclaredCriteria；任何必要条件未知→NotEvaluated，不能从已有目标均未失败补总体合格。一次Run只有1个EndToEnd样本，P95等可以描述但MinimumSamples限制照常；跨Run统计由宿主冻结多Run证据后消费同口径，不默默把iteration当模块Run独立样本。

#### A.3.3.1 新Benchmark两Host及固定软件夹具

Fixture只在唯一Core.Tests的HostExamples命名空间，有消费者与断言，不进入产品Core。两个独立Exe为ExecuteBenchMain与RecordedBenchMain（各编译入口名Main）；沿§12显式RecoveryOwner/Root/预约/单return-after-finally/业务cleanup两轴与有限恢复。Profile、Recorded资产均为真实不同内容bytes，reader按全ArtifactRef取，缺引用抛QLF-INPUT-INCOMPLETE，不把共享opaque hash当各内容。软件夹具端口仅实现本节公开签名；没有真实设备副作用，不能声称测得客户性能。

```csharp
public sealed class TestBenchmarkClock : IBenchmarkClock {
    public TestBenchmarkClock(string domainId,long frequency,long initialTick);
    public BenchmarkClockIdentity Identity { get; }
    public long GetTimestamp();
    public Task WaitUntilAsync(long timestamp,CancellationToken token);
}
public sealed class TestBenchmarkAssetReader : IBenchmarkAssetReader {
    public TestBenchmarkAssetReader(IReadOnlyList<BenchmarkAsset> assets);
    public ValueTask<BenchmarkAsset> ReadAsync(ArtifactRef source,int maxBytes,CancellationToken token);
}
public sealed class TestBenchmarkProbe : IBenchmarkProbe {
    public TestBenchmarkProbe(TestBenchmarkClock clock,ArtifactRef probe,ArtifactRef build,bool lateCompletion);
    public ProbeCapabilities Capabilities { get; }
    public void ReleaseLateCompletion();
    public ValueTask<ProbeReady> PrepareAsync(ProbePrepareRequest request,CancellationToken token);
    public Task<ProbeRun> InvokeAsync(ProbeReady ready,ProbeInvocation request,CancellationToken token);
    public Task<ProbeDrain> DrainAsync(ProbeReady ready,TimeSpan waitBudget,CancellationToken waitToken);
}
public sealed class TestBenchmarkLease : IQualificationLease {
    public TestBenchmarkLease(string leaseId,long retainedBytes);
    public string LeaseId { get; }
    public long RetainedBytes { get; }
    public ValueTask DisposeAsync();
}
public sealed class TestResourceSampler : IResourceSampler {
    public TestResourceSampler(TestBenchmarkClock clock);
    public ResourceSamplerCapabilities Capabilities { get; }
    public ValueTask<SamplerReady> PrepareAsync(SamplerPrepareRequest request,CancellationToken token);
    public ValueTask<ResourceSampleBatch> SampleAsync(SamplerReady ready,BenchmarkSamplePhase phase,
        CancellationToken token);
    public Task<SamplerDrain> DrainAsync(SamplerReady ready,TimeSpan waitBudget,CancellationToken waitToken);
}
```

TestBenchmarkClock Frequency=1000、DomainId=fixture-bench、构造初值0；它包裹实例Stopwatch起点，GetTimestamp为initialTick+floor(真实elapsed秒×Frequency)，用商余checked换算，不自行快进时间。WaitUntil通过同clock的有限Task.Delay重复观测到目标、过点立即完成，cancel只结束本等待，目标最多TotalBudget内；这是纯软件测试clock，不能授予目标平台精度。TestBenchmarkProbe能力=(构造传入的完整Probe引用，指定build，MaxParallelism=1，SessionBytes=4096，Tasks=8，Leases=1，SupportsCancellation=true，SupportsFreshWorker=false，SideEffects=false)。Prepare由原Task等待Task.Delay(2ms,token)后采真实clock，返回唯一worker/lease；Invoke在给定Ready/Enqueued之后等待Task.Delay(1ms,token)采Start、再Task.Delay(10ms,token)采ActualCompletion和同tickRelease，OutputSha256为UTF8 result=ok的hash，Outcome=Succeeded。lateCompletion=true仅QBEN-05闩锁场景（公开ReleaseLateCompletion解同实例原闩锁，重复调用幂等、不启动新工作）：原Task继续由Root持有直到显式有界闩锁释放（测试harness于≤5s截止内必须释放），不提前返回Completed；超时不能在同lane再Invoke。TestBenchmarkLease仅BCL托管测试资源，leaseId来自原SessionId+"/probe"或OperationId+"/sampler"、bytes=4096，Dispose以实例原子状态只归还一次并返回原有限释放任务，重复调用不重复计数；它不持有真实设备/native资源。PrepareReady.WorkerId=原SessionId+"/worker"、Mode=Plan.CacheMode、Environment=Profile.Environment，Clock=构造clock.Identity（Source=fixture），Build/Input=原Plan；SamplerReady同clock与原Sampling.Metrics，不猜单位或clock。Sampler能力=(test-sampler,SessionBytes=4096,Tasks=8,Leases=1,上述Metrics)，一lease、无后台线程，每阶段唯一行managed-live-bytes/Process/host/byte，Value固定100，Attributed；fixture explicit回执不冒充真实GC；Drain与Dispose分别计一次，重复调用返回原回执。reader≤4个asset、完整有界复制、同ref不同bytes拒绝；clock/probe/sampler计数为实例字段，非静态。

正常QLBR手算fixture不用TestProbe生成器：Origin=SoftwareFixture，Clock fixture-bench/1000/fixture，Accepted=0，Prepared=2，MeasuredStart=10，MeasuredEnd=70，ProbeReleased=75，ResourcesReleased=80；三测量行Ready/Enqueued/Start/Complete/Release分别(10,10,12,22,25)、(30,30,33,48,50)、(60,60,61,69,70)，Outcome均Succeeded，lane0、workerW01，无Warmup，P/Build/Input/Profile引用各按真实bytes。采样分别BeforePrepare@0、AfterPrepare@2、AfterWarmup@10、Measured@20/30/40/50/60/70、AfterProbeRelease@75，Value全100、Dropped=0、Complete=true。因此Queue=[2,3,1]ms、Service=[10,15,8]ms、ProbeElapsed=[12,18,9]ms、ProbeReleased=[15,20,10]ms，Source EndToEnd=80ms、资源peak=100byte/delta=0；客户目标全null→NotEvaluated。固定第三方录制输入展示不同形状，不把与执行fixture的不同tick声明成差异失败。

下面的构造及Host完整复用本页公开类型；CreateStudyRequest/CreateReplayRequest只用于取得既有公开工程预算/方法/空计划，构造新的Benchmark请求不会改原Study/Replay或其hash。

```csharp
static (QualificationRequest Request,BenchmarkAsset[] Assets) CreateBenchmarkRequest(bool recorded)
{
    static ArtifactRef Ref(string ns,string id,string text) =>
        QualificationCodec.ArtifactFromBytes(ns,id,"1",System.Text.Encoding.UTF8.GetBytes(text));
    var empty=CreateReplayRequest();
    var environment=Ref("env","test","software-fixture;no-devices");
    var workload=Ref("load","test","fixed-three-calls");
    var probe=Ref("probe","test","test-probe-v1");
    var build=Ref("build","test","fixture-bench-v1");
    var metrics=new[] {new ResourceMetricSpec("managed-live-bytes","Process","host","byte","Polled","Attributed")};
    var profile=new BenchmarkProfile("BP01","1",environment,workload,
        new[] {new WorkloadDimension("calls","count",3)},Array.Empty<ArrivalSlot>(),
        new[] {new LatencyTarget("Service",1,null,null,null,null)},
        new BenchmarkSampling(TimeSpan.FromMilliseconds(10),TimeSpan.FromSeconds(1),metrics,5000,true),
        new BenchmarkLimits(TimeSpan.FromSeconds(1),TimeSpan.FromSeconds(1),TimeSpan.FromSeconds(30),
            TimeSpan.FromSeconds(2),8388608,1048576,10),null);
    var pb=QualificationCodec.EncodeBenchmarkProfile(profile);
    var pr=QualificationCodec.ArtifactFromBytes("bench-profile","BP01","1",pb);
    var plan=new BenchmarkPlan(probe,build,workload,0,3,1,TimeSpan.FromSeconds(30),
        "ClosedLoop","WarmReuse","StopOnFailure",Array.Empty<ResourceMetricBudget>(),
        recorded ? BenchmarkExecutionMode.AnalyzeRecordedRun : BenchmarkExecutionMode.ExecuteProbe,pr);
    var assets=new List<BenchmarkAsset> {new(pr,pb)};
    var sourceRequest=empty with {CalculationId=new CalculationId("BEN-ORIGIN"),
        ExperimentId=new ExperimentId("BENCH-01"),
        Analysis=new BenchmarkAnalysis(plan with {ExecutionMode=BenchmarkExecutionMode.ExecuteProbe}),
        Resources=empty.Resources with {MaxResidentBytes=8388608},
        Method=new MethodRef("Benchmark.v1","1.0",Ref("method","benchmark","benchmark-v1"),
            empty.Method.NumericPolicy,build),Evidence=EvidenceLevel.SoftwareReplay};
    if (recorded) {
        string output=Ref("out","ok","result=ok").Sha256;
        long[] ready={10,30,60},start={12,33,61},done={22,48,69},release={25,50,70};
        var rows=new List<ProbeRun>();
        for (int i=0;i<3;i++) rows.Add(new ProbeRun("BEN-ORIGIN/measure/"+i,i,false,0,"W01",
            ProbeOutcome.Succeeded,ready[i],ready[i],start[i],done[i],release[i],output,null));
        var samples=new List<ResourceSample>();
        long[] ticks={0,2,10,20,30,40,50,60,70,75};
        BenchmarkSamplePhase[] phases={BenchmarkSamplePhase.BeforePrepare,BenchmarkSamplePhase.AfterPrepare,
            BenchmarkSamplePhase.AfterWarmup,BenchmarkSamplePhase.Measured,BenchmarkSamplePhase.Measured,
            BenchmarkSamplePhase.Measured,BenchmarkSamplePhase.Measured,BenchmarkSamplePhase.Measured,
            BenchmarkSamplePhase.Measured,BenchmarkSamplePhase.AfterProbeRelease};
        for (int i=0;i<ticks.Length;i++) samples.Add(new ResourceSample(ticks[i],phases[i],
            "managed-live-bytes","byte","Process","host",100,"Attributed",null));
        var record=new BenchmarkRecordedRun("BR01",new CalculationId("BEN-ORIGIN"),
            QualificationCodec.ArtifactFromBytes("origin","request","1",
                QualificationCodec.EncodeRequest(sourceRequest)).Sha256,RecordedOrigin.SoftwareFixture,
            QualificationCodec.ArtifactFromBytes("work-plan","test","1",
                QualificationCodec.EncodeBenchmarkWorkPlan(plan)).Sha256,pr,probe,build,workload,environment,
            new BenchmarkClockIdentity("fixture-bench",1000,"fixture"),0,2,10,70,75,80,true,0,null,
            new[] {new ProbeSessionRecord("L01","W01",0,"WarmReuse",0,2,75)},rows,samples);
        var rb=QualificationCodec.EncodeBenchmarkRecordedRun(record);
        var rr=QualificationCodec.ArtifactFromBytes("bench-record","BR01","1",rb);
        assets.Add(new BenchmarkAsset(rr,rb));plan=plan with {RecordedRun=rr};
    }
    var request=sourceRequest with {CalculationId=new CalculationId(recorded ? "BR-ANALYZE" : "BX-EXECUTE"),
        Analysis=new BenchmarkAnalysis(plan)};
    return (request,assets.ToArray());
}
static async Task<int> RunBenchmarkHostAsync(QualificationRecoveryOwner owner,bool recorded)
{
    string rootId=recorded ? "root-bench-recorded" : "root-bench-execute";
    QualificationRoot? root=null;QualificationOutcome? business=null;RootCloseResult? cleanup=null;
    string? businessError=null,cleanupError=null;int businessCode=5,cleanupCode=0;
    try {
        root=owner.CreateRoot(rootId,new RootLimits(16777216,1,4,64,16,TimeSpan.FromSeconds(2)));
        var reservation=root.Reserve(rootId,16777216,1,64,16);
        var fixture=CreateBenchmarkRequest(recorded);root.RetainInput(reservation,fixture.Request);
        var plan=((BenchmarkAnalysis)fixture.Request.Analysis).Plan;
        var clock=new TestBenchmarkClock("fixture-bench",1000,0);
        var ports=new QualificationFactoryPorts(
            new TestNumericsPort(TestNumericVector.BiasQ01,TimeSpan.Zero,false),
            new TestLedgerPort("ConfirmedAccepted"),null,null,null,
            recorded ? null : new TestBenchmarkProbe(clock,plan.Probe,plan.Build,false),
            recorded ? null : new TestResourceSampler(clock),null,null,null,
            new TestBenchmarkAssetReader(fixture.Assets),recorded ? null : clock);
        var service=QualificationFactory.Create(root,reservation,ports);
        var validation=service.ValidateDesign(fixture.Request);
        if (!validation.CanAnalyze) {businessCode=2;businessError="design-rejected";}
        else {
            var cancel=new CancellationTokenSource();root.RegisterCancellation(reservation,cancel);
            Task<QualificationOutcome> original=root.StartOwned(reservation,"benchmark",() =>
                service.BenchmarkAsync(new BenchmarkRequest(fixture.Request,plan),cancel.Token));
            business=await original.WaitAsync(TimeSpan.FromSeconds(30));
            businessCode=TerminalExitCode(business.Terminal);
        }
    } catch (TimeoutException) {businessCode=7;businessError="benchmark-host-wait-timeout";}
      catch (OperationCanceledException) {businessCode=4;businessError="benchmark-host-cancelled";}
      catch (Exception e) {businessCode=5;businessError=e.GetType().Name;}
    finally {
        if (root is not null) {
            try {var original=root.CloseAsync(TimeSpan.FromSeconds(2),CancellationToken.None);
                 cleanup=await original.WaitAsync(TimeSpan.FromSeconds(2));if (!cleanup.Drained) cleanupCode=6;}
            catch (Exception e) {cleanupCode=6;cleanupError=e.GetType().Name;}
            owner.RecordHostCompletion(rootId,new HostCompletion(recorded ? "BR-ANALYZE" : "BX-EXECUTE",
                business,businessError,cleanup,cleanupError,businessCode,cleanupCode));
        }
    }
    return cleanupCode!=0 ? cleanupCode : businessCode;
}
static async Task<int> ExecuteBenchMain(string[] args)
{
    var owner=new QualificationRecoveryOwner("bench-execute-process",1,64,16,16777216);
    int code=await RunBenchmarkHostAsync(owner,false);GC.KeepAlive(owner);return code;
}
static async Task<int> RecordedBenchMain(string[] args)
{
    var owner=new QualificationRecoveryOwner("bench-recorded-process",1,64,16,16777216);
    int code=await RunBenchmarkHostAsync(owner,true);GC.KeepAlive(owner);return code;
}
```

Root仍由Exe.Main强持到真实退出；Close未Drained返回6，软件外层隔离进程deadline=35s，不能声明杀进程等native安全停机。软件验证Host的result断言由同Core.Tests的QBEN-01/02调用链在得到business后、finally清理前核公开BenchmarkReport，任何不符抛异常转businessCode=5；这里RunBenchmarkHostAsync是公开装配示例，不将仅Completed的0当断言套件通过。保持长寿命进程时沿§12原Owner移交/ObserveRoot（有限1s），不返回裸int让Owner失根。ValidateDesign只做现成请求结构与必要端口能力核对；Profile/Recorded内容验证发生在已持有Root的BenchmarkAsync读入阶段，失败记录原CalculationId，不能从同步ValidateDesign偷做异步IO。

#### A.3.3.2 新范围正常、反例与可判定断言

| ID | 输入/事件 | 精确断言 |
|---|---|---|
| QBEN-01 | 上述Recorded Host | 零次Probe/Sampler/Clock调用；Planned=3、Succeeded=3，Queue P50/P95/P99=2/3/3ms、Service=10/15/15ms、ProbeElapsed=12/18/18ms、ProbeReleased=15/20/20ms、源EndToEnd=80ms；客户目标null→NotEvaluated，不冒充Execute |
| QBEN-02 | 上述Execute Host | sampler准备→baseline→probe准备→三次实际调用→probe真实Drain/lease释放→末样→samplerDrain/释放；全部原Task/lease有Root Owner，调用index不重跑；只编排软件fixture，结果完整但目标缺失仍NotEvaluated |
| QBEN-03 | QLBP/QLBR改一byte、错WorkPlan/Clock/Frequency或重复iteration、Recorded引用null | 读入接纳前/解析阶段拒绝对应字段和hash；不派发probe、不修输入、同ID异内容Conflict；QLBP与QLBR完整Encode/Decode byte-for-byte、尾随1byte拒绝 |
| QBEN-04 | RecordedSchedule offsets=0/1/2ms，单lane第一Invoke尚运行 | 后两项NotExecuted/concurrency-full，不排隐式队列；完整分母3；目标FailureTarget缺失总体NotEvaluated，原任务释放前零次复用lane |
| QBEN-05 | Invoke等闩锁，wait超时/Cancel，Close后晚到lease或Drain=false | business 7/4、cleanup 6两轴，原Task/CTS/lease当前Owner强持；未知ResourcesReleased不返槽；显式闩锁释放后原Completion可观察，不建替代worker |
| QBEN-06 | Sampler unsupported/null、Shared污染、漏tick、窗不满/单点 | 资源Unavailable/NotEvaluated，不填0/不标绝对峰值；周期真实样本无伪时刻；达MaximumSamples停止并保留DroppedSamples/完整分母 |
| QBEN-07 | FreshWorker缺能力/worker复用/存在预热、负阶段差或跨clock | 派发前拒绝或原回执port-contract错误，保留原工作并Drain；无清cache/强GC；同worker并发数不超lane容量 |
| QBEN-08 | 工程预算不足、客户目标全部空、目标来自正式软件fixture且显式超限 | 前者无prepare副作用；目标空可分析但NotEvaluated；后者Failures/Latency/Resources声明来源且完整时按Satisfies/Fails判断，软件目标不冒充客户值 |

### A.3.4 已批准Adapter的公开装配和技术证据边界

本节补可决定的软件装配，不增加检验算法、设备操作或用途批准。Core只依赖本页端口，原A.3.1/1.1数值映射、A.3.3性能及A.3.2 Root不重选。optional包的唯一落点都在src/Modules/qualification，验证在同名tests/Modules/qualification目录：Statistics桥用已定工程；Replay桥为Asun.Modules.Qualification.Replay（Core+Replay.Core）；Storage桥为Asun.Modules.Qualification.Storage（Core+IM-066 Contracts/Runtime）；Wpf见§2。每包可单独build/publish且引用固定精确合同版本；模块Core禁止引用这些optional包。Snapshot/Reference与BCL sampler/clock作为Core的无UI有限适配，无HALCON引用或隐藏窗口；HALCON的真实测量/探针由原metrology/算法Owner注入，无本模块第二metrology worker。

```csharp
// Declaration fragments in Asun.Modules.Qualification, not existing implementation.
public sealed record QualificationCodecLimits(int MaxBytes,int MaxStringBytes,int MaxItems,
    int MaxTotalItems,int MaxDepth);
public interface IQualificationArtifactLease : IQualificationLease {
    ArtifactRef Reference { get; }
    long Bytes { get; }
    ValueTask<System.IO.Stream> OpenReadAsync(CancellationToken token);
}
public interface IQualificationArtifactSource {
    ValueTask<IQualificationArtifactLease> OpenAsync(ArtifactRef reference,int maxBytes,CancellationToken token);
}
public sealed record NumericsBridgeProfile(string Name,DemingBridgeBudget Budget);
public interface IQualificationSynchronousNumerics : IQualificationNumerics {
    NumericResult Calculate(NumericRequest request,CancellationToken token);
}
public enum ReferenceCheck { Supported, Contradicted, Unknown }
public sealed record ReferenceUseEvidence(DateTimeOffset EvaluatedUtc,ArtifactRef ParsedCertificate,
    ArtifactRef UseRelation,ReferenceCheck Identity,ReferenceCheck Conditions,
    ReferenceCheck Time,ReferenceCheck Use,IReadOnlyList<QualificationDiagnostic> Diagnostics);
public sealed record QualificationReferenceDocument(ReferenceProjection Projection,ReferenceUseEvidence Use);
public interface IQualificationReferenceSource {
    ValueTask<QualificationReferenceDocument> ReadAsync(ReferenceAssignment assignment,CancellationToken token);
}
public sealed record GoldenOutputBinding(string CaseId,string ParentId,string ExpectedKey,string ActualKey,
    ArtifactRef Expected,string ExpectedRole,ArtifactRef? Actual,string ActualRole);
public sealed record QualificationReplayEvidence(ArtifactRef Report,ArtifactRef Input,ArtifactRef Environment,
    ArtifactRef Build,ArtifactRef Comparator,ReplayResult Result,IReadOnlyList<GoldenOutputBinding> Outputs);
public interface IQualificationSealedReplaySource {
    ValueTask<QualificationReplayEvidence> ReadAsync(GoldenPlan plan,CancellationToken token);
}
public static class QualificationAdapterFactory {
    public static IObservationSnapshotReader CreateSnapshotReader(QualificationRoot root,
        RootReservation reservation,ExperimentPlan plan,IQualificationArtifactSource source,
        QualificationCodecLimits limits);
    public static IReferenceProjectionReader CreateReferenceReader(QualificationRoot root,
        RootReservation reservation,IQualificationReferenceSource source);
    public static IReplayQualificationReader CreateReplayReader(QualificationRoot root,
        RootReservation reservation,IQualificationSealedReplaySource source);
    public static IBenchmarkClock CreateMonotonicClock(string domainId);
    public static IResourceSampler CreateProcessSampler(IBenchmarkClock clock,string processTargetId);
}
```

公开工厂先验证Root预约/限额→构造纯实例→登记本适配所获租约和原工作；constructor不Open/运行算法/启动timer。注册失败遵A.3.2先预留强持，原ValueTask在StartOwned内只AsTask一次；Stop/Dispose只管本实例，不Close根或Dispose共享source。同步Analyze必须注入IQualificationSynchronousNumerics；无该能力只拒绝同步入口，不能以async.Result伪装。Statistics optional包提供公开QualificationStatisticsBridge(root,reservation,Asun.Modules.Statistics.INumericalStatistics engine,NumericsBridgeProfile profile)，实现IQualificationSynchronousNumerics；NumericsBridgeProfile公开位置字段为(Name string, Budget DemingBridgeBudget)，Budget的13字段分别映NumericalBudget。N01沿A.3.1固定值；S7单family交给已有QualificationDemingStatisticsBridge，不混task。Methods/SupportDomain由原实际Capabilities声明，各请求先冻结有效较小Budget/hash，缺t/F端口仅所需区间Unsupported。方法选择与逐字段请求/返回/Completion/Dispose都只按A.3.1/1.1，不新增数值算法。

| Adapter | 逐步规则/身份/错误/恢复/输出 |
|---|---|
| SnapshotReader | Open指定QLIP精确ref：源Open→持原lease→读≤MaxBytes到EOF→全hash/length校验→严格decode QLIP header、Plan.Plan与完整Observation→同调用者plan核QLEP hash、Count/ID/序与bytes→SnapshotHeader实际长度/hash/revision。ReadPages只顺序读取冻结数组，pageSize1..10000，Offset从0连续，PageSha256=SHA256(QLMS header+该页完整Observations)；分页hash不是整个QLIP身份。Seal仅在到EOF/全Count一致时Complete=true；取消、截断、hash错不返回封口。Dispose等原读取Task/流关闭/lease.Dispose真实归还，Root持至确认；可重读是新adapter同精确ref，不随机寻latest。已有ReadComplete=false诊断不改为计划缺测 |
| ReferenceReader | source输出原Assignment逐字段相同，Projection.SourceSha256等ParsedCertificate.Sha256且ParsedCertificate是精确投影引用；Complete仅解析字段读全，不是用途Supported。EvaluatedUtc为原研究实际参考核对UTC，四项ReferenceCheck分别核实物身份/测量条件/证书声明时间范围/使用关系；Unknown或Contradicted让对应参考依赖NotEvaluated，不能用机器当前时间或hash猜有效。读证书/量值投影的领域解析/签发在原证书Owner，本模块无PDF/OCR猜值。ReferenceProjection原公开形状保持，完整Use随下述ReportArchive.Reference保留，不能把bool Complete冒物理溯源。source须返回结构化读回证据，adapter不修改Assigned/共同u/相关组 |
| SealedReplayReader | 单次source.Read全量QualificationReplayEvidence，Comparator与plan.Comparator全ref相等；Planned=plan.PlannedCases，CaseId/ParentId与manifest外连接，所有计划case保留，未知/缺行明确NotExecuted/Incomparable。Result.CasesSha256=SHA256(QLCS实际结果)，Outputs恰覆盖原case；ExpectedKey/ActualKey分别匹配case文本引用、ParentId对应原计划，ExpectedRole/ActualRole只Synthetic/GoldenBaseline/Measurement/HumanOpinion/CandidateOutput，不能都变Truth。Result.Executed等实际执行类别和，NotExecuted不增执行数。原Report/Input/Environment/Build及原输出refs完整进入archive；未封存/Comparator变更/额外case/同ID异source为PORT-CONTRACT，不重新运行或换expected。source可来自Replay optional桥，见后段；本接口是本模块新typed消费口，不假称上游已有同名reader |
| Clock/Sampler | Clock用实例Stopwatch.GetTimestamp/Frequency，DomainId明确、有限WaitUntil按A.3.3的同域商余/向上取整checked规则，无UTC换算/全局clock修改。ProcessSampler只A.3.3四指标、Process/Polled/Shared：每Sample先核clock/metric、Refresh Process再读，GC.GetTotalMemory(false)不强制GC；缺权限/指标返回null+原因，不填0。Prepare冻结Metric声明、原lease；Sample/Drain无后台隐藏线程，调用方已有采样循环；Dispose只关本实例Process对象，注入clock不Dispose。实际instrumented/GPU/high-water或设备测量不由本BCL adapter承诺 |
| 报告/EvidenceSink/ledger | IEvidenceSink.SealAsync(report)仍是旧完整报告QLRP保存口，不能仅凭EvidenceReceipt三个字段证明全原请求/外部依赖已耐久。需要训练治理或跨重启报告消费必须走A.5.4～6完整QLAR与精确引用/原提交查询；ledger原CalculationId/hash不变。Analysis、存储知识与技术释放三轴独立 |

Replay optional桥唯一公开QualificationReplayProjectionFactory.Create(Asun.Modules.Replay.ReplayResult result, IReadOnlyList<Asun.Modules.Replay.ReplayCaseResult> cases, IReadOnlyList<GoldenOutputBinding> bindings, ArtifactRef sourceReport, ArtifactRef input, ArtifactRef environment, ArtifactRef build, ArtifactRef comparator)返回QualificationReplayEvidence。输入是宿主已封存原报告与全case，不StartReplay；源Result.ProductionFactWrites=0、FinalState已封存/释放、SealedResultDigest/sourceReport hash关联由原Replay正式codec核真字节。CaseId/原TargetIdentity与bindings原目标关联证据核对，不能按行号zip。CompletedEqual→Consistent，CompletedChanged→Changed，CompletedIncomparable或Unknown→Incomparable（保原错误在源报告），Failed→ExecutionFailed，CancelledOrNotRun→NotExecuted；尚未封口为PORT-CONTRACT，Extra case拒绝。原Differences/Errors不缩成一致率：由sourceReport精确完整内容保留，archive link必含该原件及每Expected/Actual原输出。ContentRef转换只接受DigestAlgorithm=sha256，Namespace="replay:"+Schema、Id=AssetId、Revision/Digest原样、ByteLength入link；其它摘要不改标签。Acquire/Read由IReplayEvidenceReader.AcquireAsync→IReplayContentLease.OpenReadAsync原公开API借用，逐次Read/Dispose归Root；无上游封存codec或权限实际绑定时拒绝该读回，不猜私有文件格式。可用明确typed软件夹具验证桥，但不是真实Replay资格。

源Observation/Reference/Golden表中的环境、实物状态、重定位/操作者等扩展声明不假称A.1已有字段：公开PlanCell/Observation为唯一序列；其它物理事实在FactorsRef/AssumptionsRef/ConditionsRef/UseRelationRef/TargetRef指定的Owner证据及archive精确links，不能以表格概念偷偷新增未编码运行属性。同一因素含义/单位/来源不明则相关用途Limited/NotEvaluated；不阻不依赖它的纯描述。

### A.4 UI 公开装配、原意图查询与双 STA Host

namespace为 `Asun.Modules.Qualification.Wpf`；Control继承WPF UserControl，不能把非Visual普通class传给Window.Content。Core仍不引用WPF。下列是公开声明片段，唯一Assembly与测试落点在§2；本轮只完善指导，不创建工程。

```csharp
using Asun.Modules.Qualification;
public sealed record UiContext(string Locale,System.Globalization.CultureInfo InputCulture,
    string ThemeName,long MaxPreviewBytes);
public sealed record UiPermissions(bool Read,bool Edit,bool Analyze,bool CancelOwn,bool OpenEvidence,
    long Epoch,DateTimeOffset? ExpiresUtc);
public sealed record QualificationUiSession(string SessionId,long Revision,IQualificationService Service,
    QualificationRoot Root,RootReservation Reservation,QualificationRequest Request,QualificationReport? Report,
    UiContext Context,UiPermissions Permissions,IQualificationUiHost Host);
public abstract record UiIntent(string SessionId,long Revision,string IntentId,long PermissionEpoch);
public sealed record AnalyzeIntent(string SessionId,long Revision,string IntentId,long PermissionEpoch,
    QualificationRequest Request) : UiIntent(SessionId,Revision,IntentId,PermissionEpoch);
public sealed record CancelIntent(string SessionId,long Revision,string IntentId,long PermissionEpoch,
    CalculationId CalculationId) : UiIntent(SessionId,Revision,IntentId,PermissionEpoch);
public sealed record OpenEvidenceIntent(string SessionId,long Revision,string IntentId,long PermissionEpoch,
    ArtifactRef Evidence) : UiIntent(SessionId,Revision,IntentId,PermissionEpoch);
public sealed record ReturnReportIntent(string SessionId,long Revision,string IntentId,long PermissionEpoch,
    ArtifactRef Report) : UiIntent(SessionId,Revision,IntentId,PermissionEpoch);
public sealed record UiIntentQuery(string SessionId,long Revision,string IntentId);
public sealed record UiIntentReceipt(string SessionId,long Revision,string IntentId,
    UiReceiptState State,string Reason,CalculationId? CalculationId,string? RequestSha256);
public sealed record UiIntentSnapshot(UiIntentReceipt Receipt,Task<QualificationOutcome>? OriginalOperation,
    QualificationOutcome? Outcome);
public interface IQualificationUiHost {
    Task<UiIntentReceipt> HandleAsync(UiIntent intent,CancellationToken token);
    Task<UiIntentSnapshot> QueryIntentAsync(UiIntentQuery query,CancellationToken waitToken);
    void UpdatePermissions(string sessionId,UiPermissions permissions);
}
public sealed class QualificationUiHost : IQualificationUiHost {
    public QualificationUiHost(QualificationRoot root,RootReservation reservation,
        IQualificationService service,string sessionId,long revision,UiPermissions permissions,
        IQualificationEvidenceNavigator? navigator=null);
    public Task<UiIntentReceipt> HandleAsync(UiIntent intent,CancellationToken token);
    public Task<UiIntentSnapshot> QueryIntentAsync(UiIntentQuery query,CancellationToken waitToken);
    public void UpdatePermissions(string sessionId,UiPermissions permissions);
}
public interface IQualificationEvidenceNavigator {
    Task OpenAsync(ArtifactRef evidence,CancellationToken token);
    Task ReturnAsync(ArtifactRef report,CancellationToken token);
}
public sealed class QualificationControl : System.Windows.Controls.UserControl {
    public QualificationControl();
    public QualificationBinding Bind(QualificationUiSession session);
}
public sealed class QualificationBinding : IAsyncDisposable {
    public void UpdateRequest(QualificationRequest request,long revision);
    public void UpdateReport(QualificationReport report,long revision);
    public void SetContext(UiContext context);
    public void SetPermissions(UiPermissions permissions);
    public Task<UiUnbindReceipt> UnbindAsync(TimeSpan waitBudget,CancellationToken waitToken);
    public ValueTask DisposeAsync();
}
```

IntentId由调用方**发送之前**固定，Session/Revision/Epoch同查；同IntentId同内容返回原回执，异内容拒绝。HandleAsync只是接纳意图：Analyze按请求变体派发（Golden→EvaluateGoldenAsync，Benchmark→BenchmarkAsync，其他→AnalyzeAsync），其原Task由公开Host装配器在本Root的预约内StartOwned登记，再返回Accepted；Unknown不能造ArtifactRef、不能用ReturnReport当查询、不能发新Analyze。QueryIntentAsync按原三元身份返回Unknown/Rejected/原回执及原Operation引用，NotFound用Rejected+intent-not-found表示且不证明未执行。无navigator时Open/Return返回Rejected，不偷偷开文件/存证。CancelOwn由Host查原Session拥有的CalculationId及RequestSha256，调用Service.CancelCalculationAsync原身份，不Stop共享Service。超时/等待取消只结束等待，Host/Query/Operation均保留Root。

Binding.SetPermissions在同Dispatcher同时调用Host.UpdatePermissions，Epoch严格增加；旧Epoch/过期命令拒绝。SetContext只改局部资源（zh-CN/zh-TW/en-US），不改CultureInfo.CurrentCulture/请求hash。Unbind先关闭新命令、撤订阅、丢晚到投影，注册Binding原Dispose/预览租约；UnbindPending.Completion由Root持有。Root.Close接纳Unbind原Task，并把Unbind、Stop、Dispose放进**同一**总cleanup截止；关闭窗口不先无限await IDisposable。

两个STA Host的完整装配复用§12两个已经在正文构造的请求及TerminalExitCode helper；各Exe直接包含这些helper，不依赖另一Exe。StudyMain和ReplayMain各属于独立WPF Exe；当前不创建工程，不把下述调用例标成已编译。两Host只在同一个固定1920×1080屏幕中验证，window大小按工作区扣外框；不改显示设置。

```csharp
using System.Globalization;
using System.Windows;
using Asun.Modules.Qualification;
using Asun.Modules.Qualification.Wpf;

// Each executable contains exactly one of these Main methods.
[STAThread] static int StudyUiMain(string[] args)
{
    var owner=new QualificationRecoveryOwner("ui-study",2,64,32,16777216);
    int code=5;
    try {code=RunUiApplication(owner,CreateStudyRequest(),"ui-study-root","zh-CN");}
    catch (Exception e) {code=RecordStartupFailure(owner,"ui-study-root","B01",e);}
    GC.KeepAlive(owner);
    return code;
}
[STAThread] static int ReplayUiMain(string[] args)
{
    var owner=new QualificationRecoveryOwner("ui-replay",2,64,32,16777216);
    int code=5;
    try {code=RunUiApplication(owner,CreateReplayRequest(),"ui-replay-root","zh-TW");}
    catch (Exception e) {code=RecordStartupFailure(owner,"ui-replay-root","G01",e);}
    GC.KeepAlive(owner);
    return code;
}
static int RecordStartupFailure(QualificationRecoveryOwner owner,string rootId,string calculationId,Exception error)
{
    if (owner.QueryRoot(rootId) is null) return 5; // no root/resources were admitted
    RootCloseResult? cleanup=null;
    string? cleanupError=null;
    int cleanupCode=0;
    try {
        var original=owner.CloseRootAsync(rootId,TimeSpan.FromSeconds(2),CancellationToken.None);
        cleanup=original.WaitAsync(TimeSpan.FromSeconds(2)).GetAwaiter().GetResult();
        if (!cleanup.Drained) cleanupCode=6;
    } catch (Exception e) {cleanupCode=6;cleanupError=e.GetType().Name;}
    owner.RecordHostCompletion(rootId,new HostCompletion(calculationId,null,error.GetType().Name,
        cleanup,cleanupError,5,cleanupCode));
    return cleanupCode==0 ? 5 : cleanupCode;
}
static int RunUiApplication(QualificationRecoveryOwner owner,QualificationRequest request,
    string rootId,string locale)
{
    var app=new Application {ShutdownMode=ShutdownMode.OnExplicitShutdown};
    var root=owner.CreateRoot(rootId,new RootLimits(8388608,1,4,32,16,TimeSpan.FromSeconds(2)));
    var reservation=root.Reserve(rootId,8388608,1,32,16);
    root.RetainInput(reservation,request);
    var gp=(request.Analysis as GoldenAnalysis)?.Plan;
    var ports=new QualificationFactoryPorts(
        new TestNumericsPort(TestNumericVector.BiasQ01,TimeSpan.Zero,false),
        new TestLedgerPort("ConfirmedAccepted"),null,
        gp is null ? null : new TestReplayPort(gp.CaseManifest),null,null,null,null,null,null);
    var service=QualificationFactory.Create(root,reservation,ports);
    var permissions=new UiPermissions(true,false,true,true,false,1,
        new DateTimeOffset(2026,10,12,0,0,0,TimeSpan.Zero));
    var host=new QualificationUiHost(root,reservation,service,rootId,1,permissions,null);
    var context=new UiContext(locale,CultureInfo.InvariantCulture,"Default",262144);
    var session=new QualificationUiSession(rootId,1,service,root,reservation,request,null,
        context,permissions,host);
    var control=new QualificationControl();
    var binding=control.Bind(session);
    var window=new Window {Title=locale=="zh-TW" ? "資格分析" : "资格分析",
        Content=control,Width=1200,Height=800};
    Task? lifetime=null; // Root strongly retains this UI coordinator; it never gates Close
    bool closing=false;
    int businessCode=5,cleanupCode=0;
    QualificationOutcome? business=null;
    RootCloseResult? cleanup=null;
    string? businessError=null,cleanupError=null;
    window.Loaded += (_,_) => {
        if (lifetime is not null) return;
        lifetime=ExecuteWindowAsync();
        root.RegisterTask(reservation,"ui-command",lifetime,RootTaskRole.UiCoordinator);
    };
    async Task ExecuteWindowAsync()
    {
        try {
            binding.SetContext(context with {Locale="en-US"});
            window.Title="Qualification analysis";
            binding.SetPermissions(permissions with {Epoch=2});
            var intent=new AnalyzeIntent(rootId,1,"intent-01",2,request);
            Task<UiIntentReceipt> send=host.HandleAsync(intent,CancellationToken.None);
            root.RegisterTask(reservation,"ui-send",send);
            var receipt=await send.WaitAsync(TimeSpan.FromSeconds(1));
            var query=new UiIntentQuery(rootId,1,intent.IntentId);
            Task<UiIntentSnapshot> originalQuery=host.QueryIntentAsync(query,CancellationToken.None);
            root.RegisterTask(reservation,"ui-query",originalQuery,RootTaskRole.ControlWait);
            var snapshot=await originalQuery.WaitAsync(TimeSpan.FromSeconds(1));
            if (snapshot.OriginalOperation is { } original) {
                business=await original.WaitAsync(TimeSpan.FromSeconds(30));
                businessCode=TerminalExitCode(business.Terminal);
                if (business.Report is { } report) binding.UpdateReport(report,1);
            } else {
                businessCode=receipt.State==UiReceiptState.Unknown ? 7 : 2;
                businessError=snapshot.Receipt.Reason;
            }
        } catch (TimeoutException) {businessCode=7; businessError="ui-wait-timeout";}
          catch (OperationCanceledException) {businessCode=4; businessError="ui-wait-cancelled";}
          catch (Exception e) {businessCode=5; businessError=e.GetType().Name;}
    }
    window.Closing += async (_,e) => {
        if (closing) {e.Cancel=true; return;}
        e.Cancel=true;closing=true;
        try {
            Task<UiUnbindReceipt> unbind=binding.UnbindAsync(TimeSpan.Zero,CancellationToken.None);
            root.RegisterTask(reservation,"unbind",unbind); // Root registers binding preview/dispose internally
            Task<RootCloseResult> originalClose=root.CloseAsync(TimeSpan.FromSeconds(2),CancellationToken.None);
            cleanup=await originalClose.WaitAsync(TimeSpan.FromSeconds(2));
            if (!cleanup.Drained) cleanupCode=6;
        } catch (Exception ex) {cleanupCode=6;cleanupError=ex.GetType().Name;}
        owner.RecordHostCompletion(rootId,new HostCompletion(request.CalculationId.Value,business,
            businessError,cleanup,cleanupError,businessCode,cleanupCode));
        app.Shutdown(cleanupCode!=0 ? cleanupCode : businessCode);
    };
    // Finite verification host only; a product host uses its own operator/session lifetime.
    var watchdog=new System.Windows.Threading.DispatcherTimer {Interval=TimeSpan.FromSeconds(35)};
    watchdog.Tick += (_,_) => {watchdog.Stop(); if (!closing) window.Close();};
    watchdog.Start();
    int exit;
    try {exit=app.Run(window);}
    finally {watchdog.Stop();}
    GC.KeepAlive(owner); // owner lives until this process exits; a long-lived shell retains it as a field
    return exit;
}
```

Bind/构造之前发生异常也由最外Main catch记录business=5，并对已CreateRoot的rootId启动Close；Application启动失败不允许返回0。以上装配的窗口寿命任务不算Root排空所等的自有资源Task：Core/Host只等已登记的端口/operation/preview任务；UI事件协作任务由Root保留但不形成“Close等Closing，Closing又等Close”的环。Start/Close自身控制Task同样不进入其自身Completion依赖。

权限Epoch撤销、ExpiresUtc到期、Unknown查询再次未知、关窗后晚到、异实例事件、UnbindPending与目标RecoveryOwner容量满的断言分别保留。实际DevExpress高阶布局/Grid-Chart联动/属性高级设置/SuperTip与三语键盘规则沿§11及本机25.2官方XML证据，不进行新版本研究或依赖下载。真实双STA运行/UIA/DPI/现场资格尚未执行。

### A.5 Canonical 编码、完整 Request Golden 与公开 Codec

二进制身份与 JSON 显示投影分开；不假定 JCS 能定义此处的字节。以下是 v0.2 唯一编码，Core 用显式 typed writer/reader 实现，禁止反射遍历属性或按当前文化格式化 double。限额检查先于编码；未知类型/tag、长度溢出、重复键、尾随字节拒绝，不忽略后继续接纳。**MethodRef 固定两个 string + 三个 ArtifactRef：Parameters、NumericPolicy、BackendBuild。**

| 基本编码 | 唯一规则 |
|---|---|
| domain header | 4 ASCII bytes magic + LE UInt16 major=0 + LE UInt16 minor=2，共8字节 |
| string / ID wrapper | LE UInt32 UTF-8字节数 + 严格UTF-8（无BOM）。须已为Unicode NFC，无NUL/孤立surrogate；拒绝后修输入，不静默正规化。空字符串仅在语义允许字段合法 |
| int / long / bool / enum | int=LE Int32；long=LE Int64；bool=单byte 0/1；enum=单byte，EvidenceLevel/RepeatLevel取A.1声明位置0起；其他tag见下表 |
| double / TimeSpan / UTC | IEEE754 binary64 LE；有限值，-0写+0。TimeSpan写Int64 ticks；DateTimeOffset仅接受Offset=TimeSpan.Zero，非UTC偏移即使代表同一时刻也拒绝；写其UtcDateTime.Ticks（100ns，自0001-01-01） |
| nullable / list / blob / matrix | nullable先byte 0/1再value；list先UInt32 count再元素；blob先UInt32 bytes再完整域；matrix先UInt32 rows/columns再行优先double，保留对应Units次序 |
| 普通 record | 按A.1公开位置参数顺序递归写字段，无字段名或运行时类型名。ID wrapper只写Value。ArtifactRef的Sha256为64字符小写ASCII string，不能当32字节偷偷压缩 |
| 有键集合 | Cells按CellId、Observations按ObservationId、Assumptions按Name、组件按Id、Covariance按Group、Golden cases按CaseId、Linearity Assignments按ObservationId、Agreement pairs按Stratum再PairId；UTF-8字节序升序，键唯一。EvidenceRefs按Namespace/Id/Revision/Sha256排序且去重；数值轴/Levels/矩阵/预算列表保留声明次序 |
| Outcome union | Measured=1 + QuantityValue；Failed=2 + Reason/EvidenceRefs；NotCollected=3 + Reason；Excluded=4 + RuleId/Reason/Original（Original不能再Excluded） |
| 报告 map | Values限于A.3.1的具名输出键，按UTF-8键序编码；不允许任意对象参数或未知统计字段 |

各域的字段闭包：

- `QLEP`：header → Cells → FactorsRef → RandomizationRef → AssumptionsRef → ExpectedCount。排除ExperimentPlan.Plan自身，避免自引用hash；宿主以该完整内容建立Plan ArtifactRef。
- `QLIP`：header → Plan.Plan ArtifactRef → Observations。InputSnapshot.Count等于观测行数，ActualBytes等于QLIP字节长度，ContentSha256与Snapshot.Sha256均为QLIP hash。Golden请求观测Count=0合法，案例分母从GoldenPlan取得，不能伪称空Observation是1条。Reader必须按同一封口投影核原hash。
- `QLMS`：header → Members(UInt32 count+逐完整Observation)，保留请求声明顺序，不按ID重排；重复ObservationId拒绝。NumericRequest.InputOrderHash=SHA256(QLMS bytes)，只证明派生输入次序，不证明未读成员或原总体封口。
- `QLNI`：header → NumericRequest全部公开位置字段依次编码（OperationId、SourceSnapshot、MeasurandId、SelectionPolicy、SubsetApproval、ReadComplete、PopulationClosed、ExpectedRows、Members、MethodId、Analysis、Input、Method、NumericPolicyId、UnitSystem、InputOrderHash）。Members保留声明序且按完整Observation编码；Analysis使用QLRQ同tag/payload；NumericInput tag1=ScalarNumericInput的Values声明序，2=GroupedNumericInput的Cells按CellId和Observations声明序，3=CovarianceNumericInput的Components按Id/Covariances按Group/Coverage，4=AgreementNumericInput的SideA/SideB分别按声明序/LoaMultiplier/ErrorVarianceRatio；新增5=DemingNumericInput的Stratum/Plan/SourceErrorVarianceRatio/CenterX/ErrorVarianceRatio/Pairs（按PairId Ordinal）。标量Values按Members声明序中Measured成员依次对应，非Measured没有值且仍保留在Members/覆盖中；这不是另选总体。其他变换行须与对应Members一一映射，Grouped重复投影须逐字段等于Members，Agreement按Analysis.Pairs稳定身份联接而不靠左右位置配对。旧family此完整派生内容hash作为statistics InputReference.ContentHash；S7将该hash仅作为输入身份字段，再依S7自身完整INPUT域生成InputReference.ContentHash（A.3.1.1无环顺序）；上游MemberSequenceHash仍按其自身codec计算，二者用途不同。
- `QLCS`：header → CaseCount(UInt32) → CaseId/ParentId/ExpectedRef/StatusTag/ActualRef逐例。StatusTag=Consistent1/Changed2/Incomparable3/ExecutionFailed4/NotExecuted5；案例来源原件与计划中的CaseManifest必须同内容。
- `QLGP`：header → PlanId → Cases ArtifactRef → Comparator ArtifactRef → ParentGroupingRef → StrategyRef → SeedSetRef → PlannedCases(Int32) → CaseManifest（UInt32 count，然后逐例；不重复QLCS header）。PlanId现为公开GoldenPlan字段；CaseManifest是封口来源的投影，不允许模块覆盖expected或回写实际运行。
- `QLRQ`：header → ContractVersion → CalculationId → ExperimentId → MethodRef → Scope → **Input投影** → Evidence → Resources → Deadlines → Analysis(tag+下表payload) → Reference(nullable) → Assumptions(list) → Criteria(nullable) → ParentCalculation(nullable)。Input投影依次为Snapshot ArtifactRef、Count(Int64)、ActualBytes(Int64)、ContentSha256、Plan.Plan ArtifactRef；原行及完整Plan正文由上述hash绑定，不能再有未绑定字段。Resources与Deadlines逐公开字段进入hash，二处OperationDeadline若同时提供必须相等。Reference、Assumptions、Criteria、Parent全部编码，禁止因null/无UI省字段。

S7桥新增类型是v0.2未实现扩展：Agreement tag6在Pairs后显式追加Deming nullable，旧tag6截尾不自动补null；tag1–5/7–8和本页所有旧Golden/Benchmark身份不变。仅tag6/Deming新输入union tag5按此完整定义接收；明确与上游S7 family byte域不同。

- `DemingPointPlan`编码按公开位置字段：XRole/YRole/CenterX QuantityValue/XConversion/YConversion/Method/Pairing/ErrorVarianceEvidence/ReturnDetails/Budget。每DemingAxisConversion=SourceUnit/TargetUnit/Scale/Offset/Evidence ArtifactRef；NumericDefinitionText=Id/Revision/Body/Source ArtifactRef（不能把定义自身hash放Body）；DemingBridgeBudget逐公开13字段，Int32前8项与MaxNotifications，Int64两个bytes，TimeSpan两个ticks。Plan自身无hash字段。
- `DemingBridgeObservation`按RowId/SourceObservationId/SourceRevision/OriginalEvidence nullable/State单byte（本页DemingMemberState0..6）/Reason nullable/Unit/Value nullable；DemingBridgePair=PairId/Left/Right/ClusterKey nullable。Pairs按PairId Ordinal排序，Members在QLNI仍保留声明序、源QLIP按原规范ObservationId序；双方关联以ID，不因排序换配对。
- `QLDP`：header → SourceSnapshot ArtifactRef → 完整DemingNumericInput（Stratum/Plan/SourceErrorVarianceRatio/转换后CenterX/转换后ErrorVarianceRatio/Pairs），全字段同上。本域保留原来源/转换及双侧unit/value/state，排除未来QLNI/S7 Source/Input/Result hash。SHA256(QLDP)仅作为S7 SourceBoundary/EvidenceReference的确定内容引用，Root保持原bytes供重取，不冒客户签名。
- `QLNI`新tag5完整原字段规则沿上表；InputOrderHash=QLMS(原Members)先计算，QLDP无InputOrderHash，QLNI随后计算，最后S7各域按上游原编码单向生成。Definition/Policy/Task/Source/MemberSet/PairSequence/INPUT/REQUEST的S7字节由Adapter的EncodeS7Request/GetS7InputSha256/GetS7PairSequenceSha256按原§7.1.3.10规范实现，不是statistics现有未声明公共codec API；不得将QLDP header混入S7域头或复用QLNI hash当S7 Input.ContentHash。
- 结果保留专用NumericDemingDetail/Identity/BackendDiagnostics完整字段；完整运行报告编码/严格reader由本模块A.5.4提供，Deming按其全部公开字段进入QLRP/QLAR，不造Deming-only哈希；既有请求/源域向量不变。测试断言和耐久读回均消费完整结果，不把显示JSON当数值身份。

Benchmark新增域仍用同一8-byte v0.2 header与基本类型规则，仅变更未接收的tag8 payload；本轮明确扩展tag6；已闭tag1–5/7及Golden向量不变。旧tag8缺新字段/尾截断拒绝QLF-INPUT-INVALID，不能以默认空补旧资产。Profile/Recorded分版本严格解析，不支持任意JSON或反射字段发现。

- `QLBP`：header → BenchmarkProfile所有公开位置字段（ProfileId/Revision/Environment/Workload/Dimensions/Arrivals/LatencyTargets/Sampling/Limits/Failures）。WorkloadDimension=Name/Unit/Value(Int64)；ArrivalSlot=Iteration(Int32)/Offset(TimeSpan ticks)；LatencyTarget=Stage/MinimumSamples/P50?/P95?/P99?/TargetSource?；BenchmarkSampling=Period/ReadBudget/Metrics/MaximumSamples/RequireCompleteSampling；ResourceMetricSpec=Metric/Scope/TargetId/Unit/Acquisition/Attribution；BenchmarkLimits=PrepareBudget/InvokeBudget/TotalBudget/CleanupBudget/MaxResidentBytes(Int64)/MaxAssetBytes(Int32)/MaxDetailRows(Int32)；BenchmarkFailureTarget=MaxFailed/MaxCancelled/MaxTimedOut/MaxNotExecuted各Int32及TargetSource。nullable/list/ArtifactRef沿A.5，缺字段不是null。Profile Dimensions按Name、Arrivals按Offset再Iteration、LatencyTargets按Stage、Metrics按Metric/Scope/TargetId的UTF8键序；重复键拒绝。不包含Profile自己的ArtifactRef或hash。
- `QLBW`：header → Plan.Probe/Build/Input ArtifactRef → WarmupIterations/MeasuredIterations/Parallelism → Deadline? → ArrivalMode/CacheMode/FailurePolicy → Budgets（按Metric/Scope/Unit排序，逐ResourceMetricBudget公开位置字段包括TargetSource?）→ Profile ArtifactRef。**排除ExecutionMode和RecordedRun**，因此执行来源与事后分析可核同一冻结工作计划且无录制hash循环；这两个字段仍在完整QLRQ中，不能据QLBW替代操作身份。
- `QLBR`：header → BenchmarkRecordedRun全部公开位置字段（RunId/OriginCalculationId/OriginRequestSha256/Origin/WorkPlanSha256/Profile/Probe/Build/Input/Environment/Clock/AcceptedTick/PreparedTick?/MeasuredStartTick?/MeasuredEndTick?/ProbeReleasedTick?/ResourcesReleasedTick?/Complete/DroppedSamples/CancelRequestedTick?/Sessions/Attempts/Samples）。Clock=DomainId/Frequency(Int64)/Source；ProbeSessionRecord=LeaseId/WorkerId/Lane(Int32)/Mode/PrepareStartTick/PreparedTick/ReleasedTick?；ProbeRun=InvocationId/Iteration(Int32)/Warmup(bool)/Lane(Int32)/WorkerId/Outcome(byte)/ReadyTick/EnqueuedTick/StartTick?/ActualCompletionTick?/ResourcesReleasedTick?/OutputSha256?/Reason?；ResourceSample=Tick(Int64)/Phase(byte)/Metric/Unit/Scope/TargetId/Value(nullable double)/Attribution/Reason?。所有tick/计数Int64，序号/lanes Int32；enum以本节声明从0起位置，Origin=Executed0/SoftwareFixture1，Outcome=S/F/C/T/NotExecuted=0..4，SamplePhase=BeforePrepare0/AfterPrepare1/AfterWarmup2/Measured3/AfterProbeRelease4。Sessions按PrepareStartTick再Lane再LeaseId，Attempts先Warmup=true组后false组、各按Iteration，Samples按Tick再Phase再Metric/Scope/TargetId排序（同完整键重复拒绝）。稳定排序不改变原时间/状态，不按实际完成顺序重新分配index。

Benchmark诊断复用本页QLF-INPUT-INCOMPLETE（资产缺失/未读全）、QLF-INPUT-IDENTITY（同源异内容）、QLF-INPUT-INVALID（格式/版本/有效域）、QLF-PORT-CONTRACT（端口回执不符）、QLF-BUDGET-EXCEEDED；用FieldPath/MessageKey传三语资源，不另造错误权威。

Decode先核长度/计数/字符串上界及Root剩余字节再分配，严格消费到EOF；非canonical输入顺序也拒绝（Decode→Encode不相等），不会只重排后静默采用。同Source不同bytes返回QLF-INPUT-IDENTITY，字段错误含路径，错误解析不产生部分Plan/Run可派发对象。Source SHA校验与Decode纯语义分开；reader不得把流没读全伪装成完整byte数组。Profile的超限拒绝无Probe副作用；QLBR的Complete=false允许诊断解析但不可达标。所有新增DTO在BCL Core，Probe/Sampler适配包自己映射真实API，不在Core下载runtime/统计/BenchmarkDotNet运行库。

| Analysis tag | payload的完整有序字段 |
|---|---|
| 1 BiasAnalysis | BiasPlan.Reference、Confidence(nullable)；Reference按Certificate/Assigned/StandardUncertainty(nullable)/CorrelationGroup/ConditionsRef/UseRelationRef，Confidence按Probability/OriginalText |
| 2 LinearityAnalysis | Levels(list QuantityValue)、Assignments(list，每项ObservationId/Reference QuantityValue，按ObservationId序)、Confidence(nullable)；每个实际Observation恰一分配，Reference属于Levels，缺映射/冲突拒绝 |
| 3 StabilityAnalysis | ModelId、Window、MinimumDays、RepeatsPerDay；实际时刻取原Observation，不据文件顺序造时间 |
| 4 GrrAnalysis | ModelId、Parts、Operators、Repeats、Crossed、VariancePolicy(byte RawOnly=0/PreserveRawAndClampNegative=1)、StudySpanFactor(nullable double)、Tolerance(nullable Lower/Upper QuantityValue)；null不算公差比例，不默认客户阈值 |
| 5 UncertaintyAnalysis | Components(list)、Covariances(list)、Coverage；Component按Id/Type/Source/U/Sensitivity/CorrelationGroup/Distribution/DegreesOfFreedom；Covariance按Group/Units(list)/Values(matrix)；Coverage按Kind/K(nullable)/Basis/Probability |
| 6 AgreementAnalysis | MethodId、LoaMultiplier、ErrorVarianceRatio(nullable)、PairingPolicy ArtifactRef、Pairs(list)；每Pair按PairId/Stratum/SideA(nullable ID)/SideB(nullable ID)，全外连接保留单侧缺失；追加Deming(nullable DemingPointPlan)，null保留原行为，non-null字段闭包见下段 |
| 7 GoldenAnalysis | UInt32 length + 完整QLGP bytes；GoldenRequest.Plan必须与Request.Analysis.Plan字节完全相等，不能两个Plan并存 |
| 8 BenchmarkAnalysis | Probe/Build/Input各ArtifactRef，WarmupIterations/MeasuredIterations/Parallelism、Deadline(nullable)、ArrivalMode/CacheMode/FailurePolicy、Budgets(list，每个ResourceMetricBudget的Metric/Scope/Unit/PeakLimit(nullable)/RetainedLimit(nullable)/Window/AllowedSlope(nullable)/TargetSource(nullable)全写)、ExecutionMode(byte ExecuteProbe=0/AnalyzeRecordedRun=1)、Profile ArtifactRef、RecordedRun(nullable ArtifactRef)；BenchmarkRequest同样核两个Plan相等 |

公开声明（与其它class声明片段相同，不是现有实现）：

```csharp
public static class QualificationCodec {
    public static byte[] EncodePlanContent(IReadOnlyList<PlanCell> cells,string factorsRef,
        string randomizationRef,string assumptionsRef,int expectedCount);
    public static byte[] EncodeInputContent(ExperimentPlan plan,IReadOnlyList<Observation> observations);
    public static byte[] EncodeBenchmarkProfile(BenchmarkProfile profile);
    public static BenchmarkProfile DecodeBenchmarkProfile(ReadOnlySpan<byte> bytes,BenchmarkDecodeLimits limits);
    public static byte[] EncodeBenchmarkWorkPlan(BenchmarkPlan plan);
    public static byte[] EncodeBenchmarkRecordedRun(BenchmarkRecordedRun run);
    public static BenchmarkRecordedRun DecodeBenchmarkRecordedRun(ReadOnlySpan<byte> bytes,BenchmarkDecodeLimits limits);
    public static byte[] EncodeDemingInputContent(ArtifactRef sourceSnapshot,DemingNumericInput input);
    public static byte[] EncodeNumericMembers(IReadOnlyList<Observation> members);
    public static byte[] EncodeNumericRequest(NumericRequest request);
    public static byte[] EncodeCases(IReadOnlyList<GoldenCaseResult> cases);
    public static byte[] EncodeGoldenPlan(GoldenPlan plan);
    public static byte[] EncodeRequest(QualificationRequest request);
    public static ArtifactRef ArtifactFromBytes(string ns,string id,string revision,ReadOnlySpan<byte> bytes);
}
```

ArtifactFromBytes只计算SHA-256并返回显式身份，不保存、不注册、不签署；Fixture保留原bytes供核对。SHA采用小写hex，ActualBytes均由生成bytes.Length取值，不能手填近似数。正文的资源预留另按输入/中间/结果/端口上界计账，不把canonical字节数当峰值。

#### A.5.1 完整可构造 Replay Request Golden

唯一字段例即§12的 `CreateReplayRequest()`。全部引用各自绑定实际内容，以下域独立按字段在内存重建，未运行产品Codec：

| 域 | bytes | SHA-256 |
|---|---:|---|
| QLEP：Cells空、f/r/a、ExpectedCount=0 | 31 | `c5e04068ac72dafc3c115f33e3b59dfedf9d65200b132f1274f1d17581cbf0a8` |
| QLIP：上述plan/replay/1引用、Observations空 | 103 | `72c3e3d57bddedb2b46735ac960babc1bc7bd47d177ebe6333ab232ec9321a46` |
| QLCS：C01/P01/E/Consistent/A | 37 | `03b2bbeffe0aedf5781d54cb9eaead2fbb8b543d4f2a9448eebfceb575f65b90` |
| QLGP：P01、上述cases/r01/1引用、cmp/r01/1引用、PARENT/exact-v1/空seed、1、上述manifest | 250 | `6eab19c20281531061098bcc6985e8b9165b39b7c4d0300d11d699b2ac5a7455` |
| QLRQ：完整§12 G01/RG01 Request | 974 | `19b5c3d290046bebe246079501c31bb2ab557e96d4fc42acdba97e674338a14d` |
| Study QLEP：§12 C1/C2/C3、f/r/a、ExpectedCount=3 | 145 | `e304aaf7c371e2d1923c362874788ca22a08eecca20099576ea0d93b73151576` |
| Study QLIP：§12 study计划引用、O1/O2/O3完整观测 | 561 | `c9f87678631ed49683db4988aedde630637a33725fd391bb683e198dbf1a6b6b` |

完整QLRQ字节为下列hex（换行只供排版，不能进入hash）。测试必须从§12公开构造字段编码，然后分别核byte-for-byte、长度、hash；仅对复制hex算hash不算通过。

```text
514c52510000020003000000302e3203000000473031040000005247303109000000476f6c64656e2e76310300000031
2e30060000006d6574686f6406000000676f6c64656e0100000031400000003133633762346165626430643465383033
346334623633343736613530393531373963373663303263663436636165646130633031343237333938356261393607
0000006e756d6572696306000000706f6c69637901000000314000000031666161383830333761653632356130633233
316638626238373466343734303466656362366134373762346461626638383037626563396264643361336135070000
006261636b656e64060000007265706c6179010000003140000000336238663838366265653733323661303336613631
363263336561666266653135363536316435623335383064346433336435326637613634386538306666350600000072
6573756c740100000031030000006f6e65010000003101000000310100000073060000007265706c6179010000006308
000000736e617073686f74060000007265706c6179010000003140000000373263336533643537626464656462326234
363733356163393630626162633162633762643437643137376562653633333361623233326563393332316134360000
000000000000670000000000000040000000373263336533643537626464656462326234363733356163393630626162
6331626337626434376431373765626536333333616232333265633933323161343604000000706c616e060000007265
706c61790100000031400000006335653034303638616337326461666333633131356633336533623539646665646639
643635323030623133326631323734663164313735383163626630613801640000000000000064000000000000002000
00000800000000001000000000000100a3e111000000000100a3e11100000000002d31010000000007fa000000514c47
500000020003000000503031050000006361736573030000007230310100000031400000003033623262626566666530
616564663537383164353463623965616561643266626238623534336434663261393434386565626663656235373566
363562393003000000636d70030000007230310100000031400000003561393433313462386364393930343334353266
633639333930333034643135623161306165383364333062653966336536333236626330646338346465393706000000
504152454e540800000065786163742d7631000000000100000001000000030000004330310300000050303101000000
4501010000004100000000000000
```

Method参数原bytes为ASCII `golden-exact-v1`（hash `13c7b4aebd0d4e8034c4b63476a5095179c76c02cf46caeda0c014273985ba96`），NumericPolicy为 `engineering-binary64-v1`（`1faa88037ae625a0c231f8bb874f47404fecb6a477b4dabf8807bec9bdd3a3a5`），Backend为 `fixture-replay-v1`（`3b8f886bee7326a036a6162c3eafbfe156561d5b3580d4d33d52f7a648e80ff5`），Comparator为 `exact-v1`（`5a94314b8cd99043452fc69390304d15b1a0ae83d30be9f3e6326bc0dc84de97`）；这些小字符串是版本化测试fixture的完整内容，不冒充真实后端/政策资格原件。真实Adapter必须解析对应正式内容，不能把fixture字符串当运行参数。TestNumericsPort的NumericResult须填TaskId=bias-moments、Coverage=(3,3,0,0,0,0,0,0)、Integers[count.bias]=3和Values[mean/m2/sample-variance]=0/2/1、对应ValueEvidence State=Computed、单位分别um/um²/um²；Psd/Distribution/Inference=null；Provenance的Backend Validation=Unverified，SourceSnapshot/QLNI/QLMS取本次请求，不编造statistics运行版本/MemberSequenceHash；oracle的CoreApiVersion/ImplementationVersion明确为fixture-0.2/fixture-bias-v1，StatisticsSnapshotId=fixture/B01，MemberSequenceHash明确为QLMS测试序列身份，不能当真实上游桥证明。

旧37-byte QLFG向量（hash `4581190ac8a90ce6ea0a8e7cdc838b3d2a7d910281170dcaa4375714b85067e3`）只保留为历史子域研究，不是v0.2完整请求codec。主控已重建的256-byte QLGP结构向量（hash `b5ee4737c2e58e1259c37924901d84c514f0da5c00b5732b734e2e6a5d76d839`）继续有效：PlanId=P01，Cases=cases/r01/1/H，Comparator=cmp/r01/1/H，PARENT/exact-v1/seed-1，PlannedCases=1、C01/P01/E/1/A，H为UTF-8 `qualification-host-fixture-v1` 的hash `ef7e5c4596ca7d74c503062bce0e3c98f89863facb7422e2ab2d61e9682c15ed`。它是**结构向量**，两个引用指向同一opaque来源，不能替代本轮不同内容封口的Host。新完整Request使用上述974-byte向量，未重写旧身份。

#### A.5.2 Benchmark公开字段规范向量（本轮增量）

来源为A.3.3.1完整构造；Source OriginRequestSha256绑定同页实际BEN-ORIGIN QLRQ（Execute模式、RecordedRun=null），不是opaque字符串。QLBW排除Mode/Recorded引用，执行与分析工作计划相同；两个完整QLRQ身份各异。以下从公开字段独立构造并由另一逐字段reader消费到EOF，未运行产品Codec；附尾byte负例拒绝，QBEN-01的四组分位及50/s吞吐手算核对一致。原A.5.1的974-byte QLRQ、旧256-byte结构向量保持原身份。

| 新域/完整请求 | bytes | SHA-256 |
|---|---:|---|
| QLBP Profile | 402 | `4dfdfb3ed4069f06fca30a816ab5563adeb52835928dcfad640990546bd497bc` |
| QLBW WorkPlan | 444 | `bdc51b8843efefffc2cefdcfb5fe3c8235d0e2e1ff79484296830c2a56f84d80` |
| QLBR RecordedRun | 2071 | `3b3aba3d0755d1bd7cb7086f7ddd7dad5849f1e80a5df32563ee17fc154e140a` |
| QLRQ BEN-ORIGIN Execute source | 1171 | `84ca63f41720dc748b4e68556938ab63a8002c38da5adcbd78c1ce36261d5188` |
| QLRQ BX-EXECUTE Host | 1171 | `81a62fe88e1c39fcd336844cfe9acd7e9ab0aa25e0144ff904763251daab2bb9` |
| QLRQ BR-ANALYZE Host | 1268 | `9c8faac2c36c8440b878f68c3e76762ad5937f7bf4594f800972cc913f37ebcd` |

QLBP完整hex（仅换行供显示）：

```text
514c4250000002000400000042503031010000003103000000656e760400000074657374010000003140000000626339
633537653730313432386364653366363034303561393431616364656333633136396663326361393062653961643232
37363135653664343061663737040000006c6f6164040000007465737401000000314000000030313461323536343831
353032383363656337393336336230373432366162633336306530376664333362393837393339393465326434616162
313733383666010000000500000063616c6c7305000000636f756e740300000000000000000000000100000007000000
536572766963650100000000000000a086010000000000809698000000000001000000120000006d616e616765642d6c
6976652d62797465730700000050726f6365737304000000686f7374040000006279746506000000506f6c6c65640a00
00004174747269627574656488130000018096980000000000809698000000000000a3e11100000000002d3101000000
000000800000000000000010000a00000000
```

QLBR完整hex（按上述Profile/WorkPlan/OriginRequest引用；仅换行供显示）：

```text
514c42520000020004000000425230310a00000042454e2d4f524947494e400000003834636136336634313732306463
373438623465363835353639333861623633613830303263333864613561646362643738633163653336323631643531
383801400000006264633531623838343365666566666663326365666463666235666533633832333564306532653166
66373934383432393638333063326135366638346438300d00000062656e63682d70726f66696c650400000042503031
010000003140000000346466646662336564343036396630366663613330613831366162353536336164656235323833
353932386463666164363430393930353436626434393762630500000070726f62650400000074657374010000003140
000000346665663237353034356666623466303666373436383766343865373236633765636531646464623936663266
63396130616137356264303634643034373462050000006275696c640400000074657374010000003140000000363038
326530313730363034306332376333633963613138616662336130363630376261386530376134623532343865343030
65636666333734636365343861040000006c6f6164040000007465737401000000314000000030313461323536343831
353032383363656337393336336230373432366162633336306530376664333362393837393339393465326434616162
31373338366603000000656e760400000074657374010000003140000000626339633537653730313432386364653366
363034303561393431616364656333633136396663326361393062653961643232373631356536643430616637370d00
0000666978747572652d62656e6368e80300000000000007000000666978747572650000000000000000010200000000
000000010a00000000000000014600000000000000014b00000000000000015000000000000000010000000000000000
0001000000030000004c30310300000057303100000000090000005761726d5265757365000000000000000002000000
00000000014b00000000000000030000001400000042454e2d4f524947494e2f6d6561737572652f3000000000000000
000003000000573031000a000000000000000a00000000000000010c0000000000000001160000000000000001190000
000000000001400000003434383837356637313364323533313764313734633463343234666336353564343665323635
6438343430343066383432636434393737353932326365356632001400000042454e2d4f524947494e2f6d6561737572
652f3101000000000000000003000000573031001e000000000000001e00000000000000012100000000000000013000
000000000000013200000000000000014000000034343838373566373133643235333137643137346334633432346663
363535643436653236356438343430343066383432636434393737353932326365356632001400000042454e2d4f5249
47494e2f6d6561737572652f3202000000000000000003000000573031003c000000000000003c00000000000000013d
000000000000000145000000000000000146000000000000000140000000343438383735663731336432353331376431
37346334633432346663363535643436653236356438343430343066383432636434393737353932326365356632000a
000000000000000000000000120000006d616e616765642d6c6976652d62797465730400000062797465070000005072
6f6365737304000000686f73740100000000000059400a00000041747472696275746564000200000000000000011200
00006d616e616765642d6c6976652d627974657304000000627974650700000050726f6365737304000000686f737401
00000000000059400a00000041747472696275746564000a0000000000000002120000006d616e616765642d6c697665
2d627974657304000000627974650700000050726f6365737304000000686f73740100000000000059400a0000004174
747269627574656400140000000000000003120000006d616e616765642d6c6976652d62797465730400000062797465
0700000050726f6365737304000000686f73740100000000000059400a00000041747472696275746564001e00000000
00000003120000006d616e616765642d6c6976652d627974657304000000627974650700000050726f63657373040000
00686f73740100000000000059400a0000004174747269627574656400280000000000000003120000006d616e616765
642d6c6976652d627974657304000000627974650700000050726f6365737304000000686f7374010000000000005940
0a0000004174747269627574656400320000000000000003120000006d616e616765642d6c6976652d62797465730400
0000627974650700000050726f6365737304000000686f73740100000000000059400a00000041747472696275746564
003c0000000000000003120000006d616e616765642d6c6976652d627974657304000000627974650700000050726f63
65737304000000686f73740100000000000059400a000000417474726962757465640046000000000000000312000000
6d616e616765642d6c6976652d627974657304000000627974650700000050726f6365737304000000686f7374010000
0000000059400a00000041747472696275746564004b0000000000000004120000006d616e616765642d6c6976652d62
7974657304000000627974650700000050726f6365737304000000686f73740100000000000059400a00000041747472
69627574656400
```

#### A.5.3 Deming桥新增派生identity Golden（仅本轮）

输入唯一来源为A.3.1.1.1两Host：原六观测QLIP bytes相同但SourceSnapshot.Id分别deming-noise/deming-unit；保留完整原来源引用，不把目标单位变换写回原Observation。以下在内存依本页QLDP/QLNI规则及上游S7**编码规范**重建（不是S7算法实现），QLDP由独立逐字段reader完整消费到EOF，QLDP→QLNI→S7 SOURCE/PAIR/TASK/INPUT/REQUEST无回写环。方法/配对/误差比/政策/有效Budget均进入各域，噪声与换单位身份不同。S7上游已接收normal/swap 2011/1979-byte原件、26项字段及Expected145-byte原件只引用，不重建全审。

| Host新域 | bytes | SHA-256 |
|---|---:|---|
| noise/QLIP | 1309 | `20eea89de24319bf7c5ab44440e7983a11e66e256c92d02b4491311b55d4e4a2` |
| noise/QLMS | 1218 | `3625b44ace50d0d51faa4ac1bb87f6173e6c5465c69d008be871e6f433af82a7` |
| noise/QLDP | 2317 | `6e44c4122da5e38256b767f20d69992d08181035aedeb908346db82aa14552a0` |
| noise/QLNI | 5748 | `3b1d79d7e2b3a06ac37a4636014a954ceb7b34b6f5c6d303a60a7bb7a596ed7a` |
| noise/S7-PairSequence | 2614 | `3ca0c93bea7706c01fcc66f03da3f57d0cca8d505855a00647d4c758741b6f51` |
| noise/S7-Task | 3033 | `07b09d6a98d20bf81a7118296d9899227ca67291e6b83b833ac10889314234ff` |
| noise/S7-Input | 4050 | `2d7fffb6af7d9ce88f5de1d64d8c9c459fd4f1a0babb5ac57546fccc6602ee60` |
| noise/S7-Request | 4175 | `1e7c957fe9fe6b7741482e7f83af7d83739a2efb080a63be42bc50eb5acee890` |
| unit/QLIP | 1309 | `20eea89de24319bf7c5ab44440e7983a11e66e256c92d02b4491311b55d4e4a2` |
| unit/QLMS | 1218 | `3625b44ace50d0d51faa4ac1bb87f6173e6c5465c69d008be871e6f433af82a7` |
| unit/QLDP | 2350 | `3812e8e179aa03662787cdbab87e77ae6ef1ef09a33246974f69f45641f7d6a2` |
| unit/QLNI | 5814 | `b43eac7cab65d349f485a1ae168bd75733d3bde3b5c339582e7802da82ce8735` |
| unit/S7-PairSequence | 2614 | `fac8712b65a7c011f40f186942906c99c1a9aa52d6bef37ed1a719fb7f57b81b` |
| unit/S7-Task | 3033 | `71df28c80e82f65a7a700b4083433c3cf0fe2c821e08e5a343e819b2b5f24e80` |
| unit/S7-Input | 4048 | `5b99e753472ae9321f70b1c4c18587d7008ee79152ef44975eca2a2d544e49cb` |
| unit/S7-Request | 4172 | `020b5c584ed5dfc89f870a0995243a43a577e16ce8d50cc5292b216b40363d9a` |

本页这些新S7 Request长度/hash属于桥派生来源；不得拿它们替换上游normal/swap原请求身份或原Golden。数值仅以Fraction精确核本桥n3/Moments与90位Decimal核S7 D7-004固定正常oracle，换单位β按1/1000比例、λ按1/1000000平方比；实际ComputeNumerical/Capabilities/运行Golden仍未执行。旧974/256与Benchmark所有域及两个完整Host身份保持。

#### A.5.4 完整报告/原请求归档的唯一codec（Report API 1）

<a id="qualification-report-archive"></a>

报告编码属于qualification原Owner，不转嫁训练治理、存储或未来开发者。A.1～3的Contract0.2、旧QLRQ/QLNI/Benchmark/S7输入域保持；本节独立Report API 1，定义`qualification-report/1`与`qualification-report-archive/1`，首次正式报告格式不读不存在的旧codec。以前页面JSON、37-byte局部case、256-byte结构向量、974-byte请求及QLBR只是来源/输入，均不能替完整报告。Core生产DLL提供下列公开入口；不依赖测试helper、WPF/反射/动态类型加载。

```csharp
public sealed record QualificationArchiveLink(string Path,ArtifactRef Reference,string Role,string Owner,
    long? Bytes,string? MediaType,string? Format);
public sealed record QualificationReportArchive(string ArchiveSchemaVersion,QualificationRequest Request,
    QualificationOutcome Outcome,QualificationReferenceDocument? Reference,
    QualificationReplayEvidence? Replay,IReadOnlyList<QualificationArchiveLink> Links);
public sealed record PreparedQualificationArchive(ArtifactRef Archive,ArtifactRef Report,
    string RequestSha256,ReadOnlyMemory<byte> CanonicalBytes);
public sealed class QualificationReportCodec {
    public QualificationReportCodec(QualificationCodecLimits limits);
    public QualificationReport SealReport(QualificationReport report);
    public byte[] EncodeReport(QualificationReport report);
    public QualificationReport DecodeReport(ReadOnlySpan<byte> canonicalBytes,string expectedSha256);
    public byte[] EncodeArchive(QualificationReportArchive archive);
    public QualificationReportArchive DecodeArchive(ReadOnlySpan<byte> canonicalBytes,string expectedSha256);
    public byte[] EncodeReplayEvidence(QualificationReplayEvidence evidence);
    public QualificationReplayEvidence DecodeReplayEvidence(ReadOnlySpan<byte> canonicalBytes,string expectedSha256);
    public byte[] EncodeReferenceDocument(QualificationReferenceDocument document);
    public QualificationReferenceDocument DecodeReferenceDocument(ReadOnlySpan<byte> canonicalBytes,string expectedSha256);
}
public sealed class QualificationReportArchiveFactory {
    public QualificationReportArchiveFactory(QualificationReportCodec codec);
    public PreparedQualificationArchive Prepare(QualificationRequest request,QualificationOutcome outcome,
        QualificationReferenceDocument? reference,QualificationReplayEvidence? replay,
        IReadOnlyList<QualificationArchiveLink> links);
}
```

limits全部显式、无隐藏默认：MaxBytes∈[8,268435456]、MaxStringBytes∈[1,4096]、MaxItems∈[1,1000000]、MaxTotalItems∈[1,8000000]、MaxDepth∈[1,64]。集合总计数跨递归累加、每段长度checked，先核Root可用输入/冻结副本/typed writer/结果/stream最坏工作内存，不能只计最终文件；不够则拒绝、不截明细。小软件fixture用(16777216,4096,1000000,2000000,32)，这是工程限额，不是工业性能达标值。每Codec实例只持只读limits，方法无外部IO、无全局状态；调用方给Root预算，不在UI线程编解大数组。Decode返回深冻结数组/只读map；ReadOnlyMemory并不自动不可变，Prepare始终复制并封口，输出底层数组不与draft/端口共享，返回方只读使用。

**完整typed格式，不采用自动JSON序列化。** 新域header为4 ASCII magic+LE UInt16 major=1/minor=0；基本string/int/long/bool/double/UTC/TimeSpan/nullable/list/map/blob仍用A.5唯一规则。新报告enum从本页公开位置0起1byte，ReportValue union Available=1/Unavailable=2；嵌套Analysis/Outcome分别使用原A.5 tag；任意未知tag/enum/非法bool/-0非canonical拒绝。DTO中的State/Code/Unit仍string原样：NumericalValueState词表依statistics冻结版本，NumericProvenance.ResultState另容本桥NotDispatched，未声明值拒绝，不自动解析新的后端类型。所有record均按本页位置字段递归typed写入，以下表中的特例优先；实现者须为每个类型显式write/read分支，禁止运行时反射推序或丢可选字段。

| 域与完整字段 | 唯一编码/排除与读回规则 |
|---|---|
| QLQS 完整原请求 | header1/0→blob(原QualificationCodec.EncodeRequest的完整QLRQ0/2)→blob(原QLEP完整Plan内容)→blob(原QLIP完整input内容)。QLRQ中Plan.Plan与Input.Snapshot原ref、Count/ActualBytes/hash逐核后，从QLEP/QLIP恢复完整ExperimentPlan.Cells和Observation/Excluded原outcome；不存在丢失的仅摘要输入。reader不将QLQS hash冒QLRQ/QLIP，Decode组装的原request再EncodeRequest需逐byte等原QLRQ。GoldenCaseManifest/Analysis/Assumptions/Criteria/Reference/parent都在QLRQ，不增字段改旧身份 |
| QLRP 完整QualificationReport | header1/0→CalculationId→ReportSchemaVersion（固定qualification-report/1）→Input/Plan/Method/Scope/Evidence→PlannedCount/ValidCount/FailedCount/ExcludedCount/NotExecutedCount→Values→Diagnostics→Completeness/Applicability/Criteria→RequestSha256→NumericalResults→Benchmark nullable。**只排除自身ContentSha256**，其余原公开字段全写；Decode用完整bytes实际SHA重建该字段。SealReport在副本设置schema与hash，原非空hash若不相同拒绝；Encode不忽略错hash。它不重算报告值/Criteria或把Complete改合格 |
| NumericResult递归闭包 | Values/Diagnostics/BackendCompletionId/Provenance/Tasks全位置字段；Provenance全18字段、每Backend7字段；每NumericTaskDetail的TaskId/Coverage/Integers/Values/Diagnostics/ValueEvidence/Psd?/Distribution?/Inference?/Deming?；Deming全位置字段含原三定义正文/Source、两侧Coverage、全部Moments/ScaledValues/Computation/PointDetails、两S7 hash、Identity及task/result两组BackendDiagnostics，任一null都写存在标记。S7 exponent用Int32不恢复double；df/count保持Int64。9政策参数、13Budget、Input9/Closure6及所有版本保留，不仅Slope/均值。QLRP中NumericalResults按OperationId UTF8升序、Tasks按TaskId升序，重复身份拒绝 |
| ReportValue/Diagnostics/map特例 | Available=tag1+AvailableValue(Value QuantityValue,Method MethodRef)，Unavailable=tag2+UnavailableValue.Reason。Values/Integers按UTF8键序，唯一；未请求量不可假Computed。QualificationDiagnostic完整11字段；BackendDiagnostic的5字段、Arguments有序不去重；同Code不同参数分别保留。Diagnostics、ValueEvidence、Backends、PointDetails等非map序列保持原合法请求/结果声明序，typed decoder不靠排序掩盖错序。原字符串token不是本地化文字 |
| BenchmarkReport递归闭包 | 全25个位置字段，Quantiles7字段、ResourceMetricResult13字段、Throughput6字段、Attempts与Samples完整行、SourceRun完整QLBR。SourceRun编码采用blob(原QLBR0/2)，不是显示摘要；Quantiles按Stage、Metrics按(Metric/Scope/TargetId)，其余行原规范顺序。原源运行身份/资源与当前Outcome.Resources分开，无clock转换/二次分位计算 |
| QLRF ReferenceDocument | header1/0→Projection原Assignment/Complete/SourceSha256→Use.EvaluatedUtc/ParsedCertificate/UseRelation/Identity/Conditions/Time/Use/Diagnostics。u/k/原Unit/共同CorrelationGroup保持；Unknown不是false=无误差。允许参考缺失报告保存带限制，不能封存出不存在的参考值 |
| QLRE ReplayEvidence | header1/0→Report/Input/Environment/Build/Comparator→Result全部4字段(Planned,Executed,CasesSha256,Cases)→Outputs全部8字段。Cases按CaseId、Outputs按CaseId，Parent/expected与actual原key及Source角色/refs均绑定；QLCS实际hash再核。Changed/Incomparable/Failed/NotExecuted原行不能用一致率替代 |
| QLAR 完整QualificationReportArchive | header1/0→ArchiveSchemaVersion固定qualification-report-archive/1→blob(QLQS)→Outcome的Terminal/CalculationId→blob(QLRP，必须非null完整报告)→Outcome.Diagnostics→Resources的Drained/ReleasedBytes/ReleasedSlots/DrainElapsed/CleanupDiagnostics→Reference nullable(blob QLRF)→Replay nullable(blob QLRE)→Links。Links按Path UTF8排序、Path唯一。完整request/report/运行诊断/真实释放/参考核对/Golden结果及全部外源目录同一封口；Outcome是不可变值，无Task/Root/Window/handle序列化 |

准确位置参数数以公开record为唯一依据，表中数字只是辅助阅读，不创建另一个字段Authority。Scalar State!=Computed时原有限值/Code组合按上游契约保留；数值null不以0补齐，非finite值拒绝。Scaled非零mantissa区间[1,2)绝对值，zero=(0,0)，状态/单位/Code逐原合同检查。有理/大整数内部scratch不序列化；已发布Scaled投影才是报告字段。

**Prepare顺序和身份DAG。** deep-freeze request/outcome/evidence/links→按原QLRQ/QLEP/QLIP重核source→核报告CalculationId/Input/Plan/Method/Scope/Evidence及RequestSha256等于request→SealReport生成QLRP原内容hash→生成QLRF/QLRE及完整QLQS→核Links覆盖全部外部依赖→编码QLAR→ArtifactFromBytes("qualification-archive",CalculationId+"/"+RequestSha256,"1",QLAR)，Report引用为ArtifactRef("qualification-report",同Id,"1",SHA256 QLRP)。Archive.Archive.Sha256为整个QLAR的hash，Report.Sha256/Report.ContentSha256是完整QLRP hash，RequestSha256仍原QLRQ；各自用途不同。QLRP不含自身hash，QLAR不含未来Archive/存储receipt/hash，来源输入中不存在回写环。完整报告可以Completed但NotEvaluated，Cancelled/TimedOut/Failed的部分报告也可归档且保原因；Report=null的拒绝/无报告操作由原ledger保存，不调用这个报告归档API假造空成功。

每报告计数不只核加和：Study按原观察范围（PlannedCount来自Plan.ExpectedCount）、Golden按plan案例范围、Benchmark按Measured摘要且Warmup全行在SourceRun、Deming NumericCoverage按Pair而非原6观测。分类互斥/完整分母与§6～7/A.3.3规则一致，不能将不同层计数强行相等。未知读页/执行/排空不自动Complete；Prepare不补算测量、分析、区间、分位、Golden比较或质量状态。需Criteria区间/独立性/完整性而报告缺证据或Criteria非NotEvaluated→QLF-PORT-CONTRACT；客户接受限未知仍可保存NotEvaluated报告。Cross-domain sourceEvidence真实性由原Owner，codec只校结构和身份。

Links覆盖所有原request/outcome/Reference/Replay中ArtifactRef，以及FactorsRef/RandomizationRef/AssumptionsRef/TargetRef/条件/用途/Golden文本键所指**外部**声明。规范Path为公开字段名加`/`、集合identity使用UTF8完整key的hex（如Request/Input/Observations/{hexId}/Evidence），map同hex键；不能用未经转义的key拼路径。内部小型参数/计划/原观测来源可通过归档内重新编码验证其ArtifactRef，Role=Embedded、Owner=qualification、Bytes=实际编码长度、Format=相应魔术/版本；不为未嵌入的证书/图像/Reference/Golden原输出写Embedded。外部Role=Source/Reference/Replay/Expected/Actual/Method/Policy/Environment/Build/Assumption/Criteria/Parent，Owner是精确原模块/宿主，Hash原样；外部Bytes/Format未知允许仅内存Prepare的限制性归档，但A.5.6耐久写前必须解析完整ObjectRef（含全部Format/Bytes），未知不能叫已完整保存。没有外部内容语义的f/r/a/c等fixture标签是原字面声明，不伪造文件ref；生产需有完整声明来源，缺失相应用途NotEvaluated。

#### A.5.5 严格读回、兼容拒绝与双消费者断言

读回流程：当前调用权与预算→流读到EOF且真实长度/hash→header/版本→先scan长度/总元素/深度后分配→strict UTF8/NFC/UTC/null/enum/finite与键序→还原所有typed值→按上述跨字段/原闭包校验→同codec Encode逐byte相同→才交付完整只读archive。expectedSha256必填小写64hex，错hash/未知schema/version/未知field union/重复key/截断/附尾/超限均QLF-INPUT-INVALID或QLF-INPUT-INCOMPLETE/IDENTITY，不兼容资产不重新序列化成新hash；QLRP单独reader只能读完整报告，不能假称同时恢复原请求或外部依赖。读取不运行Analyze/Compare/Probe，不重算数值以“修”旧报告；参数/method/定义版本无法识别也不能映为默认版本。

同ID同旧hash重复读保持原byte；将来新report schema用新精确reader注册，原reader/原字节/hash保留。当前无Report1→未知Report2迁移，无反射自由兼容；包API新增不自动扩展持久格式。请求Contract0.2未被这个Report1升级，旧tag6空Deming兼容规则仍A.5，本报告decoder严格按当前约定，不静默补新字段。Storage Format注册必须exact(schema/version/hash)，报告大于额度拒绝而非摘要保存；报告PDF/Excel/显示JSON是reporting模块或宿主投影，不能覆盖QLAR原件。

两个独立无UI消费路径在Core.Tests的`archive study`与`archive golden`（同一Exe不同进程、不同Owner/input；不增加测试工程）：Study用§12 CreateStudyRequest、bias=0/sample variance=1的明确software oracle完整NumericResult及NotEvaluated报告；Golden用§12 CreateReplayRequest、C01/P01/E/A两输出实际`result=ok`，Constructed输出Role=Synthetic，完整ReplayEvidence与Report。两者在原service结果资源真实归还后调用公开codec/factory，分别Encode/Decode/再Encode；完整请求bytes仍原原件，报告中的每个单位/method/count/Unavailable/diagnostic/hash及每个Actual/Expected source逐字段相等，codec测试不冒实际统计/Replay执行。Benchmark/Deming完整结果沿现有软件Host原返回值加入同suite反例，不重算上游已接收算法。

| QARC断言（Core.Tests/Storage.Tests使用） | 可确定输入与期望 |
|---|---|
| QARC-01 完整往返 | Study和Golden各完整QLAR；Decode→Encode字节相等，ReportSchema/报告hash/原QLRQ hash/Archive hash三者按域各核，所有map/诊断/完整原Plan/Observation/失败格/源单位/Assumptions/Criteria逐字段相等；Golden实际case不得只保存plan |
| QARC-02 两请求及部分结果 | 相同原请求的报告业务状态或一个Unavailable.Reason、一个backend参数/Scaled exponent变化：QLRP/QLAR hash变、原QLRQ不变；两个CalculationId不共享request/report identity。Cancelled/Failed报告保Terminal/Partial/诊断，不重写Completed |
| QARC-03 malformed | header/version/union/bool/null=2、string未NFC/非法UTF8、-0非canonical、NaN/∞、duplicate/乱序map/CaseId、length=UInt32.Max/递归超限/最后byte去掉或追加00：reader非成功、无部分对象/副作用。缺ContentSha不按0放过；一字节翻转错expectedHash拒绝 |
| QARC-04 完整数值 | 同原S7 fixture报告中的Scaled Exponent2改变、Arguments少一项、源definition body/Policy一位变、Backend.Validation变或PointDetails缺一pair：读回对应差异可见、hash改变/关联校验失败；不只比Slope。S6等外部结果不经本codec改为另一模型，未知typed结果拒绝 |
| QARC-05 参考/Golden/身份 | Report.RequestSha误置QLAR hash、Golden Result.CasesSha置plan hash、Expected绑定到Actual、ParentId不同、reference Complete但Use.Time=Unknown：前三结构错拒绝、未知用途保NotEvaluated，不变物理PASS；unknown参考不抹其它描述 |
| QARC-06 耐久知识 | 事务timeout/连接断/原技术CommitUnknown、对象缺Format/hash错、saveId同ID异payload、NoRead权、fence过期：不ReturnedSaved，不从report存在猜提交；按原operation查询，读回exact报告/依赖验证后才Durable。主task/lease/原CTS沿Root有限恢复 |
| QARC-07 进程重启 | 保存整个archive及原技术receipt，在新进程用同tenant/storeGeneration/CalculationId/request/report/archive精确键Read，不靠旧Root/Task或Current；必须完整bytes/hash/refs/receipt及只读验证相同。原operation未知仍Unknown，不重发Analyze/设备动作；隔离恢复格式缺reader→NotRestorable |

性能增量测点是Freeze/preflight→QLRP/QLAR encode+hash→stream IO→技术commit/原operation查询→exact读+strict decode→References验证→真正释放；使用已存在PerformanceProfile/DEV-GOV-010 P50/P95/P99和失败分母。负载固定四个有界档：0观察/1Golden case；Study1000/10000行；Benchmark10000 attempts+上限samples；S7 ReturnDetails=true/false及实际MaxDetailRows边界（不再核算法）。报告≤MaxBytes和总元素边界/边界+1，记录多副本峰值、Read/Write暂停及cancel→实际释放；客户ms/耐久RPO/RTO由部署Profile，当前TargetsPending，不填编造门限。serializer O(总字段字节+排序k log k)、checked分配，无N²/任意反射/全量图像嵌入；输出超预算明确拒绝。

#### A.5.6 IM-066格式注册、耐久存取和训练治理精确消费

<a id="qualification-report-storage"></a>

唯一optional Storage程序集namespace Asun.Modules.Qualification.Storage，工程/测试落点A.3.4；只用IM-066现有注册式技术API，不创私有QualificationStore/文件目录/数据库连接池，也不让IM-066或治理复制本模块报告字段/判定。以下新类属于本模块桥的公开实施规格，外部Contracts只使用[IM-066 §6.3](../storage-database/DEVELOPMENT-GUIDE.md)已公开类型。SQL/codec/格式/读回验证责任为qualification原Owner；数据读取/存储scope/principal/凭证/根路径与维护执行属于部署/存储Owner。

```csharp
// In Asun.Modules.Qualification.Storage; only this optional DLL references IM-066.
using System.Collections.Immutable;
using Asun.Platform.StorageDatabase.Contracts;
using Asun.Modules.Qualification;
public sealed record QualificationStoredLink(ArtifactRef Reference,ObjectRef Object);
public interface IQualificationStoredArtifactResolver {
    ValueTask<ImmutableArray<QualificationStoredLink>> ResolveAsync(
        IReadOnlyList<QualificationArchiveLink> links,CallContext context,CancellationToken token);
}
public sealed record QualificationArchivePayload(VersionRef Schema,PreparedQualificationArchive Archive,
    ImmutableArray<QualificationStoredLink> Links) : IOwnerStoragePayload;
public sealed record QualificationArchiveReadPayload(VersionRef Schema,string CalculationId,
    string RequestSha256,string ReportSha256,string ArchiveSha256) : IOwnerStoragePayload;
public sealed record QualificationArchiveSaveRequest(CallContext Context,string SaveId,string IdempotencyKey,
    PreparedQualificationArchive Archive);
public sealed record QualificationArchiveQuery(CallContext Context,OperationIdentity SaveIdentity);
public sealed record QualificationArchiveReadRequest(CallContext Context,string CalculationId,
    string RequestSha256,string ReportSha256,string ArchiveSha256);
public sealed record QualificationArchiveStoredReceipt(string SaveId,string State,ArtifactRef Archive,
    ArtifactRef Report,string RequestSha256,OperationIdentity SaveIdentity,
    TechnicalCommitReceipt? Technical,ImmutableArray<ObjectRef> References);
public sealed record QualificationArchiveReadResult(QualificationReportArchive Archive,
    QualificationArchiveStoredReceipt Receipt,ImmutableArray<QualificationStoredLink> Links);
public sealed record QualificationStorageRegistration(StorageBindingCatalog Catalog,
    ImmutableArray<IStorageObjectFormatValidator> Formats,VersionRef ReferenceResolver,VersionRef ReadValidation,
    VersionRef WriteBinding,VersionRef ReadBinding,VersionRef InputSchema,VersionRef ReadSchema);
public static class QualificationStorageFactory {
    public static QualificationStorageRegistration CreateRegistration(VersionRef statementCatalog,
        QualificationCodecLimits limits);
    public static QualificationReportStorageAdapter Create(QualificationRoot root,RootReservation reservation,
        IStorageDatabase database,IStorageSession writeSession,IStorageSession readSession,
        QualificationStorageRegistration registration,IQualificationStoredArtifactResolver resolver,
        QualificationCodecLimits limits);
}
public sealed class QualificationReportStorageAdapter {
    public Task<QualificationArchiveStoredReceipt> SaveAsync(QualificationArchiveSaveRequest request,
        CancellationToken token);
    public Task<QualificationArchiveStoredReceipt?> QueryAsync(QualificationArchiveQuery query,
        CancellationToken waitToken);
    public Task<QualificationArchiveReadResult?> ReadAsync(QualificationArchiveReadRequest request,
        CancellationToken token);
}
```

Factory校所有Binding/OwnerKey/codec/schema精确版本、两session的原Host所有权/池用途及限额，再登记adapter请求/结果原Task容量。write/readSession是Host已通过IM-066 OpenSessionAsync在Root持有的分别Production/Query用途实例；adapter不Dispose宿主shared database/session，不偷偷Open新scope。完整IO借用资源在Host/IM-066原Task/ResourceHandle强持；Save/Read/Query工作启动前Root.StartOwned，实际完成与IM-066 ReleaseAsync/原Task状态分别核，不把对象返回当pool已释放。Root.Close不等待本身或UI协调，adapter工作不调用Root.Close；晚到技术receipt按原saveIdentity记录，两轴继续Owner。

**格式/Schema/codec正式注册规则。** 所有VersionRef为(Id,Revision=1,Hash=SHA256 UTF8 descriptor bytes)，不是手填示例hash。descriptor无BOM、LF、末尾LF；固定文本如下（管道是ASCII字面，不是动态字符串分隔解析）：

| ID | 精确descriptor一行（附LF）；职责 |
|---|---|
| qualification.report-v1 | `IM-049|ReportAPI1|QLRP|1.0|QualificationReport|A5.4`；完整报告格式/schema |
| qualification.archive-v1 | `IM-049|ReportAPI1|QLAR|1.0|QualificationReportArchive|A5.4`；完整归档格式/schema |
| qualification.archive-input-v1 | `IM-049|ReportAPI1|QLSP|1.0|QualificationArchivePayload|A5.6`；write InputSchema/InputCodec |
| qualification.archive-query-v1 | `IM-049|ReportAPI1|QLSQ|1.0|QualificationArchiveReadPayload|A5.6`；read InputSchema/InputCodec |
| qualification.archive-receipt-v1 | `IM-049|ReportAPI1|QLSC|1.0|QualificationArchiveStoredReceipt|A5.6`；write ResultSchema/ResultCodec |
| qualification.archive-read-v1 | `IM-049|ReportAPI1|QLSD|1.0|QualificationArchiveReadResult|A5.6`；read ResultSchema/ResultCodec |
| qualification.reference-resolver-v1 | `IM-049|ReportAPI1|OwnerRefs|1|exact-root-and-history|A5.6`；完整历史引用只读枚举版本 |
| qualification.read-validation-v1 | `IM-049|ReportAPI1|OwnerReadValidation|1|exact-QLAR-and-links|A5.6`；隔离恢复只读验证版本 |

描述hash仅标协议目录身份，不证明实现DLL/SQL未改；实际发布另绑定DLL BuildHash与StatementCatalog真实字节hash，版本1不得复用descriptor而暗改字段规则。CreateRegistration生成两个Binding及上述typed codecs/validators，不能靠schema名字找到随机CLR type。WriteBinding.Id=qualification.archive-append-v1，ReadBinding.Id=qualification.archive-exact-v1；Binding自身Version.Hash按IM-066正式descriptor全部字段typed编码生成，引用已生成Input/Result refs与调用方statementCatalog，不随Culture改变；Catalog hash按Binding.Version的完整有序列表及全部codec/format/version列表生成，精确decoder拒绝旧绑定/混schema。部署把Formats加入既有IM-066 FormatValidators注册，将StorageOwnerRegistration.OwnerKey=qualification和允许scope/stores、ReferenceResolver/ReadValidation精确refs加入既有注册目录；不在Core注册另一个storage runtime。

本桥InputCodec实现IStoragePayloadCodec的Version/Schema/PayloadType/Encode/GetReferences五成员，分别只认QualificationArchivePayload或QualificationArchiveReadPayload；ResultCodec实现IStorageResultCodec.Version/Schema/Validate，Read的完整typed Decode由本桥提供，不猜上游有Decode泛型接口。QLRP/QLAR FormatValidator仅对IM-066传入boundedReadStream精确长度有界读取并调用本Codec strict reader，不查外部对象、不保留流/改流所有权。两input codec的GetReferences必须读全信封到EOF后返回全部去重ObjectRef，Query参数返回Empty；同ObjectKey异hash/format/bytes拒绝。

| Storage域 | 完整字段闭包和hash关系 |
|---|---|
| QLSP | header1/0→Schema完整VersionRef→Prepared.Archive完整ArtifactRef→Prepared.Report完整ArtifactRef→原RequestSha256→blob(完整QLAR原bytes)→Links(count+逐Reference ArtifactRef+ObjectRef完整字段)。Links按Reference四字段UTF8 tuple排序、重复Reference拒绝；ObjectKey按IM-066 StoreId Ordinal/Generation数值/TenantId/StorageDomain/ObjectId，ObjectRef含Key/Bytes/Hash/MediaType/Format VersionRef。外ref.Sha256必须等Object.Hash.Hex，Bytes/Format/当前StoreGeneration与resolver证据一致；绝不仅存hash列表 |
| QLSQ | header1/0→ReadSchema VersionRef→CalculationId→RequestSha256→ReportSha256→ArchiveSha256。当前可信CallContext/权限不放credential在blob；精确query无latest或按时间最近 |
| QLSC write ResultBytes | header1/0→SaveId→Archive/Report ArtifactRefs→RequestSha256→完整References ObjectRef list（排序/去重）→状态string固定Stored。**不含当前TechnicalCommitReceipt或最终SaveIdentity.PayloadHash**，避免receipt/payload循环；原identity/Commit/AtUtc由IM-066技术回执提供，adapter据此组装完整QualificationArchiveStoredReceipt，State=Durable只有Committed+严格QLSC核对且当前依赖可读验真。失败/未知不伪造Stored正文 |
| QLSD read ResultBytes | header1/0→blob(原QLSP)→blob(原QLSC)→保存时的OperationIdentity全字段→TechnicalCommitReceipt全部字段（含原QLSC ResultBytes/State/References/ResultSchema/AtUtc）。原receipt不引用此次读回的QLSD，不循环。Runtime QueryOperationAsync可提供原技术receipt，Read结果assembler按QLAR/QLSC/原技术identity逐字段关联后交本桥只读值 |

IQualificationStoredArtifactResolver.ResolveAsync只把精确外ArtifactRef关联原Owner已发布ObjectRef/格式，不解释量测/判定；无受信ref映射、Bytes/Format未知或不是允许Store返回可定位拒绝，不能把原路径/文本hash伪造ObjectRef。Embedded refs逐QLAR重构内容核对、无需另存外Object；外部ref按完整ArtifactRef去重但保原Path与角色。References须覆盖所有外link，原SourceRun的Input/Profile/Build/环境/Source报告与Golden全部输出也覆盖；任何图库/模型等大对象仍在受控文件对象存储，不入QLAR/数据库blob。

**注册事务与Owner数据（不存在第二存储服务）。** 由本模块交付给IM-066的参数化StatementCatalog只允许下列三项，SQL由该技术session执行；部署采用自己的既有migration登记这些表，不在Factory隐式DDL。schema固定qualification、表report_archive作为本模块报告的不可变Owner投影，不能镜像产品工单/配方/质量事实：

- `ql.archive.append`：Serializable/Production、PermissionKey=qualification.report.write；输入QLSP，结果QLSC，Expected affected rows0..1，MaxCommands=3、MaxRetries=0、RetryDelay=0、ServerLockTimeout/ServerStatementTimeout取当前CallContext有限ExecutionBudget较小值，AllowEmptyBatch=false。同scope/store-generation/CalculationId只允许一份最终RequestSha/ReportSha/ArchiveSha，保存save_id、原idempotency_key和QLSP完整bytes；同键全hash/bytes一致返回原receipt（0行）；异内容Conflict，不UPDATE替换。
- `ql.archive.exact`：RepeatableRead/Query、PermissionKey=qualification.report.read，输入QLSQ、结果QLSD，Expected rows0..1、MaxCommands=2、MaxRetries=0、RetryDelay=0，AllowEmptyBatch=true。所有tenant/site/line/station/device/storeId/generation和四精确键同时限制，缺行返回NotFound，不扩大scope。原技术receipt由查询原OperationIdentity得到并assembler嵌入，不从SQL造Committed。
- `ql.archive.validate`：Read/Recovery用途，PermissionKey=qualification.report.restore_validate；按StorageOwnerRegistration仅枚举该Owner允许scope/store的完整报告及其refs、原operation/receipt，全部scan分页固定snapshot；每行strict QLAR/QLSP/QLSC、request/report/archive原hash与技术receipt核一致及所有外Object完整可读，任何缺失Unknown/false。校验不Analyze、不修数据、不产生Outbox。

表的完整列为tenant_id/site_id/line_id/station_id/device_id/store_id（text）、store_generation（bigint>0）、calculation_id/request_sha256/report_sha256/archive_sha256/save_id/idempotency_key（text）、canonical_payload（bytea）、references_payload（bytea，完整ObjectRef序列）、save_identity（bytea，完整原OperationIdentity）。主键为前7个scope/store字段加calculation_id，save_id/idempotency_key在同scope/store唯一；所有SHA字段CHECK 64小写hex，NOT NULL，payload长度受当前Binding/Root上界。真实技术operation/TechnicalCommitReceipt由IM-066同提交保存；本模块不另设operation状态表。append的三个注册commands依次为按完整scope/calculation取原行FOR UPDATE、若不存在则INSERT...ON CONFLICT DO NOTHING并取回、核全部字节/hash相同返回QLSC（原完整References）；读exact SELECT使用同完整scope与四键、只传参数，禁止自由SQL/反射字段。并发“原行不存在”时ON CONFLICT后的exact读同事务在Serializable竞争下可拒绝/Conflict；不自动循环重试或生成新的save_id。DDL/索引/参数类型与上述固定列是StatementCatalog实现基线，不能由普通程序员另选私有字段。

append在本表与IM-066 technical receipt同一正式事务线性化；references保护/GC pending publication使用IM-066既有协调能力，不能先RETURN Durable再保存refs。StatementCatalog的原正式SQL/Schema声明、Owner只读resolver分页和validation实施属于本模块未来Storage工程，内部设计已定；部署配置/真实DB耐久/backup/恢复实测仍是未运行门。外部所有者的保留期限/删除权由其政策，qualification不自动删除/清报告或过期证书，历史报告只能追加新计算引用。

**Save/Query/Read顺序。** Host拿原request/真正完成Outcome→ReportArchiveFactory.Prepare→resolver解析全外Objects（当前Read权/预算）→Registration.Write InputCodec生成QLSP→构造OperationIdentity(scope/store/generation,OwnerKey=qualification,OperationId=SaveId,IdempotencyKey=原键,PayloadHash占位)→按IM-066 Runtime.StorageRequestHasher.Compute(RegisteredTransactionRequest,binding,canonicalPayload,实际StorageInputLimits)取技术hash填回（不拿QLAR或QLRQ当技术hash）→原writeSession.ExecuteTransactionAsync→若只接纳/在途则database.GetTaskStatusAsync/QueryOperationAsync查原Task/operation，有限等待且原Root强持→只在原Commit.State=Committed、ResultSchema/ResultBytes严格QLSC、identity全同/References全同、QLAR完整读回核对时State=Durable。事务Unknown/超时保持State=Unknown+原SaveIdentity/Root/Task，不重新Save新身份。明确RolledBack/Rejected为Failed/Rejected且保技术fault；Query只读原OperationQuery，NotFound=null仅未证明该原提交，不自动重发。

Read当前CallContext批准→readSession.ReadAsync RegisteredReadRequest→strict QLSD/原SQL行与原operation技术receipt关联→DecodeArchive+References一致→逐外ref有权只读验证真实bytes/hash/Format（技术IM-066 Verify/OpenRead原Task及lease）→返回原完整archive和StoredReceipt。缺reader/字段/未知receipt/对象缺失拒绝返回可用完整报告，调用方可显示仅隔离的诊断；同一report存在不等于原保存Committed。同ID异scope/store-generation/Hash拒绝，不跨tenant回退；读取不赋用途批准/质量PASS。

耐久读/报表关系不返回活动Root/Task/旧CTS。崩溃前保存Unknown只靠原saveIdentity技术query恢复，报告运行本身若未完成仍原ledger/任务Owner，不从半保存补算。运行排空、事务提交和外部对象保留分别确认；断电恢复只有IM-066正式ReadValidation及全部依赖读回通过才称RestoredAndVerified。Owner ReferenceResolver用report_archive固定快照分页枚举**全部历史未删除**ObjectRef，Unknown/未读全不能当空引用；准备用于GC/backup的保留协调沿IM-066，不自行删除。

**训练治理当前准确消费位置：** [ai-dataset-governance §13.1.6、§13.2](../ai-dataset-governance/DEVELOPMENT-GUIDE.md)的A1-Qualification只需引用本Core公开QualificationReportCodec/ReportArchiveFactory，在原完整request/outcome及参考/Replay来源返回后Prepare；注册qualification.archive-v1或直接采用本Storage adapter保存。ReportRef绑定QLRP，耐久归档引用另绑定QLAR及原技术receipt，两者不得互换；治理存自己的dg.report-v1和用途原决定，只关联本归档ref，不复制QLRP schema/Case判定/分位。治理现在可用本节明确公开签名/格式绑定，内部上游报告codec设计缺口关闭；实际DLL/格式目录部署、外Object解析、SQL注册/权限及耐久恢复运行仍须真实验证。本轮不修改治理指导，不授模型用途，也不要求主控再代作模块内容审核。

### A.6 唯一测试工程、Adapter工程和准入门

核心测试工程仍唯一为 `tests/Modules/qualification/Asun.Modules.Qualification.Core.Tests/Asun.Modules.Qualification.Core.Tests.csproj`，固定 `<OutputType>Exe</OutputType>`、`<TargetFramework>net10.0</TargetFramework>`，只引用Core与.NET 10 BCL，不引入test SDK、第三方统计包或WPF。按批准切片新增的可选验证工程落点已冻结但本轮不创建：`tests/Modules/qualification/Asun.Modules.Qualification.Statistics.Tests/Asun.Modules.Qualification.Statistics.Tests.csproj`（Statistics bridge/Deming）、`tests/Modules/qualification/Asun.Modules.Qualification.Replay.Tests/Asun.Modules.Qualification.Replay.Tests.csproj`（Replay adapter）、`tests/Modules/qualification/Asun.Modules.Qualification.Storage.Tests/Asun.Modules.Qualification.Storage.Tests.csproj`（IM-066 registration/durability）和`tests/Modules/qualification/Asun.Modules.Qualification.Wpf.Tests/Asun.Modules.Qualification.Wpf.Tests.csproj`（双STA/UIA）；各自仅引用对应可选包/Core与冻结外部Contract，不把statistics/storage/WPF依赖倒灌Core。生产/Adapter工程落点为A.3.4；全部工程创建须先绑定可审计仓库与实现授权。入口参数为 `case Q01..Q21`、新增 `case QBEN-01..QBEN-08` 或 `suite qualification-core`（包含已接收的Benchmark新断言）; 每个 case 有有限迭代/数据上限和单调 deadline，超时由独立进程以非零退出，进程外层负责终止软件测试；不能把外层终止当 native 已排空。命令冻结为：

```text
dotnet build tests/Modules/qualification/Asun.Modules.Qualification.Core.Tests/Asun.Modules.Qualification.Core.Tests.csproj -c Release
dotnet run --project tests/Modules/qualification/Asun.Modules.Qualification.Core.Tests/Asun.Modules.Qualification.Core.Tests.csproj -c Release -- suite qualification-core
```

Q01～Q20 复用正文向量，Q21 覆盖 Golden canonical hash、跨机 PairId 外连接/LoA 退化、Root 晚到租约和移交 Unknown、UI Epoch/UnbindPending、阈值与不支持区间。每个 Benchmark case 同时记录计划 N、成功/失败/取消/排空分母、模块 `Accepted→ResourcesReleased` end-to-end、probe `ready→actualCompletion` 及资源峰值；分位和失败口径引用 DEV-GOV-010 §3.1，不在此重复定义。Deming桥的QDEM-01..08/双Host在A.3.1.1另一个明确的桥接验证消费者（未来Statistics.Tests Exe），不改变本Core.Tests只有Core+BCL的依赖；没有上游实际运行能力时该suite不得声称通过。

新增Benchmark两Host可用同一Core.Tests Exe的 `host benchmark-execute` / `host benchmark-recorded` 分别运行，每次新进程与独立Owner；Host helper不是两个新测试工程。`suite qualification-core`在接收新切片后调用QBEN-01..08有限断言，`host`模式也要核所述结果/计数/Root排空后才0，不能只看业务Completed。以上命令和工程尚未创建或运行，不能标记通过。

### A.7 全范围文档准备结论与准入状态

2026-10-12本会话按当前独立模块架构和用户批准范围完成全范围设计收口。结论：**当前没有需要后续开发者补猜的软件设计欠账；本模块全部批准范围已达到可直接照文实施的指导准备状态。** 这不等于代码、编译、运行、性能、真实后端或生产资格通过，也不降低DEV-GOV-010门禁。

| 已批准范围 | 关键章节/唯一Owner | 当前文档结论 | 未关闭门 |
|---|---|---|---|
| Core请求、身份、生命周期、取消/恢复、Root/Owner | §1–5、§8–9、§12、A.1–A.3.2 | 输入/单位/状态/错误/线程/预算/原Task/租约/有限cleanup/转交已定；Study与Replay为独立消费者 | Core实现、编译、契约/并发/恢复运行 |
| MSA/Study与统计路线桥 | §6、§A.3.1、A.3.4 | Bias/Linearity/Stability/GRR/Uncertainty/Bland–Altman的模型前提、statistics调用映射、结果与异常边界已定；数值算法Owner为statistics | Statistics adapter编译、能力、真实样本/计量资格 |
| ConstantRatioDeming S7 | §6.4、A.3.1.1、A.3.1.1.1 | 单family、原/转换单位平方比、双侧来源/覆盖、无环身份、ScaledValue、诊断、两Host与cleanup均已定并限定接收 | 实际Adapter/Capabilities、S7运行、数值与客户物理资格 |
| Golden/Replay | §3.4、§7.1、A.3.4、A.5.5 | 全案例外连接、失败分母、来源角色、Replay封存结果和权限/恢复边界已定；比较器Owner为replay | Replay adapter/codec实际接线、运行与性能 |
| Benchmark执行/Recorded分析 | §3.4、§7.2、A.3.3、A.5.2、A.3.4 | Profile/WorkPlan/Recorded、完成屏障、资源归因、分位/删失、两Host和恢复闭包已定 | Probe/Sampler/clock真实适配、负载实测、目标判定 |
| 完整QualificationReport与耐久归档 | §5.1、A.5.4–A.5.6 | QLQS/QLRP/QLAR/QLRF/QLRE、严格读回、格式注册、IM-066 append/exact/validate、receipt/fence/Unknown/重启恢复和治理消费位置已定 | DLL/SQL/Format注册、权限/对象引用、真实耐久/断电恢复 |
| Reference/Snapshot/资源适配 | A.3.4 | 公共工厂、有限读取、封口、Source/Use证据、Process sampler/clock和租约归还已定 | 实际来源、存储权限、性能运行 |
| WPF可选控件与双STA Host | §11、A.4、A.3.4 | DevExpress25.2.3组合、布局、键盘、三语、Epoch/权限、EvidenceNavigator接线、Unbind/晚到已定；qualification不直接消费viewport Assembly v0.2，故viewport §10.6–10.9不适用 | WPF/ UIA/DPI/1920×1080真实运行；实际程序集接线 |
| HALCON/AsunImage | §10 | qualification无自身视觉算法/图像算子；量测/探针经原Owner端口注入，故无需在本模块再选HALCON算子 | 依赖模块/真实视觉Owner的公开签名与运行资格 |
| 自动参数/推荐与生产放行 | §1、§3.3、§6.5、§13 | qualification只消费调用方冻结的Method/Policy/AcceptanceCriteria，禁止自动改阈值、重采、重跑到通过、发布Golden或升级用途；该能力不属于本模块批准职责 | 算法/工艺/授权Owner另行决定；不阻断本模块纯Core/报告消费 |
| 第二消费者 | §13、A.5.5、A.5.6 | Study、Golden、Benchmark及ai-dataset-governance完整报告消费位置与独立断言已冻结；不复制判定/统计/报告schema | 各消费者实现与运行 |

剩余项均是实现、真实依赖、部署或外部事实Owner，而不是本指导内部设计决定：

- `qualification` Owner：Core/optional adapter/WPF工程创建、公开签名编译、codec/strict reader、Root/取消/租约/双Host和耐久测试。
- `statistics` Owner：Bias/Linearity/GRR/Uncertainty/Bland–Altman及S7实际Capabilities、后端和数值资格；qualification不复制算法。
- `replay` Owner：比较器、封存案例/运行来源、Report/Input/Output权限与实际Replay运行。
- `storage-database` Owner/部署：IM-066 Catalog/SQL/Format注册、scope/权限、对象存储、技术receipt、备份与断电恢复。
- `ai-dataset-governance` Owner：只按A.5.6消费完整QLAR/QLRP和原receipt，治理自身训练/评价/用途规则保持其唯一指导。
- 产品/客户/计量Owner：物理独立性、证书信任、接受限、节拍、现场/HIL、质量放行与用途批准。

不适用范围保持：qualification不实现视觉算法、HALCON图像处理、设备命令、数据库连接池、Replay比较器、训练/推理、质量放行或生产批准；X-Ray/CT、ICT、FCT及蚀刻后光板项目仍按平台入口暂缓。

本轮全范围有限自审与文档验证：复用已接收Core/Study/Replay/Benchmark/S7向量，不重算旧请求或两份4175/4172-byte S7请求；新增检查沿“空Root→Adapter Factory→原Task/lease→完整Report/Archive→IM-066原技术receipt→精确读回/Unknown恢复→训练治理只读消费”闭环，核对所有新增公开record构造位置、A.5.4–A.5.6域闭包、hash不回写、严格EOF/排序/null/版本拒绝和append/exact/validate三命令身份。核对DevExpress 25.2.3本机XML中DockLayoutManager/LayoutGroup/LayoutPanel/TabbedGroup、GridControl/TableView、ChartControl/XYDiagram2D/PointSeries2D/LineSeries2D、PropertyGridControl.SelectedObject、SuperTip/SuperTipItem存在；Grid ItemsSource/SelectedItem未以错误XML成员名冒充公共文档，使用现有WPF binding语义待目标程序集编译确认。全部示例围栏/括号、UTF-8无BOM/CRLF、唯一写入路径检查通过；未创建/编译/运行任何工程，未执行真实Codec/IM-066、WPF/UIA、HALCON、statistics、性能、耐久或现场验收。

2026-10-11主控回读§6.4/A.3.1.1/A.5.3/A.7，含逐字段单位比、原来源与无环身份、双侧完整覆盖、无损ScaledValue、两Host及末尾Owner修正，限定接收ConstantRatioDeming桥的本轮确定指导内容。真实Adapter、实际发布能力与运行、数值资格仍为PreparationIncomplete；既有Core/Study/Replay/Benchmark的ModuleCoreImplementationReady保持，不扩大实现授权。新增两Host的4175/4172-byte S7请求是本会话作者按编码规范的内存重建证据，主控未独立重建，不记作主控复算通过；上游S7原件接收证据与本桥派生证据分别保留。

历史记录：0.2.5-prep仅补ConstantRatioDeming精确桥；已接收Core/Study/Replay/Benchmark状态保持，Module API仍为v0.2独立扩展。§6.4/A.3.1.1及tag6/tag5的受影响新增字段按本页冻结；原974/256及Benchmark新域/完整请求身份不变。2026-10-11主控已按DEV-GOV-010 §3.1六项接收下述Core与Benchmark软件切片为ModuleCoreImplementationReady（仅文档规格准备）；其它范围按限定内容接收或后续门分别记录，不提升整个模块为生产Ready。

| 六项条件 | 本页唯一定位 | 本轮文档落点/接收边界 |
|---|---|---|
| 1 职责/依赖/第二消费者 | §1–2、§13–14 | 无生产事实/放行/设备写入；Study与Replay独立消费者；Core与Benchmark受审范围已接收 |
| 2 唯一Module API/有效域/错误/Owner | §3–9、A.1–A.5 | DTO、数值桥、Root/迟到/转交、取消/排空、版本与canonical；已定统计路线/U1限定内容接收；Deming本轮桥规格接收边界见下表 |
| 3 无UI最小宿主及适配注入 | §4.1、§12、A.3.2 | 两个公开构造独立Exe、真实内容引用、有限Close和进程Owner；源码尚未创建，build/run属于后续实现验证 |
| 4 正常/边界/异常/并发/版本回退断言 | §8–9、§12–14、§16、A.4/A.6 | Q01–Q21、Unknown原查询、晚到、两轴、资源转交和权限撤销；均为待实施断言，不是已跑结果 |
| 5 BenchmarkProfile/测点/上限/分位/失败来源 | §3.4、§7.2、§9、A.3.1/A.3.2/A.3.3/A.6 | Core工程预算与测量方法已写；P50/P95/P99引用DEV-GOV-010唯一口径。缺客户目标只NotEvaluated；新增Profile/Recorded/解析/有限执行与两Host闭包见A.3.3/A.5.2，已由主控接收 |
| 6 唯一工程/允许禁止路径/最小顺序/后续门 | 顶部implementation binding、§2、§12、A.4/A.6 | Core/Core.Tests路径唯一，无产品/WPF/DB/设备依赖；可选控件代码落点另接收，不据示例创建工程 |

| 切片 | 当前状态 | 精确剩余条件 |
|---|---|---|
| Core请求校验/身份编码/生命周期、Study/Replay纯托管协调 | ModuleCoreImplementationReady（仅文档准备） | 六项规格已接收；真实Core/Core.Tests实现、构建、契约/并发/恢复运行验证尚未执行，不再列内部DTO/方法欠账；创建工程仍须后续明确实现授权 |
| statistics bridge（Bias/Linearity/GRR/Uncertainty/Bland–Altman） | 已明确支持路线桥限定内容接收 | A.3.1的v0.3逐字段映射、BCL输出明细与QLNI规格已接收；真实statistics/数值policy适配实现、运行、目标样本与数值支持域资格另验，属于实现/运行门，不是已定DTO/方法欠账 |
| ConstantRatioDeming附加数值桥 | 指导内容已接收；真实Adapter/能力与运行/数值资格仍PreparationIncomplete | 上游S7六项规格已接收；本页A.3.1.1冻结逐字段单family构造/ratio单位修正/无环身份/双侧覆盖/ScaledValue/完整诊断/两Host/QDEM断言。无内部DTO/方法待猜；实际Adapter工程/上游可运行Capabilities、实现运行及数值/目标样本资格另门，不用OLS替代 |
| Replay只读报告adapter | 纯托管协调纳入Core六项规格接收；真实adapter运行后续门 | Manifest/分母/hash/失败分类和独立Replay Host规格保持；真实上游Replay来源/报告解析接线与运行另验，不冒充比较器生产资格或列已定格式欠账 |
| Benchmark执行/录制分析软件切片 | ModuleCoreImplementationReady（仅文档准备） | A.3.3/A.5.2的Profile/Recorded/codec/关联校验、Clock/Probe/Sampler原Task与lease、有界Root双Host、全分母/删失/归因/NotEvaluated及QBEN-01..08六项规格已接收；真实Probe/Sampler/BCL适配实现与运行、资源/目标负载实测另验，不是内部格式欠账 |
| HALCON/AsunImage证据adapter | PreparationIncomplete，适配切片独立门 | §10固定26.05语义/既有公共消费证据；有歧义的目标C#重载只在消费项目公共签名/编译核对。不检查封装内部或依赖授权 |
| U1 WPF及双STA Host | 公开装配恢复指导限定内容接收；实现/运行PreparationIncomplete | §11/A.4的Bind/查询/原Task/Owner/权限/语言/有限关闭装配指导已接收；可选控件代码落点与实现授权、真实1920×1080 WPF/键盘/UIA/DPI和两STA运行另验，不是本轮已闭公开装配欠账 |
| 产品集成、物理/客户现场资格 | 后续外部门 | 平台合同采纳、真实样本/参考/用途/目标及对应Owner决定、性能/计量/HIL/现场证据仅阻依赖它的范围，不阻无副作用Core |

0.2.2-prep既有两轮有限自审结果保留：分别沿“输入→结果/异常/取消/排空”和“空宿主→公开构造/预算/Owner/迟到/转交/UI原查询”检查。实际定向核对：20个本地链接/2个fragment、11个代码围栏及C#片段括号、UTF-8无BOM/CRLF；从公开字段独立重建Replay五域并完整解码974-byte QLRQ，无尾随字节，hash相符；Study QLEP/QLIP实际内容hash不同；Fraction精确核对Q03交叉SS=128/32/8/8、Q06嵌套SS=128/32/8。以上仅文档向量和结构校验，不是运行产品Codec/数值后端。本轮0.2.3-prep两轮有限自审仅核A.3.3/A.5新增范围：第一轮检查Profile/录制闭包→排队/调用/失败→真完成/cleanup，修正采样预算、源QLRQ身份、phase及完整性；第二轮检查公开构造/端口能力/fixture lease与闩锁/原Task/双Host/输出身份，修正能力全引用、失败预算覆盖预热和清理一次性。实际新增校验：24处显式公开record构造参数数量一致，新声明无第二权威，QLBP/QLBW/QLBR及三份完整QLRQ逐字段独立解码到EOF、2071-byte记录附尾字节拒绝，四组分位与50/s吞吐手算一致；新增域hex长度/hash一致，旧974/256只核身份保留、未重做旧全审。主控接收证据独立记录：按公开字段构造QLBP402/QLBW444/QLBR2071 bytes，长度/hash一致，QLBP/QLBR完整hex逐byte一致；QLBR源请求身份按已登记BEN-ORIGIN引用，本次主控未声称独立重建全部三个新QLRQ。作者上轮三份QLRQ重建是上述作者有限检查，不冒充主控独立检查。旧974/256向量接收保持。

0.2.5-prep新增S7桥已完成两轮有限自审。第一轮沿原计划/Pair外连接/双侧状态与原来源→平方比与Center单位转换→QLDP/QLMS/QLNI单向身份→单S7 family/有效Policy与Budget→全覆盖/尺度矩/单项系数/两层诊断检查，明确缺页不派发、跨Pair重复件不冒独立、缺侧不重复计Gap、Source与Definition不同hash域；修正平方单位方向和task/result诊断分别无损保留。第二轮沿公开构造/实际能力否定→原acceptance/Run/Completion→CTS/迟到/查询/Dispose→Root单cleanup/独立engine→两Host非零失败检查，改用窄StatisticsEngine/EngineLimits别名，补全Host的来源/定义/9政策参数/13Budget/尺度计算断言，明确未派发输出不伪造上游运行身份；桥等待自身run释放，不等待Root.Close或engine Dispose，消除排空环。检查仅本轮桥新增范围，未重开旧Core/Benchmark或上游26项全审。

末尾主控定向意见已并入同一S7范围：Deming Host的清理同时核Drained/原Completion成功/完整Diagnostics；摘要记录失败独立捕获并返回完整两轴摘要，两个Main最终有限Observe与有条件Acknowledge，未知Root继续Owner强持。空资源holder先登记再构造engine/CTS，CTS拒绝提交仍有释放Owner；holder/engine原Dispose在bridge退出后由Root启动，保持无自等待环。此收口不变更数值映射/算法/上游26项或任何旧向量。

实际最小检查：新增Host的28处显式公开record构造参数数量一致，新DTO/桥声明单一、C#示例分隔符与围栏成对、statistics锚点存在、无宽using歧义；两Host各仅一次CalculateAsync.AsTask、一次Close且finally保留Owner/两轴结果。先前本轮内存typed writer已逐公开字段重建两Host的QLIP/QLMS/QLDP/QLNI及S7派生PairSequence/Task/Input/Request，QLDP另由逐字段reader完整消费EOF，长度/hash见A.5.3；此次定向核Fraction矩/尺度与90位Decimal固定正常oracle、换单位比例及Computation指数/归一化ratio一致。旧974-byte完整hex及Benchmark402/2071-byte完整hex的长度/hash复核一致，原256-byte与444-byte身份保持；旧Benchmark三份完整QLRQ保留原正文、不重算全请求。UTF-8无BOM/CRLF保持。这些是同会话作者文档结构/向量检查，不是主控独立接收、产品Codec/后端运行或数值资格证据。

当前切片规格状态以上表为准，整个模块仍为Prep；全范围内部设计已闭合，真实上游statistics/Probe/Sampler实现及运行、目标样本/数值资格、WPF/UIA、产品/现场门保留，它们不重开已接收内部DTO/方法。未创建或运行C#工程，未执行HALCON、WPF、性能、HIL、计量或现场验收。本轮新增桥确定指导内容已由主控限定接收；本会话仅同步该接收状态后结束，等待下一任务，不自动推进实现或修改共享台账。
