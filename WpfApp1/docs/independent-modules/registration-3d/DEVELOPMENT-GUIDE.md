# registration-3d：三维配准与位姿质量开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`托管Core切片`

- 模块 ID：`IM-033`
- 来源包：`PKG-060`
- 规划消费者：宿主编排下的多视角 3D 整合工具、独立 3D 比较/量测工具
- 文档版本：`0.3.1-prep`
- 状态：`DesignReview / Prep`
- 托管 Core 切片：`ModuleCoreImplementationReady`（2026-10-10 主控六项规格接收；不是实现或生产验收）
- Simulation-S1 切片：`ModuleCoreImplementationReady`（2026-10-11 主控六项文档规格接收；实际构建/运行及产品资格未验）
- 日期：2026-10-11
- 独立交付候选根：`src/Modules/registration-3d/`
- 测试候选根：`tests/Modules/registration-3d/`

本页是本模块的唯一接入指导。它把 PKG-060、DEV-VIS-028 和 FS-014 的职责、算法语义和工程边界收敛成一个可脱离本检测平台使用的模块设计。本文不宣称代码已实现、HALCON 已在目标运行时验证、Golden/Replay 已通过或达到生产计量资格。本模块 Core 契约唯一见附录 A；平台传输/数据库 Schema 映射和客户资格仍由相应权威采纳，不能据此另造模块 DTO。0.3.1-prep 在保持已接收托管 Core 和 Simulation-S1 范围不变的基础上，补充 [surface-data](../surface-data/DEVELOPMENT-GUIDE.md) 的 H/codec 消费桥以及 [viewport](../viewport/DEVELOPMENT-GUIDE.md) Assembly v0.2 的 WPF 组装边界；这些是消费约束，不转移上游 Owner，也不构成运行验收。Core ApiVersion=0.2.0、canonical既有v1及真实算法保持；Simulation自有ApiVersion=1.0.0，不冒充Core版本或HALCON后端。接收范围和未授通过的部分唯一见§19/B.2/C.6。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/registration-3d/Asun.Modules.Registration3D.Core/Asun.Modules.Registration3D.Core.csproj`；namespace：`Asun.Modules.Registration3D`。预定测试工程：`tests/Modules/registration-3d/Asun.Modules.Registration3D.Core.Tests/Asun.Modules.Registration3D.Core.Tests.csproj`。上述项目尚未创建。
- 后续纯 Core 实现切片允许路径：上述 Core、唯一正式Core.Tests BCL Exe，以及独立消费者BclHost Exe `tests/Modules/registration-3d/Asun.Modules.Registration3D.BclHost/`；具体工程和命令见 A.4。本轮仅允许改本 DEVELOPMENT-GUIDE.md，不创建任何工程。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core、正式Core.Tests BCL Exe 与独立消费者BclHost Exe 作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 当前托管 Core 切片状态：`ModuleCoreImplementationReady`，DEV-GOV-010 §3.1 六项已由主控内容接收，仅规格准备。范围为值契约、输入/域/图校验、刚体组合/覆盖质量计算、identity/Receipt/发布用途纯校验、有界未测参数建议、注入端口下协调及受控测试Host；Core接收本身不授HALCON数值/Adapter、独立可发布Simulator、WPF、平台集成或现场准入。独立Simulation-S1的六项文档规格另于2026-10-11接收，实际构建/运行/发布未验；其余未接收切片仍为`PreparationIncomplete`。本轮不创建工程、不启动实现。
- Simulation-S1独立交付规格唯一见附录C：2026-10-11主控已接收为ModuleCoreImplementationReady，仅限独立纯托管脚本Simulator/factory/pack/Clock/有限资源与两个Synthetic Host。显式BackendOutcome不运行ICP，Calibration=null、仅RelativeDiagnostic/Publish拒绝；虚拟时间/真实观察、原Task/lease/timer和两层Close/root保持。唯一Simulation类库/Simulation.Tests及Simulation.Host工程，不修改已接收Core.Tests/BclHost引用边界；另获实现任务并绑定权威代码基线后才允许在C.5目录实现，本轮只同步本指导状态。

### IM-033 与重建模块的交接边界（宿主组合）

- `IM-033 registration-3d` 独占三维 registration transform 的估计、配准质量资格评估和不可变结果/Receipt 发布。只有通过本模块既定的 `InputQualityGate`、`AlgorithmQualityGate`、独立检查和可观测性门的结果，才能作为已资格化 registration transform 交给宿主；未通过的候选只能作为诊断证据，不能注入重建或整合流程。这里的“发布”只指本模块向宿主发布带 `CalculationIdentity`、输入 hash、Profile/运行时版本和质量证据的候选或已资格化 registration result，不等于质量放行、标定激活或设备命令。
- 本模块不得直接引用、调用或持有 `IM-032 reconstruction-3d` 的程序集、私有类型、状态、句柄或 Surface Store；不得以重建模块的内部对象作为隐含输入。Core、Adapter、Replay 和 UI 均通过本页定义的公共端口和宿主交接，不形成 `registration-3d → reconstruction-3d` 的编译或运行时依赖。
- 宿主/调用应用负责把 IM-033 的不可变已发布 registration result 与其已批准的 `CalibrationSnapshot`、坐标链和重建请求组合，再将完整、版本化、只读的 transform/calibration snapshot 注入需要它的模块。组合过程必须保留各自来源 hash、revision、frame/unit 和适用范围；IM-033 不替宿主写入或激活 calibration asset。
- `IM-032 reconstruction-3d` 只消费调用应用注入的不可变已发布 transform/calibration snapshot：不直接调用 IM-033，不重新估计 registration transform，不把单位阵或最近一次姿态当作缺失输入，也不对同一 registration transform 做第二次隐式应用。若 snapshot 缺失、过期、frame/unit/hash 不匹配或已应用标记不一致，宿主链应拒绝请求并保持 `Unknown/Blocked`，不得静默继续。
- IM-033 的输出必须明确“一次应用”语义：`p_target = T_target_source · p_source`，以及 transform 所对应的原始 source revision、target/public frame 和 calibration 适用范围。下游可组合不同领域的变换，但同一 registration transform 只能在宿主编排链中应用一次；本次计算不把应用后的重建结果再次应用同一变换或重复发布；合法的新原始 revision 可作为新 CalculationIdentity 的输入，不一概禁止后续配准。
- 因此，本模块的真实消费者是宿主编排/整合工具和独立 3D 比较/量测工具；重建模块是宿主注入 snapshot 后的下游消费方，不是本模块的直接依赖或直接调用方。

## 1. 目标与边界

### 1.1 模块负责什么

模块接收带来源快照的两个或多个三维表面，检查坐标、单位、有效域、初值、允许自由度和资源预算，按已批准的配准路线估计候选位姿，计算覆盖、残差、图连通、闭环和位姿可观测性，并返回不可变的候选结果与证据引用。模块只发布本次计算结果，不保存生产事实。

支持的能力：

- `Validate`：按 RequestKind 验证 Pair、Graph 或固定评价的输入、域、初值和预算。
- `RegisterPair`：在适用条件满足时执行 matching 或 ICP 路线，返回从原始 source frame 到 target frame 的位姿和质量。
- `RegisterGraph`：验证并优化带锚点的多模型图，返回每个原始 frame 到声明公共 frame 的变换。
- `EvaluateAlignment`：对固定变换重新计算双向覆盖、距离、残差和独立检查质量；不重新估计变换。
- `RequestCancelAsync` / `CloseAsync`：按 operation 请求取消、停止接收、排空并归还资源；`Query` 返回原 operation 的当前观察。
- `RecommendParameters`：离线产生有界参数建议，不改活动 Profile。
- `PublishTransform`：只把通过配准资格门的已完成结果封装为不可变 ReleasedTransformSnapshot，交宿主留存/注入；不提交生产事实。

### 1.2 明确禁止

模块不得拥有或决定以下事项：

- PCB、PCBA、SPI、AOI、点胶、涂覆或其它制程的目标关联、缺陷定义、工艺解释、公差、机判、质量放行、复判、返修和报表结论。
- 板件/工单身份、程序发布、标定激活、标定资产修改、设备触发、运动、光源、PLC、MES 或任何外部设备副作用。
- 参考面的物理资格（由 PKG-029）、最终被测量定义（由 PKG-030）、单表面采样/法向/拓扑（由 PKG-031）或已知变换数学（由 PKG-007）。
- 第二套 Surface Store、CoordinateGraph、事实提交事务、全局 singleton、隐藏窗口初始化或产品 ViewModel。
- 用单位阵代替缺失观测、用低残差覆盖自由度不足、用自配准吸收被测对象整体偏移/翘曲/尺寸误差，或把显示降采样当计量支撑。

调用方负责调用顺序、对象和目标关联、配方/方法 Profile、宿主组合与 snapshot 注入、业务适用性、质量事实提交和设备安全。未知、无效、不可适用或未达资格的结果必须保持原状态。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Registration3D.Core` 与 `Asun.Modules.Registration3D.Halcon` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Modules.Registration3D.Wpf`（可选控件）可引用 WPF/DevExpress，且 Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。§附录C 中的纯托管 Simulator 已是这条门禁的天然验证面。

**Blazor/Web 宿主中的配准结果展示**：Web 端需要"展示位姿候选、覆盖率、残差分布、图连通与闭环"时，服务端调用 Core 取得不可变配准结果，再投影到浏览器。约束：
- 浏览器端只渲染标记与数值，不重新估计位姿、不自行做 ICP 迭代、不修改 CalculationIdentity
- §1.2 的"不用低残差覆盖自由度不足"在 Web 投影中同样成立：前端不得把覆盖率低的候选显示为可用
- `RelativeDiagnostic`（无标定资产时的唯一允许输出）和 `Qualified` 必须在 Web 投影中视觉可区分

**AI 推理 Tiling 适配**：本模块的已发布不可变变换快照（`ReleasedTransformSnapshot`）是 `reconstruction-3d` 融合多视角的输入，不参与 AI 推理分块编排。适配约束：
- 本模块不实现 `RequestTileAsync`，不持有推理 tile 租约
- 三态仲裁（`ai-inference` §1A）对多视角融合结果的判定，不覆写本模块已发布的位姿事实；仲裁只作观察层

**HALCON 备选交叉验证适用性（配准链）**：本模块是 3D 视觉链中双跑 CI 的**位姿估计落点**，也是最容易"两路都收敛、但收敛到不同局部最优"的一环。约束：
- `register_object_model_3d_pair`（matching/ICP 两路线）与一条纯托管参照路线在**同一 Golden 数据集**双跑：最终变换矩阵（允许容差内不同）、覆盖率、内点 RMSE、图连通与闭环标志逐项比对，差值超容差即 CI 失败
- **已知的必然差异，不得抹平**：
  - ICP 收敛对初值极敏感；初值扰动 ≥ 1mm 时两路可能收敛到不同局部最优，这不是实现 Bug，是 ICP 本质特性；双跑门禁只对**同一冻结初值**下两路结果的差异设容差，不对不同初值的结果设门禁
  - `register_object_model_3d_global` 的全局优化含 TBB 并行随机采样（见 §7.7 已核对语义）；多次运行可能给不同结果，托管参照只能做确定性对照；双跑须固定随机种子，否则不可比
  - `register_object_model_3d_pair` matching 路线的 `default_parameters` 已核 HALCON 26.05 资料（`accurate` 为默认，见 §7.4）；托管参照须按相同语义固定参数，不得猜测 HALCON 内部默认值
- **Open3D oracle 在本模块的定位**：固定 commit `b6c5e196384ad71e75b6e6f9c5da22d046221f1d` 的 `Registration.cpp` 的 `EvaluateRegistration`/`RegistrationICP`/`RegistrationRANSACBasedOnCorrespondence` 与 `TransformationEstimation.cpp` 的 `Point2Point`/`Point2Plane`（见 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md) 与 §附录B），是**配准质量指标语义的独立参照**：
  - `fitness_` 定义（源码第 101 行）= `correspondence_set_.size() / source.points_.size()`；即**对应内点数/源点总数**——比值，有方向性（source/target 互换结果不同）
  - `inlier_rmse_` 定义（源码第 102 行）= `sqrt(error2 / corres_number)`——对应点对距离平方和的均方根
  - 空对应集时两者均为 0（源码第 97-98 行），不是 NaN 或无穷大
  - **Open3D 测试全为 DISABLED/NotImplemented**（见 `cpp/tests/pipelines/registration/Registration.cpp`），不能当测试覆盖证据
  - 这些定义用于确认"覆盖率与 RMSE 的计算口径"，HALCON 的对应字段需在实际运行时验证是否与此一致，不得假定等价
- 实际读取 SHA-256（LF 归一化）：`Registration.cpp`=`456dac720f38c0903d275c4d6ec7eb07e9cc73595dd55d9181cd4dc3f43b9f06`；`TransformationEstimation.cpp`=`f45814c59aeaa2d32d1d4866d4cb10a1dfa060119aef1247bac61fcf9b763f15`；测试文件 `tests/pipelines/registration/Registration.cpp`=`5b9112a01d16aae2c617dd7bff97a6567025fbf8a9d56c6befde5b213ac2848d`
- HALCON 仍是生产路线；Open3D 仅作交叉验证语义参照与降级保险，不作发布依据，不引入生产依赖

## 2. 独立架构与依赖

```text
多视角整合宿主 / 独立 3D 比较量测宿主
                 │ RegistrationRequest / OperationView
                 ▼
Registration3D Core（BCL；校验、质量门、生命周期）
       │ ISurfaceReadPort        │ IRegistrationBackend
       ▼                        ▼
宿主只读 Surface 适配       Halcon 可选适配包 → ImageLibDotNet.cv2
（frame/域/法向/采样来源）      或 BCL Host 的 ScriptedBackend
```


`reconstruction-3d` 不出现在本模块的依赖图中。若宿主流程需要把配准结果交给重建流程，必须由宿主读取 IM-033 的不可变 Receipt，与自身的 calibration/coordinate snapshot 组合后再注入；Core 不反向调用重建，也不读取重建内部状态。

必需依赖是稳定的公共契约和适配端口，不是对其它模块私有类型的编译依赖。模块 Core 不引用 WPF、DevExpress、数据库、设备 SDK 或产品页面。AsunImage 适配器可作为可选包发布；没有适配器时仍可用纯验证、Replay 和经批准的其它后端适配器运行。

推荐分层：

| 层 | 职责 | 禁止 |
|---|---|---|
| `Registration3D.Contracts` | 附录 A 请求/响应、单位、错误/状态、版本和 EvidenceRef；与 Core 同工程 | 供应商句柄、产品表、生产判定 |
| `Registration3D.Core` | 输入验证、路由、矩阵组合、质量门、取消和结果组装 | 直接调用 HALCON、UI、持久化 |
| `Registration3D.Adapters` | 将只读 Surface 与 HALCON 26.05 经 cv2 映射到 Core 端口 | 猜测 API、改变坐标语义、隐式重试 |
| `Registration3D.UI`（可选） | 结果投影和命令转发 | 修改事实、保存句柄、持有权限 |

## 3. 术语与坐标约定

- 所有点使用列向量：`p_target = T_target_source · p_source`。
- 变换名称的下标为“目标坐标系_源坐标系”。`T_B_A` 表示 A 到 B。
- 连用遵循 `T_C_A = T_C_B · T_B_A`；先作用的矩阵在右侧。
- Pair 的最终变换必须从**原始 source frame**出发。若先应用初值 `T0`，native 返回增量 `Δ`，最终变换为 `T = Δ · T0`，不得漏乘、反序或重复套用。
- Global 输出的每个节点变换必须从该节点原始 frame 到声明的公共 frame；`from`/`to` 的 native 语义必须由适配器固定并用非交换样例验证。
- 所有坐标必须声明长度单位（首选 `m` 或 `mm`，由 Surface 快照绑定），角度内部统一为 `rad`，显示可转换为 `deg`。跨单位转换必须显式记录一次；缺单位、混单位或尺度不明直接阻断。
- 变换质量检查至少包含有限性、正交性、`det(R)>0`、尺度为 1、位移/转角是否在调用方 Profile 允许域内。具体门值来自版本化 Profile，不在模块代码中硬编码。

## 4. 输入契约与快照

附录 A 为唯一 Core 形状。本节解释字段语义，不另定义候选 DTO。输入是 `RegistrationRequest`：显式 Kind、CalculationIdentity、冻结的节点/边/假设、已知变换、Profile、预算、Snapshot 和 RuntimeManifest。所有 public collections 使用 ImmutableArray，接纳时再复制或验证不可变来源；不能把 IReadOnlyList 的外部可变 backing array 当冻结快照。

### 4.1 不可变输入快照

`SurfaceRef` 同时绑定 SurfaceId/revision/hash、FrameRef、LengthUnit、有效点数和来源证据。数据经 `ISurfaceReadPort.AcquireAsync` 获取只读 `ISurfaceLease`；GetChunkAsync 返回带原索引的有限点批次，不能使用 latest。定位、留出、被测、排除、halo 角色按原始 source index 映射并分别计数。Graph 节点通过宿主公开契约输入，不读取其它模块状态；CoordinatePort/EvidencePort 是宿主组合角色，不是未定义的 Core 服务。

### 4.2 支持选择

每个 GraphNode.Domains 用 SurfaceDomainRef 声明五种互斥角色：`RegistrationSupport`、`IndependentCheck`、`MeasuredTarget`、`Excluded`、`HaloOnly`。定位支撑和被测目标不得重叠，独立检查域在求解前冻结，不能用求解后残差选择。缺少有效分母、域外预测、孔洞跨接或原索引映射时，对应质量门失败。

### 4.3 图输入

图请求额外包含：节点 `NodeId`、节点 SurfaceRef、边 `EdgeId`、`FromNode`、`ToNode`、初值/来源、允许方法、锚点节点及公共 frame。节点通过 SurfaceRef、边通过 Observation 绑定 revision/hash；剔除边后必须重新验证连通、锚点和必需节点，不能删失败节点后把剩余子图称为整图结果。

## 5. 参数、单位与必填边界

字段唯一见 A.1，不能依据旧名称另造 Length、Angle 或 Profile 类型。请求中的物理长度用全部 Nodes 统一的 LengthUnit（Metre/Millimetre）；角度 rad。仅 NativePairParameters 的 AbsoluteCorrespondenceMetres、SamplingStepMetres 使用 m，适配时转换一次。TimeSpan 是 BCL 时间类型；计数/预算用 int/long，按 A.1 显式校验，不设隐式转换或经验默认。

| 契约字段 | 固定语义与缺失处理 |
|---|---|
| Kind / Pair.Method | Pair=Matching/Icp，Evaluate=KnownTransform，Graph=Global；固定变换 Pair 请求亦可用 KnownTransform、Pair=null。不换隐含路线 |
| Model / DegreesOfFreedom | Rigid；估计必须 Full6，固定评价只检查声明的变换，不执行受限拟合 |
| Pair.Levels | matching 一层，ICP coarse/fine 两层；每层显式 preset、relative sampling、key fraction、steps、skip、abs correspondence、采样物理步长、normal invert |
| Global | preset Fast/Accurate、relative sampling、skip、iterations 显式；Robust 不适用 Global |
| QualityProfile | 双向覆盖、support/holdout 全域 RMS/Max、距离方式、秩/条件、跳变/允许范围、闭环/歧义、最少对应点；有来源的 AssetRef，不从 native default 补生产门 |
| Hypotheses | 支撑域、初值、身份来源与唯一点对应；列表冻结并纳入 hash；MaxCandidates 覆盖全部假设 |
| Budget | 输入点、工作集（含序列化）、句柄、节点/边/候选、并发/队列、RunTimeout/DrainTimeout；必填且不超过 RuntimePolicy.Ceiling |
| RuntimePolicy | 部署实例级并发/队列、结果保留数/时长与精确 API 版本；与请求预算分开，不动态改活动调度 |

Pair rel_sampling_distance 是对象直径比例（0<x<1），不等同物理采样步长；Pair refinement 与 Global iterations 分别映射不同 native 参数。资格距离固定 MaxDistance=0，不能把非零截断当质量门。合法范围、空值语义及字段组合以 A.1 为准；手册默认仅作研究事实。

## 6. 输出契约与发布 Owner

输出唯一为附录 A 的 `OperationView` 和 `RegistrationResult`；结果含冻结的请求、候选/节点/边、质量证据、停止原因、资源观察和 Issue。`Completed` 只表示计算成功；Qualification 为 RelativeDiagnostic、Qualified 或 NotEvaluated，不能用状态代替资格。缺失的 covariance、迭代数、条件数、signed distance 用 null/NotEvaluated，禁止填零。

IM-033 拥有 registration transform 的计算、配准资格和发布语义；宿主拥有 ReleasedTransformSnapshot 的存储、引用注入和业务采纳；标定资产 Owner 保持 calibration 发布/激活权，本模块只引用其 immutable AssetRef。公开快照绑定 TransformId、CalculationIdentity、源/目标 frame、源 revision/hash、Profile/Manifest hash、校验域和 CalibrationRef（诊断结果可空；ReleasedTransformSnapshot 必须有适用资产）。Qualified 的使用范围写在快照中，不获得任何工艺放行权。

Pair 原生 score 是重叠与非重叠部分的比率，Global Scores 是各模型充分重叠邻居数；都不是概率或本模块双向覆盖。NativeMetric 分开记录 Kind/Value，不与覆盖或置信度混用。Pair 一次 native 调用只返回一个 pose；Candidates 是显式假设/支撑分支的汇总，不能宣称 native 已枚举所有解。

`PublishTransform` 对已完成、资源已归还、质量门完整且 Qualification=Qualified 的结果作纯封装；失败、歧义、RelativeDiagnostic、stale 或 Unknown 拒绝发布消费快照。TransformId 按 A.2 冻结的发布预像生成；相同已完成结果和校准引用产生同一身份，冲突内容拒绝；没有新的 Store、自动激活或 DB 提交。宿主注入时同时传 ApplicationLedger（TransformId、NodeId、SourceHash、TargetFrame、ApplicationCount）；ValidateUse 对已有计数≥1 返回 AlreadyApplied；该纯校验不写账本，宿主必须在同一注入事务中串行/CAS 校验并增加计数，防止两个调用同时通过。显示叠加使用原始点临时映射，不写回 Surface；KnownTransform 固定评估可重复计算距离，但不改变账本或应用次数。

## 7. 处理路线与质量门

### 7.1 统一流程

1. 创建新的 `CalculationIdentity`，冻结请求和所有输入 revision/hash；建立只读租约。
2. `InputQualityGate`：验证点/面/法向来源、有限性、单位、坐标链、域角色、版本和资源上限。
3. 通过 PKG-031 公开端口取得声明采样/法向，保留原索引、实际有效分母和派生方法；不得把显示 LOD 当定位或计量输入。
4. 根据 Kind / Pair.Method 选择唯一已批准路线。若初值、连通性或适用域不满足，返回 Blocked/Rejected 及附录 A 错误键，不新增未定义的 NotApplicable 分类，不切换隐含路线。
5. 执行 pair 或 global；所有 native 句柄、临时模型和矩阵归本次计算租约，异常/取消/超时均进入统一排空。
6. `AlgorithmQualityGate`：检查变换方向、有限性、刚体约束、残差、覆盖、独立检查、候选歧义和停止原因。
7. Global 重新核全图连通、锚点、边质量、闭环和必需节点；剔边后重新核，不静默删节点。
8. 固定最终变换，在原始有效支撑及独立检查域重新求值；`EvaluateAlignment` 不改变变换。
9. `BusinessApplicabilityGate` 只输出给调用方检查，不由模块替代工艺/产品资格；返回不可变结果和证据。
10. 计算完成且 native、回调都已真实退出后归还工作资源与输入租约；发布 `Completed` 或明确失败终态。

### 7.2 路线判定

| 路线 | 允许条件 | 明确拒绝 |
|---|---|---|
| Pair `Matching` | 任务允许无外部初值，目标 HALCON 路线明确；候选和歧义可观测 | 将单位阵当作观测、用结果吸收被测缺陷 |
| Pair `Icp` | 已有足够近的共同坐标初值，支撑和独立域已冻结 | 把 ICP 当全局搜索、初值无效、重叠不足 |
| Global | 节点/边/锚点有版本来源，图连通，`from/to` 语义已适配 | 图分裂、必需节点缺失、剔边后未复核 |
| KnownTransform | 调用方已拥有经批准的变换，只执行矩阵/质量检查 | 从点云重新估计、把已知变换伪装成配准成功 |

Fallback 只能是已登记的 Pairwise/KnownTransform 路线，并且必须说明为什么图和任务语义允许；不能用 fallback 隐藏 global 残差失败，也不能降低质量门。

### 7.2.1 标定板是否必需及 3D 坐标资格

3D 配准的算法输入是带坐标、单位和有效域的 Surface；因此 **纯粹把两份已有 Surface 对齐，不强制标定板**。若 `KnownTransform` 来自已经资格化的传感器/设备外参，可直接使用；若 `Matching/ICP` 只在重叠表面上估计相对刚体变换，可输出相对坐标诊断，但不能据此声称毫米级绝对坐标或量测资格。

当消费者需要把 3D 点云绑定到相机、运动平台、设备坐标或有证物理长度时，必须有对应的标定/标准件链及适用资格。参考物应由标定方法决定：结构光/面结构光使用有已知几何尺寸和表面特性的 3D 标准件或平面/阶梯靶；手眼使用固定于工具/设备坐标且几何已知的靶，采集多组可观测姿态；相机内参可用带证书的平面标定板。普通 2D 棋盘格只提供平面角点，不自动校准 Z 尺度、深度偏置、结构光三角测量或手眼链；HALCON 的 `calibrate_sheet_of_light`、`calibrate_hand_eye` 和 `calibrate_cameras` 是不同物理模型，资产不得跨模型替用。

板型、证书/几何修订、相机/传感器/镜头/投影器、安装、工作距离、温度和采样 Profile 均须进入 `CalibrationAssetRef` 的适用性解析。标定板不必出现在生产 Surface 中；若无适用资产，仅可进行 `RelativeDiagnostic`，结果应保留源 frame，禁用绝对长度、跨设备公共 frame 和计量用途。标定/标准件资产未知、失效或撤销时，不得降级为单位阵、ICP“补偿”或最近一次姿态。配准算法失败也不能回退成无标记变换；允许的 fallback 仅用于显式诊断的新 CalculationIdentity，并保留主路线失败证据。

### 7.3 关键反例

- 单平面点面数据低 RMS：返回自由度不足/不可观测，不因数值小而通过。
- 周期阵列多解：保留候选和歧义，不按第一项直接采纳。
- A-B 与 C-D 两个连通分量：返回图分裂，不删掉一个分量后报告整图完成。
- 整体抬高 `0.2 mm` 的对象：独立基准检查仍能看到偏差，不允许自配准归零。
- `MaxDistance=0.1 mm`：只表示截断/关注范围；不得把结果最大值写成 `0.1 mm`。

### 7.4 场景驱动复审执行卡

以下执行卡是实现和审核的最小闭环。每个场景都必须能从输入快照和 Profile 重现，不得依赖开发者口头补充。`输出`只表示本模块结果；业务放行、设备动作和量测结论仍由调用方负责。

**正常配置与正常执行**

- **输入**：两个或多个已冻结的 Surface Snapshot，frame、unit、revision、hash、支撑域、独立检查域和方法均有效；图场景有锚点和连通路径。
- **参数来源**：调用方传入已批准的 `Recipe/MethodPolicy/Qualification/PerformanceProfile`；路线、自由度、采样、质量门和预算没有隐含默认值。
- **处理顺序**：创建 CalculationIdentity → 校验快照和资源预算 → 建立只读租约 → 按唯一方法调用 native → 独立质量评估 → 固定变换复核 → native 排空 → 发布结果。
- **输出**：不可变候选、刚体变换方向、原生指标及 MetricKind、覆盖分母、残差、可观测性、EvidenceRef 和运行时清单。
- **状态/错误**：成功为 `Completed`；质量未达门为 `Rejected/ResidualAboveGate` 或对应明确原因，不把候选改写成业务 PASS。
- **恢复动作**：调用方可依据证据提交后续流程；若输入或 Profile 改变，必须创建新的 CalculationIdentity。
- **可判定验收断言**：同一输入 hash、Profile hash 和运行时 manifest 重放时，变换方向、状态和证据字段完整且没有隐式单位阵或缺失分母。

**空输入**

- **输入**：空模型、空节点列表、零有效点、只含 NaN/Infinity 的点或空图。
- **参数来源**：仍要求完整 Profile；不以 Profile 默认值填补缺失输入。
- **处理顺序**：在 native 调用前检查对象数量、有效点数、拓扑/法向引用和图最小规模，立即停止。
- **输出**：无候选、无变换；返回输入诊断和缺失字段的 EvidenceRef。
- **状态/错误**：`Invalid/REG3D-001 InvalidInput`；不得进入 `Running`。
- **恢复动作**：调用方提供新的合法 Snapshot；不重试同一 CalculationIdentity。
- **可判定验收断言**：空输入不会创建 native 工作句柄，也不会产生 `Completed`、单位阵或零残差结果。

**多模型部分成功**

- **输入**：Global 图中部分边可配准，至少一个必需节点无充分重叠、失败或缺少合法路径。
- **参数来源**：Global 的关系模式、锚点、边允许方法、邻居/重叠门和是否允许局部诊断由同一 Profile 绑定。
- **处理顺序**：先验证全图 → 执行登记 → 逐节点/逐边收集质量 → 重新计算剔边后的连通性和锚点可达性，不静默删除失败节点。
- **输出**：保留成功边的诊断候选，同时标记失败节点/边、缺失路径和整图结论；不输出可冒充整图公共 frame 的完整结果。
- **状态/错误**：必需节点失败为 `Rejected/DisconnectedGraph/InsufficientSupport`；仅非必需边失败时，局部结果也必须带整图未完成标志。
- **恢复动作**：补采样或补约束后以新 revision 重算；fallback 仅在图语义和 Profile 已批准且明确标记整图失败时执行。
- **可判定验收断言**：删除任一失败节点后，结果仍不能声明原请求的全图成功；节点、边和错误均可按原 ID 对齐。

**歧义解**

- **输入**：周期纹理、重复结构或多个候选分数接近的 Pair/Global 输入，并带足够的候选上限。
- **参数来源**：`MaxCandidates`、歧义阈值、排序规则和人工复核策略来自 Profile；不得按第一项数组元素采纳。
- **处理顺序**：保留所有满足基础门的候选 → 计算候选间差异和独立检查 → 应用已批准的唯一性规则 → 无法唯一时停止采纳。
- **输出**：候选排名、歧义组、每个候选的变换和证据；不写唯一“最佳”事实。
- **状态/错误**：`Rejected/REG3D-008 AmbiguousSolution`，除非 Profile 规定的唯一性门明确通过。
- **恢复动作**：调用方增加独立支撑、限制搜索域或人工选择后创建新 CalculationIdentity；不得调低歧义门。
- **可判定验收断言**：存在两个未能按规则区分的候选时，结果必为歧义，不会因低 RMS 或数组顺序变成唯一解。

**错误 frame、unit、hash 或版本**

- **输入**：源/目标 frame 不可达，长度或角度单位不一致，Snapshot/Manifest hash 不匹配，或 Contract/Surface 版本不支持。
- **参数来源**：CoordinatePort、Snapshot 元数据、Contract 版本和 Adapter capability manifest；禁止从数值或字段位置猜测兼容关系。
- **处理顺序**：先验证身份、版本、hash、单位和坐标链，再检查算法参数；任一项失败都不进入 native。
- **输出**：逐字段不一致诊断，包含期望/实际版本或 hash 的引用；无候选。
- **状态/错误**：分别使用 `FrameMismatch`、`UnitMismatch`、`InvalidInput` 或 `UnsupportedCapability`。
- **恢复动作**：重新绑定同一合法 revision，或显式运行已验证迁移器生成新 Snapshot；不得原地改写旧快照。
- **可判定验收断言**：任何身份或单位不一致的请求不会创建 native 句柄，也不会以单位阵继续运行。

**超大点云、超大模型图**

- **输入**：点数、节点数、边数或估计工作集超过 Profile/宿主预算，或图规模超过适配器能力清单。
- **参数来源**：`MaxInputPoints`、`MaxWorkingBytes`、图规模上限和超时来自 PerformanceProfile；降采样策略来自调用方的 Surface 版本。
- **处理顺序**：在复制到 native 前估算峰值内存和句柄数 → 与预算比较 → 超限立即拒绝；只有调用方生成新快照后才可再次提交。
- **输出**：预算估算、实际计数、拒绝原因和输入缩减建议；不产生部分变换。
- **状态/错误**：`Blocked/REG3D-012 ResourceLimit`。
- **恢复动作**：调用方按批准采样版本减少输入或拆分任务并生成新 revision；不得模块内偷偷降采样或扩大预算。
- **可判定验收断言**：超预算请求在 native 调用前被拒绝，内存峰值和句柄计数不会越过声明上限。

**高并发、队列满、背压**

- **输入**：并发请求超过 `MaxConcurrency`，或有界队列达到容量；请求带独立 CalculationIdentity 和输入租约。
- **参数来源**：实例并发/队列由RuntimePolicy.Ceiling冻结；请求RunTimeout自Accepted起含排队时间，fixture显式单并发，无部署默认。
- **处理顺序**：先判断容量和取消状态 → 接受、拒绝或按约定背压 → 仅在获得租约后进入 native；不在无界队列等待。
- **输出**：每个请求有明确接收/拒绝/排队证据和队列时长；不得共享可变 ObjectModel3D 属性。
- **状态/错误**：队列满为 `ResourceLimit` 或宿主定义的显式背压状态；被取消的排队请求为 `Cancelled`。
- **恢复动作**：调用方退避、合并或稍后以新请求重试；不复制旧 CalculationIdentity。
- **可判定验收断言**：队列达到上限时内存和延迟仍受界定，任何请求都不会无限等待或覆盖其他请求结果。

**噪声、遮挡、离群点**

- **输入**：带噪声、局部遮挡、稀疏有效域或离群点的 Surface，保留原始有效分母和过滤来源。
- **参数来源**：matching 的默认参数、采样、关键点、refinement、距离门和离群处理均由 Profile 显式绑定；不得以经验值隐式替换。
- **处理顺序**：记录输入质量 → 按批准方法采样/准备 → 求解 → 分别计算重叠、残差和独立检查 → 评估可观测性。
- **输出**：覆盖分母、遮挡/离群诊断、残差分布、停止原因和候选；`distance_object_model_3d` 截断值标为截断，不写成真实最大偏差。
- **状态/错误**：支撑不足、残差超门或未收敛分别为 `InsufficientSupport`、`ResidualAboveGate`、`Diverged`。
- **恢复动作**：调用方改善采集、明确排除域或生成新采样 Snapshot；不自动放宽门、不自动从 ICP 换 matching。
- **可判定验收断言**：遮挡或离群导致有效分母不足时不报告通过；`MaxDistance>0` 的饱和值不会被当作真实最大偏差。

**单平面、共线或退化点集**

- **输入**：有效点全部近似共线、共面，或几何对某些自由度无约束；退化判定参数已随 Profile 固定。
- **参数来源**：允许自由度、条件数/秩门、法向和独立检查域来自 Profile 与 Surface 能力声明。
- **处理顺序**：native 前做几何可观测性预检；即使进入 native，也在结果阶段检查秩、条件和自由度覆盖。
- **输出**：可观测性谱和退化证据；不产生受限拟合变换；不把低 RMS 视为完整位姿。
- **状态/错误**：`Rejected/REG3D-007 InsufficientObservability` 或 `InsufficientSupport`。
- **恢复动作**：补充非退化支撑或选择 KnownTransform；不得以删掉自由度掩盖无约束求解；创建新 CalculationIdentity。
- **可判定验收断言**：单平面点面和共线点点在秩不足时拒绝；唯一非共线平面标记点点按六维谱判断，不因共面一概拒绝。

**法向缺失或反向**

- **输入**：法向未提供、法向数量与点数不一致、方向来源未知或整体反向。
- **参数来源**：法向是否必需、允许重算、`model_invert_normals` 是否允许以及法向质量门均由 Profile 和 PKG-031 来源决定。
- **处理顺序**：先核对法向来源/基数/有限性 → 需要时由批准的 Surface 端口生成新快照 → 再传入 native；不能在适配器中无记录改向。
- **输出**：法向状态、来源、是否反向处理和对结果的影响；无合法法向时返回不适用。
- **状态/错误**：`InvalidInput`、`UnsupportedCapability` 或 `InsufficientSupport`，取决于缺失是否可由已批准端口恢复。
- **恢复动作**：调用方补法向或重新生成快照；只有 Profile 明确允许时才使用 `model_invert_normals`，并保留开关在 CalculationIdentity 中。
- **可判定验收断言**：缺失/反向法向不会被静默当作正确法向；反向处理必须可追溯且不改变源快照。

**取消、超时、native 排空、迟到结果**

- **输入**：计算在校验、排队、native、质量评估或排空阶段收到取消或 deadline，可能随后收到 native 回调。
- **参数来源**：宿主 timeout、取消策略和 native 中断能力来自请求预算及 Adapter capability manifest。
- **处理顺序**：停止接收新工作 → 请求取消/中断 → 等待 native 确认退出 → 释放派生句柄和输入租约 → 发布终态；迟到回调按原 CalculationIdentity 关联。
- **输出**：`Cancelled`/`TimedOut` 及排空证据；native 未确认退出时不发布候选、不释放可能仍在使用的句柄。
- **状态/错误**：排空完成后为 `Cancelled` 或 `TimedOut`；已终态的回调为 `LateResult`，只进诊断。
- **恢复动作**：排空后允许新 CalculationIdentity；进程重启或回执丢失时标记 `Unknown`，由宿主查询原 operation。
- **可判定验收断言**：终态之后不会出现进度或结果覆盖；取消/超时请求不会把未知结果当成功或失败，也不会引发句柄并发释放。

**内存、点数、句柄资源上限**

- **输入**：接近或超过托管内存、native 工作集、点数、临时数组、句柄或序列化缓冲上限的请求。
- **参数来源**：资源预算、采样版本和适配器句柄上限来自 PerformanceProfile 与 RuntimeManifest。
- **处理顺序**：提交前估算 → 分配时计数 → 达到软/硬门时停止后续分配并进入统一排空；成功、失败、取消都执行同一释放路径。
- **输出**：资源峰值、当前计数、释放结果和触发门；不返回不完整的变换。
- **状态/错误**：`ResourceLimit` 或 `RecoverableError`；释放未确认保持非终态 `DrainUnknown`。
- **恢复动作**：重建适配器或减少输入后以新 revision 重算；不在同一 identity 上复用部分句柄。
- **可判定验收断言**：所有已确认终态的句柄和租约计数归零；未确认仍为 DrainUnknown，无终态，连续请求不会因泄漏逐步降低可用预算。

**持久化 Snapshot、CalculationIdentity、Receipt、Unknown**

- **输入**：不可变 Snapshot 引用、CalculationIdentity、运行时 manifest、Receipt/operation 标识和可能未回执的历史任务。
- **参数来源**：持久化 Schema、Receipt 版本和恢复策略由 State/Owner/Contract 权威定义；模块不读取 latest 猜测事实。
- **处理顺序**：先校验 Snapshot/hash/identity → 执行计算 → 在结果和证据完整后写 Receipt 引用 → 进程异常时保留未确认 operation。
- **输出**：可重放的输入引用、结果 Receipt、状态迁移和 EvidenceRef；未确认任务显式为 `Unknown`。
- **状态/错误**：Receipt 不完整为 `RecoverableError`；存活实例无法确认 native/回调/释放时为非终态 `DrainUnknown`；进程丢失为宿主观察 `Unknown`，不能映射 `Rejected` 或 `Completed`。
- **恢复动作**：按 Receipt 查询原 operation，或绑定同一合法 Snapshot 创建新 identity 重算；不覆盖旧 Receipt。
- **可判定验收断言**：重启后能区分已确认终态和 Unknown；相同 Snapshot/identity 不会生成两个互相覆盖的终态 Receipt。

**输入 revision 变化和 stale result**

- **输入**：计算期间或发布前，Surface/Coordinate/Recipe revision、hash 或对象身份发生变化。
- **参数来源**：Snapshot ReadPort 的租约和 revision 校验、调用方提交的 expected hash；不是按对象引用相等判断。
- **处理顺序**：开始时冻结 → native 前再次核对 → 发布前核对 → 任一变化即拒绝旧结果，不把新旧对象混合。
- **输出**：stale 诊断、旧 identity、冲突 revision/hash；无可用于当前 revision 的候选。
- **状态/错误**：`Rejected/InvalidInput`，可用 `StaleResult` 诊断码关联迟到结果语义。
- **恢复动作**：调用方生成新 Snapshot 后新建 CalculationIdentity；不原地改写旧证据。
- **可判定验收断言**：发布的结果引用的所有输入 revision/hash 与 CalculationIdentity 一致；变化期间产生的结果不会进入当前业务事实。

**升级、兼容矩阵、回退**

- **输入**：旧/新 Core、Adapter、HALCON 26.05 能力 manifest、Contract/Schema 和历史 Snapshot/Receipt 的版本组合。
- **参数来源**：发布包兼容矩阵、迁移器清单和回退版本；未列入矩阵即拒绝。
- **处理顺序**：加载前验证 major、能力和 hash → 必要时运行已验证迁移器生成新 Snapshot → 停止新任务并等待旧版本排空后切换。
- **输出**：兼容性诊断、迁移引用、版本化结果和回退指针；不改写旧结果。
- **状态/错误**：不兼容为 `Blocked/UnsupportedCapability`；回退期间未确认的 operation 为 `Unknown`。
- **恢复动作**：恢复上一已验证版本或使用明确迁移器；迁移失败保留原始快照和证据。
- **可判定验收断言**：改变变换方向、score 语义、单位、默认路线、质量门或事件顺序的版本不能以 minor 兼容读取；回退后旧版本不会读取未兼容新输入。

**无 UI 调用**

- **输入**：服务、Replay 或批处理宿主构造的 RegistrationRequest，不创建窗口、不依赖 Dispatcher。
- **参数来源**：调用方注入 Profile、SnapshotReadPort、RuntimeManifest 和 CancellationToken；所有字段与 UI 路径相同。
- **处理顺序**：调用 `Validate` → `Register*Async` → 接收进度/终态 → 由调用方处理结果。
- **输出**：与 UI 调用完全相同的不可变结果、事件和 EvidenceRef；不产生 UI 状态副本。
- **状态/错误**：按公共状态机返回；缺少宿主服务时为 `Blocked`，不是 NullReference 或隐式单例初始化。
- **恢复动作**：宿主处理错误码和重算边界；可在没有桌面会话时完成释放和审计。
- **可判定验收断言**：在无窗口、无 UI 线程和重复服务实例下，核心调用仍能完成校验、取消、排空和结果序列化。

**可选 UI 投影**

- **输入**：Core 的只读结果、进度、错误和候选证据；UI 不直接持有或修改 native 句柄。
- **参数来源**：页面权限、语言资源和 DevExpress 视图配置由宿主 UI 包提供；Core Profile 不因 UI 改变。
- **处理顺序**：UI 发出已校验命令 → Core 执行 → UI 订阅有序事件 → 显示影像/身份/状态/下一安全动作 → 终态后允许复核或导出。
- **输出**：可选的页面投影、诊断和人工复核动作；不产生新的业务事实或质量放行。
- **状态/错误**：UI 如遇断连显示 Core 的原状态；迟到事件按 CalculationIdentity 丢弃，不能覆盖当前任务。
- **恢复动作**：重连后重新查询 operation/Receipt；宿主决定是否新建计算，UI 不自动重试或改门。
- **可判定验收断言**：移除 UI 投影包后 Core 测试和无 UI 调用结果不变；1920×1080 下候选、状态、错误和恢复动作可见且无关键命令隐藏。

**第二消费者：3D 比较/量测工具**

- **输入**：冻结参考 Surface、被测 Surface、独立定位域、排除被测目标规则和调用方质量 Profile。
- **参数来源**：由量测工具提供定位/独立检查域和批准的 RegistrationProfile；公差、偏差、面积/体积计算不属于本模块。
- **处理顺序**：验证域不重叠 → 配准或应用 KnownTransform → 固定变换复核 → 返回质量证据 → 由 PKG-030 计算偏差。
- **输出**：变换、覆盖、残差、可观测性和 EvidenceRef；不输出尺寸偏差或量测结论。
- **状态/错误**：定位不足、目标混入支撑或 stale 输入按公共错误语义拒绝。
- **恢复动作**：工具补充基准或重新采样后新建 identity；不得把被测目标加入支撑以消除真实差异。
- **可判定验收断言**：同一 Core 结果可被比较工具消费，且模块不会因被测对象整体偏移而把后续真实差异归零。

**长期运行、泄漏、缓存失效、累计队列压力**

- **输入**：长时间连续请求、重复 Snapshot、缓存命中/失效、取消和异常交错，达到宿主运行周期要求。
- **参数来源**：v0.2 不跨 operation 缓存索引/模型；结果保留数/时长由RuntimePolicy，队列水位、周期和资源阈值来自显式PerformanceProfile。
- **处理顺序**：每次请求独立租约和identity → 同identity重提交只Query原operation → 新identity新工作模型 → 按RuntimePolicy淘汰已终态结果 → 定期采集资源/队列并排空。
- **输出**：按identity的结果、重复接纳/保留淘汰观察、资源曲线和泄漏诊断；结果留存不能隐藏新revision。
- **状态/错误**：累计压力触发显式 `ResourceLimit`/`RecoverableError`；存活实例释放不明为 `DrainUnknown`。
- **恢复动作**：按水位背压、只淘汰已终态结果；确认旧资源后重建适配器，并查询未确认operation；不清空正式 Receipt 或静默丢任务。
- **可判定验收断言**：长时运行后句柄/内存/队列不呈单调泄漏，新请求hash变化不重用原operation，队列压力可预测并可恢复。

### 7.5 算法参数、Global 模式与训练边界

#### Pair Matching

`register_object_model_3d_pair` 的 `default_parameters` 只能使用目标 HALCON 26.05 资料确认的 `fast`、`accurate`、`robust`，资料默认值为 `accurate`；本模块不把它升级成产品默认，实际选择必须由 Profile 绑定。`rel_sampling_distance` 是相对于对象直径的比例，不是长度单位，必须满足 `0 < x < 1`；手册中的 `0.03/0.05/0.07` 只是建议候选。`key_point_fraction` 是比例，手册建议 `0.2/0.3/0.4`，资料默认 `0.3`；`pose_ref_num_steps` 资料默认 `5`，建议候选 `5/7/10`；`pose_ref_sub_sampling` 资料默认 `2` 且必须 `>0`。`pose_ref_dist_threshold_rel` 相对于较大模型直径，`pose_ref_dist_threshold_abs` 使用绝对距离；二者的单位和是否同时启用由 Profile 明确。`model_invert_normals` 资料默认 `false`，只能在 Profile 明确允许小模型法向反向补偿时启用，并把开关写入 CalculationIdentity。

Matching 负责在允许无外部初值时产生候选；它仍受重叠、歧义、退化和独立检查门约束。任何建议值都必须在目标点云资格和 Golden/Replay 中验证后才可进入批准 Profile，不能直接从手册建议变成生产门。

#### Pair ICP

`icp` 只在已有足够近的共同坐标、支撑和独立检查域已冻结时使用。没有初值、严重遮挡/低重叠、退化自由度或坐标不一致时，验证阶段返回 `MissingInitialTransform`、`InsufficientSupport` 或 `InsufficientObservability`。适配器不得把 ICP 失败自动改为 matching；若调用方要换路线，必须显式创建新 CalculationIdentity、记录新 Profile 和路线选择。

#### Global

Global 请求必须明确下列三种关系模式之一：

- `global`：每个模型提供到公共 frame 的 12 项刚体矩阵，`to` 为空；统一适配时先转换为公共初值边，再以显式 from/to 调用并重锚；不让 native 搜索未声明边。
- `previous`：输入 N-1 个连续变换，表达相邻模型之间的初始关系；节点顺序、锚点和输出公共 frame 按 A.1 固定，展开显式边后调用。
- 显式 `from/to`：每条登记边声明方向，只优化已声明 Solve 边；所有必需节点必须存在从锚点到公共 frame 的路径。

三种模式的矩阵方向都按 `p_target = T_target_source · p_source` 解释，输出必须由 Core 重新表达并核对。显式边图若任意节点无路径、图分裂、锚点缺失或某模型无充分重叠，不能删除模型后报告整图成功。Global 失败后只有在图语义允许、调用方 Profile 已批准且结果显式标记为“整图失败后的诊断/替代路线”时，才可新建 identity 退回 Pairwise 或 KnownTransform；fallback 不得覆盖 Global 的失败、残差或连通性证据。

#### 训练不适用

本模块没有训练阶段。Pair/Global 只使用运行时 ObjectModel3D、已冻结的 Surface Snapshot 和参数，不产生或更新训练模型资产。`create_shape_model_3d`、模型训练、训练集管理和训练失败属于其它模块或调用方；若请求进入本模块，返回 `UnsupportedCapability`/边界外，并指向相应模块，不把“训练失败”伪装成本模块配准错误。

### 7.6 冻结的粗精路线、反例与质量公式

**模型边界。** 当前完整模块支持 SE(3) 刚体、固定 KnownTransform 和多视角刚体图。相似/尺度、affine、non-rigid、颜色配准、在线 SLAM 均不支持，返回 UnsupportedCapability；HALCON `vector_to_hom_mat3d` 虽支持其它 TransformationType，也不能用于吸收被测尺寸/形变。自由度子集不是把六自由度解的几项置零：本 HALCON pair/global 路线仅支持完整 6DOF 估计，非 6DOF 的估计请求预检拒绝；KnownTransform 可以按宿主声明检查受限自由度，但不估计。正文“允许子集”的含义仅是适用性检查，不能暗示 native 带约束优化。

| 功能/输入分支 | 主路线与固定顺序 | 比较候选及不采用理由 | 失败/恢复 |
|---|---|---|---|
| 无合法初值的 Pair | 几何支撑 ROI → 冻结 sampling step 的私有工作副本 → `register_object_model_3d_pair('matching')`（含 native refinement）→ 固定最终变换在原始域/留出域评价 | 不用 ICP 做全局搜索；不新增 create_surface_model 训练资产；Open3D RANSAC/FPFH 仅作为研究基准，未证明 HALCON 能力缺口，不新增运行依赖 | 无 pose/覆盖不足/歧义拒绝；不换路线 |
| 已冻结近似初值的 Pair | 私有源副本先应用 T0 → coarse `icp` 得 Δc → 原始 fine 源副本应用 Tc=Δc·T0 → fine `icp` 得 Δf → T=Δf·Tc → 原始域/留出域评价 | 只跑 full-resolution ICP 作为同样本基准；不能声称 coarse/fine 最快；matching 是新请求路线而非 retry | 每层检查非空/刚体/跳变/支撑；任何一层失败停止，不用上一层冒充最终 Qualified |
| 固定变换 | `EvaluateAlignment` 用原始未变换私有源 + Pose=T；反向用原始目标 + Pose=T⁻¹；只求质量 | 或已变换源+空 Pose 二选一；正式路线选前者，禁止两者并用 | 不调用 pair/global、不更新 T、不改应用账本 |
| 多视角 Graph | 校验节点、已知近似边与锚点 → 执行冻结 pair 边（仅请求明确的边/假设）→ 核连通/留出/独立闭环 → `register_object_model_3d_global` → 重锚 → 原始节点/边复核 | native global/previous 可探索额外邻居；本契约全部模式展开显式 from/to 限定图，不优化 CheckOnly。Open3D line-process 剔边思想可作诊断，不复制其优化器 | 必需节点/连接失败整图拒绝；保留边诊断，fallback 新 identity |
| 距离/对应证据 | points 或 triangles 由 Profile 指定 → 私有模型准备 → `distance_object_model_3d` 显式 `distance_to`、`method='kd-tree'`、`store_closest_index='true'`、`MaxDistance=0` → get params | linear 是小负载比较路线；voxel 近似、无法提供所需 closest-index，不进入资格路线；不使用 auto 属性优先级 | 缺点/拓扑/索引/有限性拒绝，内存不够不得偷偷截断 |
| 可观测性谱 | 有效几何对应 → 构造单位归一化 JᵀJ → `create_matrix` → `eigenvalues_symmetric_matrix` → `get_full_matrix` → `clear_matrix` | Core 不编写第二套视觉 ICP；谱计算是质量验证，不是新配准算法 | 谱缺失/负特征值超数值容差/秩不足拒绝 |

原始Surface经只读端口提供；每层临时采样由 NativePairParameters.SamplingStepMetres 固定（coarse≥fine>0），模块不发布新的采样Surface或拥有第二套采样服务。若适配器为 native 求解临时减点，点云路线固定 `sample_object_model_3d('fast', physical_step)`，保留 point_coord、point_normal、source-index 扩展属性；输入顺序绑定 Snapshot，避免 fast 顺序变化。`accurate` 会生成重心且丢扩展属性，不作为源索引保留路线；XYZ mapping 的采样单位为 pixel，仅作诊断比较，不能自动替换本契约的 physical_step。faces/primitive 采样会生成新点且可能丢属性，需由 Surface 端口提供独立映射，否则拒绝资格评价。法向缺失由宿主调用 SurfaceFeatures 公共能力提供新快照（point cloud MLS、triangles 或 xyz_mapping 分支由输入拓扑固定），IM-033 不复制该模块；`surface_normals_object_model_3d` 可产生零法向，零/NaN/数量不匹配先拒绝本次资格，只有宿主重新冻结有效点/域的新Snapshot才能剔除，不在本次质量评价缩小分母。无纹理但几何丰富可以配准；颜色缺失不等于几何缺失。平面/球/圆柱/重复阵列等几何对称性才影响可观测性和唯一解。

**参数映射。** `MaxIterations` 仅用于 Global 的 `max_num_iterations`（正整数）；Pair 使用 `pose_ref_num_steps`（本模块有效范围正整数），没有伪造的 max_iterations 参数。Pair preset 为 fast/accurate/robust；Global 仅 fast/accurate，传 robust 预检 InvalidInput。Pair/ICP 的 rel sampling 为各自模型直径比例，abs distance 转 native m；全程先把本次私有 xyz 和物理长度统一到 m，输出平移/距离转回请求单位一次，rotation 无单位、角度 rad。Profile 明确每层 sampling、key fraction、steps、skip、距离界，preset 先传，其后显式 override，实际生效映射完整写入证据。Rel 与 Abs 距离阈值互斥；正式 Profile 固定 abs 模式、rel 保留诊断比较，避免未说明的优先级。Global defaults 手册 accurate 下 rel=0.05、skip=2，fast 下 rel=0.07、skip=10，iterations=3；仅资料事实，不是消费者生产默认。

**多候选与自动建议。** Pair native 单次只返回一解。本模块将调用方冻结的 Hypothesis（几何支撑组合或 ICP 初值）按请求已冻结的 ordinal Id 顺序逐项执行，MaxCandidates 是全部显式假设及保留候选总数的资源上限（Graph计所有Solve边的假设数总和）；禁止截掉未评价假设后声称唯一。不同解用 `Tj·Ti⁻¹` 的位移和旋转角分组，门值来自 Profile；若两个不同组都通过基础/留出门，则 AmbiguousSolution，不按 RMS 最小自动唯一。无外部初值的 matching 还必须具备由宿主冻结的非对称/锚点可辨识证据（DistinctivenessEvidenceRef），不能把单解读回当作唯一性证明；证据缺失可返回诊断候选但 Qualification=NotEvaluated、PublishTransform 拒绝。

`RecommendParameters` 无生产副作用：输入绑定 Snapshot/ROI/单位、噪声/点间距观测来源、预算及已允许参数区间；固定生成按字典序排序的有限建议集合，Pair 仅取手册 rel={0.03,0.05,0.07}×fraction={0.2,0.3,0.4}×steps={5,7,10}（最多27组，取区间交集；无交集拒绝），skip/preset/normals 保持输入 Profile 不变。Global 仅 rel 三值×iterations={1,3,10}（最多9组），不推荐 robust。按固定样本计划分别新 identity Replay，先比较拒识/误接受和留出正确性，再对合格建议比较实测端到端资源/时延，排序 tie 用完整参数序列；没有实测只能标 SuggestionUnverified，不选“最快”。推荐结果带 input/Profile/Manifest hash、参数差异及依据；任一键变动即 stale，宿主审批后产生新 Profile revision，不写活动参数。用户授权下的技术主路线已按上表固定，外部门仅是物理阈值/真实资格。

**双向覆盖与残差。** 用求解前冻结的原始有效域，不按解后残差删分母。方向 S→T：N 为该域全部有效源点，C 为最近目标点/三角面距离 d≤CorrespondenceGate 的点数（含等号），coverage=C/N；T→S 同理，两方向分别≥MinOverlap。N=0 或 C=0 拒绝。native 距离无截断，覆盖只用 gate 分类；d>gate 的点仍进入全域残差并保留。RMS=√(Σd²/N)，Max=max|d|，绝对距离分位按固定 nearest-rank，support 和 IndependentCheck 分开；signed 仅在法向/有向面已资格化时存在，不能从 unsigned 填正号。Profile 同时固定全域 RMS/Max 和留出 RMS/Max 门，门缺失 NotEvaluated，不只报 inlier RMS。Pose 跳变 t/θ 门使用最终 T 相对 frozen 初值；matching无初值时将同字段解释为目标frame内允许绝对位移/转角（相对数学I度量范围，I不是观测/初值），禁止无界搜索后自动采纳。

**可观测性反例与公式。** 不能写“所有平面点都无法做6DOF”：有唯一、非共线标记对应的平面点到点刚体可以约束6DOF；无对应的平面点面残差不能约束平面内平移/绕法向旋转。两种 WitnessKind 明确区分。归一化 q=(Tp−centroid)/L（centroid为有效对应中变换后源点均值，L为这些点包围盒对角长度，L>0），twist=[δt/L, δω]。点面 J=[nᵀ,(q×n)ᵀ]；已确认唯一 point correspondence 的点点 J=[I,−[q]×]。G=ΣJᵀJ/N（这里N为合法对应数，不是覆盖的全域分母），eigenvalues 按升序，数值误差允许范围来自 Profile；rank 取 λ>RankRelativeGate·λmax，condition=λmax/λmin，λmax=0 或 rank<6 拒绝。Pair 不暴露 native point-plane/point-point 优化器内部，WitnessKind 是独立质量检查模型，不伪称其内部算法。谱只说明局部可观测性，不排除全局重复解，仍须 Distinctiveness/多候选/留出。共线点点、单平面点面、对称结构都应有对应反例；不以3×3点坐标 covariance 秩代替6DOF残差谱。

**Global 锚点、闭环和留出。** 公共契约边 T_to_from 从 From 的原始 frame 到 To；previous 仅是连续边输入语法，Core 展开为显式 `from/to`，避免让实现者猜 HALCON previous 序列方向。CommonFrame 是公共初值输入语法：Core 按 Solve 边列表将初值 Uj⁻¹·Ui 展开为显式 from/to，不探索未声明邻居；Previous 同样展开，不把原生全邻居行为隐入契约；所有模型必需（不定义隐藏可选节点）。返回 native Ui 后，固定锚点 a 的已知 Ta，输出 Ti=Ta·Ua⁻¹·Ui，锚点恰为 Ta。预测边 T̂j_i=Tj⁻¹·Ti，误差 Eji=Tj_i⁻¹·T̂j_i；t=||E.translation||、θ=acos(clamp((tr(R)−1)/2,−1,1))。闭环按节点/EdgeId 固定排序生成覆盖全部非树边的基本环，沿环反向边取逆，乘积 Ec 应接近 I；每个环的 t/θ≤Profile 门。只用优化后的节点变换重构环恒等是恒真式，不能作为独立闭环证据：必须使用冻结的观测边/留出边。IndependentCheck 点和 CheckOnly 边不参与求解；每个必需节点须有独立检查覆盖。没有环的树可完成诊断，若 Profile.RequireLoop=true 则拒绝资格；不编造 loop score=0。global 没有任意节点约束参数，靠重锚表达而非声称原生锁定锚点。

### 7.7 两个审查视角的故障闭环补充

算法视角沿 Validate、Pair/Graph、Matching、ICP、KnownTransform、Global、Recommend、Publish 逐项模拟：空/重复 point index、弱几何、重复阵列、遮挡/外点、共线/平面、有向法向、超预算、hypothesis 改变、留出泄漏、Calibration 撤销。输入改变一律新 identity；不能在排队/执行中换 Profile；重复 SurfaceId 的同 frame 自配准只有显式 DiagnosticSelfTest 证据且不得发布消费快照。Graph duplicate NodeId/EdgeId、self-edge、同 pair 多次重复 solve-edge 预检 InvalidInput；独立观测的平行边仅 CheckOnly，必须不同 evidence。

外部接入/运维视角沿提交→查询→取消→关闭→恢复→第二消费者：同 identity+相同请求 hash 重复提交只返回原 operation，不再次 native、不双发 Accepted；同 identity+不同 hash 为 IdentityConflict。新 identity 可使用同合法输入，但不能绕开仍未排空的实例预算。所有Task/progress/backend回调绑定operation identity，Core Sequence单调；UI另绑定Attach Generation（Core不增加未定义的generation字段）；订阅断连不停止 Core，重连 Query 原 operation，UI 不自动再次提交。Query 无记录用State=Unknown并带OperationNotFound，仅是查询观察、不伪造原operation状态；进程丢失的Unknown是宿主对旧Receipt的不可确认观察，DrainUnknown 是已知 operation 排空尚未证实，两者不混用。取消与完成同时到达：资源归还前已记录的取消/deadline优先决定 Cancelled/TimedOut，不发布计算候选；归还且终态后取消为 NoEffect，保留原终态。关闭先冻结接纳（与接纳锁同一原子门）→取消或等待所有已接纳 operations→排空→归还→Closed；Close 的等待 deadline 不取消后台清理，未排空返回 ResourcesReleased=false 并隔离实例，不能重新开启。IBackendRun.ReleaseAsync/registrar.CloseAsync 重复调用幂等；禁用 Task.Wait/Thread.Abort/GC.Collect 作为 native 停止证明。

资源关闭异常：backend 必须区分 native still running、native 已停但释放失败、全部归还；前两者返回 DrainUnknown/ResourcesReleased=false，保留实际租约/句柄追踪，不盲目 clear。释放成功后可诊断 RecoverableError；不得将未知的释放记零句柄。输入租约只读、每次 operation 私有工作副本；预计算索引不跨 operation 缓存，本 v0.2 不提供跨 operation 预计算缓存开关（后续另修契约），Prepare/距离写属性的模型不能共享。Query/Close 状态不依赖 UI，后台清理直到确认或宿主进程销毁；宿主崩溃后的旧句柄不恢复，只凭保存的 identity/Receipt 留为 Unknown。

## 8. 无 UI 入口与最小 Host

唯一接口见附录 A。Pair、Graph、固定变换评估具有同步和异步入口，参数和结果完全同源；同步仅用于非 UI 的小任务/Replay，不在 Dispatcher 上调用，不通过锁占住回调线程。Validate 只验证已提交元数据；运行时取得租约后仍必须验证真实点/域/版本，不以预检 PASS 跳过真实输入门。

最小 Host 是 A.4 唯一独立 BCL 控制台工程，只引用 Core（net10.0）与其 BCL，不引用 Shell、数据库、设备、DevExpress 或 AsunImage。注入 `ISurfaceReadPort`（内存快照）、`IRegistrationBackend`（脚本化模拟步骤）和 `TimeProvider`；Simulator 不自动给单位阵，每个脚本显式给原始 frame 的候选、距离、对应点、谱、停止及排空结果。HALCON 适配器另包引用用户确定的 AsunImage，并经 `ImageLibDotNet.cv2` 调用目标算子。

### 8.1 两个 Host 的正常与异常调用顺序

IntegrationHost / ComparisonHost 都按以下同一所有权顺序运行，只在消费者任务和输入域上不同。该顺序使用 A.2 既有 API；下面的强持槽是各宿主私有 BCL 数据结构，不新增模块公开能力或平台恢复服务。

1. 构造任何 registrar 或启动其工厂前，宿主进程根 Owner 先预留一个有限强持槽。BclHost 每次只运行一个 mode，槽数固定1；Core.Tests 的并发场景最多2个实例，槽数固定2。槽由进程主监督循环强引用，不能只放在业务方法局部变量、弱引用或无等待的 fire-and-forget continuation 中；槽满拒绝创建，不覆盖原槽。槽先保存借用的 surfacePort/backend/timeProvider/runtimePolicy、独立业务/cleanup错误集合及有限Task/identity存储；每槽预留8个原业务Task、8个operation身份、一个原CloseTask和一个关闭最终确认Task的位置（总Task槽10），并受请求/RuntimePolicy更小额度限制。相同identity的重复提交也保存每次返回的原Task；注册位置满则在调用前拒绝，不遗失已发Task。注册记录失败不得先调用有副作用的入口。
2. `new ObjectModel3dRegistrar(surfacePort, backend, timeProvider, runtimePolicy)` 返回后，在执行任何 Validate/Register/Publish 或事件代码前立即保存 registrar 到已预留槽。构造只保存依赖/校验策略、不启动backend或取得租约；构造失败记录业务错误，未返回实例的依赖由原宿主按其既有Owner收尾，不能虚构Close成功。若宿主将来外包工厂，工厂也必须在该已预留槽中交付实例及Task，不能先创建后尝试寻找Owner。
3. 业务 `try` 内按 `RegistrationIdentity.Create` → `Validate` → 对应 `RegisterPairAsync/RegisterGraphAsync/EvaluateAlignmentAsync` → `GetReceiptPayload` → `PublishTransform/ValidateUse` → 宿主采纳执行。提交前先保存 CalculationIdentity，返回的 ValueTask 只调用一次 `.AsTask()` 并立即保存原Task，再有限等待；不能只保存 WaitAsync 的包装Task。非法请求、DrainUnknown、Publish拒绝、宿主采纳失败均记录结果，不能从业务try内直接退出Main。两个Host的events回调异常按既有CallbackFailure语义核验；业务层捕获Register/Publish/证据消费/事件装配同步异常并保留原异常与阶段，不因此跳过cleanup。
4. **业务try外的独立cleanup预算与嵌套finally。** 无论正常、业务异常、取消或业务等待期限到达，最外层finally都启动独立真实wall cleanup观察预算2s，不复用业务CancellationToken或已耗尽的虚拟RunTimeout。cleanup内再用 `try/catch/finally`：以注入 registrar 的同一个模块 `clock.GetUtcNow().AddSeconds(2)` 为外部deadline调用原 registrar 的 `CloseAsync`，返回的ValueTask只 `.AsTask()` 一次并立即存到强持槽原CloseTask；同步调用异常或原Task异常单独放入CleanupErrors。内层finally在本轮剩余真实wall预算内观察**同一个**原CloseTask，可用 `Task.WaitAsync(remaining, TimeProvider.System, CancellationToken.None)`；TimeProvider.System仅用于真实wall等待观察，不能把SystemUTC生成的deadline交给固定虚拟clock消费。等待包装超时不取消原CloseTask、不停止底层清理、不另造替代CloseTask。调用本身阻塞或finally卡死由 A.4 外进程wall保护处理，虚拟时钟不能作为卡死保护。
5. 最外层finally即使观察失败仍必须把槽标为保留，由原Host主监督循环接手；只有Close报告State=Closed、ResourcesReleased=true，所有原业务/CloseTask已完成并观察异常、所有已登记且接纳operation的Query资源归还确认后，才允许按依赖Owner顺序释放借用端口/清空槽；未接纳identity的OperationNotFound仅结合保存的预检/拒绝记录判断没有资源，不把未知查询当释放证明。监督循环每100ms以真实wall有限观察原CloseTask/Query，至suite/外进程期限都不丢Owner。原CloseTask若已完成但返回DrainUnknown或抛错，不覆盖该Task/报告；全部operation资源归还确认后，仅允许一次幂等 `CloseAsync` 最终关闭确认，其deadline同样由注入模块 `clock.GetUtcNow().AddSeconds(2)` 生成，先保存到预留的第二Task位置，独立真实wall观察至多2s且不超过剩余suite/外层期限。该调用不是重建实例或重启后台清理；失败/未确认则继续保留，不无界创建Close Task。未确认归还、任一Close仍在途、Close异常未取得最终确认或转交被拒绝时，原Host持续强持 registrar、所有原Task、身份、借用端口及错误；禁止退出业务栈时丢Owner、换新实例、重用槽或dispose在用依赖。对本轮两个BCL Host不设置外部转交入口，固定由原Host保留；产品宿主若按其既有协议转交，必须获得接收方已强持相同对象/Task的明确回执后才能放手，转交拒绝仍由原Host持有。
6. **finally完成后再决定退出码。** 业务/cleanup错误分别保留并输出阶段、identity和释放观察，不让cleanup异常覆盖业务异常。全部必需动作/断言完成且槽已确认归还才exit0；任何失败/跳过/未完成/观察超时为非零候选。仍有保留槽时即使已经决定失败，Main继续运行原Owner监督循环，有限周期观察原CloseTask并对同identity Query，不提前返回候选退出码；确认全部归还后才非零退出。测试外进程wall到期可终止Synthetic worker并记录非零/未确认，这属于进程失败隔离，不得宣称资源已归还或已通过。真实HALCON/产品进程不能以此测试保护冒充安全释放。

正常IntegrationHost必须演练发布/一次应用及Close归还，正常ComparisonHost必须演练独立定位/被测域隔离及同一Close规则；二者异常分支都注入Register任务异常、Publish/结果消费同步异常、events回调异常、Close等待超时/迟到完成，验证原Owner保留、错误分离和最后退出判定。可控制后端在cleanup观察超时之后显式放行，再确认同一原Task被观察和槽被释放；不能用创建新实例让原失败看起来已恢复。

事件按 operation 单调 Sequence，进度可合并，接纳/排空/终态不可丢。订阅器异常只形成诊断，不改变算法结果或跳过释放；Core 回调不依赖 UI SynchronizationContext，WPF 投影自行派送。取消 Token 表示意图；运行 deadline 到期仍先走排空。Drain deadline 到期返回非终态 `OperationView(DrainUnknown)`，持有租约、隔离容量并保持 Query；不伪造 Cancelled/TimedOut，后台继续观察真实退出。

## 9. 状态、事件顺序与错误语义

### 9.1 状态机

| 状态 | 进入条件 | 允许行为 | 终态含义 |
|---|---|---|---|
| `Ready` | 依赖和实例可用 | 接收新计算 | 非计算态 |
| `Validating` | 已创建 CalculationIdentity | 只读校验、租约准备 | 可执行或失败 |
| `Queued` | Accepted且取得有界队列槽 | 等待执行、允许取消，RunTimeout持续计时 | 非终态 |
| `Running` | 输入门通过且 native 已开始 | 计算、进度通知 | 结果尚未发布 |
| `Cancelling` | 收到取消/deadline | 停止接收、请求 native 中断、排空 | 仅 `Cancelled`/`TimedOut` |
| `Draining` | 收到停止/完成请求，native、回调或资源可能仍在使用 | 等待所有 native、线程和队列工作退出 | 不能发布终态 |
| `DrainUnknown` | 排空等待期限到达或释放未确认 | 隔离实例容量、Query 原 operation，后台继续清理 | 非终态、Result=null |
| `Drained` | 所有 native 调用和回调真实退出 | 释放计算持有资源 | 不能发布终态 |
| `ResourcesReleased` | 句柄、缓冲区和输入租约已按所有权归还 | 发布一个终态 | 资源归还已确认 |
| `Completed` | 输出和证据完整 | 只读返回 | 不可变候选；不代表业务通过 |
| `Rejected` | 预检拒绝，或已接纳执行后的算法/质量门结果 | 预检短路径可直接返回；已接纳时仅在 `ResourcesReleased` 后返回原因和证据 | 不可映射为 OK |
| `Blocked` | 输入/能力/权限/Profile 缺失 | 要求调用方修正 | 不执行 native |
| `Invalid` | 输入格式/单位/版本不合法 | 返回校验错误 | 不执行 native |
| `RecoverableError` | native/资源/外部故障，可重新计算 | 已接纳时仅在 `ResourcesReleased` 后返回；保留本次证据，新 CalculationIdentity 重算 | 不自动重试 |
| `TimedOut` | deadline 到达且停止/排空完成 | 查询本次 operation | 不得假定结果 |
| `Cancelled` | 取消且排空完成 | 允许新计算 | 不产生结果事实 |
| `Unknown` | 宿主观察进程丢失的旧 operation；或 Query 无记录并带 REG3D-018 | 宿主对账，不恢复旧 native 句柄 | 查询观察，不可当失败或成功 |
| `Closed` | 实例停止接收、所有 operation 排空且资源归还 | 保留可用 Query，拒绝新计算 | 实例终态，不覆盖 operation 终态 |

### 9.2 事件顺序

每个 `CalculationIdentity` 的事件按接纳分支：预检拒绝为 `RequestReceived → Validating → Rejected | Blocked | Invalid`；若预检曾取得临时资源，先 `ResourcesReleased` 再拒绝。未接纳请求不得发送 `Accepted`、`Running`、`QualityEvaluated` 或结果事件。已接纳执行为 `RequestReceived → Validating → ValidationCompleted → Accepted → Queued? → Running → (Progress*) → QualityEvaluated? → DrainStarted → Drained → ResourcesReleased → Completed | Rejected | Blocked | Invalid | Cancelled | TimedOut | RecoverableError`。`Accepted` 只在检查通过并取得有界调度容量后发出；此后的任意失败（包括运行前失败）必须先排空 native/回调/租约、归还资源，再发唯一终态。`QualityEvaluated` 只在 native 已产生可评价候选时发送。

`DrainStarted` 后可发 DrainUnknown（非终态），确认后仍继续 Drained→ResourcesReleased→唯一终态；`Closed` 为实例通知，不替换 operation 终态。`Draining` 后不得再发送进度；`Drained` 表示 native 调用和回调已退出，`ResourcesReleased` 表示计算持有的句柄/缓冲区/租约已归还。终态只在这两项之后发送一次。迟到的 native 回调必须带原 CalculationIdentity，若已进入终态则记录为诊断事件并丢弃其结果。事件载荷只含候选摘要和 EvidenceRef，不含生产事实写权限。进程在回执前丢失时的 `Unknown` 是宿主查询观察，不伪造执行事件或已排空终态。

### 9.3 模块规范错误键（本轮契约待接收，平台映射另行采纳）

| 代码 | 语义 | 调用方动作 |
|---|---|---|
| `REG3D-001 InvalidInput` | 空对象、NaN/Inf、索引/拓扑/版本/hash 错 | 修正输入并创建新计算 |
| `REG3D-002 UnitMismatch` | 长度或角度单位不一致 | 绑定明确 Coordinate/Surface 版本 |
| `REG3D-003 FrameMismatch` | frame/修订/作用域不兼容 | 由调用方重建坐标链 |
| `REG3D-004 MissingInitialTransform` | 当前路线需要初值但没有 | 提供已声明初值或选择获批 matching |
| `REG3D-005 UnsupportedCapability` | 本模块未支持的方法/参数/属性或精确 API 版本 | 选择合法请求，不猜 API、不核验封装是否有算子 |
| `REG3D-006 InsufficientSupport` | 点/面/覆盖/独立检查支撑不足 | 保留缺口，改输入或返回不可适用 |
| `REG3D-007 InsufficientObservability` | 自由度未被数据约束 | 不采纳位姿；补独立约束 |
| `REG3D-008 AmbiguousSolution` | 多候选无法按 Profile 唯一选择 | 交给调用方复核/扩充约束 |
| `REG3D-009 DisconnectedGraph` | 图不连通或锚点缺失 | 修复图；不可删节点冒充成功 |
| `REG3D-010 ResidualAboveGate` | 残差超过 Profile 门 | 返回 Reject/Review，不调大门值 |
| `REG3D-011 Diverged` | native 未收敛或停止原因不可信 | 记录原始原因，按新 identity 重算 |
| `REG3D-012 ResourceLimit` | 点数、内存、并发或时间预算超限 | 降低输入需由调用方显式生成新快照 |
| `REG3D-013 Cancelled` | 调用方取消且已排空 | 不发布结果 |
| `REG3D-014 TimedOut` | deadline 到达且已排空 | 查询原 operation，不隐式重试 |
| `REG3D-015 NativeFailure` | AsunImage/HALCON 抛错或句柄失败 | 保留错误上下文；必要时重启适配器 |
| `REG3D-016 LateResult` | 终态后到达的回调/结果 | 丢弃结果，保留诊断关联 |

## 10. 取消、超时、线程、资源与排空

### 10.1 资源所有权

- `ISurfaceReadPort` 借用的输入租约由本次 CalculationIdentity 持有；模块不得修改源 Surface 或其属性。
- native ObjectModel3D、HomMat3D、Pose、临时数组、索引和序列化缓冲由本次计算的 `NativeResourceScope` 持有。
- 成功、异常、取消、超时和进程关闭均执行同一释放路径：停止接收 → 请求中断 → 等待 native 返回 → 释放派生资源 → 释放输入租约 → 记录释放结果。
- `clear_object_model_3d` 或等效释放只能在确认无并发访问后执行；跨线程共享必须由适配器串行化。

### 10.2 取消与超时

取消在验证、采样前、native 调用中、质量评估和排空阶段均可请求。取消不回滚历史结果、不改变标定、不发送设备命令。超时不是“失败后再试”的信号；只有排空和资源归还确认后产生 `TimedOut`；此前可为 `DrainUnknown`，调用方若要重算必须创建新的 CalculationIdentity。

### 10.3 线程与队列

- Core 可在宿主线程池运行，UI 线程只发命令/接收投影。
- 队列必须有界；并发上限和队列容量由不可变 PerformanceProfile 冻结，BCL Host fixture 显式 `MaxConcurrency=1`；部署值由 RuntimePolicy 必填，不得依赖 `Environment.ProcessorCount`；达到上限返回 `ResourceLimit` 或显式背压，不无限排队。
- 相同源模型的并行读只有在适配器声明 native 线程安全时才允许；不同请求不得共享可变属性或工作句柄。
- 进程重启后不得恢复 native 句柄，不读取 `latest` 猜测结果；宿主凭 Snapshot/Receipt/operation 查询并将未确认结果标为 `Unknown`。

## 11. HALCON 26.05 与 AsunImage 适配边界

### 11.1 已核对的资料

项目 `halcon算子手册\operators` 已提供以下目标路线资料：`register_object_model_3d_pair.html`、`register_object_model_3d_global.html`、`rigid_trans_object_model_3d.html`、`get_object_model_3d_params.html`、`distance_object_model_3d.html`、`clear_object_model_3d.html`。手册明确 pair/global 支持取消/中断；pair 返回 pose 和 overlap score；global 接收模型集合、变换关系类型、初始/输出变换及每模型邻居 score。参数语义按 7.5/7.6 固定；运行时验收仍须记录 native 错误和实际生效参数，不能只根据 HTML 名称推断。

适配器统一以 `ImageLibDotNet.cv2` 调用上述算子；HALCON 26.05 全算子能力按用户基线直接使用。公共 API 不暴露 HALCON 类型。只有实际 C# 参数类型、重载或封送存在歧义时，在消费项目核对公开签名/编译；不列对象式候选重载，不扫描 AsunImage 内部，不设置算子存在/授权/版本安装准入门。

### 11.2 算子决策

1. 经 `using ImageLibDotNet;` / `cv2` 调用 HALCON 26.05 算子，不另接 HOperatorSet 或 halcondotnet.dll；重载/封送有实际歧义时再查公共签名。
2. Pair 计算前确认 method、参数名和值、初始 pose/坐标、采样和法向条件；读回 score 后保留其原生 `MetricKind`。
3. Global 先在 Core 验证节点/边/锚点和公共 frame，再传入 native；读回每节点矩阵后由 Core 按 `from/to` 语义重表达并独立检查。
4. 质量评估需使用固定变换和独立域；`distance_object_model_3d` 的 `MaxDistance=0` 表示计算全部距离，非零时超出值会被设为 `MaxDistance`，因此截断距离、方向和 output attribute 按目标版本资料适配，不能把饱和值或空对应的零值当作真实最大偏差或合格证据。`&distance`、`&closest_index` 会写入源 ObjectModel3D 的扩展属性，不能在共享输入句柄上无保护地执行。
5. `prepare_object_model_3d` 仅用于本次 distance 计算的私有工作副本或明确租约；它会改变 ObjectModel3D 的准备数据，不能对跨请求共享句柄做无记录的原地准备。
6. 变换/法向/点属性的单位和索引映射由 Surface/Coordinate 端口提供；native 内部属性编号不能代替平台 source index。

### 11.3 AsunControl 资料的使用边界

既有只读参考记录涉及 `Vision_CameraCalib` 的接口、状态事件和资源释放。当前不访问 AsunImage 内部。其 `CameraCalibrationEngine`/WinForms 控件提供了状态事件和 Dispose 组织方式，可借鉴“事件绑定、失败显式、清理集中”的工程思想；它不是本模块的 3D 配准契约，不能复制其 UI、固定参数、错误文本或 .NET 8 宿主依赖。未发现可直接复用的三维配准成品模块；不以历史项目代码替代目标 HALCON 26.05 资料。

### 11.4 SurfaceData H/codec 消费桥

Registration 只消费 [surface-data §17-19](../surface-data/DEVELOPMENT-GUIDE.md) 已定义的原始 Surface/域/索引/单位/来源，不接管其 Source、buffer、lease、metadata 或 raw object 的 Owner。Core 仍以原始 CPU 坐标、原始 slot、`SurfaceRevision`、`CoordinateRevision` 和 `LengthUnit` 作为输入事实；native 返回的量化坐标、临时属性或显示 LOD 不能覆盖这些事实。

需要 HALCON 时，Adapter 必须按以下顺序执行：先完成 Core 输入与域校验，再由 SurfaceData 端口取得冻结输入；随后冻结 `NativeRuntimeBinding`（worker 可执行文件绝对路径、worker/AsunImage hash、commit 上限、wire 上限）和用途提供的 `NativeAccuracyPolicy`，保留 CPU 原值后才选择 H1 float32、H2 double tuple 或 H3 显式闭区间筛选。H1 往返不是无损转换，必须按显式误差阈值逐坐标核对；H3 native 选出的 slot 集合必须与 CPU 闭区间集合完全一致。任何单位换算、边界进出、点数/mapping、hash、frame 或 revision 不一致均返回 Integrity/Rejected，不能夹紧、补 slot、静默切换表示或把 native 值写回测量事实。质量门和残差计算始终使用 CPU 原坐标，native 值只作执行和保真验证。

每次 H 调用都在该请求的隔离 worker、JobObject、IPC frame 和有限 budget 内完成；父进程保留原 Task、CallId、输入引用和清理记录。取消或 deadline 只发出取消/终止信号，必须继续观察 worker、pipe、native clear 和资源回执；未确认退出只能保持 `Pending/DrainUnknown`，不能提前标记 `Cancelled`、`TimedOut` 或 `ResourcesReleased`。H 适配器不持有跨请求可变 ObjectModel3D，`prepare`、distance 扩展属性和 clear 均使用私有副本或明确 lease，成功、失败、取消路径按原 Owner 归还。

`surface-metadata/1` 和 `surface-raw-buffer/1` 只作为可选的重开输入。调用方必须注册完整 `VersionRef`、发布包 hash、有限读取上限和对应 validator；未知版本、尾字节、hash/长度错误、缺 buffer 或权限失败均拒绝，不读取无限流，也不以 codec 恢复 lease、Task、native handle 或执行状态。Decode/Validate 成功后仍须重新执行 SurfaceData Validate→Plan→Open，生成新的 session/CalculationIdentity，并重新核对 source/domain/slot/unit/hash；回退包只保留原证据和诊断，不能伪造空 Surface 或沿用旧运行身份。自动分块、表示或阈值建议只能作为带原因的候选，必须由新请求显式采纳，不能静默改变批准 Profile。

## 12. 可选 WPF UI 契约与操作规格

Wpf 是独立投影包（net10.0-windows，UseWPF=true），用本机 DevExpress25.2.3，不从 NuGet下载。业务入口仍是同一 registrar，图/配准/参数校验不复制进 ViewModel；3D视口经宿主公共 adapter 注入，不以Chart代替3D视图，不新建viewport、ROI、计量或重建引擎。本节为实施规格，未创建原型、运行WPF或作视觉验收。

### 12.1 角色与连续任务

操作者能查看输入/图/候选/错误、在宿主授权下计算或取消；工程师可修改参数草稿、批量诊断边并请求宿主采纳变换；只读/维护角色分别由 UiPermissions 显式控制。权限检查由宿主执行，每次动作前重新取得最新权限；禁用命令仍显示原因。UI不持有生产放行权、标定激活权或设备控制权。

1. Attach载入冻结Nodes/域/Profile及已有operation；先展示source/target或图节点、frame、unit、revision和当前状态。缺输入显示“选择输入”，不生成单位阵。
2. 工程师在右侧草稿修改方法/初值/采样/预算；PropertyGrid按“方法、质量、资源、来源”分组，高级项渐进展开。修改由SetDraftAsync按最新CanEditDraft权限交宿主草稿Owner校验保存，返回字段Issue；只影响Draft，新计算由宿主生成新identity；运行中的Request不改写。
3. 明确点击“计算”：宿主GetDraftAsync返回完整不可变请求，UI调用Validate；错误定位到节点/边/字段，不启动backend。通过后按Kind调用异步入口；Dispatcher只发命令、不调用同步计算。进度显示阶段/身份，分数只显示为原生指标，不标“置信度”。
4. 候选Grid选中后与3D叠加、节点/边树、残差Chart及独立检查域联动；域颜色/线型同时区分定位、留出、被测和排除，不能只靠红绿。原始/变换后切换是临时显示映射，不写Surface、不增加ApplicationLedger。
5. 图中多选边后“检查选中边”只筛选/投影已有诊断；重新求解必须生成新请求。CheckOnly与Solve用图标/文字区分；失败边保持可见，不默认从图中移除。查看一条边可定位源/目标、误差和输入证据，查看环可高亮完整环。
6. Completed后先展示“配准合格/仅供诊断/未评估”和各门；“使用变换”一直可见，仅在权限/资格/资源/当前输入/校准/账本校验都通过时启用。调用PublishTransform，再由宿主在原子注入步骤采纳；不提交质量事实。候选手动选择仅改变诊断投影，不能越过AmbiguousSolution门变成Qualified。
7. Cancelling/Draining/DrainUnknown禁用新计算和使用变换；显示“正在停止/正在释放/释放未确认”及“查看状态”。断连后重新Attach→Query原identity，不自动提交。宿主确认旧实例释放后才可创建新实例。

### 12.2 1920×1080构图、细节与控件落点

唯一验证viewport为1920×1080物理像素；实际可用client area须扣除任务栏、窗口边框/标题、宿主导航/状态栏。记录当前DPI下物理像素→DIP换算，不改显示设置、不跑其它分辨率矩阵。布局以下述可用client约1888×960（100%时的参考预算，实际测量为准）设计，宿主占用增大时收起高级草稿，仍保证图像/身份/状态/关键动作可见。

| 区域 | 构图与交互 | 固定控件/公开依据 |
|---|---|---|
| 顶部56 DIP | 左输入身份和frame/unit，中状态/资格，右计算、取消、使用变换；溢出诊断入口可紧凑，但关键命令不放下拉隐藏 | WPF按钮/宿主命令样式；DevExpress.Xpf.Core.SuperTip提供限制和恢复说明 |
| 左侧约232 DIP | 节点/域/边层级，数量和失败标志；键盘选中联动，支持多边选择和过滤 | DevExpress.Xpf.Grid.TreeListControl、TreeListView，ItemsSource；Grid.v25.2.dll |
| 中央弹性区 | 原始/目标/叠加3D图像，主任务区不少于约60%宽；工具条只放视图复位/原始叠加/域显隐，紧贴影像 | 宿主注入FrameworkElement及公开视口端口；不由ChartControl绘制3D |
| 右侧约320 DIP | PropertyGrid草稿；来源/质量先显示，参数高级组折叠；运行期间字段只读且显示冻结revision | DevExpress.Xpf.PropertyGrid.PropertyGridControl，SelectedObject；PropertyGrid.v25.2.dll |
| 底部约220 DIP | 候选/节点结果Grid与残差Chart横向联动，默认看全域和留出两系列、可按域筛选；缺值显示“未评估”，不是0 | DevExpress.Xpf.Grid.GridControl、TableView、ItemsSource；DevExpress.Xpf.Charts.ChartControl、XYDiagram2D、Series.DataSource/ArgumentDataMember/ValueDataMember；Grid/Charts.v25.2.dll |
| 框架与详情 | 8 DIP分隔、16 DIP内距，标题/分组有统一层级；左/右/底可以调整并恢复；证据详情渐进展开 | DevExpress.Xpf.Docking.DockLayoutManager、LayoutGroup/LayoutPanel，Docking.v25.2.dll；DevExpress.Xpf.Editors.Flyout.FlyoutControl（Core.v25.2.dll） |

使用宿主统一DevExpress主题、图标和字体，常规文字14 DIP、区块标题16 DIP、状态文字加图标；单位与数值对齐，hash默认短显并可复制完整值，状态不写夸张文案。所有可用图标动作有同名文字/AutomationName。Grid/TreeList保留虚拟化，重图只发布有界摘要，不在Dispatcher一次创建全点云行。残差Chart用宿主/结果的有界投影数据，不能在UI删外点后重算质量；选区只影响查看范围。动画只用于非关键面板/详情转换，输入接纳、取消/排空状态立即更新；高负载禁用非必要动画，不把动效当算法进度。

FlyoutControl使用已核的IsOpen/StaysOpen/PlacementTarget及FlyoutSettings.Placement；非明显动作的SuperTip包含“作用范围、当前限制、恢复动作”。BarItem可用SuperTip属性；普通WPF控件ToolTip使用SuperTipControl容器，不能将SuperTip对象误当普通Tooltip内容。Dock布局只保存视图布局，不保存Profile/native对象；宿主按版本保留XML并恢复，缺关键区域/损坏时回到本节默认构图，提供“恢复布局”。不在本任务造新的产品配置Store。

### 12.3 公开 UI 挂接、权限、语言和所有权

以下类型只在 `Asun.Modules.Registration3D.Wpf`，不进入Core或要求Core引用WPF。导入 System.Collections.Immutable、System.Globalization、System.Threading/Tasks、System.Windows/Controls 以及Core namespace；类型均为契约，没有伪工厂或未定义回调。

```csharp
public sealed record UiPermissions(string Revision, bool CanCalculate,
    bool CanCancel, bool CanEditDraft, bool CanUseTransform);
public sealed record UiAttachment(CalculationIdentity? Calculation, string LayoutKey);
public sealed record ViewportProjection(CalculationIdentity Calculation, long Generation,
    string? CandidateId, ImmutableArray<NodeTransform> Transforms,
    ImmutableArray<string> NodeIds, ImmutableArray<string> DomainIds,
    ImmutableArray<long> OriginalPointIndices);
public interface IRegistrationViewportPort {
    FrameworkElement View { get; }
    ValueTask ShowAsync(ViewportProjection projection, CancellationToken cancellationToken);
    ValueTask DetachAsync(long generation);
}
public interface IRegistrationUiHost {
    UiPermissions GetPermissions();
    string ResolveText(string resourceKey, CultureInfo culture);
    ValueTask<RegistrationRequest> GetDraftAsync(CancellationToken cancellationToken);
    ValueTask<ValidationReport> SetDraftAsync(RegistrationRequest draft, CancellationToken cancellationToken);
    ValueTask<TransformUseContext> GetUseContextAsync(CancellationToken cancellationToken);
    ValueTask<ValidationReport> AcceptSnapshotAsync(ReleasedTransformSnapshot snapshot,
        CancellationToken cancellationToken);
    ValueTask<string?> ReadLayoutAsync(string layoutKey, CancellationToken cancellationToken);
    ValueTask WriteLayoutAsync(string layoutKey, string layoutXml, CancellationToken cancellationToken);
}
public sealed class RegistrationWorkbench : UserControl, IAsyncDisposable {
    public RegistrationWorkbench(IObjectModel3dRegistrar registrar,
        IRegistrationViewportPort viewport, IRegistrationUiHost host);
    public long Generation { get; }
    public ValueTask<long> AttachAsync(UiAttachment attachment, CancellationToken cancellationToken);
    public ValueTask DetachAsync();
    public void SetPermissions(UiPermissions permissions);
    public void SetCulture(CultureInfo culture);
    public ValueTask DisposeAsync();
}
```

Attach必须在控件Dispatcher调用，每次递增Generation，先Detach旧投影/查询，挂接viewport.View，Query已有identity并读取宿主layout；同View不能挂到两个父控件，借用期间宿主不可转移。不存在operation显示“未找到记录”，不重提交。新计算的progress绑定operation+generation+sequence后Dispatcher投影；对已存在/重新Attach的operation每250ms Query（仅运行/排空期、有界单个查询），终态停止；Detach取消查询计时器，不取消Core计算。读取layout失败可恢复默认并显示诊断，不改Profile或阻断后台清理。

SetPermissions更改投影且即刻禁用无权命令；实际动作仍重新GetPermissions与宿主权威检查，不依靠按钮禁用充当授权。权限撤销不擅自终止已接纳计算，后续取消由宿主授权者处理。SetCulture在Dispatcher执行，默认zh-CN，支持zh-TW/en-US并可扩展；重新解析标题/状态/参数/提示/错误/恢复/AutomationName、格式化数值，保留Request与域选择，不重新计算。模块不放语言切换入口。无法解析resourceKey按key显示并产生诊断，不暴露原始native异常作为唯一用户提示。

Detach/Dispose只停止UI查询、解绑监听、调用viewport.DetachAsync(旧generation)并移除借用View；不调用registrar.CloseAsync，不dispose借用视口或Surface/native资源。UI等待期间返回的旧generation回调丢弃投影，Core仍按原operation清理；Dispose重复幂等，Dispose后Attach拒绝。registrar的创建宿主是唯一Close Owner：退出应用时先Detach UI，再显式CloseAsync并确认ResourcesReleased；关闭等待超时不得由WPF Unloaded抢先释放后端。窗体/页面不是算法资源生命周期Owner。

### 12.4 键盘、三语和可判定验收

Tab顺序：输入/方法→计算→取消→树→视口工具→候选→草稿→使用变换→证据；F5仅在可计算状态触发显式计算，Esc关闭详情或请求取消（有权限且宿主允许时），不把Esc映射为使用/采纳。Enter在候选行只选中诊断，不能默认发布。错误摘要能定位字段，焦点不因进度刷新跳回顶部；批量选择可用Shift/Ctrl，所有命令有键盘替代。稳定AutomationId前缀 `Registration3D.`，具体键为Calculate、Cancel、UseTransform、NodeTree、Viewport、CandidateGrid、Draft、Status、Evidence、RestoreLayout。

| key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Calculate / Cancel / UseTransform | 计算 / 取消 / 使用变换 | 計算 / 取消 / 使用變換 | Calculate / Cancel / Use transform |
| Draining / DrainUnknown | 正在释放 / 释放未确认 | 正在釋放 / 釋放未確認 | Releasing resources / Release unconfirmed |
| RelativeDiagnostic / NotEvaluated | 仅供诊断 / 未评估 | 僅供診斷 / 未評估 | Diagnostic only / Not evaluated |
| Disconnected / ViewEvidence | 图不连通 / 查看证据 | 圖不連通 / 檢視證據 | Graph disconnected / View evidence |
| RestoreLayout / CheckStatus | 恢复布局 / 查看状态 | 還原版面 / 檢視狀態 | Restore layout / Check status |

1920×1080真实WPF验收须逐项核：client area/DPI记录、长英文不截关键状态/动作、图像区域和候选可同时查看、树/Grid/Chart/视口联动、三语即时刷新、键盘/UIA、布局保存/损坏恢复、权限撤销、断连Attach、晚回调、Detach不Close、宿主Close超时保持DrainUnknown。视觉品质（主题、排版、图标、留白、动效）与操作正确性分别验收；截图/模拟数据不能证明真实HALCON或现场性能。

### 12.5 Viewport Assembly v0.2 消费桥

Registration 的 `IRegistrationViewportPort` 是窄投影桥，不是第二个 viewport、ROI、计量或重建引擎。宿主必须把同一 `ViewportControl` 实例的 `IViewportControlBinding.Presentation` 与已绑定的 `IViewportUiBinding` 接入该桥；桥不得自行创建 renderer、root、session、Surface lease 或隐藏 Dispatcher。`ViewportUiBindingOptions.Lifetime` 必须显式传入实际 `IViewportUiLifetimePort`，并与该 Control/root/session 属于同一 Owner；null 或跨 root 的 Lifetime 在 Reserve/Dispatcher 之前拒绝。

投影桥复用 viewport Assembly v0.2 的原始调用链和 Task：`PresentationRequest`、原 `Commit` Task、`Acquire`/`Confirm`、`Revoke`/`Return`、`PresenterLease`、`SourceCall`、`DisplayGeneration`、`BackendGeneration` 与完整授权快照逐项绑定。Registration 只发布 `ViewportProjection` 和观察结果，不替换原 Task 为 wrapper，不把 `Dispatcher` 完成当作 GPU/native/lease 完成，也不从 `PresentationId` 非空推断授权。generation、backend generation、source/context revision、authorization 和 binding identity 任一不一致时丢弃新投影并按原记录观察；新 binding 不得接收旧 submission。

`RegistrationWorkbench.AttachAsync`/`DetachAsync`/`DisposeAsync` 只管理 UI 借用和查询。Detach 先关 binding 门、取消手势和 UI 查询，再等待有限的 Dispatcher/呈现清理并沿同 Owner 执行 Revoke→Return；晚到的 Commit、Dispatcher 或 Return 必须保留在原 binding/root 的 trace 中，超时返回 `UiCleanupUnknown`/`DrainUnknown`，不能删除记录或重新 Acquire。`OwnSession=false` 时不调用 `registrar.CloseAsync`、不关闭共享 session、不 Dispose 宿主 Lifetime；关闭 registrar/session 的唯一 Owner 仍是宿主。`OwnSession=true` 也只能在原 Control Task/借用真实收敛后调用同一 session 的 Close，不能由 `Unloaded` 冒充完成。

UI 资源使用 viewport 的完整 `viewport-ui-text/1` schema 和三语 `zh-CN`、`zh-TW`、`en-US` 快照，并由 Registration 自有 `Registration.*` 键扩展；缺键、非法 schema、超长文本或版本/hash 不匹配时保持旧资源并拒绝更新。语言切换只重新投影文字、AutomationName、提示和错误恢复，不刷新像素、不重新授权、不提交草稿；真实 WPF、UIA、键盘、DPI 和 1920×1080 视觉验收仍属于 viewport/宿主运行门。

## 13. 正常、边界与失败案例

### 13.1 正常 pair

两个有来源 hash、同一长度单位和相容 frame 的表面，初值来自批准外部关系，定位支撑与独立检查域不重叠。输入门通过，ICP 返回有限刚体变换和 score；Core 组合 `Δ·T0`，复核双向覆盖/残差/可观测性，输出 `Completed` 候选。调用方仍需判断自己的业务适用性。

### 13.2 边界 pair

- 重叠刚好处于 Profile 门值：门值边界的包含关系由 Profile 固定并在测试中分别验证；缺省不自行四舍五入。
- 所有点在一个平面：无对应的点面残差请求6DOF时返回 `InsufficientObservability`；有唯一非共线标记对应的点点模型按7.6谱判断，不一概拒绝平面。受限自由度估计不支持。
- 只有一个有效点或零对应：返回 `InsufficientSupport`；RMSE=0 不改变状态。
- 两个请求共享源 Surface：源只读不变，每个请求有独立租约、临时工作模型和结果。

### 13.3 失败与恢复

- 单位或 frame 修订不匹配：`Blocked/UnitMismatch/FrameMismatch`，不调用 native。
- Global 图分裂或锚点缺失：`Rejected/DisconnectedGraph`，保留各节点/边诊断。
- native 抛异常：进入 `RecoverableError`，记录 operator、参数摘要、native 错误和释放状态；新请求使用新 CalculationIdentity。
- 取消/超时：停止接收、排空 native、释放资源后分别返回 `Cancelled`/`TimedOut`；排空未确认则返回非终态 `DrainUnknown`，不释放仍在使用的句柄。
- 进程在回执前重启：原 operation 标记 `Unknown`，宿主查询原 identity；不得自动创建新结果冒充原结果。

## 14. 测试矩阵与可判定断言

| ID | 层级 | 场景 | 必须断言 |
|---|---|---|---|
| R3D-C01 | Contract | 字段、单位、版本、Owner 校验 | 缺失/冲突字段为 Blocked/Invalid；无影子 Schema |
| R3D-N01 | Unit | 非交换 `T0` 与 `Δ` | 结果为 `Δ·T0`，不是 `T0·Δ`；原 frame 正确 |
| R3D-N02 | Integration | AsunImage pair/global 适配 | 真实 pose/matrix/score 读回并保留原生类型；只在实际 C# 重载/封送歧义时核对公开签名或编译；不重复核验封装存在 |
| R3D-Q01 | Quality | 双向覆盖、残差和空对应 | 分母、单位、截断语义正确；空对应不通过 |
| R3D-Q02 | Quality | 平面低 RMS、周期阵列多解、整体抬高 | 自由度不足/歧义/缺陷保持分别显式返回 |
| R3D-G01 | Graph | 分裂图、单桥错边、缺失锚点 | 不删点伪造整图成功；剔边后重验连通 |
| R3D-R01 | Replay | 固定输入+RuntimeManifest+Profile | 语义结果可复现；差异必须有批准的非确定性说明 |
| R3D-F01 | Fault | native 异常、坏句柄、内存上限 | RecoverableError/ResourceLimit；所有资源释放证据齐全 |
| R3D-F02 | Fault | 每个阶段取消、deadline、迟到回调 | 事件顺序合法；迟到结果不覆盖终态 |
| R3D-CN01 | Concurrency | 两实例共享源、不同参数 | 无属性覆盖、无句柄交叉、租约独立 |
| R3D-P01 | Performance | 点数 N、节点 K、边 E、候选数 | 记录冷/热 P50/P95/P99、峰值内存、并发、取消延迟 |
| R3D-U01 | UI（如有） | 1920×1080、UIA、键盘、三语、八态 | 页面只投影；所有命令可追溯到 CalculationIdentity |
| R3D-V01 | Version | HALCON/AsunImage 版本变更 | 适配器能力矩阵和回放差异先审；不兼容时可回退 |

测试证据至少保存输入快照 hash、Profile/参数版本、RuntimeManifest、expected/actual、Issue、资源释放和 trace。Mock/Simulator 只能验证软件控制流，不能冒充真实 HALCON、计量标准件或现场验收。

## 15. 性能预算与资源证据

每个消费者必须冻结不可变 `PerformanceProfile`/`BenchmarkProfile`，绑定模块/Core/adapter、HALCON/AsunImage、运行时/OS/硬件、输入快照和方法/参数/精度 revision/hash。负载按 `N`（有效点数）、`M`（目标点数）、`K`（模型数）、`E`（图边数）、`C`（候选数）、采样层数、路线、并发、队列和缓存冷/热状态分桶。Profile 在运行前冻结预热次数、测量次数、最低有效样本数、固定吞吐观察窗口、有限 deadline、最大队列/工作集/安全并发、峰值资源预算和阈值来源；冷启动单独测量，热态固定预热且不计入样本。没有 Profile 数值时使用“无默认并阻断”，真实性能目标记 `TargetPending`；纯 Core 合成验证使用显式 fixture 预算，不等待客户节拍。

分别测输入快照/只读租约准备、采样/法向/工作模型创建、native pair/global 核心、质量评估、独立检查、结果封装/序列化、UI 投影（如有）、排队及端到端至 `ResourcesReleased`；另测取消至 native 停止、Drain 和租约归还。报告各阶段延迟、固定窗口吞吐、队列深度/高水位、峰值/稳态托管与 native 内存、分配、句柄、并发和重启恢复成本；未知 native 资源记 `Unknown`，不得记 0。Global 候选边可能为 `O(K²)`，先验减边须由调用方声明且保留连通性。索引/模型缓存键必须含输入 hash、frame revision、方法/参数和精度版本，不能跨修订复用。

通用 P50/P95/P99、样本有效性、失败/删失和未排空规则按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)。本模块须按终态分别报告配准质量拒绝、资源拒绝和 `DrainUnknown`；不得将它们混作已完成成功样本。阈值只能来自已采纳消费者/客户 Profile；缺失时标 `TargetPending`。

## 16. 可观测性与诊断

每次计算写入结构化 trace（不写生产事实）：

- `operationId`、`CalculationIdentity`、宿主 correlation/parent id；
- 输入 SurfaceId/revision/hash、frame/单位、域计数、有效/剔除/派生点数；
- 方法、实际生效参数、Profile/算法版本、native operator 和适配器版本；
- 阶段开始/结束、耗时、队列等待、取消时间、排空时间、资源字节和并发槽；
- 候选数、score 原生类型、覆盖分母、残差摘要、可观测自由度、图连通/闭环结果；
- 状态迁移、错误码、native 错误、异常类型、EvidenceRef、释放确认。

日志不得记录完整点云或敏感图像，除非宿主 EvidencePolicy 明确允许；摘要必须能回到可引用的快照。诊断事件与结果事件分开，晚到事件不改变终态。

## 17. 版本、兼容、发布与回退

### 17.1 兼容策略

- Core 契约使用显式 major/minor/patch；同一 major 内允许新增可选证据字段，不改变已有坐标、单位、状态和指标语义。
- 任何改变变换方向、score 解释、默认路线、质量门、参数单位、错误码或事件顺序的变化必须升 major，并同时更新 Contract/Schema、Replay manifest 和适配器矩阵。
- HALCON 26.05 / cv2 全算子是固定基线；RuntimeManifest 记录算法和参数语义。UnsupportedCapability 用于本模块未支持的变换模型/自由度或参数组合，不用于重复核验封装算子。
- 输入和结果版本均带 hash；不支持的旧版本应明确拒绝或走经过验证的迁移器，不能按字段位置猜测。

### 17.2 发布包

独立发布至少包含：Core/Contracts/Adapter 程序集、依赖清单、版本与 commit、HALCON/AsunImage 能力矩阵、API/错误/事件契约、Replay/Golden 索引、PerformanceProfile、兼容说明、许可证与安全审查记录、回退版本和校验 hash。发布不包含客户项目、制程配方、生产事实库或设备配置。

### 17.3 回退

回退前先停止新任务并等待旧任务排空；保留旧结果和 EvidenceRef，不覆盖历史。宿主按兼容矩阵恢复上一已验证版本，旧版本不能读取未兼容的新输入/结果。回退失败或回执不明时状态为 `Unknown`，由宿主按原 operation 查询。

## 18. 两个真实消费者的接入边界

两个消费者都通过宿主/调用应用接收 IM-033 已发布的不可变 registration result；任何需要重建或跨设备坐标的流程，都由宿主把该 result 与合法 `CalibrationSnapshot`/坐标链组合成新的只读输入后注入。消费者不得以模块间直接调用替代宿主交接，也不得重复估计或重复应用同一 registration transform。

### 18.1 多视角 3D 整合工具

调用方负责采集/重建产生的 Surface 集合、共同坐标声明、外参/初值来源和最终整合策略。模块只返回节点变换、边质量、闭环/覆盖和可观测性，并发布带来源和适用范围的 registration result。若已获资格的外参足够，调用方可选择 `KnownTransform`，不强制每次自由 ICP。宿主将结果与 calibration/coordinate snapshot 组合后再交给需要它的重建或整合流程；整合后的 Surface 由调用方交回 PKG-027/028；本模块不持有全局场或拼接事实。

### 18.2 独立 3D 比较/量测工具

调用方提供冻结参考 Surface、被测 Surface、独立定位域和排除被测目标的规则，模块输出固定变换和质量证据；后续偏差、距离、面积、体积由 PKG-030 执行。调用方不得把被测目标放入定位支撑以消除真实差异，也不得把模块的候选结果直接当量测结论。

两个消费者必须共享同一 Core/Contract/Replay 语义；允许不同适配器和 UI 投影，不允许复制一套 Registrar、质量门或错误枚举。

### 18.3 消费桥、Owner 与版本边界

| 消费面 | Registration 的职责 | 保留在原模块/宿主的职责 |
|---|---|---|
| 托管 Core 与 Simulation-S1 | 仅消费已接收的 Core 端口、S1 脚本结果和原 Task/lease 语义；S1 的 `BackendOutcome` 不能冒充 ICP | Core/S1 的实现、测试、发布和资源根；S1 不授真实 HALCON 或生产资格 |
| HALCON Adapter | 按 §11.4 绑定 `NativeRuntimeBinding`、Accuracy、CPU 原值和 H/worker 清理证据 | `surface-data` 的 Surface/buffer/lease Owner、真实 runtime/worker 发布 hash 与运行资格 |
| SurfaceData H/codec | 只按 `surface-metadata/1`、`surface-raw-buffer/1` validator 有界重开并重新 Validate/Plan/Open | codec、format registry、raw bytes、Storage/Source 事实和 validator 版本/hash |
| Viewport WPF Assembly v0.2 | 通过同 Control 的 `Presentation` 生成 Registration 投影，复用原 Task/lease/generation/auth，执行有限 Detach | `viewport` 的 Root/Session/Presenter/Lifetime/Close Owner、完整资源 Catalog 和实际 WPF 验收 |
| 两个 Synthetic Host 与两个真实消费者 | 按各自 Profile 提供输入、授权、Calibration/coordinate snapshot 和最终业务采纳 | 宿主的设备/数据库/质量放行/客户事实；Registration 不写下游 Store、不发设备命令 |

上述桥只约束已公开契约的消费顺序、身份和所有权，不复制上游 API，不改变 C1-C5 接口，也不把 codec、UI 或 native handle 纳入 Registration Core 的可序列化身份。

## 19. 实施顺序、准入与验收

2026-10-10主控已内容接收托管 Core 六项，状态为`ModuleCoreImplementationReady`，仅规格准备：值契约、输入/域/图校验、刚体组合/覆盖质量计算、identity/Receipt/发布用途纯校验、有界未测参数建议、注入端口下协调和受控测试Host。Pair/Graph/Known算法规格的回读不等于HALCON数值或Adapter实现准入；本次不授WPF、平台集成、真实算法/性能/计量或现场资格，也不启动产品实现。既有ScriptedBackend/ManualTimeProvider仍仅为Core测试Host内stub；2026-10-11主控另完成附录C.1～C.6回读，独立Simulation-S1按DEV-GOV-010 §3.1六项文档规格接收为ModuleCoreImplementationReady，仅限纯托管脚本Simulator/factory/pack/Clock/有限资源与两个Synthetic Host，不是从Core接收推导Ready。显式BackendOutcome不运行ICP，Calibration=null仅RelativeDiagnostic/Publish拒绝，虚拟时间与真实观察分离，原Task/lease/timer与两层Close/root保持；实际构建运行、HALCON/WPF、物理/性能/生产资格未提升。

截至 2026-10-11，完整批准文档范围内可决定的软件设计已经闭合：Core 0.2.0、既有 canonical v1、Simulation-S1 1.0.0、HALCON Adapter 的 H/RuntimeBinding 边界、SurfaceData H/codec 消费桥、Viewport Assembly v0.2 消费桥、两个消费者及其 Owner/失败/回退路径均有唯一落点。本模块没有待由实现者自行补猜的内部设计欠账；尚未通过的项目是执行或外部资格门，不应改写为“设计未闭合”。

实施顺序固定为：

1. 托管 Core 六项规格已接收；实际实现另派明确任务，先绑定权威代码仓库/快照；产品 Contract/Schema/Owner 映射另行串行采纳；
2. 托管 Core 消费 A.2 已接收的 ISurfaceReadPort / ISurfaceLease / IRegistrationBackend / IBackendRun 及所有权；真实适配实现仍另行准入；
3. 获准实现时先做无 UI 的值/输入/域/图校验、刚体组合、质量计算和注入端口下协调/排空，以受控Host stub验证；不在托管 Core 自写Pair/Global视觉求解器；
4. 接入 global 图和两个消费者，建立 Golden/Replay；
5. 在目标 HALCON 26.05/AsunImage 公共桥上完成实际适配与 operator-version 验证；
6. 完成性能/故障/取消/重启证据；
7. 最后接可选 WPF/DevExpress 投影，并完成 UIA、键盘、三语和 1920×1080 验证；
8. 由集成 Owner 串行更新 Manifest、模块目录和引用关系。

以下为产品集成/真实算法切片的后续门，不能笼统阻断附录 A 已定义的纯 Core 与模拟契约测试：

- Contract/Schema/State/Owner 尚未批准；
- 真实 C# 参数类型/重载/封送仍有歧义时，只阻断相应调用适配切片；cv2 全算子能力按用户基线直接使用，不重复审查算子存在性；
- 采样、单位、坐标、质量门、分母或 PerformanceProfile 未绑定；
- Primary/Fallback/Reject 条件不清；
- 需要新增事实 Store、全局对象、产品页面或设备副作用；
- 缺少真实 Golden/Replay 或消费者物理验收值只阻断相应真实算法/产品资格；纯 Core 可用明确标注的合成算例验证数学与生命周期。

后续 Owner 与验收边界固定为：模块实现 Owner 负责 Core/S1 工程、构建、单元/契约/Replay 和资源排空；HALCON Adapter Owner 负责真实 `ImageLibDotNet.Cv2` 封送、worker/Job/IPC、native 数值和取消证据；SurfaceData/Storage Owner 负责 H/codec、format validator、raw bytes/hash 和重新打开；Viewport/WPF Owner 负责 Assembly v0.2、UIA、三语、DPI、晚回调和 1920×1080；集成 Owner 负责 Contract/Schema/State/Owner 采纳、两个真实消费者及 Manifest；Qualification/客户/设备 Owner 负责 Golden/Replay、性能 P50/P95/P99、物理计量、设备/HIL、客户和生产资格。实际代码、构建、真实 HALCON、WPF、性能、Golden/Replay、物理计量和生产放行在各自证据未完成前均保持 `Unverified/Blocked`，不影响本节的设计闭合结论。

文档验收断言：普通开发者只读本页及其权威引用，能够确定职责、端口、输入/输出语义、参数单位/范围/默认处理、同步/异步入口、事件/状态/错误、取消/超时/排空、资源线程、UI 边界、测试和发布回退；任何未确认 API、数值门或业务判定都能定位为 Blocked/Unverified，而不是依赖聊天上下文补充。

## 20. 固定来源、采纳边界与本轮自审

仓库职责/历史消费入口为 [PKG-060](../../shared-modules/packages/PKG-060_Registration3D.md)、[DEV-VIS-028](<../../shared-modules/guidance/03-vision/DEV-VIS-028_3D对象模型、配准与表面分析开发指导.md>)、[FS-014](../../shared-modules/guidance/12-function-specs/FS-014_3D_registration.md)及[独立模块架构](../INDEPENDENT-MODULE-ARCHITECTURE.md)。旧包/旧字段只作责任与迁移映射，本页A.1/A.2是当前唯一模块API；上游平台合同的采纳由主任务串行完成。

### 20.1 HALCON 26.05 与只读实现研究

| 实读来源/固定版本 | 采纳落点 | 强项与限制 |
|---|---|---|
| [pair](../../../halcon算子手册/operators/register_object_model_3d_pair.html)、[global](../../../halcon算子手册/operators/register_object_model_3d_global.html)，项目HALCON26.05手册 | §7.5/7.6 Pair单pose、matching refinement、近初值ICP、Global显式图及重锚、参数/指标区别 | pair score不是概率，global score是充分重叠邻居数；无充分重叠可失败；资料数值精度约点云尺寸0.1%不能变成客户计量保证 |
| [distance](../../../halcon算子手册/operators/distance_object_model_3d.html)、[params](../../../halcon算子手册/operators/get_object_model_3d_params.html)、[copy](../../../halcon算子手册/operators/copy_object_model_3d.html) | §7.6/A.1 私有原始域、显式points/triangles、kd-tree、closest-index、MaxDistance=0、索引闭包 | distance写源属性，非零上限会饱和，auto受属性优先级影响；voxel不能提供此质量路线的closest-index，不能用显示/近似值代替全域门 |
| [sample](../../../halcon算子手册/operators/sample_object_model_3d.html)、[normals](../../../halcon算子手册/operators/surface_normals_object_model_3d.html)、[smooth](../../../halcon算子手册/operators/smooth_object_model_3d.html)、[vector](../../../halcon算子手册/operators/vector_to_hom_mat3d.html) | §7.6 临时fast采样、m/pixel区别、索引/法向来源、只Rigid路线 | accurate重心可丢扩展属性；零法向不能作有效约束；相似/affine算子存在不代表本模块允许吸收形变；采样/法向公共模块责任不复制 |
| [create_matrix](../../../halcon算子手册/operators/create_matrix.html)、[eigenvalues](../../../halcon算子手册/operators/eigenvalues_symmetric_matrix.html)、[clear_matrix](../../../halcon算子手册/operators/clear_matrix.html) | §7.6/A.1 归一化6×6 Gram谱、升序/秩/条件、所有矩阵释放 | 谱只证明局部约束，不证明重复阵列全局唯一；三维点协方差秩不能代替六自由度残差谱 |
| [Open3D固定源码](../../references/open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/pipelines/registration/Registration.cpp)、[Registration测试](../../references/open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/tests/pipelines/registration/Registration.cpp)、[TransformationEstimation测试](../../references/open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/tests/pipelines/registration/TransformationEstimation.cpp)；commit `b6c5e196384ad71e75b6e6f9c5da22d046221f1d` | §7.6/B.1 私有点云、增量左乘、非交换样例、空对应/方向fitness反例 | MIT；C++/Eigen/TBB/fmt等依赖，按固定CMakeLists实际配置，不是本Core运行依赖。源码返回空correspondence时RMSE=0且fitness偏源方向；相关测试有大量DISABLED/NotImplemented，不能当生产充分测试 |
| 同commit [GlobalOptimization源码](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/pipelines/registration/GlobalOptimization.cpp)与[测试](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/tests/pipelines/registration/GlobalOptimization.cpp)，[multiway教程](https://www.open3d.org/docs/release/tutorial/pipelines/multiway_registration.html)为浮动说明页 | §7.6/7.7 图观测边、uncertain闭环、优化/剔不可信边/再优化、参考节点补偿思想 | 已读实际源码和测试，不只README；剔uncertain边后必须重核必需节点/连通，不复制它的成功语义或优化器；测试缺口与上项同样限制。教程非锁定实现/验收证据 |
| [RFC8785](https://www.rfc-editor.org/rfc/rfc8785.txt) §3.2.1/3.2.2/3.2.3；复用项目既有原件与model-assets §9规范研究 | A.2.1 固定DTO array/string/bool/null投影、严格Unicode、转义、UTF8、hash，不引入JCS数字formatter | RFC不定义业务字段/数组集合或身份；double round-trip≠JCS number。本规则故意将double投影为位串字符串，不等同model-core-jcs-v1，也不引用其内部writer/新增通用canonical包 |

原件SHA256（来源变动才重新核，不将改后hash冒充本次实读）：pair HTML `687fdf25a46ad2606477668d2fe83f2d61c384146684394c5e05ef3b92eb3008`；eigenvalues HTML `ed9c17fd393f22017134aa7805e9ac5b394d2d58dacee46a782a4dedcb45e28b`；copy HTML `89e0175b68799a7a22120536903759af2842255defe54183b549b30134aef0ad`；既有RFC原件 `63d52294eb0e3f0014174288186d388b4ddbf2c67d1ce8af1d9726eb0c3ab240`。Open3D按固定commit与本地LICENSE/CMakeLists追溯；本轮不复制源码、不新增来源快照。

AsunControl只读参考保留于 `docs/references/project-snapshots/AsunControl/20261004/original/Vision_CameraCalib/`，只借鉴事件/失败/清理组织，不迁移.NET8 WinForms页面、固定参数或生产语义，不再访问AsunImage内部。ImageLibDotNet/cv2全算子和本机DevExpress25.2.3按用户基线直接使用，不安排安装/授权/封装存在性核验。

### 20.2 DevExpress官方WPF 25.2研究

本轮已通过官方网页读取25.2分支；dxdocs MCP与匹配WPF技能在当前工具列表中不可用，HTTP直取403后使用浏览器官方页面。页面所示最新NuGet patch不覆盖本机25.2.3冻结基线，未下载/替换程序集。具体参考如下，所有采纳只落§12：

- [DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)：LayoutGroup/LayoutPanel、保存/恢复布局；[GridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.GridControl?v=25.2)、[TreeListControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TreeListControl?v=25.2)：ItemsSource、TableView/TreeListView与虚拟化。
- [PropertyGridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.PropertyGrid.PropertyGridControl?v=25.2)：SelectedObject、分组/搜索/编辑；[ChartControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Charts.ChartControl?v=25.2)：XYDiagram2D/Series数据映射，仅残差投影。
- [FlyoutControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Editors.Flyout.FlyoutControl?v=25.2)：真实namespace是Editors.Flyout、程序集Core.v25.2.dll，IsOpen/StaysOpen/PlacementTarget/FlyoutSettings.Placement及动画开关；不能写成Xpf.Core.FlyoutControl。
- [SuperTip](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip?v=25.2)：Items/HeaderItem/Item/Separator、BarItem.SuperTip、普通控件SuperTipControl容器。官方API能说明用法，不证明实际25.2.3编译、UIA、DPI、语言长度、联动/动画或视觉品质已验收。

### 20.3 有限自审与接收界限

按算法/生命周期与外部宿主两个视角，各做一轮定向内容检查并修复本页发现的冲突：Full6估计与平面反例、显式图与独立观测环、原始域分母/三角索引、非终态DrainUnknown、取消完成竞争、公开入口/类型闭包、精确ApiVersion、无循环身份/Receipt预像、校准当前证据/一次应用CAS、未测建议、唯一BCL Exe及UIDetach/权限/语言。随后只做本页链接/结构/旧入口定向检查，不跑全仓审核、不新增过程报告。

本轮只改本DEVELOPMENT-GUIDE.md；19场景、A/B/C契约、测试/性能计划是规格，不是已实现代码。2026-10-10主控已回读0.2.1-prep并接收§19/B.2限定的托管 Core 六项为ModuleCoreImplementationReady；主控用独立字段构造复算855-byte typed投影及SHA256一致。2026-10-11主控已回读C.1～C.6并接收Simulation-S1六项文档规格为ModuleCoreImplementationReady，仅限C.6范围；既有Core测试stub与独立Simulation实现分开，Core公开ApiVersion/canonical仍为0.2.0/既有v1。Simulation-S1实际构建运行/发布、真实HALCON数值/Adapter、WPF、平台集成及现场资格均未授通过。未创建产品工程，未执行C#构建、Core.Tests/BclHost/Simulation.Tests/Simulation.Host、真实HALCON、WPF、性能、Golden/HIL、计量或现场验收。

2026-10-10定向校验结果：本页全部相对链接/锚点存在，标题无重复、代码围栏成对、无冲突标记，C#声明块括号配对；旧成对/成图校验入口、整数版本比较和工程命令占位已消除。A.2.1完整预像实算为855 UTF8 bytes，SHA256与正文固定值一致。上述仅为文档和字节算例检查，不是C#类型编译或产品算法测试。

2026-10-11对Simulation-S1完成两轮有限自审：第一轮修正run相对At、Manifest无循环绑定、factory与Core.Validate职责、timer Infinite/Dispose、快照调度与Release竞争、逻辑预算及自身deadline timer归还；第二轮闭合异常类型、两个Host完整字段/负面Publish/原Owner双Close、脚本顺序/回退与唯一工程。定向复用validate_docs.targets核本页链接，并检查锚点、标题、围栏和声明分隔符；A.2.1原855-byte Golden保持，C.1.1完整192/135/1544-byte预像及hash一致。本模块会话由公开字段独立构造C.3两套正常fixture，复算3570/3816-byte request、12442/13697-byte pack、6124-byte Outcome与预约式，并核对合成变换、measured隔离和G的trace；结果见C.3正文，不新增辅助文件。主控本轮只内容回读接收S1六项规格，未独立重建新pack/fixture各hash，不新增主控复算通过声称。上述只验证规格/字节算例，不声称C#编译、运行测试、真实谱/视觉求解、HALCON/WPF、性能或生产验收通过；本次仅同步S1的ModuleCoreImplementationReady文档规格状态。

2026-10-11本轮补桥自审已核对 [surface-data 0.6.0-prep §17-19](../surface-data/DEVELOPMENT-GUIDE.md) 与 [viewport 0.3.4-prep §10.6-10.9](../viewport/DEVELOPMENT-GUIDE.md)：确认 H1/H2/H3 的 Accuracy、CPU 原值、RuntimeBinding、worker/Job/IPC、取消/清理语义，确认 metadata/raw validator 的版本/hash/有界读取/回退/重新打开语义，确认 Presentation/Lifetime、原 Task/lease、OwnSession、有限 Unbind、晚到 Return、generation/backend generation/authorization 及 `viewport-ui-text/1` 完整三语资源约束。未修改其它模块，未创建代码、测试、报告或新 hash 文件；Core 855-byte Golden 未变，Simulation-S1 新 pack/fixture hash 未由主控独立重算。仅执行本页定向结构/链接/锚点/围栏和 Golden 内容检查，未运行构建、测试、HALCON、WPF、性能、Golden/Replay、HIL、计量或生产验收。

## 附录 A：Module API Contract v0.2（唯一模块契约；待主任务逐切片接收）

0.1 中未定义的 Graph/Evaluate/端口/基础类型及 Create/ToCallerAction 伪 API 由本节替代，不保留第二套 DTO。下列签名与字段形状是独立模块实施规格，不是已生成的产品代码或已编译声明。所有类型置于 `Asun.Modules.Registration3D`，Core 程序集为 Asun.Modules.Registration3D.Core，TFM=net10.0，仅 BCL；ImmutableArray 为不可变数组，default 数组视为非法（optional集合也用 Empty）。字符串 ID/revision/evidence/hash 必须非空，hash 格式为 SHA-256 小写64位；证据 URI 与 hash 分开，禁止把定位 URI 当内容身份。

### A.1 公共类型闭包

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;

namespace Asun.Modules.Registration3D;

public enum LengthUnit { Metre, Millimetre }
public enum RequestKind { Pair, Graph, Evaluate }
public enum RegistrationMethod { Matching, Icp, KnownTransform, Global }
public enum TransformModel { Rigid }
[Flags] public enum DegreesOfFreedom { Tx=1, Ty=2, Tz=4, Rx=8, Ry=16, Rz=32, Full6=63 }
public enum DomainRole { RegistrationSupport, IndependentCheck, MeasuredTarget, Excluded, HaloOnly }
public enum GraphMode { ExplicitEdges, CommonFrame, Previous }
public enum EdgeRole { Solve, CheckOnly }
public enum DistanceTarget { Points, Triangles }
public enum Qualification { NotEvaluated, RelativeDiagnostic, Qualified }
public enum WitnessKind { PointToPlane, UniquePointToPoint }
public enum PairPreset { Fast, Accurate, Robust }
public enum GlobalPreset { Fast, Accurate }
public enum MetricKind { PairOverlapRatio, GlobalNeighborCount }
public enum RegistrationState {
    Ready, Validating, Queued, Running, Cancelling, Draining, DrainUnknown,
    Drained, ResourcesReleased, Completed, Rejected, Blocked, Invalid,
    RecoverableError, Cancelled, TimedOut, Unknown, Closed
}
public enum RegistrationEventKind {
    RequestReceived, Validating, ValidationCompleted, Accepted, Queued, Running,
    Progress, QualityEvaluated, DrainStarted, DrainUnknown, Drained,
    ResourcesReleased, Completed, Rejected, Blocked, Invalid,
    RecoverableError, Cancelled, TimedOut, Closed, Diagnostic
}
public readonly record struct CalculationIdentity(Guid OperationId, string RequestHash);
public sealed record EvidenceRef(string Uri, string Hash);
public sealed record FrameRef(string Id, string Revision);
public sealed record AssetRef(string Id, string Revision, string Hash, EvidenceRef Evidence);
public readonly record struct Point3(double X, double Y, double Z);
public sealed record RigidTransform3D(ImmutableArray<double> RowMajor12);
public sealed record SurfaceRef(string SurfaceId, string Revision, string ContentHash,
    FrameRef Frame, LengthUnit Unit, long ValidPointCount, long TriangleCount,
    EvidenceRef Evidence, EvidenceRef? OrientedNormalEvidence);
public sealed record SurfaceDomainRef(string Id, string Revision, string Hash,
    DomainRole Role, ImmutableArray<long> OriginalIndices);
public sealed record GraphNode(string NodeId, SurfaceRef Surface,
    ImmutableArray<SurfaceDomainRef> Domains, RigidTransform3D? CommonInitial);
public sealed record IdentityCorrespondence(long SourceIndex, long TargetIndex, EvidenceRef Evidence);
public sealed record Hypothesis(string Id, RigidTransform3D? Initial,
    string SourceDomainId, string TargetDomainId, EvidenceRef IdentityEvidence,
    ImmutableArray<IdentityCorrespondence> IdentityPairs);
public sealed record NativePairParameters(PairPreset Preset, double RelativeSampling,
    double KeyPointFraction, int RefinementSteps, int SkippedPoints,
    double AbsoluteCorrespondenceMetres, double SamplingStepMetres, bool InvertSmallerNormals);
public sealed record PairPlan(RegistrationMethod Method,
    ImmutableArray<NativePairParameters> Levels, ImmutableArray<Hypothesis> Hypotheses);
public sealed record GraphEdge(string EdgeId, string FromNode, string ToNode, EdgeRole Role,
    PairPlan? Plan, RigidTransform3D? ObservedTransform, EvidenceRef Observation);
public sealed record NativeGlobalParameters(GlobalPreset Preset, double RelativeSampling,
    int SkippedPoints, int MaxIterations);
public sealed record ResourceBudget(long MaxInputPoints, long MaxWorkingBytes,
    int MaxHandles, int MaxNodes, int MaxEdges, int MaxCandidates,
    int MaxConcurrency, int QueueCapacity, TimeSpan RunTimeout, TimeSpan DrainTimeout);
public sealed record QualityProfileRef(AssetRef Identity, double MinOverlap,
    double CorrespondenceGate, double MaxSupportRms, double MaxSupportDistance,
    double MaxHoldoutRms, double MaxHoldoutDistance, double RankRelativeGate,
    double MaxCondition, double NumericalTolerance, double MaxInitialTranslationChange,
    double MaxInitialRotationChangeRad, double MaxLoopTranslation,
    double MaxLoopRotationRad, double AmbiguityTranslation, double AmbiguityRotationRad,
    int MinCorrespondences, bool RequireLoop, WitnessKind Witness, DistanceTarget DistanceTarget,
    EvidenceRef? DistinctivenessEvidence, AssetRef? Calibration);
public sealed record RegistrationRequest(CalculationIdentity Calculation, string ApiVersion,
    RequestKind Kind, TransformModel Model, DegreesOfFreedom DegreesOfFreedom,
    ImmutableArray<GraphNode> Nodes, ImmutableArray<GraphEdge> Edges,
    PairPlan? Pair, GraphMode GraphMode, string? AnchorNodeId,
    FrameRef TargetFrame, RigidTransform3D? AnchorToTarget,
    RigidTransform3D? KnownTransform, QualityProfileRef QualityProfile,
    NativeGlobalParameters? Global, ResourceBudget Budget, AssetRef RuntimeManifest);
public sealed record RegistrationIssue(string Code, string Field, string DetailKey,
    EvidenceRef? Evidence);
public sealed record ValidationReport(bool IsExecutable, ImmutableArray<RegistrationIssue> Issues);
public sealed record NativeMetric(MetricKind Kind, string ItemId, double Value);
public sealed record NodeTransform(string NodeId, FrameRef Source, FrameRef Target,
    string SourceHash, RigidTransform3D Transform);
public sealed record DistanceSample(long SourceIndex, long? TargetIndex, long? TargetTriangleIndex,
    Point3? ClosestTargetPoint, double? AbsoluteDistance, double? SignedDistance);
public sealed record Correspondence(long SourceIndex, long? TargetIndex, long? TargetTriangleIndex,
    Point3 TransformedSource, Point3 Target, Point3? TargetNormal);
public sealed record DomainWitness(string NodeId, string OtherNodeId, string DomainId,
    bool Reverse, WitnessKind Kind, ImmutableArray<string> TargetDomainIds, long EligibleCount,
    ImmutableArray<DistanceSample> Distances, ImmutableArray<Correspondence> Correspondences,
    ImmutableArray<double> NormalizedGramEigenvalues, EvidenceRef Evidence);
public sealed record EdgeObservation(string EdgeId, RigidTransform3D Transform, EvidenceRef Evidence);
public sealed record NativeCandidate(string HypothesisId, ImmutableArray<NodeTransform> Transforms,
    ImmutableArray<NativeMetric> Metrics, ImmutableArray<DomainWitness> Witnesses,
    ImmutableArray<EdgeObservation> EdgeObservations, string StopReason);
public sealed record PoseCandidate(string HypothesisId, ImmutableArray<NodeTransform> Transforms,
    ImmutableArray<NativeMetric> Metrics, ImmutableArray<QualityEvidence> Quality,
    bool GatesPassed, string? AmbiguityGroup, string StopReason);
public sealed record QualityEvidence(string NodeId, string OtherNodeId, string DomainId, bool Reverse,
    long EligibleCount, long CoveredCount, double? Coverage, double? Rms,
    double? MaxDistance, double? P95Distance, int? Rank, double? Condition,
    bool Passed, EvidenceRef Evidence);
public sealed record GraphEdgeResult(string EdgeId, bool Passed,
    double? TranslationError, double? RotationErrorRad, EvidenceRef Evidence);
public sealed record LoopQualityEvidence(string LoopId, ImmutableArray<string> EdgeIds,
    ImmutableArray<bool> ReverseDirections,
    double TranslationError, double RotationErrorRad, bool Passed, EvidenceRef Evidence);
public sealed record ResourceObservation(bool NativeStopped, bool CallbacksStopped,
    bool ResourcesReleased, long? PeakBytes, int? PeakHandles);
public sealed record RegistrationResult(RegistrationState State, RegistrationRequest Request,
    Qualification Qualification, ImmutableArray<PoseCandidate> Candidates,
    ImmutableArray<NodeTransform> Nodes, ImmutableArray<GraphEdgeResult> Edges,
    ImmutableArray<EdgeObservation> Observations, ImmutableArray<LoopQualityEvidence> Loops,
    ImmutableArray<RegistrationIssue> Issues, ResourceObservation Resources,
    EvidenceRef Receipt);
public sealed record OperationView(CalculationIdentity Calculation, RegistrationState State,
    long Sequence, RegistrationResult? Result, ImmutableArray<RegistrationIssue> Issues,
    ResourceObservation Resources);
public sealed record RegistrationProgress(CalculationIdentity Calculation, long Sequence,
    RegistrationEventKind Kind, string Stage, double? Fraction, RegistrationIssue? Issue);
public sealed record CloseReport(RegistrationState State, bool ResourcesReleased,
    ImmutableArray<OperationView> Outstanding);
public sealed record ApplicationLedger(string TransformId, string NodeId, string SourceHash,
    FrameRef TargetFrame, int ApplicationCount);
public sealed record CalibrationUseEvidence(AssetRef Asset, bool Current, bool Applicable,
    bool Revoked, FrameRef TargetFrame, ImmutableArray<string> SourceHashes, EvidenceRef Evidence);
public sealed record TransformUseContext(ImmutableArray<GraphNode> CurrentNodes,
    FrameRef TargetFrame, AssetRef CurrentProfile, AssetRef CurrentRuntimeManifest,
    CalibrationUseEvidence Calibration, ImmutableArray<ApplicationLedger> Ledger);
public sealed record ReleasedTransformSnapshot(string TransformId, CalculationIdentity Calculation,
    RegistrationRequest RequestBinding,
    ImmutableArray<NodeTransform> Transforms, AssetRef Profile, AssetRef RuntimeManifest,
    AssetRef Calibration, EvidenceRef Receipt);
public sealed record PublishReport(ReleasedTransformSnapshot? Snapshot,
    ImmutableArray<RegistrationIssue> Issues);
public sealed record ParameterRange(double Min, double Max);
public sealed record RecommendationRequest(RegistrationRequest Basis,
    ParameterRange RelativeSampling, ParameterRange KeyPointFraction,
    ParameterRange RefinementSteps, ParameterRange GlobalIterations,
    EvidenceRef SpacingNoiseEvidence);
public sealed record ParameterSuggestion(string Id, NativePairParameters? Pair,
    NativeGlobalParameters? Global);
public sealed record RecommendationReport(CalculationIdentity Basis,
    ImmutableArray<ParameterSuggestion> Suggestions, bool Measured,
    ImmutableArray<RegistrationIssue> Issues);
public sealed record RequestProjectionReport(ImmutableArray<byte> CanonicalBytes,
    string? RequestHash, ImmutableArray<RegistrationIssue> Issues);
public sealed record RequestCreationReport(RegistrationRequest? Request,
    ImmutableArray<RegistrationIssue> Issues);
public sealed record ReceiptPayloadReport(ImmutableArray<byte> CanonicalBytes,
    EvidenceRef? Reference, ImmutableArray<RegistrationIssue> Issues);
public sealed record PointSample(long OriginalIndex, Point3 Position,
    Point3? Normal, ImmutableArray<string> DomainIds);
public sealed record SurfaceChunk(long Offset, ImmutableArray<PointSample> Points, bool IsLast);
public sealed record TriangleSample(long OriginalTriangleIndex, long A, long B, long C,
    ImmutableArray<string> DomainIds);
public sealed record TriangleChunk(long Offset, ImmutableArray<TriangleSample> Triangles, bool IsLast);
public sealed record BackendOutcome(ImmutableArray<NativeCandidate> Candidates,
    ImmutableArray<RegistrationIssue> Issues, bool NativeStopped, bool CallbacksStopped);
public sealed record DrainReport(bool NativeStopped, bool CallbacksStopped,
    ImmutableArray<RegistrationIssue> Issues);
public sealed record RuntimePolicy(ResourceBudget Ceiling, int MaxRetainedCompleted,
    TimeSpan CompletedRetention, string ApiVersion);
```

OperationId不得为Empty，NodeId/EdgeId在请求内唯一；Surface的frame/revision/hash须与lease.Snapshot逐字段一致。正常运行SurfaceChunk不能为空（零点输入预检拒绝），IsLast必须仅出现在末块；末块后不再读取。TriangleCount=0时GetTrianglesAsync(0,...)返回Empty/IsLast=true；非零三角块不允许空或提前末块。点块/三角块都按Offset连续，但OriginalIndex/OriginalTriangleIndex无需连续，必须唯一、非负。输入全部content hash由Surface Owner保证并由宿主公开读端口验证；Core验证实际点/域/索引一致性，不臆测另一个Surface二进制hash规则。

StopReason公开键固定为PoseReturned、GraphReturned、FixedEvaluated；native未提供迭代收敛标志时只用前两键，不能宣称迭代收敛。native无pose或异常走Issue/诊断，不以“默认成功”继续。图基本环固定：按EdgeId ordinal排序，union-find取首个连通生成树；每条非树边与树上唯一返回路径形成一个基本环，按非树EdgeId排序，以非树边From→To为环起始、树路径To→From；ReverseDirections记录边反向，按实际作用顺序左乘累计Ec。Core只做图与刚体代数，不实现第二套视觉图优化。

类型约束是契约的一部分：12项矩阵按 `[r00,r01,r02,tx,r10,r11,r12,ty,r20,r21,r22,tz]`，有效末行固定[0,0,0,1]；正交/行列式/数值容差见 QualityProfile，不用 double.Epsilon 当业务精度。Profile 的所有长度使用 Nodes 的统一 Unit，NativePairParameters 的 AbsoluteCorrespondenceMetres 则显式 m。比例域0<MinOverlap≤1，0<RelativeSampling<1，0<KeyPointFraction≤1，0<RankRelativeGate<1；Steps/Skipped/Iterations/正值预算/MinCorrespondences均正整数，TriangleCount≥0、QueueCapacity≥0；MinCorrespondences≥3，Surface.ValidPointCount>0，Domain.OriginalIndices不可空；所有时间为有限正值，Retention/MaxRetainedCompleted>0；NumericalTolerance>0，MaxCondition≥1，采样/绝对对应距离/CorrespondenceGate 均>0，其余长度/转角上限非负、旋转≤π，必须有限。所有 Id 使用 ordinal 大小写敏感比较。CorrespondenceGate/RMS/Max/闭环门无消费者物理来源时请求只能做诊断，不能从模块默认值补齐 Qualified。

ApiVersion 精确为 "0.2.0"，RuntimePolicy.ApiVersion 同值，不用 int major 与 0.2 比较；其它版本预检 UnsupportedCapability。本 prep 契约尚无已发布生产版本，后续语义变化仍按§17版本纪律。

Pair/Evaluate 固定 Nodes[0]=source、Nodes[1]=target，二者统一 Unit，TargetFrame必须等于Nodes[1].Surface.Frame、AnchorToTarget=null、所有CommonInitial=null、GraphMode=ExplicitEdges；Edges=Empty、AnchorNodeId=null、Global=null。Pair成功输出Nodes恰含源节点原frame→target变换，不新增目标identity观测；Graph成功输出所有节点。Matching/Icp 用 Pair，Evaluate/Pair KnownTransform 用 KnownTransform 且 Pair=null；不能同时提供两个方法。Graph≥2节点、Pair=null、KnownTransform=null，AnchorNodeId 必须存在、AnchorToTarget必填、Global必填；CommonFrame每节点CommonInitial，Previous的Solve边必须恰好N−1条相邻原始frame边并展开为ExplicitEdges，显式图连通才执行。Graph 所有节点必需；每个Solve边的Pair候选须先有唯一通过组，多个组或任何必需边失败整图拒绝，不枚举指数级组合；Global最终候选HypothesisId固定为graph，Obs/Quality仍按EdgeId关联。CheckOnly不传native。ObservedTransform 为原始frame的观测边，不是native增量；CheckOnly 必须 Plan=null、ObservedTransform非空且有独立 Observation；Solve 若 Plan=null 必须有冻结观测；CommonFrame 将每条 Solve 的初值按 CommonInitial_j⁻¹·CommonInitial_i 展开，禁止与 Hypotheses 初值冲突。Previous 的边顺序为 Nodes[i]→Nodes[i+1]，不要求锚点为首节点。Solve边可以以合法ObservedTransform为初值，每条 Solve 边必须有 Plan 或 ObservedTransform；两者可共存但 Plan.Hypotheses.Initial 必须与观测相等，否则冲突拒绝。Pair Levels：matching恰1层，ICP恰coarse/fine两层，Known无层；原始source只在层间通过明确组合表达，不原地累计写回。外部缺新类型/字段时修订本附录，不靠 Schema 猜。

**域与对应完整性。** 每个节点原始索引唯一；所有 Domains.Id 在本节点唯一，每个域 OriginalIndices 严格递增、无重复且均能读回。五种角色在本节点互斥，多个同角色域也不得重叠。Hypothesis.SourceDomainId/TargetDomainId 分别定位 Nodes[0]/[1]（Graph 在该边 From/To）的一个 RegistrationSupport 域，支持多个域通过显式多假设组合，不凭名称选第一个。matching 初值必须 null；ICP 每假设初值必填；Hypotheses.Id 唯一、列表须预先按 ordinal Id 排序（不在 canonical 中悄悄改顺序）。Graph Solve Plan 的 hypothesisId 在 EdgeId 内唯一，结果候选键用 EdgeId/HypothesisId。所有假设必须完整评价，未跑完没有唯一资格。

Pair质量评价每个原始 RegistrationSupport/IndependentCheck 域、每个方向都必须有 DomainWitness；TargetDomainIds 是对端同角色域 ID 的完整 ordinal 有序列表，最近距离限制在该集合，不能用 measured/excluded/halo 点作对应。Hypothesis支撑子集只限定求解，不缩小完整质量分母。EligibleCount等于该原始域有效点数，不能信任 backend 自报；Distances 按 SourceIndex 原索引严格递增、恰覆盖该域一次。原始有效点定义为冻结 Snapshot 已确认的有限点；PointSample.DomainIds须与GraphNode.Domains索引集合严格一致，不能只核计数；后续发现 NaN/丢点/无拓扑不静默删分母，而拒绝 InvalidBackendEvidence。正常距离必须有限非负，最近点字段按下方Points/Triangles分别校验；无对应用null并令门失败，不能用0补空值。QualityEvidence须保留OtherNodeId，不能把图中同一域对不同邻居的质量合并成同名证据。

DistanceTarget.Points 时 TargetIndex 必填、TargetTriangleIndex=null，ClosestTargetPoint等于目标快照该点；Triangles时 TargetIndex=null、TargetTriangleIndex为目标原始三角形索引，ClosestTargetPoint=null（distance算子未输出最近坐标，不能猜一个字段或另写最近三角算法）。TriangleSample.A/B/C是原点索引，不是chunk offset；TriangleCount=0时Triangles路线拒绝。ISurfaceLease.GetTrianglesAsync遵与点块相同连续offset/IsLast规则，数目核对TriangleCount；target面及其顶点只来自 TargetDomainIds，域外跨孔面不能参与。HALCON closest-index按所选目标类型转回对应原始 point/triangle索引，不能拿三角形号当TargetIndex。获取失败/缺映射不标资格。SignedDistance仅在OrientedNormalEvidence与Profile约束已绑定时可存在，unsigned绝对距离仍为全域门依据。

Correspondences的Points模式TargetIndex非空、TargetTriangleIndex=null；Triangles点面模式TargetIndex=null、TargetTriangleIndex非空，Target为该面A顶点（仅定位法向约束平面，不宣称最近点）、TargetNormal为有来源的该面法向。三角域的残差门始终使用HALCON真实点面距离，不以到A顶点距离或无限平面距离代替。UniquePointToPoint限定DistanceTarget.Points，使用冻结标记的目标点索引；法向模型不能混淆。Correspondences仅使用距离≤gate的合法对应，>=MinCorrespondences；TransformedSource与候选T作用原点一致，Target/TargetNormal与目标读回/法向旋转一致，单位统一；正常法向单位化且非零。UniquePointToPoint必须与冻结 Hypothesis.IdentityPairs 一一对应并保留各对应独立身份来源（IdentityPairs包含support及holdout的对应，但holdout项绝不传求解器；按source域角色区分），不能把 nearest-index 当已知标记身份；WitnessKind只声明独立质量模型，不宣称native求解器内部算法。matching 唯一性还需要Profile.DistinctivenessEvidence与各Hypothesis.IdentityEvidence：宿主提供的可辨识证据须独立于本次pose的低RMS，原生单解布尔值不能证明全局唯一，NativeCandidate不设该布尔开关。

Backend按7.6从这些Correspondences构建G并提供6项升序有限谱；Core独立核对点/法向/索引及G的trace与谱和（NumericalTolerance内）、非负容差、秩/条件，再按7.6求质量，不仅信任GatesPassed。真实谱计算经HALCON矩阵算子；纯BCL测试backend只返回明确合成输入的预期谱，不实现视觉优化。6DOF估计需要rank=6；KnownTransform不估计自由度，可用NormalizedGramEigenvalues=Empty，Rank/Condition=null，只评价固定变换、覆盖/留出与外部校准来源，不因无求解谱伪造rank6或强制退化拟合。covariance/迭代数native未提供时不新造输出字段；资源/真实时延走§15独立性能观察，不属于自动Qualified的测量保证。

Graph最终评价按每条请求边（含CheckOnly）及两方向在原域进行，Witness绑定NodeId/OtherNodeId/DomainId；覆盖每个必需节点及其独立检查域，多个邻居不重复累加分母。Graph结果Edges恰包含所有EdgeId，包括失败/CheckOnly；Observations 保存global优化前冻结原frame观测（Solve有Plan时用该Pair结果，CheckOnly用请求观测），不得由最终Ti反构造。Loops按7.6基本环固定构建，保存参与EdgeId及等长ReverseDirections（true为沿反向取逆）、t/θ及证据；RequireLoop=true时每个必需非树闭环须包含至少一条CheckOnly观测；缺独立环拒绝，false且树时Loops=Empty，不填零。Nodes只在整图成功时有全部节点；部分诊断留在Candidates。Core用观测边与Nodes独立计算GraphEdgeResult误差及LoopQualityEvidence门，不把backend Passed当发布依据。

### A.2 端口与入口

```csharp
public interface ISurfaceReadPort {
    ValueTask<ISurfaceLease> AcquireAsync(SurfaceRef surface, CancellationToken cancellationToken);
}
public interface ISurfaceLease : IAsyncDisposable {
    SurfaceRef Snapshot { get; }
    ValueTask<SurfaceChunk> GetChunkAsync(long offset, int maxPoints, CancellationToken cancellationToken);
    ValueTask<TriangleChunk> GetTrianglesAsync(long offset, int maxTriangles, CancellationToken cancellationToken);
}
public interface IRegistrationBackend {
    ValueTask<IBackendRun> StartAsync(RegistrationRequest request,
        ImmutableArray<ISurfaceLease> inputs, IProgress<RegistrationProgress>? diagnostic,
        CancellationToken cancellationToken);
}
public interface IBackendRun {
    Task<BackendOutcome> Completion { get; }
    ValueTask RequestStopAsync();
    ValueTask<DrainReport> DrainAsync(DateTimeOffset deadlineUtc);
    ValueTask<ResourceObservation> ReleaseAsync();
}
public interface IObjectModel3dRegistrar {
    ValidationReport Validate(RegistrationRequest request);
    OperationView RegisterPair(RegistrationRequest request, CancellationToken cancellationToken);
    ValueTask<OperationView> RegisterPairAsync(RegistrationRequest request,
        IProgress<RegistrationProgress>? events, CancellationToken cancellationToken);
    OperationView RegisterGraph(RegistrationRequest request, CancellationToken cancellationToken);
    ValueTask<OperationView> RegisterGraphAsync(RegistrationRequest request,
        IProgress<RegistrationProgress>? events, CancellationToken cancellationToken);
    OperationView EvaluateAlignment(RegistrationRequest request, CancellationToken cancellationToken);
    ValueTask<OperationView> EvaluateAlignmentAsync(RegistrationRequest request,
        IProgress<RegistrationProgress>? events, CancellationToken cancellationToken);
    RecommendationReport RecommendParameters(RecommendationRequest request);
    PublishReport PublishTransform(RegistrationResult result, TransformUseContext context);
    ValidationReport ValidateUse(ReleasedTransformSnapshot snapshot, TransformUseContext context);
    ReceiptPayloadReport GetReceiptPayload(CalculationIdentity calculation);
    OperationView Query(CalculationIdentity calculation);
    ValueTask<OperationView> RequestCancelAsync(CalculationIdentity calculation, DateTimeOffset deadlineUtc);
    ValueTask<CloseReport> CloseAsync(DateTimeOffset deadlineUtc);
}
public static class RegistrationIdentity {
    public static RequestProjectionReport Project(RegistrationRequest draft, int maxCanonicalBytes);
    public static RequestCreationReport Create(Guid operationId, RegistrationRequest draft, int maxCanonicalBytes);
}
```

`ObjectModel3dRegistrar(ISurfaceReadPort surfaces, IRegistrationBackend backend, TimeProvider clock, RuntimePolicy policy)` 为唯一实现构造函数；无默认静态依赖。RuntimePolicy 上限由部署宿主明确给出，每个请求预算不得超过Ceiling；相同实例并发/队列按Ceiling冻结，不能按请求不同值修改正在运行的调度。metadata Validate 无句柄；Acquire取消/异常时Core归还已取得租约。GetChunk maxPoints>0、offset从0到末尾连续、最后offset+count=Snapshot.ValidPointCount，批次上限由工作集预算推导，索引缺口保留OriginalIndex，不能错误要求原始索引连续。StartAsync 返回run前若失败，backend保证其私有资源已归还；做不到时必须返回可查询IBackendRun，不抛出遗失所有权。Completion返回只表示native逻辑计算停止，还需DrainAsync确认callback退出；ReleaseAsync仅在两者确认时调用，重复调用幂等。不以run对象Dispose代替stop证明。Core归还native后再DisposeAsync输入lease，所有阶段异常都保留owner。

接纳顺序唯一：纯metadata/hash校验→在实例锁下检查Closed/OperationId冲突/重复及预算槽→Accepted→必要时Queued→获得执行槽→按Nodes顺序Acquire→实际点/域校验→backend.StartAsync→Running。预检不取得输入租约；Accepted后即使Acquire失败也先归还已持有租约，再发唯一错误终态。请求预算的MaxInputPoints计全部节点有效点数之和，MaxWorkingBytes计同时持有输入/派生/输出/摘要，超上限不偷偷削减支撑域。CloseAsync固定取消所有已接纳未终态operation（不留“等待或取消”给实现者选），然后排空；deadline只限制等待，后台清理继续。CloseReport未排空时State=DrainUnknown、Outstanding保留原operation，全部归还后State=Closed。RequestCancelAsync在未知identity返回REG3D-018，在已终态返回原view（NoEffect是行为、不新增枚举）；重复取消不重启排空。重复提交相同identity只返回Query当前view，不注册新progress订阅或启动第二次任务；活跃客户端以Query追踪。

Backend事件仅作为诊断/进度，Core拥有公开Sequence与接纳/终态；backend不得发公共Completed/ResourcesReleased。Core可与两消费者分别单实例单并发接入，不共享全局当前请求。查询/取消/关闭用同identity，并发安全；Query unknown ID用Issue REG3D-018，不创建operation。结果（成功或仅诊断）只在资源归还后有Result，DrainUnknown.Result=null。请求RunTimeout自Accepted起用TimeProvider单调elapsed（含队列/Acquire/执行/质检）；DrainTimeout自DrainStarted起计，到期仅返回非终态；DateTimeOffset仅为外部截止输入，接纳时转换剩余时长，避免系统时间回拨绕过预算。

#### A.2.1 身份创建与唯一 canonical 规则

公开 helper 是 RegistrationIdentity.Project / Create，不要求宿主先编写 hash 算法。draft.Calculation 可为 default；helper 完全忽略该字段，Create 的 operationId 必须非 Empty。Project 只做有限性/Unicode/枚举/数组和输出预算等投影校验，不替代 Validate 的领域校验；失败 Bytes=Empty、Hash=null。成功 Create 以 OperationId 和所得 hash 替换 Calculation，返回新不可变 request；禁止先拿占位 hash 提交。Validate/接纳均用同一 helper 重算，再核对请求 hash。运行预算只接受不超过 RuntimePolicy.Ceiling，canonical 输出字节计入 MaxWorkingBytes，helper 的 int 上限同时限制完整 byte 数（UTF-8，无 BOM/换行），超限 REG3D-012；不得先序列化无限数据再限额。不能依赖 record/ImmutableArray 的默认引用相等判断重复请求，用 hash 和逐内容比对。

冻结 `registration-request-jcs-v1`，SHA-256 输出小写64位。RFC8785 §3.2 的 JSON 生成规则作用于以下**类型化投影**：该投影只含 array/string/bool/null，不含 JSON number 或 object，故不实现/移植 ECMAScript 浮点 formatter，也不调用 model-assets 内部 writer。不是把普通 serializer 输出当 JCS。

1. 每个 record 投影为声明中构造字段顺序的 array；ImmutableArray 保持请求顺序，default 拒绝、Empty 为 []；nullable 无值为 null，未知字段/派生类型拒绝。RegistrationRequest 单独排除首字段 Calculation，余下字段按 A.1 顺序。请求预像为 `["registration-request-jcs-v1", requestProjection]`；声明字段顺序/新增字段改变必须新规则或精确 API 版本，不能默默增加默认字段。
2. ID/hash/revision/URI/string 原样输出，不归一化 Unicode；enum 输出 A.1 英文成员名，非法枚举拒绝；DegreesOfFreedom 用有效位掩码的十进制字符串。int/long 用 InvariantCulture 十进制字符串（无加号/前导零），TimeSpan 用 Ticks 的同规则字符串。Guid 为小写 D 字符串。bool/null 是 JSON literal。
3. double（含 Point3 和矩阵每项）投影为 `"f64:"+16位小写 IEEE754 binary64 位串`，通过 DoubleToInt64Bits 取得位后以 unsigned X16 再转小写；NaN/Inf 拒绝，+0/-0统一正零位串。不经过文化、R/round-trip、decimal或JSON number转换；保留其它有限位值，不按质量容差量化。语义矩阵比较可用 Profile 容差，身份字节不能用容差比较。
4. 字符串按 RFC8785 §3.2.2.2：quote/backslash转义，b/t/n/f/r短转义，其它 U+0000–001F用小写\u00xx；slash/HTML/非ASCII原样，拒绝孤立 surrogate；无空白/末尾换行。writer 为固定 DTO 有界 traversal，不提供任意 JSON/parser 或开放对象反射入口。日期不在请求字段中；外部 Close/Cancel deadline 不进入 request hash。
5. helper 与接纳使用同一 Core 私有 writer；BCL SHA256 与 UTF8Encoding(false,true)。没有第三方运行依赖。Record 嵌套深度由固定类型闭包确定；所有 collection 长度、string UTF8字节与最终输出都计工作集，在遍历/追加前检查上限。

Golden byte 示例（不是生产点云）：Point3(1,+0,-0) → `["f64:3ff0000000000000","f64:0000000000000000","f64:0000000000000000"]`；FrameRef("源\nA","r1") → `["源\nA","r1"]`（预像内是反斜线 n 两字符）；TimeSpan.FromTicks(10) → `"10"`；DegreesOfFreedom.Full6 → `"63"`；Int64.MaxValue → `"9223372036854775807"`。正负零请求 hash 相同；1 与 BitIncrement(1) hash 不同；交换域/节点/边顺序 hash 改变；换 OperationId、取消等待 deadline 不改 RequestHash。B.1须比较整个请求 expected UTF8 bytes（按上面的固定字段次序）及 SHA，而不能只测再次序列化相等。旧0.1未声明规则只作诊断，不重算旧身份。

完整投影Golden（仅测试Project，不是可执行请求）：ApiVersion=0.2.0、Kind=Evaluate、Rigid/Full6；Nodes/Edges=Empty、Pair=null、GraphMode=ExplicitEdges、Anchor=null、TargetFrame=(F,r)、AnchorToTarget/KnownTransform=null；QualityProfile.Identity与RuntimeManifest均为AssetRef(a,r,64个0,EvidenceRef(e,64个0))，15个double字段全为1、MinCorrespondences=3、RequireLoop=false、Witness=PointToPlane、DistanceTarget=Points、最后两引用null；Budget依声明顺序为1,1,1,1,1,1,1,0,TimeSpan(1tick),TimeSpan(1tick)。这些值故意不满足领域执行条件，Validate必须拒绝，Project仍可验证封闭类型的字节。以下单行无末尾换行，共855 UTF8 bytes，SHA256=`6323c4974460692db216eca194dfc8cb553c41ccf5476d792724ea81e1c5d429`：

```json
["registration-request-jcs-v1",["0.2.0","Evaluate","Rigid","63",[],[],null,"ExplicitEdges",null,["F","r"],null,null,[["a","r","0000000000000000000000000000000000000000000000000000000000000000",["e","0000000000000000000000000000000000000000000000000000000000000000"]],"f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","3",false,"PointToPlane","Points",null,null],null,["1","1","1","1","1","1","1","0","1","1"],["a","r","0000000000000000000000000000000000000000000000000000000000000000",["e","0000000000000000000000000000000000000000000000000000000000000000"]]]]
```

#### A.2.2 Receipt、发布与一次应用

Core 在终态、资源已归还后生成 Receipt 预像 `["registration-receipt-jcs-v1", calculationProjection, resultProjectionWithoutReceipt]`，各字段按 A.1 record 顺序投影，RegistrationResult.Request 仍使用排除 Calculation 的 requestProjection，Calculation 在外层唯一出现。包含 State/Qualification/Candidates/Nodes/Edges/Observations/Loops/Issues/Resources；排除 Receipt 自身与 URI，不能循环求 hash。EvidenceRef.Hash为该预像 UTF8 的 SHA256，URI=`registration-receipt:<OperationId小写D>`。GetReceiptPayload 返回这份可保存的完整预像 bytes/Reference；无Result/已淘汰时返回 Issue，无假摘要。宿主按 URI 留存 bytes 与 hash，再绑定其证据存储引用；Core 不自动写文件/DB。已接纳且资源归还的Rejected/RecoverableError可有仅诊断RegistrationResult/Receipt（Qualification=NotEvaluated、Nodes=Empty、Candidates保留），其State必须等于operation终态；预检Invalid/Blocked和Cancelled/TimedOut无Result，仅OperationView/Issues。所有失败均不可发布消费快照。

PublishTransform 仅接受本实例仍保留的 Completed.Result，按完整内容及 receipt 复算比对，拒绝反序列化/篡改结果（需要时以原请求新 identity Replay）。Result.State=Completed、Qualification=Qualified、Resources 三确认、节点齐全、质量/留出/歧义/必要闭环都通过后，再用 context 校验当前输入/Profile/Manifest 和 calibration。CalibrationUseEvidence由宿主从标定资产 Owner 的公开适用性解析取得；Current=true、Applicable=true、Revoked=false、TargetFrame相等、SourceHashes覆盖全部输出节点，Asset必须与请求 QualityProfile.Calibration 完整相等。模块不自行推断资产物理有效性；宿主不能从本结果布尔值造该外部证据。当前 revision 改变不修改原已完成 Receipt，只拒绝当前用途。

TransformId=SHA256(`["registration-transform-jcs-v1", RequestHash, NodesProjection, QualityProfile.IdentityProjection, RuntimeManifestProjection, CalibrationAssetProjection]`)；节点顺序按请求，矩阵按 f64 规则，含源/目标 frame与源hash，排除 OperationId、elapsed、峰值资源、URI以及 TransformId 本身。两个新 operation 使用相同内容和相同最终变换可得相同 TransformId；不同结果矩阵不能沿旧 TransformId。ReleasedTransformSnapshot 的 Receipt 保留原回执，不替代其输入/校准引用。

ValidateUse 为无 I/O 的同步纯校验：复算 TransformId，核 Nodes 对 currentNodes 的 NodeId/SurfaceId/revision/hash/frame/unit、当前 TargetFrame/Profile/Manifest、CalibrationUseEvidence，检查 context.Ledger 仅允许合法非负计数、无重复 (TransformId,NodeId,SourceHash,TargetFrame) 键。任何输出 source 对应 count≥1 拒绝 AlreadyApplied；不存在该键等价未应用（0），但宿主必须从权威账本读取，不能丢弃历史条目。Snapshot.RequestBinding 保留完整冻结请求：ValidateUse重算其RequestHash并要求与Calculation一致，由此核对 unit/revision/域资格；不得只看 TransformId 字符串。纯摘要能证明内容一致，不能证明发布者可信；宿主必须接受本实例 PublishReport 或校验已留存的原 Receipt bytes和来源，不把外部任意自填快照视为已批准。发布的纯校验不消耗应用次数。实际注入时宿主在同一个版本/CAS或串行事务内重新核校准/当前输入并登记一次应用，再调用下游；并发失败保留原账本，结果未知由宿主对账，不把未确认注入计数清零重试。

Qualification的确定顺序：请求/证据缺失→NotEvaluated；质量门明确失败→Rejected且NotEvaluated；全部算法/留出/可观测性/唯一性通过但QualityProfile.Calibration=null→Completed/RelativeDiagnostic；全部通过且有绑定Calibration资产→Completed/Qualified（只对绑定asset和input成立，实际current/applicable由Publish/ValidateUse的宿主证据另核）。KnownTransform不做可观测性估计，但固定矩阵/双向/留出/域来源同样必查。BCL合成Fixture即使演练Qualified分支也明确Synthetic，不构成真实资产/计量资格，不能注入生产。异常/取消/超时和任何DrainUnknown不可Qualified。

OperationView保留至CompletedRetention，最多MaxRetainedCompleted；只能淘汰已终态且资源归还的 operation，未排空永不淘汰。容量不足拒绝接纳，不无界保存墓碑。Query 不存在/已淘汰用 REG3D-018（State=Unknown 是无此实例内结果的观察，不冒充原执行状态）；未丢进程但排空不明使用 DrainUnknown。跨进程对账只由宿主保存的 Receipt 完成，不恢复 native句柄。Publish/ValidateUse/GetReceiptPayload不启动 backend。RecommendParameters.Measured 永远 false：本入口只生成最多27/9组未测建议；测量由宿主逐个新 identity Replay，审批后新 Profile，不能自行把 bool 置 true。

### A.3 规范错误与三语投影

REG3D-001～016保持§9.3键语义；新增键如下，DetailKey由宿主提供zh-CN/zh-TW/en-US资源，Core不拼产品句子、不暴露native英文异常给操作员：

| 键 | 状态/含义 | 允许恢复 |
|---|---|---|
| REG3D-017 IdentityConflict | Invalid；相同OperationId不同hash | 新identity，不覆盖原operation |
| REG3D-018 OperationNotFound | Query Issue；无此operation或已过保留期 | 查询宿主Receipt，禁止自动提交 |
| REG3D-019 StaleResult | Rejected；绑定输入/Profile/calibration变化 | 新快照/new identity |
| REG3D-020 DrainUnknown | 非终态；native/callback/释放未证实 | 隔离、Query原operation，禁止释放/复跑 |
| REG3D-021 InstanceClosed | Blocked；关闭后新提交 | 新建独立实例，先确认旧实例资源 |
| REG3D-022 AlreadyApplied | 发布/宿主注入校验拒绝 | 使用原始source与新合法变换链，不能把计数清零 |
| REG3D-023 UnqualifiedTransform | 发布拒绝；门/留出/身份或calibration缺失 | 补资格证据再新identity计算 |
| REG3D-024 UnsupportedModel | Blocked；非刚体或非Full6估计 | 选择现有合法路线，不删自由度伪装 |
| REG3D-025 CallbackFailure | Diagnostic；进度订阅器异常 | 重新订阅/Query，原计算继续 |
| REG3D-026 InvalidBackendEvidence | Rejected；方向/索引/分母/谱/资源证据非法 | 修适配器后新identity，保存原错误 |
| REG3D-027 RecommendationStale | 建议拒绝；绑定键变化 | 重新离线建议，不更改活动Profile |

### A.4 独立交付与后续适配落点

Core/API在同一Core工程内，逻辑Contracts层不要求新建空DLL。后续正式需要时才拆Contracts包且保持namespace/major。候选独立适配工程固定 `src/Modules/registration-3d/Asun.Modules.Registration3D.Halcon/Asun.Modules.Registration3D.Halcon.csproj`（net10.0），可选UI固定 `.../Asun.Modules.Registration3D.Wpf/Asun.Modules.Registration3D.Wpf.csproj`（net10.0-windows，UseWPF=true）；其测试分别在 `tests/Modules/registration-3d/Asun.Modules.Registration3D.Halcon.Tests/` 与 `Asun.Modules.Registration3D.Wpf.Tests/`，创建须获明确实现切片授权，本任务不创建。

**唯一正式 Core.Tests** 固定 `tests/Modules/registration-3d/Asun.Modules.Registration3D.Core.Tests/Asun.Modules.Registration3D.Core.Tests.csproj`；SDK=Microsoft.NET.Sdk、TargetFramework=net10.0、OutputType=Exe，仅ProjectReference本模块Core并使用.NET BCL，无PackageReference、无待选测试框架；namespace为Asun.Modules.Registration3D.Core.Tests。入口执行B.1及§14绑定的全部适用Core/Contract/Simulator必需断言，按确定CaseId输出expected/actual及完成状态；不以只编译/不抛异常/仅跑BclHost代替正式测试。任一必需断言失败、跳过、未完成、超时或cleanup未确认均非零，列出CaseId；全部完成且资源已确认才exit0。真实HALCON/WPF/性能/现场项不属于PureCore suite，按原后续门明示，不把它们作为Core跳过项伪报通过。

**唯一独立消费者 BclHost** 保留 `tests/Modules/registration-3d/Asun.Modules.Registration3D.BclHost/Asun.Modules.Registration3D.BclHost.csproj`，TFM=net10.0、OutputType=Exe、无PackageReference，仅ProjectReference本模块Core；namespace为Asun.Modules.Registration3D.BclHost。IntegrationHost和ComparisonHost是该一个Exe里的两个mode，不另建第二Exe；这是两个真实独立消费者的接入计划，当前Synthetic演练不证明生产集成，BclHost不代替正式Core.Tests。WPF视口从宿主注入公开视图/选中事件，不内建viewport/ROI/计量引擎或修改测量工作台边界。

获准实施后，从仓库根运行以下唯一明确命令（当前工程未创建，未执行）：

```powershell
dotnet build src/Modules/registration-3d/Asun.Modules.Registration3D.Core/Asun.Modules.Registration3D.Core.csproj -c Release
dotnet run --project tests/Modules/registration-3d/Asun.Modules.Registration3D.Core.Tests/Asun.Modules.Registration3D.Core.Tests.csproj -c Release
dotnet run --project tests/Modules/registration-3d/Asun.Modules.Registration3D.BclHost/Asun.Modules.Registration3D.BclHost.csproj -c Release -- --mode integration --fixture core-normal
dotnet run --project tests/Modules/registration-3d/Asun.Modules.Registration3D.BclHost/Asun.Modules.Registration3D.BclHost.csproj -c Release -- --mode comparison --fixture measured-domain
```

**测试真实期限冻结**：每个case真实wall上限10s（含业务和finally，最后2s独立预留给cleanup观察）、完整suite真实wall上限120s、外进程wall上限180s。正常suite按B.1表序及§14适用ID顺序执行，只有指定并发case最多2实例；新case开始前须有至少10s剩余suite时间，否则记未完成/非零，不补造成功。业务最多占前8s，正常提前结束也立即进入独立2s cleanup预算；cleanup观察不能挪用业务Token。ManualTimeProvider/ITimer只驱动Core的虚拟RunTimeout/DrainTimeout和可控制闩锁，不能驱动10/120/180s保护。真实wall由BCL Stopwatch/GetTimestamp及TimeProvider.System观测；业务取消或虚拟时钟推进均不能取消finally清理。单case超时仍执行§8.1的独立cleanup并保留未归还Owner；case记失败后不再启动同槽新实例，原监督循环继续观察至归还或suite/外层期限。

外进程保护不另建测试项目/脚本：Core.Tests和BclHost各自同一Exe的默认入口为BCL Process监督父进程，启动同一已构建assembly的一个suite/mode worker（内部参数分别为`--suite-worker`或`--mode-worker`），使用ProcessStartInfo.ArgumentList传参、重定向输出并持续排空，保留原Process与WaitForExitAsync Task。从worker启动起用真实wall计180s，worker内自计suite120s及case10s；编译时间不计入worker期限，构建错误仍非零。父进程收齐stdout/stderr及退出码，必需case清单不完整、worker非零或未结束一律非零，不接受仅打印PASS后卡死。worker在120s时若仍有强持槽，记录suite失败/未确认并停新业务，继续由原Host持有至释放或外层失败隔离。父进程为退出/输出排空预留最后2s：worker未结束则真实wall178s开始终止该Synthetic worker进程树，在剩余预算内观察退出/输出；180s为硬上限，不无限等待管道或另延长期限，保留未确认及CaseId并非零。父进程最外层真实wall保护覆盖其输出观察/异常finally，到硬上限仍不能结束则由该测试进程硬失败终止；这是Synthetic进程失败隔离，不是Close/ResourcesReleased证据，不能计作断言通过。两个期限均不借用虚拟时钟。

BclHost两个mode都先按§8.1预留强持槽，再构造内存SurfaceReadPort、ScriptedBackend、BCL ManualTimeProvider/ITimer和registrar，按Create→Validate→异步计算→GetReceiptPayload→Publish/ValidateUse→宿主模拟注入→独立finally Close串行运行；两个mode各自应用上述10/120/180s保护。fixture在该工程内固定，不读取产品配置/DB/设备；core-normal验证非交换变换、事件/排空/一次应用，measured-domain验证定位域与被测域分离和同Core第二消费者，二者同时覆盖§8.1异常路径。输出expected/actual与错误键到stdout，所有必需动作/断言完成且Owner归还才exit0，失败/跳过/未完成exit1、参数非法exit2；finally之后且无未确认强持槽才允许返回，外层失败保护另记非零。标明Synthetic，不称实测生产合格。Core.Tests和BclHost都不需要测试框架依赖；HALCON/WPF使用各自适用验证并明确目标运行时，不复用Core测试结果冒充。以上是执行计划，没有工程创建/运行通过声明。

包分别为Core、Halcon、Wpf，新增Simulation独立包落点/发布规则见C.5；只引用Core可运行本Host内部stub，独立Simulation需显式引用Simulation包，不以stub冒充可发布后端。发布保留API版本、已测Replay索引、符号/错误资源键、预算/benchmark、原版本回退；HALCON/WPF包使用本机用户确定依赖，不安装/授权/版本准入复审。回退保持原receipt/canonical规则，新版本不能静默用旧算法结果填新门。

## 附录 B：逐能力实施验证与六项准备结论

### B.1 可执行测试和两个消费者

正式测试放入A.4唯一Core.Tests BCL Exe；CaseId取本表第一列完整场景名（包含R3D-H编号时取该编号），§14用既定R3D编号；每case可含有限子断言，case/suite/外进程期限10/120/180s按A.4冻结。表中的坐标/阈值是**合成数学/控制流fixture**，只用于断言，不是客户精度、物理门或生产Profile。每fixture冻结Manifest/Profile/request hash，操作及期望自动比对；故障后检查事件Sequence、资源Owner和publish拒绝，不能只断言不抛异常。BclHost独立运行两个消费者任务及其异常演练，不作为正式测试工程。故障注入时Host的预期非零与正式测试case结果分开：只有完整观察到预期错误、finally和资源/强持断言才可判该case通过；意外卡死/超期/未完成仍使正式suite非零，不能把未观察到的行为写成预期失败已通过。

| 场景/能力 | 输入与操作 | 可判定输出 |
|---|---|---|
| Pair正常/非交换组合 | source={0,e1,e2,e3}；T0=绕Z90°，Δ=沿X平移1；模拟backend给原frame最终Δ·T0及完整双向/留出 | 点e1映射(1,1,0)，不是(0,2,0)；原source不变，终态前ResourcesReleased |
| 单次应用/固定评价 | 原p=(1,0,0)，T平移(1,0,0)；Evaluate一次，ledger count=1后再次注入 | 评价点为(2,0,0)，不为(3,0,0)；第二次AlreadyApplied；Evaluate重复不写ledger |
| 空/非法/大负载 | empty points，NaN/Inf，重复OriginalIndex，Budget.MaxInputPoints+1、MaxNodes/Edges+1，queue满 | native调用0；Invalid/ResourceLimit；拒绝路径不发Accepted |
| score/覆盖不同 | native Pair score=2，eligible=10、covered=6 | score保持2且coverage=.6；不拒绝score>1，不当confidence |
| 双向/遮挡/外点 | 10source均可对应、target仅1/10可对应；另全域含远外点、inlier RMS很小 | 双向coverage门失败；外点在原分母/全域RMS，不能删掉 |
| 平面/共线/弱几何 | 平面point-plane谱rank3；唯一平面标记point-point非共线谱rank6；共线point-point有零特征值 | 第一个/第三个拒绝可观测性；第二个不因共面一律拒绝；重复阵列仍可能Ambiguous |
| 多候选/参数变化 | 2不同Hypothesis均通过留出；sameId改Pair level/hash | AmbiguousSolution不可publish；IdentityConflict不第二次native；新ID保留原结果 |
| Global正常 | 3node冻结A→B→C和A→C观测，锚点非identity，CheckOnly边不送native | Ui重锚后Ta精确恢复；闭环按观测边检验；all Nodes/Edges完整 |
| 闭环反例/部分成功 | 所有优化后Ti一致但独立A→C观测错；失败桥边使图分裂 | IndependentLoop失败，不用Ti恒等闭环掩盖；Graph拒绝、Nodes不伪造全部 |
| 原域/留出泄漏 | IndependentCheck index与RegistrationSupport重叠；normal=0；采样丢source index | 预检/运行校验拒绝；无资格快照 |
| Cancel/Timeout/late | BCL ManualTimeProvider（TimeProvider/ITimer 的测试实现）及可控制 native/callback 退出的 backend；各阶段cancel、deadline、late generation | native/callback退出且资源归还后才终态；排空未确认DrainUnknown无Result，迟到不改终态 |
| 并发/断连/关闭 | 两实例同snapshot不同Profile；断开progress；Close deadline早于native退出；重复Close | 源属性hash不变；按instance预算背压；CallbackFailure不丢清理；旧实例隔离、可Query、资源归还后Closed |
| receipt/publish/版本 | 篡改Result，stale revision/calibration撤销；ApiVersion 非精确 0.2.0；旧0.1无canonical | Publish拒绝，原receipt不覆盖；兼容矩阵拒绝/诊断，不猜字段 |
| 推荐/训练边界 | candidate interval无交集，已有建议但Profile改变，Global请求robust，create_shape_model训练意图 | InvalidInput/RecommendationStale/UnsupportedCapability；生产参数不变 |
| 第二消费者 | IntegrationHost注入snapshot后模拟重建接口；ComparisonHost只用独立定位域然后模拟metrology消费 | IM-032不直接调用registrar；比较工具被测目标不参与支撑；两者Core结果/事件完全同源 |
| R3D-H01 Host正常/构造门 | 两个Host分别预留槽→构造立即留存→Create/Validate/Register/Publish/消费→独立finally Close；另先占满槽并尝试构造 | 槽满时构造/工厂/backend启动次数均0；正常两个Host原Task/identity可核回，全部归还后才清槽/exit0；BclHost演练与正式Core.Tests断言分别执行 |
| R3D-H02 Host业务/事件异常 | 两个Host分别在Register同步/异步、Publish或消费处抛错，events抛错；业务Token已取消或虚拟时钟已超期 | 每个已构造实例仍执行独立cleanup；业务与cleanup错误各自保留，事件异常不越过Core终态语义；finally前不能返回0，原业务Task异常被观察，不替换实例 |
| R3D-H03 Host Close在途/迟到 | Close原Task超过独立2s观察预算；backend闩锁保持native/callback/租约未归还，随后在case真实10s内放行；同时模拟转交拒绝；注入clock固定UTC=2020-01-01T00:00:00Z且不同于SystemUTC | 原Close及最终确认Close传入deadline均为各次模块clock当前UTC+2s，首个固定例恰为2020-01-01T00:00:02Z；虚拟clock不推进时外层System真实wall观察仍至多2s，不能因UTC差值延长期限；包装等待超时未取消底层Close；原Host进程根槽持续强持registrar、原Task/身份/端口；拒绝转交不清槽、不dispose、不新建；放行后观察同一原Task并确认归还，finally之后返回非零且保留超时错误 |
| R3D-H04 Close异常/双错 | 业务已抛错后Close同步调用或原CloseTask再抛错；后台随后按可控脚本恢复排空 | 两份错误不覆盖；Close异常不等于ResourcesReleased，原Owner留存原Task；Query原identity并按§8.1确认实例关闭后才释放槽；未确认不退出Main |
| R3D-H05 有限正式测试保护 | case必需子断言失败/跳过/未完成；虚拟时钟暂停或迅速推进；worker持续不释放或同步卡死 | 任一必需缺失非零并列CaseId；10/120/180s只用真实wall，先有限finally/强持，suite到期停新任务仍保留Owner；外进程终止记录未确认/非零、不伪造Close成功；全部必需清单与资源确认才exit0 |
| 长稳/缓存/资源 | 冻结运行周期，交错异常/取消/队列压力；确认不跨 operation 缓存；Retention容量达到上限 | 每个已完成资源归零、unknown单列，预算受限；未排空不被淘汰、缓存stale不重用 |

真实HALCON验收另用同一批几何标准/实采Surface：明确无初值matching、已近似ICP、full-resolution对照、coarse/fine、相同几何不同颜色、重复阵列、噪声/遮挡/正常及退化、Global三种关系输入、全域/留出/闭环；评估误接受/误拒绝、实际位姿误差、可靠拒识、端到端及峰值资源。未获得真实样本和Profile门时只记录NotEvaluated，不能宣称最快/合格。Pair/global手册记载数值精度约受point-cloud尺寸0.1%限制；不换算成用户计量保证，也不以缩小云坐标单位“提高精度”。

### B.2 BenchmarkProfile 与准入接收

模块专属维度/测点见§15，统计口径唯一引用 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)。计划先分别运行纯Core校验/图/质量组装/模拟排空，再运行真实HALCON Pair/Graph/固定质量、最后WPF投影；冷热、点/节点/边/假设数、ROI层数、法向/拓扑、重叠与退化、租约/句柄/峰值bytes、队列/取消/排空均入桶。缺时延目标仅NotEvaluated，不阻断冻结的纯Core合成测试；资源/deadline上限是运行必填，不能缺失后无界执行。

| DEV-GOV-010 §3.1 六项 | 本轮可定位准备 | 尚影响的切片/接收状态 |
|---|---|---|
| 1 边界与第二消费者 | §1/2/18；IM-033Owner，宿主组合、IM-032无直接依赖、ComparisonHost | 托管 Core 规格已接收；批准模块边界保持，真实消费者集成未验收 |
| 2 精确公开契约 | 附录A全类型/入口/端口/资源/错误/单位/canonical；§7.6数学 | 托管 Core 规格已接收；855-byte typed投影由主控独立复算一致，ApiVersion=0.2.0；未编译/未验证HALCON数值 |
| 3 独立最小宿主 | §8/A.2/A.4 BclHost两mode、Core BCL、注入端口及Host内stub | 托管 Core/受控Host规格已接收；不是独立可发布Simulator准入，真实HALCON/Adapter与集成门保持 |
| 4 正常/故障/并发/关闭/版本 | §7.4/7.7/8.1/9/10/B.1；Core.Tests BCL Exe、10/120/180s、异常finally及原Host强持断言 | 托管 Core 规格已接收；Close deadline用注入clock、真实wall用System，H03覆盖UTC不一致反例；未执行测试/长稳 |
| 5 Benchmark | §15/B.2及DEV-GOV-010统计；Profile阈值来源明确 | 托管 Core 测量方法/规格已接收；真实性能/物理目标待消费者Profile，结果NotEvaluated，不授达标 |
| 6 工程/路径/最小顺序/后续门 | Core binding/A.4，代码、正式BCL测试、BclHost、Halcon、Wpf唯一位置 | 托管 Core 规格已接收；本轮只改指导，代码仓库/快照与实际实现任务另绑定；真实Adapter/WPF/平台/现场门保持 |

2026-10-10主控已接收§19限定的托管 Core 六项为`ModuleCoreImplementationReady`，仅规格准备；2026-10-11另回读C.1～C.6，接收独立Simulation-S1六项文档规格为`ModuleCoreImplementationReady`，范围及六项状态见C.6。整模块仍为`DesignReview / Prep`，HALCON数值/Adapter、WPF、平台集成及现场切片仍为`PreparationIncomplete`，不授整模块`ImplementationSpecificationReady`或已实现/测试/生产资格。ScriptedBackend及ManualTimeProvider只为原受控Host内stub；S1是独立纯托管脚本Simulator/factory/pack/Clock/有限资源及两个Synthetic Host，显式BackendOutcome不运行ICP，Calibration=null只作RelativeDiagnostic/Publish拒绝；虚拟时间/真实观察、原Task/lease/timer和两层Close/root不变。实际构建/运行/性能/包发布仍待验证，主控本轮未独立重建新pack/fixture各hash。客户物理质量门/calibration适用域/真实精度及节拍仅影响相应资格切片，不撤销已接收Core/S1规格；本轮不创建工程或启动代码实现。


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

## 附录 C：Simulation-S1 独立模拟后端交付规格（ModuleCoreImplementationReady，仅文档规格）

### C.1 职责、消费者与唯一公开装配

现有架构“视觉核心、模拟后端和HALCON适配端口”包含本模块，§18两消费者分别需要离线验证原始域/候选消费和停止/恢复链。Simulation-S1只重放有限合成Surface、显式BackendOutcome、诊断及逻辑资源动作，通过Core已有ISurfaceReadPort/IRegistrationBackend端口注入；不调用HALCON、不求最近距离/ICP/Global/谱、不生成随机物理真值、不学习/推荐生产参数、不写产品事实。调用方仍使用已接收的ObjectModel3dRegistrar和质量门。首版仅在同一进程由显式Advance驱动，不后台按真实时钟跑、不读取文件/DB/环境变量/网络、不支持无限脚本或任意委托执行；不内置配方/工艺/设备控制。

命名空间`Asun.Modules.Registration3D.Simulation`，引用Core namespace及System/Collections.Immutable/Threading/Tasks。所有集合ImmutableArray、default非法；构造只存值，实际校验在factory完成。封闭enum按固定英文名，未知值拒绝。本节新类型不写入Core程序集，不改A.1/A.2 API。SimulationSession无公开构造；公开factory是唯一装配入口，返回失败时Session=null且无Task/timer/租约已经启动；Advance/Signal也不得暗创建session。

```csharp
public enum SimulationActionKind {
    Progress, Complete, FailCompletion, CallbacksStopped, PermitRelease, FailReleaseOnce
}
public enum SimulationRunState { Running, CompletionPublished, CallbacksStopped, Released }
public sealed record SimulationDomainDraft(string Id, string Revision, DomainRole Role,
    ImmutableArray<long> OriginalIndices);
public sealed record SimulationSurfaceDraft(string Id, string Revision, FrameRef Frame,
    LengthUnit Unit, ImmutableArray<PointSample> Points,
    ImmutableArray<TriangleSample> Triangles, ImmutableArray<SimulationDomainDraft> Domains);
public sealed record SimulationSurface(GraphNode Node, ImmutableArray<PointSample> Points,
    ImmutableArray<TriangleSample> Triangles);
public sealed record SimulationSurfaceReport(SimulationSurface? Surface,
    ImmutableArray<RegistrationIssue> Issues);
public sealed record SimulationAction(int Sequence, TimeSpan At, string? Gate,
    SimulationActionKind Kind, string Stage, double? Fraction,
    BackendOutcome? Outcome, RegistrationIssue? Issue);
public sealed record SimulationScript(string Id, string Revision,
    RegistrationRequest ExpectedRequest, ImmutableArray<SimulationAction> Actions,
    long ReservedBytes, int LogicalHandles);
public sealed record SimulationPack(string ApiVersion, string Id, string Revision,
    string Hash, ImmutableArray<SimulationSurface> Surfaces,
    ImmutableArray<SimulationScript> Scripts, EvidenceRef Provenance);
public sealed record SimulationOptions(int MaxSources, int MaxScripts, int MaxActionsPerScript,
    int MaxRuns, int MaxConcurrentRuns, int MaxLeases, int MaxTimers, int MaxGates,
    int MaxPointChunk, int MaxTriangleChunk, long MaxResidentBytes, int MaxLogicalHandles,
    int MaxCanonicalBytes, TimeSpan MaxVirtualDuration, int MaxDispatchPerAdvance);
public sealed record SimulationCreateReport(SimulationSession? Session,
    ImmutableArray<RegistrationIssue> Issues);
public sealed record SimulationDigestReport(ImmutableArray<byte> CanonicalBytes,
    string? Hash, ImmutableArray<RegistrationIssue> Issues);
public sealed record SimulationRunView(CalculationIdentity Calculation, string ScriptId,
    TimeSpan StartElapsed, SimulationRunState State, bool StopRequested, bool NativeStopped,
    bool CallbacksStopped, bool Released, long ReservedBytes, int LogicalHandles);
public sealed record SimulationObservation(string PackHash, TimeSpan Elapsed,
    int StartedRuns, int ActiveRuns, int ActiveLeases, int ActiveTimers,
    long ReservedBytes, int LogicalHandles, ImmutableArray<SimulationRunView> Runs);
public sealed record SimulationStepReport(TimeSpan Elapsed, int Dispatched,
    SimulationObservation Observation, ImmutableArray<RegistrationIssue> Issues);
public sealed record SimulationCloseReport(bool Closed, bool ResourcesReleased,
    SimulationObservation Observation, ImmutableArray<RegistrationIssue> Issues);
public sealed class SimulationRunException : Exception {
    public SimulationRunException(RegistrationIssue issue);
    public RegistrationIssue Issue { get; }
}
public static class RegistrationSimulationFactory {
    public static SimulationSurfaceReport CreateSurface(string nodeId,
        SimulationSurfaceDraft draft, SimulationOptions options);
    public static SimulationDigestReport ProjectPack(SimulationPack draft, SimulationOptions options);
    public static SimulationCreateReport Create(SimulationPack pack, SimulationOptions options,
        DateTimeOffset initialUtc);
}
public sealed class SimulationSession {
    public ISurfaceReadPort Surfaces { get; }
    public IRegistrationBackend Backend { get; }
    public TimeProvider Clock { get; }
    public SimulationObservation Query();
    public SimulationStepReport Advance(TimeSpan delta);
    public SimulationStepReport Signal(CalculationIdentity calculation, string gate);
    public ValueTask<SimulationCloseReport> CloseAsync(DateTimeOffset deadlineUtc);
}
```

Factory的Surface/Create失败分别返回Surface/Session=null、Issues非空，成功Issues=Empty；Digest失败CanonicalBytes=Empty/Hash=null，成功给完整bytes/hash。Query返回不可变一致观察，不启动/释放资源。Step拒绝预检时Dispatched=0、Elapsed/Observation保留原状态；回调已经执行后捕获错误则返回实际Dispatched和继续排空后的观察，不能报告回滚。Close未确认给当前Observation/明确Issue，不把未知计数填0；成功Closed/ResourcesReleased同时true、Issues=Empty。以上仅是公开签名规格，代码块不作为已有可编译实现。

Options所有int/long/TimeSpan为有限正值；MaxConcurrentRuns≤MaxRuns、MaxCanonicalBytes≤MaxResidentBytes、所有值由调用方显式传入，无CPU/环境默认。MaxRuns是本session终生实际StartAsync次数（释放后不回补），保留所有已启动run观察至session关闭，禁止无限墓碑。MaxLeases限制并存Acquire，MaxTimers限制Clock创建的未归还timer（禁用timer仍占槽，Dispose后在途回调退出前仍占槽）。MaxGates限制pack全部不同(scriptId,gate)键；每个run只存有限对应gate bool，不建立外部队列。Point/TriangleChunk是单次读上限；MaxResidentBytes是C.2定义的逻辑预约上限，同时测实际managed分配，不能用逻辑上限保证实际堆内存。逻辑handles只表示脚本资源，不称native句柄。

CreateSurface按A.1点/域/三角约束核对并复制不可变内容，点必须按OriginalIndex严格递增，DomainIds与Draft.Domains的OriginalIndices双向核对、无重复成员，TriangleIndex递增、顶点均在点表；同一索引/域角色冲突或未声明DomainId拒绝，不自动删点/补法向。域数组/域成员顺序纳入摘要，indices严格递增；不按hash自动重排。NodeId显式传入且非空，CommonInitial=null。来源强制Synthetic：SurfaceRef.Evidence.Uri=`registration-sim:surface:<Id>`；OrientedNormalEvidence=null，signed距离首版不支持。Surface.ContentHash=SHA256(`["registration-sim-surface-v1",draftProjection]`)，SurfaceRef保留Id/Revision/Frame/Unit，ValidPointCount/TriangleCount分别等于Points/Triangles实际长度；每个Domain.Hash=SHA256(`["registration-sim-domain-v1",surfaceHash,domainDraftProjection]`)；Evidence.Hash=surfaceHash。CreateSurface不生成法向或物理标定资产，只生成本包有限合成值的身份。不得把真实source hash重写为模拟身份后当实采来源。

ProjectPack忽略draft.Hash及Provenance自身（避免循环），预像固定`["registration-sim-pack-v1",ApiVersion,Id,Revision,SurfacesProjection,ScriptsProjection]`；SimulationSurface.Node含已生成source/domain身份，scripts包含完整ExpectedRequest（沿A.2.1排除Calculation，直接嵌入RegistrationRequest字段数组，不额外包Core request-rule标签）、所有action/Outcome/预约参数。嵌套A.1及C.1 record均按构造字段序array/string/bool/null、double f64位串、整数/TimeSpan ticks字符串、严格Unicode/无BOM规则；Simulation writer在本包独立实现这一固定类型投影，不访问Core私有writer、不提供通用JCS或JSON解析器。ProjectPack只做封闭类型投影、有限性/Unicode/枚举/default集合/输出预算核对，不承担执行准入，允许投影完整但领域不可执行的Golden。Create再做包结构、来源/hash和预算核对，以RegistrationIdentity.Project复算每个RequestHash；Core领域Validate由装配后的Host调用、接纳时Core再校验，不构造临时registrar或复制第二套领域validator。任何投影规则变动须新rule/Simulation API，不用容差合并hash。ProjectPack失败CanonicalBytes=Empty/Hash=null，预算先检查再追加，整体超MaxCanonicalBytes拒绝。

装配顺序为CreateSurface→宿主构造带该Node/域的完整request→RegistrationIdentity.Create→显式动作/Outcome脚本→ProjectPack（draft.Hash可空、Provenance忽略）→用`with`填入Hash及EvidenceRef(`registration-sim:pack:<Id>`,Hash)→Create。Create精确要求SimulationPack.ApiVersion="1.0.0"、ExpectedRequest.ApiVersion="0.2.0"、Hash/Provenance相符，每个脚本完整hash可核回、来源URI为registration-sim、ExpectedRequest.QualityProfile.Calibration=null；options及initialUtc不纳入pack内容身份，根Owner分别保存原options与initialUtc供交付观察。Create要求至少一个Surface和Script、唯一NodeId/SurfaceId/Script.Id，重算每个source/domain内容身份并核请求引用与pack严格一致；不接纳占位身份或缺少来源的包。相同Id/revision而内容hash改变是新pack，绝不在session内替换；Create后无Load/Update/Reset/latest入口。Profile/Manifest/Evidence为Synthetic命名空间（URI前缀registration-sim:），RuntimeManifest.Hash绑定独立模拟后端版本证据，PackHash另绑定本次脚本/输入；不能以HALCON Manifest冒充模拟，不反引用PackHash，避免请求→脚本→pack→Manifest循环。

Factory对Outcome作类型/有限性/长度/原索引存在/方向/合法谱基本核对；一致但门失败的显式残差/退化候选允许作为故障fixture，最终质量仍由Core重新验证。首版不允许NaN/未知索引伪装成正常后端；用FailCompletion/Issue注入错误。所有Outcome.NativeStopped必须true，CallbacksStopped必须false，最终CallbacksStopped由后续资源动作证明；signed距离=null。点点Witness必须有冻结IdentityPairs；Graph观测和环仍由Core按原契约验证，不由模拟器“自动成功”。脚本的Synthetic可辨识证据只证明fixture已指定映射，不证明真实物理唯一性。Calibration=null故Core输出最多RelativeDiagnostic/NotEvaluated；Simulation不返回ReleasedTransformSnapshot，两个Host的Publish应拒绝，不能生成生产配准资格。

#### C.1.1 完整字节 Golden（投影断言，非可执行配准）

三个预像均由本节公开字段独立构造，以下单行UTF8无BOM/末尾换行，不仅比较单个成员hash。SurfaceDraft=(x,r,Frame(F,r),Metre)，一个PointSample=(0,Point3(1,+0,-0),null,[d])，Triangles=Empty、DomainDraft=(d,r,RegistrationSupport,[0])，nodeId=n。完整surface预像192 bytes，SHA256=`dac116eb0e7fa5f811649b0e9a92dd29eb0809fb9a1c578fbcff34548df8b421`：

```json
["registration-sim-surface-v1",["x","r",["F","r"],"Metre",[["0",["f64:3ff0000000000000","f64:0000000000000000","f64:0000000000000000"],null,["d"]]],[],[["d","r","RegistrationSupport",["0"]]]]]
```

完整domain预像135 bytes，SHA256=`f66cecc724862c9d100e6338ea4af91757e48776bf55d061b5cee0c36c6c6adc`：

```json
["registration-sim-domain-v1","dac116eb0e7fa5f811649b0e9a92dd29eb0809fb9a1c578fbcff34548df8b421",["d","r","RegistrationSupport",["0"]]]
```

完整Pack=(1.0.0,p,r,Hash忽略,[上述SimulationSurface],[Script(s,r,ExpectedRequest,Actions,65536,1)],Provenance忽略)。ExpectedRequest逐字段取A.2.1完整855-byte Golden中定义的DTO（不是把其JSON当运行输入），Calculation任意；Actions三项均At=0/Gate=null/Fraction=null/Issue=null，Stage对应Simulation.Complete/Simulation.CallbacksStopped/Simulation.PermitRelease，只有Complete携带BackendOutcome(Empty,Empty,true,false)。完整pack预像1544 bytes，SHA256=`9150b1e810e85e3693d32516621bd9271fca3685e6ce568afeea7f859b0e6049`：

```json
["registration-sim-pack-v1","1.0.0","p","r",[[["n",["x","r","dac116eb0e7fa5f811649b0e9a92dd29eb0809fb9a1c578fbcff34548df8b421",["F","r"],"Metre","1","0",["registration-sim:surface:x","dac116eb0e7fa5f811649b0e9a92dd29eb0809fb9a1c578fbcff34548df8b421"],null],[["d","r","f66cecc724862c9d100e6338ea4af91757e48776bf55d061b5cee0c36c6c6adc","RegistrationSupport",["0"]]],null],[["0",["f64:3ff0000000000000","f64:0000000000000000","f64:0000000000000000"],null,["d"]]],[]]],[["s","r",["0.2.0","Evaluate","Rigid","63",[],[],null,"ExplicitEdges",null,["F","r"],null,null,[["a","r","0000000000000000000000000000000000000000000000000000000000000000",["e","0000000000000000000000000000000000000000000000000000000000000000"]],"f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","f64:3ff0000000000000","3",false,"PointToPlane","Points",null,null],null,["1","1","1","1","1","1","1","0","1","1"],["a","r","0000000000000000000000000000000000000000000000000000000000000000",["e","0000000000000000000000000000000000000000000000000000000000000000"]]],[["1","0",null,"Complete","Simulation.Complete",null,[[],[],true,false],null],["2","0",null,"CallbacksStopped","Simulation.CallbacksStopped",null,null,null],["3","0",null,"PermitRelease","Simulation.PermitRelease",null,null,null]],"65536","1"]]]
```

ProjectPack允许该完整封闭类型算例；Create必须因ExpectedRequest来源/节点/hash不满足装配拒绝，Core.Validate也拒绝空Nodes，不能启动run。这里一个点不证明可观测性，数值/两个Host正常路径使用C.3的完整fixture。未知API可投影为字符串但Create拒绝，不新增rule选择参数或兼容Load入口。此Golden只验证字节协议，不算C#运行测试或算法验收。

### C.2 有限脚本执行、Clock、失效与资源动作

**逻辑预约的唯一计数模型。** P为完整ProjectPack预像UTF8字节数，G为pack任一script不同非null gate数的最大值。Create先checked核`BaseBytes=2*P+512+MaxRuns*(256+64*G)+MaxLeases*(128+128*MaxPointChunk+64*MaxTriangleChunk)+128*MaxTimers+32*MaxDispatchPerAdvance`≤MaxResidentBytes，再建立session；2P分别代表冻结payload和值摘要字节，固定槽cost是本模拟规则的逻辑计数，不等于CLR对象布局。所有槽在BaseBytes预留：run/墓碑/gate、lease及每lease一个有界读批次、timer、dispatch快照；Acquire/CreateTimer再核数量不重复加bytes。每script.ReservedBytes≥512+该Complete的BackendOutcome完整typed投影UTF8字节数（FailCompletion改用Issue投影），Start原子核`BaseBytes+所有未Release run.ReservedBytes+本次ReservedBytes`及逻辑handles总量≤各上限。ReservedBytes由调用方显式给定，不自动放大或遗漏输出；Create已核每script单次预约至少能装入总预算。中间投影缓冲须在MaxCanonicalBytes内先计数再追加，checked溢出是拒绝不是wrap。Query.ReservedBytes报告此总量，Release只减原run预约；BaseBytes到session真正Closed才归还。宿主持有返回chunk/Outcome/Task的实际内存与进程总堆另外测量，不以本逻辑模型冒充硬managed上限；相应调用/输出都有有限长度，但宿主无限缓存不在session内存保证内。Lease不并发读同实例，重复Dispose幂等，chunk返回后的消费所有权由借用者负责，不得原地改写不可变数组。

脚本不是程序：Actions数量3..MaxActionsPerScript，Sequence恰从1递增、At非负非递减且最后At≤MaxVirtualDuration；At相对该run成功接纳时的StartElapsed，到期值=StartElapsed+At，相同At按Sequence执行。Start前checked核每个到期值≤session.MaxVirtualDuration，越界无预约拒绝。Stage固定非空诊断key，Progress的Fraction可null或[0,1]且Outcome/Issue=null；其它Kind.Fraction=null。Gate仅null表示无闩锁，空字符串拒绝，非空名称为本script内ordinal字符串，有限键由pack固定；Signal仅放行已启动原run的这个已声明gate，不创建新gate/新任务。每script恰一Complete或FailCompletion，后者Issue.Code必须为REG3D-015且Outcome=null，前者Outcome非空/Issue=null；此前只能Progress，其后允许有限Progress（模拟native已停但回调迟到），再恰一CallbacksStopped、可选一个FailReleaseOnce、最后恰一PermitRelease；CallbacksStopped后禁止Progress，PermitRelease前无资源释放。资源动作的Fraction/Outcome/Issue均null，Complete/Fail不能同时给结果和错误。无显式Complete/排空/释放动作就拒绝pack，不预设单位阵或“finally全归零”。

每个ExpectedRequest.Calculation.RequestHash至多匹配一个script；多个script同hash即歧义拒绝，不依赖列表首项或OperationId碰运气。StartAsync先核Calculation非Empty且hash可重算、完整请求与脚本投影一致、所有传入lease未Dispose且属于同session、Snapshot/数量/顺序严格匹配request.Nodes；无匹配REG3DS-004，不consume运行槽、不开run。图脚本一次给明确的最终候选/优化前观测，不在Simulation重放隐含Pair组合/运行视觉算法。相同内容的新OperationId可重放同一script一次并consume另一个MaxRuns；本session同OperationId（即使改hash）再次直调Backend拒绝REG3DS-005（Core正常幂等提交不会二次Start）。Start返回IBackendRun前原子预约run/工作集/逻辑handles并登记唯一Owner，不能分配失败后抛出遗失run；失败前未预约或已完整回滚，无资源逃逸。所有Async入口ValueTask按A.2转存原Task一次。

AcquireAsync用exact SurfaceRef逐字段匹配冻结pack（非latest）；创建只读lease并预约MaxLeases，每lease只实现A.2读端口，无隐藏窗口。offset是顺序批次位置，OriginalIndex仍保留；maxPoints/maxTriangles必须1..options相应上限，offset必须0..count，offset=count可返回Empty/IsLast=true且重复读确定同值，不削减为默认值。offset>count/负值拒绝REG3DS-001；读是无游标纯值访问，可回读，不要求消费者私有递增状态。已Dispose后读拒绝，DisposeAsync幂等、归还该lease一次；session后台run只借用Core持有lease，不自行dispose输入。session开始Close后拒绝新Acquire/Start，但已有lease读/Advance/Signal/Query和原run清理保持可用。断连UI/宿主事件异常不会换输入/脚本；异步事件异常遵Core CallbackFailure，模拟器仍推进排空。

虚拟时间只通过`Advance(delta)`推进：delta≥0，Elapsed+delta≤MaxVirtualDuration，否则不改变时钟/动作，返回Issue；Advance(0)处理当前已到期动作。Clock由session创建，初始UTC为Create显式initialUtc，Timestamp初始0、TimestampFrequency=TimeSpan.TicksPerSecond；GetUtcNow=initialUtc+Elapsed，GetTimestamp=Elapsed.Ticks，不受SystemUTC/本机时区影响。Clock.LocalTimeZone=UTC；Create须核initialUtc.Offset=0且initialUtc+MaxVirtualDuration不溢出，advance加法仍checked。Clock.Override CreateTimer提供BCL ITimer给Core/Task.Delay，不返回System定时器；due只能Timeout.InfiniteTimeSpan（-1ms，即-10000ticks）或≥0，period只能Infinite或>0，period=0在本模拟子集拒绝，不宣称支持全部System timer行为。due=0在下一次Advance(0)/Advance时触发。不因timer到期自动快进到未来。Change是重新设到期/周期，已Dispose返回false；同步Dispose幂等禁止新回调但不等待自己，在途回调退出前ActiveTimers仍含该槽，DisposeAsync才等待退出。回调内不得同步阻塞等待自身DisposeAsync；异步观察由原Owner负责。禁用timer仍占槽；Clock不是独立公开可构造ManualTimeProvider。

Advance/Signal在一个session有一个串行dispatch Owner，并发或回调重入调用拒绝REG3DS-006而不改状态。入口在锁内冻结本次可到期timer generation及各run顺序可执行动作快照，按到期Elapsed、类别（timer先于script）、timer创建序或run接纳序/Sequence稳定排序；periodic错过多期按每期逐次处理，不能悄悄合并。先数学计算周期数并checked汇总，≤MaxDispatchPerAdvance才材质化有界快照、提交新Elapsed/Signal gate；超限时连gate都不放行，时间/动作/timer不变，可更小delta恢复。dispatch期间CreateTimer/Change及新Start不加入本次快照，最早下一次Advance处理；Change/Dispose使该timer旧generation快照项跳过，排序不重写。Advance先把Clock设为目标Elapsed，所有回调读取同一目标时间，排序到期值只控制派发顺序；回调中新due相对目标Elapsed。闩锁只阻塞本run下一动作及后续，不阻塞其它run/timer；Signal只执行该run已到期/已开闩动作，不调度timer、不改变时间。重复Signal已放行gate为NoEffect（空Issues/Dispatched=0）；未知run/gate拒绝，原Released run的已知gate同样NoEffect。回调在锁外同步调用；timer/diagnostic回调抛错捕获为本次Step的REG3D-025并继续余下有限快照，不回滚已执行动作或跳过排空，run.CallbacksStopped只能在本run在途回调实际归零后确认。Dispatched计实际尝试执行项，skipped项不计。同步dispatch完成不保证Core异步continuation已跑完，Host须有限等待/Query原Task后再推进，不以Advance(0)忙循环代替等待。

Complete将冻结Outcome发布到同一IBackendRun.Completion（RunContinuationsAsynchronously），逻辑NativeStopped=true、State=CompletionPublished；FailCompletion将同一Completion置SimulationRunException（Issue.Code=REG3D-015），同样确认本模拟native逻辑停止。Progress只对Start借入的diagnostic同步调用Report，RegistrationProgress.Calculation为原Calculation、Sequence取Action.Sequence、Kind=Progress、Stage/Fraction取动作、Issue=null；diagnostic=null仍消费动作，不新建订阅器。CallbacksStopped动作确认本run全部Report调用已经返回、以后不再Report，State=CallbacksStopped；消费者用Progress<T>另投递的外部continuation仍由消费者/Core自己的回调Owner排空，Simulation不冒充能确认外部队列退出。RequestStopAsync只幂等置StopRequested=true，不越过脚本闩锁、不伪造NativeStopped/释放；取消与完成竞争继续由Core已冻结规则决定。资源停止标志是脚本控制流观察，不是真实HALCON停止证据。DrainAsync将同Clock deadline在调用时转换为有限剩余duration；负/零返回当前DrainReport，不取消后台；期限到达仍false，后台等待CallbacksStopped继续。Clock固定不推进时该虚拟等待可不完成，Host真实2s观察和原Owner强持仍按§8.1执行。

PermitRelease只设置释放许可；IBackendRun.ReleaseAsync在当前dispatch退出后才判NativeStopped/CallbacksStopped/许可，三项均true才释放预约工作集/逻辑handles，State=Released、ActiveRuns减1，返回ResourcesReleased=true；否则返回false及REG3DS-008，不clear在用资源。dispatch在途调用Release时异步等该次dispatch退出，每run最多一个原ReleaseTask、重复调用返回同一个；不能同步阻塞回调等待它。这样同次Complete/CallbacksStopped/PermitRelease不会因Core continuation抢先运行而随机出现false。FailReleaseOnce设置一次释放故障，首次许可后的Release返回false/REG3D-015并保留预约，原Task完成后下一次同run Release可幂等完成；不引入自动重试或新run。Core在backend释放后才归还输入lease。released run继续保留有限墓碑，Completion仍是同一已完成Task、不能换成空Outcome；临时工作数组可释放，原Task/冻结payload仍按原Owner/预算保留。Query只含RunView，StartedRuns为终生数、ActiveRuns为尚未Release数。逻辑PeakBytes/PeakHandles取本run.ReservedBytes/LogicalHandles（本run观察）和session总预约高水位（benchmark），明确Synthetic，不能用其0当实测资源峰值。

Session.CloseAsync用于包Owner停止接纳/请求各run停止并等待资源归还，**不越权替Core调用run.Release/lease.Dispose**；deadline用session.Clock.GetUtcNow+duration生成，等待到期返回Closed=false/ResourcesReleased=false/REG3DS-008，原session仍Closing、Advance/Signal继续可用。同一Close进程内不resetElapsed/更换端口；同报告后可再次有限查询/幂等Close最终确认。Drain/Close只各保留一个在途等待：重复调用以首次deadline返回同一原Task（包装ValueTask），完成后才可重新有限调用；不把无限并发等待藏在有限timer外。模拟器自己建立的deadline timer仍占MaxTimers，由原等待Owner在完成/到期/异常路径finally Dispose；判断借用资源归还时排除当前自身Close timer，报告返回前仍须归还它和在途回调。只有run已Release、lease归零、全部借用timer已Dispose且无dispatch/回调在途，才可结束Close；结束时释放包值与已预留槽，最终观察ReservedBytes=0/LogicalHandles=0/ActiveRuns=0/ActiveLeases=0/ActiveTimers=0。关闭不为证明归零而强行Dispose Core仍持有timer，保留有限RunView/原Task观察所需身份；没有外部资源被冒充native句柄。Closed后的Query仍可读最终观察，其他动作拒绝REG3DS-007。session没有IDisposable快捷入口，Host必须按C.4确认Close后清Owner。

| Simulation错误键 | 语义/状态 | 恢复动作 |
|---|---|---|
| REG3DS-001 InvalidScript | Factory/读/Advance拒绝；字段、序列、来源/身份、范围、timer参数错误 | 更正明确输入，新pack/session；错误自身不释放旧Owner |
| REG3DS-002 VersionUnsupported | 仅支持Simulation1.0.0/Core0.2.0 | 使用匹配包，不自动兼容未知脚本 |
| REG3DS-003 CapacityExceeded | factory/run/lease/timer/dispatch总量超限 | 无部分预约；原任务继续，确认已释放再重建有界新session |
| REG3DS-004 ScriptNotFound | request hash/内容/lease不匹配 | 新正确快照/请求，不换latest/首个脚本 |
| REG3DS-005 DuplicateRun | 同OperationId再次直接Start | Query原run，不再次消耗脚本/任务 |
| REG3DS-006 ReentrantDispatch | Advance/Signal重入或并发调用 | 等原dispatch退出再调用，不改时钟 |
| REG3DS-007 SessionClosing | 新输入/Start在Closing/Closed；Closed后的控制操作 | 保留原session清理，确认归还后另建 |
| REG3DS-008 ReleaseUnconfirmed | native/callback/许可/租约/timer未归还 | Signal/Advance按原脚本排空、Query/原Task观察，不强制clear |

SimulationRunException为本包sealed Exception，唯一公开构造`SimulationRunException(RegistrationIssue issue)`和只读`Issue`属性；无需调用方查内部异常类型。后端/lease无Report可返回的失败分别Fault ValueTask/Completion为该异常，Core按原NativeFailure路径清理，Issue.Code保留原REG3DS键为诊断；System cancellation token在接纳前取消返回OperationCanceledException，无预约。timer.CreateTimer无法返回报告时同样抛该异常而不占槽。资源/Step/Factory/Close有Report的入口用Issue不抛领域错误；编程错误/不可恢复运行时异常仍由Host独立cleanup保留，不靠异常自动释放。错误DetailKey=`Simulation.<键名>`，由宿主三语映射，如“脚本不匹配/腳本不符/Script mismatch”“释放未确认/釋放未確認/Release unconfirmed”；Core错误码/状态不重命名。

### C.3 首版双消费者的完整合成算例

Simulation包不内置FixtureFactory或样例生成算法；以下构造规则由C.5两个Host各自的固定fixture输入落实，使用C.1公开CreateSurface/ProjectPack/Create装配。所有身份/URI均为Synthetic。该算例只检验控制链/公开装配，不证明真实配准正确性/精度。正式测试可逐字段复算，不能用私有Create方法或缺失DTO补完整性。

**共用几何和身份。** source的support原索引0..3依次为(1,1,1)、(1,-1,-1)、(-1,1,-1)、(-1,-1,1)，holdout原索引4..7为前四点各加(10,0,0)，单位Metre。两个域Id为support/check、revision=r1、对应DomainRole RegistrationSupport/IndependentCheck。每PointSample.Normal=null，DomainIds分别单项support/check，Triangles=Empty，OrientedNormalEvidence=null。T固定为绕Z正90°后沿X平移1，RowMajor12=`[0,-1,0,1,1,0,0,0,0,0,1,0]`。target原索引同source并由这个**已声明固定刚体代数**变换得到，不求最近邻，不新增视觉算法。FrameRef source=(S,r1)、target=(T,r1)；nodeId=s/t、SurfaceDraft.Id=source/target、revision=r1、CommonInitial=null。CreateSurface按C.1填合法SurfaceHash/DomainHash并返回GraphNode，两个完整lease原点数8。

ComparisonHost另在source索引8..11放与support同四个点各加(20,0,0)，DomainIds=measured、Role=MeasuredTarget；target的8..11为固定T作用该点再加(0,0,0.2)，该差值只保留在被测域，绝不纳入对应/质量/求解。两节点的measured域都固定，Points=12；在OutputView只投影原始measured点和T，不计算/宣布产品尺寸结论。IntegrationHost不含measured，消费Completed/RelativeDiagnostic结果作为离线整合演练的只读叠加，不直接调用IM-032/不注入生产重建。两个Host都调用PublishTransform并断言因Calibration缺失拒绝Snapshot，不能为演练成功造校准资产。

**完整请求字段。** 两个Host各自使用OperationId=Guid.Parse("00000000-0000-0000-0000-000000000101") / 尾值102。ApiVersion="0.2.0"、Kind=Pair、Model=Rigid、DOF=Full6、Nodes为上述source/target、Edges=Empty、GraphMode=ExplicitEdges、AnchorNodeId/AnchorToTarget/KnownTransform/Global=null、TargetFrame=(T,r1)。Pair.Method=Icp，Levels恰两项：Preset=Accurate、RelativeSampling=.05、KeyPointFraction=.3、RefinementSteps=5、SkippedPoints=2、AbsoluteCorrespondenceMetres=.1、SamplingStepMetres分别.2/.1、InvertSmallerNormals=false。一个Hypothesis.Id=h1、Initial=T、SourceDomainId/TargetDomainId=support、IdentityPairs完整包含0..7同原索引匹配（measured不含），每对Evidence为Synthetic。两层没有模拟native迭代，脚本直接给原frame最终T，Initial已近似/恰等于T是声明输入，不是隐含单位阵。

QualityProfile字段按A.1全部填写：Identity=(qp,r1,profileHash,Synthetic Evidence)，MinOverlap=1、CorrespondenceGate=.001、MaxSupportRms/Distance=.001、MaxHoldoutRms/Distance=.001、RankRelativeGate=1e-8、MaxCondition=100、NumericalTolerance=1e-10、MaxInitialTranslationChange=1、MaxInitialRotationChangeRad=.1、MaxLoopTranslation=.001、MaxLoopRotationRad=.01、AmbiguityTranslation=.001、AmbiguityRotationRad=.01、MinCorrespondences=3、RequireLoop=false、Witness=UniquePointToPoint、DistanceTarget=Points、DistinctivenessEvidence=Synthetic fixture映射证据、Calibration=null。RuntimeManifest=(sim-backend-1,r1,versionHash,Synthetic Evidence)；versionHash固定SHA256 UTF8字面文本`registration-simulation/1.0.0`，profileHash固定SHA256 UTF8 `registration-simulation/fixture-profile-r1`；对应AssetRef.Evidence.Hash各等于自身Hash，Uri为`registration-sim:version:1`/`registration-sim:profile:r1`。correspondenceHash=SHA256 UTF8 `registration-simulation/fixture-correspondence-r1`用于Hypothesis.IdentityEvidence/每个IdentityCorrespondence/Distinctiveness/Witness，Uri分别`registration-sim:hypothesis:h1`、`registration-sim:correspondence:<index>`、`registration-sim:distinctiveness:r1`、`registration-sim:witness:<node>:<domain>`。版本/Profile文本标识仅是本fixture来源，不是生产Profile内容摘要或物理证书。

Budget按A.1为MaxInputPoints=64、MaxWorkingBytes=16777216、MaxHandles=8、MaxNodes=4、MaxEdges=8、MaxCandidates=8、MaxConcurrency=1、QueueCapacity=0、RunTimeout=30s、DrainTimeout=2s；RuntimePolicy.Ceiling同Budget、MaxRetainedCompleted=8、CompletedRetention=60s、ApiVersion=0.2.0。先RegistrationIdentity.Create生成完整RequestHash，然后构造脚本，Pack身份不反写到Request。Options全部显式：MaxSources=4、MaxScripts=8、MaxActionsPerScript=16、MaxRuns=8、MaxConcurrentRuns=1、MaxLeases=4、MaxTimers=32、MaxGates=16、MaxPointChunk=64、MaxTriangleChunk=64、MaxResidentBytes=16777216、MaxLogicalHandles=8、MaxCanonicalBytes=1048576、MaxVirtualDuration=60s、MaxDispatchPerAdvance=256。初始UTC=2020-01-01T00:00:00Z。Factory MaxResident同时预约canonical与冻结输入，不因 fixture小而省限额。

**显式BackendOutcome。** 恰一个NativeCandidate.HypothesisId=h1、Transforms仅NodeTransform(s,(S,r1),(T,r1),source.ContentHash,T)、Metrics一项NativeMetric(PairOverlapRatio,h1,2)、StopReason=PoseReturned、EdgeObservations=Empty；Issues=Empty、NativeStopped=true、CallbacksStopped=false。Witnesses恰四项，固定顺序为(s,t,support,false)、(s,t,check,false)、(t,s,support,true)、(t,s,check,true)，Reverse=false/true表示source→target/target→source；DomainId为support/check、TargetDomainIds单项相同Id、EligibleCount=4、Kind=UniquePointToPoint。Distances/Correspondences按该域原索引递增，全部对应目标同索引、TargetTriangleIndex=null、ClosestTargetPoint为对端原点、AbsoluteDistance=0、SignedDistance=null；Correspondence.TransformedSource在对端frame（正向T、反向T⁻¹）、Target为对端该原点、TargetNormal=null，声明IdentityPairs可核回。四组对应分别中心化后支撑包围盒对角长度sqrt(12)，NormalizedGramEigenvalues均为`[1/6,1/6,1/6,1,1,1]`（1/6按binary64最近舍入，位串3fc5555555555555）；G的平移谱为1、旋转谱1/6，trace=3.5、condition=6、rank6，误差0是合成T已指定的数学结果，不是测量。Witness Evidence用Synthetic Uri `registration-sim:witness:<node>:<domain>`及correspondenceHash。Comparison measured点不出现在这四Witnesses中；域数组固定support/check/measured顺序，support/check原点索引各递增。

**正常脚本与预期。** Script.Id=normal、revision=r1，ExpectedRequest为各Host request，ReservedBytes=65536、LogicalHandles=1；Actions恰三项：Sequence1/At=1s/Gate=null/Complete/Stage=Simulation.Complete/Outcome上述/Issue=null；Sequence2/At=1s/Gate=null/CallbacksStopped/Stage=Simulation.CallbacksStopped；Sequence3/At=1s/Gate=null/PermitRelease/Stage=Simulation.PermitRelease。各Fraction=null，资源动作Outcome/Issue=null。Pack.ApiVersion=1.0.0、Id=integration-fixture或comparison-fixture、revision=r1、Surfaces两个、Scripts单项，先ProjectPack再填Hash/Provenance。预期Core.Completed、RelativeDiagnostic、support/check coverage=1且RMS/Max=0、原Surface不改写、backend逻辑handles在释放前1/之后0、所有lease由Core归还。NativeMetric保持2，不改为confidence；Publish.Snapshot=null。Comparison的measured差仍为显式0.2，不被配准支撑吸收。

以下核对值由上述完整字段独立构造后按唯一投影实算；不从已有hash反推字段，也不新增fixture生成依赖。各double先按binary64计算，再写位串；measured的`z+.2`也遵此规则，比较差值使用NumericalTolerance=1e-10，不要求浮点相减恰等于.2。versionHash=`c2b7bab68562ef48cdce53cb0eaa3e6fe54ff6bf37c0aa957f41a9e2273b3da7`，profileHash=`4e175b59264f03cf84175399ae64f4360aa57a38d9362beea9d65404c70545c6`，correspondenceHash=`a958b1fa97c7a9ad5bcb0c589fea3a6097734b2ad89acde9414881b8e98a5174`。两个Outcome投影均6124 bytes，所以65536满足最小预约；G=0，BaseBytes分别89396/91906，Start后分别154932/157442，均小于16777216。

| 完整字段预像 | UTF8 bytes | SHA256 |
|---|---|---|
| integration source | 926 | `600478c88ad4027b9ba68278a50e94ec2ffcfc9c8f4f63d99d3305a03fb951b9` |
| integration target | 926 | `ae1586634c9b7c2357b21ec7c23a7bbb850193fe0d412a68e4943fb1508f7d0b` |
| integration request（含Core rule标签） | 3570 | `554deb65f585d29e458ee6305521e70153dd6857cd2f19cd98233bbc279e4fd1` |
| integration normal pack | 12442 | `9887c4d0b47424b972996bb4c41df760f94a68e104b36172ef535174a6fb9128` |
| comparison source | 1363 | `82a631c63376ee912aa065ab2b90dc6db63ee0ff41c0df52487a12afb5d55d8f` |
| comparison target | 1363 | `4b0a36ed1ae3ef01f1c4894e4a81873bc436561bf598de7d47b4b1a2655aa3e8` |
| comparison request（含Core rule标签） | 3816 | `2c8350e48256b8f4568441500fd2abf539d99a9ab6d2a33c0b76af53d97fa99b` |
| comparison normal pack | 13697 | `1d4e136f59383c3591b2bc6199d164fb67be7c45ccd43a55af676c408e4d7590` |

Publish负面用例的TransformUseContext固定CurrentNodes=原request.Nodes、TargetFrame=原request.TargetFrame、CurrentProfile=QualityProfile.Identity、CurrentRuntimeManifest=RuntimeManifest、Ledger=Empty。CalibrationUseEvidence=(AssetRef(unavailable,r1,versionHash,EvidenceRef(registration-sim:calibration:unavailable,versionHash)),false,false,false,TargetFrame,[source.ContentHash],同Evidence)。这只是显式“无可用校准”的Synthetic拒绝fixture，不能写入标定资产或设Current/Applicable=true，不能补入request.QualityProfile.Calibration。断言Snapshot=null、REG3D-023，不绕过非Qualified门。

**异常→恢复脚本。** 新pack/新session（原session必须已确认归还）同输入但Script.Id=late，actions为Complete@1s；Progress@1s、Gate=late、Stage=Simulation.Late/Fraction=.5；CallbacksStopped@1s、Gate=drain；PermitRelease@1s。Host先Advance(1s)，Core开始排空；独立Close传session.Clock.GetUtcNow+2s，固定虚拟时间不继续推进时System真实观察2s到期，保留原CloseTask/session/registrar/端口；Signal原operation late只发原诊断，Core不得由该progress覆盖排空/终态；Signal drain后继续原回调排空/释放，再有限观察原Task，必要时以同clock幂等Close最终确认。恢复是原资源收尾，非重跑/替换实例；超时异常演练Host返回非零但正式测试观察到完整预期流程才case通过。另一个fault脚本将Complete改FailCompletion/REG3D-015，其后CallbacksStopped/PermitRelease明确，Core只有归还后RecoverableError，无成功候选；业务及cleanup错误分开保留。

late的Actions按上述顺序Sequence=1..4，Complete/CallbacksStopped/PermitRelease的Stage和payload沿正常脚本，其余Gate=null；Progress.Outcome/Issue=null。fault固定Script.Id=fault，Sequence=1..3，首项Stage=Simulation.FailCompletion、Outcome=null、Issue=RegistrationIssue(REG3D-015,Backend,Simulation.Fault,null)，后两项沿正常脚本。两者revision=r1、ReservedBytes=65536、LogicalHandles=1，Pack.Id分别在原mode Id后加-late/-fault；每次重新ProjectPack/Create，不沿用normal PackHash。调用方还须保留原正常包以回退，不重写它。

### C.4 两个从空 Host 的公开装配与根Owner收尾

Simulation.Host提供integration/comparison两mode，C.3给出两套完整fixture，不引用Core.Tests/BclHost内部类型。两个独立调用应用从空进程均只引用Core+Simulation并执行同一公开路径：

1. 根Owner先按§8.1预留有界槽（每mode最多1套），额外保存options、initialUtc、pack/出处、C.1顺序纯值构造的完整request、SimulationSession、session原CloseTask/最后确认Task槽和registrar原Task/identity/借用端口；所有有限槽先分配，满则factory调用0。CreateSurface/ProjectPack是纯值阶段失败不会启动后台；Create返回后**先存session再取Surfaces/Backend/Clock**，然后`new ObjectModel3dRegistrar(session.Surfaces, session.Backend, session.Clock, runtimePolicy)`并立即存强持槽，runtimePolicy逐字段取C.3，不能构造后等业务成功才登记。SimulationSession占该槽直到自身Close确认，无外部移交/弱引用/全局singleton。
2. registrar的clock只用session.Clock；Validate已保存的同一request（不更改ExpectedRequest绑定）→保存request.Calculation→调用RegisterPairAsync(request, events, businessToken)→ValueTask.AsTask一次保存原Task→有限System真实wall观察，events为明确同步Report的Host订阅器或null。Advance(1s)前必须有限等待该原业务Task对应的backend run出现在session.Query（用真实100ms间隔，总等待不超过case业务8s）；只有原RunView存在后推进，否则At相对run接纳时间，不能假设async调用返回就已Acquire/Start。Signal精确传原CalculationIdentity和已声明gate，不只传Guid。按脚本逐步Advance/Signal，有限观察Core.Query和原Task；Complete的Outcome仅作候选，Core独立质检/归还仍需真实continuation执行。保存GetReceiptPayload的原bytes/reference并核原hash，正常只消费C.3诊断结果，Publish按C.3负面context调用并拒绝Snapshot，不向真实下游注入Synthetic配准快照。
3. 正常/消费异常/events异常/脚本不匹配/取消/超时均进入独立cleanup，业务try不return Main。独立真实2s预算内首先保存原registrar.CloseAsync(session.Clock.GetUtcNow+2s)的Task；内层finally只有限观察原Task，包装等待到期不取消底层。如果native/callback卡在脚本gate，**仍允许根Owner按冻结脚本Signal/Advance**，不人工clearhandles/Disposelease；业务已取消不取消该控制清理。脚本里剩余gate名称/动作公开，清理只放行剩余已声明gate和推进至最后动作，不能改Outcome、伪造停止/新编脚本；脚本fault或消费抛错不会因cleanup改成业务成功。
4. 再一层finally保存SimulationSession.CloseAsync(session.Clock.GetUtcNow+2s)原Task并在本轮剩余真实wall观察，预算耗尽也必须发出非阻塞Close意图、保存返回Task，不能业务异常使模拟包Owner漏收尾。session.Close不代替registrar排空，两个Task可仍在途，原根Owner持续强持。清理推进上限从原RunView.StartElapsed+脚本最后At求出，已过期只Advance(0)，遇超dispatch预算用更小delta；仅放行已声明gate，不为timer到期无限快进。Core的deadline timer由Core自己的finally归还，模拟器自己Drain/Close timer按C.2归还；**模拟器不得代Core Dispose其timer**，若Core未归还timer则保留Issue/Owner，不能将已标Closed当包归还。session.Close需原run都Released、lease/timer/dispatch归零，随后清槽/可非零退出。报告false且原Task已完成时，保留原观察并只允许一次各自幂等Close最终确认（deadline均同session.Clock），不覆盖原Task。
5. 明确错误分层：业务、registrar cleanup、session cleanup三个有限记录组，按阶段/identity输出；错误不覆盖，未知资源不填0。任何强持槽未确认，仍由原Host监督loop持有至实际归还或A.4同样10/120/180s外进程失败隔离；未确认不能返回exit0/替换实例。构造registrar失败但session已存槽时仍执行session.Close并核无run/lease/timer，不dispose还未构造完成的Core对象。factory失败Session=null则原预留槽安全释放，不能误写session Closed=true。

两个Host的资源所有权有同一先后：宿主预留槽→Simulation session→借用端口/Clock→registrar→Core operation→backend run/lease/timer；归还由各Owner反向完成，Synthetic进程被kill仅是失败隔离不是恢复。真实产品Host必须保留相同依赖，不使用本测试kill作为设备/本机HALCON资源关闭证明。工厂/端口/task在正文已公开，无内部装配欠账；新API版本、真实持久化、任意脚本解释器、物理误差模型和独立设备模拟不在S1范围。

### C.5 唯一工程、正式验证、发布与benchmark

| 工程/namespace | 唯一路径/引用 | 用途与允许边界 |
|---|---|---|
| Asun.Modules.Registration3D.Simulation | `src/Modules/registration-3d/Asun.Modules.Registration3D.Simulation/Asun.Modules.Registration3D.Simulation.csproj`；net10.0、BCL、仅ProjectReference本模块Core、无PackageReference | 独立可发布DLL，C.1公开factory/session/DTO；不引用Core.Tests、BclHost、WPF、DevExpress、AsunImage或其它模块实现 |
| Asun.Modules.Registration3D.Simulation.Tests | `tests/Modules/registration-3d/Asun.Modules.Registration3D.Simulation.Tests/Asun.Modules.Registration3D.Simulation.Tests.csproj`；Microsoft.NET.Sdk、net10.0、OutputType=Exe、BCL、仅Core+Simulation引用、无PackageReference | 本切片唯一正式测试；不修改已接收Core.Tests引用，全部S1断言完整执行 |
| Asun.Modules.Registration3D.Simulation.Host | `tests/Modules/registration-3d/Asun.Modules.Registration3D.Simulation.Host/Asun.Modules.Registration3D.Simulation.Host.csproj`；同上Exe及引用 | 两个空Host mode独立消费者装配/消费演练；不是正式测试替身，无产品Store或Shell |

以上目录仅在S1经主控接收并另获明确实现任务后允许变更；其它模块、Shell、原件/共享文件、AsunImage内部禁止。本轮不建工程。模拟包版本1.0.0和Core依赖0.2.0冻结；包带公开契约/规则、脚本内容hash、显式options/fixture、错误资源键、验证/benchmark及回退索引，不随包带真实客户配方/物理标定或生产资格。session.Close后只在新session使用新pack/revision；旧脚本/原hash/原Task证据保留，回退不迁移活动Task或改写旧Receipt。

```powershell
dotnet build src/Modules/registration-3d/Asun.Modules.Registration3D.Simulation/Asun.Modules.Registration3D.Simulation.csproj -c Release
dotnet run --project tests/Modules/registration-3d/Asun.Modules.Registration3D.Simulation.Tests/Asun.Modules.Registration3D.Simulation.Tests.csproj -c Release
dotnet run --project tests/Modules/registration-3d/Asun.Modules.Registration3D.Simulation.Host/Asun.Modules.Registration3D.Simulation.Host.csproj -c Release -- --mode integration --fixture normal
dotnet run --project tests/Modules/registration-3d/Asun.Modules.Registration3D.Simulation.Host/Asun.Modules.Registration3D.Simulation.Host.csproj -c Release -- --mode comparison --fixture measured-domain
```

host另外允许`--fixture late`/`fault`，输入及恢复按C.3；每mode各有对应完整request。正式Simulation.Tests继承A.4真实case10s（业务8s/独立cleanup2s）、suite120s、外Process180s及BCL自身worker有限监督，不用模拟Clock驱动卡死保护；唯一内部worker参数仍--suite-worker/--mode-worker，同assembly，无新增工具项目。故障case预期Host非零只在完整事件/资源/强持断言观察后才算测试通过；任何必需失败/跳过/未完成/迟到未清理非零并列SIM编号，全部完成及归还才exit0。

| ID | 明确操作 | 必须断言/恢复 |
|---|---|---|
| SIM-01 双空Host正常 | C.3两mode各纯值factory→session→registrar→Advance1s→诊断消费→C.4双Close | coverage1/condition6/原hash不变；comparison measured显式差0.2保持；无Snapshot；两个层次租约/逻辑handles/timer归零才exit0 |
| SIM-02 factory/来源/身份 | 同Ids改一个Point/Domain/Outcome/At或请求Profile，保留旧pack.Hash；unknown API；NaN或重复索引；initialUtc+MaxVirtualDuration溢出；Calibration非空/非simulation URI | Create拒绝无Task/timer/run/lease；对应hash全纳入预像，不能老pack/revision冒充；新合法hash/session才恢复 |
| SIM-03 脚本匹配/幂等 | 注册同Core identity两次；直调同Backend identity重复；新OperationId同request；hash不存在/两script同hash | Core只一次Start；直调DuplicateRun；新id consume另run槽；不匹配拒绝、不consume槽；Run墓碑至session关闭，旧结果不覆盖 |
| SIM-04 时间/迟到/取消 | initialUTC固定2020与SystemUTC不同，Clock不推进；C.3 late gates、取消与Complete在同At竞争；迟到Progress及callbacks待gate | Close deadline=ClockUTC+2s、System真实观察≤2s；原Task不被包装timeout取消；Core迟到不改终态；原session强持，经Signal排空再最终确认，恢复不换identity |
| SIM-05 timer与dispatch | CreateTimer due0/Infinite=-10000ticks/period10ms、Change/Dispose及回调内Dispose；Advance错过多期、超过dispatch256、回调创建/改期timer、重入/并发Advance；时间负值/UTC溢出 | stable序/禁用仍占槽/Dispose不自锁且DisposeAsync等退出；超限原时间/动作/gate不变，可较小delta恢复；回调新generation下次Advance才触发；System经过不触发虚拟timer，period0拒绝；回调抛错仍排空 |
| SIM-06 容量 | 每个Options源/脚本/动作/pointchunk/timer/run/lease/bytes/handles/gates限额恰界及+1；checked乘加溢出；ReservedBytes低于payload下界；MaxRuns消耗后run释放 | 全部超限无部分预约，未完成原run资源保持；活动归还后并发容量可用、终生MaxRuns不回补；Close未确认时不删Source/Outcome减少预算 |
| SIM-07 资源与原Task | 直接Backend取得IBackendRun，CallbacksStopped/PermitRelease gate未开先Drain/Release；FailReleaseOnce；同run反复stop/Release；Core消费异常及构造失败 | false不是释放；一次失败预约保持、再次Release确认且lease只由原OwnerDispose；Core/session双cleanup不覆盖业务错误；session已有而registrar构造失败仍Close确认 |
| SIM-08 断连/Close/恢复 | 两Host events异常、停止订阅、sessionClosing期间新Acquire/Start；同时保留未归还timer/lease；先sessionClose后registrarClose | 原run继续诊断/清理；新输入SessionClosing；timer/lease未归还不Closed，Advance/Signal仍可用；registrar确认归还后session幂等最终Close，不reset或替换 |
| SIM-09 异常候选/图 | 脚本零覆盖/平面rank3/歧义候选、无环图或独立错误观测；明确FailCompletion | Core按既定门Rejected/RecoverableError，Simulation不求解或降低门；仍保留原候选诊断/原任务，全部资源排空后才能终态 |
| SIM-10 规范身份/回退 | C.1.1完整source/domain/pack预像字节核对；换Calculation或仅换Pack.Hash/Provenance，ProjectPack字节不变；改纳入投影字段的规范值或顺序，预像变化（±0按同值规则）；改options/initialUtc不改packhash；未知ApiVersion新Create拒绝（无Load入口） | SHA针对实际字节、正负零同/邻接double异；hash不变不表示可以忽略Create来源/预算校验；未知版本拒绝且保留原证据；新session不接续旧run；Core855-byte golden保持 |

benchmark计划按§15/DEV-GOV-010唯一统计口径：分桶源点/三角/域/脚本/动作/gate/timer/并发run及chunk大小；测CreateSurface、ProjectPack/Create、Acquire/read、Start、每Advance/Signal、原Task完成/回调退出/逻辑预约释放/lease/timer归还及双Close，记录真实wall/虚拟Elapsed分开、P50/P95/P99、managed分配/峰值、逻辑预约高水位/句柄/租约/timer/保留run计数、取消至实际归还。负载N=8/12为功能fixture，容量恰界/+1与长稳由Options上限形成有限次数；MaxRuns不回补，用关闭后的新session按固定次数重复而非增加无限队列。逻辑PeakBytes/虚拟1s不当实测吞吐或HALCON/native时延；门缺消费者目标只NotEvaluated。并发/清理/摘要超预算为确定失败，不能仅挑成功或资源已经忘记的样本统计。冷热各桶冻结预热/次数/最少样本/观察窗口后才运行，无实测数据/目标值不声明最快或达标。

### C.6 Simulation-S1 六项准备与后续门

| DEV-GOV-010 §3.1 | 唯一准备位置/判定内容 | 当前状态 |
|---|---|---|
| 1 边界/第二消费者 | C.1/C.3/C.4；离线整合/比较两个既有消费者；显式结果重放、无视觉/物理真值/设备副作用 | 主控已接收文档规格；托管Core接收保持，不授生产集成 |
| 2 公开契约/Owner | C.1完整DTO/factory/session/Clock/端口，C.2有限动作/错误/容量/hash/归还/失效 | 主控已接收文档规格；独立公开装配，不提升实际DLL构建运行 |
| 3 独立空Host | C.3逐字段fixture、C.4根槽/原Task/双独立finally；两个mode无Shell/SDK/DB/UI | 主控已接收文档规格；未构建/执行两个Synthetic Host |
| 4 正常/错误/并发/取消/关闭/版本 | C.5 SIM-01～10、§8.1复用；虚拟clock/真实wall、late/stop/gates/容量/失效/失败回退 | 主控已接收文档规格；原Task/lease/timer与两层Close/root保持，未执行测试/长稳 |
| 5 benchmark | C.5及DEV-GOV-010统计；真实wall/逻辑资源和虚拟Elapsed分开，硬预算/目标来源 | 主控已接收方法/文档规格；目标待Profile、NotEvaluated，不授性能或HALCON数值达标 |
| 6 工程/允许路径/顺序 | C.5唯一Simulation/Simulation.Tests/Simulation.Host，C.1公开装配→C.4双Close | 主控已接收文档规格；未创建工程，实际实现任务和权威代码仓库/快照另绑定 |

2026-10-11主控已回读C.1～C.6，Simulation-S1按DEV-GOV-010 §3.1六项文档规格接收为`ModuleCoreImplementationReady`，仅规格准备，整模块仍为`DesignReview / Prep`。接收范围只含独立纯托管脚本Simulator/factory/pack/Clock/有限资源与两个Synthetic Host：显式BackendOutcome不运行ICP，Calibration=null仅RelativeDiagnostic/Publish拒绝，虚拟时间与真实观察分离，原Task/lease/timer与两层Close/root保持。主控本轮未独立重建新pack/fixture各hash，本文自审复算不改写成主控复算通过。剩余精确门为另派实现任务/权威代码基线、实际DLL构建/Simulation.Tests/两个Host/有界异常排空/benchmark结果和包发布验证。真实HALCON/Adapter/WPF/平台Contract/客户物理、性能及生产资格仍各自验收，不作为S1纯合成脚本构造的阻断，也不能借S1文档接收授这些门通过；本轮不创建工程，不新增研究/报告/测试，不启动代码实现。
