# 成像质量评价独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`ManagedCoreSlice-01, QualityServiceSlice-02`

- 模块：`image-quality`；平台标识：`IM-020`；来源：`PKG-013`
- 状态：`DesignReview/Prep` / `PreparationIncomplete`（产品资格）；版本：`0.6.1-prep`；完整批准范围的可决定软件设计已在原会话收口并自审，见§24.5；服务关闭0.5.2-prep已接收：2026-10-10；服务六项与WPF/AsunImage限定指导已接收：2026-10-11；目标视觉运行时：HALCON `26.05`
- 规划消费者：OCR、读码、2D/3D 前置检查；独立模块工程候选：`ImageQuality.Core`、`ImageQuality.AsunImage`、可选 `ImageQuality.Wpf`
- 本页分层：附录A为 `ManagedCoreSlice-01` 的Module API v0.1；§16为无UI `QualityServiceSlice-02` 的模块端口/执行/有界根合同（完整六项见§24.1，双Host见§16.11）；可选WpfSlice-03公开接线见§8.4–8.5；§3.4–3.5产品形状仅供C-03/C-04映射。指标算法唯一正文见[§18–24](#image-quality-implementation)；预处理图由[PKG-014](../../shared-modules/packages/PKG-014_ImageProcessing.md)负责，不另建正式平台Schema。

> 分层规则：ManagedCoreSlice-01及QualityServiceSlice-02/Core+Simulator已由主控按DEV-GOV-010 §3.1接收为ModuleCoreImplementationReady（仅文档规格准备）；WpfSlice-03的整体装配/Presenter/原Owner恢复新增指导及AsunImage公开构造指导的确定范围已限定内容接收，均不授运行/产品资格。切片最新接收以本页Core binding和§24.1/24.4为准，正文早先送审/PreparationIncomplete表述保留为当轮准备背景；正式产品Contract/Schema/State/Owner、C-03/C-04映射、客户Profile与真实产品桥仍待对应采纳/验收。任何未列入切片的类型不得由实现者补造。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/image-quality/Asun.Modules.ImageQuality.Core/Asun.Modules.ImageQuality.Core.csproj`；namespace：`Asun.Modules.ImageQuality`。预定测试工程：`tests/Modules/image-quality/Asun.Modules.ImageQuality.Core.Tests/Asun.Modules.ImageQuality.Core.Tests.csproj`。上述项目尚未创建。
- 允许变更范围：仅上述 Core 和测试工程目录；在明确获准的实现切片中，必要的新文件也只能放入这两个目录。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 当前切片状态：`ManagedCoreSlice-01`（2026-10-10）与`QualityServiceSlice-02/Core+Simulator`（2026-10-11）均为`ModuleCoreImplementationReady`，仅六项文档规格准备；服务包括§16.2–16.11公开端口/factory/Profile、构造前进程根/原Task、双Host完整Fixture及业务/cleanup两轴。WpfSlice-03整体装配/Presenter/原保存Owner恢复与AsunImage公开构造指导确定范围已由主控限定内容接收；真实WPF/AsunImage/产品资格仍`PreparationIncomplete / NotReady`。保存知识、原意图查询与0.5.2-prep Stop已接收范围保持；整模块不提升。未创建工程、编译运行、验证native资源系数、真实Viewer/保存Owner/产品映射、性能或现场指标；Memory viewer仅按固定显示能力验，不外推超大图/3D性能。

### 首片 `ManagedCoreSlice-01` 范围和最小宿主

`ManagedCoreSlice-01` 只包含可脱离检测平台运行的纯托管、确定性图像质量计算：原始灰度值上的饱和/曝光分布计数、总体对比度（总体标准差或 nearest-rank 分位范围）、固定灰度范围直方图、显式有效 mask 覆盖率，以及这些量所需的有限值、分母、范围和资源校验。输入是宿主在内存中构造的不可变托管灰度快照；首片不负责从相机、文件、HALCON 对象或产品帧租约取得图像。

首片明确排除 `sobel_amp`、`laplace_of_gauss`、`estimate_noise`、`deviation_image`、结构光多帧完整性、任何邻域 halo/native 支持、帧租约、`ImageSupportLease`、AsunImage/HALCON、WPF、数据库、设备 SDK、产品事实写入和质量放行。上述能力只能在后续切片中通过显式 Adapter Port 接入；不得以纯托管实现偷偷替代已选 HALCON 路线，也不得把后续类型放入首片最小宿主。

首片的唯一执行入口是 `IImageQualityEvaluator`；唯一构造入口是 `ImageQualityManagedFactory.Create`；唯一外部诊断端口是可选注入的 `IQualityDiagnosticPort`。宿主不得直接调用算法函数、创建第二套隐藏入口或绕过factory；不同宿主可各自经factory创建独立evaluator，禁止通过静态状态传递请求。首片只提供同步 `Validate`/`Evaluate`，因为没有 native 工作、设备副作用或可证明的异步排空；取消令牌若由宿主包装，只能标记调用方意图，不得伪造可中断执行状态。

最小 host 是一个无 UI、无产品 Shell、无数据库、无设备 SDK、无 HALCON runtime、无 AsunImage 程序集的 .NET 10 控制台/测试宿主：只引用 `ImageQuality.Core`，在内存中创建 `ManagedGrayImage`、`ManagedQualityRegion` 和具名 `ManagedQualityMethodSet`，调用 `ImageQualityManagedFactory.Create` → `Validate` → `Evaluate`，检查逐指标值/单位/样本数/原因，并释放 evaluator。该 host 不需要 `ImageFrameLease`、`ImageSupportLease`、相机图像或网络；它是首片可构造性的验收边界，不代表产品集成已经通过。

首片以后需要真实帧时，由独立 `FrameAdapterSlice` 把获批C-03输入映射为托管快照或§16端口。未采纳产品帧/支持域映射只阻断该集成桥，不阻断独立服务/模拟端口定义。AsunImage及全部HALCON26.05算子按项目规则直接使用，不重复核验是否存在；仅实际C#类型、重载或封送歧义查公共签名/消费项目编译。native所有权、排空、算法Golden仍是本模块自身验收。

## 1. 职责和禁止边界

模块长期候选职责是接收一帧或一个明确的多通道/曝光/结构光输入组，以及冻结的方法描述，计算图像本身可观测的质量量。`ManagedCoreSlice-01` 只接收内存托管灰度快照；真实帧组、邻域支撑、来源和缺失原因通过后续 Product Schema/Adapter 映射进入。其报告可以供调用方作为任务适用性证据。

模块不采图、不调曝光/光源/运动、不重拍、不改原图、不做 OCR/读码/缺陷检测/重建、不关联 PCB/目标/工单、不设制程阈值、不解释工艺、不作质量放行、不提交生产事实、不驱动设备。调用方持有调用顺序、目标关联、质量门限及解释、重拍策略、授权和副作用。清晰度或其它单项高值不能推出任务可检或产品合格。

模块不提供无来源的万能分数。对黑像素不推断遮挡；遮挡/无效区只能来自输入携带的、具有来源的支持图或上游观测。相同像素哈希不代表同帧、同曝光或同一目标。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.ImageQuality.Core` 及 `Asun.Modules.ImageQuality.AsunImage` 子程序集不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Modules.ImageQuality.Wpf`（诊断/报告控件）可引用 WPF/DevExpress，且 Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。这条门禁使首片最小宿主（§Core binding 的 "ManagedCoreSlice-01 范围和最小宿主"）在移除 WPF/HALCON/AsunImage 引用后仍可运行，从而成为可被 Blazor Server 宿主直接引用的纯托管能力。

**Blazor/Web 宿主中的质量查询**：Web 端需要展示某帧/某 ROI 的质量报告时，服务端调用本模块的 §16（`QualityServiceSlice-02`，后续无 UI 服务合同）或首片的 `ManagedCoreSlice-01` 入口取得逐指标结果（含方法修订、单位、样本数、有效域摘要与缺项原因），再投影到浏览器。约束：
- 浏览器端不重算任何指标，也不自行解释"清晰度/对比度"阈值；单指标高值不构成可检或合格结论
- `ApplicabilityResult` 是一次快照结论，不是长期可用布尔值；资产/帧/方法修订变化后必须重新解析
- 无帧租约可用时（如离线回放、历史证据查询），宿主以托管快照构造 `ManagedGrayImage` 走首片路径，不为此新增 Web 专用算法入口
**AI 推理 Tiling 适配**：本模块可作为 `ai-inference` 分块推理的**前置质量门**——对 tile 字节做质量检查以决定该 tile 是否进入推理，而不是在推理后过滤结果。适配约束：
- 质量检查消费的是 tile 的只读字节与其 `EffectiveDomain`，本模块不自行向 `image-frame` 申请 tile、不持有 `FrameLease`
- tile 级质量结论与帧级质量结论是不同对象，不得互相顶替；tile 结论只对该 tile 及其所属帧修订有效
- 本模块不因"tile 质量差"自动触发重拍、跳过或参数调整；是否中止推理由调用方（宿主/`ai-inference`）按已冻结 Profile 决定

**HALCON 备选交叉验证适用性**：本模块是 2D 视觉链中**双跑 CI 的首个落点**，因为 `ManagedCoreSlice-01` 天然提供一条不依赖 HALCON 的确定性参照路线。约束：
- `ManagedCoreSlice-01` 的纯托管统计（饱和/曝光分布计数、总体对比度、固定灰度范围直方图、有效 mask 覆盖率）与 §20 HALCON 路线（`intensity`/`gray_histo_abs`/`gray_histo_range`）**按同一 Golden 数据集双跑**，差值超容差即 CI 失败并产出差异报告
- 容差按指标分别冻结（例如直方图按 bin 对齐、计数按整数精确相等、对比度按相对容差），不得用统一 eps 覆盖全部指标；未冻结容差的指标不参与双跑门禁，只登记为诊断
- 语义差异是**已知且不允许抹平**的：§20.5 的 `deviation_image` 响应是 2 倍局部标准差、邻域算子有二维 halo/支撑域、`gray_histo_abs` 有 Quantization 语义、`estimate_noise` 依方法假设（`foerstner`/`immerkaer` 有 Gaussian 假设且不受 Percent 调节）。托管路线与 HALCON 路线在这些点本就不同，双跑差异报告必须按指标标注"语义差异"或"实现缺陷"，不把语义差异记为失败
- HALCON 仍是生产路线，托管路线只作交叉验证参照与降级保险，不作发布依据；OpenCV 仅在需要第三方独立参照时使用，固定 commit `a0cda081f8d769f40ab2f4904738b4787b44d07c` 的本地已读快照见 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)，不引入平行生产算法
- 未采纳的邻域/多帧/结构光能力不得为凑双跑而提前引入 HALCON 路线或替换首片边界

## 2. 程序集和适配层

首发独立交付边界建议如下；长期能力均可无 UI 调用，首片只验证纯托管 Core：

| 部件 | 职责和依赖 |
|---|---|
| `ImageQuality.Core` | 首片只实现 `ManagedCoreSlice-01`；不引用 WPF、DevExpress、HALCON、AsunImage、宿主 ViewModel、产品数据层或帧租约。强类型托管请求/报告、参数校验、有限值统计、方法编排和诊断。目标 `net10.0`。 |
| `ImageQuality.FrameAdapter`（后续 gated） | 将获批 C-03 帧/支持域输入映射为 Core 托管快照，或在正式 Contract 采纳后提供唯一 Adapter Port；依赖 `ImageFrameLease`/`ImageSupportLease` 的切片不得进入首片。 |
| `ImageQuality.AsunImage`（后续切片） | 经ImageLibDotNet.cv2实现§20路线与native所有权；Golden/Replay验收跟随实际实现，不能把它们当禁止实现的前置依赖门；不暴露 `HObject`、窗口或本机句柄给核心/宿主。适配端口形状见§16，算子语义见§20；仅实际C#重载歧义在该适配实现中查公共签名，不把它列为依赖准入门。 |
| `ImageQuality.Wpf`（后续切片） | 只读报告/影像诊断和工程参数草稿控件；校验/执行使用同一§16服务，Raw量由同Core evaluator。无产品页面、设备命令、隐藏初始化或第二套判定。 |

首片输入由宿主构造托管快照；不经 image-frame 公共租约。产品原帧与掩膜通过后续ImageQuality.FrameAdapter消费IM-006获批契约，其精确产品映射/lease生命周期仍待原Owner采纳。独立工具的文件/内存来源可自行实现§16端口，不受产品桥阻断。存储、日志、本地化、调度器均由宿主通过端口提供；模块不查全局容器或硬编码路径。正式产品 API/包 ID、引用方向和依赖版本须由映射/集成阶段冻结。

### 2.1 HALCON 路线核对

以仓库 `halcon算子手册/operators` 内 HALCON `26.05.0.0` 页面为选择依据。已核对的候选包括：`intensity`、`gray_histo`、`gray_histo_abs`、`gray_histo_range`、`sobel_amp`、`laplace_of_gauss`、`estimate_noise`、`deviation_image`。选择和边界见本指导 §19–21：显式传实际统计 Region；高位深不使用自动 256-bin 结果冒充精确饱和计数；邻域算子保留二维支撑/halo；噪声估计依方法假设；`deviation_image` 响应按其 2 倍局部标准差语义处理。方向响应不能单独证明运动模糊，灰度离散不能冒充独立噪声。

已核对26.05形状：`intensity(Regions, Image : : : Mean, Deviation)`；`gray_histo_abs(Region, Image : : Quantization : AbsoluteHisto)`；`gray_histo_range(Region, Image : : Min, Max, NumBins : Histo, BinSize)`；`sobel_amp(Image : EdgeAmplitude : FilterType, Size : )`；`laplace_of_gauss(Image : ImageLaplace : Sigma : )`；`derivate_gauss(Image : DerivGauss : Sigma, Component : )`；`estimate_noise(Image : : Method, Percent : Sigma)`；`deviation_image(Image : ImageDeviation : Width, Height : )`。这是官方语义/参数顺序，经 `ImageLibDotNet.cv2` 调用；本方图像、Region、Tuple及响应图所有权按所有出口验证。

适配器必须按下面的固定顺序把托管块交给算子，不能由实现者用 `ReduceDomain` 或显示图像替代有效域：

1. `ReadBlock` 返回的 `QualityBlock` 先核对半开坐标、`Samples.Length == width*height`、`ValidMask.Length`、`SourceRevision/CoordinateRevision` 和剩余预算；任何乘法、字节数和行列转换使用 checked。块坐标保留为原源坐标，HALCON 局部图只使用 `localRow = row - Row0`、`localCol = col - Col0`。
2. 按 `QualityPixelType` 建立一次、连续、行优先的临时数组：UInt8 用 `byte[]` 对应 `byte`，UInt16 用 `ushort[]` 对应 `uint2`，Float32 用 `float[]` 对应 `real`（4 byte/像素）；§16.3要求所有位置（含mask=false）为有限、精确可承载的原码值，违规在native调用前拒绝。不得先转 byte、归一化或按容器上限裁剪；UInt16转real时所有整数精确保留，Float32从double载体还原时不得改变原值。仅§20.5要求的路线调用 `convert_image_type(...,"real")`；类型相同时也登记返回对象的所有权，不假设必有新矩阵。数组只在创建图像调用期间固定，原样使用64位地址，不转Int32，所有路径finally解除固定。
3. 用 `cv2` 对应 HALCON `gen_image1(Image : : Type, Width, Height, PixelPointer : )` 以精确类型、宽、高创建本地图，不使用 `gen_image1_extern`。该调用复制像素，固定数组必须保持到调用实际返回；创建失败时不继续算子。本方block、临时数组、HALCON图、转换图和输出按同时存活容量计账，引用同一矩阵不重复计像素容量但对象元数据仍计；不得让 HALCON 图引用已释放的托管数组。
4. 从 `ValidMask` 按行合并连续true段，按(row,colBegin)升序用 `gen_region_runs(Region : : Row, ColumnBegin, ColumnEnd : )` 创建一份Region；HALCON run的终点包含最后一列，半开[a,b)转[a,b−1]，先核等长/不重叠/本地图范围/`ColumnEnd>=ColumnBegin`。N=0时在native前按§16.3/20.5生成缺项，Raw Coverage仍0，不调用受全局空域配置影响的Region构造/统计。N>0时先用 `count_obj(Objects : : : Number)` 核返回恰一个Region，再用 `get_region_runs` 核每个run及总像素数与原mask一致；宿主当前image format/clip_region导致裁切、空对象或几何改变均为QS-ProviderFailure，不改SetSystem、不接受改变后的域。邻域路线用 `erosion_rectangle1(Region : RegionErosion : Width, Height : )` 对含halo的有效域求完整中心；返回0对象时不再调用get_region_runs，按无中心处理，返回1对象才读取中心runs，超过1对象为QS-ProviderFailure。空中心按§20.6返回NotObservable/SamplesInsufficient；非空只选择本tile拥有且完整落原ROI的中心。native异常仍按§16失败/释放规则处理，不能当作有效0响应；其他矩形路线按§20.6执行。
5. 每次 `cv2` 调用只接收本方图像/Region和冻结参数；显式Region的统计不得依赖图像domain。响应固定用 `get_image_pointer1(Image : : : Pointer, Type, Width, Height)`，核一个单通道对象、类型与尺寸，再在响应图保持存活期间按中心runs行优先读取：int1/int2先提升double再abs/square，uint2按无符号读取，real按float读取提升double。只读指针，不写输入、不返回指针、不另存全响应double副本；逐值有限/溢出核对，以在线均值累积abs或square，固定tile合并顺序。`get_grayval`只作有限Golden点差分，不是大图实现路径。控制Tuple复制后核长度/单位/有限性/闭合计数，按§16.3封闭Key输出。
6. 在同一 `try/finally` 中按“响应图和临时 Tuple/Region → 本地 HALCON 图 → 本次 invocation 记录”逆序释放；任何异常先保留 `invocationId` 和释放状态，再由 `CheckDrain`/`Close` 完成。只有所有对象确认释放才返回 `ResourcesReleased=true`。适配器不得关闭 Core 借入的 `IQualityReadScope`，也不得把 HALCON 对象放进报告、ViewModel、静态缓存或跨请求队列。

以上是公开 HALCON 语义到适配器的实施步骤，不是 AsunImage 内部假设；实际 C# 重载、Tuple 类型和 Dispose 名称只在消费项目引用的公共程序集上编译核对。若签名不能从公开资料和编译确定，仅暂停并报告受影响的适配调用绑定，不新增运行时错误码或阻断无关Core，不以反射或扫描封装内部猜测。

算子页定义HALCON语义；不得扫描/反编译AsunImage内部、另接 `HOperatorSet` 或 `halcondotnet.dll`。具体C#歧义只记录受影响调用，不扩大成依赖存在/兼容/授权审查。模块不调用SetSystem临时改全局参数；CPU/设备后端与线程配置由宿主runtime Owner保持，实际identity入报告。官方reentrant不等于允许共享可变句柄。

### 2.2 具体路线、备用条件和训练边界

首发路线是确定性指标组合，不是一个跨任务的总分。每次请求必须给出具名方法、Revision及完整强类型参数；hash由宿主按获批持久化规则计算，不是未定义的Core字段。模块按显式方法计划执行，不根据图像结果自动换方法。允许的路线和备用条件如下：

| 质量问题 | 首选路线 | 仅在明确条件满足时的备用 | 拒绝/不可观测条件 |
|---|---|---|---|
| 饱和、欠曝、曝光分布 | 附录A原值计数为RawStatistics基准；HALCON统计用于§20.5均匀性/差分，显式Region/阈值，不复制另一套Core算法 | 只有当原图类型与固定灰度范围均满足已批准量化规则时才可用量化直方图；必须另记范围外计数 | 缺有效位深/黑白参考、N=0、阈值顺序错误；不以显示 LUT 或容器上限补齐 |
| 对比度/均匀性 | 原始值矩和固定分位规则；局部均匀性按分区逐块报告 | 仅可在同一方法修订内使用 `deviation_image` 作为局部离散诊断；不能代替全局对比或噪声 | 分区有效样本不足、统计mask合法有洞可计算；邻域支撑不足只影响邻域路线、非有限值 |
| 清晰度/焦点评价 | §20.5固定Sobel3主路线，高位深/浮点实值Gaussian独立分支，LoG是UInt8量化候选 | 第二路线只能作为调用方显式请求的独立观察，不得取两者最高值或混成新分数；同物件受控离焦序列可用于 Profile 标定 | 纹理/支撑不足、边界 halo 不足、后端/图像类型不支持；高梯度不证明字符可读 |
| 加性噪声 | `estimate_noise` 的指定方法和 Percent，保留方法假设、Sigma 和失败语义 | 局部标准差只作纹理/离散诊断，不可伪装成噪声估计；切换估计方法必须生成新方法修订 | 均匀区/点数/方法前提不满足、算子返回无法可靠估计；不吞异常为 0 |
| 结构光输入支持 | 检查曝光/条纹角色集合、步序、饱和比例和空间支持 | 仅对完整且有来源的输入组输出结构光支持量；重建由 3D 模块另行执行 | 缺 step、角色重复/冲突、配准/支持域不足；不从单帧亮度推断相位质量 |

备用必须显式新方法/请求，报告原Unsupported/NotObservable及ActualRoute；原因使用§16.6封闭集合，不生成未声明PrimaryNotObservable字段。模块不在异常后盲目尝试下一方法，不以“成功率”选择结果，不把另一路线结果写回原方法身份。若确需训练质量分类器，训练、数据划分、模型 hash、后端、资源上限和离线评估归 AI 治理/模型资产模块；本模块只可通过适配端口接收已批准的模型快照，先以 Replay/Shadow/Advice 产生候选观察，不能替换确定性指标、自动改变方法、自动重拍或形成质量事实。当前版本不定义训练接口，也不把神经网络作为备用路线。

恢复规则固定为：输入错误先修输入；方法不支持由调用方选择已批准的新方法并提交新 `RequestId`；后端异常由宿主在原operation确认排空/释放后显式提交新RequestId，保留原失败关联；模块没有隐含尝试序号或自动重试。由宿主决定隔离/进程回收。模块不自动改参数、不自动降采样、不自动切换 CPU/GPU。

### 2.3 首发明确不支持

首发模块不支持：自动曝光/光源/运动优化；相机触发或硬件同步；跨帧/跨 FOV 配准和目标关联；运动速度/模糊长度反演；3D 相位解码、点云重建或高度计量；从图像生成 ROI/缺陷候选；训练、在线更新或模型推理；按阈值生成机判、质量放行、报表提交或设备命令；跨请求结果数据库、全局 latest 缓存和隐式重试。调用方可组合其它独立模块，但不得把这些能力通过未登记适配器偷偷塞回本模块。

## 3. 分层 API 与正式产品 Schema 映射

本节定位三层；模块托管首片在附录A、后续模块服务在§16、正式产品映射在§3.4–3.5：

1. `Module API v0.1`：只服务 `ManagedCoreSlice-01`，是纯托管 Core 的唯一实现基线。它只接收内存快照，不包含平台身份、产品状态、帧 lease、设备句柄或正式提交事实。
2. `Module API image-quality-service-v0.1`：§16无UI端口/编排及§20全部路线，不依赖产品DTO；独立接收，不能把完成首片当整模块完成。
3. `Product Schema Mapping`：把未来 C-03/C-04 的正式字段、Owner、序列化和采集来源映射到模块输入；当前仅记录候选关系，不是首片 API，不得在 Core 或最小 host 中引用。

下列原有 C# 形状中，`QualityRequest`、`QualityFrameInput`、`QualityRegion`、`ImagePlaneDescriptor`、`QualityCaptureConditions` 及所有 `ImageFrameLease`/`ImageSupportLease` 依赖属于第二层候选映射。它们保留用于审查正式产品边界，但不属于 `ManagedCoreSlice-01` 的可构造入口。首片必须使用附录 A 的 `ManagedQualityRequest` 等纯托管类型；不得把候选产品 DTO 别名为首片 API。

### 3.1 Module API v0.1 的唯一首片入口

首片唯一入口的语义及完整声明见附录A，以下仅为同一接口导航摘录，不能再生成第二份接口。ManagedCoreSlice-01六项规格已获主控接收，本轮不执行编码：

```csharp
public interface IImageQualityEvaluator : IDisposable
{
    ManagedQualityValidation Validate(ManagedQualityRequest request);
    ManagedQualityResult Evaluate(ManagedQualityRequest request);
}

public static class ImageQualityManagedFactory
{
    public static IImageQualityEvaluator Create(
        ManagedQualityRuntimeOptions options,
        IQualityDiagnosticPort? diagnostics = null);
}
```

`ImageQualityManagedFactory.Create` 是唯一构造入口；`IImageQualityEvaluator` 是唯一计算入口。Core 不公开单项算法函数、静态全局 evaluator、第二套工厂或隐式默认实例。`Evaluate` 只处理已校验的托管快照并返回确定性结果；它没有 native handle、设备副作用、异步事件或排空状态。

### 3.2 Product Schema Mapping（候选，后续 gated）

| 正式产品事实/候选来源 | 映射目标 | 当前状态和门 |
|---|---|---|
| C-03 帧/plane、原始/派生来源、FrameId/PlaneId、实际位深和有效域 | `ManagedGrayImage`、`ManagedQualityRegion` 的托管快照或后续正式 Adapter Port | C-03 字段、Owner、序列化和来源修订未采纳；`ImageFrameLease`/`ImageSupportLease` 不得进入首片 |
| C-03/C-04 指标方法、单位、逐指标缺项和原因 | `ManagedQualityMethodSet` 与 `ManagedQualityObservation` | 首片只冻结可由托管灰度快照计算的指标；正式枚举/错误映射须由原 C Owner 采纳 |
| C-04 报告、证据关系、提交/读取保持和产品状态 | `ManagedQualityResult` 的只读投影 | Core 不写产品事实、不提交报告；持久化和生产状态映射后续另立切片 |
| 采集曝光/光源/线程排空证据 | §16 QualitySourceDescriptor 的已知来源引用 | 不进入附录A首片；设备应用/读回/排空由宿主负责，不把请求值当实际值 |

映射层必须明确 `SourceRevision`、单位、有效域、Unknown/Invalid 传播和错误码对应关系。映射未采纳时，Core 只能接受首片定义的内存快照；不得用当前产品候选字段、默认值或最近一次有效设备值补齐输入。

### 3.3 首片输入和结果的托管边界

首片输入只允许：不可变 `ManagedGrayImage`（宽、高、像素类型、托管灰度样本和来源修订）、不可变 `ManagedQualityRegion`（区域边界与可选托管有效 mask）、具名 `ManagedQualityMethodSet`、正的托管资源预算和可选诊断端口。首片结果只允许逐指标数值、单位、样本数、有效域摘要、方法修订和结构化原因；不允许产品目标、板件、工单、设备句柄、数据库主键或质量放行状态。

首片不接收 `ImageFrameLease`、`ImageSupportLease`、HALCON `HObject`/`HTuple`、`PixelRectangle` 等未被本层冻结为托管类型的外部对象。若未来需要这些对象，必须在 `FrameAdapterSlice` 中完成来源快照、所有权和排空证明，再映射到正式产品 Schema；不得修改 `ManagedCoreSlice-01` 的最小 host 依赖图。

### 3.4 后续 Product Schema 映射形状（非首片 API）

以下代码只记录未来 C-03/C-04 映射的待采纳形状；不得在 `ImageQuality.Core`、首片测试或最小 host 中引用：

```csharp
public sealed record QualityRequest(
    Guid RequestId,
    IReadOnlyList<QualityFrameInput> Frames,
    IReadOnlyList<QualityRegion> Regions,
    QualityMethodSet Methods,
    QualityResourceBudget Budget,
    DateTimeOffset DeadlineUtc);

public sealed record QualityFrameInput(
    ImageFrameLease Frame,
    ImagePlaneDescriptor Plane,
    string MethodRoleKey,
    int SequenceIndex,
    QualityCaptureConditions Conditions);

public sealed record QualityRegion(
    string RegionKey,
    string MethodRoleKey,
    PixelRectangle Bounds,
    ImageSupportLease? ValidSupport,
    PhysicalScale? Scale);

public sealed record ImagePlaneDescriptor(
    string FrameId,
    string PlaneId,
    PixelType PixelType,
    int WidthPx,
    int HeightPx,
    int? EffectiveBitDepth,
    double? SensorBlackLevel,
    double? SensorWhiteLevel,
    string SourceRevision,
    string? DerivationRevision);

public sealed record QualityCaptureConditions(
    TimeSpan? ExposureDuration,
    string? IlluminationRevision,
    string? PoseRevision,
    MotionConditionState MotionState,
    double? ObjectSpeedMillimetersPerSecond,
    string SourceRevision);

public enum MotionConditionState { Known, NotApplicable, Unknown }

public sealed record QualityFrameSummary(
    ImagePlaneDescriptor Plane,
    string MethodRoleKey,
    int SequenceIndex,
    QualityCaptureConditions Conditions);

public sealed record QualityMethodSet(
    IReadOnlyList<QualityMethodRequest> Required,
    IReadOnlyList<QualityMethodRequest> Optional);

public abstract record QualityMethodRequest(string Revision);
public sealed record SaturationCountMethod(
    string Revision, double? LowClipInclusive, double? HighClipInclusive)
    : QualityMethodRequest(Revision);
public sealed record ExposureDistributionMethod(
    string Revision, double LowClip, double LowExposure,
    double HighExposure, double HighClip)
    : QualityMethodRequest(Revision);
public sealed record ContrastMethod(
    string Revision, ContrastStatistic Statistic,
    double? LowerQuantile, double? UpperQuantile)
    : QualityMethodRequest(Revision);
public sealed record SobelResponseMethod(
    string Revision, SobelFilterType FilterType, int Size, SobelAggregation Aggregation)
    : QualityMethodRequest(Revision);
public sealed record LaplaceOfGaussMethod(string Revision, double Sigma)
    : QualityMethodRequest(Revision);
public sealed record NoiseEstimateMethod(
    string Revision, NoiseEstimator Estimator, double Percent)
    : QualityMethodRequest(Revision);
public sealed record ValidCoverageMethod(string Revision) : QualityMethodRequest(Revision);
public sealed record StructuredLightSupportMethod(
    string Revision, IReadOnlyList<string> RequiredRoleKeys)
    : QualityMethodRequest(Revision);

public enum ContrastStatistic { PopulationStandardDeviation, NearestRankQuantileRange }
public enum SobelAggregation { MeanAbsoluteResponse, MeanSquaredResponse }
public enum SobelFilterType
{
    SumAbs, SumAbsBinomial, SumSqrt, SumSqrtBinomial,
    ThinMaxAbs, ThinMaxAbsBinomial, ThinSumAbs, ThinSumAbsBinomial,
    X, XBinomial, Y, YBinomial
}
public enum NoiseEstimator { Foerstner, Immerkaer, LeastSquares, Mean }
public enum QualityMetricKind
{
    Saturation, ExposureDistribution, BlurResponse, Contrast, NoiseSigma,
    ValidCoverage, LocalUniformity, StructuredLightSupport
}
public enum MetricUnit
{
    Count, Fraction, GrayLevel, KernelResponse,
    KernelResponseSquared, Millimeter, Micrometer, Dimensionless
}
public enum ObservationState { Computed, NotObservable, Unsupported }
public enum QualityExecutionState
{
    Completed, CompletedWithUnavailableMetrics, Cancelled, TimedOut, Rejected, Failed
}
public enum QueueOverflowPolicy { RejectNew, WaitForCapacity }
public enum MetricRequirement { Required, Optional }

public sealed record QualityResourceBudget(TimeSpan MaxDuration, long MaxWorkingBytes);
public sealed record QualityRuntimeOptions(
    int MaxConcurrentRequests,
    int MaxQueuedRequests,
    QueueOverflowPolicy QueueOverflowPolicy);
public sealed record QualityError(string Code, string FieldPath, string MessageKey, bool Retryable);

public sealed record MetricObservation(
    string RegionKey,
    string MethodRoleKey,
    MetricRequirement Requirement,
    QualityMetricKind Kind,
    ObservationState State,
    double? Value,
    MetricUnit Unit,
    double? NormalizationScale,
    long? SampleCount,
    long? RequestedPixelCount,
    string MethodId,
    string MethodRevision,
    string ParametersHash,
    string? ReasonCode,
    ImageSupportSummary Support,
    TimeSpan Elapsed);

public sealed record QualityReport(
    Guid RequestId,
    IReadOnlyList<QualityFrameSummary> Inputs,
    IReadOnlyList<MetricObservation> Observations,
    string BackendId,
    string BackendRevision,
    DateTimeOffset StartedUtc,
    DateTimeOffset CompletedUtc);

public sealed record QualityExecutionResult(
    QualityExecutionState State,
    QualityReport? Report,
    QualityError? Error,
    DateTimeOffset StartedUtc,
    DateTimeOffset CompletedUtc);

public sealed record QualityValidation(bool IsValid, IReadOnlyList<QualityError> Issues);
public sealed record QualityProgress(Guid RequestId, long Sequence, string Stage, double? Fraction);
```

`ImageFrameLease`、`ImageSupportLease`、`PixelRectangle`、`PhysicalScale`、`PixelType` 是需复用 IM-006/IM-007 Contract 的概念占位，不可在本包复制其实现。`MethodRoleKey` 和 `SequenceIndex` 只表达本次所选方法需要的输入位置；帧间对象/目标关系、采集封口和重拍归宿仍由调用方。若方法要求配准输入组，模块只接受调用方给定且有来源的配准修订，不自行找同一物件或拼组。图像坐标为整数像素边界、矩形半开 `[row0,row1) × [col0,col1)`；行向下、列向右。像素间距仅允许正有限 `mm/px` 或 `um/px`，换算统一在明确尺度对象中完成；不提供尺度时仅可算像素单位方法。

采集条件以只读快照传入。`MotionState` 候选值为 `Known, NotApplicable, Unknown`；Known 时速度须为有限非负 `mm/s` 且带同源修订，NotApplicable/Unknown 时速度必须为空。曝光时长为正 `TimeSpan`；照明/姿态均用来源修订引用而非设备句柄。条件未知时仍可返回不依赖该事实的图像量，但依赖项状态为 `NotObservable`；静态 2D 明确传 `NotApplicable`，不能用虚构的 0 速度替代。

建议枚举：`QualityMetricKind = Saturation, ExposureDistribution, BlurResponse, Contrast, NoiseSigma, ValidCoverage, LocalUniformity, StructuredLightSupport`；`MetricUnit = Count, Fraction, GrayLevel, KernelResponse, KernelResponseSquared, Millimeter, Micrometer, Dimensionless`；`ObservationState = Computed, NotObservable, Unsupported`；`QualityExecutionState = Completed, CompletedWithUnavailableMetrics, Cancelled, TimedOut, Rejected, Failed`。参数/后端错误属于请求执行终态和 `QualityError`，不塞进指标状态。不得用 0、NaN、Infinity 或“默认失败分”表示缺值。计数用 `long`，除法前检查分母，数值结果须有限。方法专有量必须新增明确单位/归一化定义，不能复用近似单位。

### 3.5 后续 Product Schema 参数、单位和范围候选

以下表格只适用于后续 Product Schema/Adapter；首片参数以附录 A 的托管类型和校验为准。调用方必须选择具名 `QualityMethodRequest`，冻结 `MethodId + Revision + Parameters`；模块不得按目标类型自动推断/偷偷切换方法。字段表是候选校验合同：

| 参数 | 强类型/单位 | 候选范围与默认 | 校验和语义 |
|---|---|---|---|
| `Frames` | 有序 `QualityFrameInput` 集合 | 至少 1 项；无默认 | `(MethodRoleKey, SequenceIndex)` 唯一；索引 `>=0`。各方法声明所需角色/顺序，未要求的额外输入不得悄悄参与计算。 |
| `Regions` | `QualityRegion` 集合 | 至少 1 项；无默认 | RegionKey 唯一；role 必须引用现有输入；有效 mask 尺寸/FrameId/PlaneId 必须匹配。 |
| `RegionKey` | 非空字符串 | 长度 1–128；无默认 | 请求内唯一，关联报告；不是产品目标 ID。 |
| `Bounds` | 整数像素半开框 | 非负起点、正宽高且全框在图像内；无默认 | 越界拒绝，不静默裁切；与有效支持相交后保留原请求面积。 |
| `EffectiveBitDepth` | `int?`, bit | `1..PixelType.ContainerBits`；无默认 | 未知保持 null；不得从容器类型猜有效位深。 |
| `SensorBlackLevel/WhiteLevel` | `double?`, 原始灰度码 | 有限且 `black < white`；无默认 | 两者须来自同一帧设置/校准来源；未知时报告缺项。绝不把容器最大值当传感器白电平。 |
| `PhysicalScale` | 有类型单位的正有限比例 | `>0`；无默认 | 来源/修订必填；没有物理标定时拒绝物理单位输出。 |
| `SaturationMethod` | 具名阈值/区域规则 | 阈值由调用方方法给出；无默认 | 阈值采用输入原始灰度单位，必须在已知有效范围内；不定义“够好”门限。 |
| `ExposureDistributionMethod` | 四个有限灰度码阈值 | 必须显式给出；无默认 | 必须 `LowClip <= LowExposure < HighExposure <= HighClip`；区间按本指导 §19 的互斥端点定义，五类计数和必须等于有效 N。 |
| `ContrastStatistic` / quantile | 枚举与比例 | StdDev 无额外参数；分位 `0 < q <= 1`；无默认 | quantile 仅对 `NearestRankQuantileRange` 要求，固定 nearest-rank 规则；有效域/分母随结果返回。 |
| `SobelFilterType` | 枚举 | `sum_abs`（HALCON 页面默认；模块仍要求方法修订显式冻结） | 26.05 候选值：`sum_abs`、`sum_abs_binomial`、`sum_sqrt`、`sum_sqrt_binomial`、`thin_max_abs`、`thin_max_abs_binomial`、`thin_sum_abs`、`thin_sum_abs_binomial`、`x`、`x_binomial`、`y`、`y_binomial`。不同 FilterType 不共用阈值/单位。 |
| `SobelAggregation` | 枚举 | 无静默默认 | 原算子聚合单位KernelResponse或KernelResponseSquared，不能当物理梯度；FilterType/Size/边界和响应符号共同冻结。 |
| `SobelSize` | 整数px | 非binomial仅3/5/7/9/11/13；binomial仅5..39奇数 | binomial输入仅byte/uint2/real，不接受int2；模块不开放二轴Size tuple。Size>3含平滑与幅值乘2，不共用Size=3阈值。 |
| `LoGSigma` | `double`, `px` | `0.01..25.0`，步进 `0.01`；HALCON 默认 `2.0` | 只限 `laplace_of_gauss`；应冻结离散响应聚合、单位、支持域。不同 Sigma 的分数不能直接共用阈值。 |
| `DeviationWindowWidth/Height` | 奇数整数px | HALCON默认11；3≤size、odd且小于对应图尺寸两倍 | 模块拒绝偶数，不接受算子自动加1；响应是2倍局部灰度标准差，边界镜像不恢复有效域。 |
| `NoiseEstimator` | 枚举 | 必须显式选择；HALCON 默认 `foerstner` 不作为模块默认 | 26.05 候选：`foerstner`、`immerkaer`、`least_squares`、`mean`。按本指导 §20 所列各自假设/失败路径选用，不能自动 fallback。 |
| `NoisePercent` | `double`, `%` | HALCON 默认 `20`；合法 `(0,50]` | 只传所选 `estimate_noise` 路线；仅表达参与估计的点比例，不是置信度/质量分。`foerstner`、`immerkaer` 不以 Percent 调节结果；其余路线按本指导 §20 的 HALCON 定义和方法假设核对。方法修订须显式冻结实际值。 |
| `HistogramRange/NumBins` | 有限灰度上下界/正整数箱数 | 按附录A；无默认 | 不再使用未冻结BinWidth；范围外计数与分箱端点以A.3为准。 |
| `Required` / `Optional` | 指标请求集合 | 必须明确提供；无默认全选 | 所需指标缺失将使执行结果 `CompletedWithUnavailableMetrics`，但不生成产品合格状态。 |
| `RequiredRoleKeys` | 唯一方法角色键集合 | 非空、每项长度 1–128；无默认 | 仅核对调用方给定输入集中所需 role 是否存在/唯一，不负责采集组装、对象配准或产品目标关联。 |
| `MaxWorkingBytes` | `long`, byte | `>0`；无隐式无限默认 | 宿主按有效像素、邻域缓冲、HALCON 临时对象和报告估算配置；预计超限须在计算前拒绝或按已批准 tile 策略运行。 |
| `MaxDuration` / `DeadlineUtc` | `TimeSpan` / UTC | `MaxDuration > 0`；绝对截止时间不得为过去值；无默认 | 单一有效截止时刻取两者较早值，覆盖排队、准备、算子和排空；超时不提前释放 native 输入。 |

`QualityRuntimeOptions` 是实例级资源策略，不属于图像质量事实：`MaxConcurrentRequests` 为正整数，产品候选值；模块服务实际固定为 `1`；`MaxQueuedRequests` 为 `0..N`；队列满时 `RejectNew` 立即返回 `IQ-BUD-006`，`WaitForCapacity` 只在调用方截止时间内等待。高并发不得通过无界任务队列、全局静态缓存或跨实例共享 native handle 实现。实例运行中不得热改这些选项；修改须停止、排空、重新创建实例并记录运行时修订。

上述数值范围是 API 候选的防错边界，不是传感器限制或生产质量阈值。真实指标门限、各方法支持域、采集设置源和大图容量须由实际 Profile/样本冻结。省略无来源阈值不是漏项：返回量和有效性事实由调用方解释。

### 3.6 本节及后续门的适用范围

§3.4–3.5代码块是产品映射语义草图，含未定义产品概念，不能作为可编译模块API。§4–6维护后续执行要求，具体公开合同见§16；§8/23维护可选UI，§18–24维护算法。首片以Core binding、§3.1–3.3及附录A为准；冲突先修唯一正文，不拿候选产品DTO实现模块端口。

## 4. 同步、异步与通知顺序

首片同步Validate/Evaluate/Dispose的唯一合同见A.1–A.2：无CancellationToken、native或异步事件。宿主超时等待不能虚构计算已停止。

服务的唯一合同见§16：Validate→Start→IQualityOperation.Completion，状态从GetSnapshot读取，取消用RequestCancel，关闭用StopAsync。没有EvaluateAsync、observer或第二个事件结果权威。接纳前拒绝为QualityStartResult.Operation=null+Issue；接纳后仅Completion带最终值，资源未确认时Completion不结束。产品宿主如另需通知，只投影此状态/结果，不在本模块重新定义事件序列。Computed是量可算，Completed是执行完成，均非质量PASS。

## 5. 状态、错误码和恢复

服务公开状态唯一见§16 QualityOperationState；接纳前没有operation，校验拒绝由StartResult表达。内部准备/工作→Draining→确认Drained/ResourcesReleased→Terminal；运行超时等native实际返回并释放后才TimedOut，未知则DrainUnknown。`Drained` 和 `ResourcesReleased` 是资源事实，不是质量结论；状态机只属于本执行实例，不表示图像、对象、产品任务或质量结论。

错误码候选：

| 错误码 | 含义 | 调用方动作 |
|---|---|---|
| `IQ-REQ-001 InvalidRequest` | null/重复方法键/预算非法 | 修正请求，不重试原字节。 |
| `IQ-IMG-002 InvalidImage` | plane、类型、stride、尺寸、非有限输入与帧描述不一致 | 隔离该输入并检查 IM-006 适配。 |
| `IQ-DOM-003 InvalidDomain` | ROI 越界、掩膜尺寸/帧来源不匹配 | 修正来源/域；不自动裁剪或补满。 |
| `IQ-MET-004 UnsupportedMethod` | 图像类型/后端/目标尺度不支持所请求方法 | 显式换方法并生成新请求修订，不静默降级。 |
| `IQ-SRC-005 MissingRequiredSource` | 方法依赖的位深/白电平/尺度/支持证据缺失 | 报告该指标 `NotObservable`；必要方法缺失时由调用方停止相依工作。 |
| `IQ-BUD-006 ResourceBudgetExceeded` | 预计资源或并发预算超限 | 缩小 ROI/指标或按批准分块；禁止部分假成功。 |
| `IQ-RUN-007 BackendFailure` | AsunImage/HALCON 异常或无效输出 | 保留脱敏诊断/方法修订；不把异常映射成零或默认分。 |
| `IQ-CAN-008 Cancelled` | 调用方取消 | 等待排空和释放；是否重算由调用方发新 RequestId。 |
| `IQ-TIM-009 TimedOut` | 截止期已过，且计算已排空 | 不重复使用未归还的帧租约；新尝试须使用新 RequestId。 |
| `IQ-LIF-010 Disposed` | 实例停止接收新请求 | 新建实例/宿主组合后提交新请求。 |
| `IQ-VER-011 UnsupportedVersion` | Contract、模块或 HALCON 版本不在显式支持矩阵中 | 恢复匹配版本组合；不猜相邻版本兼容。 |

上述IQ码仅保留产品映射候选，不能在Core生成第二套错误。服务使用§16的QualityIssue与QS码，首片使用A的MQ码；MessageKey取资源，不增加未声明QualityValidationIssue。模块不自主重试；宿主基于新输入/同一冻结输入和预算明确发起新 RequestId，并能把新请求关联原诊断。异常堆栈只进受控诊断端口，不进本地化 UI 文案。首片使用附录 A 的 `ManagedQualityError`，不实现此后续错误码表。

## 6. 线程、并发、取消、资源和排空

模块输入不可变，原来源借读、scope与适配临时资源的实际Owner和关闭顺序唯一见§16.3–16.6。实例并发固定1、无队列、无跨请求缓存，跨实例总额度由宿主控制；不因HALCON reentrant共享可变句柄。首片Dispose语义见A.2，服务只用StopAsync且必须检查Released，没有Dispose伪释放。

端口工作在后台串行调度，不在状态锁中运行native、关闭或回调。取消/期限仅关闭发布准入，仍持有任务、输入和预算到真实排空；native卡住为DrainUnknown，资源释放失败为ResourcesRetained。RetryRelease只调度未完成阶段，确认归还后才Completion；首次释放失败保留为最终失败。临时资源finally中尝试释放但失败不可吞掉或丢引用。模块不线程强杀、不自行重连/重拍、不改原Owner状态。

scope.Close只在其CheckDrain=Drained且全部依赖invocation已归还后发起；服务创建并持有scopeClose任务，未知/挂起时保留Owner与预留，后续RetryRelease不重复并发调用。Close结果Released=true是本scope对来源的借读归还证明，不授权释放其它消费者租约。读取hash/descriptor相等不能代替借读稳定性、当前来源或授权。

## 7. 无 UI 接入流程与示例

首片无 UI 调用顺序固定为：构造不可变托管灰度快照和区域 → 选择 `ManagedQualityMethodSet` 并冻结参数 → `ImageQualityManagedFactory.Create` → `Validate` → `Evaluate` → 按 RequestId 读取逐指标结果/诊断 → 宿主独立解释适用性。首片不取得帧租约、不等待 native 排空、不发重拍命令。

```csharp
// 顺序说明；完整参数与可构造示例见附录A.2。
using var evaluator = ImageQualityManagedFactory.Create(options, diagnostics);
var request = new ManagedQualityRequest(
    RequestId: Guid.NewGuid(),
    Image: managedGrayImage,
    Regions: regions,
    Methods: methods,
    Budget: budget);

var validation = evaluator.Validate(request);
var result = evaluator.Evaluate(request);
// Evaluate内部重新校验；宿主从结构化结果读取观察。
```

本节示例只是调用顺序，未赋值变量不宣称可编译；附录A.2给出无需辅助函数的完整可构造片段。`QualityRequest`/`EvaluateAsync`产品草图不能用于模块最小host；后续服务用§16唯一端口。

## 8. 可选 WPF 控件契约

控件以独立 `ImageQuality.Wpf` 包交付；不拥有核心实例、帧租约和宿主语言状态。唯一输入和命令意图见§8.1；宿主校验权限并调用§16服务，不存在另一套QualityReport/ReevaluateRequested接口。控件不得直接开始采集、重拍、改生产 ROI、改阈值/方法版本或提交质量判定。

紧凑工作区按“原图和有效域为主、指标/单位/样本数/原因可扫描、直方图和方法细节渐进展开”布局。报告切换时按 RequestId/FrameId/PlaneId 隔离旧选择；未完成、取消、不可观测、执行失败用文字+图形同时区分。禁止只有颜色表达状态或展示通用“质量分”。模块提供宿主可调用的 `SetLanguage(culture)`/刷新资源能力，不在控件内重复设置语言；`zh-CN`、`zh-TW`、`en-US` 文案由独立资源提供并允许宿主扩展。全部按钮/字段、键盘顺序、AutomationId、焦点和错误恢复以§8.1的IQ-WPF-01为唯一模块规格；宿主只映射页面；本稿不替代真实 WPF/UIA 验收。

### 8.1 IQ-WPF-01 模块质量控件规格（可选 WpfSlice-03）

本控件已有架构职责，继续提供可嵌入只读诊断与参数草稿，不增加产品页面、控制相机或预处理编辑器。项目src/Modules/image-quality/Asun.Modules.ImageQuality.Wpf/同名csproj，namespace Asun.Modules.ImageQuality.Wpf，net10.0-windows/UseWPF；引用Core与本机DevExpress25.2.3；viewport经本节IQualityViewerPort由Host注入，不引用viewport实现或宿主页。测试tests/Modules/image-quality/Asun.Modules.ImageQuality.Wpf.Tests/同名csproj；单独WPF测试host只引用本控件和Core，源码放该测试工程。无UICore无需这些依赖。禁止修改共享PageContract，本节是本模块唯一规格，正式宿主页面仅作映射。

角色和闭环：操作员选择原报告→点缺项行→定位其域/原因→把安全下一动作交宿主；工程师选择帧/plane/ROI→查看原量/支持→打开参数草稿→修改使旧预览Stale→显式预览→比较同源两份方法结果→向宿主请求保存草稿。生产参数只读；控件不批准建议、不发重拍，不将选择/排序/直方图缩放写回方法。保存状态与预览状态分别显示：未知结果保留原保存意图并显示“保存结果待确认”，只能查询原意图；只有确认未提交且Drained后才允许当前授权下显式新尝试。源改变保留原意图/草稿为历史候选，不应用到新源。

布局在唯一1920×1080物理验证视口内，先量OS任务栏/边框/宿主标题栏及状态栏后取可用客户区；不把外围空白算影像。顶部44 DIP为源/用途/方法修订与“预览/取消/保存草稿/查询保存”平铺命令（无权限就禁用并给原因）；底部28 DIP为执行状态/有效像素/已持有资源。中部默认影像占宽72%、右侧指标28%，影像占中部全高；右侧上70%为指标Grid，下30%为直方图/参数/来源三个页签。工程展开参数时右侧可到36%，影像仍≥64%；最低内容宽度不足时参数/来源进入侧边Flyout，不隐藏当前身份、取消/恢复和缺项列表。可收起高级图表恢复影像，不新建第二分辨率验证矩阵。文字缩放按当前真实DPI测量，长英文允许两行/列横向滚动，状态/主命令不截成省略号。

DevExpress25.2官方公开XML已核成员：
- DockLayoutManager + LayoutGroup + DocumentGroup/DocumentPanel承载主图/对比，LayoutPanel承载指标；主图与身份区AllowClose=false、AllowFloat=false。布局只由宿主可信流调用SaveLayoutToStream/RestoreLayoutFromStream；恢复前核布局版本/面板白名单，坏布局回默认且保留当前来源/草稿，不从客户任意文件反序列化。
- GridControl + TableView显示“指标/值/单位/有效像素/状态/原因”，显式列；ItemsSource为不可变报告投影，NavigationStyle使键盘行/单元格可达。按区域/方法分组；显示层排序只更新投影，不能重排canonical报告。FocusRowHandle只作视图索引，联动始终用MethodKey/RegionKey/SourceRevision，不把行号当事实Id。
- 需要“源→区域→方法→尺度/分块”的层级时使用同GridControl的TreeListView；默认只展开当前区域与缺项，按需展开tile，不建立两个不同结果树。多选同源行作对比，跨坐标源先显示并列，不强叠层。
- PropertyGridControl.SelectedObject绑定当前强类型参数草稿；ShowCategories按“方法/尺度/可观测要求/资源”分组，默认只露相关字段，未知属性不允许自由新增。变更经同Core.Validate；实际来源/域门在Start，不在UI复制算法。
- ChartControl + BarSideBySideSeries2D，Series.ArgumentDataMember绑定bin原区间标签，ValueDataMember绑定count；高bin数只在显示投影合并到不超过1024柱，原报告Counts不改，range外单列。点击柱显示原区间/count并定位同源ROI，匹配诊断层按§8.2由viewer提供，不改生产阈值。
- DevExpress.Xpf.Core.SuperTip/SuperTipItem提供方法假设、支持缺口、恢复动作；既有宿主tooltip承载，具体模板只用已核成员。DevExpress.Xpf.Editors.Flyout.FlyoutControl承载参数/来源详情。关键动作平铺，不为效果隐藏于DropDown。主题跟随宿主应用资源；控制实例不写全局Theme/Culture。无闪烁动画，Busy仅轻量指示，不对高频数值做连续位移动效。

控件公开入口只存在于Wpf，不污染Core：
~~~csharp
public interface IQualityViewerPort
{
    FrameworkElement View { get; } // 宿主提供已建立的viewport公开控件
    void Select(QualitySourceDescriptor source, QualityBox bounds, string layerKey);
    void Clear();
}
public sealed record QualityViewPermissions(bool CanPreview, bool CanSaveDraft);
public sealed record QualityViewContext(
    QualityServiceRequest Request,
    ImmutableArray<QualitySourceDescriptor> Sources, string UsageKey);
public sealed record QualityPreviewIntent(
    Guid ViewGeneration, QualityServiceRequest Request);
public sealed record QualityRegionIntent(
    Guid ViewGeneration, QualitySourceRef Source, QualityBox Bounds);
public sealed record QualityDraftSaveIntent(
    Guid IntentId, Guid ViewGeneration,
    ImmutableArray<QualitySourceRef> Sources, QualityMethodPlan Draft);
public enum QualitySaveKnowledge
{
    Unknown = 1, ConfirmedNotCommitted = 2, ConfirmedCommitted = 3
}
public enum QualitySaveActivity { Pending = 1, DrainUnknown = 2, Drained = 3 }
public sealed record QualityDraftSaveResult(
    QualityDraftSaveIntent Intent, Guid? QueryId, long Sequence,
    QualitySaveKnowledge Knowledge, QualitySaveActivity Activity,
    QualityIssue? Issue);
public sealed record QualitySaveStatusQuery(
    Guid QueryId, QualityDraftSaveIntent Intent,
    TimeSpan MaxWait, DateTimeOffset DeadlineUtc);
public sealed class ImageQualityPanel : UserControl
{
    public ImageQualityPanel(); // 等价TimeProvider.System，供XAML
    public ImageQualityPanel(TimeProvider clock);
    public TimeProvider Clock { get; }
    public void Bind(QualityViewContext context, QualityServiceReport? report,
        IQualityViewerPort viewer, IImageQualityService validator,
        QualityViewPermissions permissions, Guid viewGeneration,
        QualityDraftSaveResult? retainedSave);
    public void SetExecution(Guid viewGeneration, QualityOperationSnapshot snapshot);
    public void ApplyPreviewResult(Guid viewGeneration, QualityOperationResult result,
        Guid requestId);
    public void ApplySaveResult(QualityDraftSaveResult result);
    public QualityDraftSaveIntent? GetPendingSaveIntent();
    public Guid RequestSaveStatus(TimeSpan maxWait, DateTimeOffset deadlineUtc);
    public void CancelSaveStatusWait();
    public void BindComparison(Guid viewGeneration,
        QualityServiceReport left, QualityServiceReport right);
    public void SetLanguage(CultureInfo culture);
    public void SetPermissions(QualityViewPermissions permissions);
    public void CloseView();
    public event Action<QualityPreviewIntent>? PreviewRequested;
    public event Action<Guid>? CancelRequested; // 当前预览RequestId
    public event Action<Guid>? PreviewRecoveryRequested; // 查询原pendingRequestId，不重新Start
    public event Action<QualityDraftSaveIntent>? SaveDraftRequested;
    public event Action<QualitySaveStatusQuery>? SaveStatusRequested;
    public event Action<Guid>? SaveStatusWaitCancelled; // 仅取消QueryId的观察等待
    public event Action<QualityRegionIntent>? RegionSelectionRequested;
}
~~~
这是待实现的公开成员规格（方法体不在文档中），不是已实现示例；System.Windows/Controls与System.Globalization只属于Wpf。控件不拥有viewer、service或图像租约；CloseView退订并禁止新意图，清本方显示引用，不调用宿主viewer.Dispose或释放像素。宿主处理命令后用新viewGeneration+精确报告Bind；迟到预览只有generation/source/method都一致才显示，语言切换保持当前草稿/选中/在途generation。SetLanguage只接受宿主文化，不提供重复切换入口。

预览状态Ready/Busy/Empty/Stale/Blocked/Failed分别为“就绪/计算中/无报告/预览已过期/缺少依据/计算失败”；单指标“已计算/无法评价/不支持”。zh-TW对应“就緒/計算中/無報告/預覽已過期/缺少依據/計算失敗”，“已計算/無法評估/不支援”；en-US对应“Ready/Calculating/No report/Preview out of date/Evidence missing/Calculation failed”，“Calculated/Not observable/Unsupported”。这些短句是资源值，错误显示具体原因和恢复，不显示“智能优化/极致/质量合格”。所有控件自动文本、空记录、校验和SuperTip随同宿主三语切换；数值显示文化可变，计算/序列化不变。

键盘顺序：源/plane→ROI→指标行→图表→草稿→预览/取消/保存；Ctrl+Enter请求预览，Esc在Busy时请求取消（不直接终止service），F6在影像/指标/草稿循环，Ctrl+S仅保存草稿且需权限。AutomationId固定Quality.Source、Quality.Viewport、Quality.Metrics、Quality.Histogram、Quality.Parameters、Quality.Preview、Quality.Cancel、Quality.SaveDraft、Quality.SaveQuery、Quality.SaveStatus、Quality.Status；状态文本与图标同时表达，不靠红绿。列表/TreeList虚拟化，只实例化可见tile；新结果整批替换，不每像素Dispatcher更新。预览/热图按需读取，关闭、隐藏和源切换取消本方显示请求并归还本方副本，原算法仍按真实排空。UI刷新按宿主Profile有界合并，完成/错误状态不丢；测首次可见/选择联动/切语/布局恢复、分配与关闭回收，不宣称未测帧率。

### 8.2 挂接、回执、草稿与本地化闭环

Bind只在控件Dispatcher线程调用；context/viewer/validator/culture非null，generation非空，context.Request必须通过同validator.Validate，Sources与请求SourceRef逐一对应；参数错抛ArgumentException/ArgumentNullException（宿主编程错误），不伪装质量结果。Viewer.View必须无其它可视父级，否则拒绝挂接，不从另一窗口偷走控件。validator只借用来Validate，控件不调用Start/StopAsync/Dispose。初始草稿是当前方法的不可变副本；PropertyGrid编辑投影后构造同类型QualityParameters，并替换原Request对应Method，而非反射修改运行中参数。选择源/区域/方法只改变当前投影，不更新生产事实。

预览：允许且Validate通过→复制context.Request，RequestId=新Guid并替换选中方法草稿→PreviewRequested(ViewGeneration,完整Request)；显示Busy并登记pendingRequestId，宿主调用同服务Start。无事件订阅时按钮禁用并提示“未连接预览处理”；不能假Busy。宿主把Snapshot传SetExecution、最终结果传ApplyPreviewResult，控件核generation、requestId、源/方法参数均与pending匹配；旧代次/旧请求直接忽略。Busy期间可改草稿但不得覆盖已提交参数；草稿变更后旧预览显示Stale且不能保存为已验证参数。CancelRequested只发pendingRequestId一次；显示“正在停止”直到宿主报告真实资源终态，不把点击取消当已停。

保存：仅CanSaveDraft、当前草稿合法且最近匹配预览完成、Required量可观测并且没有未决保存意图时，才能首次发SaveDraftRequested。发出前冻结QualityDraftSaveIntent的IntentId、ViewGeneration、Sources及完整Draft，保存Knowledge=Unknown、Activity=Pending；本方不创建持久IO或当前主体快照。宿主在任何写入前登记该不可变意图，执行当前主体/源修订/写入权限与持久事务校验。事件正常返回只证明调用结束，不证明未提交/已提交；回执按§8.3接收。Unknown、未排空和事件异常期间禁用新Save，不分配新IntentId、不重发SaveDraftRequested。显示查询保存命令并查询原意图；ConfirmedCommitted只表示草稿已保存，不是生产激活。ConfirmedNotCommitted且Activity=Drained、无其它未决尝试时，才可当前权限/源/预览重验后显式新IntentId。未连接SaveDraftRequested或SaveStatusRequested任一处理器时首次保存禁用并给原因。撤权或完整Bind换generation不能取消/清除原保存意图；处理规则见§8.3。

比较：BindComparison仅只读显示；两份报告都必须属于当前context的SourceRef/坐标/区域；同源但方法/参数不同可并列值/原单位/支持，不生成“提升百分比”质量结论。跨源/坐标报告只在宿主切换context后独立查看，不强叠层。右指标选择通过IQualityViewerPort.Select(source,bounds,layerKey)联动，layerKey固定quality.roi / quality.support / quality.clipped-low / quality.clipped-high / quality.response；viewer不支持热图数据时只定位框/原源，不从缺失数据生成假覆盖。模块不读像素产生第二算法；真实热图由宿主具公开输入资格的viewer提供，加载/取消/副本生命周期归viewer Owner。

联动实施边界：`Select`只传Source/Bounds/layerKey，不携带灰度区间、参数或响应像素；`QualityServiceReport`也不承诺响应图。柱选择因此显示原bin上下界/count并定位同源ROI，不能仅凭layerKey让viewer画“此bin像素”或让另一个方法的响应覆盖当前方法。真实viewer若有宿主预先绑定的同来源/坐标/完整方法参数诊断层，可按该层显示；无法唯一匹配、缺层或跨方法比较时退回quality.roi定位，并显示资源键 `ImageQuality.Tip.RegionLocationOnly` 的“仅定位区域/僅定位區域/Region location only”。不支持诊断层仍满足当前公开viewer合同，真实诊断像素的生成/持有须由对应Owner已有公开能力提供，不由本模块增加隐藏像素接口；这不声称已交付热图资格。图表原counts及全部Required缺项仍保留。

视觉实施：随宿主主题取背景/前景/强调/边框资源，影像使用中性深底，数据区用低对比边框与清楚文字；颜色不承载唯一状态。区间距8 DIP、外边距12 DIP、常规文字14 DIP、节标题16 DIP，数值右对齐，单位独立列，状态以图标+短句呈现；只读值、草稿、历史待确认区有固定标题，不以闪烁强调失败。Grid显示顺序固定身份→数值/单位→支持→状态/原因，默认不展开所有tile。查看参数默认展示所选route强类型字段与Policy，条件不适用字段只读并说明原因，不偷偷清参数。切语复用同一实例投影并保持焦点/选择/滚动/草稿；图标按钮必须有可见文字或三语SuperTip/UIA名称。图像缩放/平移归注入viewer已有能力，模块只定位，不新增不受合同约束的缩放命令；运行中的取消/原保存查询保持平铺可达。按§8.1唯一1920×1080真实可用客户区验影像占比、三语长句与上述层级，视觉品质和键盘可用性分别判定。

CloseView终止该控件实例：停止新预览/保存/查询意图，取消本方QueryId观察等待并退订本方绑定、清计时器与可视引用；不调用viewer.Dispose/Clear、不关闭validator，也不取消保存事务。宿主在退订/关窗前读取GetPendingSaveIntent并核自己的保存登记记录，关窗后继续查询/排空/恢复该原IntentId，不依赖控件回调完成事务；移交细节与有界保留见§8.3。关闭后改变入口抛ObjectDisposedException，ApplySaveResult/ApplyPreviewResult迟到安全忽略，不能据忽略判事务未提交。Bind新generation只重建当前预览/编辑投影，原未决保存独立保留为历史待确认；主题/三语改变不修改原意图。保存事件订阅者抛错且尚无确认回执时仍为Unknown，前一监听者可能已开始写入；显示“保存结果待确认”，查询原意图。已有合法确认回执不因后续监听者异常降级。预览回调异常也不推定请求未接纳；保留pendingRequestId，由Host核原服务operation并投影状态，不能自动重发。

Wpf包内Resources/ImageQuality.zh-CN.resx、zh-TW.resx、en-US.resx是未来实现落点，不在本文另建资源文件。全部Key唯一以ImageQuality开头：Command.Preview/Cancel/SaveDraft/QuerySave/CancelSaveWait、Save.<知识/活动/恢复名>、Column.Metric/Value/Unit/ValidPixels/State/Reason、Field.<公开参数名>、Route.<枚举名>、Unit.<枚举名>、State.<枚举名>、Quality.<原因码>、Error.<MQ/QS后缀>、Tip.<行为名>；没有自由异常字符串替代资源。文化回退链为宿主指定culture→其父文化→zh-CN；额外语言通过宿主WPF资源覆盖同键，模块不写全局CurrentCulture。动态切换须刷新当前行、SuperTip、PropertyGrid名/校验、图例与DevExpress自动空记录文本。中文、繁体、英文均须资源完整性枚举测试，缺键退出非0。

| 文案组/恢复语义 | zh-CN / zh-TW / en-US 资源值 |
|---|---|
| 主命令/列 | 预览/預覽/Preview；取消/取消/Cancel；保存草稿/儲存草稿/Save draft；指标/指標/Metric；值/數值/Value；单位/單位/Unit；有效像素/有效像素/Valid pixels；状态/狀態/State；原因/原因/Reason |
| 支撑/纹理/曝光缺项 | 缺少所需原量/缺少所需原量/Required raw metric unavailable；无有效像素/無有效像素/No valid pixels；有效像素不足/有效像素不足/Too few valid pixels；覆盖不足/覆蓋不足/Insufficient coverage；纹理不足/紋理不足/Insufficient texture；低端截断过多/低端截斷過多/Too much low clipping；高端截断过多/高端截斷過多/Too much high clipping |
| 方法/依据缺项 | 无法估计噪声/無法估計雜訊/Noise cannot be estimated；方向响应不足/方向響應不足/Insufficient directional response；缺少辐射标定依据/缺少輻射校正依據/Radiometric evidence missing；缺少投影步骤/缺少投影步驟/Projection step missing；缺少组来源依据/缺少組來源依據/Group evidence missing；不支持此掩膜/不支援此遮罩/Mask not supported；不支持此像素类型/不支援此像素類型/Pixel type not supported；不支持此方法变体/不支援此方法變體/Method variant not supported |
| 请求/预算/状态错误 | 请求无效，请检查参数/請求無效，請檢查參數/Invalid request; check parameters；资源不足，请缩小范围/資源不足，請縮小範圍/Resource limit exceeded; reduce the range；正在计算，请稍后重试/正在計算，請稍後重試/Calculation in progress; try again later；已停止接收，请重新打开/已停止接收，請重新開啟/Service stopped; reopen；不支持此版本，请恢复匹配版本/不支援此版本，請還原相符版本/Version not supported; restore matching versions |
| 输入/执行错误 | 图像输入无效，请检查来源/影像輸入無效，請檢查來源/Invalid image input; check the source；区域无效，请检查边界/區域無效，請檢查邊界/Invalid region; check bounds；方法参数无效，请修正/方法參數無效，請修正/Invalid method parameters; correct them；来源已变化，请重新选择/來源已變更，請重新選擇/Source changed; select it again；计算失败，请查看诊断/計算失敗，請查看診斷/Calculation failed; check diagnostics；结果无效，请查看诊断/結果無效，請查看診斷/Invalid result; check diagnostics；运行时已变化，请重新打开/執行環境已變更，請重新開啟/Runtime changed; reopen |
| 取消/关闭/保存恢复 | 正在停止/正在停止/Stopping；计算已取消/計算已取消/Calculation cancelled；计算超时，等待资源归还/計算逾時，等待資源歸還/Calculation timed out; waiting for resources；停止等待，后台仍在关闭/停止等待，背景仍在關閉/Wait cancelled; closing continues；资源未归还，请重试关闭/資源未歸還，請重試關閉/Resources retained; retry closing；调用重入，请查看诊断/呼叫重入，請查看診斷/Reentrant call; check diagnostics；保存结果待确认/儲存結果待確認/Save outcome unconfirmed；查询保存/查詢儲存/Check save status；已确认未保存，可重新尝试/已確認未儲存，可重新嘗試/Not saved; a new attempt is allowed；已停止等待，保存仍由宿主处理/已停止等待，儲存仍由主程式處理/Wait stopped; the host still owns the save；草稿已保存/草稿已儲存/Draft saved |
| 绑定/数值/未接入 | 数值超出范围，请检查输入/數值超出範圍，請檢查輸入/Numeric range exceeded; check input；未连接预览处理/未連接預覽處理/Preview handler not connected；未连接保存处理/未連接儲存處理/Save handler not connected；请求状态待确认/請求狀態待確認/Request status unconfirmed；无法查询保存，请检查宿主/無法查詢儲存，請檢查主程式/Save status unavailable; check the host |
| 保存知识/恢复补充 | 保存尚未结束，等待确认/儲存尚未結束，等待確認/Save still active; awaiting confirmation；草稿已保存，等待结束/草稿已儲存，等待結束/Draft saved; waiting for completion；原来源保存待确认/原來源儲存待確認/Save for the original source is unconfirmed；停止等待/停止等待/Stop waiting；保存回执不匹配，请检查宿主/儲存回覆不符，請檢查主程式/Save receipt mismatch; check the host；保存回执冲突，请检查宿主/儲存回覆衝突，請檢查主程式/Save receipts conflict; check the host；保存记录容量不足，请处理待确认记录/儲存記錄容量不足，請處理待確認記錄/Save record capacity reached; resolve pending records |

字段/方法/单位的资源标签按其技术语义翻译，不能显示C#成员名。KernelResponse=“核响应/核心響應/Kernel response”，KernelResponseSquared=“核响应平方/核心響應平方/Squared kernel response”，GrayLevel=“灰度码/灰階碼/Gray level”，Count=“计数/計數/Count”，Fraction=“比例/比例/Fraction”。Language与权限试验以真实控件检验：中→繁→英不丢草稿/焦点，长英文允许两行且取消可达；行选择/显示分箱不改变canonical报告；关闭无本方事件残留；版本布局恢复失败回默认而非丢源。

### 8.3 保存知识、原意图查询与宿主责任（2026-10-10 定向收口）

本节只冻结WPF保存知识投影及Host挂接；真实持久IO、提交证据、幂等/恢复与当前主体始终归Host原Owner，不增加模块存储器、自动重试器或第二保存事实权威。§8.1的QualityDraftSaveResult是唯一回执，无QualitySaveResult别名或bool Saved兼容形状。尚未实现/发布；保存知识/原意图查询定向修订已由主控接收，整个WpfSlice-03仍按§24.1等待其余规格接收。

| Knowledge / Activity | 可显示的事实与允许动作 |
|---|---|
| Unknown / Pending | 原意图可能尚未提交、已提交但回执未到、或仍在处理；显示“保存结果待确认”。可查询同意图，禁止新保存/重发原写入。 |
| Unknown / DrainUnknown | 无法确认写入工作是否退出；显示“保存尚未结束，等待确认”。保留原身份，由Host恢复/对账，不强杀、不新尝试。 |
| Unknown / Drained | 工作已结束仍不能确认提交事实；显示“保存结果待确认”。排空不等于未提交，只能查原意图/Host对账。 |
| ConfirmedCommitted / Pending或DrainUnknown | 已有真实提交证据，但释放/工作退出未确认；显示“草稿已保存，等待结束”。禁新保存，Host继续排空/归还；不能再次提交。 |
| ConfirmedCommitted / Drained | 原意图草稿保存且执行已排空；显示“草稿已保存”。以后只有用户显式编辑、重新预览和当前授权才能发新的独立保存；同一已保存草稿不重复提交。 |
| ConfirmedNotCommitted / Drained | Host已证明该原意图没有提交效果且没有迟到提交的在途工作；显示“已确认未保存，可重新尝试”。重验当前主体/源/草稿/预览后用户显式新IntentId，不自动重试。 |

ConfirmedNotCommitted+Pending/DrainUnknown是非法组合；没有receipt、查询NotFound、连接失败、等待取消/超时、权限被撤或事件抛异常均不是ConfirmedNotCommitted。ConfirmedCommitted只依据Host原持久化Owner的提交/读回证据，不能由控件推测或仅用回调完成赋值。当前权限决定能否开始新写入，不反向改写历史保存知识。

**公开查询与接收步骤**
1. 首次保存前复制并冻结原意图；IntentId/ViewGeneration非空，Sources非Default且顺序/SourceId/Revision唯一并与提交时context一致，Draft为提交时全部参数的不可变快照。在控件状态中先登记Unknown/Pending，再调用事件，避免同步回执早于登记。SaveDraftRequested与SaveStatusRequested应各由一个明确Host Owner处理，不把多个监听者分别当事务Owner；若发生多播监听者异常，仍执行以下保守规则。
2. GetPendingSaveIntent在Dispatcher线程返回当前尚未解决（Unknown、Activity非Drained或存在回执冲突阻断）的原不可变意图，已确认且Drained且无冲突阻断则null；关闭后该读取入口返回null仅表示控件已清显示记录，不证明Host台账已清；它不发IO、不生成新Id、不从当前context重建Sources。Host拿到的是值快照而非图像lease。即便草稿已编辑/Bind换代，返回的仍是旧保存意图。
3. RequestSaveStatus(maxWait,deadlineUtc)只查询当前原未决/冲突阻断意图。maxWait必须0<且≤30秒，DeadlineUtc须是当前UTC之后、至多30秒；实际等待取二者较早值并用单调计时。本控件最多一个待观察QueryId；已有查询未完成时抛InvalidOperationException，不派发第二查询。无未决意图/查询处理器时抛InvalidOperationException，UI给对应原因并保留原保存身份。参数非法抛ArgumentException，已关闭抛ObjectDisposedException。
4. 为每次查询生成新的QueryId，保存IntentId不变。登记观察等待后发SaveStatusRequested(QueryId,原Intent,maxWait,deadlineUtc)；Host只查询自己的登记/真实IO状态，有限观察等待取query.MaxWait/query.DeadlineUtc较早值。每原Intent最多一个真实查询工作项；观察超时后底层查询尚未返回时保留其任务/Owner与预算，后续同Intent查询复用该工作状态或返回Unknown，不叠加无界查询。Host只保留当前/最近QueryId映射，原保存Owner独立保留，不把查询当写入/重新提交，也不使用当前viewGeneration替换原保存generation。事件抛异常时结束本次观察等待但保留原意图、知识和Activity，显示“无法查询保存，请检查宿主”；首次保存事件抛异常且意图未解决、没有活动查询时派发一次有界查询（maxWait=5秒、deadlineUtc=当前UTC+5秒），不反复轮询。已存在查询就等待该查询，已确认且Drained不多发查询。若在异常前已同步收到合法已确认回执，保留确认事实，不退回Unknown。
5. ApplySaveResult先验证IntentId、原ViewGeneration、Sources逐项SourceId/Revision/顺序及Draft的全字段/枚举/嵌套数组结构值相等；不能用ImmutableArray引用Equals或只比MethodRevision。验证针对保留的原意图，非当前页面context。Sequence为Host按原IntentId分配的正long单调证据序号，QueryId=null表示Host主动投影；非空QueryId必须关联曾派发的同原意图查询。初次恢复投影同样须完整绑定。未知Id/畸形枚举/来源冲突不得更新状态；与保留IntentId相同而内容冲突时置冲突阻断，完全无关Id只丢弃并显示诊断；显示“保存回执不匹配，请检查宿主”并保留原意图供查询。
6. 每意图只接收Sequence更高的合法事实；QueryId是观察关联，不是保存事实的一部分，同序Knowledge/Activity/Intent/Issue相同即幂等，匹配当前QueryId仍结束当前等待、较旧回执忽略、同序冲突显示“保存回执冲突，请检查宿主”。合法Knowledge只能Unknown→一个确认状态，确认后不降Unknown、不在ConfirmedCommitted/ConfirmedNotCommitted间翻转；Activity一旦Drained不能回Pending/DrainUnknown。矛盾的较高序号同样不覆盖已有事实，置本方回执冲突阻断并保留原意图可查询；即使已确认且Drained也不允许新Save。只有Host查询返回更高序号、原确认事实不变且Drained的对账投影才能解除阻断；仍互相矛盾则继续阻断，不能删除原意图绕过。事件异常/查询超时是观察问题，不能制造新的Host事实Sequence。
7. QueryId决定哪个观察等待结束，IntentId/Sequence决定保存知识是否更新：本轮查询的同Id回执结束本轮等待；已取消/超时查询的迟到回执，在保留的最近QueryId与原意图相符且Sequence合法时仍可改善原保存知识，不重开已结束等待。下一次查询替换最近QueryId后，更旧查询回执不进入控件，但Host仍必须接收/保留其事务证据；Host可用QueryId=null主动投影最新事实。未知QueryId不接受。控件只保留一个活动/最近查询记录，避免无限查询表。
8. CancelSaveStatusWait取消本方计时器/观察等待，并通过SaveStatusWaitCancelled(QueryId)通知Host停止该观察等待；事件异常隔离。超时走同一观察退出路径。两者不取消持久事务、不修改Knowledge/Activity、不清IntentId，也不授权新Save。保存中的“取消”仍只取消预览RequestId；查询区域单独提供“停止等待”（AutomationId=Quality.SaveWaitCancel），键盘查询与停止等待排在保存命令之后，Esc在该查询区域仅结束观察，不能取消持久事务。预览Ready/Busy/Stale与保存知识/Activity显示为两个独立状态区，保存未知不伪造计算Failed/Ready。无新用户动作不自动重复查询。
9. QualityDraftSaveResult.Issue：ConfirmedCommitted必须null；ConfirmedNotCommitted必须带Host已确认未提交的结构化原因；Unknown可null（处理中）或有问题。Issue只为说明，不能由Code推断Knowledge。保存回执本方校验错误资源键固定ImageQuality.Save.InvalidReceipt / ConflictingReceipt / Unknown / DrainUnknown / ConfirmedCommitted / ConfirmedNotCommitted / QueryUnavailable / WaitStopped / WaitingForDrain / CapacityExceeded；它们不新增Core MQ/QS故障。
10. 已确认未提交且Drained后的新尝试必须新IntentId，原意图只读保留为最近完成记录；若当前generation/源修订已变，不将旧Draft直接保存到新源，须明确重新绑定/编辑/预览。Host始终在新的写入前重验当前主体与实际目标权限；控件CanSaveDraft只提供UI能力投影，不是持久授权凭证。

**换代、撤权、关窗与有界保留**
- 一个控件至多保留1份未决/冲突原保存意图、1份最近完成投影和1份活动/最近查询，全部只含受预算约束的Sources/Draft/诊断值，不留图像/native/数据库连接。未决意图不因TTL、Bind次数、等待超时、撤权或关窗当作未保存/被安全删除。未决时所有新的Save（包括新generation草稿）均禁用，可继续独立预览/查看，保存区域明确标“原来源保存待确认”，不覆盖当前来源的已保存标记。
- ApplySaveResult若属于保留旧generation，更新历史保存区与新保存准入，不改变新context草稿/影像/当前预览；不同SourceRevision不能把旧ConfirmedCommitted显示为新源已保存。Host撤权后完整Bind权限投影为不可保存，旧回执仍可更新保存事实；查询由Host按当前主体授权显示，查询被拒绝仍Unknown并转授权Host恢复，不能重新提交。
- 重开控件时Bind新增的retainedSave可由Host提供自己的最新合法原意图投影（包括旧generation）；该参数只恢复值知识、不触发保存。Bind已有未决意图时retainedSave=null表示保持原记录，非空仅允许同IntentId一致投影；不允许以另一意图覆盖。恢复retainedSave须QueryId=null、Sequence正、绑定完整且符合知识/活动组合，不能恢复未知QueryId观察等待；初次有效投影不调用ApplySaveResult制造新Id。新控件没有retainedSave时只表示没有本方显示记录，不证明Host无未决保存；Host在允许新Save前必须核真实未决台账。恢复已确认且Drained结果只保留为最近完成，不能反向当当前源已保存。
- Host必须在任何持久写入前把原意图与真实任务Owner/目标映射登记成功；登记失败证明未执行任何写入且已排空时方可ConfirmedNotCommitted。登记记录不能依赖控件存在、事件订阅或返回顺序。Host按已有持久化权威的有限容量/保留与恢复规则接入，容量不足在写入前拒绝新增意图；未解决记录转该原Owner可恢复台账，不能靠无限内存或丢记录取得容量。本模块不定义新的存储Schema/工程。
- Host关闭窗口前调用GetPendingSaveIntent核登记，解除UI回调订阅后CloseView释放本方引用；Host继续持有原IntentId/源/草稿与真实任务直到已确认知识且Drained。查询等待取消或UI对象回收不结束该责任；迟到提交回执进入Host台账，不向已关闭Dispatcher投递。CloseView不因移交异常阻止清本方显示，也不谎报保存资源已释放；若Host未能完成可恢复移交，Host不得退出负责该事务的Owner，应显示恢复问题并保留未决状态。
- CloseView退订并清全部本方事件委托/定时器，包括SaveStatusRequested/SaveStatusWaitCancelled与保存回执挂接；它不销毁Host台账。宿主使用自己的当前主体、已授权查询路径和关闭/恢复机制完成对账；资料不可查询时保持Unknown，阻断受影响目标的新写入，不阻无关图像计算。

**挂接样例与两轮定向反例（规格样例，未运行WPF/持久IO）**

示例绑定原IntentId=11111111-1111-1111-1111-111111111111、generation=22222222-2222-2222-2222-222222222222、Sources=[gray-1/rev-1]与完整Draft d1。Host已登记，真实IO提交后通信断开：ApplySaveResult(Intent原快照,QueryId=null,Sequence=1,Knowledge=Unknown,Activity=Drained,Issue=宿主“回执未知”原因)。UI保留原Id→RequestSaveStatus(5秒,当前UTC+5秒)生成QueryId q1→SaveStatusRequested原Intent→Host查询原记录→ApplySaveResult(Intent原快照,q1,Sequence=2,ConfirmedCommitted,Drained,null)。只发生一次写入；q1超时后Sequence=2迟到仍能更新保留原意图，不能把超时变成第二次保存。若真实查询确认无提交且无迟到工作，则Sequence=2/ConfirmedNotCommitted/Drained/非空Issue，重新通过权限/源/预览校验后用户才可新IntentId。

| 定向轮次/用例ID（Wpf.Tests） | 反例与可判定断言 |
|---|---|
| 第一轮 IQ.SAVE.01：知识/活动 | 已提交但丢回执、Unknown+Drained、NotFound、查询权限拒绝：均保留原IntentId且新Save次数0；只有ConfirmedNotCommitted+Drained才允许新尝试。ConfirmedCommitted+Pending仍不能新保存。 |
| 第一轮 IQ.SAVE.02：多播/同步异常 | 首监听者已开始IO，后监听者抛错；不能“请求未提交”/生成新Id，查询次数至多1次。若首监听者已同步ConfirmedCommitted，后异常不降级保存知识。 |
| 第一轮 IQ.SAVE.03：查询/等待 | q1取消/超时只结束观察；q1合法迟到确认可改善原知识；再查询q2只换QueryId不换IntentId，不重复写入；更旧q1回执交Host保留而不覆盖控件最新查询。 |
| 第二轮 IQ.SAVE.04：代次/来源/顺序 | Bind g2与rev-2后原g1/rev-1确认更新历史保存区，不标新源已保存；错误Sources、同序冲突、较旧Sequence与确认后降级均不覆盖知识，冲突阻断保存并交Host对账。 |
| 第二轮 IQ.SAVE.05：撤权/关窗/容量 | 撤权可禁止新Save但不能把在途保存改未提交；CloseView清事件/计时器，Host原记录仍可查询/恢复，重开retainedSave不会发新Save；容量拒绝不丢未决记录/不绕过Owner。 |
| 第二轮 IQ.SAVE.06：预览与保存分离 | 新预览Completed或Cancelled不改变旧保存Unknown；停止查询等待不取消持久IO；修改草稿不覆盖已提交Draft，最终确认只绑定原快照。 |

以上为两轮定向内容自审与后续真实Wpf.Tests/Host契约断言，没有扩大算法或重审已接收Core。Host真实存储/权限/退出恢复仍是其原集成门，WpfSlice-03自身API/挂接/知识/保留语义必须先接收，不能将它们伪作外部客户门。



### 8.4 公开Presenter、权限刷新与原保存Owner端口（2026-10-11）

本节补齐WpfSlice-03接线，不变更已接收§8.1–8.3的原意图/知识/活动/查询/迟到规则。所有声明在Asun.Modules.ImageQuality.Wpf，依赖Core的§16.10根槽；Presenter不写文件/数据库、不造质量放行、不接管Host持久化事务。下列Owner端口是Host已有保存权威的适配面，不是新的存储器；槽绑定只关联UI恢复责任，不把SlotId当保存目标/事务身份。

~~~csharp
public sealed record QualityDraftSaveRegistration(
    IQualityDraftSaveOperation? Operation, QualityDraftSaveResult Receipt);
public interface IQualityDraftSaveOperation
{
    QualityDraftSaveIntent Intent { get; }
    Task<QualityDraftSaveResult>? OriginalWrite { get; }
    Task<QualityDraftSaveResult>? OriginalQuery { get; }
    QualityDraftSaveResult GetSnapshot();
    void BeginWrite();
    void BeginQuery(QualitySaveStatusQuery query);
    void EndQueryObservation(Guid queryId);
}
public interface IQualityDraftSaveOwner
{
    QualityDraftSaveRegistration Register(
        Guid hostSlotId, QualityDraftSaveIntent intent);
    IQualityDraftSaveOperation Get(Guid intentId);
    QualityDraftSaveResult? GetRetained(Guid hostSlotId);
    event Action<QualityDraftSaveResult>? ReceiptChanged;
}
public sealed record QualityPresenterDetachResult(
    Guid HostSlotId, QualityDraftSaveIntent? PendingSave,
    Task<QualityCloseResult> CleanupObservation);
public sealed class ImageQualityPresenter
{
    public ImageQualityPresenter(
        ImageQualityPanel panel, QualityHostSlot hostSlot,
        IQualityDraftSaveOwner? saveOwner, TimeProvider clock);
    public void Attach(
        QualityViewContext context, QualityServiceReport? report,
        IQualityViewerPort viewer, QualityViewPermissions permissions,
        Guid viewGeneration, CultureInfo culture);
    public void Rebind(
        QualityViewContext context, QualityServiceReport? report,
        QualityViewPermissions permissions, Guid viewGeneration);
    public void RefreshPermissions(QualityViewPermissions permissions);
    public void SetLanguage(CultureInfo culture);
    public void ObserveRetainedPreview();
    public QualityPresenterDetachResult Unbind();
}
~~~

ImageQualityPanel的显式clock构造只保存同一TimeProvider；查询预算校验/单调等待统一用该Clock，纯UI Dispatcher刷新仍只是呈现。参数less构造仅委托TimeProvider.System；其它clock的Host须显式new ImageQualityPanel(clock)，不能混用系统UTC和固定时钟。ImageQualityPanel在§8.1同一class新增公开成员public void SetPermissions(QualityViewPermissions permissions);与public event Action<Guid>? PreviewRecoveryRequested;。SetPermissions只刷新命令能力/原因，不重建草稿、不换generation、不清保存知识；两者沿原Dispatcher/CloseView终态，不新增第二控件。RefreshPermissions调用前者，不用完整Bind模拟撤权而丢当前编辑。后者只发原pendingRequestId，连接Presenter.ObserveRetainedPreview；等待到期后在原取消/预览区域平铺“查询预览/查詢預覽/Check preview”，AutomationId=Quality.PreviewQuery，不用新PreviewRequested重算。

**输入、权限、保存原Task**
- Presenter构造只校验参数，必须同panel.Dispatcher线程、hostSlot已由进程根持有且Service非null、原构造Task已真实成功；panel.Clock、hostSlot.Clock与传入clock必须ReferenceEquals，Service使用同一root时钟。它不调用factory，也不抢其它Owner的槽。一个panel/slot只能一份活动Presenter，Attach一次；重复Attach或终止后Rebind拒绝。构造/Attach未触发IO前的失败不产生保存Unknown或假drain，但根槽仍按原service Close确认。
- 保存Owner的Register在BeginWrite前同步完成原Intent/目标/当前主体准入及有界登记；不能在返回Operation之前启动IO。首次接纳的Receipt=Unknown/Pending，Sequence=1，完整原Intent相等、QueryId=null，Operation非null且Intent相等；拒绝时Operation=null，Owner明确证明尚未启动写入且无迟到副作用，返回ConfirmedNotCommitted/Drained/非空结构原因。容量拒绝在写入前发生；若确实不能证明未写，必须保留已登记原Operation并返回Unknown，不能假拒绝。
- BeginWrite仅第一次执行；Owner必须先将OriginalWrite原Task存入原Operation/自己的进程或持久恢复登记，再派发实际IO，重复BeginWrite不重新提交。同一个IntentId再次Register只在完整原意图结构相等且同Host绑定时返回原Operation/当前Receipt，不重分配Sequence；同Id内容冲突拒绝并保留原Owner。同步异常可能已启动工作；Get(IntentId)仍取得该原Operation/Task并保留Unknown，按原意图查询，不靠方法离栈结束它。OriginalWrite实际结束/Drained不等于是否提交，GetSnapshot/回执知识依据Owner提交或对账证据。没有IO的内存示例同步完成即可Drained，无native排空。
- BeginQuery核同原Intent，先登记OriginalQuery和QueryId，再开始只读查询；每Intent最多一个真实查询Task。此前查询原Task仍在途时新QueryId只重新关联观察，复用原查询或投影Unknown，不能叠IO。EndQueryObservation只停止这个QueryId观察，不取消写入/真实查询或删除Owner登记。Query/Receipt知识转移、序号与Issue严格沿§8.3，不定义第二状态机。Owner主动ReceiptChanged的QueryId=null；只传有界不可变值，不传Exception、连接或图像。
- Owner的GetRetained(slotId)按Host绑定的原真实保存目标，从自己的有界登记取最近未解决（优先）或最近完成投影；不从panel反推。SlotId只是显示/恢复关联，不是目标身份；换窗口/新槽仍查询同目标未决意图，Register在同目标有未解决记录时拒绝新意图，不能按新SlotId绕过。Owner只在真实Confirmed知识且Drained、无冲突后可释放该记录的任务/资源；新意图需要当前主体/目标资格重验。控件CanSaveDraft不是写入授权，真实Owner在Register与实际提交边界均以自己当前授权/fence为准；撤权、关窗和新generation不改旧提交事实。
- saveOwner=null仅允许CanSaveDraft=false的只读/无保存Host；Attach若saveOwner=null且CanSaveDraft=true拒绝，不显示能保存的空按钮。有Owner但没有获准写入时仍可按Owner批准的查询投影恢复原意图；查询被拒保留Unknown，交原授权Owner对账。应用选择哪种真实持久化实现是产品接入门，Presenter的调用和异常闭包已在这里冻结，不能把接线留到现场决定。

**具体订阅与有限投影算法**
1. Attach先记录context/generation/viewer/权限/文化，订阅panel的PreviewRequested、CancelRequested、PreviewRecoveryRequested、SaveDraftRequested、SaveStatusRequested、SaveStatusWaitCancelled及Owner.ReceiptChanged；成功挂接后SetLanguage(culture)和Bind(context,report,viewer,slot.Service,permissions,generation,Owner.GetRetained(slotId))。任何步骤抛错立即撤销已订阅委托/停止本方计时器，CloseView清本方引用；根仍持槽，Host finally调用Unbind启动有限Close，原Owner没有被Dispose。原保存登记不依赖Attach成功。
2. PreviewRequested的同步处理器先核当前generation、CanPreview与同service.Validate，再slot.Start完整intent.Request；Root在返回前强持原operation/Completion。接纳即SetExecution原snapshot；拒绝以ApplyPreviewResult投影Failed/原Issue、Report=null和该RequestId，不自动再发。处理器异常不假定未接纳：核槽原RequestId/Task并继续观察，不能new service补试。
3. Presenter仅用一个DispatcherTimer（100ms诊断刷新上限，非设备节拍）扫描slot.Operation.GetSnapshot与OriginalCompletion状态，所有读为非阻塞；结果/错误变化才整批更新，最多一份待呈现投影。Timer只负责UI观察，不驱动设备、不推进Close；5秒单调观察预算由同clock.GetTimestamp/GetElapsedTime判定。预算到期请求原operation取消一次，停止重复结果观察，显示“等待已到期，尚未确认结束”；槽继续持有原Task，后续明确ObserveRetainedPreview/重新打开才观察原结果，不能在旧代次自动补成功。ObserveRetainedPreview只在原pendingRequestId/当前generation/来源/参数仍一致时开启一次新的有限5秒观察；不Start、不重设执行期限、不替换Task。来源已换时按钮禁用并由Host打开原只读历史记录，不能把原結果覆盖新源。host正常仍可查看原snapshot的真实释放事实；显示代次失效不改原操作state。
4. 原Completion已结束且同generation/RequestId/完整参数/源匹配时，先核Result.State/报告，再ApplyPreviewResult；CompletedWithUnavailableMetrics保留缺项，Failed/Cancelled/TimedOut不显示成功。模块Presenter不执行业务下游消费。ApplyPreviewResult/图表/Viewer呈现异常只写宿主WorkIssue并禁用保存，原计算结果不改；若原任务未释放仍由槽持有，无无限Dispatcher Invoke等待。可算结果/保存知识/关闭投影三者分区，不用一个Busy bool覆盖。
5. CancelRequested只对当前pendingRequestId调用slot.RequestCancel，不清Operation。正常预览结束且原operation已ResourcesReleased、OriginalCompletion已完成时，同一个仍开放service可接纳下一用户显式预览；槽替换原已完成操作的引用而保留最多一份最近终态，不能每次累积Task。整个service Stop仅在Unbind/Host退出/明确终止时调用，一次Stop后不可复用该槽Start。
6. SaveDraftRequested先核保存资格，再Owner.Register；立即ApplySaveResult注册回执，接纳才BeginWrite。BeginWrite异常仅触发§8.3的一次有界原意图查询，保留登记和Unknown；合法同步确认不降级。SaveStatusRequested调用Owner.Get(intentId).BeginQuery原query；SaveStatusWaitCancelled调用该原Operation.EndQueryObservation，不调用取消写入。全部事件处理器捕获自身异常，保留一份结构化诊断；不async void、不持无限后台投递。
7. ReceiptChanged可能在任意线程；Host保存知识已在Owner中先更新。Presenter按同IntentId保留一个最高Sequence的待呈现值并通过panel.Dispatcher.BeginInvoke单次投递，回调执行前核attached/generation与原意图（旧generation合法回执仍更新历史区，规则沿§8.3）。投递失败/Dispatcher已关闭只停止UI投影，不能把Owner知识降Unknown。队列积压仅合并相同Intent的更高事实，同序冲突交panel原校验，不以覆盖隐藏；不把UI订阅者异常传播为持久化失败。
8. Rebind只替换当前context/generation，清当前预览观察并请求原在途预览取消；不Start，根仍持旧操作，未结束前新的预览Busy/Blocked。panel.Bind保存原未决意图，Owner.GetRetained提供同原记录；原g1结果迟到不进入g2，原g1保存事实仍进原历史区。RefreshPermissions与SetLanguage只刷新本方控件，保留原Task/草稿/Intent/选中；SetLanguage不写全局CurrentCulture或DevExpress全局Localizer。
9. Unbind必须在panel.Dispatcher线程且幂等：先停新意图/Timer、取GetPendingSaveIntent核Owner登记、退订全部panel/Owner委托和待呈现回调，CloseView移除本方viewer显示引用但不Clear/Dispose宿主viewer；再调用slot.CloseAsync(5秒/clock UTC+5秒,CancellationToken.None)，保存该同一CleanupObservation到detach结果。不能把已取消窗口token传收尾，不能await Dispatcher里同步阻塞Task.Result。返回后Host继续持root/SaveOwner/原Task/所有借读；旧UI回调不得重开。重复Unbind返回同一detach结果、不叠Stop观察。
10. Unbind开始时UI引用可先断开，资源事实仍未确认；Host在进程Owner边界有限await detach.CleanupObservation并查看根snapshot，保存Unknown/非Drained则继续原SaveOwner对账。无人接管不能让root/Owner正常退出；确认移交按§16.9同对象、先确认再串行授予推进权。模块不因为CloseView完成宣称IO结束，也不在UI等无限native。

**控件实现的确定接线**
- ImageQualityPanel根为Grid的44 DIP命令行/中部DockLayoutManager/28 DIP状态行；命令使用WPF Button绑定本控件ICommand，Presenter只处理公开事件；主图DocumentPanel.Content为独立viewer.View，指标LayoutPanel.Content为GridControl。具体GridColumn.FieldName为MetricName/DisplayValue/UnitText/ValidPixelsText/StateText/ReasonText，ItemsSource为本控件内部不可变行投影；TableView、SelectedItem联动按行原MethodKey/RegionKey/SourceRef，不能用排序后行号。
- 直方图XAML在ChartControl内声明XYDiagram2D作为Diagram，其继承的Diagram.Series收集BarSideBySideSeries2D，DataSource为本方有界显示bin投影，ArgumentDataMember=BinLabel、ValueDataMember=Count；UI合箱只求原计数和，原报告不变。没有该指标就显示无报告/原因，不填假0柱。
- PropertyGrid.SelectedObject是本方可编辑投影（公开参数字段的setter），不是带init的冻结QualityParameters直接可写实例。每次提交编辑显式switch原QualityRoute构造对应唯一参数record并调用同Validate；未知路线不能编辑。投影错误保留原合法草稿、显示字段原因；支持字段/枚举全来自§16.2，不动态反射生成新的参数。显示别名/单位/校验文字走当前culture资源；不会写原报告Methods。
- 只读诊断Host的PropertyGrid与保存命令为只读，工程Host当前权限允许才启用；撤权先禁执行命令，不清草稿或提交事实。已有结果仍可查看；保存查询权限由Owner判定。布局与主题沿§8.1且影像比例不变；回收文档面板不得调用原viewport/native Dispose。

SetLanguage的实例实施固定为：替换本panel.Resources中同键资源值，重建行显示字符串/图例/SuperTip和ICustomTypeDescriptor草稿描述器（保留同一原typed Draft与选中字段），FrameworkElement.Language用当前IETF语言标签；数字用显式culture格式，不改序列化。TableView.ShowEmptyText=false，由本方覆盖TextBlock显示本地化空报告/原因；IsColumnMenuEnabled=false，排序/分组保留列头操作及本方已本地化查看命令。ShowSearchPanelMode.Never/ShowFilterPanelMode.Never关闭本模块不使用的vendor文字面板；PropertyGrid.ShowSearchBox=false、PropertyDefinition.ShowMenuButton=false，改用本方字段查找/恢复值命令。所有实际业务编辑/分组/排序仍可用，不隐藏关键检测/取消/保存命令。不得设置GridControlLocalizer.Active或其它DevExpress全局Localizer来切单实例语言；默认vendor文字通过这些显式局部投影/模板替代，两个STA可同时保持不同culture。该组合使用25.2官方XML已核成员，不留“编码时查怎么本地化”的内部欠账。

新增Host资源组自然三语：ConstructionFailed“模块构造失败/模組建立失敗/Module creation failed”、ConsumerFailed“结果处理失败/結果處理失敗/Result processing failed”、ObservationExpired“等待已到期，尚未确认结束/等待已到期，尚未確認結束/Wait expired; completion unconfirmed”、CapacityExceeded“恢复槽已满，请先处理未结束任务/復原槽已滿，請先處理未結束工作/Recovery slots full; resolve unfinished work”。它们是Host状态，不新增生产事实或夸大文案。


### 8.5 双STA宿主从零Attach→Unbind（2026-10-11）

两个测试Host均只引用发布Core/Wpf与本机DevExpress，不引用产品Shell、真实数据库、设备或其它测试程序集。Wpf.Tests通过编译链接§16.11的QualityEmptyHostExamples.cs源文件复用已完整列出的Fixture方法（不是引用Core.Tests DLL）；其唯一来源仍在原Core.Tests，不建立第三builder。这里只使用Fixture构造值，RunOcr/RunGroup例程不自动启动。

**Host A / Host B的完整Profile与接线**

| 项 | Host A：只读诊断STA | Host B：工程草稿STA |
|---|---|---|
| Core输入 | §16.11 Fixture(clock,false)：ocr-memory/r1、4×1 UInt8、raw-gray与完整sources | §16.11 Fixture(clock,true)：group-memory/r1、三step源、三Raw及group-support |
| 槽/根 | 进程Owner创建同clock的QualityHostLifetimeRoot(MaxSlots=2,MaxRetainedManagedBytes=128MiB)，A先Reserve非空slotA/64MiB | 在同进程根另Reserve slotB/64MiB；单独进程B也可root1/64MiB，不依赖A配置 |
| 构造 | slot.ConstructAsync中两显式lambda分别调用MemoryInputFactory与ManagedVisualFactory，所有profile/sources/clock/limits均来自本行已列fixture，先保留原Task再后台构造 | 同调用、自己的fixture与端口；A取消/Stop不触及B；构造异常/等待超时仍由原槽恢复 |
| 控件/Viewer | 当前STA new ImageQualityPanel(clock)及下方MemoryBoxViewer(f.Sources)，未挂其它父级；非nullservice=slot.Service | 当前另一个STA分别创建自己的panel/viewer，不跨线程借用FrameworkElement |
| Attach值 | context=new QualityViewContext(f.Request, f.Sources.Select(x=>x.Descriptor).ToImmutableArray(), "diagnostic")；report=null；permissions=(true,false)；generation=new非空Guid；culture=zh-CN | UsageKey="engineering"，权限=(true,true)，独立generation；culture=en-US，再显式SetLanguage(zh-TW)及zh-CN检查长度 |
| 保存Owner | 下方MemoryDraftOwner(2,clock)由同进程Owner创建并强持；A无写入权限但可查询原合法保留投影 | 同Owner按slotB登记，当前fixture授权可写；只演示内存草稿保存，非持久/产品激活 |
| 生命周期 | 先Presenter构造→Attach→Window.Content=panel→Show→操作预览/选择→Closed事件Unbind→移除Content | 同流程，另外编辑→预览→显式保存→原Intent查询→撤权/Unbind→Owner保留原记录 |
| 线程/退出 | 每STA线程自己的Dispatcher；进程Owner在Start前登记原Thread/退出TCS/slot，窗口Closed不等于线程已退出；线程实际finally才完成退出TCS | 不用第一个STA的Dispatcher/全局culture；同一个1920×1080验证视口串行显示两个Host，不改变显示设置、不另测分辨率矩阵 |

下方是完整**测试Host**保存Owner例子，位于未来Wpf.Tests的QualityPresenterHostTests，不发布到Wpf包、不作为产品存储默认值。它只保存有界不可变Draft值到内存：ConfirmCommitted是该内存Owner真实登记成功，绝不能称磁盘/数据库持久化完成。写入/查询同步结束，所以原Task完成即Drained，不构造假的native等待。真实Host适配同公开接口并持自己的原IO任务/fence/恢复登记。

~~~csharp
internal sealed class MemoryDraftOwner : IQualityDraftSaveOwner
{
    private readonly object _gate = new();
    private readonly int _maxBindings;
    private readonly TimeProvider _clock;
    private readonly Dictionary<Guid, Entry> _byBinding = new();
    private readonly Dictionary<Guid, (QualityViewContext Context,
        IImageQualityService Validator, Guid Generation, bool CanWrite, string Target)> _contexts = new();
    private bool _writable = true;
    public event Action<QualityDraftSaveResult>? ReceiptChanged;

    public MemoryDraftOwner(int maxBindings, TimeProvider clock)
    {
        if (maxBindings <= 0) throw new ArgumentOutOfRangeException(nameof(maxBindings));
        _maxBindings = maxBindings;
        _clock = clock ?? throw new ArgumentNullException(nameof(clock));
    }
    public void SetWritable(bool writable) { lock (_gate) _writable = writable; }
    public void BindFixture(Guid binding, QualityViewContext context,
        IImageQualityService validator, Guid generation, bool fixtureCanWrite, string fixtureTarget)
    {
        lock (_gate)
        {
            if (binding == Guid.Empty || generation == Guid.Empty ||
                !validator.Validate(context.Request).IsValid ||
                context.Sources.IsDefaultOrEmpty || context.Sources.Length > 3 ||
                context.Request.Methods.Length > 4 || context.Request.Regions.Length != 1 ||
                string.IsNullOrEmpty(fixtureTarget) || fixtureTarget.Length > 128)
                throw new ArgumentException("Invalid fixture context.");
            if (!_contexts.ContainsKey(binding) && _contexts.Count >= _maxBindings)
                throw new InvalidOperationException("Fixture capacity exceeded.");
            _contexts[binding] = (context, validator, generation, fixtureCanWrite, fixtureTarget);
        }
    }
    public void UnbindFixture(Guid binding)
    {
        lock (_gate) _contexts.Remove(binding); // 不清原保存Entry/Task
    }
    private static bool SameIntent(QualityDraftSaveIntent a, QualityDraftSaveIntent b)
        => a.IntentId == b.IntentId && a.ViewGeneration == b.ViewGeneration &&
           a.Sources.SequenceEqual(b.Sources) && SameDraft(a.Draft, b.Draft);
    private static bool SameDraft(QualityMethodPlan a, QualityMethodPlan b)
    {
        if (a.MethodKey != b.MethodKey || a.Revision != b.Revision ||
            a.RegionKey != b.RegionKey || a.RoleKey != b.RoleKey ||
            a.Route != b.Route || a.Required != b.Required || a.Policy != b.Policy)
            return false;
        return (a.Parameters, b.Parameters) switch
        {
            (QualityRawParameters x, QualityRawParameters y) =>
                x.Methods.Required.SequenceEqual(y.Methods.Required) &&
                x.Methods.Optional.SequenceEqual(y.Methods.Optional),
            (QualityColorParameters x, QualityColorParameters y) =>
                x.OrderedRgbRoleKeys.SequenceEqual(y.OrderedRgbRoleKeys) &&
                x.ReferenceFractions.SequenceEqual(y.ReferenceFractions) &&
                x.ReferenceRevision == y.ReferenceRevision &&
                x.MinimumTotalSignal == y.MinimumTotalSignal,
            (QualityGroupParameters x, QualityGroupParameters y) =>
                x.OrderedRoleKeys.SequenceEqual(y.OrderedRoleKeys) &&
                x.OrderedStepIndices.SequenceEqual(y.OrderedStepIndices),
            // 其余冻结record仅含标量/枚举/string，用已生成的结构Equals。
            (QualitySobelParameters, QualitySobelParameters) or
            (QualityGaussianParameters, QualityGaussianParameters) or
            (QualityNoiseParameters, QualityNoiseParameters) or
            (QualityUniformityParameters, QualityUniformityParameters) or
            (QualityDeviationParameters, QualityDeviationParameters) or
            (QualityDirectionParameters, QualityDirectionParameters) =>
                a.Parameters.Equals(b.Parameters),
            _ => false
        };
    }
    private static long PayloadBytes(QualityDraftSaveIntent intent)
    {
        long Text(string? value)
        {
            if (value is null || value.Length > 128)
                throw new ArgumentException("Invalid fixture text.");
            return checked(2L * value.Length);
        }
        var d = intent.Draft;
        long n = checked(4096 + 512 + Text(d.MethodKey) + Text(d.Revision) +
            Text(d.RegionKey) + Text(d.RoleKey));
        foreach (var source in intent.Sources)
            n = checked(n + 1024 + Text(source.SourceId) + Text(source.Revision));
        switch (d.Parameters)
        {
            case QualityRawParameters raw:
                foreach (var m in raw.Methods.Required.Concat(raw.Methods.Optional))
                    n = checked(n + 1024 + Text(m.MethodId) + Text(m.Revision));
                break;
            case QualityGroupParameters group:
                foreach (var role in group.OrderedRoleKeys)
                    n = checked(n + 128 + Text(role));
                n = checked(n + 4L * group.OrderedStepIndices.Length);
                break;
            case QualityColorParameters color:
                foreach (var role in color.OrderedRgbRoleKeys)
                    n = checked(n + 128 + Text(role));
                n = checked(n + 8L * color.ReferenceFractions.Length + Text(color.ReferenceRevision));
                break;
            case QualityNoiseParameters noise:
                n = checked(n + Text(noise.AssumptionRevision));
                break;
        }
        return n;
    }
    public QualityDraftSaveRegistration Register(
        Guid binding, QualityDraftSaveIntent intent)
    {
        lock (_gate)
        {
            if (binding == Guid.Empty || intent.IntentId == Guid.Empty ||
                intent.ViewGeneration == Guid.Empty || intent.Sources.IsDefaultOrEmpty ||
                intent.Sources.Length > 3)
                throw new ArgumentException("Invalid fixture intent.");
            var duplicate = _byBinding.Values.FirstOrDefault(
                x => x.Intent.IntentId == intent.IntentId);
            if (duplicate is not null)
            {
                if (!_byBinding.TryGetValue(binding, out var registered) ||
                    !ReferenceEquals(registered, duplicate) ||
                    !SameIntent(duplicate.Intent, intent))
                    throw new InvalidOperationException("Intent content conflict.");
                return new QualityDraftSaveRegistration(
                    duplicate, duplicate.GetSnapshot());
            }
            if (!_contexts.TryGetValue(binding, out var current))
                return Reject(intent, "ImageQuality.Save.ContextUnavailable");
            var targetRecord = _byBinding.Values.FirstOrDefault(x => x.Target == current.Target);
            if (targetRecord is not null)
            {
                var previousTarget = targetRecord.GetSnapshot();
                if (previousTarget.Knowledge == QualitySaveKnowledge.Unknown ||
                    previousTarget.Activity != QualitySaveActivity.Drained ||
                    targetRecord.OriginalWrite is { IsCompleted: false } ||
                    targetRecord.OriginalQuery is { IsCompleted: false })
                    return Reject(intent, "ImageQuality.Save.CapacityExceeded");
            }
            var expectedSources = current.Context.Sources.Select(x => x.Source).ToArray();
            if (intent.ViewGeneration != current.Generation ||
                !intent.Sources.SequenceEqual(expectedSources) ||
                !current.Context.Request.Methods.Any(
                    x => x.MethodKey == intent.Draft.MethodKey))
                return Reject(intent, "ImageQuality.Save.InvalidReceipt");
            var candidate = current.Context.Request with
            {
                Methods = current.Context.Request.Methods.Select(x =>
                    x.MethodKey == intent.Draft.MethodKey ? intent.Draft : x).ToImmutableArray()
            };
            if (!current.Validator.Validate(candidate).IsValid)
                return Reject(intent, "ImageQuality.Save.InvalidReceipt");
            if (PayloadBytes(intent) > 64 * 1024)
                return Reject(intent, "ImageQuality.Save.CapacityExceeded");
            if (_byBinding.TryGetValue(binding, out var old))
            {
                var previous = old.GetSnapshot();
                if (previous.Knowledge == QualitySaveKnowledge.Unknown ||
                    previous.Activity != QualitySaveActivity.Drained ||
                    old.OriginalWrite is { IsCompleted: false } ||
                    old.OriginalQuery is { IsCompleted: false })
                    return Reject(intent, "ImageQuality.Save.CapacityExceeded");
            }
            else if (_byBinding.Count >= _maxBindings && targetRecord is null)
                return Reject(intent, "ImageQuality.Save.CapacityExceeded");
            if (!_writable || !current.CanWrite)
                return Reject(intent, "ImageQuality.Save.PermissionDenied");
            // 同一测试目标只保留当前/最近一份；未解决已在上面拒绝。
            if (targetRecord is not null)
            {
                var oldBinding = _byBinding.Single(
                    x => ReferenceEquals(x.Value, targetRecord)).Key;
                _byBinding.Remove(oldBinding);
            }
            var entry = new Entry(this, binding, current.Target, intent);
            _byBinding[binding] = entry; // IO前的唯一Owner登记
            return new QualityDraftSaveRegistration(entry, entry.GetSnapshot());
        }
    }
    private static QualityDraftSaveRegistration Reject(
        QualityDraftSaveIntent intent, string key) => new(
            null, new QualityDraftSaveResult(intent, null, 1,
                QualitySaveKnowledge.ConfirmedNotCommitted, QualitySaveActivity.Drained,
                new QualityIssue("HostSaveRejected", "draft", key)));
    public IQualityDraftSaveOperation Get(Guid intentId)
    {
        lock (_gate) return _byBinding.Values.Single(x => x.Intent.IntentId == intentId);
    }
    public QualityDraftSaveResult? GetRetained(Guid binding)
    {
        lock (_gate)
        {
            if (_contexts.TryGetValue(binding, out var context))
                return _byBinding.Values.FirstOrDefault(
                    x => x.Target == context.Target)?.GetSnapshot();
            return _byBinding.TryGetValue(binding, out var e) ? e.GetSnapshot() : null;
        }
    }
    private void Notify(QualityDraftSaveResult receipt)
    {
        var handlers = ReceiptChanged;
        if (handlers is null) return;
        foreach (Action<QualityDraftSaveResult> handler in handlers.GetInvocationList())
            try { handler(receipt); } catch (Exception) { /* 只隔离UI投影异常 */ }
    }
    private sealed class Entry : IQualityDraftSaveOperation
    {
        private readonly MemoryDraftOwner _owner;
        private readonly Guid _binding;
        private QualityDraftSaveResult _receipt;
        public QualityDraftSaveIntent Intent { get; }
        public string Target { get; }
        private Task<QualityDraftSaveResult>? _write;
        private Task<QualityDraftSaveResult>? _query;
        public Task<QualityDraftSaveResult>? OriginalWrite
        {
            get { lock (_owner._gate) return _write; }
            private set { lock (_owner._gate) _write = value; }
        }
        public Task<QualityDraftSaveResult>? OriginalQuery
        {
            get { lock (_owner._gate) return _query; }
            private set { lock (_owner._gate) _query = value; }
        }
        public Entry(MemoryDraftOwner owner, Guid binding, string target, QualityDraftSaveIntent intent)
        {
            _owner = owner;
            _binding = binding;
            Target = target;
            Intent = intent;
            _receipt = new QualityDraftSaveResult(intent, null, 1,
                QualitySaveKnowledge.Unknown, QualitySaveActivity.Pending, null);
        }
        public QualityDraftSaveResult GetSnapshot() { lock (_owner._gate) return _receipt; }
        public void BeginWrite()
        {
            QualityDraftSaveResult receipt;
            lock (_owner._gate)
            {
                if (OriginalWrite is not null) return; // 不重发
                var tcs = new TaskCompletionSource<QualityDraftSaveResult>(
                    TaskCreationOptions.RunContinuationsAsynchronously);
                OriginalWrite = tcs.Task; // 先登记原Task再写本内存登记
                var allowed = _owner._writable &&
                    _owner._contexts.TryGetValue(_binding, out var current) && current.CanWrite;
                receipt = allowed
                    ? new QualityDraftSaveResult(Intent, null, 2,
                        QualitySaveKnowledge.ConfirmedCommitted, QualitySaveActivity.Drained, null)
                    : new QualityDraftSaveResult(Intent, null, 2,
                        QualitySaveKnowledge.ConfirmedNotCommitted, QualitySaveActivity.Drained,
                        new QualityIssue("HostSaveRejected", "draft",
                            "ImageQuality.Save.PermissionDenied"));
                _receipt = receipt;
                tcs.SetResult(receipt); // 同步内存操作实际结束，无native drain
            }
            _owner.Notify(receipt);
        }
        public void BeginQuery(QualitySaveStatusQuery query)
        {
            QualityDraftSaveResult receipt;
            lock (_owner._gate)
            {
                if (query.QueryId == Guid.Empty || !SameIntent(query.Intent, Intent) ||
                    query.MaxWait <= TimeSpan.Zero || query.MaxWait > TimeSpan.FromSeconds(30) ||
                    query.DeadlineUtc <= _owner._clock.GetUtcNow() ||
                    query.DeadlineUtc > _owner._clock.GetUtcNow().AddSeconds(30))
                    throw new ArgumentException("Query identity/budget mismatch.");
                if (OriginalQuery is { IsCompleted: false })
                    throw new InvalidOperationException("Query already active.");
                var tcs = new TaskCompletionSource<QualityDraftSaveResult>(
                    TaskCreationOptions.RunContinuationsAsynchronously);
                OriginalQuery = tcs.Task;
                // 只关联观察，不制造知识变化或事实Sequence。
                receipt = _receipt with { QueryId = query.QueryId };
                tcs.SetResult(receipt);
            }
            _owner.Notify(receipt);
        }
        public void EndQueryObservation(Guid queryId)
        {
            // 本例查询同步完成，没有仍在途IO或任务可取消；不改保存知识。
        }
    }
}
~~~

示例额外使用System.Collections.Generic、Linq；Attach前Host按slotId调用BindFixture(slotId,context,slot.Service,generation,fixtureCanWrite,fixtureTarget)，A的fixtureCanWrite=false/fixtureTarget=memory-ocr、B为true/memory-group，换窗口仍映射同原测试目标；SlotId从不当存储目标。GetRetained和未决准入按该目标跨绑定恢复，不能新槽绕过；生产目标映射仍由原Host Owner持有。这是内存Owner的明确测试授权，不由按钮能力倒推。Rebind时更新该原绑定，Unbind后调用UnbindFixture清本方校验借用，不清原保存Entry/Task。Register按完整Sources/代次及替换Draft后的同一service.Validate检查；幂等同Intent必须完整参数/数组结构一致，冲突保留原登记。BeginQuery用同SameIntent核原来源/草稿而非只核Id。允许最多3源/4方法/1ROI、字符串≤128字符且原强类型参数集合有限，保存值每binding预留64KiB（两binding共128KiB），超限拒绝，不存像素/报告/validator副本；validator仅在活动Fixture绑定借用。替换完成Entry前必须原Write/Query Task都已结束、知识确认且Drained。PermissionDenied三语“没有保存权限/沒有儲存權限/Save permission required”，ContextUnavailable三语“保存来源未绑定/儲存來源未連結/Save context unavailable”，不从异常文字生成资源。此内存例的BeginQuery同步完成，真实异步Owner仍须按§8.4保留原查询Task，不用此即时行为伪证IO已退出。

MemoryBoxViewer是Wpf.Tests里的**显示适配器**，不是模块视觉算法或生产viewport替代。构造后View为独立Viewbox，内层Canvas按原像素尺寸排列WPF Image/Rectangle；像素显示从对应SourceRef的fixture UInt8数组逐值复制byte[]，BitmapSource.Create(width,height,96,96,PixelFormats.Gray8,null,bytes,width)后Freeze，NearestNeighbor只用于显示；Select核SourceRef/Bounds/坐标后替换源并设置框Left=Col0、Top=Row0、Width=Col1−Col0、Height=Row1−Row0。Clear只清本方框，不释放宿主source；不支持的layerKey回退quality.roi定位，不伪造响应热图。全部操作在所属STA；此适配器完整实现§8.1三个成员，没有SDK或隐藏窗口。两个Host使用自己的viewer，图像仅4×1合成验证输入，真实影像/视口资格仍另验。

~~~csharp
internal sealed class MemoryBoxViewer : IQualityViewerPort
{
    private readonly Dictionary<QualitySourceRef, QualityMemorySource> _sources;
    private readonly Canvas _canvas = new();
    private readonly Image _image = new();
    private readonly Rectangle _box = new()
    {
        Stroke = Brushes.Orange, StrokeThickness = 0.1,
        IsHitTestVisible = false
    };
    public FrameworkElement View { get; }

    public MemoryBoxViewer(ImmutableArray<QualityMemorySource> sources)
    {
        if (sources.IsDefaultOrEmpty) throw new ArgumentException("No fixture source.");
        _sources = sources.ToDictionary(x => x.Descriptor.Source);
        _canvas.Children.Add(_image);
        _canvas.Children.Add(_box);
        View = new Viewbox { Child = _canvas, Stretch = Stretch.Uniform };
        RenderOptions.SetBitmapScalingMode(_image, BitmapScalingMode.NearestNeighbor);
        var first = sources[0].Descriptor;
        Select(first, new QualityBox(0, 0, first.HeightPx, first.WidthPx), "quality.roi");
    }
    public void Select(QualitySourceDescriptor source, QualityBox bounds, string layerKey)
    {
        View.Dispatcher.VerifyAccess();
        if (!_sources.TryGetValue(source.Source, out var memory) ||
            memory.Descriptor != source || source.PixelType != QualityPixelType.UInt8 ||
            bounds.Row0 < 0 || bounds.Col0 < 0 ||
            bounds.Row1 <= bounds.Row0 || bounds.Col1 <= bounds.Col0 ||
            bounds.Row1 > source.HeightPx || bounds.Col1 > source.WidthPx)
            throw new ArgumentException("Fixture source/domain mismatch.");
        var pixels = new byte[memory.Samples.Length];
        for (var i = 0; i < pixels.Length; i++) pixels[i] = checked((byte)memory.Samples[i]);
        var bitmap = BitmapSource.Create(source.WidthPx, source.HeightPx,
            96, 96, PixelFormats.Gray8, null, pixels, source.WidthPx);
        bitmap.Freeze();
        _canvas.Width = source.WidthPx;
        _canvas.Height = source.HeightPx;
        _image.Width = source.WidthPx;
        _image.Height = source.HeightPx;
        _image.Source = bitmap; // 只有显示转换，无算法/租约
        Canvas.SetLeft(_box, bounds.Col0);
        Canvas.SetTop(_box, bounds.Row0);
        _box.Width = bounds.Col1 - bounds.Col0;
        _box.Height = bounds.Row1 - bounds.Row0;
        _box.Visibility = Visibility.Visible; // 所有layer仅定位原框，未冒造热图
    }
    public void Clear()
    {
        View.Dispatcher.VerifyAccess();
        _box.Visibility = Visibility.Collapsed;
    }
}
~~~

此源码额外使用System.Windows、Controls、Media、Media.Imaging、Shapes，都是WPF公开显示API；未运行。Borrowed viewer由测试Host最终清其Image.Source/可视父级后回收，panel/Presenter的Unbind不替Host销毁它。

**完整STA执行顺序（实现规格，不把未实现代码称运行样例）**
1. 主进程创建clock、root、MemoryDraftOwner(2,clock)，以及长度2的attempt表；表由进程Owner持有，字段固定SlotId/原Thread/ExitTask/原ConstructTask/Detach，拒绝超容量。先Reserve A/B，构造委托明确为上表公开factory。保存OriginalConstruction后有限5秒WaitAsync；构造等待异常先slot.CloseAsync独立5秒，无UI部分仍由根恢复，不启动第二构造。
2. 每attempt先创建RunContinuationsAsynchronously退出TCS和原Thread，再把二者登记到attempt表，最后SetApartmentState(STA)→Start。线程入口try创建panel/viewer/Presenter和Window；Attach所有参数来自上表，不使用Application.Current的隐藏全局service。Show前订阅Window.Closed；其处理器try调用Presenter.Unbind，记录同一个Detach与CleanupObservation，finally Window.Content=null并Dispatcher.BeginInvokeShutdown。若Show/Attach抛错，在线程finally也执行同一Unbind或未建Presenter时slot.CloseAsync；保存问题不覆盖原工作问题。
3. Dispatcher.Run只用于该STA消息循环。正常Closed仅请求退出，原Thread入口finally完成退出TCS才表示线程代码结束；进程Owner仍核Thread.Join的有限结果（最多5秒，不在UI线程Join）。Close回执/Save知识/线程退出三个证据独立。附带“窗口已关”字符串不等价于service已释放或保存已提交。
4. 验证Owner有限等待ExitTask/Detach.CleanupObservation，各预算5秒、总90秒；超时不丢原Thread/Task/Slot。恢复/查询从root.Get(slotId)和SaveOwner.Get(intentId)进入，原根没有因为UI线程结束被GC；未确认时不TryForget、不销毁真实源Owner。测试屏障必须在case finally解除并确认线程/任务退出，外层180秒强制终止只记验证失败，不冒充模块资源通过。
5. 每个Host正常“Attach→选择区域→显式预览→查看量/缺项→三语刷新→Unbind”都能脱离产品Shell。Host B另验“合法草稿→预览→保存→Query原Intent→撤权→重开retainedSave”，Owner实例/Intent不变，保存区和预览区独立。新panel只能在原UI已Unbind之后建，未解决service与保存仍在原root/Owner，不能新panel绕过未解决登记。
6. 固定1920×1080物理验证框由Wpf.Tests测量当前真实DPI/任务栏/边框/标题及状态栏得客户区；窗口外框和截图裁剪都在该单一框内，主图比例按§8.1。两个STA顺序占用同一验证框。语言/键盘/AutomationId/UIA/视觉品质都用真实DevExpress控件检查；不拿上表或合成Bitmap当已通过真实布局/工业图像资格。

两STA都可从未来公开包装配；具体真实viewport Adapter和真实保存/主体/fence映射属于各Host原产品集成门。这里已决定module Presenter/API/内存Owner/线程/正常异常流程与所有构造参数，不能再把这些内部接线列为待客户选择。

## 9. 可判定场景

| 场景 | 输入和期望 |
|---|---|
| 正常 8-bit 计数 | 原值 `[0, 100, 254, 255]`，4 个有效像素；调用方显式指定饱和边界 `255`。报告高端计数 `1`、比例 `0.25`、`N=4`，只说明观测量，不产生合格判断。 |
| 高位深范围 | `uint2`、有效位深 12、明确黑白参考 `[0,4095]`；精确原值计数与统计不得用按图 min-max 拉伸后的 256 bins 代替。白参考缺失时依赖参考的饱和指标为 `NotObservable`。 |
| 有效域缺口 | 请求面积 8、有效 mask 仅 4 个像素；曝光比例分母为有效 `N=4`，覆盖比例为 `4/8`，两者分别输出。无有效像素返回 `NotObservable/NoValidPixels`，绝不填 0。 |
| 邻域边界 | Sobel/LoG 的 mask 内有洞、图像边界、tile 接缝；仅完整输入支撑的中心参与聚合，跨 tile 读取真实 halo。全图与分块的支持集和值须在方法容差内一致。 |
| 假高清 | 高噪声导致梯度增大，或均匀区梯度接近零；报告不把高响应叫清晰资格，不把低纹理叫失焦；不足时返回不可观测原因。 |
| ROI/元数据错误 | 越界 ROI、错误 plane、frame ID 不同的 mask、stride/payload 不一致、非有限 real；在 native 调用前明确拒绝，不裁剪、补零或吞异常。 |
| 方法不支持 | 不支持的 PixelType/后端/尺度组合；方法记 `Unsupported` 或请求拒绝，不能悄悄换算法/CPU-GPU 或重解释单位。 |
| 取消/超时 | native 运算中取消或期限到达；请求进入 Draining，native 归还后才终止并释放 lease；超时/取消不产生完成报告、不重试、不释放在用对象。 |
| observer 故障/迟到 | 回调抛异常或 UI 关闭；计算结果不变，迟到事件以 RequestId/代次过滤；取消一个实例不影响另一个。 |
| 关闭竞态 | Stop 与新提交并发；Stop 后新请求 `Disposed/Stopping`，已接收请求逐一终态并排空，重复 Stop/Dispose 幂等。 |

没有真实样本、传感器白电平/曝光来源或任务 Profile 时，只能验语义与数值闭合，不能宣称适用性阈值通过。

### 9.1 第二轮场景驱动复审矩阵

下表把“输入—来源—处理顺序—输出—恢复—验收”绑定到同一调用实例。任何未列出的自动补值、静默 fallback 或跨请求复用都视为架构缺口。

| 场景 | 输入与参数来源 | 处理顺序 | 输出、状态和错误 | 恢复动作与可判定验收 |
|---|---|---|---|---|
| 正常配置/执行 | 一个有效 Frame/Plane、一个合法 ROI、已冻结方法修订、有效位深/来源和资源预算；参数来自调用方 Profile/草稿快照 | Validate → Start接纳 → 获取只读scope → 按方法计划计算 → 检查有限值/支持域 → 释放 native → 生成报告 | 全部所需指标有值时 Completed + QualityServiceReport；每项带原参数、单位、支持摘要，性能分解只在测试测点记录 | 同一冻结输入重复运行在方法容差内一致；没有设备动作、产品 PASS 或隐藏总分 |
| 空输入/零支持 | 缺图、null来源、空Regions非法；尺寸正确但全false mask是已知零支持 | 先结构校验再数支持 | 前者Rejected；后者覆盖0、灰度项NotObservable/NoValidPixels，零native计算 | 不补满mask；空前景或覆盖0不解释为通过 |
| 部分成功 | Required/Optional 方法混合；某 Optional 不支持，或某 Required 的来源事实缺失；来源分别来自方法合同和采集快照 | 逐指标隔离执行，不因Optional不支持/不可观测丢量，但后端执行故障仍整次Failed；保留每项 requirement | QualityServiceReport保留NotObservable/Unsupported；Required缺项为CompletedWithUnavailableMetrics，Optional缺项可Completed；Required 缺项阻断依赖它的调用流程 | 调用方只可使用已完成且满足自身前置的指标；不把报告状态显示为质量通过；补齐来源后新修订重算 |
| 歧义/错误输入 | 重复 role/sequence、同一 FrameId 对应不同 PlaneRevision、ROI 越界、阈值顺序冲突、mask 来源不一致、非有限参数 | 结构/身份/单位/范围/预算全量校验后才接收 | `Rejected` + `IQ-IMG-002`/`IQ-DOM-003`/`IQ-REQ-001`，不部分执行 | 调用方修正来源或参数并重新提交；验收证明原请求没有副作用、没有“尽量计算”结果 |
| 超大输入 | 大尺寸/高位深/多 ROI/多曝光组，预算来自消费者 Profile；工作集估算包含halo、本方native临时对象和报告，内部native实际峰值另测 | 先估算checked内存/累计读取成本，再选择已批准 tile/halo 或拒绝；分块结果只在支持集闭合时合并 | 预算不足 `Rejected + IQ-BUD-006`；批准的分块路线才返回完成报告并保留每 tile 支持/缺口 | full 与 tile 在支持闭合时对照通过；超限不靠 OOM、截断或降低分辨率伪造成功 |
| 高并发/背压 | 多宿主同时提交，本模块实例并发1、无队列；无全局共享句柄 | 服务实例无队列；在途Start立即QS-Busy，新实例由宿主总预算管理 | QS-Busy或正常终态；每请求RequestId独立，Snapshot.Sequence不跨实例比较 | 验证无隐藏队列/无静态串扰、另一实例取消不影响本实例；宿主显式重提 |
| 噪声/遮挡/退化 | 高噪声、低纹理、反光、局部 mask 洞、曝光极端、方向纹理；来源为 Golden/Replay 或有来源支持图 | 先计算可用域/邻域支撑，再运行具名路线；方法前提不足即停止该指标 | 指标可为 `Computed`、`NotObservable` 或 `Unsupported`；不得把高 Sobel 响应叫清晰、黑像素叫遮挡、局部离散叫噪声 | 逐类 Golden 复现原因码和支持域；调用方决定复拍/换方法，模块不改参数、不驱设备 |
| 取消/超时/native 排空 | token 取消或 deadline 到达，可能正处于不可中断 HALCON 调用；输入 lease 仍有效 | 标记取消 → 等 native 返回 → 释放临时对象 → 结算请求 → 发唯一终态 | `Cancelled` 或 `TimedOut`，无部分 QualityReport；排空前不归还 lease、不复用 worker | 记录取消到 drain 时长；慢 native 不被线程终止；宿主只有收到终态后才释放输入 |
| 资源上限 | ManagedBytes/NativeBytes、读取或句柄租约预算不足；预算由宿主运行 Profile 提供 | 分配前估算；不满足则拒绝；运行中发现超限进入受控 drain，不扩容无界缓存 | `IQ-BUD-006` 或 `Failed`（实际破坏/泄漏）；不返回假完整结果 | 同一输入按较小批准 ROI/分块新请求重试；验收峰值内存、释放和失败后实例可继续运行 |
| 持久化/版本修订 | 宿主保存报告快照、方法参数、输入 revision、模块/后端/HALCON 版本和 hash；模块无数据库副作用 | 计算完成后由宿主序列化；读回先核 Contract/方法/后端支持矩阵，再决定仅查看或重算 | 版本不支持 `Rejected + IQ-VER-011`；旧报告仍可只读，不伪装当前资格 | 读回不改变原报告/事实；重算使用新 RequestId 和新方法修订，差异可追溯 |
| 升级/回退 | 新旧 Core/Adapter/HALCON 组合和兼容矩阵；发布包、配置、Golden、参数 hash 均可定位 | 先停新请求 → drain → 安装/选择精确组合 → 运行迁移检查和小型 Golden → 恢复接收 | 不支持组合拒绝；升级后报告标新环境；回退恢复旧组合，旧报告不重写 | 升级/回退均不跨版本复用 native handle 或缓存资格；迁移失败保持停用并由宿主处理 |
| 无 UI 首片 | 独立 .NET 10 console/test host 只注入内存 `ManagedGrayImage`、区域、方法和可选诊断端口；无 Dispatcher、窗口、产品 Shell、帧 lease 或全局初始化 | `Create` → `Validate` → `Evaluate` → 读取 `ManagedQualityResult` → `Dispose` | 返回逐指标数值/单位/样本数/原因；不产生 native、设备或产品终态 | 移除 WPF、HALCON、AsunImage、设备 SDK 和数据库引用后仍可运行；两个 evaluator 无串扰；后续异步/帧 lease 映射另行验收 |
| 后续产品/适配宿主 | 服务端口按§16已定义，正式产品帧lease桥在原Schema/Owner采纳后绑定 | §16 Validate→Start→Completion/真实释放→产品映射 | §16 QualityOperationResult；不回写附录A API | 每个 FrameAdapter/AsunImage slice 单独满足 `DEV-GOV-010 §3.1`，不得用后续 host 证明首片可构造性 |
| 可选 UI | 只读报告/原图/支持图和草稿；语言/主题/权限由宿主传入 | 同一校验→宿主新请求 | 只发意图；换帧隔离旧预览，旧保存回执仍归原意图/Host；不写质量事实 | 仅1920×1080固定验证视口；三语/键盘/UIA/真实DPI，关闭退订；无UI核心仍运行 |
| 第二消费者 | 独立 OCR/读码或 2D/3D 前置工具，自己的配置/缓存/身份/Profile，仅引用同一发布包 | 两个宿主分别创建实例或受控共享 Core，独立提交/取消/关闭 | 一方失败/取消不改变另一方结果；报告仅保留各自 RequestId/来源 | 断开第一宿主仍可运行第二宿主；包依赖扫描无产品 VM、私表、设备 SDK 或隐藏窗口 |
| 长期运行 | 连续不同 FrameId/PlaneId、周期性取消、方法修订、异常 observer、内存压力和重启演练 | 每请求独立 lease/诊断/序号；定期采集资源计数；达到维护阈值由宿主滚动 Stop/重建 | 无增长的 native/托管资源；已确认排空/释放的异常有唯一终态；未知排空仍保留非终态Owner；重启后不恢复未完成请求为成功 | 长稳测试验证句柄、队列、订阅、缓存和日志有界；重启/进程回收后未知请求不补写完成事实 |

### 9.2 DZ-XVision 可迁移的输入质量证据（后续 Product Schema/Adapter）

`DZ-XVision` 快照只作为后续映射层已观察的采集事实来源，不能把旧项目的设备 SDK、线程模型、默认值或日志文字复制为本模块契约。以下证据由采集宿主形成只读快照，再随未来 `ImageFrameLease`/派生图适配进入；本模块只消费证据，不控制相机、光源、运动或重拍。它们不属于 `ManagedCoreSlice-01` 的输入。

| 证据 | 快照事实与来源 | 进入质量模块前的校验顺序 | `Valid` / `Unknown` / `Invalid` 影响 |
|---|---|---|---|
| `ExposureEvidence` | 请求曝光后调用应用操作；相机配置另存为 INI。见 [`CamLights_Control.cs`](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/CamLights_Control.cs) 与 [`DZXVision.cs`](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/DZXVision.cs) 的 `BoardGrab`。 | 记录 `ExposureRequested`、应用返回/异常、读回值和 `SourceEvidenceRevision`；读回值须为有限正数且与当前 Frame/Plane 关联。仅有请求值、没有应用或读回证据时不得降级为实际值。 | `Valid` 可供依赖曝光的指标使用；应用失败、非有限或与帧不匹配为 `Invalid`；缺少读回/修订为 `Unknown`，相关指标 `NotObservable`。不定义默认曝光。 |
| `LightingEvidence` | 快照逐通道写入光源并返回成功/失败；配置校验要求数组存在、长度和范围合法。见 [`CamLights_Control.cs`](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/CamLights_Control.cs)、[`LampControllerUART.cs`](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/LampControllerUART.cs)、[`LampControllerUDP.cs`](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/LampControllerUDP.cs)。 | 宿主提供逻辑通道标识、请求值、应用结果、读回结果、稳定等待是否完成及来源修订；通道数量/范围由宿主 Profile 给出，不固化旧项目的四通道或 `0..255`。 | 全部必需通道应用且读回一致为 `Valid`；未提供稳定等待/读回或通道映射不完整为 `Unknown`；明确失败、越界或重复身份为 `Invalid`。依赖照明的指标不得使用请求值冒充实际值。 |
| `GrabEvidence` | `取一副图(0)` 的返回码可能被连续调用；返回成功后复制 SDK 图像。见 [`DZXVision.cs`](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/DZXVision.cs) 的 `BoardGrab`/`RunGrab`。 | 保存每次尝试的序号、返回状态、时间、FrameId 和缺帧/重复/错序信息；只接受与当前任务关联且完成性满足 Profile 的帧。连续调用次数不构成成功证明。 | 返回成功且帧身份、顺序和 payload 完整为 `Valid`；无返回码、身份无法关联或顺序信息缺失为 `Unknown`；明确失败、缺帧、重复占位或错序为 `Invalid`，阻断受影响指标。 |
| `ImageObjectEvidence` | 旧流程先释放旧图，再检查 `hImage` 非空；SDK 成功不保证最终图像对象有效。见 [`DZXVision.cs`](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/DZXVision.cs) 的 `BoardGrab`。 | 检查对象非空、尺寸/像素类型/域可读、payload 与 FrameId 一致，再创建只读 lease；任一检查失败不得把旧对象继续当新帧。 | 全部检查通过为 `Valid`；未能读取尺寸/域或来源修订缺失为 `Unknown`；空对象、损坏 payload、身份串帧为 `Invalid`。`Invalid` 不进入 native 算子。 |
| `DerivedImageEvidence` | 旋转使用 `constant` 边界填充，派生对象再次检查后才交给 ROI/拼图；原图、旋转图、拼图图分开保存。见 [`DZXVision.cs`](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/DZXVision.cs) 的 `BoardGrab`/`Setting.cs`。 | 记录父来源、变换参数/修订、填充策略、有效域和派生结果对象；任何拼接/旋转失败或有效域未定义均停止该派生路线。 | 派生对象及有效域完整为 `Valid`；变换完成但填充影响/域信息未知为 `Unknown`，只能运行不依赖该域的指标；对象为空、变换异常或来源断裂为 `Invalid`。填充区不得作为原始观测。 |
| `ThreadDrainEvidence` | 停止请求通过标志位和事件发出，线程退出后才设置停止事件；等待超时仅表示未证明排空。见 [`DZXVision.cs`](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/DZXVision.cs) 的 `StopGrab`/`RunGrab`。 | 分开记录 `StopRequestedAt`、线程退出、native 调用返回、lease 归还和最终状态；未收到排空证明不得释放在用输入或复用 worker。 | 全部阶段按序完成为 `Valid`；只收到停止请求或等待超时为 `Unknown`/`Draining`；线程异常、资源无法归还为 `Invalid`/`Failed`，不得发完成报告。 |

建议的候选字段名为 `AcquisitionEvidenceState`、`ExposureRequested/Actual/ReadbackState`、`LightingRequested/Actual/ReadbackState`、`GrabReturnState`、`ImageObjectState`、`DerivedImageState`、`FrameCompletenessState`、`ThreadDrainState` 和 `SourceEvidenceRevision`。它们是输入证据候选，不替代 C-03/C-04 的正式字段、错误码或采集 Owner；宿主必须保留请求值与实际/读回值的区别。

### 9.3 `Unknown` / `Invalid` 分层

`Unknown` 表示事实尚未被证明或无法关联，例如只有曝光请求值、没有读回值，或停止请求已发出但线程仍可能运行。`Invalid` 表示已证明事实不满足契约，例如明确 SDK 失败、空图、损坏 payload、重复/错序帧或变换失败。两者都不能按 PASS、零值、默认值或“最近一次有效值”替代。

证据状态按依赖图向指标传播：指标只有在其所需的每个证据为 `Valid` 且支持域闭合时才可为 `Computed`；任一必需证据为 `Invalid` 时指标为 `NotObservable` 并携带结构化原因，任一必需证据为 `Unknown` 时指标为 `NotObservable`/`EvidenceIncomplete`。与该证据无关的指标可以继续执行，但报告必须保留逐指标依赖和来源修订。`Invalid` 是输入/执行故障，`Unknown` 是证据不足；调用方不得把二者合并为“质量差”。

### 9.4 恢复建议与调用方责任

模块只返回结构化恢复建议，不执行设备动作。建议至少区分：`AcquireAgainAfterSourceReady`（采集或光源证据不足）、`RefreshReadbackAndResubmit`（请求值与实际值未闭合）、`DiscardFrameAndAcquireNewIdentity`（缺帧/重复/错序/空图）、`RebuildDerivedImageWithDomain`（旋转/拼接有效域缺失）、`WaitForDrainThenDispose`（取消/停止尚未排空）和 `ReviewUnsupportedProfile`（Profile/版本不支持）。每项建议带触发证据、受影响指标、是否允许新 RequestId 重试和不得执行的副作用。

采集宿主负责设备应用、读回、稳定等待、帧身份/顺序、原图与派生图修订、线程排空和资源所有权；本模块负责证据一致性校验、指标状态传播、原因码和报告构造。AOI 判定、复拍策略、运动/光源命令、MES 事务、质量放行和日志文案均由调用方或其权威模块决定。

### 9.5 快照事实验证矩阵

| 验证项 | 最小断言 | 失败时的模块结果 |
|---|---|---|
| 请求值与读回值 | 改变请求但读回缺失或不一致时，报告保留两者及修订，不把请求值当实际值 | 依赖项 `Unknown` 或 `Invalid`，指标 `NotObservable` |
| SDK 返回与最终对象 | SDK 返回成功但目标对象为空、尺寸不可读或 payload 不一致时不创建有效 lease | `Invalid`，无 native 质量计算 |
| 原图/派生图链 | 旋转/拼图结果能追溯父 FrameId、变换修订和有效域；`constant` 填充不进入原始有效域 | 派生指标 `Unknown`/`Invalid`，保留父来源 |
| 完整性 | 缺帧、重复帧、错序帧和跨任务 FrameId 均能被重放检测，不能靠连续三次调用掩盖 | 受影响指标 `NotObservable`，建议新身份采集 |
| 停止与排空 | stop 请求、线程退出、native 返回、lease 归还和终态顺序可观测；超时不提前释放 | `Draining`/`TimedOut` 或 `Failed`，不发完成报告 |
| 配置边界 | 宿主 Profile 可表达通道数量、值域、曝光单位和稳定等待；测试不得依赖旧项目固定 `3000`、四通道或 `0..255` | 配置缺失/越界为 `Rejected` 或证据 `Invalid` |

验证应使用快照中的调用顺序作为 Replay 夹具来源，并补充空返回、异常返回、迟到返回和重启场景；快照本身不证明 HALCON Golden、性能、HIL 或生产资格。

## 10. 测试矩阵和验收断言

| 层级 | 断言 |
|---|---|
| ManagedCoreSlice-01 最小 host | 只引用 `ImageQuality.Core`；内存构造 `ManagedGrayImage`/区域/方法；按 `Create` → `Validate` → `Evaluate` → `Dispose` 完成；无帧 lease、HALCON、AsunImage、WPF、设备或数据库；两个 evaluator 无状态串扰；Dispose 后拒绝新请求。 |
| Core 合同单测 | 参数边界、类型/单位、空 ROI、非法 mask、有限数、计数 checked、缺值非零占位、结果字段来源完整。 |
| 算子适配测试 | HALCON 26.05 每个支持 PixelType/方法的真实 AsunImage 公共入口；逐项对照官方语义、边界值、ROI/domain、输出类型、CPU/设备分支；确定性释放。编译只证签名，不证算法资格。 |
| Golden/Replay | 标准灰阶、曝光阶梯、可控焦距序列、方向纹理、噪声、反光、遮挡/缺测 mask、高位深、曝光组/相位组和真实生产变化；冻结来源、参数、环境和期望方法容差。 |
| 属性/差分 | 直方图计数与 N 闭合；tile/full 支撑和值对照；合法仿射灰度变化只按各方法的预期变换；输入排列/无关 ROI 不污染指标；不同物理尺度不混单位。 |
| 故障/并发 | HALCON 抛错/无效输出、取消前中后、超时、native 慢返回、资源超限、Stop/Dispose 竞态、慢/异常 observer、多实例隔离、无订阅执行、内存释放。 |
| 两消费者接入 | OCR/读码消费者与 2D/3D 前置质量消费者在各自独立最小宿主引用同一包，不改 Core；一个调用方可选择不需要的指标，缺项仅影响依赖它的调用流程。 |
| 可选 UI | 仅1920×1080固定验证视口，三语长文本、真实DPI、键盘/UIA、切帧迟到隔离、草稿恢复及关闭不提前归还lease；与无UI同一报告。 |

接收需逐个关闭语义断言和证据。Mock、合成图、截图、编译通过均不冒充 HALCON Golden、真实 WPF、客户 Profile 或现场资格。消费者不能以模块“成功计算”替代自己的 OCR/读码/重建验收。

## 11. 性能和可观测性

每个消费者提供经批准的 `QualityPerformanceProfile`：帧尺寸/有效像素、plane/曝光数、指标集合、ROI 数、mask 密度、位深、HALCON/设备、并发度、允许额外周期时间 `MaxDuration`、峰值工作集 `MaxWorkingBytes`。预算覆盖接纳、源准备、算子、结果复制和排空；§11.1测试测点分解耗时，负载测试报告 P50/P95/P99、冷/热启动、峰值托管/native 内存、CPU/GPU、队列深度和取消排空尾部。预估溢出须在分配大对象前拒绝或按已批准 tile/halo 路线执行。

后续帧/报告适配的工作集按同时存活量核算：借读保留的实际槽容量、有效域快照、准备/复制缓冲、native 临时区、报告和诊断均计入，短 payload 不代表只占 payload 大小。累计输入/读取/复制字节与峰值工作集分别记录，不把已释放的顺序临时分配相加冒充峰值，也不漏掉仍持有的槽容量。多 ROI、指标和子调用共用原请求预算；子调用只取得剩余额度，额度归还须以真实释放为依据，不能重复领取完整预算。子期限只能收窄，取原期限与子期限较早者，不因重借或换域续期。分配前采用 checked 预留并核实际用量；native 预估不冒充第三方内部工作区的硬上界。这些规则不使首片引入帧/报告租约或新的预算 DTO。

当前消费者目标硬件、实际输入分辨率、调用频率与目标Profile数值尚未采纳；因此本版本不给毫秒、吞吐或内存硬门，也不声称达到实时要求。两个消费者分别给出 Profile 后才能固定发布性能预算。每次方法/后端变更以同一 Profile 重测，不用 8-bit 小 ROI 结果外推高位深全帧。

核心诊断只使用公开结果/Snapshot字段；§11.1测试测点另记录RequestId、source/plane、方法/修订、ROI、支持数、原因、runtime、阶段耗时/预留/实际峰值与取消到drain时长，不承诺报告中不存在的阶段事件/耗时字段。宿主产品关联才附FrameId/实例代次；服务无队列，排队测点不适用。原始图像、敏感目标身份和异常堆栈不进入普通日志；宿主决定关联身份和保留期。进度是诊断投影，不作为完成或资格证据。

### 11.1 QualityBenchmarkProfile（计划字段与执行测点）

本节是测试/资格输入规格，不新增公开运行时DTO或另一统计权威。每次Profile须冻结ProfileId/Revision、模块/API/适配器/runtime精确版本、输入像素/来源/mask/hash、方法完整参数、目标机器/OS/.NET/CPU/内存及显示DPI（仅WPF）、负载、并发、冷/热、预热与测量数量、最低有效样本数、有限deadline、资源上限、目标来源和失败处理。分位统计、删失/失败样本处理唯一遵循[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)，这里不复制算法。客户目标、预热数或最低样本数未采纳时仅诊断测量，资格NotEvaluated。

| 切片/负载维度 | 固定阶段测点与计数 | 失败/阈值来源 |
|---|---|---|
| ManagedCoreSlice-01 | 各类型UInt8/UInt16/Float64；宽高、ROI数与重叠、全有效/稀疏/全false mask；五方法组合、K、Float64精确分位排序。进入Evaluate→校验/预留→扫描→分位/分箱→复制结果→scratch释放并返回。另计工厂冷创建、GC/分配、逻辑ReservedWorkingBytes及进程峰值 | 请求/实例MaxWorkingBytes为准入硬限；返回前scratch不再持有是端点。无native不虚构ResourcesReleased事件。迟延/实际内存目标由两个消费者各自Profile冻结。 |
| QualityServiceSlice-02 + Simulator | 输入个数/去重、source槽容量、ROI/方法数、tile尺寸/次数、输出量；并发1与根MaxSlots总预留；可控构造/Open/Observe/Close延迟、取消/超时/首次释放失败。Reserve→原构造Task→接纳→读取→Observe→输出验证→Close→scope归还→Completion | 资源端点为Snapshot.ResourcesReleased/Completion及根CanForget；另测Stop观察接入→返回/注册及槽归还、根保留Task/端口/逻辑bytes，活动Stop≤1。观察到期不替代真实释放，纯托管同步值没有native drain测点。Unknown/Retained不算资源性能通过；模拟只验证协调/Owner因果，资格目标由§11.1已采纳Profile。 |
| AsunImageSlice-02A | 同一真实样本比较请求的Sobel/Gaussian/LoG/Noise、位深、纹理/反光、全域/获支持tile；CPU配置和优化identity固定；冷初始化/热重复分开 | 统计准备/复制、operator、结果汇总、native真实排空与释放；本方native容量和实际进程峰值都记录。错路由/计数/非有限值/支持域失真直接失败，精度/误接受拒绝/时延目标由同一Golden/Profile，不按最快候选补阈值。 |
| WpfSlice-03 | 唯一1920×1080视口及当前真实DPI；双独立STA串行、三语、可见行/tile数、K与显示柱数、只读/草稿/比较/切源；预览/保存/关闭轴独立 | Attach→首次可见、行选中→图层定位、语言→全可见文本更新、Unbind→本方显示/订阅归还，另记录原预览Task/原SaveOwner及根真实资源终点。每Presenter≤1 Timer/待呈现投影，UI线程分配/迟到丢弃/退订记录。PageProfile目标缺失=NotEvaluated；图像比例/键盘/权限/代次按§8.1/8.4硬断言。 |
| FrameAdapter/Product | 原帧借读容量、并发消费者、真实源断连/修订/租约期限与来源复制 | 帧取得→原合同映射→服务→原租约真实归还；与Core测量分开。原Contract/Owner及客户节拍为来源，未绑定不得推断通过。 |

执行顺序：核Profile完整性→冻结输入及版本→冷进程测量→按Profile预热→固定次数测量并保留全部状态→取消/超时/释放失败专项→资源确认→按唯一统计口径汇总。测量期间不改变方法/参数/后端，不自动排除慢样本。两个候选采用相同输入序列、预算和测点；误接受/误拒绝、不可观测率及下游真值先比较，再比较尾延迟/资源。硬限超出、泄漏、迟到成功、未排空均不能用更高平均吞吐补偿。

预算边界测试使用§A.3/§16.6确定的逻辑预留值B：上限B接纳、B−1在对应分配前拒绝；这只验证账本，不证明实际RSS=B。真实native资源上界尚需测量，适配器不得把HALCON内部未报告峰值编成精确数字。每次Benchmark另记录预估与实际偏差，超过Profile实际资源限时不授该Profile资格。

## 12. 版本、兼容、发布和回退

- 独立包语义版本采用 `MAJOR.MINOR.PATCH`；准备状态包追加 `-prep`，不得作为生产依赖。公开字段/单位/枚举含义变化、终态变化或移除方法属 Major；兼容新增可选指标/诊断字段属 Minor；不改变语义的修复属 Patch。Contract 版本与程序集版本分开记录。
- 每份报告保存模块版本、方法/参数修订、AsunImage 公开适配版本、HALCON 26.05 精确版本、后端和必要来源修订。未知版本明确 `UnsupportedVersion`，不得按相邻版本推测行为。升级 HALCON、AsunImage、算子参数或 GPU 路线时重跑相关适配 Golden/资源/并发测试。
- 发布包按切片包含Core、被批准的AsunImage adapter和可选WPF包；登记目标 TFM、依赖清单、公开 API、方法支持矩阵、变更说明、校验 hash、Golden/性能证据和兼容矩阵。禁止隐式下载/动态替换依赖。
- 宿主锁定精确包版本；升级前保留原包及对应 HALCON/适配配置。回退恢复已知包/adapter 组合并重新执行小型 Golden；已生成报告保留原方法与环境标识，不重算覆盖、不修改调用方事实。回退失败停止该质量调用，由调用方决定受影响流程。

发布按切片：纯托管Core按附录A独立打包/测试/回退，不要求产品C契约或HALCON；服务端口按§16契约测试，AsunImage切片做真实26.05 Golden/资源/性能，C映射另由原Owner采纳，WPF独立验收。对应门未关保持PreparationIncomplete，不列AsunImage/DevExpress安装、存在或授权待办。

### 12.1 报告持久化和修订

模块核心不写数据库、不维护“latest”结果、不覆盖历史报告。宿主若需要持久化，必须保存不可变结果快照及以下最小关联：`RequestId`、`FrameId/PlaneId`、输入来源/派生修订、方法 ID/版本/参数 hash、Contract 版本、模块/适配器/HALCON 版本、后端、有效域摘要、每项指标状态/原因/单位、开始/完成时间和资源诊断。保存失败属于宿主提交/证据问题，不得把内存报告改写为已保存事实；本模块只返回计算结果，不声明持久化成功。

读取历史报告只支持只读显示、审计和差异比较。若方法、输入来源、后端或 Contract 修订改变，旧报告不自动成为当前适用性；重算必须创建新 `RequestId`，并保留 `SupersedesRequestId` 关系于宿主/原权威。未知字段、缺失来源或 hash 不匹配不得静默丢弃或按当前默认解释。

### 12.2 升级、回退和恢复决策

升级前宿主冻结当前包组合、运行中请求排空证据、方法矩阵、Golden 和性能基线；升级只在无运行 native 句柄、无在途 lease 且新组合通过版本/能力校验后启用。升级期间失败返回 `IQ-VER-011` 或 `IQ-RUN-007`，不混用新旧适配器输出。回退恢复原组合和原方法版本，重新跑最小 Golden；回退不能重写已存报告、改变调用方判定或把 Unknown 改为成功。若 native 无法排空，优先在宿主 worker 进程边界回收，模块不提供线程强杀。

## 13. 第二消费者与独立接入证明

第二个消费者不是复制源码的第二个项目，而是一个不共享第一个宿主 UI、配置、身份或数据库的独立 OCR/读码或 2D/3D 前置工具。它仅引用发布包、注入自己的帧/掩膜/诊断适配器、选择自己的方法集和资源 Profile；相同 Core 产生相同单位/方法/支持语义。宿主自行把 FrameId/PlaneId 关联到自己的对象和任务，并自行判定是否继续。

验收时临时断开第一个宿主仍能构建/运行第二宿主；扫描包依赖不得出现任一产品 VM、私表、设备 SDK、静态运行态或 UI 初始化依赖。改变消费者输入、显示语言、取消其中一个运行或卸载其控件，不能影响另一个消费者的请求与帧租约。第二消费者的失败不得污染第一个消费者报告或质量事实。

## 14. 精确后续合同、范围与资格门

以下事项分别归原合同/产品/资格Owner；总控只协调状态，不代做本模块内容审核。模块完整可决定软件设计结论见§24.5，未确认事项只阻断依赖它的范围，产品资格保持 `PreparationIncomplete / NotReady`：

1. C-03/C-04 中 `ImageFrameLease`、有效支持、曝光/条纹组角色、报告保存关联和正式错误码的 canonical 字段/序列化版本。
2. 首批消费者的真实 Profile：图像尺寸/位深/ROI 数、最大并发和排队策略、P50/P95/P99 周期预算、峰值托管/native 内存和取消排空上限。
3. 真实Golden集、方法数值容差及生产Profile适用资格；软件路线/类型/参数范围由本指导§20冻结，不让实施者自选。没有客户光学事实只阻断生产资格，不能用HALCON默认代工艺参数。
4. 结构光组支持已属于本模块批准范围，§16/20.5的公开方法/调用/完整性语义已冻结；具体产品是否将它列为Required及其与3D重建的原事实映射由对应产品/重建Owner采纳，不再等待是否设计该能力。本模块不拥有相位解码或重建。
5. 学习型质量不属于当前接口与实现范围，不是当前准备欠账；若用户另行批准，模型资产、离线训练/评估、Replay/Shadow/Advice阶段、模型hash及回退策略须先由AI治理与模型资产权威采纳，不能阻断当前确定性指标。
6. 可选WPF的正式宿主PageContract映射、权限及目标机真实验收；模块操作、控件和三语语义按§8.1/§23执行。

### 14.1 跨 Owner 合同采纳清单（仅采纳，不复制第二套事实）

本表是 IM-020 进入产品桥、诊断投影和持久化接入前的逐项采纳清单。表中“阻断用途”只表示未采纳时不能声称的实际用途；不把外部合同缺口改写成 IM-020 的算法或 API 设计欠账。**本模块当前批准范围内由 Owner 决定的软件设计欠账已闭合**；剩余项目是原 Owner 的合同采纳、宿主装配、运行验证或产品/客户资格门。

| 外部 Owner | 模块 ID | 指导/合同章节 | IM-020 必须采纳的字段、端口、Profile 或事实映射 | 未采纳时实际阻断的用途 |
|---|---|---|---|---|
| 图像帧与有效域 Owner | `IM-006 image-frame` | [image-frame §4.3–4.4、§6、§9、§19.1](../image-frame/DEVELOPMENT-GUIDE.md#43-module-api-contract-v01进程内-copystoragelease) | `ImageFrameLease`/`ImageSupportLease` 的借读身份、`FrameKey`/来源修订、plane 与像素类型/尺寸/有效域、读取窗口与 halo、借读期限、真实 Release/排空回执。IM-020 只消费适配后的不可变块，不复制租约或来源事实。 | 阻断真实产品帧/支持域适配、邻域指标和帧级报告关联；不阻断纯托管 Core 或显式 Simulator。 |
| 采集、相机、光源、运动与采集序列 Owner | `DEV-PLT-015`（采集宿主及设备能力 Owner；对应相机/光源模块由宿主接入） | [§10–14](../../shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md#acquisition-sequence-implementation) | 实际帧完整性、曝光/触发/光源/姿态/条纹步骤及其来源修订、请求值与实际值分离、采集封口、丢帧/背压、线程排空和取消恢复。不得把请求曝光、ACK 或当前设备设置写成历史实际事实。 | 阻断依赖真实采集证据的曝光/结构光质量准入、产品资格和现场报告；不阻断无设备的托管计算。 |
| 质量事实与结果提交 Owner | `IM-015 inspection-evidence`（来源包 `PKG-040`） | [IM-015 §3–8、§17；PKG-040 §7.1–7.4、§9–10；DEV-PLT-012 §1–8](../inspection-evidence/DEVELOPMENT-GUIDE.md#3-公共输入与输出契约) | `Evidence`/`EvidenceManifest` 与 source/derived 关系、`InspectionFact`/`RuleEvaluation`/`InspectionDecision` 角色、`CommitIdentity`/`OperationId`/`Receipt`/`OutboxIntent`、保持、幂等、fence、Unknown、崩溃恢复和对象引用。IM-020 只提交自己的质量观测投影，不拥有质量事实或提交状态机。 | 阻断生产结果提交、回放/复判证据闭包、未知提交对账和正式报告资格；不阻断内存报告或无持久化 Core 验证。 |
| 技术存储与文件对象 Owner | `IM-066 storage-database`（来源包 `PKG-041`） | [IM-066 §6–7](../storage-database/DEVELOPMENT-GUIDE.md#6-公开集成契约module-api-contract-v03-的-io-部分)；[PKG-041 §2–3](../../shared-modules/packages/PKG-041_Storage.md#2-职责与边界) | 仅采纳受控文件对象、数据库技术事务、保持/GC、对象引用、读回和恢复端口；实际质量事实、规则决定和放行仍归 IM-015/产品 Owner。所有 Unknown 保持原身份查询，不以存储成功替代质量提交事实。 | 阻断真实报告/证据对象保存、耐久读回、崩溃恢复和 GC/保持资格；不阻断不接存储的质量算法。 |
| viewer 诊断层与页面投影 Owner | `IM-060 viewport`；页面宿主另受 PageContract Owner 约束 | [viewport §10.4、§10.6–10.7、§15.2.1–15.2.2](../viewport/DEVELOPMENT-GUIDE.md#104-19201080-固定验证视口的-pagecontract)；[UI-PCS-014 §13](../../shared-modules/guidance/14-page-contracts/UI-PCS-014_Engineering_Diagnostics.md#13-采集链与成像质量的只读诊断) | 诊断层与原值/派生值/支持域的映射、当前 generation/backend revision、权限、迟到结果隔离、`Bind`/`Unbind`/Presenter 借用、页面命令和资源解绑。IM-020 不拥有通用 viewer、Scene、源缓存或产品页面事实。 | 阻断真实影像/ROI/诊断层联动、工程诊断页和 UI 资源归还验收；不阻断无 UI 质量服务。 |
| 结构光采集与步骤组 Owner | `IM-011 structured-light` | [structured-light §4、§7、附录 B.4.6–B.4.7](../structured-light/DEVELOPMENT-GUIDE.md#b4-下游公开消费桥-2026-10-11已支持范围指导内容限定接收)；采集实际步骤另按 DEV-PLT-015 §10–14 | 有序 pattern/曝光/条纹角色、step 身份与修订、组完整性、实际投影/采集证据和资格消费桥。IM-020 只提供逐帧原始质量、共同支持和组完整性，不实现相位解码、调制度或 Required 产品判定。 | 阻断结构光组质量证据和产品 Required 资格映射；不阻断单帧 2D 质量指标。 |
| 3D 解码、重建与高度事实 Owner | `IM-032 reconstruction-3d` | [§4.2.2、§4.4.1、§8.1；附录 B.4.6–B.4.7](../reconstruction-3d/DEVELOPMENT-GUIDE.md#422-完整结构光角色增量-r3d-sl-sequence-v1) | 结构光角色/步组输入、共同支持到重建请求的映射、重建诊断输出、层/高度事实与来源引用、装配前资格复查。IM-020 不输出相位/高度、不替重建 Owner 产生事实。 | 阻断 3D 前置质量与重建诊断/高度事实关联；不阻断 IM-020 的逐帧或组支持观测。 |
| 报告投影与客户输出 Owner | `IM-044 reporting`（来源包 `PKG-046`） | [reporting §3–5、§7](../reporting/DEVELOPMENT-GUIDE.md#3-module-api-contract-v02公开形状与有效域) | 只读报告输入快照、原值/显示值/单位/Validity/Reason、`Artifact`/`Metadata`/范围清单、输出格式、发布/Unknown/Partial 和权限映射；报告只投影 IM-020/IM-015 已有事实，不重算质量。 | 阻断正式单件/批次报告和客户输出；不阻断质量结果在服务内查询或工程诊断显示。 |

采纳顺序固定为：先由原 Owner 冻结公开字段、版本和事实权限，再由宿主完成 Adapter/PageContract/持久化装配，最后以真实编译、运行、Golden/Replay、WPF 和现场 Profile 验收。产品/客户 Profile（阈值、Required、性能、设备实际值和物理资格）缺失时对应用途为 `NotEvaluated/NotReady`，不得由 IM-020 补猜；这不改变本模块内部设计已闭合的结论。

## 15. 参考与自审

- 算法语义唯一详细位置：[本指导 §18–24](#image-quality-implementation)。方向/预处理边界：[DEV-VIS-021C](../../shared-modules/guidance/03-vision/DEV-VIS-021C_图像通道与预处理独立能力开发指导.md)。Contract/状态/Owner 依赖：[CONTRACT-CANDIDATES（采集与成像质量候选段）](../../13-contract-candidates/CONTRACT-CANDIDATES.md)、[DEV-VIS-020](../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md)。
- HALCON 26.05 本地页面：[`estimate_noise`](../../../halcon算子手册/operators/estimate_noise.html)、[`sobel_amp`](../../../halcon算子手册/operators/sobel_amp.html)、[`laplace_of_gauss`](../../../halcon算子手册/operators/laplace_of_gauss.html)、[`deviation_image`](../../../halcon算子手册/operators/deviation_image.html)、[`intensity`](../../../halcon算子手册/operators/intensity.html)、[`gray_histo_abs`](../../../halcon算子手册/operators/gray_histo_abs.html)、[`gray_histo_range`](../../../halcon算子手册/operators/gray_histo_range.html)。本页列出的 HALCON 默认和支持集只作方法显式配置的输入，不等同本模块默认；应在实现时同时复核相关 `toc_*.html` 和目标方法页。
- 只读公共边界观察：历史 `AsunControl` 消费者在 AsunImage 外部使用 `ImageLibDotNet`，通过 `Cv2.MinMaxGray`、`Cv2.SobelAmp`、`Cv2.GetDomain`、`Cv2.Intensity` 组织过质量样例；这些工程为 `.NET 8` 历史消费者，只证明可观察的命名空间/调用形状和资源责任，不证明本平台 `.NET 10` 的签名、版本兼容或算法资格。其固定评分和异常回退不迁入模块。目标实现必须改用已引用公共程序集/公开文档与编译核对，不能读取 AsunImage 源码树；历史观察不构成公共 API、质量方法或性能证据。
- 2026-10-06 只读来源：`H:\docs\40-development\41-vision-platform\03-calibration-imaging\图像质量与预处理流水线开发指导.md`，版本 1.12 / IND-REV-03，SHA-256 `14903113483e10088d44def9b003828bc7fa127921f5ad9ff80a14d66b9345dd`；身份核对见[全量 H:\docs 来源清单](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)。采纳 §8.5(2) 的域分类、§8.1.3 的确定性分区、末部活帧/逐检测域/文件借读章节中可独立迁移的持有、释放、容量和期限规则，落实在本指导 §6、§11、§18–20、§24。排除旧 AOI 私有 API、批准/签名及 canonical 协议、宿主编排/实施授权、固定 8-bit/256 bins、HALCON 24.11 参数和未经统计支持的“噪声不确定度”/弱梯度轴运动推断；预处理 Stage 与通道混合归 image-preprocessing，不在本模块复制。来源中的实现/测试陈述不作本平台通过证据。

自审结论（2026-10-11最后准备收尾）：ManagedCoreSlice-01六项及0.5.2-prep的§16.9服务关闭/§8.1–8.3保存知识与原意图查询接收保持，未重审算法。本轮只补§16.10公开托管端口/构造前有界根、§16.11两不同空Host完整Profile和原Task、§8.4 Presenter/原保存Owner与§8.5双STA Attach→Unbind。两轮分别按实现者正常→异常→恢复及外部消费者从空包装配走查，精确反例/断言见§24.4；服务完整六项与WPF内容分别送主控接收，未自行提升Ready。只有本文被修改；未创建工程、执行C#或上游代码、HALCON/WPF、性能/HIL/现场资格。

0.6.1-prep完整范围收口：上述0.6.0接收历史保持；本轮补§2.1 native搬运/域/结果提取、§17.1有限实验分母/停止/留出、§8.2具体视觉与联动限制、§14/24.5全范围结论。执行、内容自审与修复都在本模块永久原会话完成，不等待总控内容复核。只交付正文规格，不创建工程或执行产品资格测试。

### 15.1 本轮复用的官方资料与固定源码/测试证据（2026-10-09）

HALCON页均为本项目26.05.0.0原件，已读Description/Attention/Execution/Parameters，不改原件。补读[Filters章](../../../halcon算子手册/operators/toc_filters.html)关于reduced domain边界仍会读取域外值的正文，并核[Edges目录](../../../halcon算子手册/operators/toc_filters_edges.html)/[Noise目录](../../../halcon算子手册/operators/toc_filters_noise.html)候选导航；目录只证明候选分类，不证明算法/性能通过。

| 官方页/原件SHA-256 | 本指导采用与限制 |
|---|---|
| [sobel_amp](../../../halcon算子手册/operators/sobel_amp.html) / 51cdcdb81357af95d8a7010ec517643dd1b6e47eb53591cca4e96dfae3eac333 | Size/filter/输入输出/size>3倍率及CPU/OpenCL不同；§20.5固定主路线，不声称SIMD或大核一定最快。 |
| [derivate_gauss](../../../halcon算子手册/operators/derivate_gauss.html) / 95c7f307cf9a2bd4d43afa1cf776a5995c608a79f1af693d0c1da11f670cb408 | real输出、gradient/laplace/x/y及Sigma0.01..50；高位深实值分支、方向响应，不编Gaussian精确halo。 |
| [laplace_of_gauss](../../../halcon算子手册/operators/laplace_of_gauss.html) / 6e22c083bfa427b0e692525416d6ef33efd25f85c36cb6e31286453637143748 | 输出int2与Sigma0.01..25；仅独立UInt8候选，不等同Gaussian real。 |
| [deviation_image](../../../halcon算子手册/operators/deviation_image.html) / 860e4e29003f00ce2b79b5e2c75c91551686f4c8c85bb4bc3b62bf64846e14a4 | ≥3奇数窗口、2倍响应、镜像和OpenCL精度；§20.5保留响应不冒称noise。 |
| [estimate_noise](../../../halcon算子手册/operators/estimate_noise.html) / 43cec22be0593e197a9dcabec871af742ff8479890f9a138f3da8e3e55a9409f | byte/uint2、(0,50]、各假设及3175；固定全域估计，不以普通σ/tile平均代替。 |
| [gray_histo_range](../../../halcon算子手册/operators/gray_histo_range.html) / 52ebcbb49e20fd7378b12ddf2ba152ae7aa6a65c5307d175f49d024d71f864ce | 显式Region忽略image domain、整数/real宽度不同、边界较小bin；A是已定义的托管分箱合同，实际HALCON差分另验。 |

0.6.1仅定向补读以下HALCON26.05.0.0公开页的Description/Attention/Parameters/Result，解决§2.1搬运/有效域/读取缺口；不是重新研究已选算法，也未运行native。

| 官方页 / SHA-256 | 采用与限制 |
|---|---|
| [gen_image1](../../../halcon算子手册/operators/gen_image1.html) / d268da1562bab640cc506296c1684eaa643f97b84b705d3c9cf47bbdd5c019c3 | 行优先、复制像素、指针有效与64位不截断；禁止extern长借用。 |
| [gen_image_const](../../../halcon算子手册/operators/gen_image_const.html) / fe96d0a35794aaf042c21c3582f942abf28a332b14620750ce93fcbe5dc39d4c | 仅核类型：byte1/uint2及int2为2/real4 byte，不使用受全局init_new_image影响的未初始化图。 |
| [convert_image_type](../../../halcon算子手册/operators/convert_image_type.html) / 4e7ea41cc5be0f7e5dc4e95fc98a49441e8eb03788bf45c36d46776832d2312d | 缩窄类型会clipping，同类型不新增矩阵；按所选route转real，句柄/矩阵分开计账。 |
| [gen_region_runs](../../../halcon算子手册/operators/gen_region_runs.html) / 8f7f1845b85bc1873e1507f815f2153d956b6b7561fcdde61396dde4a3b2f203 | 升序runs、等长与包含终点，调用方必须校验起止；不依赖空域/全局clipping设置猜有效数。 |
| [get_region_runs](../../../halcon算子手册/operators/get_region_runs.html) / 39ae03235b99a4b34f24ff019d5738280f3da12ae1be1ebbfa81211193cd6c15 | 只传一份Region，取实际runs并与声明mask核对；空Region返回空tuple。 |
| [get_image_pointer1](../../../halcon算子手册/operators/get_image_pointer1.html) / 720f3d922e81b12d27615a17e2744fcb7b449c6db78b3ad78c957bac44b9ba35 | 行优先、本地图存活期间只读指针；仅首通道，必须核单通道和Type/尺寸。 |
| [get_grayval](../../../halcon算子手册/operators/get_grayval.html) / 930d4a89168dd7f5a3780e1ce21ec595c62ecf026a79342abe87e8f29042d2cf | 忽略image domain、有调用开销；只作有限Golden点读取，不作为滤波实现。 |
| [erosion_rectangle1](../../../halcon算子手册/operators/erosion_rectangle1.html) / e2060ce4738a575f2fa911a7cbe9f2562f37d45707feb76e893cd8a9c24f7d43 | 1..511且奇数才对称；使用已冻结footprint，不把偶数/域外值当真实支撑。 |
| [count_obj](../../../halcon算子手册/operators/count_obj.html) / 31cb3e6ee59a74e107689dcaae58c78a99728ee35bdc6da0b52163f133e5d8c9 | 核iconic对象数，不是连通分量数；非空mask构造必须1对象，侵蚀0对象不继续读取runs。 |

开源研究固定[Math.NET Numerics v5.0.0](https://github.com/mathnet/mathnet-numerics/tree/4435308e1b0efcb40dc483140059a4e3a2204044)，commit 4435308e1b0efcb40dc483140059a4e3a2204044；本轮联网raw读取与已有只读快照一致，GitHub API限流403不当研究正文，未新增快照。已实读Push/Combine实现与ShortSequences、ZeroVariance、Combine及NIST numacc测试；未运行上游测试。

| 已读原件/固定hash | 可迁移强项、依赖与排除 |
|---|---|
| [RunningStatistics源码](../../references/open-source/mathnet_numerics/4435308e1b0efcb40dc483140059a4e3a2204044/src/Numerics/Statistics/RunningStatistics.cs) / 01465c61b69661ba029b040c03df642085757431361b845236e93d9f0c7cb03c | 采用在线中心矩及可合并(n,μ,M2)思想到A.3/20.6，避免消减；不引入Math.NET包/高阶矩/持久化。Combine空一侧会返回可变原实例，不能作为独立快照；N<2 PopulationVariance的NaN与本模块N=1定义不同。高阶矩long乘积可能溢出不迁入。 |
| [RunningStatisticsTests](../../references/open-source/mathnet_numerics/4435308e1b0efcb40dc483140059a4e3a2204044/src/Numerics.Tests/StatisticsTests/RunningStatisticsTests.cs) / 980d923bc4e4ccd99057c8e12471b1396c84dcc9c5353cc8d5953beb5743cabd | 借鉴偏置/短序列/零方差/合并边界与NIST数据测试思想；部分期望仍引用同库，不能全部称独立oracle。测试依赖NUnit/其fixture，不复制为平台测试框架。 |
| [LICENSE.md](../../references/open-source/mathnet_numerics/4435308e1b0efcb40dc483140059a4e3a2204044/LICENSE.md) / 3f87fb0bec6467d87760555e3cb246646a51912b0e97f432c159ba6baf5738f2；[Numerics.csproj](../../references/open-source/mathnet_numerics/4435308e1b0efcb40dc483140059a4e3a2204044/src/Numerics/Numerics.csproj) / 2d80ad19c4f8371f39e21e03f8bf339e7b1abf00ccb7daf87be195cd9436e596 | MIT；该源码框架net6/net5/net461/net48/netstandard2，CodeAnalysis分析器与条件ValueTuple/FrameworkReferences。只移植数值思想并重写本模块BCL路线，不整包搬入，不把DataContract无跨版保证带进报告合同。 |

dxdocs本轮无可用工具、匹配WPF skill未发现，官方网页请求403，未读到网页正文；因此直接采用用户已安装25.2.3随附官方公开XML，仅核UI成员/说明，未扫描程序集内部、未做安装/许可/兼容审查。原件目录为C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/。§8.1中的组合均来自下列成员，网页/示例获取失败不算生产证据。

2026-10-11仅对新接线缺口补读同目录/同hash公开XML，未重新扫描依赖或研究算法：ColumnBase.FieldName、DataControlBase.SelectedItem、DataViewBase.ColumnHeaderTemplate/ShowEmptyText/IsColumnMenuEnabled/ShowSearchPanelMode/ShowFilterPanelMode、PropertyGridControl.ShowSearchBox与PropertyDefinition.ShowMenuButton、ChartControl.Diagram/Diagram.Series/Series.DataSource、ContentItem.Content。用于§8.4的实例呈现/语言方案；未将GridControlLocalizer.Active这类全局入口用于模块切语。dxdocs当前仍无可调用工具，匹配WPF skill未发现，故复用随附官方XML证据；此核对只证明公开成员定位，不证明真实WPF行为。

| 官方公开XML/完整SHA-256 | 实际核对成员 |
|---|---|
| DevExpress.Xpf.Docking.v25.2.xml / b11b45dd7afc27b5e16b679a6a9e2e4291ecd13cb1f8e1b7c0fbe4e94a64477f | DockLayoutManager、LayoutGroup/DocumentGroup/DocumentPanel/LayoutPanel；BaseLayoutItem.AllowFloat/AllowClose；SaveLayoutToStream/RestoreLayoutFromStream以及安全反序列化限制。 |
| DevExpress.Xpf.Grid.v25.2.Core.xml / 9ca164e53a54e5bc0eb6432a709e95c9295e60db3b0eac4fabf6dd32604b8eba；DevExpress.Xpf.Grid.v25.2.xml / 7537e3db16162155eda70058baccf40a6731f6dc9851ad31d382332c39c3d6bd | ItemsSource、EnableSmartColumnsGeneration、FocusedRowHandle、NavigationStyle、GridControl/TableView/TreeListView；行索引只作投影，Method/Region/Source为身份。 |
| DevExpress.Xpf.PropertyGrid.v25.2.xml / 0e0cb8a0503889f13cd86fa4d5db7cbb975c9c4f4506dfea8d681f68fc4a65c9 | PropertyGridControl.SelectedObject/ShowCategories；草稿通过同Core.Validate，不构造第二算法校验。 |
| DevExpress.Xpf.Charts.v25.2.xml / 2e80660ea0316294482e5b45096cc23c52250243e12551e84c117f692445bfb0 | ChartControl、BarSideBySideSeries2D、Series.ArgumentDataMember/ValueDataMember；仅显示投影合箱不改变原计数。 |
| DevExpress.Xpf.Core.v25.2.xml / cf99d297b336a80f2361fa8bb79369434a6a10b9426efa670d636803433e8196 | Core.SuperTip/SuperTipItem、Editors.Flyout.FlyoutControl；未核SuperTipControl不猜调用。 |


### AOI.Main 原图质量证据采纳

只读复核 [原图预览与保存指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-29-camera-original-preview-and-save-design.md) 后，质量指标必须明确输入是原始帧、派生图还是缩略图：全分辨率质量/像素指标不得从显示缩略图推导；派生图必须记录父帧、变换、填充策略和有效域。原图保存、质量计算和显示转换分别计账，异步结果携带帧 revision，旧帧迟到结果不能覆盖新指标。

## 16. Module API v0.1：QualityServiceSlice-02（后续无 UI 服务合同）

这是本模块自己的后续合同，供无UI模拟端口/实际AsunImage适配和两个独立消费者使用；不引用§3.4产品草图、不要求平台Shell。与附录A分切片接收，当前PreparationIncomplete。A只算托管标量，服务覆盖原帧区域统计、清晰度、噪声、局部均匀性、方向响应、RGB比例和结构光组支持，不能把完成A当成整模块完成。

### 16.1 唯一工程和组合边界

服务及端口/DTO仍在Core工程与namespace Asun.Modules.ImageQuality，契约/模拟测试在唯一Core.Tests；不会另建Contracts工程分裂权威。后续具体工程：src/Modules/image-quality/Asun.Modules.ImageQuality.AsunImage/Asun.Modules.ImageQuality.AsunImage.csproj（namespace Asun.Modules.ImageQuality.AsunImage；net10.0；引用Core与用户已有AsunImage）；测试为tests/Modules/image-quality/Asun.Modules.ImageQuality.AsunImage.Tests/同名csproj。产品FrameAdapter按宿主已有公开帧契约组合到IQualityInputPort，不复制其它模块lease；它的实际工程/共享接口由主会话在产品映射切片冻结。Wpf工程见§8.1。这里只指定未来落点，不授权本轮写src/tests或创建项目。

服务工厂显式注入输入、视觉和时钟端口；不找service locator、静态latest、设备SDK或磁盘路径。输入端口负责取得真实不可变借读及文件/采集来源当前性；视觉端口只通过ReadBlock获得独立二维不可变快照并调用cv2。额外复制明确计账，不称零复制。Core只组合方法、校验端口结果/支持域和封口；宿主拥有生产批准、报告保存和相依设备动作。所有集合使用ImmutableArray，字段无隐式默认；下列声明须位于一个namespace，不允许实现者加同义DTO。

### 16.2 完整服务/端口形状

~~~csharp
public readonly record struct QualityBox(int Row0, int Col0, int Row1, int Col1);
public sealed record QualitySourceRef(string SourceId, string Revision);
public enum QualitySourceKind { RawAcquisition = 1, Derived = 2, ImportedFile = 3 }
public enum QualityPixelType { UInt8 = 1, UInt16 = 2, Float32 = 3 }
public sealed record QualitySourceDescriptor(
    QualitySourceRef Source, QualitySourceKind Kind, string PlaneId,
    QualityPixelType PixelType, int WidthPx, int HeightPx,
    string CoordinateRevision, string? ParentRevision,
    string? ObservationGroupRevision, int? StepIndex,
    string? ExposureRevision, string? MotionRevision,
    string? ProjectionRevision, string? RadiometricRevision,
    DateTimeOffset? AcquisitionUtc, DateTimeOffset? ImportUtc,
    int? EffectiveBitDepth, double? BlackLevel, double? WhiteLevel);
public sealed record QualityInput(string RoleKey, QualitySourceRef Source);
public sealed record QualityRegionSpec(string RegionKey, QualityBox Bounds);
public sealed record QualityBudget(
    long ManagedBytes, long NativeBytes, long MaxReadPixels,
    long MaxOutputBytes, TimeSpan MaxDuration, DateTimeOffset DeadlineUtc);
public sealed record QualityIssue(string Code, string FieldPath, string MessageKey);
public enum QualityCurrentState { Current = 1, Unavailable = 2, Changed = 3 }
public sealed record QualityCloseResult(bool Released, QualityIssue? Issue);
public sealed record QualityBlock(
    QualityBox Bounds, QualityPixelType PixelType,
    ImmutableArray<double> Samples, ImmutableArray<bool> ValidMask,
    string SourceRevision, string CoordinateRevision);
public sealed record QualityBlockResult(QualityBlock? Block, QualityIssue? Issue);
public interface IQualityReadScope
{
    QualitySourceDescriptor Descriptor { get; }
    long RetainedManagedBytes { get; }
    long RetainedNativeBytes { get; }
    DateTimeOffset DeadlineUtc { get; }
    QualityCurrentState CheckCurrent();
    QualityDrainState CheckDrain();
    QualityBlockResult ReadBlock(QualityBox bounds, QualityBudget remainingBudget,
        CancellationToken token);
    QualityCloseResult Close();
}
public sealed record QualityOpenResult(
    Guid OpenAttemptId, IQualityReadScope? Scope, QualityIssue? Issue,
    bool ResourcesReleased);
public interface IQualityInputPort
{
    QualityOpenResult Open(Guid openAttemptId, QualitySourceRef source, QualityBudget budget,
        CancellationToken token);
    QualityDrainState CheckOpen(Guid openAttemptId);
    QualityCloseResult CloseOpen(Guid openAttemptId);
}
public enum QualityRoute
{
    RawStatistics = 1, Sobel = 2, LoG = 3, GaussianGradient = 4,
    GaussianLaplace = 5, Noise = 6, Uniformity = 7,
    LocalDeviation = 8, DirectionResponse = 9,
    ColorBalance = 10, StructuredGroupSupport = 11
}
public sealed record QualityObservablePolicy(
    long MinimumSamples, double MinimumCoverage,
    double? MinimumPopulationDeviation,
    double? MaximumLowClippedFraction, double? MaximumHighClippedFraction);
public abstract record QualityParameters;
public sealed record QualityRawParameters(
    ManagedQualityMethodSet Methods) : QualityParameters;
public sealed record QualitySobelParameters(
    SobelFilterType FilterType, int Size, SobelAggregation Aggregation)
    : QualityParameters;
public sealed record QualityGaussianParameters(double Sigma, SobelAggregation Aggregation) : QualityParameters;
public sealed record QualityNoiseParameters(
    NoiseEstimator Estimator, double Percent, string AssumptionRevision)
    : QualityParameters;
public sealed record QualityUniformityParameters(int Rows, int Columns)
    : QualityParameters;
public sealed record QualityDeviationParameters(int WidthPx, int HeightPx)
    : QualityParameters;
public sealed record QualityDirectionParameters(double Sigma) : QualityParameters;
public sealed record QualityColorParameters(
    ImmutableArray<string> OrderedRgbRoleKeys,
    ImmutableArray<double> ReferenceFractions, string ReferenceRevision,
    double MinimumTotalSignal) : QualityParameters;
public sealed record QualityGroupParameters(
    ImmutableArray<string> OrderedRoleKeys,
    ImmutableArray<int> OrderedStepIndices) : QualityParameters;
public sealed record QualityMethodPlan(
    string MethodKey, string Revision, string RegionKey, string RoleKey,
    QualityRoute Route, QualityParameters Parameters,
    QualityObservablePolicy Policy, bool Required);
public sealed record QualityServiceRequest(
    Guid RequestId, string ApiVersion,
    ImmutableArray<QualityInput> Inputs,
    ImmutableArray<QualityRegionSpec> Regions,
    ImmutableArray<QualityMethodPlan> Methods,
    QualityBudget Budget, int TileWidthPx, int TileHeightPx);
public enum QualityValueUnit
{
    Count = 1, Fraction = 2, GrayLevel = 3,
    KernelResponse = 4, KernelResponseSquared = 5
}
public sealed record QualityScalar(string Key, double Value, QualityValueUnit Unit);
public enum QualityMetricState { Computed = 1, NotObservable = 2, Unsupported = 3 }
public enum QualitySupportModel { OriginalPixels = 1, ValidNeighborhood = 2, OperatorRectangleBoundary = 3 }
public sealed record QualitySupport(
    long RequestedPixels, long ValidPixels, long CenterPixels,
    string CoordinateRevision, QualityBox Bounds, QualitySupportModel Model);
public sealed record QualityTileObservation(
    int RowIndex, int ColumnIndex, QualitySupport Support,
    QualityMetricState State, ImmutableArray<QualityScalar> Values,
    string? ReasonCode);
public sealed record QualityMetricObservation(
    string MethodKey, string MethodRevision, QualityRoute ActualRoute,
    QualityMetricState State, QualitySupport Support,
    ImmutableArray<QualityScalar> Values,
    ImmutableArray<ManagedQualityObservation> RawValues,
    ImmutableArray<QualityTileObservation> Tiles, string? ReasonCode);
public sealed record QualityBackendResult(
    QualityMetricObservation? Observation, string RuntimeRevision,
    long PeakAdditionalManagedBytes, long PeakAdditionalNativeBytes, long ReadPixels,
    bool Drained, bool ResourcesReleased, QualityIssue? Issue);
public interface IQualityVisualPort
{
    // 严格一次方法调用；Core借给端口的Scope不能由端口关闭。
    QualityBackendResult Observe(
        Guid invocationId, QualityMethodPlan method, QualityRegionSpec region,
        ImmutableArray<IQualityReadScope> scopes,
        QualityBudget remainingBudget, int tileWidthPx, int tileHeightPx,
        CancellationToken token);
    QualityDrainState CheckDrain(Guid invocationId);
    QualityCloseResult Close(Guid invocationId);
}
public enum QualityDrainState { Drained = 1, Pending = 2, Unknown = 3 }
public enum QualityOperationState
{
    Running = 1, Draining = 2, DrainUnknown = 3, ResourcesRetained = 4,
    Completed = 5, CompletedWithUnavailableMetrics = 6,
    Cancelled = 7, TimedOut = 8, Failed = 9
}
public sealed record QualityOperationSnapshot(
    Guid RequestId, long Sequence, QualityOperationState State,
    bool Drained, bool ResourcesReleased, QualityIssue? Issue,
    ImmutableArray<QualityIssue> Causes);
public sealed record QualityServiceReport(
    Guid RequestId, string ApiVersion, string ModuleVersion,
    ImmutableArray<QualitySourceDescriptor> Sources,
    ImmutableArray<QualityInput> Inputs, ImmutableArray<QualityRegionSpec> Regions,
    ImmutableArray<QualityMethodPlan> Methods,
    string RuntimeRevision,
    ImmutableArray<QualityMetricObservation> Observations,
    long PeakManagedBytes, long PeakNativeBytes, long ReadPixels);
public sealed record QualityOperationResult(
    QualityOperationState State, QualityServiceReport? Report,
    QualityIssue? Issue);
public interface IQualityOperation
{
    Task<QualityOperationResult> Completion { get; }
    QualityOperationSnapshot GetSnapshot();
    void RequestCancel();
    QualityCloseResult RetryRelease();
}
public sealed record QualityStartResult(
    IQualityOperation? Operation, QualityIssue? Issue);
public sealed record QualityStopWaitBudget(
    TimeSpan MaxWait, DateTimeOffset DeadlineUtc);
public interface IImageQualityService
{
    QualityRequestValidation Validate(QualityServiceRequest request);
    QualityStartResult Start(QualityServiceRequest request, CancellationToken token);
    // 有限观察同一关闭生命周期；Released=false仍须保留原service/operation。
    Task<QualityCloseResult> StopAsync(
        QualityStopWaitBudget waitBudget, CancellationToken waitToken);
}
public sealed record QualityRequestValidation(
    bool IsValid, ImmutableArray<QualityIssue> Issues);
public static class ImageQualityServiceFactory
{
    public static IImageQualityService Create(
        IQualityInputPort input, IQualityVisualPort visual,
        TimeProvider clock, QualityBudget instanceLimits);
}
~~~

System.Threading、System.Threading.Tasks、System.Collections.Immutable均为.NET公开类型；没有假设备句柄。SobelFilterType / SobelAggregation / NoiseEstimator复用§3.4同名枚举的值定义作为模块服务枚举，移入Core时只能各定义一次；产品候选必须映射它们，不创建同名第二定义。其它§3.4类不能编译到Core。ApiVersion固定image-quality-service-v0.1；ModuleVersion由包提供，不由请求伪造。RuntimeRevision必须非空且全部方法一次观察同一identity，后端漂移返回QS-RuntimeChanged。

### 16.3 校验、输出键和资源闭合

Validate只做结构、参数、引用、checked预算和期限校验，无来源IO/诊断副作用；Start总是重验，再Open取得真实Descriptor核实际域/来源。Inputs/Regions/Methods非空且身份唯一，所有已提供角色必须能精确定位，方法缺角色按§16.8保留缺项；方法RegionKey/RoleKey引用现有项（Group附加缺失角色按§20.5形成StepMissing，不提前当非法请求），Color/Group已提供的附加角色按参数声明顺序借入，缺角色按§16.8对应缺项，不按输入数组顺序猜色。Bounds全框在每个依赖来源中，坐标/组/配准修订匹配；无Source用最近帧补齐属于拒绝。Region独立统计，重叠不合并丢面积。原始单通道是精确plane；不隐式Rgb1ToGray，彩色转灰由预处理生成有父源的派生输入。

预算六项正有限（MaxReadPixels/MaxOutputBytes也是正），有效期限在Start时将UTC剩余时间转单调TimeProvider计时，取请求duration、请求绝对期限、实例duration/期限及各scope期限最早者；每个边界检查，不能因UTC后退续期。TileWidth/Height正且checked halo/面积/累计读取在预算内，分块规则见§20.6。scopes按SourceId+Revision去重，只借入一次；借入失败前已取得scope反序Close。所有scope持有直到端口实际返回、最后CheckCurrent及报告封口；只返回值，不返回活像素。

Open成功必须Scope非null/Issue=null；ResourcesReleased=true仅表示Open尝试未留有Scope以外的资源，不表示Scope已释放。失败Scope=null/Issue非null；若失败中实际资源尚未归还，ResourcesReleased=false，输入端口按OpenAttemptId保存实际Owner。服务先CheckOpen确认不再使用资源，再CloseOpen；成功阶段不重复关闭。OpenAttemptId由服务生成并传入，抛异常也能按同Id查询/释放；失败且已释放的CloseOpen重复调用幂等。ReadBlock同样二择一；Block严格二维行优先、Bounds原请求不裁切，Samples和ValidMask恰等块面积，PixelType/来源/坐标与Descriptor一致，valid=false也保留原位置。UInt8/UInt16值整数/范围正确，Float32必须满足(double)(float)value==value且有限；用double承载不提高原图精度。保留容量在任何复制前检查；端口不得在关闭后继续ReadBlock，视觉端口不得释放scope。端口返回异常/未知枚举均QS-ProviderFailure；零支持在native前生成不可观测项，Coverage仍0。

Policy.MinimumSamples≥1，MinimumCoverage在[0,1]；MinimumPopulationDeviation若存在须≥0，可选量必须有限，fraction在[0,1]。灰度门引用同原灰度码；Focus（Sobel/LoG/GaussianGradient/GaussianLaplace）与Direction必须提供非负最小总体离散及高低截断上限和用于门计算的RawStatistics（同角色/域且在方法列表先声明），不能猜阈值。Policy只是工程可观测性要求，不生产质量门。满足N/coverage但缺纹理时NotObservable/TextureInsufficient；明确参数错误拒绝整请求，3175只该方法NoiseNotEstimable；backend故障/数值损坏使整操作Failed并丢待发布报告，不按Optional吞执行故障。合法但输入类型无路由时该指标Unsupported，其他独立指标保留。

输出采用封闭Key表，不自由字典；Keys唯一、单位一致、有限数值，NotObservable/Unsupported不带Values/RawValues且Tiles空（RawStatistics的完整RawValues及Uniformity的Tiles是明确例外），保留Support/原因；Computed必须有本路线完整结果：
- RawStatistics：RawValues为附录A全部内层观察（包括NotObservable及Coverage0），Values/Tiles为空；内层Required全Computed则本容器Computed，任一内层Required缺失则本容器NotObservable/SubmetricUnavailable，保留完整RawValues。Policy固定MinimumSamples=1、MinimumCoverage=0、其它null，A自身逐指标规则是唯一计算语义。服务外层Required依容器状态影响报告，不能删除内层缺项。浮点输入的Descriptor保留Float32，不改成测量Float64精度。
- Sobel/LoG/GaussianGradient/GaussianLaplace：response，单位KernelResponse或平方聚合KernelResponseSquared，CenterPixels在Support；不得标mm精度。
- Noise：sigma/GrayLevel，不产生不确定度。LocalDeviation：twiceLocalStdMean/KernelResponse，保留2倍响应，不能叫Noise。
- Uniformity：mean、populationStd/GrayLevel，Tiles保留各块mean/populationStd；最差项键worstAbsMeanOffset/GrayLevel与worstTileIndex/Count，缺块时全域均匀性State=NotObservable，已有各块诊断仍保留Tiles；无有效块时全局Values为空。
- DirectionResponse：xAbs/yAbs单位KernelResponse，anisotropy单位Fraction；x+y=0时NotObservable/LowDirectionalEnergy，不填0比例；不输出MotionDirection。
- ColorBalance：r/g/bFraction、referenceDistance/Fraction（欧氏距离范围0..sqrt(2)）；3个reference非负和为1（容差固定1e-12），MinimumTotalSignal>0；基于每通道同域mean，缺标定/光谱事实NotObservable/RadiometricEvidenceMissing。不输出DeltaE。
- StructuredGroupSupport：presentSteps/requiredSteps为Count，commonValidFraction为Fraction，逐步曝光/来源/ProjectionRevision、相同组与唯一step完整后才Computed。缺step输出NotObservable/StepMissing，Values/RawValues/Tiles为空；期望步序从报告Methods原参数读取，不承诺未定义的诊断字段。不解码相位/提线。

RawStatistics的内层观察/Uniformity的局部Tiles是明确不可观测例外；其不可观测全局Values为空，均匀性validity仍不能自动变为Computed。后端需返回ActualRoute与请求一致、完整Support计数、ReadPixels累计、本方逻辑追加峰值和Drained/ResourcesReleased；伪造单位、样本数、raw histogram和count闭合在Core拒绝QS-OutputInvalid。ReadPixels累计包括halo与重复读取，不能只报unique有效数；BackendResult的PeakAdditional只含该invocation的block/native准备/本方元数据/输出，不能重复含service已经预留的scope/此前报告；ServiceReport的总峰值由服务把其常驻预留与该追加峰值合并；剩余额度只发一次，超限QS-BudgetExceeded。

### 16.4 并发、取消、迟到和释放失败

一个service实例一次接纳一个operation，无队列；Start同步校验并在短锁下占位，Busy/Stopping/非法请求返回Operation=null+Issue，不产生假终态。Work在后台本实例工作项串行执行，锁内不运行端口/native/回调。公开状态查询可并发，Sequence单调；Completion是唯一结果，快照只是执行事实，不作为质量发布。RequestCancel幂等，外部token注册只设置请求意图；均不终止同步native。

Running→Draining→资源确认→唯一Completed/CompletedWithUnavailableMetrics/Cancelled/TimedOut/Failed。取消或deadline后不发布报告，即使native返回完好的数值。输入断连/Changed先关闭发布，等native真退出后Failed/QS-SourceChanged；原scope不能被替换成新连接同Id。无法确认native退出是DrainUnknown，ResourcesReleased=false，Completion仍未结束；不能用Task取消、超时等待或Dispose正常返回解除输入。StopAsync使用§16.9唯一有限观察预算，停止准入、幂等请求在途取消，并观察同一operation资源确认；waitToken只取消本次观察。等待取消/到期返回Released=false/QS-WaitCancelled或QS-WaitExpired，仍持原service/operation/Owner，不能推断native已退出。

视觉端口在实际native未退出时不得返回假Drained；若后台隔离故障使状态未知，按invocationId保留本实例operation及实际Owner，GetSnapshot=DrainUnknown。RetryRelease先调用visual.CheckDrain；Pending/Unknown只返回Released=false，不关闭在用资源、不释放输入；后续worker退出确认须真实进入Drained。视觉端口的invocationId生命周期状态是本实例显式资源表，不是静态全局状态；方法顺序执行，前一方法未Drained/未释放不得开始下一方法。确认Drained后先visual.Close(invocationId)、再反序scope.Close；任何失败→ResourcesRetained，保存Owner/预留。RetryRelease仅重试未完成阶段，成功阶段不重复；同线程端口回调重入立即QS-Reentrant。最终确认Released=true、无在用原任务且Scope.Close均成功才结束Completion，首次释放失败即使以后成功也令该次Failed/QS-ReleaseFailed，不追补成功报告。服务无Dispose伪确认入口，宿主必须检查StopAsync结果。每port只保留当前operation内的关闭墓碑和最近完成operation的一份有界墓碑；新operation开始后可替换最近墓碑。service记录已成功阶段且不再重复调用它们；同operation Close幂等，未知/过期Id返回QS-InvalidRequest，不能维护无限历史表。

失败码封闭：QS-InvalidRequest、QS-InvalidSource、QS-UnsupportedVersion、QS-Busy、QS-Stopping、QS-SourceChanged、QS-ProviderFailure、QS-OutputInvalid、QS-RuntimeChanged、QS-BudgetExceeded、QS-Cancelled、QS-DeadlineExceeded、QS-WaitCancelled、QS-WaitExpired、QS-WaitBusy、QS-ReleaseFailed、QS-Reentrant。MessageKey固定ImageQuality.Error.<后缀>；取消优先于deadline，来源/数值/资源失败优先于取消；所有已观察执行错误保留到Snapshot.Causes，不使用异常字符串代操作员说明。只有纯输入内容不支持为逐指标Unsupported。重试均由宿主显式新RequestId/输入revision，不在模块盲目自动重算。

### 16.5 最小 Host 与两个消费者

最小无UI host只引用Core，注入TestInputPort（不可变内存/可控Open与Close）、TestVisualPort（具名算例/因果屏障）及TimeProvider。已接收Stop/finally回归示例见§16.9；可外部包装配的完整根/公开端口/两个Host见§16.10–16.11；不是只写正常Completion→Stop的可选模式。这些port类仍仅位于Core.Tests的QualityServiceHostContractTests，并完整实现§16公开接口，不成为产品shim；模拟不声称HALCON通过。

独立OCR/读码工具使用RawStatistics+Sobel、关键字符/码ROI，Required缺项时宿主停止读取；独立3D工程工具使用每步RawStatistics+StructuredGroupSupport，可选Noise，StepMissing时宿主不重建。双方注入自己的来源/预算/批准组合且单独打包部署，只共享发布Core/AsunImage DLL。无数据库、Shell或隐藏窗口亦能执行；二者都不把Computed解释为PASS；一方取消/断连/Stop不触及另一实例。只有真实输入bridge依赖正式帧契约，两个软件host可先用独立文件/内存来源验公开端口。

### 16.6 执行顺序、预算账本与失败打开闭环

这些规则是§16接口的实施步骤，不是交给适配器自行设计的选项。
1. Start在短锁中占位并冻结请求；先检查实例限制、版本、集合和参数。后台工作按Inputs声明顺序、SourceId+Revision去重Open，服务生成每次OpenAttemptId；每个方法另生成唯一invocationId，供Observe/CheckDrain/Close使用，不能多个方法复用RequestId作为资源Id。
2. 输入/输出标识、修订和所有资源MessageKey限128 UTF-16字符；ImmutableArray.Default、null元素、未知枚举均拒绝。QualityBox为半开整数像素框。Descriptor宽高正，引用非空；Derived必须ParentRevision；ImportedFile必须ImportUtc且AcquisitionUtc可未知；RawAcquisition必须AcquisitionUtc。有效位深若存在须1..8/16，BlackLevel/WhiteLevel若存在须有限且Black<White；未知物理白电平不从容器最大值补齐。
3. 用不可变请求/报告的逻辑预算账本：元数据为4096 + 每Input/Region/Method/Scope各1024 + 每输出Observation/Tile各2048 + 所有保留字符串2×Length。图像/块按Samples的8×面积、mask的1×面积以及每数组64字节预留；native使用scope.RetainedNativeBytes和适配本方准备/响应/Region/Tuple容量。预算计保留容量而非短payload。所有算式checked；分配前取父额度剩余量。账本约束本方逻辑工作集，不能当CLR/RSS或HALCON内部工作区的已证明硬上界；实际峰值另测并用于Profile资格。
4. scope.RetainedManagedBytes/NativeBytes包括来源为本次借读保留的完整容量，非负且调用期间不得静默增大。不同SourceRef不能假定共享；同SourceRef只Open一次。同一个返回block由读取者持有到本次消费结束，不缓存；ReadBlock接收当前剩余预算，须在创建完整数组前拒绝超限。managed剩余=上限−仍持有的源/请求/报告/准备；native同理；MaxReadPixels为累计读取（含halo/重复读取）剩余；MaxOutputBytes为累计最终保留结果的剩余，不能在每个方法重置。MaxDuration为单调剩余时间，DeadlineUtc保持原最早期限。仅请求/实例上限要求六项正；内部剩余额度允许资源项为0，但任何需要分配/读取项必须足额，过期就停止工作并转drain，释放工作不因预算用尽而被拒绝。
5. 各方法按请求顺序串行Observe；一个invocation的Drained且ResourcesReleased/Close确认前不能开始下一方法。结果输出先验证类型/单位/计数/来源/有限值，再复制进入报告账本，关闭该invocation后归还仅已释放临时量。RawStatistics见§20.6；返回RawValues的方法参数和RegionKey须与请求精确一致。Float32映射A的Float64只是double承载，报告Sources保留Float32。
6. CheckCurrent在每个ReadBlock前后、每个Observe返回和封口前执行；变化/断连即禁止发布并按QS-SourceChanged结束。最后CheckCurrent仅证明封口时借读来源一致，报告不持有活帧，也不保证来源以后永不变。所有scope关闭成功后才发布Completion/报告；关闭失败丢待发布成功报告并保留Owner。
7. Open抛异常或资源未知，按已生成OpenAttemptId调用CheckOpen；Pending/Unknown只记录Draining/DrainUnknown。确认Drained后CloseOpen，再反序关闭已取得scope。所有查询必须非阻塞、线程安全，只读实际执行状态；CheckOpen/CheckDrain返回Unknown不能解读为已退出。
8. Open/ReadBlock/Observe/Close可能同步进入native，均在显式后台工作项执行，实际返回前保留任务、参数、scope、预算和Owner。不能Task取消后丢弃返回值。RetryRelease仅调度一次未完成释放阶段并返回当前Released状态，不在调用线程等待native；同一关闭任务未返回时禁止并发再次Close。StopAsync按§16.9有限等待同一生命周期，waitToken只停止观察；同实例最多一份活动Stop观察，不每次Stop重新创建关闭任务。查询和调度锁不覆盖端口调用；挂起任务不终结Completion、不开放新Start，宿主可在自己的隔离worker边界恢复，不能线程强杀。
9. 报告状态：全部Required容器及其中Required原量已算为Completed；任一Required不可观测/不支持为CompletedWithUnavailableMetrics，Optional缺项保留但不改变该完成状态。执行故障仍整次Failed。失败优先级为输出/来源/释放故障→取消→期限；同时发生的其它原因存入Snapshot的Causes，不覆盖首个故障。重复RequestId不返回历史缓存；同实例运行时Busy，完成后同字节可重新计算，方法/来源改变应新RequestId。
10. 重入检测覆盖Open/ReadBlock/Observe/Close及诊断回调；重入同实例的Start/RetryRelease/Stop调度拒绝QS-Reentrant，不死锁。GetSnapshot是只读可调用。工厂null端口/时钟抛ArgumentNullException，非法instanceLimits抛ArgumentException；请求null由Validate/Start返回QS-InvalidRequest。没有服务进度事件，宿主有界查询Snapshot，不生成第二结果通道。Snapshot.Causes按发生顺序仅保留去重(code,fieldPath)项，最多64项，超出附一项QS-DiagnosticsTruncated并停止增长；该诊断不改变终态优先级，必须计预算。QS-DiagnosticsTruncated只作附加诊断，不是新的执行故障。

Policy不足原因固定NoValidPixels、SubmetricUnavailable、SamplesInsufficient、CoverageInsufficient、TextureInsufficient、LowClipped、HighClipped；NoiseNotEstimable、LowDirectionalEnergy、RadiometricEvidenceMissing、ColorSourceMissing、StepMissing、GroupEvidenceMissing、MaskUnsupported、PixelTypeUnsupported、MethodVariantUnsupported为方法原因。Computed ReasonCode为空；NotObservable/Unsupported必须原因非空。输出Support须0≤Center≤Valid≤Requested，Bounds/CoordinateRevision匹配本方法域，Model按§20路线固定。Required不能从请求删除后宣称原任务齐全。

服务接纳时创建TimeProvider单调截止计时器（同时保留GetTimestamp起点），计时器仅设置deadline意图并把在用工作投影Draining，RequestCancel同理；不调用端口或释放。native正常同步执行且未返回时就是Pending/Draining，只有无法确认工作所在/退出事实才DrainUnknown。Open/ReadBlock/Observe各工作任务都实际结束并端口Check确认后才进行释放；Observe提前返回Drained=false时不接受其Observation，即使随后CheckDrain=Drained也不追补成功报告（接口无迟到结果通道），按QS-ProviderFailure走释放。取消/超时先被请求时仍按终态优先级保留Cancelled/TimedOut；真实端口执行错误仍优先Failed。最后释放计时器/token注册，资源阶段发生的失败不被截止意图覆盖。

Open返回畸形组合（例如Scope与Issue同时存在）时，服务仍登记已返回Scope与OpenAttemptId，先保存所有实际Owner再Failed，不仅按合法成功字段挑一个引用。QualityOpenResult.OpenAttemptId须精确回显调用Id；Id错仍用调用Id关闭端口失败尝试，并保留返回Scope单独归还。ReadBlock的托管输出由调用方消费后清引用，port内部native残留属于scope；不能返回带活native别名的Samples。查询抛异常变Unknown/ProviderFailure，不能解读为资源已释放。


### 16.7 正常与故障的独立Host夹具

Core.Tests中的QualityServiceHostContractTests用固定TimeProvider和显式闩锁控制端口，测试入口见§24.2。最小请求由4×1 UInt8 [0,100,254,255]、全true mask、roi=[0,0,1,4]、RawStatistics(Saturation 0/255 + Coverage，内层两项Required)构造；Inputs只有role-gray与source-gray/rev-1，Policy为MinimumSamples=1、MinimumCoverage=0，其余null，有限budget与实例上限一致。依§16 DTO构造→§16.9 Host构造工厂→Start→有限Completion观察/核原量→无条件finally有限Stop；等待/消费失败不覆盖关闭诊断，Stop未确认时Host继续持有同operation。正常夹具必须最后Released=true。最小host不使用Shell或未声明helper；TestInputPort完整实现Open/CheckOpen/CloseOpen/Scope，TestVisualPort按冻结原始夹具返回A结果。

| 用例ID/反例 | 必须满足的断言 |
|---|---|
| QS.H01 正常/两个独立host | 上述数值、声明顺序、源/方法修订不变；一方关闭另一方仍可运行。 |
| QS.H02 全false/不完整组 | Coverage0；依灰度项NoValidPixels；Group期望[0,1,2]实际[0,2]为StepMissing，不能删除step1补Computed。 |
| QS.H03 mask错长/非法边界/未知参数类 | Start拒绝，Open次数0；PixelType合法但不支持某路线只该项Unsupported。 |
| QS.H04 Open失败留资源/抛异常 | 已知OpenAttemptId仍可查询；Pending时不Close/不Completion；Drained后CloseOpen成功，已取得scope逆序关闭，最终Failed。补充§16.9 QS.STOP.01有限观察及重复Stop同原Owner。 |
| QS.H05 native卡住/取消/超时 | RequestCancel或固定时钟期限后报告永不发布；释放闩锁前Completion未结束、无第二Start；之后Cancel/Timeout终态及资源归还。补充§16.9 QS.STOP.02独立finally有限等待，不延长执行期限。 |
| QS.H06 Close首次失败/重试 | ResourcesRetained；第一次Snapshot保留失败；RetryRelease成功也最终Failed/QS-ReleaseFailed；已成功关闭阶段计数不增加。补充§16.9 QS.STOP.03关闭挂起不叠任务、Repeat Stop不自动重试。 |
| QS.H07 迟到/断连/新revision同Id | 原scopeChanged即Failed；新源不能替换原在途scope；旧报告不进入新UI代次。 |
| QS.H08 预算/并发/重入 | 每方法剩余额度递减；原预留大槽超过budget在复制前拒绝；Busy/Stopping/Reentrant确定；Close并发调用次数最多1。 |
| QS.H09 版本/重复/回退 | 未知ApiVersion以QS-UnsupportedVersion拒绝不Open；完成后同字节重跑同值；回退只解释对应版本报告，不重写已生成结果。 |


### 16.8 请求/输出封闭校验、计数与端口恢复细节

Route与Parameters运行时类型必须一一对应§20.5：不接受派生未知参数类、不按字段相似猜路线；枚举必须为已列值，方法键全局唯一，Revision/RegionKey/RoleKey非空。Inputs/Regions/Methods数量与输出Observation数、语义网格Rows×Columns先checked核预算和BCL int数组长度；因集合超预算拒绝而非先创建输出投影。Budget.ManagedBytes/NativeBytes/ReadPixels/OutputBytes来自显式请求，每项须≤实例上限，期限取较早；实例配置NativeBytes必须正，但无native路线实际预留可为0。

Group允许OrderedRoleKeys引用尚未提供的Inputs，以形成StepMissing；主RoleKey仍须存在且属于OrderedRoleKeys，step索引非负/唯一，提供的每个角色若实际StepIndex不等期望是QS-InvalidSource，不解释为缺失；ProjectionRevision/ObservationGroupRevision/ExposureRevision为空是GroupEvidenceMissing，不补最近一步。Color的主RoleKey须属于三个OrderedRgbRoleKeys，三个角色必须都提供，缺角色为NotObservable/ColorSourceMissing；提供源的坐标/尺寸冲突仍QS-InvalidSource。共同有效域是所有依赖源mask交集，ValidPixels/CenterPixels及coverage用同交集；依赖源任何一个CheckCurrent变化即整次Failed。

Policy门按固定顺序判断：0支持→NoValidPixels；Center<MinimumSamples→SamplesInsufficient；Valid/Requested<MinimumCoverage→CoverageInsufficient；原总体σ<MinimumPopulationDeviation→TextureInsufficient；低截断比例>上限→LowClipped；高截断比例>上限→HighClipped。等于门值允许；比例原分母固定N，不用中心N冒替饱和分母。RawStatistics的A合同例外按§16.3；Colour/Group若信号/依据缺失先给具名原因，不填Computed。在完整矩形边界路线中Center=Valid=Requested，Model=OperatorRectangleBoundary；Sobel3/Deviation的Center是有效窗口中心数；其它统计/共同mask路线Center=Valid、Model=OriginalPixels。

Computed标量键、数量、单位严格按§16.3：不得多键/少键/重复键。Count型scalar为有限非负整数且≤2^53（超出精确double计数域QS-OutputInvalid），真正raw计数仍long；Fraction通常0..1，唯referenceDistance允许0..sqrt(2)。KernelResponse/平方和sigma非负，Uniformity mean允许Float32真实有符号码，populationStd/worstAbsMeanOffset非负，worstTileIndex为合法行优先索引。RawValues全部内层state/value/method/domain闭合且方法顺序一致。RuntimeRevision非空同实例恒定；各方法输出Support.Bounds/CoordinateRevision匹配原源区域、Requested等框面积，不能只相信backend自报N而省略结构验证。Service不能从Support摘要证明所有像素数正确，实际差分/Golden是§10门，不把结构校验等同视觉资格。

QualityBackendResult：正常Observation非null/Issue=null；执行故障Observation=null/Issue非null，不以Optional吞故障；Drained=false绝不能ResourcesReleased=true。若Observe抛异常/返回null或畸形值，服务按已生成invocationId保留资源查询并Failed/QS-ProviderFailure或OutputInvalid，不丢Owner。ReadBlock抛异常/返回畸形Block时scope仍持有所有端口侧准备资源；服务可查询scope.CheckDrain，且不提前scope.Close。Scope只归还它自己的借读；输入port自己的OpenAttempt残留与scope分开处理。Close/CloseOpen Released=false必须Issue非空（Pending/Unknown用QS-DrainPending/QS-DrainUnknown只作资源诊断）；Released=true必须Issue=null；首失败保留Causes。原成功结果可能先完成计算、后来源关闭失败，仍不能发布报告。

诊断码新增QS-DrainPending/QS-DrainUnknown/QS-DiagnosticsTruncated仅用于资源/附加诊断，不是另一个执行终态；其三语资源为“等待计算退出/等待計算結束/Waiting for calculation to exit”、“无法确认计算退出/無法確認計算結束/Calculation exit unconfirmed”、“诊断已截断/診斷已截斷/Diagnostics truncated”。方法原因ColorSourceMissing三语“缺少颜色通道/缺少色彩通道/Color channel missing”。输出畸形、未知关闭阶段与端口异常均不自动重连或补读取；显式RetryRelease只重试实际尚持有阶段。Service启动新请求前必须确认上一个operation全部Drained/Released；已完成报告由宿主持有，其内存不计新operation，但模块不能暗中保留报告副本。


### 16.9 有限Stop观察、最小Host异常收尾与原Owner保留（2026-10-10）

这是QualityServiceSlice-02的唯一关闭方案：使用§16.2的StopAsync(QualityStopWaitBudget,CancellationToken)，不保留仅token的重载、不由编码者自选默认等待或另造关闭工厂。ImageQualityServiceFactory.Create(input,visual,clock,instanceLimits)不变；同工厂的TimeProvider用于执行与关闭观察。操作的执行deadline、native实际退出、关闭资源事实、调用方观察等待四者独立；不能把观察截止点变成ResourcesReleased。

**有限入口与同一关闭生命周期**
1. waitBudget非null，MaxWait必须0<且≤30秒，DeadlineUtc不得为DateTimeOffset.MaxValue/MinValue；非法预算返回Released=false/QS-InvalidRequest，字段指waitBudget，不创建观察/任务，也不改变准入。允许过去的有效DeadlineUtc：它表示观察已到期而非参数非法，仍按下面规则停止准入，不等待并返回QS-WaitExpired。没有隐含无限值。
2. 合法Stop先在短锁中将实例准入状态置Stopping（不可恢复），幂等标记原operation取消意图，取得唯一内部关闭完成信号。没有在途operation时，本实例资源表确为空才能Closed/Released=true；不能仅凭外部Operation=null推断内部资源为空。Stop不直接关闭Host拥有的input/visual对象，不执行设备/存储动作。
3. Stop不是新的operation：第一次合法Stop只启动/唤醒本实例已有协调工作，不重复Open、Observe或正在执行的Close；重复Stop只观察原operation与同一资源阶段表。首次释放失败后，Stop不自动重试失败阶段，须原operation.RetryRelease显式推进；Stop观察不能掩盖原QS-ReleaseFailed或导致第二个native Close。所有请求/源/预算Owner直到真实归还仍在同一实例。
4. 等待先检查确已Closed：即使waitToken已取消/观察已过期仍可返回已确认Released=true/Issue=null。未Closed时，先检查waitToken取消→Released=false/QS-WaitCancelled，再检查有效等待到期→Released=false/QS-WaitExpired；正在观察的冲突调用→Released=false/QS-WaitBusy，不另建观察任务/队列/计时器。它们都不改变operation执行终态。
5. 同实例最多一个活动Stop观察槽，使用同一关闭完成信号及该调用的单调截止计时器/token注册。观察期限取MaxWait、接入时DeadlineUtc−clock.GetUtcNow()较早者，接入后冻结为单调计时，不随UTC回退延长；也不因Repeat Stop重设请求执行deadline。TimeProvider计时器仅完成观察返回，不访问端口/关闭资源。结束/取消/到期后finally销毁该观察计时器/token注册并归还槽；未释放的原任务/预算/Owner不受影响。
6. 与观察到期同时释放时，在锁内核Closed事实优先；未确认则Released=false，不要求等native退出才让Stop有限返回。已有ResourcesRetained且无在用释放任务时可立即返回Released=false/原QS-ReleaseFailed，不必占满观察预算；Pending/DrainUnknown则有限观察至事实变化/截止。等待本身的取消和截止以QualityCloseResult结构化返回，不让OperationCanceledException成为“已关闭”。资源错误使原operation Failed，观察错误只记本次返回，不覆盖原失败原因。
7. 原operation.RequestCancel、RetryRelease/GetSnapshot不执行同步native；正常Close/Check后台任务仍受§16.6约束。端口异常/查询异常转原资源未知/失败阶段，关闭观察返回Released=false及对应Issue；协调内部出现未预期异常亦保留原任务/阶段/Owner并回QS-ProviderFailure，不让等待Task异常丢引用。Host仍须防御外部契约破坏/消费异常，执行以下finally。Released=false必须Issue非空；Released=true仅证明实例拥有的执行/资源已归还，不代表计算成功、宿主消费成功或原产品租约所有消费者均结束。
8. 资源未确认时只保留一份原operation、资源阶段表、最多一个在用native工作/释放阶段任务、一个活动Stop观察与§16.4有限墓碑，不创建每次Stop对应的新后台关闭Task。Completed/Failed的report投影不作为关闭证据；Host查询operation.GetSnapshot仅查看原RequestId/Sequence，不创建新Operation。服务不提供Dispose/另起实例来替代未知关闭。

QS-WaitExpired三语为“等待已到期，尚未确认释放/等待已到期，尚未確認釋放/Wait expired; release unconfirmed”；QS-WaitBusy为“已有关闭等待，请稍后查询/已有關閉等待，請稍後查詢/A close wait is active; check later”。它们属于MessageKey=ImageQuality.Error.WaitExpired/WaitBusy的观察诊断，不是新的执行TimedOut/Failed原因。

**可构造Host与完整finally示例**

以下类位于未来Core.Tests的QualityServiceHostContractTests样例区，使用System、System.Threading、System.Threading.Tasks和Asun.Modules.ImageQuality。它只持一份service/operation与有限诊断，不是模块公开API/产品通用框架；input/visual可为§16.7的确定性端口，request按该夹具完整构造，consume用同夹具的数值/来源断言或故意抛异常。没有未声明Handle/Dispose helper。Host Owner必须在ExecuteAsync前把此对象保存在本宿主唯一恢复槽中，不能临时new后只依靠调用栈；正常/异常都运行同一finally。

~~~csharp
public sealed class QualityExampleHost
{
    private readonly IImageQualityService _service;
    private readonly TimeProvider _clock;
    private int _entryGate;
    private bool _attempted;

    public IQualityOperation? Operation { get; private set; }
    public QualityCloseResult? LastClose { get; private set; }
    public Exception? WorkFailure { get; private set; }
    public Exception? CloseFailure { get; private set; }
    public Exception? RecoveryFailure { get; private set; }
    public bool HasRetainedOwnership { get; private set; } = true;

    public QualityExampleHost(
        IQualityInputPort input, IQualityVisualPort visual,
        TimeProvider clock, QualityBudget limits)
    {
        _clock = clock ?? throw new ArgumentNullException(nameof(clock));
        _service = ImageQualityServiceFactory.Create(input, visual, clock, limits);
    }

    public async Task<bool> ExecuteAsync(
        QualityServiceRequest request, Action<QualityOperationResult> consume,
        CancellationToken observationToken)
    {
        if (Interlocked.CompareExchange(ref _entryGate, 1, 0) != 0)
            throw new InvalidOperationException("Host entry is already active.");
        if (_attempted)
        {
            Volatile.Write(ref _entryGate, 0);
            throw new InvalidOperationException("Use the retained operation.");
        }
        try
        {
            _attempted = true;
            ArgumentNullException.ThrowIfNull(request);
            ArgumentNullException.ThrowIfNull(consume);
            var start = _service.Start(request, observationToken);
            Operation = start.Operation; // 立即保留，不先await或调用consume
            if (Operation is null || start.Issue is not null)
                throw new InvalidOperationException(
                    start.Issue?.Code ?? "Invalid Start result.");

            var result = await Operation.Completion.WaitAsync(
                TimeSpan.FromSeconds(5), _clock, observationToken)
                .ConfigureAwait(false);
            consume(result); // 等待已结束也可能消费失败
        }
        catch (Exception ex)
        {
            WorkFailure ??= ex; // 不覆盖后续关闭问题，也不写生产事实
        }
        finally
        {
            try
            {
                // 不能把已取消的observationToken用于异常收尾。
                await ObserveCloseCoreAsync(false, CancellationToken.None)
                    .ConfigureAwait(false);
            }
            finally
            {
                Volatile.Write(ref _entryGate, 0);
            }
        }
        return WorkFailure is null && LastClose?.Released == true;
    }

    public async Task<bool> ObserveRetainedAsync(CancellationToken waitToken)
    {
        if (Interlocked.CompareExchange(ref _entryGate, 1, 0) != 0)
            throw new InvalidOperationException("Host entry is already active.");
        try
        {
            if (!HasRetainedOwnership) return true;
            return await ObserveCloseCoreAsync(true, waitToken)
                .ConfigureAwait(false);
        }
        finally
        {
            Volatile.Write(ref _entryGate, 0);
        }
    }

    private async Task<bool> ObserveCloseCoreAsync(
        bool advanceRelease, CancellationToken waitToken)
    {
        if (advanceRelease && Operation is not null)
        {
            try { Operation.RetryRelease(); } // 非阻塞，只推进未完成阶段
            catch (Exception ex) { RecoveryFailure ??= ex; }
        }

        try
        {
            var budget = new QualityStopWaitBudget(
                TimeSpan.FromSeconds(5), _clock.GetUtcNow().AddSeconds(5));
            var close = await _service.StopAsync(budget, waitToken)
                .ConfigureAwait(false);
            if (close is null || (close.Released && close.Issue is not null) ||
                (!close.Released && close.Issue is null))
                throw new InvalidOperationException("Invalid close result.");
            if (close.Released && Operation is not null)
            {
                var snapshot = Operation.GetSnapshot();
                if (!snapshot.Drained || !snapshot.ResourcesReleased ||
                    !Operation.Completion.IsCompleted)
                    throw new InvalidOperationException("Release is unconfirmed.");
            }
            LastClose = close;
            if (!close.Released) return false;
            HasRetainedOwnership = false;
            Operation = null; // 仅全部资源事实已确认时清本方operation引用
            return true;
        }
        catch (Exception ex)
        {
            CloseFailure ??= ex;
            // 保留原_service/Operation，不Dispose，不返回“已释放”。
            return false;
        }
    }
}
~~~

§16.9原QualityExampleHost保留为已接收的单次Stop回归样例；新工具/Presenter统一使用§16.10进程根，不能靠这份局部对象代替构造前登记。示例返回bool只表示“消费流程无异常且本实例关闭已确认”，不是质量PASS；实际QualityOperationResult由consume按原state核验，Failed/Cancelled不能当Completed。WorkFailure/CloseFailure/RecoveryFailure只在测试诊断读取，不把原Exception当操作员文案。ExecuteAsync只执行一次；重复Execute在工作块外拒绝并释放入口槽，不覆盖已有工作/关闭诊断。后续关闭观察始终ObserveRetainedAsync，同对象/同RequestId、没有重新Start/新工厂。Host等待取消/超时或consume抛错后，finally使用独立的有限5秒budget和CancellationToken.None，绝不无限等native；返回false且HasRetainedOwnership仍true时原宿主恢复槽不得丢弃此对象。

**有界保留与确认转交**
- service负责实际输入scope、invocation、OpenAttempt与预算Owner，Host恢复槽负责保住service/原operation引用、来源关联与诊断。每次有限等待结束只清本次观察注册，不清原Owner。一个Host槽最多持一份未解决实例；未解决时禁止再创建相同消费者的新Host绕过预算/关闭，也不累计每次Stop的Task/异常列表。新请求实例只能在原已确认归还或主Owner接受了独立额度/隔离方案后进入，不由本模块自动安排。
- Host继续存活时，人工或明确调度按原operation.RetryRelease→有限Stop观察推进；不自动busy-loop、不递归Stop、不每次重建input/visual。若释放任务仍Pending/Unknown，RetryRelease不启动第二Close；若首次Close失败并已返回，仅显式RetryRelease重试该未完成阶段。第一次失败仍决定原Failed/QS-ReleaseFailed，后续资源释放不能补成功报告。
- Host准备关闭/卸载而HasRetainedOwnership=true时，必须把同一QualityExampleHost（实际宿主可用同等原service/operation/阶段Owner值）交给其既有恢复Owner的一个有界槽。接收者先实际保留原对象及未解决状态并返回明确接收确认，发送者核同一对象/RequestId后才解除自己的Owner责任；不是只发通知或新建service代替。接收过程异常/超时/容量不足/无确认，发送者保持原引用与恢复责任，禁止继续销毁借读Owner。交接确认只表示责任已转交，不是Drained/ResourcesReleased。
- 新Owner只查询/推进该原实例；不得以new operation、像素复制、同Id新来源或修改期限“恢复”已在用native。接收/发送同一时刻只一方具有推进释放权。接收者保留对象并返回接收确认时仍只保留、不推进；发送者实际收到并核验确认后，先停止新观察/RetryRelease、结束本方活动观察，再沿Host已有串行交接机制明确授予接收者推进权。只有实际取得该授予后接收者才可推进；接收确认丢失/异常时没有授予，发送者仍保留责任，接收者不得自行启动恢复，避免重复Close。交接槽/记录有限容量沿Host已批准恢复生命周期管理，不能因保留时长到期丢未解决引用；容量不足拒绝新接收，不能把Unknown改Released。
- 若需要进程隔离硬恢复，由Host原worker Owner依据实际进程退出/借读隔离事实对账；本模块不提供线程强杀或把“退出等待”当worker已死。接收者不能取得原真实Owner、源重用安全性或退出证明时保留未知，阻断受影响实例资源复用；外部操作需按Host原合同恢复，不影响其它独立实例的纯计算。

**两轮定向断言（补充到原QS.H，不建立第二测试工程）**

| 轮次/原用例及补充ID | 固定反例与可判定结果 |
|---|---|
| 第一轮 QS.H04 / QS.STOP.01 | Open调用仍挂起或返回失败留资源；Stop 5秒到期/被取消返回false，原OpenAttemptId/Scope/operation仍相同。连续三次顺序Stop不增加Open/Observe/Close次数、不生成第二operation；确认Open实际Drained后只CloseOpen原Id及逆序scope。 |
| 第一轮 QS.H05 / QS.STOP.02 | native超执行deadline、Host等待token已取消：finally仍独立5秒有限Stop；native屏障未释放前Completion未结束/Released=false，后续同实例Stop不续执行期限。等待到期不修改原TimedOut/Cancelled原因。 |
| 第一轮 QS.H06 / QS.STOP.03 | scope或visual.Close挂起：Stop/RetryRelease最多一份该阶段任务；释放屏障前不能再次Close。首次Close返回失败后Repeat Stop只观察不自动重试；显式RetryRelease一次重试失败阶段，成功后原执行仍Failed/QS-ReleaseFailed。 |
| 第二轮 QS.STOP.04 | 正常结果消费抛异常、Completion等待抛错、Start结构拒绝：均执行finally；WorkFailure与关闭失败分别保留。关闭confirmed才清Operation；Close异常不覆盖消费异常、不丢原service Owner。 |
| 第二轮 QS.STOP.05 | 两个并发合法Stop、预取消token、过去deadline、非法MaxWait、Repeat Stop已Closed：最多一份观察槽；冲突QS-WaitBusy，未Closed预取消/到期均false但已Stopping，非法预算不改准入；已Closed重复返回true且不调用端口。 |
| 第二轮 QS.STOP.06 | 原Host转交抛错/接收槽满/确认丢失：原Host仍保留相同operation，不能重建/销毁，接收者未取得推进权不得恢复。明确接收确认并串行授予后，新Owner持原实例且旧方不再推进；handoff本身永不发ResourcesReleased。 |

上述两轮仅走查关闭/消费/Owner反例，未重审首片数值、算法或引用研究；有限时间用Core.Tests固定TimeProvider推进，native/Close因果用已有闩锁控制，不在文档阶段运行产品测试。主控2026-10-10已内容复核接收0.5.2-prep服务关闭定向修订；这不是QualityServiceSlice-02整片六项Ready，服务仍PreparationIncomplete。WPF此前保存知识/原意图查询定向修订已被主控接收，整体控件挂接/真实UI及服务集成仍按各切片接收和运行门执行。



### 16.10 公开托管端口与构造前的有界进程根（2026-10-11）

本节补齐QualityServiceSlice-02/Core+Simulator的可构造边界，不改变附录A算法、§16.2服务工厂或已接收§16.9 Stop语义。以下新声明均位于Core的Asun.Modules.ImageQuality，不另建Host/Contracts工程。两个独立工具和§8.4 Presenter是实际消费者；它们不能引用Core.Tests的TestInputPort/TestVisualPort。原测试端口仅保留为因果故障夹具，正常空Host使用本节公开工厂。

~~~csharp
public sealed record QualityMemoryInputProfile(
    string ProfileId, string Revision, int MaxSources,
    long MaxRetainedBytes);
public sealed record QualityMemorySource(
    QualitySourceDescriptor Descriptor,
    ImmutableArray<double> Samples, ImmutableArray<bool> ValidMask);
public sealed record QualityManagedVisualProfile(
    string ProfileId, string Revision, int MaxHistogramBins,
    int MaxGroupInputs);
public static class ImageQualityMemoryInputFactory
{
    public static IQualityInputPort Create(
        QualityMemoryInputProfile profile,
        ImmutableArray<QualityMemorySource> sources,
        TimeProvider clock, QualityBudget limits);
}
public static class ImageQualityManagedVisualFactory
{
    public static IQualityVisualPort Create(
        QualityManagedVisualProfile profile,
        TimeProvider clock, QualityBudget limits);
}
public sealed record QualityHostRootLimits(
    int MaxSlots, long MaxRetainedManagedBytes);
public enum QualityHostWorkState
{
    Reserved = 1, Constructing = 2, Ready = 3, Running = 4,
    ResultAvailable = 5, Rejected = 6, ConstructionFailed = 7
}
public enum QualityHostCleanupState
{
    NotRequested = 1, Observing = 2, Unconfirmed = 3, Released = 4
}
public sealed record QualityHostSnapshot(
    Guid SlotId, QualityHostWorkState Work,
    QualityHostCleanupState Cleanup,
    Guid? RequestId, QualityIssue? WorkIssue,
    QualityIssue? CleanupIssue, bool CanForget);
public sealed class QualityHostLifetimeRoot
{
    public QualityHostLifetimeRoot(TimeProvider clock, QualityHostRootLimits limits);
    public QualityHostSlot Reserve(Guid slotId, long reservedManagedBytes);
    public QualityHostSlot Get(Guid slotId);
    public bool TryForget(Guid slotId);
}
public sealed class QualityHostSlot
{
    public Guid SlotId { get; }
    public TimeProvider Clock { get; }
    public Task<IImageQualityService>? OriginalConstruction { get; }
    public IImageQualityService? Service { get; }
    public IQualityOperation? Operation { get; }
    public Task<QualityOperationResult>? OriginalCompletion { get; }
    public Task<QualityCloseResult>? ActiveCloseObservation { get; }
    public Task<IImageQualityService> ConstructAsync(
        Func<IQualityInputPort> inputFactory,
        Func<IQualityVisualPort> visualFactory,
        QualityBudget instanceLimits);
    public QualityStartResult Start(
        QualityServiceRequest request, CancellationToken executionToken);
    public void RequestCancel(Guid requestId);
    public void RecordConsumerFailure(QualityIssue issue);
    public Task<QualityCloseResult> CloseAsync(
        QualityStopWaitBudget waitBudget, CancellationToken waitToken);
    public Task<QualityCloseResult> RecoverAsync(
        QualityStopWaitBudget waitBudget, CancellationToken waitToken);
    public QualityHostSnapshot GetSnapshot();
}
~~~

这是待实现的完整公开规格，声明不是已编译代码。QualityHostSlot只能由root内部构造，无公共构造入口；已发布service factory签名不变。root由进程Program/应用生命周期Owner创建并强持，非模块静态单例、非窗口DataContext；必须先Reserve再调用任何端口/服务构造。SlotId非空且根内唯一，MaxSlots为1..64，MaxRetainedManagedBytes/reservedManagedBytes≥8192byte、checked总预留不超根限（每槽4096byte控制/任务元数据已包含在预留内）；重复Id或容量不足同步抛InvalidOperationException，参数错ArgumentException，不调用factory。每槽预留覆盖请求、来源快照、端口、报告、构造委托捕获与有限诊断；instanceLimits.ManagedBytes≤该槽预留。槽只接纳一次构造、一个串行service，未解决时不能用新槽绕过同消费者关闭；根级总额度与service额度两层都生效。Get未知Id抛KeyNotFoundException；TryForget未知Id返回false，不把它当释放证明。

**构造、原Task与两个状态轴**
1. ConstructAsync先把两factory、limits与原构造Task登记到已存在的槽，再启动一个后台构造工作项。先inputFactory，返回后立即强持input，再visualFactory并立即强持visual，最后唯一ImageQualityServiceFactory.Create(input,visual,root的clock,limits)。每一步只调用一次；OriginalConstruction永远是同一Task，调用方WaitAsync超时不重启它。重复ConstructAsync返回同一Task，传入不同委托/limits拒绝，不换端口。委托必须是显式公开factory调用，本节双Host给出全部参数；不依赖隐藏builder、service locator、窗口初始化或外部已构造service。
2. 本节两个公开托管factory只校验/复制不可变托管值，无文件/网络/native/后台IO；ImageQualityServiceFactory.Create也只校验/初始化有界托管状态，不Open/Observe或启动native。factory失败须不留下未返回的执行/资源，已返回托管port由槽保留至构造工作实际结束再清。无native、原Task已结束且无借读时，Cleanup=Released；不制造DrainUnknown或等待不存在的线程。构造Task实际未结束则保持Constructing/Unconfirmed，观察超时不清委托/部分端口。注入会有副作用的第三方factory必须先由其原Owner登记构造尝试及真实Task/失败资源查询；不符合此构造合同不能作为本节端口。真实AsunImage构造资格仍属AsunImageSlice-02A，不阻托管服务。
3. 服务已创建但Start未调用时，CloseAsync仍调用原service的有限Stop，确认它确无operation/资源才能Released。Close在构造中发生时登记关闭意图，禁止后续Start；在waitBudget内观察原构造Task，迟到构造成功后同槽仅一次启动原service.StopAsync；观察过期仍由原槽持有该构造Task及关闭意图，不能把新factory用于恢复。构造失败的业务问题和清理结果分别记录。
4. Start同步在槽短锁检查Ready或上一请求已结束的ResultAvailable/Rejected且实例未关闭；上一原operation必须ResourcesReleased、原Completion完成，才可在同开放service中接纳下一个显式请求。之后调用原service.Start；立刻保留返回Operation及原Operation.Completion，然后才返回QualityStartResult。拒绝保存Issue/Work=Rejected，不伪造operation/Task。接纳后Work=Running；原Completion实际结束才ResultAvailable，其原State可能Failed/Cancelled/TimedOut。消费失败用RecordConsumerFailure记录宿主诊断，不改变QualityOperationResult/报告。此方法只保存有界Code/FieldPath/MessageKey（≤128字符）；已有构造/执行WorkIssue优先，消费问题只作一份附加诊断，不覆盖原错误。不会另存Exception对象图；BCL原Task自身的失败对象只随该原Task保留至真实结束/可忘，不能为减少诊断丢在用Task。
5. Work和Cleanup独立：结果可算但Close失败不能消费为成功；消费抛错但资源已释放仍记录WorkIssue，Cleanup=Released不覆盖它。观察超时只Cleanup=Unconfirmed；原Completion/构造Task没有结束仍强持。GetSnapshot只读，不调用端口，不回调UI。没有新模块执行终态；QH-ConstructionFailed/ConsumerFailed/ObservationExpired/CapacityExceeded是Host投影诊断，MessageKey=ImageQuality.Host.<后缀>，不写入operation.Causes或质量事实。
6. CloseAsync冻结§16.9预算，登记关闭意图/原观察Task后调用同一service.StopAsync；并发观察以QS-WaitBusy立即返回，最多一份活动观察，不延长原执行deadline。构造仍在途也只一份观察槽，剩余预算不得在构造完成后重置。正常返回、异常、取消都在finally归还本次注册/槽；原Task/端口/operation仍按实际状态保留。未预期异常结构化为QS-ProviderFailure并记CleanupIssue，不覆盖WorkIssue。
7. RecoverAsync只在该槽无活动观察时，显式调度原operation.RetryRelease一次，再用CloseAsync有限观察；没有operation时只处理原构造/关闭意图，不Start新请求。正在释放的原任务不重叠，首次释放失败后的最终Failed保持。迟到结果只完成原Task/更新原槽，不调用旧消费委托或已卸载Dispatcher；主动恢复调用取原GetSnapshot/Get，再自行核原RequestId。
8. TryForget只在无构造/工作/关闭任务在用、原service已确认Released、无其它借读/端口资源且CanForget=true时清本槽引用并归还根预留。它不调用Close、不靠TTL/GC/窗口关闭判断释放。不受影响槽独立工作；每槽只留当前实例/原结果和一份有界诊断，不累积每次观察Task/异常/完成历史；构造实际结束后清factory委托及只用于构造的捕获值，避免在OriginalConstruction之外暗留源副本。根Owner退出前逐槽有限Close，未解决时按§16.9同对象确认移交；无人确认接管就保留进程根并拒绝正常卸载，不能只让局部变量离栈。
9. original构造/Completion/阶段工作与观察Task分开；槽不能把WaitAsync包装Task当原任务。根表持原Task直到实际结束。测试进程外层强制终止只属验证失败/退出事实，不能在生产中当共享借读资源已释放；需要硬恢复由原隔离进程Owner证明实际退出与源安全性。

**托管输入port的确定实现**
- profile的Id/Revision非空≤128字符，MaxSources正，MaxRetainedBytes正且≤limits.ManagedBytes；sources非Default/非空、数量≤MaxSources、SourceRef唯一。Descriptor和每个像素/mask完整性按§16.3/16.6验证，Samples和mask均恰等Width×Height，checked总保留为每源1024+2×全部字符串长度+8N+N+2×64字节。profile不含物理阈值；超限在复制前拒绝。Create构造独立ImmutableArray副本，不保留调用方可写别名。Root在这之前已预留两份源快照同时存活的构造峰值。
- Open只借入匹配SourceId/Revision不可变快照，按OpenAttemptId保留一个scope；不取最新源。scope.RetainedManagedBytes报该源全部容量，native=0；有效期限为源所属limits和本次budget更早者。当前槽scope未Close前不能再Open同源生成第二借读；方法复用同scope。CheckCurrent固定Current（纯值不会断连）；已Close再读返回QS-InvalidSource。CheckDrain在没有正在执行ReadBlock时立即Drained，不能为纯托管值编native未知。
- ReadBlock按半开bounds逐行复制原位置及mask，计8×面积+1×面积+两数组128，先核remaining预算/clock/取消；不修改源、缩小框或压缩有效点。同步读取实际返回后无后台任务；Close在线程安全下归还本方scope借读标记，重复同scope Released=true。CloseOpen只归还Open尝试本身，不能擅自关另一个scope；成功Open后CheckOpen=Drained，CloseOpen为无残留幂等true。port只保留当前尝试/最近一份关闭墓碑，无无限表。

**托管visual的确定实现**
- profile的Id非空≤128字符、Revision非空≤32字符，MaxHistogramBins/MaxGroupInputs正合法；clock、limits与根一致。Core包版本标识≤32字符，组合RuntimeRevision总长≤128。RuntimeRevision固定image-quality-managed-port-v0.1/<Core包版本>/<profile.Revision>，所有方法同identity；不得称HALCON backend。该port定位Core/Simulator的无依赖契约消费者，非HALCON成像路线的生产替代；Group只核上游validmask/组来源事实及计数，不产生相位/检测资格。它只执行RawStatistics与StructuredGroupSupport：Raw严格按§20.6第2步调用已接收A evaluator；Group严格按§16.8/§20.5共同mask及组证据校验，逐位置读取各已有角色，不计算相位。MaxHistogramBins/MaxGroupInputs为构造准入限，超过请求拒绝而非截断。
- 其它路线返回该指标Unsupported/BackendRouteUnsupported且Values/RawValues/Tiles为空，保留正确Support/原请求；不伪造Sobel/Noise成功，不引入平行视觉算法。原因三语“当前后端不支持此方法/目前後端不支援此方法/Method unavailable on this backend”。实际HALCON工厂在§24.3，原算法研究不变。
- Observe的invocationId在调用前登记，所有同步读取/计算实际结束后返回Drained=true。纯值临时量在finally归还，无native句柄；ResourcesReleased=true表示本方临时量已归还，service仍按原scope顺序收尾。异常同finally后CheckDrain=Drained；若测试故障装饰器确有原后台工作，则由其真实Task决定Pending/Unknown，不用本纯值port的即时Drained掩盖它。预算/读取次数含所有块及共同mask，每次调用取父剩余；Close(invocationId)幂等，只清该方法本方阶段，不关闭输入scope。


### 16.11 两个空无UI Host的完整输入与调用（2026-10-11）

下面是未来Core.Tests中QualityEmptyHostExamples的完整C#示例源码规格，引用Core和.NET BCL（System、Collections.Immutable、Linq、Threading、Tasks），不是已编译/运行结果。两个入口使用不同Source/方法/Profile；同一示例文件只为重复数值构造声明一个可见Fixture方法，全部方法体在本节，没有未声明request/ports/builder。正式两个工具可各自复制本工具调用部分而仅引用发布Core，不引用另一工具。它们的进程生命周期Owner必须保有root直到最后未解决槽真实释放或确认移交；RunAsync返回SlotId不是释放许可。

~~~csharp
internal sealed record QualityHostFixture(
    QualityMemoryInputProfile InputProfile,
    QualityManagedVisualProfile VisualProfile,
    ImmutableArray<QualityMemorySource> Sources,
    QualityBudget InstanceLimits, QualityServiceRequest Request);

internal static class QualityEmptyHostExamples
{
    public static Task<Guid> RunOcrAsync(
        QualityHostLifetimeRoot root, TimeProvider clock,
        CancellationToken token) => RunAsync(root, clock, false, token);

    public static Task<Guid> RunGroupAsync(
        QualityHostLifetimeRoot root, TimeProvider clock,
        CancellationToken token) => RunAsync(root, clock, true, token);

    private static async Task<Guid> RunAsync(
        QualityHostLifetimeRoot root, TimeProvider clock,
        bool group, CancellationToken token)
    {
        var slotId = Guid.NewGuid();
        var slot = root.Reserve(slotId, 64L * 1024 * 1024); // 构造前登记
        try
        {
            var f = Fixture(clock, group);
            var service = await slot.ConstructAsync(
                () => ImageQualityMemoryInputFactory.Create(
                    f.InputProfile, f.Sources, clock, f.InstanceLimits),
                () => ImageQualityManagedVisualFactory.Create(
                    f.VisualProfile, clock, f.InstanceLimits),
                f.InstanceLimits).WaitAsync(
                    TimeSpan.FromSeconds(5), clock, token).ConfigureAwait(false);
            var validation = service.Validate(f.Request);
            if (!validation.IsValid)
                throw new InvalidOperationException("Fixture rejected.");
            var start = slot.Start(f.Request, token);
            if (start.Operation is null || start.Issue is not null)
                throw new InvalidOperationException("Start rejected.");
            var original = slot.OriginalCompletion
                ?? throw new InvalidOperationException("Original task missing.");
            if (!ReferenceEquals(original, start.Operation.Completion))
                throw new InvalidOperationException("Task identity changed.");
            var result = await original.WaitAsync(
                TimeSpan.FromSeconds(5), clock, token).ConfigureAwait(false);
            if (result.State != QualityOperationState.Completed ||
                result.Report is null || result.Issue is not null)
                throw new InvalidOperationException("Unexpected execution state.");
            if (!group)
            {
                var raw = result.Report.Observations.Single();
                var sat = (ManagedSaturationValue)raw.RawValues.Single(
                    x => x.Kind == ManagedQualityMetricKind.SaturationCount).Value!;
                var contrast = (ManagedContrastValue)raw.RawValues.Single(
                    x => x.Kind == ManagedQualityMetricKind.Contrast).Value!;
                var histogram = (ManagedHistogramValue)raw.RawValues.Single(
                    x => x.Kind == ManagedQualityMetricKind.HistogramRange).Value!;
                if (sat.LowCount != 1 || sat.HighCount != 1 ||
                    sat.LowFraction != 0.25 || sat.HighFraction != 0.25 ||
                    contrast.Value != 254 ||
                    !histogram.Counts.SequenceEqual(new long[] { 1, 1, 0, 2 }))
                    throw new InvalidOperationException("Raw metric mismatch.");
            }
            else
            {
                var support = result.Report.Observations.Single(
                    x => x.MethodKey == "group-support");
                if (support.State != QualityMetricState.Computed ||
                    support.Support.RequestedPixels != 4 ||
                    support.Support.ValidPixels != 3 ||
                    support.Values.Single(x => x.Key == "commonValidFraction").Value != 0.75 ||
                    support.Values.Single(x => x.Key == "presentSteps").Value != 3)
                    throw new InvalidOperationException("Group support mismatch.");
            }
        }
        catch (Exception)
        {
            // 只留有界宿主诊断；不把异常字符串写进质量结果/操作员文案。
            slot.RecordConsumerFailure(new QualityIssue(
                "QH-ConsumerFailed", "consumer",
                "ImageQuality.Host.ConsumerFailed"));
        }
        finally
        {
            await slot.CloseAsync(
                new QualityStopWaitBudget(TimeSpan.FromSeconds(5),
                    clock.GetUtcNow().AddSeconds(5)),
                CancellationToken.None).ConfigureAwait(false);
        }
        return slotId; // root仍持原Task/端口/operation；调用者核两轴
    }

    internal static QualityHostFixture Fixture(TimeProvider clock, bool group)
    {
        var now = clock.GetUtcNow();
        var instance = new QualityBudget(
            32L * 1024 * 1024, 1024 * 1024, 1000000,
            4L * 1024 * 1024, TimeSpan.FromSeconds(30), now.AddSeconds(60));
        var budget = new QualityBudget(
            16L * 1024 * 1024, 1024 * 1024, 100000,
            2L * 1024 * 1024, TimeSpan.FromSeconds(20), now.AddSeconds(20));
        var policy = new QualityObservablePolicy(1, 0, null, null, null);
        var rawMethods = new ManagedQualityMethodSet(
            group
                ? ImmutableArray.Create<ManagedQualityMethod>(
                    new ManagedSaturationMethod("r1", 0, 255),
                    new ManagedCoverageMethod("r1"))
                : ImmutableArray.Create<ManagedQualityMethod>(
                    new ManagedSaturationMethod("r1", 0, 255),
                    new ManagedContrastMethod("r1",
                        ManagedContrastStatistic.NearestRankQuantileRange, 0.25, 0.75)),
            group
                ? ImmutableArray<ManagedQualityMethod>.Empty
                : ImmutableArray.Create<ManagedQualityMethod>(
                    new ManagedCoverageMethod("r1"),
                    new ManagedHistogramRangeMethod("r1", 0, 255, 4)));
        var sources = ImmutableArray.CreateBuilder<QualityMemorySource>();
        var inputs = ImmutableArray.CreateBuilder<QualityInput>();
        var methods = ImmutableArray.CreateBuilder<QualityMethodPlan>();
        var count = group ? 3 : 1;
        for (var i = 0; i < count; i++)
        {
            var role = group ? "step-" + i : "gray";
            var source = new QualitySourceRef(
                group ? "group-source-" + i : "ocr-source", "rev-1");
            var descriptor = new QualitySourceDescriptor(
                source, QualitySourceKind.RawAcquisition, role,
                QualityPixelType.UInt8, 4, 1, "pixel-r1", null,
                group ? "group-r1" : null, group ? i : null,
                group ? "exposure-r1" : null, group ? "motion-r1" : null,
                group ? "projection-r1" : null, null,
                now, null, 8, null, null);
            var pixels = group
                ? ImmutableArray.Create<double>(
                    10 + 10 * i, 20 + 10 * i, 30 + 10 * i, 40 + 10 * i)
                : ImmutableArray.Create<double>(0, 100, 254, 255);
            var mask = group && i == 1
                ? ImmutableArray.Create(true, true, true, false)
                : ImmutableArray.Create(true, true, true, true);
            sources.Add(new QualityMemorySource(descriptor, pixels, mask));
            inputs.Add(new QualityInput(role, source));
            methods.Add(new QualityMethodPlan(
                "raw-" + role, "r1", "roi", role, QualityRoute.RawStatistics,
                new QualityRawParameters(rawMethods), policy, true));
        }
        if (group)
            methods.Add(new QualityMethodPlan(
                "group-support", "r1", "roi", "step-0",
                QualityRoute.StructuredGroupSupport,
                new QualityGroupParameters(
                    ImmutableArray.Create("step-0", "step-1", "step-2"),
                    ImmutableArray.Create(0, 1, 2)),
                new QualityObservablePolicy(1, 0.75, null, null, null), true));
        var request = new QualityServiceRequest(
            Guid.NewGuid(), "image-quality-service-v0.1",
            inputs.ToImmutable(),
            ImmutableArray.Create(new QualityRegionSpec(
                "roi", new QualityBox(0, 0, 1, 4))),
            methods.ToImmutable(), budget, 2, 1);
        return new QualityHostFixture(
            new QualityMemoryInputProfile(
                group ? "group-memory" : "ocr-memory", "r1", count, 1024 * 1024),
            new QualityManagedVisualProfile(
                group ? "group-managed" : "ocr-managed", "r1", 256, 3),
            sources.ToImmutable(), instance, request);
    }
}
~~~

测试入口Program在第一次调用前创建clock=TimeProvider.System和root=new QualityHostLifetimeRoot(clock,new QualityHostRootLimits(2,128L*1024*1024))，依次调用RunOcrAsync、RunGroupAsync，各得SlotId；不能让第一次异常阻止第二槽已登记任务的收尾。逐槽GetSnapshot必须WorkIssue=null、Cleanup=Released、CanForget=true，原结果state及上述数值一致后才TryForget；否则契约测试退出非0，root仍保留待恢复槽直到测试控制的真实任务结束。将两个入口分别用--host ocr与--host group启动为两个独立子进程，是第二消费者验收；每进程root为MaxSlots=1/64MiB，主测试进程使用§24.2有限命令。普通应用Owner遇到未确认槽进入“恢复未完成”的存活状态，不能照搬测试失败退出作为生产清理。

固定Profile给出的MiB、20/30/60秒、块2×1、直方图4bin均为有限软件夹具参数，不是客户节拍/生产阈值。OCR宿主这里只消费原像素诊断，不执行OCR；Group宿主这里只检查步组共同支持，不解相位或宣称重建可用。Required缺项/完整结果由各工具任务策略解释，无质量PASS。数据变化须新SourceRevision/完整新fixture，不用相同像素假造曝光身份。

**可控异常与恢复装饰器（仅原Core.Tests，不发布第二模拟包）**

原QualityServiceHostContractTests的端口装饰器仍完整实现§16.2：构造时从公开memory/managed port取得inner，并按下面一份不可变fault profile和控制闩锁分支；不是未声明“测试设备”。每个闩锁由该测试case的Owner保留、每阶段只一份原Task，case finally释放所有本方屏障并等待实际结束，单个观察5秒/总90秒。测试闩锁证明协调因果，绝非真实native排空证据。

| 注入点与明确行为 | 真实状态/恢复断言 |
|---|---|
| 构造闩锁 | inputFactory先等待case拥有的闩锁，再显式调用公开memory factory；root必须先有槽/OriginalConstruction，5秒观察退出后仍同Task，Close意图先登记，闩锁释放后不Start而仅Stop，双轴Construction完成/Released。 |
| Open异常 | 装饰器收到服务提供的OpenAttemptId后先登记；仅本case下抛异常并保有本case资源标记。CheckOpen在屏障前Pending、屏幕后Drained，CloseOpen只清原Id标记，成功次数1，不能Close未知attempt。普通memory port不造这种标记。 |
| Observe原任务 | 装饰器按invocationId登记屏障任务并在原调用内等待；屏障前CheckDrain=Pending，退出后才委托inner.Observe并记录Drained。执行token/期限失效只封口，不能把屏障任务取消成已结束；迟到结果丢发布、原scope最后才Close。 |
| 首次Close失败 | 已Drained后装饰器第一次Close返回false/QS-ReleaseFailed，保留原标记；第二次只由显式RetryRelease委托inner.Close。重复Stop不调用第二Close；最终原操作Failed，资源true，根可忘但WorkIssue/原Failed不变。 |
| Close挂起 | 服务已登记原释放工作后装饰器Close等待Owner屏障；Stop/Recover观察到期仍只一份原Close任务；屏障结束后Close成功，不并发再次进入。 |
| 来源Changed/结果畸形 | 输入CheckCurrent装饰一次返回Changed，或visual返回少键/NaN/错Support；Failed且无报告，最后真实归还；不能用Optional吞故障。无原生工作的畸形托管结果在同步返回后立即Drained，不另造排空。 |
| 消费/观察异常 | 在上述完整RunAsync中让消费断言抛错或token预取消；finally使用独立budget。WorkIssue和CleanupIssue独立，原Task仍由槽持有，恢复后不会重新消费迟到报告。 |

## 17. 参数建议与方法资格（无自动生产改参）

建议由工程宿主按本指导的有限实验计划生成，调用§16同一Start执行；不添加训练器、自动曝光搜索或第二套质量算法。候选只来自明确的强类型方法集合，最大数、源样本数量、总预算、最早期限由实验Profile给出；枚举次序冻结并串行，每组参数用新RequestId。Sobel候选限sum_abs/size3与显式sum_abs_binomial/5,7,9；LoG与Gaussian路线候选Sigma限[0.5,1,2,3]与所选路线实际范围交集；Noise限显式foerstner/immerkaer/least_squares/mean与Percent[10,20,40]（前两种只取一个Percent避免重复实验）。这些是工程候选网格，不是生产推荐值；超出网格须新实验修订，不在线按结果扩大搜索。

1. 输入固定原图/ROI/支持修订、传感器码范围、镜头/曝光/材料标签、受控同物离焦序列或噪声真值；任务成功/误接受标签由消费者给出，质量模块不造标签。缺真实任务标签只生成数值对照，Suggestion=NotEvaluated，不选winner。
2. 每个候选记录完整参数/实际route/runtime、N/coverage/缺项、每样本原响应、端到端费用/峰值；不能把不同尺度绝对高分横向当最好。焦点评估看同物受控离焦排序，已知噪声看sigma偏差，曝光按计数闭合；任一源变更或取消使整次建议过期。
3. 筛掉消费者Profile误接受/误拒绝、拒识覆盖、数值误差、支持、时延/资源硬门未满足的候选；目标缺失保留NotEvaluated。合格候选按“误接受升序→误拒绝升序→不可观测率升序→完整端到端P95升序→峰值升序→声明索引升序”排序。同样本/独立留出集各记录，失败/超时样本不删除。没有实测不能说最快。
4. 建议只由宿主保留原候选参数及所有依据，不改变生产Profile。人工选择/留出验证/批准后冻结为新的方法Revision；SourceRevision/ROI/mask、光学、runtime、材料或候选集合改变则原建议Stale。不自动调整饱和阈值使更多图通过，不自动删除反光/难ROI；曝光/光源物理优化仍归imaging-optimization。

### 17.1 有限实验的调用、分母与停止

这是工程宿主操作规约，不新增模块API或Experiment DTO。开始前冻结候选序、样本序、全部输入/支持/方法/任务政策修订、搜索集与独立留出集、实例和实验总预算。先用同一service.Validate逐候选校验完整请求；合法候选按声明索引、样本索引串行Start，每次使用新RequestId，包含更早声明的Raw可观测依赖，不仅提交待比较的滤波参数。前一Completion与ResourcesReleased未确认前不提交下一请求。父实验截止和剩余资源只能收窄子QualityBudget；母预算未设、目标缺失或总实验容量不足不开始建议，不能给每个候选重置完整父预算。Noise前两方法的候选Percent固定20，与§20.5相同；binomial为完整矩形域候选，输入域不支持时记录Unsupported，不用补洞或换ROI适配网格。

父预算按量的生命周期记账：读取像素/提交次数是实验累计量，已耗时间不返还；工作内存按当前同时存活量/峰值，前轮真实释放后可归还，不能逐轮累加峰值假称内存已耗尽。保留的输入、报告/实验记录和原未释放Task/root持续计入父容量；子请求只获扣除此常驻量后的剩余额度，累计读取余额与更早期限同样收窄。Validate失败的候选保留原原因和全部未提交组合，不能悄悄从计划删除或取得资格。§16请求六项预算及账本保持，不新增另一资源权威。

实验记录使用宿主已有保存能力，至少保留完整候选/样本序、预先声明的全部计划组合、原QualityOperationResult或尚未结束的原operation/root槽、每指标支持与原因、实测端到端耗时/峰值和排序依据。没有执行的计划组合也保留“未提交/原因”；不生成虚构报告。标签、任务解释阈值和成功判据由消费者先冻结：正例=应允许进入下游任务，负例=应拒绝；每个候选分别以同一冻结样本计划计算，搜索集和留出集不混合分母。误接受率=负例中被任务政策接受数/全部负例数，误拒绝率=正例中被明确拒绝数/全部正例数，不可观测率=无可用任务结论的计划样本数/全部计划样本数。失败、超时、未提交、缺必需量归不可观测，不能当正确拒绝；三类分别保留，正/负分母不因失败减少。任一所需分母0、标签/任务政策/精度容差/资源目标缺失，评价为NotEvaluated，不选择winner。

搜索集按§17顺序筛选排序；任何失败/超时/未提交使候选不能取得方法资格，即使消费者容许部分物理拒识。对剩余候选的拒识覆盖、误差、受控离焦排序、时延/峰值硬门使用消费者冻结值，全部可判定才比较；精确相同排序向量按声明索引选一个。只有完整成功请求构成数值误差/焦点排序样本，缺数值不填0；耗时/不可观测和全部分母仍保留。对选中的一个候选执行一次独立留出验证，留出失败拒绝本次建议，不能试遍其他候选直到留出通过或利用留出重调阈值；须新实验修订/新留出证据。解释展示选中参数、完整排序向量、淘汰门及相关原报告，不能把绝对梯度最高叫最佳。

到候选/样本上限、总期限、取消或任何Draining/DrainUnknown/ResourcesRetained时停止新增提交。若当前原任务仍在用，只按§16原operation.RequestCancel和有界root.CloseAsync观察，保留原Task/Owner；反复观察不等于重算。未执行组合保持在原计划分母，整次建议无资格；不得创建替代service跨过未知资源。冻结新Revision须经原保存Owner/当前权限，关联选中候选与完整搜索/留出证据；草稿保存不是生产批准。输入、光学、Profile、方法或runtime变更均使建议Stale，旧记录只读，不自动再Start。

<a id="image-quality-implementation"></a>
## 18. 按任务评价，保留原量与适用域

本模块指导 §18–24 是质量指标的唯一实施细节；[DEV-VIS-021C](../../shared-modules/guidance/03-vision/DEV-VIS-021C_图像通道与预处理独立能力开发指导.md)只维护014派生处理图。012负责采集关联，宿主/038把006原帧、实际成像条件和方法质量需求传给013；013不依赖采集实现、不控制曝光、不修改原帧。OCR/读码与3D条纹重建是两个独立消费者，同一帧对一个任务可用、对另一个任务不可用。

输入需有精确帧/plane/来源角色、像素类型及实际有效位深/黑白参考、ROI与原有效mask、像素/物理尺度、处理来源、曝光/光源/姿态引用、质量方法/参数/适用任务和资源期限。实际设置未知可输出已知指标及缺项，但依赖该事实的任务不能被标合格。静态2D的Motion不适用必须由调用合同明确，不填虚构MotionActual。

后续文件输入映射须保留原文件/像素来源与导入时间；导入时间不是曝光或采集时间，不向采集条件填入假值。单文件不能自证运动、投影步序/时序或颜色标定；缺这些事实只使依赖它们的指标不可观测，不阻断原像素可支持的灰度统计。必需指标仍保留请求与缺失原因，不能删除它们换取完整状态，文件报告不因数值可算而获得生产资格。具体文件入口与来源契约仍须单独采纳，不进入首片 API。

报告逐指标给出方法/版本/尺度、数值/单位/归一化、有效域/样本数、原证据及有效性/原因。能计算、可观测、满足本方法质量要求与产品合格四层分别表达。缺值用明确缺失原因，不填0/NaN占位；算法失败不能用另一指标最高分遮住。任务所需指标缺失则适用性未满足，未配置的非必需指标可以显式不适用，不强迫所有任务做所有质检。正式标识与枚举回原C候选采纳，以下公式不是新增Schema。

## 19. 域、直方图与曝光计数

1. 通过006核plane/stride/payload、有限值及范围。请求ROI越界/来源矛盾为非法输入，不静默裁成小ROI；已知缺测由valid mask表达。有效统计域S=请求ROI∩原图可读域∩有效mask，保留原ROI面积A及N=|S|；N=0无统计数值，N/A与读取失败分开。
2. 原始采集指标使用原辐射值；增强/LUT/逐图min-max后指标另标派生。颜色分量、不同光型、多曝光及深度通道分开，不能从屏幕亮度反推实际曝光。
3. HALCON `intensity`、`gray_histo`、`gray_histo_abs`、`gray_histo_range`均按显式Region计算并忽略图像已有domain，故必须传S；仅ReduceDomain不保证孔洞/无效像素被排除。空输入按适配合同处理，不临时修改全局设置。
4. `gray_histo`输出256 bins，对real/int2/uint2/int4先按本图范围线性映射，不能把末bin直接解释为12/16位sensor饱和。`gray_histo_abs`支持byte/cyclic/direction/int1/int2/uint2，不支持int4/int8/real；高位深uint2/int2可按批准Quantization保留原灰度区间。逐灰度完整计数需q=1；仅做区间分类时可采用与阈值严格对齐的量化，不能把跨阈值一bin随意分给两类。int4/int8/real或固定范围图优先评估`gray_histo_range`，冻结范围/bin边界，并单列范围外/非有限值。官方规定非real的Min/Max向下取整，落在两bin边界的值归较小bin；real且Min=Max时相等值只进首bin。适配按目标API与边界样例核对，不用UI图表默认的左闭右开规则代替，也不把range外省略成N。
5. 固定直方图与显示用自适应直方图必须区分。histogram计数总和等于其声明统计域的有效数，范围内/外与无效数闭合；相对频率用同一N，零分母不算100%。所有计数/字节预估checked；不生成多份全图像素副本来计算各个标量。

后续消费者域解释另区分请求域 R、原可读有效域 V、消费者显式批准的检查排除域 X，以及二值前景、派生 clipping 和显示补值。原始采集质量仍使用 S=R∩V；若方法明确要求排除检查域，其统计域另记 D=(R∩V)\X，不能静默覆盖原 S 或原有效覆盖率。分别报告 |R|、|R∩V|、|R∩V∩X|、|D|，重叠按集合只计一次，满足 |R∩V|=|R∩V∩X|+|D|；以 D 为分母的指标显式标注，零分母保留缺项。前景过滤的 Kept/Excluded/Added 只说明候选变化，不自动生成 X 或改写 V；零前景既不证明输入无效，也不证明无缺陷。派生 clipping 按已批准处理规则影响该派生图的有效域，不反写原帧 V；显示补值不能恢复观测支持。X 的批准与变更归消费者，本模块不授予排除/免检权限。此处是后续解释与验收要求，不追加首片 mask 种类或产品字段。

曝光分区候选固定Lc≤Ld<Hb≤Hc：低端截断g≤Lc，偏暗Lc<g≤Ld，可用Ld<g<Hb，偏亮Hb≤g<Hc，高端截断g≥Hc，五类互斥且总数=N。合并“偏暗含截断”“偏亮含截断”只是显示派生，不能与五类再相加。阈值来自任务/传感器及批准方法，不把byte上限、容器16位上限或百分比亮度当sensor白电平。

HighClipped/N是有效像素内的高端截断比例，N/A是观测有效比例；两者不能互换。原有效值[0,100,100,255]、ROI有8个位置而仅4有效时，高端阈值255得到1/4，valid fraction=4/8；不写1/8来掩盖有效区饱和。µ=Σg·h(g)/N；总体灰度离散σ=√(Σh(g)(g−µ)²/N)，此处h(g)为原灰度的精确频数，不是量化bin中心的代用品；浮点/量化图应由原有效值计算矩，若用近似必须另标方法/误差，不能标同一个原量。跨帧重复拍摄样本标准差用N−1，与上述总体灰度离散不同。采用HALCON Intensity输出时须保留其官方语义并以原灰度计数样例对照，不因同叫Deviation混用。N=1即使库返回0也不证明图像有足够纹理。

## 20. 清晰度、噪声、对比与运动模糊

### 20.1 每个邻域指标都保留二维支撑

滤波支撑域包含所有参与邻域像素；不能把mask有效像素挤成一条连续数组后做Sobel/LoG/局部方差。按§20.5固定支撑Model：ValidNeighborhood只在完整有效窗口中心汇总，跨tile需真实halo；OperatorRectangleBoundary明确使用完整矩形的算子边界约定，不能冒充独立真实halo支持。官方提示reduced domain滤波可能产生意外结果，图像边缘镜像/补零不自动是有效观测。某后端仅支持完整矩形时应返回受支持域及缺口，不能把整份带洞ROI偷偷视为全有效。

### 20.2 清晰度及可观测性

HALCON Sobel主路线与实值Gaussian/LoG独立候选按§20.5执行，方法同时固定滤波族/参数、像素或物理尺度、聚合域、响应类型与归一化。可定义平均绝对响应Σ|r|/N或平均平方响应Σr²/N，但两者单位和阈值不同，不共用“BlurScore”。Sobel x/y的byte输入输出可为有符号int1，必须先扩大类型再取绝对值；把-128仍放sbyte取绝对值会溢出。尺寸>3的Sobel包含平滑且幅值有额外倍率，不能跨size直接比原分数；CPU/OpenCL结果可能不同，固定后端并核最终判定。

纹理、曝光及有效支撑不足返回不可观测。均匀金属区低梯度不证明失焦；噪声会增加梯度/LoG，高分不证明字符或细桥可检。方法选择使用固定同物件的受控焦距/离焦序列与下游定位/OCR/重建成功性，覆盖方向纹理、反光、弱对比、小缺陷与材料变化，不能按当天图像临时选最高分候选。

### 20.3 噪声与局部灰度离散不能混称

`estimate_noise`输出加性噪声标准差；foerstner/immerkaer有Gaussian假设，least_squares/mean依赖足够均匀区，mean还要求大连通均匀区。foerstner和immerkaer不使用Percent调节结果。缩放造成直方图空洞时foerstner可能错误收敛0；3175表示无法可靠估计，不吞异常填0。仅按事先批准的路线扩大域或切换方法，并记录方法变化/耗时，不用普通图像标准差冒充替代噪声算法。

`deviation_image`的官方输出是局部标准差乘2，偶数窗口会变下一奇数，图像边界镜像；输出类型/量化及OpenCL精度限制须入适配。保留原响应及“2倍局部灰度标准差响应”单位；只有确认非截断、量化可接受后才按方法显式除2获得局部离散量。它含纹理/边缘，不是独立噪声估计。源AOI用sigma与localMean的相对差作为“Uncertainty”不能直接迁入：既可能量纲倍率不一致，也没有统计不确定度依据。可以在同一方法明确语义下记录候选分歧，但分歧不是计量不确定度、置信度或精度证明。

### 20.4 对比、均匀性与方向性

对比指标固定总体σ或原灰度分位距等具体定义。分位数排序规则/插值在方法冻结，例如离散最近秩q取第ceil(qN)个（0<q≤1），不能由UI图表库默认决定。局部指标按固定空间分区及原mask输出，记录每tile有效数、均值/离散、缺口和最差位置，禁止丢掉缺测tile后把余下均匀宣称全图均匀。光照均匀性须均匀参考靶或已知参考反射条件；真实PCB的材料/丝印/铜面变化不能直接归因为光源不均。

后续采用等网格时，方法修订固定分区行数 nr、列数 nc，均为正整数且分别不超过 ROI 高 H、宽 W；ROI 起点为 (r0,c0)，端点固定 r(i)=r0+floor(i×H/nr)、c(j)=c0+floor(j×W/nc)，乘法 checked，tile 为半开 [r(i),r(i+1))×[c(j),c(j+1))。按行优先索引 i×nc+j 输出，不取整后丢弃余边，也不让 UI 重排改变声明顺序；每 tile 再与原统计域相交并保留缺测原因。全局统计从同一原统计域计算，不能对有效数不同的 tile 均值作无权平均。最差 tile 采用方法冻结的具名量及方向，相同值取最小行优先索引；不可观测 tile 原位保留，已有可观测 tile 的最差值不能证明全域完整。此分区只服务后续 LocalUniformity，不扩大 `ManagedCoreSlice-01` 方法集。

方向梯度Ex/Ey及abs(Ex−Ey)/(Ex+Ey)只反映方向纹理差异。单张水平条纹本就可能一个导数方向弱，不能据此宣布运动模糊方向。运动模糊需实际曝光/位姿或可比静态参考与光学模型；缺依据只显示方向响应及未证原因。简化平面/匀速例中模糊长度b=v·t/s（v为物方速度、t曝光、s为物方mm/px）可作先验；实际需处理行时序、加减速、旋转、景深和投影，不能把该式当任意图像测量。

### 20.5 已冻结的主路线、类型与不可观测分支

所有视觉算子经ImageLibDotNet.cv2；首发固定CPU，不自动启用OpenCL或修改HALCON全局优化/线程。HALCON精确版本、CPU优化配置和适配器修订构成RuntimeRevision。未请求的路线不暗中替换；参数非法拒绝请求，合法但当前路线不支持的类型/域返回Unsupported。

| Route/参数 | 输入、具体顺序与聚合 | 支撑/失败与单位 |
|---|---|---|
| RawStatistics / QualityRawParameters | 原像素+原mask→§20.6托管快照→附录A一次Evaluate，Methods不能Default或全空；保留原ROI键与方法参数 | OriginalPixels；原始码值计数，不经显示LUT。N=0仍Coverage0，其它无值。 |
| Sobel / QualitySobelParameters | 主方法为SumAbs、Size=3、MeanAbsoluteResponse；配置必须显式传入。其它已列FilterType按枚举唯一映射为HALCON小写名（SumAbs→sum_abs等），非binomial Size∈{3,5,7,9,11,13}，binomial为5..39奇数。UInt16/Float32的非X/Y响应先转HALCON real保留码值，UInt8保留byte；响应按MeanAbsoluteResponse或MeanSquaredResponse聚合 | 非thin Size3可采用完整3×3有效中心；其余整矩形边界路线。UInt16/Float32的X/Y族Unsupported/MethodVariantUnsupported，不接受int2截断方向量。平方聚合先扩大到double；单位KernelResponse或KernelResponseSquared。 |
| GaussianGradient / GaussianLaplace / QualityGaussianParameters | Sigma有限0.01..50 pixel；原码值转real→derivate_gauss(component=gradient/laplace)→实值响应绝对均值或平方均值，由Aggregation显式决定 | full矩形、OperatorRectangleBoundary；有洞mask不填0，Unsupported/MaskUnsupported。不用未证实的ceil(3Sigma)伪造完整halo。 |
| LoG / QualityGaussianParameters | Sigma有限0.01..25 pixel；仅UInt8完整矩形→laplace_of_gauss→int2响应扩大到double后绝对/平方聚合 | 独立量化候选，OperatorRectangleBoundary；UInt16/Float32 Unsupported/PixelTypeUnsupported，应显式新请求GaussianLaplace，不能在LoG身份下换算法。 |
| Noise / QualityNoiseParameters | UInt8/UInt16完整矩形；Estimator唯一对应foerstner/immerkaer/least_squares/mean；0<Percent≤50，AssumptionRevision非空。前两种Percent固定20，只为完整调用参数，不声称它能调结果。后两种使用显式Percent | 一次全域estimate_noise，不平均各tile sigma；3175→NotObservable/NoiseNotEstimable；有限sigma≥0。Gaussian/均匀假设必须来自冻结方法资格，不能仅凭字符串自证。Float32 Unsupported。 |
| LocalDeviation / QualityDeviationParameters | Width/Height各≥3奇数，且不超过ROI相应边长；转real→deviation_image→完整有效窗口中心上的响应均值 | ValidNeighborhood，2倍局部标准差响应twiceLocalStdMean/KernelResponse；不除2、不称Noise。窗口超过511时直接请求Unsupported/MethodVariantUnsupported（本模块有界侵蚀实现范围）。 |
| Uniformity / QualityUniformityParameters | Rows/Columns正且不超过ROI高/宽；按§20.4等网格，逐块原域intensity计算mean/总体σ，全域亦按原域计算 | OriginalPixels；worstAbsMeanOffset=max abs(tileMean−globalMean)，并列最小行优先index。块按同Policy的样本/覆盖判定；有缺块时全局Values为空而保留全部Tiles。 |
| DirectionResponse / QualityDirectionParameters | Sigma有限0.01..50 pixel；原码值转real→derivate_gauss的x/y→xAbs=mean(abs(dx))、yAbs=mean(abs(dy))→abs(xAbs−yAbs)/(xAbs+yAbs) | 完整矩形、OperatorRectangleBoundary；总能量0不可观测，不反演运动方向。高位深不经过Sobel signed int2方向输出。 |
| ColorBalance / QualityColorParameters | 3个不同OrderedRgbRoleKeys、同坐标/组/辐射修订、同共同有效域，各原mean非负；total=Σmean，须≥MinimumTotalSignal；fractions=mean/total；referenceDistance=sqrt(Σ(fraction−reference)²) | OriginalPixels；referenceDistance是通道比例的欧氏距离，范围0..sqrt(2)，不是ΔE；缺组/辐射事实不可观测，负信号QS-OutputInvalid，不截成0。 |
| StructuredGroupSupport / QualityGroupParameters | OrderedRoleKeys与OrderedStepIndices长度相同且非空，role/step各唯一；按请求顺序匹配实际Descriptor的group/step/曝光/投影修订，交集mask统计commonValidFraction=commonValid/Requested | OriginalPixels；缺输入role/step允许进入方法NotObservable/StepMissing；重复/冲突拒绝请求。完整组才presentSteps=requiredSteps，不输出条纹调制度或相位质量。 |

QualityGaussianParameters增加Aggregation，QualityDirectionParameters只含Sigma；不留下由实现者选择的聚合或导数核。Focus/Direction可观测Policy要求同源同域RawStatistics含Saturation与PopulationStandardDeviation；服务消费先声明的这些原量，依赖必须在Methods中更早，否则Validate拒绝；缓存只在本请求。缺依赖拒绝请求；门失败输出对应原因，不按梯度高分越过曝光/纹理门。Policy.MinimumCoverage用Valid/Requested，MinimumSamples用本路线Center；Gaussian矩形路线明确含算子边界约定，不声称全部中心有独立真实halo。Noise前提的物理适用性和客户阈值留在真实样本资格，不阻断接口/错误/执行顺序冻结。

反光/过亮区只输出原高截断、覆盖和局部响应，不能仅凭高亮证明镜面反射或真实缺陷。Required ROI不得自动删亮区；需要材料区域排除时由宿主按新ROI/mask修订提交，原报告保留。服务v0.1仅使用来源ValidMask与请求框，无独立前景/排除域参数；§19的更多域分类仅供未来产品映射，不允许实现者自行生成排除域。

### 20.6 大图读取、支撑与合并的固定执行步骤

1. 每ROI独立、每方法按声明顺序；分块为行优先，tile半开框边长至多请求TileWidthPx/HeightPx，余边保留。所有像素位置按原行列，不把mask有效点挤成连续图。分配/读取前checked核完整ROI、块、halo、累计读取和结果预算；不够即QS-BudgetExceeded，不能降低分辨率/精度/NumBins或截断结果。
2. RawStatistics先按有界块ReadBlock，复制入单份ROI宽×高double+mask快照（临时源block与目标同时计账），得到§A的ManagedGrayImage；UInt8/UInt16保持类型，Float32精确扩为double承载并记录原Descriptor。以单个Region[0,0,H,W]调用同一evaluator，结果RegionKey映射原键；预算用父剩余ManagedBytes，MaxRegions=1、MaxMethods=本方法数、MaxHistogramBins=请求实际最大NumBins（无直方图时1）。A额外scratch/输出仍计父账本，MQ错误对应QS-InvalidRequest/BudgetExceeded/OutputInvalid，不重复算法。必须容纳完整快照，tile读取不等于常数内存分位数。
3. 纯计数/直方图分块优化只在不改变公开值和A算法的实现资格后引入；整数原值频数可逐块long相加，Float64精确分位仍保留全N排序副本，不取tile分位平均。矩可用(n,μ,M2)合并：δ=μb−μa，n=na+nb，μ=μa+δ×nb/n，M2=M2a+M2b+δ²×na×nb/n；先将计数转double避免long乘积溢出，空一侧复制值、不返回可变别名。固定tile合并顺序，浮点与逐行基准按资格容差对比，不宣称bitwise等价。未通过此差分前使用第2步基准。
4. Sobel非thin Size3与LocalDeviation具已知有限窗口。中心域是原ROI∩ValidMask经完整窗口侵蚀（cv2.erosion_rectangle1，奇数足迹≤511）；必须完全落原ROI，不把ROI外像素纳入定义。读每tile中心加真实halo，Sobel半径1，Deviation半径Width/2、Height/2；只汇总本tile拥有的中心，不重复计算halo分母。边界不足中心缺失；Ncenter=0返回NotObservable/SamplesInsufficient。借入block的ValidMask也需halo全有效，不能仅检查中心mask。
5. 其它Sobel/Thin、Gaussian、LoG及Noise先一次读取完整ROI矩形并确认mask全true，完整域执行，标OperatorRectangleBoundary；请求tile只限流式路线，不能强迫这些算子逐tile运算。它们的全域准备峰值若不满足预算则QS-BudgetExceeded；有洞mask为Unsupported/MaskUnsupported。Noise全域sigma无可证明的tile合并；Gaussian/LoG未冻结精确有限halo，不以经验半径声称full等价。未来支持带洞/精确tile须先增加方法修订与差分证据，本版无自动备用。
6. Uniformity使用§20.4的语义网格，与读取tile独立；任一语义块可由多个读取tile拼成原像素域，intensity显式传实际统计Region（该算子忽略Image domain）。全域intensity须使用同原域；不要平均块σ。Color/Group按对应像素位置形成共同mask，分别记录所有读取量；域不一致不按数组顺序配对。
7. 每块/方法检查取消、单调deadline、CheckCurrent；native返回后仍核输出和来源，再释放临时对象。取消/超时期间不在未退出native上关scope。精确释放顺序为响应/临时Region/Tuple→本方准备图→invocation.Close确认→所有scope逆序Close；首次失败进入§16保留路径。native内部峰值必须用实际Profile测，不能以输入字节上界替代。

资格反例：5×5全有效、Sobel3的完整中心为3×3；中心(2,2)的mask孔洞使所有与它3×3相交的中心失效。tile边界穿过一条亮边时，full与tile须在相同中心集对比响应/计数；不允许只比较各图均值。高位深[0,4095]阈值4094.5按原值比较，HALCON threshold若用于整数区域须明确ceil/floor端点，不能按算子截断把4094计为高截断。颜色比例(1,0,0)与参考(0,1,0)距离sqrt(2)，不能错误限制为1。

## 21. 多帧、颜色、条纹与缺陷保护

多曝光HDR、RGB、偏振、投影相位等首先验证原曝光/角色/配准/时序组。逐通道饱和和有效mask保留，颜色比R/(R+G+B)是相对通道量，不等于Lab/ΔE；总信号不足不能除零补0。CFA/白平衡/线性化及光谱条件未确定时，不拿彩色显示作为颜色计量资格。

结构光输入质量可包含饱和、调制度/条纹响应、完整步序和空间支撑；本版§16公开输出仅含所请求的逐帧原统计与§20.5组完整性/共同支持，不实现调制度、条纹响应或相位质量输出。单帧线提取成功不能证明相位组足够或三维重建合格。条纹/相位具体算法在028/[DEV-VIS-027](<../../shared-modules/guidance/03-vision/DEV-VIS-027_3D HeightField与重建开发指导.md>)，013输出方法需消费的质量量，不复制重建器。遮挡/反射不可观测域需要物理/多视角或方法证据，黑像素本身不是遮挡证明。

坏点/平场/去噪由014及标定能力生成派生图，013对原图与派生图分别评价。真实小缺陷也可能表现为亮点/细线，不能用单帧异常点统计自动生成永久坏点表。增强后更高分不证明更好检测；批准链须比较最小缺陷保留、边缘位移、OCR原读/码质量、条纹相位及下游误接受，原图和处理谱系可回看。

## 22. 原报告、缓存与重拍交接

同一请求冻结方法/来源后可共享ROI准备和适用统计；缓存键含原帧/plane/处理链、ROI/mask、有效位深/参考、方法/尺度/后端及依赖修订。相同像素hash不证明同一物件/曝光，原来源不可丢。计算结果可缓存，当前资格/授权不能永久缓存成可用。

质量报告只产生数值/域/原因。宿主按原方法策略决定能否进入OCR/3D或是否请求受控重拍；013不得调用设备，012不得把缺失质量填0。来源报告尚在计算时，不让FrameSet等待质量、质量又等待“已通过FrameSet”形成循环：先发布结构冻结且只授读取资格的原帧，013计算，宿主再核具体方法准入。原帧租约要覆盖native完成；取消请求不是已停，释放到实际排空后执行。

AI质量分类可作为可解释候选/影子对照，须另经AI治理及工业样本资格；本页不将无证据的“AI清晰度分”加入生产硬门。曝光/光源自动优化由[061](../../shared-modules/packages/PKG-061_ImagingOptimization.md#imaging-candidate-validation)消费本报告，036/工程宿主接入；优化目标不能是制造更多PASS或删掉困难ROI。013不维护候选搜索或独立试验批准，原指标与派生目标/排序分开。

## 23. 无 UI 调用与独立质量控件

首片无窗口宿主完成内存托管灰度快照→固定 `ManagedQualityRequest`→逐指标 `ManagedQualityResult`→宿主解释→释放 evaluator；不读取原帧、不创建 lease、不加载 HALCON/AsunImage。服务无UI宿主先按§16完成端口读取→质量请求→Completion/逐指标报告→真实释放；产品宿主在获批映射后关联原产品事实。唯一控件规格见§8.1。可选控件显示宿主viewer提供的原图/派生图、已请求的分通道直方图、逐指标/尺度原量与单位、原始证据和方法版本。有效域/高低截断热图与尺度响应图仅使用§8.2宿主已有且唯一匹配的诊断层；无匹配层则定位原ROI，不从标量报告推造像素。默认是任务所需指标和失败定位，高级面板展开直方图 bin/滤波支撑/来源；不放无依据的万能“质量100分”。图上选择 ROI 只改变工程查看范围，改生产 ROI/阈值须导航原编程工作台。

图例同时用线型/文字与颜色；每指标选择同步影像支持域，缺值显示“无法评价：纹理不足”等具体原因。切换frame/plane/方法时冻结选择代，旧报告可查历史而不填入新画面。宿主提供三语/主题，控件不重复建语言切换或全局静态缓存；关闭一实例不取消其它宿主请求。UI014用只读诊断模式，编程宿主以明确草稿上下文提供参数预览，两者使用同一核心。

## 24. 验收、性能与研究边界

首片先验证托管灰度快照的指标/域/单位、有限值/分母/预算、唯一 evaluator/factory 和最小 host；之后才进入正式指标/域/单位和原 C 合同→曝光/直方图精确计数→支撑感知 Sobel/LoG/噪声→区域/颜色/多帧适用性→宿主质量桥/两消费者→控件/真实规模。性能测原 ROI 有效数/纹理/位深、histogram bins/邻域支撑、共享准备/复制量、native 峰值、冷/热尾延迟与取消排空。不能只测 8-bit 小 ROI 就宣布高位深全图达标。

必须挑战：ROI外污染且Image domain已缩小；12位装uint2的窄动态范围；边界阈值/统计分母；空域/单像素；mask孔洞/跨tile支撑；高噪声假高清；均匀靶低梯度；强方向纹理假运动；Deviation的2倍与量化；两个候选差值被误叫不确定度；多步相位少一帧；同帧重包假重复性；旧结果晚到/取消/native未停；任务A可用而B不可用。预期均可回到上述精确语义，不靠截图“看起来清楚”。

后续增量的可判定断言：R 有8个像素、R∩V 有6个、两个批准排除子域在 R∩V 内各有2个且重叠1个时，排除计数为3、D为3，原覆盖率仍为6/8；清空前景不改变上述计数，D为空时依赖比例缺失。高5、宽8的 ROI 分为2×3时，行端点为0/2/5、列端点为0/2/5/8（相对 ROI），六块无重叠且覆盖40像素；最差量并列时按最小行优先索引，缺测块仍保留。短 payload/大槽、两个 ROI 各自申请完整父预算、较晚子期限、native慢退出、首次释放失败/后续显式重试，分别证明真实容量计账、累计限额、期限收窄及未释放资源不发 `ResourcesReleased`；不可变借读中的像素 hash 不替代当前来源核对。文件导入时间与采集时间分离，缺运动/投影/颜色证据只阻断依赖项。验收随获批适配切片进入既有对应测试，不在文档阶段新增产品或测试文件，也不把这些断言写成已通过。

来源：[HALCON/Aravis/Basler及竞品原页](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#acquisition-quality-research)、[AOI只读采纳](../../references/REF-008_PCBA-AOI指导副本与平台采纳映射.md#acquisition-quality-adoption)。未读取AsunImage内部、未运行HALCON/WPF/上游测试或工业对标。纯托管首片API为主控已接收六项规格的Module API v0.1基线（ModuleCoreImplementationReady，仅规格准备）；本版所有公开路线/变体/空间尺度及算法规格按§16/20冻结，真实消费者的选择/Required/物理尺度映射、正式产品Schema、真实成像条件、生产阈值、真实UI/性能与产品Adapter集成仍需对应Owner采纳或验收；当前产品资格保持 `PreparationIncomplete`，完整文档结论见§24.5。


实现时坐标和资源账本的局部变换规则：ReadBlock.Bounds是原源全局整数像素框，Samples[localRow×width+localCol]对应(Row0+localRow,Col0+localCol)。建立HALCON局部图时原Region/mask减去该block起点，计算后Support.Bounds/CoordinateRevision始终返回原框；不得把局部(0,0)当原源坐标。scope/请求保留只由service账本计一次，adapter PeakAdditional只计它本方新增分配；托管Raw快照在service账本计一次，调用A时用父剩余额度加该快照已预留量供A账本核完整视图，A的ReservedWorkingBytes再减已计快照才作为追加，不能重复计费或漏记临时源block。Raw输出与A scratch按同时存活时间计峰值，顺序消费释放后归还临时量；不同方法不可重复申请原父上限。

参数实验不是新的模块API：§17的建议/候选排序由工程宿主完整Request/方法/原量实施，并使用§8保存草稿意图；没有模块Advisor结果或StaleDTO，不允许编码时临时增加“推荐器”项目。只有客户真实光学/标签/阈值和目标性能需要真实Profile；接口、排序、参数边界、单位、恢复与Owner已由本指导冻结，不能借这些外部门继续搁置内部语义。


### 24.1 逐切片六项规格结论与两轮反例自审

六项按DEV-GOV-010 §3.1逐一列明：ManagedCoreSlice-01原接收保持；主控2026-10-11已回读0.6.0-prep并接收QualityServiceSlice-02/Core+Simulator完整六项为ModuleCoreImplementationReady（仅文档规格准备）。WpfSlice-03整体装配/Presenter/原Owner恢复新增指导和AsunImage公开构造指导确定范围限定内容接收；保存知识及0.5.2-prep Stop原接收保持。规格接收不证明HALCON/WPF/native资源系数、真实Viewer/保存Owner/产品映射、运行/性能或现场资格；相应资格仍PreparationIncomplete/NotReady，不由Core推广整模块Ready。

| 切片 | ①边界/第二消费者 | ②API/Owner/单位/版本 | ③独立Host/依赖 | ④场景/恢复断言 | ⑤Benchmark | ⑥工程/范围/顺序及剩余门 |
|---|---|---|---|---|---|---|
| ManagedCoreSlice-01 | §1/A.4；OCR与2D/3D工程工具 | A.1–A.3，唯一evaluator/factory，纯值Owner | A.2可构造内存host，无外部库 | A.3固定数值/预算/重复/并发/Dispose；取消/期限不适用已明示 | §11.1纯托管端点及目标来源 | Core binding/§24.2；主控2026-10-10已接收六项，ModuleCoreImplementationReady（仅规格准备）；实际创建/build/run/两进程接入尚未执行，不受产品帧/客户值阻断。 |
| QualityServiceSlice-02/Core+Simulator | §16.1/16.5/16.11；独立OCR原统计与3D步组支持两Host，非产品控制 | §16.2–16.10完整公开端口/factory/Profile/预算/错误/Stop/原Task/根Owner；版本沿§12 | §16.11完整Fixture+两显式端口lambda+clock+构造前root槽；只引Core/BCL，无测试shim/产品Shell | QS.H01–09、QS.STOP.01–06、QS.A01–08；§16.11因果装饰器与§24.4两轮正常/异常/恢复 | §11.1服务/构造/根预留/观察槽/真实归还测点；目标未采纳=NotEvaluated | 仅Core/Core.Tests，路径及顺序Core binding/§16.1/§24.2；主控2026-10-11已接收完整六项文档规格，ModuleCoreImplementationReady；实际创建/build/run/双进程/协调/资源与真实AsunImage资格未验，不表示实现或产品准入。 |
| AsunImageSlice-02A | 全部请求路线与CPU边界§20.5–20.6 | §16唯一端口/§24.3公开工厂、§2.1搬运/域/提取/逆序释放，native局部Owner，不外露句柄 | 文件/内存scope+真实port，无WPF | §10/20.6/24.5，3175、高位深、洞mask、full/tile、clipping/空对象、关闭失败；真实Golden/资源未执行 | §11.1同样本路线/准备/native/释放 | §16.1工程+测试；公开构造指导的确定范围已由主控2026-10-11限定内容接收；0.6.1仅补可决定实施步骤，实际C#类型/重载歧义只在消费编译中处理，真实算法/native构造/资源系数/释放/性能资格仍PreparationIncomplete/NotReady，不列安装/授权/算子存在核验。 |
| WpfSlice-03 | IQ-WPF-01/§8.1、§8.5；只读诊断与工程草稿两个独立STA Host | §8.1–8.4控件/Presenter/权限刷新/语言/原保存Owner/知识与活动/恢复查询；§8.2视觉/诊断层边界，原事实不变 | §8.5从完整两Fixture/公开service-root/MemoryDraftOwner/MemoryBoxViewer创建独立panel/Presenter，Attach→Unbind，进程表持原Thread/Task | IQ.SAVE.01–06、IQ.WIRE.01–08与§24.4/24.5；代次/撤权/迟到/异常/查询/双Owner分离、键盘/三语 | §11.1唯一1920×1080真实DPI，首次呈现/切语/回收/Dispatcher积压≤1；目标来源为PageProfile | §8.1唯一Wpf/Wpf.Tests；原保存定向接收保持，主控2026-10-11已限定内容接收整体装配/Presenter/原Owner恢复新增指导，真实资格整体仍PreparationIncomplete/NotReady；真实DevExpress/WPF/UIA/DPI、视觉品质/性能与真实Host持久化/fence/产品接线未验。 |
| FrameAdapter/ProductSlice | 只映射原事实，不生成机判/设备动作 | §3.2产品候选不是新模块API；原C-03/C-04 Owner待采纳 | 输入桥实现IQualityInputPort，无第二租约权威 | §9/16.7源断连、同Id新revision、真实租约释放 | §11.1产品端点 | 实际宿主工程/共享字段须原Owner冻结后绑定；这是明确内部集成缺口，不伪称客户外部门，也不阻无关Core。 |
| 参数建议/方法资格 | §17–17.1有限宿主实验，不增加搜索器DLL | 同§16强类型参数/报告，宿主保存/人工批准 | 两工程工具均可串行实验，无隐含训练/设备动作 | §17.1/24.5缺标签NotEvaluated、失败/未提交保留分母、留出失败拒选、输入变更Stale | 同§11.1/Profile，质量先于速度 | 不另建模块工程；有限实验、生命周期预算与保存挂接已给出，真实留出/方法资格/人工批准待执行。 |

两轮内容自审的反例、正文修订和可判定接收断言如下。这是本轮文档走查，不声称已运行所列产品测试。

| 视角/具体反例 | 本轮同步修订 | 后续执行必须观察到的结果 |
|---|---|---|
| 第一轮：数值/信号。Float histogram [0,1,2,3,4]与整数同范围；大偏置小方差；mask孔洞邻接tile边 | A.3封闭分箱/总体矩/精确分位；§20.5–20.6真实支撑与固定分支 | 分箱Count/N闭合，σ不被消减误算，hole/halo改变中心计数而非压缩图像；源/支持相同才对比。 |
| 第一轮：高位深LoG int2被当实值、噪声σ被tile平均、反光ROI被删 | §20.5独立LoG/Gaussian、Noise全域、反光原量与Required保留 | UInt16 LoG Unsupported；Gaussian实值新请求；3175无σ；所需反光域仍存在，不因删除而Complete。 |
| 第二轮：接入/生命周期。Open抛错但内部留资源、同RequestId多个方法Close墓碑冲突 | §16 OpenAttemptId先生成、CheckOpen/CloseOpen；每方法独立invocationId | 无丢失Owner；Pending期间不Close；下一个方法不能误认为已释放，成功关闭不重复。 |
| 第二轮：取消后native晚到、Close挂起/首次失败、ReadBlock复制超额 | §16.6后台持有原任务、单次释放任务、scope drain查询、剩余预算 | Completion未确认前不终结、不发布迟到报告；超额在复制前拒绝；重试最终仍保留首次失败。 |
| 第二轮：控件保存未知回执、旧generation预览覆盖新源、关闭误关宿主viewer | §8.1–8.3显式知识/活动/原意图查询、SetExecution/ApplySaveResult/BindComparison与借用Owner | 原草稿/IntentId可恢复；旧预览隔离，旧保存事实更新原意图历史而非新源；CloseView只清本方显示引用，Host继续对账。 |

### 24.2 唯一测试执行约定与有界命令（未来实现任务）

Core.Tests固定Microsoft.NET.Sdk、net10.0、OutputType=Exe、仅ProjectReference受测Core与.NET BCL，不引入待选测试包。入口Program执行ManagedQualityContractTests、ManagedQualityNumericsTests、ManagedQualityLifecycleTests、ConsumerHostContractTests、QualityServiceHostContractTests全部断言；本轮QS.A01–08加入原QualityServiceHostContractTests，两个公开包装配入口源文件为同测试目录QualityEmptyHostExamples.cs。ID为MQ.C/MQ.N/MQ.L/MQ.H/QS.H/QS.STOP/QS.A；--host ocr或--host group只运行对应双Host独立进程断言，无selector则全部执行，未知selector退出非0。Wpf.Tests内QualityPresenterHostTests固定IQ.SAVE/IQ.WIRE；MemoryDraftOwner/MemoryBoxViewer/有限STA进程表源码仅在该测试工程，Fixture以编译链接原示例源复用，不引用Core.Tests DLL。任一失败/未完成/必需跳过退出非0并输出ID，完整通过才0。固定TimeProvider/因果闩锁；内部总截止90秒，单个观察≤5秒，最后确认全部本方Thread/任务/资源真实归还。分配超大值测试用预检，不真实制造OOM或无限挂起；dotnet test不执行这些Exe。

获准创建后在仓库根运行下面完整PowerShell命令；此轮不执行，不声称工程已存在。函数已完整给出，不依赖聊天helper。外层120秒build/180秒run只终止验证子进程；产品native退出/资源资格仍须自身证明，进程被杀不记通过。

~~~powershell
function Invoke-QualityBounded {
    param([string[]]$Arguments, [int]$TimeoutMs)
    $qualityStart = [System.Diagnostics.ProcessStartInfo]::new('dotnet')
    $qualityStart.UseShellExecute = $false
    $qualityStart.CreateNoWindow = $true
    foreach ($qualityArg in $Arguments) { $qualityStart.ArgumentList.Add($qualityArg) }
    $qualityProcess = [System.Diagnostics.Process]::Start($qualityStart)
    if (-not $qualityProcess.WaitForExit($TimeoutMs)) {
        $qualityProcess.Kill($true)
        $qualityProcess.WaitForExit()
        $qualityProcess.Dispose()
        throw 'ImageQuality verification exceeded its process deadline.'
    }
    $qualityExitCode = $qualityProcess.ExitCode
    $qualityProcess.Dispose()
    if ($qualityExitCode -ne 0) { throw "ImageQuality verification failed: exit $qualityExitCode" }
}
Invoke-QualityBounded -TimeoutMs 120000 -Arguments @(
    'build', 'src/Modules/image-quality/Asun.Modules.ImageQuality.Core/Asun.Modules.ImageQuality.Core.csproj',
    '-c', 'Release', '--nologo')
Invoke-QualityBounded -TimeoutMs 180000 -Arguments @(
    'run', '--project', 'tests/Modules/image-quality/Asun.Modules.ImageQuality.Core.Tests/Asun.Modules.ImageQuality.Core.Tests.csproj',
    '-c', 'Release', '--', '--deadline-seconds', '90')
~~~

AsunImage.Tests另为net10.0 Exe，引用Core/实际adapter及已有依赖；Wpf.Tests为net10.0-windows Exe/UseWPF、STA入口，引用Wpf/Core/本机DevExpress。获准切片后用同函数build各自§16.1/§8.1唯一工程、run对应Tests；不得把Core Exe结果当它们通过，也不用dotnet test的空执行作为证据。真实native/Golden套件需给定真实输入及资格Profile，缺资料退出非0/NotEvaluated，不填模拟成功。WPF只在固定1920×1080验证视口运行真实控件，关闭最后做资源/事件退订检查。性能/耐久/HIL/现场按对应Profile另验，文档结构检查不代替它们。

### 24.3 AsunImage适配器的公开构造与独立交付

本节公开构造指导的确定范围已由主控2026-10-11限定内容接收；不代表实际HALCON/native构造/资源系数、Golden或性能资格通过。namespace Asun.Modules.ImageQuality.AsunImage仅公开下列工厂；实现IQualityVisualPort的具体类型内部化，不暴露SDK/native句柄、HALCON对象或静态runtime。Create校验null/正预算后捕获实际HALCON26.05 CPU/runtime identity，与本实例绑定；不接受宿主伪造的版本字符串。

~~~csharp
public static class ImageQualityAsunImageFactory
{
    public static IQualityVisualPort Create(TimeProvider clock, QualityBudget limits);
}
~~~

工厂产物一实例只注入一个service，不能两个service共享可变资源表。所有图像/Region/Tuple由该port保有并按invocation归还；service停止前关闭全部invocation。无需隐藏窗口/初始化UI/产品数据库；host可用自己的文件/内存IQualityInputPort，仍按相同Start/Completion/StopAsync接入。公开语义算子及参数顺序已在§2.1冻结，C#实际类型/封送不明确时只查公共签名/消费编译；不得研究AsunImage内部或另接HOperatorSet。



### 24.4 0.6.0-prep两轮有限自审与精确后续门（2026-10-11）

本节保留0.6.0-prep新增服务/公开接线的两轮走查，不重复已接收ManagedCore算法、保存知识或0.5.2 Stop规则；下表是**正文规格推演与未来测试断言**，未编译或运行。每个反例都有本模块内可决定的处理路径；真实样本/IO/设备/性能等门只阻依赖它的用途。0.6.1完整批准范围收口和新增边界自审见§24.5。

| 轮次/断言ID/精确反例 | 本轮闭合位置与后续必须观察的结果 |
|---|---|
| 实现者正常 QS.A01 / IQ.WIRE.01 | §16.11两个完整fixture经公开Input/Visual/Clock/Profile/root构造：OCR低/高截断1/1、分位距254、hist=[1,1,0,2]；3D三步共同mask3/4。服务Report/原Source/参数不变，根/两实例无串扰；§8.5两STA各Attach、无隐含产品依赖。 |
| 实现者边界 QS.A02 | Root.MaxSlots=1已保留未知槽时第二Reserve拒绝且factory调用0；预留刚好及差1byte、超过MaxSources/HistogramBins/GroupInputs在对应分配前拒绝。Root持原Task，不把第二实例当恢复。槽上限是软件夹具，实际RSS/客户目标另验。 |
| 实现者构造异常/到期 QS.A03 | Reserve先于所有factory；构造闩锁不退出时有限WaitAsync/Close返回未确认，原OriginalConstruction/捕获/部分port仍保留。迟到成功仅同槽Stop，不Start；纯托管factory失败且原Task已结束、无资源则立即Released，不造native drain。 |
| 实现者消费/清理分离 QS.A04 | 同源正常result后消费故意抛错，WorkIssue保留而Cleanup可Released；同时Close失败有独立CleanupIssue。等待取消/过期的finally使用None和剩余有限budget，不能覆盖原TimedOut/ReleaseFailed或清Task。 |
| 实现者取消/重复恢复 QS.A05 | 复用QS.STOP.01–06与§16.11故障装饰器；观察Task结束不代表原屏障Task退出，RetryRelease只一份阶段任务，首次Close失败最终仍Failed。成功阶段不重做，确认移交丢失保持发送方推进权。 |
| 实现者UI异常 IQ.WIRE.02–03 | Attach/Show/Viewer/ApplyPreviewResult抛错仍撤订/Unbind/有限Close；原线程退出TCS只在实际finally完成，Close结果/保存知识/线程退出三轴分开。窗口离栈不丢root或SaveOwner，不在Dispatcher同步等native。 |
| 实现者保存/恢复 IQ.WIRE.04 | MemoryDraftOwner.Register先完整字段/容量/当前授权检查，登记OriginalWrite后BeginWrite；同Id不同数组内容拒绝，同Id同内容复用原操作。§8.3 Unknown/Drained仍不可新Save，停止Query等待不写入、不制造序号；跨generation知识只进原历史区。 |
| 外部消费者空包 QS.A06 | 只按§16.10公开形状和§16.11全源码构造参数即可引用Core；没有TestInputPort/TestVisualPort、外部已构造request或隐藏builder。--host ocr/group两个独立进程各完成调用/两轴/归还，断开A仍能运行B。 |
| 外部消费者重复/回退 QS.A07 | 同开放service在上次Completion/ResourcesReleased之后可接受新的显式Preview RequestId；Stop后拒绝。未知ApiVersion不Open；包/API语义按§12回退，只读原版本报告，不能把0.6新增Root/Presenter删去后继续解释在途状态。 |
| 外部消费者保留/重新挂接 QS.A08 / IQ.WIRE.05 | 原Task挂起时关闭A不会清B；同槽Get/Recover原实例、不new factory。旧预览g1迟到不写g2；查询预览只观察原Task，保存原Intent查询独立。Unbind后根/保存仍未解决就只能保留或同对象确认移交，不能销毁真实借读Owner。 |
| 外部消费者完整UI IQ.WIRE.06–07 | Wpf.Tests源码链接唯一Fixture，Host自己的MemoryBoxViewer/MemoryDraftOwner及两STA流程公开完整。三语SetLanguage、SetPermissions撤权不重置草稿/原Intent/Task；订阅/Timer/待呈现队列上限可判定，Presenter不设置全局culture、不中途换事实Owner。 |
| 外部消费者版本/关闭 IQ.WIRE.08 | CloseView后原改变入口拒绝、迟到结果安全忽略，Unbind幂等返回同Detach.Task；重开新panel用原Owner.GetRetained恢复知识不重新提交。当前尚无已发布0.6消费者，新增API按prep→发布Minor规则，未知版本拒绝而非默补参数。 |

**本轮接收与剩余门**
- QualityServiceSlice-02/Core+Simulator：§24.1六项已分别指向边界、完整API/Owner、从零双Host、异常/恢复断言、Benchmark与唯一工程/路径/执行顺序；主控2026-10-11已接收完整六项文档规格，现为ModuleCoreImplementationReady（仅规格准备），不是运行或产品准入。不再把公开port/root/factory/完整输入/Profile/正常异常恢复列为待客户事项。后续实际创建、build/run、确定性根/协调/版本/双进程及资源断言尚未执行。
- WpfSlice-03：§8.1–8.5已冻结公开控件/Presenter/保存Owner、权限与语言刷新、原意图恢复、具体DevExpress组合及双STA Attach→Unbind；主控2026-10-11已限定内容接收整体装配/Presenter/原Owner恢复新增指导，真实资格仍PreparationIncomplete/NotReady。真实WPF/DevExpress呈现、键盘/UIA、当前DPI与唯一1920×1080布局/视觉品质、退出退订/真实两Host接线尚未运行。
- AsunImageSlice-02A：§24.3公开构造指导确定范围已由主控2026-10-11限定内容接收，真实资格仍PreparationIncomplete/NotReady；复用§15.1/20/24.3既有HALCON26.05官方路线/完整参数；真实公共C#消费构建及Golden差分、复杂mask/halo/full-tile、native构造/原任务/释放、同样本准确性/尾延迟/峰值资格未验。不是算子存在、安装/授权门；本轮不新增或重做视觉研究。
- 真实Host保存/权限/产品桥：按§8.3–8.4适配原持久化Owner的目标/当前主体/fence、幂等登记/原IO查询、崩溃恢复/确认转交；FrameAdapter的原C-03/C-04字段和真实借读资格仍由其原Owner采纳。这里的内存Owner/合成图只验软件接线，不证明事务持久化或设备/产品发布。
- 性能/场景/现场：§11.1测点和统计方法已定；目标机器、真实输入/Golden/误接受拒绝及客户任务目标由相应批准Profile提供，未采纳=NotEvaluated。客户物理条件、设备真实退出和现场指标只阻相应用途；不能借它们退回已接收纯托管Core或替代本模块内部接线缺口。

### 24.5 完整批准范围的软件设计收口与原会话自审（0.6.1-prep，2026-10-11）

**结论：本模块当前批准范围内可由模块Owner决定的软件设计欠账已闭合。** 范围不是只含ManagedCoreSlice-01：包括§16全部具名视觉方法、Core/Simulator/AsunImage适配、无UI独立接入、可选WPF诊断/工程草稿和宿主有限参数建议。执行、内容审核、修复与验证均在登记原会话 `01a10306-f171-79a1-9e16-755c1ee237d1` 完成，总控仅接收状态。下面是本页实施章节索引与验收核对，不新增API、产品事实或第二套指导。

| 批准能力/真实消费者 | 唯一输入→处理→输出与参数位置 | 异常/恢复与可判定验收 |
|---|---|---|
| 亮度、曝光截断、直方图、总体对比、覆盖；OCR/读码/2D前检 | A.1–A.3内存值合同；§16.3/19/20.5 RawStatistics复用同evaluator，原值/原mask、显式阈值/bin/分位→具名原量/单位/完整计数。§16.11 OCR完整fixture | 零域保留Coverage0和其它缺项；读失败不是覆盖0；范围内/外/无效数闭合，截断分母N与覆盖分母A不混。A.3及§9–10原断言保持。 |
| 清晰度；OCR/读码与2D/3D前置纹理检查 | §16强类型方法/Policy先声明Raw依赖；§20.5固定Sobel/Gaussian/LoG类型/完整参数/聚合/单位；§2.1与20.6像素/中心域/halo/全域路线→response/Support/原因 | 缺纹理/曝光支持返回原原因；合法不支持类型/域为Unsupported，不暗换路线。Sobel3全有效5×5中心3×3，孔洞影响完整窗口；真实full/tile在同中心集差分。 |
| 噪声、局部灰度离散；OCR与工程诊断 | §20.3/20.5明确estimate_noise各假设/Percent及单次全域sigma；deviation_image奇数足迹/real/完整中心→twiceLocalStdMean。全部参数由请求冻结 | 3175缺项而非0；不平均tile sigma，不把纹理/2倍局部离散叫噪声或不确定度。假设适用性须真实样本资格。 |
| 局部均匀性、方向响应；2D/3D工程工具 | §20.4/20.5固定等网格/原域intensity、原全域均值、最差方向与并列索引；real derivate_gauss x/y→具名响应/anisotropy | 缺块原位保留Tiles且全局缺值，不能余块冒全域；x+y=0无比例；方向纹理不推出运动方向/模糊长度。 |
| RGB通道平衡；颜色前置与工程诊断 | §16.3/20.5/21按有序RGB角色、共同mask、辐射/组修订→各mean比例与referenceDistance；固定参考和最小总信号 | 缺依据NotObservable，负信号不裁0；(1,0,0)与(0,1,0)距离sqrt(2)，不称DeltaE。颜色转灰归预处理Owner。 |
| 结构光组支持；3D前置工具 | §16.3/16.11 Group fixture/20.5有序角色/step、组/投影/曝光/配准→presentSteps/requiredSteps/commonValidFraction；逐帧原量显式请求 | 少step缺项、重复/冲突拒绝、交集mask不按数组猜配对；不输出调制度/相位质量、不重建、不放行。产品Required归产品Owner。 |
| 有限参数建议与方法资格；两个工程宿主 | §17–17.1有限候选/样本/修订/预算→同Validate/Start/原报告→固定筛选/排序→单次独立留出→原Owner草稿。没有模块Advisor API | 失败/未提交保留每候选原分母，无完整证据NotEvaluated；留出失败拒整次；变化Stale、停止留原Task/root，不能自动生产改参或操控设备。 |
| AsunImage适配与来源读取；文件/内存无UI消费者 | §2.1公开搬运/Region/响应/释放；§16.2–16.10端口/执行/构造前根；§20.6分块；§24.3唯一工厂及§16.1唯一工程/依赖 | checked容量、精确码值、mask/runs回核、返回前Current；所有异常/取消保留原invocation/Owner。§10/16.7–16.11及本节边界断言随实际适配验证；公共签名只消费编译，不检查AsunImage内部。 |
| 无UI独立调用、版本/发布/回退；OCR与3D独立Host | A.2与§16.10–16.11从空包可构造；§12独立包/报告版本，Core不依赖SDK/UI/产品Shell；§24.2未来有界执行约定 | 两个独立实例/进程不串扰；未知API拒绝，回退只读原版本；业务/cleanup分轴，资源未知不能遗忘/替代实例。性能测点和目标来源见§11.1，不假称已执行。 |
| WPF诊断/比较/预览/草稿；只读与工程两个STA宿主 | §8.1–8.5唯一控件/Presenter/公开viewer/原保存Owner/完整挂接；§8.2三语/主题/视觉/键盘；§23标量与诊断层边界 | 旧代次不写新源；撤权/未知保存原Intent查询；CloseView/Unbind不取消他人Owner；无匹配诊断层只定位ROI。唯一1920×1080客户区，真实视觉与键盘分别验。 |

两轮有限自审复用§24.1/24.4已接收结论，只走查本轮补缺涉及的输入、参数、失败与消费者边界；以下数值是软件反例推演，**不是HALCON实测响应、Golden通过或客户容差**。

| 轮次/具体反例 | 正文处理与未来必须观察到的断言 |
|---|---|
| 实现者：UInt16原值65535经过有符号int2或byte；Float32载体不能精确还原；mask=false位置NaN | §16.3/2.1在native前拒绝不合法载体；合法65535保持uint2/real码值，不成−1/255。所有位置有限，mask不豁免源完整性。 |
| 实现者：局部row2半开列[3,6)变成inclusive[3,6]；裁切后恰好仍有相同N | §2.1生成(2,3,5)，回核每run而不只比总数；clipping/坐标变形QS-ProviderFailure，不能用新域继续统计。 |
| 实现者：孔洞贴tile边；侵蚀返回0对象或1个空Region | §2.1/20.6用真实halo及完整有效窗口，只汇总拥有中心；0对象不读runs，空中心SamplesInsufficient，不输出0响应。 |
| 实现者：gen_image1未返回时取消，提前解除固定或Close借入scope；response为int1的−128 | §2.1/16/20.6保持原调用/pin/Owner直到实际返回，再逆序释放；扩大double后abs=128、square=16384，不发生sbyte溢出。原Task/资源轴规则保持。 |
| 实现者：每轮重置读取上限或逐轮相加内存峰值；Validate失败删候选 | §17.1累计读取/时间不返还，工作内存按同时存活量，原记录/未释放资源持续预留；失败候选及未提交组合保留、无资格。 |
| 实现者：每候选计划4正/6负，其中1负例误接受、1正例明确拒绝、1负例超时、1正例未提交 | §17.1分别为1/6、1/4、2/10；超时/未提交不当正确拒绝也不改分母，该候选不取得方法资格。搜索集/留出分开，不按其它候选分母摊薄。 |
| 外部消费者：最高梯度就胜出，候选A留出失败后用同留出挑B | §17–17.1质量/不可观测/时延/资源完整硬门及原排序向量；仅一个候选一次留出，失败拒整次，不调阈值或遍试留出。 |
| 外部消费者：保存建议后切ROI/runtime，旧记录仍自动Start或批准 | §17.1/8.3原建议Stale/历史只读，原Intent知识保留；新Revision由原Owner当前权限处理，草稿不是生产批准，不新增设备动作。 |
| 外部消费者：按柱bin或同名layerKey假造高截断/尺度热图；两方法同layer但参数不同 | §8.1–8.2/23只显示原区间/count并定位ROI，只有宿主已有唯一匹配诊断层才显示；无匹配显示三语RegionLocationOnly，不补像素接口或覆盖另一方法响应。 |
| 外部消费者：模块自建viewer缩放、替换保存Owner，或关闭STA就清理未结束Task | §8.2–8.5/16既有合同与所有权保持；缩放归viewer已有能力，原保存查询/保留根独立，不以窗口消失冒资源Released。 |

剩余条件按责任分类，不能全部叫客户外部门，也不能反向把已闭合模块设计或已接收Core规格退回待定：

1. **本模块实现与运行验证**：获准切片后创建唯一工程，公共消费编译、真实HALCON Golden/full-tile/高位深/释放与native资源系数、Core/Simulator两Host、真实WPF/DevExpress/双STA/三语/键盘/UIA/唯一1920×1080视觉与性能均由本模块Owner执行。上述未运行；AsunImage/DevExpress不作安装、授权、兼容性或算子存在核验。
2. **跨Owner正式合同采纳与产品接入**：原C-03/C-04 canonical字段/序列化/真实帧借读桥，真实viewer诊断层、原持久保存Owner的fence/幂等/崩溃恢复，宿主PageContract/权限/产品Required及事实保存映射须对应原Owner冻结、采纳、实现并联验。这是内部跨模块合同/接入门，不伪称客户物理条件；候选产品形状不自动成为正式DTO，只阻断确实依赖它的产品桥/诊断层/持久化接入。
3. **真实Profile与资格事实**：客户光学条件/真实正负及留出证据、方法数值容差/误接受拒绝/生产阈值、目标机器资源/节拍/排空目标和现场验收由产品、客户及资格Owner提供或批准；缺失则NotEvaluated/NotReady，不编造物理值，不用模拟器替代。

ManagedCoreSlice-01与QualityServiceSlice-02/Core+Simulator既有`ModuleCoreImplementationReady`（六项文档规格）保持；WPF/AsunImage限定指导接收、§8.1–8.3保存知识、§16.9 Stop与附录A的原接收语义保持。**整模块不提升为ImplementationSpecificationReady或ProductReady，真实HALCON/WPF/产品资格仍PreparationIncomplete/NotReady。** 没有新工程、产品代码、测试工程、共享台账或新过程文件；本次交付仅为本页完整范围指导及自审。

文档验证（2026-10-11）：现有 `tools/validate_docs.py` 通过，含活动文档链接/DAG/消费者映射；本页定向核对围栏闭合、表格列数、50个本地目标和15项已记HALCON来源SHA-256无错误，§24.5唯一且已落正文。与本轮修改前原文比对，§16完整端口/Root/Fixture/Stop、§8.3–8.5保存/Presenter/双STA、§18–20算法路线、§24.3工厂、附录A正文及全部代码围栏保持；本轮仅补已列指导缺口。校验只证明文档完整性与保护范围，不证明产品执行或资格。


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

## 附录 A：Module API v0.1（ManagedCoreSlice-01 唯一首片基线）

本附录冻结模块自身纯托管合同，不引用产品 Contract、相机或 HALCON 类型。2026-10-09 修正尚未实现的 v0.1：使用真正不可变集合，结果改为完整的具名值类型，增加样本/分箱/数值资源语义。旧单 Value 形状没有已实现消费者，不要求为它添加兼容重载；若后续发现真实已发布消费者，先由主会话确认迁移，不能重解释旧字节。

### A.1 完整公开类型

下列声明均在 namespace Asun.Modules.ImageQuality，使用 System、System.Collections.Immutable；一个声明一个定义，§3.1 仅导航本接口。ImmutableArray.Default 非法，Empty 是否合法按以下表定义。宿主构造 ImmutableArray 时必须复制外部可变源，不使用可继续写入的别名；Core 和结果不返回底层数组。

~~~csharp
public enum ManagedPixelType { UInt8 = 1, UInt16 = 2, Float64 = 3 }
public sealed record ManagedGrayImage(
    int WidthPx, int HeightPx, ManagedPixelType PixelType,
    ImmutableArray<double> Samples, string SourceRevision);
public sealed record ManagedQualityRegion(
    string RegionKey, int Row0, int Col0, int Row1, int Col1,
    ImmutableArray<bool>? ValidMask, string SourceRevision);

public enum ManagedQualityMetricKind
{
    SaturationCount = 1, ExposureDistribution = 2,
    Contrast = 3, HistogramRange = 4, ValidCoverage = 5
}
public enum ManagedContrastStatistic
{
    PopulationStandardDeviation = 1, NearestRankQuantileRange = 2
}
public abstract record ManagedQualityMethod(string MethodId, string Revision);
public sealed record ManagedSaturationMethod(
    string Revision, double LowClip, double HighClip)
    : ManagedQualityMethod("saturation-count", Revision);
public sealed record ManagedExposureDistributionMethod(
    string Revision, double LowClip, double LowExposure,
    double HighExposure, double HighClip)
    : ManagedQualityMethod("exposure-distribution", Revision);
public sealed record ManagedContrastMethod(
    string Revision, ManagedContrastStatistic Statistic,
    double? LowerQuantile, double? UpperQuantile)
    : ManagedQualityMethod("contrast", Revision);
public sealed record ManagedHistogramRangeMethod(
    string Revision, double Minimum, double Maximum, int NumBins)
    : ManagedQualityMethod("histogram-range", Revision);
public sealed record ManagedCoverageMethod(string Revision)
    : ManagedQualityMethod("valid-coverage", Revision);

public sealed record ManagedQualityMethodSet(
    ImmutableArray<ManagedQualityMethod> Required,
    ImmutableArray<ManagedQualityMethod> Optional);
public sealed record ManagedQualityRuntimeOptions(
    long MaxWorkingBytes, int MaxRegions, int MaxMethods, int MaxHistogramBins);
public sealed record ManagedQualityRequest(
    Guid RequestId, ManagedGrayImage Image,
    ImmutableArray<ManagedQualityRegion> Regions,
    ManagedQualityMethodSet Methods, ManagedQualityRuntimeOptions Budget);

public enum ManagedObservationState { Computed = 1, NotObservable = 2 }
public enum ManagedExecutionState
{
    Completed = 1, CompletedWithUnavailableMetrics = 2, Rejected = 3, Failed = 4
}
public enum ManagedQualityUnit { Count = 1, Fraction = 2, GrayLevel = 3 }
public sealed record ManagedQualityError(
    string Code, string FieldPath, string MessageKey, bool Retryable);
public sealed record ManagedQualityValidation(
    bool IsValid, ImmutableArray<ManagedQualityError> Issues);
public sealed record ManagedDomainSummary(long RequestedPixels, long ValidPixels, string RegionRevision);

public abstract record ManagedQualityValue;
public sealed record ManagedSaturationValue(
    long LowCount, long HighCount, double LowFraction, double HighFraction)
    : ManagedQualityValue;
public sealed record ManagedExposureValue(
    long LowClipped, long Dark, long Middle, long Bright, long HighClipped)
    : ManagedQualityValue;
public sealed record ManagedContrastValue(
    double Value, ManagedContrastStatistic Statistic) : ManagedQualityValue;
public sealed record ManagedHistogramValue(
    double EffectiveMinimum, double EffectiveMaximum, double BinSize,
    ImmutableArray<long> Counts, long BelowRange, long AboveRange)
    : ManagedQualityValue;
public sealed record ManagedCoverageValue(double ValidFraction) : ManagedQualityValue;
public sealed record ManagedQualityObservation(
    string RegionKey, ManagedQualityMetricKind Kind, bool Required,
    ManagedObservationState State, ManagedQualityValue? Value,
    ManagedQualityUnit Unit, ManagedDomainSummary Domain,
    string MethodId, string MethodRevision, ManagedQualityMethod Method,
    string? ReasonCode);
public sealed record ManagedQualityResult(
    Guid RequestId, string ApiVersion, string ModuleVersion, string SourceRevision,
    ManagedExecutionState State,
    ImmutableArray<ManagedQualityObservation> Observations,
    ImmutableArray<ManagedQualityError> Errors, long ReservedWorkingBytes);
public interface IQualityDiagnosticPort
{
    void Publish(Guid requestId, string stage, string code);
}
public interface IImageQualityEvaluator : IDisposable
{
    ManagedQualityValidation Validate(ManagedQualityRequest request);
    ManagedQualityResult Evaluate(ManagedQualityRequest request);
}
public static class ImageQualityManagedFactory
{
    public static IImageQualityEvaluator Create(
        ManagedQualityRuntimeOptions options, IQualityDiagnosticPort? diagnostics = null);
}
~~~

所有参数无隐式默认；方法列表全局应用到所有 Regions，不自行挑 ROI。每种方法仅允许一项，Required/Optional 不能重复相同 MethodId；比较多组参数须发不同请求。未知枚举/派生方法拒绝，不由自由字符串或反射加载算法。Revision、SourceRevision、RegionKey 非空且不超过128 UTF-16 code units；RequestId 非空。结果ApiVersion固定image-quality-managed-v0.1，ModuleVersion取Core包版本且非调用方字段，Domain.RegionRevision保留ManagedQualityRegion.SourceRevision（该区域/mask快照修订，不要求等于图像修订），Method 是本次原参数快照，避免只留 Revision 却无法回放。

| 校验对象 | 唯一语义 |
|---|---|
| 图像 | 宽高正；checked long 面积再验证不超过 ImmutableArray 的 int 长度；Samples.Length 恰等面积，UInt8/UInt16 必须整数且在0..255/0..65535，Float64 为有限值。不由容器上限推断传感器白电平。 |
| ROI/mask | 半开框且全框在图内、面积正、键唯一；mask 为 null 表示全有效，否则长度恰等 ROI 面积。全 false 是已知零有效支持，合法；空数组与尺寸不符是非法。重叠 ROI 独立报告，不算全图并集。 |
| 方法 | Required/Optional 至少一项；饱和 LowClip < HighClip；曝光 LowClip ≤ LowExposure < HighExposure ≤ HighClip；整数图阈值必须在容器范围内，允许非整数阈值但按原值比较，不向下取整改变分类。它们是调用方明确的码值界限，不自证物理饱和。 |
| 对比 | 总体标准差必须两个分位参数均为空；分位路线须0 < LowerQuantile < UpperQuantile ≤1。N=1总体标准差为0，是数学诊断，不自证纹理可观测。 |
| 直方图 | finite Minimum < Maximum、NumBins正且不超过实例与请求上限；整数Minimum/Maximum须在容器码范围内，再将有效 min/max 向下取整，取整后须 min≤max；BinSize 整数图为(max-min+1)/NumBins，Float64 为(max-min)/NumBins；BinSize须正有限。分箱规则见A.3，不沿用旧BinWidth。 |
| 容量 | 四个选项均正；请求每项上限只能收紧工厂上限。分配前checked估算输入/参数保留、mask、scratch、全部报告与直方图；同时存活工作集不得超 MaxWorkingBytes。数量超限先拒绝，不先复制后报错。 |

### A.2 顺序、失败、线程和示例

Validate 无诊断副作用、无结果缓存，不授予后续免检。Evaluate 总是重新 Validate，不要求调用者先调用；依请求 Regions 声明顺序、各区 Required 后 Optional 的方法声明顺序输出。一项输出恰对应一个(region,method)。Computed 必有匹配方法的 Value，ReasonCode=null；NotObservable 必须 Value=null 且原因非空。Coverage 在 A>0、N=0时仍是 Computed/0，其它依赖灰度的量是 NotObservable/NoValidPixels；报告状态 CompletedWithUnavailableMetrics，不按全遮蔽返回PASS。

Rejected/Failed 不带任何观察。Rejected 对应非法请求、资源超限、Busy、Disposed、Reentrant；Failed 对应执行中数值溢出或不可恢复的计算异常。代码固定 MQ-001 InvalidRequest、MQ-002 InvalidImage、MQ-003 InvalidDomain、MQ-004 InvalidMethod、MQ-005 BudgetExceeded、MQ-006 NumericOverflow、MQ-007 Busy、MQ-008 Disposed、MQ-009 Reentrant、MQ-010 ComputationFailure。MessageKey 为 ImageQuality.Error.<名称>；FieldPath 指实际字段/索引，所有 Retryable=false，纠正后提交新 RequestId。非法工厂选项抛 ArgumentException，null选项抛 ArgumentNullException；配置编程错误发生于尚无请求之前，不伪造请求结果。

同实例无等待队列，一次只接纳一个 Evaluate；Validate 可并发，不修改实例。Evaluate接纳与Dispose在短锁内序列化，不在锁内调用诊断或做计算。Dispose在短锁中标记停止新准入并立即返回，不等待/中断已接纳Evaluate；在途Evaluate仍按原输入完成、释放scratch后返回结果。Dispose返回不宣称在途计算已退出。Validate关闭后返回MQ-008，在途忙时Validate可做无副作用校验但不保证后续接纳。诊断端口同线程调用，异常隔离；端口重入同实例立即 MQ-009；并发别的线程 MQ-007。同RequestId重复运行是无副作用重新计算，相同输入数值相同；不建幂等存储或按Id返旧缓存。参数改变使用新RequestId并保留旧结果，不覆盖。无CancellationToken/期限入口；宿主等待超时只表示停止等待，不能将未退出计算记录为取消/排空成功。

以下是独立 console/test host 可构造调用片段（使用本附录类型及 System.Collections.Immutable），没有未声明 helper：

~~~csharp
var options = new ManagedQualityRuntimeOptions(1024 * 1024, 4, 5, 256);
using var evaluator = ImageQualityManagedFactory.Create(options);
var request = new ManagedQualityRequest(
    Guid.NewGuid(),
    new ManagedGrayImage(4, 1, ManagedPixelType.UInt8,
        ImmutableArray.Create(0d, 100d, 254d, 255d), "fixture-gray-v1"),
    ImmutableArray.Create(new ManagedQualityRegion(
        "roi-1", 0, 0, 1, 4, null, "region-v1")),
    new ManagedQualityMethodSet(
        ImmutableArray.Create<ManagedQualityMethod>(
            new ManagedSaturationMethod("1", 0, 255),
            new ManagedCoverageMethod("1")),
        ImmutableArray<ManagedQualityMethod>.Empty),
    options);
var result = evaluator.Evaluate(request);
Console.WriteLine(result.State);
~~~

预期两项观察按声明顺序：Saturation 低/高各1、比例各0.25，Coverage为1；A=N=4。模块不提供合格或重拍命令。

附录A补充输入/结果约定：null request返回Rejected/MQ-001，RequestId=Guid.Empty、SourceRevision为空、Observations为空、ReservedWorkingBytes=0；null Image/Region/Method或集合Default按所属字段MQ-002/003/004拒绝，不解引用后变ComputationFailure。非法请求返回能安全读取的原RequestId/图像SourceRevision，其余为空，不伪造来源。Revision/键在校验前不可复制成无限长诊断；FieldPath只含固定名与受限索引。执行中Failed清全部观察，ReservedWorkingBytes保留接纳时预留用于诊断但不代表资源仍驻留。任何NotObservable（含Optional）使纯托管报告CompletedWithUnavailableMetrics；这与服务外层Required判定有意不同，服务消费完整RawValues，不直接复用A的状态为质量放行。

IQualityDiagnosticPort.Publish只在Evaluate接纳后发出至多Compute与Completed/Failed两条，接纳前Rejected可发一条Rejected；Validate永不发。stage封闭Compute/Completed/Failed/Rejected；code为空仅用于Compute/无缺项Completed，其余用MQ错误码或NoValidPixels；回调异常隔离，不调用第二诊断端口，不改变结果。回调重入Validate/Evaluate都返回MQ-009；Dispose只标停止准入并立即返回。诊断字段是稳定技术标识，本地化由宿主/控件资源负责，不发送像素/异常堆栈。无订阅结果完全相同。


### A.3 确定性计算、资源和可执行断言

按原灰度逐行扫描，仅mask内有效值进入统计。一次ROI准备可共享给本区多个方法，不复制整帧到每个ROI。计数和面积用long/checked；整数原值直方图可累计256/65536个long桶，NumBins是输出分箱上限而非内部原值桶限制。总体方差采用在线中心矩：n←n+1，δ=x−μ，μ←μ+δ/n，M2←M2+δ×(x−μ)；输出sqrt(M2/n)。所有中间量必须有限；负M2不取abs或任意归零，返回MQ-006。Float64按行优先固定顺序，N=0缺失、N=1输出0。不能用Σx²−Nμ²的消减形式、bin中心或不同tile σ的平均代替。

nearest-rank只从原有效值排序/整数频数累计得到第ceil(qN)值；UInt8/UInt16按精确原值桶，Float64只创建一份N个double排序副本，预算不足拒绝，不降为近似分位。直方图先按effective min/max分离Below/Above，再分箱：整数i=floor((g−min)×K/(max−min+1))，用checked long乘法与整数除法，不向浮点边界取ceil；K等码数时每码恰一bin。Float64 i=max(0,min(K−1,ceil((g−min)/BinSize)−1))，内部精确边界入较小bin，g=min首bin、g=max末bin；按IEEE double的实际运算定义，不使用容差挪箱。Counts.Sum+BelowRange+AboveRange=N、Counts.Length=K。整数范围必须在相应容器码范围内，差与乘积checked；Float64范围差/BinSize须正有限，否则Validate MQ-004。本托管合同由这些公式定义，实际HALCON边界差分仍按§20/15另验，不能把它宣称未经运行的bitwise等价。直方图单位Count，曝光Count，饱和/覆盖Fraction（饱和另保留计数），对比GrayLevel。

预算账本冻结为：4096固定请求/工厂运行预留 + 每Region/Method各1024 + 每Observation各2048 + 每个保留字符串2×UTF16Length + 每数组64字节 + 输入8×WH + 每个非null mask的1×ROI面积 + 每个输出Counts的8×K + 一个整数原桶8×256/65536或Float64排序8×N（仅需要对应scratch的方法）。按最大单ROI scratch与累计全部结果同时存活量checked预留，不对每个ROI重复算输入，也不共享不同数组容量。Validate仅用尺寸/类型/方法计算预留，不创建大scratch；Evaluate分配前用同账本再验。ReservedWorkingBytes为此逻辑峰值预留；账本不是CLR/RSS硬上界，不称实测保守界。完成/失败释放scratch引用，本实例不缓存图像/结果，返回结果归调用方；实际进程峰值按§11.1另测。计数/面积到long，输出数R×M亦checked且≤int.MaxValue；工厂选项再大也不能突破BCL数组实际长度。

计划测试类 ManagedQualityContractTests / ManagedQualityNumericsTests / ManagedQualityLifecycleTests 位于唯一 Core.Tests 工程；方法断言如下，开工后实现，不在文档阶段造测试：

| 夹具/操作 | 可判定结果 |
|---|---|
| [0,10,100,240,255]，曝光0/10/240/255 | 五类各1，N=5；精确端点互斥。 |
| [0,100,254,255]，mask全false | A=4/N=0；覆盖0，统计无Value/NoValidPixels，完成但有缺项。 |
| [1,2,3,4]，StdDev；q=.25/.75 | μ=2.5，总体σ=sqrt(1.25)，分位距=3−1=2；不能输出样本σ。 |
| Float64 [0,1,2,3,4]，range[0,4]/K=4；UInt8 [0,1,2,3] range[0,3]/K=4 | Float64 Counts=[2,1,1,1]；UInt8 Counts=[1,1,1,1]。整数width1.5样例[0..5]/K4为[2,1,2,1]，不能混用real边界。 |
| 单值7/全常量7；大偏置小离散[10000001,10000002,10000003] | σ=0/0/sqrt(2/3)，均有限；Float64巨大相反符号导致差值溢出时MQ-006且零观察。 |
| mask错长、非整数UInt8、未知enum、任一Default、非法分位、超bins、checked面积溢出 | Evaluate拒绝且零观察，Validate和Evaluate错误分类一致。 |
| 同输入重复、两个实例、诊断异常/重入、并发Evaluate、Dispose竞态 | 数值/顺序稳定；Busy/Reentrant可判定，无串扰；已接纳计算完成，关闭后MQ-008。 |
| 第二维ROI边界/重叠ROI、预算刚好/差1byte、调用方修改原可变源数组 | 原快照不变；不因相同图像以全帧分母代ROI，不先分配超额副本。 |

### A.4 两消费者、性能和六项准备结论

第一消费者为独立 OCR/读码工程工具的输入诊断 console host（构造托管快照；需要曝光/饱和、原分位距），第二消费者为独立2D/3D重建前检查 console host（构造自己的快照；需要覆盖/直方图，缺运动/相位另交宿主）。二者只引用 Asun.Modules.ImageQuality.Core，分别创建 evaluator、options、diagnostics；不依赖第一消费者的配置、Shell、设备或数据库。host代码落在本模块 Core.Tests 的 ConsumerHostContractTests；单独引用发布Core本地DLL 后在临时无UI .NET10进程调用上例，断开第一host仍能运行第二host。无生产事实写入；不新建产品host工程来伪装集成。

Benchmark计划见§11.1，首片端到端测点是Evaluate进入→结果返回及scratch释放；没有ResourcesReleased事件，不虚构native门。代码唯一工程/namespace和允许禁止路径见Core binding。Module API、失败与数值反例已在A.1–A.3补齐；主控2026-10-10已按§24.1接收ManagedCoreSlice-01六项规格，同步ModuleCoreImplementationReady（仅规格准备），尚未创建项目或执行代码；0.5.2-prep服务关闭及此前WPF保存定向修订均已由主控接收，主控2026-10-11另接收QualityServiceSlice-02/Core+Simulator六项为ModuleCoreImplementationReady（仅文档规格），限定内容接收WpfSlice-03装配/Presenter/原Owner恢复及AsunImage公开构造指导确定范围。真实HALCON/WPF/native资源系数、Viewer/保存Owner/产品映射、运行/性能及现场资格仍PreparationIncomplete/NotReady，Memory viewer不外推超大图/3D能力。正式C-03/C-04与产品身份映射、真实帧lease桥、HALCON、WPF和客户阈值分别是后续门，不阻断这份纯托管合同的内容审查。

